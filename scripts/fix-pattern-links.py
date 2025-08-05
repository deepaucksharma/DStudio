#!/usr/bin/env python3
"""
Fix pattern library links by mapping to correct locations.
This script specifically handles the pattern-library vs patterns confusion.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict
import json

def analyze_pattern_structure():
    """Analyze the actual pattern structure in the repository"""
    pattern_locations = {}
    
    # Check pattern-library directory
    pattern_lib_dir = Path('docs/pattern-library')
    if pattern_lib_dir.exists():
        for category_dir in pattern_lib_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                for pattern_file in category_dir.glob('*.md'):
                    if pattern_file.name != 'index.md':
                        rel_path = pattern_file.relative_to(Path('docs'))
                        pattern_name = pattern_file.stem
                        pattern_locations[pattern_name] = str(rel_path)
    
    return pattern_locations

def revert_incorrect_fixes(file_path, dry_run=False):
    """Revert incorrect pattern references back to pattern-library"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        fixes_made = []
        
        # Revert patterns/ back to pattern-library/ for files that exist
        pattern_locations = analyze_pattern_structure()
        
        def check_and_fix(match):
            text = match.group(1)
            url = match.group(2)
            
            # Check if this is a broken patterns/ reference
            if '/patterns/' in url and not url.startswith('http'):
                # Extract the pattern name from the URL
                pattern_match = re.search(r'/patterns/(?:[\w-]+/)?(\w+(?:-\w+)*)\.md', url)
                if pattern_match:
                    pattern_name = pattern_match.group(1)
                    
                    # Check if this pattern exists in pattern-library
                    if pattern_name in pattern_locations:
                        # Replace with correct pattern-library path
                        correct_path = pattern_locations[pattern_name]
                        new_url = url.replace('/patterns/', '/pattern-library/')
                        
                        # Handle specific category mappings
                        new_url = re.sub(r'/patterns/(\w+(?:-\w+)*)/(\w+(?:-\w+)*)\.md', 
                                        lambda m: f'/pattern-library/{m.group(1)}/{m.group(2)}.md', 
                                        new_url)
                        
                        fixes_made.append((url, new_url))
                        return f'[{text}]({new_url})'
                
                # For directory references without specific files
                elif url.endswith('/patterns/'):
                    new_url = url.replace('/patterns/', '/pattern-library/')
                    fixes_made.append((url, new_url))
                    return f'[{text}]({new_url})'
            
            return match.group(0)
        
        # Apply fixes
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', check_and_fix, content)
        
        if content != original_content and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        return fixes_made
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Fix pattern library links')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    parser.add_argument('--path', default='docs', help='Path to scan (default: docs)')
    
    args = parser.parse_args()
    
    # First analyze the pattern structure
    print("Analyzing pattern structure...")
    pattern_locations = analyze_pattern_structure()
    print(f"Found {len(pattern_locations)} patterns in pattern-library")
    
    print(f"\n{'DRY RUN: ' if args.dry_run else ''}Fixing pattern links...")
    
    total_fixes = defaultdict(int)
    files_fixed = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk(args.path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                fixes = revert_incorrect_fixes(file_path, dry_run=args.dry_run)
                
                if fixes:
                    files_fixed += 1
                    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {len(fixes)} links in: {file_path}")
                    for old, new in fixes[:5]:  # Show first 5
                        print(f"  {old} → {new}")
                    if len(fixes) > 5:
                        print(f"  ... and {len(fixes) - 5} more")
                        
                    for old, new in fixes:
                        total_fixes[old] += 1
    
    # Summary
    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} links in {files_fixed} files")
    print(f"Total unique broken patterns: {len(total_fixes)}")
    
    # Save pattern mapping for reference
    with open('pattern-mappings.json', 'w') as f:
        json.dump(pattern_locations, f, indent=2)
    print(f"\nPattern mappings saved to: pattern-mappings.json")
    
    return 0 if not args.dry_run else 1

if __name__ == '__main__':
    sys.exit(main())
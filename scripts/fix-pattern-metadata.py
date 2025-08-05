#!/usr/bin/env python3
"""
Fix pattern metadata issues in pattern library files.
"""

import os
import re
import yaml
from pathlib import Path

def extract_title_from_content(content):
    """Extract title from first heading in content"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Pattern"

def determine_category(file_path):
    """Determine category from file path"""
    path_parts = Path(file_path).parts
    if 'pattern-library' in path_parts:
        idx = path_parts.index('pattern-library')
        if idx + 1 < len(path_parts) - 1:  # Has subdirectory
            return path_parts[idx + 1]
    return 'general'

def fix_pattern_metadata(file_path, dry_run=False):
    """Fix metadata in a pattern file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip index files
        if file_path.endswith('index.md'):
            return None
            
        # Skip non-pattern files
        skip_files = [
            'pattern-antipatterns-guide.md',
            'pattern-combination-recipes.md', 
            'pattern-comparison-tool.md',
            'pattern-decision-matrix.md',
            'pattern-implementation-roadmap.md',
            'pattern-migration-guides.md',
            'pattern-relationship-map.md',
            'pattern-synthesis-guide.md',
            'pattern-template-v2.md',
            'visual-asset-creation-plan.md',
            'RENDERING_INSTRUCTIONS.md',
            'pattern-selection-matrix.md'
        ]
        
        if any(file_path.endswith(skip) for skip in skip_files):
            return None
        
        # Check if has frontmatter
        if content.strip().startswith('---'):
            # Extract existing frontmatter
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                except:
                    frontmatter = {}
                    
                body = parts[2]
            else:
                frontmatter = {}
                body = content
        else:
            frontmatter = {}
            body = content
        
        # Ensure required fields
        changes_made = False
        
        if 'title' not in frontmatter or not frontmatter['title']:
            frontmatter['title'] = extract_title_from_content(body)
            changes_made = True
            
        if 'category' not in frontmatter or not frontmatter['category']:
            frontmatter['category'] = determine_category(file_path)
            changes_made = True
            
        if 'excellence_tier' not in frontmatter:
            # Default to silver for most patterns
            frontmatter['excellence_tier'] = 'silver'
            changes_made = True
            
        if 'pattern_status' not in frontmatter:
            # Default to stable
            frontmatter['pattern_status'] = 'stable'
            changes_made = True
        
        # Fix invalid YAML by ensuring proper types
        if 'title' in frontmatter and isinstance(frontmatter['title'], list):
            frontmatter['title'] = ' '.join(str(x) for x in frontmatter['title'])
            changes_made = True
            
        if changes_made and not dry_run:
            # Reconstruct file with updated frontmatter
            new_content = '---\n'
            new_content += yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            new_content += '---\n'
            new_content += body.lstrip()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return frontmatter
            
        return None if not changes_made else frontmatter
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Fix pattern metadata')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed')
    parser.add_argument('--path', default='docs/pattern-library', help='Path to scan')
    
    args = parser.parse_args()
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Fixing pattern metadata...")
    
    files_fixed = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk(args.path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                result = fix_pattern_metadata(file_path, dry_run=args.dry_run)
                
                if result:
                    files_fixed += 1
                    print(f"{'Would fix' if args.dry_run else 'Fixed'}: {file_path}")
                    if args.dry_run:
                        print(f"  title: {result.get('title', 'N/A')}")
                        print(f"  category: {result.get('category', 'N/A')}")
                        print(f"  excellence_tier: {result.get('excellence_tier', 'N/A')}")
                        print(f"  pattern_status: {result.get('pattern_status', 'N/A')}")
    
    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} metadata in {files_fixed} files")
    
    return 0 if not args.dry_run else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
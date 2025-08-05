#!/usr/bin/env python3
"""
Fix references to patterns/ directory to point to pattern-library/
"""

import os
import re
import sys

def fix_patterns_references(file_path, dry_run=False):
    """Fix ../patterns/ references to ../pattern-library/"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Replace various patterns/ references with pattern-library/
        patterns_to_fix = [
            (r'\.\./patterns/', '../pattern-library/'),
            (r'\.\./\.\./patterns/', '../../pattern-library/'),
            (r'\.\./\.\./\.\./patterns/', '../../../pattern-library/'),
            (r'/patterns/', '/pattern-library/'),
            (r'\[([^\]]+)\]\(patterns/', r'[\1](pattern-library/'),
        ]
        
        for pattern, replacement in patterns_to_fix:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
                
        return content != original_content
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Fix patterns directory references')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed')
    parser.add_argument('--path', default='docs', help='Path to scan')
    
    args = parser.parse_args()
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Fixing patterns/ directory references...")
    
    files_fixed = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk(args.path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                if fix_patterns_references(file_path, dry_run=args.dry_run):
                    files_fixed += 1
                    print(f"{'Would fix' if args.dry_run else 'Fixed'}: {file_path}")
    
    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {files_fixed} files")
    
    return 0 if not args.dry_run else 1

if __name__ == '__main__':
    sys.exit(main())
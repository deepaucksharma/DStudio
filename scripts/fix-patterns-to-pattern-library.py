#!/usr/bin/env python3
"""
Fix incorrect patterns/ references back to pattern-library/
"""

import os
import re
import sys
from pathlib import Path

def fix_patterns_references(file_path, dry_run=False):
    """Fix patterns/ references back to pattern-library/"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Replace patterns/ with pattern-library/
        content = re.sub(r'(\.\./)*patterns/', r'\1pattern-library/', content)
        content = re.sub(r'\[([^\]]+)\]\(([^)]*/)patterns/([^)]+)\)', r'[\1](\2pattern-library/\3)', content)
        
        if content != original_content and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
                
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Fix patterns references')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed')
    parser.add_argument('--path', default='docs', help='Path to scan')
    
    args = parser.parse_args()
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Fixing patterns/ references...")
    
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
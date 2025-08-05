#!/usr/bin/env python3
"""
Fix relative paths to pattern-library from interview-prep sections
"""

import os
import re
import sys
from pathlib import Path

def fix_relative_paths(file_path, dry_run=False):
    """Fix relative paths based on file location"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        fixes_made = 0
        
        # Determine the correct relative path based on file location
        path = Path(file_path)
        rel_to_docs = path.relative_to(Path('docs'))
        depth = len(rel_to_docs.parts) - 1  # -1 because we don't count the filename
        
        # For interview-prep/ic-interviews/common-problems/* files
        if 'interview-prep/ic-interviews/common-problems' in str(rel_to_docs):
            # These files need ../../../pattern-library/
            content = re.sub(r'\.\./pattern-library/', '../../../pattern-library/', content)
            fixes_made += content.count('../../../pattern-library/') - original_content.count('../../../pattern-library/')
        
        # For interview-prep/ic-interviews/* files (not in common-problems)
        elif 'interview-prep/ic-interviews' in str(rel_to_docs) and 'common-problems' not in str(rel_to_docs):
            # These files need ../../pattern-library/
            content = re.sub(r'(?<!\.\.)../pattern-library/', '../../pattern-library/', content)
            fixes_made += content.count('../../pattern-library/') - original_content.count('../../pattern-library/')
        
        if content != original_content and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return fixes_made
                
        return fixes_made
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Fix relative paths to pattern-library')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed')
    parser.add_argument('--path', default='docs/interview-prep', help='Path to scan')
    
    args = parser.parse_args()
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Fixing relative paths to pattern-library...")
    
    files_fixed = 0
    total_fixes = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk(args.path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                fixes = fix_relative_paths(file_path, dry_run=args.dry_run)
                if fixes > 0:
                    files_fixed += 1
                    total_fixes += fixes
                    print(f"{'Would fix' if args.dry_run else 'Fixed'} {fixes} paths in: {file_path}")
    
    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {total_fixes} paths in {files_fixed} files")
    
    return 0 if not args.dry_run else 1

if __name__ == '__main__':
    sys.exit(main())
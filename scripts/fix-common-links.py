#!/usr/bin/env python3
"""
Fix common broken link patterns in DStudio documentation.
This script maps commonly broken links to their correct locations.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict
import json

# Common link mappings based on validation results
LINK_MAPPINGS = {
    # Pattern library mappings
    'pattern-library/data-management/version-control.md': 'pattern-library/data-management/event-sourcing.md',
    'pattern-library/data-management/feature-store.md': 'pattern-library/data-management/materialized-view.md',
    'pattern-library/performance/caching.md': 'pattern-library/scaling/caching-strategies.md',
    'pattern-library/data-management/stream-processing.md': 'pattern-library/architecture/event-streaming.md',
    'pattern-library/data-management/time-series-database.md': 'pattern-library/data-management/lsm-tree.md',
    'pattern-library/communication/message-queue.md': 'pattern-library/coordination/distributed-queue.md',
    'pattern-library/scaling/database-sharding.md': 'pattern-library/scaling/sharding.md',
    'pattern-library/data-management/content-addressable-storage.md': 'pattern-library/data-management/merkle-trees.md',
    'pattern-library/collaboration/operational-transforms.md': 'pattern-library/data-management/crdt.md',
    'pattern-library/data-management/crdts.md': 'pattern-library/data-management/crdt.md',
    'pattern-library/coordination/saga.md': 'pattern-library/data-management/saga.md',
    
    # Interview prep mappings
    'scalability-cheatsheet.md': 'index.md',
    'common-patterns-reference.md': 'index.md',
    'radio-framework/': 'index.md',
    '4s-method/': 'index.md',
    
    # Fix pattern library directory references
    '../../pattern-library/': '../../patterns/',
    '../../../pattern-library/': '../../../patterns/',
    
    # Architects handbook mappings
    'architects-handbook/patterns/': 'patterns/',
    'architects-handbook/case-studies/': 'introduction/case-studies/',
}

def fix_links_in_file(file_path, dry_run=False):
    """Fix broken links in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        fixes_made = []
        
        # Fix markdown links [text](url)
        def replace_link(match):
            text = match.group(1)
            url = match.group(2)
            
            # Check if URL needs fixing
            for broken, fixed in LINK_MAPPINGS.items():
                if broken in url:
                    new_url = url.replace(broken, fixed)
                    fixes_made.append((url, new_url))
                    return f'[{text}]({new_url})'
                    
            # Check exact matches
            if url in LINK_MAPPINGS:
                new_url = LINK_MAPPINGS[url]
                fixes_made.append((url, new_url))
                return f'[{text}]({new_url})'
                
            return match.group(0)
        
        # Apply fixes
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)
        
        # Fix specific pattern references
        # Convert pattern-library to patterns where appropriate
        content = re.sub(r'\.\./pattern-library/([^/]+)/', r'../patterns/', content)
        content = re.sub(r'\.\./\.\./pattern-library/([^/]+)/', r'../../patterns/', content)
        content = re.sub(r'\.\./\.\./\.\./pattern-library/([^/]+)/', r'../../../patterns/', content)
        
        if content != original_content and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        return fixes_made
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def find_actual_pattern_files():
    """Find actual pattern files to create better mappings"""
    patterns_dir = Path('docs/patterns')
    pattern_lib_dir = Path('docs/pattern-library')
    
    actual_patterns = {}
    
    # Scan both directories
    for base_dir in [patterns_dir, pattern_lib_dir]:
        if base_dir.exists():
            for pattern_file in base_dir.rglob('*.md'):
                if pattern_file.name != 'index.md':
                    # Create various possible references
                    rel_path = pattern_file.relative_to(Path('docs'))
                    basename = pattern_file.stem
                    
                    # Store mappings
                    actual_patterns[basename] = str(rel_path)
                    
    return actual_patterns

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Fix common broken links')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    parser.add_argument('--path', default='docs', help='Path to scan (default: docs)')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    
    args = parser.parse_args()
    
    # Find actual pattern files for better mapping
    actual_patterns = find_actual_pattern_files()
    
    # Update mappings with actual files
    for broken_ref in list(LINK_MAPPINGS.keys()):
        if 'pattern-library' in broken_ref:
            basename = Path(broken_ref).stem
            if basename in actual_patterns:
                LINK_MAPPINGS[broken_ref] = actual_patterns[basename]
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Scanning for broken links to fix...")
    
    total_fixes = defaultdict(int)
    files_fixed = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk(args.path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                fixes = fix_links_in_file(file_path, dry_run=args.dry_run)
                
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
    
    if args.report:
        # Generate detailed report
        report = {
            'dry_run': args.dry_run,
            'files_processed': files_fixed,
            'link_mappings': LINK_MAPPINGS,
            'fixes_by_frequency': dict(sorted(total_fixes.items(), key=lambda x: x[1], reverse=True)),
            'actual_patterns_found': actual_patterns
        }
        
        with open('link-fix-report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to: link-fix-report.json")
    
    return 0 if not args.dry_run else 1

if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python3
"""
Fix remaining broken links with more specific mappings.
"""

import os
import re
import sys
from pathlib import Path

# Specific link fixes based on validation results
SPECIFIC_FIXES = {
    # Fix case study references
    'introduction/case-studies/index.md': 'architects-handbook/case-studies/index.md',
    '../introduction/case-studies/': '../architects-handbook/case-studies/',
    
    # Fix pattern references that don't exist
    '../patterns/common-problems/': '../interview-prep/ic-interviews/common-problems/',
    
    # Fix missing pattern files by mapping to closest existing patterns
    '../../../pattern-library/event-sourcing.md': '../../../pattern-library/data-management/event-sourcing.md',
    '../../../pattern-library/materialized-view.md': '../../../pattern-library/data-management/materialized-view.md',
    '../../../pattern-library/caching-strategies.md': '../../../pattern-library/scaling/caching-strategies.md',
    '../../../pattern-library/event-streaming.md': '../../../pattern-library/architecture/event-streaming.md',
    '../../../pattern-library/lsm-tree.md': '../../../pattern-library/data-management/lsm-tree.md',
    '../../../pattern-library/distributed-queue.md': '../../../pattern-library/coordination/distributed-queue.md',
    '../../../pattern-library/sharding.md': '../../../pattern-library/scaling/sharding.md',
    '../../../pattern-library/saga.md': '../../../pattern-library/data-management/saga.md',
    '../../../pattern-library/merkle-trees.md': '../../../pattern-library/data-management/merkle-trees.md',
    '../../../pattern-library/crdt.md': '../../../pattern-library/data-management/crdt.md',
    
    # Fix patterns without categories
    '../pattern-library/event-driven.md': '../pattern-library/architecture/event-driven.md',
    '../pattern-library/event-streaming.md': '../pattern-library/architecture/event-streaming.md',
    '../pattern-library/websocket.md': '../pattern-library/communication/websocket.md',
    '../pattern-library/queues-streaming.md': '../pattern-library/scaling/queues-streaming.md',
    '../pattern-library/lambda-architecture.md': '../pattern-library/architecture/lambda-architecture.md',
    '../pattern-library/fault-tolerance.md': '../pattern-library/resilience/fault-tolerance.md',
    '../pattern-library/geo-distribution.md': '../pattern-library/scaling/geo-distribution.md',
    '../pattern-library/url-normalization.md': '../pattern-library/scaling/url-normalization.md',
    '../pattern-library/clock-sync.md': '../pattern-library/coordination/clock-sync.md',
    '../pattern-library/logical-clocks.md': '../pattern-library/coordination/logical-clocks.md',
    '../pattern-library/id-generation-scale.md': '../pattern-library/scaling/id-generation-scale.md',
    
    # Fix absolute pattern references
    '/pattern-library/event-sourcing.md': '/pattern-library/data-management/event-sourcing.md',
    '/pattern-library/service-mesh.md': '/pattern-library/communication/service-mesh.md',
    '/pattern-library/crdt.md': '/pattern-library/data-management/crdt.md',
    '/pattern-library/geo-replication.md': '/pattern-library/scaling/geo-replication.md',
    '/pattern-library/event-driven.md': '/pattern-library/architecture/event-driven.md',
    '/pattern-library/graphql-federation.md': '/pattern-library/architecture/graphql-federation.md',
    
    # Fix pattern library root references
    '../pattern-library/': '../patterns/',
    '../../pattern-library/': '../../patterns/',
    '../../../pattern-library/': '../../../patterns/',
    
    # Fix missing category patterns
    '../pattern-library/consensus.md': '../pattern-library/coordination/consensus.md',
    '../pattern-library/leader-follower.md': '../pattern-library/coordination/leader-follower.md',
    '../pattern-library/eventual-consistency.md': '../pattern-library/data-management/eventual-consistency.md',
    '../pattern-library/cap-theorem.md': '../pattern-library/architecture/cap-theorem.md',
    '../pattern-library/cdc.md': '../pattern-library/data-management/cdc.md',
    '../pattern-library/leader-election.md': '../pattern-library/coordination/leader-election.md',
    '../pattern-library/distributed-lock.md': '../pattern-library/coordination/distributed-lock.md',
    '../pattern-library/service-discovery.md': '../pattern-library/communication/service-discovery.md',
}

def fix_links_in_file(file_path, dry_run=False):
    """Fix broken links in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        fixes_made = []
        
        # Apply specific fixes
        for broken, fixed in SPECIFIC_FIXES.items():
            if broken in content:
                content = content.replace(broken, fixed)
                fixes_made.append((broken, fixed))
        
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
    parser = argparse.ArgumentParser(description='Fix remaining broken links')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed')
    parser.add_argument('--path', default='docs', help='Path to scan')
    
    args = parser.parse_args()
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Fixing remaining broken links...")
    
    files_fixed = 0
    total_fixes = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk(args.path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                fixes = fix_links_in_file(file_path, dry_run=args.dry_run)
                
                if fixes:
                    files_fixed += 1
                    total_fixes += len(fixes)
                    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {len(fixes)} links in: {file_path}")
                    for old, new in fixes[:5]:
                        print(f"  {old} → {new}")
                    if len(fixes) > 5:
                        print(f"  ... and {len(fixes) - 5} more")
    
    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {total_fixes} links in {files_fixed} files")
    
    return 0 if not args.dry_run else 1

if __name__ == '__main__':
    sys.exit(main())
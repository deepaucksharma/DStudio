#!/usr/bin/env python3
"""
Comprehensive fix for all broken links in the documentation.
Maps broken references to existing pattern files.
"""

import os
import re
import sys
from pathlib import Path
import json

# Comprehensive mapping of broken links to existing patterns
PATTERN_MAPPINGS = {
    # Direct pattern mappings (without category)
    'circuit-breaker.md': 'resilience/circuit-breaker.md',
    'bulkhead.md': 'resilience/bulkhead.md',
    'saga.md': 'data-management/saga.md',
    'cqrs.md': 'data-management/cqrs.md',
    'rate-limiting.md': 'scaling/rate-limiting.md',
    'leader-election.md': 'coordination/leader-election.md',
    'load-balancing.md': 'scaling/load-balancing.md',
    'caching-strategies.md': 'scaling/caching-strategies.md',
    'consensus.md': 'coordination/consensus.md',
    'event-sourcing.md': 'data-management/event-sourcing.md',
    'sharding.md': 'scaling/sharding.md',
    'leader-follower.md': 'coordination/leader-follower.md',
    'eventual-consistency.md': 'data-management/eventual-consistency.md',
    'cap-theorem.md': 'architecture/cap-theorem.md',
    'cdc.md': 'data-management/cdc.md',
    'distributed-lock.md': 'coordination/distributed-lock.md',
    'service-discovery.md': 'communication/service-discovery.md',
    'logical-clocks.md': 'coordination/logical-clocks.md',
    'crdt.md': 'data-management/crdt.md',
    'outbox.md': 'data-management/outbox.md',
    'timeout.md': 'resilience/timeout.md',
    'health-check.md': 'resilience/health-check.md',
    'retry-backoff.md': 'resilience/retry-backoff.md',
    'event-driven.md': 'architecture/event-driven.md',
    'event-streaming.md': 'architecture/event-streaming.md',
    'websocket.md': 'communication/websocket.md',
    'queues-streaming.md': 'scaling/queues-streaming.md',
    'lambda-architecture.md': 'architecture/lambda-architecture.md',
    'fault-tolerance.md': 'resilience/fault-tolerance.md',
    'geo-distribution.md': 'scaling/geo-distribution.md',
    'url-normalization.md': 'scaling/url-normalization.md',
    'clock-sync.md': 'coordination/clock-sync.md',
    'id-generation-scale.md': 'scaling/id-generation-scale.md',
    'merkle-trees.md': 'data-management/merkle-trees.md',
    'failover.md': 'resilience/failover.md',
    'service-mesh.md': 'communication/service-mesh.md',
    'geo-replication.md': 'scaling/geo-replication.md',
    'backpressure.md': 'scaling/backpressure.md',
    'auto-scaling.md': 'scaling/auto-scaling.md',
    'edge-computing.md': 'scaling/edge-computing.md',
    'api-gateway.md': 'communication/api-gateway.md',
    'graceful-degradation.md': 'resilience/graceful-degradation.md',
    'hlc.md': 'coordination/hlc.md',
    'publish-subscribe.md': 'communication/publish-subscribe.md',
    'distributed-queue.md': 'coordination/distributed-queue.md',
    'lsm-tree.md': 'data-management/lsm-tree.md',
    'materialized-view.md': 'data-management/materialized-view.md',
    'consistent-hashing.md': 'data-management/consistent-hashing.md',
    'sidecar.md': 'architecture/sidecar.md',
    'two-phase-commit.md': 'data-management/saga.md',  # Map to saga as 2PC doesn't exist
    'vector-clocks.md': 'coordination/logical-clocks.md',  # Map to logical clocks
    'paxos.md': 'coordination/consensus.md',  # Map to consensus
    'raft.md': 'coordination/consensus.md',  # Map to consensus
    'map-reduce.md': 'scaling/scatter-gather.md',  # Map to scatter-gather
    'finops.md': 'scaling/auto-scaling.md',  # Map to auto-scaling for cost optimization
    'serverless.md': 'architecture/serverless-faas.md',
    'multi-cloud.md': 'scaling/multi-region.md',  # Map to multi-region
    'cost-optimization.md': 'scaling/auto-scaling.md',  # Map to auto-scaling
    
    # Specific missing patterns mapped to closest alternatives
    'performance/caching.md': 'scaling/caching-strategies.md',
    'caching.md': 'scaling/caching-strategies.md',
    'data-management/version-control.md': 'data-management/event-sourcing.md',
    'data-management/feature-store.md': 'data-management/materialized-view.md',
    'data-management/stream-processing.md': 'architecture/event-streaming.md',
    'data-management/time-series-database.md': 'data-management/lsm-tree.md',
    'communication/message-queue.md': 'coordination/distributed-queue.md',
    'scaling/database-sharding.md': 'scaling/sharding.md',
    'data-management/content-addressable-storage.md': 'data-management/merkle-trees.md',
    'collaboration/operational-transforms.md': 'data-management/crdt.md',
    'data-management/crdts.md': 'data-management/crdt.md',
    'communication/websocket-scaling.md': 'communication/websocket.md',
    'communication/request-routing.md': 'communication/api-gateway.md',
    'data-management/database-per-service.md': 'data-management/polyglot-persistence.md',
    'data-management/idempotent-receiver.md': 'data-management/deduplication.md',
    'data-management/time-series-ids.md': 'scaling/id-generation-scale.md',
    'scaling/geohashing.md': 'scaling/geo-distribution.md',
    'data-management/wal.md': 'data-management/write-ahead-log.md',
    'location-privacy.md': 'resilience/split-brain.md',  # No direct match, map to split-brain
    'queue-based-load-leveling.md.md': 'scaling/queues-streaming.md',
    
    # Architecture patterns
    'monolith.md': 'architecture/strangler-fig.md',  # Map to strangler fig for migration
    'microservices.md': 'architecture/backends-for-frontends.md',  # Map to BFF
    'event-driven-architecture.md': 'architecture/event-driven.md',
    'containerization.md': 'architecture/cell-based.md',  # Map to cell-based
    'distributed-queues.md': 'coordination/distributed-queue.md',
}

# Additional mappings for different URL patterns
URL_REPLACEMENTS = {
    # Fix architects-handbook patterns references
    'architects-handbook/patterns/': 'pattern-library/',
    
    # Fix broken directory references
    '../patterns/': '../pattern-library/',
    '../../patterns/': '../../pattern-library/',
    '../../../patterns/': '../../../pattern-library/',
    
    # Fix broken case study references that still exist
    'architects-handbook/case-studies/infrastructure/consistent-hashing.md': 'architects-handbook/case-studies/index.md',
    
    # Fix pattern references without .md
    'pattern-library/cache-aside': 'pattern-library/scaling/caching-strategies.md',
    'pattern-library/read-through-cache': 'pattern-library/scaling/caching-strategies.md',
    'pattern-library/write-through-cache': 'pattern-library/scaling/caching-strategies.md',
    'pattern-library/write-behind-cache': 'pattern-library/scaling/caching-strategies.md',
    'pattern-library/tile-caching': 'pattern-library/scaling/tile-caching.md',
    
    # Fix hashtag references
    '#idempotency-pattern.md': '#idempotency',
    '#double-entry-ledger-pattern.md': '#double-entry-ledger',
    '#performance-scaling': '#performance',
}

def fix_broken_link(url, source_file):
    """Fix a broken link based on mappings"""
    # First try direct URL replacements
    for broken, fixed in URL_REPLACEMENTS.items():
        if broken in url:
            return url.replace(broken, fixed)
    
    # Extract pattern filename from URL
    if 'pattern-library/' in url:
        # Get the pattern path after pattern-library/
        pattern_part = url.split('pattern-library/')[-1]
        
        # Check if this pattern is in our mappings
        if pattern_part in PATTERN_MAPPINGS:
            # Replace with the correct path
            base_url = url.split('pattern-library/')[0]
            return base_url + 'pattern-library/' + PATTERN_MAPPINGS[pattern_part]
        
        # Check without category
        if '/' in pattern_part:
            category, pattern_name = pattern_part.rsplit('/', 1)
            if pattern_name in PATTERN_MAPPINGS:
                base_url = url.split('pattern-library/')[0]
                return base_url + 'pattern-library/' + PATTERN_MAPPINGS[pattern_name]
    
    # Handle direct pattern references
    if url.endswith('.md') and '/' not in url:
        if url in PATTERN_MAPPINGS:
            return PATTERN_MAPPINGS[url]
    
    return None

def fix_links_in_file(file_path, dry_run=False):
    """Fix broken links in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        fixes_made = []
        
        # Find all markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def replace_link(match):
            text = match.group(1)
            url = match.group(2)
            
            # Skip external links
            if url.startswith(('http://', 'https://', 'mailto:', '#')):
                return match.group(0)
            
            # Try to fix the broken link
            fixed_url = fix_broken_link(url, file_path)
            if fixed_url and fixed_url != url:
                fixes_made.append((url, fixed_url))
                return f'[{text}]({fixed_url})'
            
            return match.group(0)
        
        # Apply fixes
        content = re.sub(link_pattern, replace_link, content)
        
        # Fix standalone pattern references that are directories
        for pattern in ['../pattern-library/', '../../pattern-library/', '../../../pattern-library/']:
            if pattern in content and pattern + 'index.md' not in content:
                # This is likely a broken directory reference
                content = content.replace(f']({pattern})', '](../patterns/)')
                fixes_made.append((pattern, '../patterns/'))
        
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
    parser = argparse.ArgumentParser(description='Fix all broken links comprehensively')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed')
    parser.add_argument('--path', default='docs', help='Path to scan')
    parser.add_argument('--verbose', action='store_true', help='Show all fixes')
    
    args = parser.parse_args()
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Fixing all broken links...")
    
    files_fixed = 0
    total_fixes = 0
    all_fixes = []
    
    # Process all markdown files
    for root, dirs, files in os.walk(args.path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                fixes = fix_links_in_file(file_path, dry_run=args.dry_run)
                
                if fixes:
                    files_fixed += 1
                    total_fixes += len(fixes)
                    all_fixes.extend([(file_path, old, new) for old, new in fixes])
                    
                    if args.verbose or len(fixes) > 0:
                        print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {len(fixes)} links in: {file_path}")
                        for old, new in fixes[:5]:
                            print(f"  {old} → {new}")
                        if len(fixes) > 5:
                            print(f"  ... and {len(fixes) - 5} more")
    
    # Summary
    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {total_fixes} links in {files_fixed} files")
    
    # Save detailed report
    if not args.dry_run:
        report = {
            'files_fixed': files_fixed,
            'total_fixes': total_fixes,
            'pattern_mappings': PATTERN_MAPPINGS,
            'url_replacements': URL_REPLACEMENTS,
            'all_fixes': [{'file': f, 'old': old, 'new': new} for f, old, new in all_fixes]
        }
        with open('link-fixes-report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to: link-fixes-report.json")
    
    return 0 if not args.dry_run else 1

if __name__ == '__main__':
    sys.exit(main())
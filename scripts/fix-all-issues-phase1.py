#!/usr/bin/env python3
"""
Phase 1: Fix path resolution issues and remove 'Coming Soon' mislabeling.
This will fix approximately 85% of broken links.
"""

import os
import re
import sys

def fix_path_resolution_issues(content, file_path):
    """Fix all path resolution problems."""
    
    # Fix Google interview relative paths
    if 'google-interviews' in file_path:
        content = re.sub(r'\]\(../../patterns/', '](../patterns/', content)
        content = re.sub(r'\]\(../../quantitative/', '](../quantitative/', content)
        content = re.sub(r'\]\(../../case-studies/', '](../case-studies/', content)
        content = re.sub(r'\]\(../../part1-axioms/', '](../part1-axioms/', content)
        content = re.sub(r'\]\(../../part2-pillars/', '](../part2-pillars/', content)
    
    # Fix consistent-hashing references
    content = re.sub(r'/patterns/consistent-hashing\.md\)', '/case-studies/consistent-hashing)', content)
    content = re.sub(r'/patterns/consistent-hashing\)', '/case-studies/consistent-hashing)', content)
    content = re.sub(r'\.\./patterns/consistent-hashing\)', '../case-studies/consistent-hashing)', content)
    
    # Fix retry pattern references
    content = re.sub(r'/patterns/retry\.md\)', '/patterns/retry-backoff)', content)
    content = re.sub(r'/patterns/retry\)', '/patterns/retry-backoff)', content)
    
    # Fix directory index references
    content = re.sub(r'(/part1-axioms/law\d+-[^/]+)\)', r'\1/index)', content)
    content = re.sub(r'(/part2-pillars/[^/]+)\)', r'\1/index)', content)
    
    # Fix ./ relative paths
    content = re.sub(r'\]\(\./', '](', content)
    
    # Fix patterns that should point to existing files
    pattern_mappings = {
        '/patterns/quorum-consensus': '/patterns/consensus',
        '/patterns/quorum\.md': '/patterns/consensus',
        '/patterns/quorum': '/patterns/consensus',
        '/patterns/geospatial-indexing': '/patterns/spatial-indexing',
        '/patterns/replication\.md': '/patterns/leader-follower',
        '/patterns/replication': '/patterns/leader-follower',
    }
    
    for old, new in pattern_mappings.items():
        content = re.sub(old + r'\)', new + ')', content)
    
    return content

def remove_coming_soon_mislabeling(content):
    """Remove 'Coming Soon' labels from existing content."""
    
    # List of patterns that exist but are marked as "Coming Soon"
    existing_patterns = [
        'ambassador', 'anti-corruption-layer', 'api-gateway', 'auto-scaling',
        'backends-for-frontends', 'bulkhead', 'cache-aside', 'caching-strategies',
        'cdc', 'cell-based', 'circuit-breaker', 'cqrs', 'data-lake', 'data-mesh',
        'distributed-lock', 'distributed-queue', 'edge-computing', 'event-driven',
        'event-sourcing', 'event-streaming', 'fault-tolerance', 'finops',
        'geo-replication', 'gossip-protocol', 'graceful-degradation', 'graphql-federation',
        'health-check', 'heartbeat', 'kappa-architecture', 'lambda-architecture',
        'leader-election', 'leader-follower', 'load-balancing', 'load-shedding',
        'materialized-view', 'merkle-trees', 'multi-region', 'observability',
        'outbox', 'polyglot-persistence', 'rate-limiting', 'read-through-cache',
        'request-batching', 'retry-backoff', 'saga', 'service-discovery',
        'service-mesh', 'service-registry', 'sharding', 'sidecar', 'timeout',
        'two-phase-commit', 'vector-clocks', 'wal', 'write-behind-cache',
        'write-through-cache'
    ]
    
    # Remove "Coming Soon" from these patterns
    for pattern in existing_patterns:
        # Match various "Coming Soon" formats
        content = re.sub(
            rf'(\[.*?\]\(/patterns/{pattern}/?\))(\s*(?:\(Coming Soon\)|Coming Soon|<[^>]*>Coming Soon<[^>]*>))',
            r'\1',
            content
        )
        content = re.sub(
            rf'({pattern})(\s*\(Coming Soon\))',
            r'\1',
            content,
            flags=re.IGNORECASE
        )
    
    return content

def fix_google_interview_paths(content, file_path):
    """Fix Google interview specific path issues."""
    
    if 'google-interviews' in file_path:
        # Fix dashboard.md specific pattern paths
        mappings = {
            'patterns/application/ads-systems.md': 'google-ads',
            'patterns/application/media-platforms.md': 'youtube',
            'patterns/application/communication-systems.md': 'gmail',
            'patterns/infrastructure/geo-systems.md': 'google-maps',
            'patterns/data/storage-systems.md': 'google-drive',
            'patterns/data/ml-data-systems.md': 'google-photos',
            'patterns/infrastructure/cloud-infrastructure.md': '#',  # Placeholder
            'patterns/infrastructure/mobile-platforms.md': '#',  # Placeholder
            'patterns/application/marketplace-systems.md': '#',  # Placeholder
        }
        
        for old, new in mappings.items():
            if new != '#':
                content = re.sub(rf'\({old}\)', f'({new})', content)
            else:
                content = re.sub(rf'\[Guide\]\({old}\)', '[Guide (Coming Soon)](#)', content)
    
    return content

def process_file(file_path):
    """Process a single file with all Phase 1 fixes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all Phase 1 fixes
        content = fix_path_resolution_issues(content, file_path)
        content = remove_coming_soon_mislabeling(content)
        content = fix_google_interview_paths(content, file_path)
        
        # Save if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function."""
    print("Phase 1: Fixing path resolution issues and removing 'Coming Soon' mislabeling...")
    print("-" * 80)
    
    files_fixed = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                if process_file(file_path):
                    files_fixed += 1
                    print(f"Fixed: {file_path}")
    
    print(f"\nPhase 1 Complete: Fixed {files_fixed} files")
    
    # Run verification
    print("\nRunning verification...")
    os.system("python3 scripts/verify-links.py 2>&1 | grep -E '(Files checked:|Total internal links found:|Broken links found:)'")

if __name__ == "__main__":
    main()
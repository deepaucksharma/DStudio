#!/usr/bin/env python3
"""
Comprehensive script to fix broken internal links in markdown files.
"""

import os
import re
from pathlib import Path
import sys

# Mapping of broken patterns to correct paths
LINK_MAPPING = {
    # Pattern fixes - directories
    '/patterns/pattern-selector/': '/patterns/pattern-selector',
    '/patterns/pattern-matrix/': '/patterns/pattern-matrix',
    '/patterns/geospatial-indexing/': '/patterns/spatial-indexing',
    '/patterns/caching/': '/patterns/caching-strategies',
    '/reference/cheat-sheets/': '/reference/cheat-sheets',
    '/reference/glossary/': '/reference/glossary',
    '/reference/recipe-cards/': '/reference/recipe-cards',
    '/introduction/getting-started/': '/introduction/getting-started',
    
    # Google system case studies
    '/case-studies/google-systems/google-search/': '/case-studies/google-systems/google-search',
    '/case-studies/google-systems/google-youtube/': '/case-studies/google-systems/google-youtube',
    '/case-studies/google-systems/google-maps-system/': '/case-studies/google-systems/google-maps',
    '/case-studies/google-systems/google-gmail/': '/case-studies/google-systems/google-gmail',
    '/case-studies/google-systems/google-docs/': '/case-studies/google-systems/google-docs',
    
    # Case studies that should point to existing files
    '/case-studies/amazon-aurora/': '/case-studies/amazon-aurora',
    '/case-studies/s3-object-storage-enhanced/': '/case-studies/s3-object-storage-enhanced',
    '/case-studies/google-drive/': '/case-studies/google-drive',
    '/case-studies/google-maps/': '/case-studies/google-maps',
    '/case-studies/youtube/': '/case-studies/youtube',
    '/case-studies/netflix-streaming/': '/case-studies/netflix-streaming',
    '/case-studies/apple-maps/': '/case-studies/apple-maps',
    '/case-studies/twitter-timeline/': '/case-studies/twitter-timeline',
    '/case-studies/chat-system/': '/case-studies/chat-system',
    '/case-studies/consistency-deep-dive-chat/': '/case-studies/consistency-deep-dive-chat',
    '/case-studies/distributed-email-enhanced/': '/case-studies/distributed-email-enhanced',
    '/case-studies/distributed-message-queue/': '/case-studies/distributed-message-queue',
    '/case-studies/news-feed/': '/case-studies/news-feed',
    '/case-studies/notification-system/': '/case-studies/notification-system',
    '/case-studies/social-media-feed/': '/case-studies/social-media-feed',
    '/case-studies/apache-spark/': '/case-studies/apache-spark',
    '/case-studies/consistent-hashing/': '/case-studies/consistent-hashing',
    '/case-studies/elasticsearch/': '/case-studies/elasticsearch',
    '/case-studies/key-value-store/': '/case-studies/key-value-store',
    '/case-studies/mapreduce/': '/case-studies/mapreduce',
    '/case-studies/memcached/': '/case-studies/memcached',
    '/case-studies/mongodb/': '/case-studies/mongodb',
    '/case-studies/object-storage/': '/case-studies/object-storage',
    '/case-studies/redis-architecture/': '/case-studies/redis-architecture',
    '/case-studies/zookeeper/': '/case-studies/zookeeper',
    '/case-studies/digital-wallet-enhanced/': '/case-studies/digital-wallet-enhanced',
    '/case-studies/ecommerce-platform/': '/case-studies/ecommerce-platform',
    '/case-studies/hotel-reservation/': '/case-studies/hotel-reservation',
    '/case-studies/payment-system/': '/case-studies/payment-system',
    '/case-studies/stock-exchange/': '/case-studies/stock-exchange',
    '/case-studies/find-my-device/': '/case-studies/find-my-device',
    '/case-studies/here-maps/': '/case-studies/here-maps',
    '/case-studies/life360/': '/case-studies/life360',
    '/case-studies/nearby-friends/': '/case-studies/nearby-friends',
    '/case-studies/openstreetmap/': '/case-studies/openstreetmap',
    '/case-studies/proximity-service/': '/case-studies/proximity-service',
    '/case-studies/snap-map/': '/case-studies/snap-map',
    '/case-studies/strava-heatmaps/': '/case-studies/strava-heatmaps',
    '/case-studies/uber-maps/': '/case-studies/uber-maps',
    '/case-studies/search-autocomplete/': '/case-studies/search-autocomplete',
    '/case-studies/web-crawler/': '/case-studies/web-crawler',
    '/case-studies/ad-click-aggregation/': '/case-studies/ad-click-aggregation',
    '/case-studies/gaming-leaderboard-enhanced/': '/case-studies/gaming-leaderboard-enhanced',
    '/case-studies/vault/': '/case-studies/vault',
    '/case-studies/kubernetes/': '/case-studies/kubernetes',
    '/case-studies/metrics-monitoring/': '/case-studies/metrics-monitoring',
    '/case-studies/prometheus/': '/case-studies/prometheus',
    '/case-studies/prometheus-datadog-enhanced/': '/case-studies/prometheus-datadog-enhanced',
    '/case-studies/rate-limiter/': '/case-studies/rate-limiter',
    '/case-studies/unique-id-generator/': '/case-studies/unique-id-generator',
    '/case-studies/url-shortener/': '/case-studies/url-shortener',
    '/case-studies/video-streaming/': '/case-studies/video-streaming',
    
    # Pattern fixes
    '/patterns/service-mesh/': '/patterns/service-mesh',
    '/patterns/sidecar/': '/patterns/sidecar',
    '/patterns/event-sourcing/': '/patterns/event-sourcing',
    '/patterns/cqrs/': '/patterns/cqrs',
    '/patterns/saga/': '/patterns/saga',
    '/patterns/event-streaming/': '/patterns/event-streaming',
    '/patterns/data-mesh/': '/patterns/data-mesh',
    '/patterns/lambda-architecture/': '/patterns/lambda-architecture',
    '/patterns/kappa-architecture/': '/patterns/kappa-architecture',
    '/patterns/cdc/': '/patterns/cdc',
    '/patterns/geo-replication/': '/patterns/geo-replication',
    '/patterns/edge-computing/': '/patterns/edge-computing',
    '/patterns/cell-based/': '/patterns/cell-based',
    '/patterns/graceful-degradation/': '/patterns/graceful-degradation',
    '/patterns/e2e-encryption/': '/patterns/e2e-encryption',
    '/patterns/key-management/': '/patterns/key-management',
    '/patterns/consent-management/': '/patterns/consent-management',
    '/patterns/finops/': '/patterns/finops',
    '/patterns/serverless-faas/': '/patterns/serverless-faas',
    '/patterns/auto-scaling/': '/patterns/auto-scaling',
    '/patterns/retry-backoff/': '/patterns/retry-backoff',
    '/patterns/health-check/': '/patterns/health-check',
    '/patterns/load-balancing/': '/patterns/load-balancing',
    '/patterns/rate-limiting/': '/patterns/rate-limiting',
    '/patterns/timeout/': '/patterns/timeout',
    '/patterns/distributed-lock/': '/patterns/distributed-lock',
    '/patterns/two-phase-commit/': '/patterns/two-phase-commit',
    '/patterns/logical-clocks/': '/patterns/logical-clocks',
    '/patterns/crdt/': '/patterns/crdt',
    '/patterns/outbox/': '/patterns/outbox',
    '/patterns/split-brain/': '/patterns/split-brain',
    '/patterns/clock-sync/': '/patterns/clock-sync',
    '/patterns/cache-aside/': '/patterns/cache-aside',
    '/patterns/read-through-cache/': '/patterns/read-through-cache',
    '/patterns/write-through-cache/': '/patterns/write-through-cache',
    '/patterns/write-behind-cache/': '/patterns/write-behind-cache',
    
    # Learning paths
    '/learning-paths/performance/': '/learning-paths/performance',
    '/learning-paths/reliability/': '/learning-paths/reliability',
    '/learning-paths/security/': '/learning-paths/senior-engineer',
    
    # Quantitative
    '/quantitative/pacelc/': '/quantitative/cap-theorem',
    '/quantitative/littles-law/': '/quantitative/littles-law',
    '/quantitative/queueing-models/': '/quantitative/queueing-models',
    '/quantitative/computational-geometry/': '/quantitative/comp-geometry',
    
    # Pillars
    '/part2-pillars/work-distribution/': '/part2-pillars/work',
    '/part2-pillars/state-distribution/': '/part2-pillars/state',
    '/part2-pillars/intelligence-distribution/': '/part2-pillars/intelligence',
    
    # Non-existent files that should be fixed
    '/case-studies/apache-kafka.md': '/case-studies/kafka',
    '/case-studies/blockchain-consensus.md': '/case-studies/blockchain',
    '/case-studies/amazon-search.md': '/case-studies/amazon-dynamo',
    '/case-studies/doordash/': '/case-studies/uber-location',
    '/case-studies/lyft/': '/case-studies/uber-location',
    '/case-studies/netflix-scale.md': '/case-studies/netflix-chaos',
    '/case-studies/discord-messages.md': '/case-studies/chat-system',
    '/case-studies/scylladb.md': '/case-studies/cassandra',
    '/case-studies/airbnb-architecture/': '/case-studies/hotel-reservation',
    '/case-studies/linkedin-architecture/': '/case-studies/social-graph',
    
    # Pattern aliases
    '/patterns/zero-trust/': '/patterns/key-management',
    '/patterns/chaos-engineering/': '/human-factors/chaos-engineering',
    '/patterns/resource-optimization/': '/patterns/auto-scaling',
    '/patterns/spot-instances/': '/patterns/finops',
    '/patterns/multi-cloud/': '/patterns/multi-region',
    '/patterns/time-series/': '/patterns/time-series-ids',
    '/patterns/geospatial-indexing': '/patterns/spatial-indexing',
    '/patterns/caching': '/patterns/caching-strategies',
    '/patterns/privacy.md': '/patterns/location-privacy',
    
    # Google interview specific
    '/preparation-guide': '/google-interviews/preparation-guide',
    '/common-mistakes': '/google-interviews/common-mistakes',
    '/google-search': '/google-interviews/google-search',
}

def fix_links_in_file(file_path):
    """Fix all broken links in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Process each mapping
    for broken_pattern, correct_pattern in LINK_MAPPING.items():
        # Create regex pattern to match links
        if broken_pattern.endswith('.md'):
            # Exact file match
            pattern = r'\[([^\]]+)\]\(' + re.escape(broken_pattern) + r'\)'
            replacement = f'[\\1]({correct_pattern})'
        else:
            # Directory or path match
            pattern = r'\[([^\]]+)\]\(([^)]*' + re.escape(broken_pattern) + r'[^)]*)\)'
            
            def replace_func(match):
                link_text = match.group(1)
                link_url = match.group(2)
                new_url = link_url.replace(broken_pattern, correct_pattern)
                return f'[{link_text}]({new_url})'
            
            content = re.sub(pattern, replace_func, content)
            continue
        
        # Apply simple replacement
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            changes_made += 1
    
    # Fix relative paths that are incorrect
    # Fix patterns like ../../patterns/ to ../patterns/ when appropriate
    if '/case-studies/' in file_path:
        content = re.sub(r'\]\(../../patterns/', '](../../patterns/', content)
        content = re.sub(r'\]\(../../quantitative/', '](../../quantitative/', content)
    
    if '/patterns/' in file_path:
        content = re.sub(r'\]\(../patterns/', '](../patterns/', content)
    
    # Save if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Main function."""
    print("Applying comprehensive link fixes...")
    print("-" * 80)
    
    files_fixed = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                try:
                    if fix_links_in_file(file_path):
                        files_fixed += 1
                        print(f"Fixed links in: {file_path}")
                
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    print(f"\nFixed links in {files_fixed} files")
    
    # Run verification again
    print("\nRunning verification to check remaining broken links...")
    os.system("python3 scripts/verify-links.py")

if __name__ == "__main__":
    main()
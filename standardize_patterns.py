#!/usr/bin/env python3

import os
import re
from datetime import datetime
from pathlib import Path

# Pattern categorization mapping
PATTERN_CATEGORIES = {
    # Caching patterns
    'cache-aside.md': 'caching',
    'caching.md': 'caching',
    'caching-strategies.md': 'caching',
    'read-through-cache.md': 'caching',
    'write-through-cache.md': 'caching',
    'write-behind-cache.md': 'caching',
    'tile-caching.md': 'caching',
    
    # Distributed data patterns
    'sharding.md': 'distributed-data',
    'eventual-consistency.md': 'distributed-data',
    'event-sourcing.md': 'distributed-data',
    'cdc.md': 'distributed-data',
    'crdt.md': 'distributed-data',
    'vector-clocks.md': 'distributed-data',
    'merkle-trees.md': 'distributed-data',
    'anti-entropy.md': 'distributed-data',
    'data-lake.md': 'distributed-data',
    'data-mesh.md': 'distributed-data',
    'geo-replication.md': 'distributed-data',
    'multi-region.md': 'distributed-data',
    'distributed-storage.md': 'distributed-data',
    'lsm-tree.md': 'distributed-data',
    'bloom-filter.md': 'distributed-data',
    'distributed-dedup.md': 'distributed-data',
    
    # Resilience patterns
    'circuit-breaker.md': 'resilience',
    'circuit-breaker-enhanced.md': 'resilience',
    'retry-backoff.md': 'resilience',
    'bulkhead.md': 'resilience',
    'graceful-degradation.md': 'resilience',
    'failover.md': 'resilience',
    'fault-tolerance.md': 'resilience',
    'timeout.md': 'resilience',
    'backpressure.md': 'resilience',
    'load-shedding.md': 'resilience',
    'health-check.md': 'resilience',
    
    # Communication patterns
    'api-gateway.md': 'communication',
    'graphql-federation.md': 'communication',
    'websocket.md': 'communication',
    'scatter-gather.md': 'communication',
    'outbox.md': 'communication',
    'idempotent-receiver.md': 'communication',
    'choreography.md': 'communication',
    'saga.md': 'communication',
    'distributed-queue.md': 'communication',
    'priority-queue.md': 'communication',
    'backends-for-frontends.md': 'communication',
    
    # Architectural patterns
    'service-mesh.md': 'architectural',
    'sidecar.md': 'architectural',
    'cell-based.md': 'architectural',
    'event-driven.md': 'architectural',
    'lambda-architecture.md': 'architectural',
    'kappa-architecture.md': 'architectural',
    'strangler-fig.md': 'architectural',
    'anti-corruption-layer.md': 'architectural',
    'shared-nothing.md': 'architectural',
    'actor-model.md': 'architectural',
    'ambassador.md': 'architectural',
    'edge-computing.md': 'architectural',
    'cqrs.md': 'architectural',
    
    # Security patterns
    'valet-key.md': 'security',
    'e2e-encryption.md': 'security',
    'key-management.md': 'security',
    'consent-management.md': 'security',
    'location-privacy.md': 'security',
    'security-shortener.md': 'security',
    
    # Performance patterns
    'network-optimization.md': 'performance',
    'battery-optimization.md': 'performance',
    'chunking.md': 'performance',
    'delta-sync.md': 'performance',
    'client-rendering.md': 'performance',
    'adaptive-scheduling.md': 'performance',
    'auto-scaling.md': 'performance',
    
    # Specialized patterns
    'service-discovery.md': 'specialized',
    'service-registry.md': 'specialized',
    'leader-election.md': 'specialized',
    'leader-follower.md': 'specialized',
    'consensus.md': 'specialized',
    'distributed-lock.md': 'specialized',
    'two-phase-commit.md': 'specialized',
    'gossip-protocol.md': 'specialized',
    'clock-sync.md': 'specialized',
    'hlc.md': 'specialized',
    'split-brain.md': 'specialized',
    'metadata-service.md': 'specialized',
    'rate-limiting.md': 'specialized',
    'cap-theorem.md': 'specialized',
    'tunable-consistency.md': 'specialized',
    'cas.md': 'specialized',
    'id-generation-scale.md': 'specialized',
    'time-series-ids.md': 'specialized',
    'spatial-indexing.md': 'specialized',
    'geohashing.md': 'specialized',
    'tile-pyramid.md': 'specialized',
    'vector-tiles.md': 'specialized',
    'vector-maps.md': 'specialized',
    'trie.md': 'specialized',
    'url-frontier.md': 'specialized',
    'url-normalization.md': 'specialized',
    'deduplication.md': 'specialized',
    'js-crawling.md': 'specialized',
    'politeness.md': 'specialized',
    'ml-pipeline.md': 'specialized',
    'analytics-scale.md': 'specialized',
    'real-time.md': 'specialized',
    'geo-distribution.md': 'specialized',
    'observability.md': 'specialized',
    'client-library-design.md': 'specialized',
}

# Status mapping based on content length and structure
def determine_status(content):
    """Determine status based on content analysis"""
    lines = content.strip().split('\n')
    
    # Check for TODO or under construction markers
    if any('TODO' in line or 'under construction' in line or 'coming soon' in line.lower() for line in lines):
        return 'stub'
    
    # Check for 5-level structure
    levels = ['Level 1:', 'Level 2:', 'Level 3:', 'Level 4:', 'Level 5:']
    level_count = sum(1 for level in levels if any(level in line for line in lines))
    
    if level_count >= 4:
        return 'complete'
    elif level_count >= 2:
        return 'partial'
    elif len(lines) < 50:
        return 'stub'
    else:
        return 'partial'

def extract_frontmatter(content):
    """Extract existing frontmatter from content"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1].strip(), parts[2]
    return '', content

def parse_frontmatter(fm_text):
    """Parse frontmatter into dictionary"""
    fm_dict = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            fm_dict[key.strip()] = value.strip().strip('"').strip("'")
    return fm_dict

def update_pattern_file(filepath):
    """Update a single pattern file with standardized frontmatter"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    
    # Skip template and index files
    if filename in ['PATTERN_TEMPLATE.md', 'index.md']:
        return False
    
    # Extract existing frontmatter
    fm_text, body = extract_frontmatter(content)
    fm_dict = parse_frontmatter(fm_text) if fm_text else {}
    
    # Determine category
    category = PATTERN_CATEGORIES.get(filename, 'specialized')
    
    # Determine status
    status = determine_status(content)
    
    # Update frontmatter fields
    updated_fm = {
        'title': fm_dict.get('title', filename.replace('.md', '').replace('-', ' ').title()),
        'description': fm_dict.get('description', f'Pattern for {category} in distributed systems'),
        'type': 'pattern',
        'category': category,
        'difficulty': fm_dict.get('difficulty', 'intermediate'),
        'reading_time': fm_dict.get('reading_time', '30 min'),
        'prerequisites': fm_dict.get('prerequisites', '[]'),
        'when_to_use': fm_dict.get('when_to_use', f'When dealing with {category} challenges'),
        'when_not_to_use': fm_dict.get('when_not_to_use', 'When simpler solutions suffice'),
        'status': status,
        'last_updated': fm_dict.get('last_updated', datetime.now().strftime('%Y-%m-%d'))
    }
    
    # Build new frontmatter
    new_fm_lines = ['---']
    for key, value in updated_fm.items():
        if key == 'prerequisites' and value == '[]':
            new_fm_lines.append(f'{key}: []')
        else:
            new_fm_lines.append(f'{key}: {value}')
    new_fm_lines.append('---')
    
    # Ensure proper navigation breadcrumb
    if body.strip():
        lines = body.strip().split('\n')
        nav_line = '[Home](../introduction/index.md) → [Part III: Patterns](index.md) → **' + updated_fm['title'] + '**'
        
        # Check if navigation line exists
        has_nav = False
        nav_index = -1
        for i, line in enumerate(lines):
            if '[Home]' in line and '[Part III: Patterns]' in line:
                has_nav = True
                nav_index = i
                break
        
        # Add or update navigation
        if not has_nav:
            # Insert after blank lines following frontmatter
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#'):
                    insert_pos = i
                    break
            lines.insert(insert_pos, '')
            lines.insert(insert_pos + 1, '<!-- Navigation -->')
            lines.insert(insert_pos + 2, nav_line)
            lines.insert(insert_pos + 3, '')
        else:
            # Update existing navigation
            lines[nav_index] = nav_line
    
    # Write updated content
    new_content = '\n'.join(new_fm_lines) + '\n' + '\n'.join(lines) if body.strip() else '\n'.join(new_fm_lines)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True

def fix_specific_patterns():
    """Fix specific patterns with known issues"""
    patterns_dir = Path('/Users/deepaksharma/syc/DStudio/docs/patterns')
    
    # Fix tile-caching.md
    tile_caching_path = patterns_dir / 'tile-caching.md'
    if tile_caching_path.exists():
        with open(tile_caching_path, 'r') as f:
            content = f.read()
        
        # Update with proper structure
        new_content = """---
title: Tile Caching
description: Efficient caching strategy for map tiles and spatial data at multiple zoom levels
type: pattern
category: caching
difficulty: intermediate
reading_time: 25 min
prerequisites: [caching, spatial-indexing]
when_to_use: Map applications, GIS systems, spatial data visualization
when_not_to_use: Non-spatial data, dynamic content that changes frequently
status: partial
last_updated: 2025-01-23
---

<!-- Navigation -->
[Home](../introduction/index.md) → [Part III: Patterns](index.md) → **Tile Caching**

# Tile Caching

**Optimize map rendering with pre-computed tile pyramids**

> *"Why render the world every time when you can cache it once?"*

## Overview

Tile caching optimizes the storage and delivery of map tiles by pre-rendering and caching spatial data at multiple zoom levels. This pattern is fundamental to modern mapping applications.

## Key Concepts

- **Tile Pyramid**: Pre-rendered tiles at multiple zoom levels
- **Cache Hierarchy**: Multi-level caching from edge to origin
- **Invalidation Strategy**: Updating tiles when data changes

## Related Patterns
- [CDN Pattern](../patterns/edge-computing.md)
- [Cache-Aside](cache-aside.md)
- [Spatial Indexing](spatial-indexing.md)
- [Vector Maps](vector-maps.md)

## References
- [Google Maps Case Study](../case-studies/google-maps.md) - Implements multi-level tile caching
"""
        with open(tile_caching_path, 'w') as f:
            f.write(new_content)
    
    # Fix graceful-degradation.md structure
    graceful_path = patterns_dir / 'graceful-degradation.md'
    if graceful_path.exists():
        # Just update its frontmatter category
        update_pattern_file(graceful_path)
    
    # Fix retry-backoff.md extra sections
    retry_path = patterns_dir / 'retry-backoff.md'
    if retry_path.exists():
        with open(retry_path, 'r') as f:
            content = f.read()
        
        # Find and remove extra sections at the end if they exist
        # Pattern files should end with the last main section
        lines = content.split('\n')
        # Keep the standard structure
        new_lines = []
        in_extra_section = False
        for line in lines:
            # Detect if we're past the main content structure
            if line.strip() == '## Extra Section' or line.strip() == '### Non-Standard Section':
                in_extra_section = True
            if not in_extra_section:
                new_lines.append(line)
        
        with open(retry_path, 'w') as f:
            f.write('\n'.join(new_lines))

def main():
    """Main function to standardize all pattern files"""
    patterns_dir = Path('/Users/deepaksharma/syc/DStudio/docs/patterns')
    
    # First fix specific known issues
    print("Fixing specific pattern issues...")
    fix_specific_patterns()
    
    # Then standardize all patterns
    updated_count = 0
    total_count = 0
    
    for pattern_file in patterns_dir.glob('*.md'):
        total_count += 1
        if update_pattern_file(pattern_file):
            updated_count += 1
            print(f"Updated: {pattern_file.name}")
    
    print(f"\nStandardization complete!")
    print(f"Total files processed: {total_count}")
    print(f"Files updated: {updated_count}")
    
    # Report on status distribution
    status_counts = {'stub': 0, 'partial': 0, 'complete': 0}
    for pattern_file in patterns_dir.glob('*.md'):
        if pattern_file.name not in ['PATTERN_TEMPLATE.md', 'index.md']:
            with open(pattern_file, 'r') as f:
                content = f.read()
            fm_text, _ = extract_frontmatter(content)
            fm_dict = parse_frontmatter(fm_text)
            status = fm_dict.get('status', 'unknown')
            if status in status_counts:
                status_counts[status] += 1
    
    print(f"\nStatus distribution:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Add pattern implementation references to all law files."""

from pathlib import Path
import re

def get_patterns_for_law(law_name):
    """Get patterns that implement each law."""
    law_patterns = {
        'correlated-failure': [
            ('Bulkhead', 'resilience/bulkhead.md', 'Isolates failures to prevent correlation'),
            ('Circuit Breaker', 'resilience/circuit-breaker.md', 'Prevents cascading failures'),
            ('Failover', 'resilience/failover.md', 'Handles correlated infrastructure failures'),
            ('Health Check', 'resilience/health-check.md', 'Detects correlated failures early'),
            ('Cell-Based Architecture', 'architecture/cell-based.md', 'Limits blast radius of failures'),
        ],
        'asynchronous-reality': [
            ('Event Sourcing', 'data-management/event-sourcing.md', 'Embraces asynchronous event flow'),
            ('CQRS', 'data-management/cqrs.md', 'Separates async read/write paths'),
            ('Eventual Consistency', 'data-management/eventual-consistency.md', 'Accepts async propagation delays'),
            ('Saga', 'data-management/saga.md', 'Manages async distributed transactions'),
            ('Message Queue', 'communication/publish-subscribe.md', 'Decouples async communication'),
        ],
        'emergent-chaos': [
            ('Chaos Engineering', '../architects-handbook/human-factors/chaos-engineering.md', 'Proactively discovers emergent failures'),
            ('Circuit Breaker', 'resilience/circuit-breaker.md', 'Prevents emergent cascade effects'),
            ('Rate Limiting', 'scaling/rate-limiting.md', 'Controls emergent load patterns'),
            ('Backpressure', 'scaling/backpressure.md', 'Manages emergent congestion'),
            ('Graceful Degradation', 'resilience/graceful-degradation.md', 'Handles emergent overload'),
        ],
        'multidimensional-optimization': [
            ('CAP Theorem', 'architecture/cap-theorem.md', 'Fundamental trade-off framework'),
            ('Tunable Consistency', 'data-management/tunable-consistency.md', 'Adjustable trade-offs'),
            ('Caching Strategies', 'scaling/caching-strategies.md', 'Speed vs consistency trade-offs'),
            ('Sharding', 'scaling/sharding.md', 'Scale vs complexity trade-offs'),
            ('Lambda Architecture', 'architecture/lambda-architecture.md', 'Batch vs stream trade-offs'),
        ],
        'distributed-knowledge': [
            ('Consensus', 'coordination/consensus.md', 'Agrees on shared truth despite partial knowledge'),
            ('Leader Election', 'coordination/leader-election.md', 'Selects authority with incomplete info'),
            ('Gossip Protocol', 'communication/gossip.md', 'Spreads knowledge probabilistically'),
            ('CRDT', 'data-management/crdt.md', 'Merges distributed updates without coordination'),
            ('Vector Clocks', 'coordination/logical-clocks.md', 'Tracks causality with partial knowledge'),
        ],
        'cognitive-load': [
            ('API Gateway', 'communication/api-gateway.md', 'Simplifies client complexity'),
            ('Service Mesh', 'communication/service-mesh.md', 'Abstracts network complexity'),
            ('Backends for Frontends', 'architecture/backends-for-frontends.md', 'Tailors complexity per client'),
            ('Aggregator', 'architecture/aggregator.md', 'Reduces client orchestration burden'),
            ('GraphQL Federation', 'architecture/graphql-federation.md', 'Unifies complex data graphs'),
        ],
        'economic-reality': [
            ('Auto-scaling', 'scaling/auto-scaling.md', 'Optimizes resource costs dynamically'),
            ('Serverless', 'architecture/serverless-faas.md', 'Pay-per-use cost model'),
            ('Cold Storage Tiers', 'data-management/data-lake.md', 'Optimizes storage costs by access patterns'),
            ('Request Batching', 'scaling/request-batching.md', 'Amortizes fixed costs'),
            ('Edge Computing', 'scaling/edge-computing.md', 'Reduces bandwidth costs'),
        ],
    }
    return law_patterns.get(law_name, [])

def add_pattern_section(file_path, law_name):
    """Add pattern implementation section to a law file."""
    content = file_path.read_text()
    
    # Check if pattern section already exists
    if '## Patterns Addressing This Law' in content or '## Pattern Implementations' in content:
        print(f"Pattern section already exists in {file_path.name}")
        return False
    
    # Find where to insert (before Related Topics or at end)
    insert_marker = '## Related Topics'
    if insert_marker not in content:
        insert_marker = '## References'
    if insert_marker not in content:
        # Add at end
        insert_pos = len(content)
    else:
        insert_pos = content.find(insert_marker)
    
    # Build pattern section
    patterns = get_patterns_for_law(law_name)
    if not patterns:
        return False
    
    pattern_section = '\n## Pattern Implementations\n\n'
    pattern_section += 'Patterns that address this law:\n\n'
    
    for pattern_name, pattern_path, description in patterns:
        pattern_section += f'- **[{pattern_name}](../../pattern-library/{pattern_path})** - {description}\n'
    
    pattern_section += '\n'
    
    # Insert section
    new_content = content[:insert_pos] + pattern_section + content[insert_pos:]
    file_path.write_text(new_content)
    
    return True

def main():
    """Add pattern references to all law files."""
    laws_dir = Path("docs/core-principles/laws")
    
    law_files = {
        'correlated-failure.md': 'correlated-failure',
        'asynchronous-reality.md': 'asynchronous-reality',
        'emergent-chaos.md': 'emergent-chaos',
        'multidimensional-optimization.md': 'multidimensional-optimization',
        'distributed-knowledge.md': 'distributed-knowledge',
        'cognitive-load.md': 'cognitive-load',
        'economic-reality.md': 'economic-reality',
    }
    
    fixed_count = 0
    for filename, law_name in law_files.items():
        file_path = laws_dir / filename
        if file_path.exists():
            if add_pattern_section(file_path, law_name):
                print(f"Added pattern references to {filename}")
                fixed_count += 1
        else:
            print(f"Warning: {filename} not found")
    
    print(f"\nTotal law files updated: {fixed_count}")

if __name__ == "__main__":
    main()
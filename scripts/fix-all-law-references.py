#!/usr/bin/env python3
"""Fix all old law/axiom references to use new paths."""

import re
from pathlib import Path

def get_law_mappings():
    """Define all old to new path mappings."""
    return {
        # Old axiom paths to new law paths
        '/core-principles/axioms/law1-failure': '/core-principles/laws/correlated-failure',
        '/part1-axioms/law1-failure': '/core-principles/laws/correlated-failure',
        'part1-axioms/law1-failure': '/core-principles/laws/correlated-failure',
        
        '/core-principles/axioms/law2-asynchrony': '/core-principles/laws/asynchronous-reality',
        '/part1-axioms/law2-asynchrony': '/core-principles/laws/asynchronous-reality',
        'part1-axioms/law2-asynchrony': '/core-principles/laws/asynchronous-reality',
        
        '/core-principles/axioms/law3-chaos': '/core-principles/laws/emergent-chaos',
        '/part1-axioms/law3-chaos': '/core-principles/laws/emergent-chaos',
        'part1-axioms/law3-chaos': '/core-principles/laws/emergent-chaos',
        
        '/core-principles/axioms/law4-tradeoffs': '/core-principles/laws/multidimensional-optimization',
        '/part1-axioms/law4-tradeoffs': '/core-principles/laws/multidimensional-optimization',
        'part1-axioms/law4-tradeoffs': '/core-principles/laws/multidimensional-optimization',
        
        '/core-principles/axioms/law5-epistemology': '/core-principles/laws/distributed-knowledge',
        '/part1-axioms/law5-epistemology': '/core-principles/laws/distributed-knowledge',
        'part1-axioms/law5-epistemology': '/core-principles/laws/distributed-knowledge',
        
        '/core-principles/axioms/law6-load': '/core-principles/laws/cognitive-load',
        '/part1-axioms/law6-load': '/core-principles/laws/cognitive-load',
        'part1-axioms/law6-load': '/core-principles/laws/cognitive-load',
        
        '/core-principles/axioms/law7-economics': '/core-principles/laws/economic-reality',
        '/part1-axioms/law7-economics': '/core-principles/laws/economic-reality',
        'part1-axioms/law7-economics': '/core-principles/laws/economic-reality',
        
        # Also fix axioms directory references
        '/core-principles/axioms/': '/core-principles/laws/',
        '/part1-axioms/': '/core-principles/laws/',
        'part1-axioms/': '/core-principles/laws/',
    }

def fix_law_references(content: str, current_file: Path) -> str:
    """Fix all law references in content."""
    mappings = get_law_mappings()
    
    # Sort by length to fix longer paths first
    sorted_mappings = sorted(mappings.items(), key=lambda x: len(x[0]), reverse=True)
    
    for old_path, new_path in sorted_mappings:
        # Fix in markdown links
        content = content.replace(f']({old_path})', f']({new_path})')
        content = content.replace(f']({old_path}.md)', f']({new_path}.md)')
        content = content.replace(f']({old_path}/)', f']({new_path}/)')
        
        # Fix in plain text references
        if old_path.startswith('/'):
            content = content.replace(f' {old_path} ', f' {new_path} ')
            content = content.replace(f' {old_path}.', f' {new_path}.')
            content = content.replace(f' {old_path},', f' {new_path},')
    
    # Convert absolute paths to relative where appropriate
    if 'pattern-library' in str(current_file):
        # In pattern library, use relative paths to core-principles
        content = content.replace('](/core-principles/laws/', '](../../core-principles/laws/')
    elif 'architects-handbook' in str(current_file):
        # In architects handbook, use relative paths
        content = content.replace('](/core-principles/laws/', '](../../core-principles/laws/')
    elif 'core-principles/pillars' in str(current_file):
        # In pillars, use relative paths to laws
        content = content.replace('](/core-principles/laws/', '](../laws/')
    
    return content

def main():
    """Fix all law references across the documentation."""
    docs_dir = Path("docs")
    fixed_count = 0
    
    # Files identified with old references
    files_to_fix = [
        "core-principles/pillars/state-distribution.md",
        "core-principles/pillars/work-distribution.md",
        "reference/law-mapping-guide.md",
        "pattern-library/resilience/bulkhead.md",
        "pattern-library/resilience/failover.md",
        "pattern-library/resilience/heartbeat.md",
        "pattern-library/resilience/split-brain.md",
        "pattern-library/communication/grpc.md",
        "pattern-library/resilience/load-shedding.md",
        "pattern-library/communication/api-gateway.md",
        "pattern-library/communication/service-registry.md",
        "pattern-library/scaling/load-balancing.md",
        "pattern-library/scaling/rate-limiting.md",
        "pattern-library/scaling/auto-scaling.md",
        "pattern-library/scaling/analytics-scale.md",
        "pattern-library/scaling/backpressure.md",
        "pattern-library/scaling/caching-strategies.md",
        "pattern-library/data-management/delta-sync.md",
        "pattern-library/data-management/merkle-trees.md",
        "pattern-library/data-management/write-ahead-log.md",
        "pattern-library/data-management/bloom-filter.md",
        "pattern-library/data-management/materialized-view.md",
        "pattern-library/data-management/read-repair.md",
        "pattern-library/data-management/saga.md",
        "pattern-library/data-management/eventual-consistency.md",
        "pattern-library/data-management/outbox.md",
        "pattern-library/coordination/clock-sync.md",
        "pattern-library/coordination/actor-model.md",
        "pattern-library/coordination/distributed-lock.md",
        "pattern-library/coordination/leader-election.md",
        "pattern-library/coordination/cas.md",
        "pattern-library/coordination/consensus.md",
        "pattern-library/coordination/leader-follower.md",
        "pattern-library/coordination/distributed-queue.md",
        "pattern-library/architecture/event-streaming.md",
        "pattern-library/architecture/cap-theorem.md",
        "pattern-library/architecture/choreography.md",
        "pattern-library/architecture/shared-nothing.md",
        "excellence/implementation-guides/index.md",
        "architects-handbook/case-studies/monitoring-observability/rate-limiter.md",
        "architects-handbook/case-studies/infrastructure/consistent-hashing.md",
        "architects-handbook/case-studies/infrastructure/unique-id-generator.md",
        "architects-handbook/case-studies/infrastructure/url-shortener.md",
        "architects-handbook/case-studies/databases/key-value-store.md",
        "architects-handbook/case-studies/social-communication/notification-system.md",
        "architects-handbook/case-studies/social-communication/news-feed.md",
        "architects-handbook/case-studies/location-services/nearby-friends.md",
        "architects-handbook/learning-paths/cost.md",
        "architects-handbook/learning-paths/architect.md",
        "architects-handbook/learning-paths/manager.md",
        "architects-handbook/learning-paths/senior-engineer.md",
        "architects-handbook/learning-paths/reliability.md",
        "architects-handbook/learning-paths/index.md",
        "architects-handbook/human-factors/sre-practices.md",
        "pattern-library/scaling/queues-streaming.md",
        "pattern-library/coordination/low-high-water-marks.md",
        "pattern-library/architecture/valet-key.md",
        "architects-handbook/case-studies/search-analytics/google-drive.md",
        "pattern-library/resilience/graceful-degradation.md",
        "pattern-library/data-management/lsm-tree.md",
        "pattern-library/resilience/fault-tolerance.md",
        "pattern-library/data-management/data-lake.md",
        "pattern-library/coordination/lease.md",
        "pattern-library/resilience/circuit-breaker.md",
        "architects-handbook/tools/consistency-calculator.md",
        "architects-handbook/tools/cost-optimizer.md",
        "pattern-library/pattern-template-v2.md",
        "reference/pattern-analysis.json",
        "reference/pattern-template.md",
        "macros.py",
        "architects-handbook/human-factors/blameless-postmortems.md",
        "architects-handbook/human-factors/chaos-engineering.md",
        "architects-handbook/human-factors/consistency-tuning.md",
        "architects-handbook/human-factors/incident-response.md",
        "architects-handbook/human-factors/observability-stacks.md",
        ".meta.yml"
    ]
    
    for file_path in files_to_fix:
        full_path = docs_dir / file_path
        if full_path.exists() and full_path.suffix in ['.md', '.json', '.yml', '.py']:
            try:
                content = full_path.read_text()
                original_content = content
                
                content = fix_law_references(content, full_path)
                
                if content != original_content:
                    full_path.write_text(content)
                    fixed_count += 1
                    print(f"Fixed: {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
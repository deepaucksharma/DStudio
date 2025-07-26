#!/usr/bin/env python3
"""
Fix broken links in DStudio documentation.
Common issues:
1. Links ending with / but file is index.md
2. Incorrect relative paths
3. Case sensitivity issues
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def load_broken_links_report():
    """Load the broken links report."""
    with open('broken_links_report.json', 'r') as f:
        return json.load(f)

def analyze_broken_links(report):
    """Analyze patterns in broken links."""
    patterns = defaultdict(int)
    
    for file_path, data in report['broken_links_by_file'].items():
        for link_info in data['links']:
            link = link_info['link']
            
            # Categorize the issue
            if link.endswith('/'):
                patterns['trailing_slash'] += 1
            elif './index.md' in link:
                patterns['relative_index'] += 1
            elif link.startswith('/'):
                patterns['absolute_path'] += 1
            else:
                patterns['other'] += 1
                
    return patterns

def get_link_fixes():
    """Return common link fixes."""
    return {
        # Part 1 - Axioms fixes
        '/part1-axioms/': '/part1-axioms/index.md',
        '/part1-axioms/law1-failure/': '/part1-axioms/law1-failure/index.md',
        '/part1-axioms/law2-asynchrony/': '/part1-axioms/law2-asynchrony/index.md',
        '/part1-axioms/law3-emergence/': '/part1-axioms/law3-emergence/index.md',
        '/part1-axioms/law4-tradeoffs/': '/part1-axioms/law4-tradeoffs/index.md',
        '/part1-axioms/law5-epistemology/': '/part1-axioms/law5-epistemology/index.md',
        '/part1-axioms/law6-human-api/': '/part1-axioms/law6-human-api/index.md',
        '/part1-axioms/law7-economics/': '/part1-axioms/law7-economics/index.md',
        
        # Part 2 - Pillars fixes
        '/part2-pillars/': '/part2-pillars/index.md',
        '/part2-pillars/work/': '/part2-pillars/work/index.md',
        '/part2-pillars/state/': '/part2-pillars/state/index.md',
        '/part2-pillars/truth/': '/part2-pillars/truth/index.md',
        '/part2-pillars/control/': '/part2-pillars/control/index.md',
        '/part2-pillars/intelligence/': '/part2-pillars/intelligence/index.md',
        
        # Patterns fixes
        '/patterns/': '/patterns/index.md',
        '/patterns/circuit-breaker/': '/patterns/circuit-breaker.md',
        '/patterns/bulkhead/': '/patterns/bulkhead.md',
        '/patterns/timeout/': '/patterns/timeout.md',
        '/patterns/api-gateway/': '/patterns/api-gateway.md',
        '/patterns/rate-limiting/': '/patterns/rate-limiting.md',
        '/patterns/cdn/': '/patterns/cdn.md',
        '/patterns/encryption-rest/': '/patterns/encryption-at-rest.md',
        '/patterns/leader-election/': '/patterns/leader-election.md',
        '/patterns/service-discovery/': '/patterns/service-discovery.md',
        '/patterns/gossip-protocol/': '/patterns/gossip-protocol.md',
        '/patterns/failure-detector/': '/patterns/failure-detector.md',
        '/patterns/membership/': '/patterns/membership.md',
        '/patterns/consistent-hashing/': '/patterns/consistent-hashing.md',
        '/patterns/vector-clocks/': '/patterns/vector-clocks.md',
        '/patterns/merkle-trees/': '/patterns/merkle-trees.md',
        '/patterns/quorum-consensus/': '/patterns/quorum.md',
        '/patterns/consensus/': '/patterns/consensus.md',
        '/patterns/write-ahead-log/': '/patterns/write-ahead-log.md',
        '/patterns/snapshot/': '/patterns/snapshot.md',
        '/patterns/log-compaction/': '/patterns/log-compaction.md',
        '/patterns/leader-follower/': '/patterns/leader-follower.md',
        
        # Case studies fixes
        '/case-studies/': '/case-studies/index.md',
        '/case-studies/cassandra/': '/case-studies/cassandra.md',
        '/case-studies/redis/': '/case-studies/redis-cluster.md',
        '/case-studies/google-spanner/': '/case-studies/google-spanner.md',
        '/case-studies/netflix-scale/': '/case-studies/netflix-scale.md',
        '/case-studies/discord-messages/': '/case-studies/discord-messages.md',
        '/case-studies/scylladb/': '/case-studies/scylladb.md',
        '/case-studies/similar/': '/case-studies/index.md',
        '/case-studies/etcd/': '/case-studies/etcd.md',
        '/case-studies/blockchain/': '/case-studies/blockchain-consensus.md',
        '/case-studies/kafka/': '/case-studies/apache-kafka.md',
        
        # Quantitative fixes
        '/quantitative/': '/quantitative/index.md',
        '/quantitative/cap-theorem/': '/quantitative/cap-theorem.md',
        '/quantitative/consistency-models/': '/quantitative/consistency-models.md',
        '/quantitative/performance-modeling/': '/quantitative/performance-modeling.md',
        '/quantitative/failure-models/': '/quantitative/failure-models.md',
        
        # Human factors fixes
        '/human-factors/': '/human-factors/index.md',
        '/human-factors/sre-practices/': '/human-factors/sre-practices.md',
        '/human-factors/chaos-engineering/': '/human-factors/chaos-engineering.md',
        
        # Reference fixes
        '/references/papers/dynamo/': '/reference/papers.md#dynamo',
        '/references/papers/spanner/': '/reference/papers.md#spanner',
        '/references/papers/tao/': '/reference/papers.md#tao',
        
        # Other common fixes
        './index.md': 'index.md',
        '../': '../index.md',
        '/learn/': '/introduction/getting-started.md',
    }

def fix_links_in_file(file_path, fixes):
    """Fix links in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
        
    original_content = content
    changes_made = False
    
    # Apply fixes
    for broken_link, fixed_link in fixes.items():
        if broken_link in content:
            content = content.replace(f"]({broken_link})", f"]({fixed_link})")
            content = content.replace(f'href="{broken_link}"', f'href="{fixed_link}"')
            content = content.replace(f"href='{broken_link}'", f"href='{fixed_link}'")
            changes_made = True
            
    # Special case: fix relative index.md links
    content = re.sub(r'\]\(\.\/index\.md\)', '](index.md)', content)
    if content != original_content:
        changes_made = True
        
    if changes_made:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
        
    return False

def main():
    """Main function to fix broken links."""
    print("Loading broken links report...")
    report = load_broken_links_report()
    
    print(f"\nFound {report['summary']['total_broken_links']} broken links in {report['summary']['files_with_broken_links']} files")
    
    # Analyze patterns
    patterns = analyze_broken_links(report)
    print("\nBroken link patterns:")
    for pattern, count in patterns.items():
        print(f"  {pattern}: {count}")
        
    # Get fixes
    fixes = get_link_fixes()
    print(f"\nPrepared {len(fixes)} link fixes")
    
    # Apply fixes
    fixed_files = 0
    for file_path in report['broken_links_by_file'].keys():
        full_path = Path('docs') / file_path
        if full_path.exists():
            if fix_links_in_file(full_path, fixes):
                fixed_files += 1
                print(f"Fixed links in: {file_path}")
                
    print(f"\nFixed links in {fixed_files} files")
    
    # Suggest running verification again
    print("\nRun 'python3 verify_links.py' again to check remaining broken links")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Fix broken internal links in DStudio documentation
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Base directory
DOCS_DIR = Path("/Users/deepaksharma/syc/DStudio/docs")

# Common link fixes
LINK_FIXES = {
    # Fix axiom paths
    "../part1-axioms/latency/": "../part1-axioms/axiom1-latency/",
    "../part1-axioms/capacity/": "../part1-axioms/axiom2-capacity/",
    "../part1-axioms/failure/": "../part1-axioms/axiom3-failure/",
    "../part1-axioms/concurrency/": "../part1-axioms/axiom4-concurrency/",
    "../part1-axioms/coordination/": "../part1-axioms/axiom5-coordination/",
    "../part1-axioms/observability/": "../part1-axioms/axiom6-observability/",
    "../part1-axioms/human-interface/": "../part1-axioms/axiom7-human/",
    "../part1-axioms/economics/": "../part1-axioms/axiom8-economics/",
    "../../part1-axioms/axiom7-human-interface/index.md": "../../part1-axioms/axiom7-human/index.md",
    
    # Fix axiom directory links without trailing slash
    "/part1-axioms/axiom1-latency/": "/part1-axioms/axiom1-latency/index.md",
    "/part1-axioms/axiom2-capacity/": "/part1-axioms/axiom2-capacity/index.md",
    "/part1-axioms/axiom3-failure/": "/part1-axioms/axiom3-failure/index.md",
    "/part1-axioms/axiom4-concurrency/": "/part1-axioms/axiom4-concurrency/index.md",
    "/part1-axioms/axiom5-coordination/": "/part1-axioms/axiom5-coordination/index.md",
    "/part1-axioms/axiom6-observability/": "/part1-axioms/axiom6-observability/index.md",
    "/part1-axioms/axiom7-human/": "/part1-axioms/axiom7-human/index.md",
    "/part1-axioms/axiom8-economics/": "/part1-axioms/axiom8-economics/index.md",
    
    # Fix pattern links without .md extension  
    "/patterns/circuit-breaker": "/patterns/circuit-breaker.md",
    "/patterns/event-sourcing": "/patterns/event-sourcing.md",
    "/patterns/saga": "/patterns/saga.md",
    "/patterns/cqrs": "/patterns/cqrs.md",
    "/patterns/outbox": "/patterns/outbox.md",
    "/patterns/rate-limiting": "/patterns/rate-limiting.md",
    "/patterns/event-driven": "/patterns/event-driven.md",
    "/patterns/load-balancing": "/patterns/load-balancing.md",
    "/patterns/health-check": "/patterns/health-check.md",
    "/patterns/timeout": "/patterns/timeout.md",
    
    # Fix common misnamed files
    "postmortem-culture.md": "blameless-postmortems.md",
    "cap-pacelc.md": "cap-theorem.md",
    "queueing-theory.md": "queueing-models.md",
    "scaling-laws.md": "amdahl-gustafson.md",
    "../quantitative/cap-pacelc.md": "../patterns/cap-theorem.md",
    "../human-factors/postmortem-culture.md": "../human-factors/blameless-postmortems.md",
    "../human-factors/capacity-planning.md": "../quantitative/capacity-planning.md",
    
    # Fix paths that should point to case studies
    "../patterns/consistent-hashing.md": "../case-studies/consistent-hashing.md",
    
    # Fix case study index paths
    "../../case-studies/apache-spark/index.md": "../../case-studies/apache-spark.md",
    "../../case-studies/blockchain/index.md": "../../case-studies/blockchain.md",
    "../../case-studies/cassandra/index.md": "../../case-studies/cassandra.md",
    "../../case-studies/dynamodb/index.md": "../../case-studies/amazon-dynamo.md",
    "../../case-studies/etcd/index.md": "../../case-studies/etcd.md",
    "../../case-studies/google-mapreduce/index.md": "../../case-studies/mapreduce.md",
    "../../case-studies/kafka/index.md": "../../case-studies/kafka.md",
    "../../case-studies/mongodb/index.md": "../../case-studies/mongodb.md",
    "../../case-studies/netflix-chaos/index.md": "../../case-studies/netflix-chaos.md",
    
    # Fix learning path references
    "../introduction/learning-paths.md": "../LEARNING_PATHS.md",
    "../../introduction/learning-paths.md": "../../LEARNING_PATHS.md",
    "../learning-paths.md": "../LEARNING_PATHS.md",
    
    # Fix more quantitative references
    "../../quantitative/scaling-laws.md": "../../quantitative/amdahl-gustafson.md",
    "../../quantitative/queueing/index.md": "../../quantitative/queueing-models.md",
    "../quantitative/queueing-models/": "../quantitative/queueing-models.md",
    "../quantitative/universal-scalability/": "../quantitative/universal-scalability.md",
    "../../tools/capacity-planning.md": "../../quantitative/capacity-planning.md",
    
    # Fix case study references
    "../../case-studies/redis-cluster/index.md": "../../case-studies/redis.md",
    "../../case-studies/spanner/index.md": "../../case-studies/google-spanner.md",
    "../../case-studies/uber-ringpop.md": "../../case-studies/uber-location.md",
    
    # Fix human factors references
    "../../human-factors/capacity-planning.md": "../../quantitative/capacity-planning.md",
    "../../human-factors/game-days.md": "../../human-factors/chaos-engineering.md",
    "../../human-factors/on-call.md": "../../human-factors/oncall-culture.md",
    "../../human-factors/post-mortems.md": "../../human-factors/blameless-postmortems.md",
    "../../human-factors/runbooks.md": "../../human-factors/runbooks-playbooks.md",
    
    # Fix pattern references
    "../../patterns/chaos-engineering.md": "../../human-factors/chaos-engineering.md",
    "../patterns/coordination.md": "../patterns/consensus.md",
    "../patterns/partition-tolerance.md": "../patterns/graceful-degradation.md",
    "../../patterns/circuit-breaker/index.md": "../../patterns/circuit-breaker.md",
    "../../patterns/consensus/index.md": "../../patterns/consensus.md",
    "../../patterns/cqrs/index.md": "../../patterns/cqrs.md",
    "../../patterns/event-sourcing/index.md": "../../patterns/event-sourcing.md",
    "../../patterns/event-streaming/index.md": "../../patterns/queues-streaming.md",
    "../../patterns/health-checks.md": "../../patterns/health-check.md",
    "../../patterns/mapreduce/index.md": "../../case-studies/mapreduce.md",
    "../../patterns/replication/index.md": "../../patterns/geo-replication.md",
    "../../patterns/saga/index.md": "../../patterns/saga.md",
    "../../patterns/service-mesh/index.md": "../../patterns/service-mesh.md",
    "../../patterns/sharding/index.md": "../../patterns/sharding.md",
    "../../patterns/streaming/index.md": "../../patterns/queues-streaming.md",
    
    # Fix directory references without trailing slash
    "../patterns/cqrs/": "../patterns/cqrs.md",
    "../patterns/event-driven/": "../patterns/event-driven.md",
    "../patterns/event-sourcing/": "../patterns/event-sourcing.md",
    "../patterns/saga/": "../patterns/saga.md",
    "../quantitative/littles-law/": "../quantitative/littles-law.md",
    "/quantitative/littles-law/": "/quantitative/littles-law.md",
    "/quantitative/queueing-models/": "/quantitative/queueing-models.md",
    "../patterns/bulkhead": "../patterns/bulkhead.md",
    "../patterns/edge-computing": "../patterns/edge-computing.md",
    "../patterns/geo-replication": "../patterns/geo-replication.md",
    "../patterns/queues-streaming": "../patterns/queues-streaming.md",
    "../patterns/service-mesh": "../patterns/service-mesh.md",
    "../patterns/tunable-consistency": "../patterns/tunable-consistency.md",
}

# Files that need to be created as stubs
MISSING_FILES = {
    "patterns": [
        "leader-follower.md",
        "actor-model.md",
        "adaptive-scheduling.md",
        "analytics-scale.md",
        "anti-entropy.md",
        "battery-optimization.md",
        "caching.md",
        "gossip-protocol.md",
        "eventual-consistency.md",
        "cap-theorem.md",
        "distributed-transactions.md",
        "write-through-cache.md",
        "write-behind-cache.md",
        "cache-aside.md",
        "read-through-cache.md",
        "choreography.md",
        "distributed-queue.md",
        "sidecar.md",
        "ambassador.md",
        "anti-corruption-layer.md",
        "backends-for-frontends.md",
        "data-lake.md",
        "data-mesh.md",
        "lambda-architecture.md",
        "kappa-architecture.md",
        "materialized-view.md",
        "polyglot-persistence.md",
        "request-routing.md",
        "scatter-gather.md",
        "service-registry.md",
        "shared-nothing.md",
        "split-brain.md",
        "strangler-fig.md",
        "valet-key.md"
    ],
    "quantitative": [
        "information-theory.md",
        "cap-theorem.md",
        "power-laws.md",
        "consistency-models.md",
        "reliability-engineering.md",
        "network-theory.md",
        "performance-modeling.md",
        "reliability-theory.md",
        "stochastic-processes.md",
        "availability.md",
        "blast-radius.md",
        "failure-models.md",
        "mtbf-mttr.md",
        "network-model.md",
        "performance-testing.md",
        "graph-models.md",
        "time-complexity.md",
        "space-complexity.md",
        "bayesian-reasoning.md",
        "queuing-networks.md",
        "markov-chains.md"
    ],
    "case-studies": [
        "twitter-timeline.md",
        "netflix-streaming.md",
        "google-spanner.md",
        "amazon-aurora.md",
        "apache-spark.md",
        "blockchain.md",
        "cassandra.md",
        "etcd.md",
        "kafka.md",
        "mapreduce.md",
        "mongodb.md",
        "netflix-chaos.md",
        "redis.md",
        "kubernetes.md",
        "elasticsearch.md",
        "memcached.md",
        "prometheus.md",
        "vault.md",
        "zookeeper.md"
    ]
}

def find_broken_links(file_path):
    """Find all internal links in a markdown file"""
    broken_links = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find all markdown links
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(link_pattern, content)
    
    for link_text, link_url in matches:
        # Skip external links
        if link_url.startswith('http'):
            continue
            
        # Skip anchors
        if link_url.startswith('#'):
            continue
            
        # Check if it's a relative path
        if link_url.endswith('.md'):
            # Resolve the path
            if link_url.startswith('../'):
                parent_count = link_url.count('../')
                base_path = file_path.parent
                for _ in range(parent_count):
                    base_path = base_path.parent
                relative_path = link_url.replace('../', '')
                full_path = base_path / relative_path
            else:
                full_path = file_path.parent / link_url
                
            # Check if file exists
            if not full_path.exists():
                broken_links.append((link_text, link_url, full_path))
                
    return broken_links

def fix_links_in_file(file_path):
    """Fix known broken links in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Apply known fixes
    for old_link, new_link in LINK_FIXES.items():
        content = content.replace(f"]({old_link})", f"]({new_link})")
    
    # Fix absolute paths that should be relative
    # When linking to axiom index.md from patterns/quantitative folders
    if 'patterns/' in str(file_path) or 'quantitative/' in str(file_path):
        # Replace absolute paths with relative ones
        content = content.replace('](/part1-axioms/', '](../part1-axioms/')
        content = content.replace('](/part2-pillars/', '](../part2-pillars/')
        content = content.replace('](/patterns/', '](../patterns/')
        content = content.replace('](/case-studies/', '](../case-studies/')
        
    # Write back if changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def create_stub_file(category, filename):
    """Create a stub pattern/case study file"""
    base_path = DOCS_DIR / category
    file_path = base_path / filename
    
    if file_path.exists():
        return False
        
    title = filename.replace('.md', '').replace('-', ' ').title()
    
    stub_content = f"""---
title: {title}
description: This topic is under development
type: {category.rstrip('s')}
difficulty: intermediate
reading_time: 30 min
prerequisites: []
pattern_type: "various"
status: stub
last_updated: 2025-01-23
---

<!-- Navigation -->
[Home](../index.md) → [{category.title()}](index.md) → **{title}**

# {title}

> *This content is currently under development.*

## Overview

This page will cover {title.lower()} in distributed systems.

## Key Concepts

Coming soon...

## Related Topics

- See other [{category}](index.md)

---

*This is a stub page. Full content coming soon.*
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(stub_content)
    
    return True

def main():
    """Main function to fix broken links"""
    print("🔧 Fixing broken links in DStudio documentation...\n")
    
    # Step 1: Create missing stub files
    print("📝 Creating missing stub files...")
    created_count = 0
    for category, files in MISSING_FILES.items():
        for filename in files:
            if create_stub_file(category, filename):
                created_count += 1
                print(f"  ✅ Created {category}/{filename}")
    
    print(f"\n  Created {created_count} stub files\n")
    
    # Step 2: Fix known broken links
    print("🔗 Fixing broken links...")
    fixed_files = 0
    total_files = 0
    
    for md_file in DOCS_DIR.rglob("*.md"):
        total_files += 1
        if fix_links_in_file(md_file):
            fixed_files += 1
            print(f"  ✅ Fixed links in {md_file.relative_to(DOCS_DIR)}")
    
    print(f"\n  Fixed links in {fixed_files} files (out of {total_files} total)\n")
    
    # Step 3: Find remaining broken links
    print("🔍 Checking for remaining broken links...")
    all_broken_links = defaultdict(list)
    
    for md_file in DOCS_DIR.rglob("*.md"):
        broken_links = find_broken_links(md_file)
        if broken_links:
            for link_text, link_url, full_path in broken_links:
                all_broken_links[link_url].append(str(md_file.relative_to(DOCS_DIR)))
    
    if all_broken_links:
        print(f"\n⚠️  Found {len(all_broken_links)} unique broken links still remaining:\n")
        for link, files in sorted(all_broken_links.items())[:10]:  # Show top 10
            print(f"  - {link} (in {len(files)} files)")
    else:
        print("\n✅ No broken links found!")
    
    print("\n✨ Link fixing complete!")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Comprehensive link fixes based on deep analysis of verification reports.
This script addresses critical issues found in manual verification.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import json

class ComprehensiveLinkFixer:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / 'docs'
        self.fixes_applied = 0
        self.files_modified = set()
        self.files_created = 0
        
    def fix_mdindex_corruption(self):
        """
        Fix the critical mdindex.md corruption pattern.
        This is a malformed pattern where links have been corrupted to contain 'mdindex.md'
        instead of proper file references.
        """
        print("🔧 Fixing critical mdindex.md corruption patterns...")
        
        # Pattern variations we've seen:
        # 1. file.mdindex.md -> file.md
        # 2. path/index.mdindex.md -> path/index.md
        # 3. index.mdindex.mdpath -> path/index.md
        
        patterns_to_fix = [
            # Fix .mdindex.md to .md
            (r'\.mdindex\.md', '.md'),
            # Fix index.mdindex.md to index.md
            (r'index\.mdindex\.md', 'index.md'),
            # Fix complex corruptions like index.mdindex.mdmonolith-decomposition
            (r'index\.mdindex\.md([a-z-]+)', r'\1/index.md'),
            # Fix paths that have mdindex in them
            (r'([a-z-]+)\.mdindex\.md([a-z-/]+)', r'\1/\2'),
            # Clean up any remaining mdindex patterns
            (r'mdindex\.md', 'index.md'),
        ]
        
        for md_file in self.docs_dir.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                for pattern, replacement in patterns_to_fix:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_modified.add(md_file)
                    # Count how many fixes were made
                    fixes_in_file = len(re.findall(r'mdindex', original_content))
                    self.fixes_applied += fixes_in_file
                    print(f"  ✅ Fixed {fixes_in_file} mdindex corruptions in {md_file.relative_to(self.base_dir)}")
                    
            except Exception as e:
                print(f"  ❌ Error processing {md_file}: {e}")
    
    def create_missing_navigation_files(self):
        """
        Create critical missing navigation files for core-principles section.
        These are essential for breadcrumb navigation.
        """
        print("\n📁 Creating missing navigation files...")
        
        navigation_files = {
            'docs/core-principles.md': {
                'title': 'Core Principles',
                'description': 'Fundamental laws and pillars of distributed systems',
                'content': '''# Core Principles

The foundation of distributed systems mastery lies in understanding fundamental laws and architectural pillars.

## The 7 Fundamental Laws

Every distributed system, regardless of scale or complexity, is governed by these immutable laws:

1. **[The Inevitability of Failure](core-principles/laws/correlated-failure.md)** - Systems will fail
2. **[The Economics of Scale](core-principles/laws/economic-reality.md)** - Cost shapes architecture
3. **[The Constraints of Time](core-principles/laws/temporal-constraints.md)** - Time is never synchronized
4. **[The Reality of Networks](core-principles/laws/asynchronous-reality.md)** - Networks are unreliable
5. **[The Human Factor](core-principles/laws/cognitive-load.md)** - Humans have limits
6. **[The Nature of Knowledge](core-principles/laws/distributed-knowledge.md)** - Knowledge is always partial
7. **[The Emergence of Chaos](core-principles/laws/emergent-chaos.md)** - Complexity breeds unpredictability

[Explore the Laws →](core-principles/laws/)

## The 5 Architectural Pillars

Built upon these laws, five pillars guide practical system design:

1. **[Work Distribution](core-principles/pillars/work-distribution.md)** - How to divide computation
2. **[Control Distribution](core-principles/pillars/control-distribution.md)** - How to coordinate decisions
3. **[State Distribution](core-principles/pillars/state-distribution.md)** - How to manage data
4. **[Truth Distribution](core-principles/pillars/truth-distribution.md)** - How to establish consensus
5. **[Information Flow](core-principles/pillars/information-flow.md)** - How to move data

[Explore the Pillars →](core-principles/pillars/)

## Pattern Application

These principles manifest in concrete patterns:

- **[Pattern Library](pattern-library/)** - 100+ battle-tested patterns
- **[Case Studies](architects-handbook/case-studies/)** - Real-world applications
- **[Implementation Guides](excellence/implementation-guides/)** - Practical blueprints

## Start Your Journey

Begin with [Law 1: The Inevitability of Failure](core-principles/laws/correlated-failure.md) - it's the foundation everything else builds upon.
'''
            },
            'docs/core-principles/laws.md': {
                'title': 'The 7 Fundamental Laws',
                'description': 'Immutable laws that govern all distributed systems',
                'content': '''# The 7 Fundamental Laws

These laws are not guidelines or best practices - they are immutable constraints that govern every distributed system.

## The Laws

1. **[The Inevitability of Failure](correlated-failure.md)**
   - Components will fail
   - Failures cascade and correlate
   - Perfect reliability is impossible

2. **[The Economics of Scale](economic-reality.md)**
   - Resources are finite
   - Cost drives architectural decisions
   - Trade-offs are inevitable

3. **[The Constraints of Time](temporal-constraints.md)**
   - Perfect synchronization is impossible
   - Time ordering is relative
   - Causality requires explicit tracking

4. **[The Reality of Networks](asynchronous-reality.md)**
   - Networks partition
   - Latency is non-zero
   - Bandwidth is limited

5. **[The Human Factor](cognitive-load.md)**
   - Humans have cognitive limits
   - Complexity must be managed
   - Operations require human understanding

6. **[The Nature of Knowledge](distributed-knowledge.md)**
   - Global state is unknowable
   - Information propagates slowly
   - Decisions use partial information

7. **[The Emergence of Chaos](emergent-chaos.md)**
   - Complex systems exhibit emergent behavior
   - Small changes have large effects
   - Predictability decreases with scale

## Understanding the Laws

Each law represents a fundamental constraint that cannot be overcome, only managed. Understanding these laws helps you:

- **Design realistic systems** that acknowledge fundamental limitations
- **Make informed trade-offs** between competing concerns
- **Predict failure modes** before they occur
- **Build resilient architectures** that embrace constraints

## Pattern Relationships

These laws directly influence pattern selection:

- **Failure patterns** emerge from Law 1
- **Optimization patterns** emerge from Law 2
- **Coordination patterns** emerge from Laws 3, 4, and 6
- **Operational patterns** emerge from Law 5
- **Adaptive patterns** emerge from Law 7

Continue to [The 5 Pillars](../pillars/) to see how these laws translate into architectural principles.
'''
            },
            'docs/core-principles/pillars.md': {
                'title': 'The 5 Architectural Pillars',
                'description': 'Core architectural principles for distributed systems',
                'content': '''# The 5 Architectural Pillars

Building on the fundamental laws, these five pillars provide the architectural foundation for all distributed systems.

## The Pillars

### 1. [Work Distribution](work-distribution.md)
How computation is divided across nodes
- Load balancing strategies
- Task partitioning
- Parallel processing patterns

### 2. [Control Distribution](control-distribution.md)
How decisions are coordinated
- Consensus mechanisms
- Leader election
- Distributed coordination

### 3. [State Distribution](state-distribution.md)
How data is managed across nodes
- Replication strategies
- Consistency models
- Partitioning schemes

### 4. [Truth Distribution](truth-distribution.md)
How agreement is reached
- Consensus protocols
- Conflict resolution
- Version reconciliation

### 5. [Information Flow](information-flow.md)
How data moves through the system
- Communication patterns
- Event propagation
- Data pipelines

## Pillar Interactions

The pillars are interconnected:

```mermaid
graph TD
    W[Work Distribution] --> C[Control Distribution]
    C --> S[State Distribution]
    S --> T[Truth Distribution]
    T --> I[Information Flow]
    I --> W
    
    W -.-> S
    C -.-> T
    S -.-> I
```

## Design Principles

Each pillar embodies key principles:

### Work Distribution Principles
- Minimize coordination overhead
- Balance load dynamically
- Isolate failure domains

### Control Distribution Principles
- Avoid single points of failure
- Enable autonomous operation
- Coordinate only when necessary

### State Distribution Principles
- Optimize for access patterns
- Choose appropriate consistency
- Plan for partition tolerance

### Truth Distribution Principles
- Define authoritative sources
- Handle concurrent updates
- Resolve conflicts deterministically

### Information Flow Principles
- Minimize data movement
- Optimize for latency or throughput
- Handle backpressure gracefully

## Pattern Application

Each pillar maps to specific pattern categories:

- **Work Distribution** → [Scaling Patterns](../pattern-library/scaling/)
- **Control Distribution** → [Coordination Patterns](../pattern-library/coordination/)
- **State Distribution** → [Data Management Patterns](../pattern-library/data-management/)
- **Truth Distribution** → [Consensus Patterns](../pattern-library/coordination/consensus.md)
- **Information Flow** → [Communication Patterns](../pattern-library/communication/)

## Next Steps

1. Review each pillar in detail
2. Understand the relationships between pillars
3. Apply patterns that align with your architectural needs
4. Use the [Pattern Library](../pattern-library/) to implement solutions

Start with [Work Distribution](work-distribution.md) to understand how computation scales.
'''
            }
        }
        
        for file_path, metadata in navigation_files.items():
            full_path = self.base_dir / file_path
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                content = f"""---
title: {metadata['title']}
description: {metadata['description']}
---

{metadata['content']}
"""
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.files_created += 1
                print(f"  ✅ Created: {file_path}")
    
    def fix_malformed_https_urls(self):
        """
        Fix malformed HTTPS URLs missing the second slash.
        Pattern: https:/example.com -> https://example.com
        """
        print("\n🌐 Fixing malformed HTTPS URLs...")
        
        # This pattern matches https:/ followed by non-slash character
        pattern = r'https:/([^/])'
        replacement = r'https://\1'
        
        for md_file in self.docs_dir.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all malformed URLs for reporting
                malformed_urls = re.findall(pattern, content)
                
                if malformed_urls:
                    # Fix them
                    new_content = re.sub(pattern, replacement, content)
                    
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.files_modified.add(md_file)
                    self.fixes_applied += len(malformed_urls)
                    print(f"  ✅ Fixed {len(malformed_urls)} malformed URLs in {md_file.relative_to(self.base_dir)}")
                    
            except Exception as e:
                print(f"  ❌ Error processing {md_file}: {e}")
    
    def fix_excellence_index_paths(self):
        """
        Fix the wrong paths in excellence section index files.
        These are pointing to non-existent architects-handbook paths.
        """
        print("\n📂 Fixing excellence section index paths...")
        
        fixes = {
            'docs/excellence/migrations/index.md': [
                # Wrong: ../architects-handbook/implementation-playbooks/migrations/
                # Right: ./
                (r'\.\./architects-handbook/implementation-playbooks/migrations/', './'),
                (r'architects-handbook/implementation-playbooks/migrations/', './'),
            ],
            'docs/excellence/implementation-guides/index.md': [
                # Wrong: ../architects-handbook/implementation-playbooks/implementation-guides/
                # Right: ./
                (r'\.\./architects-handbook/implementation-playbooks/implementation-guides/', './'),
                (r'architects-handbook/implementation-playbooks/implementation-guides/', './'),
            ]
        }
        
        for file_path, patterns in fixes.items():
            full_path = self.base_dir / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    for pattern, replacement in patterns:
                        content = re.sub(pattern, replacement, content)
                    
                    if content != original_content:
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        self.files_modified.add(full_path)
                        print(f"  ✅ Fixed paths in {file_path}")
                        
                except Exception as e:
                    print(f"  ❌ Error fixing {file_path}: {e}")
    
    def fix_core_principles_path_issues(self):
        """
        Fix specific path issues in core-principles section.
        """
        print("\n🔗 Fixing core-principles path issues...")
        
        # Fix the wrong self-reference in state-distribution.md
        file_path = self.docs_dir / 'core-principles/pillars/state-distribution.md'
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Fix the incorrect path
                content = re.sub(
                    r'\[Pillar 3: Truth\]\(\.\./core-principles/pillars/truth-distribution\.md\)',
                    '[Pillar 3: Truth](truth-distribution.md)',
                    content
                )
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.files_modified.add(file_path)
                print(f"  ✅ Fixed self-reference in state-distribution.md")
                
            except Exception as e:
                print(f"  ❌ Error fixing state-distribution.md: {e}")
        
        # Fix the double prefix issue in low-high-water-marks.md
        file_path = self.docs_dir / 'pattern-library/coordination/low-high-water-marks.md'
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Fix the double prefix patterns
                content = re.sub(
                    r'core-principles\.\./core-principles/',
                    '../../core-principles/',
                    content
                )
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.files_modified.add(file_path)
                print(f"  ✅ Fixed double prefix in low-high-water-marks.md")
                
            except Exception as e:
                print(f"  ❌ Error fixing low-high-water-marks.md: {e}")
    
    def create_missing_deployment_patterns(self):
        """
        Create missing deployment pattern files that are referenced but don't exist.
        """
        print("\n📦 Creating missing deployment patterns...")
        
        deployment_patterns = {
            'docs/pattern-library/deployment/canary.md': {
                'title': 'Canary Deployment',
                'description': 'Gradual rollout with early failure detection',
                'content': '''# Canary Deployment

## Overview

Canary deployment is a pattern for rolling out releases to a subset of users or servers, allowing you to test in production with reduced risk.

## How It Works

1. **Deploy to Small Subset**: Release new version to 1-5% of infrastructure
2. **Monitor Metrics**: Watch error rates, latency, and business metrics
3. **Gradual Rollout**: If healthy, progressively increase traffic
4. **Quick Rollback**: If issues detected, instantly revert

## Implementation

### Traffic Routing
```yaml
# Example: Kubernetes canary with Istio
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
spec:
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: service
        subset: v2
      weight: 10  # 10% to canary
    - destination:
        host: service
        subset: v1
      weight: 90  # 90% to stable
```

## Success Metrics

- Error rate remains below threshold
- P99 latency within bounds
- Business metrics stable or improving
- No increase in support tickets

## When to Use

- **High-risk changes**: Database migrations, algorithm changes
- **Performance-sensitive**: When latency matters
- **Large user base**: Minimize blast radius
- **Continuous deployment**: Part of CD pipeline

## Related Patterns

- [Blue-Green Deployment](blue-green.md)
- [Circuit Breaker](../resilience/circuit-breaker.md)
- [Feature Flags](feature-flags.md)
'''
            },
            'docs/pattern-library/deployment/blue-green.md': {
                'title': 'Blue-Green Deployment',
                'description': 'Zero-downtime deployment with instant rollback',
                'content': '''# Blue-Green Deployment

## Overview

Blue-green deployment eliminates downtime and reduces risk by running two identical production environments called Blue and Green.

## How It Works

1. **Blue = Current Production**: Live environment serving all traffic
2. **Green = New Version**: Deploy and test new version
3. **Switch Traffic**: Route all traffic from blue to green
4. **Keep Blue as Backup**: Instant rollback if issues arise

## Implementation

### Load Balancer Switch
```nginx
# Nginx configuration
upstream backend {
    # Switch between blue and green
    server green.internal.com;  # Currently active
    # server blue.internal.com backup;
}
```

### DNS Switch
```python
# Route53 weighted routing
def switch_to_green():
    route53.change_resource_record_sets(
        ChangeBatch={
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': 'api.example.com',
                    'Type': 'A',
                    'AliasTarget': {
                        'HostedZoneId': GREEN_ZONE_ID,
                        'DNSName': GREEN_DNS
                    }
                }
            }]
        }
    )
```

## Advantages

- Zero downtime deployments
- Instant rollback capability
- Full production testing before switch
- Simple and reliable

## Disadvantages

- Requires double infrastructure
- Database migrations complex
- Long-running transactions need handling
- Session state management

## When to Use

- **Critical systems**: Where downtime is unacceptable
- **Major releases**: Significant changes needing validation
- **Quick rollback required**: Financial, healthcare systems
- **Simple architecture**: Stateless applications

## Related Patterns

- [Canary Deployment](canary.md)
- [Feature Flags](feature-flags.md)
- [Database Migration Patterns](../data-management/migration-patterns.md)
'''
            },
            'docs/pattern-library/scaling/shuffle-sharding.md': {
                'title': 'Shuffle Sharding',
                'description': 'Isolation technique to prevent cascade failures',
                'content': '''# Shuffle Sharding

## Overview

Shuffle sharding creates isolated failure domains by randomly assigning resources to customers, preventing one customer's issue from affecting all others.

## How It Works

Instead of traditional sharding where customers map to specific shards, shuffle sharding assigns each customer a random subset of shards.

### Traditional Sharding
```
Customer A → Shard 1
Customer B → Shard 2
Customer C → Shard 3
```

### Shuffle Sharding
```
Customer A → Shards [1, 3, 5, 7]
Customer B → Shards [2, 4, 6, 8]
Customer C → Shards [1, 2, 7, 8]
```

## Implementation

```python
import hashlib
import random

class ShuffleShardRouter:
    def __init__(self, total_shards: int, shards_per_customer: int):
        self.total_shards = total_shards
        self.shards_per_customer = shards_per_customer
    
    def get_shards(self, customer_id: str) -> List[int]:
        """Get deterministic random shards for customer"""
        # Seed with customer ID for consistency
        random.seed(hashlib.md5(customer_id.encode()).hexdigest())
        
        # Select random subset of shards
        shards = random.sample(
            range(self.total_shards), 
            self.shards_per_customer
        )
        
        return sorted(shards)
    
    def route_request(self, customer_id: str) -> int:
        """Route to one of customer's shards"""
        shards = self.get_shards(customer_id)
        # Could use round-robin, random, or load-based selection
        return random.choice(shards)
```

## Isolation Guarantees

With shuffle sharding, the probability of two customers sharing all the same shards is extremely low:

- 8 total shards, 2 per customer: 28 possible combinations
- 100 total shards, 5 per customer: ~75 million combinations

## Use Cases

- **Multi-tenant systems**: Isolate tenant failures
- **API rate limiting**: Prevent one customer affecting others
- **Database connection pools**: Isolate noisy neighbors
- **Cache partitions**: Prevent cache pollution

## Trade-offs

### Advantages
- Strong isolation between customers
- Prevents cascade failures
- Maintains redundancy per customer
- Scales with shard count

### Disadvantages
- More complex than simple sharding
- Requires more total resources
- Load balancing more difficult
- Debugging can be challenging

## Related Patterns

- [Bulkhead Pattern](../resilience/bulkhead.md)
- [Cell-Based Architecture](../architecture/cell-based.md)
- [Consistent Hashing](../coordination/consistent-hashing.md)
'''
            }
        }
        
        for file_path, metadata in deployment_patterns.items():
            full_path = self.base_dir / file_path
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                content = f"""---
title: {metadata['title']}
description: {metadata['description']}
---

{metadata['content']}
"""
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.files_created += 1
                print(f"  ✅ Created: {file_path}")
    
    def run(self):
        """
        Execute all fixes in priority order.
        """
        print("=" * 60)
        print("🚀 COMPREHENSIVE LINK FIX OPERATION")
        print("=" * 60)
        
        # Priority 1: Fix critical corruptions
        self.fix_mdindex_corruption()
        
        # Priority 2: Create missing navigation files
        self.create_missing_navigation_files()
        
        # Priority 3: Fix malformed HTTPS URLs
        self.fix_malformed_https_urls()
        
        # Priority 4: Fix excellence section paths
        self.fix_excellence_index_paths()
        
        # Priority 5: Fix core principles path issues
        self.fix_core_principles_path_issues()
        
        # Priority 6: Create missing deployment patterns
        self.create_missing_deployment_patterns()
        
        print("\n" + "=" * 60)
        print("📊 FINAL SUMMARY")
        print("=" * 60)
        print(f"✅ Total fixes applied: {self.fixes_applied}")
        print(f"📝 Files modified: {len(self.files_modified)}")
        print(f"📁 Files created: {self.files_created}")
        print("\n✨ Link health significantly improved!")
        
        # Save a detailed report
        report = {
            'fixes_applied': self.fixes_applied,
            'files_modified': len(self.files_modified),
            'files_created': self.files_created,
            'modified_files': [str(f.relative_to(self.base_dir)) for f in self.files_modified]
        }
        
        report_path = self.base_dir / 'link_fix_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: link_fix_report.json")

if __name__ == '__main__':
    fixer = ComprehensiveLinkFixer('/home/deepak/DStudio')
    fixer.run()

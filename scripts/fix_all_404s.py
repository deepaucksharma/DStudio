#!/usr/bin/env python3
"""
Comprehensive fix for all 404 errors in the deployed site
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set

class ComprehensiveLinkFixer:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / 'docs'
        self.fixes_applied = 0
        self.files_created = 0
        self.files_modified = set()
        
    def create_missing_root_files(self):
        """Create missing root-level files"""
        root_files = {
            'docs/index.md': {
                'title': 'Distributed Systems Studio',
                'description': 'Master distributed systems through fundamental laws and proven patterns',
                'content': '''# Welcome to Distributed Systems Studio

## Start Your Journey

<div class="grid cards" markdown>

- :material-book-open:{ .lg .middle } **[Core Principles](core-principles/)**
    
    Master the 7 fundamental laws that govern all distributed systems

- :material-puzzle:{ .lg .middle } **[Pattern Library](pattern-library/)**
    
    Explore 100+ battle-tested patterns used by industry leaders

- :material-school:{ .lg .middle } **[Architect\'s Handbook](architects-handbook/)**
    
    Learn from real-world case studies and implementation guides

- :material-rocket:{ .lg .middle } **[Excellence](excellence/)**
    
    Best practices for building production-ready systems

</div>'''
            },
            'docs/monolith-to-microservices.md': {
                'title': 'Monolith to Microservices Migration',
                'redirect': 'excellence/migrations/monolith-to-microservices'
            },
            'docs/performance-testing.md': {
                'title': 'Performance Testing Guide',
                'redirect': 'architects-handbook/quantitative-analysis/performance-testing'
            },
            'docs/incident-response.md': {
                'title': 'Incident Response Guide',
                'redirect': 'architects-handbook/human-factors/incident-response'
            },
            'docs/latency-calculator.md': {
                'title': 'Latency Calculator',
                'redirect': 'architects-handbook/tools/latency-calculator'
            },
            'docs/human-factors.md': {
                'title': 'Human Factors in Distributed Systems',
                'redirect': 'architects-handbook/human-factors/'
            }
        }
        
        for file_path, metadata in root_files.items():
            self._create_file(file_path, metadata)
    
    def create_missing_pattern_files(self):
        """Create missing pattern library files"""
        patterns = [
            # Core patterns that are referenced frequently
            ('pattern-library/index.md', 'Pattern Library', 'Comprehensive collection of distributed systems patterns'),
            ('pattern-library/resilience/circuit-breaker.md', 'Circuit Breaker', 'Prevent cascading failures'),
            ('pattern-library/data-management/saga.md', 'Saga Pattern', 'Manage distributed transactions'),
            ('pattern-library/data-management/event-sourcing.md', 'Event Sourcing', 'Store state as events'),
            ('pattern-library/data-management/cqrs.md', 'CQRS', 'Command Query Responsibility Segregation'),
            ('pattern-library/coordination/consensus.md', 'Consensus Patterns', 'Achieve agreement in distributed systems'),
            
            # Scaling patterns
            ('pattern-library/scaling/multi-region.md', 'Multi-Region Deployment', 'Scale across geographic regions'),
            ('pattern-library/scaling/database-sharding.md', 'Database Sharding', 'Horizontal database partitioning'),
            ('pattern-library/scaling/database-per-service.md', 'Database per Service', 'Microservices data isolation'),
            ('pattern-library/scaling/horizontal-pod-autoscaler.md', 'Horizontal Pod Autoscaler', 'Kubernetes autoscaling'),
            ('pattern-library/scaling/geographic-load-balancing.md', 'Geographic Load Balancing', 'Distribute load globally'),
            ('pattern-library/scaling/content-delivery-network.md', 'CDN', 'Content delivery at edge'),
            
            # Communication patterns
            ('pattern-library/communication/publish-subscribe.md', 'Publish-Subscribe', 'Decoupled messaging'),
            ('pattern-library/communication/observability/health-check.md', 'Health Check', 'Service health monitoring'),
            ('pattern-library/communication/architecture/configuration-management.md', 'Configuration Management', 'Centralized config'),
            
            # Data management
            ('pattern-library/data-management/lsm-tree.md', 'LSM Tree', 'Log-structured merge tree'),
            ('pattern-library/data-management/merkle-trees.md', 'Merkle Trees', 'Data verification trees'),
            ('pattern-library/data-management/data-lake.md', 'Data Lake', 'Centralized data repository'),
            ('pattern-library/data-management/materialized-view.md', 'Materialized View', 'Precomputed query results'),
            ('pattern-library/data-management/crdt.md', 'CRDT', 'Conflict-free replicated data types'),
            
            # Architecture patterns
            ('pattern-library/architecture/event-driven.md', 'Event-Driven Architecture', 'Asynchronous event processing'),
            ('pattern-library/architecture/serverless-faas.md', 'Serverless FaaS', 'Function as a Service'),
            ('pattern-library/architecture/lambda-architecture.md', 'Lambda Architecture', 'Batch and stream processing'),
            ('pattern-library/architecture/hybrid-cloud.md', 'Hybrid Cloud', 'On-premise and cloud integration'),
            
            # Resilience patterns
            ('pattern-library/resilience/bulkhead.md', 'Bulkhead', 'Failure isolation'),
            ('pattern-library/resilience/timeout-advanced.md', 'Advanced Timeout', 'Sophisticated timeout strategies'),
            ('pattern-library/resilience/coordination/service-discovery.md', 'Service Discovery', 'Dynamic service location'),
            ('pattern-library/resilience/coordination/deadline-propagation.md', 'Deadline Propagation', 'Request deadline tracking'),
            
            # Coordination patterns
            ('pattern-library/coordination/distributed-queue.md', 'Distributed Queue', 'Queue across nodes'),
            
            # Security patterns
            ('pattern-library/security/zero-trust-security.md', 'Zero Trust Security', 'Never trust, always verify'),
            ('pattern-library/security/location-privacy.md', 'Location Privacy', 'Protect location data'),
            ('pattern-library/security/consent-management.md', 'Consent Management', 'User consent tracking')
        ]
        
        for path, title, desc in patterns:
            file_path = f'docs/{path}'
            self._create_file(file_path, {'title': title, 'description': desc})
    
    def create_missing_architects_handbook_files(self):
        """Create missing architects handbook files"""
        handbook_files = [
            # Case studies
            ('architects-handbook/amazon-dynamo.md', 'Amazon DynamoDB', 'architects-handbook/case-studies/databases/amazon-dynamo'),
            ('architects-handbook/netflix-chaos.md', 'Netflix Chaos Engineering', 'architects-handbook/case-studies/elite-engineering/netflix-chaos'),
            ('architects-handbook/google-spanner.md', 'Google Spanner', 'architects-handbook/case-studies/databases/google-spanner'),
            ('architects-handbook/chat-system.md', 'Chat System Design', 'architects-handbook/case-studies/social-communication/chat-system'),
            ('architects-handbook/consistent-hashing.md', 'Consistent Hashing', 'architects-handbook/case-studies/infrastructure/consistent-hashing'),
            ('architects-handbook/apache-spark.md', 'Apache Spark', 'architects-handbook/case-studies/messaging-streaming/apache-spark'),
            
            # Tools
            ('architects-handbook/tools/latency-calculator.md', 'Latency Calculator', 'Calculate system latency'),
            ('architects-handbook/tools/capacity-calculator.md', 'Capacity Calculator', 'Plan system capacity'),
            ('architects-handbook/tools/throughput-calculator.md', 'Throughput Calculator', 'Estimate throughput'),
            ('architects-handbook/tools/availability-calculator.md', 'Availability Calculator', 'Calculate uptime'),
            ('architects-handbook/tools/cost-optimizer.md', 'Cost Optimizer', 'Optimize cloud costs'),
            ('architects-handbook/tools/consistency-calculator.md', 'Consistency Calculator', 'Analyze consistency models'),
            
            # Quantitative analysis
            ('quantitative-analysis/littles-law.md', "Little's Law", 'architects-handbook/quantitative-analysis/littles-law'),
            ('quantitative-analysis/cap-theorem.md', 'CAP Theorem', 'architects-handbook/quantitative-analysis/cap-theorem'),
            ('quantitative-analysis/queueing-models.md', 'Queueing Models', 'architects-handbook/quantitative-analysis/queueing-models'),
            ('quantitative-analysis/capacity-planning.md', 'Capacity Planning', 'architects-handbook/quantitative-analysis/capacity-planning'),
            ('quantitative-analysis/availability-math.md', 'Availability Math', 'architects-handbook/quantitative-analysis/availability-math'),
            ('quantitative-analysis/coordination-costs.md', 'Coordination Costs', 'architects-handbook/quantitative-analysis/coordination-costs'),
            
            # Human factors
            ('architects-handbook/human-factors/operational-excellence.md', 'Operational Excellence', 'Best practices for operations'),
            ('architects-handbook/human-factors/privacy-engineering.md', 'Privacy Engineering', 'Building privacy into systems'),
            ('architects-handbook/human-factors/mobile-ux.md', 'Mobile UX', 'Mobile user experience'),
            ('architects-handbook/human-factors/content-moderation.md', 'Content Moderation', 'Managing user content'),
            ('architects-handbook/human-factors/community-management.md', 'Community Management', 'Building healthy communities'),
            ('architects-handbook/human-factors/ab-testing.md', 'A/B Testing', 'Experimentation frameworks'),
            ('architects-handbook/human-factors/search-ux.md', 'Search UX', 'Search user experience'),
            ('architects-handbook/human-factors/search-analytics.md', 'Search Analytics', 'Analyzing search behavior')
        ]
        
        for path, title, desc_or_redirect in handbook_files:
            file_path = f'docs/{path}'
            if '/' in desc_or_redirect and not ' ' in desc_or_redirect:
                # It's a redirect
                self._create_file(file_path, {'title': title, 'redirect': desc_or_redirect})
            else:
                # It's a description
                self._create_file(file_path, {'title': title, 'description': desc_or_redirect})
    
    def create_core_principles_redirects(self):
        """Create redirects for core principles patterns"""
        # These are patterns that should redirect to their proper locations
        core_patterns = [
            ('core-principles/pattern-library/resilience/bulkhead/', 'pattern-library/resilience/bulkhead'),
            ('core-principles/pattern-library/resilience/circuit-breaker/', 'pattern-library/resilience/circuit-breaker-transformed'),
            ('core-principles/pattern-library/architecture/cell-based/', 'pattern-library/architecture/cell-based'),
            ('core-principles/pattern-library/scaling/load-balancing/', 'pattern-library/scaling/load-balancing'),
            ('core-principles/pattern-library/scaling/sharding/', 'pattern-library/scaling/sharding'),
            ('core-principles/pattern-library/scaling/multi-region/', 'pattern-library/scaling/geo-distribution'),
            ('core-principles/pattern-library/resilience/retry-backoff/', 'pattern-library/resilience/retry-backoff'),
            ('core-principles/pattern-library/scaling/backpressure/', 'pattern-library/scaling/backpressure'),
            ('core-principles/pattern-library/scaling/rate-limiting/', 'pattern-library/scaling/rate-limiting'),
            ('core-principles/pattern-library/scaling/auto-scaling/', 'pattern-library/scaling/auto-scaling'),
            ('core-principles/pattern-library/architecture/cap-theorem/', 'pattern-library/architecture/cap-theorem'),
            ('core-principles/pattern-library/scaling/caching-strategies/', 'pattern-library/scaling/caching-strategies'),
            ('core-principles/pattern-library/scaling/edge-computing/', 'pattern-library/scaling/edge-computing')
        ]
        
        for from_path, to_path in core_patterns:
            file_path = f'docs/{from_path}index.md'
            self._create_redirect_file(file_path, to_path)
    
    def _create_file(self, file_path: str, metadata: Dict):
        """Create a file with content or redirect"""
        full_path = self.base_dir / file_path
        
        if full_path.exists():
            return
        
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        content_lines = ['---']
        content_lines.append(f"title: {metadata.get('title', 'Page')}")
        
        if 'description' in metadata:
            content_lines.append(f"description: {metadata['description']}")
        
        if 'redirect' in metadata:
            content_lines.append(f"redirect_to: /{metadata['redirect']}/")
        
        content_lines.extend(['---', '', f"# {metadata.get('title', 'Page')}", ''])
        
        if 'redirect' in metadata:
            content_lines.extend([
                '!!! info "This page has moved"',
                f'    Please visit [{metadata["redirect"]}](/{metadata["redirect"]}/)',
                '',
                '<meta http-equiv="refresh" content="0; url=/{metadata["redirect"]}/">'
            ])
        elif 'content' in metadata:
            content_lines.append(metadata['content'])
        else:
            content_lines.append(metadata.get('description', 'This page is under construction.'))
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))
        
        self.files_created += 1
        print(f"Created: {file_path}")
    
    def _create_redirect_file(self, file_path: str, redirect_to: str):
        """Create a redirect file"""
        self._create_file(file_path, {
            'title': 'Redirect',
            'redirect': redirect_to
        })
    
    def fix_all_links_in_files(self):
        """Fix all broken link patterns in existing files"""
        for md_file in self.docs_dir.rglob('*.md'):
            self._fix_file_links(md_file)
    
    def _fix_file_links(self, file_path: Path):
        """Fix links in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix patterns
            replacements = [
                # Remove /index.md from URLs
                (r'(https://[^)]+)/index\.md\)', r'\1/)'),
                # Fix paths with .md in the middle
                (r'([a-z-]+)\.md/([a-z-]+)', r'\1/\2'),
                # Fix architects-handbook duplications
                (r'architects-handbook/architects-handbook/', r'architects-handbook/'),
                # Fix pattern-library paths
                (r'\.\.\.\.\./pattern-library/', r'../'),
                (r'\.\.\.\.\./core-principles/', r'../../core-principles/'),
                (r'\.\.\.\.\./architects-handbook/', r'../../architects-handbook/'),
                # Remove trailing /index.md
                (r'/index\.md\)', r'/)'),
            ]
            
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_modified.add(file_path)
                self.fixes_applied += 1
                
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
    
    def run(self):
        """Run all fixes"""
        print("Starting comprehensive 404 fixes...\n")
        
        print("Creating missing root files...")
        self.create_missing_root_files()
        
        print("\nCreating missing pattern files...")
        self.create_missing_pattern_files()
        
        print("\nCreating missing handbook files...")
        self.create_missing_architects_handbook_files()
        
        print("\nCreating core principles redirects...")
        self.create_core_principles_redirects()
        
        print("\nFixing links in existing files...")
        self.fix_all_links_in_files()
        
        print(f"\n=== Summary ===")
        print(f"Files created: {self.files_created}")
        print(f"Files modified: {len(self.files_modified)}")
        print(f"Link fixes applied: {self.fixes_applied}")

if __name__ == '__main__':
    fixer = ComprehensiveLinkFixer('/home/deepak/DStudio')
    fixer.run()

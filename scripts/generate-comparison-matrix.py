#!/usr/bin/env python3
"""
Pattern Comparison Matrix Generator

Auto-generates pattern comparison tables:
- Groups patterns by problem domain
- Includes tier information
- Exports as markdown tables
"""

import os
import re
import yaml
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PatternInfo:
    """Information about a pattern for comparison"""
    name: str
    category: str
    tier: str
    difficulty: str
    when_to_use: str
    when_not_to_use: str
    status: str
    introduced: str
    relevance: str

class ComparisonMatrixGenerator:
    """Generates comparison matrices for patterns"""
    
    def __init__(self, patterns_dir: Path):
        self.patterns_dir = patterns_dir
        
        # Problem domain groupings
        self.domain_groups = {
            'Communication': [
                'event-sourcing', 'cqrs', 'publish-subscribe', 'request-reply',
                'message-queue', 'event-driven', 'choreography', 'orchestration',
                'competing-consumers', 'priority-queue', 'claim-check',
                'pipes-and-filters', 'routing-slip', 'scatter-gather',
                'splitter', 'aggregator', 'resequencer', 'content-based-router',
                'message-translator', 'envelope-wrapper', 'correlation-id'
            ],
            'Resilience': [
                'circuit-breaker', 'bulkhead', 'retry', 'timeout',
                'rate-limiting', 'health-check', 'heartbeat',
                'compensating-transaction', 'idempotent-receiver'
            ],
            'Distribution': [
                'sharding', 'consistent-hashing', 'geo-replication',
                'leader-election', 'consensus', 'distributed-lock',
                'gossip-protocol', 'vector-clock', 'lamport-timestamp',
                'two-phase-commit', 'three-phase-commit', 'paxos', 'raft'
            ],
            'Service Design': [
                'api-gateway', 'service-mesh', 'sidecar', 'ambassador',
                'adapter', 'anti-corruption-layer', 'bff', 'strangler-fig',
                'service-discovery', 'load-balancing', 'distributed-tracing'
            ],
            'Data Management': [
                'database-per-service', 'shared-database', 'polyglot-persistence',
                'transactional-outbox', 'change-data-capture', 'event-carried-state',
                'write-behind-cache', 'read-through-cache', 'cache-aside',
                'materialized-view', 'data-lake', 'data-mesh'
            ],
            'Deployment': [
                'blue-green-deployment', 'canary-deployment', 'feature-toggle',
                'rolling-deployment', 'immutable-server', 'phoenix-server',
                'deployment-stamps', 'geodes'
            ],
            'Architecture': [
                'microservices', 'monolith', 'serverless', 'modular-monolith',
                'service-oriented', 'event-driven-architecture', 'domain-driven',
                'hexagonal-architecture', 'clean-architecture', 'onion-architecture'
            ]
        }
        
        # Reverse mapping for quick lookup
        self.pattern_to_domain = {}
        for domain, patterns in self.domain_groups.items():
            for pattern in patterns:
                self.pattern_to_domain[pattern] = domain
    
    def extract_pattern_info(self, file_path: Path) -> Optional[PatternInfo]:
        """Extract pattern information from markdown file"""
        pattern_name = file_path.stem
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract front matter
            if not content.startswith('---'):
                return None
            
            end_idx = content.find('---', 3)
            if end_idx == -1:
                return None
            
            yaml_content = content[3:end_idx]
            front_matter = yaml.safe_load(yaml_content) or {}
            
            # Determine domain
            domain = self.pattern_to_domain.get(pattern_name, 'Other')
            
            return PatternInfo(
                name=pattern_name,
                category=front_matter.get('category', 'unknown'),
                tier=front_matter.get('excellence_tier', 'unclassified'),
                difficulty=front_matter.get('difficulty', 'unknown'),
                when_to_use=front_matter.get('when_to_use', ''),
                when_not_to_use=front_matter.get('when_not_to_use', ''),
                status=front_matter.get('pattern_status', 'unknown'),
                introduced=front_matter.get('introduced', ''),
                relevance=front_matter.get('current_relevance', 'unknown')
            )
        except Exception as e:
            logger.error(f"Error extracting info from {file_path}: {e}")
            return None
    
    def load_all_patterns(self) -> Dict[str, List[PatternInfo]]:
        """Load all patterns grouped by domain"""
        patterns_by_domain = {domain: [] for domain in self.domain_groups}
        patterns_by_domain['Other'] = []
        
        # Find all pattern files
        pattern_files = list(self.patterns_dir.glob('*.md'))
        pattern_files = [f for f in pattern_files if f.stem not in ['index', 'README']]
        
        for pattern_file in pattern_files:
            info = self.extract_pattern_info(pattern_file)
            if info:
                domain = self.pattern_to_domain.get(info.name, 'Other')
                patterns_by_domain[domain].append(info)
        
        # Sort patterns within each domain by tier and name
        tier_order = {'gold': 0, 'silver': 1, 'bronze': 2, 'unclassified': 3}
        for domain in patterns_by_domain:
            patterns_by_domain[domain].sort(
                key=lambda p: (tier_order.get(p.tier, 3), p.name)
            )
        
        return patterns_by_domain
    
    def generate_tier_comparison_table(self, patterns: List[PatternInfo]) -> List[str]:
        """Generate comparison table by tier"""
        lines = [
            "| Pattern | Tier | Status | When to Use | When Not to Use |",
            "|---------|------|--------|-------------|-----------------|"]
        
        for pattern in patterns:
            tier_emoji = {
                'gold': '🏆',
                'silver': '🥈',
                'bronze': '🥉'
            }.get(pattern.tier, '')
            
            status_emoji = {
                'recommended': '✅',
                'use_with_caution': '⚠️',
                'legacy': '🚫'
            }.get(pattern.status, '')
            
            # Truncate long descriptions
            when_use = pattern.when_to_use[:60] + '...' if len(pattern.when_to_use) > 60 else pattern.when_to_use
            when_not = pattern.when_not_to_use[:60] + '...' if len(pattern.when_not_to_use) > 60 else pattern.when_not_to_use
            
            lines.append(
                f"| [{pattern.name}]({pattern.name}.md) | "
                f"{tier_emoji} {pattern.tier} | "
                f"{status_emoji} {pattern.status} | "
                f"{when_use} | "
                f"{when_not} |"
            )
        
        return lines
    
    def generate_feature_comparison_table(self, patterns: List[PatternInfo]) -> List[str]:
        """Generate feature comparison table"""
        lines = [
            "| Pattern | Difficulty | Introduced | Current Relevance | Category |",
            "|---------|------------|------------|-------------------|----------|"]
        
        for pattern in patterns:
            difficulty_emoji = {
                'basic': '🟢',
                'intermediate': '🟡',
                'advanced': '🔴'
            }.get(pattern.difficulty, '')
            
            relevance_emoji = {
                'mainstream': '🚀',
                'growing': '📈',
                'stable': '↔️',
                'niche': '🎯',
                'declining': '📉'
            }.get(pattern.relevance, '')
            
            lines.append(
                f"| [{pattern.name}]({pattern.name}.md) | "
                f"{difficulty_emoji} {pattern.difficulty} | "
                f"{pattern.introduced} | "
                f"{relevance_emoji} {pattern.relevance} | "
                f"{pattern.category} |"
            )
        
        return lines
    
    def generate_quick_decision_matrix(self, patterns: List[PatternInfo]) -> List[str]:
        """Generate quick decision matrix"""
        lines = [
            "### Quick Decision Matrix",
            "",
            "| Need | Recommended Pattern(s) | Alternatives |",
            "|------|----------------------|--------------|"]
        
        # Group patterns by common needs
        needs_mapping = {
            'Handle failures gracefully': {
                'primary': ['circuit-breaker', 'bulkhead', 'retry'],
                'alternatives': ['timeout', 'compensating-transaction']
            },
            'Scale horizontally': {
                'primary': ['sharding', 'consistent-hashing'],
                'alternatives': ['geo-replication', 'read-replicas']
            },
            'Coordinate distributed work': {
                'primary': ['leader-election', 'consensus'],
                'alternatives': ['distributed-lock', 'gossip-protocol']
            },
            'Decouple services': {
                'primary': ['event-sourcing', 'publish-subscribe'],
                'alternatives': ['message-queue', 'cqrs']
            },
            'Manage service complexity': {
                'primary': ['api-gateway', 'service-mesh'],
                'alternatives': ['bff', 'anti-corruption-layer']
            },
            'Deploy safely': {
                'primary': ['blue-green-deployment', 'canary-deployment'],
                'alternatives': ['feature-toggle', 'rolling-deployment']
            }
        }
        
        # Filter to only include patterns we have
        available_patterns = {p.name for p in patterns}
        
        for need, mapping in needs_mapping.items():
            primary = [p for p in mapping['primary'] if p in available_patterns]
            alternatives = [p for p in mapping['alternatives'] if p in available_patterns]
            
            if primary:
                primary_links = [f"[{p}]({p}.md)" for p in primary]
                alt_links = [f"[{p}]({p}.md)" for p in alternatives] if alternatives else ['None']
                
                lines.append(
                    f"| {need} | {', '.join(primary_links)} | {', '.join(alt_links)} |"
                )
        
        return lines
    
    def generate_domain_report(self, domain: str, patterns: List[PatternInfo], 
                             output_file: Path):
        """Generate comparison report for a domain"""
        report_lines = [
            f"# {domain} Patterns Comparison",
            f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
            "",
            f"## Overview",
            f"Total patterns in {domain}: {len(patterns)}",
            ""
        ]
        
        # Tier distribution
        tier_counts = {'gold': 0, 'silver': 0, 'bronze': 0, 'unclassified': 0}
        for p in patterns:
            tier_counts[p.tier] = tier_counts.get(p.tier, 0) + 1
        
        report_lines.extend([
            "### Tier Distribution",
            f"- 🏆 Gold: {tier_counts['gold']}",
            f"- 🥈 Silver: {tier_counts['silver']}",
            f"- 🥉 Bronze: {tier_counts['bronze']}",
            f"- Unclassified: {tier_counts['unclassified']}",
            ""
        ])
        
        # Tier comparison table
        report_lines.extend([
            "## Pattern Comparison by Excellence Tier",
            ""
        ])
        report_lines.extend(self.generate_tier_comparison_table(patterns))
        report_lines.append("")
        
        # Feature comparison table
        report_lines.extend([
            "## Pattern Features Comparison",
            ""
        ])
        report_lines.extend(self.generate_feature_comparison_table(patterns))
        report_lines.append("")
        
        # Quick decision matrix
        report_lines.extend(self.generate_quick_decision_matrix(patterns))
        report_lines.append("")
        
        # Write report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Generated comparison matrix for {domain}: {output_file}")
    
    def generate_master_comparison(self, patterns_by_domain: Dict[str, List[PatternInfo]], 
                                 output_file: Path):
        """Generate master comparison matrix"""
        report_lines = [
            "# Master Pattern Comparison Matrix",
            f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## Pattern Distribution by Domain",
            ""
        ]
        
        # Summary table
        report_lines.extend([
            "| Domain | Total | Gold | Silver | Bronze | Unclassified |",
            "|--------|-------|------|--------|--------|--------------|"]
        )
        
        total_counts = {'total': 0, 'gold': 0, 'silver': 0, 'bronze': 0, 'unclassified': 0}
        
        for domain, patterns in patterns_by_domain.items():
            if not patterns:
                continue
            
            counts = {'gold': 0, 'silver': 0, 'bronze': 0, 'unclassified': 0}
            for p in patterns:
                counts[p.tier] = counts.get(p.tier, 0) + 1
            
            report_lines.append(
                f"| {domain} | {len(patterns)} | "
                f"{counts['gold']} | {counts['silver']} | "
                f"{counts['bronze']} | {counts['unclassified']} |"
            )
            
            # Update totals
            total_counts['total'] += len(patterns)
            for tier in ['gold', 'silver', 'bronze', 'unclassified']:
                total_counts[tier] += counts[tier]
        
        # Add totals row
        report_lines.append(
            f"| **TOTAL** | **{total_counts['total']}** | "
            f"**{total_counts['gold']}** | **{total_counts['silver']}** | "
            f"**{total_counts['bronze']}** | **{total_counts['unclassified']}** |"
        )
        
        report_lines.extend(["", ""])
        
        # All gold patterns
        gold_patterns = []
        for patterns in patterns_by_domain.values():
            gold_patterns.extend([p for p in patterns if p.tier == 'gold'])
        
        if gold_patterns:
            report_lines.extend([
                "## 🏆 Gold Standard Patterns",
                "",
                "| Pattern | Domain | Status | Relevance |",
                "|---------|--------|--------|-----------|"]
            )
            
            for p in sorted(gold_patterns, key=lambda x: x.name):
                domain = self.pattern_to_domain.get(p.name, 'Other')
                status_emoji = '✅' if p.status == 'recommended' else '⚠️'
                
                report_lines.append(
                    f"| [{p.name}](patterns/{p.name}.md) | {domain} | "
                    f"{status_emoji} {p.status} | {p.relevance} |"
                )
            
            report_lines.append("")
        
        # Patterns by relevance
        report_lines.extend([
            "## Patterns by Current Relevance",
            ""
        ])
        
        relevance_groups = {'mainstream': [], 'growing': [], 'stable': [], 
                          'niche': [], 'declining': []}
        
        for patterns in patterns_by_domain.values():
            for p in patterns:
                if p.relevance in relevance_groups:
                    relevance_groups[p.relevance].append(p)
        
        for relevance, patterns in relevance_groups.items():
            if patterns:
                emoji = {
                    'mainstream': '🚀',
                    'growing': '📈',
                    'stable': '↔️',
                    'niche': '🎯',
                    'declining': '📉'
                }.get(relevance, '')
                
                report_lines.append(f"### {emoji} {relevance.capitalize()} ({len(patterns)} patterns)")
                
                # Group by tier
                by_tier = {'gold': [], 'silver': [], 'bronze': []}
                for p in patterns:
                    if p.tier in by_tier:
                        by_tier[p.tier].append(p.name)
                
                for tier in ['gold', 'silver', 'bronze']:
                    if by_tier[tier]:
                        tier_emoji = {'gold': '🏆', 'silver': '🥈', 'bronze': '🥉'}[tier]
                        names = ', '.join(f"[{name}](patterns/{name}.md)" for name in sorted(by_tier[tier]))
                        report_lines.append(f"- {tier_emoji} {tier.capitalize()}: {names}")
                
                report_lines.append("")
        
        # Write report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Generated master comparison matrix: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate pattern comparison matrices')
    parser.add_argument('--patterns-dir', type=Path, default=Path('docs/patterns'),
                       help='Directory containing pattern markdown files')
    parser.add_argument('--output-dir', type=Path, default=Path('comparison-matrices'),
                       help='Output directory for comparison matrices')
    parser.add_argument('--domain', help='Generate matrix for specific domain only')
    
    args = parser.parse_args()
    
    # Ensure patterns directory exists
    if not args.patterns_dir.exists():
        logger.error(f"Patterns directory not found: {args.patterns_dir}")
        return 1
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize generator
    generator = ComparisonMatrixGenerator(args.patterns_dir)
    
    # Load all patterns
    patterns_by_domain = generator.load_all_patterns()
    
    if args.domain:
        # Generate for specific domain
        if args.domain not in patterns_by_domain:
            logger.error(f"Unknown domain: {args.domain}")
            logger.info(f"Available domains: {', '.join(patterns_by_domain.keys())}")
            return 1
        
        patterns = patterns_by_domain[args.domain]
        if patterns:
            output_file = args.output_dir / f"{args.domain.lower()}_comparison.md"
            generator.generate_domain_report(args.domain, patterns, output_file)
            print(f"\nComparison matrix generated: {output_file}")
        else:
            print(f"No patterns found for domain: {args.domain}")
    else:
        # Generate for all domains
        for domain, patterns in patterns_by_domain.items():
            if patterns:
                output_file = args.output_dir / f"{domain.lower()}_comparison.md"
                generator.generate_domain_report(domain, patterns, output_file)
        
        # Generate master comparison
        master_file = args.output_dir / 'master_comparison.md'
        generator.generate_master_comparison(patterns_by_domain, master_file)
        
        print(f"\nComparison matrices generated in: {args.output_dir}")
        print(f"  - Master comparison: {master_file}")
        print(f"  - Domain comparisons: {args.output_dir}/*_comparison.md")
    
    return 0

if __name__ == '__main__':
    exit(main())
#!/usr/bin/env python3
"""Fix pattern library references missing category directories."""

import re
from pathlib import Path
import argparse

class PatternLibraryCategoryFixer:
    def __init__(self, docs_dir: Path = Path("docs"), fix: bool = False):
        self.docs_dir = docs_dir
        self.fix = fix
        self.changes_made = []
        
        # Extended pattern to category mappings
        self.pattern_categories = {
            # Resilience patterns
            'circuit-breaker': 'resilience',
            'bulkhead': 'resilience',
            'health-check': 'resilience',
            'health-checks': 'resilience',
            'failover': 'resilience',
            'retry': 'resilience',
            'retry-backoff': 'resilience',
            'timeout': 'resilience',
            'load-shedding': 'resilience',
            'graceful-degradation': 'resilience',
            'heartbeat': 'resilience',
            'split-brain': 'resilience',
            'fault-tolerance': 'resilience',
            
            # Communication patterns
            'api-gateway': 'communication',
            'service-mesh': 'communication',
            'grpc': 'communication',
            'publish-subscribe': 'communication',
            'pub-sub': 'communication',
            'request-reply': 'communication',
            'service-discovery': 'communication',
            'service-registry': 'communication',
            'websocket': 'communication',
            'server-sent-events': 'communication',
            
            # Scaling patterns
            'sharding': 'scaling',
            'caching': 'scaling',
            'caching-strategies': 'scaling',
            'load-balancing': 'scaling',
            'auto-scaling': 'scaling',
            'rate-limiting': 'scaling',
            'scatter-gather': 'scaling',
            'priority-queue': 'scaling',
            'backpressure': 'scaling',
            'edge-computing': 'scaling',
            'geo-distribution': 'scaling',
            'geo-replication': 'scaling',
            'multi-region': 'scaling',
            'request-batching': 'scaling',
            'analytics-scale': 'scaling',
            'id-generation-scale': 'scaling',
            'tile-caching': 'scaling',
            'url-normalization': 'scaling',
            'chunking': 'scaling',
            'queues-streaming': 'scaling',
            
            # Data management patterns
            'event-sourcing': 'data-management',
            'cqrs': 'data-management',
            'saga': 'data-management',
            'write-ahead-log': 'data-management',
            'materialized-view': 'data-management',
            'shared-database': 'data-management',
            'polyglot-persistence': 'data-management',
            'delta-sync': 'data-management',
            'bloom-filter': 'data-management',
            'merkle-trees': 'data-management',
            'consistent-hashing': 'data-management',
            'crdt': 'data-management',
            'outbox': 'data-management',
            'cdc': 'data-management',
            'data-lake': 'data-management',
            'eventual-consistency': 'data-management',
            'read-repair': 'data-management',
            'lsm-tree': 'data-management',
            'segmented-log': 'data-management',
            'tunable-consistency': 'data-management',
            'deduplication': 'data-management',
            'distributed-storage': 'data-management',
            
            # Coordination patterns
            'leader-election': 'coordination',
            'distributed-lock': 'coordination',
            'consensus': 'coordination',
            'clock-sync': 'coordination',
            'logical-clocks': 'coordination',
            'vector-clocks': 'coordination',
            'hlc': 'coordination',
            'lease': 'coordination',
            'distributed-queue': 'coordination',
            'actor-model': 'coordination',
            'state-watch': 'coordination',
            'generation-clock': 'coordination',
            'cas': 'coordination',
            'emergent-leader': 'coordination',
            'leader-follower': 'coordination',
            'low-high-water-marks': 'coordination',
            
            # Architecture patterns
            'strangler-fig': 'architecture',
            'anti-corruption-layer': 'architecture',
            'backends-for-frontends': 'architecture',
            'sidecar': 'architecture',
            'ambassador': 'architecture',
            'cell-based': 'architecture',
            'serverless-faas': 'architecture',
            'lambda-architecture': 'architecture',
            'kappa-architecture': 'architecture',
            'event-streaming': 'architecture',
            'event-driven': 'architecture',
            'choreography': 'architecture',
            'cap-theorem': 'architecture',
            'shared-nothing': 'architecture',
            'valet-key': 'architecture',
            'graphql-federation': 'architecture',
        }
        
    def fix_pattern_references(self, file_path: Path) -> int:
        """Fix pattern library references in a single file."""
        try:
            content = file_path.read_text()
            original_content = content
            changes = 0
            
            # Find all pattern library references
            # Matches: ../pattern-library/pattern-name or /pattern-library/pattern-name
            pattern = r'(\.\./pattern-library/|/pattern-library/)([a-z0-9-]+)(?![a-z0-9-/])'
            
            def replace_pattern(match):
                nonlocal changes
                prefix = match.group(1)
                pattern_name = match.group(2)
                
                # Check if this pattern needs a category
                if pattern_name in self.pattern_categories:
                    category = self.pattern_categories[pattern_name]
                    changes += 1
                    return f'{prefix}{category}/{pattern_name}'
                
                return match.group(0)
            
            content = re.sub(pattern, replace_pattern, content)
            
            # Also fix patterns with .md extension
            pattern_md = r'(\.\./pattern-library/|/pattern-library/)([a-z0-9-]+)(\.md)'
            
            def replace_pattern_md(match):
                nonlocal changes
                prefix = match.group(1)
                pattern_name = match.group(2)
                extension = match.group(3)
                
                if pattern_name in self.pattern_categories:
                    category = self.pattern_categories[pattern_name]
                    changes += 1
                    return f'{prefix}{category}/{pattern_name}{extension}'
                
                return match.group(0)
            
            content = re.sub(pattern_md, replace_pattern_md, content)
            
            # Write back if changed
            if content != original_content and self.fix:
                file_path.write_text(content)
                self.changes_made.append(f"Fixed {changes} patterns in {file_path.relative_to(self.docs_dir)}")
                
            return changes if content != original_content else 0
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return 0
            
    def analyze_and_fix(self):
        """Analyze and fix all pattern library references."""
        print("🔧 FIXING PATTERN LIBRARY CATEGORY REFERENCES...")
        print("="*60)
        
        total_fixed = 0
        files_fixed = 0
        
        for md_file in self.docs_dir.glob("**/*.md"):
            fixes = self.fix_pattern_references(md_file)
            if fixes > 0:
                files_fixed += 1
                total_fixed += fixes
                if not self.fix:
                    print(f"Would fix {fixes} patterns in: {md_file.relative_to(self.docs_dir)}")
                    
        print(f"\n📊 Summary:")
        print(f"  - Files with missing categories: {files_fixed}")
        print(f"  - Total pattern references found: {total_fixed}")
        
        if self.fix:
            print(f"  - Pattern references fixed: {total_fixed}")
        else:
            print(f"  - Pattern references to be fixed: {total_fixed}")
            print(f"\nRun with --fix to apply changes")
            
        if self.changes_made:
            print(f"\n✅ Changes made:")
            for change in self.changes_made[:10]:
                print(f"  - {change}")
            if len(self.changes_made) > 10:
                print(f"  ... and {len(self.changes_made) - 10} more files")

def main():
    parser = argparse.ArgumentParser(description='Fix pattern library category references')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (default: dry run)')
    args = parser.parse_args()
    
    fixer = PatternLibraryCategoryFixer(fix=args.fix)
    fixer.analyze_and_fix()

if __name__ == "__main__":
    main()
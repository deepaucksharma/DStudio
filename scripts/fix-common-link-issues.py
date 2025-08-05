#!/usr/bin/env python3
"""Fix common link issues found in the analysis."""

import re
from pathlib import Path
import argparse

class CommonLinkFixer:
    def __init__(self, docs_dir: Path = Path("docs"), fix: bool = False):
        self.docs_dir = docs_dir
        self.fix = fix
        self.changes_made = []
        self.errors = []
        
    def fix_link_issues_in_file(self, file_path: Path) -> int:
        """Fix common link issues in a single file."""
        try:
            content = file_path.read_text()
            original_content = content
            changes = 0
            
            # Fix 1: Remove /index from end of links
            # [text](path/index) -> [text](path/)
            content = re.sub(r'\]\(([^)]+)/index\)', r'](\1/)', content)
            
            # Fix 2: Fix pattern library links missing category
            # ../pattern-library/circuit-breaker -> ../pattern-library/resilience/circuit-breaker
            pattern_mappings = {
                'circuit-breaker': 'resilience/circuit-breaker',
                'bulkhead': 'resilience/bulkhead',
                'health-checks': 'resilience/health-check',
                'health-check': 'resilience/health-check',
                'failover': 'resilience/failover',
                'retry': 'resilience/retry-backoff',
                'retry-backoff': 'resilience/retry-backoff',
                'timeout': 'resilience/timeout',
                'load-shedding': 'resilience/load-shedding',
                'graceful-degradation': 'resilience/graceful-degradation',
                'heartbeat': 'resilience/heartbeat',
                'split-brain': 'resilience/split-brain',
                'fault-tolerance': 'resilience/fault-tolerance',
                
                'api-gateway': 'communication/api-gateway',
                'service-mesh': 'communication/service-mesh',
                'grpc': 'communication/grpc',
                'publish-subscribe': 'communication/publish-subscribe',
                'request-reply': 'communication/request-reply',
                'service-discovery': 'communication/service-discovery',
                'service-registry': 'communication/service-registry',
                'websocket': 'communication/websocket',
                
                'sharding': 'scaling/sharding',
                'caching': 'scaling/caching-strategies',
                'caching-strategies': 'scaling/caching-strategies',
                'load-balancing': 'scaling/load-balancing',
                'auto-scaling': 'scaling/auto-scaling',
                'rate-limiting': 'scaling/rate-limiting',
                'scatter-gather': 'scaling/scatter-gather',
                'priority-queue': 'scaling/priority-queue',
                'backpressure': 'scaling/backpressure',
                
                'event-sourcing': 'data-management/event-sourcing',
                'event-streaming': 'architecture/event-streaming',
                'cqrs': 'data-management/cqrs',
                'saga': 'data-management/saga',
                'write-ahead-log': 'data-management/write-ahead-log',
                'materialized-view': 'data-management/materialized-view',
                'shared-database': 'data-management/shared-database',
                'polyglot-persistence': 'data-management/polyglot-persistence',
                'delta-sync': 'data-management/delta-sync',
                'bloom-filter': 'data-management/bloom-filter',
                'merkle-trees': 'data-management/merkle-trees',
                'consistent-hashing': 'data-management/consistent-hashing',
                'crdt': 'data-management/crdt',
                
                'leader-election': 'coordination/leader-election',
                'distributed-lock': 'coordination/distributed-lock',
                'consensus': 'coordination/consensus',
                'clock-sync': 'coordination/clock-sync',
                'logical-clocks': 'coordination/logical-clocks',
                'vector-clocks': 'coordination/vector-clocks',
                'hlc': 'coordination/hlc',
                
                'strangler-fig': 'architecture/strangler-fig',
                'anti-corruption-layer': 'architecture/anti-corruption-layer',
                'backends-for-frontends': 'architecture/backends-for-frontends',
                'sidecar': 'architecture/sidecar',
                'ambassador': 'architecture/ambassador',
                'cell-based': 'architecture/cell-based',
                'serverless-faas': 'architecture/serverless-faas',
                'lambda-architecture': 'architecture/lambda-architecture',
                'kappa-architecture': 'architecture/kappa-architecture',
            }
            
            # Apply pattern mappings
            for pattern_name, correct_path in pattern_mappings.items():
                # Fix relative paths
                old_pattern = f'../pattern-library/{pattern_name})'
                new_pattern = f'../pattern-library/{correct_path})'
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    changes += 1
                    
                # Also fix with .md extension
                old_pattern = f'../pattern-library/{pattern_name}.md)'
                new_pattern = f'../pattern-library/{correct_path}.md)'
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    changes += 1
                    
            # Fix 3: Fix links with anchors to non-existent files
            # path.md#anchor -> path/#anchor if path.md doesn't exist but path/index.md does
            def fix_anchor_links(match):
                nonlocal changes
                text = match.group(1)
                path = match.group(2)
                anchor = match.group(3)
                
                # Check if file exists
                source_dir = file_path.parent
                target = source_dir / path
                
                if not target.exists():
                    # Try directory with index.md
                    dir_path = path.replace('.md', '')
                    dir_target = source_dir / dir_path / "index.md"
                    if dir_target.exists():
                        changes += 1
                        return f'[{text}]({dir_path}/#{anchor})'
                        
                return match.group(0)
                
            content = re.sub(r'\[([^\]]+)\]\(([^#)]+\.md)#([^)]+)\)', fix_anchor_links, content)
            
            # Fix 4: Remove .md from links that should be directories
            # core-principles/laws/cognitive-load.md -> core-principles/laws/cognitive-load/
            for law in ['correlated-failure', 'asynchronous-reality', 'emergent-chaos', 
                       'multidimensional-optimization', 'distributed-knowledge', 
                       'cognitive-load', 'economic-reality']:
                content = content.replace(f'/laws/{law}.md', f'/laws/{law}/')
                
            # Write back if changed
            if content != original_content and self.fix:
                file_path.write_text(content)
                self.changes_made.append(f"Fixed {changes} issues in {file_path.relative_to(self.docs_dir)}")
                
            return changes if content != original_content else 0
            
        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {e}")
            return 0
            
    def fix_all_files(self):
        """Fix common link issues in all markdown files."""
        print("🔧 FIXING COMMON LINK ISSUES...")
        print("="*60)
        
        total_fixed = 0
        files_fixed = 0
        
        for md_file in self.docs_dir.glob("**/*.md"):
            fixes = self.fix_link_issues_in_file(md_file)
            if fixes > 0:
                files_fixed += 1
                total_fixed += fixes
                if not self.fix:
                    print(f"Would fix {fixes} issues in: {md_file.relative_to(self.docs_dir)}")
                    
        print(f"\n📊 Summary:")
        print(f"  - Files with issues: {files_fixed}")
        print(f"  - Total issues found: {total_fixed}")
        
        if self.fix:
            print(f"  - Issues fixed: {total_fixed}")
        else:
            print(f"  - Issues to be fixed: {total_fixed}")
            print(f"\nRun with --fix to apply changes")
            
    def generate_report(self):
        """Generate summary report."""
        if self.changes_made:
            print(f"\n✅ Changes made:")
            for change in self.changes_made[:10]:
                print(f"  - {change}")
            if len(self.changes_made) > 10:
                print(f"  ... and {len(self.changes_made) - 10} more files")
                
        if self.errors:
            print(f"\n❌ Errors encountered:")
            for error in self.errors[:5]:
                print(f"  - {error}")

def main():
    parser = argparse.ArgumentParser(description='Fix common link issues')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (default: dry run)')
    args = parser.parse_args()
    
    fixer = CommonLinkFixer(fix=args.fix)
    fixer.fix_all_files()
    fixer.generate_report()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Final comprehensive navigation fix including bidirectional links."""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Set

class FinalNavigationFix:
    def __init__(self, docs_dir: Path = Path("docs")):
        self.docs_dir = docs_dir
        
        # Complete mapping of all variations
        self.tag_mappings = {
            'law1-failure': 'correlated-failure',
            'law2-asynchrony': 'asynchronous-reality',
            'law3-chaos': 'emergent-chaos',
            'law3-emergence': 'emergent-chaos',
            'law4-tradeoffs': 'multidimensional-optimization',
            'law4-optimization': 'multidimensional-optimization',
            'law5-epistemology': 'distributed-knowledge',
            'law6-load': 'cognitive-load',
            'law6-cognitive': 'cognitive-load',
            'law6-human-api': 'cognitive-load',
            'law7-economics': 'economic-reality',
            'part1-axioms': 'laws',
            'part2-pillars': 'pillars',
        }
        
        # Pattern to law mapping for bidirectional links
        self.pattern_to_laws = {
            'bulkhead': ['correlated-failure'],
            'circuit-breaker': ['correlated-failure', 'emergent-chaos'],
            'failover': ['correlated-failure', 'asynchronous-reality'],
            'graceful-degradation': ['correlated-failure', 'multidimensional-optimization'],
            'event-sourcing': ['asynchronous-reality'],
            'cqrs': ['asynchronous-reality'],
            'saga': ['asynchronous-reality'],
            'eventual-consistency': ['asynchronous-reality'],
            'consensus': ['asynchronous-reality', 'distributed-knowledge'],
            'leader-election': ['distributed-knowledge'],
            'api-gateway': ['cognitive-load'],
            'service-mesh': ['cognitive-load'],
            'auto-scaling': ['economic-reality'],
            'rate-limiting': ['emergent-chaos', 'economic-reality'],
            'backpressure': ['emergent-chaos'],
            'sharding': ['multidimensional-optimization'],
            'caching-strategies': ['multidimensional-optimization'],
        }
    
    def fix_frontmatter_tags(self, content: str) -> str:
        """Fix all tags in frontmatter."""
        if not content.startswith('---'):
            return content
            
        parts = content.split('---', 2)
        if len(parts) < 3:
            return content
        
        # Try YAML parsing first
        try:
            frontmatter = yaml.safe_load(parts[1])
            if frontmatter and 'tags' in frontmatter:
                if isinstance(frontmatter['tags'], list):
                    new_tags = []
                    for tag in frontmatter['tags']:
                        new_tags.append(self.tag_mappings.get(tag, tag))
                    frontmatter['tags'] = new_tags
                    
                    new_fm = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
                    return f"---\n{new_fm}---{parts[2]}"
        except:
            pass
        
        # Fallback to string replacement
        fm = parts[1]
        for old_tag, new_tag in self.tag_mappings.items():
            fm = re.sub(f'^(\\s*- ){old_tag}$', f'\\1{new_tag}', fm, flags=re.MULTILINE)
        
        return f"---{fm}---{parts[2]}"
    
    def fix_link_references(self, content: str) -> str:
        """Fix all link references in content."""
        # Fix law4-optimization specifically
        content = content.replace('/law4-optimization/', '/multidimensional-optimization/')
        content = content.replace('law4-optimization)', 'multidimensional-optimization)')
        
        # Fix other law references
        for old_ref, new_ref in self.tag_mappings.items():
            if old_ref.startswith('law'):
                # In links
                content = re.sub(
                    rf'(\[[^\]]*\]\([^)]*){old_ref}([^)]*\))',
                    rf'\1{new_ref}\2',
                    content
                )
                # In paths
                content = content.replace(f'/{old_ref}/', f'/{new_ref}/')
                content = content.replace(f'/{old_ref})', f'/{new_ref})')
        
        return content
    
    def add_bidirectional_links(self, file_path: Path) -> bool:
        """Add missing bidirectional links to patterns."""
        if not str(file_path).startswith(str(self.docs_dir / "pattern-library")):
            return False
            
        pattern_name = file_path.stem
        if pattern_name not in self.pattern_to_laws:
            return False
            
        content = file_path.read_text()
        
        # Check if Related Laws section exists
        if '## Related Laws' in content or '## Relevant Laws' in content:
            return False
            
        # Find insertion point
        insert_marker = '## Related Patterns'
        if insert_marker not in content:
            insert_marker = '## References'
        if insert_marker not in content:
            insert_marker = '## Examples'
            
        if insert_marker in content:
            insert_pos = content.find(insert_marker)
        else:
            # Add before end
            insert_pos = len(content.rstrip())
            content = content.rstrip() + '\n\n'
        
        # Build Related Laws section
        laws_section = '\n## Related Laws\n\n'
        for law_slug in self.pattern_to_laws[pattern_name]:
            law_name = {
                'correlated-failure': 'Correlated Failure',
                'asynchronous-reality': 'Asynchronous Reality',
                'emergent-chaos': 'Emergent Chaos',
                'multidimensional-optimization': 'Multidimensional Optimization',
                'distributed-knowledge': 'Distributed Knowledge',
                'cognitive-load': 'Cognitive Load',
                'economic-reality': 'Economic Reality'
            }.get(law_slug, law_slug.replace('-', ' ').title())
            
            laws_section += f'- [Law: {law_name}](../../core-principles/laws/{law_slug}/)\n'
        
        laws_section += '\n'
        
        # Insert section
        new_content = content[:insert_pos] + laws_section + content[insert_pos:]
        file_path.write_text(new_content)
        
        return True
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix all issues in a single file."""
        content = file_path.read_text()
        original = content
        
        # Fix frontmatter tags
        content = self.fix_frontmatter_tags(content)
        
        # Fix link references
        content = self.fix_link_references(content)
        
        # Add bidirectional links if applicable
        if content != original:
            file_path.write_text(content)
            return True
            
        # Try adding bidirectional links
        if self.add_bidirectional_links(file_path):
            return True
            
        return False
    
    def run(self):
        """Run the final fix on all files."""
        fixed_count = 0
        
        print("Fixing remaining navigation issues...")
        
        # Fix all markdown files
        for md_file in self.docs_dir.glob("**/*.md"):
            if self.fix_file(md_file):
                print(f"Fixed: {md_file.relative_to(self.docs_dir)}")
                fixed_count += 1
        
        print(f"\nTotal files fixed: {fixed_count}")
        
        # Now add pattern references to laws
        print("\nAdding pattern references to laws...")
        self.add_pattern_references_to_laws()
    
    def add_pattern_references_to_laws(self):
        """Add pattern implementation references to law files."""
        laws_dir = self.docs_dir / "core-principles" / "laws"
        
        # Invert pattern_to_laws to get law_to_patterns
        law_to_patterns = {}
        for pattern, laws in self.pattern_to_laws.items():
            for law in laws:
                if law not in law_to_patterns:
                    law_to_patterns[law] = []
                law_to_patterns[law].append(pattern)
        
        for law_slug, patterns in law_to_patterns.items():
            law_file = laws_dir / f"{law_slug}.md"
            if not law_file.exists():
                continue
                
            content = law_file.read_text()
            
            # Skip if already has pattern section
            if '## Pattern Implementations' in content or '## Patterns Addressing This Law' in content:
                continue
                
            # Build pattern section
            section = '\n## Pattern Implementations\n\nPatterns that address this law:\n\n'
            for pattern in sorted(patterns):
                pattern_title = pattern.replace('-', ' ').title()
                # Determine category
                if pattern in ['bulkhead', 'circuit-breaker', 'failover', 'graceful-degradation']:
                    category = 'resilience'
                elif pattern in ['event-sourcing', 'cqrs', 'saga', 'eventual-consistency']:
                    category = 'data-management'
                elif pattern in ['consensus', 'leader-election']:
                    category = 'coordination'
                elif pattern in ['api-gateway', 'service-mesh']:
                    category = 'communication'
                elif pattern in ['auto-scaling', 'rate-limiting', 'backpressure', 'sharding', 'caching-strategies']:
                    category = 'scaling'
                else:
                    category = 'architecture'
                    
                section += f'- [{pattern_title}](../../pattern-library/{category}/{pattern}/)\n'
            
            # Find insertion point
            if '## References' in content:
                insert_pos = content.find('## References')
            elif '## Related Topics' in content:
                insert_pos = content.find('## Related Topics')
            else:
                insert_pos = len(content.rstrip())
                content = content.rstrip() + '\n'
            
            # Insert
            new_content = content[:insert_pos] + section + '\n' + content[insert_pos:]
            law_file.write_text(new_content)
            print(f"Added pattern references to {law_slug}")

def main():
    fixer = FinalNavigationFix()
    fixer.run()

if __name__ == "__main__":
    main()
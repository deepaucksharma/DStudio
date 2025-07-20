#!/usr/bin/env python3
"""
Add consistent navigation to all content files
"""

import os
import re
from pathlib import Path

class NavigationAdder:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.nav_structure = self.build_nav_structure()
        self.updated_count = 0
        
    def build_nav_structure(self):
        """Build navigation structure from file system"""
        nav = {}
        
        # Define the logical order
        sections = [
            ('introduction', 'Introduction'),
            ('part1-axioms', 'Part I: Axioms'),
            ('part2-pillars', 'Part II: Pillars'),
            ('patterns', 'Part III: Patterns'),
            ('quantitative', 'Part IV: Quantitative'),
            ('human-factors', 'Part V: Human Factors'),
            ('case-studies', 'Case Studies'),
            ('reference', 'Reference')
        ]
        
        for section_dir, section_name in sections:
            section_path = self.docs_dir / section_dir
            if section_path.exists():
                nav[section_dir] = {
                    'name': section_name,
                    'path': section_path,
                    'files': list(section_path.rglob('*.md'))
                }
        
        return nav
    
    def get_breadcrumb(self, file_path):
        """Generate breadcrumb navigation"""
        relative = file_path.relative_to(self.docs_dir)
        parts = relative.parts
        
        breadcrumb = ['[Home](/)']
        
        # Build path progressively
        if len(parts) > 1:
            section = parts[0]
            if section in self.nav_structure:
                section_name = self.nav_structure[section]['name']
                breadcrumb.append(f'[{section_name}](/{section}/)')
            
            # Add subsection if applicable
            if len(parts) > 2:
                subsection = parts[1]
                # Clean up subsection name
                if subsection.startswith('axiom'):
                    num = re.search(r'\d+', subsection)
                    if num:
                        breadcrumb.append(f'[Axiom {num.group()}](/{section}/{subsection}/)')
                elif subsection.startswith('pillar'):
                    breadcrumb.append(f'[{subsection.replace("-", " ").title()}](/{section}/{subsection}/)')
                else:
                    breadcrumb.append(f'[{subsection.replace("-", " ").title()}](/{section}/{subsection}/)')
        
        # Current page
        current_name = self.extract_title_from_file(file_path)
        breadcrumb.append(f'**{current_name}**')
        
        return ' → '.join(breadcrumb)
    
    def extract_title_from_file(self, file_path):
        """Extract title from file content or frontmatter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try frontmatter first
            if content.startswith('---'):
                match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
                if match:
                    return match.group(1)
            
            # Try first H1
            h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if h1_match:
                return h1_match.group(1).strip()
                
        except:
            pass
        
        # Fallback to filename
        name = file_path.stem
        if name == 'index':
            name = file_path.parent.name
        return name.replace('-', ' ').replace('_', ' ').title()
    
    def find_prev_next(self, file_path):
        """Find previous and next files in sequence"""
        relative = file_path.relative_to(self.docs_dir)
        parts = relative.parts
        
        if len(parts) < 1:
            return None, None
        
        section = parts[0]
        
        # Special handling for different sections
        if 'axiom' in str(file_path):
            return self.find_axiom_prev_next(file_path)
        elif 'patterns' in section:
            return self.find_pattern_prev_next(file_path)
        elif 'case-studies' in section:
            return self.find_case_study_prev_next(file_path)
        
        return None, None
    
    def find_axiom_prev_next(self, file_path):
        """Find prev/next for axiom files"""
        name = file_path.name
        parent = file_path.parent.name
        
        # Order within an axiom
        if name == 'index.md':
            prev_link = None
            next_link = ('[Examples](examples.md)', 'Examples')
        elif name == 'examples.md':
            prev_link = ('[Overview](./)', 'Overview')
            next_link = ('[Exercises](exercises.md)', 'Exercises')
        elif name == 'exercises.md':
            prev_link = ('[Examples](examples.md)', 'Examples')
            # Next is the next axiom
            axiom_num = int(re.search(r'\d+', parent).group())
            if axiom_num < 8:
                next_link = (f'[Axiom {axiom_num + 1}](../axiom{axiom_num + 1}-*)', f'Axiom {axiom_num + 1}')
            else:
                next_link = ('[Synthesis](../synthesis.md)', 'Synthesis')
        else:
            return None, None
            
        return prev_link, next_link
    
    def find_pattern_prev_next(self, file_path):
        """Find prev/next for pattern files"""
        # Get all pattern files
        pattern_files = sorted([
            f for f in self.docs_dir.glob('patterns/*.md')
            if f.name not in ['index.md', 'PATTERN_TEMPLATE.md', 'PATTERN_STRUCTURE_GUIDE.md']
        ])
        
        try:
            current_idx = pattern_files.index(file_path)
            prev_link = None
            next_link = None
            
            if current_idx > 0:
                prev_file = pattern_files[current_idx - 1]
                prev_title = self.extract_title_from_file(prev_file)
                prev_link = (f'[← {prev_title}]({prev_file.name})', prev_title)
            
            if current_idx < len(pattern_files) - 1:
                next_file = pattern_files[current_idx + 1]
                next_title = self.extract_title_from_file(next_file)
                next_link = (f'[{next_title} →]({next_file.name})', next_title)
                
            return prev_link, next_link
        except:
            return None, None
    
    def find_case_study_prev_next(self, file_path):
        """Find prev/next for case studies"""
        order = [
            'uber-location.md',
            'amazon-dynamo.md', 
            'spotify-recommendations.md',
            'paypal-payments.md'
        ]
        
        name = file_path.name
        if name in order:
            idx = order.index(name)
            prev_link = None
            next_link = None
            
            if idx > 0:
                prev_name = order[idx - 1]
                titles = {
                    'uber-location.md': "Uber's Location System",
                    'amazon-dynamo.md': "Amazon DynamoDB",
                    'spotify-recommendations.md': "Spotify Recommendations",
                    'paypal-payments.md': "PayPal Payments"
                }
                prev_link = (f'[← {titles[prev_name]}]({prev_name})', titles[prev_name])
            
            if idx < len(order) - 1:
                next_name = order[idx + 1]
                titles = {
                    'uber-location.md': "Uber's Location System",
                    'amazon-dynamo.md': "Amazon DynamoDB",
                    'spotify-recommendations.md': "Spotify Recommendations",
                    'paypal-payments.md': "PayPal Payments"
                }
                next_link = (f'[{titles[next_name]} →]({next_name})', titles[next_name])
                
            return prev_link, next_link
            
        return None, None
    
    def find_related_content(self, file_path, content):
        """Find related content based on type and content"""
        related = []
        
        # Extract type from frontmatter or path
        if 'axiom' in str(file_path):
            # Related patterns for axioms
            axiom_patterns = {
                'latency': ['timeout', 'circuit-breaker', 'caching-strategies'],
                'capacity': ['auto-scaling', 'load-balancing', 'sharding'],
                'failure': ['circuit-breaker', 'retry-backoff', 'bulkhead'],
                'concurrency': ['distributed-lock', 'leader-election', 'saga'],
                'coordination': ['consensus', 'distributed-lock', 'leader-election']
            }
            
            for keyword, patterns in axiom_patterns.items():
                if keyword in str(file_path).lower():
                    for pattern in patterns[:3]:  # Top 3
                        related.append(f'[{pattern.replace("-", " ").title()}](/patterns/{pattern}/)')
                    break
                    
        elif 'pattern' in str(file_path):
            # Related patterns
            pattern_relations = {
                'circuit-breaker': ['retry-backoff', 'bulkhead', 'timeout'],
                'event-sourcing': ['cqrs', 'saga', 'event-driven'],
                'cqrs': ['event-sourcing', 'saga', 'event-driven'],
                'distributed-lock': ['leader-election', 'consensus'],
                'sharding': ['consistent-hashing', 'geo-replication']
            }
            
            name = file_path.stem
            if name in pattern_relations:
                for rel in pattern_relations[name][:3]:
                    related.append(f'[{rel.replace("-", " ").title()}](/patterns/{rel}/)')
        
        return related
    
    def add_navigation_to_file(self, file_path):
        """Add navigation to a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if already has navigation
            if '<!-- Navigation -->' in content or '<div class="navigation-header">' in content:
                print(f"  ✓ Already has navigation")
                return
            
            # Generate navigation elements
            breadcrumb = self.get_breadcrumb(file_path)
            prev_link, next_link = self.find_prev_next(file_path)
            related = self.find_related_content(file_path, content)
            
            # Build top navigation
            top_nav = f'<!-- Navigation -->\n{breadcrumb}\n\n'
            
            # Build bottom navigation
            bottom_nav_parts = []
            
            if prev_link or next_link:
                nav_line = []
                if prev_link:
                    nav_line.append(f'**Previous**: {prev_link[0]}')
                if next_link:
                    nav_line.append(f'**Next**: {next_link[0]}')
                bottom_nav_parts.append(' | '.join(nav_line))
            
            if related:
                bottom_nav_parts.append(f'**Related**: {" • ".join(related)}')
            
            if bottom_nav_parts:
                bottom_nav = '\n---\n\n' + '\n\n'.join(bottom_nav_parts) + '\n'
            else:
                bottom_nav = ''
            
            # Find where to insert navigation
            # After frontmatter if present
            if content.startswith('---'):
                fm_end = content.find('\n---\n', 4)
                if fm_end > 0:
                    fm_end += 5  # Include the closing ---\n
                    new_content = content[:fm_end] + '\n' + top_nav + content[fm_end:]
                else:
                    new_content = top_nav + content
            else:
                new_content = top_nav + content
            
            # Add bottom navigation before final quote if present
            if new_content.rstrip().endswith('"'):
                # Find the last quote block
                last_quote = new_content.rfind('\n*"')
                if last_quote > 0:
                    new_content = new_content[:last_quote] + bottom_nav + new_content[last_quote:]
                else:
                    new_content = new_content.rstrip() + '\n' + bottom_nav
            else:
                new_content = new_content.rstrip() + '\n' + bottom_nav
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.updated_count += 1
            print(f"  ✅ Added navigation")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    def process_all(self):
        """Process all markdown files"""
        print("🧭 Adding navigation to all content files...")
        
        for md_file in sorted(self.docs_dir.rglob("*.md")):
            # Skip templates and internal docs
            if any(x in str(md_file) for x in ['TEMPLATE', 'GUIDE', 'STYLE', 'SOLUTION']):
                continue
            
            print(f"\nProcessing {md_file.relative_to(self.docs_dir)}...")
            self.add_navigation_to_file(md_file)
        
        print(f"\n✅ Updated {self.updated_count} files with navigation")


if __name__ == "__main__":
    nav_adder = NavigationAdder()
    nav_adder.process_all()
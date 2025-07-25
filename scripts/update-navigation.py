#!/usr/bin/env python3
"""
Update MkDocs navigation to include all pages using Material's native features.
This script enhances pages with proper navigation without custom CSS/JS.
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Navigation metadata template
NAV_TEMPLATE = """---
title: "{title}"
description: "{description}"
search:
  boost: {boost}
tags:{tags}
---

# {title}

!!! abstract "Overview"
    {description}

**Category:** :material-folder: {category} |
**Updated:** :material-calendar: {date}
"""

PREREQUISITES_TEMPLATE = """
## Prerequisites

!!! prerequisite "Before You Begin"
    
    Make sure you understand these concepts:
    {prerequisites}
"""

RELATED_TEMPLATE = """
## Related Topics

=== "Related {category}"

    <div class="grid cards" markdown>
    {items}
    </div>

=== "See Also"

    {see_also}
"""

NEXT_STEPS_TEMPLATE = """
## Next Steps

!!! success "Continue Learning"
    
    **Explore these related topics:**
    {next_steps}
"""

NAV_FOOTER_TEMPLATE = """
---

<div class="page-nav" markdown>
[:material-arrow-left: {prev_title}]({prev_link}) | 
[:material-arrow-up: {up_title}]({up_link}) | 
[:material-arrow-right: {next_title}]({next_link})
</div>
"""


class NavigationEnhancer:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.page_map: Dict[str, Dict] = {}
        self.nav_structure: Dict = {}
        
    def scan_pages(self):
        """Scan all markdown files and build page map."""
        for md_file in self.docs_dir.rglob("*.md"):
            if any(part.startswith('.') for part in md_file.parts):
                continue  # Skip hidden directories
            
            rel_path = md_file.relative_to(self.docs_dir)
            self.page_map[str(rel_path)] = {
                'path': md_file,
                'rel_path': rel_path,
                'title': self._extract_title(md_file),
                'category': self._determine_category(rel_path),
                'boost': self._calculate_boost(rel_path),
                'tags': self._generate_tags(rel_path),
            }
    
    def _extract_title(self, file_path: Path) -> str:
        """Extract title from markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Try to extract from front matter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter = yaml.safe_load(parts[1])
                    if 'title' in front_matter:
                        return front_matter['title']
            
            # Try to extract from first heading
            match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if match:
                return match.group(1).strip()
                
        except Exception:
            pass
            
        # Fallback to filename
        return file_path.stem.replace('-', ' ').replace('_', ' ').title()
    
    def _determine_category(self, rel_path: Path) -> str:
        """Determine category based on path."""
        parts = rel_path.parts
        if len(parts) > 0:
            category_map = {
                'part1-axioms': 'Laws',
                'part2-pillars': 'Pillars',
                'patterns': 'Patterns',
                'case-studies': 'Case Studies',
                'quantitative': 'Theory',
                'tools': 'Tools',
                'tutorials': 'Tutorials',
                'reference': 'Reference',
                'human-factors': 'Operations',
                'google-interviews': 'Interviews',
                'learning-paths': 'Learning Paths',
            }
            return category_map.get(parts[0], 'General')
        return 'General'
    
    def _calculate_boost(self, rel_path: Path) -> float:
        """Calculate search boost based on importance."""
        path_str = str(rel_path).lower()
        
        # High priority pages
        if any(x in path_str for x in ['index.md', 'overview.md', 'getting-started']):
            return 2.0
        
        # Important patterns and concepts
        if any(x in path_str for x in ['circuit-breaker', 'cap-theorem', 'consistency', 
                                        'saga', 'cqrs', 'event-sourcing']):
            return 1.5
        
        # Laws and pillars
        if 'law' in path_str or 'pillar' in path_str:
            return 1.5
            
        return 1.0
    
    def _generate_tags(self, rel_path: Path) -> List[str]:
        """Generate tags based on path and content."""
        tags = []
        path_str = str(rel_path).lower()
        
        # Category tags
        if 'patterns' in path_str:
            tags.append('pattern')
        if 'case-studies' in path_str:
            tags.append('case-study')
        if 'quantitative' in path_str:
            tags.append('theory')
        if 'axioms' in path_str:
            tags.append('fundamental')
            
        # Topic tags
        topic_tags = {
            'resilience': ['circuit-breaker', 'retry', 'bulkhead', 'timeout'],
            'consistency': ['cap', 'consensus', 'eventual', 'strong'],
            'performance': ['cache', 'shard', 'scale', 'latency'],
            'security': ['encrypt', 'auth', 'key', 'vault'],
        }
        
        for tag, keywords in topic_tags.items():
            if any(kw in path_str for kw in keywords):
                tags.append(tag)
                
        return tags
    
    def find_related_pages(self, page_path: str, max_items: int = 6) -> List[Tuple[str, str]]:
        """Find related pages based on category and tags."""
        current_page = self.page_map.get(page_path)
        if not current_page:
            return []
            
        related = []
        current_tags = set(current_page['tags'])
        current_category = current_page['category']
        
        for path, page in self.page_map.items():
            if path == page_path:
                continue
                
            # Calculate relevance score
            score = 0
            
            # Same category bonus
            if page['category'] == current_category:
                score += 2
                
            # Shared tags bonus
            shared_tags = len(set(page['tags']) & current_tags)
            score += shared_tags
            
            # Path similarity bonus
            if Path(path).parent == Path(page_path).parent:
                score += 1
                
            if score > 0:
                related.append((score, path, page))
        
        # Sort by score and return top items
        related.sort(key=lambda x: x[0], reverse=True)
        return [(path, page) for _, path, page in related[:max_items]]
    
    def enhance_page(self, page_path: str, dry_run: bool = False):
        """Enhance a single page with navigation features."""
        page_info = self.page_map.get(page_path)
        if not page_info:
            return
            
        file_path = page_info['path']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Skip if already enhanced
            if '!!! abstract "Overview"' in content:
                print(f"Skipping {page_path} - already enhanced")
                return
                
            # Extract existing front matter
            front_matter = {}
            body = content
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter = yaml.safe_load(parts[1]) or {}
                    body = parts[2]
                    
            # Update front matter
            front_matter['search'] = {'boost': page_info['boost']}
            if page_info['tags']:
                front_matter['tags'] = page_info['tags']
                
            # Build enhanced content
            enhanced = f"---\n{yaml.dump(front_matter, default_flow_style=False)}---\n\n"
            
            # Add overview if main title exists
            if match := re.search(r'^#\s+(.+)$', body, re.MULTILINE):
                title = match.group(1)
                # Add overview after title
                body = body.replace(
                    match.group(0),
                    f"{match.group(0)}\n\n!!! abstract \"Overview\"\n    {front_matter.get('description', 'Overview content here.')}\n"
                )
                
            # Add prerequisites section if related pages exist
            related_pages = self.find_related_pages(page_path)
            if related_pages and 'Prerequisites' not in body:
                prereq_links = []
                for rel_path, rel_page in related_pages[:3]:
                    prereq_links.append(
                        f"    - :material-book: [{rel_page['title']}](/{rel_path}) - Related concept"
                    )
                    
                if prereq_links:
                    # Find a good place to insert prerequisites
                    insert_pos = body.find('\n## ')
                    if insert_pos > 0:
                        body = (body[:insert_pos] + 
                               PREREQUISITES_TEMPLATE.format(prerequisites='\n'.join(prereq_links)) +
                               body[insert_pos:])
                               
            # Add navigation footer
            nav_footer = self._generate_nav_footer(page_path)
            if nav_footer and '[:material-arrow-left:' not in body:
                body += f"\n{nav_footer}"
                
            enhanced += body
            
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced)
                print(f"Enhanced {page_path}")
            else:
                print(f"Would enhance {page_path}")
                
        except Exception as e:
            print(f"Error enhancing {page_path}: {e}")
            
    def _generate_nav_footer(self, page_path: str) -> str:
        """Generate navigation footer for the page."""
        path = Path(page_path)
        parent_dir = path.parent
        
        # Find siblings
        siblings = []
        if parent_dir != Path('.'):
            for sibling in self.page_map:
                if Path(sibling).parent == parent_dir and sibling != page_path:
                    siblings.append(sibling)
                    
        siblings.sort()
        
        # Find current position
        current_idx = -1
        if page_path in siblings:
            current_idx = siblings.index(page_path)
            
        prev_page = siblings[current_idx - 1] if current_idx > 0 else None
        next_page = siblings[current_idx + 1] if current_idx < len(siblings) - 1 else None
        
        # Build navigation
        nav_parts = []
        
        if prev_page:
            prev_info = self.page_map[prev_page]
            nav_parts.append(f"[:material-arrow-left: {prev_info['title']}](/{prev_page})")
        
        # Up navigation
        if parent_dir != Path('.'):
            parent_index = parent_dir / 'index.md'
            if str(parent_index) in self.page_map:
                parent_info = self.page_map[str(parent_index)]
                nav_parts.append(f"[:material-arrow-up: {parent_info['title']}](/{parent_index})")
                
        if next_page:
            next_info = self.page_map[next_page]
            nav_parts.append(f"[:material-arrow-right: {next_info['title']}](/{next_page})")
            
        if nav_parts:
            return f"\n---\n\n{' | '.join(nav_parts)}"
            
        return ""
    
    def enhance_all(self, dry_run: bool = False):
        """Enhance all pages with navigation."""
        print("Scanning pages...")
        self.scan_pages()
        print(f"Found {len(self.page_map)} pages")
        
        # Enhance pages by category
        categories = {}
        for page_path, page_info in self.page_map.items():
            cat = page_info['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(page_path)
            
        for category, pages in categories.items():
            print(f"\nEnhancing {category} pages ({len(pages)} pages)...")
            for page_path in sorted(pages):
                self.enhance_page(page_path, dry_run)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhance MkDocs pages with native Material navigation')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--docs-dir', default='docs', help='Documentation directory (default: docs)')
    parser.add_argument('--page', help='Enhance only a specific page')
    
    args = parser.parse_args()
    
    enhancer = NavigationEnhancer(args.docs_dir)
    
    if args.page:
        enhancer.scan_pages()
        enhancer.enhance_page(args.page, args.dry_run)
    else:
        enhancer.enhance_all(args.dry_run)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Add breadcrumb navigation to all pages in the documentation.
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

# Breadcrumb patterns for different sections
BREADCRUMB_PATTERNS = {
    'part1-axioms/law': '[Home](/) > [Learn](/learn/) > [The 7 Laws](/part1-axioms/) > {title}',
    'part2-pillars': '[Home](/) > [Learn](/learn/) > [The 5 Pillars](/part2-pillars/) > {title}',
    'patterns': '[Home](/) > [Patterns](/patterns/) > {title}',
    'case-studies': '[Home](/) > [Case Studies](/case-studies/) > {title}',
    'quantitative': '[Home](/) > [Quantitative](/quantitative/) > {title}',
    'learning-paths': '[Home](/) > [Learn](/learn/) > [Learning Paths](/learning-paths/) > {title}',
    'tools': '[Home](/) > [Tools](/tools/) > {title}',
    'google-interviews': '[Home](/) > [Interviews](/google-interviews/) > {title}',
    'human-factors': '[Home](/) > [Human Factors](/human-factors/) > {title}',
    'reference': '[Home](/) > [Reference](/reference/) > {title}',
}

# Navigation structure for prev/next links
NAV_STRUCTURE = {
    'part1-axioms': {
        'law1-failure': ('index', 'law2-asynchrony'),
        'law2-asynchrony': ('law1-failure', 'law3-emergence'),
        'law3-emergence': ('law2-asynchrony', 'law4-tradeoffs'),
        'law4-tradeoffs': ('law3-emergence', 'law5-epistemology'),
        'law5-epistemology': ('law4-tradeoffs', 'law6-human-api'),
        'law6-human-api': ('law5-epistemology', 'law7-economics'),
        'law7-economics': ('law6-human-api', 'quiz'),
    },
    'part2-pillars': {
        'work': ('index', 'state'),
        'state': ('work', 'truth'),
        'truth': ('state', 'control'),
        'control': ('truth', 'intelligence'),
        'intelligence': ('control', 'decision-tree'),
    }
}


class BreadcrumbAdder:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        
    def get_breadcrumb_pattern(self, file_path: Path) -> Optional[str]:
        """Determine which breadcrumb pattern to use based on file path."""
        rel_path = file_path.relative_to(self.docs_dir)
        path_str = str(rel_path).replace('\\', '/')
        
        for pattern_key, pattern in BREADCRUMB_PATTERNS.items():
            if path_str.startswith(pattern_key):
                return pattern
                
        # Check parent directory
        if len(rel_path.parts) > 1:
            parent_key = rel_path.parts[0]
            if parent_key in BREADCRUMB_PATTERNS:
                return BREADCRUMB_PATTERNS[parent_key]
                
        return None
        
    def extract_title(self, content: str) -> str:
        """Extract title from markdown content."""
        # Try front matter first
        if content.startswith('---'):
            match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
            if match:
                return match.group(1)
                
        # Try first heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1)
            
        return "Page"
        
    def get_navigation_links(self, file_path: Path) -> Tuple[Optional[str], Optional[str]]:
        """Get previous and next page links based on navigation structure."""
        rel_path = file_path.relative_to(self.docs_dir)
        
        if len(rel_path.parts) >= 2:
            section = rel_path.parts[0]
            subsection = rel_path.stem
            
            if section in NAV_STRUCTURE and subsection in NAV_STRUCTURE[section]:
                prev_page, next_page = NAV_STRUCTURE[section][subsection]
                
                prev_link = f"/{section}/{prev_page}/" if prev_page else None
                next_link = f"/{section}/{next_page}/" if next_page else None
                
                return prev_link, next_link
                
        return None, None
        
    def add_breadcrumb(self, file_path: Path, dry_run: bool = False):
        """Add breadcrumb navigation to a markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Skip if breadcrumb already exists
            if '[Home](/)' in content and '>' in content[:500]:
                print(f"Skipping {file_path} - breadcrumb already exists")
                return
                
            # Get breadcrumb pattern
            pattern = self.get_breadcrumb_pattern(file_path)
            if not pattern:
                print(f"No pattern for {file_path}")
                return
                
            # Extract title
            title = self.extract_title(content)
            breadcrumb = pattern.format(title=title)
            
            # Find where to insert breadcrumb
            if content.startswith('---'):
                # After front matter
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # Find first heading after front matter
                    match = re.search(r'^(#\s+.+)$', parts[2], re.MULTILINE)
                    if match:
                        # Insert after heading
                        parts[2] = parts[2].replace(
                            match.group(0),
                            f"{match.group(0)}\n\n{breadcrumb}\n",
                            1
                        )
                        new_content = '---'.join(parts)
                    else:
                        # Insert at beginning of content
                        new_content = f"---{parts[1]}---\n\n{breadcrumb}\n{parts[2]}"
            else:
                # Find first heading
                match = re.search(r'^(#\s+.+)$', content, re.MULTILINE)
                if match:
                    new_content = content.replace(
                        match.group(0),
                        f"{match.group(0)}\n\n{breadcrumb}\n",
                        1
                    )
                else:
                    new_content = f"{breadcrumb}\n\n{content}"
                    
            # Add navigation footer if applicable
            prev_link, next_link = self.get_navigation_links(file_path)
            if (prev_link or next_link) and '[:material-arrow-' not in content:
                nav_parts = []
                if prev_link:
                    nav_parts.append(f"[:material-arrow-left: Previous]({prev_link})")
                nav_parts.append(f"[:material-arrow-up: Up](../)")
                if next_link:
                    nav_parts.append(f"[:material-arrow-right: Next]({next_link})")
                    
                nav_footer = f"\n\n---\n\n{' | '.join(nav_parts)}"
                new_content = new_content.rstrip() + nav_footer + "\n"
                
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Added breadcrumb to {file_path}")
            else:
                print(f"Would add breadcrumb to {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    def process_all(self, dry_run: bool = False):
        """Process all markdown files in the docs directory."""
        for md_file in self.docs_dir.rglob("*.md"):
            # Skip hidden directories and special files
            if any(part.startswith('.') for part in md_file.parts):
                continue
            if md_file.name in ['README.md', 'CHANGELOG.md']:
                continue
                
            self.add_breadcrumb(md_file, dry_run)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Add breadcrumb navigation to documentation')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--docs-dir', default='docs', help='Documentation directory')
    parser.add_argument('--file', help='Process only a specific file')
    
    args = parser.parse_args()
    
    adder = BreadcrumbAdder(args.docs_dir)
    
    if args.file:
        adder.add_breadcrumb(Path(args.file), args.dry_run)
    else:
        adder.process_all(args.dry_run)


if __name__ == '__main__':
    main()
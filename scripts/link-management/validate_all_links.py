#!/usr/bin/env python3
"""
Validate all links in the documentation to identify remaining issues.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class LinkValidator:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.all_files = self._build_file_map()
        self.broken_links = defaultdict(list)
        self.empty_links = defaultdict(list)
        self.external_links = defaultdict(list)
        self.valid_links = 0
        
    def _build_file_map(self) -> Set[str]:
        """Build a set of all existing markdown files."""
        files = set()
        for file_path in self.docs_dir.rglob("*.md"):
            # Store relative path from docs directory
            rel_path = file_path.relative_to(self.docs_dir)
            files.add(str(rel_path))
            # Also store without extension
            files.add(str(rel_path).replace('.md', ''))
            # Store directory paths for index.md files
            if file_path.name == 'index.md':
                parent = str(rel_path.parent)
                if parent != '.':
                    files.add(parent)
        return files
    
    def validate_file(self, file_path: Path) -> Dict[str, List]:
        """Validate all links in a single file."""
        issues = {
            'broken': [],
            'empty': [],
            'external': []
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Find all markdown links
            link_pattern = r'\[([^\]]*)\]\(([^\)]*)\)'
            matches = re.finditer(link_pattern, content)
            
            for match in matches:
                link_text = match.group(1)
                link_url = match.group(2)
                line_num = content[:match.start()].count('\n') + 1
                
                # Skip anchors
                if link_url.startswith('#'):
                    self.valid_links += 1
                    continue
                
                # Check for empty links
                if not link_url or link_url.isspace():
                    issues['empty'].append({
                        'line': line_num,
                        'text': link_text,
                        'url': link_url
                    })
                    continue
                
                # Check for external links
                if link_url.startswith('http://') or link_url.startswith('https://'):
                    issues['external'].append({
                        'line': line_num,
                        'text': link_text,
                        'url': link_url
                    })
                    continue
                
                # Validate internal links
                if not self._validate_internal_link(file_path, link_url):
                    issues['broken'].append({
                        'line': line_num,
                        'text': link_text,
                        'url': link_url
                    })
                else:
                    self.valid_links += 1
                    
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
        
        return issues
    
    def _validate_internal_link(self, source_file: Path, link_url: str) -> bool:
        """Check if an internal link points to an existing file."""
        # Remove anchor if present
        link_path = link_url.split('#')[0]
        
        if not link_path:
            return True  # Pure anchor link
        
        # Get the directory of the source file
        source_dir = source_file.parent
        
        # Try to resolve the link
        if link_path.startswith('/'):
            # Absolute path from docs root
            target = self.docs_dir / link_path.lstrip('/')
        else:
            # Relative path
            target = (source_dir / link_path).resolve()
        
        # Check if it's within docs directory
        try:
            target_rel = target.relative_to(self.docs_dir)
        except ValueError:
            # Path is outside docs directory
            return False
        
        # Check various possibilities
        target_str = str(target_rel).replace('\\', '/')
        
        # Direct match
        if target_str in self.all_files:
            return True
        
        # Try with .md extension
        if f"{target_str}.md" in self.all_files:
            return True
        
        # Try as directory with index.md
        if f"{target_str}/index.md" in self.all_files:
            return True
        
        return False
    
    def validate_all(self):
        """Validate all markdown files."""
        all_files = list(self.docs_dir.rglob("*.md"))
        total = len(all_files)
        
        logger.info(f"Validating links in {total} files...")
        
        for i, file_path in enumerate(all_files, 1):
            if i % 50 == 0:
                logger.info(f"Progress: {i}/{total}")
            
            issues = self.validate_file(file_path)
            
            rel_path = str(file_path.relative_to(self.docs_dir))
            
            if issues['broken']:
                self.broken_links[rel_path] = issues['broken']
            if issues['empty']:
                self.empty_links[rel_path] = issues['empty']
            if issues['external']:
                self.external_links[rel_path] = issues['external']
    
    def generate_report(self):
        """Generate a comprehensive validation report."""
        total_broken = sum(len(links) for links in self.broken_links.values())
        total_empty = sum(len(links) for links in self.empty_links.values())
        total_external = sum(len(links) for links in self.external_links.values())
        
        print("\n" + "=" * 80)
        print("LINK VALIDATION REPORT")
        print("=" * 80)
        
        print(f"\nSUMMARY:")
        print(f"  Valid internal links: {self.valid_links}")
        print(f"  Broken internal links: {total_broken}")
        print(f"  Empty links: {total_empty}")
        print(f"  External links: {total_external}")
        print(f"  Files with issues: {len(self.broken_links) + len(self.empty_links)}")
        
        if self.broken_links:
            print(f"\n{'=' * 80}")
            print(f"BROKEN INTERNAL LINKS ({total_broken} total)")
            print(f"{'=' * 80}")
            
            for file_path, links in sorted(self.broken_links.items()):
                print(f"\n{file_path}:")
                for link in links:
                    print(f"  Line {link['line']}: [{link['text']}]({link['url']})")
        
        if self.empty_links:
            print(f"\n{'=' * 80}")
            print(f"EMPTY LINKS ({total_empty} total)")
            print(f"{'=' * 80}")
            
            for file_path, links in sorted(self.empty_links.items()):
                print(f"\n{file_path}:")
                for link in links:
                    print(f"  Line {link['line']}: [{link['text']}]()")
        
        # Create a fix summary
        if total_broken > 0:
            print(f"\n{'=' * 80}")
            print("RECOMMENDED FIXES")
            print(f"{'=' * 80}")
            
            # Group broken links by pattern
            patterns = defaultdict(list)
            for file_path, links in self.broken_links.items():
                for link in links:
                    url = link['url']
                    if '.md/' in url:
                        patterns['md_as_directory'].append((file_path, link))
                    elif url.count('../') > 3:
                        patterns['excessive_parent'].append((file_path, link))
                    elif url.endswith('/'):
                        patterns['trailing_slash'].append((file_path, link))
                    else:
                        patterns['other'].append((file_path, link))
            
            for pattern, items in patterns.items():
                if items:
                    print(f"\n{pattern.upper().replace('_', ' ')} ({len(items)} instances):")
                    for file_path, link in items[:3]:  # Show first 3 examples
                        print(f"  {file_path}: {link['url']}")
                    if len(items) > 3:
                        print(f"  ... and {len(items) - 3} more")

def check_mkdocs_navigation():
    """Check if all files in mkdocs.yml navigation exist."""
    mkdocs_path = Path("mkdocs.yml")
    if not mkdocs_path.exists():
        logger.error("mkdocs.yml not found")
        return
    
    print(f"\n{'=' * 80}")
    print("MKDOCS.YML NAVIGATION CHECK")
    print(f"{'=' * 80}")
    
    # Use simple YAML parsing to avoid the Python tag issue
    with open(mkdocs_path, 'r') as f:
        content = f.read()
    
    # Extract nav section using simple string parsing
    nav_start = content.find('nav:')
    if nav_start == -1:
        print("No navigation section found")
        return
    
    nav_section = content[nav_start:]
    nav_end = nav_section.find('\n\n')
    if nav_end != -1:
        nav_section = nav_section[:nav_end]
    
    # Find all file references (crude but effective)
    file_pattern = r':\s*([a-zA-Z0-9_/-]+\.md)'
    matches = re.findall(file_pattern, nav_section)
    
    missing_files = []
    for file_ref in matches:
        file_path = Path('docs') / file_ref
        if not file_path.exists():
            missing_files.append(file_ref)
    
    if missing_files:
        print(f"\nMissing navigation files ({len(missing_files)}):")
        for file_ref in missing_files:
            print(f"  - {file_ref}")
    else:
        print("\nAll navigation files exist!")
    
    # Check for redirects
    redirect_pattern = r'([a-zA-Z0-9_/-]+\.md):\s*([a-zA-Z0-9_/-]+\.md)'
    redirects = re.findall(redirect_pattern, content)
    
    if redirects:
        print(f"\nRedirects configured: {len(redirects)}")
        print("(These help with URL migrations)")

def main():
    """Main entry point."""
    validator = LinkValidator()
    validator.validate_all()
    validator.generate_report()
    
    # Check mkdocs navigation
    check_mkdocs_navigation()
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
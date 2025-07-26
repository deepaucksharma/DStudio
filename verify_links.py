#!/usr/bin/env python3
"""
Link verification tool for DStudio documentation.
Checks all internal links to ensure they point to existing files.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json

class LinkVerifier:
    def __init__(self, docs_root="docs"):
        self.docs_root = Path(docs_root)
        self.broken_links = defaultdict(list)
        self.all_links = defaultdict(list)
        self.existing_files = set()
        
        # Common link patterns in markdown
        self.link_patterns = [
            r'\[([^\]]+)\]\(([^)]+)\)',  # [text](link)
            r'["\']([^"\']+\.md)["\']',   # "file.md" or 'file.md'
            r'href=["\']([^"\']+)["\']',  # href="link"
        ]
        
        # Collect all existing .md files
        self._collect_existing_files()
        
    def _collect_existing_files(self):
        """Collect all existing markdown files."""
        for md_file in self.docs_root.rglob("*.md"):
            # Store relative path from docs root
            rel_path = md_file.relative_to(self.docs_root)
            self.existing_files.add(str(rel_path))
            # Also store without .md extension
            self.existing_files.add(str(rel_path).replace('.md', ''))
            # Store with leading slash
            self.existing_files.add('/' + str(rel_path))
            self.existing_files.add('/' + str(rel_path).replace('.md', ''))
    
    def _normalize_link(self, link, source_file):
        """Normalize link path relative to source file."""
        # Skip external links
        if link.startswith(('http://', 'https://', 'mailto:', '#')):
            return None
            
        # Remove anchors
        if '#' in link:
            link = link.split('#')[0]
            
        # Skip empty links
        if not link:
            return None
            
        # Handle absolute paths
        if link.startswith('/'):
            return link[1:]  # Remove leading slash
            
        # Handle relative paths
        source_dir = source_file.parent
        if link.startswith('../'):
            # Navigate up directories
            path_parts = link.split('/')
            try:
                # Start from source directory
                current_path = self.docs_root / source_dir
                
                for part in path_parts:
                    if part == '..':
                        current_path = current_path.parent
                    elif part and part != '.':
                        current_path = current_path / part
                        
                # Get relative path from docs root
                if current_path.is_relative_to(self.docs_root):
                    return str(current_path.relative_to(self.docs_root))
                else:
                    # Path goes outside docs root
                    return None
            except Exception:
                return None
        else:
            # Same directory or subdirectory
            if source_dir == Path('.'):
                return link
            else:
                return str(source_dir) + '/' + link
    
    def verify_file(self, file_path):
        """Verify all links in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return
            
        rel_path = Path(file_path).relative_to(self.docs_root)
        
        # Find all links
        for pattern in self.link_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    # For pattern with groups
                    link = match[1] if len(match) > 1 else match[0]
                else:
                    link = match
                    
                # Normalize the link
                normalized = self._normalize_link(link, rel_path)
                if normalized is None:
                    continue
                    
                self.all_links[str(rel_path)].append({
                    'original': link,
                    'normalized': normalized
                })
                
                # Check if file exists
                if not self._link_exists(normalized):
                    self.broken_links[str(rel_path)].append({
                        'link': link,
                        'normalized': normalized,
                        'pattern': pattern
                    })
    
    def _link_exists(self, normalized_link):
        """Check if a link points to an existing file."""
        # Check various forms
        variants = [
            normalized_link,
            normalized_link + '.md',
            normalized_link.replace('.md', ''),
            normalized_link + '/index.md',
            normalized_link.replace('/index', '')
        ]
        
        for variant in variants:
            if variant in self.existing_files:
                return True
                
        return False
    
    def verify_all(self):
        """Verify all markdown files in the docs directory."""
        md_files = list(self.docs_root.rglob("*.md"))
        total_files = len(md_files)
        
        print(f"Checking {total_files} markdown files...")
        
        for i, md_file in enumerate(md_files):
            if (i + 1) % 50 == 0:
                print(f"Progress: {i + 1}/{total_files}")
            self.verify_file(md_file)
            
        print(f"\nVerification complete!")
        
    def generate_report(self):
        """Generate a comprehensive report of broken links."""
        report = {
            'summary': {
                'total_files_checked': len(self.all_links),
                'files_with_broken_links': len(self.broken_links),
                'total_broken_links': sum(len(links) for links in self.broken_links.values()),
                'total_links_checked': sum(len(links) for links in self.all_links.values())
            },
            'broken_links_by_file': {}
        }
        
        # Group broken links by file
        for file_path, broken_links in sorted(self.broken_links.items()):
            report['broken_links_by_file'][file_path] = {
                'count': len(broken_links),
                'links': broken_links
            }
            
        return report
    
    def print_report(self):
        """Print a formatted report of broken links."""
        report = self.generate_report()
        
        print("\n" + "="*80)
        print("LINK VERIFICATION REPORT")
        print("="*80)
        
        print(f"\nSummary:")
        print(f"  Files checked: {report['summary']['total_files_checked']}")
        print(f"  Total links: {report['summary']['total_links_checked']}")
        print(f"  Files with broken links: {report['summary']['files_with_broken_links']}")
        print(f"  Total broken links: {report['summary']['total_broken_links']}")
        
        if report['broken_links_by_file']:
            print(f"\n\nBroken Links by File:")
            print("-"*80)
            
            for file_path, data in report['broken_links_by_file'].items():
                print(f"\n📄 {file_path} ({data['count']} broken links)")
                for link_data in data['links']:
                    print(f"   ❌ {link_data['link']}")
                    print(f"      Normalized: {link_data['normalized']}")
                    
        else:
            print("\n✅ No broken links found!")
            
        return report

def main():
    """Main function to run link verification."""
    verifier = LinkVerifier("docs")
    verifier.verify_all()
    report = verifier.print_report()
    
    # Save detailed report as JSON
    with open('broken_links_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n\nDetailed report saved to: broken_links_report.json")
    
    # Return exit code based on whether broken links were found
    return 1 if report['summary']['total_broken_links'] > 0 else 0

if __name__ == "__main__":
    exit(main())
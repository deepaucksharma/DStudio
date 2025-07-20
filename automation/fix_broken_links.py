#!/usr/bin/env python3
"""
Fix all broken internal links in the documentation
"""

import os
import re
from pathlib import Path
from collections import defaultdict

class LinkFixer:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.link_mapping = {}
        self.broken_links = defaultdict(list)
        self.fixed_count = 0
        
    def scan_all_files(self):
        """Build a map of all available files"""
        file_map = {}
        for md_file in self.docs_dir.rglob("*.md"):
            # Skip template files
            if any(x in str(md_file) for x in ['TEMPLATE', 'GUIDE', 'STYLE']):
                continue
                
            relative_path = md_file.relative_to(self.docs_dir)
            file_map[str(relative_path)] = md_file
            
            # Also map without .md extension
            file_map[str(relative_path).replace('.md', '')] = md_file
            
            # Map just the filename
            file_map[md_file.name] = md_file
            
        return file_map
    
    def extract_links(self, file_path):
        """Extract all markdown links from a file"""
        links = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all markdown links
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for match in re.finditer(pattern, content):
                link_text = match.group(1)
                link_url = match.group(2)
                
                # Skip external links
                if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                    continue
                    
                links.append({
                    'text': link_text,
                    'url': link_url,
                    'full_match': match.group(0),
                    'start': match.start(),
                    'end': match.end()
                })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
        return links
    
    def fix_link(self, link_url, from_file):
        """Attempt to fix a broken link"""
        # Remove any anchors for file lookup
        base_url = link_url.split('#')[0]
        anchor = '#' + link_url.split('#')[1] if '#' in link_url else ''
        
        # Try various fixes
        fixes = [
            # Try as-is
            base_url,
            # Add .md extension
            base_url + '.md' if not base_url.endswith('.md') else base_url,
            # Remove .md extension
            base_url.replace('.md', '') if base_url.endswith('.md') else base_url,
            # Try with index.md
            os.path.join(base_url, 'index.md'),
            # Try parent directory
            os.path.join('..', base_url),
            # Try from root
            base_url.lstrip('/'),
        ]
        
        file_map = self.scan_all_files()
        from_dir = Path(from_file).parent
        
        for fix in fixes:
            # Try relative to current file
            if from_dir != Path('.'):
                relative_path = from_dir / fix
                clean_path = os.path.normpath(relative_path)
                if clean_path in file_map:
                    return self.calculate_relative_path(from_file, file_map[clean_path]) + anchor
            
            # Try from docs root
            if fix in file_map:
                return self.calculate_relative_path(from_file, file_map[fix]) + anchor
        
        # Special case fixes
        if 'sharding' in base_url and 'consistent-hashing' in link_url:
            return '../patterns/sharding.md#consistent-hashing'
        
        if 'fortnite-game' in base_url:
            return '#' if anchor else 'fortnite-game.md'
            
        if 'spacex-control' in base_url:
            return '#' if anchor else 'spacex-control.md'
            
        return None
    
    def calculate_relative_path(self, from_file, to_file):
        """Calculate relative path between two files"""
        from_path = Path(from_file).parent
        to_path = Path(to_file)
        
        try:
            relative = os.path.relpath(to_path, from_path)
            # Convert to forward slashes
            return relative.replace('\\', '/')
        except:
            return str(to_path)
    
    def fix_file(self, file_path):
        """Fix all broken links in a single file"""
        links = self.extract_links(file_path)
        if not links:
            return
        
        file_map = self.scan_all_files()
        relative_path = file_path.relative_to(self.docs_dir)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        replacements = []
        
        for link in links:
            link_url = link['url']
            
            # Check if link is broken
            if link_url.startswith('/'):
                # Absolute path from docs root
                target = link_url.lstrip('/').split('#')[0]
            else:
                # Relative path
                from_dir = Path(relative_path).parent
                target = os.path.normpath(from_dir / link_url.split('#')[0])
            
            # Check if target exists
            if target not in file_map and not link_url.startswith('#'):
                # Broken link - try to fix
                fixed_url = self.fix_link(link_url, relative_path)
                
                if fixed_url:
                    replacements.append({
                        'old': link['full_match'],
                        'new': f"[{link['text']}]({fixed_url})"
                    })
                    self.fixed_count += 1
                    print(f"  Fixed: {link_url} → {fixed_url}")
                else:
                    self.broken_links[str(relative_path)].append(link_url)
                    print(f"  Still broken: {link_url}")
        
        # Apply replacements
        if replacements:
            for r in replacements:
                content = content.replace(r['old'], r['new'])
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Updated {relative_path} with {len(replacements)} fixes")
    
    def fix_all(self):
        """Fix broken links in all files"""
        print("🔧 Fixing broken links in all documentation files...")
        
        for md_file in self.docs_dir.rglob("*.md"):
            # Skip templates
            if any(x in str(md_file) for x in ['TEMPLATE', 'GUIDE', 'STYLE']):
                continue
            
            print(f"\nChecking {md_file.relative_to(self.docs_dir)}...")
            self.fix_file(md_file)
        
        print(f"\n✅ Fixed {self.fixed_count} broken links")
        
        if self.broken_links:
            print(f"\n❌ Still broken ({len(self.broken_links)} files):")
            for file, links in self.broken_links.items():
                print(f"\n{file}:")
                for link in links:
                    print(f"  - {link}")
        
        # Save report
        with open("broken_links_report.txt", "w") as f:
            f.write(f"Fixed {self.fixed_count} links\n\n")
            if self.broken_links:
                f.write("Still broken:\n")
                for file, links in self.broken_links.items():
                    f.write(f"\n{file}:\n")
                    for link in links:
                        f.write(f"  - {link}\n")


if __name__ == "__main__":
    fixer = LinkFixer()
    fixer.fix_all()
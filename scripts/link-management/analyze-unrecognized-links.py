#!/usr/bin/env python3
"""Analyze unrecognized relative links to understand what's missing."""

import re
from pathlib import Path
from collections import defaultdict
import json

class UnrecognizedLinkAnalyzer:
    def __init__(self, docs_dir: Path = Path("docs")):
        self.docs_dir = docs_dir
        self.unrecognized_links = defaultdict(list)
        self.link_patterns = defaultdict(int)
        
    def extract_links_from_file(self, file_path: Path):
        """Extract all relative links from a markdown file."""
        try:
            content = file_path.read_text()
            
            # Find all markdown links [text](path)
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            
            for match in re.finditer(link_pattern, content):
                link_text = match.group(1)
                link_path = match.group(2)
                
                # Skip absolute links, anchors, and external URLs
                if link_path.startswith('/') or link_path.startswith('#') or '://' in link_path:
                    continue
                    
                # Check if the linked file exists
                if not self.check_link_exists(file_path, link_path):
                    self.unrecognized_links[str(file_path.relative_to(self.docs_dir))].append({
                        'text': link_text,
                        'path': link_path,
                        'line': content[:match.start()].count('\n') + 1
                    })
                    
                    # Categorize the type of missing link
                    self.categorize_link(link_path)
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    def check_link_exists(self, source_file: Path, link_path: str) -> bool:
        """Check if a linked file exists relative to the source file."""
        # Remove any anchors
        link_path = link_path.split('#')[0]
        
        if not link_path:
            return True  # Just an anchor, that's fine
            
        # Calculate the target path
        source_dir = source_file.parent
        
        # Handle different link formats
        if link_path.endswith('/'):
            # Directory link - check for index.md
            target = source_dir / link_path / "index.md"
        else:
            # File link - add .md if not present
            if not link_path.endswith('.md'):
                target = source_dir / f"{link_path}.md"
            else:
                target = source_dir / link_path
                
        # Resolve the path and check existence
        try:
            target = target.resolve()
            return target.exists()
        except:
            return False
            
    def categorize_link(self, link_path: str):
        """Categorize the type of missing link."""
        if 'implementation-playbooks' in link_path:
            self.link_patterns['Implementation Playbooks'] += 1
        elif 'case-studies' in link_path:
            self.link_patterns['Case Studies'] += 1
        elif 'guides/' in link_path:
            self.link_patterns['Guides'] += 1
        elif 'tools/' in link_path:
            self.link_patterns['Tools'] += 1
        elif 'pattern-library' in link_path:
            self.link_patterns['Pattern Library'] += 1
        elif '.md' not in link_path and link_path.endswith('/'):
            self.link_patterns['Directory Links'] += 1
        else:
            self.link_patterns['Other'] += 1
            
    def analyze_all_files(self):
        """Analyze all markdown files for unrecognized links."""
        print("🔍 ANALYZING UNRECOGNIZED LINKS...")
        print("="*60)
        
        for md_file in self.docs_dir.glob("**/*.md"):
            self.extract_links_from_file(md_file)
            
    def generate_report(self):
        """Generate a detailed report of findings."""
        total_unrecognized = sum(len(links) for links in self.unrecognized_links.values())
        
        print(f"\n📊 Summary:")
        print(f"  - Files with unrecognized links: {len(self.unrecognized_links)}")
        print(f"  - Total unrecognized links: {total_unrecognized}")
        
        print(f"\n📈 Link Categories:")
        for category, count in sorted(self.link_patterns.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_unrecognized * 100) if total_unrecognized > 0 else 0
            print(f"  - {category}: {count} ({percentage:.1f}%)")
            
        # Show sample problematic files
        print(f"\n🔴 Top Files with Most Unrecognized Links:")
        sorted_files = sorted(self.unrecognized_links.items(), 
                            key=lambda x: len(x[1]), reverse=True)[:10]
        
        for file_path, links in sorted_files:
            print(f"\n  {file_path} ({len(links)} broken links):")
            for link in links[:3]:
                print(f"    - Line {link['line']}: [{link['text']}]({link['path']})")
            if len(links) > 3:
                print(f"    ... and {len(links) - 3} more")
                
        # Write detailed JSON report
        with open("UNRECOGNIZED_LINKS_REPORT.json", "w") as f:
            json.dump(dict(self.unrecognized_links), f, indent=2)
            
        print(f"\n📄 Detailed report written to UNRECOGNIZED_LINKS_REPORT.json")
        
        # Suggest fixes
        self.suggest_fixes()
        
    def suggest_fixes(self):
        """Suggest fixes for common patterns."""
        print(f"\n💡 Suggested Fixes:")
        
        if self.link_patterns.get('Implementation Playbooks', 0) > 0:
            print("\n1. Missing Implementation Playbooks:")
            print("   - These appear to be planned but not created")
            print("   - Either create the files or remove the links")
            
        if self.link_patterns.get('Directory Links', 0) > 0:
            print("\n2. Directory Links Missing index.md:")
            print("   - Many links point to directories without index.md")
            print("   - Add index.md files to these directories")
            
        if self.link_patterns.get('Guides', 0) > 0:
            print("\n3. Missing Guide Files:")
            print("   - Excellence guides referenced but not created")
            print("   - Create guide files in excellence/guides/")

def main():
    analyzer = UnrecognizedLinkAnalyzer()
    analyzer.analyze_all_files()
    analyzer.generate_report()

if __name__ == "__main__":
    main()
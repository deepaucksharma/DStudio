#!/usr/bin/env python3
"""
Comprehensive Link Analysis for DStudio Documentation
Analyzes all markdown files and identifies link issues with specific fixes
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
import sys

class LinkAnalyzer:
    def __init__(self, base_dir="docs"):
        self.base_dir = Path(base_dir)
        self.all_files = set()
        self.issues = defaultdict(list)
        self.link_patterns = {
            'markdown': re.compile(r'\[([^\]]*)\]\(([^)]+)\)'),
            'reference': re.compile(r'\[([^\]]*)\]\[([^\]]+)\]'),
            'definition': re.compile(r'^\[([^\]]+)\]:\s*(.+)$', re.MULTILINE),
        }
        self.stats = {
            'total_files': 0,
            'total_links': 0,
            'broken_internal': 0,
            'broken_external': 0,
            'malformed': 0,
            'navigation_issues': 0,
        }
        
    def find_all_markdown_files(self):
        """Find all markdown files in the docs directory"""
        for path in self.base_dir.rglob("*.md"):
            self.all_files.add(path.relative_to(self.base_dir))
        self.stats['total_files'] = len(self.all_files)
        
    def normalize_path(self, from_file, link):
        """Normalize a relative link to an absolute path"""
        # Remove anchor if present
        if '#' in link:
            link = link.split('#')[0]
            
        # Skip external links
        if link.startswith(('http://', 'https://', 'mailto:', 'ftp://')):
            return None
            
        # Handle absolute paths
        if link.startswith('/'):
            # Absolute from docs root
            return Path(link[1:])
            
        # Handle relative paths
        from_dir = from_file.parent
        
        # Clean up the link
        link = link.strip()
        
        try:
            # Resolve the path
            if link.startswith('../'):
                # Going up directories
                resolved = (from_dir / link).resolve().relative_to(self.base_dir.resolve())
            elif link.startswith('./'):
                # Current directory
                resolved = from_dir / link[2:]
            else:
                # Relative to current directory
                resolved = from_dir / link
                
            return resolved
        except Exception as e:
            return None
            
    def check_link(self, from_file, link, line_num):
        """Check if a link is valid"""
        # Skip external links for now
        if link.startswith(('http://', 'https://', 'mailto:', 'ftp://')):
            return True
            
        # Handle anchors
        anchor = None
        if '#' in link:
            parts = link.split('#', 1)
            link = parts[0]
            anchor = parts[1] if len(parts) > 1 else None
            
        # Empty link means same page anchor
        if not link and anchor:
            return True
            
        # Normalize the path
        target_path = self.normalize_path(from_file, link)
        
        if target_path is None:
            self.issues[from_file].append({
                'type': 'malformed',
                'link': link,
                'line': line_num,
                'message': 'Could not resolve path'
            })
            self.stats['malformed'] += 1
            return False
            
        # Check if target exists
        if target_path not in self.all_files:
            # Try adding .md extension
            md_path = Path(str(target_path) + '.md')
            if md_path not in self.all_files:
                # Try without .md if it had one
                if str(target_path).endswith('.md'):
                    no_md_path = Path(str(target_path)[:-3])
                    if no_md_path not in self.all_files:
                        self.issues[from_file].append({
                            'type': 'broken_internal',
                            'link': link,
                            'line': line_num,
                            'target': str(target_path),
                            'suggestion': self.find_similar_file(target_path)
                        })
                        self.stats['broken_internal'] += 1
                        return False
                else:
                    self.issues[from_file].append({
                        'type': 'broken_internal',
                        'link': link,
                        'line': line_num,
                        'target': str(target_path),
                        'suggestion': self.find_similar_file(target_path)
                    })
                    self.stats['broken_internal'] += 1
                    return False
                    
        return True
        
    def find_similar_file(self, target_path):
        """Find similar files that might be the intended target"""
        target_name = target_path.name
        target_parts = target_path.parts
        
        suggestions = []
        
        for file in self.all_files:
            # Check if filename is similar
            if file.name == target_name:
                suggestions.append(str(file))
                
            # Check if it's in a similar directory structure
            if len(file.parts) == len(target_parts):
                matching_parts = sum(1 for a, b in zip(file.parts, target_parts) if a == b)
                if matching_parts >= len(target_parts) - 1:
                    suggestions.append(str(file))
                    
        return suggestions[:3]  # Return top 3 suggestions
        
    def analyze_file(self, file_path):
        """Analyze all links in a single file"""
        full_path = self.base_dir / file_path
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                
            # Find all markdown links
            for match in self.link_patterns['markdown'].finditer(content):
                link = match.group(2)
                line_num = content[:match.start()].count('\n') + 1
                self.stats['total_links'] += 1
                self.check_link(file_path, link, line_num)
                
            # Find reference-style links
            definitions = {}
            for match in self.link_patterns['definition'].finditer(content):
                ref_name = match.group(1)
                ref_url = match.group(2)
                definitions[ref_name] = ref_url
                
            for match in self.link_patterns['reference'].finditer(content):
                ref_name = match.group(2)
                if ref_name in definitions:
                    link = definitions[ref_name]
                    line_num = content[:match.start()].count('\n') + 1
                    self.stats['total_links'] += 1
                    self.check_link(file_path, link, line_num)
                    
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
    def analyze_navigation(self):
        """Analyze mkdocs.yml navigation for issues"""
        mkdocs_path = Path("mkdocs.yml")
        if not mkdocs_path.exists():
            return
            
        try:
            import yaml
            with open(mkdocs_path, 'r') as f:
                config = yaml.safe_load(f)
                
            nav_files = self.extract_nav_files(config.get('nav', []))
            
            # Check if all nav files exist
            for nav_file in nav_files:
                nav_path = Path(nav_file)
                if nav_path not in self.all_files:
                    self.issues['mkdocs.yml'].append({
                        'type': 'navigation',
                        'file': nav_file,
                        'message': 'File in navigation does not exist'
                    })
                    self.stats['navigation_issues'] += 1
                    
            # Check for orphaned files (in docs but not in nav)
            nav_set = set(nav_files)
            for file in self.all_files:
                if str(file) not in nav_set and not str(file).startswith(('patterns/', 'company-specific/')):
                    # Some directories might be intentionally excluded
                    if not any(part.startswith('.') for part in file.parts):
                        print(f"Warning: {file} not in navigation")
                        
        except ImportError:
            print("PyYAML not installed, skipping navigation analysis")
        except Exception as e:
            print(f"Error analyzing navigation: {e}")
            
    def extract_nav_files(self, nav, prefix=""):
        """Extract all file paths from navigation structure"""
        files = []
        
        if isinstance(nav, list):
            for item in nav:
                files.extend(self.extract_nav_files(item, prefix))
        elif isinstance(nav, dict):
            for key, value in nav.items():
                if isinstance(value, str):
                    # This is a file reference
                    files.append(value)
                else:
                    # This is a nested structure
                    files.extend(self.extract_nav_files(value, prefix))
                    
        return files
        
    def generate_fixes(self):
        """Generate specific fixes for each issue"""
        fixes = []
        
        for file, file_issues in self.issues.items():
            if file == 'mkdocs.yml':
                continue
                
            for issue in file_issues:
                if issue['type'] == 'broken_internal':
                    fix = {
                        'file': str(file),
                        'line': issue['line'],
                        'old_link': issue['link'],
                        'issue': f"Broken link to {issue['target']}",
                    }
                    
                    # Determine the correct fix
                    suggestions = issue.get('suggestion', [])
                    if suggestions:
                        # Calculate relative path from current file to suggestion
                        from_path = Path(file)
                        to_path = Path(suggestions[0])
                        
                        # Calculate relative path
                        try:
                            common = os.path.commonpath([from_path.parent, to_path.parent])
                            from_rel = from_path.parent.relative_to(common)
                            to_rel = to_path.relative_to(common)
                            
                            # Build the relative path
                            ups = len(from_rel.parts)
                            if ups > 0:
                                new_link = '../' * ups + str(to_rel)
                            else:
                                new_link = str(to_rel)
                                
                            fix['new_link'] = new_link
                            fix['suggestion'] = suggestions[0]
                        except:
                            fix['new_link'] = suggestions[0]
                            
                    fixes.append(fix)
                    
        return fixes
        
    def run_analysis(self):
        """Run the complete analysis"""
        print("Finding all markdown files...")
        self.find_all_markdown_files()
        print(f"Found {self.stats['total_files']} files")
        
        print("\nAnalyzing links in all files...")
        for i, file in enumerate(self.all_files, 1):
            if i % 50 == 0:
                print(f"Progress: {i}/{self.stats['total_files']}")
            self.analyze_file(file)
            
        print("\nAnalyzing navigation structure...")
        self.analyze_navigation()
        
        print("\nGenerating fixes...")
        fixes = self.generate_fixes()
        
        return {
            'stats': self.stats,
            'issues': {str(k): v for k, v in self.issues.items()},
            'fixes': fixes
        }
        
    def print_summary(self, results):
        """Print a summary of the analysis"""
        stats = results['stats']
        
        print("\n" + "=" * 80)
        print("LINK ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Total files analyzed: {stats['total_files']}")
        print(f"Total links found: {stats['total_links']}")
        print(f"Broken internal links: {stats['broken_internal']}")
        print(f"Malformed links: {stats['malformed']}")
        print(f"Navigation issues: {stats['navigation_issues']}")
        
        print("\n" + "=" * 80)
        print("TOP FILES WITH ISSUES")
        print("=" * 80)
        
        # Sort files by number of issues
        file_issue_counts = [(file, len(issues)) for file, issues in results['issues'].items()]
        file_issue_counts.sort(key=lambda x: x[1], reverse=True)
        
        for file, count in file_issue_counts[:10]:
            print(f"{file}: {count} issues")
            
        print("\n" + "=" * 80)
        print("SAMPLE FIXES NEEDED")
        print("=" * 80)
        
        for fix in results['fixes'][:20]:
            print(f"\nFile: {fix['file']} (line {fix['line']})")
            print(f"  Issue: {fix['issue']}")
            print(f"  Current: {fix['old_link']}")
            if 'new_link' in fix:
                print(f"  Fix to: {fix['new_link']}")
                
        # Save full results to file
        with open('link_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\nFull results saved to link_analysis_results.json")
        print(f"Total fixes needed: {len(results['fixes'])}")
        
        return stats['broken_internal'] + stats['malformed'] + stats['navigation_issues']

def main():
    analyzer = LinkAnalyzer()
    results = analyzer.run_analysis()
    total_issues = analyzer.print_summary(results)
    
    # Return non-zero exit code if there are issues
    sys.exit(1 if total_issues > 0 else 0)

if __name__ == "__main__":
    main()
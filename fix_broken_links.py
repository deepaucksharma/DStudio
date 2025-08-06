#!/usr/bin/env python3
"""
Comprehensive broken link fixer for DStudio documentation.
This script analyzes and fixes broken internal links by:
1. Reading link_analysis_results.json
2. Categorizing different types of broken links
3. Applying appropriate fixes for each category
4. Updating files using proper path resolution
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set

class BrokenLinkFixer:
    def __init__(self, base_dir: str, analysis_file: str):
        self.base_dir = Path(base_dir)
        self.analysis_file = analysis_file
        self.results = {
            'files_processed': 0,
            'links_fixed': 0,
            'fix_types': defaultdict(int),
            'files_modified': [],
            'errors': []
        }
        
    def load_analysis_results(self) -> Dict:
        """Load the link analysis results"""
        try:
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading analysis file: {e}")
            return {}
    
    def find_actual_file(self, target_path: str, source_file_dir: Path) -> str:
        """Find the actual file that a broken link should point to"""
        # Remove leading dots and slashes
        clean_target = target_path.lstrip('./')
        
        # Common patterns to try
        patterns_to_try = [
            f"{clean_target}",
            f"{clean_target}.md",
            f"{clean_target}/index.md",
            f"{os.path.splitext(clean_target)[0]}.md",
        ]
        
        # Try relative to source file
        for pattern in patterns_to_try:
            full_path = source_file_dir / pattern
            if full_path.exists():
                return str(pattern)
        
        # Try relative to docs root
        docs_root = self.base_dir / "docs"
        for pattern in patterns_to_try:
            full_path = docs_root / pattern
            if full_path.exists():
                # Calculate relative path from source to target
                try:
                    rel_path = os.path.relpath(str(full_path), str(source_file_dir))
                    return rel_path
                except ValueError:
                    continue
        
        return None
    
    def categorize_link_issues(self, issues: Dict) -> Dict:
        """Categorize different types of link issues"""
        categorized = {
            'missing_extension': [],
            'missing_index': [],
            'wrong_path': [],
            'malformed_relative': [],
            'other': []
        }
        
        for file_path, file_issues in issues.items():
            if file_path == 'stats':
                continue
                
            for issue in file_issues:
                link = issue.get('link', '')
                issue_type = issue.get('type', '')
                
                # Skip if not a broken internal link or malformed link we can fix
                if issue_type not in ['broken_internal', 'malformed']:
                    continue
                    
                # Categorize the issue
                if link.endswith('/') or (not link.endswith('.md') and not link.endswith('.html')):
                    if link.endswith('/'):
                        categorized['missing_index'].append((file_path, issue))
                    else:
                        categorized['missing_extension'].append((file_path, issue))
                elif '../' in link or './' in link:
                    categorized['malformed_relative'].append((file_path, issue))
                else:
                    categorized['other'].append((file_path, issue))
        
        return categorized
    
    def fix_link_in_file(self, file_path: str, old_link: str, new_link: str, line_num: int) -> bool:
        """Fix a specific link in a file"""
        try:
            full_path = self.base_dir / file_path
            if not full_path.exists():
                print(f"Source file does not exist: {full_path}")
                return False
            
            # Read the file
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_num > len(lines):
                print(f"Line number {line_num} exceeds file length in {file_path}")
                return False
            
            # Get the line (line_num is 1-based)
            line = lines[line_num - 1]
            
            # Look for markdown link patterns
            markdown_link_pattern = rf'\[([^\]]*)\]\({re.escape(old_link)}\)'
            if re.search(markdown_link_pattern, line):
                new_line = re.sub(markdown_link_pattern, rf'[\1]({new_link})', line)
                lines[line_num - 1] = new_line
                
                # Write back to file
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                return True
            else:
                # Try direct replacement if markdown pattern doesn't match
                if old_link in line:
                    new_line = line.replace(old_link, new_link)
                    lines[line_num - 1] = new_line
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    return True
        
        except Exception as e:
            print(f"Error fixing link in {file_path}: {e}")
            return False
        
        return False
    
    def fix_missing_extensions(self, issues: List[Tuple]) -> int:
        """Fix links missing .md extensions"""
        fixes = 0
        for file_path, issue in issues:
            old_link = issue['link']
            line_num = issue['line']
            
            # Skip if already has extension
            if old_link.endswith('.md') or old_link.endswith('.html'):
                continue
            
            source_dir = (self.base_dir / file_path).parent
            new_link = self.find_actual_file(old_link, source_dir)
            
            if new_link and new_link != old_link:
                if self.fix_link_in_file(file_path, old_link, new_link, line_num):
                    fixes += 1
                    self.results['fix_types']['missing_extension'] += 1
                    print(f"Fixed missing extension: {file_path}:{line_num} {old_link} -> {new_link}")
        
        return fixes
    
    def fix_missing_index(self, issues: List[Tuple]) -> int:
        """Fix links ending with / that should point to index.md"""
        fixes = 0
        for file_path, issue in issues:
            old_link = issue['link']
            line_num = issue['line']
            
            if not old_link.endswith('/'):
                continue
            
            # Try adding index.md
            potential_new_link = old_link + 'index.md'
            source_dir = (self.base_dir / file_path).parent
            
            # Check if index.md exists at this path
            actual_link = self.find_actual_file(old_link.rstrip('/'), source_dir)
            
            if actual_link:
                if self.fix_link_in_file(file_path, old_link, actual_link, line_num):
                    fixes += 1
                    self.results['fix_types']['missing_index'] += 1
                    print(f"Fixed missing index: {file_path}:{line_num} {old_link} -> {actual_link}")
        
        return fixes
    
    def fix_malformed_relative(self, issues: List[Tuple]) -> int:
        """Fix malformed relative path links"""
        fixes = 0
        for file_path, issue in issues:
            old_link = issue['link']
            line_num = issue['line']
            
            source_dir = (self.base_dir / file_path).parent
            new_link = self.find_actual_file(old_link, source_dir)
            
            if new_link and new_link != old_link:
                if self.fix_link_in_file(file_path, old_link, new_link, line_num):
                    fixes += 1
                    self.results['fix_types']['malformed_relative'] += 1
                    print(f"Fixed malformed relative: {file_path}:{line_num} {old_link} -> {new_link}")
        
        return fixes
    
    def fix_other_issues(self, issues: List[Tuple]) -> int:
        """Fix other types of link issues"""
        fixes = 0
        for file_path, issue in issues:
            old_link = issue['link']
            line_num = issue['line']
            
            source_dir = (self.base_dir / file_path).parent
            new_link = self.find_actual_file(old_link, source_dir)
            
            if new_link and new_link != old_link:
                if self.fix_link_in_file(file_path, old_link, new_link, line_num):
                    fixes += 1
                    self.results['fix_types']['other'] += 1
                    print(f"Fixed other issue: {file_path}:{line_num} {old_link} -> {new_link}")
        
        return fixes
    
    def run_fixes(self):
        """Run all the fixes"""
        print("Loading link analysis results...")
        analysis_data = self.load_analysis_results()
        
        if not analysis_data or 'issues' not in analysis_data:
            print("No analysis data found")
            return
        
        print("Categorizing link issues...")
        categorized = self.categorize_link_issues(analysis_data['issues'])
        
        print(f"Found issues:")
        for category, issues in categorized.items():
            print(f"  {category}: {len(issues)}")
        
        # Track unique files that will be modified
        files_to_modify = set()
        for category_issues in categorized.values():
            for file_path, _ in category_issues:
                files_to_modify.add(file_path)
        
        print(f"\nProcessing {len(files_to_modify)} files...")
        
        # Fix each category
        total_fixes = 0
        
        print("Fixing missing extensions...")
        total_fixes += self.fix_missing_extensions(categorized['missing_extension'])
        
        print("Fixing missing index files...")
        total_fixes += self.fix_missing_index(categorized['missing_index'])
        
        print("Fixing malformed relative paths...")
        total_fixes += self.fix_malformed_relative(categorized['malformed_relative'])
        
        print("Fixing other issues...")
        total_fixes += self.fix_other_issues(categorized['other'])
        
        # Update results
        self.results['files_processed'] = len(files_to_modify)
        self.results['links_fixed'] = total_fixes
        self.results['files_modified'] = list(files_to_modify)
        
        print(f"\nSummary:")
        print(f"Files processed: {self.results['files_processed']}")
        print(f"Links fixed: {self.results['links_fixed']}")
        print(f"Fix types:")
        for fix_type, count in self.results['fix_types'].items():
            print(f"  {fix_type}: {count}")
        
        return self.results

if __name__ == "__main__":
    fixer = BrokenLinkFixer("/home/deepak/DStudio", "/home/deepak/DStudio/link_analysis_results.json")
    results = fixer.run_fixes()
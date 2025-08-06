#!/usr/bin/env python3
"""
Comprehensive Link Fixer for DStudio Documentation
Fixes all identified link issues systematically
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

class ComprehensiveLinkFixer:
    def __init__(self):
        self.base_dir = Path("docs")
        self.fixes_applied = 0
        self.files_modified = set()
        
        # Load the analysis results
        with open('link_analysis_results.json', 'r') as f:
            self.analysis = json.load(f)
            
        # Pattern fixes for common issues
        self.pattern_fixes = {
            # Fix malformed external links (missing second slash)
            r'https:/([^/])': r'https://\1',
            r'http:/([^/])': r'http://\1',
            
            # Fix empty links in pattern library
            r'\[([^\]]+)\]\(\)': r'\1',  # Remove empty link markdown
            
            # Fix broken absolute paths
            r'/architects-handbook/(.+?)(?:\.md)?(?=/|$|\))': r'../architects-handbook/\1.md',
            r'/pattern-library/(.+?)(?:\.md)?(?=/|$|\))': r'../pattern-library/\1.md',
            r'/core-principles/(.+?)(?:\.md)?(?=/|$|\))': r'../core-principles/\1.md',
            
            # Fix double slashes in paths
            r'//': r'/',
            
            # Fix links ending with /index.md/index.md
            r'/index\.md/index\.md': r'/index.md',
            
            # Fix redundant ../../ in paths
            r'(\.\./){4,}': r'../../',
        }
        
        # Specific file mappings for moved/renamed files
        self.file_mappings = {
            'implementation-playbooks/': 'implementation-playbooks/index.md',
            'quantitative/littles-law/': 'quantitative-analysis/littles-law.md',
            'quantitative/capacity-planning/': 'quantitative-analysis/capacity-planning.md',
            'quantitative/universal-scalability/': 'quantitative-analysis/universal-scalability.md',
            'core-principles/core-principles/': 'core-principles/',
            'sre-principles/': 'sre-practices.md',
            'toil-reduction/': 'knowledge-management.md',
            'capacity-management/': 'capacity-calculator.md',
            'release-engineering/': 'incident-response.md',
            'postmortem-culture/': 'blameless-postmortems.md',
            'runbook-development/': 'runbooks-playbooks.md',
            'war-room-protocols/': 'incident-response.md',
            'on-call-philosophy/': 'oncall-culture.md',
            'escalation-policies/': 'incident-response.md',
            'alert-fatigue/': 'observability-stacks.md',
            'handoff-procedures/': 'oncall-culture.md',
            'observability-strategy/': 'observability-stacks.md',
            'dashboard-design/': 'observability-stacks.md',
            'alert-design/': 'observability-stacks.md',
            'debugging-guide/': 'incident-response.md',
        }
        
    def fix_link(self, link, from_file):
        """Fix a single link based on its type and context"""
        original_link = link
        
        # Apply pattern fixes
        for pattern, replacement in self.pattern_fixes.items():
            link = re.sub(pattern, replacement, link)
            
        # Handle specific file mappings
        for old_path, new_path in self.file_mappings.items():
            if old_path in link:
                link = link.replace(old_path, new_path)
                
        # Fix relative paths based on file location
        if link.startswith('../') and from_file:
            # Calculate correct relative path
            from_path = Path(from_file)
            depth = len(from_path.parts) - 1
            
            # Adjust the number of ../ based on file depth
            if 'pattern-library' in link and 'pattern-library' in str(from_path):
                # Same directory structure
                link = re.sub(r'^(\.\./)+', '', link)
            elif depth > 2:
                # Deep nesting requires more ../
                link = '../' * (depth - 1) + link.lstrip('../')
                
        return link if link != original_link else None
        
    def fix_file(self, file_path):
        """Fix all links in a single file"""
        full_path = self.base_dir / file_path
        
        if not full_path.exists():
            return 0
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        fixes_in_file = 0
        
        # Fix markdown links [text](url)
        def replace_link(match):
            nonlocal fixes_in_file
            text = match.group(1)
            link = match.group(2)
            
            # Skip external links that are already correct
            if link.startswith(('https://', 'http://', 'mailto:', '#')):
                return match.group(0)
                
            fixed_link = self.fix_link(link, file_path)
            if fixed_link:
                fixes_in_file += 1
                return f'[{text}]({fixed_link})'
            return match.group(0)
            
        content = re.sub(r'\[([^\]]*)\]\(([^)]+)\)', replace_link, content)
        
        # Fix malformed external links globally
        content = re.sub(r'https:/([^/])', r'https://\1', content)
        content = re.sub(r'http:/([^/])', r'http://\1', content)
        
        # Fix empty links
        content = re.sub(r'\[([^\]]+)\]\(\)', r'\1', content)
        
        # Write back if changed
        if content != original_content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.files_modified.add(str(file_path))
            self.fixes_applied += fixes_in_file
            return fixes_in_file
            
        return 0
        
    def fix_specific_files(self):
        """Fix specific files with known issues"""
        specific_fixes = {
            'architects-handbook/human-factors/index.md': {
                'sre-principles/': 'sre-practices.md',
                'toil-reduction/': 'knowledge-management.md',
                'capacity-management/': '../tools/capacity-calculator.md',
                'release-engineering/': 'incident-response.md',
                'postmortem-culture/': 'blameless-postmortems.md',
                'runbook-development/': 'runbooks-playbooks.md',
                'war-room-protocols/': 'incident-response.md',
                'on-call-philosophy/': 'oncall-culture.md',
                'escalation-policies/': 'incident-response.md',
                'alert-fatigue/': 'observability-stacks.md',
                'handoff-procedures/': 'oncall-culture.md',
                'observability-strategy/': 'observability-stacks.md',
                'dashboard-design/': 'observability-stacks.md',
                'alert-design/': 'observability-stacks.md',
                'debugging-guide/': 'incident-response.md',
            },
            'architects-handbook/case-studies/index.md': {
                '/architects-handbook/': '',
                'case-studies/': '',
                '../index.md': '../../index.md',
            },
            'pattern-library/cost-optimization/finops.md': {
                r'\[\]\(\)': '',  # Remove empty links
            }
        }
        
        for file_path, replacements in specific_fixes.items():
            full_path = self.base_dir / file_path
            if not full_path.exists():
                continue
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original = content
            for old, new in replacements.items():
                content = re.sub(old, new, content)
                
            if content != original:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_modified.add(file_path)
                
    def run(self):
        """Run the comprehensive fix"""
        print("Starting comprehensive link fix...")
        
        # Fix specific known issues first
        print("Fixing specific file issues...")
        self.fix_specific_files()
        
        # Process all files with issues from the analysis
        print("Processing files from analysis...")
        files_to_fix = set()
        for fix in self.analysis['fixes']:
            files_to_fix.add(fix['file'])
            
        for i, file_path in enumerate(files_to_fix, 1):
            if i % 50 == 0:
                print(f"Progress: {i}/{len(files_to_fix)}")
            self.fix_file(file_path)
            
        # Also process files with high issue counts
        print("Processing high-issue files...")
        for file_path, issues in self.analysis['issues'].items():
            if len(issues) > 10 and file_path != 'mkdocs.yml':
                self.fix_file(Path(file_path))
                
        print(f"\nFix complete!")
        print(f"Files modified: {len(self.files_modified)}")
        print(f"Total fixes applied: {self.fixes_applied}")
        
        # List top modified files
        if self.files_modified:
            print("\nTop modified files:")
            for file in list(self.files_modified)[:10]:
                print(f"  - {file}")
                
def main():
    fixer = ComprehensiveLinkFixer()
    fixer.run()

if __name__ == "__main__":
    main()
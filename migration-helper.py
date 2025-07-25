#!/usr/bin/env python3
"""
CSS Migration Helper for DStudio
Helps identify and fix CSS issues during migration to unified-system.css
"""

import re
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class CSSMigrationHelper:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.issues_found = []
        
        # Old to new class mappings
        self.class_mappings = {
            'c-card': 'card',
            'feature-card': 'card',
            'pattern-card': 'card',
            'c-card__title': 'card__title',
            'feature-card__title': 'card__title',
            'pattern-card__title': 'card__title',
        }
        
        # Old color variables to new
        self.color_mappings = {
            '--brand-primary': '--color-primary',
            '--brand-secondary': '--color-accent',
            '--brand-primary-light': '--color-primary-light',
            '--brand-primary-dark': '--color-primary-dark',
        }
        
        # Font size mappings
        self.font_mappings = {
            '0.875rem': 'var(--font-size-sm)',
            '1rem': 'var(--font-size-base)',
            '1.1rem': 'var(--font-size-lg)',
            '1.125rem': 'var(--font-size-lg)',
            '1.2rem': 'var(--font-size-xl)',
            '1.25rem': 'var(--font-size-xl)',
            '1.5rem': 'var(--font-size-2xl)',
            '2rem': 'var(--font-size-3xl)',
            '2.5rem': 'var(--font-size-4xl)',
        }
        
        # Spacing mappings
        self.spacing_mappings = {
            '0.25rem': 'var(--space-1)',
            '0.5rem': 'var(--space-2)',
            '0.75rem': 'var(--space-3)',
            '1rem': 'var(--space-4)',
            '1.25rem': 'var(--space-5)',
            '1.5rem': 'var(--space-6)',
            '2rem': 'var(--space-8)',
            '2.5rem': 'var(--space-10)',
            '3rem': 'var(--space-12)',
            '4rem': 'var(--space-16)',
        }
    
    def find_emojis_in_navigation(self, file_path: Path) -> List[Tuple[int, str]]:
        """Find emojis in navigation items"""
        emoji_pattern = re.compile(r'(:[a-z0-9_]+:|[\U0001F000-\U0001F9FF]|🚧|📚|🔍|⚖️|🎯|🔗|🛠️|🎭|👥|📖|📊)')
        issues = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        in_nav_section = False
        for i, line in enumerate(lines):
            if line.strip() == 'nav:':
                in_nav_section = True
            elif in_nav_section and not line.startswith(' ') and not line.startswith('-'):
                in_nav_section = False
                
            if in_nav_section and emoji_pattern.search(line):
                issues.append((i + 1, line.strip()))
                
        return issues
    
    def find_emoji_bullets(self, file_path: Path) -> List[Tuple[int, str]]:
        """Find emoji bullets in markdown files"""
        emoji_bullet_pattern = re.compile(r'^[\s]*[-*]\s*(:[a-z0-9_]+:|[\U0001F000-\U0001F9FF])')
        issues = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if emoji_bullet_pattern.search(line):
                issues.append((i + 1, line.strip()))
                
        return issues
    
    def find_old_css_classes(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """Find old CSS classes that need updating"""
        issues = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        for i, line in enumerate(lines):
            for old_class, new_class in self.class_mappings.items():
                if old_class in line:
                    issues.append((i + 1, old_class, new_class))
                    
        return issues
    
    def find_hard_coded_values(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """Find hard-coded font sizes and spacing"""
        issues = []
        
        if file_path.suffix not in ['.css', '.html', '.md']:
            return issues
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            # Check font sizes
            for old_value, new_value in self.font_mappings.items():
                if f'font-size: {old_value}' in line:
                    issues.append((i + 1, f'font-size: {old_value}', f'font-size: {new_value}'))
                    
            # Check spacing
            for old_value, new_value in self.spacing_mappings.items():
                for prop in ['margin', 'padding', 'gap']:
                    if f'{prop}: {old_value}' in line:
                        issues.append((i + 1, f'{prop}: {old_value}', f'{prop}: {new_value}'))
                        
        return issues
    
    def find_important_declarations(self, file_path: Path) -> List[Tuple[int, str]]:
        """Find !important declarations"""
        if file_path.suffix != '.css':
            return []
            
        issues = []
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if '!important' in line:
                issues.append((i + 1, line.strip()))
                
        return issues
    
    def find_tables_without_responsive(self, file_path: Path) -> List[Tuple[int, str]]:
        """Find tables without responsive class"""
        if file_path.suffix != '.md':
            return []
            
        issues = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find HTML tables
        table_pattern = re.compile(r'<table(?![^>]*class[^>]*responsive-table)', re.IGNORECASE)
        for match in table_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            issues.append((line_num, '<table> without responsive-table class'))
            
        return issues
    
    def analyze_file(self, file_path: Path) -> Dict[str, List]:
        """Analyze a single file for all issues"""
        results = {
            'emoji_bullets': [],
            'old_classes': [],
            'hard_coded_values': [],
            'important_declarations': [],
            'tables_without_responsive': [],
        }
        
        if not file_path.exists():
            return results
            
        try:
            if file_path.suffix == '.md':
                results['emoji_bullets'] = self.find_emoji_bullets(file_path)
                results['tables_without_responsive'] = self.find_tables_without_responsive(file_path)
                results['old_classes'] = self.find_old_css_classes(file_path)
                
            elif file_path.suffix == '.css':
                results['hard_coded_values'] = self.find_hard_coded_values(file_path)
                results['important_declarations'] = self.find_important_declarations(file_path)
                results['old_classes'] = self.find_old_css_classes(file_path)
                
            elif file_path.suffix in ['.html', '.yml', '.yaml']:
                results['old_classes'] = self.find_old_css_classes(file_path)
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return results
    
    def generate_report(self) -> str:
        """Generate migration report"""
        report = ["# CSS Migration Report\n"]
        report.append(f"Analyzed {len(self.issues_found)} files\n")
        
        # Group issues by type
        issue_types = {
            'emoji_bullets': "Emoji Bullets to Remove",
            'old_classes': "Old CSS Classes to Update",
            'hard_coded_values': "Hard-coded Values to Replace",
            'important_declarations': "!important Declarations to Remove",
            'tables_without_responsive': "Tables Missing Responsive Class",
            'navigation_emojis': "Emojis in Navigation",
        }
        
        for issue_type, title in issue_types.items():
            issues = [i for i in self.issues_found if i['type'] == issue_type]
            if issues:
                report.append(f"\n## {title}\n")
                for issue in issues:
                    report.append(f"- **{issue['file']}** (line {issue['line']}): {issue['description']}\n")
                    
        return ''.join(report)
    
    def run_analysis(self):
        """Run analysis on all files"""
        print("Starting CSS migration analysis...")
        
        # Analyze mkdocs.yml for navigation emojis
        mkdocs_file = Path("mkdocs.yml")
        if mkdocs_file.exists():
            nav_emojis = self.find_emojis_in_navigation(mkdocs_file)
            for line_num, line in nav_emojis:
                self.issues_found.append({
                    'type': 'navigation_emojis',
                    'file': 'mkdocs.yml',
                    'line': line_num,
                    'description': line
                })
        
        # Analyze all docs files
        for file_path in self.docs_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.md', '.css', '.html', '.yml']:
                print(f"Analyzing {file_path}...")
                results = self.analyze_file(file_path)
                
                for issue_type, issues in results.items():
                    for issue in issues:
                        self.issues_found.append({
                            'type': issue_type,
                            'file': str(file_path),
                            'line': issue[0],
                            'description': issue[1] if len(issue) == 2 else f"{issue[1]} → {issue[2]}"
                        })
        
        # Generate and save report
        report = self.generate_report()
        with open('CSS_MIGRATION_REPORT.md', 'w') as f:
            f.write(report)
            
        print(f"\nAnalysis complete! Found {len(self.issues_found)} issues.")
        print("Report saved to CSS_MIGRATION_REPORT.md")
        
        # Summary
        print("\nSummary by type:")
        from collections import Counter
        issue_counts = Counter(issue['type'] for issue in self.issues_found)
        for issue_type, count in issue_counts.most_common():
            print(f"  {issue_type}: {count}")


def main():
    helper = CSSMigrationHelper()
    helper.run_analysis()


if __name__ == "__main__":
    main()
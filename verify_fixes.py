#!/usr/bin/env python3
"""
Verification script for DStudio documentation fixes.
Checks file existence, internal links, axiom paths, and pattern navigation.
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple, Set

class DocumentationVerifier:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "docs"
        self.mkdocs_path = self.base_path / "mkdocs.yml"
        self.errors = []
        self.warnings = []
        self.info = []
        
    def load_mkdocs_config(self) -> dict:
        """Load and parse mkdocs.yml configuration."""
        # Use FullLoader to handle custom tags
        with open(self.mkdocs_path, 'r') as f:
            # Read the content and remove problematic tags for navigation parsing
            content = f.read()
            # Simply load as unsafe YAML to handle custom tags
            try:
                return yaml.load(content, Loader=yaml.FullLoader)
            except:
                # If that fails, try removing custom tags
                cleaned_content = re.sub(r'!!python/name:[\w.]+', '', content)
                return yaml.safe_load(cleaned_content)
    
    def extract_nav_files(self, nav_item, files=None) -> Set[str]:
        """Recursively extract all file paths from navigation structure."""
        if files is None:
            files = set()
            
        if isinstance(nav_item, dict):
            for key, value in nav_item.items():
                if isinstance(value, str):
                    files.add(value)
                elif isinstance(value, list):
                    for item in value:
                        self.extract_nav_files(item, files)
                elif isinstance(value, dict):
                    self.extract_nav_files(value, files)
        elif isinstance(nav_item, list):
            for item in nav_item:
                self.extract_nav_files(item, files)
        elif isinstance(nav_item, str):
            files.add(nav_item)
            
        return files
    
    def check_files_exist(self) -> None:
        """Check that all files referenced in mkdocs.yml exist."""
        print("\n=== Checking File Existence ===")
        config = self.load_mkdocs_config()
        nav_files = self.extract_nav_files(config.get('nav', []))
        
        missing_files = []
        for file_path in nav_files:
            full_path = self.docs_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                self.errors.append(f"Missing file: {file_path}")
            else:
                self.info.append(f"✓ File exists: {file_path}")
        
        print(f"Total files in navigation: {len(nav_files)}")
        print(f"Missing files: {len(missing_files)}")
        if missing_files:
            for file in missing_files[:10]:  # Show first 10
                print(f"  ❌ {file}")
            if len(missing_files) > 10:
                print(f"  ... and {len(missing_files) - 10} more")
    
    def extract_markdown_links(self, content: str) -> List[str]:
        """Extract all markdown links from content."""
        # Match [text](link) pattern
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)
        return [match[1] for match in matches if not match[1].startswith(('http://', 'https://', '#'))]
    
    def check_internal_links(self) -> None:
        """Check for broken internal links in all markdown files."""
        print("\n=== Checking Internal Links ===")
        broken_links = defaultdict(list)
        total_links = 0
        
        for md_file in self.docs_path.rglob("*.md"):
            relative_path = md_file.relative_to(self.docs_path)
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                links = self.extract_markdown_links(content)
                total_links += len(links)
                
                for link in links:
                    # Handle anchor links
                    link_path = link.split('#')[0] if '#' in link else link
                    if not link_path:  # Pure anchor link
                        continue
                        
                    # Resolve relative link
                    if link_path.startswith('/'):
                        # Absolute path from docs root
                        target_path = self.docs_path / link_path.lstrip('/')
                    else:
                        # Relative path from current file
                        target_path = md_file.parent / link_path
                    
                    # Normalize and check existence
                    target_path = target_path.resolve()
                    
                    # Handle index.md implicit links
                    if target_path.is_dir():
                        target_path = target_path / "index.md"
                    
                    if not target_path.exists():
                        broken_links[str(relative_path)].append(link)
                        self.errors.append(f"Broken link in {relative_path}: {link}")
                        
            except Exception as e:
                self.warnings.append(f"Error reading {relative_path}: {e}")
        
        print(f"Total internal links found: {total_links}")
        print(f"Files with broken links: {len(broken_links)}")
        
        if broken_links:
            for file, links in list(broken_links.items())[:5]:  # Show first 5 files
                print(f"\n  File: {file}")
                for link in links[:3]:  # Show first 3 broken links per file
                    print(f"    ❌ {link}")
                if len(links) > 3:
                    print(f"    ... and {len(links) - 3} more")
    
    def check_axiom_paths(self) -> None:
        """Check for incorrect axiom reference patterns."""
        print("\n=== Checking Axiom Paths ===")
        incorrect_patterns = [
            (r'/axioms/(\w+)', 'Old axiom path pattern'),
            (r'part1-axioms/axioms/(\w+)', 'Double axioms path'),
            (r'\.\./\.\./axioms/', 'Incorrect relative axiom path'),
        ]
        
        files_with_issues = defaultdict(list)
        
        for md_file in self.docs_path.rglob("*.md"):
            relative_path = md_file.relative_to(self.docs_path)
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern, description in incorrect_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        files_with_issues[str(relative_path)].append({
                            'pattern': pattern,
                            'description': description,
                            'count': len(matches),
                            'examples': matches[:3]
                        })
                        self.warnings.append(f"Incorrect axiom path in {relative_path}: {description}")
                        
            except Exception as e:
                self.warnings.append(f"Error reading {relative_path}: {e}")
        
        print(f"Files with incorrect axiom paths: {len(files_with_issues)}")
        
        if files_with_issues:
            for file, issues in list(files_with_issues.items())[:5]:
                print(f"\n  File: {file}")
                for issue in issues:
                    print(f"    ⚠️  {issue['description']} ({issue['count']} occurrences)")
                    for example in issue['examples']:
                        print(f"        Example: {example}")
    
    def check_pattern_navigation(self) -> None:
        """Verify pattern navigation consistency."""
        print("\n=== Checking Pattern Navigation ===")
        
        patterns_dir = self.docs_path / "patterns"
        if not patterns_dir.exists():
            self.errors.append("Patterns directory not found")
            return
            
        # Expected structure for each pattern
        expected_files = ['index.md', 'examples.md', 'exercises.md']
        pattern_issues = []
        
        # Check each pattern directory
        for pattern_dir in patterns_dir.iterdir():
            if pattern_dir.is_dir() and not pattern_dir.name.startswith('.'):
                missing_files = []
                for expected_file in expected_files:
                    file_path = pattern_dir / expected_file
                    if not file_path.exists():
                        missing_files.append(expected_file)
                
                if missing_files:
                    pattern_issues.append({
                        'pattern': pattern_dir.name,
                        'missing': missing_files
                    })
                    for file in missing_files:
                        self.warnings.append(f"Pattern {pattern_dir.name} missing: {file}")
                
                # Check navigation structure in index.md
                index_path = pattern_dir / "index.md"
                if index_path.exists():
                    with open(index_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for navigation links
                    has_examples_link = 'examples.md' in content or 'Examples' in content
                    has_exercises_link = 'exercises.md' in content or 'Exercises' in content
                    
                    if not has_examples_link:
                        self.warnings.append(f"Pattern {pattern_dir.name}/index.md missing examples navigation")
                    if not has_exercises_link:
                        self.warnings.append(f"Pattern {pattern_dir.name}/index.md missing exercises navigation")
        
        print(f"Patterns with issues: {len(pattern_issues)}")
        if pattern_issues:
            for issue in pattern_issues[:5]:
                print(f"  Pattern: {issue['pattern']}")
                print(f"    Missing: {', '.join(issue['missing'])}")
    
    def check_cross_references(self) -> None:
        """Check cross-references between patterns, axioms, and pillars."""
        print("\n=== Checking Cross-References ===")
        
        # Define expected cross-reference patterns
        cross_ref_patterns = {
            'axiom_refs': r'\[([^\]]*[Aa]xiom[^\]]*)\]\(([^)]+)\)',
            'pillar_refs': r'\[([^\]]*[Pp]illar[^\]]*)\]\(([^)]+)\)',
            'pattern_refs': r'\[([^\]]*[Pp]attern[^\]]*)\]\(([^)]+)\)'
        }
        
        stats = defaultdict(int)
        
        for md_file in self.docs_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for ref_type, pattern in cross_ref_patterns.items():
                    matches = re.findall(pattern, content)
                    stats[ref_type] += len(matches)
                    
            except Exception as e:
                self.warnings.append(f"Error reading {md_file}: {e}")
        
        print("Cross-reference statistics:")
        for ref_type, count in stats.items():
            print(f"  {ref_type}: {count}")
    
    def generate_report(self) -> None:
        """Generate final verification report."""
        print("\n" + "="*60)
        print("FINAL VERIFICATION REPORT")
        print("="*60)
        
        print(f"\n📊 Summary:")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Info messages: {len(self.info)}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for i, error in enumerate(self.errors[:10], 1):
                print(f"  {i}. {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings[:10], 1):
                print(f"  {i}. {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        # Save detailed report
        report_path = self.base_path / "verification_report.txt"
        with open(report_path, 'w') as f:
            f.write("DStudio Documentation Verification Report\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Summary:\n")
            f.write(f"  Total Errors: {len(self.errors)}\n")
            f.write(f"  Total Warnings: {len(self.warnings)}\n")
            f.write(f"  Total Info: {len(self.info)}\n\n")
            
            if self.errors:
                f.write(f"\nErrors:\n")
                for error in self.errors:
                    f.write(f"  - {error}\n")
            
            if self.warnings:
                f.write(f"\nWarnings:\n")
                for warning in self.warnings:
                    f.write(f"  - {warning}\n")
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Overall status
        print("\n" + "="*60)
        if len(self.errors) == 0:
            print("✅ VERIFICATION PASSED - No critical errors found!")
        else:
            print("❌ VERIFICATION FAILED - Critical errors detected!")
        print("="*60)

def main():
    """Run the verification process."""
    base_path = "/Users/deepaksharma/syc/DStudio"
    verifier = DocumentationVerifier(base_path)
    
    print("Starting DStudio Documentation Verification...")
    print(f"Base path: {base_path}")
    
    # Run all checks
    verifier.check_files_exist()
    verifier.check_internal_links()
    verifier.check_axiom_paths()
    verifier.check_pattern_navigation()
    verifier.check_cross_references()
    
    # Generate final report
    verifier.generate_report()

if __name__ == "__main__":
    main()
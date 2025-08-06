#!/usr/bin/env python3
"""
First-principles MkDocs site validator.

Core principle: In MkDocs, everything revolves around mkdocs.yml.
If mkdocs can build successfully with --strict mode, the site is valid.

This validator:
1. Builds MkDocs in strict mode (catches all navigation/link errors)
2. Analyzes the build output for any warnings
3. Cross-references mkdocs.yml with actual file structure
4. Reports all issues in a unified way
"""

import subprocess
import sys
import yaml
import json
from pathlib import Path
import re

class MkDocsValidator:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.mkdocs_config = None
        
    def load_mkdocs_config(self):
        """Load and parse mkdocs.yml"""
        try:
            # Custom YAML loader that ignores MkDocs-specific tags
            class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
                pass
            
            def constructor_undefined(loader, node):
                if isinstance(node, yaml.ScalarNode):
                    return loader.construct_scalar(node)
                elif isinstance(node, yaml.SequenceNode):
                    return loader.construct_sequence(node)
                elif isinstance(node, yaml.MappingNode):
                    return loader.construct_mapping(node)
                return None
            
            SafeLoaderIgnoreUnknown.add_constructor(None, constructor_undefined)
            
            with open('mkdocs.yml', 'r') as f:
                self.mkdocs_config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
            return True
        except Exception as e:
            self.issues.append(f"Failed to parse mkdocs.yml: {e}")
            return False
    
    def run_mkdocs_build(self):
        """Run mkdocs build --strict and capture output"""
        print("🏗️  Running MkDocs build in strict mode...")
        try:
            result = subprocess.run(
                ['mkdocs', 'build', '--strict', '--quiet'],
                capture_output=True,
                text=True
            )
            
            # Parse output for errors and warnings
            if result.returncode != 0:
                # MkDocs strict mode failed - parse the errors
                for line in result.stderr.split('\n'):
                    if line.strip():
                        if 'WARNING' in line:
                            self.warnings.append(line.strip())
                        elif 'ERROR' in line:
                            self.issues.append(line.strip())
                        # Extract specific file/link errors
                        elif 'not found' in line.lower():
                            self.issues.append(f"Missing file: {line.strip()}")
                        elif 'broken link' in line.lower():
                            self.issues.append(f"Broken link: {line.strip()}")
                
                # Also check stdout for additional info
                for line in result.stdout.split('\n'):
                    if 'WARNING' in line and line.strip():
                        self.warnings.append(line.strip())
            
            return result.returncode == 0
            
        except FileNotFoundError:
            self.issues.append("MkDocs not installed. Run: pip install -r requirements.txt")
            return False
        except Exception as e:
            self.issues.append(f"Failed to run MkDocs build: {e}")
            return False
    
    def validate_navigation_files(self):
        """Validate all files referenced in navigation exist"""
        if not self.mkdocs_config:
            return
            
        print("📂 Validating navigation structure...")
        
        def extract_files_from_nav(nav_item, files_set):
            """Recursively extract all file paths from navigation"""
            if isinstance(nav_item, str):
                if nav_item.endswith('.md'):
                    files_set.add(nav_item)
            elif isinstance(nav_item, dict):
                for value in nav_item.values():
                    extract_files_from_nav(value, files_set)
            elif isinstance(nav_item, list):
                for item in nav_item:
                    extract_files_from_nav(item, files_set)
        
        nav_files = set()
        if 'nav' in self.mkdocs_config:
            extract_files_from_nav(self.mkdocs_config['nav'], nav_files)
        
        # Check each file exists
        docs_dir = Path('docs')
        for nav_file in nav_files:
            file_path = docs_dir / nav_file
            if not file_path.exists():
                self.issues.append(f"Navigation references missing file: {nav_file}")
    
    def find_orphaned_files(self):
        """Find markdown files not in navigation"""
        if not self.mkdocs_config:
            return
            
        print("🔍 Finding orphaned files...")
        
        # Get all files from navigation
        def extract_files_from_nav(nav_item, files_set):
            if isinstance(nav_item, str) and nav_item.endswith('.md'):
                files_set.add(nav_item)
            elif isinstance(nav_item, dict):
                for value in nav_item.values():
                    extract_files_from_nav(value, files_set)
            elif isinstance(nav_item, list):
                for item in nav_item:
                    extract_files_from_nav(item, files_set)
        
        nav_files = set()
        if 'nav' in self.mkdocs_config:
            extract_files_from_nav(self.mkdocs_config['nav'], nav_files)
        
        # Find all markdown files
        docs_dir = Path('docs')
        all_files = set()
        for md_file in docs_dir.rglob('*.md'):
            rel_path = str(md_file.relative_to(docs_dir))
            all_files.add(rel_path)
        
        # Find orphaned files
        orphaned = all_files - nav_files
        if orphaned:
            for file in sorted(orphaned):
                self.warnings.append(f"Orphaned file (not in navigation): {file}")
    
    def validate_internal_links(self):
        """Quick validation of internal link patterns"""
        print("🔗 Checking link patterns...")
        
        # Common problematic patterns
        problematic_patterns = [
            (r'/pattern-library/index\.md#', 'Links to pattern-library/index.md# won\'t work after move to /patterns/'),
            (r'\.\./(patterns|pattern-library)/', 'Inconsistent pattern directory references'),
            (r'/core-principles/(axioms|laws)/', 'Mixed axioms/laws references'),
            (r'law[0-9]-\w+', 'Old law naming convention'),
            (r'/part[0-9]-\w+/', 'Old part1/part2 structure references'),
        ]
        
        docs_dir = Path('docs')
        for md_file in docs_dir.rglob('*.md'):
            content = md_file.read_text()
            for pattern, description in problematic_patterns:
                if re.search(pattern, content):
                    self.warnings.append(f"{md_file.relative_to(docs_dir)}: {description}")
    
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*80)
        print("📊 MKDOCS VALIDATION REPORT")
        print("="*80)
        
        if not self.issues and not self.warnings:
            print("\n✅ All validations passed!")
            return 0
        
        if self.issues:
            print(f"\n❌ ERRORS ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  - {issue}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:20]:  # Limit output
                print(f"  - {warning}")
            if len(self.warnings) > 20:
                print(f"  ... and {len(self.warnings) - 20} more")
        
        # Write detailed report
        report = {
            'errors': self.issues,
            'warnings': self.warnings,
            'summary': {
                'total_errors': len(self.issues),
                'total_warnings': len(self.warnings)
            }
        }
        
        with open('mkdocs-validation-report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report written to mkdocs-validation-report.json")
        
        return 1 if self.issues else 0
    
    def run(self):
        """Run all validations"""
        print("🚀 Starting MkDocs validation...\n")
        
        # Load config first
        if not self.load_mkdocs_config():
            return self.generate_report()
        
        # Run MkDocs build - this catches most issues
        build_success = self.run_mkdocs_build()
        
        # Additional validations
        self.validate_navigation_files()
        self.find_orphaned_files()
        self.validate_internal_links()
        
        # Generate report
        return self.generate_report()

def main():
    """Main entry point"""
    validator = MkDocsValidator()
    sys.exit(validator.run())

if __name__ == '__main__':
    main()
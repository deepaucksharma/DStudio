#!/usr/bin/env python3
"""
Final Navigation Fix - Addresses remaining broken links with deep path analysis
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

class FinalNavigationFixer:
    def __init__(self, base_dir="/home/deepak/DStudio"):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.fixes_applied = 0
        self.files_modified = set()
        
        # Load current issues
        with open(self.base_dir / 'link_analysis_results.json', 'r') as f:
            self.analysis = json.load(f)
            
    def fix_architects_handbook_paths(self, file_path, content):
        """Fix paths within architects-handbook that reference themselves incorrectly"""
        if 'architects-handbook' in str(file_path):
            # Remove redundant ../architects-handbook/ when already in architects-handbook
            content = re.sub(
                r'\[([^\]]+)\]\(\.\./architects-handbook/([^)]+)\)',
                r'[\1](../\2)',
                content
            )
            
            # Fix paths like ../core-principles/laws/X/index.md -> ../../core-principles/laws/X.md
            content = re.sub(
                r'\[([^\]]+)\]\(\.\./core-principles/laws/([^/]+)/index\.md\)',
                r'[\1](../../core-principles/laws/\2.md)',
                content
            )
            
            # Fix paths like ../core-principles/pillars/X/index.md -> ../../core-principles/pillars/X.md
            content = re.sub(
                r'\[([^\]]+)\]\(\.\./core-principles/pillars/([^/]+)/index\.md\)',
                r'[\1](../../core-principles/pillars/\2.md)',
                content
            )
            
        return content
        
    def fix_pattern_library_paths(self, file_path, content):
        """Fix paths within pattern-library that reference incorrectly"""
        if 'pattern-library' in str(file_path):
            # Remove redundant ../pattern-library/ when already in pattern-library
            content = re.sub(
                r'\[([^\]]+)\]\(\.\./pattern-library/([^)]+)\)',
                r'[\1](../\2)',
                content
            )
            
            # Fix core-principles references from pattern-library (need ../../)
            content = re.sub(
                r'\[([^\]]+)\]\(\.\./core-principles/([^)]+)\)',
                r'[\1](../../core-principles/\2)',
                content
            )
            
            # Fix architects-handbook references from pattern-library (need ../../)
            content = re.sub(
                r'\[([^\]]+)\]\(\.\./architects-handbook/([^)]+)\)',
                r'[\1](../../architects-handbook/\2)',
                content
            )
            
            # Fix excellence references - map to architects-handbook
            content = re.sub(
                r'\[([^\]]+)\]\(\.\./excellence/([^)]+)\)',
                r'[\1](../../architects-handbook/implementation-playbooks/\2)',
                content
            )
            
        return content
        
    def fix_core_principles_paths(self, file_path, content):
        """Fix paths within core-principles"""
        if 'core-principles' in str(file_path):
            # Remove /index.md from law and pillar references
            content = re.sub(
                r'\[([^\]]+)\]\(([^)]+)/index\.md\)',
                r'[\1](\2.md)',
                content
            )
            
            # Fix pattern-library references from core-principles (need ../../)
            content = re.sub(
                r'\[([^\]]+)\]\([\./]*pattern-library/([^)]+)\)',
                r'[\1](../../pattern-library/\2)',
                content
            )
            
        return content
        
    def fix_specific_broken_paths(self, content):
        """Fix specific known broken paths"""
        replacements = {
            # Fix quantitative analysis paths
            'quantitative-analysis/': '../architects-handbook/quantitative-analysis/',
            '../quantitative/': '../architects-handbook/quantitative-analysis/',
            
            # Fix human factors paths
            '../human-factors/': '../architects-handbook/human-factors/',
            'human-factors/': '../architects-handbook/human-factors/',
            
            # Fix case studies paths
            '../case-studies/': '../architects-handbook/case-studies/',
            'case-studies/': '../architects-handbook/case-studies/',
            
            # Fix learning paths
            '../learning-paths/': '../architects-handbook/learning-paths/',
            'learning-paths/': '../architects-handbook/learning-paths/',
            
            # Fix excellence/implementation guides
            '../excellence/': '../architects-handbook/implementation-playbooks/',
            'excellence/': '../architects-handbook/implementation-playbooks/',
            
            # Specific file fixes
            'zoom-scaling.md': '../architects-handbook/case-studies/infrastructure/zoom-scaling.md',
            'redis-architecture.md': '../architects-handbook/case-studies/databases/redis-architecture.md',
            'coordination-costs.md': '../architects-handbook/quantitative-analysis/coordination-costs.md',
            'monolith-to-microservices.md': '../architects-handbook/case-studies/infrastructure/monolith-to-microservices.md',
        }
        
        for old, new in replacements.items():
            if old in content and 'http' not in old:
                content = content.replace(f']({old}', f']({new}')
                
        return content
        
    def fix_index_references(self, content):
        """Convert /index.md references to proper paths"""
        # Convert /index.md to .md for laws and pillars
        content = re.sub(
            r'/laws/([^/]+)/index\.md',
            r'/laws/\1.md',
            content
        )
        content = re.sub(
            r'/pillars/([^/]+)/index\.md', 
            r'/pillars/\1.md',
            content
        )
        
        # Remove trailing /index.md for other paths
        content = re.sub(
            r'([^/]+)/index\.md\)',
            r'\1/)',
            content
        )
        
        return content
        
    def calculate_relative_path(self, from_file, to_file):
        """Calculate proper relative path between two files"""
        from_parts = from_file.parent.parts
        to_parts = Path(to_file).parts
        
        # Find common ancestor
        common_len = 0
        for i, (f, t) in enumerate(zip(from_parts, to_parts)):
            if f != t:
                break
            common_len = i + 1
            
        # Calculate ups needed
        ups = len(from_parts) - common_len
        
        # Build relative path
        if ups > 0:
            rel_path = '../' * ups + '/'.join(to_parts[common_len:])
        else:
            rel_path = '/'.join(to_parts[common_len:])
            
        return rel_path
        
    def fix_file(self, file_path):
        """Apply all fixes to a single file"""
        full_path = self.docs_dir / file_path
        if not full_path.exists():
            return 0
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original = content
        
        # Apply all fix strategies
        content = self.fix_architects_handbook_paths(file_path, content)
        content = self.fix_pattern_library_paths(file_path, content)
        content = self.fix_core_principles_paths(file_path, content)
        content = self.fix_specific_broken_paths(content)
        content = self.fix_index_references(content)
        
        # Additional pattern fixes
        # Fix double slashes
        content = re.sub(r'//', r'/', content)
        
        # Fix .md.md duplicates
        content = re.sub(r'\.md\.md', r'.md', content)
        
        # Fix empty links
        content = re.sub(r'\[([^\]]+)\]\(\)', r'\1', content)
        
        # Write back if changed
        if content != original:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.files_modified.add(str(file_path))
            self.fixes_applied += 1
            return 1
            
        return 0
        
    def create_missing_files(self):
        """Create any remaining missing files"""
        missing_files = [
            'docs/architects-handbook/quantitative-analysis/coordination-costs.md',
            'docs/architects-handbook/case-studies/infrastructure/zoom-scaling.md',
            'docs/progress.md',
        ]
        
        for file_path in missing_files:
            full_path = Path(file_path)
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Generate appropriate content
                title = full_path.stem.replace('-', ' ').replace('_', ' ').title()
                content = f"""# {title}

## Overview

This section covers {title.lower()}.

## Key Concepts

- Core principles
- Implementation strategies
- Best practices
- Common patterns

## Related Topics

- [Pattern Library](../../pattern-library/index.md)
- [Case Studies](../index.md)
- [Quantitative Analysis](../index.md)

## Further Reading

Additional resources and references for {title.lower()}.
"""
                with open(full_path, 'w') as f:
                    f.write(content)
                print(f"Created: {file_path}")
                
    def run(self):
        """Run final fixes"""
        print("Starting Final Navigation Fix...")
        print("=" * 50)
        
        # Create missing files first
        print("\n1. Creating missing files...")
        self.create_missing_files()
        
        # Process files with issues
        print("\n2. Processing files with issues...")
        files_to_fix = set()
        
        # Get files from analysis
        for file_path in self.analysis.get('issues', {}).keys():
            if file_path != 'mkdocs.yml' and file_path != 'stats':
                files_to_fix.add(file_path)
                
        total = len(files_to_fix)
        print(f"Processing {total} files with issues...")
        
        for i, file_path in enumerate(files_to_fix, 1):
            if i % 50 == 0:
                print(f"Progress: {i}/{total}")
            self.fix_file(Path(file_path))
            
        # Also process high-value files
        print("\n3. Processing high-value files...")
        important_files = [
            'architects-handbook/index.md',
            'pattern-library/index.md',
            'core-principles/index.md',
            'start-here/index.md',
            'index.md',
        ]
        
        for file_path in important_files:
            self.fix_file(Path(file_path))
            
        print(f"\n✅ Fixed {self.fixes_applied} files")
        print(f"Modified files: {len(self.files_modified)}")
        
        if self.files_modified:
            print("\nSample of modified files:")
            for f in list(self.files_modified)[:10]:
                print(f"  - {f}")
                
        return self.fixes_applied > 0

if __name__ == "__main__":
    fixer = FinalNavigationFixer()
    success = fixer.run()
    exit(0 if success else 1)
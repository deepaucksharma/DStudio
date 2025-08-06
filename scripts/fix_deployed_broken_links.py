#!/usr/bin/env python3
"""
Fix broken links found in deployed GitHub Pages site
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
import json

class DeployedLinkFixer:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / 'docs'
        self.fixes_applied = 0
        self.files_modified = set()
        
        # Map of broken patterns to their fixes
        self.link_fixes = {
            # Remove /index.md from internal links
            r'\[([^\]]+)\]\(([^)]+)/index\.md\)': r'[\1](\2/)',
            
            # Fix pattern-library paths
            r'/pattern-library/index\.md': '/pattern-library/',
            
            # Fix repeated directory structures
            r'architects-handbook/architects-handbook/': 'architects-handbook/',
            r'core-principles/core-principles/': 'core-principles/',
            r'pattern-library/pattern-library/': 'pattern-library/',
            
            # Fix .md in middle of paths
            r'([^)]+)\.md/([^)]+)': r'\1/\2',
            
            # Fix excessive parent directory traversal
            r'\.\./(\.\.)+/': '../',
            
            # Fix specific broken patterns
            r'learning-paths\.md/': 'learning-paths/',
            r'case-studies\.md/': 'case-studies/',
            r'scaling\.md/': 'scaling/',
            r'tools\.md/': 'tools/',
            r'human-factors\.md/': 'human-factors/',
        }
        
        # Files that should exist but don't - we'll create them
        self.missing_files_to_create = [
            'docs/index.md',
            'docs/pattern-library/ml-infrastructure/index.md',
            'docs/pattern-library/resilience/circuit-breaker.md',
            'docs/pattern-library/data-management/saga.md',
            'docs/pattern-library/data-management/event-sourcing.md',
            'docs/pattern-library/data-management/cqrs.md',
            'docs/pattern-library/coordination/consensus.md',
        ]
    
    def fix_file(self, file_path: Path) -> int:
        """Fix links in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_in_file = 0
            
            # Apply all regex fixes
            for pattern, replacement in self.link_fixes.items():
                new_content, count = re.subn(pattern, replacement, content)
                if count > 0:
                    fixes_in_file += count
                    content = new_content
            
            # Fix specific broken link patterns
            # Fix paths with too many ../ 
            content = re.sub(r'\.\./(\.\./)+(\.\./)+(\.\./)/', '../../', content)
            content = re.sub(r'\.\./(\.\./)+(\.\./)/', '../', content)
            
            # Fix paths like ../../....../
            content = re.sub(r'\.\./(\.\.)+\.\./', '../../', content)
            
            # Remove /index.md from end of internal links
            content = re.sub(r'\]\(([^)]+?)/index\.md\)', r'](\1/)', content)
            
            # Fix doubled slashes
            content = re.sub(r'([^:])//+', r'\1/', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_modified.add(file_path)
                self.fixes_applied += fixes_in_file
                return fixes_in_file
            
            return 0
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return 0
    
    def create_missing_index_files(self):
        """Create missing index.md files"""
        created_files = []
        
        # Template for index files
        index_template = """---
title: {title}
description: {description}
---

# {title}

{content}
"""
        
        index_contents = {
            'docs/index.md': {
                'title': 'Distributed Systems Studio',
                'description': 'Master distributed systems through fundamental laws and proven patterns',
                'content': '\n'.join([
                    '## Welcome to Distributed Systems Studio\n',
                    'Navigate to:',
                    '- [Core Principles](core-principles/)',
                    '- [Pattern Library](pattern-library/)',
                    '- [Architect\'s Handbook](architects-handbook/)',
                    '- [Excellence Guides](excellence/)'
                ])
            },
            'docs/pattern-library/ml-infrastructure/index.md': {
                'title': 'ML Infrastructure Patterns',
                'description': 'Patterns for building scalable machine learning infrastructure',
                'content': '\n'.join([
                    '## ML Infrastructure Patterns\n',
                    'Explore patterns for:',
                    '- [Model Serving at Scale](model-serving-scale/)',
                    '- [Feature Store](feature-store/)',
                    '- [ML Pipeline Orchestration](ml-pipeline-orchestration/)',
                    '- [Distributed Training](distributed-training-infrastructure/)',
                    '- [Experiment Tracking](experiment-tracking-mlflow/)'
                ])
            },
            'docs/pattern-library/resilience/circuit-breaker.md': {
                'title': 'Circuit Breaker Pattern',
                'description': 'Prevent cascading failures in distributed systems',
                'content': 'See [Circuit Breaker Transformed](circuit-breaker-transformed/)'
            },
            'docs/pattern-library/data-management/saga.md': {
                'title': 'Saga Pattern',
                'description': 'Manage distributed transactions without 2PC',
                'content': 'Content for Saga pattern - managing distributed transactions'
            },
            'docs/pattern-library/data-management/event-sourcing.md': {
                'title': 'Event Sourcing Pattern', 
                'description': 'Store state as a sequence of events',
                'content': 'Content for Event Sourcing pattern'
            },
            'docs/pattern-library/data-management/cqrs.md': {
                'title': 'CQRS Pattern',
                'description': 'Command Query Responsibility Segregation',
                'content': 'Content for CQRS pattern'
            },
            'docs/pattern-library/coordination/consensus.md': {
                'title': 'Consensus Patterns',
                'description': 'Achieving agreement in distributed systems',
                'content': 'Content for Consensus patterns'
            }
        }
        
        for file_path, content_data in index_contents.items():
            full_path = self.base_dir / file_path
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                content = index_template.format(**content_data)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                created_files.append(file_path)
                print(f"Created: {file_path}")
        
        return created_files
    
    def fix_all_files(self):
        """Fix all markdown files in docs directory"""
        print("Starting deployed link fixes...")
        
        # First create missing files
        created_files = self.create_missing_index_files()
        print(f"\nCreated {len(created_files)} missing files")
        
        # Then fix links in existing files
        for md_file in self.docs_dir.rglob('*.md'):
            fixes = self.fix_file(md_file)
            if fixes > 0:
                rel_path = md_file.relative_to(self.base_dir)
                print(f"Fixed {fixes} links in {rel_path}")
        
        print(f"\n=== Summary ===")
        print(f"Files modified: {len(self.files_modified)}")
        print(f"Total fixes applied: {self.fixes_applied}")
        print(f"Files created: {len(created_files)}")

if __name__ == '__main__':
    fixer = DeployedLinkFixer('/home/deepak/DStudio')
    fixer.fix_all_files()

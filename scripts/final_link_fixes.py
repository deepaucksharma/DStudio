#!/usr/bin/env python3
"""
Final pass to fix remaining broken link patterns
"""

import re
from pathlib import Path
from typing import Tuple

class FinalLinkFixer:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / 'docs'
        self.fixes_applied = 0
        self.files_modified = set()
    
    def fix_file(self, file_path: Path) -> int:
        """Apply final fixes to a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_in_file = 0
            
            # Fix patterns with ..../
            content = re.sub(r'\.\.\.\.\./([^)]+)', r'../../\1', content)
            
            # Fix patterns with repeated ../
            content = re.sub(r'(\.\./)\1{3,}', r'../../', content)
            
            # Fix specific broken patterns
            replacements = [
                # Fix pattern-library internal references
                (r'\[([^]]+)\]\(\.\.\.\.\./pattern-library/([^)]+)\)', r'[\1](../\2)'),
                (r'\[([^]]+)\]\(\.\.\.\.\./core-principles/([^)]+)\)', r'[\1](../../core-principles/\2)'),
                (r'\[([^]]+)\]\(\.\.\.\.\./architects-handbook/([^)]+)\)', r'[\1](../../architects-handbook/\2)'),
                
                # Remove .md from middle of paths
                (r'([a-z-]+)\.md/([a-z-]+)', r'\1/\2'),
                
                # Fix external links that shouldn't have /index.md
                (r'(https://[^)]+)/index\.md\)', r'\1/)'),
                (r'(https://[^)]+)\.html/index\.md\)', r'\1.html)'),
                
                # Fix paths with index.md that should be directory references
                (r'\[([^]]+)\]\(([^)]+)/index\.md\)', r'[\1](\2/)'),
                
                # Fix broken relative paths in pattern-library
                (r'\.\./(\.\./)+(pattern-library|core-principles|architects-handbook)/', r'../../\3/'),
                
                # Fix learning path references
                (r'architects-handbook/learning-paths\.md/', r'architects-handbook/learning-paths/'),
                (r'case-studies\.md/', r'case-studies/'),
                
                # Remove duplicate slashes
                (r'([^:])//+', r'\1/'),
            ]
            
            for pattern, replacement in replacements:
                new_content, count = re.subn(pattern, replacement, content)
                if count > 0:
                    fixes_in_file += count
                    content = new_content
            
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
    
    def run(self):
        """Run final fixes on all markdown files"""
        print("Applying final link fixes...\n")
        
        for md_file in self.docs_dir.rglob('*.md'):
            fixes = self.fix_file(md_file)
            if fixes > 0:
                rel_path = md_file.relative_to(self.base_dir)
                print(f"Fixed {fixes} links in {rel_path}")
        
        print(f"\n=== Final Fix Summary ===")
        print(f"Files modified: {len(self.files_modified)}")
        print(f"Total fixes applied: {self.fixes_applied}")

if __name__ == '__main__':
    fixer = FinalLinkFixer('/home/deepak/DStudio')
    fixer.run()

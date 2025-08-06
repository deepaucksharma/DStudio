#!/usr/bin/env python3
"""
Fix common broken link patterns in DStudio documentation.
"""

import os
import re
from pathlib import Path
from typing import List

class CommonPatternFixer:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.fixes_applied = 0
        
    def fix_empty_links(self, file_path: Path):
        """Fix empty links like []() or [text]()'"""
        if not file_path.exists():
            return 0
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove empty links [text]()
            content = re.sub(r'\[([^\]]+)\]\(\)', r'\1', content)
            
            # Remove empty links []()  
            content = re.sub(r'\[\]\(\)', '', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return 1
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return 0
    
    def fix_double_slashes(self, file_path: Path):
        """Fix links with double slashes like pattern//index.md"""
        if not file_path.exists():
            return 0
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix double slashes in links
            content = re.sub(r'\]\(([^)]*?)//([^)]*)\)', r'](\1/\2)', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return 1
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return 0
    
    def fix_index_redirects(self, file_path: Path):
        """Fix patterns that should point to index.md"""
        if not file_path.exists():
            return 0
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Common patterns that should be index.md
            patterns = [
                (r'\]\(([^)]*?)/\)', r'](\1/index.md)'),  # pattern/ -> pattern/index.md
                (r'\]\(([^)]*?)\)', lambda m: f']({m.group(1)}/index.md)' 
                 if not m.group(1).endswith('.md') and not m.group(1).endswith('.html') 
                    and '.' not in os.path.basename(m.group(1)) and not m.group(1).startswith('http') 
                    else m.group(0))
            ]
            
            for pattern, replacement in patterns:
                if callable(replacement):
                    content = re.sub(pattern, replacement, content)
                else:
                    content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return 1
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return 0
    
    def fix_redundant_paths(self, file_path: Path):
        """Fix redundant paths like pattern-library/coordination/pattern-library/"""
        if not file_path.exists():
            return 0
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix redundant pattern-library paths
            content = re.sub(
                r'\]\(([^)]*?)pattern-library/([^/]*?)/pattern-library/([^)]*?)\)',
                r'](\1pattern-library/\3)',
                content
            )
            
            # Fix redundant core-principles paths
            content = re.sub(
                r'\]\(([^)]*?)core-principles/([^/]*?)/core-principles/([^)]*?)\)',
                r'](\1core-principles/\3)',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return 1
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return 0
    
    def run(self):
        """Run all the common pattern fixes"""
        print("Starting common pattern fixes...")
        
        total_fixes = 0
        
        for md_file in self.docs_dir.rglob("*.md"):
            fixes = 0
            fixes += self.fix_empty_links(md_file)
            fixes += self.fix_double_slashes(md_file)
            fixes += self.fix_redundant_paths(md_file)
            
            if fixes > 0:
                total_fixes += fixes
                print(f"Fixed {fixes} patterns in {md_file.relative_to(self.base_dir)}")
        
        print(f"\nTotal fixes applied: {total_fixes}")

if __name__ == "__main__":
    fixer = CommonPatternFixer("/home/deepak/DStudio")
    fixer.run()
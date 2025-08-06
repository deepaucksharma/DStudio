#!/usr/bin/env python3
"""
Targeted broken link fixer for DStudio documentation.
This script focuses on fixing the most common patterns of broken links.
"""

import os
import re
from pathlib import Path
from typing import Dict, List

class TargetedLinkFixer:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.fixed_count = 0
        self.files_modified = []
        
    def fix_file_links(self, file_path: Path):
        """Fix links in a specific file"""
        if not file_path.exists():
            return 0
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_in_file = 0
            
            # Pattern 1: Fix relative paths like "../../architects-handbook/case-studies/" 
            # when already in architects-handbook/case-studies/
            if "architects-handbook/case-studies" in str(file_path):
                # Replace incorrect relative paths
                content = re.sub(
                    r'\[([^\]]*)\]\(\.\.\/\.\.\/architects-handbook\/case-studies\/([^)]+)\)',
                    r'[\1](\2)',
                    content
                )
                if content != original_content:
                    fixes_in_file += len(re.findall(r'\.\.\/\.\.\/architects-handbook\/case-studies\/', original_content))
                    print(f"Fixed relative paths in {file_path}")
            
            # Pattern 2: Fix links missing .md extension
            # Look for links to directories that should be index.md files
            content = re.sub(
                r'\[([^\]]*)\]\(([^)]*/)([^/)]*)\)',
                lambda m: f'[{m.group(1)}]({m.group(2)}{m.group(3)}/index.md)' if not m.group(3).endswith('.md') else m.group(0),
                content
            )
            
            # Pattern 3: Fix links ending with / that should point to index.md
            content = re.sub(
                r'\[([^\]]*)\]\(([^)]+)/\)',
                r'[\1](\2/index.md)',
                content
            )
            
            # Pattern 4: Add .md extension to files that exist but are referenced without extension
            def fix_missing_md_extension(match):
                link_text = match.group(1)
                link_path = match.group(2)
                
                # If it already has an extension, leave it
                if '.' in os.path.basename(link_path):
                    return match.group(0)
                
                # Check if adding .md would create a valid path
                current_dir = file_path.parent
                target_path = current_dir / f"{link_path}.md"
                
                if target_path.exists():
                    return f'[{link_text}]({link_path}.md)'
                
                return match.group(0)
            
            content = re.sub(
                r'\[([^\]]*)\]\(([^)#]+?)(?=#|$)\)',
                fix_missing_md_extension,
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                if file_path not in self.files_modified:
                    self.files_modified.append(str(file_path.relative_to(self.base_dir)))
                
                return 1
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return 0
    
    def fix_specific_problematic_files(self):
        """Fix specific files that were identified as having many issues"""
        problem_files = [
            "docs/architects-handbook/case-studies/index.md",
            "docs/architects-handbook/learning-paths/index.md", 
            "docs/interview-prep/engineering-leadership/framework-index.md",
            "docs/interview-prep/engineering-leadership/index.md"
        ]
        
        for file_path in problem_files:
            full_path = self.base_dir / file_path
            if self.fix_file_links(full_path):
                self.fixed_count += 1
                print(f"Fixed links in {file_path}")
    
    def fix_all_markdown_files(self):
        """Fix all markdown files in the docs directory"""
        for md_file in self.docs_dir.rglob("*.md"):
            if self.fix_file_links(md_file):
                self.fixed_count += 1
    
    def run(self):
        """Run the targeted fixes"""
        print("Starting targeted link fixes...")
        
        print("1. Fixing specific problematic files...")
        self.fix_specific_problematic_files()
        
        print("2. Scanning all markdown files...")
        self.fix_all_markdown_files()
        
        print(f"\nSummary:")
        print(f"Files with fixes applied: {self.fixed_count}")
        print(f"Total files modified: {len(self.files_modified)}")
        
        if self.files_modified:
            print("\nModified files:")
            for file in self.files_modified[:20]:  # Show first 20
                print(f"  - {file}")
            if len(self.files_modified) > 20:
                print(f"  ... and {len(self.files_modified) - 20} more")

if __name__ == "__main__":
    fixer = TargetedLinkFixer("/home/deepak/DStudio")
    fixer.run()
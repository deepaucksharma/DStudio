#!/usr/bin/env python3
"""
Fix escaped admonitions that were accidentally broken by previous scripts
"""

import os
from pathlib import Path

def fix_admonitions():
    """Fix escaped exclamation marks in admonitions"""
    docs_dir = Path("/home/deepak/DStudio/docs")
    fixed_count = 0
    
    for md_file in docs_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            # Fix escaped admonitions
            content = content.replace(r'\!\!\!', '!!!')
            
            if content != original:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                print(f"Fixed: {md_file.relative_to(docs_dir)}")
                
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            
    print(f"\nFixed {fixed_count} files with broken admonitions")
    return fixed_count

if __name__ == "__main__":
    fix_admonitions()
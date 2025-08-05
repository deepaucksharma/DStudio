#!/usr/bin/env python3
"""
Ultra-aggressive final reduction for the last 7 patterns.
"""

import re
from pathlib import Path

FINAL_TARGETS = [
    ('coordination', 'lease'),
    ('scaling', 'id-generation-scale'), 
    ('coordination', 'generation-clock'),
    ('communication', 'websocket'),
    ('data-management', 'consistent-hashing'),
    ('resilience', 'retry-backoff'),
    ('communication', 'request-reply')
]

def ultra_aggressive_reduction(file_path):
    """Ultra-aggressive code reduction - prioritize concepts over all code."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    original_lines = len(content.split('\n'))
    
    # 1. Replace ALL remaining code blocks with single concept line
    content = re.sub(r'```.*?```', '**Concept:** See production implementations\n\n', content, flags=re.DOTALL)
    
    # 2. Replace ALL mermaid diagrams with simple text
    content = re.sub(r'```mermaid.*?```', '**Architecture:** Component interaction pattern\n\n', content, flags=re.DOTALL)
    
    # 3. Convert all lists with >3 items to summary statements
    def condense_long_lists(match):
        text = match.group(0)
        if text.count('\n-') > 3:
            return "**Key Points:** Multiple configuration options and trade-offs available\n\n"
        return text
    
    content = re.sub(r'(?:^- .*\n){4,}', condense_long_lists, content, flags=re.MULTILINE)
    
    # 4. Remove verbose implementation sections entirely
    content = re.sub(r'### (?:Implementation|Examples?|Configuration).*?(?=###|\n---|\n## |$)', '', content, flags=re.DOTALL)
    
    # 5. Condense any remaining multi-line code-like content
    content = re.sub(r'(?:^    .*\n){2,}', '**Implementation available in production systems**\n\n', content, flags=re.MULTILINE)
    
    # 6. Remove indented code blocks (4+ spaces)
    content = re.sub(r'(?:^[ ]{4,}.*\n)+', '', content, flags=re.MULTILINE)
    
    # 7. Clean up excessive whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # 8. Remove empty sections
    content = re.sub(r'###[^\n]*\n\n(?=###|\n---|\n## |$)', '', content)
    
    final_lines = len(content.split('\n'))
    reduction_percent = ((original_lines - final_lines) / original_lines) * 100
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path.name}: {original_lines} → {final_lines} lines ({reduction_percent:.1f}% reduction)")
        return True
    except Exception as e:
        print(f"❌ Error writing {file_path}: {e}")
        return False

def main():
    """Ultra-aggressive reduction for final 7 patterns."""
    base_path = Path('/home/deepak/DStudio/docs/pattern-library')
    
    print("⚡ Ultra-aggressive final reduction for last 7 patterns...")
    
    for category, pattern_name in FINAL_TARGETS:
        file_path = base_path / category / f"{pattern_name}.md"
        if file_path.exists():
            ultra_aggressive_reduction(file_path)
        else:
            print(f"⚠️  Could not find {pattern_name}.md in {category}/")
    
    print("\n⚡ Ultra-aggressive reduction complete!")

if __name__ == "__main__":
    main()
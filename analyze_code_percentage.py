#!/usr/bin/env python3
"""
Code percentage analyzer for pattern library files.
Calculates percentage of code content vs total content for each pattern.
"""

import os
import re
from pathlib import Path

def count_lines_and_code(file_path):
    """Count total lines and code lines in a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0, 0, 0
    
    lines = content.split('\n')
    total_lines = len(lines)
    
    # Count code blocks (fenced with ``` or indented)
    code_lines = 0
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check for fenced code blocks
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
            
        # Count code lines
        if in_code_block:
            code_lines += 1
        elif line.startswith('    ') and stripped:  # Indented code
            code_lines += 1
    
    # Also count inline code (rough estimate)
    inline_code_chars = len(re.findall(r'`[^`]+`', content))
    
    return total_lines, code_lines, inline_code_chars

def analyze_patterns():
    """Analyze all patterns and return sorted by code percentage."""
    pattern_dirs = [
        'architecture', 'communication', 'coordination', 
        'data-management', 'resilience', 'scaling'
    ]
    
    results = []
    base_path = Path('/home/deepak/DStudio/docs/pattern-library')
    
    for pattern_dir in pattern_dirs:
        dir_path = base_path / pattern_dir
        if not dir_path.exists():
            continue
            
        for file_path in dir_path.glob('*.md'):
            if file_path.name == 'index.md':
                continue
                
            total_lines, code_lines, inline_code = count_lines_and_code(file_path)
            
            if total_lines > 0:
                # Weight inline code less than block code
                effective_code_lines = code_lines + (inline_code / 10)
                code_percentage = (effective_code_lines / total_lines) * 100
                
                results.append({
                    'file': str(file_path),
                    'category': pattern_dir,
                    'name': file_path.stem,
                    'total_lines': total_lines,
                    'code_lines': code_lines,
                    'inline_code': inline_code,
                    'code_percentage': round(code_percentage, 1)
                })
    
    # Sort by code percentage (highest first)
    results.sort(key=lambda x: x['code_percentage'], reverse=True)
    return results

def main():
    print("Analyzing code percentage in all pattern library files...\n")
    
    results = analyze_patterns()
    high_code_patterns = [r for r in results if r['code_percentage'] > 20]
    
    print(f"Found {len(results)} patterns total")
    print(f"Found {len(high_code_patterns)} patterns with >20% code content\n")
    
    print("TOP 20 PATTERNS WITH HIGHEST CODE PERCENTAGE:")
    print("=" * 80)
    print(f"{'Pattern':<30} {'Category':<15} {'Code %':<8} {'Lines':<8} {'Code Lines'}")
    print("-" * 80)
    
    for pattern in results[:20]:
        print(f"{pattern['name']:<30} {pattern['category']:<15} {pattern['code_percentage']:<8} "
              f"{pattern['total_lines']:<8} {pattern['code_lines']}")
    
    print(f"\nAll {len(high_code_patterns)} patterns needing reduction:")
    print("=" * 50)
    for pattern in high_code_patterns:
        print(f"- {pattern['name']} ({pattern['category']}): {pattern['code_percentage']}%")
    
    return high_code_patterns

if __name__ == "__main__":
    main()
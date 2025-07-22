#!/usr/bin/env python3
"""Scan markdown files for code blocks to identify which need visual conversion."""

import os
import re
from pathlib import Path

def count_code_blocks(file_path):
    """Count code blocks in a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count different types of code blocks
    triple_backtick = len(re.findall(r'```[\s\S]*?```', content))
    indented_code = len(re.findall(r'^    \S.*$', content, re.MULTILINE))
    
    # Also check for specific code languages
    python_blocks = len(re.findall(r'```python[\s\S]*?```', content))
    java_blocks = len(re.findall(r'```java[\s\S]*?```', content))
    yaml_blocks = len(re.findall(r'```yaml[\s\S]*?```', content))
    
    return {
        'total': triple_backtick,
        'python': python_blocks,
        'java': java_blocks,
        'yaml': yaml_blocks,
        'indented': indented_code
    }

def scan_directory(base_path):
    """Scan directory for markdown files with code blocks."""
    results = {}
    
    for root, dirs, files in os.walk(base_path):
        # Skip axioms and other directories
        if 'part1-axioms' in root or 'assets' in root or '_templates' in root:
            continue
            
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_path)
                
                code_count = count_code_blocks(file_path)
                if code_count['total'] > 0:
                    results[rel_path] = code_count
    
    return results

def categorize_results(results):
    """Categorize results by section."""
    categories = {
        'pillars': {},
        'patterns': {},
        'case_studies': {},
        'quantitative': {},
        'human_factors': {},
        'other': {}
    }
    
    for path, count in results.items():
        if 'part2-pillars' in path:
            categories['pillars'][path] = count
        elif 'patterns' in path:
            categories['patterns'][path] = count
        elif 'case-studies' in path:
            categories['case_studies'][path] = count
        elif 'quantitative' in path:
            categories['quantitative'][path] = count
        elif 'human-factors' in path:
            categories['human_factors'][path] = count
        else:
            categories['other'][path] = count
    
    return categories

def main():
    base_path = 'docs'
    results = scan_directory(base_path)
    categorized = categorize_results(results)
    
    # Print summary
    print("# Code Block Analysis Summary\n")
    
    for category, files in categorized.items():
        if files:
            print(f"## {category.replace('_', ' ').title()}")
            print(f"Files with code: {len(files)}\n")
            
            # Sort by total code blocks
            sorted_files = sorted(files.items(), key=lambda x: x[1]['total'], reverse=True)
            
            for path, count in sorted_files[:10]:  # Top 10 files
                print(f"- `{path}`: {count['total']} code blocks")
                if count['python'] > 0:
                    print(f"  - Python: {count['python']}")
                if count['java'] > 0:
                    print(f"  - Java: {count['java']}")
                if count['yaml'] > 0:
                    print(f"  - YAML: {count['yaml']}")
            
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")
            print()

if __name__ == "__main__":
    main()
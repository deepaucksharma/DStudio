#!/usr/bin/env python3
"""
Fix remaining broken links with targeted fixes.
"""

import os
import re
import sys

def fix_double_suffix(content):
    """Fix double suffix issue like caching-strategies-strategies."""
    # Fix caching-strategies-strategies -> caching-strategies
    content = re.sub(r'caching-strategies-strategies', 'caching-strategies', content)
    return content

def fix_relative_paths(content, file_path):
    """Fix incorrect relative paths based on file location."""
    # Determine the depth of the current file
    rel_path = os.path.relpath(file_path, 'docs')
    depth = len(rel_path.split(os.sep)) - 1
    
    # For files in case-studies/, patterns should be ../patterns/
    if 'case-studies' in file_path and depth == 1:
        # Fix ../../patterns/ to ../patterns/
        content = re.sub(r'\]\(../../patterns/', '](../patterns/', content)
        content = re.sub(r'\]\(../../quantitative/', '](../quantitative/', content)
        content = re.sub(r'\]\(../../part1-axioms/', '](../part1-axioms/', content)
        content = re.sub(r'\]\(../../part2-pillars/', '](../part2-pillars/', content)
    
    return content

def fix_trailing_slashes(content):
    """Remove trailing slashes from links that should point to .md files."""
    # Pattern to match links with trailing slashes
    patterns_to_fix = [
        (r'\(/case-studies/netflix-chaos/\)', '(/case-studies/netflix-chaos)'),
        (r'\(/case-studies/social-graph/\)', '(/case-studies/social-graph)'),
        (r'\(/patterns/([^/]+)/\)', r'(/patterns/\1)'),
        (r'\(/learning-paths/([^/]+)/\)', r'(/learning-paths/\1)'),
        (r'\(/quantitative/([^/]+)/\)', r'(/quantitative/\1)'),
        (r'\(/tools/([^/]+)/\)', r'(/tools/\1)'),
    ]
    
    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_google_interview_paths(content):
    """Fix Google interview specific paths."""
    # Remove google-interviews prefix from internal case study links
    content = re.sub(r'/case-studies/google-systems/google-interviews/google-search', 
                     '/case-studies/google-systems/google-search', content)
    content = re.sub(r'/google-systems/google-interviews/google-search',
                     '/case-studies/google-systems/google-search', content)
    
    # Fix preparation guide references
    content = re.sub(r'\]\(/preparation-guide\)', '](preparation-guide)', content)
    content = re.sub(r'\]\(/common-mistakes\)', '](common-mistakes)', content)
    content = re.sub(r'\]\(/google-search\)', '](google-search)', content)
    
    return content

def fix_pattern_references(content):
    """Fix references to patterns that don't exist or have wrong names."""
    # Map non-existent patterns to existing ones
    pattern_mappings = {
        'consistent-hashing': 'consistent-hashing',  # Ensure no .md extension
        'geospatial-indexing': 'spatial-indexing',
        'caching': 'caching-strategies',
        'privacy.md': 'location-privacy',
        'pacelc': '../quantitative/cap-theorem',
    }
    
    for old_pattern, new_pattern in pattern_mappings.items():
        # Fix various link formats
        content = re.sub(rf'\]\(/patterns/{old_pattern}\)', f'](/patterns/{new_pattern})', content)
        content = re.sub(rf'\]\(../patterns/{old_pattern}\)', f'](../patterns/{new_pattern})', content)
        content = re.sub(rf'\]\(../../patterns/{old_pattern}\)', f'](../../patterns/{new_pattern})', content)
    
    return content

def fix_absolute_links(content):
    """Fix absolute links that should be relative."""
    # Remove .md extensions from absolute links
    content = re.sub(r'\]\(/patterns/([^)]+)\.md\)', r'](/patterns/\1)', content)
    content = re.sub(r'\]\(/case-studies/([^)]+)\.md\)', r'](/case-studies/\1)', content)
    content = re.sub(r'\]\(/quantitative/([^)]+)\.md\)', r'](/quantitative/\1)', content)
    
    return content

def process_file(file_path):
    """Process a single file with all fixes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all fixes
        content = fix_double_suffix(content)
        content = fix_relative_paths(content, file_path)
        content = fix_trailing_slashes(content)
        content = fix_google_interview_paths(content)
        content = fix_pattern_references(content)
        content = fix_absolute_links(content)
        
        # Save if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function."""
    print("Applying targeted fixes for remaining broken links...")
    print("-" * 80)
    
    files_fixed = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                if process_file(file_path):
                    files_fixed += 1
                    print(f"Fixed: {file_path}")
    
    print(f"\nFixed {files_fixed} files")
    
    # Run verification
    print("\nRunning final verification...")
    os.system("python3 scripts/verify-links.py")

if __name__ == "__main__":
    main()
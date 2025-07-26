#!/usr/bin/env python3
"""
Analyze broken link patterns to understand common issues.
"""

import os
import re
from collections import defaultdict, Counter
from pathlib import Path

def extract_links(content, file_path):
    """Extract all markdown links from content."""
    links = []
    
    # Pattern for [text](url) style links
    markdown_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    for match in re.finditer(markdown_link_pattern, content):
        link_text = match.group(1)
        link_url = match.group(2)
        line_num = content[:match.start()].count('\n') + 1
        
        # Skip external links and anchors
        if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
            continue
            
        links.append({
            'text': link_text,
            'url': link_url,
            'line': line_num,
            'file': file_path
        })
    
    return links

def normalize_link(link_url, source_file):
    """Normalize a link URL to an absolute path."""
    source_dir = os.path.dirname(source_file)
    
    # Remove any anchors
    if '#' in link_url:
        link_url = link_url.split('#')[0]
    
    # Handle absolute paths (starting with /)
    if link_url.startswith('/'):
        # Strip leading slash and treat as relative to docs/
        link_url = link_url[1:]
        target = os.path.join('docs', link_url)
    else:
        # Relative path
        target = os.path.normpath(os.path.join(source_dir, link_url))
    
    # Add .md extension if missing and not pointing to a directory
    if not target.endswith('.md') and not target.endswith('/'):
        # Check if it's meant to be a directory index
        if os.path.isdir(target):
            target = os.path.join(target, 'index.md')
        else:
            target += '.md'
    elif target.endswith('/'):
        target = target.rstrip('/') + '/index.md'
    
    return target

def analyze_broken_links():
    """Analyze patterns in broken links."""
    broken_patterns = defaultdict(list)
    link_types = Counter()
    missing_files = set()
    
    # Walk through all markdown files
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    links = extract_links(content, file_path)
                    
                    for link in links:
                        target_path = normalize_link(link['url'], file_path)
                        
                        if not os.path.exists(target_path):
                            # Categorize the broken link
                            if link['url'].startswith('/'):
                                link_types['absolute'] += 1
                            elif link['url'].startswith('../'):
                                link_types['relative_parent'] += 1
                            elif link['url'].startswith('./'):
                                link_types['relative_current'] += 1
                            else:
                                link_types['relative_implicit'] += 1
                            
                            # Check if it's a directory link
                            if link['url'].endswith('/'):
                                broken_patterns['directory_links'].append(link['url'])
                            
                            # Check for common patterns
                            if '/patterns/' in target_path:
                                broken_patterns['patterns'].append(target_path)
                            elif '/case-studies/' in target_path:
                                broken_patterns['case_studies'].append(target_path)
                            elif '/learning-paths/' in target_path:
                                broken_patterns['learning_paths'].append(target_path)
                            elif '/tools/' in target_path:
                                broken_patterns['tools'].append(target_path)
                            elif '/quantitative/' in target_path:
                                broken_patterns['quantitative'].append(target_path)
                            
                            missing_files.add(target_path)
                
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return broken_patterns, link_types, missing_files

def find_similar_existing_files(missing_file):
    """Find similar existing files that might be the correct target."""
    base_name = os.path.basename(missing_file).replace('.md', '')
    similar = []
    
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md') and base_name in file:
                similar.append(os.path.join(root, file))
    
    return similar

def main():
    """Main function."""
    print("Analyzing broken link patterns...")
    print("-" * 80)
    
    broken_patterns, link_types, missing_files = analyze_broken_links()
    
    print("\nBroken Link Types:")
    for link_type, count in link_types.items():
        print(f"  {link_type}: {count}")
    
    print("\nBroken Links by Category:")
    for category, links in broken_patterns.items():
        print(f"  {category}: {len(links)} broken links")
    
    print("\nMost Common Missing Files:")
    file_counter = Counter(missing_files)
    for file, count in file_counter.most_common(20):
        print(f"  {file}: referenced {count} times")
        similar = find_similar_existing_files(file)
        if similar:
            print(f"    Possible matches: {', '.join(similar)}")
    
    print("\nSummary:")
    print(f"  Total unique missing files: {len(missing_files)}")
    print(f"  Total broken link references: {sum(file_counter.values())}")

if __name__ == "__main__":
    main()
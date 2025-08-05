#!/usr/bin/env python3
"""
Script to verify all internal links in markdown files.
Checks that link targets exist and are correctly referenced.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import sys

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

def verify_links():
    """Verify all internal links in markdown files."""
    broken_links = []
    all_links = []
    files_checked = 0
    
    # Walk through all markdown files
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                files_checked += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    links = extract_links(content, file_path)
                    
                    for link in links:
                        all_links.append(link)
                        target_path = normalize_link(link['url'], file_path)
                        
                        if not os.path.exists(target_path):
                            broken_links.append({
                                'source': file_path,
                                'target': target_path,
                                'original_url': link['url'],
                                'line': link['line'],
                                'text': link['text']
                            })
                
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return broken_links, all_links, files_checked

def main():
    """Main function."""
    print("Verifying internal links in markdown files...")
    print("-" * 80)
    
    broken_links, all_links, files_checked = verify_links()
    
    print(f"\nFiles checked: {files_checked}")
    print(f"Total internal links found: {len(all_links)}")
    print(f"Broken links found: {len(broken_links)}")
    
    if broken_links:
        print("\n" + "=" * 80)
        print("BROKEN LINKS REPORT")
        print("=" * 80)
        
        # Group by source file
        by_source = defaultdict(list)
        for link in broken_links:
            by_source[link['source']].append(link)
        
        for source_file, links in sorted(by_source.items()):
            print(f"\n{source_file}:")
            for link in sorted(links, key=lambda x: x['line']):
                print(f"  Line {link['line']}: [{link['text']}]({link['original_url']})")
                print(f"    -> Expected: {link['target']}")
        
        print("\n" + "=" * 80)
        print(f"Total broken links: {len(broken_links)}")
        return 1
    else:
        print("\n✅ All internal links are valid!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
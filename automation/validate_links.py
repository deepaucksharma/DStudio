#!/usr/bin/env python3
"""
Link validator for distributed systems documentation.
Checks all internal links to ensure they point to valid targets.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import sys

def extract_links_from_file(file_path):
    """Extract all markdown links from a file."""
    links = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Match markdown links: [text](url)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    for text, url in matches:
        # Skip external links
        if url.startswith('http://') or url.startswith('https://'):
            continue
        # Skip mailto links
        if url.startswith('mailto:'):
            continue
        # Store internal links
        links.append((text, url, file_path))
    
    return links

def resolve_link(link_url, source_file):
    """Resolve a relative link to an absolute path."""
    source_dir = os.path.dirname(source_file)
    
    # Handle absolute paths (starting with /)
    if link_url.startswith('/'):
        # Remove leading slash and treat as relative to docs/
        link_path = link_url[1:]
        resolved = os.path.join('docs', link_path)
    else:
        # Relative path
        resolved = os.path.join(source_dir, link_url)
    
    # Normalize the path
    resolved = os.path.normpath(resolved)
    
    # Handle anchors
    if '#' in resolved:
        file_part, anchor = resolved.split('#', 1)
        return file_part, anchor
    
    return resolved, None

def check_file_exists(file_path):
    """Check if a file exists, handling directory index.md."""
    if os.path.exists(file_path):
        return True
    
    # If path ends with /, check for index.md
    if file_path.endswith('/'):
        index_path = os.path.join(file_path, 'index.md')
        return os.path.exists(index_path)
    
    # If path doesn't have extension, try .md
    if not os.path.splitext(file_path)[1]:
        md_path = file_path + '.md'
        if os.path.exists(md_path):
            return True
        
        # Also try as directory with index.md
        index_path = os.path.join(file_path, 'index.md')
        if os.path.exists(index_path):
            return True
    
    return False

def validate_links(docs_dir='docs'):
    """Validate all internal links in the documentation."""
    broken_links = []
    all_links = []
    file_count = 0
    
    # Walk through all markdown files
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                file_count += 1
                
                # Extract links from this file
                links = extract_links_from_file(file_path)
                all_links.extend(links)
                
                # Check each link
                for text, url, source in links:
                    resolved_path, anchor = resolve_link(url, source)
                    
                    # Check if target exists
                    if not check_file_exists(resolved_path):
                        broken_links.append({
                            'source': source,
                            'text': text,
                            'url': url,
                            'resolved': resolved_path,
                            'anchor': anchor
                        })
    
    return broken_links, all_links, file_count

def main():
    """Main function to run link validation."""
    print("🔍 Validating internal links in documentation...")
    print("-" * 60)
    
    broken_links, all_links, file_count = validate_links()
    
    print(f"📊 Summary:")
    print(f"   Files scanned: {file_count}")
    print(f"   Total internal links: {len(all_links)}")
    print(f"   Broken links: {len(broken_links)}")
    print()
    
    if broken_links:
        print("❌ Broken links found:")
        print("-" * 60)
        
        # Group by source file
        by_source = defaultdict(list)
        for link in broken_links:
            by_source[link['source']].append(link)
        
        for source, links in sorted(by_source.items()):
            print(f"\n📄 {source}:")
            for link in links:
                print(f"   ❌ [{link['text']}]({link['url']})")
                print(f"      Resolved to: {link['resolved']}")
                if link['anchor']:
                    print(f"      Anchor: #{link['anchor']}")
        
        print("\n" + "-" * 60)
        print(f"❌ Total broken links: {len(broken_links)}")
        sys.exit(1)
    else:
        print("✅ All internal links are valid!")
        sys.exit(0)

if __name__ == "__main__":
    main()
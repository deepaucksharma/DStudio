#!/usr/bin/env python3
"""
Validate all internal links in DStudio documentation
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json

# Base directory
DOCS_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).joinpath('docs')

def extract_all_links(content, file_path):
    """Extract all internal links from markdown content"""
    links = []
    
    # Find all markdown links
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(link_pattern, content)
    
    for link_text, link_url in matches:
        # Skip external links
        if link_url.startswith('http'):
            continue
            
        # Skip anchors
        if link_url.startswith('#'):
            continue
            
        links.append({
            'text': link_text,
            'url': link_url,
            'file': str(file_path.relative_to(DOCS_DIR))
        })
    
    return links

def resolve_link(link_url, source_file):
    """Resolve a relative link to an absolute path"""
    source_path = Path(source_file)
    
    # Remove anchor if present
    if '#' in link_url:
        link_url = link_url.split('#')[0]
        if not link_url:  # Pure anchor link
            return source_path  # Return the source file itself
    
    if link_url.startswith('../'):
        # Count parent traversals
        parent_count = link_url.count('../')
        base_path = source_path.parent
        for _ in range(parent_count):
            base_path = base_path.parent
        relative_path = link_url.replace('../', '')
        return base_path / relative_path
    else:
        return source_path.parent / link_url

def validate_links():
    """Validate all links in the documentation"""
    all_links = []
    broken_links = []
    
    # Collect all markdown files
    md_files = list(DOCS_DIR.rglob("*.md"))
    print(f"📄 Found {len(md_files)} markdown files")
    
    # Extract all links
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_links = extract_all_links(content, md_file)
            all_links.extend(file_links)
        except Exception as e:
            print(f"⚠️  Error reading {md_file}: {e}")
    
    print(f"🔗 Found {len(all_links)} internal links")
    
    # Validate each link
    for link in all_links:
        source_file = DOCS_DIR / link['file']
        target_path = resolve_link(link['url'], source_file)
        
        if not target_path.exists():
            try:
                expected_path = str(target_path.relative_to(DOCS_DIR))
            except ValueError:
                # Path is outside docs directory
                expected_path = str(target_path)
            
            broken_links.append({
                'source': link['file'],
                'text': link['text'],
                'url': link['url'],
                'expected_path': expected_path
            })
    
    return broken_links

def generate_report(broken_links):
    """Generate a detailed report of broken links"""
    print(f"\n❌ Found {len(broken_links)} broken links")
    
    # Group by source file
    by_source = defaultdict(list)
    for link in broken_links:
        by_source[link['source']].append(link)
    
    # Group by target URL
    by_target = defaultdict(list)
    for link in broken_links:
        by_target[link['url']].append(link['source'])
    
    # Write detailed report
    with open(DOCS_DIR.parent / 'broken_links_report.json', 'w') as f:
        json.dump({
            'total_broken': len(broken_links),
            'by_source_file': dict(by_source),
            'by_target_url': dict(by_target),
            'all_broken_links': broken_links
        }, f, indent=2)
    
    print("\n📊 Top 10 most referenced broken links:")
    for url, sources in sorted(by_target.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"  - {url} (referenced in {len(sources)} files)")
    
    print("\n📁 Top 10 files with most broken links:")
    for source, links in sorted(by_source.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"  - {source} ({len(links)} broken links)")
    
    print("\n📝 Full report saved to: broken_links_report.json")
    
    return by_target

def suggest_fixes(by_target):
    """Suggest fixes for common broken link patterns"""
    print("\n💡 Suggested fixes:")
    
    suggestions = []
    
    for url, sources in by_target.items():
        # Check for common patterns
        if 'index.md' in url and url.endswith('/index.md'):
            base_name = url.replace('/index.md', '.md')
            suggestions.append(f"  '{url}': '{base_name}',  # Used in {len(sources)} files")
        
        elif url.endswith('.md'):
            # Check if it's a misnamed file
            parts = url.split('/')
            filename = parts[-1]
            
            # Common renames
            if 'theory' in filename:
                new_name = filename.replace('theory', 'models')
                suggestions.append(f"  '{url}': '{'/'.join(parts[:-1])}/{new_name}',  # Used in {len(sources)} files")
            
            if 'queueing' in filename and 'models' not in filename:
                suggestions.append(f"  '{url}': '{url.replace('.md', '-models.md')}',  # Used in {len(sources)} files")
    
    if suggestions:
        print("\nAdd these to LINK_FIXES in fix_broken_links.py:")
        for s in suggestions[:20]:  # Limit to 20 suggestions
            print(s)

def main():
    """Main validation function"""
    print("🔍 Validating all links in DStudio documentation...\n")
    
    broken_links = validate_links()
    
    if broken_links:
        by_target = generate_report(broken_links)
        suggest_fixes(by_target)
    else:
        print("\n✅ All links are valid!")

if __name__ == "__main__":
    main()
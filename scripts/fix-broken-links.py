#!/usr/bin/env python3
"""
Script to fix broken internal links in markdown files.
"""

import os
import re
from pathlib import Path
import sys

def find_best_match(broken_link, existing_files):
    """Find the best matching file for a broken link."""
    # Extract the base name from the broken link
    base_name = os.path.basename(broken_link).replace('.md', '').replace('/index.md', '')
    
    # Look for exact matches first
    for file in existing_files:
        if base_name in os.path.basename(file) and file.endswith('.md'):
            return file
    
    # If no exact match, look for similar names
    for file in existing_files:
        file_base = os.path.basename(file).replace('.md', '')
        if file_base in base_name or base_name in file_base:
            return file
    
    return None

def get_all_markdown_files():
    """Get all markdown files in the docs directory."""
    files = []
    for root, dirs, filenames in os.walk('docs'):
        for filename in filenames:
            if filename.endswith('.md'):
                files.append(os.path.join(root, filename))
    return files

def fix_link(original_url, source_file, target_file):
    """Convert a broken link to a working relative link."""
    # Remove 'docs/' prefix from paths for calculation
    source_dir = os.path.dirname(source_file.replace('docs/', ''))
    target_path = target_file.replace('docs/', '')
    
    # Calculate relative path
    rel_path = os.path.relpath(target_path, source_dir)
    
    # Clean up the path
    if rel_path.endswith('/index.md'):
        # For index files, link to directory
        rel_path = rel_path.replace('/index.md', '/')
    elif rel_path.endswith('.md'):
        # Remove .md extension
        rel_path = rel_path[:-3]
    
    return rel_path

def process_file(file_path, fixes):
    """Process a single file and apply fixes."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Sort fixes by position in reverse order to avoid offset issues
    sorted_fixes = sorted(fixes, key=lambda x: x['position'], reverse=True)
    
    for fix in sorted_fixes:
        old_link = fix['old_link']
        new_link = fix['new_link']
        
        # Find and replace the link
        pattern = r'\[([^\]]+)\]\(' + re.escape(old_link) + r'\)'
        replacement = f'[\\1]({new_link})'
        
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            changes_made += 1
    
    if changes_made > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes_made
    
    return 0

def main():
    """Main function to fix broken links."""
    print("Fixing broken links in markdown files...")
    print("-" * 80)
    
    # Get all existing markdown files
    existing_files = get_all_markdown_files()
    
    # Common link fixes based on patterns
    link_fixes = {
        # Pattern fixes for directories that should point to index.md
        '/patterns/circuit-breaker/': '/patterns/circuit-breaker',
        '/patterns/consistent-hashing/': '/patterns/consistent-hashing',
        '/patterns/quorum-consensus/': '/patterns/consensus',
        '/patterns/anti-entropy/': '/patterns/anti-entropy',
        '/case-studies/amazon-dynamo/': '/case-studies/amazon-dynamo',
        '/case-studies/uber-location/': '/case-studies/uber-location',
        '/case-studies/spotify-recommendations/': '/case-studies/spotify-recommendations',
        '/case-studies/paypal-payments/': '/case-studies/paypal-payments',
        '/patterns/lsm-tree/': '/patterns/lsm-tree',
        '/patterns/bloom-filter/': '/patterns/bloom-filter',
        '/patterns/nosql-patterns/': '/patterns/polyglot-persistence',
        '/patterns/time-series-db/': '/patterns/time-series-ids',
        '/patterns/multi-region/': '/patterns/multi-region',
        '/patterns/database-internals/': '/patterns/lsm-tree',
        '/learning-paths/new-graduate/': '/learning-paths/new-graduate',
        '/learning-paths/mid-level/': '/learning-paths/senior-engineer',
        '/learning-paths/senior/': '/learning-paths/architect',
        '/learning-paths/manager/': '/learning-paths/manager',
        '/patterns/pacelc/': '/quantitative/cap-theorem',
        '/part1-axioms/distributed-knowledge/': '/part1-axioms/law5-epistemology',
        '/patterns/circuit-breaker': '/patterns/circuit-breaker',
        '/patterns/quorum.md': '/patterns/consensus',
        '/case-studies/redis-cluster.md': '/case-studies/redis',
        '/case-studies/netflix-scale.md': '/case-studies/netflix-chaos',
        '/case-studies/discord-messages.md': '/case-studies/chat-system',
        '/case-studies/scylladb.md': '/case-studies/cassandra',
    }
    
    files_fixed = 0
    total_fixes = 0
    
    # Process each markdown file
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                fixes_for_file = []
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find all links in the file
                    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                    
                    for match in re.finditer(link_pattern, content):
                        link_text = match.group(1)
                        link_url = match.group(2)
                        position = match.start()
                        
                        # Skip external links
                        if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                            continue
                        
                        # Check if this link needs fixing
                        fixed_url = None
                        
                        # Try pattern-based fixes first
                        for pattern, replacement in link_fixes.items():
                            if pattern in link_url:
                                fixed_url = link_url.replace(pattern, replacement)
                                break
                        
                        if fixed_url and fixed_url != link_url:
                            fixes_for_file.append({
                                'position': position,
                                'old_link': link_url,
                                'new_link': fixed_url
                            })
                    
                    # Apply fixes to the file
                    if fixes_for_file:
                        num_fixes = process_file(file_path, fixes_for_file)
                        if num_fixes > 0:
                            files_fixed += 1
                            total_fixes += num_fixes
                            print(f"Fixed {num_fixes} links in {file_path}")
                
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    print("\n" + "=" * 80)
    print(f"Summary: Fixed {total_fixes} links in {files_fixed} files")
    
    # Run verification again
    print("\nRunning verification to check remaining broken links...")
    os.system("python3 scripts/verify-links.py")

if __name__ == "__main__":
    main()
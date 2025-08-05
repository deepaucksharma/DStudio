#!/usr/bin/env python3
"""Fix broken links from MkDocs perspective - ensure all internal links work."""

import re
from pathlib import Path
from typing import Set, Dict, Tuple

def get_all_markdown_files() -> Dict[str, Path]:
    """Get all markdown files mapped by their relative path from docs/."""
    docs_dir = Path("docs")
    files = {}
    
    for md_file in docs_dir.glob("**/*.md"):
        rel_path = md_file.relative_to(docs_dir)
        # Store both with and without .md extension
        files[str(rel_path)] = md_file
        files[str(rel_path.with_suffix(''))] = md_file
        
        # Also store by stem for pattern references
        files[md_file.stem] = md_file
        
    return files

def fix_link_in_content(link: str, current_file: Path, all_files: Dict[str, Path]) -> str:
    """Fix a single link to make it work in MkDocs."""
    original_link = link
    
    # Skip external links, anchors, and already working links
    if link.startswith(('http://', 'https://', 'mailto:', '#', '/')):
        return link
    
    # Remove any trailing slash
    link = link.rstrip('/')
    
    # Handle special cases
    if link == '../pattern-library':
        return '/pattern-library/'
    
    if link == '../../../company-specific':
        return '/company-specific/'
    
    # Calculate the correct relative path
    current_dir = current_file.parent
    
    # Resolve the link relative to current directory
    if link.startswith('../'):
        # Count how many levels up
        parts = link.split('/')
        up_levels = 0
        for part in parts:
            if part == '..':
                up_levels += 1
            else:
                break
        
        # Go up the required levels
        target_dir = current_dir
        for _ in range(up_levels):
            if target_dir.parent != target_dir:  # Not at root
                target_dir = target_dir.parent
        
        # Get the rest of the path
        rest_path = '/'.join(parts[up_levels:])
        if rest_path:
            target_path = target_dir / rest_path
        else:
            target_path = target_dir
        
        # Make it relative to docs/
        try:
            rel_to_docs = target_path.relative_to(Path("docs"))
            
            # Check if this file exists
            possible_files = [
                str(rel_to_docs) + '.md',
                str(rel_to_docs) + '/index.md',
                str(rel_to_docs)
            ]
            
            for possible in possible_files:
                if possible in all_files:
                    # Return as absolute path for MkDocs
                    return '/' + possible.replace('.md', '/')
            
            # If it's a directory reference, add trailing slash
            if (Path("docs") / rel_to_docs).is_dir():
                return '/' + str(rel_to_docs) + '/'
                
        except ValueError:
            # Path is outside docs directory
            pass
    
    # For non-relative links, try to find the file
    possible_matches = []
    for file_key in all_files:
        if link in file_key or file_key.endswith(link):
            possible_matches.append(file_key)
    
    if possible_matches:
        # Use the shortest match (most specific)
        best_match = min(possible_matches, key=len)
        return '/' + best_match.replace('.md', '/')
    
    # Return original if we can't fix it
    return original_link

def fix_links_in_file(file_path: Path, all_files: Dict[str, Path]) -> int:
    """Fix all links in a single file."""
    content = file_path.read_text()
    original_content = content
    
    # Find all markdown links
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    def replace_link(match):
        text = match.group(1)
        link = match.group(2)
        
        # Split link and anchor if present
        if '#' in link and not link.startswith('#'):
            link_part, anchor = link.split('#', 1)
            fixed_link = fix_link_in_content(link_part, file_path, all_files)
            if fixed_link != link_part:
                return f'[{text}]({fixed_link}#{anchor})'
        else:
            fixed_link = fix_link_in_content(link, file_path, all_files)
            if fixed_link != link:
                return f'[{text}]({fixed_link})'
        
        return match.group(0)
    
    content = re.sub(link_pattern, replace_link, content)
    
    if content != original_content:
        file_path.write_text(content)
        return 1
    return 0

def main():
    """Fix all broken links for MkDocs."""
    docs_dir = Path("docs")
    
    # Get all markdown files
    all_files = get_all_markdown_files()
    print(f"Found {len(all_files)} markdown file references")
    
    # Fix links in all files
    fixed_count = 0
    for md_file in docs_dir.glob("**/*.md"):
        if fix_links_in_file(md_file, all_files):
            fixed_count += 1
            print(f"Fixed links in: {md_file.relative_to(docs_dir)}")
    
    print(f"\nTotal files with fixed links: {fixed_count}")
    
    # Create missing directories that are referenced
    missing_dirs = set()
    for md_file in docs_dir.glob("**/*.md"):
        content = md_file.read_text()
        # Find directory references
        for match in re.finditer(r'\]\(/([^)]+)/\)', content):
            dir_path = match.group(1)
            full_path = docs_dir / dir_path
            if not full_path.exists():
                missing_dirs.add(dir_path)
    
    if missing_dirs:
        print(f"\nCreating {len(missing_dirs)} missing directories:")
        for dir_path in sorted(missing_dirs):
            full_path = docs_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            # Create index.md if it doesn't exist
            index_file = full_path / "index.md"
            if not index_file.exists():
                title = dir_path.split('/')[-1].replace('-', ' ').title()
                index_file.write_text(f"""# {title}

> **Note**: This section is under construction.

## Overview

Coming soon.
""")
                print(f"  - Created {dir_path}/index.md")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Check for broken internal links in markdown files.
"""

import os
import sys
import re
from pathlib import Path

def resolve_path(source_file, link):
    """Resolve relative links to absolute paths"""
    if link.startswith('/'):
        return Path('docs') / link[1:]
    else:
        source_dir = source_file.parent
        return (source_dir / link).resolve()

def check_link_exists(resolved_path):
    """Check if a link target exists"""
    # Try as-is
    if resolved_path.exists():
        return True
    
    # Try adding .md extension
    if not str(resolved_path).endswith('.md'):
        md_path = Path(str(resolved_path) + '.md')
        if md_path.exists():
            return True
    
    # Try as directory with index.md
    index_path = resolved_path / 'index.md'
    if index_path.exists():
        return True
    
    return False

def validate_links(filepath):
    """Validate links in a single file"""
    errors = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find markdown links
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    for match in link_pattern.finditer(content):
        link_text = match.group(1)
        link_url = match.group(2)
        
        # Skip external links and anchors
        if link_url.startswith(('http', 'https', '#', 'mailto:')):
            continue
        
        # Remove anchor from link
        if '#' in link_url:
            link_url = link_url.split('#')[0]
        
        # Skip empty links
        if not link_url:
            continue
        
        # Resolve the link
        try:
            resolved_path = resolve_path(Path(filepath), link_url)
            
            # Check if file exists
            if not check_link_exists(resolved_path):
                errors.append(f"{filepath}: Broken link '{link_url}' (text: '{link_text}')")
        except Exception as e:
            errors.append(f"{filepath}: Error resolving link '{link_url}': {e}")
    
    return errors

def main():
    """Main validation function"""
    errors = []
    
    # Get all markdown files
    docs_dir = Path('docs')
    total_files = 0
    
    for md_file in docs_dir.rglob('*.md'):
        total_files += 1
        file_errors = validate_links(md_file)
        errors.extend(file_errors)
    
    # Report results
    print(f"Checked {total_files} files")
    if errors:
        print(f"\n❌ Found {len(errors)} broken links:\n")
        for error in errors[:100]:  # Limit output
            print(f"  - {error}")
        if len(errors) > 100:
            print(f"  ... and {len(errors) - 100} more")
        sys.exit(1)
    else:
        print("✅ All internal links validated!")

if __name__ == '__main__':
    main()
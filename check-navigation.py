#!/usr/bin/env python3
"""
Check navigation consistency - verify all files in mkdocs.yml exist
"""

import re
from pathlib import Path

def extract_md_files_from_nav(mkdocs_content):
    """Extract all .md file references from navigation"""
    # Find all lines that contain .md files
    md_files = []
    lines = mkdocs_content.split('\n')
    
    for line in lines:
        # Look for patterns like "- Name: path/to/file.md"
        match = re.search(r':\s*([^\s]+\.md)', line)
        if match:
            md_files.append(match.group(1))
    
    return md_files

def check_files_exist(md_files, docs_dir='docs'):
    """Check which files exist and which are missing"""
    docs_path = Path(docs_dir)
    missing = []
    existing = []
    
    for file in md_files:
        full_path = docs_path / file
        if full_path.exists():
            existing.append(file)
        else:
            missing.append(file)
    
    return existing, missing

def main():
    # Read mkdocs.yml
    with open('mkdocs.yml', 'r') as f:
        content = f.read()
    
    # Extract navigation section
    nav_start = content.find('nav:')
    if nav_start == -1:
        print("No navigation section found")
        return
    
    # Get content from nav: to the next top-level section
    nav_content = content[nav_start:]
    next_section = re.search(r'\n\w+:', nav_content[4:])
    if next_section:
        nav_content = nav_content[:next_section.start() + 4]
    
    # Extract .md files
    md_files = extract_md_files_from_nav(nav_content)
    md_files = list(set(md_files))  # Remove duplicates
    
    print(f"Found {len(md_files)} unique .md files in navigation")
    
    # Check existence
    existing, missing = check_files_exist(md_files)
    
    print(f"\n✅ Existing files: {len(existing)}")
    print(f"❌ Missing files: {len(missing)}")
    
    if missing:
        print("\nMissing files:")
        for file in sorted(missing):
            print(f"  - {file}")
            
    # Group missing by section
    if missing:
        print("\nMissing by section:")
        sections = {}
        for file in missing:
            section = file.split('/')[0] if '/' in file else 'root'
            if section not in sections:
                sections[section] = []
            sections[section].append(file)
        
        for section, files in sorted(sections.items()):
            print(f"\n{section}:")
            for file in sorted(files):
                print(f"  - {file}")

if __name__ == '__main__':
    main()
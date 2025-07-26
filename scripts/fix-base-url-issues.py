#!/usr/bin/env python3
"""
Fix base URL issues where links are missing the /DStudio path
"""

import os
import re
from pathlib import Path

def fix_base_url_issues(root_dir: Path):
    """Fix links that might be missing the /DStudio base path"""
    
    fixes_made = 0
    files_modified = set()
    
    # Pattern to find links that start with / but not /DStudio
    # This will catch links like [text](/patterns/...) that should be relative
    absolute_link_pattern = re.compile(r'\[([^\]]+)\]\((/(?!DStudio/)[^)]+)\)')
    
    for md_file in root_dir.rglob("*.md"):
        if '.venv' in str(md_file) or 'site/' in str(md_file):
            continue
            
        try:
            content = md_file.read_text(encoding='utf-8')
            original_content = content
            
            # Find all absolute links that don't include /DStudio
            matches = list(absolute_link_pattern.finditer(content))
            
            if matches:
                print(f"\nProcessing {md_file.relative_to(root_dir)}:")
                
                for match in reversed(matches):  # Process in reverse to maintain positions
                    link_text = match.group(1)
                    link_url = match.group(2)
                    
                    # Convert absolute path to relative
                    # Remove leading slash to make it relative
                    relative_url = link_url.lstrip('/')
                    
                    # For patterns, ensure they don't have trailing slashes
                    if relative_url.startswith('patterns/') and relative_url.endswith('/'):
                        relative_url = relative_url.rstrip('/')
                    
                    new_link = f"[{link_text}]({relative_url})"
                    old_link = match.group(0)
                    
                    print(f"  - {old_link} -> {new_link}")
                    
                    # Replace in content
                    content = content[:match.start()] + new_link + content[match.end():]
                    fixes_made += 1
                
                if content != original_content:
                    md_file.write_text(content, encoding='utf-8')
                    files_modified.add(str(md_file.relative_to(root_dir)))
                    
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return fixes_made, files_modified


def check_for_hardcoded_urls(root_dir: Path):
    """Check for any hardcoded GitHub Pages URLs"""
    
    hardcoded_pattern = re.compile(r'https://deepaucksharma\.github\.io/(?!DStudio/)')
    
    for md_file in root_dir.rglob("*.md"):
        if '.venv' in str(md_file) or 'site/' in str(md_file):
            continue
            
        try:
            content = md_file.read_text(encoding='utf-8')
            matches = list(hardcoded_pattern.finditer(content))
            
            if matches:
                print(f"\nHardcoded URLs found in {md_file.relative_to(root_dir)}:")
                for match in matches:
                    # Get surrounding context
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end].replace('\n', ' ')
                    print(f"  ...{context}...")
                    
        except Exception as e:
            print(f"Error checking {md_file}: {e}")


def main():
    root_dir = Path('/home/deepak/DStudio')
    docs_dir = root_dir / 'docs'
    
    print("Checking for hardcoded GitHub Pages URLs...")
    check_for_hardcoded_urls(docs_dir)
    
    print("\n" + "="*80)
    print("Fixing base URL issues in links...")
    print("="*80)
    
    fixes_made, files_modified = fix_base_url_issues(docs_dir)
    
    print(f"\n{'='*80}")
    print(f"Summary:")
    print(f"  Total fixes made: {fixes_made}")
    print(f"  Files modified: {len(files_modified)}")
    
    if files_modified:
        print(f"\nModified files:")
        for file in sorted(files_modified):
            print(f"  - {file}")


if __name__ == "__main__":
    main()
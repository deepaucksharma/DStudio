#!/usr/bin/env python3
"""Fix frontmatter key consistency - convert hyphens to underscores."""

import os
import re
import yaml
from pathlib import Path

def fix_frontmatter_keys(filepath):
    """Fix frontmatter keys to use underscores instead of hyphens."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has frontmatter
    if not content.startswith('---'):
        return False
    
    # Extract frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return False
    
    frontmatter_text = fm_match.group(1)
    remaining_content = content[fm_match.end():]
    
    try:
        # Parse frontmatter
        frontmatter = yaml.safe_load(frontmatter_text)
        if not frontmatter:
            return False
        
        # Check if any keys need fixing
        needs_fix = False
        fixed_frontmatter = {}
        
        for key, value in frontmatter.items():
            if '-' in str(key):
                new_key = key.replace('-', '_')
                fixed_frontmatter[new_key] = value
                needs_fix = True
                print(f"  Fixing key: '{key}' -> '{new_key}' in {filepath}")
            else:
                fixed_frontmatter[key] = value
        
        if not needs_fix:
            return False
        
        # Rebuild the file content
        new_content = "---\n"
        
        # Preserve key order for common fields
        key_order = ['title', 'description', 'type', 'difficulty', 'reading_time', 
                     'excellence_tier', 'pattern_status', 'best_for', 'introduced', 
                     'current_relevance', 'tags', 'related_laws', 'related_patterns']
        
        # Write ordered keys first
        for key in key_order:
            if key in fixed_frontmatter:
                value = fixed_frontmatter[key]
                if isinstance(value, list):
                    new_content += f"{key}:\n"
                    for item in value:
                        new_content += f"  - {item}\n"
                elif isinstance(value, dict):
                    new_content += f"{key}:\n"
                    for k, v in value.items():
                        new_content += f"  {k}: {v}\n"
                else:
                    new_content += f"{key}: {value}\n"
        
        # Write remaining keys
        for key, value in fixed_frontmatter.items():
            if key not in key_order:
                if isinstance(value, list):
                    new_content += f"{key}:\n"
                    for item in value:
                        new_content += f"  - {item}\n"
                elif isinstance(value, dict):
                    new_content += f"{key}:\n"
                    for k, v in value.items():
                        new_content += f"  {k}: {v}\n"
                else:
                    new_content += f"{key}: {value}\n"
        
        new_content += "---"
        new_content += remaining_content
        
        # Write updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except yaml.YAMLError as e:
        print(f"  Error parsing YAML in {filepath}: {e}")
        return False

def main():
    """Fix frontmatter consistency across all markdown files."""
    docs_dir = Path('docs')
    updated = 0
    skipped = 0
    errors = 0
    
    print("Fixing frontmatter key consistency (hyphens to underscores)...\n")
    
    for md_file in docs_dir.rglob('*.md'):
        try:
            if fix_frontmatter_keys(md_file):
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  Error processing {md_file}: {e}")
            errors += 1
    
    print(f"\n📊 Summary:")
    print(f"  - Files updated: {updated}")
    print(f"  - Files skipped: {skipped}")
    print(f"  - Errors: {errors}")

if __name__ == '__main__':
    main()
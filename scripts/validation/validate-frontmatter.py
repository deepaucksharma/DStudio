#!/usr/bin/env python3
"""
Validate frontmatter consistency across all markdown files.
Ensures consistent formatting and required fields.
"""

import os
import sys
import yaml
import re
from pathlib import Path

def validate_frontmatter(filepath):
    """Validate a single file's frontmatter"""
    errors = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has frontmatter
    if not content.startswith('---'):
        # Some files legitimately don't need frontmatter
        if 'index.md' not in str(filepath) and 'README' not in str(filepath):
            errors.append(f"{filepath}: Missing frontmatter")
        return errors
    
    # Extract frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        errors.append(f"{filepath}: Invalid frontmatter format")
        return errors
    
    try:
        frontmatter = yaml.safe_load(fm_match.group(1))
        if not frontmatter:
            errors.append(f"{filepath}: Empty frontmatter")
            return errors
    except yaml.YAMLError as e:
        errors.append(f"{filepath}: YAML parse error - {e}")
        return errors
    
    # Check for consistent key format (prefer underscores)
    for key in frontmatter.keys():
        if '-' in str(key):
            errors.append(f"{filepath}: Use underscores instead of hyphens in key '{key}'")
    
    # Validate required fields based on document type
    doc_type = frontmatter.get('type', '')
    
    required_fields = {
        'pattern': ['title', 'excellence_tier', 'pattern_status'],
        'law': ['title', 'type', 'difficulty', 'reading_time'],
        'pillar': ['title', 'type', 'difficulty', 'reading_time'],
        'case-study': ['title', 'type', 'difficulty'],
        'learning-path': ['title', 'description', 'type']
    }
    
    if doc_type in required_fields:
        for field in required_fields[doc_type]:
            if field not in frontmatter:
                errors.append(f"{filepath}: Missing required field '{field}' for type '{doc_type}'")
    
    # Validate excellence_tier values
    if 'excellence_tier' in frontmatter:
        valid_tiers = ['gold', 'silver', 'bronze']
        if frontmatter['excellence_tier'] not in valid_tiers:
            errors.append(f"{filepath}: Invalid excellence_tier '{frontmatter['excellence_tier']}' (must be: {', '.join(valid_tiers)})")
    
    # Validate pattern_status values
    if 'pattern_status' in frontmatter:
        valid_statuses = ['recommended', 'use-with-expertise', 'use-with-caution', 'legacy']
        if frontmatter['pattern_status'] not in valid_statuses:
            errors.append(f"{filepath}: Invalid pattern_status '{frontmatter['pattern_status']}'")
    
    return errors

def main():
    """Main validation function"""
    errors = []
    
    # Get all markdown files
    docs_dir = Path('docs')
    for md_file in docs_dir.rglob('*.md'):
        file_errors = validate_frontmatter(md_file)
        errors.extend(file_errors)
    
    # Report results
    if errors:
        print(f"❌ Found {len(errors)} frontmatter validation errors:\n")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ All frontmatter validation passed!")

if __name__ == '__main__':
    main()
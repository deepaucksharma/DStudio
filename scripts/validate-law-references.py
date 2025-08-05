#!/usr/bin/env python3
"""
Validate law references to ensure they use correct naming.
"""

import os
import sys
import yaml
import re
from pathlib import Path

# Valid law names (based on actual file names)
VALID_LAWS = [
    'correlated-failure',
    'asynchronous-reality',
    'emergent-chaos',
    'multidimensional-optimization',
    'distributed-knowledge',
    'cognitive-load',
    'economic-reality'
]

# Old law patterns that should not be used
OLD_LAW_PATTERNS = {
    'law1-failure': 'correlated-failure',
    'law2-asynchrony': 'asynchronous-reality',
    'law2-asynchronous': 'asynchronous-reality',
    'law3-emergence': 'emergent-chaos',
    'law4-tradeoffs': 'multidimensional-optimization',
    'law4-trade-offs': 'multidimensional-optimization',
    'law5-epistemology': 'distributed-knowledge',
    'law6-human-api': 'cognitive-load',
    'law7-economics': 'economic-reality',
    'part1-axioms': 'core-principles/laws',
    'axioms': 'laws'
}

def check_frontmatter_laws(frontmatter, filepath):
    """Check law references in frontmatter"""
    errors = []
    
    if 'related_laws' in frontmatter and frontmatter['related_laws']:
        for law in frontmatter['related_laws']:
            if law and law not in VALID_LAWS:
                # Check if it's an old pattern
                suggestion = OLD_LAW_PATTERNS.get(law, None)
                if suggestion:
                    errors.append(f"{filepath}: Old law reference '{law}' should be '{suggestion}'")
                else:
                    errors.append(f"{filepath}: Invalid law reference '{law}'")
    
    return errors

def check_content_laws(content, filepath):
    """Check law references in content"""
    errors = []
    
    # Check for old law patterns in links and text
    for old_pattern, new_pattern in OLD_LAW_PATTERNS.items():
        # Check in markdown links
        pattern = rf'\[([^\]]*)\]\([^)]*{re.escape(old_pattern)}[^)]*\)'
        if re.search(pattern, content):
            errors.append(f"{filepath}: Found old law reference '{old_pattern}' in link (should be '{new_pattern}')")
        
        # Check in text references
        if old_pattern in content:
            # Avoid duplicate reporting if already found in link
            if not any(old_pattern in error for error in errors):
                errors.append(f"{filepath}: Found old law reference '{old_pattern}' in text")
    
    # Check for incorrect paths
    if '/core-principles/axioms/' in content:
        errors.append(f"{filepath}: Found old path '/core-principles/axioms/' (should be '/core-principles/laws/')")
    
    if 'part1-axioms' in content:
        errors.append(f"{filepath}: Found old path 'part1-axioms' (should be 'core-principles/laws')")
    
    return errors

def validate_law_references(filepath):
    """Validate law references in a single file"""
    errors = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check frontmatter
    if content.startswith('---'):
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            try:
                frontmatter = yaml.safe_load(fm_match.group(1))
                if frontmatter:
                    errors.extend(check_frontmatter_laws(frontmatter, filepath))
            except yaml.YAMLError:
                pass  # Frontmatter errors handled by other validator
    
    # Check content
    errors.extend(check_content_laws(content, filepath))
    
    return errors

def main():
    """Main validation function"""
    errors = []
    
    # Get all markdown files
    docs_dir = Path('docs')
    for md_file in docs_dir.rglob('*.md'):
        file_errors = validate_law_references(md_file)
        errors.extend(file_errors)
    
    # Report results
    if errors:
        print(f"❌ Found {len(errors)} law reference errors:\n")
        for error in errors[:50]:  # Limit output
            print(f"  - {error}")
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more")
        sys.exit(1)
    else:
        print("✅ All law references validated!")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Validate path consistency across all markdown files.
Ensures all internal paths follow the correct structure.
"""

import os
import sys
import re
from pathlib import Path

# Path patterns to check
PATH_ISSUES = [
    # (old_pattern, correct_pattern, description)
    (r'\.\./patterns/', '../pattern-library/', 'pattern path'),
    (r'/core-principles/axioms/', '/core-principles/laws/', 'axiom path'),
    (r'/core-principles/pillars/work/index', '/core-principles/pillars/work-distribution', 'pillar path'),
    (r'/core-principles/pillars/state/index', '/core-principles/pillars/state-distribution', 'pillar path'),
    (r'/core-principles/pillars/truth/index', '/core-principles/pillars/truth-distribution', 'pillar path'),
    (r'/core-principles/pillars/control/index', '/core-principles/pillars/control-distribution', 'pillar path'),
    (r'/core-principles/pillars/intelligence/index', '/core-principles/pillars/intelligence-distribution', 'pillar path'),
    (r'\.\./quantitative/', '../quantitative-analysis/', 'quantitative path'),
    (r'/part1-axioms/', '/core-principles/laws/', 'old axioms path'),
    (r'/part2-pillars/', '/core-principles/pillars/', 'old pillars path'),
    (r'pattern-library/index\.md#', 'patterns/#', 'pattern discovery tool path'),
]

def validate_paths(filepath):
    """Validate paths in a single file"""
    errors = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old_pattern, correct_pattern, desc in PATH_ISSUES:
        matches = re.findall(old_pattern, content, re.IGNORECASE)
        if matches:
            errors.append(f"{filepath}: Found {len(matches)} instances of old {desc} '{old_pattern}' (should be '{correct_pattern}')")
    
    # Check for pillar path confusion
    pillar_paths = {
        '/pillars/work/': '/pillars/work-distribution/',
        '/pillars/state/': '/pillars/state-distribution/',
        '/pillars/truth/': '/pillars/truth-distribution/',
        '/pillars/control/': '/pillars/control-distribution/',
        '/pillars/intelligence/': '/pillars/intelligence-distribution/',
    }
    
    for wrong, correct in pillar_paths.items():
        if wrong in content:
            errors.append(f"{filepath}: Found incorrect pillar path '{wrong}' (should be '{correct}')")
    
    return errors

def main():
    """Main validation function"""
    errors = []
    
    # Get all markdown files
    docs_dir = Path('docs')
    for md_file in docs_dir.rglob('*.md'):
        file_errors = validate_paths(md_file)
        errors.extend(file_errors)
    
    # Report results
    if errors:
        print(f"❌ Found {len(errors)} path consistency errors:\n")
        for error in errors[:50]:  # Limit output
            print(f"  - {error}")
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more")
        sys.exit(1)
    else:
        print("✅ All paths validated!")

if __name__ == '__main__':
    main()
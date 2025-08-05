#!/usr/bin/env python3
"""Fix self-referential links in markdown files."""

import re
from pathlib import Path

def fix_self_referential_links(file_path: Path) -> int:
    """Fix links pointing to index.md#anchor in the same file."""
    content = file_path.read_text()
    original_content = content
    
    # Pattern to match self-referential links like [text](index.md#anchor)
    # when the current file IS index.md
    if file_path.name == 'index.md':
        # Replace index.md#anchor with just #anchor
        content = re.sub(r'\]\(index\.md(#[^)]+)\)', r'](\1)', content)
    
    # Also fix links like ../company-specific/ that should point to a specific file
    # Pattern: ends with just a directory slash
    content = re.sub(r'\]\(\.\./company-specific/\)', r'](../../../company-specific/)', content)
    content = re.sub(r'\]\(\.\./pattern-library/\)', r'](../../../pattern-library/)', content)
    
    if content != original_content:
        file_path.write_text(content)
        return 1
    return 0

def main():
    """Fix self-referential links across the documentation."""
    docs_dir = Path("docs")
    fixed_count = 0
    
    # Focus on interview-prep directory where most issues are
    for md_file in docs_dir.glob("interview-prep/**/*.md"):
        if fix_self_referential_links(md_file):
            fixed_count += 1
            print(f"Fixed: {md_file}")
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
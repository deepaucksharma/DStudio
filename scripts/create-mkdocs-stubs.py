#!/usr/bin/env python3
"""Create stub files for all missing pages referenced in mkdocs.yml navigation."""

import yaml
from pathlib import Path
from typing import Any, List, Dict, Union

class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    """Custom YAML loader that ignores unknown tags."""
    def ignore_unknown(self, node):
        return None

def add_unknown_constructors(loader):
    """Add constructors for unknown tags."""
    yaml.add_constructor(None, loader.ignore_unknown, Loader=loader)

def extract_nav_files(nav_item: Union[str, Dict, List], base_path: Path = Path("docs")) -> List[Path]:
    """Recursively extract all file paths from navigation structure."""
    files = []
    
    if isinstance(nav_item, str):
        # Direct file reference
        if nav_item.endswith('.md'):
            files.append(base_path / nav_item)
    elif isinstance(nav_item, dict):
        # Dictionary with nested items
        for key, value in nav_item.items():
            files.extend(extract_nav_files(value, base_path))
    elif isinstance(nav_item, list):
        # List of items
        for item in nav_item:
            files.extend(extract_nav_files(item, base_path))
    
    return files

def create_stub_content(file_path: Path) -> str:
    """Generate appropriate stub content based on file path."""
    # Extract title from file path
    title = file_path.stem.replace('-', ' ').title()
    if file_path.stem == 'index':
        # Use parent directory name for index files
        title = file_path.parent.name.replace('-', ' ').title()
    
    content = f"""# {title}

> **Note**: This page is under construction and will be completed soon.

## Overview

This section will cover {title.lower()} in detail.

## Topics to be covered

- Key concepts
- Best practices
- Examples and case studies
- Related patterns and resources

## Coming Soon

Check back soon for comprehensive content on this topic.

---

**Related Resources:**
- [Home](/)
- [Pattern Library](/pattern-library/)
- [Core Principles](/core-principles/)
"""
    
    return content

def main():
    """Create stub files for all missing navigation entries."""
    # Load mkdocs.yml
    mkdocs_path = Path("mkdocs.yml")
    
    if not mkdocs_path.exists():
        print("ERROR: mkdocs.yml not found!")
        return
    
    # Set up custom loader
    add_unknown_constructors(SafeLoaderIgnoreUnknown)
    
    with open(mkdocs_path, 'r') as f:
        config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
    
    if 'nav' not in config:
        print("ERROR: No navigation found in mkdocs.yml")
        return
    
    # Extract all file paths from navigation
    nav_files = extract_nav_files(config['nav'])
    
    # Create missing files
    created_count = 0
    for file_path in nav_files:
        if not file_path.exists():
            # Create directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create stub file
            content = create_stub_content(file_path)
            file_path.write_text(content)
            print(f"Created stub: {file_path}")
            created_count += 1
    
    print(f"\nTotal stub files created: {created_count}")
    
    # Also check for orphaned files
    docs_dir = Path("docs")
    all_md_files = set(docs_dir.glob("**/*.md"))
    nav_files_set = set(nav_files)
    orphaned = all_md_files - nav_files_set
    
    if orphaned:
        print(f"\nFound {len(orphaned)} orphaned files not in navigation:")
        for file in sorted(orphaned)[:10]:
            print(f"  - {file.relative_to(docs_dir)}")
        if len(orphaned) > 10:
            print(f"  ... and {len(orphaned) - 10} more")

if __name__ == "__main__":
    main()
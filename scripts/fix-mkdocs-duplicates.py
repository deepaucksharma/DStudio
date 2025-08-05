#!/usr/bin/env python3
"""Fix duplicate entries in MkDocs navigation."""

import yaml
from pathlib import Path
from typing import Any, List, Dict, Union, Set

class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    """Custom YAML loader that ignores unknown tags."""
    def ignore_unknown(self, node):
        return None

def add_unknown_constructors(loader):
    """Add constructors for unknown tags."""
    yaml.add_constructor(None, loader.ignore_unknown, Loader=loader)

def find_duplicates_in_nav(nav_item: Union[str, Dict, List], seen: Set[str] = None, duplicates: List[str] = None, path: str = "") -> List[str]:
    """Recursively find duplicate file references in navigation."""
    if seen is None:
        seen = set()
    if duplicates is None:
        duplicates = []
    
    if isinstance(nav_item, str):
        # Direct file reference
        if nav_item.endswith('.md'):
            if nav_item in seen:
                duplicates.append(f"{path} -> {nav_item}")
            else:
                seen.add(nav_item)
    elif isinstance(nav_item, dict):
        # Dictionary with nested items
        for key, value in nav_item.items():
            find_duplicates_in_nav(value, seen, duplicates, f"{path}/{key}")
    elif isinstance(nav_item, list):
        # List of items
        for i, item in enumerate(nav_item):
            find_duplicates_in_nav(item, seen, duplicates, f"{path}[{i}]")
    
    return duplicates

def remove_duplicate_entries(nav_item: Union[str, Dict, List], seen: Set[str] = None) -> Union[str, Dict, List, None]:
    """Remove duplicate entries from navigation structure."""
    if seen is None:
        seen = set()
    
    if isinstance(nav_item, str):
        # Direct file reference
        if nav_item.endswith('.md'):
            if nav_item in seen:
                return None  # Remove duplicate
            else:
                seen.add(nav_item)
                return nav_item
        return nav_item
    elif isinstance(nav_item, dict):
        # Dictionary with nested items
        new_dict = {}
        for key, value in nav_item.items():
            new_value = remove_duplicate_entries(value, seen)
            if new_value is not None:
                new_dict[key] = new_value
        return new_dict if new_dict else None
    elif isinstance(nav_item, list):
        # List of items
        new_list = []
        for item in nav_item:
            new_item = remove_duplicate_entries(item, seen)
            if new_item is not None:
                new_list.append(new_item)
        return new_list if new_list else None
    
    return nav_item

def main():
    """Fix duplicate entries in mkdocs.yml."""
    mkdocs_path = Path("mkdocs.yml")
    
    if not mkdocs_path.exists():
        print("ERROR: mkdocs.yml not found!")
        return
    
    # Set up custom loader
    add_unknown_constructors(SafeLoaderIgnoreUnknown)
    
    # Load config
    with open(mkdocs_path, 'r') as f:
        config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
    
    if 'nav' not in config:
        print("ERROR: No navigation found in mkdocs.yml")
        return
    
    # Find duplicates
    duplicates = find_duplicates_in_nav(config['nav'])
    
    if duplicates:
        print(f"Found {len(duplicates)} duplicate entries:")
        for dup in duplicates[:10]:
            print(f"  - {dup}")
        if len(duplicates) > 10:
            print(f"  ... and {len(duplicates) - 10} more")
        
        # Remove duplicates
        config['nav'] = remove_duplicate_entries(config['nav'])
        
        # Write back to file
        with open(mkdocs_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        print(f"\nRemoved {len(duplicates)} duplicate entries from mkdocs.yml")
    else:
        print("No duplicate entries found in navigation.")

if __name__ == "__main__":
    main()
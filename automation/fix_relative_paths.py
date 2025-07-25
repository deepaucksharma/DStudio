#!/usr/bin/env python3
"""
Fix relative path issues in MkDocs documentation.
Converts relative paths like ../index.md to absolute paths from /docs root.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime

# Base directory for docs
DOCS_DIR = Path("/home/deepak/DStudio/docs")

# Mapping of common patterns to their absolute equivalents
PATH_MAPPINGS = {
    # Direct mappings for common patterns
    "../introduction/index.md": "/",
    "../../introduction/index.md": "/",
    "../index.md": None,  # Special case - needs context-aware handling
    "../../index.md": None,  # Special case - needs context-aware handling
}

# Directory mappings for context-aware resolution
DIR_MAPPINGS = {
    "introduction": "/",
    "part1-axioms": "/part1-axioms/",
    "part2-pillars": "/part2-pillars/",
    "patterns": "/patterns/",
    "quantitative": "/quantitative/",
    "human-factors": "/human-factors/",
    "case-studies": "/case-studies/",
    "tools": "/tools/",
    "reference": "/reference/",
    "amazon-interviews": "/amazon-interviews/",
    "google-interviews": "/google-interviews/",
}

def backup_file(file_path: Path) -> Path:
    """Create a backup of the file before modifying."""
    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
    shutil.copy2(file_path, backup_path)
    return backup_path

def is_archive_file(file_path: Path) -> bool:
    """Check if a file is in the archive directory."""
    return "archive-old-8-axiom-structure" in str(file_path)

def resolve_relative_path(current_file: Path, relative_path: str) -> str:
    """
    Resolve a relative path to an absolute path from docs root.
    
    Args:
        current_file: Path to the current markdown file
        relative_path: The relative path to resolve (e.g., '../index.md')
    
    Returns:
        Absolute path from docs root (e.g., '/part1-axioms/')
    """
    # Check if it's in our direct mappings
    if relative_path in PATH_MAPPINGS:
        result = PATH_MAPPINGS[relative_path]
        if result is not None:
            return result
    
    # Parse the relative path
    rel_path = Path(relative_path)
    current_dir = current_file.parent
    
    # Handle anchor links
    anchor = ""
    if "#" in relative_path:
        path_part, anchor = relative_path.split("#", 1)
        rel_path = Path(path_part)
        anchor = f"#{anchor}"
    
    # Special handling for archive files - they reference old structure
    if is_archive_file(current_file):
        # For archive files, we need to map to the new structure
        # Most ../../patterns/ should become /patterns/
        # Most ../../quantitative/ should become /quantitative/
        # etc.
        if relative_path.startswith("../../patterns/"):
            return "/patterns/" + relative_path[15:].replace(".md", "")
        elif relative_path.startswith("../../quantitative/"):
            return "/quantitative/" + relative_path[19:].replace(".md", "")
        elif relative_path.startswith("../../case-studies/"):
            return "/case-studies/" + relative_path[19:].replace(".md", "")
        elif relative_path.startswith("../../part2-pillars/"):
            path_part = relative_path[20:]
            if path_part.endswith("/index.md"):
                return "/part2-pillars/" + path_part[:-9] + "/"
            return "/part2-pillars/" + path_part.replace(".md", "")
        elif relative_path == "../../introduction/index.md":
            return "/"
        elif relative_path == "../index.md":
            return "/part1-axioms/"
    
    # Navigate up according to ../ count
    up_count = len([p for p in rel_path.parts if p == ".."])
    target_dir = current_dir
    for _ in range(up_count):
        target_dir = target_dir.parent
    
    # Get the remaining path after ../
    remaining_parts = [p for p in rel_path.parts if p != ".."]
    
    # Build the full target path
    if remaining_parts:
        target_path = target_dir / Path(*remaining_parts)
    else:
        target_path = target_dir
    
    # Make sure the path is within docs directory
    try:
        rel_from_docs = target_path.relative_to(DOCS_DIR)
    except ValueError:
        # Path is outside docs directory, this shouldn't happen
        return relative_path
    
    # Special handling for index.md
    if remaining_parts and remaining_parts[-1] == "index.md":
        # Remove index.md and just use the directory
        if len(remaining_parts) == 1:
            # Just index.md, use the target directory
            path_str = str(rel_from_docs).replace("\\", "/")
        else:
            # Path to a specific directory's index
            parent_path = rel_from_docs.parent
            path_str = str(parent_path).replace("\\", "/")
        
        # Handle special mappings
        if path_str in DIR_MAPPINGS:
            return DIR_MAPPINGS[path_str] + anchor
        elif path_str == ".":
            return "/" + anchor
        else:
            return "/" + path_str + "/" + anchor
    else:
        # Regular file reference
        path_str = str(rel_from_docs).replace("\\", "/")
        
        # Remove .md extension for cleaner URLs
        if path_str.endswith(".md"):
            path_str = path_str[:-3]
        
        return "/" + path_str + anchor

def find_markdown_links(content: str) -> List[Tuple[str, str, int]]:
    """
    Find all markdown links with relative paths.
    
    Returns:
        List of tuples (full_match, path, position)
    """
    # Pattern to match markdown links with relative paths
    pattern = r'\[([^\]]+)\]\((\.\.+/[^)]+)\)'
    
    matches = []
    for match in re.finditer(pattern, content):
        full_match = match.group(0)
        link_text = match.group(1)
        path = match.group(2)
        position = match.start()
        matches.append((full_match, path, position))
    
    return matches

def fix_file(file_path: Path, dry_run: bool = False) -> Dict[str, List[str]]:
    """
    Fix relative paths in a single file.
    
    Returns:
        Dictionary with 'fixed' and 'errors' lists
    """
    results = {'fixed': [], 'errors': [], 'file': str(file_path)}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        matches = find_markdown_links(content)
        
        if not matches:
            return results
        
        # Process matches in reverse order to maintain positions
        for full_match, rel_path, position in reversed(matches):
            try:
                # Extract link text
                link_text = full_match[full_match.find('[')+1:full_match.find(']')]
                
                # Resolve the path
                abs_path = resolve_relative_path(file_path, rel_path)
                
                # Create new link
                new_link = f"[{link_text}]({abs_path})"
                
                # Replace in content
                content = content[:position] + new_link + content[position + len(full_match):]
                
                results['fixed'].append(f"{rel_path} → {abs_path}")
                
            except Exception as e:
                results['errors'].append(f"Error processing {rel_path}: {str(e)}")
        
        # Write the fixed content if not dry run and there were changes
        if content != original_content and not dry_run:
            # Create backup
            backup_file(file_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    except Exception as e:
        results['errors'].append(f"Error processing file: {str(e)}")
    
    return results

def find_all_markdown_files(directory: Path) -> List[Path]:
    """Find all markdown files in the directory recursively."""
    return list(directory.rglob("*.md"))

def main(dry_run: bool = False, specific_files: List[str] = None):
    """
    Main function to fix relative paths in documentation.
    
    Args:
        dry_run: If True, only report what would be changed
        specific_files: List of specific files to process (for testing)
    """
    print(f"{'DRY RUN: ' if dry_run else ''}Fixing relative paths in MkDocs documentation")
    print(f"Docs directory: {DOCS_DIR}")
    print("-" * 60)
    
    # Get files to process
    if specific_files:
        files = [Path(f) for f in specific_files if Path(f).exists()]
    else:
        files = find_all_markdown_files(DOCS_DIR)
    
    total_fixed = 0
    total_errors = 0
    files_modified = 0
    
    # Process each file
    for file_path in sorted(files):
        results = fix_file(file_path, dry_run)
        
        if results['fixed'] or results['errors']:
            rel_path = file_path.relative_to(DOCS_DIR)
            print(f"\n📄 {rel_path}")
            
            if results['fixed']:
                files_modified += 1
                print(f"  ✅ Fixed {len(results['fixed'])} links:")
                for fix in results['fixed']:
                    print(f"     {fix}")
                    total_fixed += 1
            
            if results['errors']:
                print(f"  ❌ Errors ({len(results['errors'])}):")
                for error in results['errors']:
                    print(f"     {error}")
                    total_errors += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files processed: {len(files)}")
    print(f"Files modified: {files_modified}")
    print(f"Links fixed: {total_fixed}")
    print(f"Errors: {total_errors}")
    
    if dry_run:
        print("\n⚠️  This was a dry run. No files were modified.")
        print("Run without --dry-run flag to apply changes.")
    else:
        print("\n✅ Files have been modified. Backups created with .bak extension.")

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    dry_run = "--dry-run" in sys.argv
    
    # Check for specific files
    specific_files = []
    for arg in sys.argv[1:]:
        if arg != "--dry-run" and os.path.exists(arg):
            specific_files.append(arg)
    
    # Test on a few files first if requested
    if "--test" in sys.argv:
        test_files = [
            "/home/deepak/DStudio/docs/case-studies/chat-system.md",
            "/home/deepak/DStudio/docs/case-studies/google-systems/google-docs.md",
            "/home/deepak/DStudio/docs/part1-axioms/archive-old-8-axiom-structure/axiom1-latency/index.md",
        ]
        print("🧪 TEST MODE: Processing only test files\n")
        main(dry_run=True, specific_files=test_files)
    else:
        main(dry_run=dry_run, specific_files=specific_files)
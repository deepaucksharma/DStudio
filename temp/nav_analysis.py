#!/usr/bin/env python3
"""
Navigation Analysis Script
Identifies inconsistencies between mkdocs.yml navigation and actual file structure
"""

import os
import yaml
from pathlib import Path

def extract_nav_paths(nav_item, path_prefix=""):
    """Recursively extract all file paths from navigation structure"""
    paths = []
    
    if isinstance(nav_item, dict):
        for key, value in nav_item.items():
            if isinstance(value, str) and value.endswith('.md'):
                paths.append(value)
            elif isinstance(value, list):
                for item in value:
                    paths.extend(extract_nav_paths(item, path_prefix))
            elif isinstance(value, dict):
                paths.extend(extract_nav_paths(value, path_prefix))
    elif isinstance(nav_item, list):
        for item in nav_item:
            paths.extend(extract_nav_paths(item, path_prefix))
    elif isinstance(nav_item, str) and nav_item.endswith('.md'):
        paths.append(nav_item)
    
    return paths

def find_all_md_files(docs_dir):
    """Find all markdown files in docs directory"""
    md_files = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, file), docs_dir)
                md_files.append(rel_path.replace('\\', '/'))
    return sorted(md_files)

def analyze_navigation():
    """Main analysis function"""
    
    # Read mkdocs.yml
    with open('mkdocs.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Extract navigation paths
    nav_paths = extract_nav_paths(config['nav'])
    nav_paths = sorted(set(nav_paths))  # Remove duplicates and sort
    
    # Find actual files
    docs_dir = 'docs'
    actual_files = find_all_md_files(docs_dir)
    
    # Convert to sets for comparison
    nav_set = set(nav_paths)
    actual_set = set(actual_files)
    
    print("=== NAVIGATION STRUCTURE ANALYSIS ===\n")
    
    # 1. Navigation entries pointing to non-existent files
    print("1. NAVIGATION ENTRIES POINTING TO NON-EXISTENT FILES:")
    missing_files = nav_set - actual_set
    if missing_files:
        for file in sorted(missing_files):
            print(f"   ❌ {file}")
    else:
        print("   ✅ All navigation entries point to existing files")
    print()
    
    # 2. Files that exist but aren't in navigation
    print("2. FILES THAT EXIST BUT AREN'T IN NAVIGATION:")
    orphaned_files = actual_set - nav_set
    if orphaned_files:
        for file in sorted(orphaned_files):
            print(f"   ⚠️  {file}")
    else:
        print("   ✅ All files are included in navigation")
    print()
    
    # 3. Check for specific patterns and inconsistencies
    print("3. SPECIFIC PATTERN ANALYSIS:")
    
    # Check for missing index files in directories with subdirectories
    directories_with_subdirs = set()
    for file in actual_files:
        parts = file.split('/')
        if len(parts) > 1:
            directories_with_subdirs.add(parts[0])
    
    print("   Directory Index File Check:")
    for dir_name in sorted(directories_with_subdirs):
        index_file = f"{dir_name}/index.md"
        if index_file not in actual_set:
            print(f"   ❌ Missing index file: {index_file}")
        else:
            print(f"   ✅ {index_file}")
    print()
    
    # 4. Pattern-specific analysis
    print("4. PATTERN-SPECIFIC ISSUES:")
    
    # Check for pattern files mentioned in nav but missing
    pattern_nav_files = [f for f in nav_paths if f.startswith('patterns/')]
    pattern_actual_files = [f for f in actual_files if f.startswith('patterns/')]
    
    missing_patterns = set(pattern_nav_files) - set(pattern_actual_files)
    if missing_patterns:
        print("   Missing Pattern Files:")
        for file in sorted(missing_patterns):
            print(f"   ❌ {file}")
    
    extra_patterns = set(pattern_actual_files) - set(pattern_nav_files)
    if extra_patterns:
        print("   Pattern Files Not in Navigation:")
        for file in sorted(extra_patterns):
            print(f"   ⚠️  {file}")
    
    if not missing_patterns and not extra_patterns:
        print("   ✅ All pattern files are properly aligned")
    print()
    
    # 5. Summary statistics
    print("5. SUMMARY STATISTICS:")
    print(f"   Total files in navigation: {len(nav_paths)}")
    print(f"   Total markdown files found: {len(actual_files)}")
    print(f"   Missing files: {len(missing_files)}")
    print(f"   Orphaned files: {len(orphaned_files)}")
    print()
    
    # 6. Recommendations
    print("6. RECOMMENDATIONS:")
    if missing_files:
        print("   📝 Create missing files or remove from navigation:")
        for file in sorted(missing_files):
            print(f"      - {file}")
    
    if orphaned_files:
        print("   📝 Add to navigation or move to appropriate location:")
        for file in sorted(orphaned_files):
            if not any(skip in file for skip in ['FORMATTING_ISSUES', 'LEARNING_PATHS', 'NAVIGATION_ENHANCEMENTS']):
                print(f"      - {file}")
    
    return {
        'nav_paths': nav_paths,
        'actual_files': actual_files,
        'missing_files': missing_files,
        'orphaned_files': orphaned_files
    }

if __name__ == "__main__":
    os.chdir('/Users/deepaksharma/syc/DStudio')
    analyze_navigation()
#!/usr/bin/env python3
"""
Manual Navigation Analysis Script
Identifies inconsistencies between mkdocs.yml navigation and actual file structure
"""

import os
import re
from pathlib import Path

def extract_nav_paths_from_text(mkdocs_content):
    """Extract navigation paths from mkdocs.yml text content"""
    nav_paths = []
    
    # Find the nav section
    nav_match = re.search(r'^nav:\s*$', mkdocs_content, re.MULTILINE)
    if not nav_match:
        return nav_paths
    
    # Extract lines after nav:
    lines = mkdocs_content[nav_match.end():].split('\n')
    
    for line in lines:
        # Stop if we hit another top-level config section
        if line and not line.startswith(' ') and not line.startswith('\t') and ':' in line:
            break
            
        # Look for .md file references
        md_match = re.search(r':\s*([^:\s]+\.md)\s*$', line)
        if md_match:
            nav_paths.append(md_match.group(1))
    
    return nav_paths

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
    
    # Read mkdocs.yml as text
    with open('mkdocs.yml', 'r') as f:
        mkdocs_content = f.read()
    
    # Extract navigation paths manually
    nav_paths = extract_nav_paths_from_text(mkdocs_content)
    nav_paths = sorted(set(nav_paths))  # Remove duplicates and sort
    
    # Find actual files
    docs_dir = 'docs'
    actual_files = find_all_md_files(docs_dir)
    
    # Convert to sets for comparison
    nav_set = set(nav_paths)
    actual_set = set(actual_files)
    
    print("=== MKDOCS.YML NAVIGATION STRUCTURE ANALYSIS ===\n")
    
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
        # Filter out certain files that shouldn't be in navigation
        filtered_orphaned = []
        skip_patterns = [
            'FORMATTING_ISSUES.md',
            'LEARNING_PATHS.md', 
            'NAVIGATION_ENHANCEMENTS.md',
            'index-enhanced.md'  # These seem to be alternate versions
        ]
        
        for file in sorted(orphaned_files):
            should_skip = any(pattern in file for pattern in skip_patterns)
            if not should_skip:
                filtered_orphaned.append(file)
                print(f"   ⚠️  {file}")
            else:
                print(f"   📝 {file} (excluded - likely meta/alternate file)")
        
        if not filtered_orphaned:
            print("   ✅ All relevant files are included in navigation")
    else:
        print("   ✅ All files are included in navigation")
    print()
    
    # 3. Check for missing index files
    print("3. DIRECTORY INDEX FILE CHECK:")
    directories_with_subdirs = set()
    for file in actual_files:
        parts = file.split('/')
        if len(parts) > 1:
            directories_with_subdirs.add(parts[0])
    
    for dir_name in sorted(directories_with_subdirs):
        index_file = f"{dir_name}/index.md"
        if index_file not in actual_set:
            print(f"   ❌ Missing index file: {index_file}")
        else:
            print(f"   ✅ {index_file}")
    print()
    
    # 4. Pattern-specific analysis
    print("4. PATTERN-SPECIFIC ISSUES:")
    
    # Check for pattern files
    pattern_nav_files = [f for f in nav_paths if f.startswith('patterns/')]
    pattern_actual_files = [f for f in actual_files if f.startswith('patterns/')]
    
    missing_patterns = set(pattern_nav_files) - set(pattern_actual_files)
    extra_patterns = set(pattern_actual_files) - set(pattern_nav_files)
    
    if missing_patterns:
        print("   Missing Pattern Files Referenced in Nav:")
        for file in sorted(missing_patterns):
            print(f"   ❌ {file}")
    
    if extra_patterns:
        print("   Pattern Files Not in Navigation:")
        for file in sorted(extra_patterns):
            # Skip enhanced versions and meta files
            if not any(skip in file for skip in ['-enhanced.md', 'pattern-comparison.md', 'pattern-selector.md']):
                print(f"   ⚠️  {file}")
            else:
                print(f"   📝 {file} (excluded - likely enhanced/meta file)")
    
    if not missing_patterns and not extra_patterns:
        print("   ✅ All pattern files are properly aligned")
    print()
    
    # 5. Case studies analysis
    print("5. CASE STUDIES ANALYSIS:")
    case_study_nav_files = [f for f in nav_paths if f.startswith('case-studies/')]
    case_study_actual_files = [f for f in actual_files if f.startswith('case-studies/')]
    
    print(f"   Navigation includes {len(case_study_nav_files)} case studies")
    print(f"   Directory contains {len(case_study_actual_files)} case study files")
    
    # Show which case studies are in nav vs actual
    nav_case_studies = set(case_study_nav_files)
    actual_case_studies = set(case_study_actual_files)
    
    missing_from_nav = actual_case_studies - nav_case_studies
    if missing_from_nav:
        print("   Case Studies Not in Navigation:")
        for file in sorted(missing_from_nav):
            if not any(skip in file for skip in ['-enhanced.md']):
                print(f"   ⚠️  {file}")
            else:
                print(f"   📝 {file} (excluded - enhanced version)")
    print()
    
    # 6. Summary and specific issues
    print("6. SPECIFIC INCONSISTENCIES FOUND:")
    
    # Show the problematic files clearly
    critical_issues = []
    
    for file in missing_files:
        critical_issues.append(f"❌ MISSING FILE: {file}")
    
    for file in orphaned_files:
        if not any(skip in file for skip in ['FORMATTING_ISSUES', 'LEARNING_PATHS', 'NAVIGATION_ENHANCEMENTS', 'index-enhanced']):
            critical_issues.append(f"⚠️  ORPHANED FILE: {file}")
    
    if critical_issues:
        for issue in critical_issues:
            print(f"   {issue}")
    else:
        print("   ✅ No critical inconsistencies found")
    print()
    
    # 7. Statistics
    print("7. SUMMARY STATISTICS:")
    print(f"   Navigation entries: {len(nav_paths)}")
    print(f"   Actual MD files: {len(actual_files)}")
    print(f"   Missing files: {len(missing_files)}")
    print(f"   Orphaned files: {len(orphaned_files)}")
    
    return {
        'nav_paths': nav_paths,
        'actual_files': actual_files,
        'missing_files': missing_files,
        'orphaned_files': orphaned_files
    }

if __name__ == "__main__":
    os.chdir('/Users/deepaksharma/syc/DStudio')
    analyze_navigation()
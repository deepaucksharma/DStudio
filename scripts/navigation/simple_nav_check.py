#!/usr/bin/env python3
"""
Simple navigation analysis that doesn't require YAML parsing.
Focus on file existence and broken link patterns.
"""

import os
import re
from pathlib import Path

def check_critical_files():
    """Check for critical missing files."""
    docs_path = Path("/home/deepak/DStudio/docs")
    
    critical_files = [
        'index.md',  # Homepage
        'progress.md',  # Progress tracking
        'start-here/index.md',  # Start here guide
        'pattern-library/ml-infrastructure/index.md',  # ML infrastructure index
        'interview-prep/ENGINEERING_LEADERSHIP_INTERVIEW_FRAMEWORK.md',
        'excellence/migrations/MIGRATION_GUIDES_COMPLETE.md',
    ]
    
    print("🔍 Critical File Analysis")
    print("-" * 40)
    
    missing_critical = []
    existing_critical = []
    
    for critical_file in critical_files:
        file_path = docs_path / critical_file
        if file_path.exists():
            existing_critical.append(critical_file)
            print(f"✅ {critical_file}")
        else:
            missing_critical.append(critical_file)
            print(f"❌ {critical_file}")
    
    return existing_critical, missing_critical

def analyze_nav_references():
    """Extract file references from mkdocs.yml nav section."""
    mkdocs_path = Path("/home/deepak/DStudio/mkdocs.yml")
    
    print("\n📋 Navigation File References Analysis")
    print("-" * 50)
    
    with open(mkdocs_path, 'r') as f:
        content = f.read()
    
    # Extract nav section
    nav_match = re.search(r'^nav:(.*)', content, re.MULTILINE | re.DOTALL)
    if nav_match:
        nav_content = nav_match.group(1)
        
        # Find all .md file references
        md_references = re.findall(r'([a-zA-Z0-9/_-]+\.md)', nav_content)
        
        print(f"Total .md files referenced in navigation: {len(md_references)}")
        
        # Check existence
        docs_path = Path("/home/deepak/DStudio/docs")
        missing_nav_files = []
        
        for md_file in md_references:
            file_path = docs_path / md_file
            if not file_path.exists():
                missing_nav_files.append(md_file)
        
        print(f"Missing navigation files: {len(missing_nav_files)}")
        
        if missing_nav_files:
            print("\nFirst 10 missing files:")
            for i, missing_file in enumerate(missing_nav_files[:10]):
                print(f"  {i+1}. {missing_file}")
        
        return md_references, missing_nav_files
    
    return [], []

def count_redirects():
    """Count redirect mappings in mkdocs.yml."""
    mkdocs_path = Path("/home/deepak/DStudio/mkdocs.yml")
    
    with open(mkdocs_path, 'r') as f:
        content = f.read()
    
    # Count redirect entries (lines with: pattern)
    redirect_lines = re.findall(r'^\s+[^#\s-][^:]+\.md:', content, re.MULTILINE)
    
    print(f"\n🔄 Redirect Mappings: {len(redirect_lines)}")
    
    # Categorize redirects
    categories = {
        'patterns/': 0,
        'part1-axioms/': 0,
        'part2-pillars/': 0,
        'case-studies/': 0,
        'quantitative/': 0,
        'human-factors/': 0,
        'learning-paths/': 0,
        'other': 0
    }
    
    for line in redirect_lines:
        categorized = False
        for category in categories.keys():
            if category != 'other' and category in line:
                categories[category] += 1
                categorized = True
                break
        if not categorized:
            categories['other'] += 1
    
    print("Redirect categories:")
    for category, count in categories.items():
        if count > 0:
            print(f"  {category}: {count}")
    
    return len(redirect_lines)

def find_broken_internal_links():
    """Search for potentially broken internal links in markdown files."""
    docs_path = Path("/home/deepak/DStudio/docs")
    
    print(f"\n🔗 Internal Link Analysis")
    print("-" * 30)
    
    # Pattern library reference pattern
    pattern_lib_pattern = r'pattern-library/[a-zA-Z0-9/_-]+'
    relative_path_pattern = r'\]\(\.\./[^)]+\)'
    
    files_with_issues = []
    total_md_files = 0
    
    for md_file in docs_path.rglob('*.md'):
        total_md_files += 1
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                pattern_lib_matches = len(re.findall(pattern_lib_pattern, content))
                relative_path_matches = len(re.findall(relative_path_pattern, content))
                
                if pattern_lib_matches > 0 or relative_path_matches > 0:
                    files_with_issues.append({
                        'file': str(md_file.relative_to(docs_path)),
                        'pattern_lib_refs': pattern_lib_matches,
                        'relative_paths': relative_path_matches
                    })
                    
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    
    print(f"Total markdown files: {total_md_files}")
    print(f"Files with potential link issues: {len(files_with_issues)}")
    
    if files_with_issues:
        print("\nFiles with most references:")
        sorted_files = sorted(files_with_issues, 
                            key=lambda x: x['pattern_lib_refs'] + x['relative_paths'], 
                            reverse=True)
        
        for i, file_info in enumerate(sorted_files[:5]):
            total_refs = file_info['pattern_lib_refs'] + file_info['relative_paths']
            print(f"  {i+1}. {file_info['file']}: {total_refs} refs")
    
    return files_with_issues

def check_directory_structure():
    """Check for directory structure issues."""
    docs_path = Path("/home/deepak/DStudio/docs")
    
    print(f"\n📁 Directory Structure Analysis")
    print("-" * 35)
    
    # Check for symlinks
    symlinks = []
    for item in docs_path.rglob('*'):
        if item.is_symlink():
            target = item.readlink()
            symlinks.append(f"{item.relative_to(docs_path)} → {target}")
    
    if symlinks:
        print(f"Symlinks found ({len(symlinks)}):")
        for symlink in symlinks:
            print(f"  {symlink}")
    
    # Check major directories exist
    major_dirs = [
        'core-principles',
        'pattern-library', 
        'architects-handbook',
        'interview-prep',
        'excellence',
        'reference'
    ]
    
    print("\nMajor directories:")
    for dir_name in major_dirs:
        dir_path = docs_path / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/")
    
    return symlinks

def main():
    """Main analysis function."""
    print("🔍 DStudio Navigation Issues Analysis")
    print("=" * 50)
    
    # Check critical files
    existing_critical, missing_critical = check_critical_files()
    
    # Analyze navigation references
    nav_files, missing_nav_files = analyze_nav_references()
    
    # Count redirects
    redirect_count = count_redirects()
    
    # Find broken internal links
    link_issues = find_broken_internal_links()
    
    # Check directory structure
    symlinks = check_directory_structure()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    print(f"Critical files missing: {len(missing_critical)}")
    print(f"Navigation files missing: {len(missing_nav_files)}")
    print(f"Total redirects: {redirect_count}")
    print(f"Files with link issues: {len(link_issues)}")
    print(f"Symlinks found: {len(symlinks)}")
    
    # Priority recommendations
    print(f"\n🎯 TOP PRIORITY FIXES:")
    
    if 'index.md' in missing_critical:
        print("1. 🚨 Create docs/index.md - HOMEPAGE MISSING!")
    
    if missing_nav_files:
        print(f"2. 📋 Fix {len(missing_nav_files)} missing navigation files")
    
    if redirect_count > 100:
        print(f"3. 🔄 Review {redirect_count} redirects - high complexity")
    
    if symlinks:
        print("4. 📁 Review symlink structure for consistency")
    
    print(f"\n✨ Run this script regularly to track navigation health!")

if __name__ == "__main__":
    main()
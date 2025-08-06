#!/usr/bin/env python3
"""
Comprehensive analysis of navigation and linking issues in DStudio codebase.
This script validates the findings from the navigation analysis.
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict

def load_mkdocs_config():
    """Load and parse mkdocs.yml configuration."""
    config_path = Path("/home/deepak/DStudio/mkdocs.yml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def extract_nav_files(nav_structure, prefix=""):
    """Extract all files referenced in navigation structure."""
    files = []
    
    if isinstance(nav_structure, dict):
        for key, value in nav_structure.items():
            if isinstance(value, str) and value.endswith('.md'):
                files.append(value)
            elif isinstance(value, (list, dict)):
                files.extend(extract_nav_files(value, prefix))
    elif isinstance(nav_structure, list):
        for item in nav_structure:
            files.extend(extract_nav_files(item, prefix))
    elif isinstance(nav_structure, str) and nav_structure.endswith('.md'):
        files.append(nav_structure)
    
    return files

def check_file_existence(docs_dir, nav_files):
    """Check which navigation files actually exist."""
    docs_path = Path(docs_dir)
    missing_files = []
    existing_files = []
    
    for nav_file in nav_files:
        file_path = docs_path / nav_file
        if file_path.exists():
            existing_files.append(nav_file)
        else:
            missing_files.append(nav_file)
    
    return existing_files, missing_files

def analyze_redirects(config):
    """Analyze redirect patterns to understand URL evolution."""
    redirect_maps = config.get('plugins', [{}])[1].get('redirects', {}).get('redirect_maps', {})
    
    redirect_patterns = defaultdict(list)
    
    for old_url, new_url in redirect_maps.items():
        # Categorize redirects by pattern
        if old_url.startswith('part1-axioms/'):
            redirect_patterns['laws_restructure'].append((old_url, new_url))
        elif old_url.startswith('part2-pillars/'):
            redirect_patterns['pillars_restructure'].append((old_url, new_url))
        elif old_url.startswith('patterns/'):
            redirect_patterns['pattern_library_restructure'].append((old_url, new_url))
        elif old_url.startswith('case-studies/'):
            redirect_patterns['case_studies_restructure'].append((old_url, new_url))
        elif old_url.startswith('quantitative/'):
            redirect_patterns['quantitative_restructure'].append((old_url, new_url))
        else:
            redirect_patterns['other'].append((old_url, new_url))
    
    return redirect_patterns

def find_broken_internal_links(docs_dir):
    """Search for potentially broken internal links."""
    docs_path = Path(docs_dir)
    broken_links = []
    
    # Patterns that might indicate broken links
    link_patterns = [
        r'\]\(\.\./[^)]+\)',  # Relative paths with ../
        r'\]\(/[^)]+\.md\)',  # Absolute paths to .md files
        r'pattern-library/[^)]+',  # Pattern library references
    ]
    
    for md_file in docs_path.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                for pattern in link_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        broken_links.append({
                            'file': str(md_file.relative_to(docs_path)),
                            'pattern': pattern,
                            'matches': matches[:5]  # Limit to first 5 matches
                        })
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    
    return broken_links

def check_critical_files(docs_dir):
    """Check for critical missing files."""
    docs_path = Path(docs_dir)
    
    critical_files = [
        'index.md',  # Homepage
        'progress.md',  # Progress tracking
        'start-here/index.md',  # Start here guide
        'pattern-library/ml-infrastructure/index.md',  # ML infrastructure index
        'interview-prep/ENGINEERING_LEADERSHIP_INTERVIEW_FRAMEWORK.md',
        'excellence/migrations/MIGRATION_GUIDES_COMPLETE.md',
    ]
    
    missing_critical = []
    existing_critical = []
    
    for critical_file in critical_files:
        file_path = docs_path / critical_file
        if file_path.exists():
            existing_critical.append(critical_file)
        else:
            missing_critical.append(critical_file)
    
    return existing_critical, missing_critical

def analyze_url_patterns(config):
    """Analyze URL configuration for consistency."""
    site_url = config.get('site_url', '')
    use_directory_urls = config.get('use_directory_urls', True)
    docs_dir = config.get('docs_dir', 'docs')
    
    return {
        'site_url': site_url,
        'use_directory_urls': use_directory_urls,
        'docs_dir': docs_dir,
        'expected_url_format': 'directory' if use_directory_urls else 'file'
    }

def main():
    """Main analysis function."""
    print("🔍 Comprehensive Navigation Analysis for DStudio")
    print("=" * 60)
    
    # Load configuration
    config = load_mkdocs_config()
    docs_dir = "/home/deepak/DStudio/docs"
    
    # Extract navigation files
    nav_files = extract_nav_files(config.get('nav', []))
    print(f"📊 Total files referenced in navigation: {len(nav_files)}")
    
    # Check file existence
    existing_files, missing_files = check_file_existence(docs_dir, nav_files)
    print(f"✅ Existing navigation files: {len(existing_files)}")
    print(f"❌ Missing navigation files: {len(missing_files)}")
    
    # Show missing files
    if missing_files:
        print("\n🚨 Critical Missing Navigation Files:")
        for missing_file in missing_files[:10]:  # Show first 10
            print(f"   - {missing_file}")
        if len(missing_files) > 10:
            print(f"   ... and {len(missing_files) - 10} more")
    
    # Check critical files
    existing_critical, missing_critical = check_critical_files(docs_dir)
    if missing_critical:
        print(f"\n🔥 Missing Critical Files ({len(missing_critical)}):")
        for critical_file in missing_critical:
            print(f"   - {critical_file}")
    
    # Analyze redirects
    redirect_patterns = analyze_redirects(config)
    total_redirects = sum(len(patterns) for patterns in redirect_patterns.values())
    print(f"\n🔄 Total Redirects: {total_redirects}")
    
    for pattern_type, redirects in redirect_patterns.items():
        if redirects:
            print(f"   - {pattern_type}: {len(redirects)} redirects")
    
    # URL pattern analysis
    url_config = analyze_url_patterns(config)
    print(f"\n🌐 URL Configuration:")
    print(f"   - Site URL: {url_config['site_url']}")
    print(f"   - Directory URLs: {url_config['use_directory_urls']}")
    print(f"   - Expected format: {url_config['expected_url_format']}")
    
    # Find potentially broken internal links
    print("\n🔗 Analyzing Internal Links...")
    broken_links = find_broken_internal_links(docs_dir)
    print(f"   - Files with potential link issues: {len(broken_links)}")
    
    if broken_links:
        print("\n⚠️  Files with Potential Link Issues:")
        for link_issue in broken_links[:5]:  # Show first 5
            print(f"   - {link_issue['file']}: {len(link_issue['matches'])} matches")
    
    # Summary and recommendations
    print("\n" + "=" * 60)
    print("📋 SUMMARY OF ISSUES")
    print("=" * 60)
    
    issues = []
    if missing_files:
        issues.append(f"❌ {len(missing_files)} missing navigation files")
    if missing_critical:
        issues.append(f"🔥 {len(missing_critical)} missing critical files")
    if total_redirects > 100:
        issues.append(f"🔄 {total_redirects} redirects (high complexity)")
    if broken_links:
        issues.append(f"🔗 {len(broken_links)} files with potential link issues")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ No major navigation issues detected!")
    
    print("\n🔧 RECOMMENDED ACTIONS:")
    print("1. Create missing critical files (especially index.md)")
    print("2. Fix broken navigation references")
    print("3. Validate and clean up redirect mappings")
    print("4. Standardize internal link formats")
    print("5. Add navigation validation to CI/CD")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Final validation to ensure no side effects from navigation fixes
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def check_side_effects():
    """Check for common side effects from the navigation fixes"""
    docs_dir = Path("/home/deepak/DStudio/docs")
    issues = []
    
    print("🔍 Checking for side effects from navigation fixes...\n")
    
    # Check 1: Escaped admonitions (should be fixed now)
    escaped_admonitions = 0
    for md_file in docs_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if r'\!\!\!' in content:
                    escaped_admonitions += 1
                    issues.append(f"Escaped admonition in {md_file.relative_to(docs_dir)}")
        except:
            pass
    
    if escaped_admonitions > 0:
        print(f"❌ {escaped_admonitions} files still have escaped admonitions")
    else:
        print("✅ No escaped admonitions found")
    
    # Check 2: Empty links
    empty_links = 0
    for md_file in docs_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if re.search(r'\[([^\]]+)\]\(\)', content):
                    empty_links += 1
                    issues.append(f"Empty link in {md_file.relative_to(docs_dir)}")
        except:
            pass
    
    if empty_links > 0:
        print(f"⚠️  {empty_links} files have empty links []() ")
    else:
        print("✅ No empty links found")
    
    # Check 3: Double .md extensions
    double_md = 0
    for md_file in docs_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '.md.md' in content:
                    double_md += 1
                    issues.append(f"Double .md in {md_file.relative_to(docs_dir)}")
        except:
            pass
    
    if double_md > 0:
        print(f"❌ {double_md} files have .md.md extensions")
    else:
        print("✅ No double .md extensions found")
    
    # Check 4: Broken relative paths
    broken_paths = 0
    for md_file in docs_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for patterns that indicate broken paths
                if 'core-principles/pattern-library/' in content:
                    broken_paths += 1
                    issues.append(f"Wrong path prefix in {md_file.relative_to(docs_dir)}")
                elif 'pattern-library/core-principles/' in content:
                    broken_paths += 1
                    issues.append(f"Inverted path in {md_file.relative_to(docs_dir)}")
                elif 'architects-handbook/pattern-library/' in content:
                    broken_paths += 1
                    issues.append(f"Wrong architects path in {md_file.relative_to(docs_dir)}")
        except:
            pass
    
    if broken_paths > 0:
        print(f"⚠️  {broken_paths} files have broken path patterns")
    else:
        print("✅ No broken path patterns found")
    
    # Check 5: HTML in markdown files
    html_in_md = 0
    for md_file in docs_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Ignore meta refresh tags for redirects
                clean_content = re.sub(r'<meta[^>]+refresh[^>]+>', '', content)
                # Check for other HTML tags (except allowed ones)
                if re.search(r'<(?!/?(?:br|hr|meta|sup|sub|kbd|mark|code|pre|div|span|img|table|tr|td|th|tbody|thead)\b)[^>]+>', clean_content):
                    html_in_md += 1
                    issues.append(f"Unexpected HTML in {md_file.relative_to(docs_dir)}")
        except:
            pass
    
    if html_in_md > 0:
        print(f"⚠️  {html_in_md} files have unexpected HTML tags")
    else:
        print("✅ No unexpected HTML tags found")
    
    # Check 6: File size (content deletion check)
    tiny_files = []
    for md_file in docs_dir.rglob("*.md"):
        try:
            size = md_file.stat().st_size
            if size < 100 and 'index.md' not in str(md_file):
                tiny_files.append(md_file.relative_to(docs_dir))
        except:
            pass
    
    if tiny_files:
        print(f"⚠️  {len(tiny_files)} suspiciously small files found")
        for f in tiny_files[:5]:
            print(f"    - {f}")
    else:
        print("✅ No suspiciously small files found")
    
    # Check 7: Critical files exist
    critical_files = [
        'index.md',
        'start-here/index.md',
        'core-principles/index.md',
        'pattern-library/index.md',
        'architects-handbook/index.md',
        'pattern-library/ml-infrastructure/index.md',
    ]
    
    missing_critical = []
    for cf in critical_files:
        if not (docs_dir / cf).exists():
            missing_critical.append(cf)
            issues.append(f"Missing critical file: {cf}")
    
    if missing_critical:
        print(f"❌ {len(missing_critical)} critical files missing")
        for f in missing_critical:
            print(f"    - {f}")
    else:
        print("✅ All critical files exist")
    
    # Summary
    print("\n" + "=" * 60)
    if issues:
        print(f"⚠️  Total issues found: {len(issues)}")
        print("\nFirst 10 issues:")
        for issue in issues[:10]:
            print(f"  - {issue}")
    else:
        print("✅ NO SIDE EFFECTS DETECTED - All checks passed!")
    print("=" * 60)
    
    return len(issues) == 0

if __name__ == "__main__":
    success = check_side_effects()
    exit(0 if success else 1)
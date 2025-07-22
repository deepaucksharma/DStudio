#!/usr/bin/env python3
"""
Check for naming inconsistencies and navigation structure issues
"""

import os
import re

def check_naming_consistency():
    """Check for naming inconsistencies between navigation and files"""
    
    with open('mkdocs.yml', 'r') as f:
        content = f.read()
    
    print("=== NAMING CONSISTENCY ANALYSIS ===\n")
    
    # Extract navigation section
    nav_match = re.search(r'^nav:\s*$', content, re.MULTILINE)
    if not nav_match:
        print("❌ Could not find nav section")
        return
    
    nav_section = content[nav_match.end():]
    # Stop at next top-level section
    next_section = re.search(r'^[a-zA-Z]', nav_section, re.MULTILINE)
    if next_section:
        nav_section = nav_section[:next_section.start()]
    
    print("1. NAVIGATION STRUCTURE ANALYSIS:")
    
    # Check for proper indentation and structure
    lines = nav_section.split('\n')
    prev_indent = 0
    nav_items = []
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
            
        # Count indentation
        indent = len(line) - len(line.lstrip())
        
        # Extract item name and file reference
        if ':' in line:
            parts = line.split(':', 1)
            name = parts[0].strip().strip('"').strip("'")
            if len(parts) > 1:
                file_ref = parts[1].strip()
                if file_ref.endswith('.md'):
                    nav_items.append((name, file_ref, indent))
    
    print(f"   Found {len(nav_items)} navigation entries")
    
    # Check for duplicate entries
    print("\n2. DUPLICATE DETECTION:")
    file_refs = [item[1] for item in nav_items]
    duplicates = set([x for x in file_refs if file_refs.count(x) > 1])
    
    if duplicates:
        print("   ❌ Duplicate file references found:")
        for dup in duplicates:
            print(f"      - {dup}")
    else:
        print("   ✅ No duplicate file references")
    
    # Check for consistent naming patterns
    print("\n3. NAMING PATTERN ANALYSIS:")
    
    patterns = {
        'index_files': [],
        'examples_files': [],
        'exercises_files': [],
        'case_studies': [],
        'patterns': [],
        'axioms': [],
        'pillars': []
    }
    
    for name, file_ref, indent in nav_items:
        if 'index.md' in file_ref:
            patterns['index_files'].append((name, file_ref))
        elif 'examples.md' in file_ref:
            patterns['examples_files'].append((name, file_ref))
        elif 'exercises.md' in file_ref:
            patterns['exercises_files'].append((name, file_ref))
        elif 'case-studies/' in file_ref:
            patterns['case_studies'].append((name, file_ref))
        elif 'patterns/' in file_ref:
            patterns['patterns'].append((name, file_ref))
        elif 'axiom' in file_ref:
            patterns['axioms'].append((name, file_ref))
        elif 'part2-pillars/' in file_ref and ('work/' in file_ref or 'state/' in file_ref or 'truth/' in file_ref or 'control/' in file_ref or 'intelligence/' in file_ref):
            patterns['pillars'].append((name, file_ref))
    
    for pattern_name, items in patterns.items():
        if items:
            print(f"\n   {pattern_name.replace('_', ' ').title()}:")
            for name, file_ref in items[:5]:  # Show first 5
                print(f"      '{name}' -> {file_ref}")
            if len(items) > 5:
                print(f"      ... and {len(items) - 5} more")
    
    # Check for common inconsistencies
    print("\n4. COMMON INCONSISTENCY CHECKS:")
    
    # Check if "Overview" vs "Index" naming is consistent
    overview_count = sum(1 for name, _, _ in nav_items if name.lower() == 'overview')
    index_count = sum(1 for name, _, _ in nav_items if name.lower() == 'index')
    
    print(f"   Overview entries: {overview_count}")
    print(f"   Index entries: {index_count}")
    
    if overview_count > 0 and index_count > 0:
        print("   ⚠️  Mixed usage of 'Overview' and 'Index' - consider standardizing")
    else:
        print("   ✅ Consistent naming for main pages")
    
    # Check for case sensitivity issues
    file_names = [item[1].split('/')[-1] for item in nav_items]
    lowercase_files = [f.lower() for f in file_names]
    if len(set(file_names)) != len(set(lowercase_files)):
        print("   ⚠️  Potential case sensitivity issues detected")
    else:
        print("   ✅ No case sensitivity issues")
    
    return nav_items

def check_tools_section():
    """Special check for the tools section issue"""
    print("\n=== TOOLS SECTION SPECIFIC ANALYSIS ===")
    
    # Check if tools/index.md exists and what's in navigation
    tools_file = 'docs/tools/index.md'
    if os.path.exists(tools_file):
        print(f"✅ {tools_file} exists")
        
        # Check what's in the navigation for tools
        with open('mkdocs.yml', 'r') as f:
            content = f.read()
        
        tools_match = re.search(r'Tools:\s*\n\s*-\s*([^\n]+)', content)
        if tools_match:
            tools_nav = tools_match.group(1)
            print(f"Navigation entry: 'Tools: {tools_nav}'")
            
            if tools_nav.strip() == 'tools/index.md':
                print("✅ Tools navigation correctly points to tools/index.md")
            else:
                print(f"❌ Tools navigation issue: expected 'tools/index.md', got '{tools_nav}'")
        else:
            print("❌ Could not find Tools section in navigation")
    else:
        print(f"❌ {tools_file} does not exist")

if __name__ == "__main__":
    os.chdir('/Users/deepaksharma/syc/DStudio')
    nav_items = check_naming_consistency()
    check_tools_section()
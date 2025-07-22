#!/usr/bin/env python3
"""
Generate a focused verification summary with actionable fixes.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_broken_links(report_path):
    """Analyze the verification report and categorize issues."""
    
    with open(report_path, 'r') as f:
        content = f.read()
    
    # Extract broken links
    broken_links = re.findall(r'Broken link in ([^:]+): (.+)', content)
    
    # Categorize issues
    issues = {
        'missing_pattern_pages': defaultdict(list),
        'incorrect_paths': defaultdict(list),
        'missing_human_factors': [],
        'missing_quantitative': [],
        'code_snippets': defaultdict(list),
        'case_study_refs': defaultdict(list)
    }
    
    for file, link in broken_links:
        # Pattern links that need fixing
        if '/patterns/' in link and link.endswith('/'):
            pattern_name = link.split('/')[-2]
            issues['missing_pattern_pages'][pattern_name].append(file)
        
        # Incorrect relative paths to axioms
        elif 'part1-axioms' in link and file.startswith('quantitative/'):
            issues['incorrect_paths'][file].append(link)
        
        # Missing human-factors pages
        elif 'human-factors' in link:
            issues['missing_human_factors'].append((file, link))
        
        # Code snippet pseudo-links (not real links)
        elif link in ['event', 'context', 'event, context', 'current_load', 'clean_event', 'my_share', 'conflicts']:
            issues['code_snippets'][file].append(link)
        
        # Case study specific references
        elif file.startswith('case-studies/'):
            issues['case_study_refs'][file].append(link)
    
    return issues

def generate_actionable_summary(issues):
    """Generate an actionable summary of fixes needed."""
    
    print("\n" + "="*60)
    print("ACTIONABLE VERIFICATION SUMMARY")
    print("="*60)
    
    # 1. Code snippets that aren't links
    if issues['code_snippets']:
        print("\n1. CODE SNIPPETS INCORRECTLY FORMATTED AS LINKS")
        print("   These are code examples that should use backticks instead of link syntax:")
        for file, snippets in issues['code_snippets'].items():
            print(f"\n   File: {file}")
            for snippet in set(snippets):
                print(f"     - Change [{snippet}]({snippet}) to `{snippet}`")
    
    # 2. Pattern cross-references
    pattern_refs = issues['missing_pattern_pages']
    if pattern_refs:
        print("\n2. PATTERN CROSS-REFERENCES")
        print("   These patterns are referenced but may need index.md added to the path:")
        for pattern, files in sorted(pattern_refs.items()):
            print(f"\n   Pattern: {pattern}")
            print(f"     Referenced in: {', '.join(set(files))}")
            print(f"     Fix: Change /patterns/{pattern}/ to /patterns/{pattern}/index.md")
    
    # 3. Incorrect axiom paths
    if issues['incorrect_paths']:
        print("\n3. INCORRECT RELATIVE PATHS FROM QUANTITATIVE SECTION")
        print("   These need path corrections:")
        for file, paths in issues['incorrect_paths'].items():
            print(f"\n   File: {file}")
            for path in paths:
                if 'part1-axioms' in path:
                    axiom = path.split('/')[-2]
                    print(f"     - Change {path} to ../part1-axioms/{axiom}/")
    
    # 4. Missing human-factors pages
    if issues['missing_human_factors']:
        print("\n4. MISSING HUMAN-FACTORS PAGES")
        print("   These pages are referenced but don't exist:")
        unique_pages = set()
        for file, link in issues['missing_human_factors']:
            page = link.split('/')[-1].replace('.md', '')
            unique_pages.add(page)
        for page in sorted(unique_pages):
            print(f"     - {page}")
    
    # 5. Case study specific issues
    if issues['case_study_refs']:
        print("\n5. CASE STUDY SPECIFIC REFERENCES")
        print("   These are domain-specific references in case studies:")
        for file, refs in issues['case_study_refs'].items():
            case_study = file.split('/')[-1].replace('.md', '')
            unique_refs = set(refs)
            # Filter out quantitative and pattern refs we've already handled
            specific_refs = [r for r in unique_refs if not any(x in r for x in ['../patterns/', '../quantitative/', '../human-factors/'])]
            if specific_refs:
                print(f"\n   Case Study: {case_study}")
                for ref in specific_refs:
                    print(f"     - {ref}")
    
    # Summary statistics
    total_issues = sum([
        sum(len(v) for v in issues['code_snippets'].values()),
        sum(len(v) for v in issues['missing_pattern_pages'].values()),
        sum(len(v) for v in issues['incorrect_paths'].values()),
        len(issues['missing_human_factors']),
        sum(len(v) for v in issues['case_study_refs'].values())
    ])
    
    print("\n" + "="*60)
    print(f"TOTAL ISSUES TO FIX: {total_issues}")
    print("="*60)
    
    # Priority fixes
    print("\nPRIORITY FIXES:")
    print("1. Fix code snippet formatting (easy - just change syntax)")
    print("2. Add index.md to pattern cross-references")
    print("3. Correct relative paths in quantitative section")
    print("4. Review case study specific references")
    print("5. Consider creating missing human-factors pages or removing references")

def main():
    """Main function."""
    report_path = "/Users/deepaksharma/syc/DStudio/verification_report.txt"
    
    if not Path(report_path).exists():
        print("Error: verification_report.txt not found. Run verify_fixes.py first.")
        return
    
    issues = analyze_broken_links(report_path)
    generate_actionable_summary(issues)

if __name__ == "__main__":
    main()
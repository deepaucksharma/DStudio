#!/usr/bin/env python3
"""
Check for consistency issues in the pattern library.
"""

import os
import re
import yaml
from collections import defaultdict
from pathlib import Path

def extract_frontmatter(file_path):
    """Extract YAML frontmatter from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    return None

def check_patterns():
    pattern_dir = Path('docs/pattern-library')
    issues = defaultdict(list)
    statistics = {
        'total_patterns': 0,
        'patterns_with_excellence_tier': 0,
        'patterns_by_category': defaultdict(int),
        'patterns_by_tier': defaultdict(int),
        'missing_metadata': []
    }
    
    # Expected categories
    expected_categories = {
        'architecture', 'communication', 'coordination', 
        'data-management', 'resilience', 'scaling'
    }
    
    # Check all pattern files
    for root, dirs, files in os.walk(pattern_dir):
        for file in files:
            if file.endswith('.md') and not file.startswith('pattern-') and file != 'index.md':
                statistics['total_patterns'] += 1
                file_path = os.path.join(root, file)
                category = os.path.basename(os.path.dirname(file_path))
                
                # Check category
                if category not in expected_categories:
                    issues['invalid_category'].append(f"{file_path}: Category '{category}' not expected")
                
                statistics['patterns_by_category'][category] += 1
                
                # Check metadata
                metadata = extract_frontmatter(file_path)
                if metadata:
                    # Check excellence_tier
                    if 'excellence_tier' in metadata:
                        statistics['patterns_with_excellence_tier'] += 1
                        tier = metadata['excellence_tier']
                        if tier not in ['gold', 'silver', 'bronze']:
                            issues['invalid_tier'].append(f"{file_path}: Invalid tier '{tier}'")
                        statistics['patterns_by_tier'][tier] += 1
                    else:
                        issues['missing_excellence_tier'].append(file_path)
                    
                    # Check required fields
                    required_fields = ['title', 'description', 'category']
                    for field in required_fields:
                        if field not in metadata:
                            issues[f'missing_{field}'].append(file_path)
                    
                    # Check pattern_status consistency
                    if 'pattern_status' in metadata:
                        status = metadata['pattern_status']
                        valid_statuses = [
                            'recommended', 'stable', 'use-with-expertise', 
                            'use-with-caution', 'legacy', 'deprecated'
                        ]
                        if status not in valid_statuses and status.replace('_', '-') not in valid_statuses:
                            issues['invalid_status'].append(f"{file_path}: Invalid status '{status}'")
                else:
                    issues['no_frontmatter'].append(file_path)
    
    # Check count discrepancy
    claimed_count = 112
    actual_count = statistics['total_patterns']
    if actual_count != claimed_count:
        issues['count_mismatch'].append(f"Claimed {claimed_count} patterns but found {actual_count}")
    
    return statistics, issues

def main():
    print("🔍 Checking Pattern Library Consistency\n")
    
    statistics, issues = check_patterns()
    
    # Print statistics
    print("📊 Statistics:")
    print(f"  Total patterns: {statistics['total_patterns']}")
    print(f"  With excellence_tier: {statistics['patterns_with_excellence_tier']}")
    print(f"  Missing excellence_tier: {statistics['total_patterns'] - statistics['patterns_with_excellence_tier']}")
    
    print("\n📁 Patterns by Category:")
    for cat, count in sorted(statistics['patterns_by_category'].items()):
        print(f"  {cat}: {count}")
    
    print("\n🏆 Patterns by Tier:")
    for tier, count in sorted(statistics['patterns_by_tier'].items()):
        print(f"  {tier}: {count}")
    
    # Print issues
    if issues:
        print("\n⚠️  Issues Found:")
        for issue_type, items in sorted(issues.items()):
            if items:
                print(f"\n  {issue_type.replace('_', ' ').title()} ({len(items)}):")
                for item in items[:5]:  # Show first 5
                    print(f"    - {item}")
                if len(items) > 5:
                    print(f"    ... and {len(items) - 5} more")
    else:
        print("\n✅ No issues found!")
    
    # Summary
    total_issues = sum(len(items) for items in issues.values())
    print(f"\n📋 Summary: {total_issues} total issues found")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Fix broken links in interview-prep section
"""

import os
import re
import sys

LINK_FIXES = {
    # Fix company-specific references
    'company-specific/': '../company-specific/',
    '../../company-specific/': '../../company-specific/amazon/index.md',
    
    # Fix file references that don't exist
    'architecture-patterns.md': 'index.md#architecture-patterns',
    'engineering-excellence.md': 'index.md#engineering-excellence',
    'technical-mentorship.md': 'index.md#technical-mentorship',
    'cross-functional.md': 'index.md#cross-functional-leadership',
    'stakeholder-management.md': 'index.md#stakeholder-management',
    'product-thinking.md': 'index.md#product-thinking',
    'strategic-planning.md': 'index.md#strategic-planning',
    'roi-metrics.md': 'index.md#roi-and-metrics',
    'team-building.md': 'index.md#team-building',
    'performance-management.md': 'index.md#performance-management',
    'career-development.md': 'index.md#career-development',
    'conflict-resolution.md': 'index.md#conflict-resolution',
    'structure-process.md': 'index.md#organizational-structure',
    'scaling-teams.md': 'index.md#scaling-teams',
    'culture-building.md': 'index.md#culture-building',
    'change-management.md': 'index.md#change-management',
    
    # Fix anchor links
    '#level-iv-interview-preparation--execution-the-proof': '#level-iv-interview-execution',
    '#financial-literacy': '#business-understanding',
    '#product-sense': '#product-thinking',
    '#strategic-thinking': '#strategic-planning',
    '#roi--metrics': '#roi-and-metrics',
    '#scaling-organizations': '#scaling-teams',
    '#agile--process': '#structure-and-process',
    
    # Fix framework references
    'framework/': '../framework-index.md',
    'tools/': '../tools/',
    
    # Fix behavioral references
    '../behavioral/': '../behavioral/scenarios.md',
    '../../behavioral/': '../../behavioral/scenarios.md',
}

def fix_links_in_file(file_path, dry_run=False):
    """Fix broken links in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        fixes_made = []
        
        # Fix markdown links
        def replace_link(match):
            text = match.group(1)
            url = match.group(2)
            
            for broken, fixed in LINK_FIXES.items():
                if url == broken or url.endswith('/' + broken):
                    new_url = url.replace(broken, fixed)
                    fixes_made.append((url, new_url))
                    return f'[{text}]({new_url})'
                    
            return match.group(0)
        
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)
        
        # Also fix standalone references
        for broken, fixed in LINK_FIXES.items():
            if f']({broken})' in content:
                content = content.replace(f']({broken})', f']({fixed})')
                fixes_made.append((broken, fixed))
        
        if content != original_content and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        return fixes_made
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Fix interview prep links')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed')
    parser.add_argument('--path', default='docs/interview-prep', help='Path to scan')
    
    args = parser.parse_args()
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Fixing interview prep broken links...")
    
    files_fixed = 0
    total_fixes = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk(args.path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                fixes = fix_links_in_file(file_path, dry_run=args.dry_run)
                
                if fixes:
                    files_fixed += 1
                    total_fixes += len(fixes)
                    print(f"{'Would fix' if args.dry_run else 'Fixed'} {len(fixes)} links in: {file_path}")
                    for old, new in fixes[:3]:
                        print(f"  {old} → {new}")
                    if len(fixes) > 3:
                        print(f"  ... and {len(fixes) - 3} more")
    
    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {total_fixes} links in {files_fixed} files")
    
    return 0 if not args.dry_run else 1

if __name__ == '__main__':
    sys.exit(main())
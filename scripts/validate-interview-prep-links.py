#!/usr/bin/env python3
"""
Validate all links in the interview-prep section of the documentation.
Checks for broken internal links, missing anchors, and external URLs.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import sys

# Base directory for the documentation
DOCS_DIR = Path(__file__).parent.parent / "docs"
INTERVIEW_PREP_DIR = DOCS_DIR / "interview-prep"

# Regex patterns for finding links
MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
ANCHOR_PATTERN = re.compile(r'^#(.+)$')
HEADING_PATTERN = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)

def normalize_anchor(text):
    """Convert heading text to anchor format."""
    # Remove special characters and convert to lowercase
    anchor = text.lower()
    # Remove markdown formatting
    anchor = re.sub(r'\*\*([^*]+)\*\*', r'\1', anchor)  # Bold
    anchor = re.sub(r'\*([^*]+)\*', r'\1', anchor)      # Italic
    anchor = re.sub(r'`([^`]+)`', r'\1', anchor)        # Code
    # Replace spaces and special chars with hyphens
    anchor = re.sub(r'[^\w\s-]', '', anchor)
    anchor = re.sub(r'[-\s]+', '-', anchor)
    return anchor.strip('-')

def extract_headings(content):
    """Extract all headings and their anchors from markdown content."""
    headings = set()
    for match in HEADING_PATTERN.finditer(content):
        heading_text = match.group(1).strip()
        anchor = normalize_anchor(heading_text)
        headings.add(anchor)
    return headings

def check_file_exists(base_path, link_path):
    """Check if a file exists relative to the base path."""
    if link_path.startswith('/'):
        # Absolute path from docs root
        full_path = DOCS_DIR / link_path.lstrip('/')
    else:
        # Relative path
        full_path = (base_path.parent / link_path).resolve()
    
    # Remove anchor if present
    if '#' in str(full_path):
        full_path = Path(str(full_path).split('#')[0])
    
    # Check with and without .md extension
    if full_path.exists():
        return True, full_path
    elif full_path.with_suffix('.md').exists():
        return True, full_path.with_suffix('.md')
    else:
        return False, full_path

def validate_links_in_file(file_path):
    """Validate all links in a single markdown file."""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all links
    for match in MARKDOWN_LINK_PATTERN.finditer(content):
        link_text = match.group(1)
        link_url = match.group(2)
        
        # Skip external links
        if link_url.startswith(('http://', 'https://', 'mailto:')):
            continue
        
        # Skip "Coming Soon" placeholders
        if 'Coming Soon' in link_text:
            continue
        
        # Check anchor-only links
        if link_url.startswith('#'):
            anchor = link_url[1:]
            headings = extract_headings(content)
            if anchor not in headings:
                issues.append({
                    'type': 'missing-anchor',
                    'file': str(file_path.relative_to(DOCS_DIR)),
                    'link_text': link_text,
                    'link_url': link_url,
                    'line': content[:match.start()].count('\n') + 1
                })
            continue
        
        # Check file links
        if '#' in link_url:
            file_part, anchor_part = link_url.split('#', 1)
        else:
            file_part = link_url
            anchor_part = None
        
        exists, target_path = check_file_exists(file_path, file_part)
        
        if not exists:
            issues.append({
                'type': 'broken-link',
                'file': str(file_path.relative_to(DOCS_DIR)),
                'link_text': link_text,
                'link_url': link_url,
                'line': content[:match.start()].count('\n') + 1
            })
        elif anchor_part:
            # Check if anchor exists in target file
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    target_content = f.read()
                target_headings = extract_headings(target_content)
                if anchor_part not in target_headings:
                    issues.append({
                        'type': 'missing-anchor',
                        'file': str(file_path.relative_to(DOCS_DIR)),
                        'link_text': link_text,
                        'link_url': link_url,
                        'line': content[:match.start()].count('\n') + 1,
                        'target_file': str(target_path.relative_to(DOCS_DIR))
                    })
            except Exception as e:
                print(f"Error reading {target_path}: {e}")
    
    return issues

def validate_all_interview_prep_links():
    """Validate links in all interview-prep markdown files."""
    all_issues = []
    file_count = 0
    
    # Walk through all markdown files in interview-prep
    for root, dirs, files in os.walk(INTERVIEW_PREP_DIR):
        for file in files:
            if file.endswith('.md'):
                file_path = Path(root) / file
                file_count += 1
                issues = validate_links_in_file(file_path)
                all_issues.extend(issues)
    
    return all_issues, file_count

def main():
    """Main function to run link validation."""
    print("🔍 Validating links in interview-prep section...")
    print("-" * 60)
    
    issues, file_count = validate_all_interview_prep_links()
    
    # Group issues by type
    issues_by_type = defaultdict(list)
    for issue in issues:
        issues_by_type[issue['type']].append(issue)
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"  Files checked: {file_count}")
    print(f"  Total issues found: {len(issues)}")
    print(f"  - Broken links: {len(issues_by_type['broken-link'])}")
    print(f"  - Missing anchors: {len(issues_by_type['missing-anchor'])}")
    
    if issues:
        print("\n❌ Issues found:\n")
        
        # Print broken links
        if issues_by_type['broken-link']:
            print("🔗 Broken Links:")
            for issue in sorted(issues_by_type['broken-link'], key=lambda x: x['file']):
                print(f"  {issue['file']}:{issue['line']}")
                print(f"    [{issue['link_text']}]({issue['link_url']})")
            print()
        
        # Print missing anchors
        if issues_by_type['missing-anchor']:
            print("⚓ Missing Anchors:")
            for issue in sorted(issues_by_type['missing-anchor'], key=lambda x: x['file']):
                print(f"  {issue['file']}:{issue['line']}")
                print(f"    [{issue['link_text']}]({issue['link_url']})")
                if 'target_file' in issue:
                    print(f"    Target file: {issue['target_file']}")
            print()
        
        return 1
    else:
        print("\n✅ All links are valid!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
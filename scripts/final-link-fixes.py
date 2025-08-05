#!/usr/bin/env python3
"""Final comprehensive link fixes for remaining issues."""

import re
from pathlib import Path

def fix_company_specific_links(content: str, file_path: Path) -> str:
    """Fix broken company-specific links."""
    # Count how many ../ we need based on file depth
    depth = len(file_path.relative_to(Path("docs")).parts) - 1
    correct_path = "../" * depth + "company-specific/"
    
    # Fix various company-specific patterns
    content = re.sub(r'\]\(\.\./+company-specific/\)', f']({correct_path})', content)
    
    return content

def fix_missing_resource_links(content: str) -> str:
    """Remove or fix links to non-existent resource files."""
    # These files don't exist, so we'll remove the links but keep the text
    missing_patterns = [
        (r'\[([^\]]+)\]\(tools/roi-calculator\.md\)', r'\1'),
        (r'\[([^\]]+)\]\(tools/tech-debt-cost\.md\)', r'\1'),
        (r'\[([^\]]+)\]\(tools/budget-planner\.md\)', r'\1'),
        (r'\[([^\]]+)\]\(templates/exec-briefing\.md\)', r'\1'),
        (r'\[([^\]]+)\]\(templates/business-case\.md\)', r'\1'),
        (r'\[([^\]]+)\]\(templates/metrics-dashboard\.md\)', r'\1'),
        (r'\[([^\]]+)\]\(resources/finance-guide\.md\)', r'\1'),
        (r'\[([^\]]+)\]\(resources/pl-basics\.md\)', r'\1'),
        (r'\[([^\]]+)\]\(resources/budgeting\.md\)', r'\1'),
    ]
    
    for pattern, replacement in missing_patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_interview_prep_links(file_path: Path) -> bool:
    """Fix all remaining issues in interview-prep files."""
    if not file_path.exists():
        return False
        
    content = file_path.read_text()
    original_content = content
    
    # Apply fixes
    content = fix_company_specific_links(content, file_path)
    content = fix_missing_resource_links(content)
    
    # Fix framework index anchor
    content = re.sub(r'\]\(#level-iv-interview-execution\)', '](level-4-interview-execution/)', content)
    
    if content != original_content:
        file_path.write_text(content)
        return True
    return False

def main():
    """Apply final fixes to all interview-prep files."""
    docs_dir = Path("docs")
    fixed_count = 0
    
    # Process all interview-prep markdown files
    for md_file in docs_dir.glob("interview-prep/**/*.md"):
        if fix_interview_prep_links(md_file):
            fixed_count += 1
            print(f"Fixed: {md_file}")
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
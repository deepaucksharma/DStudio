#!/usr/bin/env python3
"""
Fix final specific issues with broken links.
"""

import os
import re
import sys

def fix_consistent_hashing_links(content):
    """Fix links to consistent-hashing which is in case-studies, not patterns."""
    # Fix various patterns of consistent-hashing links
    replacements = [
        # Absolute paths
        (r'\]\(/patterns/consistent-hashing\.md\)', '](/case-studies/consistent-hashing)'),
        (r'\]\(/patterns/consistent-hashing\)', '](/case-studies/consistent-hashing)'),
        
        # Relative paths from case-studies
        (r'\]\(../patterns/consistent-hashing\)', '](../case-studies/consistent-hashing)'),
        (r'\]\(../../patterns/consistent-hashing\)', '](../consistent-hashing)'),
        
        # Fix patterns that don't exist but have case-study equivalents
        (r'\]\(/patterns/quorum\.md\)', '](/patterns/consensus)'),
        (r'\]\(/patterns/quorum-consensus\)', '](/patterns/consensus)'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_absolute_links_without_docs(content):
    """Remove 'docs' prefix from absolute links."""
    # Fix patterns like "Expected: docs/patterns/xxx.md"
    content = re.sub(r'\]\(/case-studies/([^)]+)\.md\)', r'](/case-studies/\1)', content)
    content = re.sub(r'\]\(/patterns/([^)]+)\.md\)', r'](/patterns/\1)', content)
    content = re.sub(r'\]\(/quantitative/([^)]+)\.md\)', r'](/quantitative/\1)', content)
    content = re.sub(r'\]\(/part1-axioms/([^)]+)\.md\)', r'](/part1-axioms/\1)', content)
    content = re.sub(r'\]\(/part2-pillars/([^)]+)\.md\)', r'](/part2-pillars/\1)', content)
    
    return content

def fix_google_interview_links(content, file_path):
    """Fix Google interview specific link issues."""
    if 'google-interviews' in file_path:
        # Fix relative links within google-interviews
        content = re.sub(r'\]\(([^/)][^)]*)\)', lambda m: f'](/{os.path.dirname(file_path.replace("docs/", ""))}/{m.group(1)})', content)
        
        # Fix specific known issues
        content = re.sub(r'\]\(/preparation-guide\)', '](/google-interviews/preparation-guide)', content)
        content = re.sub(r'\]\(/common-mistakes\)', '](/google-interviews/common-mistakes)', content)
        content = re.sub(r'\]\(/google-search\)', '](/google-interviews/google-search)', content)
    
    return content

def fix_template_placeholders(content):
    """Fix or remove template placeholder links."""
    # Remove obvious template placeholders
    content = re.sub(r'\[([^\]]+)\]\(link\)', r'\1', content)
    content = re.sub(r'\[([^\]]+)\]\(link/\)', r'\1', content)
    
    return content

def fix_pillar_references(content):
    """Fix pillar references that use old naming."""
    replacements = [
        ('/part2-pillars/work-distribution/', '/part2-pillars/work/'),
        ('/part2-pillars/state-distribution/', '/part2-pillars/state/'),
        ('/part2-pillars/truth-distribution/', '/part2-pillars/truth/'),
        ('/part2-pillars/control-distribution/', '/part2-pillars/control/'),
        ('/part2-pillars/intelligence-distribution/', '/part2-pillars/intelligence/'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    return content

def process_file(file_path):
    """Process a single file with all fixes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all fixes
        content = fix_consistent_hashing_links(content)
        content = fix_absolute_links_without_docs(content)
        content = fix_google_interview_links(content, file_path)
        content = fix_template_placeholders(content)
        content = fix_pillar_references(content)
        
        # Save if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function."""
    print("Applying final targeted fixes...")
    print("-" * 80)
    
    files_fixed = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                if process_file(file_path):
                    files_fixed += 1
                    print(f"Fixed: {file_path}")
    
    print(f"\nFixed {files_fixed} files")
    
    # Run verification
    print("\nRunning final verification...")
    os.system("python3 scripts/verify-links.py 2>&1 | grep -E '(Files checked:|Total internal links found:|Broken links found:)'")

if __name__ == "__main__":
    main()
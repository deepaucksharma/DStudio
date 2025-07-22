#!/usr/bin/env python3
"""
Quick validation specifically for heading structure issues.
"""

import re
from pathlib import Path

def validate_headings():
    docs_root = Path("/Users/deepaksharma/syc/DStudio/docs")
    issues = []
    
    for md_file in docs_root.rglob("*.md"):
        relative_path = md_file.relative_to(docs_root)
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            prev_level = 0
            
            for line_num, line in enumerate(lines, 1):
                atx_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
                if atx_match:
                    level = len(atx_match.group(1))
                    text = atx_match.group(2).strip()
                    
                    # Check for skipped levels
                    if level > prev_level + 1:
                        issues.append(f"{relative_path}:{line_num} - Jump from h{prev_level} to h{level}: '{text}'")
                    
                    prev_level = level
                    
        except Exception as e:
            issues.append(f"{relative_path} - Error: {e}")
    
    return issues

if __name__ == "__main__":
    print("Validating heading structures...")
    issues = validate_headings()
    
    print(f"\nFound {len(issues)} heading structure issues:")
    
    # Group by severity
    h1_to_h3 = [i for i in issues if "h0 to h3" in i or "h1 to h3" in i]
    h1_to_h4 = [i for i in issues if "h0 to h4" in i or "h1 to h4" in i] 
    other = [i for i in issues if i not in h1_to_h3 and i not in h1_to_h4]
    
    print(f"\nMost severe (h1→h3 jumps): {len(h1_to_h3)}")
    print(f"Very severe (h1→h4 jumps): {len(h1_to_h4)}")
    print(f"Other issues: {len(other)}")
    
    # Show examples
    print(f"\nExample h1→h3 issues:")
    for issue in h1_to_h3[:5]:
        print(f"  {issue}")
    
    print(f"\nExample h1→h4 issues:")
    for issue in h1_to_h4[:5]:
        print(f"  {issue}")
        
    # Save full report
    with open("/Users/deepaksharma/syc/DStudio/temp/heading_issues.txt", "w") as f:
        f.write("HEADING STRUCTURE ISSUES\n")
        f.write("=" * 50 + "\n\n")
        for issue in issues:
            f.write(issue + "\n")
    
    print(f"\nFull report saved to: /Users/deepaksharma/syc/DStudio/temp/heading_issues.txt")
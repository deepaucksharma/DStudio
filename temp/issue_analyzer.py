#!/usr/bin/env python3
"""
Analyze the cross-reference issues and categorize them by type.
"""

import re
from pathlib import Path

def analyze_issues():
    # Read the full report
    with open("/Users/deepaksharma/syc/DStudio/temp/cross_reference_report.md", "r") as f:
        content = f.read()
    
    # Extract all issues
    broken_links = re.findall(r'Line \d+: Broken link \'([^\']+)\' - target file not found', content)
    broken_anchors = re.findall(r'Line \d+: Broken anchor \'([^\']+)\' - anchor not found', content)
    heading_jumps = re.findall(r'Line \d+: Heading level jumps from h(\d+) to h(\d+)', content)
    duplicate_headings = re.findall(r'Line \d+: Duplicate heading text \'([^\']+)\'', content)
    
    # Categorize broken links
    missing_files = {}
    relative_path_issues = []
    
    for link in broken_links:
        if '../index.md' in link:
            relative_path_issues.append(link)
        elif '../' in link:
            # Extract the target filename
            target = link.split('/')[-1]
            if target not in missing_files:
                missing_files[target] = 0
            missing_files[target] += 1
        else:
            if link not in missing_files:
                missing_files[link] = 0
            missing_files[link] += 1
    
    # Generate analysis report
    report = []
    report.append("# Cross-Reference Issue Analysis")
    report.append("")
    
    report.append("## Summary of Issues")
    report.append(f"- Broken links: {len(broken_links)}")
    report.append(f"- Broken anchors: {len(broken_anchors)}")
    report.append(f"- Heading level jumps: {len(heading_jumps)}")
    report.append(f"- Duplicate headings: {len(duplicate_headings)}")
    report.append("")
    
    report.append("## Issue Categories")
    report.append("")
    
    # 1. Parent directory index references
    report.append("### 1. Parent Directory Index References")
    report.append(f"Many files reference '../index.md' which doesn't exist.")
    report.append(f"Count: {len(relative_path_issues)}")
    report.append("**Solution**: Remove or fix these references")
    report.append("")
    
    # 2. Most commonly missing files
    report.append("### 2. Most Commonly Referenced Missing Files")
    sorted_missing = sorted(missing_files.items(), key=lambda x: x[1], reverse=True)
    for filename, count in sorted_missing[:15]:
        report.append(f"- `{filename}`: {count} references")
    report.append("")
    
    # 3. Anchor issues
    report.append("### 3. Broken Anchors")
    anchor_patterns = {}
    for anchor in broken_anchors:
        if '#' in anchor:
            anchor_name = anchor.split('#')[-1]
            if anchor_name not in anchor_patterns:
                anchor_patterns[anchor_name] = 0
            anchor_patterns[anchor_name] += 1
    
    report.append("Most common broken anchors:")
    sorted_anchors = sorted(anchor_patterns.items(), key=lambda x: x[1], reverse=True)
    for anchor, count in sorted_anchors[:10]:
        report.append(f"- `#{anchor}`: {count} references")
    report.append("")
    
    # 4. Heading structure issues
    report.append("### 4. Heading Structure Issues")
    jump_patterns = {}
    for from_level, to_level in heading_jumps:
        pattern = f"h{from_level} -> h{to_level}"
        if pattern not in jump_patterns:
            jump_patterns[pattern] = 0
        jump_patterns[pattern] += 1
    
    report.append("Most common heading level jumps:")
    sorted_jumps = sorted(jump_patterns.items(), key=lambda x: x[1], reverse=True)
    for pattern, count in sorted_jumps:
        report.append(f"- {pattern}: {count} occurrences")
    report.append("")
    
    # 5. Recommendations
    report.append("## Recommendations")
    report.append("")
    report.append("### High Priority Fixes")
    report.append("1. **Remove or fix parent index references**: Many files reference '../index.md' which doesn't exist")
    report.append("2. **Create missing pattern files**: Many patterns are referenced but don't exist")
    report.append("3. **Fix broken anchors**: Update anchor links to match actual heading structures")
    report.append("")
    report.append("### Medium Priority Fixes")
    report.append("4. **Fix heading structure**: Avoid jumping heading levels (h1 -> h3)")
    report.append("5. **Remove duplicate headings**: Ensure unique headings within files")
    report.append("")
    report.append("### Pattern Analysis")
    
    # Check which patterns are missing
    docs_root = Path("/Users/deepaksharma/syc/DStudio/docs")
    existing_patterns = set()
    patterns_dir = docs_root / "patterns"
    if patterns_dir.exists():
        for pattern_file in patterns_dir.glob("*.md"):
            existing_patterns.add(pattern_file.name)
    
    missing_patterns = []
    for filename, count in sorted_missing:
        if filename.endswith('.md') and 'pattern' in filename.lower():
            if filename not in existing_patterns:
                missing_patterns.append((filename, count))
    
    if missing_patterns:
        report.append("")
        report.append("### Missing Pattern Files")
        for pattern, count in missing_patterns[:10]:
            report.append(f"- `{pattern}`: {count} references - **Should be created**")
    
    return "\n".join(report)

if __name__ == "__main__":
    analysis = analyze_issues()
    
    with open("/Users/deepaksharma/syc/DStudio/temp/issue_analysis.md", "w") as f:
        f.write(analysis)
    
    print("Issue analysis complete!")
    print("Report saved to: /Users/deepaksharma/syc/DStudio/temp/issue_analysis.md")
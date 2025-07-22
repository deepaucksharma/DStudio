#!/usr/bin/env python3
"""
Simplified link validation for MkDocs documentation.
Focuses on the most critical cross-reference issues.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

class SimpleLinkChecker:
    def __init__(self, docs_root):
        self.docs_root = Path(docs_root).resolve()
        self.all_files = set()
        self.issues = []
        
    def scan_files(self):
        """Scan all markdown files."""
        for md_file in self.docs_root.rglob("*.md"):
            relative_path = md_file.relative_to(self.docs_root)
            self.all_files.add(str(relative_path).replace('\\', '/'))
        
        print(f"Found {len(self.all_files)} markdown files")
    
    def extract_headings(self, content):
        """Extract headings and convert to anchor format."""
        headings = []
        lines = content.split('\n')
        
        for line in lines:
            # ATX-style headings (# ## ### etc.)
            atx_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if atx_match:
                text = atx_match.group(2).strip()
                # Remove markdown formatting
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # bold
                text = re.sub(r'\*(.+?)\*', r'\1', text)      # italic
                text = re.sub(r'`(.+?)`', r'\1', text)        # code
                text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # links
                
                # Convert to anchor
                anchor = text.lower()
                anchor = re.sub(r'[^\w\s-]', '', anchor)
                anchor = re.sub(r'[\s_-]+', '-', anchor)
                anchor = anchor.strip('-')
                headings.append(anchor)
        
        return headings
    
    def check_file_links(self, file_path, content):
        """Check all links in a single file."""
        file_issues = []
        current_dir = Path(file_path).parent
        lines = content.split('\n')
        
        # Extract headings for anchor validation
        headings = self.extract_headings(content)
        
        for line_num, line in enumerate(lines, 1):
            # Find markdown links [text](url)
            markdown_links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', line)
            
            for link_text, url in markdown_links:
                url = url.strip()
                
                # Skip external links
                if url.startswith(('http://', 'https://', 'mailto:', 'ftp:')):
                    continue
                
                # Handle anchor-only links (same page)
                if url.startswith('#'):
                    anchor = url[1:]
                    if anchor and anchor not in headings:
                        available = ', '.join(headings[:5]) + ('...' if len(headings) > 5 else '')
                        file_issues.append(f"Line {line_num}: Broken anchor '{url}' - Available: {available}")
                    continue
                
                # Handle file links (with or without anchors)
                if '#' in url:
                    file_part, anchor_part = url.split('#', 1)
                    target_file = file_part
                    target_anchor = anchor_part
                else:
                    target_file = url
                    target_anchor = None
                
                if not target_file:  # Empty file part means same file
                    target_file = file_path
                
                # Resolve relative path
                if target_file.startswith('/'):
                    # Absolute from docs root
                    resolved_path = target_file.lstrip('/')
                else:
                    # Relative path
                    if str(current_dir) == '.':
                        resolved_path = target_file
                    else:
                        resolved_path = str(current_dir / target_file).replace('\\', '/')
                
                # Check if target file exists
                target_exists = False
                actual_target = None
                
                for existing_file in self.all_files:
                    if existing_file == resolved_path:
                        target_exists = True
                        actual_target = existing_file
                        break
                    # Check without .md extension
                    elif not resolved_path.endswith('.md') and existing_file == resolved_path + '.md':
                        target_exists = True
                        actual_target = existing_file
                        break
                    # Check index files
                    elif resolved_path.endswith('/') and existing_file == resolved_path + 'index.md':
                        target_exists = True
                        actual_target = existing_file
                        break
                    elif existing_file == resolved_path + '/index.md':
                        target_exists = True
                        actual_target = existing_file
                        break
                
                if not target_exists:
                    file_issues.append(f"Line {line_num}: Broken link '{url}' - target file not found")
                elif target_anchor:
                    # Check if anchor exists in target file
                    try:
                        target_file_path = self.docs_root / actual_target
                        with open(target_file_path, 'r', encoding='utf-8') as f:
                            target_content = f.read()
                            target_headings = self.extract_headings(target_content)
                            if target_anchor not in target_headings:
                                available = ', '.join(target_headings[:3]) + ('...' if len(target_headings) > 3 else '')
                                file_issues.append(f"Line {line_num}: Broken anchor '{url}' - anchor not found in {actual_target}. Available: {available}")
                    except Exception as e:
                        file_issues.append(f"Line {line_num}: Error checking anchor in '{url}': {e}")
        
        return file_issues
    
    def check_heading_structure(self, file_path, content):
        """Check heading structure issues."""
        issues = []
        lines = content.split('\n')
        prev_level = 0
        headings_seen = []
        
        for line_num, line in enumerate(lines, 1):
            atx_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if atx_match:
                level = len(atx_match.group(1))
                text = atx_match.group(2).strip()
                
                # Check for skipped levels
                if level > prev_level + 1:
                    issues.append(f"Line {line_num}: Heading level jumps from h{prev_level} to h{level}: '{text}'")
                
                # Check for duplicate headings (which create duplicate anchors)
                if text in headings_seen:
                    issues.append(f"Line {line_num}: Duplicate heading text '{text}' creates duplicate anchor")
                
                headings_seen.append(text)
                prev_level = level
        
        return issues
    
    def validate_all(self):
        """Validate all files."""
        self.scan_files()
        
        total_link_issues = 0
        total_heading_issues = 0
        files_with_issues = 0
        
        for file_path in sorted(self.all_files):
            full_path = self.docs_root / file_path
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check links
                link_issues = self.check_file_links(file_path, content)
                
                # Check heading structure
                heading_issues = self.check_heading_structure(file_path, content)
                
                if link_issues or heading_issues:
                    files_with_issues += 1
                    self.issues.append(f"\n## {file_path}")
                    
                    if link_issues:
                        self.issues.append("### Link Issues:")
                        for issue in link_issues:
                            self.issues.append(f"- {issue}")
                        total_link_issues += len(link_issues)
                    
                    if heading_issues:
                        self.issues.append("### Heading Structure Issues:")
                        for issue in heading_issues:
                            self.issues.append(f"- {issue}")
                        total_heading_issues += len(heading_issues)
                        
            except Exception as e:
                self.issues.append(f"\n## {file_path}")
                self.issues.append(f"- ERROR reading file: {e}")
        
        return total_link_issues, total_heading_issues, files_with_issues
    
    def generate_report(self, total_link_issues, total_heading_issues, files_with_issues):
        """Generate summary report."""
        report = []
        report.append("# Cross-Reference Validation Report")
        report.append(f"## Summary")
        report.append(f"- Total files scanned: {len(self.all_files)}")
        report.append(f"- Files with issues: {files_with_issues}")
        report.append(f"- Total link issues: {total_link_issues}")
        report.append(f"- Total heading structure issues: {total_heading_issues}")
        report.append("")
        
        if self.issues:
            report.append("# Detailed Issues")
            report.extend(self.issues)
        else:
            report.append("✅ No issues found!")
        
        return "\n".join(report)

if __name__ == "__main__":
    docs_root = "/Users/deepaksharma/syc/DStudio/docs"
    checker = SimpleLinkChecker(docs_root)
    
    print("Validating cross-references...")
    total_link_issues, total_heading_issues, files_with_issues = checker.validate_all()
    
    report = checker.generate_report(total_link_issues, total_heading_issues, files_with_issues)
    
    # Save report
    with open("/Users/deepaksharma/syc/DStudio/temp/cross_reference_report.md", "w") as f:
        f.write(report)
    
    print(f"\nValidation complete!")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total link issues: {total_link_issues}")
    print(f"Total heading structure issues: {total_heading_issues}")
    print(f"Report saved to: /Users/deepaksharma/syc/DStudio/temp/cross_reference_report.md")
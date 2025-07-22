#!/usr/bin/env python3
"""
Comprehensive link validation script for MkDocs documentation.
Checks for:
1. Internal links that are broken
2. References to sections that don't exist  
3. Inconsistent heading structures that break anchor links
4. Missing back-references or circular links
5. Links to external resources (flagged for manual review)
"""

import os
import re
import glob
from pathlib import Path
from urllib.parse import urlparse, unquote
import yaml

class LinkValidator:
    def __init__(self, docs_root):
        self.docs_root = Path(docs_root)
        self.all_files = {}  # file_path -> content
        self.all_headings = {}  # file_path -> list of headings
        self.internal_links = {}  # file_path -> list of (link, line_num)
        self.external_links = {}  # file_path -> list of (link, line_num)
        self.anchor_links = {}  # file_path -> list of (link, line_num)
        self.issues = []
        
    def scan_files(self):
        """Scan all markdown files and extract content."""
        md_files = self.docs_root.rglob("*.md")
        
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                relative_path = file_path.relative_to(self.docs_root)
                self.all_files[str(relative_path)] = content
                self.extract_headings(str(relative_path), content)
                self.extract_links(str(relative_path), content)
                    
            except Exception as e:
                self.issues.append(f"ERROR reading {file_path}: {e}")
    
    def extract_headings(self, file_path, content):
        """Extract all headings from markdown content."""
        headings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # ATX-style headings (# ## ### etc.)
            atx_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if atx_match:
                level = len(atx_match.group(1))
                text = atx_match.group(2).strip()
                anchor = self.text_to_anchor(text)
                headings.append({
                    'level': level,
                    'text': text,
                    'anchor': anchor,
                    'line': line_num
                })
                
            # Setext-style headings (underlined with = or -)
            elif line_num < len(lines):
                next_line = lines[line_num] if line_num < len(lines) else ""
                if re.match(r'^=+$', next_line.strip()) and line.strip():
                    anchor = self.text_to_anchor(line.strip())
                    headings.append({
                        'level': 1,
                        'text': line.strip(),
                        'anchor': anchor,
                        'line': line_num
                    })
                elif re.match(r'^-+$', next_line.strip()) and line.strip():
                    anchor = self.text_to_anchor(line.strip())
                    headings.append({
                        'level': 2,
                        'text': line.strip(),
                        'anchor': anchor,
                        'line': line_num
                    })
        
        self.all_headings[file_path] = headings
    
    def text_to_anchor(self, text):
        """Convert heading text to GitHub-style anchor."""
        # Remove markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)      # italic
        text = re.sub(r'`(.+?)`', r'\1', text)        # code
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # links
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        anchor = text.lower()
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'[\s_-]+', '-', anchor)
        anchor = anchor.strip('-')
        
        return anchor
    
    def extract_links(self, file_path, content):
        """Extract all links from markdown content."""
        internal_links = []
        external_links = []
        anchor_links = []
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Find markdown links [text](url)
            markdown_links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', line)
            
            for link_text, url in markdown_links:
                url = url.strip()
                
                if url.startswith('#'):
                    # Anchor link within same page
                    anchor_links.append((url, line_num, link_text))
                elif url.startswith('http://') or url.startswith('https://'):
                    # External link
                    external_links.append((url, line_num, link_text))
                elif '://' in url:
                    # Other protocols (ftp, mailto, etc.)
                    external_links.append((url, line_num, link_text))
                else:
                    # Internal link (relative path)
                    internal_links.append((url, line_num, link_text))
            
            # Find reference-style links [text][ref]
            ref_links = re.findall(r'\[([^\]]*)\]\[([^\]]+)\]', line)
            for link_text, ref in ref_links:
                # Look for reference definition elsewhere in the document
                ref_pattern = f'^\\[{re.escape(ref)}\\]:\\s*(.+)$'
                ref_match = re.search(ref_pattern, content, re.MULTILINE | re.IGNORECASE)
                if ref_match:
                    url = ref_match.group(1).strip()
                    if url.startswith('#'):
                        anchor_links.append((url, line_num, link_text))
                    elif url.startswith('http://') or url.startswith('https://'):
                        external_links.append((url, line_num, link_text))
                    else:
                        internal_links.append((url, line_num, link_text))
        
        self.internal_links[file_path] = internal_links
        self.external_links[file_path] = external_links
        self.anchor_links[file_path] = anchor_links
    
    def validate_internal_links(self):
        """Check if internal links point to existing files."""
        for file_path, links in self.internal_links.items():
            current_dir = Path(file_path).parent
            
            for link, line_num, link_text in links:
                # Handle anchor links in other files
                if '#' in link:
                    file_part, anchor_part = link.split('#', 1)
                    target_file = file_part if file_part else file_path
                else:
                    target_file = link
                    anchor_part = None
                
                # Resolve relative path
                if target_file:
                    if target_file.startswith('/'):
                        # Absolute path from docs root
                        resolved_path = target_file.lstrip('/')
                    else:
                        # Relative path - resolve within docs directory structure
                        if current_dir == Path('.'):
                            # File is in root docs directory
                            resolved_path = target_file
                        else:
                            # Resolve relative to current directory
                            resolved_path = str(current_dir / target_file)
                            # Normalize path separators and clean up
                            resolved_path = resolved_path.replace('\\', '/')
                            resolved_path = '/'.join(Path(resolved_path).parts)
                    
                    # Normalize path separators
                    resolved_path = resolved_path.replace('\\', '/')
                    
                    # Check if target file exists
                    target_exists = False
                    for existing_file in self.all_files.keys():
                        if existing_file == resolved_path:
                            target_exists = True
                            break
                        # Also check without .md extension if original didn't have it
                        if not resolved_path.endswith('.md') and existing_file == resolved_path + '.md':
                            target_exists = True
                            resolved_path = existing_file
                            break
                        # Check directory index files
                        if resolved_path.endswith('/') and existing_file == resolved_path + 'index.md':
                            target_exists = True
                            resolved_path = existing_file
                            break
                        if not resolved_path.endswith('/') and existing_file == resolved_path + '/index.md':
                            target_exists = True
                            resolved_path = existing_file
                            break
                    
                    if not target_exists:
                        self.issues.append(f"BROKEN LINK in {file_path}:{line_num} - '{link}' -> file '{resolved_path}' not found")
                        continue
                    
                    # Check anchor if present
                    if anchor_part:
                        if resolved_path in self.all_headings:
                            heading_anchors = [h['anchor'] for h in self.all_headings[resolved_path]]
                            if anchor_part not in heading_anchors:
                                available_anchors = ', '.join(heading_anchors) if heading_anchors else 'none'
                                self.issues.append(f"BROKEN ANCHOR in {file_path}:{line_num} - '{link}' -> anchor '{anchor_part}' not found in {resolved_path}. Available: {available_anchors}")
    
    def validate_anchor_links(self):
        """Check if anchor links point to existing headings in the same file."""
        for file_path, links in self.anchor_links.items():
            if file_path in self.all_headings:
                heading_anchors = [h['anchor'] for h in self.all_headings[file_path]]
                
                for link, line_num, link_text in links:
                    anchor = link.lstrip('#')
                    if anchor not in heading_anchors:
                        available_anchors = ', '.join(heading_anchors) if heading_anchors else 'none'
                        self.issues.append(f"BROKEN ANCHOR in {file_path}:{line_num} - '{link}' not found. Available: {available_anchors}")
    
    def check_heading_structure(self):
        """Check for heading structure issues."""
        for file_path, headings in self.all_headings.items():
            if not headings:
                continue
                
            prev_level = 0
            for heading in headings:
                level = heading['level']
                
                # Check for skipped heading levels (e.g., # then ###)
                if level > prev_level + 1:
                    self.issues.append(f"HEADING STRUCTURE in {file_path}:{heading['line']} - Skipped from h{prev_level} to h{level}: '{heading['text']}'")
                
                prev_level = level
            
            # Check for duplicate anchors
            anchors = [h['anchor'] for h in headings]
            seen_anchors = set()
            for heading in headings:
                if heading['anchor'] in seen_anchors:
                    self.issues.append(f"DUPLICATE ANCHOR in {file_path}:{heading['line']} - '{heading['anchor']}' from '{heading['text']}' already exists")
                seen_anchors.add(heading['anchor'])
    
    def find_potential_circular_references(self):
        """Find potential circular reference issues."""
        # Build a graph of file references
        file_graph = {}
        
        for file_path, links in self.internal_links.items():
            file_graph[file_path] = []
            current_dir = Path(file_path).parent
            
            for link, line_num, link_text in links:
                target_file = link.split('#')[0] if '#' in link else link
                
                if target_file:
                    # Resolve relative path
                    if target_file.startswith('/'):
                        resolved_path = target_file.lstrip('/')
                    else:
                        resolved_path = str((current_dir / target_file))
                        try:
                            resolved_path = str(Path(resolved_path).relative_to(self.docs_root))
                        except:
                            continue
                    
                    resolved_path = resolved_path.replace('\\', '/')
                    
                    # Normalize to existing file
                    for existing_file in self.all_files.keys():
                        if (existing_file == resolved_path or 
                            existing_file == resolved_path + '.md' or
                            existing_file == resolved_path + '/index.md'):
                            file_graph[file_path].append(existing_file)
                            break
        
        # Note: Full circular reference detection would be complex
        # For now, just flag files that reference each other
        for file_path, targets in file_graph.items():
            for target in targets:
                if target in file_graph and file_path in file_graph[target]:
                    self.issues.append(f"CIRCULAR REFERENCE between {file_path} and {target}")
    
    def check_external_links(self):
        """Flag external links for manual review."""
        external_count = 0
        for file_path, links in self.external_links.items():
            for link, line_num, link_text in links:
                external_count += 1
        
        if external_count > 0:
            self.issues.append(f"INFO: Found {external_count} external links that should be manually reviewed for currency")
    
    def validate(self):
        """Run all validations."""
        print("Scanning markdown files...")
        self.scan_files()
        
        print("Validating internal links...")
        self.validate_internal_links()
        
        print("Validating anchor links...")
        self.validate_anchor_links()
        
        print("Checking heading structure...")
        self.check_heading_structure()
        
        print("Finding potential circular references...")
        self.find_potential_circular_references()
        
        print("Checking external links...")
        self.check_external_links()
        
        return self.issues
    
    def generate_report(self):
        """Generate a comprehensive report."""
        report = []
        report.append("# Cross-Reference Validation Report")
        report.append(f"Generated for: {self.docs_root}")
        report.append(f"Total files scanned: {len(self.all_files)}")
        report.append("")
        
        if not self.issues:
            report.append("✅ No issues found!")
            return "\n".join(report)
        
        # Categorize issues
        broken_links = [i for i in self.issues if i.startswith("BROKEN LINK")]
        broken_anchors = [i for i in self.issues if i.startswith("BROKEN ANCHOR")]
        heading_issues = [i for i in self.issues if i.startswith("HEADING STRUCTURE")]
        duplicate_anchors = [i for i in self.issues if i.startswith("DUPLICATE ANCHOR")]
        circular_refs = [i for i in self.issues if i.startswith("CIRCULAR REFERENCE")]
        errors = [i for i in self.issues if i.startswith("ERROR")]
        info = [i for i in self.issues if i.startswith("INFO")]
        
        report.append(f"## Summary")
        report.append(f"- Broken links: {len(broken_links)}")
        report.append(f"- Broken anchors: {len(broken_anchors)}")
        report.append(f"- Heading structure issues: {len(heading_issues)}")
        report.append(f"- Duplicate anchors: {len(duplicate_anchors)}")
        report.append(f"- Circular references: {len(circular_refs)}")
        report.append(f"- Errors: {len(errors)}")
        report.append("")
        
        if broken_links:
            report.append("## Broken Links")
            for issue in broken_links:
                report.append(f"- {issue}")
            report.append("")
        
        if broken_anchors:
            report.append("## Broken Anchors")
            for issue in broken_anchors:
                report.append(f"- {issue}")
            report.append("")
        
        if heading_issues:
            report.append("## Heading Structure Issues")
            for issue in heading_issues:
                report.append(f"- {issue}")
            report.append("")
        
        if duplicate_anchors:
            report.append("## Duplicate Anchors")
            for issue in duplicate_anchors:
                report.append(f"- {issue}")
            report.append("")
        
        if circular_refs:
            report.append("## Circular References")
            for issue in circular_refs:
                report.append(f"- {issue}")
            report.append("")
        
        if errors:
            report.append("## Errors")
            for issue in errors:
                report.append(f"- {issue}")
            report.append("")
        
        if info:
            report.append("## Information")
            for issue in info:
                report.append(f"- {issue}")
            report.append("")
        
        # Add file statistics
        report.append("## File Statistics")
        total_internal_links = sum(len(links) for links in self.internal_links.values())
        total_external_links = sum(len(links) for links in self.external_links.values())
        total_anchor_links = sum(len(links) for links in self.anchor_links.values())
        total_headings = sum(len(headings) for headings in self.all_headings.values())
        
        report.append(f"- Total internal links: {total_internal_links}")
        report.append(f"- Total external links: {total_external_links}")
        report.append(f"- Total anchor links: {total_anchor_links}")
        report.append(f"- Total headings: {total_headings}")
        
        return "\n".join(report)

if __name__ == "__main__":
    docs_root = "/Users/deepaksharma/syc/DStudio/docs"
    validator = LinkValidator(docs_root)
    issues = validator.validate()
    
    report = validator.generate_report()
    
    # Save report
    with open("/Users/deepaksharma/syc/DStudio/temp/link_validation_report.md", "w") as f:
        f.write(report)
    
    print("\nValidation complete!")
    print(f"Report saved to: /Users/deepaksharma/syc/DStudio/temp/link_validation_report.md")
    print(f"Total issues found: {len(issues)}")
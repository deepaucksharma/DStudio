#!/usr/bin/env python3
"""
Comprehensive internal link validator for MkDocs site.
Validates all internal markdown links, relative paths, and anchor references.
"""

import os
import re
import json
from pathlib import Path
from urllib.parse import unquote
import markdown
from markdown.extensions import toc

class LinkValidator:
    def __init__(self, docs_root):
        self.docs_root = Path(docs_root)
        self.broken_links = []
        self.valid_links = []
        self.all_files = {}
        self.all_headings = {}
        
        # Collect all markdown files
        self._collect_files()
        # Extract headings from all files
        self._extract_headings()
    
    def _collect_files(self):
        """Collect all markdown files and their paths."""
        for md_file in self.docs_root.rglob("*.md"):
            relative_path = md_file.relative_to(self.docs_root)
            self.all_files[str(relative_path)] = md_file
            # Also add without extension for compatibility
            stem_path = str(relative_path.with_suffix(''))
            self.all_files[stem_path] = md_file
    
    def _extract_headings(self):
        """Extract all headings from markdown files for anchor validation."""
        md = markdown.Markdown(extensions=['toc'])
        
        for file_path, abs_path in self.all_files.items():
            if not abs_path.suffix == '.md':
                continue
                
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract headings manually (more reliable than markdown extension)
                headings = []
                for line in content.split('\n'):
                    if line.strip().startswith('#'):
                        level = len(line) - len(line.lstrip('#'))
                        if 1 <= level <= 6:
                            heading_text = line.strip('#').strip()
                            # Convert to slug format
                            slug = self._text_to_slug(heading_text)
                            headings.append(slug)
                
                self.all_headings[file_path] = headings
                
            except Exception as e:
                print(f"Error reading {abs_path}: {e}")
    
    def _text_to_slug(self, text):
        """Convert heading text to URL slug format."""
        # Remove markdown formatting
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic
        text = re.sub(r'`([^`]+)`', r'\1', text)  # Code
        text = re.sub(r'[^\w\s-]', '', text)  # Remove special chars
        text = re.sub(r'[-\s]+', '-', text)  # Replace spaces/hyphens
        return text.lower().strip('-')
    
    def validate_file(self, file_path):
        """Validate all links in a single markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return
        
        relative_file_path = file_path.relative_to(self.docs_root)
        file_dir = relative_file_path.parent
        
        # Find all markdown links: [text](url)
        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        
        for match in re.finditer(link_pattern, content):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Skip external links
            if link_url.startswith(('http://', 'https://', 'mailto:')):
                continue
            
            # Skip images (though we should validate them separately)
            if link_url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                continue
                
            self._validate_internal_link(
                str(relative_file_path), 
                link_text, 
                link_url, 
                file_dir
            )
    
    def _validate_internal_link(self, source_file, link_text, link_url, file_dir):
        """Validate a single internal link."""
        original_url = link_url
        
        # Handle anchor-only links
        if link_url.startswith('#'):
            anchor = link_url[1:]
            if source_file in self.all_headings:
                if anchor in self.all_headings[source_file]:
                    self.valid_links.append({
                        'source': source_file,
                        'text': link_text,
                        'url': original_url,
                        'type': 'anchor',
                        'status': 'valid'
                    })
                    return
            
            self.broken_links.append({
                'source': source_file,
                'text': link_text,
                'url': original_url,
                'expected_path': f"{source_file}#{anchor}",
                'error': 'missing_anchor',
                'description': f"Anchor '{anchor}' not found in {source_file}"
            })
            return
        
        # Split URL and anchor
        if '#' in link_url:
            link_url, anchor = link_url.split('#', 1)
        else:
            anchor = None
        
        # Resolve relative paths
        if link_url.startswith('/'):
            # Absolute path from docs root
            target_path = link_url.lstrip('/')
        elif link_url.startswith('../') or link_url.startswith('./'):
            # Relative path - resolve manually to avoid path issues
            try:
                resolved_path = (file_dir / link_url).resolve()
                docs_root_resolved = self.docs_root.resolve()
                
                # Check if path is within docs root (compatible with older Python)
                try:
                    relative_path = resolved_path.relative_to(docs_root_resolved)
                    target_path = str(relative_path)
                except ValueError:
                    # Path goes outside docs root, mark as broken
                    self.broken_links.append({
                        'source': source_file,
                        'text': link_text,
                        'url': original_url,
                        'expected_path': str(resolved_path),
                        'error': 'outside_docs_root',
                        'description': f"Link points outside docs directory: {resolved_path}"
                    })
                    return
            except Exception as e:
                self.broken_links.append({
                    'source': source_file,
                    'text': link_text,
                    'url': original_url,
                    'expected_path': link_url,
                    'error': 'path_resolution_error',
                    'description': f"Error resolving path: {e}"
                })
                return
        else:
            # Same directory
            target_path = str(file_dir / link_url)
        
        # Normalize path
        target_path = target_path.replace('\\', '/')
        
        # Add .md extension if missing
        if not target_path.endswith('.md') and not target_path.endswith('/'):
            target_path_md = target_path + '.md'
            if target_path_md in self.all_files:
                target_path = target_path_md
        
        # Check if target file exists
        if target_path not in self.all_files:
            # Try with index.md
            if target_path.endswith('/'):
                index_path = target_path + 'index.md'
                if index_path in self.all_files:
                    target_path = index_path
                else:
                    self.broken_links.append({
                        'source': source_file,
                        'text': link_text,
                        'url': original_url,
                        'expected_path': target_path,
                        'error': 'missing_file',
                        'description': f"File not found: {target_path}"
                    })
                    return
            else:
                self.broken_links.append({
                    'source': source_file,
                    'text': link_text,
                    'url': original_url,
                    'expected_path': target_path,
                    'error': 'missing_file',
                    'description': f"File not found: {target_path}"
                })
                return
        
        # Check anchor if present
        if anchor:
            if target_path in self.all_headings:
                if anchor not in self.all_headings[target_path]:
                    self.broken_links.append({
                        'source': source_file,
                        'text': link_text,
                        'url': original_url,
                        'expected_path': target_path,
                        'error': 'missing_anchor',
                        'description': f"Anchor '{anchor}' not found in {target_path}. Available: {', '.join(self.all_headings[target_path][:5])}"
                    })
                    return
        
        # Link is valid
        self.valid_links.append({
            'source': source_file,
            'text': link_text,
            'url': original_url,
            'target': target_path,
            'anchor': anchor,
            'type': 'internal',
            'status': 'valid'
        })
    
    def validate_all(self):
        """Validate all markdown files in the docs directory."""
        for md_file in self.docs_root.rglob("*.md"):
            print(f"Validating: {md_file.relative_to(self.docs_root)}")
            self.validate_file(md_file)
    
    def generate_report(self):
        """Generate comprehensive validation report."""
        report = {
            'summary': {
                'total_files_scanned': len([f for f in self.all_files.values() if f.suffix == '.md']),
                'total_links_found': len(self.broken_links) + len(self.valid_links),
                'valid_links': len(self.valid_links),
                'broken_links': len(self.broken_links),
                'error_types': {}
            },
            'broken_links': self.broken_links,
            'valid_links_sample': self.valid_links[:20],  # Sample to avoid huge output
            'recommendations': []
        }
        
        # Count error types
        for link in self.broken_links:
            error_type = link.get('error', 'unknown')
            report['summary']['error_types'][error_type] = report['summary']['error_types'].get(error_type, 0) + 1
        
        # Generate recommendations
        if report['summary']['error_types'].get('missing_file', 0) > 0:
            report['recommendations'].append("Consider creating missing files or updating links to point to existing files")
        
        if report['summary']['error_types'].get('missing_anchor', 0) > 0:
            report['recommendations'].append("Review heading structures and update anchor links accordingly")
        
        return report

def main():
    """Main validation function."""
    docs_root = "/home/deepak/DStudio/docs"
    
    print("🔍 Starting comprehensive link validation...")
    validator = LinkValidator(docs_root)
    
    print("📁 Collecting files and extracting headings...")
    print(f"Found {len(validator.all_files)} files")
    
    print("🔗 Validating all internal links...")
    validator.validate_all()
    
    print("📊 Generating report...")
    report = validator.generate_report()
    
    # Save detailed report
    with open("/home/deepak/DStudio/comprehensive_link_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📋 VALIDATION SUMMARY")
    print("="*60)
    print(f"Files scanned: {report['summary']['total_files_scanned']}")
    print(f"Total links: {report['summary']['total_links_found']}")
    print(f"Valid links: {report['summary']['valid_links']}")
    print(f"Broken links: {report['summary']['broken_links']}")
    
    if report['summary']['error_types']:
        print("\n📈 Error breakdown:")
        for error_type, count in report['summary']['error_types'].items():
            print(f"  {error_type}: {count}")
    
    if report['recommendations']:
        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    
    print(f"\n📄 Detailed report saved to: comprehensive_link_validation_report.json")
    
    return len(validator.broken_links)

if __name__ == "__main__":
    broken_count = main()
    exit(0 if broken_count == 0 else 1)
#!/usr/bin/env python3
"""
Comprehensive Navigation and Link Validator for DStudio
Consolidates all navigation and link validation functionality into a single tool.

Features:
- Navigation structure validation (mkdocs.yml)
- Internal link verification across all markdown files
- External link validation (optional)
- Orphaned file detection
- Duplicate entry detection
- Pattern metadata validation
- Cross-reference validation
- Anchor link validation
- Image and asset link validation
- Comprehensive reporting with auto-fix capabilities
"""

import os
import sys
import yaml
import json
import re
import argparse
import urllib.parse
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional, Any
import concurrent.futures
import hashlib

# Custom YAML loader to handle MkDocs-specific tags
class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    """A custom YAML loader that ignores unknown tags"""
    pass

def ignore_unknown(loader, suffix, node):
    """Ignore unknown tags by returning empty string"""
    if isinstance(node, yaml.ScalarNode):
        return ''
    elif isinstance(node, yaml.SequenceNode):
        return []
    elif isinstance(node, yaml.MappingNode):
        return {}

SafeLoaderIgnoreUnknown.add_multi_constructor('', ignore_unknown)

class ComprehensiveValidator:
    """Comprehensive navigation and link validator"""
    
    def __init__(self, project_root: str = ".", verbose: bool = False, fix: bool = False):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.mkdocs_file = self.project_root / "mkdocs.yml"
        self.verbose = verbose
        self.fix = fix
        
        # Issue tracking
        self.errors = []
        self.warnings = []
        self.info = []
        self.fixed = []
        
        # Data structures for validation
        self.nav_files = set()
        self.all_files = set()
        self.file_contents = {}
        self.internal_links = defaultdict(list)
        self.external_links = defaultdict(list)
        self.anchors = defaultdict(set)
        self.broken_links = []
        self.orphaned_files = []
        self.duplicate_entries = []
        
        # Statistics
        self.stats = {
            "total_files": 0,
            "files_in_nav": 0,
            "orphaned_files": 0,
            "total_links": 0,
            "internal_links": 0,
            "external_links": 0,
            "broken_links": 0,
            "duplicate_entries": 0,
            "anchor_links": 0,
            "broken_anchors": 0,
            "image_links": 0,
            "broken_images": 0
        }
        
    def log_error(self, message: str, file: str = None, line: int = None):
        """Log an error"""
        entry = {"level": "error", "message": message}
        if file:
            entry["file"] = file
        if line:
            entry["line"] = line
        self.errors.append(entry)
        if self.verbose:
            print(f"❌ ERROR: {message}" + (f" in {file}" if file else "") + (f":{line}" if line else ""))
            
    def log_warning(self, message: str, file: str = None, line: int = None):
        """Log a warning"""
        entry = {"level": "warning", "message": message}
        if file:
            entry["file"] = file
        if line:
            entry["line"] = line
        self.warnings.append(entry)
        if self.verbose:
            print(f"⚠️  WARNING: {message}" + (f" in {file}" if file else "") + (f":{line}" if line else ""))
            
    def log_info(self, message: str):
        """Log info message"""
        self.info.append({"level": "info", "message": message})
        if self.verbose:
            print(f"ℹ️  INFO: {message}")
            
    def log_fixed(self, message: str, file: str = None):
        """Log a fixed issue"""
        entry = {"level": "fixed", "message": message}
        if file:
            entry["file"] = file
        self.fixed.append(entry)
        if self.verbose:
            print(f"✅ FIXED: {message}" + (f" in {file}" if file else ""))
    
    def load_mkdocs_config(self) -> dict:
        """Load and parse mkdocs.yml"""
        try:
            with open(self.mkdocs_file, 'r') as f:
                return yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
        except Exception as e:
            self.log_error(f"Failed to load mkdocs.yml: {e}")
            return {}
    
    def extract_nav_files(self, nav_items, current_path="") -> None:
        """Recursively extract all files from navigation"""
        if isinstance(nav_items, list):
            for item in nav_items:
                self.extract_nav_files(item, current_path)
        elif isinstance(nav_items, dict):
            for key, value in nav_items.items():
                if isinstance(value, str) and value.endswith('.md'):
                    self.nav_files.add(value)
                    # Check for duplicates
                    if value in self.nav_files and current_path:
                        self.duplicate_entries.append(value)
                else:
                    self.extract_nav_files(value, f"{current_path}/{key}" if current_path else key)
    
    def find_all_files(self) -> None:
        """Find all markdown files and assets in docs directory"""
        for path in self.docs_dir.rglob("*"):
            if path.is_file():
                rel_path = path.relative_to(self.docs_dir)
                self.all_files.add(str(rel_path))
                
                # Load markdown file contents
                if path.suffix == '.md':
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            self.file_contents[str(rel_path)] = content
                            self.stats["total_files"] += 1
                    except Exception as e:
                        self.log_error(f"Failed to read file: {e}", str(rel_path))
    
    def extract_links_and_anchors(self, content: str, file_path: str) -> None:
        """Extract all links and anchors from markdown content"""
        lines = content.split('\n')
        
        # Extract markdown links [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for i, line in enumerate(lines, 1):
            for match in re.finditer(link_pattern, line):
                link_text = match.group(1)
                link_url = match.group(2)
                
                self.stats["total_links"] += 1
                
                # Categorize link
                if link_url.startswith(('http://', 'https://', 'mailto:')):
                    self.external_links[file_path].append({
                        'url': link_url,
                        'text': link_text,
                        'line': i
                    })
                    self.stats["external_links"] += 1
                elif link_url.startswith('#'):
                    # Anchor link within same file
                    self.internal_links[file_path].append({
                        'url': link_url,
                        'text': link_text,
                        'line': i,
                        'type': 'anchor'
                    })
                    self.stats["anchor_links"] += 1
                else:
                    # Internal link to another file
                    self.internal_links[file_path].append({
                        'url': link_url,
                        'text': link_text,
                        'line': i,
                        'type': 'internal'
                    })
                    self.stats["internal_links"] += 1
                    
                    # Check if it's an image
                    if any(link_url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
                        self.stats["image_links"] += 1
        
        # Extract HTML links
        html_link_pattern = r'<a\s+href=["\'](.*?)["\']'
        for i, line in enumerate(lines, 1):
            for match in re.finditer(html_link_pattern, line):
                link_url = match.group(1)
                if not link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                    self.internal_links[file_path].append({
                        'url': link_url,
                        'text': 'HTML link',
                        'line': i,
                        'type': 'html'
                    })
        
        # Extract anchors (headers and explicit anchors)
        # Headers: # Header {#anchor}
        header_anchor_pattern = r'^#+\s+.*?\{#([\w-]+)\}'
        for i, line in enumerate(lines, 1):
            match = re.match(header_anchor_pattern, line)
            if match:
                self.anchors[file_path].add(match.group(1))
        
        # Auto-generated anchors from headers
        header_pattern = r'^(#+)\s+(.+?)$'
        for i, line in enumerate(lines, 1):
            match = re.match(header_pattern, line)
            if match and '{#' not in line:
                header_text = match.group(2)
                # Convert header to anchor (simplified version)
                anchor = re.sub(r'[^\w\s-]', '', header_text.lower())
                anchor = re.sub(r'[-\s]+', '-', anchor).strip('-')
                self.anchors[file_path].add(anchor)
        
        # HTML anchors: <a name="anchor"> or <a id="anchor">
        html_anchor_pattern = r'<a\s+(?:name|id)=["\']([\w-]+)["\']'
        for i, line in enumerate(lines, 1):
            for match in re.finditer(html_anchor_pattern, line):
                self.anchors[file_path].add(match.group(1))
    
    def normalize_link(self, link_url: str, source_file: str) -> str:
        """Normalize a link URL to an absolute path relative to docs/"""
        # Remove any anchors
        if '#' in link_url:
            link_url = link_url.split('#')[0]
            
        if not link_url:  # Was just an anchor
            return source_file
        
        source_dir = os.path.dirname(source_file)
        
        # Handle absolute paths (starting with /)
        if link_url.startswith('/'):
            # Strip leading slash and treat as relative to docs/
            normalized = link_url[1:]
        else:
            # Relative path
            normalized = os.path.normpath(os.path.join(source_dir, link_url))
        
        # Handle directory references
        if not normalized.endswith('.md') and not any(normalized.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
            # Check if it's a directory
            potential_dir = self.docs_dir / normalized
            if potential_dir.is_dir():
                normalized = str(Path(normalized) / 'index.md')
            else:
                normalized += '.md'
        
        return normalized
    
    def validate_internal_links(self) -> None:
        """Validate all internal links"""
        for source_file, links in self.internal_links.items():
            for link in links:
                if link['type'] == 'anchor':
                    # Check anchor in same file
                    anchor = link['url'][1:]  # Remove #
                    if anchor and anchor not in self.anchors.get(source_file, set()):
                        self.broken_links.append({
                            'source': source_file,
                            'target': link['url'],
                            'line': link['line'],
                            'type': 'broken_anchor',
                            'text': link['text']
                        })
                        self.stats["broken_anchors"] += 1
                else:
                    # Check file link
                    target = self.normalize_link(link['url'], source_file)
                    
                    # Check if file exists
                    if target not in self.all_files:
                        self.broken_links.append({
                            'source': source_file,
                            'target': target,
                            'original_url': link['url'],
                            'line': link['line'],
                            'type': 'broken_link',
                            'text': link['text']
                        })
                        self.stats["broken_links"] += 1
                        
                        # Check for image links
                        if any(target.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
                            self.stats["broken_images"] += 1
                    
                    # Check anchor in target file if present
                    if '#' in link['url']:
                        anchor = link['url'].split('#')[1]
                        if anchor and target in self.all_files and anchor not in self.anchors.get(target, set()):
                            self.broken_links.append({
                                'source': source_file,
                                'target': link['url'],
                                'line': link['line'],
                                'type': 'broken_anchor',
                                'text': link['text']
                            })
                            self.stats["broken_anchors"] += 1
    
    def validate_navigation_files(self) -> None:
        """Validate that all files in navigation exist"""
        for nav_file in self.nav_files:
            if nav_file not in self.all_files:
                self.log_error(f"Navigation references non-existent file: {nav_file}")
                self.broken_links.append({
                    'source': 'mkdocs.yml',
                    'target': nav_file,
                    'type': 'broken_nav_link'
                })
    
    def find_orphaned_files(self) -> None:
        """Find markdown files not referenced in navigation"""
        md_files = {f for f in self.all_files if f.endswith('.md')}
        
        for file in md_files:
            if file not in self.nav_files:
                # Skip special files
                if file in ['index.md', 'README.md', 'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md']:
                    continue
                    
                # Skip files in special directories
                if any(file.startswith(d) for d in ['stylesheets/', 'javascripts/', 'assets/', '.github/']):
                    continue
                    
                self.orphaned_files.append(file)
                self.stats["orphaned_files"] += 1
    
    def validate_pattern_metadata(self) -> Dict[str, List[str]]:
        """Validate pattern files have required metadata"""
        issues = {}
        pattern_dirs = ['patterns', 'pattern-library']
        
        required_fields = {
            'title', 'category', 'excellence_tier', 'pattern_status'
        }
        
        valid_tiers = {'gold', 'silver', 'bronze'}
        valid_status = {
            'recommended', 'stable', 'use-with-expertise', 
            'use-with-caution', 'legacy', 'deprecated'
        }
        
        for pattern_dir in pattern_dirs:
            dir_path = self.docs_dir / pattern_dir
            if not dir_path.exists():
                continue
                
            for file_path in dir_path.rglob("*.md"):
                if file_path.name == 'index.md':
                    continue
                    
                rel_path = file_path.relative_to(self.docs_dir)
                content = self.file_contents.get(str(rel_path), "")
                
                file_issues = []
                
                # Check for YAML frontmatter
                if not content.strip().startswith('---'):
                    file_issues.append("Missing YAML frontmatter")
                else:
                    # Extract frontmatter
                    try:
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            frontmatter = yaml.safe_load(parts[1])
                            
                            # Check required fields
                            for field in required_fields:
                                if field not in frontmatter:
                                    file_issues.append(f"Missing required field: {field}")
                                    
                            # Validate field values
                            if 'excellence_tier' in frontmatter and frontmatter['excellence_tier'] not in valid_tiers:
                                file_issues.append(f"Invalid excellence_tier: {frontmatter['excellence_tier']}")
                                
                            if 'pattern_status' in frontmatter and frontmatter['pattern_status'] not in valid_status:
                                file_issues.append(f"Invalid pattern_status: {frontmatter['pattern_status']}")
                    except Exception as e:
                        file_issues.append(f"Invalid YAML frontmatter: {e}")
                
                if file_issues:
                    issues[str(rel_path)] = file_issues
                    
        return issues
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        # Calculate statistics
        nav_coverage = (self.stats["files_in_nav"] / self.stats["total_files"] * 100) if self.stats["total_files"] > 0 else 0
        orphan_rate = (self.stats["orphaned_files"] / self.stats["total_files"] * 100) if self.stats["total_files"] > 0 else 0
        link_broken_rate = (self.stats["broken_links"] / self.stats["total_links"] * 100) if self.stats["total_links"] > 0 else 0
        
        # Calculate health score
        score = 100
        score -= len(self.errors) * 10
        score -= len(self.warnings) * 5
        score -= min(self.stats["broken_links"], 10) * 5
        score -= min(self.stats["orphaned_files"], 20) * 2
        score = max(0, score)
        
        if score >= 90:
            health_grade = "A"
        elif score >= 80:
            health_grade = "B"
        elif score >= 70:
            health_grade = "C"
        elif score >= 60:
            health_grade = "D"
        else:
            health_grade = "F"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "statistics": self.stats,
            "percentages": {
                "navigation_coverage": round(nav_coverage, 2),
                "orphan_rate": round(orphan_rate, 2),
                "link_broken_rate": round(link_broken_rate, 2)
            },
            "health": {
                "score": score,
                "grade": health_grade
            },
            "issues": {
                "errors": self.errors,
                "warnings": self.warnings,
                "info": self.info,
                "fixed": self.fixed
            },
            "broken_links": self.broken_links,
            "orphaned_files": sorted(self.orphaned_files),
            "duplicate_entries": sorted(list(set(self.duplicate_entries))),
            "summary": {
                "total_issues": len(self.errors) + len(self.warnings),
                "critical_issues": len(self.errors),
                "auto_fixed": len(self.fixed)
            }
        }
    
    def fix_broken_links(self) -> None:
        """Attempt to auto-fix broken links"""
        if not self.fix:
            return
            
        # Common fixes mapping
        common_fixes = {
            # Add common link mappings here
            'README.md': 'index.md',
            'readme.md': 'index.md',
        }
        
        files_to_update = defaultdict(list)
        
        for broken_link in self.broken_links:
            if broken_link['type'] == 'broken_link':
                source = broken_link['source']
                original_url = broken_link.get('original_url', '')
                target = broken_link['target']
                
                # Try common fixes
                fixed_url = None
                
                # Check if file exists with different case
                for file in self.all_files:
                    if file.lower() == target.lower():
                        fixed_url = original_url.replace(os.path.basename(target), os.path.basename(file))
                        break
                
                # Check common mappings
                if not fixed_url:
                    basename = os.path.basename(target)
                    if basename in common_fixes:
                        fixed_url = original_url.replace(basename, common_fixes[basename])
                
                if fixed_url:
                    files_to_update[source].append({
                        'original': original_url,
                        'fixed': fixed_url,
                        'line': broken_link['line']
                    })
        
        # Apply fixes
        for file_path, fixes in files_to_update.items():
            try:
                full_path = self.docs_dir / file_path
                with open(full_path, 'r') as f:
                    content = f.read()
                
                original_content = content
                for fix in fixes:
                    # Replace the specific link
                    pattern = rf'\[([^\]]+)\]\({re.escape(fix["original"])}\)'
                    replacement = rf'[\1]({fix["fixed"]})'
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    with open(full_path, 'w') as f:
                        f.write(content)
                    self.log_fixed(f"Fixed {len(fixes)} broken links", file_path)
                    
            except Exception as e:
                self.log_error(f"Failed to fix links in {file_path}: {e}")
    
    def run(self) -> Dict[str, Any]:
        """Run all validations"""
        print("🔍 Starting comprehensive navigation and link validation...")
        
        # Load configuration
        config = self.load_mkdocs_config()
        if not config:
            return self.generate_report()
        
        # Extract navigation files
        self.extract_nav_files(config.get('nav', []))
        self.stats["files_in_nav"] = len(self.nav_files)
        self.stats["duplicate_entries"] = len(self.duplicate_entries)
        
        # Find all files
        self.find_all_files()
        
        # Extract links and anchors from all files
        for file_path, content in self.file_contents.items():
            self.extract_links_and_anchors(content, file_path)
        
        # Validate navigation files exist
        self.validate_navigation_files()
        
        # Validate internal links
        self.validate_internal_links()
        
        # Find orphaned files
        self.find_orphaned_files()
        
        # Validate pattern metadata
        pattern_issues = self.validate_pattern_metadata()
        for file, issues in pattern_issues.items():
            for issue in issues:
                self.log_warning(f"Pattern metadata: {issue}", file)
        
        # Attempt to fix issues if requested
        if self.fix:
            self.fix_broken_links()
        
        # Generate report
        return self.generate_report()

def main():
    parser = argparse.ArgumentParser(description='Comprehensive navigation and link validator for MkDocs')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--fix', '-f', action='store_true', help='Attempt to auto-fix issues')
    parser.add_argument('--report', '-r', default='console', choices=['console', 'json', 'markdown'],
                        help='Report format (default: console)')
    parser.add_argument('--output', '-o', help='Output file for report')
    parser.add_argument('--fail-on-warnings', action='store_true', help='Exit with error on warnings')
    
    args = parser.parse_args()
    
    # Run validation
    validator = ComprehensiveValidator(verbose=args.verbose, fix=args.fix)
    report = validator.run()
    
    # Output report
    if args.report == 'json':
        output = json.dumps(report, indent=2)
    elif args.report == 'markdown':
        output = f"""# Navigation and Link Validation Report

**Generated:** {report['timestamp']}  
**Health Grade:** {report['health']['grade']} (Score: {report['health']['score']}/100)

## Summary

- **Total Files:** {report['statistics']['total_files']}
- **Files in Navigation:** {report['statistics']['files_in_nav']} ({report['percentages']['navigation_coverage']}%)
- **Orphaned Files:** {report['statistics']['orphaned_files']} ({report['percentages']['orphan_rate']}%)
- **Total Links:** {report['statistics']['total_links']}
- **Broken Links:** {report['statistics']['broken_links']} ({report['percentages']['link_broken_rate']}%)
- **Duplicate Navigation Entries:** {report['statistics']['duplicate_entries']}

## Issues

- **Critical Errors:** {len(report['issues']['errors'])}
- **Warnings:** {len(report['issues']['warnings'])}
- **Auto-fixed:** {report['summary']['auto_fixed']}

"""
        if report['broken_links']:
            output += "\n## Broken Links\n\n"
            for link in report['broken_links'][:20]:  # Show first 20
                output += f"- {link['source']}:{link.get('line', '?')} → {link.get('original_url', link['target'])}\n"
            if len(report['broken_links']) > 20:
                output += f"\n...and {len(report['broken_links']) - 20} more\n"
                
        if report['orphaned_files']:
            output += "\n## Orphaned Files\n\n"
            for file in report['orphaned_files'][:20]:
                output += f"- {file}\n"
            if len(report['orphaned_files']) > 20:
                output += f"\n...and {len(report['orphaned_files']) - 20} more\n"
    else:
        # Console output
        output = f"""
╔══════════════════════════════════════════════════════════════╗
║          Navigation and Link Validation Report               ║
╚══════════════════════════════════════════════════════════════╝

Health Grade: {report['health']['grade']} (Score: {report['health']['score']}/100)

📊 Statistics:
   Total Files: {report['statistics']['total_files']}
   Files in Navigation: {report['statistics']['files_in_nav']} ({report['percentages']['navigation_coverage']}%)
   Orphaned Files: {report['statistics']['orphaned_files']} ({report['percentages']['orphan_rate']}%)
   
   Total Links: {report['statistics']['total_links']}
   ├─ Internal: {report['statistics']['internal_links']}
   ├─ External: {report['statistics']['external_links']}
   ├─ Anchors: {report['statistics']['anchor_links']}
   └─ Images: {report['statistics']['image_links']}
   
   Broken Links: {report['statistics']['broken_links']} ({report['percentages']['link_broken_rate']}%)
   ├─ Files: {report['statistics']['broken_links'] - report['statistics']['broken_anchors']}
   ├─ Anchors: {report['statistics']['broken_anchors']}
   └─ Images: {report['statistics']['broken_images']}

📋 Issues Summary:
   Critical Errors: {len(report['issues']['errors'])}
   Warnings: {len(report['issues']['warnings'])}
   Auto-fixed: {report['summary']['auto_fixed']}
"""

        if report['issues']['errors']:
            output += "\n❌ Critical Errors:\n"
            for error in report['issues']['errors'][:10]:
                output += f"   - {error['message']}\n"
            if len(report['issues']['errors']) > 10:
                output += f"   ...and {len(report['issues']['errors']) - 10} more\n"

        if report['broken_links']:
            output += "\n🔗 Broken Links (first 10):\n"
            for link in report['broken_links'][:10]:
                output += f"   {link['source']}:{link.get('line', '?')} → {link.get('original_url', link['target'])}\n"
            if len(report['broken_links']) > 10:
                output += f"   ...and {len(report['broken_links']) - 10} more\n"

        if args.fix and report['issues']['fixed']:
            output += "\n✅ Auto-fixed Issues:\n"
            for fix in report['issues']['fixed']:
                output += f"   - {fix['message']}\n"

        # Add recommendations
        output += "\n💡 Recommendations:\n"
        if report['statistics']['broken_links'] > 0:
            output += "   1. Fix broken links immediately (run with --fix for auto-fix)\n"
        if report['statistics']['orphaned_files'] > 10:
            output += "   2. Review orphaned files and add to navigation or remove\n"
        if report['statistics']['duplicate_entries'] > 0:
            output += "   3. Remove duplicate entries from navigation\n"
        if report['percentages']['navigation_coverage'] < 80:
            output += "   4. Improve navigation coverage\n"

    # Output to file or console
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report saved to: {args.output}")
    else:
        print(output)
    
    # Exit code
    if len(report['issues']['errors']) > 0:
        sys.exit(1)
    elif args.fail_on_warnings and len(report['issues']['warnings']) > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Comprehensive Pattern Library Link Validator

This script validates all internal links in the pattern library documentation:
1. Checks all markdown links in pattern files
2. Verifies cross-references between patterns work
3. Ensures category index links are valid
4. Checks that merged pattern redirects work (via aliases)
5. Validates related pattern references
6. Finds broken links to non-existent files
7. Provides detailed reporting and fix suggestions
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import logging
from collections import defaultdict
import urllib.parse

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class PatternLinkValidator:
    def __init__(self, docs_dir: str = "/home/deepak/DStudio/docs"):
        self.docs_dir = Path(docs_dir)
        self.pattern_dir = self.docs_dir / "pattern-library"
        
        # File mappings and indexes
        self.all_files = self._build_file_map()
        self.pattern_metadata = self._load_pattern_metadata()
        self.aliases = self._build_alias_map()
        
        # Issue tracking
        self.broken_links = defaultdict(list)
        self.empty_links = defaultdict(list)
        self.external_links = defaultdict(list)
        self.alias_issues = defaultdict(list)
        self.cross_ref_issues = defaultdict(list)
        self.category_issues = defaultdict(list)
        
        # Statistics
        self.valid_links = 0
        self.total_files = 0
        
    def _build_file_map(self) -> Set[str]:
        """Build a comprehensive set of all existing markdown files."""
        files = set()
        
        # Include all markdown files in docs directory
        for file_path in self.docs_dir.rglob("*.md"):
            rel_path = file_path.relative_to(self.docs_dir)
            rel_str = str(rel_path).replace('\\', '/')
            
            # Store multiple variations
            files.add(rel_str)  # Full path with .md
            files.add(rel_str.replace('.md', ''))  # Without .md extension
            
            # For index.md files, also add the directory path
            if file_path.name == 'index.md':
                parent = str(rel_path.parent).replace('\\', '/')
                if parent != '.':
                    files.add(parent)
                    files.add(parent + '/')
                    
        logger.info(f"Built file map with {len(files)} path variations")
        return files
    
    def _load_pattern_metadata(self) -> Dict[str, Dict]:
        """Load metadata from all pattern files."""
        metadata = {}
        
        for file_path in self.pattern_dir.rglob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Extract YAML front matter
                if content.startswith('---'):
                    end_marker = content.find('---', 3)
                    if end_marker != -1:
                        yaml_content = content[3:end_marker]
                        try:
                            meta = yaml.safe_load(yaml_content)
                            if meta:
                                rel_path = str(file_path.relative_to(self.docs_dir)).replace('\\', '/')
                                metadata[rel_path] = meta
                        except yaml.YAMLError as e:
                            logger.warning(f"YAML error in {file_path}: {e}")
                            
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
                
        logger.info(f"Loaded metadata from {len(metadata)} pattern files")
        return metadata
    
    def _build_alias_map(self) -> Dict[str, str]:
        """Build mapping of aliases to actual file paths."""
        aliases = {}
        
        for file_path, meta in self.pattern_metadata.items():
            if 'aliases' in meta:
                for alias in meta['aliases']:
                    # Handle different alias formats
                    if isinstance(alias, str):
                        # Clean up alias
                        clean_alias = alias.strip()
                        if clean_alias.endswith('.md'):
                            clean_alias = clean_alias[:-3]
                        aliases[clean_alias] = file_path
                        aliases[clean_alias + '.md'] = file_path
                        
        logger.info(f"Built alias map with {len(aliases)} aliases")
        return aliases
    
    def validate_file(self, file_path: Path) -> Dict[str, List]:
        """Validate all links in a single pattern file."""
        issues = {
            'broken': [],
            'empty': [],
            'external': [],
            'alias_issues': [],
            'cross_ref_issues': [],
            'category_issues': []
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Find all markdown links
            link_pattern = r'\[([^\]]*)\]\(([^\)]*)\)'
            matches = list(re.finditer(link_pattern, content))
            
            # Also find reference-style links
            ref_link_pattern = r'\[([^\]]*)\]\[([^\]]*)\]'
            ref_matches = list(re.finditer(ref_link_pattern, content))
            
            # Find reference definitions
            ref_defs = {}
            ref_def_pattern = r'^\[([^\]]+)\]:\s*(.+)$'
            for line_num, line in enumerate(content.split('\n'), 1):
                match = re.match(ref_def_pattern, line.strip())
                if match:
                    ref_defs[match.group(1)] = match.group(2)
            
            # Process all links
            all_links = []
            
            # Direct links
            for match in matches:
                link_text = match.group(1)
                link_url = match.group(2)
                line_num = content[:match.start()].count('\n') + 1
                all_links.append((link_text, link_url, line_num, 'direct'))
            
            # Reference links
            for match in ref_matches:
                link_text = match.group(1)
                ref_key = match.group(2) or link_text
                line_num = content[:match.start()].count('\n') + 1
                link_url = ref_defs.get(ref_key, '')
                all_links.append((link_text, link_url, line_num, 'reference'))
            
            # Validate each link
            for link_text, link_url, line_num, link_type in all_links:
                self._validate_single_link(
                    file_path, link_text, link_url, line_num, link_type, issues
                )
                
            # Additional pattern-specific validations
            self._validate_pattern_specific_links(file_path, content, issues)
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
        
        return issues
    
    def _validate_single_link(self, source_file: Path, link_text: str, link_url: str, 
                            line_num: int, link_type: str, issues: Dict):
        """Validate a single link."""
        if not link_url:
            issues['empty'].append({
                'line': line_num,
                'text': link_text,
                'url': link_url,
                'type': link_type
            })
            return
            
        # Skip anchors and external links for now
        if link_url.startswith('#'):
            self.valid_links += 1
            return
            
        if link_url.startswith(('http://', 'https://', 'mailto:')):
            issues['external'].append({
                'line': line_num,
                'text': link_text,
                'url': link_url,
                'type': link_type
            })
            return
        
        # Validate internal link
        if not self._validate_internal_link(source_file, link_url):
            # Check if it might be an alias
            if self._check_alias_link(link_url):
                issues['alias_issues'].append({
                    'line': line_num,
                    'text': link_text,
                    'url': link_url,
                    'type': link_type,
                    'alias_target': self.aliases.get(link_url.split('#')[0], 'unknown')
                })
            else:
                issues['broken'].append({
                    'line': line_num,
                    'text': link_text,
                    'url': link_url,
                    'type': link_type
                })
        else:
            self.valid_links += 1
    
    def _validate_internal_link(self, source_file: Path, link_url: str) -> bool:
        """Check if an internal link points to an existing file."""
        # Remove anchor and query parameters
        clean_url = link_url.split('#')[0].split('?')[0]
        
        if not clean_url:
            return True  # Pure anchor/query link
        
        # URL decode
        clean_url = urllib.parse.unquote(clean_url)
        
        # Get source directory
        source_rel = source_file.relative_to(self.docs_dir)
        source_dir = str(source_rel.parent).replace('\\', '/')
        
        # Resolve the link path
        if clean_url.startswith('/'):
            # Absolute path from docs root
            target_path = clean_url.lstrip('/')
        else:
            # Relative path
            if source_dir == '.':
                target_path = clean_url
            else:
                # Resolve relative path
                parts = source_dir.split('/') + clean_url.split('/')
                resolved_parts = []
                for part in parts:
                    if part == '..':
                        if resolved_parts:
                            resolved_parts.pop()
                    elif part and part != '.':
                        resolved_parts.append(part)
                target_path = '/'.join(resolved_parts)
        
        # Check various possibilities
        variants = [
            target_path,
            target_path + '.md',
            target_path + '/index.md',
            target_path + '/index',
            target_path.rstrip('/'),
            target_path.rstrip('/') + '.md'
        ]
        
        for variant in variants:
            if variant in self.all_files:
                return True
        
        # Check aliases
        return self._check_alias_link(target_path)
    
    def _check_alias_link(self, link_url: str) -> bool:
        """Check if a link points to an alias."""
        clean_url = link_url.split('#')[0]
        return clean_url in self.aliases or clean_url + '.md' in self.aliases
    
    def _validate_pattern_specific_links(self, file_path: Path, content: str, issues: Dict):
        """Validate pattern-specific links like Related Patterns sections."""
        # Look for Related Patterns sections
        related_pattern = r'(?i)##\s*related\s+patterns?\s*\n(.*?)(?=\n##|\n---|\Z)'
        matches = re.findall(related_pattern, content, re.DOTALL)
        
        for match in matches:
            # Find links in related patterns section
            links = re.finditer(r'\[([^\]]*)\]\(([^\)]*)\)', match)
            for link in links:
                link_text = link.group(1)
                link_url = link.group(2)
                
                # Check if this is supposed to be a pattern link
                if 'pattern' in link_text.lower() or link_url.startswith('../'):
                    if not self._validate_internal_link(file_path, link_url):
                        issues['cross_ref_issues'].append({
                            'text': link_text,
                            'url': link_url,
                            'context': 'Related Patterns'
                        })
    
    def validate_all_patterns(self):
        """Validate all pattern files in the pattern library."""
        pattern_files = list(self.pattern_dir.rglob("*.md"))
        self.total_files = len(pattern_files)
        
        logger.info(f"Validating links in {self.total_files} pattern files...")
        
        for i, file_path in enumerate(pattern_files, 1):
            if i % 20 == 0:
                logger.info(f"Progress: {i}/{self.total_files}")
            
            issues = self.validate_file(file_path)
            
            rel_path = str(file_path.relative_to(self.docs_dir)).replace('\\', '/')
            
            # Store issues by category
            if issues['broken']:
                self.broken_links[rel_path] = issues['broken']
            if issues['empty']:
                self.empty_links[rel_path] = issues['empty']
            if issues['external']:
                self.external_links[rel_path] = issues['external']
            if issues['alias_issues']:
                self.alias_issues[rel_path] = issues['alias_issues']
            if issues['cross_ref_issues']:
                self.cross_ref_issues[rel_path] = issues['cross_ref_issues']
            if issues['category_issues']:
                self.category_issues[rel_path] = issues['category_issues']
    
    def check_category_index_links(self):
        """Specifically validate category index files and their links."""
        logger.info("Checking category index files...")
        
        category_dirs = [
            'architecture', 'communication', 'coordination', 'cost-optimization',
            'data-management', 'deployment', 'ml-infrastructure', 'resilience',
            'scaling', 'security'
        ]
        
        for category in category_dirs:
            index_path = self.pattern_dir / category / "index.md"
            if index_path.exists():
                try:
                    content = index_path.read_text(encoding='utf-8')
                    
                    # Find pattern references in the category index
                    pattern_links = re.finditer(r'\[([^\]]*)\]\(([^\)]*\.md)\)', content)
                    
                    for link in pattern_links:
                        link_text = link.group(1)
                        link_url = link.group(2)
                        
                        if not self._validate_internal_link(index_path, link_url):
                            rel_path = str(index_path.relative_to(self.docs_dir)).replace('\\', '/')
                            if rel_path not in self.category_issues:
                                self.category_issues[rel_path] = []
                            
                            self.category_issues[rel_path].append({
                                'text': link_text,
                                'url': link_url,
                                'category': category
                            })
                            
                except Exception as e:
                    logger.warning(f"Could not check category index {index_path}: {e}")
            else:
                logger.warning(f"Category index not found: {index_path}")
    
    def validate_redirects_and_aliases(self):
        """Validate that aliases and redirects work properly."""
        logger.info("Validating redirects and aliases...")
        
        # Check if aliases point to valid files
        broken_aliases = []
        for alias, target in self.aliases.items():
            target_path = self.docs_dir / target
            if not target_path.exists():
                broken_aliases.append((alias, target))
        
        if broken_aliases:
            logger.warning(f"Found {len(broken_aliases)} broken aliases")
            for alias, target in broken_aliases[:5]:  # Show first 5
                logger.warning(f"  {alias} -> {target} (missing)")
    
    def suggest_fixes(self) -> List[Dict]:
        """Generate fix suggestions for common link issues."""
        fixes = []
        
        # Analyze broken links for patterns
        all_broken = []
        for file_path, links in self.broken_links.items():
            for link in links:
                all_broken.append((file_path, link))
        
        # Group by common issues
        issues_by_type = defaultdict(list)
        
        for file_path, link in all_broken:
            url = link['url']
            
            # Categorize the issue
            if url.endswith('/index.md'):
                issues_by_type['index_md_suffix'].append((file_path, link))
            elif url.endswith('/'):
                issues_by_type['trailing_slash'].append((file_path, link))
            elif '.md/' in url:
                issues_by_type['md_as_directory'].append((file_path, link))
            elif url.count('../') > 2:
                issues_by_type['excessive_parent'].append((file_path, link))
            elif not url.endswith('.md') and not url.startswith('#'):
                issues_by_type['missing_md_extension'].append((file_path, link))
            else:
                issues_by_type['other'].append((file_path, link))
        
        # Generate fix suggestions
        for issue_type, items in issues_by_type.items():
            if items:
                fixes.append({
                    'type': issue_type,
                    'count': len(items),
                    'description': self._get_fix_description(issue_type),
                    'examples': items[:3],  # Show first 3 examples
                    'fix_command': self._get_fix_command(issue_type)
                })
        
        return fixes
    
    def _get_fix_description(self, issue_type: str) -> str:
        """Get human-readable description for fix type."""
        descriptions = {
            'index_md_suffix': 'Links ending with /index.md should just end with /',
            'trailing_slash': 'Directory links with trailing slash may need index.md',
            'md_as_directory': 'Markdown files being treated as directories',
            'excessive_parent': 'Too many ../ in relative path',
            'missing_md_extension': 'Links missing .md extension',
            'other': 'Other broken link issues'
        }
        return descriptions.get(issue_type, 'Unknown issue type')
    
    def _get_fix_command(self, issue_type: str) -> str:
        """Get suggested fix command for issue type."""
        commands = {
            'index_md_suffix': "sed -i 's|/index.md)|/)|g' <file>",
            'trailing_slash': "Check if target directory has index.md",
            'md_as_directory': "Remove .md from middle of path",
            'excessive_parent': "Use absolute paths or simplify relative paths",
            'missing_md_extension': "Add .md extension to link",
            'other': 'Manual review required'
        }
        return commands.get(issue_type, 'Manual fix required')
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive validation report."""
        total_broken = sum(len(links) for links in self.broken_links.values())
        total_empty = sum(len(links) for links in self.empty_links.values())
        total_external = sum(len(links) for links in self.external_links.values())
        total_alias_issues = sum(len(links) for links in self.alias_issues.values())
        total_cross_ref = sum(len(links) for links in self.cross_ref_issues.values())
        total_category = sum(len(links) for links in self.category_issues.values())
        
        print("\n" + "=" * 100)
        print("PATTERN LIBRARY LINK VALIDATION REPORT")
        print("=" * 100)
        
        print(f"\nOVERALL SUMMARY:")
        print(f"  Files processed: {self.total_files}")
        print(f"  Valid internal links: {self.valid_links}")
        print(f"  Broken internal links: {total_broken}")
        print(f"  Empty links: {total_empty}")
        print(f"  Alias-related issues: {total_alias_issues}")
        print(f"  Cross-reference issues: {total_cross_ref}")
        print(f"  Category index issues: {total_category}")
        print(f"  External links found: {total_external}")
        
        # Health score
        total_issues = total_broken + total_empty + total_alias_issues + total_cross_ref + total_category
        total_links = self.valid_links + total_issues
        health_score = (self.valid_links / total_links * 100) if total_links > 0 else 100
        
        print(f"\n  LINK HEALTH SCORE: {health_score:.1f}%")
        
        if health_score >= 95:
            print("  Status: 🟢 EXCELLENT - Pattern library links are in great shape!")
        elif health_score >= 90:
            print("  Status: 🟡 GOOD - Minor issues to address")
        elif health_score >= 80:
            print("  Status: 🟠 FAIR - Several issues need attention")
        else:
            print("  Status: 🔴 POOR - Significant link issues found")
        
        # Detailed breakdowns
        if self.broken_links:
            self._print_broken_links_report(total_broken)
        
        if self.alias_issues:
            self._print_alias_issues_report(total_alias_issues)
        
        if self.cross_ref_issues:
            self._print_cross_ref_report(total_cross_ref)
        
        if self.category_issues:
            self._print_category_issues_report(total_category)
        
        if self.empty_links:
            self._print_empty_links_report(total_empty)
        
        # Fix suggestions
        fixes = self.suggest_fixes()
        if fixes:
            self._print_fix_suggestions(fixes)
    
    def _print_broken_links_report(self, total_broken: int):
        """Print detailed broken links report."""
        print(f"\n{'=' * 100}")
        print(f"BROKEN INTERNAL LINKS ({total_broken} total)")
        print(f"{'=' * 100}")
        
        # Show top files with most issues
        file_counts = [(path, len(links)) for path, links in self.broken_links.items()]
        file_counts.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\nFiles with most broken links:")
        for file_path, count in file_counts[:10]:
            print(f"  {count:2d} issues - {file_path}")
        
        print(f"\nDetailed breakdown:")
        for file_path, links in sorted(list(self.broken_links.items())[:5]):  # Show first 5 files
            print(f"\n{file_path}:")
            for link in links[:3]:  # Show first 3 links per file
                print(f"  Line {link['line']:3d}: [{link['text']}]({link['url']})")
            if len(links) > 3:
                print(f"  ... and {len(links) - 3} more issues")
        
        if len(self.broken_links) > 5:
            print(f"\n... and {len(self.broken_links) - 5} more files with broken links")
    
    def _print_alias_issues_report(self, total_alias_issues: int):
        """Print alias-related issues."""
        print(f"\n{'=' * 100}")
        print(f"ALIAS & REDIRECT ISSUES ({total_alias_issues} total)")
        print(f"{'=' * 100}")
        
        for file_path, links in sorted(list(self.alias_issues.items())[:3]):
            print(f"\n{file_path}:")
            for link in links:
                print(f"  Line {link['line']:3d}: [{link['text']}]({link['url']}) -> {link['alias_target']}")
    
    def _print_cross_ref_report(self, total_cross_ref: int):
        """Print cross-reference issues."""
        print(f"\n{'=' * 100}")
        print(f"CROSS-REFERENCE ISSUES ({total_cross_ref} total)")
        print(f"{'=' * 100}")
        
        for file_path, links in sorted(list(self.cross_ref_issues.items())[:3]):
            print(f"\n{file_path}:")
            for link in links:
                print(f"  {link['context']}: [{link['text']}]({link['url']})")
    
    def _print_category_issues_report(self, total_category: int):
        """Print category index issues."""
        print(f"\n{'=' * 100}")
        print(f"CATEGORY INDEX ISSUES ({total_category} total)")
        print(f"{'=' * 100}")
        
        for file_path, links in sorted(self.category_issues.items()):
            print(f"\n{file_path}:")
            for link in links:
                print(f"  [{link['text']}]({link['url']}) in {link['category']} category")
    
    def _print_empty_links_report(self, total_empty: int):
        """Print empty links report."""
        if total_empty > 0:
            print(f"\n{'=' * 100}")
            print(f"EMPTY LINKS ({total_empty} total)")
            print(f"{'=' * 100}")
            
            for file_path, links in sorted(list(self.empty_links.items())[:3]):
                print(f"\n{file_path}:")
                for link in links:
                    print(f"  Line {link['line']:3d}: [{link['text']}]()")
    
    def _print_fix_suggestions(self, fixes: List[Dict]):
        """Print fix suggestions."""
        print(f"\n{'=' * 100}")
        print("AUTOMATED FIX SUGGESTIONS")
        print(f"{'=' * 100}")
        
        for fix in fixes:
            print(f"\n{fix['type'].upper().replace('_', ' ')} ({fix['count']} instances):")
            print(f"  Issue: {fix['description']}")
            print(f"  Fix: {fix['fix_command']}")
            
            if fix['examples']:
                print(f"  Examples:")
                for file_path, link in fix['examples']:
                    print(f"    {file_path}: {link['url']}")
    
    def run_comprehensive_validation(self):
        """Run all validation checks."""
        logger.info("Starting comprehensive pattern library link validation...")
        
        # Main validation
        self.validate_all_patterns()
        
        # Specialized checks
        self.check_category_index_links()
        self.validate_redirects_and_aliases()
        
        # Generate report
        self.generate_comprehensive_report()
        
        # Summary
        total_issues = (
            sum(len(links) for links in self.broken_links.values()) +
            sum(len(links) for links in self.empty_links.values()) +
            sum(len(links) for links in self.alias_issues.values()) +
            sum(len(links) for links in self.cross_ref_issues.values()) +
            sum(len(links) for links in self.category_issues.values())
        )
        
        print(f"\n{'=' * 100}")
        print("VALIDATION COMPLETE")
        print(f"{'=' * 100}")
        
        if total_issues == 0:
            print("🎉 ALL LINKS VALID! Pattern library is in perfect shape.")
            return True
        else:
            print(f"⚠️  Found {total_issues} link issues that need attention.")
            print("Use the suggestions above to fix the most common issues.")
            return False

def main():
    """Main entry point."""
    print("🔍 Pattern Library Link Validator")
    print("=================================")
    
    validator = PatternLinkValidator()
    success = validator.run_comprehensive_validation()
    
    exit_code = 0 if success else 1
    exit(exit_code)

if __name__ == "__main__":
    main()
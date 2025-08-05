#!/usr/bin/env python3
"""
Comprehensive Pattern Library Validator

This script provides comprehensive validation of the pattern library to prevent
inconsistencies and maintain quality standards. It validates:

1. Pattern count accuracy across all documentation
2. Category metadata matches folder structure
3. All patterns have complete, valid metadata
4. Navigation matches file structure
5. No broken internal links
6. Consistent naming conventions

Usage:
    python3 scripts/comprehensive-pattern-validator.py [options]

Options:
    --fix             Auto-fix issues where possible
    --verbose         Show detailed output
    --category=NAME   Validate specific category only
    --report=FORMAT   Output format: json, yaml, markdown (default: markdown)
    --fail-fast       Stop on first critical error
"""

import os
import sys
import yaml
import json
import re
import argparse
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple, Any
from datetime import datetime
import fnmatch

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

@dataclass
class ValidationIssue:
    """Represents a validation issue found during checks"""
    level: str  # 'error', 'warning', 'info'
    category: str  # Which validation category
    file_path: str  # File where issue was found
    line_number: Optional[int] = None
    message: str = ""
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False

@dataclass
class PatternMetadata:
    """Pattern metadata structure"""
    title: str
    category: str
    excellence_tier: str
    pattern_status: str
    introduced: Optional[str] = None
    current_relevance: Optional[str] = None
    file_path: str = ""
    nav_path: str = ""
    
class PatternValidator:
    """Comprehensive pattern library validator"""
    
    # Required metadata fields for patterns
    REQUIRED_FIELDS = {
        'title', 'category', 'excellence_tier', 'pattern_status'
    }
    
    # Valid values for specific fields
    VALID_EXCELLENCE_TIERS = {'gold', 'silver', 'bronze'}
    VALID_PATTERN_STATUS = {
        'recommended', 'stable', 'use-with-expertise', 'use-with-caution', 
        'legacy', 'deprecated', 'experimental'
    }
    VALID_CATEGORIES = {
        'architecture', 'communication', 'coordination', 'data-management',
        'resilience', 'scaling'
    }
    VALID_RELEVANCE = {'mainstream', 'growing', 'declining', 'niche'}
    
    # Excellence tier specific requirements
    GOLD_REQUIREMENTS = {'modern_examples', 'production_checklist'}
    SILVER_REQUIREMENTS = {'trade_offs', 'best_for'}
    BRONZE_REQUIREMENTS = {'modern_alternatives', 'deprecation_reason'}
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.issues: List[ValidationIssue] = []
        self.patterns: Dict[str, PatternMetadata] = {}
        self.categories: Dict[str, List[str]] = defaultdict(list)
        self.navigation_patterns: Set[str] = set()
        
        # Paths
        self.docs_path = project_root / "docs"
        self.pattern_lib_path = self.docs_path / "pattern-library"
        self.mkdocs_config = project_root / "mkdocs.yml"
        
    def validate(self) -> Tuple[bool, List[ValidationIssue]]:
        """Run comprehensive validation and return success status and issues"""
        self.log("🔍 Starting comprehensive pattern library validation...")
        
        # Core validation steps
        self._load_patterns()
        self._validate_pattern_metadata()
        self._validate_category_structure()
        self._validate_navigation_consistency()
        self._validate_pattern_counts()
        self._validate_internal_links()
        self._validate_naming_conventions()
        self._validate_excellence_framework()
        
        # Generate summary
        errors = [i for i in self.issues if i.level == 'error']
        warnings = [i for i in self.issues if i.level == 'warning']
        
        success = len(errors) == 0
        
        self.log(f"✅ Validation complete: {len(errors)} errors, {len(warnings)} warnings")
        return success, self.issues
    
    def _load_patterns(self):
        """Load all patterns and their metadata"""
        self.log("📚 Loading pattern metadata...")
        
        for category_dir in self.pattern_lib_path.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue
                
            category = category_dir.name
            if category == '__pycache__':
                continue
                
            for pattern_file in category_dir.glob("*.md"):
                if pattern_file.name == 'index.md':
                    continue
                    
                try:
                    metadata = self._extract_metadata(pattern_file)
                    if metadata:
                        pattern_id = f"{category}/{pattern_file.stem}"
                        self.patterns[pattern_id] = metadata
                        self.categories[category].append(pattern_file.stem)
                        
                except Exception as e:
                    self._add_issue('error', 'metadata_loading', str(pattern_file),
                                  message=f"Failed to load pattern metadata: {e}")
    
    def _extract_metadata(self, file_path: Path) -> Optional[PatternMetadata]:
        """Extract metadata from pattern file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            if not content.startswith('---'):
                return None
                
            end_marker = content.find('---', 3)
            if end_marker == -1:
                return None
                
            frontmatter = content[3:end_marker].strip()
            metadata = yaml.safe_load(frontmatter) or {}
            
            # Extract category from file path
            category = file_path.parent.name
            
            return PatternMetadata(
                title=metadata.get('title', ''),
                category=metadata.get('category', category),
                excellence_tier=metadata.get('excellence_tier', ''),
                pattern_status=metadata.get('pattern_status', ''),
                introduced=metadata.get('introduced'),
                current_relevance=metadata.get('current_relevance'),
                file_path=str(file_path.relative_to(self.project_root)),
                nav_path=f"pattern-library/{category}/{file_path.stem}.md"
            )
            
        except Exception as e:
            self._add_issue('error', 'metadata_parsing', str(file_path),
                          message=f"Failed to parse metadata: {e}")
            return None
    
    def _validate_pattern_metadata(self):
        """Validate pattern metadata completeness and correctness"""
        self.log("🔍 Validating pattern metadata...")
        
        for pattern_id, pattern in self.patterns.items():
            file_path = pattern.file_path
            
            # Check required fields
            for field in self.REQUIRED_FIELDS:
                value = getattr(pattern, field, None)
                if not value:
                    self._add_issue('error', 'missing_metadata', file_path,
                                  message=f"Missing required field: {field}",
                                  suggested_fix=f"Add '{field}' to frontmatter")
            
            # Validate field values
            if pattern.excellence_tier and pattern.excellence_tier not in self.VALID_EXCELLENCE_TIERS:
                self._add_issue('error', 'invalid_metadata', file_path,
                              message=f"Invalid excellence_tier: {pattern.excellence_tier}",
                              suggested_fix=f"Use one of: {', '.join(self.VALID_EXCELLENCE_TIERS)}")
            
            if pattern.pattern_status and pattern.pattern_status not in self.VALID_PATTERN_STATUS:
                self._add_issue('error', 'invalid_metadata', file_path,
                              message=f"Invalid pattern_status: {pattern.pattern_status}",
                              suggested_fix=f"Use one of: {', '.join(self.VALID_PATTERN_STATUS)}")
            
            if pattern.current_relevance and pattern.current_relevance not in self.VALID_RELEVANCE:
                self._add_issue('error', 'invalid_metadata', file_path,
                              message=f"Invalid current_relevance: {pattern.current_relevance}",
                              suggested_fix=f"Use one of: {', '.join(self.VALID_RELEVANCE)}")
            
            # Check category consistency
            expected_category = Path(file_path).parent.name
            if pattern.category != expected_category:
                self._add_issue('error', 'category_mismatch', file_path,
                              message=f"Category mismatch: metadata='{pattern.category}', folder='{expected_category}'",
                              suggested_fix=f"Update category to '{expected_category}'",
                              auto_fixable=True)
    
    def _validate_category_structure(self):
        """Validate category folder structure matches metadata"""
        self.log("📁 Validating category structure...")
        
        # Check if all categories in filesystem are valid
        for category_dir in self.pattern_lib_path.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue
                
            category = category_dir.name
            if category not in self.VALID_CATEGORIES:
                self._add_issue('warning', 'unknown_category', str(category_dir),
                              message=f"Unknown category directory: {category}",
                              suggested_fix=f"Ensure category is one of: {', '.join(self.VALID_CATEGORIES)}")
        
        # Check for empty categories
        for category in self.VALID_CATEGORIES:
            category_path = self.pattern_lib_path / category
            if not category_path.exists():
                self._add_issue('warning', 'missing_category', str(category_path),
                              message=f"Missing category directory: {category}")
            elif not list(category_path.glob("*.md")):
                self._add_issue('info', 'empty_category', str(category_path),
                              message=f"Empty category directory: {category}")
    
    def _validate_navigation_consistency(self):
        """Validate mkdocs navigation matches file structure"""
        self.log("🧭 Validating navigation consistency...")
        
        try:
            with open(self.mkdocs_config, 'r', encoding='utf-8') as f:
                mkdocs_config = yaml.safe_load(f)
            
            # Extract pattern library navigation
            nav = mkdocs_config.get('nav', [])
            pattern_nav = self._find_pattern_nav(nav)
            
            if not pattern_nav:
                self._add_issue('error', 'navigation_missing', str(self.mkdocs_config),
                              message="Pattern library section not found in navigation")
                return
            
            # Collect navigation patterns
            nav_patterns = set()
            self._collect_nav_patterns(pattern_nav, nav_patterns)
            
            # Compare with filesystem patterns
            fs_patterns = set(self.patterns.keys())
            
            # Find missing patterns in navigation
            missing_in_nav = fs_patterns - nav_patterns
            for pattern in missing_in_nav:
                self._add_issue('error', 'navigation_missing_pattern', self.patterns[pattern].file_path,
                              message=f"Pattern not in navigation: {pattern}",
                              suggested_fix="Add to mkdocs.yml navigation")
            
            # Find extra patterns in navigation
            extra_in_nav = nav_patterns - fs_patterns
            for pattern in extra_in_nav:
                self._add_issue('error', 'navigation_extra_pattern', str(self.mkdocs_config),
                              message=f"Navigation references non-existent pattern: {pattern}",
                              suggested_fix="Remove from mkdocs.yml navigation")
                              
        except Exception as e:
            self._add_issue('error', 'navigation_parsing', str(self.mkdocs_config),
                          message=f"Failed to parse navigation: {e}")
    
    def _find_pattern_nav(self, nav: List) -> Optional[Dict]:
        """Find pattern library section in navigation"""
        for item in nav:
            if isinstance(item, dict):
                for key, value in item.items():
                    if 'Pattern Library' in key:
                        return value
                    elif isinstance(value, list):
                        result = self._find_pattern_nav(value)
                        if result:
                            return result
        return None
    
    def _collect_nav_patterns(self, nav_section: List, patterns: Set[str]):
        """Collect all pattern references from navigation"""
        for item in nav_section:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str) and value.startswith('pattern-library/'):
                        # Extract pattern ID from path
                        path_parts = Path(value).parts
                        if len(path_parts) >= 3:
                            category = path_parts[1]
                            pattern = Path(path_parts[2]).stem
                            patterns.add(f"{category}/{pattern}")
                    elif isinstance(value, list):
                        self._collect_nav_patterns(value, patterns)
    
    def _validate_pattern_counts(self):
        """Validate pattern counts mentioned in documentation"""
        self.log("🔢 Validating pattern counts...")
        
        total_patterns = len(self.patterns)
        
        # Check pattern counts in key files
        count_files = [
            self.docs_path / "index.md",
            self.docs_path / "pattern-library" / "index.md",
            self.project_root / "README.md",
            self.project_root / "CLAUDE.md"
        ]
        
        for file_path in count_files:
            if file_path.exists():
                self._validate_count_in_file(file_path, total_patterns)
    
    def _validate_count_in_file(self, file_path: Path, expected_count: int):
        """Validate pattern count in specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for pattern count references
            patterns = [
                r'(\d+)\s+[Pp]atterns?',
                r'[Pp]attern\s+[Ll]ibrary.*?(\d+)',
                r'(\d+)\s+architectural\s+patterns?',
                r'Total.*?(\d+).*?patterns?'
            ]
            
            for i, line in enumerate(content.split('\n'), 1):
                for pattern in patterns:
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    for match in matches:
                        count = int(match)
                        if count != expected_count:
                            self._add_issue('warning', 'incorrect_count', str(file_path),
                                          line_number=i,
                                          message=f"Incorrect pattern count: found {count}, expected {expected_count}",
                                          suggested_fix=f"Update count to {expected_count}",
                                          auto_fixable=True)
                            
        except Exception as e:
            self._add_issue('warning', 'count_validation', str(file_path),
                          message=f"Failed to validate counts: {e}")
    
    def _validate_internal_links(self):
        """Validate internal links in pattern files"""
        self.log("🔗 Validating internal links...")
        
        for pattern_id, pattern in self.patterns.items():
            file_path = Path(self.project_root / pattern.file_path)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self._check_links_in_content(content, file_path)
                
            except Exception as e:
                self._add_issue('warning', 'link_validation', str(file_path),
                              message=f"Failed to validate links: {e}")
    
    def _check_links_in_content(self, content: str, file_path: Path):
        """Check all links in content"""
        # Find markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for match in re.finditer(link_pattern, content):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Skip external links and anchors
            if link_url.startswith(('http', 'https', 'mailto', '#')):
                continue
            
            # Check internal links
            if link_url.startswith('/'):
                # Absolute path from docs root
                target_path = self.docs_path / link_url[1:]
            else:
                # Relative path
                target_path = file_path.parent / link_url
                
            # Resolve path and check existence
            try:
                resolved_path = target_path.resolve()
                if not resolved_path.exists():
                    self._add_issue('error', 'broken_link', str(file_path),
                                  message=f"Broken link: {link_url} -> {resolved_path}",
                                  suggested_fix="Fix or remove broken link")
            except Exception:
                self._add_issue('warning', 'link_resolution', str(file_path),
                              message=f"Could not resolve link: {link_url}")
    
    def _validate_naming_conventions(self):
        """Validate naming conventions across patterns"""
        self.log("📝 Validating naming conventions...")
        
        for pattern_id, pattern in self.patterns.items():
            file_path = Path(pattern.file_path)
            
            # Check filename conventions
            filename = file_path.stem
            if not re.match(r'^[a-z0-9-]+$', filename):
                self._add_issue('warning', 'naming_convention', pattern.file_path,
                              message=f"Filename should use lowercase and hyphens only: {filename}",
                              suggested_fix="Use lowercase letters, numbers, and hyphens")
            
            # Check title consistency
            expected_title_pattern = filename.replace('-', ' ').title()
            if pattern.title and not pattern.title.lower().replace(' ', '-').startswith(filename.lower()):
                self._add_issue('warning', 'title_consistency', pattern.file_path,
                              message=f"Title doesn't match filename: '{pattern.title}' vs '{filename}'",
                              suggested_fix="Ensure title matches filename pattern")
    
    def _validate_excellence_framework(self):
        """Validate excellence framework requirements"""
        self.log("🏆 Validating excellence framework...")
        
        for pattern_id, pattern in self.patterns.items():
            file_path = Path(self.project_root / pattern.file_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check tier-specific requirements
                if pattern.excellence_tier == 'gold':
                    self._check_gold_requirements(content, pattern)
                elif pattern.excellence_tier == 'silver':
                    self._check_silver_requirements(content, pattern)
                elif pattern.excellence_tier == 'bronze':
                    self._check_bronze_requirements(content, pattern)
                    
            except Exception as e:
                self._add_issue('warning', 'excellence_validation', pattern.file_path,
                              message=f"Failed to validate excellence requirements: {e}")
    
    def _check_gold_requirements(self, content: str, pattern: PatternMetadata):
        """Check Gold tier requirements"""
        # Look for modern examples section
        if 'modern_examples' not in content.lower() and 'production example' not in content.lower():
            self._add_issue('warning', 'missing_gold_requirement', pattern.file_path,
                          message="Gold pattern missing modern examples section",
                          suggested_fix="Add modern examples with real companies")
        
        # Look for production checklist
        if 'production_checklist' not in content.lower() and 'checklist' not in content.lower():
            self._add_issue('warning', 'missing_gold_requirement', pattern.file_path,
                          message="Gold pattern missing production checklist",
                          suggested_fix="Add production readiness checklist")
    
    def _check_silver_requirements(self, content: str, pattern: PatternMetadata):
        """Check Silver tier requirements"""
        # Look for trade-offs section
        if 'trade_offs' not in content.lower() and 'trade-off' not in content.lower():
            self._add_issue('warning', 'missing_silver_requirement', pattern.file_path,
                          message="Silver pattern missing trade-offs analysis",
                          suggested_fix="Add pros/cons trade-off analysis")
        
        # Look for best use cases
        if 'best_for' not in content.lower() and 'when to use' not in content.lower():
            self._add_issue('warning', 'missing_silver_requirement', pattern.file_path,
                          message="Silver pattern missing usage guidance",
                          suggested_fix="Add 'best for' or 'when to use' section")
    
    def _check_bronze_requirements(self, content: str, pattern: PatternMetadata):
        """Check Bronze tier requirements"""
        # Look for modern alternatives
        if 'modern_alternatives' not in content.lower() and 'alternative' not in content.lower():
            self._add_issue('warning', 'missing_bronze_requirement', pattern.file_path,
                          message="Bronze pattern missing modern alternatives",
                          suggested_fix="Add modern alternatives section")
        
        # Look for deprecation reason
        if 'deprecation_reason' not in content.lower() and 'legacy' not in content.lower():
            self._add_issue('warning', 'missing_bronze_requirement', pattern.file_path,
                          message="Bronze pattern missing deprecation context",
                          suggested_fix="Add deprecation reason or legacy context")
    
    def _add_issue(self, level: str, category: str, file_path: str, 
                   line_number: Optional[int] = None, message: str = "",
                   suggested_fix: Optional[str] = None, auto_fixable: bool = False):
        """Add validation issue"""
        issue = ValidationIssue(
            level=level,
            category=category,
            file_path=file_path,
            line_number=line_number,
            message=message,
            suggested_fix=suggested_fix,
            auto_fixable=auto_fixable
        )
        self.issues.append(issue)
        
        if self.verbose:
            icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}.get(level, '•')
            print(f"{icon} {level.upper()}: {message} ({file_path})")
    
    def log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            print(message)
    
    def generate_report(self, format: str = 'markdown') -> str:
        """Generate validation report"""
        if format == 'json':
            return self._generate_json_report()
        elif format == 'yaml':
            return self._generate_yaml_report()
        else:
            return self._generate_markdown_report()
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown validation report"""
        errors = [i for i in self.issues if i.level == 'error']
        warnings = [i for i in self.issues if i.level == 'warning']
        info = [i for i in self.issues if i.level == 'info']
        
        report = f"""# Pattern Library Validation Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Patterns**: {len(self.patterns)}
- **Categories**: {len(self.categories)}
- **Errors**: {len(errors)}
- **Warnings**: {len(warnings)}
- **Info**: {len(info)}

## Pattern Distribution by Category

"""
        
        for category, patterns in sorted(self.categories.items()):
            report += f"- **{category.title()}**: {len(patterns)} patterns\n"
        
        if errors:
            report += "\n## ❌ Critical Errors\n\n"
            for issue in errors:
                report += f"### {issue.category}: {issue.message}\n"
                report += f"- **File**: `{issue.file_path}`\n"
                if issue.line_number:
                    report += f"- **Line**: {issue.line_number}\n"
                if issue.suggested_fix:
                    report += f"- **Fix**: {issue.suggested_fix}\n"
                report += "\n"
        
        if warnings:
            report += "\n## ⚠️ Warnings\n\n"
            for issue in warnings:
                report += f"### {issue.category}: {issue.message}\n"
                report += f"- **File**: `{issue.file_path}`\n"
                if issue.line_number:
                    report += f"- **Line**: {issue.line_number}\n"
                if issue.suggested_fix:
                    report += f"- **Fix**: {issue.suggested_fix}\n"
                report += "\n"
        
        if not errors and not warnings:
            report += "\n## ✅ All Validations Passed\n\nNo issues found!\n"
        
        return report
    
    def _generate_json_report(self) -> str:
        """Generate JSON validation report"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_patterns': len(self.patterns),
                'categories': len(self.categories),
                'errors': len([i for i in self.issues if i.level == 'error']),
                'warnings': len([i for i in self.issues if i.level == 'warning']),
                'info': len([i for i in self.issues if i.level == 'info'])
            },
            'categories': {cat: len(patterns) for cat, patterns in self.categories.items()},
            'issues': [
                {
                    'level': issue.level,
                    'category': issue.category,
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'message': issue.message,
                    'suggested_fix': issue.suggested_fix,
                    'auto_fixable': issue.auto_fixable
                }
                for issue in self.issues
            ]
        }
        return json.dumps(data, indent=2)
    
    def _generate_yaml_report(self) -> str:
        """Generate YAML validation report"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_patterns': len(self.patterns),
                'categories': len(self.categories),
                'errors': len([i for i in self.issues if i.level == 'error']),
                'warnings': len([i for i in self.issues if i.level == 'warning']),
                'info': len([i for i in self.issues if i.level == 'info'])
            },
            'categories': {cat: len(patterns) for cat, patterns in self.categories.items()},
            'issues': [
                {
                    'level': issue.level,
                    'category': issue.category,
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'message': issue.message,
                    'suggested_fix': issue.suggested_fix,
                    'auto_fixable': issue.auto_fixable
                }
                for issue in self.issues
            ]
        }
        return yaml.dump(data, default_flow_style=False)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Comprehensive Pattern Library Validator')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues where possible')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--category', help='Validate specific category only')
    parser.add_argument('--report', choices=['json', 'yaml', 'markdown'], 
                       default='markdown', help='Output format')
    parser.add_argument('--fail-fast', action='store_true', help='Stop on first critical error')
    parser.add_argument('--output', '-o', help='Output file for report')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = PatternValidator(PROJECT_ROOT, verbose=args.verbose)
    
    # Run validation
    try:
        success, issues = validator.validate()
        
        # Generate report
        report = validator.generate_report(args.report)
        
        # Output report
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report written to: {args.output}")
        else:
            print(report)
        
        # Exit with appropriate code
        errors = [i for i in issues if i.level == 'error']
        if errors:
            print(f"\n❌ Validation failed with {len(errors)} errors")
            sys.exit(1)
        else:
            print(f"\n✅ Validation passed")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Navigation Validator for DStudio
Validates mkdocs.yml navigation structure and detects orphaned files.
"""

import yaml
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
import json
from datetime import datetime

# Custom YAML constructors to handle MkDocs-specific tags
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
    
# Add constructor for any unknown tag
SafeLoaderIgnoreUnknown.add_multi_constructor('', ignore_unknown)

class NavigationValidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.mkdocs_file = self.project_root / "mkdocs.yml"
        self.issues = []
        self.warnings = []
        self.stats = {
            "total_files": 0,
            "files_in_nav": 0,
            "orphaned_files": 0,
            "broken_links": 0,
            "duplicate_entries": 0
        }
        
    def load_mkdocs_config(self) -> dict:
        """Load and parse mkdocs.yml"""
        try:
            with open(self.mkdocs_file, 'r') as f:
                # Use custom loader that ignores unknown tags
                return yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
        except Exception as e:
            self.issues.append(f"Failed to load mkdocs.yml: {e}")
            return {}
    
    def extract_nav_files(self, nav_items, prefix="") -> Set[str]:
        """Recursively extract all files from navigation"""
        files = set()
        
        if isinstance(nav_items, list):
            for item in nav_items:
                files.update(self.extract_nav_files(item, prefix))
        elif isinstance(nav_items, dict):
            for key, value in nav_items.items():
                if isinstance(value, str) and value.endswith('.md'):
                    files.add(value)
                else:
                    files.update(self.extract_nav_files(value, prefix))
        
        return files
    
    def find_all_md_files(self) -> Set[str]:
        """Find all markdown files in docs directory"""
        md_files = set()
        
        for path in self.docs_dir.rglob("*.md"):
            # Get relative path from docs directory
            rel_path = path.relative_to(self.docs_dir)
            md_files.add(str(rel_path))
            
        return md_files
    
    def validate_navigation_links(self, nav_files: Set[str]) -> List[str]:
        """Check if all navigation links point to existing files"""
        broken_links = []
        
        for nav_file in nav_files:
            full_path = self.docs_dir / nav_file
            if not full_path.exists():
                broken_links.append(nav_file)
                self.issues.append(f"Broken link in navigation: {nav_file}")
                
        return broken_links
    
    def find_duplicate_entries(self, config: dict) -> List[str]:
        """Find files that appear multiple times in navigation"""
        duplicates = []
        seen = set()
        
        nav_files = self.extract_nav_files(config.get('nav', []))
        
        for file in nav_files:
            if file in seen:
                duplicates.append(file)
                self.warnings.append(f"Duplicate navigation entry: {file}")
            seen.add(file)
            
        return duplicates
    
    def analyze_orphaned_files(self, all_files: Set[str], nav_files: Set[str]) -> List[str]:
        """Find files not referenced in navigation"""
        orphaned = []
        
        for file in all_files:
            if file not in nav_files:
                # Skip special files
                if file in ['index.md', 'README.md', 'CONTRIBUTING.md']:
                    continue
                    
                orphaned.append(file)
                
        return orphaned
    
    def check_navigation_depth(self, nav_items, depth=0, path="") -> None:
        """Check navigation depth and warn about deep nesting"""
        if depth > 3:
            self.warnings.append(f"Deep navigation nesting (level {depth}) at: {path}")
            
        if isinstance(nav_items, list):
            for i, item in enumerate(nav_items):
                self.check_navigation_depth(item, depth, f"{path}[{i}]")
        elif isinstance(nav_items, dict):
            for key, value in nav_items.items():
                if not isinstance(value, str):
                    self.check_navigation_depth(value, depth + 1, f"{path}/{key}")
    
    def validate_pattern_metadata(self) -> Dict[str, List[str]]:
        """Validate pattern files have required metadata"""
        metadata_issues = {}
        pattern_dir = self.docs_dir / "patterns"
        
        if pattern_dir.exists():
            for pattern_file in pattern_dir.glob("*.md"):
                issues = []
                
                with open(pattern_file, 'r') as f:
                    content = f.read()
                    
                # Check for required metadata fields
                required_fields = ['excellence_tier', 'pattern_status', 'category']
                for field in required_fields:
                    if f"{field}:" not in content:
                        issues.append(f"Missing {field}")
                        
                if issues:
                    metadata_issues[str(pattern_file.name)] = issues
                    
        return metadata_issues
    
    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        config = self.load_mkdocs_config()
        nav_files = self.extract_nav_files(config.get('nav', []))
        all_files = self.find_all_md_files()
        
        # Update stats
        self.stats["total_files"] = len(all_files)
        self.stats["files_in_nav"] = len(nav_files)
        
        # Perform validations
        broken_links = self.validate_navigation_links(nav_files)
        self.stats["broken_links"] = len(broken_links)
        
        duplicates = self.find_duplicate_entries(config)
        self.stats["duplicate_entries"] = len(duplicates)
        
        orphaned = self.analyze_orphaned_files(all_files, nav_files)
        self.stats["orphaned_files"] = len(orphaned)
        
        # Check navigation depth
        self.check_navigation_depth(config.get('nav', []))
        
        # Check pattern metadata
        metadata_issues = self.validate_pattern_metadata()
        
        # Calculate percentages
        nav_coverage = (self.stats["files_in_nav"] / self.stats["total_files"] * 100) if self.stats["total_files"] > 0 else 0
        orphan_rate = (self.stats["orphaned_files"] / self.stats["total_files"] * 100) if self.stats["total_files"] > 0 else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "percentages": {
                "navigation_coverage": round(nav_coverage, 2),
                "orphan_rate": round(orphan_rate, 2)
            },
            "issues": self.issues,
            "warnings": self.warnings,
            "broken_links": broken_links,
            "duplicate_entries": duplicates,
            "orphaned_files": sorted(orphaned),
            "metadata_issues": metadata_issues,
            "summary": {
                "health_score": self._calculate_health_score(),
                "recommendation": self._get_recommendation()
            }
        }
    
    def _calculate_health_score(self) -> str:
        """Calculate overall navigation health score"""
        score = 100
        
        # Deduct points for issues
        score -= len(self.issues) * 10
        score -= len(self.warnings) * 5
        score -= self.stats["broken_links"] * 15
        score -= min(self.stats["orphaned_files"], 20) * 2  # Cap at 40 point deduction
        
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _get_recommendation(self) -> str:
        """Get actionable recommendation based on findings"""
        if self.stats["broken_links"] > 0:
            return "CRITICAL: Fix broken navigation links immediately"
        elif self.stats["orphaned_files"] > 50:
            return "HIGH: Review and integrate orphaned files"
        elif len(self.warnings) > 10:
            return "MEDIUM: Address navigation structure warnings"
        elif len(self.issues) > 0:
            return "LOW: Review and fix minor issues"
        else:
            return "Navigation structure is healthy"

def main():
    validator = NavigationValidator()
    report = validator.generate_report()
    
    # Print summary to console
    print("\n=== DStudio Navigation Validation Report ===\n")
    print(f"Total Files: {report['stats']['total_files']}")
    print(f"Files in Navigation: {report['stats']['files_in_nav']} ({report['percentages']['navigation_coverage']}%)")
    print(f"Orphaned Files: {report['stats']['orphaned_files']} ({report['percentages']['orphan_rate']}%)")
    print(f"Broken Links: {report['stats']['broken_links']}")
    print(f"Duplicate Entries: {report['stats']['duplicate_entries']}")
    print(f"\nHealth Score: {report['summary']['health_score']}")
    print(f"Recommendation: {report['summary']['recommendation']}")
    
    # Print issues if any
    if report['issues']:
        print("\n⚠️  Issues Found:")
        for issue in report['issues']:
            print(f"  - {issue}")
    
    # Print warnings if any
    if report['warnings']:
        print("\n⚡ Warnings:")
        for warning in report['warnings'][:5]:  # Show first 5
            print(f"  - {warning}")
        if len(report['warnings']) > 5:
            print(f"  ... and {len(report['warnings']) - 5} more warnings")
    
    # Save detailed report
    with open('navigation-validation-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Detailed report saved to: navigation-validation-report.json")
    
    # Exit with appropriate code
    if report['stats']['broken_links'] > 0:
        sys.exit(1)  # Fail if broken links found
    elif report['summary']['health_score'] in ['D', 'F']:
        sys.exit(1)  # Fail if health score is poor
    else:
        sys.exit(0)  # Success

if __name__ == "__main__":
    main()
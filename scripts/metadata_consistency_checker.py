#!/usr/bin/env python3
"""
Comprehensive metadata consistency checker for pattern files.
Validates excellence framework metadata against CLAUDE.md requirements.
"""

import os
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Any

# Expected metadata according to CLAUDE.md
VALID_EXCELLENCE_TIERS = {'gold', 'silver', 'bronze'}
VALID_PATTERN_STATUS = {'recommended', 'use-with-expertise', 'use-with-caution', 'legacy'}
VALID_CURRENT_RELEVANCE = {'mainstream', 'growing', 'declining', 'niche'}

# Required sections per tier
GOLD_REQUIRED_SECTIONS = {'modern_examples', 'production_checklist'}
SILVER_REQUIRED_SECTIONS = {'trade_offs', 'best_for'}
BRONZE_REQUIRED_SECTIONS = {'modern_alternatives', 'deprecation_reason'}

class PatternMetadataChecker:
    def __init__(self, patterns_dir: Path):
        self.patterns_dir = patterns_dir
        self.issues = []
        self.patterns_checked = 0
        self.valid_patterns = 0
        
    def log_issue(self, file_path: str, issue_type: str, description: str):
        """Log a metadata consistency issue."""
        self.issues.append({
            'file': file_path,
            'type': issue_type,
            'description': description
        })
    
    def extract_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter from markdown content."""
        try:
            if content.startswith('---\n'):
                end_pos = content.find('\n---\n', 4)
                if end_pos != -1:
                    frontmatter_yaml = content[4:end_pos]
                    return yaml.safe_load(frontmatter_yaml)
        except yaml.YAMLError as e:
            return None
        return None
    
    def validate_required_frontmatter(self, file_path: str, metadata: Dict[str, Any]):
        """Validate required excellence framework frontmatter fields."""
        required_fields = {
            'excellence_tier': VALID_EXCELLENCE_TIERS,
            'pattern_status': VALID_PATTERN_STATUS,
            'introduced': None,  # Will validate format separately
            'current_relevance': VALID_CURRENT_RELEVANCE
        }
        
        for field, valid_values in required_fields.items():
            if field not in metadata:
                self.log_issue(file_path, 'MISSING_FIELD', f"Missing required field: {field}")
                continue
                
            if valid_values and metadata[field] not in valid_values:
                self.log_issue(file_path, 'INVALID_VALUE', 
                             f"{field} has invalid value '{metadata[field]}'. Valid values: {valid_values}")
        
        # Validate date format for 'introduced' field
        if 'introduced' in metadata:
            introduced = str(metadata['introduced'])
            if not re.match(r'^\d{4}-\d{2}$', introduced):
                self.log_issue(file_path, 'INVALID_DATE_FORMAT', 
                             f"'introduced' field must be in YYYY-MM format, got: {introduced}")
    
    def validate_tier_specific_sections(self, file_path: str, metadata: Dict[str, Any], content: str):
        """Validate tier-specific required sections."""
        tier = metadata.get('excellence_tier')
        if not tier:
            return
            
        required_sections = set()
        if tier == 'gold':
            required_sections = GOLD_REQUIRED_SECTIONS
        elif tier == 'silver':
            required_sections = SILVER_REQUIRED_SECTIONS
        elif tier == 'bronze':
            required_sections = BRONZE_REQUIRED_SECTIONS
        
        # Check frontmatter sections
        for section in required_sections:
            if section not in metadata:
                self.log_issue(file_path, 'MISSING_TIER_SECTION', 
                             f"{tier.title()} tier pattern missing required section: {section}")
        
        # For Gold patterns, validate structure of modern_examples and production_checklist
        if tier == 'gold':
            if 'modern_examples' in metadata:
                examples = metadata['modern_examples']
                if not isinstance(examples, list) or len(examples) == 0:
                    self.log_issue(file_path, 'INVALID_STRUCTURE', 
                                 "modern_examples should be a non-empty list")
                else:
                    for i, example in enumerate(examples):
                        if not isinstance(example, dict):
                            self.log_issue(file_path, 'INVALID_STRUCTURE', 
                                         f"modern_examples[{i}] should be a dictionary")
                            continue
                        required_keys = {'company', 'implementation', 'scale'}
                        missing_keys = required_keys - set(example.keys())
                        if missing_keys:
                            self.log_issue(file_path, 'MISSING_EXAMPLE_FIELDS', 
                                         f"modern_examples[{i}] missing keys: {missing_keys}")
            
            if 'production_checklist' in metadata:
                checklist = metadata['production_checklist']
                if not isinstance(checklist, list) or len(checklist) == 0:
                    self.log_issue(file_path, 'INVALID_STRUCTURE', 
                                 "production_checklist should be a non-empty list")
        
        # For Silver patterns, validate trade_offs structure
        if tier == 'silver' and 'trade_offs' in metadata:
            trade_offs = metadata['trade_offs']
            if not isinstance(trade_offs, dict):
                self.log_issue(file_path, 'INVALID_STRUCTURE', 
                             "trade_offs should be a dictionary")
            else:
                required_keys = {'pros', 'cons'}
                missing_keys = required_keys - set(trade_offs.keys())
                if missing_keys:
                    self.log_issue(file_path, 'MISSING_TRADEOFF_FIELDS', 
                                 f"trade_offs missing keys: {missing_keys}")
                for key in ['pros', 'cons']:
                    if key in trade_offs and not isinstance(trade_offs[key], list):
                        self.log_issue(file_path, 'INVALID_STRUCTURE', 
                                     f"trade_offs.{key} should be a list")
    
    def check_pattern_file(self, file_path: Path):
        """Check a single pattern file for metadata consistency."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip non-pattern files
            if file_path.name in ['README.md', 'index.md', 'index-new.md', 'pattern-catalog.md', 
                                 'pattern-selector-tool.md', 'pattern-relationships.md', 
                                 'PATTERN_TEMPLATE.md']:
                return
            
            # Skip deleted files mentioned in git status
            deleted_files = [
                'EXCELLENCE_TRANSFORMATION_PROGRESS.md',
                'GOLD_PATTERNS_COMPLETE.md',
                'INDEX_UPDATE_SUMMARY.md',
                'METADATA_ENHANCEMENT_REPORT.md',
                'METADATA_ENHANCEMENT_REPORT_PHASE2.md',
                'NAVIGATION_FILTERING_COMPLETE.md',
                'NAVIGATION_INTEGRATION_COMPLETE.md',
                'PATTERN_CLASSIFICATION_RESULTS.md',
                'PATTERN_CLASSIFICATION_SUMMARY.md',
                'PATTERN_ORGANIZATION.md',
                'PATTERN_RESTORATION_COMPLETE.md'
            ]
            if file_path.name in deleted_files:
                return
            
            self.patterns_checked += 1
            
            # Extract and validate frontmatter
            metadata = self.extract_frontmatter(content)
            if not metadata:
                self.log_issue(str(file_path), 'NO_FRONTMATTER', "No valid YAML frontmatter found")
                return
            
            # Validate required excellence framework fields
            self.validate_required_frontmatter(str(file_path), metadata)
            
            # Validate tier-specific sections
            self.validate_tier_specific_sections(str(file_path), metadata, content)
            
            # Check if pattern has all required metadata
            has_required_fields = all(field in metadata for field in 
                                    ['excellence_tier', 'pattern_status', 'introduced', 'current_relevance'])
            if has_required_fields:
                self.valid_patterns += 1
                
        except Exception as e:
            self.log_issue(str(file_path), 'FILE_ERROR', f"Error reading file: {str(e)}")
    
    def check_all_patterns(self):
        """Check all pattern files in the patterns directory."""
        pattern_files = list(self.patterns_dir.glob('*.md'))
        
        for file_path in sorted(pattern_files):
            self.check_pattern_file(file_path)
    
    def generate_report(self) -> str:
        """Generate a comprehensive metadata consistency report."""
        report = []
        report.append("# Pattern Metadata Consistency Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        report.append("## Summary")
        report.append(f"- **Total patterns checked**: {self.patterns_checked}")
        report.append(f"- **Patterns with complete metadata**: {self.valid_patterns}")
        report.append(f"- **Patterns with issues**: {self.patterns_checked - self.valid_patterns}")
        report.append(f"- **Total issues found**: {len(self.issues)}")
        report.append("")
        
        # Issue breakdown by type
        issue_types = {}
        for issue in self.issues:
            issue_type = issue['type']
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        report.append("## Issues by Type")
        for issue_type, count in sorted(issue_types.items()):
            report.append(f"- **{issue_type}**: {count}")
        report.append("")
        
        # Detailed issues
        if self.issues:
            report.append("## Detailed Issues")
            
            # Group issues by file
            issues_by_file = {}
            for issue in self.issues:
                file_path = issue['file']
                if file_path not in issues_by_file:
                    issues_by_file[file_path] = []
                issues_by_file[file_path].append(issue)
            
            for file_path, file_issues in sorted(issues_by_file.items()):
                report.append(f"### {os.path.basename(file_path)}")
                for issue in file_issues:
                    report.append(f"- **{issue['type']}**: {issue['description']}")
                report.append("")
        else:
            report.append("## ✅ No Issues Found!")
            report.append("All patterns have consistent metadata according to the excellence framework requirements.")
        
        return "\n".join(report)

def main():
    """Main function to run the metadata consistency check."""
    patterns_dir = Path("docs/patterns")
    
    if not patterns_dir.exists():
        print(f"Error: Patterns directory not found: {patterns_dir}")
        return
    
    checker = PatternMetadataChecker(patterns_dir)
    checker.check_all_patterns()
    
    report = checker.generate_report()
    print(report)
    
    # Also save to file
    with open("pattern_metadata_consistency_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\nReport saved to: pattern_metadata_consistency_report.md")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Pattern Validator Script

Validates that all patterns have required excellence metadata:
- Tier classifications (gold/silver/bronze)
- Bronze patterns have alternatives listed
- Gold patterns have real-world examples
- All required front matter fields
"""

import os
import re
import yaml
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationIssue:
    """Represents a validation issue found in a pattern"""
    pattern_name: str
    issue_type: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    line_number: Optional[int] = None

@dataclass
class PatternValidation:
    """Validation results for a pattern"""
    pattern_name: str
    file_path: Path
    is_valid: bool
    issues: List[ValidationIssue]
    front_matter: Dict

class PatternValidator:
    """Validates pattern files for excellence metadata"""
    
    def __init__(self, patterns_dir: Path):
        self.patterns_dir = patterns_dir
        
        # Required front matter fields
        self.required_fields = [
            'title',
            'category',
            'difficulty',
            'when_to_use',
            'when_not_to_use',
            'excellence_tier',
            'pattern_status'
        ]
        
        # Excellence tier specific requirements
        self.tier_requirements = {
            'gold': {
                'required_fields': ['modern_examples', 'production_checklist'],
                'min_examples': 2,
                'min_checklist_items': 5
            },
            'silver': {
                'required_fields': ['modern_examples'],
                'min_examples': 1,
                'min_checklist_items': 3
            },
            'bronze': {
                'required_fields': ['alternatives'],
                'min_alternatives': 1
            }
        }
        
        # Valid values for enums
        self.valid_values = {
            'excellence_tier': ['gold', 'silver', 'bronze'],
            'pattern_status': ['recommended', 'use_with_caution', 'legacy'],
            'category': ['core', 'specialized', 'emerging'],
            'difficulty': ['basic', 'intermediate', 'advanced']
        }
    
    def extract_front_matter(self, file_path: Path) -> Tuple[Dict, int]:
        """Extract YAML front matter from markdown file"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return {}, 0
        
        # Find the closing ---
        end_idx = content.find('---', 3)
        if end_idx == -1:
            return {}, 0
        
        yaml_content = content[3:end_idx]
        line_count = yaml_content.count('\n') + 2  # +2 for the --- markers
        
        try:
            front_matter = yaml.safe_load(yaml_content) or {}
            return front_matter, line_count
        except yaml.YAMLError as e:
            logger.error(f"YAML parse error in {file_path}: {e}")
            return {}, 0
    
    def validate_required_fields(self, pattern_name: str, front_matter: Dict) -> List[ValidationIssue]:
        """Validate that all required fields are present"""
        issues = []
        
        for field in self.required_fields:
            if field not in front_matter:
                issues.append(ValidationIssue(
                    pattern_name=pattern_name,
                    issue_type='missing_field',
                    severity='error',
                    message=f"Missing required field: {field}"
                ))
        
        return issues
    
    def validate_field_values(self, pattern_name: str, front_matter: Dict) -> List[ValidationIssue]:
        """Validate that field values are valid"""
        issues = []
        
        for field, valid_values in self.valid_values.items():
            if field in front_matter:
                value = front_matter[field]
                if value not in valid_values:
                    issues.append(ValidationIssue(
                        pattern_name=pattern_name,
                        issue_type='invalid_value',
                        severity='error',
                        message=f"Invalid value for {field}: '{value}'. Valid values: {', '.join(valid_values)}"
                    ))
        
        return issues
    
    def validate_tier_requirements(self, pattern_name: str, front_matter: Dict) -> List[ValidationIssue]:
        """Validate tier-specific requirements"""
        issues = []
        
        tier = front_matter.get('excellence_tier')
        if not tier or tier not in self.tier_requirements:
            return issues
        
        requirements = self.tier_requirements[tier]
        
        # Check required fields for tier
        for field in requirements.get('required_fields', []):
            if field not in front_matter:
                issues.append(ValidationIssue(
                    pattern_name=pattern_name,
                    issue_type='tier_requirement',
                    severity='error',
                    message=f"{tier.capitalize()} tier patterns must have '{field}' field"
                ))
        
        # Validate gold tier requirements
        if tier == 'gold':
            # Check modern examples
            examples = front_matter.get('modern_examples', [])
            if len(examples) < requirements['min_examples']:
                issues.append(ValidationIssue(
                    pattern_name=pattern_name,
                    issue_type='tier_requirement',
                    severity='error',
                    message=f"Gold tier requires at least {requirements['min_examples']} modern examples (found {len(examples)})"
                ))
            
            # Validate example structure
            for i, example in enumerate(examples):
                if not isinstance(example, dict):
                    issues.append(ValidationIssue(
                        pattern_name=pattern_name,
                        issue_type='invalid_structure',
                        severity='error',
                        message=f"Modern example {i+1} must be a dictionary with 'company', 'implementation', and 'scale' fields"
                    ))
                elif not all(k in example for k in ['company', 'implementation', 'scale']):
                    missing = [k for k in ['company', 'implementation', 'scale'] if k not in example]
                    issues.append(ValidationIssue(
                        pattern_name=pattern_name,
                        issue_type='incomplete_example',
                        severity='error',
                        message=f"Modern example {i+1} missing fields: {', '.join(missing)}"
                    ))
            
            # Check production checklist
            checklist = front_matter.get('production_checklist', [])
            if len(checklist) < requirements['min_checklist_items']:
                issues.append(ValidationIssue(
                    pattern_name=pattern_name,
                    issue_type='tier_requirement',
                    severity='error',
                    message=f"Gold tier requires at least {requirements['min_checklist_items']} production checklist items (found {len(checklist)})"
                ))
        
        # Validate silver tier requirements
        elif tier == 'silver':
            examples = front_matter.get('modern_examples', [])
            if len(examples) < requirements['min_examples']:
                issues.append(ValidationIssue(
                    pattern_name=pattern_name,
                    issue_type='tier_requirement',
                    severity='error',
                    message=f"Silver tier requires at least {requirements['min_examples']} modern example (found {len(examples)})"
                ))
        
        # Validate bronze tier requirements
        elif tier == 'bronze':
            alternatives = front_matter.get('alternatives', [])
            if len(alternatives) < requirements['min_alternatives']:
                issues.append(ValidationIssue(
                    pattern_name=pattern_name,
                    issue_type='tier_requirement',
                    severity='error',
                    message=f"Bronze tier requires at least {requirements['min_alternatives']} alternative pattern (found {len(alternatives)})"
                ))
        
        return issues
    
    def validate_content_structure(self, pattern_name: str, file_path: Path, front_matter: Dict) -> List[ValidationIssue]:
        """Validate content structure based on tier"""
        issues = []
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        tier = front_matter.get('excellence_tier')
        
        # Check for tier badge in content
        tier_badges = {
            'gold': '🏆 Gold Standard Pattern',
            'silver': '🥈 Silver Standard Pattern',
            'bronze': '🥉 Bronze Pattern'
        }
        
        if tier and tier in tier_badges:
            badge_text = tier_badges[tier]
            if badge_text not in content:
                issues.append(ValidationIssue(
                    pattern_name=pattern_name,
                    issue_type='missing_badge',
                    severity='warning',
                    message=f"Missing {tier} tier badge in content. Expected: '{badge_text}'"
                ))
        
        # Check for required sections
        required_sections = {
            'gold': ['## Level', '## Analysis', '## Real-World Examples', '## Production Checklist'],
            'silver': ['## Level', '## Analysis', '## Real-World Examples'],
            'bronze': ['## Level', '## Better Alternatives']
        }
        
        if tier and tier in required_sections:
            for section in required_sections[tier]:
                if section not in content:
                    issues.append(ValidationIssue(
                        pattern_name=pattern_name,
                        issue_type='missing_section',
                        severity='warning',
                        message=f"Missing recommended section for {tier} tier: {section}"
                    ))
        
        return issues
    
    def validate_pattern(self, file_path: Path) -> PatternValidation:
        """Validate a single pattern file"""
        pattern_name = file_path.stem
        issues = []
        
        # Extract front matter
        front_matter, _ = self.extract_front_matter(file_path)
        
        if not front_matter:
            issues.append(ValidationIssue(
                pattern_name=pattern_name,
                issue_type='missing_front_matter',
                severity='error',
                message="No front matter found in file"
            ))
            return PatternValidation(
                pattern_name=pattern_name,
                file_path=file_path,
                is_valid=False,
                issues=issues,
                front_matter={}
            )
        
        # Validate required fields
        issues.extend(self.validate_required_fields(pattern_name, front_matter))
        
        # Validate field values
        issues.extend(self.validate_field_values(pattern_name, front_matter))
        
        # Validate tier-specific requirements
        issues.extend(self.validate_tier_requirements(pattern_name, front_matter))
        
        # Validate content structure
        issues.extend(self.validate_content_structure(pattern_name, file_path, front_matter))
        
        # Determine if pattern is valid (no errors)
        is_valid = not any(issue.severity == 'error' for issue in issues)
        
        return PatternValidation(
            pattern_name=pattern_name,
            file_path=file_path,
            is_valid=is_valid,
            issues=issues,
            front_matter=front_matter
        )
    
    def validate_all_patterns(self) -> Dict[str, PatternValidation]:
        """Validate all patterns in the directory"""
        results = {}
        
        # Find all pattern markdown files
        pattern_files = list(self.patterns_dir.glob('*.md'))
        pattern_files = [f for f in pattern_files if f.stem not in ['index', 'README']]
        
        logger.info(f"Found {len(pattern_files)} patterns to validate")
        
        for pattern_file in pattern_files:
            validation = self.validate_pattern(pattern_file)
            results[pattern_file.stem] = validation
        
        return results
    
    def generate_report(self, results: Dict[str, PatternValidation], output_file: Path):
        """Generate validation report"""
        # Count statistics
        total_patterns = len(results)
        valid_patterns = sum(1 for v in results.values() if v.is_valid)
        total_issues = sum(len(v.issues) for v in results.values())
        error_count = sum(1 for v in results.values() for i in v.issues if i.severity == 'error')
        warning_count = sum(1 for v in results.values() for i in v.issues if i.severity == 'warning')
        
        # Count by tier
        tier_counts = {'gold': 0, 'silver': 0, 'bronze': 0, 'unclassified': 0}
        for validation in results.values():
            tier = validation.front_matter.get('excellence_tier', 'unclassified')
            if tier in tier_counts:
                tier_counts[tier] += 1
            else:
                tier_counts['unclassified'] += 1
        
        report_lines = [
            "# Pattern Validation Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- **Total Patterns**: {total_patterns}",
            f"- **Valid Patterns**: {valid_patterns} ({valid_patterns/total_patterns*100:.1f}%)",
            f"- **Total Issues**: {total_issues}",
            f"  - Errors: {error_count}",
            f"  - Warnings: {warning_count}",
            "",
            "## Tier Distribution",
            f"- **Gold**: {tier_counts['gold']}",
            f"- **Silver**: {tier_counts['silver']}",
            f"- **Bronze**: {tier_counts['bronze']}",
            f"- **Unclassified**: {tier_counts['unclassified']}",
            ""
        ]
        
        # Patterns with errors
        error_patterns = [(name, v) for name, v in results.items() if not v.is_valid]
        if error_patterns:
            report_lines.extend([
                "## ❌ Patterns with Errors",
                ""
            ])
            
            for pattern_name, validation in sorted(error_patterns):
                tier = validation.front_matter.get('excellence_tier', 'unclassified')
                report_lines.append(f"### {pattern_name} ({tier})")
                
                for issue in validation.issues:
                    if issue.severity == 'error':
                        report_lines.append(f"- **ERROR**: {issue.message}")
                
                report_lines.append("")
        
        # Patterns with warnings
        warning_patterns = [(name, v) for name, v in results.items() 
                          if v.is_valid and any(i.severity == 'warning' for i in v.issues)]
        if warning_patterns:
            report_lines.extend([
                "## ⚠️ Patterns with Warnings",
                ""
            ])
            
            for pattern_name, validation in sorted(warning_patterns):
                tier = validation.front_matter.get('excellence_tier', 'unclassified')
                report_lines.append(f"### {pattern_name} ({tier})")
                
                for issue in validation.issues:
                    if issue.severity == 'warning':
                        report_lines.append(f"- **WARNING**: {issue.message}")
                
                report_lines.append("")
        
        # Valid patterns summary
        valid_pattern_list = [(name, v) for name, v in results.items() if v.is_valid and not v.issues]
        if valid_pattern_list:
            report_lines.extend([
                "## ✅ Valid Patterns",
                ""
            ])
            
            # Group by tier
            by_tier = {'gold': [], 'silver': [], 'bronze': []}
            for name, validation in valid_pattern_list:
                tier = validation.front_matter.get('excellence_tier', 'bronze')
                if tier in by_tier:
                    by_tier[tier].append(name)
            
            for tier in ['gold', 'silver', 'bronze']:
                if by_tier[tier]:
                    emoji = {'gold': '🏆', 'silver': '🥈', 'bronze': '🥉'}[tier]
                    report_lines.append(f"### {emoji} {tier.capitalize()} Tier")
                    for name in sorted(by_tier[tier]):
                        report_lines.append(f"- {name}")
                    report_lines.append("")
        
        # Missing tier classifications
        missing_tier = [name for name, v in results.items() 
                       if 'excellence_tier' not in v.front_matter]
        if missing_tier:
            report_lines.extend([
                "## 🔍 Missing Tier Classifications",
                ""
            ])
            for name in sorted(missing_tier):
                report_lines.append(f"- {name}")
            report_lines.append("")
        
        # Write report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Validation report generated: {output_file}")
        
        # Return summary for console output
        return {
            'total': total_patterns,
            'valid': valid_patterns,
            'errors': error_count,
            'warnings': warning_count
        }

def main():
    parser = argparse.ArgumentParser(description='Validate pattern excellence metadata')
    parser.add_argument('--patterns-dir', type=Path, default=Path('docs/patterns'),
                       help='Directory containing pattern markdown files')
    parser.add_argument('--output', type=Path, default=Path('pattern_validation_report.md'),
                       help='Output report file')
    parser.add_argument('--pattern', help='Validate a specific pattern only')
    parser.add_argument('--fix', action='store_true',
                       help='Attempt to fix common issues (adds missing fields with defaults)')
    
    args = parser.parse_args()
    
    # Ensure patterns directory exists
    if not args.patterns_dir.exists():
        logger.error(f"Patterns directory not found: {args.patterns_dir}")
        return 1
    
    # Initialize validator
    validator = PatternValidator(args.patterns_dir)
    
    # Validate patterns
    if args.pattern:
        # Single pattern
        pattern_file = args.patterns_dir / f"{args.pattern}.md"
        if not pattern_file.exists():
            logger.error(f"Pattern file not found: {pattern_file}")
            return 1
        
        validation = validator.validate_pattern(pattern_file)
        
        print(f"\nPattern: {args.pattern}")
        print(f"Valid: {'✅ Yes' if validation.is_valid else '❌ No'}")
        print(f"Tier: {validation.front_matter.get('excellence_tier', 'unclassified')}")
        
        if validation.issues:
            print("\nIssues:")
            for issue in validation.issues:
                severity_emoji = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[issue.severity]
                print(f"{severity_emoji} {issue.severity.upper()}: {issue.message}")
        else:
            print("\n✅ No issues found!")
    else:
        # All patterns
        results = validator.validate_all_patterns()
        summary = validator.generate_report(results, args.output)
        
        print(f"\nValidation complete:")
        print(f"  Total patterns: {summary['total']}")
        print(f"  Valid patterns: {summary['valid']} ({summary['valid']/summary['total']*100:.1f}%)")
        print(f"  Errors: {summary['errors']}")
        print(f"  Warnings: {summary['warnings']}")
        print(f"\nDetailed report saved to: {args.output}")
    
    return 0

if __name__ == '__main__':
    exit(main())
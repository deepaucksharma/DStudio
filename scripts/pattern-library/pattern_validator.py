#!/usr/bin/env python3
"""
Pattern Content Validator

Validates pattern content quality based on execution plan requirements:
1. Essential question presence
2. Line count <= 1000
3. "When not to use" position < 200 lines
4. Template section compliance
5. Code percentage < 20%
6. Minimum 3 diagrams
7. Decision matrix presence

This validator focuses on content quality rather than metadata.
"""

import os
import re
import yaml
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ContentMetrics:
    """Metrics collected from pattern content"""
    total_lines: int = 0
    code_lines: int = 0
    diagram_count: int = 0
    table_count: int = 0
    essential_question_line: Optional[int] = None
    when_not_use_line: Optional[int] = None
    has_decision_matrix: bool = False
    sections_found: Set[str] = field(default_factory=set)
    missing_sections: Set[str] = field(default_factory=set)
    code_blocks: List[Tuple[int, int]] = field(default_factory=list)  # (start_line, end_line)
    diagrams: List[Tuple[int, str]] = field(default_factory=list)  # (line, type)

@dataclass
class ValidationResult:
    """Result of pattern validation"""
    pattern_name: str
    file_path: Path
    passed: bool
    metrics: ContentMetrics
    issues: List[Dict[str, any]] = field(default_factory=list)
    warnings: List[Dict[str, any]] = field(default_factory=list)
    
    def add_issue(self, check: str, message: str, line: Optional[int] = None):
        """Add a validation issue (failure)"""
        issue = {
            'check': check,
            'message': message,
            'severity': 'error'
        }
        if line:
            issue['line'] = line
        self.issues.append(issue)
        self.passed = False
    
    def add_warning(self, check: str, message: str, line: Optional[int] = None):
        """Add a validation warning (non-failure)"""
        warning = {
            'check': check,
            'message': message,
            'severity': 'warning'
        }
        if line:
            warning['line'] = line
        self.warnings.append(warning)

class PatternContentValidator:
    """Validates pattern content quality"""
    
    # Required template sections based on execution plan
    REQUIRED_SECTIONS = {
        'Essential Question',
        'When to Use / When NOT to Use',
        'Level 1: Intuition',
        'Level 2: Foundation',
        'Level 3: Deep Dive',
        'Level 4: Expert',
        'Level 5: Mastery',
        'Quick Reference'
    }
    
    # Optional but recommended sections
    RECOMMENDED_SECTIONS = {
        'Real-World Examples',
        'Production Checklist',
        'Trade-offs',
        'Performance Considerations',
        'Migration Guide'
    }
    
    def __init__(self):
        self.max_lines = 1000
        self.max_when_not_position = 200
        self.max_code_percentage = 0.20
        self.min_diagrams = 3
        
    def extract_front_matter(self, content: str) -> Tuple[Dict, int]:
        """Extract YAML front matter and return (data, line_offset)"""
        if not content.startswith('---\n'):
            return {}, 0
            
        end_match = re.search(r'\n---\n', content[4:])
        if not end_match:
            return {}, 0
            
        yaml_content = content[4:end_match.start() + 4]
        try:
            data = yaml.safe_load(yaml_content) or {}
            line_offset = yaml_content.count('\n') + 2
            return data, line_offset
        except:
            return {}, 0
    
    def analyze_content(self, file_path: Path) -> ContentMetrics:
        """Analyze pattern content and collect metrics"""
        metrics = ContentMetrics()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Skip front matter
        _, front_matter_lines = self.extract_front_matter(content)
        
        metrics.total_lines = len(lines)
        in_code_block = False
        code_block_start = 0
        
        for i, line in enumerate(lines[front_matter_lines:], start=front_matter_lines + 1):
            # Track code blocks
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_block_start = i
                else:
                    in_code_block = False
                    metrics.code_blocks.append((code_block_start, i))
                    metrics.code_lines += (i - code_block_start + 1)
            elif in_code_block:
                continue
                
            # Check for essential question
            if not metrics.essential_question_line:
                if re.match(r'^##?\s+Essential Question', line, re.IGNORECASE):
                    metrics.essential_question_line = i
                elif 'essential_question:' in line.lower():
                    metrics.essential_question_line = i
            
            # Check for "when not to use" section
            if not metrics.when_not_use_line:
                if re.search(r'When (NOT|Not) to Use|Don\'t Use When|❌', line, re.IGNORECASE):
                    metrics.when_not_use_line = i
            
            # Check for diagrams (Mermaid)
            if re.match(r'^```mermaid', line.strip(), re.IGNORECASE):
                metrics.diagrams.append((i, 'mermaid'))
                metrics.diagram_count += 1
            
            # Check for decision matrix/table
            if '|' in line and not in_code_block:
                # Simple heuristic: 3+ pipes might indicate a table
                if line.count('|') >= 3:
                    metrics.table_count += 1
                    # Check if it's a decision-related table
                    if re.search(r'decision|criteria|when|comparison|vs\.?', line, re.IGNORECASE):
                        metrics.has_decision_matrix = True
            
            # Track sections
            if line.startswith('#'):
                # Extract section title
                section_match = re.match(r'^#+\s+(.+)', line)
                if section_match:
                    section_title = section_match.group(1).strip()
                    
                    # Check against required sections (fuzzy match)
                    for required in self.REQUIRED_SECTIONS:
                        if self._fuzzy_section_match(section_title, required):
                            metrics.sections_found.add(required)
                            break
        
        # Determine missing sections
        metrics.missing_sections = self.REQUIRED_SECTIONS - metrics.sections_found
        
        return metrics
    
    def _fuzzy_section_match(self, actual: str, expected: str) -> bool:
        """Fuzzy match section titles"""
        # Normalize both strings
        actual_norm = re.sub(r'[^\w\s]', '', actual.lower())
        expected_norm = re.sub(r'[^\w\s]', '', expected.lower())
        
        # Check if all significant words from expected are in actual
        expected_words = set(expected_norm.split())
        actual_words = set(actual_norm.split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'to', 'in', 'on', 'at'}
        expected_words -= common_words
        actual_words -= common_words
        
        # Check overlap
        if expected_words.issubset(actual_words):
            return True
            
        # Check if the key words are present
        key_mappings = {
            'essential question': ['essential', 'question'],
            'when to use / when not to use': ['when', 'use'],
            'level 1: intuition': ['level', '1', 'intuition'],
            'level 2: foundation': ['level', '2', 'foundation'],
            'level 3: deep dive': ['level', '3', 'deep'],
            'level 4: expert': ['level', '4', 'expert'],
            'level 5: mastery': ['level', '5', 'mastery'],
            'quick reference': ['quick', 'reference']
        }
        
        expected_lower = expected.lower()
        if expected_lower in key_mappings:
            key_words = key_mappings[expected_lower]
            if all(word in actual_norm for word in key_words):
                return True
        
        return False
    
    def validate_pattern(self, file_path: Path) -> ValidationResult:
        """Validate a single pattern file"""
        pattern_name = file_path.stem
        result = ValidationResult(
            pattern_name=pattern_name,
            file_path=file_path,
            passed=True,
            metrics=ContentMetrics()
        )
        
        try:
            # Analyze content
            metrics = self.analyze_content(file_path)
            result.metrics = metrics
            
            # 1. Check essential question
            if not metrics.essential_question_line:
                result.add_issue(
                    'essential_question',
                    'Missing essential question section'
                )
            else:
                # Also check it's in the front matter
                with open(file_path, 'r') as f:
                    content = f.read()
                front_matter, _ = self.extract_front_matter(content)
                if 'essential_question' not in front_matter:
                    result.add_warning(
                        'essential_question',
                        'Essential question found in content but missing from front matter',
                        metrics.essential_question_line
                    )
            
            # 2. Check line count
            if metrics.total_lines > self.max_lines:
                result.add_issue(
                    'line_count',
                    f'File has {metrics.total_lines} lines (max: {self.max_lines})'
                )
            elif metrics.total_lines > self.max_lines * 0.9:
                result.add_warning(
                    'line_count',
                    f'File has {metrics.total_lines} lines (approaching max of {self.max_lines})'
                )
            
            # 3. Check "when not to use" position
            if not metrics.when_not_use_line:
                result.add_issue(
                    'when_not_position',
                    'Missing "When NOT to Use" section'
                )
            elif metrics.when_not_use_line > self.max_when_not_position:
                result.add_issue(
                    'when_not_position',
                    f'"When NOT to Use" at line {metrics.when_not_use_line} (should be < {self.max_when_not_position})'
                )
            
            # 4. Check template sections
            if metrics.missing_sections:
                missing_list = ', '.join(sorted(metrics.missing_sections))
                result.add_issue(
                    'template_sections',
                    f'Missing required sections: {missing_list}'
                )
            
            # 5. Check code percentage
            if metrics.total_lines > 0:
                code_percentage = metrics.code_lines / metrics.total_lines
                if code_percentage > self.max_code_percentage:
                    result.add_issue(
                        'code_percentage',
                        f'Code makes up {code_percentage:.1%} of content (max: {self.max_code_percentage:.0%})'
                    )
            
            # 6. Check diagram count
            if metrics.diagram_count < self.min_diagrams:
                result.add_issue(
                    'diagram_count',
                    f'Only {metrics.diagram_count} diagrams found (min: {self.min_diagrams})'
                )
            
            # 7. Check decision matrix
            if not metrics.has_decision_matrix:
                result.add_issue(
                    'decision_matrix',
                    'No decision matrix/comparison table found'
                )
            
            # Additional quality warnings
            if metrics.table_count < 3:
                result.add_warning(
                    'table_usage',
                    f'Only {metrics.table_count} tables found - consider using more tables for comparisons'
                )
            
        except Exception as e:
            result.add_issue(
                'validation_error',
                f'Error validating file: {str(e)}'
            )
        
        return result
    
    def validate_directory(self, directory: Path, pattern_filter: Optional[str] = None) -> List[ValidationResult]:
        """Validate all patterns in a directory"""
        results = []
        
        # Find all pattern files
        pattern_files = []
        if directory.name == 'pattern-library':
            # Recursively find patterns in subdirectories
            for category_dir in directory.iterdir():
                if category_dir.is_dir() and not category_dir.name.startswith('.'):
                    pattern_files.extend(category_dir.glob('*.md'))
        else:
            # Direct pattern files
            pattern_files = list(directory.glob('*.md'))
        
        # Filter out index files
        pattern_files = [f for f in pattern_files if f.stem not in ['index', 'README', '_template']]
        
        # Apply pattern filter if specified
        if pattern_filter:
            pattern_files = [f for f in pattern_files if pattern_filter in f.stem]
        
        logger.info(f"Found {len(pattern_files)} patterns to validate")
        
        for pattern_file in sorted(pattern_files):
            logger.info(f"Validating {pattern_file.stem}...")
            result = self.validate_pattern(pattern_file)
            results.append(result)
        
        return results
    
    def generate_report(self, results: List[ValidationResult], output_format: str = 'markdown') -> str:
        """Generate validation report"""
        if output_format == 'json':
            return self._generate_json_report(results)
        else:
            return self._generate_markdown_report(results)
    
    def _generate_markdown_report(self, results: List[ValidationResult]) -> str:
        """Generate markdown format report"""
        # Calculate statistics
        total_patterns = len(results)
        passed_patterns = sum(1 for r in results if r.passed)
        total_issues = sum(len(r.issues) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        
        # Group by validation checks
        check_stats = {}
        for result in results:
            for issue in result.issues:
                check = issue['check']
                check_stats[check] = check_stats.get(check, 0) + 1
        
        lines = [
            "# Pattern Content Validation Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- **Total Patterns**: {total_patterns}",
            f"- **Passed**: {passed_patterns} ({passed_patterns/total_patterns*100:.1f}%)",
            f"- **Failed**: {total_patterns - passed_patterns}",
            f"- **Total Issues**: {total_issues}",
            f"- **Total Warnings**: {total_warnings}",
            "",
            "## Validation Criteria",
            "1. ✅ Essential question present",
            "2. ✅ Line count ≤ 1000",
            "3. ✅ 'When NOT to use' within first 200 lines",
            "4. ✅ All template sections present",
            "5. ✅ Code percentage < 20%",
            "6. ✅ Minimum 3 diagrams",
            "7. ✅ Decision matrix present",
            "",
            "## Issue Distribution",
            "| Check | Count | Percentage |",
            "|-------|-------|------------|"
        ]
        
        for check, count in sorted(check_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total_patterns * 100
            lines.append(f"| {check} | {count} | {percentage:.1f}% |")
        
        lines.extend(["", "## Failed Patterns"])
        
        failed_results = [r for r in results if not r.passed]
        if failed_results:
            for result in sorted(failed_results, key=lambda r: len(r.issues), reverse=True):
                lines.extend([
                    "",
                    f"### {result.pattern_name}",
                    f"**File**: `{result.file_path}`",
                    f"**Issues**: {len(result.issues)}",
                    ""
                ])
                
                for issue in result.issues:
                    line_info = f" (line {issue['line']})" if 'line' in issue else ""
                    lines.append(f"- ❌ **{issue['check']}**: {issue['message']}{line_info}")
                
                if result.warnings:
                    lines.append("\n**Warnings**:")
                    for warning in result.warnings:
                        line_info = f" (line {warning['line']})" if 'line' in warning else ""
                        lines.append(f"- ⚠️ {warning['message']}{line_info}")
                
                # Add metrics summary
                metrics = result.metrics
                lines.extend([
                    "",
                    "**Metrics**:",
                    f"- Total lines: {metrics.total_lines}",
                    f"- Code lines: {metrics.code_lines} ({metrics.code_lines/max(metrics.total_lines,1)*100:.1f}%)",
                    f"- Diagrams: {metrics.diagram_count}",
                    f"- Tables: {metrics.table_count}",
                ])
        else:
            lines.append("\n✅ All patterns passed validation!")
        
        # Patterns with warnings only
        warning_only = [r for r in results if r.passed and r.warnings]
        if warning_only:
            lines.extend(["", "## Patterns with Warnings Only"])
            for result in sorted(warning_only, key=lambda r: len(r.warnings), reverse=True):
                lines.extend([
                    "",
                    f"### {result.pattern_name}",
                    f"**Warnings**: {len(result.warnings)}",
                ])
                for warning in result.warnings:
                    line_info = f" (line {warning['line']})" if 'line' in warning else ""
                    lines.append(f"- ⚠️ {warning['message']}{line_info}")
        
        # Perfect patterns
        perfect = [r for r in results if r.passed and not r.warnings]
        if perfect:
            lines.extend(["", "## ✨ Perfect Patterns", ""])
            for result in sorted(perfect, key=lambda r: r.pattern_name):
                lines.append(f"- {result.pattern_name}")
        
        return '\n'.join(lines)
    
    def _generate_json_report(self, results: List[ValidationResult]) -> str:
        """Generate JSON format report"""
        report_data = {
            'generated': datetime.now().isoformat(),
            'summary': {
                'total_patterns': len(results),
                'passed': sum(1 for r in results if r.passed),
                'failed': sum(1 for r in results if not r.passed),
                'total_issues': sum(len(r.issues) for r in results),
                'total_warnings': sum(len(r.warnings) for r in results)
            },
            'patterns': []
        }
        
        for result in results:
            pattern_data = {
                'name': result.pattern_name,
                'file': str(result.file_path),
                'passed': result.passed,
                'issues': result.issues,
                'warnings': result.warnings,
                'metrics': {
                    'total_lines': result.metrics.total_lines,
                    'code_lines': result.metrics.code_lines,
                    'code_percentage': result.metrics.code_lines / max(result.metrics.total_lines, 1),
                    'diagram_count': result.metrics.diagram_count,
                    'table_count': result.metrics.table_count,
                    'has_essential_question': result.metrics.essential_question_line is not None,
                    'has_decision_matrix': result.metrics.has_decision_matrix,
                    'when_not_position': result.metrics.when_not_use_line,
                    'missing_sections': list(result.metrics.missing_sections)
                }
            }
            report_data['patterns'].append(pattern_data)
        
        return json.dumps(report_data, indent=2)

def main():
    parser = argparse.ArgumentParser(
        description='Validate pattern content quality based on execution plan requirements'
    )
    parser.add_argument(
        '--dir', '-d',
        type=Path,
        default=Path('docs/pattern-library'),
        help='Directory containing patterns (default: docs/pattern-library)'
    )
    parser.add_argument(
        '--pattern', '-p',
        help='Validate specific pattern(s) by name filter'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file for report (default: stdout)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'json'],
        default='markdown',
        help='Report format (default: markdown)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if directory exists
    if not args.dir.exists():
        logger.error(f"Directory not found: {args.dir}")
        return 1
    
    # Create validator
    validator = PatternContentValidator()
    
    # Validate patterns
    if args.pattern and args.dir.name != 'pattern-library':
        # Single pattern file
        pattern_file = args.dir / f"{args.pattern}.md"
        if not pattern_file.exists():
            logger.error(f"Pattern file not found: {pattern_file}")
            return 1
        results = [validator.validate_pattern(pattern_file)]
    else:
        # Directory of patterns
        results = validator.validate_directory(args.dir, args.pattern)
    
    # Generate report
    report = validator.generate_report(results, args.format)
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report written to: {args.output}")
    else:
        print(report)
    
    # Exit with error if any patterns failed
    failed_count = sum(1 for r in results if not r.passed)
    if failed_count > 0:
        logger.error(f"{failed_count} patterns failed validation")
        return 1
    else:
        logger.info("All patterns passed validation!")
        return 0

if __name__ == '__main__':
    exit(main())
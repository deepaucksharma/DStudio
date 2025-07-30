#!/usr/bin/env python3
"""
Batch Pattern Validation Script

Runs comprehensive validation on all patterns and generates reports.
Can validate both metadata (using pattern-validator-metadata.py) and
content quality (using pattern_validator.py).
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchPatternValidator:
    """Orchestrates validation across all patterns"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scripts_dir = project_root / 'scripts'
        self.pattern_library_dir = project_root / 'docs' / 'pattern-library'
        self.reports_dir = project_root / 'reports' / 'pattern-validation'
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Validator scripts
        self.metadata_validator = self.scripts_dir / 'pattern-validator-metadata.py'
        self.content_validator = self.scripts_dir / 'pattern_validator.py'
        
    def run_metadata_validation(self) -> Dict:
        """Run metadata validation and return results"""
        logger.info("Running metadata validation...")
        
        output_file = self.reports_dir / f'metadata-validation-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md'
        
        try:
            # Run the metadata validator
            cmd = [
                sys.executable,
                str(self.metadata_validator),
                '--patterns-dir', str(self.pattern_library_dir),
                '--output', str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Metadata validation failed: {result.stderr}")
            else:
                logger.info(f"Metadata validation complete. Report: {output_file}")
                
            return {
                'success': result.returncode == 0,
                'report_file': output_file,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            logger.error(f"Error running metadata validation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_content_validation(self) -> Dict:
        """Run content quality validation and return results"""
        logger.info("Running content validation...")
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        markdown_output = self.reports_dir / f'content-validation-{timestamp}.md'
        json_output = self.reports_dir / f'content-validation-{timestamp}.json'
        
        results = {}
        
        # Run markdown report
        try:
            cmd = [
                sys.executable,
                str(self.content_validator),
                '--dir', str(self.pattern_library_dir),
                '--output', str(markdown_output),
                '--format', 'markdown'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Content validation found issues: {result.stderr}")
            else:
                logger.info(f"Content validation complete. Markdown report: {markdown_output}")
                
            results['markdown'] = {
                'success': result.returncode == 0,
                'report_file': markdown_output,
                'stdout': result.stdout
            }
            
        except Exception as e:
            logger.error(f"Error running content validation (markdown): {e}")
            results['markdown'] = {'success': False, 'error': str(e)}
        
        # Run JSON report for programmatic analysis
        try:
            cmd = [
                sys.executable,
                str(self.content_validator),
                '--dir', str(self.pattern_library_dir),
                '--output', str(json_output),
                '--format', 'json'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Content validation JSON report: {json_output}")
                
                # Load and analyze JSON results
                with open(json_output, 'r') as f:
                    json_data = json.load(f)
                    results['analysis'] = self.analyze_json_results(json_data)
            
            results['json'] = {
                'success': result.returncode == 0,
                'report_file': json_output
            }
            
        except Exception as e:
            logger.error(f"Error running content validation (json): {e}")
            results['json'] = {'success': False, 'error': str(e)}
        
        return results
    
    def analyze_json_results(self, json_data: Dict) -> Dict:
        """Analyze JSON validation results for insights"""
        analysis = {
            'summary': json_data.get('summary', {}),
            'top_issues': {},
            'patterns_by_issue_count': [],
            'perfect_patterns': [],
            'critical_patterns': []  # Patterns with 5+ issues
        }
        
        # Count issues by type
        issue_counts = {}
        for pattern in json_data.get('patterns', []):
            for issue in pattern.get('issues', []):
                check = issue.get('check', 'unknown')
                issue_counts[check] = issue_counts.get(check, 0) + 1
            
            # Track patterns by issue count
            issue_count = len(pattern.get('issues', []))
            pattern_info = {
                'name': pattern['name'],
                'issues': issue_count,
                'warnings': len(pattern.get('warnings', []))
            }
            
            if issue_count == 0 and pattern_info['warnings'] == 0:
                analysis['perfect_patterns'].append(pattern['name'])
            elif issue_count >= 5:
                analysis['critical_patterns'].append(pattern_info)
            
            analysis['patterns_by_issue_count'].append(pattern_info)
        
        # Sort patterns by issue count
        analysis['patterns_by_issue_count'].sort(key=lambda x: x['issues'], reverse=True)
        analysis['top_issues'] = dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True))
        
        return analysis
    
    def generate_summary_report(self, metadata_results: Dict, content_results: Dict) -> Path:
        """Generate a comprehensive summary report"""
        summary_file = self.reports_dir / f'validation-summary-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md'
        
        lines = [
            "# Pattern Validation Summary Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Overview",
            "This report summarizes the results of both metadata and content validation for all patterns.",
            ""
        ]
        
        # Metadata validation summary
        lines.extend([
            "## Metadata Validation",
            f"- Status: {'✅ Passed' if metadata_results.get('success') else '❌ Failed'}",
            f"- Report: `{metadata_results.get('report_file', 'N/A')}`",
            ""
        ])
        
        # Content validation summary
        if 'analysis' in content_results:
            analysis = content_results['analysis']
            summary = analysis.get('summary', {})
            
            lines.extend([
                "## Content Validation",
                f"- Total Patterns: {summary.get('total_patterns', 0)}",
                f"- Passed: {summary.get('passed', 0)} ({summary.get('passed', 0)/max(summary.get('total_patterns', 1), 1)*100:.1f}%)",
                f"- Failed: {summary.get('failed', 0)}",
                f"- Total Issues: {summary.get('total_issues', 0)}",
                f"- Total Warnings: {summary.get('total_warnings', 0)}",
                "",
                "### Top Issues",
                "| Issue Type | Count |",
                "|------------|-------|"
            ])
            
            for issue, count in list(analysis.get('top_issues', {}).items())[:5]:
                lines.append(f"| {issue} | {count} |")
            
            lines.extend([
                "",
                "### Critical Patterns (5+ issues)",
                ""
            ])
            
            if analysis.get('critical_patterns'):
                for pattern in analysis['critical_patterns'][:10]:
                    lines.append(f"- **{pattern['name']}**: {pattern['issues']} issues, {pattern['warnings']} warnings")
            else:
                lines.append("✅ No critical patterns found!")
            
            perfect_count = len(analysis.get('perfect_patterns', []))
            if perfect_count > 0:
                lines.extend([
                    "",
                    f"### Perfect Patterns ({perfect_count} total)",
                    ""
                ])
                for pattern in analysis['perfect_patterns'][:10]:
                    lines.append(f"- {pattern}")
                if perfect_count > 10:
                    lines.append(f"- ... and {perfect_count - 10} more")
        
        lines.extend([
            "",
            "## Report Files",
            f"- Metadata validation: `{metadata_results.get('report_file', 'N/A')}`",
            f"- Content validation (Markdown): `{content_results.get('markdown', {}).get('report_file', 'N/A')}`",
            f"- Content validation (JSON): `{content_results.get('json', {}).get('report_file', 'N/A')}`",
            "",
            "## Next Steps",
            "1. Review critical patterns and fix high-priority issues",
            "2. Use the JSON report for programmatic analysis",
            "3. Track progress by comparing reports over time"
        ])
        
        with open(summary_file, 'w') as f:
            f.write('\n'.join(lines))
        
        return summary_file
    
    def validate_single_pattern(self, pattern_name: str) -> Dict:
        """Validate a single pattern with both validators"""
        logger.info(f"Validating single pattern: {pattern_name}")
        
        results = {}
        
        # Find the pattern file
        pattern_file = None
        for category_dir in self.pattern_library_dir.iterdir():
            if category_dir.is_dir():
                candidate = category_dir / f"{pattern_name}.md"
                if candidate.exists():
                    pattern_file = candidate
                    break
        
        if not pattern_file:
            logger.error(f"Pattern file not found: {pattern_name}")
            return {'error': 'Pattern not found'}
        
        # Run content validation
        try:
            cmd = [
                sys.executable,
                str(self.content_validator),
                '--dir', str(pattern_file.parent),
                '--pattern', pattern_name,
                '--format', 'json'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                results['content'] = json.loads(result.stdout)
            results['success'] = result.returncode == 0
            
        except Exception as e:
            logger.error(f"Error validating pattern: {e}")
            results['error'] = str(e)
        
        return results

def main():
    parser = argparse.ArgumentParser(
        description='Batch validation for all patterns'
    )
    parser.add_argument(
        '--project-root',
        type=Path,
        default=Path.cwd(),
        help='Project root directory'
    )
    parser.add_argument(
        '--pattern',
        help='Validate a single pattern by name'
    )
    parser.add_argument(
        '--skip-metadata',
        action='store_true',
        help='Skip metadata validation'
    )
    parser.add_argument(
        '--skip-content',
        action='store_true',
        help='Skip content validation'
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = BatchPatternValidator(args.project_root)
    
    if args.pattern:
        # Single pattern validation
        results = validator.validate_single_pattern(args.pattern)
        print(json.dumps(results, indent=2))
    else:
        # Full validation
        metadata_results = {}
        content_results = {}
        
        if not args.skip_metadata:
            metadata_results = validator.run_metadata_validation()
        
        if not args.skip_content:
            content_results = validator.run_content_validation()
        
        # Generate summary
        summary_file = validator.generate_summary_report(metadata_results, content_results)
        logger.info(f"Summary report generated: {summary_file}")
        
        # Print quick summary
        if 'analysis' in content_results:
            summary = content_results['analysis']['summary']
            print(f"\nValidation Summary:")
            print(f"  Total patterns: {summary.get('total_patterns', 0)}")
            print(f"  Passed: {summary.get('passed', 0)} ({summary.get('passed', 0)/max(summary.get('total_patterns', 1), 1)*100:.1f}%)")
            print(f"  Failed: {summary.get('failed', 0)}")
            print(f"\nFull reports available in: {validator.reports_dir}")

if __name__ == '__main__':
    main()
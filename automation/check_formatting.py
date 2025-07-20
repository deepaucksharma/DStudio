#!/usr/bin/env python3
"""
Check documentation files for formatting consistency based on STYLE_GUIDE.md
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class FormatChecker:
    def __init__(self, docs_dir: str):
        self.docs_dir = Path(docs_dir)
        self.issues = []
        
    def check_file(self, filepath: Path) -> List[Dict]:
        """Check a single file for formatting issues"""
        issues = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check for emoji in headers (patterns should have them)
        if 'patterns' in str(filepath) and filepath.name != 'index.md':
            if not re.search(r'^## 🎯 Pattern Overview', content, re.MULTILINE):
                issues.append({
                    'file': str(filepath.relative_to(self.docs_dir)),
                    'type': 'missing_pattern_structure',
                    'line': 0,
                    'message': 'Pattern file missing new template structure'
                })
        
        # Check for ASCII art (but not in code blocks)
        ascii_art_indicators = ['┌', '└', '│', '├', '─', '┼', '┤', '┐', '┘']
        in_code_block = False
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if not in_code_block and any(char in line for char in ascii_art_indicators):
                issues.append({
                    'file': str(filepath.relative_to(self.docs_dir)),
                    'type': 'ascii_art',
                    'line': i + 1,
                    'message': f'Possible ASCII art found: {line.strip()[:50]}...'
                })
        
        # Check for footer quote
        if lines and filepath.suffix == '.md':
            last_lines = '\n'.join(lines[-5:])
            has_quote = re.search(r'\*"[^"]+"\*', last_lines)
            
            if 'axioms' in str(filepath) or 'pillars' in str(filepath):
                if not has_quote:
                    issues.append({
                        'file': str(filepath.relative_to(self.docs_dir)),
                        'type': 'missing_footer_quote',
                        'line': len(lines),
                        'message': 'Axiom/Pillar file missing italicized footer quote'
                    })
        
        # Check for consistent table formatting
        in_code_block = False
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
                
            if not in_code_block and '|' in line and i > 0:
                # Check if it's a proper table
                pipe_count = line.count('|')
                if pipe_count >= 3:  # Minimum for a table row
                    # Check if previous line is also a table line or separator
                    if '|' not in lines[i-1] and '---' not in lines[i-1]:
                        # Check if it's the header row (next line should be separator)
                        if i + 1 < len(lines) and '|' in lines[i+1] and '---' in lines[i+1]:
                            continue
                        else:
                            # Check if this might be a continuation or isolated table line
                            if i + 1 < len(lines) and '|' not in lines[i+1]:
                                issues.append({
                                    'file': str(filepath.relative_to(self.docs_dir)),
                                    'type': 'table_formatting',
                                    'line': i + 1,
                                    'message': 'Isolated table row - might be formatting issue'
                                })
        
        return issues
    
    def check_all_files(self) -> Dict[str, List[Dict]]:
        """Check all markdown files in docs directory"""
        all_issues = {}
        
        for filepath in self.docs_dir.rglob('*.md'):
            # Skip template files and meta files
            if any(skip in filepath.name for skip in ['TEMPLATE', 'GUIDE', 'README']):
                continue
                
            issues = self.check_file(filepath)
            if issues:
                all_issues[str(filepath.relative_to(self.docs_dir))] = issues
        
        return all_issues
    
    def generate_report(self, issues: Dict[str, List[Dict]]) -> str:
        """Generate a formatted report of issues"""
        report = ["# Formatting Consistency Report\n"]
        
        if not issues:
            report.append("✅ No formatting issues found!\n")
            return '\n'.join(report)
        
        # Group by issue type
        by_type = {}
        for file, file_issues in issues.items():
            for issue in file_issues:
                issue_type = issue['type']
                if issue_type not in by_type:
                    by_type[issue_type] = []
                by_type[issue_type].append({**issue, 'file': file})
        
        # Report by type
        report.append(f"Found {sum(len(v) for v in by_type.values())} issues in {len(issues)} files:\n")
        
        for issue_type, type_issues in by_type.items():
            report.append(f"\n## {issue_type.replace('_', ' ').title()} ({len(type_issues)} issues)\n")
            
            for issue in type_issues[:10]:  # Show first 10
                report.append(f"- **{issue['file']}** (line {issue['line']}): {issue['message']}")
            
            if len(type_issues) > 10:
                report.append(f"- ... and {len(type_issues) - 10} more")
        
        # Summary of files needing updates
        report.append("\n## Files Needing Updates\n")
        
        pattern_updates = [f for f in issues.keys() if 'patterns' in f and 'missing_pattern_structure' in [i['type'] for i in issues[f]]]
        if pattern_updates:
            report.append(f"\n### Pattern Files Needing New Template ({len(pattern_updates)}):")
            for f in sorted(pattern_updates):
                report.append(f"- {f}")
        
        return '\n'.join(report)


def main():
    """Run formatting check"""
    docs_dir = Path(__file__).parent.parent / 'docs'
    
    if not docs_dir.exists():
        print(f"Error: Docs directory not found at {docs_dir}")
        return
    
    checker = FormatChecker(docs_dir)
    issues = checker.check_all_files()
    report = checker.generate_report(issues)
    
    print(report)
    
    # Save report
    report_path = docs_dir / 'FORMATTING_ISSUES.md'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\nDetailed report saved to: {report_path}")
    
    # Return exit code based on issues
    return 1 if issues else 0


if __name__ == '__main__':
    exit(main())
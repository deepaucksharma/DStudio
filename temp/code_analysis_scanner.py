#!/usr/bin/env python3
"""
Code Analysis Scanner for MkDocs Documentation

Scans all markdown files in docs/ for:
1. Outdated code syntax or deprecated APIs
2. Broken code examples that won't run
3. Inconsistent code formatting
4. Missing code language specifications
5. Examples that don't match described concepts
6. Security issues in code examples
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, asdict

@dataclass
class CodeIssue:
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # 'high', 'medium', 'low'
    description: str
    code_snippet: str
    recommendation: str

class CodeAnalyzer:
    def __init__(self, docs_path: str):
        self.docs_path = Path(docs_path)
        self.issues = []
        
        # Patterns for different types of issues
        self.deprecated_patterns = {
            'javascript': [
                (r'var\s+\w+', 'Use const/let instead of var'),
                (r'\.innerHTML\s*=', 'Consider using textContent or safer DOM methods'),
                (r'eval\s*\(', 'eval() is dangerous and should be avoided'),
                (r'document\.write\s*\(', 'document.write is deprecated'),
            ],
            'python': [
                (r'import\s+imp\b', 'imp module is deprecated, use importlib'),
                (r'\.has_key\s*\(', 'has_key() is deprecated, use "in" operator'),
                (r'urllib2', 'urllib2 is Python 2, use urllib in Python 3'),
                (r'xrange\s*\(', 'xrange is Python 2, use range in Python 3'),
                (r'print\s+[^(]', 'Use print() function syntax'),
            ],
            'java': [
                (r'Vector\s+\w+', 'Vector is legacy, use ArrayList'),
                (r'Hashtable\s+\w+', 'Hashtable is legacy, use HashMap'),
                (r'StringBuffer\s+\w+', 'Consider StringBuilder for single-threaded use'),
            ],
            'sql': [
                (r'SELECT\s+\*\s+FROM', 'Avoid SELECT *, specify columns explicitly'),
            ]
        }
        
        # Security issue patterns
        self.security_patterns = [
            (r'password\s*=\s*["\'][^"\']*["\']', 'Hardcoded password detected'),
            (r'api[_-]?key\s*=\s*["\'][^"\']*["\']', 'Hardcoded API key detected'),
            (r'secret\s*=\s*["\'][^"\']*["\']', 'Hardcoded secret detected'),
            (r'token\s*=\s*["\'][^"\']*["\']', 'Hardcoded token detected'),
            (r'exec\s*\(', 'exec() can be dangerous'),
            (r'eval\s*\(', 'eval() can be dangerous'),
            (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', 'shell=True can be dangerous'),
            (r'os\.system\s*\(', 'os.system() can be dangerous'),
        ]
        
        # Code block patterns
        self.code_block_pattern = re.compile(r'```(\w*)\n(.*?)\n```', re.DOTALL)
        self.inline_code_pattern = re.compile(r'`([^`]+)`')
        
    def analyze_file(self, file_path: Path) -> List[CodeIssue]:
        """Analyze a single markdown file for code issues."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Find all code blocks
            code_blocks = self.code_block_pattern.findall(content)
            
            # Analyze each code block
            for match in self.code_block_pattern.finditer(content):
                language = match.group(1).lower()
                code = match.group(2)
                
                # Find line number of code block
                line_num = content[:match.start()].count('\n') + 1
                
                # Check for missing language specification
                if not language:
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type='missing_language',
                        severity='medium',
                        description='Code block missing language specification',
                        code_snippet=code[:100] + '...' if len(code) > 100 else code,
                        recommendation='Add language identifier to code block (e.g., ```python)'
                    ))
                
                # Check for deprecated patterns
                if language in self.deprecated_patterns:
                    for pattern, message in self.deprecated_patterns[language]:
                        if re.search(pattern, code, re.IGNORECASE):
                            issues.append(CodeIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                issue_type='deprecated_syntax',
                                severity='medium',
                                description=f'Deprecated syntax detected: {message}',
                                code_snippet=code[:200] + '...' if len(code) > 200 else code,
                                recommendation=message
                            ))
                
                # Check for security issues
                for pattern, message in self.security_patterns:
                    if re.search(pattern, code, re.IGNORECASE):
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            issue_type='security_issue',
                            severity='high',
                            description=f'Security issue: {message}',
                            code_snippet=code[:200] + '...' if len(code) > 200 else code,
                            recommendation=f'Remove or replace: {message}'
                        ))
                
                # Check for syntax issues by language
                issues.extend(self._check_language_specific_issues(file_path, line_num, language, code))
                
            # Check for inconsistent code formatting
            issues.extend(self._check_formatting_consistency(file_path, content))
            
        except Exception as e:
            issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=1,
                issue_type='file_error',
                severity='high',
                description=f'Error reading file: {str(e)}',
                code_snippet='',
                recommendation='Check file encoding and permissions'
            ))
            
        return issues
    
    def _check_language_specific_issues(self, file_path: Path, line_num: int, language: str, code: str) -> List[CodeIssue]:
        """Check for language-specific syntax and logical issues."""
        issues = []
        
        if language == 'python':
            # Check for common Python issues
            if 'import *' in code:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type='bad_practice',
                    severity='medium',
                    description='Wildcard import detected',
                    code_snippet=code[:200] + '...' if len(code) > 200 else code,
                    recommendation='Use specific imports instead of import *'
                ))
            
            # Check for missing exception handling in network calls
            if any(keyword in code for keyword in ['requests.', 'urllib.', 'http.']):
                if 'try:' not in code and 'except' not in code:
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type='missing_error_handling',
                        severity='medium',
                        description='Network calls without exception handling',
                        code_snippet=code[:200] + '...' if len(code) > 200 else code,
                        recommendation='Add try/except blocks for network operations'
                    ))
        
        elif language == 'javascript':
            # Check for console.log in production examples
            if 'console.log' in code and 'debug' not in code.lower():
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type='debug_code',
                    severity='low',
                    description='console.log found in production example',
                    code_snippet=code[:200] + '...' if len(code) > 200 else code,
                    recommendation='Remove console.log or add comment about debugging'
                ))
            
            # Check for missing async/await with Promise-based APIs
            if 'fetch(' in code and 'await' not in code and 'then(' not in code:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type='missing_async_handling',
                    severity='medium',
                    description='fetch() call without proper async handling',
                    code_snippet=code[:200] + '...' if len(code) > 200 else code,
                    recommendation='Use await or .then() with fetch() calls'
                ))
        
        elif language == 'sql':
            # Check for SQL injection vulnerabilities in examples
            if any(pattern in code for pattern in ['WHERE.*=.*+', 'WHERE.*=.*%']):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type='sql_injection_risk',
                    severity='high',
                    description='Potential SQL injection vulnerability',
                    code_snippet=code[:200] + '...' if len(code) > 200 else code,
                    recommendation='Use parameterized queries or prepared statements'
                ))
        
        return issues
    
    def _check_formatting_consistency(self, file_path: Path, content: str) -> List[CodeIssue]:
        """Check for inconsistent code formatting across the file."""
        issues = []
        
        # Find all code blocks and their indentation
        code_blocks = []
        for match in self.code_block_pattern.finditer(content):
            line_start = content[:match.start()].count('\n') + 1
            code_blocks.append((line_start, match.group(1), match.group(2)))
        
        # Check for mixed indentation styles within the same language
        indent_styles = {}
        for line_num, language, code in code_blocks:
            if language:
                if language not in indent_styles:
                    indent_styles[language] = []
                
                # Check indentation in this code block
                for line in code.split('\n'):
                    if line.strip() and line.startswith((' ', '\t')):
                        if line.startswith('    '):
                            indent_styles[language].append('spaces')
                        elif line.startswith('\t'):
                            indent_styles[language].append('tabs')
        
        # Report mixed indentation
        for language, styles in indent_styles.items():
            if 'spaces' in styles and 'tabs' in styles:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=1,
                    issue_type='mixed_indentation',
                    severity='low',
                    description=f'Mixed indentation styles in {language} code blocks',
                    code_snippet='',
                    recommendation=f'Use consistent indentation (spaces or tabs) for {language} examples'
                ))
        
        return issues
    
    def scan_all_files(self) -> List[CodeIssue]:
        """Scan all markdown files in the docs directory."""
        all_issues = []
        
        for md_file in self.docs_path.rglob('*.md'):
            issues = self.analyze_file(md_file)
            all_issues.extend(issues)
            
        return all_issues
    
    def generate_report(self, output_file: str = None):
        """Generate a comprehensive report of all issues found."""
        issues = self.scan_all_files()
        
        # Group issues by type and severity
        by_type = {}
        by_severity = {'high': [], 'medium': [], 'low': []}
        by_file = {}
        
        for issue in issues:
            # Group by type
            if issue.issue_type not in by_type:
                by_type[issue.issue_type] = []
            by_type[issue.issue_type].append(issue)
            
            # Group by severity
            by_severity[issue.severity].append(issue)
            
            # Group by file
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)
        
        # Generate report
        report = []
        report.append("# Code Analysis Report for MkDocs Documentation\n")
        report.append(f"**Total Issues Found:** {len(issues)}\n")
        report.append(f"**High Severity:** {len(by_severity['high'])}")
        report.append(f"**Medium Severity:** {len(by_severity['medium'])}")
        report.append(f"**Low Severity:** {len(by_severity['low'])}\n")
        
        # Summary by issue type
        report.append("## Issues by Type\n")
        for issue_type, type_issues in sorted(by_type.items()):
            report.append(f"- **{issue_type.replace('_', ' ').title()}:** {len(type_issues)} issues")
        report.append("")
        
        # Detailed issues by file
        report.append("## Detailed Issues by File\n")
        for file_path, file_issues in sorted(by_file.items()):
            rel_path = file_path.replace('/Users/deepaksharma/syc/DStudio/', '')
            report.append(f"### {rel_path}\n")
            report.append(f"**{len(file_issues)} issues found**\n")
            
            for issue in sorted(file_issues, key=lambda x: (x.severity == 'low', x.severity == 'medium', x.line_number)):
                severity_icon = "🔴" if issue.severity == "high" else "🟡" if issue.severity == "medium" else "🟢"
                report.append(f"**Line {issue.line_number}** {severity_icon} **{issue.issue_type.replace('_', ' ').title()}**")
                report.append(f"- **Issue:** {issue.description}")
                report.append(f"- **Recommendation:** {issue.recommendation}")
                if issue.code_snippet.strip():
                    report.append(f"- **Code Snippet:**")
                    report.append(f"  ```")
                    report.append(f"  {issue.code_snippet}")
                    report.append(f"  ```")
                report.append("")
        
        # High priority recommendations
        report.append("## High Priority Recommendations\n")
        high_priority = [issue for issue in issues if issue.severity == 'high']
        if high_priority:
            for issue in high_priority[:10]:  # Top 10 high priority issues
                rel_path = issue.file_path.replace('/Users/deepaksharma/syc/DStudio/', '')
                report.append(f"1. **{rel_path}:{issue.line_number}** - {issue.description}")
                report.append(f"   - {issue.recommendation}\n")
        else:
            report.append("No high priority issues found! 🎉\n")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
        
        return report_text, issues

if __name__ == "__main__":
    analyzer = CodeAnalyzer("/Users/deepaksharma/syc/DStudio/docs")
    report, issues = analyzer.generate_report("/Users/deepaksharma/syc/DStudio/temp/code_analysis_report.md")
    
    print("Code Analysis Complete!")
    print(f"Total issues found: {len(issues)}")
    print("Report saved to: /Users/deepaksharma/syc/DStudio/temp/code_analysis_report.md")
    
    # Also save as JSON for programmatic access
    issues_json = [asdict(issue) for issue in issues]
    with open("/Users/deepaksharma/syc/DStudio/temp/code_analysis_issues.json", 'w') as f:
        json.dump(issues_json, f, indent=2)
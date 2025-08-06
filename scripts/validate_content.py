#!/usr/bin/env python3
"""
Architects Handbook - Content Validation Tool
Automated validation of content quality, completeness, and technical accuracy
"""

import os
import re
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class ValidationResult:
    """Stores validation results for a document"""
    file_path: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, any] = field(default_factory=dict)
    score: float = 0.0

class ContentValidator:
    """Validates content quality across the Architects Handbook"""
    
    def __init__(self, base_path: str = "docs/architects-handbook"):
        self.base_path = Path(base_path)
        self.results: List[ValidationResult] = []
        
        # Content standards by document type
        self.standards = {
            'case_studies': {
                'min_lines': 500,
                'required_sections': [
                    'Problem Statement', 'Architecture Overview', 
                    'Implementation Details', 'Quantitative Analysis',
                    'Trade-offs', 'Production Checklist'
                ],
                'min_reading_time': 15
            },
            'implementation_playbooks': {
                'min_lines': 800,
                'required_sections': [
                    'Prerequisites', 'Implementation', 'Validation',
                    'Rollback', 'Monitoring'
                ],
                'min_reading_time': 20
            },
            'quantitative_analysis': {
                'min_lines': 400,
                'required_sections': [
                    'Mathematical Foundation', 'Calculator', 
                    'Examples', 'Analysis'
                ],
                'min_reading_time': 10
            },
            'human_factors': {
                'min_lines': 400,
                'required_sections': [
                    'Overview', 'Implementation', 'Best Practices', 'Metrics'
                ],
                'min_reading_time': 15
            }
        }

    def validate_all_content(self) -> Dict[str, any]:
        """Run comprehensive validation across all content"""
        print("🔍 Starting comprehensive content validation...")
        
        md_files = list(self.base_path.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files to validate")
        
        for file_path in md_files:
            if self._should_skip_file(file_path):
                continue
                
            result = self._validate_document(file_path)
            self.results.append(result)
        
        return self._generate_summary_report()

    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if file should be skipped during validation"""
        skip_patterns = ['index.md', 'README.md', 'template']
        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _validate_document(self, file_path: Path) -> ValidationResult:
        """Validate a single document"""
        result = ValidationResult(file_path=str(file_path.relative_to(self.base_path)))
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract frontmatter and content
            frontmatter, body = self._parse_frontmatter(content)
            
            # Determine document type
            doc_type = self._determine_document_type(file_path, frontmatter)
            
            # Run validation checks
            self._validate_frontmatter(frontmatter, result)
            self._validate_content_structure(body, doc_type, result)
            self._validate_technical_content(body, result)
            self._validate_links_and_references(body, result)
            self._calculate_metrics(content, frontmatter, result)
            
            # Calculate overall score
            result.score = self._calculate_quality_score(result)
            
        except Exception as e:
            result.errors.append(f"Validation failed: {str(e)}")
            result.score = 0.0
        
        return result

    def _parse_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Extract YAML frontmatter and content body"""
        if not content.startswith('---'):
            return {}, content
        
        try:
            _, frontmatter_str, body = content.split('---', 2)
            frontmatter = yaml.safe_load(frontmatter_str)
            return frontmatter or {}, body.strip()
        except:
            return {}, content

    def _determine_document_type(self, file_path: Path, frontmatter: Dict) -> str:
        """Determine document type from path and frontmatter"""
        path_str = str(file_path)
        
        if 'case-studies' in path_str:
            return 'case_studies'
        elif 'implementation-playbooks' in path_str:
            return 'implementation_playbooks' 
        elif 'quantitative-analysis' in path_str:
            return 'quantitative_analysis'
        elif 'human-factors' in path_str:
            return 'human_factors'
        
        return frontmatter.get('type', 'generic')

    def _validate_frontmatter(self, frontmatter: Dict, result: ValidationResult):
        """Validate document frontmatter completeness and accuracy"""
        required_fields = ['title', 'description', 'status']
        recommended_fields = ['reading_time', 'difficulty', 'prerequisites']
        
        for field in required_fields:
            if field not in frontmatter:
                result.errors.append(f"Missing required frontmatter field: {field}")
        
        for field in recommended_fields:
            if field not in frontmatter:
                result.warnings.append(f"Missing recommended frontmatter field: {field}")
        
        # Validate specific field formats
        if 'reading_time' in frontmatter:
            reading_time_str = frontmatter['reading_time']
            if not re.match(r'\d+ min$', str(reading_time_str)):
                result.errors.append("reading_time must be in format 'N min'")
        
        if 'status' in frontmatter:
            valid_statuses = ['complete', 'draft', 'in-progress', 'review']
            if frontmatter['status'] not in valid_statuses:
                result.warnings.append(f"Unusual status: {frontmatter['status']}")

    def _validate_content_structure(self, content: str, doc_type: str, result: ValidationResult):
        """Validate document structure and completeness"""
        if doc_type not in self.standards:
            return
        
        standards = self.standards[doc_type]
        lines = content.split('\n')
        
        # Check minimum length
        if len(lines) < standards['min_lines']:
            result.warnings.append(
                f"Document may be too short: {len(lines)} lines "
                f"(minimum: {standards['min_lines']})"
            )
        
        # Check for required sections (fuzzy matching)
        content_lower = content.lower()
        missing_sections = []
        
        for section in standards['required_sections']:
            # Look for section headers containing key terms
            section_patterns = [
                f"#{1,6}.*{section.lower()}",
                f"##.*{section.lower()}",  
                f"###.*{section.lower()}"
            ]
            
            found = any(re.search(pattern, content_lower, re.MULTILINE) 
                       for pattern in section_patterns)
            
            if not found:
                missing_sections.append(section)
        
        if missing_sections:
            result.warnings.append(
                f"Potentially missing sections: {', '.join(missing_sections)}"
            )

    def _validate_technical_content(self, content: str, result: ValidationResult):
        """Validate technical accuracy of content"""
        
        # Check for TODO/FIXME markers
        todo_markers = re.findall(r'(TODO|FIXME|XXX|INCOMPLETE|TBD).*', content, re.IGNORECASE)
        if todo_markers:
            result.warnings.append(f"Found {len(todo_markers)} TODO/FIXME markers")
        
        # Validate code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
        for language, code in code_blocks:
            if language and language.lower() in ['python', 'javascript', 'bash']:
                issues = self._validate_code_block(code, language.lower())
                result.warnings.extend(issues)
        
        # Check for mathematical formulas
        math_formulas = re.findall(r'\$\$(.*?)\$\$', content, re.DOTALL)
        if math_formulas:
            result.metrics['math_formulas'] = len(math_formulas)
        
        # Check for Mermaid diagrams
        mermaid_diagrams = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)
        if mermaid_diagrams:
            result.metrics['mermaid_diagrams'] = len(mermaid_diagrams)
            for diagram in mermaid_diagrams:
                if 'graph' not in diagram and 'flowchart' not in diagram:
                    result.warnings.append("Mermaid diagram may have syntax issues")

    def _validate_code_block(self, code: str, language: str) -> List[str]:
        """Basic syntax validation for code blocks"""
        issues = []
        
        if language == 'python':
            # Check for common Python syntax issues
            if 'import ' in code and not re.search(r'^import ', code, re.MULTILINE):
                issues.append("Python import statements should be at the top")
            
            # Check indentation consistency
            lines = [line for line in code.split('\n') if line.strip()]
            if lines:
                indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
                if indents and any(indent % 4 != 0 for indent in indents if indent > 0):
                    issues.append("Python code may have inconsistent indentation")
        
        elif language == 'javascript':
            # Check for common JavaScript issues
            if code.count('{') != code.count('}'):
                issues.append("JavaScript code has mismatched braces")
            
        elif language == 'bash':
            # Check for common bash issues
            if '#!/bin/bash' not in code and code.strip().startswith('#!/'):
                issues.append("Bash script shebang may be incorrect")
        
        return issues

    def _validate_links_and_references(self, content: str, result: ValidationResult):
        """Validate internal and external links"""
        
        # Find all markdown links
        links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
        
        internal_links = 0
        external_links = 0
        
        for link_text, url in links:
            if url.startswith('http'):
                external_links += 1
                # Note: Full HTTP validation would be done separately to avoid rate limiting
            elif url.endswith('.md') or '/' in url:
                internal_links += 1
                # Basic validation - check if it looks like a valid relative path
                if url.startswith('/') and not url.startswith('/DStudio/'):
                    result.warnings.append(f"Potentially invalid internal link: {url}")
        
        result.metrics['internal_links'] = internal_links
        result.metrics['external_links'] = external_links
        
        # Check for broken reference patterns
        broken_patterns = [
            r'\]\(\)',  # Empty link
            r'\]\(#\)',  # Empty anchor
            r'\]\(TODO\)',  # TODO placeholder
        ]
        
        for pattern in broken_patterns:
            matches = re.findall(pattern, content)
            if matches:
                result.errors.append(f"Found {len(matches)} broken link patterns: {pattern}")

    def _calculate_metrics(self, content: str, frontmatter: Dict, result: ValidationResult):
        """Calculate various content metrics"""
        
        lines = content.split('\n')
        words = len(content.split())
        
        result.metrics.update({
            'total_lines': len(lines),
            'total_words': words,
            'estimated_reading_time': max(1, round(words / 250)),  # 250 words per minute
            'code_blocks': len(re.findall(r'```', content)) // 2,
            'headers': len(re.findall(r'^#+', content, re.MULTILINE)),
            'images': len(re.findall(r'!\[.*?\]\(.*?\)', content)),
        })
        
        # Compare estimated vs declared reading time
        if 'reading_time' in frontmatter:
            declared_time = int(re.search(r'(\d+)', str(frontmatter['reading_time'])).group(1))
            estimated_time = result.metrics['estimated_reading_time']
            
            if abs(declared_time - estimated_time) > 5:  # 5 minute tolerance
                result.warnings.append(
                    f"Reading time mismatch: declared {declared_time}min, "
                    f"estimated {estimated_time}min"
                )

    def _calculate_quality_score(self, result: ValidationResult) -> float:
        """Calculate overall quality score (0-100)"""
        base_score = 100.0
        
        # Deduct for errors and warnings
        base_score -= len(result.errors) * 10  # 10 points per error
        base_score -= len(result.warnings) * 2  # 2 points per warning
        
        # Bonus for completeness
        if result.metrics.get('total_lines', 0) > 500:
            base_score += 5
        
        if result.metrics.get('code_blocks', 0) > 2:
            base_score += 3
            
        if result.metrics.get('mermaid_diagrams', 0) > 0:
            base_score += 2
        
        return max(0, min(100, base_score))

    def _generate_summary_report(self) -> Dict[str, any]:
        """Generate comprehensive validation summary"""
        
        total_docs = len(self.results)
        if total_docs == 0:
            return {"error": "No documents validated"}
        
        # Calculate aggregate metrics
        avg_score = sum(r.score for r in self.results) / total_docs
        total_errors = sum(len(r.errors) for r in self.results)
        total_warnings = sum(len(r.warnings) for r in self.results)
        
        # Categorize results
        excellent = len([r for r in self.results if r.score >= 90])
        good = len([r for r in self.results if 70 <= r.score < 90])
        needs_work = len([r for r in self.results if r.score < 70])
        
        # Content metrics
        total_lines = sum(r.metrics.get('total_lines', 0) for r in self.results)
        total_words = sum(r.metrics.get('total_words', 0) for r in self.results)
        
        # Top issues
        all_errors = []
        all_warnings = []
        
        for result in self.results:
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        error_counts = defaultdict(int)
        warning_counts = defaultdict(int)
        
        for error in all_errors:
            error_counts[error] += 1
        
        for warning in all_warnings:
            warning_counts[warning] += 1
        
        return {
            "summary": {
                "total_documents": total_docs,
                "average_quality_score": round(avg_score, 2),
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "quality_distribution": {
                    "excellent (90-100)": excellent,
                    "good (70-89)": good, 
                    "needs_work (<70)": needs_work
                }
            },
            "content_metrics": {
                "total_lines": total_lines,
                "total_words": total_words,
                "average_doc_length": round(total_lines / total_docs),
                "estimated_total_reading_time": f"{round(total_words / 250)} minutes"
            },
            "top_issues": {
                "most_common_errors": dict(list(error_counts.items())[:5]),
                "most_common_warnings": dict(list(warning_counts.items())[:5])
            },
            "detailed_results": [
                {
                    "file": r.file_path,
                    "score": r.score,
                    "errors": len(r.errors),
                    "warnings": len(r.warnings),
                    "metrics": r.metrics
                }
                for r in sorted(self.results, key=lambda x: x.score)
            ]
        }

def main():
    """Main validation entry point"""
    validator = ContentValidator()
    
    print("🚀 Starting Architects Handbook Content Validation")
    print("=" * 60)
    
    report = validator.validate_all_content()
    
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    summary = report['summary']
    print(f"Documents Validated: {summary['total_documents']}")
    print(f"Average Quality Score: {summary['average_quality_score']}/100")
    print(f"Total Errors: {summary['total_errors']}")
    print(f"Total Warnings: {summary['total_warnings']}")
    
    print(f"\n📈 QUALITY DISTRIBUTION")
    for level, count in summary['quality_distribution'].items():
        percentage = (count / summary['total_documents']) * 100
        print(f"{level}: {count} documents ({percentage:.1f}%)")
    
    print(f"\n📚 CONTENT METRICS")
    metrics = report['content_metrics']
    print(f"Total Content: {metrics['total_lines']:,} lines, {metrics['total_words']:,} words")
    print(f"Average Document Length: {metrics['average_doc_length']} lines")
    print(f"Total Reading Time: {metrics['estimated_total_reading_time']}")
    
    if report['top_issues']['most_common_errors']:
        print(f"\n🚨 TOP ERRORS")
        for error, count in list(report['top_issues']['most_common_errors'].items())[:3]:
            print(f"• {error} ({count} occurrences)")
    
    if report['top_issues']['most_common_warnings']:
        print(f"\n⚠️  TOP WARNINGS")
        for warning, count in list(report['top_issues']['most_common_warnings'].items())[:3]:
            print(f"• {warning} ({count} occurrences)")
    
    # Write detailed report to file
    output_file = "validation_report.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {output_file}")
    
    # Exit with appropriate code
    if summary['total_errors'] > 0:
        print("\n❌ Validation completed with errors")
        return 1
    elif summary['average_quality_score'] < 80:
        print("\n⚠️  Validation completed with quality concerns")
        return 1
    else:
        print("\n✅ Validation completed successfully")
        return 0

if __name__ == "__main__":
    exit(main())
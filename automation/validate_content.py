#!/usr/bin/env python3
"""
Content validation tool to check documentation completeness and quality
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json

class ContentValidator:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.validation_results = defaultdict(dict)
        self.summary = {
            'total_files': 0,
            'complete_files': 0,
            'incomplete_files': 0,
            'missing_sections': defaultdict(int),
            'quality_issues': defaultdict(int)
        }
        
    def validate_axiom_structure(self, file_path, content):
        """Validate axiom files have required sections"""
        required_sections = [
            'The Constraint',
            'Why It Matters', 
            'Real-World Examples',
            'Common Misconceptions',
            'Practical Implications',
            'Exercises',
            'Quiz Questions',
            'Further Reading'
        ]
        
        missing = []
        for section in required_sections:
            if section.lower() not in content.lower():
                missing.append(section)
                
        return missing
    
    def validate_pattern_structure(self, file_path, content):
        """Validate pattern files have required sections"""
        required_sections = [
            'Problem',
            'Solution',
            'Implementation',
            'When to Use',
            'When NOT to Use',
            'Trade-offs',
            'Real Examples',
            'Code Sample',
            'Exercise'
        ]
        
        missing = []
        for section in required_sections:
            # More flexible matching
            if not re.search(rf'#{1,3}\s*{re.escape(section)}', content, re.IGNORECASE):
                missing.append(section)
                
        return missing
    
    def check_code_examples(self, content):
        """Check if code examples are present and valid"""
        code_blocks = re.findall(r'```(\w+)?.*?```', content, re.DOTALL)
        
        issues = []
        if len(code_blocks) == 0:
            issues.append('No code examples found')
        else:
            for i, block in enumerate(code_blocks):
                if not block:  # No language specified
                    issues.append(f'Code block {i+1} missing language specification')
                    
        return issues
    
    def check_exercises(self, content):
        """Check if exercises are present and structured"""
        exercise_pattern = r'(?:Exercise|Problem|Task)\s*\d+[\.:]\s*'
        exercises = re.findall(exercise_pattern, content, re.IGNORECASE)
        
        issues = []
        if len(exercises) == 0:
            issues.append('No exercises found')
        elif len(exercises) < 3:
            issues.append(f'Only {len(exercises)} exercises found (minimum 3 recommended)')
            
        # Check for solutions
        if 'solution' not in content.lower() and len(exercises) > 0:
            issues.append('Exercises found but no solutions provided')
            
        return issues
    
    def check_frontmatter_quality(self, content):
        """Validate frontmatter completeness"""
        issues = []
        
        if not content.startswith('---'):
            issues.append('Missing frontmatter')
            return issues
            
        fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            issues.append('Invalid frontmatter format')
            return issues
            
        fm_content = fm_match.group(1)
        
        # Check required fields
        required_fields = ['title', 'description', 'type', 'difficulty', 'reading_time']
        for field in required_fields:
            if f'{field}:' not in fm_content:
                issues.append(f'Missing frontmatter field: {field}')
                
        # Check description quality
        if 'description:' in fm_content:
            desc_match = re.search(r'description:\s*["\']?(.+?)["\']?\s*$', fm_content, re.MULTILINE)
            if desc_match:
                desc = desc_match.group(1)
                if len(desc) < 20:
                    issues.append('Description too short (< 20 chars)')
                if 'documentation' in desc.lower() and 'distributed systems' in desc.lower():
                    issues.append('Generic description detected')
                    
        return issues
    
    def check_links_quality(self, content):
        """Check for placeholder or broken link patterns"""
        issues = []
        
        # Find suspicious link patterns
        placeholder_patterns = [
            r'\[.*?\]\(#\)',  # Links to just #
            r'\[.*?\]\(\)',   # Empty links
            r'\[.*?\]\(TODO\)',  # TODO links
            r'\[.*?\]\([^/)]+\)',  # Single word links (likely placeholders)
        ]
        
        for pattern in placeholder_patterns:
            matches = re.findall(pattern, content)
            if matches:
                issues.append(f'Placeholder links found: {len(matches)} instances')
                break
                
        return issues
    
    def calculate_completeness_score(self, validation_result):
        """Calculate a completeness score from 0-100"""
        total_checks = 0
        passed_checks = 0
        
        for category, items in validation_result.items():
            if isinstance(items, list):
                total_checks += max(1, len(items) if items else 1)
                if not items:  # Empty list means no issues
                    passed_checks += 1
            elif isinstance(items, bool):
                total_checks += 1
                if items:
                    passed_checks += 1
                    
        return int((passed_checks / total_checks) * 100) if total_checks > 0 else 100
    
    def validate_file(self, file_path):
        """Validate a single markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            relative_path = file_path.relative_to(self.docs_dir)
            path_str = str(relative_path)
            
            result = {}
            
            # Check frontmatter
            result['frontmatter_issues'] = self.check_frontmatter_quality(content)
            
            # Check structure based on type
            if 'axiom' in path_str and 'index.md' in path_str:
                result['missing_sections'] = self.validate_axiom_structure(file_path, content)
            elif 'patterns' in path_str and path_str.endswith('.md'):
                result['missing_sections'] = self.validate_pattern_structure(file_path, content)
            else:
                result['missing_sections'] = []
                
            # Check code examples
            result['code_issues'] = self.check_code_examples(content)
            
            # Check exercises
            if 'exercise' not in path_str:  # Don't check exercise files themselves
                result['exercise_issues'] = self.check_exercises(content)
            else:
                result['exercise_issues'] = []
                
            # Check link quality
            result['link_issues'] = self.check_links_quality(content)
            
            # Calculate completeness
            result['completeness_score'] = self.calculate_completeness_score(result)
            
            # Update summary
            self.summary['total_files'] += 1
            if result['completeness_score'] >= 80:
                self.summary['complete_files'] += 1
            else:
                self.summary['incomplete_files'] += 1
                
            # Track issues
            for section in result.get('missing_sections', []):
                self.summary['missing_sections'][section] += 1
                
            for category in ['frontmatter_issues', 'code_issues', 'exercise_issues', 'link_issues']:
                for issue in result.get(category, []):
                    self.summary['quality_issues'][issue] += 1
                    
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def validate_all(self):
        """Validate all markdown files"""
        print("🔍 Validating all content files...\n")
        
        for md_file in sorted(self.docs_dir.rglob("*.md")):
            # Skip non-content files
            if any(x in str(md_file) for x in ['TEMPLATE', 'GUIDE', 'STYLE', 'NAVIGATION', 'FORMATTING']):
                continue
                
            relative_path = md_file.relative_to(self.docs_dir)
            
            result = self.validate_file(md_file)
            self.validation_results[str(relative_path)] = result
            
            # Print summary for each file
            if result.get('completeness_score', 0) < 80:
                score = result.get('completeness_score', 0)
                print(f"❌ {relative_path} - {score}% complete")
                
                if result.get('missing_sections'):
                    print(f"   Missing: {', '.join(result['missing_sections'][:3])}")
                if result.get('code_issues'):
                    print(f"   Code: {result['code_issues'][0]}")
                if result.get('exercise_issues'):
                    print(f"   Exercises: {result['exercise_issues'][0]}")
                print()
    
    def generate_report(self):
        """Generate validation report"""
        report = []
        report.append("# Content Validation Report\n")
        report.append(f"Total files analyzed: {self.summary['total_files']}\n")
        report.append(f"Complete files (≥80%): {self.summary['complete_files']}")
        report.append(f"Incomplete files (<80%): {self.summary['incomplete_files']}\n")
        
        # Most common missing sections
        if self.summary['missing_sections']:
            report.append("## Most Common Missing Sections\n")
            sorted_sections = sorted(self.summary['missing_sections'].items(), 
                                   key=lambda x: x[1], reverse=True)
            for section, count in sorted_sections[:10]:
                report.append(f"- {section}: {count} files")
            report.append("")
            
        # Quality issues
        if self.summary['quality_issues']:
            report.append("## Common Quality Issues\n")
            sorted_issues = sorted(self.summary['quality_issues'].items(),
                                 key=lambda x: x[1], reverse=True)
            for issue, count in sorted_issues[:10]:
                report.append(f"- {issue}: {count} occurrences")
            report.append("")
            
        # Files needing attention
        report.append("## Files Needing Immediate Attention\n")
        
        urgent_files = [(path, result) for path, result in self.validation_results.items()
                       if result.get('completeness_score', 100) < 50]
        
        for path, result in sorted(urgent_files, key=lambda x: x[1].get('completeness_score', 100))[:20]:
            score = result.get('completeness_score', 0)
            report.append(f"\n### {path} ({score}% complete)")
            
            if result.get('missing_sections'):
                report.append(f"Missing sections: {', '.join(result['missing_sections'])}")
            if result.get('frontmatter_issues'):
                report.append(f"Frontmatter: {', '.join(result['frontmatter_issues'])}")
            if result.get('code_issues'):
                report.append(f"Code: {', '.join(result['code_issues'])}")
            if result.get('exercise_issues'):
                report.append(f"Exercises: {', '.join(result['exercise_issues'])}")
                
        # Save detailed results
        with open('validation_results.json', 'w') as f:
            json.dump({
                'summary': self.summary,
                'details': self.validation_results
            }, f, indent=2, default=str)
            
        return '\n'.join(report)


if __name__ == "__main__":
    validator = ContentValidator()
    validator.validate_all()
    
    report = validator.generate_report()
    
    with open('content_validation_report.md', 'w') as f:
        f.write(report)
        
    print("\n" + "="*50)
    print("📊 VALIDATION SUMMARY")
    print("="*50)
    print(f"Total files: {validator.summary['total_files']}")
    print(f"Complete (≥80%): {validator.summary['complete_files']}")
    print(f"Incomplete (<80%): {validator.summary['incomplete_files']}")
    print(f"\n✅ Report saved to: content_validation_report.md")
    print(f"📄 Detailed results: validation_results.json")
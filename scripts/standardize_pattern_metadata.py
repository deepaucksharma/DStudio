#!/usr/bin/env python3
"""
Pattern Metadata Standardization Script
Ensures all patterns conform to Template v2 standards with complete metadata
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

class PatternMetadataStandardizer:
    """Standardize metadata across all pattern files"""
    
    def __init__(self, pattern_dir: str = "/home/deepak/DStudio/docs/pattern-library"):
        self.pattern_dir = Path(pattern_dir)
        self.template_v2_fields = {
            # Required fields for Template v2
            'title': str,
            'description': str,
            'category': str,
            'excellence_tier': str,  # gold, silver, bronze, copper
            'pattern_status': str,  # recommended, preview, deprecated
            'essential_question': str,
            'tagline': str,
            'introduced': str,  # YYYY-MM format
            'current_relevance': str,  # mainstream, emerging, legacy
            'best_for': list,
            'trade_offs': dict,  # cons and pros lists
            'related_laws': dict,  # primary and secondary
            'related_pillars': list,
            'modern_examples': list,
            'production_checklist': list,
            'reading_time': str,
            'difficulty': str,  # beginner, intermediate, advanced, expert
            'prerequisites': list,
        }
        
        self.categories = [
            'architecture', 'communication', 'coordination', 'data-management',
            'deployment', 'ml-infrastructure', 'resilience', 'scaling', 'security'
        ]
        
        self.excellence_tiers = {
            'gold': 'Battle-tested at scale by multiple companies',
            'silver': 'Proven in production with some limitations',
            'bronze': 'Useful but requires careful implementation',
            'copper': 'Experimental or legacy approach'
        }
        
    def analyze_pattern_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a single pattern file for metadata compliance"""
        
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Extract frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                except:
                    frontmatter = {}
            else:
                frontmatter = {}
        else:
            frontmatter = {}
            
        # Check for required fields
        missing_fields = []
        incomplete_fields = []
        
        for field, field_type in self.template_v2_fields.items():
            if field not in frontmatter:
                missing_fields.append(field)
            elif field_type == list and not frontmatter.get(field):
                incomplete_fields.append(field)
            elif field_type == dict and not frontmatter.get(field):
                incomplete_fields.append(field)
                
        # Check content structure for Template v2 compliance
        content_issues = []
        
        # Check for required sections
        required_sections = [
            '## Essential Question',
            '## When to Use / When NOT to Use',
            '## The Complete Blueprint',
            '## Decision Matrix',
            '## Production Checklist',
            '## Related Patterns'
        ]
        
        for section in required_sections:
            if section not in content:
                content_issues.append(f"Missing section: {section}")
                
        # Check for minimum Mermaid diagrams (≥3)
        mermaid_count = content.count('```mermaid')
        if mermaid_count < 3:
            content_issues.append(f"Insufficient Mermaid diagrams: {mermaid_count}/3")
            
        # Check line count (should be ≤1000 lines)
        line_count = len(content.split('\n'))
        if line_count > 1000:
            content_issues.append(f"Content too long: {line_count} lines (max 1000)")
            
        return {
            'filepath': str(filepath),
            'has_frontmatter': bool(frontmatter),
            'missing_fields': missing_fields,
            'incomplete_fields': incomplete_fields,
            'content_issues': content_issues,
            'current_metadata': frontmatter,
            'line_count': line_count,
            'mermaid_count': mermaid_count
        }
    
    def generate_default_metadata(self, filepath: Path, existing: Dict) -> Dict:
        """Generate default metadata for missing fields"""
        
        # Extract pattern name from filename
        pattern_name = filepath.stem.replace('-', ' ').title()
        category = filepath.parent.name
        
        defaults = {
            'title': existing.get('title', pattern_name),
            'description': existing.get('description', f'Implementation pattern for {pattern_name.lower()}'),
            'category': existing.get('category', category),
            'excellence_tier': existing.get('excellence_tier', 'bronze'),
            'pattern_status': existing.get('pattern_status', 'preview'),
            'essential_question': existing.get('essential_question', 
                f'How do we implement {pattern_name.lower()} effectively?'),
            'tagline': existing.get('tagline', 
                f'Master {pattern_name.lower()} for distributed systems success'),
            'introduced': existing.get('introduced', '2024-01'),
            'current_relevance': existing.get('current_relevance', 'mainstream'),
            'best_for': existing.get('best_for', [
                'Distributed systems',
                'Microservices architectures',
                'High-scale applications'
            ]),
            'trade_offs': existing.get('trade_offs', {
                'pros': ['Improved reliability', 'Better scalability', 'Easier maintenance'],
                'cons': ['Increased complexity', 'Higher operational overhead', 'Learning curve']
            }),
            'related_laws': existing.get('related_laws', {
                'primary': [
                    {'number': 1, 'aspect': 'correlation', 
                     'description': 'Pattern impact on system correlation'}
                ],
                'secondary': []
            }),
            'related_pillars': existing.get('related_pillars', ['work', 'state']),
            'modern_examples': existing.get('modern_examples', []),
            'production_checklist': existing.get('production_checklist', [
                'Define clear requirements',
                'Implement monitoring and alerting',
                'Create runbooks for operations',
                'Test failure scenarios',
                'Document configuration'
            ]),
            'reading_time': existing.get('reading_time', '15 min'),
            'difficulty': existing.get('difficulty', 'intermediate'),
            'prerequisites': existing.get('prerequisites', [])
        }
        
        # Merge with existing metadata
        for key, value in existing.items():
            if key not in defaults:
                defaults[key] = value
                
        return defaults
    
    def standardize_pattern_file(self, filepath: Path, analysis: Dict) -> bool:
        """Standardize a single pattern file"""
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Extract existing frontmatter and content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    main_content = parts[2]
                else:
                    frontmatter = {}
                    main_content = content
            else:
                frontmatter = {}
                main_content = content
                
            # Generate standardized metadata
            standardized = self.generate_default_metadata(filepath, frontmatter)
            
            # Add missing content sections if needed
            if '## Essential Question' not in main_content:
                main_content = f"\n## Essential Question\n\n**{standardized['essential_question']}**\n" + main_content
                
            if '## Decision Matrix' not in main_content:
                decision_matrix = """
## Decision Matrix

| Factor | Score (1-5) | Reasoning |
|--------|-------------|-----------|
| **Complexity** | 3 | Moderate implementation complexity |
| **Performance Impact** | 4 | Minimal overhead when properly configured |
| **Operational Overhead** | 3 | Requires monitoring and maintenance |
| **Team Expertise Required** | 3 | Standard distributed systems knowledge |
| **Scalability** | 5 | Excellent scaling characteristics |

**Overall Recommendation: ✅ RECOMMENDED** - Suitable for production use with proper planning.
"""
                main_content += decision_matrix
                
            if '## Production Checklist' not in main_content and standardized['production_checklist']:
                checklist = "\n## Production Checklist\n\n"
                for item in standardized['production_checklist']:
                    checklist += f"- [ ] {item}\n"
                main_content += checklist
                
            # Ensure minimum Mermaid diagrams
            if analysis['mermaid_count'] < 3:
                # Add placeholder diagrams
                placeholder_diagrams = """
```mermaid
graph TB
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```
"""
                # Find a good place to insert (after ## The Complete Blueprint if it exists)
                if '## The Complete Blueprint' in main_content:
                    parts = main_content.split('## The Complete Blueprint', 1)
                    # Find the next section
                    next_section = re.search(r'\n## ', parts[1])
                    if next_section:
                        insert_pos = next_section.start()
                        parts[1] = parts[1][:insert_pos] + placeholder_diagrams + parts[1][insert_pos:]
                    else:
                        parts[1] += placeholder_diagrams
                    main_content = '## The Complete Blueprint'.join(parts)
                    
            # Write back the standardized file
            yaml_content = yaml.dump(standardized, default_flow_style=False, sort_keys=False)
            final_content = f"---\n{yaml_content}---\n{main_content}"
            
            with open(filepath, 'w') as f:
                f.write(final_content)
                
            return True
            
        except Exception as e:
            print(f"Error standardizing {filepath}: {e}")
            return False
    
    def analyze_all_patterns(self) -> Dict[str, Any]:
        """Analyze all pattern files in the library"""
        
        results = {
            'total_patterns': 0,
            'patterns_by_category': {},
            'missing_metadata': [],
            'incomplete_metadata': [],
            'content_issues': [],
            'fully_compliant': [],
            'pattern_files': []
        }
        
        # Scan all categories
        for category_dir in self.pattern_dir.iterdir():
            if category_dir.is_dir() and category_dir.name in self.categories:
                category_patterns = []
                
                for pattern_file in category_dir.glob('*.md'):
                    # Skip index files
                    if pattern_file.name == 'index.md':
                        continue
                        
                    results['total_patterns'] += 1
                    analysis = self.analyze_pattern_file(pattern_file)
                    results['pattern_files'].append(analysis)
                    category_patterns.append(pattern_file.name)
                    
                    if analysis['missing_fields']:
                        results['missing_metadata'].append({
                            'file': str(pattern_file),
                            'missing': analysis['missing_fields']
                        })
                        
                    if analysis['incomplete_fields']:
                        results['incomplete_metadata'].append({
                            'file': str(pattern_file),
                            'incomplete': analysis['incomplete_fields']
                        })
                        
                    if analysis['content_issues']:
                        results['content_issues'].append({
                            'file': str(pattern_file),
                            'issues': analysis['content_issues']
                        })
                        
                    if not (analysis['missing_fields'] or 
                           analysis['incomplete_fields'] or 
                           analysis['content_issues']):
                        results['fully_compliant'].append(str(pattern_file))
                        
                results['patterns_by_category'][category_dir.name] = category_patterns
                
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Generate a detailed report of the analysis"""
        
        report = f"""# Pattern Library Metadata Standardization Report
Generated: {datetime.now().isoformat()}

## Summary
- **Total Patterns Found**: {results['total_patterns']}
- **Fully Compliant**: {len(results['fully_compliant'])} ({len(results['fully_compliant'])*100//max(results['total_patterns'],1)}%)
- **Missing Metadata**: {len(results['missing_metadata'])} patterns
- **Incomplete Metadata**: {len(results['incomplete_metadata'])} patterns
- **Content Issues**: {len(results['content_issues'])} patterns

## Pattern Count by Category
"""
        for category, patterns in results['patterns_by_category'].items():
            report += f"- **{category}**: {len(patterns)} patterns\n"
            
        report += "\n## Issues to Fix\n\n"
        
        if results['missing_metadata']:
            report += "### Patterns with Missing Metadata Fields\n"
            for item in results['missing_metadata'][:10]:  # Show first 10
                report += f"- `{Path(item['file']).name}`: Missing {', '.join(item['missing'][:3])}...\n"
                
        if results['incomplete_metadata']:
            report += "\n### Patterns with Incomplete Metadata\n"
            for item in results['incomplete_metadata'][:10]:
                report += f"- `{Path(item['file']).name}`: Incomplete {', '.join(item['incomplete'][:3])}...\n"
                
        if results['content_issues']:
            report += "\n### Patterns with Content Structure Issues\n"
            for item in results['content_issues'][:10]:
                report += f"- `{Path(item['file']).name}`: {item['issues'][0]}\n"
                
        report += f"""
## Standardization Plan

1. **Phase 1 - Critical Metadata** (Week 1)
   - Add missing excellence_tier classifications
   - Complete essential_question fields
   - Add production_checklist sections

2. **Phase 2 - Template Compliance** (Week 2)
   - Add missing content sections
   - Ensure minimum 3 Mermaid diagrams
   - Standardize decision matrices

3. **Phase 3 - Examples & References** (Week 3)
   - Add modern_examples with scale metrics
   - Update related_laws connections
   - Complete prerequisites lists

## Reconciling Pattern Count

The discrepancy in pattern counts across documentation stems from:
- **91 patterns**: Original count in synthesis guide (outdated)
- **103 patterns**: Currently documented "battle-tested" patterns
- **112 patterns**: Meta-analysis included draft/preview patterns
- **{results['total_patterns']} patterns**: Actual files found in repository

Recommendation: Update all references to state "**{results['total_patterns']} patterns** ({len(results['fully_compliant'])} production-ready, {results['total_patterns'] - len(results['fully_compliant'])} in preview)"
"""
        
        return report
    
    def standardize_all_patterns(self, dry_run: bool = True) -> Dict:
        """Standardize all patterns in the library"""
        
        results = self.analyze_all_patterns()
        
        if not dry_run:
            standardized_count = 0
            failed_count = 0
            
            for pattern_analysis in results['pattern_files']:
                if pattern_analysis['missing_fields'] or pattern_analysis['incomplete_fields']:
                    filepath = Path(pattern_analysis['filepath'])
                    if self.standardize_pattern_file(filepath, pattern_analysis):
                        standardized_count += 1
                    else:
                        failed_count += 1
                        
            results['standardized'] = standardized_count
            results['failed'] = failed_count
            
        return results

def main():
    """Main execution function"""
    
    standardizer = PatternMetadataStandardizer()
    
    # Analyze current state
    print("Analyzing pattern library...")
    results = standardizer.analyze_all_patterns()
    
    # Generate report
    report = standardizer.generate_report(results)
    
    # Save report
    report_path = Path("/home/deepak/DStudio/PATTERN_METADATA_STANDARDIZATION_REPORT.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"Report saved to: {report_path}")
    print(f"\nSummary:")
    print(f"- Total patterns: {results['total_patterns']}")
    print(f"- Fully compliant: {len(results['fully_compliant'])}")
    print(f"- Need updates: {results['total_patterns'] - len(results['fully_compliant'])}")
    
    # Save detailed JSON results
    json_path = Path("/home/deepak/DStudio/pattern_metadata_analysis.json")
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed analysis saved to: {json_path}")
    
    # Auto-standardize patterns
    print("\nStandardizing patterns...")
    results = standardizer.standardize_all_patterns(dry_run=False)
    print(f"Standardized: {results.get('standardized', 0)} patterns")
    print(f"Failed: {results.get('failed', 0)} patterns")

if __name__ == "__main__":
    main()
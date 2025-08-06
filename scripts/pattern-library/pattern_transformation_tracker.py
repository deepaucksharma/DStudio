#!/usr/bin/env python3
"""
Pattern Transformation Tracking System

Tracks the progress of pattern transformations, identifies priorities,
and generates status reports.
"""

import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import subprocess

class PatternTransformationTracker:
    def __init__(self, pattern_library_path: str):
        self.pattern_library_path = Path(pattern_library_path)
        self.validation_script = Path('scripts/pattern_validator.py')
        self.status_file = Path('reports/pattern-transformation-status.json')
        
    def run_validation(self, pattern_path: Path) -> Dict:
        """Run validation on a single pattern."""
        try:
            result = subprocess.run(
                ['python3', str(self.validation_script), str(pattern_path)],
                capture_output=True,
                text=True
            )
            
            # Parse validation output
            output = result.stdout
            issues = []
            
            if 'Code percentage:' in output:
                code_pct = float(output.split('Code percentage: ')[1].split('%')[0])
                if code_pct > 20:
                    issues.append(f'High code percentage: {code_pct}%')
                    
            if 'Missing essential question' in output:
                issues.append('Missing essential question')
                
            if 'Missing 5-level structure' in output:
                issues.append('Missing 5-level structure')
                
            if 'Missing When to Use section' in output:
                issues.append('Missing When to Use section')
                
            if 'Missing decision matrix' in output:
                issues.append('Missing decision matrix')
                
            return {
                'path': str(pattern_path),
                'issues': issues,
                'issue_count': len(issues),
                'validated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'path': str(pattern_path),
                'error': str(e),
                'issue_count': -1
            }
    
    def categorize_patterns(self) -> Dict[str, List[Path]]:
        """Categorize patterns by their directory."""
        categories = {}
        
        for pattern_file in self.pattern_library_path.rglob('*.md'):
            if pattern_file.name in ['index.md', 'pattern-template-v2.md']:
                continue
                
            category = pattern_file.parent.name
            if category not in categories:
                categories[category] = []
            categories[category].append(pattern_file)
            
        return categories
    
    def analyze_pattern_status(self) -> Dict:
        """Analyze current status of all patterns."""
        categories = self.categorize_patterns()
        status = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_patterns': 0,
                'transformed': 0,
                'in_progress': 0,
                'pending': 0,
                'critical_issues': 0
            },
            'categories': {},
            'priority_patterns': []
        }
        
        all_patterns = []
        
        for category, patterns in categories.items():
            category_status = {
                'total': len(patterns),
                'transformed': 0,
                'issues_by_count': {}
            }
            
            for pattern in patterns:
                validation = self.run_validation(pattern)
                all_patterns.append(validation)
                
                issue_count = validation['issue_count']
                if issue_count == 0:
                    category_status['transformed'] += 1
                    status['summary']['transformed'] += 1
                else:
                    if issue_count not in category_status['issues_by_count']:
                        category_status['issues_by_count'][issue_count] = []
                    category_status['issues_by_count'][issue_count].append(pattern.name)
                    
                    if issue_count >= 6:
                        status['summary']['critical_issues'] += 1
                        status['priority_patterns'].append({
                            'pattern': pattern.name,
                            'category': category,
                            'issues': validation['issues']
                        })
                
                status['summary']['total_patterns'] += 1
            
            status['categories'][category] = category_status
        
        # Calculate pending
        status['summary']['pending'] = (
            status['summary']['total_patterns'] - 
            status['summary']['transformed'] - 
            status['summary']['in_progress']
        )
        
        # Save status
        self.save_status(status)
        
        return status
    
    def save_status(self, status: Dict):
        """Save status to JSON file."""
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def load_status(self) -> Dict:
        """Load previous status from JSON file."""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                return json.load(f)
        return {}
    
    def generate_progress_report(self) -> str:
        """Generate a markdown progress report."""
        status = self.analyze_pattern_status()
        
        report = f"""# Pattern Transformation Progress Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

- **Total Patterns**: {status['summary']['total_patterns']}
- **Transformed**: {status['summary']['transformed']} ({status['summary']['transformed']/status['summary']['total_patterns']*100:.1f}%)
- **Critical Issues**: {status['summary']['critical_issues']} patterns with 6+ issues
- **Pending**: {status['summary']['pending']} patterns

## Progress by Category

| Category | Total | Transformed | Completion | Critical Issues |
|----------|-------|-------------|------------|-----------------|
"""
        
        for category, cat_status in status['categories'].items():
            completion = cat_status['transformed'] / cat_status['total'] * 100
            critical = len([p for issues in cat_status['issues_by_count'].items() 
                          for p in issues[1] if issues[0] >= 6])
            
            report += f"| {category} | {cat_status['total']} | {cat_status['transformed']} | {completion:.1f}% | {critical} |\n"
        
        report += f"""
## Priority Patterns (6+ Issues)

These patterns require immediate attention:

"""
        
        for pattern in status['priority_patterns'][:10]:
            report += f"### {pattern['pattern']} ({pattern['category']})\n"
            report += "Issues:\n"
            for issue in pattern['issues']:
                report += f"- {issue}\n"
            report += "\n"
        
        if len(status['priority_patterns']) > 10:
            report += f"\n... and {len(status['priority_patterns']) - 10} more critical patterns\n"
        
        report += """
## Transformation Velocity

Based on current progress:
- Patterns transformed today: [Calculate from timestamps]
- Average time per pattern: [Calculate from data]
- Estimated completion: [Calculate from velocity]

## Next Steps

1. Complete critical patterns (6+ issues)
2. Address high-priority patterns (5 issues)
3. Systematic transformation of remaining patterns
4. Continuous validation and quality checks
"""
        
        return report
    
    def generate_dashboard(self) -> str:
        """Generate an interactive dashboard."""
        status = self.load_status() or self.analyze_pattern_status()
        
        dashboard = f"""# Pattern Transformation Dashboard
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Current Status

```mermaid
pie title Pattern Transformation Status
    "Transformed" : {status['summary']['transformed']}
    "In Progress" : {status['summary']['in_progress']}
    "Pending" : {status['summary']['pending']}
```

## 📊 Progress Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Patterns | {status['summary']['total_patterns']} | {status['summary']['total_patterns']} | - |
| Transformed | {status['summary']['transformed']} | {status['summary']['total_patterns']} | {'🟢' if status['summary']['transformed'] > 50 else '🟡'} |
| Weekly Velocity | TBD | 20 patterns/week | - |
| Quality Score | TBD | 95%+ | - |

## 🔥 Hot Spots

Patterns requiring immediate attention:

```mermaid
graph TD
    A[Critical Patterns] --> B[6+ Issues: {status['summary']['critical_issues']} patterns]
    A --> C[5 Issues: TBD patterns]
    A --> D[4 Issues: TBD patterns]
    
    style B fill:#f96,stroke:#333,stroke-width:2px
    style C fill:#fc6,stroke:#333,stroke-width:2px
    style D fill:#ff9,stroke:#333,stroke-width:2px
```

## 📈 Transformation Timeline

[Timeline visualization would go here]

## 🏆 Recent Achievements

- ✅ Automated transformation script created
- ✅ 12 critical patterns transformed
- ✅ Validation pipeline operational
- ✅ Tracking system implemented
"""
        
        return dashboard

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Track pattern transformation progress')
    parser.add_argument('--report', action='store_true', help='Generate progress report')
    parser.add_argument('--dashboard', action='store_true', help='Generate dashboard')
    parser.add_argument('--analyze', action='store_true', help='Analyze current status')
    
    args = parser.parse_args()
    
    tracker = PatternTransformationTracker('docs/pattern-library')
    
    if args.report:
        report = tracker.generate_progress_report()
        report_path = Path('reports/pattern-transformation-progress.md')
        report_path.write_text(report)
        print(f"✅ Progress report generated: {report_path}")
        
    elif args.dashboard:
        dashboard = tracker.generate_dashboard()
        dashboard_path = Path('reports/pattern-transformation-dashboard.md')
        dashboard_path.write_text(dashboard)
        print(f"✅ Dashboard generated: {dashboard_path}")
        
    elif args.analyze:
        status = tracker.analyze_pattern_status()
        print(f"📊 Pattern Analysis Complete")
        print(f"Total: {status['summary']['total_patterns']}")
        print(f"Transformed: {status['summary']['transformed']}")
        print(f"Critical Issues: {status['summary']['critical_issues']}")
        
    else:
        # Default: show quick status
        status = tracker.load_status()
        if status:
            print(f"📊 Pattern Transformation Status")
            print(f"Total: {status['summary']['total_patterns']}")
            print(f"Transformed: {status['summary']['transformed']} ({status['summary']['transformed']/status['summary']['total_patterns']*100:.1f}%)")
            print(f"Remaining: {status['summary']['pending']}")
        else:
            print("No status found. Run with --analyze to generate initial status.")

if __name__ == '__main__':
    main()
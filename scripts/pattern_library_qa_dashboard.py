#!/usr/bin/env python3
"""
Pattern Library Quality Assurance Dashboard
Comprehensive health check and validation suite for the pattern library
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import subprocess

class PatternLibraryQADashboard:
    def __init__(self):
        self.base_dir = Path("/home/deepak/DStudio")
        self.pattern_dir = self.base_dir / "docs" / "pattern-library"
        self.scripts_dir = self.base_dir / "scripts"
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.results = {}
        
    def run_pattern_count_audit(self) -> Dict:
        """Run pattern count audit"""
        print("📊 Running pattern count audit...")
        try:
            result = subprocess.run(
                ["python3", str(self.scripts_dir / "count_patterns.py")],
                capture_output=True,
                text=True,
                cwd=str(self.base_dir)
            )
            
            # Load the audit results
            audit_file = self.base_dir / "pattern_count_audit.json"
            if audit_file.exists():
                with open(audit_file, 'r') as f:
                    audit_data = json.load(f)
                    return {
                        'status': 'success',
                        'total_patterns': audit_data['total'],
                        'categories': audit_data['categories'],
                        'timestamp': self.timestamp
                    }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
            
        return {'status': 'not_found'}
        
    def check_metadata_compliance(self) -> Dict:
        """Check metadata compliance across patterns"""
        print("🔍 Checking metadata compliance...")
        
        required_fields = [
            'title', 'description', 'category', 'excellence_tier',
            'pattern_status', 'essential_question', 'tagline'
        ]
        
        compliant = 0
        non_compliant = []
        total = 0
        
        for pattern_file in self.pattern_dir.rglob("*.md"):
            if pattern_file.name == "index.md":
                continue
                
            total += 1
            with open(pattern_file, 'r') as f:
                content = f.read()
                
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    import yaml
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        missing = [f for f in required_fields if f not in frontmatter]
                        if not missing:
                            compliant += 1
                        else:
                            non_compliant.append({
                                'file': pattern_file.name,
                                'missing_fields': missing
                            })
                    except:
                        non_compliant.append({
                            'file': pattern_file.name,
                            'error': 'Invalid YAML'
                        })
                        
        return {
            'total_patterns': total,
            'compliant': compliant,
            'non_compliant_count': len(non_compliant),
            'compliance_rate': f"{(compliant/total*100):.1f}%" if total > 0 else "0%",
            'non_compliant_files': non_compliant[:5]  # Show first 5
        }
        
    def validate_links(self) -> Dict:
        """Validate internal links"""
        print("🔗 Validating internal links...")
        
        broken_links = 0
        total_links = 0
        link_issues = []
        
        for pattern_file in self.pattern_dir.rglob("*.md"):
            with open(pattern_file, 'r') as f:
                content = f.read()
                
            # Extract markdown links
            import re
            links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
            
            for link_text, link_url in links:
                total_links += 1
                
                # Check internal links only
                if not link_url.startswith('http'):
                    # Resolve relative path
                    if link_url.startswith('../'):
                        target = pattern_file.parent.parent / link_url[3:]
                    elif link_url.startswith('./'):
                        target = pattern_file.parent / link_url[2:]
                    elif link_url.startswith('/'):
                        target = self.base_dir / link_url[1:]
                    else:
                        target = pattern_file.parent / link_url
                        
                    # Remove anchors
                    if '#' in str(target):
                        target = Path(str(target).split('#')[0])
                        
                    if not target.exists():
                        broken_links += 1
                        link_issues.append({
                            'file': pattern_file.name,
                            'broken_link': link_url
                        })
                        
        return {
            'total_links': total_links,
            'broken_links': broken_links,
            'health_score': f"{((total_links-broken_links)/total_links*100):.1f}%" if total_links > 0 else "100%",
            'sample_issues': link_issues[:5]
        }
        
    def check_duplicate_patterns(self) -> Dict:
        """Check for potential duplicate patterns"""
        print("🔄 Checking for duplicate patterns...")
        
        pattern_names = {}
        duplicates = []
        
        for pattern_file in self.pattern_dir.rglob("*.md"):
            if pattern_file.name == "index.md":
                continue
                
            # Check for similar names
            base_name = pattern_file.stem.lower().replace('-', '').replace('_', '')
            
            if base_name in pattern_names:
                duplicates.append({
                    'file1': pattern_names[base_name],
                    'file2': str(pattern_file.relative_to(self.pattern_dir))
                })
            else:
                pattern_names[base_name] = str(pattern_file.relative_to(self.pattern_dir))
                
        return {
            'total_patterns': len(pattern_names),
            'duplicates_found': len(duplicates),
            'duplicate_pairs': duplicates
        }
        
    def analyze_pattern_connectivity(self) -> Dict:
        """Analyze pattern connectivity and relationships"""
        print("🕸️ Analyzing pattern connectivity...")
        
        try:
            # Load dependency analysis if it exists
            dep_file = self.base_dir / "pattern_dependency_analysis.json"
            if dep_file.exists():
                with open(dep_file, 'r') as f:
                    dep_data = json.load(f)
                    
                return {
                    'total_patterns': dep_data['statistics']['total_patterns'],
                    'relationships': dep_data['statistics']['total_relationships'],
                    'isolated_patterns': dep_data['statistics']['isolated_patterns'],
                    'avg_connections': dep_data['statistics']['average_connections'],
                    'top_hubs': dep_data['hub_patterns'][:3]
                }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
            
        return {'status': 'not_analyzed'}
        
    def check_search_index(self) -> Dict:
        """Check search index status"""
        print("🔍 Checking search index...")
        
        index_dir = self.base_dir / "search_index"
        if not index_dir.exists():
            return {'status': 'not_built'}
            
        try:
            patterns_file = index_dir / "patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns = json.load(f)
                    
                return {
                    'status': 'ready',
                    'indexed_patterns': len(patterns),
                    'last_updated': datetime.fromtimestamp(
                        patterns_file.stat().st_mtime
                    ).strftime("%Y-%m-%d %H:%M:%S")
                }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
            
        return {'status': 'incomplete'}
        
    def check_category_consistency(self) -> Dict:
        """Check category consistency across patterns"""
        print("📁 Checking category consistency...")
        
        issues = []
        correct = 0
        total = 0
        
        for category_dir in self.pattern_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name in ['visual-assets', 'images']:
                continue
                
            for pattern_file in category_dir.glob("*.md"):
                if pattern_file.name == "index.md":
                    continue
                    
                total += 1
                with open(pattern_file, 'r') as f:
                    content = f.read()
                    
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        import yaml
                        try:
                            frontmatter = yaml.safe_load(parts[1]) or {}
                            if 'category' in frontmatter:
                                if frontmatter['category'] == category_dir.name:
                                    correct += 1
                                else:
                                    issues.append({
                                        'file': pattern_file.name,
                                        'expected': category_dir.name,
                                        'found': frontmatter['category']
                                    })
                        except:
                            pass
                            
        return {
            'total_checked': total,
            'correct': correct,
            'issues': len(issues),
            'consistency_rate': f"{(correct/total*100):.1f}%" if total > 0 else "0%",
            'sample_issues': issues[:5]
        }
        
    def generate_health_score(self, metrics: Dict) -> float:
        """Calculate overall health score"""
        scores = []
        
        # Metadata compliance
        if 'metadata' in metrics:
            compliance = float(metrics['metadata']['compliance_rate'].rstrip('%'))
            scores.append(compliance)
            
        # Link health
        if 'links' in metrics:
            health = float(metrics['links']['health_score'].rstrip('%'))
            scores.append(health)
            
        # Category consistency
        if 'categories' in metrics:
            consistency = float(metrics['categories']['consistency_rate'].rstrip('%'))
            scores.append(consistency)
            
        # Connectivity (inverse of isolation)
        if 'connectivity' in metrics and metrics['connectivity'].get('status') != 'error':
            total = metrics['connectivity'].get('total_patterns', 0)
            isolated = metrics['connectivity'].get('isolated_patterns', 0)
            if total > 0:
                connected_rate = ((total - isolated) / total) * 100
                scores.append(connected_rate)
                
        return sum(scores) / len(scores) if scores else 0
        
    def generate_dashboard_report(self) -> str:
        """Generate comprehensive dashboard report"""
        
        # Run all checks
        metrics = {
            'pattern_count': self.run_pattern_count_audit(),
            'metadata': self.check_metadata_compliance(),
            'links': self.validate_links(),
            'duplicates': self.check_duplicate_patterns(),
            'connectivity': self.analyze_pattern_connectivity(),
            'search': self.check_search_index(),
            'categories': self.check_category_consistency()
        }
        
        health_score = self.generate_health_score(metrics)
        
        # Generate report
        report = f"""# 📊 Pattern Library Quality Assurance Dashboard
Generated: {self.timestamp}

## 🏥 Overall Health Score: {health_score:.1f}%

{self._get_health_badge(health_score)}

## 📈 Key Metrics

### Pattern Count
- **Total Patterns**: {metrics['pattern_count'].get('total_patterns', 'Unknown')}
- **Categories**: {len(metrics['pattern_count'].get('categories', {}))}
"""
        
        if metrics['pattern_count'].get('categories'):
            report += "\n**Distribution:**\n"
            for cat, info in sorted(metrics['pattern_count']['categories'].items(), 
                                   key=lambda x: x[1]['count'], reverse=True)[:5]:
                report += f"- {cat}: {info['count']} patterns\n"
                
        report += f"""
### Metadata Compliance
- **Compliance Rate**: {metrics['metadata']['compliance_rate']}
- **Compliant Patterns**: {metrics['metadata']['compliant']}/{metrics['metadata']['total_patterns']}
- **Issues Found**: {metrics['metadata']['non_compliant_count']}

### Link Validation
- **Health Score**: {metrics['links']['health_score']}
- **Total Links**: {metrics['links']['total_links']}
- **Broken Links**: {metrics['links']['broken_links']}

### Duplicate Detection
- **Unique Patterns**: {metrics['duplicates']['total_patterns']}
- **Duplicates Found**: {metrics['duplicates']['duplicates_found']}

### Pattern Connectivity
"""
        
        if metrics['connectivity'].get('status') != 'error':
            report += f"""- **Total Relationships**: {metrics['connectivity'].get('relationships', 'Unknown')}
- **Isolated Patterns**: {metrics['connectivity'].get('isolated_patterns', 'Unknown')}
- **Average Connections**: {metrics['connectivity'].get('avg_connections', 'Unknown')}
"""
        else:
            report += "- Status: Not analyzed (run dependency analyzer)\n"
            
        report += f"""
### Search Index
- **Status**: {metrics['search'].get('status', 'Unknown')}
"""
        
        if metrics['search'].get('status') == 'ready':
            report += f"""- **Indexed Patterns**: {metrics['search']['indexed_patterns']}
- **Last Updated**: {metrics['search']['last_updated']}
"""
            
        report += f"""
### Category Consistency
- **Consistency Rate**: {metrics['categories']['consistency_rate']}
- **Correct Categorization**: {metrics['categories']['correct']}/{metrics['categories']['total_checked']}
- **Issues Found**: {metrics['categories']['issues']}

## 🚨 Action Items
"""
        
        # Generate action items based on metrics
        actions = []
        
        if metrics['metadata']['non_compliant_count'] > 0:
            actions.append(f"Fix metadata for {metrics['metadata']['non_compliant_count']} patterns")
            
        if metrics['links']['broken_links'] > 0:
            actions.append(f"Fix {metrics['links']['broken_links']} broken links")
            
        if metrics['duplicates']['duplicates_found'] > 0:
            actions.append(f"Review {metrics['duplicates']['duplicates_found']} potential duplicate patterns")
            
        if metrics['connectivity'].get('isolated_patterns', 0) > 50:
            actions.append("Add relationships to isolated patterns")
            
        if metrics['search'].get('status') != 'ready':
            actions.append("Build or update search index")
            
        if metrics['categories']['issues'] > 0:
            actions.append(f"Fix category metadata for {metrics['categories']['issues']} patterns")
            
        if actions:
            for i, action in enumerate(actions, 1):
                report += f"{i}. {action}\n"
        else:
            report += "✅ No critical issues found!\n"
            
        report += """
## 🛠️ Quick Commands

```bash
# Run full QA suite
python3 scripts/pattern_library_qa_dashboard.py

# Fix metadata issues
python3 scripts/standardize_pattern_metadata.py

# Validate and fix links
python3 scripts/validate_pattern_links.py

# Build search index
python3 scripts/build_pattern_search_index.py

# Analyze dependencies
python3 scripts/pattern_dependency_analyzer.py
```

## 📊 Trend Analysis

Monitor these metrics weekly:
- Pattern count growth
- Metadata compliance rate
- Link health score
- Search index freshness
- Pattern connectivity

---
*Dashboard powered by Pattern Library QA Suite v1.0*
"""
        
        return report
        
    def _get_health_badge(self, score: float) -> str:
        """Get health badge based on score"""
        if score >= 90:
            return "🟢 **Excellent** - Pattern library is in great shape!"
        elif score >= 75:
            return "🟡 **Good** - Minor improvements needed"
        elif score >= 60:
            return "🟠 **Fair** - Several areas need attention"
        else:
            return "🔴 **Needs Attention** - Critical issues to address"
            
    def save_metrics(self, metrics: Dict):
        """Save metrics for trend analysis"""
        metrics_file = self.base_dir / "qa_metrics_history.json"
        
        history = []
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                history = json.load(f)
                
        history.append({
            'timestamp': self.timestamp,
            'metrics': metrics,
            'health_score': self.generate_health_score(metrics)
        })
        
        # Keep last 30 entries
        history = history[-30:]
        
        with open(metrics_file, 'w') as f:
            json.dump(history, f, indent=2)
            
    def run(self):
        """Run the QA dashboard"""
        print("=" * 60)
        print("🚀 Pattern Library QA Dashboard")
        print("=" * 60)
        
        # Generate report
        report = self.generate_dashboard_report()
        
        # Save report
        report_file = self.base_dir / "PATTERN_LIBRARY_QA_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)
            
        print(f"\n✅ Report saved to: {report_file}")
        
        # Display summary
        print("\n" + "=" * 60)
        lines = report.split('\n')
        for line in lines[:20]:  # Show first 20 lines
            print(line)
        print("...")
        print("\n📄 See full report in PATTERN_LIBRARY_QA_REPORT.md")

def main():
    dashboard = PatternLibraryQADashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
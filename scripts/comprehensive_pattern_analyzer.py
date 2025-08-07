#!/usr/bin/env python3
"""
Comprehensive Pattern File Analysis Tool

This script provides multiple analysis approaches:
1. Backup directory comparison (if available)
2. Git history comparison (fallback)
3. Content quality assessment
4. Priority-based review recommendations

Usage:
    python comprehensive_pattern_analyzer.py [options]
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from collections import defaultdict
import argparse
from datetime import datetime
import re

class ComprehensivePatternAnalyzer:
    def __init__(self, repo_root="/home/deepak/DStudio"):
        self.repo_root = Path(repo_root)
        self.pattern_dir = self.repo_root / "docs" / "pattern-library"
        
    def detect_analysis_method(self, backup_path=None):
        """Detect the best analysis method available"""
        methods = {
            'backup_comparison': False,
            'git_comparison': False,
            'content_analysis': False
        }
        
        # Check for backup directory
        if backup_path and Path(backup_path).exists():
            methods['backup_comparison'] = True
        else:
            # Auto-detect backup directories
            for pattern in ["*backup*", "*_backup_*", "pattern_backup*"]:
                if list(self.repo_root.glob(pattern)):
                    methods['backup_comparison'] = True
                    break
        
        # Check for git availability
        try:
            subprocess.run(['git', 'status'], cwd=self.repo_root, 
                         capture_output=True, check=True)
            methods['git_comparison'] = True
        except:
            pass
        
        # Content analysis always available
        methods['content_analysis'] = True
        
        return methods
    
    def analyze_content_quality(self):
        """Analyze content quality and completeness of pattern files"""
        results = []
        
        if not self.pattern_dir.exists():
            return results
        
        # Define expected sections in pattern files
        expected_sections = [
            'overview', 'problem', 'solution', 'implementation',
            'example', 'benefits', 'drawbacks', 'considerations',
            'related patterns', 'references'
        ]
        
        for file_path in self.pattern_dir.rglob('*.md'):
            if file_path.name.startswith('index'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic metrics
                lines = content.split('\n')
                word_count = len(content.split())
                char_count = len(content)
                
                # Section analysis
                content_lower = content.lower()
                sections_found = []
                for section in expected_sections:
                    if f'# {section}' in content_lower or f'## {section}' in content_lower:
                        sections_found.append(section)
                
                # Code block analysis
                code_blocks = content.count('```')
                diagrams = content.count('mermaid') + content.count('.mmd')
                
                # Relative path for reporting
                relative_path = file_path.relative_to(self.pattern_dir)
                
                # Quality score calculation
                quality_score = self._calculate_quality_score(
                    word_count, len(sections_found), code_blocks, diagrams
                )
                
                results.append({
                    'file_path': str(relative_path),
                    'filename': file_path.name,
                    'category': str(relative_path.parts[0]) if relative_path.parts else 'root',
                    'size_bytes': char_count,
                    'line_count': len(lines),
                    'word_count': word_count,
                    'sections_found': len(sections_found),
                    'sections_missing': len(expected_sections) - len(sections_found),
                    'code_blocks': code_blocks,
                    'diagrams': diagrams,
                    'quality_score': quality_score,
                    'quality_rating': self._get_quality_rating(quality_score)
                })
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        return sorted(results, key=lambda x: x['quality_score'], reverse=True)
    
    def _calculate_quality_score(self, word_count, sections, code_blocks, diagrams):
        """Calculate quality score based on content metrics"""
        score = 0
        
        # Word count scoring (target: 1000-3000 words)
        if 1000 <= word_count <= 3000:
            score += 40
        elif 500 <= word_count < 1000:
            score += 30
        elif word_count >= 3000:
            score += 35
        else:
            score += 10
        
        # Section completeness (out of 30 points)
        score += min(30, sections * 3)
        
        # Code examples (out of 20 points)
        score += min(20, code_blocks * 5)
        
        # Diagrams/visuals (out of 10 points)
        score += min(10, diagrams * 5)
        
        return score
    
    def _get_quality_rating(self, score):
        """Convert quality score to rating"""
        if score >= 85:
            return "EXCELLENT"
        elif score >= 70:
            return "GOOD"
        elif score >= 55:
            return "FAIR"
        elif score >= 40:
            return "POOR"
        else:
            return "INCOMPLETE"
    
    def get_git_size_comparison(self, commit_ref="HEAD~5"):
        """Get size comparison using git history"""
        try:
            # Import the existing analyzer
            sys.path.append(str(self.repo_root / "scripts"))
            from pattern_file_size_analyzer import PatternFileSizeAnalyzer
            
            analyzer = PatternFileSizeAnalyzer(str(self.repo_root), commit_ref)
            results, categories = analyzer.analyze_size_changes()
            return results
        except ImportError:
            return self._basic_git_comparison(commit_ref)
    
    def _basic_git_comparison(self, commit_ref):
        """Basic git-based size comparison"""
        results = []
        
        try:
            # Get list of pattern files that changed
            cmd = ["git", "diff", "--name-only", commit_ref, "HEAD", "--", "docs/pattern-library/"]
            result = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                changed_files = [f.strip() for f in result.stdout.split('\n') if f.strip().endswith('.md')]
                
                for file_path in changed_files:
                    full_path = self.repo_root / file_path
                    if full_path.exists() and not full_path.name.startswith('index'):
                        current_size = full_path.stat().st_size
                        # Simple analysis - just mark as changed
                        results.append({
                            'file_path': file_path,
                            'current_size': current_size,
                            'status': 'modified',
                            'priority': 'REVIEW'
                        })
            
        except Exception as e:
            print(f"Git comparison error: {e}")
        
        return results
    
    def generate_comprehensive_report(self, output_file="comprehensive_pattern_analysis.md"):
        """Generate comprehensive analysis report"""
        print("Generating Comprehensive Pattern Analysis...")
        print("=" * 60)
        
        # Detect available analysis methods
        methods = self.detect_analysis_method()
        print("Available analysis methods:")
        for method, available in methods.items():
            status = "✓" if available else "✗"
            print(f"  {status} {method.replace('_', ' ').title()}")
        print()
        
        report = []
        
        # Header
        report.append("# Comprehensive Pattern Library Analysis")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Repository:** {self.repo_root}")
        report.append("")
        
        # Analysis methods used
        report.append("## Analysis Methods Applied")
        for method, available in methods.items():
            status = "Used" if available else "Not Available"
            report.append(f"- **{method.replace('_', ' ').title()}:** {status}")
        report.append("")
        
        # Content Quality Analysis
        print("Performing content quality analysis...")
        quality_results = self.analyze_content_quality()
        
        if quality_results:
            report.append("## Content Quality Analysis")
            report.append(f"**Files Analyzed:** {len(quality_results)}")
            report.append("")
            
            # Quality distribution
            quality_dist = defaultdict(int)
            for result in quality_results:
                quality_dist[result['quality_rating']] += 1
            
            report.append("### Quality Distribution")
            for rating in ['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'INCOMPLETE']:
                count = quality_dist.get(rating, 0)
                percentage = (count / len(quality_results)) * 100 if quality_results else 0
                report.append(f"- **{rating}:** {count} files ({percentage:.1f}%)")
            report.append("")
            
            # Top quality files
            report.append("### Top Quality Files")
            report.append("| File | Category | Quality Score | Rating | Word Count | Sections |")
            report.append("|------|----------|---------------|--------|------------|----------|")
            
            for result in quality_results[:10]:
                report.append(
                    f"| `{result['filename']}` | {result['category']} | "
                    f"{result['quality_score']} | {result['quality_rating']} | "
                    f"{result['word_count']} | {result['sections_found']}/10 |"
                )
            report.append("")
            
            # Files needing improvement
            poor_files = [r for r in quality_results if r['quality_rating'] in ['POOR', 'INCOMPLETE']]
            if poor_files:
                report.append("### Files Needing Content Improvement")
                report.append("| File | Category | Issues | Priority |")
                report.append("|------|----------|--------|----------|")
                
                for result in poor_files:
                    issues = []
                    if result['word_count'] < 500:
                        issues.append("Low word count")
                    if result['sections_missing'] > 5:
                        issues.append("Missing sections")
                    if result['code_blocks'] == 0:
                        issues.append("No code examples")
                    
                    priority = "HIGH" if len(issues) >= 2 else "MEDIUM"
                    report.append(
                        f"| `{result['filename']}` | {result['category']} | "
                        f"{', '.join(issues)} | {priority} |"
                    )
                report.append("")
        
        # Git comparison analysis
        if methods['git_comparison']:
            print("Performing git history analysis...")
            git_results = self.get_git_size_comparison()
            
            if git_results:
                decreased_files = [r for r in git_results if r.get('size_diff', 0) < 0]
                
                if decreased_files:
                    report.append("## Size Change Analysis (Git History)")
                    report.append(f"**Files that decreased in size:** {len(decreased_files)}")
                    report.append("")
                    
                    # Most significant reductions
                    significant_reductions = [r for r in decreased_files 
                                            if abs(r.get('size_diff', 0)) > 100]
                    
                    if significant_reductions:
                        report.append("### Significant Size Reductions")
                        report.append("| File | Size Change | Priority |")
                        report.append("|------|-------------|----------|")
                        
                        for result in sorted(significant_reductions, 
                                           key=lambda x: x.get('size_diff', 0))[:10]:
                            report.append(
                                f"| `{result['file_path']}` | "
                                f"{result.get('size_diff', 0)} bytes | "
                                f"{result.get('priority', 'MEDIUM')} |"
                            )
                        report.append("")
        
        # Combined recommendations
        report.append("## Priority Review Recommendations")
        report.append("")
        
        # High priority files (combining all analyses)
        high_priority_files = set()
        
        if quality_results:
            high_priority_files.update([
                r['filename'] for r in quality_results 
                if r['quality_rating'] in ['POOR', 'INCOMPLETE']
            ])
        
        if methods['git_comparison']:
            git_results = self.get_git_size_comparison()
            if git_results:
                high_priority_files.update([
                    Path(r['file_path']).name for r in git_results
                    if r.get('priority') in ['CRITICAL', 'HIGH'] or abs(r.get('size_diff', 0)) > 200
                ])
        
        if high_priority_files:
            report.append("### Files Requiring Immediate Review")
            for filename in sorted(high_priority_files):
                report.append(f"- `{filename}`")
            report.append("")
        
        report.append("### Review Actions")
        report.append("1. **Content Quality**: Focus on POOR/INCOMPLETE rated files")
        report.append("2. **Size Changes**: Verify files with significant size reductions")
        report.append("3. **Template Compliance**: Ensure all patterns follow standard structure")
        report.append("4. **Technical Accuracy**: Validate implementation examples and diagrams")
        report.append("")
        
        report.append("### Automated Checks")
        report.append("```bash")
        report.append("# Check file sizes")
        report.append("find docs/pattern-library -name '*.md' -exec wc -c {} + | sort -n")
        report.append("")
        report.append("# Check for missing sections")
        report.append("grep -L '## Implementation' docs/pattern-library/**/*.md")
        report.append("")
        report.append("# Validate markdown syntax")
        report.append("markdownlint docs/pattern-library/")
        report.append("```")
        report.append("")
        
        # Save report
        output_path = self.repo_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"Comprehensive analysis complete!")
        print(f"Report saved to: {output_path}")
        
        # Summary statistics
        if quality_results:
            avg_quality = sum(r['quality_score'] for r in quality_results) / len(quality_results)
            print(f"\nQuality Summary:")
            print(f"  Average quality score: {avg_quality:.1f}/100")
            print(f"  Files analyzed: {len(quality_results)}")
            print(f"  High-priority reviews needed: {len(high_priority_files)}")
        
        return output_path

def main():
    parser = argparse.ArgumentParser(description='Comprehensive pattern file analysis')
    parser.add_argument('--backup-path', 
                       help='Path to backup directory (optional)')
    parser.add_argument('--output', default='comprehensive_pattern_analysis.md',
                       help='Output report file name')
    parser.add_argument('--repo-root', default='/home/deepak/DStudio',
                       help='Repository root path')
    
    args = parser.parse_args()
    
    analyzer = ComprehensivePatternAnalyzer(args.repo_root)
    analyzer.generate_comprehensive_report(args.output)

if __name__ == "__main__":
    main()
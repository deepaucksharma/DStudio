#!/usr/bin/env python3
"""
Pattern File Size Analysis Tool

This script compares pattern files between current state and git history
to identify files that have decreased in size, indicating potential content loss.

Usage:
    python pattern_file_size_analyzer.py [--commit-ref HEAD~1] [--output analysis_report.md]
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from collections import defaultdict
import argparse
from datetime import datetime

class PatternFileSizeAnalyzer:
    def __init__(self, repo_root="/home/deepak/DStudio", commit_ref="HEAD~5"):
        self.repo_root = Path(repo_root)
        self.commit_ref = commit_ref
        self.pattern_dir = self.repo_root / "docs" / "pattern-library"
        
    def get_current_pattern_files(self):
        """Get all current .md pattern files (excluding index files)"""
        pattern_files = []
        
        if not self.pattern_dir.exists():
            print(f"Pattern directory not found: {self.pattern_dir}")
            return pattern_files
            
        for root, dirs, files in os.walk(self.pattern_dir):
            for file in files:
                if file.endswith('.md') and not file.startswith('index'):
                    relative_path = Path(root) / file
                    pattern_files.append(relative_path)
        
        return sorted(pattern_files)
    
    def get_file_size(self, file_path):
        """Get current file size in bytes"""
        try:
            return file_path.stat().st_size
        except FileNotFoundError:
            return 0
    
    def get_git_file_size(self, relative_path, commit_ref):
        """Get file size from git at specific commit"""
        try:
            # Get relative path from repo root
            rel_path = relative_path.relative_to(self.repo_root)
            
            # Use git show to get file content at specific commit
            cmd = ["git", "show", f"{commit_ref}:{rel_path}"]
            result = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                return len(result.stdout.encode('utf-8'))
            else:
                return None
        except Exception as e:
            print(f"Error getting git file size for {relative_path}: {e}")
            return None
    
    def get_available_commits(self, max_commits=10):
        """Get list of recent commits for reference"""
        try:
            cmd = ["git", "log", "--oneline", f"-{max_commits}"]
            result = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        commit_hash = line.split()[0]
                        commit_msg = ' '.join(line.split()[1:])
                        commits.append({'hash': commit_hash, 'message': commit_msg})
                return commits
            return []
        except Exception as e:
            print(f"Error getting git commits: {e}")
            return []
    
    def categorize_files(self):
        """Categorize pattern files by type/domain"""
        categories = defaultdict(list)
        
        current_files = self.get_current_pattern_files()
        
        for file_path in current_files:
            # Extract category from path
            parts = file_path.parts
            pattern_lib_idx = None
            for i, part in enumerate(parts):
                if part == 'pattern-library':
                    pattern_lib_idx = i
                    break
            
            if pattern_lib_idx is not None and len(parts) > pattern_lib_idx + 1:
                category = parts[pattern_lib_idx + 1]
                categories[category].append(file_path)
        
        return categories
    
    def analyze_size_changes(self):
        """Main analysis function"""
        print("Starting Pattern File Size Analysis...")
        print("=" * 60)
        
        # Get available commits for reference
        commits = self.get_available_commits()
        print(f"Available recent commits:")
        for i, commit in enumerate(commits[:5]):
            print(f"  {i}: {commit['hash']} - {commit['message']}")
        print()
        
        # Get current pattern files
        current_files = self.get_current_pattern_files()
        print(f"Found {len(current_files)} pattern files to analyze")
        
        # Analyze each file
        results = []
        categories = self.categorize_files()
        
        for file_path in current_files:
            current_size = self.get_file_size(file_path)
            git_size = self.get_git_file_size(file_path, self.commit_ref)
            
            if git_size is not None:
                size_diff = current_size - git_size
                if git_size > 0:
                    percent_change = (size_diff / git_size) * 100
                else:
                    percent_change = 100.0 if current_size > 0 else 0.0
                
                # Extract category and filename
                parts = file_path.parts
                category = "unknown"
                for i, part in enumerate(parts):
                    if part == 'pattern-library' and len(parts) > i + 1:
                        category = parts[i + 1]
                        break
                
                filename = file_path.name
                relative_path = file_path.relative_to(self.repo_root)
                
                results.append({
                    'file_path': str(relative_path),
                    'category': category,
                    'filename': filename,
                    'current_size': current_size,
                    'previous_size': git_size,
                    'size_diff': size_diff,
                    'percent_change': percent_change,
                    'priority': self._calculate_priority(size_diff, percent_change, current_size)
                })
        
        # Sort by size reduction (most concerning first)
        results.sort(key=lambda x: x['size_diff'])
        
        return results, categories
    
    def _calculate_priority(self, size_diff, percent_change, current_size):
        """Calculate review priority based on size change metrics"""
        if size_diff >= 0:
            return "LOW"  # File grew or stayed same
        
        # File decreased in size
        abs_reduction = abs(size_diff)
        abs_percent_change = abs(percent_change)
        
        if abs_reduction > 5000 or abs_percent_change > 50:
            return "CRITICAL"
        elif abs_reduction > 2000 or abs_percent_change > 25:
            return "HIGH" 
        elif abs_reduction > 500 or abs_percent_change > 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_report(self, results, categories, output_file="pattern_size_analysis.md"):
        """Generate comprehensive analysis report"""
        report = []
        
        # Header
        report.append("# Pattern File Size Analysis Report")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Comparison Reference:** {self.commit_ref}")
        report.append(f"**Total Files Analyzed:** {len(results)}")
        report.append("")
        
        # Executive Summary
        decreased_files = [r for r in results if r['size_diff'] < 0]
        critical_files = [r for r in decreased_files if r['priority'] == 'CRITICAL']
        high_files = [r for r in decreased_files if r['priority'] == 'HIGH']
        
        report.append("## Executive Summary")
        report.append(f"- **Files that decreased in size:** {len(decreased_files)}")
        report.append(f"- **Critical priority files:** {len(critical_files)}")
        report.append(f"- **High priority files:** {len(high_files)}")
        report.append(f"- **Total size reduction:** {sum(abs(r['size_diff']) for r in decreased_files):,} bytes")
        report.append("")
        
        # Priority Section - Files Needing Review
        report.append("## Files Requiring Immediate Review")
        report.append("")
        
        priority_files = [r for r in results if r['size_diff'] < 0 and r['priority'] in ['CRITICAL', 'HIGH']]
        
        if priority_files:
            report.append("| Priority | File | Category | Size Reduction | % Change | Current Size |")
            report.append("|----------|------|----------|----------------|----------|--------------|")
            
            for result in priority_files:
                report.append(
                    f"| {result['priority']} | `{result['file_path']}` | {result['category']} | "
                    f"{abs(result['size_diff']):,} bytes | {result['percent_change']:.1f}% | "
                    f"{result['current_size']:,} bytes |"
                )
        else:
            report.append("*No files require immediate review.*")
        
        report.append("")
        
        # Detailed Analysis by Category
        report.append("## Analysis by Category")
        report.append("")
        
        for category, files in categories.items():
            category_results = [r for r in results if r['category'] == category]
            decreased_in_category = [r for r in category_results if r['size_diff'] < 0]
            
            report.append(f"### {category.title()} ({len(category_results)} files)")
            
            if decreased_in_category:
                report.append(f"**Files with size reduction:** {len(decreased_in_category)}")
                report.append("")
                report.append("| File | Size Change | % Change | Priority |")
                report.append("|------|-------------|----------|----------|")
                
                for result in sorted(decreased_in_category, key=lambda x: x['size_diff']):
                    report.append(
                        f"| `{result['filename']}` | {result['size_diff']:,} bytes | "
                        f"{result['percent_change']:.1f}% | {result['priority']} |"
                    )
            else:
                report.append("*No files decreased in size.*")
            
            report.append("")
        
        # Complete File List
        report.append("## Complete Analysis Results")
        report.append("")
        report.append("| File Path | Category | Current Size | Previous Size | Size Change | % Change | Priority |")
        report.append("|-----------|----------|--------------|---------------|-------------|----------|----------|")
        
        for result in results:
            report.append(
                f"| `{result['file_path']}` | {result['category']} | {result['current_size']:,} | "
                f"{result['previous_size']:,} | {result['size_diff']:,} | {result['percent_change']:.1f}% | {result['priority']} |"
            )
        
        report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        report.append("1. **Immediately review CRITICAL priority files** - likely significant content loss")
        report.append("2. **Review HIGH priority files** - potential content reduction")
        report.append("3. **Consider git diff analysis** for detailed change investigation:")
        report.append(f"   ```bash")
        report.append(f"   git diff {self.commit_ref} -- docs/pattern-library/")
        report.append(f"   ```")
        report.append("4. **Verify content completeness** for files showing major reductions")
        report.append("5. **Check for missing sections** in pattern templates")
        report.append("")
        
        # Save report
        output_path = self.repo_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"Analysis complete! Report saved to: {output_path}")
        return output_path

def main():
    parser = argparse.ArgumentParser(description='Analyze pattern file size changes')
    parser.add_argument('--commit-ref', default='HEAD~5', 
                       help='Git commit reference for comparison (default: HEAD~5)')
    parser.add_argument('--output', default='pattern_size_analysis.md',
                       help='Output file name (default: pattern_size_analysis.md)')
    parser.add_argument('--repo-root', default='/home/deepak/DStudio',
                       help='Repository root path')
    
    args = parser.parse_args()
    
    analyzer = PatternFileSizeAnalyzer(args.repo_root, args.commit_ref)
    results, categories = analyzer.analyze_size_changes()
    
    if results:
        analyzer.generate_report(results, categories, args.output)
        
        # Print summary to console
        decreased_files = [r for r in results if r['size_diff'] < 0]
        critical_files = [r for r in decreased_files if r['priority'] == 'CRITICAL']
        
        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        print(f"Files analyzed: {len(results)}")
        print(f"Files decreased in size: {len(decreased_files)}")
        print(f"Critical priority files: {len(critical_files)}")
        
        if critical_files:
            print("\nCRITICAL FILES NEEDING REVIEW:")
            for cf in critical_files:
                print(f"  - {cf['file_path']} ({cf['size_diff']} bytes, {cf['percent_change']:.1f}%)")
    else:
        print("No results to analyze. Check if pattern files exist and git history is available.")

if __name__ == "__main__":
    main()
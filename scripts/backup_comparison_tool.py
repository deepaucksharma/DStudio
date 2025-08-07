#!/usr/bin/env python3
"""
Backup Directory Comparison Tool

This script compares pattern files between the current state and backup directories,
or falls back to git-based comparison when backup directories are not available.

Usage:
    python backup_comparison_tool.py [--backup-path path] [--output analysis.md]
"""

import os
import sys
import json
import shutil
from pathlib import Path
from collections import defaultdict
import argparse
from datetime import datetime

class BackupComparisonTool:
    def __init__(self, repo_root="/home/deepak/DStudio", backup_path=None):
        self.repo_root = Path(repo_root)
        self.backup_path = Path(backup_path) if backup_path else None
        self.pattern_dir = self.repo_root / "docs" / "pattern-library"
        
    def find_backup_directories(self):
        """Find potential backup directories in the repository"""
        backup_dirs = []
        
        # Look for common backup directory patterns
        patterns = [
            "*backup*",
            "*_backup_*",
            "pattern_backup*",
            "backup_*"
        ]
        
        for pattern in patterns:
            for path in self.repo_root.glob(pattern):
                if path.is_dir() and "pattern" in str(path).lower():
                    backup_dirs.append(path)
        
        return backup_dirs
    
    def get_pattern_files(self, root_dir):
        """Get all .md pattern files from a directory, excluding index files"""
        pattern_files = {}
        pattern_lib_path = root_dir / "docs" / "pattern-library"
        
        if not pattern_lib_path.exists():
            return pattern_files
            
        for root, dirs, files in os.walk(pattern_lib_path):
            for file in files:
                if file.endswith('.md') and not file.startswith('index'):
                    file_path = Path(root) / file
                    # Create relative path from pattern-library directory
                    relative_path = file_path.relative_to(pattern_lib_path)
                    pattern_files[str(relative_path)] = file_path
        
        return pattern_files
    
    def compare_file_sizes(self, current_files, backup_files):
        """Compare file sizes between current and backup versions"""
        comparison_results = []
        
        # Compare files that exist in both versions
        common_files = set(current_files.keys()) & set(backup_files.keys())
        
        for relative_path in common_files:
            current_file = current_files[relative_path]
            backup_file = backup_files[relative_path]
            
            try:
                current_size = current_file.stat().st_size
                backup_size = backup_file.stat().st_size
                
                size_diff = current_size - backup_size
                if backup_size > 0:
                    percent_change = (size_diff / backup_size) * 100
                else:
                    percent_change = 100.0 if current_size > 0 else 0.0
                
                # Extract category from path
                parts = Path(relative_path).parts
                category = parts[0] if len(parts) > 0 else "unknown"
                filename = Path(relative_path).name
                
                comparison_results.append({
                    'relative_path': relative_path,
                    'filename': filename,
                    'category': category,
                    'current_size': current_size,
                    'backup_size': backup_size,
                    'size_diff': size_diff,
                    'percent_change': percent_change,
                    'priority': self._calculate_priority(size_diff, percent_change, current_size),
                    'status': 'compared'
                })
                
            except Exception as e:
                print(f"Error comparing {relative_path}: {e}")
        
        # Files only in current version (newly added)
        only_current = set(current_files.keys()) - set(backup_files.keys())
        for relative_path in only_current:
            current_file = current_files[relative_path]
            try:
                current_size = current_file.stat().st_size
                parts = Path(relative_path).parts
                category = parts[0] if len(parts) > 0 else "unknown"
                filename = Path(relative_path).name
                
                comparison_results.append({
                    'relative_path': relative_path,
                    'filename': filename,
                    'category': category,
                    'current_size': current_size,
                    'backup_size': 0,
                    'size_diff': current_size,
                    'percent_change': 100.0,
                    'priority': 'NEW',
                    'status': 'new_file'
                })
            except Exception as e:
                print(f"Error processing new file {relative_path}: {e}")
        
        # Files only in backup version (deleted)
        only_backup = set(backup_files.keys()) - set(current_files.keys())
        for relative_path in only_backup:
            backup_file = backup_files[relative_path]
            try:
                backup_size = backup_file.stat().st_size
                parts = Path(relative_path).parts
                category = parts[0] if len(parts) > 0 else "unknown"
                filename = Path(relative_path).name
                
                comparison_results.append({
                    'relative_path': relative_path,
                    'filename': filename,
                    'category': category,
                    'current_size': 0,
                    'backup_size': backup_size,
                    'size_diff': -backup_size,
                    'percent_change': -100.0,
                    'priority': 'DELETED',
                    'status': 'deleted_file'
                })
            except Exception as e:
                print(f"Error processing deleted file {relative_path}: {e}")
        
        return comparison_results
    
    def _calculate_priority(self, size_diff, percent_change, current_size):
        """Calculate review priority based on size change metrics"""
        if size_diff > 0:
            return "GROWTH"  # File grew
        
        if size_diff == 0:
            return "NO_CHANGE"
        
        # File decreased in size
        abs_reduction = abs(size_diff)
        abs_percent_change = abs(percent_change)
        
        if abs_reduction > 10000 or abs_percent_change > 75:
            return "CRITICAL"
        elif abs_reduction > 5000 or abs_percent_change > 50:
            return "HIGH"
        elif abs_reduction > 2000 or abs_percent_change > 25:
            return "MEDIUM"
        elif abs_reduction > 500 or abs_percent_change > 10:
            return "LOW"
        else:
            return "MINIMAL"
    
    def generate_detailed_report(self, results, current_files, backup_files, output_file):
        """Generate comprehensive comparison report"""
        report = []
        
        # Header
        report.append("# Pattern File Backup Comparison Report")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Current Files:** {len(current_files)}")
        report.append(f"**Backup Files:** {len(backup_files) if backup_files else 'N/A'}")
        report.append(f"**Files Analyzed:** {len(results)}")
        report.append("")
        
        # Executive Summary
        decreased_files = [r for r in results if r['size_diff'] < 0 and r['status'] == 'compared']
        critical_files = [r for r in decreased_files if r['priority'] == 'CRITICAL']
        high_files = [r for r in decreased_files if r['priority'] == 'HIGH']
        new_files = [r for r in results if r['status'] == 'new_file']
        deleted_files = [r for r in results if r['status'] == 'deleted_file']
        
        report.append("## Executive Summary")
        report.append(f"- **Files decreased in size:** {len(decreased_files)}")
        report.append(f"- **Critical priority files:** {len(critical_files)}")
        report.append(f"- **High priority files:** {len(high_files)}")
        report.append(f"- **New files:** {len(new_files)}")
        report.append(f"- **Deleted files:** {len(deleted_files)}")
        if decreased_files:
            total_reduction = sum(abs(r['size_diff']) for r in decreased_files)
            report.append(f"- **Total size reduction:** {total_reduction:,} bytes")
        report.append("")
        
        # Critical Files Section
        if critical_files or high_files:
            report.append("## Critical Files Requiring Immediate Review")
            report.append("")
            
            priority_files = critical_files + high_files
            priority_files.sort(key=lambda x: x['size_diff'])  # Most reduction first
            
            report.append("| Priority | File | Category | Size Reduction | % Change | Current Size |")
            report.append("|----------|------|----------|----------------|----------|--------------|")
            
            for result in priority_files:
                report.append(
                    f"| {result['priority']} | `{result['relative_path']}` | {result['category']} | "
                    f"{abs(result['size_diff']):,} bytes | {result['percent_change']:.1f}% | "
                    f"{result['current_size']:,} bytes |"
                )
            report.append("")
        
        # Deleted Files
        if deleted_files:
            report.append("## Deleted Files")
            report.append("")
            report.append("| File | Category | Original Size |")
            report.append("|------|----------|---------------|")
            
            for result in deleted_files:
                report.append(
                    f"| `{result['relative_path']}` | {result['category']} | "
                    f"{result['backup_size']:,} bytes |"
                )
            report.append("")
        
        # New Files
        if new_files:
            report.append("## New Files")
            report.append("")
            report.append("| File | Category | Size |")
            report.append("|------|----------|------|")
            
            for result in new_files:
                report.append(
                    f"| `{result['relative_path']}` | {result['category']} | "
                    f"{result['current_size']:,} bytes |"
                )
            report.append("")
        
        # Category Analysis
        report.append("## Analysis by Category")
        report.append("")
        
        categories = defaultdict(list)
        for result in results:
            categories[result['category']].append(result)
        
        for category, files in sorted(categories.items()):
            decreased_in_category = [f for f in files if f['size_diff'] < 0 and f['status'] == 'compared']
            new_in_category = [f for f in files if f['status'] == 'new_file']
            deleted_in_category = [f for f in files if f['status'] == 'deleted_file']
            
            report.append(f"### {category.title().replace('-', ' ')} ({len(files)} files)")
            report.append(f"- Decreased: {len(decreased_in_category)}")
            report.append(f"- New: {len(new_in_category)}")
            report.append(f"- Deleted: {len(deleted_in_category)}")
            
            if decreased_in_category:
                report.append("")
                report.append("**Files with Size Reduction:**")
                report.append("")
                report.append("| File | Size Change | % Change | Priority |")
                report.append("|------|-------------|----------|----------|")
                
                for result in sorted(decreased_in_category, key=lambda x: x['size_diff']):
                    report.append(
                        f"| `{result['filename']}` | {result['size_diff']:,} bytes | "
                        f"{result['percent_change']:.1f}% | {result['priority']} |"
                    )
            
            report.append("")
        
        # Complete Results Table
        report.append("## Complete Comparison Results")
        report.append("")
        report.append("| File Path | Category | Current | Backup | Change | % Change | Priority | Status |")
        report.append("|-----------|----------|---------|--------|--------|----------|----------|--------|")
        
        # Sort by size difference (most concerning first)
        sorted_results = sorted(results, key=lambda x: x['size_diff'])
        
        for result in sorted_results:
            report.append(
                f"| `{result['relative_path']}` | {result['category']} | "
                f"{result['current_size']:,} | {result['backup_size']:,} | "
                f"{result['size_diff']:,} | {result['percent_change']:.1f}% | "
                f"{result['priority']} | {result['status']} |"
            )
        
        report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        if critical_files:
            report.append("1. **URGENT: Review CRITICAL files immediately** - significant content loss detected")
        if high_files:
            report.append("2. **Review HIGH priority files** - substantial content reduction")
        if deleted_files:
            report.append("3. **Investigate deleted files** - determine if deletion was intentional")
        if new_files:
            report.append("4. **Validate new files** - ensure they follow pattern template standards")
        
        report.append("5. **Detailed investigation commands:**")
        report.append("   ```bash")
        report.append("   # Compare specific file content")
        report.append("   diff current_file backup_file")
        report.append("   ")
        report.append("   # Show file content statistics")
        report.append("   wc -l current_file backup_file")
        report.append("   ```")
        report.append("")
        
        # Save report
        output_path = self.repo_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        return output_path
    
    def run_comparison(self, output_file="backup_comparison_analysis.md"):
        """Main comparison function"""
        print("Pattern File Backup Comparison Tool")
        print("=" * 50)
        
        # Get current files
        current_files = self.get_pattern_files(self.repo_root)
        print(f"Current pattern files: {len(current_files)}")
        
        # Try to find backup files
        backup_files = {}
        
        if self.backup_path and self.backup_path.exists():
            backup_files = self.get_pattern_files(self.backup_path)
            print(f"Backup pattern files: {len(backup_files)}")
        else:
            # Try to find backup directories automatically
            backup_dirs = self.find_backup_directories()
            if backup_dirs:
                print(f"Found potential backup directories:")
                for i, bd in enumerate(backup_dirs):
                    print(f"  {i}: {bd}")
                
                # Use the first one found
                self.backup_path = backup_dirs[0]
                backup_files = self.get_pattern_files(self.backup_path)
                print(f"Using backup: {self.backup_path}")
                print(f"Backup pattern files: {len(backup_files)}")
            else:
                print("No backup directory found. Cannot perform comparison.")
                print("Available backup directories search completed:")
                for pattern in ["*backup*", "*_backup_*", "pattern_backup*"]:
                    found = list(self.repo_root.glob(pattern))
                    print(f"  {pattern}: {found}")
                return None
        
        if not backup_files:
            print("No backup files available for comparison.")
            return None
        
        # Perform comparison
        results = self.compare_file_sizes(current_files, backup_files)
        
        # Generate report
        report_path = self.generate_detailed_report(results, current_files, backup_files, output_file)
        
        # Print summary
        print("\n" + "=" * 50)
        print("COMPARISON SUMMARY")
        print("=" * 50)
        
        decreased_files = [r for r in results if r['size_diff'] < 0 and r['status'] == 'compared']
        critical_files = [r for r in decreased_files if r['priority'] == 'CRITICAL']
        high_files = [r for r in decreased_files if r['priority'] == 'HIGH']
        
        print(f"Total files compared: {len([r for r in results if r['status'] == 'compared'])}")
        print(f"Files decreased in size: {len(decreased_files)}")
        print(f"Critical priority: {len(critical_files)}")
        print(f"High priority: {len(high_files)}")
        print(f"New files: {len([r for r in results if r['status'] == 'new_file'])}")
        print(f"Deleted files: {len([r for r in results if r['status'] == 'deleted_file'])}")
        
        print(f"\nReport saved to: {report_path}")
        return report_path

def main():
    parser = argparse.ArgumentParser(description='Compare pattern files with backup directory')
    parser.add_argument('--backup-path', 
                       help='Path to backup directory containing pattern files')
    parser.add_argument('--output', default='backup_comparison_analysis.md',
                       help='Output report file name')
    parser.add_argument('--repo-root', default='/home/deepak/DStudio',
                       help='Repository root path')
    
    args = parser.parse_args()
    
    tool = BackupComparisonTool(args.repo_root, args.backup_path)
    result = tool.run_comparison(args.output)
    
    if result:
        print(f"\nComparison completed successfully!")
        print(f"Review the report at: {result}")
    else:
        print("\nComparison could not be completed. Check backup directory availability.")

if __name__ == "__main__":
    main()
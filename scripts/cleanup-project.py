#!/usr/bin/env python3
"""
Comprehensive project cleanup script to remove temporary files, 
reports, and consolidate useful scripts.
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Clean up temporary files, reports, and organize useful scripts"""
    
    root_dir = Path('/home/deepak/DStudio')
    
    # Files and directories to delete
    cleanup_targets = []
    
    # 1. Temporary report files in root
    temp_files_root = [
        'BROKEN_LINKS_REPORT.md',
        'FINAL_LINK_ANALYSIS_REPORT.md', 
        'LINK_FIX_SUMMARY.md',
        'PARALLEL_AGENT_ANALYSIS_REPORT.md',
        'PATTERN_IMPROVEMENTS_SUMMARY.md',
        'FINAL_UI_TRANSFORMATION_SUMMARY.md',
        'BASE_URL_FIX_REPORT.md',
        'PHASE_1_2_COMPLETION_REPORT.md',
        'PATTERN_IMPROVEMENTS_PHASE3_SUMMARY.md',
        'PATTERN_IMPROVEMENTS_PHASE2_SUMMARY.md', 
        'PHASE_5_UX_ENHANCEMENTS_REPORT.md',
        'mermaid-analysis-report.md',
        'broken_links_report.json',
        'link_report.txt',
        'agent_batches.json',
        'fix_links.py',
        'verify_links.py'
    ]
    
    # 2. Artifacts directory (entire directory)
    artifacts_dir = root_dir / 'artifacts'
    
    # 3. Temporary scripts to remove (keep only essential ones)
    temp_scripts = [
        'scripts/fix-base-url-issues.py',
        'scripts/fix-all-issues-phase1.py',
        'scripts/fix-remaining-links.py',
        'scripts/analyze-broken-links.py',
        'scripts/analyze-pages-for-agents.py',
        'scripts/fix-final-issues.py',
        'scripts/fix-broken-links-comprehensive.py',
        'scripts/fix-final-patterns.py',
        'scripts/fix-broken-links.py',
        'scripts/fix-double-slashes.py',
        'scripts/get-pages-with-issues.py',
        'scripts/verify_material_conversion.py'
    ]
    
    # 4. Build directory
    site_dir = root_dir / 'site'
    
    # 5. Pattern cleanup reports
    pattern_reports = [
        'docs/patterns/CLEANUP_REPORT.md'
    ]
    
    print("🧹 Starting comprehensive project cleanup...")
    
    # Delete temp files in root
    print("\n1. Cleaning up temporary files in root directory...")
    for file in temp_files_root:
        file_path = root_dir / file
        if file_path.exists():
            file_path.unlink()
            print(f"  ❌ Deleted: {file}")
            cleanup_targets.append(file)
    
    # Delete artifacts directory
    print("\n2. Removing artifacts directory...")
    if artifacts_dir.exists():
        shutil.rmtree(artifacts_dir)
        print(f"  ❌ Deleted directory: artifacts/")
        cleanup_targets.append('artifacts/')
    
    # Delete temporary scripts
    print("\n3. Cleaning up temporary scripts...")
    for script in temp_scripts:
        script_path = root_dir / script
        if script_path.exists():
            script_path.unlink()
            print(f"  ❌ Deleted: {script}")
            cleanup_targets.append(script)
    
    # Delete site directory if it exists
    print("\n4. Removing build directory...")
    if site_dir.exists():
        shutil.rmtree(site_dir)
        print(f"  ❌ Deleted directory: site/")
        cleanup_targets.append('site/')
    
    # Delete pattern reports
    print("\n5. Cleaning up pattern reports...")
    for report in pattern_reports:
        report_path = root_dir / report
        if report_path.exists():
            report_path.unlink()
            print(f"  ❌ Deleted: {report}")
            cleanup_targets.append(report)
    
    # Keep essential scripts
    essential_scripts = [
        'scripts/verify-links.py',  # Keep main link verification
        'scripts/cleanup-project.py'  # Keep this script itself
    ]
    
    print("\n6. Essential scripts preserved:")
    for script in essential_scripts:
        script_path = root_dir / script
        if script_path.exists():
            print(f"  ✅ Kept: {script}")
    
    # Clean up empty directories
    print("\n7. Cleaning up empty directories...")
    empty_dirs = []
    for dirpath in root_dir.rglob('*'):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            try:
                dirpath.rmdir()
                empty_dirs.append(str(dirpath.relative_to(root_dir)))
                print(f"  ❌ Removed empty directory: {dirpath.relative_to(root_dir)}")
            except OSError:
                pass  # Directory not empty or permission denied
    
    # Summary
    print(f"\n{'='*60}")
    print("🎉 CLEANUP COMPLETE!")
    print(f"{'='*60}")
    print(f"Files removed: {len(cleanup_targets)}")
    print(f"Empty directories removed: {len(empty_dirs)}")
    
    if cleanup_targets:
        print("\nFiles/directories removed:")
        for target in sorted(cleanup_targets):
            print(f"  - {target}")
    
    print(f"\n📁 Project structure is now clean and organized!")
    
    # Check remaining files
    print(f"\n📊 Remaining project files:")
    important_files = [
        'mkdocs.yml',
        'requirements.txt', 
        'README.md',
        'CLAUDE.md'
    ]
    
    for file in important_files:
        file_path = root_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {file} ({size:,} bytes)")

if __name__ == "__main__":
    cleanup_project()
#!/usr/bin/env python3
"""
Fix metadata issues in case study files that are mislabeled as stubs.
This script implements the Week 1 critical fixes from the comprehensive plan.
"""

import os
import re
from pathlib import Path

def fix_case_study_metadata(file_path, new_status="complete", update_reading_time=True):
    """Fix metadata in a case study file."""
    
    with open(file_path, 'r') as f:
        content = f.read()
        lines = content.splitlines()
    
    # Count actual content lines (excluding frontmatter)
    content_lines = len([l for l in lines if l.strip()])
    
    # Update status
    content = re.sub(r'^status:\s*stub$', f'status: {new_status}', content, flags=re.MULTILINE)
    
    # Update reading time based on actual content
    if update_reading_time:
        # Estimate reading time (250 words per minute, ~10 words per line)
        estimated_minutes = max(15, (content_lines * 10) // 250)
        content = re.sub(r'^reading_time:\s*\d+\s*min$', f'reading_time: {estimated_minutes} min', 
                         content, flags=re.MULTILINE)
    
    # Update excellence tier based on content volume and quality indicators
    if content_lines > 1500:
        excellence_tier = "gold"
    elif content_lines > 1000:
        excellence_tier = "silver"
    else:
        excellence_tier = "bronze"
    
    content = re.sub(r'^excellence_tier:\s*\w+$', f'excellence_tier: {excellence_tier}', 
                     content, flags=re.MULTILINE)
    
    # Write updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    return content_lines, excellence_tier

def main():
    """Fix metadata for identified case study files."""
    
    base_path = Path("/home/deepak/DStudio/docs/architects-handbook/case-studies")
    
    # Files identified as mislabeled
    files_to_fix = [
        ("elite-engineering/netflix-chaos.md", "complete"),
        ("infrastructure/blockchain.md", "complete"),
        ("databases/vault.md", "complete"),
        ("databases/amazon-aurora.md", "complete"),
    ]
    
    print("🔧 Fixing Case Study Metadata Issues")
    print("=" * 50)
    
    for relative_path, new_status in files_to_fix:
        file_path = base_path / relative_path
        
        if not file_path.exists():
            print(f"❌ File not found: {relative_path}")
            continue
        
        try:
            lines, tier = fix_case_study_metadata(file_path, new_status)
            print(f"✅ Fixed: {relative_path}")
            print(f"   - Status: stub → {new_status}")
            print(f"   - Lines: {lines}")
            print(f"   - Tier: {tier}")
        except Exception as e:
            print(f"❌ Error fixing {relative_path}: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Metadata fixes complete!")
    print("\nNext steps:")
    print("1. Review the changes with: git diff")
    print("2. Commit the fixes: git commit -am 'fix: correct case study metadata'")
    print("3. Continue with Week 1 navigation fixes")

if __name__ == "__main__":
    main()
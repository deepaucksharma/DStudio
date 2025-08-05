#!/usr/bin/env python3
"""
Replace Mermaid text blocks in markdown files with rendered picture elements.
Preserves original diagram source as HTML comments for future updates.
"""

import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class MermaidReplacer:
    def __init__(self, picture_elements_path: str = "picture_elements.json"):
        self.picture_elements = self._load_picture_elements(picture_elements_path)
        self.base_path = Path("docs/pattern-library")
        self.backup_dir = Path(f"backups/mermaid_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.processed_files = []
        self.replacement_count = 0
        
    def _load_picture_elements(self, path: str) -> Dict:
        """Load the generated picture elements."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def create_backups(self) -> None:
        """Create backups of all files before modification."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        for md_file in self.base_path.rglob("*.md"):
            if "visual-assets" in str(md_file):
                continue
                
            relative_path = md_file.relative_to(self.base_path)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(md_file, backup_path)
        
        print(f"✅ Created backups in: {self.backup_dir}")
    
    def replace_diagrams_in_file(self, file_path: Path) -> int:
        """Replace Mermaid blocks in a single file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            replacements = 0
            
            # Find all mermaid code blocks
            mermaid_pattern = r'```mermaid\n(.*?)\n```'
            
            def replace_mermaid(match):
                nonlocal replacements
                diagram_content = match.group(1)
                
                # Generate diagram ID (must match the extraction logic)
                import hashlib
                content_hash = hashlib.md5(diagram_content.encode()).hexdigest()[:8]
                relative_path = file_path.relative_to(self.base_path)
                diagram_id = f"{relative_path.stem}-{replacements}-{content_hash}"
                
                if diagram_id in self.picture_elements:
                    replacements += 1
                    
                    # Create replacement with preserved source
                    replacement = [
                        "<!-- MERMAID_SOURCE",
                        "```mermaid",
                        diagram_content,
                        "```",
                        "END_MERMAID_SOURCE -->",
                        "",
                        self.picture_elements[diagram_id]
                    ]
                    
                    return '\n'.join(replacement)
                else:
                    # If no rendered version found, keep original
                    print(f"⚠️  No rendered version found for diagram in {file_path}")
                    return match.group(0)
            
            # Replace all mermaid blocks
            new_content = re.sub(mermaid_pattern, replace_mermaid, content, flags=re.DOTALL)
            
            if new_content != original_content:
                file_path.write_text(new_content, encoding='utf-8')
                self.processed_files.append(file_path)
                self.replacement_count += replacements
                return replacements
            
            return 0
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return 0
    
    def process_all_files(self) -> None:
        """Process all markdown files in the pattern library."""
        total_files = 0
        
        print("🔄 Processing markdown files...")
        
        for md_file in self.base_path.rglob("*.md"):
            if "visual-assets" in str(md_file):
                continue
                
            total_files += 1
            replacements = self.replace_diagrams_in_file(md_file)
            
            if replacements > 0:
                print(f"✅ Replaced {replacements} diagrams in: {md_file.relative_to(self.base_path)}")
        
        print(f"\n📊 Summary:")
        print(f"   - Files processed: {total_files}")
        print(f"   - Files modified: {len(self.processed_files)}")
        print(f"   - Total diagrams replaced: {self.replacement_count}")
    
    def validate_replacements(self) -> None:
        """Validate that replacements were successful."""
        issues = []
        
        for file_path in self.processed_files:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for any remaining mermaid blocks
            if '```mermaid' in content and 'MERMAID_SOURCE' not in content:
                issues.append(f"Unreplaced mermaid block in {file_path}")
            
            # Check for broken picture elements
            if '<picture>' in content:
                picture_count = content.count('<picture>')
                img_count = content.count('<img ')
                if picture_count != img_count:
                    issues.append(f"Mismatched picture/img tags in {file_path}")
        
        if issues:
            print("\n⚠️  Validation issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("\n✅ All replacements validated successfully!")
    
    def generate_report(self) -> str:
        """Generate a replacement report."""
        report = ["# Mermaid Block Replacement Report\n"]
        report.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Backup Location**: {self.backup_dir}\n")
        
        report.append("## Summary\n")
        report.append(f"- **Total Files Processed**: {len(self.processed_files)}")
        report.append(f"- **Total Diagrams Replaced**: {self.replacement_count}")
        report.append(f"- **Average Diagrams per File**: {self.replacement_count / len(self.processed_files):.1f}" 
                     if self.processed_files else "N/A")
        
        report.append("\n## Modified Files\n")
        for file_path in sorted(self.processed_files):
            relative_path = file_path.relative_to(self.base_path)
            report.append(f"- {relative_path}")
        
        report.append("\n## Rollback Instructions\n")
        report.append("To rollback changes, run:")
        report.append(f"```bash")
        report.append(f"cp -r {self.backup_dir}/* docs/pattern-library/")
        report.append(f"```")
        
        return '\n'.join(report)
    
    def create_rollback_script(self) -> None:
        """Create a rollback script for easy restoration."""
        script_content = f"""#!/bin/bash
# Rollback script for Mermaid diagram replacement
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "🔄 Rolling back Mermaid diagram replacements..."
cp -r {self.backup_dir}/* docs/pattern-library/
echo "✅ Rollback complete!"
"""
        
        script_path = Path("rollback_mermaid_changes.sh")
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        
        print(f"✅ Created rollback script: {script_path}")


def main():
    """Main execution function."""
    replacer = MermaidReplacer()
    
    print("📁 Creating backups...")
    replacer.create_backups()
    
    print("\n🔄 Replacing Mermaid blocks with picture elements...")
    replacer.process_all_files()
    
    print("\n✓ Validating replacements...")
    replacer.validate_replacements()
    
    print("\n📝 Generating report...")
    report = replacer.generate_report()
    
    report_path = Path("replacement_report.md")
    report_path.write_text(report)
    print(f"✅ Report saved to: {report_path}")
    
    print("\n🔧 Creating rollback script...")
    replacer.create_rollback_script()
    
    print("\n✅ Replacement process complete!")


if __name__ == "__main__":
    main()
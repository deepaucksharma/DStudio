#!/usr/bin/env python3
"""
Final Pattern Link Cleanup

This script addresses the remaining obvious link issues to get us closer to 90%+ link health.
"""

import os
import re
from pathlib import Path
from typing import Dict, List
import logging
import shutil
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class FinalPatternLinkCleanup:
    def __init__(self, docs_dir: str = "/home/deepak/DStudio/docs"):
        self.docs_dir = Path(docs_dir)
        self.pattern_dir = self.docs_dir / "pattern-library"
        self.fixes_applied = []
        
    def fix_category_index_links(self, file_path: Path, content: str) -> str:
        """Fix the broken category index links."""
        modified = content
        
        # Fix the main pattern library links in category index files
        if str(file_path).endswith('/index.md') and 'pattern-library' in str(file_path):
            # Fix [...md) links (obvious errors)
            modified = re.sub(r'\[([^\]]+)\]\(\.\.\.md\)', r'[\1](../)', modified)
            
            # Fix double .md.md endings
            modified = re.sub(r'\.md\.md\)', r'.md)', modified)
            
            if modified != content:
                self.fixes_applied.append({
                    'file': str(file_path.relative_to(self.docs_dir)),
                    'type': 'category_index_fix'
                })
        
        return modified
    
    def fix_main_index_category_links(self, file_path: Path, content: str) -> str:
        """Fix the main pattern library index category links."""
        if file_path.name == 'index.md' and file_path.parent.name == 'pattern-library':
            # Fix category links that are missing /index.md or have wrong format
            category_fixes = {
                '(communication.md)': '(communication/)',
                '(resilience.md)': '(resilience/)',
                '(data-management.md)': '(data-management/)',
                '(scaling.md)': '(scaling/)',
                '(architecture.md)': '(architecture/)',
                '(coordination.md)': '(coordination/)',
                '(security.md)': '(security/)',
                '(deployment.md)': '(deployment/)',
                '(ml-infrastructure.md)': '(ml-infrastructure/)',
                '(cost-optimization.md)': '(cost-optimization/)',
            }
            
            for wrong, right in category_fixes.items():
                if wrong in content:
                    content = content.replace(wrong, right)
                    self.fixes_applied.append({
                        'file': str(file_path.relative_to(self.docs_dir)),
                        'type': 'main_index_category_fix',
                        'fix': f'{wrong} -> {right}'
                    })
        
        return content
    
    def fix_empty_link_artifacts(self, file_path: Path, content: str) -> str:
        """Fix remaining empty link artifacts."""
        modified = content
        
        # Remove the specific broken artifacts we identified
        artifacts = [
            r"\[h\['metrics'\]\(\)",
            r"\['spec'\]\(\)",
            r"\[0\]\(\)",
        ]
        
        for artifact in artifacts:
            if re.search(artifact, modified):
                modified = re.sub(artifact, '<!-- Removed broken artifact -->', modified)
                self.fixes_applied.append({
                    'file': str(file_path.relative_to(self.docs_dir)),
                    'type': 'empty_artifact_fix'
                })
        
        return modified
    
    def fix_common_wrong_extensions(self, file_path: Path, content: str) -> str:
        """Fix common wrong file extensions."""
        modified = content
        
        # Fix obvious wrong patterns
        wrong_patterns = {
            r'\[(.*?)\]\(([^)]*?)\.md/\)': r'[\1](\2/)',  # .md/ -> /
            r'\[(.*?)\]\(([^)]*?)\.md\.md\)': r'[\1](\2.md)',  # .md.md -> .md
        }
        
        for pattern, replacement in wrong_patterns.items():
            new_content = re.sub(pattern, replacement, modified)
            if new_content != modified:
                modified = new_content
                self.fixes_applied.append({
                    'file': str(file_path.relative_to(self.docs_dir)),
                    'type': 'extension_fix'
                })
        
        return modified
    
    def fix_missing_category_patterns(self, file_path: Path, content: str) -> str:
        """Fix links to patterns that exist but in wrong category."""
        modified = content
        
        # Common patterns that exist but are referenced incorrectly
        pattern_location_fixes = {
            '../scaling/consistent-hashing.md': '../data-management/consistent-hashing.md',
            '../coordination/consistent-hashing.md': '../data-management/consistent-hashing.md',
            '../data/consistent-hashing.md': '../data-management/consistent-hashing.md',
        }
        
        for wrong, right in pattern_location_fixes.items():
            if wrong in modified:
                modified = modified.replace(wrong, right)
                self.fixes_applied.append({
                    'file': str(file_path.relative_to(self.docs_dir)),
                    'type': 'pattern_location_fix',
                    'fix': f'{wrong} -> {right}'
                })
        
        return modified
    
    def fix_template_placeholders(self, file_path: Path, content: str) -> str:
        """Fix remaining template placeholders."""
        modified = content
        
        # Template pattern fixes
        template_fixes = {
            '../../core-principles/pillars/pillar2.md': '<!-- TODO: Add pillar reference -->',
            '../core-principles/pillars/1-work-distribution.md': '<!-- TODO: Add work distribution pillar -->',
        }
        
        for wrong, right in template_fixes.items():
            if wrong in modified:
                pattern = rf'\[([^\]]*)\]\({re.escape(wrong)}\)'
                modified = re.sub(pattern, right, modified)
                self.fixes_applied.append({
                    'file': str(file_path.relative_to(self.docs_dir)),
                    'type': 'template_placeholder_fix'
                })
        
        return modified
    
    def fix_file(self, file_path: Path) -> bool:
        """Apply all fixes to a single file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply fixes
            content = self.fix_category_index_links(file_path, content)
            content = self.fix_main_index_category_links(file_path, content)
            content = self.fix_empty_link_artifacts(file_path, content)
            content = self.fix_common_wrong_extensions(file_path, content)
            content = self.fix_missing_category_patterns(file_path, content)
            content = self.fix_template_placeholders(file_path, content)
            
            # Write back if changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
                
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
        
        return False
    
    def run_final_cleanup(self):
        """Run final cleanup."""
        print("🔧 Final Pattern Link Cleanup")
        print("=" * 40)
        
        # Process all pattern files
        pattern_files = list(self.pattern_dir.rglob("*.md"))
        total_files = len(pattern_files)
        files_fixed = 0
        
        for file_path in pattern_files:
            if self.fix_file(file_path):
                files_fixed += 1
        
        print(f"\n{'=' * 80}")
        print("FINAL CLEANUP SUMMARY")
        print(f"{'=' * 80}")
        print(f"Files processed: {total_files}")
        print(f"Files modified: {files_fixed}")
        print(f"Total fixes applied: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            print("\n✅ Final cleanup complete!")
            
            # Group fixes by type
            by_type = {}
            for fix in self.fixes_applied:
                fix_type = fix['type']
                if fix_type not in by_type:
                    by_type[fix_type] = 0
                by_type[fix_type] += 1
            
            for fix_type, count in by_type.items():
                print(f"  {fix_type.replace('_', ' ').title()}: {count} fixes")
        
        return len(self.fixes_applied) > 0

def main():
    """Main entry point."""
    cleanup = FinalPatternLinkCleanup()
    success = cleanup.run_final_cleanup()
    
    if success:
        print("\nRun the validator one more time to see the final results!")
    else:
        print("\nNo additional fixes were needed.")

if __name__ == "__main__":
    main()
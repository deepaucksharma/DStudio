#!/usr/bin/env python3
"""
Manual Pattern Link Fixes

This script provides targeted fixes for the remaining broken links found by the validator.
It focuses on the most common and easily fixable issues that require manual review.
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

class ManualPatternLinkFixer:
    def __init__(self, docs_dir: str = "/home/deepak/DStudio/docs"):
        self.docs_dir = Path(docs_dir)
        self.pattern_dir = self.docs_dir / "pattern-library"
        
        # Define specific fixes for known broken links
        self.specific_fixes = {
            # Template fixes
            '../../core-principles/laws/law1.md': '<!-- TODO: Add actual law reference -->',
            '../../core-principles/laws/law2.md': '<!-- TODO: Add actual law reference -->',
            '../../core-principles/pillars/pillar1.md': '<!-- TODO: Add actual pillar reference -->',
            
            # Common missing pattern fixes
            '../coordination/saga.md': '../data-management/saga.md',
            '../scaling/load-balancing/': '../scaling/load-balancing.md',
            '../resilience/health-check/': '../resilience/health-check.md',
            '../scaling/caching-strategies/': '../scaling/caching-strategies.md',
            '../data/cqrs.md': '../data-management/cqrs.md',
            
            # Architecture handbook references (remove for now)
            '../../architects-handbook/': '<!-- TODO: Add architects handbook -->',
            
            # PDF/external resources (comment out)
            'playbooks/': '<!-- TODO: Add actual playbook -->',
            '.pdf/': '<!-- TODO: Add actual PDF resource -->',
            
            # Broken internal references
            '../pattern-library/append-only.md': '<!-- TODO: Add append-only pattern -->',
            '../data-management/migration-patterns.md': '<!-- TODO: Add migration patterns -->',
            '../architecture/multi-region.md': '../scaling/multi-region.md',
            '../performance/cdn.md': '../scaling/content-delivery-network.md',
            '../data-management/replication.md': '<!-- TODO: Add replication pattern -->',
            '../architecture/global-load-balancing.md': '../scaling/geographic-load-balancing.md',
        }
        
        self.fixes_applied = []
        
    def create_backup(self):
        """Create backup before making changes."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f"/home/deepak/DStudio/manual_fixes_backup_{timestamp}")
        
        logger.info(f"Creating backup at {backup_dir}")
        shutil.copytree(self.docs_dir, backup_dir)
        return backup_dir
        
    def fix_trailing_slash_links(self, content: str, file_path: Path) -> str:
        """Fix links ending with trailing slash."""
        modified = content
        
        # Pattern for links ending with /
        pattern = r'\[([^\]]+)\]\(([^)]+)/\)'
        
        def replace_func(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # If it's a PDF reference, comment it out
            if '.pdf' in link_url:
                return f'<!-- TODO: Add {link_text} resource -->'
            
            # Otherwise try without the trailing slash
            return f'[{link_text}]({link_url}.md)'
        
        new_content = re.sub(pattern, replace_func, modified)
        if new_content != modified:
            self.fixes_applied.append({
                'file': str(file_path.relative_to(self.docs_dir)),
                'type': 'trailing_slash_fix',
                'count': len(re.findall(pattern, modified))
            })
        
        return new_content
    
    def fix_empty_link_artifacts(self, content: str, file_path: Path) -> str:
        """Fix broken link artifacts that create empty links."""
        modified = content
        
        # Common broken patterns that result in empty links
        broken_patterns = [
            r"\[h\['metrics'\]\(\)",
            r"\['spec'\]\(\)",
            r"\[0\]\(\)",
            r"\[([^\]]*)\]\(\s*\)",  # Empty parentheses
        ]
        
        fixes_count = 0
        for pattern in broken_patterns:
            if re.search(pattern, modified):
                modified = re.sub(pattern, '<!-- Removed broken link artifact -->', modified)
                fixes_count += 1
        
        if fixes_count > 0:
            self.fixes_applied.append({
                'file': str(file_path.relative_to(self.docs_dir)),
                'type': 'empty_link_cleanup',
                'count': fixes_count
            })
        
        return modified
    
    def apply_specific_fixes(self, content: str, file_path: Path) -> str:
        """Apply specific known fixes."""
        modified = content
        fixes_count = 0
        
        for broken_link, fix in self.specific_fixes.items():
            if broken_link in modified:
                # Handle different types of fixes
                if fix.startswith('<!--'):
                    # Comment replacement
                    pattern = rf'\[([^\]]*)\]\({re.escape(broken_link)}\)'
                    modified = re.sub(pattern, fix, modified)
                else:
                    # Direct replacement
                    modified = modified.replace(broken_link, fix)
                fixes_count += 1
        
        if fixes_count > 0:
            self.fixes_applied.append({
                'file': str(file_path.relative_to(self.docs_dir)),
                'type': 'specific_fix',
                'count': fixes_count
            })
        
        return modified
    
    def fix_case_study_references(self, content: str, file_path: Path) -> str:
        """Fix or comment out case study references."""
        pattern = r'\[([^\]]*[Cc]ase [Ss]tudy[^\]]*)\]\(([^)]+)\)'
        
        def replace_func(match):
            link_text = match.group(1)
            return f'<!-- TODO: Add {link_text} -->'
        
        new_content = re.sub(pattern, replace_func, content)
        if new_content != content:
            self.fixes_applied.append({
                'file': str(file_path.relative_to(self.docs_dir)),
                'type': 'case_study_cleanup',
                'count': len(re.findall(pattern, content))
            })
        
        return new_content
    
    def fix_architects_handbook_references(self, content: str, file_path: Path) -> str:
        """Fix or comment out architects handbook references."""
        pattern = r'\[([^\]]*)\]\(([^)]*architects-handbook[^)]*)\)'
        
        def replace_func(match):
            link_text = match.group(1)
            return f'<!-- TODO: Add {link_text} from Architects Handbook -->'
        
        new_content = re.sub(pattern, replace_func, content)
        if new_content != content:
            self.fixes_applied.append({
                'file': str(file_path.relative_to(self.docs_dir)),
                'type': 'handbook_cleanup',
                'count': len(re.findall(pattern, content))
            })
        
        return new_content
    
    def fix_file(self, file_path: Path) -> bool:
        """Apply all fixes to a single file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply all fixes
            content = self.fix_empty_link_artifacts(content, file_path)
            content = self.fix_trailing_slash_links(content, file_path)
            content = self.apply_specific_fixes(content, file_path)
            content = self.fix_case_study_references(content, file_path)
            content = self.fix_architects_handbook_references(content, file_path)
            
            # Write back if changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
                
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
        
        return False
    
    def run_manual_fixes(self):
        """Run all manual fixes."""
        print("🔧 Manual Pattern Link Fixes")
        print("=" * 40)
        
        # Create backup
        backup_dir = self.create_backup()
        
        # Process all pattern files
        pattern_files = list(self.pattern_dir.rglob("*.md"))
        total_files = len(pattern_files)
        files_fixed = 0
        
        logger.info(f"Processing {total_files} pattern files...")
        
        for file_path in pattern_files:
            if self.fix_file(file_path):
                files_fixed += 1
        
        # Generate report
        self.generate_fix_report()
        
        print(f"\n{'=' * 80}")
        print("MANUAL FIX SUMMARY")
        print(f"{'=' * 80}")
        print(f"Files processed: {total_files}")
        print(f"Files modified: {files_fixed}")
        print(f"Total fixes applied: {len(self.fixes_applied)}")
        print(f"Backup created at: {backup_dir}")
        
        if self.fixes_applied:
            print("\n✅ Manual fixes applied!")
            print("Run the validator again to see final results.")
        else:
            print("\nℹ️  No additional fixes could be applied automatically.")
    
    def generate_fix_report(self):
        """Generate report of manual fixes applied."""
        if not self.fixes_applied:
            return
            
        print(f"\n{'=' * 80}")
        print("MANUAL FIX REPORT")
        print(f"{'=' * 80}")
        
        # Group by type
        by_type = {}
        for fix in self.fixes_applied:
            fix_type = fix['type']
            if fix_type not in by_type:
                by_type[fix_type] = []
            by_type[fix_type].append(fix)
        
        for fix_type, fixes in by_type.items():
            total_count = sum(fix['count'] for fix in fixes)
            print(f"\n{fix_type.upper().replace('_', ' ')} ({len(fixes)} files, {total_count} fixes):")
            
            for fix in fixes[:5]:  # Show first 5
                print(f"  {fix['file']}: {fix['count']} fixes")
                
            if len(fixes) > 5:
                print(f"  ... and {len(fixes) - 5} more files")

def main():
    """Main entry point."""
    fixer = ManualPatternLinkFixer()
    fixer.run_manual_fixes()

if __name__ == "__main__":
    main()
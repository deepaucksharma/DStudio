#!/usr/bin/env python3
"""
Automated Pattern Link Fixer

This script automatically fixes common link issues found by the validator:
1. Fix links to missing but similar files 
2. Fix broken relative paths
3. Fix links that should go to category index files
4. Fix missing .md extensions
5. Remove/fix placeholder links
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import logging
from collections import defaultdict
import shutil
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class PatternLinkFixer:
    def __init__(self, docs_dir: str = "/home/deepak/DStudio/docs"):
        self.docs_dir = Path(docs_dir)
        self.pattern_dir = self.docs_dir / "pattern-library"
        
        # Build comprehensive file mappings
        self.all_files = self._build_file_map()
        self.pattern_files = self._build_pattern_file_map()
        
        # Track fixes
        self.fixes_applied = []
        self.backup_dir = None
        
    def _build_file_map(self) -> Set[str]:
        """Build comprehensive set of all existing files."""
        files = set()
        
        for file_path in self.docs_dir.rglob("*.md"):
            rel_path = file_path.relative_to(self.docs_dir)
            rel_str = str(rel_path).replace('\\', '/')
            
            files.add(rel_str)
            files.add(rel_str.replace('.md', ''))
            
            if file_path.name == 'index.md':
                parent = str(rel_path.parent).replace('\\', '/')
                if parent != '.':
                    files.add(parent)
                    files.add(parent + '/')
                    
        return files
    
    def _build_pattern_file_map(self) -> Dict[str, str]:
        """Build mapping of pattern names to file paths."""
        pattern_map = {}
        
        for file_path in self.pattern_dir.rglob("*.md"):
            rel_path = str(file_path.relative_to(self.docs_dir)).replace('\\', '/')
            
            # Extract pattern name from file path
            pattern_name = file_path.stem
            if pattern_name != 'index':
                pattern_map[pattern_name] = rel_path
                pattern_map[pattern_name.replace('-', ' ')] = rel_path
                
        return pattern_map
    
    def create_backup(self):
        """Create backup of docs directory before making changes."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"/home/deepak/DStudio/pattern_links_backup_{timestamp}")
        
        logger.info(f"Creating backup at {self.backup_dir}")
        shutil.copytree(self.docs_dir, self.backup_dir)
        
    def find_similar_file(self, broken_url: str) -> Optional[str]:
        """Find similar file that might be the intended target."""
        # Remove .md and normalize
        clean_url = broken_url.replace('.md', '').replace('/', ' ').replace('-', ' ').lower()
        
        # Try to match by pattern name
        for pattern_name, file_path in self.pattern_files.items():
            if pattern_name.lower() == clean_url:
                return file_path
                
        # Try partial matching
        for pattern_name, file_path in self.pattern_files.items():
            if clean_url in pattern_name.lower() or pattern_name.lower() in clean_url:
                return file_path
                
        return None
    
    def fix_relative_path(self, source_file: Path, broken_url: str) -> Optional[str]:
        """Try to fix broken relative paths."""
        if not broken_url.startswith('../'):
            return None
            
        # Parse the intended target
        parts = broken_url.split('/')
        if len(parts) < 2:
            return None
            
        category = parts[-2] if len(parts) > 1 else None
        filename = parts[-1]
        
        # Common pattern: ../category/pattern-name.md
        if category and category in ['architecture', 'communication', 'coordination', 'cost-optimization',
                                   'data-management', 'deployment', 'ml-infrastructure', 'resilience', 
                                   'scaling', 'security']:
            
            # Check if file exists in that category
            potential_path = f"pattern-library/{category}/{filename}"
            if potential_path in self.all_files or potential_path + '.md' in self.all_files:
                # Calculate correct relative path
                source_rel = source_file.relative_to(self.docs_dir)
                source_depth = len(str(source_rel).split('/')) - 1
                
                if source_depth == 1:  # Top level
                    return f"{category}/{filename}"
                elif source_depth == 2:  # In category
                    return f"../{category}/{filename}"
                else:  # Deeper
                    prefix = '../' * (source_depth - 1)
                    return f"{prefix}{category}/{filename}"
        
        return None
    
    def fix_template_placeholder_links(self, file_path: Path, content: str) -> str:
        """Remove or fix template placeholder links."""
        # Common placeholder patterns
        placeholders = [
            r'\[Pattern \d+\]\(\.\./category/pattern\d+\.md\)',
            r'\[Pattern \d+\]\(\.\./related-pattern-\d+\.md\)',
            r'\[related pattern\]\(link-to-pattern\.md\)',
            r'\[TODO: Add link\]\(\)',
            r'\[TODO: Link\]\(\)',
            r'\[TBD\]\(\)',
        ]
        
        modified = content
        fixes_count = 0
        
        for pattern in placeholders:
            if re.search(pattern, modified, re.IGNORECASE):
                # Replace with commented version
                modified = re.sub(pattern, '<!-- TODO: Add actual pattern link -->', modified, flags=re.IGNORECASE)
                fixes_count += 1
        
        if fixes_count > 0:
            self.fixes_applied.append({
                'file': str(file_path.relative_to(self.docs_dir)),
                'type': 'placeholder_removal',
                'count': fixes_count
            })
            
        return modified
    
    def fix_missing_md_extensions(self, content: str) -> str:
        """Add missing .md extensions to internal links."""
        # Pattern for links that should have .md extension
        pattern = r'\[([^\]]+)\]\(([^)]*[^/)])\)'
        
        def replace_func(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Skip if already has extension, is external, or is anchor
            if link_url.endswith('.md') or link_url.startswith(('http', '#', 'mailto:')):
                return match.group(0)
                
            # Skip if it's a directory reference ending with /
            if link_url.endswith('/'):
                return match.group(0)
                
            # Add .md extension
            return f'[{link_text}]({link_url}.md)'
        
        return re.sub(pattern, replace_func, content)
    
    def fix_category_links(self, source_file: Path, content: str) -> str:
        """Fix links that should go to category index files."""
        pattern = r'\[([^\]]+)\]\(([^)]+)/\)'
        
        def replace_func(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Check if this is a category reference
            category = link_url.split('/')[-1] if '/' in link_url else link_url
            
            if category in ['architecture', 'communication', 'coordination', 'cost-optimization',
                          'data-management', 'deployment', 'ml-infrastructure', 'resilience', 
                          'scaling', 'security']:
                # Fix to proper category index
                source_rel = source_file.relative_to(self.docs_dir)
                if str(source_rel).startswith('pattern-library/'):
                    if source_rel.parent.name == 'pattern-library':
                        # Top level, direct reference
                        return f'[{link_text}]({category}/)'
                    else:
                        # In category, need ../
                        return f'[{link_text}](../{category}/)'
                        
            return match.group(0)
        
        return re.sub(pattern, replace_func, content)
    
    def fix_common_patterns(self, source_file: Path, content: str) -> str:
        """Fix common broken link patterns."""
        modified = content
        
        # Fix links to common patterns that are in wrong categories
        common_fixes = {
            '../architecture/api-gateway.md': '../communication/api-gateway.md',
            '../architecture/service-mesh.md': '../communication/service-mesh.md',
            '../architecture/cqrs.md': '../data-management/cqrs.md',
            '../architecture/event-sourcing.md': '../data-management/event-sourcing.md',
            '../architecture/bff.md': '../architecture/backends-for-frontends.md',
            '../data/database-per-service.md': '../scaling/database-per-service.md',
            '../infrastructure/service-mesh.md': '../communication/service-mesh.md',
            
            # Fix relative path issues
            '../scaling/consistent-hashing.md': '../data-management/consistent-hashing.md',
            '../resilience/circuit-breaker.md': '../resilience/circuit-breaker.md',
        }
        
        for broken, fixed in common_fixes.items():
            if broken in modified:
                # Verify the target exists
                source_rel = source_file.relative_to(self.docs_dir)
                source_dir = source_rel.parent
                
                # Resolve the target path
                if fixed.startswith('../'):
                    if source_dir.name == 'pattern-library':
                        target_path = fixed[3:]  # Remove ../
                    else:
                        target_path = f"{source_dir.parent}/{fixed[3:]}"
                else:
                    target_path = fixed
                    
                if target_path in self.all_files:
                    modified = modified.replace(broken, fixed)
                    self.fixes_applied.append({
                        'file': str(source_file.relative_to(self.docs_dir)),
                        'type': 'common_pattern_fix',
                        'from': broken,
                        'to': fixed
                    })
        
        return modified
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix all issues in a single file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply fixes
            content = self.fix_template_placeholder_links(file_path, content)
            content = self.fix_category_links(file_path, content)
            content = self.fix_common_patterns(file_path, content)
            # Temporarily disable this as it might be too aggressive
            # content = self.fix_missing_md_extensions(content)
            
            # Write back if changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
                
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
            
        return False
    
    def fix_all_pattern_files(self):
        """Fix issues in all pattern files."""
        logger.info("Fixing link issues in pattern files...")
        
        pattern_files = list(self.pattern_dir.rglob("*.md"))
        total_files = len(pattern_files)
        files_fixed = 0
        
        for i, file_path in enumerate(pattern_files, 1):
            if i % 20 == 0:
                logger.info(f"Progress: {i}/{total_files}")
                
            if self.fix_file(file_path):
                files_fixed += 1
        
        logger.info(f"Fixed issues in {files_fixed} files")
        return files_fixed
    
    def generate_fix_report(self):
        """Generate report of fixes applied."""
        if not self.fixes_applied:
            print("No fixes were applied.")
            return
            
        print(f"\n{'=' * 80}")
        print("LINK FIX REPORT")
        print(f"{'=' * 80}")
        
        # Group by fix type
        by_type = defaultdict(list)
        for fix in self.fixes_applied:
            by_type[fix['type']].append(fix)
        
        for fix_type, fixes in by_type.items():
            print(f"\n{fix_type.upper().replace('_', ' ')} ({len(fixes)} instances):")
            
            for fix in fixes[:5]:  # Show first 5
                if fix_type == 'placeholder_removal':
                    print(f"  {fix['file']}: Removed {fix['count']} placeholder links")
                elif fix_type == 'common_pattern_fix':
                    print(f"  {fix['file']}: {fix['from']} -> {fix['to']}")
                else:
                    print(f"  {fix['file']}")
                    
            if len(fixes) > 5:
                print(f"  ... and {len(fixes) - 5} more")
    
    def run_fixes(self):
        """Run all automated fixes."""
        print("🔧 Pattern Link Auto-Fixer")
        print("=" * 40)
        
        # Create backup
        self.create_backup()
        
        # Apply fixes
        files_fixed = self.fix_all_pattern_files()
        
        # Generate report
        self.generate_fix_report()
        
        print(f"\n{'=' * 80}")
        print("FIX SUMMARY")
        print(f"{'=' * 80}")
        print(f"Files processed: {files_fixed}")
        print(f"Total fixes applied: {len(self.fixes_applied)}")
        print(f"Backup created at: {self.backup_dir}")
        
        if self.fixes_applied:
            print("\n✅ Fixes applied successfully!")
            print("Run the validator again to see remaining issues.")
        else:
            print("\nℹ️  No automatic fixes could be applied.")
            print("Manual review of broken links is required.")

def main():
    """Main entry point."""
    fixer = PatternLinkFixer()
    fixer.run_fixes()

if __name__ == "__main__":
    main()
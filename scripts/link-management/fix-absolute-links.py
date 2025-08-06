#!/usr/bin/env python3
"""Fix absolute links to use relative paths in all markdown files."""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

class AbsoluteLinkFixer:
    def __init__(self, docs_dir: Path = Path("docs"), fix: bool = False):
        self.docs_dir = docs_dir
        self.fix = fix
        self.changes_made = []
        self.errors = []
        
    def calculate_relative_path(self, from_file: Path, to_path: str) -> str:
        """Calculate relative path from one file to another."""
        # Remove leading slash and trailing slash if present
        to_path = to_path.strip('/')
        
        # Handle special cases
        if to_path.endswith('/index') or to_path.endswith('/index/'):
            to_path = to_path.replace('/index/', '/').replace('/index', '/')
            
        # Determine target path
        if to_path.endswith('/'):
            # Directory reference - add index.md
            target = self.docs_dir / to_path / "index.md"
        else:
            # File reference - add .md if missing
            if not to_path.endswith('.md'):
                target = self.docs_dir / f"{to_path}.md"
            else:
                target = self.docs_dir / to_path
                
        # Check if target exists
        if not target.exists():
            # Try without index
            alt_target = self.docs_dir / to_path.rstrip('/') / "index.md"
            if alt_target.exists():
                target = alt_target
                
        # Calculate relative path
        try:
            from_dir = from_file.parent
            rel_path = Path(target).relative_to(self.docs_dir)
            
            # Calculate how many levels up we need to go
            levels_up = len(from_file.relative_to(self.docs_dir).parts) - 1
            
            if levels_up == 0:
                # Same directory level as docs
                return str(rel_path)
            else:
                # Need to go up some levels
                prefix = "../" * levels_up
                return prefix + str(rel_path)
        except ValueError:
            # Can't calculate relative path
            return None
            
    def fix_absolute_links_in_file(self, file_path: Path) -> int:
        """Fix absolute links in a single file."""
        try:
            content = file_path.read_text()
            original_content = content
            changes = 0
            
            # Pattern to match markdown links with absolute paths
            # Matches [text](/path) and [text](/path/)
            pattern = r'\[([^\]]+)\]\((/[^)]+)\)'
            
            def replace_link(match):
                nonlocal changes
                text = match.group(1)
                abs_path = match.group(2)
                
                # Skip external URLs
                if abs_path.startswith('//') or '://' in abs_path:
                    return match.group(0)
                    
                # Calculate relative path
                rel_path = self.calculate_relative_path(file_path, abs_path)
                
                if rel_path:
                    changes += 1
                    return f'[{text}]({rel_path})'
                else:
                    # Couldn't calculate relative path, leave as is
                    return match.group(0)
                    
            # Replace all absolute links
            content = re.sub(pattern, replace_link, content)
            
            # Also fix reference-style links: [text]: /path
            ref_pattern = r'^\[([^\]]+)\]:\s*(/[^\s]+)'
            
            def replace_ref_link(match):
                nonlocal changes
                label = match.group(1)
                abs_path = match.group(2)
                
                rel_path = self.calculate_relative_path(file_path, abs_path)
                if rel_path:
                    changes += 1
                    return f'[{label}]: {rel_path}'
                return match.group(0)
                
            content = re.sub(ref_pattern, replace_ref_link, content, flags=re.MULTILINE)
            
            # Write back if changed
            if content != original_content and self.fix:
                file_path.write_text(content)
                self.changes_made.append(f"Fixed {changes} links in {file_path.relative_to(self.docs_dir)}")
                
            return changes
            
        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {e}")
            return 0
            
    def fix_all_files(self):
        """Fix absolute links in all markdown files."""
        print("🔧 FIXING ABSOLUTE LINKS...")
        print("="*60)
        
        total_changes = 0
        files_processed = 0
        
        for md_file in self.docs_dir.glob("**/*.md"):
            changes = self.fix_absolute_links_in_file(md_file)
            if changes > 0:
                files_processed += 1
                total_changes += changes
                if not self.fix:
                    print(f"Would fix {changes} links in: {md_file.relative_to(self.docs_dir)}")
                    
        print(f"\n📊 Summary:")
        print(f"  - Files with absolute links: {files_processed}")
        print(f"  - Total absolute links found: {total_changes}")
        
        if self.fix:
            print(f"  - Links fixed: {total_changes}")
        else:
            print(f"  - Links to be fixed: {total_changes}")
            print(f"\nRun with --fix to apply changes")
            
    def generate_report(self):
        """Generate summary report."""
        if self.changes_made:
            print(f"\n✅ Changes made:")
            for change in self.changes_made[:10]:
                print(f"  - {change}")
            if len(self.changes_made) > 10:
                print(f"  ... and {len(self.changes_made) - 10} more files")
                
        if self.errors:
            print(f"\n❌ Errors encountered:")
            for error in self.errors[:5]:
                print(f"  - {error}")

def main():
    parser = argparse.ArgumentParser(description='Fix absolute links in documentation')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (default: dry run)')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    args = parser.parse_args()
    
    fixer = AbsoluteLinkFixer(fix=args.fix)
    fixer.fix_all_files()
    fixer.generate_report()

if __name__ == "__main__":
    main()
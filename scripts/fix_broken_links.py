#!/usr/bin/env python3
"""
Fix broken links in markdown files systematically.
This script addresses the main patterns of broken links identified in the analysis.
"""

import os
import re
from pathlib import Path
import logging
from typing import List, Tuple, Dict, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class LinkFixer:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.fixes_made = 0
        self.files_modified = set()
        
        # Build a map of all existing markdown files for validation
        self.existing_files = self._build_file_map()
        
    def _build_file_map(self) -> Dict[str, Path]:
        """Build a map of all existing markdown files."""
        file_map = {}
        for file_path in self.docs_dir.rglob("*.md"):
            # Store both relative and absolute paths
            rel_path = file_path.relative_to(self.docs_dir)
            file_map[str(rel_path)] = file_path
            # Also store without .md extension for easier lookup
            file_map[str(rel_path).replace('.md', '')] = file_path
        return file_map
    
    def fix_file(self, file_path: Path) -> int:
        """Fix links in a single file."""
        fixes = 0
        
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Fix Pattern 1: .md files treated as directories
            # e.g., ../../pattern-library/resilience.md/circuit-breaker.md
            content, count = self._fix_md_as_directory(content)
            fixes += count
            
            # Fix Pattern 2: Excessive parent directory traversal (..../)
            content, count = self._fix_excessive_traversal(content)
            fixes += count
            
            # Fix Pattern 3: Empty links
            content, count = self._fix_empty_links(content)
            fixes += count
            
            # Fix Pattern 4: File extensions in URLs (.md in web URLs)
            content, count = self._fix_url_extensions(content)
            fixes += count
            
            # Fix Pattern 5: Validate and fix relative paths
            content, count = self._fix_relative_paths(content, file_path)
            fixes += count
            
            # Write back if changes were made
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                self.files_modified.add(file_path)
                logger.info(f"Fixed {fixes} links in {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
        
        return fixes
    
    def _fix_md_as_directory(self, content: str) -> Tuple[str, int]:
        """Fix pattern where .md files are treated as directories."""
        fixes = 0
        
        # Pattern: something.md/something-else.md or something.md/index.md
        pattern = r'(\.\./)*([a-zA-Z0-9-_/]+)\.md/([a-zA-Z0-9-_/]+)(\.md)?'
        
        def replacer(match):
            nonlocal fixes
            prefix = match.group(1) or ''
            parent = match.group(2)
            child = match.group(3)
            extension = match.group(4) or '.md'
            
            # Remove .md from parent path
            new_link = f"{prefix}{parent}/{child}{extension}"
            fixes += 1
            return new_link
        
        content = re.sub(pattern, replacer, content)
        return content, fixes
    
    def _fix_excessive_traversal(self, content: str) -> Tuple[str, int]:
        """Fix excessive parent directory traversal (..../ patterns)."""
        fixes = 0
        
        # Replace ..../ with ../
        def replacer(match):
            nonlocal fixes
            fixes += 1
            # Count the dots to determine intended depth
            dots = match.group(0).count('.')
            if dots >= 4:
                # Assume they meant multiple ../ segments
                depth = (dots - 1) // 2
                return '../' * depth
            return match.group(0)
        
        # Pattern for excessive dots
        pattern = r'\.{4,}/'
        content = re.sub(pattern, replacer, content)
        
        return content, fixes
    
    def _fix_empty_links(self, content: str) -> Tuple[str, int]:
        """Remove empty markdown links."""
        fixes = 0
        
        # Pattern for empty links: [text]()
        pattern = r'\[([^\]]+)\]\(\s*\)'
        
        def replacer(match):
            nonlocal fixes
            fixes += 1
            # Return just the text without link markup
            return match.group(1)
        
        content = re.sub(pattern, replacer, content)
        return content, fixes
    
    def _fix_url_extensions(self, content: str) -> Tuple[str, int]:
        """Remove .md extensions from web URLs."""
        fixes = 0
        
        # Pattern for URLs with .md extension
        pattern = r'(https?://[^/\s]+/[^\s]*?)\.md(\s|$|\))'
        
        def replacer(match):
            nonlocal fixes
            fixes += 1
            # Remove .md extension from URL
            return match.group(1) + match.group(2)
        
        content = re.sub(pattern, replacer, content)
        return content, fixes
    
    def _fix_relative_paths(self, content: str, file_path: Path) -> Tuple[str, int]:
        """Validate and fix relative paths to ensure they point to existing files."""
        fixes = 0
        
        # Get the directory of the current file
        current_dir = file_path.parent
        
        # Pattern for markdown links with relative paths
        pattern = r'\[([^\]]+)\]\((\.\./[^\)]+)\)'
        
        def replacer(match):
            nonlocal fixes
            link_text = match.group(1)
            link_path = match.group(2)
            
            # Skip if it's a URL or anchor
            if link_path.startswith('http') or link_path.startswith('#'):
                return match.group(0)
            
            # Try to resolve the path
            target_path = self._resolve_path(current_dir, link_path)
            
            if target_path:
                # Calculate correct relative path
                try:
                    correct_path = os.path.relpath(target_path, current_dir)
                    # Ensure forward slashes for consistency
                    correct_path = correct_path.replace('\\', '/')
                    
                    if correct_path != link_path:
                        fixes += 1
                        return f'[{link_text}]({correct_path})'
                except ValueError:
                    # Can't compute relative path (different drives on Windows)
                    pass
            
            return match.group(0)
        
        content = re.sub(pattern, replacer, content)
        return content, fixes
    
    def _resolve_path(self, current_dir: Path, link_path: str) -> Optional[Path]:
        """Try to resolve a relative path to an existing file."""
        # Remove any URL fragments or query parameters
        clean_path = link_path.split('#')[0].split('?')[0]
        
        # Try direct resolution
        target = (current_dir / clean_path).resolve()
        
        # Check if file exists
        if target.exists() and target.suffix == '.md':
            return target
        
        # Try adding .md extension
        if not clean_path.endswith('.md'):
            target_with_md = (current_dir / f"{clean_path}.md").resolve()
            if target_with_md.exists():
                return target_with_md
        
        # Try as directory with index.md
        target_index = (current_dir / clean_path / "index.md").resolve()
        if target_index.exists():
            return target_index
        
        return None
    
    def fix_all_files(self):
        """Fix links in all markdown files."""
        all_files = list(self.docs_dir.rglob("*.md"))
        total_files = len(all_files)
        
        logger.info(f"Processing {total_files} markdown files...")
        
        for i, file_path in enumerate(all_files, 1):
            if i % 50 == 0:
                logger.info(f"Progress: {i}/{total_files} files processed")
            
            fixes = self.fix_file(file_path)
            self.fixes_made += fixes
        
        logger.info(f"\nSummary:")
        logger.info(f"Total fixes made: {self.fixes_made}")
        logger.info(f"Files modified: {len(self.files_modified)}")
        
        if self.files_modified:
            logger.info("\nModified files:")
            for file_path in sorted(self.files_modified):
                logger.info(f"  - {file_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix broken links in markdown files")
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Path to the docs directory (default: docs)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making changes (analysis only)"
    )
    
    args = parser.parse_args()
    
    if not Path(args.docs_dir).exists():
        logger.error(f"Directory {args.docs_dir} does not exist")
        return 1
    
    fixer = LinkFixer(args.docs_dir)
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        # TODO: Implement dry run analysis
    else:
        fixer.fix_all_files()
    
    return 0


if __name__ == "__main__":
    exit(main())
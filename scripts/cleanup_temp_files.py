#!/usr/bin/env python3
"""
Clean up temporary files from pattern library fixes
Preserves important documentation while removing temporary artifacts
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class TempFileCleaner:
    def __init__(self):
        self.base_dir = Path("/home/deepak/DStudio")
        self.preserve_list = [
            # Important documentation to keep
            "PATTERN_LIBRARY_MAINTENANCE_GUIDE.md",
            "PATTERN_LIBRARY_COMPLETE_FIX_SUMMARY.md",
            
            # Scripts to keep
            "scripts/",
            
            # Main docs
            "docs/",
            "mkdocs.yml",
            "README.md",
            ".git/",
            ".github/",
            
            # Config files
            ".gitignore",
            "requirements.txt",
            "pyproject.toml",
        ]
        
        self.temp_patterns = [
            # Temporary files to remove
            "*_backup_*",
            "*_report.md",
            "*_analysis.json", 
            "*_audit.json",
            "pattern_merge_report.md",
            "pattern_metadata_analysis.json",
            "PATTERN_METADATA_STANDARDIZATION_REPORT.md",
            "PATTERN_LIBRARY_FIXES_SUMMARY.md",
            "PATTERN_LIBRARY_STANDARDIZATION_SUMMARY.md",
            "PATTERN_LIBRARY_QA_REPORT.md",
        ]
        
        self.files_removed = []
        self.dirs_removed = []
        self.space_freed = 0
        
    def should_preserve(self, path: Path) -> bool:
        """Check if file should be preserved"""
        for pattern in self.preserve_list:
            if pattern in str(path):
                return True
        return False
        
    def is_temp_file(self, path: Path) -> bool:
        """Check if file matches temporary patterns"""
        from fnmatch import fnmatch
        
        for pattern in self.temp_patterns:
            if fnmatch(path.name, pattern):
                return True
        return False
        
    def get_size(self, path: Path) -> int:
        """Get size of file or directory"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total = 0
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
            return total
        return 0
        
    def clean_temp_files(self):
        """Clean temporary files and directories"""
        print("🧹 Cleaning temporary files from pattern library fixes...")
        print("-" * 60)
        
        # Clean root directory files
        for item in self.base_dir.iterdir():
            if self.is_temp_file(item) and not self.should_preserve(item):
                size = self.get_size(item)
                
                if item.is_file():
                    print(f"  📄 Removing file: {item.name}")
                    os.remove(item)
                    self.files_removed.append(item.name)
                    self.space_freed += size
                    
                elif item.is_dir() and "backup" in item.name:
                    print(f"  📁 Removing directory: {item.name}")
                    shutil.rmtree(item)
                    self.dirs_removed.append(item.name)
                    self.space_freed += size
                    
        print("-" * 60)
        
    def generate_summary(self):
        """Generate cleanup summary"""
        print("\n📊 Cleanup Summary")
        print("=" * 60)
        print(f"  Files removed: {len(self.files_removed)}")
        print(f"  Directories removed: {len(self.dirs_removed)}")
        print(f"  Space freed: {self.format_size(self.space_freed)}")
        print("=" * 60)
        
        if self.files_removed:
            print("\n📄 Files Removed:")
            for f in self.files_removed:
                print(f"  - {f}")
                
        if self.dirs_removed:
            print("\n📁 Directories Removed:")
            for d in self.dirs_removed:
                print(f"  - {d}")
                
        print("\n✅ Important files preserved:")
        print("  - PATTERN_LIBRARY_MAINTENANCE_GUIDE.md")
        print("  - PATTERN_LIBRARY_COMPLETE_FIX_SUMMARY.md")
        print("  - All scripts in scripts/")
        print("  - All documentation in docs/")
        
    def format_size(self, size: int) -> str:
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
        
    def create_archive(self):
        """Create archive of important artifacts before cleanup"""
        archive_dir = self.base_dir / "pattern_library_artifacts"
        archive_dir.mkdir(exist_ok=True)
        
        # Copy important reports to archive
        important_files = [
            "PATTERN_LIBRARY_COMPLETE_FIX_SUMMARY.md",
            "PATTERN_LIBRARY_MAINTENANCE_GUIDE.md",
        ]
        
        for file in important_files:
            source = self.base_dir / file
            if source.exists():
                dest = archive_dir / file
                shutil.copy2(source, dest)
                
        print(f"📦 Important artifacts archived in: {archive_dir}")
        
    def run(self):
        """Run the cleanup process"""
        print("=" * 60)
        print("🧹 Pattern Library Temporary File Cleanup")
        print("=" * 60)
        
        # Create archive of important files
        self.create_archive()
        
        # Clean temporary files
        self.clean_temp_files()
        
        # Generate summary
        self.generate_summary()
        
        print("\n✨ Cleanup complete!")

def main():
    cleaner = TempFileCleaner()
    cleaner.run()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Final cleanup - Archive important docs and remove all temporary files
"""

import os
import tarfile
from pathlib import Path
from datetime import datetime
import shutil

class FinalCleanup:
    def __init__(self):
        self.base_dir = Path("/home/deepak/DStudio")
        self.archive_name = f"pattern_library_final_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        self.files_to_archive = []
        self.files_to_remove = []
        self.preserved_files = [
            "PATTERN_LIBRARY_MAINTENANCE_GUIDE.md",  # Keep this - it's the main guide
            "docs/",  # Keep all documentation
            "scripts/",  # Keep all scripts
            ".git/",  # Keep git
            "mkdocs.yml",  # Keep config
            "README.md",  # Keep readme
        ]
        
    def identify_files(self):
        """Identify files to archive and remove"""
        
        # Patterns for temporary files
        temp_patterns = [
            "*REPORT*.md",
            "*VALIDATION*.md", 
            "*SUMMARY*.md",
            "*ANALYSIS*.md",
            "*.csv",
            "*.json",
            "*backup*",
            "*transformed.md",
            "CLEANUP_COMPLETE.md",
        ]
        
        # Files to archive before removal
        archive_patterns = [
            "PATTERN_LIBRARY_COMPLETE_FIX_SUMMARY.md",
            "FINAL_CONTENT_VALIDATION_REPORT.md",
        ]
        
        for pattern in temp_patterns:
            for file in self.base_dir.glob(pattern):
                if file.is_file():
                    # Check if it should be preserved
                    should_preserve = False
                    for preserved in self.preserved_files:
                        if preserved in str(file):
                            should_preserve = True
                            break
                    
                    if not should_preserve:
                        # Check if it should be archived
                        should_archive = False
                        for archive_pattern in archive_patterns:
                            if file.name == archive_pattern:
                                should_archive = True
                                self.files_to_archive.append(file)
                                break
                        
                        if not should_archive or file not in self.files_to_archive:
                            self.files_to_remove.append(file)
                            
        # Also check for transformed pattern files
        for transformed in self.base_dir.rglob("*-transformed.md"):
            if transformed not in self.files_to_remove:
                self.files_to_remove.append(transformed)
                
    def create_archive(self):
        """Create archive of important files"""
        if not self.files_to_archive:
            print("  No files to archive")
            return
            
        archive_path = self.base_dir / self.archive_name
        
        with tarfile.open(archive_path, "w:gz") as tar:
            for file in self.files_to_archive:
                if file.exists():
                    tar.add(file, arcname=file.name)
                    print(f"  📦 Archived: {file.name}")
                    
        print(f"\n✅ Archive created: {self.archive_name}")
        return archive_path
        
    def remove_files(self):
        """Remove temporary files"""
        removed_count = 0
        total_size = 0
        
        for file in self.files_to_remove:
            if file.exists():
                size = file.stat().st_size
                total_size += size
                os.remove(file)
                removed_count += 1
                print(f"  🗑️  Removed: {file.name}")
                
        return removed_count, total_size
        
    def clean_pattern_artifacts(self):
        """Clean pattern library artifacts directory"""
        artifacts_dir = self.base_dir / "pattern_library_artifacts"
        if artifacts_dir.exists():
            # Archive the artifacts first
            if artifacts_dir.is_dir():
                for file in artifacts_dir.iterdir():
                    if file.is_file():
                        self.files_to_archive.append(file)
                        
                # Remove the directory after archiving
                shutil.rmtree(artifacts_dir)
                print("  🗑️  Removed: pattern_library_artifacts/")
                return True
        return False
        
    def format_size(self, size: int) -> str:
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
        
    def run(self):
        """Run the final cleanup"""
        print("=" * 60)
        print("🧹 Final Cleanup - Pattern Library")
        print("=" * 60)
        
        # Identify files
        print("\n📋 Identifying files...")
        self.identify_files()
        
        print(f"  - Files to archive: {len(self.files_to_archive)}")
        print(f"  - Files to remove: {len(self.files_to_remove)}")
        
        # Create archive
        print("\n📦 Creating archive...")
        archive_path = self.create_archive()
        
        # Remove files
        print("\n🗑️  Removing temporary files...")
        removed_count, total_size = self.remove_files()
        
        # Clean artifacts directory
        artifacts_removed = self.clean_pattern_artifacts()
        
        # Summary
        print("\n" + "=" * 60)
        print("✨ Cleanup Complete!")
        print("=" * 60)
        print(f"  📦 Archive created: {self.archive_name if archive_path else 'None'}")
        print(f"  🗑️  Files removed: {removed_count}")
        print(f"  💾 Space freed: {self.format_size(total_size)}")
        print(f"  ✅ Artifacts cleaned: {'Yes' if artifacts_removed else 'No'}")
        
        print("\n📁 Preserved:")
        print("  - PATTERN_LIBRARY_MAINTENANCE_GUIDE.md")
        print("  - All scripts in scripts/")
        print("  - All documentation in docs/")
        print("  - Final archive with key reports")
        
        print("\n" + "=" * 60)

def main():
    cleanup = FinalCleanup()
    cleanup.run()

if __name__ == "__main__":
    main()
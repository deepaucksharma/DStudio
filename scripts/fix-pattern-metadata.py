#!/usr/bin/env python3
"""
Comprehensive Pattern Metadata Fix Script

This script fixes the major issues identified in pattern metadata:
1. Invalid status values ("stable", "educational-only", "use-with-context", etc.)
2. Invalid relevance values ("specialized", "theoretical", "historical", etc.)
3. Missing description fields
4. Field naming inconsistencies (underscores vs hyphens)
5. Missing tier-specific required fields
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any

class PatternMetadataFixer:
    def __init__(self, base_path: str = "docs/pattern-library"):
        self.base_path = Path(base_path)
        
        # Status value mappings
        self.status_mapping = {
            "stable": "recommended",
            "educational-only": "use-with-caution", 
            "use-with-context": "use-with-expertise",
            "use_with_caution": "use-with-caution",
            "specialized-use": "use-with-expertise",
            "deprecated": "legacy",
            "experimental": "use-with-caution",
            "beta": "use-with-expertise"
        }
        
        # Relevance value mappings
        self.relevance_mapping = {
            "specialized": "niche",
            "theoretical": "niche",
            "historical": "declining", 
            "stable": "mainstream",
            "essential": "mainstream",
            "evolving": "growing"
        }
        
        # Default values for missing fields
        self.default_descriptions = {
            "cap-theorem": "Fundamental theorem defining trade-offs between Consistency, Availability, and Partition tolerance in distributed systems",
            "event-driven": "Architectural pattern where components communicate through events, enabling loose coupling and scalability",
            "cell-based": "Architecture pattern that isolates failures by partitioning systems into independent cells with shared-nothing design",
            "distributed-lock": "Coordination pattern that ensures mutual exclusion across distributed systems using consensus algorithms",
            "event-sourcing": "Data management pattern that stores all changes as immutable events, enabling audit trails and time travel",
            "cdc": "Data synchronization pattern that captures and propagates database changes in real-time",
            "cqrs": "Architectural pattern separating read and write operations to optimize performance and scalability",
            "consistent-hashing": "Load distribution algorithm that minimizes reorganization when nodes are added or removed",
            "geo-distribution": "Scaling pattern that distributes data and compute across geographic regions for performance and compliance",
            "multi-region": "Deployment pattern that spans multiple geographic regions for disaster recovery and latency optimization",
            "sharding": "Data partitioning technique that horizontally distributes data across multiple database instances",
            "backpressure": "Flow control mechanism that prevents system overload by limiting upstream request rates",
            "auto-scaling": "Dynamic resource management pattern that adjusts capacity based on demand metrics",
            "load-balancing": "Traffic distribution pattern that spreads requests across multiple backend instances",
            "service-mesh": "Infrastructure layer providing service-to-service communication, security, and observability"
        }

    def extract_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter and body from markdown content."""
        if not content.startswith('---'):
            return {}, content
        
        try:
            # Find the end of frontmatter
            end_marker = content.find('\n---\n', 3)
            if end_marker == -1:
                end_marker = content.find('\n---', 3)
                if end_marker == -1:
                    return {}, content
            
            frontmatter = content[3:end_marker].strip()
            body = content[end_marker + 4:]
            
            metadata = yaml.safe_load(frontmatter) or {}
            return metadata, body
        except yaml.YAMLError as e:
            print(f"YAML parsing error: {e}")
            return {}, content

    def write_frontmatter(self, metadata: Dict[str, Any], body: str) -> str:
        """Write metadata and body back to markdown format."""
        if not metadata:
            return body
        
        frontmatter = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        return f"---\n{frontmatter}---\n{body}"

    def fix_status_values(self, metadata: Dict[str, Any]) -> bool:
        """Fix invalid pattern_status values."""
        if "pattern_status" not in metadata:
            return False
        
        current_status = metadata["pattern_status"]
        if current_status in self.status_mapping:
            metadata["pattern_status"] = self.status_mapping[current_status]
            print(f"  ✓ Fixed status: {current_status} → {metadata['pattern_status']}")
            return True
        
        return False

    def fix_relevance_values(self, metadata: Dict[str, Any]) -> bool:
        """Fix invalid current_relevance values."""
        if "current_relevance" not in metadata:
            return False
        
        current_relevance = metadata["current_relevance"]
        if current_relevance in self.relevance_mapping:
            metadata["current_relevance"] = self.relevance_mapping[current_relevance]
            print(f"  ✓ Fixed relevance: {current_relevance} → {metadata['current_relevance']}")
            return True
        
        return False

    def add_missing_description(self, metadata: Dict[str, Any], filename: str) -> bool:
        """Add missing description field."""
        if "description" in metadata and metadata["description"]:
            return False
        
        # Extract pattern name from filename
        pattern_name = filename.replace('.md', '').replace('-', '_')
        
        if pattern_name in self.default_descriptions:
            metadata["description"] = self.default_descriptions[pattern_name]
            print(f"  ✓ Added description")
            return True
        
        # Generate generic description based on filename
        readable_name = filename.replace('.md', '').replace('-', ' ').title()
        metadata["description"] = f"Distributed systems pattern: {readable_name}"
        print(f"  ✓ Added generic description")
        return True

    def add_missing_fields(self, metadata: Dict[str, Any]) -> bool:
        """Add missing required fields based on tier."""
        changes = False
        
        # Add missing introduced date
        if "introduced" not in metadata or not metadata["introduced"]:
            metadata["introduced"] = "2024-01"
            print(f"  ✓ Added introduced date")
            changes = True
        
        # Add missing current_relevance
        if "current_relevance" not in metadata or not metadata["current_relevance"]:
            metadata["current_relevance"] = "mainstream"
            print(f"  ✓ Added current_relevance")
            changes = True
        
        # Add tier-specific fields
        tier = metadata.get("excellence_tier")
        if tier == "gold":
            if "modern_examples" not in metadata or not metadata["modern_examples"]:
                metadata["modern_examples"] = []
                print(f"  ✓ Added modern_examples (empty list)")
                changes = True
            if "production_checklist" not in metadata or not metadata["production_checklist"]:
                metadata["production_checklist"] = []
                print(f"  ✓ Added production_checklist (empty list)")
                changes = True
        elif tier == "silver":
            if "trade_offs" not in metadata or not metadata["trade_offs"]:
                metadata["trade_offs"] = {"pros": [], "cons": []}
                print(f"  ✓ Added trade_offs structure")
                changes = True
            if "best_for" not in metadata or not metadata["best_for"]:
                metadata["best_for"] = []
                print(f"  ✓ Added best_for (empty list)")
                changes = True
        elif tier == "bronze":
            if "modern_alternatives" not in metadata or not metadata["modern_alternatives"]:
                metadata["modern_alternatives"] = []
                print(f"  ✓ Added modern_alternatives (empty list)")
                changes = True
            if "deprecation_reason" not in metadata or not metadata["deprecation_reason"]:
                metadata["deprecation_reason"] = "Consider modern alternatives for new implementations"
                print(f"  ✓ Added deprecation_reason")
                changes = True
        
        return changes

    def fix_field_naming(self, metadata: Dict[str, Any]) -> bool:
        """Fix field naming inconsistencies (convert underscores to hyphens)."""
        changes = False
        
        # Fields that should keep underscores
        keep_underscores = {"excellence_tier", "pattern_status", "current_relevance"}
        
        # Create new metadata dict with corrected field names
        new_metadata = {}
        
        for key, value in metadata.items():
            if key in keep_underscores or '_' not in key:
                new_metadata[key] = value
            else:
                new_key = key.replace('_', '-')
                new_metadata[new_key] = value
                print(f"  ✓ Renamed field: {key} → {new_key}")
                changes = True
        
        if changes:
            metadata.clear()
            metadata.update(new_metadata)
        
        return changes

    def fix_pattern_file(self, file_path: Path) -> bool:
        """Fix a single pattern file."""
        print(f"\n🔧 Fixing {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  ❌ Could not read file: {e}")
            return False
        
        metadata, body = self.extract_frontmatter(content)
        
        if not metadata:
            print(f"  ⚠️  No frontmatter found")
            return False
        
        changes = False
        
        # Fix status values
        if self.fix_status_values(metadata):
            changes = True
        
        # Fix relevance values  
        if self.fix_relevance_values(metadata):
            changes = True
        
        # Add missing description
        if self.add_missing_description(metadata, file_path.name):
            changes = True
        
        # Add missing fields
        if self.add_missing_fields(metadata):
            changes = True
        
        # Fix field naming
        if self.fix_field_naming(metadata):
            changes = True
        
        if changes:
            try:
                new_content = self.write_frontmatter(metadata, body)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  ✅ File updated successfully")
                return True
            except Exception as e:
                print(f"  ❌ Could not write file: {e}")
                return False
        else:
            print(f"  ℹ️  No changes needed")
            return False

    def fix_all_patterns(self) -> Dict[str, int]:
        """Fix all pattern files in the pattern library."""
        pattern_files = [f for f in self.base_path.rglob("*.md") 
                        if f.name != "index.md" and "pattern-" not in f.name]
        
        stats = {
            "total_files": len(pattern_files),
            "files_modified": 0,
            "files_with_errors": 0
        }
        
        print(f"🚀 Starting pattern metadata fixes for {stats['total_files']} files...")
        
        for file_path in pattern_files:
            try:
                if self.fix_pattern_file(file_path):
                    stats["files_modified"] += 1
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
                stats["files_with_errors"] += 1
        
        return stats

def main():
    """Main fix function."""
    print("🔧 Pattern Metadata Fixer")
    print("=" * 50)
    
    fixer = PatternMetadataFixer()
    stats = fixer.fix_all_patterns()
    
    print(f"\n📊 SUMMARY")
    print(f"{'='*30}")
    print(f"Total files processed: {stats['total_files']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Files with errors: {stats['files_with_errors']}")
    print(f"Success rate: {((stats['total_files'] - stats['files_with_errors']) / stats['total_files'] * 100):.1f}%")
    
    if stats["files_modified"] > 0:
        print(f"\n✅ Fixed {stats['files_modified']} pattern files!")
        print("Run the validation script again to verify all fixes.")
    else:
        print(f"\nℹ️  No files needed modifications.")

if __name__ == "__main__":
    main()
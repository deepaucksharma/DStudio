#!/usr/bin/env python3
"""
Update Front Matter Script

Bulk updates pattern front matter to add excellence metadata.
Preserves existing content and creates backups before changes.
"""

import os
import re
import yaml
import shutil
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrontMatterUpdater:
    """Updates front matter in pattern markdown files"""
    
    def __init__(self, patterns_dir: Path, backup_dir: Optional[Path] = None):
        self.patterns_dir = patterns_dir
        self.backup_dir = backup_dir or patterns_dir / '.backups'
        
        # Default values for new fields
        self.field_defaults = {
            'excellence_tier': 'bronze',
            'pattern_status': 'use_with_caution',
            'introduced': '2010-01',
            'current_relevance': 'niche',
            'alternatives': [],
            'modern_examples': [],
            'production_checklist': []
        }
        
        # Load tier assignments if available
        self.tier_assignments = self._load_tier_assignments()
    
    def _load_tier_assignments(self) -> Dict[str, str]:
        """Load tier assignments from classification report if available"""
        assignments = {}
        
        # Check for classification report
        report_path = self.patterns_dir.parent.parent / 'pattern_classification_report.md'
        if report_path.exists():
            logger.info(f"Loading tier assignments from {report_path}")
            with open(report_path, 'r') as f:
                content = f.read()
            
            # Parse tier assignments from report
            current_pattern = None
            for line in content.split('\n'):
                if line.startswith('### ') and ('🏆' in line or '🥈' in line or '🥉' in line):
                    # Extract pattern name
                    pattern_match = re.match(r'### ([\w-]+)', line)
                    if pattern_match:
                        current_pattern = pattern_match.group(1)
                elif current_pattern and '**Recommended Tier**:' in line:
                    tier_match = re.search(r'\*\*Recommended Tier\*\*: (\w+)', line)
                    if tier_match:
                        assignments[current_pattern] = tier_match.group(1)
        
        return assignments
    
    def create_backup(self, file_path: Path) -> Path:
        """Create a backup of the file before modification"""
        # Create backup directory if needed
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{file_path.stem}_{timestamp}.md"
        backup_path = self.backup_dir / backup_name
        
        # Copy file to backup
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
        return backup_path
    
    def extract_front_matter(self, file_path: Path) -> Tuple[Dict, str, str]:
        """Extract front matter and content from markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has front matter
        if not content.startswith('---'):
            return {}, '', content
        
        # Find the closing ---
        end_match = re.search(r'^---$', content[3:], re.MULTILINE)
        if not end_match:
            return {}, '', content
        
        end_idx = end_match.start() + 3
        yaml_content = content[3:end_idx]
        body_content = content[end_idx+4:]  # Skip the closing --- and newline
        
        try:
            front_matter = yaml.safe_load(yaml_content) or {}
            return front_matter, yaml_content, body_content
        except yaml.YAMLError as e:
            logger.error(f"YAML parse error in {file_path}: {e}")
            return {}, '', content
    
    def update_front_matter(self, file_path: Path, updates: Dict[str, Any], 
                          preserve_existing: bool = True) -> bool:
        """Update front matter in a file"""
        try:
            # Extract current front matter
            front_matter, yaml_content, body_content = self.extract_front_matter(file_path)
            
            # Create new front matter
            if preserve_existing:
                # Merge updates with existing
                new_front_matter = front_matter.copy()
                new_front_matter.update(updates)
            else:
                # Replace entirely
                new_front_matter = updates
            
            # Format new front matter
            new_yaml = yaml.dump(new_front_matter, 
                               default_flow_style=False, 
                               sort_keys=False,
                               allow_unicode=True)
            
            # Reconstruct file content
            new_content = f"---\n{new_yaml}---\n{body_content}"
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating {file_path}: {e}")
            return False
    
    def add_excellence_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Add excellence metadata to a pattern file"""
        pattern_name = file_path.stem
        front_matter, _, _ = self.extract_front_matter(file_path)
        
        updates = {}
        
        # Add excellence tier if missing
        if 'excellence_tier' not in front_matter:
            # Check if we have a tier assignment from classification
            if pattern_name in self.tier_assignments:
                updates['excellence_tier'] = self.tier_assignments[pattern_name]
            else:
                updates['excellence_tier'] = self.field_defaults['excellence_tier']
        
        # Add pattern status if missing
        if 'pattern_status' not in front_matter:
            # Determine status based on tier
            tier = updates.get('excellence_tier', front_matter.get('excellence_tier', 'bronze'))
            if tier == 'gold':
                updates['pattern_status'] = 'recommended'
            elif tier == 'silver':
                updates['pattern_status'] = 'recommended'
            else:
                updates['pattern_status'] = 'use_with_caution'
        
        # Add introduced date if missing
        if 'introduced' not in front_matter:
            # Try to infer from pattern name or use default
            known_dates = {
                'gang-of-four': '1994-10',
                'enterprise-integration': '2003-10',
                'microservices': '2014-03',
                'event-sourcing': '2005-01',
                'cqrs': '2010-01',
                'saga-pattern': '1987-01',
                'circuit-breaker': '2007-01',
                'bulkhead': '2007-01',
                'service-mesh': '2017-01',
                'serverless': '2014-11',
                'event-driven': '2003-01',
                'domain-driven': '2003-08'
            }
            
            for key, date in known_dates.items():
                if key in pattern_name.lower():
                    updates['introduced'] = date
                    break
            else:
                updates['introduced'] = self.field_defaults['introduced']
        
        # Add current relevance if missing
        if 'current_relevance' not in front_matter:
            tier = updates.get('excellence_tier', front_matter.get('excellence_tier', 'bronze'))
            if tier == 'gold':
                updates['current_relevance'] = 'mainstream'
            elif tier == 'silver':
                updates['current_relevance'] = 'growing'
            else:
                updates['current_relevance'] = 'niche'
        
        # Add empty arrays for tier-specific fields if missing
        tier = updates.get('excellence_tier', front_matter.get('excellence_tier', 'bronze'))
        
        if tier == 'bronze' and 'alternatives' not in front_matter:
            updates['alternatives'] = []
        
        if tier in ['gold', 'silver'] and 'modern_examples' not in front_matter:
            updates['modern_examples'] = []
        
        if tier == 'gold' and 'production_checklist' not in front_matter:
            updates['production_checklist'] = []
        
        return updates
    
    def update_pattern(self, file_path: Path, dry_run: bool = False) -> bool:
        """Update a single pattern file"""
        pattern_name = file_path.stem
        logger.info(f"Processing pattern: {pattern_name}")
        
        # Determine updates needed
        updates = self.add_excellence_metadata(file_path)
        
        if not updates:
            logger.info(f"  No updates needed for {pattern_name}")
            return True
        
        logger.info(f"  Updates needed: {list(updates.keys())}")
        
        if dry_run:
            logger.info(f"  [DRY RUN] Would update with: {updates}")
            return True
        
        # Create backup
        backup_path = self.create_backup(file_path)
        
        # Apply updates
        success = self.update_front_matter(file_path, updates)
        
        if success:
            logger.info(f"  ✅ Successfully updated {pattern_name}")
        else:
            logger.error(f"  ❌ Failed to update {pattern_name}")
            # Restore from backup on failure
            shutil.copy2(backup_path, file_path)
            logger.info(f"  Restored from backup")
        
        return success
    
    def update_all_patterns(self, dry_run: bool = False) -> Dict[str, bool]:
        """Update all patterns in the directory"""
        results = {}
        
        # Find all pattern markdown files
        pattern_files = list(self.patterns_dir.glob('*.md'))
        pattern_files = [f for f in pattern_files if f.stem not in ['index', 'README']]
        
        logger.info(f"Found {len(pattern_files)} patterns to process")
        
        for pattern_file in pattern_files:
            success = self.update_pattern(pattern_file, dry_run)
            results[pattern_file.stem] = success
        
        return results
    
    def generate_update_report(self, results: Dict[str, bool], output_file: Path):
        """Generate report of updates performed"""
        successful = [name for name, success in results.items() if success]
        failed = [name for name, success in results.items() if not success]
        
        report_lines = [
            "# Front Matter Update Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- **Total Patterns**: {len(results)}",
            f"- **Successfully Updated**: {len(successful)}",
            f"- **Failed**: {len(failed)}",
            ""
        ]
        
        if successful:
            report_lines.extend([
                "## ✅ Successfully Updated",
                ""
            ])
            for name in sorted(successful):
                report_lines.append(f"- {name}")
            report_lines.append("")
        
        if failed:
            report_lines.extend([
                "## ❌ Failed Updates",
                ""
            ])
            for name in sorted(failed):
                report_lines.append(f"- {name}")
            report_lines.append("")
        
        # Write report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Update report generated: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Update pattern front matter with excellence metadata')
    parser.add_argument('--patterns-dir', type=Path, default=Path('docs/patterns'),
                       help='Directory containing pattern markdown files')
    parser.add_argument('--backup-dir', type=Path,
                       help='Directory for backups (default: patterns-dir/.backups)')
    parser.add_argument('--pattern', help='Update a specific pattern only')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be updated without making changes')
    parser.add_argument('--output', type=Path, default=Path('front_matter_update_report.md'),
                       help='Output report file')
    parser.add_argument('--tier-assignments', type=Path,
                       help='JSON file with pattern tier assignments')
    
    args = parser.parse_args()
    
    # Ensure patterns directory exists
    if not args.patterns_dir.exists():
        logger.error(f"Patterns directory not found: {args.patterns_dir}")
        return 1
    
    # Initialize updater
    updater = FrontMatterUpdater(args.patterns_dir, args.backup_dir)
    
    # Load custom tier assignments if provided
    if args.tier_assignments and args.tier_assignments.exists():
        with open(args.tier_assignments, 'r') as f:
            updater.tier_assignments.update(json.load(f))
    
    # Update patterns
    if args.pattern:
        # Single pattern
        pattern_file = args.patterns_dir / f"{args.pattern}.md"
        if not pattern_file.exists():
            logger.error(f"Pattern file not found: {pattern_file}")
            return 1
        
        success = updater.update_pattern(pattern_file, args.dry_run)
        
        if args.dry_run:
            print("\n[DRY RUN] No changes were made.")
        else:
            print(f"\nUpdate {'successful' if success else 'failed'} for {args.pattern}")
    else:
        # All patterns
        results = updater.update_all_patterns(args.dry_run)
        
        if not args.dry_run:
            updater.generate_update_report(results, args.output)
        
        # Print summary
        successful = sum(1 for success in results.values() if success)
        print(f"\nUpdate complete:")
        print(f"  Patterns processed: {len(results)}")
        print(f"  Successfully updated: {successful}")
        print(f"  Failed: {len(results) - successful}")
        
        if args.dry_run:
            print("\n[DRY RUN] No changes were made.")
        else:
            print(f"\nBackups saved to: {updater.backup_dir}")
            print(f"Report saved to: {args.output}")
    
    return 0

if __name__ == '__main__':
    exit(main())
#!/usr/bin/env python3
"""
Organize scripts into logical subdirectories based on functionality.
This script analyzes and moves scripts to appropriate folders.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Script categorization based on analysis
SCRIPT_CATEGORIES = {
    'link-management': [
        'comprehensive_link_analysis.py',
        'fix_all_link_issues.py',
        'check-broken-links.py',
        'fix-broken-links.py',
        'analyze-unrecognized-links.py',
        'validate_all_links.py',
        'fix-absolute-links.py',
        'fix-common-link-issues.py',
        'fix_link_normalization.py',
        'comprehensive_link_fixes.py',
        'final_link_fixes.py',
    ],
    
    'pattern-library': [
        'pattern-manager.py',
        'comprehensive-pattern-validator.py',
        'template_v2_transformer.py',
        'template_v2_transformer_enhanced.py',
        'pattern-classifier.py',
        'pattern_validator.py',
        'analyze-patterns.py',
        'pattern-validator-metadata.py',
        'pattern_transformation_tracker.py',
        'tier_section_validator.py',
        'fix-pattern-library-categories.py',
        'create_remaining_patterns.py',
        'generate-comparison-matrix.py',
    ],
    
    'validation': [
        'mkdocs-validator.py',
        'final_validation.py',
        'validate-frontmatter.py',
        'validate_content.py',
        'validate-law-references.py',
        'validate-paths.py',
        'comprehensive-structural-fix.py',
        'check_duplicates.py',
        'comprehensive_metadata_summary.py',
    ],
    
    'navigation': [
        'final_navigation_fix.py',
        'comprehensive_navigation_fix.py',
        'analyze_navigation_issues.py',
        'simple_nav_check.py',
        'validate_navigation.py',
        'fix_navigation_404s.py',
        'create_redirect_map.py',
    ],
    
    'content-generation': [
        'create_missing_files.py',
        'create_missing_handbook_files.py',
        'add-missing-frontmatter.py',
        'add-missing-descriptions.py',
        'create-leadership-content.py',
        'create-leadership-interview-structure.py',
        'create-missing-directories.py',
        'add-orphaned-files.py',
        'add-existing-orphaned-files.py',
        'add-law-pattern-references.py',
        'fix-frontmatter-consistency.py',
        'update-front-matter.py',
    ],
    
    'visual-assets': [
        'extract_mermaid_diagrams.py',
        'render_mermaid_diagrams.py',
        'replace_mermaid_blocks.py',
        'monitor_diagram_conversion.py',
    ],
    
    'archive': [
        # One-time migration scripts
        'fix_deployed_broken_links.py',
        'fix_learning_paths.py',
        'fix_metadata_issues.py',
        'remove-broken-additions.py',
        'continue-cleanup.py',
        'synthesize-cleanup.py',
        'fix_all_404s.py',
        'fix_duplicates.py',
        'cleanup-project.py',
        'ultra-comprehensive-fix.py',
        'deep-structure-analyzer.py',
        'fix_admonitions.py',  # Specific fix that's been applied
        'fix_broken_links.py',  # Superseded by comprehensive versions
    ]
}

# Shell scripts to keep in main directory
SHELL_SCRIPTS = [
    'validate-all.sh',
    'quick_pattern_check.sh',
    'pre-commit-pattern-validation.sh',
    'pre-commit-navigation-check.sh',
    'setup_diagram_tools.sh',
    'check_links.sh',
    'validate-pattern-counts.sh',
]

# Files to keep in main directory
KEEP_IN_MAIN = [
    'README.md',
    'README-validation.md',
    'pattern-validation-tools.md',
    'SCRIPT_INVENTORY.md',
    'organize_scripts.py',  # This script itself
]


def categorize_uncategorized(scripts_dir: Path) -> List[str]:
    """Find scripts not yet categorized."""
    all_scripts = set(f.name for f in scripts_dir.glob('*.py'))
    all_scripts.update(f.name for f in scripts_dir.glob('*.sh'))
    
    categorized = set()
    for scripts in SCRIPT_CATEGORIES.values():
        categorized.update(scripts)
    categorized.update(SHELL_SCRIPTS)
    categorized.update(KEEP_IN_MAIN)
    
    # Already moved to subdirectories
    moved_patterns = {'knowledge_graph_', 'query_knowledge', 'test_knowledge'}
    uncategorized = []
    
    for script in all_scripts:
        if script not in categorized:
            if not any(pattern in script for pattern in moved_patterns):
                uncategorized.append(script)
    
    return sorted(uncategorized)


def move_scripts(dry_run: bool = True) -> Dict[str, List[Tuple[str, str]]]:
    """Move scripts to their designated subdirectories."""
    scripts_dir = Path('/home/deepak/DStudio/scripts')
    moves = {}
    
    for category, scripts in SCRIPT_CATEGORIES.items():
        moves[category] = []
        target_dir = scripts_dir / category
        
        for script in scripts:
            source = scripts_dir / script
            target = target_dir / script
            
            if source.exists():
                moves[category].append((str(source), str(target)))
                if not dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(target))
                    print(f"Moved {script} -> {category}/")
    
    return moves


def main():
    """Main execution."""
    scripts_dir = Path('/home/deepak/DStudio/scripts')
    
    print("=" * 60)
    print("Script Organization Plan")
    print("=" * 60)
    
    # Find uncategorized scripts
    uncategorized = categorize_uncategorized(scripts_dir)
    if uncategorized:
        print("\n⚠️  Uncategorized scripts found:")
        for script in uncategorized:
            print(f"  - {script}")
    
    # Show planned moves
    print("\n📁 Planned directory structure:")
    moves = move_scripts(dry_run=True)
    
    for category, script_moves in moves.items():
        if script_moves:
            print(f"\n{category}/ ({len(script_moves)} scripts)")
            for source, target in script_moves[:3]:  # Show first 3
                print(f"  - {Path(source).name}")
            if len(script_moves) > 3:
                print(f"  ... and {len(script_moves) - 3} more")
    
    print("\n" + "=" * 60)
    
    # Ask for confirmation
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--yes':
        response = 'yes'
    else:
        try:
            response = input("\nProceed with organization? (yes/no): ")
        except EOFError:
            response = 'no'
    
    if response.lower() in ['yes', 'y']:
        print("\n🚀 Organizing scripts...")
        moves = move_scripts(dry_run=False)
        
        total_moved = sum(len(m) for m in moves.values())
        print(f"\n✅ Successfully organized {total_moved} scripts")
        
        # Create category READMEs
        for category in SCRIPT_CATEGORIES.keys():
            readme_path = scripts_dir / category / 'README.md'
            if not readme_path.exists():
                with open(readme_path, 'w') as f:
                    f.write(f"# {category.replace('-', ' ').title()} Scripts\n\n")
                    f.write(f"Scripts for {category.replace('-', ' ')} operations.\n\n")
                    f.write("See ../SCRIPT_INVENTORY.md for detailed documentation.\n")
        
        print("✅ Created README files in each category")
    else:
        print("❌ Organization cancelled")


if __name__ == "__main__":
    main()
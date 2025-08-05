#!/usr/bin/env python3
"""Fix the final remaining old references."""

from pathlib import Path
import re

def fix_final_issues():
    """Fix the last remaining old references."""
    docs_dir = Path("docs")
    
    # Specific fixes needed
    fixes = {
        'law2-async': 'asynchronous-reality',
        'law5-knowledge': 'distributed-knowledge',
        'law6-cognitive-load': 'cognitive-load',
        'law4-tradeoffs': 'multidimensional-optimization',
        'law5-epistemology': 'distributed-knowledge',
        'law7-economics': 'economic-reality',
        'law1-failure': 'correlated-failure',
        'law2-asynchrony': 'asynchronous-reality',
    }
    
    files_to_fix = [
        "pattern-library/coordination/distributed-lock.md",
        "pattern-library/coordination/leader-election.md",
        "pattern-library/data-management/read-repair.md",
        "pattern-library/data-management/data-lake.md",
        "pattern-library/data-management/bloom-filter.md",
        "pattern-library/data-management/merkle-trees.md",
        "pattern-library/data-management/delta-sync.md",
        "reference/pattern-template.md",
    ]
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        full_path = docs_dir / file_path
        if not full_path.exists():
            continue
            
        content = full_path.read_text()
        original = content
        
        # Fix all occurrences
        for old_ref, new_ref in fixes.items():
            # In links
            content = content.replace(f'/laws/{old_ref}/', f'/laws/{new_ref}/')
            content = content.replace(f'{old_ref})', f'{new_ref})')
            # In tags
            content = re.sub(f'^(\\s*- ){old_ref}$', f'\\1{new_ref}', content, flags=re.MULTILINE)
            # In related_laws
            content = content.replace(f'[{old_ref}', f'[{new_ref}')
        
        if content != original:
            full_path.write_text(content)
            print(f"Fixed: {file_path}")
            fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    fix_final_issues()
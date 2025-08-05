#!/usr/bin/env python3
"""Fix all law tags in frontmatter and remaining references."""

import re
import yaml
from pathlib import Path

def fix_law_tags(tags):
    """Fix law tags in frontmatter."""
    if not tags:
        return tags
    
    tag_mappings = {
        'law1-failure': 'correlated-failure',
        'law2-asynchrony': 'asynchronous-reality',
        'law3-chaos': 'emergent-chaos',
        'law3-emergence': 'emergent-chaos',
        'law4-tradeoffs': 'multidimensional-optimization',
        'law5-epistemology': 'distributed-knowledge',
        'law6-load': 'cognitive-load',
        'law7-economics': 'economic-reality',
        'part1-axioms': 'laws',
    }
    
    fixed_tags = []
    for tag in tags:
        if tag in tag_mappings:
            fixed_tags.append(tag_mappings[tag])
        else:
            fixed_tags.append(tag)
    
    return fixed_tags

def fix_content_references(content):
    """Fix all remaining references in content."""
    # Fix frontmatter tags
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                if frontmatter and 'tags' in frontmatter:
                    frontmatter['tags'] = fix_law_tags(frontmatter['tags'])
                    
                # Rebuild content
                new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
                content = f"---\n{new_frontmatter}---{parts[2]}"
            except:
                pass
    
    # Fix all path references
    replacements = [
        # Part1-axioms to core-principles/laws
        ('../../part1-axioms/law1-failure/', '../../core-principles/laws/correlated-failure/'),
        ('../../part1-axioms/law2-asynchrony/', '../../core-principles/laws/asynchronous-reality/'),
        ('../../part1-axioms/law3-chaos/', '../../core-principles/laws/emergent-chaos/'),
        ('../../part1-axioms/law3-emergence/', '../../core-principles/laws/emergent-chaos/'),
        ('../../part1-axioms/law4-tradeoffs/', '../../core-principles/laws/multidimensional-optimization/'),
        ('../../part1-axioms/law5-epistemology/', '../../core-principles/laws/distributed-knowledge/'),
        ('../../part1-axioms/law6-load/', '../../core-principles/laws/cognitive-load/'),
        ('../../part1-axioms/law7-economics/', '../../core-principles/laws/economic-reality/'),
        
        # Without trailing slash
        ('../../part1-axioms/law1-failure', '../../core-principles/laws/correlated-failure'),
        ('../../part1-axioms/law2-asynchrony', '../../core-principles/laws/asynchronous-reality'),
        ('../../part1-axioms/law3-chaos', '../../core-principles/laws/emergent-chaos'),
        ('../../part1-axioms/law3-emergence', '../../core-principles/laws/emergent-chaos'),
        ('../../part1-axioms/law4-tradeoffs', '../../core-principles/laws/multidimensional-optimization'),
        ('../../part1-axioms/law5-epistemology', '../../core-principles/laws/distributed-knowledge'),
        ('../../part1-axioms/law6-load', '../../core-principles/laws/cognitive-load'),
        ('../../part1-axioms/law7-economics', '../../core-principles/laws/economic-reality'),
        
        # Fix general part1-axioms references
        ('../part1-axioms/', '../core-principles/laws/'),
        ('../../part1-axioms/', '../../core-principles/laws/'),
        
        # Fix pillar references
        ('/part2-pillars/', '/core-principles/pillars/'),
        ('../../part2-pillars/', '../../core-principles/pillars/'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    return content

def fix_macros_py():
    """Fix the macros.py file specifically."""
    macros_file = Path("docs/macros.py")
    if macros_file.exists():
        content = macros_file.read_text()
        # Fix the law reference function
        content = content.replace(
            "return f'[Law {number}: {name}](../part1-axioms/law{number}-{name.lower().replace(\" \", \"-\")}/)'"
            ,
            "return f'[Law {number}: {name}](../core-principles/laws/{get_law_slug(number, name)}/)'"
        )
        
        # Add helper function if needed
        if "def get_law_slug" not in content:
            helper = '''
def get_law_slug(number, name):
    """Get the correct slug for a law."""
    law_slugs = {
        1: "correlated-failure",
        2: "asynchronous-reality",
        3: "emergent-chaos",
        4: "multidimensional-optimization",
        5: "distributed-knowledge",
        6: "cognitive-load",
        7: "economic-reality"
    }
    return law_slugs.get(number, name.lower().replace(" ", "-"))

'''
            # Insert after imports
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('def '):
                    lines.insert(i, helper)
                    break
            content = '\n'.join(lines)
        
        macros_file.write_text(content)
        print("Fixed: macros.py")

def main():
    """Fix all law references comprehensively."""
    docs_dir = Path("docs")
    fixed_count = 0
    
    # First fix macros.py
    fix_macros_py()
    
    # Then fix all markdown files
    for md_file in docs_dir.glob("**/*.md"):
        try:
            content = md_file.read_text()
            original_content = content
            
            content = fix_content_references(content)
            
            if content != original_content:
                md_file.write_text(content)
                fixed_count += 1
                print(f"Fixed: {md_file.relative_to(docs_dir)}")
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    # Also fix .meta.yml
    meta_file = docs_dir / ".meta.yml"
    if meta_file.exists():
        try:
            content = meta_file.read_text()
            original_content = content
            
            content = fix_content_references(content)
            
            if content != original_content:
                meta_file.write_text(content)
                fixed_count += 1
                print("Fixed: .meta.yml")
        except Exception as e:
            print(f"Error processing .meta.yml: {e}")
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
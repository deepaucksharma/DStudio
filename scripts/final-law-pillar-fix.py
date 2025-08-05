#!/usr/bin/env python3
"""Final comprehensive fix for all law and pillar references."""

import re
import yaml
from pathlib import Path

def fix_frontmatter_comprehensively(content):
    """Fix all frontmatter issues comprehensively."""
    if not content.startswith('---'):
        return content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return content
    
    try:
        frontmatter = yaml.safe_load(parts[1])
        if not frontmatter:
            return content
        
        # Fix tags
        if 'tags' in frontmatter:
            tag_mappings = {
                'law1-failure': 'correlated-failure',
                'law2-asynchrony': 'asynchronous-reality',
                'law3-chaos': 'emergent-chaos',
                'law3-emergence': 'emergent-chaos',
                'law4-tradeoffs': 'multidimensional-optimization',
                'law5-epistemology': 'distributed-knowledge',
                'law6-load': 'cognitive-load',
                'law6-human-api': 'cognitive-load',
                'law7-economics': 'economic-reality',
                'part1-axioms': 'laws',
                'part2-pillars': 'pillars',
            }
            
            if isinstance(frontmatter['tags'], list):
                new_tags = []
                for tag in frontmatter['tags']:
                    # Remove path-like tags
                    if '/' in tag:
                        base_tag = tag.split('/')[-1]
                        if base_tag in tag_mappings:
                            new_tags.append(tag_mappings[base_tag])
                        elif base_tag.startswith('law') and '-' in base_tag:
                            # Extract law name
                            parts = base_tag.split('-', 1)
                            if len(parts) > 1 and parts[1] in ['failure', 'asynchrony', 'chaos', 'emergence', 'tradeoffs', 'epistemology', 'load', 'human-api', 'economics']:
                                mapped = tag_mappings.get(base_tag, base_tag)
                                new_tags.append(mapped)
                    else:
                        new_tags.append(tag_mappings.get(tag, tag))
                frontmatter['tags'] = new_tags
        
        # Fix prerequisites
        if 'prerequisites' in frontmatter:
            if isinstance(frontmatter['prerequisites'], list):
                new_prereqs = []
                for prereq in frontmatter['prerequisites']:
                    if 'part1-axioms' in prereq:
                        prereq = prereq.replace('part1-axioms/law1-failure', 'core-principles/laws/correlated-failure')
                        prereq = prereq.replace('part1-axioms/law2-asynchrony', 'core-principles/laws/asynchronous-reality')
                        prereq = prereq.replace('part1-axioms/law3-chaos', 'core-principles/laws/emergent-chaos')
                        prereq = prereq.replace('part1-axioms/law4-tradeoffs', 'core-principles/laws/multidimensional-optimization')
                        prereq = prereq.replace('part1-axioms/law5-epistemology', 'core-principles/laws/distributed-knowledge')
                        prereq = prereq.replace('part1-axioms/law6-load', 'core-principles/laws/cognitive-load')
                        prereq = prereq.replace('part1-axioms/law6-human-api', 'core-principles/laws/cognitive-load')
                        prereq = prereq.replace('part1-axioms/law7-economics', 'core-principles/laws/economic-reality')
                    if 'part2-pillars' in prereq:
                        prereq = prereq.replace('part2-pillars', 'core-principles/pillars')
                    new_prereqs.append(prereq)
                frontmatter['prerequisites'] = new_prereqs
        
        # Rebuild content
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return f"---\n{new_frontmatter}---{parts[2]}"
    except Exception as e:
        print(f"Error processing frontmatter: {e}")
        return content

def fix_macros_pillars(content):
    """Fix pillar references in macros.py."""
    content = content.replace(
        "return f'[Pillar {number}: {name}](../part2-pillars/{name.lower()}/)'"
        ,
        "return f'[Pillar {number}: {name}](../core-principles/pillars/{name.lower().replace(\" \", \"-\")}/)'"
    )
    return content

def main():
    """Final comprehensive fix."""
    docs_dir = Path("docs")
    fixed_count = 0
    
    # Fix macros.py
    macros_file = docs_dir / "macros.py"
    if macros_file.exists():
        content = macros_file.read_text()
        original = content
        content = fix_macros_pillars(content)
        if content != original:
            macros_file.write_text(content)
            print("Fixed: macros.py (pillars)")
            fixed_count += 1
    
    # Fix all markdown files with frontmatter issues
    target_files = [
        "architects-handbook/human-factors/observability-stacks.md",
        "architects-handbook/human-factors/sre-practices.md",
        "architects-handbook/human-factors/chaos-engineering.md",
        "architects-handbook/human-factors/consistency-tuning.md",
        "architects-handbook/human-factors/incident-response.md",
        "architects-handbook/human-factors/blameless-postmortems.md",
    ]
    
    # Also scan all files for any remaining issues
    for md_file in docs_dir.glob("**/*.md"):
        try:
            content = md_file.read_text()
            original = content
            
            # Fix frontmatter
            content = fix_frontmatter_comprehensively(content)
            
            # Fix any remaining text references
            content = content.replace('part1-axioms/', 'core-principles/laws/')
            content = content.replace('part2-pillars/', 'core-principles/pillars/')
            
            if content != original:
                md_file.write_text(content)
                fixed_count += 1
                print(f"Fixed: {md_file.relative_to(docs_dir)}")
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
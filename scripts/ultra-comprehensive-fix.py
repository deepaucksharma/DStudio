#!/usr/bin/env python3
"""Ultra comprehensive fix for ALL remaining law/pillar references."""

import re
import yaml
from pathlib import Path

def fix_all_patterns(content, file_path):
    """Fix all possible patterns of old references."""
    
    # Fix law references with /index suffix
    replacements = [
        # With /index
        ('../../core-principles/laws/law1-failure/index', '../../core-principles/laws/correlated-failure'),
        ('../../core-principles/laws/law2-asynchrony/index', '../../core-principles/laws/asynchronous-reality'),
        ('../../core-principles/laws/law3-chaos/index', '../../core-principles/laws/emergent-chaos'),
        ('../../core-principles/laws/law4-tradeoffs/index', '../../core-principles/laws/multidimensional-optimization'),
        ('../../core-principles/laws/law5-epistemology/index', '../../core-principles/laws/distributed-knowledge'),
        ('../../core-principles/laws/law6-load/index', '../../core-principles/laws/cognitive-load'),
        ('../../core-principles/laws/law7-economics/index', '../../core-principles/laws/economic-reality'),
        
        # Without ../../
        ('../core-principles/laws/law1-failure/index', '../core-principles/laws/correlated-failure'),
        ('../core-principles/laws/law2-asynchrony/index', '../core-principles/laws/asynchronous-reality'),
        ('../core-principles/laws/law1-failure', '../core-principles/laws/correlated-failure'),
        ('../core-principles/laws/law2-asynchrony', '../core-principles/laws/asynchronous-reality'),
        
        # In prerequisites
        ('core-principles/laws/law2-asynchrony', 'core-principles/laws/asynchronous-reality'),
        ('core-principles/laws/law4-tradeoffs', 'core-principles/laws/multidimensional-optimization'),
        
        # Tags in frontmatter (handled separately)
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Fix .meta.yml patterns
    if file_path.name == '.meta.yml':
        content = content.replace('part1-axioms:', 'laws:')
        content = content.replace('part2-pillars:', 'pillars:')
    
    return content

def fix_frontmatter_tags(content):
    """Fix tags in frontmatter."""
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
        if 'tags' in frontmatter and isinstance(frontmatter['tags'], list):
            new_tags = []
            for tag in frontmatter['tags']:
                if tag == 'law1-failure':
                    new_tags.append('correlated-failure')
                elif tag == 'law2-asynchrony':
                    new_tags.append('asynchronous-reality')
                elif tag == 'law3-chaos' or tag == 'law3-emergence':
                    new_tags.append('emergent-chaos')
                elif tag == 'law4-tradeoffs':
                    new_tags.append('multidimensional-optimization')
                elif tag == 'law5-epistemology':
                    new_tags.append('distributed-knowledge')
                elif tag == 'law6-load' or tag == 'law6-human-api':
                    new_tags.append('cognitive-load')
                elif tag == 'law7-economics':
                    new_tags.append('economic-reality')
                else:
                    new_tags.append(tag)
            frontmatter['tags'] = new_tags
        
        # Fix prerequisites
        if 'prerequisites' in frontmatter:
            if isinstance(frontmatter['prerequisites'], list):
                new_prereqs = []
                for prereq in frontmatter['prerequisites']:
                    prereq = fix_all_patterns(prereq, Path('dummy'))
                    new_prereqs.append(prereq)
                frontmatter['prerequisites'] = new_prereqs
        
        # Rebuild
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return f"---\n{new_frontmatter}---{parts[2]}"
    except:
        # If YAML parsing fails, do simple string replacement
        frontmatter_text = parts[1]
        frontmatter_text = frontmatter_text.replace('law1-failure', 'correlated-failure')
        frontmatter_text = frontmatter_text.replace('law2-asynchrony', 'asynchronous-reality')
        frontmatter_text = frontmatter_text.replace('law3-chaos', 'emergent-chaos')
        frontmatter_text = frontmatter_text.replace('law3-emergence', 'emergent-chaos')
        frontmatter_text = frontmatter_text.replace('law4-tradeoffs', 'multidimensional-optimization')
        frontmatter_text = frontmatter_text.replace('law5-epistemology', 'distributed-knowledge')
        frontmatter_text = frontmatter_text.replace('law6-load', 'cognitive-load')
        frontmatter_text = frontmatter_text.replace('law6-human-api', 'cognitive-load')
        frontmatter_text = frontmatter_text.replace('law7-economics', 'economic-reality')
        return f"---{frontmatter_text}---{parts[2]}"

def main():
    """Ultra comprehensive fix."""
    docs_dir = Path("docs")
    fixed_count = 0
    
    # Process all files
    for file_path in docs_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix in ['.md', '.yml', '.yaml']:
            try:
                content = file_path.read_text()
                original = content
                
                # Fix frontmatter first
                if file_path.suffix == '.md':
                    content = fix_frontmatter_tags(content)
                
                # Then fix all patterns
                content = fix_all_patterns(content, file_path)
                
                if content != original:
                    file_path.write_text(content)
                    fixed_count += 1
                    print(f"Fixed: {file_path.relative_to(docs_dir)}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
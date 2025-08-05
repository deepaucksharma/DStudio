#!/usr/bin/env python3
"""Add missing frontmatter to markdown files."""

import os
import re
from pathlib import Path

def get_title_from_content(content):
    """Extract title from first heading in content."""
    # Look for first # heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Untitled"

def get_description_from_content(content, title):
    """Generate description from content."""
    # Remove frontmatter if exists
    content_no_fm = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    
    # Get first paragraph after title
    lines = content_no_fm.split('\n')
    description_lines = []
    found_content = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if found_content and description_lines:
                break
            continue
        if line.startswith('#'):
            found_content = True
            continue
        if found_content and not line.startswith('!') and not line.startswith('<'):
            description_lines.append(line)
            if len(' '.join(description_lines)) > 100:
                break
    
    description = ' '.join(description_lines)[:150].strip()
    if not description:
        description = f"Documentation for {title}"
    
    return description

def determine_type(filepath):
    """Determine document type from path."""
    path_str = str(filepath).lower()
    
    if 'pattern-library' in path_str:
        return 'pattern'
    elif 'case-studies' in path_str or 'case-study' in path_str:
        return 'case-study'
    elif 'learning-path' in path_str:
        return 'learning-path'
    elif 'laws' in path_str and 'index.md' not in path_str:
        return 'law'
    elif 'pillars' in path_str and 'index.md' not in path_str:
        return 'pillar'
    elif 'interview' in path_str:
        return 'interview-guide'
    elif 'reference' in path_str:
        return 'reference'
    elif 'guide' in path_str or 'playbook' in path_str:
        return 'guide'
    else:
        return 'documentation'

def determine_difficulty(filepath, content):
    """Determine difficulty level."""
    path_str = str(filepath).lower()
    
    if 'beginner' in path_str or 'introduction' in path_str or 'getting-started' in path_str:
        return 'beginner'
    elif 'advanced' in path_str or 'expert' in path_str:
        return 'advanced'
    elif 'intermediate' in path_str:
        return 'intermediate'
    
    # Check content complexity
    complex_terms = ['distributed consensus', 'byzantine', 'paxos', 'raft', 'vector clock', 'crdt', 'cap theorem']
    content_lower = content.lower()
    complex_count = sum(1 for term in complex_terms if term in content_lower)
    
    if complex_count >= 3:
        return 'advanced'
    elif complex_count >= 1:
        return 'intermediate'
    else:
        return 'beginner'

def estimate_reading_time(content):
    """Estimate reading time based on word count."""
    words = len(re.findall(r'\w+', content))
    # Average reading speed: 200 words per minute
    minutes = max(1, round(words / 200))
    return f"{minutes} min"

def add_frontmatter(filepath):
    """Add frontmatter to a file if missing."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if frontmatter exists
    if content.startswith('---'):
        return False
    
    # Generate frontmatter fields
    title = get_title_from_content(content)
    description = get_description_from_content(content, title)
    doc_type = determine_type(filepath)
    difficulty = determine_difficulty(filepath, content)
    reading_time = estimate_reading_time(content)
    
    # Build frontmatter
    frontmatter = f"""---
title: {title}
description: {description}
type: {doc_type}
"""
    
    # Add type-specific fields
    if doc_type in ['law', 'pillar', 'pattern', 'case-study', 'learning-path']:
        frontmatter += f"difficulty: {difficulty}\n"
        frontmatter += f"reading_time: {reading_time}\n"
    
    if doc_type == 'pattern':
        # Add pattern-specific fields with defaults
        frontmatter += """excellence_tier: silver
pattern_status: use-with-expertise
"""
    
    frontmatter += "---\n\n"
    
    # Write updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)
    
    return True

def main():
    """Add missing frontmatter to all markdown files."""
    docs_dir = Path('docs')
    updated = 0
    skipped = 0
    
    # Files to skip
    skip_patterns = ['README.md', 'CHANGELOG.md', 'CODE_OF_CONDUCT.md']
    
    for md_file in docs_dir.rglob('*.md'):
        # Skip certain files
        if any(pattern in md_file.name for pattern in skip_patterns):
            skipped += 1
            continue
        
        if add_frontmatter(md_file):
            print(f"✅ Added frontmatter to: {md_file.relative_to(docs_dir)}")
            updated += 1
        else:
            skipped += 1
    
    print(f"\n📊 Summary:")
    print(f"  - Files updated: {updated}")
    print(f"  - Files skipped: {skipped}")

if __name__ == '__main__':
    main()
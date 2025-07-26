#!/usr/bin/env python3
"""
Fix final remaining pattern issues.
"""

import os
import re
import sys

def fix_law_references(content):
    """Fix incorrect law references."""
    replacements = [
        # Fix law2-async -> law2-asynchrony
        (r'/part1-axioms/law2-async/', '/part1-axioms/law2-asynchrony/'),
        (r'\.\./law2-async/', '../law2-asynchrony/'),
        
        # Fix law6-cognitive -> law6-human-api
        (r'/part1-axioms/law6-cognitive/', '/part1-axioms/law6-human-api/'),
        (r'\.\./law6-cognitive/', '../law6-human-api/'),
        
        # Fix human-factors paths that are incorrectly nested
        (r'/part1-axioms/human-factors/sre-practices', '/human-factors/sre-practices'),
        (r'/part1-axioms/human-factors/chaos-engineering', '/human-factors/chaos-engineering'),
    ]
    
    for old, new in replacements:
        content = re.sub(old, new, content)
    
    return content

def fix_google_interview_paths(content, file_path):
    """Fix paths in google-interviews that use ../../patterns/."""
    if 'google-interviews' in file_path:
        # These should be /patterns/ not ../../patterns/
        content = re.sub(r'\]\(../../patterns/([^)]+)\)', r'](/patterns/\1)', content)
        content = re.sub(r'\]\(../../quantitative/([^)]+)\)', r'](/quantitative/\1)', content)
        content = re.sub(r'\]\(../../case-studies/([^)]+)\)', r'](/case-studies/\1)', content)
    
    return content

def fix_malformed_patterns(content):
    """Fix specific malformed patterns."""
    # Fix "event, context" which appears to be a function parameter mistaken for a link
    content = re.sub(r'\[([^\]]+)\]\([^)]*event, context[^)]*\)', r'\1', content)
    
    # Fix regex patterns in links
    content = re.sub(r'\[([^\]]+)\]\([^)]*\[\^"\'\]\+[^)]*\)', r'\1', content)
    
    # Fix template variables like {user_id}, {self}, etc.
    content = re.sub(r'\[([^\]]+)\]\([^)]*\{[^}]+\}[^)]*\)', r'\1', content)
    content = re.sub(r'\[([^\]]+)\]\(user_id\)', r'\1', content)
    content = re.sub(r'\[([^\]]+)\]\(self\)', r'\1', content)
    content = re.sub(r'\[([^\]]+)\]\(e\)', r'\1', content)
    content = re.sub(r'\[([^\]]+)\]\(path\)', r'\1', content)
    
    return content

def fix_pattern_directory_refs(content):
    """Fix references to patterns that expect directories but are files."""
    # These patterns exist as .md files, not directories with index.md
    patterns_as_files = [
        'saga', 'event-streaming', 'event-driven', 'outbox',
        'distributed-queue', 'caching-strategies', 'circuit-breaker',
        'sharding', 'event-sourcing'
    ]
    
    for pattern in patterns_as_files:
        # Fix /patterns/pattern/index.md -> /patterns/pattern
        content = re.sub(f'/patterns/{pattern}/index\\.md', f'/patterns/{pattern}', content)
        content = re.sub(f'/patterns/{pattern}/', f'/patterns/{pattern}', content)
        # Fix relative paths
        content = re.sub(f'\\.\\./{pattern}/index\\.md', f'../{pattern}', content)
        content = re.sub(f'\\.\\./{pattern}/', f'../{pattern}', content)
    
    return content

def fix_missing_files_refs(content):
    """Fix references to files that don't exist but have alternatives."""
    replacements = [
        # Tags functionality not implemented
        ('/tags/', '#'),
        ('/tags/index.md', '#'),
        ('docs/tags/index.md', '#'),
        
        # Template references
        ('/reference/papers.md', '/reference/'),
        ('/reference/papers/', '/reference/'),
        
        # Generic template links
        ('/previous', '#'),
        ('/next', '#'),
        ('../previous', '#'),
        ('../next', '#'),
        
        # Pattern template
        ('/patterns/pattern.md', '#'),
        ('/patterns/pattern/', '#'),
        
        # Quantitative mappings
        ('/quantitative/queueing-theory', '/quantitative/queueing-models'),
        ('quantitative/cap-theorem.md', '/quantitative/cap-theorem'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    return content

def fix_relative_paths_in_subdirs(content, file_path):
    """Fix relative paths that are incorrect based on file location."""
    # Get the relative depth
    rel_path = os.path.relpath(file_path, 'docs')
    depth = len(rel_path.split(os.sep)) - 1
    
    # For files deep in the hierarchy, fix incorrect relative paths
    if depth >= 2:
        # Fix paths that go up too many levels
        content = re.sub(r'\.\./\.\./\.\./patterns/', '../../patterns/', content)
        content = re.sub(r'\.\./\.\./\.\./quantitative/', '../../quantitative/', content)
    
    return content

def process_file(file_path):
    """Process a single file with all fixes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all fixes
        content = fix_law_references(content)
        content = fix_google_interview_paths(content, file_path)
        content = fix_malformed_patterns(content)
        content = fix_pattern_directory_refs(content)
        content = fix_missing_files_refs(content)
        content = fix_relative_paths_in_subdirs(content, file_path)
        
        # Save if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function."""
    print("Applying final pattern fixes...")
    print("-" * 80)
    
    files_fixed = 0
    
    # Process all markdown files
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                if process_file(file_path):
                    files_fixed += 1
                    print(f"Fixed: {file_path}")
    
    print(f"\nFixed {files_fixed} files")
    
    # Run verification
    print("\nRunning verification...")
    os.system("python3 scripts/verify-links.py 2>&1 | grep -E '(Files checked:|Total internal links found:|Broken links found:)'")

if __name__ == "__main__":
    main()
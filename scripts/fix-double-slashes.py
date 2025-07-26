#!/usr/bin/env python3
"""
Fix double slashes and other remaining issues.
"""

import os
import re
import sys

def fix_double_slashes(content):
    """Fix double slashes in paths."""
    # Fix patterns like ..//quantitative/
    content = re.sub(r'\.\.//', '../', content)
    # Fix patterns like (// at start
    content = re.sub(r'\(//([^)]+)\)', r'(/\1)', content)
    return content

def fix_index_extensions(content):
    """Remove /index extensions from links."""
    # Remove /index from the end of links
    content = re.sub(r'(/[^/\s]+)/index\)', r'\1)', content)
    content = re.sub(r'(/[^/\s]+)/index\]', r'\1]', content)
    content = re.sub(r'(/[^/\s]+)/index\s', r'\1 ', content)
    return content

def fix_incident_response_path(content):
    """Fix incident-response path issue."""
    content = content.replace('/human-factors/incident-response/', '/human-factors/incident-response')
    return content

def fix_remaining_patterns(content):
    """Fix other remaining patterns."""
    # Fix patterns that still have wrong references
    replacements = [
        ('/patterns/replication.md', '/patterns/leader-follower'),
        ('/patterns/replication', '/patterns/leader-follower'),
        ('/patterns/quorum.md', '/patterns/consensus'),
        ('/patterns/quorum', '/patterns/consensus'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    return content

def process_file(file_path):
    """Process a single file with all fixes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all fixes
        content = fix_double_slashes(content)
        content = fix_index_extensions(content)
        content = fix_incident_response_path(content)
        content = fix_remaining_patterns(content)
        
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
    print("Fixing double slashes and remaining issues...")
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

if __name__ == "__main__":
    main()
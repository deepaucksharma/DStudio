#!/usr/bin/env python3
"""
Convert custom CSS components to Material for MkDocs features.
This script finds and converts legacy custom CSS classes to Material's native components.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
import argparse

# Mapping of custom CSS classes to Material admonition types
CSS_TO_MATERIAL_MAP = {
    'axiom-box': 'abstract',
    'decision-box': 'tip', 
    'failure-vignette': 'danger',
    'truth-box': 'info',
    'warning-box': 'warning',
    'success-box': 'success',
    'info-box': 'info',
    'error-box': 'failure',
    'note-box': 'note',
    'example-box': 'example',
    'question-box': 'question',
    'quote-box': 'quote',
    'pill': 'info',  # Convert pills to inline code or admonitions
    'journey-container': 'info',  # Special handling needed
    'grid cards': 'grid cards',  # Already Material-native
    'responsive-table': None,  # Tables are responsive by default in Material
}

# Stats tracking
stats = {
    'files_processed': 0,
    'files_modified': 0,
    'components_converted': 0,
    'conversion_details': {}
}

def extract_title_from_content(content: str) -> Tuple[str, str]:
    """Extract a title from the content if it starts with a header."""
    lines = content.strip().split('\n')
    if lines and lines[0].startswith('#'):
        # Remove the # and any trailing punctuation
        title = lines[0].lstrip('#').strip().rstrip(':')
        # Return remaining content and title
        remaining = '\n'.join(lines[1:]).strip()
        return title, remaining
    # Check for bold text as title
    bold_match = re.match(r'\*\*(.*?)\*\*:?\s*(.*)', content, re.DOTALL)
    if bold_match:
        return bold_match.group(1), bold_match.group(2).strip()
    return None, content

def convert_responsive_table(content: str) -> str:
    """Convert responsive table divs - tables are responsive by default in Material."""
    # Pattern for responsive table divs (including markdown attribute)
    pattern = r'<div class="responsive-table"[^>]*>\s*(.*?)\s*</div>'
    
    def replace_table_div(match):
        table_content = match.group(1).strip()
        stats['components_converted'] += 1
        if 'responsive-table' not in stats['conversion_details']:
            stats['conversion_details']['responsive-table'] = 0
        stats['conversion_details']['responsive-table'] += 1
        # Just return the table content without the wrapper div
        return table_content
    
    return re.sub(pattern, replace_table_div, content, flags=re.DOTALL | re.MULTILINE)

def convert_custom_divs_multiline(content: str) -> str:
    """Convert custom divs that might span multiple lines."""
    # More comprehensive pattern for divs
    patterns = [
        # Pattern for divs with class (may have other attributes)
        (r'<div\s+class="([^"]+)"[^>]*>\s*(.*?)\s*</div>', True),
        # Pattern for divs with both class and style
        (r'<div\s+class="([^"]+)"[^>]*style="[^"]*"[^>]*>\s*(.*?)\s*</div>', True),
        # Pattern for spans with class (pills, etc)
        (r'<span\s+class="([^"]+)"[^>]*>\s*(.*?)\s*</span>', False),
    ]
    
    for pattern, is_div in patterns:
        def replace_element(match):
            class_names = match.group(1)
            element_content = match.group(2).strip()
            
            # Handle multiple classes
            primary_class = None
            for cls in class_names.split():
                if cls in CSS_TO_MATERIAL_MAP:
                    primary_class = cls
                    break
            
            if not primary_class:
                # Check for partial matches
                for cls in class_names.split():
                    for known_cls in CSS_TO_MATERIAL_MAP:
                        if known_cls in cls or cls in known_cls:
                            primary_class = known_cls
                            break
                    if primary_class:
                        break
            
            if not primary_class:
                return match.group(0)  # Return unchanged if no mapping found
            
            material_type = CSS_TO_MATERIAL_MAP.get(primary_class)
            
            if material_type is None:
                # Special handling for responsive-table, etc.
                return element_content
            
            if material_type == 'grid cards':
                return match.group(0)  # Already Material-native
            
            # For spans (pills), convert to inline code
            if not is_div and primary_class == 'pill':
                stats['components_converted'] += 1
                if 'pill' not in stats['conversion_details']:
                    stats['conversion_details']['pill'] = 0
                stats['conversion_details']['pill'] += 1
                return f'`{element_content}`'
            
            # For divs, convert to admonition
            if is_div:
                # Extract title if present
                title, remaining_content = extract_title_from_content(element_content)
                
                # Format as admonition
                if title:
                    admonition = f'!!! {material_type} "{title}"\n'
                else:
                    admonition = f'!!! {material_type}\n'
                
                # Indent content
                if remaining_content:
                    indented_content = '\n'.join(f'    {line}' if line.strip() else '' 
                                                 for line in remaining_content.split('\n'))
                    admonition += indented_content
                
                stats['components_converted'] += 1
                if primary_class not in stats['conversion_details']:
                    stats['conversion_details'][primary_class] = 0
                stats['conversion_details'][primary_class] += 1
                
                return admonition
            
            return match.group(0)
        
        content = re.sub(pattern, replace_element, content, flags=re.DOTALL | re.MULTILINE)
    
    return content

def convert_custom_components(content: str) -> str:
    """Convert all custom CSS components to Material components."""
    # First, handle responsive tables specially
    content = convert_responsive_table(content)
    
    # Then handle other custom divs and spans
    content = convert_custom_divs_multiline(content)
    
    # Convert any inline style attributes to remove them
    # Pattern to remove style attributes from remaining elements
    style_removal_pattern = r'(\s+style="[^"]*")'
    content = re.sub(style_removal_pattern, '', content)
    
    return content

def process_file(filepath: Path, dry_run: bool = False) -> bool:
    """Process a single markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Check if file contains custom components
        if not any(pattern in original_content for pattern in ['class="', 'style="']):
            return False
        
        # Skip certain files that shouldn't be converted
        skip_files = ['examples/material-', 'examples/responsive-', 'mkdocs-responsive-config.md']
        if any(skip in str(filepath) for skip in skip_files):
            return False
        
        # Convert content
        converted_content = convert_custom_components(original_content)
        
        # Only write if content changed
        if converted_content != original_content:
            if not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
            
            stats['files_modified'] += 1
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def find_markdown_files(directory: Path) -> List[Path]:
    """Find all markdown files in directory."""
    return list(directory.rglob('*.md'))

def main():
    parser = argparse.ArgumentParser(description='Convert custom CSS to Material for MkDocs')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be changed without modifying files')
    parser.add_argument('--path', default='docs', 
                        help='Path to docs directory (default: docs)')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed conversion information')
    args = parser.parse_args()
    
    docs_path = Path(args.path)
    if not docs_path.exists():
        print(f"Error: Directory {docs_path} does not exist")
        sys.exit(1)
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Converting custom CSS to Material components...")
    print(f"Scanning directory: {docs_path}\n")
    
    # Find all markdown files
    md_files = find_markdown_files(docs_path)
    print(f"Found {len(md_files)} markdown files\n")
    
    # Process each file
    for filepath in md_files:
        stats['files_processed'] += 1
        if process_file(filepath, args.dry_run):
            rel_path = filepath.relative_to(docs_path)
            print(f"{'Would modify' if args.dry_run else 'Modified'}: {rel_path}")
            
            if args.verbose:
                # Show a preview of changes
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'responsive-table' in content:
                    count = content.count('responsive-table')
                    print(f"  - {count} responsive-table divs to remove")
                if 'axiom-box' in content:
                    count = content.count('axiom-box')
                    print(f"  - {count} axiom-box → abstract admonitions")
                if 'decision-box' in content:
                    count = content.count('decision-box')
                    print(f"  - {count} decision-box → tip admonitions")
                if 'failure-vignette' in content:
                    count = content.count('failure-vignette')
                    print(f"  - {count} failure-vignette → danger admonitions")
    
    # Print statistics
    print("\n" + "="*60)
    print("CONVERSION SUMMARY")
    print("="*60)
    print(f"Files processed: {stats['files_processed']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Components converted: {stats['components_converted']}")
    
    if stats['conversion_details']:
        print("\nConversion breakdown:")
        for class_name, count in sorted(stats['conversion_details'].items(), key=lambda x: -x[1]):
            material_type = CSS_TO_MATERIAL_MAP.get(class_name, 'unknown')
            if material_type is None:
                print(f"  {class_name} → removed wrapper: {count}")
            else:
                print(f"  {class_name} → {material_type}: {count}")
    
    if args.dry_run:
        print("\nThis was a dry run. No files were modified.")
        print("Run without --dry-run to apply changes.")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Comprehensive script to convert custom CSS components to Material for MkDocs features.
Handles complex cases including nested divs, inline styles, and SVG content.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
import argparse

# Enhanced mapping of custom CSS classes to Material admonition types
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
    'pill': None,  # Convert to inline code
    'journey-container': 'info',
    'grid cards': None,  # Already Material-native - skip
    'responsive-table': None,  # Tables are responsive by default
    'text-center': None,  # Remove wrapper, keep content
    'scaling-regimes': None,  # Complex layout - needs special handling
}

# Stats tracking
stats = {
    'files_processed': 0,
    'files_modified': 0,
    'components_converted': 0,
    'conversion_details': {},
    'complex_components': []
}

def extract_title_from_content(content: str) -> Tuple[Optional[str], str]:
    """Extract a title from the content if it starts with a header."""
    lines = content.strip().split('\n')
    if not lines:
        return None, content
        
    # Check for h4 header (common in custom boxes)
    if lines[0].strip().startswith('<h4'):
        h4_match = re.match(r'<h4[^>]*>(.*?)</h4>', lines[0].strip())
        if h4_match:
            title = re.sub(r'<[^>]+>', '', h4_match.group(1)).strip()
            remaining = '\n'.join(lines[1:]).strip()
            return title, remaining
    
    # Check for markdown header
    if lines[0].startswith('#'):
        title = lines[0].lstrip('#').strip().rstrip(':')
        remaining = '\n'.join(lines[1:]).strip()
        return title, remaining
        
    # Check for bold text as title
    bold_match = re.match(r'\*\*(.*?)\*\*:?\s*(.*)', content, re.DOTALL)
    if bold_match:
        return bold_match.group(1), bold_match.group(2).strip()
        
    return None, content

def convert_nested_divs_to_content(content: str) -> str:
    """Extract content from nested divs with inline styles."""
    # Remove style attributes
    content = re.sub(r'\s*style="[^"]*"', '', content)
    
    # Extract content from simple divs
    div_pattern = r'<div[^>]*>\s*(.*?)\s*</div>'
    while '<div' in content:
        old_content = content
        content = re.sub(div_pattern, r'\1', content, flags=re.DOTALL)
        if old_content == content:
            break  # Prevent infinite loop
    
    # Handle SVG content - preserve it
    svg_pattern = r'(<svg[^>]*>.*?</svg>)'
    svg_matches = re.findall(svg_pattern, content, re.DOTALL)
    
    # Clean up remaining HTML tags except SVG
    if svg_matches:
        # Temporarily replace SVG with placeholders
        for i, svg in enumerate(svg_matches):
            content = content.replace(svg, f'__SVG_PLACEHOLDER_{i}__')
    
    # Remove other HTML tags
    content = re.sub(r'<(?!svg)[^>]+>', '', content)
    
    # Restore SVG content
    if svg_matches:
        for i, svg in enumerate(svg_matches):
            content = content.replace(f'__SVG_PLACEHOLDER_{i}__', svg)
    
    return content.strip()

def convert_complex_component(class_name: str, content: str) -> str:
    """Handle complex components that need special conversion."""
    if class_name == 'scaling-regimes':
        # This is a grid layout with multiple boxes - convert each inner box
        inner_boxes = re.findall(r'<div class="([^"]+)"[^>]*>(.*?)</div>', content, re.DOTALL)
        converted_parts = []
        
        for inner_class, inner_content in inner_boxes:
            if inner_class in CSS_TO_MATERIAL_MAP:
                material_type = CSS_TO_MATERIAL_MAP[inner_class]
                if material_type:
                    title, remaining = extract_title_from_content(inner_content)
                    if title:
                        converted_parts.append(f'!!! {material_type} "{title}"\n    {remaining}')
                    else:
                        converted_parts.append(f'!!! {material_type}\n    {inner_content}')
        
        return '\n\n'.join(converted_parts) if converted_parts else content
    
    return None

def convert_div_to_material(match) -> str:
    """Convert a div with custom class to Material component."""
    full_div = match.group(0)
    class_attr = match.group(1)
    content = match.group(2).strip()
    
    # Extract primary class
    classes = class_attr.split()
    primary_class = None
    
    for cls in classes:
        if cls in CSS_TO_MATERIAL_MAP:
            primary_class = cls
            break
    
    if not primary_class:
        return full_div  # No known class found
    
    material_type = CSS_TO_MATERIAL_MAP.get(primary_class)
    
    # Handle special cases
    if primary_class == 'grid cards':
        return full_div  # Already Material-native
    
    if primary_class == 'responsive-table':
        stats['components_converted'] += 1
        stats['conversion_details']['responsive-table'] = stats['conversion_details'].get('responsive-table', 0) + 1
        return content  # Just return content without wrapper
    
    if primary_class == 'text-center':
        stats['components_converted'] += 1
        stats['conversion_details']['text-center'] = stats['conversion_details'].get('text-center', 0) + 1
        return content  # Just return content without wrapper
    
    # Handle complex components
    if primary_class in ['scaling-regimes']:
        result = convert_complex_component(primary_class, content)
        if result:
            stats['complex_components'].append(primary_class)
            return result
    
    if material_type is None:
        # Remove wrapper but keep content
        stats['components_converted'] += 1
        stats['conversion_details'][primary_class] = stats['conversion_details'].get(primary_class, 0) + 1
        return content
    
    # Convert to admonition
    # First, clean up nested divs and styles
    cleaned_content = convert_nested_divs_to_content(content)
    
    # Extract title
    title, remaining_content = extract_title_from_content(cleaned_content)
    
    # Format as admonition
    if title:
        # Clean up title - remove emojis and extra formatting
        title = re.sub(r'[🚀🔧⚠️💀🎯📊]', '', title).strip()
        admonition = f'!!! {material_type} "{title}"\n'
    else:
        admonition = f'!!! {material_type}\n'
    
    # Indent content
    if remaining_content:
        lines = remaining_content.split('\n')
        indented_lines = []
        for line in lines:
            if line.strip():
                indented_lines.append(f'    {line}')
            else:
                indented_lines.append('')
        admonition += '\n'.join(indented_lines)
    
    stats['components_converted'] += 1
    stats['conversion_details'][primary_class] = stats['conversion_details'].get(primary_class, 0) + 1
    
    return admonition

def convert_custom_components(content: str) -> str:
    """Convert all custom CSS components to Material components."""
    # Pattern for divs with class attribute (handles nested content and newlines)
    div_pattern = r'<div\s+class="([^"]+)"[^>]*>\s*(.*?)\s*</div>'
    
    # First pass: Convert divs
    converted = re.sub(div_pattern, convert_div_to_material, content, flags=re.DOTALL | re.MULTILINE)
    
    # Convert pills (spans) to inline code
    pill_pattern = r'<span\s+class="pill[^"]*"[^>]*>(.*?)</span>'
    converted = re.sub(pill_pattern, lambda m: f'`{m.group(1)}`', converted)
    
    # Remove any remaining style attributes
    converted = re.sub(r'\s+style="[^"]*"', '', converted)
    
    return converted

def process_file(filepath: Path, dry_run: bool = False) -> bool:
    """Process a single markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Skip certain example files
        skip_patterns = [
            'examples/material-',
            'examples/responsive-',
            'mkdocs-responsive-config',
            'material-grid-examples',
            'material-transformations'
        ]
        if any(pattern in str(filepath) for pattern in skip_patterns):
            return False
        
        # Check if file contains custom components
        if not re.search(r'class="[^"]*"', original_content):
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

def analyze_custom_usage(directory: Path) -> Dict[str, int]:
    """Analyze custom CSS usage across all files."""
    usage = {}
    md_files = list(directory.rglob('*.md'))
    
    for filepath in md_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all class attributes
            classes = re.findall(r'class="([^"]+)"', content)
            for class_list in classes:
                for cls in class_list.split():
                    usage[cls] = usage.get(cls, 0) + 1
        except:
            pass
    
    return usage

def main():
    parser = argparse.ArgumentParser(description='Convert custom CSS to Material for MkDocs')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be changed without modifying files')
    parser.add_argument('--path', default='docs', 
                        help='Path to docs directory (default: docs)')
    parser.add_argument('--analyze', action='store_true',
                        help='Analyze custom CSS usage before conversion')
    args = parser.parse_args()
    
    docs_path = Path(args.path)
    if not docs_path.exists():
        print(f"Error: Directory {docs_path} does not exist")
        sys.exit(1)
    
    # Analyze usage if requested
    if args.analyze:
        print("Analyzing custom CSS usage...")
        usage = analyze_custom_usage(docs_path)
        print("\nCustom CSS classes found:")
        for cls, count in sorted(usage.items(), key=lambda x: -x[1])[:20]:
            mapped = CSS_TO_MATERIAL_MAP.get(cls, 'unmapped')
            print(f"  {cls}: {count} occurrences → {mapped}")
        print()
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Converting custom CSS to Material components...")
    print(f"Scanning directory: {docs_path}\n")
    
    # Find all markdown files
    md_files = list(docs_path.rglob('*.md'))
    print(f"Found {len(md_files)} markdown files\n")
    
    # Process each file
    modified_files = []
    for filepath in md_files:
        stats['files_processed'] += 1
        if process_file(filepath, args.dry_run):
            modified_files.append(filepath)
            print(f"{'Would modify' if args.dry_run else 'Modified'}: {filepath.relative_to(docs_path)}")
    
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
    
    if stats['complex_components']:
        print(f"\nComplex components handled: {', '.join(set(stats['complex_components']))}")
    
    if args.dry_run:
        print("\nThis was a dry run. No files were modified.")
        print("Run without --dry-run to apply changes.")
    else:
        print(f"\nSuccessfully converted {stats['components_converted']} components in {stats['files_modified']} files.")

if __name__ == '__main__':
    main()
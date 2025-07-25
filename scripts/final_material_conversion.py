#!/usr/bin/env python3
"""
Final comprehensive conversion script for Material for MkDocs.
Handles all remaining custom CSS classes including complex calculators and tools.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

# Comprehensive mapping of ALL custom classes to Material equivalents
COMPREHENSIVE_CSS_MAP = {
    # Box-style components
    'axiom-box': 'abstract',
    'decision-box': 'tip', 
    'failure-vignette': 'danger',
    'truth-box': 'info',
    'law-box': 'abstract',
    'insight-box': 'info',
    'warning-box': 'warning',
    'success-box': 'success',
    'error-box': 'failure',
    'note-box': 'note',
    'example-box': 'example',
    'question-box': 'question',
    'quote-box': 'quote',
    'problem-box': 'warning',
    'key-insight': 'info',
    'formula-box': 'example',
    'summary-box': 'abstract',
    'conclusion-note': 'note',
    'warning-banner': 'warning',
    'insight-banner': 'info',
    'insight-note': 'info',
    'warning-note': 'warning',
    'lesson-learned': 'tip',
    
    # Table wrappers (remove - tables are responsive by default)
    'responsive-table': None,
    'comparison-table': None,
    'metrics-table': None,
    'data-table': None,
    
    # Card components (preserve Material native)
    'pattern-card': 'card',
    'pattern-card__title': 'card__title',
    'pattern-card__description': 'card__description',
    
    # Calculator/tool specific (convert to structured content)
    'calculator-container': 'info',
    'calculator-tool': None,
    'results-panel': 'note',
    'input-group': None,
    'calc-header': None,
    'calc-button': None,
    'help': None,
    
    # Progress/metrics visualization
    'progress-bar': None,
    'progress-fill': None,
    'metric-value': None,
    'stat-number': None,
    'metric-card': 'card',
    
    # Navigation elements
    'navigation-links': None,
    'prev-link': None,
    'next-link': None,
    
    # Generic containers
    'journey-container': 'info',
    'cost-insight': 'tip',
    'diagnosis-result': 'info',
}

# Stats tracking
stats = {
    'files_processed': 0,
    'files_modified': 0,
    'components_converted': 0,
    'conversion_details': {},
    'complex_tools_converted': []
}

def clean_calculator_html(content: str) -> str:
    """Clean up calculator/interactive tool HTML to use Material components."""
    # Remove calculator-specific divs but preserve structure
    calculator_pattern = r'<div class="calculator-container"[^>]*>(.*?)</div>'
    
    def replace_calculator(match):
        inner_content = match.group(1)
        stats['complex_tools_converted'].append('calculator')
        return f'!!! info "Interactive Calculator"\n    {inner_content.strip()}'
    
    content = re.sub(calculator_pattern, replace_calculator, content, flags=re.DOTALL)
    
    # Clean up input groups
    input_pattern = r'<div class="input-group"[^>]*>(.*?)</div>'
    content = re.sub(input_pattern, r'\1', content, flags=re.DOTALL)
    
    # Clean up help elements
    help_pattern = r'<(?:div|span) class="help"[^>]*>(.*?)</(?:div|span)>'
    content = re.sub(help_pattern, r'*\1*', content, flags=re.DOTALL)
    
    return content

def convert_all_custom_divs(content: str) -> str:
    """Convert all custom div classes to Material admonitions."""
    # Pattern for any div with a custom class
    div_pattern = r'<div\s+class="([^"]+)"[^>]*>\s*(.*?)\s*</div>'
    
    def replace_div(match):
        classes = match.group(1).split()
        inner_content = match.group(2).strip()
        
        # Check if it's a Material native class
        material_natives = {'grid', 'cards', 'card', 'admonition'}
        if any(cls in material_natives for cls in classes):
            return match.group(0)  # Keep as is
        
        # Find the first mapped class
        for cls in classes:
            if cls in COMPREHENSIVE_CSS_MAP:
                material_type = COMPREHENSIVE_CSS_MAP[cls]
                
                if material_type is None:
                    # Remove wrapper
                    stats['components_converted'] += 1
                    stats['conversion_details'][cls] = stats['conversion_details'].get(cls, 0) + 1
                    return inner_content
                else:
                    # Convert to admonition
                    title = extract_title(inner_content)
                    if title:
                        admonition = f'!!! {material_type} "{title[0]}"\n'
                        content_to_indent = title[1]
                    else:
                        admonition = f'!!! {material_type}\n'
                        content_to_indent = inner_content
                    
                    # Indent content
                    if content_to_indent:
                        lines = content_to_indent.split('\n')
                        indented = '\n'.join(f'    {line}' if line.strip() else '' for line in lines)
                        admonition += indented
                    
                    stats['components_converted'] += 1
                    stats['conversion_details'][cls] = stats['conversion_details'].get(cls, 0) + 1
                    
                    return admonition
        
        # No mapping found - check for specific patterns
        class_str = ' '.join(classes)
        
        # Handle inline style calculations or template variables
        if '${' in class_str or ':' in class_str or '?' in class_str:
            # This is likely JavaScript template syntax - leave as is
            return match.group(0)
        
        # Generic box-like classes
        if any(word in class_str for word in ['box', 'container', 'panel', 'section']):
            stats['components_converted'] += 1
            stats['conversion_details']['generic-box'] = stats['conversion_details'].get('generic-box', 0) + 1
            return f'!!! info\n    {inner_content}'
        
        # Default: remove wrapper
        return inner_content
    
    # Apply conversion with multiline flag
    return re.sub(div_pattern, replace_div, content, flags=re.DOTALL | re.MULTILINE)

def extract_title(content: str) -> Optional[Tuple[str, str]]:
    """Extract title from content."""
    lines = content.strip().split('\n', 1)
    if not lines:
        return None
    
    first_line = lines[0].strip()
    
    # Check for markdown header
    if first_line.startswith('#'):
        title = first_line.lstrip('#').strip()
        remaining = lines[1] if len(lines) > 1 else ''
        return (title, remaining)
    
    # Check for bold text
    bold_match = re.match(r'\*\*(.*?)\*\*:?\s*$', first_line)
    if bold_match:
        title = bold_match.group(1)
        remaining = lines[1] if len(lines) > 1 else ''
        return (title, remaining)
    
    # Check for HTML header
    header_match = re.match(r'<h[1-6][^>]*>(.*?)</h[1-6]>', first_line)
    if header_match:
        title = re.sub(r'<[^>]+>', '', header_match.group(1))
        remaining = lines[1] if len(lines) > 1 else ''
        return (title, remaining)
    
    return None

def clean_remaining_styles(content: str) -> str:
    """Remove any remaining style attributes."""
    # Remove style attributes
    content = re.sub(r'\s+style="[^"]*"', '', content)
    
    # Remove empty class attributes
    content = re.sub(r'\s+class=""', '', content)
    
    # Clean up multiple spaces
    content = re.sub(r'  +', ' ', content)
    
    return content

def process_file(filepath: Path, dry_run: bool = False) -> bool:
    """Process a single markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Skip if no custom classes
        if not re.search(r'class="[^"]*"', original_content):
            return False
        
        # Apply conversions
        content = original_content
        
        # Clean calculator/tool HTML first
        if 'calculator' in str(filepath) or 'tool' in str(filepath):
            content = clean_calculator_html(content)
        
        # Convert all custom divs
        content = convert_all_custom_divs(content)
        
        # Clean remaining styles
        content = clean_remaining_styles(content)
        
        # Only write if changed
        if content != original_content:
            if not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            stats['files_modified'] += 1
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Final Material for MkDocs conversion')
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
        return
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Final Material for MkDocs Conversion")
    print("=" * 60)
    
    # Find all markdown files
    md_files = list(docs_path.rglob('*.md'))
    print(f"Found {len(md_files)} markdown files\n")
    
    # Process each file
    for filepath in md_files:
        stats['files_processed'] += 1
        if process_file(filepath, args.dry_run):
            rel_path = filepath.relative_to(docs_path)
            print(f"{'Would modify' if args.dry_run else 'Modified'}: {rel_path}")
            
            if args.verbose and args.dry_run:
                # Show what would be converted
                with open(filepath, 'r') as f:
                    content = f.read()
                custom_classes = re.findall(r'class="([^"]+)"', content)
                if custom_classes:
                    unique_classes = set()
                    for class_list in custom_classes:
                        unique_classes.update(class_list.split())
                    print(f"  Classes found: {', '.join(sorted(unique_classes))}")
    
    # Print statistics
    print("\n" + "=" * 60)
    print("FINAL CONVERSION SUMMARY")
    print("=" * 60)
    print(f"Files processed: {stats['files_processed']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Components converted: {stats['components_converted']}")
    
    if stats['conversion_details']:
        print("\nConversion breakdown:")
        for class_name, count in sorted(stats['conversion_details'].items(), key=lambda x: -x[1]):
            material_type = COMPREHENSIVE_CSS_MAP.get(class_name, 'unknown')
            if material_type is None:
                print(f"  {class_name} → removed wrapper: {count}")
            else:
                print(f"  {class_name} → {material_type}: {count}")
    
    if stats['complex_tools_converted']:
        print(f"\nComplex tools converted: {len(set(stats['complex_tools_converted']))}")
    
    if args.dry_run:
        print("\nThis was a dry run. No files were modified.")
        print("Run without --dry-run to apply changes.")
    else:
        print(f"\n✅ Successfully converted all custom CSS components!")
        print(f"   {stats['components_converted']} total components converted")
        print(f"   {stats['files_modified']} files updated")

if __name__ == '__main__':
    main()
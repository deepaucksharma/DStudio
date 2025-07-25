#!/usr/bin/env python3
"""
Verify Material for MkDocs conversion and generate report.
Checks for remaining custom CSS and provides recommendations.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Material for MkDocs native classes that should be preserved
MATERIAL_NATIVE_CLASSES = {
    'grid', 'cards',  # Grid system
    'card', 'card__title', 'card__description',  # Card components
    'admonition', 'note', 'abstract', 'info', 'tip', 'success',  # Admonitions
    'question', 'warning', 'failure', 'danger', 'bug', 'example', 'quote',
    'md-typeset', 'md-button', 'md-content',  # Material theme classes
    'annotate', 'highlight', 'keys',  # Special features
    'arithmatex', 'mermaid',  # Extensions
}

# Known custom classes that need conversion
CUSTOM_CLASSES_TO_CONVERT = {
    'axiom-box': 'abstract admonition',
    'decision-box': 'tip admonition', 
    'failure-vignette': 'danger admonition',
    'truth-box': 'info admonition',
    'law-box': 'abstract admonition',
    'insight-box': 'info admonition',
    'warning-box': 'warning admonition',
    'success-box': 'success admonition',
    'journey-container': 'info admonition',
    'pattern-card': 'card',
    'pattern-card__title': 'card__title',
    'pattern-card__description': 'card__description',
    'responsive-table': '',  # Tables are responsive by default
    'comparison-table': '',
    'metrics-table': '',
    'data-table': '',
}

def find_all_classes(content: str) -> Set[str]:
    """Extract all class names from HTML in markdown."""
    classes = set()
    
    # Find class attributes in HTML
    class_pattern = r'class="([^"]+)"'
    for match in re.finditer(class_pattern, content):
        class_list = match.group(1)
        classes.update(class_list.split())
    
    # Find div/span with classes (common patterns)
    div_pattern = r'<(?:div|span)\s+class="([^"]+)"'
    for match in re.finditer(div_pattern, content):
        class_list = match.group(1)
        classes.update(class_list.split())
    
    return classes

def analyze_file(filepath: Path) -> Dict:
    """Analyze a single file for custom CSS usage."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        classes = find_all_classes(content)
        
        # Categorize classes
        material_native = classes & MATERIAL_NATIVE_CLASSES
        known_custom = classes & set(CUSTOM_CLASSES_TO_CONVERT.keys())
        unknown_custom = classes - MATERIAL_NATIVE_CLASSES - set(CUSTOM_CLASSES_TO_CONVERT.keys())
        
        # Remove common non-issue classes
        ignore_classes = {'responsive', 'text-center', 'grid-flow-row', 'gap-4', 'p-4', 'm-4'}
        unknown_custom = unknown_custom - ignore_classes
        
        return {
            'all_classes': classes,
            'material_native': material_native,
            'known_custom': known_custom,
            'unknown_custom': unknown_custom,
            'has_custom': bool(known_custom or unknown_custom)
        }
        
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return {}

def generate_conversion_recommendations(class_usage: Dict[str, int]) -> List[Tuple[str, str, str]]:
    """Generate recommendations for converting custom classes."""
    recommendations = []
    
    for class_name, count in sorted(class_usage.items(), key=lambda x: -x[1]):
        if class_name in CUSTOM_CLASSES_TO_CONVERT:
            material_equivalent = CUSTOM_CLASSES_TO_CONVERT[class_name]
            if material_equivalent:
                action = f"Convert to: {material_equivalent}"
            else:
                action = "Remove wrapper (not needed)"
            recommendations.append((class_name, str(count), action))
        elif class_name not in MATERIAL_NATIVE_CLASSES:
            # Unknown custom class
            if 'box' in class_name:
                recommendations.append((class_name, str(count), "Convert to appropriate admonition"))
            elif 'table' in class_name:
                recommendations.append((class_name, str(count), "Remove wrapper (tables are responsive)"))
            elif 'card' in class_name:
                recommendations.append((class_name, str(count), "Use Material card classes"))
            else:
                recommendations.append((class_name, str(count), "Review and convert/remove"))
    
    return recommendations

def main():
    docs_path = Path('docs')
    
    print("=" * 80)
    print("MATERIAL FOR MKDOCS CONVERSION VERIFICATION REPORT")
    print("=" * 80)
    print()
    
    # Find all markdown files
    md_files = list(docs_path.rglob('*.md'))
    print(f"Total markdown files found: {len(md_files)}")
    print()
    
    # Analyze all files
    files_with_custom = []
    all_custom_classes = defaultdict(int)
    all_unknown_classes = defaultdict(int)
    
    for filepath in md_files:
        analysis = analyze_file(filepath)
        if analysis.get('has_custom'):
            files_with_custom.append((filepath, analysis))
            
            for class_name in analysis['known_custom']:
                all_custom_classes[class_name] += 1
            
            for class_name in analysis['unknown_custom']:
                all_unknown_classes[class_name] += 1
    
    # Summary statistics
    print("CONVERSION SUMMARY")
    print("-" * 40)
    print(f"Files analyzed: {len(md_files)}")
    print(f"Files with custom CSS: {len(files_with_custom)}")
    print(f"Files fully converted: {len(md_files) - len(files_with_custom)}")
    print(f"Conversion rate: {((len(md_files) - len(files_with_custom)) / len(md_files) * 100):.1f}%")
    print()
    
    # Known custom classes still in use
    if all_custom_classes:
        print("KNOWN CUSTOM CLASSES STILL IN USE")
        print("-" * 40)
        print(f"{'Class Name':<30} {'Count':<10} {'Action Required'}")
        print("-" * 80)
        recommendations = generate_conversion_recommendations(all_custom_classes)
        for class_name, count, action in recommendations:
            print(f"{class_name:<30} {count:<10} {action}")
        print()
    
    # Unknown custom classes
    if all_unknown_classes:
        print("UNKNOWN CUSTOM CLASSES DETECTED")
        print("-" * 40)
        print(f"{'Class Name':<30} {'Count':<10} {'Recommendation'}")
        print("-" * 80)
        for class_name, count in sorted(all_unknown_classes.items(), key=lambda x: -x[1]):
            if count > 5:  # Only show classes used more than 5 times
                recommendation = "Review usage and convert"
                if 'grid' in class_name or 'flex' in class_name:
                    recommendation = "Likely Tailwind/utility class - safe to ignore"
                elif 'js-' in class_name or 'data-' in class_name:
                    recommendation = "JavaScript hook - keep as is"
                print(f"{class_name:<30} {count:<10} {recommendation}")
        print()
    
    # Files needing attention
    if files_with_custom:
        print("FILES REQUIRING ATTENTION")
        print("-" * 40)
        print(f"Top 10 files with most custom CSS usage:")
        print()
        
        # Sort by number of custom classes
        files_sorted = sorted(files_with_custom, 
                             key=lambda x: len(x[1]['known_custom']) + len(x[1]['unknown_custom']), 
                             reverse=True)
        
        for i, (filepath, analysis) in enumerate(files_sorted[:10]):
            rel_path = filepath.relative_to(docs_path)
            custom_count = len(analysis['known_custom']) + len(analysis['unknown_custom'])
            print(f"{i+1}. {rel_path}")
            print(f"   Custom classes: {custom_count}")
            if analysis['known_custom']:
                print(f"   Known: {', '.join(sorted(analysis['known_custom']))}")
            if analysis['unknown_custom']:
                print(f"   Unknown: {', '.join(sorted(analysis['unknown_custom']))}")
            print()
    
    # Final recommendations
    print("RECOMMENDATIONS")
    print("-" * 40)
    if len(files_with_custom) == 0:
        print("✅ Excellent! All files have been fully converted to Material for MkDocs.")
        print("   No custom CSS classes detected.")
    elif len(files_with_custom) < 10:
        print("✅ Good progress! Only a few files remain with custom CSS.")
        print(f"   {len(files_with_custom)} files need final conversion.")
        print("   Run the conversion script on these remaining files.")
    else:
        print("⚠️  Significant custom CSS usage remains.")
        print(f"   {len(files_with_custom)} files still use custom CSS classes.")
        print("   Consider:")
        print("   1. Running the comprehensive conversion script")
        print("   2. Manually reviewing complex components")
        print("   3. Updating any custom JavaScript that depends on these classes")
    
    print()
    print("=" * 80)
    print("Report generated successfully!")

if __name__ == '__main__':
    main()
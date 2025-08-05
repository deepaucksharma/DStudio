#!/usr/bin/env python3
"""
Analyze and synthesize metadata from all pattern files in the pattern library.
"""

import os
import yaml
import json
from pathlib import Path
from collections import defaultdict, Counter
import re
from datetime import datetime

def extract_frontmatter(file_path):
    """Extract YAML frontmatter from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    return None

def analyze_patterns(pattern_dir):
    """Analyze all patterns in the pattern library."""
    patterns = []
    categories = defaultdict(list)
    
    # Walk through all markdown files
    for root, dirs, files in os.walk(pattern_dir):
        # Skip the root index files and synthesis files
        if root == pattern_dir:
            continue
            
        for file in files:
            if file.endswith('.md') and file != 'index.md':
                # Skip synthesis and guide files
                if file in ['pattern-synthesis-guide.md', 'pattern-relationship-map.md', 'pattern-decision-matrix.md']:
                    continue
                file_path = os.path.join(root, file)
                metadata = extract_frontmatter(file_path)
                
                if metadata:
                    # Extract category from path
                    relative_path = os.path.relpath(file_path, pattern_dir)
                    category = relative_path.split(os.sep)[0]
                    
                    # Add computed fields
                    metadata['file_path'] = file_path
                    metadata['category'] = category
                    metadata['pattern_name'] = file.replace('.md', '')
                    
                    patterns.append(metadata)
                    categories[category].append(metadata)
    
    return patterns, categories

def generate_statistics(patterns):
    """Generate comprehensive statistics about patterns."""
    stats = {
        'total_patterns': len(patterns),
        'by_category': Counter(p.get('category') for p in patterns),
        'by_excellence_tier': Counter(p.get('excellence_tier') for p in patterns),
        'by_pattern_status': Counter(p.get('pattern_status') for p in patterns),
        'by_current_relevance': Counter(p.get('current_relevance') for p in patterns),
        'by_difficulty': Counter(p.get('difficulty') for p in patterns),
        'patterns_with_modern_examples': sum(1 for p in patterns if p.get('modern_examples')),
        'patterns_with_production_checklist': sum(1 for p in patterns if p.get('production_checklist')),
        'patterns_with_prerequisites': sum(1 for p in patterns if p.get('prerequisites')),
    }
    
    # Extract introduction years
    intro_years = []
    for p in patterns:
        if p.get('introduced'):
            try:
                year = int(p['introduced'].split('-')[0])
                intro_years.append(year)
            except:
                pass
    
    if intro_years:
        stats['introduction_years'] = {
            'earliest': min(intro_years),
            'latest': max(intro_years),
            'by_year': Counter(intro_years)
        }
    
    return stats

def analyze_relationships(patterns):
    """Analyze relationships between patterns."""
    relationships = {
        'law_connections': defaultdict(list),
        'pillar_connections': defaultdict(list),
        'pattern_combinations': [],
        'common_prerequisites': Counter(),
        'dependency_graph': defaultdict(set)
    }
    
    for pattern in patterns:
        # Laws and pillars
        for law in pattern.get('related_laws', []):
            relationships['law_connections'][law].append(pattern['pattern_name'])
        
        for pillar in pattern.get('related_pillars', []):
            relationships['pillar_connections'][pillar].append(pattern['pattern_name'])
        
        # Prerequisites
        prereqs = pattern.get('prerequisites', [])
        if prereqs:
            for prereq in prereqs:
                relationships['common_prerequisites'][prereq] += 1
    
    return relationships

def generate_insights(patterns, categories, stats, relationships):
    """Generate key insights from the analysis."""
    insights = {
        'excellence_distribution': {
            'gold_percentage': (stats['by_excellence_tier'].get('gold', 0) / stats['total_patterns']) * 100,
            'silver_percentage': (stats['by_excellence_tier'].get('silver', 0) / stats['total_patterns']) * 100,
            'bronze_percentage': (stats['by_excellence_tier'].get('bronze', 0) / stats['total_patterns']) * 100,
        },
        'category_insights': {},
        'maturity_insights': {},
        'adoption_trends': {},
        'key_patterns': []
    }
    
    # Category-specific insights
    for cat, cat_patterns in categories.items():
        gold_count = sum(1 for p in cat_patterns if p.get('excellence_tier') == 'gold')
        insights['category_insights'][cat] = {
            'total': len(cat_patterns),
            'gold_patterns': gold_count,
            'gold_percentage': (gold_count / len(cat_patterns)) * 100 if cat_patterns else 0,
            'common_difficulty': Counter(p.get('difficulty') for p in cat_patterns).most_common(1)[0][0] if cat_patterns else None
        }
    
    # Find key patterns (Gold + mainstream + have modern examples)
    key_patterns = [
        p for p in patterns 
        if p.get('excellence_tier') == 'gold' 
        and p.get('current_relevance') == 'mainstream'
        and p.get('modern_examples')
    ]
    insights['key_patterns'] = [p['pattern_name'] for p in key_patterns]
    
    return insights

def main():
    pattern_dir = Path(__file__).parent.parent / 'docs' / 'pattern-library'
    
    print("🔍 Analyzing Pattern Library...\n")
    
    # Extract and analyze patterns
    patterns, categories = analyze_patterns(pattern_dir)
    stats = generate_statistics(patterns)
    relationships = analyze_relationships(patterns)
    insights = generate_insights(patterns, categories, stats, relationships)
    
    # Output results
    print(f"📊 Pattern Library Statistics")
    print(f"{'=' * 50}")
    print(f"Total Patterns: {stats['total_patterns']}")
    print(f"\nBy Category:")
    for cat, count in sorted(stats['by_category'].items()):
        print(f"  - {cat}: {count} patterns")
    
    print(f"\nBy Excellence Tier:")
    for tier, count in [('gold', stats['by_excellence_tier'].get('gold', 0)),
                        ('silver', stats['by_excellence_tier'].get('silver', 0)),
                        ('bronze', stats['by_excellence_tier'].get('bronze', 0))]:
        percentage = (count / stats['total_patterns']) * 100
        print(f"  🥇 {tier.capitalize()}: {count} ({percentage:.1f}%)")
    
    print(f"\nBy Current Relevance:")
    for relevance, count in stats['by_current_relevance'].most_common():
        if relevance:
            print(f"  - {relevance}: {count}")
    
    print(f"\nBy Pattern Status:")
    for status, count in stats['by_pattern_status'].most_common():
        if status:
            print(f"  - {status}: {count}")
    
    print(f"\n🔗 Pattern Relationships")
    print(f"{'=' * 50}")
    print(f"\nMost Connected Laws:")
    for law, patterns in sorted(relationships['law_connections'].items(), 
                               key=lambda x: len(x[1]), reverse=True)[:5]:
        print(f"  - {law}: {len(patterns)} patterns")
    
    print(f"\nMost Connected Pillars:")
    for pillar, patterns in sorted(relationships['pillar_connections'].items(),
                                  key=lambda x: len(x[1]), reverse=True)[:5]:
        print(f"  - {pillar}: {len(patterns)} patterns")
    
    print(f"\n🎯 Key Insights")
    print(f"{'=' * 50}")
    print(f"Excellence Distribution:")
    print(f"  - Gold: {insights['excellence_distribution']['gold_percentage']:.1f}%")
    print(f"  - Silver: {insights['excellence_distribution']['silver_percentage']:.1f}%")
    print(f"  - Bronze: {insights['excellence_distribution']['bronze_percentage']:.1f}%")
    
    print(f"\nCategory Excellence Leaders:")
    for cat, data in sorted(insights['category_insights'].items(),
                           key=lambda x: x[1]['gold_percentage'], reverse=True):
        print(f"  - {cat}: {data['gold_percentage']:.1f}% gold ({data['gold_patterns']}/{data['total']})")
    
    print(f"\n🌟 Key Patterns (Gold + Mainstream + Modern Examples): {len(insights['key_patterns'])}")
    for pattern in sorted(insights['key_patterns'])[:10]:
        print(f"  - {pattern}")
    
    # Save detailed analysis
    output_file = pattern_dir.parent / 'reference' / 'pattern-analysis.json'
    with open(output_file, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'relationships': {k: dict(v) if isinstance(v, defaultdict) else v 
                            for k, v in relationships.items()},
            'insights': insights,
            'categories': {cat: len(patterns) for cat, patterns in categories.items()}
        }, f, indent=2, default=str)
    
    print(f"\n✅ Detailed analysis saved to {output_file}")

if __name__ == '__main__':
    main()

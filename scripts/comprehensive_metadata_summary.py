#!/usr/bin/env python3
"""
Comprehensive metadata consistency summary including cross-validation with pattern_metadata.json
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional, Any

def extract_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """Extract YAML frontmatter from markdown content."""
    try:
        if content.startswith('---\n'):
            end_pos = content.find('\n---\n', 4)
            if end_pos != -1:
                frontmatter_yaml = content[4:end_pos]
                return yaml.safe_load(frontmatter_yaml)
    except yaml.YAMLError as e:
        return None
    return None

def analyze_patterns():
    """Analyze all patterns and their metadata consistency."""
    patterns_dir = Path("docs/patterns")
    
    # Load pattern_metadata.json
    with open("docs/patterns/pattern_metadata.json", 'r') as f:
        metrics_data = json.load(f)
    
    # Extract pattern names from metrics file
    metrics_patterns = set()
    for key in metrics_data.keys():
        if key.endswith('_metrics'):
            pattern_name = key[:-8]  # Remove '_metrics' suffix
            metrics_patterns.add(pattern_name)
    
    # Analyze markdown files
    markdown_files = list(patterns_dir.glob('*.md'))
    
    # Skip non-pattern files
    skip_files = {
        'README.md', 'index.md', 'index-new.md', 'pattern-catalog.md', 
        'pattern-selector-tool.md', 'pattern-relationships.md', 
        'PATTERN_TEMPLATE.md'
    }
    
    # Skip deleted files mentioned in git status
    deleted_files = {
        'EXCELLENCE_TRANSFORMATION_PROGRESS.md',
        'GOLD_PATTERNS_COMPLETE.md',
        'INDEX_UPDATE_SUMMARY.md',
        'METADATA_ENHANCEMENT_REPORT.md',
        'METADATA_ENHANCEMENT_REPORT_PHASE2.md',
        'NAVIGATION_FILTERING_COMPLETE.md',
        'NAVIGATION_INTEGRATION_COMPLETE.md',
        'PATTERN_CLASSIFICATION_RESULTS.md',
        'PATTERN_CLASSIFICATION_SUMMARY.md',
        'PATTERN_ORGANIZATION.md',
        'PATTERN_RESTORATION_COMPLETE.md'
    }
    
    patterns_analyzed = {
        'total_files': 0,
        'pattern_files': 0,
        'with_excellence_metadata': 0,
        'complete_excellence_metadata': 0,
        'gold_patterns': 0,
        'silver_patterns': 0,
        'bronze_patterns': 0,
        'missing_excellence_metadata': [],
        'invalid_metadata_values': [],
        'tier_distribution': {}
    }
    
    valid_excellence_tiers = {'gold', 'silver', 'bronze'}
    valid_pattern_status = {'recommended', 'use-with-expertise', 'use-with-caution', 'legacy'}
    valid_current_relevance = {'mainstream', 'growing', 'declining', 'niche'}
    
    for file_path in sorted(markdown_files):
        patterns_analyzed['total_files'] += 1
        
        if file_path.name in skip_files or file_path.name in deleted_files:
            continue
            
        patterns_analyzed['pattern_files'] += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = extract_frontmatter(content)
            if not metadata:
                patterns_analyzed['missing_excellence_metadata'].append(f"{file_path.name} - No frontmatter")
                continue
            
            has_excellence_fields = 'excellence_tier' in metadata
            if not has_excellence_fields:
                patterns_analyzed['missing_excellence_metadata'].append(f"{file_path.name} - No excellence_tier")
                continue
                
            patterns_analyzed['with_excellence_metadata'] += 1
            
            # Check completeness of excellence metadata
            required_fields = ['excellence_tier', 'pattern_status', 'introduced', 'current_relevance']
            complete = all(field in metadata for field in required_fields)
            
            if complete:
                patterns_analyzed['complete_excellence_metadata'] += 1
            
            # Count by tier
            tier = metadata.get('excellence_tier')
            if tier in valid_excellence_tiers:
                patterns_analyzed[f'{tier}_patterns'] += 1
                if tier not in patterns_analyzed['tier_distribution']:
                    patterns_analyzed['tier_distribution'][tier] = []
                patterns_analyzed['tier_distribution'][tier].append(file_path.name)
            
            # Check for invalid values
            invalid_values = []
            if tier and tier not in valid_excellence_tiers:
                invalid_values.append(f"excellence_tier: {tier}")
            
            status = metadata.get('pattern_status')
            if status and status not in valid_pattern_status:
                invalid_values.append(f"pattern_status: {status}")
            
            relevance = metadata.get('current_relevance')
            if relevance and relevance not in valid_current_relevance:
                invalid_values.append(f"current_relevance: {relevance}")
            
            if invalid_values:
                patterns_analyzed['invalid_metadata_values'].append(f"{file_path.name} - {', '.join(invalid_values)}")
                
        except Exception as e:
            patterns_analyzed['missing_excellence_metadata'].append(f"{file_path.name} - Error: {str(e)}")
    
    return patterns_analyzed, metrics_patterns

def main():
    """Generate comprehensive summary."""
    patterns_data, metrics_patterns = analyze_patterns()
    
    print("# Comprehensive Pattern Metadata Summary")
    print()
    
    print("## Overall Statistics")
    print(f"- **Total markdown files**: {patterns_data['total_files']}")
    print(f"- **Actual pattern files**: {patterns_data['pattern_files']}")
    print(f"- **Patterns with excellence metadata**: {patterns_data['with_excellence_metadata']}")
    print(f"- **Patterns with complete excellence metadata**: {patterns_data['complete_excellence_metadata']}")
    print(f"- **Completion rate**: {patterns_data['complete_excellence_metadata'] / patterns_data['pattern_files'] * 100:.1f}%")
    print()
    
    print("## Excellence Tier Distribution")
    print(f"- **🥇 Gold patterns**: {patterns_data['gold_patterns']}")
    print(f"- **🥈 Silver patterns**: {patterns_data['silver_patterns']}")
    print(f"- **🥉 Bronze patterns**: {patterns_data['bronze_patterns']}")
    print()
    
    if patterns_data['tier_distribution']:
        print("## Patterns by Tier")
        for tier, patterns in patterns_data['tier_distribution'].items():
            print(f"### {tier.title()} Tier ({len(patterns)} patterns)")
            for pattern in sorted(patterns):
                print(f"- {pattern}")
            print()
    
    if patterns_data['missing_excellence_metadata']:
        print(f"## Patterns Missing Excellence Metadata ({len(patterns_data['missing_excellence_metadata'])})")
        for item in patterns_data['missing_excellence_metadata']:
            print(f"- {item}")
        print()
    
    if patterns_data['invalid_metadata_values']:
        print(f"## Patterns with Invalid Metadata Values ({len(patterns_data['invalid_metadata_values'])})")
        for item in patterns_data['invalid_metadata_values']:
            print(f"- {item}")
        print()
    
    print("## Next Steps")
    missing_count = len(patterns_data['missing_excellence_metadata'])
    invalid_count = len(patterns_data['invalid_metadata_values'])
    
    if missing_count > 0:
        print(f"1. **Add excellence metadata** to {missing_count} patterns")
    if invalid_count > 0:
        print(f"2. **Fix invalid metadata values** in {invalid_count} patterns")
    
    total_issues = missing_count + invalid_count
    if total_issues == 0:
        print("✅ **All patterns have valid excellence metadata!**")
    else:
        remaining_work = patterns_data['pattern_files'] - patterns_data['complete_excellence_metadata']
        print(f"3. **Total patterns needing work**: {remaining_work}")
        print(f"4. **Progress**: {patterns_data['complete_excellence_metadata']}/{patterns_data['pattern_files']} patterns complete ({patterns_data['complete_excellence_metadata'] / patterns_data['pattern_files'] * 100:.1f}%)")

if __name__ == "__main__":
    main()
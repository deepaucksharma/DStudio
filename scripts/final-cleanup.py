#!/usr/bin/env python3
"""
Final cleanup - handle remaining orphaned files
"""

import os
import shutil
from pathlib import Path
import yaml

# Custom YAML constructors
class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    pass

def ignore_unknown(loader, suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return ''
    elif isinstance(node, yaml.SequenceNode):
        return []
    elif isinstance(node, yaml.MappingNode):
        return {}

SafeLoaderIgnoreUnknown.add_multi_constructor('', ignore_unknown)

# Files/directories to remove
TO_REMOVE = [
    # Excellence framework tracking files (keep only index.md)
    'docs/excellence/comparisons/',
    'docs/excellence/excellence-journeys/',
    'docs/excellence/quick-start/',
    'docs/excellence/real-world-excellence/',
    'docs/excellence/transformation/',
    'docs/excellence/excellence-dashboard.md',
    'docs/excellence/pattern-selection-wizard.md',
    'docs/excellence/pattern-usage-examples.md',
    'docs/excellence/pattern-usage-index.md',
    
    # Introduction files (already covered in main index)
    'docs/introduction/',
    
    # Old human factors index
    'docs/human-factors/index.md',
    
    # Test and includes
    'docs/test-plan/',
    'docs/includes/',
    
    # Old pattern/quantitative indices
    'docs/patterns/index.md',
    'docs/quantitative/',
    
    # Interview prep duplicates
    'docs/interview-prep/cheatsheets/common-patterns-reference.md',
    'docs/interview-prep/cheatsheets/scalability-cheatsheet.md',
    'docs/interview-prep/frameworks/system-design-framework.md',
]

# Add to navigation
NAV_ADDITIONS = {
    'human_factors': [
        ('Chaos Engineering', 'chaos-engineering.md'),
        ('Blameless Postmortems', 'blameless-postmortems.md'),
        ('On-Call Culture', 'oncall-culture.md'),
        ('Incident Response', 'incident-response.md'),
        ('SRE Practices', 'sre-practices.md'),
        ('Team Topologies', 'team-topologies.md'),
        ('Consistency Tuning', 'consistency-tuning.md'),
    ],
    
    'tools': [
        ('Overview', 'index.md'),
        ('Availability Calculator', 'availability-calculator.md'),
        ('Capacity Calculator', 'capacity-calculator.md'),
        ('Consistency Calculator', 'consistency-calculator.md'),
        ('Cost Optimizer', 'cost-optimizer.md'),
        ('Latency Calculator', 'latency-calculator.md'),
        ('Throughput Calculator', 'throughput-calculator.md'),
    ],
    
    'quantitative_advanced': [
        ('Graph Theory', 'graph-theory.md'),
        ('Queueing Networks', 'queuing-networks.md'),
        ('Markov Chains', 'markov-chains.md'),
        ('Bayesian Reasoning', 'bayesian-reasoning.md'),
        ('Information Theory', 'information-theory.md'),
        ('Network Theory', 'network-theory.md'),
        ('Reliability Theory', 'reliability-theory.md'),
        ('Storage Economics', 'storage-economics.md'),
        ('Cache Economics', 'cache-economics.md'),
        ('Computational Geometry', 'computational-geometry.md'),
    ]
}

def remove_files_and_dirs():
    """Remove unnecessary files and directories"""
    removed = 0
    for path in TO_REMOVE:
        p = Path(path)
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
                print(f"Removed directory: {path}")
            else:
                p.unlink()
                print(f"Removed file: {path}")
            removed += 1
    return removed

def move_tools():
    """Move tools to architects handbook"""
    moved = 0
    src_dir = Path('docs/tools')
    dst_dir = Path('docs/architects-handbook/tools')
    
    if src_dir.exists():
        dst_dir.mkdir(parents=True, exist_ok=True)
        for file in src_dir.glob('*.md'):
            dst_file = dst_dir / file.name
            if not dst_file.exists():
                shutil.move(str(file), str(dst_file))
                print(f"Moved: {file.name} to architects-handbook/tools/")
                moved += 1
        
        if not list(src_dir.iterdir()):
            src_dir.rmdir()
    
    return moved

def update_navigation():
    """Update navigation with final additions"""
    # Load mkdocs.yml
    with open('mkdocs.yml', 'r') as f:
        config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
    
    nav = config.get('nav', [])
    added = 0
    
    # Add human factors that were missed
    for item in nav:
        if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
            for sub in item['Part 3 - Architect\'s Handbook']:
                if isinstance(sub, dict) and 'Human Factors' in sub:
                    human = sub['Human Factors']
                    for title, filename in NAV_ADDITIONS['human_factors']:
                        path = f'architects-handbook/human-factors/{filename}'
                        if Path(f'docs/{path}').exists() and not any(path in str(i) for i in human):
                            human.append({title: path})
                            added += 1
    
    # Add Tools section
    for item in nav:
        if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
            handbook = item['Part 3 - Architect\'s Handbook']
            
            # Add Tools section after Learning Paths
            tools_section = []
            for i, h_item in enumerate(handbook):
                if isinstance(h_item, dict) and 'Learning Paths' in h_item:
                    handbook.insert(i + 1, {'Interactive Tools': tools_section})
                    break
            
            for title, filename in NAV_ADDITIONS['tools']:
                path = f'architects-handbook/tools/{filename}'
                if Path(f'docs/{path}').exists():
                    tools_section.append({title: path})
                    added += 1
    
    # Add advanced quantitative topics
    for item in nav:
        if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
            for sub in item['Part 3 - Architect\'s Handbook']:
                if isinstance(sub, dict) and 'Quantitative Analysis' in sub:
                    quant = sub['Quantitative Analysis']
                    
                    # Add Advanced Topics subsection
                    advanced = []
                    quant.append({'Advanced Topics': advanced})
                    
                    for title, filename in NAV_ADDITIONS['quantitative_advanced']:
                        path = f'architects-handbook/quantitative-analysis/{filename}'
                        if Path(f'docs/{path}').exists():
                            advanced.append({title: path})
                            added += 1
    
    # Write back
    with open('mkdocs.yml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    
    return added

def main():
    print("=== Final Cleanup ===\n")
    
    # 1. Move tools
    print("1. Moving tools to architects handbook...")
    moved = move_tools()
    print(f"   Moved {moved} files\n")
    
    # 2. Remove unnecessary files
    print("2. Removing unnecessary files and directories...")
    removed = remove_files_and_dirs()
    print(f"   Removed {removed} items\n")
    
    # 3. Update navigation
    print("3. Adding remaining valuable files to navigation...")
    added = update_navigation()
    print(f"   Added {added} entries\n")
    
    print("=== Cleanup Complete ===")

if __name__ == "__main__":
    main()
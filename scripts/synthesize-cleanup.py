#!/usr/bin/env python3
"""
Synthesize and clean up remaining orphaned files
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

# Define cleanup actions
ACTIONS = {
    # 1. Remove template/example files (not needed in production)
    'remove': [
        'examples/',  # All example files
        'templates/',  # All template files
        'reports/cleanup-report-2025-01-29.md',  # Old cleanup report
        'excellence/EXCELLENCE_GUIDES_COMPLETE.md',  # Tracking file
        'excellence/EXCELLENCE_STRUCTURE_COMPLETE.md',  # Tracking file
        'excellence/case-study-organization-examples.md',  # Example file
        'excellence/case-study-template.md',  # Template
        'excellence/migration-guide-template.md',  # Template
        'excellence/pattern-reorganization-output.md',  # Temp file
        'pattern-library/deployment/',  # Duplicate deployment patterns
        'pattern-library/observability/',  # Duplicate observability patterns
    ],
    
    # 2. Move human factors to architects handbook
    'move': {
        'human-factors/': 'architects-handbook/human-factors/',
    },
    
    # 3. Move quantitative files to architects handbook
    'move_quantitative': {
        'quantitative/': 'architects-handbook/quantitative-analysis/',
    },
    
    # 4. Move learning paths to architects handbook
    'move_learning': {
        'learning-paths/': 'architects-handbook/learning-paths/',
    },
    
    # 5. Add to navigation
    'add_to_nav': {
        # Reference section
        'reference': [
            ('Glossary', 'glossary.md'),
            ('Navigation Guide', 'navigation-guide.md'),
            ('Navigation Maintenance', 'navigation-maintenance.md'),
            ('Law Mapping Guide', 'law-mapping-guide.md'),
            ('Admonition Guide', 'admonition-guide.md'),
            ('Recipe Cards', 'recipe-cards.md'),
        ],
        
        # More case studies
        'case_studies_infrastructure': [
            ('URL Shortener', 'url-shortener.md'),
            ('Web Crawler', 'web-crawler.md'),
            ('Object Storage', 'object-storage.md'),
            ('S3 Object Storage', 's3-object-storage-enhanced.md'),
            ('Unique ID Generator', 'unique-id-generator.md'),
            ('Blockchain', 'blockchain.md'),
            ('Consistent Hashing', 'consistent-hashing.md'),
            ('Zoom Scaling', 'zoom-scaling.md'),
        ],
        
        # More location services
        'case_studies_location': [
            ('Find My Device', 'find-my-device.md'),
            ('HERE Maps', 'here-maps.md'),
            ('Life360', 'life360.md'),
            ('Snap Map', 'snap-map.md'),
            ('Strava Heatmaps', 'strava-heatmaps.md'),
            ('OpenStreetMap', 'openstreetmap.md'),
        ],
        
        # Human factors (after move)
        'human_factors': [
            ('Chaos Engineering', 'chaos-engineering.md'),
            ('Blameless Postmortems', 'blameless-postmortems.md'),
            ('On-Call Culture', 'oncall-culture.md'),
            ('Incident Response', 'incident-response.md'),
            ('SRE Practices', 'sre-practices.md'),
            ('Production Readiness', 'production-readiness-reviews.md'),
            ('Monitoring & Observability', 'monitoring-observability-debugging.md'),
            ('Team Topologies', 'team-topologies.md'),
            ('Consistency Tuning', 'consistency-tuning.md'),
        ],
        
        # Learning paths (after move)
        'learning_paths': [
            ('New Graduate Path', 'new-graduate.md'),
            ('Senior Engineer Path', 'senior-engineer.md'),
            ('Architect Path', 'architect.md'),
            ('Manager Path', 'manager.md'),
            ('Performance Focus', 'performance.md'),
            ('Reliability Focus', 'reliability.md'),
            ('Consistency Focus', 'consistency.md'),
            ('Cost Optimization', 'cost.md'),
        ],
    },
    
    # 6. Merge duplicate database case studies
    'merge': {
        'architects-handbook/case-studies/databases/amazon-dynamodb.md': 'architects-handbook/case-studies/databases/amazon-dynamo.md',
        'architects-handbook/case-studies/databases/redis.md': 'architects-handbook/case-studies/databases/redis-architecture.md',
        'architects-handbook/case-studies/databases/facebook-memcached.md': 'architects-handbook/case-studies/databases/memcached.md',
    }
}

def remove_files(patterns):
    """Remove files matching patterns"""
    removed = 0
    for pattern in patterns:
        if pattern.endswith('/'):
            # Remove directory
            dir_path = Path(f'docs/{pattern}')
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"Removed directory: {pattern}")
                removed += 1
        else:
            # Remove file
            file_path = Path(f'docs/{pattern}')
            if file_path.exists():
                file_path.unlink()
                print(f"Removed file: {pattern}")
                removed += 1
    return removed

def move_files(mappings):
    """Move files from source to destination"""
    moved = 0
    for src, dst in mappings.items():
        src_path = Path(f'docs/{src}')
        dst_path = Path(f'docs/{dst}')
        
        if src_path.exists():
            if src_path.is_dir():
                # Create destination directory
                dst_path.mkdir(parents=True, exist_ok=True)
                
                # Move all files in directory
                for file in src_path.glob('*.md'):
                    dst_file = dst_path / file.name
                    if not dst_file.exists():
                        shutil.move(str(file), str(dst_file))
                        print(f"Moved: {file.name} to {dst}")
                        moved += 1
                # Remove empty source directory
                if not list(src_path.iterdir()):
                    src_path.rmdir()
            else:
                # Create destination directory
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                # Move single file
                shutil.move(str(src_path), str(dst_path))
                print(f"Moved: {src} to {dst}")
                moved += 1
    return moved

def merge_files(mappings):
    """Merge duplicate files"""
    merged = 0
    for src, dst in mappings.items():
        src_path = Path(f'docs/{src}')
        if src_path.exists():
            src_path.unlink()
            print(f"Removed duplicate: {src} (keeping {dst})")
            merged += 1
    return merged

def update_navigation(additions):
    """Update mkdocs.yml with new entries"""
    # Load mkdocs.yml
    with open('mkdocs.yml', 'r') as f:
        config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
    
    nav = config.get('nav', [])
    added = 0
    
    # Add reference items
    if 'reference' in additions:
        for item in nav:
            if isinstance(item, dict) and 'Contributing' in item:
                contrib_section = item['Contributing']
                for title, filename in additions['reference']:
                    path = f'reference/{filename}'
                    if Path(f'docs/{path}').exists() and not any(path in str(i) for i in contrib_section):
                        contrib_section.append({title: path})
                        added += 1
    
    # Add infrastructure case studies
    if 'case_studies_infrastructure' in additions:
        for item in nav:
            if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
                for sub in item['Part 3 - Architect\'s Handbook']:
                    if isinstance(sub, dict) and 'Case Studies' in sub:
                        for cs in sub['Case Studies']:
                            if isinstance(cs, dict) and 'Technology Deep Dives' in cs:
                                for td in cs['Technology Deep Dives']:
                                    if isinstance(td, dict) and 'Infrastructure' in td:
                                        infra = td['Infrastructure']
                                        for title, filename in additions['case_studies_infrastructure']:
                                            path = f'architects-handbook/case-studies/infrastructure/{filename}'
                                            if Path(f'docs/{path}').exists() and not any(path in str(i) for i in infra):
                                                infra.append({title: path})
                                                added += 1
    
    # Add location services
    if 'case_studies_location' in additions:
        for item in nav:
            if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
                for sub in item['Part 3 - Architect\'s Handbook']:
                    if isinstance(sub, dict) and 'Case Studies' in sub:
                        for cs in sub['Case Studies']:
                            if isinstance(cs, dict) and 'System Design' in cs:
                                sys_design = cs['System Design']
                                for title, filename in additions['case_studies_location']:
                                    path = f'architects-handbook/case-studies/location-services/{filename}'
                                    if Path(f'docs/{path}').exists() and not any(path in str(i) for i in sys_design):
                                        sys_design.append({title: path})
                                        added += 1
    
    # Add human factors
    if 'human_factors' in additions:
        for item in nav:
            if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
                for sub in item['Part 3 - Architect\'s Handbook']:
                    if isinstance(sub, dict) and 'Human Factors' in sub:
                        human = sub['Human Factors']
                        for title, filename in additions['human_factors']:
                            path = f'architects-handbook/human-factors/{filename}'
                            if Path(f'docs/{path}').exists() and not any(path in str(i) for i in human):
                                human.append({title: path})
                                added += 1
    
    # Add learning paths
    if 'learning_paths' in additions:
        for item in nav:
            if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
                handbook = item['Part 3 - Architect\'s Handbook']
                
                # Find or create Learning Paths section
                lp_section = None
                for h_item in handbook:
                    if isinstance(h_item, dict) and 'Learning Paths' in h_item:
                        lp_section = h_item['Learning Paths']
                        break
                
                if lp_section is None:
                    lp_section = [{'Overview': 'architects-handbook/learning-paths/index.md'}]
                    handbook.append({'Learning Paths': lp_section})
                
                for title, filename in additions['learning_paths']:
                    path = f'architects-handbook/learning-paths/{filename}'
                    if Path(f'docs/{path}').exists() and not any(path in str(i) for i in lp_section):
                        lp_section.append({title: path})
                        added += 1
    
    # Write back
    with open('mkdocs.yml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    
    return added

def main():
    print("=== Starting Orphaned Files Cleanup ===\n")
    
    # 1. Remove unnecessary files
    print("1. Removing template/example files...")
    removed = remove_files(ACTIONS['remove'])
    print(f"   Removed {removed} files/directories\n")
    
    # 2. Move human factors
    print("2. Moving human factors to architects handbook...")
    moved = move_files(ACTIONS['move'])
    print(f"   Moved {moved} files\n")
    
    # 3. Move quantitative files
    print("3. Moving quantitative files to architects handbook...")
    moved_quant = move_files(ACTIONS['move_quantitative'])
    print(f"   Moved {moved_quant} files\n")
    
    # 4. Move learning paths
    print("4. Moving learning paths to architects handbook...")
    moved_lp = move_files(ACTIONS['move_learning'])
    print(f"   Moved {moved_lp} files\n")
    
    # 5. Merge duplicate files
    print("5. Merging duplicate case studies...")
    merged = merge_files(ACTIONS['merge'])
    print(f"   Merged {merged} files\n")
    
    # 6. Update navigation
    print("6. Updating navigation...")
    added = update_navigation(ACTIONS['add_to_nav'])
    print(f"   Added {added} entries to navigation\n")
    
    print("=== Cleanup Complete ===")
    print(f"Total changes: {removed + moved + moved_quant + moved_lp + merged} files processed")
    print(f"Navigation entries added: {added}")

if __name__ == "__main__":
    main()
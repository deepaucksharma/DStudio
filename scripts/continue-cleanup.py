#!/usr/bin/env python3
"""
Continue cleanup after moving directories
"""

import os
import yaml
from pathlib import Path

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

# Files to remove
TO_REMOVE = [
    # Duplicate database files
    'docs/architects-handbook/case-studies/databases/amazon-dynamodb.md',
    'docs/architects-handbook/case-studies/databases/redis.md',
    'docs/architects-handbook/case-studies/databases/facebook-memcached.md',
    
    # Old excellence tracking files
    'docs/excellence/case-study-template.md',
    'docs/excellence/migration-guide-template.md',
    'docs/excellence/pattern-reorganization-output.md',
    
    # Pattern duplicates
    'docs/pattern-library/data-management/data-mesh.md',
    'docs/pattern-library/data-management/geohashing.md',
    'docs/pattern-library/data-management/singleton-database.md',
    'docs/pattern-library/data-management/stored-procedures.md',
    'docs/pattern-library/scaling/database-per-service.md',
    'docs/pattern-library/resilience/idempotent-receiver.md',
    'docs/pattern-library/resilience/timeout-advanced.md',
    'docs/pattern-library/scaling/adaptive-scheduling.md',
    'docs/pattern-library/scaling/content-delivery-network.md',
    'docs/pattern-library/scaling/database-sharding.md',
    'docs/pattern-library/scaling/geographic-load-balancing.md',
    'docs/pattern-library/scaling/horizontal-pod-autoscaler.md',
    'docs/pattern-library/scaling/request-routing.md',
    'docs/pattern-library/scaling/single-socket-channel.md',
    'docs/pattern-library/scaling/spatial-indexing.md',
    'docs/pattern-library/scaling/thick-client.md',
    'docs/pattern-library/scaling/time-series-ids.md',
]

# Navigation additions
NAV_ADDITIONS = {
    'reference': [
        ('Glossary', 'glossary.md'),
        ('Navigation Guide', 'navigation-guide.md'),
        ('Navigation Maintenance', 'navigation-maintenance.md'),
        ('Law Mapping Guide', 'law-mapping-guide.md'),
        ('Admonition Guide', 'admonition-guide.md'),
        ('Recipe Cards', 'recipe-cards.md'),
        ('Offline Support', 'offline.md'),
    ],
    
    'case_studies_infrastructure': [
        ('URL Shortener', 'url-shortener.md'),
        ('Web Crawler', 'web-crawler.md'),
        ('Object Storage', 'object-storage.md'),
        ('S3 Object Storage', 's3-object-storage-enhanced.md'),
        ('Unique ID Generator', 'unique-id-generator.md'),
        ('Blockchain', 'blockchain.md'),
        ('Consistent Hashing', 'consistent-hashing.md'),
        ('Zoom Scaling', 'zoom-scaling.md'),
        ('Monolith to Microservices', 'monolith-to-microservices.md'),
    ],
    
    'case_studies_location': [
        ('Find My Device', 'find-my-device.md'),
        ('HERE Maps', 'here-maps.md'),
        ('Life360', 'life360.md'),
        ('Snap Map', 'snap-map.md'),
        ('Strava Heatmaps', 'strava-heatmaps.md'),
        ('OpenStreetMap', 'openstreetmap.md'),
        ('Uber Maps', 'uber-maps.md'),
        ('Google Maps System', 'google-maps-system.md'),
    ],
    
    'case_studies_messaging': [
        ('Batch to Streaming', 'batch-to-streaming.md'),
        ('Polling to Event Driven', 'polling-to-event-driven.md'),
    ],
    
    'human_factors': [
        ('Knowledge Management', 'knowledge-management.md'),
        ('Runbooks & Playbooks', 'runbooks-playbooks.md'),
        ('Observability Stacks', 'observability-stacks.md'),
        ('Org Structure', 'org-structure.md'),
    ],
    
    'learning_paths': [
        ('Overview', 'index.md'),
        ('New Graduate Path', 'new-graduate.md'),
        ('Senior Engineer Path', 'senior-engineer.md'),
        ('Architect Path', 'architect.md'),
        ('Manager Path', 'manager.md'),
        ('Performance Focus', 'performance.md'),
        ('Reliability Focus', 'reliability.md'),
        ('Consistency Focus', 'consistency.md'),
        ('Cost Optimization', 'cost.md'),
    ],
}

def remove_files():
    """Remove duplicate and unnecessary files"""
    removed = 0
    for file_path in TO_REMOVE:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            print(f"Removed: {file_path}")
            removed += 1
    return removed

def update_navigation():
    """Update navigation with remaining orphaned files"""
    # Load mkdocs.yml
    with open('mkdocs.yml', 'r') as f:
        config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
    
    nav = config.get('nav', [])
    added = 0
    
    # Add reference items
    for item in nav:
        if isinstance(item, dict) and 'Contributing' in item:
            contrib_section = item['Contributing']
            for title, filename in NAV_ADDITIONS['reference']:
                path = f'reference/{filename}'
                if Path(f'docs/{path}').exists() and not any(path in str(i) for i in contrib_section):
                    contrib_section.append({title: path})
                    added += 1
    
    # Add infrastructure case studies  
    for item in nav:
        if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
            for sub in item['Part 3 - Architect\'s Handbook']:
                if isinstance(sub, dict) and 'Case Studies' in sub:
                    for cs in sub['Case Studies']:
                        if isinstance(cs, dict) and 'Technology Deep Dives' in cs:
                            for td in cs['Technology Deep Dives']:
                                if isinstance(td, dict) and 'Infrastructure' in td:
                                    infra = td['Infrastructure']
                                    for title, filename in NAV_ADDITIONS['case_studies_infrastructure']:
                                        path = f'architects-handbook/case-studies/infrastructure/{filename}'
                                        if Path(f'docs/{path}').exists() and not any(path in str(i) for i in infra):
                                            infra.append({title: path})
                                            added += 1
    
    # Add more location services
    for item in nav:
        if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
            for sub in item['Part 3 - Architect\'s Handbook']:
                if isinstance(sub, dict) and 'Case Studies' in sub:
                    for cs in sub['Case Studies']:
                        if isinstance(cs, dict) and 'System Design' in cs:
                            sys_design = cs['System Design']
                            for title, filename in NAV_ADDITIONS['case_studies_location']:
                                path = f'architects-handbook/case-studies/location-services/{filename}'
                                if Path(f'docs/{path}').exists() and not any(path in str(i) for i in sys_design):
                                    sys_design.append({title: path})
                                    added += 1
    
    # Add messaging case studies
    for item in nav:
        if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
            for sub in item['Part 3 - Architect\'s Handbook']:
                if isinstance(sub, dict) and 'Case Studies' in sub:
                    for cs in sub['Case Studies']:
                        if isinstance(cs, dict) and 'Technology Deep Dives' in cs:
                            for td in cs['Technology Deep Dives']:
                                if isinstance(td, dict) and 'Message Systems' in td:
                                    msg = td['Message Systems']
                                    for title, filename in NAV_ADDITIONS['case_studies_messaging']:
                                        path = f'architects-handbook/case-studies/messaging-streaming/{filename}'
                                        if Path(f'docs/{path}').exists() and not any(path in str(i) for i in msg):
                                            msg.append({title: path})
                                            added += 1
    
    # Add human factors
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
    
    # Add learning paths section
    for item in nav:
        if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
            handbook = item['Part 3 - Architect\'s Handbook']
            
            # Create Learning Paths section
            lp_section = []
            handbook.append({'Learning Paths': lp_section})
            
            for title, filename in NAV_ADDITIONS['learning_paths']:
                path = f'architects-handbook/learning-paths/{filename}'
                if Path(f'docs/{path}').exists():
                    lp_section.append({title: path})
                    added += 1
    
    # Write back
    with open('mkdocs.yml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    
    return added

def main():
    print("=== Continuing Cleanup ===\n")
    
    # 1. Remove duplicate files
    print("1. Removing duplicate/unnecessary files...")
    removed = remove_files()
    print(f"   Removed {removed} files\n")
    
    # 2. Update navigation
    print("2. Updating navigation with remaining orphaned files...")
    added = update_navigation()
    print(f"   Added {added} entries to navigation\n")
    
    print("=== Cleanup Complete ===")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Add orphaned files that actually exist to navigation
"""

import yaml
import os
from pathlib import Path

# Custom YAML constructors to handle MkDocs-specific tags
class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    """A custom YAML loader that ignores unknown tags"""
    pass

def ignore_unknown(loader, suffix, node):
    """Ignore unknown tags by returning empty string"""
    if isinstance(node, yaml.ScalarNode):
        return ''
    elif isinstance(node, yaml.SequenceNode):
        return []
    elif isinstance(node, yaml.MappingNode):
        return {}
    
# Add constructor for any unknown tag
SafeLoaderIgnoreUnknown.add_multi_constructor('', ignore_unknown)

def title_from_filename(filename):
    """Convert filename to title"""
    name = filename.replace('.md', '')
    # Convert kebab-case to Title Case
    words = name.split('-')
    title = ' '.join(word.capitalize() for word in words)
    # Special cases
    title = title.replace('Dynamodb', 'DynamoDB')
    title = title.replace('Mongodb', 'MongoDB')
    title = title.replace('Rabbitmq', 'RabbitMQ')
    title = title.replace('Grpc', 'gRPC')
    title = title.replace('Api', 'API')
    title = title.replace('Sre', 'SRE')
    title = title.replace('Aws', 'AWS')
    title = title.replace('Gcp', 'GCP')
    title = title.replace('Cdn', 'CDN')
    title = title.replace('Crdt', 'CRDT')
    title = title.replace('Cdc', 'CDC')
    title = title.replace('Cqrs', 'CQRS')
    title = title.replace('Faas', 'FaaS')
    title = title.replace('Hlc', 'HLC')
    title = title.replace('Lsm', 'LSM')
    title = title.replace('Cas', 'CAS')
    return title

def add_to_navigation(config):
    """Add orphaned files to navigation"""
    nav = config.get('nav', [])
    added_count = 0
    
    # Add Elite Engineering case studies
    for item in nav:
        if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
            for sub_item in item['Part 3 - Architect\'s Handbook']:
                if isinstance(sub_item, dict) and 'Case Studies' in sub_item:
                    case_studies = sub_item['Case Studies']
                    
                    # Add Elite Engineering section if not exists
                    elite_eng_section = None
                    for cs_item in case_studies:
                        if isinstance(cs_item, dict) and 'Elite Engineering' in cs_item:
                            elite_eng_section = cs_item['Elite Engineering']
                            break
                    
                    if elite_eng_section is None:
                        # Create new section after Technology Deep Dives
                        elite_eng_section = []
                        for i, cs_item in enumerate(case_studies):
                            if isinstance(cs_item, dict) and 'Technology Deep Dives' in cs_item:
                                case_studies.insert(i + 1, {'Elite Engineering': elite_eng_section})
                                break
                    
                    # Add elite engineering files
                    elite_path = Path('docs/architects-handbook/case-studies/elite-engineering')
                    if elite_path.exists():
                        for file in sorted(elite_path.glob('*.md')):
                            if file.name != 'index.md':
                                nav_path = f'architects-handbook/case-studies/elite-engineering/{file.name}'
                                if not any(nav_path in str(item) for item in elite_eng_section):
                                    title = title_from_filename(file.name)
                                    elite_eng_section.append({title: nav_path})
                                    added_count += 1
                    
                    # Add more categories
                    # Financial & Commerce
                    fin_section = None
                    for cs_item in case_studies:
                        if isinstance(cs_item, dict) and 'Financial & Commerce' in cs_item:
                            fin_section = cs_item['Financial & Commerce']
                            break
                    
                    if fin_section is None:
                        fin_section = []
                        case_studies.insert(2, {'Financial & Commerce': fin_section})
                    
                    fin_path = Path('docs/architects-handbook/case-studies/financial-commerce')
                    if fin_path.exists():
                        for file in sorted(fin_path.glob('*.md')):
                            if file.name != 'index.md' and file.name != 'payment-system.md':  # Skip already added
                                nav_path = f'architects-handbook/case-studies/financial-commerce/{file.name}'
                                if not any(nav_path in str(item) for item in fin_section):
                                    title = title_from_filename(file.name)
                                    fin_section.append({title: nav_path})
                                    added_count += 1
                    
                    # Social & Communication
                    social_section = None
                    for cs_item in case_studies:
                        if isinstance(cs_item, dict) and 'Social & Communication' in cs_item:
                            social_section = cs_item['Social & Communication']
                            break
                    
                    if social_section is None:
                        social_section = []
                        case_studies.insert(3, {'Social & Communication': social_section})
                    
                    social_path = Path('docs/architects-handbook/case-studies/social-communication')
                    if social_path.exists():
                        for file in sorted(social_path.glob('*.md')):
                            if file.name != 'index.md' and file.name != 'news-feed.md':  # Skip already added
                                nav_path = f'architects-handbook/case-studies/social-communication/{file.name}'
                                if not any(nav_path in str(item) for item in social_section):
                                    title = title_from_filename(file.name)
                                    social_section.append({title: nav_path})
                                    added_count += 1
                    
                    # Search & Analytics
                    search_section = None
                    for cs_item in case_studies:
                        if isinstance(cs_item, dict) and 'Search & Analytics' in cs_item:
                            search_section = cs_item['Search & Analytics']
                            break
                    
                    if search_section is None:
                        search_section = []
                        case_studies.insert(4, {'Search & Analytics': search_section})
                    
                    search_path = Path('docs/architects-handbook/case-studies/search-analytics')
                    if search_path.exists():
                        for file in sorted(search_path.glob('*.md')):
                            if file.name != 'index.md':
                                nav_path = f'architects-handbook/case-studies/search-analytics/{file.name}'
                                if not any(nav_path in str(item) for item in search_section):
                                    title = title_from_filename(file.name)
                                    search_section.append({title: nav_path})
                                    added_count += 1
                    
                    # Monitoring & Observability
                    monitor_section = None
                    for cs_item in case_studies:
                        if isinstance(cs_item, dict) and 'Monitoring & Observability' in cs_item:
                            monitor_section = cs_item['Monitoring & Observability']
                            break
                    
                    if monitor_section is None:
                        monitor_section = []
                        # Add to Technology Deep Dives
                        for cs_item in case_studies:
                            if isinstance(cs_item, dict) and 'Technology Deep Dives' in cs_item:
                                tech_dives = cs_item['Technology Deep Dives']
                                tech_dives.append({'Monitoring & Observability': monitor_section})
                                break
                    
                    monitor_path = Path('docs/architects-handbook/case-studies/monitoring-observability')
                    if monitor_path.exists():
                        for file in sorted(monitor_path.glob('*.md')):
                            if file.name != 'index.md' and file.name != 'prometheus.md':  # Skip already added
                                nav_path = f'architects-handbook/case-studies/monitoring-observability/{file.name}'
                                if not any(nav_path in str(item) for item in monitor_section):
                                    title = title_from_filename(file.name)
                                    monitor_section.append({title: nav_path})
                                    added_count += 1
    
    # Add coordination patterns that actually exist
    for item in nav:
        if isinstance(item, dict) and 'Part 2 - Pattern Library' in item:
            for sub_item in item['Part 2 - Pattern Library']:
                if isinstance(sub_item, dict) and 'Coordination Patterns' in sub_item:
                    coord_section = sub_item['Coordination Patterns']
                    coord_path = Path('docs/pattern-library/coordination')
                    
                    if coord_path.exists():
                        existing_files = set()
                        for cs_item in coord_section:
                            if isinstance(cs_item, dict):
                                for _, path in cs_item.items():
                                    existing_files.add(Path(path).name)
                        
                        for file in sorted(coord_path.glob('*.md')):
                            if file.name != 'index.md' and file.name not in existing_files:
                                nav_path = f'pattern-library/coordination/{file.name}'
                                # Verify file exists
                                if Path(f'docs/{nav_path}').exists():
                                    title = title_from_filename(file.name)
                                    coord_section.append({title: nav_path})
                                    added_count += 1
    
    # Add additional location services
    for item in nav:
        if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
            for sub_item in item['Part 3 - Architect\'s Handbook']:
                if isinstance(sub_item, dict) and 'Case Studies' in sub_item:
                    for cs_item in sub_item['Case Studies']:
                        if isinstance(cs_item, dict) and 'System Design' in cs_item:
                            sys_design = cs_item['System Design']
                            
                            # Add Location Services subsection
                            location_path = Path('docs/architects-handbook/case-studies/location-services')
                            if location_path.exists():
                                # Add more location service case studies
                                location_files = [
                                    'google-maps.md',
                                    'apple-maps.md', 
                                    'nearby-friends.md',
                                    'proximity-service.md'
                                ]
                                
                                for filename in location_files:
                                    file_path = location_path / filename
                                    if file_path.exists():
                                        nav_path = f'architects-handbook/case-studies/location-services/{filename}'
                                        if not any(nav_path in str(item) for item in sys_design):
                                            title = title_from_filename(filename)
                                            sys_design.append({title: nav_path})
                                            added_count += 1
    
    print(f"Added {added_count} orphaned files to navigation")
    return config

def main():
    # Load mkdocs.yml
    with open('mkdocs.yml', 'r') as f:
        config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
    
    # Add orphaned files
    config = add_to_navigation(config)
    
    # Write back
    with open('mkdocs.yml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)

if __name__ == "__main__":
    main()
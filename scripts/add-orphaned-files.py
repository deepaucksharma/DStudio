#!/usr/bin/env python3
"""
Add orphaned files to mkdocs.yml navigation after due diligence
"""

import yaml
import json
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

# Files to add to navigation
ADDITIONS = {
    # Case Studies - Additional Databases
    'architects-handbook/case-studies/databases': [
        ('Google Spanner', 'google-spanner.md'),
        ('Amazon Aurora', 'amazon-aurora.md'),
        ('ZooKeeper', 'zookeeper.md'),
        ('Vault', 'vault.md'),
        ('Memcached', 'memcached.md'),
        ('Key-Value Store Design', 'key-value-store.md'),
    ],
    
    # Case Studies - Additional Infrastructure
    'architects-handbook/case-studies/infrastructure': [
        ('Docker', 'docker.md'),
        ('Apache Flink', 'apache-flink.md'),
        ('Apache Storm', 'apache-storm.md'),
        ('Envoy Proxy', 'envoy-proxy.md'),
        ('Consul', 'consul.md'),
        ('Vault', 'vault.md'),
    ],
    
    # Case Studies - Additional Messaging/Streaming
    'architects-handbook/case-studies/messaging-streaming': [
        ('Apache Spark', 'apache-spark.md'),
        ('Apache Pulsar', 'apache-pulsar.md'),
        ('MapReduce', 'mapreduce.md'),
        ('RabbitMQ', 'rabbitmq.md'),
    ],
    
    # Pattern Library - Additional Communication Patterns
    'pattern-library/communication': [
        ('gRPC', 'grpc.md'),
        ('Request-Reply', 'request-reply.md'),
    ],
    
    # Pattern Library - Additional Coordination Patterns
    'pattern-library/coordination': [
        ('Actor Model', 'actor-model.md'),
        ('Distributed Lock', 'distributed-lock.md'),
        ('Distributed Queue', 'distributed-queue.md'),
        ('Emergent Leader', 'emergent-leader.md'),
        ('Leader Election', 'leader-election.md'),
        ('Quorum', 'quorum.md'),
        ('Request Waiting List', 'request-waiting-list.md'),
        ('Single Update Queue', 'single-update-queue.md'),
        ('Two-Phase Commit', 'two-phase-commit.md'),
        ('Vector Clocks', 'vector-clocks.md'),
    ],
    
    # Pattern Library - Additional Data Management
    'pattern-library/data-management': [
        ('Gossip Protocol', 'gossip-protocol.md'),
        ('Idempotent Consumer', 'idempotent-consumer.md'),
        ('Low-High Water Marks', 'low-high-water-marks.md'),
        ('Phi Accrual Failure Detector', 'phi-accrual-failure-detector.md'),
        ('Replicated Log', 'replicated-log.md'),
        ('Time-Based UUID', 'time-based-uuid.md'),
        ('Versioned Value', 'versioned-value.md'),
    ],
    
    # Pattern Library - Additional Scaling Patterns
    'pattern-library/scaling': [
        ('Blue-Green Deployment', 'blue-green-deployment.md'),
        ('Canary Deployment', 'canary-deployment.md'),
        ('Command Sourcing', 'command-sourcing.md'),
        ('Database per Service', 'database-per-service.md'),
        ('Geohashing', 'geohashing.md'),
        ('Shared Database', 'shared-database.md'),
        ('Throttling', 'throttling.md'),
    ],
    
    # Human Factors - Missing sections
    'architects-handbook/human-factors': [
        ('Chaos Engineering', 'chaos-engineering.md'),
        ('Observability Strategy', 'observability.md'),
        ('Team Topologies', 'team-topologies.md'),
        ('Blameless Postmortems', 'blameless-postmortems.md'),
        ('On-Call Best Practices', 'oncall-culture.md'),
        ('Incident Response', 'incident-response.md'),
        ('SRE Practices', 'sre-practices.md'),
        ('Production Readiness', 'production-readiness-reviews.md'),
        ('Consistency Tuning', 'consistency-tuning.md'),
        ('Monitoring Strategy', 'monitoring-observability-debugging.md'),
    ],
    
    # Reference - Additional Resources
    'reference': [
        ('Glossary', 'glossary.md'),
        ('Pattern Health Dashboard', 'pattern-health-dashboard.md'),
        ('Security Considerations', 'security.md'),
        ('Cheat Sheets', 'cheat-sheets.md'),
        ('Keyboard Shortcuts', 'keyboard-shortcuts.md'),
        ('Tags', 'tags.md'),
    ],
}

def find_nav_section(nav, path_parts):
    """Find the section in navigation where we should add items"""
    current = nav
    
    for part in path_parts:
        found = False
        for item in current:
            if isinstance(item, dict):
                for key, value in item.items():
                    if part.lower() in key.lower():
                        current = value
                        found = True
                        break
            if found:
                break
        
        if not found:
            return None
    
    return current

def add_to_navigation(config, additions):
    """Add orphaned files to appropriate sections"""
    nav = config.get('nav', [])
    
    # Initialize sections
    db_section = None
    msg_section = None
    infra_section = None
    
    # Find Case Studies sections
    for item in nav:
        if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
            for sub_item in item['Part 3 - Architect\'s Handbook']:
                if isinstance(sub_item, dict) and 'Case Studies' in sub_item:
                    for case_item in sub_item['Case Studies']:
                        if isinstance(case_item, dict) and 'Technology Deep Dives' in case_item:
                            for tech_item in case_item['Technology Deep Dives']:
                                if isinstance(tech_item, dict) and 'Databases' in tech_item:
                                    db_section = tech_item['Databases']
                                elif isinstance(tech_item, dict) and 'Message Systems' in tech_item:
                                    msg_section = tech_item['Message Systems']
                                elif isinstance(tech_item, dict) and 'Infrastructure' in tech_item:
                                    infra_section = tech_item['Infrastructure']
    
    # Add database case studies
    if db_section and 'architects-handbook/case-studies/databases' in additions:
        for title, filename in additions['architects-handbook/case-studies/databases']:
            path = f'architects-handbook/case-studies/databases/{filename}'
            # Check if not already in nav
            if not any(path in str(item) for item in db_section):
                db_section.append({title: path})
    
    # Add infrastructure case studies
    if infra_section and 'architects-handbook/case-studies/infrastructure' in additions:
        for title, filename in additions['architects-handbook/case-studies/infrastructure']:
            path = f'architects-handbook/case-studies/infrastructure/{filename}'
            if not any(path in str(item) for item in infra_section):
                infra_section.append({title: path})
    
    # Add messaging case studies
    if msg_section and 'architects-handbook/case-studies/messaging-streaming' in additions:
        for title, filename in additions['architects-handbook/case-studies/messaging-streaming']:
            path = f'architects-handbook/case-studies/messaging-streaming/{filename}'
            if not any(path in str(item) for item in msg_section):
                msg_section.append({title: path})
    
    # Add Pattern Library items
    for item in nav:
        if isinstance(item, dict) and 'Part 2 - Pattern Library' in item:
            for sub_item in item['Part 2 - Pattern Library']:
                if isinstance(sub_item, dict):
                    # Communication Patterns
                    if 'Communication Patterns' in sub_item:
                        comm_section = sub_item['Communication Patterns']
                        if 'pattern-library/communication' in additions:
                            for title, filename in additions['pattern-library/communication']:
                                path = f'pattern-library/communication/{filename}'
                                if not any(path in str(i) for i in comm_section):
                                    comm_section.append({title: path})
                    
                    # Coordination Patterns
                    elif 'Coordination Patterns' in sub_item:
                        coord_section = sub_item['Coordination Patterns']
                        if 'pattern-library/coordination' in additions:
                            for title, filename in additions['pattern-library/coordination']:
                                path = f'pattern-library/coordination/{filename}'
                                if not any(path in str(i) for i in coord_section):
                                    coord_section.append({title: path})
                    
                    # Data Management Patterns
                    elif 'Data Management Patterns' in sub_item:
                        data_section = sub_item['Data Management Patterns']
                        if 'pattern-library/data-management' in additions:
                            for title, filename in additions['pattern-library/data-management']:
                                path = f'pattern-library/data-management/{filename}'
                                if not any(path in str(i) for i in data_section):
                                    data_section.append({title: path})
                    
                    # Scaling Patterns
                    elif 'Scaling Patterns' in sub_item:
                        scale_section = sub_item['Scaling Patterns']
                        if 'pattern-library/scaling' in additions:
                            for title, filename in additions['pattern-library/scaling']:
                                path = f'pattern-library/scaling/{filename}'
                                if not any(path in str(i) for i in scale_section):
                                    scale_section.append({title: path})
    
    # Add Human Factors items
    for item in nav:
        if isinstance(item, dict) and 'Part 3 - Architect\'s Handbook' in item:
            for sub_item in item['Part 3 - Architect\'s Handbook']:
                if isinstance(sub_item, dict) and 'Human Factors' in sub_item:
                    human_section = sub_item['Human Factors']
                    if 'architects-handbook/human-factors' in additions:
                        for title, filename in additions['architects-handbook/human-factors']:
                            path = f'architects-handbook/human-factors/{filename}'
                            # Skip files that don't exist
                            if Path(f'docs/{path}').exists() and not any(path in str(i) for i in human_section):
                                human_section.append({title: path})
    
    # Add Reference items
    for item in nav:
        if isinstance(item, dict) and 'Contributing' in item:
            ref_section = item['Contributing']
            if 'reference' in additions:
                for title, filename in additions['reference']:
                    path = f'reference/{filename}'
                    if Path(f'docs/{path}').exists() and not any(path in str(i) for i in ref_section):
                        ref_section.append({title: path})
    
    return config

def main():
    # Load mkdocs.yml
    with open('mkdocs.yml', 'r') as f:
        config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
    
    # Add orphaned files
    config = add_to_navigation(config, ADDITIONS)
    
    # Write back the updated config
    with open('mkdocs.yml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    
    print("Added orphaned files to mkdocs.yml navigation")

if __name__ == "__main__":
    main()
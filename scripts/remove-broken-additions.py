#!/usr/bin/env python3
"""
Remove broken links that were mistakenly added
"""

import yaml

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

# List of broken links to remove
BROKEN_LINKS = [
    'pattern-library/coordination/quorum.md',
    'pattern-library/data-management/low-high-water-marks.md',
    'architects-handbook/case-studies/infrastructure/consul.md',
    'pattern-library/coordination/request-waiting-list.md',
    'architects-handbook/case-studies/infrastructure/apache-storm.md',
    'pattern-library/scaling/blue-green-deployment.md',
    'pattern-library/data-management/gossip-protocol.md',
    'pattern-library/data-management/time-based-uuid.md',
    'architects-handbook/case-studies/infrastructure/docker.md',
    'architects-handbook/case-studies/messaging-streaming/apache-pulsar.md',
    'pattern-library/data-management/phi-accrual-failure-detector.md',
    'pattern-library/coordination/two-phase-commit.md',
    'pattern-library/scaling/geohashing.md',
    'pattern-library/scaling/throttling.md',
    'architects-handbook/case-studies/infrastructure/envoy-proxy.md',
    'pattern-library/data-management/idempotent-consumer.md',
    'architects-handbook/case-studies/infrastructure/vault.md',
    'architects-handbook/case-studies/infrastructure/apache-flink.md',
    'pattern-library/scaling/shared-database.md',
    'pattern-library/coordination/vector-clocks.md',
    'pattern-library/data-management/versioned-value.md',
    'pattern-library/data-management/replicated-log.md',
    'pattern-library/coordination/single-update-queue.md',
    'architects-handbook/case-studies/messaging-streaming/rabbitmq.md',
    'pattern-library/scaling/canary-deployment.md',
    'pattern-library/scaling/command-sourcing.md',
]

def remove_broken_items(nav_items):
    """Recursively remove broken items from navigation"""
    if isinstance(nav_items, list):
        cleaned = []
        for item in nav_items:
            cleaned_item = remove_broken_items(item)
            if cleaned_item is not None:
                cleaned.append(cleaned_item)
        return cleaned
    elif isinstance(nav_items, dict):
        cleaned = {}
        for key, value in nav_items.items():
            if isinstance(value, str) and value in BROKEN_LINKS:
                # Skip this item
                continue
            cleaned_value = remove_broken_items(value)
            if cleaned_value is not None:
                cleaned[key] = cleaned_value
        return cleaned if cleaned else None
    else:
        return nav_items

def main():
    # Load mkdocs.yml
    with open('mkdocs.yml', 'r') as f:
        config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
    
    # Clean navigation
    if 'nav' in config:
        config['nav'] = remove_broken_items(config['nav'])
    
    # Write back
    with open('mkdocs.yml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    
    print(f"Removed {len(BROKEN_LINKS)} broken links from navigation")

if __name__ == "__main__":
    main()
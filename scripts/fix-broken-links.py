#!/usr/bin/env python3
"""
Fix broken links in mkdocs.yml by mapping to actual file locations
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

# Define the mapping of broken links to their actual locations
LINK_MAPPINGS = {
    # Case Studies - System Design
    'architects-handbook/case-studies/news-feed.md': 'architects-handbook/case-studies/social-media/news-feed.md',
    'architects-handbook/case-studies/payment-system.md': 'architects-handbook/case-studies/payments-finance/payment-processing.md',
    'architects-handbook/case-studies/video-streaming.md': 'architects-handbook/case-studies/messaging-streaming/netflix-streaming.md',
    'architects-handbook/case-studies/uber-location.md': 'architects-handbook/case-studies/location-services/uber-location.md',
    'architects-handbook/case-studies/netflix-streaming.md': 'architects-handbook/case-studies/messaging-streaming/netflix-streaming.md',
    
    # Case Studies - Databases
    'architects-handbook/case-studies/cassandra.md': 'architects-handbook/case-studies/databases/cassandra.md',
    'architects-handbook/case-studies/redis-architecture.md': 'architects-handbook/case-studies/databases/redis-architecture.md',
    'architects-handbook/case-studies/mongodb.md': 'architects-handbook/case-studies/databases/mongodb.md',
    'architects-handbook/case-studies/etcd.md': 'architects-handbook/case-studies/databases/etcd.md',
    'architects-handbook/case-studies/amazon-dynamo.md': 'architects-handbook/case-studies/databases/amazon-dynamo.md',
    
    # Case Studies - Message Systems
    'architects-handbook/case-studies/kafka.md': 'architects-handbook/case-studies/messaging-streaming/kafka.md',
    'architects-handbook/case-studies/distributed-message-queue.md': 'architects-handbook/case-studies/messaging-streaming/distributed-message-queue.md',
    
    # Case Studies - Infrastructure
    'architects-handbook/case-studies/kubernetes.md': 'architects-handbook/case-studies/infrastructure/kubernetes.md',
    'architects-handbook/case-studies/prometheus.md': 'architects-handbook/case-studies/infrastructure/prometheus.md',
    
    # Pattern Library - Remove broken or misplaced patterns
    'pattern-library/architecture/thick-client.md': None,  # Remove - doesn't exist
    'pattern-library/architecture/stored-procedures.md': None,  # Remove - doesn't exist
    'pattern-library/architecture/singleton-database.md': None,  # Remove - doesn't exist
    'pattern-library/architecture/blue-green-deployment.md': None,  # Remove - doesn't exist
    'pattern-library/architecture/actor-model.md': None,  # Remove - doesn't exist
    'pattern-library/architecture/leader-follower.md': None,  # Remove - doesn't exist
    'pattern-library/architecture/emergent-leader.md': None,  # Remove - doesn't exist
    'pattern-library/architecture/data-mesh.md': None,  # Remove - doesn't exist
    'pattern-library/communication/distributed-queue.md': None,  # Remove - doesn't exist
    'pattern-library/communication/graphql-federation.md': 'pattern-library/architecture/graphql-federation.md',
    'pattern-library/communication/request-routing.md': None,  # Remove - doesn't exist
    'pattern-library/communication/event-streaming.md': 'pattern-library/architecture/event-streaming.md',
    'pattern-library/coordination/observability.md': None,  # Remove - doesn't exist
    'pattern-library/coordination/cap-theorem.md': 'pattern-library/architecture/cap-theorem.md',
    'pattern-library/coordination/valet-key.md': 'pattern-library/architecture/valet-key.md',
    'pattern-library/coordination/single-socket-channel.md': None,  # Remove - doesn't exist
    'pattern-library/coordination/adaptive-scheduling.md': None,  # Remove - doesn't exist
    'pattern-library/coordination/emergent-leader.md': None,  # Remove - doesn't exist
    'pattern-library/data-management/wal.md': 'pattern-library/data-management/write-ahead-log.md',
    'pattern-library/data-management/database-per-service.md': None,  # Remove - doesn't exist
    'pattern-library/data-management/idempotent-receiver.md': None,  # Remove - doesn't exist
    'pattern-library/data-management/time-series-ids.md': None,  # Remove - doesn't exist
    'pattern-library/data-management/leader-election.md': None,  # Remove - doesn't exist
    'pattern-library/data-management/distributed-lock.md': None,  # Remove - doesn't exist
    'pattern-library/data-management/low-high-water-marks.md': None,  # Remove - doesn't exist
    'pattern-library/scaling/geohashing.md': None,  # Remove - doesn't exist
    
    # Implementation Playbooks - Remove non-existent
    'architects-handbook/implementation-playbooks/getting-started.md': None,
    'architects-handbook/implementation-playbooks/pattern-discovery.md': None,
    'architects-handbook/implementation-playbooks/pattern-selection-wizard.md': None,
    'architects-handbook/implementation-playbooks/excellence-dashboard.md': None,
    'architects-handbook/implementation-playbooks/resilience-first.md': None,
    'architects-handbook/implementation-playbooks/data-consistency.md': None,
    'architects-handbook/implementation-playbooks/performance-optimization.md': None,
    'architects-handbook/implementation-playbooks/operational-excellence.md': None,
    'architects-handbook/implementation-playbooks/service-communication.md': None,
    'architects-handbook/implementation-playbooks/platform-engineering-playbook.md': None,
    'architects-handbook/implementation-playbooks/security-patterns.md': None,
    'architects-handbook/implementation-playbooks/migrations/index.md': None,
    'architects-handbook/implementation-playbooks/migrations/2pc-to-saga.md': None,
    'architects-handbook/implementation-playbooks/migrations/batch-to-streaming.md': None,
    'architects-handbook/implementation-playbooks/migrations/monolith-to-microservices.md': None,
    'architects-handbook/implementation-playbooks/migrations/polling-to-websocket.md': None,
    'architects-handbook/implementation-playbooks/migrations/migration-playbook-template.md': None,
    
    # Human Factors - Remove non-existent
    'architects-handbook/human-factors/sre-practices.md': None,
    'architects-handbook/human-factors/oncall-culture.md': None,
    'architects-handbook/human-factors/incident-response.md': None,
    'architects-handbook/human-factors/blameless-postmortems.md': None,
    
    # Learning Paths - Remove non-existent
    'architects-handbook/learning-paths/index.md': None,
    'architects-handbook/learning-paths/new-graduate.md': None,
    'architects-handbook/learning-paths/senior-engineer.md': None,
    'architects-handbook/learning-paths/architect.md': None,
    'architects-handbook/learning-paths/manager.md': None,
    'architects-handbook/learning-paths/performance.md': None,
    'architects-handbook/learning-paths/cost.md': None,
    'architects-handbook/learning-paths/reliability.md': None,
    'architects-handbook/learning-paths/consistency.md': None,
    
    # Interview Prep - Remove non-existent
    'interview-prep/frameworks/google-interviews/dashboard.md': None,
    'interview-prep/frameworks/approach-methodology.md': None,
    'interview-prep/frameworks/requirements-gathering.md': None,
    'interview-prep/frameworks/capacity-estimation.md': None,
    'interview-prep/frameworks/api-design.md': None,
    'interview-prep/frameworks/data-model-design.md': None,
    'interview-prep/frameworks/high-level-design.md': None,
    'interview-prep/frameworks/detailed-design.md': None,
    'interview-prep/frameworks/scale-discussion.md': None,
    'interview-prep/common-problems/news-feed.md': None,
    'interview-prep/common-problems/twitter-timeline.md': None,
    'interview-prep/common-problems/instagram-stories.md': None,
    'interview-prep/common-problems/chat-application.md': None,
    'interview-prep/common-problems/video-conferencing.md': None,
    'interview-prep/common-problems/notification-system.md': None,
    'interview-prep/common-problems/payment-system.md': None,
    'interview-prep/common-problems/shopping-cart.md': None,
    'interview-prep/common-problems/inventory-management.md': None,
    'interview-prep/common-problems/video-streaming.md': None,
    'interview-prep/common-problems/music-streaming.md': None,
    'interview-prep/common-problems/cdn-design.md': None,
    'interview-prep/common-problems/url-shortener.md': None,
    'interview-prep/common-problems/rate-limiter.md': None,
    'interview-prep/common-problems/distributed-cache.md': None,
    'interview-prep/common-problems/message-queue.md': None,
    'interview-prep/common-problems/task-scheduler.md': None,
    'interview-prep/common-problems/ride-sharing.md': None,
    'interview-prep/common-problems/maps-navigation.md': None,
    'interview-prep/common-problems/nearby-friends.md': None,
    'interview-prep/cheatsheets/pattern-quick-reference.md': None,
    'interview-prep/cheatsheets/scaling-numbers.md': None,
    'interview-prep/cheatsheets/database-comparison.md': None,
    'interview-prep/cheatsheets/message-queue-comparison.md': None,
    'interview-prep/cheatsheets/consistency-models.md': None,
    'interview-prep/cheatsheets/cap-tradeoffs.md': None,
    'interview-prep/cheatsheets/api-design.md': None,
    
    # Reference - Remove non-existent
    'reference/style-guide.md': None,
    'reference/pattern-template.md': None,
    'reference/case-study-template.md': None,
}

def fix_navigation_item(item):
    """Recursively fix navigation items"""
    if isinstance(item, str):
        # This is a direct link
        if item in LINK_MAPPINGS:
            return LINK_MAPPINGS[item]
        return item
    elif isinstance(item, dict):
        # This is a nested structure
        fixed_dict = {}
        for key, value in item.items():
            fixed_value = fix_navigation_item(value)
            if fixed_value is not None:
                fixed_dict[key] = fixed_value
        return fixed_dict if fixed_dict else None
    elif isinstance(item, list):
        # This is a list of items
        fixed_list = []
        for sub_item in item:
            fixed_item = fix_navigation_item(sub_item)
            if fixed_item is not None:
                fixed_list.append(fixed_item)
        return fixed_list if fixed_list else None
    return item

def main():
    # Load mkdocs.yml
    with open('mkdocs.yml', 'r') as f:
        config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
    
    # Fix navigation
    if 'nav' in config:
        config['nav'] = fix_navigation_item(config['nav'])
    
    # Write back the fixed config
    with open('mkdocs.yml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("Fixed mkdocs.yml navigation links")

if __name__ == "__main__":
    main()
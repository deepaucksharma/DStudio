#!/usr/bin/env python3
"""
Create missing files that are causing 404 errors in the deployed site
"""

import os
from pathlib import Path

# Base directory
base_dir = Path('/home/deepak/DStudio')
docs_dir = base_dir / 'docs'

# Missing files that need to be created with proper content
missing_files = {
    'docs/pattern-library/resilience/circuit-breaker.md': {
        'title': 'Circuit Breaker Pattern',
        'description': 'Prevent cascading failures by monitoring and breaking connections to failing services',
        'redirect': 'circuit-breaker-transformed'
    },
    'docs/pattern-library/data-management/saga.md': {
        'title': 'Saga Pattern',
        'description': 'Manage distributed transactions without two-phase commit',
        'content': 'Saga pattern for managing distributed transactions'
    },
    'docs/pattern-library/data-management/event-sourcing.md': {
        'title': 'Event Sourcing Pattern',
        'description': 'Store system state as a sequence of events',
        'content': 'Event sourcing pattern for audit and replay'
    },
    'docs/pattern-library/data-management/cqrs.md': {
        'title': 'CQRS Pattern',
        'description': 'Command Query Responsibility Segregation for scalable systems',
        'content': 'CQRS pattern separates read and write models'
    },
    'docs/pattern-library/coordination/consensus.md': {
        'title': 'Consensus Patterns',
        'description': 'Achieve agreement in distributed systems',
        'content': 'Consensus algorithms like Raft and Paxos'
    },
    'docs/zoom-scaling.md': {
        'title': 'Zoom Scaling Architecture',
        'description': 'How Zoom scaled to handle millions of concurrent users',
        'redirect': 'architects-handbook/case-studies/infrastructure/zoom-scaling'
    },
    'docs/redis-architecture.md': {
        'title': 'Redis Architecture',
        'description': 'In-memory data structure store architecture',
        'redirect': 'architects-handbook/case-studies/databases/redis-architecture'
    },
    'docs/coordination-costs.md': {
        'title': 'Coordination Costs in Distributed Systems',
        'description': 'Understanding the costs of coordination in distributed systems',
        'content': 'Analysis of coordination overhead and strategies to minimize it'
    },
    'docs/progress.md': {
        'title': 'Learning Progress Tracker',
        'description': 'Track your progress through the learning paths',
        'content': 'Progress tracking for distributed systems learning'
    },
    'docs/quantitative-analysis/queueing-models.md': {
        'title': 'Queueing Models',
        'description': 'Mathematical models for analyzing queues in systems',
        'redirect': 'architects-handbook/quantitative-analysis/queueing-models'
    }
}

def create_file_with_content(file_path: str, metadata: dict):
    """Create a markdown file with proper frontmatter and content"""
    full_path = base_dir / file_path
    
    # Create directory if it doesn't exist
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build content
    content_lines = [
        '---',
        f"title: {metadata['title']}",
        f"description: {metadata['description']}"
    ]
    
    if 'redirect' in metadata:
        content_lines.append(f"redirect_to: /{metadata['redirect']}/")
    
    content_lines.extend([
        '---',
        '',
        f"# {metadata['title']}",
        ''
    ])
    
    if 'redirect' in metadata:
        content_lines.extend([
            '!!! info "This page has moved"',
            f'    This content has been moved to [{metadata["redirect"]}](/{metadata["redirect"]}/)',
            '',
            f'    You will be redirected automatically, or [click here](/{metadata["redirect"]}/) to go there now.'
        ])
    elif 'content' in metadata:
        content_lines.append(metadata['content'])
    else:
        content_lines.extend([
            f"## Overview",
            '',
            metadata['description'],
            '',
            '## Content',
            '',
            'This section is under development.'
        ])
    
    # Write file
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content_lines))
    
    return full_path

# Create missing implementation playbook index files
playbook_dirs = [
    'docs/architects-handbook/implementation-playbooks/monolith-decomposition',
    'docs/architects-handbook/implementation-playbooks/zero-downtime',
    'docs/architects-handbook/implementation-playbooks/global-expansion',
    'docs/architects-handbook/implementation-playbooks/pattern-selection-wizard',
    'docs/architects-handbook/implementation-playbooks/migration-checklist',
    'docs/architects-handbook/implementation-playbooks/monolith-to-microservices'
]

for playbook_dir in playbook_dirs:
    index_path = base_dir / playbook_dir / 'index.md'
    if not index_path.exists():
        index_path.parent.mkdir(parents=True, exist_ok=True)
        playbook_name = playbook_dir.split('/')[-1].replace('-', ' ').title()
        content = f"""---
title: {playbook_name} Playbook
description: Implementation guide for {playbook_name.lower()}
---

# {playbook_name} Playbook

## Overview

Comprehensive guide for implementing {playbook_name.lower()} in distributed systems.

## Steps

1. Assessment
2. Planning
3. Implementation
4. Validation
5. Optimization

## Resources

- Patterns
- Tools
- Case Studies
"""
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {index_path.relative_to(base_dir)}")

def main():
    print("Creating missing files...\n")
    
    # Create missing pattern and reference files
    for file_path, metadata in missing_files.items():
        full_path = create_file_with_content(file_path, metadata)
        print(f"Created: {full_path.relative_to(base_dir)}")
    
    print(f"\nCreated {len(missing_files)} missing files")
    print(f"Created {len(playbook_dirs)} playbook index files")

if __name__ == '__main__':
    main()

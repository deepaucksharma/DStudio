#!/usr/bin/env python3
"""
Fix navigation 404 errors by creating missing files and updating mkdocs.yml.
"""

import os
import yaml
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Critical missing files that need to be created
CRITICAL_MISSING_FILES = [
    "docs/zoom-scaling.md",
    "docs/redis-architecture.md",
    "docs/coordination-costs.md",
    "docs/progress.md",
]

# Missing implementation playbooks
IMPLEMENTATION_PLAYBOOKS = [
    "docs/architects-handbook/implementation-playbooks/monolith-decomposition/index.md",
    "docs/architects-handbook/implementation-playbooks/zero-downtime/index.md",
    "docs/architects-handbook/implementation-playbooks/global-expansion/index.md",
    "docs/architects-handbook/implementation-playbooks/pattern-selection-wizard/index.md",
    "docs/architects-handbook/implementation-playbooks/migration-checklist/index.md",
    "docs/architects-handbook/implementation-playbooks/monolith-to-microservices/index.md",
]

def create_missing_file(file_path: str, title: str, description: str):
    """Create a missing markdown file with basic content."""
    path = Path(file_path)
    
    # Create directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Skip if file already exists
    if path.exists():
        logger.info(f"File already exists: {file_path}")
        return False
    
    # Create content based on file type
    content = f"""---
title: {title}
description: {description}
status: draft
last_updated: 2025-08-06
---

# {title}

!!! warning "Content Under Development"
    This page is currently being developed. Check back soon for updates.

## Overview

{description}

## Key Concepts

Coming soon...

## Implementation Guide

Coming soon...

## Best Practices

Coming soon...

## Related Patterns

Coming soon...
"""
    
    # Write the file
    path.write_text(content, encoding='utf-8')
    logger.info(f"Created: {file_path}")
    return True

def create_critical_files():
    """Create critical missing files."""
    files_created = 0
    
    # Create coordination-costs.md (already exists based on earlier output)
    # Create other critical files
    
    file_configs = {
        "docs/zoom-scaling.md": {
            "title": "Zoom-Level Scaling Architecture",
            "description": "Learn how to scale applications like Zoom with millions of concurrent users"
        },
        "docs/redis-architecture.md": {
            "title": "Redis Architecture Deep Dive", 
            "description": "Understanding Redis internals, clustering, and scaling patterns"
        },
        "docs/progress.md": {
            "title": "Learning Progress Tracker",
            "description": "Track your progress through the Distributed Systems Studio learning paths"
        },
    }
    
    for file_path, config in file_configs.items():
        if create_missing_file(file_path, config["title"], config["description"]):
            files_created += 1
    
    return files_created

def create_implementation_playbooks():
    """Create missing implementation playbook directories and index files."""
    files_created = 0
    
    playbook_configs = {
        "docs/architects-handbook/implementation-playbooks/monolith-decomposition/index.md": {
            "title": "Monolith Decomposition Playbook",
            "description": "Step-by-step guide to decomposing monolithic applications into microservices"
        },
        "docs/architects-handbook/implementation-playbooks/zero-downtime/index.md": {
            "title": "Zero Downtime Deployment Playbook",
            "description": "Strategies and patterns for achieving zero downtime deployments"
        },
        "docs/architects-handbook/implementation-playbooks/global-expansion/index.md": {
            "title": "Global Expansion Playbook",
            "description": "Guide to expanding your application globally with multi-region architectures"
        },
        "docs/architects-handbook/implementation-playbooks/pattern-selection-wizard/index.md": {
            "title": "Pattern Selection Wizard",
            "description": "Interactive guide to selecting the right distributed system patterns"
        },
        "docs/architects-handbook/implementation-playbooks/migration-checklist/index.md": {
            "title": "Migration Checklist",
            "description": "Comprehensive checklist for system migrations and modernization"
        },
        "docs/architects-handbook/implementation-playbooks/monolith-to-microservices/index.md": {
            "title": "Monolith to Microservices Migration",
            "description": "Complete guide for migrating from monolithic to microservices architecture"
        },
    }
    
    for file_path, config in playbook_configs.items():
        if create_missing_file(file_path, config["title"], config["description"]):
            files_created += 1
    
    return files_created

def fix_mkdocs_navigation():
    """Update mkdocs.yml to fix navigation issues."""
    mkdocs_path = Path("mkdocs.yml")
    
    if not mkdocs_path.exists():
        logger.error("mkdocs.yml not found")
        return
    
    try:
        with open(mkdocs_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check and log navigation structure
        if 'nav' in config:
            logger.info("Checking navigation structure...")
            check_navigation_files(config['nav'], 'docs')
        
        # Note: We don't modify mkdocs.yml directly as the structure seems correct
        # The issue is with missing files, which we're creating
        
    except Exception as e:
        logger.error(f"Error processing mkdocs.yml: {e}")

def check_navigation_files(nav_items, base_dir='docs'):
    """Recursively check if navigation files exist."""
    if isinstance(nav_items, list):
        for item in nav_items:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str):
                        # It's a file reference
                        file_path = Path(base_dir) / value
                        if not file_path.exists():
                            logger.warning(f"Navigation file missing: {file_path}")
                    elif isinstance(value, list):
                        # It's a nested navigation
                        check_navigation_files(value, base_dir)

def main():
    """Main entry point."""
    logger.info("Starting navigation fix process...")
    
    # Create critical missing files
    critical_created = create_critical_files()
    logger.info(f"Created {critical_created} critical files")
    
    # Create implementation playbooks
    playbooks_created = create_implementation_playbooks()
    logger.info(f"Created {playbooks_created} implementation playbook files")
    
    # Check mkdocs navigation
    fix_mkdocs_navigation()
    
    total_created = critical_created + playbooks_created
    logger.info(f"\nSummary: Created {total_created} missing files")
    
    if total_created > 0:
        logger.info("Run 'mkdocs serve' to test the changes locally")
        logger.info("Then commit and push to see changes on the live site")

if __name__ == "__main__":
    main()
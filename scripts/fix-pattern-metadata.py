#!/usr/bin/env python3
"""
Fix missing metadata in pattern files
"""

import os
import yaml
from pathlib import Path
import re

PATTERNS_DIR = Path("docs/patterns")
REQUIRED_FIELDS = {
    'title': 'Pattern Name',
    'category': 'uncategorized', 
    'excellence_tier': 'bronze',
    'pattern_status': 'stable'
}

def extract_title_from_content(content):
    """Extract title from first # heading if no title in frontmatter"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Untitled Pattern"

def determine_category(file_path, content):
    """Determine category based on file name or content"""
    filename = file_path.stem.lower()
    
    # Category mapping based on filename patterns
    category_map = {
        'resilience': ['circuit-breaker', 'bulkhead', 'retry', 'timeout', 'failover', 'graceful'],
        'data': ['cache', 'shard', 'partition', 'replication', 'consistency', 'saga', 'outbox', 'event-sourcing', 'cqrs'],
        'integration': ['api-gateway', 'service-mesh', 'message', 'queue', 'broker', 'adapter', 'ambassador'],
        'architecture': ['microservices', 'serverless', 'cell-based', 'layered', 'hexagonal', 'domain'],
        'deployment': ['blue-green', 'canary', 'rolling', 'feature-toggle', 'dark-launch'],
        'observability': ['logging', 'monitoring', 'tracing', 'metrics', 'health-check'],
        'security': ['authentication', 'authorization', 'encryption', 'vault', 'key-management']
    }
    
    for category, patterns in category_map.items():
        for pattern in patterns:
            if pattern in filename:
                return category
    
    # Check content for category hints
    content_lower = content.lower()
    if 'resilience' in content_lower or 'failure' in content_lower:
        return 'resilience'
    elif 'data' in content_lower or 'database' in content_lower:
        return 'data'
    elif 'api' in content_lower or 'integration' in content_lower:
        return 'integration'
    
    return 'uncategorized'

def determine_tier(file_path, content):
    """Determine excellence tier based on pattern maturity indicators"""
    filename = file_path.stem.lower()
    content_lower = content.lower()
    
    # Gold tier patterns (industry standard, 10+ years)
    gold_patterns = ['load-balancing', 'caching', 'sharding', 'replication', 'api-gateway']
    if any(pattern in filename for pattern in gold_patterns):
        return 'gold'
    
    # Check for maturity indicators in content
    if 'widely adopted' in content_lower or 'industry standard' in content_lower:
        return 'gold'
    elif 'emerging' in content_lower or 'experimental' in content_lower:
        return 'bronze'
    
    # Default to silver for established patterns
    return 'silver'

def fix_metadata(file_path):
    """Fix missing metadata in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return
    
    # Extract existing frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                frontmatter = {}
            body = parts[2]
        else:
            frontmatter = {}
            body = content
    else:
        frontmatter = {}
        body = content
    
    # Add missing fields
    updated = False
    
    # Handle title specially
    if 'title' not in frontmatter:
        frontmatter['title'] = extract_title_from_content(body)
        updated = True
    
    # Handle category specially
    if 'category' not in frontmatter:
        frontmatter['category'] = determine_category(file_path, body)
        updated = True
    
    # Handle excellence_tier specially
    if 'excellence_tier' not in frontmatter:
        frontmatter['excellence_tier'] = determine_tier(file_path, body)
        updated = True
    
    # Add other required fields with defaults
    for field, default in REQUIRED_FIELDS.items():
        if field not in frontmatter and field not in ['title', 'category', 'excellence_tier']:
            frontmatter[field] = default
            updated = True
    
    if updated:
        # Write back
        new_content = f"---\n{yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)}---\n{body}"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✓ Fixed: {file_path.name}")
        except Exception as e:
            print(f"✗ Error writing {file_path}: {e}")
    else:
        print(f"✓ Already complete: {file_path.name}")

def main():
    """Main function to fix all pattern files"""
    print("Fixing pattern metadata...")
    print(f"Scanning directory: {PATTERNS_DIR}")
    
    if not PATTERNS_DIR.exists():
        print(f"Error: Directory not found: {PATTERNS_DIR}")
        return
    
    pattern_files = list(PATTERNS_DIR.glob("*.md"))
    exclude_files = ['README.md', 'PATTERN_TEMPLATE.md', 'index.md', 'pattern-catalog.md']
    
    fixed_count = 0
    for pattern_file in pattern_files:
        if pattern_file.name not in exclude_files:
            fix_metadata(pattern_file)
            fixed_count += 1
    
    print(f"\nProcessed {fixed_count} pattern files")

if __name__ == "__main__":
    main()
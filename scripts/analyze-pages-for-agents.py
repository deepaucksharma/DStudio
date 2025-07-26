#!/usr/bin/env python3
"""
Analyze pages to determine which ones need agents and what fixes are needed
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

def analyze_broken_links():
    """Run verify-links.py and parse output"""
    import subprocess
    
    result = subprocess.run(
        ['python3', 'scripts/verify-links.py'],
        capture_output=True,
        text=True
    )
    
    # Parse output
    pages_with_issues = defaultdict(list)
    current_file = None
    
    for line in result.stderr.split('\n'):
        if line.endswith('.md:'):
            current_file = line[:-1]
        elif current_file and 'Line' in line and '->' in line:
            # Extract link info
            match = re.search(r'Line (\d+): \[(.*?)\]\((.*?)\)', line)
            if match:
                line_num, link_text, link_url = match.groups()
                pages_with_issues[current_file].append({
                    'line': int(line_num),
                    'text': link_text,
                    'url': link_url,
                    'type': categorize_link_issue(link_url, current_file)
                })
    
    return pages_with_issues

def categorize_link_issue(link_url, source_file):
    """Categorize the type of link issue"""
    if link_url.startswith('http'):
        return 'external'
    elif link_url.startswith('#'):
        return 'anchor'
    elif link_url.startswith('mailto:'):
        return 'email'
    elif link_url.endswith('.md/index'):
        return 'directory-index'
    elif link_url.startswith('../') and link_url.count('../') > 3:
        return 'excessive-parent'
    elif '//' in link_url:
        return 'double-slash'
    elif link_url.endswith('.md.md'):
        return 'double-extension'
    else:
        return 'missing-file'

def group_pages_by_priority(pages_with_issues):
    """Group pages by priority for agent assignment"""
    groups = {
        'critical': [],     # Core documentation pages
        'high': [],         # Case studies and patterns
        'medium': [],       # Examples and learning paths
        'low': []          # Templates and misc
    }
    
    for page, issues in pages_with_issues.items():
        issue_count = len(issues)
        
        # Categorize by path and issue count
        if 'index.md' in page and issue_count > 10:
            groups['critical'].append((page, issue_count, issues))
        elif 'case-studies' in page or 'patterns' in page:
            groups['high'].append((page, issue_count, issues))
        elif 'google-interviews' in page or 'learning-paths' in page:
            groups['high'].append((page, issue_count, issues))
        elif 'examples' in page or 'templates' in page:
            groups['medium'].append((page, issue_count, issues))
        else:
            groups['low'].append((page, issue_count, issues))
    
    # Sort each group by issue count
    for priority in groups:
        groups[priority].sort(key=lambda x: x[1], reverse=True)
    
    return groups

def create_agent_batch_config(groups, max_agents=10):
    """Create configuration for agent batches"""
    batches = []
    current_batch = []
    
    # Process in priority order
    for priority in ['critical', 'high', 'medium', 'low']:
        for page_info in groups[priority]:
            page, count, issues = page_info
            
            # Skip pages with very few issues
            if count < 3:
                continue
                
            agent_config = {
                'page': page,
                'issue_count': count,
                'priority': priority,
                'fix_types': list(set(issue['type'] for issue in issues)),
                'sample_issues': issues[:5]  # First 5 issues as examples
            }
            
            current_batch.append(agent_config)
            
            if len(current_batch) >= max_agents:
                batches.append(current_batch)
                current_batch = []
    
    if current_batch:
        batches.append(current_batch)
    
    return batches

def main():
    print("Analyzing pages for parallel agent deployment...")
    
    # Analyze broken links
    pages_with_issues = analyze_broken_links()
    
    print(f"\nTotal pages with issues: {len(pages_with_issues)}")
    
    # Group by priority
    groups = group_pages_by_priority(pages_with_issues)
    
    print("\nPages by priority:")
    for priority, pages in groups.items():
        print(f"  {priority}: {len(pages)} pages")
        if pages:
            print(f"    Top 3: {[p[0].split('/')[-1] for p in pages[:3]]}")
    
    # Create agent batches
    batches = create_agent_batch_config(groups)
    
    print(f"\nAgent deployment plan: {len(batches)} batches")
    for i, batch in enumerate(batches[:3]):  # Show first 3 batches
        print(f"\nBatch {i+1} ({len(batch)} agents):")
        for agent in batch[:5]:  # Show first 5 agents
            print(f"  - {agent['page'].split('/')[-2:]}: {agent['issue_count']} issues")
            print(f"    Types: {', '.join(agent['fix_types'])}")
    
    # Save configuration
    with open('agent_batches.json', 'w') as f:
        json.dump(batches, f, indent=2)
    
    print(f"\nAgent configuration saved to agent_batches.json")
    print(f"Ready to deploy {sum(len(b) for b in batches)} agents in {len(batches)} batches")

if __name__ == "__main__":
    main()
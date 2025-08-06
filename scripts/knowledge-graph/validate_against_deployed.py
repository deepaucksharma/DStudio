#!/usr/bin/env python3
"""
Validate knowledge graph against deployed website URLs
"""

import sqlite3
from pathlib import Path
from urllib.parse import urlparse
import re

def extract_deployed_urls(url_text):
    """Extract URLs from the provided text"""
    urls = []
    # Extract all URLs that match the pattern
    pattern = r'https://deepaucksharma\.github\.io/DStudio/([^\s]*?)/?'
    matches = re.findall(pattern, url_text)
    
    # Clean and normalize paths
    for match in matches:
        # Remove trailing slash if present
        path = match.rstrip('/')
        if path:  # Skip empty paths (root)
            urls.append(path)
    
    return sorted(set(urls))

def validate_knowledge_graph(db_path="knowledge_graph_ultimate.db"):
    """Validate our knowledge graph against deployed URLs"""
    
    # The deployed URLs from the website
    deployed_urls_text = """
https://deepaucksharma.github.io/DStudio/
https://deepaucksharma.github.io/DStudio/CALCULATOR_VALIDATION_TESTING_PLAN/
https://deepaucksharma.github.io/DStudio/COMPREHENSIVE_FIX_IMPLEMENTATION_PLAN/
https://deepaucksharma.github.io/DStudio/architects-handbook/
https://deepaucksharma.github.io/DStudio/company-specific/
https://deepaucksharma.github.io/DStudio/core-principles/
https://deepaucksharma.github.io/DStudio/human-factors/
https://deepaucksharma.github.io/DStudio/implementation-playbooks/
https://deepaucksharma.github.io/DStudio/incident-response/
https://deepaucksharma.github.io/DStudio/interview-prep/
https://deepaucksharma.github.io/DStudio/latency-calculator/
https://deepaucksharma.github.io/DStudio/migrations/
https://deepaucksharma.github.io/DStudio/monolith-to-microservices/
https://deepaucksharma.github.io/DStudio/pattern-library/
https://deepaucksharma.github.io/DStudio/patterns/
https://deepaucksharma.github.io/DStudio/performance-testing/
https://deepaucksharma.github.io/DStudio/progress/
https://deepaucksharma.github.io/DStudio/quantitative-analysis/
https://deepaucksharma.github.io/DStudio/reference/
https://deepaucksharma.github.io/DStudio/start-here/
https://deepaucksharma.github.io/DStudio/analysis/cap-theorem/
https://deepaucksharma.github.io/DStudio/analysis/littles-law/
https://deepaucksharma.github.io/DStudio/analysis/queueing-models/
https://deepaucksharma.github.io/DStudio/architects-handbook/QUALITY_ASSURANCE_STRATEGY/
https://deepaucksharma.github.io/DStudio/architects-handbook/QUALITY_IMPLEMENTATION_GUIDE/
https://deepaucksharma.github.io/DStudio/architects-handbook/amazon-dynamo/
https://deepaucksharma.github.io/DStudio/architects-handbook/apache-spark/
https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/
https://deepaucksharma.github.io/DStudio/architects-handbook/chat-system/
https://deepaucksharma.github.io/DStudio/architects-handbook/consistent-hashing/
https://deepaucksharma.github.io/DStudio/architects-handbook/google-spanner/
https://deepaucksharma.github.io/DStudio/architects-handbook/human-factors/
https://deepaucksharma.github.io/DStudio/architects-handbook/implementation-playbooks/
https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/
https://deepaucksharma.github.io/DStudio/architects-handbook/netflix-chaos/
https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/
https://deepaucksharma.github.io/DStudio/architects-handbook/tools/
https://deepaucksharma.github.io/DStudio/tools/availability-calculator/
https://deepaucksharma.github.io/DStudio/tools/capacity-calculator/
https://deepaucksharma.github.io/DStudio/tools/latency-calculator/
https://deepaucksharma.github.io/DStudio/tools/throughput-calculator/
https://deepaucksharma.github.io/DStudio/patterns/resilience/
https://deepaucksharma.github.io/DStudio/patterns/scaling/
https://deepaucksharma.github.io/DStudio/patterns/security/
https://deepaucksharma.github.io/DStudio/pattern-library/resilience/circuit-breaker/
https://deepaucksharma.github.io/DStudio/pattern-library/data-management/saga/
https://deepaucksharma.github.io/DStudio/core-principles/laws/asynchronous-reality/
https://deepaucksharma.github.io/DStudio/core-principles/laws/correlated-failure/
    """
    
    # Extract deployed paths
    deployed_paths = extract_deployed_urls(deployed_urls_text)
    
    print("=" * 60)
    print("KNOWLEDGE GRAPH VALIDATION")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all pages from our knowledge graph
    cursor.execute("SELECT page_id FROM pages")
    kb_pages = set(row['page_id'] for row in cursor.fetchall())
    
    # Normalize deployed paths to match our page_id format
    # Deployed URLs end with / which we need to convert to /index
    deployed_page_ids = set()
    for path in deployed_paths:
        # Remove trailing slash and add to set
        clean_path = path.rstrip('/')
        deployed_page_ids.add(clean_path)
    
    print(f"\nDeployed pages (from sitemap): {len(deployed_page_ids)}")
    print(f"Knowledge graph pages: {len(kb_pages)}")
    
    # Find pages that are deployed but not in our KB
    deployed_not_in_kb = deployed_page_ids - kb_pages
    if deployed_not_in_kb:
        print(f"\n⚠️  Pages deployed but NOT in knowledge graph ({len(deployed_not_in_kb)}):")
        for page in sorted(deployed_not_in_kb)[:20]:
            print(f"   - {page}")
            # Check if it's a redirect or duplicate
            if 'patterns/' in page:
                pattern_lib_equivalent = page.replace('patterns/', 'pattern-library/')
                if pattern_lib_equivalent in kb_pages:
                    print(f"     → Likely duplicate of {pattern_lib_equivalent}")
    
    # Find pages in KB but not deployed
    kb_not_deployed = kb_pages - deployed_page_ids
    if kb_not_deployed:
        print(f"\n⚠️  Pages in KB but NOT deployed ({len(kb_not_deployed)}):")
        for page in sorted(kb_not_deployed)[:20]:
            print(f"   - {page}")
    
    # Analyze the URL structure difference
    print("\n" + "=" * 60)
    print("URL STRUCTURE ANALYSIS")
    print("=" * 60)
    
    # Check patterns vs pattern-library duplication
    patterns_pages = [p for p in deployed_page_ids if p.startswith('patterns/')]
    pattern_lib_pages = [p for p in kb_pages if p.startswith('pattern-library/')]
    
    print(f"\nDuplicate structure detected:")
    print(f"  - 'patterns/' paths in deployment: {len(patterns_pages)}")
    print(f"  - 'pattern-library/' paths in KB: {len(pattern_lib_pages)}")
    
    # Check for index pages
    print("\n" + "=" * 60)
    print("INDEX PAGE HANDLING")
    print("=" * 60)
    
    # URLs ending with / should map to page_id/index
    cursor.execute("""
        SELECT page_id FROM pages 
        WHERE page_id LIKE '%/index' OR page_id = 'index'
    """)
    index_pages = [row['page_id'] for row in cursor.fetchall()]
    
    print(f"\nIndex pages in KB: {len(index_pages)}")
    for page in index_pages[:10]:
        print(f"  - {page}")
    
    # Validate broken links
    print("\n" + "=" * 60)
    print("BROKEN LINK VALIDATION")
    print("=" * 60)
    
    # Check how many "broken" links are actually valid deployed URLs
    cursor.execute("""
        SELECT DISTINCT dst_page, COUNT(*) as count
        FROM links
        WHERE is_valid = 0 AND is_external = 0
        GROUP BY dst_page
        ORDER BY count DESC
        LIMIT 20
    """)
    
    false_broken = []
    for row in cursor.fetchall():
        dst_page = row['dst_page']
        if dst_page:
            # Check various forms
            checks = [
                dst_page in deployed_page_ids,
                dst_page.rstrip('/index') in deployed_page_ids,
                f"{dst_page}/index" in deployed_page_ids,
            ]
            
            if any(checks):
                false_broken.append((dst_page, row['count']))
    
    if false_broken:
        print("\nLinks marked as broken but page exists on deployed site:")
        for page, count in false_broken[:10]:
            print(f"  {count:3} links to {page}")
    
    # URL pattern analysis
    print("\n" + "=" * 60)
    print("URL PATTERN INSIGHTS")
    print("=" * 60)
    
    # MkDocs seems to be creating both /page and /page/ URLs
    # And our links ending with / need to resolve to /index in our page_ids
    
    print("\nKey findings:")
    print("1. MkDocs generates URLs with trailing slashes for directories")
    print("2. The 'patterns/' directory is a duplicate/redirect of 'pattern-library/'")
    print("3. Links ending with '/' should map to page_id + '/index'")
    print("4. Some pages exist in multiple locations (redirects/aliases)")
    
    conn.close()
    
    return {
        'deployed': len(deployed_page_ids),
        'kb': len(kb_pages),
        'missing_from_kb': len(deployed_not_in_kb),
        'missing_from_deployment': len(kb_not_deployed),
        'false_broken': len(false_broken)
    }

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    
    # Read the full URL list from the user's input
    stats = validate_knowledge_graph()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Deployed pages: {stats['deployed']}")
    print(f"Knowledge graph pages: {stats['kb']}")
    print(f"Missing from KB: {stats['missing_from_kb']}")
    print(f"Not deployed: {stats['missing_from_deployment']}")
    print(f"False broken links: {stats['false_broken']}")
#!/usr/bin/env python3
"""
Query the knowledge graph database for insights
"""

import sqlite3
import json

def query_graph(db_path="knowledge_graph_ultimate.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 60)
    print("KNOWLEDGE GRAPH STATISTICS")
    print("=" * 60)
    
    # Basic stats
    cursor.execute("SELECT COUNT(*) as count FROM pages")
    pages = cursor.fetchone()['count']
    print(f"Total pages: {pages}")
    
    cursor.execute("SELECT COUNT(*) as count FROM links")
    links = cursor.fetchone()['count']
    print(f"Total links: {links}")
    
    cursor.execute("SELECT COUNT(*) as count FROM links WHERE is_valid = 0")
    broken = cursor.fetchone()['count']
    print(f"Broken links: {broken}")
    
    cursor.execute("SELECT COUNT(*) as count FROM concepts")
    concepts = cursor.fetchone()['count']
    print(f"Unique concepts: {concepts}")
    
    cursor.execute("SELECT AVG(quality_score) as avg FROM pages")
    avg_quality = cursor.fetchone()['avg']
    print(f"Average quality score: {avg_quality:.1f}/100")
    
    print("\n" + "=" * 60)
    print("TOP ISSUES BY CATEGORY")
    print("=" * 60)
    
    cursor.execute("""
        SELECT category, COUNT(DISTINCT i.page_id) as pages_with_issues,
               COUNT(i.issue_id) as total_issues
        FROM pages p
        JOIN issues i ON i.page_id = p.page_id
        GROUP BY category
        ORDER BY total_issues DESC
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        print(f"{row['category']:30} {row['pages_with_issues']:4} pages, {row['total_issues']:5} issues")
    
    print("\n" + "=" * 60)
    print("PAGES WITH MOST BROKEN LINKS")
    print("=" * 60)
    
    cursor.execute("""
        SELECT p.page_id, p.title, COUNT(*) as broken_count
        FROM pages p
        JOIN links l ON l.src_page = p.page_id
        WHERE l.is_valid = 0
        GROUP BY p.page_id
        ORDER BY broken_count DESC
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        print(f"{row['broken_count']:3} broken links: {row['title'][:50]:<50} ({row['page_id']})")
    
    print("\n" + "=" * 60)
    print("ORPHANED PAGES (not linked from anywhere)")
    print("=" * 60)
    
    cursor.execute("""
        SELECT p.page_id, p.title
        FROM pages p
        WHERE NOT EXISTS (
            SELECT 1 FROM links WHERE dst_page = p.page_id
        )
        AND p.page_id != 'index'
        ORDER BY p.page_id
        LIMIT 20
    """)
    
    orphans = cursor.fetchall()
    for row in orphans:
        print(f"  - {row['page_id']}")
    print(f"\nTotal orphaned pages: {len(orphans)}+")
    
    print("\n" + "=" * 60)
    print("MOST LINKED PAGES")
    print("=" * 60)
    
    cursor.execute("""
        SELECT dst_page, COUNT(*) as incoming_links
        FROM links
        WHERE dst_page IS NOT NULL
        GROUP BY dst_page
        ORDER BY incoming_links DESC
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        cursor.execute("SELECT title FROM pages WHERE page_id = ?", (row['dst_page'],))
        title_row = cursor.fetchone()
        title = title_row['title'] if title_row else row['dst_page']
        print(f"{row['incoming_links']:3} links: {title[:50]:<50} ({row['dst_page']})")
    
    print("\n" + "=" * 60)
    print("PATTERN LIBRARY ANALYSIS")
    print("=" * 60)
    
    cursor.execute("""
        SELECT tier, COUNT(*) as count
        FROM pages
        WHERE tier IS NOT NULL
        GROUP BY tier
        ORDER BY 
            CASE tier
                WHEN 'gold' THEN 1
                WHEN 'silver' THEN 2
                WHEN 'bronze' THEN 3
            END
    """)
    
    for row in cursor.fetchall():
        print(f"{row['tier'].capitalize():10} {row['count']} patterns")
    
    print("\n" + "=" * 60)
    print("ACTIONABLE INSIGHTS")
    print("=" * 60)
    
    # Find most common broken link patterns
    cursor.execute("""
        SELECT dst_url, COUNT(*) as count
        FROM links
        WHERE is_valid = 0 AND is_external = 0
        GROUP BY dst_url
        ORDER BY count DESC
        LIMIT 5
    """)
    
    print("\nMost common broken internal links:")
    for row in cursor.fetchall():
        print(f"  {row['count']:3}x {row['dst_url']}")
    
    # Check navigation coverage
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM pages) as total,
            (SELECT COUNT(DISTINCT child) FROM nav_edges) as in_nav
    """)
    
    nav = cursor.fetchone()
    if nav['total'] > 0:
        coverage = (nav['in_nav'] / nav['total']) * 100
        print(f"\nNavigation coverage: {nav['in_nav']}/{nav['total']} pages ({coverage:.1f}%)")
    
    conn.close()

if __name__ == "__main__":
    query_graph()
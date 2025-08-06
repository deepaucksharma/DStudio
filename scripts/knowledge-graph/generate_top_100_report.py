#!/usr/bin/env python3
"""
Generate comprehensive report with top 100 pages from knowledge graph
"""

import sqlite3
import json

def generate_report():
    conn = sqlite3.connect('knowledge_graph_ultimate.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get updated statistics after fixes
    cursor.execute('SELECT COUNT(*) FROM pages')
    total_pages = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM links WHERE is_valid = 0 AND is_external = 0')
    broken_internal = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM links WHERE is_external = 0')
    total_internal = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM links WHERE is_external = 1')
    total_external = cursor.fetchone()[0]

    print('=' * 60)
    print('UPDATED KNOWLEDGE GRAPH STATISTICS')
    print('=' * 60)
    print(f'Total pages analyzed: {total_pages}')
    print(f'Total internal links: {total_internal}')
    print(f'Total external links: {total_external}')
    print(f'Broken internal links: {broken_internal}')
    print(f'Broken link rate: {(broken_internal/total_internal)*100:.1f}%')

    # Get top 100 pages by importance (PageRank + quality score)
    query = '''
    WITH page_metrics AS (
        SELECT 
            p.page_id,
            p.title,
            p.quality_score,
            p.pagerank,
            COUNT(*) as total_links,
            SUM(CASE WHEN l.is_valid = 0 AND l.is_external = 0 THEN 1 ELSE 0 END) as broken_links,
            (p.quality_score * 0.6 + p.pagerank * 10000 * 0.4) as importance_score
        FROM pages p
        LEFT JOIN links l ON p.page_id = l.src_page
        GROUP BY p.page_id, p.title, p.quality_score, p.pagerank
    )
    SELECT 
        page_id,
        title,
        ROUND(quality_score, 1) as quality,
        ROUND(pagerank * 10000, 2) as pagerank_scaled,
        ROUND(importance_score, 2) as importance,
        total_links,
        broken_links
    FROM page_metrics
    ORDER BY importance_score DESC
    LIMIT 100
    '''

    cursor.execute(query)
    top_pages = cursor.fetchall()

    print('\n' + '=' * 60)
    print('TOP 100 PAGES BY IMPORTANCE (Quality Score + PageRank)')
    print('=' * 60)
    
    # Print header
    header = f"{'Rank':>4} | {'Page ID':<70} | {'Quality':>7} | {'PageRank':>8} | {'Importance':>10} | {'Links':>5} | {'Broken':>6}"
    print(header)
    print('-' * len(header))

    # Generate working URLs for top pages
    base_url = "https://deepaucksharma.github.io/DStudio/"
    urls = []
    
    for idx, page in enumerate(top_pages, 1):
        page_id = page['page_id']
        
        # Generate URL from page_id
        if page_id == 'index':
            url = base_url
        elif page_id.endswith('/index'):
            url = base_url + page_id[:-6] + '/'
        else:
            url = base_url + page_id + '/'
        
        urls.append({
            'rank': idx,
            'page_id': page_id,
            'title': page['title'],
            'url': url,
            'quality': page['quality'],
            'pagerank': page['pagerank_scaled'],
            'importance': page['importance'],
            'links': page['total_links'],
            'broken': page['broken_links']
        })
        
        # Print the row
        display_id = page_id[:70] if len(page_id) > 70 else page_id
        print(f"{idx:4} | {display_id:<70} | {page['quality']:7.1f} | {page['pagerank_scaled']:8.2f} | {page['importance']:10.2f} | {page['total_links']:5} | {page['broken_links']:6}")

    # Save URLs to JSON file
    with open('top_100_pages.json', 'w') as f:
        json.dump(urls, f, indent=2)
    
    print(f"\n✅ Top 100 pages saved to top_100_pages.json")

    # Print working URLs for top 20
    print('\n' + '=' * 60)
    print('TOP 20 WORKING URLs')
    print('=' * 60)
    
    for item in urls[:20]:
        print(f"{item['rank']:2}. {item['url']}")
        if item['title']:
            print(f"    Title: {item['title']}")
        print(f"    Quality: {item['quality']:.1f} | PageRank: {item['pagerank']:.2f} | Broken Links: {item['broken']}")
        print()

    # Get pages with most broken links
    print('=' * 60)
    print('PAGES WITH MOST BROKEN LINKS')
    print('=' * 60)

    cursor.execute('''
    SELECT 
        src_page,
        COUNT(*) as broken_count
    FROM links
    WHERE is_valid = 0 AND is_external = 0
    GROUP BY src_page
    ORDER BY broken_count DESC
    LIMIT 10
    ''')

    for row in cursor.fetchall():
        print(f"{row['broken_count']:3} broken links: {row['src_page']}")

    # Get most common broken destinations
    print('\n' + '=' * 60)
    print('MOST COMMON BROKEN LINK DESTINATIONS')
    print('=' * 60)

    cursor.execute('''
    SELECT 
        dst_page,
        COUNT(*) as reference_count
    FROM links
    WHERE is_valid = 0 AND is_external = 0 AND dst_page IS NOT NULL
    GROUP BY dst_page
    ORDER BY reference_count DESC
    LIMIT 10
    ''')

    for row in cursor.fetchall():
        print(f"{row['reference_count']:3} references to: {row['dst_page']}")

    conn.close()

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    generate_report()
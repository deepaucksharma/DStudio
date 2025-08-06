#!/usr/bin/env python3
"""
Generate final comprehensive summary of the knowledge graph with all pages
"""

import sqlite3
import networkx as nx
import json
from collections import Counter, defaultdict

def generate_final_summary(db_path="knowledge_graph_ultimate.db"):
    """Generate comprehensive summary of all 627 pages in the graph"""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 80)
    print("FINAL KNOWLEDGE GRAPH SUMMARY - ALL 627 PAGES")
    print("=" * 80)
    
    # 1. Overall statistics
    cursor.execute("SELECT COUNT(*) FROM pages")
    total_pages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM links WHERE is_external = 0")
    total_links = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 0 AND is_external = 0")
    broken_links = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 1 AND is_external = 0")
    valid_links = cursor.fetchone()[0]
    
    print(f"\n📊 OVERALL STATISTICS")
    print(f"  Total Pages: {total_pages}")
    print(f"  Total Internal Links: {total_links}")
    print(f"  Valid Links: {valid_links} ({(valid_links/total_links)*100:.1f}%)")
    print(f"  Broken Links: {broken_links} ({(broken_links/total_links)*100:.1f}%)")
    
    # 2. Category breakdown
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM pages
        GROUP BY category
        ORDER BY count DESC
    """)
    
    print(f"\n📁 PAGES BY CATEGORY")
    categories = cursor.fetchall()
    for cat in categories[:10]:
        category = cat['category'] or 'root'
        print(f"  {category}: {cat['count']} pages")
    
    # 3. Build NetworkX graph for analysis
    G = nx.DiGraph()
    
    cursor.execute("SELECT page_id FROM pages")
    for row in cursor.fetchall():
        G.add_node(row['page_id'])
    
    cursor.execute("""
        SELECT src_page, dst_page
        FROM links
        WHERE is_external = 0 AND is_valid = 1 AND dst_page IS NOT NULL
    """)
    
    for link in cursor.fetchall():
        if link['src_page'] in G and link['dst_page'] in G:
            G.add_edge(link['src_page'], link['dst_page'])
    
    # 4. Connectivity analysis
    wcc = list(nx.weakly_connected_components(G))
    largest_wcc = max(wcc, key=len)
    
    print(f"\n🔗 CONNECTIVITY ANALYSIS")
    print(f"  Connected Components: {len(wcc)}")
    print(f"  Largest Component: {len(largest_wcc)} pages ({(len(largest_wcc)/total_pages)*100:.1f}%)")
    print(f"  Isolated Pages: {len([c for c in wcc if len(c) == 1])}")
    
    # Find unreachable from index
    unreachable = total_pages
    if 'index' in G:
        reachable = nx.descendants(G, 'index')
        reachable.add('index')
        unreachable = total_pages - len(reachable)
        print(f"  Reachable from Index: {len(reachable)} pages")
        print(f"  Unreachable from Index: {unreachable} pages")
    
    # 5. Top broken link patterns
    cursor.execute("""
        SELECT dst_page, COUNT(*) as count
        FROM links
        WHERE is_valid = 0 AND is_external = 0 AND dst_page IS NOT NULL
        GROUP BY dst_page
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print(f"\n⚠️  TOP BROKEN LINK DESTINATIONS")
    for row in cursor.fetchall():
        print(f"  {row['count']:3} references to: {row['dst_page'][:70]}")
    
    # 6. Quality analysis
    cursor.execute("""
        SELECT 
            AVG(quality_score) as avg_quality,
            MIN(quality_score) as min_quality,
            MAX(quality_score) as max_quality,
            COUNT(CASE WHEN quality_score < 50 THEN 1 END) as low_quality,
            COUNT(CASE WHEN quality_score >= 90 THEN 1 END) as high_quality
        FROM pages
    """)
    
    quality = cursor.fetchone()
    print(f"\n✨ CONTENT QUALITY")
    print(f"  Average Quality Score: {quality['avg_quality']:.1f}/100")
    print(f"  High Quality (≥90): {quality['high_quality']} pages")
    print(f"  Low Quality (<50): {quality['low_quality']} pages")
    
    # 7. Most connected pages
    if G.number_of_nodes() > 0:
        in_degrees = [(n, G.in_degree(n)) for n in G.nodes()]
        out_degrees = [(n, G.out_degree(n)) for n in G.nodes()]
        
        in_degrees.sort(key=lambda x: x[1], reverse=True)
        out_degrees.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n🌟 MOST CONNECTED PAGES")
        print("  Most Referenced (incoming links):")
        for page, degree in in_degrees[:5]:
            print(f"    {degree:3} <- {page[:60]}")
        
        print("  Most Linking (outgoing links):")
        for page, degree in out_degrees[:5]:
            print(f"    {degree:3} -> {page[:60]}")
    
    # 8. Issue summary
    cursor.execute("""
        SELECT issue_type, COUNT(*) as count
        FROM issues
        GROUP BY issue_type
        ORDER BY count DESC
    """)
    
    print(f"\n🔍 IDENTIFIED ISSUES")
    issues = cursor.fetchall()
    total_issues = sum(row['count'] for row in issues)
    print(f"  Total Issues: {total_issues}")
    for issue in issues:
        print(f"  {issue['issue_type']}: {issue['count']}")
    
    # 9. Path patterns
    cursor.execute("SELECT page_id FROM pages")
    path_depths = defaultdict(int)
    path_prefixes = defaultdict(int)
    
    for row in cursor.fetchall():
        page_id = row[0]
        depth = len(page_id.split('/'))
        path_depths[depth] += 1
        
        if '/' in page_id:
            prefix = page_id.split('/')[0]
            path_prefixes[prefix] += 1
    
    print(f"\n📂 PATH STRUCTURE")
    print("  Page Depth Distribution:")
    for depth in sorted(path_depths.keys())[:5]:
        print(f"    Level {depth}: {path_depths[depth]} pages")
    
    print("  Top Path Prefixes:")
    for prefix, count in sorted(path_prefixes.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    {prefix}/: {count} pages")
    
    # 10. Recommendations
    print(f"\n💡 KEY RECOMMENDATIONS")
    
    recommendations = []
    
    if broken_links > total_links * 0.5:
        recommendations.append(f"1. Fix {broken_links} broken links (currently {(broken_links/total_links)*100:.1f}% broken)")
    
    if unreachable > total_pages * 0.3:
        recommendations.append(f"2. Connect {unreachable} unreachable pages to main navigation")
    
    if quality['low_quality'] > 10:
        recommendations.append(f"3. Improve {quality['low_quality']} low-quality pages")
    
    if len(wcc) > 100:
        recommendations.append(f"4. Consolidate {len(wcc)} disconnected components")
    
    isolated = len([c for c in wcc if len(c) == 1])
    if isolated > 50:
        recommendations.append(f"5. Link {isolated} isolated pages")
    
    for rec in recommendations[:5]:
        print(f"  {rec}")
    
    # Save comprehensive report
    report = {
        'summary': {
            'total_pages': total_pages,
            'total_links': total_links,
            'valid_links': valid_links,
            'broken_links': broken_links,
            'broken_rate': round((broken_links/total_links)*100, 1)
        },
        'connectivity': {
            'components': len(wcc),
            'largest_component': len(largest_wcc),
            'isolated_pages': len([c for c in wcc if len(c) == 1]),
            'unreachable_from_index': unreachable
        },
        'quality': {
            'average': round(quality['avg_quality'], 1),
            'high_quality': quality['high_quality'],
            'low_quality': quality['low_quality']
        },
        'categories': [{'name': cat['category'] or 'root', 'count': cat['count']} 
                      for cat in categories],
        'recommendations': recommendations
    }
    
    with open('final_knowledge_graph_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    conn.close()
    
    print(f"\n✅ Complete report saved to final_knowledge_graph_report.json")
    
    return report

def list_all_pages_hierarchically(db_path="knowledge_graph_ultimate.db"):
    """List all 627 pages in hierarchical structure"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT page_id, title, quality_score FROM pages ORDER BY page_id")
    pages = cursor.fetchall()
    
    # Organize hierarchically
    tree = defaultdict(list)
    
    for page_id, title, quality in pages:
        parts = page_id.split('/')
        if len(parts) == 1:
            tree['root'].append((page_id, title, quality))
        else:
            parent = '/'.join(parts[:-1])
            tree[parent].append((page_id, title, quality))
    
    print("\n" + "=" * 80)
    print("HIERARCHICAL PAGE LISTING (ALL 627 PAGES)")
    print("=" * 80)
    
    def print_tree(parent='root', indent=0):
        if parent in tree:
            for page_id, title, quality in sorted(tree[parent]):
                prefix = "  " * indent + "├── "
                if quality < 50:
                    marker = "⚠️"
                elif quality >= 90:
                    marker = "✅"
                else:
                    marker = "📄"
                
                display_title = title or page_id.split('/')[-1]
                if len(display_title) > 50:
                    display_title = display_title[:47] + "..."
                
                print(f"{prefix}{marker} {display_title} [{quality:.0f}]")
                
                # Recursively print children
                if page_id in tree:
                    print_tree(page_id, indent + 1)
    
    # Start with root level pages
    print("\n📁 ROOT")
    for page_id, title, quality in sorted(tree['root']):
        marker = "✅" if quality >= 90 else "📄"
        print(f"├── {marker} {page_id} [{quality:.0f}]")
        if page_id in tree:
            print_tree(page_id, 1)
    
    conn.close()

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    
    # Generate comprehensive summary
    report = generate_final_summary()
    
    # Optionally list all pages (this would be very long)
    # Uncomment to see full hierarchical listing:
    # list_all_pages_hierarchically()
    
    print("\n" + "=" * 80)
    print("KNOWLEDGE GRAPH ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"✅ All {report['summary']['total_pages']} pages analyzed")
    print(f"✅ {report['summary']['valid_links']} valid links mapped")
    print(f"✅ {len(report['recommendations'])} key issues identified")
    print(f"✅ Reports saved to:")
    print("   - final_knowledge_graph_report.json")
    print("   - troubleshooting_report.json")
    print("   - graph_analysis_report.json")
    print("   - top_100_pages.json")
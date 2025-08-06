#!/usr/bin/env python3
"""
Test and validate the knowledge graph implementation
"""

import sqlite3
import json
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, Counter

def test_link_normalization():
    """Test link normalization logic"""
    print("=" * 60)
    print("TESTING LINK NORMALIZATION")
    print("=" * 60)
    
    test_cases = [
        # (source_page, link, expected_result)
        ("index", "core-principles/", "core-principles/index"),
        ("index", "./core-principles/", "core-principles/index"),
        ("index", "core-principles/laws/", "core-principles/laws/index"),
        ("pattern-library/index", "../core-principles/", "core-principles/index"),
        ("pattern-library/resilience/circuit-breaker", "../../core-principles/laws/correlated-failure.md", "core-principles/laws/correlated-failure"),
        ("pattern-library/resilience/circuit-breaker", "../scaling/auto-scaling.md", "pattern-library/scaling/auto-scaling"),
        ("architects-handbook/case-studies/databases/redis", "../../../pattern-library/", "pattern-library/index"),
        ("docs/index", "#overview", "docs/index"),
        ("start-here/index", "/core-principles/", "core-principles/index"),
    ]
    
    from knowledge_graph_ultimate import OptimizedKnowledgeGraph
    kg = OptimizedKnowledgeGraph(":memory:")  # In-memory for testing
    
    passed = 0
    failed = 0
    
    for source, link, expected in test_cases:
        result = kg._normalize_internal_link(link, source)
        if result == expected:
            print(f"✓ {source} + {link} = {result}")
            passed += 1
        else:
            print(f"✗ {source} + {link}")
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

def analyze_database(db_path="knowledge_graph_ultimate.db"):
    """Analyze the database structure and content"""
    print("\n" + "=" * 60)
    print("DATABASE ANALYSIS")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check actual files vs database
    docs_path = Path("docs")
    actual_files = set()
    for md_file in docs_path.rglob("*.md"):
        rel_path = md_file.relative_to(docs_path).with_suffix('').as_posix()
        actual_files.add(rel_path)
    
    cursor.execute("SELECT page_id FROM pages")
    db_pages = set(row['page_id'] for row in cursor.fetchall())
    
    print(f"\nFile System vs Database:")
    print(f"  Files on disk: {len(actual_files)}")
    print(f"  Pages in DB:   {len(db_pages)}")
    
    missing_from_db = actual_files - db_pages
    if missing_from_db:
        print(f"\n  Missing from DB ({len(missing_from_db)}):")
        for page in list(missing_from_db)[:5]:
            print(f"    - {page}")
    
    extra_in_db = db_pages - actual_files
    if extra_in_db:
        print(f"\n  Extra in DB ({len(extra_in_db)}):")
        for page in list(extra_in_db)[:5]:
            print(f"    - {page}")
    
    # Analyze broken links
    print("\n" + "-" * 40)
    print("BROKEN LINK ANALYSIS")
    print("-" * 40)
    
    cursor.execute("""
        SELECT l.src_page, l.dst_page, l.dst_url, l.is_valid
        FROM links l
        WHERE l.is_external = 0 AND l.is_valid = 0
        LIMIT 20
    """)
    
    broken_links = cursor.fetchall()
    print(f"\nSample broken internal links:")
    
    for link in broken_links[:10]:
        # Check if destination actually exists
        expected_dst = link['dst_page']
        if expected_dst in actual_files:
            print(f"  FALSE POSITIVE: {link['src_page']} -> {link['dst_url']}")
            print(f"    Normalized to: {expected_dst} (EXISTS!)")
        else:
            print(f"  TRULY BROKEN: {link['src_page']} -> {link['dst_url']}")
            print(f"    Normalized to: {expected_dst} (missing)")
    
    # Check specific common patterns
    print("\n" + "-" * 40)
    print("COMMON LINK PATTERNS")
    print("-" * 40)
    
    cursor.execute("""
        SELECT dst_url, COUNT(*) as count
        FROM links
        WHERE is_external = 0
        GROUP BY dst_url
        ORDER BY count DESC
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        print(f"  {row['count']:4}x {row['dst_url']}")
    
    # Check if paths are being resolved correctly
    print("\n" + "-" * 40)
    print("PATH RESOLUTION CHECK")
    print("-" * 40)
    
    # Test a specific known good link
    cursor.execute("""
        SELECT * FROM links
        WHERE src_page = 'pattern-library/resilience/circuit-breaker'
        AND dst_url LIKE '%core-principles%'
        LIMIT 5
    """)
    
    for link in cursor.fetchall():
        print(f"\nFrom: {link['src_page']}")
        print(f"  Link: {link['dst_url']}")
        print(f"  Resolved to: {link['dst_page']}")
        print(f"  Valid: {link['is_valid']}")
        
        # Check if the resolved page exists
        if link['dst_page'] in actual_files:
            print(f"  ✓ Target exists on disk!")
        else:
            print(f"  ✗ Target missing - might be wrong resolution")
    
    conn.close()

def visualize_graph(db_path="knowledge_graph_ultimate.db", output_file="knowledge_graph.png"):
    """Create a visualization of the page graph"""
    print("\n" + "=" * 60)
    print("GRAPH VISUALIZATION")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build NetworkX graph
    G = nx.DiGraph()
    
    # Add nodes with categories
    cursor.execute("SELECT page_id, category, quality_score FROM pages")
    categories = defaultdict(list)
    for row in cursor.fetchall():
        G.add_node(row['page_id'], 
                  category=row['category'] or 'root',
                  quality=row['quality_score'])
        categories[row['category'] or 'root'].append(row['page_id'])
    
    print(f"\nCategories found:")
    for cat, pages in categories.items():
        print(f"  {cat}: {len(pages)} pages")
    
    # Add edges (only valid links)
    cursor.execute("""
        SELECT src_page, dst_page 
        FROM links 
        WHERE is_external = 0 AND is_valid = 1
    """)
    
    edges = cursor.fetchall()
    for edge in edges:
        if edge['dst_page']:
            G.add_edge(edge['src_page'], edge['dst_page'])
    
    print(f"\nGraph statistics:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    
    if G.number_of_nodes() > 0:
        # Calculate metrics
        if G.number_of_edges() > 0:
            print(f"  Density: {nx.density(G):.4f}")
            
            # Find connected components
            weakly_connected = list(nx.weakly_connected_components(G))
            print(f"  Weakly connected components: {len(weakly_connected)}")
            print(f"  Largest component size: {len(max(weakly_connected, key=len))}")
            
            # Find most connected nodes
            in_degree = dict(G.in_degree())
            out_degree = dict(G.out_degree())
            
            print(f"\n  Most linked-to pages:")
            for node, degree in sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    {degree:3} <- {node}")
            
            print(f"\n  Most linking pages:")
            for node, degree in sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    {degree:3} -> {node}")
    
    # Create a smaller subgraph for visualization (top nodes)
    if G.number_of_nodes() > 50:
        print(f"\nCreating subgraph for visualization (too many nodes: {G.number_of_nodes()})")
        
        # Get top nodes by PageRank
        if G.number_of_edges() > 0:
            pagerank = nx.pagerank(G)
            top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:30]
            subgraph_nodes = [node for node, _ in top_nodes]
            
            # Add their immediate neighbors
            for node in list(subgraph_nodes):
                subgraph_nodes.extend(list(G.predecessors(node))[:2])
                subgraph_nodes.extend(list(G.successors(node))[:2])
            
            subgraph_nodes = list(set(subgraph_nodes))[:50]
            G = G.subgraph(subgraph_nodes)
            print(f"  Subgraph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    conn.close()
    
    # Visualize if not too large
    if G.number_of_nodes() > 0 and G.number_of_nodes() <= 100:
        plt.figure(figsize=(20, 15))
        
        # Use spring layout for better visualization
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Color nodes by category
        node_colors = []
        for node in G.nodes():
            cat = G.nodes[node].get('category', 'root')
            if 'pattern' in cat:
                node_colors.append('lightblue')
            elif 'architect' in cat:
                node_colors.append('lightgreen')
            elif 'core' in cat:
                node_colors.append('yellow')
            elif 'interview' in cat:
                node_colors.append('lightcoral')
            else:
                node_colors.append('lightgray')
        
        # Draw the graph
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=50, alpha=0.8)
        nx.draw_networkx_edges(G, pos, edge_color='gray', 
                              alpha=0.3, arrows=True, arrowsize=10)
        
        # Add labels for high-degree nodes
        labels = {}
        for node in G.nodes():
            if G.in_degree(node) > 5 or G.out_degree(node) > 10:
                labels[node] = node.split('/')[-1][:20]
        
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title(f"Knowledge Graph Visualization ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\nGraph saved to {output_file}")
    else:
        print(f"\nGraph too large for visualization ({G.number_of_nodes()} nodes)")

def debug_specific_cases(db_path="knowledge_graph_ultimate.db"):
    """Debug specific problematic cases"""
    print("\n" + "=" * 60)
    print("DEBUGGING SPECIFIC CASES")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check a known good page
    test_page = "pattern-library/resilience/circuit-breaker"
    
    print(f"\nAnalyzing page: {test_page}")
    
    cursor.execute("SELECT * FROM pages WHERE page_id = ?", (test_page,))
    page = cursor.fetchone()
    
    if page:
        print(f"  Title: {page['title']}")
        print(f"  Quality: {page['quality_score']}/100")
        print(f"  Links: {page['link_count']}")
    else:
        print(f"  ERROR: Page not found in database!")
        return
    
    # Check its links
    cursor.execute("""
        SELECT dst_url, dst_page, is_valid, link_text
        FROM links
        WHERE src_page = ?
        ORDER BY dst_url
    """, (test_page,))
    
    links = cursor.fetchall()
    print(f"\n  Outgoing links ({len(links)}):")
    
    valid_count = 0
    broken_count = 0
    
    for link in links[:10]:  # First 10
        status = "✓" if link['is_valid'] else "✗"
        print(f"    {status} {link['dst_url'][:50]}")
        if link['dst_page']:
            print(f"       -> {link['dst_page']}")
        
        if link['is_valid']:
            valid_count += 1
        else:
            broken_count += 1
    
    print(f"\n  Summary: {valid_count} valid, {broken_count} broken")
    
    # Check incoming links
    cursor.execute("""
        SELECT src_page, link_text
        FROM links
        WHERE dst_page = ?
        LIMIT 10
    """, (test_page,))
    
    incoming = cursor.fetchall()
    print(f"\n  Incoming links ({len(incoming)}):")
    for link in incoming:
        print(f"    <- {link['src_page']}")
    
    # Check if relative paths are the issue
    print("\n" + "-" * 40)
    print("RELATIVE PATH ANALYSIS")
    print("-" * 40)
    
    cursor.execute("""
        SELECT dst_url, COUNT(*) as count
        FROM links
        WHERE is_external = 0 
        AND is_valid = 0
        AND (dst_url LIKE '../%' OR dst_url LIKE '../../%')
        GROUP BY dst_url
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\nMost common broken relative links:")
    for row in cursor.fetchall():
        print(f"  {row['count']:4}x {row['dst_url']}")
    
    # Check absolute path issues
    cursor.execute("""
        SELECT dst_url, COUNT(*) as count
        FROM links
        WHERE is_external = 0 
        AND is_valid = 0
        AND dst_url LIKE '/%'
        GROUP BY dst_url
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\nBroken absolute path links:")
    for row in cursor.fetchall():
        print(f"  {row['count']:4}x {row['dst_url']}")
    
    conn.close()

def main():
    """Run all tests and validations"""
    print("KNOWLEDGE GRAPH VALIDATION SUITE")
    print("=" * 60)
    
    # Test link normalization
    if not test_link_normalization():
        print("\n❌ Link normalization tests failed!")
        print("This explains the high broken link rate.")
    
    # Analyze database
    analyze_database()
    
    # Debug specific cases
    debug_specific_cases()
    
    # Visualize graph
    try:
        visualize_graph()
    except Exception as e:
        print(f"\nVisualization failed: {e}")
    
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
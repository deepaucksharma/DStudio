#!/usr/bin/env python3
"""
Comprehensive graph analysis and troubleshooting for all pages
"""

import sqlite3
import networkx as nx
import json
from collections import defaultdict, Counter
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def build_complete_graph(db_path="knowledge_graph_ultimate.db"):
    """Build NetworkX graph with all pages and links"""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add all pages as nodes
    cursor.execute("""
        SELECT page_id, title, category, quality_score, word_count, 
               link_count, heading_count
        FROM pages
    """)
    
    pages = cursor.fetchall()
    for page in pages:
        G.add_node(page['page_id'], 
                  title=page['title'] or page['page_id'],
                  category=page['category'] or 'uncategorized',
                  quality_score=page['quality_score'],
                  word_count=page['word_count'],
                  link_count=page['link_count'],
                  heading_count=page['heading_count'])
    
    # Add all links as edges
    cursor.execute("""
        SELECT src_page, dst_page, is_valid, is_external
        FROM links
        WHERE is_external = 0 AND dst_page IS NOT NULL
    """)
    
    links = cursor.fetchall()
    for link in links:
        if link['src_page'] in G and link['dst_page'] in G:
            G.add_edge(link['src_page'], link['dst_page'], 
                      is_valid=link['is_valid'])
    
    conn.close()
    return G

def analyze_graph_issues(G):
    """Comprehensive analysis of graph issues"""
    
    issues = {
        'orphaned_pages': [],
        'dead_ends': [],
        'circular_dependencies': [],
        'broken_link_clusters': [],
        'unreachable_pages': [],
        'high_complexity_pages': [],
        'missing_categories': [],
        'path_inconsistencies': []
    }
    
    # Find orphaned pages (no incoming or outgoing links)
    for node in G.nodes():
        in_degree = G.in_degree(node)
        out_degree = G.out_degree(node)
        
        if in_degree == 0 and out_degree == 0:
            issues['orphaned_pages'].append({
                'page': node,
                'title': G.nodes[node].get('title', node)
            })
        elif out_degree == 0 and in_degree > 0:
            issues['dead_ends'].append({
                'page': node,
                'incoming_links': in_degree
            })
    
    # Find strongly connected components (circular dependencies)
    sccs = list(nx.strongly_connected_components(G))
    for scc in sccs:
        if len(scc) > 1:  # Multi-node cycles
            issues['circular_dependencies'].append({
                'pages': list(scc),
                'size': len(scc)
            })
    
    # Find unreachable pages from index
    if 'index' in G:
        reachable = nx.descendants(G, 'index')
        reachable.add('index')
        all_nodes = set(G.nodes())
        unreachable = all_nodes - reachable
        
        for node in unreachable:
            issues['unreachable_pages'].append({
                'page': node,
                'in_degree': G.in_degree(node),
                'out_degree': G.out_degree(node)
            })
    
    # Analyze broken link clusters
    broken_edges = [(u, v) for u, v, d in G.edges(data=True) 
                    if not d.get('is_valid', True)]
    
    if broken_edges:
        broken_subgraph = G.edge_subgraph(broken_edges)
        components = nx.weakly_connected_components(broken_subgraph)
        for comp in components:
            comp_list = list(comp)
            if len(comp_list) > 2:
                issues['broken_link_clusters'].append({
                    'pages': comp_list,
                    'size': len(comp_list)
                })
    
    # Find high complexity pages (too many links)
    for node in G.nodes():
        out_degree = G.out_degree(node)
        if out_degree > 50:
            issues['high_complexity_pages'].append({
                'page': node,
                'outgoing_links': out_degree,
                'title': G.nodes[node].get('title', node)
            })
    
    # Check for path inconsistencies
    for node in G.nodes():
        parts = node.split('/')
        
        # Check for duplicate path segments
        if len(parts) != len(set(parts)):
            issues['path_inconsistencies'].append({
                'page': node,
                'issue': 'duplicate_segments',
                'segments': parts
            })
        
        # Check for problematic patterns
        if 'pattern-library' in node and 'architects-handbook' in node:
            issues['path_inconsistencies'].append({
                'page': node,
                'issue': 'mixed_hierarchy',
                'path': node
            })
    
    # Find pages with missing categories
    for node, data in G.nodes(data=True):
        if not data.get('category') or data['category'] == 'uncategorized':
            issues['missing_categories'].append({
                'page': node,
                'title': data.get('title', node)
            })
    
    return issues

def analyze_broken_links(db_path="knowledge_graph_ultimate.db"):
    """Detailed analysis of broken links"""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all broken links with details
    cursor.execute("""
        SELECT src_page, dst_page, dst_url, COUNT(*) as count
        FROM links
        WHERE is_valid = 0 AND is_external = 0
        GROUP BY src_page, dst_page
        ORDER BY count DESC
    """)
    
    broken_links = cursor.fetchall()
    
    # Categorize broken links by pattern
    patterns = defaultdict(list)
    
    for link in broken_links:
        dst = link['dst_page'] or link['dst_url']
        
        if not dst:
            continue
            
        # Identify patterns
        if 'pattern-library' in dst and 'architects-handbook' in dst:
            patterns['incorrect_hierarchy'].append(link)
        elif 'engineering-leadership/engineering-leadership' in dst:
            patterns['duplicate_path'].append(link)
        elif 'core-principles/laws' in dst and 'architects-handbook' in dst:
            patterns['wrong_base_path'].append(link)
        elif dst.endswith('/index/index'):
            patterns['double_index'].append(link)
        elif '../' in dst or './' in dst:
            patterns['unresolved_relative'].append(link)
        else:
            patterns['other'].append(link)
    
    conn.close()
    return patterns

def generate_visualization(G, output_dir="graph_visualizations"):
    """Generate various graph visualizations"""
    
    Path(output_dir).mkdir(exist_ok=True)
    
    # 1. Category distribution
    categories = [data.get('category', 'uncategorized') 
                 for _, data in G.nodes(data=True)]
    category_counts = Counter(categories)
    
    plt.figure(figsize=(12, 6))
    plt.bar(category_counts.keys(), category_counts.values())
    plt.xticks(rotation=45, ha='right')
    plt.title('Page Distribution by Category')
    plt.xlabel('Category')
    plt.ylabel('Number of Pages')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/category_distribution.png")
    plt.close()
    
    # 2. Link degree distribution
    in_degrees = [G.in_degree(n) for n in G.nodes()]
    out_degrees = [G.out_degree(n) for n in G.nodes()]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    ax1.hist(in_degrees, bins=30, edgecolor='black')
    ax1.set_title('Incoming Links Distribution')
    ax1.set_xlabel('Number of Incoming Links')
    ax1.set_ylabel('Number of Pages')
    ax1.set_yscale('log')
    
    ax2.hist(out_degrees, bins=30, edgecolor='black')
    ax2.set_title('Outgoing Links Distribution')
    ax2.set_xlabel('Number of Outgoing Links')
    ax2.set_ylabel('Number of Pages')
    ax2.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/degree_distribution.png")
    plt.close()
    
    # 3. Component analysis
    weakly_connected = list(nx.weakly_connected_components(G))
    strongly_connected = list(nx.strongly_connected_components(G))
    
    wcc_sizes = [len(c) for c in weakly_connected]
    scc_sizes = [len(c) for c in strongly_connected if len(c) > 1]
    
    if scc_sizes:
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(scc_sizes)), sorted(scc_sizes, reverse=True))
        plt.title('Strongly Connected Components (Cycles)')
        plt.xlabel('Component Index')
        plt.ylabel('Component Size')
        plt.savefig(f"{output_dir}/connected_components.png")
        plt.close()
    
    print(f"Visualizations saved to {output_dir}/")
    
    return {
        'total_nodes': G.number_of_nodes(),
        'total_edges': G.number_of_edges(),
        'weakly_connected_components': len(weakly_connected),
        'largest_wcc_size': max(wcc_sizes) if wcc_sizes else 0,
        'strongly_connected_components': len([c for c in strongly_connected if len(c) > 1]),
        'avg_in_degree': sum(in_degrees) / len(in_degrees) if in_degrees else 0,
        'avg_out_degree': sum(out_degrees) / len(out_degrees) if out_degrees else 0,
        'max_in_degree': max(in_degrees) if in_degrees else 0,
        'max_out_degree': max(out_degrees) if out_degrees else 0
    }

def generate_fix_script(issues, patterns):
    """Generate SQL script to fix identified issues"""
    
    fixes = []
    
    # Fix duplicate path patterns
    for link in patterns.get('duplicate_path', []):
        dst = link['dst_page']
        if 'engineering-leadership/engineering-leadership' in dst:
            fixed = dst.replace('engineering-leadership/engineering-leadership', 
                              'engineering-leadership')
            fixes.append(f"""
UPDATE links 
SET dst_page = '{fixed}', is_valid = 1
WHERE dst_page = '{dst}';
""")
    
    # Fix incorrect hierarchy patterns
    for link in patterns.get('incorrect_hierarchy', []):
        dst = link['dst_page']
        if 'architects-handbook/case-studies/pattern-library' in dst:
            fixed = dst.replace('architects-handbook/case-studies/pattern-library', 
                              'pattern-library')
            fixes.append(f"""
UPDATE links 
SET dst_page = '{fixed}', is_valid = 1
WHERE dst_page = '{dst}';
""")
    
    # Fix wrong base path patterns
    for link in patterns.get('wrong_base_path', []):
        dst = link['dst_page']
        if 'architects-handbook/core-principles' in dst:
            fixed = dst.replace('architects-handbook/core-principles', 
                              'core-principles')
            fixes.append(f"""
UPDATE links 
SET dst_page = '{fixed}', is_valid = 1
WHERE dst_page = '{dst}';
""")
    
    # Save fixes to file
    with open('fix_broken_links.sql', 'w') as f:
        f.write("-- SQL script to fix broken links\n")
        f.write("-- Generated by analyze_full_graph.py\n\n")
        f.write("BEGIN TRANSACTION;\n\n")
        
        for fix in fixes[:100]:  # Limit to first 100 fixes for safety
            f.write(fix)
        
        f.write("\nCOMMIT;\n")
    
    return len(fixes)

def main():
    print("=" * 60)
    print("COMPREHENSIVE GRAPH ANALYSIS")
    print("=" * 60)
    
    # Build complete graph
    print("\n1. Building complete graph...")
    G = build_complete_graph()
    
    # Generate statistics
    stats = generate_visualization(G)
    print(f"\nGraph Statistics:")
    print(f"  - Total pages: {stats['total_nodes']}")
    print(f"  - Total links: {stats['total_edges']}")
    print(f"  - Weakly connected components: {stats['weakly_connected_components']}")
    print(f"  - Largest component: {stats['largest_wcc_size']} pages")
    print(f"  - Average links per page: {stats['avg_out_degree']:.1f}")
    print(f"  - Max outgoing links: {stats['max_out_degree']}")
    
    # Analyze issues
    print("\n2. Analyzing graph issues...")
    issues = analyze_graph_issues(G)
    
    print(f"\nIssues Found:")
    print(f"  - Orphaned pages: {len(issues['orphaned_pages'])}")
    print(f"  - Dead end pages: {len(issues['dead_ends'])}")
    print(f"  - Circular dependencies: {len(issues['circular_dependencies'])} cycles")
    print(f"  - Unreachable pages: {len(issues['unreachable_pages'])}")
    print(f"  - High complexity pages: {len(issues['high_complexity_pages'])}")
    print(f"  - Path inconsistencies: {len(issues['path_inconsistencies'])}")
    print(f"  - Missing categories: {len(issues['missing_categories'])}")
    
    # Analyze broken links
    print("\n3. Analyzing broken link patterns...")
    patterns = analyze_broken_links()
    
    print(f"\nBroken Link Patterns:")
    for pattern, links in patterns.items():
        if links:
            print(f"  - {pattern}: {len(links)} cases")
            if len(links) > 0:
                sample = links[0]
                print(f"    Example: {sample['src_page']} -> {sample['dst_page']}")
    
    # Generate fixes
    print("\n4. Generating fix script...")
    num_fixes = generate_fix_script(issues, patterns)
    print(f"  Generated {num_fixes} SQL fixes in fix_broken_links.sql")
    
    # Save detailed report
    report = {
        'statistics': stats,
        'issues': {
            'orphaned_pages': issues['orphaned_pages'][:10],
            'dead_ends': issues['dead_ends'][:10],
            'circular_dependencies': [
                {'pages': c['pages'][:5], 'size': c['size']} 
                for c in issues['circular_dependencies'][:5]
            ],
            'unreachable_pages': issues['unreachable_pages'][:10],
            'high_complexity_pages': issues['high_complexity_pages'][:5],
            'path_inconsistencies': issues['path_inconsistencies'][:10]
        },
        'broken_link_patterns': {
            pattern: len(links) for pattern, links in patterns.items()
        }
    }
    
    with open('graph_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Analysis complete! Check:")
    print("  - graph_visualizations/ for charts")
    print("  - graph_analysis_report.json for detailed report")
    print("  - fix_broken_links.sql for fixes")
    
    # Show top issues to fix
    print("\n" + "=" * 60)
    print("TOP PRIORITY FIXES")
    print("=" * 60)
    
    if issues['circular_dependencies']:
        print("\n⚠️  Circular Dependencies (top 3):")
        for cycle in issues['circular_dependencies'][:3]:
            print(f"  Cycle of {cycle['size']} pages:")
            for page in cycle['pages'][:5]:
                print(f"    - {page}")
    
    if issues['high_complexity_pages']:
        print("\n⚠️  High Complexity Pages (>50 links):")
        for page in issues['high_complexity_pages'][:5]:
            print(f"  {page['page']}: {page['outgoing_links']} links")
    
    if issues['unreachable_pages']:
        print(f"\n⚠️  {len(issues['unreachable_pages'])} pages unreachable from index")
        important_unreachable = [p for p in issues['unreachable_pages'] 
                                if not p['page'].endswith('/index')][:5]
        for page in important_unreachable:
            print(f"  - {page['page']}")

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    main()
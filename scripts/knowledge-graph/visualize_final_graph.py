#!/usr/bin/env python3
"""
Create final comprehensive visualization of the knowledge graph
"""

import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter
import json

def create_final_visualization(db_path="knowledge_graph_ultimate.db"):
    """Create comprehensive visualization of the final graph"""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build graph
    G = nx.DiGraph()
    
    # Load all pages
    cursor.execute("""
        SELECT page_id, title, category, quality_score, word_count
        FROM pages
    """)
    
    pages = cursor.fetchall()
    categories = set()
    
    for page in pages:
        category = page['category'] or 'uncategorized'
        categories.add(category)
        G.add_node(page['page_id'], 
                  title=page['title'] or page['page_id'],
                  category=category,
                  quality_score=page['quality_score'],
                  word_count=page['word_count'])
    
    # Load valid links only
    cursor.execute("""
        SELECT src_page, dst_page
        FROM links
        WHERE is_external = 0 AND is_valid = 1 AND dst_page IS NOT NULL
    """)
    
    for link in cursor.fetchall():
        if link['src_page'] in G and link['dst_page'] in G:
            G.add_edge(link['src_page'], link['dst_page'])
    
    # Create subgraphs for major sections
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Overall graph structure (top left)
    ax1 = plt.subplot(2, 3, 1)
    pos = nx.spring_layout(G, k=0.5, iterations=20, seed=42)
    
    # Color nodes by category
    category_colors = {
        'architects-handbook': '#FF6B6B',
        'pattern-library': '#4ECDC4',
        'interview-prep': '#45B7D1',
        'core-principles': '#96CEB4',
        'excellence': '#FFEAA7',
        'reference': '#DDA0DD',
        'uncategorized': '#808080'
    }
    
    node_colors = []
    for node in G.nodes():
        cat = G.nodes[node].get('category', 'uncategorized')
        for key in category_colors:
            if key in cat:
                node_colors.append(category_colors[key])
                break
        else:
            node_colors.append(category_colors['uncategorized'])
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=30, alpha=0.6, ax=ax1)
    nx.draw_networkx_edges(G, pos, edge_color='gray', 
                          alpha=0.2, arrows=False, ax=ax1)
    
    ax1.set_title('Complete Knowledge Graph Structure', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    # Add legend
    patches = [mpatches.Patch(color=color, label=cat.replace('-', ' ').title()) 
              for cat, color in category_colors.items() if cat != 'uncategorized']
    ax1.legend(handles=patches, loc='upper left', fontsize=8)
    
    # 2. Degree distribution (top middle)
    ax2 = plt.subplot(2, 3, 2)
    degrees = [G.degree(n) for n in G.nodes()]
    ax2.hist(degrees, bins=30, edgecolor='black', alpha=0.7)
    ax2.set_xlabel('Node Degree')
    ax2.set_ylabel('Count')
    ax2.set_title('Degree Distribution', fontsize=12, fontweight='bold')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # 3. Category distribution (top right)
    ax3 = plt.subplot(2, 3, 3)
    category_counts = Counter(G.nodes[node].get('category', 'uncategorized') 
                             for node in G.nodes())
    
    # Simplify category names
    simplified_counts = {}
    for cat, count in category_counts.items():
        if 'architects-handbook' in cat:
            key = 'Architects Handbook'
        elif 'pattern-library' in cat:
            key = 'Pattern Library'
        elif 'interview-prep' in cat:
            key = 'Interview Prep'
        elif 'core-principles' in cat:
            key = 'Core Principles'
        elif 'excellence' in cat:
            key = 'Excellence'
        else:
            key = 'Other'
        
        simplified_counts[key] = simplified_counts.get(key, 0) + count
    
    bars = ax3.bar(simplified_counts.keys(), simplified_counts.values())
    ax3.set_xlabel('Category')
    ax3.set_ylabel('Number of Pages')
    ax3.set_title('Pages by Category', fontsize=12, fontweight='bold')
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Color bars
    for bar, (cat, _) in zip(bars, simplified_counts.items()):
        if 'Architects' in cat:
            bar.set_color(category_colors['architects-handbook'])
        elif 'Pattern' in cat:
            bar.set_color(category_colors['pattern-library'])
        elif 'Interview' in cat:
            bar.set_color(category_colors['interview-prep'])
        elif 'Core' in cat:
            bar.set_color(category_colors['core-principles'])
        elif 'Excellence' in cat:
            bar.set_color(category_colors['excellence'])
        else:
            bar.set_color('#808080')
    
    # 4. Connected components (bottom left)
    ax4 = plt.subplot(2, 3, 4)
    wcc = list(nx.weakly_connected_components(G))
    scc = list(nx.strongly_connected_components(G))
    
    wcc_sizes = sorted([len(c) for c in wcc], reverse=True)[:20]
    scc_sizes = sorted([len(c) for c in scc if len(c) > 1], reverse=True)[:20]
    
    x = range(len(wcc_sizes))
    ax4.bar(x, wcc_sizes, alpha=0.7, label='Weakly Connected')
    if scc_sizes:
        ax4.bar(range(len(scc_sizes)), scc_sizes, alpha=0.7, label='Strongly Connected')
    
    ax4.set_xlabel('Component Index')
    ax4.set_ylabel('Component Size')
    ax4.set_title('Connected Components', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Quality score distribution (bottom middle)
    ax5 = plt.subplot(2, 3, 5)
    quality_scores = [G.nodes[node].get('quality_score', 0) for node in G.nodes()]
    ax5.hist(quality_scores, bins=20, edgecolor='black', alpha=0.7, color='green')
    ax5.set_xlabel('Quality Score')
    ax5.set_ylabel('Number of Pages')
    ax5.set_title('Content Quality Distribution', fontsize=12, fontweight='bold')
    ax5.axvline(x=50, color='red', linestyle='--', label='Low Quality Threshold')
    ax5.axvline(x=90, color='gold', linestyle='--', label='High Quality Threshold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Graph statistics (bottom right)
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    # Calculate statistics
    cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 0 AND is_external = 0")
    broken_links = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM links WHERE is_external = 0")
    total_links = cursor.fetchone()[0]
    
    stats_text = f"""
GRAPH STATISTICS
═══════════════════════════════

Total Pages: {G.number_of_nodes()}
Valid Links: {G.number_of_edges()}
Broken Links: {broken_links}
Total Internal Links: {total_links}

Connectivity:
• Connected Components: {len(wcc)}
• Largest Component: {max(wcc_sizes)} pages
• Circular Dependencies: {len([c for c in scc if len(c) > 1])}

Graph Metrics:
• Average Degree: {sum(degrees)/len(degrees):.1f}
• Max In-Degree: {max(G.in_degree(n) for n in G.nodes())}
• Max Out-Degree: {max(G.out_degree(n) for n in G.nodes())}
• Density: {nx.density(G):.4f}

Quality Metrics:
• Average Quality Score: {sum(quality_scores)/len(quality_scores):.1f}
• High Quality Pages (>90): {len([s for s in quality_scores if s > 90])}
• Low Quality Pages (<50): {len([s for s in quality_scores if s < 50])}

Link Health:
• Valid Links: {G.number_of_edges()} ({(G.number_of_edges()/total_links)*100:.1f}%)
• Broken Links: {broken_links} ({(broken_links/total_links)*100:.1f}%)
• Fix Rate: {((total_links - broken_links)/total_links)*100:.1f}%
"""
    
    ax6.text(0.1, 0.9, stats_text, transform=ax6.transAxes, 
            fontsize=10, verticalalignment='top', fontfamily='monospace')
    
    plt.suptitle('DStudio Knowledge Graph Analysis Dashboard', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('final_graph_visualization.png', dpi=150, bbox_inches='tight')
    
    # Export graph data for further analysis
    graph_data = {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'broken_links': broken_links,
        'total_links': total_links,
        'components': len(wcc),
        'largest_component': max(wcc_sizes),
        'avg_degree': sum(degrees)/len(degrees),
        'avg_quality': sum(quality_scores)/len(quality_scores),
        'categories': dict(simplified_counts)
    }
    
    with open('final_graph_stats.json', 'w') as f:
        json.dump(graph_data, f, indent=2)
    
    conn.close()
    
    print("✅ Visualization saved to final_graph_visualization.png")
    print("✅ Statistics saved to final_graph_stats.json")
    
    return graph_data

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    stats = create_final_visualization()
    
    print("\n" + "=" * 60)
    print("FINAL GRAPH SUMMARY")
    print("=" * 60)
    print(f"Total Pages: {stats['nodes']}")
    print(f"Valid Links: {stats['edges']}")
    print(f"Broken Links: {stats['broken_links']} ({(stats['broken_links']/stats['total_links'])*100:.1f}%)")
    print(f"Components: {stats['components']}")
    print(f"Average Degree: {stats['avg_degree']:.1f}")
    print(f"Average Quality: {stats['avg_quality']:.1f}/100")
#!/usr/bin/env python3
"""
Pattern Network Visualizer

This script creates basic visualizations of the pattern dependency network
using matplotlib and networkx. It generates different views of the pattern
ecosystem to help understand relationships and identify improvement opportunities.

Usage:
    python3 visualize_pattern_network.py
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from pathlib import Path
from collections import Counter
import numpy as np

class PatternNetworkVisualizer:
    """Creates visualizations of the pattern dependency network."""
    
    def __init__(self, analysis_file: str):
        self.analysis_file = Path(analysis_file)
        self.load_analysis_data()
        self.setup_style()
    
    def load_analysis_data(self):
        """Load the analysis data from JSON file."""
        with open(self.analysis_file, 'r') as f:
            data = json.load(f)
        
        self.analysis = data['analysis']
        self.graph_data = data['graph']
        
        # Build NetworkX graph
        self.graph = nx.DiGraph()
        
        # Add nodes
        for node in self.graph_data['nodes']:
            self.graph.add_node(node['id'], **node)
        
        # Add edges
        for edge in self.graph_data['edges']:
            self.graph.add_edge(edge['source'], edge['target'], **edge)
    
    def setup_style(self):
        """Setup visualization styling."""
        self.category_colors = {
            'resilience': '#e74c3c',      # Red
            'architecture': '#3498db',     # Blue  
            'data-management': '#2ecc71',  # Green
            'scaling': '#f39c12',         # Orange
            'coordination': '#9b59b6',     # Purple
            'security': '#e67e22',        # Dark Orange
            'communication': '#1abc9c',    # Teal
            'deployment': '#34495e',      # Dark Gray
            'ml-infrastructure': '#f1c40f', # Yellow
            'cost-optimization': '#95a5a6', # Gray
            'general': '#bdc3c7'          # Light Gray
        }
        
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def create_overview_visualization(self, output_file: str = 'pattern_network_overview.png'):
        """Create an overview visualization of the entire network."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Pattern Library Network Analysis Overview', fontsize=16, fontweight='bold')
        
        # 1. Network Graph
        self._plot_network_graph(ax1)
        
        # 2. Category Distribution
        self._plot_category_distribution(ax2)
        
        # 3. Hub Pattern Analysis
        self._plot_hub_analysis(ax3)
        
        # 4. Connectivity Metrics
        self._plot_connectivity_metrics(ax4)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"📊 Overview visualization saved to {output_file}")
    
    def _plot_network_graph(self, ax):
        """Plot the network graph."""
        ax.set_title('Pattern Dependency Network\n(Connected Components Only)', fontweight='bold')
        
        # Create subgraph of only connected nodes
        connected_nodes = []
        for node in self.graph.nodes():
            if self.graph.degree(node) > 0:
                connected_nodes.append(node)
        
        connected_graph = self.graph.subgraph(connected_nodes)
        
        if len(connected_nodes) == 0:
            ax.text(0.5, 0.5, 'No Connected Patterns\nFound', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            return
        
        # Layout
        pos = nx.spring_layout(connected_graph, k=3, iterations=50)
        
        # Node colors by category
        node_colors = []
        for node in connected_graph.nodes():
            category = connected_graph.nodes[node].get('category', 'general')
            node_colors.append(self.category_colors.get(category, '#cccccc'))
        
        # Node sizes by degree
        node_sizes = []
        for node in connected_graph.nodes():
            degree = connected_graph.degree(node)
            node_sizes.append(max(300, degree * 100))
        
        # Draw network
        nx.draw_networkx_nodes(connected_graph, pos, node_color=node_colors, 
                              node_size=node_sizes, alpha=0.8, ax=ax)
        nx.draw_networkx_edges(connected_graph, pos, alpha=0.6, 
                              edge_color='gray', arrows=True, 
                              arrowsize=20, ax=ax)
        
        # Labels for high-degree nodes only
        high_degree_nodes = {n: n for n in connected_graph.nodes() 
                           if connected_graph.degree(n) >= 2}
        nx.draw_networkx_labels(connected_graph, pos, high_degree_nodes, 
                              font_size=8, ax=ax)
        
        ax.axis('off')
    
    def _plot_category_distribution(self, ax):
        """Plot category distribution."""
        ax.set_title('Pattern Distribution by Category', fontweight='bold')
        
        category_stats = self.analysis['category_analysis']
        categories = []
        counts = []
        colors = []
        
        for category, stats in category_stats.items():
            categories.append(category.replace('-', '\n'))
            counts.append(stats['count'])
            colors.append(self.category_colors.get(category, '#cccccc'))
        
        bars = ax.bar(range(len(categories)), counts, color=colors, alpha=0.8)
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=9)
        ax.set_ylabel('Number of Patterns')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   str(count), ha='center', va='bottom', fontweight='bold')
    
    def _plot_hub_analysis(self, ax):
        """Plot hub pattern analysis."""
        ax.set_title('Top Hub Patterns (Most Connected)', fontweight='bold')
        
        hub_patterns = self.analysis['hub_patterns'][:8]
        
        if not hub_patterns:
            ax.text(0.5, 0.5, 'No Hub Patterns Found', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        names = [hub['name'] for hub in hub_patterns]
        scores = [hub['hub_score'] for hub in hub_patterns]
        categories = [hub['category'] for hub in hub_patterns]
        
        # Truncate long names
        names = [name[:20] + '...' if len(name) > 20 else name for name in names]
        
        colors = [self.category_colors.get(cat, '#cccccc') for cat in categories]
        
        bars = ax.barh(range(len(names)), scores, color=colors, alpha=0.8)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=9)
        ax.set_xlabel('Hub Score (2 × Incoming + Outgoing)')
        
        # Add value labels
        for bar, score in zip(bars, scores):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                   str(score), ha='left', va='center', fontweight='bold')
        
        ax.invert_yaxis()
    
    def _plot_connectivity_metrics(self, ax):
        """Plot connectivity metrics."""
        ax.set_title('Network Connectivity Metrics', fontweight='bold')
        
        metrics = self.analysis['graph_metrics']
        
        # Create metrics display
        metrics_text = f"""
Total Patterns: {metrics['nodes']}
Total Relationships: {metrics['edges']}
Graph Density: {metrics['density']:.4f}
Connected Components: {metrics['number_of_components']}
Average Degree: {metrics['average_degree']:.2f}

Isolated Patterns: {len(self.analysis['isolated_patterns'])}
({len(self.analysis['isolated_patterns'])/metrics['nodes']*100:.1f}% of total)

Most Referenced:
"""
        
        # Add top referenced patterns
        top_referenced = self.analysis['pattern_statistics']['most_referenced'][:5]
        for pattern, count in top_referenced:
            name = pattern[:25] + '...' if len(pattern) > 25 else pattern
            metrics_text += f"• {name}: {count}\n"
        
        ax.text(0.05, 0.95, metrics_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top', fontfamily='monospace')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    def create_category_heatmap(self, output_file: str = 'pattern_category_heatmap.png'):
        """Create a heatmap showing cross-category relationships."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Get category analysis
        category_stats = self.analysis['category_analysis']
        categories = list(category_stats.keys())
        n_cats = len(categories)
        
        # Create adjacency matrix
        matrix = np.zeros((n_cats, n_cats))
        
        # Fill in internal connections (diagonal)
        for i, cat in enumerate(categories):
            matrix[i, i] = category_stats[cat]['internal_connections']
        
        # Fill in cross-category connections
        cross_category = self.analysis['relationship_analysis']['cross_category_relationships']
        for relationship, count in cross_category.items():
            if ' → ' in relationship:
                source_cat, target_cat = relationship.split(' → ')
                if source_cat in categories and target_cat in categories:
                    source_idx = categories.index(source_cat)
                    target_idx = categories.index(target_cat)
                    matrix[source_idx, target_idx] = count
        
        # Create heatmap
        im = ax.imshow(matrix, cmap='Blues', aspect='auto')
        
        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Number of Relationships')
        
        # Set ticks and labels
        ax.set_xticks(range(n_cats))
        ax.set_yticks(range(n_cats))
        ax.set_xticklabels([cat.replace('-', '\n') for cat in categories], rotation=45, ha='right')
        ax.set_yticklabels([cat.replace('-', '\n') for cat in categories])
        
        # Add text annotations
        for i in range(n_cats):
            for j in range(n_cats):
                text = ax.text(j, i, int(matrix[i, j]),
                             ha="center", va="center", color="black" if matrix[i, j] < matrix.max()/2 else "white")
        
        ax.set_title('Cross-Category Pattern Relationships\n(Rows: Source Category, Columns: Target Category)', 
                    fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"🔥 Category heatmap saved to {output_file}")
    
    def create_isolated_patterns_chart(self, output_file: str = 'isolated_patterns_chart.png'):
        """Create a chart showing isolated patterns by category."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Count isolated patterns by category
        isolated_by_category = Counter()
        for pattern in self.analysis['isolated_patterns']:
            isolated_by_category[pattern['category']] += 1
        
        # Chart 1: Isolated patterns by category
        categories = list(isolated_by_category.keys())
        counts = list(isolated_by_category.values())
        colors = [self.category_colors.get(cat, '#cccccc') for cat in categories]
        
        bars = ax1.bar(range(len(categories)), counts, color=colors, alpha=0.8)
        ax1.set_title('Isolated Patterns by Category', fontweight='bold')
        ax1.set_xticks(range(len(categories)))
        ax1.set_xticklabels([cat.replace('-', '\n') for cat in categories], rotation=45, ha='right')
        ax1.set_ylabel('Number of Isolated Patterns')
        
        # Add value labels
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    str(count), ha='center', va='bottom', fontweight='bold')
        
        # Chart 2: Category connectivity comparison
        category_stats = self.analysis['category_analysis']
        cat_names = []
        total_patterns = []
        connected_patterns = []
        
        for cat, stats in category_stats.items():
            if cat in isolated_by_category:
                cat_names.append(cat.replace('-', '\n'))
                total_patterns.append(stats['count'])
                connected_patterns.append(stats['count'] - isolated_by_category[cat])
        
        x = range(len(cat_names))
        width = 0.35
        
        ax2.bar([i - width/2 for i in x], total_patterns, width, 
               label='Total Patterns', color='lightblue', alpha=0.8)
        ax2.bar([i + width/2 for i in x], connected_patterns, width,
               label='Connected Patterns', color='darkblue', alpha=0.8)
        
        ax2.set_title('Pattern Connectivity by Category', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(cat_names, rotation=45, ha='right')
        ax2.set_ylabel('Number of Patterns')
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"🏝️  Isolated patterns chart saved to {output_file}")

def main():
    """Main visualization function."""
    analysis_file = 'pattern_dependency_analysis.json'
    
    if not Path(analysis_file).exists():
        print(f"❌ Analysis file {analysis_file} not found. Run pattern_dependency_analyzer.py first.")
        return 1
    
    print("🎨 Creating pattern network visualizations...")
    
    try:
        visualizer = PatternNetworkVisualizer(analysis_file)
        
        # Create all visualizations
        visualizer.create_overview_visualization()
        visualizer.create_category_heatmap()
        visualizer.create_isolated_patterns_chart()
        
        print("✅ All visualizations created successfully!")
        print("\nGenerated files:")
        print("  📊 pattern_network_overview.png - Main network analysis")
        print("  🔥 pattern_category_heatmap.png - Cross-category relationships")
        print("  🏝️  isolated_patterns_chart.png - Isolated patterns analysis")
        
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
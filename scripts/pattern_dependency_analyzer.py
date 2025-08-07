#!/usr/bin/env python3
"""
Pattern Dependency Analyzer

This script analyzes all pattern files in the pattern library, extracts relationship information,
builds a dependency graph, and generates insights about pattern connectivity.

Features:
- Parses all pattern markdown files for relationships
- Builds a directed graph of dependencies  
- Exports data in JSON and GraphML formats for visualization
- Generates statistics on most referenced patterns
- Identifies isolated patterns with no connections
- Creates comprehensive insights about the pattern ecosystem

Author: Pattern Library Analysis Tool
Created: 2025-08-07
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import networkx as nx
import yaml

@dataclass
class Pattern:
    """Represents a pattern with its metadata and relationships."""
    name: str
    title: str
    description: str
    category: str
    file_path: str
    excellence_tier: Optional[str] = None
    pattern_status: Optional[str] = None
    related_patterns: List[str] = None
    references: List[str] = None
    see_also: List[str] = None
    laws_connected: List[str] = None
    
    def __post_init__(self):
        if self.related_patterns is None:
            self.related_patterns = []
        if self.references is None:
            self.references = []
        if self.see_also is None:
            self.see_also = []
        if self.laws_connected is None:
            self.laws_connected = []

class PatternDependencyAnalyzer:
    """Analyzes pattern dependencies and builds connectivity graph."""
    
    def __init__(self, pattern_library_path: str):
        self.pattern_library_path = Path(pattern_library_path)
        self.patterns: Dict[str, Pattern] = {}
        self.graph = nx.DiGraph()
        self.categories = set()
        
        # Regex patterns for extracting relationships
        self.relationship_patterns = {
            'related_patterns': [
                r'##\s+Related\s+Patterns?\s*\n(.*?)(?=\n##|\Z)',
                r'##\s+📚\s+Related\s+Patterns?\s*\n(.*?)(?=\n##|\Z)',
                r'\*\*Related\s+Patterns?\*\*[:\s]*(.*?)(?=\n\n|\Z)',
                r'Related\s+Patterns?[:\s]*\[(.*?)\]'
            ],
            'see_also': [
                r'##\s+See\s+Also\s*\n(.*?)(?=\n##|\Z)',
                r'\*\*See\s+Also\*\*[:\s]*(.*?)(?=\n\n|\Z)'
            ],
            'references': [
                r'##\s+References?\s*\n(.*?)(?=\n##|\Z)',
                r'##\s+Resources?\s+&?\s+References?\s*\n(.*?)(?=\n##|\Z)',
                r'\*\*References?\*\*[:\s]*(.*?)(?=\n\n|\Z)'
            ]
        }
        
        # Pattern to extract markdown links
        self.link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        self.pattern_link_pattern = r'/([\w-]+)\.md|/([\w-]+)/(?:index\.md)?'
    
    def find_pattern_files(self) -> List[Path]:
        """Find all pattern markdown files in the library."""
        pattern_files = []
        
        for root, dirs, files in os.walk(self.pattern_library_path):
            # Skip certain directories
            skip_dirs = {'templates', 'visual-assets', '__pycache__'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.md') and not file.startswith('README'):
                    pattern_files.append(Path(root) / file)
        
        return pattern_files
    
    def extract_frontmatter(self, content: str) -> Dict:
        """Extract YAML frontmatter from markdown content."""
        frontmatter = {}
        if content.startswith('---'):
            try:
                end_idx = content.find('\n---', 3)
                if end_idx != -1:
                    yaml_content = content[3:end_idx]
                    frontmatter = yaml.safe_load(yaml_content) or {}
            except yaml.YAMLError:
                pass
        return frontmatter
    
    def extract_pattern_links(self, text: str) -> List[str]:
        """Extract pattern names from markdown links."""
        patterns = []
        matches = re.findall(self.link_pattern, text, re.IGNORECASE)
        
        for link_text, link_url in matches:
            # Extract pattern name from URL
            pattern_match = re.search(self.pattern_link_pattern, link_url)
            if pattern_match:
                pattern_name = pattern_match.group(1) or pattern_match.group(2)
                if pattern_name:
                    patterns.append(pattern_name.replace('-', ' ').title())
        
        return patterns
    
    def extract_relationships(self, content: str) -> Dict[str, List[str]]:
        """Extract relationship information from pattern content."""
        relationships = {
            'related_patterns': [],
            'see_also': [],
            'references': []
        }
        
        for relationship_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    # Extract pattern links from the matched section
                    pattern_links = self.extract_pattern_links(match)
                    relationships[relationship_type].extend(pattern_links)
        
        # Remove duplicates
        for key in relationships:
            relationships[key] = list(set(relationships[key]))
        
        return relationships
    
    def normalize_pattern_name(self, name: str) -> str:
        """Normalize pattern name for consistency."""
        # Remove common prefixes and suffixes
        name = name.strip()
        name = re.sub(r'\s+Pattern\s*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^The\s+', '', name, flags=re.IGNORECASE)
        
        # Convert to title case
        return ' '.join(word.capitalize() for word in name.split())
    
    def parse_pattern_file(self, file_path: Path) -> Optional[Pattern]:
        """Parse a single pattern file and extract metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            frontmatter = self.extract_frontmatter(content)
            relationships = self.extract_relationships(content)
            
            # Determine pattern name and category
            relative_path = file_path.relative_to(self.pattern_library_path)
            category = relative_path.parts[0] if len(relative_path.parts) > 1 else 'general'
            
            pattern_name = frontmatter.get('title', file_path.stem.replace('-', ' ').title())
            pattern_name = self.normalize_pattern_name(pattern_name)
            
            # Extract laws connections if present
            laws_connected = []
            if 'related_laws' in frontmatter:
                laws_data = frontmatter['related_laws']
                if isinstance(laws_data, dict):
                    if 'primary' in laws_data:
                        laws_connected.extend([f"Law {law.get('number', 'Unknown')}" for law in laws_data['primary']])
                    if 'secondary' in laws_data:
                        laws_connected.extend([f"Law {law.get('number', 'Unknown')}" for law in laws_data['secondary']])
            
            pattern = Pattern(
                name=pattern_name,
                title=frontmatter.get('title', pattern_name),
                description=frontmatter.get('description', ''),
                category=category,
                file_path=str(file_path),
                excellence_tier=frontmatter.get('excellence_tier'),
                pattern_status=frontmatter.get('pattern_status'),
                related_patterns=relationships['related_patterns'],
                references=relationships['references'],
                see_also=relationships['see_also'],
                laws_connected=laws_connected
            )
            
            self.categories.add(category)
            return pattern
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def build_dependency_graph(self):
        """Build the dependency graph from parsed patterns."""
        # Add all patterns as nodes
        for pattern in self.patterns.values():
            self.graph.add_node(pattern.name, **asdict(pattern))
        
        # Add edges for relationships
        for pattern in self.patterns.values():
            for related_pattern in pattern.related_patterns:
                related_name = self.normalize_pattern_name(related_pattern)
                if related_name in self.patterns:
                    self.graph.add_edge(pattern.name, related_name, 
                                      relationship_type='related')
            
            for see_also_pattern in pattern.see_also:
                see_also_name = self.normalize_pattern_name(see_also_pattern)
                if see_also_name in self.patterns:
                    self.graph.add_edge(pattern.name, see_also_name, 
                                      relationship_type='see_also')
    
    def analyze_patterns(self) -> Dict:
        """Analyze all patterns and build dependency graph."""
        print("🔍 Scanning pattern library...")
        pattern_files = self.find_pattern_files()
        print(f"Found {len(pattern_files)} pattern files")
        
        print("📖 Parsing pattern files...")
        for file_path in pattern_files:
            pattern = self.parse_pattern_file(file_path)
            if pattern:
                self.patterns[pattern.name] = pattern
        
        print(f"✅ Parsed {len(self.patterns)} patterns")
        
        print("🔗 Building dependency graph...")
        self.build_dependency_graph()
        print(f"📊 Graph has {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
        
        return self.generate_analysis()
    
    def generate_analysis(self) -> Dict:
        """Generate comprehensive analysis of pattern dependencies."""
        analysis = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_patterns': len(self.patterns),
                'total_relationships': self.graph.number_of_edges(),
                'categories': list(self.categories)
            },
            'graph_metrics': self.calculate_graph_metrics(),
            'pattern_statistics': self.calculate_pattern_statistics(),
            'category_analysis': self.analyze_categories(),
            'hub_patterns': self.identify_hub_patterns(),
            'isolated_patterns': self.identify_isolated_patterns(),
            'relationship_analysis': self.analyze_relationships(),
            'recommendations': self.generate_recommendations()
        }
        
        return analysis
    
    def calculate_graph_metrics(self) -> Dict:
        """Calculate graph-level metrics."""
        metrics = {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_connected': nx.is_weakly_connected(self.graph),
            'number_of_components': nx.number_weakly_connected_components(self.graph),
        }
        
        if self.graph.number_of_nodes() > 0:
            metrics['average_degree'] = sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes()
        
        return metrics
    
    def calculate_pattern_statistics(self) -> Dict:
        """Calculate statistics about individual patterns."""
        in_degrees = dict(self.graph.in_degree())
        out_degrees = dict(self.graph.out_degree())
        
        statistics = {
            'most_referenced': sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10],
            'most_referencing': sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:10],
            'degree_distribution': {
                'in_degree_stats': {
                    'mean': sum(in_degrees.values()) / len(in_degrees) if in_degrees else 0,
                    'max': max(in_degrees.values()) if in_degrees else 0,
                    'min': min(in_degrees.values()) if in_degrees else 0
                },
                'out_degree_stats': {
                    'mean': sum(out_degrees.values()) / len(out_degrees) if out_degrees else 0,
                    'max': max(out_degrees.values()) if out_degrees else 0,
                    'min': min(out_degrees.values()) if out_degrees else 0
                }
            }
        }
        
        return statistics
    
    def analyze_categories(self) -> Dict:
        """Analyze patterns by category."""
        category_stats = defaultdict(lambda: {
            'count': 0,
            'patterns': [],
            'internal_connections': 0,
            'external_connections': 0
        })
        
        for pattern in self.patterns.values():
            category_stats[pattern.category]['count'] += 1
            category_stats[pattern.category]['patterns'].append(pattern.name)
        
        # Calculate cross-category connections
        for edge in self.graph.edges():
            source_category = self.patterns[edge[0]].category
            target_category = self.patterns[edge[1]].category
            
            if source_category == target_category:
                category_stats[source_category]['internal_connections'] += 1
            else:
                category_stats[source_category]['external_connections'] += 1
        
        return dict(category_stats)
    
    def identify_hub_patterns(self, top_n: int = 10) -> List[Dict]:
        """Identify key hub patterns with high connectivity."""
        hubs = []
        
        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            out_degree = self.graph.out_degree(node)
            total_degree = in_degree + out_degree
            
            if total_degree > 0:
                hubs.append({
                    'name': node,
                    'category': self.patterns[node].category,
                    'in_degree': in_degree,
                    'out_degree': out_degree,
                    'total_degree': total_degree,
                    'hub_score': (in_degree * 2 + out_degree)  # Weight incoming connections more
                })
        
        return sorted(hubs, key=lambda x: x['hub_score'], reverse=True)[:top_n]
    
    def identify_isolated_patterns(self) -> List[Dict]:
        """Identify patterns with no connections."""
        isolated = []
        
        for node in self.graph.nodes():
            if self.graph.degree(node) == 0:
                pattern = self.patterns[node]
                isolated.append({
                    'name': node,
                    'category': pattern.category,
                    'file_path': pattern.file_path,
                    'description': pattern.description
                })
        
        return isolated
    
    def analyze_relationships(self) -> Dict:
        """Analyze relationship patterns and types."""
        relationship_types = defaultdict(int)
        
        for _, _, data in self.graph.edges(data=True):
            relationship_types[data.get('relationship_type', 'unknown')] += 1
        
        return {
            'relationship_type_distribution': dict(relationship_types),
            'bidirectional_relationships': self.find_bidirectional_relationships(),
            'cross_category_relationships': self.find_cross_category_relationships()
        }
    
    def find_bidirectional_relationships(self) -> List[Tuple[str, str]]:
        """Find bidirectional relationships between patterns."""
        bidirectional = []
        
        for edge in self.graph.edges():
            source, target = edge
            if self.graph.has_edge(target, source):
                if (target, source) not in bidirectional:
                    bidirectional.append((source, target))
        
        return bidirectional
    
    def find_cross_category_relationships(self) -> Dict[str, int]:
        """Find relationships that cross category boundaries."""
        cross_category = defaultdict(int)
        
        for edge in self.graph.edges():
            source_category = self.patterns[edge[0]].category
            target_category = self.patterns[edge[1]].category
            
            if source_category != target_category:
                key = f"{source_category} → {target_category}"
                cross_category[key] += 1
        
        return dict(cross_category)
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        isolated_count = len(self.identify_isolated_patterns())
        if isolated_count > 0:
            recommendations.append(
                f"Consider reviewing {isolated_count} isolated patterns for potential relationships"
            )
        
        # Check for categories with low internal connectivity
        category_analysis = self.analyze_categories()
        for category, stats in category_analysis.items():
            if stats['count'] > 3 and stats['internal_connections'] == 0:
                recommendations.append(
                    f"Category '{category}' has no internal pattern relationships - consider adding cross-references"
                )
        
        # Check for unbalanced hub patterns
        hubs = self.identify_hub_patterns(5)
        if hubs and hubs[0]['in_degree'] > 10:
            recommendations.append(
                f"Pattern '{hubs[0]['name']}' is heavily referenced - ensure documentation quality is high"
            )
        
        return recommendations
    
    def export_json(self, output_path: str):
        """Export analysis results as JSON."""
        analysis = self.generate_analysis()
        
        # Convert graph to serializable format
        graph_data = {
            'nodes': [
                {
                    'id': node,
                    **self.graph.nodes[node]
                } for node in self.graph.nodes()
            ],
            'edges': [
                {
                    'source': edge[0],
                    'target': edge[1],
                    **self.graph.edges[edge]
                } for edge in self.graph.edges()
            ]
        }
        
        export_data = {
            'analysis': analysis,
            'graph': graph_data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON export saved to {output_path}")
    
    def export_graphml(self, output_path: str):
        """Export dependency graph as GraphML."""
        # Create a clean graph for GraphML export (no None values)
        clean_graph = nx.DiGraph()
        
        for node in self.graph.nodes():
            node_data = {}
            for key, value in self.graph.nodes[node].items():
                if value is not None:
                    if isinstance(value, (list, dict)):
                        node_data[key] = str(value)
                    else:
                        node_data[key] = str(value)
            clean_graph.add_node(node, **node_data)
        
        for source, target, data in self.graph.edges(data=True):
            edge_data = {}
            for key, value in data.items():
                if value is not None:
                    edge_data[key] = str(value)
            clean_graph.add_edge(source, target, **edge_data)
        
        nx.write_graphml(clean_graph, output_path)
        print(f"🔗 GraphML export saved to {output_path}")
    
    def create_summary_report(self, output_path: str):
        """Create a comprehensive summary report."""
        analysis = self.generate_analysis()
        
        report = f"""# Pattern Dependency Analysis Report

Generated: {analysis['metadata']['generated_at']}

## Executive Summary

The pattern library contains **{analysis['metadata']['total_patterns']} patterns** across **{len(analysis['metadata']['categories'])} categories** with **{analysis['metadata']['total_relationships']} documented relationships**.

## Graph Metrics

- **Nodes**: {analysis['graph_metrics']['nodes']}
- **Edges**: {analysis['graph_metrics']['edges']}
- **Density**: {analysis['graph_metrics']['density']:.3f}
- **Connected**: {analysis['graph_metrics']['is_connected']}
- **Components**: {analysis['graph_metrics']['number_of_components']}
- **Average Degree**: {analysis['graph_metrics'].get('average_degree', 0):.2f}

## Top Hub Patterns

These patterns are most connected in the ecosystem:

"""
        
        for i, hub in enumerate(analysis['hub_patterns'][:5], 1):
            report += f"{i}. **{hub['name']}** ({hub['category']})\n"
            report += f"   - Referenced by {hub['in_degree']} patterns\n"
            report += f"   - References {hub['out_degree']} patterns\n"
            report += f"   - Hub Score: {hub['hub_score']}\n\n"
        
        report += "## Most Referenced Patterns\n\n"
        for pattern, count in analysis['pattern_statistics']['most_referenced'][:5]:
            report += f"- **{pattern}**: {count} references\n"
        
        report += "\n## Category Distribution\n\n"
        for category, stats in analysis['category_analysis'].items():
            report += f"- **{category}**: {stats['count']} patterns\n"
            report += f"  - Internal connections: {stats['internal_connections']}\n"
            report += f"  - External connections: {stats['external_connections']}\n"
        
        if analysis['isolated_patterns']:
            report += f"\n## Isolated Patterns ({len(analysis['isolated_patterns'])})\n\n"
            report += "These patterns have no documented relationships:\n\n"
            for pattern in analysis['isolated_patterns']:
                report += f"- **{pattern['name']}** ({pattern['category']})\n"
        
        report += "\n## Cross-Category Relationships\n\n"
        for relationship, count in list(analysis['relationship_analysis']['cross_category_relationships'].items())[:10]:
            report += f"- {relationship}: {count} relationships\n"
        
        if analysis['recommendations']:
            report += "\n## Recommendations\n\n"
            for i, rec in enumerate(analysis['recommendations'], 1):
                report += f"{i}. {rec}\n"
        
        report += f"\n## Relationship Type Distribution\n\n"
        for rel_type, count in analysis['relationship_analysis']['relationship_type_distribution'].items():
            report += f"- **{rel_type}**: {count}\n"
        
        bidirectional = analysis['relationship_analysis']['bidirectional_relationships']
        if bidirectional:
            report += f"\n## Bidirectional Relationships ({len(bidirectional)})\n\n"
            for source, target in bidirectional[:10]:
                report += f"- {source} ↔ {target}\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📋 Summary report saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Analyze pattern dependencies in the pattern library')
    parser.add_argument('--library-path', 
                       default='/home/deepak/DStudio/docs/pattern-library',
                       help='Path to pattern library directory')
    parser.add_argument('--output-dir', 
                       default='/home/deepak/DStudio/scripts',
                       help='Output directory for generated files')
    parser.add_argument('--json-output', 
                       default='pattern_dependency_analysis.json',
                       help='JSON output filename')
    parser.add_argument('--graphml-output', 
                       default='pattern_dependency_graph.graphml',
                       help='GraphML output filename')
    parser.add_argument('--report-output', 
                       default='pattern_dependency_report.md',
                       help='Summary report filename')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Starting Pattern Dependency Analysis...")
    
    try:
        analyzer = PatternDependencyAnalyzer(args.library_path)
        analysis = analyzer.analyze_patterns()
        
        # Generate outputs
        json_path = output_dir / args.json_output
        graphml_path = output_dir / args.graphml_output
        report_path = output_dir / args.report_output
        
        analyzer.export_json(str(json_path))
        analyzer.export_graphml(str(graphml_path))
        analyzer.create_summary_report(str(report_path))
        
        print("\n✅ Analysis complete!")
        print(f"📊 Found {analysis['metadata']['total_patterns']} patterns with {analysis['metadata']['total_relationships']} relationships")
        print(f"🏆 Top hub pattern: {analysis['hub_patterns'][0]['name']}" if analysis['hub_patterns'] else "🏆 No hub patterns found")
        print(f"🏝️  Isolated patterns: {len(analysis['isolated_patterns'])}")
        
        if analysis['recommendations']:
            print("\n💡 Recommendations:")
            for rec in analysis['recommendations'][:3]:
                print(f"   • {rec}")
    
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
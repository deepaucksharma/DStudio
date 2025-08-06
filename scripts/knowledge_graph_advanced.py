#!/usr/bin/env python3
"""
Advanced Knowledge Graph with LLM-Optimized Analysis
=====================================================

This creates a sophisticated knowledge graph system optimized for LLM analysis:
- SQLite database for efficient querying
- Natural language query interface
- Semantic embeddings for concept similarity
- Graph algorithms for deep insights
- Interactive visualizations
"""

import os
import re
import json
import sqlite3
import pickle
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
import networkx as nx
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class KnowledgeGraphDB:
    """SQLite-based knowledge graph optimized for LLM analysis"""
    
    def __init__(self, db_path: str = "knowledge_graph.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_schema()
        self.graph = nx.DiGraph()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.concept_embeddings = None
        
    def create_schema(self):
        """Create optimized database schema"""
        cursor = self.conn.cursor()
        
        # Pages table with full-text search
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                tier TEXT,
                content TEXT,
                word_count INTEGER,
                last_modified TEXT,
                hash TEXT,
                frontmatter TEXT,
                pagerank REAL DEFAULT 0,
                importance_score REAL DEFAULT 0,
                embedding BLOB
            )
        ''')
        
        # Create FTS5 virtual table for full-text search
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                path, title, description, content,
                content=pages
            )
        ''')
        
        # Links table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL,
                target_path TEXT NOT NULL,
                link_type TEXT NOT NULL,
                anchor TEXT,
                context TEXT,
                FOREIGN KEY (source_path) REFERENCES pages(path),
                FOREIGN KEY (target_path) REFERENCES pages(path),
                UNIQUE(source_path, target_path, link_type)
            )
        ''')
        
        # Concepts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept TEXT UNIQUE NOT NULL,
                category TEXT,
                frequency INTEGER DEFAULT 0,
                tfidf_score REAL DEFAULT 0,
                embedding BLOB
            )
        ''')
        
        # Page-Concept relationships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page_concepts (
                page_path TEXT NOT NULL,
                concept TEXT NOT NULL,
                relevance_score REAL DEFAULT 1.0,
                FOREIGN KEY (page_path) REFERENCES pages(path),
                FOREIGN KEY (concept) REFERENCES concepts(concept),
                PRIMARY KEY (page_path, concept)
            )
        ''')
        
        # Headings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS headings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_path TEXT NOT NULL,
                level INTEGER NOT NULL,
                text TEXT NOT NULL,
                anchor TEXT,
                position INTEGER,
                FOREIGN KEY (page_path) REFERENCES pages(path)
            )
        ''')
        
        # Navigation structure
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS navigation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_path TEXT,
                child_path TEXT NOT NULL,
                position INTEGER,
                nav_title TEXT,
                FOREIGN KEY (parent_path) REFERENCES pages(path),
                FOREIGN KEY (child_path) REFERENCES pages(path)
            )
        ''')
        
        # Issues table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_type TEXT NOT NULL,
                source_path TEXT,
                target_path TEXT,
                description TEXT,
                severity TEXT DEFAULT 'warning',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Metrics table for tracking changes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                metadata TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_concepts_page ON page_concepts(page_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_concepts_concept ON page_concepts(concept)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_headings_page ON headings(page_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_navigation_parent ON navigation(parent_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_issues_type ON issues(issue_type)')
        
        self.conn.commit()
    
    def natural_language_query(self, query: str) -> Dict[str, Any]:
        """
        Process natural language queries about the knowledge graph
        
        Examples:
        - "What are the most important pages about circuit breaker?"
        - "Show me all broken links"
        - "Which pages link to CAP theorem?"
        - "Find orphaned pages in pattern-library"
        """
        query_lower = query.lower()
        results = {'query': query, 'interpretation': '', 'data': []}
        
        # Pattern matching for different query types
        if 'broken' in query_lower and 'link' in query_lower:
            results['interpretation'] = 'Finding broken links'
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT source_path, target_path, description 
                FROM issues 
                WHERE issue_type = 'broken_link'
                ORDER BY source_path
            ''')
            results['data'] = [dict(row) for row in cursor.fetchall()]
            
        elif 'orphaned' in query_lower:
            results['interpretation'] = 'Finding orphaned pages'
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT path, title, category 
                FROM pages p
                WHERE NOT EXISTS (
                    SELECT 1 FROM links WHERE target_path = p.path
                ) AND NOT EXISTS (
                    SELECT 1 FROM navigation WHERE child_path = p.path
                ) AND path != 'index.md'
            ''')
            results['data'] = [dict(row) for row in cursor.fetchall()]
            
        elif 'important' in query_lower or 'top' in query_lower:
            # Extract topic if mentioned
            topic = self._extract_topic(query_lower)
            results['interpretation'] = f'Finding most important pages{" about " + topic if topic else ""}'
            
            cursor = self.conn.cursor()
            if topic:
                cursor.execute('''
                    SELECT p.path, p.title, p.pagerank, p.importance_score
                    FROM pages p
                    JOIN pages_fts ON pages_fts.path = p.path
                    WHERE pages_fts MATCH ?
                    ORDER BY p.importance_score DESC
                    LIMIT 10
                ''', (topic,))
            else:
                cursor.execute('''
                    SELECT path, title, pagerank, importance_score
                    FROM pages
                    ORDER BY importance_score DESC
                    LIMIT 10
                ''')
            results['data'] = [dict(row) for row in cursor.fetchall()]
            
        elif 'link to' in query_lower or 'links to' in query_lower:
            # Extract target page
            match = re.search(r'links? to (.+)', query_lower)
            if match:
                target = match.group(1).strip()
                results['interpretation'] = f'Finding pages that link to {target}'
                
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT DISTINCT l.source_path, p.title
                    FROM links l
                    JOIN pages p ON p.path = l.source_path
                    WHERE l.target_path LIKE ? OR p.title LIKE ?
                ''', (f'%{target}%', f'%{target}%'))
                results['data'] = [dict(row) for row in cursor.fetchall()]
                
        elif 'concept' in query_lower or 'about' in query_lower:
            # Find pages about a concept
            topic = self._extract_topic(query_lower)
            if topic:
                results['interpretation'] = f'Finding pages about {topic}'
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT p.path, p.title, pc.relevance_score
                    FROM page_concepts pc
                    JOIN pages p ON p.path = pc.page_path
                    WHERE pc.concept LIKE ?
                    ORDER BY pc.relevance_score DESC
                    LIMIT 15
                ''', (f'%{topic}%',))
                results['data'] = [dict(row) for row in cursor.fetchall()]
                
        elif 'pattern' in query_lower:
            # Pattern-specific queries
            if 'gold' in query_lower:
                tier = 'gold'
            elif 'silver' in query_lower:
                tier = 'silver'
            elif 'bronze' in query_lower:
                tier = 'bronze'
            else:
                tier = None
                
            results['interpretation'] = f'Finding {tier + " " if tier else ""}patterns'
            cursor = self.conn.cursor()
            
            if tier:
                cursor.execute('''
                    SELECT path, title, tier, importance_score
                    FROM pages
                    WHERE tier = ? AND category LIKE '%pattern%'
                    ORDER BY importance_score DESC
                ''', (tier,))
            else:
                cursor.execute('''
                    SELECT path, title, tier, importance_score
                    FROM pages
                    WHERE category LIKE '%pattern%'
                    ORDER BY importance_score DESC
                    LIMIT 20
                ''')
            results['data'] = [dict(row) for row in cursor.fetchall()]
            
        elif 'similar to' in query_lower:
            # Find similar pages
            match = re.search(r'similar to (.+)', query_lower)
            if match:
                page_ref = match.group(1).strip()
                results['interpretation'] = f'Finding pages similar to {page_ref}'
                similar = self.find_similar_pages(page_ref, limit=10)
                results['data'] = similar
                
        else:
            # Default: full-text search
            results['interpretation'] = f'Searching for: {query}'
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT p.path, p.title, p.description,
                       snippet(pages_fts, 3, '<b>', '</b>', '...', 32) as snippet
                FROM pages p
                JOIN pages_fts ON pages_fts.path = p.path
                WHERE pages_fts MATCH ?
                ORDER BY rank
                LIMIT 20
            ''', (query,))
            results['data'] = [dict(row) for row in cursor.fetchall()]
        
        return results
    
    def _extract_topic(self, query: str) -> Optional[str]:
        """Extract topic from query"""
        # Remove common words
        stop_words = {'what', 'are', 'the', 'most', 'important', 'pages', 'about',
                     'show', 'me', 'all', 'find', 'which', 'that', 'with', 'in'}
        words = query.split()
        topic_words = [w for w in words if w not in stop_words]
        return ' '.join(topic_words) if topic_words else None
    
    def find_similar_pages(self, page_path: str, limit: int = 5) -> List[Dict]:
        """Find pages similar to a given page using TF-IDF"""
        cursor = self.conn.cursor()
        
        # Get all page contents
        cursor.execute('SELECT path, content FROM pages WHERE content IS NOT NULL')
        pages = cursor.fetchall()
        
        if not pages:
            return []
        
        paths = [p['path'] for p in pages]
        contents = [p['content'] for p in pages]
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(contents)
        
        # Find index of target page
        try:
            target_idx = paths.index(page_path)
        except ValueError:
            # Try partial match
            target_idx = None
            for i, p in enumerate(paths):
                if page_path in p or p in page_path:
                    target_idx = i
                    break
            if target_idx is None:
                return []
        
        # Calculate similarities
        similarities = cosine_similarity(tfidf_matrix[target_idx:target_idx+1], tfidf_matrix).flatten()
        
        # Get top similar pages (excluding the page itself)
        similar_indices = similarities.argsort()[-limit-1:-1][::-1]
        
        results = []
        for idx in similar_indices:
            if idx != target_idx:
                cursor.execute('SELECT path, title FROM pages WHERE path = ?', (paths[idx],))
                page = cursor.fetchone()
                if page:
                    results.append({
                        'path': page['path'],
                        'title': page['title'],
                        'similarity': float(similarities[idx])
                    })
        
        return results
    
    def analyze_information_architecture(self) -> Dict[str, Any]:
        """Analyze the information architecture quality"""
        cursor = self.conn.cursor()
        
        analysis = {
            'hierarchy': {},
            'navigation': {},
            'content': {},
            'issues': {},
            'recommendations': []
        }
        
        # Analyze hierarchy depth
        cursor.execute('''
            SELECT 
                LENGTH(path) - LENGTH(REPLACE(path, '/', '')) as depth,
                COUNT(*) as count
            FROM pages
            GROUP BY depth
            ORDER BY depth
        ''')
        analysis['hierarchy']['depth_distribution'] = [dict(row) for row in cursor.fetchall()]
        
        # Analyze navigation coverage
        cursor.execute('''
            SELECT 
                (SELECT COUNT(*) FROM pages) as total_pages,
                (SELECT COUNT(DISTINCT child_path) FROM navigation) as pages_in_nav,
                (SELECT COUNT(*) FROM pages WHERE path NOT IN (SELECT child_path FROM navigation)) as pages_not_in_nav
        ''')
        nav_stats = cursor.fetchone()
        analysis['navigation'] = dict(nav_stats)
        
        # Analyze content distribution
        cursor.execute('''
            SELECT 
                category,
                COUNT(*) as page_count,
                AVG(word_count) as avg_words,
                SUM(word_count) as total_words
            FROM pages
            GROUP BY category
            ORDER BY page_count DESC
        ''')
        analysis['content']['by_category'] = [dict(row) for row in cursor.fetchall()]
        
        # Analyze link health
        cursor.execute('''
            SELECT 
                issue_type,
                COUNT(*) as count,
                severity
            FROM issues
            GROUP BY issue_type, severity
        ''')
        analysis['issues']['by_type'] = [dict(row) for row in cursor.fetchall()]
        
        # Generate recommendations
        recommendations = []
        
        # Check for navigation coverage
        nav_coverage = nav_stats['pages_in_nav'] / nav_stats['total_pages'] if nav_stats['total_pages'] > 0 else 0
        if nav_coverage < 0.8:
            recommendations.append({
                'priority': 'high',
                'issue': 'Low navigation coverage',
                'detail': f'Only {nav_coverage:.1%} of pages are in navigation',
                'action': 'Add missing pages to mkdocs.yml navigation'
            })
        
        # Check for orphaned pages
        cursor.execute('SELECT COUNT(*) as count FROM issues WHERE issue_type = "orphaned_page"')
        orphan_count = cursor.fetchone()['count']
        if orphan_count > 0:
            recommendations.append({
                'priority': 'medium',
                'issue': f'{orphan_count} orphaned pages',
                'detail': 'Pages not linked from anywhere',
                'action': 'Link these pages or add to navigation'
            })
        
        # Check for broken links
        cursor.execute('SELECT COUNT(*) as count FROM issues WHERE issue_type = "broken_link"')
        broken_count = cursor.fetchone()['count']
        if broken_count > 0:
            recommendations.append({
                'priority': 'high',
                'issue': f'{broken_count} broken links',
                'detail': 'Links pointing to non-existent pages',
                'action': 'Fix or remove broken links'
            })
        
        # Check hierarchy balance
        max_depth = max([d['depth'] for d in analysis['hierarchy']['depth_distribution']])
        if max_depth > 4:
            recommendations.append({
                'priority': 'low',
                'issue': 'Deep hierarchy',
                'detail': f'Maximum depth is {max_depth} levels',
                'action': 'Consider flattening deeply nested sections'
            })
        
        analysis['recommendations'] = recommendations
        
        return analysis
    
    def export_for_llm_analysis(self, output_file: str = "llm_knowledge_graph.json") -> Dict:
        """Export graph in LLM-friendly format with semantic context"""
        cursor = self.conn.cursor()
        
        export_data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'version': '2.0',
                'purpose': 'LLM-optimized knowledge graph for distributed systems documentation'
            },
            'semantic_structure': {},
            'concept_map': {},
            'navigation_tree': {},
            'query_examples': [],
            'analysis_prompts': []
        }
        
        # Build semantic structure
        cursor.execute('''
            SELECT 
                p.path, p.title, p.description, p.category, p.tier,
                p.word_count, p.importance_score,
                GROUP_CONCAT(DISTINCT pc.concept) as concepts,
                GROUP_CONCAT(DISTINCT l.target_path) as outgoing_links,
                (SELECT GROUP_CONCAT(source_path) FROM links WHERE target_path = p.path) as incoming_links
            FROM pages p
            LEFT JOIN page_concepts pc ON pc.page_path = p.path
            LEFT JOIN links l ON l.source_path = p.path
            GROUP BY p.path
            ORDER BY p.importance_score DESC
        ''')
        
        semantic_pages = {}
        for row in cursor.fetchall():
            page_data = dict(row)
            page_data['concepts'] = page_data['concepts'].split(',') if page_data['concepts'] else []
            page_data['outgoing_links'] = page_data['outgoing_links'].split(',') if page_data['outgoing_links'] else []
            page_data['incoming_links'] = page_data['incoming_links'].split(',') if page_data['incoming_links'] else []
            semantic_pages[page_data['path']] = page_data
        
        export_data['semantic_structure'] = semantic_pages
        
        # Build concept map with relationships
        cursor.execute('''
            SELECT 
                c.concept,
                c.category,
                c.frequency,
                GROUP_CONCAT(pc.page_path) as pages
            FROM concepts c
            LEFT JOIN page_concepts pc ON pc.concept = c.concept
            WHERE c.frequency > 1
            GROUP BY c.concept
            ORDER BY c.frequency DESC
            LIMIT 100
        ''')
        
        concept_map = {}
        for row in cursor.fetchall():
            concept_data = dict(row)
            concept_data['pages'] = concept_data['pages'].split(',') if concept_data['pages'] else []
            concept_map[concept_data['concept']] = concept_data
        
        export_data['concept_map'] = concept_map
        
        # Build navigation tree
        def build_nav_tree(parent_path=None):
            cursor.execute('''
                SELECT child_path, nav_title, position
                FROM navigation
                WHERE parent_path IS ? OR parent_path = ?
                ORDER BY position
            ''', (parent_path, parent_path))
            
            children = []
            for row in cursor.fetchall():
                child = dict(row)
                child['children'] = build_nav_tree(child['child_path'])
                children.append(child)
            return children
        
        export_data['navigation_tree'] = build_nav_tree()
        
        # Add query examples for LLM
        export_data['query_examples'] = [
            {
                'intent': 'find_pattern',
                'example': 'What patterns should I use for handling distributed transactions?',
                'relevant_paths': ['pattern-library/data-management/saga.md', 'pattern-library/coordination/two-phase-commit.md']
            },
            {
                'intent': 'explain_concept',
                'example': 'Explain the CAP theorem and its implications',
                'relevant_paths': ['core-principles/laws/cap-theorem.md', 'architects-handbook/quantitative-analysis/cap-theorem.md']
            },
            {
                'intent': 'compare_solutions',
                'example': 'Compare different caching strategies',
                'relevant_paths': ['pattern-library/scaling/caching-strategies.md', 'architects-handbook/case-studies/databases/redis-architecture.md']
            }
        ]
        
        # Add analysis prompts
        export_data['analysis_prompts'] = [
            "Identify the most critical patterns for building resilient systems",
            "Map the learning progression from beginner to expert",
            "Find gaps in documentation coverage",
            "Suggest optimal reading paths for different roles",
            "Identify conceptual dependencies between topics"
        ]
        
        # Calculate statistics
        export_data['statistics'] = {
            'total_pages': len(semantic_pages),
            'total_concepts': len(concept_map),
            'total_links': sum(len(p['outgoing_links']) for p in semantic_pages.values()),
            'avg_page_connections': np.mean([len(p['outgoing_links']) + len(p['incoming_links']) for p in semantic_pages.values()]),
            'most_connected_pages': sorted(semantic_pages.items(), 
                                         key=lambda x: len(x[1]['incoming_links']), 
                                         reverse=True)[:10]
        }
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return export_data
    
    def generate_llm_analysis_prompt(self, focus_area: str = None) -> str:
        """Generate a comprehensive prompt for LLM analysis"""
        cursor = self.conn.cursor()
        
        # Get summary statistics
        cursor.execute('SELECT COUNT(*) as count FROM pages')
        page_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM links')
        link_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM concepts')
        concept_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM issues')
        issue_count = cursor.fetchone()['count']
        
        prompt = f"""
You are analyzing a knowledge graph of distributed systems documentation with the following characteristics:

GRAPH STRUCTURE:
- Total Pages: {page_count}
- Total Links: {link_count}
- Unique Concepts: {concept_count}
- Identified Issues: {issue_count}

KEY SECTIONS:
"""
        
        # Add category breakdown
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM pages
            GROUP BY category
            ORDER BY count DESC
            LIMIT 10
        ''')
        for row in cursor.fetchall():
            prompt += f"- {row['category']}: {row['count']} pages\n"
        
        if focus_area:
            prompt += f"\n\nFOCUS AREA: {focus_area}\n"
            
            # Add specific data for focus area
            cursor.execute('''
                SELECT path, title, importance_score
                FROM pages
                WHERE category = ? OR path LIKE ?
                ORDER BY importance_score DESC
                LIMIT 5
            ''', (focus_area, f'%{focus_area}%'))
            
            prompt += "\nTop pages in focus area:\n"
            for row in cursor.fetchall():
                prompt += f"- {row['title']} (importance: {row['importance_score']:.3f})\n"
        
        prompt += """

ANALYSIS TASKS:
1. Identify the most critical learning paths through this content
2. Find conceptual gaps or missing connections
3. Suggest improvements to the information architecture
4. Identify the most important cross-references that should exist
5. Recommend the optimal sequence for learning these concepts

Please provide specific, actionable insights based on the graph structure.
"""
        
        return prompt
    
    def close(self):
        """Close database connection"""
        self.conn.close()


class AdvancedGraphAnalyzer:
    """Advanced graph analysis using NetworkX algorithms"""
    
    def __init__(self, db: KnowledgeGraphDB):
        self.db = db
        self.graph = nx.DiGraph()
        self._build_networkx_graph()
    
    def _build_networkx_graph(self):
        """Build NetworkX graph from database"""
        cursor = self.db.conn.cursor()
        
        # Add nodes
        cursor.execute('SELECT path, title, category, importance_score FROM pages')
        for row in cursor.fetchall():
            self.graph.add_node(row['path'], 
                              title=row['title'],
                              category=row['category'],
                              importance=row['importance_score'])
        
        # Add edges
        cursor.execute('SELECT source_path, target_path, link_type FROM links')
        for row in cursor.fetchall():
            self.graph.add_edge(row['source_path'], row['target_path'], 
                               type=row['link_type'])
    
    def find_critical_paths(self) -> List[List[str]]:
        """Find critical paths in the documentation"""
        # Find paths from entry points to important destinations
        entry_points = ['index.md', 'start-here/index.md', 'core-principles/index.md']
        important_pages = sorted(self.graph.nodes(), 
                                key=lambda x: self.graph.nodes[x].get('importance', 0),
                                reverse=True)[:10]
        
        critical_paths = []
        for start in entry_points:
            if start not in self.graph:
                continue
            for end in important_pages:
                if end != start and end in self.graph:
                    try:
                        path = nx.shortest_path(self.graph, start, end)
                        if len(path) > 2:  # Non-trivial paths
                            critical_paths.append(path)
                    except nx.NetworkXNoPath:
                        pass
        
        return critical_paths[:20]  # Top 20 paths
    
    def detect_communities(self) -> List[Set[str]]:
        """Detect communities in the documentation"""
        # Convert to undirected for community detection
        undirected = self.graph.to_undirected()
        
        # Use Louvain method for community detection
        import community as community_louvain
        partition = community_louvain.best_partition(undirected)
        
        # Group nodes by community
        communities = defaultdict(set)
        for node, comm_id in partition.items():
            communities[comm_id].add(node)
        
        # Return sorted by size
        return sorted(communities.values(), key=len, reverse=True)
    
    def calculate_centrality_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate various centrality metrics"""
        metrics = {
            'pagerank': nx.pagerank(self.graph),
            'betweenness': nx.betweenness_centrality(self.graph),
            'closeness': nx.closeness_centrality(self.graph),
            'degree': nx.degree_centrality(self.graph)
        }
        
        # Store in database
        cursor = self.db.conn.cursor()
        for metric_name, values in metrics.items():
            for page, score in values.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO metrics (metric_name, metric_value, metadata)
                    VALUES (?, ?, ?)
                ''', (f'{metric_name}_{page}', score, json.dumps({'page': page, 'type': metric_name})))
        
        self.db.conn.commit()
        return metrics
    
    def find_knowledge_gaps(self) -> List[Dict]:
        """Identify potential gaps in documentation"""
        gaps = []
        
        # Find weakly connected components
        if len(self.graph) > 0:
            components = list(nx.weakly_connected_components(self.graph))
            if len(components) > 1:
                # Multiple disconnected components indicate gaps
                for i, comp in enumerate(components[1:], 1):  # Skip largest
                    gaps.append({
                        'type': 'disconnected_component',
                        'size': len(comp),
                        'sample_pages': list(comp)[:5]
                    })
        
        # Find pages with high out-degree but low in-degree (potentially underlinked)
        for node in self.graph.nodes():
            out_degree = self.graph.out_degree(node)
            in_degree = self.graph.in_degree(node)
            
            if out_degree > 5 and in_degree < 2:
                gaps.append({
                    'type': 'underlinked_hub',
                    'page': node,
                    'out_links': out_degree,
                    'in_links': in_degree
                })
        
        return gaps

def main():
    """Main execution with advanced features"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced knowledge graph builder')
    parser.add_argument('--mode', choices=['build', 'query', 'analyze', 'export'], 
                       default='build', help='Operation mode')
    parser.add_argument('--query', type=str, help='Natural language query')
    parser.add_argument('--focus', type=str, help='Focus area for analysis')
    parser.add_argument('--db', default='knowledge_graph.db', help='Database path')
    
    args = parser.parse_args()
    
    if args.mode == 'build':
        # First run the basic builder to get data
        from knowledge_graph_builder import KnowledgeGraphBuilder
        
        print("Building knowledge graph...")
        builder = KnowledgeGraphBuilder()
        builder.build()
        
        # Now populate the database
        print("Populating advanced database...")
        db = KnowledgeGraphDB(args.db)
        
        # Import pages
        for path, page in builder.pages.items():
            cursor = db.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO pages 
                (path, title, description, category, tier, word_count, last_modified, hash, frontmatter)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (path, page.title, page.description, page.category, page.tier,
                 page.word_count, page.last_modified, page.hash, json.dumps(page.frontmatter)))
            
            # Add concepts
            for concept in page.concepts:
                cursor.execute('INSERT OR IGNORE INTO concepts (concept) VALUES (?)', (concept,))
                cursor.execute('''
                    INSERT OR REPLACE INTO page_concepts (page_path, concept)
                    VALUES (?, ?)
                ''', (path, concept))
            
            # Add links
            for link in page.internal_links:
                target = link.split('#')[0]
                anchor = link.split('#')[1] if '#' in link else None
                cursor.execute('''
                    INSERT OR IGNORE INTO links (source_path, target_path, link_type, anchor)
                    VALUES (?, ?, ?, ?)
                ''', (path, target, 'internal', anchor))
        
        # Add issues
        for issue in builder.broken_links:
            cursor = db.conn.cursor()
            cursor.execute('''
                INSERT INTO issues (issue_type, source_path, target_path, description)
                VALUES (?, ?, ?, ?)
            ''', ('broken_link', issue['source'], issue['target'], f"Broken {issue['type']} link"))
        
        for page in builder.orphaned_pages:
            cursor = db.conn.cursor()
            cursor.execute('''
                INSERT INTO issues (issue_type, source_path, description)
                VALUES (?, ?, ?)
            ''', ('orphaned_page', page, "Page not in navigation and not linked"))
        
        db.conn.commit()
        
        # Run advanced analysis
        analyzer = AdvancedGraphAnalyzer(db)
        metrics = analyzer.calculate_centrality_metrics()
        
        # Update importance scores
        for page in builder.pages:
            importance = (
                metrics['pagerank'].get(page, 0) * 0.4 +
                metrics['betweenness'].get(page, 0) * 0.3 +
                metrics['closeness'].get(page, 0) * 0.2 +
                metrics['degree'].get(page, 0) * 0.1
            )
            cursor = db.conn.cursor()
            cursor.execute('''
                UPDATE pages SET importance_score = ?, pagerank = ?
                WHERE path = ?
            ''', (importance, metrics['pagerank'].get(page, 0), page))
        
        db.conn.commit()
        
        print("Knowledge graph built and stored in database")
        print(f"Database: {args.db}")
        
        # Export for LLM
        export_data = db.export_for_llm_analysis()
        print(f"LLM-optimized export saved to: llm_knowledge_graph.json")
        
        # Print analysis
        architecture = db.analyze_information_architecture()
        print("\n=== Information Architecture Analysis ===")
        print(f"Total pages: {architecture['navigation']['total_pages']}")
        print(f"Pages in navigation: {architecture['navigation']['pages_in_nav']}")
        print(f"Orphaned pages: {architecture['navigation']['pages_not_in_nav']}")
        
        print("\n=== Recommendations ===")
        for rec in architecture['recommendations']:
            print(f"[{rec['priority'].upper()}] {rec['issue']}")
            print(f"  → {rec['action']}")
        
        db.close()
        
    elif args.mode == 'query':
        if not args.query:
            print("Please provide a query with --query")
            return
        
        db = KnowledgeGraphDB(args.db)
        results = db.natural_language_query(args.query)
        
        print(f"\nQuery: {results['query']}")
        print(f"Interpretation: {results['interpretation']}")
        print(f"Results: {len(results['data'])} items found\n")
        
        for item in results['data'][:10]:
            print(f"  • {item}")
        
        db.close()
        
    elif args.mode == 'analyze':
        db = KnowledgeGraphDB(args.db)
        analyzer = AdvancedGraphAnalyzer(db)
        
        print("\n=== Critical Paths ===")
        paths = analyzer.find_critical_paths()
        for i, path in enumerate(paths[:5], 1):
            print(f"{i}. {' → '.join(path)}")
        
        print("\n=== Knowledge Gaps ===")
        gaps = analyzer.find_knowledge_gaps()
        for gap in gaps[:5]:
            print(f"  • {gap['type']}: {gap}")
        
        print("\n=== LLM Analysis Prompt ===")
        prompt = db.generate_llm_analysis_prompt(args.focus)
        print(prompt)
        
        db.close()
        
    elif args.mode == 'export':
        db = KnowledgeGraphDB(args.db)
        export_data = db.export_for_llm_analysis()
        print(f"Exported {len(export_data['semantic_structure'])} pages")
        print(f"Exported {len(export_data['concept_map'])} concepts")
        print("Saved to: llm_knowledge_graph.json")
        db.close()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Interactive troubleshooting dashboard for knowledge graph issues
"""

import sqlite3
import networkx as nx
import json
from collections import defaultdict, Counter
from pathlib import Path
import matplotlib.pyplot as plt

class KnowledgeGraphTroubleshooter:
    def __init__(self, db_path="knowledge_graph_ultimate.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.G = None
        
    def load_graph(self):
        """Load the full graph into NetworkX"""
        self.G = nx.DiGraph()
        
        # Load nodes
        self.cursor.execute("SELECT * FROM pages")
        for page in self.cursor.fetchall():
            self.G.add_node(page['page_id'], **dict(page))
        
        # Load edges
        self.cursor.execute("""
            SELECT src_page, dst_page, is_valid, is_external
            FROM links
            WHERE is_external = 0 AND dst_page IS NOT NULL
        """)
        
        for link in self.cursor.fetchall():
            if link['src_page'] in self.G and link['dst_page'] in self.G:
                self.G.add_edge(link['src_page'], link['dst_page'], 
                              is_valid=link['is_valid'])
        
        return self.G
    
    def diagnose_broken_links(self):
        """Detailed diagnosis of broken links"""
        
        # Get all broken links
        self.cursor.execute("""
            SELECT src_page, dst_page, dst_url
            FROM links
            WHERE is_valid = 0 AND is_external = 0
        """)
        
        broken_links = self.cursor.fetchall()
        
        # Categorize by type of issue
        issues = {
            'non_existent_pages': [],
            'path_mismatch': [],
            'incorrect_relative': [],
            'missing_index': [],
            'double_slash': [],
            'anchor_issues': []
        }
        
        # Get all existing pages
        self.cursor.execute("SELECT page_id FROM pages")
        existing_pages = set(row[0] for row in self.cursor.fetchall())
        
        for link in broken_links:
            dst = link['dst_page'] or ''
            url = link['dst_url'] or ''
            
            # Check if destination doesn't exist
            if dst and dst not in existing_pages:
                # Check for common patterns
                if dst.endswith('/index'):
                    # Check if parent exists
                    parent = dst[:-6]  # Remove /index
                    if parent in existing_pages:
                        issues['missing_index'].append({
                            'src': link['src_page'],
                            'dst': dst,
                            'suggested_fix': parent
                        })
                    else:
                        issues['non_existent_pages'].append({
                            'src': link['src_page'],
                            'dst': dst,
                            'url': url
                        })
                elif '//' in dst:
                    issues['double_slash'].append({
                        'src': link['src_page'],
                        'dst': dst,
                        'suggested_fix': dst.replace('//', '/')
                    })
                elif '#' in url and not dst:
                    issues['anchor_issues'].append({
                        'src': link['src_page'],
                        'url': url
                    })
                else:
                    # Check for path variations
                    possible_fixes = self._suggest_fixes(dst, existing_pages)
                    if possible_fixes:
                        issues['path_mismatch'].append({
                            'src': link['src_page'],
                            'dst': dst,
                            'suggestions': possible_fixes[:3]
                        })
                    else:
                        issues['non_existent_pages'].append({
                            'src': link['src_page'],
                            'dst': dst,
                            'url': url
                        })
        
        return issues
    
    def _suggest_fixes(self, broken_path, existing_pages):
        """Suggest possible fixes for broken paths"""
        suggestions = []
        
        # Try common transformations
        transformations = [
            # Remove duplicate segments
            lambda p: '/'.join(dict.fromkeys(p.split('/')).keys()),
            # Add /index
            lambda p: f"{p}/index",
            # Remove /index
            lambda p: p[:-6] if p.endswith('/index') else p,
            # Fix common prefixes
            lambda p: p.replace('architects-handbook/case-studies/pattern-library', 'pattern-library'),
            lambda p: p.replace('architects-handbook/core-principles', 'core-principles'),
            lambda p: p.replace('engineering-leadership/engineering-leadership', 'engineering-leadership'),
        ]
        
        for transform in transformations:
            try:
                fixed = transform(broken_path)
                if fixed in existing_pages and fixed != broken_path:
                    suggestions.append(fixed)
            except:
                pass
        
        # Find similar pages using edit distance
        if not suggestions:
            from difflib import get_close_matches
            close_matches = get_close_matches(broken_path, existing_pages, n=3, cutoff=0.6)
            suggestions.extend(close_matches)
        
        return suggestions
    
    def find_navigation_gaps(self):
        """Find gaps in navigation structure"""
        
        if not self.G:
            self.load_graph()
        
        gaps = {
            'unreachable_from_index': [],
            'no_parent_navigation': [],
            'broken_hierarchy': [],
            'isolated_clusters': []
        }
        
        # Find unreachable pages from index
        if 'index' in self.G:
            reachable = nx.descendants(self.G, 'index')
            reachable.add('index')
            unreachable = set(self.G.nodes()) - reachable
            
            # Filter out index pages (less important)
            important_unreachable = [p for p in unreachable 
                                    if not p.endswith('/index')]
            
            gaps['unreachable_from_index'] = important_unreachable
        
        # Find pages with no parent navigation
        for node in self.G.nodes():
            if '/' in node:
                parent_path = '/'.join(node.split('/')[:-1])
                if parent_path and parent_path not in self.G:
                    gaps['no_parent_navigation'].append({
                        'page': node,
                        'missing_parent': parent_path
                    })
        
        # Find isolated clusters
        components = list(nx.weakly_connected_components(self.G))
        isolated = [comp for comp in components if len(comp) > 1 and 'index' not in comp]
        
        for comp in isolated:
            gaps['isolated_clusters'].append({
                'pages': list(comp)[:10],
                'size': len(comp)
            })
        
        return gaps
    
    def analyze_content_quality(self):
        """Analyze content quality issues"""
        
        self.cursor.execute("""
            SELECT page_id, title, word_count, heading_count, 
                   link_count, quality_score
            FROM pages
        """)
        
        pages = self.cursor.fetchall()
        
        issues = {
            'low_content': [],
            'missing_titles': [],
            'no_headings': [],
            'too_many_links': [],
            'low_quality': []
        }
        
        for page in pages:
            # Low content pages
            if page['word_count'] < 100:
                issues['low_content'].append({
                    'page': page['page_id'],
                    'word_count': page['word_count']
                })
            
            # Missing titles
            if not page['title'] or page['title'] == page['page_id']:
                issues['missing_titles'].append(page['page_id'])
            
            # No headings
            if page['heading_count'] == 0 and page['word_count'] > 100:
                issues['no_headings'].append(page['page_id'])
            
            # Too many links relative to content
            if page['word_count'] > 0:
                link_density = page['link_count'] / (page['word_count'] / 100)
                if link_density > 10:  # More than 10 links per 100 words
                    issues['too_many_links'].append({
                        'page': page['page_id'],
                        'links': page['link_count'],
                        'words': page['word_count'],
                        'density': round(link_density, 2)
                    })
            
            # Low quality score
            if page['quality_score'] < 50:
                issues['low_quality'].append({
                    'page': page['page_id'],
                    'score': page['quality_score']
                })
        
        return issues
    
    def generate_fix_recommendations(self):
        """Generate prioritized fix recommendations"""
        
        recommendations = []
        
        # 1. Diagnose broken links
        broken_issues = self.diagnose_broken_links()
        
        # High priority: Path mismatches with suggestions
        for issue in broken_issues['path_mismatch'][:20]:
            recommendations.append({
                'priority': 'HIGH',
                'type': 'broken_link',
                'action': 'update_link',
                'details': issue
            })
        
        # 2. Navigation gaps
        nav_gaps = self.find_navigation_gaps()
        
        # High priority: Important unreachable pages
        for page in nav_gaps['unreachable_from_index'][:10]:
            recommendations.append({
                'priority': 'HIGH',
                'type': 'navigation',
                'action': 'add_navigation_link',
                'page': page
            })
        
        # 3. Content quality
        quality_issues = self.analyze_content_quality()
        
        # Medium priority: Low content pages
        for issue in quality_issues['low_content'][:10]:
            recommendations.append({
                'priority': 'MEDIUM',
                'type': 'content',
                'action': 'add_content',
                'details': issue
            })
        
        return recommendations
    
    def generate_report(self):
        """Generate comprehensive troubleshooting report"""
        
        print("=" * 60)
        print("KNOWLEDGE GRAPH TROUBLESHOOTING REPORT")
        print("=" * 60)
        
        # Overall statistics
        self.cursor.execute("SELECT COUNT(*) FROM pages")
        total_pages = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_external = 0")
        total_links = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 0 AND is_external = 0")
        broken_links = self.cursor.fetchone()[0]
        
        print(f"\nOverall Statistics:")
        print(f"  Total pages: {total_pages}")
        print(f"  Total internal links: {total_links}")
        print(f"  Broken links: {broken_links} ({(broken_links/total_links)*100:.1f}%)")
        
        # Broken link diagnosis
        print("\n" + "-" * 40)
        print("BROKEN LINK DIAGNOSIS")
        print("-" * 40)
        
        issues = self.diagnose_broken_links()
        for issue_type, items in issues.items():
            if items:
                print(f"\n{issue_type.replace('_', ' ').title()}: {len(items)} cases")
                if items and 'suggested_fix' in items[0]:
                    print(f"  Example: {items[0]['src']} -> {items[0]['dst']}")
                    print(f"  Suggested fix: {items[0]['suggested_fix']}")
        
        # Navigation gaps
        print("\n" + "-" * 40)
        print("NAVIGATION GAPS")
        print("-" * 40)
        
        gaps = self.find_navigation_gaps()
        print(f"\nUnreachable from index: {len(gaps['unreachable_from_index'])} pages")
        if gaps['unreachable_from_index']:
            print("  Top unreachable pages:")
            for page in gaps['unreachable_from_index'][:5]:
                print(f"    - {page}")
        
        print(f"\nIsolated clusters: {len(gaps['isolated_clusters'])}")
        if gaps['isolated_clusters']:
            for cluster in gaps['isolated_clusters'][:3]:
                print(f"  Cluster of {cluster['size']} pages")
        
        # Content quality
        print("\n" + "-" * 40)
        print("CONTENT QUALITY ISSUES")
        print("-" * 40)
        
        quality = self.analyze_content_quality()
        print(f"\nLow content pages (<100 words): {len(quality['low_content'])}")
        print(f"Missing titles: {len(quality['missing_titles'])}")
        print(f"No headings: {len(quality['no_headings'])}")
        print(f"Too many links: {len(quality['too_many_links'])}")
        print(f"Low quality score: {len(quality['low_quality'])}")
        
        # Recommendations
        print("\n" + "-" * 40)
        print("TOP RECOMMENDATIONS")
        print("-" * 40)
        
        recommendations = self.generate_fix_recommendations()
        
        high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
        print(f"\nHigh Priority Fixes: {len(high_priority)}")
        
        for rec in high_priority[:5]:
            print(f"\n  {rec['type'].upper()}: {rec['action']}")
            if 'details' in rec:
                if 'suggestions' in rec['details']:
                    print(f"    From: {rec['details']['src']}")
                    print(f"    To: {rec['details']['dst']}")
                    print(f"    Suggestions: {', '.join(rec['details']['suggestions'][:2])}")
            elif 'page' in rec:
                print(f"    Page: {rec['page']}")
        
        # Save full report
        full_report = {
            'statistics': {
                'total_pages': total_pages,
                'total_links': total_links,
                'broken_links': broken_links
            },
            'broken_link_issues': {k: len(v) for k, v in issues.items()},
            'navigation_gaps': {
                'unreachable_count': len(gaps['unreachable_from_index']),
                'isolated_clusters': len(gaps['isolated_clusters'])
            },
            'content_quality': {k: len(v) for k, v in quality.items()},
            'recommendations': recommendations[:50]
        }
        
        with open('troubleshooting_report.json', 'w') as f:
            json.dump(full_report, f, indent=2)
        
        print("\n✅ Full report saved to troubleshooting_report.json")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    troubleshooter = KnowledgeGraphTroubleshooter()
    
    # Load and analyze graph
    troubleshooter.load_graph()
    
    # Generate comprehensive report
    troubleshooter.generate_report()
    
    # Generate SQL fixes for path mismatches
    issues = troubleshooter.diagnose_broken_links()
    
    with open('auto_fixes.sql', 'w') as f:
        f.write("-- Automated fixes for path mismatches\n")
        f.write("BEGIN TRANSACTION;\n\n")
        
        for issue in issues['path_mismatch'][:50]:
            if issue['suggestions']:
                suggested = issue['suggestions'][0]
                f.write(f"""
UPDATE links 
SET dst_page = '{suggested}', is_valid = 1
WHERE src_page = '{issue['src']}' 
  AND dst_page = '{issue['dst']}';
""")
        
        f.write("\nCOMMIT;\n")
    
    print("\n✅ Additional fixes saved to auto_fixes.sql")
    
    troubleshooter.close()

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    main()
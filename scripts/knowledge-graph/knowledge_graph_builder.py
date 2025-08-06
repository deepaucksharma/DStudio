#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Builder for Distributed Systems Studio
====================================================================

This script builds a complete knowledge graph of the documentation site including:
- All pages and their relationships
- Navigation structure from mkdocs.yml
- Internal and external links
- Concepts and topics
- Broken link detection
- Orphaned page detection
- Cross-reference analysis
"""

import os
import re
import yaml
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
import networkx as nx
from urllib.parse import urlparse, urljoin
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PageNode:
    """Represents a documentation page in the knowledge graph"""
    path: str  # Relative path from docs/
    title: str
    description: str = ""
    headings: List[Dict[str, Any]] = field(default_factory=list)
    internal_links: Set[str] = field(default_factory=set)
    external_links: Set[str] = field(default_factory=set)
    anchors: Set[str] = field(default_factory=set)  # Available anchor points
    images: Set[str] = field(default_factory=set)
    code_blocks: List[Dict[str, str]] = field(default_factory=list)
    concepts: Set[str] = field(default_factory=set)  # Extracted concepts/keywords
    tags: Set[str] = field(default_factory=set)
    category: str = ""
    tier: str = ""  # Gold, Silver, Bronze for patterns
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    word_count: int = 0
    last_modified: str = ""
    hash: str = ""  # Content hash for change detection
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'path': self.path,
            'title': self.title,
            'description': self.description,
            'headings': self.headings,
            'internal_links': list(self.internal_links),
            'external_links': list(self.external_links),
            'anchors': list(self.anchors),
            'images': list(self.images),
            'code_blocks': self.code_blocks,
            'concepts': list(self.concepts),
            'tags': list(self.tags),
            'category': self.category,
            'tier': self.tier,
            'frontmatter': self.frontmatter,
            'word_count': self.word_count,
            'last_modified': self.last_modified,
            'hash': self.hash
        }

class KnowledgeGraphBuilder:
    """Builds and analyzes the documentation knowledge graph"""
    
    def __init__(self, docs_dir: str = "docs", mkdocs_file: str = "mkdocs.yml"):
        self.docs_dir = Path(docs_dir)
        self.mkdocs_file = Path(mkdocs_file)
        self.pages: Dict[str, PageNode] = {}
        self.navigation: Dict[str, Any] = {}
        self.graph = nx.DiGraph()
        self.concept_graph = nx.Graph()
        self.broken_links: List[Dict[str, str]] = []
        self.orphaned_pages: Set[str] = set()
        self.external_domains: Counter = Counter()
        
    def build(self):
        """Build the complete knowledge graph"""
        logger.info("Starting knowledge graph construction...")
        
        # Step 1: Discover all pages
        self._discover_pages()
        logger.info(f"Discovered {len(self.pages)} pages")
        
        # Step 2: Parse mkdocs.yml
        self._parse_mkdocs()
        logger.info("Parsed mkdocs.yml navigation")
        
        # Step 3: Extract content and links
        self._extract_content()
        logger.info("Extracted content and links")
        
        # Step 4: Build graph structure
        self._build_graph()
        logger.info("Built graph structure")
        
        # Step 5: Analyze and validate
        self._analyze()
        logger.info("Analysis complete")
        
        return self
    
    def _discover_pages(self):
        """Discover all markdown files in docs directory"""
        for md_file in self.docs_dir.rglob("*.md"):
            rel_path = md_file.relative_to(self.docs_dir)
            path_str = str(rel_path).replace('\\', '/')
            
            # Get file stats
            stat = md_file.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Create page node
            page = PageNode(
                path=path_str,
                title=self._extract_title_from_path(path_str),
                last_modified=last_modified
            )
            
            # Determine category from path
            parts = path_str.split('/')
            if len(parts) > 1:
                page.category = parts[0]
            
            self.pages[path_str] = page
    
    def _parse_mkdocs(self):
        """Parse mkdocs.yml to understand navigation structure"""
        if not self.mkdocs_file.exists():
            logger.warning(f"mkdocs.yml not found at {self.mkdocs_file}")
            return
        
        with open(self.mkdocs_file, 'r', encoding='utf-8') as f:
            mkdocs_config = yaml.safe_load(f)
        
        self.navigation = mkdocs_config.get('nav', [])
        self.site_name = mkdocs_config.get('site_name', 'Documentation')
        self.site_url = mkdocs_config.get('site_url', '')
        
        # Extract navigation paths
        self.nav_paths = set()
        self._extract_nav_paths(self.navigation)
    
    def _extract_nav_paths(self, nav_items, prefix=""):
        """Recursively extract paths from navigation"""
        if isinstance(nav_items, list):
            for item in nav_items:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, str):
                            # This is a direct page reference
                            self.nav_paths.add(value)
                        elif isinstance(value, list):
                            # This is a section with sub-items
                            self._extract_nav_paths(value, f"{prefix}{key}/")
                elif isinstance(item, str):
                    self.nav_paths.add(item)
    
    def _extract_content(self):
        """Extract content from all pages"""
        for path, page in self.pages.items():
            file_path = self.docs_dir / path
            
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate content hash
            page.hash = hashlib.md5(content.encode()).hexdigest()
            
            # Extract frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            if frontmatter_match:
                try:
                    page.frontmatter = yaml.safe_load(frontmatter_match.group(1))
                    page.title = page.frontmatter.get('title', page.title)
                    page.description = page.frontmatter.get('description', '')
                    page.tags = set(page.frontmatter.get('tags', []))
                except:
                    pass
                content = content[frontmatter_match.end():]
            
            # Extract title from first H1 if not in frontmatter
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match and not page.frontmatter.get('title'):
                page.title = title_match.group(1)
            
            # Extract all headings with hierarchy
            headings = []
            for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
                level = len(match.group(1))
                text = match.group(2)
                anchor = self._create_anchor(text)
                headings.append({
                    'level': level,
                    'text': text,
                    'anchor': anchor
                })
                page.anchors.add(anchor)
            page.headings = headings
            
            # Extract internal links
            # Match [text](link) and raw URLs
            link_patterns = [
                r'\[([^\]]+)\]\(([^)]+)\)',  # Markdown links
                r'(?:^|\s)((?:\.\.\/|\/)?[\w\-\/]+\.md)(?:\s|$)',  # Direct .md references
            ]
            
            for pattern in link_patterns:
                for match in re.finditer(pattern, content):
                    if pattern == link_patterns[0]:
                        link = match.group(2)
                    else:
                        link = match.group(1)
                    
                    # Process the link
                    if link.startswith('http://') or link.startswith('https://'):
                        page.external_links.add(link)
                        domain = urlparse(link).netloc
                        self.external_domains[domain] += 1
                    elif link.startswith('#'):
                        # Anchor link within same page
                        page.internal_links.add(f"{path}{link}")
                    elif link.startswith('mailto:'):
                        continue
                    else:
                        # Internal link
                        normalized = self._normalize_link(link, path)
                        if normalized:
                            page.internal_links.add(normalized)
            
            # Extract images
            for match in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', content):
                page.images.add(match.group(2))
            
            # Extract code blocks
            for match in re.finditer(r'```(\w*)\n(.*?)\n```', content, re.DOTALL):
                language = match.group(1) or 'plain'
                code = match.group(2)
                page.code_blocks.append({
                    'language': language,
                    'lines': len(code.split('\n'))
                })
            
            # Extract concepts (capitalized phrases, technical terms)
            concepts = set()
            
            # Technical terms and patterns
            tech_patterns = [
                r'\b(?:CAP|ACID|BASE|CQRS|CRDT|REST|GraphQL|gRPC|API)\b',
                r'\b(?:microservice|monolith|serverless|container|kubernetes)\w*\b',
                r'\b(?:circuit breaker|rate limit|load balanc|cach|shard|partition)\w*\b',
                r'\b(?:consensus|raft|paxos|byzantine|quorum)\b',
                r'\b(?:eventual|strong|weak|causal) consistency\b',
            ]
            
            for pattern in tech_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    concepts.add(match.group(0).lower())
            
            page.concepts = concepts
            
            # Word count
            page.word_count = len(re.findall(r'\b\w+\b', content))
            
            # Detect pattern tier
            if 'pattern-library' in path:
                if 'gold' in content.lower() or '🥇' in content:
                    page.tier = 'gold'
                elif 'silver' in content.lower() or '🥈' in content:
                    page.tier = 'silver'
                elif 'bronze' in content.lower() or '🥉' in content:
                    page.tier = 'bronze'
    
    def _normalize_link(self, link: str, source_path: str) -> Optional[str]:
        """Normalize a link relative to source path"""
        # Remove any fragment
        link = link.split('#')[0]
        
        # Remove query params
        link = link.split('?')[0]
        
        if not link:
            return None
        
        # Handle absolute paths
        if link.startswith('/'):
            link = link[1:]  # Remove leading slash
        else:
            # Relative path - resolve relative to source
            source_dir = os.path.dirname(source_path)
            if source_dir:
                link = os.path.join(source_dir, link)
        
        # Normalize path
        link = os.path.normpath(link).replace('\\', '/')
        
        # Add .md extension if missing
        if not link.endswith('.md') and not link.endswith('/'):
            # Check if it's a directory reference
            potential_index = f"{link}/index.md"
            if potential_index in self.pages:
                link = potential_index
            else:
                link = f"{link}.md"
        elif link.endswith('/'):
            link = f"{link}index.md"
        
        return link
    
    def _create_anchor(self, text: str) -> str:
        """Create anchor from heading text"""
        # Simple anchor creation - lowercase and replace spaces with hyphens
        anchor = re.sub(r'[^\w\s-]', '', text.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor.strip('-')
    
    def _extract_title_from_path(self, path: str) -> str:
        """Extract a title from file path"""
        # Get filename without extension
        name = os.path.splitext(os.path.basename(path))[0]
        
        # Convert index to parent directory name
        if name == 'index':
            parent = os.path.dirname(path)
            if parent:
                name = os.path.basename(parent)
        
        # Convert kebab-case or snake_case to title case
        name = name.replace('-', ' ').replace('_', ' ')
        return name.title()
    
    def _build_graph(self):
        """Build NetworkX graphs from extracted data"""
        # Build main page graph
        for path, page in self.pages.items():
            self.graph.add_node(path, **page.to_dict())
            
            # Add edges for internal links
            for link in page.internal_links:
                # Remove anchor from link
                target = link.split('#')[0]
                if target in self.pages:
                    self.graph.add_edge(path, target, type='link')
        
        # Build concept graph
        for path, page in self.pages.items():
            for concept in page.concepts:
                self.concept_graph.add_node(concept, type='concept')
                self.concept_graph.add_node(path, type='page')
                self.concept_graph.add_edge(concept, path)
        
        # Add navigation structure to graph
        self._add_navigation_edges()
    
    def _add_navigation_edges(self):
        """Add navigation hierarchy edges to graph"""
        def process_nav(items, parent=None):
            if isinstance(items, list):
                prev_page = None
                for item in items:
                    if isinstance(item, dict):
                        for title, value in item.items():
                            if isinstance(value, str):
                                # Direct page
                                if value in self.pages and parent:
                                    self.graph.add_edge(parent, value, type='nav_child')
                                if prev_page and value in self.pages:
                                    self.graph.add_edge(prev_page, value, type='nav_sibling')
                                prev_page = value
                            elif isinstance(value, list):
                                # Section with children
                                process_nav(value, parent)
                    elif isinstance(item, str):
                        if item in self.pages and parent:
                            self.graph.add_edge(parent, item, type='nav_child')
                        if prev_page and item in self.pages:
                            self.graph.add_edge(prev_page, item, type='nav_sibling')
                        prev_page = item
        
        # Process navigation starting from root
        if 'index.md' in self.pages:
            process_nav(self.navigation, 'index.md')
    
    def _analyze(self):
        """Analyze the graph for issues and insights"""
        # Find broken internal links
        for path, page in self.pages.items():
            for link in page.internal_links:
                target = link.split('#')[0]
                if target and target not in self.pages:
                    self.broken_links.append({
                        'source': path,
                        'target': link,
                        'type': 'internal'
                    })
                
                # Check anchor links
                if '#' in link:
                    target_page, anchor = link.split('#', 1)
                    if target_page in self.pages:
                        if anchor not in self.pages[target_page].anchors:
                            self.broken_links.append({
                                'source': path,
                                'target': link,
                                'type': 'anchor'
                            })
        
        # Find orphaned pages (not in navigation and not linked)
        for path in self.pages:
            if path not in self.nav_paths:
                # Check if it's linked from any other page
                has_incoming = any(
                    path in page.internal_links 
                    for p, page in self.pages.items() 
                    if p != path
                )
                if not has_incoming and path != 'index.md':
                    self.orphaned_pages.add(path)
        
        # Calculate page importance using PageRank
        try:
            self.pagerank = nx.pagerank(self.graph)
        except:
            self.pagerank = {}
        
        # Find strongly connected components
        if self.graph.number_of_nodes() > 0:
            # Convert to undirected for component analysis
            undirected = self.graph.to_undirected()
            self.components = list(nx.connected_components(undirected))
        else:
            self.components = []
    
    def generate_reports(self, output_dir: str = "reports"):
        """Generate comprehensive reports"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        
        # 1. Main knowledge graph JSON
        graph_data = {
            'metadata': {
                'generated': timestamp,
                'total_pages': len(self.pages),
                'total_links': sum(len(p.internal_links) for p in self.pages.values()),
                'total_concepts': len(set().union(*[p.concepts for p in self.pages.values()])),
                'site_name': self.site_name,
                'site_url': self.site_url
            },
            'pages': {path: page.to_dict() for path, page in self.pages.items()},
            'navigation': self.navigation,
            'broken_links': self.broken_links,
            'orphaned_pages': list(self.orphaned_pages),
            'external_domains': dict(self.external_domains.most_common(20)),
            'pagerank': self.pagerank,
            'components': [list(comp) for comp in self.components[:10]]  # Top 10 components
        }
        
        with open(output_path / 'knowledge_graph.json', 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2)
        
        # 2. GraphML for visualization tools
        nx.write_graphml(self.graph, output_path / 'page_graph.graphml')
        nx.write_graphml(self.concept_graph, output_path / 'concept_graph.graphml')
        
        # 3. Broken links report
        with open(output_path / 'broken_links.md', 'w', encoding='utf-8') as f:
            f.write("# Broken Links Report\n\n")
            f.write(f"Generated: {timestamp}\n\n")
            f.write(f"Total broken links: {len(self.broken_links)}\n\n")
            
            if self.broken_links:
                f.write("## Broken Internal Links\n\n")
                for link in sorted(self.broken_links, key=lambda x: x['source']):
                    f.write(f"- **{link['source']}** → `{link['target']}` ({link['type']})\n")
        
        # 4. Orphaned pages report
        with open(output_path / 'orphaned_pages.md', 'w', encoding='utf-8') as f:
            f.write("# Orphaned Pages Report\n\n")
            f.write(f"Generated: {timestamp}\n\n")
            f.write(f"Total orphaned pages: {len(self.orphaned_pages)}\n\n")
            
            if self.orphaned_pages:
                f.write("## Pages not in navigation and not linked:\n\n")
                for page in sorted(self.orphaned_pages):
                    f.write(f"- `{page}`\n")
        
        # 5. Analytics report
        with open(output_path / 'analytics.md', 'w', encoding='utf-8') as f:
            f.write("# Documentation Analytics Report\n\n")
            f.write(f"Generated: {timestamp}\n\n")
            
            f.write("## Overview\n\n")
            f.write(f"- Total pages: {len(self.pages)}\n")
            f.write(f"- Total internal links: {sum(len(p.internal_links) for p in self.pages.values())}\n")
            f.write(f"- Total external links: {sum(len(p.external_links) for p in self.pages.values())}\n")
            f.write(f"- Total images: {sum(len(p.images) for p in self.pages.values())}\n")
            f.write(f"- Total word count: {sum(p.word_count for p in self.pages.values()):,}\n")
            f.write(f"- Unique concepts: {len(set().union(*[p.concepts for p in self.pages.values()]))}\n\n")
            
            f.write("## Top Pages by PageRank\n\n")
            top_pages = sorted(self.pagerank.items(), key=lambda x: x[1], reverse=True)[:20]
            for i, (page, score) in enumerate(top_pages, 1):
                title = self.pages[page].title if page in self.pages else page
                f.write(f"{i}. **{title}** (`{page}`): {score:.4f}\n")
            
            f.write("\n## Categories\n\n")
            categories = defaultdict(list)
            for path, page in self.pages.items():
                categories[page.category].append(path)
            
            for category, pages in sorted(categories.items()):
                f.write(f"- **{category or 'root'}**: {len(pages)} pages\n")
            
            f.write("\n## Pattern Tiers\n\n")
            tiers = defaultdict(list)
            for path, page in self.pages.items():
                if page.tier:
                    tiers[page.tier].append(path)
            
            for tier in ['gold', 'silver', 'bronze']:
                if tier in tiers:
                    f.write(f"- **{tier.capitalize()}**: {len(tiers[tier])} patterns\n")
            
            f.write("\n## Most Linked Pages\n\n")
            incoming_links = defaultdict(int)
            for page in self.pages.values():
                for link in page.internal_links:
                    target = link.split('#')[0]
                    if target in self.pages:
                        incoming_links[target] += 1
            
            top_linked = sorted(incoming_links.items(), key=lambda x: x[1], reverse=True)[:15]
            for page, count in top_linked:
                title = self.pages[page].title
                f.write(f"- **{title}** (`{page}`): {count} incoming links\n")
            
            f.write("\n## Top External Domains\n\n")
            for domain, count in self.external_domains.most_common(15):
                f.write(f"- {domain}: {count} links\n")
            
            f.write("\n## Largest Connected Components\n\n")
            for i, component in enumerate(self.components[:5], 1):
                f.write(f"{i}. Component with {len(component)} pages\n")
                sample = list(component)[:5]
                for page in sample:
                    if page in self.pages:
                        f.write(f"   - {self.pages[page].title}\n")
                if len(component) > 5:
                    f.write(f"   - ... and {len(component) - 5} more\n")
        
        # 6. D3.js visualization data
        d3_nodes = []
        d3_links = []
        
        for node in self.graph.nodes():
            if node in self.pages:
                page = self.pages[node]
                d3_nodes.append({
                    'id': node,
                    'title': page.title,
                    'category': page.category,
                    'tier': page.tier,
                    'wordCount': page.word_count,
                    'pagerank': self.pagerank.get(node, 0)
                })
        
        for source, target in self.graph.edges():
            edge_data = self.graph.edges[source, target]
            d3_links.append({
                'source': source,
                'target': target,
                'type': edge_data.get('type', 'link')
            })
        
        d3_data = {
            'nodes': d3_nodes,
            'links': d3_links
        }
        
        with open(output_path / 'd3_graph.json', 'w', encoding='utf-8') as f:
            json.dump(d3_data, f, indent=2)
        
        # 7. CSV exports for further analysis
        import csv
        
        # Pages CSV
        with open(output_path / 'pages.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['path', 'title', 'category', 'tier', 'word_count', 
                           'internal_links', 'external_links', 'concepts', 'pagerank'])
            for path, page in self.pages.items():
                writer.writerow([
                    path,
                    page.title,
                    page.category,
                    page.tier,
                    page.word_count,
                    len(page.internal_links),
                    len(page.external_links),
                    len(page.concepts),
                    self.pagerank.get(path, 0)
                ])
        
        # Links CSV
        with open(output_path / 'links.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['source', 'target', 'type'])
            for source, target, data in self.graph.edges(data=True):
                writer.writerow([source, target, data.get('type', 'link')])
        
        logger.info(f"Reports generated in {output_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("KNOWLEDGE GRAPH ANALYSIS COMPLETE")
        print("="*60)
        print(f"Total pages analyzed: {len(self.pages)}")
        print(f"Total links found: {sum(len(p.internal_links) for p in self.pages.values())}")
        print(f"Broken links detected: {len(self.broken_links)}")
        print(f"Orphaned pages found: {len(self.orphaned_pages)}")
        print(f"Unique concepts extracted: {len(set().union(*[p.concepts for p in self.pages.values()]))}")
        print(f"\nReports saved to: {output_path}")
        print("\nGenerated files:")
        print("  - knowledge_graph.json    : Complete graph data")
        print("  - page_graph.graphml      : Page network for Gephi/Cytoscape")
        print("  - concept_graph.graphml   : Concept network")
        print("  - d3_graph.json          : D3.js visualization data")
        print("  - broken_links.md        : Broken links report")
        print("  - orphaned_pages.md      : Orphaned pages report")
        print("  - analytics.md           : Comprehensive analytics")
        print("  - pages.csv              : Page data for analysis")
        print("  - links.csv              : Link data for analysis")

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build knowledge graph from documentation')
    parser.add_argument('--docs-dir', default='docs', help='Documentation directory')
    parser.add_argument('--mkdocs-file', default='mkdocs.yml', help='mkdocs.yml file path')
    parser.add_argument('--output-dir', default='reports', help='Output directory for reports')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Build knowledge graph
    builder = KnowledgeGraphBuilder(args.docs_dir, args.mkdocs_file)
    builder.build()
    builder.generate_reports(args.output_dir)

if __name__ == '__main__':
    main()
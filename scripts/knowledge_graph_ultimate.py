#!/usr/bin/env python3
"""
Ultimate Knowledge Graph System for Documentation Analysis
==========================================================

Best practices extracted:
1. SQLite with FTS5 for fast full-text search
2. Stable page_id based on path (not auto-increment)
3. Async link validation for speed
4. JSON-LD for semantic portability
5. Natural language query routing
6. Incremental updates with md5 hashing
7. Comprehensive issue detection per page
"""

import os
import re
import json
import yaml
import sqlite3
import hashlib
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from datetime import datetime
import numpy as np
from urllib.parse import urlparse, urljoin
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizedKnowledgeGraph:
    """
    High-performance knowledge graph implementation
    """
    
    def __init__(self, db_path: str = "knowledge_graph_ultimate.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for performance
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA cache_size=10000")
        self.conn.execute("PRAGMA temp_store=MEMORY")
        
        self.create_optimized_schema()
        self.issues_per_page = defaultdict(list)
        self.stats = defaultdict(int)
        
    def create_optimized_schema(self):
        """Create optimized schema with best practices"""
        cursor = self.conn.cursor()
        
        # Main pages table with stable IDs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                page_id TEXT PRIMARY KEY,  -- Stable slug from path
                title TEXT NOT NULL,
                path TEXT UNIQUE NOT NULL,
                nav_parent TEXT,
                category TEXT,
                tier TEXT,
                last_modified TEXT,
                md5_hash TEXT,
                word_count INTEGER DEFAULT 0,
                has_frontmatter BOOLEAN DEFAULT 0,
                has_toc BOOLEAN DEFAULT 0,
                heading_count INTEGER DEFAULT 0,
                link_count INTEGER DEFAULT 0,
                image_count INTEGER DEFAULT 0,
                code_block_count INTEGER DEFAULT 0,
                pagerank REAL DEFAULT 0,
                importance_score REAL DEFAULT 0,
                quality_score REAL DEFAULT 0,
                FOREIGN KEY (nav_parent) REFERENCES pages(page_id)
            )
        ''')
        
        # FTS5 virtual table for full-text search
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                page_id UNINDEXED,
                title,
                body,
                content=pages,
                tokenize='porter unicode61'
            )
        ''')
        
        # Links table with validation status
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                src_page TEXT NOT NULL,
                dst_page TEXT,
                dst_url TEXT,
                is_external BOOLEAN DEFAULT 0,
                is_valid BOOLEAN,
                anchor TEXT,
                link_text TEXT,
                http_status INTEGER,
                last_checked TEXT,
                FOREIGN KEY (src_page) REFERENCES pages(page_id),
                FOREIGN KEY (dst_page) REFERENCES pages(page_id),
                PRIMARY KEY (src_page, dst_url, anchor)
            )
        ''')
        
        # Concepts with TF-IDF scoring
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                concept_id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT UNIQUE NOT NULL,
                concept_type TEXT,  -- tag, glossary, named-entity, pattern
                frequency INTEGER DEFAULT 0,
                idf_score REAL DEFAULT 0
            )
        ''')
        
        # Page-Concept relationships with scores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page_concepts (
                page_id TEXT NOT NULL,
                concept_id INTEGER NOT NULL,
                tf_score REAL DEFAULT 0,
                tfidf_score REAL DEFAULT 0,
                position_weight REAL DEFAULT 1.0,  -- Higher if in title/headers
                FOREIGN KEY (page_id) REFERENCES pages(page_id),
                FOREIGN KEY (concept_id) REFERENCES concepts(concept_id),
                PRIMARY KEY (page_id, concept_id)
            )
        ''')
        
        # Navigation edges from mkdocs.yml
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nav_edges (
                parent TEXT,
                child TEXT NOT NULL,
                position INTEGER,
                nav_title TEXT,
                depth INTEGER DEFAULT 0,
                FOREIGN KEY (parent) REFERENCES pages(page_id),
                FOREIGN KEY (child) REFERENCES pages(page_id),
                PRIMARY KEY (parent, child)
            )
        ''')
        
        # Redirects from mkdocs configuration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS redirects (
                old_path TEXT PRIMARY KEY,
                new_path TEXT NOT NULL
            )
        ''')
        
        # Comprehensive issues table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS issues (
                issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id TEXT,
                issue_type TEXT NOT NULL,  -- broken_link, missing_title, orphaned, etc.
                severity TEXT DEFAULT 'warning',  -- error, warning, info
                details TEXT,
                suggested_fix TEXT,
                auto_fixable BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES pages(page_id)
            )
        ''')
        
        # Page headings for structure analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS headings (
                page_id TEXT NOT NULL,
                level INTEGER NOT NULL,
                text TEXT NOT NULL,
                anchor TEXT,
                position INTEGER,
                parent_heading TEXT,
                FOREIGN KEY (page_id) REFERENCES pages(page_id),
                PRIMARY KEY (page_id, position)
            )
        ''')
        
        # Metrics for tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                metric_name TEXT PRIMARY KEY,
                metric_value REAL,
                details TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create optimized indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_src ON links(src_page)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_dst ON links(dst_page)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_external ON links(is_external)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_valid ON links(is_valid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_concepts_type ON concepts(concept_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_concepts_page ON page_concepts(page_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_concepts_concept ON page_concepts(concept_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nav_edges_parent ON nav_edges(parent)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nav_edges_child ON nav_edges(child)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_issues_page ON issues(page_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_issues_type ON issues(issue_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_issues_severity ON issues(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_headings_page ON headings(page_id)')
        
        self.conn.commit()
    
    def analyze_page(self, page_path: Path, docs_dir: Path) -> Dict[str, Any]:
        """
        Comprehensive analysis of a single page with issue detection
        """
        rel_path = page_path.relative_to(docs_dir)
        page_id = rel_path.with_suffix('').as_posix()
        
        # Read file
        try:
            content = page_path.read_text(encoding='utf-8')
        except Exception as e:
            self.issues_per_page[page_id].append({
                'type': 'file_read_error',
                'severity': 'error',
                'details': str(e),
                'fix': 'Check file permissions and encoding'
            })
            return None
        
        # Calculate hash for change detection
        md5_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Get file stats
        stat = page_path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        # Initialize page data
        page_data = {
            'page_id': page_id,
            'path': str(rel_path),
            'md5_hash': md5_hash,
            'last_modified': last_modified,
            'issues': [],
            'links': [],
            'concepts': [],
            'headings': [],
            'quality_score': 100.0  # Start with perfect score, deduct for issues
        }
        
        # Extract frontmatter
        frontmatter = {}
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if frontmatter_match:
            try:
                frontmatter = yaml.safe_load(frontmatter_match.group(1))
                page_data['has_frontmatter'] = True
                page_data['title'] = frontmatter.get('title', '')
                content_body = content[frontmatter_match.end():]
            except:
                self.issues_per_page[page_id].append({
                    'type': 'invalid_frontmatter',
                    'severity': 'warning',
                    'details': 'Failed to parse YAML frontmatter',
                    'fix': 'Check YAML syntax in frontmatter'
                })
                page_data['quality_score'] -= 5
                content_body = content
        else:
            page_data['has_frontmatter'] = False
            content_body = content
        
        # Check for title
        if not page_data.get('title'):
            # Try to find H1
            h1_match = re.search(r'^#\s+(.+)$', content_body, re.MULTILINE)
            if h1_match:
                page_data['title'] = h1_match.group(1).strip()
            else:
                # Generate from filename
                page_data['title'] = page_id.split('/')[-1].replace('-', ' ').title()
                self.issues_per_page[page_id].append({
                    'type': 'missing_title',
                    'severity': 'warning',
                    'details': 'No title in frontmatter or H1 heading',
                    'fix': 'Add title to frontmatter or add # Heading',
                    'auto_fixable': True
                })
                page_data['quality_score'] -= 10
        
        # Extract headings and check structure
        headings = []
        prev_level = 0
        heading_anchors = set()
        
        for match in re.finditer(r'^(#{1,6})\s+(.+)$', content_body, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            anchor = self._create_anchor(text)
            
            # Check for duplicate anchors
            if anchor in heading_anchors:
                self.issues_per_page[page_id].append({
                    'type': 'duplicate_heading_anchor',
                    'severity': 'warning',
                    'details': f'Duplicate anchor: {anchor} from heading "{text}"',
                    'fix': f'Make heading unique or use explicit anchor'
                })
                page_data['quality_score'] -= 3
            heading_anchors.add(anchor)
            
            # Check heading hierarchy
            if level > prev_level + 1 and prev_level > 0:
                self.issues_per_page[page_id].append({
                    'type': 'heading_hierarchy_skip',
                    'severity': 'info',
                    'details': f'Heading level jumps from H{prev_level} to H{level}',
                    'fix': 'Use sequential heading levels'
                })
                page_data['quality_score'] -= 2
            
            headings.append({
                'level': level,
                'text': text,
                'anchor': anchor,
                'position': match.start()
            })
            prev_level = level
        
        page_data['headings'] = headings
        page_data['heading_count'] = len(headings)
        
        # Check for TOC
        page_data['has_toc'] = '[TOC]' in content or '[[toc]]' in content.lower()
        
        # Extract and validate links
        links = []
        # Match [text](url) format
        for match in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', content_body):
            link_text = match.group(1)
            link_url = match.group(2)
            
            if not link_text:
                self.issues_per_page[page_id].append({
                    'type': 'empty_link_text',
                    'severity': 'warning',
                    'details': f'Empty link text for URL: {link_url}',
                    'fix': 'Add descriptive link text',
                    'auto_fixable': True
                })
                page_data['quality_score'] -= 2
            
            # Classify link
            is_external = link_url.startswith(('http://', 'https://', 'ftp://'))
            anchor = None
            
            if not is_external:
                # Internal link
                if '#' in link_url:
                    link_path, anchor = link_url.split('#', 1)
                else:
                    link_path = link_url
                    
                # Normalize internal link
                if link_path:
                    normalized = self._normalize_internal_link(link_path, page_id)
                    links.append({
                        'dst_page': normalized,
                        'dst_url': link_url,
                        'is_external': False,
                        'anchor': anchor,
                        'link_text': link_text
                    })
            else:
                # External link
                links.append({
                    'dst_page': None,
                    'dst_url': link_url,
                    'is_external': True,
                    'anchor': None,
                    'link_text': link_text
                })
                
                # Check for insecure HTTP
                if link_url.startswith('http://'):
                    self.issues_per_page[page_id].append({
                        'type': 'insecure_http_link',
                        'severity': 'info',
                        'details': f'HTTP link (not HTTPS): {link_url}',
                        'fix': 'Consider using HTTPS',
                        'auto_fixable': True
                    })
                    page_data['quality_score'] -= 1
        
        page_data['links'] = links
        page_data['link_count'] = len(links)
        
        # Extract images and check
        images = []
        for match in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', content_body):
            alt_text = match.group(1)
            img_url = match.group(2)
            
            if not alt_text:
                self.issues_per_page[page_id].append({
                    'type': 'missing_image_alt',
                    'severity': 'warning',
                    'details': f'Missing alt text for image: {img_url}',
                    'fix': 'Add descriptive alt text for accessibility',
                    'auto_fixable': False
                })
                page_data['quality_score'] -= 3
            
            images.append({'url': img_url, 'alt': alt_text})
        
        page_data['image_count'] = len(images)
        
        # Extract code blocks
        code_blocks = []
        for match in re.finditer(r'```(\w*)\n(.*?)\n```', content_body, re.DOTALL):
            language = match.group(1) or 'plain'
            code = match.group(2)
            code_blocks.append({
                'language': language,
                'lines': len(code.split('\n'))
            })
            
            # Check for very long code blocks
            code_lines = len(code.split('\n'))
            if code_lines > 100:
                self.issues_per_page[page_id].append({
                    'type': 'long_code_block',
                    'severity': 'info',
                    'details': f'{language} code block with {code_lines} lines',
                    'fix': 'Consider moving to separate file or splitting'
                })
                page_data['quality_score'] -= 1
        
        page_data['code_block_count'] = len(code_blocks)
        
        # Extract concepts (technical terms, patterns, etc.)
        concepts = self._extract_concepts(content_body, page_data['title'])
        page_data['concepts'] = concepts
        
        # Word count
        page_data['word_count'] = len(re.findall(r'\b\w+\b', content_body))
        
        # Check for common content issues
        self._check_content_quality(page_id, content_body, page_data)
        
        # Determine category from path
        parts = page_id.split('/')
        if len(parts) > 1:
            page_data['category'] = parts[0]
        else:
            page_data['category'] = 'root'
        
        # Detect pattern tier if applicable
        if 'pattern-library' in page_id:
            if '🥇' in content or 'gold' in content.lower():
                page_data['tier'] = 'gold'
            elif '🥈' in content or 'silver' in content.lower():
                page_data['tier'] = 'silver'
            elif '🥉' in content or 'bronze' in content.lower():
                page_data['tier'] = 'bronze'
            else:
                page_data['tier'] = None
        
        return page_data
    
    def _normalize_internal_link(self, link_path: str, source_page_id: str) -> str:
        """Normalize internal link path"""
        # Handle anchors - remove them but keep the base path
        if '#' in link_path:
            link_path = link_path.split('#')[0]
            if not link_path:  # Just an anchor like "#overview"
                return source_page_id
        
        # Remove query parameters
        if '?' in link_path:
            link_path = link_path.split('?')[0]
        
        if not link_path:
            return source_page_id
        
        # Handle absolute paths (starting with /)
        if link_path.startswith('/'):
            # Remove leading slash - these are relative to docs root
            normalized = link_path[1:]
        else:
            # Handle relative paths
            # Convert source page ID to directory path
            source_dir = os.path.dirname(source_page_id) if source_page_id else ""
            
            # Build the full path
            if link_path.startswith('../'):
                # Go up directories
                parts = link_path.split('/')
                source_parts = source_dir.split('/') if source_dir else []
                
                # Process each ../ to go up one directory
                while parts and parts[0] == '..':
                    parts.pop(0)
                    if source_parts:
                        source_parts.pop()
                
                # Combine remaining parts
                if source_parts:
                    normalized = '/'.join(source_parts + parts)
                else:
                    normalized = '/'.join(parts)
                    
            elif link_path.startswith('./'):
                # Same directory
                normalized = os.path.join(source_dir, link_path[2:]) if source_dir else link_path[2:]
            else:
                # Relative to current directory
                normalized = os.path.join(source_dir, link_path) if source_dir else link_path
        
        # Clean up the path
        normalized = os.path.normpath(normalized).replace('\\', '/')
        
        # Remove trailing slashes
        normalized = normalized.rstrip('/')
        
        # Check if this was originally a .md file
        was_md_file = normalized.endswith('.md')
        
        # Remove .md extension if present
        if was_md_file:
            normalized = normalized[:-3]
        
        # Handle directory references - add index
        # Only add /index if:
        # 1. The original link ended with / (explicit directory)
        # 2. OR it's not a .md file AND doesn't already end with index
        if link_path.endswith('/'):
            # Explicit directory reference
            if not normalized.endswith('index'):
                normalized = f"{normalized}/index"
        elif not was_md_file and normalized:
            # Not a .md file, might be a directory
            if '.' not in os.path.basename(normalized) and not normalized.endswith('index'):
                # No extension, assume directory
                normalized = f"{normalized}/index"
        
        return normalized
    
    def _create_anchor(self, text: str) -> str:
        """Create anchor from heading text"""
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic
        text = re.sub(r'`([^`]+)`', r'\1', text)  # Code
        
        # Convert to lowercase and replace spaces/special chars
        anchor = re.sub(r'[^\w\s-]', '', text.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor.strip('-')
    
    def _extract_concepts(self, content: str, title: str) -> List[Dict[str, Any]]:
        """Extract technical concepts from content"""
        concepts = []
        
        # Pattern-based extraction
        patterns = [
            # Common distributed systems terms
            (r'\b(CAP|ACID|BASE|CQRS|CRDT|DDD|SOLID)\b', 'acronym'),
            (r'\b(microservice|monolith|serverless|container|kubernetes|docker)\w*\b', 'architecture'),
            (r'\b(circuit breaker|rate limit|load balanc|cache|shard|partition)\w*\b', 'pattern'),
            (r'\b(consensus|raft|paxos|byzantine|quorum|leader election)\b', 'algorithm'),
            (r'\b(eventual|strong|weak|causal|linearizable) consistency\b', 'consistency'),
            (r'\b(latency|throughput|availability|scalability|reliability)\b', 'metric'),
            (r'\b(AWS|GCP|Azure|Kafka|Redis|MongoDB|PostgreSQL|Elasticsearch)\b', 'technology'),
        ]
        
        found_concepts = set()
        for pattern, concept_type in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                concept_text = match.group(0).lower()
                if concept_text not in found_concepts:
                    concepts.append({
                        'label': concept_text,
                        'type': concept_type,
                        'position_weight': 1.5 if match.start() < 500 else 1.0  # Higher weight if early in doc
                    })
                    found_concepts.add(concept_text)
        
        # Add title words as concepts with high weight
        title_words = re.findall(r'\b[A-Z]\w+\b', title)
        for word in title_words:
            if len(word) > 3 and word.lower() not in found_concepts:
                concepts.append({
                    'label': word.lower(),
                    'type': 'title_term',
                    'position_weight': 2.0
                })
        
        return concepts
    
    def _check_content_quality(self, page_id: str, content: str, page_data: Dict):
        """Check for content quality issues"""
        
        # Check for TODO/FIXME/XXX
        todos = re.findall(r'\b(TODO|FIXME|XXX|HACK)\b:?\s*(.{0,50})', content, re.IGNORECASE)
        for marker, context in todos:
            self.issues_per_page[page_id].append({
                'type': 'todo_marker',
                'severity': 'info',
                'details': f'{marker}: {context.strip()}',
                'fix': 'Address TODO item or move to issue tracker'
            })
            page_data['quality_score'] -= 2
        
        # Check for broken markdown
        # Unclosed code blocks
        if content.count('```') % 2 != 0:
            self.issues_per_page[page_id].append({
                'type': 'unclosed_code_block',
                'severity': 'error',
                'details': 'Odd number of ``` markers',
                'fix': 'Close all code blocks',
                'auto_fixable': False
            })
            page_data['quality_score'] -= 10
        
        # Check for very short content
        if page_data['word_count'] < 50 and 'index' not in page_id:
            self.issues_per_page[page_id].append({
                'type': 'short_content',
                'severity': 'warning',
                'details': f'Only {page_data["word_count"]} words',
                'fix': 'Add more content or consider merging with another page'
            })
            page_data['quality_score'] -= 5
        
        # Check for very long content
        if page_data['word_count'] > 3000:
            self.issues_per_page[page_id].append({
                'type': 'long_content',
                'severity': 'info',
                'details': f'{page_data["word_count"]} words',
                'fix': 'Consider splitting into multiple pages'
            })
            page_data['quality_score'] -= 2
        
        # Check for missing structure (no headings in long content)
        if page_data['word_count'] > 500 and page_data['heading_count'] < 2:
            self.issues_per_page[page_id].append({
                'type': 'poor_structure',
                'severity': 'warning',
                'details': f'Long content ({page_data["word_count"]} words) with only {page_data["heading_count"]} headings',
                'fix': 'Add section headings for better structure'
            })
            page_data['quality_score'] -= 5
        
        # Check for placeholder content
        placeholder_patterns = [
            r'lorem ipsum',
            r'coming soon',
            r'under construction',
            r'work in progress',
            r'placeholder',
            r'TBD|TBA'
        ]
        for pattern in placeholder_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.issues_per_page[page_id].append({
                    'type': 'placeholder_content',
                    'severity': 'warning',
                    'details': f'Found placeholder text: {pattern}',
                    'fix': 'Replace with actual content'
                })
                page_data['quality_score'] -= 5
                break
        
        # Ensure quality score doesn't go below 0
        page_data['quality_score'] = max(0, page_data['quality_score'])
    
    async def validate_links_async(self, pages_data: List[Dict], max_concurrent: int = 50):
        """Validate all links asynchronously"""
        logger.info(f"Validating links for {len(pages_data)} pages...")
        
        # Collect all unique external URLs
        external_urls = set()
        internal_links = []
        
        for page_data in pages_data:
            if not page_data:
                continue
            for link in page_data.get('links', []):
                if link['is_external']:
                    external_urls.add(link['dst_url'])
                else:
                    internal_links.append((page_data['page_id'], link))
        
        # Validate internal links
        logger.info(f"Checking {len(internal_links)} internal links...")
        cursor = self.conn.cursor()
        
        for src_page, link in internal_links:
            dst_page = link['dst_page']
            
            # Check if destination page exists
            cursor.execute('SELECT page_id FROM pages WHERE page_id = ?', (dst_page,))
            exists = cursor.fetchone() is not None
            
            if not exists:
                self.issues_per_page[src_page].append({
                    'type': 'broken_internal_link',
                    'severity': 'error',
                    'details': f'Link to non-existent page: {link["dst_url"]}',
                    'fix': f'Create page {dst_page}.md or fix the link',
                    'auto_fixable': False
                })
                link['is_valid'] = False
            else:
                link['is_valid'] = True
                
                # Check anchor if present
                if link['anchor']:
                    cursor.execute(
                        'SELECT anchor FROM headings WHERE page_id = ? AND anchor = ?',
                        (dst_page, link['anchor'])
                    )
                    anchor_exists = cursor.fetchone() is not None
                    
                    if not anchor_exists:
                        self.issues_per_page[src_page].append({
                            'type': 'broken_anchor_link',
                            'severity': 'warning',
                            'details': f'Anchor #{link["anchor"]} not found in {dst_page}',
                            'fix': f'Add heading with anchor {link["anchor"]} or fix the link'
                        })
        
        # Validate external links asynchronously
        logger.info(f"Checking {len(external_urls)} unique external URLs...")
        
        async def check_url(session, url):
            try:
                async with session.head(url, timeout=5, ssl=False) as response:
                    return url, response.status, True
            except asyncio.TimeoutError:
                return url, None, False
            except Exception as e:
                # Try GET as fallback (some servers don't support HEAD)
                try:
                    async with session.get(url, timeout=5, ssl=False) as response:
                        return url, response.status, True
                except:
                    return url, None, False
        
        # Run async checks
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in external_urls:
                tasks.append(check_url(session, url))
            
            # Process in batches
            results = []
            for i in range(0, len(tasks), max_concurrent):
                batch = tasks[i:i+max_concurrent]
                batch_results = await asyncio.gather(*batch)
                results.extend(batch_results)
        
        # Store results
        url_status = {url: (status, valid) for url, status, valid in results}
        
        # Update link validity in page data
        for page_data in pages_data:
            if not page_data:
                continue
            for link in page_data.get('links', []):
                if link['is_external'] and link['dst_url'] in url_status:
                    status, valid = url_status[link['dst_url']]
                    link['is_valid'] = valid
                    link['http_status'] = status
                    
                    if not valid:
                        self.issues_per_page[page_data['page_id']].append({
                            'type': 'broken_external_link',
                            'severity': 'warning',
                            'details': f'External link unreachable: {link["dst_url"]} (status: {status})',
                            'fix': 'Update or remove the broken link'
                        })
    
    def ingest_all_pages(self, docs_dir: str = "docs"):
        """Main ingestion pipeline"""
        docs_path = Path(docs_dir)
        
        if not docs_path.exists():
            logger.error(f"Docs directory not found: {docs_path}")
            return
        
        logger.info(f"Starting ingestion from {docs_path}")
        start_time = time.time()
        
        # Discover all markdown files
        md_files = list(docs_path.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")
        
        # Analyze each page
        pages_data = []
        for md_file in md_files:
            page_data = self.analyze_page(md_file, docs_path)
            if page_data:
                pages_data.append(page_data)
                self.stats['pages_analyzed'] += 1
        
        # Run async link validation
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.validate_links_async(pages_data))
        
        # Store in database
        cursor = self.conn.cursor()
        
        for page_data in pages_data:
            if not page_data:
                continue
                
            # Insert page
            cursor.execute('''
                INSERT OR REPLACE INTO pages (
                    page_id, title, path, category, tier, last_modified, md5_hash,
                    word_count, has_frontmatter, has_toc, heading_count, link_count,
                    image_count, code_block_count, quality_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                page_data['page_id'], page_data.get('title', ''), page_data['path'],
                page_data.get('category'), page_data.get('tier'), page_data['last_modified'],
                page_data['md5_hash'], page_data['word_count'], page_data.get('has_frontmatter', False),
                page_data.get('has_toc', False), page_data['heading_count'],
                page_data['link_count'], page_data['image_count'],
                page_data['code_block_count'], page_data['quality_score']
            ))
            
            # Insert headings
            for i, heading in enumerate(page_data['headings']):
                cursor.execute('''
                    INSERT OR REPLACE INTO headings (page_id, level, text, anchor, position)
                    VALUES (?, ?, ?, ?, ?)
                ''', (page_data['page_id'], heading['level'], heading['text'],
                     heading['anchor'], i))
            
            # Insert links
            for link in page_data['links']:
                cursor.execute('''
                    INSERT OR REPLACE INTO links (
                        src_page, dst_page, dst_url, is_external, is_valid,
                        anchor, link_text, http_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    page_data['page_id'], link.get('dst_page'), link['dst_url'],
                    link['is_external'], link.get('is_valid'), link.get('anchor'),
                    link.get('link_text'), link.get('http_status')
                ))
            
            # Insert concepts
            for concept in page_data['concepts']:
                cursor.execute('''
                    INSERT OR IGNORE INTO concepts (label, concept_type)
                    VALUES (?, ?)
                ''', (concept['label'], concept['type']))
                
                cursor.execute('SELECT concept_id FROM concepts WHERE label = ?', (concept['label'],))
                concept_id = cursor.fetchone()[0]
                
                cursor.execute('''
                    INSERT OR REPLACE INTO page_concepts (page_id, concept_id, position_weight)
                    VALUES (?, ?, ?)
                ''', (page_data['page_id'], concept_id, concept.get('position_weight', 1.0)))
            
            # Insert issues
            for issue in self.issues_per_page[page_data['page_id']]:
                cursor.execute('''
                    INSERT INTO issues (
                        page_id, issue_type, severity, details, suggested_fix, auto_fixable
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    page_data['page_id'], issue['type'], issue.get('severity', 'warning'),
                    issue.get('details'), issue.get('fix'), issue.get('auto_fixable', False)
                ))
        
        # Update metrics
        cursor.execute('SELECT COUNT(*) FROM pages')
        total_pages = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM issues')
        total_issues = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM issues WHERE severity = "error"')
        error_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(quality_score) FROM pages')
        avg_quality = cursor.fetchone()[0]
        
        metrics = {
            'total_pages': total_pages,
            'total_issues': total_issues,
            'error_count': error_count,
            'average_quality_score': avg_quality,
            'ingestion_time': time.time() - start_time
        }
        
        for name, value in metrics.items():
            cursor.execute('''
                INSERT OR REPLACE INTO metrics (metric_name, metric_value)
                VALUES (?, ?)
            ''', (name, value))
        
        self.conn.commit()
        
        # Print summary
        logger.info(f"""
        =====================================
        Ingestion Complete
        =====================================
        Pages analyzed: {total_pages}
        Total issues found: {total_issues}
        Critical errors: {error_count}
        Average quality score: {avg_quality:.1f}/100
        Time taken: {metrics['ingestion_time']:.2f} seconds
        
        Database: {self.db_path}
        =====================================
        """)
        
        return metrics
    
    def generate_fix_report(self, output_file: str = "fixes_to_apply.md"):
        """Generate detailed fix report"""
        cursor = self.conn.cursor()
        
        # Get all issues grouped by type and severity
        cursor.execute('''
            SELECT issue_type, severity, COUNT(*) as count,
                   GROUP_CONCAT(DISTINCT page_id) as sample_pages
            FROM issues
            GROUP BY issue_type, severity
            ORDER BY 
                CASE severity
                    WHEN 'error' THEN 1
                    WHEN 'warning' THEN 2
                    WHEN 'info' THEN 3
                END,
                count DESC
        ''')
        
        issues_by_type = cursor.fetchall()
        
        # Get auto-fixable issues
        cursor.execute('''
            SELECT issue_type, COUNT(*) as count
            FROM issues
            WHERE auto_fixable = 1
            GROUP BY issue_type
        ''')
        
        auto_fixable = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Generate report
        report = []
        report.append("# Documentation Issues and Fixes\n")
        report.append(f"Generated: {datetime.now().isoformat()}\n\n")
        
        # Summary
        cursor.execute('SELECT COUNT(*) FROM pages')
        total_pages = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM issues')
        total_issues = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT page_id) FROM issues')
        pages_with_issues = cursor.fetchone()[0]
        
        report.append("## Summary\n\n")
        report.append(f"- Total pages: {total_pages}\n")
        report.append(f"- Pages with issues: {pages_with_issues} ({pages_with_issues/total_pages*100:.1f}%)\n")
        report.append(f"- Total issues: {total_issues}\n")
        report.append(f"- Auto-fixable issues: {sum(auto_fixable.values())}\n\n")
        
        # Issues by severity
        report.append("## Issues by Severity\n\n")
        
        for severity in ['error', 'warning', 'info']:
            cursor.execute('SELECT COUNT(*) FROM issues WHERE severity = ?', (severity,))
            count = cursor.fetchone()[0]
            if count > 0:
                report.append(f"### {severity.upper()}: {count} issues\n\n")
                
                cursor.execute('''
                    SELECT issue_type, COUNT(*) as count
                    FROM issues
                    WHERE severity = ?
                    GROUP BY issue_type
                    ORDER BY count DESC
                    LIMIT 10
                ''', (severity,))
                
                for row in cursor.fetchall():
                    issue_type, count = row
                    auto_fix = f" (🤖 {auto_fixable.get(issue_type, 0)} auto-fixable)" if issue_type in auto_fixable else ""
                    report.append(f"- **{issue_type}**: {count} occurrences{auto_fix}\n")
                report.append("\n")
        
        # Detailed fixes by issue type
        report.append("## Detailed Fixes\n\n")
        
        for row in issues_by_type[:20]:  # Top 20 issue types
            issue_type = row['issue_type']
            severity = row['severity']
            count = row['count']
            sample_pages = row['sample_pages'].split(',')[:3]  # First 3 examples
            
            report.append(f"### {issue_type} ({count} occurrences)\n\n")
            report.append(f"**Severity**: {severity}\n\n")
            
            # Get a sample issue for details
            cursor.execute('''
                SELECT details, suggested_fix, page_id
                FROM issues
                WHERE issue_type = ?
                LIMIT 1
            ''', (issue_type,))
            
            sample = cursor.fetchone()
            if sample:
                report.append(f"**Example**: {sample['details']}\n\n")
                report.append(f"**Fix**: {sample['suggested_fix']}\n\n")
                report.append(f"**Sample pages affected**:\n")
                for page in sample_pages:
                    report.append(f"- `{page}`\n")
                report.append("\n")
        
        # Pages with lowest quality scores
        report.append("## Pages Needing Most Attention\n\n")
        
        cursor.execute('''
            SELECT p.page_id, p.title, p.quality_score, COUNT(i.issue_id) as issue_count
            FROM pages p
            LEFT JOIN issues i ON i.page_id = p.page_id
            GROUP BY p.page_id
            ORDER BY p.quality_score ASC
            LIMIT 20
        ''')
        
        for row in cursor.fetchall():
            report.append(f"- **{row['title']}** (`{row['page_id']}`): Quality {row['quality_score']:.0f}/100, {row['issue_count']} issues\n")
        
        # Write report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(report))
        
        logger.info(f"Fix report generated: {output_file}")
        
        return output_file

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ultimate knowledge graph builder')
    parser.add_argument('--docs-dir', default='docs', help='Documentation directory')
    parser.add_argument('--db', default='knowledge_graph_ultimate.db', help='Database path')
    parser.add_argument('--report', action='store_true', help='Generate fix report')
    
    args = parser.parse_args()
    
    # Initialize knowledge graph
    kg = OptimizedKnowledgeGraph(args.db)
    
    # Run ingestion
    metrics = kg.ingest_all_pages(args.docs_dir)
    
    # Generate fix report
    if args.report or True:  # Always generate report
        kg.generate_fix_report()
    
    kg.conn.close()

if __name__ == '__main__':
    main()
# DStudio Knowledge Graph System

## Overview
The Knowledge Graph System provides comprehensive analysis and quality monitoring for the DStudio documentation. It builds a SQLite database with full-text search capabilities to track pages, links, concepts, and quality metrics.

## Main Components

### Core System
- **`knowledge_graph_ultimate.py`** - Main analyzer that builds the knowledge graph database
- **`knowledge_graph_ultimate.db`** - SQLite database containing all analyzed data

### Key Features
- Page analysis with quality scoring (0-100 scale)
- Internal/external link validation
- Concept extraction using TF-IDF
- Heading hierarchy analysis
- Issue detection (broken links, invalid frontmatter, unclosed code blocks, etc.)
- Full-text search with FTS5

## Usage

### Build/Refresh Knowledge Graph
```bash
python3 knowledge_graph_ultimate.py --docs-dir /home/deepak/DStudio/docs
```

### Generate Fix Report
```bash
python3 knowledge_graph_ultimate.py --docs-dir /home/deepak/DStudio/docs --report
```

## Current Status (as of 2025-08-07)

### Metrics
- **Total Pages**: 640
- **Average Quality Score**: 94.7/100
- **Link Success Rate**: 88.05%
- **Critical Issues**: All resolved

### Recent Improvements
- Fixed 52 invalid frontmatter issues
- Closed 18 unclosed code blocks
- Updated 4 broken external links
- Enhanced 8 F-grade pages with 900% content growth
- Added TOCs to 40+ long pages

### Remaining Items
- 5,866 broken internal links (mostly template placeholders and missing content pages)
- Content creation needed for missing pages
- Minor cosmetic issues (heading hierarchies, duplicate anchors)

## Database Schema

The knowledge graph uses SQLite with the following structure:

```sql
-- Pages table with FTS5
CREATE VIRTUAL TABLE pages USING fts5(
    path UNINDEXED,
    title,
    description,
    content,
    category,
    tier,
    status,
    frontmatter,
    file_hash UNINDEXED,
    last_modified UNINDEXED,
    quality_score UNINDEXED
);

-- Links table
CREATE TABLE links (
    source_path TEXT,
    target_path TEXT,
    link_type TEXT,
    link_text TEXT,
    is_valid INTEGER,
    is_external INTEGER,
    status_code INTEGER,
    PRIMARY KEY (source_path, target_path)
);

-- Concepts table
CREATE TABLE concepts (
    concept TEXT PRIMARY KEY,
    frequency INTEGER,
    pages TEXT
);

-- Metadata table
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

## Output Files

| File | Description |
|------|-------------|
| `dstudio_knowledge.db` | SQLite database with full graph |
| `knowledge_graph.json` | JSON export of graph structure |
| `knowledge_graph_ld.json` | JSON-LD semantic web format |
| `knowledge_graph_analysis.json` | Analysis results and metrics |

## Use Cases

### 1. Documentation Quality Assessment
```bash
# Build graph and check quality scores
python3 knowledge_graph_ultimate.py
python3 query_knowledge_graph.py
```

### 2. Find Orphaned Pages
```python
# In Python script
import sqlite3
conn = sqlite3.connect('dstudio_knowledge.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT path FROM pages 
    WHERE path NOT IN (SELECT DISTINCT target_path FROM links)
""")
orphaned = cursor.fetchall()
```

### 3. Link Validation
The ultimate version performs async validation of all links:
- Internal links: Checked against file system
- External links: HTTP HEAD requests with timeout
- Results stored in database for analysis

### 4. Content Similarity
Using the advanced version's TF-IDF features:
```python
# Find similar pages based on content
similar_pages = graph.find_similar_pages("pattern-library/scaling/caching.md", top_k=5)
```

### 5. Export for External Tools
```bash
# Generate JSON-LD for import into graph databases
python3 knowledge_graph_ultimate.py
# Output: knowledge_graph_ld.json

# Can be imported into:
# - Neo4j
# - Amazon Neptune
# - GraphDB
# - Apache Jena
```

## Performance Considerations

- **Incremental Updates**: The ultimate version uses MD5 hashing to only update changed files
- **Async Operations**: Link validation runs concurrently for faster processing
- **FTS5 Indexing**: Full-text search is optimized with SQLite FTS5
- **Batch Processing**: Database operations are batched for efficiency

## Dependencies

```txt
# Required
pyyaml>=6.0
pathlib
sqlite3 (built-in)
json (built-in)
asyncio (built-in)

# Optional (for advanced features)
networkx>=2.6      # Graph algorithms
aiohttp>=3.8       # Async HTTP requests
rich>=10.0         # Progress bars
sentence-transformers  # Semantic embeddings (ML version)
scikit-learn      # TF-IDF vectorization (ML version)
```

## Future Enhancements

1. **GraphQL API**: Query interface for the knowledge graph
2. **Real-time Updates**: File watcher for automatic graph updates
3. **Visualization**: D3.js based interactive graph viewer
4. **Advanced Queries**: Natural language query interface
5. **Quality Recommendations**: ML-based content improvement suggestions

## Troubleshooting

### Database Locked Error
```bash
# Remove lock if process was interrupted
rm dstudio_knowledge.db-journal
```

### Memory Issues with Large Docs
```python
# Adjust batch size in ultimate version
BATCH_SIZE = 50  # Reduce from 100
```

### Slow External Link Validation
```python
# Adjust timeout and concurrent requests
TIMEOUT = 5  # Reduce from 10
MAX_CONCURRENT = 10  # Reduce from 20
```
# Knowledge Graph Tools

## Overview
This directory contains tools for building, querying, and analyzing a knowledge graph of the DStudio documentation. The knowledge graph provides semantic understanding of documentation structure, relationships, and quality metrics.

## Scripts

### 🚀 Production Ready

#### `knowledge_graph_ultimate.py`
**The recommended production implementation**

Features:
- SQLite database with FTS5 for full-text search
- Async link validation for performance
- Incremental updates using MD5 hashing
- JSON-LD export for semantic web compatibility
- Comprehensive quality scoring
- Progress tracking with rich output

Usage:
```bash
# Build or update the knowledge graph
python3 knowledge_graph_ultimate.py

# The script will:
# 1. Create/update dstudio_knowledge.db
# 2. Validate all internal and external links
# 3. Generate quality scores
# 4. Export JSON-LD representation
```

#### `query_knowledge_graph.py`
**Query interface for the knowledge graph database**

Features:
- Statistical analysis of documentation
- Link relationship queries
- Quality score reporting
- Orphaned page detection

Usage:
```bash
# Get comprehensive statistics
python3 query_knowledge_graph.py

# Query specific aspects (if CLI args supported)
python3 query_knowledge_graph.py --orphaned
python3 query_knowledge_graph.py --broken-links
```

#### `test_knowledge_graph.py`
**Test suite for knowledge graph implementation**

Features:
- Unit tests for link normalization
- Path resolution testing
- Graph integrity validation

Usage:
```bash
# Run all tests
python3 test_knowledge_graph.py

# Run with verbose output
python3 -v test_knowledge_graph.py
```

### 📚 Historical Versions (Reference Only)

#### `knowledge_graph_advanced.py`
**ML-enhanced version with semantic features**

Features:
- TF-IDF vectorization for content similarity
- Semantic embeddings (requires sentence-transformers)
- NetworkX graph algorithms
- LLM-optimized analysis

Status: SUPERSEDED by ultimate version

#### `knowledge_graph_builder.py`
**Original implementation**

Features:
- Basic graph construction
- Simple link validation
- Navigation structure analysis

Status: SUPERSEDED - kept for reference

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
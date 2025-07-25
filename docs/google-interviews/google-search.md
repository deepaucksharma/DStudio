# Design Google Search

## Problem Statement

"Design a web search engine like Google Search that can index the entire web, serve results in under 100ms, and handle billions of queries per day."

## Clarifying Questions

1. **Scope**
   - Web search only or include images, videos, news?
   - English only or multilingual?
   - Just search or also features like autocomplete, spell check?

2. **Scale**
   - Number of web pages? (Billions)
   - Queries per second? (100K+ QPS)
   - Index update frequency? (Continuous)

3. **Requirements**
   - Latency target? (<100ms p99)
   - Freshness requirements? (News: minutes, general: days)
   - Ranking factors? (Relevance, authority, freshness)

## Requirements Summary

### Functional Requirements
- Web crawling and indexing
- Query processing and ranking
- Result serving with snippets
- Spell correction and suggestions
- Safe search and spam filtering

### Non-Functional Requirements
- **Scale**: 100B+ web pages, 100K+ QPS
- **Latency**: <100ms for 99% of queries
- **Availability**: 99.99% uptime
- **Freshness**: Continuous updates

### Out of Scope
- Image/video search
- Personalization
- Ads system
- Knowledge graph

## Scale Estimation

### Data Size
```
Web pages: 100 billion
Average page size: 100KB
Total raw data: 10 PB

After processing:
- Text content: 2 PB
- Index size: 500 TB
- Link graph: 100 TB
```

### Query Volume
```
Daily queries: 8.5 billion
Peak QPS: 100,000
Average query: 3 words
Results per page: 10
```

### Resource Requirements
```
Crawling: 10,000 servers
Indexing: 50,000 servers
Serving: 100,000 servers
Storage: 10 PB distributed
```

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Internet/Web                          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Crawling System                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │Scheduler│  │ Crawler │  │ Parser  │  │Deduper  │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Indexing Pipeline                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │Doc Store│  │ Indexer │  │Link Proc│  │Ranking  │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Serving System                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │   GFE   │  │  Query  │  │ Mixer   │  │ Snippet │   │
│  │         │  │ Rewrite │  │         │  │   Gen   │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Detailed Component Design

### 1. Crawling System

**URL Frontier**
```python
class URLFrontier:
    def __init__(self):
        self.priority_queues = {}  # domain -> priority queue
        self.politeness_delay = {}  # domain -> last_crawl_time
        self.robots_cache = {}      # domain -> robots.txt rules
    
    def get_next_url(self):
# Respect politeness and priorities
        for domain, queue in self.priority_queues.items():
            if self.can_crawl(domain):
                return queue.pop()
        return None
```

**Distributed Crawling**
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  URL Queue   │────▶│   Crawler    │────▶│  Doc Store   │
│  (Bigtable)  │     │  (Stateless) │     │  (Colossus)  │
└──────────────┘     └──────────────┘     └──────────────┘
        ▲                                           │
        │                                           │
        └───────────────────────────────────────────┘
                    New URLs discovered
```

**Duplicate Detection**
- SimHash for near-duplicate detection
- Content fingerprinting
- URL canonicalization
- Bloom filters for seen URLs

### 2. Indexing System

**Inverted Index Structure**
```
Term    | Document List (sorted by doc_id)
--------|----------------------------------------
google  | [(d1,5,0.9), (d2,3,0.7), (d3,1,0.5)...]
search  | [(d1,2,0.8), (d4,4,0.6), (d5,1,0.4)...]
engine  | [(d2,1,0.7), (d3,3,0.8), (d6,2,0.5)...]

Format: (doc_id, frequency, importance_score)
```

**MapReduce Indexing**
```
Map Phase:
  Input: (url, content)
  Output: (word, (url, position, context))

Shuffle: Group by word

Reduce Phase:
  Input: (word, [(url1, pos1), (url2, pos2)...])
  Output: (word, compressed_posting_list)
```

**Index Sharding**
```
Document-based sharding:
- Shard 1: doc_ids 0-1M
- Shard 2: doc_ids 1M-2M
- ...

Term-based sharding:
- Shard A: terms starting with a-d
- Shard B: terms starting with e-h
- ...
```

### 3. Ranking System

**PageRank Computation**
```python
def compute_pagerank(links, iterations=10, damping=0.85):
    N = len(links)
    ranks = {page: 1.0/N for page in links}
    
    for _ in range(iterations):
        new_ranks = {}
        for page in links:
            rank = (1 - damping) / N
            for source in get_pages_linking_to(page):
                rank += damping * ranks[source] / len(links[source])
            new_ranks[page] = rank
        ranks = new_ranks
    
    return ranks
```

**Ranking Signals** (500+ factors)
1. **Query-Document Relevance**
   - TF-IDF score
   - BM25 score
   - Proximity of query terms
   - Semantic similarity

2. **Document Quality**
   - PageRank
   - Domain authority
   - Freshness
   - Click-through rate

3. **Query Understanding**
   - Intent classification
   - Entity recognition
   - Query expansion
   - Spell correction

### 4. Query Processing

**Query Flow**
```
User Query
    │
    ▼
┌─────────────┐
│   Query     │ ← Spell check, expansion
│  Rewriter   │
└─────────────┘
    │
    ▼
┌─────────────┐
│   Query     │ ← Parse and analyze
│  Processor  │
└─────────────┘
    │
    ├──────────────┬──────────────┬──────────────┐
    ▼              ▼              ▼              ▼
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│Index   │    │Index   │    │Index   │    │Index   │
│Shard 1 │    │Shard 2 │    │Shard 3 │    │Shard N │
└────────┘    └────────┘    └────────┘    └────────┘
    │              │              │              │
    └──────────────┴──────────────┴──────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Mixer     │ ← Merge and rank
                    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Results   │
                    └─────────────┘
```

**Query Rewriting**
```python
class QueryRewriter:
    def rewrite(self, query):
# Spell correction
        query = self.spell_correct(query)
        
# Synonym expansion
        query = self.expand_synonyms(query)
        
# Entity recognition
        entities = self.extract_entities(query)
        
# Intent classification
        intent = self.classify_intent(query)
        
        return RewrittenQuery(query, entities, intent)
```

### 5. Serving Infrastructure

**Caching Strategy**
```
┌─────────────────┐
│  Browser Cache  │ ← 1 hour TTL
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   CDN Cache     │ ← Popular queries
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Result Cache   │ ← Full result pages
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Posting Cache   │ ← Inverted index chunks
└─────────────────┘
```

**Load Balancing**
```
                    ┌─────────────┐
                    │    GFE      │
                    │  (Global)   │
                    └─────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Datacenter │    │  Datacenter │    │  Datacenter │
│   US-East   │    │   US-West   │    │    Europe   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Data Models

### Document Storage
```protobuf
message WebDocument {
  string url = 1;
  string title = 2;
  string content = 3;
  repeated string outgoing_links = 4;
  int64 crawl_timestamp = 5;
  bytes content_hash = 6;
  float page_rank = 7;
  map<string, string> metadata = 8;
}
```

### Inverted Index Entry
```protobuf
message PostingList {
  string term = 1;
  repeated Posting postings = 2;
}

message Posting {
  int64 doc_id = 1;
  repeated int32 positions = 2;
  float term_frequency = 3;
  float boost_factor = 4;
}
```

## Optimizations

### 1. Index Compression
```python
def compress_posting_list(postings):
# Delta encoding for doc_ids
    prev_id = 0
    compressed = []
    for doc_id, positions in postings:
        delta = doc_id - prev_id
        compressed.append((delta, positions))
        prev_id = doc_id
    
# Variable byte encoding
    return variable_byte_encode(compressed)
```

### 2. Early Termination
- WAND algorithm for top-k retrieval
- Skip pointers in posting lists
- Impact-ordered indexes
- Tiered indexes (quality tiers)

### 3. Caching Strategy
```
Cache hit rates:
- Query cache: 30-40%
- Document cache: 60-70%
- Posting list cache: 80-90%

Cache sizes:
- Query cache: 100 GB
- Document cache: 1 TB
- Posting cache: 10 TB
```

## Challenges and Solutions

### 1. Crawl Politeness
**Problem**: Don't overwhelm websites
**Solution**: 
- Distributed crawler with domain-based queuing
- Configurable delays per domain
- Respect robots.txt
- Adaptive crawl rates

### 2. Spam Detection
**Problem**: Low-quality and spam content
**Solution**:
- Machine learning classifiers
- Link spam detection
- Content quality signals
- Manual review for edge cases

### 3. Query Understanding
**Problem**: Ambiguous queries
**Solution**:
- Query classification
- Entity disambiguation
- User location context
- Search history (if permitted)

### 4. Real-time Updates
**Problem**: Fresh content for news/events
**Solution**:
- Caffeine indexing system
- Incremental index updates
- Priority crawling for news sites
- Real-time indexing pipeline

## Monitoring and Operations

### Key Metrics
```
Latency metrics:
- p50: 50ms
- p95: 80ms
- p99: 100ms

Quality metrics:
- Click-through rate
- Dwell time
- Query reformulation rate
- User satisfaction

System metrics:
- Index freshness
- Crawl coverage
- Spam rate
- Error rate
```

### Debugging Tools
- Query debugging UI
- Ranking explanation
- A/B testing framework
- Real-time monitoring dashboards

## Security and Privacy

### Security Measures
- HTTPS everywhere
- SafeSearch filtering
- Malware detection
- Phishing protection

### Privacy Considerations
- No personal data in main index
- Encrypted queries
- No search history by default
- Regional data compliance

## Evolution and Future

### Recent Improvements
1. **BERT Integration**: Better query understanding
2. **Mobile-First Indexing**: Prioritize mobile content
3. **Core Web Vitals**: Page experience signals
4. **Passage Indexing**: Index specific passages

### Future Directions
1. **Neural Ranking**: Deep learning for relevance
2. **Conversational Search**: Multi-turn interactions
3. **Visual Search**: Search by image
4. **Voice Search**: Natural language queries

## Interview Tips

1. **Start Simple**: Basic crawl-index-serve architecture
2. **Address Scale Early**: Mention sharding and distribution
3. **Focus on Latency**: Caching and optimization strategies
4. **Consider Freshness**: Real-time indexing for news
5. **Don't Forget Quality**: Ranking and spam detection

## Common Follow-up Questions

1. **"How would you handle JavaScript-heavy sites?"**
   - Headless browser rendering
   - JavaScript execution in crawler
   - Progressive enhancement detection

2. **"How do you update the index without downtime?"**
   - Blue-green deployment
   - Incremental index updates
   - Version-based serving

3. **"How would you personalize results?"**
   - User profile signals
   - Location-based ranking
   - Privacy-preserving personalization

4. **"How do you test search quality?"**
   - Human raters
   - A/B testing
   - Automated quality metrics
   - Side-by-side comparisons
# Google System Design Practice Problems

## Overview

This collection contains 15 carefully curated practice problems organized by difficulty level. Each problem is designed to simulate real Google system design interview scenarios with a 45-minute time constraint.

## Study Schedule

### Week 1-2: Foundation Building
- **Days 1-3**: Review fundamental concepts (scaling, caching, databases)
- **Days 4-7**: Complete Beginner Level problems (1 per day)
- **Days 8-10**: Review solutions, identify weak areas
- **Days 11-14**: Redo problems focusing on weak areas

### Week 3-4: Skill Development
- **Days 15-17**: Intermediate problems 1-3
- **Days 18-19**: Review and practice estimation
- **Days 20-22**: Intermediate problems 4-5
- **Days 23-24**: Mock interviews with peers
- **Days 25-28**: Review all intermediate solutions

### Week 5-6: Advanced Preparation
- **Days 29-31**: Advanced problems 1-2
- **Days 32-33**: Deep dive on trade-offs
- **Days 34-36**: Advanced problems 3-4
- **Days 37-38**: Advanced problem 5
- **Days 39-42**: Full mock interviews

---

## Beginner Level Problems

### 1. URL Shortener (Google's goo.gl)

**Problem Statement**: Design a URL shortening service like Google's discontinued goo.gl service that converts long URLs into short ones.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Functional requirements: Shorten URL, redirect, custom aliases
- Scale: 100M URLs/day, 10:1 read/write ratio
- Analytics: Click tracking, geographic data
- Expiration: URLs expire after 2 years of inactivity

**Minimum Viable Solution**:
```
Components:
1. API Gateway → Load Balancer
2. Application Servers (stateless)
3. Cache Layer (Redis)
4. Database (NoSQL for URLs, SQL for analytics)
5. CDN for redirects

Key Design Decisions:
- Base62 encoding for short URLs (6-7 characters)
- Pre-generate keys vs. hash+collision handling
- Separate read and write paths
- Cache popular URLs
```

**Expected Follow-ups**:
- How to handle custom URLs?
- How to prevent abuse/spam?
- How to implement analytics without impacting latency?
- How to handle URL preview feature?

**Common Mistakes**:
- Not considering cache invalidation
- Using MD5 without handling collisions
- Over-engineering the analytics pipeline
- Not discussing data expiration strategy

**Evaluation Criteria**:
- Clear capacity estimation ✓
- Appropriate database choice ✓
- Caching strategy ✓
- Handling edge cases ✓

---

### 2. Distributed Counter

**Problem Statement**: Design a system to count events (like video views) across Google's global infrastructure with eventual consistency.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Count events from millions of sources
- Near real-time updates (within 1 minute)
- Handle 1M events/second
- Queryable by time ranges

**Minimum Viable Solution**:
```
Architecture:
1. Event collectors (regional)
2. Message queue (Pub/Sub)
3. Stream processors (Apache Beam)
4. Time-series database
5. Query service with caching

Key Insights:
- Use tumbling windows for aggregation
- Regional aggregation before global
- Approximate counting algorithms for scale
- Hot partition handling
```

**Expected Follow-ups**:
- How to handle exactly-once counting?
- How to deal with late-arriving events?
- How to implement rate limiting?
- How to handle counter resets?

**Common Mistakes**:
- Using strong consistency unnecessarily
- Not considering time window boundaries
- Ignoring hot key problems
- Over-relying on database increments

**Evaluation Criteria**:
- Understanding of distributed counting challenges ✓
- Appropriate use of streaming systems ✓
- Handling of edge cases ✓
- Performance optimization ✓

---

### 3. Simple Key-Value Store

**Problem Statement**: Design a distributed key-value store for Google Cloud Platform customers with strong consistency.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Get, Put, Delete operations
- Strong consistency
- 99.99% availability
- Handle 100TB of data

**Minimum Viable Solution**:
```
Design:
1. Consistent hashing for data distribution
2. Replication (3 replicas)
3. Consensus protocol (Raft/Paxos)
4. Write-ahead logging
5. Periodic compaction

Key Features:
- Partition tolerance via replication
- Leader election per partition
- Synchronous replication
- Background compaction
```

**Expected Follow-ups**:
- How to handle hot keys?
- How to implement transactions?
- How to handle node failures during writes?
- How to implement backup/restore?

**Common Mistakes**:
- Confusing eventual with strong consistency
- Not explaining consensus protocol
- Ignoring compaction needs
- Missing failure scenarios

**Evaluation Criteria**:
- Clear consistency model ✓
- Proper replication strategy ✓
- Failure handling ✓
- Scaling approach ✓

---

### 4. Rate Limiter

**Problem Statement**: Design a distributed rate limiting service for Google APIs that can handle millions of API keys.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Multiple rate limit tiers (requests/second, minute, hour)
- Distributed across regions
- Sub-millisecond latency
- Fair sharing during overload

**Minimum Viable Solution**:
```
Components:
1. Local rate limiter (token bucket)
2. Regional aggregator
3. Global coordinator (lazy sync)
4. Redis for distributed state
5. Configuration service

Algorithms:
- Token bucket for flexibility
- Sliding window for accuracy
- Local cache with TTL
- Probabilistic sync for scale
```

**Expected Follow-ups**:
- How to handle burst traffic?
- How to implement different strategies per API?
- How to handle clock skew?
- How to provide rate limit headers?

**Common Mistakes**:
- Using only centralized approach
- Not considering latency requirements
- Missing distributed coordination
- Ignoring configuration updates

**Evaluation Criteria**:
- Algorithm selection reasoning ✓
- Distributed system understanding ✓
- Performance optimization ✓
- Edge case handling ✓

---

### 5. Notification System

**Problem Statement**: Design a notification system for Google products that can send push notifications, emails, and SMS.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Multiple channels (push, email, SMS)
- 10M notifications/hour
- Delivery guarantees
- User preferences

**Minimum Viable Solution**:
```
Architecture:
1. API layer for notification submission
2. Message queue (separate per channel)
3. Channel-specific workers
4. Delivery status tracking
5. Retry mechanism

Key Design Points:
- Template service for content
- Priority queues
- Rate limiting per user
- Delivery receipts
```

**Expected Follow-ups**:
- How to handle user preferences?
- How to implement notification grouping?
- How to ensure no duplicates?
- How to handle provider failures?

**Common Mistakes**:
- Single queue for all channels
- No delivery confirmation
- Missing rate limiting
- Poor template design

**Evaluation Criteria**:
- Multi-channel architecture ✓
- Reliability mechanisms ✓
- Scale considerations ✓
- User experience focus ✓

---

## Intermediate Level Problems

### 6. Google Forms

**Problem Statement**: Design Google Forms to handle form creation, submission, and real-time collaboration.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Form builder with 20+ field types
- Real-time collaboration
- 1M forms, 100M submissions/day
- Analytics and export features

**Minimum Viable Solution**:
```
System Design:
1. Frontend (React) with offline support
2. WebSocket for real-time updates
3. Operational Transform for collaboration
4. Document store for forms
5. Time-series DB for responses
6. Analytics pipeline (Dataflow)

Key Challenges:
- Conflict resolution in collaboration
- Schema evolution
- Response validation
- Export at scale
```

**Expected Follow-ups**:
- How to handle form versioning?
- How to implement conditional logic?
- How to prevent spam submissions?
- How to handle file uploads?

**Common Mistakes**:
- Not addressing collaboration conflicts
- Using SQL for flexible schemas
- Missing offline capabilities
- Poor export design

**Evaluation Criteria**:
- Collaboration mechanism ✓
- Appropriate storage choices ✓
- Scale handling ✓
- Feature completeness ✓

---

### 7. Google Keep (Note-taking)

**Problem Statement**: Design Google Keep with support for notes, lists, images, and real-time sync across devices.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Rich content (text, images, drawings)
- Real-time sync
- Offline support
- Search within images (OCR)

**Minimum Viable Solution**:
```
Architecture:
1. Client apps with local SQLite
2. Sync service using vector clocks
3. Blob storage for media
4. Search index (Elasticsearch)
5. OCR pipeline for images

Sync Strategy:
- Incremental sync with checksums
- Conflict resolution (last-write-wins)
- Background sync queue
- Compression for media
```

**Expected Follow-ups**:
- How to handle collaborative notes?
- How to implement reminders?
- How to optimize for battery life?
- How to handle large attachments?

**Common Mistakes**:
- Ignoring offline complexity
- No conflict resolution strategy
- Missing search architecture
- Poor media handling

**Evaluation Criteria**:
- Sync mechanism design ✓
- Offline-first approach ✓
- Search implementation ✓
- Mobile optimization ✓

---

### 8. Google News Aggregator

**Problem Statement**: Design a news aggregation system that collects, deduplicates, and personalizes news from thousands of sources.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Crawl 10K news sources
- Deduplicate similar stories
- Personalized feed for 100M users
- Real-time updates

**Minimum Viable Solution**:
```
Pipeline:
1. Distributed crawler (Scrapy cluster)
2. Content extraction (Boilerpipe)
3. Deduplication (MinHash/LSH)
4. Topic modeling (LDA)
5. Personalization (collaborative filtering)
6. Serving layer with edge caching

Key Algorithms:
- SimHash for near-duplicate detection
- TF-IDF for relevance
- Matrix factorization for recommendations
- Temporal decay for freshness
```

**Expected Follow-ups**:
- How to handle paywalled content?
- How to detect fake news?
- How to handle multiple languages?
- How to optimize for engagement?

**Common Mistakes**:
- No deduplication strategy
- Ignoring crawl politeness
- Missing personalization
- Poor freshness handling

**Evaluation Criteria**:
- Crawling architecture ✓
- Deduplication approach ✓
- ML pipeline design ✓
- Serving optimization ✓

---

### 9. Google Translate (Basic)

**Problem Statement**: Design a simplified version of Google Translate supporting 10 languages with text translation.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Text translation API
- 1M requests/minute
- <200ms latency
- Translation quality feedback

**Minimum Viable Solution**:
```
Components:
1. API Gateway with rate limiting
2. Translation service cluster
3. Model serving (TensorFlow Serving)
4. Cache layer for common phrases
5. Feedback collection system

Optimizations:
- Language detection service
- Phrase-level caching
- Model sharding by language pair
- CDN for static translations
```

**Expected Follow-ups**:
- How to handle model updates?
- How to implement offline translation?
- How to handle document translation?
- How to collect training data?

**Common Mistakes**:
- Not caching translations
- Ignoring model serving complexity
- Missing language detection
- Poor capacity planning

**Evaluation Criteria**:
- API design quality ✓
- Caching strategy ✓
- ML serving approach ✓
- Latency optimization ✓

---

### 10. Chrome Sync

**Problem Statement**: Design Chrome's sync system for bookmarks, history, passwords, and settings across devices.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Sync 5 data types across devices
- End-to-end encryption
- Conflict resolution
- 500M users

**Minimum Viable Solution**:
```
Sync Architecture:
1. Client-side encryption layer
2. Sync server with user sharding
3. Conflict resolution engine
4. Push notification service
5. Backup service

Key Design Points:
- Merkle trees for efficient sync
- Three-way merge for conflicts
- Incremental sync with timestamps
- Selective sync by data type
```

**Expected Follow-ups**:
- How to handle password encryption?
- How to implement sync pausing?
- How to handle account recovery?
- How to deal with storage limits?

**Common Mistakes**:
- Weak encryption design
- No conflict resolution
- Ignoring partial sync
- Missing versioning

**Evaluation Criteria**:
- Security considerations ✓
- Sync protocol design ✓
- Conflict handling ✓
- Scale approach ✓

---

## Advanced Level Problems

### 11. Google Scholar

**Problem Statement**: Design Google Scholar to index, rank, and search academic papers with citation tracking.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Index 200M papers
- Citation graph analysis
- Author disambiguation
- Real-time search

**Minimum Viable Solution**:
```
System Architecture:
1. Distributed crawler for repositories
2. PDF processing pipeline
3. Citation extraction system
4. Graph database for citations
5. Search index with ranking
6. Author resolution service

Complex Features:
- PageRank for papers (impact factor)
- Fuzzy matching for citations
- ML for author disambiguation
- Incremental index updates
```

**Expected Follow-ups**:
- How to handle PDF parsing at scale?
- How to merge duplicate papers?
- How to calculate h-index efficiently?
- How to detect citation manipulation?

**Common Mistakes**:
- Ignoring PDF complexity
- No citation graph design
- Missing author disambiguation
- Poor ranking algorithm

**Evaluation Criteria**:
- Graph processing design ✓
- Complex data extraction ✓
- Search architecture ✓
- Academic metrics ✓

---

### 12. Google Cloud Spanner (Simplified)

**Problem Statement**: Design a globally distributed, strongly consistent database with SQL support.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Global distribution
- External consistency
- 99.999% availability
- SQL with ACID

**Minimum Viable Solution**:
```
Core Design:
1. TrueTime API for global ordering
2. Paxos for replication
3. 2PC for transactions
4. Hierarchical timestamps
5. Multi-version storage

Key Innovations:
- GPS + atomic clocks for time
- Commit wait for consistency
- Snapshot isolation
- Directory-based sharding
```

**Expected Follow-ups**:
- How does TrueTime work?
- How to handle clock uncertainty?
- How to implement schema changes?
- How to optimize for read-heavy workloads?

**Common Mistakes**:
- Not explaining TrueTime
- Ignoring clock skew
- Missing transaction coordination
- Poor replication design

**Evaluation Criteria**:
- Understanding of distributed time ✓
- Consensus protocol knowledge ✓
- Transaction design ✓
- Global scale considerations ✓

---

### 13. Android App Store

**Problem Statement**: Design Google Play Store backend for app distribution, updates, and payments.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- 3M apps, 2B devices
- Differential updates
- Payment processing
- Abuse detection

**Minimum Viable Solution**:
```
Infrastructure:
1. CDN for APK distribution
2. Delta generation service
3. Payment gateway integration
4. ML-based abuse detection
5. Developer console backend

Advanced Features:
- Bsdiff for delta updates
- Staged rollouts
- A/B testing framework
- Real-time metrics pipeline
```

**Expected Follow-ups**:
- How to handle regional restrictions?
- How to implement app signing?
- How to detect malware?
- How to handle refunds?

**Common Mistakes**:
- Missing delta updates
- No abuse prevention
- Poor CDN design
- Ignoring payment complexity

**Evaluation Criteria**:
- Distribution optimization ✓
- Security measures ✓
- Scale handling ✓
- Developer experience ✓

---

### 14. Google Pay

**Problem Statement**: Design a global payment system supporting multiple payment methods and currencies.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Multiple payment types
- Fraud detection
- Regulatory compliance
- 100K transactions/second

**Minimum Viable Solution**:
```
Payment Architecture:
1. Payment gateway abstraction
2. Idempotency service
3. Distributed ledger
4. Fraud detection pipeline
5. Settlement system

Critical Components:
- Token vault for security
- Real-time risk scoring
- Multi-region compliance
- Reconciliation engine
```

**Expected Follow-ups**:
- How to handle payment failures?
- How to implement recurring payments?
- How to ensure PCI compliance?
- How to handle currency conversion?

**Common Mistakes**:
- Weak idempotency design
- Missing compliance requirements
- No fraud prevention
- Poor error handling

**Evaluation Criteria**:
- Security architecture ✓
- Transaction integrity ✓
- Compliance awareness ✓
- Scale design ✓

---

### 15. YouTube Live

**Problem Statement**: Design YouTube's live streaming infrastructure supporting millions of concurrent viewers.

**Time Limit**: 45 minutes

**Key Requirements to Cover**:
- Ingest from 100K streamers
- Deliver to 50M viewers
- <3 second latency
- Multiple quality levels

**Minimum Viable Solution**:
```
Streaming Pipeline:
1. RTMP ingest servers
2. Transcoding cluster (GPU)
3. HLS/DASH packaging
4. Global CDN
5. Adaptive bitrate

Advanced Features:
- DVR functionality
- Real-time analytics
- Chat system
- Monetization (ads/superchats)
```

**Expected Follow-ups**:
- How to handle stream failures?
- How to implement DVR?
- How to insert ads?
- How to scale chat?

**Common Mistakes**:
- Not separating ingest/delivery
- Missing transcoding design
- Poor CDN strategy
- Ignoring chat scale

**Evaluation Criteria**:
- Streaming protocol knowledge ✓
- CDN architecture ✓
- Real-time processing ✓
- Scale optimization ✓

---

## Practice Tips

### Before Starting
1. Clarify requirements (functional and non-functional)
2. Estimate scale (QPS, storage, bandwidth)
3. Define success metrics
4. Identify constraints

### During Design
1. Start with high-level architecture
2. Deep dive into critical components
3. Discuss data flow
4. Address bottlenecks
5. Consider failure scenarios

### Common Pitfalls to Avoid
1. Over-engineering the solution
2. Ignoring trade-offs
3. Missing capacity planning
4. Forgetting about operations
5. Not iterating on design

### After Practice
1. Compare with reference solutions
2. Research unfamiliar concepts
3. Practice explaining to others
4. Time yourself strictly
5. Build complexity gradually

## Success Metrics

Track your progress:
- [ ] Complete all beginner problems
- [ ] Achieve <45min for intermediate problems
- [ ] Handle follow-up questions confidently
- [ ] Identify trade-offs quickly
- [ ] Estimate capacity accurately

Remember: The goal isn't perfection but demonstrating systematic thinking and the ability to make informed trade-offs under time pressure.
# Mock Interview Questions for Google

## System Design Questions by Category

### Search & Discovery Systems

#### 1. Design Google Search
**Focus Areas:**
- Web crawling at scale
- Indexing billions of pages
- Ranking algorithms (PageRank basics)
- Query processing and optimization
- Handling spam and low-quality content

**Key Challenges:**
- Freshness vs completeness trade-off
- Real-time updates for breaking news
- Personalization without filter bubbles
- Multi-language support

#### 2. Design Google Images
**Focus Areas:**
- Image storage and serving
- Reverse image search
- Image recognition and tagging
- Duplicate detection
- SafeSearch filtering

**Key Challenges:**
- Perceptual hashing for similarity
- CDN optimization for images
- Copyright detection
- Multi-resolution serving

#### 3. Design Google Scholar
**Focus Areas:**
- Academic paper crawling
- Citation graph building
- Author disambiguation
- PDF processing at scale
- Metrics calculation (h-index, etc.)

### Media & Entertainment

#### 4. Design YouTube Live
**Focus Areas:**
- Real-time video streaming
- Adaptive bitrate streaming
- Global CDN for live content
- Chat system for millions
- DVR functionality

**Key Challenges:**
- Sub-second latency
- Synchronizing chat with video
- Handling millions of concurrent viewers
- Stream failure recovery

#### 5. Design Google Photos
**Focus Areas:**
- Photo backup and sync
- Face recognition and grouping
- Search within photos
- Storage optimization
- Sharing and collaboration

**Key Challenges:**
- Privacy-preserving ML
- Deduplication across accounts
- Bandwidth optimization
- Real-time sync

#### 6. Design YouTube Shorts
**Focus Areas:**
- Short video recommendation
- Vertical video optimization
- Creator tools
- Engagement metrics
- Content moderation

### Communication & Collaboration

#### 7. Design Google Meet
**Focus Areas:**
- WebRTC infrastructure
- Video/audio codec selection
- Screen sharing
- Recording and transcription
- Breakout rooms

**Key Challenges:**
- NAT traversal
- Bandwidth adaptation
- Echo cancellation
- End-to-end encryption

#### 8. Design Google Docs
**Focus Areas:**
- Operational transformation
- Real-time collaboration
- Conflict resolution
- Offline support
- Version history

**Key Challenges:**
- Consistency in distributed editing
- Performance with large documents
- Rich formatting support
- Mobile experience

#### 9. Design Google Calendar
**Focus Areas:**
- Event scheduling across time zones
- Recurring events
- Meeting room booking
- Calendar sharing
- Reminder system

**Key Challenges:**
- Free/busy calculation
- Conflict detection
- Integration with email
- Smart scheduling

### Maps & Location Services

#### 10. Design Waze
**Focus Areas:**
- Real-time traffic updates
- Crowd-sourced data validation
- Route optimization
- Incident reporting
- Gamification

**Key Challenges:**
- Data quality from users
- Real-time rerouting
- Battery optimization
- Offline support

#### 11. Design Google Earth
**Focus Areas:**
- 3D terrain rendering
- Satellite imagery pipeline
- Streaming massive datasets
- Time-lapse features
- VR support

**Key Challenges:**
- Level-of-detail optimization
- Bandwidth management
- Storage of petabytes of imagery
- Real-time rendering

#### 12. Design Location History
**Focus Areas:**
- Privacy-preserving storage
- Timeline generation
- Location inference
- Battery-efficient tracking
- GDPR compliance

### Cloud & Infrastructure

#### 13. Design BigQuery
**Focus Areas:**
- Columnar storage
- Distributed query execution
- Dremel architecture
- Cost-based optimization
- Streaming inserts

**Key Challenges:**
- Query planning at scale
- Resource allocation
- Multi-tenancy
- Data freshness

#### 14. Design Cloud Spanner
**Focus Areas:**
- Global consistency
- TrueTime API
- Multi-version concurrency
- Automatic sharding
- Cross-region replication

**Key Challenges:**
- Clock synchronization
- Distributed transactions
- Hotspot prevention
- Schema changes

#### 15. Design Google Cloud Storage
**Focus Areas:**
- Object storage design
- Multi-region replication
- Storage classes (hot/cold)
- Resumable uploads
- Access control

### Advertising & Analytics

#### 16. Design Google Ads Auction
**Focus Areas:**
- Real-time bidding (<100ms)
- Ad ranking algorithm
- Budget pacing
- Click prediction
- Fraud detection

**Key Challenges:**
- Latency requirements
- Fairness in auction
- Revenue optimization
- Real-time ML inference

#### 17. Design Google Analytics
**Focus Areas:**
- JavaScript tracking
- Data collection pipeline
- Real-time vs batch processing
- Custom dimensions
- Privacy compliance

**Key Challenges:**
- Handling billions of events
- Bot detection
- Session reconstruction
- Data sampling

### Mobile & Apps

#### 18. Design Android Push Notifications
**Focus Areas:**
- Firebase Cloud Messaging
- Device registration
- Message routing
- Priority handling
- Battery optimization

**Key Challenges:**
- Scaling to billions of devices
- Reliability guarantees
- Wake lock management
- Cross-platform support

#### 19. Design Google Play Store
**Focus Areas:**
- App distribution CDN
- Update mechanisms
- Review system
- Recommendation engine
- Payment processing

**Key Challenges:**
- APK optimization
- Differential updates
- Regional restrictions
- Security scanning

### AI & Assistant

#### 20. Design Google Lens
**Focus Areas:**
- Image recognition pipeline
- OCR at scale
- Object detection
- Real-time processing
- Knowledge graph integration

**Key Challenges:**
- On-device vs cloud processing
- Multi-modal search
- Latency optimization
- Privacy considerations

## Practice Framework

### For Each Question, Address:

1. **Functional Requirements**
   - Core features
   - User interactions
   - API design

2. **Non-Functional Requirements**
   - Scale (users, data, requests)
   - Performance (latency, throughput)
   - Reliability (availability, durability)
   - Security & Privacy

3. **Capacity Planning**
   - Storage calculations
   - Bandwidth requirements
   - Server estimates

4. **High-Level Design**
   - Component architecture
   - Data flow
   - API specification

5. **Detailed Design**
   - Data models
   - Algorithm choices
   - Technology selection

6. **Scale & Performance**
   - Bottleneck identification
   - Caching strategy
   - Sharding approach

7. **Trade-offs**
   - Alternative approaches
   - Cost considerations
   - Operational complexity

## Difficulty Levels

### Beginner (L3/L4)
Focus on core functionality and basic scale:
- URL Shortener
- Pastebin
- Rate Limiter
- Chat Application

### Intermediate (L5)
Add complexity and scale considerations:
- Design Twitter
- Design Instagram
- Design Uber
- Design Airbnb

### Advanced (L6+)
Google-scale systems with multiple constraints:
- Design YouTube
- Design Google Search
- Design Gmail
- Design Google Maps

## Follow-up Questions Bank

### Scale-Related
1. "How would this handle 10x growth?"
2. "What if we need to support 1 billion users?"
3. "How do we handle viral content?"
4. "What about geographic distribution?"

### Failure-Related
1. "What if the primary database fails?"
2. "How do we handle network partitions?"
3. "What's the disaster recovery plan?"
4. "How do we ensure no data loss?"

### Performance-Related
1. "How can we reduce latency by 50%?"
2. "What if users complain about slow loading?"
3. "How do we optimize for mobile?"
4. "Can we serve this from edge locations?"

### Cost-Related
1. "How do we reduce storage costs?"
2. "What's the most expensive component?"
3. "How does cost scale with users?"
4. "Trade storage for compute?"

### Feature-Related
1. "How would you add real-time features?"
2. "What about offline support?"
3. "How do we implement search?"
4. "Can we add machine learning?"

## Tips for Practice

1. **Time yourself** - Stick to 45 minutes
2. **Draw everything** - Practice whiteboarding
3. **Think aloud** - Verbalize your process
4. **Start simple** - Then add complexity
5. **Cover breadth** - Touch all aspects
6. **Go deep** - Pick 2-3 areas to detail
7. **Discuss trade-offs** - No perfect solutions
8. **Ask questions** - Even in practice

## 🔗 Resources for Each Question

Link each design to relevant patterns:
- [Sharding](google-interviews/../../patterns/sharding.md) for horizontal scaling
- [Caching Strategies](google-interviews/../../patterns/caching-strategies.md) for performance
- [Event Sourcing](google-interviews/../../patterns/event-sourcing.md) for audit trails
- [Circuit Breaker](google-interviews/../../pattern-library/resilience/circuit-breaker.md) for reliability
- [Load Balancing](google-interviews/../../patterns/load-balancing.md) for distribution

Remember: The goal isn't to memorize solutions but to demonstrate systematic thinking and problem-solving skills at Google scale.
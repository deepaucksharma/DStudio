# System Design Checklist

## ✅ Complete System Design Checklist

### 📋 Phase 1: Requirements Gathering (5-8 min)

#### Functional Requirements
- [ ] **Core Features** (3-5 main functions)
  - [ ] Primary use cases identified
  - [ ] User types defined
  - [ ] Core workflows mapped
- [ ] **Scope Boundaries**
  - [ ] In-scope features listed
  - [ ] Out-of-scope explicitly stated
  - [ ] MVP vs future phases
- [ ] **Success Metrics**
  - [ ] Business KPIs defined
  - [ ] Technical SLAs stated
  - [ ] User satisfaction metrics

#### Non-Functional Requirements
- [ ] **Scale**
  - [ ] Total users: _______
  - [ ] Daily active users: _______
  - [ ] Concurrent users: _______
  - [ ] Growth rate: _______% per year
- [ ] **Performance**
  - [ ] Latency P50: _______ ms
  - [ ] Latency P99: _______ ms
  - [ ] Throughput: _______ QPS
- [ ] **Reliability**
  - [ ] Availability: _______% 
  - [ ] Data durability: _______ 9s
  - [ ] RPO/RTO: _______
- [ ] **Consistency**
  - [ ] Strong / Eventual / Causal
  - [ ] Read-after-write needed?
  - [ ] Cross-region requirements
- [ ] **Security & Compliance**
  - [ ] Authentication method
  - [ ] Data encryption needs
  - [ ] Compliance requirements

### 🧮 Phase 2: Capacity Estimation (3-5 min)

#### Traffic Estimation
- [ ] **Read/Write Ratio**: ___:___
- [ ] **Peak Traffic**
  - [ ] Peak QPS = Avg QPS × ___ (typically 2-3x)
  - [ ] Special events multiplier: ___x
- [ ] **API Breakdown**
  ```
  API Endpoint         QPS    Payload Size
  GET /resource       ____    ____ KB
  POST /resource      ____    ____ KB
  PUT /resource       ____    ____ KB
  ```

#### Storage Estimation
- [ ] **Data Size**
  ```
  Entity        Count        Size Each    Total
  Users         _______      ____ KB      ____ TB
  Resources     _______      ____ KB      ____ TB
  Metadata      _______      ____ KB      ____ TB
  ```
- [ ] **Growth Rate**: ____ GB/day
- [ ] **Retention Period**: ____ years
- [ ] **Total Storage**: Current + (Growth × Retention)
- [ ] **With Replication**: Total × Replication Factor

#### Bandwidth Estimation
- [ ] **Ingress**: QPS × Request Size = ____ Gbps
- [ ] **Egress**: QPS × Response Size = ____ Gbps
- [ ] **Peak Bandwidth**: Avg × Peak Factor = ____ Gbps
- [ ] **CDN Offload**: ____% of bandwidth

#### Server Estimation
- [ ] **Application Servers**: Peak QPS / Server Capacity
- [ ] **Cache Servers**: Working Set Size / Server Memory
- [ ] **Database Servers**: Based on IOPS and storage
- [ ] **With Redundancy**: Servers × (1 + Redundancy Factor)

### 🏗️ Phase 3: High-Level Design (10-15 min)

#### System Architecture
- [ ] **Client Layer**
  - [ ] Web clients
  - [ ] Mobile clients (iOS/Android)
  - [ ] API clients
- [ ] **Edge Layer**
  - [ ] CDN for static content
  - [ ] DNS with GeoDNS
  - [ ] DDoS protection
- [ ] **Gateway Layer**
  - [ ] Load balancer (L4/L7)
  - [ ] API Gateway
  - [ ] Rate limiting
  - [ ] Authentication/Authorization
- [ ] **Application Layer**
  - [ ] Stateless app servers
  - [ ] Service mesh (if microservices)
  - [ ] Container orchestration
- [ ] **Cache Layer**
  - [ ] Client-side cache
  - [ ] CDN cache
  - [ ] Application cache
  - [ ] Database cache
- [ ] **Data Layer**
  - [ ] Primary database
  - [ ] Read replicas
  - [ ] Data warehouse
  - [ ] Object storage
- [ ] **Message Layer**
  - [ ] Message queue
  - [ ] Event streaming
  - [ ] Pub/sub system
- [ ] **Processing Layer**
  - [ ] Batch processing
  - [ ] Stream processing
  - [ ] Background workers

#### Data Flow
- [ ] **Synchronous Flow**
  ```
  Client → LB → Gateway → Service → Cache → DB
  ```
- [ ] **Asynchronous Flow**
  ```
  Service → Queue → Worker → External Service
  ```
- [ ] **Real-time Flow**
  ```
  Client ← WebSocket ← Service ← Event Stream
  ```

### 📐 Phase 4: API Design (5 min)

#### RESTful APIs
- [ ] **Resource Naming**
  - [ ] Plural nouns for collections
  - [ ] Consistent naming convention
  - [ ] Hierarchical relationships
- [ ] **Core Endpoints**
  ```
  GET    /api/v1/resources
  GET    /api/v1/resources/{id}
  POST   /api/v1/resources
  PUT    /api/v1/resources/{id}
  DELETE /api/v1/resources/{id}
  ```
- [ ] **Query Parameters**
  - [ ] Filtering: ?status=active
  - [ ] Sorting: ?sort=created_at:desc
  - [ ] Pagination: ?page=1&limit=20
  - [ ] Field selection: ?fields=id,name
- [ ] **Response Format**
  ```json
  {
    "data": {},
    "meta": {
      "page": 1,
      "total": 100
    },
    "errors": []
  }
  ```
- [ ] **Error Handling**
  - [ ] Standard HTTP status codes
  - [ ] Consistent error format
  - [ ] Meaningful error messages

#### Alternative APIs
- [ ] **GraphQL** (if flexible queries needed)
- [ ] **gRPC** (if low latency critical)
- [ ] **WebSocket** (if real-time needed)

### 💾 Phase 5: Data Model (5 min)

#### Database Selection
- [ ] **Decision Matrix**
  | Requirement | SQL | NoSQL | Cache | Search |
  |-------------|-----|-------|-------|--------|
  | ACID | ✓ | × | × | × |
  | Scale | Medium | High | High | Medium |
  | Flexibility | Low | High | Low | High |
  | Queries | Complex | Simple | Key-based | Full-text |

#### Schema Design
- [ ] **Core Entities**
  ```sql
  Users
  - id (UUID)
  - email (unique)
  - created_at
  - updated_at
  
  Resources
  - id (UUID)
  - user_id (FK)
  - data (JSON)
  - created_at
  - updated_at
  ```
- [ ] **Indexes**
  - [ ] Primary keys
  - [ ] Foreign keys
  - [ ] Frequently queried fields
  - [ ] Composite indexes for complex queries
- [ ] **Partitioning Strategy**
  - [ ] By date (time-series data)
  - [ ] By user_id (user data)
  - [ ] By geography (regional data)

### 🔍 Phase 6: Detailed Design (10-15 min)

#### Component Deep Dives
- [ ] **Choose 2-3 Critical Components**
- [ ] **For Each Component**:
  - [ ] Internal architecture
  - [ ] Technology choices
  - [ ] Scaling strategy
  - [ ] Failure handling
  - [ ] Monitoring approach

#### Scaling Strategies
- [ ] **Horizontal Scaling**
  - [ ] Stateless services
  - [ ] Load balancing algorithm
  - [ ] Session management
- [ ] **Data Scaling**
  - [ ] Read replicas for read-heavy
  - [ ] Sharding for write-heavy
  - [ ] Caching strategy
- [ ] **Geographic Scaling**
  - [ ] Multi-region deployment
  - [ ] Data replication strategy
  - [ ] Conflict resolution

#### Performance Optimization
- [ ] **Caching Strategy**
  - [ ] What to cache
  - [ ] Where to cache (L1/L2/L3)
  - [ ] TTL policies
  - [ ] Cache invalidation
- [ ] **Query Optimization**
  - [ ] Index usage
  - [ ] Query patterns
  - [ ] Denormalization needs
- [ ] **Async Processing**
  - [ ] What to make async
  - [ ] Queue selection
  - [ ] Worker scaling

### 🛡️ Phase 7: Reliability & Operations (5 min)

#### Failure Handling
- [ ] **Single Points of Failure**
  - [ ] Identified and mitigated
  - [ ] Redundancy added
- [ ] **Failure Modes**
  - [ ] Network partitions
  - [ ] Service crashes
  - [ ] Data corruption
  - [ ] Cascading failures
- [ ] **Recovery Mechanisms**
  - [ ] Circuit breakers
  - [ ] Retry with backoff
  - [ ] Fallback responses
  - [ ] Graceful degradation

#### Monitoring & Alerting
- [ ] **Key Metrics**
  - [ ] Golden signals (latency, traffic, errors, saturation)
  - [ ] Business metrics
  - [ ] Custom metrics
- [ ] **Logging**
  - [ ] Structured logging
  - [ ] Log aggregation
  - [ ] Log retention
- [ ] **Alerting**
  - [ ] Alert fatigue prevention
  - [ ] Escalation policies
  - [ ] Runbooks

#### Security
- [ ] **Authentication & Authorization**
  - [ ] OAuth2/JWT implementation
  - [ ] Role-based access control
  - [ ] API key management
- [ ] **Data Protection**
  - [ ] Encryption at rest
  - [ ] Encryption in transit
  - [ ] PII handling
- [ ] **Security Best Practices**
  - [ ] Input validation
  - [ ] SQL injection prevention
  - [ ] Rate limiting
  - [ ] DDoS protection

### 🔄 Phase 8: Trade-offs & Evolution (5 min)

#### Trade-off Analysis
- [ ] **CAP Theorem Trade-offs**
  - [ ] Consistency vs Availability choice
  - [ ] Partition tolerance handling
- [ ] **Performance vs Cost**
  - [ ] Caching costs vs benefits
  - [ ] Compute vs storage optimization
- [ ] **Complexity vs Maintainability**
  - [ ] Microservices vs monolith
  - [ ] Technology diversity

#### Future Evolution
- [ ] **Growth Path**
  ```
  Phase 1 (MVP): Simple architecture
  Phase 2 (10x): Add caching and read replicas
  Phase 3 (100x): Sharding and microservices
  Phase 4 (1000x): Multi-region and edge computing
  ```
- [ ] **Technical Debt**
  - [ ] Identified shortcuts
  - [ ] Refactoring plan
  - [ ] Migration strategy

### 🎯 Final Checklist

#### Communication
- [ ] Clear diagrams drawn
- [ ] Thought process explained
- [ ] Assumptions stated
- [ ] Questions asked
- [ ] Feedback incorporated

#### Completeness
- [ ] End-to-end flow covered
- [ ] All requirements addressed
- [ ] Major failure scenarios handled
- [ ] Monitoring strategy defined
- [ ] Security considerations included

#### Quality Indicators
- [ ] Multiple solutions considered
- [ ] Trade-offs explicitly discussed
- [ ] Real-world examples referenced
- [ ] Scalability path shown
- [ ] Operational aspects covered

## 🚀 Quick Reference

### Time Allocation (45 min)
```
Requirements: 8 min
Estimation:   5 min
High-level:  15 min
Deep dive:   15 min
Wrap-up:      2 min
```

### Must-Have Components
1. Load Balancer
2. Application Servers
3. Database (with replicas)
4. Cache Layer
5. Message Queue
6. Monitoring

### Common Mistakes to Avoid
- ❌ Over-engineering early
- ❌ Ignoring data consistency
- ❌ Forgetting failure modes
- ❌ Missing monitoring
- ❌ No clear API design
- ❌ Skipping trade-offs
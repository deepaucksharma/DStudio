# Start Here: Your Journey into Distributed Systems

## What Brings You Here Today?

### 🔥 "Our system is on fire!"
**Need immediate solutions to production problems?**

| Problem | Quick Fix | Time | Deep Dive |
|---------|-----------|------|-----------|
| Service failures cascading | [Circuit Breaker](..../pattern-library/resilience.md/circuit-breaker/index.md) | 1 hour | [Resilience patterns](..../pattern-library/resilience.md/index.md) |
| Database overwhelmed | [Read replicas + Caching](..../pattern-library/scaling.md/caching-strategies/index.md) | 2 hours | [Scaling patterns](..../pattern-library/scaling.md/index.md) |
| API rate limit breaches | [Rate Limiting](..../pattern-library/scaling.md/rate-limiting/index.md) | 30 mins | [Backpressure patterns](..../pattern-library/scaling.md/backpressure/index.md) |
| Inconsistent data across services | [Saga pattern](..../pattern-library/data-management.md/saga/index.md) | 4 hours | [Data consistency guide](/excellence/implementation-guides/data-consistency/index.md) |
| Service discovery failing | [Service Registry](..../pattern-library/communication.md/service-registry/index.md) | 1 hour | [Service mesh migration](/excellence/migrations/gossip-to-service-mesh/index.md) |

[**→ Emergency Playbooks**](/excellence/implementation-guides/quick-start-guide/index.md)

---

### 📚 "I want to learn properly"
**Building strong foundations in distributed systems?**

#### Choose Your Path

| Path | For You If... | Duration | Outcome |
|------|---------------|----------|---------|
| [**Foundations**](..../architects-handbook/learning-paths.md/new-graduate/index.md) | New to distributed systems | 10 weeks | Build & deploy a distributed URL shortener handling 10K RPS |
| [**Advanced**](..../architects-handbook/learning-paths.md/senior-engineer/index.md) | 3+ years experience | 8 weeks | Design multi-region systems with <100ms latency |
| [**Architecture**](..../architects-handbook/learning-paths.md/architect/index.md) | Leading system design | 6 weeks | Make architectural decisions for 100M+ user systems |
| [**Leadership**](..../architects-handbook/learning-paths.md/manager/index.md) | Managing teams | 4 weeks | Lead distributed teams through complex migrations |

#### Quick Learning Wins

- **Understand in 30 minutes**: [The 7 Fundamental Laws](..../core-principles/laws.md/index.md)
- **Master in 1 day**: [The 5 Distribution Pillars](..../core-principles/pillars.md/index.md)
- **Apply in 1 week**: [Gold-tier patterns](/excellence/pattern-discovery/gold-patterns/index.md)

---

### 🏗️ "I'm designing a new system"
**Need pattern recommendations for your architecture?**

#### Pattern Selection by Scale

| Users | Data | Patterns to Start | Case Study |
|-------|------|-------------------|------------|
| <10K | <1GB | Monolith + CDN + Cache | [URL Shortener](..../architects-handbook/case-studies.md/infrastructure/url-shortener/index.md) |
| 10K-1M | <100GB | API Gateway + Service Discovery + Read Replicas | [E-commerce Platform](..../architects-handbook/case-studies.md/financial-commerce/ecommerce-platform/index.md) |
| 1M-10M | <10TB | Sharding + Event Streaming + CQRS | [Social Media Feed](..../architects-handbook/case-studies.md/social-communication/social-media-feed/index.md) |
| 10M+ | >10TB | Cell-based + Multi-region + Edge Computing | [Netflix Architecture](..../architects-handbook/case-studies.md/elite-engineering/netflix-chaos-engineering/index.md) |

[**→ Pattern Discovery Tool**](/patterns/index.md) | [**→ Architecture Decision Framework**](..../pattern-library/pattern-decision-matrix.md/index.md)

---

### 🔄 "I need to migrate/modernize"
**Transitioning from legacy to modern patterns?**

#### Popular Migrations

| From | To | Complexity | Guide |
|------|----|------------|-------|
| Monolith | Microservices | High | [Step-by-step guide](/excellence/migrations/monolith-to-microservices/index.md) |
| Polling | Event-driven | Medium | [WebSocket migration](/excellence/migrations/polling-to-websocket/index.md) |
| Batch | Streaming | High | [Streaming guide](/excellence/migrations/batch-to-streaming/index.md) |
| Single DB | Distributed DB | Very High | [Database migration](/excellence/migrations/shared-database-to-microservices/index.md) |
| REST | GraphQL | Medium | [GraphQL Federation](..../pattern-library/architecture.md/graphql-federation/index.md) |

[**→ All Migration Guides**](/excellence/migrations/index.md)

---

## Quick Navigation

### By Problem Domain

<div class="grid cards">
<div class="card">
<strong>🔍 Search & Analytics</strong>

- [Elasticsearch Architecture](..../architects-handbook/case-studies.md/search-analytics/elasticsearch/index.md)
- [Google Search Infrastructure](..../architects-handbook/case-studies.md/search-analytics/google-search-infrastructure/index.md)
- [Real-time Analytics](..../pattern-library/architecture.md/lambda-architecture/index.md)
</div>

<div class="card">
<strong>💬 Messaging & Social</strong>

- [Chat Systems](..../architects-handbook/case-studies.md/social-communication/chat-system/index.md)
- [Notification Systems](..../architects-handbook/case-studies.md/social-communication/notification-system/index.md)
- [Social Graphs](..../architects-handbook/case-studies.md/social-communication/social-graph/index.md)
</div>

<div class="card">
<strong>💰 Financial & Commerce</strong>

- [Payment Systems](..../architects-handbook/case-studies.md/financial-commerce/payment-system/index.md)
- [Digital Wallets](..../architects-handbook/case-studies.md/financial-commerce/digital-wallet-enhanced/index.md)
- [Stock Exchanges](..../architects-handbook/case-studies.md/financial-commerce/stock-exchange/index.md)
</div>

<div class="card">
<strong>📍 Location Services</strong>

- [Uber Location Platform](..../architects-handbook/case-studies.md/location-services/uber-location/index.md)
- [Google Maps System](..../architects-handbook/case-studies.md/location-services/google-maps-system/index.md)
- [Proximity Services](..../architects-handbook/case-studies.md/location-services/proximity-service/index.md)
</div>
</div>

### By Company

| Company | Best Known For | Case Studies |
|---------|----------------|--------------|
| **Netflix** | Chaos Engineering, Microservices | [Streaming](..../architects-handbook/case-studies.md/messaging-streaming/netflix-streaming/index.md) • [Chaos](..../architects-handbook/case-studies.md/elite-engineering/netflix-chaos/index.md) • [Architecture Evolution](/company-specific/netflix/index.md) |
| **Uber** | Real-time Geo, Scale | [Location Platform](..../architects-handbook/case-studies.md/location-services/uber-location/index.md) • [Maps](..../architects-handbook/case-studies.md/location-services/uber-maps/index.md) • [H3 Geo-indexing](..../pattern-library/scaling.md/geo-distribution/index.md) |
| **Google** | Global Scale, Innovation | [Search](..../architects-handbook/case-studies.md/search-analytics/google-search/index.md) • [Spanner](..../architects-handbook/case-studies.md/databases/google-spanner/index.md) • [YouTube](..../architects-handbook/case-studies.md/social-communication/youtube/index.md) |
| **Amazon** | E-commerce, AWS | [DynamoDB](..../architects-handbook/case-studies.md/databases/amazon-dynamo/index.md) • [Aurora](..../architects-handbook/case-studies.md/databases/amazon-aurora/index.md) • [S3](..../architects-handbook/case-studies.md/infrastructure/s3-object-storage-enhanced/index.md) |

[**→ All Company Architectures**](/company-specific/index.md)

---

## Learning Resources

### Essential References
- 📖 [Glossary of Terms](/reference/glossary/index.md)
- 🎯 [Pattern Cheat Sheet](/reference/pattern-selection-cheatsheet/index.md)
- 📊 [Pattern Health Dashboard](/reference/pattern-health-dashboard/index.md)
- 🔒 [Security Considerations](/reference/security/index.md)

### Tools & Calculators
- [Availability Calculator](..../architects-handbook/tools.md/availability-calculator/index.md)
- [Capacity Planner](..../architects-handbook/tools.md/capacity-calculator/index.md)
- [Latency Estimator](..../architects-handbook/tools.md/latency-calculator/index.md)
- [Cost Optimizer](..../architects-handbook/tools.md/cost-optimizer/index.md)

### Community & Updates
- [Contributing Guide](/reference/contributing/index.md)
- [What's New](/excellence/framework-overview/index.md)
- [Roadmap & Vision](..../core-principles/index.md)

---

## Not Sure Where to Start?

**Answer 3 quick questions:**

1. **Your experience level?**
   - [ ] Student/New Grad → [Start with Foundations](..../architects-handbook/learning-paths.md/new-graduate/index.md)
   - [ ] 1-3 years → [Jump to Patterns](/patterns/index.md)
   - [ ] 3+ years → [Explore Case Studies](..../architects-handbook/case-studies.md/index.md)
   - [ ] Team Lead → [Leadership Path](..../architects-handbook/learning-paths.md/manager/index.md)

2. **Your immediate need?**
   - [ ] Learn concepts → [7 Laws](..../core-principles/laws.md/index.md)
   - [ ] Solve problems → [Pattern Library](..../pattern-library/index.md)
   - [ ] See examples → [Case Studies](..../architects-handbook/case-studies.md/index.md)
   - [ ] Build something → [Implementation Guides](/excellence/implementation-guides/index.md)

3. **Your domain?**
   - [ ] Web/Mobile → [API Gateway](..../pattern-library/communication.md/api-gateway/index.md) + [CDN patterns](..../pattern-library/scaling.md/edge-computing/index.md)
   - [ ] Data/Analytics → [Streaming architectures](..../pattern-library/architecture.md/event-streaming/index.md)
   - [ ] IoT/Real-time → [Event-driven patterns](..../pattern-library/architecture.md/event-driven/index.md)
   - [ ] Enterprise → [Saga](..../pattern-library/data-management.md/saga/index.md) + [Service Mesh](..../pattern-library/communication.md/service-mesh/index.md)

---

<div class="admonition tip">
<p class="admonition-title">Pro Tip</p>
<p>Bookmark this page - it's designed to be your quick-access hub for all distributed systems knowledge. Each section is updated as new patterns and case studies are added.</p>
</div>
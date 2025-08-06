# Structured Learning Path Template

## Example: Distributed Systems Foundations Path

### Before: Vague Promises ❌
- "Learn distributed systems concepts"
- "Understand scalability"
- "Master microservices"
- "Become a better architect"

### After: SMART Learning Path ✅

# Distributed Systems Foundations
**Build a Production-Ready URL Shortener Handling 10K RPS**

## Learning Outcome
By completing this 10-week path, you will:
- **Build** a distributed URL shortener from scratch
- **Scale** it to handle 10,000 requests per second
- **Deploy** across 3 geographic regions
- **Achieve** <100ms p99 latency globally
- **Pass** chaos testing with 99.9% availability

## Prerequisites Check

| Requirement | Self-Assessment | Resources if Needed |
|-------------|-----------------|---------------------|
| Basic programming (any language) | ⬜ Yes ⬜ No | [Programming basics] |
| HTTP/REST concepts | ⬜ Yes ⬜ No | [REST tutorial] |
| Basic database knowledge | ⬜ Yes ⬜ No | [SQL basics] |
| Command line comfort | ⬜ Yes ⬜ No | [Terminal guide] |

## Week-by-Week Breakdown

### Week 1: Monolith Baseline
**Goal**: Build working URL shortener handling 100 RPS

| Day | Topic | Hands-On | Checkpoint |
|-----|-------|----------|------------|
| 1 | System design basics | Design on paper | Architecture diagram |
| 2 | Database schema | Implement schema | Working database |
| 3 | Core API | Build REST endpoints | `/shorten`, `/redirect` working |
| 4 | Caching layer | Add Redis | 90% cache hit rate |
| 5 | Load testing | Use JMeter/k6 | Baseline: 100 RPS |

**Deliverable**: Single-node URL shortener with tests

### Week 2: Horizontal Scaling
**Goal**: Scale to 1,000 RPS with multiple instances

| Day | Topic | Hands-On | Checkpoint |
|-----|-------|----------|------------|
| 1 | Load balancing | Deploy HAProxy/nginx | Round-robin working |
| 2 | Session management | Implement stateless design | No sticky sessions |
| 3 | Database connection pooling | Configure pool | No connection exhaustion |
| 4 | Horizontal scaling | Deploy 3 instances | Linear scaling verified |
| 5 | Monitoring setup | Prometheus + Grafana | Dashboards live |

**Deliverable**: Multi-instance deployment hitting 1K RPS

### Week 3: Data Layer Distribution
**Goal**: Implement sharding for 1M+ URLs

| Day | Topic | Hands-On | Checkpoint |
|-----|-------|----------|------------|
| 1 | [Consistent hashing](/../pattern-library/data-management/consistent-hashing/index.md) | Implement hash ring | Even distribution |
| 2 | [Sharding](/../pattern-library/scaling/sharding/index.md) | Shard by URL key | 4 shards working |
| 3 | Shard routing | Build routing layer | Correct shard selection |
| 4 | Cross-shard queries | Implement scatter-gather | Analytics working |
| 5 | Resharding strategy | Test shard addition | Zero downtime migration |

**Deliverable**: Sharded database handling millions of URLs

### Week 4: Caching & Performance
**Goal**: Achieve <50ms p99 latency

| Day | Topic | Hands-On | Checkpoint |
|-----|-------|----------|------------|
| 1 | [Multi-tier caching](/../pattern-library/scaling/caching-strategies/index.md) | L1 + L2 cache | 95% hit rate |
| 2 | Cache warming | Implement preloading | Popular URLs cached |
| 3 | [CDN integration](/../pattern-library/scaling/edge-computing/index.md) | Configure CloudFlare | Global edge caching |
| 4 | Database optimization | Index tuning | Query time <5ms |
| 5 | Performance testing | Full stack testing | <50ms p99 achieved |

**Deliverable**: Sub-50ms response times globally

### Week 5: High Availability
**Goal**: 99.9% uptime with automatic failover

| Day | Topic | Hands-On | Checkpoint |
|-----|-------|----------|------------|
| 1 | [Health checks](/../pattern-library/resilience/health-check/index.md) | Implement endpoints | Accurate health status |
| 2 | [Circuit breakers](/../pattern-library/resilience/circuit-breaker/index.md) | Add to all calls | Cascading failures prevented |
| 3 | Database replication | Setup read replicas | Automatic failover |
| 4 | [Graceful degradation](/../pattern-library/resilience/graceful-degradation/index.md) | Fallback strategies | Service stays up |
| 5 | Chaos testing | Kill random services | Auto-recovery verified |

**Deliverable**: Resilient system surviving failures

### Week 6: Observability
**Goal**: Full system visibility and debugging

| Day | Topic | Hands-On | Checkpoint |
|-----|-------|----------|------------|
| 1 | Structured logging | ELK stack setup | Centralized logs |
| 2 | Distributed tracing | Jaeger integration | Request flow visible |
| 3 | Custom metrics | Business metrics | URL stats dashboard |
| 4 | Alerting rules | PagerDuty setup | Critical alerts configured |
| 5 | SLI/SLO definition | Define objectives | SLO dashboard live |

**Deliverable**: Observable system with <15min MTTR

### Week 7: Security & Compliance
**Goal**: Production-ready security

| Day | Topic | Hands-On | Checkpoint |
|-----|-------|----------|------------|
| 1 | Authentication | API key system | Secure endpoints |
| 2 | [Rate limiting](/../pattern-library/scaling/rate-limiting/index.md) | Per-user limits | Abuse prevention |
| 3 | Data encryption | TLS + encryption at rest | E2E encryption |
| 4 | Audit logging | Compliance logs | GDPR ready |
| 5 | Security testing | OWASP scan | Vulnerabilities fixed |

**Deliverable**: Secure, compliant system

### Week 8: Global Distribution
**Goal**: Deploy to 3 regions with <100ms latency

| Day | Topic | Hands-On | Checkpoint |
|-----|-------|----------|------------|
| 1 | [Multi-region setup](/../pattern-library/scaling/multi-region/index.md) | Deploy to 3 regions | All regions live |
| 2 | Data replication | Cross-region sync | Eventual consistency |
| 3 | [GeoDNS](/../pattern-library/scaling/geo-distribution/index.md) | Route by location | Nearest region selected |
| 4 | Conflict resolution | [CRDT implementation](/../pattern-library/data-management/crdt/index.md) | Conflicts handled |
| 5 | Global testing | Test from 10 locations | <100ms everywhere |

**Deliverable**: Globally distributed system

### Week 9: Scale to 10K RPS
**Goal**: Handle peak traffic efficiently

| Day | Topic | Hands-On | Checkpoint |
|-----|-------|----------|------------|
| 1 | Capacity planning | Calculate resources | Requirements defined |
| 2 | [Auto-scaling](/../pattern-library/scaling/auto-scaling/index.md) | Configure policies | Scales with load |
| 3 | Database optimization | Query optimization | No bottlenecks |
| 4 | Load testing | Gradual ramp to 10K | Target achieved |
| 5 | Cost optimization | Right-sizing | 30% cost reduction |

**Deliverable**: 10K RPS with acceptable costs

### Week 10: Production Operations
**Goal**: Ready for real users

| Day | Topic | Hands-On | Checkpoint |
|-----|-------|----------|------------|
| 1 | Deployment pipeline | CI/CD setup | Automated deployments |
| 2 | Runbook creation | Document procedures | Operations ready |
| 3 | Backup & recovery | Test restore | RPO/RTO verified |
| 4 | Final chaos testing | Full failure scenarios | All tests pass |
| 5 | Launch preparation | Final review | Production ready! |

**Deliverable**: Production-ready URL shortener

## Progress Tracking

### Weekly Milestones
- [ ] Week 1: 100 RPS monolith
- [ ] Week 2: 1K RPS scaled
- [ ] Week 3: Sharded data layer
- [ ] Week 4: <50ms latency
- [ ] Week 5: 99.9% availability
- [ ] Week 6: Full observability
- [ ] Week 7: Security hardened
- [ ] Week 8: Global deployment
- [ ] Week 9: 10K RPS achieved
- [ ] Week 10: Production ready

### Skills Acquired

| Skill Category | Specific Skills | Proficiency |
|----------------|-----------------|-------------|
| **Architecture** | Microservices, Sharding, Caching | ⭐⭐⭐⭐ |
| **Scalability** | Horizontal scaling, Load balancing | ⭐⭐⭐⭐ |
| **Reliability** | Circuit breakers, Failover | ⭐⭐⭐⭐ |
| **Performance** | Optimization, Caching, CDN | ⭐⭐⭐⭐ |
| **Operations** | Monitoring, Debugging, Deployment | ⭐⭐⭐ |

## Capstone Project

**Build Your Own**: After completing the URL shortener, choose one:
1. **Distributed Cache**: Like Redis, handling 100K ops/sec
2. **Message Queue**: Like RabbitMQ, with persistence
3. **Search Engine**: Basic text search over 1M documents

Success criteria:
- Applies 10+ patterns learned
- Handles stated scale
- Includes full observability
- Passes chaos testing

## Learning Resources

### Required Reading (In Order)
1. [7 Fundamental Laws](../core-principles/laws.md/index.md) - Week 1
2. [5 Distribution Pillars](../core-principles/pillars.md/index.md) - Week 2
3. [CAP Theorem Deep Dive](/../pattern-library/architecture/cap-theorem/index.md) - Week 3
4. [Scaling Patterns Overview](/../pattern-library/scaling/index.md) - Week 4

### Reference Documentation
- [Pattern Library](/../pattern-library/index.md) - Use throughout
- [Case Studies](../architects-handbook/case-studies/index.md) - Real examples
- [Quantitative Analysis](../architects-handbook/quantitative-analysis.md/index.md) - Week 9

### Community & Support
- Weekly office hours: Fridays 2-3pm
- Slack channel: #distributed-systems-foundations
- Study groups: Self-organized by cohort

## Certification Path

Upon completion, you'll be ready for:
- [ ] **AWS Solutions Architect** - With hands-on distributed systems experience
- [ ] **Google Cloud Architect** - Understanding of global scale systems
- [ ] **System Design Interviews** - Built real systems, not just theory

## FAQ

**Q: What if I fall behind?**
A: Each week builds on the previous, but you can catch up. Focus on deliverables, not perfection.

**Q: Which programming language?**
A: Any language works. Examples provided in Go, Java, and Python.

**Q: How much time needed daily?**
A: 2-3 hours per day, 5 days per week. Weekend catch-up if needed.

**Q: Can I skip weeks?**
A: Not recommended. Each week introduces critical concepts used later.

---

<div class="admonition success">
<p class="admonition-title">Success Story</p>
<p>"I completed this path in 2023. The URL shortener project helped me land a Senior SWE role at a FAANG company. The hands-on experience was invaluable during system design interviews." - Previous Student</p>
</div>
# Pattern Selection Matrices

## Resilience Patterns Comparison

| Pattern | Use Case | Failure Type | Response Time | Complexity | When to Use |
|---------|----------|--------------|---------------|------------|-------------|
| **Circuit Breaker** | External services | Cascading failures | Immediate (fail fast) | Medium | • Multiple microservices<br/>• External API calls<br/>• High failure risk |
| **Retry with Backoff** | Transient failures | Temporary issues | Delayed (exponential) | Low | • Network timeouts<br/>• Rate limiting<br/>• Service overload |
| **Bulkhead** | Resource isolation | Resource exhaustion | Normal | Medium | • Multi-tenant systems<br/>• Critical path isolation<br/>• Resource protection |
| **Timeout** | Slow operations | Hanging requests | Bounded | Low | • All network calls<br/>• Database queries<br/>• External APIs |
| **Health Check** | Service monitoring | Service degradation | Proactive | Low | • Load balancer config<br/>• Service discovery<br/>• Auto-scaling |

## API Architecture Patterns

| Pattern | Client Types | Scale | Latency | Flexibility | Example |
|---------|--------------|-------|---------|-------------|---------|
| **API Gateway** | Multiple external | Internet-scale | +5-10ms | High | Netflix Zuul<br/>AWS API Gateway |
| **Service Mesh** | Internal services | Large clusters | +1-2ms | Very High | Istio, Linkerd |
| **BFF (Backend for Frontend)** | Specific clients | Per-client | +10-15ms | Client-optimized | Netflix Mobile BFF |
| **GraphQL Gateway** | Complex queries | Medium-Large | +20-50ms | Query flexibility | GitHub, Shopify |
| **Direct Service** | Single purpose | Small | Minimal | Low | Simple microservices |

## Data Management Patterns

| Pattern | Consistency | Latency | Complexity | Use Case | Trade-offs |
|---------|-------------|---------|------------|----------|------------|
| **CQRS** | Eventual | Read: Low<br/>Write: Normal | High | • Read-heavy workloads<br/>• Complex queries<br/>• Different read/write models | ✅ Optimized reads<br/>✅ Scalable<br/>❌ Complexity<br/>❌ Eventual consistency |
| **Event Sourcing** | Eventual | Write: Low<br/>Read: Variable | Very High | • Audit requirements<br/>• Time travel queries<br/>• Event-driven systems | ✅ Complete history<br/>✅ Audit trail<br/>❌ Storage costs<br/>❌ Query complexity |
| **Saga** | Eventual | Transaction time | High | • Distributed transactions<br/>• Long-running processes<br/>• Cross-service workflows | ✅ No distributed locks<br/>✅ Resilient<br/>❌ Complex rollback<br/>❌ Debugging difficulty |
| **Database per Service** | Service-level | Normal | Medium | • Microservices<br/>• Team autonomy<br/>• Technology diversity | ✅ Independence<br/>✅ Technology choice<br/>❌ Data duplication<br/>❌ Cross-service queries |

## Scaling Patterns Decision Matrix

| Pattern | Scale Type | Cost | Complexity | Response Time | Best For |
|---------|------------|------|------------|---------------|----------|
| **Load Balancing** | Horizontal | Low | Low | No impact | • Stateless services<br/>• Request distribution |
| **Caching** | Read scale | Very Low | Low | Microseconds | • Static content<br/>• Repeated queries |
| **Sharding** | Data scale | Medium | High | Normal | • Large datasets<br/>• Geographic distribution |
| **Queue-Based Load Leveling** | Async scale | Low | Medium | Async delay | • Bursty traffic<br/>• Background jobs |
| **Auto-scaling** | Dynamic | Variable | Medium | Provision time | • Variable load<br/>• Cost optimization |

## Pattern Combination Recommendations

### For High-Traffic APIs
```
API Gateway + Circuit Breaker + Rate Limiting + Caching
```
- **Why**: Complete protection and performance optimization
- **Example**: Netflix, Amazon

### For Microservices Communication
```
Service Mesh + Circuit Breaker + Retry + Distributed Tracing
```
- **Why**: Service-to-service reliability and observability
- **Example**: Uber, Lyft

### For E-commerce Platforms
```
CQRS + Event Sourcing + Saga + API Gateway
```
- **Why**: Handle complex transactions with high read loads
- **Example**: Shopify, eBay

### For Real-time Systems
```
WebSocket + Pub-Sub + Circuit Breaker + Bulkhead
```
- **Why**: Low latency with failure isolation
- **Example**: Discord, Slack

## Quick Decision Flowchart

```mermaid
graph TD
    Start[System Design Need] --> Q1{External<br/>Clients?}
    Q1 -->|Yes| Q2{Multiple<br/>Client Types?}
    Q1 -->|No| Q3{Service<br/>Count?}
    
    Q2 -->|Yes| BFF[Use BFF Pattern]
    Q2 -->|No| GW[Use API Gateway]
    
    Q3 -->|<5| Direct[Direct Communication]
    Q3 -->|>10| Mesh[Use Service Mesh]
    
    GW --> Q4{Failure<br/>Handling?}
    Mesh --> Q4
    BFF --> Q4
    
    Q4 -->|Critical| CB[Add Circuit Breaker]
    Q4 -->|Transient| Retry[Add Retry Logic]
    
    CB --> Q5{Load<br/>Issues?}
    Retry --> Q5
    
    Q5 -->|Yes| RL[Add Rate Limiting]
    Q5 -->|No| Done[Complete Architecture]
    
    style Start fill:#5448C8,stroke:#3f33a6,color:#fff
    style Done fill:#4ade80,stroke:#16a34a
```
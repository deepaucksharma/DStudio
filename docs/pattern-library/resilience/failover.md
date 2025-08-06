---
best_for: Database clusters, network equipment, and traditional active-passive setups
category: resilience
current_relevance: mainstream
description: Automatic switching to backup systems during failures to maintain high
  availability
difficulty: intermediate
essential_question: How do we automatically switch to backup systems when primary
  systems fail without losing user requests?
excellence_tier: silver
introduced: 1990-01
pattern_status: use-with-expertise
prerequisites:
- health-monitoring
- state-replication
- network-routing
reading_time: 15 min
related_laws:
- correlated-failure
- asynchronous-reality
- distributed-knowledge
related_pillars:
- state
- control
tagline: Seamless switching to backup systems when primary systems fail
title: Failover Pattern
trade_offs:
  cons:
  - Requires redundant infrastructure (cost)
  - Split-brain risks without proper fencing
  - Data consistency challenges during switchover
  pros:
  - Provides automatic recovery from failures
  - Maintains service availability during outages
  - Well-understood and mature pattern
type: pattern
---


# Failover Pattern

!!! info "🥈 Silver Tier Pattern"
    **Seamless switching to backup systems** • Essential for high-availability architectures
    
    Mature pattern for automatic recovery from failures. While fundamental for HA, modern systems often combine with multi-region active-active deployments and service mesh retry mechanisms.
    
    **Best For:** Database clusters, network infrastructure, regional disaster recovery

## Essential Question

**How do we automatically switch to backup systems when primary systems fail without losing user requests?**

## When to Use / When NOT to Use

### ✅ Use When

| Scenario | Example | Impact |
|----------|---------|--------|
| Critical data stores | Primary/replica databases | Zero data loss requirement |
| Network infrastructure | Redundant routers/switches | Maintain connectivity |
| Regional outages | Multi-region applications | Disaster recovery |
| Stateful services | Session-based applications | Preserve user state |

### ❌ DON'T Use When

| Scenario | Why | Alternative |
|----------|-----|-------------|
| Stateless microservices | Overhead unnecessary | Load balancing + retry |
| Development environments | Cost not justified | Single instance |
| Read-heavy workloads | Active-active better | Multi-master replication |
| Serverless functions | Built-in redundancy | Platform handles it |

## Level 1: Intuition (5 min) {#intuition}

### Hospital Emergency Power Analogy

### Core Insight
> **Key Takeaway:** Failover trades resource efficiency for availability - you pay for idle backups to ensure continuous service.

## Level 2: Foundation (10 min) {#foundation}

### The Problem Space

<div class="failure-vignette">
<h4>🚨 What Happens Without Failover</h4>

**GitHub, 2018**: Database server crash caused 24-hour outage. No automated failover meant manual intervention required, extended downtime while engineers diagnosed and switched to replica.

**Impact**: $10M+ in lost productivity across developer community, significant reputation damage
</div>

### Failover Architecture Types

### Failover Timing Comparison

| Type | Detection Time | Switch Time | Total RTO | Data Loss (RPO) | Cost |
|------|----------------|-------------|-----------|-----------------|------|
| **Active-Passive** | 10-30s | 30s-5m | 1-6m | < 1 min | Low |
| **Active-Active** | < 1s | < 1s | < 2s | Zero | High |
| **Pilot Light** | 30s | 10-30m | 10-30m | < 15 min | Lowest |
| **Warm Standby** | 10s | 30s-2m | 1-3m | < 5 min | Medium |

## Level 3: Deep Dive (15 min) {#deep-dive}

### Failover State Machine

### Critical Design Decisions

| Decision | Options | Trade-off | Recommendation |
|----------|---------|-----------|----------------|
| **Detection Method** | Health checks<br>Heartbeat<br>Gossip | Speed vs. Accuracy | Health checks for simplicity |
| **Switchover Trigger** | Automatic<br>Manual approval | Speed vs. Control | Automatic with manual override |
| **State Handling** | Sync replication<br>Async replication | Performance vs. Consistency | Async with bounded lag |
| **Failback Policy** | Automatic<br>Scheduled<br>Manual | Risk vs. Convenience | Scheduled during low traffic |

## Decision Matrix

| Factor | Score (1-5) | Reasoning |
|--------|-------------|-----------|
| **Complexity** | 4 | State synchronization, split-brain prevention, health monitoring, failback logic |
| **Performance Impact** | 3 | Replication overhead, but enables high availability and disaster recovery |
| **Operational Overhead** | 4 | Monitoring health, testing failover, managing state sync, capacity planning |
| **Team Expertise Required** | 4 | Understanding of distributed state, networking, monitoring, disaster recovery |
| **Scalability** | 3 | Provides availability scaling but resource duplication limits efficiency |

**Overall Recommendation: ⚠️ USE WITH EXPERTISE** - Critical for HA but requires careful design to prevent split-brain scenarios.

### Common Pitfalls

<div class="decision-box">
<h4>⚠️ Avoid These Mistakes</h4>

1. **Split-brain scenario**: Both systems think they're primary → Use proper fencing/quorum
2. **Cascading failover**: Backup can't handle load → Test capacity regularly
3. **Data divergence**: Writes during failover → Implement proper state synchronization
4. **Failover loops**: Systems keep switching → Add dampening/cooldown periods
</div>

## Level 4: Expert (20 min) {#expert}

### Advanced Failover Strategies

#### Multi-Region Failover Architecture

### Failover Decision Algorithm

### Monitoring & Alerting

| Metric | Normal | Warning | Critical | Action |
|--------|--------|---------|----------|--------|
| Health Check Success | 100% | < 99% | < 95% | Investigate |
| Replication Lag | < 1s | 1-5s | > 5s | Pause writes |
| Failover Time | N/A | > 30s | > 60s | Review process |
| Split-brain Detection | False | N/A | True | Emergency response |

## Level 5: Mastery (25 min) {#mastery}

### Real-World Case Studies

<div class="truth-box">
<h4>💡 Netflix's Regional Failover Strategy</h4>

**Challenge**: Maintain streaming service during AWS region failures

**Implementation**: 
- Active-active across 3 regions
- Stateless microservices with regional data caches
- Chaos testing with controlled regional failures
- Customer-aware traffic routing

**Results**: 
- < 1 minute regional failover time
- 99.99% availability maintained
- Zero customer-visible outages during regional failures
- 40% reduction in cross-region traffic costs

**Key Learning**: Test failover more than you think necessary - their monthly chaos tests revealed issues automated testing missed
</div>

### Failover Economics

| Strategy | Infrastructure Cost | Operational Cost | Availability | Best For |
|----------|-------------------|------------------|--------------|----------|
| **Active-Passive** | 1.5x | Low | 99.9% | Cost-sensitive |
| **Active-Active** | 2x | Medium | 99.99% | Business critical |
| **Multi-Region** | 3x+ | High | 99.999% | Global scale |
| **Pilot Light** | 1.2x | Medium | 99.5% | Disaster recovery |

### Testing Strategies

## Quick Reference

### Decision Flowchart

### Implementation Checklist

**Pre-Implementation**
- [ ] Define RTO and RPO requirements
- [ ] Map all stateful components
- [ ] Design replication strategy
- [ ] Plan network routing changes

**Implementation**
- [ ] Set up health monitoring
- [ ] Configure replication
- [ ] Implement failover logic
- [ ] Add split-brain prevention

**Post-Implementation**
- [ ] Test failover monthly
- [ ] Monitor replication lag
- [ ] Document runbooks
- [ ] Train operations team

### Related Resources

<div class="grid cards" markdown>

- :material-book-open-variant:{ .lg .middle } **Related Patterns**
    
    ---
    
    - [Health Check](./health-check.md) - Detect when failover needed
    - [Circuit Breaker](./circuit-breaker.md) - Prevent cascading failures
    - [Load Balancing](../scaling/load-balancing.md) - Distribute during normal operation

- :material-flask:{ .lg .middle } **Fundamental Laws**
    
    ---
    
    - [Law 1: Correlated Failure](../../core-principles/laws/correlated-failure.md) - Independent failure domains
    - [Law 2: Asynchronous Reality](../../core-principles/laws/asynchronous-reality.md) - Handle replication delays
    - [Law 5: Distributed Knowledge](../../core-principles/laws/distributed-knowledge.md) - Prevent split-brain

</div>


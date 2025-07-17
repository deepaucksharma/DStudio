# Reference Guide

!!! info "Quick Reference"
    Essential references, cheat sheets, and glossary for distributed systems concepts.

!!! tip "Quick Navigation"
    [← Home](../index.md) |
    [Glossary →](glossary.md) |
    [Cheat Sheets →](cheat-sheets.md)

## Quick Reference Sections

<div class="grid cards">
  <div class="card">
    <h3>📖 Glossary</h3>
    <p>Comprehensive glossary of distributed systems terms, acronyms, and concepts.</p>
    <a href="glossary/" class="md-button md-button--primary">View Glossary</a>
  </div>

  <div class="card">
    <h3>📋 Cheat Sheets</h3>
    <p>Quick reference cards for formulas, patterns, and decision frameworks.</p>
    <a href="cheat-sheets/" class="md-button md-button--primary">View Cheat Sheets</a>
  </div>

  <div class="card">
    <h3>🔢 Formulas</h3>
    <p>Key mathematical formulas and their applications in distributed systems.</p>
    <a href="formulas/" class="md-button md-button--primary">View Formulas</a>
  </div>

  <div class="card">
    <h3>⚡ Patterns</h3>
    <p>Common distributed systems patterns and anti-patterns reference.</p>
    <a href="patterns-reference/" class="md-button md-button--primary">View Patterns</a>
  </div>
</div>

## Quick Lookup

### The 8 Axioms

| Axiom | Principle | Key Insight |
|-------|-----------|-------------|
| 1 | **Latency** | Physics can't be beaten |
| 2 | **Capacity** | Everything has limits |
| 3 | **Partial Failure** | Failure is partial and inevitable |
| 4 | **Concurrency** | Time has many meanings |
| 5 | **Coordination** | Agreement has a cost |
| 6 | **Observability** | You can't debug what you can't see |
| 7 | **Human Interface** | Complexity breeds errors |
| 8 | **Economics** | Hidden costs dominate |

### The 5 Pillars

| Pillar | Distribution of | Core Challenge |
|--------|----------------|----------------|
| 1 | **Work** | Load balancing and routing |
| 2 | **State** | Consistency vs availability |
| 3 | **Truth** | Consensus and agreement |
| 4 | **Control** | Autonomous operation |
| 5 | **Intelligence** | Learning and adaptation |

### Key Numbers to Remember

<div class="numbers-grid">
  <div class="number-box">
    <h4>Speed of Light</h4>
    <p><strong>200,000 km/s</strong> in fiber</p>
    <p>~5ms per 1000km one-way</p>
  </div>

  <div class="number-box">
    <h4>Disk Latencies</h4>
    <p>HDD: <strong>10ms</strong></p>
    <p>SSD: <strong>0.1ms</strong></p>
    <p>NVMe: <strong>0.02ms</strong></p>
  </div>

  <div class="number-box">
    <h4>Network Latencies</h4>
    <p>Same DC: <strong>0.5ms</strong></p>
    <p>Cross-AZ: <strong>2ms</strong></p>
    <p>Cross-Region: <strong>50ms+</strong></p>
  </div>

  <div class="number-box">
    <h4>Human Perception</h4>
    <p>Instant: <strong><100ms</strong></p>
    <p>Fast: <strong>100-300ms</strong></p>
    <p>Sluggish: <strong>>1s</strong></p>
  </div>
</div>

### Common Formulas

| Formula | Name | Application |
|---------|------|-------------|
| `L = λW` | Little's Law | Queue length calculation |
| `R = S/(1-ρ)` | Response Time | M/M/1 queue response |
| `A = MTBF/(MTBF+MTTR)` | Availability | Single component uptime |
| `P(k) = (λt)^k * e^(-λt) / k!` | Poisson | Event probability |

### Decision Quick Reference

<div class="decision-matrix">
<h4>Consistency vs Availability</h4>

| Choose **Consistency** | Choose **Availability** |
|------------------------|-------------------------|
| Financial transactions | Social media feeds |
| Inventory management | Analytics data |
| User authentication | Recommendation engines |
| Configuration changes | Monitoring metrics |
</div>

<div class="decision-matrix">
<h4>Synchronous vs Asynchronous</h4>

| Use **Synchronous** | Use **Asynchronous** |
|---------------------|----------------------|
| User-facing APIs | Background processing |
| Database queries | Email sending |
| Authentication | Report generation |
| Payment processing | Data synchronization |
</div>

## Failure Probabilities

### Component Reliability

| Component | Typical MTBF | Annual Failure Rate |
|-----------|--------------|---------------------|
| Server | 3-5 years | 20-33% |
| Disk (HDD) | 3-4 years | 25-33% |
| Disk (SSD) | 5-7 years | 14-20% |
| Network Switch | 5-10 years | 10-20% |
| Power Supply | 5-7 years | 14-20% |

### System Availability Targets

| Availability | Allowed Downtime/Year | Allowed Downtime/Month |
|--------------|----------------------|------------------------|
| 99% (2 nines) | 3.65 days | 7.31 hours |
| 99.9% (3 nines) | 8.77 hours | 43.83 minutes |
| 99.99% (4 nines) | 52.60 minutes | 4.38 minutes |
| 99.999% (5 nines) | 5.26 minutes | 26.30 seconds |

## Anti-Patterns Reference

### Common Distributed Systems Anti-Patterns

1. **Distributed Monolith**: Microservices that can't deploy independently
2. **Chatty Services**: Excessive synchronous communication
3. **Shared Database**: Multiple services sharing data store
4. **Synchronous Chains**: Long chains of blocking calls
5. **No Circuit Breakers**: Cascading failures
6. **Ignore Backpressure**: No flow control
7. **Homogeneous Timeouts**: Same timeout everywhere
8. **No Idempotency**: Retry causes duplication
9. **Ignore Partial Failure**: All-or-nothing thinking
10. **No Observability**: Flying blind

## Useful Conversions

| From | To | Multiply By |
|------|-----|-------------|
| Milliseconds | Microseconds | 1,000 |
| Seconds | Milliseconds | 1,000 |
| Mbps | MB/s | 0.125 |
| GB | GiB | 0.931 |
| Requests/sec | Requests/day | 86,400 |

## Command Quick Reference

### Performance Analysis

```bash
# Network latency
ping -c 10 target.com
traceroute target.com
mtr target.com

# System load
top -b -n 1
iostat -x 1
vmstat 1

# Connection tracking
netstat -an | grep ESTABLISHED
ss -s
```

### Debugging Distributed Systems

```bash
# Distributed tracing
curl -H "X-Trace-ID: $(uuidgen)" service.com

# Check service health
for svc in service1 service2 service3; do
  curl -f http://$svc/health || echo "$svc is down"
done

# Monitor logs across services
multitail -f service1.log -f service2.log -f service3.log
```

## Next Steps

- Explore detailed [Glossary](glossary.md)
- Review [Cheat Sheets](cheat-sheets.md)
- Check [Formulas Reference](formulas.md)
- Study [Patterns Reference](patterns-reference.md)
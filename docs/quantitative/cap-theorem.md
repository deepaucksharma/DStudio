---
title: CAP Theorem Deep-Dive
description: "The fundamental trade-off in distributed systems: you can have at most two of Consistency, Availability, and Partition tolerance"
type: quantitative
difficulty: intermediate
reading_time: 45 min
prerequisites: ["consistency", "network-partitions", "distributed-consensus"]
pattern_type: "fundamental-theorem"
status: complete
last_updated: 2025-01-23
---


# CAP Theorem Deep-Dive

**The impossible trinity of distributed systems**

!!! abstract "🔺 CAP Theorem Statement"

 <div class="formula-highlight">
 <h2>Choose at most 2 of 3:</h2>

| Property | Description | Example |
|----------|-------------|---------|
| **C**onsistency | All nodes see the same data simultaneously | Bank balance is same everywhere |
| **A**vailability | System remains operational | Service always responds |
| **P**artition tolerance | System continues despite network failures | Works during network splits |


!!! info
 💡 <strong>Brewer's Theorem (2000)</strong>: In a distributed system, when a network partition occurs, you must choose between consistency and availability.
</div>

## Quick Example

**Social media post**: During network partition:
- **Choose CP**: Some users can't post (unavailable) but all see same feed
- **Choose AP**: Users can post (available) but feeds may differ temporarily

!!! info "Real Impact"
 **MongoDB (2018)**: 5-hour outage choosing C over A during partition
 
 **Amazon DynamoDB**: Chooses A over C, eventual consistency = 99.999% uptime

## The Mathematical Foundation

### Formal Proof Sketch

!!! note "📐 Proof by Contradiction"
 **Assume**: System has all three properties (C, A, P)
 **Setup**: Two nodes (N1, N2) with network partition between them
 <strong>Step 1:</strong> Client writes value V to N1
 <strong>Step 2:</strong> By Availability, N1 must accept write
 <strong>Step 3:</strong> By Partition tolerance, system continues despite no N1↔N2 communication
 <strong>Step 4:</strong> Client reads from N2
 <strong>Step 5:</strong> By Availability, N2 must respond
 <strong>Step 6:</strong> N2 hasn't received V (partition!), returns old value
 <strong>Contradiction:</strong> Violates Consistency! ❌

<div class="conclusion">
✓ <strong>Therefore</strong>: Can't have all three during partition
</div>

## CAP Combinations in Practice

### CP Systems (Consistency + Partition Tolerance)

!!! info "🔒 CP System Characteristics"
| System | Consistency Model | Availability Trade-off |
 |--------|------------------|------------------------|
 | **Zookeeper** | Sequential consistency | Minority partition unavailable |
 | **HBase** | Strong consistency | Region unavailable during split |
 | **MongoDB (default)** | Linearizable reads | Primary election = downtime |

 <strong>Availability Impact = (Partition Duration) × (Affected Partition %)</strong>
 Example: 30s partition × 40% minority = 12s unavailability for 40% of requests

<div class="visual-diagram">
<svg viewBox="0 0 600 300">
 <!-- Title -->
 <text x="300" y="20" text-anchor="middle" font-weight="bold">CP System During Partition</text>
 
 <!-- Majority partition (available) -->
 <rect x="50" y="50" width="200" height="200" fill="#4CAF50" opacity="0.3" stroke="#4CAF50" stroke-width="2"/>
 <text x="150" y="40" text-anchor="middle" font-weight="bold">Majority (60%)</text>
 <circle cx="100" cy="100" r="20" fill="#4CAF50"/>
 <circle cx="200" cy="100" r="20" fill="#4CAF50"/>
 <circle cx="150" cy="150" r="20" fill="#4CAF50"/>
 <text x="150" y="200" text-anchor="middle">✓ Available</text>
 <text x="150" y="220" text-anchor="middle">✓ Consistent</text>
 
 <!-- Partition line -->
 <line x1="280" y1="50" x2="280" y2="250" stroke="#FF5722" stroke-width="4" stroke-dasharray="10,5"/>
 <text x="280" y="270" text-anchor="middle" fill="#FF5722" font-weight="bold">Network Partition</text>
 
 <!-- Minority partition (unavailable) -->
 <rect x="310" y="50" width="200" height="200" fill="#FF5722" opacity="0.3" stroke="#FF5722" stroke-width="2"/>
 <text x="410" y="40" text-anchor="middle" font-weight="bold">Minority (40%)</text>
 <circle cx="360" cy="100" r="20" fill="#9E9E9E"/>
 <circle cx="460" cy="100" r="20" fill="#9E9E9E"/>
 <text x="410" y="200" text-anchor="middle">✗ Unavailable</text>
 <text x="410" y="220" text-anchor="middle">✓ Consistent</text>
</svg>
</div>

### AP Systems (Availability + Partition Tolerance)

!!! info "🌐 AP System Characteristics"
| System | Consistency Model | Convergence Time |
 |--------|------------------|------------------|
 | **Cassandra** | Eventual consistency | ~100ms typical |
 | **DynamoDB** | Eventual consistency | <1s globally |
 | **CouchDB** | Eventual consistency | Depends on replication |

 <strong>Inconsistency Window = Network Delay + Convergence Time</strong>
 Example: 50ms network + 100ms convergence = 150ms inconsistency

<div class="visual-diagram">
<svg viewBox="0 0 600 300">
 <!-- Title -->
 <text x="300" y="20" text-anchor="middle" font-weight="bold">AP System During Partition</text>
 
 <!-- Partition A (available, divergent) -->
 <rect x="50" y="50" width="200" height="200" fill="#2196F3" opacity="0.3" stroke="#2196F3" stroke-width="2"/>
 <text x="150" y="40" text-anchor="middle" font-weight="bold">Partition A</text>
 <circle cx="100" cy="100" r="20" fill="#2196F3"/>
 <circle cx="200" cy="100" r="20" fill="#2196F3"/>
 <circle cx="150" cy="150" r="20" fill="#2196F3"/>
 <text x="150" y="200" text-anchor="middle">✓ Available</text>
 <text x="150" y="220" text-anchor="middle">Data: v1</text>
 
 <!-- Partition line -->
 <line x1="280" y1="50" x2="280" y2="250" stroke="#FF5722" stroke-width="4" stroke-dasharray="10,5"/>
 <text x="280" y="270" text-anchor="middle" fill="#FF5722" font-weight="bold">Network Partition</text>
 
 <!-- Partition B (available, divergent) -->
 <rect x="310" y="50" width="200" height="200" fill="#9C27B0" opacity="0.3" stroke="#9C27B0" stroke-width="2"/>
 <text x="410" y="40" text-anchor="middle" font-weight="bold">Partition B</text>
 <circle cx="360" cy="100" r="20" fill="#9C27B0"/>
 <circle cx="460" cy="100" r="20" fill="#9C27B0"/>
 <text x="410" y="200" text-anchor="middle">✓ Available</text>
 <text x="410" y="220" text-anchor="middle">Data: v2</text>
</svg>
</div>

### CA Systems (Consistency + Availability)

!!! danger "⚠️ CA Systems: The Myth"
| Property | Single Node | Distributed | Reality |
 |----------|-------------|-------------|---------|
 | Consistency | ✓ Trivial | ✗ Network delays | Can't ignore P |
 | Availability | ✓ No coordination | ✗ Node failures | P happens anyway |
 | Partition tolerance | N/A | Required | Can't opt out |

 !!! warning
 ⚡ <strong>Key Insight</strong>: CA only exists in single-node systems. In distributed systems, partitions are inevitable!

## Quantifying CAP Trade-offs

### Consistency Cost Calculator

!!! note "💰 Strong Consistency Overhead"
| Parameter | Value | Unit |
 |-----------|-------|------|
 | Write nodes (W) | 3 | nodes |
 | Total nodes (N) | 5 | nodes |
 | Network RTT | 10 | ms |
 | Consensus rounds | 2 | - |

 <strong>Write latency = Consensus rounds × max(RTT to W nodes)</strong>
 <strong>= 2 × 10ms = 20ms minimum</strong>
 <strong>99th percentile ≈ 3 × 20ms = 60ms</strong>

<div class="latency-comparison">
<div>Local: 1ms
<div>Consensus: 20ms</div>
</div>
</div>

### Availability Calculation

!!! abstract "📊 System Availability Formula"

 For a CP system requiring majority quorum:

 <div class="formula-highlight">
 P(available) = Σ(k=⌈N/2⌉ to N) C(N,k) × p^k × (1-p)^(N-k)

Where:
- N = total nodes
- p = individual node availability
- k = available nodes
- C(N,k) = combinations

<strong>Example: 5 nodes, 99% individual availability</strong><br>
P(available) = P(3 up) + P(4 up) + P(5 up)<br>
= 0.00098 + 0.04804 + 0.95099<br>
= <span>99.999%</span>
</div>

## PACELC Extension

!!! info "🔄 PACELC: The Complete Picture"
 **CAP + Normal Operation Trade-offs**
 <div>
 <strong>IF</strong> Partition (P) <strong>THEN</strong> Availability (A) <strong>OR</strong> Consistency (C)
 <strong>ELSE</strong> Latency (L) <strong>OR</strong> Consistency (C)

| System | Partition | Else | Trade-off |
|--------|-----------|------|-----------|
| **MongoDB** | PC | EC | Consistency preferred |
| **Cassandra** | PA | EL | Performance preferred |
| **DynamoDB** | PA | EL | Low latency preferred |
| **Spanner** | PC | EC | Global consistency |

</div>

## Real-World CAP Decisions

### Banking System Design

!!! note "🏦 Financial Transaction System"
 **Requirements Analysis**:
| Operation | CAP Choice | Reasoning |
 |-----------|------------|-----------|
 | Balance check | AP | Stale data acceptable |
 | Withdrawal | CP | Must prevent overdraft |
 | Deposit | CP | Must be durable |
 | Transaction history | AP | Eventually consistent OK |

 💡 <strong>Pattern</strong>: Use CP for writes, AP for reads with consistency levels

### E-commerce Platform

!!! info "🛒 Shopping Cart Architecture"
| Component | CAP Choice | SLA Impact |
 |-----------|------------|------------|
 | Product catalog | AP | 99.99% availability |
 | Shopping cart | AP | Merge on conflicts |
 | Inventory | CP | Prevent overselling |
 | Payment | CP | Exactly-once guarantee |

 <div>
 <strong>AP Components</strong>
 Availability: 99.99%
 Latency: <50ms
<div>
<strong>CP Components</strong><br>
Availability: 99.9%<br>
Latency: <200ms
</div>
</div>

## Practical CAP Calculations

### Network Partition Probability

!!! abstract "🔢 Partition Frequency Estimation"

 <div class="responsive-table" markdown>

 | Factor | Value | Impact |
 |--------|-------|--------|
 | Network links | 100 | More links = higher P(partition) |
 | Link MTBF | 10,000 hours | Individual reliability |
 | Topology | Mesh | Redundancy factor |


<strong>Single link failure rate</strong> = 1/10,000 = 0.01% per hour<br>
<strong>P(at least one partition)</strong> = 1 - (1 - 0.0001)^100<br>
= 1 - 0.99^100 ≈ <span>1% per hour</span><br>
<strong>Expected partitions/year</strong> = 0.01 × 24 × 365 ≈ <strong>88 partitions</strong>
</div>

### Consistency Window Calculator

!!! note "⏱️ Eventual Consistency Timing"
| Parameter | Value | Description |
 |-----------|-------|-------------|
 | Replication factor | 3 | Copies of data |
 | Network latency | 50ms | Between regions |
 | Processing time | 10ms | Per update |
 | Anti-entropy interval | 60s | Background sync |

 <svg viewBox="0 0 600 200">
 <!-- Timeline -->
 <line x1="50" y1="100" x2="550" y2="100" stroke="#333" stroke-width="2"/>
 <!-- Events -->
 <circle cx="50" cy="100" r="5" fill="#4CAF50"/>
 <text x="50" y="85" text-anchor="middle">Write</text>
 <circle cx="150" cy="100" r="5" fill="#2196F3"/>
 <text x="150" y="85" text-anchor="middle">Replica 1</text>
 <text x="150" y="120" text-anchor="middle" font-size="12">50ms</text>
 <circle cx="250" cy="100" r="5" fill="#2196F3"/>
 <text x="250" y="85" text-anchor="middle">Replica 2</text>
 <text x="250" y="120" text-anchor="middle" font-size="12">100ms</text>
 <circle cx="350" cy="100" r="5" fill="#FF9800"/>
 <text x="350" y="85" text-anchor="middle">Consistent</text>
 <text x="350" y="120" text-anchor="middle" font-size="12" font-weight="bold">100ms window</text>
 <circle cx="500" cy="100" r="5" fill="#9C27B0"/>
 <text x="500" y="85" text-anchor="middle">Anti-entropy</text>
 <text x="500" y="120" text-anchor="middle" font-size="12">60s (worst case)</text>
 </svg>

## CAP in Modern Systems

### Multi-Region Deployments

!!! info "🌍 Geographic CAP Challenges"
| Regions | RTT | Partition Risk | Common Choice |
 |---------|-----|----------------|---------------|
 | US East-West | 60ms | Low | CP feasible |
 | US-Europe | 100ms | Medium | AP common |
 | US-Asia | 150ms | High | AP required |
 | Global (5 regions) | 200ms+ | Very High | AP + local CP |

 !!! info
 🔍 <strong>Pattern</strong>: Use CP within region, AP across regions with conflict resolution

### Tunable Consistency

!!! note "🎛️ Cassandra's Approach"
 **Consistency Levels**:
| Level | Write Nodes | Read Nodes | Guarantee |
 |-------|------------|------------|-----------|
 | ONE | 1 | 1 | Lowest latency |
 | QUORUM | ⌈(N+1)/2⌉ | ⌈(N+1)/2⌉ | Strong consistency |
 | ALL | N | N | Highest consistency |
 | LOCAL_QUORUM | ⌈(RF+1)/2⌉ | ⌈(RF+1)/2⌉ | DC consistency |

 <strong>Consistency guarantee</strong>: R + W > N
 Example: N=3, W=2, R=2 → 2+2 > 3 ✓ Strong consistency

## Key Takeaways

!!! abstract "🎯 CAP Theorem Essentials"

 1. **Network partitions are inevitable** - Plan for them
 2. **Choose your trade-off explicitly** - Don't let it surprise you
 3. **Different operations need different guarantees** - Mix CP and AP
 4. **Measure your actual CAP behavior** - Theory ≠ Practice
 5. **Consider PACELC** - Normal operation matters too

 <div class="final-thought">
 "CAP theorem doesn't mean you can't have a reliable distributed system.<br>
 It means you must explicitly choose what to sacrifice when things go wrong."
</div>

## Related Topics

- [Consistency Models](consistency-models.md) - Deep dive into consistency levels
- [Consensus Algorithms](/patterns/consensus-algorithms) - Achieving agreement
- [Network Partitions](/part1-axioms/law1-failure/) - Understanding failure modes
- [Eventual Consistency](/patterns/eventual-consistency) - AP system patterns
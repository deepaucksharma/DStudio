---
title: Quantitative Analysis
description: Quantitative Analysis overview and navigation
---

# Quantitative Analysis

Mathematical tools and models for distributed systems design, capacity planning, and reliability engineering.

## Overview

This section provides the mathematical foundations every distributed systems architect needs. These quantitative tools help you:

- **Model Performance** - Predict system behavior under load
- **Ensure Reliability** - Calculate availability and failure scenarios  
- **Plan Capacity** - Size infrastructure correctly
- **Make Trade-offs** - Quantify architectural decisions

## 🔬 Fundamental Theorems

Core mathematical laws that govern distributed systems behavior:

### Consistency & Distribution
- **[CAP Theorem](../../pattern-library/architecture/cap-theorem.md)** - The impossible trinity: Consistency, Availability, Partition tolerance
- **[PACELC Theorem](cap-theorem-enhanced.md)** - Extended CAP with latency/consistency trade-offs
- **[FLP Impossibility](../architects-handbook/quantitative-analysis/consensus.md)** - Consensus impossibility in asynchronous systems

### Performance Laws
- **[Little's Law](../architects-handbook/quantitative-analysis/littles-law.md)** - Universal relationship: L = λW (queue length = arrival rate × wait time)
- **[Amdahl's Law](../architects-handbook/quantitative-analysis/amdahls-law.md)** - Limits of parallelization: speedup bounded by sequential portion
- **[Universal Scalability Law](../architects-handbook/quantitative-analysis/universal-scalability.md)** - Contention and coherence limits to scaling
- **[Queueing Theory](../architects-handbook/quantitative-analysis/queueing-theory.md)** - M/M/1, M/M/c models for system behavior under load

## 📊 Performance Analysis

Tools for modeling and predicting system performance:

### Latency & Throughput
- **[Latency Numbers](../architects-handbook/quantitative-analysis/latency-numbers.md)** - Key latencies every architect should know (L1: 0.5ns → Internet: 150ms)
- **[Performance Modeling](../architects-handbook/quantitative-analysis/performance-modeling.md)** - End-to-end latency calculation and bottleneck analysis
- **[Capacity Planning](capacity-planning.md)** - Resource sizing and growth projections

### Load Characteristics
- **[Workload Patterns](time-series.md)** - Daily, weekly, seasonal variations
- **[Power Laws](power-laws.md)** - 80/20 rule, Zipf distributions in real systems
- **[Traffic Theory](network-theory.md)** - Poisson arrivals, bursty traffic modeling

## 🛡️ Reliability Mathematics

Quantifying and improving system reliability:

### Availability Calculations
- **[Failure Models](../architects-handbook/quantitative-analysis/failure-models.md)** - Types of failures and their probabilities
- **[Availability Math](availability-math.md)** - Computing nines (99.9% = 8.76h/year downtime)
- **[MTBF/MTTR](mtbf-mttr.md)** - Mean time between failures and recovery

### Redundancy & Resilience
- **[N+K Redundancy](reliability-theory.md)** - Calculating redundancy requirements
- **[Blast Radius](blast-radius.md)** - Failure impact analysis and containment
- **[Markov Models](markov-chains.md)** - State-based reliability modeling

## 💰 Capacity Planning

Sizing systems for current and future needs:

### Resource Estimation
- **[Capacity Models](capacity-planning.md)** - CPU, memory, storage, network sizing
- **[Growth Projections](time-series.md)** - Linear, exponential, S-curve growth patterns
- **[Utilization Targets](queueing-models.md)** - Why 70% utilization is often optimal

### Cost Optimization
- **[Cost Models](storage-economics.md)** - Storage, compute, and bandwidth economics
- **[Cache Economics](cache-economics.md)** - When caching saves money
- **[Trade-off Analysis](coordination-costs.md)** - Quantifying consistency vs performance costs

## 🎯 Quick Reference

### Essential Formulas

| Concept | Formula | When to Use |
|---------|---------|-------------|
| **Little's Law** | L = λW | Sizing queues, thread pools, connection pools |
| **Availability** | A = MTBF/(MTBF+MTTR) | SLA calculations, redundancy planning |
| **Amdahl's Law** | S = 1/(s + p/n) | Evaluating parallelization benefits |
| **Queue Wait Time** | W = 1/(μ-λ) | Response time under load (M/M/1) |
| **Failure Probability** | P = 1-(1-p)^n | Independent failure scenarios |

### Key Numbers to Remember

| Metric | Value | Impact |
|--------|-------|--------|
| **L1 Cache** | 0.5 ns | 100x faster than RAM |
| **Network RTT** | 150 ms | Internet round trip |
| **Disk Seek** | 10 ms | 20,000x slower than RAM |
| **99.9% Uptime** | 8.76 hours/year | ~1 hour/month downtime |
| **70% Utilization** | Queue stability | Exponential wait time above this |

### Rules of Thumb

1. **Latency Hierarchy**: Cache → Memory → Disk → Network (each 100-1000x slower)
2. **Redundancy**: N+1 for availability, 2N+1 for consensus, 3x for geo-redundancy
3. **Load Distribution**: 80% of load from 20% of users (power law)
4. **Capacity Planning**: Plan for 2x expected peak, monitor at 70% utilization
5. **Failure Rates**: 1% annual server failure, 0.1% monthly disk failure

## 📈 Interactive Tools

### Calculators in This Section
- Little's Law calculator (in littles-law.md)
- Availability/uptime calculator (in availability-math.md)
- Amdahl's Law speedup calculator (in amdahls-law.md)
- Queue wait time calculator (in queueing-theory.md)

### External Resources
- [Google SRE Workbook](https://sre.google/workbook/index.md) - Practical reliability calculations
- [AWS Architecture Center](https://aws.amazon.com/architecture/index.md) - Real-world capacity planning
- [High Scalability](http://highscalability.com/index.md) - Case studies with numbers

## 🚀 Getting Started

1. **Start with [Little's Law](../architects-handbook/quantitative-analysis/littles-law.md)** - The most fundamental relationship in systems
2. **Understand [CAP Theorem](../../pattern-library/architecture/cap-theorem.md)** - Core distributed systems trade-off
3. **Learn [Latency Numbers](../architects-handbook/quantitative-analysis/latency-numbers.md)** - Build intuition for system performance
4. **Master [Queueing Theory](../architects-handbook/quantitative-analysis/queueing-theory.md)** - Predict behavior under load

---

*Remember: These models are simplifications of reality. Use them to build intuition and make order-of-magnitude estimates, but always validate with real-world measurements.*
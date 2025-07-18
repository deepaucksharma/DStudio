# Essential Distributed Systems Formulas

!!! tip "Quick Navigation"
    [← Reference Home](index.md) | 
    [Cheat Sheets](cheat-sheets.md) |
    [Glossary](glossary.md)

## Latency Formulas

### Network Latency
```
Total Latency = Propagation Delay + Transmission Delay + Processing Delay + Queueing Delay

Propagation Delay = Distance / Speed of Light in Medium
Transmission Delay = Data Size / Bandwidth
```

### Speed of Light Limits
- Fiber optic cable: ~200,000 km/s (2/3 speed of light in vacuum)
- Copper wire: ~200,000 km/s
- Wireless: ~300,000 km/s (speed of light in air)

### Round Trip Time (RTT)
```
RTT = 2 × One-way Latency
Minimum RTT = 2 × (Distance / Speed of Light in Medium)
```

## Capacity & Throughput Formulas

### Little's Law
```
L = λ × W

Where:
L = Average number of requests in system
λ = Average arrival rate
W = Average time in system
```

### Utilization
```
Utilization (ρ) = λ / μ

Where:
λ = Arrival rate
μ = Service rate
```

### Queue Length (M/M/1 Queue)
```
Average Queue Length = ρ² / (1 - ρ)
Average System Length = ρ / (1 - ρ)
```

## Reliability Formulas

### System Availability
```
Availability = MTTF / (MTTF + MTTR)

Where:
MTTF = Mean Time To Failure
MTTR = Mean Time To Repair
```

### Parallel System Reliability
```
R_parallel = 1 - (1 - R₁) × (1 - R₂) × ... × (1 - Rₙ)
```

### Series System Reliability
```
R_series = R₁ × R₂ × ... × Rₙ
```

### Annual Downtime
```
Downtime per year = (1 - Availability) × 365.25 × 24 × 60 minutes
```

| Availability | Downtime/Year | Downtime/Month | Downtime/Week |
|-------------|---------------|----------------|---------------|
| 99% (2 nines) | 3.65 days | 7.31 hours | 1.68 hours |
| 99.9% (3 nines) | 8.77 hours | 43.83 minutes | 10.08 minutes |
| 99.99% (4 nines) | 52.60 minutes | 4.38 minutes | 1.01 minutes |
| 99.999% (5 nines) | 5.26 minutes | 26.30 seconds | 6.05 seconds |

## Consensus & Quorum Formulas

### Quorum Requirements
```
For N replicas:
Write Quorum (W) + Read Quorum (R) > N  (ensures consistency)
```

### Common Configurations
- **Read-heavy**: W = N, R = 1
- **Write-heavy**: W = 1, R = N
- **Balanced**: W = R = ⌊N/2⌋ + 1

### Byzantine Fault Tolerance
```
To tolerate f Byzantine failures:
N ≥ 3f + 1 nodes required
```

## Sharding & Partitioning

### Consistent Hashing Load
```
Expected load per node = Total Keys / Number of Nodes
Standard deviation ≈ √(Total Keys / Number of Nodes)

With virtual nodes:
Load variance reduces by factor of √K (K = virtual nodes per physical node)
```

### Partition Key Distribution
```
Ideal partition size = Total Data Size / Number of Partitions
Skew factor = Max Partition Size / Average Partition Size
```

## Performance Modeling

### Amdahl's Law
```
Speedup = 1 / (S + P/N)

Where:
S = Serial portion of program
P = Parallel portion (1 - S)
N = Number of processors
```

### Universal Scalability Law
```
C(N) = N / (1 + α(N-1) + βN(N-1))

Where:
C(N) = Capacity with N nodes
α = Contention parameter
β = Coherency parameter
```

## Cost Formulas

### Total Cost of Ownership (TCO)
```
TCO = Infrastructure Cost + Operational Cost + Development Cost

Where:
Infrastructure = Servers + Storage + Network + Facilities
Operational = Power + Cooling + Administration + Support
Development = Initial + Maintenance + Migration
```

### Cost per Request
```
Cost per Request = (Total Monthly Cost) / (Requests per Month)
```

### Storage Cost
```
Storage Cost = (Data Size × Replication Factor × $/GB) + (IOPS × $/IOPS)
```

## Network Formulas

### Bandwidth Delay Product
```
BDP = Bandwidth × RTT
(Maximum amount of data in flight)
```

### TCP Throughput (simplified)
```
Throughput ≤ (Window Size) / RTT
Throughput ≤ 1.22 × MSS / (RTT × √packet_loss)
```

## Quick Reference Card

### Common Constants
- Speed of light in vacuum: 299,792 km/s
- Speed in fiber: ~200,000 km/s
- Earth circumference: ~40,000 km
- Minimum RTT around Earth: ~200ms
- Typical data center RTT: 0.5-2ms
- Cross-region RTT: 50-150ms

### Rule of Thumb Conversions
- 1 million requests/day ≈ 12 requests/second
- 1 GB/day ≈ 12 KB/second
- 99.9% availability ≈ 45 minutes downtime/month
- Double the nodes ≠ Double the performance (due to coordination overhead)

!!! example "Usage Example"
    **Q**: What's the minimum latency between New York and London?
    
    **A**: Distance ≈ 5,570 km
    - In fiber: 5,570 km ÷ 200,000 km/s = 27.85 ms (one way)
    - RTT: 2 × 27.85 ms = **55.7 ms minimum**
    - Real-world: Add 20-40% for routing, processing = **70-80 ms typical**
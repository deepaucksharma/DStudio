# Collision Probability

## Overview

Collision probability is fundamental to distributed systems design, affecting everything from hash tables to distributed consensus. Understanding the mathematics helps design systems that minimize conflicts and handle them gracefully.

## Core Concepts

### Birthday Paradox

The probability of collision in a uniform hash space:

```
P(collision) = 1 - (n!/(n^k × (n-k)!))
```

Where:
- n = size of hash space
- k = number of items

**Approximation for small k:**
```
P(collision) ≈ 1 - e^(-k²/2n)
```

### 50% Collision Threshold

For various hash sizes:
- 32-bit: ~77,000 items
- 64-bit: ~5.1 billion items
- 128-bit: ~2.2 × 10^19 items
- 256-bit: ~4.0 × 10^38 items

## Hash Collision Models

### Uniform Hashing

**Assumptions:**
- Each hash value equally likely
- Independent hash functions
- No correlation between inputs

**Collision probability after k insertions:**
```
P = 1 - ∏(i=0 to k-1)[(n-i)/n]
```

### Load Factor Analysis

For hash table with m buckets and n items:
```
Load factor α = n/m
Expected collisions = n × (1 - (1 - 1/m)^(n-1))
```

### Chaining vs Open Addressing

**Chaining:**
- Expected chain length = α
- Variance = α(1 - 1/m)

**Open Addressing:**
- Expected probes = 1/(1-α)
- Clustering effect increases collisions

## Distributed System Collisions

### UUID Collisions

**UUID v4 (122 random bits):**
```
P(collision) = 1 - e^(-n²/2^123)
```

For 1 billion UUIDs:
- P(collision) ≈ 4.86 × 10^-22

**UUID v1 (time-based):**
- Collision requires same timestamp AND MAC
- P(collision) ≈ 0 with proper clock sync

### Consistent Hashing

**Virtual nodes collision:**
```
P(two nodes same position) = 1/2^hash_bits
P(any collision with v vnodes) = 1 - (1 - 1/2^hash_bits)^(v×n)
```

### Vector Clock Collisions

**Node ID collisions:**
```
With k-bit node IDs and n nodes:
P(collision) = 1 - e^(-n²/2^(k+1))
```

## Probability Calculations

### Exact Formulas

**First collision expected after:**
```
E[first collision] = √(π × n/2)
```

**Collision-free probability:**
```
P(no collision) = ∏(i=1 to k-1)[(n-i)/n]
```

### Approximations

**Poisson approximation (λ = k²/2n):**
```
P(exactly c collisions) ≈ (λ^c × e^(-λ))/c!
```

**Normal approximation (large n, k):**
```
Number of collisions ~ N(μ = k²/2n, σ² = k²/2n)
```

## Bloom Filter Collisions

### False Positive Rate

With m bits, n items, k hash functions:
```
P(false positive) = (1 - e^(-kn/m))^k
```

**Optimal k:**
```
k_optimal = (m/n) × ln(2) ≈ 0.693 × (m/n)
```

**Resulting FPR:**
```
P_optimal ≈ 0.6185^(m/n)
```

### Capacity Planning

For target false positive rate p:
```
m = -n × ln(p) / (ln(2)²)
k = -ln(p) / ln(2)
```

## Cryptographic Collisions

### Hash Function Security

**Collision resistance:**
- Find any x, y where H(x) = H(y)
- Difficulty: O(2^(n/2)) for n-bit hash

**Examples:**
- MD5 (128-bit): Broken, collisions in seconds
- SHA-1 (160-bit): Broken, collisions feasible
- SHA-256 (256-bit): Secure, 2^128 operations

### Merkle Tree Collisions

**Probability of finding collision in tree:**
```
P = 1 - (1 - 2^(-hash_bits))^comparisons
comparisons = tree_size × log(tree_size)
```

## Network Protocol Collisions

### MAC Address Collisions

**Local network (n devices):**
```
P(collision) = 1 - e^(-n²/2^49)
```
(48 bits total, but first bit indicates local/global)

**Practical threshold:**
- 1% collision risk: ~370,000 devices
- 0.1% collision risk: ~117,000 devices

### TCP Sequence Numbers

**32-bit initial sequence number:**
```
P(collision) = previous_connections / 2^32
Wraparound time = 2^32 / bandwidth
```

**Protection:**
- TIME_WAIT state (2×MSL)
- Timestamp options

## Collision Resolution

### Quadratic Probing

**Probe sequence:** h(k) + c₁i + c₂i²

**Collision clusters:**
```
Expected cluster size = 1 + α + 2α² + 5α³ + ...
```

### Cuckoo Hashing

**With 2 hash functions:**
```
Maximum load before failure ≈ 0.5
P(insertion fails) ≈ O(1/n)
```

**With d hash functions:**
```
Maximum load ≈ 1 - e^(-d) × d!^(1/d)
```

## Real-World Applications

### Git Commit Hashes

**SHA-1 (160 bits):**
```
P(collision in repo with n commits) ≈ n²/2^161
```

**For 1 million commits:**
- P(collision) ≈ 3.4 × 10^-37

### Distributed Tracing

**Trace ID collisions (128-bit):**
```
Traces per second for 1% collision in 1 year:
n = √(0.01 × 2^128 / seconds_per_year) ≈ 10^15
```

### Database Sharding

**Shard key collisions affect:**
```
Hot shard probability = max_i(items_in_shard_i) / total_items
Imbalance factor = max_load / average_load
```

## Design Guidelines

### Choosing Hash Sizes

| Use Case | Recommended Bits | Collision Threshold |
|----------|------------------|-------------------|
| Session IDs | 128 | 10^19 sessions |
| Request IDs | 64 | 5 billion requests |
| Cache keys | 32-64 | Depends on size |
| Crypto hashes | 256+ | Cryptographic security |

### Safety Margins

**Rule of thumb:**
```
Hash bits = 2 × log₂(expected_items) + safety_margin
safety_margin = 20-40 bits
```

### Collision Handling

1. **Detection:**
   - Check on insert
   - Periodic scanning
   - Probabilistic counting

2. **Resolution:**
   - Chaining
   - Rehashing
   - Conflict queues

## Advanced Topics

### Minimal Perfect Hashing

**Construction complexity:** O(n³)
**Query time:** O(1)
**Space:** 2.7 bits per key

### Locality-Sensitive Hashing

**Collision probability:**
```
P(collision | similar) = p₁
P(collision | dissimilar) = p₂
Gap: p₁/p₂ > threshold
```

### Quantum Collision Finding

**Grover's algorithm:**
- Classical: O(2^(n/2))
- Quantum: O(2^(n/3))
- Impact: Need 50% more bits

## Related Topics

- [Hash Functions](../patterns/consistent-hashing.md)
- [Probabilistic Data Structures](probabilistic-structures.md)
- [Information Theory](information-theory.md)
- [Cryptographic Primitives](../reference/security-considerations.md)
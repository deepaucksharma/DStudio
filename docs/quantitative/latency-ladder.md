# Latency Ladder 2025

**Know your physics: Every operation has a cost**

## The Fundamental Latency Hierarchy

Understanding latency is crucial for system design. Here's how long common operations take, with human-scale analogies:

```
Operation                          Time (ns)     Time (human scale)
---------                          ---------     ------------------
L1 cache reference                      0.5 ns   0.5 seconds
Branch mispredict                       5 ns     5 seconds
L2 cache reference                      7 ns     7 seconds
Mutex lock/unlock                      25 ns     25 seconds
Main memory reference                 100 ns     1.5 minutes
Compress 1KB (Zippy)                2,000 ns     33 minutes
Send 1KB over 1 Gbps               10,000 ns     2.8 hours
Read 4KB random from SSD           16,000 ns     4.4 hours
Read 1MB sequentially from memory 250,000 ns     2.9 days
Round trip within datacenter       500,000 ns     5.8 days
Read 1MB from SSD                1,000,000 ns    11.6 days
Disk seek                        10,000,000 ns    3.8 months
Read 1MB from disk              20,000,000 ns     7.6 months
Send packet CA → Netherlands    150,000,000 ns     4.8 years
```

## 2025 Update: Modern Hardware

Technology evolves, but physics remains constant. Here's what's changed:

```
Operation                          Latency         Notes
---------                          -------         -----
NVMe SSD random read               10 μs           10x faster than 2015
Optane persistent memory           100 ns          Between RAM and SSD
RDMA network transfer              1-2 μs          Bypass kernel
GPU memory transfer                10-100 μs       Depends on size
5G mobile network latency          1-10 ms         10x better than 4G
Starlink satellite latency         20-40 ms        LEO constellation
Cross-region (optimized path)      30-80 ms        Private backbone
Edge compute                       <5 ms           Local processing
```

## Latency Budget Calculator

Understanding where your milliseconds go:

```
User-Perceived Latency Budget:
100ms - Instant
200ms - Fast  
500ms - Acceptable
1s    - Noticeable
3s    - Annoying
10s   - User leaves

Backend Budget Breakdown:
Total Budget:           1000 ms
- Network RTT:          -50 ms   (user to edge)
- TLS handshake:        -30 ms   (cached session)
- Load balancer:        -2 ms
- API gateway:          -5 ms
- Service mesh:         -3 ms
- Business logic:       -X ms    (your code)
- Database query:       -20 ms
- Serialization:        -5 ms
- Response network:     -50 ms
= Remaining:            835 ms for your logic
```

## Compound Latency Effects

Latencies combine differently based on architecture:

```
Serial Operations (add):
A → B → C = Latency(A) + Latency(B) + Latency(C)

Parallel Operations (max):
A ⟋ B ⟋ C = MAX(Latency(A), Latency(B), Latency(C))

Percentile Multiplication:
If each service is 99% under 100ms
Two serial calls: 98% under 200ms
Three serial calls: 97% under 300ms
Ten serial calls: 90% under 1000ms!
```

## Real-World Latency Targets

Different industries have different requirements:

```
Industry            Operation                Target      Why
--------            ---------                ------      ---
HFT Trading         Order execution          <1 μs       Competitive advantage
Gaming              Input to screen          16 ms       60 FPS requirement
Video call          End-to-end audio         150 ms      Natural conversation
Web search          Query to results         200 ms      User satisfaction
E-commerce          Add to cart              300 ms      Conversion rate
Streaming           Start playback           2 s         User retention
Email               Send confirmation        5 s         User expectation
```

## Latency Reduction Strategies

Practical approaches to reduce latency:

```
Strategy                    Typical Improvement    Cost
--------                    -------------------    ----
Add regional cache          50-90%                 $
Use CDN                     40-80%                 $
Optimize queries            20-50%                 $
Add indexes                 30-70%                 $
Batch operations            40-60%                 $
Parallel processing         30-50%                 $
Better algorithms           10-90%                 $
Hardware upgrade            20-40%                 $$
Protocol optimization       10-30%                 $
Connection pooling          20-40%                 $
```

## Practical Examples

### Example 1: E-commerce Checkout
```
User clicks "Buy Now" → Order confirmed

Latency breakdown:
- User → CDN edge: 20ms
- Edge → Region: 30ms
- API Gateway: 5ms
- Auth service: 10ms
- Inventory check: 15ms (parallel)
- Payment processing: 100ms (parallel)
- Order creation: 20ms
- Confirmation email: Async
Total: ~200ms perceived
```

### Example 2: Real-time Gaming
```
Player input → Other players see action

Latency breakdown:
- Input polling: 8ms (120Hz)
- Client → Server: 30ms
- Server processing: 5ms
- Server → Other clients: 30ms
- Render: 8ms
Total: ~81ms

Budget: 100ms for good experience
Margin: 19ms for jitter
```

### Example 3: Database Query Optimization
```
Before: Sequential queries
- Get user: 10ms
- Get orders: 20ms  
- Get items per order: 10ms × N
Total: 30ms + 10N ms

After: Batch + parallel
- Get user + orders: 15ms (join)
- Get all items: 15ms (IN clause)
Total: 30ms (constant!)
```

## Key Takeaways

1. **Cache references are 200,000x faster than network calls** - Design to minimize network hops
2. **Memory is 100x faster than SSD** - Keep hot data in RAM
3. **Same-datacenter is 300x faster than cross-region** - Locality matters
4. **Parallel operations hide latency** - But add complexity
5. **Measure actual latencies** - Hardware varies, networks congest

## Rules of Thumb

- **1ms** - Same machine operation threshold
- **10ms** - Same datacenter threshold  
- **100ms** - Human perception threshold
- **1000ms** - User patience threshold

Remember: You can't beat physics, but you can work with it.
Page 65: Latency Ladder 2025
Know your physics: Every operation has a cost
THE FUNDAMENTAL LATENCY HIERARCHY
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
2025 UPDATE: Modern Hardware
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
LATENCY BUDGET CALCULATOR
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
COMPOUND LATENCY EFFECTS
Serial Operations (add):
A → B → C = Latency(A) + Latency(B) + Latency(C)

Parallel Operations (max):
A ⟋ B ⟋ C = MAX(Latency(A), Latency(B), Latency(C))

Percentile Multiplication:
If each service is 99% under 100ms
Two serial calls: 98% under 200ms
Three serial calls: 97% under 300ms
Ten serial calls: 90% under 1000ms!
REAL-WORLD LATENCY TARGETS
Industry            Operation                Target      Why
--------            ---------                ------      ---
HFT Trading         Order execution          <1 μs       Competitive advantage
Gaming              Input to screen          16 ms       60 FPS requirement
Video call          End-to-end audio         150 ms      Natural conversation
Web search          Query to results         200 ms      User satisfaction
E-commerce          Add to cart              300 ms      Conversion rate
Streaming           Start playback           2 s         User retention
Email               Send confirmation        5 s         User expectation
LATENCY REDUCTION STRATEGIES
Strategy                    Typical Improvement    Cost
--------                    -------------------    ----
Add regional cache          50-90%                 $$
Use CDN                     40-80%                 $$
Optimize queries            20-50%                 $
Add indexes                 30-70%                 $
Batch operations            40-60%                 $
Parallel processing         30-50%                 $$
Better algorithms           10-90%                 $
Hardware upgrade            20-40%                 $$$
Protocol optimization       10-30%                 $$
Connection pooling          20-40%                 $
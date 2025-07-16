Page 6: Failure-Domain Tree + Timeouts
Visual Failure Hierarchy:
                        System
                     ╱         ╲
                Region A      Region B
               ╱    |    ╲        |
            AZ1    AZ2    AZ3    AZ1
           ╱ |      |      |      |
        Rack1 R2    R1     R1     R1
        ╱ ╲   |     |      |      |
      N1  N2  N1    N1     N1     N1
      |   |   |     |      |      |
     Pod Pod Pod   Pod    Pod    Pod
Timeout Strategy Matrix:
Layer           Timeout    Rationale
-----           -------    ---------
User → LB       30s        Human patience limit
LB → Service    10s        Allow for retries
Service → Svc   3s         Intra-DC speed
Service → DB    1s         Query should be fast
Service → Cache 100ms      Cache must be faster
Circuit Open    5s         Recovery probe interval
Timeout Coordination Problem:
WRONG (Timeout Inversion):
Client timeout:   5s
Service timeout:  10s  
Result: Client gives up, service keeps trying

RIGHT (Nested Timeouts):
Client timeout:   10s
Service timeout:  3s
Retry budget:     3 × 3s = 9s < 10s ✓
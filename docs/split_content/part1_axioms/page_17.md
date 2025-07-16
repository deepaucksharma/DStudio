Page 17: Axioms Spider-Chart
Visual Radar Chart Showing Axiom Dominance by Use Case:
                        Latency
                          10
                      8   .   
                  6     .   .
              4       .       .
          2         .           .
Cost    0 ─────────*─────────────. Capacity
        .           .             .
        .           .           .
        .           .         .     Failure
        .           .       .
        .           .     .
                    . . .
                Coordination

Legend: 
─── E-commerce Site (latency + capacity critical)
─·─ Analytics Pipeline (cost + coordination matter)
··· Trading System (latency dominates everything)
─── Social Network (failure + capacity focus)
How to Read Your System's Shape:

Spike on one axis: Optimize for that constraint
Balanced polygon: General-purpose architecture
Flat shape: Over-engineered or under-specified
Irregular: Different subsystems have different needs

Example Profiles:
Real-time Bidding System:
Latency:       ████████████ (10/10) - 100ms budget
Capacity:      ████████ (8/10) - 1M requests/sec
Failure:       ████ (4/10) - Some loss acceptable
Coordination:  ██ (2/10) - Read mostly
Cost:          ████████ (8/10) - Every ms costs money
Batch Analytics Platform:
Latency:       ██ (2/10) - Hours acceptable
Capacity:      ██████████ (10/10) - Petabytes
Failure:       ████ (4/10) - Can retry
Coordination:  ████████ (8/10) - Complex DAGs
Cost:          ██████████ (10/10) - Main constraint
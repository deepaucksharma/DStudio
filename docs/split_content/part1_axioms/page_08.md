Page 8: Space-Time Diagram & Vector Clock Intro
Visual Representation of Distributed Time:
Process A  ─────●─────────●───────────●────→ time
                │ e1      │ e3        │ e5
                ↓         ↓           ↓
Process B  ───────────●───────●───────────→ time
                      │ e2    │ e4
                      
Happens-before: e1 → e2 → e3 → e4 → e5
Concurrent: (e1 || e4), (e3 || e4)
Vector Clocks Explained:
Each process maintains vector: [A_count, B_count, C_count]

Process A: [1,0,0] → sends message → [2,0,0]
Process B: [0,0,0] → receives → [2,1,0] → sends → [2,2,0]
Process C: [0,0,1] → receives → [2,2,1]

Comparing vectors:
[2,1,0] happens-before [2,2,1] ✓
[2,1,0] concurrent-with [1,0,2] ✓
Practical Use: Detect causality violations in distributed systems
Page 21: Why Pillars?
Learning Objective: Understand how axioms combine to create fundamental architectural patterns.
The Emergence Principle:
Axioms = Constraints (what you cannot change)
Pillars = Patterns (how you work within constraints)

Just as chemistry emerges from physics, and biology from chemistry,
distributed system patterns emerge from fundamental constraints.
The Three Core + Two Extension Model:
                    AXIOMS (Constraints)
                           ↓
    ┌────────────────────────────────────────────┐
    │            CORE PILLARS                     │
    │                                             │
    │  Work         State          Truth         │
    │  Distribution Distribution   Distribution  │
    │     ↑            ↑              ↑          │
    │  Capacity    Capacity      Coordination   │
    │  Latency     Latency       Concurrency    │
    │              Failure       Partial Fail    │
    └────────────────────────────────────────────┘
                           ↓
    ┌────────────────────────────────────────────┐
    │         EXTENSION PILLARS                   │
    │                                             │
    │     Control           Intelligence         │
    │     Distribution      Distribution         │
    │         ↑                   ↑              │
    │    Human Interface    All Axioms +        │
    │    Observability      Feedback Loops       │
    └────────────────────────────────────────────┘
Why These Five?
Coverage Analysis:
System Aspect               Covered By Pillar
-------------               -----------------
Request handling           → Work Distribution
Data persistence          → State Distribution  
Consistency               → Truth Distribution
Operations                → Control Distribution
Adaptation                → Intelligence Distribution

Completeness check: ✓ All aspects covered
Minimality check: ✓ No redundant pillars
Orthogonality check: ✓ Pillars independent
Historical Evolution:
1960s: Mainframes (no distribution needed)
1970s: Client-server (Work distribution emerges)
1980s: Databases (State distribution emerges)
1990s: Internet (Truth distribution critical)
2000s: Web-scale (Control distribution needed)
2010s: Cloud (All pillars mature)
2020s: AI/Edge (Intelligence distribution emerges)
The Pillar Interaction Model:
Work × State = Stateless vs Stateful services
Work × Truth = Consistency models for compute
State × Truth = CAP theorem territory
Control × All = Orchestration patterns
Intelligence × All = Self-healing systems
Mental Model: The Distributed Systems House
     Intelligence (Roof - Protects/Adapts)
           /                    \
    Control                    Control
    (Walls)                    (Walls)
      |                          |
Work--+--------State--------+---Work
      |                     |
      |        Truth        |
      |      (Foundation)   |
      +---------------------+
# CAST vs SPACE Models

**Learning Objective**: Compare different distributed systems models to choose the right mental framework.

## CAST Model (Control, Availability, State, Time)

```
Control
├─ Centralized: Master/slave, orchestration
├─ Distributed: Peer-to-peer, choreography
└─ Hybrid: Regional masters, hierarchical

Availability  
├─ Best effort: May fail under load
├─ Highly available: 99.9%+ uptime
└─ Fault tolerant: Continues despite failures

State
├─ Stateless: No memory between requests
├─ Stateful: Maintains context
└─ Externalized: State in database/cache

Time
├─ Synchronous: Wait for response
├─ Asynchronous: Fire and forget
└─ Eventual: Converges over time
```

## SPACE Model (State, Processing, Access, Concurrency, Exchange)

```
State
├─ Shared: Multiple nodes access same data
├─ Partitioned: Data divided among nodes
└─ Replicated: Copies for fault tolerance

Processing
├─ Stream: Continuous data flow
├─ Batch: Periodic bulk processing
└─ Interactive: Request/response

Access
├─ Random: Any record, any time
├─ Sequential: Ordered traversal
└─ Temporal: Time-based queries

Concurrency
├─ Pessimistic: Lock and proceed
├─ Optimistic: Try and retry
└─ Lock-free: Atomic operations

Exchange
├─ Message passing: Explicit communication
├─ Shared memory: Implicit communication
└─ Tuple spaces: Generative communication
```

## Model Comparison Matrix

```
Aspect          CAST Focus           SPACE Focus
------          ----------           -----------
Abstraction     Architectural        Implementation
Scope           System-wide          Component-level
Primary Use     Design decisions     Pattern selection
Granularity     Coarse              Fine
Best For        Architects          Developers
```

## When to Use Which Model

**Use CAST when:**
- Designing new systems
- Explaining to stakeholders
- Making trade-off decisions
- System-level architecture

**Use SPACE when:**
- Implementing components
- Choosing data structures
- Optimizing performance
- Detailed design work

## Real-World Example: Video Streaming Platform

**CAST Analysis**:
```
Control: Centralized CDN management
Availability: 99.99% (52 min downtime/year)
State: User sessions, watch history
Time: Async upload, sync playback
```

**SPACE Analysis**:
```
State: Replicated video files
Processing: Stream transcoding
Access: Random seek in videos
Concurrency: Optimistic for views
Exchange: HTTP for delivery
```

## 🔧 Try This: Model Your System

```python
class SystemModel:
    def __init__(self, name):
        self.name = name
        self.cast = {}
        self.space = {}
    
    def analyze_cast(self):
        """CAST model analysis"""
        print(f"\n=== CAST Analysis for {self.name} ===")
        
        # Control
        control_score = 0
        if self.cast.get('master_node'):
            control_score = 1  # Centralized
        elif self.cast.get('consensus'):
            control_score = 5  # Distributed
        else:
            control_score = 3  # Hybrid
            
        # Availability
        nines = self.cast.get('sla', 99.0)
        avail_score = min(5, (nines - 95) / 0.9)
        
        # State
        state_score = 1 if self.cast.get('stateless') else 4
        
        # Time
        time_score = 1 if self.cast.get('sync') else 4
        
        print(f"Control: {'█' * control_score}{'░' * (5-control_score)} "
              f"({'Centralized' if control_score < 3 else 'Distributed'})")
        print(f"Availability: {'█' * int(avail_score)}{'░' * (5-int(avail_score))} "
              f"({nines}%)")
        print(f"State: {'█' * state_score}{'░' * (5-state_score)} "
              f"({'Stateless' if state_score < 3 else 'Stateful'})")
        print(f"Time: {'█' * time_score}{'░' * (5-time_score)} "
              f"({'Synchronous' if time_score < 3 else 'Asynchronous'})")
    
    def analyze_space(self):
        """SPACE model analysis"""
        print(f"\n=== SPACE Analysis for {self.name} ===")
        
        patterns = {
            'State': self.space.get('state', 'Unknown'),
            'Processing': self.space.get('processing', 'Unknown'),
            'Access': self.space.get('access', 'Unknown'),
            'Concurrency': self.space.get('concurrency', 'Unknown'),
            'Exchange': self.space.get('exchange', 'Unknown')
        }
        
        for aspect, pattern in patterns.items():
            print(f"{aspect:12} : {pattern}")

# Example usage
netflix = SystemModel("Netflix")
netflix.cast = {
    'master_node': False,
    'consensus': True,
    'sla': 99.99,
    'stateless': False,
    'sync': False
}
netflix.space = {
    'state': 'Replicated (videos) + Partitioned (users)',
    'processing': 'Stream (playback) + Batch (recommendations)',
    'access': 'Sequential (video) + Random (catalog)',
    'concurrency': 'Optimistic (views) + Pessimistic (billing)',
    'exchange': 'HTTP streaming + Message queues'
}

netflix.analyze_cast()
netflix.analyze_space()
```

---

**Next**: [When Models Collide →](models-collide.md)
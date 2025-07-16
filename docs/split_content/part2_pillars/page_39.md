Page 39: Failure-Vignette Recap Boxes
Quick Reference: How Each Pillar Fails
┌─────────────────────────────────────┐
│ WORK DISTRIBUTION FAILURE           │
│ "The Thundering Herd"               │
│ All workers start simultaneously,   │
│ overwhelming shared resources.      │
│ Fix: Jittered starts, gradual ramp │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ STATE DISTRIBUTION FAILURE          │
│ "The Hot Shard"                     │
│ Celebrity user overloads one shard  │
│ while others sit idle.              │
│ Fix: Virtual shards, rebalancing    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ TRUTH DISTRIBUTION FAILURE          │
│ "The Split Brain"                   │
│ Network partition causes two nodes  │
│ to think they're primary.           │
│ Fix: Proper quorum, fencing         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ CONTROL DISTRIBUTION FAILURE        │
│ "The Cascading Restart"             │
│ Config push causes all services     │
│ to restart, triggering failures.    │
│ Fix: Canary deployments, waves      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ INTELLIGENCE DISTRIBUTION FAILURE   │
│ "The Feedback Loop of Doom"         │
│ ML model learns from its mistakes,  │
│ amplifying bad decisions.           │
│ Fix: Human review, drift detection  │
└─────────────────────────────────────┘
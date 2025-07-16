Page 1: AXIOM 1 – Latency (Speed of Light)
Learning Objective: Internalize that latency is physics, not engineering.
Core Content Structure:
Definition Box:
Latency := Time for information to travel from point A to point B
Minimum Bound: distance / speed_of_light
In fiber: ~200,000 km/s (2/3 of c due to refractive index)
The Physics Foundation:

Light in vacuum: 299,792 km/s
In fiber optic cable: ~200,000 km/s
Copper wire: ~200,000 km/s (electromagnetic wave)
Fundamental Insight: No engineering can overcome physics

🎬 Failure Vignette: The Tokyo Checkout Disaster
Scene: Black Friday 2019, US e-commerce giant
Setup: "Smart" optimization routes all Asian traffic to Tokyo DC
Problem: SF inventory DB is source of truth
Impact: 250ms RTT × 3 DB calls = 750ms per checkout
Result: 67% cart abandonment, $12M lost revenue
Fix: Regional inventory caches with eventual consistency
Lesson: Speed of light is a budget, not a suggestion
The Latency Ladder (mini version):
Same rack:          0.5 ms
Same DC:            1-2 ms
Same region:        10 ms
Cross-continent:    100 ms
Opposite globe:     200+ ms
Geosync satellite:  500+ ms
Mars (best case):   4 min
🎯 Decision Box: Cache vs Replica
IF (latency_budget < physics_minimum) THEN
  IF (data_changes_rarely) THEN
    USE cache WITH ttl = change_frequency
  ELSE IF (eventual_consistency_ok) THEN
    USE read_replica WITH async_replication
  ELSE
    REDESIGN to avoid remote calls
  END
ELSE
  USE remote_calls WITH latency_budget - physics_minimum margin
END
Interactive Element:

Globe visualization with draggable points
Shows theoretical minimum latency between any two points
Overlays actual internet paths vs great circle routes

🔧 Try This (2 minutes):
bash# Measure your physics tax
ping -c 10 google.com | grep "min/avg/max"
traceroute google.com | tail -5
# Calculate: actual_latency / theoretical_minimum
Counter-Intuitive Truth 💡:
"Adding more servers can INCREASE latency if it adds more hops. The fastest distributed system is often the one with fewer, better-placed nodes."
Cross-Links:

→ Caching Hierarchies (p.57): Implementation patterns
→ Geo-Replication (p.61): Multi-region strategies
→ Latency Budget Worksheet (p.2): Practical application

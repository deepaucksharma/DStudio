# Pattern Interconnection Matrix v2

## The Full Pattern Relationship Heatmap

```
                    Patterns (Impact on Axioms)
         Queue  CQRS  Event  Saga  Mesh  Lambda  Cache  Shard
Latency    +     ++    +     --    -      +      +++    +
Capacity   +++   ++    ++    +     +      +++    ++     +++
Failure    ++    +     ++    +++   ++     -      +      --
Concur     +     +++   ++    ++    +      -      --     ---
Coord      -     +     -     ---   --     +      +      --
Observ     +     ++    +++   ++    +++    --     -      -
Human      +     -     -     --    ++     +      +      --
Cost       +     -     +     --    --     +/-    ++     -

Legend:
+++ Strongly improves axiom constraint
++  Moderately improves  
+   Slightly improves
+/- Context dependent
-   Slightly worsens
--  Moderately worsens
--- Strongly worsens
```

## Reading the Matrix

### Example 1: Caching
- Latency: +++ (massive improvement)
- Concurrency: -- (cache invalidation is hard)
- Human: + (conceptually simple)
- **Verdict**: Use when latency dominates

### Example 2: Saga Pattern
- Latency: -- (multiple steps)
- Failure: +++ (handles partial failure well)
- Coordination: --- (complex orchestration)
- **Verdict**: Use when consistency matters more than speed

## Pattern Combinations that Work

```
1. Queue + Lambda
   - Queue absorbs spikes
   - Lambda scales with queue depth
   - Cost efficient for variable load

2. CQRS + Event Sourcing
   - Commands create events
   - Queries from projected views
   - Full audit trail bonus

3. Cache + Shard
   - Cache hides sharding complexity
   - Sharding enables cache scaling
   - Together handle any scale

4. Service Mesh + Circuit Breaker
   - Mesh provides uniform policy
   - Circuit breaker prevents cascades
   - Observability built-in
```

## Pattern Combinations to Avoid

```
1. Saga + Synchronous Calls
   - Latency multiplies
   - Failure complexity explodes
   - Timeouts become nightmare

2. Strong Consistency + Geo-Distribution
   - Physics says no
   - Coordination costs explode
   - Users suffer latency

3. Stateful Services + Serverless
   - Cold starts lose state
   - Scaling breaks affinity
   - Costs unpredictable
```

---

**Next**: [Trade-off Calculus →](tradeoff-calculus.md)
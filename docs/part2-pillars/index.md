# Part II: Foundational Pillars

## Why Pillars?

The axioms teach us *what* constrains distributed systems. The pillars teach us *how* to work within those constraints.

Think of it this way: if axioms are Newton's laws of motion, then pillars are aerospace engineering. Physics constrains what's possible; engineering shows us how to achieve it.

### From Constraints to Capabilities

The eight axioms reveal fundamental limits:
- Information cannot travel faster than light (Latency)
- Systems have finite resources (Capacity) 
- Components fail independently (Partial Failure)
- Events happen concurrently (Concurrency)
- Coordination has costs (Coordination)
- Perfect information is impossible (Observability)
- Humans are the system's purpose (Human Interface)
- Everything has economic costs (Economics)

But within these constraints, we can build remarkable systems. The five pillars show us how:

<div class="pillar-overview">

**Work**: How to decompose and distribute computation  
**State**: How to manage and replicate data  
**Truth**: How to establish consensus and consistency  
**Control**: How to coordinate and orchestrate systems  
**Intelligence**: How to adapt and evolve systems

</div>

### The Emergence Property

Here's something beautiful: when you master these five pillars, something emerges that's greater than their sum. You develop *systems intuition*—the ability to see how changes ripple through complex architectures, to predict where bottlenecks will form, to design for failures you haven't seen yet.

This intuition is what separates senior engineers from junior ones. It's what lets you walk into a room full of smart people arguing about architecture and quietly suggest the solution that makes everyone say "oh, obviously."

### How Pillars Build on Axioms

Each pillar respects all eight axioms, but typically wrestles most directly with a subset:

- **Work** primarily grapples with Latency and Capacity
- **State** wrestles with Consistency and Partial Failure  
- **Truth** deals with Coordination and Observability
- **Control** balances Human Interface and Economics
- **Intelligence** emerges from all axioms working together

### The Five Pillars Journey

We'll explore each pillar through three lenses:

1. **Foundations**: The mathematical and physical principles
2. **Patterns**: Proven architectural approaches
3. **Practice**: Real implementations and trade-offs

By the end, you'll understand not just *what* each pillar does, but *why* it works the way it does, and *how* to apply these principles to your own systems.

---

*"Give me a lever long enough and I can move the world. Give me the right abstractions and I can build any system."*

## The Five Pillars

<div class="grid cards" markdown>

- :material-cog: **[Work](work/index.md)**

    ---
    
    Decomposing computation across space and time

- :material-database: **[State](state/index.md)**

    ---
    
    Managing data consistency and replication

- :material-check-decagram: **[Truth](truth/index.md)**

    ---
    
    Establishing consensus and ordering

- :material-tune: **[Control](control/index.md)**

    ---
    
    Coordinating system behavior

- :material-brain: **[Intelligence](intelligence/index.md)**

    ---
    
    Adaptive and self-organizing systems

</div>
# Preface: Why Another Systems Book?

## The Manifesto

Existing distributed systems literature falls into two camps: academic proofs divorced from practice, or engineering cookbooks lacking theoretical foundation. Books like *Designing Data-Intensive Applications* give you the 'what' and 'how'; SRE books provide the 'when things break.' This book uniquely provides the **'why from first principles.'**

We don't start with Kafka or Kubernetes. We start with the speed of light and the laws of thermodynamics. Every pattern emerges from inescapable constraints. When you understand why coordination has fundamental costs, you'll never again wonder whether to use 2PC or saga patterns—the physics will tell you.

### Three Breakthroughs

This approach is finally practical due to three breakthroughs:

1. **Axiom Unification**: Eight fundamental constraints explain all distributed behavior
2. **Pattern Derivation**: Every architecture pattern emerges from axiom combinations  
3. **Decision Calculus**: Quantitative trade-off framework replacing intuition with math

This isn't another 500-page tome to read once. It's a 100-page compass you'll reference throughout your career. Each page earns its place through information density and immediate applicability.

## Scope Boundaries

### What's Included ✓
- Distributed systems from 2-node to planet-scale
- Both synchronous and asynchronous architectures
- Patterns that transcend specific technologies
- Quantitative decision frameworks
- Real failure stories with root cause analysis

### What's Excluded ✗
- Single-node optimization (see Hennessy & Patterson)
- Specific vendor products (patterns over products)
- Full protocol specifications (we extract principles)
- Implementation code (we focus on design)
- Technology fashion (we teach timeless principles)

## The First-Principles Promise

Every concept in this book follows this progression:

```
Fundamental Constraint → Emergent Behavior → System Impact → Design Pattern → Trade-off Decision
```

No pattern is presented as received wisdom. Each is derived from constraints you can verify yourself.

## How This Book Is Different

### Traditional Approach
- Chapter 1: Here's MapReduce
- Chapter 2: Here's Paxos
- Chapter 3: Here's Consistent Hashing
- Reader: "But when do I use each?"

### Our Approach
- Axiom: Light has finite speed
- Therefore: Distant coordination is expensive
- Therefore: Minimize coordination requirements
- Options: Eventual consistency, CRDT, event sourcing
- Decision: Use physics to calculate trade-offs

## Reading Commitment

**Our promise**: Each page contains ONE core insight you'll use within 30 days.

**Your commitment**: Question everything. If a principle doesn't derive from physics or math, challenge it.

## Acknowledgments

This book exists because distributed systems engineers have been remarkably generous in sharing their failures. Every disaster story in these pages represents someone's worst day at work, shared so others might avoid the same fate.

To those who contributed failure stories: your scars became our wisdom.

To those who will build tomorrow's systems: may you fail in new and interesting ways, not the ways documented here.

---

*"In distributed systems, the impossible becomes merely difficult, and the difficult becomes a career."*

**Ready to begin?** → [Start with the Reader Roadmap](roadmap.md)
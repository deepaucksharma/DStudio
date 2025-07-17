# Consistency Trade-off Visualizer

!!! info "Prerequisites"
    - Understanding of [CAP theorem](../part1-axioms/axiom-4-concurrency/index.md)
    - Basic knowledge of consistency models
    - Familiarity with distributed systems concepts

!!! tip "Quick Navigation"
    [← Tools Overview](index.md) | 
    [Latency Calculator](latency-calculator.md) | 
    [Capacity Planner](capacity-planner.md)

## Explore Consistency Models Interactively

<div class="key-takeaway">
  <div class="key-takeaway-header">
    <span class="key-takeaway-icon">🔄</span>
    <h3 class="key-takeaway-title">Understanding Consistency Trade-offs</h3>
  </div>
  <div class="key-takeaway-content">
    <p>Visualize how different consistency models behave under various scenarios:</p>
    <ul>
      <li><strong>Strong Consistency</strong>: All nodes see the same data at the same time</li>
      <li><strong>Eventual Consistency</strong>: Nodes converge to the same state eventually</li>
      <li><strong>Causal Consistency</strong>: Preserves cause-and-effect relationships</li>
      <li><strong>Weak Consistency</strong>: No ordering guarantees between operations</li>
    </ul>
  </div>
</div>

## Interactive Visualizer

<div id="consistency-visualizer"></div>

## Understanding the Visualization

### Node States

<div class="concept-cards">
  <div class="concept-card">
    <div class="concept-card-icon">🟢</div>
    <h4 class="concept-card-title">Green Nodes</h4>
    <p class="concept-card-description">Stable state - data is consistent</p>
  </div>
  <div class="concept-card">
    <div class="concept-card-icon">🟡</div>
    <h4 class="concept-card-title">Orange Nodes</h4>
    <p class="concept-card-description">Pending update - waiting for consensus or propagation</p>
  </div>
  <div class="concept-card">
    <div class="concept-card-icon">🔴</div>
    <h4 class="concept-card-title">Red Nodes</h4>
    <p class="concept-card-description">Conflict or unavailable - cannot complete operation</p>
  </div>
</div>

### Scenarios Explained

<div class="progressive-disclosure">
  <div class="disclosure-header">
    <div class="disclosure-title">
      <span class="disclosure-icon">📝</span>
      <span class="disclosure-text">Write Operation</span>
    </div>
    <span class="disclosure-arrow">▼</span>
  </div>
  <div class="disclosure-content">
    <div class="disclosure-inner">
      <p>A single node initiates a write operation. Watch how the update propagates based on the consistency model:</p>
      <ul>
        <li><strong>Strong</strong>: Write blocks until all nodes acknowledge</li>
        <li><strong>Eventual</strong>: Write completes immediately, propagates asynchronously</li>
        <li><strong>Causal</strong>: Write respects dependencies between operations</li>
        <li><strong>Weak</strong>: Write completes with no coordination</li>
      </ul>
    </div>
  </div>
</div>

<div class="progressive-disclosure">
  <div class="disclosure-header">
    <div class="disclosure-title">
      <span class="disclosure-icon">⚡</span>
      <span class="disclosure-text">Concurrent Writes</span>
    </div>
    <span class="disclosure-arrow">▼</span>
  </div>
  <div class="disclosure-content">
    <div class="disclosure-inner">
      <p>Multiple nodes attempt to write simultaneously. This scenario demonstrates conflict resolution:</p>
      <ul>
        <li><strong>Strong</strong>: Serializes writes, one must wait</li>
        <li><strong>Eventual</strong>: Both succeed, last-write-wins or merge</li>
        <li><strong>Causal</strong>: Concurrent if independent, ordered if related</li>
        <li><strong>Weak</strong>: No conflict resolution, may diverge</li>
      </ul>
    </div>
  </div>
</div>

<div class="progressive-disclosure">
  <div class="disclosure-header">
    <div class="disclosure-title">
      <span class="disclosure-icon">🌐</span>
      <span class="disclosure-text">Network Partition</span>
    </div>
    <span class="disclosure-arrow">▼</span>
  </div>
  <div class="disclosure-content">
    <div class="disclosure-inner">
      <p>Network split isolates nodes. This demonstrates the CAP theorem trade-offs:</p>
      <ul>
        <li><strong>Strong</strong>: Chooses consistency, becomes unavailable</li>
        <li><strong>Eventual</strong>: Remains available, diverges temporarily</li>
        <li><strong>Causal</strong>: Partial availability based on dependencies</li>
        <li><strong>Weak</strong>: Full availability, no consistency guarantees</li>
      </ul>
    </div>
  </div>
</div>

## CAP Theorem Trade-offs

The visualizer demonstrates the fundamental trade-offs in distributed systems:

<div class="decision-box">

**🎯 CAP Theorem Decision Tree**

```
Network Partition Occurs
│
├─ Choose Consistency (CP)
│   ├─ System becomes unavailable
│   ├─ No writes accepted
│   └─ Data remains consistent
│
└─ Choose Availability (AP)
    ├─ System remains available
    ├─ Writes accepted on both sides
    └─ Data may diverge
```

</div>

## Real-World Applications

### When to Use Each Model

<div class="truth-box">

**Strong Consistency**
- Financial transactions
- Inventory management
- User authentication
- Configuration management

**Eventual Consistency**
- Social media feeds
- Analytics data
- Content delivery
- Shopping carts

**Causal Consistency**
- Chat applications
- Collaborative editing
- Social networks
- Event sourcing

**Weak Consistency**
- Caching layers
- Session storage
- Metrics collection
- Log aggregation

</div>

## Key Insights

1. **No Silver Bullet**: Each consistency model has trade-offs. Choose based on your specific requirements.

2. **Physics Matters**: Network delays and partitions are inevitable. Design for them.

3. **User Experience**: Sometimes "good enough" consistency provides better UX than perfect consistency.

4. **Cost Implications**: Stronger consistency generally requires more coordination, increasing latency and resource usage.

## Related Concepts

- **[Axiom 1: Latency](../part1-axioms/axiom-1-latency/index.md)**: Consistency coordination adds latency
- **[Axiom 3: Partial Failure](../part1-axioms/axiom-3-failure/index.md)**: Network partitions are a form of failure
- **[Pillar 3: Distribution of Truth](../part2-pillars/pillar-3-truth/index.md)**: Managing consistency at scale

## Try It Yourself

1. **Compare Models**: Run the same scenario with different consistency models
2. **Adjust Speed**: Use the speed slider to see operations in slow motion
3. **Chain Scenarios**: Run multiple scenarios to see cumulative effects
4. **Observe Metrics**: Watch how latency, availability, and consistency metrics change

<div class="key-takeaway success">
  <div class="key-takeaway-header">
    <span class="key-takeaway-icon">💡</span>
    <h3 class="key-takeaway-title">Remember</h3>
  </div>
  <div class="key-takeaway-content">
    <p>Consistency is not binary - it's a spectrum. Choose the right level for your use case, not the strongest level available.</p>
  </div>
</div>

## Navigation

!!! tip "Continue Learning"
    
    **More Tools**: [Latency Calculator](latency-calculator.md) | [Capacity Planner](capacity-planner.md)
    
    **Deep Dive**: [Consistency Patterns](../part2-pillars/pillar-3-truth/index.md)
    
    **Practice**: [Consistency Exercises](../part1-axioms/axiom-4-concurrency/exercises.md)
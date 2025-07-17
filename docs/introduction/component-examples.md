# Component Examples

This page demonstrates all the enhanced UI components available for content creation.

## Key Takeaway Components

### Default Key Takeaway

<div class="key-takeaway">
  <div class="key-takeaway-header">
    <span class="key-takeaway-icon">💡</span>
    <h3 class="key-takeaway-title">Default Information Box</h3>
  </div>
  <div class="key-takeaway-content">
    This is a standard key takeaway box for highlighting important information. Use this for general insights and important concepts that readers should remember.
  </div>
</div>

### Success Key Takeaway

<div class="key-takeaway success">
  <div class="key-takeaway-header">
    <span class="key-takeaway-icon">✅</span>
    <h3 class="key-takeaway-title">Best Practice</h3>
  </div>
  <div class="key-takeaway-content">
    Use the success variant to highlight recommended approaches and best practices. This green styling indicates positive patterns to follow.
  </div>
</div>

### Warning Key Takeaway

<div class="key-takeaway warning">
  <div class="key-takeaway-header">
    <span class="key-takeaway-icon">⚠️</span>
    <h3 class="key-takeaway-title">Important Consideration</h3>
  </div>
  <div class="key-takeaway-content">
    The warning variant draws attention to important caveats or things to be careful about. Use this when readers need to pay special attention.
  </div>
</div>

### Danger Key Takeaway

<div class="key-takeaway danger">
  <div class="key-takeaway-header">
    <span class="key-takeaway-icon">🚨</span>
    <h3 class="key-takeaway-title">Critical Alert</h3>
  </div>
  <div class="key-takeaway-content">
    The danger variant is for critical warnings about common mistakes or anti-patterns. Use sparingly for maximum impact.
  </div>
</div>

## Concept Cards

<div class="concept-cards">
  <div class="concept-card axiom">
    <div class="concept-card-icon">⚡</div>
    <h4 class="concept-card-title">Latency Axiom</h4>
    <p class="concept-card-description">The speed of light creates fundamental constraints on distributed systems.</p>
    <div class="concept-card-formula">latency ≥ distance / c</div>
    <div class="concept-card-example">NYC to London: minimum 28ms</div>
    <a href="#" class="concept-card-link">Learn more →</a>
  </div>
  
  <div class="concept-card pillar">
    <div class="concept-card-icon">📊</div>
    <h4 class="concept-card-title">State Distribution</h4>
    <p class="concept-card-description">How data is spread across multiple nodes in a system.</p>
    <div class="concept-card-formula">CAP Theorem applies</div>
    <div class="concept-card-example">Sharding, Replication, Caching</div>
    <a href="#" class="concept-card-link">Explore patterns →</a>
  </div>
  
  <div class="concept-card pattern">
    <div class="concept-card-icon">🔄</div>
    <h4 class="concept-card-title">Circuit Breaker</h4>
    <p class="concept-card-description">Prevent cascading failures by failing fast when errors exceed threshold.</p>
    <div class="concept-card-formula">if (errors > threshold) → open circuit</div>
    <a href="#" class="concept-card-link">Implementation guide →</a>
  </div>
</div>

### Featured Concept Card

<div class="concept-cards">
  <div class="concept-card featured">
    <div class="concept-card-icon">🎯</div>
    <h4 class="concept-card-title">The CAP Theorem</h4>
    <p class="concept-card-description">You can only guarantee two of: Consistency, Availability, and Partition tolerance. This fundamental theorem shapes all distributed system designs.</p>
    <div class="concept-card-formula">C + A + P → Pick 2</div>
    <div class="concept-card-example">
      • CP: HBase, MongoDB (strong consistency mode)
      • AP: Cassandra, DynamoDB
      • CA: Traditional RDBMS (single node)
    </div>
    <a href="#" class="concept-card-link">Deep dive into CAP →</a>
  </div>
</div>

## Progressive Disclosure

<div class="progressive-disclosure">
  <div class="disclosure-header">
    <div class="disclosure-title">
      <span class="disclosure-icon">📚</span>
      <span class="disclosure-text">What is eventual consistency?</span>
    </div>
    <span class="disclosure-arrow">▼</span>
  </div>
  <div class="disclosure-content">
    <div class="disclosure-inner">
      <p>Eventual consistency is a consistency model used in distributed computing to achieve high availability. It informally guarantees that, if no new updates are made to a given data item, eventually all accesses to that item will return the last updated value.</p>
      
      <h4>Key Characteristics:</h4>
      <ul>
        <li>Updates propagate asynchronously</li>
        <li>Different nodes may see different values temporarily</li>
        <li>System converges to consistent state over time</li>
        <li>Trade consistency for availability and partition tolerance</li>
      </ul>
      
      <div class="progressive-disclosure info">
        <div class="disclosure-header">
          <div class="disclosure-title">
            <span class="disclosure-icon">🔍</span>
            <span class="disclosure-text">Real-world example</span>
          </div>
          <span class="disclosure-arrow">▼</span>
        </div>
        <div class="disclosure-content">
          <div class="disclosure-inner">
            <p><strong>DNS (Domain Name System)</strong> is a perfect example of eventual consistency:</p>
            <ul>
              <li>DNS changes propagate gradually across servers</li>
              <li>Different users may resolve to different IPs temporarily</li>
              <li>Eventually, all DNS servers converge to the new value</li>
              <li>TTL (Time To Live) provides an upper bound on inconsistency</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="progressive-disclosure warning">
  <div class="disclosure-header">
    <div class="disclosure-title">
      <span class="disclosure-icon">⚠️</span>
      <span class="disclosure-text">Common pitfalls with microservices</span>
    </div>
    <span class="disclosure-arrow">▼</span>
  </div>
  <div class="disclosure-content">
    <div class="disclosure-inner">
      <ol>
        <li><strong>Distributed Monolith</strong>: Services too tightly coupled</li>
        <li><strong>Chatty Services</strong>: Too many synchronous calls</li>
        <li><strong>Shared Database</strong>: Violates service boundaries</li>
        <li><strong>Inadequate Monitoring</strong>: Can't debug distributed failures</li>
        <li><strong>Missing Circuit Breakers</strong>: Cascading failures</li>
      </ol>
    </div>
  </div>
</div>

## Content Breaks

<div class="content-break">
  <span class="content-break-icon">🌟</span>
</div>

Use content breaks to visually separate major sections and give readers a mental pause.

<div class="content-break">
  <span class="content-break-icon">💭</span>
</div>

## Section Dividers

<div class="section-divider">
  <h2 class="section-divider-title">Advanced Topics</h2>
  <p class="section-divider-subtitle">Deep dive into complex concepts</p>
</div>

Section dividers create clear visual hierarchy and help readers understand when they're transitioning to a new major topic.

## Combining Components

You can combine these components to create rich, engaging content:

<div class="section-divider">
  <h2 class="section-divider-title">Distributed Consensus</h2>
  <p class="section-divider-subtitle">How systems agree in an unreliable world</p>
</div>

<div class="key-takeaway">
  <div class="key-takeaway-header">
    <span class="key-takeaway-icon">🤝</span>
    <h3 class="key-takeaway-title">The Consensus Challenge</h3>
  </div>
  <div class="key-takeaway-content">
    Achieving agreement among distributed nodes is one of the hardest problems in computer science. It requires multiple round trips, making it inherently slow and complex.
  </div>
</div>

<div class="concept-cards">
  <div class="concept-card">
    <div class="concept-card-icon">🗳️</div>
    <h4 class="concept-card-title">Paxos</h4>
    <p class="concept-card-description">The original consensus algorithm, mathematically proven but complex to implement.</p>
    <a href="#" class="concept-card-link">Learn Paxos →</a>
  </div>
  
  <div class="concept-card">
    <div class="concept-card-icon">🚤</div>
    <h4 class="concept-card-title">Raft</h4>
    <p class="concept-card-description">Designed for understandability, widely used in modern systems.</p>
    <a href="#" class="concept-card-link">Learn Raft →</a>
  </div>
</div>

<div class="progressive-disclosure">
  <div class="disclosure-header">
    <div class="disclosure-title">
      <span class="disclosure-icon">🔧</span>
      <span class="disclosure-text">Implementation considerations</span>
    </div>
    <span class="disclosure-arrow">▼</span>
  </div>
  <div class="disclosure-content">
    <div class="disclosure-inner">
      <p>When implementing consensus in production:</p>
      <ul>
        <li>Network partitions will happen - design for them</li>
        <li>Leader election is critical - handle split-brain scenarios</li>
        <li>Log compaction prevents unbounded growth</li>
        <li>Client request deduplication prevents duplicate operations</li>
      </ul>
    </div>
  </div>
</div>

## Usage Guidelines

1. **Key Takeaways**: Use sparingly, 1-2 per page maximum for impact
2. **Concept Cards**: Great for comparing related concepts or listing options
3. **Progressive Disclosure**: Perfect for optional deep-dives and advanced topics
4. **Content Breaks**: Use between major sections, not within sections
5. **Section Dividers**: Reserve for major topic transitions

Remember: Visual elements should enhance understanding, not distract from content.
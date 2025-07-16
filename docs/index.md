# The Compendium of Distributed Systems

<div style="text-align: center; margin: 2rem 0 3rem 0;">
    <p style="font-size: 1.5rem; font-weight: 300; line-height: 1.6; color: var(--md-default-fg-color--light); max-width: 800px; margin: 0 auto;">
        A first-principles approach to understanding distributed systems, deriving patterns from fundamental physical and mathematical constraints rather than memorizing solutions.
    </p>
</div>

---

## 🚀 Quick Navigation

<div class="grid cards" markdown>

- :material-book-open-page-variant:{ .lg .middle } **[Start Reading →](distributed-systems-book.md)**

    ---

    Dive into the complete compendium and begin your journey from first principles

- :material-map:{ .lg .middle } **[Learning Paths →](distributed-systems-book.md#page-iv-reader-road-map)**

    ---

    Choose a customized path based on your role and experience level

- :material-lightbulb:{ .lg .middle } **[Key Concepts →](#what-youll-learn)**

    ---

    Explore the 8 fundamental axioms that govern all distributed systems

- :material-github:{ .lg .middle } **[Contribute →](https://github.com/deepaucksharma/DStudio)**

    ---

    Join our community and help improve this resource

</div>

## 🗺️ Interactive Journey Map

<div class="journey-container">
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: var(--primary-color);"></div>
            <span>Core Axiom</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: var(--success-color);"></div>
            <span>Practice/Implementation</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: var(--warning-color);"></div>
            <span>Deep Dive Content</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: var(--error-color);"></div>
            <span>Case Study</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #8b5cf6;"></div>
            <span>Theory/Content</span>
        </div>
    </div>
    <svg id="journey-map" style="width: 100%; height: 600px; background: transparent;"></svg>
</div>

<div class="summary-box" id="summaryBox">
    <h3 class="summary-title">Distributed Systems: From Theory to Practice</h3>
    <div class="summary-content">
        <p>A comprehensive journey through the fundamental axioms that govern distributed systems at scale. Each concept builds upon the previous, illustrated with real-world failures and practical implementations.</p>
        
        <div class="summary-grid">
            <div class="summary-item">
                <h4>🎯 Learning Path</h4>
                <p>8 core axioms, 20+ case studies, 50+ patterns organized in a logical progression from basic concepts to advanced implementations.</p>
            </div>
            <div class="summary-item">
                <h4>⚡ Interactive Learning</h4>
                <p>Click any node to explore deeper. Each axiom includes practical exercises, real-world examples, and implementation details.</p>
            </div>
            <div class="summary-item">
                <h4>🔧 Hands-On Practice</h4>
                <p>Every concept paired with coding exercises, system design problems, and production-ready patterns.</p>
            </div>
            <div class="summary-item">
                <h4>📊 Real-World Focus</h4>
                <p>Learn from actual outages at Netflix, Uber, Amazon. Understand not just the theory but the practice.</p>
            </div>
        </div>
        
        <div id="selectedNodeDetails"></div>
    </div>
</div>

## 🎯 Our Philosophy

This project takes a unique approach to teaching distributed systems:

- **Physics First**: We start with the speed of light, not with Kafka
- **Math Over Mythology**: Quantitative trade-offs replace "best practices"
- **Failures as Teachers**: Real production disasters illuminate principles
- **Derive, Don't Memorize**: Every pattern emerges from fundamental constraints


## 📚 What You'll Learn {#what-youll-learn}

<div class="axiom-box animate-fadeIn">

### The Eight Fundamental Axioms

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1.5rem;">

<div>
<h4 style="color: var(--primary-color); margin: 0;">⚡ Latency</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Speed of light is non-negotiable</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">📦 Finite Capacity</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Every resource has a breaking point</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">💥 Failure</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Components will fail; plan accordingly</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">⚖️ Consistency</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">You can't have your cake and eat it too</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">⏰ Time</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">There is no "now" in distributed systems</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">🔄 Ordering</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Events happen, but in what order?</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">🧩 Knowledge</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Partial information is the only information</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">📈 Growth</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Systems evolve or die</p>
</div>

</div>

</div>

## 🛠️ Key Features

- **🎬 Real Failure Stories**: Learn from anonymized production disasters
- **🧮 Quantitative Tools**: Make decisions with math, not gut feelings
- **🔧 Hands-On Exercises**: Try concepts in under 5 minutes
- **💡 Counter-Intuitive Truths**: Challenge your assumptions
- **🎯 Decision Frameworks**: Know when to use which pattern

## 🌟 Why This Approach?

| Traditional Learning | Our Approach |
|---------------------|--------------|
| Memorize patterns | Derive patterns from physics |
| "Best practices" | Context-dependent trade-offs |
| Tool-specific knowledge | Timeless principles |
| Academic theory OR practice | Theory THROUGH practice |

## 🚦 Quick Start: Your First Insight

<div class="truth-box">

### Why does adding more servers sometimes make your system slower?

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1.5rem;">

<div>
<h4 style="margin: 0 0 0.5rem 0;">📊 The Math</h4>

- 2 servers = 1 connection
- 5 servers = 10 connections  
- 10 servers = 45 connections
- n servers = n(n-1)/2 connections

**Coordination cost**: O(n²)  
**Capacity growth**: O(n)
</div>

<div>
<h4 style="margin: 0 0 0.5rem 0;">💡 The Lesson</h4>

Sometimes the best distributed system is the one that isn't distributed. Before adding complexity:

1. **Optimize** what you have
2. **Measure** actual bottlenecks
3. **Calculate** coordination overhead
4. **Consider** vertical scaling first
</div>

</div>

</div>


---

<div style="text-align: center; margin: 3rem 0;">
    <a href="distributed-systems-book.md" class="md-button md-button--primary" style="font-size: 1.1rem; padding: 0.8rem 2rem;">
        Begin Your Journey →
    </a>
</div>

<div style="text-align: center; color: var(--md-default-fg-color--light); font-size: 0.9rem; margin-top: 2rem;">
    Built with ❤️ using <a href="https://squidfunk.github.io/mkdocs-material/">Material for MkDocs</a>
</div>

<!-- Tooltip -->
<div class="tooltip" id="tooltip"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
// Comprehensive table of contents data
const tableOfContents = {
    name: "Distributed Systems Mastery",
    type: "root",
    children: [
        {
            name: "Axiom 1: Network Is Slow",
            type: "axiom",
            id: "network-slow",
            description: "Network latency dominates - 6 orders of magnitude slower than memory",
            children: [
                {
                    name: "Latency Numbers",
                    type: "content",
                    description: "L1 cache: 0.5ns, Network: 500μs, Cross-region: 150ms",
                    topics: ["Hardware basics", "Network RTT", "Speed of light limits"]
                },
                {
                    name: "Batching & Compression",
                    type: "practice",
                    description: "Reduce network calls through batching, use compression wisely",
                    examples: ["GraphQL vs REST", "Protocol Buffers", "HTTP/2 multiplexing"]
                },
                {
                    name: "Netflix CDN Strategy",
                    type: "case-study",
                    description: "How Netflix serves 167M users with edge caching",
                    lessons: ["Open Connect", "ISP partnerships", "Predictive caching"]
                }
            ]
        },
        {
            name: "Axiom 2: Queues Everywhere",
            type: "axiom",
            id: "queues-everywhere",
            description: "Little's Law rules - systems cliff at high utilization",
            children: [
                {
                    name: "Little's Law",
                    type: "content",
                    description: "L = λW: The fundamental equation of queuing theory",
                    topics: ["Queue math", "Utilization curves", "Response time"]
                },
                {
                    name: "The Saturation Cliff",
                    type: "practice",
                    description: "At 95% utilization, wait time = 19x service time",
                    examples: ["CPU scheduling", "Thread pools", "Connection pools"]
                },
                {
                    name: "Uber Surge Pricing",
                    type: "case-study",
                    description: "Managing queues through dynamic pricing",
                    lessons: ["Demand shaping", "Driver utilization", "Market equilibrium"]
                }
            ]
        },
        {
            name: "Axiom 3: Partial Failure",
            type: "axiom",
            id: "partial-failure",
            description: "Systems work AND are broken simultaneously",
            children: [
                {
                    name: "Failure Modes",
                    type: "content",
                    description: "Slow, intermittent, asymmetric, and gray failures",
                    topics: ["Byzantine failures", "Network partitions", "Silent corruption"]
                },
                {
                    name: "Resilience Patterns",
                    type: "practice",
                    description: "Circuit breakers, bulkheads, timeouts, retries",
                    examples: ["Hystrix", "Resilience4j", "Envoy proxy"]
                },
                {
                    name: "2022 Retry Storm",
                    type: "case-study",
                    description: "How one slow DB caused complete outage",
                    lessons: ["Cascading failures", "Retry amplification", "Backpressure"]
                }
            ]
        },
        {
            name: "Axiom 4: Concurrency Chaos",
            type: "axiom",
            id: "concurrency-chaos",
            description: "Concurrent operations create non-sequential states",
            children: [
                {
                    name: "Race Conditions",
                    type: "content",
                    description: "When timing determines correctness",
                    topics: ["Memory models", "Happens-before", "Atomic operations"]
                },
                {
                    name: "Coordination Patterns",
                    type: "practice",
                    description: "Locks, CAS, MVCC, and lock-free algorithms",
                    examples: ["Database isolation levels", "Optimistic locking", "STM"]
                },
                {
                    name: "Double-Booked Seat",
                    type: "case-study",
                    description: "Airline's $40M race condition",
                    lessons: ["Distributed locks", "Compensating transactions", "Saga pattern"]
                }
            ]
        },
        {
            name: "Axiom 5: Coordination Cost",
            type: "axiom",
            id: "coordination-cost",
            description: "Every sync point reduces availability and increases latency",
            children: [
                {
                    name: "Cost Analysis",
                    type: "content",
                    description: "Communication + Consensus + Failure handling costs",
                    topics: ["2PC overhead", "Quorum systems", "Gossip protocols"]
                },
                {
                    name: "Avoiding Coordination",
                    type: "practice",
                    description: "CRDTs, event sourcing, and eventual consistency",
                    examples: ["Riak", "Cassandra", "DynamoDB"]
                },
                {
                    name: "$2M Transaction Cost",
                    type: "case-study",
                    description: "Financial firm's cross-region 2PC nightmare",
                    lessons: ["Regional aggregation", "Eventual consistency", "Cost models"]
                }
            ]
        },
        {
            name: "Axiom 6: CAP Reality",
            type: "axiom",
            id: "cap-reality",
            description: "Partition tolerance isn't optional - choose CP or AP",
            children: [
                {
                    name: "CAP Theorem",
                    type: "content",
                    description: "Why you can't have all three",
                    topics: ["Formal proof", "PACELC extension", "Harvest/Yield"]
                },
                {
                    name: "System Trade-offs",
                    type: "practice",
                    description: "When to choose CP vs AP",
                    examples: ["HBase (CP)", "Cassandra (AP)", "Spanner (CA with bounds)"]
                }
            ]
        },
        {
            name: "Axiom 7: Time Is Relative",
            type: "axiom",
            id: "time-relative",
            description: "No global 'now' - only causality matters",
            children: [
                {
                    name: "Logical Time",
                    type: "content",
                    description: "Lamport timestamps and vector clocks",
                    topics: ["Causality", "Concurrent events", "Clock skew"]
                },
                {
                    name: "Google Spanner",
                    type: "case-study",
                    description: "Using atomic clocks for global consistency",
                    lessons: ["TrueTime API", "Uncertainty bounds", "External consistency"]
                }
            ]
        },
        {
            name: "Axiom 8: State Management",
            type: "axiom",
            id: "state-management",
            description: "State is the root of complexity - minimize and isolate",
            children: [
                {
                    name: "State Patterns",
                    type: "content",
                    description: "Event sourcing, CQRS, and stateless services",
                    topics: ["Immutability", "Append-only logs", "Materialized views"]
                },
                {
                    name: "Scaling State",
                    type: "practice",
                    description: "Sharding, replication, and caching strategies",
                    examples: ["Consistent hashing", "Read replicas", "Write-through cache"]
                }
            ]
        }
    ]
};

// Initialize D3
const margin = {top: 40, right: 120, bottom: 40, left: 120};
const width = 1200;
const height = 600;

const svg = d3.select("#journey-map")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

const treeWidth = width - margin.left - margin.right;
const treeHeight = height - margin.top - margin.bottom;

// Create tree layout - horizontal for better space usage
const tree = d3.tree()
    .size([treeHeight, treeWidth])
    .nodeSize([40, 200])
    .separation((a, b) => a.parent == b.parent ? 1 : 1.5);

// Create hierarchy
const root = d3.hierarchy(tableOfContents);

// Initially collapse all except root and axioms
root.descendants().forEach(d => {
    if (d.depth > 1) {
        d._children = d.children;
        d.children = null;
    }
    d.data.nodeId = `${d.data.type}-${d.data.name.replace(/\s+/g, '-')}`;
});

// Update function
function update(source) {
    const treeData = tree(root);

    treeData.descendants().forEach(d => {
        d.y = d.depth * 200;
    });

    // Update links
    const links = svg.selectAll(".link")
        .data(treeData.links(), d => d.target.data.nodeId);

    links.exit()
        .transition()
        .duration(500)
        .style("opacity", 0)
        .remove();

    const linksEnter = links.enter().append("path")
        .attr("class", "link")
        .style("fill", "none")
        .style("stroke", "var(--md-default-fg-color--lighter)")
        .style("stroke-width", 2)
        .style("opacity", 0)
        .attr("d", d => {
            const o = {x: source.x0, y: source.y0};
            return diagonal({source: o, target: o});
        });

    links.merge(linksEnter)
        .transition()
        .duration(500)
        .style("opacity", 0.6)
        .attr("d", diagonal);

    // Update nodes
    const nodes = svg.selectAll(".node")
        .data(treeData.descendants(), d => d.data.nodeId);

    nodes.exit()
        .transition()
        .duration(500)
        .style("opacity", 0)
        .attr("transform", d => `translate(${source.y0},${source.x0})`)
        .remove();

    const nodeEnter = nodes.enter().append("g")
        .attr("class", d => `node ${d.data.type}`)
        .attr("transform", d => `translate(${source.y0},${source.x0})`)
        .style("opacity", 0);

    // Add rectangles
    nodeEnter.append("rect")
        .attr("class", "node-rect")
        .attr("width", d => {
            if (d.depth === 0) return 180;
            if (d.depth === 1) return 160;
            return 140;
        })
        .attr("height", 35)
        .attr("x", d => {
            if (d.depth === 0) return -90;
            if (d.depth === 1) return -80;
            return -70;
        })
        .attr("y", -17.5)
        .on("click", (event, d) => {
            event.stopPropagation();
            toggleNode(d);
        });

    // Add text
    nodeEnter.append("text")
        .attr("class", "node-text")
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .text(d => {
            if (d.data.name.length > 25) {
                return d.data.name.substring(0, 25) + "...";
            }
            return d.data.name;
        });

    // Update all nodes
    const nodeUpdate = nodes.merge(nodeEnter)
        .transition()
        .duration(500)
        .style("opacity", 1)
        .attr("transform", d => `translate(${d.y},${d.x})`);

    // Store old positions for transition
    nodes.merge(nodeEnter).each(d => {
        d.x0 = d.x;
        d.y0 = d.y;
    });

    // Add hover events
    nodes.merge(nodeEnter)
        .on("mouseenter", (event, d) => showTooltip(event, d))
        .on("mouseleave", hideTooltip)
        .on("click", (event, d) => showNodeDetails(d));
}

// Diagonal link generator
function diagonal(d) {
    return `M ${d.source.y} ${d.source.x}
            C ${(d.source.y + d.target.y) / 2} ${d.source.x},
              ${(d.source.y + d.target.y) / 2} ${d.target.x},
              ${d.target.y} ${d.target.x}`;
}

function toggleNode(d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else {
        d.children = d._children;
        d._children = null;
    }
    update(d);
}

// Tooltip functions
function showTooltip(event, d) {
    const tooltip = document.getElementById("tooltip");
    if (d.data.description) {
        tooltip.innerHTML = `
            <strong>${d.data.name}</strong><br>
            ${d.data.description}
        `;
        tooltip.style.left = event.pageX + 10 + "px";
        tooltip.style.top = event.pageY - 30 + "px";
        tooltip.classList.add("active");
    }
}

function hideTooltip() {
    document.getElementById("tooltip").classList.remove("active");
}

// Show node details
function showNodeDetails(d) {
    const detailsDiv = document.getElementById("selectedNodeDetails");
    if (d.depth === 0) return;

    let html = `<div class="node-details">
        <h3>${d.data.name}</h3>
        <p>${d.data.description}</p>`;

    if (d.data.topics) {
        html += `<p><strong>Topics:</strong></p><ul>`;
        d.data.topics.forEach(topic => {
            html += `<li>${topic}</li>`;
        });
        html += `</ul>`;
    }

    if (d.data.examples) {
        html += `<p><strong>Examples:</strong></p><ul>`;
        d.data.examples.forEach(example => {
            html += `<li>${example}</li>`;
        });
        html += `</ul>`;
    }

    if (d.data.lessons) {
        html += `<p><strong>Key Lessons:</strong></p><ul>`;
        d.data.lessons.forEach(lesson => {
            html += `<li>${lesson}</li>`;
        });
        html += `</ul>`;
    }

    html += `</div>`;
    detailsDiv.innerHTML = html;
}

// Initial render
root.x0 = treeHeight / 2;
root.y0 = 0;
update(root);
</script>
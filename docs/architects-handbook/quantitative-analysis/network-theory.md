---
title: Network Theory for Distributed Systems
description: Graph theory, network models, and communication patterns for understanding
  distributed system topologies
type: quantitative
difficulty: intermediate
reading_time: 40 min
prerequisites:
- graph-theory-basics
- probability
pattern_type: various
status: complete
last_updated: 2025-01-23
---


# Network Theory for Distributed Systems

!!! abstract "🎯 Core Principle"
 Network theory provides mathematical tools to analyze communication patterns, failure propagation, and information flow in distributed systems. Understanding network properties helps design more resilient and efficient architectures.

## Visual Network Models

```mermaid
graph TB
 subgraph "Network Topologies"
 subgraph "Star"
 C1[Central] --> N1[Node]
 C1 --> N2[Node]
 C1 --> N3[Node]
 C1 --> N4[Node]
 end
 
 subgraph "Mesh"
 M1[Node] --- M2[Node]
 M1 --- M3[Node]
 M1 --- M4[Node]
 M2 --- M3
 M2 --- M4
 M3 --- M4
 end
 
 subgraph "Ring"
 R1[Node] --> R2[Node]
 R2 --> R3[Node]
 R3 --> R4[Node]
 R4 --> R1
 end
 end
```

## Fundamental Network Metrics

### 1. Degree Distribution

!!! example "Node Degree"
 <table class="formula-table responsive-table">
 <tr><td><strong>k_i</strong></td><td>Degree of node i (number of connections)</td></tr>
 <tr><td><strong>⟨k⟩</strong></td><td>Average degree = 2E/N</td></tr>
 <tr><td><strong>P(k)</strong></td><td>Probability of degree k</td></tr>
 </table>

 **Common Distributions**:
 - **Random**: P(k) ~ Poisson(λ)
 - **Scale-free**: P(k) ~ k^(-γ)
 - **Regular**: P(k) = δ(k - k₀)

### 2. Path Metrics

```python
def network_metrics(graph):
 """Calculate key network metrics"""
 metrics = {
 'diameter': nx.diameter(graph),
 'avg_path_length': nx.average_shortest_path_length(graph),
 'clustering_coefficient': nx.average_clustering(graph),
 'degree_centrality': nx.degree_centrality(graph),
 'betweenness': nx.betweenness_centrality(graph)
 }
 return metrics

# Example: Data center network
# Diameter: 6 (worst-case hops)
# Avg path: 3.2 (typical communication)
# Clustering: 0.15 (triangles/triples)
```

## Network Models in Distributed Systems

### 1. Small World Networks

```mermaid
graph TB
 subgraph "Small World Properties"
 Local[High Local<br/>Clustering]
 Short[Short Average<br/>Path Length]
 Random[Few Random<br/>Long Links]
 end
 
 subgraph "Benefits"
 Fast[Fast Information<br/>Propagation]
 Robust[Robust to<br/>Random Failures]
 Efficient[Efficient<br/>Routing]
 end
 
 Local --> Fast
 Short --> Fast
 Random --> Efficient
```

**Watts-Strogatz Model**:
```python
def small_world_network(n, k, p):
 """
 n: number of nodes
 k: initial neighbors
 p: rewiring probability
 """
# Start with ring lattice
 G = nx.watts_strogatz_graph(n, k, p)
 
# Properties:
# p=0: Regular lattice (high clustering, long paths)
# p=1: Random graph (low clustering, short paths)
# 0<p<1: Small world (high clustering, short paths)
 return G
```

### 2. Scale-Free Networks

<h4>Barabási-Albert Model</h4>

**Preferential Attachment**: New nodes connect to existing nodes with probability proportional to their degree.

```python
def scale_free_growth(initial_nodes=3, total_nodes=1000, m=2):
 """Generate scale-free network via preferential attachment"""
 G = nx.barabasi_albert_graph(total_nodes, m)
 
# Power-law degree distribution
# P(k) ~ k^(-3) for BA model
# Few hubs, many low-degree nodes
 return G
```

**Properties**:
- **Hubs**: Few highly connected nodes
- **Resilient**: To random failures
- **Vulnerable**: To targeted attacks on hubs

## Communication Patterns

### 1. Broadcast Algorithms

```mermaid
graph TD
 subgraph "Broadcast Strategies"
 subgraph "Flooding"
 F1[Source] --> F2[Node]
 F1 --> F3[Node]
 F2 --> F4[Node]
 F3 --> F4
 F2 --> F5[Node]
 F3 --> F5
 end
 
 subgraph "Tree-Based"
 T1[Root] --> T2[L1]
 T1 --> T3[L1]
 T2 --> T4[L2]
 T2 --> T5[L2]
 T3 --> T6[L2]
 T3 --> T7[L2]
 end
 
 subgraph "Gossip"
 G1[Node] -.->|Random| G2[Node]
 G2 -.->|Random| G3[Node]
 G3 -.->|Random| G4[Node]
 end
 end
```

### 2. Epidemic Spread Models

```python
def epidemic_spread(graph, infection_prob=0.1, recovery_prob=0.05):
 """SIR model on network"""
 states = {node: 'S' for node in graph.nodes()} # Susceptible
 patient_zero = random.choice(list(graph.nodes()))
 states[patient_zero] = 'I' # Infected
 
 infected_over_time = []
 
 while 'I' in states.values():
 new_states = states.copy()
 
 for node in graph.nodes():
 if states[node] == 'I':
# Try to infect neighbors
 for neighbor in graph.neighbors(node):
 if states[neighbor] == 'S' and random.random() < infection_prob:
 new_states[neighbor] = 'I'
 
# Try to recover
 if random.random() < recovery_prob:
 new_states[node] = 'R' # Recovered
 
 states = new_states
 infected_over_time.append(sum(1 for s in states.values() if s == 'I'))
 
 return infected_over_time
```

## Network Reliability

### 1. Failure Propagation

```mermaid
graph TB
 subgraph "Cascading Failures"
 Init[Initial<br/>Failure] --> Over1[Overload<br/>Neighbor]
 Over1 --> Fail1[Secondary<br/>Failure]
 Fail1 --> Over2[More<br/>Overload]
 Over2 --> Cascade[Cascade<br/>Effect]
 end
 
 subgraph "Mitigation"
 Redundancy[Add<br/>Redundancy]
 Capacity[Excess<br/>Capacity]
 Isolation[Failure<br/>Isolation]
 end
```

### 2. Percolation Theory

!!! example "Critical Threshold"

 For random failures with probability p:
 - **Connected**: p < p_c (critical threshold)
 - **Fragmented**: p > p_c

 **Critical thresholds**:
 - Random graph: p_c = 1/⟨k⟩
 - 2D lattice: p_c ≈ 0.593
 - Scale-free: p_c → 0 (very robust)

## Network Flow Algorithms

### 1. Max Flow Problem

```python
def max_flow_analysis(graph, source, sink):
 """Analyze maximum flow in network"""
# Ford-Fulkerson algorithm
 flow_value, flow_dict = nx.maximum_flow(graph, source, sink)
 
# Find bottlenecks (min cut)
 cut_value, (reachable, non_reachable) = nx.minimum_cut(graph, source, sink)
 
# Identify critical edges
 critical_edges = []
 for u, v in graph.edges():
 if u in reachable and v in non_reachable:
 critical_edges.append((u, v))
 
 return {
 'max_flow': flow_value,
 'min_cut': cut_value,
 'bottlenecks': critical_edges
 }
```

### 2. Load Balancing

```mermaid
graph LR
 subgraph "Load Distribution"
 Source[Traffic<br/>Source] --> LB[Load<br/>Balancer]
 LB -->|33%| S1[Server 1]
 LB -->|33%| S2[Server 2]
 LB -->|34%| S3[Server 3]
 end
 
 subgraph "Algorithms"
 RR[Round Robin]
 WRR[Weighted RR]
 LC[Least Connections]
 CH[Consistent Hash]
 end
```

## Distributed System Topologies

### 1. Data Center Networks

```mermaid
graph TB
 subgraph "Fat-Tree Topology"
 subgraph "Core"
 C1[Core1] --- C2[Core2]
 C1 --- C3[Core3]
 C2 --- C4[Core4]
 C3 --- C4
 end
 
 subgraph "Aggregation"
 A1[Agg1] --- A2[Agg2]
 A3[Agg3] --- A4[Agg4]
 end
 
 subgraph "Edge"
 E1[Edge1]
 E2[Edge2]
 E3[Edge3]
 E4[Edge4]
 end
 
 C1 --- A1
 C2 --- A1
 C3 --- A3
 C4 --- A3
 
 A1 --- E1
 A1 --- E2
 A3 --- E3
 A3 --- E4
 end
```

### 2. P2P Network Structures

<table class="responsive-table">
<thead>
<tr>
<th>Topology</th>
<th>Lookup Time</th>
<th>State/Node</th>
<th>Resilience</th>
<th>Example</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Topology"><strong>Unstructured</strong></td>
<td data-label="Lookup Time">O(N)</td>
<td data-label="State/Node">O(1)</td>
<td data-label="Resilience">High</td>
<td data-label="Example">Gnutella</td>
</tr>
<tr>
<td data-label="Topology"><strong>DHT Ring</strong></td>
<td data-label="Lookup Time">O(log N)</td>
<td data-label="State/Node">O(log N)</td>
<td data-label="Resilience">Medium</td>
<td data-label="Example">Chord</td>
</tr>
<tr>
<td data-label="Topology"><strong>Hypercube</strong></td>
<td data-label="Lookup Time">O(log N)</td>
<td data-label="State/Node">O(log N)</td>
<td data-label="Resilience">High</td>
<td data-label="Example">CAN</td>
</tr>
<tr>
<td data-label="Topology"><strong>Skip Graph</strong></td>
<td data-label="Lookup Time">O(log N)</td>
<td data-label="State/Node">O(log N)</td>
<td data-label="Resilience">High</td>
<td data-label="Example">Skip Net</td>
</tr>
</tbody>
</table>

## Consensus Network Requirements

### Byzantine Fault Tolerance

```python
def byzantine_generals(n, f):
 """
 n: total nodes
 f: byzantine nodes
 """
# Requirement: n > 3f
 if n <= 3 * f:
 return "No consensus possible"
 
# Rounds needed: f + 1
 rounds = f + 1
 
# Message complexity: O(n²) per round
 messages = rounds * n * (n - 1)
 
 return {
 'feasible': True,
 'rounds': rounds,
 'messages': messages,
 'resilience': f'{f}/{n} byzantine nodes'
 }
```

## Network Partitioning

### Detecting Partitions

```mermaid
graph TB
 subgraph "Network Partition"
 subgraph "Partition A"
 A1[Node] --- A2[Node]
 A1 --- A3[Node]
 end
 
 subgraph "Partition B"
 B1[Node] --- B2[Node]
 B2 --- B3[Node]
 end
 
 A1 -.X.- B1
 A2 -.X.- B2
 end
 
 subgraph "Detection Methods"
 HB[Heartbeat<br/>Timeout]
 QS[Quorum<br/>Size]
 ML[Membership<br/>List]
 end
```

## Performance Analysis

### Network Latency Model

```python
def network_latency(distance_km, processing_ms=1, queuing_ms=0):
 """Total latency calculation"""
# Speed of light in fiber: ~200,000 km/s
 propagation_ms = distance_km / 200
 
# Total latency
 total_ms = propagation_ms + processing_ms + queuing_ms
 
 return {
 'propagation': f'{propagation_ms:.1f}ms',
 'processing': f'{processing_ms}ms',
 'queuing': f'{queuing_ms}ms',
 'total': f'{total_ms:.1f}ms',
 'round_trip': f'{2 * total_ms:.1f}ms'
 }

# Examples:
# Same city (10km): ~0.1ms RTT
# Cross-country (4000km): ~40ms RTT
# Cross-ocean (10000km): ~100ms RTT
```

## Key Insights

!!! info "🎯 Network Theory Principles"
 1. **Diameter matters**: Affects worst-case latency
 2. **Clustering creates redundancy**: Higher resilience
 3. **Hubs are double-edged**: Efficient but vulnerable
 4. **Topology determines properties**: Choose wisely
 5. **Partitions are inevitable**: Design for split-brain
 6. **Communication complexity**: Often quadratic in nodes

## Related Topics

- **Theory**: [Graph Theory](/architects-handbook/quantitative-analysis/graph-theory/) | [Queueing Networks](/architects-handbook/quantitative-analysis/queuing-networks/) | [Information Theory](/architects-handbook/quantitative-analysis/information-theory/)
- **Practice**: [Network Protocols](../patterns/network-protocols.md) | [Consensus](../pattern-library/coordination/consensus.md) | [P2P Systems](../patterns/p2p.md)
- **Laws**: [Law 2: Asynchronous Reality](../core-principles/laws/asynchronous-reality.md) | [Law 5: Distributed Knowledge](../core-principles/laws/distributed-knowledge.md)

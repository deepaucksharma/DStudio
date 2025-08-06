---
title: Graph Theory
description: Mathematical foundations of graphs, network algorithms, and their applications to distributed systems analysis
type: quantitative
difficulty: advanced
reading_time: 55 min
prerequisites: [linear-algebra, discrete-mathematics, probability-theory]
pattern_type: foundational
status: complete
last_updated: 2025-01-23
category: architects-handbook
tags: [architects-handbook]
date: 2025-08-07
---

# Graph Theory



## Overview

Graph Theory
description: Mathematical foundations of graphs, network algorithms, and their applications to distributed systems analysis
type: quantitative
difficulty: advanced
reading_time: 55 min
prerequisites: [linear-algebra, discrete-mathematics, probability-theory]
pattern_type: foundational
status: complete
last_updated: 2025-01-23
---

# Graph Theory

## Table of Contents

- [Mathematical Foundations](#mathematical-foundations)
  - [Basic Definitions and Properties](#basic-definitions-and-properties)
  - [Graph Representations](#graph-representations)
    - [Adjacency Matrix](#adjacency-matrix)
    - [Adjacency List](#adjacency-list)
- [Example usage](#example-usage)
- [Create a sample graph](#create-a-sample-graph)
- [Shortest Path Algorithms](#shortest-path-algorithms)
  - [Dijkstra's Algorithm](#dijkstras-algorithm)
- [Example: Shortest paths](#example-shortest-paths)
  - [Bellman-Ford Algorithm](#bellman-ford-algorithm)
  - [Floyd-Warshall Algorithm](#floyd-warshall-algorithm)
  - [Example usage with adjacency matrix](#example-usage-with-adjacency-matrix)
- [Replace zeros with infinity (except diagonal)](#replace-zeros-with-infinity-except-diagonal)
- [Minimum Spanning Trees](#minimum-spanning-trees)
  - [Kruskal's Algorithm](#kruskals-algorithm)
- [Example: MST](#example-mst)
  - [Prim's Algorithm](#prims-algorithm)
- [Compare Kruskal and Prim](#compare-kruskal-and-prim)
- [Network Flow Algorithms](#network-flow-algorithms)
  - [Maximum Flow Problem](#maximum-flow-problem)
  - [Ford-Fulkerson Algorithm](#ford-fulkerson-algorithm)
- [Example: Create flow network](#example-create-flow-network)
- [Spectral Graph Theory](#spectral-graph-theory)
  - [Graph Laplacian](#graph-laplacian)
  - [Spectral Clustering](#spectral-clustering)
- [Example: Spectral analysis](#example-spectral-analysis)
- [Spectral clustering](#spectral-clustering)
- [Centrality Measures](#centrality-measures)
  - [Degree Centrality](#degree-centrality)
  - [Betweenness Centrality](#betweenness-centrality)
  - [Closeness Centrality](#closeness-centrality)
  - [PageRank (Eigenvector Centrality)](#pagerank-eigenvector-centrality)
- [Example: Centrality analysis](#example-centrality-analysis)
- [Community Detection](#community-detection)
  - [Modularity](#modularity)
  - [Louvain Algorithm](#louvain-algorithm)
- [Example: Community detection](#example-community-detection)
- [Applications in Distributed Systems](#applications-in-distributed-systems)
  - [Service Dependency Analysis](#service-dependency-analysis)
- [Example: Service dependency analysis](#example-service-dependency-analysis)
  - [Network Routing and Load Balancing](#network-routing-and-load-balancing)
- [Example: Network routing analysis](#example-network-routing-analysis)
- [Link weights (latencies in ms)](#link-weights-latencies-in-ms)
- [Advanced Graph Algorithms](#advanced-graph-algorithms)
  - [Graph Coloring](#graph-coloring)
- [Example: Graph coloring](#example-graph-coloring)
  - [Matching Algorithms](#matching-algorithms)
- [Example: Bipartite matching](#example-bipartite-matching)
- [Performance Analysis and Complexity](#performance-analysis-and-complexity)
  - [Algorithm Complexity Summary](#algorithm-complexity-summary)
  - [Graph Properties and Thresholds](#graph-properties-and-thresholds)
- [Interactive Visualization and Tools](#interactive-visualization-and-tools)
  - [Graph Visualization](#graph-visualization)
- [Research Frontiers and Modern Applications](#research-frontiers-and-modern-applications)
  - [Graph Neural Networks](#graph-neural-networks)
  - [Dynamic Graphs](#dynamic-graphs)
  - [Quantum Graph Algorithms](#quantum-graph-algorithms)
- [References and Further Reading](#references-and-further-reading)
  - [Foundational Texts](#foundational-texts)
  - [Algorithms and Complexity](#algorithms-and-complexity)
  - [Spectral Graph Theory](#spectral-graph-theory)
  - [Network Analysis](#network-analysis)
  - [Applications in Computer Science](#applications-in-computer-science)
- [Related Topics](#related-topics)



## Mathematical Foundations

Graph theory provides the mathematical framework for analyzing networks, relationships, and connectivity patterns in distributed systems. A graph $G = (V, E)$ consists of a set of vertices (nodes) $V$ and a set of edges $E \subseteq V \times V$.

**Reading time:** ~22 minutes

## Table of Contents

- [Mathematical Foundations](#mathematical-foundations)
  - [Basic Definitions and Properties](#basic-definitions-and-properties)
  - [Graph Representations](#graph-representations)
    - [Adjacency Matrix](#adjacency-matrix)
    - [Adjacency List](#adjacency-list)
- [Example usage](#example-usage)
- [Create a sample graph](#create-a-sample-graph)
- [Shortest Path Algorithms](#shortest-path-algorithms)
  - [Dijkstra's Algorithm](#dijkstras-algorithm)
- [Example: Shortest paths](#example-shortest-paths)
  - [Bellman-Ford Algorithm](#bellman-ford-algorithm)
  - [Floyd-Warshall Algorithm](#floyd-warshall-algorithm)
  - [Example usage with adjacency matrix](#example-usage-with-adjacency-matrix)
- [Replace zeros with infinity (except diagonal)](#replace-zeros-with-infinity-except-diagonal)
- [Minimum Spanning Trees](#minimum-spanning-trees)
  - [Kruskal's Algorithm](#kruskals-algorithm)
- [Example: MST](#example-mst)
  - [Prim's Algorithm](#prims-algorithm)
- [Compare Kruskal and Prim](#compare-kruskal-and-prim)
- [Network Flow Algorithms](#network-flow-algorithms)
  - [Maximum Flow Problem](#maximum-flow-problem)
  - [Ford-Fulkerson Algorithm](#ford-fulkerson-algorithm)
- [Example: Create flow network](#example-create-flow-network)
- [Spectral Graph Theory](#spectral-graph-theory)
  - [Graph Laplacian](#graph-laplacian)
  - [Spectral Clustering](#spectral-clustering)
- [Example: Spectral analysis](#example-spectral-analysis)
- [Spectral clustering](#spectral-clustering)
- [Centrality Measures](#centrality-measures)
  - [Degree Centrality](#degree-centrality)
  - [Betweenness Centrality](#betweenness-centrality)
  - [Closeness Centrality](#closeness-centrality)
  - [PageRank (Eigenvector Centrality)](#pagerank-eigenvector-centrality)
- [Example: Centrality analysis](#example-centrality-analysis)
- [Community Detection](#community-detection)
  - [Modularity](#modularity)
  - [Louvain Algorithm](#louvain-algorithm)
- [Example: Community detection](#example-community-detection)
- [Applications in Distributed Systems](#applications-in-distributed-systems)
  - [Service Dependency Analysis](#service-dependency-analysis)
- [Example: Service dependency analysis](#example-service-dependency-analysis)
  - [Network Routing and Load Balancing](#network-routing-and-load-balancing)
- [Example: Network routing analysis](#example-network-routing-analysis)
- [Link weights (latencies in ms)](#link-weights-latencies-in-ms)
- [Advanced Graph Algorithms](#advanced-graph-algorithms)
  - [Graph Coloring](#graph-coloring)
- [Example: Graph coloring](#example-graph-coloring)
  - [Matching Algorithms](#matching-algorithms)
- [Example: Bipartite matching](#example-bipartite-matching)
- [Performance Analysis and Complexity](#performance-analysis-and-complexity)
  - [Algorithm Complexity Summary](#algorithm-complexity-summary)
  - [Graph Properties and Thresholds](#graph-properties-and-thresholds)
- [Interactive Visualization and Tools](#interactive-visualization-and-tools)
  - [Graph Visualization](#graph-visualization)
- [Research Frontiers and Modern Applications](#research-frontiers-and-modern-applications)
  - [Graph Neural Networks](#graph-neural-networks)
  - [Dynamic Graphs](#dynamic-graphs)
  - [Quantum Graph Algorithms](#quantum-graph-algorithms)
- [References and Further Reading](#references-and-further-reading)
  - [Foundational Texts](#foundational-texts)
  - [Algorithms and Complexity](#algorithms-and-complexity)
  - [Spectral Graph Theory](#spectral-graph-theory)
  - [Network Analysis](#network-analysis)
  - [Applications in Computer Science](#applications-in-computer-science)
- [Related Topics](#related-topics)



## Mathematical Foundations

Graph theory provides the mathematical framework for analyzing networks, relationships, and connectivity patterns in distributed systems. A graph $G = (V, E)$ consists of a set of vertices (nodes) $V$ and a set of edges $E \subseteq V \times V$.

### Basic Definitions and Properties

**Types of Graphs**:
- **Simple Graph**: No loops or multiple edges
- **Directed Graph (Digraph)**: Edges have direction
- **Weighted Graph**: Edges have associated weights
- **Bipartite Graph**: Vertices can be divided into two disjoint sets

**Fundamental Properties**:
- **Degree**: $\deg(v) = |N(v)|$ where $N(v)$ is the neighborhood of $v$
- **Handshaking Lemma**: $\sum_{v \in V} \deg(v) = 2|E|$
- **Density**: $\delta = \frac{2|E|}{|V|(|V|-1)}$ for undirected graphs

### Graph Representations

#### Adjacency Matrix
For graph $G = (V,E)$ with $|V| = n$:
$$A_{ij} = \begin{cases} 1 & \text{if } (v_i, v_j) \in E \\ 0 & \text{otherwise} \end{cases}$$

**Properties**:
- Symmetric for undirected graphs: $A = A^T$
- $(A^k)_{ij}$ counts $k$-length paths from $v_i$ to $v_j$
- Space complexity: $O(n^2)$

#### Adjacency List
Each vertex $v$ maintains list $Adj[v]$ of adjacent vertices.

**Properties**:
- Space complexity: $O(|V| + |E|)$
- Better for sparse graphs: $|E| \ll |V|^2$

```python
import numpy as np
import networkx as nx
from collections import defaultdict, deque
import heapq
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path, minimum_spanning_tree

class Graph:
    """Comprehensive graph data structure with multiple representations"""
    
    def __init__(self, vertices=None, directed=False, weighted=False):
        self.directed = directed
        self.weighted = weighted
        self.vertices = set(vertices) if vertices else set()
        
        # Multiple representations
        self.adj_list = defaultdict(dict if weighted else list)
        self.adj_matrix = None
        self.edges = set()
        
    def add_vertex(self, v):
        """Add a vertex to the graph"""
        self.vertices.add(v)
        if v not in self.adj_list:
            self.adj_list[v] = {} if self.weighted else []
    
    def add_edge(self, u, v, weight=1):
        """Add an edge to the graph"""
        self.add_vertex(u)
        self.add_vertex(v)
        
        if self.weighted:
            self.adj_list[u][v] = weight
            if not self.directed:
                self.adj_list[v][u] = weight
        else:
            if v not in self.adj_list[u]:
                self.adj_list[u].append(v)
            if not self.directed and u not in self.adj_list[v]:
                self.adj_list[v].append(u)
        
        self.edges.add((u, v) if self.directed else tuple(sorted([u, v])))
    
    def to_adjacency_matrix(self):
        """Convert to adjacency matrix representation"""
        n = len(self.vertices)
        vertex_to_idx = {v: i for i, v in enumerate(sorted(self.vertices))}
        
        matrix = np.zeros((n, n))
        
        for u in self.vertices:
            i = vertex_to_idx[u]
            if self.weighted:
                for v, weight in self.adj_list[u].items():
                    j = vertex_to_idx[v]
                    matrix[i][j] = weight
            else:
                for v in self.adj_list[u]:
                    j = vertex_to_idx[v]
                    matrix[i][j] = 1
        
        self.adj_matrix = matrix
        return matrix, vertex_to_idx
    
    def get_degree_sequence(self):
        """Get degree sequence of the graph"""
        degrees = []
        for v in self.vertices:
            if self.weighted:
                degree = len(self.adj_list[v])
            else:
                degree = len(self.adj_list[v])
            degrees.append(degree)
        return sorted(degrees, reverse=True)
    
    def is_connected(self):
        """Check if the graph is connected (undirected)"""
        if self.directed:
            raise ValueError("Use strongly_connected for directed graphs")
        
        if not self.vertices:
            return True
        
        visited = set()
        start = next(iter(self.vertices))
        self._dfs(start, visited)
        
        return len(visited) == len(self.vertices)
    
    def _dfs(self, v, visited):
        """Depth-first search helper"""
        visited.add(v)
        neighbors = self.adj_list[v].keys() if self.weighted else self.adj_list[v]
        for u in neighbors:
            if u not in visited:
                self._dfs(u, visited)

## Example usage
print("Graph Theory Examples")
print("=" * 50)

## Create a sample graph
g = Graph(directed=False, weighted=True)
edges = [('A', 'B', 4), ('A', 'C', 2), ('B', 'C', 1), 
         ('B', 'D', 5), ('C', 'D', 8), ('C', 'E', 10), ('D', 'E', 2)]

for u, v, w in edges:
    g.add_edge(u, v, w)

print(f"Vertices: {g.vertices}")
print(f"Edges: {g.edges}")
print(f"Degree sequence: {g.get_degree_sequence()}")
print(f"Connected: {g.is_connected()}")
```

## Shortest Path Algorithms

### Dijkstra's Algorithm

For graphs with non-negative weights, Dijkstra's algorithm finds shortest paths from a source vertex.

**Algorithm Complexity**: $O((|V| + |E|) \log |V|)$ with binary heap

**Mathematical Foundation**: 
- **Relaxation**: If $d[u] + w(u,v) < d[v]$, then $d[v] = d[u] + w(u,v)$
- **Correctness**: Based on the optimal substructure property

```python
def dijkstra(graph, source):
    """
    Dijkstra's shortest path algorithm
    Returns distances and predecessors
    """
    distances = {v: float('inf') for v in graph.vertices}
    predecessors = {v: None for v in graph.vertices}
    distances[source] = 0
    
    # Priority queue: (distance, vertex)
    pq = [(0, source)]
    visited = set()
    
    while pq:
        current_dist, u = heapq.heappop(pq)
        
        if u in visited:
            continue
        
        visited.add(u)
        
        # Relax neighbors
        neighbors = graph.adj_list[u].items() if graph.weighted else [(v, 1) for v in graph.adj_list[u]]
        for v, weight in neighbors:
            if v not in visited:
                new_dist = current_dist + weight
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    predecessors[v] = u
                    heapq.heappush(pq, (new_dist, v))
    
    return distances, predecessors

def reconstruct_path(predecessors, source, target):
    """Reconstruct shortest path from predecessors"""
    path = []
    current = target
    
    while current is not None:
        path.append(current)
        current = predecessors[current]
    
    path.reverse()
    return path if path[0] == source else None

## Example: Shortest paths
distances, preds = dijkstra(g, 'A')
print(f"\nShortest distances from A: {distances}")

path_to_e = reconstruct_path(preds, 'A', 'E')
print(f"Shortest path A → E: {' → '.join(path_to_e)}")
print(f"Path length: {distances['E']}")
```

### Bellman-Ford Algorithm

Handles graphs with negative weights and detects negative cycles.

**Algorithm Complexity**: $O(|V||E|)$

**Key Insight**: After $|V|-1$ iterations, all shortest paths are found. A $|V|$-th iteration detecting improvements indicates negative cycles.

```python
def bellman_ford(graph, source):
    """
    Bellman-Ford algorithm for graphs with negative weights
    Returns distances, predecessors, and whether negative cycle exists
    """
    distances = {v: float('inf') for v in graph.vertices}
    predecessors = {v: None for v in graph.vertices}
    distances[source] = 0
    
    # Relax all edges |V|-1 times
    for _ in range(len(graph.vertices) - 1):
        for u in graph.vertices:
            neighbors = graph.adj_list[u].items() if graph.weighted else [(v, 1) for v in graph.adj_list[u]]
            for v, weight in neighbors:
                if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u
    
    # Check for negative cycles
    has_negative_cycle = False
    for u in graph.vertices:
        neighbors = graph.adj_list[u].items() if graph.weighted else [(v, 1) for v in graph.adj_list[u]]
        for v, weight in neighbors:
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                has_negative_cycle = True
                break
        if has_negative_cycle:
            break
    
    return distances, predecessors, has_negative_cycle
```

### Floyd-Warshall Algorithm

Finds shortest paths between all pairs of vertices.

**Algorithm Complexity**: $O(|V|^3)$

**Recurrence Relation**:
$$d_{ij}^{(k)} = \min(d_{ij}^{(k-1)}, d_{ik}^{(k-1)} + d_{kj}^{(k-1)})$$

where $d_{ij}^{(k)}$ is shortest path from $i$ to $j$ using vertices $\{1, 2, \ldots, k\}$ as intermediates.

```python
def floyd_warshall(adj_matrix):
    """
    Floyd-Warshall all-pairs shortest path algorithm
    """
    n = adj_matrix.shape[0]
    
    # Initialize distance matrix
    dist = np.copy(adj_matrix)
    
    # Set diagonal to 0 and infinity for non-edges
    for i in range(n):
        for j in range(n):
            if i == j:
                dist[i][j] = 0
            elif dist[i][j] == 0 and i != j:
                dist[i][j] = float('inf')
    
    # Floyd-Warshall main loop
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    return dist

### Example usage with adjacency matrix
adj_matrix, vertex_map = g.to_adjacency_matrix()
print(f"\nAdjacency matrix:\n{adj_matrix}")

## Replace zeros with infinity (except diagonal)
for i in range(adj_matrix.shape[0]):
    for j in range(adj_matrix.shape[1]):
        if i != j and adj_matrix[i][j] == 0:
            adj_matrix[i][j] = float('inf')

all_pairs_dist = floyd_warshall(adj_matrix)
print(f"All-pairs shortest distances:\n{all_pairs_dist}")
```

## Minimum Spanning Trees

### Kruskal's Algorithm

Finds minimum spanning tree using edge-based greedy approach with Union-Find.

**Algorithm Complexity**: $O(|E| \log |E|)$

**Mathematical Foundation**: 
- **Cut Property**: For any cut $(S, V-S)$, the minimum weight edge crossing the cut is in the MST
- **Cycle Property**: Maximum weight edge in any cycle is not in MST

```python
class UnionFind:
    """Union-Find (Disjoint Set Union) data structure"""
    
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}
    
    def find(self, x):
        """Find root with path compression"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        """Union by rank"""
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x != root_y:
            if self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            elif self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
            else:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1
            return True
        return False

def kruskal_mst(graph):
    """
    Kruskal's algorithm for Minimum Spanning Tree
    """
    # Create list of all edges with weights
    edges = []
    for u in graph.vertices:
        if graph.weighted:
            for v, weight in graph.adj_list[u].items():
                if not graph.directed or u < v:  # Avoid duplicates in undirected graphs
                    edges.append((weight, u, v))
        else:
            for v in graph.adj_list[u]:
                if not graph.directed or u < v:
                    edges.append((1, u, v))
    
    # Sort edges by weight
    edges.sort()
    
    mst_edges = []
    mst_weight = 0
    uf = UnionFind(graph.vertices)
    
    for weight, u, v in edges:
        if uf.union(u, v):
            mst_edges.append((u, v, weight))
            mst_weight += weight
            
            if len(mst_edges) == len(graph.vertices) - 1:
                break
    
    return mst_edges, mst_weight

## Example: MST
mst_edges, total_weight = kruskal_mst(g)
print(f"\nMinimum Spanning Tree:")
print(f"Edges: {mst_edges}")
print(f"Total weight: {total_weight}")
```

### Prim's Algorithm

Vertex-based greedy approach for MST.

**Algorithm Complexity**: $O(|E| \log |V|)$ with priority queue

```python
def prim_mst(graph, start_vertex=None):
    """
    Prim's algorithm for Minimum Spanning Tree
    """
    if not start_vertex:
        start_vertex = next(iter(graph.vertices))
    
    mst_edges = []
    visited = {start_vertex}
    total_weight = 0
    
    # Priority queue: (weight, from_vertex, to_vertex)
    pq = []
    
    # Add all edges from start vertex
    if graph.weighted:
        for neighbor, weight in graph.adj_list[start_vertex].items():
            heapq.heappush(pq, (weight, start_vertex, neighbor))
    else:
        for neighbor in graph.adj_list[start_vertex]:
            heapq.heappush(pq, (1, start_vertex, neighbor))
    
    while pq and len(visited) < len(graph.vertices):
        weight, u, v = heapq.heappop(pq)
        
        if v not in visited:
            visited.add(v)
            mst_edges.append((u, v, weight))
            total_weight += weight
            
            # Add new edges from v
            if graph.weighted:
                for neighbor, edge_weight in graph.adj_list[v].items():
                    if neighbor not in visited:
                        heapq.heappush(pq, (edge_weight, v, neighbor))
            else:
                for neighbor in graph.adj_list[v]:
                    if neighbor not in visited:
                        heapq.heappush(pq, (1, v, neighbor))
    
    return mst_edges, total_weight

## Compare Kruskal and Prim
prim_mst_edges, prim_total_weight = prim_mst(g)
print(f"\nPrim's MST:")
print(f"Edges: {prim_mst_edges}")
print(f"Total weight: {prim_total_weight}")
```

## Network Flow Algorithms

### Maximum Flow Problem

Given a flow network $G = (V, E)$ with source $s$, sink $t$, and capacity function $c: E \rightarrow \mathbb{R}^+$, find maximum flow from $s$ to $t$.

**Flow Conservation**: $\sum_{u:(u,v) \in E} f(u,v) = \sum_{w:(v,w) \in E} f(v,w)$ for all $v \in V \setminus \{s,t\}$

**Capacity Constraint**: $0 \leq f(e) \leq c(e)$ for all $e \in E$

### Ford-Fulkerson Algorithm

**Max-Flow Min-Cut Theorem**: Maximum flow value equals minimum cut capacity.

```python
def ford_fulkerson(graph, source, sink):
    """
    Ford-Fulkerson algorithm with DFS for finding augmenting paths
    """
    def dfs_path(graph, source, sink, visited, path, min_capacity):
        if source == sink:
            return min_capacity
        
        visited.add(source)
        
        for neighbor, capacity in graph.adj_list[source].items():
            if neighbor not in visited and capacity > 0:
                bottleneck = min(min_capacity, capacity)
                result = dfs_path(graph, neighbor, sink, visited, path + [neighbor], bottleneck)
                
                if result > 0:
                    # Update residual capacities
                    graph.adj_list[source][neighbor] -= result
                    if neighbor not in graph.adj_list:
                        graph.adj_list[neighbor] = {}
                    if source not in graph.adj_list[neighbor]:
                        graph.adj_list[neighbor][source] = 0
                    graph.adj_list[neighbor][source] += result
                    
                    return result
        
        return 0
    
    max_flow_value = 0
    
    while True:
        visited = set()
        path_flow = dfs_path(graph, source, sink, visited, [source], float('inf'))
        
        if path_flow == 0:
            break
        
        max_flow_value += path_flow
    
    return max_flow_value

## Example: Create flow network
flow_graph = Graph(directed=True, weighted=True)
flow_edges = [('s', 'a', 10), ('s', 'b', 8), ('a', 'b', 5), ('a', 'c', 8), 
              ('b', 'c', 2), ('b', 'd', 10), ('c', 't', 10), ('d', 't', 8)]

for u, v, capacity in flow_edges:
    flow_graph.add_edge(u, v, capacity)

max_flow = ford_fulkerson(flow_graph, 's', 't')
print(f"\nMaximum flow from s to t: {max_flow}")
```

## Spectral Graph Theory

### Graph Laplacian

The **Laplacian matrix** $L = D - A$ where $D$ is the degree matrix and $A$ is the adjacency matrix.

**Properties**:
- $L$ is positive semi-definite
- $L\mathbf{1} = \mathbf{0}$ (constant vector is eigenvector with eigenvalue 0)
- Number of connected components = multiplicity of eigenvalue 0

**Normalized Laplacian**: $\mathcal{L} = D^{-1/2}LD^{-1/2}$

### Spectral Clustering

Uses eigenvalues and eigenvectors of the Laplacian for graph partitioning.

```python
def compute_laplacian(adj_matrix, normalized=True):
    """
    Compute graph Laplacian matrix
    """
    n = adj_matrix.shape[0]
    
    # Degree matrix
    degrees = np.sum(adj_matrix, axis=1)
    D = np.diag(degrees)
    
    # Basic Laplacian
    L = D - adj_matrix
    
    if normalized:
        # Normalized Laplacian
        D_inv_sqrt = np.diag(1.0 / np.sqrt(degrees + 1e-10))  # Add small value to avoid division by zero
        L_norm = D_inv_sqrt @ L @ D_inv_sqrt
        return L_norm
    
    return L

def spectral_clustering(adj_matrix, k=2):
    """
    Spectral clustering using normalized Laplacian
    """
    from sklearn.cluster import KMeans
    
    L = compute_laplacian(adj_matrix, normalized=True)
    
    # Compute eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    
    # Use first k eigenvectors (corresponding to smallest eigenvalues)
    features = eigenvectors[:, :k]
    
    # K-means clustering on the eigenvector features
    kmeans = KMeans(n_clusters=k, random_state=42)
    clusters = kmeans.fit_predict(features)
    
    return clusters, eigenvalues, eigenvectors

## Example: Spectral analysis
adj_matrix, _ = g.to_adjacency_matrix()
L = compute_laplacian(adj_matrix)
eigenvals, eigenvecs = np.linalg.eigh(L)

print(f"\nSpectral Analysis:")
print(f"Laplacian eigenvalues: {eigenvals}")
print(f"Algebraic connectivity (Fiedler value): {eigenvals[1]:.4f}")

## Spectral clustering
clusters, eigenvals_norm, _ = spectral_clustering(adj_matrix, k=2)
vertex_list = sorted(g.vertices)
print(f"Spectral clustering (2 clusters):")
for i, vertex in enumerate(vertex_list):
    print(f"  {vertex}: Cluster {clusters[i]}")
```

## Centrality Measures

### Degree Centrality

$$C_D(v) = \frac{\deg(v)}{n-1}$$

### Betweenness Centrality

$$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$

where $\sigma_{st}$ is the number of shortest paths from $s$ to $t$, and $\sigma_{st}(v)$ is the number that pass through $v$.

### Closeness Centrality

$$C_C(v) = \frac{n-1}{\sum_{u \neq v} d(v,u)}$$

### PageRank (Eigenvector Centrality)

$$PR(v) = \frac{1-d}{n} + d \sum_{u:(u,v) \in E} \frac{PR(u)}{|\text{out}(u)|}$$

```python
def compute_centrality_measures(graph):
    """
    Compute various centrality measures
    """
    # Convert to NetworkX for built-in algorithms
    nx_graph = nx.Graph() if not graph.directed else nx.DiGraph()
    
    for u in graph.vertices:
        nx_graph.add_node(u)
    
    for u in graph.vertices:
        if graph.weighted:
            for v, weight in graph.adj_list[u].items():
                nx_graph.add_edge(u, v, weight=weight)
        else:
            for v in graph.adj_list[u]:
                nx_graph.add_edge(u, v)
    
    # Compute centrality measures
    degree_cent = nx.degree_centrality(nx_graph)
    betweenness_cent = nx.betweenness_centrality(nx_graph)
    closeness_cent = nx.closeness_centrality(nx_graph)
    
    if not graph.directed:
        eigenvector_cent = nx.eigenvector_centrality(nx_graph)
    else:
        eigenvector_cent = nx.pagerank(nx_graph)
    
    return {
        'degree': degree_cent,
        'betweenness': betweenness_cent,
        'closeness': closeness_cent,
        'eigenvector': eigenvector_cent
    }

## Example: Centrality analysis
centrality_measures = compute_centrality_measures(g)

print(f"\nCentrality Measures:")
for measure, values in centrality_measures.items():
    print(f"\n{measure.capitalize()} Centrality:")
    for vertex, score in sorted(values.items(), key=lambda x: x[1], reverse=True):
        print(f"  {vertex}: {score:.4f}")
```

## Community Detection

### Modularity

**Newman-Girvan Modularity**:
$$Q = \frac{1}{2m} \sum_{ij} \left(A_{ij} - \frac{k_i k_j}{2m}\right) \delta(c_i, c_j)$$

where $m = \frac{1}{2}\sum_{ij} A_{ij}$, $k_i$ is degree of vertex $i$, $c_i$ is community of vertex $i$, and $\delta(c_i, c_j) = 1$ if $c_i = c_j$.

### Louvain Algorithm

Hierarchical community detection algorithm maximizing modularity.

```python
def louvain_community_detection(graph, resolution=1.0):
    """
    Simplified Louvain algorithm for community detection
    Note: This is a basic implementation for demonstration
    """
    # Convert to NetworkX for community detection
    import networkx.algorithms.community as nx_comm
    
    nx_graph = nx.Graph()
    for u in graph.vertices:
        nx_graph.add_node(u)
    
    for u in graph.vertices:
        if graph.weighted:
            for v, weight in graph.adj_list[u].items():
                nx_graph.add_edge(u, v, weight=weight)
        else:
            for v in graph.adj_list[u]:
                nx_graph.add_edge(u, v)
    
    # Use NetworkX's implementation
    communities = list(nx_comm.louvain_communities(nx_graph, resolution=resolution))
    modularity = nx_comm.modularity(nx_graph, communities)
    
    return communities, modularity

## Example: Community detection
communities, modularity = louvain_community_detection(g)
print(f"\nCommunity Detection:")
print(f"Number of communities: {len(communities)}")
print(f"Modularity: {modularity:.4f}")
for i, community in enumerate(communities):
    print(f"Community {i}: {list(community)}")
```

## Applications in Distributed Systems

### Service Dependency Analysis

Model services and their dependencies as a directed acyclic graph (DAG) to analyze:
- **Critical Path**: Longest path determining system latency
- **Single Points of Failure**: Articulation points in the dependency graph
- **Cascading Failures**: Impact analysis using network flow

```python
def analyze_service_dependencies(dependencies):
    """
    Analyze service dependency graph for distributed systems
    
    dependencies: list of (service, depends_on) tuples
    """
    # Build dependency graph
    dep_graph = Graph(directed=True)
    
    for service, dependency in dependencies:
        dep_graph.add_edge(dependency, service)
    
    # Convert to NetworkX for analysis
    nx_graph = nx.DiGraph()
    for u in dep_graph.vertices:
        nx_graph.add_node(u)
    
    for u in dep_graph.vertices:
        for v in dep_graph.adj_list[u]:
            nx_graph.add_edge(u, v)
    
    # Analysis
    try:
        # Check if DAG
        is_dag = nx.is_directed_acyclic_graph(nx_graph)
        
        # Topological sort (deployment order)
        topo_order = list(nx.topological_sort(nx_graph)) if is_dag else []
        
        # Find articulation points (critical services)
        undirected = nx_graph.to_undirected()
        articulation_points = list(nx.articulation_points(undirected))
        
        # Compute centrality measures
        in_degree_cent = nx.in_degree_centrality(nx_graph)
        out_degree_cent = nx.out_degree_centrality(nx_graph)
        betweenness_cent = nx.betweenness_centrality(nx_graph)
        
        return {
            'is_dag': is_dag,
            'topological_order': topo_order,
            'critical_services': articulation_points,
            'in_degree_centrality': in_degree_cent,
            'out_degree_centrality': out_degree_cent,
            'betweenness_centrality': betweenness_cent
        }
    
    except nx.NetworkXError as e:
        return {'error': str(e)}

## Example: Service dependency analysis
service_deps = [
    ('web-server', 'load-balancer'),
    ('web-server', 'database'),
    ('api-gateway', 'auth-service'),
    ('web-server', 'api-gateway'),
    ('database', 'storage'),
    ('auth-service', 'user-db'),
    ('monitoring', 'database'),
    ('logging', 'storage')
]

dep_analysis = analyze_service_dependencies(service_deps)
print(f"\nService Dependency Analysis:")
print(f"Is DAG (no circular dependencies): {dep_analysis['is_dag']}")
print(f"Deployment order: {dep_analysis['topological_order']}")
print(f"Critical services: {dep_analysis['critical_services']}")

print("\nService Centrality (most depended upon):")
sorted_services = sorted(dep_analysis['in_degree_centrality'].items(), 
                        key=lambda x: x[1], reverse=True)
for service, centrality in sorted_services[:3]:
    print(f"  {service}: {centrality:.3f}")
```

### Network Routing and Load Balancing

Use shortest path algorithms for:
- **Routing Tables**: Precompute shortest paths for packet forwarding
- **Load Distribution**: Multiple shortest paths for load balancing
- **Fault Tolerance**: Alternative paths when links fail

```python
def analyze_network_routing(topology, weights=None):
    """
    Analyze network topology for routing optimization
    
    topology: list of (node1, node2) edges
    weights: optional dict of (edge) -> weight
    """
    # Build network graph
    network = Graph(directed=False, weighted=bool(weights))
    
    for u, v in topology:
        weight = weights.get((u, v), weights.get((v, u), 1)) if weights else 1
        network.add_edge(u, v, weight)
    
    # Analysis
    analysis = {}
    
    # All-pairs shortest paths
    adj_matrix, vertex_map = network.to_adjacency_matrix()
    
    # Replace zeros with infinity for non-edges
    for i in range(adj_matrix.shape[0]):
        for j in range(adj_matrix.shape[1]):
            if i != j and adj_matrix[i][j] == 0:
                adj_matrix[i][j] = float('inf')
    
    all_pairs = floyd_warshall(adj_matrix)
    
    # Network diameter (longest shortest path)
    finite_distances = all_pairs[all_pairs != float('inf')]
    diameter = np.max(finite_distances) if len(finite_distances) > 0 else float('inf')
    
    # Average path length
    n = len(network.vertices)
    total_distance = np.sum(finite_distances)
    avg_path_length = total_distance / (n * (n - 1)) if n > 1 else 0
    
    # Node connectivity (minimum node cut)
    nx_graph = nx.Graph()
    for u in network.vertices:
        nx_graph.add_node(u)
    for u in network.vertices:
        for v in (network.adj_list[u].keys() if network.weighted else network.adj_list[u]):
            nx_graph.add_edge(u, v)
    
    node_connectivity = nx.node_connectivity(nx_graph)
    edge_connectivity = nx.edge_connectivity(nx_graph)
    
    return {
        'diameter': diameter,
        'average_path_length': avg_path_length,
        'node_connectivity': node_connectivity,
        'edge_connectivity': edge_connectivity,
        'all_pairs_distances': all_pairs,
        'vertex_mapping': vertex_map
    }

## Example: Network routing analysis
network_topology = [
    ('Router1', 'Router2'), ('Router1', 'Router3'),
    ('Router2', 'Router4'), ('Router3', 'Router4'),
    ('Router2', 'Router5'), ('Router4', 'Router6'),
    ('Router5', 'Router6')
]

## Link weights (latencies in ms)
link_weights = {
    ('Router1', 'Router2'): 10,
    ('Router1', 'Router3'): 15,
    ('Router2', 'Router4'): 20,
    ('Router3', 'Router4'): 12,
    ('Router2', 'Router5'): 8,
    ('Router4', 'Router6'): 25,
    ('Router5', 'Router6'): 18
}

routing_analysis = analyze_network_routing(network_topology, link_weights)
print(f"\nNetwork Routing Analysis:")
print(f"Network diameter: {routing_analysis['diameter']:.2f} ms")
print(f"Average path length: {routing_analysis['average_path_length']:.2f} ms")
print(f"Node connectivity: {routing_analysis['node_connectivity']}")
print(f"Edge connectivity: {routing_analysis['edge_connectivity']}")
```

## Advanced Graph Algorithms

### Graph Coloring

**Chromatic Number**: Minimum colors needed to color vertices such that no adjacent vertices share the same color.

**Applications**: Register allocation, scheduling, frequency assignment.

```python
def greedy_coloring(graph):
    """
    Greedy graph coloring algorithm
    """
    colors = {}
    vertices = list(graph.vertices)
    
    # Sort vertices by degree (largest first heuristic)
    vertices.sort(key=lambda v: len(graph.adj_list[v]), reverse=True)
    
    for vertex in vertices:
        # Find available colors
        used_colors = set()
        
        neighbors = graph.adj_list[vertex].keys() if graph.weighted else graph.adj_list[vertex]
        for neighbor in neighbors:
            if neighbor in colors:
                used_colors.add(colors[neighbor])
        
        # Assign smallest available color
        color = 0
        while color in used_colors:
            color += 1
        colors[vertex] = color
    
    return colors

def chromatic_number_bound(graph):
    """
    Compute bounds on chromatic number
    """
    # Lower bound: clique number (approximated by max degree + 1)
    max_degree = max(len(graph.adj_list[v]) for v in graph.vertices) if graph.vertices else 0
    lower_bound = max_degree + 1
    
    # Upper bound: greedy coloring
    coloring = greedy_coloring(graph)
    upper_bound = max(coloring.values()) + 1 if coloring else 0
    
    return lower_bound, upper_bound, coloring

## Example: Graph coloring
coloring_bounds = chromatic_number_bound(g)
print(f"\nGraph Coloring Analysis:")
print(f"Chromatic number bounds: [{coloring_bounds[0]}, {coloring_bounds[1]}]")
print(f"Greedy coloring:")
for vertex, color in coloring_bounds[2].items():
    print(f"  {vertex}: Color {color}")
```

### Matching Algorithms

**Maximum Bipartite Matching**: Find maximum matching in bipartite graphs.

**Applications**: Task assignment, resource allocation, network flows.

```python
def maximum_bipartite_matching(left_vertices, right_vertices, edges):
    """
    Maximum bipartite matching using Ford-Fulkerson
    """
    # Create flow network
    # Source -> left vertices (capacity 1)
    # Left vertices -> right vertices (capacity 1 if edge exists)
    # Right vertices -> sink (capacity 1)
    
    flow_graph = Graph(directed=True, weighted=True)
    
    source = 'SOURCE'
    sink = 'SINK'
    
    # Add source edges
    for left in left_vertices:
        flow_graph.add_edge(source, left, 1)
    
    # Add bipartite edges
    for left, right in edges:
        flow_graph.add_edge(left, right, 1)
    
    # Add sink edges
    for right in right_vertices:
        flow_graph.add_edge(right, sink, 1)
    
    # Find maximum flow
    max_flow = ford_fulkerson(flow_graph, source, sink)
    
    return max_flow

## Example: Bipartite matching
left = ['Worker1', 'Worker2', 'Worker3']
right = ['Task1', 'Task2', 'Task3', 'Task4']
bipartite_edges = [
    ('Worker1', 'Task1'), ('Worker1', 'Task2'),
    ('Worker2', 'Task2'), ('Worker2', 'Task3'),
    ('Worker3', 'Task1'), ('Worker3', 'Task4')
]

max_matching = maximum_bipartite_matching(left, right, bipartite_edges)
print(f"\nMaximum Bipartite Matching:")
print(f"Maximum matching size: {max_matching}")
```

## Performance Analysis and Complexity

### Algorithm Complexity Summary

| Algorithm | Time Complexity | Space Complexity | Use Case |
|-----------|----------------|------------------|----------|
| DFS/BFS | $O(\|V\| + \|E\|)$ | $O(\|V\|)$ | Graph traversal |
| Dijkstra | $O((\|V\| + \|E\|) \log \|V\|)$ | $O(\|V\|)$ | Single-source shortest path |
| Bellman-Ford | $O(\|V\|\|E\|)$ | $O(\|V\|)$ | Negative weights, cycle detection |
| Floyd-Warshall | $O(\|V\|^3)$ | $O(\|V\|^2)$ | All-pairs shortest paths |
| Kruskal MST | $O(\|E\| \log \|E\|)$ | $O(\|V\|)$ | Minimum spanning tree |
| Prim MST | $O(\|E\| \log \|V\|)$ | $O(\|V\|)$ | Minimum spanning tree |
| Ford-Fulkerson | $O(\|E\| f^*)$ | $O(\|V\|^2)$ | Maximum flow |

where $f^*$ is the maximum flow value.

### Graph Properties and Thresholds

**Random Graph Model $G(n,p)$**: Graph with $n$ vertices where each edge exists with probability $p$.

**Phase Transitions**:
- **Connectivity**: $p = \frac{\ln n}{n}$
- **Giant Component**: $p = \frac{1}{n}$
- **Perfect Matching**: $p = \frac{\ln n}{n}$

**Small World Property**: Most real networks have diameter $O(\log n)$.

**Scale-Free Networks**: Degree distribution follows power law $P(k) \propto k^{-\gamma}$.

## Interactive Visualization and Tools

### Graph Visualization

```javascript
class GraphVisualizer {
    constructor(canvas, graph) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.graph = graph;
        this.positions = {};
        this.selectedVertex = null;
        
        this.initializePositions();
        this.setupInteraction();
    }
    
    initializePositions() {
        / Simple circular layout
        const vertices = Object.keys(this.graph);
        const n = vertices.length;
        const radius = Math.min(this.canvas.width, this.canvas.height) / 3;
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        vertices.forEach((vertex, i) => {
            const angle = (2 * Math.PI * i) / n;
            this.positions[vertex] = {
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle)
            };
        });
    }
    
    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        / Draw edges
        this.ctx.strokeStyle = '#ccc';
        this.ctx.lineWidth = 2;
        
        for (const [vertex, neighbors] of Object.entries(this.graph)) {
            const pos1 = this.positions[vertex];
            
            for (const neighbor of neighbors) {
                const pos2 = this.positions[neighbor];
                
                this.ctx.beginPath();
                this.ctx.moveTo(pos1.x, pos1.y);
                this.ctx.lineTo(pos2.x, pos2.y);
                this.ctx.stroke();
            }
        }
        
        / Draw vertices
        for (const [vertex, pos] of Object.entries(this.positions)) {
            this.ctx.beginPath();
            this.ctx.arc(pos.x, pos.y, 20, 0, 2 * Math.PI);
            this.ctx.fillStyle = this.selectedVertex === vertex ? '#ff6b6b' : '#4ecdc4';
            this.ctx.fill();
            this.ctx.strokeStyle = '#333';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            / Draw label
            this.ctx.fillStyle = '#333';
            this.ctx.font = '14px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(vertex, pos.x, pos.y + 5);
        }
    }
    
    setupInteraction() {
        this.canvas.addEventListener('click', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            / Find clicked vertex
            for (const [vertex, pos] of Object.entries(this.positions)) {
                const distance = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2);
                if (distance <= 20) {
                    this.selectedVertex = this.selectedVertex === vertex ? null : vertex;
                    this.highlightShortestPaths();
                    break;
                }
            }
        });
    }
    
    highlightShortestPaths() {
        if (!this.selectedVertex) {
            this.draw();
            return;
        }
        
        / Simple BFS for shortest paths visualization
        const distances = this.bfs(this.selectedVertex);
        
        this.draw();
        
        / Draw distance labels
        this.ctx.fillStyle = '#ff6b6b';
        this.ctx.font = '12px Arial';
        
        for (const [vertex, distance] of Object.entries(distances)) {
            if (vertex !== this.selectedVertex && distance !== Infinity) {
                const pos = this.positions[vertex];
                this.ctx.fillText(`d=${distance}`, pos.x, pos.y - 30);
            }
        }
    }
    
    bfs(start) {
        const distances = {};
        const queue = [start];
        
        for (const vertex of Object.keys(this.graph)) {
            distances[vertex] = Infinity;
        }
        distances[start] = 0;
        
        while (queue.length > 0) {
            const current = queue.shift();
            
            for (const neighbor of this.graph[current]) {
                if (distances[neighbor] === Infinity) {
                    distances[neighbor] = distances[current] + 1;
                    queue.push(neighbor);
                }
            }
        }
        
        return distances;
    }
}

/ Example usage
const exampleGraph = {
    'A': ['B', 'C'],
    'B': ['A', 'C', 'D'],
    'C': ['A', 'B', 'E'],
    'D': ['B', 'E'],
    'E': ['C', 'D']
};

/ Initialize visualizer when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('graphCanvas');
    if (canvas) {
        const visualizer = new GraphVisualizer(canvas, exampleGraph);
        visualizer.draw();
    }
});
```

## Research Frontiers and Modern Applications

### Graph Neural Networks

**Message Passing**: $h_v^{(l+1)} = \text{UPDATE}^{(l)}(h_v^{(l)}, \text{AGGREGATE}^{(l)}(\{h_u^{(l)} : u \in N(v)\}))$

**Applications**: Node classification, link prediction, graph-level tasks.

### Dynamic Graphs

**Temporal Networks**: Graphs that change over time $G(t) = (V(t), E(t))$.

**Streaming Algorithms**: Process graph updates in real-time with limited memory.

### Quantum Graph Algorithms

**Quantum Walks**: Quantum analog of classical random walks.

**Speedup**: Potential exponential speedup for certain graph problems.

## References and Further Reading

### Foundational Texts
1. Bondy, J.A. & Murty, U.S.R. "Graph Theory" (2008)
2. West, D.B. "Introduction to Graph Theory" (2017)
3. Diestel, R. "Graph Theory" (2017)

### Algorithms and Complexity
4. Cormen, T.H. et al. "Introduction to Algorithms" (2022) - Graph algorithms chapters
5. Kleinberg, J. & Tardos, E. "Algorithm Design" (2014)

### Spectral Graph Theory
6. Chung, F.R.K. "Spectral Graph Theory" (1997)
7. Spielman, D.A. "Spectral and Algebraic Graph Theory" (2019)

### Network Analysis
8. Newman, M.E.J. "Networks: An Introduction" (2018)
9. Barabási, A.L. "Network Science" (2016)

### Applications in Computer Science
10. Skiena, S.S. "The Algorithm Design Manual" (2020)
11. Roughgarden, T. "Algorithms Illuminated" (2019-2020) - 4 volume series

## Related Topics

- [Network Theory](network-theory.md) - Complex network analysis and models
- [Markov Chains](markov-chains.md) - Random walks on graphs
- [Information Theory](information-theory.md) - Network coding and information flow
- [Social Networks](social-networks.md) - Social network analysis and community detection
- [Spatial Stats](spatial-stats.md) - Geometric graphs and spatial networks
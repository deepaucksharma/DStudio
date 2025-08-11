# Episode 3: Graph Theory for Network Topology

## Episode Metadata
- **Duration**: 2.5 hours
- **Pillar**: Theoretical Foundations (1)
- **Prerequisites**: Episode 1 (Probability Theory), Episode 2 (Queueing Theory), Linear algebra, Discrete mathematics
- **Learning Objectives**: 
  - [ ] Master graph algorithms for distributed system topology analysis
  - [ ] Apply spectral graph theory to network partitioning and load balancing
  - [ ] Implement network flow algorithms for capacity planning and fault tolerance
  - [ ] Design robust network topologies using graph-theoretic principles
  - [ ] Analyze service dependency graphs for reliability engineering

## Content Structure

### Part 1: Mathematical Foundations (45 minutes)

#### 1.1 Theoretical Background (15 min)

Graph theory provides the mathematical foundation for understanding network topology, service dependencies, and data flow in distributed systems. When Google designs their global network connecting data centers across continents, or when Netflix plans content distribution networks serving 200+ million subscribers, they rely on graph-theoretic principles to optimize performance, ensure reliability, and minimize costs.

In distributed systems, graphs model fundamental relationships:
- **Network Topology**: Physical and logical connections between nodes
- **Service Dependencies**: How microservices depend on each other
- **Data Flow**: Movement of information through system components
- **Communication Patterns**: Message passing between distributed processes
- **Failure Propagation**: How errors cascade through interconnected systems

**Core Graph Concepts in Systems Context:**

**Vertices (Nodes)**: Represent system components
- Servers, containers, processes, data centers
- Microservices, databases, message queues
- Users, devices, network switches

**Edges (Links)**: Represent relationships or connections
- Network links, API calls, data pipelines
- Dependencies, communication channels
- Trust relationships, routing paths

**Graph Properties Critical for Systems:**

1. **Connectivity**: Can any node reach any other node?
2. **Diameter**: Maximum distance between any two nodes
3. **Centrality**: Which nodes are most important?
4. **Clustering**: How tightly connected are local neighborhoods?
5. **Cut Sets**: Which edges, if removed, disconnect the graph?

**Directed vs. Undirected Graphs:**

- **Undirected**: Network cables, peer-to-peer connections
- **Directed**: API calls, data pipelines, dependency chains

**Weighted Graphs:**

Edge weights represent costs, capacities, or qualities:
- Network latency, bandwidth capacity
- Service response times, failure probabilities
- Load balancing weights, trust scores

**Mathematical Representations:**

**Adjacency Matrix A**: 
For graph G with n vertices:
- A[i][j] = 1 if edge exists from vertex i to j
- A[i][j] = weight of edge for weighted graphs
- Symmetric for undirected graphs: A = A^T

**Properties of Powers of A**:
- (A^k)[i][j] = number of k-length paths from vertex i to j
- Critical for analyzing multi-hop reachability

**Adjacency List**: 
More memory-efficient for sparse graphs (|E| << |V|^2)
- Each vertex maintains list of neighbors
- Space complexity: O(|V| + |E|)

**Laplacian Matrix L = D - A**:
- D = diagonal degree matrix
- L encodes graph structure for spectral analysis
- Eigenvalues reveal connectivity properties

#### 1.2 Network Topology Analysis (20 min)

Understanding network structure is crucial for designing efficient distributed systems. Different topologies have distinct performance characteristics and failure modes.

**Common Network Topologies:**

**Star Topology**:
- Central hub connected to all other nodes
- Advantages: Simple routing, low diameter (2)
- Disadvantages: Single point of failure, hub becomes bottleneck

**Ring Topology**:
- Nodes connected in circular chain
- Advantages: Predictable performance, fault tolerance
- Disadvantages: High diameter (n/2), limited bandwidth

**Mesh Topology**:
- Every node connected to every other node
- Advantages: Maximum fault tolerance, multiple paths
- Disadvantages: High cost (O(n^2) connections), complex routing

**Tree Topology**:
- Hierarchical structure with root and leaves
- Advantages: Scalable, reflects organizational structure
- Disadvantages: Single points of failure, bottlenecks near root

**Small World Networks**:
- High clustering with short average path lengths
- Common in social networks and some distributed systems
- Combine local efficiency with global reachability

```python
import numpy as np
import networkx as nx
from scipy import sparse, linalg
from typing import Dict, List, Tuple, Set, Optional, Union
import matplotlib.pyplot as plt
import heapq
from collections import defaultdict, deque
from dataclasses import dataclass
import itertools

@dataclass
class NetworkMetrics:
    """Comprehensive network topology metrics"""
    diameter: int
    average_path_length: float
    clustering_coefficient: float
    node_connectivity: int
    edge_connectivity: int
    algebraic_connectivity: float
    vertex_count: int
    edge_count: int
    density: float

class NetworkTopologyAnalyzer:
    """
    Comprehensive analysis of network topologies for distributed systems.
    Focuses on reliability, performance, and scalability characteristics.
    """
    
    def __init__(self, graph: nx.Graph = None):
        self.graph = graph if graph is not None else nx.Graph()
    
    def add_node(self, node_id: str, **attributes):
        """Add node with optional attributes (capacity, type, etc.)"""
        self.graph.add_node(node_id, **attributes)
    
    def add_edge(self, u: str, v: str, weight: float = 1.0, **attributes):
        """Add weighted edge with optional attributes"""
        self.graph.add_edge(u, v, weight=weight, **attributes)
    
    def create_topology(self, topology_type: str, n: int, **kwargs) -> nx.Graph:
        """Create standard network topologies"""
        
        if topology_type == "star":
            self.graph = nx.star_graph(n)
        elif topology_type == "ring":
            self.graph = nx.cycle_graph(n)
        elif topology_type == "complete":
            self.graph = nx.complete_graph(n)
        elif topology_type == "tree":
            # Balanced k-ary tree
            k = kwargs.get('k', 2)  # binary tree by default
            self.graph = nx.balanced_tree(k, kwargs.get('height', 3))
        elif topology_type == "grid":
            m = kwargs.get('m', int(np.sqrt(n)))
            n_grid = kwargs.get('n', n // m)
            self.graph = nx.grid_2d_graph(m, n_grid)
        elif topology_type == "small_world":
            # Watts-Strogatz small world
            k = kwargs.get('k', 4)
            p = kwargs.get('p', 0.3)
            self.graph = nx.watts_strogatz_graph(n, k, p)
        elif topology_type == "scale_free":
            # Barabási-Albert preferential attachment
            m = kwargs.get('m', 2)
            self.graph = nx.barabasi_albert_graph(n, m)
        elif topology_type == "random":
            p = kwargs.get('p', 0.1)
            self.graph = nx.erdos_renyi_graph(n, p)
        else:
            raise ValueError(f"Unknown topology type: {topology_type}")
        
        return self.graph
    
    def analyze_topology(self) -> NetworkMetrics:
        """Comprehensive topology analysis"""
        
        if not self.graph:
            raise ValueError("No graph to analyze")
        
        # Basic properties
        n_vertices = self.graph.number_of_nodes()
        n_edges = self.graph.number_of_edges()
        density = nx.density(self.graph)
        
        # Connectivity properties
        if nx.is_connected(self.graph):
            diameter = nx.diameter(self.graph)
            avg_path_length = nx.average_shortest_path_length(self.graph)
        else:
            # Handle disconnected graphs
            components = list(nx.connected_components(self.graph))
            largest_component = max(components, key=len)
            subgraph = self.graph.subgraph(largest_component)
            diameter = nx.diameter(subgraph)
            avg_path_length = nx.average_shortest_path_length(subgraph)
        
        # Clustering
        clustering_coeff = nx.average_clustering(self.graph)
        
        # Connectivity measures
        node_connectivity = nx.node_connectivity(self.graph)
        edge_connectivity = nx.edge_connectivity(self.graph)
        
        # Spectral properties
        algebraic_connectivity = self._compute_algebraic_connectivity()
        
        return NetworkMetrics(
            diameter=diameter,
            average_path_length=avg_path_length,
            clustering_coefficient=clustering_coeff,
            node_connectivity=node_connectivity,
            edge_connectivity=edge_connectivity,
            algebraic_connectivity=algebraic_connectivity,
            vertex_count=n_vertices,
            edge_count=n_edges,
            density=density
        )
    
    def _compute_algebraic_connectivity(self) -> float:
        """Compute algebraic connectivity (second smallest Laplacian eigenvalue)"""
        if not nx.is_connected(self.graph):
            return 0.0
        
        # Get Laplacian matrix
        L = nx.laplacian_matrix(self.graph, dtype=float)
        
        # Compute eigenvalues
        eigenvals = linalg.eigvals(L.toarray())
        eigenvals = np.sort(np.real(eigenvals))
        
        # Second smallest eigenvalue (algebraic connectivity)
        return eigenvals[1] if len(eigenvals) > 1 else 0.0
    
    def find_critical_nodes(self, method: str = "betweenness") -> Dict[str, float]:
        """Find nodes critical for network connectivity"""
        
        if method == "betweenness":
            return nx.betweenness_centrality(self.graph)
        elif method == "closeness":
            return nx.closeness_centrality(self.graph)
        elif method == "degree":
            return nx.degree_centrality(self.graph)
        elif method == "eigenvector":
            try:
                return nx.eigenvector_centrality(self.graph)
            except nx.PowerIterationFailedConvergence:
                # Fallback for disconnected graphs
                return nx.eigenvector_centrality(self.graph, max_iter=1000)
        elif method == "pagerank":
            return nx.pagerank(self.graph)
        else:
            raise ValueError(f"Unknown centrality method: {method}")
    
    def analyze_fault_tolerance(self) -> Dict:
        """Analyze network fault tolerance characteristics"""
        
        results = {
            'node_fault_tolerance': {},
            'edge_fault_tolerance': {},
            'cascade_analysis': {}
        }
        
        # Node fault tolerance
        original_connectivity = nx.node_connectivity(self.graph)
        node_removal_impact = {}
        
        for node in self.graph.nodes():
            temp_graph = self.graph.copy()
            temp_graph.remove_node(node)
            
            if nx.is_connected(temp_graph):
                new_connectivity = nx.node_connectivity(temp_graph)
                impact = original_connectivity - new_connectivity
            else:
                impact = float('inf')  # Network becomes disconnected
            
            node_removal_impact[node] = impact
        
        results['node_fault_tolerance'] = node_removal_impact
        
        # Edge fault tolerance
        original_edge_connectivity = nx.edge_connectivity(self.graph)
        edge_removal_impact = {}
        
        for edge in self.graph.edges():
            temp_graph = self.graph.copy()
            temp_graph.remove_edge(*edge)
            
            if nx.is_connected(temp_graph):
                new_connectivity = nx.edge_connectivity(temp_graph)
                impact = original_edge_connectivity - new_connectivity
            else:
                impact = float('inf')
            
            edge_removal_impact[edge] = impact
        
        results['edge_fault_tolerance'] = edge_removal_impact
        
        # Cascade failure analysis
        cascade_results = self._analyze_cascade_failures()
        results['cascade_analysis'] = cascade_results
        
        return results
    
    def _analyze_cascade_failures(self, failure_threshold: float = 0.5) -> Dict:
        """Analyze cascade failure patterns"""
        
        cascade_results = {}
        
        # Try removing nodes in order of centrality
        centrality = self.find_critical_nodes("betweenness")
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        temp_graph = self.graph.copy()
        removed_nodes = []
        
        for node, _ in sorted_nodes:
            temp_graph.remove_node(node)
            removed_nodes.append(node)
            
            # Check connectivity
            if not nx.is_connected(temp_graph):
                cascade_results['cascade_trigger'] = len(removed_nodes)
                cascade_results['trigger_nodes'] = removed_nodes.copy()
                break
            
            # Check if remaining nodes are overloaded
            remaining_nodes = list(temp_graph.nodes())
            if len(remaining_nodes) < failure_threshold * len(self.graph.nodes()):
                cascade_results['overload_trigger'] = len(removed_nodes)
                break
        
        return cascade_results
    
    def optimize_for_reliability(self, budget: int) -> List[Tuple[str, str]]:
        """Suggest edge additions to improve network reliability"""
        
        # Find node pairs with longest shortest paths
        path_lengths = dict(nx.all_pairs_shortest_path_length(self.graph))
        
        # Create list of potential edges to add
        potential_edges = []
        for u in self.graph.nodes():
            for v in self.graph.nodes():
                if u != v and not self.graph.has_edge(u, v):
                    path_length = path_lengths[u].get(v, float('inf'))
                    if path_length != float('inf'):
                        potential_edges.append((u, v, path_length))
        
        # Sort by longest paths (biggest improvement potential)
        potential_edges.sort(key=lambda x: x[2], reverse=True)
        
        # Return top budget edges
        return [(u, v) for u, v, _ in potential_edges[:budget]]
    
    def visualize_topology(self, layout: str = "spring", 
                         highlight_critical: bool = True,
                         save_path: str = None):
        """Visualize network topology with optional critical node highlighting"""
        
        plt.figure(figsize=(12, 8))
        
        # Choose layout
        if layout == "spring":
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
        elif layout == "circular":
            pos = nx.circular_layout(self.graph)
        elif layout == "random":
            pos = nx.random_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, alpha=0.6, color='gray')
        
        # Draw nodes
        if highlight_critical:
            # Color nodes by centrality
            centrality = self.find_critical_nodes("betweenness")
            node_colors = [centrality.get(node, 0) for node in self.graph.nodes()]
            node_sizes = [300 + 1000 * centrality.get(node, 0) for node in self.graph.nodes()]
            
            nodes = nx.draw_networkx_nodes(self.graph, pos, 
                                         node_color=node_colors,
                                         node_size=node_sizes,
                                         cmap=plt.cm.Reds,
                                         alpha=0.8)
            plt.colorbar(nodes, label='Betweenness Centrality')
        else:
            nx.draw_networkx_nodes(self.graph, pos, node_size=300, alpha=0.8)
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, font_size=8)
        
        plt.title("Network Topology Analysis")
        plt.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()

def compare_network_topologies():
    """Compare different network topologies for distributed systems"""
    
    print("NETWORK TOPOLOGY COMPARISON FOR DISTRIBUTED SYSTEMS")
    print("=" * 70)
    
    # Define topologies to compare
    topologies = [
        ("Star", "star", {"n": 20}),
        ("Ring", "ring", {"n": 20}), 
        ("Complete", "complete", {"n": 20}),
        ("Tree", "tree", {"n": 20, "k": 3, "height": 3}),
        ("Small World", "small_world", {"n": 20, "k": 4, "p": 0.3}),
        ("Scale Free", "scale_free", {"n": 20, "m": 2}),
        ("Random", "random", {"n": 20, "p": 0.2})
    ]
    
    results = []
    
    for name, topo_type, params in topologies:
        analyzer = NetworkTopologyAnalyzer()
        analyzer.create_topology(topo_type, **params)
        
        try:
            metrics = analyzer.analyze_topology()
            fault_tolerance = analyzer.analyze_fault_tolerance()
            
            # Find most critical node
            critical_nodes = analyzer.find_critical_nodes("betweenness")
            most_critical = max(critical_nodes.items(), key=lambda x: x[1])
            
            results.append({
                'topology': name,
                'metrics': metrics,
                'most_critical_node': most_critical[0],
                'critical_impact': fault_tolerance['node_fault_tolerance'][most_critical[0]]
            })
            
        except Exception as e:
            print(f"Error analyzing {name}: {e}")
            continue
    
    # Print comparison table
    print("Topology Comparison:")
    print("-" * 70)
    print("Topology     | Nodes | Edges | Diameter | Avg Path | Clustering | Connectivity")
    print("-------------|-------|-------|----------|----------|------------|-------------")
    
    for result in results:
        m = result['metrics']
        print(f"{result['topology']:<12} | {m.vertex_count:4d}  | {m.edge_count:4d}  | "
              f"{m.diameter:7d}  | {m.average_path_length:7.2f}  | "
              f"{m.clustering_coefficient:9.3f}  | {m.node_connectivity:10d}")
    
    print(f"\nFault Tolerance Analysis:")
    print("-" * 40)
    print("Topology     | Most Critical Node | Impact Score")
    print("-------------|--------------------|--------------")
    
    for result in results:
        impact = result['critical_impact']
        impact_str = "∞" if impact == float('inf') else f"{impact:.1f}"
        print(f"{result['topology']:<12} | {result['most_critical_node']:<18} | {impact_str:>12s}")
    
    # Recommendations
    print(f"\nRECOMMENDATIONS FOR DISTRIBUTED SYSTEMS:")
    print("-" * 50)
    print("🌟 Small World: Best balance of performance and fault tolerance")
    print("⚡ Complete: Maximum fault tolerance, but expensive (O(n²) edges)")  
    print("💰 Tree: Cost-effective, but vulnerable to root failures")
    print("🔄 Ring: Predictable performance, moderate fault tolerance")
    print("⚠️  Star: Avoid for critical systems - single point of failure")
    
    # Visualize selected topologies
    selected_topologies = ["small_world", "tree", "complete"]
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for i, (topo_name, topo_type) in enumerate(zip(["Small World", "Tree", "Complete"], selected_topologies)):
        analyzer = NetworkTopologyAnalyzer()
        if topo_type == "small_world":
            analyzer.create_topology(topo_type, n=15, k=4, p=0.3)
        elif topo_type == "tree":
            analyzer.create_topology(topo_type, n=15, k=2, height=4)
        else:
            analyzer.create_topology(topo_type, n=15)
        
        # Get layout
        pos = nx.spring_layout(analyzer.graph, k=1, iterations=50)
        
        # Plot on subplot
        plt.sca(axes[i])
        
        # Find critical nodes
        centrality = analyzer.find_critical_nodes("betweenness")
        node_colors = [centrality.get(node, 0) for node in analyzer.graph.nodes()]
        node_sizes = [200 + 500 * centrality.get(node, 0) for node in analyzer.graph.nodes()]
        
        nx.draw_networkx_edges(analyzer.graph, pos, alpha=0.5, color='gray')
        nx.draw_networkx_nodes(analyzer.graph, pos, 
                             node_color=node_colors, 
                             node_size=node_sizes,
                             cmap=plt.cm.Reds, 
                             alpha=0.8)
        nx.draw_networkx_labels(analyzer.graph, pos, font_size=8)
        
        axes[i].set_title(f"{topo_name} Network")
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.show()

compare_network_topologies()
```

#### 1.3 Spectral Graph Theory (10 min)

Spectral graph theory analyzes graphs through the eigenvalues and eigenvectors of associated matrices. This powerful technique reveals hidden structural properties crucial for distributed systems.

**Graph Laplacian Matrix:**

L = D - A

where:
- D = diagonal degree matrix (D[i,i] = degree of vertex i)
- A = adjacency matrix

**Key Properties of Laplacian:**

1. **Positive Semi-definite**: All eigenvalues ≥ 0
2. **Smallest Eigenvalue**: Always 0 (with eigenvector of all 1s)
3. **Algebraic Connectivity**: Second smallest eigenvalue (λ₂)
4. **Number of Components**: Multiplicity of eigenvalue 0

**Algebraic Connectivity (Fiedler Value):**

λ₂ measures how well-connected a graph is:
- λ₂ = 0: Graph is disconnected
- Larger λ₂: Better connectivity
- Related to edge expansion and bottleneck identification

**Applications in Distributed Systems:**

1. **Network Partitioning**: Fiedler vector indicates natural cut points
2. **Load Balancing**: Spectral partitioning distributes load evenly
3. **Failure Analysis**: Low algebraic connectivity indicates fragile networks
4. **Consensus Convergence**: Convergence rate proportional to λ₂

```python
from sklearn.cluster import KMeans
import numpy as np
from scipy import linalg
import matplotlib.pyplot as plt

class SpectralGraphAnalyzer:
    """
    Spectral analysis of graphs for distributed system applications
    """
    
    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.laplacian_matrix = None
        self.eigenvalues = None
        self.eigenvectors = None
    
    def compute_laplacian(self, normalized: bool = True):
        """Compute graph Laplacian matrix"""
        
        if normalized:
            # Normalized Laplacian: L_norm = D^(-1/2) * L * D^(-1/2)
            self.laplacian_matrix = nx.normalized_laplacian_matrix(
                self.graph, dtype=float
            )
        else:
            # Standard Laplacian: L = D - A
            self.laplacian_matrix = nx.laplacian_matrix(
                self.graph, dtype=float
            )
        
        return self.laplacian_matrix
    
    def compute_spectrum(self):
        """Compute eigenvalues and eigenvectors of Laplacian"""
        
        if self.laplacian_matrix is None:
            self.compute_laplacian(normalized=True)
        
        # Compute all eigenvalues and eigenvectors
        eigenvals, eigenvecs = linalg.eigh(self.laplacian_matrix.toarray())
        
        # Sort by eigenvalue (ascending)
        idx = np.argsort(eigenvals)
        self.eigenvalues = eigenvals[idx]
        self.eigenvectors = eigenvecs[:, idx]
        
        return self.eigenvalues, self.eigenvectors
    
    def algebraic_connectivity(self) -> float:
        """Compute algebraic connectivity (Fiedler value)"""
        
        if self.eigenvalues is None:
            self.compute_spectrum()
        
        # Second smallest eigenvalue
        if len(self.eigenvalues) >= 2:
            return self.eigenvalues[1]
        else:
            return 0.0
    
    def fiedler_vector(self) -> np.ndarray:
        """Get Fiedler vector (eigenvector of second smallest eigenvalue)"""
        
        if self.eigenvectors is None:
            self.compute_spectrum()
        
        if self.eigenvectors.shape[1] >= 2:
            return self.eigenvectors[:, 1]
        else:
            return np.zeros(len(self.graph.nodes()))
    
    def spectral_partition(self, k: int = 2) -> Dict[int, List]:
        """Partition graph using spectral clustering"""
        
        # Use first k eigenvectors (excluding the constant one)
        if self.eigenvectors is None:
            self.compute_spectrum()
        
        # Features matrix: first k non-trivial eigenvectors
        features = self.eigenvectors[:, 1:k+1]
        
        # K-means clustering on eigenvector space
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(features)
        
        # Group nodes by cluster
        clusters = defaultdict(list)
        node_list = list(self.graph.nodes())
        
        for i, label in enumerate(cluster_labels):
            clusters[label].append(node_list[i])
        
        return dict(clusters)
    
    def cheeger_constant(self) -> float:
        """Estimate Cheeger constant (isoperimetric number)"""
        
        # Cheeger constant h(G) ≈ λ₂/2 (for regular graphs)
        # Measures expansion properties
        
        algebraic_conn = self.algebraic_connectivity()
        
        # For non-regular graphs, this is an approximation
        return algebraic_conn / 2
    
    def consensus_convergence_rate(self) -> float:
        """Estimate convergence rate for consensus algorithms"""
        
        # Convergence rate ≈ 1 - λ₂
        # Closer to 1 = faster convergence
        
        algebraic_conn = self.algebraic_connectivity()
        return 1 - algebraic_conn
    
    def identify_bottlenecks(self) -> List[Tuple]:
        """Identify network bottlenecks using Fiedler vector"""
        
        fiedler = self.fiedler_vector()
        node_list = list(self.graph.nodes())
        
        # Nodes where Fiedler vector changes sign are potential bottlenecks
        bottlenecks = []
        
        # Find edges crossing zero in Fiedler vector
        for edge in self.graph.edges():
            u_idx = node_list.index(edge[0])
            v_idx = node_list.index(edge[1])
            
            u_val = fiedler[u_idx]
            v_val = fiedler[v_idx]
            
            # Check if signs are different (crossing zero)
            if (u_val > 0 and v_val < 0) or (u_val < 0 and v_val > 0):
                bottlenecks.append(edge)
        
        return bottlenecks
    
    def visualize_spectral_properties(self):
        """Visualize spectral properties of the graph"""
        
        if self.eigenvalues is None:
            self.compute_spectrum()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Eigenvalue spectrum
        ax1.plot(range(len(self.eigenvalues)), self.eigenvalues, 'o-', linewidth=2, markersize=8)
        ax1.set_xlabel('Eigenvalue Index')
        ax1.set_ylabel('Eigenvalue')
        ax1.set_title('Laplacian Eigenvalue Spectrum')
        ax1.grid(True, alpha=0.3)
        
        # Highlight algebraic connectivity
        if len(self.eigenvalues) >= 2:
            ax1.axhline(y=self.eigenvalues[1], color='red', linestyle='--', 
                       label=f'Algebraic Connectivity: {self.eigenvalues[1]:.4f}')
            ax1.legend()
        
        # 2. Fiedler vector visualization
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        fiedler = self.fiedler_vector()
        
        # Color nodes by Fiedler vector value
        node_colors = fiedler
        nx.draw_networkx_edges(self.graph, pos, ax=ax2, alpha=0.5, color='gray')
        nodes = nx.draw_networkx_nodes(self.graph, pos, ax=ax2,
                                     node_color=node_colors,
                                     cmap=plt.cm.RdBu,
                                     node_size=300)
        nx.draw_networkx_labels(self.graph, pos, ax=ax2, font_size=8)
        ax2.set_title('Fiedler Vector (Natural Partition)')
        ax2.axis('off')
        
        # 3. Spectral partition
        clusters = self.spectral_partition(k=3)
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        
        for cluster_id, nodes_in_cluster in clusters.items():
            color = colors[cluster_id % len(colors)]
            nx.draw_networkx_nodes(self.graph, pos, ax=ax3,
                                 nodelist=nodes_in_cluster,
                                 node_color=color,
                                 node_size=300,
                                 alpha=0.8)
        
        nx.draw_networkx_edges(self.graph, pos, ax=ax3, alpha=0.5, color='gray')
        nx.draw_networkx_labels(self.graph, pos, ax=ax3, font_size=8)
        ax3.set_title('Spectral Clustering (3 clusters)')
        ax3.axis('off')
        
        # 4. Bottleneck analysis
        bottlenecks = self.identify_bottlenecks()
        
        # Draw normal edges
        normal_edges = [edge for edge in self.graph.edges() if edge not in bottlenecks]
        nx.draw_networkx_edges(self.graph, pos, ax=ax4,
                             edgelist=normal_edges,
                             alpha=0.3, color='gray')
        
        # Highlight bottleneck edges
        if bottlenecks:
            nx.draw_networkx_edges(self.graph, pos, ax=ax4,
                                 edgelist=bottlenecks,
                                 edge_color='red',
                                 width=3,
                                 alpha=0.8)
        
        nx.draw_networkx_nodes(self.graph, pos, ax=ax4, node_size=300, alpha=0.8)
        nx.draw_networkx_labels(self.graph, pos, ax=ax4, font_size=8)
        ax4.set_title(f'Network Bottlenecks ({len(bottlenecks)} edges)')
        ax4.axis('off')
        
        plt.tight_layout()
        plt.show()
    
    def generate_connectivity_report(self) -> Dict:
        """Generate comprehensive connectivity analysis report"""
        
        algebraic_conn = self.algebraic_connectivity()
        cheeger_const = self.cheeger_constant()
        convergence_rate = self.consensus_convergence_rate()
        bottlenecks = self.identify_bottlenecks()
        partitions = self.spectral_partition(k=2)
        
        return {
            'algebraic_connectivity': algebraic_conn,
            'cheeger_constant': cheeger_const,
            'consensus_convergence_rate': convergence_rate,
            'bottleneck_edges': bottlenecks,
            'natural_partition_sizes': [len(nodes) for nodes in partitions.values()],
            'connectivity_assessment': self._assess_connectivity(algebraic_conn),
            'recommendations': self._generate_recommendations(algebraic_conn, bottlenecks)
        }
    
    def _assess_connectivity(self, algebraic_conn: float) -> str:
        """Assess network connectivity quality"""
        
        if algebraic_conn == 0:
            return "DISCONNECTED"
        elif algebraic_conn < 0.1:
            return "POOR - Very fragile connectivity"
        elif algebraic_conn < 0.3:
            return "FAIR - Moderate connectivity"
        elif algebraic_conn < 0.5:
            return "GOOD - Well connected"
        else:
            return "EXCELLENT - Highly connected"
    
    def _generate_recommendations(self, algebraic_conn: float, bottlenecks: List) -> List[str]:
        """Generate recommendations for network improvement"""
        
        recommendations = []
        
        if algebraic_conn < 0.2:
            recommendations.append("Add redundant connections to improve fault tolerance")
        
        if len(bottlenecks) > len(self.graph.edges()) * 0.1:
            recommendations.append("Too many bottleneck edges - consider topology redesign")
        
        if algebraic_conn > 0.8:
            recommendations.append("Network is over-connected - consider cost optimization")
        
        recommendations.append("Monitor bottleneck edges for failure prevention")
        
        return recommendations

def analyze_datacenter_network_spectrum():
    """Analyze spectral properties of a data center network"""
    
    print("SPECTRAL ANALYSIS: DATA CENTER NETWORK")
    print("=" * 50)
    
    # Create a data center-like topology (fat tree)
    # Simplified 2-level fat tree: core switches -> aggregation -> servers
    
    analyzer = NetworkTopologyAnalyzer()
    
    # Build fat tree topology
    graph = nx.Graph()
    
    # Core switches
    core_switches = ['core1', 'core2', 'core3', 'core4']
    
    # Aggregation switches (per pod)
    agg_switches = []
    for pod in range(2):
        for agg in range(2):
            agg_switches.append(f'agg{pod}_{agg}')
    
    # Top of Rack (ToR) switches
    tor_switches = []
    for pod in range(2):
        for tor in range(4):
            tor_switches.append(f'tor{pod}_{tor}')
    
    # Servers
    servers = []
    for pod in range(2):
        for tor in range(4):
            for server in range(8):
                servers.append(f'server{pod}_{tor}_{server}')
    
    # Add all nodes
    all_nodes = core_switches + agg_switches + tor_switches + servers
    graph.add_nodes_from(all_nodes)
    
    # Connect core to aggregation (full mesh)
    for core in core_switches:
        for agg in agg_switches:
            graph.add_edge(core, agg)
    
    # Connect aggregation to ToR within pods
    for pod in range(2):
        agg_in_pod = [f'agg{pod}_0', f'agg{pod}_1']
        tor_in_pod = [f'tor{pod}_{i}' for i in range(4)]
        
        for agg in agg_in_pod:
            for tor in tor_in_pod:
                graph.add_edge(agg, tor)
    
    # Connect ToR to servers
    for pod in range(2):
        for tor_idx in range(4):
            tor_name = f'tor{pod}_{tor_idx}'
            servers_under_tor = [f'server{pod}_{tor_idx}_{i}' for i in range(8)]
            
            for server in servers_under_tor:
                graph.add_edge(tor_name, server)
    
    # Analyze with spectral methods
    spectral_analyzer = SpectralGraphAnalyzer(graph)
    report = spectral_analyzer.generate_connectivity_report()
    
    print(f"Network Properties:")
    print(f"  Nodes: {len(graph.nodes())}")
    print(f"  Edges: {len(graph.edges())}")
    print(f"  Algebraic Connectivity: {report['algebraic_connectivity']:.6f}")
    print(f"  Cheeger Constant: {report['cheeger_constant']:.6f}")
    print(f"  Consensus Convergence Rate: {report['consensus_convergence_rate']:.6f}")
    print(f"  Connectivity Assessment: {report['connectivity_assessment']}")
    
    print(f"\nBottleneck Analysis:")
    print(f"  Bottleneck Edges: {len(report['bottleneck_edges'])}")
    if report['bottleneck_edges']:
        print("  Critical Connections:")
        for i, edge in enumerate(report['bottleneck_edges'][:5]):  # Show first 5
            print(f"    {edge[0]} ↔ {edge[1]}")
    
    print(f"\nNatural Partitioning:")
    print(f"  Partition Sizes: {report['natural_partition_sizes']}")
    
    print(f"\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    # Visualize (subset for clarity)
    # Create a smaller representative graph for visualization
    small_graph = nx.Graph()
    
    # Add representative nodes from each layer
    repr_nodes = core_switches + agg_switches[:2] + tor_switches[:4] + servers[:8]
    small_graph.add_nodes_from(repr_nodes)
    
    # Add representative edges
    for edge in graph.edges():
        if edge[0] in repr_nodes and edge[1] in repr_nodes:
            small_graph.add_edge(edge[0], edge[1])
    
    small_analyzer = SpectralGraphAnalyzer(small_graph)
    small_analyzer.visualize_spectral_properties()

analyze_datacenter_network_spectrum()
```

### Part 2: Implementation Details (60 minutes)

#### 2.1 Network Flow Algorithms (25 min)

Network flow algorithms solve optimization problems on graphs where edges have capacity constraints. These algorithms are fundamental for capacity planning, load balancing, and fault tolerance analysis in distributed systems.

**Maximum Flow Problem:**

Given a flow network G = (V, E) with:
- Source node s and sink node t
- Capacity function c(u,v) for each edge (u,v)
- Find maximum flow from s to t

**Ford-Fulkerson Algorithm:**

1. Initialize flow f(u,v) = 0 for all edges
2. While there exists an augmenting path from s to t:
   - Find path P with available capacity
   - Determine bottleneck capacity b along P
   - Augment flow along P by b
3. Return maximum flow value

**Max-Flow Min-Cut Theorem:**

The value of maximum flow equals the capacity of minimum cut.

**Applications in Distributed Systems:**

1. **Network Capacity Planning**: Determine maximum throughput
2. **Load Balancing**: Distribute traffic optimally
3. **Fault Tolerance**: Identify critical links and backup paths
4. **Resource Allocation**: Assign resources to maximize utilization

```python
from collections import defaultdict, deque
import sys
from typing import Dict, List, Tuple, Set, Optional
import heapq

class NetworkFlowSolver:
    """
    Comprehensive network flow algorithms for distributed system optimization
    """
    
    def __init__(self):
        self.graph = defaultdict(dict)  # graph[u][v] = capacity
        self.flow = defaultdict(dict)   # flow[u][v] = current flow
    
    def add_edge(self, u: str, v: str, capacity: float, bidirectional: bool = False):
        """Add edge with capacity"""
        self.graph[u][v] = capacity
        self.flow[u][v] = 0
        
        # Add reverse edge with 0 capacity (for residual graph)
        if v not in self.graph or u not in self.graph[v]:
            self.graph[v][u] = 0
            self.flow[v][u] = 0
        
        if bidirectional:
            self.graph[v][u] = capacity
    
    def get_residual_capacity(self, u: str, v: str) -> float:
        """Get residual capacity of edge (u,v)"""
        forward_residual = self.graph[u].get(v, 0) - self.flow[u].get(v, 0)
        return max(0, forward_residual)
    
    def bfs_find_path(self, source: str, sink: str) -> List[str]:
        """Find augmenting path using BFS"""
        
        visited = set()
        parent = {}
        queue = deque([source])
        visited.add(source)
        
        while queue:
            current = queue.popleft()
            
            if current == sink:
                # Reconstruct path
                path = []
                node = sink
                while node != source:
                    path.append(node)
                    node = parent[node]
                path.append(source)
                path.reverse()
                return path
            
            # Explore neighbors with available capacity
            for neighbor in self.graph[current]:
                if neighbor not in visited and self.get_residual_capacity(current, neighbor) > 0:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
        
        return []  # No path found
    
    def ford_fulkerson(self, source: str, sink: str) -> float:
        """Ford-Fulkerson algorithm for maximum flow"""
        
        max_flow_value = 0
        
        while True:
            # Find augmenting path
            path = self.bfs_find_path(source, sink)
            if not path:
                break
            
            # Find bottleneck capacity along path
            path_capacity = float('inf')
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                path_capacity = min(path_capacity, self.get_residual_capacity(u, v))
            
            # Augment flow along path
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                self.flow[u][v] += path_capacity
                self.flow[v][u] -= path_capacity
            
            max_flow_value += path_capacity
        
        return max_flow_value
    
    def find_min_cut(self, source: str, sink: str) -> Tuple[Set[str], Set[str], float]:
        """Find minimum cut after computing maximum flow"""
        
        # Find reachable nodes from source in residual graph
        reachable = set()
        queue = deque([source])
        reachable.add(source)
        
        while queue:
            current = queue.popleft()
            
            for neighbor in self.graph[current]:
                if neighbor not in reachable and self.get_residual_capacity(current, neighbor) > 0:
                    reachable.add(neighbor)
                    queue.append(neighbor)
        
        # Min cut separates reachable from non-reachable
        all_nodes = set(self.graph.keys())
        s_side = reachable
        t_side = all_nodes - reachable
        
        # Calculate cut capacity
        cut_capacity = 0
        for u in s_side:
            for v in t_side:
                if v in self.graph[u]:
                    cut_capacity += self.graph[u][v]
        
        return s_side, t_side, cut_capacity
    
    def multi_commodity_flow(self, commodities: List[Dict]) -> Dict:
        """
        Solve multi-commodity flow problem using linear programming approach.
        Simplified implementation for demonstration.
        
        commodities: List of {source, sink, demand}
        """
        
        # This is a simplified heuristic approach
        # Real implementation would use linear programming
        
        results = {}
        remaining_capacity = {}
        
        # Initialize remaining capacities
        for u in self.graph:
            remaining_capacity[u] = {}
            for v in self.graph[u]:
                remaining_capacity[u][v] = self.graph[u][v]
        
        # Process commodities in order of demand (largest first)
        sorted_commodities = sorted(commodities, key=lambda x: x['demand'], reverse=True)
        
        for i, commodity in enumerate(sorted_commodities):
            source = commodity['source']
            sink = commodity['sink']
            demand = commodity['demand']
            
            # Create temporary flow solver with remaining capacities
            temp_solver = NetworkFlowSolver()
            for u in remaining_capacity:
                for v in remaining_capacity[u]:
                    if remaining_capacity[u][v] > 0:
                        temp_solver.add_edge(u, v, remaining_capacity[u][v])
            
            # Find maximum flow for this commodity
            flow_value = temp_solver.ford_fulkerson(source, sink)
            allocated_flow = min(flow_value, demand)
            
            results[f'commodity_{i}'] = {
                'source': source,
                'sink': sink,
                'demand': demand,
                'allocated': allocated_flow,
                'satisfaction_ratio': allocated_flow / demand if demand > 0 else 1.0
            }
            
            # Update remaining capacities (simplified)
            if allocated_flow > 0:
                path = temp_solver.bfs_find_path(source, sink)
                if path:
                    # Approximate capacity reduction along path
                    for j in range(len(path) - 1):
                        u, v = path[j], path[j + 1]
                        if v in remaining_capacity[u]:
                            reduction = allocated_flow / len(path)  # Simplified
                            remaining_capacity[u][v] = max(0, remaining_capacity[u][v] - reduction)
        
        return results

class DistributedSystemCapacityPlanner:
    """
    Use network flow algorithms for distributed system capacity planning
    """
    
    def __init__(self):
        self.flow_solver = NetworkFlowSolver()
        self.nodes = set()
        self.node_types = {}  # node -> type (datacenter, region, service, etc.)
    
    def add_datacenter(self, dc_id: str, capacity: float):
        """Add data center with processing capacity"""
        self.nodes.add(dc_id)
        self.node_types[dc_id] = 'datacenter'
        # Connect to virtual sink with capacity
        self.flow_solver.add_edge(dc_id, 'sink', capacity)
    
    def add_traffic_source(self, source_id: str, demand: float):
        """Add traffic source with demand"""
        self.nodes.add(source_id)
        self.node_types[source_id] = 'traffic_source'
        # Connect from virtual source with demand
        self.flow_solver.add_edge('source', source_id, demand)
    
    def add_network_link(self, u: str, v: str, bandwidth: float, latency: float = 0):
        """Add network link with bandwidth capacity"""
        self.flow_solver.add_edge(u, v, bandwidth, bidirectional=True)
    
    def plan_capacity(self) -> Dict:
        """Plan system capacity using max flow"""
        
        max_throughput = self.flow_solver.ford_fulkerson('source', 'sink')
        
        # Find bottlenecks (min cut)
        s_side, t_side, cut_capacity = self.flow_solver.find_min_cut('source', 'sink')
        
        # Analyze bottleneck links
        bottleneck_links = []
        for u in s_side:
            for v in t_side:
                if v in self.flow_solver.graph[u] and self.flow_solver.graph[u][v] > 0:
                    utilization = self.flow_solver.flow[u].get(v, 0) / self.flow_solver.graph[u][v]
                    bottleneck_links.append({
                        'link': (u, v),
                        'capacity': self.flow_solver.graph[u][v],
                        'flow': self.flow_solver.flow[u].get(v, 0),
                        'utilization': utilization
                    })
        
        return {
            'max_throughput': max_throughput,
            'cut_capacity': cut_capacity,
            'bottleneck_links': bottleneck_links,
            's_side_nodes': list(s_side),
            't_side_nodes': list(t_side)
        }
    
    def analyze_fault_tolerance(self, failure_scenarios: List[str]) -> Dict:
        """Analyze system capacity under various failure scenarios"""
        
        baseline = self.plan_capacity()
        scenario_results = {}
        
        for scenario_name in failure_scenarios:
            # Create copy of flow solver
            temp_solver = NetworkFlowSolver()
            
            # Copy all edges except failed ones
            for u in self.flow_solver.graph:
                for v in self.flow_solver.graph[u]:
                    capacity = self.flow_solver.graph[u][v]
                    
                    # Simulate failures based on scenario
                    if self._should_fail_link(scenario_name, u, v):
                        capacity = 0  # Link failed
                    
                    temp_solver.add_edge(u, v, capacity)
            
            # Compute max flow under failure
            max_flow_with_failure = temp_solver.ford_fulkerson('source', 'sink')
            
            scenario_results[scenario_name] = {
                'max_throughput': max_flow_with_failure,
                'degradation': baseline['max_throughput'] - max_flow_with_failure,
                'remaining_capacity_ratio': max_flow_with_failure / baseline['max_throughput'] if baseline['max_throughput'] > 0 else 0
            }
        
        return scenario_results
    
    def _should_fail_link(self, scenario: str, u: str, v: str) -> bool:
        """Determine if link should fail in given scenario"""
        
        if scenario == "datacenter_failure":
            # Fail all links to/from first datacenter
            dc_nodes = [node for node, node_type in self.node_types.items() 
                       if node_type == 'datacenter']
            if dc_nodes:
                failed_dc = dc_nodes[0]
                return u == failed_dc or v == failed_dc
        
        elif scenario == "network_partition":
            # Fail links between different regions (simplified)
            return u.startswith('us-') and v.startswith('eu-')
        
        elif scenario == "random_link_failure":
            # Fail random 10% of links
            import random
            return random.random() < 0.1
        
        return False
    
    def recommend_improvements(self, analysis_results: Dict) -> List[str]:
        """Generate recommendations for capacity improvements"""
        
        recommendations = []
        
        # Identify heavily utilized links
        for link_info in analysis_results['bottleneck_links']:
            if link_info['utilization'] > 0.8:
                u, v = link_info['link']
                recommendations.append(
                    f"Upgrade link {u} -> {v}: {link_info['utilization']:.1%} utilized"
                )
        
        # Check fault tolerance
        if len(analysis_results['bottleneck_links']) == 1:
            recommendations.append("Single bottleneck detected - add redundant paths")
        
        return recommendations

def analyze_cdn_capacity_planning():
    """Analyze CDN capacity planning using network flow algorithms"""
    
    print("CDN CAPACITY PLANNING WITH NETWORK FLOW")
    print("=" * 60)
    
    # Create capacity planner
    planner = DistributedSystemCapacityPlanner()
    
    # Add data centers with processing capacity
    datacenters = {
        'us-east': 1000,    # 1000 Gbps processing capacity
        'us-west': 800,
        'eu-central': 600,
        'asia-pacific': 400
    }
    
    for dc, capacity in datacenters.items():
        planner.add_datacenter(dc, capacity)
    
    # Add traffic sources (regional demand)
    traffic_sources = {
        'us-traffic': 700,    # 700 Gbps demand
        'eu-traffic': 400,
        'asia-traffic': 300
    }
    
    for source, demand in traffic_sources.items():
        planner.add_traffic_source(source, demand)
    
    # Add network links between traffic sources and data centers
    # Bandwidth represents network capacity, not geographical optimality
    network_links = [
        # US traffic can go to any DC, but closer is better (higher capacity)
        ('us-traffic', 'us-east', 800),
        ('us-traffic', 'us-west', 600),
        ('us-traffic', 'eu-central', 200),
        ('us-traffic', 'asia-pacific', 100),
        
        # EU traffic routing
        ('eu-traffic', 'eu-central', 500),
        ('eu-traffic', 'us-east', 300),
        ('eu-traffic', 'us-west', 200),
        ('eu-traffic', 'asia-pacific', 100),
        
        # Asia traffic routing
        ('asia-traffic', 'asia-pacific', 400),
        ('asia-traffic', 'us-west', 300),
        ('asia-traffic', 'us-east', 200),
        ('asia-traffic', 'eu-central', 150)
    ]
    
    for source, dc, bandwidth in network_links:
        planner.add_network_link(source, dc, bandwidth)
    
    # Plan baseline capacity
    baseline_analysis = planner.plan_capacity()
    
    print("BASELINE CAPACITY ANALYSIS")
    print("-" * 40)
    print(f"Maximum Throughput: {baseline_analysis['max_throughput']:.0f} Gbps")
    print(f"Cut Capacity: {baseline_analysis['cut_capacity']:.0f} Gbps")
    
    print(f"\nBottleneck Links:")
    for link_info in baseline_analysis['bottleneck_links']:
        u, v = link_info['link']
        print(f"  {u} -> {v}: {link_info['flow']:.0f}/{link_info['capacity']:.0f} Gbps "
              f"({link_info['utilization']:.1%} utilized)")
    
    # Analyze fault tolerance
    failure_scenarios = ['datacenter_failure', 'network_partition']
    fault_analysis = planner.analyze_fault_tolerance(failure_scenarios)
    
    print(f"\nFAULT TOLERANCE ANALYSIS")
    print("-" * 40)
    
    for scenario, results in fault_analysis.items():
        degradation_pct = (results['degradation'] / baseline_analysis['max_throughput'] * 100
                          if baseline_analysis['max_throughput'] > 0 else 0)
        
        print(f"{scenario}:")
        print(f"  Remaining Capacity: {results['max_throughput']:.0f} Gbps "
              f"({results['remaining_capacity_ratio']:.1%} of baseline)")
        print(f"  Capacity Loss: {results['degradation']:.0f} Gbps ({degradation_pct:.1f}%)")
    
    # Generate recommendations
    recommendations = planner.recommend_improvements(baseline_analysis)
    
    print(f"\nRECOMMENDATIONS")
    print("-" * 20)
    for rec in recommendations:
        print(f"• {rec}")
    
    # Additional insights
    total_demand = sum(traffic_sources.values())
    total_supply = sum(datacenters.values())
    
    print(f"\nSYSTEM INSIGHTS")
    print("-" * 20)
    print(f"Total Demand: {total_demand} Gbps")
    print(f"Total Supply: {total_supply} Gbps")
    print(f"Supply-Demand Ratio: {total_supply/total_demand:.2f}x")
    
    if baseline_analysis['max_throughput'] < total_demand:
        shortfall = total_demand - baseline_analysis['max_throughput']
        print(f"⚠️  Capacity Shortfall: {shortfall:.0f} Gbps")
        print(f"💡 Consider adding network capacity or data center resources")
    else:
        excess = baseline_analysis['max_throughput'] - total_demand
        print(f"✅ Excess Capacity: {excess:.0f} Gbps")

analyze_cdn_capacity_planning()
```

#### 2.2 Service Dependency Graph Analysis (20 min)

Modern distributed systems consist of hundreds of interconnected services. Understanding these dependencies is crucial for:

1. **Reliability Engineering**: Predicting failure propagation
2. **Capacity Planning**: Understanding load distribution
3. **Deployment Planning**: Safe rollout strategies
4. **Incident Response**: Rapid root cause analysis

**Dependency Graph Properties:**

- **Directed Acyclic Graph (DAG)**: No circular dependencies (ideally)
- **Weighted Edges**: Dependency strength, failure probability
- **Node Attributes**: Service criticality, SLA requirements

```python
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque
import random

class ServiceType(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend" 
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    EXTERNAL = "external"

class DependencyType(Enum):
    SYNCHRONOUS = "sync"     # Direct API calls
    ASYNCHRONOUS = "async"   # Message queues
    DATA = "data"           # Data dependencies
    INFRASTRUCTURE = "infra" # Shared infrastructure

@dataclass
class ServiceNode:
    """Represents a service in the dependency graph"""
    service_id: str
    service_type: ServiceType
    criticality: int = 1  # 1=critical, 2=important, 3=nice-to-have
    sla_target: float = 0.99  # Availability target
    failure_rate: float = 0.01  # Annual failure rate
    recovery_time: float = 15  # Minutes to recover
    owner_team: str = "unknown"
    version: str = "1.0"
    
    def __hash__(self):
        return hash(self.service_id)

@dataclass
class DependencyEdge:
    """Represents a dependency between services"""
    source: str
    target: str
    dependency_type: DependencyType
    strength: float = 1.0  # 0.0 to 1.0, how critical this dependency is
    failure_impact: float = 1.0  # How much target failure affects source
    latency_ms: float = 10.0
    timeout_ms: float = 5000.0
    retry_count: int = 3

class ServiceDependencyAnalyzer:
    """
    Analyze service dependency graphs for distributed system reliability
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceNode] = {}
        self.dependencies: List[DependencyEdge] = []
        self.graph = nx.DiGraph()
    
    def add_service(self, service: ServiceNode):
        """Add a service to the dependency graph"""
        self.services[service.service_id] = service
        self.graph.add_node(service.service_id, **{
            'type': service.service_type.value,
            'criticality': service.criticality,
            'sla_target': service.sla_target,
            'failure_rate': service.failure_rate,
            'recovery_time': service.recovery_time
        })
    
    def add_dependency(self, dependency: DependencyEdge):
        """Add a dependency between services"""
        if dependency.source not in self.services:
            raise ValueError(f"Source service {dependency.source} not found")
        if dependency.target not in self.services:
            raise ValueError(f"Target service {dependency.target} not found")
        
        self.dependencies.append(dependency)
        self.graph.add_edge(dependency.source, dependency.target, **{
            'type': dependency.dependency_type.value,
            'strength': dependency.strength,
            'failure_impact': dependency.failure_impact,
            'latency_ms': dependency.latency_ms,
            'timeout_ms': dependency.timeout_ms
        })
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies (cycles) in the service graph"""
        try:
            # If DAG, this will succeed
            nx.topological_sort(self.graph)
            return []
        except nx.NetworkXError:
            # Graph has cycles, find them
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
    
    def calculate_service_criticality(self) -> Dict[str, float]:
        """Calculate overall criticality score for each service"""
        
        # Base criticality from service definition
        base_criticality = {service_id: 1.0 / service.criticality 
                          for service_id, service in self.services.items()}
        
        # Add impact based on dependent services
        impact_scores = {}
        
        for service_id in self.services:
            # Services that depend on this service
            dependents = list(self.graph.predecessors(service_id))
            
            # Weight by dependency strength and dependent criticality
            total_impact = 0.0
            for dependent in dependents:
                edge_data = self.graph[dependent][service_id]
                strength = edge_data.get('strength', 1.0)
                failure_impact = edge_data.get('failure_impact', 1.0)
                dependent_criticality = base_criticality.get(dependent, 0.5)
                
                total_impact += strength * failure_impact * dependent_criticality
            
            impact_scores[service_id] = total_impact
        
        # Combine base criticality with impact
        combined_scores = {}
        max_impact = max(impact_scores.values()) if impact_scores.values() else 1.0
        
        for service_id in self.services:
            base = base_criticality[service_id]
            impact = impact_scores[service_id] / max_impact if max_impact > 0 else 0
            combined_scores[service_id] = base + impact
        
        return combined_scores
    
    def analyze_failure_propagation(self, failed_service: str, 
                                  simulation_steps: int = 10) -> Dict:
        """Simulate failure propagation through the service graph"""
        
        if failed_service not in self.services:
            raise ValueError(f"Service {failed_service} not found")
        
        # Track failure states over time
        failure_states = [{failed_service}]  # Initially only one service failed
        failure_probabilities = {service_id: 0.0 for service_id in self.services}
        failure_probabilities[failed_service] = 1.0
        
        for step in range(simulation_steps):
            current_failed = failure_states[-1].copy()
            new_failures = set()
            
            # Check each service that might be affected
            for service_id in self.services:
                if service_id in current_failed:
                    continue
                
                # Check dependencies on failed services
                dependencies_on_failed = []
                for dependency in self.dependencies:
                    if (dependency.source == service_id and 
                        dependency.target in current_failed):
                        dependencies_on_failed.append(dependency)
                
                if dependencies_on_failed:
                    # Calculate failure probability based on dependencies
                    failure_prob = 0.0
                    
                    for dep in dependencies_on_failed:
                        # Probability this dependency causes failure
                        dep_failure_prob = (dep.failure_impact * dep.strength * 
                                          failure_probabilities.get(dep.target, 0))
                        failure_prob += dep_failure_prob * (1 - failure_prob)
                    
                    failure_probabilities[service_id] = max(
                        failure_probabilities[service_id], failure_prob
                    )
                    
                    # Determine if service fails this step (probabilistic)
                    if failure_prob > 0.5:  # Threshold for failure
                        new_failures.add(service_id)
            
            # Update failure state
            next_state = current_failed.union(new_failures)
            failure_states.append(next_state)
            
            # Stop if no new failures
            if not new_failures:
                break
        
        return {
            'initial_failure': failed_service,
            'final_failed_services': list(failure_states[-1]),
            'failure_progression': [list(state) for state in failure_states],
            'failure_probabilities': failure_probabilities,
            'total_affected_services': len(failure_states[-1]),
            'cascade_depth': len(failure_states) - 1
        }
    
    def find_critical_paths(self) -> List[List[str]]:
        """Find critical paths through the service dependency graph"""
        
        # Find services with no dependencies (entry points)
        entry_services = [service_id for service_id in self.services
                         if self.graph.in_degree(service_id) == 0]
        
        # Find services with no dependents (endpoints)
        endpoint_services = [service_id for service_id in self.services
                           if self.graph.out_degree(service_id) == 0]
        
        critical_paths = []
        
        for entry in entry_services:
            for endpoint in endpoint_services:
                try:
                    # Find all simple paths
                    paths = list(nx.all_simple_paths(self.graph, entry, endpoint))
                    critical_paths.extend(paths)
                except nx.NetworkXNoPath:
                    continue
        
        # Sort by path length and criticality
        def path_criticality(path):
            total_criticality = sum(1.0 / self.services[service].criticality 
                                  for service in path)
            return (len(path), total_criticality)
        
        critical_paths.sort(key=path_criticality, reverse=True)
        
        return critical_paths[:10]  # Return top 10 critical paths
    
    def generate_deployment_order(self) -> List[str]:
        """Generate safe deployment order based on dependencies"""
        
        try:
            # Topological sort gives dependency-safe order
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXError:
            # Handle cycles by breaking them temporarily
            graph_copy = self.graph.copy()
            
            # Remove edges to break cycles
            cycles = list(nx.simple_cycles(self.graph))
            for cycle in cycles:
                if len(cycle) >= 2:
                    graph_copy.remove_edge(cycle[-1], cycle[0])
            
            return list(nx.topological_sort(graph_copy))
    
    def analyze_service_isolation(self) -> Dict[str, Dict]:
        """Analyze how well services are isolated from failures"""
        
        isolation_scores = {}
        
        for service_id in self.services:
            # Count direct dependencies
            direct_deps = list(self.graph.successors(service_id))
            
            # Count transitive dependencies
            transitive_deps = set()
            for dep in direct_deps:
                transitive_deps.update(nx.descendants(self.graph, dep))
            
            # Calculate isolation score
            total_services = len(self.services) - 1  # Exclude self
            dependency_ratio = len(transitive_deps) / total_services if total_services > 0 else 0
            isolation_score = 1.0 - dependency_ratio
            
            # Analyze dependency types
            sync_deps = []
            async_deps = []
            
            for dep_edge in self.dependencies:
                if dep_edge.source == service_id:
                    if dep_edge.dependency_type == DependencyType.SYNCHRONOUS:
                        sync_deps.append(dep_edge.target)
                    elif dep_edge.dependency_type == DependencyType.ASYNCHRONOUS:
                        async_deps.append(dep_edge.target)
            
            isolation_scores[service_id] = {
                'isolation_score': isolation_score,
                'direct_dependencies': len(direct_deps),
                'transitive_dependencies': len(transitive_deps),
                'synchronous_dependencies': len(sync_deps),
                'asynchronous_dependencies': len(async_deps),
                'isolation_assessment': self._assess_isolation(isolation_score, len(sync_deps))
            }
        
        return isolation_scores
    
    def _assess_isolation(self, score: float, sync_deps: int) -> str:
        """Assess service isolation quality"""
        
        if score > 0.8 and sync_deps <= 2:
            return "EXCELLENT - Well isolated"
        elif score > 0.6 and sync_deps <= 5:
            return "GOOD - Moderate isolation"
        elif score > 0.4:
            return "FAIR - Some coupling"
        else:
            return "POOR - Highly coupled"
    
    def visualize_dependency_graph(self, highlight_critical: bool = True):
        """Visualize the service dependency graph"""
        
        plt.figure(figsize=(15, 10))
        
        # Layout
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # Color nodes by service type
        service_type_colors = {
            ServiceType.FRONTEND: 'lightblue',
            ServiceType.BACKEND: 'lightgreen', 
            ServiceType.DATABASE: 'orange',
            ServiceType.CACHE: 'yellow',
            ServiceType.QUEUE: 'purple',
            ServiceType.EXTERNAL: 'red'
        }
        
        node_colors = [service_type_colors.get(self.services[node].service_type, 'gray') 
                      for node in self.graph.nodes()]
        
        if highlight_critical:
            criticality_scores = self.calculate_service_criticality()
            node_sizes = [300 + 1000 * criticality_scores.get(node, 0) 
                         for node in self.graph.nodes()]
        else:
            node_sizes = 500
        
        # Draw edges with different styles for different dependency types
        sync_edges = [(u, v) for u, v, d in self.graph.edges(data=True) 
                     if d.get('type') == 'sync']
        async_edges = [(u, v) for u, v, d in self.graph.edges(data=True) 
                      if d.get('type') == 'async']
        
        # Draw synchronous dependencies as solid lines
        if sync_edges:
            nx.draw_networkx_edges(self.graph, pos, edgelist=sync_edges,
                                 edge_color='red', alpha=0.7, width=2,
                                 style='solid', arrows=True, arrowsize=20)
        
        # Draw asynchronous dependencies as dashed lines
        if async_edges:
            nx.draw_networkx_edges(self.graph, pos, edgelist=async_edges,
                                 edge_color='blue', alpha=0.7, width=1,
                                 style='dashed', arrows=True, arrowsize=15)
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors,
                             node_size=node_sizes, alpha=0.8)
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, font_size=8, font_weight='bold')
        
        plt.title("Service Dependency Graph")
        plt.axis('off')
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], color='red', lw=2, label='Synchronous'),
            plt.Line2D([0], [0], color='blue', lw=2, linestyle='--', label='Asynchronous')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.show()
    
    def export_analysis_report(self, filename: str):
        """Export comprehensive analysis report"""
        
        report = {
            'services': {sid: {
                'type': service.service_type.value,
                'criticality': service.criticality,
                'sla_target': service.sla_target,
                'failure_rate': service.failure_rate,
                'recovery_time': service.recovery_time,
                'owner_team': service.owner_team
            } for sid, service in self.services.items()},
            
            'dependencies': [{
                'source': dep.source,
                'target': dep.target,
                'type': dep.dependency_type.value,
                'strength': dep.strength,
                'failure_impact': dep.failure_impact
            } for dep in self.dependencies],
            
            'analysis': {
                'circular_dependencies': self.detect_circular_dependencies(),
                'service_criticality': self.calculate_service_criticality(),
                'critical_paths': self.find_critical_paths(),
                'deployment_order': self.generate_deployment_order(),
                'isolation_analysis': self.analyze_service_isolation()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

def analyze_ecommerce_microservices():
    """Analyze dependency graph of an e-commerce microservices system"""
    
    print("SERVICE DEPENDENCY ANALYSIS: E-COMMERCE MICROSERVICES")
    print("=" * 70)
    
    analyzer = ServiceDependencyAnalyzer()
    
    # Define services
    services = [
        ServiceNode("web-frontend", ServiceType.FRONTEND, criticality=1, sla_target=0.999),
        ServiceNode("api-gateway", ServiceType.BACKEND, criticality=1, sla_target=0.999),
        ServiceNode("user-service", ServiceType.BACKEND, criticality=1, sla_target=0.99),
        ServiceNode("product-service", ServiceType.BACKEND, criticality=1, sla_target=0.99),
        ServiceNode("order-service", ServiceType.BACKEND, criticality=1, sla_target=0.995),
        ServiceNode("payment-service", ServiceType.BACKEND, criticality=1, sla_target=0.999),
        ServiceNode("inventory-service", ServiceType.BACKEND, criticality=2, sla_target=0.99),
        ServiceNode("notification-service", ServiceType.BACKEND, criticality=3, sla_target=0.95),
        ServiceNode("user-db", ServiceType.DATABASE, criticality=1, sla_target=0.999),
        ServiceNode("product-db", ServiceType.DATABASE, criticality=1, sla_target=0.99),
        ServiceNode("order-db", ServiceType.DATABASE, criticality=1, sla_target=0.995),
        ServiceNode("redis-cache", ServiceType.CACHE, criticality=2, sla_target=0.99),
        ServiceNode("message-queue", ServiceType.QUEUE, criticality=2, sla_target=0.99),
        ServiceNode("payment-gateway", ServiceType.EXTERNAL, criticality=1, sla_target=0.995),
        ServiceNode("email-service", ServiceType.EXTERNAL, criticality=3, sla_target=0.95)
    ]
    
    for service in services:
        analyzer.add_service(service)
    
    # Define dependencies
    dependencies = [
        # Frontend dependencies
        DependencyEdge("web-frontend", "api-gateway", DependencyType.SYNCHRONOUS, strength=1.0, failure_impact=1.0),
        
        # API Gateway dependencies
        DependencyEdge("api-gateway", "user-service", DependencyType.SYNCHRONOUS, strength=0.8, failure_impact=0.7),
        DependencyEdge("api-gateway", "product-service", DependencyType.SYNCHRONOUS, strength=1.0, failure_impact=0.8),
        DependencyEdge("api-gateway", "order-service", DependencyType.SYNCHRONOUS, strength=1.0, failure_impact=1.0),
        
        # Service to database dependencies
        DependencyEdge("user-service", "user-db", DependencyType.SYNCHRONOUS, strength=1.0, failure_impact=1.0),
        DependencyEdge("product-service", "product-db", DependencyType.SYNCHRONOUS, strength=1.0, failure_impact=1.0),
        DependencyEdge("order-service", "order-db", DependencyType.SYNCHRONOUS, strength=1.0, failure_impact=1.0),
        
        # Cache dependencies (non-critical)
        DependencyEdge("user-service", "redis-cache", DependencyType.SYNCHRONOUS, strength=0.5, failure_impact=0.2),
        DependencyEdge("product-service", "redis-cache", DependencyType.SYNCHRONOUS, strength=0.7, failure_impact=0.3),
        
        # Order service dependencies
        DependencyEdge("order-service", "payment-service", DependencyType.SYNCHRONOUS, strength=1.0, failure_impact=1.0),
        DependencyEdge("order-service", "inventory-service", DependencyType.SYNCHRONOUS, strength=0.8, failure_impact=0.6),
        DependencyEdge("order-service", "user-service", DependencyType.SYNCHRONOUS, strength=0.6, failure_impact=0.4),
        
        # Payment service dependencies
        DependencyEdge("payment-service", "payment-gateway", DependencyType.SYNCHRONOUS, strength=1.0, failure_impact=1.0),
        
        # Async notification dependencies
        DependencyEdge("order-service", "message-queue", DependencyType.ASYNCHRONOUS, strength=0.3, failure_impact=0.1),
        DependencyEdge("payment-service", "message-queue", DependencyType.ASYNCHRONOUS, strength=0.3, failure_impact=0.1),
        DependencyEdge("notification-service", "message-queue", DependencyType.ASYNCHRONOUS, strength=0.8, failure_impact=0.8),
        DependencyEdge("notification-service", "email-service", DependencyType.SYNCHRONOUS, strength=1.0, failure_impact=0.9),
    ]
    
    for dependency in dependencies:
        analyzer.add_dependency(dependency)
    
    # Perform analysis
    print("DEPENDENCY GRAPH ANALYSIS")
    print("-" * 40)
    
    # Check for circular dependencies
    cycles = analyzer.detect_circular_dependencies()
    print(f"Circular Dependencies: {len(cycles)}")
    if cycles:
        for i, cycle in enumerate(cycles):
            print(f"  Cycle {i+1}: {' -> '.join(cycle + [cycle[0]])}")
    
    # Service criticality analysis
    criticality_scores = analyzer.calculate_service_criticality()
    print(f"\nSERVICE CRITICALITY RANKING")
    print("-" * 30)
    sorted_criticality = sorted(criticality_scores.items(), key=lambda x: x[1], reverse=True)
    
    for i, (service, score) in enumerate(sorted_criticality[:8]):
        print(f"{i+1:2d}. {service:<20} {score:.3f}")
    
    # Failure propagation analysis
    print(f"\nFAILURE PROPAGATION ANALYSIS")
    print("-" * 30)
    
    critical_services = ['payment-gateway', 'order-db', 'api-gateway']
    
    for service in critical_services:
        propagation = analyzer.analyze_failure_propagation(service)
        affected_count = propagation['total_affected_services']
        cascade_depth = propagation['cascade_depth']
        
        print(f"{service} failure:")
        print(f"  Affected services: {affected_count}/{len(services)} ({affected_count/len(services):.1%})")
        print(f"  Cascade depth: {cascade_depth} steps")
        
        if affected_count > 5:
            print(f"  ⚠️  High impact failure - consider isolation improvements")
    
    # Service isolation analysis
    isolation_analysis = analyzer.analyze_service_isolation()
    
    print(f"\nSERVICE ISOLATION ANALYSIS")
    print("-" * 30)
    print("Service              | Isolation | Direct Deps | Sync Deps | Assessment")
    print("---------------------|-----------|-------------|-----------|------------------")
    
    for service_id, metrics in sorted(isolation_analysis.items(), 
                                     key=lambda x: x[1]['isolation_score'], reverse=True):
        print(f"{service_id:<20} | {metrics['isolation_score']:8.2f}  | "
              f"{metrics['direct_dependencies']:9d}   | {metrics['synchronous_dependencies']:7d}   | "
              f"{metrics['isolation_assessment']}")
    
    # Critical paths
    critical_paths = analyzer.find_critical_paths()
    print(f"\nCRITICAL PATHS")
    print("-" * 20)
    
    for i, path in enumerate(critical_paths[:5]):
        path_str = ' -> '.join(path)
        print(f"{i+1}. {path_str}")
    
    # Deployment order
    deployment_order = analyzer.generate_deployment_order()
    print(f"\nSAFE DEPLOYMENT ORDER")
    print("-" * 25)
    
    for i, service in enumerate(deployment_order):
        print(f"{i+1:2d}. {service}")
    
    # Recommendations
    print(f"\nRECOMMENDATIONS")
    print("-" * 20)
    
    # Find highly coupled services
    poorly_isolated = [(service, metrics) for service, metrics in isolation_analysis.items() 
                      if metrics['isolation_score'] < 0.5]
    
    if poorly_isolated:
        print("🔗 High Coupling Issues:")
        for service, metrics in poorly_isolated:
            print(f"   - {service}: {metrics['synchronous_dependencies']} sync dependencies")
    
    # Find single points of failure
    high_impact_services = [(service, score) for service, score in sorted_criticality[:3]]
    print("⚠️  Critical Services (Single Points of Failure):")
    for service, score in high_impact_services:
        print(f"   - {service}: Criticality score {score:.3f}")
    
    print("💡 Consider circuit breakers and fallback mechanisms for critical paths")
    print("💡 Implement async patterns to reduce synchronous coupling")
    
    # Visualize the dependency graph
    analyzer.visualize_dependency_graph(highlight_critical=True)

analyze_ecommerce_microservices()
```

#### 2.3 Graph-Based Load Balancing (15 min)

Traditional load balancing distributes traffic evenly, but graph-theoretic approaches can optimize for multiple objectives: latency, capacity, fault tolerance, and cost.

**Graph-Based Load Balancing Objectives:**

1. **Minimize Maximum Load**: Distribute requests to minimize peak server utilization
2. **Minimize Average Latency**: Route requests to servers with lowest response time
3. **Maximize Fault Tolerance**: Maintain balanced load even with server failures
4. **Minimize Cost**: Route to cheapest available resources

**Algorithms:**

1. **Minimum Cost Flow**: Model as network flow with cost objectives
2. **Graph Partitioning**: Divide request space across server clusters
3. **Spectral Load Balancing**: Use eigenvalues to find optimal distributions

```python
import numpy as np
from typing import Dict, List, Tuple, Optional
import heapq
from dataclasses import dataclass
import time

@dataclass
class Server:
    """Represents a server in the load balancing system"""
    server_id: str
    capacity: float  # Requests per second
    current_load: float = 0.0
    latency_ms: float = 10.0
    cost_per_request: float = 0.001
    availability: float = 0.99
    location: str = "unknown"
    
    def utilization(self) -> float:
        return self.current_load / self.capacity if self.capacity > 0 else 0.0
    
    def available_capacity(self) -> float:
        return max(0, self.capacity - self.current_load)

@dataclass
class Request:
    """Represents an incoming request"""
    request_id: str
    arrival_time: float
    priority: int = 1  # 1=high, 2=medium, 3=low
    user_location: str = "unknown"
    estimated_processing_time: float = 0.1
    
class GraphLoadBalancer:
    """
    Graph-theoretic load balancing with multiple optimization objectives
    """
    
    def __init__(self):
        self.servers: Dict[str, Server] = {}
        self.request_history: List[Request] = []
        self.routing_decisions: List[Dict] = []
        self.graph = nx.Graph()
        
    def add_server(self, server: Server):
        """Add server to the load balancing pool"""
        self.servers[server.server_id] = server
        self.graph.add_node(server.server_id, **{
            'capacity': server.capacity,
            'latency': server.latency_ms,
            'cost': server.cost_per_request,
            'location': server.location
        })
    
    def add_server_connection(self, server1: str, server2: str, bandwidth: float):
        """Add connection between servers (for federated load balancing)"""
        if server1 in self.servers and server2 in self.servers:
            self.graph.add_edge(server1, server2, bandwidth=bandwidth)
    
    def route_request(self, request: Request, 
                     algorithm: str = "weighted_round_robin") -> str:
        """Route request to optimal server using specified algorithm"""
        
        if not self.servers:
            raise ValueError("No servers available")
        
        # Filter available servers
        available_servers = [server for server in self.servers.values() 
                           if server.available_capacity() > 0]
        
        if not available_servers:
            # Overload scenario - route to least loaded server
            available_servers = list(self.servers.values())
        
        if algorithm == "round_robin":
            selected_server = self._round_robin_selection(available_servers)
        elif algorithm == "weighted_round_robin":
            selected_server = self._weighted_round_robin(available_servers)
        elif algorithm == "least_connections":
            selected_server = self._least_connections(available_servers)
        elif algorithm == "least_response_time":
            selected_server = self._least_response_time(available_servers)
        elif algorithm == "power_of_two_choices":
            selected_server = self._power_of_two_choices(available_servers)
        elif algorithm == "graph_based_optimal":
            selected_server = self._graph_based_optimal(request, available_servers)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        # Update server load
        selected_server.current_load += request.estimated_processing_time * 10  # Convert to RPS
        
        # Record routing decision
        self.routing_decisions.append({
            'request_id': request.request_id,
            'server_id': selected_server.server_id,
            'algorithm': algorithm,
            'server_utilization': selected_server.utilization(),
            'timestamp': request.arrival_time
        })
        
        return selected_server.server_id
    
    def _round_robin_selection(self, servers: List[Server]) -> Server:
        """Simple round robin selection"""
        request_count = len(self.request_history)
        return servers[request_count % len(servers)]
    
    def _weighted_round_robin(self, servers: List[Server]) -> Server:
        """Weighted round robin based on server capacity"""
        total_capacity = sum(server.capacity for server in servers)
        
        # Create weighted probability distribution
        weights = [server.capacity / total_capacity for server in servers]
        
        # Random selection based on weights
        r = np.random.random()
        cumulative_weight = 0
        
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if r <= cumulative_weight:
                return servers[i]
        
        return servers[-1]  # Fallback
    
    def _least_connections(self, servers: List[Server]) -> Server:
        """Route to server with least current load"""
        return min(servers, key=lambda s: s.current_load)
    
    def _least_response_time(self, servers: List[Server]) -> Server:
        """Route to server with lowest expected response time"""
        def expected_response_time(server):
            # Simple M/M/1 approximation: E[T] = 1/(μ - λ)
            if server.utilization() >= 0.99:
                return float('inf')
            return server.latency_ms + (server.latency_ms / (1 - server.utilization()))
        
        return min(servers, key=expected_response_time)
    
    def _power_of_two_choices(self, servers: List[Server]) -> Server:
        """Power of two choices algorithm"""
        if len(servers) <= 2:
            return min(servers, key=lambda s: s.current_load)
        
        # Randomly select two servers
        choices = np.random.choice(servers, size=2, replace=False)
        
        # Return the one with lower load
        return min(choices, key=lambda s: s.current_load)
    
    def _graph_based_optimal(self, request: Request, servers: List[Server]) -> Server:
        """Graph-based optimization considering multiple objectives"""
        
        # Multi-objective optimization
        scores = {}
        
        for server in servers:
            # Normalize different metrics to [0,1] scale
            load_score = 1 - server.utilization()  # Lower utilization = better
            latency_score = 1 / (1 + server.latency_ms / 100)  # Lower latency = better
            cost_score = 1 / (1 + server.cost_per_request * 1000)  # Lower cost = better
            availability_score = server.availability
            
            # Location affinity (simplified)
            location_score = 1.0 if server.location == request.user_location else 0.7
            
            # Weighted combination
            weights = {
                'load': 0.3,
                'latency': 0.25,
                'cost': 0.15,
                'availability': 0.2,
                'location': 0.1
            }
            
            total_score = (weights['load'] * load_score +
                          weights['latency'] * latency_score +
                          weights['cost'] * cost_score +
                          weights['availability'] * availability_score +
                          weights['location'] * location_score)
            
            scores[server.server_id] = total_score
        
        # Select server with highest score
        best_server_id = max(scores, key=scores.get)
        return next(s for s in servers if s.server_id == best_server_id)
    
    def simulate_load_balancing(self, requests: List[Request], 
                               algorithm: str = "graph_based_optimal") -> Dict:
        """Simulate load balancing over a series of requests"""
        
        # Reset server loads
        for server in self.servers.values():
            server.current_load = 0.0
        
        self.routing_decisions.clear()
        
        # Process requests
        for request in requests:
            self.request_history.append(request)
            
            try:
                selected_server = self.route_request(request, algorithm)
            except ValueError:
                # No available servers - skip request
                continue
            
            # Simulate request completion (simplified)
            # In reality, we'd track request completion times
        
        # Analyze results
        return self._analyze_simulation_results()
    
    def _analyze_simulation_results(self) -> Dict:
        """Analyze load balancing simulation results"""
        
        if not self.routing_decisions:
            return {}
        
        # Server utilization statistics
        server_utilizations = {server_id: server.utilization() 
                             for server_id, server in self.servers.items()}
        
        # Load distribution metrics
        utilizations = list(server_utilizations.values())
        avg_utilization = np.mean(utilizations)
        max_utilization = np.max(utilizations)
        min_utilization = np.min(utilizations)
        utilization_std = np.std(utilizations)
        
        # Request distribution
        server_request_counts = {}
        for decision in self.routing_decisions:
            server_id = decision['server_id']
            server_request_counts[server_id] = server_request_counts.get(server_id, 0) + 1
        
        # Calculate load balancing efficiency
        ideal_requests_per_server = len(self.routing_decisions) / len(self.servers)
        load_balance_efficiency = 1.0 - (utilization_std / avg_utilization if avg_utilization > 0 else 0)
        
        return {
            'total_requests': len(self.routing_decisions),
            'server_utilizations': server_utilizations,
            'avg_utilization': avg_utilization,
            'max_utilization': max_utilization,
            'min_utilization': min_utilization,
            'utilization_std': utilization_std,
            'load_balance_efficiency': load_balance_efficiency,
            'request_distribution': server_request_counts,
            'overloaded_servers': [sid for sid, util in server_utilizations.items() if util > 0.8]
        }
    
    def compare_algorithms(self, requests: List[Request]) -> Dict:
        """Compare different load balancing algorithms"""
        
        algorithms = [
            "round_robin",
            "weighted_round_robin", 
            "least_connections",
            "least_response_time",
            "power_of_two_choices",
            "graph_based_optimal"
        ]
        
        results = {}
        
        for algorithm in algorithms:
            # Reset state
            for server in self.servers.values():
                server.current_load = 0.0
            self.routing_decisions.clear()
            self.request_history.clear()
            
            # Run simulation
            result = self.simulate_load_balancing(requests, algorithm)
            results[algorithm] = result
        
        return results
    
    def visualize_load_distribution(self, results: Dict):
        """Visualize load distribution results"""
        
        algorithms = list(results.keys())
        n_algorithms = len(algorithms)
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for i, algorithm in enumerate(algorithms):
            if i >= len(axes):
                break
                
            result = results[algorithm]
            
            if not result:
                continue
            
            server_ids = list(result['server_utilizations'].keys())
            utilizations = list(result['server_utilizations'].values())
            
            # Bar chart of server utilizations
            bars = axes[i].bar(range(len(server_ids)), utilizations)
            
            # Color bars by utilization level
            for j, (bar, util) in enumerate(zip(bars, utilizations)):
                if util > 0.9:
                    bar.set_color('red')
                elif util > 0.7:
                    bar.set_color('orange')
                else:
                    bar.set_color('green')
            
            axes[i].set_title(f'{algorithm}\n'
                            f'Efficiency: {result["load_balance_efficiency"]:.3f}')
            axes[i].set_xlabel('Server')
            axes[i].set_ylabel('Utilization')
            axes[i].set_xticks(range(len(server_ids)))
            axes[i].set_xticklabels([f'S{j}' for j in range(len(server_ids))], rotation=45)
            axes[i].set_ylim(0, 1)
            axes[i].grid(True, alpha=0.3)
            
            # Add efficiency score
            axes[i].text(0.02, 0.98, f'Std: {result["utilization_std"]:.3f}', 
                        transform=axes[i].transAxes, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.show()

def demonstrate_graph_load_balancing():
    """Demonstrate graph-based load balancing algorithms"""
    
    print("GRAPH-BASED LOAD BALANCING DEMONSTRATION")
    print("=" * 60)
    
    # Create load balancer
    balancer = GraphLoadBalancer()
    
    # Add servers with different characteristics
    servers = [
        Server("server-1", capacity=100, latency_ms=5, cost_per_request=0.001, location="us-east"),
        Server("server-2", capacity=150, latency_ms=8, cost_per_request=0.0008, location="us-east"),
        Server("server-3", capacity=80, latency_ms=12, cost_per_request=0.0012, location="us-west"),
        Server("server-4", capacity=120, latency_ms=15, cost_per_request=0.0006, location="eu-west"),
        Server("server-5", capacity=90, latency_ms=20, cost_per_request=0.0004, location="asia-pacific"),
    ]
    
    for server in servers:
        balancer.add_server(server)
    
    # Generate synthetic request workload
    requests = []
    locations = ["us-east", "us-west", "eu-west", "asia-pacific"]
    
    for i in range(1000):
        request = Request(
            request_id=f"req-{i}",
            arrival_time=i * 0.01,  # 100 requests per second
            priority=np.random.choice([1, 2, 3], p=[0.2, 0.5, 0.3]),
            user_location=np.random.choice(locations, p=[0.4, 0.2, 0.25, 0.15]),
            estimated_processing_time=np.random.exponential(0.1)
        )
        requests.append(request)
    
    print(f"Generated {len(requests)} requests")
    print(f"Server capacities: {[s.capacity for s in servers]}")
    
    # Compare algorithms
    comparison_results = balancer.compare_algorithms(requests)
    
    # Print comparison results
    print(f"\nALGORITHM COMPARISON RESULTS")
    print("-" * 50)
    print("Algorithm              | Efficiency | Max Util | Std Dev | Overloaded")
    print("-----------------------|------------|----------|---------|----------")
    
    for algorithm, result in comparison_results.items():
        if result:
            efficiency = result['load_balance_efficiency']
            max_util = result['max_utilization']
            std_dev = result['utilization_std']
            overloaded_count = len(result['overloaded_servers'])
            
            print(f"{algorithm:<22} | {efficiency:8.3f}   | {max_util:6.3f}   | "
                  f"{std_dev:5.3f}   | {overloaded_count:8d}")
    
    # Detailed analysis for best algorithm
    best_algorithm = max(comparison_results.keys(), 
                        key=lambda k: comparison_results[k]['load_balance_efficiency'] 
                        if comparison_results[k] else 0)
    
    best_result = comparison_results[best_algorithm]
    
    print(f"\nBEST ALGORITHM: {best_algorithm.upper()}")
    print("-" * 40)
    print(f"Load Balance Efficiency: {best_result['load_balance_efficiency']:.3f}")
    print(f"Average Utilization: {best_result['avg_utilization']:.3f}")
    print(f"Utilization Range: {best_result['min_utilization']:.3f} - {best_result['max_utilization']:.3f}")
    
    print(f"\nSERVER UTILIZATION BREAKDOWN:")
    for server_id, util in best_result['server_utilizations'].items():
        server = balancer.servers[server_id]
        print(f"  {server_id}: {util:.3f} ({server.location}, {server.capacity} RPS capacity)")
    
    # Recommendations
    print(f"\nRECOMMENDATIONS")
    print("-" * 20)
    
    if best_result['max_utilization'] > 0.8:
        print("⚠️  Some servers are highly utilized - consider adding capacity")
    
    if best_result['utilization_std'] > 0.2:
        print("📊 High utilization variance - load balancing can be improved")
    
    if best_result['overloaded_servers']:
        print(f"🚨 {len(best_result['overloaded_servers'])} servers are overloaded")
        for server_id in best_result['overloaded_servers']:
            print(f"   - Consider scaling {server_id}")
    
    print("💡 Graph-based optimization considers multiple factors: load, latency, cost, location")
    print("💡 Monitor request patterns to adjust algorithm weights dynamically")
    
    # Visualize results
    balancer.visualize_load_distribution(comparison_results)

demonstrate_graph_load_balancing()
```

### Part 3: Production Systems (30 minutes)

#### 3.1 Real-World Applications (10 min)

**Google's Network Topology Design:**

Google's global network demonstrates advanced graph-theoretic principles:

1. **Clos Networks**: Multi-stage switching fabrics with guaranteed bisection bandwidth
2. **Software-Defined Routing**: Dynamic path computation using shortest path algorithms
3. **Traffic Engineering**: Network flow optimization for bandwidth utilization
4. **Failure Recovery**: Pre-computed backup paths using disjoint path algorithms

**Facebook's Social Graph:**

Facebook's friend network exhibits small-world properties:
- Average path length: ~3.5 degrees of separation
- High clustering coefficient: Friends of friends are likely friends
- Scale-free degree distribution: Some users have many more connections

**Netflix's Content Delivery Network:**

Netflix uses graph algorithms for content placement:
1. **Spectral Clustering**: Group users by viewing patterns
2. **Minimum Spanning Trees**: Optimize cache placement costs
3. **Max-Flow**: Determine content delivery capacity
4. **Graph Partitioning**: Distribute load across CDN nodes

#### 3.2 Performance Benchmarks (10 min)

**Network Topology Performance Characteristics:**

Real-world measurements show clear patterns:

| Topology | Avg Path Length | Diameter | Bisection BW | Fault Tolerance |
|----------|-----------------|----------|--------------|-----------------|
| Fat Tree | O(log n) | 6 | Full | High |
| Torus | O(√n) | n/2 | Limited | Moderate |
| Hypercube | O(log n) | log n | High | High |
| Random | O(log n) | O(log n) | Variable | Variable |

**Algorithm Performance Benchmarks:**

| Algorithm | Time Complexity | Space | Use Case | Scalability |
|-----------|-----------------|-------|----------|-------------|
| Dijkstra | O(E log V) | O(V) | Single-source SP | 10K nodes |
| Floyd-Warshall | O(V³) | O(V²) | All-pairs SP | 1K nodes |
| Max Flow | O(VE²) | O(V²) | Capacity planning | 10K nodes |
| Min Cut | O(VE log V) | O(V) | Bottleneck analysis | 100K nodes |
| Spectral Clustering | O(V³) | O(V²) | Graph partitioning | 10K nodes |

#### 3.3 Failure Scenarios and Recovery (10 min)

**Common Network Failure Patterns:**

1. **Correlated Failures**: 
   - Power outages affect entire racks
   - Network partitions isolate data centers
   - Software bugs cause coordinated failures

2. **Cascade Failures**:
   - Overload causes servers to fail
   - Failed servers increase load on survivors
   - Positive feedback leads to system collapse

3. **Byzantine Failures**:
   - Nodes behave unpredictably
   - May provide incorrect information
   - Require robust consensus algorithms

**Recovery Strategies:**

1. **Graph-Based Routing Recovery**:
   - Pre-compute backup paths using k-shortest paths
   - Use link-disjoint or node-disjoint alternatives
   - Implement fast rerouting (< 50ms recovery)

2. **Spectral Analysis for Failure Prediction**:
   - Monitor algebraic connectivity changes
   - Detect when network becomes fragile
   - Proactively add redundant connections

3. **Distributed Graph Algorithms**:
   - Use gossip protocols for topology discovery
   - Implement distributed spanning tree algorithms
   - Enable self-healing network overlays

### Part 4: Research and Extensions (15 minutes)

#### 4.1 Recent Advances (5 min)

**Graph Neural Networks for Network Optimization:**

Recent research applies machine learning to graph problems:

1. **GNNs for Routing**: Learn optimal routing policies from network state
2. **Reinforcement Learning**: Adapt load balancing strategies in real-time
3. **Graph Attention**: Focus on most critical network components

**Quantum Graph Algorithms:**

Quantum computing offers potential speedups:

1. **Quantum Walks**: Exponential speedup for certain graph problems
2. **Quantum Max-Cut**: Approximate solutions using quantum annealing
3. **Quantum Spectral**: Faster eigenvalue computation for large graphs

#### 4.2 Open Problems (5 min)

**Dynamic Graph Analysis:**

Real networks change continuously, but most algorithms assume static graphs:

1. **Temporal Networks**: How to analyze graphs that evolve over time
2. **Streaming Algorithms**: Process graph updates with limited memory
3. **Online Optimization**: Make routing decisions with incomplete information

**Massive Scale Challenges:**

Modern systems have millions of nodes:

1. **Distributed Graph Processing**: Split computation across many machines
2. **Approximate Algorithms**: Trade accuracy for scalability
3. **Memory Hierarchy**: Optimize for cache and memory access patterns

#### 4.3 Alternative Approaches (5 min)

**Hypergraph Models:**

Some relationships involve more than two entities:
- Hyperedges connect multiple nodes simultaneously
- Model group communications, multi-party transactions
- Require different algorithms than standard graphs

**Probabilistic Graph Models:**

Uncertainty in network topology:
- Edge existence probabilities
- Uncertain edge weights
- Robust optimization under uncertainty

**Multi-layer Networks:**

Real systems have multiple interaction types:
- Physical network topology
- Logical service dependencies  
- Social/organizational relationships
- Each layer affects the others

## Site Content Integration

### Mapped Content
- `/docs/architects-handbook/quantitative-analysis/graph-theory.md` - Core graph algorithms and spectral analysis
- `/docs/fundamentals/distributed-systems-theory.md` - Theoretical foundations
- `/docs/patterns/network-patterns.md` - Network design patterns

### Code Repository Links
- Implementation: `/examples/episode-3-graph-theory/`
- Tests: `/tests/episode-3-graph-theory/`
- Benchmarks: `/benchmarks/episode-3-graph-theory/`

## Quality Checklist
- [x] Mathematical rigor verified - graph theory formulations and algorithms validated
- [x] Code tested and benchmarked - algorithms tested on various graph types
- [x] Production examples validated - Google, Facebook, Netflix examples from documented architectures
- [x] Prerequisites clearly stated - linear algebra and discrete mathematics knowledge required
- [x] Learning objectives measurable - specific graph theory applications and implementations
- [x] Site content integrated - existing graph theory content referenced and extended
- [x] References complete - academic graph theory sources and distributed systems applications

## Key Takeaways

1. **Topology Determines Performance** - Network structure fundamentally affects latency, throughput, and fault tolerance
2. **Spectral Properties Reveal Structure** - Eigenvalues expose hidden connectivity characteristics
3. **Flow Algorithms Enable Optimization** - Network flow techniques optimize capacity and resource allocation
4. **Dependencies Create Vulnerabilities** - Service dependency graphs reveal single points of failure
5. **Graph Algorithms Scale to Production** - Modern distributed systems apply graph theory at massive scale
6. **Failure Patterns Follow Graph Structure** - Understanding topology predicts how failures propagate

Graph theory transforms network design from intuition to science. By modeling systems as graphs and applying rigorous mathematical analysis, architects can predict performance, identify bottlenecks, plan capacity, and design resilient topologies. Master these principles, and you'll build networks that are not just functional, but optimal.
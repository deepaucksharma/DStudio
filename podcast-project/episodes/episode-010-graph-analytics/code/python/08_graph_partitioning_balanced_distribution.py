"""
Graph Partitioning Algorithm for Balanced Distribution
Indian e-commerce network ko efficiently distribute karna

Author: Episode 10 - Graph Analytics at Scale
Context: Flipkart/Amazon scale graph ko multiple servers mein partition karna
"""

import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Set
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, deque
import logging
import time
import json
from datetime import datetime
import random
from dataclasses import dataclass
from enum import Enum
import math

# Hindi mein logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PartitioningAlgorithm(Enum):
    """Graph partitioning algorithms"""
    METIS = "metis"              # Multi-level partitioning
    SPECTRAL = "spectral"        # Spectral clustering
    RANDOM = "random"            # Random assignment
    GEOGRAPHIC = "geographic"    # Location-based
    LOAD_BALANCED = "load_balanced"  # Load balancing focused

class PartitionQuality(Enum):
    """Partition quality metrics"""
    EDGE_CUT = "edge_cut"           # Minimize edges between partitions
    COMMUNICATION = "communication"  # Minimize cross-partition communication  
    LOAD_BALANCE = "load_balance"   # Balance computational load
    LOCALITY = "locality"           # Maintain data locality

@dataclass
class PartitionMetrics:
    """Partition quality metrics"""
    partition_id: int
    node_count: int
    edge_count: int
    cross_partition_edges: int
    computational_load: float
    memory_usage: float
    communication_cost: float

class IndianEcommerceGraphPartitioner:
    """
    Graph Partitioning System for Indian E-commerce Networks
    
    Use Case: Flipkart/Amazon scale product-customer-seller networks
    - 10 crore+ products
    - 50 crore+ customers  
    - 10 lakh+ sellers
    - 100 crore+ interactions daily
    """
    
    def __init__(self):
        self.graph = nx.Graph()
        self.partitions = {}
        self.partition_metrics = {}
        
        # Indian e-commerce context
        self.indian_categories = [
            "Electronics", "Clothing", "Home & Kitchen", "Books", "Beauty",
            "Sports & Fitness", "Automotive", "Health", "Grocery", "Toys",
            "Jewelry", "Mobile & Accessories", "Appliances", "Furniture"
        ]
        
        self.indian_cities = [
            "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata",
            "Pune", "Ahmedabad", "Surat", "Jaipur", "Lucknow", "Kanpur", "Nagpur",
            "Indore", "Bhopal", "Visakhapatnam", "Ludhiana", "Agra", "Kochi"
        ]
        
        self.indian_brands = [
            "Reliance", "Tata", "Mahindra", "Bajaj", "Godrej", "Dabur",
            "Patanjali", "Amul", "Britannia", "ITC", "Hindustan Unilever",
            "Asian Paints", "Maruti Suzuki", "Infosys", "TCS"
        ]
        
        # Partition colors for visualization
        self.partition_colors = [
            '#FF6B35', '#4CAF50', '#2196F3', '#FF9800', '#9C27B0',
            '#607D8B', '#795548', '#E91E63', '#00BCD4', '#8BC34A',
            '#FFC107', '#FF5722', '#3F51B5', '#009688', '#CDDC39'
        ]
        
        logger.info("Indian E-commerce Graph Partitioner ready!")
    
    def generate_ecommerce_network(self, num_customers: int = 10000, 
                                 num_products: int = 5000, 
                                 num_sellers: int = 1000):
        """
        Indian e-commerce network generate karta hai
        """
        logger.info(f"Generating e-commerce network: {num_customers:,} customers, "
                   f"{num_products:,} products, {num_sellers:,} sellers...")
        
        # Generate customers
        for i in range(num_customers):
            customer_id = f"customer_{i}"
            city = random.choice(self.indian_cities)
            age = random.randint(18, 65)
            income_level = random.choices(['low', 'medium', 'high'], weights=[50, 35, 15])[0]
            
            self.graph.add_node(customer_id,
                              node_type='customer',
                              city=city,
                              age=age,
                              income_level=income_level,
                              purchase_power=random.randint(1000, 50000),
                              activity_level=random.uniform(0.1, 1.0))
        
        # Generate products
        for i in range(num_products):
            product_id = f"product_{i}"
            category = random.choice(self.indian_categories)
            brand = random.choice(self.indian_brands + [f"Brand_{random.randint(1, 100)}"])
            price = random.randint(100, 50000)
            rating = random.uniform(2.0, 5.0)
            
            self.graph.add_node(product_id,
                              node_type='product',
                              category=category,
                              brand=brand,
                              price=price,
                              rating=rating,
                              popularity=random.uniform(0.1, 1.0))
        
        # Generate sellers
        for i in range(num_sellers):
            seller_id = f"seller_{i}"
            city = random.choice(self.indian_cities)
            seller_type = random.choices(['individual', 'business'], weights=[70, 30])[0]
            
            self.graph.add_node(seller_id,
                              node_type='seller',
                              city=city,
                              seller_type=seller_type,
                              rating=random.uniform(3.0, 5.0),
                              inventory_size=random.randint(10, 1000))
        
        # Generate relationships
        self._create_ecommerce_relationships(num_customers, num_products, num_sellers)
        
        logger.info(f"E-commerce network generated: {self.graph.number_of_nodes():,} nodes, "
                   f"{self.graph.number_of_edges():,} edges")
    
    def _create_ecommerce_relationships(self, num_customers: int, 
                                      num_products: int, num_sellers: int):
        """E-commerce relationships create karta hai"""
        
        # Customer-Product purchases
        logger.info("Creating customer-product purchase relationships...")
        for i in range(num_customers):
            customer_id = f"customer_{i}"
            
            # Each customer purchases 1-20 products
            num_purchases = random.randint(1, 20)
            purchased_products = random.sample(range(num_products), num_purchases)
            
            for product_idx in purchased_products:
                product_id = f"product_{product_idx}"
                
                # Purchase attributes
                purchase_amount = self.graph.nodes[product_id]['price'] * random.randint(1, 3)
                purchase_date = datetime.now() - pd.Timedelta(days=random.randint(1, 365))
                rating_given = random.uniform(1.0, 5.0)
                
                self.graph.add_edge(customer_id, product_id,
                                  relationship='purchase',
                                  amount=purchase_amount,
                                  date=purchase_date,
                                  rating=rating_given,
                                  weight=purchase_amount / 1000)  # Weight for algorithms
        
        # Seller-Product relationships (who sells what)
        logger.info("Creating seller-product inventory relationships...")
        for i in range(num_sellers):
            seller_id = f"seller_{i}"
            
            # Each seller sells 5-100 products
            num_products_sold = random.randint(5, 100)
            seller_products = random.sample(range(num_products), 
                                          min(num_products_sold, num_products))
            
            for product_idx in seller_products:
                product_id = f"product_{product_idx}"
                
                self.graph.add_edge(seller_id, product_id,
                                  relationship='sells',
                                  inventory_count=random.randint(1, 500),
                                  seller_price=self.graph.nodes[product_id]['price'] * 
                                               random.uniform(0.8, 1.2),
                                  weight=1.0)
        
        # Customer similarity (for recommendations)
        logger.info("Creating customer similarity relationships...")
        customers = [f"customer_{i}" for i in range(min(num_customers, 1000))]  # Limit for performance
        
        for i, customer1 in enumerate(customers):
            # Connect to 5-15 similar customers
            similar_customers = random.sample(customers[:i] + customers[i+1:], 
                                            random.randint(5, 15))
            
            for customer2 in similar_customers:
                similarity_score = random.uniform(0.1, 0.9)
                
                self.graph.add_edge(customer1, customer2,
                                  relationship='similar',
                                  similarity=similarity_score,
                                  weight=similarity_score)
    
    def partition_graph_metis_style(self, num_partitions: int = 8) -> Dict[int, Set[str]]:
        """
        METIS-style multi-level graph partitioning algorithm
        """
        logger.info(f"Running METIS-style partitioning into {num_partitions} partitions...")
        
        start_time = time.time()
        
        # Step 1: Graph coarsening phase
        coarsened_graph = self._coarsen_graph()
        
        # Step 2: Initial partitioning on coarsened graph
        initial_partitions = self._initial_partition(coarsened_graph, num_partitions)
        
        # Step 3: Refinement phase - project back to original graph
        final_partitions = self._refine_partitions(initial_partitions, num_partitions)
        
        partitioning_time = time.time() - start_time
        
        logger.info(f"METIS-style partitioning completed in {partitioning_time:.2f} seconds")
        
        # Calculate partition quality
        self._calculate_partition_metrics(final_partitions)
        
        return final_partitions
    
    def _coarsen_graph(self) -> nx.Graph:
        """Graph coarsening - merge similar nodes"""
        logger.info("Coarsening graph...")
        
        coarsened = self.graph.copy()
        
        # Find pairs of nodes to merge based on high edge weights
        nodes_to_merge = []
        processed_nodes = set()
        
        for node in coarsened.nodes():
            if node in processed_nodes:
                continue
                
            # Find best neighbor to merge with
            best_neighbor = None
            best_weight = 0
            
            for neighbor in coarsened.neighbors(node):
                if neighbor not in processed_nodes:
                    edge_weight = coarsened[node][neighbor].get('weight', 0)
                    if edge_weight > best_weight:
                        best_weight = edge_weight
                        best_neighbor = neighbor
            
            if best_neighbor and best_weight > 0.5:  # Merge threshold
                nodes_to_merge.append((node, best_neighbor))
                processed_nodes.add(node)
                processed_nodes.add(best_neighbor)
        
        # Merge selected node pairs
        for node1, node2 in nodes_to_merge:
            if node1 in coarsened and node2 in coarsened:
                # Merge node2 into node1
                merged_attrs = coarsened.nodes[node1].copy()
                merged_attrs.update({'merged_nodes': [node1, node2]})
                
                # Add node2's edges to node1
                for neighbor in list(coarsened.neighbors(node2)):
                    if neighbor != node1:  # Avoid self-loops
                        if coarsened.has_edge(node1, neighbor):
                            # Combine edge weights
                            combined_weight = (coarsened[node1][neighbor].get('weight', 0) + 
                                             coarsened[node2][neighbor].get('weight', 0))
                            coarsened[node1][neighbor]['weight'] = combined_weight
                        else:
                            # Transfer edge
                            edge_attrs = coarsened[node2][neighbor].copy()
                            coarsened.add_edge(node1, neighbor, **edge_attrs)
                
                # Remove node2
                coarsened.remove_node(node2)
        
        logger.info(f"Graph coarsened from {self.graph.number_of_nodes()} to "
                   f"{coarsened.number_of_nodes()} nodes")
        
        return coarsened
    
    def _initial_partition(self, graph: nx.Graph, num_partitions: int) -> Dict[int, Set[str]]:
        """Initial partitioning using spectral clustering approach"""
        logger.info("Computing initial partitioning...")
        
        partitions = {i: set() for i in range(num_partitions)}
        
        try:
            # Use spectral clustering approach
            # Calculate Laplacian matrix
            laplacian = nx.laplacian_matrix(graph).astype(float)
            
            # Compute eigenvalues and eigenvectors
            eigenvals, eigenvecs = np.linalg.eigh(laplacian.toarray())
            
            # Use Fiedler vector (second smallest eigenvalue) for bisection
            fiedler_vector = eigenvecs[:, 1]
            
            # Recursively bisect the graph
            nodes_list = list(graph.nodes())
            self._recursive_bisection(nodes_list, fiedler_vector, partitions, 0, num_partitions)
            
        except Exception as e:
            logger.warning(f"Spectral partitioning failed: {e}, using random partitioning")
            # Fallback to random partitioning
            nodes = list(graph.nodes())
            random.shuffle(nodes)
            
            nodes_per_partition = len(nodes) // num_partitions
            for i in range(num_partitions):
                start_idx = i * nodes_per_partition
                if i == num_partitions - 1:  # Last partition gets remaining nodes
                    end_idx = len(nodes)
                else:
                    end_idx = (i + 1) * nodes_per_partition
                
                partitions[i] = set(nodes[start_idx:end_idx])
        
        return partitions
    
    def _recursive_bisection(self, nodes: List[str], fiedler_vector: np.ndarray, 
                           partitions: Dict[int, Set[str]], depth: int, max_partitions: int):
        """Recursive graph bisection using Fiedler vector"""
        if len(nodes) <= max_partitions or depth >= int(math.log2(max_partitions)):
            # Assign remaining nodes to partitions
            partition_id = depth % max_partitions
            partitions[partition_id].update(nodes)
            return
        
        # Find median of Fiedler vector values
        median_value = np.median(fiedler_vector)
        
        # Split nodes based on Fiedler vector
        left_nodes = [node for i, node in enumerate(nodes) if fiedler_vector[i] <= median_value]
        right_nodes = [node for i, node in enumerate(nodes) if fiedler_vector[i] > median_value]
        
        # Recursively partition
        if left_nodes:
            left_indices = [i for i, node in enumerate(nodes) if node in left_nodes]
            left_fiedler = fiedler_vector[left_indices]
            self._recursive_bisection(left_nodes, left_fiedler, partitions, depth + 1, max_partitions)
        
        if right_nodes:
            right_indices = [i for i, node in enumerate(nodes) if node in right_nodes]
            right_fiedler = fiedler_vector[right_indices]
            self._recursive_bisection(right_nodes, right_fiedler, partitions, depth + 1, max_partitions)
    
    def _refine_partitions(self, partitions: Dict[int, Set[str]], 
                          num_partitions: int) -> Dict[int, Set[str]]:
        """Refine partitions using Kernighan-Lin style local optimization"""
        logger.info("Refining partitions...")
        
        refined_partitions = partitions.copy()
        max_iterations = 10
        
        for iteration in range(max_iterations):
            improvement_found = False
            
            # Try to improve each partition pair
            for p1 in range(num_partitions):
                for p2 in range(p1 + 1, num_partitions):
                    if self._improve_partition_pair(refined_partitions, p1, p2):
                        improvement_found = True
            
            if not improvement_found:
                break
        
        logger.info(f"Partition refinement completed after {iteration + 1} iterations")
        return refined_partitions
    
    def _improve_partition_pair(self, partitions: Dict[int, Set[str]], 
                               p1: int, p2: int) -> bool:
        """Improve a pair of partitions by swapping nodes"""
        improved = False
        
        # Calculate current cut cost
        current_cut = self._calculate_cut_cost(partitions, p1, p2)
        
        # Try swapping each node from p1 to p2 and vice versa
        for node in list(partitions[p1]):
            # Try moving node from p1 to p2
            partitions[p1].remove(node)
            partitions[p2].add(node)
            
            new_cut = self._calculate_cut_cost(partitions, p1, p2)
            
            if new_cut < current_cut:
                # Keep the improvement
                current_cut = new_cut
                improved = True
            else:
                # Revert the move
                partitions[p2].remove(node)
                partitions[p1].add(node)
        
        return improved
    
    def _calculate_cut_cost(self, partitions: Dict[int, Set[str]], 
                           p1: int, p2: int) -> float:
        """Calculate cut cost between two partitions"""
        cut_cost = 0
        
        for node1 in partitions[p1]:
            for node2 in partitions[p2]:
                if self.graph.has_edge(node1, node2):
                    edge_weight = self.graph[node1][node2].get('weight', 1.0)
                    cut_cost += edge_weight
        
        return cut_cost
    
    def partition_graph_geographic(self, num_partitions: int = 8) -> Dict[int, Set[str]]:
        """
        Geographic-based partitioning for Indian e-commerce
        """
        logger.info(f"Running geographic partitioning into {num_partitions} partitions...")
        
        start_time = time.time()
        
        # Group cities by regions
        city_regions = {
            'North': ['Delhi', 'Jaipur', 'Lucknow', 'Kanpur', 'Ludhiana', 'Agra'],
            'West': ['Mumbai', 'Pune', 'Ahmedabad', 'Surat'],
            'South': ['Bangalore', 'Chennai', 'Hyderabad', 'Kochi'],
            'East': ['Kolkata', 'Bhubaneswar', 'Guwahati'],
            'Central': ['Nagpur', 'Indore', 'Bhopal']
        }
        
        # Reverse mapping: city -> region
        city_to_region = {}
        for region, cities in city_regions.items():
            for city in cities:
                city_to_region[city] = region
        
        # Assign nodes to partitions based on geography
        partitions = {i: set() for i in range(num_partitions)}
        region_to_partition = {}
        partition_idx = 0
        
        for region in city_regions.keys():
            region_to_partition[region] = partition_idx % num_partitions
            partition_idx += 1
        
        # Assign nodes to partitions
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            
            if 'city' in node_data:
                city = node_data['city']
                region = city_to_region.get(city, 'Central')  # Default to Central
                partition_id = region_to_partition[region]
                partitions[partition_id].add(node)
            else:
                # For nodes without city info (like products), use hash-based assignment
                partition_id = hash(node) % num_partitions
                partitions[partition_id].add(node)
        
        partitioning_time = time.time() - start_time
        
        logger.info(f"Geographic partitioning completed in {partitioning_time:.2f} seconds")
        
        # Calculate partition quality
        self._calculate_partition_metrics(partitions)
        
        return partitions
    
    def partition_graph_load_balanced(self, num_partitions: int = 8) -> Dict[int, Set[str]]:
        """
        Load-balanced partitioning considering computational requirements
        """
        logger.info(f"Running load-balanced partitioning into {num_partitions} partitions...")
        
        start_time = time.time()
        
        # Calculate computational load for each node
        node_loads = {}
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            
            # Load calculation based on node type and properties
            if node_data.get('node_type') == 'customer':
                # Customer load based on activity and connections
                load = (node_data.get('activity_level', 0.5) * 
                       self.graph.degree(node) * 0.1)
            elif node_data.get('node_type') == 'product':
                # Product load based on popularity and connections
                load = (node_data.get('popularity', 0.5) * 
                       self.graph.degree(node) * 0.2)
            elif node_data.get('node_type') == 'seller':
                # Seller load based on inventory and connections
                load = (node_data.get('inventory_size', 100) / 1000 * 
                       self.graph.degree(node) * 0.15)
            else:
                load = self.graph.degree(node) * 0.05  # Default load
            
            node_loads[node] = load
        
        # Sort nodes by load (heaviest first)
        sorted_nodes = sorted(node_loads.items(), key=lambda x: x[1], reverse=True)
        
        # Greedy assignment to balance loads
        partitions = {i: set() for i in range(num_partitions)}
        partition_loads = {i: 0.0 for i in range(num_partitions)}
        
        for node, load in sorted_nodes:
            # Find partition with minimum load
            min_load_partition = min(partition_loads.items(), key=lambda x: x[1])[0]
            
            # Assign node to partition with minimum load
            partitions[min_load_partition].add(node)
            partition_loads[min_load_partition] += load
        
        partitioning_time = time.time() - start_time
        
        logger.info(f"Load-balanced partitioning completed in {partitioning_time:.2f} seconds")
        
        # Store load information in metrics
        for partition_id, load in partition_loads.items():
            if partition_id not in self.partition_metrics:
                self.partition_metrics[partition_id] = {}
            self.partition_metrics[partition_id]['computational_load'] = load
        
        # Calculate other partition quality metrics
        self._calculate_partition_metrics(partitions)
        
        return partitions
    
    def _calculate_partition_metrics(self, partitions: Dict[int, Set[str]]):
        """Calculate comprehensive partition quality metrics"""
        logger.info("Calculating partition quality metrics...")
        
        total_edges = self.graph.number_of_edges()
        total_cross_partition_edges = 0
        
        for partition_id, nodes in partitions.items():
            if not nodes:
                continue
                
            # Create subgraph for this partition
            subgraph = self.graph.subgraph(nodes)
            
            # Count cross-partition edges
            cross_edges = 0
            for node in nodes:
                for neighbor in self.graph.neighbors(node):
                    if neighbor not in nodes:
                        cross_edges += 1
            
            total_cross_partition_edges += cross_edges
            
            # Calculate memory usage estimate (based on nodes and edges)
            memory_usage = len(nodes) * 0.1 + subgraph.number_of_edges() * 0.05  # MB estimate
            
            # Calculate communication cost
            communication_cost = cross_edges * 0.1  # Cost per cross-partition edge
            
            # Store metrics
            self.partition_metrics[partition_id] = PartitionMetrics(
                partition_id=partition_id,
                node_count=len(nodes),
                edge_count=subgraph.number_of_edges(),
                cross_partition_edges=cross_edges,
                computational_load=self.partition_metrics.get(partition_id, {}).get('computational_load', len(nodes) * 0.1),
                memory_usage=memory_usage,
                communication_cost=communication_cost
            )
        
        # Calculate global metrics
        edge_cut_ratio = total_cross_partition_edges / (2 * total_edges) if total_edges > 0 else 0
        
        logger.info(f"Partition quality: {edge_cut_ratio:.3f} edge cut ratio")
        
    def compare_partitioning_algorithms(self, num_partitions: int = 8) -> Dict:
        """
        Compare different partitioning algorithms
        """
        logger.info("Comparing different partitioning algorithms...")
        
        comparison_results = {}
        
        algorithms = [
            ('METIS-style', lambda: self.partition_graph_metis_style(num_partitions)),
            ('Geographic', lambda: self.partition_graph_geographic(num_partitions)),
            ('Load-balanced', lambda: self.partition_graph_load_balanced(num_partitions))
        ]
        
        for algo_name, algo_func in algorithms:
            logger.info(f"Testing {algo_name} algorithm...")
            
            start_time = time.time()
            partitions = algo_func()
            execution_time = time.time() - start_time
            
            # Calculate quality metrics
            total_cross_edges = sum(
                metrics.cross_partition_edges 
                for metrics in self.partition_metrics.values()
                if isinstance(metrics, PartitionMetrics)
            )
            
            # Load balance metric (standard deviation of partition sizes)
            partition_sizes = [len(nodes) for nodes in partitions.values()]
            load_balance = np.std(partition_sizes) / np.mean(partition_sizes) if partition_sizes else 0
            
            comparison_results[algo_name] = {
                'execution_time': execution_time,
                'cross_partition_edges': total_cross_edges,
                'load_balance_coefficient': load_balance,
                'partitions': len(partitions),
                'avg_partition_size': np.mean(partition_sizes),
                'partition_size_std': np.std(partition_sizes)
            }
        
        return comparison_results
    
    def visualize_partitions(self, partitions: Dict[int, Set[str]], 
                           algorithm_name: str = "Graph Partitioning",
                           save_path: Optional[str] = None):
        """
        Visualize graph partitions
        """
        logger.info(f"Creating partition visualization for {algorithm_name}...")
        
        # Create subgraph for visualization (sample for large graphs)
        max_nodes = 500
        if self.graph.number_of_nodes() > max_nodes:
            # Sample nodes from each partition
            sample_nodes = set()
            for partition_id, nodes in partitions.items():
                sample_size = min(max_nodes // len(partitions), len(nodes))
                sample_nodes.update(random.sample(list(nodes), sample_size))
            
            viz_graph = self.graph.subgraph(sample_nodes)
        else:
            viz_graph = self.graph
        
        plt.figure(figsize=(16, 12))
        
        # Create layout
        pos = nx.spring_layout(viz_graph, k=1, iterations=50, seed=42)
        
        # Node colors based on partitions
        node_colors = []
        node_to_partition = {}
        
        # Create node to partition mapping
        for partition_id, nodes in partitions.items():
            for node in nodes:
                node_to_partition[node] = partition_id
        
        for node in viz_graph.nodes():
            partition_id = node_to_partition.get(node, 0)
            color_idx = partition_id % len(self.partition_colors)
            node_colors.append(self.partition_colors[color_idx])
        
        # Node sizes based on node type
        node_sizes = []
        for node in viz_graph.nodes():
            node_data = viz_graph.nodes[node]
            node_type = node_data.get('node_type', 'unknown')
            
            if node_type == 'customer':
                size = 30
            elif node_type == 'product':
                size = 50
            elif node_type == 'seller':
                size = 70
            else:
                size = 20
            
            node_sizes.append(size)
        
        # Draw edges with different colors for cross-partition edges
        within_partition_edges = []
        cross_partition_edges = []
        
        for edge in viz_graph.edges():
            node1, node2 = edge
            partition1 = node_to_partition.get(node1, 0)
            partition2 = node_to_partition.get(node2, 0)
            
            if partition1 == partition2:
                within_partition_edges.append(edge)
            else:
                cross_partition_edges.append(edge)
        
        # Draw within-partition edges
        if within_partition_edges:
            nx.draw_networkx_edges(viz_graph, pos, edgelist=within_partition_edges,
                                  edge_color='lightblue', alpha=0.3, width=0.5)
        
        # Draw cross-partition edges (thicker, more visible)
        if cross_partition_edges:
            nx.draw_networkx_edges(viz_graph, pos, edgelist=cross_partition_edges,
                                  edge_color='red', alpha=0.7, width=1.5)
        
        # Draw nodes
        nx.draw_networkx_nodes(viz_graph, pos, node_color=node_colors, 
                              node_size=node_sizes, alpha=0.8)
        
        plt.title(f"E-commerce Graph Partitions - {algorithm_name}\n"
                 f"Red edges = Cross-partition communications\n"
                 f"Blue edges = Within-partition communications", 
                 fontsize=14, pad=20)
        
        # Create legend for partitions
        legend_elements = []
        for i in range(min(len(partitions), len(self.partition_colors))):
            color = self.partition_colors[i]
            legend_elements.append(plt.scatter([], [], c=color, s=100, 
                                             label=f'Partition {i}'))
        
        plt.legend(handles=legend_elements, loc='upper left')
        
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Partition visualization saved to {save_path}")
        
        plt.show()
    
    def generate_partitioning_report(self, comparison_results: Dict) -> str:
        """
        Generate comprehensive partitioning analysis report
        """
        report = []
        report.append("📊 GRAPH PARTITIONING ANALYSIS REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Network overview
        report.append("🌐 NETWORK OVERVIEW:")
        report.append(f"• Total Nodes: {self.graph.number_of_nodes():,}")
        report.append(f"• Total Edges: {self.graph.number_of_edges():,}")
        report.append(f"• Network Density: {nx.density(self.graph):.6f}")
        report.append("")
        
        # Algorithm comparison
        report.append("⚖️ ALGORITHM COMPARISON:")
        report.append("-" * 30)
        
        for algo_name, results in comparison_results.items():
            report.append(f"\n🔧 {algo_name}:")
            report.append(f"   • Execution Time: {results['execution_time']:.3f}s")
            report.append(f"   • Cross-partition Edges: {results['cross_partition_edges']:,}")
            report.append(f"   • Load Balance Coefficient: {results['load_balance_coefficient']:.3f}")
            report.append(f"   • Avg Partition Size: {results['avg_partition_size']:.1f} nodes")
            report.append(f"   • Partition Size StdDev: {results['partition_size_std']:.1f}")
        
        # Best algorithm recommendation
        if comparison_results:
            # Find best algorithm based on different criteria
            min_cross_edges = min(comparison_results.items(), 
                                key=lambda x: x[1]['cross_partition_edges'])
            min_load_imbalance = min(comparison_results.items(), 
                                   key=lambda x: x[1]['load_balance_coefficient'])
            fastest_execution = min(comparison_results.items(), 
                                  key=lambda x: x[1]['execution_time'])
            
            report.append(f"\n🏆 ALGORITHM RECOMMENDATIONS:")
            report.append(f"   • Min Communication Overhead: {min_cross_edges[0]}")
            report.append(f"   • Best Load Balance: {min_load_imbalance[0]}")
            report.append(f"   • Fastest Execution: {fastest_execution[0]}")
        
        # Partition metrics details
        if self.partition_metrics:
            report.append(f"\n📈 PARTITION DETAILS:")
            report.append("-" * 25)
            
            for partition_id, metrics in self.partition_metrics.items():
                if isinstance(metrics, PartitionMetrics):
                    report.append(f"\nPartition {partition_id}:")
                    report.append(f"   • Nodes: {metrics.node_count:,}")
                    report.append(f"   • Internal Edges: {metrics.edge_count:,}")
                    report.append(f"   • Cross-partition Edges: {metrics.cross_partition_edges}")
                    report.append(f"   • Computational Load: {metrics.computational_load:.2f}")
                    report.append(f"   • Memory Usage: {metrics.memory_usage:.2f} MB")
                    report.append(f"   • Communication Cost: {metrics.communication_cost:.2f}")
        
        # E-commerce specific insights
        report.append(f"\n🛒 E-COMMERCE PARTITIONING INSIGHTS:")
        report.append("-" * 40)
        report.append("• Geographic partitioning reduces network latency for regional queries")
        report.append("• Load-balanced partitioning ensures even resource utilization")
        report.append("• Customer-product relationships should be co-located when possible")
        report.append("• Seller-product edges can tolerate cross-partition placement")
        report.append("• Recommendation algorithms benefit from customer co-location")
        
        # Production recommendations
        report.append(f"\n🎯 PRODUCTION RECOMMENDATIONS:")
        report.append("-" * 35)
        report.append("• Use geographic partitioning for user-facing queries (low latency)")
        report.append("• Apply load balancing for batch processing jobs")
        report.append("• Implement dynamic re-partitioning for changing workloads")
        report.append("• Cache frequently accessed cross-partition data")
        report.append("• Monitor partition metrics and rebalance quarterly")
        
        return "\n".join(report)


def run_graph_partitioning_demo():
    """
    Complete graph partitioning demonstration
    """
    print("📊 Graph Partitioning for Indian E-commerce Networks")
    print("="*60)
    
    # Initialize partitioner
    partitioner = IndianEcommerceGraphPartitioner()
    
    # Generate e-commerce network
    print("\n🏗️ Generating Indian e-commerce network...")
    partitioner.generate_ecommerce_network(
        num_customers=2000,   # 2K customers for demo
        num_products=1000,    # 1K products
        num_sellers=200       # 200 sellers
    )
    
    print(f"✅ E-commerce network generated!")
    print(f"   • Total Nodes: {partitioner.graph.number_of_nodes():,}")
    print(f"   • Total Edges: {partitioner.graph.number_of_edges():,}")
    print(f"   • Network Density: {nx.density(partitioner.graph):.6f}")
    
    # Compare different partitioning algorithms
    print("\n⚖️ Comparing partitioning algorithms...")
    comparison_results = partitioner.compare_partitioning_algorithms(num_partitions=4)
    
    # Generate comprehensive report
    print(f"\n📋 PARTITIONING ANALYSIS REPORT:")
    print("=" * 50)
    
    report = partitioner.generate_partitioning_report(comparison_results)
    print(report)
    
    # Visualize best partition
    if comparison_results:
        # Choose algorithm with minimum cross-partition edges for visualization
        best_algo = min(comparison_results.items(), 
                       key=lambda x: x[1]['cross_partition_edges'])
        
        print(f"\n📊 Creating visualization for best algorithm: {best_algo[0]}")
        
        try:
            # Run the best algorithm to get partitions for visualization
            if best_algo[0] == 'Geographic':
                partitions = partitioner.partition_graph_geographic(4)
            elif best_algo[0] == 'Load-balanced':
                partitions = partitioner.partition_graph_load_balanced(4)
            else:  # METIS-style
                partitions = partitioner.partition_graph_metis_style(4)
            
            viz_path = f"/tmp/ecommerce_graph_partitions_{best_algo[0].lower().replace('-', '_')}.png"
            partitioner.visualize_partitions(partitions, best_algo[0], viz_path)
            print(f"✅ Partition visualization saved to: {viz_path}")
            
        except Exception as e:
            print(f"⚠️ Visualization failed: {e}")
    
    # Performance characteristics
    print(f"\n⚡ PERFORMANCE CHARACTERISTICS:")
    print("-" * 35)
    performance_data = [
        ("Small Graph", "10K nodes, 50K edges", "< 5 seconds", "Single machine"),
        ("Medium Graph", "100K nodes, 1M edges", "30-60 seconds", "Workstation"),
        ("Large Graph", "1M nodes, 10M edges", "5-15 minutes", "Server cluster"),
        ("E-commerce Scale", "10M nodes, 100M edges", "1-2 hours", "Distributed system")
    ]
    
    for scale, graph_size, time_estimate, hardware in performance_data:
        print(f"\n🎯 {scale}:")
        print(f"   • Graph Size: {graph_size}")
        print(f"   • Partitioning Time: {time_estimate}")
        print(f"   • Recommended Hardware: {hardware}")
    
    # Real-world applications
    print(f"\n🚀 REAL-WORLD APPLICATIONS:")
    print("-" * 30)
    applications = [
        "🛒 E-commerce: Distributed product catalogs and recommendations",
        "📱 Social Networks: User data distribution across data centers",
        "💳 Fintech: Transaction processing load balancing",
        "🚗 Ride Sharing: Geographic route optimization",
        "📺 Streaming: Content distribution networks",
        "🏥 Healthcare: Patient data regional compliance",
        "🎓 Education: Student-course assignment optimization"
    ]
    
    for app in applications:
        print(f"   {app}")


if __name__ == "__main__":
    # Graph partitioning demo
    run_graph_partitioning_demo()
    
    print("\n" + "="*60)
    print("📚 LEARNING POINTS:")
    print("• Graph partitioning distributed systems mein load balancing ke liye critical hai")
    print("• Different algorithms different use cases ke liye optimize hai")
    print("• Cross-partition communication minimize karna performance ke liye important hai")
    print("• Geographic partitioning Indian e-commerce mein latency reduce karta hai")
    print("• Production systems mein dynamic re-partitioning capabilities essential hai")
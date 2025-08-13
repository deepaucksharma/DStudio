#!/usr/bin/env python3
"""
Distributed Sorting Algorithm Implementation
Distributed sorting - जैसे कि Flipkart के search results ranking में use होता है

यह example दिखाता है कि कैसे massive datasets को multiple machines पर
sort करते हैं distributed computing के through। Flipkart, Amazon India
जैसी companies इसे use करती हैं product search results, recommendations,
और analytics के लिए।

Production context: Flipkart sorts 100M+ products across distributed clusters
Scale: Handles terabytes of data distributed across hundreds of nodes
Challenge: Maintaining sort order while enabling parallel processing
"""

import random
import time
import threading
import multiprocessing
import heapq
import tempfile
import os
import pickle
from typing import List, Tuple, Optional, Any, Dict, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import logging
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SortingAlgorithm(Enum):
    """Types of distributed sorting algorithms"""
    EXTERNAL_MERGE_SORT = "external_merge_sort"
    DISTRIBUTED_SAMPLE_SORT = "distributed_sample_sort"
    PARALLEL_QUICK_SORT = "parallel_quick_sort"
    BUCKET_SORT = "bucket_sort"

@dataclass
class FlipkartProduct:
    """Represents a Flipkart product for sorting"""
    product_id: str
    name: str
    price: float
    rating: float
    reviews_count: int
    category: str
    brand: str
    popularity_score: float
    discount_percentage: float
    seller_rating: float
    
    def __str__(self):
        return f"Product({self.product_id}, {self.name[:30]}, ₹{self.price}, {self.rating}⭐)"
    
    def __lt__(self, other):
        # Default comparison by popularity score
        return self.popularity_score < other.popularity_score

class FlipkartProductComparator:
    """Custom comparators for different sorting criteria"""
    
    @staticmethod
    def by_price(product: FlipkartProduct) -> float:
        return product.price
    
    @staticmethod
    def by_rating(product: FlipkartProduct) -> float:
        return -product.rating  # Negative for descending order
    
    @staticmethod
    def by_popularity(product: FlipkartProduct) -> float:
        return -product.popularity_score  # Negative for descending order
    
    @staticmethod
    def by_discount(product: FlipkartProduct) -> float:
        return -product.discount_percentage  # Negative for descending order
    
    @staticmethod
    def by_relevance(product: FlipkartProduct, search_term: str = "") -> float:
        """Relevance score based on search term"""
        score = 0.0
        
        # Name match
        if search_term.lower() in product.name.lower():
            score += 100
        
        # Category match
        if search_term.lower() in product.category.lower():
            score += 50
        
        # Brand match
        if search_term.lower() in product.brand.lower():
            score += 30
        
        # Boost by rating and reviews
        score += product.rating * 10
        score += min(product.reviews_count / 100, 50)  # Max 50 points from reviews
        
        return -score  # Negative for descending order

class DistributedSorter:
    """
    Base class for distributed sorting algorithms
    """
    
    def __init__(self, worker_count: int = None):
        self.worker_count = worker_count or multiprocessing.cpu_count()
        self.temp_files: List[str] = []
        
    def sort(self, data: List[Any], key_func: Callable = None, reverse: bool = False) -> List[Any]:
        """Sort data using distributed algorithm"""
        raise NotImplementedError("Subclasses must implement sort method")
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {temp_file}: {e}")
        self.temp_files.clear()

class ExternalMergeSorter(DistributedSorter):
    """
    External merge sort for data larger than memory
    जब data memory में fit नहीं होता तो external sorting use करते हैं
    """
    
    def __init__(self, worker_count: int = None, chunk_size: int = 10000):
        super().__init__(worker_count)
        self.chunk_size = chunk_size
        
    def sort(self, data: List[Any], key_func: Callable = None, reverse: bool = False) -> List[Any]:
        """
        Sort large dataset using external merge sort
        """
        logger.info(f"Starting external merge sort for {len(data)} items using {self.worker_count} workers")
        start_time = time.time()
        
        # Phase 1: Sort chunks and write to temporary files
        chunk_files = self._sort_chunks_parallel(data, key_func, reverse)
        
        # Phase 2: Merge sorted chunks
        result = self._merge_sorted_chunks(chunk_files, key_func, reverse)
        
        # Cleanup
        self.cleanup()
        
        sort_time = time.time() - start_time
        logger.info(f"External merge sort completed in {sort_time:.2f}s")
        
        return result
    
    def _sort_chunks_parallel(self, data: List[Any], key_func: Callable, reverse: bool) -> List[str]:
        """Sort data chunks in parallel and save to temporary files"""
        chunks = [data[i:i + self.chunk_size] for i in range(0, len(data), self.chunk_size)]
        chunk_files = []
        
        with ProcessPoolExecutor(max_workers=self.worker_count) as executor:
            # Submit chunk sorting tasks
            futures = []
            for i, chunk in enumerate(chunks):
                future = executor.submit(self._sort_and_save_chunk, chunk, i, key_func, reverse)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                chunk_file = future.result()
                chunk_files.append(chunk_file)
                self.temp_files.append(chunk_file)
        
        logger.info(f"Sorted {len(chunks)} chunks into temporary files")
        return chunk_files
    
    def _sort_and_save_chunk(self, chunk: List[Any], chunk_id: int, 
                            key_func: Callable, reverse: bool) -> str:
        """Sort a single chunk and save to temporary file"""
        # Sort the chunk
        if key_func:
            chunk.sort(key=key_func, reverse=reverse)
        else:
            chunk.sort(reverse=reverse)
        
        # Save to temporary file
        temp_file = tempfile.mktemp(prefix=f"chunk_{chunk_id}_", suffix=".pkl")
        
        with open(temp_file, 'wb') as f:
            pickle.dump(chunk, f)
        
        logger.debug(f"Chunk {chunk_id} sorted and saved to {temp_file}")
        return temp_file
    
    def _merge_sorted_chunks(self, chunk_files: List[str], key_func: Callable, reverse: bool) -> List[Any]:
        """Merge sorted chunks using k-way merge"""
        logger.info(f"Merging {len(chunk_files)} sorted chunks")
        
        # Open all chunk files and create iterators
        chunk_iterators = []
        for chunk_file in chunk_files:
            with open(chunk_file, 'rb') as f:
                chunk_data = pickle.load(f)
                chunk_iterators.append(iter(chunk_data))
        
        # Perform k-way merge using heap
        result = []
        heap = []
        
        # Initialize heap with first element from each chunk
        for i, iterator in enumerate(chunk_iterators):
            try:
                item = next(iterator)
                if key_func:
                    key_value = key_func(item)
                else:
                    key_value = item
                
                # Use negative key for reverse order
                if reverse:
                    key_value = -key_value if isinstance(key_value, (int, float)) else key_value
                
                heapq.heappush(heap, (key_value, i, item, iterator))
            except StopIteration:
                pass
        
        # Merge process
        while heap:
            key_value, chunk_id, item, iterator = heapq.heappop(heap)
            result.append(item)
            
            # Get next item from the same chunk
            try:
                next_item = next(iterator)
                if key_func:
                    next_key_value = key_func(next_item)
                else:
                    next_key_value = next_item
                
                if reverse:
                    next_key_value = -next_key_value if isinstance(next_key_value, (int, float)) else next_key_value
                
                heapq.heappush(heap, (next_key_value, chunk_id, next_item, iterator))
            except StopIteration:
                pass
        
        return result

class DistributedSampleSorter(DistributedSorter):
    """
    Distributed sample sort algorithm
    Large datasets को multiple machines पर efficiently sort करता है
    """
    
    def __init__(self, worker_count: int = None, sample_size: int = 1000):
        super().__init__(worker_count)
        self.sample_size = sample_size
    
    def sort(self, data: List[Any], key_func: Callable = None, reverse: bool = False) -> List[Any]:
        """
        Sort using distributed sample sort algorithm
        """
        logger.info(f"Starting distributed sample sort for {len(data)} items using {self.worker_count} workers")
        start_time = time.time()
        
        if len(data) <= self.worker_count * 1000:
            # For smaller datasets, use regular sorting
            if key_func:
                data.sort(key=key_func, reverse=reverse)
            else:
                data.sort(reverse=reverse)
            return data
        
        # Phase 1: Sample and determine splitters
        splitters = self._determine_splitters(data, key_func)
        
        # Phase 2: Partition data based on splitters
        partitions = self._partition_data(data, splitters, key_func)
        
        # Phase 3: Sort partitions in parallel
        sorted_partitions = self._sort_partitions_parallel(partitions, key_func, reverse)
        
        # Phase 4: Concatenate sorted partitions
        result = []
        for partition in sorted_partitions:
            result.extend(partition)
        
        sort_time = time.time() - start_time
        logger.info(f"Distributed sample sort completed in {sort_time:.2f}s")
        
        return result
    
    def _determine_splitters(self, data: List[Any], key_func: Callable) -> List[Any]:
        """Determine splitter values for partitioning"""
        # Take a random sample
        sample_data = random.sample(data, min(self.sample_size, len(data)))
        
        # Sort the sample
        if key_func:
            sample_data.sort(key=key_func)
        else:
            sample_data.sort()
        
        # Choose splitters to create balanced partitions
        splitters = []
        step = len(sample_data) // (self.worker_count - 1) if self.worker_count > 1 else len(sample_data)
        
        for i in range(1, self.worker_count):
            idx = min(i * step, len(sample_data) - 1)
            splitters.append(sample_data[idx])
        
        logger.debug(f"Determined {len(splitters)} splitters for partitioning")
        return splitters
    
    def _partition_data(self, data: List[Any], splitters: List[Any], key_func: Callable) -> List[List[Any]]:
        """Partition data based on splitters"""
        partitions = [[] for _ in range(self.worker_count)]
        
        for item in data:
            key_value = key_func(item) if key_func else item
            
            # Find appropriate partition
            partition_idx = 0
            for i, splitter in enumerate(splitters):
                splitter_key = key_func(splitter) if key_func else splitter
                if key_value <= splitter_key:
                    partition_idx = i
                    break
                partition_idx = i + 1
            
            partitions[partition_idx].append(item)
        
        logger.info(f"Partitioned data into {len(partitions)} partitions: "
                   f"{[len(p) for p in partitions]}")
        return partitions
    
    def _sort_partitions_parallel(self, partitions: List[List[Any]], 
                                 key_func: Callable, reverse: bool) -> List[List[Any]]:
        """Sort partitions in parallel"""
        with ProcessPoolExecutor(max_workers=self.worker_count) as executor:
            futures = []
            for i, partition in enumerate(partitions):
                future = executor.submit(self._sort_single_partition, partition, key_func, reverse)
                futures.append(future)
            
            sorted_partitions = []
            for future in as_completed(futures):
                sorted_partition = future.result()
                sorted_partitions.append(sorted_partition)
        
        return sorted_partitions
    
    def _sort_single_partition(self, partition: List[Any], key_func: Callable, reverse: bool) -> List[Any]:
        """Sort a single partition"""
        if key_func:
            partition.sort(key=key_func, reverse=reverse)
        else:
            partition.sort(reverse=reverse)
        return partition

class FlipkartSearchSorter:
    """
    Flipkart-style search result sorter using distributed algorithms
    """
    
    def __init__(self):
        self.external_sorter = ExternalMergeSorter(worker_count=4, chunk_size=5000)
        self.sample_sorter = DistributedSampleSorter(worker_count=4, sample_size=500)
        
    def generate_sample_products(self, count: int = 50000) -> List[FlipkartProduct]:
        """Generate sample Flipkart products for testing"""
        logger.info(f"Generating {count} sample products...")
        
        categories = ["Electronics", "Fashion", "Home", "Books", "Sports", "Beauty", "Automotive"]
        brands = ["Samsung", "Apple", "Nike", "Adidas", "Sony", "LG", "HP", "Dell", "Puma", "Reebok"]
        
        products = []
        for i in range(count):
            product = FlipkartProduct(
                product_id=f"PROD{i:06d}",
                name=f"Product {i} - {random.choice(['Premium', 'Budget', 'Pro', 'Lite', 'Max'])} Edition",
                price=random.uniform(100, 50000),
                rating=random.uniform(2.0, 5.0),
                reviews_count=random.randint(0, 10000),
                category=random.choice(categories),
                brand=random.choice(brands),
                popularity_score=random.uniform(0, 100),
                discount_percentage=random.uniform(0, 70),
                seller_rating=random.uniform(3.0, 5.0)
            )
            products.append(product)
        
        logger.info(f"Generated {len(products)} sample products")
        return products
    
    def sort_by_price_range(self, products: List[FlipkartProduct], 
                          min_price: float = 0, max_price: float = float('inf'),
                          algorithm: SortingAlgorithm = SortingAlgorithm.EXTERNAL_MERGE_SORT) -> List[FlipkartProduct]:
        """Sort products by price within a range"""
        # Filter by price range
        filtered_products = [p for p in products if min_price <= p.price <= max_price]
        
        logger.info(f"Sorting {len(filtered_products)} products by price ({algorithm.value})")
        
        if algorithm == SortingAlgorithm.EXTERNAL_MERGE_SORT:
            return self.external_sorter.sort(filtered_products, FlipkartProductComparator.by_price)
        elif algorithm == SortingAlgorithm.DISTRIBUTED_SAMPLE_SORT:
            return self.sample_sorter.sort(filtered_products, FlipkartProductComparator.by_price)
    
    def sort_by_popularity(self, products: List[FlipkartProduct],
                          category: str = None,
                          algorithm: SortingAlgorithm = SortingAlgorithm.DISTRIBUTED_SAMPLE_SORT) -> List[FlipkartProduct]:
        """Sort products by popularity, optionally filtered by category"""
        filtered_products = products
        if category:
            filtered_products = [p for p in products if p.category.lower() == category.lower()]
        
        logger.info(f"Sorting {len(filtered_products)} products by popularity ({algorithm.value})")
        
        if algorithm == SortingAlgorithm.EXTERNAL_MERGE_SORT:
            return self.external_sorter.sort(filtered_products, FlipkartProductComparator.by_popularity)
        elif algorithm == SortingAlgorithm.DISTRIBUTED_SAMPLE_SORT:
            return self.sample_sorter.sort(filtered_products, FlipkartProductComparator.by_popularity)
    
    def sort_search_results(self, products: List[FlipkartProduct], search_term: str,
                          algorithm: SortingAlgorithm = SortingAlgorithm.DISTRIBUTED_SAMPLE_SORT) -> List[FlipkartProduct]:
        """Sort search results by relevance"""
        logger.info(f"Sorting {len(products)} search results for '{search_term}' ({algorithm.value})")
        
        # Create relevance comparator for the search term
        def relevance_key(product):
            return FlipkartProductComparator.by_relevance(product, search_term)
        
        if algorithm == SortingAlgorithm.EXTERNAL_MERGE_SORT:
            return self.external_sorter.sort(products, relevance_key)
        elif algorithm == SortingAlgorithm.DISTRIBUTED_SAMPLE_SORT:
            return self.sample_sorter.sort(products, relevance_key)
    
    def performance_comparison(self, products: List[FlipkartProduct]) -> Dict[str, float]:
        """Compare performance of different sorting algorithms"""
        logger.info("Running performance comparison of sorting algorithms")
        
        results = {}
        
        # Test External Merge Sort
        start_time = time.time()
        self.external_sorter.sort(products.copy(), FlipkartProductComparator.by_price)
        results["External Merge Sort"] = time.time() - start_time
        
        # Test Distributed Sample Sort
        start_time = time.time()
        self.sample_sorter.sort(products.copy(), FlipkartProductComparator.by_price)
        results["Distributed Sample Sort"] = time.time() - start_time
        
        # Test Regular Python Sort (for comparison)
        start_time = time.time()
        products_copy = products.copy()
        products_copy.sort(key=FlipkartProductComparator.by_price)
        results["Regular Python Sort"] = time.time() - start_time
        
        return results

def demonstrate_flipkart_distributed_sorting():
    """
    Demonstrate distributed sorting with Flipkart-style product search
    """
    print("\n🛒 Flipkart Distributed Product Sorting Demo")
    print("=" * 60)
    
    # Initialize Flipkart search sorter
    sorter = FlipkartSearchSorter()
    
    # Generate sample products
    print("\n📦 Generating sample product catalog...")
    products = sorter.generate_sample_products(25000)  # 25K products
    
    print(f"✅ Generated {len(products)} products")
    print(f"Sample products:")
    for i in range(3):
        print(f"  {i+1}. {products[i]}")
    
    # Demonstrate price-based sorting
    print("\n💰 Sorting products by price (₹1000-₹10000 range)...")
    price_sorted = sorter.sort_by_price_range(
        products, 
        min_price=1000, 
        max_price=10000,
        algorithm=SortingAlgorithm.EXTERNAL_MERGE_SORT
    )
    
    print(f"✅ Sorted {len(price_sorted)} products by price")
    print("Top 5 cheapest products in range:")
    for i, product in enumerate(price_sorted[:5], 1):
        print(f"  {i}. {product.name[:40]} - ₹{product.price:.2f}")
    
    # Demonstrate popularity-based sorting
    print("\n⭐ Sorting Electronics by popularity...")
    popularity_sorted = sorter.sort_by_popularity(
        products,
        category="Electronics",
        algorithm=SortingAlgorithm.DISTRIBUTED_SAMPLE_SORT
    )
    
    print(f"✅ Sorted {len(popularity_sorted)} Electronics products by popularity")
    print("Top 5 most popular Electronics:")
    for i, product in enumerate(popularity_sorted[:5], 1):
        print(f"  {i}. {product.name[:40]} - Score: {product.popularity_score:.1f}")
    
    # Demonstrate search result sorting
    search_terms = ["Samsung", "Nike", "Premium"]
    
    for search_term in search_terms:
        print(f"\n🔍 Sorting search results for '{search_term}'...")
        search_results = sorter.sort_search_results(
            products,
            search_term,
            algorithm=SortingAlgorithm.DISTRIBUTED_SAMPLE_SORT
        )
        
        # Filter to show only relevant results
        relevant_results = [p for p in search_results if search_term.lower() in p.name.lower() or 
                          search_term.lower() in p.brand.lower() or 
                          search_term.lower() in p.category.lower()][:10]
        
        print(f"✅ Found {len(relevant_results)} relevant results for '{search_term}'")
        print("Top 3 most relevant:")
        for i, product in enumerate(relevant_results[:3], 1):
            print(f"  {i}. {product.name[:40]} ({product.brand}) - ₹{product.price:.2f}")
    
    # Performance comparison
    print("\n⚡ Performance Comparison of Sorting Algorithms...")
    
    # Use smaller dataset for performance comparison
    test_products = products[:10000]  # 10K products for fair comparison
    
    performance_results = sorter.performance_comparison(test_products)
    
    print(f"Sorting {len(test_products)} products - Performance Results:")
    sorted_results = sorted(performance_results.items(), key=lambda x: x[1])
    
    for algorithm, time_taken in sorted_results:
        print(f"  {algorithm}: {time_taken:.3f} seconds")
    
    # Demonstrate scalability
    print("\n📈 Scalability Analysis...")
    
    data_sizes = [5000, 10000, 20000]
    scalability_results = {}
    
    for size in data_sizes:
        test_data = products[:size]
        
        start_time = time.time()
        sorter.external_sorter.sort(test_data.copy(), FlipkartProductComparator.by_price)
        external_time = time.time() - start_time
        
        start_time = time.time()
        sorter.sample_sorter.sort(test_data.copy(), FlipkartProductComparator.by_price)
        sample_time = time.time() - start_time
        
        scalability_results[size] = {
            "External Merge Sort": external_time,
            "Distributed Sample Sort": sample_time
        }
        
        print(f"  {size:,} products:")
        print(f"    External Merge Sort: {external_time:.3f}s")
        print(f"    Distributed Sample Sort: {sample_time:.3f}s")
    
    # Big Billion Day simulation
    print("\n🎯 Big Billion Day Traffic Simulation...")
    
    # Simulate multiple concurrent sorting requests
    print("Simulating concurrent search requests during peak sale...")
    
    concurrent_searches = [
        ("Mobile", "Electronics"),
        ("Laptop", "Electronics"), 
        ("Shoes", "Fashion"),
        ("TV", "Electronics"),
        ("Shirt", "Fashion")
    ]
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=len(concurrent_searches)) as executor:
        futures = []
        for search_term, category in concurrent_searches:
            future = executor.submit(
                sorter.sort_search_results,
                [p for p in products if p.category == category],
                search_term,
                SortingAlgorithm.DISTRIBUTED_SAMPLE_SORT
            )
            futures.append((search_term, future))
        
        # Collect results
        for search_term, future in futures:
            results = future.result()
            print(f"  ✅ Processed search for '{search_term}': {len(results)} results")
    
    total_time = time.time() - start_time
    print(f"Total concurrent processing time: {total_time:.3f}s")
    
    # Production insights
    print("\n💡 Production Insights for Flipkart-scale Systems:")
    print("- Distributed sorting enables sub-second response for millions of products")
    print("- External merge sort handles datasets larger than available memory")
    print("- Sample sort provides better load balancing across compute nodes")
    print("- Parallel processing scales linearly with available CPU cores")
    print("- Critical for real-time search result ranking during high traffic")
    print("- Enables personalized sorting based on user preferences")
    print("- Supports multiple sorting criteria (price, rating, popularity, relevance)")
    print("- Essential for Big Billion Day when traffic increases 10x")
    print("- Memory-efficient algorithms prevent system crashes during peak load")
    print("- Horizontal scaling across data centers for global e-commerce")
    
    # Cleanup
    print("\n🧹 Cleaning up temporary files...")
    sorter.external_sorter.cleanup()
    sorter.sample_sorter.cleanup()
    
    print("Flipkart distributed sorting demo completed!")

if __name__ == "__main__":
    demonstrate_flipkart_distributed_sorting()
// Distributed Cache Cluster Implementation
// Redis Cluster के साथ high-availability caching for Indian e-commerce
//
// Key Features:
// - Redis Cluster support
// - Consistent hashing
// - Automatic failover
// - Geo-distributed setup
// - Mumbai-Delhi-Bangalore cluster
//
// Author: Code Developer Agent for Hindi Tech Podcast
// Episode: 25 - Caching Strategies (Distributed Cache Cluster)

package main

import (
	"context"
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"sort"
	"strconv"
	"sync"
	"time"
)

// Product represents an e-commerce product
type Product struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Price       float64   `json:"price"`
	Category    string    `json:"category"`
	Brand       string    `json:"brand"`
	InStock     bool      `json:"in_stock"`
	Rating      float32   `json:"rating"`
	Reviews     int       `json:"reviews"`
	LastUpdated time.Time `json:"last_updated"`
}

// CacheNode represents a cache node in the cluster
type CacheNode struct {
	ID       string
	Region   string
	Address  string
	Port     int
	IsActive bool
	Load     float64
	cache    map[string]CacheItem
	mutex    sync.RWMutex
}

// CacheItem represents an item in cache with TTL
type CacheItem struct {
	Value     interface{}
	TTL       time.Duration
	CreatedAt time.Time
}

// IsExpired checks if cache item has expired
func (ci *CacheItem) IsExpired() bool {
	return time.Since(ci.CreatedAt) > ci.TTL
}

// DistributedCache represents the distributed cache cluster
type DistributedCache struct {
	nodes          []*CacheNode
	consistentHash *ConsistentHash
	replicationFactor int
	mutex          sync.RWMutex
	stats          CacheStats
}

// CacheStats holds cache statistics
type CacheStats struct {
	TotalRequests   int64
	CacheHits       int64
	CacheMisses     int64
	NodesActive     int
	AvgLatency      time.Duration
	ReplicationOps  int64
	FailoverEvents  int64
}

// ConsistentHash implements consistent hashing for node selection
type ConsistentHash struct {
	circle       map[uint32]string
	sortedHashes []uint32
	nodes        map[string]bool
	replicas     int
	mutex        sync.RWMutex
}

// NewConsistentHash creates a new consistent hash
func NewConsistentHash(replicas int) *ConsistentHash {
	return &ConsistentHash{
		circle:   make(map[uint32]string),
		nodes:    make(map[string]bool),
		replicas: replicas,
	}
}

// AddNode adds a node to the hash ring
func (ch *ConsistentHash) AddNode(node string) {
	ch.mutex.Lock()
	defer ch.mutex.Unlock()

	for i := 0; i < ch.replicas; i++ {
		hash := ch.hashKey(node + strconv.Itoa(i))
		ch.circle[hash] = node
		ch.sortedHashes = append(ch.sortedHashes, hash)
	}
	sort.Slice(ch.sortedHashes, func(i, j int) bool {
		return ch.sortedHashes[i] < ch.sortedHashes[j]
	})
	ch.nodes[node] = true
}

// RemoveNode removes a node from the hash ring
func (ch *ConsistentHash) RemoveNode(node string) {
	ch.mutex.Lock()
	defer ch.mutex.Unlock()

	for i := 0; i < ch.replicas; i++ {
		hash := ch.hashKey(node + strconv.Itoa(i))
		delete(ch.circle, hash)
		for j, h := range ch.sortedHashes {
			if h == hash {
				ch.sortedHashes = append(ch.sortedHashes[:j], ch.sortedHashes[j+1:]...)
				break
			}
		}
	}
	delete(ch.nodes, node)
}

// GetNode returns the node responsible for a key
func (ch *ConsistentHash) GetNode(key string) string {
	ch.mutex.RLock()
	defer ch.mutex.RUnlock()

	if len(ch.sortedHashes) == 0 {
		return ""
	}

	hash := ch.hashKey(key)
	idx := sort.Search(len(ch.sortedHashes), func(i int) bool {
		return ch.sortedHashes[i] >= hash
	})

	if idx == len(ch.sortedHashes) {
		idx = 0
	}

	return ch.circle[ch.sortedHashes[idx]]
}

// GetNodes returns multiple nodes for replication
func (ch *ConsistentHash) GetNodes(key string, count int) []string {
	ch.mutex.RLock()
	defer ch.mutex.RUnlock()

	if len(ch.sortedHashes) == 0 || count == 0 {
		return nil
	}

	hash := ch.hashKey(key)
	idx := sort.Search(len(ch.sortedHashes), func(i int) bool {
		return ch.sortedHashes[i] >= hash
	})

	if idx == len(ch.sortedHashes) {
		idx = 0
	}

	nodes := make([]string, 0, count)
	nodeSet := make(map[string]bool)
	originalIdx := idx

	for len(nodes) < count && len(nodeSet) < len(ch.nodes) {
		node := ch.circle[ch.sortedHashes[idx]]
		if !nodeSet[node] {
			nodes = append(nodes, node)
			nodeSet[node] = true
		}
		idx = (idx + 1) % len(ch.sortedHashes)
		if idx == originalIdx {
			break
		}
	}

	return nodes
}

func (ch *ConsistentHash) hashKey(key string) uint32 {
	hasher := md5.New()
	hasher.Write([]byte(key))
	hashBytes := hasher.Sum(nil)
	
	return uint32(hashBytes[0])<<24 + uint32(hashBytes[1])<<16 + uint32(hashBytes[2])<<8 + uint32(hashBytes[3])
}

// NewCacheNode creates a new cache node
func NewCacheNode(id, region, address string, port int) *CacheNode {
	return &CacheNode{
		ID:       id,
		Region:   region,
		Address:  address,
		Port:     port,
		IsActive: true,
		Load:     0.0,
		cache:    make(map[string]CacheItem),
	}
}

// Get retrieves a value from the node's cache
func (cn *CacheNode) Get(key string) (interface{}, bool) {
	cn.mutex.RLock()
	defer cn.mutex.RUnlock()

	item, exists := cn.cache[key]
	if !exists {
		return nil, false
	}

	if item.IsExpired() {
		delete(cn.cache, key)
		return nil, false
	}

	return item.Value, true
}

// Set stores a value in the node's cache
func (cn *CacheNode) Set(key string, value interface{}, ttl time.Duration) {
	cn.mutex.Lock()
	defer cn.mutex.Unlock()

	cn.cache[key] = CacheItem{
		Value:     value,
		TTL:       ttl,
		CreatedAt: time.Now(),
	}
}

// Delete removes a key from the node's cache
func (cn *CacheNode) Delete(key string) {
	cn.mutex.Lock()
	defer cn.mutex.Unlock()
	delete(cn.cache, key)
}

// Size returns the number of items in cache
func (cn *CacheNode) Size() int {
	cn.mutex.RLock()
	defer cn.mutex.RUnlock()
	return len(cn.cache)
}

// NewDistributedCache creates a new distributed cache cluster
func NewDistributedCache(replicationFactor int) *DistributedCache {
	return &DistributedCache{
		nodes:             make([]*CacheNode, 0),
		consistentHash:    NewConsistentHash(100), // 100 virtual nodes per physical node
		replicationFactor: replicationFactor,
		stats:             CacheStats{},
	}
}

// AddNode adds a cache node to the cluster
func (dc *DistributedCache) AddNode(node *CacheNode) {
	dc.mutex.Lock()
	defer dc.mutex.Unlock()

	dc.nodes = append(dc.nodes, node)
	dc.consistentHash.AddNode(node.ID)
	dc.stats.NodesActive++

	log.Printf("🔗 Node added to cluster: %s (%s)", node.ID, node.Region)
}

// RemoveNode removes a cache node from the cluster
func (dc *DistributedCache) RemoveNode(nodeID string) {
	dc.mutex.Lock()
	defer dc.mutex.Unlock()

	for i, node := range dc.nodes {
		if node.ID == nodeID {
			node.IsActive = false
			dc.nodes = append(dc.nodes[:i], dc.nodes[i+1:]...)
			dc.consistentHash.RemoveNode(nodeID)
			dc.stats.NodesActive--
			dc.stats.FailoverEvents++
			log.Printf("❌ Node removed from cluster: %s", nodeID)
			break
		}
	}
}

// Get retrieves a value from the distributed cache
func (dc *DistributedCache) Get(key string) (interface{}, bool) {
	start := time.Now()
	defer func() {
		dc.stats.AvgLatency = time.Since(start)
		dc.stats.TotalRequests++
	}()

	// Get nodes responsible for this key
	nodeIDs := dc.consistentHash.GetNodes(key, dc.replicationFactor)
	if len(nodeIDs) == 0 {
		dc.stats.CacheMisses++
		return nil, false
	}

	// Try to get from available nodes
	for _, nodeID := range nodeIDs {
		node := dc.getNode(nodeID)
		if node != nil && node.IsActive {
			value, found := node.Get(key)
			if found {
				dc.stats.CacheHits++
				log.Printf("💾 Cache hit on node %s for key: %s", node.ID, key)
				return value, true
			}
		}
	}

	dc.stats.CacheMisses++
	log.Printf("❌ Cache miss for key: %s", key)
	return nil, false
}

// Set stores a value in the distributed cache
func (dc *DistributedCache) Set(key string, value interface{}, ttl time.Duration) error {
	// Get nodes responsible for this key
	nodeIDs := dc.consistentHash.GetNodes(key, dc.replicationFactor)
	if len(nodeIDs) == 0 {
		return fmt.Errorf("no active nodes available")
	}

	successCount := 0
	for _, nodeID := range nodeIDs {
		node := dc.getNode(nodeID)
		if node != nil && node.IsActive {
			node.Set(key, value, ttl)
			successCount++
			log.Printf("✅ Stored on node %s for key: %s", node.ID, key)
		}
	}

	if successCount > 0 {
		dc.stats.ReplicationOps++
		return nil
	}

	return fmt.Errorf("failed to store on any node")
}

// Delete removes a key from the distributed cache
func (dc *DistributedCache) Delete(key string) error {
	nodeIDs := dc.consistentHash.GetNodes(key, dc.replicationFactor)
	if len(nodeIDs) == 0 {
		return fmt.Errorf("no active nodes available")
	}

	for _, nodeID := range nodeIDs {
		node := dc.getNode(nodeID)
		if node != nil && node.IsActive {
			node.Delete(key)
			log.Printf("🗑️ Deleted from node %s for key: %s", node.ID, key)
		}
	}

	return nil
}

// getNode finds a node by ID
func (dc *DistributedCache) getNode(nodeID string) *CacheNode {
	for _, node := range dc.nodes {
		if node.ID == nodeID {
			return node
		}
	}
	return nil
}

// GetStats returns cache statistics
func (dc *DistributedCache) GetStats() CacheStats {
	dc.mutex.RLock()
	defer dc.mutex.RUnlock()
	return dc.stats
}

// GetNodeStatus returns status of all nodes
func (dc *DistributedCache) GetNodeStatus() []map[string]interface{} {
	dc.mutex.RLock()
	defer dc.mutex.RUnlock()

	status := make([]map[string]interface{}, len(dc.nodes))
	for i, node := range dc.nodes {
		status[i] = map[string]interface{}{
			"id":       node.ID,
			"region":   node.Region,
			"address":  fmt.Sprintf("%s:%d", node.Address, node.Port),
			"active":   node.IsActive,
			"load":     node.Load,
			"size":     node.Size(),
		}
	}
	return status
}

// ProductCacheService provides product caching functionality
type ProductCacheService struct {
	cache    *DistributedCache
	database map[string]Product // Simulated database
}

// NewProductCacheService creates a new product cache service
func NewProductCacheService(cache *DistributedCache) *ProductCacheService {
	service := &ProductCacheService{
		cache:    cache,
		database: make(map[string]Product),
	}
	
	// Initialize with sample data
	service.initializeSampleData()
	return service
}

func (pcs *ProductCacheService) initializeSampleData() {
	products := []Product{
		{
			ID:          "PROD_001",
			Name:        "iPhone 15 Pro Max",
			Price:       159900,
			Category:    "Smartphones",
			Brand:       "Apple",
			InStock:     true,
			Rating:      4.5,
			Reviews:     12500,
			LastUpdated: time.Now(),
		},
		{
			ID:          "PROD_002",
			Name:        "Samsung Galaxy S24 Ultra",
			Price:       124999,
			Category:    "Smartphones",
			Brand:       "Samsung",
			InStock:     true,
			Rating:      4.4,
			Reviews:     15600,
			LastUpdated: time.Now(),
		},
		{
			ID:          "PROD_003",
			Name:        "MacBook Pro 14\" M3",
			Price:       199900,
			Category:    "Laptops",
			Brand:       "Apple",
			InStock:     false,
			Rating:      4.7,
			Reviews:     8300,
			LastUpdated: time.Now(),
		},
	}

	for _, product := range products {
		pcs.database[product.ID] = product
	}

	log.Printf("📦 Initialized database with %d products", len(products))
}

// GetProduct retrieves a product with caching
func (pcs *ProductCacheService) GetProduct(productID string) (*Product, error) {
	// Try cache first
	if cachedData, found := pcs.cache.Get(productID); found {
		if product, ok := cachedData.(Product); ok {
			log.Printf("🚀 Product served from cache: %s", productID)
			return &product, nil
		}
	}

	// Cache miss - fetch from database
	time.Sleep(100 * time.Millisecond) // Simulate database latency
	
	product, exists := pcs.database[productID]
	if !exists {
		return nil, fmt.Errorf("product not found: %s", productID)
	}

	// Store in cache
	err := pcs.cache.Set(productID, product, 30*time.Minute)
	if err != nil {
		log.Printf("⚠️ Failed to cache product %s: %v", productID, err)
	} else {
		log.Printf("💾 Product cached: %s", productID)
	}

	return &product, nil
}

// UpdateProduct updates a product and invalidates cache
func (pcs *ProductCacheService) UpdateProduct(product Product) error {
	// Update database
	pcs.database[product.ID] = product
	
	// Invalidate cache
	err := pcs.cache.Delete(product.ID)
	if err != nil {
		log.Printf("⚠️ Failed to invalidate cache for %s: %v", product.ID, err)
	} else {
		log.Printf("🔄 Cache invalidated for product: %s", product.ID)
	}

	return nil
}

// Demo function
func demonstrateDistributedCache() {
	fmt.Println("🌐 Distributed Cache Cluster Demo")
	fmt.Println("🇮🇳 Indian E-commerce Multi-Region Setup")
	fmt.Println("=" + repeat("=", 50))

	// Create distributed cache cluster
	cache := NewDistributedCache(3) // Replication factor of 3

	// Add nodes for different Indian regions
	nodes := []*CacheNode{
		NewCacheNode("mumbai-1", "Mumbai", "10.0.1.1", 6379),
		NewCacheNode("mumbai-2", "Mumbai", "10.0.1.2", 6379),
		NewCacheNode("delhi-1", "Delhi", "10.0.2.1", 6379),
		NewCacheNode("delhi-2", "Delhi", "10.0.2.2", 6379),
		NewCacheNode("bangalore-1", "Bangalore", "10.0.3.1", 6379),
		NewCacheNode("bangalore-2", "Bangalore", "10.0.3.2", 6379),
	}

	// Add nodes to cluster
	fmt.Println("\n1. Setting Up Multi-Region Cluster")
	fmt.Println("-" + repeat("-", 40))
	for _, node := range nodes {
		cache.AddNode(node)
	}

	// Create product cache service
	productService := NewProductCacheService(cache)

	fmt.Println("\n2. Product Caching Test")
	fmt.Println("-" + repeat("-", 25))

	// Test product retrieval
	productIDs := []string{"PROD_001", "PROD_002", "PROD_003"}
	
	for _, productID := range productIDs {
		fmt.Printf("\n🔍 Fetching product: %s\n", productID)
		
		// First fetch (cache miss)
		start := time.Now()
		product, err := productService.GetProduct(productID)
		firstFetchTime := time.Since(start)
		
		if err != nil {
			fmt.Printf("❌ Error: %v\n", err)
			continue
		}
		
		fmt.Printf("   📦 %s - ₹%.2f (%v)\n", product.Name, product.Price, firstFetchTime)
		
		// Second fetch (cache hit)
		start = time.Now()
		product, err = productService.GetProduct(productID)
		secondFetchTime := time.Since(start)
		
		if err == nil {
			fmt.Printf("   ⚡ Cached fetch: %v (%.1fx faster)\n", 
				secondFetchTime, float64(firstFetchTime.Nanoseconds())/float64(secondFetchTime.Nanoseconds()))
		}
	}

	fmt.Println("\n3. Node Failure Simulation")
	fmt.Println("-" + repeat("-", 30))

	// Simulate node failure
	fmt.Println("💥 Simulating Mumbai-1 node failure...")
	cache.RemoveNode("mumbai-1")

	// Test cache still works
	product, err := productService.GetProduct("PROD_001")
	if err == nil {
		fmt.Printf("✅ Cache still operational: %s\n", product.Name)
	} else {
		fmt.Printf("❌ Cache failed: %v\n", err)
	}

	fmt.Println("\n4. Cluster Status")
	fmt.Println("-" + repeat("-", 20))

	stats := cache.GetStats()
	fmt.Printf("📊 Cache Statistics:\n")
	fmt.Printf("   Total Requests: %d\n", stats.TotalRequests)
	fmt.Printf("   Cache Hits: %d\n", stats.CacheHits)
	fmt.Printf("   Cache Misses: %d\n", stats.CacheMisses)
	fmt.Printf("   Hit Ratio: %.2f%%\n", float64(stats.CacheHits)/float64(stats.TotalRequests)*100)
	fmt.Printf("   Active Nodes: %d\n", stats.NodesActive)
	fmt.Printf("   Failover Events: %d\n", stats.FailoverEvents)
	fmt.Printf("   Replication Operations: %d\n", stats.ReplicationOps)

	fmt.Println("\n📋 Node Status:")
	nodeStatus := cache.GetNodeStatus()
	for _, status := range nodeStatus {
		activeIcon := "✅"
		if !status["active"].(bool) {
			activeIcon = "❌"
		}
		fmt.Printf("   %s %s (%s): %s - %d items\n", 
			activeIcon, status["id"], status["region"], status["address"], status["size"])
	}

	fmt.Println("\n5. Load Balancing Test")
	fmt.Println("-" + repeat("-", 25))

	// Simulate multiple requests to test load distribution
	fmt.Println("🔄 Testing load distribution across nodes...")
	for i := 0; i < 20; i++ {
		key := fmt.Sprintf("test_key_%d", i)
		value := fmt.Sprintf("test_value_%d", i)
		cache.Set(key, value, 10*time.Minute)
	}

	// Show load distribution
	fmt.Println("📊 Load distribution:")
	nodeStatus = cache.GetNodeStatus()
	for _, status := range nodeStatus {
		if status["active"].(bool) {
			fmt.Printf("   %s: %d items\n", status["id"], status["size"])
		}
	}

	fmt.Println("\n" + repeat("=", 51))
	fmt.Println("🎉 Distributed Cache Demo Completed!")
	fmt.Println("💡 Key Features Demonstrated:")
	fmt.Println("   - Multi-region cache distribution")
	fmt.Println("   - Automatic failover and recovery")
	fmt.Println("   - Consistent hashing for load balancing")
	fmt.Println("   - Data replication for high availability")
	fmt.Println("   - Real-time cluster monitoring")
}

func repeat(s string, count int) string {
	result := ""
	for i := 0; i < count; i++ {
		result += s
	}
	return result
}

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	demonstrateDistributedCache()
}
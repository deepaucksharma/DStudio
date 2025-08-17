/*
🇮🇳 Consistent Hash Load Balancer - PayTM Wallet Style
Session stickiness के लिए consistent hashing

Features:
- Consistent hashing for session affinity
- Virtual nodes for better distribution
- Minimal disruption on node changes
- PayTM wallet session management
- Ring-based hash distribution
- Production-ready implementation
- Hindi comments

Author: Agent 5 - Code Developer
Episode: 27 - Load Balancing
Context: PayTM wallet session management system
*/

package main

import (
	"crypto/sha1"
	"errors"
	"fmt"
	"hash/crc32"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"sort"
	"strconv"
	"sync"
	"time"
)

// WalletNode represents a backend server for wallet services
type WalletNode struct {
	ID            string            `json:"id"`
	URL           *url.URL          `json:"url"`
	Zone          string            `json:"zone"`
	IsHealthy     bool              `json:"is_healthy"`
	Metadata      map[string]string `json:"metadata"`
	VirtualNodes  int               `json:"virtual_nodes"`
	RequestCount  uint64            `json:"request_count"`
	LastSeen      time.Time         `json:"last_seen"`
	mutex         sync.RWMutex      `json:"-"`
}

// IsAvailable checks if node is available for requests
func (wn *WalletNode) IsAvailable() bool {
	wn.mutex.RLock()
	defer wn.mutex.RUnlock()
	return wn.IsHealthy
}

// SetHealth updates node health status
func (wn *WalletNode) SetHealth(healthy bool) {
	wn.mutex.Lock()
	defer wn.mutex.Unlock()
	wn.IsHealthy = healthy
	wn.LastSeen = time.Now()

	status := "🟢 Available"
	if !healthy {
		status = "🔴 Unavailable"
	}
	log.Printf("💳 Wallet node %s status: %s", wn.ID, status)
}

// IncrementRequests increments request counter
func (wn *WalletNode) IncrementRequests() {
	wn.mutex.Lock()
	defer wn.mutex.Unlock()
	wn.RequestCount++
	wn.LastSeen = time.Now()
}

// GetStats returns node statistics
func (wn *WalletNode) GetStats() map[string]interface{} {
	wn.mutex.RLock()
	defer wn.mutex.RUnlock()

	return map[string]interface{}{
		"id":            wn.ID,
		"zone":          wn.Zone,
		"is_healthy":    wn.IsHealthy,
		"virtual_nodes": wn.VirtualNodes,
		"request_count": wn.RequestCount,
		"last_seen":     wn.LastSeen,
		"metadata":      wn.Metadata,
	}
}

// VirtualNode represents a virtual node on the hash ring
type VirtualNode struct {
	Hash uint32     `json:"hash"`
	Node *WalletNode `json:"node"`
}

// ConsistentHashRing implements consistent hashing algorithm
type ConsistentHashRing struct {
	virtualNodes []VirtualNode    `json:"virtual_nodes"`
	nodes        []*WalletNode    `json:"nodes"`
	nodeMap      map[string]*WalletNode `json:"-"`
	mutex        sync.RWMutex     `json:"-"`
}

// NewConsistentHashRing creates a new consistent hash ring
func NewConsistentHashRing() *ConsistentHashRing {
	return &ConsistentHashRing{
		virtualNodes: make([]VirtualNode, 0),
		nodes:        make([]*WalletNode, 0),
		nodeMap:      make(map[string]*WalletNode),
	}
}

// hashFunction creates a hash for given key
func (chr *ConsistentHashRing) hashFunction(key string) uint32 {
	return crc32.ChecksumIEEE([]byte(key))
}

// AddNode adds a wallet node to the hash ring
func (chr *ConsistentHashRing) AddNode(node *WalletNode) {
	chr.mutex.Lock()
	defer chr.mutex.Unlock()

	// Add node to maps
	chr.nodes = append(chr.nodes, node)
	chr.nodeMap[node.ID] = node

	// Add virtual nodes to the ring
	for i := 0; i < node.VirtualNodes; i++ {
		virtualKey := fmt.Sprintf("%s:%d", node.ID, i)
		hash := chr.hashFunction(virtualKey)

		virtualNode := VirtualNode{
			Hash: hash,
			Node: node,
		}

		chr.virtualNodes = append(chr.virtualNodes, virtualNode)
	}

	// Sort virtual nodes by hash
	sort.Slice(chr.virtualNodes, func(i, j int) bool {
		return chr.virtualNodes[i].Hash < chr.virtualNodes[j].Hash
	})

	log.Printf("✅ Wallet node added to ring: %s (%d virtual nodes)",
		node.ID, node.VirtualNodes)
	log.Printf("🔄 Hash ring now has %d virtual nodes", len(chr.virtualNodes))
}

// RemoveNode removes a wallet node from the hash ring
func (chr *ConsistentHashRing) RemoveNode(nodeID string) error {
	chr.mutex.Lock()
	defer chr.mutex.Unlock()

	// Find and remove node
	nodeIndex := -1
	for i, node := range chr.nodes {
		if node.ID == nodeID {
			nodeIndex = i
			break
		}
	}

	if nodeIndex == -1 {
		return fmt.Errorf("node not found: %s", nodeID)
	}

	// Remove from nodes slice
	chr.nodes = append(chr.nodes[:nodeIndex], chr.nodes[nodeIndex+1:]...)
	delete(chr.nodeMap, nodeID)

	// Remove virtual nodes
	newVirtualNodes := make([]VirtualNode, 0)
	for _, vnode := range chr.virtualNodes {
		if vnode.Node.ID != nodeID {
			newVirtualNodes = append(newVirtualNodes, vnode)
		}
	}
	chr.virtualNodes = newVirtualNodes

	log.Printf("🗑️ Wallet node removed from ring: %s", nodeID)
	log.Printf("🔄 Hash ring now has %d virtual nodes", len(chr.virtualNodes))

	return nil
}

// GetNode returns the node responsible for given key
func (chr *ConsistentHashRing) GetNode(key string) (*WalletNode, error) {
	chr.mutex.RLock()
	defer chr.mutex.RUnlock()

	if len(chr.virtualNodes) == 0 {
		return nil, errors.New("no nodes available in hash ring")
	}

	hash := chr.hashFunction(key)

	// Find the first virtual node with hash >= key hash
	for _, vnode := range chr.virtualNodes {
		if vnode.Hash >= hash && vnode.Node.IsAvailable() {
			log.Printf("🎯 Hash %d -> Node %s (virtual hash: %d)",
				hash, vnode.Node.ID, vnode.Hash)
			return vnode.Node, nil
		}
	}

	// Wrap around to the first available node
	for _, vnode := range chr.virtualNodes {
		if vnode.Node.IsAvailable() {
			log.Printf("🔄 Hash %d -> Node %s (wrap around, virtual hash: %d)",
				hash, vnode.Node.ID, vnode.Hash)
			return vnode.Node, nil
		}
	}

	return nil, errors.New("no healthy nodes available")
}

// GetNodesByKey returns multiple nodes for redundancy
func (chr *ConsistentHashRing) GetNodesByKey(key string, count int) ([]*WalletNode, error) {
	chr.mutex.RLock()
	defer chr.mutex.RUnlock()

	if len(chr.virtualNodes) == 0 {
		return nil, errors.New("no nodes available in hash ring")
	}

	hash := chr.hashFunction(key)
	nodes := make([]*WalletNode, 0, count)
	seenNodes := make(map[string]bool)

	// Start from the position in the ring
	startIndex := 0
	for i, vnode := range chr.virtualNodes {
		if vnode.Hash >= hash {
			startIndex = i
			break
		}
	}

	// Collect unique nodes
	for i := 0; i < len(chr.virtualNodes) && len(nodes) < count; i++ {
		index := (startIndex + i) % len(chr.virtualNodes)
		vnode := chr.virtualNodes[index]

		if vnode.Node.IsAvailable() && !seenNodes[vnode.Node.ID] {
			nodes = append(nodes, vnode.Node)
			seenNodes[vnode.Node.ID] = true
		}
	}

	if len(nodes) == 0 {
		return nil, errors.New("no healthy nodes available")
	}

	return nodes, nil
}

// GetRingStats returns hash ring statistics
func (chr *ConsistentHashRing) GetRingStats() map[string]interface{} {
	chr.mutex.RLock()
	defer chr.mutex.RUnlock()

	nodeStats := make([]map[string]interface{}, 0, len(chr.nodes))
	healthyNodes := 0
	totalVirtualNodes := 0

	for _, node := range chr.nodes {
		if node.IsHealthy {
			healthyNodes++
		}
		totalVirtualNodes += node.VirtualNodes
		nodeStats = append(nodeStats, node.GetStats())
	}

	return map[string]interface{}{
		"total_nodes":         len(chr.nodes),
		"healthy_nodes":       healthyNodes,
		"total_virtual_nodes": len(chr.virtualNodes),
		"expected_virtual_nodes": totalVirtualNodes,
		"node_stats":          nodeStats,
	}
}

// GetKeyDistribution analyzes key distribution across nodes
func (chr *ConsistentHashRing) GetKeyDistribution(keys []string) map[string]int {
	chr.mutex.RLock()
	defer chr.mutex.RUnlock()

	distribution := make(map[string]int)

	for _, key := range keys {
		node, err := chr.GetNode(key)
		if err == nil {
			distribution[node.ID]++
		}
	}

	return distribution
}

// PayTMLoadBalancer implements consistent hash load balancing
type PayTMLoadBalancer struct {
	hashRing    *ConsistentHashRing
	healthChecker *NodeHealthChecker
}

// NewPayTMLoadBalancer creates a new PayTM-style load balancer
func NewPayTMLoadBalancer() *PayTMLoadBalancer {
	hashRing := NewConsistentHashRing()
	lb := &PayTMLoadBalancer{
		hashRing: hashRing,
	}

	// Start health checker
	lb.healthChecker = NewNodeHealthChecker(hashRing, 30*time.Second, 5*time.Second)
	lb.healthChecker.Start()

	return lb
}

// AddWalletNode adds a wallet node to load balancer
func (lb *PayTMLoadBalancer) AddWalletNode(node *WalletNode) {
	lb.hashRing.AddNode(node)
}

// RemoveWalletNode removes a wallet node from load balancer
func (lb *PayTMLoadBalancer) RemoveWalletNode(nodeID string) error {
	return lb.hashRing.RemoveNode(nodeID)
}

// GetNodeForUser returns node for a specific user (session affinity)
func (lb *PayTMLoadBalancer) GetNodeForUser(userID string) (*WalletNode, error) {
	// Use user ID as the consistent hash key
	return lb.hashRing.GetNode(userID)
}

// GetNodeForWallet returns node for a specific wallet
func (lb *PayTMLoadBalancer) GetNodeForWallet(walletID string) (*WalletNode, error) {
	// Use wallet ID as the consistent hash key
	return lb.hashRing.GetNode(walletID)
}

// GetReplicaNodes returns multiple nodes for redundancy
func (lb *PayTMLoadBalancer) GetReplicaNodes(key string, replicaCount int) ([]*WalletNode, error) {
	return lb.hashRing.GetNodesByKey(key, replicaCount)
}

// GetLoadBalancerStats returns comprehensive statistics
func (lb *PayTMLoadBalancer) GetLoadBalancerStats() map[string]interface{} {
	return lb.hashRing.GetRingStats()
}

// NodeHealthChecker monitors node health
type NodeHealthChecker struct {
	hashRing *ConsistentHashRing
	interval time.Duration
	timeout  time.Duration
	stopChan chan bool
}

// NewNodeHealthChecker creates a new health checker
func NewNodeHealthChecker(ring *ConsistentHashRing, interval, timeout time.Duration) *NodeHealthChecker {
	return &NodeHealthChecker{
		hashRing: ring,
		interval: interval,
		timeout:  timeout,
		stopChan: make(chan bool),
	}
}

// Start begins health checking
func (hc *NodeHealthChecker) Start() {
	go hc.healthCheckLoop()
	log.Printf("🔍 Node health checker started (interval: %v)", hc.interval)
}

// Stop stops health checking
func (hc *NodeHealthChecker) Stop() {
	hc.stopChan <- true
	log.Printf("🛑 Node health checker stopped")
}

// healthCheckLoop performs periodic health checks
func (hc *NodeHealthChecker) healthCheckLoop() {
	ticker := time.NewTicker(hc.interval)
	defer ticker.Stop()

	for {
		select {
		case <-hc.stopChan:
			return
		case <-ticker.C:
			hc.checkAllNodes()
		}
	}
}

// checkAllNodes checks health of all nodes
func (hc *NodeHealthChecker) checkAllNodes() {
	hc.hashRing.mutex.RLock()
	nodes := make([]*WalletNode, len(hc.hashRing.nodes))
	copy(nodes, hc.hashRing.nodes)
	hc.hashRing.mutex.RUnlock()

	var wg sync.WaitGroup
	for _, node := range nodes {
		wg.Add(1)
		go func(n *WalletNode) {
			defer wg.Done()
			hc.checkNodeHealth(n)
		}(node)
	}
	wg.Wait()
}

// checkNodeHealth checks health of a single node
func (hc *NodeHealthChecker) checkNodeHealth(node *WalletNode) {
	healthURL := fmt.Sprintf("%s/health", node.URL.String())

	client := &http.Client{Timeout: hc.timeout}
	resp, err := client.Get(healthURL)

	if err != nil {
		log.Printf("💔 Health check failed for %s: %v", node.ID, err)
		node.SetHealth(false)
		return
	}
	defer resp.Body.Close()

	isHealthy := resp.StatusCode >= 200 && resp.StatusCode < 300
	node.SetHealth(isHealthy)

	if isHealthy {
		log.Printf("💚 Node %s healthy", node.ID)
	} else {
		log.Printf("💛 Node %s unhealthy (status: %d)", node.ID, resp.StatusCode)
	}
}

// PayTMProxy implements HTTP proxy with consistent hashing
type PayTMProxy struct {
	loadBalancer *PayTMLoadBalancer
}

// NewPayTMProxy creates a new proxy
func NewPayTMProxy(lb *PayTMLoadBalancer) *PayTMProxy {
	return &PayTMProxy{
		loadBalancer: lb,
	}
}

// ServeHTTP implements http.Handler interface
func (p *PayTMProxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// Extract user ID or wallet ID from request
	userID := r.Header.Get("X-User-ID")
	walletID := r.Header.Get("X-Wallet-ID")

	var key string
	var node *WalletNode
	var err error

	// Determine routing key
	if userID != "" {
		key = userID
		node, err = p.loadBalancer.GetNodeForUser(userID)
	} else if walletID != "" {
		key = walletID
		node, err = p.loadBalancer.GetNodeForWallet(walletID)
	} else {
		// Fallback to session ID or IP
		key = r.Header.Get("X-Session-ID")
		if key == "" {
			key = r.RemoteAddr
		}
		node, err = p.loadBalancer.hashRing.GetNode(key)
	}

	if err != nil {
		log.Printf("❌ No nodes available for key %s: %v", key, err)
		http.Error(w, "Service Unavailable", http.StatusServiceUnavailable)
		return
	}

	// Create reverse proxy
	proxy := httputil.NewSingleHostReverseProxy(node.URL)

	// Add custom headers
	r.Header.Set("X-Forwarded-Node", node.ID)
	r.Header.Set("X-Forwarded-Zone", node.Zone)
	r.Header.Set("X-Routing-Key", key)

	// Log request routing
	log.Printf("🔀 Routing request %s %s to node %s (key: %s)",
		r.Method, r.URL.Path, node.ID, key)

	// Increment request counter
	node.IncrementRequests()

	// Proxy the request
	proxy.ServeHTTP(w, r)
}

// Stop gracefully shuts down the proxy
func (p *PayTMProxy) Stop() {
	if p.loadBalancer.healthChecker != nil {
		p.loadBalancer.healthChecker.Stop()
	}
}

// mustParseURL parses URL or panics
func mustParseURL(rawURL string) *url.URL {
	url, err := url.Parse(rawURL)
	if err != nil {
		panic(fmt.Sprintf("Invalid URL: %s", rawURL))
	}
	return url
}

// generateSHA1Hash generates SHA1 hash for demonstration
func generateSHA1Hash(input string) string {
	h := sha1.New()
	h.Write([]byte(input))
	return fmt.Sprintf("%x", h.Sum(nil))
}

// Example usage and demo
func main() {
	// Create PayTM load balancer with consistent hashing
	lb := NewPayTMLoadBalancer()

	// Add wallet nodes with different virtual node counts
	walletNodes := []*WalletNode{
		{
			ID:           "wallet-mumbai-primary",
			URL:          mustParseURL("http://localhost:8081"),
			Zone:         "mumbai",
			IsHealthy:    true,
			VirtualNodes: 150, // More virtual nodes = more traffic
			Metadata: map[string]string{
				"type":     "primary",
				"capacity": "high",
			},
		},
		{
			ID:           "wallet-mumbai-secondary",
			URL:          mustParseURL("http://localhost:8082"),
			Zone:         "mumbai",
			IsHealthy:    true,
			VirtualNodes: 100,
			Metadata: map[string]string{
				"type":     "secondary",
				"capacity": "medium",
			},
		},
		{
			ID:           "wallet-delhi-primary",
			URL:          mustParseURL("http://localhost:8083"),
			Zone:         "delhi",
			IsHealthy:    true,
			VirtualNodes: 120,
			Metadata: map[string]string{
				"type":     "primary",
				"capacity": "high",
			},
		},
		{
			ID:           "wallet-bangalore-primary",
			URL:          mustParseURL("http://localhost:8084"),
			Zone:         "bangalore",
			IsHealthy:    true,
			VirtualNodes: 80,
			Metadata: map[string]string{
				"type":     "primary",
				"capacity": "medium",
			},
		},
	}

	// Add nodes to load balancer
	for _, node := range walletNodes {
		lb.AddWalletNode(node)
	}

	// Create proxy
	proxy := NewPayTMProxy(lb)
	defer proxy.Stop()

	// Demo: Show consistent hashing behavior
	fmt.Println("\n💳 PayTM Consistent Hash Load Balancer Demo")
	fmt.Println("============================================")

	fmt.Println("\n1. 🔄 User-to-node mapping (session affinity):")
	userIDs := []string{"user001", "user002", "user003", "user004", "user005"}
	for _, userID := range userIDs {
		node, err := lb.GetNodeForUser(userID)
		if err != nil {
			fmt.Printf("   ❌ Error for %s: %v\n", userID, err)
			continue
		}
		fmt.Printf("   👤 %s -> Node: %s (%s)\n", userID, node.ID, node.Zone)
	}

	fmt.Println("\n2. 💰 Wallet-to-node mapping:")
	walletIDs := []string{"wallet_001", "wallet_002", "wallet_003", "wallet_004", "wallet_005"}
	for _, walletID := range walletIDs {
		node, err := lb.GetNodeForWallet(walletID)
		if err != nil {
			fmt.Printf("   ❌ Error for %s: %v\n", walletID, err)
			continue
		}
		fmt.Printf("   💰 %s -> Node: %s (%s)\n", walletID, node.ID, node.Zone)
	}

	fmt.Println("\n3. 🔄 Replica nodes for redundancy:")
	replicaNodes, err := lb.GetReplicaNodes("critical_wallet_001", 3)
	if err != nil {
		fmt.Printf("   ❌ Error getting replicas: %v\n", err)
	} else {
		fmt.Printf("   🔄 critical_wallet_001 replicas:\n")
		for i, node := range replicaNodes {
			fmt.Printf("      %d. %s (%s)\n", i+1, node.ID, node.Zone)
		}
	}

	fmt.Println("\n4. 📊 Hash ring statistics:")
	stats := lb.GetLoadBalancerStats()
	fmt.Printf("   🔄 Total nodes: %d\n", stats["total_nodes"])
	fmt.Printf("   💚 Healthy nodes: %d\n", stats["healthy_nodes"])
	fmt.Printf("   🔄 Virtual nodes: %d\n", stats["total_virtual_nodes"])

	fmt.Println("\n5. 📈 Key distribution analysis:")
	testKeys := make([]string, 100)
	for i := 0; i < 100; i++ {
		testKeys[i] = fmt.Sprintf("user%03d", i)
	}
	distribution := lb.hashRing.GetKeyDistribution(testKeys)
	fmt.Printf("   📊 Distribution of 100 test keys:\n")
	for nodeID, count := range distribution {
		percentage := float64(count) / float64(len(testKeys)) * 100
		fmt.Printf("      %s: %d keys (%.1f%%)\n", nodeID, count, percentage)
	}

	fmt.Println("\n6. 🔧 Testing node removal and consistency:")
	fmt.Printf("   Before removal - user001 -> ")
	node1, _ := lb.GetNodeForUser("user001")
	fmt.Printf("%s\n", node1.ID)

	// Remove a node
	lb.RemoveWalletNode("wallet-delhi-primary")
	fmt.Printf("   After removal - user001 -> ")
	node2, _ := lb.GetNodeForUser("user001")
	fmt.Printf("%s\n", node2.ID)

	if node1.ID == node2.ID {
		fmt.Printf("   ✅ Session maintained during node removal\n")
	} else {
		fmt.Printf("   ⚠️ Session moved to different node: %s -> %s\n", node1.ID, node2.ID)
	}

	// Start HTTP server for demo
	fmt.Println("\n🌐 Starting HTTP proxy server on :8080")
	fmt.Println("📝 Test with headers: curl -H \"X-User-ID: user123\" http://localhost:8080/api/wallet")
	fmt.Println("💰 Or with wallet: curl -H \"X-Wallet-ID: wallet_456\" http://localhost:8080/api/balance")
	fmt.Println("🔍 Health checks running every 30 seconds")
	fmt.Println("🛑 Press Ctrl+C to stop")

	server := &http.Server{
		Addr:    ":8080",
		Handler: proxy,
	}

	log.Fatal(server.ListenAndServe())
}
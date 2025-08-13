/*
Concurrent Graph Algorithms for High-Performance Analytics
Production-grade parallel graph processing for Indian scale systems

Author: Episode 10 - Graph Analytics at Scale  
Context: Concurrent graph algorithms - multi-goroutine processing for scalability
*/

package main

import (
	"context"
	"fmt"
	"log"
	"math"
	"math/rand"
	"runtime"
	"sort"
	"strings"
	"sync"
	"time"
)

// Graph data structures
type Node struct {
	ID         string                 `json:"id"`
	Label      string                 `json:"label"`
	Properties map[string]interface{} `json:"properties"`
}

type Edge struct {
	From       string                 `json:"from"`
	To         string                 `json:"to"`
	Weight     float64                `json:"weight"`
	Properties map[string]interface{} `json:"properties"`
}

type Graph struct {
	Nodes       map[string]*Node              `json:"nodes"`
	Edges       map[string]map[string]*Edge   `json:"edges"` // from_id -> to_id -> edge
	mutex       sync.RWMutex
	directed    bool
	nodeCount   int
	edgeCount   int
}

// Algorithm results
type PageRankResult struct {
	NodeID string  `json:"node_id"`
	Score  float64 `json:"score"`
}

type CentralityResult struct {
	NodeID              string  `json:"node_id"`
	BetweennessCentrality float64 `json:"betweenness_centrality"`
	ClosenessCentrality   float64 `json:"closeness_centrality"`
	DegreeCentrality      float64 `json:"degree_centrality"`
}

type CommunityResult struct {
	CommunityID int      `json:"community_id"`
	Members     []string `json:"members"`
	Size        int      `json:"size"`
}

// Concurrent Graph Analytics Engine
type ConcurrentGraphAnalytics struct {
	graph           *Graph
	workerPoolSize  int
	resultChannels  map[string]chan interface{}
	ctx             context.Context
	cancel          context.CancelFunc
	performanceStats map[string]time.Duration
	mutex           sync.RWMutex
}

// Initialize graph analytics engine
func NewConcurrentGraphAnalytics(directed bool, workerPoolSize int) *ConcurrentGraphAnalytics {
	if workerPoolSize <= 0 {
		workerPoolSize = runtime.NumCPU()
	}
	
	ctx, cancel := context.WithCancel(context.Background())
	
	return &ConcurrentGraphAnalytics{
		graph: &Graph{
			Nodes:    make(map[string]*Node),
			Edges:    make(map[string]map[string]*Edge),
			directed: directed,
		},
		workerPoolSize:   workerPoolSize,
		resultChannels:   make(map[string]chan interface{}),
		ctx:              ctx,
		cancel:           cancel,
		performanceStats: make(map[string]time.Duration),
	}
}

// Add node to graph (thread-safe)
func (cga *ConcurrentGraphAnalytics) AddNode(node *Node) {
	cga.graph.mutex.Lock()
	defer cga.graph.mutex.Unlock()
	
	cga.graph.Nodes[node.ID] = node
	cga.graph.nodeCount++
}

// Add edge to graph (thread-safe)
func (cga *ConcurrentGraphAnalytics) AddEdge(edge *Edge) {
	cga.graph.mutex.Lock()
	defer cga.graph.mutex.Unlock()
	
	// Ensure from node exists in adjacency list
	if cga.graph.Edges[edge.From] == nil {
		cga.graph.Edges[edge.From] = make(map[string]*Edge)
	}
	
	cga.graph.Edges[edge.From][edge.To] = edge
	cga.graph.edgeCount++
	
	// Add reverse edge for undirected graphs
	if !cga.graph.directed {
		if cga.graph.Edges[edge.To] == nil {
			cga.graph.Edges[edge.To] = make(map[string]*Edge)
		}
		
		reverseEdge := &Edge{
			From:   edge.To,
			To:     edge.From,
			Weight: edge.Weight,
			Properties: edge.Properties,
		}
		cga.graph.Edges[edge.To][edge.From] = reverseEdge
	}
}

// Concurrent PageRank implementation
func (cga *ConcurrentGraphAnalytics) ComputePageRankConcurrent(dampingFactor float64, maxIterations int, tolerance float64) ([]PageRankResult, error) {
	start := time.Now()
	defer func() {
		cga.mutex.Lock()
		cga.performanceStats["PageRank"] = time.Since(start)
		cga.mutex.Unlock()
	}()
	
	log.Println("Starting concurrent PageRank computation...")
	
	nodeIDs := cga.getNodeIDs()
	nodeCount := len(nodeIDs)
	
	if nodeCount == 0 {
		return nil, fmt.Errorf("graph has no nodes")
	}
	
	// Initialize PageRank scores
	currentScores := make(map[string]float64)
	newScores := make(map[string]float64)
	
	initialScore := 1.0 / float64(nodeCount)
	for _, nodeID := range nodeIDs {
		currentScores[nodeID] = initialScore
	}
	
	// Worker function for PageRank computation
	worker := func(nodeSubset []string, scores map[string]float64, resultChan chan map[string]float64) {
		localScores := make(map[string]float64)
		
		for _, nodeID := range nodeSubset {
			localScores[nodeID] = (1.0-dampingFactor)/float64(nodeCount) + cga.computeNodePageRank(nodeID, scores, dampingFactor)
		}
		
		resultChan <- localScores
	}
	
	// Run PageRank iterations
	for iteration := 0; iteration < maxIterations; iteration++ {
		// Divide nodes among workers
		nodeSubsets := cga.divideNodesAmongWorkers(nodeIDs, cga.workerPoolSize)
		resultChan := make(chan map[string]float64, cga.workerPoolSize)
		
		// Launch workers
		for _, subset := range nodeSubsets {
			go worker(subset, currentScores, resultChan)
		}
		
		// Collect results
		for i := 0; i < len(nodeSubsets); i++ {
			partialScores := <-resultChan
			for nodeID, score := range partialScores {
				newScores[nodeID] = score
			}
		}
		close(resultChan)
		
		// Check convergence
		if cga.hasConverged(currentScores, newScores, tolerance) {
			log.Printf("PageRank converged after %d iterations", iteration+1)
			break
		}
		
		// Swap scores for next iteration
		currentScores, newScores = newScores, currentScores
		
		// Clear newScores for next iteration
		for k := range newScores {
			delete(newScores, k)
		}
	}
	
	// Prepare results
	results := make([]PageRankResult, 0, nodeCount)
	for nodeID, score := range currentScores {
		results = append(results, PageRankResult{
			NodeID: nodeID,
			Score:  score,
		})
	}
	
	// Sort by score (descending)
	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})
	
	log.Printf("PageRank computation completed for %d nodes", nodeCount)
	return results, nil
}

// Compute PageRank contribution for a single node
func (cga *ConcurrentGraphAnalytics) computeNodePageRank(nodeID string, scores map[string]float64, dampingFactor float64) float64 {
	cga.graph.mutex.RLock()
	defer cga.graph.mutex.RUnlock()
	
	sum := 0.0
	
	// Find all nodes that link to this node
	for fromNodeID, edges := range cga.graph.Edges {
		if _, exists := edges[nodeID]; exists {
			// Get out-degree of fromNode
			outDegree := len(cga.graph.Edges[fromNodeID])
			if outDegree > 0 {
				sum += scores[fromNodeID] / float64(outDegree)
			}
		}
	}
	
	return dampingFactor * sum
}

// Concurrent Betweenness Centrality computation
func (cga *ConcurrentGraphAnalytics) ComputeBetweennessCentralityConcurrent() ([]CentralityResult, error) {
	start := time.Now()
	defer func() {
		cga.mutex.Lock()
		cga.performanceStats["BetweennessCentrality"] = time.Since(start)
		cga.mutex.Unlock()
	}()
	
	log.Println("Starting concurrent betweenness centrality computation...")
	
	nodeIDs := cga.getNodeIDs()
	nodeCount := len(nodeIDs)
	
	if nodeCount == 0 {
		return nil, fmt.Errorf("graph has no nodes")
	}
	
	// Initialize centrality scores
	betweennessCentrality := make(map[string]float64)
	for _, nodeID := range nodeIDs {
		betweennessCentrality[nodeID] = 0.0
	}
	
	// Mutex for thread-safe updates to centrality scores
	var centralityMutex sync.Mutex
	
	// Worker function for betweenness centrality
	worker := func(sourceNodes []string, wg *sync.WaitGroup) {
		defer wg.Done()
		
		localCentrality := make(map[string]float64)
		for _, nodeID := range nodeIDs {
			localCentrality[nodeID] = 0.0
		}
		
		for _, sourceNode := range sourceNodes {
			// Compute shortest paths from source node
			paths := cga.computeAllShortestPaths(sourceNode)
			
			// Calculate betweenness contribution
			for targetNode, pathInfo := range paths {
				if sourceNode != targetNode {
					for _, intermediateNode := range pathInfo.IntermediateNodes {
						if intermediateNode != sourceNode && intermediateNode != targetNode {
							localCentrality[intermediateNode] += 1.0 / float64(pathInfo.PathCount)
						}
					}
				}
			}
		}
		
		// Update global centrality scores (thread-safe)
		centralityMutex.Lock()
		for nodeID, contribution := range localCentrality {
			betweennessCentrality[nodeID] += contribution
		}
		centralityMutex.Unlock()
	}
	
	// Divide source nodes among workers
	sourceNodeSubsets := cga.divideNodesAmongWorkers(nodeIDs, cga.workerPoolSize)
	
	var wg sync.WaitGroup
	for _, subset := range sourceNodeSubsets {
		wg.Add(1)
		go worker(subset, &wg)
	}
	
	wg.Wait()
	
	// Normalize betweenness centrality scores
	normalizationFactor := 1.0
	if nodeCount > 2 {
		if cga.graph.directed {
			normalizationFactor = 1.0 / float64((nodeCount-1)*(nodeCount-2))
		} else {
			normalizationFactor = 2.0 / float64((nodeCount-1)*(nodeCount-2))
		}
	}
	
	// Compute other centrality measures and prepare results
	results := make([]CentralityResult, 0, nodeCount)
	for _, nodeID := range nodeIDs {
		degreeCentrality := float64(cga.getDegree(nodeID)) / float64(nodeCount-1)
		
		results = append(results, CentralityResult{
			NodeID:                nodeID,
			BetweennessCentrality: betweennessCentrality[nodeID] * normalizationFactor,
			ClosenessCentrality:   cga.computeClosenessCentrality(nodeID),
			DegreeCentrality:      degreeCentrality,
		})
	}
	
	// Sort by betweenness centrality (descending)
	sort.Slice(results, func(i, j int) bool {
		return results[i].BetweennessCentrality > results[j].BetweennessCentrality
	})
	
	log.Printf("Betweenness centrality computation completed for %d nodes", nodeCount)
	return results, nil
}

// Path information for shortest path computation
type PathInfo struct {
	Distance          int
	PathCount         int
	IntermediateNodes []string
}

// Compute all shortest paths from a source node using BFS
func (cga *ConcurrentGraphAnalytics) computeAllShortestPaths(sourceNode string) map[string]PathInfo {
	cga.graph.mutex.RLock()
	defer cga.graph.mutex.RUnlock()
	
	paths := make(map[string]PathInfo)
	visited := make(map[string]bool)
	queue := []string{sourceNode}
	distances := make(map[string]int)
	predecessors := make(map[string][]string)
	
	distances[sourceNode] = 0
	visited[sourceNode] = true
	
	// BFS to find shortest paths
	for len(queue) > 0 {
		currentNode := queue[0]
		queue = queue[1:]
		
		currentDistance := distances[currentNode]
		
		// Explore neighbors
		if neighbors, exists := cga.graph.Edges[currentNode]; exists {
			for neighborNode := range neighbors {
				if !visited[neighborNode] {
					visited[neighborNode] = true
					distances[neighborNode] = currentDistance + 1
					predecessors[neighborNode] = []string{currentNode}
					queue = append(queue, neighborNode)
				} else if distances[neighborNode] == currentDistance+1 {
					// Found another shortest path
					predecessors[neighborNode] = append(predecessors[neighborNode], currentNode)
				}
			}
		}
	}
	
	// Reconstruct paths and count them
	for targetNode, distance := range distances {
		if sourceNode != targetNode {
			pathCount := cga.countPaths(sourceNode, targetNode, predecessors)
			intermediateNodes := cga.getIntermediateNodes(sourceNode, targetNode, predecessors)
			
			paths[targetNode] = PathInfo{
				Distance:          distance,
				PathCount:         pathCount,
				IntermediateNodes: intermediateNodes,
			}
		}
	}
	
	return paths
}

// Count number of shortest paths between source and target
func (cga *ConcurrentGraphAnalytics) countPaths(source, target string, predecessors map[string][]string) int {
	if source == target {
		return 1
	}
	
	if preds, exists := predecessors[target]; exists {
		count := 0
		for _, pred := range preds {
			count += cga.countPaths(source, pred, predecessors)
		}
		return count
	}
	
	return 0
}

// Get intermediate nodes in shortest paths
func (cga *ConcurrentGraphAnalytics) getIntermediateNodes(source, target string, predecessors map[string][]string) []string {
	intermediates := make(map[string]bool)
	
	var dfs func(current string)
	dfs = func(current string) {
		if current == source {
			return
		}
		
		if preds, exists := predecessors[current]; exists {
			for _, pred := range preds {
				if pred != source {
					intermediates[pred] = true
				}
				dfs(pred)
			}
		}
	}
	
	dfs(target)
	
	result := make([]string, 0, len(intermediates))
	for node := range intermediates {
		result = append(result, node)
	}
	
	return result
}

// Concurrent Community Detection using Label Propagation
func (cga *ConcurrentGraphAnalytics) DetectCommunitiesConcurrent(maxIterations int) ([]CommunityResult, error) {
	start := time.Now()
	defer func() {
		cga.mutex.Lock()
		cga.performanceStats["CommunityDetection"] = time.Since(start)
		cga.mutex.Unlock()
	}()
	
	log.Println("Starting concurrent community detection...")
	
	nodeIDs := cga.getNodeIDs()
	nodeCount := len(nodeIDs)
	
	if nodeCount == 0 {
		return nil, fmt.Errorf("graph has no nodes")
	}
	
	// Initialize each node with its own label
	labels := make(map[string]string)
	for _, nodeID := range nodeIDs {
		labels[nodeID] = nodeID
	}
	
	// Worker function for label propagation
	worker := func(nodeSubset []string, currentLabels map[string]string, resultChan chan map[string]string) {
		newLabels := make(map[string]string)
		
		for _, nodeID := range nodeSubset {
			// Count neighbor labels
			neighborLabels := make(map[string]int)
			
			cga.graph.mutex.RLock()
			if neighbors, exists := cga.graph.Edges[nodeID]; exists {
				for neighborID := range neighbors {
					if label, exists := currentLabels[neighborID]; exists {
						neighborLabels[label]++
					}
				}
			}
			cga.graph.mutex.RUnlock()
			
			// Find most frequent label among neighbors
			if len(neighborLabels) > 0 {
				maxCount := 0
				mostFrequentLabel := currentLabels[nodeID]
				
				for label, count := range neighborLabels {
					if count > maxCount {
						maxCount = count
						mostFrequentLabel = label
					}
				}
				
				newLabels[nodeID] = mostFrequentLabel
			} else {
				newLabels[nodeID] = currentLabels[nodeID]
			}
		}
		
		resultChan <- newLabels
	}
	
	// Run label propagation iterations
	for iteration := 0; iteration < maxIterations; iteration++ {
		// Shuffle nodes for random order processing
		shuffledNodes := make([]string, len(nodeIDs))
		copy(shuffledNodes, nodeIDs)
		rand.Shuffle(len(shuffledNodes), func(i, j int) {
			shuffledNodes[i], shuffledNodes[j] = shuffledNodes[j], shuffledNodes[i]
		})
		
		// Divide nodes among workers
		nodeSubsets := cga.divideNodesAmongWorkers(shuffledNodes, cga.workerPoolSize)
		resultChan := make(chan map[string]string, cga.workerPoolSize)
		
		// Launch workers
		for _, subset := range nodeSubsets {
			go worker(subset, labels, resultChan)
		}
		
		// Collect results
		newLabels := make(map[string]string)
		for i := 0; i < len(nodeSubsets); i++ {
			partialLabels := <-resultChan
			for nodeID, label := range partialLabels {
				newLabels[nodeID] = label
			}
		}
		close(resultChan)
		
		// Check if labels have stabilized
		changed := false
		for nodeID := range labels {
			if labels[nodeID] != newLabels[nodeID] {
				changed = true
				break
			}
		}
		
		labels = newLabels
		
		if !changed {
			log.Printf("Community detection converged after %d iterations", iteration+1)
			break
		}
	}
	
	// Group nodes by community labels
	communities := make(map[string][]string)
	for nodeID, label := range labels {
		communities[label] = append(communities[label], nodeID)
	}
	
	// Prepare results
	results := make([]CommunityResult, 0, len(communities))
	communityID := 0
	for _, members := range communities {
		if len(members) > 1 { // Only include communities with multiple members
			results = append(results, CommunityResult{
				CommunityID: communityID,
				Members:     members,
				Size:        len(members),
			})
			communityID++
		}
	}
	
	// Sort by community size (descending)
	sort.Slice(results, func(i, j int) bool {
		return results[i].Size > results[j].Size
	})
	
	log.Printf("Community detection completed: found %d communities", len(results))
	return results, nil
}

// Helper functions

func (cga *ConcurrentGraphAnalytics) getNodeIDs() []string {
	cga.graph.mutex.RLock()
	defer cga.graph.mutex.RUnlock()
	
	nodeIDs := make([]string, 0, len(cga.graph.Nodes))
	for nodeID := range cga.graph.Nodes {
		nodeIDs = append(nodeIDs, nodeID)
	}
	return nodeIDs
}

func (cga *ConcurrentGraphAnalytics) divideNodesAmongWorkers(nodes []string, workerCount int) [][]string {
	if workerCount <= 0 {
		workerCount = 1
	}
	
	nodeCount := len(nodes)
	if nodeCount == 0 {
		return [][]string{}
	}
	
	if workerCount > nodeCount {
		workerCount = nodeCount
	}
	
	subsets := make([][]string, workerCount)
	nodesPerWorker := nodeCount / workerCount
	remainder := nodeCount % workerCount
	
	startIdx := 0
	for i := 0; i < workerCount; i++ {
		endIdx := startIdx + nodesPerWorker
		if i < remainder {
			endIdx++
		}
		
		subsets[i] = nodes[startIdx:endIdx]
		startIdx = endIdx
	}
	
	return subsets
}

func (cga *ConcurrentGraphAnalytics) hasConverged(oldScores, newScores map[string]float64, tolerance float64) bool {
	for nodeID := range oldScores {
		diff := math.Abs(oldScores[nodeID] - newScores[nodeID])
		if diff > tolerance {
			return false
		}
	}
	return true
}

func (cga *ConcurrentGraphAnalytics) getDegree(nodeID string) int {
	cga.graph.mutex.RLock()
	defer cga.graph.mutex.RUnlock()
	
	degree := 0
	
	// Out-degree
	if neighbors, exists := cga.graph.Edges[nodeID]; exists {
		degree += len(neighbors)
	}
	
	// In-degree (for directed graphs)
	if cga.graph.directed {
		for _, edges := range cga.graph.Edges {
			if _, exists := edges[nodeID]; exists {
				degree++
			}
		}
	}
	
	return degree
}

func (cga *ConcurrentGraphAnalytics) computeClosenessCentrality(nodeID string) float64 {
	// Simplified closeness centrality computation
	// In production, would use proper shortest path algorithms
	totalDistance := 0
	reachableNodes := 0
	
	cga.graph.mutex.RLock()
	nodeCount := len(cga.graph.Nodes)
	cga.graph.mutex.RUnlock()
	
	// BFS to compute distances
	visited := make(map[string]bool)
	queue := []string{nodeID}
	distances := make(map[string]int)
	
	distances[nodeID] = 0
	visited[nodeID] = true
	
	for len(queue) > 0 {
		currentNode := queue[0]
		queue = queue[1:]
		
		currentDistance := distances[currentNode]
		
		cga.graph.mutex.RLock()
		if neighbors, exists := cga.graph.Edges[currentNode]; exists {
			for neighborNode := range neighbors {
				if !visited[neighborNode] {
					visited[neighborNode] = true
					distances[neighborNode] = currentDistance + 1
					totalDistance += currentDistance + 1
					reachableNodes++
					queue = append(queue, neighborNode)
				}
			}
		}
		cga.graph.mutex.RUnlock()
	}
	
	if reachableNodes == 0 {
		return 0.0
	}
	
	// Closeness centrality = (n-1) / sum of distances
	return float64(nodeCount-1) / float64(totalDistance)
}

// Generate demo Indian tech network
func (cga *ConcurrentGraphAnalytics) generateDemoTechNetwork() {
	log.Println("Generating demo Indian tech network...")
	
	// Tech companies and their employees
	companies := map[string][]string{
		"flipkart": {"flipkart_ceo", "flipkart_cto", "flipkart_dev1", "flipkart_dev2", "flipkart_pm"},
		"paytm":    {"paytm_ceo", "paytm_cto", "paytm_dev1", "paytm_dev2", "paytm_analytics"},
		"ola":      {"ola_ceo", "ola_cto", "ola_dev1", "ola_dev2", "ola_data_scientist"},
		"zomato":   {"zomato_ceo", "zomato_cto", "zomato_dev1", "zomato_dev2", "zomato_designer"},
		"byju":     {"byju_ceo", "byju_cto", "byju_dev1", "byju_dev2", "byju_content"},
	}
	
	roles := map[string]string{
		"ceo":            "Chief Executive Officer",
		"cto":            "Chief Technology Officer",
		"dev1":           "Senior Developer",
		"dev2":           "Junior Developer",
		"pm":             "Product Manager",
		"analytics":      "Analytics Manager",
		"data_scientist": "Data Scientist",
		"designer":       "UI/UX Designer",
		"content":        "Content Manager",
	}
	
	cities := []string{"Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune"}
	skills := []string{"Go", "Python", "JavaScript", "React", "Kubernetes", "AWS", "Machine Learning", "Analytics"}
	
	// Add nodes (employees)
	for company, employees := range companies {
		for _, employeeID := range employees {
			// Extract role from employee ID
			role := "developer"
			for roleKey, roleTitle := range roles {
				if contains(employeeID, roleKey) {
					role = roleTitle
					break
				}
			}
			
			node := &Node{
				ID:    employeeID,
				Label: fmt.Sprintf("%s Employee", company),
				Properties: map[string]interface{}{
					"company":    company,
					"role":       role,
					"city":       cities[rand.Intn(len(cities))],
					"experience": rand.Intn(15) + 1,
					"skills":     getRandomSkills(skills, 2+rand.Intn(4)),
					"salary":     rand.Intn(50) + 10, // 10-60 lakhs
				},
			}
			cga.AddNode(node)
		}
	}
	
	// Add intra-company connections
	for company, employees := range companies {
		for i, emp1 := range employees {
			for j, emp2 := range employees {
				if i != j {
					weight := calculateConnectionWeight(emp1, emp2, company)
					if weight > 0.3 { // Only add strong connections
						edge := &Edge{
							From:   emp1,
							To:     emp2,
							Weight: weight,
							Properties: map[string]interface{}{
								"type":    "colleague",
								"company": company,
							},
						}
						cga.AddEdge(edge)
					}
				}
			}
		}
	}
	
	// Add inter-company connections (job changes, partnerships, etc.)
	interCompanyConnections := [][]string{
		{"flipkart_dev1", "paytm_dev2"},   // Job switch
		{"ola_cto", "zomato_cto"},         // CTO network
		{"byju_data_scientist", "flipkart_analytics"}, // Analytics community
		{"paytm_ceo", "ola_ceo"},          // CEO network
		{"zomato_designer", "byju_content"}, // Creative network
	}
	
	for _, connection := range interCompanyConnections {
		edge := &Edge{
			From:   connection[0],
			To:     connection[1],
			Weight: 0.4 + rand.Float64()*0.4, // 0.4 to 0.8
			Properties: map[string]interface{}{
				"type": "professional_network",
			},
		}
		cga.AddEdge(edge)
	}
	
	log.Printf("Generated tech network: %d nodes, %d edges", 
		cga.graph.nodeCount, cga.graph.edgeCount)
}

// Helper functions for demo data generation
func contains(s, substr string) bool {
	return len(s) >= len(substr) && s[len(s)-len(substr):] == substr ||
		   len(s) > len(substr) && s[:len(substr)] == substr ||
		   len(s) > len(substr) && contains(s[1:], substr)
}

func getRandomSkills(skills []string, count int) []string {
	if count >= len(skills) {
		return skills
	}
	
	selected := make([]string, count)
	indices := rand.Perm(len(skills))
	
	for i := 0; i < count; i++ {
		selected[i] = skills[indices[i]]
	}
	
	return selected
}

func calculateConnectionWeight(emp1, emp2, company string) float64 {
	baseWeight := 0.3
	
	// Same level employees (both have same role indicators)
	if (contains(emp1, "ceo") && contains(emp2, "ceo")) ||
	   (contains(emp1, "cto") && contains(emp2, "cto")) ||
	   (contains(emp1, "dev") && contains(emp2, "dev")) {
		baseWeight += 0.3
	}
	
	// Manager-reportee relationships
	if (contains(emp1, "ceo") && !contains(emp2, "ceo")) ||
	   (contains(emp1, "cto") && contains(emp2, "dev")) {
		baseWeight += 0.4
	}
	
	// Add randomness
	baseWeight += (rand.Float64() - 0.5) * 0.3
	
	return math.Max(0.0, math.Min(1.0, baseWeight))
}

// Performance analysis and reporting
func (cga *ConcurrentGraphAnalytics) generatePerformanceReport() {
	cga.mutex.RLock()
	defer cga.mutex.RUnlock()
	
	fmt.Println("\n⚡ CONCURRENT GRAPH ANALYTICS - PERFORMANCE REPORT")
	fmt.Println(strings.Repeat("=", 65))
	
	fmt.Printf("Worker Pool Size: %d goroutines\n", cga.workerPoolSize)
	fmt.Printf("CPU Cores: %d\n", runtime.NumCPU())
	fmt.Printf("Graph Size: %d nodes, %d edges\n", cga.graph.nodeCount, cga.graph.edgeCount)
	
	fmt.Println("\nAlgorithm Performance:")
	fmt.Println(strings.Repeat("-", 30))
	
	var totalTime time.Duration
	for algorithm, duration := range cga.performanceStats {
		fmt.Printf("• %-25s: %v\n", algorithm, duration)
		totalTime += duration
	}
	fmt.Printf("• %-25s: %v\n", "Total Execution Time", totalTime)
	
	// Memory estimation
	memEstimate := (cga.graph.nodeCount*200 + cga.graph.edgeCount*100) / 1024
	fmt.Printf("\nEstimated Memory Usage: ~%d KB\n", memEstimate)
	
	// Scalability projections
	fmt.Println("\n📈 Scalability Projections:")
	fmt.Println(strings.Repeat("-", 30))
	
	scalingFactors := []struct {
		name  string
		nodes int
		edges int
	}{
		{"Current Demo", cga.graph.nodeCount, cga.graph.edgeCount},
		{"Small Company", 1000, 5000},
		{"Medium Company", 10000, 50000},
		{"Large Enterprise", 100000, 1000000},
		{"Industry Scale", 1000000, 10000000},
	}
	
	for _, factor := range scalingFactors {
		if factor.nodes == cga.graph.nodeCount {
			fmt.Printf("• %-15s: %6d nodes, %8d edges (Current)\n", 
				factor.name, factor.nodes, factor.edges)
		} else {
			estimatedTime := time.Duration(float64(totalTime) * 
				math.Sqrt(float64(factor.nodes)/float64(cga.graph.nodeCount)))
			fmt.Printf("• %-15s: %6d nodes, %8d edges (~%v)\n", 
				factor.name, factor.nodes, factor.edges, estimatedTime)
		}
	}
}

// Cleanup resources
func (cga *ConcurrentGraphAnalytics) Close() {
	if cga.cancel != nil {
		cga.cancel()
	}
	
	for _, ch := range cga.resultChannels {
		close(ch)
	}
}

// Demo function
func runConcurrentGraphAnalyticsDemo() {
	fmt.Println("🚀 Concurrent Graph Analytics - Indian Tech Network")
	fmt.Println(strings.Repeat("=", 60))
	
	// Initialize analytics engine
	cga := NewConcurrentGraphAnalytics(false, runtime.NumCPU())
	defer cga.Close()
	
	// Generate demo network
	cga.generateDemoTechNetwork()
	
	fmt.Printf("\n🏗️  Tech network created with %d employees\n", len(cga.graph.Nodes))
	
	// Run concurrent PageRank
	fmt.Println("\n🏆 Running Concurrent PageRank Analysis...")
	pageRankResults, err := cga.ComputePageRankConcurrent(0.85, 100, 1e-6)
	if err != nil {
		log.Printf("PageRank error: %v", err)
	} else {
		fmt.Println("\nTop 10 Most Important Employees (PageRank):")
		for i, result := range pageRankResults[:min(10, len(pageRankResults))] {
			node := cga.graph.Nodes[result.NodeID]
			fmt.Printf("%2d. %s (Score: %.6f)\n", i+1, result.NodeID, result.Score)
			if company, ok := node.Properties["company"].(string); ok {
				if role, ok := node.Properties["role"].(string); ok {
					fmt.Printf("    %s at %s\n", role, company)
				}
			}
		}
	}
	
	// Run concurrent centrality analysis
	fmt.Println("\n🎯 Running Concurrent Centrality Analysis...")
	centralityResults, err := cga.ComputeBetweennessCentralityConcurrent()
	if err != nil {
		log.Printf("Centrality error: %v", err)
	} else {
		fmt.Println("\nTop 5 Bridge Employees (Betweenness Centrality):")
		for i, result := range centralityResults[:min(5, len(centralityResults))] {
			node := cga.graph.Nodes[result.NodeID]
			fmt.Printf("%d. %s (Betweenness: %.6f)\n", i+1, result.NodeID, result.BetweennessCentrality)
			if company, ok := node.Properties["company"].(string); ok {
				fmt.Printf("   Company: %s\n", company)
			}
		}
	}
	
	// Run concurrent community detection
	fmt.Println("\n🏘️  Running Concurrent Community Detection...")
	communityResults, err := cga.DetectCommunitiesConcurrent(50)
	if err != nil {
		log.Printf("Community detection error: %v", err)
	} else {
		fmt.Printf("\nDetected %d communities:\n", len(communityResults))
		for i, community := range communityResults[:min(5, len(communityResults))] {
			fmt.Printf("\nCommunity %d (%d members):\n", i+1, community.Size)
			
			// Analyze community composition
			companies := make(map[string]int)
			for _, memberID := range community.Members {
				if node, exists := cga.graph.Nodes[memberID]; exists {
					if company, ok := node.Properties["company"].(string); ok {
						companies[company]++
					}
				}
			}
			
			fmt.Printf("  Companies: ")
			for company, count := range companies {
				fmt.Printf("%s(%d) ", company, count)
			}
			fmt.Println()
			
			// Show some members
			fmt.Printf("  Members: ")
			for i, memberID := range community.Members[:min(3, len(community.Members))] {
				if i > 0 {
					fmt.Printf(", ")
				}
				fmt.Printf("%s", memberID)
			}
			if len(community.Members) > 3 {
				fmt.Printf(" and %d more", len(community.Members)-3)
			}
			fmt.Println()
		}
	}
	
	// Generate performance report
	cga.generatePerformanceReport()
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func main() {
	// Set up proper random seed
	rand.Seed(time.Now().UnixNano())
	
	runConcurrentGraphAnalyticsDemo()
	
	fmt.Printf("\n" + strings.Repeat("=", 60))
	fmt.Printf("\n📚 LEARNING POINTS:\n")
	fmt.Printf("• Concurrent Go programming graph analytics को dramatically speed up karta hai\n")
	fmt.Printf("• Goroutines और channels efficient parallel processing provide karte hai\n")
	fmt.Printf("• Worker pool pattern large graph processing के लिए scalable solution hai\n")
	fmt.Printf("• Mutex और sync primitives thread-safe graph operations ensure करते hai\n")
	fmt.Printf("• Production systems मein concurrent algorithms real-time analytics enable करते hai\n")
	fmt.Printf("• Indian tech companies के network patterns unique insights reveal करते hai\n")
	fmt.Printf("• Graph analytics distributed systems की complexity को handle कर सकते है\n")
}
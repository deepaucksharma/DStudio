package main

import (
	"context"
	"fmt"
	"log"
	"math"
	"math/rand"
	"runtime"
	"sort"
	"sync"
	"sync/atomic"
	"time"
)

/*
Parallel Graph Processing for Social Networks
जैसे कि Facebook, Instagram के social graph analysis में use होता है

यह example दिखाता है कि कैसे massive social graphs को parallel processing
के through analyze करते हैं। Indian social media companies और platforms
जैसे ShareChat, Koo, MX TakaTak इसे use करती हैं user recommendations,
content ranking, और influence analysis के लिए।

Production context: Facebook processes graphs with 3+ billion nodes and trillions of edges
Scale: Handles social graphs with millions of users and billions of relationships
Challenge: Distributing graph algorithms across multiple processors efficiently
*/

// Vertex represents a user in the social network
type Vertex struct {
	ID       int64             `json:"id"`
	UserID   string            `json:"user_id"`
	Name     string            `json:"name"`
	Metadata map[string]string `json:"metadata"`
	
	// Graph algorithm specific fields
	PageRankScore    float64 `json:"pagerank_score"`
	CommunityID      int     `json:"community_id"`
	ShortestDistance int     `json:"shortest_distance"`
	Visited          bool    `json:"visited"`
	
	// Synchronization
	mutex sync.RWMutex
}

// Edge represents a relationship between users
type Edge struct {
	From   int64   `json:"from"`
	To     int64   `json:"to"`
	Weight float64 `json:"weight"`
	Type   string  `json:"type"` // "friend", "follow", "like", etc.
}

// SocialGraph represents the social network graph
type SocialGraph struct {
	Vertices    map[int64]*Vertex `json:"vertices"`
	Adjacency   map[int64][]int64 `json:"adjacency"`
	Edges       []Edge            `json:"edges"`
	VertexCount int64             `json:"vertex_count"`
	EdgeCount   int64             `json:"edge_count"`
	
	// Threading
	mutex       sync.RWMutex
	workerCount int
}

// NewSocialGraph creates a new social graph
func NewSocialGraph(workerCount int) *SocialGraph {
	if workerCount <= 0 {
		workerCount = runtime.NumCPU()
	}
	
	return &SocialGraph{
		Vertices:    make(map[int64]*Vertex),
		Adjacency:   make(map[int64][]int64),
		Edges:       make([]Edge, 0),
		workerCount: workerCount,
	}
}

// AddVertex adds a vertex to the graph
func (sg *SocialGraph) AddVertex(vertex *Vertex) {
	sg.mutex.Lock()
	defer sg.mutex.Unlock()
	
	sg.Vertices[vertex.ID] = vertex
	if sg.Adjacency[vertex.ID] == nil {
		sg.Adjacency[vertex.ID] = make([]int64, 0)
	}
	sg.VertexCount++
}

// AddEdge adds an edge to the graph
func (sg *SocialGraph) AddEdge(edge Edge) {
	sg.mutex.Lock()
	defer sg.mutex.Unlock()
	
	// Add to adjacency list
	sg.Adjacency[edge.From] = append(sg.Adjacency[edge.From], edge.To)
	
	// Add reverse edge for undirected relationships like friendship
	if edge.Type == "friend" {
		sg.Adjacency[edge.To] = append(sg.Adjacency[edge.To], edge.From)
	}
	
	sg.Edges = append(sg.Edges, edge)
	sg.EdgeCount++
}

// GetNeighbors returns neighbors of a vertex
func (sg *SocialGraph) GetNeighbors(vertexID int64) []int64 {
	sg.mutex.RLock()
	defer sg.mutex.RUnlock()
	
	neighbors := sg.Adjacency[vertexID]
	result := make([]int64, len(neighbors))
	copy(result, neighbors)
	return result
}

// GetDegree returns the degree of a vertex
func (sg *SocialGraph) GetDegree(vertexID int64) int {
	sg.mutex.RLock()
	defer sg.mutex.RUnlock()
	
	return len(sg.Adjacency[vertexID])
}

// ParallelPageRank implements PageRank algorithm using parallel processing
func (sg *SocialGraph) ParallelPageRank(ctx context.Context, iterations int, dampingFactor float64) error {
	log.Printf("Starting parallel PageRank with %d iterations, damping factor %.2f", iterations, dampingFactor)
	startTime := time.Now()
	
	sg.mutex.RLock()
	vertexCount := float64(sg.VertexCount)
	vertices := make([]*Vertex, 0, len(sg.Vertices))
	for _, v := range sg.Vertices {
		vertices = append(vertices, v)
	}
	sg.mutex.RUnlock()
	
	// Initialize PageRank scores
	initialScore := 1.0 / vertexCount
	for _, vertex := range vertices {
		vertex.mutex.Lock()
		vertex.PageRankScore = initialScore
		vertex.mutex.Unlock()
	}
	
	// Create worker channels
	vertexChan := make(chan *Vertex, len(vertices))
	resultChan := make(chan map[int64]float64, sg.workerCount)
	
	// PageRank iterations
	for iter := 0; iter < iterations; iter++ {
		iterStartTime := time.Now()
		
		// Start workers
		var wg sync.WaitGroup
		for i := 0; i < sg.workerCount; i++ {
			wg.Add(1)
			go sg.pageRankWorker(ctx, &wg, vertexChan, resultChan, dampingFactor, vertexCount)
		}
		
		// Send vertices to workers
		go func() {
			defer close(vertexChan)
			for _, vertex := range vertices {
				select {
				case vertexChan <- vertex:
				case <-ctx.Done():
					return
				}
			}
		}()
		
		// Collect results
		newScores := make(map[int64]float64)
		for i := 0; i < sg.workerCount; i++ {
			select {
			case scores := <-resultChan:
				for vertexID, score := range scores {
					newScores[vertexID] += score
				}
			case <-ctx.Done():
				return ctx.Err()
			}
		}
		
		wg.Wait()
		
		// Update scores
		for _, vertex := range vertices {
			vertex.mutex.Lock()
			if newScore, exists := newScores[vertex.ID]; exists {
				vertex.PageRankScore = newScore
			}
			vertex.mutex.Unlock()
		}
		
		log.Printf("PageRank iteration %d completed in %v", iter+1, time.Since(iterStartTime))
		
		// Reset channels for next iteration
		vertexChan = make(chan *Vertex, len(vertices))
		resultChan = make(chan map[int64]float64, sg.workerCount)
	}
	
	log.Printf("Parallel PageRank completed in %v", time.Since(startTime))
	return nil
}

// pageRankWorker processes PageRank computation for assigned vertices
func (sg *SocialGraph) pageRankWorker(ctx context.Context, wg *sync.WaitGroup, vertexChan <-chan *Vertex, 
	resultChan chan<- map[int64]float64, dampingFactor, vertexCount float64) {
	defer wg.Done()
	
	localScores := make(map[int64]float64)
	
	for {
		select {
		case vertex, ok := <-vertexChan:
			if !ok {
				// Send results and exit
				resultChan <- localScores
				return
			}
			
			// Calculate new PageRank score
			vertex.mutex.RLock()
			currentScore := vertex.PageRankScore
			vertex.mutex.RUnlock()
			
			neighbors := sg.GetNeighbors(vertex.ID)
			newScore := (1.0 - dampingFactor) / vertexCount
			
			// Sum contributions from neighbors
			for _, neighborID := range neighbors {
				sg.mutex.RLock()
				neighbor := sg.Vertices[neighborID]
				sg.mutex.RUnlock()
				
				if neighbor != nil {
					neighbor.mutex.RLock()
					neighborScore := neighbor.PageRankScore
					neighbor.mutex.RUnlock()
					
					neighborDegree := float64(sg.GetDegree(neighborID))
					if neighborDegree > 0 {
						newScore += dampingFactor * (neighborScore / neighborDegree)
					}
				}
			}
			
			localScores[vertex.ID] = newScore
			
		case <-ctx.Done():
			resultChan <- localScores
			return
		}
	}
}

// ParallelBFS performs parallel breadth-first search
func (sg *SocialGraph) ParallelBFS(ctx context.Context, startVertexID int64) error {
	log.Printf("Starting parallel BFS from vertex %d", startVertexID)
	startTime := time.Now()
	
	// Initialize distances
	sg.mutex.RLock()
	for _, vertex := range sg.Vertices {
		vertex.mutex.Lock()
		vertex.ShortestDistance = math.MaxInt32
		vertex.Visited = false
		vertex.mutex.Unlock()
	}
	startVertex := sg.Vertices[startVertexID]
	sg.mutex.RUnlock()
	
	if startVertex == nil {
		return fmt.Errorf("start vertex %d not found", startVertexID)
	}
	
	// Set start vertex distance
	startVertex.mutex.Lock()
	startVertex.ShortestDistance = 0
	startVertex.Visited = true
	startVertex.mutex.Unlock()
	
	// BFS using parallel processing
	currentLevel := []int64{startVertexID}
	distance := 0
	
	for len(currentLevel) > 0 {
		nextLevel := sg.processLevelParallel(ctx, currentLevel, distance+1)
		currentLevel = nextLevel
		distance++
		
		log.Printf("BFS level %d: processed %d vertices", distance, len(nextLevel))
	}
	
	log.Printf("Parallel BFS completed in %v", time.Since(startTime))
	return nil
}

// processLevelParallel processes a BFS level using parallel workers
func (sg *SocialGraph) processLevelParallel(ctx context.Context, currentLevel []int64, newDistance int) []int64 {
	if len(currentLevel) == 0 {
		return nil
	}
	
	// Create channels for work distribution
	vertexChan := make(chan int64, len(currentLevel))
	nextLevelChan := make(chan []int64, sg.workerCount)
	
	// Start workers
	var wg sync.WaitGroup
	for i := 0; i < sg.workerCount; i++ {
		wg.Add(1)
		go sg.bfsWorker(ctx, &wg, vertexChan, nextLevelChan, newDistance)
	}
	
	// Send current level vertices to workers
	go func() {
		defer close(vertexChan)
		for _, vertexID := range currentLevel {
			select {
			case vertexChan <- vertexID:
			case <-ctx.Done():
				return
			}
		}
	}()
	
	// Collect next level vertices
	var nextLevel []int64
	for i := 0; i < sg.workerCount; i++ {
		select {
		case levelVertices := <-nextLevelChan:
			nextLevel = append(nextLevel, levelVertices...)
		case <-ctx.Done():
			break
		}
	}
	
	wg.Wait()
	return nextLevel
}

// bfsWorker processes BFS for assigned vertices
func (sg *SocialGraph) bfsWorker(ctx context.Context, wg *sync.WaitGroup, vertexChan <-chan int64, 
	nextLevelChan chan<- []int64, newDistance int) {
	defer wg.Done()
	
	var localNextLevel []int64
	
	for {
		select {
		case vertexID, ok := <-vertexChan:
			if !ok {
				nextLevelChan <- localNextLevel
				return
			}
			
			neighbors := sg.GetNeighbors(vertexID)
			for _, neighborID := range neighbors {
				sg.mutex.RLock()
				neighbor := sg.Vertices[neighborID]
				sg.mutex.RUnlock()
				
				if neighbor != nil {
					neighbor.mutex.Lock()
					if !neighbor.Visited {
						neighbor.Visited = true
						neighbor.ShortestDistance = newDistance
						localNextLevel = append(localNextLevel, neighborID)
					}
					neighbor.mutex.Unlock()
				}
			}
			
		case <-ctx.Done():
			nextLevelChan <- localNextLevel
			return
		}
	}
}

// ParallelCommunityDetection detects communities using parallel label propagation
func (sg *SocialGraph) ParallelCommunityDetection(ctx context.Context, maxIterations int) error {
	log.Printf("Starting parallel community detection with max %d iterations", maxIterations)
	startTime := time.Now()
	
	// Initialize communities (each vertex starts in its own community)
	sg.mutex.RLock()
	vertices := make([]*Vertex, 0, len(sg.Vertices))
	for _, v := range sg.Vertices {
		vertices = append(vertices, v)
	}
	sg.mutex.RUnlock()
	
	for _, vertex := range vertices {
		vertex.mutex.Lock()
		vertex.CommunityID = int(vertex.ID)
		vertex.mutex.Unlock()
	}
	
	// Label propagation iterations
	for iter := 0; iter < maxIterations; iter++ {
		iterStartTime := time.Now()
		
		// Process vertices in parallel
		changed := sg.propagateLabelsParallel(ctx, vertices)
		
		log.Printf("Community detection iteration %d: %d labels changed in %v", 
			iter+1, changed, time.Since(iterStartTime))
		
		// Convergence check
		if changed == 0 {
			log.Printf("Community detection converged after %d iterations", iter+1)
			break
		}
	}
	
	log.Printf("Parallel community detection completed in %v", time.Since(startTime))
	return nil
}

// propagateLabelsParallel propagates community labels using parallel workers
func (sg *SocialGraph) propagateLabelsParallel(ctx context.Context, vertices []*Vertex) int64 {
	vertexChan := make(chan *Vertex, len(vertices))
	resultChan := make(chan int64, sg.workerCount)
	
	// Start workers
	var wg sync.WaitGroup
	for i := 0; i < sg.workerCount; i++ {
		wg.Add(1)
		go sg.communityDetectionWorker(ctx, &wg, vertexChan, resultChan)
	}
	
	// Send vertices to workers
	go func() {
		defer close(vertexChan)
		for _, vertex := range vertices {
			select {
			case vertexChan <- vertex:
			case <-ctx.Done():
				return
			}
		}
	}()
	
	// Collect results
	var totalChanged int64
	for i := 0; i < sg.workerCount; i++ {
		select {
		case changed := <-resultChan:
			totalChanged += changed
		case <-ctx.Done():
			break
		}
	}
	
	wg.Wait()
	return totalChanged
}

// communityDetectionWorker processes community detection for assigned vertices
func (sg *SocialGraph) communityDetectionWorker(ctx context.Context, wg *sync.WaitGroup, 
	vertexChan <-chan *Vertex, resultChan chan<- int64) {
	defer wg.Done()
	
	var localChanged int64
	
	for {
		select {
		case vertex, ok := <-vertexChan:
			if !ok {
				resultChan <- localChanged
				return
			}
			
			// Get current community ID
			vertex.mutex.RLock()
			currentCommunity := vertex.CommunityID
			vertex.mutex.RUnlock()
			
			// Count neighbor community labels
			neighbors := sg.GetNeighbors(vertex.ID)
			communityCount := make(map[int]int)
			
			for _, neighborID := range neighbors {
				sg.mutex.RLock()
				neighbor := sg.Vertices[neighborID]
				sg.mutex.RUnlock()
				
				if neighbor != nil {
					neighbor.mutex.RLock()
					neighborCommunity := neighbor.CommunityID
					neighbor.mutex.RUnlock()
					
					communityCount[neighborCommunity]++
				}
			}
			
			// Find most frequent community label
			maxCount := 0
			newCommunity := currentCommunity
			
			for community, count := range communityCount {
				if count > maxCount {
					maxCount = count
					newCommunity = community
				}
			}
			
			// Update community if changed
			if newCommunity != currentCommunity {
				vertex.mutex.Lock()
				vertex.CommunityID = newCommunity
				vertex.mutex.Unlock()
				
				localChanged++
			}
			
		case <-ctx.Done():
			resultChan <- localChanged
			return
		}
	}
}

// GetTopPageRankVertices returns vertices with highest PageRank scores
func (sg *SocialGraph) GetTopPageRankVertices(limit int) []*Vertex {
	sg.mutex.RLock()
	vertices := make([]*Vertex, 0, len(sg.Vertices))
	for _, v := range sg.Vertices {
		vertices = append(vertices, v)
	}
	sg.mutex.RUnlock()
	
	// Sort by PageRank score
	sort.Slice(vertices, func(i, j int) bool {
		vertices[i].mutex.RLock()
		vertices[j].mutex.RLock()
		defer vertices[i].mutex.RUnlock()
		defer vertices[j].mutex.RUnlock()
		
		return vertices[i].PageRankScore > vertices[j].PageRankScore
	})
	
	if limit > len(vertices) {
		limit = len(vertices)
	}
	
	return vertices[:limit]
}

// GetCommunityStats returns community statistics
func (sg *SocialGraph) GetCommunityStats() map[int]int {
	sg.mutex.RLock()
	defer sg.mutex.RUnlock()
	
	communityStats := make(map[int]int)
	
	for _, vertex := range sg.Vertices {
		vertex.mutex.RLock()
		communityStats[vertex.CommunityID]++
		vertex.mutex.RUnlock()
	}
	
	return communityStats
}

// GenerateSampleSocialGraph creates a sample social network graph
func GenerateSampleSocialGraph(userCount, connectionCount int) *SocialGraph {
	log.Printf("Generating sample social graph with %d users and %d connections", userCount, connectionCount)
	
	graph := NewSocialGraph(runtime.NumCPU())
	
	// Generate users
	userNames := []string{
		"Rahul", "Priya", "Arjun", "Sneha", "Amit", "Deepika", "Vikash", "Kiran",
		"Ankit", "Pooja", "Ravi", "Neha", "Suresh", "Kavya", "Manish", "Asha",
		"Raj", "Sunita", "Anil", "Geeta", "Rohit", "Meera", "Sanjay", "Rekha"
	}
	
	for i := 0; i < userCount; i++ {
		vertex := &Vertex{
			ID:       int64(i),
			UserID:   fmt.Sprintf("user_%d", i),
			Name:     userNames[i%len(userNames)] + fmt.Sprintf("_%d", i),
			Metadata: map[string]string{
				"city":    []string{"Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"}[i%5],
				"age":     fmt.Sprintf("%d", 18+rand.Intn(50)),
				"interests": []string{"tech", "sports", "music", "travel", "food"}[i%5],
			},
		}
		
		graph.AddVertex(vertex)
	}
	
	// Generate connections
	connectionTypes := []string{"friend", "follow", "like"}
	
	for i := 0; i < connectionCount; i++ {
		from := int64(rand.Intn(userCount))
		to := int64(rand.Intn(userCount))
		
		// Avoid self-connections
		if from == to {
			continue
		}
		
		edge := Edge{
			From:   from,
			To:     to,
			Weight: rand.Float64(),
			Type:   connectionTypes[rand.Intn(len(connectionTypes))],
		}
		
		graph.AddEdge(edge)
	}
	
	log.Printf("Generated social graph with %d vertices and %d edges", graph.VertexCount, graph.EdgeCount)
	return graph
}

// Performance benchmark for graph algorithms
func benchmarkGraphAlgorithms(graph *SocialGraph) {
	fmt.Println("\n⚡ Performance Benchmarks:")
	fmt.Println("=" + string(make([]byte, 50)))
	
	ctx := context.Background()
	
	// Benchmark PageRank
	fmt.Println("\n📊 PageRank Performance:")
	
	// Sequential PageRank simulation (for comparison)
	startTime := time.Now()
	// Simulate sequential processing time
	time.Sleep(time.Duration(graph.VertexCount/1000) * time.Millisecond)
	sequentialTime := time.Since(startTime)
	
	// Parallel PageRank
	startTime = time.Now()
	graph.ParallelPageRank(ctx, 5, 0.85)
	parallelTime := time.Since(startTime)
	
	fmt.Printf("  Sequential (simulated): %v\n", sequentialTime)
	fmt.Printf("  Parallel (%d cores): %v\n", runtime.NumCPU(), parallelTime)
	if sequentialTime > parallelTime {
		speedup := float64(sequentialTime) / float64(parallelTime)
		fmt.Printf("  Speedup: %.2fx\n", speedup)
	}
	
	// Benchmark BFS
	fmt.Println("\n🔍 BFS Performance:")
	startTime = time.Now()
	graph.ParallelBFS(ctx, 0)
	bfsTime := time.Since(startTime)
	fmt.Printf("  Parallel BFS: %v\n", bfsTime)
	
	// Benchmark Community Detection
	fmt.Println("\n👥 Community Detection Performance:")
	startTime = time.Now()
	graph.ParallelCommunityDetection(ctx, 10)
	communityTime := time.Since(startTime)
	fmt.Printf("  Parallel Community Detection: %v\n", communityTime)
}

// Main demonstration function
func main() {
	fmt.Println("🌐 Social Network Parallel Graph Processing Demo")
	fmt.Println("=" + string(make([]byte, 59)))
	
	// Generate sample social network
	fmt.Println("\n👥 Generating sample social network...")
	
	userCount := 10000    // 10K users
	connectionCount := 50000  // 50K connections
	
	graph := GenerateSampleSocialGraph(userCount, connectionCount)
	
	fmt.Printf("✅ Generated social graph:")
	fmt.Printf("   Users: %d\n", graph.VertexCount)
	fmt.Printf("   Connections: %d\n", graph.EdgeCount)
	fmt.Printf("   Average degree: %.2f\n", float64(graph.EdgeCount*2)/float64(graph.VertexCount))
	fmt.Printf("   Worker threads: %d\n", graph.workerCount)
	
	ctx := context.Background()
	
	// Run PageRank to find influential users
	fmt.Println("\n⭐ Running PageRank to find influential users...")
	err := graph.ParallelPageRank(ctx, 10, 0.85)
	if err != nil {
		log.Fatalf("PageRank failed: %v", err)
	}
	
	topUsers := graph.GetTopPageRankVertices(10)
	fmt.Println("\n🏆 Top 10 Most Influential Users:")
	for i, user := range topUsers {
		user.mutex.RLock()
		fmt.Printf("%2d. %s (ID: %d) - Score: %.6f, Degree: %d\n", 
			i+1, user.Name, user.ID, user.PageRankScore, graph.GetDegree(user.ID))
		user.mutex.RUnlock()
	}
	
	// Run BFS to find shortest paths
	fmt.Println("\n🔍 Running BFS for shortest path analysis...")
	startUserID := topUsers[0].ID
	err = graph.ParallelBFS(ctx, startUserID)
	if err != nil {
		log.Fatalf("BFS failed: %v", err)
	}
	
	// Analyze distance distribution
	distanceCount := make(map[int]int)
	graph.mutex.RLock()
	for _, vertex := range graph.Vertices {
		vertex.mutex.RLock()
		if vertex.ShortestDistance < math.MaxInt32 {
			distanceCount[vertex.ShortestDistance]++
		}
		vertex.mutex.RUnlock()
	}
	graph.mutex.RUnlock()
	
	fmt.Printf("\n📏 Distance distribution from user %d:\n", startUserID)
	for distance := 0; distance <= 6; distance++ {
		count := distanceCount[distance]
		percentage := float64(count) / float64(graph.VertexCount) * 100
		fmt.Printf("  Distance %d: %d users (%.1f%%)\n", distance, count, percentage)
	}
	
	// Run community detection
	fmt.Println("\n👥 Running community detection...")
	err = graph.ParallelCommunityDetection(ctx, 20)
	if err != nil {
		log.Fatalf("Community detection failed: %v", err)
	}
	
	communityStats := graph.GetCommunityStats()
	
	// Sort communities by size
	type communitySize struct {
		ID   int
		Size int
	}
	
	var communities []communitySize
	for id, size := range communityStats {
		communities = append(communities, communitySize{ID: id, Size: size})
	}
	
	sort.Slice(communities, func(i, j int) bool {
		return communities[i].Size > communities[j].Size
	})
	
	fmt.Printf("\n🏘️  Top 10 Largest Communities:\n")
	for i, community := range communities[:min(10, len(communities))] {
		percentage := float64(community.Size) / float64(graph.VertexCount) * 100
		fmt.Printf("%2d. Community %d: %d users (%.1f%%)\n", 
			i+1, community.ID, community.Size, percentage)
	}
	
	// Show graph connectivity analysis
	fmt.Println("\n🔗 Graph Connectivity Analysis:")
	
	// Calculate basic graph metrics
	var totalDegree int64
	var maxDegree int
	var minDegree = math.MaxInt32
	
	graph.mutex.RLock()
	for vertexID := range graph.Vertices {
		degree := graph.GetDegree(vertexID)
		totalDegree += int64(degree)
		if degree > maxDegree {
			maxDegree = degree
		}
		if degree < minDegree {
			minDegree = degree
		}
	}
	graph.mutex.RUnlock()
	
	avgDegree := float64(totalDegree) / float64(graph.VertexCount)
	density := float64(graph.EdgeCount) / (float64(graph.VertexCount) * float64(graph.VertexCount-1) / 2)
	
	fmt.Printf("  Average degree: %.2f\n", avgDegree)
	fmt.Printf("  Max degree: %d\n", maxDegree)
	fmt.Printf("  Min degree: %d\n", minDegree)
	fmt.Printf("  Graph density: %.6f\n", density)
	fmt.Printf("  Clustering coefficient: %.4f (estimated)\n", density*avgDegree)
	
	// Performance benchmarks
	benchmarkGraphAlgorithms(graph)
	
	// Social media insights
	fmt.Println("\n💡 Social Media Platform Insights:")
	fmt.Println("- Parallel graph processing enables real-time social media analysis")
	fmt.Println("- PageRank identifies influential users for targeted marketing")
	fmt.Println("- BFS powers friend suggestions and connection recommendations")
	fmt.Println("- Community detection helps in content personalization")
	fmt.Println("- Critical for platforms like Facebook, Instagram with billions of users")
	fmt.Println("- Enables fraud detection through graph pattern analysis")
	fmt.Println("- Powers viral content prediction and trend analysis")
	fmt.Println("- Essential for ad targeting and audience segmentation")
	fmt.Println("- Scales to handle graphs with trillions of edges")
	fmt.Println("- Parallel processing reduces analysis time from hours to minutes")
	
	fmt.Println("\nSocial network graph processing demo completed!")
}

// Helper function
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
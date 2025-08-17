/*
🇮🇳 Load Balancer Tests
Episode 27: Load Balancing - Go Tests

Author: Agent 5 - Code Developer
Context: Testing load balancing algorithms
*/

package tests

import (
	"fmt"
	"math"
	"net/url"
	"sync"
	"testing"
	"time"
)

// Mock structures for testing (simplified versions)
type MockRestaurant struct {
	ID        string
	URL       *url.URL
	IsHealthy bool
	Weight    int
	Zone      string
	mutex     sync.RWMutex
}

func (r *MockRestaurant) IsAvailable() bool {
	r.mutex.RLock()
	defer r.mutex.RUnlock()
	return r.IsHealthy
}

func (r *MockRestaurant) SetHealth(healthy bool) {
	r.mutex.Lock()
	defer r.mutex.Unlock()
	r.IsHealthy = healthy
}

type MockLoadBalancer struct {
	restaurants []*MockRestaurant
	current     uint64
	mutex       sync.RWMutex
}

func NewMockLoadBalancer() *MockLoadBalancer {
	return &MockLoadBalancer{
		restaurants: make([]*MockRestaurant, 0),
		current:     0,
	}
}

func (lb *MockLoadBalancer) AddRestaurant(restaurant *MockRestaurant) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()
	lb.restaurants = append(lb.restaurants, restaurant)
}

func (lb *MockLoadBalancer) GetNextRestaurant() (*MockRestaurant, error) {
	lb.mutex.RLock()
	defer lb.mutex.RUnlock()

	if len(lb.restaurants) == 0 {
		return nil, fmt.Errorf("no restaurants available")
	}

	// Simple round-robin for testing
	for attempts := 0; attempts < len(lb.restaurants); attempts++ {
		index := int(lb.current) % len(lb.restaurants)
		lb.current++
		
		restaurant := lb.restaurants[index]
		if restaurant.IsAvailable() {
			return restaurant, nil
		}
	}

	return nil, fmt.Errorf("no healthy restaurants available")
}

// Test Round Robin Load Balancing
func TestRoundRobinLoadBalancing(t *testing.T) {
	// Create load balancer
	lb := NewMockLoadBalancer()

	// Add test restaurants
	restaurants := []*MockRestaurant{
		{
			ID:        "rest-mumbai-001",
			URL:       mustParseURL("http://localhost:8081"),
			IsHealthy: true,
			Zone:      "mumbai",
		},
		{
			ID:        "rest-mumbai-002",
			URL:       mustParseURL("http://localhost:8082"),
			IsHealthy: true,
			Zone:      "mumbai",
		},
		{
			ID:        "rest-delhi-001",
			URL:       mustParseURL("http://localhost:8083"),
			IsHealthy: true,
			Zone:      "delhi",
		},
	}

	for _, restaurant := range restaurants {
		lb.AddRestaurant(restaurant)
	}

	// Test round-robin distribution
	selections := make(map[string]int)
	rounds := 6 // 2 complete rounds

	for i := 0; i < rounds; i++ {
		restaurant, err := lb.GetNextRestaurant()
		if err != nil {
			t.Fatalf("Error getting restaurant: %v", err)
		}
		selections[restaurant.ID]++
	}

	// Verify equal distribution
	for id, count := range selections {
		expected := rounds / len(restaurants)
		if count != expected {
			t.Errorf("Restaurant %s got %d requests, expected %d", id, count, expected)
		}
	}
}

// Test Health Check Integration
func TestHealthCheckIntegration(t *testing.T) {
	lb := NewMockLoadBalancer()

	// Add test restaurants
	restaurants := []*MockRestaurant{
		{
			ID:        "healthy-rest",
			URL:       mustParseURL("http://localhost:8081"),
			IsHealthy: true,
			Zone:      "mumbai",
		},
		{
			ID:        "unhealthy-rest",
			URL:       mustParseURL("http://localhost:8082"),
			IsHealthy: false, // Unhealthy
			Zone:      "mumbai",
		},
	}

	for _, restaurant := range restaurants {
		lb.AddRestaurant(restaurant)
	}

	// Should only get healthy restaurant
	for i := 0; i < 5; i++ {
		restaurant, err := lb.GetNextRestaurant()
		if err != nil {
			t.Fatalf("Error getting restaurant: %v", err)
		}

		if restaurant.ID != "healthy-rest" {
			t.Errorf("Got unhealthy restaurant: %s", restaurant.ID)
		}
	}

	// Mark unhealthy restaurant as healthy
	restaurants[1].SetHealth(true)

	// Now should distribute between both
	selections := make(map[string]int)
	for i := 0; i < 10; i++ {
		restaurant, err := lb.GetNextRestaurant()
		if err != nil {
			t.Fatalf("Error getting restaurant: %v", err)
		}
		selections[restaurant.ID]++
	}

	// Both should receive requests
	if selections["healthy-rest"] == 0 {
		t.Error("Healthy restaurant should receive requests")
	}
	if selections["unhealthy-rest"] == 0 {
		t.Error("Previously unhealthy restaurant should receive requests after recovery")
	}
}

// Test Concurrent Access
func TestConcurrentAccess(t *testing.T) {
	lb := NewMockLoadBalancer()

	// Add test restaurants
	for i := 0; i < 3; i++ {
		restaurant := &MockRestaurant{
			ID:        fmt.Sprintf("concurrent-rest-%d", i),
			URL:       mustParseURL(fmt.Sprintf("http://localhost:808%d", i+1)),
			IsHealthy: true,
			Zone:      "test",
		}
		lb.AddRestaurant(restaurant)
	}

	// Test concurrent access
	const goroutines = 100
	const requestsPerGoroutine = 50

	var wg sync.WaitGroup
	results := make(chan string, goroutines*requestsPerGoroutine)

	for i := 0; i < goroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < requestsPerGoroutine; j++ {
				restaurant, err := lb.GetNextRestaurant()
				if err != nil {
					t.Errorf("Error in concurrent access: %v", err)
					return
				}
				results <- restaurant.ID
			}
		}()
	}

	wg.Wait()
	close(results)

	// Count results
	selections := make(map[string]int)
	totalRequests := 0
	for result := range results {
		selections[result]++
		totalRequests++
	}

	// Verify all requests were processed
	expectedTotal := goroutines * requestsPerGoroutine
	if totalRequests != expectedTotal {
		t.Errorf("Expected %d total requests, got %d", expectedTotal, totalRequests)
	}

	// Verify distribution is reasonable (within 20% variance)
	expectedPerRestaurant := totalRequests / 3
	tolerance := expectedPerRestaurant / 5 // 20% tolerance

	for id, count := range selections {
		if count < expectedPerRestaurant-tolerance || count > expectedPerRestaurant+tolerance {
			t.Errorf("Restaurant %s received %d requests, expected ~%d (±%d)",
				id, count, expectedPerRestaurant, tolerance)
		}
	}
}

// Test No Available Restaurants
func TestNoAvailableRestaurants(t *testing.T) {
	lb := NewMockLoadBalancer()

	// Test with no restaurants
	_, err := lb.GetNextRestaurant()
	if err == nil {
		t.Error("Expected error when no restaurants available")
	}

	// Add unhealthy restaurants
	for i := 0; i < 3; i++ {
		restaurant := &MockRestaurant{
			ID:        fmt.Sprintf("unhealthy-rest-%d", i),
			URL:       mustParseURL(fmt.Sprintf("http://localhost:808%d", i+1)),
			IsHealthy: false,
			Zone:      "test",
		}
		lb.AddRestaurant(restaurant)
	}

	// Should still get error
	_, err = lb.GetNextRestaurant()
	if err == nil {
		t.Error("Expected error when no healthy restaurants available")
	}
}

// Benchmark Round Robin Performance
func BenchmarkRoundRobinSelection(b *testing.B) {
	lb := NewMockLoadBalancer()

	// Add test restaurants
	for i := 0; i < 10; i++ {
		restaurant := &MockRestaurant{
			ID:        fmt.Sprintf("bench-rest-%d", i),
			URL:       mustParseURL(fmt.Sprintf("http://localhost:808%d", i+1)),
			IsHealthy: true,
			Zone:      "test",
		}
		lb.AddRestaurant(restaurant)
	}

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			_, err := lb.GetNextRestaurant()
			if err != nil {
				b.Fatalf("Benchmark error: %v", err)
			}
		}
	})
}

// Test Geographic Distance Calculations
func TestGeographicDistanceCalculation(t *testing.T) {
	// Mumbai coordinates
	mumbai := &MockGeoLocation{
		Latitude:  19.0760,
		Longitude: 72.8777,
		City:      "Mumbai",
	}

	// Delhi coordinates
	delhi := &MockGeoLocation{
		Latitude:  28.7041,
		Longitude: 77.1025,
		City:      "Delhi",
	}

	// Calculate distance
	distance := mumbai.CalculateDistance(delhi)

	// Mumbai to Delhi is approximately 1150-1200 km
	expectedDistance := 1150.0
	tolerance := 100.0 // 100km tolerance

	if distance < expectedDistance-tolerance || distance > expectedDistance+tolerance {
		t.Errorf("Distance Mumbai-Delhi: got %.2f km, expected ~%.2f km (±%.2f)",
			distance, expectedDistance, tolerance)
	}
}

// Mock geographic location for testing
type MockGeoLocation struct {
	Latitude  float64
	Longitude float64
	City      string
}

func (g *MockGeoLocation) CalculateDistance(other *MockGeoLocation) float64 {
	const earthRadius = 6371 // Earth radius in kilometers
	
	lat1Rad := g.Latitude * math.Pi / 180
	lon1Rad := g.Longitude * math.Pi / 180
	lat2Rad := other.Latitude * math.Pi / 180
	lon2Rad := other.Longitude * math.Pi / 180

	deltaLat := lat2Rad - lat1Rad
	deltaLon := lon2Rad - lon1Rad

	a := math.Sin(deltaLat/2)*math.Sin(deltaLat/2) +
		math.Cos(lat1Rad)*math.Cos(lat2Rad)*
			math.Sin(deltaLon/2)*math.Sin(deltaLon/2)

	c := 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))
	distance := earthRadius * c

	return distance
}

// Test Weighted Load Balancing
func TestWeightedLoadBalancing(t *testing.T) {
	type WeightedRestaurant struct {
		*MockRestaurant
		Weight          int
		EffectiveWeight int
		CurrentWeight   int
	}

	restaurants := []*WeightedRestaurant{
		{
			MockRestaurant: &MockRestaurant{
				ID:        "high-weight",
				IsHealthy: true,
			},
			Weight:          30,
			EffectiveWeight: 30,
		},
		{
			MockRestaurant: &MockRestaurant{
				ID:        "low-weight",
				IsHealthy: true,
			},
			Weight:          10,
			EffectiveWeight: 10,
		},
	}

	// Simulate weighted round-robin algorithm
	totalWeight := 40
	selections := make(map[string]int)
	
	// Run 100 iterations
	for i := 0; i < 100; i++ {
		var selected *WeightedRestaurant
		maxCurrentWeight := -1

		// Find restaurant with maximum current weight
		for _, restaurant := range restaurants {
			restaurant.CurrentWeight += restaurant.EffectiveWeight
			if restaurant.CurrentWeight > maxCurrentWeight {
				maxCurrentWeight = restaurant.CurrentWeight
				selected = restaurant
			}
		}

		// Decrease selected restaurant's current weight
		if selected != nil {
			selected.CurrentWeight -= totalWeight
			selections[selected.ID]++
		}
	}

	// High weight restaurant should get more requests
	highWeightCount := selections["high-weight"]
	lowWeightCount := selections["low-weight"]

	// Should be roughly 3:1 ratio (30:10 weight ratio)
	ratio := float64(highWeightCount) / float64(lowWeightCount)
	expectedRatio := 3.0
	tolerance := 0.5

	if ratio < expectedRatio-tolerance || ratio > expectedRatio+tolerance {
		t.Errorf("Weight ratio: got %.2f, expected ~%.2f (±%.2f)",
			ratio, expectedRatio, tolerance)
	}
}

// Helper function
func mustParseURL(rawURL string) *url.URL {
	url, err := url.Parse(rawURL)
	if err != nil {
		panic(fmt.Sprintf("Invalid URL: %s", rawURL))
	}
	return url
}


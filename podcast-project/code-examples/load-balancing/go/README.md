# 🚀 Go Load Balancing Examples
## Episode 27: Load Balancing - Go Implementations

---

## 🇮🇳 भारतीय Context में Load Balancing

Load balancing Indian microservices का backbone है। Swiggy delivery करते समय orders को different restaurants में distribute करने जैसा - सबसे efficient और available restaurant को order assign करना।

Mumbai traffic signals की तरह, incoming requests को multiple servers में intelligently distribute करना पड़ता है।

---

## 📂 Examples Structure

```
go/
├── 01_round_robin_balancer.go           # Basic round-robin distribution
├── 02_weighted_round_robin.go           # Weight-based distribution  
├── 03_health_aware_balancer.go          # Health check integration
├── 04_consistent_hash_balancer.go       # Session-aware routing
├── 05_geographic_load_balancer.go       # Location-based routing
├── go.mod                               # Go module definition
├── go.sum                               # Dependencies
├── tests/                               # Unit tests
│   ├── balancer_test.go
│   └── benchmark_test.go
└── README.md                            # This file
```

---

## 🚀 Example 1: Round Robin Load Balancer

```go
// 01_round_robin_balancer.go
/*
🇮🇳 Round Robin Load Balancer - Swiggy Restaurant Style
Orders को restaurants में equally distribute करने जैसा

Features:
- Equal request distribution
- Thread-safe operations
- Health status integration
- Swiggy-style restaurant allocation
- Production-ready error handling
- Hindi comments
*/

package main

import (
    "context"
    "errors"
    "fmt"
    "log"
    "net/http"
    "net/http/httputil"
    "net/url"
    "sync"
    "sync/atomic"
    "time"
)

// Restaurant represents a backend server - Swiggy restaurant style
type Restaurant struct {
    ID          string    // Restaurant ID (e.g., "rest-mumbai-001")
    URL         *url.URL  // Restaurant API endpoint
    IsHealthy   bool      // Restaurant availability status
    Weight      int       // Restaurant capacity weight
    Zone        string    // Geographic zone (mumbai, delhi, bangalore)
    Metadata    map[string]string // Restaurant metadata
    LastChecked time.Time // Last health check time
    mutex       sync.RWMutex
}

// IsAvailable checks if restaurant is currently accepting orders
func (r *Restaurant) IsAvailable() bool {
    r.mutex.RLock()
    defer r.mutex.RUnlock()
    return r.IsHealthy
}

// SetHealth updates restaurant health status
func (r *Restaurant) SetHealth(healthy bool) {
    r.mutex.Lock()
    defer r.mutex.Unlock()
    r.IsHealthy = healthy
    r.LastChecked = time.Now()
    
    status := "🟢 Available"
    if !healthy {
        status = "🔴 Unavailable"
    }
    log.Printf("🏪 Restaurant %s status: %s", r.ID, status)
}

// SwiggyLoadBalancer implements round-robin load balancing
type SwiggyLoadBalancer struct {
    restaurants []*Restaurant  // List of restaurants (backend servers)
    current     uint64         // Current restaurant index (atomic for thread safety)
    mutex       sync.RWMutex   // Read-write mutex for restaurant list
}

// NewSwiggyLoadBalancer creates a new load balancer
func NewSwiggyLoadBalancer() *SwiggyLoadBalancer {
    return &SwiggyLoadBalancer{
        restaurants: make([]*Restaurant, 0),
        current:     0,
    }
}

// AddRestaurant adds a new restaurant to the load balancer
func (lb *SwiggyLoadBalancer) AddRestaurant(restaurant *Restaurant) {
    lb.mutex.Lock()
    defer lb.mutex.Unlock()
    
    lb.restaurants = append(lb.restaurants, restaurant)
    log.Printf("✅ Restaurant added: %s in %s zone", restaurant.ID, restaurant.Zone)
}

// RemoveRestaurant removes a restaurant from the load balancer
func (lb *SwiggyLoadBalancer) RemoveRestaurant(restaurantID string) error {
    lb.mutex.Lock()
    defer lb.mutex.Unlock()
    
    for i, restaurant := range lb.restaurants {
        if restaurant.ID == restaurantID {
            // Remove restaurant from slice
            lb.restaurants = append(lb.restaurants[:i], lb.restaurants[i+1:]...)
            log.Printf("🗑️ Restaurant removed: %s", restaurantID)
            return nil
        }
    }
    
    return fmt.Errorf("restaurant not found: %s", restaurantID)
}

// GetNextRestaurant returns the next available restaurant using round-robin
func (lb *SwiggyLoadBalancer) GetNextRestaurant() (*Restaurant, error) {
    lb.mutex.RLock()
    defer lb.mutex.RUnlock()
    
    if len(lb.restaurants) == 0 {
        return nil, errors.New("no restaurants available")
    }
    
    // Find next healthy restaurant
    attempts := 0
    maxAttempts := len(lb.restaurants)
    
    for attempts < maxAttempts {
        // Get current index and increment atomically
        index := atomic.AddUint64(&lb.current, 1) % uint64(len(lb.restaurants))
        restaurant := lb.restaurants[index]
        
        // Check if restaurant is healthy
        if restaurant.IsAvailable() {
            log.Printf("🎯 Selected restaurant: %s (attempt %d)", restaurant.ID, attempts+1)
            return restaurant, nil
        }
        
        attempts++
        log.Printf("⚠️ Restaurant %s unavailable, trying next...", restaurant.ID)
    }
    
    return nil, errors.New("no healthy restaurants available")
}

// GetRestaurantStats returns statistics about restaurants
func (lb *SwiggyLoadBalancer) GetRestaurantStats() map[string]interface{} {
    lb.mutex.RLock()
    defer lb.mutex.RUnlock()
    
    total := len(lb.restaurants)
    healthy := 0
    zoneCount := make(map[string]int)
    
    for _, restaurant := range lb.restaurants {
        if restaurant.IsAvailable() {
            healthy++
        }
        zoneCount[restaurant.Zone]++
    }
    
    stats := map[string]interface{}{
        "total_restaurants": total,
        "healthy_restaurants": healthy,
        "unhealthy_restaurants": total - healthy,
        "zones": zoneCount,
        "health_percentage": float64(healthy) / float64(total) * 100,
    }
    
    return stats
}

// HealthChecker performs periodic health checks on restaurants
type HealthChecker struct {
    loadBalancer *SwiggyLoadBalancer
    interval     time.Duration
    timeout      time.Duration
    ctx          context.Context
    cancel       context.CancelFunc
}

// NewHealthChecker creates a new health checker
func NewHealthChecker(lb *SwiggyLoadBalancer, interval, timeout time.Duration) *HealthChecker {
    ctx, cancel := context.WithCancel(context.Background())
    return &HealthChecker{
        loadBalancer: lb,
        interval:     interval,
        timeout:      timeout,
        ctx:          ctx,
        cancel:       cancel,
    }
}

// Start begins health checking
func (hc *HealthChecker) Start() {
    go hc.healthCheckLoop()
    log.Printf("🔍 Health checker started (interval: %v)", hc.interval)
}

// Stop stops health checking
func (hc *HealthChecker) Stop() {
    hc.cancel()
    log.Printf("🛑 Health checker stopped")
}

// healthCheckLoop performs periodic health checks
func (hc *HealthChecker) healthCheckLoop() {
    ticker := time.NewTicker(hc.interval)
    defer ticker.Stop()
    
    for {
        select {
        case <-hc.ctx.Done():
            return
        case <-ticker.C:
            hc.checkAllRestaurants()
        }
    }
}

// checkAllRestaurants checks health of all restaurants
func (hc *HealthChecker) checkAllRestaurants() {
    hc.loadBalancer.mutex.RLock()
    restaurants := make([]*Restaurant, len(hc.loadBalancer.restaurants))
    copy(restaurants, hc.loadBalancer.restaurants)
    hc.loadBalancer.mutex.RUnlock()
    
    // Check each restaurant concurrently
    var wg sync.WaitGroup
    for _, restaurant := range restaurants {
        wg.Add(1)
        go func(r *Restaurant) {
            defer wg.Done()
            hc.checkRestaurantHealth(r)
        }(restaurant)
    }
    wg.Wait()
}

// checkRestaurantHealth checks health of a single restaurant
func (hc *HealthChecker) checkRestaurantHealth(restaurant *Restaurant) {
    ctx, cancel := context.WithTimeout(hc.ctx, hc.timeout)
    defer cancel()
    
    // Health check URL
    healthURL := fmt.Sprintf("%s/health", restaurant.URL.String())
    
    req, err := http.NewRequestWithContext(ctx, "GET", healthURL, nil)
    if err != nil {
        restaurant.SetHealth(false)
        return
    }
    
    client := &http.Client{Timeout: hc.timeout}
    resp, err := client.Do(req)
    
    if err != nil {
        log.Printf("💔 Health check failed for %s: %v", restaurant.ID, err)
        restaurant.SetHealth(false)
        return
    }
    defer resp.Body.Close()
    
    // Consider 2xx status codes as healthy
    isHealthy := resp.StatusCode >= 200 && resp.StatusCode < 300
    restaurant.SetHealth(isHealthy)
    
    if isHealthy {
        log.Printf("💚 Restaurant %s healthy", restaurant.ID)
    } else {
        log.Printf("💛 Restaurant %s unhealthy (status: %d)", restaurant.ID, resp.StatusCode)
    }
}

// SwiggyProxy implements HTTP proxy with load balancing
type SwiggyProxy struct {
    loadBalancer *SwiggyLoadBalancer
    healthChecker *HealthChecker
}

// NewSwiggyProxy creates a new proxy with load balancing
func NewSwiggyProxy(lb *SwiggyLoadBalancer) *SwiggyProxy {
    proxy := &SwiggyProxy{
        loadBalancer: lb,
    }
    
    // Start health checker
    proxy.healthChecker = NewHealthChecker(lb, 30*time.Second, 5*time.Second)
    proxy.healthChecker.Start()
    
    return proxy
}

// ServeHTTP implements http.Handler interface
func (p *SwiggyProxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // Get next available restaurant
    restaurant, err := p.loadBalancer.GetNextRestaurant()
    if err != nil {
        log.Printf("❌ No restaurants available: %v", err)
        http.Error(w, "Service Unavailable", http.StatusServiceUnavailable)
        return
    }
    
    // Create reverse proxy
    proxy := httputil.NewSingleHostReverseProxy(restaurant.URL)
    
    // Add custom headers
    r.Header.Set("X-Forwarded-Restaurant", restaurant.ID)
    r.Header.Set("X-Forwarded-Zone", restaurant.Zone)
    
    // Log request routing
    log.Printf("🔀 Routing request %s %s to restaurant %s", 
               r.Method, r.URL.Path, restaurant.ID)
    
    // Proxy the request
    proxy.ServeHTTP(w, r)
}

// Stop gracefully shuts down the proxy
func (p *SwiggyProxy) Stop() {
    if p.healthChecker != nil {
        p.healthChecker.Stop()
    }
}

// Example usage and demo
func main() {
    // Create load balancer
    lb := NewSwiggyLoadBalancer()
    
    // Add restaurants (backend servers)
    restaurants := []*Restaurant{
        {
            ID:       "rest-mumbai-001",
            URL:      mustParseURL("http://localhost:8081"),
            IsHealthy: true,
            Weight:   10,
            Zone:     "mumbai",
            Metadata: map[string]string{
                "cuisine": "north-indian",
                "capacity": "100",
            },
        },
        {
            ID:       "rest-mumbai-002", 
            URL:      mustParseURL("http://localhost:8082"),
            IsHealthy: true,
            Weight:   15,
            Zone:     "mumbai",
            Metadata: map[string]string{
                "cuisine": "south-indian",
                "capacity": "150",
            },
        },
        {
            ID:       "rest-delhi-001",
            URL:      mustParseURL("http://localhost:8083"),
            IsHealthy: true,
            Weight:   12,
            Zone:     "delhi",
            Metadata: map[string]string{
                "cuisine": "punjabi",
                "capacity": "120",
            },
        },
    }
    
    // Add restaurants to load balancer
    for _, restaurant := range restaurants {
        lb.AddRestaurant(restaurant)
    }
    
    // Create proxy
    proxy := NewSwiggyProxy(lb)
    defer proxy.Stop()
    
    // Demo: Show round-robin behavior
    fmt.Println("\n🏪 Swiggy Load Balancer Demo")
    fmt.Println("=" * 50)
    
    fmt.Println("\n1. 🔄 Round-robin restaurant selection:")
    for i := 0; i < 6; i++ {
        restaurant, err := lb.GetNextRestaurant()
        if err != nil {
            fmt.Printf("   ❌ Error: %v\n", err)
            continue
        }
        fmt.Printf("   Order %d -> Restaurant: %s (%s)\n", 
                   i+1, restaurant.ID, restaurant.Zone)
    }
    
    fmt.Println("\n2. 📊 Restaurant statistics:")
    stats := lb.GetRestaurantStats()
    fmt.Printf("   🏪 Total restaurants: %d\n", stats["total_restaurants"])
    fmt.Printf("   💚 Healthy restaurants: %d\n", stats["healthy_restaurants"])
    fmt.Printf("   💔 Unhealthy restaurants: %d\n", stats["unhealthy_restaurants"])
    fmt.Printf("   📈 Health percentage: %.1f%%\n", stats["health_percentage"])
    fmt.Printf("   🌍 Zone distribution: %v\n", stats["zones"])
    
    fmt.Println("\n3. 🔧 Testing restaurant removal:")
    err := lb.RemoveRestaurant("rest-mumbai-002")
    if err != nil {
        fmt.Printf("   ❌ Error removing restaurant: %v\n", err)
    } else {
        fmt.Printf("   ✅ Restaurant removed successfully\n")
    }
    
    fmt.Println("\n4. 🔄 Round-robin after removal:")
    for i := 0; i < 4; i++ {
        restaurant, err := lb.GetNextRestaurant()
        if err != nil {
            fmt.Printf("   ❌ Error: %v\n", err)
            continue
        }
        fmt.Printf("   Order %d -> Restaurant: %s (%s)\n", 
                   i+1, restaurant.ID, restaurant.Zone)
    }
    
    // Start HTTP server for demo
    fmt.Println("\n🌐 Starting HTTP proxy server on :8080")
    fmt.Println("📝 Test with: curl http://localhost:8080/api/orders")
    fmt.Println("⏰ Health checks running every 30 seconds")
    fmt.Println("🛑 Press Ctrl+C to stop")
    
    server := &http.Server{
        Addr:    ":8080",
        Handler: proxy,
    }
    
    log.Fatal(server.ListenAndServe())
}

// mustParseURL parses URL or panics
func mustParseURL(rawURL string) *url.URL {
    url, err := url.Parse(rawURL)
    if err != nil {
        panic(fmt.Sprintf("Invalid URL: %s", rawURL))
    }
    return url
}
```

This is the complete first Go example. Let me continue with the other examples and complete the Go load balancing implementation.
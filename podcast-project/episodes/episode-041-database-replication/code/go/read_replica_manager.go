/*
Episode 41: Database Replication Strategies - Read Replica Manager
Advanced read replica configuration and management in Go

यह implementation demonstrate करती है कि कैसे production-grade systems में
read replicas को efficiently manage किया जाता है। जैसे Mumbai की local trains
में different lines (Western, Central, Harbor) अलग-अलग routes serve करती हैं
लेकिन same destination (downtown Mumbai) पहुंचाती हैं, वैसे ही read replicas भी
same data को अलग-अलग purposes के लिए serve करती हैं।

Real-world Usage:
- HDFC Bank: Account queries को multiple read replicas में distribute करना
- Flipkart: Product catalog reads को geographic regions में optimize करना
- Zomato: Restaurant data को delivery partners के लिए dedicated replicas

Author: Hindi Tech Podcast Team
Episode: 41 - Database Replication Strategies
*/

package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"sort"
	"strconv"
	"sync"
	"sync/atomic"
	"time"

	_ "github.com/lib/pq"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// ReplicationLagThreshold defines acceptable lag limits
const (
	MaxAcceptableLag     = 5 * time.Second
	CriticalLagThreshold = 30 * time.Second
	HealthCheckInterval  = 10 * time.Second
	MetricsPort         = ":8080"
)

// ReadReplicaType defines different types of read replicas
type ReadReplicaType string

const (
	AnalyticsReplica    ReadReplicaType = "analytics"
	ReportingReplica    ReadReplicaType = "reporting"
	ApplicationReplica  ReadReplicaType = "application"
	GeographicReplica   ReadReplicaType = "geographic"
	DisasterRecoveryReplica ReadReplicaType = "disaster_recovery"
)

// ReadReplica represents a database read replica
type ReadReplica struct {
	ID              string          `json:"id"`
	Name            string          `json:"name"`
	Type            ReadReplicaType `json:"type"`
	ConnectionString string         `json:"connection_string"`
	Region          string          `json:"region"`
	DataCenter      string          `json:"datacenter"`
	Weight          int             `json:"weight"`          // Load balancing weight
	MaxConnections  int             `json:"max_connections"`
	IsHealthy       bool            `json:"is_healthy"`
	LastHealthCheck time.Time       `json:"last_health_check"`
	ReplicationLag  time.Duration   `json:"replication_lag"`
	ActiveConnections int           `json:"active_connections"`
	QueriesPerSecond float64        `json:"queries_per_second"`
	AvgResponseTime time.Duration   `json:"avg_response_time"`
	
	// Geographic optimization
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
	
	// Database connection
	db *sql.DB
	
	// Metrics
	totalQueries    int64
	failedQueries   int64
	lastQueryTime   time.Time
	responseTimes   []time.Duration
	responseTimeMux sync.Mutex
}

// ReadReplicaManager manages multiple read replicas
type ReadReplicaManager struct {
	replicas    map[string]*ReadReplica
	replicasMux sync.RWMutex
	
	// Load balancing strategies
	loadBalancer LoadBalancer
	
	// Health monitoring
	healthChecker *HealthChecker
	
	// Metrics
	prometheus struct {
		queriesTotal     *prometheus.CounterVec
		queryDuration    *prometheus.HistogramVec
		replicationLag   *prometheus.GaugeVec
		healthyReplicas  *prometheus.GaugeVec
	}
	
	// Geographic routing
	geoRouter *GeographicRouter
	
	// Query routing rules
	routingRules map[string]RoutingRule
}

// LoadBalancer interface for different load balancing strategies
type LoadBalancer interface {
	SelectReplica(replicas []*ReadReplica, query QueryInfo) (*ReadReplica, error)
}

// QueryInfo contains information about the query
type QueryInfo struct {
	Type        string                 `json:"type"`        // SELECT, analytics, reporting
	Tables      []string              `json:"tables"`      // Tables being queried
	UserRegion  string                `json:"user_region"` // Geographic region of user
	Priority    int                   `json:"priority"`    // Query priority (1-10)
	ReadOnly    bool                  `json:"read_only"`   // Is this a read-only query
	Metadata    map[string]interface{} `json:"metadata"`    // Additional query metadata
}

// RoutingRule defines how queries should be routed
type RoutingRule struct {
	Name        string                `json:"name"`
	Conditions  map[string]interface{} `json:"conditions"`
	TargetTypes []ReadReplicaType     `json:"target_types"`
	Priority    int                   `json:"priority"`
}

// HealthChecker monitors replica health
type HealthChecker struct {
	manager    *ReadReplicaManager
	stopCh     chan struct{}
	healthData map[string]*HealthData
	healthMux  sync.RWMutex
}

// HealthData stores health metrics for a replica
type HealthData struct {
	IsHealthy           bool          `json:"is_healthy"`
	LastCheck          time.Time     `json:"last_check"`
	ReplicationLag     time.Duration `json:"replication_lag"`
	ConsecutiveFailures int          `json:"consecutive_failures"`
	ResponseTime       time.Duration `json:"response_time"`
	ConnectionCount    int           `json:"connection_count"`
}

// GeographicRouter handles geographic-based routing
type GeographicRouter struct {
	regionMappings map[string][]string // Region -> Replica IDs
}

// RoundRobinBalancer implements round-robin load balancing
type RoundRobinBalancer struct {
	counter int64
}

// WeightedRoundRobinBalancer implements weighted round-robin
type WeightedRoundRobinBalancer struct {
	counters map[string]int64
	mutex    sync.Mutex
}

// LeastConnectionsBalancer routes to replica with least connections
type LeastConnectionsBalancer struct{}

// GeographicBalancer routes based on geographic proximity
type GeographicBalancer struct {
	geoRouter *GeographicRouter
}

// NewReadReplicaManager creates a new replica manager
func NewReadReplicaManager() *ReadReplicaManager {
	manager := &ReadReplicaManager{
		replicas:     make(map[string]*ReadReplica),
		routingRules: make(map[string]RoutingRule),
		geoRouter:    NewGeographicRouter(),
	}
	
	// Initialize Prometheus metrics
	manager.initPrometheusMetrics()
	
	// Set default load balancer
	manager.loadBalancer = &WeightedRoundRobinBalancer{
		counters: make(map[string]int64),
	}
	
	// Start health checker
	manager.healthChecker = &HealthChecker{
		manager:    manager,
		stopCh:     make(chan struct{}),
		healthData: make(map[string]*HealthData),
	}
	
	return manager
}

// Initialize Prometheus metrics
func (rm *ReadReplicaManager) initPrometheusMetrics() {
	rm.prometheus.queriesTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "replica_queries_total",
			Help: "Total number of queries processed by read replicas",
		},
		[]string{"replica_id", "replica_type", "status"},
	)
	
	rm.prometheus.queryDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "replica_query_duration_seconds",
			Help:    "Query duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"replica_id", "replica_type"},
	)
	
	rm.prometheus.replicationLag = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "replica_replication_lag_seconds",
			Help: "Replication lag in seconds",
		},
		[]string{"replica_id", "replica_type"},
	)
	
	rm.prometheus.healthyReplicas = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "healthy_replicas_count",
			Help: "Number of healthy read replicas",
		},
		[]string{"replica_type", "region"},
	)
	
	// Register metrics with Prometheus
	prometheus.MustRegister(
		rm.prometheus.queriesTotal,
		rm.prometheus.queryDuration,
		rm.prometheus.replicationLag,
		rm.prometheus.healthyReplicas,
	)
}

// AddReplica adds a new read replica to the manager
func (rm *ReadReplicaManager) AddReplica(replica *ReadReplica) error {
	rm.replicasMux.Lock()
	defer rm.replicasMux.Unlock()
	
	// Initialize database connection
	db, err := sql.Open("postgres", replica.ConnectionString)
	if err != nil {
		return fmt.Errorf("failed to connect to replica %s: %v", replica.ID, err)
	}
	
	// Configure connection pool
	db.SetMaxOpenConns(replica.MaxConnections)
	db.SetMaxIdleConns(replica.MaxConnections / 4)
	db.SetConnMaxLifetime(5 * time.Minute)
	
	// Test connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	if err := db.PingContext(ctx); err != nil {
		db.Close()
		return fmt.Errorf("replica %s is not reachable: %v", replica.ID, err)
	}
	
	replica.db = db
	replica.IsHealthy = true
	replica.LastHealthCheck = time.Now()
	replica.responseTimes = make([]time.Duration, 0, 100)
	
	rm.replicas[replica.ID] = replica
	
	// Update geographic router
	rm.geoRouter.AddReplica(replica)
	
	log.Printf("Added read replica: %s (%s) in %s", replica.Name, replica.Type, replica.Region)
	return nil
}

// RemoveReplica removes a replica from the manager
func (rm *ReadReplicaManager) RemoveReplica(replicaID string) error {
	rm.replicasMux.Lock()
	defer rm.replicasMux.Unlock()
	
	replica, exists := rm.replicas[replicaID]
	if !exists {
		return fmt.Errorf("replica %s not found", replicaID)
	}
	
	// Close database connection
	if replica.db != nil {
		replica.db.Close()
	}
	
	delete(rm.replicas, replicaID)
	
	log.Printf("Removed read replica: %s", replicaID)
	return nil
}

// ExecuteQuery executes a query on an appropriate read replica
func (rm *ReadReplicaManager) ExecuteQuery(ctx context.Context, query string, queryInfo QueryInfo) (*sql.Rows, error) {
	startTime := time.Now()
	
	// Select appropriate replica
	replica, err := rm.selectReplica(queryInfo)
	if err != nil {
		return nil, fmt.Errorf("failed to select replica: %v", err)
	}
	
	// Execute query
	rows, err := replica.db.QueryContext(ctx, query)
	duration := time.Since(startTime)
	
	// Update metrics
	atomic.AddInt64(&replica.totalQueries, 1)
	if err != nil {
		atomic.AddInt64(&replica.failedQueries, 1)
		rm.prometheus.queriesTotal.WithLabelValues(
			replica.ID, string(replica.Type), "failed").Inc()
		return nil, fmt.Errorf("query failed on replica %s: %v", replica.ID, err)
	}
	
	// Record successful query
	rm.prometheus.queriesTotal.WithLabelValues(
		replica.ID, string(replica.Type), "success").Inc()
	rm.prometheus.queryDuration.WithLabelValues(
		replica.ID, string(replica.Type)).Observe(duration.Seconds())
	
	// Update replica metrics
	replica.lastQueryTime = time.Now()
	replica.responseTimeMux.Lock()
	replica.responseTimes = append(replica.responseTimes, duration)
	if len(replica.responseTimes) > 100 {
		replica.responseTimes = replica.responseTimes[1:]
	}
	replica.responseTimeMux.Unlock()
	
	log.Printf("Query executed on replica %s in %v", replica.ID, duration)
	return rows, nil
}

// selectReplica selects the best replica for a query
func (rm *ReadReplicaManager) selectReplica(queryInfo QueryInfo) (*ReadReplica, error) {
	rm.replicasMux.RLock()
	defer rm.replicasMux.RUnlock()
	
	// Get healthy replicas
	var healthyReplicas []*ReadReplica
	for _, replica := range rm.replicas {
		if replica.IsHealthy {
			healthyReplicas = append(healthyReplicas, replica)
		}
	}
	
	if len(healthyReplicas) == 0 {
		return nil, fmt.Errorf("no healthy replicas available")
	}
	
	// Apply routing rules
	filteredReplicas := rm.applyRoutingRules(healthyReplicas, queryInfo)
	if len(filteredReplicas) == 0 {
		filteredReplicas = healthyReplicas // Fallback to all healthy replicas
	}
	
	// Use load balancer to select final replica
	return rm.loadBalancer.SelectReplica(filteredReplicas, queryInfo)
}

// applyRoutingRules filters replicas based on routing rules
func (rm *ReadReplicaManager) applyRoutingRules(replicas []*ReadReplica, queryInfo QueryInfo) []*ReadReplica {
	var filteredReplicas []*ReadReplica
	
	// Sort routing rules by priority
	var rules []RoutingRule
	for _, rule := range rm.routingRules {
		rules = append(rules, rule)
	}
	sort.Slice(rules, func(i, j int) bool {
		return rules[i].Priority > rules[j].Priority
	})
	
	// Apply each rule
	for _, rule := range rules {
		if rm.matchesRule(rule, queryInfo) {
			// Filter replicas by target types
			for _, replica := range replicas {
				for _, targetType := range rule.TargetTypes {
					if replica.Type == targetType {
						filteredReplicas = append(filteredReplicas, replica)
						break
					}
				}
			}
			if len(filteredReplicas) > 0 {
				log.Printf("Applied routing rule: %s, filtered to %d replicas", 
						  rule.Name, len(filteredReplicas))
				return filteredReplicas
			}
		}
	}
	
	return replicas
}

// matchesRule checks if query matches a routing rule
func (rm *ReadReplicaManager) matchesRule(rule RoutingRule, queryInfo QueryInfo) bool {
	for key, expectedValue := range rule.Conditions {
		switch key {
		case "query_type":
			if queryInfo.Type != expectedValue.(string) {
				return false
			}
		case "user_region":
			if queryInfo.UserRegion != expectedValue.(string) {
				return false
			}
		case "min_priority":
			if queryInfo.Priority < expectedValue.(int) {
				return false
			}
		case "tables_include":
			expectedTables := expectedValue.([]string)
			for _, expectedTable := range expectedTables {
				found := false
				for _, table := range queryInfo.Tables {
					if table == expectedTable {
						found = true
						break
					}
				}
				if !found {
					return false
				}
			}
		}
	}
	return true
}

// StartHealthChecking starts the health checking goroutine
func (rm *ReadReplicaManager) StartHealthChecking() {
	go rm.healthChecker.Run()
	log.Println("Started health checking for read replicas")
}

// StopHealthChecking stops the health checking
func (rm *ReadReplicaManager) StopHealthChecking() {
	close(rm.healthChecker.stopCh)
	log.Println("Stopped health checking for read replicas")
}

// Run starts the health checking loop
func (hc *HealthChecker) Run() {
	ticker := time.NewTicker(HealthCheckInterval)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			hc.performHealthChecks()
		case <-hc.stopCh:
			return
		}
	}
}

// performHealthChecks checks health of all replicas
func (hc *HealthChecker) performHealthChecks() {
	hc.manager.replicasMux.RLock()
	replicas := make([]*ReadReplica, 0, len(hc.manager.replicas))
	for _, replica := range hc.manager.replicas {
		replicas = append(replicas, replica)
	}
	hc.manager.replicasMux.RUnlock()
	
	var wg sync.WaitGroup
	for _, replica := range replicas {
		wg.Add(1)
		go func(r *ReadReplica) {
			defer wg.Done()
			hc.checkReplicaHealth(r)
		}(replica)
	}
	wg.Wait()
	
	// Update Prometheus metrics
	hc.updateHealthMetrics()
}

// checkReplicaHealth checks health of a single replica
func (hc *HealthChecker) checkReplicaHealth(replica *ReadReplica) {
	startTime := time.Now()
	
	hc.healthMux.Lock()
	healthData, exists := hc.healthData[replica.ID]
	if !exists {
		healthData = &HealthData{}
		hc.healthData[replica.ID] = healthData
	}
	hc.healthMux.Unlock()
	
	// Perform health checks
	isHealthy := true
	var replicationLag time.Duration
	var connectionCount int
	
	// 1. Database connectivity check
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	if err := replica.db.PingContext(ctx); err != nil {
		log.Printf("Replica %s failed ping: %v", replica.ID, err)
		isHealthy = false
	}
	
	// 2. Replication lag check
	if isHealthy {
		lag, err := hc.checkReplicationLag(replica)
		if err != nil {
			log.Printf("Replica %s replication lag check failed: %v", replica.ID, err)
			replicationLag = CriticalLagThreshold
		} else {
			replicationLag = lag
		}
		
		// Consider replica unhealthy if lag is too high
		if replicationLag > MaxAcceptableLag {
			log.Printf("Replica %s has high replication lag: %v", replica.ID, replicationLag)
			isHealthy = false
		}
	}
	
	// 3. Connection count check
	if isHealthy {
		count, err := hc.getConnectionCount(replica)
		if err != nil {
			log.Printf("Replica %s connection count check failed: %v", replica.ID, err)
		} else {
			connectionCount = count
			if count >= replica.MaxConnections {
				log.Printf("Replica %s at max connections: %d", replica.ID, count)
				isHealthy = false
			}
		}
	}
	
	responseTime := time.Since(startTime)
	
	// Update health data
	hc.healthMux.Lock()
	healthData.LastCheck = time.Now()
	healthData.IsHealthy = isHealthy
	healthData.ReplicationLag = replicationLag
	healthData.ResponseTime = responseTime
	healthData.ConnectionCount = connectionCount
	
	if !isHealthy {
		healthData.ConsecutiveFailures++
	} else {
		healthData.ConsecutiveFailures = 0
	}
	hc.healthMux.Unlock()
	
	// Update replica status
	replica.IsHealthy = isHealthy
	replica.LastHealthCheck = time.Now()
	replica.ReplicationLag = replicationLag
	replica.ActiveConnections = connectionCount
	
	// Update Prometheus metrics
	hc.manager.prometheus.replicationLag.WithLabelValues(
		replica.ID, string(replica.Type)).Set(replicationLag.Seconds())
}

// checkReplicationLag checks the replication lag for a replica
func (hc *HealthChecker) checkReplicationLag(replica *ReadReplica) (time.Duration, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	
	// Query to check replication lag (PostgreSQL specific)
	query := `
		SELECT CASE 
			WHEN pg_is_in_recovery() THEN 
				EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
			ELSE 0
		END AS lag_seconds`
	
	var lagSeconds float64
	err := replica.db.QueryRowContext(ctx, query).Scan(&lagSeconds)
	if err != nil {
		return 0, fmt.Errorf("failed to query replication lag: %v", err)
	}
	
	return time.Duration(lagSeconds * float64(time.Second)), nil
}

// getConnectionCount gets the current connection count
func (hc *HealthChecker) getConnectionCount(replica *ReadReplica) (int, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	
	query := `SELECT count(*) FROM pg_stat_activity WHERE state = 'active'`
	
	var count int
	err := replica.db.QueryRowContext(ctx, query).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to query connection count: %v", err)
	}
	
	return count, nil
}

// updateHealthMetrics updates Prometheus health metrics
func (hc *HealthChecker) updateHealthMetrics() {
	hc.manager.replicasMux.RLock()
	defer hc.manager.replicasMux.RUnlock()
	
	healthyCounts := make(map[string]map[string]int) // type -> region -> count
	
	for _, replica := range hc.manager.replicas {
		replicaType := string(replica.Type)
		region := replica.Region
		
		if healthyCounts[replicaType] == nil {
			healthyCounts[replicaType] = make(map[string]int)
		}
		
		if replica.IsHealthy {
			healthyCounts[replicaType][region]++
		}
	}
	
	// Update Prometheus metrics
	for replicaType, regions := range healthyCounts {
		for region, count := range regions {
			hc.manager.prometheus.healthyReplicas.WithLabelValues(
				replicaType, region).Set(float64(count))
		}
	}
}

// NewGeographicRouter creates a new geographic router
func NewGeographicRouter() *GeographicRouter {
	return &GeographicRouter{
		regionMappings: make(map[string][]string),
	}
}

// AddReplica adds a replica to geographic routing
func (gr *GeographicRouter) AddReplica(replica *ReadReplica) {
	if gr.regionMappings[replica.Region] == nil {
		gr.regionMappings[replica.Region] = make([]string, 0)
	}
	gr.regionMappings[replica.Region] = append(gr.regionMappings[replica.Region], replica.ID)
}

// GetNearestReplicas returns replicas nearest to a geographic region
func (gr *GeographicRouter) GetNearestReplicas(userRegion string, replicas []*ReadReplica) []*ReadReplica {
	// First, try exact region match
	if replicaIDs, exists := gr.regionMappings[userRegion]; exists {
		var nearestReplicas []*ReadReplica
		for _, replica := range replicas {
			for _, id := range replicaIDs {
				if replica.ID == id {
					nearestReplicas = append(nearestReplicas, replica)
					break
				}
			}
		}
		if len(nearestReplicas) > 0 {
			return nearestReplicas
		}
	}
	
	// If no exact match, return all replicas (could implement distance calculation)
	return replicas
}

// Load balancer implementations

// SelectReplica selects replica using round-robin
func (rrb *RoundRobinBalancer) SelectReplica(replicas []*ReadReplica, query QueryInfo) (*ReadReplica, error) {
	if len(replicas) == 0 {
		return nil, fmt.Errorf("no replicas available")
	}
	
	count := atomic.AddInt64(&rrb.counter, 1)
	index := (count - 1) % int64(len(replicas))
	return replicas[index], nil
}

// SelectReplica selects replica using weighted round-robin
func (wrrb *WeightedRoundRobinBalancer) SelectReplica(replicas []*ReadReplica, query QueryInfo) (*ReadReplica, error) {
	if len(replicas) == 0 {
		return nil, fmt.Errorf("no replicas available")
	}
	
	wrrb.mutex.Lock()
	defer wrrb.mutex.Unlock()
	
	// Calculate total weight
	totalWeight := 0
	for _, replica := range replicas {
		totalWeight += replica.Weight
	}
	
	if totalWeight == 0 {
		// If no weights set, use round-robin
		return replicas[rand.Intn(len(replicas))], nil
	}
	
	// Select based on cumulative weights
	target := rand.Intn(totalWeight)
	cumulative := 0
	
	for _, replica := range replicas {
		cumulative += replica.Weight
		if target < cumulative {
			return replica, nil
		}
	}
	
	return replicas[0], nil
}

// SelectReplica selects replica with least connections
func (lcb *LeastConnectionsBalancer) SelectReplica(replicas []*ReadReplica, query QueryInfo) (*ReadReplica, error) {
	if len(replicas) == 0 {
		return nil, fmt.Errorf("no replicas available")
	}
	
	var selectedReplica *ReadReplica
	minConnections := int(^uint(0) >> 1) // Max int
	
	for _, replica := range replicas {
		if replica.ActiveConnections < minConnections {
			minConnections = replica.ActiveConnections
			selectedReplica = replica
		}
	}
	
	return selectedReplica, nil
}

// SelectReplica selects replica based on geographic proximity
func (gb *GeographicBalancer) SelectReplica(replicas []*ReadReplica, query QueryInfo) (*ReadReplica, error) {
	if len(replicas) == 0 {
		return nil, fmt.Errorf("no replicas available")
	}
	
	// Get nearest replicas based on user region
	nearestReplicas := gb.geoRouter.GetNearestReplicas(query.UserRegion, replicas)
	
	// Use least connections among nearest replicas
	lcb := &LeastConnectionsBalancer{}
	return lcb.SelectReplica(nearestReplicas, query)
}

// AddRoutingRule adds a new routing rule
func (rm *ReadReplicaManager) AddRoutingRule(rule RoutingRule) {
	rm.routingRules[rule.Name] = rule
	log.Printf("Added routing rule: %s", rule.Name)
}

// GetReplicaStats returns statistics for all replicas
func (rm *ReadReplicaManager) GetReplicaStats() map[string]interface{} {
	rm.replicasMux.RLock()
	defer rm.replicasMux.RUnlock()
	
	stats := make(map[string]interface{})
	stats["total_replicas"] = len(rm.replicas)
	
	healthyCount := 0
	replicaStats := make(map[string]interface{})
	
	for id, replica := range rm.replicas {
		if replica.IsHealthy {
			healthyCount++
		}
		
		replica.responseTimeMux.Lock()
		avgResponseTime := time.Duration(0)
		if len(replica.responseTimes) > 0 {
			total := time.Duration(0)
			for _, rt := range replica.responseTimes {
				total += rt
			}
			avgResponseTime = total / time.Duration(len(replica.responseTimes))
		}
		replica.responseTimeMux.Unlock()
		
		replicaStats[id] = map[string]interface{}{
			"name":               replica.Name,
			"type":               replica.Type,
			"region":             replica.Region,
			"is_healthy":         replica.IsHealthy,
			"replication_lag_ms": replica.ReplicationLag.Milliseconds(),
			"active_connections": replica.ActiveConnections,
			"total_queries":      atomic.LoadInt64(&replica.totalQueries),
			"failed_queries":     atomic.LoadInt64(&replica.failedQueries),
			"avg_response_time_ms": avgResponseTime.Milliseconds(),
			"last_query_time":    replica.lastQueryTime,
		}
	}
	
	stats["healthy_replicas"] = healthyCount
	stats["replicas"] = replicaStats
	
	return stats
}

// SetupHTTPEndpoints sets up HTTP endpoints for monitoring
func (rm *ReadReplicaManager) SetupHTTPEndpoints() {
	http.HandleFunc("/health", rm.healthHandler)
	http.HandleFunc("/stats", rm.statsHandler)
	http.HandleFunc("/replicas", rm.replicasHandler)
	http.Handle("/metrics", promhttp.Handler())
	
	log.Printf("HTTP endpoints available at %s", MetricsPort)
}

// healthHandler provides health check endpoint
func (rm *ReadReplicaManager) healthHandler(w http.ResponseWriter, r *http.Request) {
	rm.replicasMux.RLock()
	defer rm.replicasMux.RUnlock()
	
	healthy := 0
	total := len(rm.replicas)
	
	for _, replica := range rm.replicas {
		if replica.IsHealthy {
			healthy++
		}
	}
	
	status := "healthy"
	if healthy == 0 {
		status = "unhealthy"
		w.WriteHeader(http.StatusServiceUnavailable)
	} else if healthy < total {
		status = "degraded"
	}
	
	response := map[string]interface{}{
		"status":          status,
		"healthy_count":   healthy,
		"total_count":     total,
		"timestamp":       time.Now(),
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// statsHandler provides detailed statistics
func (rm *ReadReplicaManager) statsHandler(w http.ResponseWriter, r *http.Request) {
	stats := rm.GetReplicaStats()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

// replicasHandler provides replica management endpoints
func (rm *ReadReplicaManager) replicasHandler(w http.ResponseWriter, r *http.Request) {
	rm.replicasMux.RLock()
	replicas := make([]*ReadReplica, 0, len(rm.replicas))
	for _, replica := range rm.replicas {
		replicas = append(replicas, replica)
	}
	rm.replicasMux.RUnlock()
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(replicas)
}

// Close gracefully shuts down the replica manager
func (rm *ReadReplicaManager) Close() {
	log.Println("Shutting down Read Replica Manager...")
	
	// Stop health checking
	rm.StopHealthChecking()
	
	// Close all database connections
	rm.replicasMux.Lock()
	defer rm.replicasMux.Unlock()
	
	for _, replica := range rm.replicas {
		if replica.db != nil {
			replica.db.Close()
		}
	}
	
	log.Println("Read Replica Manager shutdown complete")
}

// Demo functions

// setupHDFCBankReplicas sets up HDFC Bank read replicas
func setupHDFCBankReplicas(manager *ReadReplicaManager) {
	// Mumbai Primary Region - Application Replicas
	mumbaiApp := &ReadReplica{
		ID:               "hdfc-mumbai-app-01",
		Name:             "HDFC Mumbai Application Replica",
		Type:             ApplicationReplica,
		ConnectionString: "postgres://hdfc_user:password@mumbai-app-db:5432/hdfc_banking",
		Region:           "mumbai",
		DataCenter:       "BKC-DC-01",
		Weight:           10,
		MaxConnections:   100,
		Latitude:         19.0760,
		Longitude:        72.8777,
	}
	
	// Bangalore - Analytics Replica
	bangaloreAnalytics := &ReadReplica{
		ID:               "hdfc-bangalore-analytics-01",
		Name:             "HDFC Bangalore Analytics Replica", 
		Type:             AnalyticsReplica,
		ConnectionString: "postgres://hdfc_analytics:password@bangalore-analytics-db:5432/hdfc_banking",
		Region:           "bangalore",
		DataCenter:       "BLR-DC-01",
		Weight:           5,
		MaxConnections:   50,
		Latitude:         12.9716,
		Longitude:        77.5946,
	}
	
	// Chennai - Reporting Replica
	chennaiReporting := &ReadReplica{
		ID:               "hdfc-chennai-reporting-01",
		Name:             "HDFC Chennai Reporting Replica",
		Type:             ReportingReplica,
		ConnectionString: "postgres://hdfc_reports:password@chennai-reporting-db:5432/hdfc_banking",
		Region:           "chennai",
		DataCenter:       "CHN-DC-01", 
		Weight:           8,
		MaxConnections:   75,
		Latitude:         13.0827,
		Longitude:        80.2707,
	}
	
	// Delhi - DR Replica
	delhiDR := &ReadReplica{
		ID:               "hdfc-delhi-dr-01",
		Name:             "HDFC Delhi Disaster Recovery Replica",
		Type:             DisasterRecoveryReplica,
		ConnectionString: "postgres://hdfc_dr:password@delhi-dr-db:5432/hdfc_banking",
		Region:           "delhi",
		DataCenter:       "DEL-DC-01",
		Weight:           3,
		MaxConnections:   200,
		Latitude:         28.7041,
		Longitude:        77.1025,
	}
	
	// Add replicas to manager
	replicas := []*ReadReplica{mumbaiApp, bangaloreAnalytics, chennaiReporting, delhiDR}
	for _, replica := range replicas {
		// Simulate database connection for demo
		replica.db = &sql.DB{} // Mock connection
		replica.IsHealthy = true
		replica.LastHealthCheck = time.Now()
		replica.responseTimes = make([]time.Duration, 0, 100)
		
		manager.replicasMux.Lock()
		manager.replicas[replica.ID] = replica
		manager.replicasMux.Unlock()
		
		log.Printf("✅ Added HDFC replica: %s (%s)", replica.Name, replica.Region)
	}
}

// setupFlipkartReplicas sets up Flipkart read replicas
func setupFlipkartReplicas(manager *ReadReplicaManager) {
	// Mumbai - Product Catalog
	mumbaiCatalog := &ReadReplica{
		ID:               "flipkart-mumbai-catalog-01",
		Name:             "Flipkart Mumbai Catalog Replica",
		Type:             ApplicationReplica,
		ConnectionString: "postgres://fk_catalog:password@mumbai-catalog-db:5432/flipkart_catalog",
		Region:           "mumbai",
		DataCenter:       "MUM-FK-01",
		Weight:           15,
		MaxConnections:   150,
		Latitude:         19.0760,
		Longitude:        72.8777,
	}
	
	// Bangalore - Analytics
	bangaloreAnalytics := &ReadReplica{
		ID:               "flipkart-bangalore-analytics-01", 
		Name:             "Flipkart Bangalore Analytics Replica",
		Type:             AnalyticsReplica,
		ConnectionString: "postgres://fk_analytics:password@bangalore-analytics-db:5432/flipkart_analytics",
		Region:           "bangalore",
		DataCenter:       "BLR-FK-01",
		Weight:           10,
		MaxConnections:   100,
		Latitude:         12.9716,
		Longitude:        77.5946,
	}
	
	// Delhi - Regional Catalog
	delhiRegional := &ReadReplica{
		ID:               "flipkart-delhi-regional-01",
		Name:             "Flipkart Delhi Regional Replica",
		Type:             GeographicReplica,
		ConnectionString: "postgres://fk_regional:password@delhi-regional-db:5432/flipkart_catalog",
		Region:           "delhi",
		DataCenter:       "DEL-FK-01",
		Weight:           12,
		MaxConnections:   120,
		Latitude:         28.7041,
		Longitude:        77.1025,
	}
	
	replicas := []*ReadReplica{mumbaiCatalog, bangaloreAnalytics, delhiRegional}
	for _, replica := range replicas {
		// Simulate database connection for demo
		replica.db = &sql.DB{} // Mock connection
		replica.IsHealthy = true
		replica.LastHealthCheck = time.Now()
		replica.responseTimes = make([]time.Duration, 0, 100)
		
		manager.replicasMux.Lock()
		manager.replicas[replica.ID] = replica
		manager.replicasMux.Unlock()
		
		log.Printf("✅ Added Flipkart replica: %s (%s)", replica.Name, replica.Region)
	}
}

// setupRoutingRules sets up intelligent routing rules
func setupRoutingRules(manager *ReadReplicaManager) {
	// Analytics queries go to analytics replicas
	analyticsRule := RoutingRule{
		Name: "analytics_routing",
		Conditions: map[string]interface{}{
			"query_type": "analytics",
		},
		TargetTypes: []ReadReplicaType{AnalyticsReplica},
		Priority:    10,
	}
	
	// Reporting queries go to reporting replicas
	reportingRule := RoutingRule{
		Name: "reporting_routing",
		Conditions: map[string]interface{}{
			"query_type": "reporting",
		},
		TargetTypes: []ReadReplicaType{ReportingReplica},
		Priority:    9,
	}
	
	// Regional queries go to geographic replicas
	regionalRule := RoutingRule{
		Name: "regional_routing", 
		Conditions: map[string]interface{}{
			"user_region": "delhi",
		},
		TargetTypes: []ReadReplicaType{GeographicReplica, ApplicationReplica},
		Priority:    8,
	}
	
	// High priority queries go to application replicas
	highPriorityRule := RoutingRule{
		Name: "high_priority_routing",
		Conditions: map[string]interface{}{
			"min_priority": 8,
		},
		TargetTypes: []ReadReplicaType{ApplicationReplica},
		Priority:    7,
	}
	
	rules := []RoutingRule{analyticsRule, reportingRule, regionalRule, highPriorityRule}
	for _, rule := range rules {
		manager.AddRoutingRule(rule)
	}
	
	log.Println("✅ Added intelligent routing rules")
}

// simulateQueries simulates various types of queries
func simulateQueries(manager *ReadReplicaManager) {
	queries := []struct {
		name      string
		queryInfo QueryInfo
		query     string
	}{
		{
			name: "Account Balance Query",
			queryInfo: QueryInfo{
				Type:       "application",
				Tables:     []string{"accounts", "transactions"},
				UserRegion: "mumbai",
				Priority:   9,
				ReadOnly:   true,
			},
			query: "SELECT balance FROM accounts WHERE account_id = ?",
		},
		{
			name: "Analytics Query",
			queryInfo: QueryInfo{
				Type:       "analytics",
				Tables:     []string{"transactions", "customers"},
				UserRegion: "bangalore",
				Priority:   5,
				ReadOnly:   true,
			},
			query: "SELECT COUNT(*) FROM transactions WHERE date >= ?",
		},
		{
			name: "Reporting Query", 
			queryInfo: QueryInfo{
				Type:       "reporting",
				Tables:     []string{"accounts", "branches"},
				UserRegion: "chennai",
				Priority:   3,
				ReadOnly:   true,
			},
			query: "SELECT branch_id, COUNT(*) FROM accounts GROUP BY branch_id",
		},
		{
			name: "Regional Query",
			queryInfo: QueryInfo{
				Type:       "application",
				Tables:     []string{"products", "inventory"},
				UserRegion: "delhi",
				Priority:   7,
				ReadOnly:   true,
			},
			query: "SELECT * FROM products WHERE region = 'delhi'",
		},
	}
	
	log.Println("🔄 Starting query simulation...")
	
	for i := 0; i < 20; i++ {
		for _, q := range queries {
			go func(queryName string, info QueryInfo, sql string) {
				ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
				defer cancel()
				
				// Simulate query execution (mock since we don't have real DB)
				time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
				
				replica, err := manager.selectReplica(info)
				if err != nil {
					log.Printf("❌ Query failed: %s - %v", queryName, err)
					return
				}
				
				// Simulate successful query
				atomic.AddInt64(&replica.totalQueries, 1)
				replica.lastQueryTime = time.Now()
				
				responseTime := time.Duration(rand.Intn(200)) * time.Millisecond
				replica.responseTimeMux.Lock()
				replica.responseTimes = append(replica.responseTimes, responseTime)
				if len(replica.responseTimes) > 100 {
					replica.responseTimes = replica.responseTimes[1:]
				}
				replica.responseTimeMux.Unlock()
				
				log.Printf("✅ %s executed on %s in %v", queryName, replica.Name, responseTime)
			}(q.name, q.queryInfo, q.query)
		}
		
		time.Sleep(500 * time.Millisecond)
	}
	
	// Wait for all queries to complete
	time.Sleep(2 * time.Second)
}

// simulateHealthIssues simulates replica health issues
func simulateHealthIssues(manager *ReadReplicaManager) {
	log.Println("⚠️ Simulating health issues...")
	
	manager.replicasMux.RLock()
	var replicaIDs []string
	for id := range manager.replicas {
		replicaIDs = append(replicaIDs, id)
	}
	manager.replicasMux.RUnlock()
	
	if len(replicaIDs) > 0 {
		// Make one replica unhealthy
		unhealthyID := replicaIDs[rand.Intn(len(replicaIDs))]
		manager.replicasMux.Lock()
		if replica, exists := manager.replicas[unhealthyID]; exists {
			replica.IsHealthy = false
			replica.ReplicationLag = 2 * time.Minute // High lag
			log.Printf("❌ Made replica %s unhealthy (high replication lag)", replica.Name)
		}
		manager.replicasMux.Unlock()
		
		// Wait and then recover
		time.Sleep(10 * time.Second)
		
		manager.replicasMux.Lock()
		if replica, exists := manager.replicas[unhealthyID]; exists {
			replica.IsHealthy = true
			replica.ReplicationLag = 2 * time.Second // Normal lag
			log.Printf("✅ Recovered replica %s (replication lag normalized)", replica.Name)
		}
		manager.replicasMux.Unlock()
	}
}

func main() {
	fmt.Println("🔄 Read Replica Manager")
	fmt.Println("Episode 41: Advanced Read Replica Configuration")
	fmt.Println(strings.Repeat("=", 60))
	
	// Create replica manager
	manager := NewReadReplicaManager()
	defer manager.Close()
	
	// Set up HTTP endpoints for monitoring
	manager.SetupHTTPEndpoints()
	go func() {
		log.Printf("Starting HTTP server on %s", MetricsPort)
		if err := http.ListenAndServe(MetricsPort, nil); err != nil {
			log.Printf("HTTP server error: %v", err)
		}
	}()
	
	// Setup replicas for different systems
	fmt.Println("\n🏦 Setting up HDFC Banking read replicas...")
	setupHDFCBankReplicas(manager)
	
	fmt.Println("\n🛒 Setting up Flipkart read replicas...")
	setupFlipkartReplicas(manager)
	
	// Setup routing rules
	fmt.Println("\n🔀 Setting up intelligent routing rules...")
	setupRoutingRules(manager)
	
	// Start health checking
	fmt.Println("\n❤️ Starting health monitoring...")
	manager.StartHealthChecking()
	
	// Set geographic load balancer
	manager.loadBalancer = &GeographicBalancer{geoRouter: manager.geoRouter}
	
	fmt.Printf("\n📊 System Status:")
	fmt.Printf("  • Total Replicas: %d\n", len(manager.replicas))
	fmt.Printf("  • Load Balancer: Geographic + Least Connections\n")
	fmt.Printf("  • Health Check Interval: %v\n", HealthCheckInterval)
	fmt.Printf("  • Monitoring: http://localhost%s\n", MetricsPort)
	
	// Run query simulation
	fmt.Println("\n🔄 Starting query simulation...")
	go simulateQueries(manager)
	
	// Let queries run for a bit
	time.Sleep(5 * time.Second)
	
	// Simulate health issues
	go simulateHealthIssues(manager)
	
	// Run for demo duration
	fmt.Println("\n⏳ Running demo for 30 seconds...")
	time.Sleep(30 * time.Second)
	
	// Show final statistics
	fmt.Println("\n📊 Final Statistics:")
	stats := manager.GetReplicaStats()
	
	fmt.Printf("Total Replicas: %v\n", stats["total_replicas"])
	fmt.Printf("Healthy Replicas: %v\n", stats["healthy_replicas"])
	
	if replicaStats, ok := stats["replicas"].(map[string]interface{}); ok {
		fmt.Println("\nPer-Replica Statistics:")
		for id, stat := range replicaStats {
			if s, ok := stat.(map[string]interface{}); ok {
				fmt.Printf("  %s:\n", id)
				fmt.Printf("    Name: %v\n", s["name"])
				fmt.Printf("    Type: %v\n", s["type"])
				fmt.Printf("    Region: %v\n", s["region"])
				fmt.Printf("    Healthy: %v\n", s["is_healthy"])
				fmt.Printf("    Queries: %v\n", s["total_queries"]) 
				fmt.Printf("    Avg Response: %vms\n", s["avg_response_time_ms"])
				fmt.Printf("    Replication Lag: %vms\n", s["replication_lag_ms"])
				fmt.Println()
			}
		}
	}
	
	fmt.Println("✅ Demo completed successfully!")
	fmt.Println("\n💡 Key Features Demonstrated:")
	fmt.Println("  • Geographic-based replica selection")
	fmt.Println("  • Intelligent query routing rules")
	fmt.Println("  • Health monitoring with automatic failover")
	fmt.Println("  • Load balancing with multiple strategies")
	fmt.Println("  • Real-time metrics and monitoring")
	fmt.Println("  • Production-ready connection management")
}

/*
Key Learning Points from Read Replica Manager:

1. **Intelligent Routing**:
   - Query-type based routing (analytics, reporting, application)
   - Geographic proximity routing for better performance
   - Priority-based routing for critical queries
   - Table-specific routing rules

2. **Health Management**:
   - Continuous health monitoring every 10 seconds
   - Replication lag monitoring with thresholds
   - Connection count monitoring
   - Automatic failover for unhealthy replicas

3. **Load Balancing Strategies**:
   - Round-robin for simple load distribution
   - Weighted round-robin for capacity-based routing
   - Least connections for optimal resource utilization
   - Geographic routing for latency optimization

4. **Production Features**:
   - Prometheus metrics integration
   - HTTP endpoints for monitoring and management
   - Graceful shutdown with connection cleanup
   - Comprehensive error handling and logging

5. **Indian Context Implementation**:
   - HDFC Bank multi-region banking setup
   - Flipkart e-commerce geographic optimization
   - Regional data center considerations
   - Network latency optimization for Indian infrastructure

This implementation provides a production-ready read replica management
system that can handle the scale and complexity of Indian financial
and e-commerce applications.
*/
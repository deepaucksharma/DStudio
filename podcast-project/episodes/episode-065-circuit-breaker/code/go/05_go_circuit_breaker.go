// Go Circuit Breaker Implementation
// Production-ready circuit breaker pattern in Go
// गो में circuit breaker का implementation concurrency के साथ
package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"math/rand"
	"sync"
	"sync/atomic"
	"time"
)

// CircuitState represents the state of the circuit breaker
// Circuit breaker के states को represent करता है
type CircuitState int

const (
	// StateClosed - Normal operation, requests are allowed
	// सामान्य operation, सभी requests allow हैं
	StateClosed CircuitState = iota
	
	// StateOpen - Circuit is open, requests are rejected
	// Circuit open है, सभी requests reject हो रहे हैं
	StateOpen
	
	// StateHalfOpen - Testing state, limited requests allowed
	// Testing phase, limited requests allow हैं
	StateHalfOpen
)

// String returns string representation of circuit state
func (s CircuitState) String() string {
	switch s {
	case StateClosed:
		return "CLOSED"
	case StateOpen:
		return "OPEN"
	case StateHalfOpen:
		return "HALF_OPEN"
	default:
		return "UNKNOWN"
	}
}

// CircuitBreakerConfig holds configuration for circuit breaker
// Circuit breaker के लिए configuration structure
type CircuitBreakerConfig struct {
	// MaxRequests is the maximum number of requests allowed to pass through
	// when the CircuitBreaker is half-open
	MaxRequests uint32
	
	// Interval is the cyclic period of the closed state for the CircuitBreaker
	// to clear the internal Counts
	Interval time.Duration
	
	// Timeout is the period of the open state, after which the state of
	// the CircuitBreaker becomes half-open
	Timeout time.Duration
	
	// ReadyToTrip is called with a copy of Counts whenever a request fails
	// in the closed state. If ReadyToTrip returns true, the CircuitBreaker
	// will be placed into the open state
	ReadyToTrip func(counts Counts) bool
	
	// OnStateChange is called whenever the state of the CircuitBreaker changes
	OnStateChange func(name string, from CircuitState, to CircuitState)
	
	// IsSuccessful is called with the error returned from a request
	// If IsSuccessful returns true, the request is considered successful
	IsSuccessful func(err error) bool
}

// Counts holds the numbers of requests and their successes/failures
// Request counts और success/failure का data store करता है
type Counts struct {
	Requests             uint32 // Total requests
	TotalSuccesses       uint32 // Total successful requests
	TotalFailures        uint32 // Total failed requests
	ConsecutiveSuccesses uint32 // Consecutive successes in half-open state
	ConsecutiveFailures  uint32 // Consecutive failures
}

// OnRequest increments the request count
func (c *Counts) OnRequest() {
	atomic.AddUint32(&c.Requests, 1)
}

// OnSuccess increments success counters
func (c *Counts) OnSuccess() {
	atomic.AddUint32(&c.TotalSuccesses, 1)
	atomic.AddUint32(&c.ConsecutiveSuccesses, 1)
	atomic.StoreUint32(&c.ConsecutiveFailures, 0)
}

// OnFailure increments failure counters
func (c *Counts) OnFailure() {
	atomic.AddUint32(&c.TotalFailures, 1)
	atomic.AddUint32(&c.ConsecutiveFailures, 1)
	atomic.StoreUint32(&c.ConsecutiveSuccesses, 0)
}

// Clear resets all counts
func (c *Counts) Clear() {
	atomic.StoreUint32(&c.Requests, 0)
	atomic.StoreUint32(&c.TotalSuccesses, 0)
	atomic.StoreUint32(&c.TotalFailures, 0)
	atomic.StoreUint32(&c.ConsecutiveSuccesses, 0)
	atomic.StoreUint32(&c.ConsecutiveFailures, 0)
}

// Copy returns a copy of the counts
func (c *Counts) Copy() Counts {
	return Counts{
		Requests:             atomic.LoadUint32(&c.Requests),
		TotalSuccesses:       atomic.LoadUint32(&c.TotalSuccesses),
		TotalFailures:        atomic.LoadUint32(&c.TotalFailures),
		ConsecutiveSuccesses: atomic.LoadUint32(&c.ConsecutiveSuccesses),
		ConsecutiveFailures:  atomic.LoadUint32(&c.ConsecutiveFailures),
	}
}

// CircuitBreaker is a state machine to prevent cascading failures
// Cascading failures को prevent करने के लिए state machine
type CircuitBreaker struct {
	name         string
	maxRequests  uint32
	interval     time.Duration
	timeout      time.Duration
	readyToTrip  func(counts Counts) bool
	isSuccessful func(err error) bool
	onStateChange func(name string, from CircuitState, to CircuitState)

	mutex      sync.RWMutex
	state      CircuitState
	generation uint64
	counts     Counts
	expiry     time.Time
}

// NewCircuitBreaker creates a new CircuitBreaker
func NewCircuitBreaker(name string, config CircuitBreakerConfig) *CircuitBreaker {
	cb := &CircuitBreaker{
		name:          name,
		maxRequests:   config.MaxRequests,
		interval:      config.Interval,
		timeout:       config.Timeout,
		readyToTrip:   config.ReadyToTrip,
		isSuccessful:  config.IsSuccessful,
		onStateChange: config.OnStateChange,
		state:         StateClosed,
		expiry:        time.Now().Add(config.Interval),
	}

	// Default ReadyToTrip function
	if cb.readyToTrip == nil {
		cb.readyToTrip = func(counts Counts) bool {
			failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
			return counts.Requests >= 3 && failureRatio >= 0.6
		}
	}

	// Default IsSuccessful function
	if cb.isSuccessful == nil {
		cb.isSuccessful = func(err error) bool {
			return err == nil
		}
	}

	log.Printf("🔧 Circuit Breaker '%s' initialized", name)
	log.Printf("   - Max requests in half-open: %d", cb.maxRequests)
	log.Printf("   - Interval: %v", cb.interval)
	log.Printf("   - Timeout: %v", cb.timeout)

	return cb
}

// Execute executes the given function if the CircuitBreaker accepts it
// दी गई function को execute करता है अगर circuit breaker allow करता है
func (cb *CircuitBreaker) Execute(fn func() (interface{}, error)) (interface{}, error) {
	generation, err := cb.beforeRequest()
	if err != nil {
		return nil, err
	}

	defer func() {
		e := recover()
		if e != nil {
			cb.afterRequest(generation, false)
			panic(e)
		}
	}()

	result, err := fn()
	cb.afterRequest(generation, cb.isSuccessful(err))
	return result, err
}

// ExecuteWithContext executes function with context support
// Context के साथ function execute करता है
func (cb *CircuitBreaker) ExecuteWithContext(ctx context.Context, fn func() (interface{}, error)) (interface{}, error) {
	// Check if context is already cancelled
	select {
	case <-ctx.Done():
		return nil, ctx.Err()
	default:
	}

	generation, err := cb.beforeRequest()
	if err != nil {
		return nil, err
	}

	// Channel for function result
	type result struct {
		data interface{}
		err  error
	}
	resultCh := make(chan result, 1)

	go func() {
		defer func() {
			if e := recover(); e != nil {
				cb.afterRequest(generation, false)
				resultCh <- result{nil, fmt.Errorf("panic: %v", e)}
			}
		}()

		data, err := fn()
		cb.afterRequest(generation, cb.isSuccessful(err))
		resultCh <- result{data, err}
	}()

	select {
	case <-ctx.Done():
		cb.afterRequest(generation, false)
		return nil, ctx.Err()
	case res := <-resultCh:
		return res.data, res.err
	}
}

// beforeRequest checks if the request should be allowed
func (cb *CircuitBreaker) beforeRequest() (uint64, error) {
	cb.mutex.Lock()
	defer cb.mutex.Unlock()

	now := time.Now()
	state, generation := cb.currentState(now)

	if state == StateOpen {
		return generation, errors.New("circuit breaker is open")
	} else if state == StateHalfOpen && cb.counts.Requests >= cb.maxRequests {
		return generation, errors.New("too many requests in half-open state")
	}

	cb.counts.OnRequest()
	return generation, nil
}

// afterRequest records the result of the request
func (cb *CircuitBreaker) afterRequest(before uint64, success bool) {
	cb.mutex.Lock()
	defer cb.mutex.Unlock()

	now := time.Now()
	state, generation := cb.currentState(now)
	if generation != before {
		return
	}

	if success {
		cb.onSuccess(state, now)
	} else {
		cb.onFailure(state, now)
	}
}

// onSuccess handles successful requests
func (cb *CircuitBreaker) onSuccess(state CircuitState, now time.Time) {
	switch state {
	case StateClosed:
		cb.counts.OnSuccess()
	case StateHalfOpen:
		cb.counts.OnSuccess()
		if cb.counts.ConsecutiveSuccesses >= cb.maxRequests {
			cb.setState(StateClosed, now)
		}
	}
}

// onFailure handles failed requests
func (cb *CircuitBreaker) onFailure(state CircuitState, now time.Time) {
	switch state {
	case StateClosed:
		cb.counts.OnFailure()
		if cb.readyToTrip(cb.counts.Copy()) {
			cb.setState(StateOpen, now)
		}
	case StateHalfOpen:
		cb.setState(StateOpen, now)
	}
}

// currentState returns the current state and generation
func (cb *CircuitBreaker) currentState(now time.Time) (CircuitState, uint64) {
	switch cb.state {
	case StateClosed:
		if !cb.expiry.IsZero() && cb.expiry.Before(now) {
			cb.toNewGeneration(now)
		}
	case StateOpen:
		if cb.expiry.Before(now) {
			cb.setState(StateHalfOpen, now)
		}
	}
	return cb.state, cb.generation
}

// setState changes the state of the circuit breaker
func (cb *CircuitBreaker) setState(state CircuitState, now time.Time) {
	if cb.state == state {
		return
	}

	prev := cb.state
	cb.state = state

	cb.toNewGeneration(now)

	if cb.onStateChange != nil {
		cb.onStateChange(cb.name, prev, state)
	}

	log.Printf("🔄 Circuit Breaker '%s': %s → %s", cb.name, prev, state)
}

// toNewGeneration starts a new generation
func (cb *CircuitBreaker) toNewGeneration(now time.Time) {
	cb.generation++
	cb.counts.Clear()

	var zero time.Time
	switch cb.state {
	case StateClosed:
		if cb.interval == 0 {
			cb.expiry = zero
		} else {
			cb.expiry = now.Add(cb.interval)
		}
	case StateOpen:
		cb.expiry = now.Add(cb.timeout)
	default: // StateHalfOpen
		cb.expiry = zero
	}
}

// State returns the current state of the CircuitBreaker
func (cb *CircuitBreaker) State() CircuitState {
	cb.mutex.RLock()
	defer cb.mutex.RUnlock()

	state, _ := cb.currentState(time.Now())
	return state
}

// Counts returns a copy of the current counts
func (cb *CircuitBreaker) Counts() Counts {
	cb.mutex.RLock()
	defer cb.mutex.RUnlock()

	return cb.counts.Copy()
}

// Metrics returns detailed metrics about the circuit breaker
func (cb *CircuitBreaker) Metrics() map[string]interface{} {
	counts := cb.Counts()
	state := cb.State()

	successRate := float64(0)
	if counts.Requests > 0 {
		successRate = float64(counts.TotalSuccesses) / float64(counts.Requests) * 100
	}

	return map[string]interface{}{
		"name":                  cb.name,
		"state":                 state.String(),
		"requests":              counts.Requests,
		"successes":             counts.TotalSuccesses,
		"failures":              counts.TotalFailures,
		"consecutive_successes": counts.ConsecutiveSuccesses,
		"consecutive_failures":  counts.ConsecutiveFailures,
		"success_rate":          fmt.Sprintf("%.2f%%", successRate),
	}
}

// Example service implementations
// विभिन्न services के examples

// PaymentService simulates a payment gateway
// Payment gateway का simulation
type PaymentService struct {
	failureRate float64
	slowRate    float64
}

// ProcessPayment simulates payment processing
func (p *PaymentService) ProcessPayment(orderID string, amount float64) (string, error) {
	// Simulate network delay
	delay := time.Duration(rand.Intn(200)+50) * time.Millisecond
	if rand.Float64() < p.slowRate {
		delay = time.Duration(rand.Intn(1000)+1000) * time.Millisecond // 1-2 seconds
	}
	time.Sleep(delay)

	// Simulate failure
	if rand.Float64() < p.failureRate {
		return "", errors.New("payment gateway unavailable")
	}

	return fmt.Sprintf("Payment successful: OrderID=%s, Amount=%.2f", orderID, amount), nil
}

// DatabaseService simulates a database service
// Database service का simulation  
type DatabaseService struct {
	failureRate float64
}

// FetchUserData simulates database query
func (d *DatabaseService) FetchUserData(userID string) (map[string]interface{}, error) {
	// Simulate query time
	time.Sleep(time.Duration(rand.Intn(100)+50) * time.Millisecond)

	if rand.Float64() < d.failureRate {
		return nil, errors.New("database connection timeout")
	}

	return map[string]interface{}{
		"user_id": userID,
		"name":    "User " + userID,
		"email":   userID + "@example.com",
		"active":  true,
	}, nil
}

// Example usage and testing
func main() {
	fmt.Println("🧪 Testing Go Circuit Breaker")
	fmt.Println(strings.Repeat("=", 60))

	// Test Payment Service Circuit Breaker
	testPaymentCircuitBreaker()

	fmt.Println()

	// Test Database Service Circuit Breaker
	testDatabaseCircuitBreaker()

	fmt.Println()

	// Test concurrent requests
	testConcurrentRequests()
}

func testPaymentCircuitBreaker() {
	fmt.Println("\n📊 Testing Payment Service Circuit Breaker")
	fmt.Println(strings.Repeat("-", 50))

	// Payment service with high failure rate
	paymentService := &PaymentService{
		failureRate: 0.7, // 70% failure rate
		slowRate:    0.2, // 20% slow responses
	}

	// Circuit breaker configuration
	config := CircuitBreakerConfig{
		MaxRequests: 3,
		Interval:    5 * time.Second,
		Timeout:     10 * time.Second,
		ReadyToTrip: func(counts Counts) bool {
			failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
			return counts.Requests >= 5 && failureRatio >= 0.6
		},
		OnStateChange: func(name string, from CircuitState, to CircuitState) {
			fmt.Printf("🔄 %s: %s → %s\n", name, from, to)
		},
	}

	cb := NewCircuitBreaker("payment-service", config)

	// Test requests
	for i := 1; i <= 20; i++ {
		orderID := fmt.Sprintf("ORDER_%d", i)
		amount := float64(100 + i*10)

		result, err := cb.Execute(func() (interface{}, error) {
			return paymentService.ProcessPayment(orderID, amount)
		})

		if err != nil {
			fmt.Printf("❌ Request %d: %s\n", i, err.Error())
		} else {
			fmt.Printf("✅ Request %d: %s\n", i, result)
		}

		// Show metrics every 5 requests
		if i%5 == 0 {
			metrics := cb.Metrics()
			fmt.Printf("📈 Metrics: State=%s, Requests=%v, Success Rate=%v\n",
				metrics["state"], metrics["requests"], metrics["success_rate"])
		}

		time.Sleep(500 * time.Millisecond)
	}

	// Final metrics
	fmt.Printf("\n📈 Final Payment Service Metrics:\n")
	printMetrics(cb.Metrics())
}

func testDatabaseCircuitBreaker() {
	fmt.Println("\n📊 Testing Database Service Circuit Breaker")
	fmt.Println(strings.Repeat("-", 50))

	// Database service with moderate failure rate
	dbService := &DatabaseService{
		failureRate: 0.4, // 40% failure rate
	}

	config := CircuitBreakerConfig{
		MaxRequests: 2,
		Interval:    3 * time.Second,
		Timeout:     5 * time.Second,
		OnStateChange: func(name string, from CircuitState, to CircuitState) {
			fmt.Printf("🔄 %s: %s → %s\n", name, from, to)
		},
	}

	cb := NewCircuitBreaker("database-service", config)

	// Test with context
	for i := 1; i <= 15; i++ {
		userID := fmt.Sprintf("USER_%d", i)

		// Create context with timeout
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)

		result, err := cb.ExecuteWithContext(ctx, func() (interface{}, error) {
			return dbService.FetchUserData(userID)
		})

		cancel()

		if err != nil {
			fmt.Printf("❌ DB Query %d: %s\n", i, err.Error())
		} else {
			userData := result.(map[string]interface{})
			fmt.Printf("✅ DB Query %d: User=%s\n", i, userData["name"])
		}

		time.Sleep(300 * time.Millisecond)
	}

	fmt.Printf("\n📈 Final Database Service Metrics:\n")
	printMetrics(cb.Metrics())
}

func testConcurrentRequests() {
	fmt.Println("\n📊 Testing Concurrent Requests")
	fmt.Println(strings.Repeat("-", 50))

	service := &PaymentService{
		failureRate: 0.5,
		slowRate:    0.1,
	}

	config := CircuitBreakerConfig{
		MaxRequests: 3,
		Interval:    2 * time.Second,
		Timeout:     3 * time.Second,
	}

	cb := NewCircuitBreaker("concurrent-test", config)

	var wg sync.WaitGroup
	numGoroutines := 10
	requestsPerGoroutine := 5

	for g := 1; g <= numGoroutines; g++ {
		wg.Add(1)
		go func(goroutineID int) {
			defer wg.Done()
			
			for r := 1; r <= requestsPerGoroutine; r++ {
				orderID := fmt.Sprintf("G%d_ORDER_%d", goroutineID, r)
				
				result, err := cb.Execute(func() (interface{}, error) {
					return service.ProcessPayment(orderID, 100.0)
				})

				if err != nil {
					fmt.Printf("❌ G%d-R%d: %s\n", goroutineID, r, err.Error())
				} else {
					fmt.Printf("✅ G%d-R%d: Success\n", goroutineID, r)
				}

				time.Sleep(100 * time.Millisecond)
			}
		}(g)
	}

	wg.Wait()
	
	fmt.Printf("\n📈 Concurrent Test Final Metrics:\n")
	printMetrics(cb.Metrics())
}

func printMetrics(metrics map[string]interface{}) {
	for key, value := range metrics {
		fmt.Printf("   %s: %v\n", key, value)
	}
}

// Additional utility functions
import "strings"
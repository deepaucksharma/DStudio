package main

/*
Redis Distributed Lock Implementation in Go
==========================================

Production-ready Redis-based distributed locking with proper error handling.
Used by companies like Uber, Twitter for critical resource coordination.

Mumbai Context: यह Mumbai local train के multiple platforms पर coordination
करने जैसा है - हर platform को पता होना चाहिए कि कौन सी train कहाँ है!

Real-world usage:
- Critical section protection
- Resource allocation
- Job scheduling coordination
- Cache invalidation locks
*/

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"log"
	"math"
	"strconv"
	"sync"
	"sync/atomic"
	"time"

	"github.com/go-redis/redis/v8"
)

// RedisLockManager manages distributed locks using Redis
type RedisLockManager struct {
	client       *redis.Client
	lockPrefix   string
	defaultTTL   time.Duration
	retryCount   int
	retryDelay   time.Duration
	
	// Statistics
	locksAcquired int64
	locksFailed   int64
	locksReleased int64
}

// LockInfo contains information about an acquired lock
type LockInfo struct {
	Resource    string
	Token       string
	ExpiresAt   time.Time
	AcquiredAt  time.Time
	TTL         time.Duration
}

// NewRedisLockManager creates a new Redis lock manager
func NewRedisLockManager(redisURL string) *RedisLockManager {
	opt, err := redis.ParseURL(redisURL)
	if err != nil {
		log.Fatalf("Failed to parse Redis URL: %v", err)
	}
	
	client := redis.NewClient(opt)
	
	// Test connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	if err := client.Ping(ctx).Err(); err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}
	
	log.Printf("✅ Connected to Redis: %s", opt.Addr)
	
	return &RedisLockManager{
		client:     client,
		lockPrefix: "lock:",
		defaultTTL: 30 * time.Second,
		retryCount: 3,
		retryDelay: 100 * time.Millisecond,
	}
}

// generateToken generates a unique token for the lock
func (r *RedisLockManager) generateToken() string {
	bytes := make([]byte, 16)
	rand.Read(bytes)
	return hex.EncodeToString(bytes)
}

// AcquireLock attempts to acquire a distributed lock
func (r *RedisLockManager) AcquireLock(ctx context.Context, resource string, ttl time.Duration) (*LockInfo, error) {
	if ttl == 0 {
		ttl = r.defaultTTL
	}
	
	lockKey := r.lockPrefix + resource
	token := r.generateToken()
	
	for attempt := 0; attempt < r.retryCount; attempt++ {
		// Try to acquire lock using SET with NX and EX
		acquired, err := r.client.SetNX(ctx, lockKey, token, ttl).Result()
		if err != nil {
			log.Printf("❌ Redis error during lock acquisition: %v", err)
			continue
		}
		
		if acquired {
			lockInfo := &LockInfo{
				Resource:   resource,
				Token:      token,
				ExpiresAt:  time.Now().Add(ttl),
				AcquiredAt: time.Now(),
				TTL:        ttl,
			}
			
			atomic.AddInt64(&r.locksAcquired, 1)
			log.Printf("🔒 Redis lock acquired: %s (expires: %s)", resource, lockInfo.ExpiresAt.Format(time.RFC3339))
			
			return lockInfo, nil
		}
		
		// Lock is held by someone else
		if attempt < r.retryCount-1 {
			select {
			case <-ctx.Done():
				atomic.AddInt64(&r.locksFailed, 1)
				return nil, ctx.Err()
			case <-time.After(r.retryDelay):
				// Continue to next attempt
			}
		}
	}
	
	atomic.AddInt64(&r.locksFailed, 1)
	return nil, fmt.Errorf("failed to acquire lock for resource: %s", resource)
}

// ReleaseLock releases a distributed lock
func (r *RedisLockManager) ReleaseLock(ctx context.Context, lockInfo *LockInfo) error {
	lockKey := r.lockPrefix + lockInfo.Resource
	
	// Lua script to atomically check and delete
	script := `
		if redis.call("GET", KEYS[1]) == ARGV[1] then
			return redis.call("DEL", KEYS[1])
		else
			return 0
		end
	`
	
	result, err := r.client.Eval(ctx, script, []string{lockKey}, lockInfo.Token).Result()
	if err != nil {
		log.Printf("❌ Failed to release lock: %v", err)
		return err
	}
	
	if result.(int64) == 1 {
		atomic.AddInt64(&r.locksReleased, 1)
		log.Printf("🔓 Redis lock released: %s", lockInfo.Resource)
		return nil
	}
	
	log.Printf("⚠️ Lock was not owned by us or already expired: %s", lockInfo.Resource)
	return nil
}

// ExtendLock extends the TTL of an existing lock
func (r *RedisLockManager) ExtendLock(ctx context.Context, lockInfo *LockInfo, newTTL time.Duration) error {
	lockKey := r.lockPrefix + lockInfo.Resource
	
	// Lua script to atomically check owner and extend TTL
	script := `
		if redis.call("GET", KEYS[1]) == ARGV[1] then
			return redis.call("EXPIRE", KEYS[1], ARGV[2])
		else
			return 0
		end
	`
	
	result, err := r.client.Eval(ctx, script, []string{lockKey}, lockInfo.Token, int(newTTL.Seconds())).Result()
	if err != nil {
		return err
	}
	
	if result.(int64) == 1 {
		lockInfo.ExpiresAt = time.Now().Add(newTTL)
		lockInfo.TTL = newTTL
		log.Printf("⏰ Lock extended: %s (new expiry: %s)", lockInfo.Resource, lockInfo.ExpiresAt.Format(time.RFC3339))
		return nil
	}
	
	return fmt.Errorf("lock not owned by us or already expired")
}

// IsLocked checks if a resource is currently locked
func (r *RedisLockManager) IsLocked(ctx context.Context, resource string) (bool, error) {
	lockKey := r.lockPrefix + resource
	exists, err := r.client.Exists(ctx, lockKey).Result()
	return exists == 1, err
}

// GetStatistics returns lock manager statistics
func (r *RedisLockManager) GetStatistics() (int64, int64, int64, float64) {
	acquired := atomic.LoadInt64(&r.locksAcquired)
	failed := atomic.LoadInt64(&r.locksFailed)
	released := atomic.LoadInt64(&r.locksReleased)
	
	total := acquired + failed
	successRate := 0.0
	if total > 0 {
		successRate = float64(acquired) / float64(total) * 100.0
	}
	
	return acquired, failed, released, successRate
}

// Close closes the Redis connection
func (r *RedisLockManager) Close() error {
	return r.client.Close()
}

/*
Zomato Order Processing System using Redis Locks
===============================================

Mumbai Story: Zomato में peak lunch time (12-2 PM) में हजारों orders एक साथ
आते हैं. Restaurant capacity limited होती है, तो Redis locks help करते हैं
order processing को coordinate करने में!
*/

// OrderStatus represents the status of an order
type OrderStatus string

const (
	OrderStatusPending    OrderStatus = "PENDING"
	OrderStatusAccepted   OrderStatus = "ACCEPTED"
	OrderStatusPreparing  OrderStatus = "PREPARING"
	OrderStatusReady      OrderStatus = "READY"
	OrderStatusDelivered  OrderStatus = "DELIVERED"
	OrderStatusRejected   OrderStatus = "REJECTED"
)

// Order represents a food order
type Order struct {
	OrderID      string      `json:"order_id"`
	RestaurantID string      `json:"restaurant_id"`
	CustomerID   string      `json:"customer_id"`
	Items        []OrderItem `json:"items"`
	TotalAmount  float64     `json:"total_amount"`
	Status       OrderStatus `json:"status"`
	CreatedAt    time.Time   `json:"created_at"`
	UpdatedAt    time.Time   `json:"updated_at"`
}

// OrderItem represents an item in an order
type OrderItem struct {
	ItemID   string  `json:"item_id"`
	Name     string  `json:"name"`
	Quantity int     `json:"quantity"`
	Price    float64 `json:"price"`
}

// Restaurant represents a restaurant with capacity limits
type Restaurant struct {
	ID                string `json:"id"`
	Name              string `json:"name"`
	MaxOrdersPerHour  int    `json:"max_orders_per_hour"`
	CurrentOrderCount int    `json:"current_order_count"`
	Location          string `json:"location"`
	Rating            float64 `json:"rating"`
}

// ZomatoOrderProcessor processes food orders with distributed locking
type ZomatoOrderProcessor struct {
	lockManager  *RedisLockManager
	restaurants  map[string]*Restaurant
	orders       map[string]*Order
	ordersMutex  sync.RWMutex
	
	// Statistics
	totalOrders     int64
	acceptedOrders  int64
	rejectedOrders  int64
	conflictsPrevented int64
}

// NewZomatoOrderProcessor creates a new order processor
func NewZomatoOrderProcessor(lockManager *RedisLockManager) *ZomatoOrderProcessor {
	processor := &ZomatoOrderProcessor{
		lockManager: lockManager,
		restaurants: make(map[string]*Restaurant),
		orders:      make(map[string]*Order),
	}
	
	processor.initializeRestaurants()
	log.Printf("🍽️ Zomato Order Processor initialized")
	
	return processor
}

// initializeRestaurants initializes popular Mumbai restaurants
func (z *ZomatoOrderProcessor) initializeRestaurants() {
	restaurants := []*Restaurant{
		{ID: "rest_001", Name: "Mumbai Darbar (Bandra)", MaxOrdersPerHour: 50, Location: "Bandra West", Rating: 4.2},
		{ID: "rest_002", Name: "Theobroma (Powai)", MaxOrdersPerHour: 40, Location: "Powai", Rating: 4.5},
		{ID: "rest_003", Name: "Cafe Mocha (Andheri)", MaxOrdersPerHour: 35, Location: "Andheri East", Rating: 4.1},
		{ID: "rest_004", Name: "Burger King (Malad)", MaxOrdersPerHour: 60, Location: "Malad West", Rating: 3.9},
		{ID: "rest_005", Name: "Dominos (Kurla)", MaxOrdersPerHour: 45, Location: "Kurla West", Rating: 3.8},
	}
	
	for _, restaurant := range restaurants {
		z.restaurants[restaurant.ID] = restaurant
	}
}

// ProcessOrder processes a new food order with distributed locking
func (z *ZomatoOrderProcessor) ProcessOrder(ctx context.Context, order *Order) error {
	atomic.AddInt64(&z.totalOrders, 1)
	
	// Lock restaurant capacity to prevent overselling
	restaurantLockResource := fmt.Sprintf("restaurant_capacity_%s", order.RestaurantID)
	
	lockInfo, err := z.lockManager.AcquireLock(ctx, restaurantLockResource, 30*time.Second)
	if err != nil {
		log.Printf("❌ Failed to acquire restaurant lock for order %s: %v", order.OrderID, err)
		return err
	}
	defer z.lockManager.ReleaseLock(ctx, lockInfo)
	
	// Check restaurant exists and capacity
	restaurant, exists := z.restaurants[order.RestaurantID]
	if !exists {
		order.Status = OrderStatusRejected
		atomic.AddInt64(&z.rejectedOrders, 1)
		return fmt.Errorf("restaurant not found: %s", order.RestaurantID)
	}
	
	// Check capacity (simplified - in reality this would be time-based)
	if restaurant.CurrentOrderCount >= restaurant.MaxOrdersPerHour {
		order.Status = OrderStatusRejected
		atomic.AddInt64(&z.rejectedOrders, 1)
		atomic.AddInt64(&z.conflictsPrevented, 1)
		
		log.Printf("❌ Order %s rejected - Restaurant %s at capacity (%d/%d)", 
			order.OrderID, restaurant.Name, restaurant.CurrentOrderCount, restaurant.MaxOrdersPerHour)
		
		return fmt.Errorf("restaurant at full capacity")
	}
	
	// Process order
	restaurant.CurrentOrderCount++
	order.Status = OrderStatusAccepted
	order.UpdatedAt = time.Now()
	
	// Store order
	z.ordersMutex.Lock()
	z.orders[order.OrderID] = order
	z.ordersMutex.Unlock()
	
	atomic.AddInt64(&z.acceptedOrders, 1)
	
	log.Printf("🍕 Order accepted: %s - %s (₹%.2f) for %s", 
		order.OrderID, restaurant.Name, order.TotalAmount, order.CustomerID)
	
	// Simulate order preparation time
	go z.simulateOrderPreparation(order)
	
	return nil
}

// simulateOrderPreparation simulates the order preparation process
func (z *ZomatoOrderProcessor) simulateOrderPreparation(order *Order) {
	// Simulate preparation time (5-15 minutes scaled down for demo)
	preparationTime := time.Duration(5+int(math.Mod(float64(time.Now().UnixNano()), 10))) * time.Second
	
	time.Sleep(preparationTime)
	
	// Update order status
	z.ordersMutex.Lock()
	if storedOrder, exists := z.orders[order.OrderID]; exists {
		storedOrder.Status = OrderStatusReady
		storedOrder.UpdatedAt = time.Now()
	}
	z.ordersMutex.Unlock()
	
	// Free up restaurant capacity
	ctx := context.Background()
	restaurantLockResource := fmt.Sprintf("restaurant_capacity_%s", order.RestaurantID)
	
	lockInfo, err := z.lockManager.AcquireLock(ctx, restaurantLockResource, 10*time.Second)
	if err == nil {
		if restaurant, exists := z.restaurants[order.RestaurantID]; exists {
			restaurant.CurrentOrderCount--
		}
		z.lockManager.ReleaseLock(ctx, lockInfo)
	}
	
	log.Printf("🚚 Order ready for delivery: %s", order.OrderID)
}

// GetOrderStatus returns the status of an order
func (z *ZomatoOrderProcessor) GetOrderStatus(orderID string) (*Order, error) {
	z.ordersMutex.RLock()
	defer z.ordersMutex.RUnlock()
	
	order, exists := z.orders[orderID]
	if !exists {
		return nil, fmt.Errorf("order not found: %s", orderID)
	}
	
	return order, nil
}

// GetRestaurantStatus returns current status of a restaurant
func (z *ZomatoOrderProcessor) GetRestaurantStatus(restaurantID string) (*Restaurant, error) {
	restaurant, exists := z.restaurants[restaurantID]
	if !exists {
		return nil, fmt.Errorf("restaurant not found: %s", restaurantID)
	}
	
	return restaurant, nil
}

// GetStatistics returns processing statistics
func (z *ZomatoOrderProcessor) GetStatistics() (total, accepted, rejected, conflicts int64, acceptanceRate float64) {
	total = atomic.LoadInt64(&z.totalOrders)
	accepted = atomic.LoadInt64(&z.acceptedOrders)
	rejected = atomic.LoadInt64(&z.rejectedOrders)
	conflicts = atomic.LoadInt64(&z.conflictsPrevented)
	
	if total > 0 {
		acceptanceRate = float64(accepted) / float64(total) * 100.0
	}
	
	return
}

// Demo function to simulate Zomato order processing
func simulateZomatoOrderProcessing() {
	log.Println("🍽️ Starting Zomato order processing simulation...")
	
	// Initialize Redis lock manager
	lockManager := NewRedisLockManager("redis://localhost:6379/0")
	defer lockManager.Close()
	
	// Initialize order processor
	processor := NewZomatoOrderProcessor(lockManager)
	
	// Generate sample orders
	orders := generateSampleOrders()
	
	// Process orders concurrently
	ctx := context.Background()
	var wg sync.WaitGroup
	
	for i, order := range orders {
		wg.Add(1)
		
		go func(orderNum int, o *Order) {
			defer wg.Done()
			
			// Small delay to simulate realistic order timing
			time.Sleep(time.Duration(orderNum*50) * time.Millisecond)
			
			err := processor.ProcessOrder(ctx, o)
			if err != nil {
				log.Printf("⚠️ Order processing failed: %s - %v", o.OrderID, err)
			}
		}(i, order)
	}
	
	// Wait for all orders to be processed
	wg.Wait()
	
	// Wait a bit more for order preparation to complete
	time.Sleep(5 * time.Second)
	
	// Show statistics
	showZomatoStatistics(processor, lockManager)
}

// generateSampleOrders creates sample food orders
func generateSampleOrders() []*Order {
	restaurants := []string{"rest_001", "rest_002", "rest_003", "rest_004", "rest_005"}
	
	var orders []*Order
	
	for i := 1; i <= 30; i++ {
		restaurantID := restaurants[(i-1)%len(restaurants)]
		orderID := fmt.Sprintf("ORD_%d_%d", time.Now().Unix(), i)
		customerID := fmt.Sprintf("customer_%04d", i)
		
		// Create sample items
		items := []OrderItem{
			{ItemID: "item_1", Name: "Butter Chicken", Quantity: 1, Price: 299.0},
			{ItemID: "item_2", Name: "Garlic Naan", Quantity: 2, Price: 49.0},
		}
		
		if i%3 == 0 {
			items = append(items, OrderItem{ItemID: "item_3", Name: "Biryani", Quantity: 1, Price: 349.0})
		}
		
		// Calculate total
		totalAmount := 0.0
		for _, item := range items {
			totalAmount += item.Price * float64(item.Quantity)
		}
		
		order := &Order{
			OrderID:      orderID,
			RestaurantID: restaurantID,
			CustomerID:   customerID,
			Items:        items,
			TotalAmount:  totalAmount,
			Status:       OrderStatusPending,
			CreatedAt:    time.Now(),
			UpdatedAt:    time.Now(),
		}
		
		orders = append(orders, order)
	}
	
	return orders
}

// showZomatoStatistics displays processing and lock statistics
func showZomatoStatistics(processor *ZomatoOrderProcessor, lockManager *RedisLockManager) {
	// Order processing statistics
	total, accepted, rejected, conflicts, acceptanceRate := processor.GetStatistics()
	
	log.Println("\n📊 Zomato Order Processing Results:")
	log.Printf("Total orders: %d", total)
	log.Printf("Accepted orders: %d", accepted)
	log.Printf("Rejected orders: %d", rejected)
	log.Printf("Capacity conflicts prevented: %d", conflicts)
	log.Printf("Acceptance rate: %.2f%%", acceptanceRate)
	
	// Lock manager statistics
	acquired, failed, released, lockSuccessRate := lockManager.GetStatistics()
	log.Println("\n🔒 Redis Lock Statistics:")
	log.Printf("Locks acquired: %d", acquired)
	log.Printf("Lock failures: %d", failed)
	log.Printf("Locks released: %d", released)
	log.Printf("Lock success rate: %.2f%%", lockSuccessRate)
	
	// Restaurant status
	log.Println("\n🏪 Restaurant Status:")
	restaurants := []string{"rest_001", "rest_002", "rest_003", "rest_004", "rest_005"}
	for _, restID := range restaurants {
		if status, err := processor.GetRestaurantStatus(restID); err == nil {
			log.Printf("%s: %d/%d orders", status.Name, status.CurrentOrderCount, status.MaxOrdersPerHour)
		}
	}
}

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	
	// Test Redis connection
	lockManager := NewRedisLockManager("redis://localhost:6379/0")
	ctx := context.Background()
	
	// Simple lock test
	log.Println("🧪 Testing basic lock functionality...")
	
	lockInfo, err := lockManager.AcquireLock(ctx, "test_resource", 5*time.Second)
	if err != nil {
		log.Fatalf("Failed to acquire test lock: %v", err)
	}
	
	log.Printf("✅ Test lock acquired: %s", lockInfo.Resource)
	
	err = lockManager.ReleaseLock(ctx, lockInfo)
	if err != nil {
		log.Fatalf("Failed to release test lock: %v", err)
	}
	
	log.Printf("✅ Test lock released")
	lockManager.Close()
	
	// Run Zomato simulation
	simulateZomatoOrderProcessing()
	
	log.Println("🏁 Simulation completed successfully!")
}
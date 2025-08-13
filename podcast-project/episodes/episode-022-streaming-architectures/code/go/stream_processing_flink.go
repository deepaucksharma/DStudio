/*
Episode 22: Streaming Architectures - Stream Processing with Apache Flink
Author: Code Developer Agent
Description: Apache Flink implementation for real-time Indian e-commerce analytics

Flink है stateful stream processing का powerful framework
यह complex event processing और real-time analytics के लिए perfect है
*/

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"sort"
	"sync"
	"time"
)

// E-commerce Event Types
type EventType string

const (
	UserRegistration  EventType = "user_registration"
	ProductView       EventType = "product_view"
	AddToCart         EventType = "add_to_cart"
	RemoveFromCart    EventType = "remove_from_cart"
	Purchase          EventType = "purchase"
	PaymentSuccess    EventType = "payment_success"
	PaymentFailure    EventType = "payment_failure"
	ProductSearch     EventType = "product_search"
	UserLogin         EventType = "user_login"
	UserLogout        EventType = "user_logout"
)

// E-commerce Event Model
type EcommerceEvent struct {
	EventID     string                 `json:"event_id"`
	EventType   EventType              `json:"event_type"`
	UserID      string                 `json:"user_id"`
	SessionID   string                 `json:"session_id"`
	ProductID   string                 `json:"product_id,omitempty"`
	CategoryID  string                 `json:"category_id,omitempty"`
	Price       float64                `json:"price,omitempty"`
	Quantity    int                    `json:"quantity,omitempty"`
	Timestamp   time.Time              `json:"timestamp"`
	Platform    string                 `json:"platform"` // web, android, ios
	Location    Location               `json:"location"`
	Metadata    map[string]interface{} `json:"metadata"`
}

type Location struct {
	Country string `json:"country"`
	State   string `json:"state"`
	City    string `json:"city"`
}

// Analytics Results
type ProductAnalytics struct {
	ProductID       string    `json:"product_id"`
	CategoryID      string    `json:"category_id"`
	ViewCount       int64     `json:"view_count"`
	CartAdditions   int64     `json:"cart_additions"`
	Purchases       int64     `json:"purchases"`
	TotalRevenue    float64   `json:"total_revenue"`
	ConversionRate  float64   `json:"conversion_rate"`
	WindowStart     time.Time `json:"window_start"`
	WindowEnd       time.Time `json:"window_end"`
}

type UserSessionAnalytics struct {
	UserID           string        `json:"user_id"`
	SessionID        string        `json:"session_id"`
	SessionDuration  time.Duration `json:"session_duration"`
	EventsCount      int           `json:"events_count"`
	ProductsViewed   int           `json:"products_viewed"`
	CartValue        float64       `json:"cart_value"`
	PurchaseValue    float64       `json:"purchase_value"`
	Platform         string        `json:"platform"`
	ConversionStatus string        `json:"conversion_status"` // converted, abandoned, active
}

type RealTimeMetrics struct {
	Timestamp           time.Time `json:"timestamp"`
	ActiveUsers         int64     `json:"active_users"`
	EventsPerSecond     float64   `json:"events_per_second"`
	RevenuePerMinute    float64   `json:"revenue_per_minute"`
	ConversionRate      float64   `json:"conversion_rate"`
	AverageCartValue    float64   `json:"average_cart_value"`
	TopCategories       []string  `json:"top_categories"`
	PopularProducts     []string  `json:"popular_products"`
}

// Stream Processing Framework (Simplified Flink-like)
type StreamProcessor struct {
	name        string
	inputChan   chan EcommerceEvent
	outputChans map[string]chan interface{}
	processors  []ProcessorFunc
	windows     map[string]*TimeWindow
	state       *StreamState
	ctx         context.Context
	cancel      context.CancelFunc
	wg          sync.WaitGroup
}

type ProcessorFunc func(event EcommerceEvent, state *StreamState) interface{}

type TimeWindow struct {
	Size     time.Duration
	Slide    time.Duration
	Buffer   []EcommerceEvent
	LastSlide time.Time
}

type StreamState struct {
	mu                  sync.RWMutex
	userSessions        map[string]*UserSessionState
	productAnalytics    map[string]*ProductState
	realTimeMetrics     *RealTimeMetrics
	eventCounts         map[EventType]int64
	lastMetricsUpdate   time.Time
}

type UserSessionState struct {
	UserID        string
	SessionID     string
	StartTime     time.Time
	LastActivity  time.Time
	EventsCount   int
	ProductsViewed map[string]bool
	CartValue     float64
	PurchaseValue float64
	Platform      string
	IsActive      bool
}

type ProductState struct {
	ProductID     string
	CategoryID    string
	ViewCount     int64
	CartAdditions int64
	Purchases     int64
	TotalRevenue  float64
}

// Stream Processor Constructor
func NewStreamProcessor(name string) *StreamProcessor {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &StreamProcessor{
		name:        name,
		inputChan:   make(chan EcommerceEvent, 1000),
		outputChans: make(map[string]chan interface{}),
		processors:  make([]ProcessorFunc, 0),
		windows:     make(map[string]*TimeWindow),
		state:       NewStreamState(),
		ctx:         ctx,
		cancel:      cancel,
	}
}

func NewStreamState() *StreamState {
	return &StreamState{
		userSessions:     make(map[string]*UserSessionState),
		productAnalytics: make(map[string]*ProductState),
		realTimeMetrics: &RealTimeMetrics{
			Timestamp: time.Now(),
		},
		eventCounts:       make(map[EventType]int64),
		lastMetricsUpdate: time.Now(),
	}
}

// Stream Operations
func (sp *StreamProcessor) AddProcessor(name string, processor ProcessorFunc) {
	sp.processors = append(sp.processors, processor)
	sp.outputChans[name] = make(chan interface{}, 100)
}

func (sp *StreamProcessor) AddTimeWindow(name string, size, slide time.Duration) {
	sp.windows[name] = &TimeWindow{
		Size:      size,
		Slide:     slide,
		Buffer:    make([]EcommerceEvent, 0),
		LastSlide: time.Now(),
	}
}

func (sp *StreamProcessor) Start() {
	sp.wg.Add(1)
	go sp.processEvents()
	
	// Start metrics updater
	sp.wg.Add(1)
	go sp.updateMetrics()
	
	fmt.Printf("🌊 Stream Processor '%s' started\n", sp.name)
}

func (sp *StreamProcessor) Stop() {
	sp.cancel()
	close(sp.inputChan)
	sp.wg.Wait()
	
	fmt.Printf("🔚 Stream Processor '%s' stopped\n", sp.name)
}

func (sp *StreamProcessor) SendEvent(event EcommerceEvent) {
	select {
	case sp.inputChan <- event:
	case <-sp.ctx.Done():
		return
	default:
		// Channel full, drop event (in production, use backpressure handling)
		fmt.Printf("⚠️ Dropping event due to full buffer: %s\n", event.EventID)
	}
}

func (sp *StreamProcessor) processEvents() {
	defer sp.wg.Done()
	
	for {
		select {
		case event, ok := <-sp.inputChan:
			if !ok {
				return
			}
			
			// Process event through all processors
			for i, processor := range sp.processors {
				result := processor(event, sp.state)
				if result != nil {
					// Send to corresponding output channel
					outputName := fmt.Sprintf("output_%d", i)
					select {
					case sp.outputChans[outputName] <- result:
					default:
						// Output channel full, skip
					}
				}
			}
			
			// Update time windows
			sp.updateTimeWindows(event)
			
		case <-sp.ctx.Done():
			return
		}
	}
}

func (sp *StreamProcessor) updateTimeWindows(event EcommerceEvent) {
	for name, window := range sp.windows {
		// Add event to window buffer
		window.Buffer = append(window.Buffer, event)
		
		// Check if window should slide
		if time.Since(window.LastSlide) >= window.Slide {
			sp.processWindow(name, window)
			window.LastSlide = time.Now()
			
			// Remove old events outside window
			cutoff := time.Now().Add(-window.Size)
			newBuffer := make([]EcommerceEvent, 0)
			for _, e := range window.Buffer {
				if e.Timestamp.After(cutoff) {
					newBuffer = append(newBuffer, e)
				}
			}
			window.Buffer = newBuffer
		}
	}
}

func (sp *StreamProcessor) processWindow(windowName string, window *TimeWindow) {
	// Process windowed analytics
	switch windowName {
	case "product_analytics":
		sp.processProductAnalyticsWindow(window)
	case "user_session":
		sp.processUserSessionWindow(window)
	}
}

func (sp *StreamProcessor) updateMetrics() {
	defer sp.wg.Done()
	
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			sp.calculateRealTimeMetrics()
		case <-sp.ctx.Done():
			return
		}
	}
}

// Processor Functions
func UserSessionProcessor(event EcommerceEvent, state *StreamState) interface{} {
	state.mu.Lock()
	defer state.mu.Unlock()
	
	sessionKey := fmt.Sprintf("%s:%s", event.UserID, event.SessionID)
	
	session, exists := state.userSessions[sessionKey]
	if !exists {
		session = &UserSessionState{
			UserID:         event.UserID,
			SessionID:      event.SessionID,
			StartTime:      event.Timestamp,
			LastActivity:   event.Timestamp,
			EventsCount:    0,
			ProductsViewed: make(map[string]bool),
			CartValue:      0.0,
			PurchaseValue:  0.0,
			Platform:       event.Platform,
			IsActive:       true,
		}
		state.userSessions[sessionKey] = session
	}
	
	// Update session
	session.LastActivity = event.Timestamp
	session.EventsCount++
	
	switch event.EventType {
	case ProductView:
		if event.ProductID != "" {
			session.ProductsViewed[event.ProductID] = true
		}
	case AddToCart:
		session.CartValue += event.Price * float64(event.Quantity)
	case RemoveFromCart:
		session.CartValue -= event.Price * float64(event.Quantity)
		if session.CartValue < 0 {
			session.CartValue = 0
		}
	case Purchase:
		session.PurchaseValue += event.Price * float64(event.Quantity)
	case UserLogout:
		session.IsActive = false
	}
	
	return session
}

func ProductAnalyticsProcessor(event EcommerceEvent, state *StreamState) interface{} {
	if event.ProductID == "" {
		return nil
	}
	
	state.mu.Lock()
	defer state.mu.Unlock()
	
	product, exists := state.productAnalytics[event.ProductID]
	if !exists {
		product = &ProductState{
			ProductID:     event.ProductID,
			CategoryID:    event.CategoryID,
			ViewCount:     0,
			CartAdditions: 0,
			Purchases:     0,
			TotalRevenue:  0.0,
		}
		state.productAnalytics[event.ProductID] = product
	}
	
	switch event.EventType {
	case ProductView:
		product.ViewCount++
	case AddToCart:
		product.CartAdditions++
	case Purchase:
		product.Purchases++
		product.TotalRevenue += event.Price * float64(event.Quantity)
	}
	
	return product
}

func RealTimeMetricsProcessor(event EcommerceEvent, state *StreamState) interface{} {
	state.mu.Lock()
	defer state.mu.Unlock()
	
	// Update event counts
	state.eventCounts[event.EventType]++
	
	return nil
}

// Analytics Functions
func (sp *StreamProcessor) processProductAnalyticsWindow(window *TimeWindow) {
	if len(window.Buffer) == 0 {
		return
	}
	
	// Aggregate product analytics for this window
	productStats := make(map[string]*ProductAnalytics)
	
	for _, event := range window.Buffer {
		if event.ProductID == "" {
			continue
		}
		
		stats, exists := productStats[event.ProductID]
		if !exists {
			stats = &ProductAnalytics{
				ProductID:    event.ProductID,
				CategoryID:   event.CategoryID,
				WindowStart:  time.Now().Add(-window.Size),
				WindowEnd:    time.Now(),
			}
			productStats[event.ProductID] = stats
		}
		
		switch event.EventType {
		case ProductView:
			stats.ViewCount++
		case AddToCart:
			stats.CartAdditions++
		case Purchase:
			stats.Purchases++
			stats.TotalRevenue += event.Price * float64(event.Quantity)
		}
	}
	
	// Calculate conversion rates
	for _, stats := range productStats {
		if stats.ViewCount > 0 {
			stats.ConversionRate = float64(stats.Purchases) / float64(stats.ViewCount) * 100
		}
	}
	
	// Output top products
	sp.outputTopProducts(productStats)
}

func (sp *StreamProcessor) processUserSessionWindow(window *TimeWindow) {
	// Calculate session analytics
	sessionAnalytics := make([]*UserSessionAnalytics, 0)
	
	sp.state.mu.RLock()
	for _, session := range sp.state.userSessions {
		analytics := &UserSessionAnalytics{
			UserID:           session.UserID,
			SessionID:        session.SessionID,
			SessionDuration:  session.LastActivity.Sub(session.StartTime),
			EventsCount:      session.EventsCount,
			ProductsViewed:   len(session.ProductsViewed),
			CartValue:        session.CartValue,
			PurchaseValue:    session.PurchaseValue,
			Platform:         session.Platform,
		}
		
		// Determine conversion status
		if session.PurchaseValue > 0 {
			analytics.ConversionStatus = "converted"
		} else if time.Since(session.LastActivity) > 30*time.Minute {
			analytics.ConversionStatus = "abandoned"
		} else {
			analytics.ConversionStatus = "active"
		}
		
		sessionAnalytics = append(sessionAnalytics, analytics)
	}
	sp.state.mu.RUnlock()
	
	// Output session analytics
	sp.outputSessionAnalytics(sessionAnalytics)
}

func (sp *StreamProcessor) calculateRealTimeMetrics() {
	sp.state.mu.Lock()
	defer sp.state.mu.Unlock()
	
	now := time.Now()
	timeDiff := now.Sub(sp.state.lastMetricsUpdate).Seconds()
	
	// Active users (users with activity in last 5 minutes)
	var activeUsers int64
	var totalCartValue float64
	var totalPurchaseValue float64
	var conversions int64
	var totalSessions int64
	
	for _, session := range sp.state.userSessions {
		if time.Since(session.LastActivity) <= 5*time.Minute {
			activeUsers++
		}
		
		totalSessions++
		totalCartValue += session.CartValue
		if session.PurchaseValue > 0 {
			conversions++
			totalPurchaseValue += session.PurchaseValue
		}
	}
	
	// Events per second
	totalEvents := int64(0)
	for _, count := range sp.state.eventCounts {
		totalEvents += count
	}
	eventsPerSecond := float64(totalEvents) / timeDiff
	
	// Update metrics
	sp.state.realTimeMetrics = &RealTimeMetrics{
		Timestamp:        now,
		ActiveUsers:      activeUsers,
		EventsPerSecond:  eventsPerSecond,
		RevenuePerMinute: totalPurchaseValue / (timeDiff / 60),
		ConversionRate:   float64(conversions) / float64(totalSessions) * 100,
		AverageCartValue: totalCartValue / float64(activeUsers+1),
		TopCategories:    sp.getTopCategories(),
		PopularProducts:  sp.getPopularProducts(),
	}
	
	sp.state.lastMetricsUpdate = now
	
	// Reset event counts for next interval
	for eventType := range sp.state.eventCounts {
		sp.state.eventCounts[eventType] = 0
	}
}

func (sp *StreamProcessor) getTopCategories() []string {
	categoryStats := make(map[string]int64)
	
	for _, product := range sp.state.productAnalytics {
		if product.CategoryID != "" {
			categoryStats[product.CategoryID] += product.ViewCount
		}
	}
	
	// Sort categories by view count
	type categoryCount struct {
		category string
		count    int64
	}
	
	categories := make([]categoryCount, 0, len(categoryStats))
	for cat, count := range categoryStats {
		categories = append(categories, categoryCount{cat, count})
	}
	
	sort.Slice(categories, func(i, j int) bool {
		return categories[i].count > categories[j].count
	})
	
	result := make([]string, 0, 5)
	for i := 0; i < len(categories) && i < 5; i++ {
		result = append(result, categories[i].category)
	}
	
	return result
}

func (sp *StreamProcessor) getPopularProducts() []string {
	// Sort products by view count
	type productCount struct {
		productID string
		count     int64
	}
	
	products := make([]productCount, 0, len(sp.state.productAnalytics))
	for pid, product := range sp.state.productAnalytics {
		products = append(products, productCount{pid, product.ViewCount})
	}
	
	sort.Slice(products, func(i, j int) bool {
		return products[i].count > products[j].count
	})
	
	result := make([]string, 0, 5)
	for i := 0; i < len(products) && i < 5; i++ {
		result = append(result, products[i].productID)
	}
	
	return result
}

func (sp *StreamProcessor) outputTopProducts(productStats map[string]*ProductAnalytics) {
	fmt.Println("\n📊 Top Products Analysis:")
	
	// Convert to slice for sorting
	products := make([]*ProductAnalytics, 0, len(productStats))
	for _, stats := range productStats {
		products = append(products, stats)
	}
	
	// Sort by revenue
	sort.Slice(products, func(i, j int) bool {
		return products[i].TotalRevenue > products[j].TotalRevenue
	})
	
	for i, product := range products {
		if i >= 5 { // Top 5
			break
		}
		fmt.Printf("  %d. Product %s: ₹%.2f revenue, %.1f%% conversion\n",
			i+1, product.ProductID, product.TotalRevenue, product.ConversionRate)
	}
}

func (sp *StreamProcessor) outputSessionAnalytics(analytics []*UserSessionAnalytics) {
	converted := 0
	abandoned := 0
	active := 0
	
	for _, session := range analytics {
		switch session.ConversionStatus {
		case "converted":
			converted++
		case "abandoned":
			abandoned++
		case "active":
			active++
		}
	}
	
	fmt.Printf("\n📈 Session Analytics: %d converted, %d abandoned, %d active\n",
		converted, abandoned, active)
}

func (sp *StreamProcessor) PrintRealTimeMetrics() {
	sp.state.mu.RLock()
	metrics := sp.state.realTimeMetrics
	sp.state.mu.RUnlock()
	
	fmt.Println("\n🔥 Real-time Metrics:")
	fmt.Printf("  Active Users: %d\n", metrics.ActiveUsers)
	fmt.Printf("  Events/Second: %.2f\n", metrics.EventsPerSecond)
	fmt.Printf("  Revenue/Minute: ₹%.2f\n", metrics.RevenuePerMinute)
	fmt.Printf("  Conversion Rate: %.2f%%\n", metrics.ConversionRate)
	fmt.Printf("  Avg Cart Value: ₹%.2f\n", metrics.AverageCartValue)
	fmt.Printf("  Top Categories: %v\n", metrics.TopCategories)
	fmt.Printf("  Popular Products: %v\n", metrics.PopularProducts)
}

// Event Generator
type EventGenerator struct {
	users     []string
	products  []string
	categories []string
	platforms []string
	cities    []string
}

func NewEventGenerator() *EventGenerator {
	return &EventGenerator{
		users:     []string{"U001", "U002", "U003", "U004", "U005", "U006", "U007", "U008", "U009", "U010"},
		products:  []string{"P001", "P002", "P003", "P004", "P005", "P006", "P007", "P008", "P009", "P010"},
		categories: []string{"electronics", "clothing", "books", "home", "sports", "beauty"},
		platforms: []string{"web", "android", "ios"},
		cities:    []string{"Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Pune"},
	}
}

func (eg *EventGenerator) GenerateEvent() EcommerceEvent {
	eventTypes := []EventType{
		ProductView, ProductView, ProductView, // More views
		AddToCart, AddToCart,
		Purchase,
		ProductSearch,
		UserLogin,
	}
	
	eventType := eventTypes[rand.Intn(len(eventTypes))]
	userID := eg.users[rand.Intn(len(eg.users))]
	sessionID := fmt.Sprintf("sess_%s_%d", userID, rand.Intn(100))
	
	event := EcommerceEvent{
		EventID:   fmt.Sprintf("evt_%d", time.Now().UnixNano()),
		EventType: eventType,
		UserID:    userID,
		SessionID: sessionID,
		Timestamp: time.Now(),
		Platform:  eg.platforms[rand.Intn(len(eg.platforms))],
		Location: Location{
			Country: "India",
			State:   "Maharashtra",
			City:    eg.cities[rand.Intn(len(eg.cities))],
		},
		Metadata: make(map[string]interface{}),
	}
	
	// Add event-specific data
	switch eventType {
	case ProductView, AddToCart, Purchase:
		event.ProductID = eg.products[rand.Intn(len(eg.products))]
		event.CategoryID = eg.categories[rand.Intn(len(eg.categories))]
		event.Price = math.Round(rand.Float64()*10000*100) / 100 // ₹0-10,000
		event.Quantity = rand.Intn(5) + 1
	}
	
	return event
}

// Demo Function
func main() {
	fmt.Println("🛒 Indian E-commerce Stream Processing Demo")
	fmt.Println("=" + "=" + "=" + "=" + "=" + "=" + "=" + "=" + "=" + "=" + "=" + "=" + "=")
	
	// Create stream processor
	processor := NewStreamProcessor("ecommerce-analytics")
	
	// Add processors
	processor.AddProcessor("user_session", UserSessionProcessor)
	processor.AddProcessor("product_analytics", ProductAnalyticsProcessor)
	processor.AddProcessor("real_time_metrics", RealTimeMetricsProcessor)
	
	// Add time windows
	processor.AddTimeWindow("product_analytics", 2*time.Minute, 30*time.Second)
	processor.AddTimeWindow("user_session", 5*time.Minute, 1*time.Minute)
	
	// Start processing
	processor.Start()
	
	// Generate events
	generator := NewEventGenerator()
	
	fmt.Println("\n🌊 Generating e-commerce events...")
	
	// Generate events for 30 seconds
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	
	eventCount := 0
	ticker := time.NewTicker(100 * time.Millisecond) // 10 events per second
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			event := generator.GenerateEvent()
			processor.SendEvent(event)
			eventCount++
			
			if eventCount%50 == 0 {
				fmt.Printf("📈 Generated %d events\n", eventCount)
				processor.PrintRealTimeMetrics()
			}
			
		case <-ctx.Done():
			fmt.Printf("\n✅ Generated total %d events\n", eventCount)
			goto cleanup
		}
	}
	
cleanup:
	// Wait a bit for final processing
	time.Sleep(2 * time.Second)
	
	// Print final metrics
	fmt.Println("\n📊 Final Analytics:")
	processor.PrintRealTimeMetrics()
	
	// Stop processor
	processor.Stop()
	
	fmt.Println("\n✅ Stream Processing Demo completed!")
}

/*
Key Apache Flink Benefits demonstrated:

1. Real-time Processing: Immediate analytics और insights
2. Stateful Operations: Complex aggregations और joins
3. Time Windows: Time-based analytics और trends
4. Low Latency: Millisecond processing for real-time decisions
5. Fault Tolerance: Checkpointing और recovery mechanisms
6. Scalability: Horizontal scaling across multiple nodes
7. Complex Event Processing: Multi-step analytics workflows

Production Considerations:
- Checkpointing for fault tolerance
- Backpressure handling for load management
- State backend optimization
- Watermarks for late event handling
- Exactly-once processing guarantees
*/
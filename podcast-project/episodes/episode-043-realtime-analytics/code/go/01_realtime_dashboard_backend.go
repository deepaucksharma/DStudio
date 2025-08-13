/*
Real-time Dashboard Backend in Go
Episode 43: Real-time Analytics at Scale

Production-grade real-time dashboard with WebSocket support
Use Case: Swiggy delivery dashboard - real-time order tracking and analytics
*/

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"sync"
	"time"

	"github.com/gorilla/mux"
	"github.com/gorilla/websocket"
)

// SwiggyOrder represents a delivery order
// Swiggy order की complete information
type SwiggyOrder struct {
	OrderID        string            `json:"order_id"`
	CustomerID     string            `json:"customer_id"`
	RestaurantID   string            `json:"restaurant_id"`
	RestaurantName string            `json:"restaurant_name"`
	DeliveryPartnerID string         `json:"delivery_partner_id,omitempty"`
	Status         string            `json:"status"` // placed, confirmed, preparing, ready, picked_up, delivered, cancelled
	Items          []OrderItem       `json:"items"`
	TotalAmount    float64           `json:"total_amount"`
	DeliveryFee    float64           `json:"delivery_fee"`
	Address        DeliveryAddress   `json:"address"`
	Location       GPSLocation       `json:"location"`
	Timestamps     OrderTimestamps   `json:"timestamps"`
	Metadata       map[string]string `json:"metadata"`
}

type OrderItem struct {
	ItemID       string  `json:"item_id"`
	Name         string  `json:"name"`
	Quantity     int     `json:"quantity"`
	Price        float64 `json:"price"`
	Category     string  `json:"category"`
	Customizations []string `json:"customizations,omitempty"`
}

type DeliveryAddress struct {
	AddressLine1 string  `json:"address_line1"`
	AddressLine2 string  `json:"address_line2"`
	City         string  `json:"city"`
	Pincode      string  `json:"pincode"`
	Latitude     float64 `json:"latitude"`
	Longitude    float64 `json:"longitude"`
}

type GPSLocation struct {
	Latitude  float64   `json:"latitude"`
	Longitude float64   `json:"longitude"`
	Timestamp time.Time `json:"timestamp"`
	Accuracy  float64   `json:"accuracy"`
}

type OrderTimestamps struct {
	PlacedAt    time.Time  `json:"placed_at"`
	ConfirmedAt *time.Time `json:"confirmed_at,omitempty"`
	PreparedAt  *time.Time `json:"prepared_at,omitempty"`
	PickedUpAt  *time.Time `json:"picked_up_at,omitempty"`
	DeliveredAt *time.Time `json:"delivered_at,omitempty"`
	CancelledAt *time.Time `json:"cancelled_at,omitempty"`
}

// RealTimeMetrics represents dashboard metrics
// Dashboard के लिए real-time metrics
type RealTimeMetrics struct {
	TotalOrders       int                    `json:"total_orders"`
	ActiveOrders      int                    `json:"active_orders"`
	CompletedOrders   int                    `json:"completed_orders"`
	CancelledOrders   int                    `json:"cancelled_orders"`
	TotalRevenue      float64                `json:"total_revenue"`
	AverageOrderValue float64                `json:"average_order_value"`
	OrdersByStatus    map[string]int         `json:"orders_by_status"`
	TopRestaurants    []RestaurantMetrics    `json:"top_restaurants"`
	DeliveryMetrics   DeliveryMetrics        `json:"delivery_metrics"`
	OrdersByHour      map[string]int         `json:"orders_by_hour"`
	Timestamp         time.Time              `json:"timestamp"`
}

type RestaurantMetrics struct {
	RestaurantID   string  `json:"restaurant_id"`
	RestaurantName string  `json:"restaurant_name"`
	TotalOrders    int     `json:"total_orders"`
	Revenue        float64 `json:"revenue"`
	AvgRating      float64 `json:"avg_rating"`
	AvgPrepTime    int     `json:"avg_prep_time_minutes"`
}

type DeliveryMetrics struct {
	ActiveDeliveryPartners int     `json:"active_delivery_partners"`
	AverageDeliveryTime    int     `json:"avg_delivery_time_minutes"`
	DeliverySuccessRate    float64 `json:"delivery_success_rate"`
	OnTimeDeliveryRate     float64 `json:"on_time_delivery_rate"`
}

// OrderStore manages order data in memory
// Memory में orders को store और manage करता है
type OrderStore struct {
	orders map[string]*SwiggyOrder
	mutex  sync.RWMutex
}

func NewOrderStore() *OrderStore {
	return &OrderStore{
		orders: make(map[string]*SwiggyOrder),
	}
}

func (os *OrderStore) AddOrder(order *SwiggyOrder) {
	os.mutex.Lock()
	defer os.mutex.Unlock()
	os.orders[order.OrderID] = order
}

func (os *OrderStore) UpdateOrder(orderID string, updates map[string]interface{}) error {
	os.mutex.Lock()
	defer os.mutex.Unlock()
	
	order, exists := os.orders[orderID]
	if !exists {
		return fmt.Errorf("order not found: %s", orderID)
	}
	
	// Update order fields
	if status, ok := updates["status"].(string); ok {
		order.Status = status
		
		// Update timestamps based on status
		now := time.Now()
		switch status {
		case "confirmed":
			order.Timestamps.ConfirmedAt = &now
		case "ready":
			order.Timestamps.PreparedAt = &now
		case "picked_up":
			order.Timestamps.PickedUpAt = &now
		case "delivered":
			order.Timestamps.DeliveredAt = &now
		case "cancelled":
			order.Timestamps.CancelledAt = &now
		}
	}
	
	if deliveryPartnerID, ok := updates["delivery_partner_id"].(string); ok {
		order.DeliveryPartnerID = deliveryPartnerID
	}
	
	if location, ok := updates["location"].(GPSLocation); ok {
		order.Location = location
	}
	
	return nil
}

func (os *OrderStore) GetOrder(orderID string) (*SwiggyOrder, error) {
	os.mutex.RLock()
	defer os.mutex.RUnlock()
	
	order, exists := os.orders[orderID]
	if !exists {
		return nil, fmt.Errorf("order not found: %s", orderID)
	}
	
	return order, nil
}

func (os *OrderStore) GetAllOrders() []*SwiggyOrder {
	os.mutex.RLock()
	defer os.mutex.RUnlock()
	
	orders := make([]*SwiggyOrder, 0, len(os.orders))
	for _, order := range os.orders {
		orders = append(orders, order)
	}
	
	return orders
}

func (os *OrderStore) GetOrdersByStatus(status string) []*SwiggyOrder {
	os.mutex.RLock()
	defer os.mutex.RUnlock()
	
	var orders []*SwiggyOrder
	for _, order := range os.orders {
		if order.Status == status {
			orders = append(orders, order)
		}
	}
	
	return orders
}

// MetricsCalculator calculates real-time metrics
// Real-time metrics को calculate करता है
type MetricsCalculator struct {
	orderStore *OrderStore
}

func NewMetricsCalculator(orderStore *OrderStore) *MetricsCalculator {
	return &MetricsCalculator{orderStore: orderStore}
}

func (mc *MetricsCalculator) CalculateMetrics() *RealTimeMetrics {
	orders := mc.orderStore.GetAllOrders()
	
	metrics := &RealTimeMetrics{
		OrdersByStatus: make(map[string]int),
		OrdersByHour:   make(map[string]int),
		Timestamp:      time.Now(),
	}
	
	// Basic counts
	metrics.TotalOrders = len(orders)
	
	totalRevenue := 0.0
	completedRevenue := 0.0
	restaurantStats := make(map[string]*RestaurantMetrics)
	
	var completedDeliveryTimes []int
	var onTimeDeliveries int
	totalDeliveries := 0
	
	for _, order := range orders {
		// Status distribution
		metrics.OrdersByStatus[order.Status]++
		
		// Revenue calculation
		if order.Status == "delivered" {
			completedRevenue += order.TotalAmount
			metrics.CompletedOrders++
			totalDeliveries++
		} else if order.Status == "cancelled" {
			metrics.CancelledOrders++
		} else {
			metrics.ActiveOrders++
		}
		
		totalRevenue += order.TotalAmount
		
		// Restaurant statistics
		if _, exists := restaurantStats[order.RestaurantID]; !exists {
			restaurantStats[order.RestaurantID] = &RestaurantMetrics{
				RestaurantID:   order.RestaurantID,
				RestaurantName: order.RestaurantName,
				AvgRating:      4.0 + rand.Float64(), // Simulated rating
			}
		}
		restaurantStats[order.RestaurantID].TotalOrders++
		if order.Status == "delivered" {
			restaurantStats[order.RestaurantID].Revenue += order.TotalAmount
		}
		
		// Order timing analysis
		hour := order.Timestamps.PlacedAt.Hour()
		hourKey := fmt.Sprintf("%02d:00", hour)
		metrics.OrdersByHour[hourKey]++
		
		// Delivery time analysis
		if order.Status == "delivered" && order.Timestamps.DeliveredAt != nil {
			deliveryTime := int(order.Timestamps.DeliveredAt.Sub(order.Timestamps.PlacedAt).Minutes())
			completedDeliveryTimes = append(completedDeliveryTimes, deliveryTime)
			
			// Consider on-time if delivered within 45 minutes
			if deliveryTime <= 45 {
				onTimeDeliveries++
			}
		}
	}
	
	// Calculate averages
	if metrics.CompletedOrders > 0 {
		metrics.AverageOrderValue = completedRevenue / float64(metrics.CompletedOrders)
	}
	metrics.TotalRevenue = completedRevenue
	
	// Top restaurants
	for _, stats := range restaurantStats {
		metrics.TopRestaurants = append(metrics.TopRestaurants, *stats)
	}
	
	// Sort top restaurants by revenue
	for i := 0; i < len(metrics.TopRestaurants)-1; i++ {
		for j := i + 1; j < len(metrics.TopRestaurants); j++ {
			if metrics.TopRestaurants[i].Revenue < metrics.TopRestaurants[j].Revenue {
				metrics.TopRestaurants[i], metrics.TopRestaurants[j] = 
					metrics.TopRestaurants[j], metrics.TopRestaurants[i]
			}
		}
	}
	
	// Limit to top 5 restaurants
	if len(metrics.TopRestaurants) > 5 {
		metrics.TopRestaurants = metrics.TopRestaurants[:5]
	}
	
	// Delivery metrics
	metrics.DeliveryMetrics.ActiveDeliveryPartners = rand.Intn(100) + 50 // Simulated
	
	if len(completedDeliveryTimes) > 0 {
		totalTime := 0
		for _, time := range completedDeliveryTimes {
			totalTime += time
		}
		metrics.DeliveryMetrics.AverageDeliveryTime = totalTime / len(completedDeliveryTimes)
	}
	
	if totalDeliveries > 0 {
		metrics.DeliveryMetrics.DeliverySuccessRate = float64(metrics.CompletedOrders) / float64(metrics.CompletedOrders + metrics.CancelledOrders) * 100
		metrics.DeliveryMetrics.OnTimeDeliveryRate = float64(onTimeDeliveries) / float64(totalDeliveries) * 100
	}
	
	return metrics
}

// WebSocketManager manages WebSocket connections
// WebSocket connections को manage करता है
type WebSocketManager struct {
	clients    map[*websocket.Conn]bool
	broadcast  chan []byte
	register   chan *websocket.Conn
	unregister chan *websocket.Conn
	mutex      sync.RWMutex
}

func NewWebSocketManager() *WebSocketManager {
	return &WebSocketManager{
		clients:    make(map[*websocket.Conn]bool),
		broadcast:  make(chan []byte),
		register:   make(chan *websocket.Conn),
		unregister: make(chan *websocket.Conn),
	}
}

func (wsm *WebSocketManager) Run() {
	for {
		select {
		case client := <-wsm.register:
			wsm.mutex.Lock()
			wsm.clients[client] = true
			wsm.mutex.Unlock()
			log.Printf("📱 Client connected. Total clients: %d", len(wsm.clients))
			
		case client := <-wsm.unregister:
			wsm.mutex.Lock()
			if _, ok := wsm.clients[client]; ok {
				delete(wsm.clients, client)
				client.Close()
			}
			wsm.mutex.Unlock()
			log.Printf("📱 Client disconnected. Total clients: %d", len(wsm.clients))
			
		case message := <-wsm.broadcast:
			wsm.mutex.RLock()
			for client := range wsm.clients {
				select {
				case client.WriteMessage(websocket.TextMessage, message):
				default:
					delete(wsm.clients, client)
					client.Close()
				}
			}
			wsm.mutex.RUnlock()
		}
	}
}

func (wsm *WebSocketManager) BroadcastMetrics(metrics *RealTimeMetrics) {
	data, err := json.Marshal(map[string]interface{}{
		"type": "metrics_update",
		"data": metrics,
	})
	if err != nil {
		log.Printf("Error marshaling metrics: %v", err)
		return
	}
	
	select {
	case wsm.broadcast <- data:
	default:
		log.Println("Broadcast channel full, dropping message")
	}
}

func (wsm *WebSocketManager) BroadcastOrderUpdate(order *SwiggyOrder) {
	data, err := json.Marshal(map[string]interface{}{
		"type": "order_update",
		"data": order,
	})
	if err != nil {
		log.Printf("Error marshaling order: %v", err)
		return
	}
	
	select {
	case wsm.broadcast <- data:
	default:
		log.Println("Broadcast channel full, dropping message")
	}
}

// DashboardServer is the main server
// Main dashboard server
type DashboardServer struct {
	orderStore        *OrderStore
	metricsCalculator *MetricsCalculator
	wsManager         *WebSocketManager
	upgrader          websocket.Upgrader
}

func NewDashboardServer() *DashboardServer {
	orderStore := NewOrderStore()
	metricsCalculator := NewMetricsCalculator(orderStore)
	wsManager := NewWebSocketManager()
	
	return &DashboardServer{
		orderStore:        orderStore,
		metricsCalculator: metricsCalculator,
		wsManager:         wsManager,
		upgrader: websocket.Upgrader{
			CheckOrigin: func(r *http.Request) bool {
				return true // Allow all origins in demo
			},
		},
	}
}

func (ds *DashboardServer) StartMetricsBroadcast(ctx context.Context) {
	ticker := time.NewTicker(2 * time.Second) // Broadcast metrics every 2 seconds
	defer ticker.Stop()
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			metrics := ds.metricsCalculator.CalculateMetrics()
			ds.wsManager.BroadcastMetrics(metrics)
		}
	}
}

// HTTP Handlers

func (ds *DashboardServer) handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := ds.upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		return
	}
	
	ds.wsManager.register <- conn
	
	// Send initial metrics
	metrics := ds.metricsCalculator.CalculateMetrics()
	data, _ := json.Marshal(map[string]interface{}{
		"type": "initial_metrics",
		"data": metrics,
	})
	conn.WriteMessage(websocket.TextMessage, data)
	
	// Handle client messages (ping/pong, etc.)
	defer func() {
		ds.wsManager.unregister <- conn
	}()
	
	for {
		_, _, err := conn.ReadMessage()
		if err != nil {
			break
		}
	}
}

func (ds *DashboardServer) handleCreateOrder(w http.ResponseWriter, r *http.Request) {
	var order SwiggyOrder
	if err := json.NewDecoder(r.Body).Decode(&order); err != nil {
		http.Error(w, "Invalid order data", http.StatusBadRequest)
		return
	}
	
	// Set default values
	order.OrderID = fmt.Sprintf("ORD_%d", time.Now().UnixNano()/1000000)
	order.Status = "placed"
	order.Timestamps.PlacedAt = time.Now()
	order.Location = GPSLocation{
		Latitude:  order.Address.Latitude,
		Longitude: order.Address.Longitude,
		Timestamp: time.Now(),
		Accuracy:  10.0,
	}
	
	ds.orderStore.AddOrder(&order)
	ds.wsManager.BroadcastOrderUpdate(&order)
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(order)
	
	log.Printf("🆕 New order created: %s (₹%.2f)", order.OrderID, order.TotalAmount)
}

func (ds *DashboardServer) handleUpdateOrder(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	orderID := vars["orderID"]
	
	var updates map[string]interface{}
	if err := json.NewDecoder(r.Body).Decode(&updates); err != nil {
		http.Error(w, "Invalid update data", http.StatusBadRequest)
		return
	}
	
	if err := ds.orderStore.UpdateOrder(orderID, updates); err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}
	
	// Get updated order and broadcast
	order, _ := ds.orderStore.GetOrder(orderID)
	ds.wsManager.BroadcastOrderUpdate(order)
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(order)
	
	log.Printf("🔄 Order updated: %s -> %s", orderID, updates["status"])
}

func (ds *DashboardServer) handleGetOrders(w http.ResponseWriter, r *http.Request) {
	status := r.URL.Query().Get("status")
	
	var orders []*SwiggyOrder
	if status != "" {
		orders = ds.orderStore.GetOrdersByStatus(status)
	} else {
		orders = ds.orderStore.GetAllOrders()
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(orders)
}

func (ds *DashboardServer) handleGetMetrics(w http.ResponseWriter, r *http.Request) {
	metrics := ds.metricsCalculator.CalculateMetrics()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(metrics)
}

func (ds *DashboardServer) handleHealthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":    "healthy",
		"timestamp": time.Now(),
		"version":   "1.0.0",
		"service":   "swiggy-dashboard",
	})
}

// Order Generator for simulation
// Testing के लिए sample orders generate करता है
func (ds *DashboardServer) StartOrderSimulation(ctx context.Context) {
	restaurants := []string{
		"मैकडॉनल्ड्स", "डोमिनोज पिज्जा", "केएफसी", "सब्वे", "पिज्जा हट",
		"बर्गर किंग", "तंदूर रेस्टोरेंट", "पंजाबी धाबा", "साउथ इंडियन", "चाइना टाउन",
	}
	
	cities := []string{"Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Pune", "Hyderabad"}
	
	items := []OrderItem{
		{ItemID: "ITEM_001", Name: "वेज बर्गर", Quantity: 1, Price: 120.0, Category: "Main Course"},
		{ItemID: "ITEM_002", Name: "चिकन पिज्जा", Quantity: 1, Price: 280.0, Category: "Pizza"},
		{ItemID: "ITEM_003", Name: "फ्राइज", Quantity: 2, Price: 80.0, Category: "Sides"},
		{ItemID: "ITEM_004", Name: "कोल्ड ड्रिंक", Quantity: 2, Price: 60.0, Category: "Beverages"},
	}
	
	ticker := time.NewTicker(3 * time.Second) // New order every 3 seconds
	defer ticker.Stop()
	
	orderCounter := 0
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			orderCounter++
			
			// Create random order
			restaurantName := restaurants[rand.Intn(len(restaurants))]
			city := cities[rand.Intn(len(cities))]
			
			// Random selection of items
			orderItems := []OrderItem{}
			itemCount := rand.Intn(3) + 1 // 1-3 items
			for i := 0; i < itemCount; i++ {
				item := items[rand.Intn(len(items))]
				item.Quantity = rand.Intn(3) + 1
				orderItems = append(orderItems, item)
			}
			
			// Calculate total
			total := 0.0
			for _, item := range orderItems {
				total += item.Price * float64(item.Quantity)
			}
			
			deliveryFee := 30.0 + rand.Float64()*20.0 // ₹30-50 delivery fee
			
			order := &SwiggyOrder{
				OrderID:        fmt.Sprintf("SIM_%06d", orderCounter),
				CustomerID:     fmt.Sprintf("CUST_%03d", rand.Intn(100)+1),
				RestaurantID:   fmt.Sprintf("REST_%03d", rand.Intn(len(restaurants))+1),
				RestaurantName: restaurantName,
				Status:         "placed",
				Items:          orderItems,
				TotalAmount:    total,
				DeliveryFee:    deliveryFee,
				Address: DeliveryAddress{
					AddressLine1: fmt.Sprintf("Flat %d, Building %d", rand.Intn(100)+1, rand.Intn(50)+1),
					AddressLine2: fmt.Sprintf("Sector %d", rand.Intn(20)+1),
					City:         city,
					Pincode:      fmt.Sprintf("%06d", rand.Intn(900000)+100000),
					Latitude:     19.0760 + rand.Float64()*0.1,
					Longitude:    72.8777 + rand.Float64()*0.1,
				},
				Location: GPSLocation{
					Latitude:  19.0760 + rand.Float64()*0.1,
					Longitude: 72.8777 + rand.Float64()*0.1,
					Timestamp: time.Now(),
					Accuracy:  10.0,
				},
				Timestamps: OrderTimestamps{
					PlacedAt: time.Now(),
				},
				Metadata: map[string]string{
					"channel":   "mobile_app",
					"device_id": fmt.Sprintf("DEVICE_%d", rand.Intn(1000)),
					"platform":  "android",
				},
			}
			
			ds.orderStore.AddOrder(order)
			ds.wsManager.BroadcastOrderUpdate(order)
			
			log.Printf("🎭 Simulated order: %s (%s) - ₹%.2f", order.OrderID, restaurantName, total)
		}
	}
}

// Order Status Simulator
// Orders की status को automatically update करता है
func (ds *DashboardServer) StartStatusSimulation(ctx context.Context) {
	ticker := time.NewTicker(5 * time.Second) // Update status every 5 seconds
	defer ticker.Stop()
	
	statusProgression := []string{"confirmed", "preparing", "ready", "picked_up", "delivered"}
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			orders := ds.orderStore.GetAllOrders()
			
			for _, order := range orders {
				// Skip if order is already completed
				if order.Status == "delivered" || order.Status == "cancelled" {
					continue
				}
				
				// Random chance to progress status
				if rand.Float64() < 0.3 { // 30% chance to progress
					var newStatus string
					
					switch order.Status {
					case "placed":
						if rand.Float64() < 0.9 { // 90% chance to confirm, 10% to cancel
							newStatus = "confirmed"
						} else {
							newStatus = "cancelled"
						}
					case "confirmed":
						newStatus = "preparing"
					case "preparing":
						newStatus = "ready"
					case "ready":
						newStatus = "picked_up"
						// Assign delivery partner
						ds.orderStore.UpdateOrder(order.OrderID, map[string]interface{}{
							"delivery_partner_id": fmt.Sprintf("DP_%03d", rand.Intn(200)+1),
						})
					case "picked_up":
						newStatus = "delivered"
					}
					
					if newStatus != "" {
						ds.orderStore.UpdateOrder(order.OrderID, map[string]interface{}{
							"status": newStatus,
						})
						
						// Get updated order and broadcast
						updatedOrder, _ := ds.orderStore.GetOrder(order.OrderID)
						ds.wsManager.BroadcastOrderUpdate(updatedOrder)
						
						log.Printf("🔄 Status update: %s -> %s", order.OrderID, newStatus)
					}
				}
			}
		}
	}
}

func main() {
	log.Println("🍕 Starting Swiggy Real-time Dashboard...")
	
	// Initialize server
	server := NewDashboardServer()
	
	// Start WebSocket manager
	go server.wsManager.Run()
	
	// Create context for graceful shutdown
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	
	// Start background processes
	go server.StartMetricsBroadcast(ctx)
	go server.StartOrderSimulation(ctx)
	go server.StartStatusSimulation(ctx)
	
	// Setup HTTP routes
	r := mux.NewRouter()
	
	// WebSocket endpoint
	r.HandleFunc("/ws", server.handleWebSocket)
	
	// REST API endpoints
	api := r.PathPrefix("/api/v1").Subrouter()
	api.HandleFunc("/orders", server.handleCreateOrder).Methods("POST")
	api.HandleFunc("/orders/{orderID}", server.handleUpdateOrder).Methods("PUT")
	api.HandleFunc("/orders", server.handleGetOrders).Methods("GET")
	api.HandleFunc("/metrics", server.handleGetMetrics).Methods("GET")
	api.HandleFunc("/health", server.handleHealthCheck).Methods("GET")
	
	// Static files (in production, serve from CDN)
	r.PathPrefix("/").Handler(http.FileServer(http.Dir("./static/")))
	
	// Add CORS middleware
	r.Use(func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Access-Control-Allow-Origin", "*")
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
			
			if r.Method == "OPTIONS" {
				w.WriteHeader(http.StatusOK)
				return
			}
			
			next.ServeHTTP(w, r)
		})
	})
	
	// Start server
	port := ":8080"
	log.Printf("🚀 Dashboard server starting on port %s", port)
	log.Printf("📊 WebSocket endpoint: ws://localhost%s/ws", port)
	log.Printf("🔗 REST API: http://localhost%s/api/v1", port)
	log.Printf("💊 Health check: http://localhost%s/api/v1/health", port)
	
	if err := http.ListenAndServe(port, r); err != nil {
		log.Fatal("Server failed to start:", err)
	}
}

/*
API Usage Examples:

1. Create Order:
POST /api/v1/orders
{
  "customer_id": "CUST_001",
  "restaurant_id": "REST_001",
  "restaurant_name": "मैकडॉनल्ड्स",
  "items": [
    {
      "item_id": "ITEM_001",
      "name": "वेज बर्गर",
      "quantity": 2,
      "price": 120.0,
      "category": "Main Course"
    }
  ],
  "total_amount": 240.0,
  "delivery_fee": 30.0,
  "address": {
    "address_line1": "Flat 101, Tower A",
    "city": "Mumbai",
    "pincode": "400001",
    "latitude": 19.0760,
    "longitude": 72.8777
  }
}

2. Update Order Status:
PUT /api/v1/orders/{orderID}
{
  "status": "confirmed",
  "delivery_partner_id": "DP_001"
}

3. Get Orders:
GET /api/v1/orders?status=active

4. Get Real-time Metrics:
GET /api/v1/metrics

5. WebSocket Connection:
Connect to ws://localhost:8080/ws for real-time updates

The server will automatically:
- Generate sample orders every 3 seconds
- Update order statuses every 5 seconds
- Broadcast metrics every 2 seconds
- Handle WebSocket connections for real-time dashboard updates
*/
// Episode 34: Vector Clocks - Go Implementation
// Mumbai E-commerce Order Processing System
//
// Demonstrates: Vector clocks in distributed order processing
// Context: Flipkart warehouses coordination across Mumbai

package main

import (
	"fmt"
	"log"
	"sync"
	"time"
)

// OrderEvent represents an event in the e-commerce system
type OrderEvent struct {
	OrderID     string            `json:"order_id"`
	WarehouseID string            `json:"warehouse_id"`
	EventType   string            `json:"event_type"`
	ProductID   string            `json:"product_id"`
	Quantity    int               `json:"quantity"`
	Timestamp   time.Time         `json:"timestamp"`
	VectorClock map[string]int    `json:"vector_clock"`
	CustomerID  string            `json:"customer_id"`
}

// FlipkartWarehouseVectorClock manages vector clock for a warehouse
type FlipkartWarehouseVectorClock struct {
	warehouseID string
	clock       map[string]int
	eventLog    []OrderEvent
	mutex       sync.RWMutex
	allWarehouses []string
}

// NewFlipkartWarehouseVectorClock creates a new warehouse vector clock
func NewFlipkartWarehouseVectorClock(warehouseID string, allWarehouses []string) *FlipkartWarehouseVectorClock {
	clock := make(map[string]int)
	for _, warehouse := range allWarehouses {
		clock[warehouse] = 0
	}
	
	return &FlipkartWarehouseVectorClock{
		warehouseID:   warehouseID,
		clock:         clock,
		eventLog:      make([]OrderEvent, 0),
		allWarehouses: allWarehouses,
	}
}

// ProcessLocalEvent processes a local warehouse event
func (w *FlipkartWarehouseVectorClock) ProcessLocalEvent(orderID, eventType, productID, customerID string, quantity int) OrderEvent {
	w.mutex.Lock()
	defer w.mutex.Unlock()
	
	// Increment own clock
	w.clock[w.warehouseID]++
	
	event := OrderEvent{
		OrderID:     orderID,
		WarehouseID: w.warehouseID,
		EventType:   eventType,
		ProductID:   productID,
		Quantity:    quantity,
		Timestamp:   time.Now(),
		VectorClock: w.copyClockMap(),
		CustomerID:  customerID,
	}
	
	w.eventLog = append(w.eventLog, event)
	
	fmt.Printf("📦 %s | %s | Order: %s | Product: %s | Clock: %v\n", 
		w.warehouseID, eventType, orderID, productID, w.clock)
	
	return event
}

// ReceiveRemoteEvent receives an event from another warehouse
func (w *FlipkartWarehouseVectorClock) ReceiveRemoteEvent(remoteEvent OrderEvent) {
	w.mutex.Lock()
	defer w.mutex.Unlock()
	
	// Update vector clock using max rule
	for warehouse, clockValue := range remoteEvent.VectorClock {
		if currentValue, exists := w.clock[warehouse]; exists {
			if clockValue > currentValue {
				w.clock[warehouse] = clockValue
			}
		}
	}
	
	// Increment own clock
	w.clock[w.warehouseID]++
	
	w.eventLog = append(w.eventLog, remoteEvent)
	
	fmt.Printf("📨 %s received event from %s: %s | Updated Clock: %v\n",
		w.warehouseID, remoteEvent.WarehouseID, remoteEvent.EventType, w.clock)
}

// CompareEvents compares two events using vector clocks
func (w *FlipkartWarehouseVectorClock) CompareEvents(event1, event2 OrderEvent) string {
	clock1 := event1.VectorClock
	clock2 := event2.VectorClock
	
	event1Before := true
	event1StrictlyBefore := false
	event2Before := true
	event2StrictlyBefore := false
	
	for _, warehouse := range w.allWarehouses {
		c1, exists1 := clock1[warehouse]
		if !exists1 {
			c1 = 0
		}
		c2, exists2 := clock2[warehouse]
		if !exists2 {
			c2 = 0
		}
		
		if c1 > c2 {
			event1Before = false
		}
		if c1 < c2 {
			event1StrictlyBefore = true
			event2Before = false
		}
		if c2 > c1 {
			event2Before = false
		}
		if c2 < c1 {
			event2StrictlyBefore = true
			event1Before = false
		}
	}
	
	if event1Before && event1StrictlyBefore {
		return "BEFORE"
	} else if event2Before && event2StrictlyBefore {
		return "AFTER"
	} else if w.mapsEqual(clock1, clock2) {
		return "SAME"
	} else {
		return "CONCURRENT"
	}
}

// Helper functions
func (w *FlipkartWarehouseVectorClock) copyClockMap() map[string]int {
	copy := make(map[string]int)
	for k, v := range w.clock {
		copy[k] = v
	}
	return copy
}

func (w *FlipkartWarehouseVectorClock) mapsEqual(map1, map2 map[string]int) bool {
	if len(map1) != len(map2) {
		return false
	}
	for k, v := range map1 {
		if map2[k] != v {
			return false
		}
	}
	return true
}

func (w *FlipkartWarehouseVectorClock) GetEventLog() []OrderEvent {
	w.mutex.RLock()
	defer w.mutex.RUnlock()
	
	events := make([]OrderEvent, len(w.eventLog))
	copy(events, w.eventLog)
	return events
}

// MumbaiEcommerceNetwork manages the entire network
type MumbaiEcommerceNetwork struct {
	warehouses map[string]*FlipkartWarehouseVectorClock
}

// NewMumbaiEcommerceNetwork creates a new e-commerce network
func NewMumbaiEcommerceNetwork() *MumbaiEcommerceNetwork {
	warehouseIDs := []string{"MUMBAI_ANDHERI", "MUMBAI_BANDRA", "MUMBAI_THANE"}
	warehouses := make(map[string]*FlipkartWarehouseVectorClock)
	
	for _, id := range warehouseIDs {
		warehouses[id] = NewFlipkartWarehouseVectorClock(id, warehouseIDs)
	}
	
	return &MumbaiEcommerceNetwork{warehouses: warehouses}
}

// SimulateBigBillionDays simulates Flipkart's Big Billion Days
func (network *MumbaiEcommerceNetwork) SimulateBigBillionDays() {
	fmt.Println("🛒 Flipkart Big Billion Days Simulation")
	fmt.Println("Mumbai Warehouses Coordination with Vector Clocks")
	fmt.Println(strings.Repeat("=", 60))
	
	// Event 1: Customer places order for iPhone (Andheri warehouse)
	event1 := network.warehouses["MUMBAI_ANDHERI"].ProcessLocalEvent(
		"ORD_12345", "ORDER_PLACED", "IPHONE_15", "CUST_67890", 1)
	
	// Event 2: Inventory check in Bandra warehouse
	event2 := network.warehouses["MUMBAI_BANDRA"].ProcessLocalEvent(
		"ORD_12346", "INVENTORY_CHECK", "SAMSUNG_S24", "CUST_11111", 1)
	
	// Event 3: Stock update in Thane warehouse
	event3 := network.warehouses["MUMBAI_THANE"].ProcessLocalEvent(
		"ORD_12347", "STOCK_UPDATE", "ONEPLUS_12", "CUST_22222", 5)
	
	// Inter-warehouse communication
	fmt.Println("\n🔄 Inter-warehouse Communication:")
	network.warehouses["MUMBAI_BANDRA"].ReceiveRemoteEvent(event1)
	network.warehouses["MUMBAI_THANE"].ReceiveRemoteEvent(event2)
	network.warehouses["MUMBAI_ANDHERI"].ReceiveRemoteEvent(event3)
	
	// Event 4: Order fulfillment after receiving updates
	event4 := network.warehouses["MUMBAI_ANDHERI"].ProcessLocalEvent(
		"ORD_12345", "ORDER_SHIPPED", "IPHONE_15", "CUST_67890", 1)
	
	// Event 5: Concurrent inventory restock
	event5 := network.warehouses["MUMBAI_BANDRA"].ProcessLocalEvent(
		"RESTOCK_001", "INVENTORY_RESTOCK", "SAMSUNG_S24", "SUPPLIER_ABC", 50)
	
	// Analyze event relationships
	network.analyzeCausalRelationships([]OrderEvent{event1, event2, event3, event4, event5})
}

func (network *MumbaiEcommerceNetwork) analyzeCausalRelationships(events []OrderEvent) {
	fmt.Println("\n🔍 Event Causal Relationship Analysis:")
	fmt.Println(strings.Repeat("-", 50))
	
	analyzer := network.warehouses["MUMBAI_ANDHERI"]
	
	for i := 0; i < len(events); i++ {
		for j := i + 1; j < len(events); j++ {
			relationship := analyzer.CompareEvents(events[i], events[j])
			fmt.Printf("Event %d vs Event %d: %s\n", i+1, j+1, relationship)
		}
	}
	
	// Find concurrent events
	fmt.Println("\n⏱️ Concurrent Events (No Causal Relationship):")
	for i := 0; i < len(events); i++ {
		for j := i + 1; j < len(events); j++ {
			if analyzer.CompareEvents(events[i], events[j]) == "CONCURRENT" {
				fmt.Printf("  • Event %d (%s) || Event %d (%s)\n", 
					i+1, events[i].EventType, j+1, events[j].EventType)
			}
		}
	}
}

// SimulateZomatoDelivery simulates Zomato food delivery coordination
func SimulateZomatoDelivery() {
	fmt.Println("\n" + strings.Repeat("=", 60))
	fmt.Println("🍕 Production Example: Zomato Food Delivery Coordination")
	fmt.Println("Multiple delivery hubs coordinating orders with vector clocks")
	fmt.Println(strings.Repeat("=", 60))
	
	hubIDs := []string{"HUB_BANDRA", "HUB_ANDHERI", "HUB_POWAI"}
	hubs := make(map[string]*FlipkartWarehouseVectorClock)
	
	for _, id := range hubIDs {
		hubs[id] = NewFlipkartWarehouseVectorClock(id, hubIDs)
	}
	
	// Order coordination scenario
	fmt.Println("\n📱 Food Order #ZOM98765 Coordination:")
	
	// Event 1: Customer places order (Bandra hub)
	orderEvent := hubs["HUB_BANDRA"].ProcessLocalEvent(
		"ZOM_98765", "ORDER_RECEIVED", "PIZZA_MARGHERITA", "FOODIE_123", 2)
	
	// Event 2: Restaurant confirmation (Andheri hub gets notification)
	hubs["HUB_ANDHERI"].ReceiveRemoteEvent(orderEvent)
	restaurantEvent := hubs["HUB_ANDHERI"].ProcessLocalEvent(
		"ZOM_98765", "RESTAURANT_CONFIRMED", "PIZZA_MARGHERITA", "RESTAURANT_456", 2)
	
	// Event 3: Delivery partner assignment (Powai hub)
	hubs["HUB_POWAI"].ReceiveRemoteEvent(restaurantEvent)
	assignmentEvent := hubs["HUB_POWAI"].ProcessLocalEvent(
		"ZOM_98765", "PARTNER_ASSIGNED", "DELIVERY_ROUTE", "PARTNER_789", 1)
	
	// Event 4: Food pickup (back to Bandra hub)
	hubs["HUB_BANDRA"].ReceiveRemoteEvent(assignmentEvent)
	pickupEvent := hubs["HUB_BANDRA"].ProcessLocalEvent(
		"ZOM_98765", "FOOD_PICKED_UP", "PIZZA_MARGHERITA", "PARTNER_789", 2)
	
	// Event 5: Food delivered
	deliveryEvent := hubs["HUB_BANDRA"].ProcessLocalEvent(
		"ZOM_98765", "FOOD_DELIVERED", "PIZZA_MARGHERITA", "FOODIE_123", 2)
	
	// Analyze delivery workflow causality
	fmt.Println("\n🔗 Food Delivery Causality Analysis:")
	analyzer := hubs["HUB_BANDRA"]
	fmt.Printf("Order → Restaurant Confirmation: %s\n", 
		analyzer.CompareEvents(orderEvent, restaurantEvent))
	fmt.Printf("Restaurant → Partner Assignment: %s\n", 
		analyzer.CompareEvents(restaurantEvent, assignmentEvent))
	fmt.Printf("Assignment → Pickup: %s\n", 
		analyzer.CompareEvents(assignmentEvent, pickupEvent))
	fmt.Printf("Pickup → Delivery: %s\n", 
		analyzer.CompareEvents(pickupEvent, deliveryEvent))
	
	fmt.Println("\n📊 Final Vector Clock States:")
	for hubID, hub := range hubs {
		fmt.Printf("%s: %v\n", hubID, hub.clock)
	}
}

func main() {
	// Mumbai E-commerce Network Simulation
	network := NewMumbaiEcommerceNetwork()
	network.SimulateBigBillionDays()
	
	// Zomato delivery coordination example
	SimulateZomatoDelivery()
	
	fmt.Println("\n✅ Mumbai E-commerce Vector Clock Simulation Complete!")
	fmt.Println("💡 Key Learning: Vector clocks enable precise event ordering")
	fmt.Println("   in distributed systems without synchronized physical clocks")
}

// Helper function for string repetition
func strings.Repeat(s string, count int) string {
	if count <= 0 {
		return ""
	}
	result := make([]byte, 0, len(s)*count)
	for i := 0; i < count; i++ {
		result = append(result, s...)
	}
	return string(result)
}
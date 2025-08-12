package main

/*
Basic Event Publisher/Subscriber Pattern - Go Implementation
उदाहरण: Zomato के food delivery events को handle करना

Setup:
go mod init basic-pubsub
go get github.com/google/uuid

Indian Context: Jab Zomato par order place karta hai,
multiple services को notification जाना चाहिए:
- Restaurant service (order notification)
- Delivery service (delivery partner assignment)
- Customer service (order tracking)
- Payment service (payment processing)
*/

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"sync"
	"time"

	"github.com/google/uuid"
)

// Event structure - har event ka basic format
type Event struct {
	EventID   string                 `json:"event_id"`
	EventType string                 `json:"event_type"`
	Data      map[string]interface{} `json:"data"`
	Timestamp string                 `json:"timestamp"`
	Source    string                 `json:"source"`
	Version   string                 `json:"version"`
}

// Handler function type - event ko process karne ke liye
type EventHandler func(ctx context.Context, event Event) error

// EventBus - Mumbai local train ki tarah, har station par log chadhte/utarte hain
type EventBus struct {
	subscribers map[string][]EventHandler // Event type ke liye handlers
	eventStore  []Event                   // Event history ke liye
	mutex       sync.RWMutex              // Concurrent access ke liye
}

// NewEventBus - event bus initialize karna
func NewEventBus() *EventBus {
	return &EventBus{
		subscribers: make(map[string][]EventHandler),
		eventStore:  make([]Event, 0),
	}
}

// Subscribe - event type ke liye handler register karna
// Jaise newspaper subscription - specific category ke liye
func (eb *EventBus) Subscribe(eventType string, handler EventHandler) {
	eb.mutex.Lock()
	defer eb.mutex.Unlock()

	eb.subscribers[eventType] = append(eb.subscribers[eventType], handler)
	log.Printf("Handler registered for event_type: %s", eventType)
}

// Publish - event ko sabko broadcast karna
// Railway announcement ki tarah - sabko sunai deta hai
func (eb *EventBus) Publish(ctx context.Context, event Event) error {
	eb.mutex.Lock()
	// Event store mein save karna - debugging ke liye
	eb.eventStore = append(eb.eventStore, event)
	handlers := eb.subscribers[event.EventType]
	eb.mutex.Unlock()

	log.Printf("📢 Publishing event: %s - ID: %s", event.EventType, event.EventID)

	// Agar koi subscriber hai toh
	if len(handlers) > 0 {
		var wg sync.WaitGroup
		
		// Saare handlers ko parallel execute karna
		for i, handler := range handlers {
			wg.Add(1)
			go func(handlerIndex int, h EventHandler) {
				defer wg.Done()
				
				if err := h(ctx, event); err != nil {
					log.Printf("❌ Handler %d failed for event %s: %v", 
						handlerIndex, event.EventID, err)
				}
			}(i, handler)
		}
		
		// Saare handlers complete hone ka wait karna
		wg.Wait()
	}

	return nil
}

// GetEvents - debug ke liye event history dekhna
func (eb *EventBus) GetEvents(eventType string) []Event {
	eb.mutex.RLock()
	defer eb.mutex.RUnlock()

	if eventType == "" {
		return eb.eventStore
	}

	var filteredEvents []Event
	for _, event := range eb.eventStore {
		if event.EventType == eventType {
			filteredEvents = append(filteredEvents, event)
		}
	}
	return filteredEvents
}

// ZomatoOrderService - food ordering service
type ZomatoOrderService struct {
	eventBus *EventBus
}

// NewZomatoOrderService - service initialize karna
func NewZomatoOrderService(eventBus *EventBus) *ZomatoOrderService {
	return &ZomatoOrderService{eventBus: eventBus}
}

// PlaceOrder - order place karna
func (zos *ZomatoOrderService) PlaceOrder(ctx context.Context, customerID string, 
	restaurantID string, items []map[string]interface{}, totalAmount float64) (string, error) {
	
	orderID := fmt.Sprintf("ZOM-%s", uuid.New().String()[:8])

	// Order data prepare karna
	orderData := map[string]interface{}{
		"order_id":      orderID,
		"customer_id":   customerID,
		"restaurant_id": restaurantID,
		"items":         items,
		"total_amount":  totalAmount,
		"currency":      "INR",
		"delivery_area": "Bandra West, Mumbai",
		"order_time":    time.Now().Format(time.RFC3339),
	}

	// Order placed event create karna
	event := Event{
		EventID:   uuid.New().String(),
		EventType: "order.placed",
		Data:      orderData,
		Timestamp: time.Now().Format(time.RFC3339),
		Source:    "zomato.order.service",
		Version:   "1.0",
	}

	// Event publish karna
	err := zos.eventBus.Publish(ctx, event)
	if err != nil {
		return "", fmt.Errorf("failed to publish order event: %w", err)
	}

	return orderID, nil
}

// RestaurantService - restaurant notifications handle karna
type RestaurantService struct {
	name string
}

func NewRestaurantService() *RestaurantService {
	return &RestaurantService{name: "Restaurant Service"}
}

func (rs *RestaurantService) HandleOrderPlaced(ctx context.Context, event Event) error {
	orderData := event.Data
	orderID := orderData["order_id"].(string)
	restaurantID := orderData["restaurant_id"].(string)

	log.Printf("🍽️ %s: New order received for restaurant %s", rs.name, restaurantID)
	log.Printf("   📋 Order ID: %s", orderID)

	// Restaurant ko notification send karna - items ki details
	if items, ok := orderData["items"].([]map[string]interface{}); ok {
		for _, item := range items {
			log.Printf("   🍛 Item: %s x %v", item["name"], item["quantity"])
		}
	}

	// Restaurant acceptance simulation
	time.Sleep(200 * time.Millisecond)

	// Random restaurant response
	accepted := rand.Float32() > 0.1 // 90% acceptance rate
	if accepted {
		log.Printf("✅ Restaurant accepted order %s", orderID)
	} else {
		log.Printf("❌ Restaurant rejected order %s", orderID)
	}

	return nil
}

// DeliveryService - delivery partner assignment
type DeliveryService struct {
	name string
}

func NewDeliveryService() *DeliveryService {
	return &DeliveryService{name: "Delivery Service"}
}

func (ds *DeliveryService) HandleOrderPlaced(ctx context.Context, event Event) error {
	orderData := event.Data
	orderID := orderData["order_id"].(string)
	deliveryArea := orderData["delivery_area"].(string)

	log.Printf("🏍️ %s: Finding delivery partner for order %s", ds.name, orderID)
	log.Printf("   📍 Delivery area: %s", deliveryArea)

	// Delivery partner search simulation
	time.Sleep(300 * time.Millisecond)

	// Random delivery partner assignment
	partners := []string{"Ravi Sharma", "Suresh Patil", "Amit Kumar", "Rajesh Singh"}
	selectedPartner := partners[rand.Intn(len(partners))]

	log.Printf("✅ Delivery partner assigned: %s for order %s", selectedPartner, orderID)

	return nil
}

// CustomerNotificationService - customer ko updates
type CustomerNotificationService struct {
	name string
}

func NewCustomerNotificationService() *CustomerNotificationService {
	return &CustomerNotificationService{name: "Customer Notification"}
}

func (cns *CustomerNotificationService) HandleOrderPlaced(ctx context.Context, event Event) error {
	orderData := event.Data
	orderID := orderData["order_id"].(string)
	customerID := orderData["customer_id"].(string)

	log.Printf("📱 %s: Sending confirmation to customer %s", cns.name, customerID)
	log.Printf("   🛍️ Order: %s", orderID)

	// Customer notification simulation - SMS/Push/Email
	time.Sleep(100 * time.Millisecond)

	log.Printf("✅ Order confirmation sent to customer %s", customerID)

	return nil
}

// PaymentService - payment processing
type PaymentService struct {
	name string
}

func NewPaymentService() *PaymentService {
	return &PaymentService{name: "Payment Service"}
}

func (ps *PaymentService) HandleOrderPlaced(ctx context.Context, event Event) error {
	orderData := event.Data
	orderID := orderData["order_id"].(string)
	amount := orderData["total_amount"].(float64)

	log.Printf("💳 %s: Processing payment for order %s", ps.name, orderID)
	log.Printf("   💰 Amount: ₹%.2f", amount)

	// Payment processing simulation - UPI/Card
	time.Sleep(500 * time.Millisecond)

	// Random payment success (95% success rate)
	success := rand.Float32() > 0.05
	if success {
		txnID := fmt.Sprintf("TXN%s", uuid.New().String()[:8])
		log.Printf("✅ Payment successful: %s for order %s", txnID, orderID)
	} else {
		log.Printf("❌ Payment failed for order %s", orderID)
	}

	return nil
}

func main() {
	fmt.Println("🍕 Zomato Event-Driven Food Delivery Demo")
	fmt.Println(strings.Repeat("=", 50))

	// Event bus initialize karna
	eventBus := NewEventBus()

	// Services initialize karna
	orderService := NewZomatoOrderService(eventBus)
	restaurantService := NewRestaurantService()
	deliveryService := NewDeliveryService()
	customerService := NewCustomerNotificationService()
	paymentService := NewPaymentService()

	// Event handlers register karna
	eventBus.Subscribe("order.placed", restaurantService.HandleOrderPlaced)
	eventBus.Subscribe("order.placed", deliveryService.HandleOrderPlaced)
	eventBus.Subscribe("order.placed", customerService.HandleOrderPlaced)
	eventBus.Subscribe("order.placed", paymentService.HandleOrderPlaced)

	// Sample food items
	items := []map[string]interface{}{
		{"name": "Butter Chicken", "quantity": 2, "price": 350.0},
		{"name": "Garlic Naan", "quantity": 4, "price": 60.0},
		{"name": "Basmati Rice", "quantity": 1, "price": 180.0},
	}

	// Context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Order place karna
	orderID, err := orderService.PlaceOrder(
		ctx,
		"CUST456",
		"REST789",
		items,
		830.0, // Total amount
	)

	if err != nil {
		log.Fatalf("Failed to place order: %v", err)
	}

	fmt.Printf("\n🎉 Order placed successfully: %s\n", orderID)

	// Processing complete hone ke liye wait karna
	time.Sleep(2 * time.Second)

	// Event statistics
	allEvents := eventBus.GetEvents("")
	orderEvents := eventBus.GetEvents("order.placed")

	fmt.Printf("\n📊 Total events processed: %d\n", len(allEvents))
	fmt.Printf("🛍️ Order events: %d\n", len(orderEvents))

	// Event details show karna
	if len(orderEvents) > 0 {
		eventJSON, _ := json.MarshalIndent(orderEvents[0], "", "  ")
		fmt.Printf("\n📄 Sample event:\n%s\n", string(eventJSON))
	}
}
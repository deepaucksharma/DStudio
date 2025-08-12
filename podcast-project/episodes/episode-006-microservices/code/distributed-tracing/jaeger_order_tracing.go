package main

/*
Distributed Tracing with Jaeger for Order Processing
Complete order flow tracing across multiple microservices

जैसे Mumbai local train की पूरी journey को track करते हैं हर station पर,
वैसे ही distributed tracing में request की पूरी journey track करते हैं
*/

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"math/rand"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/opentracing/opentracing-go"
	"github.com/opentracing/opentracing-go/ext"
	jaeger "github.com/uber/jaeger-client-go"
	jaegercfg "github.com/uber/jaeger-client-go/config"
	"github.com/uber/jaeger-lib/metrics"
)

// Order represents a Flipkart-style order
type Order struct {
	OrderID      string    `json:"order_id"`
	UserID       string    `json:"user_id"`
	Items        []Item    `json:"items"`
	TotalAmount  float64   `json:"total_amount"`
	Status       string    `json:"status"`
	CreatedAt    time.Time `json:"created_at"`
	DeliveryAddr string    `json:"delivery_address"`
}

type Item struct {
	ProductID string  `json:"product_id"`
	Name      string  `json:"name"`
	Price     float64 `json:"price"`
	Quantity  int     `json:"quantity"`
}

// Service responses
type ValidationResponse struct {
	Valid   bool   `json:"valid"`
	Message string `json:"message"`
}

type InventoryResponse struct {
	Available   bool `json:"available"`
	Reserved    bool `json:"reserved"`
	ReserveID   string `json:"reserve_id,omitempty"`
	Message     string `json:"message"`
}

type PaymentResponse struct {
	Success       bool   `json:"success"`
	TransactionID string `json:"transaction_id,omitempty"`
	Message       string `json:"message"`
}

type ShippingResponse struct {
	Shipped    bool   `json:"shipped"`
	TrackingID string `json:"tracking_id,omitempty"`
	EstimatedDelivery string `json:"estimated_delivery,omitempty"`
	Message    string `json:"message"`
}

// Initialize Jaeger tracer
func initJaeger(serviceName string) (opentracing.Tracer, io.Closer) {
	cfg := jaegercfg.Configuration{
		ServiceName: serviceName,
		Sampler: &jaegercfg.SamplerConfig{
			Type:  jaeger.SamplerTypeConst,
			Param: 1, // Sample 100% of requests (for demo)
		},
		Reporter: &jaegercfg.ReporterConfig{
			LogSpans:           true,
			LocalAgentHostPort: "localhost:6831",
		},
	}

	jLogger := jaeger.StdLogger
	jMetricsFactory := metrics.NullFactory

	tracer, closer, err := cfg.NewTracer(
		jaegercfg.Logger(jLogger),
		jaegercfg.Metrics(jMetricsFactory),
	)
	if err != nil {
		log.Fatal("Cannot initialize Jaeger tracer: ", err)
	}

	return tracer, closer
}

// API Gateway Service - Entry point like Mumbai CST station
func startAPIGateway() {
	tracer, closer := initJaeger("api-gateway")
	defer closer.Close()
	opentracing.SetGlobalTracer(tracer)

	r := gin.Default()

	// Middleware for tracing every request
	r.Use(func(c *gin.Context) {
		// Start root span for incoming request
		span := tracer.StartSpan("api_gateway_request")
		defer span.Finish()

		// Add span to context
		ctx := opentracing.ContextWithSpan(c.Request.Context(), span)
		c.Request = c.Request.WithContext(ctx)

		// Add Mumbai-specific tags
		span.SetTag("mumbai.region", "west")
		span.SetTag("service.version", "1.0.0")
		span.SetTag("http.method", c.Request.Method)
		span.SetTag("http.url", c.Request.URL.String())
		span.SetTag("user.region", "mumbai")

		c.Next()

		// Set response status
		span.SetTag("http.status_code", c.Writer.Status())
	})

	r.POST("/api/orders", processOrderHandler)

	log.Println("🚂 API Gateway started on :8080 - Ready for Mumbai traffic!")
	log.Fatal(http.ListenAndServe(":8080", r))
}

// Order processing handler - Complete Flipkart order flow
func processOrderHandler(c *gin.Context) {
	span, ctx := opentracing.StartSpanFromContext(c.Request.Context(), "process_order")
	defer span.Finish()

	var order Order
	if err := c.ShouldBindJSON(&order); err != nil {
		span.SetTag("error", true)
		span.LogFields(
			opentracing.Log{Key: "event", Value: "error"},
			opentracing.Log{Key: "message", Value: err.Error()},
		)
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Generate order ID like Mumbai train number
	order.OrderID = fmt.Sprintf("MUM_%d_%d", time.Now().Unix(), rand.Intn(9999))
	order.CreatedAt = time.Now()
	order.Status = "processing"

	span.SetTag("order.id", order.OrderID)
	span.SetTag("order.user_id", order.UserID)
	span.SetTag("order.amount", order.TotalAmount)
	span.SetTag("order.items_count", len(order.Items))

	log.Printf("🛒 Processing order %s for user %s - Amount: ₹%.2f", 
		order.OrderID, order.UserID, order.TotalAmount)

	// Step 1: Validate Order - जैसे Mumbai local ticket validation
	if !validateOrder(ctx, order) {
		order.Status = "validation_failed"
		span.SetTag("order.status", "validation_failed")
		c.JSON(http.StatusBadRequest, gin.H{
			"order_id": order.OrderID,
			"status":   order.Status,
			"message":  "Order validation failed",
		})
		return
	}

	// Step 2: Check Inventory - जैसे seat availability check
	reserveID, available := checkInventory(ctx, order)
	if !available {
		order.Status = "inventory_unavailable"
		span.SetTag("order.status", "inventory_unavailable")
		c.JSON(http.StatusConflict, gin.H{
			"order_id": order.OrderID,
			"status":   order.Status,
			"message":  "Items not available in inventory",
		})
		return
	}

	span.SetTag("inventory.reserve_id", reserveID)

	// Step 3: Process Payment - जैसे UPI payment
	transactionID, paymentSuccess := processPayment(ctx, order)
	if !paymentSuccess {
		// Release inventory reservation
		releaseInventory(ctx, reserveID)
		order.Status = "payment_failed"
		span.SetTag("order.status", "payment_failed")
		c.JSON(http.StatusPaymentRequired, gin.H{
			"order_id": order.OrderID,
			"status":   order.Status,
			"message":  "Payment processing failed",
		})
		return
	}

	span.SetTag("payment.transaction_id", transactionID)

	// Step 4: Ship Order - जैसे Mumbai delivery network
	trackingID, shipped := shipOrder(ctx, order)
	if !shipped {
		// In real scenario, would initiate refund process
		order.Status = "shipping_failed"
		span.SetTag("order.status", "shipping_failed")
		c.JSON(http.StatusInternalServerError, gin.H{
			"order_id": order.OrderID,
			"status":   order.Status,
			"message":  "Shipping failed - refund will be processed",
		})
		return
	}

	// Success!
	order.Status = "shipped"
	span.SetTag("order.status", "shipped")
	span.SetTag("shipping.tracking_id", trackingID)

	// Add Mumbai-specific success metrics
	span.SetTag("success", true)
	span.SetTag("processing.duration_ms", time.Since(order.CreatedAt).Milliseconds())
	span.LogFields(
		opentracing.Log{Key: "event", Value: "order_completed"},
		opentracing.Log{Key: "message", Value: "Order processed successfully like Mumbai Dabbawalas!"},
	)

	log.Printf("✅ Order %s completed successfully - Tracking: %s", order.OrderID, trackingID)

	c.JSON(http.StatusOK, gin.H{
		"order_id":       order.OrderID,
		"status":         order.Status,
		"transaction_id": transactionID,
		"tracking_id":    trackingID,
		"message":        "Order placed successfully! Mumbai delivery network activated 🚚",
	})
}

// Step 1: Order Validation Service
func validateOrder(ctx context.Context, order Order) bool {
	span, _ := opentracing.StartSpanFromContext(ctx, "validate_order")
	defer span.Finish()

	// Add validation-specific tags
	span.SetTag("service.name", "order-validation")
	span.SetTag("validation.items_count", len(order.Items))
	span.SetTag("validation.amount", order.TotalAmount)

	// Simulate validation logic
	time.Sleep(time.Duration(50+rand.Intn(100)) * time.Millisecond)

	// Mumbai-specific business rules
	if order.TotalAmount <= 0 {
		span.SetTag("error", true)
		span.LogFields(
			opentracing.Log{Key: "event", Value: "validation_error"},
			opentracing.Log{Key: "message", Value: "Invalid order amount"},
		)
		return false
	}

	if len(order.Items) == 0 {
		span.SetTag("error", true)
		span.LogFields(
			opentracing.Log{Key: "event", Value: "validation_error"},
			opentracing.Log{Key: "message", Value: "No items in order"},
		)
		return false
	}

	// Check delivery address for Mumbai coverage
	if order.DeliveryAddr == "" {
		span.SetTag("error", true)
		span.LogFields(
			opentracing.Log{Key: "event", Value: "validation_error"},
			opentracing.Log{Key: "message", Value: "Missing delivery address"},
		)
		return false
	}

	// Simulate occasional validation failures (5%)
	if rand.Intn(100) < 5 {
		span.SetTag("error", true)
		span.LogFields(
			opentracing.Log{Key: "event", Value: "validation_error"},
			opentracing.Log{Key: "message", Value: "Random validation failure for demo"},
		)
		return false
	}

	span.SetTag("validation.result", "success")
	span.LogFields(
		opentracing.Log{Key: "event", Value: "validation_success"},
		opentracing.Log{Key: "message", Value: "Order validation passed - ready for Mumbai processing"},
	)

	return true
}

// Step 2: Inventory Service - जैसे warehouse stock check
func checkInventory(ctx context.Context, order Order) (string, bool) {
	span, _ := opentracing.StartSpanFromContext(ctx, "check_inventory")
	defer span.Finish()

	span.SetTag("service.name", "inventory-service")
	span.SetTag("inventory.warehouse", "mumbai-west")

	// Simulate database/inventory check
	time.Sleep(time.Duration(100+rand.Intn(200)) * time.Millisecond)

	reserveID := fmt.Sprintf("RES_%s_%d", order.OrderID, rand.Intn(9999))

	// Check each item availability
	totalItemsToReserve := 0
	for _, item := range order.Items {
		childSpan := opentracing.StartSpan(
			"check_item_availability",
			opentracing.ChildOf(span.Context()),
		)
		
		childSpan.SetTag("item.product_id", item.ProductID)
		childSpan.SetTag("item.quantity", item.Quantity)
		childSpan.SetTag("item.name", item.Name)

		// Simulate stock check (95% items are available)
		available := rand.Intn(100) < 95
		
		if available {
			totalItemsToReserve += item.Quantity
			childSpan.SetTag("item.available", true)
			childSpan.LogFields(
				opentracing.Log{Key: "event", Value: "item_available"},
				opentracing.Log{Key: "message", Value: fmt.Sprintf("Reserved %d units of %s", item.Quantity, item.Name)},
			)
		} else {
			childSpan.SetTag("item.available", false)
			childSpan.SetTag("error", true)
			childSpan.LogFields(
				opentracing.Log{Key: "event", Value: "item_unavailable"},
				opentracing.Log{Key: "message", Value: fmt.Sprintf("Item %s out of stock", item.Name)},
			)
			childSpan.Finish()
			
			span.SetTag("inventory.result", "unavailable")
			return "", false
		}
		
		childSpan.Finish()
	}

	span.SetTag("inventory.reserve_id", reserveID)
	span.SetTag("inventory.total_items", totalItemsToReserve)
	span.SetTag("inventory.result", "reserved")
	span.LogFields(
		opentracing.Log{Key: "event", Value: "inventory_reserved"},
		opentracing.Log{Key: "message", Value: fmt.Sprintf("Reserved %d items from Mumbai warehouse", totalItemsToReserve)},
	)

	return reserveID, true
}

// Step 3: Payment Service - जैसे Paytm/PhonePe payment
func processPayment(ctx context.Context, order Order) (string, bool) {
	span, _ := opentracing.StartSpanFromContext(ctx, "process_payment")
	defer span.Finish()

	span.SetTag("service.name", "payment-service")
	span.SetTag("payment.amount", order.TotalAmount)
	span.SetTag("payment.currency", "INR")
	span.SetTag("payment.method", "UPI") // Most popular in Mumbai

	// Simulate payment processing time
	time.Sleep(time.Duration(200+rand.Intn(800)) * time.Millisecond)

	transactionID := fmt.Sprintf("TXN_%s_%d", order.OrderID, rand.Intn(999999))

	// Simulate payment gateway interaction
	gatewaySpan := opentracing.StartSpan(
		"payment_gateway_call",
		opentracing.ChildOf(span.Context()),
	)
	gatewaySpan.SetTag("gateway.provider", "razorpay")
	gatewaySpan.SetTag("gateway.method", "upi")

	// Simulate gateway processing
	time.Sleep(time.Duration(300+rand.Intn(500)) * time.Millisecond)

	// Simulate payment failure (8% failure rate)
	success := rand.Intn(100) >= 8

	if success {
		gatewaySpan.SetTag("gateway.status", "success")
		gatewaySpan.LogFields(
			opentracing.Log{Key: "event", Value: "payment_success"},
			opentracing.Log{Key: "message", Value: "UPI payment successful"},
		)
		
		span.SetTag("payment.transaction_id", transactionID)
		span.SetTag("payment.status", "success")
		span.LogFields(
			opentracing.Log{Key: "event", Value: "payment_completed"},
			opentracing.Log{Key: "message", Value: fmt.Sprintf("Payment of ₹%.2f successful - Mumbai digital transaction!", order.TotalAmount)},
		)
	} else {
		gatewaySpan.SetTag("gateway.status", "failed")
		gatewaySpan.SetTag("error", true)
		gatewaySpan.LogFields(
			opentracing.Log{Key: "event", Value: "payment_failure"},
			opentracing.Log{Key: "message", Value: "UPI payment failed - insufficient balance or network issue"},
		)
		
		span.SetTag("payment.status", "failed")
		span.SetTag("error", true)
		span.LogFields(
			opentracing.Log{Key: "event", Value: "payment_failed"},
			opentracing.Log{Key: "message", Value: "Payment processing failed"},
		)
	}

	gatewaySpan.Finish()

	return transactionID, success
}

// Step 4: Shipping Service - जैसे Mumbai delivery network
func shipOrder(ctx context.Context, order Order) (string, bool) {
	span, _ := opentracing.StartSpanFromContext(ctx, "ship_order")
	defer span.Finish()

	span.SetTag("service.name", "shipping-service")
	span.SetTag("shipping.destination", order.DeliveryAddr)
	span.SetTag("shipping.carrier", "mumbai-express-delivery")

	// Simulate shipping preparation
	time.Sleep(time.Duration(150+rand.Intn(300)) * time.Millisecond)

	trackingID := fmt.Sprintf("TRACK_%s_%d", order.OrderID, rand.Intn(999999))

	// Shipping allocation sub-process
	allocationSpan := opentracing.StartSpan(
		"shipping_allocation",
		opentracing.ChildOf(span.Context()),
	)
	allocationSpan.SetTag("allocation.zone", "mumbai-west")
	allocationSpan.SetTag("allocation.delivery_partner", "mumbai-dabbawalas")

	// Simulate delivery partner assignment
	time.Sleep(time.Duration(100+rand.Intn(200)) * time.Millisecond)

	// Simulate occasional shipping failures (3%)
	success := rand.Intn(100) >= 3

	if success {
		estimatedDelivery := time.Now().Add(48 * time.Hour).Format("2006-01-02 15:04")
		
		allocationSpan.SetTag("allocation.partner_id", "PARTNER_MUM_001")
		allocationSpan.SetTag("allocation.estimated_delivery", estimatedDelivery)
		allocationSpan.LogFields(
			opentracing.Log{Key: "event", Value: "partner_assigned"},
			opentracing.Log{Key: "message", Value: "Delivery partner assigned - Mumbai Dabbawalas network activated"},
		)
		
		span.SetTag("shipping.tracking_id", trackingID)
		span.SetTag("shipping.status", "shipped")
		span.SetTag("shipping.estimated_delivery", estimatedDelivery)
		span.LogFields(
			opentracing.Log{Key: "event", Value: "order_shipped"},
			opentracing.Log{Key: "message", Value: "Order shipped via Mumbai delivery network - efficient as Dabbawalas!"},
		)
	} else {
		allocationSpan.SetTag("allocation.status", "failed")
		allocationSpan.SetTag("error", true)
		allocationSpan.LogFields(
			opentracing.Log{Key: "event", Value: "allocation_failed"},
			opentracing.Log{Key: "message", Value: "No delivery partners available in Mumbai zone"},
		)
		
		span.SetTag("shipping.status", "failed")
		span.SetTag("error", true)
		span.LogFields(
			opentracing.Log{Key: "event", Value: "shipping_failed"},
			opentracing.Log{Key: "message", Value: "Shipping allocation failed"},
		)
	}

	allocationSpan.Finish()

	return trackingID, success
}

// Helper function to release inventory reservation
func releaseInventory(ctx context.Context, reserveID string) {
	span, _ := opentracing.StartSpanFromContext(ctx, "release_inventory")
	defer span.Finish()

	span.SetTag("service.name", "inventory-service")
	span.SetTag("operation", "release_reservation")
	span.SetTag("reserve_id", reserveID)

	time.Sleep(time.Duration(50+rand.Intn(100)) * time.Millisecond)

	span.LogFields(
		opentracing.Log{Key: "event", Value: "reservation_released"},
		opentracing.Log{Key: "message", Value: "Inventory reservation released due to payment failure"},
	)
}

// Health check endpoint with tracing
func healthCheckHandler(c *gin.Context) {
	span := opentracing.StartSpan("health_check")
	defer span.Finish()

	span.SetTag("service.name", "api-gateway")
	span.SetTag("health.status", "healthy")
	span.SetTag("mumbai.datacenter", "operational")

	c.JSON(http.StatusOK, gin.H{
		"status":    "healthy",
		"service":   "mumbai-ecommerce-api",
		"timestamp": time.Now().Format(time.RFC3339),
		"message":   "Service running smoothly like Mumbai local trains! 🚂",
	})
}

func main() {
	// Seed random number generator
	rand.Seed(time.Now().UnixNano())

	fmt.Println("🚂 Starting Mumbai E-commerce Distributed Tracing Demo")
	fmt.Println("Services: API Gateway → Order Validation → Inventory → Payment → Shipping")
	fmt.Println("Jaeger UI: http://localhost:16686")
	fmt.Println("API Endpoint: POST http://localhost:8080/api/orders")
	fmt.Println()
	fmt.Println("Sample request:")
	fmt.Println(`curl -X POST http://localhost:8080/api/orders -H "Content-Type: application/json" -d '{
  "user_id": "user_mumbai_123",
  "items": [
    {"product_id": "phone_001", "name": "OnePlus 12", "price": 65999, "quantity": 1},
    {"product_id": "case_001", "name": "Phone Case", "price": 1299, "quantity": 1}
  ],
  "total_amount": 67298,
  "delivery_address": "Flat 3B, Dadar East, Mumbai 400014"
}'`)
	fmt.Println()

	// Start the API Gateway
	startAPIGateway()
}

/*
To run this example:

1. Start Jaeger:
   docker run -d --name jaeger \
     -p 16686:16686 \
     -p 6831:6831/udp \
     jaegertracing/all-in-one:latest

2. Install dependencies:
   go mod init mumbai-tracing
   go get github.com/gin-gonic/gin
   go get github.com/opentracing/opentracing-go
   go get github.com/uber/jaeger-client-go
   go get github.com/uber/jaeger-lib/metrics

3. Run the service:
   go run jaeger_order_tracing.go

4. Make requests and view traces at:
   http://localhost:16686

This demonstrates:
- Complete order flow tracing across multiple services
- Mumbai-specific business logic and context
- Error scenarios and their traces
- Parent-child span relationships
- Custom tags and logs for debugging
- Production-ready distributed tracing patterns
*/
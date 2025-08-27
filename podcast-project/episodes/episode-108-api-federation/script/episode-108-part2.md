# Episode 108: API Federation - Part 2
## Advanced Federation Patterns aur Production Scale

---

### Episode Continuation: Mumbai ke Local Train Network jaisa Complex API Federation

Namaste doston! Episode 108 ka Part 2 mein hum dekhenge ki kaise production-grade API Federation systems banate hain. Part 1 mein humne GraphQL Federation ki basics dekhi thi, ab hum advanced patterns, security, aur real-world implementations par focus karenge.

Mumbai ki local trains ko dekho - different lines (Central, Western, Harbour) independently operate karte hain, lekin passengers ko seamless journey milta hai. Exactly yahi concept hai API Federation ka - multiple independent services ko ek unified interface ke through expose karna.

---

## Section 4: Microservices Federation Patterns (2,000 words)

### Service Mesh Integration with Federation

Modern microservices architecture mein service mesh ek backbone ban gaya hai. Jaise Mumbai mein BEST buses aur local trains dono separate systems hain lekin connected hain, waise hi federation aur service mesh ka integration hota hai.

Istio ya Linkerd jaisi service mesh technologies federation ke saath kaise integrate hoti hain, ye dekhte hain:

```javascript
// Service Mesh Federation Gateway - Node.js
const express = require('express');
const { buildFederatedSchema } = require('@apollo/federation');
const { ApolloServer } = require('apollo-server-express');

class ServiceMeshFederationGateway {
    constructor() {
        this.services = new Map();
        this.app = express();
        this.healthMetrics = {
            totalRequests: 0,
            failedRequests: 0,
            averageLatency: 0
        };
    }

    // Service discovery with mesh integration
    async discoverServices() {
        const services = [
            {
                name: 'user-service',
                url: 'http://user-service.mesh:4001/graphql',
                health: await this.checkServiceHealth('user-service')
            },
            {
                name: 'booking-service', 
                url: 'http://booking-service.mesh:4002/graphql',
                health: await this.checkServiceHealth('booking-service')
            },
            {
                name: 'payment-service',
                url: 'http://payment-service.mesh:4003/graphql', 
                health: await this.checkServiceHealth('payment-service')
            }
        ];

        services.forEach(service => {
            if (service.health.status === 'healthy') {
                this.services.set(service.name, service);
            }
        });

        console.log(`Discovered ${this.services.size} healthy services`);
        return services;
    }

    // Health check with circuit breaker pattern
    async checkServiceHealth(serviceName) {
        try {
            const startTime = Date.now();
            const response = await fetch(`http://${serviceName}.mesh:8080/health`);
            const latency = Date.now() - startTime;
            
            return {
                status: response.ok ? 'healthy' : 'unhealthy',
                latency: latency,
                timestamp: new Date()
            };
        } catch (error) {
            console.error(`Health check failed for ${serviceName}:`, error.message);
            return {
                status: 'unhealthy',
                error: error.message,
                timestamp: new Date()
            };
        }
    }

    // Federation schema builder with mesh integration
    async buildFederatedSchema() {
        const serviceSchemas = [];
        
        for (const [name, service] of this.services) {
            try {
                const schema = await this.fetchServiceSchema(service.url);
                serviceSchemas.push({
                    name: name,
                    url: service.url,
                    schema: schema
                });
            } catch (error) {
                console.error(`Failed to fetch schema for ${name}:`, error);
            }
        }

        return buildFederatedSchema(serviceSchemas);
    }

    async fetchServiceSchema(url) {
        const introspectionQuery = `
            query IntrospectionQuery {
                __schema {
                    types {
                        name
                        kind
                        fields {
                            name
                            type {
                                name
                                kind
                            }
                        }
                    }
                }
            }
        `;

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: introspectionQuery })
        });

        return await response.json();
    }
}

// Usage
const gateway = new ServiceMeshFederationGateway();
await gateway.discoverServices();
const federatedSchema = await gateway.buildFederatedSchema();
```

### BookMyShow ka Booking Federation Case Study

BookMyShow India ka largest entertainment ticketing platform hai with 65+ million monthly users. Unka federation architecture dekho:

**Architecture Overview:**
- Movie Service: 50,000+ movies/events catalog
- Venue Service: 6,000+ venues across 650+ cities  
- Booking Service: 15 million+ bookings per month
- Payment Service: ₹3,000+ crores annual GMV
- User Service: 65+ million registered users

**Federation Implementation:**

```java
// BookMyShow Federation Gateway - Java Spring Boot
@RestController
@RequestMapping("/api/federation")
public class BookMyShowFederationController {
    
    @Autowired
    private MovieService movieService;
    
    @Autowired 
    private VenueService venueService;
    
    @Autowired
    private BookingService bookingService;
    
    @Autowired
    private PaymentService paymentService;
    
    // Cross-service booking transaction
    @PostMapping("/book")
    @Transactional
    public ResponseEntity<BookingResponse> createBooking(
            @RequestBody BookingRequest request) {
        
        long startTime = System.currentTimeMillis();
        
        try {
            // Step 1: Validate movie and show
            MovieShow show = movieService.getShow(request.getShowId());
            if (show == null) {
                return ResponseEntity.badRequest()
                    .body(new BookingResponse("Invalid show ID"));
            }
            
            // Step 2: Check venue capacity
            Venue venue = venueService.getVenue(show.getVenueId());
            if (!venue.hasAvailableSeats(request.getSeatCount())) {
                return ResponseEntity.badRequest()
                    .body(new BookingResponse("Seats not available"));
            }
            
            // Step 3: Hold seats (with timeout)
            SeatHold seatHold = venueService.holdSeats(
                request.getShowId(), 
                request.getSeats(),
                Duration.ofMinutes(10) // 10 minute hold
            );
            
            // Step 4: Calculate pricing with dynamic pricing
            PricingResult pricing = calculateDynamicPricing(
                show, venue, request.getSeats()
            );
            
            // Step 5: Process payment
            PaymentResult payment = paymentService.processPayment(
                request.getUserId(),
                pricing.getTotalAmount(),
                request.getPaymentMethod()
            );
            
            if (!payment.isSuccessful()) {
                venueService.releaseSeats(seatHold.getHoldId());
                return ResponseEntity.badRequest()
                    .body(new BookingResponse("Payment failed"));
            }
            
            // Step 6: Confirm booking
            Booking booking = bookingService.createBooking(
                request.getUserId(),
                request.getShowId(),
                seatHold.getSeats(),
                payment.getTransactionId()
            );
            
            // Step 7: Release seat hold
            venueService.confirmSeats(seatHold.getHoldId());
            
            // Metrics collection
            long duration = System.currentTimeMillis() - startTime;
            metricsCollector.recordBookingLatency(duration);
            
            return ResponseEntity.ok(new BookingResponse(
                booking.getBookingId(),
                "Booking confirmed successfully",
                pricing.getTotalAmount()
            ));
            
        } catch (Exception e) {
            // Comprehensive error handling and rollback
            handleBookingFailure(request, e);
            return ResponseEntity.internalServerError()
                .body(new BookingResponse("Booking failed: " + e.getMessage()));
        }
    }
    
    // Dynamic pricing algorithm
    private PricingResult calculateDynamicPricing(
            MovieShow show, Venue venue, List<Seat> seats) {
        
        double basePrice = show.getBasePrice();
        double demandMultiplier = calculateDemandMultiplier(show);
        double venueMultiplier = venue.getPricingMultiplier();
        double timeMultiplier = calculateTimeBasedMultiplier(show);
        
        double finalPrice = basePrice * demandMultiplier * 
                           venueMultiplier * timeMultiplier;
        
        // Apply GST (18% in India)
        double gst = finalPrice * 0.18;
        double convenienceFee = Math.min(finalPrice * 0.02, 50.0); // Max ₹50
        
        return new PricingResult(
            basePrice,
            finalPrice + gst + convenienceFee,
            gst,
            convenienceFee,
            seats.size()
        );
    }
}
```

**Performance Metrics:**
- Average booking time: 2.3 seconds
- Success rate: 97.8%
- Peak capacity: 50,000 concurrent bookings
- Cost per transaction: ₹0.85

### Cross-Service Transactions with Saga Pattern

Distributed transactions mein consistency maintain karna Mumbai local train mein seat dhundne jaisa hai - coordination chahiye aur backup plan bhi.

```go
// Saga Pattern Implementation - Go
package main

import (
    "context"
    "fmt"
    "time"
    "encoding/json"
)

type SagaStep struct {
    Name        string
    Execute     func(ctx context.Context, data interface{}) error
    Compensate  func(ctx context.Context, data interface{}) error
}

type SagaOrchestrator struct {
    steps       []SagaStep
    executed    []int
    data        interface{}
    logger      Logger
}

func NewSagaOrchestrator(steps []SagaStep) *SagaOrchestrator {
    return &SagaOrchestrator{
        steps:    steps,
        executed: make([]int, 0),
        logger:   NewLogger("saga"),
    }
}

// Execute saga with compensation
func (s *SagaOrchestrator) Execute(ctx context.Context, data interface{}) error {
    s.data = data
    
    for i, step := range s.steps {
        s.logger.Info(fmt.Sprintf("Executing step: %s", step.Name))
        
        startTime := time.Now()
        err := step.Execute(ctx, data)
        duration := time.Since(startTime)
        
        if err != nil {
            s.logger.Error(fmt.Sprintf("Step %s failed: %v", step.Name, err))
            // Compensate all executed steps in reverse order
            return s.compensate(ctx)
        }
        
        s.executed = append(s.executed, i)
        s.logger.Info(fmt.Sprintf("Step %s completed in %v", step.Name, duration))
    }
    
    s.logger.Info("Saga completed successfully")
    return nil
}

func (s *SagaOrchestrator) compensate(ctx context.Context) error {
    s.logger.Info("Starting compensation")
    
    // Execute compensation in reverse order
    for i := len(s.executed) - 1; i >= 0; i-- {
        stepIndex := s.executed[i]
        step := s.steps[stepIndex]
        
        s.logger.Info(fmt.Sprintf("Compensating step: %s", step.Name))
        
        if err := step.Compensate(ctx, s.data); err != nil {
            s.logger.Error(fmt.Sprintf("Compensation failed for step %s: %v", 
                          step.Name, err))
            // Continue with other compensations even if one fails
        }
    }
    
    return fmt.Errorf("saga failed and compensation completed")
}

// E-commerce order saga example
func createOrderSaga() *SagaOrchestrator {
    steps := []SagaStep{
        {
            Name: "ValidateInventory",
            Execute: func(ctx context.Context, data interface{}) error {
                order := data.(*OrderData)
                return validateInventory(ctx, order)
            },
            Compensate: func(ctx context.Context, data interface{}) error {
                // No compensation needed for validation
                return nil
            },
        },
        {
            Name: "ReserveInventory", 
            Execute: func(ctx context.Context, data interface{}) error {
                order := data.(*OrderData)
                return reserveInventory(ctx, order)
            },
            Compensate: func(ctx context.Context, data interface{}) error {
                order := data.(*OrderData)
                return releaseInventory(ctx, order)
            },
        },
        {
            Name: "ProcessPayment",
            Execute: func(ctx context.Context, data interface{}) error {
                order := data.(*OrderData)
                return processPayment(ctx, order)
            },
            Compensate: func(ctx context.Context, data interface{}) error {
                order := data.(*OrderData)
                return refundPayment(ctx, order)
            },
        },
        {
            Name: "CreateOrder",
            Execute: func(ctx context.Context, data interface{}) error {
                order := data.(*OrderData)
                return createOrder(ctx, order)
            },
            Compensate: func(ctx context.Context, data interface{}) error {
                order := data.(*OrderData)
                return cancelOrder(ctx, order)
            },
        },
        {
            Name: "SendNotification",
            Execute: func(ctx context.Context, data interface{}) error {
                order := data.(*OrderData)
                return sendOrderConfirmation(ctx, order)
            },
            Compensate: func(ctx context.Context, data interface{}) error {
                order := data.(*OrderData)
                return sendCancellationNotification(ctx, order)
            },
        },
    }
    
    return NewSagaOrchestrator(steps)
}

type OrderData struct {
    UserID    string  `json:"user_id"`
    ProductID string  `json:"product_id"`
    Quantity  int     `json:"quantity"`
    Amount    float64 `json:"amount"`
    OrderID   string  `json:"order_id"`
}

// Inventory service integration
func validateInventory(ctx context.Context, order *OrderData) error {
    // Check if product exists and has sufficient quantity
    client := &http.Client{Timeout: 5 * time.Second}
    
    reqBody, _ := json.Marshal(map[string]interface{}{
        "product_id": order.ProductID,
        "quantity":   order.Quantity,
    })
    
    resp, err := client.Post("http://inventory-service/validate", 
                           "application/json", 
                           bytes.NewBuffer(reqBody))
    if err != nil {
        return fmt.Errorf("inventory validation failed: %w", err)
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != 200 {
        return fmt.Errorf("insufficient inventory")
    }
    
    return nil
}
```

Mumbai mein daily 7.5 million passengers travel karte hain local trains mein. Har passenger ka journey multiple systems involve karta hai - ticketing, security, crowd management. Yahi complexity federated systems mein hoti hai.

---

## Section 5: Event-Driven Federation (2,000 words)

### Event Sourcing with Federation

Event-driven architecture federation ka backbone hai. Jaise Mumbai ki news systems (newspapers, TV, radio) different sources se information gather karke distribute karte hain, waise hi event-driven federation multiple services ke events ko coordinate karta hai.

```javascript
// Event-Driven Federation Hub - Node.js
const EventEmitter = require('events');
const Redis = require('redis');

class EventDrivenFederationHub extends EventEmitter {
    constructor() {
        super();
        this.redis = Redis.createClient();
        this.eventStore = new Map();
        this.subscribers = new Map();
        this.eventProcessors = new Map();
        
        this.setupEventProcessing();
    }

    // Event publishing with federation routing
    async publishEvent(event) {
        const eventId = this.generateEventId();
        const timestamp = new Date().toISOString();
        
        const federatedEvent = {
            id: eventId,
            type: event.type,
            source: event.source,
            data: event.data,
            timestamp: timestamp,
            version: '1.0',
            federation: {
                targets: this.determineTargetServices(event),
                routing: this.calculateRoutingStrategy(event),
                priority: event.priority || 'normal'
            }
        };

        // Store event for replay capability
        this.eventStore.set(eventId, federatedEvent);
        
        // Publish to Redis for distribution
        await this.redis.publish('federation-events', JSON.stringify(federatedEvent));
        
        // Route to target services
        await this.routeEventToServices(federatedEvent);
        
        this.emit('event-published', federatedEvent);
        return eventId;
    }

    // Intelligent routing based on event type and service capabilities
    determineTargetServices(event) {
        const routingRules = {
            'user.created': ['notification-service', 'analytics-service', 'email-service'],
            'order.placed': ['inventory-service', 'payment-service', 'shipping-service'],
            'payment.completed': ['order-service', 'accounting-service', 'notification-service'],
            'product.updated': ['search-service', 'cache-service', 'recommendation-service']
        };

        const targets = routingRules[event.type] || [];
        
        // Add conditional routing based on event data
        if (event.type === 'order.placed' && event.data.amount > 10000) {
            targets.push('fraud-detection-service');
        }
        
        if (event.type === 'user.created' && event.data.country === 'IN') {
            targets.push('kyc-service', 'localization-service');
        }

        return targets;
    }

    // Route events to target services with retry logic
    async routeEventToServices(event) {
        const routingPromises = event.federation.targets.map(async (service) => {
            try {
                await this.deliverEventToService(service, event);
            } catch (error) {
                console.error(`Failed to deliver event to ${service}:`, error);
                await this.scheduleRetry(service, event, error);
            }
        });

        await Promise.allSettled(routingPromises);
    }

    async deliverEventToService(serviceName, event) {
        const serviceConfig = await this.getServiceConfig(serviceName);
        
        if (!serviceConfig.isHealthy) {
            throw new Error(`Service ${serviceName} is unhealthy`);
        }

        const response = await fetch(`${serviceConfig.endpoint}/events`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Event-ID': event.id,
                'X-Source-Service': event.source
            },
            body: JSON.stringify(event),
            timeout: 5000
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // Log successful delivery
        console.log(`Event ${event.id} delivered to ${serviceName}`);
    }

    // CQRS implementation for read/write separation
    setupCQRSHandlers() {
        // Command handlers (write side)
        this.on('command.create-user', async (command) => {
            const event = await this.handleCreateUserCommand(command);
            await this.publishEvent(event);
        });

        this.on('command.place-order', async (command) => {
            const events = await this.handlePlaceOrderCommand(command);
            for (const event of events) {
                await this.publishEvent(event);
            }
        });

        // Query handlers (read side)
        this.setupQueryHandlers();
    }

    async handleCreateUserCommand(command) {
        // Validate command
        this.validateCreateUserCommand(command);
        
        // Create user entity
        const user = {
            id: this.generateUserId(),
            email: command.email,
            name: command.name,
            createdAt: new Date().toISOString(),
            status: 'active'
        };

        // Return event
        return {
            type: 'user.created',
            source: 'user-service',
            data: user
        };
    }

    setupQueryHandlers() {
        // Read model updaters
        this.on('event-published', async (event) => {
            switch (event.type) {
                case 'user.created':
                    await this.updateUserReadModel(event.data);
                    break;
                case 'order.placed':
                    await this.updateOrderReadModel(event.data);
                    break;
                case 'payment.completed':
                    await this.updatePaymentReadModel(event.data);
                    break;
            }
        });
    }
}
```

### Zerodha ka Trading Platform Case Study

Zerodha India ka largest stockbroker hai with 6+ million active clients aur daily ₹40,000+ crores trading volume. Unka event-driven federation architecture dekho:

**Architecture Components:**
- Trading Engine: 5+ million orders per day
- Market Data: 200+ MB/second real-time data
- Risk Management: Real-time position monitoring
- Settlement: T+2 settlement cycle automation
- Compliance: SEBI regulatory reporting

```python
# Zerodha-style Trading Event Federation - Python
import asyncio
import json
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"

class OrderStatus(Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    COMPLETE = "COMPLETE" 
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

@dataclass
class TradingEvent:
    event_id: str
    event_type: str
    user_id: str
    symbol: str
    quantity: int
    price: float
    order_type: OrderType
    timestamp: float
    exchange: str = "NSE"
    
class TradingEventFederation:
    def __init__(self):
        self.event_handlers = {}
        self.risk_engine = RiskEngine()
        self.market_data = MarketDataService()
        self.order_book = OrderBookManager()
        self.compliance = ComplianceEngine()
        
    async def process_order_event(self, event: TradingEvent):
        """
        Process trading order with multi-service coordination
        """
        start_time = time.time()
        
        try:
            # Step 1: Pre-trade risk checks
            risk_result = await self.risk_engine.validate_order(event)
            if not risk_result.approved:
                await self.reject_order(event, risk_result.reason)
                return
            
            # Step 2: Get real-time market data
            market_data = await self.market_data.get_live_price(event.symbol)
            
            # Step 3: Apply regulatory compliance
            compliance_check = await self.compliance.validate_trade(event)
            if not compliance_check.compliant:
                await self.reject_order(event, "Compliance violation")
                return
                
            # Step 4: Submit to order book
            order_result = await self.order_book.place_order({
                'user_id': event.user_id,
                'symbol': event.symbol,
                'quantity': event.quantity,
                'price': event.price,
                'order_type': event.order_type.value,
                'market_price': market_data.ltp
            })
            
            # Step 5: Update portfolio
            await self.update_portfolio(event, order_result)
            
            # Step 6: Emit downstream events
            await self.emit_order_events(event, order_result)
            
            processing_time = time.time() - start_time
            print(f"Order processed in {processing_time:.3f}s")
            
        except Exception as e:
            await self.handle_order_failure(event, str(e))
    
    async def emit_order_events(self, original_event, order_result):
        """
        Emit events to downstream services
        """
        events_to_emit = []
        
        # Order placement event
        events_to_emit.append({
            'type': 'order.placed',
            'data': {
                'order_id': order_result.order_id,
                'user_id': original_event.user_id,
                'symbol': original_event.symbol,
                'status': order_result.status
            }
        })
        
        # Risk update event
        events_to_emit.append({
            'type': 'risk.position_updated',
            'data': {
                'user_id': original_event.user_id,
                'symbol': original_event.symbol,
                'position_change': original_event.quantity
            }
        })
        
        # Analytics event
        events_to_emit.append({
            'type': 'analytics.trade_executed',
            'data': {
                'symbol': original_event.symbol,
                'volume': original_event.quantity * original_event.price,
                'timestamp': original_event.timestamp
            }
        })
        
        # Emit all events concurrently
        await asyncio.gather(*[
            self.publish_event(event) for event in events_to_emit
        ])

class RiskEngine:
    def __init__(self):
        self.position_limits = {}
        self.margin_requirements = {}
    
    async def validate_order(self, event: TradingEvent) -> Dict:
        # Check margin requirements
        required_margin = self.calculate_margin(event)
        available_margin = await self.get_available_margin(event.user_id)
        
        if required_margin > available_margin:
            return {
                'approved': False,
                'reason': 'Insufficient margin',
                'required': required_margin,
                'available': available_margin
            }
        
        # Check position limits
        current_position = await self.get_position(event.user_id, event.symbol)
        max_position = self.position_limits.get(event.symbol, float('inf'))
        
        if abs(current_position + event.quantity) > max_position:
            return {
                'approved': False,
                'reason': 'Position limit exceeded'
            }
        
        return {'approved': True}
    
    def calculate_margin(self, event: TradingEvent) -> float:
        # Simplified margin calculation
        base_margin = event.quantity * event.price * 0.20  # 20% margin
        
        # Add additional margin for volatile stocks
        volatility_margin = base_margin * self.get_volatility_factor(event.symbol)
        
        return base_margin + volatility_margin
```

**Performance Metrics:**
- Order processing: <50ms average
- Peak throughput: 100,000 orders/minute  
- System availability: 99.95%
- Margin calls processed: 99.8% accuracy

### Kafka-based Federation Architecture

Apache Kafka federation ke liye Mumbai ki newspaper distribution system jaisa hai - central hub se multiple locations par news distribute hota hai.

```go
// Kafka Federation Manager - Go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "github.com/segmentio/kafka-go"
    "time"
)

type KafkaFederationManager struct {
    brokers    []string
    topics     map[string]*kafka.Writer
    consumers  map[string]*kafka.Reader
    config     FederationConfig
}

type FederationConfig struct {
    RetryAttempts    int           `json:"retry_attempts"`
    RetryDelay       time.Duration `json:"retry_delay"`
    BatchSize        int           `json:"batch_size"`
    FlushInterval    time.Duration `json:"flush_interval"`
    CompressionType  string        `json:"compression"`
}

func NewKafkaFederationManager(brokers []string) *KafkaFederationManager {
    return &KafkaFederationManager{
        brokers:   brokers,
        topics:    make(map[string]*kafka.Writer),
        consumers: make(map[string]*kafka.Reader),
        config: FederationConfig{
            RetryAttempts:   3,
            RetryDelay:      100 * time.Millisecond,
            BatchSize:       100,
            FlushInterval:   1 * time.Second,
            CompressionType: "gzip",
        },
    }
}

// Setup federation topics
func (k *KafkaFederationManager) SetupTopics() error {
    topicConfigs := []kafka.TopicConfig{
        {
            Topic:             "user-events",
            NumPartitions:     10,
            ReplicationFactor: 3,
        },
        {
            Topic:             "order-events", 
            NumPartitions:     20,
            ReplicationFactor: 3,
        },
        {
            Topic:             "payment-events",
            NumPartitions:     15,
            ReplicationFactor: 3,
        },
        {
            Topic:             "notification-events",
            NumPartitions:     5,
            ReplicationFactor: 2,
        },
    }

    conn, err := kafka.Dial("tcp", k.brokers[0])
    if err != nil {
        return fmt.Errorf("failed to connect to kafka: %w", err)
    }
    defer conn.Close()

    return conn.CreateTopics(topicConfigs...)
}

// Publish federated event
func (k *KafkaFederationManager) PublishEvent(topic string, event interface{}) error {
    writer, exists := k.topics[topic]
    if !exists {
        writer = k.createWriter(topic)
        k.topics[topic] = writer
    }

    eventData, err := json.Marshal(event)
    if err != nil {
        return fmt.Errorf("failed to marshal event: %w", err)
    }

    message := kafka.Message{
        Key:   []byte(fmt.Sprintf("%d", time.Now().UnixNano())),
        Value: eventData,
        Headers: []kafka.Header{
            {Key: "source", Value: []byte("federation-gateway")},
            {Key: "timestamp", Value: []byte(time.Now().Format(time.RFC3339))},
        },
    }

    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    return writer.WriteMessages(ctx, message)
}

func (k *KafkaFederationManager) createWriter(topic string) *kafka.Writer {
    return &kafka.Writer{
        Addr:                   kafka.TCP(k.brokers...),
        Topic:                  topic,
        BatchSize:              k.config.BatchSize,
        BatchTimeout:           k.config.FlushInterval,
        RequiredAcks:           kafka.RequireOne,
        CompressionCodec:       kafka.Gzip,
        AllowAutoTopicCreation: true,
    }
}

// Event consumer with federation routing
func (k *KafkaFederationManager) ConsumeEvents(topic string, handler func([]byte) error) error {
    reader := kafka.NewReader(kafka.ReaderConfig{
        Brokers:   k.brokers,
        Topic:     topic,
        GroupID:   fmt.Sprintf("%s-federation-consumer", topic),
        Partition: 0,
        MinBytes:  10e3, // 10KB
        MaxBytes:  10e6, // 10MB
    })

    k.consumers[topic] = reader

    for {
        message, err := reader.ReadMessage(context.Background())
        if err != nil {
            fmt.Printf("Error reading message: %v\n", err)
            continue
        }

        // Process message with retry logic
        if err := k.processMessageWithRetry(message.Value, handler); err != nil {
            fmt.Printf("Failed to process message after retries: %v\n", err)
        }
    }
}

func (k *KafkaFederationManager) processMessageWithRetry(data []byte, handler func([]byte) error) error {
    var lastErr error
    
    for attempt := 1; attempt <= k.config.RetryAttempts; attempt++ {
        if err := handler(data); err == nil {
            return nil
        } else {
            lastErr = err
            if attempt < k.config.RetryAttempts {
                time.Sleep(k.config.RetryDelay * time.Duration(attempt))
            }
        }
    }
    
    return fmt.Errorf("failed after %d attempts: %w", k.config.RetryAttempts, lastErr)
}
```

Mumbai mein daily 500+ newspapers print hote hain different languages mein. Each newspaper different audience ke liye hai, lekin same events cover karte hain. Event-driven federation mein bhi yahi hota hai - same event different services ke liye different format mein process hota hai.

---

## Section 6: Security & Authorization in Federation (2,500 words)

### OAuth2/OIDC Implementation in Federation

Security federated systems ka most critical aspect hai. Jaise Mumbai mein different areas mein entry ke liye different permissions chahiye (Bollywood studios, corporate offices, residential societies), waise hi API federation mein granular authorization chahiye.

```javascript
// OAuth2/OIDC Federation Security - Node.js
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const redis = require('redis');

class FederationSecurityManager {
    constructor() {
        this.redisClient = redis.createClient();
        this.tokenCache = new Map();
        this.authorizedServices = new Set();
        this.securityPolicies = new Map();
        
        this.setupSecurityPolicies();
    }

    // JWT token validation with federation context
    async validateFederationToken(token, requiredScopes = []) {
        try {
            // Check token cache first
            const cacheKey = `token:${crypto.createHash('sha256').update(token).digest('hex')}`;
            const cachedResult = await this.redisClient.get(cacheKey);
            
            if (cachedResult) {
                const tokenData = JSON.parse(cachedResult);
                return this.validateScopes(tokenData, requiredScopes);
            }

            // Decode and verify JWT
            const decoded = jwt.verify(token, process.env.JWT_SECRET);
            
            // Additional federation-specific validations
            const validationResult = await this.performFederationValidation(decoded);
            if (!validationResult.valid) {
                throw new Error(`Federation validation failed: ${validationResult.reason}`);
            }

            // Cache valid token
            await this.redisClient.setex(cacheKey, 300, JSON.stringify(decoded)); // 5 min cache

            return this.validateScopes(decoded, requiredScopes);

        } catch (error) {
            console.error('Token validation failed:', error.message);
            return {
                valid: false,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    async performFederationValidation(tokenData) {
        // Check if issuer is authorized
        if (!this.authorizedServices.has(tokenData.iss)) {
            return {
                valid: false,
                reason: `Unauthorized issuer: ${tokenData.iss}`
            };
        }

        // Check token expiration with buffer
        const now = Math.floor(Date.now() / 1000);
        if (tokenData.exp < now + 60) { // 60 second buffer
            return {
                valid: false,
                reason: 'Token expired or expiring soon'
            };
        }

        // Check audience
        if (tokenData.aud && !tokenData.aud.includes('federation-gateway')) {
            return {
                valid: false,
                reason: 'Invalid audience'
            };
        }

        // Rate limiting check
        const rateLimitResult = await this.checkRateLimit(tokenData.sub);
        if (!rateLimitResult.allowed) {
            return {
                valid: false,
                reason: 'Rate limit exceeded'
            };
        }

        return { valid: true };
    }

    validateScopes(tokenData, requiredScopes) {
        const userScopes = tokenData.scopes || [];
        const hasRequiredScopes = requiredScopes.every(scope => 
            userScopes.includes(scope) || userScopes.includes('admin')
        );

        return {
            valid: hasRequiredScopes,
            user: {
                id: tokenData.sub,
                email: tokenData.email,
                scopes: userScopes,
                roles: tokenData.roles || []
            },
            scopes: userScopes
        };
    }

    // Fine-grained authorization
    async authorizeOperation(user, resource, operation) {
        const policyKey = `${resource}:${operation}`;
        const policy = this.securityPolicies.get(policyKey);
        
        if (!policy) {
            return {
                authorized: false,
                reason: 'No policy found for operation'
            };
        }

        // Check role-based access
        const hasRequiredRole = policy.roles.some(role => 
            user.roles.includes(role)
        );

        // Check scope-based access
        const hasRequiredScope = policy.scopes.some(scope =>
            user.scopes.includes(scope)
        );

        // Custom business logic
        const businessRuleResult = await this.applyBusinessRules(
            user, resource, operation, policy
        );

        const authorized = (hasRequiredRole || hasRequiredScope) && 
                          businessRuleResult.allowed;

        return {
            authorized,
            reason: authorized ? 'Access granted' : businessRuleResult.reason,
            policy: policyKey
        };
    }

    async applyBusinessRules(user, resource, operation, policy) {
        // Time-based restrictions
        if (policy.timeRestrictions) {
            const currentHour = new Date().getHours();
            if (currentHour < policy.timeRestrictions.startHour || 
                currentHour > policy.timeRestrictions.endHour) {
                return {
                    allowed: false,
                    reason: 'Operation not allowed at this time'
                };
            }
        }

        // Geographic restrictions
        if (policy.geoRestrictions && user.location) {
            if (!policy.geoRestrictions.allowedCountries.includes(user.location.country)) {
                return {
                    allowed: false,
                    reason: 'Geographic access restriction'
                };
            }
        }

        // Data sensitivity checks
        if (resource.includes('sensitive') && !user.roles.includes('data-admin')) {
            return {
                allowed: false,
                reason: 'Insufficient privileges for sensitive data'
            };
        }

        return { allowed: true };
    }

    setupSecurityPolicies() {
        // User operations
        this.securityPolicies.set('user:read', {
            roles: ['user', 'admin'],
            scopes: ['read:user', 'admin'],
            timeRestrictions: null
        });

        this.securityPolicies.set('user:write', {
            roles: ['admin'],
            scopes: ['write:user', 'admin'],
            timeRestrictions: {
                startHour: 6,
                endHour: 22
            }
        });

        // Payment operations
        this.securityPolicies.set('payment:read', {
            roles: ['finance', 'admin'],
            scopes: ['read:payment'],
            geoRestrictions: {
                allowedCountries: ['IN', 'US', 'GB']
            }
        });

        this.securityPolicies.set('payment:write', {
            roles: ['finance-admin'],
            scopes: ['write:payment'],
            timeRestrictions: {
                startHour: 9,
                endHour: 18
            }
        });
    }

    // API key management for service-to-service communication
    async generateServiceApiKey(serviceName, permissions) {
        const apiKey = crypto.randomBytes(32).toString('hex');
        const keyHash = crypto.createHash('sha256').update(apiKey).digest('hex');
        
        const keyData = {
            serviceName,
            permissions,
            createdAt: new Date().toISOString(),
            expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(), // 1 year
            status: 'active'
        };

        // Store in Redis
        await this.redisClient.setex(`apikey:${keyHash}`, 31536000, JSON.stringify(keyData)); // 1 year

        return {
            apiKey: `fed_${apiKey}`,
            hash: keyHash,
            metadata: keyData
        };
    }

    async validateApiKey(apiKey) {
        if (!apiKey.startsWith('fed_')) {
            return { valid: false, error: 'Invalid API key format' };
        }

        const key = apiKey.substring(4);
        const keyHash = crypto.createHash('sha256').update(key).digest('hex');
        
        const keyData = await this.redisClient.get(`apikey:${keyHash}`);
        if (!keyData) {
            return { valid: false, error: 'API key not found' };
        }

        const parsedData = JSON.parse(keyData);
        
        // Check expiration
        if (new Date(parsedData.expiresAt) < new Date()) {
            return { valid: false, error: 'API key expired' };
        }

        // Check status
        if (parsedData.status !== 'active') {
            return { valid: false, error: 'API key inactive' };
        }

        return {
            valid: true,
            service: parsedData.serviceName,
            permissions: parsedData.permissions
        };
    }

    // Rate limiting implementation
    async checkRateLimit(userId, limit = 1000, window = 3600) {
        const key = `ratelimit:${userId}`;
        const current = await this.redisClient.get(key);
        
        if (!current) {
            await this.redisClient.setex(key, window, 1);
            return { allowed: true, remaining: limit - 1 };
        }

        const count = parseInt(current);
        if (count >= limit) {
            return { allowed: false, remaining: 0 };
        }

        await this.redisClient.incr(key);
        return { allowed: true, remaining: limit - count - 1 };
    }
}

// Usage in federation gateway
const securityManager = new FederationSecurityManager();

// Middleware for request authentication
async function federationAuthMiddleware(req, res, next) {
    const token = req.headers.authorization?.split(' ')[1];
    const apiKey = req.headers['x-api-key'];
    
    let authResult;
    
    if (token) {
        authResult = await securityManager.validateFederationToken(token);
    } else if (apiKey) {
        authResult = await securityManager.validateApiKey(apiKey);
    } else {
        return res.status(401).json({ error: 'No authentication provided' });
    }
    
    if (!authResult.valid) {
        return res.status(401).json({ error: authResult.error });
    }
    
    req.user = authResult.user || { service: authResult.service };
    next();
}
```

### PhonePe ka Security Architecture Case Study

PhonePe processes 12+ billion transactions annually worth ₹15+ lakh crores. Unka security-first federation approach dekho:

**Security Layers:**
1. **API Gateway Security**: JWT + OAuth2.0
2. **Service Mesh**: mTLS between services  
3. **Data Encryption**: AES-256 at rest, TLS 1.3 in transit
4. **Fraud Detection**: ML-based real-time scoring
5. **Compliance**: PCI DSS Level 1, RBI guidelines

```java
// PhonePe-style Security Implementation - Java Spring Boot
@RestController
@RequestMapping("/api/payments")
@Validated
public class SecurePaymentController {
    
    @Autowired
    private PaymentSecurityService securityService;
    
    @Autowired
    private FraudDetectionService fraudDetection;
    
    @Autowired
    private ComplianceService compliance;
    
    @PostMapping("/initiate")
    @PreAuthorize("hasRole('USER') and hasPermission('PAYMENT_INITIATE')")
    public ResponseEntity<PaymentResponse> initiatePayment(
            @Valid @RequestBody PaymentRequest request,
            @RequestHeader("X-Device-ID") String deviceId,
            @RequestHeader("X-Session-ID") String sessionId,
            Authentication authentication) {
        
        long startTime = System.currentTimeMillis();
        String transactionId = generateTransactionId();
        
        try {
            // Security validations
            SecurityContext securityContext = SecurityContext.builder()
                .userId(authentication.getName())
                .deviceId(deviceId) 
                .sessionId(sessionId)
                .ipAddress(getClientIpAddress())
                .userAgent(request.getHeader("User-Agent"))
                .build();
            
            // Step 1: Device and session validation
            DeviceValidationResult deviceValidation = 
                securityService.validateDevice(deviceId, authentication.getName());
            
            if (!deviceValidation.isTrusted()) {
                return handleSecurityViolation("Untrusted device", transactionId);
            }
            
            // Step 2: Real-time fraud detection
            FraudScore fraudScore = fraudDetection.calculateRiskScore(
                request, securityContext
            );
            
            if (fraudScore.getScore() > 0.8) {
                // High risk - require additional authentication
                return requireStepUpAuthentication(request, transactionId);
            }
            
            // Step 3: Regulatory compliance checks
            ComplianceResult complianceResult = compliance.validateTransaction(
                request, authentication.getName()
            );
            
            if (!complianceResult.isCompliant()) {
                return ResponseEntity.badRequest()
                    .body(PaymentResponse.error("Compliance violation: " + 
                         complianceResult.getReason()));
            }
            
            // Step 4: Encryption and tokenization
            EncryptedPaymentData encryptedData = securityService.encryptPaymentData(
                request.getCardDetails(), request.getAmount()
            );
            
            // Step 5: Process payment with security context
            PaymentResult result = processSecurePayment(
                encryptedData, securityContext, fraudScore
            );
            
            // Step 6: Audit logging
            auditPaymentTransaction(transactionId, result, securityContext);
            
            long processingTime = System.currentTimeMillis() - startTime;
            
            return ResponseEntity.ok(PaymentResponse.builder()
                .transactionId(transactionId)
                .status(result.getStatus())
                .amount(result.getAmount())
                .processingTime(processingTime)
                .securityScore(fraudScore.getScore())
                .build());
                
        } catch (SecurityException e) {
            return handleSecurityViolation(e.getMessage(), transactionId);
        } catch (Exception e) {
            logSecurityIncident(transactionId, e, authentication.getName());
            return ResponseEntity.internalServerError()
                .body(PaymentResponse.error("Payment processing failed"));
        }
    }
    
    private PaymentResult processSecurePayment(
            EncryptedPaymentData data, 
            SecurityContext context,
            FraudScore fraudScore) {
        
        // Multi-factor payment processing
        PaymentProcessor processor = PaymentProcessorFactory
            .createProcessor(data.getPaymentMethod());
        
        // Add security headers for downstream services
        PaymentContext paymentContext = PaymentContext.builder()
            .encryptedData(data)
            .securityContext(context)
            .fraudScore(fraudScore)
            .compliance(true)
            .build();
        
        return processor.processPayment(paymentContext);
    }
    
    // Fraud detection with ML
    @Component
    public class FraudDetectionService {
        
        @Autowired
        private MLModelService mlModelService;
        
        public FraudScore calculateRiskScore(
                PaymentRequest request, SecurityContext context) {
            
            // Feature extraction
            Map<String, Object> features = extractFeatures(request, context);
            
            // ML model inference
            double riskScore = mlModelService.predict("fraud_detection_v2", features);
            
            // Rule-based checks
            double ruleScore = applyRuleBasedChecks(request, context);
            
            // Combined score
            double finalScore = (riskScore * 0.7) + (ruleScore * 0.3);
            
            return FraudScore.builder()
                .score(finalScore)
                .riskLevel(getRiskLevel(finalScore))
                .factors(identifyRiskFactors(features, riskScore))
                .build();
        }
        
        private Map<String, Object> extractFeatures(
                PaymentRequest request, SecurityContext context) {
            
            return Map.of(
                "amount", request.getAmount(),
                "time_of_day", LocalTime.now().getHour(),
                "device_trust", context.getDeviceId(),
                "location_country", context.getLocation().getCountry(),
                "velocity_24h", getTransactionVelocity(context.getUserId(), 24),
                "merchant_category", request.getMerchantCategory(),
                "payment_method", request.getPaymentMethod()
            );
        }
        
        private double applyRuleBasedChecks(
                PaymentRequest request, SecurityContext context) {
            
            double score = 0.0;
            
            // High amount transaction
            if (request.getAmount() > 50000) {
                score += 0.3;
            }
            
            // Unusual time (late night)
            int hour = LocalTime.now().getHour();
            if (hour < 6 || hour > 22) {
                score += 0.2;
            }
            
            // Geographic anomaly
            if (!context.getLocation().getCountry().equals("IN")) {
                score += 0.4;
            }
            
            // High velocity
            int dailyTransactions = getTransactionCount(context.getUserId(), 24);
            if (dailyTransactions > 10) {
                score += 0.3;
            }
            
            return Math.min(score, 1.0);
        }
    }
}

@Service
public class PaymentSecurityService {
    
    @Autowired
    private KeyManagementService kms;
    
    public EncryptedPaymentData encryptPaymentData(
            CardDetails cardDetails, BigDecimal amount) {
        
        // Tokenize sensitive data
        String cardToken = tokenizeCardNumber(cardDetails.getCardNumber());
        
        // Encrypt amount and metadata
        String encryptedAmount = kms.encrypt(amount.toString(), "payment-key");
        String encryptedMetadata = kms.encrypt(
            cardDetails.toMetadataString(), "metadata-key"
        );
        
        return EncryptedPaymentData.builder()
            .cardToken(cardToken)
            .encryptedAmount(encryptedAmount)
            .encryptedMetadata(encryptedMetadata)
            .timestamp(Instant.now())
            .build();
    }
    
    private String tokenizeCardNumber(String cardNumber) {
        // PCI DSS compliant tokenization
        String last4 = cardNumber.substring(cardNumber.length() - 4);
        String tokenPrefix = "tok_";
        String randomSuffix = generateRandomString(16);
        
        // Store mapping in secure vault
        String token = tokenPrefix + randomSuffix;
        vaultService.storeCardMapping(token, cardNumber);
        
        return token;
    }
}
```

**Security Metrics:**
- Fraud detection accuracy: 99.7%
- False positive rate: <0.1%
- Transaction security: 99.99% success rate
- Compliance violations: 0 (clean PCI DSS audits)

### API Key Management at Scale

Enterprise federation mein API key management ek major challenge hai. Jaise Mumbai mein building society keys manage karte hain (different keys for different people and purposes), waise hi API keys ko manage karna padta hai.

```python
# Enterprise API Key Management - Python
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import redis
import asyncio

@dataclass 
class ApiKeyMetadata:
    key_id: str
    name: str
    service_name: str
    permissions: List[str]
    rate_limit: int
    expires_at: datetime
    created_by: str
    last_used: Optional[datetime] = None
    usage_count: int = 0
    status: str = 'active'

class EnterpriseApiKeyManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.key_prefix = "apikey:"
        self.usage_prefix = "usage:"
        self.rate_limit_prefix = "ratelimit:"
        
    async def create_api_key(
        self, 
        name: str, 
        service_name: str, 
        permissions: List[str],
        rate_limit: int = 10000,
        expires_days: int = 365,
        created_by: str = "system"
    ) -> Dict[str, str]:
        """
        Create new API key with metadata
        """
        # Generate secure API key
        key_id = secrets.token_urlsafe(16)
        api_key = f"ak_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Create metadata
        metadata = ApiKeyMetadata(
            key_id=key_id,
            name=name,
            service_name=service_name, 
            permissions=permissions,
            rate_limit=rate_limit,
            expires_at=datetime.now() + timedelta(days=expires_days),
            created_by=created_by
        )
        
        # Store in Redis
        await self.redis.hset(
            f"{self.key_prefix}{key_hash}",
            mapping={
                "metadata": json.dumps(metadata.__dict__, default=str),
                "created_at": datetime.now().isoformat()
            }
        )
        
        # Set expiration
        await self.redis.expire(
            f"{self.key_prefix}{key_hash}", 
            expires_days * 24 * 3600
        )
        
        return {
            "api_key": api_key,
            "key_id": key_id,
            "expires_at": metadata.expires_at.isoformat()
        }
    
    async def validate_api_key(self, api_key: str) -> Dict:
        """
        Validate API key and return metadata
        """
        if not api_key.startswith("ak_"):
            return {"valid": False, "error": "Invalid key format"}
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Get key metadata
        key_data = await self.redis.hgetall(f"{self.key_prefix}{key_hash}")
        if not key_data:
            return {"valid": False, "error": "Key not found"}
        
        metadata = json.loads(key_data["metadata"])
        
        # Check expiration
        expires_at = datetime.fromisoformat(metadata["expires_at"])
        if datetime.now() > expires_at:
            return {"valid": False, "error": "Key expired"}
        
        # Check status
        if metadata["status"] != "active":
            return {"valid": False, "error": "Key inactive"}
        
        # Check rate limit
        rate_limit_result = await self.check_rate_limit(
            key_hash, metadata["rate_limit"]
        )
        
        if not rate_limit_result["allowed"]:
            return {
                "valid": False, 
                "error": "Rate limit exceeded",
                "reset_at": rate_limit_result["reset_at"]
            }
        
        # Update usage metrics
        await self.update_usage_metrics(key_hash)
        
        return {
            "valid": True,
            "metadata": metadata,
            "rate_limit_remaining": rate_limit_result["remaining"]
        }
    
    async def check_rate_limit(self, key_hash: str, limit: int) -> Dict:
        """
        Check and enforce rate limits using sliding window
        """
        now = datetime.now()
        window_start = now - timedelta(hours=1)  # 1-hour sliding window
        
        rate_key = f"{self.rate_limit_prefix}{key_hash}"
        
        # Remove old entries
        await self.redis.zremrangebyscore(
            rate_key,
            0,
            window_start.timestamp()
        )
        
        # Count current requests
        current_count = await self.redis.zcard(rate_key)
        
        if current_count >= limit:
            # Calculate reset time
            oldest_request = await self.redis.zrange(rate_key, 0, 0, withscores=True)
            if oldest_request:
                reset_at = datetime.fromtimestamp(oldest_request[0][1]) + timedelta(hours=1)
            else:
                reset_at = now + timedelta(hours=1)
            
            return {
                "allowed": False,
                "remaining": 0,
                "reset_at": reset_at.isoformat()
            }
        
        # Add current request
        await self.redis.zadd(rate_key, {str(now.timestamp()): now.timestamp()})
        await self.redis.expire(rate_key, 3600)  # 1 hour TTL
        
        return {
            "allowed": True,
            "remaining": limit - current_count - 1,
            "reset_at": (now + timedelta(hours=1)).isoformat()
        }
    
    async def update_usage_metrics(self, key_hash: str):
        """
        Update API key usage statistics
        """
        usage_key = f"{self.usage_prefix}{key_hash}"
        
        # Update counters
        pipeline = self.redis.pipeline()
        pipeline.hincrby(usage_key, "total_requests", 1)
        pipeline.hset(usage_key, "last_used", datetime.now().isoformat())
        await pipeline.execute()
    
    async def get_usage_analytics(self, key_id: str) -> Dict:
        """
        Get detailed usage analytics for API key
        """
        # Find key by key_id
        keys = await self.redis.keys(f"{self.key_prefix}*")
        target_key = None
        
        for key in keys:
            data = await self.redis.hgetall(key)
            if data and json.loads(data["metadata"])["key_id"] == key_id:
                target_key = key
                break
        
        if not target_key:
            return {"error": "Key not found"}
        
        key_hash = target_key.split(":")[-1]
        usage_key = f"{self.usage_prefix}{key_hash}"
        
        usage_data = await self.redis.hgetall(usage_key)
        
        return {
            "total_requests": int(usage_data.get("total_requests", 0)),
            "last_used": usage_data.get("last_used"),
            "daily_average": await self.calculate_daily_average(key_hash),
            "peak_usage_hour": await self.get_peak_usage_hour(key_hash)
        }
    
    async def revoke_api_key(self, key_id: str, reason: str = "Manual revocation"):
        """
        Revoke API key immediately
        """
        keys = await self.redis.keys(f"{self.key_prefix}*")
        
        for key in keys:
            data = await self.redis.hgetall(key)
            if data and json.loads(data["metadata"])["key_id"] == key_id:
                metadata = json.loads(data["metadata"])
                metadata["status"] = "revoked"
                metadata["revoked_at"] = datetime.now().isoformat()
                metadata["revocation_reason"] = reason
                
                await self.redis.hset(key, "metadata", json.dumps(metadata, default=str))
                return {"success": True, "message": "Key revoked successfully"}
        
        return {"success": False, "error": "Key not found"}

# Usage example
async def main():
    redis_client = redis.Redis(decode_responses=True)
    key_manager = EnterpriseApiKeyManager(redis_client)
    
    # Create API key for microservice
    result = await key_manager.create_api_key(
        name="Payment Service Key",
        service_name="payment-service",
        permissions=["read:payments", "write:payments", "read:users"],
        rate_limit=50000,  # 50k requests per hour
        expires_days=90
    )
    
    print(f"Created API key: {result['api_key']}")
    
    # Validate the key
    validation = await key_manager.validate_api_key(result['api_key'])
    print(f"Validation result: {validation}")
```

Mumbai mein local train pass different types ke hote hain - monthly, quarterly, first class, second class. Each pass different privileges deta hai. API keys bhi similar hain - different permissions, rate limits, aur access levels.

### Production Security Metrics

Real-world federation security mein ye metrics track karne padते हैं:

1. **Authentication Metrics:**
   - Token validation latency: <10ms
   - Authentication success rate: >99.9%
   - Invalid token attempts: <0.01%

2. **Authorization Metrics:**
   - Authorization check latency: <5ms
   - Permission denial rate: <1%
   - Privilege escalation attempts: 0

3. **Rate Limiting:**
   - Rate limit hit rate: <5%
   - False positive blocks: <0.1%
   - DDoS mitigation: >99.9% effective

4. **Security Incidents:**
   - Mean time to detect: <2 minutes
   - Mean time to respond: <10 minutes
   - False security alerts: <5%

---

## Episode Conclusion

Doston, aaj humne API Federation ke advanced patterns dekhe - microservices integration से लेकर security implementation तक। Key takeaways:

1. **Service Mesh Integration**: Federation aur service mesh ka combination powerful coordination deta hai
2. **Event-Driven Patterns**: Kafka-based federation scalable aur resilient systems banata hai  
3. **Security First**: OAuth2/OIDC, fine-grained authorization, aur API key management essential हैं
4. **Production Ready**: BookMyShow aur PhonePe जैसे real examples से सीखें

Mumbai ki local train system jaisa - multiple lines, coordination, security, aur millions of daily users. API Federation bhi waise hi complex lekin organized system hai.

Next episode mein hum "Serverless at Scale" dekhenge - कैसे serverless functions को production में scale करें।

**Total Word Count: 6,500 words**

---

*Generated for System Design Hindi Podcast - Episode 108 Part 2*
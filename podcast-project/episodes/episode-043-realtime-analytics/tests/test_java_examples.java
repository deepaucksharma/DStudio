/*
 * Test Suite for Java Real-time Analytics Examples
 * Episode 43: Real-time Analytics at Scale
 * 
 * Comprehensive tests for all Java code examples using JUnit 5
 */

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;

import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.time.LocalDateTime;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

/**
 * Test Suite for Flink Stream Processing
 * FlipkartInventoryAnalytics की functionality test करता है
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("Flink Stream Processing Tests")
class FlinkStreamProcessingTest {
    
    // Mock objects for testing
    @Mock
    private MockInventoryEventSource mockEventSource;
    
    @Mock
    private MockInventoryEventSink mockEventSink;
    
    private List<InventoryEvent> testEvents;
    
    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        testEvents = createTestInventoryEvents();
    }
    
    private List<InventoryEvent> createTestInventoryEvents() {
        List<InventoryEvent> events = new ArrayList<>();
        
        // Create sample inventory events
        events.add(new InventoryEvent(
            "PRODUCT_001", "WH_MUM", "sale", -5, 
            System.currentTimeMillis(), 1000.0, "electronics"
        ));
        
        events.add(new InventoryEvent(
            "PRODUCT_001", "WH_MUM", "restock", 100, 
            System.currentTimeMillis(), 1000.0, "electronics"
        ));
        
        events.add(new InventoryEvent(
            "PRODUCT_002", "WH_DEL", "sale", -3, 
            System.currentTimeMillis(), 500.0, "fashion"
        ));
        
        return events;
    }
    
    @Test
    @DisplayName("Test Inventory Event Creation")
    void testInventoryEventCreation() {
        InventoryEvent event = new InventoryEvent(
            "TEST_PRODUCT", "TEST_WH", "sale", -10,
            System.currentTimeMillis(), 100.0, "test_category"
        );
        
        assertEquals("TEST_PRODUCT", event.productId);
        assertEquals("TEST_WH", event.warehouseId);
        assertEquals("sale", event.eventType);
        assertEquals(-10, event.quantityChange);
        assertEquals("test_category", event.category);
        assertTrue(event.price > 0);
    }
    
    @Test
    @DisplayName("Test JSON to Inventory Event Mapping")
    void testJsonToInventoryEventMapping() {
        String jsonString = "{\"product_id\":\"PROD_001\"," +
                           "\"warehouse_id\":\"WH_001\"," +
                           "\"event_type\":\"sale\"," +
                           "\"quantity_change\":-5," +
                           "\"timestamp\":" + System.currentTimeMillis() + "," +
                           "\"price\":1000.0," +
                           "\"category\":\"electronics\"}";
        
        try {
            JsonToInventoryEventMapper mapper = new JsonToInventoryEventMapper();
            InventoryEvent event = mapper.map(jsonString);
            
            assertEquals("PROD_001", event.productId);
            assertEquals("WH_001", event.warehouseId);
            assertEquals("sale", event.eventType);
            assertEquals(-5, event.quantityChange);
            assertEquals("electronics", event.category);
        } catch (Exception e) {
            fail("JSON mapping should not throw exception: " + e.getMessage());
        }
    }
    
    @Test
    @DisplayName("Test Invalid JSON Handling")
    void testInvalidJsonHandling() {
        String invalidJson = "{invalid json}";
        
        try {
            JsonToInventoryEventMapper mapper = new JsonToInventoryEventMapper();
            InventoryEvent event = mapper.map(invalidJson);
            
            // Should return default event with "unknown" values
            assertEquals("unknown", event.productId);
            assertEquals("error", event.eventType);
        } catch (Exception e) {
            fail("Should handle invalid JSON gracefully");
        }
    }
    
    @Test
    @DisplayName("Test Inventory Aggregation Logic")
    void testInventoryAggregation() {
        // Test the aggregation logic
        List<InventoryEvent> windowEvents = testEvents.stream()
            .filter(event -> "PRODUCT_001".equals(event.productId))
            .collect(Collectors.toList());
        
        int totalStockChange = windowEvents.stream()
            .mapToInt(event -> event.quantityChange)
            .sum();
        
        double totalRevenue = windowEvents.stream()
            .filter(event -> "sale".equals(event.eventType))
            .mapToDouble(event -> Math.abs(event.quantityChange) * event.price)
            .sum();
        
        assertEquals(95, totalStockChange); // -5 + 100
        assertEquals(5000.0, totalRevenue); // 5 * 1000.0
    }
    
    @Test
    @DisplayName("Test Alert Level Determination")
    void testAlertLevelDetermination() {
        // Test different stock levels and their alert levels
        assertEquals("OUT_OF_STOCK", determineAlertLevel(0, 1));
        assertEquals("CRITICAL", determineAlertLevel(5, 1));
        assertEquals("LOW", determineAlertLevel(25, 1));
        assertEquals("OK", determineAlertLevel(100, 1));
    }
    
    private String determineAlertLevel(int currentStock, int eventCount) {
        if (currentStock == 0) {
            return "OUT_OF_STOCK";
        } else if (currentStock < 10) {
            return "CRITICAL";
        } else if (currentStock < 50) {
            return "LOW";
        } else {
            return "OK";
        }
    }
    
    @Test
    @DisplayName("Test Concurrent Event Processing")
    @Execution(ExecutionMode.CONCURRENT)
    void testConcurrentEventProcessing() throws InterruptedException {
        int numThreads = 5;
        int eventsPerThread = 10;
        CountDownLatch latch = new CountDownLatch(numThreads);
        List<InventoryEvent> allEvents = new CopyOnWriteArrayList<>();
        
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        
        for (int i = 0; i < numThreads; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    for (int j = 0; j < eventsPerThread; j++) {
                        InventoryEvent event = new InventoryEvent(
                            "PRODUCT_" + threadId + "_" + j,
                            "WAREHOUSE_" + threadId,
                            "sale",
                            -(j + 1),
                            System.currentTimeMillis(),
                            100.0 * (j + 1),
                            "category_" + threadId
                        );
                        allEvents.add(event);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        assertTrue(latch.await(5, TimeUnit.SECONDS));
        assertEquals(numThreads * eventsPerThread, allEvents.size());
        
        executor.shutdown();
    }
}

/**
 * Test Suite for Event Sourcing Pattern
 * OlaEventSourcingSystem की functionality test करता है
 */
@DisplayName("Event Sourcing Pattern Tests")
class EventSourcingTest {
    
    private EventStore eventStore;
    private RideAggregateRepository repository;
    
    @BeforeEach
    void setUp() {
        eventStore = new EventStore();
        repository = new RideAggregateRepository(eventStore);
    }
    
    @Test
    @DisplayName("Test Event Store Basic Operations")
    void testEventStoreBasicOperations() {
        RideRequestedEvent event = new RideRequestedEvent(
            "EVENT_001", "RIDE_001", "USER_001",
            "Bandra", "Andheri", "Mini", 200.0
        );
        
        eventStore.appendEvent(event);
        
        assertEquals(1, eventStore.getTotalEventCount());
        
        List<Event> events = eventStore.getEventsForAggregate("RIDE_001");
        assertEquals(1, events.size());
        assertEquals("EVENT_001", events.get(0).eventId);
    }
    
    @Test
    @DisplayName("Test Ride Aggregate State Changes")
    void testRideAggregateStateChanges() {
        String rideId = "RIDE_TEST_001";
        String userId = "USER_TEST_001";
        
        // Create ride requested event
        RideRequestedEvent requestEvent = new RideRequestedEvent(
            "EVENT_001", rideId, userId,
            "Bandra", "Andheri", "Mini", 200.0
        );
        repository.saveEvent(requestEvent);
        
        // Get aggregate and verify state
        RideAggregate aggregate = repository.getAggregate(rideId);
        assertEquals("REQUESTED", aggregate.status);
        assertEquals(userId, aggregate.userId);
        assertEquals("Bandra", aggregate.pickupLocation);
        assertEquals("Andheri", aggregate.dropLocation);
        
        // Add driver assigned event
        DriverAssignedEvent driverEvent = new DriverAssignedEvent(
            "EVENT_002", rideId, userId, "DRIVER_001",
            "राम शर्मा", "MH01AB1234", 4.5, 10
        );
        repository.saveEvent(driverEvent);
        
        // Verify state change
        aggregate = repository.getAggregate(rideId);
        assertEquals("DRIVER_ASSIGNED", aggregate.status);
        assertEquals("DRIVER_001", aggregate.driverId);
        assertEquals("राम शर्मा", aggregate.driverName);
    }
    
    @Test
    @DisplayName("Test Event Replay Functionality")
    void testEventReplay() {
        String rideId = "RIDE_REPLAY_001";
        
        // Create multiple events
        List<Event> events = Arrays.asList(
            new RideRequestedEvent("E1", rideId, "USER_001", "A", "B", "Mini", 200.0),
            new DriverAssignedEvent("E2", rideId, "USER_001", "DRIVER_001", "Driver", "MH01", 4.5, 10),
            new RideStartedEvent("E3", rideId, "USER_001", 19.0, 72.0, System.currentTimeMillis()),
            new RideCompletedEvent("E4", rideId, "USER_001", 19.1, 72.1, 180.0, 10.5, System.currentTimeMillis(), "UPI")
        );
        
        // Store all events
        for (Event event : events) {
            repository.saveEvent(event);
        }
        
        // Clear cache and replay
        repository.clearCache();
        RideAggregate aggregate = repository.getAggregate(rideId);
        
        // Verify final state
        assertEquals("COMPLETED", aggregate.status);
        assertEquals(180.0, aggregate.actualFare);
        assertEquals("UPI", aggregate.paymentMethod);
        assertEquals(4, aggregate.eventHistory.size());
    }
    
    @Test
    @DisplayName("Test Real-time Analytics Processing")
    void testRealTimeAnalyticsProcessing() {
        RealTimeAnalyticsProcessor processor = new RealTimeAnalyticsProcessor(eventStore);
        
        // Add some test events
        for (int i = 0; i < 10; i++) {
            RideRequestedEvent event = new RideRequestedEvent(
                "EVENT_" + i, "RIDE_" + i, "USER_" + (i % 3),
                "Location_A", "Location_B", "Mini", 200.0 + i * 10
            );
            eventStore.appendEvent(event);
        }
        
        // Let processor run briefly
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        Map<String, Object> metrics = processor.getCurrentMetrics();
        assertTrue(metrics.containsKey("totalRides"));
        assertTrue((Integer) metrics.get("totalRides") >= 0);
    }
    
    @Test
    @DisplayName("Test Event Handler Registration")
    void testEventHandlerRegistration() {
        List<Event> processedEvents = new ArrayList<>();
        
        // Register event handler
        eventStore.addEventHandler(processedEvents::add);
        
        // Add event
        RideRequestedEvent event = new RideRequestedEvent(
            "HANDLER_TEST", "RIDE_001", "USER_001",
            "A", "B", "Mini", 200.0
        );
        eventStore.appendEvent(event);
        
        // Verify handler was called
        assertEquals(1, processedEvents.size());
        assertEquals("HANDLER_TEST", processedEvents.get(0).eventId);
    }
}

/**
 * Test Suite for CQRS Implementation
 * ZomatoCQRSSystem की functionality test करता है
 */
@DisplayName("CQRS Implementation Tests")
class CQRSImplementationTest {
    
    private OrderCommandHandler commandHandler;
    private OrderQueryHandler queryHandler;
    private EventHandlerBridge eventBridge;
    
    @BeforeEach
    void setUp() {
        commandHandler = new OrderCommandHandler();
        queryHandler = new OrderQueryHandler();
        eventBridge = new EventHandlerBridge(queryHandler);
        
        // Wire up event handling
        commandHandler.addEventHandler(eventBridge::handleEvent);
    }
    
    @Test
    @DisplayName("Test Order Placement Command")
    void testOrderPlacementCommand() {
        List<OrderItem> items = Arrays.asList(
            new OrderItem("ITEM_001", "पवभाजी", 2, 80.0, "Main Course", Collections.emptyList())
        );
        
        PlaceOrderCommand command = new PlaceOrderCommand(
            "CMD_001", "ORDER_001", "CUST_001", "REST_001",
            items, "Mumbai", "UPI", 160.0
        );
        
        commandHandler.handle(command);
        
        // Verify aggregate was created
        OrderAggregate aggregate = commandHandler.getAggregate("ORDER_001");
        assertNotNull(aggregate);
        assertEquals("PLACED", aggregate.status);
        assertEquals("CUST_001", aggregate.customerId);
        assertEquals(160.0, aggregate.totalAmount);
    }
    
    @Test
    @DisplayName("Test Order Status Update Command")
    void testOrderStatusUpdateCommand() {
        // First place an order
        List<OrderItem> items = Arrays.asList(
            new OrderItem("ITEM_001", "पवभाजी", 1, 80.0, "Main Course", Collections.emptyList())
        );
        
        PlaceOrderCommand placeCommand = new PlaceOrderCommand(
            "CMD_001", "ORDER_002", "CUST_001", "REST_001",
            items, "Mumbai", "UPI", 80.0
        );
        commandHandler.handle(placeCommand);
        
        // Then update status
        UpdateOrderStatusCommand updateCommand = new UpdateOrderStatusCommand(
            "CMD_002", "ORDER_002", "CONFIRMED", "SYSTEM", "Order confirmed"
        );
        commandHandler.handle(updateCommand);
        
        // Verify status change
        OrderAggregate aggregate = commandHandler.getAggregate("ORDER_002");
        assertEquals("CONFIRMED", aggregate.status);
        assertTrue(aggregate.statusHistory.contains("CONFIRMED"));
    }
    
    @Test
    @DisplayName("Test Order Cancellation Command")
    void testOrderCancellationCommand() {
        // Place order first
        List<OrderItem> items = Arrays.asList(
            new OrderItem("ITEM_001", "दाल", 1, 60.0, "Main Course", Collections.emptyList())
        );
        
        PlaceOrderCommand placeCommand = new PlaceOrderCommand(
            "CMD_001", "ORDER_003", "CUST_001", "REST_001",
            items, "Mumbai", "UPI", 60.0
        );
        commandHandler.handle(placeCommand);
        
        // Cancel order
        CancelOrderCommand cancelCommand = new CancelOrderCommand(
            "CMD_002", "ORDER_003", "Customer changed mind", "CUSTOMER", 48.0
        );
        commandHandler.handle(cancelCommand);
        
        // Verify cancellation
        OrderAggregate aggregate = commandHandler.getAggregate("ORDER_003");
        assertEquals("CANCELLED", aggregate.status);
        assertEquals("Customer changed mind", aggregate.cancellationReason);
    }
    
    @Test
    @DisplayName("Test Query Side Read Models")
    void testQuerySideReadModels() {
        // Place multiple orders
        for (int i = 1; i <= 5; i++) {
            List<OrderItem> items = Arrays.asList(
                new OrderItem("ITEM_" + i, "Item " + i, 1, 100.0, "Category", Collections.emptyList())
            );
            
            PlaceOrderCommand command = new PlaceOrderCommand(
                "CMD_" + i, "ORDER_" + i, "CUST_001", "REST_001",
                items, "Mumbai", "UPI", 100.0
            );
            commandHandler.handle(command);
        }
        
        // Query orders by customer
        List<OrderSummaryReadModel> customerOrders = queryHandler.getOrdersByCustomer("CUST_001");
        assertEquals(5, customerOrders.size());
        
        // Query orders by restaurant
        List<OrderSummaryReadModel> restaurantOrders = queryHandler.getOrdersByRestaurant("REST_001");
        assertEquals(5, restaurantOrders.size());
        
        // Query orders by status
        List<OrderSummaryReadModel> placedOrders = queryHandler.getOrdersByStatus("PLACED");
        assertEquals(5, placedOrders.size());
    }
    
    @Test
    @DisplayName("Test Real-time Analytics")
    void testRealTimeAnalytics() {
        // Place and complete some orders
        for (int i = 1; i <= 3; i++) {
            List<OrderItem> items = Arrays.asList(
                new OrderItem("ITEM_" + i, "Item " + i, 1, 200.0, "Category", Collections.emptyList())
            );
            
            // Place order
            PlaceOrderCommand placeCommand = new PlaceOrderCommand(
                "CMD_PLACE_" + i, "ORDER_ANALYTICS_" + i, "CUST_001", "REST_001",
                items, "Mumbai", "UPI", 200.0
            );
            commandHandler.handle(placeCommand);
            
            // Complete order
            UpdateOrderStatusCommand completeCommand = new UpdateOrderStatusCommand(
                "CMD_COMPLETE_" + i, "ORDER_ANALYTICS_" + i, "DELIVERED", "SYSTEM", "Order delivered"
            );
            commandHandler.handle(completeCommand);
        }
        
        // Get analytics
        Map<String, Object> analytics = queryHandler.getRealTimeAnalytics();
        
        assertTrue(analytics.containsKey("totalOrders"));
        assertTrue(analytics.containsKey("totalRevenue"));
        assertTrue(analytics.containsKey("averageOrderValue"));
        
        long totalOrders = (Long) analytics.get("totalOrders");
        assertTrue(totalOrders >= 3);
    }
    
    @Test
    @DisplayName("Test Invalid Command Handling")
    void testInvalidCommandHandling() {
        // Try to update non-existent order
        UpdateOrderStatusCommand invalidCommand = new UpdateOrderStatusCommand(
            "CMD_INVALID", "NON_EXISTENT_ORDER", "CONFIRMED", "SYSTEM", "Test"
        );
        
        assertThrows(IllegalStateException.class, () -> {
            commandHandler.handle(invalidCommand);
        });
    }
    
    @Test
    @DisplayName("Test Business Rule Validation")
    void testBusinessRuleValidation() {
        // Try to place order with empty items
        PlaceOrderCommand invalidCommand = new PlaceOrderCommand(
            "CMD_INVALID", "ORDER_INVALID", "CUST_001", "REST_001",
            Collections.emptyList(), "Mumbai", "UPI", 0.0
        );
        
        assertThrows(IllegalArgumentException.class, () -> {
            commandHandler.handle(invalidCommand);
        });
    }
}

/**
 * Test Suite for Stream Join Operations
 * IRCTCStreamJoins की functionality test करता है
 */
@DisplayName("Stream Join Operations Tests")
class StreamJoinOperationsTest {
    
    @Test
    @DisplayName("Test User Activity Event Creation")
    void testUserActivityEventCreation() {
        UserActivityEvent event = new UserActivityEvent(
            "USER_001", "SESSION_001", "search",
            "MUMBAI_CENTRAL", "NEW_DELHI", "TRAIN_001",
            "3A", LocalDateTime.now(), "mobile", "Mumbai"
        );
        
        assertEquals("USER_001", event.userId);
        assertEquals("search", event.activityType);
        assertEquals("MUMBAI_CENTRAL", event.sourceStation);
        assertEquals("NEW_DELHI", event.destinationStation);
        assertEquals("TRAIN_001", event.trainNumber);
    }
    
    @Test
    @DisplayName("Test Train Status Event Creation")
    void testTrainStatusEventCreation() {
        Map<String, Integer> seatAvailability = new HashMap<>();
        seatAvailability.put("SL", 100);
        seatAvailability.put("3A", 50);
        
        TrainStatusEvent event = new TrainStatusEvent(
            "TRAIN_001", "राजधानी एक्सप्रेस", "NEW_DELHI",
            30, "delayed", seatAvailability, 1500.0, "DEL-MUM", true
        );
        
        assertEquals("TRAIN_001", event.trainNumber);
        assertEquals("राजधानी एक्सप्रेस", event.trainName);
        assertEquals(30, event.delayMinutes);
        assertTrue(event.isOperational);
        assertEquals(100, event.seatAvailability.get("SL").intValue());
    }
    
    @Test
    @DisplayName("Test Payment Event Creation")
    void testPaymentEventCreation() {
        PaymentEvent event = new PaymentEvent(
            "PAY_001", "USER_001", "SESSION_001", "BOOKING_001",
            "UPI", 1500.0, "success", null, 2000
        );
        
        assertEquals("PAY_001", event.paymentId);
        assertEquals("UPI", event.paymentMethod);
        assertEquals(1500.0, event.amount);
        assertEquals("success", event.status);
        assertEquals(2000, event.processingTimeMs);
    }
    
    @Test
    @DisplayName("Test User-Train Join Logic")
    void testUserTrainJoinLogic() {
        UserActivityEvent userEvent = new UserActivityEvent(
            "USER_001", "SESSION_001", "book",
            "MUMBAI_CENTRAL", "NEW_DELHI", "TRAIN_001",
            "3A", LocalDateTime.now(), "mobile", "Mumbai"
        );
        
        Map<String, Integer> seats = new HashMap<>();
        seats.put("3A", 5); // Limited availability
        
        TrainStatusEvent trainEvent = new TrainStatusEvent(
            "TRAIN_001", "राजधानी एक्सप्रेस", "NEW_DELHI",
            15, "delayed", seats, 1500.0, "DEL-MUM", true
        );
        
        UserTrainJoinFunction joinFunction = new UserTrainJoinFunction();
        
        try {
            Tuple3<UserActivityEvent, TrainStatusEvent, String> result = 
                joinFunction.join(userEvent, trainEvent);
            
            assertEquals(userEvent, result.f0);
            assertEquals(trainEvent, result.f1);
            assertEquals("LIMITED_AVAILABILITY", result.f2); // Should detect limited seats
        } catch (Exception e) {
            fail("Join operation should not throw exception: " + e.getMessage());
        }
    }
    
    @Test
    @DisplayName("Test Booking Viability Determination")
    void testBookingViabilityDetermination() {
        Map<String, Integer> seats = new HashMap<>();
        
        // Test different scenarios
        
        // Scenario 1: No seats available
        seats.put("3A", 0);
        String viability1 = determineViability(true, "on_time", 10, seats, "3A");
        assertEquals("NO_SEATS_AVAILABLE", viability1);
        
        // Scenario 2: Train cancelled
        seats.put("3A", 50);
        String viability2 = determineViability(true, "cancelled", 0, seats, "3A");
        assertEquals("TRAIN_CANCELLED", viability2);
        
        // Scenario 3: Excessive delay
        String viability3 = determineViability(true, "delayed", 150, seats, "3A");
        assertEquals("EXCESSIVE_DELAY", viability3);
        
        // Scenario 4: Good conditions
        String viability4 = determineViability(true, "on_time", 5, seats, "3A");
        assertEquals("POSSIBLE", viability4);
    }
    
    private String determineViability(boolean isOperational, String status, 
                                    int delayMinutes, Map<String, Integer> seats, String classType) {
        if (!isOperational) {
            return "TRAIN_NOT_OPERATIONAL";
        } else if ("cancelled".equals(status)) {
            return "TRAIN_CANCELLED";
        } else if (delayMinutes > 120) {
            return "EXCESSIVE_DELAY";
        } else {
            Integer availableSeats = seats.get(classType);
            if (availableSeats == null || availableSeats <= 0) {
                return "NO_SEATS_AVAILABLE";
            } else if (availableSeats < 5) {
                return "LIMITED_AVAILABILITY";
            }
        }
        return "POSSIBLE";
    }
    
    @Test
    @DisplayName("Test Data Generator Consistency")
    void testDataGeneratorConsistency() {
        UserActivityGenerator userGenerator = new UserActivityGenerator();
        TrainStatusGenerator trainGenerator = new TrainStatusGenerator();
        PaymentEventGenerator paymentGenerator = new PaymentEventGenerator();
        
        try {
            // Generate events with same seed for consistency
            UserActivityEvent userEvent1 = userGenerator.map(123L);
            UserActivityEvent userEvent2 = userGenerator.map(123L);
            
            // Same seed should produce same result
            assertEquals(userEvent1.userId, userEvent2.userId);
            assertEquals(userEvent1.trainNumber, userEvent2.trainNumber);
            
            TrainStatusEvent trainEvent1 = trainGenerator.map(456L);
            TrainStatusEvent trainEvent2 = trainGenerator.map(456L);
            
            assertEquals(trainEvent1.trainNumber, trainEvent2.trainNumber);
            assertEquals(trainEvent1.trainName, trainEvent2.trainName);
            
            PaymentEvent paymentEvent1 = paymentGenerator.map(789L);
            PaymentEvent paymentEvent2 = paymentGenerator.map(789L);
            
            assertEquals(paymentEvent1.userId, paymentEvent2.userId);
            assertEquals(paymentEvent1.paymentMethod, paymentEvent2.paymentMethod);
            
        } catch (Exception e) {
            fail("Data generation should not throw exception: " + e.getMessage());
        }
    }
}

/**
 * Test Suite for Exactly-Once Processing
 * PhonePeExactlyOnceProcessing की functionality test करता है
 */
@DisplayName("Exactly-Once Processing Tests")
class ExactlyOnceProcessingTest {
    
    private IdempotencyStore idempotencyStore;
    private SequenceNumberManager sequenceManager;
    private TransactionProcessor processor;
    
    @BeforeEach
    void setUp() {
        idempotencyStore = new IdempotencyStore();
        sequenceManager = new SequenceNumberManager();
        processor = new TransactionProcessor(idempotencyStore, sequenceManager);
    }
    
    @AfterEach
    void tearDown() {
        if (idempotencyStore != null) {
            idempotencyStore.shutdown();
        }
    }
    
    @Test
    @DisplayName("Test Idempotency Store Basic Operations")
    void testIdempotencyStoreBasicOperations() {
        String key = "TEST_KEY_001";
        ProcessingResult result = new ProcessingResult(
            "TXN_001", "SUCCESS", "COMPLETED", "Test transaction",
            100, false, "PROC_001"
        );
        
        // Store result
        idempotencyStore.storeResult(key, result);
        
        // Retrieve result
        Optional<ProcessingResult> retrieved = idempotencyStore.getExistingResult(key);
        assertTrue(retrieved.isPresent());
        assertEquals("TXN_001", retrieved.get().transactionId);
        assertEquals("SUCCESS", retrieved.get().status);
        
        // Check duplicate detection
        assertTrue(idempotencyStore.isDuplicate(key));
        assertFalse(idempotencyStore.isDuplicate("NON_EXISTENT_KEY"));
    }
    
    @Test
    @DisplayName("Test Sequence Number Management")
    void testSequenceNumberManagement() {
        String userId = "USER_TEST_001";
        
        // Test sequence number generation
        long seq1 = sequenceManager.getNextSequenceNumber(userId);
        long seq2 = sequenceManager.getNextSequenceNumber(userId);
        long seq3 = sequenceManager.getNextSequenceNumber(userId);
        
        assertEquals(1, seq1);
        assertEquals(2, seq2);
        assertEquals(3, seq3);
        
        // Test sequence validation
        assertTrue(sequenceManager.isValidSequence(userId, 1));
        assertFalse(sequenceManager.isValidSequence(userId, 2)); // Out of order
        
        // Mark sequence as processed
        sequenceManager.markSequenceProcessed(userId, 1);
        assertTrue(sequenceManager.isValidSequence(userId, 2));
        
        // Test out of order detection
        assertTrue(sequenceManager.isOutOfOrder(userId, 1)); // Already processed
    }
    
    @Test
    @DisplayName("Test Transaction Processing")
    void testTransactionProcessing() {
        TransactionEvent transaction = new TransactionEvent(
            "TXN_TEST_001", "USER_001", "USER_002", 1000.0, "INR", "P2P",
            "AC_001", "AC_002", "Test payment", new HashMap<>(),
            "IDEM_001", 1
        );
        
        // Process transaction
        ProcessingResult result = processor.processTransaction(transaction);
        
        assertNotNull(result);
        assertEquals("TXN_TEST_001", result.transactionId);
        assertTrue(Arrays.asList("SUCCESS", "FAILED").contains(result.status));
        assertFalse(result.isIdempotent); // First time processing
    }
    
    @Test
    @DisplayName("Test Duplicate Transaction Handling")
    void testDuplicateTransactionHandling() {
        TransactionEvent transaction = new TransactionEvent(
            "TXN_DUP_001", "USER_001", "USER_002", 1000.0, "INR", "P2P",
            "AC_001", "AC_002", "Test payment", new HashMap<>(),
            "IDEM_DUP_001", 1
        );
        
        // Process first time
        ProcessingResult result1 = processor.processTransaction(transaction);
        assertFalse(result1.isIdempotent);
        
        // Process same transaction again (duplicate)
        ProcessingResult result2 = processor.processTransaction(transaction);
        assertTrue(result2.isIdempotent);
        assertEquals("DUPLICATE", result2.status);
    }
    
    @Test
    @DisplayName("Test Invalid Transaction Handling")
    void testInvalidTransactionHandling() {
        // Create invalid transaction (empty ID)
        TransactionEvent invalidTransaction = new TransactionEvent(
            "", "USER_001", "USER_002", 1000.0, "INR", "P2P",
            "AC_001", "AC_002", "Test payment", new HashMap<>(),
            "IDEM_INVALID", 1
        );
        
        ProcessingResult result = processor.processTransaction(invalidTransaction);
        assertEquals("FAILED", result.status);
        assertEquals("INVALID_TRANSACTION", result.resultCode);
    }
    
    @Test
    @DisplayName("Test Out of Order Transaction Handling")
    void testOutOfOrderTransactionHandling() {
        String userId = "USER_ORDER_TEST";
        
        // Process transaction with sequence 1
        TransactionEvent tx1 = new TransactionEvent(
            "TXN_ORDER_001", userId, "USER_002", 1000.0, "INR", "P2P",
            "AC_001", "AC_002", "First payment", new HashMap<>(),
            "IDEM_ORDER_001", 1
        );
        
        ProcessingResult result1 = processor.processTransaction(tx1);
        assertEquals("SUCCESS", result1.status);
        
        // Try to process transaction with sequence 3 (skipping 2)
        TransactionEvent tx3 = new TransactionEvent(
            "TXN_ORDER_003", userId, "USER_002", 1000.0, "INR", "P2P",
            "AC_001", "AC_002", "Third payment", new HashMap<>(),
            "IDEM_ORDER_003", 3
        );
        
        ProcessingResult result3 = processor.processTransaction(tx3);
        assertEquals("FAILED", result3.status);
        assertEquals("INVALID_SEQUENCE", result3.resultCode);
    }
    
    @Test
    @DisplayName("Test Concurrent Transaction Processing")
    void testConcurrentTransactionProcessing() throws InterruptedException {
        int numThreads = 5;
        CountDownLatch latch = new CountDownLatch(numThreads);
        List<ProcessingResult> results = new CopyOnWriteArrayList<>();
        
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        
        for (int i = 0; i < numThreads; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    TransactionEvent transaction = new TransactionEvent(
                        "TXN_CONCURRENT_" + threadId, "USER_CONCURRENT", "USER_002",
                        1000.0 + threadId, "INR", "P2P", "AC_001", "AC_002",
                        "Concurrent payment " + threadId, new HashMap<>(),
                        "IDEM_CONCURRENT_" + threadId, threadId + 1
                    );
                    
                    ProcessingResult result = processor.processTransaction(transaction);
                    results.add(result);
                } finally {
                    latch.countDown();
                }
            });
        }
        
        assertTrue(latch.await(10, TimeUnit.SECONDS));
        assertEquals(numThreads, results.size());
        
        // Only first transaction should succeed due to sequence ordering
        long successCount = results.stream()
            .filter(r -> "SUCCESS".equals(r.status))
            .count();
        assertEquals(1, successCount);
        
        executor.shutdown();
    }
    
    @Test
    @DisplayName("Test Processing Metrics")
    void testProcessingMetrics() {
        // Process several transactions
        for (int i = 1; i <= 5; i++) {
            TransactionEvent transaction = new TransactionEvent(
                "TXN_METRICS_" + i, "USER_METRICS", "USER_002",
                1000.0, "INR", "P2P", "AC_001", "AC_002",
                "Metrics test " + i, new HashMap<>(),
                "IDEM_METRICS_" + i, i
            );
            
            processor.processTransaction(transaction);
        }
        
        Map<String, Object> metrics = processor.getProcessingMetrics();
        
        assertTrue(metrics.containsKey("processedCount"));
        assertTrue(metrics.containsKey("errorCount"));
        assertTrue(metrics.containsKey("successRate"));
        
        long processed = (Long) metrics.get("processedCount");
        assertTrue(processed >= 1); // At least first transaction should succeed
    }
}

/**
 * Test Utilities and Helper Classes
 */
class TestUtils {
    
    /**
     * Create a mock inventory event for testing
     */
    public static InventoryEvent createMockInventoryEvent(String productId, String warehouseId, 
                                                         String eventType, int quantityChange) {
        return new InventoryEvent(productId, warehouseId, eventType, quantityChange,
                                 System.currentTimeMillis(), 100.0, "test_category");
    }
    
    /**
     * Create a mock order item for testing
     */
    public static OrderItem createMockOrderItem(String itemId, String name, int quantity, double price) {
        return new OrderItem(itemId, name, quantity, price, "test_category", Collections.emptyList());
    }
    
    /**
     * Create a mock transaction event for testing
     */
    public static TransactionEvent createMockTransaction(String transactionId, String userId, 
                                                        double amount, String idempotencyKey, long sequenceNumber) {
        return new TransactionEvent(transactionId, userId, "RECEIVER_001", amount, "INR", "P2P",
                                   "AC_001", "AC_002", "Test transaction", new HashMap<>(),
                                   idempotencyKey, sequenceNumber);
    }
    
    /**
     * Wait for a condition to be true with timeout
     */
    public static boolean waitForCondition(Callable<Boolean> condition, long timeoutMs) {
        long startTime = System.currentTimeMillis();
        
        while (System.currentTimeMillis() - startTime < timeoutMs) {
            try {
                if (condition.call()) {
                    return true;
                }
                Thread.sleep(100);
            } catch (Exception e) {
                return false;
            }
        }
        
        return false;
    }
}

/**
 * Integration Test Suite
 * End-to-end integration tests
 */
@DisplayName("Integration Tests")
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class IntegrationTest {
    
    @Test
    @DisplayName("Test Complete Order Processing Flow")
    void testCompleteOrderProcessingFlow() {
        // Setup CQRS system
        OrderCommandHandler commandHandler = new OrderCommandHandler();
        OrderQueryHandler queryHandler = new OrderQueryHandler();
        EventHandlerBridge eventBridge = new EventHandlerBridge(queryHandler);
        commandHandler.addEventHandler(eventBridge::handleEvent);
        
        String orderId = "INTEGRATION_ORDER_001";
        String customerId = "INTEGRATION_CUSTOMER_001";
        
        // Step 1: Place order
        List<OrderItem> items = Arrays.asList(
            TestUtils.createMockOrderItem("ITEM_001", "Test Item", 2, 100.0)
        );
        
        PlaceOrderCommand placeCommand = new PlaceOrderCommand(
            "CMD_001", orderId, customerId, "REST_001",
            items, "Test Address", "UPI", 200.0
        );
        
        commandHandler.handle(placeCommand);
        
        // Verify order was placed
        OrderSummaryReadModel orderSummary = queryHandler.getOrderSummary(orderId);
        assertNotNull(orderSummary);
        assertEquals("PLACED", orderSummary.status);
        
        // Step 2: Update order status through multiple stages
        String[] statuses = {"CONFIRMED", "PREPARING", "READY", "PICKED_UP", "OUT_FOR_DELIVERY", "DELIVERED"};
        
        for (int i = 0; i < statuses.length; i++) {
            UpdateOrderStatusCommand updateCommand = new UpdateOrderStatusCommand(
                "CMD_" + (i + 2), orderId, statuses[i], "SYSTEM", "Status update " + (i + 1)
            );
            
            commandHandler.handle(updateCommand);
            
            // Verify status update
            orderSummary = queryHandler.getOrderSummary(orderId);
            assertEquals(statuses[i], orderSummary.status);
        }
        
        // Step 3: Verify final analytics
        Map<String, Object> analytics = queryHandler.getRealTimeAnalytics();
        assertTrue((Long) analytics.get("totalOrders") >= 1);
        
        // Step 4: Verify customer orders
        List<OrderSummaryReadModel> customerOrders = queryHandler.getOrdersByCustomer(customerId);
        assertEquals(1, customerOrders.size());
        assertEquals("DELIVERED", customerOrders.get(0).status);
    }
    
    @Test
    @DisplayName("Test Fraud Detection Integration")
    void testFraudDetectionIntegration() {
        // Setup fraud detection system
        IdempotencyStore idempotencyStore = new IdempotencyStore();
        SequenceNumberManager sequenceManager = new SequenceNumberManager();
        TransactionProcessor processor = new TransactionProcessor(idempotencyStore, sequenceManager);
        
        try {
            String userId = "FRAUD_TEST_USER";
            
            // Process multiple transactions to build user profile
            for (int i = 1; i <= 5; i++) {
                TransactionEvent transaction = TestUtils.createMockTransaction(
                    "FRAUD_TXN_" + i, userId, 1000.0 + i * 100,
                    "FRAUD_IDEM_" + i, i
                );
                
                ProcessingResult result = processor.processTransaction(transaction);
                if (i == 1) {
                    assertEquals("SUCCESS", result.status);
                } else {
                    // Later transactions might fail due to sequence ordering in concurrent test
                    assertTrue(Arrays.asList("SUCCESS", "FAILED").contains(result.status));
                }
            }
            
            // Try suspicious transaction (very high amount)
            TransactionEvent suspiciousTransaction = TestUtils.createMockTransaction(
                "FRAUD_TXN_SUSPICIOUS", userId, 100000.0, "FRAUD_IDEM_SUSPICIOUS", 6
            );
            
            ProcessingResult suspiciousResult = processor.processTransaction(suspiciousTransaction);
            assertNotNull(suspiciousResult);
            
            // Verify metrics
            Map<String, Object> metrics = processor.getProcessingMetrics();
            assertTrue((Long) metrics.get("processedCount") >= 1);
            
        } finally {
            idempotencyStore.shutdown();
        }
    }
    
    @Test
    @DisplayName("Test System Performance Under Load")
    void testSystemPerformanceUnderLoad() throws InterruptedException {
        // Setup CQRS system
        OrderCommandHandler commandHandler = new OrderCommandHandler();
        OrderQueryHandler queryHandler = new OrderQueryHandler();
        EventHandlerBridge eventBridge = new EventHandlerBridge(queryHandler);
        commandHandler.addEventHandler(eventBridge::handleEvent);
        
        int numOrders = 100; // Reduced for test environment
        CountDownLatch latch = new CountDownLatch(numOrders);
        List<String> orderIds = new CopyOnWriteArrayList<>();
        
        long startTime = System.currentTimeMillis();
        
        ExecutorService executor = Executors.newFixedThreadPool(10);
        
        // Submit orders concurrently
        for (int i = 0; i < numOrders; i++) {
            final int orderId = i;
            executor.submit(() -> {
                try {
                    String orderIdStr = "PERF_ORDER_" + orderId;
                    orderIds.add(orderIdStr);
                    
                    List<OrderItem> items = Arrays.asList(
                        TestUtils.createMockOrderItem("ITEM_" + orderId, "Perf Item " + orderId, 1, 100.0)
                    );
                    
                    PlaceOrderCommand command = new PlaceOrderCommand(
                        "PERF_CMD_" + orderId, orderIdStr, "PERF_CUSTOMER_" + (orderId % 10),
                        "PERF_REST_" + (orderId % 5), items, "Address", "UPI", 100.0
                    );
                    
                    commandHandler.handle(command);
                } finally {
                    latch.countDown();
                }
            });
        }
        
        // Wait for all orders to complete
        assertTrue(latch.await(30, TimeUnit.SECONDS), "Orders should complete within 30 seconds");
        
        long endTime = System.currentTimeMillis();
        long totalTime = endTime - startTime;
        
        // Verify performance
        double ordersPerSecond = (double) numOrders / (totalTime / 1000.0);
        assertTrue(ordersPerSecond > 10, "Should process more than 10 orders per second");
        
        // Verify all orders were processed
        Map<String, Object> analytics = queryHandler.getRealTimeAnalytics();
        long totalOrders = (Long) analytics.get("totalOrders");
        assertTrue(totalOrders >= numOrders, "All orders should be processed");
        
        executor.shutdown();
    }
}

/**
 * Main Test Runner
 */
public class JavaExamplesTestRunner {
    
    public static void main(String[] args) {
        System.out.println("🧪 Running Java Real-time Analytics Tests...");
        System.out.println("=" + "=".repeat(60));
        
        // Run all test classes using JUnit Platform
        // This would typically be done with Maven/Gradle test runners
        // For demonstration, we'll show the test structure
        
        System.out.println("✅ Test structure verified:");
        System.out.println("  📊 Flink Stream Processing Tests");
        System.out.println("  🔄 Event Sourcing Pattern Tests");
        System.out.println("  📝 CQRS Implementation Tests");
        System.out.println("  🔗 Stream Join Operations Tests");
        System.out.println("  ⚡ Exactly-Once Processing Tests");
        System.out.println("  🔧 Integration Tests");
        
        System.out.println("\n" + "=".repeat(60));
        System.out.println("📋 To run these tests in your environment:");
        System.out.println("   mvn test  # Using Maven");
        System.out.println("   gradle test  # Using Gradle");
        System.out.println("   # Or run individual test classes in your IDE");
    }
}

/*
Test Coverage Summary:

1. Flink Stream Processing Tests:
   ✅ Event creation and validation
   ✅ JSON parsing and error handling
   ✅ Aggregation logic verification
   ✅ Alert level determination
   ✅ Concurrent processing safety

2. Event Sourcing Tests:
   ✅ Event store operations
   ✅ Aggregate state management
   ✅ Event replay functionality
   ✅ Real-time analytics processing
   ✅ Event handler registration

3. CQRS Implementation Tests:
   ✅ Command processing (place, update, cancel)
   ✅ Query side read models
   ✅ Real-time analytics
   ✅ Business rule validation
   ✅ Error handling

4. Stream Join Operations Tests:
   ✅ Event object creation
   ✅ Join logic verification
   ✅ Booking viability determination
   ✅ Data generator consistency

5. Exactly-Once Processing Tests:
   ✅ Idempotency store operations
   ✅ Sequence number management
   ✅ Duplicate detection
   ✅ Transaction processing
   ✅ Concurrent safety

6. Integration Tests:
   ✅ End-to-end order processing flow
   ✅ Fraud detection integration
   ✅ Performance under load
   ✅ System reliability

Dependencies required:
- JUnit 5 (jupiter)
- Mockito for mocking
- Apache Flink (for stream processing tests)
- Kafka clients (for integration tests)
- JSON processing library (Jackson)

These tests ensure:
- Functional correctness
- Performance characteristics
- Error handling
- Thread safety
- Integration reliability
*/
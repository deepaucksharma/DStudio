/*
 * CQRS (Command Query Responsibility Segregation) Implementation
 * Episode 43: Real-time Analytics at Scale
 * 
 * Complete CQRS pattern with real-time read models
 * Use Case: Zomato order management with separate read/write models
 */

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import java.util.function.Consumer;

/**
 * Zomato CQRS Implementation
 * 
 * Write side: Order commands (place, update, cancel)
 * Read side: Order queries (search, analytics, reporting)
 * 
 * यह pattern read और write operations को completely separate करता है
 */
public class ZomatoCQRSSystem {
    
    /**
     * Base Command Interface
     * सभी commands का base interface
     */
    public interface Command {
        String getCommandId();
        String getAggregateId();
        String getCommandType();
        long getTimestamp();
    }
    
    /**
     * Order Commands - Write Side
     */
    public static class PlaceOrderCommand implements Command {
        public final String commandId;
        public final String orderId;
        public final String customerId;
        public final String restaurantId;
        public final List<OrderItem> items;
        public final String deliveryAddress;
        public final String paymentMethod;
        public final double totalAmount;
        public final long timestamp;
        
        public PlaceOrderCommand(String commandId, String orderId, String customerId, 
                               String restaurantId, List<OrderItem> items, String deliveryAddress,
                               String paymentMethod, double totalAmount) {
            this.commandId = commandId;
            this.orderId = orderId;
            this.customerId = customerId;
            this.restaurantId = restaurantId;
            this.items = new ArrayList<>(items);
            this.deliveryAddress = deliveryAddress;
            this.paymentMethod = paymentMethod;
            this.totalAmount = totalAmount;
            this.timestamp = System.currentTimeMillis();
        }
        
        @Override public String getCommandId() { return commandId; }
        @Override public String getAggregateId() { return orderId; }
        @Override public String getCommandType() { return "PlaceOrder"; }
        @Override public long getTimestamp() { return timestamp; }
    }
    
    public static class UpdateOrderStatusCommand implements Command {
        public final String commandId;
        public final String orderId;
        public final String newStatus;
        public final String updatedBy;
        public final String reason;
        public final long timestamp;
        
        public UpdateOrderStatusCommand(String commandId, String orderId, String newStatus, 
                                      String updatedBy, String reason) {
            this.commandId = commandId;
            this.orderId = orderId;
            this.newStatus = newStatus;
            this.updatedBy = updatedBy;
            this.reason = reason;
            this.timestamp = System.currentTimeMillis();
        }
        
        @Override public String getCommandId() { return commandId; }
        @Override public String getAggregateId() { return orderId; }
        @Override public String getCommandType() { return "UpdateOrderStatus"; }
        @Override public long getTimestamp() { return timestamp; }
    }
    
    public static class CancelOrderCommand implements Command {
        public final String commandId;
        public final String orderId;
        public final String cancellationReason;
        public final String cancelledBy;
        public final double refundAmount;
        public final long timestamp;
        
        public CancelOrderCommand(String commandId, String orderId, String cancellationReason,
                                String cancelledBy, double refundAmount) {
            this.commandId = commandId;
            this.orderId = orderId;
            this.cancellationReason = cancellationReason;
            this.cancelledBy = cancelledBy;
            this.refundAmount = refundAmount;
            this.timestamp = System.currentTimeMillis();
        }
        
        @Override public String getCommandId() { return commandId; }
        @Override public String getAggregateId() { return orderId; }
        @Override public String getCommandType() { return "CancelOrder"; }
        @Override public long getTimestamp() { return timestamp; }
    }
    
    /**
     * Order Item
     */
    public static class OrderItem {
        public final String itemId;
        public final String itemName;
        public final int quantity;
        public final double price;
        public final String category;
        public final List<String> customizations;
        
        public OrderItem(String itemId, String itemName, int quantity, double price, 
                        String category, List<String> customizations) {
            this.itemId = itemId;
            this.itemName = itemName;
            this.quantity = quantity;
            this.price = price;
            this.category = category;
            this.customizations = new ArrayList<>(customizations);
        }
        
        public double getTotalPrice() {
            return quantity * price;
        }
        
        @Override
        public String toString() {
            return String.format("%s x%d @%.2f", itemName, quantity, price);
        }
    }
    
    /**
     * Domain Events - Generated by Write Side
     */
    public static abstract class DomainEvent {
        public final String eventId;
        public final String aggregateId;
        public final String eventType;
        public final long timestamp;
        
        public DomainEvent(String eventId, String aggregateId, String eventType) {
            this.eventId = eventId;
            this.aggregateId = aggregateId;
            this.eventType = eventType;
            this.timestamp = System.currentTimeMillis();
        }
    }
    
    public static class OrderPlacedEvent extends DomainEvent {
        public final String customerId;
        public final String restaurantId;
        public final List<OrderItem> items;
        public final String deliveryAddress;
        public final String paymentMethod;
        public final double totalAmount;
        
        public OrderPlacedEvent(String eventId, String orderId, String customerId, String restaurantId,
                              List<OrderItem> items, String deliveryAddress, String paymentMethod, double totalAmount) {
            super(eventId, orderId, "OrderPlaced");
            this.customerId = customerId;
            this.restaurantId = restaurantId;
            this.items = new ArrayList<>(items);
            this.deliveryAddress = deliveryAddress;
            this.paymentMethod = paymentMethod;
            this.totalAmount = totalAmount;
        }
    }
    
    public static class OrderStatusUpdatedEvent extends DomainEvent {
        public final String previousStatus;
        public final String newStatus;
        public final String updatedBy;
        public final String reason;
        
        public OrderStatusUpdatedEvent(String eventId, String orderId, String previousStatus, 
                                     String newStatus, String updatedBy, String reason) {
            super(eventId, orderId, "OrderStatusUpdated");
            this.previousStatus = previousStatus;
            this.newStatus = newStatus;
            this.updatedBy = updatedBy;
            this.reason = reason;
        }
    }
    
    public static class OrderCancelledEvent extends DomainEvent {
        public final String cancellationReason;
        public final String cancelledBy;
        public final double refundAmount;
        
        public OrderCancelledEvent(String eventId, String orderId, String cancellationReason,
                                 String cancelledBy, double refundAmount) {
            super(eventId, orderId, "OrderCancelled");
            this.cancellationReason = cancellationReason;
            this.cancelledBy = cancelledBy;
            this.refundAmount = refundAmount;
        }
    }
    
    /**
     * Write Side - Order Aggregate
     * Business logic और state management
     */
    public static class OrderAggregate {
        public final String orderId;
        public String customerId;
        public String restaurantId;
        public List<OrderItem> items;
        public String status;
        public String deliveryAddress;
        public String paymentMethod;
        public double totalAmount;
        public LocalDateTime placedAt;
        public LocalDateTime lastUpdatedAt;
        public List<String> statusHistory;
        public String cancellationReason;
        
        private final List<DomainEvent> uncommittedEvents = new ArrayList<>();
        
        public OrderAggregate(String orderId) {
            this.orderId = orderId;
            this.items = new ArrayList<>();
            this.statusHistory = new ArrayList<>();
        }
        
        // Command Handlers
        public void handle(PlaceOrderCommand command) {
            if (this.status != null) {
                throw new IllegalStateException("Order already exists: " + orderId);
            }
            
            // Business validation
            if (command.items.isEmpty()) {
                throw new IllegalArgumentException("Order must have at least one item");
            }
            
            if (command.totalAmount <= 0) {
                throw new IllegalArgumentException("Order total must be positive");
            }
            
            // Apply changes
            this.customerId = command.customerId;
            this.restaurantId = command.restaurantId;
            this.items = new ArrayList<>(command.items);
            this.deliveryAddress = command.deliveryAddress;
            this.paymentMethod = command.paymentMethod;
            this.totalAmount = command.totalAmount;
            this.status = "PLACED";
            this.placedAt = LocalDateTime.now();
            this.lastUpdatedAt = LocalDateTime.now();
            this.statusHistory.add("PLACED");
            
            // Generate event
            addEvent(new OrderPlacedEvent(
                UUID.randomUUID().toString(), orderId, customerId, restaurantId,
                items, deliveryAddress, paymentMethod, totalAmount
            ));
            
            System.out.println("📝 Order placed: " + orderId + " for customer: " + customerId);
        }
        
        public void handle(UpdateOrderStatusCommand command) {
            if (this.status == null) {
                throw new IllegalStateException("Order does not exist: " + orderId);
            }
            
            if ("CANCELLED".equals(this.status)) {
                throw new IllegalStateException("Cannot update cancelled order: " + orderId);
            }
            
            if ("DELIVERED".equals(this.status)) {
                throw new IllegalStateException("Cannot update delivered order: " + orderId);
            }
            
            // Validate status transition
            if (!isValidStatusTransition(this.status, command.newStatus)) {
                throw new IllegalArgumentException("Invalid status transition: " + this.status + " -> " + command.newStatus);
            }
            
            String previousStatus = this.status;
            this.status = command.newStatus;
            this.lastUpdatedAt = LocalDateTime.now();
            this.statusHistory.add(command.newStatus);
            
            // Generate event
            addEvent(new OrderStatusUpdatedEvent(
                UUID.randomUUID().toString(), orderId, previousStatus, 
                command.newStatus, command.updatedBy, command.reason
            ));
            
            System.out.println("🔄 Order status updated: " + orderId + " -> " + command.newStatus);
        }
        
        public void handle(CancelOrderCommand command) {
            if (this.status == null) {
                throw new IllegalStateException("Order does not exist: " + orderId);
            }
            
            if ("CANCELLED".equals(this.status)) {
                throw new IllegalStateException("Order already cancelled: " + orderId);
            }
            
            if ("DELIVERED".equals(this.status)) {
                throw new IllegalStateException("Cannot cancel delivered order: " + orderId);
            }
            
            this.status = "CANCELLED";
            this.cancellationReason = command.cancellationReason;
            this.lastUpdatedAt = LocalDateTime.now();
            this.statusHistory.add("CANCELLED");
            
            // Generate event
            addEvent(new OrderCancelledEvent(
                UUID.randomUUID().toString(), orderId, command.cancellationReason,
                command.cancelledBy, command.refundAmount
            ));
            
            System.out.println("❌ Order cancelled: " + orderId + " - " + command.cancellationReason);
        }
        
        private boolean isValidStatusTransition(String currentStatus, String newStatus) {
            Map<String, List<String>> validTransitions = Map.of(
                "PLACED", Arrays.asList("CONFIRMED", "CANCELLED"),
                "CONFIRMED", Arrays.asList("PREPARING", "CANCELLED"),
                "PREPARING", Arrays.asList("READY", "CANCELLED"),
                "READY", Arrays.asList("PICKED_UP", "CANCELLED"),
                "PICKED_UP", Arrays.asList("OUT_FOR_DELIVERY"),
                "OUT_FOR_DELIVERY", Arrays.asList("DELIVERED")
            );
            
            return validTransitions.getOrDefault(currentStatus, Collections.emptyList()).contains(newStatus);
        }
        
        private void addEvent(DomainEvent event) {
            uncommittedEvents.add(event);
        }
        
        public List<DomainEvent> getUncommittedEvents() {
            return new ArrayList<>(uncommittedEvents);
        }
        
        public void markEventsAsCommitted() {
            uncommittedEvents.clear();
        }
        
        @Override
        public String toString() {
            return String.format("Order{id='%s', customer='%s', restaurant='%s', status='%s', amount=%.2f}",
                               orderId, customerId, restaurantId, status, totalAmount);
        }
    }
    
    /**
     * Command Handler - Write Side
     */
    public static class OrderCommandHandler {
        private final Map<String, OrderAggregate> aggregates = new ConcurrentHashMap<>();
        private final List<Consumer<DomainEvent>> eventHandlers = new CopyOnWriteArrayList<>();
        
        public void handle(Command command) {
            OrderAggregate aggregate = aggregates.computeIfAbsent(
                command.getAggregateId(), 
                id -> new OrderAggregate(id)
            );
            
            // Dispatch to appropriate handler
            if (command instanceof PlaceOrderCommand) {
                aggregate.handle((PlaceOrderCommand) command);
            } else if (command instanceof UpdateOrderStatusCommand) {
                aggregate.handle((UpdateOrderStatusCommand) command);
            } else if (command instanceof CancelOrderCommand) {
                aggregate.handle((CancelOrderCommand) command);
            } else {
                throw new UnsupportedOperationException("Unknown command type: " + command.getCommandType());
            }
            
            // Publish events
            List<DomainEvent> events = aggregate.getUncommittedEvents();
            for (DomainEvent event : events) {
                publishEvent(event);
            }
            aggregate.markEventsAsCommitted();
        }
        
        private void publishEvent(DomainEvent event) {
            eventHandlers.forEach(handler -> {
                try {
                    handler.accept(event);
                } catch (Exception e) {
                    System.err.println("Error in event handler: " + e.getMessage());
                }
            });
        }
        
        public void addEventHandler(Consumer<DomainEvent> handler) {
            eventHandlers.add(handler);
        }
        
        public OrderAggregate getAggregate(String orderId) {
            return aggregates.get(orderId);
        }
        
        public Collection<OrderAggregate> getAllAggregates() {
            return aggregates.values();
        }
    }
    
    /**
     * Read Models - Query Side
     */
    public static class OrderSummaryReadModel {
        public final String orderId;
        public final String customerId;
        public final String restaurantId;
        public final String restaurantName;
        public final String status;
        public final double totalAmount;
        public final int itemCount;
        public final LocalDateTime placedAt;
        public final LocalDateTime lastUpdatedAt;
        public final String deliveryAddress;
        
        public OrderSummaryReadModel(String orderId, String customerId, String restaurantId, 
                                   String restaurantName, String status, double totalAmount, 
                                   int itemCount, LocalDateTime placedAt, LocalDateTime lastUpdatedAt,
                                   String deliveryAddress) {
            this.orderId = orderId;
            this.customerId = customerId;
            this.restaurantId = restaurantId;
            this.restaurantName = restaurantName;
            this.status = status;
            this.totalAmount = totalAmount;
            this.itemCount = itemCount;
            this.placedAt = placedAt;
            this.lastUpdatedAt = lastUpdatedAt;
            this.deliveryAddress = deliveryAddress;
        }
        
        @Override
        public String toString() {
            return String.format("OrderSummary{id='%s', restaurant='%s', status='%s', amount=%.2f, items=%d}",
                               orderId, restaurantName, status, totalAmount, itemCount);
        }
    }
    
    public static class RestaurantAnalyticsReadModel {
        public final String restaurantId;
        public final String restaurantName;
        public int totalOrders;
        public int completedOrders;
        public int cancelledOrders;
        public double totalRevenue;
        public double averageOrderValue;
        public double cancellationRate;
        public Map<String, Integer> popularItems;
        public LocalDateTime lastUpdated;
        
        public RestaurantAnalyticsReadModel(String restaurantId, String restaurantName) {
            this.restaurantId = restaurantId;
            this.restaurantName = restaurantName;
            this.popularItems = new HashMap<>();
            this.lastUpdated = LocalDateTime.now();
        }
        
        public void updateMetrics() {
            if (totalOrders > 0) {
                this.averageOrderValue = totalRevenue / completedOrders;
                this.cancellationRate = (double) cancelledOrders / totalOrders * 100;
            }
            this.lastUpdated = LocalDateTime.now();
        }
        
        @Override
        public String toString() {
            return String.format("RestaurantAnalytics{id='%s', name='%s', orders=%d, revenue=%.2f, cancellationRate=%.1f%%}",
                               restaurantId, restaurantName, totalOrders, totalRevenue, cancellationRate);
        }
    }
    
    public static class CustomerAnalyticsReadModel {
        public final String customerId;
        public int totalOrders;
        public int completedOrders;
        public int cancelledOrders;
        public double totalSpent;
        public double averageOrderValue;
        public Set<String> favoriteRestaurants;
        public Map<String, Integer> orderFrequencyByHour;
        public LocalDateTime lastOrderDate;
        
        public CustomerAnalyticsReadModel(String customerId) {
            this.customerId = customerId;
            this.favoriteRestaurants = new HashSet<>();
            this.orderFrequencyByHour = new HashMap<>();
        }
        
        public void updateMetrics() {
            if (completedOrders > 0) {
                this.averageOrderValue = totalSpent / completedOrders;
            }
        }
        
        @Override
        public String toString() {
            return String.format("CustomerAnalytics{id='%s', orders=%d, spent=%.2f, avgOrder=%.2f}",
                               customerId, totalOrders, totalSpent, averageOrderValue);
        }
    }
    
    /**
     * Query Handlers - Read Side
     */
    public static class OrderQueryHandler {
        private final Map<String, OrderSummaryReadModel> orderSummaries = new ConcurrentHashMap<>();
        private final Map<String, RestaurantAnalyticsReadModel> restaurantAnalytics = new ConcurrentHashMap<>();
        private final Map<String, CustomerAnalyticsReadModel> customerAnalytics = new ConcurrentHashMap<>();
        
        // Restaurants database (simulated)
        private final Map<String, String> restaurantNames = Map.of(
            "REST_001", "दिलीप पवभाजी",
            "REST_002", "सागर रत्न",
            "REST_003", "महाराष्ट्र थाली",
            "REST_004", "मुंबई दर्शन",
            "REST_005", "गुजराती भोजनालय"
        );
        
        public OrderQueryHandler() {
            // Initialize restaurant analytics
            restaurantNames.forEach((id, name) -> 
                restaurantAnalytics.put(id, new RestaurantAnalyticsReadModel(id, name))
            );
        }
        
        // Event Handlers - Build Read Models from Events
        public void on(OrderPlacedEvent event) {
            String restaurantName = restaurantNames.getOrDefault(event.restaurantId, "Unknown Restaurant");
            
            // Update Order Summary
            orderSummaries.put(event.aggregateId, new OrderSummaryReadModel(
                event.aggregateId,
                event.customerId,
                event.restaurantId,
                restaurantName,
                "PLACED",
                event.totalAmount,
                event.items.size(),
                LocalDateTime.now(),
                LocalDateTime.now(),
                event.deliveryAddress
            ));
            
            // Update Restaurant Analytics
            RestaurantAnalyticsReadModel restaurantModel = restaurantAnalytics.get(event.restaurantId);
            if (restaurantModel != null) {
                restaurantModel.totalOrders++;
                
                // Update popular items
                for (OrderItem item : event.items) {
                    restaurantModel.popularItems.put(
                        item.itemName, 
                        restaurantModel.popularItems.getOrDefault(item.itemName, 0) + item.quantity
                    );
                }
                restaurantModel.updateMetrics();
            }
            
            // Update Customer Analytics
            CustomerAnalyticsReadModel customerModel = customerAnalytics.computeIfAbsent(
                event.customerId, 
                id -> new CustomerAnalyticsReadModel(id)
            );
            customerModel.totalOrders++;
            customerModel.favoriteRestaurants.add(event.restaurantId);
            customerModel.lastOrderDate = LocalDateTime.now();
            
            // Track order frequency by hour
            int hour = LocalDateTime.now().getHour();
            customerModel.orderFrequencyByHour.put(
                String.valueOf(hour),
                customerModel.orderFrequencyByHour.getOrDefault(String.valueOf(hour), 0) + 1
            );
            
            customerModel.updateMetrics();
        }
        
        public void on(OrderStatusUpdatedEvent event) {
            OrderSummaryReadModel orderSummary = orderSummaries.get(event.aggregateId);
            if (orderSummary != null) {
                // Create updated model (immutable)
                OrderSummaryReadModel updatedSummary = new OrderSummaryReadModel(
                    orderSummary.orderId,
                    orderSummary.customerId,
                    orderSummary.restaurantId,
                    orderSummary.restaurantName,
                    event.newStatus,
                    orderSummary.totalAmount,
                    orderSummary.itemCount,
                    orderSummary.placedAt,
                    LocalDateTime.now(),
                    orderSummary.deliveryAddress
                );
                
                orderSummaries.put(event.aggregateId, updatedSummary);
                
                // Update analytics if order completed
                if ("DELIVERED".equals(event.newStatus)) {
                    RestaurantAnalyticsReadModel restaurantModel = restaurantAnalytics.get(orderSummary.restaurantId);
                    if (restaurantModel != null) {
                        restaurantModel.completedOrders++;
                        restaurantModel.totalRevenue += orderSummary.totalAmount;
                        restaurantModel.updateMetrics();
                    }
                    
                    CustomerAnalyticsReadModel customerModel = customerAnalytics.get(orderSummary.customerId);
                    if (customerModel != null) {
                        customerModel.completedOrders++;
                        customerModel.totalSpent += orderSummary.totalAmount;
                        customerModel.updateMetrics();
                    }
                }
            }
        }
        
        public void on(OrderCancelledEvent event) {
            OrderSummaryReadModel orderSummary = orderSummaries.get(event.aggregateId);
            if (orderSummary != null) {
                // Update order summary
                OrderSummaryReadModel updatedSummary = new OrderSummaryReadModel(
                    orderSummary.orderId,
                    orderSummary.customerId,
                    orderSummary.restaurantId,
                    orderSummary.restaurantName,
                    "CANCELLED",
                    orderSummary.totalAmount,
                    orderSummary.itemCount,
                    orderSummary.placedAt,
                    LocalDateTime.now(),
                    orderSummary.deliveryAddress
                );
                
                orderSummaries.put(event.aggregateId, updatedSummary);
                
                // Update analytics
                RestaurantAnalyticsReadModel restaurantModel = restaurantAnalytics.get(orderSummary.restaurantId);
                if (restaurantModel != null) {
                    restaurantModel.cancelledOrders++;
                    restaurantModel.updateMetrics();
                }
                
                CustomerAnalyticsReadModel customerModel = customerAnalytics.get(orderSummary.customerId);
                if (customerModel != null) {
                    customerModel.cancelledOrders++;
                    customerModel.updateMetrics();
                }
            }
        }
        
        // Query Methods
        public OrderSummaryReadModel getOrderSummary(String orderId) {
            return orderSummaries.get(orderId);
        }
        
        public List<OrderSummaryReadModel> getOrdersByCustomer(String customerId) {
            return orderSummaries.values().stream()
                                 .filter(order -> order.customerId.equals(customerId))
                                 .sorted((a, b) -> b.placedAt.compareTo(a.placedAt))
                                 .collect(Collectors.toList());
        }
        
        public List<OrderSummaryReadModel> getOrdersByRestaurant(String restaurantId) {
            return orderSummaries.values().stream()
                                 .filter(order -> order.restaurantId.equals(restaurantId))
                                 .sorted((a, b) -> b.placedAt.compareTo(a.placedAt))
                                 .collect(Collectors.toList());
        }
        
        public List<OrderSummaryReadModel> getOrdersByStatus(String status) {
            return orderSummaries.values().stream()
                                 .filter(order -> order.status.equals(status))
                                 .sorted((a, b) -> b.placedAt.compareTo(a.placedAt))
                                 .collect(Collectors.toList());
        }
        
        public RestaurantAnalyticsReadModel getRestaurantAnalytics(String restaurantId) {
            return restaurantAnalytics.get(restaurantId);
        }
        
        public List<RestaurantAnalyticsReadModel> getTopRestaurantsByRevenue(int limit) {
            return restaurantAnalytics.values().stream()
                                     .sorted((a, b) -> Double.compare(b.totalRevenue, a.totalRevenue))
                                     .limit(limit)
                                     .collect(Collectors.toList());
        }
        
        public CustomerAnalyticsReadModel getCustomerAnalytics(String customerId) {
            return customerAnalytics.get(customerId);
        }
        
        public List<CustomerAnalyticsReadModel> getTopCustomersBySpending(int limit) {
            return customerAnalytics.values().stream()
                                   .sorted((a, b) -> Double.compare(b.totalSpent, a.totalSpent))
                                   .limit(limit)
                                   .collect(Collectors.toList());
        }
        
        // Real-time Analytics Queries
        public Map<String, Object> getRealTimeAnalytics() {
            Map<String, Object> analytics = new HashMap<>();
            
            // Overall metrics
            long totalOrders = orderSummaries.size();
            long activeOrders = orderSummaries.values().stream()
                                             .filter(order -> !order.status.equals("DELIVERED") && !order.status.equals("CANCELLED"))
                                             .count();
            
            double totalRevenue = restaurantAnalytics.values().stream()
                                                   .mapToDouble(r -> r.totalRevenue)
                                                   .sum();
            
            analytics.put("totalOrders", totalOrders);
            analytics.put("activeOrders", activeOrders);
            analytics.put("totalRevenue", totalRevenue);
            analytics.put("averageOrderValue", totalRevenue / Math.max(totalOrders, 1));
            
            // Status distribution
            Map<String, Long> statusDistribution = orderSummaries.values().stream()
                                                                 .collect(Collectors.groupingBy(
                                                                     order -> order.status,
                                                                     Collectors.counting()
                                                                 ));
            analytics.put("statusDistribution", statusDistribution);
            
            // Top restaurants
            List<String> topRestaurants = getTopRestaurantsByRevenue(5).stream()
                                                                       .map(r -> r.restaurantName)
                                                                       .collect(Collectors.toList());
            analytics.put("topRestaurants", topRestaurants);
            
            analytics.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            return analytics;
        }
    }
    
    /**
     * Event Handler Bridge
     * Domain events को query handlers तक पहुंचाता है
     */
    public static class EventHandlerBridge {
        private final OrderQueryHandler queryHandler;
        
        public EventHandlerBridge(OrderQueryHandler queryHandler) {
            this.queryHandler = queryHandler;
        }
        
        public void handleEvent(DomainEvent event) {
            switch (event.eventType) {
                case "OrderPlaced":
                    queryHandler.on((OrderPlacedEvent) event);
                    break;
                case "OrderStatusUpdated":
                    queryHandler.on((OrderStatusUpdatedEvent) event);
                    break;
                case "OrderCancelled":
                    queryHandler.on((OrderCancelledEvent) event);
                    break;
            }
        }
    }
    
    /**
     * Main Demo Application
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🍕 Starting Zomato CQRS Demo...");
        
        // Initialize CQRS components
        OrderCommandHandler commandHandler = new OrderCommandHandler();
        OrderQueryHandler queryHandler = new OrderQueryHandler();
        EventHandlerBridge eventBridge = new EventHandlerBridge(queryHandler);
        
        // Wire up event handling
        commandHandler.addEventHandler(eventBridge::handleEvent);
        
        // Simulate order processing
        simulateOrderWorkflow(commandHandler, queryHandler);
        
        // Real-time analytics
        System.out.println("\n📊 === Real-time Analytics ===");
        Map<String, Object> analytics = queryHandler.getRealTimeAnalytics();
        analytics.forEach((key, value) -> System.out.println(key + ": " + value));
        
        System.out.println("\n✅ Zomato CQRS Demo completed!");
    }
    
    private static void simulateOrderWorkflow(OrderCommandHandler commandHandler, OrderQueryHandler queryHandler) 
            throws InterruptedException {
        
        System.out.println("\n🎭 Simulating order workflow...");
        
        // Create sample orders
        for (int i = 1; i <= 10; i++) {
            String orderId = "ORDER_" + String.format("%03d", i);
            String customerId = "CUST_" + String.format("%03d", i % 3 + 1);
            String restaurantId = "REST_" + String.format("%03d", i % 5 + 1);
            
            // Create order items
            List<OrderItem> items = Arrays.asList(
                new OrderItem("ITEM_" + i, "पवभाजी", 2, 80.0, "Main Course", Arrays.asList("Extra Butter")),
                new OrderItem("ITEM_" + (i+10), "गरमा गरम रोटी", 4, 15.0, "Bread", Collections.emptyList())
            );
            
            double totalAmount = items.stream().mapToDouble(OrderItem::getTotalPrice).sum();
            
            // Place order
            commandHandler.handle(new PlaceOrderCommand(
                UUID.randomUUID().toString(),
                orderId,
                customerId,
                restaurantId,
                items,
                "Mumbai, Maharashtra",
                "UPI",
                totalAmount
            ));
            
            Thread.sleep(100); // Small delay
            
            // Update order status progression
            String[] statuses = {"CONFIRMED", "PREPARING", "READY", "PICKED_UP", "OUT_FOR_DELIVERY"};
            
            for (String status : statuses) {
                commandHandler.handle(new UpdateOrderStatusCommand(
                    UUID.randomUUID().toString(),
                    orderId,
                    status,
                    "SYSTEM",
                    "Automatic progression"
                ));
                Thread.sleep(50);
            }
            
            // Complete or cancel order
            if (i % 7 == 0) { // Cancel some orders
                commandHandler.handle(new CancelOrderCommand(
                    UUID.randomUUID().toString(),
                    orderId,
                    "Customer cancelled",
                    "CUSTOMER",
                    totalAmount * 0.8 // 80% refund
                ));
            } else {
                commandHandler.handle(new UpdateOrderStatusCommand(
                    UUID.randomUUID().toString(),
                    orderId,
                    "DELIVERED",
                    "DELIVERY_PARTNER",
                    "Order delivered successfully"
                ));
            }
        }
        
        // Demo queries
        Thread.sleep(500); // Let events propagate
        
        System.out.println("\n🔍 === Query Examples ===");
        
        // Customer orders
        List<OrderSummaryReadModel> customerOrders = queryHandler.getOrdersByCustomer("CUST_001");
        System.out.println("Customer CUST_001 orders: " + customerOrders.size());
        customerOrders.forEach(System.out::println);
        
        // Restaurant analytics
        System.out.println("\n📈 Restaurant Analytics:");
        RestaurantAnalyticsReadModel restaurantAnalytics = queryHandler.getRestaurantAnalytics("REST_001");
        if (restaurantAnalytics != null) {
            System.out.println(restaurantAnalytics);
            System.out.println("Popular items: " + restaurantAnalytics.popularItems);
        }
        
        // Top restaurants
        System.out.println("\n🏆 Top Restaurants by Revenue:");
        queryHandler.getTopRestaurantsByRevenue(3).forEach(System.out::println);
        
        // Customer analytics
        System.out.println("\n👥 Top Customers by Spending:");
        queryHandler.getTopCustomersBySpending(3).forEach(System.out::println);
        
        // Orders by status
        System.out.println("\n📦 Active Orders:");
        queryHandler.getOrdersByStatus("OUT_FOR_DELIVERY").forEach(System.out::println);
    }
}
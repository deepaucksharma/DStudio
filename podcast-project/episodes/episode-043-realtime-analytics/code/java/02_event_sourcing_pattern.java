/*
 * Event Sourcing Pattern Implementation
 * Episode 43: Real-time Analytics at Scale
 * 
 * Complete Event Sourcing implementation with real-time event replay
 * Use Case: Ola ride booking system with complete audit trail
 */

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.function.Consumer;

/**
 * Event Sourcing for Ola Ride Booking System
 * 
 * यह system हर ride booking की complete history maintain करता है
 * और real-time में state changes को track करता है
 */
public class OlaEventSourcingSystem {
    
    /**
     * Base Event Class
     * सभी events का base class
     */
    public static abstract class Event {
        public final String eventId;
        public final String aggregateId;
        public final String eventType;
        public final long timestamp;
        public final String userId;
        
        public Event(String eventId, String aggregateId, String eventType, String userId) {
            this.eventId = eventId;
            this.aggregateId = aggregateId;
            this.eventType = eventType;
            this.timestamp = System.currentTimeMillis();
            this.userId = userId;
        }
        
        public abstract Map<String, Object> getEventData();
        
        @Override
        public String toString() {
            return String.format("Event{id='%s', type='%s', aggregateId='%s', timestamp=%d, userId='%s'}",
                               eventId, eventType, aggregateId, timestamp, userId);
        }
    }
    
    /**
     * Ride Booking Events
     * Ride booking के सभी possible events
     */
    public static class RideRequestedEvent extends Event {
        public final String pickupLocation;
        public final String dropLocation;
        public final String rideType;
        public final double estimatedFare;
        
        public RideRequestedEvent(String eventId, String rideId, String userId, 
                                String pickupLocation, String dropLocation, String rideType, double estimatedFare) {
            super(eventId, rideId, "RideRequested", userId);
            this.pickupLocation = pickupLocation;
            this.dropLocation = dropLocation;
            this.rideType = rideType;
            this.estimatedFare = estimatedFare;
        }
        
        @Override
        public Map<String, Object> getEventData() {
            Map<String, Object> data = new HashMap<>();
            data.put("pickupLocation", pickupLocation);
            data.put("dropLocation", dropLocation);
            data.put("rideType", rideType);
            data.put("estimatedFare", estimatedFare);
            return data;
        }
    }
    
    public static class DriverAssignedEvent extends Event {
        public final String driverId;
        public final String driverName;
        public final String vehicleNumber;
        public final double driverRating;
        public final int estimatedArrivalTime;
        
        public DriverAssignedEvent(String eventId, String rideId, String userId, String driverId, 
                                 String driverName, String vehicleNumber, double driverRating, int estimatedArrivalTime) {
            super(eventId, rideId, "DriverAssigned", userId);
            this.driverId = driverId;
            this.driverName = driverName;
            this.vehicleNumber = vehicleNumber;
            this.driverRating = driverRating;
            this.estimatedArrivalTime = estimatedArrivalTime;
        }
        
        @Override
        public Map<String, Object> getEventData() {
            Map<String, Object> data = new HashMap<>();
            data.put("driverId", driverId);
            data.put("driverName", driverName);
            data.put("vehicleNumber", vehicleNumber);
            data.put("driverRating", driverRating);
            data.put("estimatedArrivalTime", estimatedArrivalTime);
            return data;
        }
    }
    
    public static class RideStartedEvent extends Event {
        public final double startLatitude;
        public final double startLongitude;
        public final long actualStartTime;
        
        public RideStartedEvent(String eventId, String rideId, String userId, 
                              double startLatitude, double startLongitude, long actualStartTime) {
            super(eventId, rideId, "RideStarted", userId);
            this.startLatitude = startLatitude;
            this.startLongitude = startLongitude;
            this.actualStartTime = actualStartTime;
        }
        
        @Override
        public Map<String, Object> getEventData() {
            Map<String, Object> data = new HashMap<>();
            data.put("startLatitude", startLatitude);
            data.put("startLongitude", startLongitude);
            data.put("actualStartTime", actualStartTime);
            return data;
        }
    }
    
    public static class RideCompletedEvent extends Event {
        public final double endLatitude;
        public final double endLongitude;
        public final double actualFare;
        public final double distance;
        public final long actualEndTime;
        public final String paymentMethod;
        
        public RideCompletedEvent(String eventId, String rideId, String userId,
                                double endLatitude, double endLongitude, double actualFare,
                                double distance, long actualEndTime, String paymentMethod) {
            super(eventId, rideId, "RideCompleted", userId);
            this.endLatitude = endLatitude;
            this.endLongitude = endLongitude;
            this.actualFare = actualFare;
            this.distance = distance;
            this.actualEndTime = actualEndTime;
            this.paymentMethod = paymentMethod;
        }
        
        @Override
        public Map<String, Object> getEventData() {
            Map<String, Object> data = new HashMap<>();
            data.put("endLatitude", endLatitude);
            data.put("endLongitude", endLongitude);
            data.put("actualFare", actualFare);
            data.put("distance", distance);
            data.put("actualEndTime", actualEndTime);
            data.put("paymentMethod", paymentMethod);
            return data;
        }
    }
    
    public static class RideCancelledEvent extends Event {
        public final String cancellationReason;
        public final String cancelledBy; // USER, DRIVER, SYSTEM
        public final double cancellationFee;
        
        public RideCancelledEvent(String eventId, String rideId, String userId,
                                String cancellationReason, String cancelledBy, double cancellationFee) {
            super(eventId, rideId, "RideCancelled", userId);
            this.cancellationReason = cancellationReason;
            this.cancelledBy = cancelledBy;
            this.cancellationFee = cancellationFee;
        }
        
        @Override
        public Map<String, Object> getEventData() {
            Map<String, Object> data = new HashMap<>();
            data.put("cancellationReason", cancellationReason);
            data.put("cancelledBy", cancelledBy);
            data.put("cancellationFee", cancellationFee);
            return data;
        }
    }
    
    /**
     * Ride Aggregate
     * Complete ride state को represent करता है
     */
    public static class RideAggregate {
        public final String rideId;
        public String userId;
        public String status;
        public String pickupLocation;
        public String dropLocation;
        public String rideType;
        public double estimatedFare;
        public String driverId;
        public String driverName;
        public String vehicleNumber;
        public double driverRating;
        public double actualFare;
        public double distance;
        public long requestTime;
        public long startTime;
        public long endTime;
        public String paymentMethod;
        public String cancellationReason;
        public double cancellationFee;
        public List<Event> eventHistory;
        
        public RideAggregate(String rideId) {
            this.rideId = rideId;
            this.status = "UNKNOWN";
            this.eventHistory = new ArrayList<>();
        }
        
        /**
         * Apply event to aggregate
         * Event को aggregate पर apply करके state update करता है
         */
        public void apply(Event event) {
            eventHistory.add(event);
            
            switch (event.eventType) {
                case "RideRequested":
                    applyRideRequested((RideRequestedEvent) event);
                    break;
                case "DriverAssigned":
                    applyDriverAssigned((DriverAssignedEvent) event);
                    break;
                case "RideStarted":
                    applyRideStarted((RideStartedEvent) event);
                    break;
                case "RideCompleted":
                    applyRideCompleted((RideCompletedEvent) event);
                    break;
                case "RideCancelled":
                    applyRideCancelled((RideCancelledEvent) event);
                    break;
            }
        }
        
        private void applyRideRequested(RideRequestedEvent event) {
            this.userId = event.userId;
            this.pickupLocation = event.pickupLocation;
            this.dropLocation = event.dropLocation;
            this.rideType = event.rideType;
            this.estimatedFare = event.estimatedFare;
            this.requestTime = event.timestamp;
            this.status = "REQUESTED";
        }
        
        private void applyDriverAssigned(DriverAssignedEvent event) {
            this.driverId = event.driverId;
            this.driverName = event.driverName;
            this.vehicleNumber = event.vehicleNumber;
            this.driverRating = event.driverRating;
            this.status = "DRIVER_ASSIGNED";
        }
        
        private void applyRideStarted(RideStartedEvent event) {
            this.startTime = event.actualStartTime;
            this.status = "IN_PROGRESS";
        }
        
        private void applyRideCompleted(RideCompletedEvent event) {
            this.actualFare = event.actualFare;
            this.distance = event.distance;
            this.endTime = event.actualEndTime;
            this.paymentMethod = event.paymentMethod;
            this.status = "COMPLETED";
        }
        
        private void applyRideCancelled(RideCancelledEvent event) {
            this.cancellationReason = event.cancellationReason;
            this.cancellationFee = event.cancellationFee;
            this.status = "CANCELLED";
        }
        
        public double getRideDuration() {
            if (startTime > 0 && endTime > 0) {
                return (endTime - startTime) / 1000.0 / 60.0; // minutes
            }
            return 0.0;
        }
        
        @Override
        public String toString() {
            return String.format("RideAggregate{rideId='%s', status='%s', userId='%s', " +
                               "pickup='%s', drop='%s', driver='%s', fare=%.2f}",
                               rideId, status, userId, pickupLocation, dropLocation, driverName, actualFare);
        }
    }
    
    /**
     * Event Store
     * सभी events को store और retrieve करता है
     */
    public static class EventStore {
        private final List<Event> eventLog = new CopyOnWriteArrayList<>();
        private final Map<String, List<Event>> eventsByAggregate = new ConcurrentHashMap<>();
        private final List<Consumer<Event>> eventHandlers = new CopyOnWriteArrayList<>();
        
        public void appendEvent(Event event) {
            // Store in main log
            eventLog.add(event);
            
            // Store by aggregate ID
            eventsByAggregate.computeIfAbsent(event.aggregateId, k -> new CopyOnWriteArrayList<>()).add(event);
            
            // Notify handlers
            eventHandlers.forEach(handler -> {
                try {
                    handler.accept(event);
                } catch (Exception e) {
                    System.err.println("Error in event handler: " + e.getMessage());
                }
            });
            
            System.out.println("📝 Event stored: " + event);
        }
        
        public List<Event> getEventsForAggregate(String aggregateId) {
            return new ArrayList<>(eventsByAggregate.getOrDefault(aggregateId, new ArrayList<>()));
        }
        
        public List<Event> getAllEvents() {
            return new ArrayList<>(eventLog);
        }
        
        public List<Event> getEventsSince(long timestamp) {
            return eventLog.stream()
                          .filter(event -> event.timestamp >= timestamp)
                          .collect(Collectors.toList());
        }
        
        public List<Event> getEventsByType(String eventType) {
            return eventLog.stream()
                          .filter(event -> event.eventType.equals(eventType))
                          .collect(Collectors.toList());
        }
        
        public void addEventHandler(Consumer<Event> handler) {
            eventHandlers.add(handler);
        }
        
        public int getTotalEventCount() {
            return eventLog.size();
        }
    }
    
    /**
     * Aggregate Repository
     * Aggregates को manage करता है
     */
    public static class RideAggregateRepository {
        private final EventStore eventStore;
        private final Map<String, RideAggregate> aggregateCache = new ConcurrentHashMap<>();
        
        public RideAggregateRepository(EventStore eventStore) {
            this.eventStore = eventStore;
        }
        
        public RideAggregate getAggregate(String rideId) {
            // Check cache first
            RideAggregate aggregate = aggregateCache.get(rideId);
            if (aggregate != null) {
                return aggregate;
            }
            
            // Rebuild from events
            aggregate = new RideAggregate(rideId);
            List<Event> events = eventStore.getEventsForAggregate(rideId);
            
            for (Event event : events) {
                aggregate.apply(event);
            }
            
            // Cache for future use
            aggregateCache.put(rideId, aggregate);
            return aggregate;
        }
        
        public void saveEvent(Event event) {
            eventStore.appendEvent(event);
            
            // Update cache if aggregate is loaded
            RideAggregate aggregate = aggregateCache.get(event.aggregateId);
            if (aggregate != null) {
                aggregate.apply(event);
            }
        }
        
        public void clearCache() {
            aggregateCache.clear();
        }
        
        public List<RideAggregate> getAllActiveRides() {
            return eventStore.getAllEvents().stream()
                           .map(event -> event.aggregateId)
                           .distinct()
                           .map(this::getAggregate)
                           .filter(ride -> !"COMPLETED".equals(ride.status) && !"CANCELLED".equals(ride.status))
                           .collect(Collectors.toList());
        }
    }
    
    /**
     * Real-time Analytics Processor
     * Events के based पर real-time analytics calculate करता है
     */
    public static class RealTimeAnalyticsProcessor {
        private final Map<String, Object> metrics = new ConcurrentHashMap<>();
        private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
        
        public RealTimeAnalyticsProcessor(EventStore eventStore) {
            // Initialize metrics
            resetMetrics();
            
            // Register event handler
            eventStore.addEventHandler(this::processEvent);
            
            // Schedule periodic metric reports
            scheduler.scheduleAtFixedRate(this::printMetrics, 30, 30, TimeUnit.SECONDS);
        }
        
        private void resetMetrics() {
            metrics.put("totalRides", 0);
            metrics.put("completedRides", 0);
            metrics.put("cancelledRides", 0);
            metrics.put("activeRides", 0);
            metrics.put("totalRevenue", 0.0);
            metrics.put("averageFare", 0.0);
            metrics.put("averageRating", 0.0);
            metrics.put("cancellationRate", 0.0);
            metrics.put("hourlyRides", new HashMap<Integer, Integer>());
        }
        
        private void processEvent(Event event) {
            switch (event.eventType) {
                case "RideRequested":
                    processRideRequested((RideRequestedEvent) event);
                    break;
                case "RideCompleted":
                    processRideCompleted((RideCompletedEvent) event);
                    break;
                case "RideCancelled":
                    processRideCancelled((RideCancelledEvent) event);
                    break;
                case "DriverAssigned":
                    processDriverAssigned((DriverAssignedEvent) event);
                    break;
            }
            
            updateHourlyMetrics(event);
        }
        
        private void processRideRequested(RideRequestedEvent event) {
            metrics.put("totalRides", (Integer) metrics.get("totalRides") + 1);
            metrics.put("activeRides", (Integer) metrics.get("activeRides") + 1);
        }
        
        private void processRideCompleted(RideCompletedEvent event) {
            metrics.put("completedRides", (Integer) metrics.get("completedRides") + 1);
            metrics.put("activeRides", (Integer) metrics.get("activeRides") - 1);
            
            double currentRevenue = (Double) metrics.get("totalRevenue");
            metrics.put("totalRevenue", currentRevenue + event.actualFare);
            
            // Update average fare
            int completedRides = (Integer) metrics.get("completedRides");
            double totalRevenue = (Double) metrics.get("totalRevenue");
            metrics.put("averageFare", totalRevenue / completedRides);
        }
        
        private void processRideCancelled(RideCancelledEvent event) {
            metrics.put("cancelledRides", (Integer) metrics.get("cancelledRides") + 1);
            metrics.put("activeRides", (Integer) metrics.get("activeRides") - 1);
            
            // Update cancellation rate
            int totalRides = (Integer) metrics.get("totalRides");
            int cancelledRides = (Integer) metrics.get("cancelledRides");
            metrics.put("cancellationRate", (double) cancelledRides / totalRides * 100);
        }
        
        private void processDriverAssigned(DriverAssignedEvent event) {
            // Update average driver rating
            double currentAvgRating = (Double) metrics.get("averageRating");
            int assignedRides = ((Integer) metrics.get("totalRides")) - ((Integer) metrics.get("activeRides"));
            
            if (assignedRides == 0) {
                metrics.put("averageRating", event.driverRating);
            } else {
                double newAvgRating = (currentAvgRating * (assignedRides - 1) + event.driverRating) / assignedRides;
                metrics.put("averageRating", newAvgRating);
            }
        }
        
        @SuppressWarnings("unchecked")
        private void updateHourlyMetrics(Event event) {
            LocalDateTime eventTime = LocalDateTime.ofInstant(Instant.ofEpochMilli(event.timestamp), ZoneId.systemDefault());
            int hour = eventTime.getHour();
            
            Map<Integer, Integer> hourlyRides = (Map<Integer, Integer>) metrics.get("hourlyRides");
            hourlyRides.put(hour, hourlyRides.getOrDefault(hour, 0) + 1);
        }
        
        @SuppressWarnings("unchecked")
        private void printMetrics() {
            System.out.println("\n📊 === Real-time Ola Analytics ===");
            System.out.println("Total Rides: " + metrics.get("totalRides"));
            System.out.println("Active Rides: " + metrics.get("activeRides"));
            System.out.println("Completed Rides: " + metrics.get("completedRides"));
            System.out.println("Cancelled Rides: " + metrics.get("cancelledRides"));
            System.out.println("Total Revenue: ₹" + String.format("%.2f", (Double) metrics.get("totalRevenue")));
            System.out.println("Average Fare: ₹" + String.format("%.2f", (Double) metrics.get("averageFare")));
            System.out.println("Average Driver Rating: " + String.format("%.2f", (Double) metrics.get("averageRating")));
            System.out.println("Cancellation Rate: " + String.format("%.2f%%", (Double) metrics.get("cancellationRate")));
            
            Map<Integer, Integer> hourlyRides = (Map<Integer, Integer>) metrics.get("hourlyRides");
            System.out.println("Peak Hours: " + hourlyRides.entrySet().stream()
                                                           .sorted(Map.Entry.<Integer, Integer>comparingByValue().reversed())
                                                           .limit(3)
                                                           .map(entry -> entry.getKey() + ":00 (" + entry.getValue() + " rides)")
                                                           .collect(Collectors.joining(", ")));
            System.out.println("===============================\n");
        }
        
        public Map<String, Object> getCurrentMetrics() {
            return new HashMap<>(metrics);
        }
        
        public void shutdown() {
            scheduler.shutdown();
        }
    }
    
    /**
     * Event Replay Service
     * Historical events को replay करके state reconstruct करता है
     */
    public static class EventReplayService {
        private final EventStore eventStore;
        private final RideAggregateRepository repository;
        
        public EventReplayService(EventStore eventStore, RideAggregateRepository repository) {
            this.eventStore = eventStore;
            this.repository = repository;
        }
        
        public void replayAllEvents() {
            System.out.println("🔄 Replaying all events...");
            
            repository.clearCache();
            List<Event> allEvents = eventStore.getAllEvents();
            
            System.out.println("Found " + allEvents.size() + " events to replay");
            
            for (Event event : allEvents) {
                RideAggregate aggregate = repository.getAggregate(event.aggregateId);
                // Aggregate will automatically rebuild from events
            }
            
            System.out.println("✅ Event replay completed");
        }
        
        public void replayEventsForRide(String rideId) {
            System.out.println("🔄 Replaying events for ride: " + rideId);
            
            List<Event> events = eventStore.getEventsForAggregate(rideId);
            System.out.println("Found " + events.size() + " events for ride " + rideId);
            
            RideAggregate aggregate = new RideAggregate(rideId);
            for (Event event : events) {
                aggregate.apply(event);
                System.out.println("Applied: " + event.eventType + " -> Status: " + aggregate.status);
            }
            
            System.out.println("Final aggregate state: " + aggregate);
        }
        
        public void replayEventsSince(long timestamp) {
            System.out.println("🔄 Replaying events since: " + Instant.ofEpochMilli(timestamp));
            
            List<Event> events = eventStore.getEventsSince(timestamp);
            System.out.println("Found " + events.size() + " events since timestamp");
            
            Map<String, Integer> eventTypeCounts = new HashMap<>();
            for (Event event : events) {
                eventTypeCounts.put(event.eventType, eventTypeCounts.getOrDefault(event.eventType, 0) + 1);
            }
            
            System.out.println("Event type distribution:");
            eventTypeCounts.forEach((type, count) -> System.out.println("  " + type + ": " + count));
        }
    }
    
    /**
     * Main Ola Event Sourcing Demo
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🚗 Starting Ola Event Sourcing Demo...");
        
        // Initialize components
        EventStore eventStore = new EventStore();
        RideAggregateRepository repository = new RideAggregateRepository(eventStore);
        RealTimeAnalyticsProcessor analytics = new RealTimeAnalyticsProcessor(eventStore);
        EventReplayService replayService = new EventReplayService(eventStore, repository);
        
        // Simulate ride booking scenarios
        simulateRideBookings(repository);
        
        // Wait for metrics to be processed
        Thread.sleep(2000);
        
        // Demonstrate event replay
        System.out.println("\n=== Event Replay Demonstration ===");
        replayService.replayAllEvents();
        
        // Show specific ride history
        String sampleRideId = "RIDE_001";
        replayService.replayEventsForRide(sampleRideId);
        
        // Show recent events
        long oneHourAgo = System.currentTimeMillis() - (60 * 60 * 1000);
        replayService.replayEventsSince(oneHourAgo);
        
        // Final metrics
        System.out.println("\n=== Final System State ===");
        Map<String, Object> finalMetrics = analytics.getCurrentMetrics();
        finalMetrics.forEach((key, value) -> System.out.println(key + ": " + value));
        
        System.out.println("\nTotal events in store: " + eventStore.getTotalEventCount());
        System.out.println("Active rides: " + repository.getAllActiveRides().size());
        
        // Cleanup
        analytics.shutdown();
        
        System.out.println("\n✅ Ola Event Sourcing Demo completed!");
    }
    
    private static void simulateRideBookings(RideAggregateRepository repository) {
        System.out.println("\n🎭 Simulating ride bookings...");
        
        // Simulate multiple ride scenarios
        for (int i = 1; i <= 10; i++) {
            String rideId = "RIDE_" + String.format("%03d", i);
            String userId = "USER_" + String.format("%03d", i % 5 + 1);
            
            try {
                simulateCompleteRide(repository, rideId, userId, i);
                Thread.sleep(100); // Small delay between rides
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        // Simulate some cancellations
        for (int i = 11; i <= 13; i++) {
            String rideId = "RIDE_" + String.format("%03d", i);
            String userId = "USER_" + String.format("%03d", i % 5 + 1);
            
            try {
                simulateCancelledRide(repository, rideId, userId);
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
    
    private static void simulateCompleteRide(RideAggregateRepository repository, String rideId, String userId, int variation) {
        String[] pickups = {"Bandra", "Andheri", "Powai", "Dadar", "Kurla"};
        String[] drops = {"Airport", "Ghatkopar", "Thane", "Malad", "Worli"};
        String[] rideTypes = {"Mini", "Prime", "Auto"};
        String[] drivers = {"राम शर्मा", "श्याम वर्मा", "गीता पटेल", "सुनील कुमार", "अजय सिंह"};
        String[] vehicles = {"MH01AB1234", "MH02CD5678", "MH03EF9012", "MH04GH3456", "MH05IJ7890"};
        
        // Ride requested
        repository.saveEvent(new RideRequestedEvent(
            UUID.randomUUID().toString(),
            rideId,
            userId,
            pickups[variation % pickups.length],
            drops[variation % drops.length],
            rideTypes[variation % rideTypes.length],
            200 + (variation * 50)
        ));
        
        // Driver assigned
        repository.saveEvent(new DriverAssignedEvent(
            UUID.randomUUID().toString(),
            rideId,
            userId,
            "DRIVER_" + String.format("%03d", variation % 5 + 1),
            drivers[variation % drivers.length],
            vehicles[variation % vehicles.length],
            4.0 + (variation % 10) * 0.1,
            5 + (variation % 10)
        ));
        
        // Ride started
        repository.saveEvent(new RideStartedEvent(
            UUID.randomUUID().toString(),
            rideId,
            userId,
            19.0760 + (variation * 0.01),
            72.8777 + (variation * 0.01),
            System.currentTimeMillis() + (variation * 1000)
        ));
        
        // Ride completed
        repository.saveEvent(new RideCompletedEvent(
            UUID.randomUUID().toString(),
            rideId,
            userId,
            19.0760 + (variation * 0.02),
            72.8777 + (variation * 0.02),
            180 + (variation * 40),
            8.5 + (variation * 2),
            System.currentTimeMillis() + ((variation + 20) * 1000),
            variation % 2 == 0 ? "UPI" : "Cash"
        ));
    }
    
    private static void simulateCancelledRide(RideAggregateRepository repository, String rideId, String userId) {
        String[] pickups = {"Bandra", "Andheri", "Powai"};
        String[] drops = {"Airport", "Ghatkopar", "Thane"};
        String[] reasons = {"Driver not reachable", "Changed plans", "Found alternative", "Emergency"};
        String[] cancelledBy = {"USER", "DRIVER", "SYSTEM"};
        
        int variation = rideId.hashCode() % 100;
        
        // Ride requested
        repository.saveEvent(new RideRequestedEvent(
            UUID.randomUUID().toString(),
            rideId,
            userId,
            pickups[Math.abs(variation) % pickups.length],
            drops[Math.abs(variation) % drops.length],
            "Mini",
            150
        ));
        
        // Sometimes assign driver before cancellation
        if (variation % 2 == 0) {
            repository.saveEvent(new DriverAssignedEvent(
                UUID.randomUUID().toString(),
                rideId,
                userId,
                "DRIVER_999",
                "टेस्ट ड्राइवर",
                "MH01XX9999",
                4.5,
                8
            ));
        }
        
        // Cancel ride
        repository.saveEvent(new RideCancelledEvent(
            UUID.randomUUID().toString(),
            rideId,
            userId,
            reasons[Math.abs(variation) % reasons.length],
            cancelledBy[Math.abs(variation) % cancelledBy.length],
            variation % 2 == 0 ? 20.0 : 0.0
        ));
    }
}
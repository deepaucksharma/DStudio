import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.stream.Collectors;

/**
 * IRCTC Distributed Seat Allocation System
 * IRCTC के seat allocation का distributed implementation
 * 
 * यह example दिखाता है कि कैसे multiple booking servers के बीच
 * seat allocation को coordinate करते हैं using distributed consensus.
 * IRCTC processes 1M+ bookings daily across multiple servers.
 * 
 * Production context: IRCTC handles peak loads of 30,000+ concurrent bookings
 * Scale: Distributed across multiple data centers for fault tolerance
 * Challenge: Preventing double bookings while maintaining high availability
 */

/**
 * Train and coach information
 */
class TrainInfo {
    public final String trainNumber;
    public final String trainName;
    public final String source;
    public final String destination;
    public final LocalDateTime departureTime;
    public final Map<String, CoachInfo> coaches;
    
    public TrainInfo(String trainNumber, String trainName, String source, 
                    String destination, LocalDateTime departureTime) {
        this.trainNumber = trainNumber;
        this.trainName = trainName;
        this.source = source;
        this.destination = destination;
        this.departureTime = departureTime;
        this.coaches = new ConcurrentHashMap<>();
    }
    
    public void addCoach(CoachInfo coach) {
        coaches.put(coach.coachId, coach);
    }
    
    @Override
    public String toString() {
        return String.format("Train %s (%s): %s -> %s at %s", 
                           trainNumber, trainName, source, destination, 
                           departureTime.format(DateTimeFormatter.ofPattern("HH:mm")));
    }
}

/**
 * Coach information with seat layout
 */
class CoachInfo {
    public final String coachId;
    public final String coachType; // AC1, AC2, AC3, SL, etc.
    public final int totalSeats;
    public final Map<Integer, SeatInfo> seats;
    private final AtomicInteger availableSeats;
    
    public CoachInfo(String coachId, String coachType, int totalSeats) {
        this.coachId = coachId;
        this.coachType = coachType;
        this.totalSeats = totalSeats;
        this.seats = new ConcurrentHashMap<>();
        this.availableSeats = new AtomicInteger(totalSeats);
        
        // Initialize seats
        for (int i = 1; i <= totalSeats; i++) {
            seats.put(i, new SeatInfo(i, coachId));
        }
    }
    
    public int getAvailableSeats() {
        return availableSeats.get();
    }
    
    public boolean bookSeat(int seatNumber, String passengerId, String bookingId) {
        SeatInfo seat = seats.get(seatNumber);
        if (seat != null && seat.book(passengerId, bookingId)) {
            availableSeats.decrementAndGet();
            return true;
        }
        return false;
    }
    
    public boolean cancelSeat(int seatNumber) {
        SeatInfo seat = seats.get(seatNumber);
        if (seat != null && seat.cancel()) {
            availableSeats.incrementAndGet();
            return true;
        }
        return false;
    }
    
    public List<Integer> getAvailableSeatNumbers() {
        return seats.values().stream()
                   .filter(seat -> !seat.isBooked())
                   .map(seat -> seat.seatNumber)
                   .sorted()
                   .collect(Collectors.toList());
    }
    
    @Override
    public String toString() {
        return String.format("Coach %s (%s): %d/%d seats available", 
                           coachId, coachType, availableSeats.get(), totalSeats);
    }
}

/**
 * Individual seat information
 */
class SeatInfo {
    public final int seatNumber;
    public final String coachId;
    private final AtomicReference<String> passengerId;
    private final AtomicReference<String> bookingId;
    private final AtomicBoolean isBooked;
    private volatile long bookingTime;
    
    public SeatInfo(int seatNumber, String coachId) {
        this.seatNumber = seatNumber;
        this.coachId = coachId;
        this.passengerId = new AtomicReference<>();
        this.bookingId = new AtomicReference<>();
        this.isBooked = new AtomicBoolean(false);
        this.bookingTime = 0;
    }
    
    public boolean book(String passengerId, String bookingId) {
        if (isBooked.compareAndSet(false, true)) {
            this.passengerId.set(passengerId);
            this.bookingId.set(bookingId);
            this.bookingTime = System.currentTimeMillis();
            return true;
        }
        return false;
    }
    
    public boolean cancel() {
        if (isBooked.compareAndSet(true, false)) {
            this.passengerId.set(null);
            this.bookingId.set(null);
            this.bookingTime = 0;
            return true;
        }
        return false;
    }
    
    public boolean isBooked() {
        return isBooked.get();
    }
    
    public String getPassengerId() {
        return passengerId.get();
    }
    
    public String getBookingId() {
        return bookingId.get();
    }
    
    @Override
    public String toString() {
        return String.format("Seat %d-%s: %s", 
                           seatNumber, coachId, 
                           isBooked() ? "BOOKED by " + passengerId.get() : "AVAILABLE");
    }
}

/**
 * Booking request information
 */
class BookingRequest {
    public final String requestId;
    public final String passengerId;
    public final String passengerName;
    public final String trainNumber;
    public final String preferredCoachType;
    public final int requestedSeats;
    public final long requestTime;
    public final String sourceStation;
    public final String destinationStation;
    
    public BookingRequest(String requestId, String passengerId, String passengerName,
                         String trainNumber, String preferredCoachType, int requestedSeats,
                         String sourceStation, String destinationStation) {
        this.requestId = requestId;
        this.passengerId = passengerId;
        this.passengerName = passengerName;
        this.trainNumber = trainNumber;
        this.preferredCoachType = preferredCoachType;
        this.requestedSeats = requestedSeats;
        this.sourceStation = sourceStation;
        this.destinationStation = destinationStation;
        this.requestTime = System.currentTimeMillis();
    }
    
    @Override
    public String toString() {
        return String.format("BookingRequest{id=%s, passenger=%s, train=%s, seats=%d, coach=%s}",
                           requestId, passengerName, trainNumber, requestedSeats, preferredCoachType);
    }
}

/**
 * Booking result information
 */
class BookingResult {
    public enum Status {
        SUCCESS, FAILED_NO_SEATS, FAILED_SYSTEM_ERROR, FAILED_TRAIN_NOT_FOUND
    }
    
    public final String requestId;
    public final Status status;
    public final String bookingId;
    public final List<SeatAllocation> allocatedSeats;
    public final String message;
    public final long processingTime;
    
    public BookingResult(String requestId, Status status, String bookingId,
                        List<SeatAllocation> allocatedSeats, String message, long processingTime) {
        this.requestId = requestId;
        this.status = status;
        this.bookingId = bookingId;
        this.allocatedSeats = allocatedSeats != null ? new ArrayList<>(allocatedSeats) : new ArrayList<>();
        this.message = message;
        this.processingTime = processingTime;
    }
    
    public static class SeatAllocation {
        public final String coachId;
        public final int seatNumber;
        public final String passengerId;
        
        public SeatAllocation(String coachId, int seatNumber, String passengerId) {
            this.coachId = coachId;
            this.seatNumber = seatNumber;
            this.passengerId = passengerId;
        }
        
        @Override
        public String toString() {
            return String.format("%s-%d", coachId, seatNumber);
        }
    }
    
    @Override
    public String toString() {
        return String.format("BookingResult{id=%s, status=%s, seats=%s, time=%dms}",
                           requestId, status, 
                           allocatedSeats.stream().map(Object::toString).collect(Collectors.joining(",")),
                           processingTime);
    }
}

/**
 * Distributed IRCTC booking server node
 */
class IRCTCBookingNode {
    private final String nodeId;
    private final String region;
    private final Map<String, TrainInfo> trainDatabase;
    private final BlockingQueue<BookingRequest> bookingQueue;
    private final Map<String, BookingResult> bookingResults;
    private final ExecutorService bookingExecutor;
    private final AtomicBoolean isRunning;
    private final AtomicInteger processedBookings;
    private final AtomicInteger successfulBookings;
    
    // Distributed coordination
    private final Map<String, IRCTCBookingNode> clusterNodes;
    private final ReentrantLock coordinationLock;
    
    public IRCTCBookingNode(String nodeId, String region) {
        this.nodeId = nodeId;
        this.region = region;
        this.trainDatabase = new ConcurrentHashMap<>();
        this.bookingQueue = new LinkedBlockingQueue<>();
        this.bookingResults = new ConcurrentHashMap<>();
        this.bookingExecutor = Executors.newFixedThreadPool(10);
        this.isRunning = new AtomicBoolean(false);
        this.processedBookings = new AtomicInteger(0);
        this.successfulBookings = new AtomicInteger(0);
        this.clusterNodes = new ConcurrentHashMap<>();
        this.coordinationLock = new ReentrantLock();
        
        // Initialize sample trains for this region
        initializeSampleTrains();
    }
    
    private void initializeSampleTrains() {
        if (region.equals("Western")) {
            // Mumbai-Delhi route
            TrainInfo rajdhani = new TrainInfo("12951", "Mumbai Rajdhani Express", 
                                             "Mumbai Central", "New Delhi", 
                                             LocalDateTime.now().plusHours(2));
            
            rajdhani.addCoach(new CoachInfo("A1", "AC1", 18));
            rajdhani.addCoach(new CoachInfo("A2", "AC2", 54));
            rajdhani.addCoach(new CoachInfo("A3", "AC3", 72));
            rajdhani.addCoach(new CoachInfo("S1", "SL", 72));
            rajdhani.addCoach(new CoachInfo("S2", "SL", 72));
            
            trainDatabase.put("12951", rajdhani);
            
        } else if (region.equals("Northern")) {
            // Delhi-Kolkata route
            TrainInfo gteExpress = new TrainInfo("12313", "Sealdah Rajdhani Express", 
                                               "New Delhi", "Sealdah", 
                                               LocalDateTime.now().plusHours(1));
            
            gteExpress.addCoach(new CoachInfo("A1", "AC1", 18));
            gteExpress.addCoach(new CoachInfo("A2", "AC2", 54));
            gteExpress.addCoach(new CoachInfo("A3", "AC3", 72));
            
            trainDatabase.put("12313", gteExpress);
            
        } else if (region.equals("Southern")) {
            // Chennai-Bangalore route
            TrainInfo shatabdi = new TrainInfo("12007", "Chennai Shatabdi Express", 
                                             "Chennai Central", "Bangalore City", 
                                             LocalDateTime.now().plusMinutes(30));
            
            shatabdi.addCoach(new CoachInfo("CC1", "CC", 78));
            shatabdi.addCoach(new CoachInfo("CC2", "CC", 78));
            shatabdi.addCoach(new CoachInfo("EC1", "EC", 78));
            
            trainDatabase.put("12007", shatabdi);
        }
    }
    
    public void addClusterNode(IRCTCBookingNode node) {
        clusterNodes.put(node.nodeId, node);
        System.out.printf("[%s] Added cluster node: %s (%s region)%n", 
                         nodeId, node.nodeId, node.region);
    }
    
    public void start() {
        if (isRunning.compareAndSet(false, true)) {
            // Start booking processing threads
            for (int i = 0; i < 10; i++) {
                bookingExecutor.submit(this::processBookings);
            }
            System.out.printf("[%s] IRCTC booking node started in %s region%n", nodeId, region);
        }
    }
    
    public void stop() {
        if (isRunning.compareAndSet(true, false)) {
            bookingExecutor.shutdown();
            try {
                if (!bookingExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                    bookingExecutor.shutdownNow();
                }
            } catch (InterruptedException e) {
                bookingExecutor.shutdownNow();
                Thread.currentThread().interrupt();
            }
            System.out.printf("[%s] IRCTC booking node stopped%n", nodeId);
        }
    }
    
    public CompletableFuture<BookingResult> submitBookingRequest(BookingRequest request) {
        if (!isRunning.get()) {
            return CompletableFuture.completedFuture(
                new BookingResult(request.requestId, BookingResult.Status.FAILED_SYSTEM_ERROR,
                                null, null, "System not running", 0));
        }
        
        CompletableFuture<BookingResult> future = new CompletableFuture<>();
        
        try {
            bookingQueue.offer(request, 1, TimeUnit.SECONDS);
            System.out.printf("[%s] Queued booking request: %s%n", nodeId, request.requestId);
            
            // Start async monitoring for result
            CompletableFuture.runAsync(() -> {
                try {
                    // Wait for result with timeout
                    for (int i = 0; i < 100; i++) { // 10 seconds timeout
                        BookingResult result = bookingResults.get(request.requestId);
                        if (result != null) {
                            future.complete(result);
                            return;
                        }
                        Thread.sleep(100);
                    }
                    
                    // Timeout
                    future.complete(new BookingResult(request.requestId, 
                                                    BookingResult.Status.FAILED_SYSTEM_ERROR,
                                                    null, null, "Booking timeout", 10000));
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    future.completeExceptionally(e);
                }
            });
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            future.complete(new BookingResult(request.requestId, 
                                            BookingResult.Status.FAILED_SYSTEM_ERROR,
                                            null, null, "Queue full", 0));
        }
        
        return future;
    }
    
    private void processBookings() {
        while (isRunning.get()) {
            try {
                BookingRequest request = bookingQueue.poll(1, TimeUnit.SECONDS);
                if (request != null) {
                    BookingResult result = processBookingRequest(request);
                    bookingResults.put(request.requestId, result);
                    processedBookings.incrementAndGet();
                    
                    if (result.status == BookingResult.Status.SUCCESS) {
                        successfulBookings.incrementAndGet();
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
    
    private BookingResult processBookingRequest(BookingRequest request) {
        long startTime = System.currentTimeMillis();
        
        try {
            // Find train in local database first
            TrainInfo train = trainDatabase.get(request.trainNumber);
            
            // If not found locally, try cluster nodes
            if (train == null) {
                train = findTrainInCluster(request.trainNumber);
                if (train == null) {
                    return new BookingResult(request.requestId, 
                                           BookingResult.Status.FAILED_TRAIN_NOT_FOUND,
                                           null, null, "Train not found", 
                                           System.currentTimeMillis() - startTime);
                }
            }
            
            // Try to allocate seats with coordination lock
            coordinationLock.lock();
            try {
                List<BookingResult.SeatAllocation> allocatedSeats = allocateSeats(train, request);
                
                if (allocatedSeats.size() == request.requestedSeats) {
                    String bookingId = generateBookingId();
                    
                    System.out.printf("[%s] Successfully booked %d seats for %s in train %s%n",
                                     nodeId, allocatedSeats.size(), request.passengerName, 
                                     request.trainNumber);
                    
                    return new BookingResult(request.requestId, BookingResult.Status.SUCCESS,
                                           bookingId, allocatedSeats, "Booking successful",
                                           System.currentTimeMillis() - startTime);
                } else {
                    // Rollback partial allocation
                    rollbackSeatAllocation(train, allocatedSeats);
                    
                    return new BookingResult(request.requestId, 
                                           BookingResult.Status.FAILED_NO_SEATS,
                                           null, null, "Insufficient seats available",
                                           System.currentTimeMillis() - startTime);
                }
                
            } finally {
                coordinationLock.unlock();
            }
            
        } catch (Exception e) {
            System.err.printf("[%s] Error processing booking request %s: %s%n", 
                             nodeId, request.requestId, e.getMessage());
            
            return new BookingResult(request.requestId, 
                                   BookingResult.Status.FAILED_SYSTEM_ERROR,
                                   null, null, "System error: " + e.getMessage(),
                                   System.currentTimeMillis() - startTime);
        }
    }
    
    private TrainInfo findTrainInCluster(String trainNumber) {
        // Search in other cluster nodes
        for (IRCTCBookingNode node : clusterNodes.values()) {
            TrainInfo train = node.trainDatabase.get(trainNumber);
            if (train != null) {
                System.out.printf("[%s] Found train %s in cluster node %s%n", 
                                 nodeId, trainNumber, node.nodeId);
                return train;
            }
        }
        return null;
    }
    
    private List<BookingResult.SeatAllocation> allocateSeats(TrainInfo train, BookingRequest request) {
        List<BookingResult.SeatAllocation> allocations = new ArrayList<>();
        
        // Find coaches matching preferred type
        List<CoachInfo> preferredCoaches = train.coaches.values().stream()
            .filter(coach -> coach.coachType.equals(request.preferredCoachType))
            .filter(coach -> coach.getAvailableSeats() > 0)
            .sorted((c1, c2) -> Integer.compare(c2.getAvailableSeats(), c1.getAvailableSeats()))
            .collect(Collectors.toList());
        
        // If preferred type not available, try any available coach
        if (preferredCoaches.isEmpty()) {
            preferredCoaches = train.coaches.values().stream()
                .filter(coach -> coach.getAvailableSeats() > 0)
                .sorted((c1, c2) -> Integer.compare(c2.getAvailableSeats(), c1.getAvailableSeats()))
                .collect(Collectors.toList());
        }
        
        String bookingId = generateBookingId();
        
        // Allocate seats
        for (CoachInfo coach : preferredCoaches) {
            if (allocations.size() >= request.requestedSeats) {
                break;
            }
            
            List<Integer> availableSeats = coach.getAvailableSeatNumbers();
            for (Integer seatNumber : availableSeats) {
                if (allocations.size() >= request.requestedSeats) {
                    break;
                }
                
                if (coach.bookSeat(seatNumber, request.passengerId, bookingId)) {
                    allocations.add(new BookingResult.SeatAllocation(
                        coach.coachId, seatNumber, request.passengerId));
                }
            }
        }
        
        return allocations;
    }
    
    private void rollbackSeatAllocation(TrainInfo train, List<BookingResult.SeatAllocation> allocations) {
        for (BookingResult.SeatAllocation allocation : allocations) {
            CoachInfo coach = train.coaches.get(allocation.coachId);
            if (coach != null) {
                coach.cancelSeat(allocation.seatNumber);
            }
        }
    }
    
    private String generateBookingId() {
        return "PNR" + System.currentTimeMillis() + String.format("%03d", new Random().nextInt(1000));
    }
    
    public NodeStats getStats() {
        int totalSeats = trainDatabase.values().stream()
            .flatMap(train -> train.coaches.values().stream())
            .mapToInt(coach -> coach.totalSeats)
            .sum();
        
        int availableSeats = trainDatabase.values().stream()
            .flatMap(train -> train.coaches.values().stream())
            .mapToInt(coach -> coach.getAvailableSeats())
            .sum();
        
        return new NodeStats(
            nodeId,
            region,
            trainDatabase.size(),
            totalSeats,
            availableSeats,
            processedBookings.get(),
            successfulBookings.get(),
            bookingQueue.size()
        );
    }
    
    public static class NodeStats {
        public final String nodeId;
        public final String region;
        public final int trains;
        public final int totalSeats;
        public final int availableSeats;
        public final int processedBookings;
        public final int successfulBookings;
        public final int queueSize;
        
        public NodeStats(String nodeId, String region, int trains, int totalSeats,
                        int availableSeats, int processedBookings, int successfulBookings,
                        int queueSize) {
            this.nodeId = nodeId;
            this.region = region;
            this.trains = trains;
            this.totalSeats = totalSeats;
            this.availableSeats = availableSeats;
            this.processedBookings = processedBookings;
            this.successfulBookings = successfulBookings;
            this.queueSize = queueSize;
        }
        
        @Override
        public String toString() {
            double successRate = processedBookings > 0 ? 
                (double) successfulBookings / processedBookings * 100 : 0;
            
            return String.format("Node{id=%s, region=%s, trains=%d, seats=%d/%d, " +
                               "bookings=%d, success=%.1f%%, queue=%d}",
                               nodeId, region, trains, availableSeats, totalSeats,
                               processedBookings, successRate, queueSize);
        }
    }
}

/**
 * Main demonstration class
 */
public class IRCTCDistributedBookingDemo {
    
    public static void main(String[] args) throws InterruptedException, ExecutionException {
        System.out.println("🚂 IRCTC Distributed Seat Allocation System");
        System.out.println("=" .repeat(60));
        
        // Create booking nodes for different regions
        IRCTCBookingNode westernNode = new IRCTCBookingNode("irctc-west-01", "Western");
        IRCTCBookingNode northernNode = new IRCTCBookingNode("irctc-north-01", "Northern");
        IRCTCBookingNode southernNode = new IRCTCBookingNode("irctc-south-01", "Southern");
        
        // Setup cluster
        System.out.println("\n🏢 Setting up IRCTC distributed booking cluster...");
        westernNode.addClusterNode(northernNode);
        westernNode.addClusterNode(southernNode);
        northernNode.addClusterNode(westernNode);
        northernNode.addClusterNode(southernNode);
        southernNode.addClusterNode(westernNode);
        southernNode.addClusterNode(northernNode);
        
        // Start all nodes
        westernNode.start();
        northernNode.start();
        southernNode.start();
        
        System.out.println("✅ All IRCTC booking nodes started");
        
        // Show initial stats
        System.out.println("\n📊 Initial Cluster Statistics:");
        System.out.println("  " + westernNode.getStats());
        System.out.println("  " + northernNode.getStats());
        System.out.println("  " + southernNode.getStats());
        
        // Simulate concurrent booking requests
        System.out.println("\n🎫 Simulating concurrent Tatkal booking rush...");
        
        List<BookingRequest> bookingRequests = Arrays.asList(
            new BookingRequest("REQ001", "PASS001", "Rahul Sharma", "12951", "AC2", 2, "Mumbai Central", "New Delhi"),
            new BookingRequest("REQ002", "PASS002", "Priya Patel", "12951", "AC1", 1, "Mumbai Central", "New Delhi"),
            new BookingRequest("REQ003", "PASS003", "Arjun Singh", "12313", "AC2", 4, "New Delhi", "Sealdah"),
            new BookingRequest("REQ004", "PASS004", "Sneha Gupta", "12007", "CC", 3, "Chennai Central", "Bangalore City"),
            new BookingRequest("REQ005", "PASS005", "Amit Kumar", "12951", "SL", 6, "Mumbai Central", "New Delhi"),
            new BookingRequest("REQ006", "PASS006", "Deepika Reddy", "12007", "EC", 2, "Chennai Central", "Bangalore City"),
            new BookingRequest("REQ007", "PASS007", "Vikash Yadav", "12313", "AC3", 3, "New Delhi", "Sealdah"),
            new BookingRequest("REQ008", "PASS008", "Kiran Nair", "12951", "AC2", 2, "Mumbai Central", "New Delhi")
        );
        
        // Submit requests to different nodes (simulating load balancing)
        List<CompletableFuture<BookingResult>> futures = new ArrayList<>();
        
        for (int i = 0; i < bookingRequests.size(); i++) {
            BookingRequest request = bookingRequests.get(i);
            IRCTCBookingNode node;
            
            // Round-robin distribution
            switch (i % 3) {
                case 0: node = westernNode; break;
                case 1: node = northernNode; break;
                default: node = southernNode; break;
            }
            
            System.out.printf("Submitting %s to node %s%n", request.requestId, node.getStats().nodeId);
            futures.add(node.submitBookingRequest(request));
        }
        
        // Wait for all bookings to complete
        System.out.println("\n⏳ Processing booking requests...");
        Thread.sleep(3000);
        
        // Collect and display results
        System.out.println("\n📋 Booking Results:");
        for (CompletableFuture<BookingResult> future : futures) {
            try {
                BookingResult result = future.get(10, TimeUnit.SECONDS);
                String status = result.status == BookingResult.Status.SUCCESS ? "✅" : "❌";
                System.out.printf("%s %s%n", status, result);
                
                if (result.status == BookingResult.Status.SUCCESS) {
                    System.out.printf("    Allocated seats: %s%n", 
                                     result.allocatedSeats.stream()
                                         .map(Object::toString)
                                         .collect(Collectors.joining(", ")));
                }
            } catch (TimeoutException e) {
                System.out.println("❌ Booking request timed out");
            }
        }
        
        // Show final stats
        System.out.println("\n📈 Final Cluster Statistics:");
        System.out.println("  " + westernNode.getStats());
        System.out.println("  " + northernNode.getStats());
        System.out.println("  " + southernNode.getStats());
        
        // Test cross-region booking
        System.out.println("\n🌏 Testing cross-region booking...");
        BookingRequest crossRegionRequest = new BookingRequest(
            "REQ009", "PASS009", "Cross Region User", "12007", "CC", 1, 
            "Chennai Central", "Bangalore City");
        
        // Submit to Western node (which doesn't have Southern region trains)
        CompletableFuture<BookingResult> crossRegionFuture = westernNode.submitBookingRequest(crossRegionRequest);
        BookingResult crossRegionResult = crossRegionFuture.get(5, TimeUnit.SECONDS);
        
        String crossStatus = crossRegionResult.status == BookingResult.Status.SUCCESS ? "✅" : "❌";
        System.out.printf("%s Cross-region booking: %s%n", crossStatus, crossRegionResult);
        
        // Production insights
        System.out.println("\n💡 Production Insights:");
        System.out.println("- Distributed architecture handles 30,000+ concurrent Tatkal bookings");
        System.out.println("- Cross-region train search ensures comprehensive availability");
        System.out.println("- Coordination locks prevent double booking across multiple servers");
        System.out.println("- Queue-based processing provides backpressure during peak loads");
        System.out.println("- Regional distribution reduces latency for users");
        System.out.println("- Automatic rollback ensures data consistency on partial failures");
        System.out.println("- Horizontal scaling possible by adding more regional nodes");
        System.out.println("- Critical for handling festival season booking rushes");
        
        // Cleanup
        System.out.println("\n🧹 Shutting down IRCTC booking cluster...");
        westernNode.stop();
        northernNode.stop();
        southernNode.stop();
        
        System.out.println("Demo completed!");
    }
}
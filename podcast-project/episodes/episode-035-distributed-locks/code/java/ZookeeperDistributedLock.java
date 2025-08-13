/**
 * ZooKeeper Distributed Lock Implementation in Java
 * =================================================
 * 
 * Production-ready ZooKeeper-based distributed locking using sequential ephemeral nodes.
 * Used by companies like LinkedIn, Yahoo, and many enterprise systems.
 * 
 * Mumbai Context: ZooKeeper = Mumbai traffic control के central command जैसा है!
 * सभी signals एक central system से coordinate होते हैं.
 * 
 * Real-world usage:
 * - Apache Kafka partition leadership
 * - HBase region server coordination  
 * - Hadoop NameNode high availability
 * - Configuration management locks
 */

package com.distributedlocks.zookeeper;

import org.apache.zookeeper.*;
import org.apache.zookeeper.data.Stat;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Logger;
import java.util.logging.Level;

public class ZookeeperDistributedLock implements Watcher {
    
    private static final Logger LOGGER = Logger.getLogger(ZookeeperDistributedLock.class.getName());
    
    private ZooKeeper zooKeeper;
    private final String connectString;
    private final int sessionTimeout;
    private final String lockBasePath;
    private final String nodeId;
    
    private final AtomicBoolean connected = new AtomicBoolean(false);
    private final CountDownLatch connectionLatch = new CountDownLatch(1);
    
    // Statistics
    private final AtomicInteger locksAcquired = new AtomicInteger(0);
    private final AtomicInteger locksFailed = new AtomicInteger(0);
    private final AtomicInteger locksReleased = new AtomicInteger(0);
    
    public ZookeeperDistributedLock(String connectString, int sessionTimeout, String lockBasePath) {
        this.connectString = connectString;
        this.sessionTimeout = sessionTimeout;
        this.lockBasePath = lockBasePath;
        this.nodeId = UUID.randomUUID().toString().substring(0, 8);
        
        try {
            connect();
        } catch (IOException | InterruptedException e) {
            throw new RuntimeException("Failed to connect to ZooKeeper", e);
        }
    }
    
    private void connect() throws IOException, InterruptedException {
        this.zooKeeper = new ZooKeeper(connectString, sessionTimeout, this);
        
        // Wait for connection
        if (!connectionLatch.await(sessionTimeout, TimeUnit.MILLISECONDS)) {
            throw new RuntimeException("Failed to connect to ZooKeeper within timeout");
        }
        
        // Ensure base path exists
        createPathIfNotExists(lockBasePath);
        
        LOGGER.info(String.format("✅ Connected to ZooKeeper: %s (node: %s)", 
            connectString, nodeId));
    }
    
    @Override
    public void process(WatchedEvent event) {
        Event.KeeperState state = event.getState();
        
        if (state == Event.KeeperState.SyncConnected) {
            connected.set(true);
            connectionLatch.countDown();
            LOGGER.info("🔗 ZooKeeper connected");
        } else if (state == Event.KeeperState.Disconnected) {
            connected.set(false);
            LOGGER.warning("⚠️ ZooKeeper disconnected");
        } else if (state == Event.KeeperState.Expired) {
            connected.set(false);
            LOGGER.warning("💀 ZooKeeper session expired");
        }
    }
    
    private void createPathIfNotExists(String path) {
        try {
            if (zooKeeper.exists(path, false) == null) {
                String[] parts = path.split("/");
                StringBuilder currentPath = new StringBuilder();
                
                for (String part : parts) {
                    if (part.isEmpty()) continue;
                    
                    currentPath.append("/").append(part);
                    
                    try {
                        zooKeeper.create(currentPath.toString(), new byte[0], 
                            ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.PERSISTENT);
                    } catch (KeeperException.NodeExistsException e) {
                        // Path already exists, continue
                    }
                }
            }
        } catch (KeeperException | InterruptedException e) {
            LOGGER.log(Level.WARNING, "Failed to create path: " + path, e);
        }
    }
    
    /**
     * Acquire distributed lock using ZooKeeper sequential ephemeral nodes
     */
    public LockHandle acquireLock(String resource, long timeoutMillis) {
        if (!connected.get()) {
            LOGGER.warning("❌ Not connected to ZooKeeper");
            return null;
        }
        
        String resourcePath = lockBasePath + "/" + resource;
        createPathIfNotExists(resourcePath);
        
        try {
            // Create sequential ephemeral node
            String lockNodePrefix = resourcePath + "/lock_" + nodeId + "_";
            String actualPath = zooKeeper.create(lockNodePrefix, 
                getLockMetadata(resource).getBytes(),
                ZooDefs.Ids.OPEN_ACL_UNSAFE,
                CreateMode.EPHEMERAL_SEQUENTIAL);
            
            // Extract sequence number
            String nodeName = actualPath.substring(actualPath.lastIndexOf('/') + 1);
            
            // Wait for lock acquisition
            long startTime = System.currentTimeMillis();
            long deadline = startTime + timeoutMillis;
            
            while (System.currentTimeMillis() < deadline) {
                // Get all children and sort
                List<String> children = zooKeeper.getChildren(resourcePath, false);
                Collections.sort(children);
                
                if (children.isEmpty()) {
                    LOGGER.warning("No children found in lock path");
                    break;
                }
                
                // Find our position
                int ourIndex = children.indexOf(nodeName);
                if (ourIndex == -1) {
                    LOGGER.error("Our node disappeared!");
                    return null;
                }
                
                // If we're first, we have the lock!
                if (ourIndex == 0) {
                    LockHandle handle = new LockHandle(resource, actualPath, this);
                    locksAcquired.incrementAndGet();
                    
                    LOGGER.info(String.format("🔒 ZK Lock acquired: %s (path: %s)", 
                        resource, actualPath));
                    return handle;
                }
                
                // Watch the node before us
                String prevNodeName = children.get(ourIndex - 1);
                String prevNodePath = resourcePath + "/" + prevNodeName;
                
                CountDownLatch watchLatch = new CountDownLatch(1);
                
                Watcher nodeWatcher = event -> {
                    if (event.getType() == Event.EventType.NodeDeleted) {
                        watchLatch.countDown();
                    }
                };
                
                // Set watch and check if node still exists
                Stat stat = zooKeeper.exists(prevNodePath, nodeWatcher);
                if (stat == null) {
                    // Node was deleted, loop again to check our status
                    continue;
                }
                
                LOGGER.debug(String.format("⏳ Waiting for lock, watching: %s", prevNodePath));
                
                // Wait for previous node to be deleted or timeout
                long remainingTime = deadline - System.currentTimeMillis();
                if (remainingTime > 0) {
                    watchLatch.await(remainingTime, TimeUnit.MILLISECONDS);
                }
            }
            
            // Timeout occurred - cleanup our node
            try {
                zooKeeper.delete(actualPath, -1);
            } catch (KeeperException e) {
                LOGGER.log(Level.WARNING, "Failed to cleanup lock node", e);
            }
            
            locksFailed.incrementAndGet();
            LOGGER.warning(String.format("⏰ Lock acquisition timeout for %s", resource));
            return null;
            
        } catch (KeeperException | InterruptedException e) {
            locksFailed.incrementAndGet();
            LOGGER.log(Level.SEVERE, String.format("❌ Failed to acquire lock for %s", resource), e);
            return null;
        }
    }
    
    /**
     * Release lock by deleting the ephemeral node
     */
    public boolean releaseLock(LockHandle handle) {
        try {
            zooKeeper.delete(handle.getLockPath(), -1);
            locksReleased.incrementAndGet();
            
            LOGGER.info(String.format("🔓 ZK Lock released: %s", handle.getResource()));
            return true;
            
        } catch (KeeperException.NoNodeException e) {
            LOGGER.warning("Lock node already deleted");
            return true;
        } catch (KeeperException | InterruptedException e) {
            LOGGER.log(Level.SEVERE, "❌ Failed to release lock", e);
            return false;
        }
    }
    
    private String getLockMetadata(String resource) {
        return String.format("{\"resource\":\"%s\",\"nodeId\":\"%s\",\"acquiredAt\":%d}",
            resource, nodeId, System.currentTimeMillis());
    }
    
    /**
     * Get current lock statistics
     */
    public LockStatistics getStatistics() {
        return new LockStatistics(
            locksAcquired.get(),
            locksFailed.get(),
            locksReleased.get()
        );
    }
    
    /**
     * Close ZooKeeper connection
     */
    public void close() {
        try {
            if (zooKeeper != null) {
                zooKeeper.close();
            }
            LOGGER.info("🔌 ZooKeeper connection closed");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            LOGGER.warning("Interrupted while closing ZooKeeper connection");
        }
    }
    
    // Helper classes
    public static class LockHandle {
        private final String resource;
        private final String lockPath;
        private final ZookeeperDistributedLock lockManager;
        private final long acquiredAt;
        
        public LockHandle(String resource, String lockPath, ZookeeperDistributedLock lockManager) {
            this.resource = resource;
            this.lockPath = lockPath;
            this.lockManager = lockManager;
            this.acquiredAt = System.currentTimeMillis();
        }
        
        public String getResource() { return resource; }
        public String getLockPath() { return lockPath; }
        public long getAcquiredAt() { return acquiredAt; }
        
        public boolean release() {
            return lockManager.releaseLock(this);
        }
    }
    
    public static class LockStatistics {
        private final int acquired;
        private final int failed;
        private final int released;
        
        public LockStatistics(int acquired, int failed, int released) {
            this.acquired = acquired;
            this.failed = failed;
            this.released = released;
        }
        
        public int getAcquired() { return acquired; }
        public int getFailed() { return failed; }
        public int getReleased() { return released; }
        public double getSuccessRate() {
            int total = acquired + failed;
            return total == 0 ? 0.0 : (double) acquired / total * 100.0;
        }
    }
}

/**
 * BookMyShow Seat Booking System using ZooKeeper Locks
 * ==================================================
 * 
 * Mumbai Story: BookMyShow में movie tickets book करते time हजारों लोग एक साथ
 * same seats के लिए try करते हैं. ZooKeeper locks ensure करते हैं कि same
 * seat multiple लोगों को न मिल जाए!
 */
class BookMyShowSeatManager {
    
    private static final Logger LOGGER = Logger.getLogger(BookMyShowSeatManager.class.getName());
    
    private final ZookeeperDistributedLock zkLock;
    private final Map<String, MovieShow> movieShows;
    private final Map<String, SeatBooking> bookingHistory;
    
    // Booking statistics
    private final AtomicInteger bookingAttempts = new AtomicInteger(0);
    private final AtomicInteger successfulBookings = new AtomicInteger(0);
    private final AtomicInteger failedBookings = new AtomicInteger(0);
    private final AtomicInteger conflictsPrevented = new AtomicInteger(0);
    
    public BookMyShowSeatManager(ZookeeperDistributedLock zkLock) {
        this.zkLock = zkLock;
        this.movieShows = new ConcurrentHashMap<>();
        this.bookingHistory = new ConcurrentHashMap<>();
        
        initializeMovieShows();
        LOGGER.info("🎬 BookMyShow Seat Manager initialized");
    }
    
    private void initializeMovieShows() {
        // Popular movies in Mumbai theaters
        String[] theaters = {"PVR_Phoenix", "INOX_Malad", "Cinepolis_Andheri", "Fun_Republic_Bandra"};
        String[] movies = {"RRR", "KGF_Chapter_2", "Pushpa", "Sooryavanshi", "83_The_Film"};
        
        for (String theater : theaters) {
            for (String movie : movies) {
                String showId = theater + "_" + movie + "_7PM";
                
                // Create show with 100 seats (10x10 grid)
                Map<String, SeatInfo> seats = new HashMap<>();
                char[] rows = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'};
                
                for (char row : rows) {
                    for (int col = 1; col <= 10; col++) {
                        String seatId = row + String.valueOf(col);
                        SeatType seatType = (row <= 'C') ? SeatType.PREMIUM : 
                                          (row <= 'G') ? SeatType.GOLD : SeatType.REGULAR;
                        seats.put(seatId, new SeatInfo(seatId, seatType, SeatStatus.AVAILABLE));
                    }
                }
                
                movieShows.put(showId, new MovieShow(showId, movie, theater, seats));
            }
        }
    }
    
    /**
     * Book movie seat with distributed locking
     */
    public BookingResult bookSeat(String showId, String seatId, String customerId) {
        bookingAttempts.incrementAndGet();
        
        // Create lock resource for the specific seat
        String lockResource = String.format("seat_booking_%s_%s", showId, seatId);
        
        ZookeeperDistributedLock.LockHandle lockHandle = zkLock.acquireLock(lockResource, 15000);
        
        if (lockHandle == null) {
            failedBookings.incrementAndGet();
            return new BookingResult(false, "Seat booking busy - please try again", 
                "LOCK_ACQUISITION_FAILED");
        }
        
        try {
            // Check if show exists
            MovieShow show = movieShows.get(showId);
            if (show == null) {
                failedBookings.incrementAndGet();
                return new BookingResult(false, "Movie show not found", "INVALID_SHOW");
            }
            
            // Check if seat exists and is available
            SeatInfo seatInfo = show.getSeats().get(seatId);
            if (seatInfo == null) {
                failedBookings.incrementAndGet();
                return new BookingResult(false, "Invalid seat number", "INVALID_SEAT");
            }
            
            if (seatInfo.getStatus() != SeatStatus.AVAILABLE) {
                conflictsPrevented.incrementAndGet();
                return new BookingResult(false, "Seat already booked", "SEAT_UNAVAILABLE");
            }
            
            // Simulate booking processing time
            try {
                Thread.sleep(100 + new Random().nextInt(200)); // 100-300ms processing
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            
            // Book the seat
            seatInfo.setStatus(SeatStatus.BOOKED);
            
            String bookingId = String.format("BMS_%d_%s", 
                System.currentTimeMillis(), customerId.substring(0, 4));
            
            SeatBooking booking = new SeatBooking(
                bookingId,
                showId,
                seatId,
                customerId,
                seatInfo.getType(),
                calculateSeatPrice(seatInfo.getType()),
                System.currentTimeMillis()
            );
            
            bookingHistory.put(bookingId, booking);
            successfulBookings.incrementAndGet();
            
            LOGGER.info(String.format("🎫 Seat booked: %s - %s %s for %s (₹%.2f)",
                bookingId, showId, seatId, customerId, booking.getPrice()));
            
            return new BookingResult(true, 
                String.format("Seat %s booked successfully! Booking ID: %s", seatId, bookingId),
                booking);
                
        } finally {
            lockHandle.release();
        }
    }
    
    /**
     * Cancel booking with locking
     */
    public boolean cancelBooking(String bookingId) {
        SeatBooking booking = bookingHistory.get(bookingId);
        if (booking == null) {
            return false;
        }
        
        String lockResource = String.format("seat_booking_%s_%s", 
            booking.getShowId(), booking.getSeatId());
            
        ZookeeperDistributedLock.LockHandle lockHandle = zkLock.acquireLock(lockResource, 10000);
        
        if (lockHandle == null) {
            return false;
        }
        
        try {
            // Free the seat
            MovieShow show = movieShows.get(booking.getShowId());
            if (show != null) {
                SeatInfo seatInfo = show.getSeats().get(booking.getSeatId());
                if (seatInfo != null) {
                    seatInfo.setStatus(SeatStatus.AVAILABLE);
                }
            }
            
            // Remove booking
            bookingHistory.remove(bookingId);
            
            LOGGER.info(String.format("❌ Booking cancelled: %s - %s %s", 
                bookingId, booking.getShowId(), booking.getSeatId()));
            
            return true;
            
        } finally {
            lockHandle.release();
        }
    }
    
    private double calculateSeatPrice(SeatType seatType) {
        switch (seatType) {
            case PREMIUM: return 350.0;
            case GOLD: return 250.0;
            case REGULAR: return 150.0;
            default: return 150.0;
        }
    }
    
    /**
     * Get show availability
     */
    public ShowAvailability getShowAvailability(String showId) {
        MovieShow show = movieShows.get(showId);
        if (show == null) {
            return null;
        }
        
        Map<SeatStatus, Long> statusCounts = show.getSeats().values().stream()
            .collect(java.util.stream.Collectors.groupingBy(
                SeatInfo::getStatus,
                java.util.stream.Collectors.counting()
            ));
        
        return new ShowAvailability(
            showId,
            statusCounts.getOrDefault(SeatStatus.AVAILABLE, 0L).intValue(),
            statusCounts.getOrDefault(SeatStatus.BOOKED, 0L).intValue(),
            show.getSeats().size()
        );
    }
    
    /**
     * Get booking statistics
     */
    public BookingStatistics getStatistics() {
        int total = bookingAttempts.get();
        int successful = successfulBookings.get();
        int failed = failedBookings.get();
        int conflicts = conflictsPrevented.get();
        
        double successRate = total == 0 ? 0.0 : (double) successful / total * 100.0;
        double totalRevenue = bookingHistory.values().stream()
            .mapToDouble(SeatBooking::getPrice)
            .sum();
        
        return new BookingStatistics(total, successful, failed, conflicts, successRate, totalRevenue);
    }
    
    // Helper classes
    public enum SeatType {
        PREMIUM, GOLD, REGULAR
    }
    
    public enum SeatStatus {
        AVAILABLE, BOOKED, BLOCKED
    }
    
    public static class SeatInfo {
        private final String seatId;
        private final SeatType type;
        private volatile SeatStatus status;
        
        public SeatInfo(String seatId, SeatType type, SeatStatus status) {
            this.seatId = seatId;
            this.type = type;
            this.status = status;
        }
        
        // Getters and setters
        public String getSeatId() { return seatId; }
        public SeatType getType() { return type; }
        public SeatStatus getStatus() { return status; }
        public void setStatus(SeatStatus status) { this.status = status; }
    }
    
    public static class MovieShow {
        private final String showId;
        private final String movieName;
        private final String theater;
        private final Map<String, SeatInfo> seats;
        
        public MovieShow(String showId, String movieName, String theater, Map<String, SeatInfo> seats) {
            this.showId = showId;
            this.movieName = movieName;
            this.theater = theater;
            this.seats = seats;
        }
        
        // Getters
        public String getShowId() { return showId; }
        public String getMovieName() { return movieName; }
        public String getTheater() { return theater; }
        public Map<String, SeatInfo> getSeats() { return seats; }
    }
    
    public static class SeatBooking {
        private final String bookingId;
        private final String showId;
        private final String seatId;
        private final String customerId;
        private final SeatType seatType;
        private final double price;
        private final long bookedAt;
        
        public SeatBooking(String bookingId, String showId, String seatId, String customerId,
                          SeatType seatType, double price, long bookedAt) {
            this.bookingId = bookingId;
            this.showId = showId;
            this.seatId = seatId;
            this.customerId = customerId;
            this.seatType = seatType;
            this.price = price;
            this.bookedAt = bookedAt;
        }
        
        // Getters
        public String getBookingId() { return bookingId; }
        public String getShowId() { return showId; }
        public String getSeatId() { return seatId; }
        public String getCustomerId() { return customerId; }
        public SeatType getSeatType() { return seatType; }
        public double getPrice() { return price; }
        public long getBookedAt() { return bookedAt; }
    }
    
    public static class BookingResult {
        private final boolean success;
        private final String message;
        private final String errorCode;
        private final SeatBooking booking;
        
        public BookingResult(boolean success, String message, String errorCode) {
            this.success = success;
            this.message = message;
            this.errorCode = errorCode;
            this.booking = null;
        }
        
        public BookingResult(boolean success, String message, SeatBooking booking) {
            this.success = success;
            this.message = message;
            this.errorCode = null;
            this.booking = booking;
        }
        
        // Getters
        public boolean isSuccess() { return success; }
        public String getMessage() { return message; }
        public String getErrorCode() { return errorCode; }
        public SeatBooking getBooking() { return booking; }
    }
    
    public static class ShowAvailability {
        private final String showId;
        private final int availableSeats;
        private final int bookedSeats;
        private final int totalSeats;
        
        public ShowAvailability(String showId, int availableSeats, int bookedSeats, int totalSeats) {
            this.showId = showId;
            this.availableSeats = availableSeats;
            this.bookedSeats = bookedSeats;
            this.totalSeats = totalSeats;
        }
        
        // Getters
        public String getShowId() { return showId; }
        public int getAvailableSeats() { return availableSeats; }
        public int getBookedSeats() { return bookedSeats; }
        public int getTotalSeats() { return totalSeats; }
        public double getOccupancyRate() { 
            return totalSeats == 0 ? 0.0 : (double) bookedSeats / totalSeats * 100.0; 
        }
    }
    
    public static class BookingStatistics {
        private final int totalAttempts;
        private final int successfulBookings;
        private final int failedBookings;
        private final int conflictsPrevented;
        private final double successRate;
        private final double totalRevenue;
        
        public BookingStatistics(int totalAttempts, int successfulBookings, int failedBookings,
                               int conflictsPrevented, double successRate, double totalRevenue) {
            this.totalAttempts = totalAttempts;
            this.successfulBookings = successfulBookings;
            this.failedBookings = failedBookings;
            this.conflictsPrevented = conflictsPrevented;
            this.successRate = successRate;
            this.totalRevenue = totalRevenue;
        }
        
        // Getters
        public int getTotalAttempts() { return totalAttempts; }
        public int getSuccessfulBookings() { return successfulBookings; }
        public int getFailedBookings() { return failedBookings; }
        public int getConflictsPrevented() { return conflictsPrevented; }
        public double getSuccessRate() { return successRate; }
        public double getTotalRevenue() { return totalRevenue; }
    }
}

/**
 * Demo class to test BookMyShow seat booking
 */
class BookMyShowDemo {
    
    public static void main(String[] args) throws InterruptedException {
        Logger.getGlobal().setLevel(Level.INFO);
        
        // Initialize ZooKeeper lock
        ZookeeperDistributedLock zkLock = new ZookeeperDistributedLock(
            "localhost:2181", 
            30000, 
            "/bookmyshow/locks"
        );
        
        BookMyShowSeatManager seatManager = new BookMyShowSeatManager(zkLock);
        
        // Simulate concurrent seat bookings
        simulateMovieBookings(seatManager);
        
        // Cleanup
        zkLock.close();
    }
    
    private static void simulateMovieBookings(BookMyShowSeatManager seatManager) 
            throws InterruptedException {
        
        System.out.println("🎬 Starting BookMyShow seat booking simulation...\n");
        
        ExecutorService executor = Executors.newFixedThreadPool(15);
        CountDownLatch latch = new CountDownLatch(25);
        
        // Popular show
        String popularShow = "PVR_Phoenix_RRR_7PM";
        
        // Popular seats (center rows)
        String[] popularSeats = {"E5", "E6", "F5", "F6", "G5", "G6", "E4", "E7", "F4", "F7"};
        
        Random random = new Random();
        
        // Simulate concurrent booking attempts
        for (int i = 0; i < 25; i++) {
            final int customerNum = i + 1;
            
            executor.submit(() -> {
                try {
                    String customerId = String.format("customer_%04d", customerNum);
                    String seatId = popularSeats[random.nextInt(popularSeats.length)];
                    
                    BookMyShowSeatManager.BookingResult result = 
                        seatManager.bookSeat(popularShow, seatId, customerId);
                    
                    System.out.println(String.format("%s Customer %s booking %s: %s",
                        result.isSuccess() ? "✅" : "❌", 
                        customerId, 
                        seatId,
                        result.getMessage()));
                        
                } catch (Exception e) {
                    System.err.println("Booking failed: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
            
            Thread.sleep(20); // Small delay between booking attempts
        }
        
        latch.await(30, TimeUnit.SECONDS);
        executor.shutdown();
        
        // Show final statistics
        BookMyShowSeatManager.BookingStatistics stats = seatManager.getStatistics();
        BookMyShowSeatManager.ShowAvailability availability = seatManager.getShowAvailability(popularShow);
        ZookeeperDistributedLock.LockStatistics lockStats = zkLock.getStatistics();
        
        System.out.println("\n📊 BookMyShow Booking Results:");
        System.out.println("Total booking attempts: " + stats.getTotalAttempts());
        System.out.println("Successful bookings: " + stats.getSuccessfulBookings());
        System.out.println("Failed bookings: " + stats.getFailedBookings());
        System.out.println("Conflicts prevented: " + stats.getConflictsPrevented());
        System.out.println("Success rate: " + String.format("%.2f%%", stats.getSuccessRate()));
        System.out.println("Total revenue: ₹" + String.format("%.2f", stats.getTotalRevenue()));
        
        if (availability != null) {
            System.out.println("\n🎭 Show Status: " + availability.getShowId());
            System.out.println("Available seats: " + availability.getAvailableSeats());
            System.out.println("Booked seats: " + availability.getBookedSeats());
            System.out.println("Occupancy rate: " + String.format("%.2f%%", availability.getOccupancyRate()));
        }
        
        System.out.println("\n🔒 ZooKeeper Lock Statistics:");
        System.out.println("Locks acquired: " + lockStats.getAcquired());
        System.out.println("Lock failures: " + lockStats.getFailed());
        System.out.println("Locks released: " + lockStats.getReleased());
        System.out.println("Lock success rate: " + String.format("%.2f%%", lockStats.getSuccessRate()));
    }
}
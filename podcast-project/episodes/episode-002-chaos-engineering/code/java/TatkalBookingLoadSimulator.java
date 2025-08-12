/**
 * IRCTC Tatkal Booking Load Simulator with Chaos Engineering
 * तत्काल टिकट बुकिंग system की chaos testing और load simulation
 * 
 * Indian Context: IRCTC tatkal booking के दौरान server behavior analysis
 * Real Example: Rajdhani Express tatkal opening के first 2 minutes में system behavior
 */

import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

public class TatkalBookingLoadSimulator {
    
    // IRCTC system configuration - realistic parameters
    private static final int MAX_CONCURRENT_USERS = 2_000_000;    // 20 lakh concurrent users
    private static final int DATABASE_CONNECTIONS = 1000;         // Limited DB connections
    private static final int PAYMENT_GATEWAY_TPS = 5000;         // Payment transactions per second
    private static final int SESSION_TIMEOUT_SECONDS = 300;      // 5 minute session timeout
    
    // Tatkal booking timings
    private static final LocalTime AC_TATKAL_TIME = LocalTime.of(10, 0);      // 10 AM
    private static final LocalTime NON_AC_TATKAL_TIME = LocalTime.of(11, 0);  // 11 AM
    
    // Popular routes और उनके demand patterns
    private enum PopularRoute {
        MUMBAI_DELHI("Mumbai-Delhi", "12951", 0.9, 750),           // Rajdhani - highest demand
        DELHI_MUMBAI("Delhi-Mumbai", "12952", 0.9, 750),           // Return Rajdhani
        MUMBAI_BANGALORE("Mumbai-Bangalore", "12295", 0.8, 500),   // Udyan Express
        DELHI_KOLKATA("Delhi-Kolkata", "12313", 0.7, 400),        // Sealdah Rajdhani
        CHENNAI_BANGALORE("Chennai-Bangalore", "12607", 0.6, 300); // Lalbagh Express
        
        public final String routeName;
        public final String trainNumber;
        public final double demandIntensity;    // 0.0 to 1.0
        public final int availableSeats;       // Tatkal quota
        
        PopularRoute(String routeName, String trainNumber, double demandIntensity, int availableSeats) {
            this.routeName = routeName;
            this.trainNumber = trainNumber;
            this.demandIntensity = demandIntensity;
            this.availableSeats = availableSeats;
        }
    }
    
    // System failure modes during high load
    private enum FailureMode {
        DATABASE_CONNECTION_POOL_EXHAUSTED(0.25, "DB connection pool full"),
        PAYMENT_GATEWAY_TIMEOUT(0.20, "Payment processing timeout"),
        SESSION_SERVER_OVERLOAD(0.18, "Session management failure"),
        CAPTCHA_SERVICE_DOWN(0.15, "Captcha verification failed"),
        OTP_SMS_DELAY(0.12, "OTP delivery delayed"),
        LOAD_BALANCER_FAILURE(0.10, "Load balancer unhealthy");
        
        public final double probability;
        public final String description;
        
        FailureMode(double probability, String description) {
            this.probability = probability;
            this.description = description;
        }
    }
    
    // User behavior simulation
    private static class TatkalUser {
        final String userId;
        final PopularRoute preferredRoute;
        final LocalDateTime loginTime;
        final int retryAttempts;
        final boolean isPremiumUser;     // Premium users get slight advantage
        final String userLocation;      // Mumbai, Delhi, etc.
        
        TatkalUser(String userId, PopularRoute preferredRoute, LocalDateTime loginTime,
                  int retryAttempts, boolean isPremiumUser, String userLocation) {
            this.userId = userId;
            this.preferredRoute = preferredRoute;
            this.loginTime = loginTime;
            this.retryAttempts = retryAttempts;
            this.isPremiumUser = isPremiumUser;
            this.userLocation = userLocation;
        }
    }
    
    // Booking attempt result
    private static class BookingResult {
        final String userId;
        final PopularRoute route;
        final boolean success;
        final FailureMode failureReason;
        final Duration responseTime;
        final int attemptNumber;
        final LocalDateTime timestamp;
        
        BookingResult(String userId, PopularRoute route, boolean success, 
                     FailureMode failureReason, Duration responseTime,
                     int attemptNumber, LocalDateTime timestamp) {
            this.userId = userId;
            this.route = route;
            this.success = success;
            this.failureReason = failureReason;
            this.responseTime = responseTime;
            this.attemptNumber = attemptNumber;
            this.timestamp = timestamp;
        }
    }
    
    // System state tracking
    private final AtomicInteger currentConcurrentUsers = new AtomicInteger(0);
    private final AtomicInteger dbConnectionsInUse = new AtomicInteger(0);
    private final AtomicInteger paymentTransactionsInProgress = new AtomicInteger(0);
    private final AtomicLong totalBookingAttempts = new AtomicLong(0);
    private final AtomicLong successfulBookings = new AtomicLong(0);
    
    // Chaos engineering controls
    private volatile boolean chaosEnabled = false;
    private volatile double chaosIntensity = 0.1;  // 10% base chaos
    
    private final ExecutorService executorService;
    private final Random random = new Random();
    
    public TatkalBookingLoadSimulator(int threadPoolSize) {
        this.executorService = Executors.newFixedThreadPool(threadPoolSize);
    }
    
    /**
     * Simulate realistic tatkal booking load for specific route
     */
    public CompletableFuture<BookingResult> simulateBookingAttempt(TatkalUser user, int attemptNumber) {
        
        return CompletableFuture.supplyAsync(() -> {
            LocalDateTime startTime = LocalDateTime.now();
            totalBookingAttempts.incrementAndGet();
            
            try {
                // Check system capacity
                int concurrent = currentConcurrentUsers.incrementAndGet();
                
                // System overload protection
                if (concurrent > MAX_CONCURRENT_USERS) {
                    return new BookingResult(user.userId, user.preferredRoute, false,
                        FailureMode.LOAD_BALANCER_FAILURE, 
                        Duration.between(startTime, LocalDateTime.now()),
                        attemptNumber, startTime);
                }
                
                // Simulate realistic processing steps
                return processBookingSteps(user, attemptNumber, startTime);
                
            } finally {
                currentConcurrentUsers.decrementAndGet();
            }
            
        }, executorService);
    }
    
    private BookingResult processBookingSteps(TatkalUser user, int attemptNumber, LocalDateTime startTime) {
        
        try {
            // Step 1: Session validation (quick)
            Thread.sleep(random.nextInt(100) + 50); // 50-150ms
            
            if (chaosEnabled && random.nextDouble() < chaosIntensity * 0.3) {
                return createFailureResult(user, FailureMode.SESSION_SERVER_OVERLOAD, 
                                         attemptNumber, startTime);
            }
            
            // Step 2: Database connection acquisition
            int dbConnections = dbConnectionsInUse.incrementAndGet();
            try {
                if (dbConnections > DATABASE_CONNECTIONS) {
                    return createFailureResult(user, FailureMode.DATABASE_CONNECTION_POOL_EXHAUSTED,
                                             attemptNumber, startTime);
                }
                
                // Step 3: Seat availability check (database heavy)
                Thread.sleep(random.nextInt(500) + 200); // 200-700ms
                
                if (chaosEnabled && random.nextDouble() < chaosIntensity * 0.5) {
                    return createFailureResult(user, FailureMode.DATABASE_CONNECTION_POOL_EXHAUSTED,
                                             attemptNumber, startTime);
                }
                
                // Step 4: Seat booking logic
                if (!checkSeatAvailability(user.preferredRoute)) {
                    // Seats exhausted - not a system failure
                    return new BookingResult(user.userId, user.preferredRoute, false,
                        null, Duration.between(startTime, LocalDateTime.now()),
                        attemptNumber, startTime);
                }
                
                // Step 5: CAPTCHA verification
                Thread.sleep(random.nextInt(200) + 100); // 100-300ms
                
                if (chaosEnabled && random.nextDouble() < chaosIntensity * 0.2) {
                    return createFailureResult(user, FailureMode.CAPTCHA_SERVICE_DOWN,
                                             attemptNumber, startTime);
                }
                
                // Step 6: Payment processing
                return processPayment(user, attemptNumber, startTime);
                
            } finally {
                dbConnectionsInUse.decrementAndGet();
            }
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return createFailureResult(user, FailureMode.DATABASE_CONNECTION_POOL_EXHAUSTED,
                                     attemptNumber, startTime);
        }
    }
    
    private BookingResult processPayment(TatkalUser user, int attemptNumber, LocalDateTime startTime) {
        
        int paymentTxns = paymentTransactionsInProgress.incrementAndGet();
        
        try {
            // Payment gateway capacity check
            if (paymentTxns > PAYMENT_GATEWAY_TPS) {
                return createFailureResult(user, FailureMode.PAYMENT_GATEWAY_TIMEOUT,
                                         attemptNumber, startTime);
            }
            
            // Simulate payment processing time
            Thread.sleep(random.nextInt(2000) + 1000); // 1-3 seconds
            
            // Chaos injection during payment
            if (chaosEnabled && random.nextDouble() < chaosIntensity * 0.6) {
                // Payment failures are expensive and frustrating
                FailureMode[] paymentFailures = {
                    FailureMode.PAYMENT_GATEWAY_TIMEOUT,
                    FailureMode.OTP_SMS_DELAY
                };
                FailureMode selectedFailure = paymentFailures[random.nextInt(paymentFailures.length)];
                
                return createFailureResult(user, selectedFailure, attemptNumber, startTime);
            }
            
            // Success case - booking confirmed
            successfulBookings.incrementAndGet();
            
            return new BookingResult(user.userId, user.preferredRoute, true, null,
                Duration.between(startTime, LocalDateTime.now()),
                attemptNumber, startTime);
                
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return createFailureResult(user, FailureMode.PAYMENT_GATEWAY_TIMEOUT,
                                     attemptNumber, startTime);
        } finally {
            paymentTransactionsInProgress.decrementAndGet();
        }
    }
    
    private BookingResult createFailureResult(TatkalUser user, FailureMode failureMode,
                                           int attemptNumber, LocalDateTime startTime) {
        return new BookingResult(user.userId, user.preferredRoute, false, failureMode,
            Duration.between(startTime, LocalDateTime.now()),
            attemptNumber, startTime);
    }
    
    private boolean checkSeatAvailability(PopularRoute route) {
        // Simulate realistic seat exhaustion based on demand
        // Higher demand routes run out faster
        long elapsedSeconds = Duration.between(AC_TATKAL_TIME, LocalDateTime.now().toLocalTime()).getSeconds();
        
        // Seats get booked exponentially fast for high-demand routes
        double remainingProbability = Math.exp(-elapsedSeconds * route.demandIntensity / 60.0);
        
        return random.nextDouble() < remainingProbability;
    }
    
    /**
     * Run comprehensive tatkal booking chaos simulation
     */
    public void runTatkalChaosSimulation(int totalUsers, Duration simulationDuration) {
        
        System.out.println("🚂 IRCTC Tatkal Booking Chaos Engineering Simulation");
        System.out.println("⏰ Tatkal Time: " + AC_TATKAL_TIME + " (AC) / " + NON_AC_TATKAL_TIME + " (Non-AC)");
        System.out.println("👥 Simulated Users: " + totalUsers);
        System.out.println("🕐 Duration: " + simulationDuration.toMinutes() + " minutes");
        System.out.println("=" + "=".repeat(60));
        
        // Generate realistic user distribution
        List<TatkalUser> users = generateRealisticUserBase(totalUsers);
        
        // Enable chaos engineering
        chaosEnabled = true;
        chaosIntensity = 0.15; // 15% failure rate during peak load
        
        LocalDateTime simulationStart = LocalDateTime.now();
        List<CompletableFuture<BookingResult>> allBookingAttempts = new ArrayList<>();
        
        // Simulate gradual user arrival (realistic pattern)
        for (int minute = 0; minute < simulationDuration.toMinutes(); minute++) {
            
            // Users arrive in waves - most in first 2 minutes
            double arrivalIntensity = calculateArrivalIntensity(minute);
            int usersThisMinute = (int)(totalUsers * arrivalIntensity / simulationDuration.toMinutes());
            
            System.out.println(String.format("\n⏱️  Minute %d: %d users attempting booking", 
                minute + 1, usersThisMinute));
            
            // Process users for this minute
            for (int i = 0; i < usersThisMinute && (minute * usersThisMinute + i) < users.size(); i++) {
                TatkalUser user = users.get(minute * usersThisMinute + i);
                
                // Each user might make multiple attempts
                for (int attempt = 1; attempt <= user.retryAttempts; attempt++) {
                    CompletableFuture<BookingResult> bookingAttempt = 
                        simulateBookingAttempt(user, attempt);
                    allBookingAttempts.add(bookingAttempt);
                }
            }
            
            // Print system metrics every minute
            printSystemMetrics(minute + 1);
            
            try {
                Thread.sleep(1000); // 1 second per minute simulation
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        // Wait for all booking attempts to complete
        System.out.println("\n⌛ Waiting for all booking attempts to complete...");
        
        List<BookingResult> results = allBookingAttempts.stream()
            .map(CompletableFuture::join)
            .collect(Collectors.toList());
        
        // Analyze results
        analyzeSimulationResults(results, simulationStart);
    }
    
    private List<TatkalUser> generateRealisticUserBase(int totalUsers) {
        List<TatkalUser> users = new ArrayList<>();
        
        // Route popularity distribution (realistic IRCTC patterns)
        Map<PopularRoute, Double> routeDistribution = Map.of(
            PopularRoute.MUMBAI_DELHI, 0.35,    // 35% - highest demand
            PopularRoute.DELHI_MUMBAI, 0.25,    // 25% - return journey
            PopularRoute.MUMBAI_BANGALORE, 0.20, // 20% - tech corridor
            PopularRoute.DELHI_KOLKATA, 0.12,   // 12% - capital route
            PopularRoute.CHENNAI_BANGALORE, 0.08 // 8% - south India
        );
        
        // User location distribution
        String[] userLocations = {"Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Kolkata"};
        
        for (int i = 0; i < totalUsers; i++) {
            // Select route based on distribution
            PopularRoute selectedRoute = selectWeightedRoute(routeDistribution);
            
            // User characteristics
            boolean isPremium = random.nextDouble() < 0.1; // 10% premium users
            int retryAttempts = isPremium ? random.nextInt(5) + 3 : random.nextInt(3) + 1; // Premium users retry more
            String location = userLocations[random.nextInt(userLocations.length)];
            
            TatkalUser user = new TatkalUser(
                "USER_" + (i + 1),
                selectedRoute,
                LocalDateTime.now().minusMinutes(random.nextInt(10)), // Login time spread
                retryAttempts,
                isPremium,
                location
            );
            
            users.add(user);
        }
        
        return users;
    }
    
    private PopularRoute selectWeightedRoute(Map<PopularRoute, Double> distribution) {
        double rand = random.nextDouble();
        double cumulative = 0.0;
        
        for (Map.Entry<PopularRoute, Double> entry : distribution.entrySet()) {
            cumulative += entry.getValue();
            if (rand <= cumulative) {
                return entry.getKey();
            }
        }
        
        return PopularRoute.MUMBAI_DELHI; // Default fallback
    }
    
    private double calculateArrivalIntensity(int minute) {
        // Realistic user arrival pattern - most users arrive in first 2 minutes
        if (minute < 2) {
            return 0.6; // 60% of users in first 2 minutes
        } else if (minute < 5) {
            return 0.3; // 30% in next 3 minutes
        } else {
            return 0.1; // 10% spread over remaining time
        }
    }
    
    private void printSystemMetrics(int minute) {
        System.out.println(String.format("   📊 System Load: %d concurrent users", 
            currentConcurrentUsers.get()));
        System.out.println(String.format("   💾 DB Connections: %d/%d in use", 
            dbConnectionsInUse.get(), DATABASE_CONNECTIONS));
        System.out.println(String.format("   💳 Payment TPS: %d active transactions", 
            paymentTransactionsInProgress.get()));
        System.out.println(String.format("   📈 Success Rate: %.1f%%", 
            calculateCurrentSuccessRate()));
    }
    
    private double calculateCurrentSuccessRate() {
        long total = totalBookingAttempts.get();
        long successful = successfulBookings.get();
        
        return total > 0 ? (successful * 100.0 / total) : 0.0;
    }
    
    private void analyzeSimulationResults(List<BookingResult> results, LocalDateTime simulationStart) {
        
        System.out.println("\n📊 TATKAL BOOKING SIMULATION ANALYSIS");
        System.out.println("=" + "=".repeat(50));
        
        // Overall statistics
        long totalAttempts = results.size();
        long successful = results.stream().mapToLong(r -> r.success ? 1 : 0).sum();
        double successRate = (successful * 100.0) / totalAttempts;
        
        System.out.println("📈 Overall Results:");
        System.out.println(String.format("   Total Booking Attempts: %,d", totalAttempts));
        System.out.println(String.format("   Successful Bookings: %,d", successful));
        System.out.println(String.format("   Success Rate: %.2f%%", successRate));
        
        // Response time analysis
        DoubleSummaryStatistics responseTimeStats = results.stream()
            .mapToDouble(r -> r.responseTime.toMillis())
            .summaryStatistics();
        
        System.out.println("\n⏱️ Response Time Analysis:");
        System.out.println(String.format("   Average Response: %.0f ms", responseTimeStats.getAverage()));
        System.out.println(String.format("   Min Response: %.0f ms", responseTimeStats.getMin()));
        System.out.println(String.format("   Max Response: %.0f ms", responseTimeStats.getMax()));
        
        // Failure mode analysis
        Map<FailureMode, Long> failureModes = results.stream()
            .filter(r -> !r.success && r.failureReason != null)
            .collect(Collectors.groupingBy(r -> r.failureReason, Collectors.counting()));
        
        if (!failureModes.isEmpty()) {
            System.out.println("\n🚨 Failure Mode Analysis:");
            failureModes.entrySet().stream()
                .sorted(Map.Entry.<FailureMode, Long>comparingByValue().reversed())
                .forEach(entry -> {
                    double percentage = (entry.getValue() * 100.0) / totalAttempts;
                    System.out.println(String.format("   %s: %d times (%.1f%%)",
                        entry.getKey().description, entry.getValue(), percentage));
                });
        }
        
        // Route-wise success analysis
        Map<PopularRoute, List<BookingResult>> routeResults = results.stream()
            .collect(Collectors.groupingBy(r -> r.route));
        
        System.out.println("\n🛤️ Route-wise Success Rates:");
        for (Map.Entry<PopularRoute, List<BookingResult>> entry : routeResults.entrySet()) {
            List<BookingResult> routeAttempts = entry.getValue();
            long routeSuccesses = routeAttempts.stream().mapToLong(r -> r.success ? 1 : 0).sum();
            double routeSuccessRate = (routeSuccesses * 100.0) / routeAttempts.size();
            
            System.out.println(String.format("   %s: %.1f%% (%d/%d)",
                entry.getKey().routeName, routeSuccessRate, routeSuccesses, routeAttempts.size()));
        }
        
        // Business impact analysis
        analyzeBusinessImpact(results);
        
        // Mumbai local analogy
        System.out.println("\n🏙️ Mumbai Local Train Analogy:");
        System.out.println("   Tatkal booking rush = Mumbai local train में Virar fast का wait");
        System.out.println("   Database connections = Platform पर available space");
        System.out.println("   Payment gateway = Ticket counter (limited capacity)");
        System.out.println("   Chaos engineering = Monsoon disruptions simulation");
        System.out.println("   Success rate = Actually getting seat in desired train");
    }
    
    private void analyzeBusinessImpact(List<BookingResult> results) {
        System.out.println("\n💰 Business Impact Analysis:");
        
        // Revenue calculation (approximate)
        long successfulBookings = results.stream().mapToLong(r -> r.success ? 1 : 0).sum();
        double avgTicketPrice = 2500.0; // Average Rajdhani ticket price
        double totalRevenue = successfulBookings * avgTicketPrice;
        
        System.out.println(String.format("   Successfully Booked Tickets: %,d", successfulBookings));
        System.out.println(String.format("   Estimated Revenue: ₹%,.0f", totalRevenue));
        
        // Lost opportunity calculation
        long failedAttempts = results.size() - successfulBookings;
        double lostRevenue = failedAttempts * avgTicketPrice * 0.7; // 70% would have booked if system worked
        
        System.out.println(String.format("   Failed Booking Attempts: %,d", failedAttempts));
        System.out.println(String.format("   Estimated Revenue Loss: ₹%,.0f", lostRevenue));
        
        // System improvement ROI
        double currentSuccessRate = (successfulBookings * 100.0) / results.size();
        double improvedSuccessRate = Math.min(95.0, currentSuccessRate + 20.0); // Target improvement
        double additionalRevenue = results.size() * (improvedSuccessRate - currentSuccessRate) / 100.0 * avgTicketPrice;
        
        System.out.println(String.format("   Current Success Rate: %.1f%%", currentSuccessRate));
        System.out.println(String.format("   Target Success Rate: %.1f%%", improvedSuccessRate));
        System.out.println(String.format("   Additional Revenue Potential: ₹%,.0f", additionalRevenue));
    }
    
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
        }
    }
    
    public static void main(String[] args) {
        System.out.println("🇮🇳 IRCTC Tatkal Booking Chaos Engineering");
        System.out.println("🚂 Mumbai-Delhi Rajdhani Express Simulation");
        System.out.println("⏰ Tatkal Opening Time: 10:00 AM");
        System.out.println("=" + "=".repeat(60));
        
        TatkalBookingLoadSimulator simulator = new TatkalBookingLoadSimulator(100); // 100 threads
        
        try {
            // Simulate 10,000 users trying to book in 5 minutes
            simulator.runTatkalChaosSimulation(10_000, Duration.ofMinutes(5));
            
        } finally {
            simulator.shutdown();
        }
        
        System.out.println("\n🔧 Technical Recommendations:");
        System.out.println("   1. Implement queue-based booking system for fairness");
        System.out.println("   2. Use circuit breakers for payment gateway protection");
        System.out.println("   3. Add read replicas for seat availability checks");
        System.out.println("   4. Implement progressive web app for better mobile experience");
        System.out.println("   5. Use CDN for static resources during high load");
        
        System.out.println("\n💡 Chaos Engineering Insights:");
        System.out.println("   💡 Payment failures have highest user impact");
        System.out.println("   💡 Database connection exhaustion is most common failure");
        System.out.println("   💡 First 2 minutes see 60% of total load");
        System.out.println("   💡 Premium users show higher retry persistence");
        System.out.println("   💡 Route popularity significantly affects success rates");
    }
}
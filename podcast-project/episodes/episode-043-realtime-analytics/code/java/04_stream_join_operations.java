/*
 * Stream Join Operations for Real-time Analytics
 * Episode 43: Real-time Analytics at Scale
 * 
 * Advanced stream joins using Apache Flink
 * Use Case: IRCTC booking system - joining user, train, and payment streams
 */

import org.apache.flink.api.common.functions.JoinFunction;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.functions.CoMapFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.api.java.tuple.Tuple4;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.ConnectedStreams;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.co.ProcessJoinFunction;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ThreadLocalRandom;

/**
 * IRCTC Real-time Stream Joins
 * 
 * तीन streams को join करके complete booking analytics करता है:
 * 1. User Stream - User activities और preferences
 * 2. Train Stream - Train status, availability, delays
 * 3. Payment Stream - Payment attempts और results
 */
public class IRCTCStreamJoins {
    
    /**
     * User Activity Event
     * User के actions और preferences
     */
    public static class UserActivityEvent {
        public String userId;
        public String sessionId;
        public String activityType; // search, select, book, cancel
        public String sourceStation;
        public String destinationStation;
        public String trainNumber;
        public String classType;
        public LocalDateTime preferredDate;
        public long timestamp;
        public String deviceType;
        public String location;
        
        public UserActivityEvent() {}
        
        public UserActivityEvent(String userId, String sessionId, String activityType,
                               String sourceStation, String destinationStation, String trainNumber,
                               String classType, LocalDateTime preferredDate, String deviceType, String location) {
            this.userId = userId;
            this.sessionId = sessionId;
            this.activityType = activityType;
            this.sourceStation = sourceStation;
            this.destinationStation = destinationStation;
            this.trainNumber = trainNumber;
            this.classType = classType;
            this.preferredDate = preferredDate;
            this.timestamp = System.currentTimeMillis();
            this.deviceType = deviceType;
            this.location = location;
        }
        
        @Override
        public String toString() {
            return String.format("UserActivity{user='%s', activity='%s', train='%s', route='%s->%s', timestamp=%d}",
                               userId, activityType, trainNumber, sourceStation, destinationStation, timestamp);
        }
    }
    
    /**
     * Train Status Event
     * Train की current status और availability
     */
    public static class TrainStatusEvent {
        public String trainNumber;
        public String trainName;
        public String currentStation;
        public int delayMinutes;
        public String status; // on_time, delayed, cancelled, departed
        public Map<String, Integer> seatAvailability; // class -> available seats
        public double baseFare;
        public String route;
        public long timestamp;
        public boolean isOperational;
        
        public TrainStatusEvent() {}
        
        public TrainStatusEvent(String trainNumber, String trainName, String currentStation,
                              int delayMinutes, String status, Map<String, Integer> seatAvailability,
                              double baseFare, String route, boolean isOperational) {
            this.trainNumber = trainNumber;
            this.trainName = trainName;
            this.currentStation = currentStation;
            this.delayMinutes = delayMinutes;
            this.status = status;
            this.seatAvailability = new HashMap<>(seatAvailability);
            this.baseFare = baseFare;
            this.route = route;
            this.timestamp = System.currentTimeMillis();
            this.isOperational = isOperational;
        }
        
        @Override
        public String toString() {
            return String.format("TrainStatus{train='%s(%s)', station='%s', delay=%dmin, status='%s', operational=%s}",
                               trainNumber, trainName, currentStation, delayMinutes, status, isOperational);
        }
    }
    
    /**
     * Payment Event
     * Payment attempts और results
     */
    public static class PaymentEvent {
        public String paymentId;
        public String userId;
        public String sessionId;
        public String bookingId;
        public String paymentMethod;
        public double amount;
        public String currency;
        public String status; // initiated, processing, success, failed, timeout
        public String failureReason;
        public String gatewayResponse;
        public long timestamp;
        public long processingTimeMs;
        
        public PaymentEvent() {}
        
        public PaymentEvent(String paymentId, String userId, String sessionId, String bookingId,
                          String paymentMethod, double amount, String status, String failureReason,
                          long processingTimeMs) {
            this.paymentId = paymentId;
            this.userId = userId;
            this.sessionId = sessionId;
            this.bookingId = bookingId;
            this.paymentMethod = paymentMethod;
            this.amount = amount;
            this.currency = "INR";
            this.status = status;
            this.failureReason = failureReason;
            this.timestamp = System.currentTimeMillis();
            this.processingTimeMs = processingTimeMs;
        }
        
        @Override
        public String toString() {
            return String.format("Payment{id='%s', user='%s', amount=%.2f, status='%s', method='%s', timestamp=%d}",
                               paymentId, userId, amount, status, paymentMethod, timestamp);
        }
    }
    
    /**
     * Enriched Booking Analytics Event
     * सभी streams का joined result
     */
    public static class BookingAnalyticsEvent {
        public String userId;
        public String sessionId;
        public String trainNumber;
        public String trainName;
        public String route;
        public String classType;
        public String userLocation;
        public String deviceType;
        public String paymentMethod;
        public double amount;
        public String bookingStatus;
        public String paymentStatus;
        public int trainDelay;
        public boolean isTrainOperational;
        public int availableSeats;
        public String failureReason;
        public long userActivityTime;
        public long paymentTime;
        public long totalBookingDuration;
        public LocalDateTime bookingDateTime;
        
        public BookingAnalyticsEvent() {}
        
        @Override
        public String toString() {
            return String.format("BookingAnalytics{user='%s', train='%s', route='%s', amount=%.2f, " +
                               "bookingStatus='%s', paymentStatus='%s', delay=%dmin, duration=%dms}",
                               userId, trainNumber, route, amount, bookingStatus, paymentStatus, 
                               trainDelay, totalBookingDuration);
        }
    }
    
    /**
     * User-Train Join Function
     * User activity को train status के साथ join करता है
     */
    public static class UserTrainJoinFunction implements JoinFunction<UserActivityEvent, TrainStatusEvent, Tuple3<UserActivityEvent, TrainStatusEvent, String>> {
        
        @Override
        public Tuple3<UserActivityEvent, TrainStatusEvent, String> join(UserActivityEvent userEvent, TrainStatusEvent trainEvent) throws Exception {
            
            // Determine booking viability based on train status and availability
            String viability = "POSSIBLE";
            
            if (!trainEvent.isOperational) {
                viability = "TRAIN_NOT_OPERATIONAL";
            } else if ("cancelled".equals(trainEvent.status)) {
                viability = "TRAIN_CANCELLED";
            } else if (trainEvent.delayMinutes > 120) { // More than 2 hours delay
                viability = "EXCESSIVE_DELAY";
            } else {
                // Check seat availability for user's preferred class
                Integer availableSeats = trainEvent.seatAvailability.get(userEvent.classType);
                if (availableSeats == null || availableSeats <= 0) {
                    viability = "NO_SEATS_AVAILABLE";
                } else if (availableSeats < 5) {
                    viability = "LIMITED_AVAILABILITY";
                }
            }
            
            return new Tuple3<>(userEvent, trainEvent, viability);
        }
    }
    
    /**
     * Complete Booking Join Function
     * User-Train joined data को payment data के साथ join करता है
     */
    public static class CompleteBookingJoinFunction extends ProcessJoinFunction<Tuple3<UserActivityEvent, TrainStatusEvent, String>, PaymentEvent, BookingAnalyticsEvent> {
        
        @Override
        public void processElement(Tuple3<UserActivityEvent, TrainStatusEvent, String> userTrainData, 
                                 PaymentEvent paymentEvent, 
                                 Context context, 
                                 Collector<BookingAnalyticsEvent> collector) throws Exception {
            
            UserActivityEvent userEvent = userTrainData.f0;
            TrainStatusEvent trainEvent = userTrainData.f1;
            String viability = userTrainData.f2;
            
            // Create enriched booking analytics event
            BookingAnalyticsEvent analytics = new BookingAnalyticsEvent();
            
            // User data
            analytics.userId = userEvent.userId;
            analytics.sessionId = userEvent.sessionId;
            analytics.userLocation = userEvent.location;
            analytics.deviceType = userEvent.deviceType;
            analytics.userActivityTime = userEvent.timestamp;
            
            // Train data
            analytics.trainNumber = trainEvent.trainNumber;
            analytics.trainName = trainEvent.trainName;
            analytics.route = userEvent.sourceStation + " -> " + userEvent.destinationStation;
            analytics.classType = userEvent.classType;
            analytics.trainDelay = trainEvent.delayMinutes;
            analytics.isTrainOperational = trainEvent.isOperational;
            analytics.availableSeats = trainEvent.seatAvailability.getOrDefault(userEvent.classType, 0);
            
            // Payment data
            analytics.paymentMethod = paymentEvent.paymentMethod;
            analytics.amount = paymentEvent.amount;
            analytics.paymentStatus = paymentEvent.status;
            analytics.paymentTime = paymentEvent.timestamp;
            analytics.failureReason = paymentEvent.failureReason;
            
            // Derived analytics
            analytics.totalBookingDuration = paymentEvent.timestamp - userEvent.timestamp;
            analytics.bookingDateTime = LocalDateTime.now();
            
            // Determine final booking status
            if ("success".equals(paymentEvent.status) && "POSSIBLE".equals(viability)) {
                analytics.bookingStatus = "CONFIRMED";
            } else if (!"success".equals(paymentEvent.status)) {
                analytics.bookingStatus = "PAYMENT_FAILED";
            } else {
                analytics.bookingStatus = "BOOKING_FAILED_" + viability;
            }
            
            collector.collect(analytics);
            
            // Log significant events
            if ("CONFIRMED".equals(analytics.bookingStatus)) {
                System.out.println("✅ Booking Confirmed: " + analytics);
            } else {
                System.out.println("❌ Booking Failed: " + analytics.bookingStatus + " - " + analytics);
            }
        }
    }
    
    /**
     * Real-time Analytics Processor
     * Joined data से real-time metrics calculate करता है
     */
    public static class BookingAnalyticsProcessor extends ProcessWindowFunction<BookingAnalyticsEvent, String, String, TimeWindow> {
        
        @Override
        public void process(String key, 
                          Context context, 
                          Iterable<BookingAnalyticsEvent> bookings, 
                          Collector<String> collector) throws Exception {
            
            List<BookingAnalyticsEvent> bookingList = new ArrayList<>();
            bookings.forEach(bookingList::add);
            
            if (bookingList.isEmpty()) return;
            
            // Calculate metrics for this window
            int totalBookings = bookingList.size();
            long successfulBookings = bookingList.stream()
                                                .filter(b -> "CONFIRMED".equals(b.bookingStatus))
                                                .count();
            
            double totalRevenue = bookingList.stream()
                                           .filter(b -> "CONFIRMED".equals(b.bookingStatus))
                                           .mapToDouble(b -> b.amount)
                                           .sum();
            
            double averageBookingTime = bookingList.stream()
                                                 .mapToLong(b -> b.totalBookingDuration)
                                                 .average()
                                                 .orElse(0.0);
            
            // Payment method distribution
            Map<String, Long> paymentMethodDist = bookingList.stream()
                                                            .collect(java.util.stream.Collectors.groupingBy(
                                                                b -> b.paymentMethod,
                                                                java.util.stream.Collectors.counting()
                                                            ));
            
            // Device type distribution
            Map<String, Long> deviceTypeDist = bookingList.stream()
                                                         .collect(java.util.stream.Collectors.groupingBy(
                                                             b -> b.deviceType,
                                                             java.util.stream.Collectors.counting()
                                                         ));
            
            // Popular routes
            Map<String, Long> routeDist = bookingList.stream()
                                                   .collect(java.util.stream.Collectors.groupingBy(
                                                       b -> b.route,
                                                       java.util.stream.Collectors.counting()
                                                   ));
            
            // Failure analysis
            Map<String, Long> failureReasons = bookingList.stream()
                                                         .filter(b -> !"CONFIRMED".equals(b.bookingStatus))
                                                         .collect(java.util.stream.Collectors.groupingBy(
                                                             b -> b.bookingStatus,
                                                             java.util.stream.Collectors.counting()
                                                         ));
            
            // Train delay impact
            double avgDelayForSuccessful = bookingList.stream()
                                                    .filter(b -> "CONFIRMED".equals(b.bookingStatus))
                                                    .mapToInt(b -> b.trainDelay)
                                                    .average()
                                                    .orElse(0.0);
            
            double avgDelayForFailed = bookingList.stream()
                                                .filter(b -> !"CONFIRMED".equals(b.bookingStatus))
                                                .mapToInt(b -> b.trainDelay)
                                                .average()
                                                .orElse(0.0);
            
            // Create analytics report
            String report = String.format(
                "=== IRCTC Analytics Window [%s - %s] ===\n" +
                "Window Key: %s\n" +
                "Total Bookings: %d\n" +
                "Successful Bookings: %d (%.1f%%)\n" +
                "Total Revenue: ₹%.2f\n" +
                "Average Booking Time: %.2f seconds\n" +
                "Payment Methods: %s\n" +
                "Device Types: %s\n" +
                "Popular Routes: %s\n" +
                "Failure Reasons: %s\n" +
                "Avg Delay (Successful): %.1f minutes\n" +
                "Avg Delay (Failed): %.1f minutes\n" +
                "================================================\n",
                
                LocalDateTime.ofEpochSecond(context.window().getStart() / 1000, 0, java.time.ZoneOffset.UTC),
                LocalDateTime.ofEpochSecond(context.window().getEnd() / 1000, 0, java.time.ZoneOffset.UTC),
                key,
                totalBookings,
                successfulBookings,
                (double) successfulBookings / totalBookings * 100,
                totalRevenue,
                averageBookingTime / 1000.0,
                paymentMethodDist,
                deviceTypeDist,
                routeDist,
                failureReasons,
                avgDelayForSuccessful,
                avgDelayForFailed
            );
            
            collector.collect(report);
        }
    }
    
    /**
     * Stream Data Generators
     */
    public static class UserActivityGenerator implements MapFunction<Long, UserActivityEvent> {
        private final String[] users = {"USER_001", "USER_002", "USER_003", "USER_004", "USER_005"};
        private final String[] stations = {"MUMBAI_CENTRAL", "NEW_DELHI", "BANGALORE", "CHENNAI", "KOLKATA", "PUNE", "HYDERABAD"};
        private final String[] activities = {"search", "select", "book", "cancel"};
        private final String[] classes = {"SL", "3A", "2A", "1A"};
        private final String[] devices = {"mobile", "desktop", "tablet"};
        private final String[] locations = {"Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"};
        
        @Override
        public UserActivityEvent map(Long seed) throws Exception {
            Random rand = new Random(seed);
            
            String userId = users[rand.nextInt(users.length)];
            String sessionId = "SESSION_" + (seed % 100);
            String activity = activities[rand.nextInt(activities.length)];
            String source = stations[rand.nextInt(stations.length)];
            String dest;
            do {
                dest = stations[rand.nextInt(stations.length)];
            } while (dest.equals(source));
            
            String trainNumber = "TRAIN_" + String.format("%03d", rand.nextInt(50) + 1);
            String classType = classes[rand.nextInt(classes.length)];
            String device = devices[rand.nextInt(devices.length)];
            String location = locations[rand.nextInt(locations.length)];
            
            return new UserActivityEvent(
                userId, sessionId, activity, source, dest, trainNumber,
                classType, LocalDateTime.now().plusDays(rand.nextInt(7)),
                device, location
            );
        }
    }
    
    public static class TrainStatusGenerator implements MapFunction<Long, TrainStatusEvent> {
        private final String[] trainNames = {
            "राजधानी एक्सप्रेस", "शताब्दी एक्सप्रेस", "दुरंतो एक्सप्रेस", 
            "गरीब रथ", "जन शताब्दी", "सुपरफास्ट एक्सप्रेस"
        };
        private final String[] stations = {"MUMBAI_CENTRAL", "NEW_DELHI", "BANGALORE", "CHENNAI", "KOLKATA"};
        private final String[] statuses = {"on_time", "delayed", "departed", "cancelled"};
        
        @Override
        public TrainStatusEvent map(Long seed) throws Exception {
            Random rand = new Random(seed + 1000);
            
            String trainNumber = "TRAIN_" + String.format("%03d", (int)(seed % 50) + 1);
            String trainName = trainNames[rand.nextInt(trainNames.length)];
            String currentStation = stations[rand.nextInt(stations.length)];
            int delay = rand.nextBoolean() ? rand.nextInt(180) : 0; // 0-3 hours delay
            String status = delay > 0 ? "delayed" : statuses[rand.nextInt(statuses.length)];
            
            // Seat availability
            Map<String, Integer> seats = new HashMap<>();
            seats.put("SL", rand.nextInt(200));
            seats.put("3A", rand.nextInt(100));
            seats.put("2A", rand.nextInt(50));
            seats.put("1A", rand.nextInt(20));
            
            double baseFare = 500 + rand.nextDouble() * 2000;
            String route = "MUL-TI CITY ROUTE";
            boolean operational = !status.equals("cancelled");
            
            return new TrainStatusEvent(
                trainNumber, trainName, currentStation, delay, status,
                seats, baseFare, route, operational
            );
        }
    }
    
    public static class PaymentEventGenerator implements MapFunction<Long, PaymentEvent> {
        private final String[] users = {"USER_001", "USER_002", "USER_003", "USER_004", "USER_005"};
        private final String[] methods = {"UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"};
        private final String[] statuses = {"success", "failed", "timeout", "processing"};
        private final String[] failures = {"Insufficient Balance", "Card Expired", "Network Error", "Bank Declined"};
        
        @Override
        public PaymentEvent map(Long seed) throws Exception {
            Random rand = new Random(seed + 2000);
            
            String paymentId = "PAY_" + seed;
            String userId = users[rand.nextInt(users.length)];
            String sessionId = "SESSION_" + (seed % 100);
            String bookingId = "BOOKING_" + seed;
            String method = methods[rand.nextInt(methods.length)];
            double amount = 200 + rand.nextDouble() * 3000;
            String status = statuses[rand.nextInt(statuses.length)];
            String failure = status.equals("failed") ? failures[rand.nextInt(failures.length)] : null;
            long processingTime = 1000 + rand.nextInt(5000); // 1-6 seconds
            
            return new PaymentEvent(
                paymentId, userId, sessionId, bookingId, method,
                amount, status, failure, processingTime
            );
        }
    }
    
    /**
     * Main Flink Job
     */
    public static void main(String[] args) throws Exception {
        
        System.out.println("🚂 Starting IRCTC Stream Joins Demo...");
        
        // Set up Flink environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);
        env.setParallelism(2);
        
        // Generate source streams
        DataStream<UserActivityEvent> userStream = env
            .generateSequence(1, 1000)
            .map(new UserActivityGenerator())
            .name("User Activity Stream");
        
        DataStream<TrainStatusEvent> trainStream = env
            .generateSequence(1, 200)
            .map(new TrainStatusGenerator())
            .name("Train Status Stream");
        
        DataStream<PaymentEvent> paymentStream = env
            .generateSequence(1, 500)
            .map(new PaymentEventGenerator())
            .name("Payment Event Stream");
        
        // Print source streams for monitoring
        userStream.print("👤 User");
        trainStream.print("🚂 Train");
        paymentStream.print("💳 Payment");
        
        // Stream Join 1: User Activity + Train Status
        // Time-based window join for real-time correlation
        DataStream<Tuple3<UserActivityEvent, TrainStatusEvent, String>> userTrainJoined = userStream
            .join(trainStream)
            .where(user -> user.trainNumber)  // Join key: train number
            .equalTo(train -> train.trainNumber)
            .window(org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows.of(Time.seconds(10)))
            .apply(new UserTrainJoinFunction())
            .name("User-Train Join");
        
        // Stream Join 2: (User + Train) + Payment
        // Interval join for payment correlation within booking session
        DataStream<BookingAnalyticsEvent> completeBookingJoined = userTrainJoined
            .keyBy(data -> data.f0.sessionId)  // Key by session ID
            .intervalJoin(paymentStream.keyBy(payment -> payment.sessionId))
            .between(Time.seconds(-30), Time.seconds(30))  // Payment can happen 30 seconds before/after user activity
            .process(new CompleteBookingJoinFunction())
            .name("Complete Booking Join");
        
        // Real-time Analytics
        DataStream<String> analytics = completeBookingJoined
            .keyBy(booking -> "global")  // Global key for all bookings
            .timeWindow(Time.minutes(2))  // 2-minute analytics windows
            .process(new BookingAnalyticsProcessor())
            .name("Booking Analytics");
        
        // Output analytics
        analytics.print("📊 Analytics");
        
        // Additional analytics streams
        
        // Stream 3: Connected Streams for Complex Event Processing
        ConnectedStreams<UserActivityEvent, PaymentEvent> connectedUserPayment = userStream
            .connect(paymentStream);
        
        DataStream<String> userPaymentCorrelation = connectedUserPayment
            .keyBy(user -> user.userId, payment -> payment.userId)
            .map(new CoMapFunction<UserActivityEvent, PaymentEvent, String>() {
                
                private Map<String, UserActivityEvent> pendingUsers = new HashMap<>();
                private Map<String, PaymentEvent> pendingPayments = new HashMap<>();
                
                @Override
                public String map1(UserActivityEvent userEvent) throws Exception {
                    String key = userEvent.userId + ":" + userEvent.sessionId;
                    
                    // Check if there's a matching payment
                    PaymentEvent matchingPayment = pendingPayments.remove(key);
                    if (matchingPayment != null) {
                        return String.format("🔗 User-Payment Match: %s -> %s (%.2f INR)",
                                           userEvent.activityType, matchingPayment.status, matchingPayment.amount);
                    } else {
                        // Store user event for later matching
                        pendingUsers.put(key, userEvent);
                        return null;
                    }
                }
                
                @Override
                public String map2(PaymentEvent paymentEvent) throws Exception {
                    String key = paymentEvent.userId + ":" + paymentEvent.sessionId;
                    
                    // Check if there's a matching user activity
                    UserActivityEvent matchingUser = pendingUsers.remove(key);
                    if (matchingUser != null) {
                        return String.format("🔗 Payment-User Match: %s -> %s (%s train)",
                                           paymentEvent.status, matchingUser.activityType, matchingUser.trainNumber);
                    } else {
                        // Store payment event for later matching
                        pendingPayments.put(key, paymentEvent);
                        return null;
                    }
                }
            })
            .filter(Objects::nonNull)
            .name("User-Payment Correlation");
        
        userPaymentCorrelation.print("🔗 Correlation");
        
        // Execute the streaming job
        System.out.println("⚡ Executing IRCTC Stream Joins...");
        env.execute("IRCTC Real-time Stream Joins");
    }
}
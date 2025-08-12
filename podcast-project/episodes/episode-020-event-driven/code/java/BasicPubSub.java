package com.flipkart.events;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Basic Event Publisher/Subscriber Pattern - Java Implementation
 * उदाहरण: IRCTC के ticket booking events को handle करना
 * 
 * Setup:
 * - Add lombok dependency
 * - Add slf4j logging
 * 
 * Indian Context: Jab IRCTC par ticket book karta hai,
 * multiple services को notification जाना चाहिए:
 * - Payment service (paisa deduct)
 * - SMS service (confirmation message)
 * - Email service (e-ticket)
 * - Waiting list service (if applicable)
 */

@Data
@AllArgsConstructor
class Event {
    private String eventId;
    private String eventType;
    private Map<String, Object> data;
    private String timestamp;
    private String source;
    private String version;
    
    public Event(String eventType, Map<String, Object> data, String source) {
        this.eventId = UUID.randomUUID().toString();
        this.eventType = eventType;
        this.data = data;
        this.source = source;
        this.timestamp = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        this.version = "1.0";
    }
}

@Slf4j
public class EventBus {
    // Mumbai local train ki tarah - har station par different log
    private final Map<String, List<Consumer<Event>>> subscribers = new ConcurrentHashMap<>();
    private final List<Event> eventStore = new ArrayList<>(); // Event history
    private final ExecutorService executorService = Executors.newCachedThreadPool();
    
    /**
     * Event type ke liye handler register karna
     * Jaise newspaper subscription - specific topic ke liye
     */
    public void subscribe(String eventType, Consumer<Event> handler) {
        subscribers.computeIfAbsent(eventType, k -> new ArrayList<>()).add(handler);
        log.info("Handler registered for event_type: {}", eventType);
    }
    
    /**
     * Event ko sabko broadcast karna
     * Railway announcement ki tarah - sabko sunai deta hai
     */
    public CompletableFuture<Void> publish(Event event) {
        // Event store mein save karna
        eventStore.add(event);
        
        log.info("Publishing event: {} - ID: {}", event.getEventType(), event.getEventId());
        
        // Subscribers ko notify karna
        List<Consumer<Event>> handlers = subscribers.get(event.getEventType());
        if (handlers != null && !handlers.isEmpty()) {
            List<CompletableFuture<Void>> futures = new ArrayList<>();
            
            for (Consumer<Event> handler : handlers) {
                CompletableFuture<Void> future = CompletableFuture.runAsync(() -> {
                    try {
                        handler.accept(event);
                    } catch (Exception e) {
                        log.error("Handler failed for event {}: {}", event.getEventId(), e.getMessage());
                    }
                }, executorService);
                futures.add(future);
            }
            
            // Saare handlers complete hone ka wait karna
            return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]));
        }
        
        return CompletableFuture.completedFuture(null);
    }
    
    public List<Event> getEvents(String eventType) {
        if (eventType != null) {
            return eventStore.stream()
                    .filter(e -> eventType.equals(e.getEventType()))
                    .collect(java.util.stream.Collectors.toList());
        }
        return new ArrayList<>(eventStore);
    }
    
    public void shutdown() {
        executorService.shutdown();
    }
}

/**
 * IRCTC ticket booking service
 */
@Slf4j
class IRCTCBookingService {
    private final EventBus eventBus;
    
    public IRCTCBookingService(EventBus eventBus) {
        this.eventBus = eventBus;
    }
    
    public CompletableFuture<String> bookTicket(String passengerId, String trainNo, 
                                               String from, String to, int passengers) {
        String pnr = "PNR" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        
        Map<String, Object> ticketData = new HashMap<>();
        ticketData.put("pnr", pnr);
        ticketData.put("passenger_id", passengerId);
        ticketData.put("train_no", trainNo);
        ticketData.put("from_station", from);
        ticketData.put("to_station", to);
        ticketData.put("passenger_count", passengers);
        ticketData.put("fare", calculateFare(from, to, passengers));
        ticketData.put("journey_date", "2025-01-15");
        ticketData.put("class", "3AC");
        
        Event event = new Event("ticket.booked", ticketData, "irctc.booking.service");
        
        return eventBus.publish(event).thenApply(v -> pnr);
    }
    
    private double calculateFare(String from, String to, int passengers) {
        // Simple fare calculation - Mumbai to Delhi
        return 1500.0 * passengers; // ₹1500 per passenger
    }
}

/**
 * Payment processing service - paisa deduct karna
 */
@Slf4j
class PaymentService {
    private final String serviceName = "Payment Service";
    
    public void handleTicketBooked(Event event) {
        Map<String, Object> data = event.getData();
        String pnr = (String) data.get("pnr");
        Double fare = (Double) data.get("fare");
        
        log.info("💳 {}: Processing payment for PNR {}", serviceName, pnr);
        log.info("   💰 Amount: ₹{}", fare);
        
        try {
            // UPI/Card processing simulation
            Thread.sleep(500);
            
            log.info("✅ Payment successful for PNR {}", pnr);
        } catch (InterruptedException e) {
            log.error("Payment processing interrupted", e);
            Thread.currentThread().interrupt();
        }
    }
}

/**
 * SMS notification service
 */
@Slf4j
class SMSService {
    private final String serviceName = "SMS Service";
    
    public void handleTicketBooked(Event event) {
        Map<String, Object> data = event.getData();
        String pnr = (String) data.get("pnr");
        String passengerId = (String) data.get("passenger_id");
        String trainNo = (String) data.get("train_no");
        
        log.info("📱 {}: Sending SMS to passenger {}", serviceName, passengerId);
        log.info("   🚂 Train: {} | PNR: {}", trainNo, pnr);
        
        try {
            // SMS gateway call simulation
            Thread.sleep(200);
            
            String message = String.format("Aapka ticket confirm hai! PNR: %s, Train: %s. Happy Journey!", 
                                          pnr, trainNo);
            log.info("✅ SMS sent: {}", message);
        } catch (InterruptedException e) {
            log.error("SMS sending interrupted", e);
            Thread.currentThread().interrupt();
        }
    }
}

/**
 * Email service for e-ticket
 */
@Slf4j
class EmailService {
    private final String serviceName = "Email Service";
    
    public void handleTicketBooked(Event event) {
        Map<String, Object> data = event.getData();
        String pnr = (String) data.get("pnr");
        String from = (String) data.get("from_station");
        String to = (String) data.get("to_station");
        
        log.info("📧 {}: Sending e-ticket for PNR {}", serviceName, pnr);
        log.info("   🛤️ Journey: {} to {}", from, to);
        
        try {
            // Email service call simulation
            Thread.sleep(300);
            
            log.info("✅ E-ticket emailed for PNR {}", pnr);
        } catch (InterruptedException e) {
            log.error("Email sending interrupted", e);
            Thread.currentThread().interrupt();
        }
    }
}

/**
 * Waiting list management service
 */
@Slf4j
class WaitingListService {
    private final String serviceName = "Waiting List Service";
    
    public void handleTicketBooked(Event event) {
        Map<String, Object> data = event.getData();
        String pnr = (String) data.get("pnr");
        Integer passengerCount = (Integer) data.get("passenger_count");
        
        log.info("📋 {}: Checking waiting list for PNR {}", serviceName, pnr);
        log.info("   👥 Passengers: {}", passengerCount);
        
        try {
            // Waiting list check simulation
            Thread.sleep(100);
            
            // Random waiting list status
            boolean isConfirmed = Math.random() > 0.3; // 70% confirmation chance
            String status = isConfirmed ? "CONFIRMED" : "WL/15";
            
            log.info("✅ Ticket status: {} for PNR {}", status, pnr);
        } catch (InterruptedException e) {
            log.error("Waiting list check interrupted", e);
            Thread.currentThread().interrupt();
        }
    }
}

/**
 * Main demo class
 */
@Slf4j
public class BasicPubSub {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🚂 IRCTC Event-Driven Ticket Booking Demo");
        System.out.println("=".repeat(50));
        
        // Event bus initialize karna
        EventBus eventBus = new EventBus();
        
        // Services initialize karna
        IRCTCBookingService bookingService = new IRCTCBookingService(eventBus);
        PaymentService paymentService = new PaymentService();
        SMSService smsService = new SMSService();
        EmailService emailService = new EmailService();
        WaitingListService waitingListService = new WaitingListService();
        
        // Event handlers register karna
        eventBus.subscribe("ticket.booked", paymentService::handleTicketBooked);
        eventBus.subscribe("ticket.booked", smsService::handleTicketBooked);
        eventBus.subscribe("ticket.booked", emailService::handleTicketBooked);
        eventBus.subscribe("ticket.booked", waitingListService::handleTicketBooked);
        
        // Ticket book karna
        CompletableFuture<String> bookingFuture = bookingService.bookTicket(
            "PASS123", 
            "12901", // Godan Express
            "Mumbai Central", 
            "New Delhi", 
            2 // 2 passengers
        );
        
        String pnr = bookingFuture.get(); // Block and wait for completion
        System.out.println("\n🎫 Ticket booked successfully: " + pnr);
        
        // Processing complete hone ke liye wait karna
        Thread.sleep(2000);
        
        // Event history dekhna
        List<Event> allEvents = eventBus.getEvents(null);
        List<Event> ticketEvents = eventBus.getEvents("ticket.booked");
        
        System.out.println(String.format("\n📊 Total events processed: %d", allEvents.size()));
        System.out.println(String.format("🎫 Ticket events: %d", ticketEvents.size()));
        
        // Cleanup
        eventBus.shutdown();
    }
}
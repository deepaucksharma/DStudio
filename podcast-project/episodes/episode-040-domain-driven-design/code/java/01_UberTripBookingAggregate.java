/*
 * Domain-Driven Design: Aggregate Pattern - Uber Trip Booking
 * Hindi Tech Podcast Series - Episode 40
 * 
 * यह example दिखाता है कि कैसे DDD में Aggregate pattern का इस्तेमाल करके
 * Uber trip booking की complete business logic को handle करते हैं।
 * Java में enterprise-level implementation।
 * 
 * Author: Hindi Tech Podcast
 * Date: 2025
 */

package com.hindipodcast.ddd.uber;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.Duration;
import java.util.*;
import java.util.stream.Collectors;

// ====================================================================
// DOMAIN EXCEPTIONS - Business rule violations
// ====================================================================

class DomainException extends RuntimeException {
    public DomainException(String message) {
        super(message);
    }
}

class InvalidTripStateException extends DomainException {
    public InvalidTripStateException(String message) {
        super(message);
    }
}

class InsufficientDriversException extends DomainException {
    public InsufficientDriversException(String message) {
        super(message);
    }
}

class PaymentFailedException extends DomainException {
    public PaymentFailedException(String message) {
        super(message);
    }
}

// ====================================================================
// VALUE OBJECTS - Immutable objects representing concepts
// ====================================================================

/**
 * Location value object - Geographic coordinates with address
 * Location value object - address के साथ geographic coordinates
 */
class Location {
    private final double latitude;
    private final double longitude;
    private final String address;
    private final String landmark;
    
    public Location(double latitude, double longitude, String address, String landmark) {
        if (latitude < -90 || latitude > 90) {
            throw new IllegalArgumentException("Invalid latitude - गलत latitude");
        }
        if (longitude < -180 || longitude > 180) {
            throw new IllegalArgumentException("Invalid longitude - गलत longitude");
        }
        if (address == null || address.trim().isEmpty()) {
            throw new IllegalArgumentException("Address cannot be empty - Address खाली नहीं हो सकता");
        }
        
        this.latitude = latitude;
        this.longitude = longitude;
        this.address = address.trim();
        this.landmark = landmark != null ? landmark.trim() : "";
    }
    
    public double getLatitude() { return latitude; }
    public double getLongitude() { return longitude; }
    public String getAddress() { return address; }
    public String getLandmark() { return landmark; }
    
    /**
     * Calculate distance to another location using Haversine formula
     * दूसरे location तक distance calculate करना
     */
    public double distanceTo(Location other) {
        final double R = 6371; // Earth's radius in km
        
        double lat1Rad = Math.toRadians(this.latitude);
        double lon1Rad = Math.toRadians(this.longitude);
        double lat2Rad = Math.toRadians(other.latitude);
        double lon2Rad = Math.toRadians(other.longitude);
        
        double dLat = lat2Rad - lat1Rad;
        double dLon = lon2Rad - lon1Rad;
        
        double a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                   Math.cos(lat1Rad) * Math.cos(lat2Rad) *
                   Math.sin(dLon / 2) * Math.sin(dLon / 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        
        return R * c;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Location location = (Location) o;
        return Double.compare(location.latitude, latitude) == 0 &&
               Double.compare(location.longitude, longitude) == 0 &&
               Objects.equals(address, location.address);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(latitude, longitude, address);
    }
    
    @Override
    public String toString() {
        return String.format("Location(%.6f, %.6f) - %s", latitude, longitude, address);
    }
}

/**
 * Money value object - Currency amount with proper validations
 * Money value object - proper validations के साथ currency amount
 */
class Money {
    private final BigDecimal amount;
    private final String currency;
    
    public Money(BigDecimal amount, String currency) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Amount cannot be negative - रकम negative नहीं हो सकती");
        }
        if (currency == null || currency.trim().isEmpty()) {
            throw new IllegalArgumentException("Currency cannot be empty");
        }
        
        this.amount = amount.setScale(2, BigDecimal.ROUND_HALF_UP);
        this.currency = currency.toUpperCase();
    }
    
    public Money(double amount) {
        this(BigDecimal.valueOf(amount), "INR");
    }
    
    public BigDecimal getAmount() { return amount; }
    public String getCurrency() { return currency; }
    
    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("Currency mismatch - Currency match नहीं करती");
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }
    
    public Money multiply(double factor) {
        return new Money(this.amount.multiply(BigDecimal.valueOf(factor)), this.currency);
    }
    
    public boolean isGreaterThan(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("Currency mismatch");
        }
        return this.amount.compareTo(other.amount) > 0;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Money money = (Money) o;
        return Objects.equals(amount, money.amount) &&
               Objects.equals(currency, money.currency);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(amount, currency);
    }
    
    @Override
    public String toString() {
        return String.format("₹%.2f", amount.doubleValue());
    }
}

/**
 * Trip ID strong-typed identifier
 * Trip ID का strong-typed identifier
 */
class TripId {
    private final String value;
    
    public TripId(String value) {
        if (value == null || value.trim().isEmpty() || value.length() < 8) {
            throw new IllegalArgumentException("Trip ID must be at least 8 characters");
        }
        this.value = value.trim();
    }
    
    public static TripId generate() {
        return new TripId("UBER_" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
    }
    
    public String getValue() { return value; }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        TripId tripId = (TripId) o;
        return Objects.equals(value, tripId.value);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(value);
    }
    
    @Override
    public String toString() {
        return value;
    }
}

// ====================================================================
// ENUMS - Domain-specific states
// ====================================================================

enum TripStatus {
    REQUESTED("requested", "Trip requested"),
    DRIVER_ASSIGNED("driver_assigned", "Driver assigned"),
    DRIVER_ARRIVED("driver_arrived", "Driver arrived"),
    TRIP_STARTED("trip_started", "Trip in progress"),
    TRIP_COMPLETED("trip_completed", "Trip completed"),
    CANCELLED("cancelled", "Trip cancelled"),
    PAYMENT_FAILED("payment_failed", "Payment failed");
    
    private final String code;
    private final String description;
    
    TripStatus(String code, String description) {
        this.code = code;
        this.description = description;
    }
    
    public String getCode() { return code; }
    public String getDescription() { return description; }
}

enum VehicleType {
    UBER_GO("UberGo", 1.0, 4),
    UBER_PRIME("UberPrime", 1.3, 4),
    UBER_XL("UberXL", 1.8, 6),
    UBER_AUTO("UberAuto", 0.7, 3);
    
    private final String displayName;
    private final double priceMultiplier;
    private final int capacity;
    
    VehicleType(String displayName, double priceMultiplier, int capacity) {
        this.displayName = displayName;
        this.priceMultiplier = priceMultiplier;
        this.capacity = capacity;
    }
    
    public String getDisplayName() { return displayName; }
    public double getPriceMultiplier() { return priceMultiplier; }
    public int getCapacity() { return capacity; }
}

enum PaymentMethod {
    CASH("Cash", "cash"),
    UPI("UPI", "upi"),
    CREDIT_CARD("Credit Card", "credit_card"),
    DEBIT_CARD("Debit Card", "debit_card"),
    WALLET("Wallet", "wallet");
    
    private final String displayName;
    private final String code;
    
    PaymentMethod(String displayName, String code) {
        this.displayName = displayName;
        this.code = code;
    }
    
    public String getDisplayName() { return displayName; }
    public String getCode() { return code; }
}

// ====================================================================
// DOMAIN EVENTS - Events that matter to the business
// ====================================================================

/**
 * Base domain event
 * Base domain event class
 */
abstract class DomainEvent {
    private final String eventId;
    private final LocalDateTime occurredAt;
    private final String aggregateId;
    private final int version;
    
    protected DomainEvent(String aggregateId, int version) {
        this.eventId = UUID.randomUUID().toString();
        this.occurredAt = LocalDateTime.now();
        this.aggregateId = aggregateId;
        this.version = version;
    }
    
    public String getEventId() { return eventId; }
    public LocalDateTime getOccurredAt() { return occurredAt; }
    public String getAggregateId() { return aggregateId; }
    public int getVersion() { return version; }
    
    public abstract String getEventType();
}

class TripRequestedEvent extends DomainEvent {
    private final String customerId;
    private final Location pickup;
    private final Location destination;
    private final VehicleType vehicleType;
    
    public TripRequestedEvent(String aggregateId, int version, String customerId, 
                             Location pickup, Location destination, VehicleType vehicleType) {
        super(aggregateId, version);
        this.customerId = customerId;
        this.pickup = pickup;
        this.destination = destination;
        this.vehicleType = vehicleType;
    }
    
    @Override
    public String getEventType() { return "TripRequested"; }
    
    // Getters
    public String getCustomerId() { return customerId; }
    public Location getPickup() { return pickup; }
    public Location getDestination() { return destination; }
    public VehicleType getVehicleType() { return vehicleType; }
}

class DriverAssignedEvent extends DomainEvent {
    private final String driverId;
    private final String driverName;
    private final String vehicleNumber;
    private final int estimatedArrivalMinutes;
    
    public DriverAssignedEvent(String aggregateId, int version, String driverId, 
                              String driverName, String vehicleNumber, int estimatedArrivalMinutes) {
        super(aggregateId, version);
        this.driverId = driverId;
        this.driverName = driverName;
        this.vehicleNumber = vehicleNumber;
        this.estimatedArrivalMinutes = estimatedArrivalMinutes;
    }
    
    @Override
    public String getEventType() { return "DriverAssigned"; }
    
    public String getDriverId() { return driverId; }
    public String getDriverName() { return driverName; }
    public String getVehicleNumber() { return vehicleNumber; }
    public int getEstimatedArrivalMinutes() { return estimatedArrivalMinutes; }
}

class TripCompletedEvent extends DomainEvent {
    private final double actualDistance;
    private final Duration actualDuration;
    private final Money finalFare;
    
    public TripCompletedEvent(String aggregateId, int version, double actualDistance, 
                             Duration actualDuration, Money finalFare) {
        super(aggregateId, version);
        this.actualDistance = actualDistance;
        this.actualDuration = actualDuration;
        this.finalFare = finalFare;
    }
    
    @Override
    public String getEventType() { return "TripCompleted"; }
    
    public double getActualDistance() { return actualDistance; }
    public Duration getActualDuration() { return actualDuration; }
    public Money getFinalFare() { return finalFare; }
}

// ====================================================================
// AGGREGATE ROOT - Main business entity
// ====================================================================

/**
 * Trip Booking Aggregate - Core business logic for Uber trips
 * Trip Booking Aggregate - Uber trips के लिए core business logic
 */
public class UberTripBookingAggregate {
    // Identity
    private final TripId tripId;
    
    // Trip details
    private String customerId;
    private Location pickupLocation;
    private Location destinationLocation;
    private VehicleType vehicleType;
    
    // Trip state
    private TripStatus status;
    private LocalDateTime requestedAt;
    private LocalDateTime updatedAt;
    
    // Driver information
    private String driverId;
    private String driverName;
    private String vehicleNumber;
    private double driverRating;
    
    // Trip progress tracking
    private LocalDateTime driverAssignedAt;
    private LocalDateTime driverArrivedAt;
    private LocalDateTime tripStartedAt;
    private LocalDateTime tripCompletedAt;
    
    // Pricing and payment
    private Money estimatedFare;
    private Money finalFare;
    private PaymentMethod paymentMethod;
    private String paymentTransactionId;
    
    // Trip metrics
    private double estimatedDistance;
    private double actualDistance;
    private Duration estimatedDuration;
    private Duration actualDuration;
    
    // Concurrency control
    private int version;
    
    // Domain events
    private List<DomainEvent> domainEvents;
    
    // ====================================================================
    // CONSTRUCTORS AND FACTORY METHODS
    // ====================================================================
    
    /**
     * Private constructor for aggregate creation
     * Aggregate creation के लिए private constructor
     */
    private UberTripBookingAggregate(TripId tripId) {
        this.tripId = tripId;
        this.domainEvents = new ArrayList<>();
        this.version = 0;
        this.requestedAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.status = TripStatus.REQUESTED;
        
        System.out.println("🚗 Trip aggregate created: " + tripId);
    }
    
    /**
     * Factory method to request new trip
     * नयी trip request करने के लिए factory method
     */
    public static UberTripBookingAggregate requestTrip(
            String customerId,
            Location pickupLocation,
            Location destinationLocation,
            VehicleType vehicleType,
            PaymentMethod paymentMethod) {
        
        // Validate inputs
        if (customerId == null || customerId.trim().isEmpty()) {
            throw new IllegalArgumentException("Customer ID required - Customer ID जरूरी है");
        }
        if (pickupLocation == null || destinationLocation == null) {
            throw new IllegalArgumentException("Pickup and destination required - Pickup और destination जरूरी है");
        }
        
        // Check if locations are reasonable distance apart
        double distance = pickupLocation.distanceTo(destinationLocation);
        if (distance < 0.5) {
            throw new IllegalArgumentException("Trip distance too short - Trip की distance बहुत कम है");
        }
        if (distance > 500) {
            throw new IllegalArgumentException("Trip distance too long - Trip की distance बहुत ज्यादा है");
        }
        
        // Create aggregate
        TripId tripId = TripId.generate();
        UberTripBookingAggregate trip = new UberTripBookingAggregate(tripId);
        
        // Set trip details
        trip.customerId = customerId;
        trip.pickupLocation = pickupLocation;
        trip.destinationLocation = destinationLocation;
        trip.vehicleType = vehicleType;
        trip.paymentMethod = paymentMethod;
        
        // Calculate estimates
        trip.estimatedDistance = distance;
        trip.estimatedDuration = trip.calculateEstimatedDuration(distance);
        trip.estimatedFare = trip.calculateEstimatedFare(distance);
        
        // Raise domain event
        trip.addDomainEvent(new TripRequestedEvent(
            tripId.getValue(),
            trip.nextVersion(),
            customerId,
            pickupLocation,
            destinationLocation,
            vehicleType
        ));
        
        System.out.println("📱 Trip requested: " + tripId);
        System.out.println("   Distance: " + String.format("%.2f km", distance));
        System.out.println("   Estimated fare: " + trip.estimatedFare);
        System.out.println("   Vehicle type: " + vehicleType.getDisplayName());
        
        return trip;
    }
    
    // ====================================================================
    // BUSINESS METHODS - Core trip operations
    // ====================================================================
    
    /**
     * Assign driver to trip
     * Trip को driver assign करना
     */
    public void assignDriver(String driverId, String driverName, String vehicleNumber, 
                           double driverRating, int estimatedArrivalMinutes) {
        
        if (this.status != TripStatus.REQUESTED) {
            throw new InvalidTripStateException("Can only assign driver to requested trip - केवल requested trip को driver assign कर सकते हैं");
        }
        
        if (driverId == null || driverId.trim().isEmpty()) {
            throw new IllegalArgumentException("Driver ID required");
        }
        if (driverName == null || driverName.trim().isEmpty()) {
            throw new IllegalArgumentException("Driver name required");
        }
        if (driverRating < 1.0 || driverRating > 5.0) {
            throw new IllegalArgumentException("Driver rating must be between 1.0 and 5.0");
        }
        
        // Update trip state
        this.driverId = driverId;
        this.driverName = driverName;
        this.vehicleNumber = vehicleNumber;
        this.driverRating = driverRating;
        this.status = TripStatus.DRIVER_ASSIGNED;
        this.driverAssignedAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        
        // Raise domain event
        addDomainEvent(new DriverAssignedEvent(
            this.tripId.getValue(),
            nextVersion(),
            driverId,
            driverName,
            vehicleNumber,
            estimatedArrivalMinutes
        ));
        
        System.out.println("👨‍🚗 Driver assigned: " + driverName);
        System.out.println("   Vehicle: " + vehicleNumber);
        System.out.println("   Rating: " + driverRating + "⭐");
        System.out.println("   ETA: " + estimatedArrivalMinutes + " minutes");
    }
    
    /**
     * Mark driver as arrived at pickup location
     * Driver के pickup location पहुंचने को mark करना
     */
    public void markDriverArrived() {
        if (this.status != TripStatus.DRIVER_ASSIGNED) {
            throw new InvalidTripStateException("Driver must be assigned first - पहले driver assign होना चाहिए");
        }
        
        this.status = TripStatus.DRIVER_ARRIVED;
        this.driverArrivedAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("📍 Driver arrived at pickup location");
        
        // Calculate actual arrival time vs estimated
        if (this.driverAssignedAt != null) {
            Duration waitTime = Duration.between(this.driverAssignedAt, this.driverArrivedAt);
            System.out.println("   Wait time: " + waitTime.toMinutes() + " minutes");
        }
    }
    
    /**
     * Start the trip
     * Trip शुरू करना
     */
    public void startTrip() {
        if (this.status != TripStatus.DRIVER_ARRIVED) {
            throw new InvalidTripStateException("Driver must have arrived first - Driver का पहले आना जरूरी है");
        }
        
        this.status = TripStatus.TRIP_STARTED;
        this.tripStartedAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("🏁 Trip started at " + this.tripStartedAt.format(
            java.time.format.DateTimeFormatter.ofPattern("HH:mm:ss")));
    }
    
    /**
     * Complete the trip with actual metrics
     * Actual metrics के साथ trip complete करना
     */
    public void completeTrip(double actualDistance) {
        if (this.status != TripStatus.TRIP_STARTED) {
            throw new InvalidTripStateException("Trip must be started first - Trip पहले शुरू होनी चाहिए");
        }
        
        if (actualDistance <= 0) {
            throw new IllegalArgumentException("Actual distance must be positive - Actual distance positive होनी चाहिए");
        }
        
        this.actualDistance = actualDistance;
        this.tripCompletedAt = LocalDateTime.now();
        this.actualDuration = Duration.between(this.tripStartedAt, this.tripCompletedAt);
        
        // Calculate final fare based on actual distance
        this.finalFare = calculateFinalFare(actualDistance, this.actualDuration);
        
        this.status = TripStatus.TRIP_COMPLETED;
        this.updatedAt = LocalDateTime.now();
        
        // Raise domain event
        addDomainEvent(new TripCompletedEvent(
            this.tripId.getValue(),
            nextVersion(),
            actualDistance,
            this.actualDuration,
            this.finalFare
        ));
        
        System.out.println("🎉 Trip completed!");
        System.out.println("   Actual distance: " + String.format("%.2f km", actualDistance));
        System.out.println("   Duration: " + this.actualDuration.toMinutes() + " minutes");
        System.out.println("   Final fare: " + this.finalFare);
    }
    
    /**
     * Process payment for the trip
     * Trip के लिए payment process करना
     */
    public void processPayment(String transactionId) {
        if (this.status != TripStatus.TRIP_COMPLETED) {
            throw new InvalidTripStateException("Trip must be completed first - Trip पहले complete होनी चाहिए");
        }
        
        if (transactionId == null || transactionId.trim().isEmpty()) {
            throw new IllegalArgumentException("Transaction ID required");
        }
        
        // Simulate payment processing
        boolean paymentSuccess = simulatePaymentProcessing(this.finalFare, this.paymentMethod);
        
        if (paymentSuccess) {
            this.paymentTransactionId = transactionId;
            System.out.println("💳 Payment successful: " + transactionId);
        } else {
            this.status = TripStatus.PAYMENT_FAILED;
            throw new PaymentFailedException("Payment processing failed - Payment process नहीं हुई");
        }
        
        this.updatedAt = LocalDateTime.now();
    }
    
    /**
     * Cancel trip with reason
     * Trip को reason के साथ cancel करना
     */
    public void cancelTrip(String reason, String cancelledBy) {
        if (this.status == TripStatus.TRIP_COMPLETED) {
            throw new InvalidTripStateException("Cannot cancel completed trip - Complete trip cancel नहीं हो सकती");
        }
        
        if (reason == null || reason.trim().isEmpty()) {
            throw new IllegalArgumentException("Cancellation reason required");
        }
        
        TripStatus previousStatus = this.status;
        this.status = TripStatus.CANCELLED;
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("❌ Trip cancelled by " + cancelledBy);
        System.out.println("   Reason: " + reason);
        System.out.println("   Previous status: " + previousStatus.getDescription());
        
        // Calculate cancellation charges if applicable
        Money cancellationFee = calculateCancellationFee(previousStatus);
        if (cancellationFee.getAmount().compareTo(BigDecimal.ZERO) > 0) {
            System.out.println("   Cancellation fee: " + cancellationFee);
        }
    }
    
    // ====================================================================
    // BUSINESS LOGIC - Calculations and validations
    // ====================================================================
    
    /**
     * Calculate estimated trip duration
     * Estimated trip duration calculate करना
     */
    private Duration calculateEstimatedDuration(double distance) {
        // Average speed in city: 25 km/h including traffic
        double averageSpeedKmh = 25.0;
        double hours = distance / averageSpeedKmh;
        long minutes = Math.round(hours * 60);
        
        // Minimum 10 minutes, maximum 4 hours
        minutes = Math.max(10, Math.min(240, minutes));
        
        return Duration.ofMinutes(minutes);
    }
    
    /**
     * Calculate estimated fare based on distance
     * Distance के base पर estimated fare calculate करना
     */
    private Money calculateEstimatedFare(double distance) {
        // Base fare structure (Delhi/Mumbai pricing)
        double baseFare = 50.0;  // ₹50 base fare
        double perKmRate = 12.0; // ₹12 per km
        
        // Calculate base amount
        double amount = baseFare + (distance * perKmRate);
        
        // Apply vehicle type multiplier
        amount *= this.vehicleType.getPriceMultiplier();
        
        // Apply time-based surge if needed
        double surgeMultiplier = calculateSurgeMultiplier();
        amount *= surgeMultiplier;
        
        // Add taxes (5% GST)
        amount *= 1.05;
        
        // Round to nearest rupee
        amount = Math.round(amount);
        
        return new Money(amount);
    }
    
    /**
     * Calculate final fare based on actual metrics
     * Actual metrics के base पर final fare calculate करना
     */
    private Money calculateFinalFare(double actualDistance, Duration actualDuration) {
        // Base calculation
        double baseFare = 50.0;
        double perKmRate = 12.0;
        double perMinuteRate = 1.5; // ₹1.5 per minute for time component
        
        double amount = baseFare + 
                       (actualDistance * perKmRate) + 
                       (actualDuration.toMinutes() * perMinuteRate);
        
        // Apply vehicle type multiplier
        amount *= this.vehicleType.getPriceMultiplier();
        
        // Apply surge if it was active during booking
        double surgeMultiplier = calculateSurgeMultiplier();
        amount *= surgeMultiplier;
        
        // Add taxes
        amount *= 1.05;
        
        // Apply discounts if any (loyalty, promo codes, etc.)
        amount = applyDiscounts(amount);
        
        // Minimum fare protection
        amount = Math.max(amount, 80.0); // Minimum ₹80
        
        return new Money(Math.round(amount));
    }
    
    /**
     * Calculate surge multiplier based on demand and supply
     * Demand और supply के base पर surge multiplier calculate करना
     */
    private double calculateSurgeMultiplier() {
        LocalDateTime now = LocalDateTime.now();
        int hour = now.getHour();
        
        // Peak hours surge
        if ((hour >= 8 && hour <= 10) || (hour >= 18 && hour <= 21)) {
            return 1.5; // 1.5x surge during peak hours
        }
        
        // Late night surge
        if (hour >= 23 || hour <= 5) {
            return 1.3; // 1.3x surge late night
        }
        
        // Weekend surge (simplified)
        if (now.getDayOfWeek().getValue() >= 6) {
            return 1.2; // 1.2x weekend surge
        }
        
        return 1.0; // No surge
    }
    
    /**
     * Apply discounts and offers
     * Discounts और offers apply करना
     */
    private double applyDiscounts(double amount) {
        // First ride discount for new users
        // Loyalty program discounts
        // Promo code discounts
        // Corporate account discounts
        
        // For now, no discounts applied
        return amount;
    }
    
    /**
     * Calculate cancellation fee based on trip status
     * Trip status के base पर cancellation fee calculate करना
     */
    private Money calculateCancellationFee(TripStatus statusAtCancellation) {
        switch (statusAtCancellation) {
            case REQUESTED:
                return new Money(0.0); // No fee for early cancellation
            case DRIVER_ASSIGNED:
                return new Money(20.0); // ₹20 if driver was assigned
            case DRIVER_ARRIVED:
                return new Money(50.0); // ₹50 if driver reached pickup
            case TRIP_STARTED:
                return new Money(100.0); // ₹100 if trip was started
            default:
                return new Money(0.0);
        }
    }
    
    /**
     * Simulate payment processing
     * Payment processing को simulate करना
     */
    private boolean simulatePaymentProcessing(Money amount, PaymentMethod method) {
        System.out.println("💳 Processing payment of " + amount + " via " + method.getDisplayName());
        
        // Simulate different success rates for different payment methods
        Random random = new Random();
        double successRate = switch (method) {
            case CASH -> 1.0; // Cash always succeeds
            case UPI -> 0.95; // 95% success rate
            case CREDIT_CARD -> 0.90; // 90% success rate
            case DEBIT_CARD -> 0.85; // 85% success rate
            case WALLET -> 0.98; // 98% success rate
        };
        
        return random.nextDouble() < successRate;
    }
    
    // ====================================================================
    // QUERY METHODS - Information retrieval
    // ====================================================================
    
    /**
     * Get comprehensive trip summary
     * Complete trip summary निकालना
     */
    public Map<String, Object> getTripSummary() {
        Map<String, Object> summary = new HashMap<>();
        
        summary.put("tripId", tripId.getValue());
        summary.put("customerId", customerId);
        summary.put("status", status.getDescription());
        summary.put("vehicleType", vehicleType.getDisplayName());
        summary.put("paymentMethod", paymentMethod.getDisplayName());
        
        // Locations
        summary.put("pickup", pickupLocation.getAddress());
        summary.put("destination", destinationLocation.getAddress());
        
        // Driver info (if assigned)
        if (driverId != null) {
            Map<String, Object> driverInfo = new HashMap<>();
            driverInfo.put("driverId", driverId);
            driverInfo.put("driverName", driverName);
            driverInfo.put("vehicleNumber", vehicleNumber);
            driverInfo.put("rating", driverRating);
            summary.put("driver", driverInfo);
        }
        
        // Pricing
        summary.put("estimatedFare", estimatedFare != null ? estimatedFare.toString() : null);
        summary.put("finalFare", finalFare != null ? finalFare.toString() : null);
        
        // Metrics
        summary.put("estimatedDistance", String.format("%.2f km", estimatedDistance));
        if (actualDistance > 0) {
            summary.put("actualDistance", String.format("%.2f km", actualDistance));
        }
        
        // Timeline
        Map<String, String> timeline = new HashMap<>();
        timeline.put("requested", requestedAt.toString());
        if (driverAssignedAt != null) timeline.put("driverAssigned", driverAssignedAt.toString());
        if (driverArrivedAt != null) timeline.put("driverArrived", driverArrivedAt.toString());
        if (tripStartedAt != null) timeline.put("tripStarted", tripStartedAt.toString());
        if (tripCompletedAt != null) timeline.put("tripCompleted", tripCompletedAt.toString());
        summary.put("timeline", timeline);
        
        return summary;
    }
    
    /**
     * Check if trip is in progress
     * Trip progress में है या नहीं check करना
     */
    public boolean isInProgress() {
        return status == TripStatus.TRIP_STARTED;
    }
    
    /**
     * Check if trip is completed
     * Trip complete है या नहीं check करना
     */
    public boolean isCompleted() {
        return status == TripStatus.TRIP_COMPLETED;
    }
    
    /**
     * Get current trip status
     * Current trip status निकालना
     */
    public TripStatus getCurrentStatus() {
        return status;
    }
    
    // ====================================================================
    // DOMAIN EVENT MANAGEMENT
    // ====================================================================
    
    private void addDomainEvent(DomainEvent event) {
        this.domainEvents.add(event);
    }
    
    public List<DomainEvent> getDomainEvents() {
        return new ArrayList<>(domainEvents);
    }
    
    public void clearDomainEvents() {
        this.domainEvents.clear();
    }
    
    private int nextVersion() {
        return ++this.version;
    }
    
    // ====================================================================
    // GETTERS - Controlled access to aggregate state
    // ====================================================================
    
    public TripId getTripId() { return tripId; }
    public String getCustomerId() { return customerId; }
    public Location getPickupLocation() { return pickupLocation; }
    public Location getDestinationLocation() { return destinationLocation; }
    public VehicleType getVehicleType() { return vehicleType; }
    public String getDriverId() { return driverId; }
    public String getDriverName() { return driverName; }
    public Money getEstimatedFare() { return estimatedFare; }
    public Money getFinalFare() { return finalFare; }
    public LocalDateTime getRequestedAt() { return requestedAt; }
    public int getVersion() { return version; }
    
    @Override
    public String toString() {
        return String.format("UberTrip(%s: %s - %s)", 
            tripId, status.getDescription(), 
            estimatedFare != null ? estimatedFare.toString() : "No fare");
    }
    
    // ====================================================================
    // DEMO AND TESTING
    // ====================================================================
    
    /**
     * Demo method showing complete trip lifecycle
     * Complete trip lifecycle दिखाने वाला demo method
     */
    public static void main(String[] args) {
        System.out.println("🚗 Uber Trip Booking Aggregate - DDD Example");
        System.out.println("=" + "=".repeat(50));
        
        try {
            // Create locations
            Location pickup = new Location(19.0596, 72.8295, "Bandra West, Mumbai", "Linking Road");
            Location destination = new Location(19.1197, 72.8464, "Andheri West, Mumbai", "Lokhandwala");
            
            System.out.println("\n📍 Trip Details:");
            System.out.println("   Pickup: " + pickup.getAddress());
            System.out.println("   Destination: " + destination.getAddress());
            System.out.println("   Distance: " + String.format("%.2f km", pickup.distanceTo(destination)));
            
            // Request trip
            System.out.println("\n🔄 Step 1: Request Trip");
            UberTripBookingAggregate trip = UberTripBookingAggregate.requestTrip(
                "CUSTOMER_12345",
                pickup,
                destination,
                VehicleType.UBER_PRIME,
                PaymentMethod.UPI
            );
            
            // Assign driver
            System.out.println("\n🔄 Step 2: Assign Driver");
            trip.assignDriver(
                "DRIVER_67890",
                "Rajesh Kumar",
                "MH 01 AB 1234",
                4.7,
                8 // 8 minutes ETA
            );
            
            // Driver arrives
            System.out.println("\n🔄 Step 3: Driver Arrives");
            // Simulate some wait time
            try { Thread.sleep(1000); } catch (InterruptedException e) {}
            trip.markDriverArrived();
            
            // Start trip
            System.out.println("\n🔄 Step 4: Start Trip");
            trip.startTrip();
            
            // Complete trip
            System.out.println("\n🔄 Step 5: Complete Trip");
            // Simulate trip duration
            try { Thread.sleep(2000); } catch (InterruptedException e) {}
            trip.completeTrip(12.3); // Actual distance traveled
            
            // Process payment
            System.out.println("\n🔄 Step 6: Process Payment");
            trip.processPayment("TXN_" + System.currentTimeMillis());
            
            // Show trip summary
            System.out.println("\n📊 Trip Summary:");
            Map<String, Object> summary = trip.getTripSummary();
            summary.forEach((key, value) -> {
                if (value instanceof Map) {
                    System.out.println("   " + key + ":");
                    ((Map<?, ?>) value).forEach((k, v) -> 
                        System.out.println("     " + k + ": " + v));
                } else {
                    System.out.println("   " + key + ": " + value);
                }
            });
            
            // Show domain events
            System.out.println("\n📋 Domain Events Generated:");
            List<DomainEvent> events = trip.getDomainEvents();
            for (int i = 0; i < events.size(); i++) {
                DomainEvent event = events.get(i);
                System.out.println("   " + (i+1) + ". " + event.getEventType() + 
                    " at " + event.getOccurredAt().format(
                        java.time.format.DateTimeFormatter.ofPattern("HH:mm:ss")));
            }
            
            System.out.println("\n✨ Trip completed successfully!");
            System.out.println("✨ All business rules enforced correctly!");
            System.out.println("✨ Ready for production Uber-scale system!");
            
        } catch (Exception e) {
            System.err.println("❌ Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
// Ola Ride Matching Service - Service Mesh Integration
// भारत की सबसे बड़ी cab service के लिए ride matching algorithm
// Handles 1M+ ride requests daily across 300+ cities

package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "math"
    "net/http"
    "sort"
    "strconv"
    "sync"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/go-redis/redis/v8"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/trace"
    "go.uber.org/zap"
)

// Geographic coordinates for Indian cities
type Location struct {
    Latitude  float64 `json:"latitude" binding:"required"`
    Longitude float64 `json:"longitude" binding:"required"`
    Address   string  `json:"address,omitempty"`
}

// Ride request from customer
type RideRequest struct {
    RequestID    string    `json:"request_id" binding:"required"`
    CustomerID   string    `json:"customer_id" binding:"required"`
    PickupLoc    Location  `json:"pickup_location" binding:"required"`
    DropLoc      Location  `json:"drop_location" binding:"required"`
    RideType     string    `json:"ride_type" binding:"required"` // MICRO, MINI, PRIME, LUX
    RequestTime  time.Time `json:"request_time"`
    MaxWaitTime  int       `json:"max_wait_time"` // seconds
    PaymentMode  string    `json:"payment_mode"`  // CASH, WALLET, UPI, CARD
}

// Driver information with real-time location
type Driver struct {
    DriverID     string    `json:"driver_id"`
    Name         string    `json:"name"`
    PhoneNumber  string    `json:"phone_number"`
    CurrentLoc   Location  `json:"current_location"`
    VehicleType  string    `json:"vehicle_type"`
    Rating       float64   `json:"rating"`
    IsAvailable  bool      `json:"is_available"`
    LastUpdated  time.Time `json:"last_updated"`
    City         string    `json:"city"` // Mumbai, Bangalore, Delhi, etc.
}

// Matched ride response
type RideMatch struct {
    RequestID       string  `json:"request_id"`
    DriverID        string  `json:"driver_id"`
    DriverName      string  `json:"driver_name"`
    DriverPhone     string  `json:"driver_phone"`
    VehicleNumber   string  `json:"vehicle_number"`
    EstimatedArrival int     `json:"estimated_arrival_minutes"`
    Distance        float64 `json:"distance_km"`
    EstimatedFare   float64 `json:"estimated_fare_inr"`
    MatchScore      float64 `json:"match_score"`
}

// Ride matching service structure
type OlaRideMatchingService struct {
    redisClient    *redis.Client
    logger         *zap.Logger
    tracer         trace.Tracer
    driversCache   sync.Map
    requestMetrics *prometheus.CounterVec
    matchTimeHist  prometheus.Histogram
}

// Prometheus metrics for monitoring
var (
    rideRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "ola_ride_requests_total",
            Help: "Total number of ride requests by city and type",
        },
        []string{"city", "ride_type", "status"},
    )

    matchingTimeHistogram = prometheus.NewHistogram(
        prometheus.HistogramOpts{
            Name:    "ola_ride_matching_duration_seconds",
            Help:    "Time taken to match a ride",
            Buckets: prometheus.DefBuckets,
        },
    )

    activeDriversGauge = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "ola_active_drivers_total",
            Help: "Number of active drivers by city",
        },
        []string{"city"},
    )
)

func init() {
    // Register Prometheus metrics
    prometheus.MustRegister(rideRequestsTotal)
    prometheus.MustRegister(matchingTimeHistogram)
    prometheus.MustRegister(activeDriversGauge)
}

// Initialize Ola ride matching service
func NewOlaRideMatchingService() *OlaRideMatchingService {
    // Initialize logger
    logger, _ := zap.NewProduction()
    
    // Initialize Redis client for driver location cache
    rdb := redis.NewClient(&redis.Options{
        Addr:         "redis:6379",
        PoolSize:     100,
        DialTimeout:  5 * time.Second,
        ReadTimeout:  3 * time.Second,
        WriteTimeout: 3 * time.Second,
    })

    // Initialize OpenTelemetry tracer for service mesh observability
    tracer := otel.Tracer("ola-ride-matching")

    return &OlaRideMatchingService{
        redisClient:    rdb,
        logger:         logger,
        tracer:         tracer,
        requestMetrics: rideRequestsTotal,
        matchTimeHist:  matchingTimeHistogram,
    }
}

// Calculate distance between two points using Haversine formula
// भारतीय शहरों के बीच दूरी calculate करने के लिए
func (s *OlaRideMatchingService) calculateDistance(loc1, loc2 Location) float64 {
    const earthRadius = 6371 // Earth radius in kilometers

    lat1Rad := loc1.Latitude * math.Pi / 180
    lat2Rad := loc2.Latitude * math.Pi / 180
    deltaLat := (loc2.Latitude - loc1.Latitude) * math.Pi / 180
    deltaLng := (loc2.Longitude - loc1.Longitude) * math.Pi / 180

    a := math.Sin(deltaLat/2)*math.Sin(deltaLat/2) +
        math.Cos(lat1Rad)*math.Cos(lat2Rad)*
            math.Sin(deltaLng/2)*math.Sin(deltaLng/2)
    c := 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))

    return earthRadius * c
}

// Get nearby drivers from Redis geospatial index
// आस-पास के drivers को find करने के लिए Redis geo commands
func (s *OlaRideMatchingService) getNearbyDrivers(ctx context.Context, location Location, radius float64) ([]Driver, error) {
    ctx, span := s.tracer.Start(ctx, "get_nearby_drivers")
    defer span.End()

    span.SetAttributes(
        attribute.Float64("latitude", location.Latitude),
        attribute.Float64("longitude", location.Longitude),
        attribute.Float64("radius_km", radius),
    )

    // Redis GEORADIUS command to find nearby drivers
    cmd := s.redisClient.GeoRadius(ctx, "drivers:locations", location.Longitude, location.Latitude, &redis.GeoRadiusQuery{
        Radius:    radius,
        Unit:      "km",
        WithCoord: true,
        WithDist:  true,
        Count:     50, // Limit to 50 nearest drivers
        Sort:      "ASC",
    })

    results, err := cmd.Result()
    if err != nil {
        s.logger.Error("Failed to get nearby drivers", zap.Error(err))
        return nil, err
    }

    var drivers []Driver
    for _, result := range results {
        // Get detailed driver info from Redis hash
        driverInfo := s.redisClient.HGetAll(ctx, fmt.Sprintf("driver:%s", result.Name))
        if driverInfo.Err() != nil {
            continue
        }

        driverData := driverInfo.Val()
        
        // Check if driver is available
        if driverData["is_available"] != "true" {
            continue
        }

        rating, _ := strconv.ParseFloat(driverData["rating"], 64)
        
        driver := Driver{
            DriverID:     result.Name,
            Name:         driverData["name"],
            PhoneNumber:  driverData["phone"],
            VehicleType:  driverData["vehicle_type"],
            Rating:       rating,
            IsAvailable:  true,
            CurrentLoc: Location{
                Latitude:  result.GeoPos.Latitude,
                Longitude: result.GeoPos.Longitude,
            },
            City: driverData["city"],
        }
        
        drivers = append(drivers, driver)
    }

    span.SetAttributes(attribute.Int("drivers_found", len(drivers)))
    return drivers, nil
}

// Match ride request with best available driver
// सबसे suitable driver के साथ ride match करने की algorithm
func (s *OlaRideMatchingService) matchRide(ctx context.Context, request RideRequest) (*RideMatch, error) {
    startTime := time.Now()
    defer func() {
        s.matchTimeHist.Observe(time.Since(startTime).Seconds())
    }()

    ctx, span := s.tracer.Start(ctx, "match_ride")
    defer span.End()

    span.SetAttributes(
        attribute.String("request_id", request.RequestID),
        attribute.String("ride_type", request.RideType),
    )

    // Find nearby drivers within 5km radius
    nearbyDrivers, err := s.getNearbyDrivers(ctx, request.PickupLoc, 5.0)
    if err != nil {
        return nil, err
    }

    if len(nearbyDrivers) == 0 {
        s.requestMetrics.WithLabelValues("unknown", request.RideType, "no_drivers").Inc()
        return nil, fmt.Errorf("कोई driver उपलब्ध नहीं है")
    }

    // Score and rank drivers based on multiple factors
    type driverScore struct {
        driver Driver
        score  float64
    }

    var scoredDrivers []driverScore

    for _, driver := range nearbyDrivers {
        // Skip if vehicle type doesn't match ride type
        if !s.isVehicleTypeCompatible(driver.VehicleType, request.RideType) {
            continue
        }

        score := s.calculateDriverScore(request, driver)
        scoredDrivers = append(scoredDrivers, driverScore{
            driver: driver,
            score:  score,
        })
    }

    if len(scoredDrivers) == 0 {
        s.requestMetrics.WithLabelValues("unknown", request.RideType, "no_compatible_drivers").Inc()
        return nil, fmt.Errorf("कोई suitable driver नहीं मिला")
    }

    // Sort drivers by score (highest first)
    sort.Slice(scoredDrivers, func(i, j int) bool {
        return scoredDrivers[i].score > scoredDrivers[j].score
    })

    bestDriver := scoredDrivers[0].driver
    distance := s.calculateDistance(request.PickupLoc, bestDriver.CurrentLoc)
    
    // Estimate fare based on distance and ride type
    estimatedFare := s.calculateFare(request, distance)
    
    // Estimate arrival time (assuming average speed in Indian cities)
    estimatedArrival := s.calculateArrivalTime(distance, bestDriver.City)

    match := &RideMatch{
        RequestID:        request.RequestID,
        DriverID:         bestDriver.DriverID,
        DriverName:       bestDriver.Name,
        DriverPhone:      bestDriver.PhoneNumber,
        VehicleNumber:    fmt.Sprintf("HR-%02d-%04d", time.Now().Day(), time.Now().Hour()*100),
        EstimatedArrival: estimatedArrival,
        Distance:         distance,
        EstimatedFare:    estimatedFare,
        MatchScore:       scoredDrivers[0].score,
    }

    // Mark driver as busy
    s.redisClient.HSet(ctx, fmt.Sprintf("driver:%s", bestDriver.DriverID), "is_available", "false")
    
    s.requestMetrics.WithLabelValues(bestDriver.City, request.RideType, "matched").Inc()
    s.logger.Info("Ride matched successfully",
        zap.String("request_id", request.RequestID),
        zap.String("driver_id", bestDriver.DriverID),
        zap.Float64("match_score", scoredDrivers[0].score),
        zap.Float64("distance_km", distance),
    )

    return match, nil
}

// Calculate driver matching score based on multiple factors
func (s *OlaRideMatchingService) calculateDriverScore(request RideRequest, driver Driver) float64 {
    var score float64

    // Distance factor (closer is better) - 40% weightage
    distance := s.calculateDistance(request.PickupLoc, driver.CurrentLoc)
    distanceScore := math.Max(0, 5-distance) / 5 * 40

    // Rating factor - 30% weightage  
    ratingScore := driver.Rating / 5 * 30

    // Availability time factor - 20% weightage
    timeSinceUpdate := time.Since(driver.LastUpdated).Minutes()
    availabilityScore := math.Max(0, 30-timeSinceUpdate) / 30 * 20

    // Vehicle type preference - 10% weightage
    vehicleScore := s.getVehicleTypeScore(driver.VehicleType, request.RideType) * 10

    score = distanceScore + ratingScore + availabilityScore + vehicleScore

    return score
}

// Check if vehicle type is compatible with ride type
func (s *OlaRideMatchingService) isVehicleTypeCompatible(vehicleType, rideType string) bool {
    compatibility := map[string][]string{
        "MICRO": {"HATCHBACK", "SEDAN"},
        "MINI":  {"HATCHBACK", "SEDAN", "COMPACT_SUV"},
        "PRIME": {"SEDAN", "COMPACT_SUV", "SUV"},
        "LUX":   {"LUXURY_SEDAN", "LUXURY_SUV"},
    }

    compatibleVehicles, exists := compatibility[rideType]
    if !exists {
        return false
    }

    for _, compatible := range compatibleVehicles {
        if vehicleType == compatible {
            return true
        }
    }
    return false
}

// Get vehicle type preference score
func (s *OlaRideMatchingService) getVehicleTypeScore(vehicleType, rideType string) float64 {
    // Perfect match gets full score
    preferredVehicles := map[string]string{
        "MICRO": "HATCHBACK",
        "MINI":  "SEDAN", 
        "PRIME": "COMPACT_SUV",
        "LUX":   "LUXURY_SEDAN",
    }

    if preferredVehicles[rideType] == vehicleType {
        return 1.0
    }

    // Compatible but not preferred gets partial score
    if s.isVehicleTypeCompatible(vehicleType, rideType) {
        return 0.7
    }

    return 0.0
}

// Calculate estimated fare in INR based on Indian city rates
func (s *OlaRideMatchingService) calculateFare(request RideRequest, distance float64) float64 {
    baseRates := map[string]map[string]float64{
        "MICRO": {"base": 15, "per_km": 8},
        "MINI":  {"base": 20, "per_km": 10},
        "PRIME": {"base": 35, "per_km": 12},
        "LUX":   {"base": 50, "per_km": 18},
    }

    rateCard := baseRates[request.RideType]
    baseFare := rateCard["base"]
    perKmRate := rateCard["per_km"]

    tripDistance := s.calculateDistance(request.PickupLoc, request.DropLoc)
    totalFare := baseFare + (tripDistance * perKmRate)

    // Add surge pricing during peak hours (7-10 AM, 6-9 PM IST)
    hour := time.Now().In(time.FixedZone("IST", 5*60*60+30*60)).Hour()
    if (hour >= 7 && hour <= 10) || (hour >= 18 && hour <= 21) {
        totalFare *= 1.5 // 1.5x surge during peak hours
    }

    // Round to nearest rupee
    return math.Round(totalFare)
}

// Calculate estimated arrival time based on city traffic conditions
func (s *OlaRideMatchingService) calculateArrivalTime(distance float64, city string) int {
    // Average speeds in different Indian cities (km/h)
    citySpeedMap := map[string]float64{
        "Mumbai":    12, // Heavy traffic
        "Delhi":     15, // Moderate traffic  
        "Bangalore": 18, // Tech city traffic
        "Chennai":   20, // Relatively better
        "Hyderabad": 22, // Good road infrastructure
        "Pune":      25, // Better traffic management
    }

    averageSpeed, exists := citySpeedMap[city]
    if !exists {
        averageSpeed = 18 // Default speed
    }

    // Calculate time in minutes
    timeInHours := distance / averageSpeed
    timeInMinutes := timeInHours * 60

    // Add buffer time for Indian road conditions
    bufferTime := 3 // 3 minutes buffer
    
    return int(math.Ceil(timeInMinutes)) + bufferTime
}

// HTTP handler for ride matching requests
func (s *OlaRideMatchingService) handleRideRequest(c *gin.Context) {
    ctx := c.Request.Context()
    
    var request RideRequest
    if err := c.ShouldBindJSON(&request); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "error":   "Invalid request format",
            "message": "कृपया सही request format का उपयोग करें",
            "details": err.Error(),
        })
        return
    }

    request.RequestTime = time.Now()

    // Match ride with best available driver
    match, err := s.matchRide(ctx, request)
    if err != nil {
        c.JSON(http.StatusNotFound, gin.H{
            "error":   "No driver available", 
            "message": err.Error(),
        })
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "status": "success",
        "data":   match,
        "message": "राइड successfully match हो गई!",
    })
}

// Health check endpoint for Kubernetes
func (s *OlaRideMatchingService) healthCheck(c *gin.Context) {
    ctx := c.Request.Context()
    
    // Check Redis connectivity
    _, err := s.redisClient.Ping(ctx).Result()
    if err != nil {
        c.JSON(http.StatusServiceUnavailable, gin.H{
            "status": "unhealthy",
            "error":  "Redis connection failed",
        })
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "status":  "healthy",
        "service": "ola-ride-matching",
        "version": "2.1.0",
    })
}

func main() {
    // Initialize service
    service := NewOlaRideMatchingService()
    defer service.redisClient.Close()

    // Initialize Gin router with recovery middleware
    gin.SetMode(gin.ReleaseMode)
    router := gin.New()
    router.Use(gin.Recovery())

    // Add request logging middleware
    router.Use(gin.LoggerWithFormatter(func(param gin.LogFormatterParams) string {
        return fmt.Sprintf("%s - [%s] \"%s %s %s %d %s \"%s\" %s\"\n",
            param.ClientIP,
            param.TimeStamp.Format(time.RFC1123),
            param.Method,
            param.Path,
            param.Request.Proto,
            param.StatusCode,
            param.Latency,
            param.Request.UserAgent(),
            param.ErrorMessage,
        )
    }))

    // API routes
    v1 := router.Group("/api/v1")
    {
        v1.POST("/match-ride", service.handleRideRequest)
        v1.GET("/health", service.healthCheck)
    }

    // Prometheus metrics endpoint
    router.GET("/metrics", gin.WrapH(promhttp.Handler()))

    // Start HTTP server
    log.Println("🚗 Ola Ride Matching Service starting on port 8080")
    log.Println("🇮🇳 Serving ride requests across 300+ Indian cities")
    
    if err := router.Run(":8080"); err != nil {
        log.Fatal("Failed to start server:", err)
    }
}
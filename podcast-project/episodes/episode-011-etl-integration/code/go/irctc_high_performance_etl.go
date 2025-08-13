// IRCTC High Performance ETL Pipeline - Episode 11
// Production-grade Go ETL with advanced concurrency patterns and performance optimization
//
// यह Go में high-performance ETL pipeline दिखाता है जो:
// - Goroutine pools और worker patterns
// - Channel-based communication
// - Memory pool management
// - Context-based cancellation
// - Metrics और monitoring
//
// Indian Context: IRCTC railway reservation system scale (10M+ bookings/day)

package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"sync/atomic"
	"time"
	"runtime"
	"os"
	"os/signal"
	"syscall"
	"math/rand"
	"strconv"
	"strings"
	
	"github.com/go-redis/redis/v8"
	"github.com/lib/pq"
	_ "github.com/lib/pq"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// Performance constants - IRCTC scale metrics
const (
	BatchSize         = 5000    // 5K bookings per batch
	WorkerPoolSize    = 20      // 20 concurrent workers
	ChannelBufferSize = 1000    // Channel buffer size
	MaxRetries        = 3       // Maximum retry attempts
	ProcessingTimeout = 300     // 5 minutes timeout
	CacheExpiration   = 1800    // 30 minutes cache TTL
)

// Booking record structure - IRCTC booking data model
type BookingRecord struct {
	BookingID    string    `json:"booking_id"`
	UserID       string    `json:"user_id"`
	TrainNumber  string    `json:"train_number"`
	FromStation  string    `json:"from_station"`
	ToStation    string    `json:"to_station"`
	JourneyDate  time.Time `json:"journey_date"`
	BookingDate  time.Time `json:"booking_date"`
	PassengerCount int     `json:"passenger_count"`
	TotalFare    float64   `json:"total_fare"`
	Class        string    `json:"class"`
	Status       string    `json:"status"`
	PaymentMode  string    `json:"payment_mode"`
}

// Enriched booking with additional context
type EnrichedBooking struct {
	*BookingRecord
	TrainName       string  `json:"train_name"`
	RouteDistance   int     `json:"route_distance_km"`
	UserTier        string  `json:"user_tier"`
	BookingScore    float64 `json:"booking_score"`
	ProcessedAt     time.Time `json:"processed_at"`
	ProcessingTimeMs int64   `json:"processing_time_ms"`
}

// Train information cache
type TrainInfo struct {
	TrainNumber string `json:"train_number"`
	TrainName   string `json:"train_name"`
	Type        string `json:"type"` // Express, Superfast, Rajdhani, etc.
	MaxSpeed    int    `json:"max_speed_kmph"`
	IsActive    bool   `json:"is_active"`
	CachedAt    time.Time `json:"cached_at"`
}

// Route information cache
type RouteInfo struct {
	FromStation string `json:"from_station"`
	ToStation   string `json:"to_station"`
	Distance    int    `json:"distance_km"`
	Duration    int    `json:"duration_minutes"`
	Frequency   int    `json:"daily_frequency"`
	CachedAt    time.Time `json:"cached_at"`
}

// User profile cache
type UserProfile struct {
	UserID         string    `json:"user_id"`
	Tier           string    `json:"tier"` // GENERAL, PREMIUM, VIP
	TotalBookings  int       `json:"total_bookings"`
	LastBookingAt  time.Time `json:"last_booking_at"`
	PreferredClass string    `json:"preferred_class"`
	HomeStation    string    `json:"home_station"`
	CachedAt       time.Time `json:"cached_at"`
}

// Processing result with metrics
type ProcessingResult struct {
	ProcessedRecords int64         `json:"processed_records"`
	SuccessCount     int64         `json:"success_count"`
	ErrorCount       int64         `json:"error_count"`
	ProcessingTime   time.Duration `json:"processing_time"`
	Throughput       float64       `json:"throughput_per_second"`
	Errors           []ProcessingError `json:"errors,omitempty"`
}

// Processing error details
type ProcessingError struct {
	BookingID string `json:"booking_id"`
	Message   string `json:"message"`
	Timestamp time.Time `json:"timestamp"`
}

// Memory pool for reusing objects
var bookingPool = sync.Pool{
	New: func() interface{} {
		return &EnrichedBooking{}
	},
}

// Prometheus metrics for monitoring
var (
	processedBookingsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "irctc_etl_processed_bookings_total",
			Help: "Total number of processed bookings",
		},
		[]string{"status"},
	)
	
	processingDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "irctc_etl_processing_duration_seconds",
			Help:    "Processing duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"operation"},
	)
	
	cacheHitRate = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "irctc_etl_cache_hit_rate",
			Help: "Cache hit rate percentage",
		},
		[]string{"cache_type"},
	)
)

// IRCTC ETL Performance Pipeline
type IRCTCETLPipeline struct {
	ctx         context.Context
	cancel      context.CancelFunc
	db          *sql.DB
	redisClient *redis.Client
	
	// Worker pools
	extractWorkers   chan struct{}
	transformWorkers chan struct{}
	loadWorkers      chan struct{}
	
	// Channels for pipeline stages
	rawBookings     chan *BookingRecord
	enrichedBookings chan *EnrichedBooking
	processedResults chan *ProcessingResult
	
	// Caches with TTL support
	trainCache   sync.Map // map[string]*TrainInfo
	routeCache   sync.Map // map[string]*RouteInfo
	userCache    sync.Map // map[string]*UserProfile
	
	// Performance metrics
	stats struct {
		ProcessedCount int64
		ErrorCount     int64
		CacheHits      int64
		CacheMisses    int64
		StartTime      time.Time
	}
	
	// Configuration
	config *ETLConfig
}

// ETL Configuration
type ETLConfig struct {
	DatabaseURL      string
	RedisURL         string
	BatchSize        int
	WorkerCount      int
	ProcessingTimeout time.Duration
	CacheExpiration  time.Duration
	EnableMetrics    bool
	LogLevel         string
}

// Initialize IRCTC ETL Pipeline
func NewIRCTCETLPipeline(config *ETLConfig) (*IRCTCETLPipeline, error) {
	ctx, cancel := context.WithCancel(context.Background())
	
	// Initialize database connection
	db, err := sql.Open("postgres", config.DatabaseURL)
	if err != nil {
		cancel()
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}
	
	// Configure database connection pool
	db.SetMaxOpenConns(50)
	db.SetMaxIdleConns(20)
	db.SetConnMaxLifetime(30 * time.Minute)
	
	// Initialize Redis client
	opt, err := redis.ParseURL(config.RedisURL)
	if err != nil {
		cancel()
		return nil, fmt.Errorf("failed to parse Redis URL: %w", err)
	}
	
	redisClient := redis.NewClient(opt)
	
	// Test Redis connection
	_, err = redisClient.Ping(ctx).Result()
	if err != nil {
		cancel()
		return nil, fmt.Errorf("failed to connect to Redis: %w", err)
	}
	
	pipeline := &IRCTCETLPipeline{
		ctx:         ctx,
		cancel:      cancel,
		db:          db,
		redisClient: redisClient,
		config:      config,
		
		// Initialize worker pools
		extractWorkers:   make(chan struct{}, config.WorkerCount),
		transformWorkers: make(chan struct{}, config.WorkerCount),
		loadWorkers:      make(chan struct{}, config.WorkerCount),
		
		// Initialize channels
		rawBookings:     make(chan *BookingRecord, ChannelBufferSize),
		enrichedBookings: make(chan *EnrichedBooking, ChannelBufferSize),
		processedResults: make(chan *ProcessingResult, 100),
	}
	
	pipeline.stats.StartTime = time.Now()
	
	log.Printf("🚀 IRCTC ETL Pipeline initialized successfully")
	log.Printf("✅ Workers: %d, Batch Size: %d, Cache TTL: %v", 
		config.WorkerCount, config.BatchSize, config.CacheExpiration)
	
	return pipeline, nil
}

// Start the ETL pipeline with all workers
func (p *IRCTCETLPipeline) Start() error {
	log.Printf("🔄 Starting IRCTC ETL Pipeline workers...")
	
	// Pre-load caches for better performance
	go p.preloadCaches()
	
	// Start extract workers
	for i := 0; i < p.config.WorkerCount; i++ {
		go p.extractWorker(i)
	}
	
	// Start transform workers
	for i := 0; i < p.config.WorkerCount; i++ {
		go p.transformWorker(i)
	}
	
	// Start load workers
	for i := 0; i < p.config.WorkerCount; i++ {
		go p.loadWorker(i)
	}
	
	// Start metrics collector
	if p.config.EnableMetrics {
		go p.metricsCollector()
	}
	
	// Start cache maintenance
	go p.cacheMaintenanceWorker()
	
	log.Printf("✅ All workers started successfully")
	return nil
}

// Pre-load frequently accessed data into caches
func (p *IRCTCETLPipeline) preloadCaches() {
	log.Printf("🔄 Pre-loading caches for optimal performance...")
	
	// Pre-load train information
	go p.preloadTrainCache()
	
	// Pre-load route information
	go p.preloadRouteCache()
	
	// Pre-load user profiles (top 10K users)
	go p.preloadUserCache()
	
	time.Sleep(10 * time.Second) // Allow cache loading to complete
	log.Printf("✅ Cache pre-loading completed")
}

// Pre-load train information from database
func (p *IRCTCETLPipeline) preloadTrainCache() {
	query := `
		SELECT train_number, train_name, type, max_speed_kmph, is_active
		FROM trains 
		WHERE is_active = true 
		ORDER BY train_number
		LIMIT 5000
	`
	
	rows, err := p.db.QueryContext(p.ctx, query)
	if err != nil {
		log.Printf("❌ Error preloading train cache: %v", err)
		return
	}
	defer rows.Close()
	
	count := 0
	for rows.Next() {
		var train TrainInfo
		err := rows.Scan(&train.TrainNumber, &train.TrainName, &train.Type, 
						 &train.MaxSpeed, &train.IsActive)
		if err != nil {
			log.Printf("❌ Error scanning train data: %v", err)
			continue
		}
		
		train.CachedAt = time.Now()
		p.trainCache.Store(train.TrainNumber, &train)
		count++
	}
	
	log.Printf("✅ Preloaded %d trains into cache", count)
}

// Pre-load route information
func (p *IRCTCETLPipeline) preloadRouteCache() {
	query := `
		SELECT from_station, to_station, distance_km, duration_minutes, daily_frequency
		FROM routes 
		WHERE is_active = true 
		ORDER BY from_station, to_station
		LIMIT 10000
	`
	
	rows, err := p.db.QueryContext(p.ctx, query)
	if err != nil {
		log.Printf("❌ Error preloading route cache: %v", err)
		return
	}
	defer rows.Close()
	
	count := 0
	for rows.Next() {
		var route RouteInfo
		err := rows.Scan(&route.FromStation, &route.ToStation, &route.Distance,
						 &route.Duration, &route.Frequency)
		if err != nil {
			log.Printf("❌ Error scanning route data: %v", err)
			continue
		}
		
		route.CachedAt = time.Now()
		routeKey := route.FromStation + "-" + route.ToStation
		p.routeCache.Store(routeKey, &route)
		count++
	}
	
	log.Printf("✅ Preloaded %d routes into cache", count)
}

// Pre-load user profiles
func (p *IRCTCETLPipeline) preloadUserCache() {
	query := `
		SELECT user_id, tier, total_bookings, last_booking_at, preferred_class, home_station
		FROM user_profiles 
		WHERE is_active = true 
		ORDER BY total_bookings DESC
		LIMIT 10000
	`
	
	rows, err := p.db.QueryContext(p.ctx, query)
	if err != nil {
		log.Printf("❌ Error preloading user cache: %v", err)
		return
	}
	defer rows.Close()
	
	count := 0
	for rows.Next() {
		var user UserProfile
		err := rows.Scan(&user.UserID, &user.Tier, &user.TotalBookings,
						 &user.LastBookingAt, &user.PreferredClass, &user.HomeStation)
		if err != nil {
			log.Printf("❌ Error scanning user data: %v", err)
			continue
		}
		
		user.CachedAt = time.Now()
		p.userCache.Store(user.UserID, &user)
		count++
	}
	
	log.Printf("✅ Preloaded %d users into cache", count)
}

// Extract worker - reads booking data from source
func (p *IRCTCETLPipeline) extractWorker(workerID int) {
	log.Printf("🔄 Extract worker %d started", workerID)
	
	for {
		select {
		case <-p.ctx.Done():
			log.Printf("🛑 Extract worker %d stopping", workerID)
			return
		case p.extractWorkers <- struct{}{}:
			// Process batch of bookings
			bookings, err := p.extractBookingBatch()
			if err != nil {
				log.Printf("❌ Extract worker %d error: %v", workerID, err)
				atomic.AddInt64(&p.stats.ErrorCount, 1)
				<-p.extractWorkers
				continue
			}
			
			// Send bookings to transform stage
			for _, booking := range bookings {
				select {
				case p.rawBookings <- booking:
				case <-p.ctx.Done():
					<-p.extractWorkers
					return
				}
			}
			
			atomic.AddInt64(&p.stats.ProcessedCount, int64(len(bookings)))
			<-p.extractWorkers
		}
	}
}

// Extract booking batch from database
func (p *IRCTCETLPipeline) extractBookingBatch() ([]*BookingRecord, error) {
	timer := prometheus.NewTimer(processingDuration.WithLabelValues("extract"))
	defer timer.ObserveDuration()
	
	query := `
		SELECT booking_id, user_id, train_number, from_station, to_station,
			   journey_date, booking_date, passenger_count, total_fare,
			   class, status, payment_mode
		FROM bookings
		WHERE processed_at IS NULL
		ORDER BY booking_date
		LIMIT $1
	`
	
	rows, err := p.db.QueryContext(p.ctx, query, p.config.BatchSize)
	if err != nil {
		return nil, fmt.Errorf("failed to extract bookings: %w", err)
	}
	defer rows.Close()
	
	var bookings []*BookingRecord
	
	for rows.Next() {
		booking := &BookingRecord{}
		err := rows.Scan(
			&booking.BookingID, &booking.UserID, &booking.TrainNumber,
			&booking.FromStation, &booking.ToStation, &booking.JourneyDate,
			&booking.BookingDate, &booking.PassengerCount, &booking.TotalFare,
			&booking.Class, &booking.Status, &booking.PaymentMode,
		)
		if err != nil {
			log.Printf("❌ Error scanning booking: %v", err)
			continue
		}
		
		bookings = append(bookings, booking)
	}
	
	return bookings, nil
}

// Transform worker - enriches booking data
func (p *IRCTCETLPipeline) transformWorker(workerID int) {
	log.Printf("🔄 Transform worker %d started", workerID)
	
	for {
		select {
		case <-p.ctx.Done():
			log.Printf("🛑 Transform worker %d stopping", workerID)
			return
		case booking := <-p.rawBookings:
			if booking == nil {
				continue
			}
			
			// Get enriched booking from pool to reduce GC pressure
			enriched := bookingPool.Get().(*EnrichedBooking)
			
			// Transform booking data
			err := p.transformBooking(booking, enriched)
			if err != nil {
				log.Printf("❌ Transform worker %d error for booking %s: %v", 
					workerID, booking.BookingID, err)
				atomic.AddInt64(&p.stats.ErrorCount, 1)
				
				// Return object to pool
				p.resetEnrichedBooking(enriched)
				bookingPool.Put(enriched)
				continue
			}
			
			// Send to load stage
			select {
			case p.enrichedBookings <- enriched:
			case <-p.ctx.Done():
				p.resetEnrichedBooking(enriched)
				bookingPool.Put(enriched)
				return
			}
		}
	}
}

// Transform single booking with enrichment
func (p *IRCTCETLPipeline) transformBooking(booking *BookingRecord, enriched *EnrichedBooking) error {
	timer := prometheus.NewTimer(processingDuration.WithLabelValues("transform"))
	defer timer.ObserveDuration()
	
	processStart := time.Now()
	
	// Reset enriched booking
	p.resetEnrichedBooking(enriched)
	enriched.BookingRecord = booking
	
	// Get train information
	trainInfo, err := p.getTrainInfo(booking.TrainNumber)
	if err != nil {
		log.Printf("⚠️ Failed to get train info for %s: %v", booking.TrainNumber, err)
		enriched.TrainName = "Unknown Train"
	} else {
		enriched.TrainName = trainInfo.TrainName
	}
	
	// Get route information
	routeInfo, err := p.getRouteInfo(booking.FromStation, booking.ToStation)
	if err != nil {
		log.Printf("⚠️ Failed to get route info: %v", err)
		enriched.RouteDistance = 0
	} else {
		enriched.RouteDistance = routeInfo.Distance
	}
	
	// Get user profile
	userProfile, err := p.getUserProfile(booking.UserID)
	if err != nil {
		log.Printf("⚠️ Failed to get user profile for %s: %v", booking.UserID, err)
		enriched.UserTier = "GENERAL"
	} else {
		enriched.UserTier = userProfile.Tier
	}
	
	// Calculate booking score
	enriched.BookingScore = p.calculateBookingScore(booking, trainInfo, routeInfo, userProfile)
	
	// Set processing metadata
	enriched.ProcessedAt = time.Now()
	enriched.ProcessingTimeMs = time.Since(processStart).Milliseconds()
	
	processedBookingsTotal.WithLabelValues("success").Inc()
	return nil
}

// Get train information with caching
func (p *IRCTCETLPipeline) getTrainInfo(trainNumber string) (*TrainInfo, error) {
	// Check local cache first
	if cached, ok := p.trainCache.Load(trainNumber); ok {
		train := cached.(*TrainInfo)
		if time.Since(train.CachedAt) < p.config.CacheExpiration {
			atomic.AddInt64(&p.stats.CacheHits, 1)
			return train, nil
		}
	}
	
	// Check Redis cache
	cacheKey := fmt.Sprintf("train:%s", trainNumber)
	cached, err := p.redisClient.Get(p.ctx, cacheKey).Result()
	if err == nil {
		var train TrainInfo
		if json.Unmarshal([]byte(cached), &train) == nil {
			p.trainCache.Store(trainNumber, &train)
			atomic.AddInt64(&p.stats.CacheHits, 1)
			return &train, nil
		}
	}
	
	// Load from database
	atomic.AddInt64(&p.stats.CacheMisses, 1)
	train, err := p.loadTrainFromDB(trainNumber)
	if err != nil {
		return nil, err
	}
	
	// Cache in both local and Redis
	p.trainCache.Store(trainNumber, train)
	if trainData, err := json.Marshal(train); err == nil {
		p.redisClient.SetEX(p.ctx, cacheKey, trainData, p.config.CacheExpiration)
	}
	
	return train, nil
}

// Load train information from database
func (p *IRCTCETLPipeline) loadTrainFromDB(trainNumber string) (*TrainInfo, error) {
	query := `
		SELECT train_number, train_name, type, max_speed_kmph, is_active
		FROM trains 
		WHERE train_number = $1 AND is_active = true
	`
	
	row := p.db.QueryRowContext(p.ctx, query, trainNumber)
	
	var train TrainInfo
	err := row.Scan(&train.TrainNumber, &train.TrainName, &train.Type,
					&train.MaxSpeed, &train.IsActive)
	if err != nil {
		return nil, fmt.Errorf("failed to load train %s: %w", trainNumber, err)
	}
	
	train.CachedAt = time.Now()
	return &train, nil
}

// Get route information with caching
func (p *IRCTCETLPipeline) getRouteInfo(fromStation, toStation string) (*RouteInfo, error) {
	routeKey := fromStation + "-" + toStation
	
	// Check local cache
	if cached, ok := p.routeCache.Load(routeKey); ok {
		route := cached.(*RouteInfo)
		if time.Since(route.CachedAt) < p.config.CacheExpiration {
			atomic.AddInt64(&p.stats.CacheHits, 1)
			return route, nil
		}
	}
	
	// Check Redis cache
	cacheKey := fmt.Sprintf("route:%s", routeKey)
	cached, err := p.redisClient.Get(p.ctx, cacheKey).Result()
	if err == nil {
		var route RouteInfo
		if json.Unmarshal([]byte(cached), &route) == nil {
			p.routeCache.Store(routeKey, &route)
			atomic.AddInt64(&p.stats.CacheHits, 1)
			return &route, nil
		}
	}
	
	// Load from database
	atomic.AddInt64(&p.stats.CacheMisses, 1)
	route, err := p.loadRouteFromDB(fromStation, toStation)
	if err != nil {
		return nil, err
	}
	
	// Cache in both local and Redis
	p.routeCache.Store(routeKey, route)
	if routeData, err := json.Marshal(route); err == nil {
		p.redisClient.SetEX(p.ctx, cacheKey, routeData, p.config.CacheExpiration)
	}
	
	return route, nil
}

// Load route from database
func (p *IRCTCETLPipeline) loadRouteFromDB(fromStation, toStation string) (*RouteInfo, error) {
	query := `
		SELECT from_station, to_station, distance_km, duration_minutes, daily_frequency
		FROM routes
		WHERE from_station = $1 AND to_station = $2 AND is_active = true
	`
	
	row := p.db.QueryRowContext(p.ctx, query, fromStation, toStation)
	
	var route RouteInfo
	err := row.Scan(&route.FromStation, &route.ToStation, &route.Distance,
					&route.Duration, &route.Frequency)
	if err != nil {
		return nil, fmt.Errorf("failed to load route %s-%s: %w", fromStation, toStation, err)
	}
	
	route.CachedAt = time.Now()
	return &route, nil
}

// Get user profile with caching
func (p *IRCTCETLPipeline) getUserProfile(userID string) (*UserProfile, error) {
	// Check local cache
	if cached, ok := p.userCache.Load(userID); ok {
		user := cached.(*UserProfile)
		if time.Since(user.CachedAt) < p.config.CacheExpiration {
			atomic.AddInt64(&p.stats.CacheHits, 1)
			return user, nil
		}
	}
	
	// Check Redis cache
	cacheKey := fmt.Sprintf("user:%s", userID)
	cached, err := p.redisClient.Get(p.ctx, cacheKey).Result()
	if err == nil {
		var user UserProfile
		if json.Unmarshal([]byte(cached), &user) == nil {
			p.userCache.Store(userID, &user)
			atomic.AddInt64(&p.stats.CacheHits, 1)
			return &user, nil
		}
	}
	
	// Load from database
	atomic.AddInt64(&p.stats.CacheMisses, 1)
	user, err := p.loadUserFromDB(userID)
	if err != nil {
		return nil, err
	}
	
	// Cache in both local and Redis
	p.userCache.Store(userID, user)
	if userData, err := json.Marshal(user); err == nil {
		p.redisClient.SetEX(p.ctx, cacheKey, userData, p.config.CacheExpiration)
	}
	
	return user, nil
}

// Load user profile from database
func (p *IRCTCETLPipeline) loadUserFromDB(userID string) (*UserProfile, error) {
	query := `
		SELECT user_id, tier, total_bookings, last_booking_at, preferred_class, home_station
		FROM user_profiles
		WHERE user_id = $1 AND is_active = true
	`
	
	row := p.db.QueryRowContext(p.ctx, query, userID)
	
	var user UserProfile
	err := row.Scan(&user.UserID, &user.Tier, &user.TotalBookings,
					&user.LastBookingAt, &user.PreferredClass, &user.HomeStation)
	if err != nil {
		return nil, fmt.Errorf("failed to load user %s: %w", userID, err)
	}
	
	user.CachedAt = time.Now()
	return &user, nil
}

// Calculate booking score based on various factors
func (p *IRCTCETLPipeline) calculateBookingScore(booking *BookingRecord, 
	train *TrainInfo, route *RouteInfo, user *UserProfile) float64 {
	
	score := 100.0
	
	// High-value booking adjustment
	if booking.TotalFare > 5000 {
		score += 10
	}
	
	// Multiple passenger adjustment
	if booking.PassengerCount > 4 {
		score += 5
	}
	
	// Premium class bonus
	if booking.Class == "1AC" || booking.Class == "2AC" {
		score += 15
	}
	
	// User tier bonus
	if user != nil {
		switch user.Tier {
		case "VIP":
			score += 20
		case "PREMIUM":
			score += 10
		}
	}
	
	// Train type bonus
	if train != nil {
		switch train.Type {
		case "Rajdhani":
			score += 25
		case "Shatabdi":
			score += 20
		case "Duronto":
			score += 15
		case "Superfast":
			score += 10
		}
	}
	
	// Long distance bonus
	if route != nil && route.Distance > 1000 {
		score += 10
	}
	
	// Advance booking bonus (more than 30 days in advance)
	if booking.JourneyDate.Sub(booking.BookingDate).Hours() > 720 { // 30 days
		score += 5
	}
	
	// Peak season adjustment (Indian festivals, holidays)
	month := booking.JourneyDate.Month()
	if month == time.October || month == time.November || month == time.April || month == time.May {
		score += 5
	}
	
	return score
}

// Load worker - saves enriched bookings to target
func (p *IRCTCETLPipeline) loadWorker(workerID int) {
	log.Printf("🔄 Load worker %d started", workerID)
	
	for {
		select {
		case <-p.ctx.Done():
			log.Printf("🛑 Load worker %d stopping", workerID)
			return
		case enriched := <-p.enrichedBookings:
			if enriched == nil {
				continue
			}
			
			err := p.loadEnrichedBooking(enriched)
			if err != nil {
				log.Printf("❌ Load worker %d error for booking %s: %v", 
					workerID, enriched.BookingID, err)
				atomic.AddInt64(&p.stats.ErrorCount, 1)
			} else {
				processedBookingsTotal.WithLabelValues("loaded").Inc()
			}
			
			// Return object to pool
			p.resetEnrichedBooking(enriched)
			bookingPool.Put(enriched)
		}
	}
}

// Load enriched booking to target database
func (p *IRCTCETLPipeline) loadEnrichedBooking(enriched *EnrichedBooking) error {
	timer := prometheus.NewTimer(processingDuration.WithLabelValues("load"))
	defer timer.ObserveDuration()
	
	query := `
		INSERT INTO enriched_bookings (
			booking_id, user_id, train_number, train_name, from_station, to_station,
			journey_date, booking_date, passenger_count, total_fare, class, status,
			payment_mode, route_distance_km, user_tier, booking_score,
			processed_at, processing_time_ms, created_at
		) VALUES (
			$1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, NOW()
		) ON CONFLICT (booking_id) DO UPDATE SET
			train_name = EXCLUDED.train_name,
			route_distance_km = EXCLUDED.route_distance_km,
			user_tier = EXCLUDED.user_tier,
			booking_score = EXCLUDED.booking_score,
			processed_at = EXCLUDED.processed_at,
			processing_time_ms = EXCLUDED.processing_time_ms,
			updated_at = NOW()
	`
	
	_, err := p.db.ExecContext(p.ctx, query,
		enriched.BookingID, enriched.UserID, enriched.TrainNumber, enriched.TrainName,
		enriched.FromStation, enriched.ToStation, enriched.JourneyDate, enriched.BookingDate,
		enriched.PassengerCount, enriched.TotalFare, enriched.Class, enriched.Status,
		enriched.PaymentMode, enriched.RouteDistance, enriched.UserTier, enriched.BookingScore,
		enriched.ProcessedAt, enriched.ProcessingTimeMs,
	)
	
	if err != nil {
		return fmt.Errorf("failed to load booking %s: %w", enriched.BookingID, err)
	}
	
	// Mark original booking as processed
	updateQuery := `UPDATE bookings SET processed_at = NOW() WHERE booking_id = $1`
	_, err = p.db.ExecContext(p.ctx, updateQuery, enriched.BookingID)
	if err != nil {
		log.Printf("⚠️ Failed to mark booking %s as processed: %v", enriched.BookingID, err)
	}
	
	return nil
}

// Reset enriched booking object for reuse
func (p *IRCTCETLPipeline) resetEnrichedBooking(enriched *EnrichedBooking) {
	enriched.BookingRecord = nil
	enriched.TrainName = ""
	enriched.RouteDistance = 0
	enriched.UserTier = ""
	enriched.BookingScore = 0
	enriched.ProcessedAt = time.Time{}
	enriched.ProcessingTimeMs = 0
}

// Cache maintenance worker - cleans expired cache entries
func (p *IRCTCETLPipeline) cacheMaintenanceWorker() {
	ticker := time.NewTicker(5 * time.Minute)
	defer ticker.Stop()
	
	for {
		select {
		case <-p.ctx.Done():
			log.Printf("🛑 Cache maintenance worker stopping")
			return
		case <-ticker.C:
			p.cleanExpiredCache()
		}
	}
}

// Clean expired cache entries
func (p *IRCTCETLPipeline) cleanExpiredCache() {
	now := time.Now()
	
	// Clean train cache
	p.trainCache.Range(func(key, value interface{}) bool {
		train := value.(*TrainInfo)
		if now.Sub(train.CachedAt) > p.config.CacheExpiration {
			p.trainCache.Delete(key)
		}
		return true
	})
	
	// Clean route cache
	p.routeCache.Range(func(key, value interface{}) bool {
		route := value.(*RouteInfo)
		if now.Sub(route.CachedAt) > p.config.CacheExpiration {
			p.routeCache.Delete(key)
		}
		return true
	})
	
	// Clean user cache
	p.userCache.Range(func(key, value interface{}) bool {
		user := value.(*UserProfile)
		if now.Sub(user.CachedAt) > p.config.CacheExpiration {
			p.userCache.Delete(key)
		}
		return true
	})
}

// Metrics collector for performance monitoring
func (p *IRCTCETLPipeline) metricsCollector() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-p.ctx.Done():
			return
		case <-ticker.C:
			// Update cache hit rate metrics
			totalRequests := atomic.LoadInt64(&p.stats.CacheHits) + atomic.LoadInt64(&p.stats.CacheMisses)
			if totalRequests > 0 {
				hitRate := float64(atomic.LoadInt64(&p.stats.CacheHits)) / float64(totalRequests) * 100
				cacheHitRate.WithLabelValues("overall").Set(hitRate)
			}
		}
	}
}

// Get processing statistics
func (p *IRCTCETLPipeline) GetStats() ProcessingResult {
	runtime := time.Since(p.stats.StartTime)
	processedCount := atomic.LoadInt64(&p.stats.ProcessedCount)
	
	var throughput float64
	if runtime.Seconds() > 0 {
		throughput = float64(processedCount) / runtime.Seconds()
	}
	
	return ProcessingResult{
		ProcessedRecords: processedCount,
		SuccessCount:     processedCount - atomic.LoadInt64(&p.stats.ErrorCount),
		ErrorCount:       atomic.LoadInt64(&p.stats.ErrorCount),
		ProcessingTime:   runtime,
		Throughput:       throughput,
	}
}

// Process bookings for a specific date range
func (p *IRCTCETLPipeline) ProcessBookingsForDateRange(startDate, endDate time.Time) (*ProcessingResult, error) {
	log.Printf("📊 Processing bookings from %v to %v", startDate.Format("2006-01-02"), endDate.Format("2006-01-02"))
	
	ctx, cancel := context.WithTimeout(p.ctx, p.config.ProcessingTimeout)
	defer cancel()
	
	// Update query to filter by date range
	query := `
		SELECT booking_id, user_id, train_number, from_station, to_station,
			   journey_date, booking_date, passenger_count, total_fare,
			   class, status, payment_mode
		FROM bookings
		WHERE booking_date >= $1 AND booking_date <= $2 
		  AND processed_at IS NULL
		ORDER BY booking_date
		LIMIT $3
	`
	
	rows, err := p.db.QueryContext(ctx, query, startDate, endDate, p.config.BatchSize)
	if err != nil {
		return nil, fmt.Errorf("failed to query bookings: %w", err)
	}
	defer rows.Close()
	
	var bookings []*BookingRecord
	for rows.Next() {
		booking := &BookingRecord{}
		err := rows.Scan(
			&booking.BookingID, &booking.UserID, &booking.TrainNumber,
			&booking.FromStation, &booking.ToStation, &booking.JourneyDate,
			&booking.BookingDate, &booking.PassengerCount, &booking.TotalFare,
			&booking.Class, &booking.Status, &booking.PaymentMode,
		)
		if err != nil {
			log.Printf("❌ Error scanning booking: %v", err)
			continue
		}
		bookings = append(bookings, booking)
	}
	
	if len(bookings) == 0 {
		log.Printf("ℹ️ No bookings found for processing")
		return &ProcessingResult{}, nil
	}
	
	log.Printf("🔄 Processing %d bookings...", len(bookings))
	
	// Process bookings through the pipeline
	for _, booking := range bookings {
		select {
		case p.rawBookings <- booking:
		case <-ctx.Done():
			return nil, fmt.Errorf("processing timeout")
		}
	}
	
	// Wait a bit for processing to complete
	time.Sleep(5 * time.Second)
	
	stats := p.GetStats()
	return &stats, nil
}

// Graceful shutdown
func (p *IRCTCETLPipeline) Shutdown() error {
	log.Printf("🛑 Shutting down IRCTC ETL Pipeline...")
	
	// Cancel context to stop all workers
	p.cancel()
	
	// Close channels
	close(p.rawBookings)
	close(p.enrichedBookings)
	close(p.processedResults)
	
	// Close database connection
	if p.db != nil {
		p.db.Close()
	}
	
	// Close Redis connection
	if p.redisClient != nil {
		p.redisClient.Close()
	}
	
	log.Printf("✅ IRCTC ETL Pipeline shutdown completed")
	return nil
}

// Create sample booking data for testing
func createSampleBookings(count int) []*BookingRecord {
	bookings := make([]*BookingRecord, count)
	
	stations := []string{"NDLS", "CSMT", "MAS", "SBC", "HWH", "PUNE", "AGC", "JUC"}
	classes := []string{"SL", "3AC", "2AC", "1AC", "CC"}
	statuses := []string{"CONFIRMED", "RAC", "WL"}
	paymentModes := []string{"DEBIT_CARD", "CREDIT_CARD", "UPI", "NET_BANKING", "WALLET"}
	
	for i := 0; i < count; i++ {
		bookings[i] = &BookingRecord{
			BookingID:      fmt.Sprintf("PNR%010d", rand.Intn(10000000000)),
			UserID:         fmt.Sprintf("USER_%06d", rand.Intn(1000000)),
			TrainNumber:    fmt.Sprintf("%05d", rand.Intn(99999)+10000),
			FromStation:    stations[rand.Intn(len(stations))],
			ToStation:      stations[rand.Intn(len(stations))],
			JourneyDate:    time.Now().AddDate(0, 0, rand.Intn(60)+1), // Next 60 days
			BookingDate:    time.Now().AddDate(0, 0, -rand.Intn(30)),  // Last 30 days
			PassengerCount: rand.Intn(6) + 1,                          // 1-6 passengers
			TotalFare:      float64(rand.Intn(5000) + 200),           // ₹200-5200
			Class:          classes[rand.Intn(len(classes))],
			Status:         statuses[rand.Intn(len(statuses))],
			PaymentMode:    paymentModes[rand.Intn(len(paymentModes))],
		}
	}
	
	return bookings
}

// Main function - demonstration of IRCTC ETL Pipeline
func main() {
	log.Printf("🚀 Starting IRCTC High Performance ETL Pipeline")
	log.Printf("यह Go में production-ready ETL pipeline है जो IRCTC scale handle करता है")
	
	// Configuration
	config := &ETLConfig{
		DatabaseURL:       "postgres://irctc:railway2024@localhost/irctc_bookings?sslmode=disable",
		RedisURL:          "redis://localhost:6379/0",
		BatchSize:         BatchSize,
		WorkerCount:       WorkerPoolSize,
		ProcessingTimeout: ProcessingTimeout * time.Second,
		CacheExpiration:   CacheExpiration * time.Second,
		EnableMetrics:     true,
		LogLevel:          "INFO",
	}
	
	// Initialize pipeline
	pipeline, err := NewIRCTCETLPipeline(config)
	if err != nil {
		log.Fatalf("❌ Failed to initialize pipeline: %v", err)
	}
	
	// Set up graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	
	// Start pipeline
	if err := pipeline.Start(); err != nil {
		log.Fatalf("❌ Failed to start pipeline: %v", err)
	}
	
	// For demonstration, create and process sample data
	log.Printf("📝 Creating sample booking data for demonstration...")
	sampleBookings := createSampleBookings(1000)
	
	// Send sample bookings to pipeline
	go func() {
		for _, booking := range sampleBookings {
			select {
			case pipeline.rawBookings <- booking:
			case <-pipeline.ctx.Done():
				return
			}
		}
	}()
	
	// Display performance stats periodically
	statsTicker := time.NewTicker(10 * time.Second)
	defer statsTicker.Stop()
	
	go func() {
		for {
			select {
			case <-statsTicker.C:
				stats := pipeline.GetStats()
				log.Printf("📊 Stats: Processed=%d, Errors=%d, Throughput=%.2f/sec, Runtime=%v",
					stats.ProcessedRecords, stats.ErrorCount, stats.Throughput, stats.ProcessingTime)
			case <-pipeline.ctx.Done():
				return
			}
		}
	}()
	
	// Wait for shutdown signal
	<-sigChan
	log.Printf("🛑 Received shutdown signal")
	
	// Get final stats
	finalStats := pipeline.GetStats()
	
	// Shutdown pipeline
	pipeline.Shutdown()
	
	// Display final results
	fmt.Printf("\n" + strings.Repeat("=", 80) + "\n")
	fmt.Printf("🎯 IRCTC ETL PIPELINE FINAL RESULTS\n")
	fmt.Printf(strings.Repeat("=", 80) + "\n")
	fmt.Printf("Total Processing Time: %v\n", finalStats.ProcessingTime)
	fmt.Printf("Total Processed Records: %d\n", finalStats.ProcessedRecords)
	fmt.Printf("Successful Records: %d\n", finalStats.SuccessCount)
	fmt.Printf("Failed Records: %d\n", finalStats.ErrorCount)
	fmt.Printf("Average Throughput: %.2f bookings/second\n", finalStats.Throughput)
	
	if finalStats.ProcessedRecords > 0 {
		successRate := float64(finalStats.SuccessCount) / float64(finalStats.ProcessedRecords) * 100
		fmt.Printf("Success Rate: %.2f%%\n", successRate)
	}
	
	// Memory stats
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	fmt.Printf("\n🧠 MEMORY USAGE:\n")
	fmt.Printf("  • Allocated: %d MB\n", m.Alloc/1024/1024)
	fmt.Printf("  • Total Allocated: %d MB\n", m.TotalAlloc/1024/1024)
	fmt.Printf("  • System: %d MB\n", m.Sys/1024/1024)
	fmt.Printf("  • GC Cycles: %d\n", m.NumGC)
	
	fmt.Printf("\n✅ IRCTC ETL Pipeline completed successfully!\n")
	fmt.Printf("यह production-grade Go ETL pipeline IRCTC scale handle कर सकता है।\n")
	fmt.Printf("Key Features: Goroutine pools, Channel communication, Multi-level caching, Metrics\n")
}
/*
Advanced ETL Pipeline for IRCTC Booking Analytics
Focus: Concurrent processing, memory efficiency, high throughput

Ye Go implementation Mumbai local train ke schedule jaise
precise aur efficient hai!

Production Ready: Yes
Testing Required: Yes  
Performance: Optimized for millions of bookings
*/

package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"runtime"
	"sync"
	"time"
	"os"
	"os/signal"
	"syscall"
	"math"
	"sort"
	"strconv"
	"strings"
	
	"github.com/go-redis/redis/v8"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/segmentio/kafka-go"
	_ "github.com/lib/pq"
)

// Configuration for IRCTC ETL Pipeline
type ETLConfig struct {
	DatabaseURL      string        `json:"database_url"`
	RedisAddr        string        `json:"redis_addr"`
	KafkaBrokers     []string      `json:"kafka_brokers"`
	BatchSize        int           `json:"batch_size"`
	WorkerCount      int           `json:"worker_count"`
	ProcessingDelay  time.Duration `json:"processing_delay"`
	CacheTTL         time.Duration `json:"cache_ttl"`
	MetricsPort      string        `json:"metrics_port"`
}

// IRCTC Booking record structure
type BookingRecord struct {
	BookingID       string    `json:"booking_id"`
	UserID          string    `json:"user_id"`
	TrainNo         string    `json:"train_no"`
	FromStation     string    `json:"from_station"`
	ToStation       string    `json:"to_station"`
	JourneyDate     time.Time `json:"journey_date"`
	BookingDate     time.Time `json:"booking_date"`
	PassengerCount  int       `json:"passenger_count"`
	TotalFare       float64   `json:"total_fare"`
	PaymentStatus   string    `json:"payment_status"`
	BookingStatus   string    `json:"booking_status"`
	ClassType       string    `json:"class_type"`
	QuotaType       string    `json:"quota_type"`
	TatkalFlag      bool      `json:"tatkal_flag"`
	SeniorCitizen   bool      `json:"senior_citizen_flag"`
}

// Enriched booking record with analytics
type EnrichedBooking struct {
	BookingRecord
	TrainName        string  `json:"train_name"`
	DistanceKM       int     `json:"distance_km"`
	RoutePopularity  int     `json:"route_popularity"`
	DemandScore      float64 `json:"demand_score"`
	RevenuePotential float64 `json:"revenue_potential"`
	UserSegment      string  `json:"user_segment"`
	ProcessedAt      time.Time `json:"processed_at"`
}

// Train information cache
type TrainInfo struct {
	TrainNo     string `json:"train_no"`
	TrainName   string `json:"train_name"`
	DistanceKM  int    `json:"distance_km"`
	Duration    int    `json:"duration_minutes"`
	TrainType   string `json:"train_type"`
	Zone        string `json:"zone"`
}

// User profile cache  
type UserProfile struct {
	UserID           string  `json:"user_id"`
	Segment          string  `json:"segment"`
	BookingFrequency int     `json:"booking_frequency"`
	AvgFare          float64 `json:"avg_fare"`
	PreferredClass   string  `json:"preferred_class"`
	LastBookingDate  time.Time `json:"last_booking_date"`
}

// Route analytics
type RouteAnalytics struct {
	Route           string  `json:"route"`
	DailyBookings   int     `json:"daily_bookings"`
	AvgFare         float64 `json:"avg_fare"`
	PopularityScore int     `json:"popularity_score"`
	RevenueShare    float64 `json:"revenue_share"`
}

// Performance metrics
var (
	processedRecords = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "irctc_etl_processed_records_total",
			Help: "Total number of processed booking records",
		},
		[]string{"status"},
	)
	
	processingDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "irctc_etl_processing_duration_seconds",
			Help: "Duration of batch processing",
		},
		[]string{"operation"},
	)
	
	cacheHitRate = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "irctc_etl_cache_hits_total",
			Help: "Number of cache hits",
		},
		[]string{"cache_type"},
	)
	
	currentGoroutines = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "irctc_etl_goroutines_active",
			Help: "Number of active goroutines",
		},
	)
	
	memoryUsage = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "irctc_etl_memory_usage_bytes",
			Help: "Current memory usage in bytes",
		},
	)
)

// Main ETL Pipeline struct
type IRCTCETLPipeline struct {
	config        *ETLConfig
	db            *pgxpool.Pool
	redis         *redis.Client
	kafkaReader   *kafka.Reader
	kafkaWriter   *kafka.Writer
	trainCache    map[string]*TrainInfo
	userCache     map[string]*UserProfile
	routeCache    map[string]*RouteAnalytics
	cacheMutex    sync.RWMutex
	shutdown      chan os.Signal
	ctx           context.Context
	cancel        context.CancelFunc
	wg            sync.WaitGroup
}

// Initialize ETL Pipeline
func NewIRCTCETLPipeline(config *ETLConfig) (*IRCTCETLPipeline, error) {
	log.Println("🚀 Initializing IRCTC ETL Pipeline...")
	
	ctx, cancel := context.WithCancel(context.Background())
	
	pipeline := &IRCTCETLPipeline{
		config:     config,
		trainCache: make(map[string]*TrainInfo),
		userCache:  make(map[string]*UserProfile),
		routeCache: make(map[string]*RouteAnalytics),
		shutdown:   make(chan os.Signal, 1),
		ctx:        ctx,
		cancel:     cancel,
	}
	
	// Initialize database connection
	if err := pipeline.initDatabase(); err != nil {
		return nil, fmt.Errorf("failed to initialize database: %w", err)
	}
	
	// Initialize Redis
	if err := pipeline.initRedis(); err != nil {
		return nil, fmt.Errorf("failed to initialize Redis: %w", err)
	}
	
	// Initialize Kafka
	if err := pipeline.initKafka(); err != nil {
		return nil, fmt.Errorf("failed to initialize Kafka: %w", err)
	}
	
	// Load initial cache data
	if err := pipeline.warmupCaches(); err != nil {
		log.Printf("⚠️ Warning: Cache warmup failed: %v", err)
	}
	
	log.Println("✅ IRCTC ETL Pipeline initialized successfully!")
	return pipeline, nil
}

// Initialize database connection pool
func (p *IRCTCETLPipeline) initDatabase() error {
	log.Println("🔌 Connecting to PostgreSQL database...")
	
	config, err := pgxpool.ParseConfig(p.config.DatabaseURL)
	if err != nil {
		return err
	}
	
	// Optimize connection pool for high throughput
	config.MaxConns = int32(runtime.NumCPU() * 4)
	config.MinConns = int32(runtime.NumCPU())
	config.MaxConnLifetime = time.Hour
	config.MaxConnIdleTime = time.Minute * 30
	
	p.db, err = pgxpool.ConnectConfig(p.ctx, config)
	if err != nil {
		return err
	}
	
	// Test connection
	if err := p.db.Ping(p.ctx); err != nil {
		return err
	}
	
	log.Println("✅ Database connection established!")
	return nil
}

// Initialize Redis client
func (p *IRCTCETLPipeline) initRedis() error {
	log.Println("🔴 Connecting to Redis cache...")
	
	p.redis = redis.NewClient(&redis.Options{
		Addr:         p.config.RedisAddr,
		DB:           0,
		PoolSize:     runtime.NumCPU() * 2,
		MinIdleConns: runtime.NumCPU(),
		MaxRetries:   3,
		ReadTimeout:  time.Second * 3,
		WriteTimeout: time.Second * 3,
	})
	
	// Test Redis connection
	_, err := p.redis.Ping(p.ctx).Result()
	if err != nil {
		return err
	}
	
	log.Println("✅ Redis connection established!")
	return nil
}

// Initialize Kafka reader and writer
func (p *IRCTCETLPipeline) initKafka() error {
	log.Println("📡 Connecting to Kafka brokers...")
	
	// Kafka reader for incoming bookings
	p.kafkaReader = kafka.NewReader(kafka.ReaderConfig{
		Brokers:     p.config.KafkaBrokers,
		Topic:       "irctc-bookings",
		GroupID:     "irctc-etl-processor",
		StartOffset: kafka.LastOffset,
		MinBytes:    10e3, // 10KB
		MaxBytes:    10e6, // 10MB
	})
	
	// Kafka writer for processed data
	p.kafkaWriter = &kafka.Writer{
		Addr:     kafka.TCP(p.config.KafkaBrokers...),
		Topic:    "irctc-analytics",
		Balancer: &kafka.LeastBytes{},
	}
	
	log.Println("✅ Kafka connections established!")
	return nil
}

// Warmup caches with frequently accessed data
func (p *IRCTCETLPipeline) warmupCaches() error {
	log.Println("🔥 Warming up caches...")
	
	// Load popular trains
	if err := p.loadTrainCache(); err != nil {
		return fmt.Errorf("failed to load train cache: %w", err)
	}
	
	// Load active user profiles
	if err := p.loadUserCache(); err != nil {
		return fmt.Errorf("failed to load user cache: %w", err)
	}
	
	// Load route analytics
	if err := p.loadRouteCache(); err != nil {
		return fmt.Errorf("failed to load route cache: %w", err)
	}
	
	log.Printf("✅ Cache warmup completed! Trains: %d, Users: %d, Routes: %d",
		len(p.trainCache), len(p.userCache), len(p.routeCache))
	
	return nil
}

// Load train information into cache
func (p *IRCTCETLPipeline) loadTrainCache() error {
	query := `
		SELECT train_no, train_name, distance_km, duration_minutes, train_type, zone
		FROM train_schedules 
		WHERE status = 'ACTIVE' 
		ORDER BY popularity_score DESC 
		LIMIT 1000
	`
	
	rows, err := p.db.Query(p.ctx, query)
	if err != nil {
		return err
	}
	defer rows.Close()
	
	p.cacheMutex.Lock()
	defer p.cacheMutex.Unlock()
	
	for rows.Next() {
		var train TrainInfo
		err := rows.Scan(
			&train.TrainNo, &train.TrainName, &train.DistanceKM,
			&train.Duration, &train.TrainType, &train.Zone,
		)
		if err != nil {
			continue
		}
		
		p.trainCache[train.TrainNo] = &train
	}
	
	return nil
}

// Load user profiles into cache
func (p *IRCTCETLPipeline) loadUserCache() error {
	query := `
		SELECT user_id, segment, booking_frequency, avg_fare, preferred_class, last_booking_date
		FROM user_profiles 
		WHERE last_booking_date >= NOW() - INTERVAL '30 days'
		ORDER BY booking_frequency DESC 
		LIMIT 10000
	`
	
	rows, err := p.db.Query(p.ctx, query)
	if err != nil {
		return err
	}
	defer rows.Close()
	
	p.cacheMutex.Lock()
	defer p.cacheMutex.Unlock()
	
	for rows.Next() {
		var user UserProfile
		err := rows.Scan(
			&user.UserID, &user.Segment, &user.BookingFrequency,
			&user.AvgFare, &user.PreferredClass, &user.LastBookingDate,
		)
		if err != nil {
			continue
		}
		
		p.userCache[user.UserID] = &user
	}
	
	return nil
}

// Load route analytics into cache
func (p *IRCTCETLPipeline) loadRouteCache() error {
	query := `
		SELECT route, daily_bookings, avg_fare, popularity_score, revenue_share
		FROM route_analytics 
		WHERE last_updated >= CURRENT_DATE - 7
		ORDER BY popularity_score DESC 
		LIMIT 5000
	`
	
	rows, err := p.db.Query(p.ctx, query)
	if err != nil {
		return err
	}
	defer rows.Close()
	
	p.cacheMutex.Lock()
	defer p.cacheMutex.Unlock()
	
	for rows.Next() {
		var route RouteAnalytics
		err := rows.Scan(
			&route.Route, &route.DailyBookings, &route.AvgFare,
			&route.PopularityScore, &route.RevenueShare,
		)
		if err != nil {
			continue
		}
		
		p.routeCache[route.Route] = &route
	}
	
	return nil
}

// Get train info with caching
func (p *IRCTCETLPipeline) getTrainInfo(trainNo string) (*TrainInfo, error) {
	// Check local cache first
	p.cacheMutex.RLock()
	if train, exists := p.trainCache[trainNo]; exists {
		p.cacheMutex.RUnlock()
		cacheHitRate.WithLabelValues("train_local").Inc()
		return train, nil
	}
	p.cacheMutex.RUnlock()
	
	// Check Redis cache
	cacheKey := fmt.Sprintf("train:%s", trainNo)
	cached, err := p.redis.Get(p.ctx, cacheKey).Result()
	if err == nil {
		var train TrainInfo
		if json.Unmarshal([]byte(cached), &train) == nil {
			// Update local cache
			p.cacheMutex.Lock()
			p.trainCache[trainNo] = &train
			p.cacheMutex.Unlock()
			
			cacheHitRate.WithLabelValues("train_redis").Inc()
			return &train, nil
		}
	}
	
	// Load from database
	query := `
		SELECT train_no, train_name, distance_km, duration_minutes, train_type, zone
		FROM train_schedules 
		WHERE train_no = $1 AND status = 'ACTIVE'
	`
	
	var train TrainInfo
	err = p.db.QueryRow(p.ctx, query, trainNo).Scan(
		&train.TrainNo, &train.TrainName, &train.DistanceKM,
		&train.Duration, &train.TrainType, &train.Zone,
	)
	
	if err != nil {
		return nil, err
	}
	
	// Cache in both local and Redis
	p.cacheMutex.Lock()
	p.trainCache[trainNo] = &train
	p.cacheMutex.Unlock()
	
	// Cache in Redis with TTL
	trainJSON, _ := json.Marshal(train)
	p.redis.Set(p.ctx, cacheKey, trainJSON, p.config.CacheTTL)
	
	return &train, nil
}

// Get user profile with caching
func (p *IRCTCETLPipeline) getUserProfile(userID string) (*UserProfile, error) {
	// Check local cache
	p.cacheMutex.RLock()
	if user, exists := p.userCache[userID]; exists {
		p.cacheMutex.RUnlock()
		cacheHitRate.WithLabelValues("user_local").Inc()
		return user, nil
	}
	p.cacheMutex.RUnlock()
	
	// Check Redis cache
	cacheKey := fmt.Sprintf("user:%s", userID)
	cached, err := p.redis.Get(p.ctx, cacheKey).Result()
	if err == nil {
		var user UserProfile
		if json.Unmarshal([]byte(cached), &user) == nil {
			p.cacheMutex.Lock()
			p.userCache[userID] = &user
			p.cacheMutex.Unlock()
			
			cacheHitRate.WithLabelValues("user_redis").Inc()
			return &user, nil
		}
	}
	
	// Load from database
	query := `
		SELECT user_id, segment, booking_frequency, avg_fare, preferred_class, last_booking_date
		FROM user_profiles 
		WHERE user_id = $1
	`
	
	var user UserProfile
	err = p.db.QueryRow(p.ctx, query, userID).Scan(
		&user.UserID, &user.Segment, &user.BookingFrequency,
		&user.AvgFare, &user.PreferredClass, &user.LastBookingDate,
	)
	
	if err != nil {
		// Create default profile for new users
		user = UserProfile{
			UserID:           userID,
			Segment:          "NEW",
			BookingFrequency: 0,
			AvgFare:          0,
			PreferredClass:   "SL",
			LastBookingDate:  time.Now(),
		}
	}
	
	// Cache the result
	p.cacheMutex.Lock()
	p.userCache[userID] = &user
	p.cacheMutex.Unlock()
	
	userJSON, _ := json.Marshal(user)
	p.redis.Set(p.ctx, cacheKey, userJSON, p.config.CacheTTL)
	
	return &user, nil
}

// Calculate demand score based on multiple factors
func (p *IRCTCETLPipeline) calculateDemandScore(booking *BookingRecord, train *TrainInfo) float64 {
	score := 50.0 // Base score
	
	// Tatkal booking indicates high demand
	if booking.TatkalFlag {
		score += 30
	}
	
	// Weekend travel (higher demand)
	if booking.JourneyDate.Weekday() == time.Saturday || booking.JourneyDate.Weekday() == time.Sunday {
		score += 15
	}
	
	// High-value booking
	if booking.TotalFare > 2000 {
		score += 20
	}
	
	// Multiple passengers
	if booking.PassengerCount > 2 {
		score += 10
	}
	
	// Popular train types
	if train != nil {
		switch train.TrainType {
		case "RAJDHANI", "SHATABDI", "VANDE_BHARAT":
			score += 25
		case "EXPRESS", "SUPERFAST":
			score += 15
		case "MAIL":
			score += 10
		}
	}
	
	// AC classes indicate higher demand
	if strings.Contains(booking.ClassType, "AC") {
		score += 15
	}
	
	// Route popularity (check cache)
	route := fmt.Sprintf("%s-%s", booking.FromStation, booking.ToStation)
	p.cacheMutex.RLock()
	if routeInfo, exists := p.routeCache[route]; exists {
		if routeInfo.PopularityScore > 80 {
			score += 20
		} else if routeInfo.PopularityScore > 60 {
			score += 10
		}
	}
	p.cacheMutex.RUnlock()
	
	return math.Min(score, 100.0) // Cap at 100
}

// Enrich booking with additional analytics data
func (p *IRCTCETLPipeline) enrichBooking(booking *BookingRecord) (*EnrichedBooking, error) {
	enriched := &EnrichedBooking{
		BookingRecord: *booking,
		ProcessedAt:   time.Now(),
	}
	
	// Get train information
	train, err := p.getTrainInfo(booking.TrainNo)
	if err == nil {
		enriched.TrainName = train.TrainName
		enriched.DistanceKM = train.DistanceKM
	} else {
		enriched.TrainName = "Unknown Train"
		enriched.DistanceKM = 0
	}
	
	// Get user profile
	user, err := p.getUserProfile(booking.UserID)
	if err == nil {
		enriched.UserSegment = user.Segment
	} else {
		enriched.UserSegment = "NEW"
	}
	
	// Calculate demand score
	enriched.DemandScore = p.calculateDemandScore(booking, train)
	
	// Calculate revenue potential
	enriched.RevenuePotential = booking.TotalFare * enriched.DemandScore / 100.0
	
	// Get route popularity
	route := fmt.Sprintf("%s-%s", booking.FromStation, booking.ToStation)
	p.cacheMutex.RLock()
	if routeInfo, exists := p.routeCache[route]; exists {
		enriched.RoutePopularity = routeInfo.PopularityScore
	}
	p.cacheMutex.RUnlock()
	
	return enriched, nil
}

// Process batch of bookings concurrently
func (p *IRCTCETLPipeline) processBatch(bookings []*BookingRecord) []*EnrichedBooking {
	startTime := time.Now()
	
	// Create channels for concurrent processing
	bookingChan := make(chan *BookingRecord, len(bookings))
	resultChan := make(chan *EnrichedBooking, len(bookings))
	
	// Start workers
	for i := 0; i < p.config.WorkerCount; i++ {
		p.wg.Add(1)
		go func() {
			defer p.wg.Done()
			for booking := range bookingChan {
				enriched, err := p.enrichBooking(booking)
				if err != nil {
					log.Printf("❌ Error enriching booking %s: %v", booking.BookingID, err)
					processedRecords.WithLabelValues("error").Inc()
					continue
				}
				resultChan <- enriched
			}
		}()
	}
	
	// Send bookings to workers
	go func() {
		defer close(bookingChan)
		for _, booking := range bookings {
			bookingChan <- booking
		}
	}()
	
	// Collect results
	results := make([]*EnrichedBooking, 0, len(bookings))
	go func() {
		defer close(resultChan)
		p.wg.Wait()
	}()
	
	for enriched := range resultChan {
		results = append(results, enriched)
		processedRecords.WithLabelValues("success").Inc()
	}
	
	duration := time.Since(startTime)
	processingDuration.WithLabelValues("batch_processing").Observe(duration.Seconds())
	
	log.Printf("✅ Processed batch of %d bookings in %v (%.2f bookings/sec)",
		len(results), duration, float64(len(results))/duration.Seconds())
	
	return results
}

// Save enriched bookings to database
func (p *IRCTCETLPipeline) saveEnrichedBookings(enriched []*EnrichedBooking) error {
	if len(enriched) == 0 {
		return nil
	}
	
	startTime := time.Now()
	
	// Prepare batch insert
	query := `
		INSERT INTO enriched_bookings (
			booking_id, user_id, train_no, from_station, to_station,
			journey_date, booking_date, passenger_count, total_fare,
			payment_status, booking_status, class_type, quota_type,
			tatkal_flag, senior_citizen_flag, train_name, distance_km,
			route_popularity, demand_score, revenue_potential,
			user_segment, processed_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
		ON CONFLICT (booking_id) DO UPDATE SET
			demand_score = EXCLUDED.demand_score,
			revenue_potential = EXCLUDED.revenue_potential,
			processed_at = EXCLUDED.processed_at
	`
	
	tx, err := p.db.Begin(p.ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(p.ctx)
	
	for _, booking := range enriched {
		_, err := tx.Exec(p.ctx, query,
			booking.BookingID, booking.UserID, booking.TrainNo,
			booking.FromStation, booking.ToStation, booking.JourneyDate,
			booking.BookingDate, booking.PassengerCount, booking.TotalFare,
			booking.PaymentStatus, booking.BookingStatus, booking.ClassType,
			booking.QuotaType, booking.TatkalFlag, booking.SeniorCitizen,
			booking.TrainName, booking.DistanceKM, booking.RoutePopularity,
			booking.DemandScore, booking.RevenuePotential, booking.UserSegment,
			booking.ProcessedAt,
		)
		
		if err != nil {
			log.Printf("❌ Error inserting booking %s: %v", booking.BookingID, err)
			continue
		}
	}
	
	if err := tx.Commit(p.ctx); err != nil {
		return err
	}
	
	duration := time.Since(startTime)
	processingDuration.WithLabelValues("database_save").Observe(duration.Seconds())
	
	log.Printf("💾 Saved %d enriched bookings to database in %v", len(enriched), duration)
	return nil
}

// Publish enriched data to Kafka
func (p *IRCTCETLPipeline) publishToKafka(enriched []*EnrichedBooking) error {
	if len(enriched) == 0 {
		return nil
	}
	
	startTime := time.Now()
	messages := make([]kafka.Message, 0, len(enriched))
	
	for _, booking := range enriched {
		data, err := json.Marshal(booking)
		if err != nil {
			log.Printf("❌ Error marshaling booking %s: %v", booking.BookingID, err)
			continue
		}
		
		messages = append(messages, kafka.Message{
			Key:   []byte(booking.BookingID),
			Value: data,
			Time:  time.Now(),
		})
	}
	
	err := p.kafkaWriter.WriteMessages(p.ctx, messages...)
	if err != nil {
		return err
	}
	
	duration := time.Since(startTime)
	processingDuration.WithLabelValues("kafka_publish").Observe(duration.Seconds())
	
	log.Printf("📤 Published %d enriched bookings to Kafka in %v", len(messages), duration)
	return nil
}

// Main processing loop
func (p *IRCTCETLPipeline) Run() {
	log.Println("🚀 Starting IRCTC ETL Pipeline processing...")
	
	// Set up signal handling
	signal.Notify(p.shutdown, syscall.SIGINT, syscall.SIGTERM)
	
	// Start metrics collection
	go p.collectMetrics()
	
	// Main processing loop
	for {
		select {
		case <-p.shutdown:
			log.Println("⚠️ Received shutdown signal, stopping pipeline...")
			p.cancel()
			return
			
		case <-p.ctx.Done():
			log.Println("⏹️ Context cancelled, stopping pipeline...")
			return
			
		default:
			// Read batch of messages from Kafka
			bookings := make([]*BookingRecord, 0, p.config.BatchSize)
			
			for i := 0; i < p.config.BatchSize; i++ {
				// Set read timeout
				readCtx, cancel := context.WithTimeout(p.ctx, time.Second*10)
				
				message, err := p.kafkaReader.FetchMessage(readCtx)
				cancel()
				
				if err != nil {
					if i == 0 {
						// No messages available, wait a bit
						time.Sleep(p.config.ProcessingDelay)
					}
					break
				}
				
				// Parse booking record
				var booking BookingRecord
				if err := json.Unmarshal(message.Value, &booking); err != nil {
					log.Printf("❌ Error parsing booking message: %v", err)
					p.kafkaReader.CommitMessages(p.ctx, message)
					continue
				}
				
				bookings = append(bookings, &booking)
				
				// Commit message
				if err := p.kafkaReader.CommitMessages(p.ctx, message); err != nil {
					log.Printf("⚠️ Error committing message: %v", err)
				}
			}
			
			if len(bookings) == 0 {
				continue
			}
			
			// Process batch
			enriched := p.processBatch(bookings)
			
			// Save to database
			if err := p.saveEnrichedBookings(enriched); err != nil {
				log.Printf("❌ Error saving to database: %v", err)
			}
			
			// Publish to Kafka
			if err := p.publishToKafka(enriched); err != nil {
				log.Printf("❌ Error publishing to Kafka: %v", err)
			}
		}
	}
}

// Collect performance metrics
func (p *IRCTCETLPipeline) collectMetrics() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			// Collect runtime metrics
			var m runtime.MemStats
			runtime.ReadMemStats(&m)
			
			memoryUsage.Set(float64(m.Alloc))
			currentGoroutines.Set(float64(runtime.NumGoroutine()))
			
			// Log cache statistics
			p.cacheMutex.RLock()
			trainCacheSize := len(p.trainCache)
			userCacheSize := len(p.userCache)
			routeCacheSize := len(p.routeCache)
			p.cacheMutex.RUnlock()
			
			log.Printf("📊 Metrics - Memory: %d KB, Goroutines: %d, Cache: T:%d U:%d R:%d",
				m.Alloc/1024, runtime.NumGoroutine(),
				trainCacheSize, userCacheSize, routeCacheSize)
				
		case <-p.ctx.Done():
			return
		}
	}
}

// Cleanup resources
func (p *IRCTCETLPipeline) Close() {
	log.Println("🧹 Cleaning up IRCTC ETL Pipeline...")
	
	// Cancel context
	p.cancel()
	
	// Wait for workers to finish
	p.wg.Wait()
	
	// Close Kafka connections
	if p.kafkaReader != nil {
		p.kafkaReader.Close()
	}
	if p.kafkaWriter != nil {
		p.kafkaWriter.Close()
	}
	
	// Close Redis connection
	if p.redis != nil {
		p.redis.Close()
	}
	
	// Close database connection
	if p.db != nil {
		p.db.Close()
	}
	
	log.Println("✅ IRCTC ETL Pipeline cleanup completed!")
}

// Main function
func main() {
	// Configuration
	config := &ETLConfig{
		DatabaseURL:     "postgres://irctc:mumbai_local@localhost/irctc_analytics?sslmode=disable",
		RedisAddr:       "localhost:6379",
		KafkaBrokers:    []string{"localhost:9092"},
		BatchSize:       1000,
		WorkerCount:     runtime.NumCPU(),
		ProcessingDelay: time.Second * 5,
		CacheTTL:        time.Minute * 30,
		MetricsPort:     ":8080",
	}
	
	// Initialize pipeline
	pipeline, err := NewIRCTCETLPipeline(config)
	if err != nil {
		log.Fatalf("❌ Failed to initialize pipeline: %v", err)
	}
	defer pipeline.Close()
	
	log.Println("🎉 IRCTC ETL Pipeline started successfully!")
	log.Printf("📊 Configuration: BatchSize=%d, Workers=%d, CacheTTL=%v",
		config.BatchSize, config.WorkerCount, config.CacheTTL)
	
	// Run the pipeline
	pipeline.Run()
	
	log.Println("👋 IRCTC ETL Pipeline stopped gracefully!")
}

/*
Mumbai Learning Notes:
1. High-performance concurrent processing with goroutines and channels
2. Multi-level caching strategy (local map, Redis) for optimal performance
3. Database connection pooling with pgxpool for scalability
4. Kafka integration for real-time stream processing
5. Prometheus metrics collection for monitoring and alerting
6. Graceful shutdown handling with context cancellation
7. Memory-efficient batch processing for large datasets
8. Error handling and resilience patterns for production systems

Production Deployment:
- Configure appropriate worker count based on system resources
- Set up monitoring dashboards with Prometheus and Grafana
- Implement proper logging with structured logs
- Configure database and Redis clusters for high availability
- Set up Kafka cluster with proper replication
- Add health checks and readiness probes
- Implement circuit breakers for external dependencies
- Add comprehensive error tracking and alerting
*/
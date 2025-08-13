package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"runtime"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"net/http"
)

// Flipkart-style ML Feature Pipeline
// Real-time feature extraction aur transformation ke liye
// Mumbai ki traffic ki tarah concurrent processing

// Metrics for monitoring pipeline performance
var (
	featuresProcessed = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "features_processed_total",
			Help: "Total number of features processed by type",
		},
		[]string{"feature_type", "status"},
	)
	
	processingLatency = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "feature_processing_duration_seconds",
			Help: "Time taken to process features",
			Buckets: prometheus.ExponentialBuckets(0.001, 2, 10),
		},
		[]string{"feature_type"},
	)
	
	pipelineErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "pipeline_errors_total",
			Help: "Total number of pipeline errors",
		},
		[]string{"error_type", "component"},
	)
)

// User behavior data structure - Flipkart user jaisa
type UserBehavior struct {
	UserID          string    `json:"user_id"`
	SessionID       string    `json:"session_id"`
	Timestamp       time.Time `json:"timestamp"`
	Action          string    `json:"action"` // view, cart, purchase, search
	ProductID       string    `json:"product_id,omitempty"`
	Category        string    `json:"category,omitempty"`
	Price           float64   `json:"price,omitempty"`
	SearchQuery     string    `json:"search_query,omitempty"`
	DeviceType      string    `json:"device_type"`
	Location        string    `json:"location"`
	TimeOnPage      int       `json:"time_on_page"`
	PreviousAction  string    `json:"previous_action,omitempty"`
}

// Extracted features - ML model ke liye ready
type MLFeatures struct {
	UserID                    string    `json:"user_id"`
	SessionID                 string    `json:"session_id"`
	Timestamp                 time.Time `json:"timestamp"`
	
	// Behavioral features
	ActionsInSession          int       `json:"actions_in_session"`
	TimeSpentInSession        float64   `json:"time_spent_in_session"`
	UniqueProductsViewed      int       `json:"unique_products_viewed"`
	UniqueCategoriesViewed    int       `json:"unique_categories_viewed"`
	
	// Engagement features
	AverageTimeOnPage         float64   `json:"avg_time_on_page"`
	SearchToViewRatio         float64   `json:"search_to_view_ratio"`
	ViewToCartRatio           float64   `json:"view_to_cart_ratio"`
	CartToPurchaseRatio       float64   `json:"cart_to_purchase_ratio"`
	
	// Price sensitivity features
	AveragePriceViewed        float64   `json:"avg_price_viewed"`
	MaxPriceViewed            float64   `json:"max_price_viewed"`
	MinPriceViewed            float64   `json:"min_price_viewed"`
	PriceVariance             float64   `json:"price_variance"`
	
	// Temporal features
	HourOfDay                 int       `json:"hour_of_day"`
	DayOfWeek                 int       `json:"day_of_week"`
	IsWeekend                 bool      `json:"is_weekend"`
	IsBusinessHour            bool      `json:"is_business_hour"`
	
	// Device and location features
	DeviceType                string    `json:"device_type"`
	LocationTier              string    `json:"location_tier"` // metro, tier1, tier2, tier3
	
	// Historical features (would come from feature store)
	UserLifetimeValue         float64   `json:"user_lifetime_value"`
	DaysSinceLastPurchase     int       `json:"days_since_last_purchase"`
	TotalPurchases            int       `json:"total_purchases"`
	FavoriteCategory          string    `json:"favorite_category"`
}

// Feature processor interface
type FeatureProcessor interface {
	Process(ctx context.Context, behavior UserBehavior) (MLFeatures, error)
	GetProcessorType() string
}

// Session-based feature processor
type SessionFeatureProcessor struct {
	sessionStore map[string][]UserBehavior
	mu           sync.RWMutex
}

func NewSessionFeatureProcessor() *SessionFeatureProcessor {
	return &SessionFeatureProcessor{
		sessionStore: make(map[string][]UserBehavior),
	}
}

func (p *SessionFeatureProcessor) Process(ctx context.Context, behavior UserBehavior) (MLFeatures, error) {
	start := time.Now()
	defer func() {
		processingLatency.WithLabelValues("session").Observe(time.Since(start).Seconds())
	}()
	
	p.mu.Lock()
	defer p.mu.Unlock()
	
	// Session mein add karo - Mumbai local mein jagah dhundne jaisa
	p.sessionStore[behavior.SessionID] = append(p.sessionStore[behavior.SessionID], behavior)
	sessionBehaviors := p.sessionStore[behavior.SessionID]
	
	features := MLFeatures{
		UserID:    behavior.UserID,
		SessionID: behavior.SessionID,
		Timestamp: behavior.Timestamp,
		DeviceType: behavior.DeviceType,
	}
	
	// Session-based features calculate karo
	features.ActionsInSession = len(sessionBehaviors)
	
	// Time-based features
	if len(sessionBehaviors) > 1 {
		firstAction := sessionBehaviors[0].Timestamp
		lastAction := sessionBehaviors[len(sessionBehaviors)-1].Timestamp
		features.TimeSpentInSession = lastAction.Sub(firstAction).Seconds()
	}
	
	// Behavioral analysis - Flipkart user behavior jaisa
	viewCount := 0
	cartCount := 0
	purchaseCount := 0
	searchCount := 0
	uniqueProducts := make(map[string]bool)
	uniqueCategories := make(map[string]bool)
	var timeOnPages []int
	var prices []float64
	
	for _, b := range sessionBehaviors {
		switch b.Action {
		case "view":
			viewCount++
			if b.ProductID != "" {
				uniqueProducts[b.ProductID] = true
			}
			if b.Category != "" {
				uniqueCategories[b.Category] = true
			}
			if b.Price > 0 {
				prices = append(prices, b.Price)
			}
		case "cart":
			cartCount++
		case "purchase":
			purchaseCount++
		case "search":
			searchCount++
		}
		
		if b.TimeOnPage > 0 {
			timeOnPages = append(timeOnPages, b.TimeOnPage)
		}
	}
	
	features.UniqueProductsViewed = len(uniqueProducts)
	features.UniqueCategoriesViewed = len(uniqueCategories)
	
	// Engagement ratios calculate karo
	if viewCount > 0 {
		features.ViewToCartRatio = float64(cartCount) / float64(viewCount)
	}
	if cartCount > 0 {
		features.CartToPurchaseRatio = float64(purchaseCount) / float64(cartCount)
	}
	if searchCount > 0 && viewCount > 0 {
		features.SearchToViewRatio = float64(searchCount) / float64(viewCount)
	}
	
	// Time on page analysis
	if len(timeOnPages) > 0 {
		totalTime := 0
		for _, t := range timeOnPages {
			totalTime += t
		}
		features.AverageTimeOnPage = float64(totalTime) / float64(len(timeOnPages))
	}
	
	// Price analysis - Shopping behavior insights
	if len(prices) > 0 {
		features.AveragePriceViewed = calculateMean(prices)
		features.MaxPriceViewed = calculateMax(prices)
		features.MinPriceViewed = calculateMin(prices)
		features.PriceVariance = calculateVariance(prices)
	}
	
	// Temporal features - Mumbai time zone mein
	features.HourOfDay = behavior.Timestamp.Hour()
	features.DayOfWeek = int(behavior.Timestamp.Weekday())
	features.IsWeekend = features.DayOfWeek == 0 || features.DayOfWeek == 6
	features.IsBusinessHour = features.HourOfDay >= 9 && features.HourOfDay <= 18
	
	// Location tier mapping - Indian cities
	features.LocationTier = getLocationTier(behavior.Location)
	
	// Historical features (mock data - production mein feature store se aayega)
	features.UserLifetimeValue = rand.Float64() * 50000 // ₹0-50k range
	features.DaysSinceLastPurchase = rand.Intn(365)
	features.TotalPurchases = rand.Intn(100)
	features.FavoriteCategory = getMockFavoriteCategory()
	
	featuresProcessed.WithLabelValues("session", "success").Inc()
	return features, nil
}

func (p *SessionFeatureProcessor) GetProcessorType() string {
	return "session"
}

// Real-time feature processor - Instant features
type RealTimeFeatureProcessor struct {
	cache map[string]interface{}
	mu    sync.RWMutex
}

func NewRealTimeFeatureProcessor() *RealTimeFeatureProcessor {
	return &RealTimeFeatureProcessor{
		cache: make(map[string]interface{}),
	}
}

func (p *RealTimeFeatureProcessor) Process(ctx context.Context, behavior UserBehavior) (MLFeatures, error) {
	start := time.Now()
	defer func() {
		processingLatency.WithLabelValues("realtime").Observe(time.Since(start).Seconds())
	}()
	
	features := MLFeatures{
		UserID:    behavior.UserID,
		SessionID: behavior.SessionID,
		Timestamp: behavior.Timestamp,
		DeviceType: behavior.DeviceType,
	}
	
	// Immediate context features
	features.HourOfDay = behavior.Timestamp.Hour()
	features.DayOfWeek = int(behavior.Timestamp.Weekday())
	features.IsWeekend = features.DayOfWeek == 0 || features.DayOfWeek == 6
	features.IsBusinessHour = features.HourOfDay >= 9 && features.HourOfDay <= 18
	features.LocationTier = getLocationTier(behavior.Location)
	
	// Single action features
	features.ActionsInSession = 1
	features.TimeSpentInSession = 0
	features.UniqueProductsViewed = 1
	if behavior.Category != "" {
		features.UniqueCategoriesViewed = 1
	}
	
	if behavior.TimeOnPage > 0 {
		features.AverageTimeOnPage = float64(behavior.TimeOnPage)
	}
	
	if behavior.Price > 0 {
		features.AveragePriceViewed = behavior.Price
		features.MaxPriceViewed = behavior.Price
		features.MinPriceViewed = behavior.Price
		features.PriceVariance = 0
	}
	
	// Mock historical data
	features.UserLifetimeValue = rand.Float64() * 50000
	features.DaysSinceLastPurchase = rand.Intn(365)
	features.TotalPurchases = rand.Intn(100)
	features.FavoriteCategory = getMockFavoriteCategory()
	
	featuresProcessed.WithLabelValues("realtime", "success").Inc()
	return features, nil
}

func (p *RealTimeFeatureProcessor) GetProcessorType() string {
	return "realtime"
}

// ML Feature Pipeline - Main orchestrator
type MLFeaturePipeline struct {
	processors    map[string]FeatureProcessor
	workerPool    chan struct{}
	outputChannel chan MLFeatures
	errorChannel  chan error
	ctx           context.Context
	cancel        context.CancelFunc
	wg            sync.WaitGroup
}

func NewMLFeaturePipeline(maxWorkers int) *MLFeaturePipeline {
	ctx, cancel := context.WithCancel(context.Background())
	
	pipeline := &MLFeaturePipeline{
		processors:    make(map[string]FeatureProcessor),
		workerPool:    make(chan struct{}, maxWorkers),
		outputChannel: make(chan MLFeatures, 1000),
		errorChannel:  make(chan error, 100),
		ctx:           ctx,
		cancel:        cancel,
	}
	
	// Initialize worker pool
	for i := 0; i < maxWorkers; i++ {
		pipeline.workerPool <- struct{}{}
	}
	
	return pipeline
}

func (p *MLFeaturePipeline) RegisterProcessor(name string, processor FeatureProcessor) {
	p.processors[name] = processor
	log.Printf("✅ Registered feature processor: %s", name)
}

func (p *MLFeaturePipeline) ProcessBehavior(behavior UserBehavior, processorName string) error {
	select {
	case <-p.workerPool: // Mumbai local mein seat milna
		defer func() {
			p.workerPool <- struct{}{} // Seat wapas karo
		}()
		
		p.wg.Add(1)
		go func() {
			defer p.wg.Done()
			
			processor, exists := p.processors[processorName]
			if !exists {
				err := fmt.Errorf("processor not found: %s", processorName)
				select {
				case p.errorChannel <- err:
				default:
				}
				pipelineErrors.WithLabelValues("processor_not_found", "pipeline").Inc()
				return
			}
			
			features, err := processor.Process(p.ctx, behavior)
			if err != nil {
				select {
				case p.errorChannel <- err:
				default:
				}
				pipelineErrors.WithLabelValues("processing_error", processor.GetProcessorType()).Inc()
				return
			}
			
			select {
			case p.outputChannel <- features:
			case <-p.ctx.Done():
				return
			default:
				// Channel full, drop the message
				pipelineErrors.WithLabelValues("output_buffer_full", "pipeline").Inc()
			}
		}()
		
		return nil
		
	case <-p.ctx.Done():
		return fmt.Errorf("pipeline is shutting down")
	default:
		pipelineErrors.WithLabelValues("worker_pool_full", "pipeline").Inc()
		return fmt.Errorf("all workers are busy")
	}
}

func (p *MLFeaturePipeline) GetOutputChannel() <-chan MLFeatures {
	return p.outputChannel
}

func (p *MLFeaturePipeline) GetErrorChannel() <-chan error {
	return p.errorChannel
}

func (p *MLFeaturePipeline) Shutdown() {
	log.Println("🛑 Shutting down ML Feature Pipeline...")
	p.cancel()
	p.wg.Wait()
	close(p.outputChannel)
	close(p.errorChannel)
	log.Println("✅ Pipeline shutdown complete")
}

// Utility functions

func calculateMean(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}
	
	sum := 0.0
	for _, v := range values {
		sum += v
	}
	return sum / float64(len(values))
}

func calculateMax(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}
	
	max := values[0]
	for _, v := range values {
		if v > max {
			max = v
		}
	}
	return max
}

func calculateMin(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}
	
	min := values[0]
	for _, v := range values {
		if v < min {
			min = v
		}
	}
	return min
}

func calculateVariance(values []float64) float64 {
	if len(values) <= 1 {
		return 0
	}
	
	mean := calculateMean(values)
	sumSquaredDiff := 0.0
	
	for _, v := range values {
		diff := v - mean
		sumSquaredDiff += diff * diff
	}
	
	return sumSquaredDiff / float64(len(values)-1)
}

func getLocationTier(location string) string {
	// Indian city tier mapping
	metros := map[string]bool{
		"Mumbai": true, "Delhi": true, "Bangalore": true, "Chennai": true,
		"Kolkata": true, "Hyderabad": true, "Pune": true, "Ahmedabad": true,
	}
	
	if metros[location] {
		return "metro"
	}
	
	// Simple tier assignment (production mein proper mapping hogi)
	hash := 0
	for _, c := range location {
		hash += int(c)
	}
	
	switch hash % 3 {
	case 0:
		return "tier1"
	case 1:
		return "tier2"
	default:
		return "tier3"
	}
}

func getMockFavoriteCategory() string {
	categories := []string{
		"Electronics", "Fashion", "Home & Kitchen", "Books",
		"Sports", "Beauty", "Automotive", "Grocery",
	}
	return categories[rand.Intn(len(categories))]
}

// Generate sample user behavior - Testing ke liye
func generateSampleBehavior() UserBehavior {
	actions := []string{"view", "cart", "purchase", "search"}
	devices := []string{"mobile", "desktop", "tablet"}
	locations := []string{"Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad"}
	categories := []string{"Electronics", "Fashion", "Home", "Books", "Sports"}
	
	userID := fmt.Sprintf("USER_%06d", rand.Intn(10000))
	sessionID := fmt.Sprintf("SESSION_%s_%d", userID, time.Now().Unix())
	
	behavior := UserBehavior{
		UserID:         userID,
		SessionID:      sessionID,
		Timestamp:      time.Now(),
		Action:         actions[rand.Intn(len(actions))],
		DeviceType:     devices[rand.Intn(len(devices))],
		Location:       locations[rand.Intn(len(locations))],
		TimeOnPage:     rand.Intn(300) + 10, // 10-310 seconds
	}
	
	if behavior.Action == "view" || behavior.Action == "cart" || behavior.Action == "purchase" {
		behavior.ProductID = fmt.Sprintf("PROD_%06d", rand.Intn(100000))
		behavior.Category = categories[rand.Intn(len(categories))]
		behavior.Price = float64(rand.Intn(50000)) + 99.99 // ₹99-50k range
	}
	
	if behavior.Action == "search" {
		searchQueries := []string{
			"smartphone", "laptop", "headphones", "shoes", "shirt",
			"camera", "book", "watch", "tablet", "speaker",
		}
		behavior.SearchQuery = searchQueries[rand.Intn(len(searchQueries))]
	}
	
	return behavior
}

// Performance monitoring
func startMetricsServer() {
	http.Handle("/metrics", promhttp.Handler())
	go func() {
		log.Println("📊 Metrics server starting on :8080/metrics")
		if err := http.ListenAndServe(":8080", nil); err != nil {
			log.Printf("❌ Metrics server error: %v", err)
		}
	}()
}

// Demo function
func demonstrateMLFeaturePipeline() {
	fmt.Println("🚀 ML Feature Pipeline Demo: Flipkart-style Real-time Feature Engineering")
	fmt.Println("=" * 80)
	
	// Start metrics server
	startMetricsServer()
	
	// Create pipeline with worker pool
	pipeline := NewMLFeaturePipeline(runtime.NumCPU())
	defer pipeline.Shutdown()
	
	// Register processors
	sessionProcessor := NewSessionFeatureProcessor()
	realtimeProcessor := NewRealTimeFeatureProcessor()
	
	pipeline.RegisterProcessor("session", sessionProcessor)
	pipeline.RegisterProcessor("realtime", realtimeProcessor)
	
	// Start feature consumer
	go func() {
		for {
			select {
			case features := <-pipeline.GetOutputChannel():
				fmt.Printf("✅ Features generated for User: %s, Session: %s\n", 
					features.UserID[:10]+"...", features.SessionID[:15]+"...")
				fmt.Printf("   Actions: %d, Time: %.1fs, Products: %d, Categories: %d\n",
					features.ActionsInSession, features.TimeSpentInSession,
					features.UniqueProductsViewed, features.UniqueCategoriesViewed)
				fmt.Printf("   Location: %s, Device: %s, LTV: ₹%.0f\n",
					features.LocationTier, features.DeviceType, features.UserLifetimeValue)
				fmt.Println("   " + strings.Repeat("-", 50))
				
			case err := <-pipeline.GetErrorChannel():
				fmt.Printf("❌ Pipeline error: %v\n", err)
			}
		}
	}()
	
	// Simulate real-time user behaviors
	fmt.Println("\n📱 Simulating Flipkart user behaviors...")
	
	// Generate multiple user sessions
	for i := 0; i < 50; i++ {
		behavior := generateSampleBehavior()
		
		// Process with different processors
		processorType := "session"
		if i%3 == 0 {
			processorType = "realtime"
		}
		
		err := pipeline.ProcessBehavior(behavior, processorType)
		if err != nil {
			fmt.Printf("❌ Failed to process behavior: %v\n", err)
		}
		
		// Simulate real-time streaming
		time.Sleep(time.Millisecond * 100)
	}
	
	// Wait for processing to complete
	time.Sleep(time.Second * 3)
	
	fmt.Println("\n📊 Pipeline Performance Summary:")
	fmt.Printf("   Workers: %d (CPU cores)\n", runtime.NumCPU())
	fmt.Printf("   Processing: Real-time feature extraction\n")
	fmt.Printf("   Output: ML-ready feature vectors\n")
	fmt.Printf("   Monitoring: Prometheus metrics on :8080/metrics\n")
	
	fmt.Println("\n🎯 Production Ready Features:")
	fmt.Println("   ✅ Concurrent processing with worker pools")
	fmt.Println("   ✅ Multiple feature processor types")
	fmt.Println("   ✅ Real-time and session-based features")
	fmt.Println("   ✅ Prometheus metrics and monitoring")
	fmt.Println("   ✅ Error handling and graceful shutdown")
	fmt.Println("   ✅ Indian e-commerce context (Flipkart-style)")
	
	fmt.Println("\n💡 Feature Engineering Insights:")
	fmt.Println("   📈 Behavioral patterns: Actions, time spent, engagement ratios")
	fmt.Println("   💰 Price sensitivity: Average, variance, min/max analysis")
	fmt.Println("   🕒 Temporal features: Hour, day, weekend, business hours")
	fmt.Println("   🌍 Geographic features: Location tier mapping for India")
	fmt.Println("   📱 Device insights: Mobile vs desktop behavior")
	fmt.Println("   🛒 Shopping journey: View → Cart → Purchase conversion")
}

func main() {
	// Set random seed for consistent demo
	rand.Seed(time.Now().UnixNano())
	
	demonstrateMLFeaturePipeline()
	
	// Keep metrics server running
	fmt.Println("\n⏳ Keeping metrics server running for 30 seconds...")
	fmt.Println("   Visit http://localhost:8080/metrics to see Prometheus metrics")
	time.Sleep(30 * time.Second)
}
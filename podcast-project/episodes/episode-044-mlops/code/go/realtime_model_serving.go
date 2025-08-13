package main

/*
Real-time Model Serving - MLOps Episode 44
Production-ready real-time ML model serving with high throughput and low latency

Author: Claude Code
Context: High-performance model serving system like what Flipkart uses for real-time recommendations
*/

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"net/http"
	"strconv"
	"sync"
	"sync/atomic"
	"time"

	"github.com/gorilla/mux"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// ModelType represents different types of ML models
type ModelType string

const (
	FraudDetection     ModelType = "fraud_detection"
	Recommendation    ModelType = "recommendation"
	PriceOptimization ModelType = "price_optimization"
	SentimentAnalysis ModelType = "sentiment_analysis"
)

// PredictionRequest represents an incoming prediction request
// Mumbai me aane waali prediction request ka structure!
type PredictionRequest struct {
	ModelID    string                 `json:"model_id"`
	RequestID  string                 `json:"request_id"`
	InputData  map[string]interface{} `json:"input_data"`
	Timeout    int                    `json:"timeout_ms,omitempty"`
	BatchData  []map[string]interface{} `json:"batch_data,omitempty"`
	Metadata   map[string]string      `json:"metadata,omitempty"`
}

// PredictionResponse represents prediction response
type PredictionResponse struct {
	RequestID        string                 `json:"request_id"`
	ModelID          string                 `json:"model_id"`
	Prediction       interface{}            `json:"prediction"`
	Confidence       float64                `json:"confidence,omitempty"`
	ProcessingTimeMs int64                  `json:"processing_time_ms"`
	ModelVersion     string                 `json:"model_version"`
	Status           string                 `json:"status"`
	ErrorMessage     string                 `json:"error_message,omitempty"`
	Timestamp        time.Time              `json:"timestamp"`
	Metadata         map[string]interface{} `json:"metadata,omitempty"`
}

// ModelMetadata represents metadata for a loaded model
type ModelMetadata struct {
	ModelID        string            `json:"model_id"`
	Name           string            `json:"name"`
	Version        string            `json:"version"`
	ModelType      ModelType         `json:"model_type"`
	Framework      string            `json:"framework"`
	LoadedAt       time.Time         `json:"loaded_at"`
	LastUsed       time.Time         `json:"last_used"`
	RequestCount   int64             `json:"request_count"`
	AvgLatencyMs   float64           `json:"avg_latency_ms"`
	ErrorRate      float64           `json:"error_rate"`
	IsActive       bool              `json:"is_active"`
	Configuration  map[string]interface{} `json:"configuration"`
}

// LoadedModel represents a model loaded in memory
type LoadedModel struct {
	Metadata     *ModelMetadata    `json:"metadata"`
	Model        interface{}       `json:"-"` // Actual model object (hidden from JSON)
	LastAccess   time.Time         `json:"last_access"`
	RequestCount int64             `json:"request_count"`
	TotalLatency int64             `json:"total_latency_ms"`
	ErrorCount   int64             `json:"error_count"`
	mutex        sync.RWMutex      `json:"-"`
}

// ModelServer represents the main model serving system
// Mumbai me sabse fast model serving ka system!
type ModelServer struct {
	models        sync.Map // map[string]*LoadedModel
	modelCache    sync.Map // LRU cache for models
	requestChan   chan *PredictionRequest
	responseChan  chan *PredictionResponse
	workers       int
	ctx           context.Context
	cancel        context.CancelFunc
	
	// Metrics
	totalRequests    int64
	successRequests  int64
	failedRequests   int64
	totalLatency     int64
	
	// Prometheus metrics
	requestCounter    prometheus.Counter
	latencyHistogram  prometheus.Histogram
	errorCounter      prometheus.Counter
	modelGauge        prometheus.Gauge
}

// NewModelServer creates a new model serving instance
func NewModelServer(workers int) *ModelServer {
	ctx, cancel := context.WithCancel(context.Background())
	
	// Initialize Prometheus metrics
	requestCounter := prometheus.NewCounter(prometheus.CounterOpts{
		Name: "model_serving_requests_total",
		Help: "Total number of prediction requests",
	})
	
	latencyHistogram := prometheus.NewHistogram(prometheus.HistogramOpts{
		Name:    "model_serving_latency_seconds",
		Help:    "Latency of prediction requests in seconds",
		Buckets: prometheus.DefBuckets,
	})
	
	errorCounter := prometheus.NewCounter(prometheus.CounterOpts{
		Name: "model_serving_errors_total",
		Help: "Total number of prediction errors",
	})
	
	modelGauge := prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "model_serving_loaded_models",
		Help: "Number of loaded models",
	})
	
	// Register metrics
	prometheus.MustRegister(requestCounter, latencyHistogram, errorCounter, modelGauge)
	
	server := &ModelServer{
		requestChan:      make(chan *PredictionRequest, 1000),
		responseChan:     make(chan *PredictionResponse, 1000),
		workers:          workers,
		ctx:              ctx,
		cancel:           cancel,
		requestCounter:   requestCounter,
		latencyHistogram: latencyHistogram,
		errorCounter:     errorCounter,
		modelGauge:       modelGauge,
	}
	
	// Start worker goroutines
	for i := 0; i < workers; i++ {
		go server.worker(i)
	}
	
	// Start model cleanup goroutine
	go server.modelCleanup()
	
	log.Printf("Model server initialized with %d workers", workers)
	return server
}

// LoadModel loads a model into memory
func (s *ModelServer) LoadModel(metadata *ModelMetadata) error {
	log.Printf("Loading model: %s (%s)", metadata.ModelID, metadata.Name)
	
	// Simulate model loading
	time.Sleep(time.Duration(100+rand.Intn(500)) * time.Millisecond)
	
	// Create mock model based on type
	var model interface{}
	switch metadata.ModelType {
	case FraudDetection:
		model = s.createFraudDetectionModel(metadata)
	case Recommendation:
		model = s.createRecommendationModel(metadata)
	case PriceOptimization:
		model = s.createPriceOptimizationModel(metadata)
	case SentimentAnalysis:
		model = s.createSentimentAnalysisModel(metadata)
	default:
		model = s.createGenericModel(metadata)
	}
	
	loadedModel := &LoadedModel{
		Metadata:   metadata,
		Model:      model,
		LastAccess: time.Now(),
	}
	
	metadata.LoadedAt = time.Now()
	metadata.LastUsed = time.Now()
	metadata.IsActive = true
	
	s.models.Store(metadata.ModelID, loadedModel)
	
	// Update model gauge
	var modelCount float64
	s.models.Range(func(key, value interface{}) bool {
		modelCount++
		return true
	})
	s.modelGauge.Set(modelCount)
	
	log.Printf("Model loaded successfully: %s", metadata.ModelID)
	return nil
}

// createFraudDetectionModel creates a mock fraud detection model
func (s *ModelServer) createFraudDetectionModel(metadata *ModelMetadata) map[string]interface{} {
	return map[string]interface{}{
		"type":           "random_forest",
		"features":       []string{"amount", "user_age", "transaction_hour", "merchant_category"},
		"threshold":      0.5,
		"model_weights": map[string]float64{
			"amount":             0.3,
			"user_age":          0.2,
			"transaction_hour":   0.15,
			"merchant_category": 0.35,
		},
		"version": metadata.Version,
	}
}

// createRecommendationModel creates a mock recommendation model
func (s *ModelServer) createRecommendationModel(metadata *ModelMetadata) map[string]interface{} {
	return map[string]interface{}{
		"type":        "collaborative_filtering",
		"embedding_dim": 128,
		"num_items":   10000,
		"num_users":   100000,
		"top_k":       10,
		"model_matrix": generateRandomMatrix(100, 128), // Simplified
		"version":     metadata.Version,
	}
}

// createPriceOptimizationModel creates a mock price optimization model
func (s *ModelServer) createPriceOptimizationModel(metadata *ModelMetadata) map[string]interface{} {
	return map[string]interface{}{
		"type":           "gradient_boosting",
		"features":       []string{"base_price", "demand", "competition", "seasonality"},
		"price_elasticity": -1.2,
		"profit_margin":   0.15,
		"version":        metadata.Version,
	}
}

// createSentimentAnalysisModel creates a mock sentiment analysis model
func (s *ModelServer) createSentimentAnalysisModel(metadata *ModelMetadata) map[string]interface{} {
	return map[string]interface{}{
		"type":       "bert",
		"vocab_size": 30000,
		"max_length": 512,
		"labels":     []string{"positive", "negative", "neutral"},
		"version":    metadata.Version,
	}
}

// createGenericModel creates a generic model
func (s *ModelServer) createGenericModel(metadata *ModelMetadata) map[string]interface{} {
	return map[string]interface{}{
		"type":    "generic",
		"version": metadata.Version,
	}
}

// generateRandomMatrix generates a random matrix for demo purposes
func generateRandomMatrix(rows, cols int) [][]float64 {
	matrix := make([][]float64, rows)
	for i := range matrix {
		matrix[i] = make([]float64, cols)
		for j := range matrix[i] {
			matrix[i][j] = rand.Float64()
		}
	}
	return matrix
}

// Predict processes a prediction request
func (s *ModelServer) Predict(req *PredictionRequest) *PredictionResponse {
	startTime := time.Now()
	
	atomic.AddInt64(&s.totalRequests, 1)
	s.requestCounter.Inc()
	
	response := &PredictionResponse{
		RequestID: req.RequestID,
		ModelID:   req.ModelID,
		Timestamp: time.Now(),
		Status:    "success",
	}
	
	// Get model
	modelInterface, exists := s.models.Load(req.ModelID)
	if !exists {
		response.Status = "error"
		response.ErrorMessage = fmt.Sprintf("Model not found: %s", req.ModelID)
		atomic.AddInt64(&s.failedRequests, 1)
		s.errorCounter.Inc()
		return response
	}
	
	loadedModel := modelInterface.(*LoadedModel)
	
	// Update model access stats
	loadedModel.mutex.Lock()
	loadedModel.LastAccess = time.Now()
	loadedModel.RequestCount++
	loadedModel.mutex.Unlock()
	
	// Perform prediction based on model type
	var prediction interface{}
	var confidence float64
	var err error
	
	switch loadedModel.Metadata.ModelType {
	case FraudDetection:
		prediction, confidence, err = s.predictFraud(loadedModel, req.InputData)
	case Recommendation:
		prediction, confidence, err = s.predictRecommendations(loadedModel, req.InputData)
	case PriceOptimization:
		prediction, confidence, err = s.optimizePrice(loadedModel, req.InputData)
	case SentimentAnalysis:
		prediction, confidence, err = s.analyzeSentiment(loadedModel, req.InputData)
	default:
		prediction, confidence, err = s.genericPredict(loadedModel, req.InputData)
	}
	
	if err != nil {
		response.Status = "error"
		response.ErrorMessage = err.Error()
		atomic.AddInt64(&s.failedRequests, 1)
		s.errorCounter.Inc()
		
		loadedModel.mutex.Lock()
		loadedModel.ErrorCount++
		loadedModel.mutex.Unlock()
	} else {
		response.Prediction = prediction
		response.Confidence = confidence
		response.ModelVersion = loadedModel.Metadata.Version
		atomic.AddInt64(&s.successRequests, 1)
	}
	
	// Calculate processing time
	processingTime := time.Since(startTime)
	response.ProcessingTimeMs = processingTime.Nanoseconds() / 1e6
	
	// Update metrics
	atomic.AddInt64(&s.totalLatency, response.ProcessingTimeMs)
	s.latencyHistogram.Observe(processingTime.Seconds())
	
	loadedModel.mutex.Lock()
	loadedModel.TotalLatency += response.ProcessingTimeMs
	loadedModel.Metadata.AvgLatencyMs = float64(loadedModel.TotalLatency) / float64(loadedModel.RequestCount)
	loadedModel.Metadata.ErrorRate = float64(loadedModel.ErrorCount) / float64(loadedModel.RequestCount)
	loadedModel.mutex.Unlock()
	
	return response
}

// predictFraud performs fraud detection prediction
// Mumbai me fraud detection ki prediction!
func (s *ModelServer) predictFraud(model *LoadedModel, inputData map[string]interface{}) (interface{}, float64, error) {
	// Simulate fraud detection logic
	time.Sleep(time.Duration(10+rand.Intn(50)) * time.Millisecond)
	
	modelConfig := model.Model.(map[string]interface{})
	weights := modelConfig["model_weights"].(map[string]float64)
	
	// Extract features
	amount, _ := inputData["amount"].(float64)
	userAge, _ := inputData["user_age"].(float64)
	transactionHour, _ := inputData["transaction_hour"].(float64)
	
	// Calculate fraud score
	fraudScore := 0.0
	
	// High amount risk
	if amount > 10000 {
		fraudScore += weights["amount"] * 0.8
	} else if amount > 1000 {
		fraudScore += weights["amount"] * 0.3
	}
	
	// User age risk (new users are riskier)
	if userAge < 30 {
		fraudScore += weights["user_age"] * 0.6
	}
	
	// Time-based risk (night transactions are riskier)
	if transactionHour < 6 || transactionHour > 22 {
		fraudScore += weights["transaction_hour"] * 0.7
	}
	
	// Add some randomness for realism
	fraudScore += rand.Float64() * 0.2
	
	// Normalize score
	fraudScore = math.Min(fraudScore, 1.0)
	
	isFraud := fraudScore > 0.5
	confidence := math.Abs(fraudScore - 0.5) * 2 // Convert to confidence (0-1)
	
	result := map[string]interface{}{
		"is_fraud":    isFraud,
		"fraud_score": fraudScore,
		"risk_factors": []string{},
	}
	
	// Add risk factors
	if amount > 10000 {
		result["risk_factors"] = append(result["risk_factors"].([]string), "high_amount")
	}
	if userAge < 30 {
		result["risk_factors"] = append(result["risk_factors"].([]string), "new_user")
	}
	if transactionHour < 6 || transactionHour > 22 {
		result["risk_factors"] = append(result["risk_factors"].([]string), "unusual_time")
	}
	
	return result, confidence, nil
}

// predictRecommendations performs product recommendation prediction
func (s *ModelServer) predictRecommendations(model *LoadedModel, inputData map[string]interface{}) (interface{}, float64, error) {
	// Simulate recommendation logic
	time.Sleep(time.Duration(20+rand.Intn(80)) * time.Millisecond)
	
	modelConfig := model.Model.(map[string]interface{})
	topK := int(modelConfig["top_k"].(int))
	
	userID, _ := inputData["user_id"].(string)
	category, _ := inputData["category"].(string)
	
	// Generate mock recommendations
	recommendations := make([]map[string]interface{}, topK)
	for i := 0; i < topK; i++ {
		score := rand.Float64() * 0.5 + 0.5 // Scores between 0.5-1.0
		recommendations[i] = map[string]interface{}{
			"item_id":   fmt.Sprintf("item_%d", rand.Intn(10000)),
			"score":     score,
			"category":  category,
			"rank":      i + 1,
		}
	}
	
	result := map[string]interface{}{
		"user_id":        userID,
		"recommendations": recommendations,
		"algorithm":      "collaborative_filtering",
	}
	
	// Average confidence based on recommendation scores
	avgConfidence := 0.0
	for _, rec := range recommendations {
		avgConfidence += rec.(map[string]interface{})["score"].(float64)
	}
	avgConfidence /= float64(len(recommendations))
	
	return result, avgConfidence, nil
}

// optimizePrice performs price optimization prediction
func (s *ModelServer) optimizePrice(model *LoadedModel, inputData map[string]interface{}) (interface{}, float64, error) {
	// Simulate price optimization logic
	time.Sleep(time.Duration(15+rand.Intn(60)) * time.Millisecond)
	
	basePrice, _ := inputData["base_price"].(float64)
	demand, _ := inputData["demand"].(float64)
	competition, _ := inputData["competition"].(float64)
	
	// Simple price optimization algorithm
	demandMultiplier := 1.0 + (demand-0.5)*0.3 // Adjust based on demand
	competitionMultiplier := 1.0 - (competition-0.5)*0.2 // Adjust based on competition
	
	optimizedPrice := basePrice * demandMultiplier * competitionMultiplier
	
	// Add some randomness
	optimizedPrice *= (0.95 + rand.Float64()*0.1)
	
	priceChange := (optimizedPrice - basePrice) / basePrice
	confidence := 1.0 - math.Abs(priceChange) // Higher confidence for smaller changes
	
	result := map[string]interface{}{
		"original_price":  basePrice,
		"optimized_price": math.Round(optimizedPrice*100) / 100,
		"price_change":    math.Round(priceChange*10000) / 100, // Percentage
		"demand_factor":   demandMultiplier,
		"competition_factor": competitionMultiplier,
	}
	
	return result, confidence, nil
}

// analyzeSentiment performs sentiment analysis prediction
func (s *ModelServer) analyzeSentiment(model *LoadedModel, inputData map[string]interface{}) (interface{}, float64, error) {
	// Simulate sentiment analysis logic
	time.Sleep(time.Duration(25+rand.Intn(75)) * time.Millisecond)
	
	text, _ := inputData["text"].(string)
	
	// Simple sentiment analysis (mock)
	sentiments := []string{"positive", "negative", "neutral"}
	scores := []float64{rand.Float64(), rand.Float64(), rand.Float64()}
	
	// Normalize scores
	total := scores[0] + scores[1] + scores[2]
	for i := range scores {
		scores[i] /= total
	}
	
	// Find max sentiment
	maxIdx := 0
	maxScore := scores[0]
	for i, score := range scores {
		if score > maxScore {
			maxScore = score
			maxIdx = i
		}
	}
	
	result := map[string]interface{}{
		"text":      text,
		"sentiment": sentiments[maxIdx],
		"scores": map[string]float64{
			"positive": scores[0],
			"negative": scores[1],
			"neutral":  scores[2],
		},
	}
	
	return result, maxScore, nil
}

// genericPredict performs generic prediction
func (s *ModelServer) genericPredict(model *LoadedModel, inputData map[string]interface{}) (interface{}, float64, error) {
	// Simulate generic prediction logic
	time.Sleep(time.Duration(10+rand.Intn(40)) * time.Millisecond)
	
	result := map[string]interface{}{
		"prediction": rand.Float64(),
		"model_type": "generic",
		"input_size": len(inputData),
	}
	
	confidence := 0.5 + rand.Float64()*0.5
	
	return result, confidence, nil
}

// worker processes prediction requests
func (s *ModelServer) worker(workerID int) {
	log.Printf("Worker %d started", workerID)
	
	for {
		select {
		case req := <-s.requestChan:
			response := s.Predict(req)
			
			select {
			case s.responseChan <- response:
			case <-s.ctx.Done():
				return
			}
			
		case <-s.ctx.Done():
			log.Printf("Worker %d stopped", workerID)
			return
		}
	}
}

// modelCleanup removes unused models from memory
func (s *ModelServer) modelCleanup() {
	ticker := time.NewTicker(10 * time.Minute)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			s.cleanupUnusedModels()
		case <-s.ctx.Done():
			return
		}
	}
}

// cleanupUnusedModels removes models that haven't been used recently
func (s *ModelServer) cleanupUnusedModels() {
	cutoff := time.Now().Add(-30 * time.Minute) // Remove models unused for 30 minutes
	
	s.models.Range(func(key, value interface{}) bool {
		modelID := key.(string)
		loadedModel := value.(*LoadedModel)
		
		loadedModel.mutex.RLock()
		lastAccess := loadedModel.LastAccess
		loadedModel.mutex.RUnlock()
		
		if lastAccess.Before(cutoff) {
			s.models.Delete(modelID)
			log.Printf("Cleaned up unused model: %s", modelID)
		}
		
		return true
	})
}

// GetStats returns server statistics
func (s *ModelServer) GetStats() map[string]interface{} {
	totalReq := atomic.LoadInt64(&s.totalRequests)
	successReq := atomic.LoadInt64(&s.successRequests)
	failedReq := atomic.LoadInt64(&s.failedRequests)
	totalLat := atomic.LoadInt64(&s.totalLatency)
	
	var avgLatency float64
	if totalReq > 0 {
		avgLatency = float64(totalLat) / float64(totalReq)
	}
	
	var successRate float64
	if totalReq > 0 {
		successRate = float64(successReq) / float64(totalReq)
	}
	
	var modelCount int
	s.models.Range(func(key, value interface{}) bool {
		modelCount++
		return true
	})
	
	return map[string]interface{}{
		"total_requests":    totalReq,
		"successful_requests": successReq,
		"failed_requests":   failedReq,
		"success_rate":      successRate,
		"avg_latency_ms":    avgLatency,
		"loaded_models":     modelCount,
		"workers":           s.workers,
		"uptime_seconds":    time.Since(time.Now()).Seconds(),
	}
}

// GetModelStats returns statistics for a specific model
func (s *ModelServer) GetModelStats(modelID string) map[string]interface{} {
	modelInterface, exists := s.models.Load(modelID)
	if !exists {
		return map[string]interface{}{"error": "Model not found"}
	}
	
	loadedModel := modelInterface.(*LoadedModel)
	loadedModel.mutex.RLock()
	defer loadedModel.mutex.RUnlock()
	
	return map[string]interface{}{
		"model_id":       loadedModel.Metadata.ModelID,
		"name":           loadedModel.Metadata.Name,
		"version":        loadedModel.Metadata.Version,
		"model_type":     loadedModel.Metadata.ModelType,
		"loaded_at":      loadedModel.Metadata.LoadedAt,
		"last_access":    loadedModel.LastAccess,
		"request_count":  loadedModel.RequestCount,
		"avg_latency_ms": loadedModel.Metadata.AvgLatencyMs,
		"error_rate":     loadedModel.Metadata.ErrorRate,
		"is_active":      loadedModel.Metadata.IsActive,
	}
}

// HTTP handlers

// handlePredict handles HTTP prediction requests
func (s *ModelServer) handlePredict(w http.ResponseWriter, r *http.Request) {
	var req PredictionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}
	
	// Generate request ID if not provided
	if req.RequestID == "" {
		req.RequestID = fmt.Sprintf("req_%d", time.Now().UnixNano())
	}
	
	response := s.Predict(&req)
	
	w.Header().Set("Content-Type", "application/json")
	if response.Status == "error" {
		w.WriteHeader(http.StatusInternalServerError)
	}
	
	json.NewEncoder(w).Encode(response)
}

// handleStats handles statistics requests
func (s *ModelServer) handleStats(w http.ResponseWriter, r *http.Request) {
	stats := s.GetStats()
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

// handleModelStats handles model-specific statistics
func (s *ModelServer) handleModelStats(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	modelID := vars["modelId"]
	
	stats := s.GetModelStats(modelID)
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

// handleHealth handles health check requests
func (s *ModelServer) handleHealth(w http.ResponseWriter, r *http.Request) {
	health := map[string]interface{}{
		"status":    "healthy",
		"timestamp": time.Now(),
		"version":   "1.0.0",
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(health)
}

// Shutdown gracefully shuts down the server
func (s *ModelServer) Shutdown() {
	log.Println("Shutting down model server...")
	s.cancel()
}

func main() {
	fmt.Println("🚀 Starting Real-time Model Serving Demo")
	fmt.Println(strings.Repeat("=", 60))
	
	// Initialize model server
	server := NewModelServer(8) // 8 workers
	
	// Load sample models
	fmt.Println("\n📦 Loading sample models...")
	
	models := []*ModelMetadata{
		{
			ModelID:   "paytm_fraud_v1",
			Name:      "Paytm Fraud Detection",
			Version:   "1.0.0",
			ModelType: FraudDetection,
			Framework: "scikit-learn",
			Configuration: map[string]interface{}{
				"threshold": 0.5,
				"features":  4,
			},
		},
		{
			ModelID:   "flipkart_rec_v2",
			Name:      "Flipkart Product Recommendations",
			Version:   "2.0.0",
			ModelType: Recommendation,
			Framework: "tensorflow",
			Configuration: map[string]interface{}{
				"embedding_dim": 128,
				"top_k":         10,
			},
		},
		{
			ModelID:   "price_optimizer_v1",
			Name:      "Dynamic Price Optimizer",
			Version:   "1.0.0",
			ModelType: PriceOptimization,
			Framework: "xgboost",
			Configuration: map[string]interface{}{
				"max_price_change": 0.2,
			},
		},
		{
			ModelID:   "sentiment_analyzer_v1",
			Name:      "Customer Sentiment Analyzer",
			Version:   "1.0.0",
			ModelType: SentimentAnalysis,
			Framework: "bert",
			Configuration: map[string]interface{}{
				"max_length": 512,
			},
		},
	}
	
	for _, model := range models {
		if err := server.LoadModel(model); err != nil {
			log.Printf("Failed to load model %s: %v", model.ModelID, err)
		} else {
			fmt.Printf("  ✅ Loaded: %s (%s)\n", model.Name, model.ModelID)
		}
	}
	
	// Setup HTTP routes
	router := mux.NewRouter()
	router.HandleFunc("/predict", server.handlePredict).Methods("POST")
	router.HandleFunc("/stats", server.handleStats).Methods("GET")
	router.HandleFunc("/models/{modelId}/stats", server.handleModelStats).Methods("GET")
	router.HandleFunc("/health", server.handleHealth).Methods("GET")
	router.Handle("/metrics", promhttp.Handler()).Methods("GET")
	
	// Start HTTP server in goroutine
	go func() {
		fmt.Println("\n🌐 Starting HTTP server on :8080...")
		log.Fatal(http.ListenAndServe(":8080", router))
	}()
	
	// Wait for server to start
	time.Sleep(2 * time.Second)
	
	// Test predictions
	fmt.Println("\n🔮 Testing model predictions...")
	
	// Test fraud detection
	fmt.Println("\n  Testing Fraud Detection:")
	fraudReq := &PredictionRequest{
		ModelID:   "paytm_fraud_v1",
		RequestID: "test_fraud_1",
		InputData: map[string]interface{}{
			"amount":           15000.0,
			"user_age":         25.0,
			"transaction_hour": 23.0,
			"merchant_category": "online_retail",
		},
	}
	
	fraudResp := server.Predict(fraudReq)
	fmt.Printf("    Request ID: %s\n", fraudResp.RequestID)
	fmt.Printf("    Processing Time: %dms\n", fraudResp.ProcessingTimeMs)
	fmt.Printf("    Status: %s\n", fraudResp.Status)
	if fraudResp.Status == "success" {
		if prediction, ok := fraudResp.Prediction.(map[string]interface{}); ok {
			fmt.Printf("    Fraud Score: %.4f\n", prediction["fraud_score"])
			fmt.Printf("    Is Fraud: %v\n", prediction["is_fraud"])
		}
	}
	
	// Test recommendations
	fmt.Println("\n  Testing Product Recommendations:")
	recReq := &PredictionRequest{
		ModelID:   "flipkart_rec_v2",
		RequestID: "test_rec_1",
		InputData: map[string]interface{}{
			"user_id":  "user_12345",
			"category": "electronics",
		},
	}
	
	recResp := server.Predict(recReq)
	fmt.Printf("    Request ID: %s\n", recResp.RequestID)
	fmt.Printf("    Processing Time: %dms\n", recResp.ProcessingTimeMs)
	fmt.Printf("    Status: %s\n", recResp.Status)
	if recResp.Status == "success" {
		if prediction, ok := recResp.Prediction.(map[string]interface{}); ok {
			recs := prediction["recommendations"].([]map[string]interface{})
			fmt.Printf("    Recommendations: %d items\n", len(recs))
			fmt.Printf("    Top Item: %s (score: %.4f)\n", 
				recs[0]["item_id"], recs[0]["score"])
		}
	}
	
	// Test price optimization
	fmt.Println("\n  Testing Price Optimization:")
	priceReq := &PredictionRequest{
		ModelID:   "price_optimizer_v1",
		RequestID: "test_price_1",
		InputData: map[string]interface{}{
			"base_price":  999.99,
			"demand":      0.7,
			"competition": 0.4,
		},
	}
	
	priceResp := server.Predict(priceReq)
	fmt.Printf("    Request ID: %s\n", priceResp.RequestID)
	fmt.Printf("    Processing Time: %dms\n", priceResp.ProcessingTimeMs)
	fmt.Printf("    Status: %s\n", priceResp.Status)
	if priceResp.Status == "success" {
		if prediction, ok := priceResp.Prediction.(map[string]interface{}); ok {
			fmt.Printf("    Original Price: ₹%.2f\n", prediction["original_price"])
			fmt.Printf("    Optimized Price: ₹%.2f\n", prediction["optimized_price"])
			fmt.Printf("    Price Change: %.2f%%\n", prediction["price_change"])
		}
	}
	
	// Load test simulation
	fmt.Println("\n⚡ Running load test simulation...")
	
	start := time.Now()
	var wg sync.WaitGroup
	numRequests := 100
	
	wg.Add(numRequests)
	for i := 0; i < numRequests; i++ {
		go func(requestNum int) {
			defer wg.Done()
			
			// Randomly select a model to test
			modelIDs := []string{"paytm_fraud_v1", "flipkart_rec_v2", "price_optimizer_v1", "sentiment_analyzer_v1"}
			modelID := modelIDs[requestNum % len(modelIDs)]
			
			req := &PredictionRequest{
				ModelID:   modelID,
				RequestID: fmt.Sprintf("load_test_%d", requestNum),
				InputData: map[string]interface{}{
					"test_data": requestNum,
					"amount":    float64(1000 + requestNum*10),
					"user_id":   fmt.Sprintf("user_%d", requestNum),
				},
			}
			
			server.Predict(req)
		}(i)
	}
	
	wg.Wait()
	loadTestDuration := time.Since(start)
	
	fmt.Printf("Load test completed: %d requests in %v\n", numRequests, loadTestDuration)
	fmt.Printf("Throughput: %.2f requests/second\n", float64(numRequests)/loadTestDuration.Seconds())
	
	// Display final statistics
	fmt.Println("\n📊 Final Server Statistics:")
	stats := server.GetStats()
	
	fmt.Printf("  Total Requests: %v\n", stats["total_requests"])
	fmt.Printf("  Successful Requests: %v\n", stats["successful_requests"])
	fmt.Printf("  Failed Requests: %v\n", stats["failed_requests"])
	fmt.Printf("  Success Rate: %.2f%%\n", stats["success_rate"].(float64)*100)
	fmt.Printf("  Average Latency: %.2fms\n", stats["avg_latency_ms"])
	fmt.Printf("  Loaded Models: %v\n", stats["loaded_models"])
	fmt.Printf("  Workers: %v\n", stats["workers"])
	
	// Display model-specific statistics
	fmt.Println("\n📈 Model-specific Statistics:")
	for _, model := range models {
		modelStats := server.GetModelStats(model.ModelID)
		if _, hasError := modelStats["error"]; !hasError {
			fmt.Printf("\n  %s:\n", model.Name)
			fmt.Printf("    Request Count: %v\n", modelStats["request_count"])
			fmt.Printf("    Avg Latency: %.2fms\n", modelStats["avg_latency_ms"])
			fmt.Printf("    Error Rate: %.2f%%\n", modelStats["error_rate"].(float64)*100)
		}
	}
	
	fmt.Println("\n🌐 HTTP Server running on http://localhost:8080")
	fmt.Println("Available endpoints:")
	fmt.Println("  POST /predict - Make predictions")
	fmt.Println("  GET  /stats - Server statistics")
	fmt.Println("  GET  /models/{modelId}/stats - Model statistics")
	fmt.Println("  GET  /health - Health check")
	fmt.Println("  GET  /metrics - Prometheus metrics")
	
	fmt.Println("\n✅ Real-time model serving demo completed!")
	fmt.Println("Mumbai me real-time serving bhi express delivery ki tarah fast!")
	
	// Keep server running for a while
	fmt.Println("\nServer will run for 30 more seconds for testing...")
	time.Sleep(30 * time.Second)
	
	// Shutdown
	server.Shutdown()
	fmt.Println("Server shut down gracefully.")
}
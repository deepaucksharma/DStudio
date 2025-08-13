package main

/*
Batch Inference Pipeline - MLOps Episode 44
Production-ready batch inference system for large-scale ML predictions

Author: Claude Code
Context: High-throughput batch processing system for ML models like Flipkart's recommendation batch jobs
*/

import (
	"context"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"math"
	"math/rand"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/google/uuid"
)

// JobStatus represents the status of a batch job
type JobStatus string

const (
	JobPending    JobStatus = "pending"
	JobRunning    JobStatus = "running"
	JobCompleted  JobStatus = "completed"
	JobFailed     JobStatus = "failed"
	JobCancelled  JobStatus = "cancelled"
)

// BatchJobConfig represents configuration for a batch inference job
type BatchJobConfig struct {
	JobID              string            `json:"job_id"`
	JobName            string            `json:"job_name"`
	ModelID            string            `json:"model_id"`
	InputPath          string            `json:"input_path"`
	OutputPath         string            `json:"output_path"`
	BatchSize          int               `json:"batch_size"`
	MaxWorkers         int               `json:"max_workers"`
	TimeoutMinutes     int               `json:"timeout_minutes"`
	RetryAttempts      int               `json:"retry_attempts"`
	EnableCheckpointing bool             `json:"enable_checkpointing"`
	Metadata           map[string]string `json:"metadata"`
	CreatedAt          time.Time         `json:"created_at"`
	Priority           int               `json:"priority"` // 1=low, 5=high
}

// BatchJob represents a batch inference job
type BatchJob struct {
	Config           *BatchJobConfig    `json:"config"`
	Status           JobStatus          `json:"status"`
	StartTime        *time.Time         `json:"start_time,omitempty"`
	EndTime          *time.Time         `json:"end_time,omitempty"`
	ProcessedRecords int64              `json:"processed_records"`
	TotalRecords     int64              `json:"total_records"`
	SuccessRecords   int64              `json:"success_records"`
	FailedRecords    int64              `json:"failed_records"`
	Progress         float64            `json:"progress"`
	ErrorMessage     string             `json:"error_message,omitempty"`
	Checkpoints      []CheckpointInfo   `json:"checkpoints"`
	Performance      *PerformanceMetrics `json:"performance,omitempty"`
	mutex            sync.RWMutex       `json:"-"`
}

// CheckpointInfo represents a checkpoint in batch processing
type CheckpointInfo struct {
	RecordOffset  int64     `json:"record_offset"`
	Timestamp     time.Time `json:"timestamp"`
	CheckpointID  string    `json:"checkpoint_id"`
	FilePath      string    `json:"file_path"`
}

// PerformanceMetrics tracks job performance
type PerformanceMetrics struct {
	RecordsPerSecond    float64       `json:"records_per_second"`
	AvgProcessingTimeMs float64       `json:"avg_processing_time_ms"`
	TotalProcessingTime time.Duration `json:"total_processing_time"`
	MemoryUsageMB       float64       `json:"memory_usage_mb"`
	CPUUtilization      float64       `json:"cpu_utilization"`
	ThroughputMBps      float64       `json:"throughput_mbps"`
}

// BatchRecord represents a single record for processing
type BatchRecord struct {
	RecordID  string                 `json:"record_id"`
	Data      map[string]interface{} `json:"data"`
	Metadata  map[string]string      `json:"metadata,omitempty"`
}

// PredictionResult represents the result of a prediction
type PredictionResult struct {
	RecordID      string                 `json:"record_id"`
	Prediction    interface{}            `json:"prediction"`
	Confidence    float64                `json:"confidence,omitempty"`
	ProcessingTime time.Duration         `json:"processing_time"`
	Status        string                 `json:"status"`
	ErrorMessage  string                 `json:"error_message,omitempty"`
	Metadata      map[string]interface{} `json:"metadata,omitempty"`
}

// BatchInferencePipeline represents the main batch processing system
// Mumbai me sabse efficient batch processing ka system!
type BatchInferencePipeline struct {
	jobs          sync.Map // map[string]*BatchJob
	jobQueue      chan *BatchJob
	workers       []*BatchWorker
	numWorkers    int
	ctx           context.Context
	cancel        context.CancelFunc
	models        map[string]interface{} // Mock model registry
	resultWriters sync.Map               // map[string]*ResultWriter
	
	// Metrics
	totalJobs     int64
	completedJobs int64
	failedJobs    int64
	
	// Configuration
	maxConcurrentJobs int
	checkpointInterval time.Duration
}

// BatchWorker represents a worker that processes batch jobs
type BatchWorker struct {
	ID       int
	pipeline *BatchInferencePipeline
	ctx      context.Context
}

// ResultWriter handles writing results to output files
type ResultWriter struct {
	outputPath string
	writer     *csv.Writer
	file       *os.File
	mutex      sync.Mutex
}

// NewBatchInferencePipeline creates a new batch inference pipeline
func NewBatchInferencePipeline(numWorkers, maxConcurrentJobs int) *BatchInferencePipeline {
	ctx, cancel := context.WithCancel(context.Background())
	
	pipeline := &BatchInferencePipeline{
		numWorkers:         numWorkers,
		maxConcurrentJobs:  maxConcurrentJobs,
		jobQueue:           make(chan *BatchJob, maxConcurrentJobs),
		ctx:                ctx,
		cancel:             cancel,
		models:             make(map[string]interface{}),
		checkpointInterval: 5 * time.Minute,
	}
	
	// Initialize mock models
	pipeline.initializeModels()
	
	// Start workers
	for i := 0; i < numWorkers; i++ {
		worker := &BatchWorker{
			ID:       i,
			pipeline: pipeline,
			ctx:      ctx,
		}
		pipeline.workers = append(pipeline.workers, worker)
		go worker.start()
	}
	
	log.Printf("Batch inference pipeline initialized with %d workers", numWorkers)
	return pipeline
}

// initializeModels initializes mock models for demonstration
func (p *BatchInferencePipeline) initializeModels() {
	// Flipkart recommendation model
	p.models["flipkart_recommendation_v1"] = map[string]interface{}{
		"type":        "collaborative_filtering",
		"latency_ms":  50,
		"accuracy":    0.89,
		"top_k":       10,
	}
	
	// Paytm fraud detection model
	p.models["paytm_fraud_v1"] = map[string]interface{}{
		"type":        "random_forest",
		"latency_ms":  25,
		"accuracy":    0.94,
		"threshold":   0.5,
	}
	
	// Price optimization model
	p.models["price_optimizer_v1"] = map[string]interface{}{
		"type":        "gradient_boosting",
		"latency_ms":  35,
		"accuracy":    0.87,
	}
	
	// Customer segmentation model
	p.models["customer_segmentation_v1"] = map[string]interface{}{
		"type":        "kmeans",
		"latency_ms":  15,
		"clusters":    5,
	}
	
	log.Printf("Initialized %d models", len(p.models))
}

// SubmitJob submits a new batch job for processing
func (p *BatchInferencePipeline) SubmitJob(config *BatchJobConfig) (*BatchJob, error) {
	// Validate config
	if config.ModelID == "" || config.InputPath == "" || config.OutputPath == "" {
		return nil, fmt.Errorf("missing required fields: model_id, input_path, output_path")
	}
	
	// Check if model exists
	if _, exists := p.models[config.ModelID]; !exists {
		return nil, fmt.Errorf("model not found: %s", config.ModelID)
	}
	
	// Generate job ID if not provided
	if config.JobID == "" {
		config.JobID = uuid.New().String()
	}
	
	// Set defaults
	if config.BatchSize <= 0 {
		config.BatchSize = 100
	}
	if config.MaxWorkers <= 0 {
		config.MaxWorkers = runtime.NumCPU()
	}
	if config.TimeoutMinutes <= 0 {
		config.TimeoutMinutes = 60
	}
	if config.RetryAttempts < 0 {
		config.RetryAttempts = 3
	}
	if config.Priority <= 0 {
		config.Priority = 3 // Medium priority
	}
	
	config.CreatedAt = time.Now()
	
	// Create job
	job := &BatchJob{
		Config:      config,
		Status:      JobPending,
		Checkpoints: make([]CheckpointInfo, 0),
		Performance: &PerformanceMetrics{},
	}
	
	// Count total records
	totalRecords, err := p.countRecords(config.InputPath)
	if err != nil {
		return nil, fmt.Errorf("failed to count input records: %v", err)
	}
	job.TotalRecords = totalRecords
	
	// Store job
	p.jobs.Store(config.JobID, job)
	atomic.AddInt64(&p.totalJobs, 1)
	
	// Submit to queue
	select {
	case p.jobQueue <- job:
		log.Printf("Job submitted: %s (%s)", config.JobID, config.JobName)
		return job, nil
	default:
		return nil, fmt.Errorf("job queue is full")
	}
}

// countRecords counts the number of records in the input file
func (p *BatchInferencePipeline) countRecords(inputPath string) (int64, error) {
	file, err := os.Open(inputPath)
	if err != nil {
		return 0, err
	}
	defer file.Close()
	
	reader := csv.NewReader(file)
	
	var count int64
	for {
		_, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return 0, err
		}
		count++
	}
	
	// Subtract 1 for header row
	if count > 0 {
		count--
	}
	
	return count, nil
}

// GetJob returns a job by ID
func (p *BatchInferencePipeline) GetJob(jobID string) (*BatchJob, error) {
	jobInterface, exists := p.jobs.Load(jobID)
	if !exists {
		return nil, fmt.Errorf("job not found: %s", jobID)
	}
	
	return jobInterface.(*BatchJob), nil
}

// ListJobs returns all jobs with optional status filter
func (p *BatchInferencePipeline) ListJobs(status JobStatus) []*BatchJob {
	var jobs []*BatchJob
	
	p.jobs.Range(func(key, value interface{}) bool {
		job := value.(*BatchJob)
		job.mutex.RLock()
		jobStatus := job.Status
		job.mutex.RUnlock()
		
		if status == "" || jobStatus == status {
			jobs = append(jobs, job)
		}
		return true
	})
	
	return jobs
}

// CancelJob cancels a running job
func (p *BatchInferencePipeline) CancelJob(jobID string) error {
	jobInterface, exists := p.jobs.Load(jobID)
	if !exists {
		return fmt.Errorf("job not found: %s", jobID)
	}
	
	job := jobInterface.(*BatchJob)
	job.mutex.Lock()
	defer job.mutex.Unlock()
	
	if job.Status == JobRunning {
		job.Status = JobCancelled
		job.EndTime = &[]time.Time{time.Now()}[0]
		log.Printf("Job cancelled: %s", jobID)
		return nil
	}
	
	return fmt.Errorf("job cannot be cancelled in status: %s", job.Status)
}

// BatchWorker.start starts the worker processing loop
func (w *BatchWorker) start() {
	log.Printf("Batch worker %d started", w.ID)
	
	for {
		select {
		case job := <-w.pipeline.jobQueue:
			w.processJob(job)
		case <-w.ctx.Done():
			log.Printf("Batch worker %d stopped", w.ID)
			return
		}
	}
}

// processJob processes a single batch job
func (w *BatchWorker) processJob(job *BatchJob) {
	log.Printf("Worker %d processing job: %s", w.ID, job.Config.JobID)
	
	// Update job status
	job.mutex.Lock()
	job.Status = JobRunning
	startTime := time.Now()
	job.StartTime = &startTime
	job.mutex.Unlock()
	
	// Setup result writer
	resultWriter, err := w.setupResultWriter(job)
	if err != nil {
		w.failJob(job, fmt.Sprintf("Failed to setup result writer: %v", err))
		return
	}
	defer resultWriter.close()
	
	// Process records
	err = w.processRecords(job, resultWriter)
	
	// Update final status
	job.mutex.Lock()
	endTime := time.Now()
	job.EndTime = &endTime
	
	if err != nil {
		job.Status = JobFailed
		job.ErrorMessage = err.Error()
		atomic.AddInt64(&w.pipeline.failedJobs, 1)
		log.Printf("Job failed: %s - %v", job.Config.JobID, err)
	} else {
		job.Status = JobCompleted
		atomic.AddInt64(&w.pipeline.completedJobs, 1)
		log.Printf("Job completed: %s", job.Config.JobID)
	}
	
	// Calculate final performance metrics
	w.calculatePerformanceMetrics(job)
	job.mutex.Unlock()
}

// setupResultWriter creates a result writer for the job
func (w *BatchWorker) setupResultWriter(job *BatchJob) (*ResultWriter, error) {
	// Create output directory if it doesn't exist
	outputDir := filepath.Dir(job.Config.OutputPath)
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return nil, err
	}
	
	file, err := os.Create(job.Config.OutputPath)
	if err != nil {
		return nil, err
	}
	
	writer := csv.NewWriter(file)
	
	// Write header
	header := []string{"record_id", "prediction", "confidence", "processing_time_ms", "status", "error_message"}
	if err := writer.Write(header); err != nil {
		file.Close()
		return nil, err
	}
	
	resultWriter := &ResultWriter{
		outputPath: job.Config.OutputPath,
		writer:     writer,
		file:       file,
	}
	
	w.pipeline.resultWriters.Store(job.Config.JobID, resultWriter)
	
	return resultWriter, nil
}

// processRecords processes all records in the input file
func (w *BatchWorker) processRecords(job *BatchJob, resultWriter *ResultWriter) error {
	file, err := os.Open(job.Config.InputPath)
	if err != nil {
		return fmt.Errorf("failed to open input file: %v", err)
	}
	defer file.Close()
	
	reader := csv.NewReader(file)
	
	// Read header
	header, err := reader.Read()
	if err != nil {
		return fmt.Errorf("failed to read header: %v", err)
	}
	
	// Process records in batches
	var batch []BatchRecord
	var recordOffset int64
	
	for {
		record, err := reader.Read()
		if err == io.EOF {
			// Process remaining batch
			if len(batch) > 0 {
				w.processBatch(job, batch, resultWriter)
			}
			break
		}
		if err != nil {
			return fmt.Errorf("failed to read record: %v", err)
		}
		
		// Convert CSV record to BatchRecord
		batchRecord := w.csvRecordToBatchRecord(header, record, recordOffset)
		batch = append(batch, batchRecord)
		recordOffset++
		
		// Process batch when it reaches the configured size
		if len(batch) >= job.Config.BatchSize {
			w.processBatch(job, batch, resultWriter)
			batch = batch[:0] // Clear batch
			
			// Create checkpoint
			if job.Config.EnableCheckpointing {
				w.createCheckpoint(job, recordOffset)
			}
			
			// Check for cancellation
			job.mutex.RLock()
			status := job.Status
			job.mutex.RUnlock()
			
			if status == JobCancelled {
				return fmt.Errorf("job was cancelled")
			}
		}
	}
	
	return nil
}

// csvRecordToBatchRecord converts a CSV record to a BatchRecord
func (w *BatchWorker) csvRecordToBatchRecord(header []string, record []string, offset int64) BatchRecord {
	data := make(map[string]interface{})
	
	for i, value := range record {
		if i < len(header) {
			// Try to parse as number, fall back to string
			if floatVal, err := strconv.ParseFloat(value, 64); err == nil {
				data[header[i]] = floatVal
			} else {
				data[header[i]] = value
			}
		}
	}
	
	return BatchRecord{
		RecordID: fmt.Sprintf("record_%d", offset),
		Data:     data,
		Metadata: map[string]string{
			"offset": strconv.FormatInt(offset, 10),
		},
	}
}

// processBatch processes a batch of records
func (w *BatchWorker) processBatch(job *BatchJob, batch []BatchRecord, resultWriter *ResultWriter) {
	var wg sync.WaitGroup
	
	// Limit concurrency to prevent overwhelming the system
	maxConcurrency := min(job.Config.MaxWorkers, len(batch))
	semaphore := make(chan struct{}, maxConcurrency)
	
	for _, record := range batch {
		wg.Add(1)
		
		go func(rec BatchRecord) {
			defer wg.Done()
			
			// Acquire semaphore
			semaphore <- struct{}{}
			defer func() { <-semaphore }()
			
			// Process single record
			result := w.processRecord(job, rec)
			
			// Write result
			w.writeResult(resultWriter, result)
			
			// Update job metrics
			job.mutex.Lock()
			job.ProcessedRecords++
			if result.Status == "success" {
				job.SuccessRecords++
			} else {
				job.FailedRecords++
			}
			job.Progress = float64(job.ProcessedRecords) / float64(job.TotalRecords)
			job.mutex.Unlock()
			
		}(record)
	}
	
	wg.Wait()
}

// processRecord processes a single record
func (w *BatchWorker) processRecord(job *BatchJob, record BatchRecord) PredictionResult {
	startTime := time.Now()
	
	// Get model
	model := w.pipeline.models[job.Config.ModelID]
	
	// Simulate model inference
	prediction, confidence, err := w.runInference(model, record.Data)
	
	processingTime := time.Since(startTime)
	
	result := PredictionResult{
		RecordID:       record.RecordID,
		ProcessingTime: processingTime,
		Metadata: map[string]interface{}{
			"model_id": job.Config.ModelID,
			"batch_id": job.Config.JobID,
		},
	}
	
	if err != nil {
		result.Status = "error"
		result.ErrorMessage = err.Error()
	} else {
		result.Status = "success"
		result.Prediction = prediction
		result.Confidence = confidence
	}
	
	return result
}

// runInference simulates model inference
func (w *BatchWorker) runInference(model interface{}, data map[string]interface{}) (interface{}, float64, error) {
	modelConfig := model.(map[string]interface{})
	modelType := modelConfig["type"].(string)
	latency := int(modelConfig["latency_ms"].(int))
	
	// Simulate processing time
	time.Sleep(time.Duration(latency) * time.Millisecond)
	
	switch modelType {
	case "collaborative_filtering":
		return w.simulateRecommendation(data), 0.85 + rand.Float64()*0.15, nil
		
	case "random_forest":
		return w.simulateFraudDetection(data), 0.80 + rand.Float64()*0.20, nil
		
	case "gradient_boosting":
		return w.simulatePriceOptimization(data), 0.75 + rand.Float64()*0.25, nil
		
	case "kmeans":
		return w.simulateCustomerSegmentation(data), 0.90 + rand.Float64()*0.10, nil
		
	default:
		return nil, 0.0, fmt.Errorf("unsupported model type: %s", modelType)
	}
}

// simulateRecommendation simulates recommendation prediction
func (w *BatchWorker) simulateRecommendation(data map[string]interface{}) interface{} {
	userID, _ := data["user_id"].(string)
	
	// Generate mock recommendations
	recommendations := make([]map[string]interface{}, 10)
	for i := 0; i < 10; i++ {
		recommendations[i] = map[string]interface{}{
			"item_id": fmt.Sprintf("item_%d", rand.Intn(10000)),
			"score":   rand.Float64() * 0.5 + 0.5,
			"rank":    i + 1,
		}
	}
	
	return map[string]interface{}{
		"user_id":        userID,
		"recommendations": recommendations[:5], // Top 5
	}
}

// simulateFraudDetection simulates fraud detection prediction
func (w *BatchWorker) simulateFraudDetection(data map[string]interface{}) interface{} {
	amount, _ := data["amount"].(float64)
	
	// Simple fraud scoring logic
	fraudScore := 0.0
	if amount > 10000 {
		fraudScore += 0.4
	}
	fraudScore += rand.Float64() * 0.3
	
	return map[string]interface{}{
		"is_fraud":    fraudScore > 0.5,
		"fraud_score": math.Min(fraudScore, 1.0),
		"risk_level":  w.getRiskLevel(fraudScore),
	}
}

// simulatePriceOptimization simulates price optimization prediction
func (w *BatchWorker) simulatePriceOptimization(data map[string]interface{}) interface{} {
	basePrice, _ := data["base_price"].(float64)
	demand := 0.5 + rand.Float64()*0.5
	
	optimizedPrice := basePrice * (0.8 + demand*0.4)
	
	return map[string]interface{}{
		"original_price":  basePrice,
		"optimized_price": math.Round(optimizedPrice*100) / 100,
		"demand_factor":   demand,
		"price_change":    (optimizedPrice - basePrice) / basePrice,
	}
}

// simulateCustomerSegmentation simulates customer segmentation prediction
func (w *BatchWorker) simulateCustomerSegmentation(data map[string]interface{}) interface{} {
	segments := []string{"premium", "regular", "budget", "new", "inactive"}
	probabilities := make([]float64, len(segments))
	
	for i := range probabilities {
		probabilities[i] = rand.Float64()
	}
	
	// Normalize probabilities
	sum := 0.0
	for _, p := range probabilities {
		sum += p
	}
	for i := range probabilities {
		probabilities[i] /= sum
	}
	
	// Find max probability segment
	maxIdx := 0
	maxProb := probabilities[0]
	for i, prob := range probabilities {
		if prob > maxProb {
			maxProb = prob
			maxIdx = i
		}
	}
	
	return map[string]interface{}{
		"segment":      segments[maxIdx],
		"confidence":   maxProb,
		"probabilities": map[string]float64{
			"premium":  probabilities[0],
			"regular":  probabilities[1],
			"budget":   probabilities[2],
			"new":      probabilities[3],
			"inactive": probabilities[4],
		},
	}
}

// getRiskLevel converts fraud score to risk level
func (w *BatchWorker) getRiskLevel(score float64) string {
	if score > 0.8 {
		return "high"
	} else if score > 0.5 {
		return "medium"
	}
	return "low"
}

// writeResult writes a prediction result to the output file
func (w *BatchWorker) writeResult(resultWriter *ResultWriter, result PredictionResult) {
	resultWriter.mutex.Lock()
	defer resultWriter.mutex.Unlock()
	
	// Convert prediction to JSON string
	predictionJSON, _ := json.Marshal(result.Prediction)
	
	record := []string{
		result.RecordID,
		string(predictionJSON),
		fmt.Sprintf("%.4f", result.Confidence),
		fmt.Sprintf("%.2f", float64(result.ProcessingTime.Nanoseconds())/1e6),
		result.Status,
		result.ErrorMessage,
	}
	
	resultWriter.writer.Write(record)
	resultWriter.writer.Flush()
}

// createCheckpoint creates a checkpoint for the job
func (w *BatchWorker) createCheckpoint(job *BatchJob, recordOffset int64) {
	checkpoint := CheckpointInfo{
		RecordOffset: recordOffset,
		Timestamp:    time.Now(),
		CheckpointID: fmt.Sprintf("checkpoint_%d", time.Now().Unix()),
		FilePath:     fmt.Sprintf("%s.checkpoint_%d", job.Config.OutputPath, recordOffset),
	}
	
	job.mutex.Lock()
	job.Checkpoints = append(job.Checkpoints, checkpoint)
	job.mutex.Unlock()
	
	log.Printf("Created checkpoint for job %s at offset %d", job.Config.JobID, recordOffset)
}

// calculatePerformanceMetrics calculates final performance metrics
func (w *BatchWorker) calculatePerformanceMetrics(job *BatchJob) {
	if job.StartTime == nil || job.EndTime == nil {
		return
	}
	
	duration := job.EndTime.Sub(*job.StartTime)
	
	if duration.Seconds() > 0 {
		job.Performance.RecordsPerSecond = float64(job.ProcessedRecords) / duration.Seconds()
		job.Performance.TotalProcessingTime = duration
		job.Performance.AvgProcessingTimeMs = duration.Seconds() * 1000 / float64(job.ProcessedRecords)
	}
	
	// Simulate memory and CPU metrics
	job.Performance.MemoryUsageMB = 100.0 + rand.Float64()*200.0
	job.Performance.CPUUtilization = 0.4 + rand.Float64()*0.4
	job.Performance.ThroughputMBps = 5.0 + rand.Float64()*10.0
}

// failJob marks a job as failed
func (w *BatchWorker) failJob(job *BatchJob, errorMessage string) {
	job.mutex.Lock()
	defer job.mutex.Unlock()
	
	job.Status = JobFailed
	job.ErrorMessage = errorMessage
	endTime := time.Now()
	job.EndTime = &endTime
	
	atomic.AddInt64(&w.pipeline.failedJobs, 1)
	log.Printf("Job failed: %s - %s", job.Config.JobID, errorMessage)
}

// ResultWriter.close closes the result writer
func (rw *ResultWriter) close() {
	rw.writer.Flush()
	rw.file.Close()
}

// GetStats returns pipeline statistics
func (p *BatchInferencePipeline) GetStats() map[string]interface{} {
	totalJobs := atomic.LoadInt64(&p.totalJobs)
	completedJobs := atomic.LoadInt64(&p.completedJobs)
	failedJobs := atomic.LoadInt64(&p.failedJobs)
	
	var runningJobs int64
	p.jobs.Range(func(key, value interface{}) bool {
		job := value.(*BatchJob)
		job.mutex.RLock()
		if job.Status == JobRunning {
			runningJobs++
		}
		job.mutex.RUnlock()
		return true
	})
	
	var successRate float64
	if totalJobs > 0 {
		successRate = float64(completedJobs) / float64(totalJobs)
	}
	
	return map[string]interface{}{
		"total_jobs":     totalJobs,
		"completed_jobs": completedJobs,
		"failed_jobs":    failedJobs,
		"running_jobs":   runningJobs,
		"success_rate":   successRate,
		"num_workers":    p.numWorkers,
		"queue_size":     len(p.jobQueue),
		"max_queue_size": cap(p.jobQueue),
	}
}

// Shutdown gracefully shuts down the pipeline
func (p *BatchInferencePipeline) Shutdown() {
	log.Println("Shutting down batch inference pipeline...")
	p.cancel()
	
	// Close all result writers
	p.resultWriters.Range(func(key, value interface{}) bool {
		resultWriter := value.(*ResultWriter)
		resultWriter.close()
		return true
	})
}

// Helper function
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// generateSampleData creates sample CSV data for testing
func generateSampleData(filename string, recordCount int, modelType string) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()
	
	writer := csv.NewWriter(file)
	defer writer.Flush()
	
	var header []string
	var generateRecord func(i int) []string
	
	switch modelType {
	case "recommendation":
		header = []string{"user_id", "category", "last_purchase_days", "avg_rating"}
		generateRecord = func(i int) []string {
			return []string{
				fmt.Sprintf("user_%d", i),
				[]string{"electronics", "fashion", "books", "home"}[i%4],
				strconv.Itoa(rand.Intn(365)),
				fmt.Sprintf("%.2f", 1.0+rand.Float64()*4.0),
			}
		}
		
	case "fraud":
		header = []string{"transaction_id", "user_id", "amount", "merchant_type", "hour"}
		generateRecord = func(i int) []string {
			return []string{
				fmt.Sprintf("txn_%d", i),
				fmt.Sprintf("user_%d", rand.Intn(1000)),
				fmt.Sprintf("%.2f", 10.0+rand.Float64()*10000.0),
				[]string{"retail", "gas", "restaurant", "online"}[rand.Intn(4)],
				strconv.Itoa(rand.Intn(24)),
			}
		}
		
	case "price":
		header = []string{"product_id", "base_price", "competitor_price", "inventory", "demand"}
		generateRecord = func(i int) []string {
			basePrice := 100.0 + rand.Float64()*1000.0
			return []string{
				fmt.Sprintf("prod_%d", i),
				fmt.Sprintf("%.2f", basePrice),
				fmt.Sprintf("%.2f", basePrice*(0.8+rand.Float64()*0.4)),
				strconv.Itoa(rand.Intn(100)),
				fmt.Sprintf("%.2f", rand.Float64()),
			}
		}
		
	default: // customer segmentation
		header = []string{"customer_id", "age", "income", "purchases_last_year", "avg_order_value"}
		generateRecord = func(i int) []string {
			return []string{
				fmt.Sprintf("cust_%d", i),
				strconv.Itoa(18 + rand.Intn(62)),
				strconv.Itoa(25000 + rand.Intn(75000)),
				strconv.Itoa(rand.Intn(50)),
				fmt.Sprintf("%.2f", 50.0+rand.Float64()*500.0),
			}
		}
	}
	
	// Write header
	if err := writer.Write(header); err != nil {
		return err
	}
	
	// Write records
	for i := 0; i < recordCount; i++ {
		record := generateRecord(i)
		if err := writer.Write(record); err != nil {
			return err
		}
	}
	
	return nil
}

func main() {
	fmt.Println("📊 Starting Batch Inference Pipeline Demo")
	fmt.Println(strings.Repeat("=", 60))
	
	// Initialize pipeline
	pipeline := NewBatchInferencePipeline(4, 10) // 4 workers, max 10 concurrent jobs
	
	// Create sample data files
	fmt.Println("\n📁 Creating sample data files...")
	
	dataFiles := []struct {
		filename  string
		modelType string
		records   int
	}{
		{"recommendation_data.csv", "recommendation", 1000},
		{"fraud_data.csv", "fraud", 500},
		{"price_data.csv", "price", 300},
		{"segmentation_data.csv", "segmentation", 800},
	}
	
	for _, dataFile := range dataFiles {
		if err := generateSampleData(dataFile.filename, dataFile.records, dataFile.modelType); err != nil {
			log.Printf("Failed to create %s: %v", dataFile.filename, err)
		} else {
			fmt.Printf("  ✅ Created: %s (%d records)\n", dataFile.filename, dataFile.records)
		}
	}
	
	// Submit batch jobs
	fmt.Println("\n🚀 Submitting batch jobs...")
	
	jobs := []*BatchJobConfig{
		{
			JobName:             "Flipkart Product Recommendations",
			ModelID:             "flipkart_recommendation_v1",
			InputPath:           "recommendation_data.csv",
			OutputPath:          "output/recommendations_output.csv",
			BatchSize:           50,
			MaxWorkers:          2,
			TimeoutMinutes:      30,
			EnableCheckpointing: true,
			Priority:            5, // High priority
			Metadata: map[string]string{
				"team":        "recommendation",
				"environment": "production",
			},
		},
		{
			JobName:             "Paytm Fraud Detection",
			ModelID:             "paytm_fraud_v1",
			InputPath:           "fraud_data.csv",
			OutputPath:          "output/fraud_output.csv",
			BatchSize:           25,
			MaxWorkers:          3,
			TimeoutMinutes:      20,
			EnableCheckpointing: false,
			Priority:            4, // High priority
			Metadata: map[string]string{
				"team":        "fraud",
				"environment": "production",
			},
		},
		{
			JobName:             "Price Optimization",
			ModelID:             "price_optimizer_v1",
			InputPath:           "price_data.csv",
			OutputPath:          "output/price_output.csv",
			BatchSize:           30,
			MaxWorkers:          2,
			TimeoutMinutes:      15,
			EnableCheckpointing: true,
			Priority:            3, // Medium priority
			Metadata: map[string]string{
				"team":        "pricing",
				"environment": "staging",
			},
		},
		{
			JobName:             "Customer Segmentation",
			ModelID:             "customer_segmentation_v1",
			InputPath:           "segmentation_data.csv",
			OutputPath:          "output/segmentation_output.csv",
			BatchSize:           40,
			MaxWorkers:          2,
			TimeoutMinutes:      25,
			EnableCheckpointing: false,
			Priority:            2, // Low priority
			Metadata: map[string]string{
				"team":        "analytics",
				"environment": "development",
			},
		},
	}
	
	var submittedJobs []*BatchJob
	for _, jobConfig := range jobs {
		job, err := pipeline.SubmitJob(jobConfig)
		if err != nil {
			log.Printf("Failed to submit job %s: %v", jobConfig.JobName, err)
		} else {
			submittedJobs = append(submittedJobs, job)
			fmt.Printf("  ✅ Submitted: %s (ID: %s)\n", jobConfig.JobName, job.Config.JobID)
		}
	}
	
	// Monitor job progress
	fmt.Println("\n📈 Monitoring job progress...")
	
	for len(submittedJobs) > 0 {
		time.Sleep(2 * time.Second)
		
		fmt.Printf("\nJob Status Update:\n")
		
		// Check job statuses
		var stillRunning []*BatchJob
		for _, job := range submittedJobs {
			job.mutex.RLock()
			status := job.Status
			progress := job.Progress
			processedRecords := job.ProcessedRecords
			totalRecords := job.TotalRecords
			job.mutex.RUnlock()
			
			fmt.Printf("  %s: %s (%.1f%% - %d/%d records)\n", 
				job.Config.JobName, status, progress*100, processedRecords, totalRecords)
			
			if status == JobRunning || status == JobPending {
				stillRunning = append(stillRunning, job)
			}
		}
		
		submittedJobs = stillRunning
		
		// Display pipeline stats
		stats := pipeline.GetStats()
		fmt.Printf("\nPipeline Stats: Running: %v, Completed: %v, Failed: %v, Queue: %v/%v\n",
			stats["running_jobs"], stats["completed_jobs"], stats["failed_jobs"],
			stats["queue_size"], stats["max_queue_size"])
	}
	
	// Display final results
	fmt.Println("\n📊 Final Job Results:")
	
	for _, jobConfig := range jobs {
		if job, err := pipeline.GetJob(jobConfig.JobID); err == nil {
			job.mutex.RLock()
			status := job.Status
			processedRecords := job.ProcessedRecords
			successRecords := job.SuccessRecords
			failedRecords := job.FailedRecords
			performance := job.Performance
			var duration time.Duration
			if job.StartTime != nil && job.EndTime != nil {
				duration = job.EndTime.Sub(*job.StartTime)
			}
			job.mutex.RUnlock()
			
			fmt.Printf("\n  %s:\n", jobConfig.JobName)
			fmt.Printf("    Status: %s\n", status)
			fmt.Printf("    Processed: %d records\n", processedRecords)
			fmt.Printf("    Success: %d, Failed: %d\n", successRecords, failedRecords)
			fmt.Printf("    Duration: %v\n", duration)
			
			if performance != nil && performance.RecordsPerSecond > 0 {
				fmt.Printf("    Throughput: %.2f records/sec\n", performance.RecordsPerSecond)
				fmt.Printf("    Avg Processing Time: %.2fms\n", performance.AvgProcessingTimeMs)
				fmt.Printf("    Memory Usage: %.2fMB\n", performance.MemoryUsageMB)
				fmt.Printf("    CPU Utilization: %.1f%%\n", performance.CPUUtilization*100)
			}
		}
	}
	
	// Display final pipeline statistics
	fmt.Println("\n📈 Final Pipeline Statistics:")
	finalStats := pipeline.GetStats()
	fmt.Printf("  Total Jobs: %v\n", finalStats["total_jobs"])
	fmt.Printf("  Completed Jobs: %v\n", finalStats["completed_jobs"])
	fmt.Printf("  Failed Jobs: %v\n", finalStats["failed_jobs"])
	fmt.Printf("  Success Rate: %.2f%%\n", finalStats["success_rate"].(float64)*100)
	fmt.Printf("  Workers: %v\n", finalStats["num_workers"])
	
	// Check output files
	fmt.Println("\n📂 Output Files Created:")
	for _, jobConfig := range jobs {
		if _, err := os.Stat(jobConfig.OutputPath); err == nil {
			fmt.Printf("  ✅ %s\n", jobConfig.OutputPath)
		} else {
			fmt.Printf("  ❌ %s (not created)\n", jobConfig.OutputPath)
		}
	}
	
	fmt.Println("\n✅ Batch inference pipeline demo completed!")
	fmt.Println("Mumbai me batch processing bhi assembly line ki tarah efficient!")
	
	// Cleanup
	pipeline.Shutdown()
	
	// Clean up sample files
	fmt.Println("\n🧹 Cleaning up sample files...")
	for _, dataFile := range dataFiles {
		os.Remove(dataFile.filename)
	}
	
	// Remove output directory
	os.RemoveAll("output")
}
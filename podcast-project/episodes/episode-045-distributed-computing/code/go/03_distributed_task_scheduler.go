package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"sort"
	"sync"
	"sync/atomic"
	"time"
)

/*
Distributed Task Scheduler for Large-Scale Systems
जैसे कि Flipkart के order processing और inventory updates में use होता है

यह example दिखाता है कि कैसे distributed task scheduling work करती है
large-scale e-commerce systems में। Flipkart जैसी companies इसे use करती हैं
millions of orders, inventory updates, और background jobs को efficiently
schedule और execute करने के लिए।

Production context: Flipkart schedules 10M+ tasks daily across distributed workers
Scale: Tasks distributed across hundreds of worker nodes for parallel execution
Challenge: Ensuring reliability, ordering, and fault tolerance in task execution
*/

// TaskPriority defines task priority levels
type TaskPriority int

const (
	PriorityLow TaskPriority = iota
	PriorityNormal
	PriorityHigh
	PriorityCritical
)

func (p TaskPriority) String() string {
	switch p {
	case PriorityLow:
		return "LOW"
	case PriorityNormal:
		return "NORMAL"
	case PriorityHigh:
		return "HIGH"
	case PriorityCritical:
		return "CRITICAL"
	default:
		return "UNKNOWN"
	}
}

// TaskStatus defines task execution status
type TaskStatus int

const (
	TaskStatusPending TaskStatus = iota
	TaskStatusRunning
	TaskStatusCompleted
	TaskStatusFailed
	TaskStatusRetrying
	TaskStatusCancelled
)

func (s TaskStatus) String() string {
	switch s {
	case TaskStatusPending:
		return "PENDING"
	case TaskStatusRunning:
		return "RUNNING"
	case TaskStatusCompleted:
		return "COMPLETED"
	case TaskStatusFailed:
		return "FAILED"
	case TaskStatusRetrying:
		return "RETRYING"
	case TaskStatusCancelled:
		return "CANCELLED"
	default:
		return "UNKNOWN"
	}
}

// Task represents a unit of work to be executed
type Task struct {
	ID              string                 `json:"id"`
	Type            string                 `json:"type"`
	Priority        TaskPriority           `json:"priority"`
	Payload         map[string]interface{} `json:"payload"`
	ScheduledAt     time.Time              `json:"scheduled_at"`
	CreatedAt       time.Time              `json:"created_at"`
	StartedAt       *time.Time             `json:"started_at,omitempty"`
	CompletedAt     *time.Time             `json:"completed_at,omitempty"`
	Status          TaskStatus             `json:"status"`
	RetryCount      int                    `json:"retry_count"`
	MaxRetries      int                    `json:"max_retries"`
	Timeout         time.Duration          `json:"timeout"`
	Dependencies    []string               `json:"dependencies"`
	AssignedWorker  string                 `json:"assigned_worker,omitempty"`
	ErrorMessage    string                 `json:"error_message,omitempty"`
	Result          interface{}            `json:"result,omitempty"`
	ExecutionTime   time.Duration          `json:"execution_time"`
	Mutex           sync.RWMutex           `json:"-"`
}

// NewTask creates a new task
func NewTask(id, taskType string, priority TaskPriority, payload map[string]interface{}) *Task {
	return &Task{
		ID:          id,
		Type:        taskType,
		Priority:    priority,
		Payload:     payload,
		ScheduledAt: time.Now(),
		CreatedAt:   time.Now(),
		Status:      TaskStatusPending,
		MaxRetries:  3,
		Timeout:     5 * time.Minute,
		Dependencies: make([]string, 0),
	}
}

// UpdateStatus updates task status with thread safety
func (t *Task) UpdateStatus(status TaskStatus) {
	t.Mutex.Lock()
	defer t.Mutex.Unlock()
	
	t.Status = status
	now := time.Now()
	
	switch status {
	case TaskStatusRunning:
		t.StartedAt = &now
	case TaskStatusCompleted, TaskStatusFailed, TaskStatusCancelled:
		t.CompletedAt = &now
		if t.StartedAt != nil {
			t.ExecutionTime = now.Sub(*t.StartedAt)
		}
	}
}

// IsReady checks if task is ready for execution (dependencies satisfied)
func (t *Task) IsReady(completedTasks map[string]bool) bool {
	t.Mutex.RLock()
	defer t.Mutex.RUnlock()
	
	if t.Status != TaskStatusPending && t.Status != TaskStatusRetrying {
		return false
	}
	
	if time.Now().Before(t.ScheduledAt) {
		return false
	}
	
	// Check dependencies
	for _, depID := range t.Dependencies {
		if !completedTasks[depID] {
			return false
		}
	}
	
	return true
}

// WorkerNode represents a distributed worker that executes tasks
type WorkerNode struct {
	ID               string
	Region           string
	Zone             string
	Capacity         int
	CurrentLoad      int32
	IsHealthy        bool
	LastHeartbeat    time.Time
	TasksExecuted    int64
	TasksSuccessful  int64
	TasksFailed      int64
	AvgExecutionTime time.Duration
	CPUUsage         float64
	MemoryUsage      float64
	Specializations  []string // Task types this worker can handle
	Mutex            sync.RWMutex
	
	// Worker state
	TaskQueue      chan *Task
	ResultChannel  chan *TaskResult
	StopChannel    chan struct{}
	IsRunning      bool
	
	ctx    context.Context
	cancel context.CancelFunc
}

// TaskResult represents the result of task execution
type TaskResult struct {
	TaskID        string        `json:"task_id"`
	WorkerID      string        `json:"worker_id"`
	Status        TaskStatus    `json:"status"`
	Result        interface{}   `json:"result,omitempty"`
	ErrorMessage  string        `json:"error_message,omitempty"`
	ExecutionTime time.Duration `json:"execution_time"`
	CompletedAt   time.Time     `json:"completed_at"`
}

// NewWorkerNode creates a new worker node
func NewWorkerNode(id, region, zone string, capacity int, specializations []string) *WorkerNode {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &WorkerNode{
		ID:              id,
		Region:          region,
		Zone:            zone,
		Capacity:        capacity,
		IsHealthy:       true,
		LastHeartbeat:   time.Now(),
		Specializations: specializations,
		TaskQueue:       make(chan *Task, capacity*2),
		ResultChannel:   make(chan *TaskResult, capacity),
		StopChannel:     make(chan struct{}),
		ctx:             ctx,
		cancel:          cancel,
	}
}

// Start begins worker execution
func (w *WorkerNode) Start() {
	w.Mutex.Lock()
	defer w.Mutex.Unlock()
	
	if w.IsRunning {
		return
	}
	
	w.IsRunning = true
	w.LastHeartbeat = time.Now()
	
	// Start worker goroutines
	for i := 0; i < w.Capacity; i++ {
		go w.taskExecutionWorker(i)
	}
	
	// Start heartbeat goroutine
	go w.heartbeatWorker()
	
	log.Printf("[%s] Worker node started in %s/%s with %d capacity", 
		w.ID, w.Region, w.Zone, w.Capacity)
}

// Stop gracefully shuts down the worker
func (w *WorkerNode) Stop() {
	w.Mutex.Lock()
	defer w.Mutex.Unlock()
	
	if !w.IsRunning {
		return
	}
	
	w.IsRunning = false
	w.cancel()
	close(w.StopChannel)
	
	log.Printf("[%s] Worker node stopping", w.ID)
}

// AssignTask assigns a task to this worker
func (w *WorkerNode) AssignTask(task *Task) bool {
	w.Mutex.RLock()
	defer w.Mutex.RUnlock()
	
	if !w.IsRunning || !w.IsHealthy {
		return false
	}
	
	if atomic.LoadInt32(&w.CurrentLoad) >= int32(w.Capacity) {
		return false
	}
	
	// Check if worker can handle this task type
	canHandle := false
	for _, spec := range w.Specializations {
		if spec == task.Type || spec == "*" {
			canHandle = true
			break
		}
	}
	
	if !canHandle {
		return false
	}
	
	select {
	case w.TaskQueue <- task:
		task.AssignedWorker = w.ID
		atomic.AddInt32(&w.CurrentLoad, 1)
		return true
	default:
		return false // Queue full
	}
}

// taskExecutionWorker executes tasks from the queue
func (w *WorkerNode) taskExecutionWorker(workerID int) {
	log.Printf("[%s] Task execution worker %d started", w.ID, workerID)
	
	for {
		select {
		case task := <-w.TaskQueue:
			result := w.executeTask(task)
			
			select {
			case w.ResultChannel <- result:
			default:
				log.Printf("[%s] Result channel full, dropping result for task %s", 
					w.ID, task.ID)
			}
			
			atomic.AddInt32(&w.CurrentLoad, -1)
			
		case <-w.StopChannel:
			log.Printf("[%s] Worker %d stopping", w.ID, workerID)
			return
			
		case <-w.ctx.Done():
			log.Printf("[%s] Worker %d context cancelled", w.ID, workerID)
			return
		}
	}
}

// executeTask executes a single task
func (w *WorkerNode) executeTask(task *Task) *TaskResult {
	startTime := time.Now()
	task.UpdateStatus(TaskStatusRunning)
	
	log.Printf("[%s] Executing task %s (type: %s, priority: %s)", 
		w.ID, task.ID, task.Type, task.Priority)
	
	// Simulate task execution based on task type
	var result interface{}
	var err error
	
	switch task.Type {
	case "order_processing":
		result, err = w.processFlipkartOrder(task.Payload)
	case "inventory_update":
		result, err = w.updateInventory(task.Payload)
	case "payment_processing":
		result, err = w.processPayment(task.Payload)
	case "notification_send":
		result, err = w.sendNotification(task.Payload)
	case "analytics_compute":
		result, err = w.computeAnalytics(task.Payload)
	case "image_processing":
		result, err = w.processImage(task.Payload)
	default:
		result, err = w.executeGenericTask(task.Payload)
	}
	
	executionTime := time.Since(startTime)
	
	// Update worker statistics
	atomic.AddInt64(&w.TasksExecuted, 1)
	
	var taskResult *TaskResult
	if err != nil {
		task.UpdateStatus(TaskStatusFailed)
		atomic.AddInt64(&w.TasksFailed, 1)
		
		taskResult = &TaskResult{
			TaskID:        task.ID,
			WorkerID:      w.ID,
			Status:        TaskStatusFailed,
			ErrorMessage:  err.Error(),
			ExecutionTime: executionTime,
			CompletedAt:   time.Now(),
		}
		
		log.Printf("[%s] Task %s failed: %v", w.ID, task.ID, err)
	} else {
		task.UpdateStatus(TaskStatusCompleted)
		task.Result = result
		atomic.AddInt64(&w.TasksSuccessful, 1)
		
		taskResult = &TaskResult{
			TaskID:        task.ID,
			WorkerID:      w.ID,
			Status:        TaskStatusCompleted,
			Result:        result,
			ExecutionTime: executionTime,
			CompletedAt:   time.Now(),
		}
		
		log.Printf("[%s] Task %s completed in %v", w.ID, task.ID, executionTime)
	}
	
	// Update average execution time
	w.updateAverageExecutionTime(executionTime)
	
	return taskResult
}

// Flipkart-specific task execution methods
func (w *WorkerNode) processFlipkartOrder(payload map[string]interface{}) (interface{}, error) {
	// Simulate order processing
	orderID := payload["order_id"].(string)
	
	// Simulate processing time (1-3 seconds)
	processingTime := time.Duration(1000+rand.Intn(2000)) * time.Millisecond
	time.Sleep(processingTime)
	
	// Simulate 95% success rate
	if rand.Float64() > 0.95 {
		return nil, fmt.Errorf("order processing failed for order %s", orderID)
	}
	
	return map[string]interface{}{
		"order_id":        orderID,
		"status":          "processed",
		"tracking_number": fmt.Sprintf("TRK%d", rand.Intn(1000000)),
		"estimated_delivery": time.Now().Add(48 * time.Hour).Format("2006-01-02"),
	}, nil
}

func (w *WorkerNode) updateInventory(payload map[string]interface{}) (interface{}, error) {
	productID := payload["product_id"].(string)
	
	// Simulate database update time
	time.Sleep(time.Duration(200+rand.Intn(300)) * time.Millisecond)
	
	if rand.Float64() > 0.98 {
		return nil, fmt.Errorf("inventory update failed for product %s", productID)
	}
	
	return map[string]interface{}{
		"product_id":     productID,
		"updated_stock":  rand.Intn(1000),
		"last_updated":   time.Now().Format(time.RFC3339),
	}, nil
}

func (w *WorkerNode) processPayment(payload map[string]interface{}) (interface{}, error) {
	paymentID := payload["payment_id"].(string)
	
	// Simulate payment gateway interaction
	time.Sleep(time.Duration(500+rand.Intn(1000)) * time.Millisecond)
	
	if rand.Float64() > 0.97 {
		return nil, fmt.Errorf("payment processing failed for payment %s", paymentID)
	}
	
	return map[string]interface{}{
		"payment_id":     paymentID,
		"status":         "success",
		"transaction_id": fmt.Sprintf("TXN%d", rand.Intn(1000000)),
		"processed_at":   time.Now().Format(time.RFC3339),
	}, nil
}

func (w *WorkerNode) sendNotification(payload map[string]interface{}) (interface{}, error) {
	userID := payload["user_id"].(string)
	
	// Simulate notification sending
	time.Sleep(time.Duration(100+rand.Intn(200)) * time.Millisecond)
	
	if rand.Float64() > 0.99 {
		return nil, fmt.Errorf("notification sending failed for user %s", userID)
	}
	
	return map[string]interface{}{
		"user_id":   userID,
		"sent_at":   time.Now().Format(time.RFC3339),
		"channel":   "push",
		"status":    "delivered",
	}, nil
}

func (w *WorkerNode) computeAnalytics(payload map[string]interface{}) (interface{}, error) {
	reportType := payload["report_type"].(string)
	
	// Simulate analytics computation (longer processing)
	time.Sleep(time.Duration(2000+rand.Intn(3000)) * time.Millisecond)
	
	if rand.Float64() > 0.96 {
		return nil, fmt.Errorf("analytics computation failed for report %s", reportType)
	}
	
	return map[string]interface{}{
		"report_type":   reportType,
		"data_points":   rand.Intn(10000),
		"computed_at":   time.Now().Format(time.RFC3339),
		"file_path":     fmt.Sprintf("/reports/%s_%d.csv", reportType, time.Now().Unix()),
	}, nil
}

func (w *WorkerNode) processImage(payload map[string]interface{}) (interface{}, error) {
	imageID := payload["image_id"].(string)
	
	// Simulate image processing (longer processing)
	time.Sleep(time.Duration(1500+rand.Intn(2000)) * time.Millisecond)
	
	if rand.Float64() > 0.94 {
		return nil, fmt.Errorf("image processing failed for image %s", imageID)
	}
	
	return map[string]interface{}{
		"image_id":        imageID,
		"processed_sizes": []string{"thumbnail", "medium", "large"},
		"processed_at":    time.Now().Format(time.RFC3339),
	}, nil
}

func (w *WorkerNode) executeGenericTask(payload map[string]interface{}) (interface{}, error) {
	// Generic task execution
	time.Sleep(time.Duration(500+rand.Intn(1000)) * time.Millisecond)
	
	if rand.Float64() > 0.97 {
		return nil, fmt.Errorf("generic task execution failed")
	}
	
	return map[string]interface{}{
		"status":      "completed",
		"executed_at": time.Now().Format(time.RFC3339),
	}, nil
}

func (w *WorkerNode) updateAverageExecutionTime(executionTime time.Duration) {
	w.Mutex.Lock()
	defer w.Mutex.Unlock()
	
	// Simple moving average
	if w.AvgExecutionTime == 0 {
		w.AvgExecutionTime = executionTime
	} else {
		w.AvgExecutionTime = (w.AvgExecutionTime + executionTime) / 2
	}
}

func (w *WorkerNode) heartbeatWorker() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			w.Mutex.Lock()
			w.LastHeartbeat = time.Now()
			// Simulate health status (95% healthy)
			w.IsHealthy = rand.Float64() > 0.05
			// Simulate resource usage
			w.CPUUsage = rand.Float64() * 100
			w.MemoryUsage = rand.Float64() * 100
			w.Mutex.Unlock()
			
		case <-w.ctx.Done():
			return
		}
	}
}

// GetStats returns worker statistics
func (w *WorkerNode) GetStats() WorkerStats {
	w.Mutex.RLock()
	defer w.Mutex.RUnlock()
	
	executed := atomic.LoadInt64(&w.TasksExecuted)
	successful := atomic.LoadInt64(&w.TasksSuccessful)
	failed := atomic.LoadInt64(&w.TasksFailed)
	currentLoad := atomic.LoadInt32(&w.CurrentLoad)
	
	var successRate float64
	if executed > 0 {
		successRate = float64(successful) / float64(executed) * 100
	}
	
	return WorkerStats{
		ID:               w.ID,
		Region:           w.Region,
		Zone:             w.Zone,
		IsHealthy:        w.IsHealthy,
		CurrentLoad:      int(currentLoad),
		Capacity:         w.Capacity,
		TasksExecuted:    executed,
		TasksSuccessful:  successful,
		TasksFailed:      failed,
		SuccessRate:      successRate,
		AvgExecutionTime: w.AvgExecutionTime,
		CPUUsage:         w.CPUUsage,
		MemoryUsage:      w.MemoryUsage,
		LastHeartbeat:    w.LastHeartbeat,
		Specializations:  w.Specializations,
	}
}

// WorkerStats represents worker node statistics
type WorkerStats struct {
	ID               string        `json:"id"`
	Region           string        `json:"region"`
	Zone             string        `json:"zone"`
	IsHealthy        bool          `json:"is_healthy"`
	CurrentLoad      int           `json:"current_load"`
	Capacity         int           `json:"capacity"`
	TasksExecuted    int64         `json:"tasks_executed"`
	TasksSuccessful  int64         `json:"tasks_successful"`
	TasksFailed      int64         `json:"tasks_failed"`
	SuccessRate      float64       `json:"success_rate"`
	AvgExecutionTime time.Duration `json:"avg_execution_time"`
	CPUUsage         float64       `json:"cpu_usage"`
	MemoryUsage      float64       `json:"memory_usage"`
	LastHeartbeat    time.Time     `json:"last_heartbeat"`
	Specializations  []string      `json:"specializations"`
}

// DistributedTaskScheduler manages task scheduling across worker nodes
type DistributedTaskScheduler struct {
	Name            string
	Workers         map[string]*WorkerNode
	Tasks           map[string]*Task
	CompletedTasks  map[string]bool
	TaskQueue       chan *Task
	ResultChannel   chan *TaskResult
	Mutex           sync.RWMutex
	
	// Statistics
	TotalTasks       int64
	CompletedCount   int64
	FailedCount      int64
	StartTime        time.Time
	
	ctx    context.Context
	cancel context.CancelFunc
}

// NewDistributedTaskScheduler creates a new distributed task scheduler
func NewDistributedTaskScheduler(name string) *DistributedTaskScheduler {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &DistributedTaskScheduler{
		Name:           name,
		Workers:        make(map[string]*WorkerNode),
		Tasks:          make(map[string]*Task),
		CompletedTasks: make(map[string]bool),
		TaskQueue:      make(chan *Task, 10000),
		ResultChannel:  make(chan *TaskResult, 1000),
		StartTime:      time.Now(),
		ctx:            ctx,
		cancel:         cancel,
	}
}

// AddWorker adds a worker node to the scheduler
func (dts *DistributedTaskScheduler) AddWorker(worker *WorkerNode) {
	dts.Mutex.Lock()
	defer dts.Mutex.Unlock()
	
	dts.Workers[worker.ID] = worker
	worker.Start()
	
	log.Printf("[%s] Added worker: %s (%s/%s)", 
		dts.Name, worker.ID, worker.Region, worker.Zone)
}

// Start begins the scheduler
func (dts *DistributedTaskScheduler) Start() {
	log.Printf("[%s] Starting distributed task scheduler", dts.Name)
	
	// Start task scheduling goroutine
	go dts.taskSchedulingLoop()
	
	// Start result processing goroutine
	go dts.resultProcessingLoop()
	
	// Start statistics reporting goroutine
	go dts.statisticsReportingLoop()
}

// Stop gracefully shuts down the scheduler
func (dts *DistributedTaskScheduler) Stop() {
	log.Printf("[%s] Stopping distributed task scheduler", dts.Name)
	
	dts.cancel()
	
	// Stop all workers
	dts.Mutex.RLock()
	for _, worker := range dts.Workers {
		worker.Stop()
	}
	dts.Mutex.RUnlock()
	
	close(dts.TaskQueue)
	close(dts.ResultChannel)
}

// SubmitTask submits a task for execution
func (dts *DistributedTaskScheduler) SubmitTask(task *Task) {
	dts.Mutex.Lock()
	dts.Tasks[task.ID] = task
	dts.Mutex.Unlock()
	
	atomic.AddInt64(&dts.TotalTasks, 1)
	
	select {
	case dts.TaskQueue <- task:
		log.Printf("[%s] Task submitted: %s (type: %s, priority: %s)", 
			dts.Name, task.ID, task.Type, task.Priority)
	default:
		log.Printf("[%s] Task queue full, task dropped: %s", dts.Name, task.ID)
		task.UpdateStatus(TaskStatusFailed)
		task.ErrorMessage = "Task queue full"
	}
}

// taskSchedulingLoop continuously schedules tasks to workers
func (dts *DistributedTaskScheduler) taskSchedulingLoop() {
	for {
		select {
		case task := <-dts.TaskQueue:
			dts.scheduleTask(task)
			
		case <-dts.ctx.Done():
			return
		}
	}
}

// scheduleTask schedules a single task to an appropriate worker
func (dts *DistributedTaskScheduler) scheduleTask(task *Task) {
	// Check if task is ready for execution
	if !task.IsReady(dts.CompletedTasks) {
		// Reschedule task for later
		go func() {
			time.Sleep(1 * time.Second)
			select {
			case dts.TaskQueue <- task:
			case <-dts.ctx.Done():
			}
		}()
		return
	}
	
	// Find suitable workers
	suitableWorkers := dts.findSuitableWorkers(task)
	if len(suitableWorkers) == 0 {
		log.Printf("[%s] No suitable workers for task %s, retrying later", dts.Name, task.ID)
		
		// Reschedule task
		go func() {
			time.Sleep(2 * time.Second)
			select {
			case dts.TaskQueue <- task:
			case <-dts.ctx.Done():
			}
		}()
		return
	}
	
	// Select best worker based on priority and load
	selectedWorker := dts.selectBestWorker(task, suitableWorkers)
	
	// Assign task to worker
	if selectedWorker.AssignTask(task) {
		log.Printf("[%s] Assigned task %s to worker %s", 
			dts.Name, task.ID, selectedWorker.ID)
	} else {
		log.Printf("[%s] Failed to assign task %s to worker %s, retrying", 
			dts.Name, task.ID, selectedWorker.ID)
		
		// Reschedule task
		go func() {
			time.Sleep(1 * time.Second)
			select {
			case dts.TaskQueue <- task:
			case <-dts.ctx.Done():
			}
		}()
	}
}

// findSuitableWorkers finds workers that can handle the task
func (dts *DistributedTaskScheduler) findSuitableWorkers(task *Task) []*WorkerNode {
	dts.Mutex.RLock()
	defer dts.Mutex.RUnlock()
	
	var suitable []*WorkerNode
	
	for _, worker := range dts.Workers {
		if !worker.IsHealthy || !worker.IsRunning {
			continue
		}
		
		// Check if worker can handle this task type
		canHandle := false
		for _, spec := range worker.Specializations {
			if spec == task.Type || spec == "*" {
				canHandle = true
				break
			}
		}
		
		if canHandle && atomic.LoadInt32(&worker.CurrentLoad) < int32(worker.Capacity) {
			suitable = append(suitable, worker)
		}
	}
	
	return suitable
}

// selectBestWorker selects the best worker for a task
func (dts *DistributedTaskScheduler) selectBestWorker(task *Task, workers []*WorkerNode) *WorkerNode {
	if len(workers) == 0 {
		return nil
	}
	
	// Sort workers by load and execution time for critical tasks
	if task.Priority == PriorityCritical {
		sort.Slice(workers, func(i, j int) bool {
			loadI := atomic.LoadInt32(&workers[i].CurrentLoad)
			loadJ := atomic.LoadInt32(&workers[j].CurrentLoad)
			
			if loadI != loadJ {
				return loadI < loadJ
			}
			
			return workers[i].AvgExecutionTime < workers[j].AvgExecutionTime
		})
	} else {
		// For normal tasks, prefer workers with lower load
		sort.Slice(workers, func(i, j int) bool {
			loadI := atomic.LoadInt32(&workers[i].CurrentLoad)
			loadJ := atomic.LoadInt32(&workers[j].CurrentLoad)
			return loadI < loadJ
		})
	}
	
	return workers[0]
}

// resultProcessingLoop processes task results
func (dts *DistributedTaskScheduler) resultProcessingLoop() {
	for {
		select {
		case result := <-dts.ResultChannel:
			dts.processTaskResult(result)
			
		case <-dts.ctx.Done():
			return
		}
		
		// Also check worker result channels
		dts.Mutex.RLock()
		for _, worker := range dts.Workers {
			select {
			case result := <-worker.ResultChannel:
				dts.processTaskResult(result)
			default:
				// No result available
			}
		}
		dts.Mutex.RUnlock()
	}
}

// processTaskResult processes a single task result
func (dts *DistributedTaskScheduler) processTaskResult(result *TaskResult) {
	dts.Mutex.Lock()
	defer dts.Mutex.Unlock()
	
	task, exists := dts.Tasks[result.TaskID]
	if !exists {
		log.Printf("[%s] Received result for unknown task: %s", dts.Name, result.TaskID)
		return
	}
	
	switch result.Status {
	case TaskStatusCompleted:
		dts.CompletedTasks[result.TaskID] = true
		atomic.AddInt64(&dts.CompletedCount, 1)
		log.Printf("[%s] Task completed: %s by worker %s in %v", 
			dts.Name, result.TaskID, result.WorkerID, result.ExecutionTime)
		
	case TaskStatusFailed:
		atomic.AddInt64(&dts.FailedCount, 1)
		
		// Retry logic
		if task.RetryCount < task.MaxRetries {
			task.RetryCount++
			task.UpdateStatus(TaskStatusRetrying)
			
			// Reschedule with exponential backoff
			backoffDuration := time.Duration(task.RetryCount*task.RetryCount) * time.Second
			
			go func() {
				time.Sleep(backoffDuration)
				select {
				case dts.TaskQueue <- task:
					log.Printf("[%s] Retrying task %s (attempt %d/%d)", 
						dts.Name, task.ID, task.RetryCount, task.MaxRetries)
				case <-dts.ctx.Done():
				}
			}()
		} else {
			log.Printf("[%s] Task failed permanently: %s after %d retries", 
				dts.Name, result.TaskID, task.MaxRetries)
		}
	}
}

// statisticsReportingLoop periodically reports scheduler statistics
func (dts *DistributedTaskScheduler) statisticsReportingLoop() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			dts.reportStatistics()
			
		case <-dts.ctx.Done():
			return
		}
	}
}

// reportStatistics reports current scheduler statistics
func (dts *DistributedTaskScheduler) reportStatistics() {
	total := atomic.LoadInt64(&dts.TotalTasks)
	completed := atomic.LoadInt64(&dts.CompletedCount)
	failed := atomic.LoadInt64(&dts.FailedCount)
	
	elapsed := time.Since(dts.StartTime)
	tasksPerSecond := float64(completed) / elapsed.Seconds()
	
	dts.Mutex.RLock()
	workerCount := len(dts.Workers)
	healthyWorkers := 0
	totalCapacity := 0
	currentLoad := 0
	
	for _, worker := range dts.Workers {
		if worker.IsHealthy {
			healthyWorkers++
		}
		totalCapacity += worker.Capacity
		currentLoad += int(atomic.LoadInt32(&worker.CurrentLoad))
	}
	dts.Mutex.RUnlock()
	
	var successRate float64
	if total > 0 {
		successRate = float64(completed) / float64(total) * 100
	}
	
	log.Printf("[%s] Stats: Total=%d, Completed=%d, Failed=%d, Success=%.1f%%, Rate=%.1f/sec, Workers=%d/%d, Load=%d/%d", 
		dts.Name, total, completed, failed, successRate, tasksPerSecond, 
		healthyWorkers, workerCount, currentLoad, totalCapacity)
}

// GetStats returns scheduler statistics
func (dts *DistributedTaskScheduler) GetStats() SchedulerStats {
	total := atomic.LoadInt64(&dts.TotalTasks)
	completed := atomic.LoadInt64(&dts.CompletedCount)
	failed := atomic.LoadInt64(&dts.FailedCount)
	
	elapsed := time.Since(dts.StartTime)
	tasksPerSecond := float64(completed) / elapsed.Seconds()
	
	var successRate float64
	if total > 0 {
		successRate = float64(completed) / float64(total) * 100
	}
	
	return SchedulerStats{
		Name:           dts.Name,
		TotalTasks:     total,
		CompletedTasks: completed,
		FailedTasks:    failed,
		SuccessRate:    successRate,
		TasksPerSecond: tasksPerSecond,
		Uptime:         elapsed,
	}
}

// SchedulerStats represents scheduler statistics
type SchedulerStats struct {
	Name           string        `json:"name"`
	TotalTasks     int64         `json:"total_tasks"`
	CompletedTasks int64         `json:"completed_tasks"`
	FailedTasks    int64         `json:"failed_tasks"`
	SuccessRate    float64       `json:"success_rate"`
	TasksPerSecond float64       `json:"tasks_per_second"`
	Uptime         time.Duration `json:"uptime"`
}

// Main demonstration function
func main() {
	fmt.Println("🚀 Flipkart Distributed Task Scheduler Demo")
	fmt.Println("=" + string(make([]byte, 59)))
	
	// Create distributed task scheduler
	scheduler := NewDistributedTaskScheduler("Flipkart-Scheduler")
	
	// Create worker nodes across different regions
	fmt.Println("\n🏢 Setting up worker nodes across India...")
	
	// Mumbai workers (order processing)
	mumbaiWorkers := []*WorkerNode{
		NewWorkerNode("FLIP-MUM-01", "Mumbai", "West", 5, []string{"order_processing", "payment_processing"}),
		NewWorkerNode("FLIP-MUM-02", "Mumbai", "West", 5, []string{"order_processing", "notification_send"}),
		NewWorkerNode("FLIP-MUM-03", "Mumbai", "West", 3, []string{"inventory_update", "*"}),
	}
	
	// Bangalore workers (analytics and image processing)
	bangaloreWorkers := []*WorkerNode{
		NewWorkerNode("FLIP-BLR-01", "Bangalore", "South", 4, []string{"analytics_compute", "image_processing"}),
		NewWorkerNode("FLIP-BLR-02", "Bangalore", "South", 6, []string{"analytics_compute", "*"}),
	}
	
	// Delhi workers (general purpose)
	delhiWorkers := []*WorkerNode{
		NewWorkerNode("FLIP-DEL-01", "Delhi", "North", 4, []string{"*"}),
		NewWorkerNode("FLIP-DEL-02", "Delhi", "North", 5, []string{"notification_send", "inventory_update"}),
	}
	
	// Add workers to scheduler
	allWorkers := append(append(mumbaiWorkers, bangaloreWorkers...), delhiWorkers...)
	for _, worker := range allWorkers {
		scheduler.AddWorker(worker)
		fmt.Printf("✅ Added worker: %s (%s/%s) - Capacity: %d, Specializations: %v\n", 
			worker.ID, worker.Region, worker.Zone, worker.Capacity, worker.Specializations)
	}
	
	// Start scheduler
	scheduler.Start()
	
	// Generate Flipkart-style tasks
	fmt.Println("\n📦 Generating Flipkart e-commerce tasks...")
	
	tasks := []*Task{
		// Critical order processing tasks
		NewTask("ORDER-001", "order_processing", PriorityCritical, map[string]interface{}{
			"order_id": "ORD123456", "customer_id": "CUST001", "amount": 2999.99,
		}),
		NewTask("ORDER-002", "order_processing", PriorityHigh, map[string]interface{}{
			"order_id": "ORD123457", "customer_id": "CUST002", "amount": 1599.50,
		}),
		
		// Payment processing
		NewTask("PAY-001", "payment_processing", PriorityHigh, map[string]interface{}{
			"payment_id": "PAY789123", "order_id": "ORD123456", "method": "UPI",
		}),
		NewTask("PAY-002", "payment_processing", PriorityHigh, map[string]interface{}{
			"payment_id": "PAY789124", "order_id": "ORD123457", "method": "Credit Card",
		}),
		
		// Inventory updates
		NewTask("INV-001", "inventory_update", PriorityNormal, map[string]interface{}{
			"product_id": "PROD001", "quantity_change": -1, "location": "WH-MUM-01",
		}),
		NewTask("INV-002", "inventory_update", PriorityNormal, map[string]interface{}{
			"product_id": "PROD002", "quantity_change": -2, "location": "WH-BLR-01",
		}),
		
		// Notification tasks
		NewTask("NOTIF-001", "notification_send", PriorityNormal, map[string]interface{}{
			"user_id": "CUST001", "type": "order_confirmation", "message": "Order confirmed",
		}),
		NewTask("NOTIF-002", "notification_send", PriorityNormal, map[string]interface{}{
			"user_id": "CUST002", "type": "payment_success", "message": "Payment successful",
		}),
		
		// Analytics tasks (Big Billion Day preparation)
		NewTask("ANALYTICS-001", "analytics_compute", PriorityLow, map[string]interface{}{
			"report_type": "sales_trends", "period": "last_7_days", "category": "electronics",
		}),
		NewTask("ANALYTICS-002", "analytics_compute", PriorityLow, map[string]interface{}{
			"report_type": "inventory_forecast", "period": "next_30_days", "region": "north",
		}),
		
		// Image processing for product catalog
		NewTask("IMG-001", "image_processing", PriorityLow, map[string]interface{}{
			"image_id": "IMG123456", "product_id": "PROD001", "operations": []string{"resize", "watermark"},
		}),
		NewTask("IMG-002", "image_processing", PriorityLow, map[string]interface{}{
			"image_id": "IMG123457", "product_id": "PROD002", "operations": []string{"crop", "optimize"},
		}),
	}
	
	// Submit tasks to scheduler
	for _, task := range tasks {
		scheduler.SubmitTask(task)
		fmt.Printf("📤 Submitted task: %s (type: %s, priority: %s)\n", 
			task.ID, task.Type, task.Priority)
		
		// Small delay between submissions
		time.Sleep(100 * time.Millisecond)
	}
	
	// Let tasks execute
	fmt.Println("\n⏳ Executing tasks across distributed workers...")
	time.Sleep(15 * time.Second)
	
	// Generate additional load to simulate Big Billion Day
	fmt.Println("\n🎯 Simulating Big Billion Day traffic spike...")
	
	for i := 0; i < 50; i++ {
		taskID := fmt.Sprintf("BBD-%03d", i+1)
		taskType := []string{"order_processing", "payment_processing", "inventory_update"}[rand.Intn(3)]
		priority := []TaskPriority{PriorityHigh, PriorityCritical}[rand.Intn(2)]
		
		task := NewTask(taskID, taskType, priority, map[string]interface{}{
			"bulk_operation": true,
			"batch_id":       fmt.Sprintf("BBD-BATCH-%d", i/10),
			"timestamp":      time.Now().Unix(),
		})
		
		scheduler.SubmitTask(task)
		
		if i%10 == 0 {
			fmt.Printf("📊 Big Billion Day tasks: %d/50 submitted\n", i+1)
		}
		
		time.Sleep(50 * time.Millisecond)
	}
	
	// Let system stabilize
	time.Sleep(20 * time.Second)
	
	// Print worker statistics
	fmt.Println("\n👥 Worker Node Performance Statistics:")
	fmt.Println("=" + string(make([]byte, 50)))
	
	for _, worker := range allWorkers {
		stats := worker.GetStats()
		status := "🟢"
		if !stats.IsHealthy {
			status = "🔴"
		}
		
		fmt.Printf("\n%s %s (%s/%s):\n", status, stats.ID, stats.Region, stats.Zone)
		fmt.Printf("   Load: %d/%d (%.1f%%)\n", 
			stats.CurrentLoad, stats.Capacity, 
			float64(stats.CurrentLoad)/float64(stats.Capacity)*100)
		fmt.Printf("   Tasks: %d executed, %.1f%% success rate\n", 
			stats.TasksExecuted, stats.SuccessRate)
		fmt.Printf("   Performance: %v avg execution time\n", stats.AvgExecutionTime)
		fmt.Printf("   Resources: CPU %.1f%%, Memory %.1f%%\n", 
			stats.CPUUsage, stats.MemoryUsage)
		fmt.Printf("   Specializations: %v\n", stats.Specializations)
	}
	
	// Print scheduler statistics
	fmt.Println("\n📈 Scheduler Performance Statistics:")
	fmt.Println("=" + string(make([]byte, 50)))
	
	schedulerStats := scheduler.GetStats()
	fmt.Printf("Total Tasks: %d\n", schedulerStats.TotalTasks)
	fmt.Printf("Completed: %d\n", schedulerStats.CompletedTasks)
	fmt.Printf("Failed: %d\n", schedulerStats.FailedTasks)
	fmt.Printf("Success Rate: %.2f%%\n", schedulerStats.SuccessRate)
	fmt.Printf("Throughput: %.1f tasks/second\n", schedulerStats.TasksPerSecond)
	fmt.Printf("Uptime: %v\n", schedulerStats.Uptime)
	
	// Production insights
	fmt.Println("\n💡 Production Insights for Flipkart-scale Systems:")
	fmt.Println("- Distributed task scheduling enables processing 10M+ daily e-commerce tasks")
	fmt.Println("- Worker specialization optimizes resource utilization for different task types")
	fmt.Println("- Priority-based scheduling ensures critical orders get processed first")
	fmt.Println("- Geographic distribution reduces latency and provides fault tolerance")
	fmt.Println("- Retry mechanisms with exponential backoff handle transient failures")
	fmt.Println("- Real-time load balancing prevents worker overload during traffic spikes")
	fmt.Println("- Health monitoring ensures failing workers don't receive new tasks")
	fmt.Println("- Horizontal scaling by adding workers handles Big Billion Day volumes")
	fmt.Println("- Dependency management ensures correct order of task execution")
	fmt.Println("- Critical for maintaining customer experience during peak sales events")
	
	// Cleanup
	fmt.Println("\n🧹 Shutting down distributed task scheduler...")
	scheduler.Stop()
	
	fmt.Println("Distributed task scheduler demo completed!")
}
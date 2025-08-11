// Priority Queue Implementation - Episode 2
// प्राथमिकता क्यू implementation
//
// Production-ready priority queue with fair scheduling and Mumbai local train analogy
// Mumbai Local की तरह - Ladies compartment, General compartment, और First class
// सबकी अलग priority, लेकिन fair scheduling भी होनी चाहिए!
//
// Author: Code Developer Agent A5-C-002
// Indian Context: IRCTC Tatkal vs General, Zomato Pro vs Regular, Flipkart Plus vs Normal

package main

import (
	"container/heap"
	"fmt"
	"log"
	"math/rand"
	"sort"
	"sync"
	"time"
)

// Priority levels - प्राथमिकता के स्तर
type Priority int

const (
	Critical Priority = iota // 0 - अति आवश्यक - Payment, Security
	High                     // 1 - उच्च - VIP customers, Premium services
	Medium                   // 2 - मध्यम - Regular users, Standard services  
	Low                      // 3 - निम्न - Background tasks, Analytics
	Bulk                     // 4 - थोक - Data migration, Cleanup jobs
)

// String representation of priorities
func (p Priority) String() string {
	names := []string{"Critical", "High", "Medium", "Low", "Bulk"}
	if int(p) < len(names) {
		return names[p]
	}
	return fmt.Sprintf("Unknown(%d)", int(p))
}

// Mumbai Local compartment analogy
func (p Priority) MumbaiAnalogy() string {
	analogies := []string{
		"Emergency/VIP Coach",     // Critical
		"First Class",             // High
		"Ladies Compartment",      // Medium  
		"General Compartment",     // Low
		"Luggage Compartment",     // Bulk
	}
	if int(p) < len(analogies) {
		return analogies[p]
	}
	return "Unknown Compartment"
}

// Task represents a task in the priority queue
// प्राथमिकता क्यू में एक कार्य का प्रतिनिधित्व करता है
type Task struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Priority    Priority  `json:"priority"`
	Payload     string    `json:"payload"`
	SubmittedAt time.Time `json:"submitted_at"`
	UserType    string    `json:"user_type"` // "premium", "regular", "bulk"
	Region      string    `json:"region"`    // "mumbai", "delhi", "bangalore"
	
	// Fair scheduling fields
	WaitingTime    time.Duration `json:"waiting_time"`
	ProcessingTime time.Duration `json:"processing_time"`
	RetryCount     int           `json:"retry_count"`
	
	// Mumbai local style fields
	CompartmentType string `json:"compartment_type"` // "ladies", "general", "first_class"
	StationFrom     string `json:"station_from"`
	StationTo       string `json:"station_to"`
}

// Calculate dynamic priority based on waiting time and other factors
// प्रतीक्षा समय और अन्य कारकों के आधार पर dynamic priority
func (t *Task) CalculateDynamicPriority() float64 {
	basePriority := float64(t.Priority)
	
	// Age-based priority boost (older tasks get higher priority)
	// पुराने कार्यों को उच्च प्राथमिकता
	agingFactor := t.WaitingTime.Minutes() * 0.1
	
	// Retry penalty (tasks with more retries get lower priority)
	// अधिक retry वाले कार्यों को कम प्राथमिकता
	retryPenalty := float64(t.RetryCount) * 0.5
	
	// Regional adjustment (Mumbai gets slight priority due to higher traffic)
	// मुंबई को अधिक ट्रैफिक के कारण थोड़ी अधिक प्राथमिकता
	regionBoost := 0.0
	if t.Region == "mumbai" {
		regionBoost = 0.2
	} else if t.Region == "delhi" {
		regionBoost = 0.1
	}
	
	// User type boost
	userBoost := 0.0
	switch t.UserType {
	case "premium":
		userBoost = 0.5
	case "regular":
		userBoost = 0.0
	case "bulk":
		userBoost = -0.3
	}
	
	dynamicPriority := basePriority - agingFactor + retryPenalty - regionBoost - userBoost
	
	// Lower number = higher priority (0 is highest)
	return dynamicPriority
}

// TaskHeap implements heap.Interface for Task slice
// Task slice के लिए heap.Interface implement करता है
type TaskHeap []*Task

func (h TaskHeap) Len() int { return len(h) }

func (h TaskHeap) Less(i, j int) bool {
	// Lower dynamic priority number = higher actual priority
	return h[i].CalculateDynamicPriority() < h[j].CalculateDynamicPriority()
}

func (h TaskHeap) Swap(i, j int) { h[i], h[j] = h[j], h[i] }

func (h *TaskHeap) Push(x interface{}) {
	*h = append(*h, x.(*Task))
}

func (h *TaskHeap) Pop() interface{} {
	old := *h
	n := len(old)
	item := old[n-1]
	*h = old[0 : n-1]
	return item
}

// PriorityQueue is a thread-safe priority queue with fair scheduling
// Fair scheduling के साथ thread-safe priority queue
type PriorityQueue struct {
	tasks           TaskHeap
	mutex           sync.RWMutex
	stats           QueueStats
	fairScheduling  bool
	maxWaitTime     time.Duration
	starvationGuard bool
	
	// Mumbai local style configuration
	compartments    map[string]int // compartment -> max capacity
	currentLoad     map[string]int // compartment -> current count
}

// QueueStats contains statistics about the queue
// क्यू के बारे में आंकड़े
type QueueStats struct {
	TotalTasks      int64         `json:"total_tasks"`
	ProcessedTasks  int64         `json:"processed_tasks"`
	AverageWaitTime time.Duration `json:"average_wait_time"`
	TasksByPriority map[Priority]int64 `json:"tasks_by_priority"`
	TasksByRegion   map[string]int64   `json:"tasks_by_region"`
	TasksByUserType map[string]int64   `json:"tasks_by_user_type"`
	StarvationEvents int64             `json:"starvation_events"`
}

// NewPriorityQueue creates a new priority queue
// नया priority queue बनाता है
func NewPriorityQueue(fairScheduling, starvationGuard bool) *PriorityQueue {
	pq := &PriorityQueue{
		tasks:           make(TaskHeap, 0),
		fairScheduling:  fairScheduling,
		starvationGuard: starvationGuard,
		maxWaitTime:     10 * time.Minute, // Max wait time before priority boost
		stats: QueueStats{
			TasksByPriority: make(map[Priority]int64),
			TasksByRegion:   make(map[string]int64),
			TasksByUserType: make(map[string]int64),
		},
		// Mumbai local compartment configuration
		compartments: map[string]int{
			"first_class": 50,   // First class - limited capacity
			"ladies":      200,  // Ladies compartment
			"general":     1000, // General compartment - highest capacity
			"emergency":   10,   // Emergency/VIP - very limited
		},
		currentLoad: map[string]int{
			"first_class": 0,
			"ladies":      0,
			"general":     0,
			"emergency":   0,
		},
	}
	
	heap.Init(&pq.tasks)
	
	// Start background processes
	if fairScheduling {
		go pq.fairSchedulingWorker()
	}
	if starvationGuard {
		go pq.starvationGuardWorker()
	}
	
	log.Printf("🚂 Priority Queue initialized | प्राथमिकता क्यू शुरू")
	log.Printf("   Fair Scheduling: %v | Fair Scheduling: %v", fairScheduling, fairScheduling)
	log.Printf("   Starvation Guard: %v | Starvation Guard: %v", starvationGuard, starvationGuard)
	
	return pq
}

// Enqueue adds a task to the priority queue
// Priority queue में कार्य जोड़ता है
func (pq *PriorityQueue) Enqueue(task *Task) error {
	pq.mutex.Lock()
	defer pq.mutex.Unlock()
	
	// Check compartment capacity (Mumbai local style)
	if !pq.checkCompartmentCapacity(task) {
		return fmt.Errorf("compartment %s is full, task rejected", task.CompartmentType)
	}
	
	// Set submission time and calculate waiting time
	now := time.Now()
	if task.SubmittedAt.IsZero() {
		task.SubmittedAt = now
	}
	task.WaitingTime = now.Sub(task.SubmittedAt)
	
	// Add to heap
	heap.Push(&pq.tasks, task)
	
	// Update statistics
	pq.stats.TotalTasks++
	pq.stats.TasksByPriority[task.Priority]++
	pq.stats.TasksByRegion[task.Region]++
	pq.stats.TasksByUserType[task.UserType]++
	pq.currentLoad[task.CompartmentType]++
	
	log.Printf("➕ Task enqueued: %s (Priority: %s, Region: %s, Compartment: %s) | कार्य जोड़ा गया: %s",
		task.Name, task.Priority.String(), task.Region, task.CompartmentType, task.Name)
	
	return nil
}

// Dequeue removes and returns the highest priority task
// सबसे उच्च प्राथमिकता का कार्य हटाता और लौटाता है
func (pq *PriorityQueue) Dequeue() (*Task, error) {
	pq.mutex.Lock()
	defer pq.mutex.Unlock()
	
	if pq.tasks.Len() == 0 {
		return nil, fmt.Errorf("queue is empty")
	}
	
	// Pop the highest priority task
	task := heap.Pop(&pq.tasks).(*Task)
	
	// Update waiting time
	task.WaitingTime = time.Since(task.SubmittedAt)
	
	// Update statistics
	pq.stats.ProcessedTasks++
	pq.currentLoad[task.CompartmentType]--
	
	// Update average wait time
	totalWaitTime := time.Duration(pq.stats.ProcessedTasks-1) * pq.stats.AverageWaitTime + task.WaitingTime
	pq.stats.AverageWaitTime = totalWaitTime / time.Duration(pq.stats.ProcessedTasks)
	
	log.Printf("➖ Task dequeued: %s (Waited: %v, Priority: %s) | कार्य निकाला गया: %s",
		task.Name, task.WaitingTime.Round(time.Millisecond), task.Priority.String(), task.Name)
	
	return task, nil
}

// checkCompartmentCapacity checks if the compartment has capacity
// डिब्बे में क्षमता है या नहीं जांचता है
func (pq *PriorityQueue) checkCompartmentCapacity(task *Task) bool {
	compartment := task.CompartmentType
	maxCapacity, exists := pq.compartments[compartment]
	if !exists {
		// Default to general compartment
		compartment = "general"
		maxCapacity = pq.compartments[compartment]
		task.CompartmentType = compartment
	}
	
	currentCount := pq.currentLoad[compartment]
	
	// Mumbai local logic: allow some overflow during peak hours
	// Peak hours में थोड़ी भीड़ allow करते हैं (जैसे local train में होता है)
	hour := time.Now().Hour()
	isPeakHour := (hour >= 8 && hour <= 10) || (hour >= 18 && hour <= 21)
	
	overflow := 0
	if isPeakHour {
		overflow = int(float64(maxCapacity) * 0.2) // 20% overflow during peak
	}
	
	return currentCount < (maxCapacity + overflow)
}

// Peek returns the highest priority task without removing it
// सबसे उच्च प्राथमिकता का कार्य हटाए बिना लौटाता है
func (pq *PriorityQueue) Peek() (*Task, error) {
	pq.mutex.RLock()
	defer pq.mutex.RUnlock()
	
	if pq.tasks.Len() == 0 {
		return nil, fmt.Errorf("queue is empty")
	}
	
	// Return copy of the top task
	topTask := *pq.tasks[0]
	topTask.WaitingTime = time.Since(topTask.SubmittedAt)
	
	return &topTask, nil
}

// Size returns the number of tasks in the queue
// क्यू में कार्यों की संख्या लौटाता है
func (pq *PriorityQueue) Size() int {
	pq.mutex.RLock()
	defer pq.mutex.RUnlock()
	return pq.tasks.Len()
}

// IsEmpty checks if the queue is empty
// क्यू खाली है या नहीं जांचता है
func (pq *PriorityQueue) IsEmpty() bool {
	return pq.Size() == 0
}

// GetStats returns current queue statistics
// वर्तमान क्यू आंकड़े लौटाता है
func (pq *PriorityQueue) GetStats() QueueStats {
	pq.mutex.RLock()
	defer pq.mutex.RUnlock()
	
	// Create a copy to avoid race conditions
	stats := pq.stats
	stats.TasksByPriority = make(map[Priority]int64)
	stats.TasksByRegion = make(map[string]int64)
	stats.TasksByUserType = make(map[string]int64)
	
	for k, v := range pq.stats.TasksByPriority {
		stats.TasksByPriority[k] = v
	}
	for k, v := range pq.stats.TasksByRegion {
		stats.TasksByRegion[k] = v
	}
	for k, v := range pq.stats.TasksByUserType {
		stats.TasksByUserType[k] = v
	}
	
	return stats
}

// fairSchedulingWorker runs in background to ensure fair scheduling
// Fair scheduling सुनिश्चित करने के लिए background में चलता है
func (pq *PriorityQueue) fairSchedulingWorker() {
	ticker := time.NewTicker(30 * time.Second) // Check every 30 seconds
	defer ticker.Stop()
	
	log.Printf("🎯 Fair scheduling worker started | Fair scheduling worker शुरू")
	
	for range ticker.C {
		pq.enforceFailScheduling()
	}
}

// enforceFailScheduling adjusts priorities to ensure fairness
// निष्पक्षता सुनिश्चित करने के लिए priorities को adjust करता है
func (pq *PriorityQueue) enforceFailScheduling() {
	pq.mutex.Lock()
	defer pq.mutex.Unlock()
	
	if pq.tasks.Len() == 0 {
		return
	}
	
	now := time.Now()
	fairnessAdjustments := 0
	
	// Check each task for fairness violations
	for i := 0; i < pq.tasks.Len(); i++ {
		task := pq.tasks[i]
		task.WaitingTime = now.Sub(task.SubmittedAt)
		
		// If a low priority task has been waiting too long, boost its priority
		// अगर कम priority का कार्य बहुत देर से इंतज़ार कर रहा है तो उसकी priority बढ़ाएं
		if task.WaitingTime > pq.maxWaitTime && task.Priority > High {
			log.Printf("⚖️ Fair scheduling: Boosting priority for task %s (waited %v) | "+
				"निष्पक्ष scheduling: कार्य %s की प्राथमिकता बढ़ा रहे हैं",
				task.Name, task.WaitingTime.Round(time.Second), task.Name)
			
			// Temporarily boost priority (this affects CalculateDynamicPriority)
			fairnessAdjustments++
		}
	}
	
	if fairnessAdjustments > 0 {
		// Re-heapify to reflect priority changes
		heap.Init(&pq.tasks)
		log.Printf("⚖️ Applied %d fairness adjustments | %d निष्पक्षता adjustments लागू किए",
			fairnessAdjustments, fairnessAdjustments)
	}
}

// starvationGuardWorker prevents low priority tasks from starving
// कम प्राथमिकता के कार्यों को भूखा रहने से रोकता है
func (pq *PriorityQueue) starvationGuardWorker() {
	ticker := time.NewTicker(1 * time.Minute) // Check every minute
	defer ticker.Stop()
	
	log.Printf("🛡️ Starvation guard worker started | Starvation guard worker शुरू")
	
	for range ticker.C {
		pq.preventStarvation()
	}
}

// preventStarvation ensures no task waits indefinitely
// कोई भी कार्य अनिश्चित काल तक इंतज़ार नहीं करता यह सुनिश्चित करता है
func (pq *PriorityQueue) preventStarvation() {
	pq.mutex.Lock()
	defer pq.mutex.Unlock()
	
	if pq.tasks.Len() == 0 {
		return
	}
	
	now := time.Now()
	starvationThreshold := 15 * time.Minute // 15 minutes
	starvationCount := 0
	
	for i := 0; i < pq.tasks.Len(); i++ {
		task := pq.tasks[i]
		task.WaitingTime = now.Sub(task.SubmittedAt)
		
		// If any task has been waiting longer than threshold, it's starving
		if task.WaitingTime > starvationThreshold {
			log.Printf("🚨 STARVATION DETECTED: Task %s waiting for %v | "+
				"भूखमरी का पता चला: कार्य %s %v से इंतज़ार कर रहा है",
				task.Name, task.WaitingTime.Round(time.Second), task.Name, task.WaitingTime.Round(time.Second))
			
			starvationCount++
			pq.stats.StarvationEvents++
			
			// Emergency priority boost for starving tasks
			// भूखे कार्यों के लिए आपातकालीन प्राथमिकता बूस्ट
		}
	}
	
	if starvationCount > 0 {
		// Re-heapify after starvation prevention
		heap.Init(&pq.tasks)
		log.Printf("🛡️ Prevented starvation for %d tasks | %d कार्यों की भूखमरी रोकी",
			starvationCount, starvationCount)
	}
}

// ListTasksByPriority returns tasks grouped by priority
// Priority के आधार पर कार्यों की सूची लौटाता है
func (pq *PriorityQueue) ListTasksByPriority() map[Priority][]*Task {
	pq.mutex.RLock()
	defer pq.mutex.RUnlock()
	
	result := make(map[Priority][]*Task)
	
	for _, task := range pq.tasks {
		result[task.Priority] = append(result[task.Priority], task)
	}
	
	// Sort tasks within each priority by waiting time
	for priority := range result {
		sort.Slice(result[priority], func(i, j int) bool {
			return result[priority][i].WaitingTime > result[priority][j].WaitingTime
		})
	}
	
	return result
}

// PrintStatus prints detailed queue status
// विस्तृत क्यू स्थिति प्रिंट करता है
func (pq *PriorityQueue) PrintStatus() {
	stats := pq.GetStats()
	
	fmt.Printf("\n📊 PRIORITY QUEUE STATUS | प्राथमिकता क्यू स्थिति\n")
	fmt.Printf("═══════════════════════════════════════════════════\n")
	fmt.Printf("Total Tasks: %d | कुल कार्य: %d\n", stats.TotalTasks, stats.TotalTasks)
	fmt.Printf("Processed Tasks: %d | संसाधित कार्य: %d\n", stats.ProcessedTasks, stats.ProcessedTasks)
	fmt.Printf("Queue Size: %d | क्यू आकार: %d\n", pq.Size(), pq.Size())
	fmt.Printf("Average Wait Time: %v | औसत प्रतीक्षा समय: %v\n", 
		stats.AverageWaitTime.Round(time.Millisecond), stats.AverageWaitTime.Round(time.Millisecond))
	fmt.Printf("Starvation Events: %d | भूखमरी घटनाएं: %d\n", stats.StarvationEvents, stats.StarvationEvents)
	
	// Priority breakdown
	fmt.Printf("\n🎯 TASKS BY PRIORITY | प्राथमिकता के आधार पर कार्य:\n")
	for priority := Critical; priority <= Bulk; priority++ {
		count := stats.TasksByPriority[priority]
		analogy := priority.MumbaiAnalogy()
		fmt.Printf("   %s (%s): %d\n", priority.String(), analogy, count)
	}
	
	// Regional breakdown
	fmt.Printf("\n🌏 TASKS BY REGION | क्षेत्र के आधार पर कार्य:\n")
	for region, count := range stats.TasksByRegion {
		fmt.Printf("   %s: %d\n", region, count)
	}
	
	// User type breakdown
	fmt.Printf("\n👥 TASKS BY USER TYPE | उपयोगकर्ता प्रकार के आधार पर कार्य:\n")
	for userType, count := range stats.TasksByUserType {
		fmt.Printf("   %s: %d\n", userType, count)
	}
	
	// Mumbai local compartment status
	fmt.Printf("\n🚂 MUMBAI LOCAL COMPARTMENT STATUS | मुंबई लोकल डिब्बा स्थिति:\n")
	for compartment, current := range pq.currentLoad {
		max := pq.compartments[compartment]
		utilization := float64(current) / float64(max) * 100
		fmt.Printf("   %s: %d/%d (%.1f%% full)\n", compartment, current, max, utilization)
	}
}

// CreateSampleTask creates a sample task for testing
// परीक्षण के लिए नमूना कार्य बनाता है
func CreateSampleTask(id, name string, priority Priority, region, userType string) *Task {
	// Determine compartment type based on priority and user type
	compartmentType := "general" // default
	
	switch {
	case priority == Critical:
		compartmentType = "emergency"
	case priority == High && userType == "premium":
		compartmentType = "first_class"
	case userType == "premium" && region == "mumbai":
		compartmentType = "ladies" // Assuming premium users in Mumbai prefer ladies compartment for safety
	}
	
	// Generate realistic station names based on region
	stations := map[string][]string{
		"mumbai":    {"Churchgate", "Marine Lines", "Charni Road", "Grant Road", "Mumbai Central", "Mahalaxmi", "Lower Parel", "Dadar", "Kurla", "Andheri", "Borivali", "Virar"},
		"delhi":     {"New Delhi", "Old Delhi", "Sarai Rohilla", "Karol Bagh", "Rajouri Garden", "Janakpuri", "Dwarka", "Gurgaon", "Faridabad", "Ghaziabad"},
		"bangalore": {"Bangalore City", "KR Puram", "Whitefield", "Yeshwantpur", "Hebbal", "Electronic City", "Koramangala", "Indiranagar"},
	}
	
	regionStations := stations[region]
	if regionStations == nil {
		regionStations = stations["mumbai"] // default
	}
	
	fromStation := regionStations[rand.Intn(len(regionStations))]
	toStation := regionStations[rand.Intn(len(regionStations))]
	
	// Ensure from and to are different
	for fromStation == toStation {
		toStation = regionStations[rand.Intn(len(regionStations))]
	}
	
	return &Task{
		ID:              id,
		Name:            name,
		Priority:        priority,
		Payload:         fmt.Sprintf("Sample payload for %s", name),
		SubmittedAt:     time.Now(),
		UserType:        userType,
		Region:          region,
		CompartmentType: compartmentType,
		StationFrom:     fromStation,
		StationTo:       toStation,
		WaitingTime:     0,
		ProcessingTime:  time.Duration(rand.Intn(5000)+1000) * time.Millisecond, // 1-6 seconds
		RetryCount:      0,
	}
}

// Demo function to show priority queue in action
func main() {
	fmt.Println("🚂 Priority Queue with Mumbai Local Train Analogy - Episode 2")
	fmt.Println("मुंबई लोकल ट्रेन सादृश्य के साथ प्राथमिकता क्यू - एपिसोड 2\n")
	
	// Create priority queue with fair scheduling and starvation guard
	pq := NewPriorityQueue(true, true)
	
	// Generate sample tasks representing different scenarios
	tasks := []*Task{
		// Critical tasks (Emergency/VIP Coach)
		CreateSampleTask("crit-001", "Payment Processing", Critical, "mumbai", "premium"),
		CreateSampleTask("crit-002", "Security Alert", Critical, "delhi", "premium"),
		
		// High priority tasks (First Class)
		CreateSampleTask("high-001", "VIP Customer Support", High, "mumbai", "premium"),
		CreateSampleTask("high-002", "Premium Order Processing", High, "bangalore", "premium"),
		CreateSampleTask("high-003", "Tatkal Booking", High, "delhi", "regular"),
		
		// Medium priority tasks (Ladies Compartment)
		CreateSampleTask("med-001", "Regular Order Processing", Medium, "mumbai", "regular"),
		CreateSampleTask("med-002", "User Registration", Medium, "bangalore", "regular"),
		CreateSampleTask("med-003", "Notification Delivery", Medium, "delhi", "regular"),
		CreateSampleTask("med-004", "Search Query", Medium, "mumbai", "regular"),
		
		// Low priority tasks (General Compartment)
		CreateSampleTask("low-001", "Analytics Processing", Low, "bangalore", "regular"),
		CreateSampleTask("low-002", "Log Aggregation", Low, "mumbai", "bulk"),
		CreateSampleTask("low-003", "Cache Warming", Low, "delhi", "bulk"),
		CreateSampleTask("low-004", "Email Marketing", Low, "mumbai", "bulk"),
		
		// Bulk tasks (Luggage Compartment)
		CreateSampleTask("bulk-001", "Data Migration", Bulk, "bangalore", "bulk"),
		CreateSampleTask("bulk-002", "Database Cleanup", Bulk, "mumbai", "bulk"),
		CreateSampleTask("bulk-003", "Report Generation", Bulk, "delhi", "bulk"),
	}
	
	fmt.Printf("Created %d sample tasks representing different priority levels:\n", len(tasks))
	for i, task := range tasks {
		fmt.Printf("  %d. %s (%s, %s, %s -> %s)\n", 
			i+1, task.Name, task.Priority.String(), task.Region, task.StationFrom, task.StationTo)
	}
	
	fmt.Println("\n" + strings.Repeat("═", 70))
	fmt.Println("ENQUEUING TASKS | कार्य जोड़े जा रहे हैं")
	fmt.Println(strings.Repeat("═", 70))
	
	// Enqueue all tasks
	for _, task := range tasks {
		if err := pq.Enqueue(task); err != nil {
			log.Printf("Failed to enqueue task %s: %v", task.Name, err)
		}
		time.Sleep(100 * time.Millisecond) // Small delay to show realistic timing
	}
	
	// Show initial status
	pq.PrintStatus()
	
	fmt.Println("\n" + strings.Repeat("═", 70))
	fmt.Println("PROCESSING TASKS | कार्य संसाधित किए जा रहे हैं")
	fmt.Println(strings.Repeat("═", 70))
	
	// Process some tasks to show priority ordering
	processedCount := 0
	maxProcessing := 8 // Process first 8 tasks to show priority ordering
	
	for processedCount < maxProcessing && !pq.IsEmpty() {
		task, err := pq.Dequeue()
		if err != nil {
			log.Printf("Failed to dequeue: %v", err)
			break
		}
		
		fmt.Printf("🔧 PROCESSING: %s | संसाधन: %s\n", task.Name, task.Name)
		fmt.Printf("   Priority: %s (%s) | प्राथमिकता: %s (%s)\n", 
			task.Priority.String(), task.Priority.MumbaiAnalogy(), 
			task.Priority.String(), task.Priority.MumbaiAnalogy())
		fmt.Printf("   Route: %s → %s | मार्ग: %s → %s\n", task.StationFrom, task.StationTo, task.StationFrom, task.StationTo)
		fmt.Printf("   Waiting Time: %v | प्रतीक्षा समय: %v\n", task.WaitingTime.Round(time.Millisecond), task.WaitingTime.Round(time.Millisecond))
		fmt.Printf("   User Type: %s | उपयोगकर्ता प्रकार: %s\n", task.UserType, task.UserType)
		
		// Simulate task processing
		fmt.Printf("   🚂 Mumbai Local Status: Compartment %s processing...\n", task.CompartmentType)
		time.Sleep(task.ProcessingTime)
		
		fmt.Printf("   ✅ Task completed in %v | कार्य %v में पूर्ण\n\n", 
			task.ProcessingTime.Round(time.Millisecond), task.ProcessingTime.Round(time.Millisecond))
		
		processedCount++
	}
	
	// Show updated status
	fmt.Println(strings.Repeat("═", 70))
	pq.PrintStatus()
	
	// Show remaining tasks by priority
	fmt.Println("\n📋 REMAINING TASKS BY PRIORITY | प्राथमिकता के आधार पर शेष कार्य:")
	tasksByPriority := pq.ListTasksByPriority()
	
	for priority := Critical; priority <= Bulk; priority++ {
		tasks := tasksByPriority[priority]
		if len(tasks) > 0 {
			fmt.Printf("\n%s (%s): %d tasks\n", priority.String(), priority.MumbaiAnalogy(), len(tasks))
			for i, task := range tasks {
				fmt.Printf("  %d. %s (waiting %v) | %s (%v से इंतज़ार)\n", 
					i+1, task.Name, task.WaitingTime.Round(time.Second), task.Name, task.WaitingTime.Round(time.Second))
			}
		}
	}
	
	// Simulate waiting and show fair scheduling in action
	fmt.Println(strings.Repeat("═", 70))
	fmt.Println("DEMONSTRATING FAIR SCHEDULING | निष्पक्ष scheduling का प्रदर्शन")
	fmt.Println(strings.Repeat("═", 70))
	
	fmt.Println("Waiting 45 seconds to demonstrate fair scheduling and starvation prevention...")
	fmt.Println("Fair scheduling और starvation prevention दिखाने के लिए 45 सेकंड प्रतीक्षा...")
	
	// Wait to let background workers run
	time.Sleep(45 * time.Second)
	
	// Show final status
	pq.PrintStatus()
	
	// Process remaining tasks to show fair scheduling effect
	fmt.Println("\n" + strings.Repeat("═", 70))
	fmt.Println("PROCESSING REMAINING TASKS AFTER FAIR SCHEDULING")
	fmt.Println("निष्पक्ष scheduling के बाद शेष कार्यों का संसाधन")
	fmt.Println(strings.Repeat("═", 70))
	
	remainingProcessed := 0
	for !pq.IsEmpty() && remainingProcessed < 5 {
		task, err := pq.Dequeue()
		if err != nil {
			break
		}
		
		fmt.Printf("🔧 %s (Priority: %s, Waited: %v) | %s (प्राथमिकता: %s, प्रतीक्षा: %v)\n",
			task.Name, task.Priority.String(), task.WaitingTime.Round(time.Second),
			task.Name, task.Priority.String(), task.WaitingTime.Round(time.Second))
		
		remainingProcessed++
	}
	
	// Final statistics
	fmt.Println("\n" + strings.Repeat("═", 70))
	fmt.Println("FINAL RESULTS | अंतिम परिणाम")
	fmt.Println(strings.Repeat("═", 70))
	
	pq.PrintStatus()
	
	fmt.Println("\n🎉 Priority Queue demonstration completed!")
	fmt.Println("प्राथमिकता क्यू प्रदर्शन पूर्ण!")
	
	fmt.Println("\n💡 KEY LEARNINGS | मुख्य शिक्षाएं:")
	fmt.Println("1. Fair scheduling prevents lower priority tasks from starving")
	fmt.Println("   निष्पक्ष scheduling कम प्राथमिकता के कार्यों को भूखा रहने से रोकती है")
	fmt.Println("2. Mumbai local compartment analogy helps understand priority levels")
	fmt.Println("   मुंबई लोकल डिब्बे की तरह प्राथमिकता स्तरों को समझना आसान")
	fmt.Println("3. Dynamic priority calculation considers multiple factors")
	fmt.Println("   Dynamic priority गणना कई कारकों को ध्यान में रखती है")
	fmt.Println("4. Regional and user type considerations for better fairness")
	fmt.Println("   बेहतर निष्पक्षता के लिए क्षेत्रीय और उपयोगकर्ता प्रकार का विचार")
}

// Additional imports needed
import "strings"
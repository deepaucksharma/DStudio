/*
Watermark and Late Data Handling in Go
Episode 43: Real-time Analytics at Scale

Advanced event-time processing with watermarks and late data handling
Use Case: WhatsApp message delivery analytics with out-of-order message handling
*/

package main

import (
	"container/heap"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"sort"
	"sync"
	"time"
)

// MessageEvent represents a WhatsApp message event
// WhatsApp message की complete delivery information
type MessageEvent struct {
	MessageID       string    `json:"message_id"`
	ConversationID  string    `json:"conversation_id"`
	SenderID        string    `json:"sender_id"`
	ReceiverID      string    `json:"receiver_id"`
	MessageType     string    `json:"message_type"` // text, image, video, audio, document
	EventType       string    `json:"event_type"`   // sent, delivered, read, failed
	EventTime       time.Time `json:"event_time"`   // When the event actually happened
	ProcessingTime  time.Time `json:"processing_time"` // When we received the event
	MessageSize     int64     `json:"message_size"`
	ServerID        string    `json:"server_id"`
	CountryCode     string    `json:"country_code"`
	NetworkType     string    `json:"network_type"` // wifi, 4g, 3g, 2g
	DeviceType      string    `json:"device_type"`  // android, ios, web
	IsGroupMessage  bool      `json:"is_group_message"`
	GroupSize       int       `json:"group_size,omitempty"`
	RetryCount      int       `json:"retry_count"`
	LatencyMs       int64     `json:"latency_ms,omitempty"`
}

// Watermark represents the event-time progress
// Event-time की progress को track करता है
type Watermark struct {
	Timestamp time.Time `json:"timestamp"`
	SourceID  string    `json:"source_id"`
}

// WindowState represents the state of a time window
// Time window का current state
type WindowState struct {
	WindowStart     time.Time     `json:"window_start"`
	WindowEnd       time.Time     `json:"window_end"`
	EventCount      int64         `json:"event_count"`
	LateEventCount  int64         `json:"late_event_count"`
	TotalSize       int64         `json:"total_size"`
	DeliveryLatency []int64       `json:"delivery_latency"`
	EventsByType    map[string]int64 `json:"events_by_type"`
	EventsByCountry map[string]int64 `json:"events_by_country"`
	EventsByNetwork map[string]int64 `json:"events_by_network"`
	LastUpdated     time.Time     `json:"last_updated"`
	IsFinalized     bool          `json:"is_finalized"`
	WatermarkTime   time.Time     `json:"watermark_time"`
}

func NewWindowState(start, end time.Time) *WindowState {
	return &WindowState{
		WindowStart:     start,
		WindowEnd:       end,
		EventsByType:    make(map[string]int64),
		EventsByCountry: make(map[string]int64),
		EventsByNetwork: make(map[string]int64),
		DeliveryLatency: make([]int64, 0),
		LastUpdated:     time.Now(),
	}
}

func (ws *WindowState) AddEvent(event MessageEvent, isLate bool) {
	ws.EventCount++
	if isLate {
		ws.LateEventCount++
	}
	
	ws.TotalSize += event.MessageSize
	ws.EventsByType[event.EventType]++
	ws.EventsByCountry[event.CountryCode]++
	ws.EventsByNetwork[event.NetworkType]++
	
	if event.LatencyMs > 0 {
		ws.DeliveryLatency = append(ws.DeliveryLatency, event.LatencyMs)
	}
	
	ws.LastUpdated = time.Now()
}

func (ws *WindowState) GetAnalytics() map[string]interface{} {
	// Calculate average latency
	avgLatency := int64(0)
	if len(ws.DeliveryLatency) > 0 {
		sum := int64(0)
		for _, latency := range ws.DeliveryLatency {
			sum += latency
		}
		avgLatency = sum / int64(len(ws.DeliveryLatency))
	}
	
	// Calculate percentiles
	p95Latency := int64(0)
	p99Latency := int64(0)
	if len(ws.DeliveryLatency) > 0 {
		sorted := make([]int64, len(ws.DeliveryLatency))
		copy(sorted, ws.DeliveryLatency)
		sort.Slice(sorted, func(i, j int) bool { return sorted[i] < sorted[j] })
		
		if len(sorted) > 0 {
			p95Index := int(float64(len(sorted)) * 0.95)
			p99Index := int(float64(len(sorted)) * 0.99)
			
			if p95Index < len(sorted) {
				p95Latency = sorted[p95Index]
			}
			if p99Index < len(sorted) {
				p99Latency = sorted[p99Index]
			}
		}
	}
	
	// Calculate delivery success rate
	deliveredCount := ws.EventsByType["delivered"]
	sentCount := ws.EventsByType["sent"]
	deliveryRate := 0.0
	if sentCount > 0 {
		deliveryRate = float64(deliveredCount) / float64(sentCount) * 100
	}
	
	// Calculate read rate
	readCount := ws.EventsByType["read"]
	readRate := 0.0
	if deliveredCount > 0 {
		readRate = float64(readCount) / float64(deliveredCount) * 100
	}
	
	return map[string]interface{}{
		"window_start":       ws.WindowStart.Format(time.RFC3339),
		"window_end":         ws.WindowEnd.Format(time.RFC3339),
		"total_events":       ws.EventCount,
		"late_events":        ws.LateEventCount,
		"late_event_rate":    float64(ws.LateEventCount) / float64(ws.EventCount) * 100,
		"total_message_size": ws.TotalSize,
		"avg_latency_ms":     avgLatency,
		"p95_latency_ms":     p95Latency,
		"p99_latency_ms":     p99Latency,
		"delivery_rate":      deliveryRate,
		"read_rate":          readRate,
		"events_by_type":     ws.EventsByType,
		"events_by_country":  ws.EventsByCountry,
		"events_by_network":  ws.EventsByNetwork,
		"is_finalized":       ws.IsFinalized,
		"watermark_time":     ws.WatermarkTime.Format(time.RFC3339),
	}
}

// EventTimeProcessor handles event-time processing with watermarks
// Event-time processing को handle करता है
type EventTimeProcessor struct {
	windowSize         time.Duration
	allowedLateness    time.Duration
	windows            map[string]*WindowState // key: window start time string
	watermarks         map[string]Watermark   // key: source ID
	lateDataBuffer     []*MessageEvent
	mutex              sync.RWMutex
	outputChannel      chan map[string]interface{}
	ctx                context.Context
	cancel             context.CancelFunc
}

func NewEventTimeProcessor(windowSize, allowedLateness time.Duration) *EventTimeProcessor {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &EventTimeProcessor{
		windowSize:      windowSize,
		allowedLateness: allowedLateness,
		windows:         make(map[string]*WindowState),
		watermarks:      make(map[string]Watermark),
		lateDataBuffer:  make([]*MessageEvent, 0),
		outputChannel:   make(chan map[string]interface{}, 1000),
		ctx:             ctx,
		cancel:          cancel,
	}
}

func (etp *EventTimeProcessor) ProcessEvent(event MessageEvent) {
	etp.mutex.Lock()
	defer etp.mutex.Unlock()
	
	// Update watermark for this source
	sourceID := event.ServerID
	currentWatermark, exists := etp.watermarks[sourceID]
	
	// Watermark should be monotonically increasing
	newWatermarkTime := event.EventTime.Add(-etp.allowedLateness)
	if !exists || newWatermarkTime.After(currentWatermark.Timestamp) {
		etp.watermarks[sourceID] = Watermark{
			Timestamp: newWatermarkTime,
			SourceID:  sourceID,
		}
	}
	
	// Determine which window this event belongs to
	windowStart := etp.getWindowStart(event.EventTime)
	windowEnd := windowStart.Add(etp.windowSize)
	windowKey := windowStart.Format(time.RFC3339)
	
	// Check if this is a late event
	globalWatermark := etp.getGlobalWatermark()
	isLateEvent := event.EventTime.Before(globalWatermark.Timestamp)
	
	// Create window if it doesn't exist
	if _, exists := etp.windows[windowKey]; !exists {
		etp.windows[windowKey] = NewWindowState(windowStart, windowEnd)
	}
	
	window := etp.windows[windowKey]
	
	// Check if window is already finalized
	if window.IsFinalized {
		if isLateEvent {
			log.Printf("🕐 Late event received for finalized window: %s (event time: %s, watermark: %s)",
				windowKey, event.EventTime.Format(time.RFC3339), globalWatermark.Timestamp.Format(time.RFC3339))
			
			// Store in late data buffer for analysis
			etp.lateDataBuffer = append(etp.lateDataBuffer, &event)
			if len(etp.lateDataBuffer) > 1000 {
				etp.lateDataBuffer = etp.lateDataBuffer[1:] // Keep only last 1000 late events
			}
		}
		return
	}
	
	// Add event to window
	window.AddEvent(event, isLateEvent)
	window.WatermarkTime = globalWatermark.Timestamp
	
	// Check if window should be finalized
	if globalWatermark.Timestamp.After(windowEnd.Add(etp.allowedLateness)) {
		etp.finalizeWindow(window)
	}
}

func (etp *EventTimeProcessor) getWindowStart(eventTime time.Time) time.Time {
	// Round down to window boundary
	windowSizeNanos := etp.windowSize.Nanoseconds()
	windowNumber := eventTime.UnixNano() / windowSizeNanos
	return time.Unix(0, windowNumber*windowSizeNanos).UTC()
}

func (etp *EventTimeProcessor) getGlobalWatermark() Watermark {
	// Global watermark is the minimum of all source watermarks
	var globalWatermark Watermark
	
	if len(etp.watermarks) == 0 {
		return Watermark{Timestamp: time.Now().Add(-time.Hour)} // Conservative default
	}
	
	isFirst := true
	for _, wm := range etp.watermarks {
		if isFirst || wm.Timestamp.Before(globalWatermark.Timestamp) {
			globalWatermark = wm
			isFirst = false
		}
	}
	
	return globalWatermark
}

func (etp *EventTimeProcessor) finalizeWindow(window *WindowState) {
	window.IsFinalized = true
	
	log.Printf("✅ Finalizing window [%s - %s]: %d events (%d late)",
		window.WindowStart.Format("15:04:05"),
		window.WindowEnd.Format("15:04:05"),
		window.EventCount,
		window.LateEventCount)
	
	// Send analytics to output channel
	analytics := window.GetAnalytics()
	select {
	case etp.outputChannel <- analytics:
	default:
		log.Println("⚠️ Output channel full, dropping analytics")
	}
}

func (etp *EventTimeProcessor) StartPeriodicWatermarkAdvancement() {
	go func() {
		ticker := time.NewTicker(1 * time.Second)
		defer ticker.Stop()
		
		for {
			select {
			case <-etp.ctx.Done():
				return
			case <-ticker.C:
				etp.advanceWatermarksAndFinalizeWindows()
			}
		}
	}()
}

func (etp *EventTimeProcessor) advanceWatermarksAndFinalizeWindows() {
	etp.mutex.Lock()
	defer etp.mutex.Unlock()
	
	globalWatermark := etp.getGlobalWatermark()
	
	// Check which windows should be finalized
	for windowKey, window := range etp.windows {
		if !window.IsFinalized {
			windowEndWithLateness := window.WindowEnd.Add(etp.allowedLateness)
			
			if globalWatermark.Timestamp.After(windowEndWithLateness) {
				etp.finalizeWindow(window)
			}
		}
	}
	
	// Clean up old finalized windows
	etp.cleanupOldWindows()
}

func (etp *EventTimeProcessor) cleanupOldWindows() {
	// Remove windows older than 1 hour
	cutoff := time.Now().Add(-time.Hour)
	
	for windowKey, window := range etp.windows {
		if window.IsFinalized && window.WindowEnd.Before(cutoff) {
			delete(etp.windows, windowKey)
		}
	}
}

func (etp *EventTimeProcessor) GetLateDataStatistics() map[string]interface{} {
	etp.mutex.RLock()
	defer etp.mutex.RUnlock()
	
	if len(etp.lateDataBuffer) == 0 {
		return map[string]interface{}{
			"total_late_events": 0,
			"avg_lateness_ms":   0,
			"max_lateness_ms":   0,
		}
	}
	
	totalLateness := int64(0)
	maxLateness := int64(0)
	
	globalWatermark := etp.getGlobalWatermark()
	
	for _, event := range etp.lateDataBuffer {
		lateness := globalWatermark.Timestamp.Sub(event.EventTime).Milliseconds()
		totalLateness += lateness
		
		if lateness > maxLateness {
			maxLateness = lateness
		}
	}
	
	avgLateness := totalLateness / int64(len(etp.lateDataBuffer))
	
	return map[string]interface{}{
		"total_late_events": len(etp.lateDataBuffer),
		"avg_lateness_ms":   avgLateness,
		"max_lateness_ms":   maxLateness,
		"watermark_time":    globalWatermark.Timestamp.Format(time.RFC3339),
	}
}

func (etp *EventTimeProcessor) GetActiveWindows() []map[string]interface{} {
	etp.mutex.RLock()
	defer etp.mutex.RUnlock()
	
	var windows []map[string]interface{}
	
	for _, window := range etp.windows {
		if !window.IsFinalized {
			windows = append(windows, window.GetAnalytics())
		}
	}
	
	// Sort by window start time
	sort.Slice(windows, func(i, j int) bool {
		startI, _ := time.Parse(time.RFC3339, windows[i]["window_start"].(string))
		startJ, _ := time.Parse(time.RFC3339, windows[j]["window_start"].(string))
		return startI.Before(startJ)
	})
	
	return windows
}

func (etp *EventTimeProcessor) Stop() {
	etp.cancel()
	close(etp.outputChannel)
}

// PriorityQueue for ordered event processing
// Out-of-order events को handle करने के लिए priority queue
type EventPriorityQueue []*MessageEvent

func (pq EventPriorityQueue) Len() int { return len(pq) }

func (pq EventPriorityQueue) Less(i, j int) bool {
	return pq[i].EventTime.Before(pq[j].EventTime)
}

func (pq EventPriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *EventPriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*MessageEvent))
}

func (pq *EventPriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

// OutOfOrderBuffer buffers events and releases them in order
// Out-of-order events को buffer करके correct order में release करता है
type OutOfOrderBuffer struct {
	buffer         *EventPriorityQueue
	maxBufferSize  int
	maxWaitTime    time.Duration
	processor      *EventTimeProcessor
	mutex          sync.Mutex
	lastReleaseTime time.Time
}

func NewOutOfOrderBuffer(maxSize int, maxWait time.Duration, processor *EventTimeProcessor) *OutOfOrderBuffer {
	buffer := make(EventPriorityQueue, 0)
	heap.Init(&buffer)
	
	return &OutOfOrderBuffer{
		buffer:          &buffer,
		maxBufferSize:   maxSize,
		maxWaitTime:     maxWait,
		processor:       processor,
		lastReleaseTime: time.Now(),
	}
}

func (oob *OutOfOrderBuffer) AddEvent(event *MessageEvent) {
	oob.mutex.Lock()
	defer oob.mutex.Unlock()
	
	heap.Push(oob.buffer, event)
	
	// Check if we should release events
	if oob.buffer.Len() >= oob.maxBufferSize || 
	   time.Since(oob.lastReleaseTime) > oob.maxWaitTime {
		oob.releaseEvents()
	}
}

func (oob *OutOfOrderBuffer) releaseEvents() {
	// Release events from buffer in order
	releasedCount := 0
	
	// Release up to half of buffer or all events older than maxWaitTime
	maxRelease := oob.buffer.Len() / 2
	if maxRelease == 0 {
		maxRelease = 1
	}
	
	for i := 0; i < maxRelease && oob.buffer.Len() > 0; i++ {
		event := heap.Pop(oob.buffer).(*MessageEvent)
		oob.processor.ProcessEvent(*event)
		releasedCount++
	}
	
	oob.lastReleaseTime = time.Now()
	
	if releasedCount > 0 {
		log.Printf("📤 Released %d events from out-of-order buffer (remaining: %d)",
			releasedCount, oob.buffer.Len())
	}
}

func (oob *OutOfOrderBuffer) StartPeriodicRelease() {
	go func() {
		ticker := time.NewTicker(oob.maxWaitTime / 2)
		defer ticker.Stop()
		
		for range ticker.C {
			oob.mutex.Lock()
			if time.Since(oob.lastReleaseTime) > oob.maxWaitTime && oob.buffer.Len() > 0 {
				oob.releaseEvents()
			}
			oob.mutex.Unlock()
		}
	}()
}

// WhatsAppEventGenerator generates sample WhatsApp events
// Testing के लिए sample WhatsApp events generate करता है
type WhatsAppEventGenerator struct {
	servers []string
	countries []string
	baseTime time.Time
}

func NewWhatsAppEventGenerator() *WhatsAppEventGenerator {
	return &WhatsAppEventGenerator{
		servers: []string{"WA_SERVER_1", "WA_SERVER_2", "WA_SERVER_3", "WA_SERVER_4", "WA_SERVER_5"},
		countries: []string{"IN", "US", "BR", "ID", "PK", "BD", "NG", "MX", "PH", "ET"},
		baseTime: time.Now(),
	}
}

func (weg *WhatsAppEventGenerator) GenerateEvent() *MessageEvent {
	// Generate realistic message flow: sent -> delivered -> read
	eventTypes := []string{"sent", "delivered", "read", "failed"}
	weights := []float64{0.4, 0.35, 0.2, 0.05} // sent is most common
	
	eventType := weightedRandomChoice(eventTypes, weights)
	
	messageTypes := []string{"text", "image", "video", "audio", "document"}
	messageType := messageTypes[rand.Intn(len(messageTypes))]
	
	// Message size based on type
	var messageSize int64
	switch messageType {
	case "text":
		messageSize = int64(100 + rand.Intn(500))     // 100B to 600B
	case "image":
		messageSize = int64(50000 + rand.Intn(200000)) // 50KB to 250KB
	case "video":
		messageSize = int64(500000 + rand.Intn(5000000)) // 500KB to 5.5MB
	case "audio":
		messageSize = int64(10000 + rand.Intn(100000))   // 10KB to 110KB
	case "document":
		messageSize = int64(100000 + rand.Intn(1000000)) // 100KB to 1.1MB
	}
	
	networkTypes := []string{"wifi", "4g", "3g", "2g"}
	networkWeights := []float64{0.4, 0.45, 0.13, 0.02}
	networkType := weightedRandomChoice(networkTypes, networkWeights)
	
	deviceTypes := []string{"android", "ios", "web"}
	deviceWeights := []float64{0.6, 0.35, 0.05}
	deviceType := weightedRandomChoice(deviceTypes, deviceWeights)
	
	// Simulate out-of-order and late events
	eventTime := weg.baseTime.Add(time.Duration(rand.Intn(10)) * time.Second)
	
	// 20% chance of being out of order (earlier event time)
	if rand.Float64() < 0.2 {
		eventTime = eventTime.Add(-time.Duration(rand.Intn(30)) * time.Second)
	}
	
	// 5% chance of being very late (simulating network issues)
	if rand.Float64() < 0.05 {
		eventTime = eventTime.Add(-time.Duration(rand.Intn(300)) * time.Second)
	}
	
	// Calculate latency for delivery events
	var latencyMs int64
	if eventType == "delivered" || eventType == "read" {
		baseLatency := int64(100) // 100ms base
		networkLatency := map[string]int64{
			"wifi": 50,
			"4g":   200,
			"3g":   800,
			"2g":   2000,
		}
		latencyMs = baseLatency + networkLatency[networkType] + int64(rand.Intn(500))
	}
	
	isGroupMessage := rand.Float64() < 0.3 // 30% group messages
	groupSize := 0
	if isGroupMessage {
		groupSize = 3 + rand.Intn(47) // 3 to 50 members
	}
	
	return &MessageEvent{
		MessageID:       fmt.Sprintf("MSG_%d_%d", time.Now().UnixNano(), rand.Intn(1000)),
		ConversationID:  fmt.Sprintf("CONV_%d", rand.Intn(10000)),
		SenderID:        fmt.Sprintf("USER_%d", rand.Intn(1000000)),
		ReceiverID:      fmt.Sprintf("USER_%d", rand.Intn(1000000)),
		MessageType:     messageType,
		EventType:       eventType,
		EventTime:       eventTime,
		ProcessingTime:  time.Now(),
		MessageSize:     messageSize,
		ServerID:        weg.servers[rand.Intn(len(weg.servers))],
		CountryCode:     weg.countries[rand.Intn(len(weg.countries))],
		NetworkType:     networkType,
		DeviceType:      deviceType,
		IsGroupMessage:  isGroupMessage,
		GroupSize:       groupSize,
		RetryCount:      rand.Intn(3),
		LatencyMs:       latencyMs,
	}
}

func weightedRandomChoice(choices []string, weights []float64) string {
	totalWeight := 0.0
	for _, weight := range weights {
		totalWeight += weight
	}
	
	randomValue := rand.Float64() * totalWeight
	currentWeight := 0.0
	
	for i, weight := range weights {
		currentWeight += weight
		if randomValue <= currentWeight {
			return choices[i]
		}
	}
	
	return choices[len(choices)-1]
}

func main() {
	log.Println("💬 Starting WhatsApp Watermark & Late Data Handling Demo...")
	
	// Initialize components
	windowSize := 30 * time.Second       // 30-second windows
	allowedLateness := 10 * time.Second  // Allow 10 seconds of lateness
	
	processor := NewEventTimeProcessor(windowSize, allowedLateness)
	buffer := NewOutOfOrderBuffer(100, 5*time.Second, processor)
	generator := NewWhatsAppEventGenerator()
	
	// Start periodic processes
	processor.StartPeriodicWatermarkAdvancement()
	buffer.StartPeriodicRelease()
	
	// Start event generation
	go func() {
		ticker := time.NewTicker(100 * time.Millisecond) // 10 events per second
		defer ticker.Stop()
		
		eventCount := 0
		
		for range ticker.C {
			event := generator.GenerateEvent()
			buffer.AddEvent(event)
			eventCount++
			
			if eventCount%100 == 0 {
				log.Printf("📨 Generated %d WhatsApp events", eventCount)
			}
		}
	}()
	
	// Start analytics output monitoring
	go func() {
		for analytics := range processor.outputChannel {
			log.Printf("📊 Window Analytics: %d events (%d late), %.1f%% delivery rate, %dms avg latency",
				analytics["total_events"],
				analytics["late_events"],
				analytics["delivery_rate"],
				analytics["avg_latency_ms"])
		}
	}()
	
	// Start periodic reporting
	go func() {
		ticker := time.NewTicker(20 * time.Second)
		defer ticker.Stop()
		
		for range ticker.C {
			log.Println("\n💬 === WhatsApp Analytics Report ===")
			
			// Active windows
			activeWindows := processor.GetActiveWindows()
			log.Printf("🪟 Active Windows: %d", len(activeWindows))
			
			for i, window := range activeWindows {
				if i >= 3 { break } // Show only first 3
				log.Printf("   Window %d: %s - %s (%d events, %d late)",
					i+1,
					window["window_start"].(string)[11:19], // Just time part
					window["window_end"].(string)[11:19],
					int(window["total_events"].(int64)),
					int(window["late_events"].(int64)))
			}
			
			// Late data statistics
			lateStats := processor.GetLateDataStatistics()
			log.Printf("🕐 Late Data Stats:")
			log.Printf("   Total Late Events: %d", lateStats["total_late_events"])
			log.Printf("   Avg Lateness: %dms", lateStats["avg_lateness_ms"])
			log.Printf("   Max Lateness: %dms", lateStats["max_lateness_ms"])
			
			// Buffer status
			buffer.mutex.Lock()
			bufferSize := buffer.buffer.Len()
			buffer.mutex.Unlock()
			log.Printf("📦 Out-of-Order Buffer: %d events", bufferSize)
			
			log.Println("=====================================")
		}
	}()
	
	// Run simulation
	log.Println("🎭 Running WhatsApp message flow simulation...")
	log.Printf("🪟 Window Size: %v", windowSize)
	log.Printf("⏰ Allowed Lateness: %v", allowedLateness)
	log.Println("📱 Simulating message delivery with out-of-order and late events")
	
	time.Sleep(3 * time.Minute) // Run for 3 minutes
	
	// Final statistics
	log.Println("\n🏁 === Final Statistics ===")
	
	finalLateStats := processor.GetLateDataStatistics()
	finalActiveWindows := processor.GetActiveWindows()
	
	summary := map[string]interface{}{
		"final_late_data_stats": finalLateStats,
		"active_windows_count":  len(finalActiveWindows),
		"simulation_duration":   "3 minutes",
		"window_size":          windowSize.String(),
		"allowed_lateness":     allowedLateness.String(),
	}
	
	summaryJSON, _ := json.MarshalIndent(summary, "", "  ")
	log.Printf("📋 Final Summary:\n%s", summaryJSON)
	
	// Clean shutdown
	processor.Stop()
	
	log.Println("✅ WhatsApp Watermark & Late Data Handling Demo completed!")
}

/*
Key Features Demonstrated:

1. Watermark Management:
   - Per-source watermark tracking
   - Global watermark calculation (minimum of all sources)
   - Monotonic watermark advancement
   - Watermark-based window finalization

2. Late Data Handling:
   - Configurable allowed lateness period
   - Late event detection and tracking
   - Late data buffer for analysis
   - Statistics on late arrivals

3. Out-of-Order Processing:
   - Priority queue-based event buffering
   - Ordered event release mechanism
   - Configurable buffer size and wait time
   - Automatic periodic buffer flushing

4. Event-Time Windows:
   - Fixed-size tumbling windows
   - Event-time based window assignment
   - Window state management with analytics
   - Automatic window cleanup

5. WhatsApp-Specific Metrics:
   - Message delivery rate calculation
   - Read receipt tracking
   - Network-type analysis
   - Country-wise statistics
   - Device-type breakdowns
   - Message size analytics

6. Production Features:
   - Thread-safe concurrent processing
   - Configurable lateness tolerance
   - Memory-efficient window management
   - Comprehensive monitoring and logging
   - Graceful shutdown handling

This system handles realistic WhatsApp traffic patterns with:
- 10+ events per second
- 20% out-of-order events
- 5% very late events (network issues)
- Multiple server sources
- Global user distribution

The watermark mechanism ensures correct event-time processing
while handling the inevitable out-of-order and late data in
distributed messaging systems.
*/
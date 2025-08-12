/*
IPL Late Data Handling with Watermarks in Go
यह system late arriving IPL data को handle करता है watermarks का use करके
Example: Commentary delay, satellite feed issues, mobile network problems

Mumbai monsoon की तरह - कभी-कभी data भी late आता है, but हमें handle करना पड़ता है!
*/

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"sort"
	"sync"
	"time"

	"github.com/segmentio/kafka-go"
)

// IPLEvent represents cricket event with timing information
type IPLEvent struct {
	EventID     string    `json:"event_id"`
	MatchID     string    `json:"match_id"`
	EventType   string    `json:"event_type"` // BALL, WICKET, BOUNDARY, MILESTONE
	EventTime   time.Time `json:"event_time"` // When event actually happened
	ProcessTime time.Time `json:"process_time"` // When system received it
	Over        int       `json:"over"`
	Ball        int       `json:"ball"`
	Batsman     string    `json:"batsman"`
	Bowler      string    `json:"bowler"`
	Runs        int       `json:"runs"`
	IsWicket    bool      `json:"is_wicket"`
	Commentary  string    `json:"commentary"`
	Source      string    `json:"source"` // TV, RADIO, MOBILE, SATELLITE
	Priority    int       `json:"priority"` // 1=Critical, 2=Important, 3=Normal
}

// WatermarkStrategy defines different watermark generation strategies
type WatermarkStrategy interface {
	GenerateWatermark(events []IPLEvent, currentTime time.Time) time.Time
	GetMaxOutOfOrder() time.Duration
	GetStrategyName() string
}

// FixedDelayWatermarkStrategy - simple fixed delay watermark
type FixedDelayWatermarkStrategy struct {
	delay time.Duration
}

func (f *FixedDelayWatermarkStrategy) GenerateWatermark(events []IPLEvent, currentTime time.Time) time.Time {
	return currentTime.Add(-f.delay)
}

func (f *FixedDelayWatermarkStrategy) GetMaxOutOfOrder() time.Duration {
	return f.delay
}

func (f *FixedDelayWatermarkStrategy) GetStrategyName() string {
	return fmt.Sprintf("FixedDelay(%v)", f.delay)
}

// PercentileWatermarkStrategy - percentile-based watermark
type PercentileWatermarkStrategy struct {
	percentile      float64
	minDelay        time.Duration
	maxDelay        time.Duration
	recentLatencies []time.Duration
	mu              sync.RWMutex
}

func (p *PercentileWatermarkStrategy) GenerateWatermark(events []IPLEvent, currentTime time.Time) time.Time {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	// Update recent latencies
	for _, event := range events {
		latency := event.ProcessTime.Sub(event.EventTime)
		if latency > 0 {
			p.recentLatencies = append(p.recentLatencies, latency)
		}
	}
	
	// Keep only recent latencies (last 1000)
	if len(p.recentLatencies) > 1000 {
		p.recentLatencies = p.recentLatencies[len(p.recentLatencies)-1000:]
	}
	
	if len(p.recentLatencies) == 0 {
		return currentTime.Add(-p.minDelay)
	}
	
	// Calculate percentile
	sortedLatencies := make([]time.Duration, len(p.recentLatencies))
	copy(sortedLatencies, p.recentLatencies)
	sort.Slice(sortedLatencies, func(i, j int) bool {
		return sortedLatencies[i] < sortedLatencies[j]
	})
	
	index := int(float64(len(sortedLatencies)) * p.percentile / 100.0)
	if index >= len(sortedLatencies) {
		index = len(sortedLatencies) - 1
	}
	
	percentileLatency := sortedLatencies[index]
	
	// Apply min/max bounds
	if percentileLatency < p.minDelay {
		percentileLatency = p.minDelay
	}
	if percentileLatency > p.maxDelay {
		percentileLatency = p.maxDelay
	}
	
	return currentTime.Add(-percentileLatency)
}

func (p *PercentileWatermarkStrategy) GetMaxOutOfOrder() time.Duration {
	return p.maxDelay
}

func (p *PercentileWatermarkStrategy) GetStrategyName() string {
	return fmt.Sprintf("Percentile(P%.1f)", p.percentile)
}

// AdaptiveWatermarkStrategy - adaptive watermark based on network conditions
type AdaptiveWatermarkStrategy struct {
	baseDelay        time.Duration
	adaptionFactor   float64
	networkLatencies map[string]time.Duration // source -> average latency
	mu               sync.RWMutex
}

func (a *AdaptiveWatermarkStrategy) GenerateWatermark(events []IPLEvent, currentTime time.Time) time.Time {
	a.mu.Lock()
	defer a.mu.Unlock()
	
	// Update network latencies per source
	sourceCounts := make(map[string]int)
	sourceTotalLatency := make(map[string]time.Duration)
	
	for _, event := range events {
		latency := event.ProcessTime.Sub(event.EventTime)
		if latency > 0 {
			sourceCounts[event.Source]++
			sourceTotalLatency[event.Source] += latency
		}
	}
	
	// Calculate average latency per source
	for source, count := range sourceCounts {
		if count > 0 {
			avgLatency := sourceTotalLatency[source] / time.Duration(count)
			if a.networkLatencies == nil {
				a.networkLatencies = make(map[string]time.Duration)
			}
			
			// Exponential moving average
			if existing, exists := a.networkLatencies[source]; exists {
				a.networkLatencies[source] = time.Duration(
					float64(existing)*0.7 + float64(avgLatency)*0.3)
			} else {
				a.networkLatencies[source] = avgLatency
			}
		}
	}
	
	// Find maximum latency across sources
	maxLatency := a.baseDelay
	for _, latency := range a.networkLatencies {
		if latency > maxLatency {
			maxLatency = latency
		}
	}
	
	// Apply adaption factor
	adaptedDelay := time.Duration(float64(maxLatency) * a.adaptionFactor)
	
	return currentTime.Add(-adaptedDelay)
}

func (a *AdaptiveWatermarkStrategy) GetMaxOutOfOrder() time.Duration {
	return time.Duration(float64(a.baseDelay) * a.adaptionFactor * 2)
}

func (a *AdaptiveWatermarkStrategy) GetStrategyName() string {
	return fmt.Sprintf("Adaptive(base=%v, factor=%.2f)", a.baseDelay, a.adaptionFactor)
}

// LateDataHandler handles different strategies for late data
type LateDataHandler struct {
	strategy           string // DROP, REPROCESS, SIDE_OUTPUT
	allowedLateness    time.Duration
	lateEventCount     int64
	reprocessedCount   int64
	droppedCount       int64
	mu                 sync.RWMutex
}

// LateDataAction represents action taken on late data
type LateDataAction struct {
	Action    string    `json:"action"`    // DROP, REPROCESS, SIDE_OUTPUT
	Event     IPLEvent  `json:"event"`
	Reason    string    `json:"reason"`
	Lateness  time.Duration `json:"lateness"`
	Timestamp time.Time `json:"timestamp"`
}

// IPLWatermarkProcessor processes IPL events with watermark-based late data handling
type IPLWatermarkProcessor struct {
	watermarkStrategy WatermarkStrategy
	lateDataHandler   *LateDataHandler
	eventBuffer       []IPLEvent
	bufferMutex       sync.RWMutex
	currentWatermark  time.Time
	processedWindows  map[string]bool // Track processed windows to avoid reprocessing
	sideOutputChannel chan LateDataAction
	ctx               context.Context
	cancel            context.CancelFunc
}

// NewIPLWatermarkProcessor creates new watermark processor
func NewIPLWatermarkProcessor(strategy WatermarkStrategy, lateDataStrategy string) *IPLWatermarkProcessor {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &IPLWatermarkProcessor{
		watermarkStrategy: strategy,
		lateDataHandler: &LateDataHandler{
			strategy:        lateDataStrategy,
			allowedLateness: 30 * time.Second, // 30 seconds allowed lateness
		},
		eventBuffer:      make([]IPLEvent, 0),
		processedWindows: make(map[string]bool),
		sideOutputChannel: make(chan LateDataAction, 100),
		ctx:              ctx,
		cancel:           cancel,
	}
}

// AddEvent adds event to buffer
func (processor *IPLWatermarkProcessor) AddEvent(event IPLEvent) {
	processor.bufferMutex.Lock()
	defer processor.bufferMutex.Unlock()
	
	event.ProcessTime = time.Now()
	processor.eventBuffer = append(processor.eventBuffer, event)
	
	// Update watermark
	processor.updateWatermark()
	
	fmt.Printf("📡 Event added: %s %s (Buffer: %d, Watermark: %s)\n", 
		event.EventType, event.EventTime.Format("15:04:05.000"), 
		len(processor.eventBuffer), processor.currentWatermark.Format("15:04:05.000"))
}

// updateWatermark updates current watermark based on strategy
func (processor *IPLWatermarkProcessor) updateWatermark() {
	newWatermark := processor.watermarkStrategy.GenerateWatermark(
		processor.eventBuffer, time.Now())
	
	// Watermark can only advance (monotonic property)
	if newWatermark.After(processor.currentWatermark) {
		oldWatermark := processor.currentWatermark
		processor.currentWatermark = newWatermark
		
		if !oldWatermark.IsZero() {
			fmt.Printf("💧 Watermark advanced: %s -> %s (Strategy: %s)\n", 
				oldWatermark.Format("15:04:05.000"), 
				newWatermark.Format("15:04:05.000"),
				processor.watermarkStrategy.GetStrategyName())
		}
	}
}

// ProcessEvents processes events based on watermarks
func (processor *IPLWatermarkProcessor) ProcessEvents() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()
	
	fmt.Println("🚀 Watermark-based event processing शुरू हो गई...")
	
	for {
		select {
		case <-ticker.C:
			processor.processReadyEvents()
		case <-processor.ctx.Done():
			fmt.Println("🛑 Watermark processor बंद हो रहा है...")
			return
		}
	}
}

// processReadyEvents processes events that are ready based on watermark
func (processor *IPLWatermarkProcessor) processReadyEvents() {
	processor.bufferMutex.Lock()
	defer processor.bufferMutex.Unlock()
	
	if processor.currentWatermark.IsZero() || len(processor.eventBuffer) == 0 {
		return
	}
	
	var readyEvents []IPLEvent
	var lateEvents []IPLEvent
	var futureEvents []IPLEvent
	
	// Separate events into ready, late, and future
	for _, event := range processor.eventBuffer {
		if event.EventTime.Before(processor.currentWatermark) || 
		   event.EventTime.Equal(processor.currentWatermark) {
			// Event is ready for processing
			readyEvents = append(readyEvents, event)
		} else {
			// Check if event is late (arrived after watermark for its window)
			lateness := time.Since(event.EventTime)
			if lateness > processor.lateDataHandler.allowedLateness {
				lateEvents = append(lateEvents, event)
			} else {
				futureEvents = append(futureEvents, event)
			}
		}
	}
	
	// Process ready events
	if len(readyEvents) > 0 {
		processor.processEventBatch(readyEvents, false)
	}
	
	// Handle late events
	if len(lateEvents) > 0 {
		processor.handleLateEvents(lateEvents)
	}
	
	// Keep future events in buffer
	processor.eventBuffer = futureEvents
	
	fmt.Printf("⚡ Processed: %d ready, %d late, %d buffered\n", 
		len(readyEvents), len(lateEvents), len(futureEvents))
}

// handleLateEvents handles late arriving events based on strategy
func (processor *IPLWatermarkProcessor) handleLateEvents(lateEvents []IPLEvent) {
	processor.lateDataHandler.mu.Lock()
	defer processor.lateDataHandler.mu.Unlock()
	
	for _, event := range lateEvents {
		lateness := time.Since(event.EventTime)
		
		switch processor.lateDataHandler.strategy {
		case "DROP":
			processor.lateDataHandler.droppedCount++
			action := LateDataAction{
				Action:    "DROP",
				Event:     event,
				Reason:    "Exceeded allowed lateness",
				Lateness:  lateness,
				Timestamp: time.Now(),
			}
			processor.sendToSideOutput(action)
			
			fmt.Printf("🗑️ DROPPED late event: %s (Late by: %v)\n", 
				event.EventType, lateness)
				
		case "REPROCESS":
			processor.lateDataHandler.reprocessedCount++
			// Reprocess the event (might trigger window recalculation)
			processor.processEventBatch([]IPLEvent{event}, true)
			
			action := LateDataAction{
				Action:    "REPROCESS",
				Event:     event,
				Reason:    "Reprocessed late event",
				Lateness:  lateness,
				Timestamp: time.Now(),
			}
			processor.sendToSideOutput(action)
			
			fmt.Printf("🔄 REPROCESSED late event: %s (Late by: %v)\n", 
				event.EventType, lateness)
				
		case "SIDE_OUTPUT":
			processor.lateDataHandler.lateEventCount++
			action := LateDataAction{
				Action:    "SIDE_OUTPUT",
				Event:     event,
				Reason:    "Sent to side output for special handling",
				Lateness:  lateness,
				Timestamp: time.Now(),
			}
			processor.sendToSideOutput(action)
			
			fmt.Printf("📤 SIDE_OUTPUT late event: %s (Late by: %v)\n", 
				event.EventType, lateness)
		}
	}
}

// processEventBatch processes a batch of events
func (processor *IPLWatermarkProcessor) processEventBatch(events []IPLEvent, isReprocessing bool) {
	// Sort events by event time
	sort.Slice(events, func(i, j int) bool {
		return events[i].EventTime.Before(events[j].EventTime)
	})
	
	// Process events by over (windowing)
	overGroups := make(map[int][]IPLEvent)
	for _, event := range events {
		overGroups[event.Over] = append(overGroups[event.Over], event)
	}
	
	for over, overEvents := range overGroups {
		windowKey := fmt.Sprintf("over_%d", over)
		
		// Check if already processed (to avoid duplicate processing)
		if !isReprocessing && processor.processedWindows[windowKey] {
			continue
		}
		
		processor.processOverWindow(over, overEvents, isReprocessing)
		processor.processedWindows[windowKey] = true
	}
}

// processOverWindow processes events for a specific over
func (processor *IPLWatermarkProcessor) processOverWindow(over int, events []IPLEvent, isReprocessing bool) {
	totalRuns := 0
	wickets := 0
	boundaries := 0
	
	reprocessFlag := ""
	if isReprocessing {
		reprocessFlag = " [REPROCESSED]"
	}
	
	fmt.Printf("🏏 Processing Over %d%s (%d events):\n", over, reprocessFlag, len(events))
	
	for _, event := range events {
		totalRuns += event.Runs
		if event.IsWicket {
			wickets++
		}
		if event.Runs == 4 || event.Runs == 6 {
			boundaries++
		}
		
		latency := event.ProcessTime.Sub(event.EventTime)
		fmt.Printf("  Ball %d: %s - %d runs%s (Latency: %v)\n", 
			event.Ball, event.Batsman, event.Runs, 
			func() string {
				if event.IsWicket { return " WICKET" }
				return ""
			}(), latency)
	}
	
	fmt.Printf("📊 Over %d Summary%s: %d runs, %d wickets, %d boundaries\n", 
		over, reprocessFlag, totalRuns, wickets, boundaries)
	
	// Publish over summary (to Kafka, database, etc.)
	processor.publishOverSummary(over, totalRuns, wickets, boundaries, isReprocessing)
}

// publishOverSummary publishes over summary
func (processor *IPLWatermarkProcessor) publishOverSummary(over, runs, wickets, boundaries int, isReprocessing bool) {
	summary := map[string]interface{}{
		"over":           over,
		"runs":          runs,
		"wickets":       wickets,
		"boundaries":    boundaries,
		"is_reprocessed": isReprocessing,
		"watermark":     processor.currentWatermark,
		"timestamp":     time.Now(),
	}
	
	// यहाँ actual publishing logic होगी
	// Kafka, Redis, Database में send करना
	fmt.Printf("📤 Publishing over summary: %+v\n", summary)
}

// sendToSideOutput sends action to side output channel
func (processor *IPLWatermarkProcessor) sendToSideOutput(action LateDataAction) {
	select {
	case processor.sideOutputChannel <- action:
	default:
		fmt.Println("⚠️ Side output channel full, dropping action")
	}
}

// GetSideOutput returns channel for late data actions
func (processor *IPLWatermarkProcessor) GetSideOutput() <-chan LateDataAction {
	return processor.sideOutputChannel
}

// GetStatistics returns processing statistics
func (processor *IPLWatermarkProcessor) GetStatistics() map[string]interface{} {
	processor.lateDataHandler.mu.RLock()
	defer processor.lateDataHandler.mu.RUnlock()
	
	return map[string]interface{}{
		"current_watermark":    processor.currentWatermark,
		"strategy":            processor.watermarkStrategy.GetStrategyName(),
		"late_data_strategy":  processor.lateDataHandler.strategy,
		"events_dropped":      processor.lateDataHandler.droppedCount,
		"events_reprocessed":  processor.lateDataHandler.reprocessedCount,
		"late_events":         processor.lateDataHandler.lateEventCount,
		"buffer_size":         len(processor.eventBuffer),
		"processed_windows":   len(processor.processedWindows),
	}
}

// Stop stops the processor
func (processor *IPLWatermarkProcessor) Stop() {
	processor.cancel()
	close(processor.sideOutputChannel)
}

// MonitorLateDataActions monitors side output for late data handling
func MonitorLateDataActions(sideOutput <-chan LateDataAction) {
	fmt.Println("📊 Late data monitoring शुरू हो गया...")
	
	actionCounts := make(map[string]int)
	sourceLateness := make(map[string][]time.Duration)
	
	for action := range sideOutput {
		actionCounts[action.Action]++
		
		// Track lateness by source
		source := action.Event.Source
		if sourceLateness[source] == nil {
			sourceLateness[source] = make([]time.Duration, 0)
		}
		sourceLateness[source] = append(sourceLateness[source], action.Lateness)
		
		fmt.Printf("🚨 Late data action: %s for %s event (Late by: %v, Source: %s)\n", 
			action.Action, action.Event.EventType, action.Lateness, source)
		
		// Print periodic statistics
		total := 0
		for _, count := range actionCounts {
			total += count
		}
		
		if total%10 == 0 { // Every 10 actions
			fmt.Printf("\n📈 LATE DATA STATISTICS (Total: %d):\n", total)
			for action, count := range actionCounts {
				fmt.Printf("  %s: %d (%.1f%%)\n", action, count, float64(count)*100/float64(total))
			}
			
			fmt.Println("Source lateness analysis:")
			for source, latencies := range sourceLateness {
				if len(latencies) > 0 {
					avg := time.Duration(0)
					max := time.Duration(0)
					for _, latency := range latencies {
						avg += latency
						if latency > max {
							max = latency
						}
					}
					avg /= time.Duration(len(latencies))
					fmt.Printf("  %s: avg=%v, max=%v, count=%d\n", source, avg, max, len(latencies))
				}
			}
			fmt.Println("---")
		}
	}
}

// ConsumeIPLEvents consumes IPL events from Kafka
func ConsumeIPLEvents(processor *IPLWatermarkProcessor) {
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers:  []string{"localhost:9092"},
		Topic:    "ipl-late-data-events",
		GroupID:  "watermark-processor",
		MinBytes: 10e3, // 10KB
		MaxBytes: 10e6, // 10MB
	})
	defer reader.Close()
	
	fmt.Println("📡 Consuming IPL events from Kafka...")
	
	for {
		msg, err := reader.ReadMessage(context.Background())
		if err != nil {
			fmt.Printf("❌ Error reading message: %v\n", err)
			continue
		}
		
		var event IPLEvent
		if err := json.Unmarshal(msg.Value, &event); err != nil {
			fmt.Printf("❌ Error unmarshaling event: %v\n", err)
			continue
		}
		
		processor.AddEvent(event)
	}
}

// GenerateIPLEventsWithLateness generates sample IPL events with various lateness patterns
func GenerateIPLEventsWithLateness() {
	writer := kafka.NewWriter(kafka.WriterConfig{
		Brokers: []string{"localhost:9092"},
		Topic:   "ipl-late-data-events",
	})
	defer writer.Close()
	
	matchID := "MI_vs_CSK_Watermark_Test"
	sources := []string{"TV", "RADIO", "MOBILE", "SATELLITE"}
	
	fmt.Println("🏏 Generating IPL events with different lateness patterns...")
	
	for over := 1; over <= 5; over++ {
		for ball := 1; ball <= 6; ball++ {
			// Create event with actual event time
			eventTime := time.Now().Add(-time.Duration(30-over*5) * time.Second)
			
			event := IPLEvent{
				EventID:    fmt.Sprintf("over_%d_ball_%d", over, ball),
				MatchID:    matchID,
				EventType:  "BALL",
				EventTime:  eventTime,
				Over:       over,
				Ball:       ball,
				Batsman:    "Rohit Sharma",
				Bowler:     "Deepak Chahar",
				Runs:       []int{0, 1, 2, 4, 6}[ball%5],
				IsWicket:   ball == 6 && over%2 == 0, // Wicket on last ball of even overs
				Commentary: fmt.Sprintf("Over %d, Ball %d commentary", over, ball),
				Source:     sources[ball%4],
				Priority:   1,
			}
			
			// Add some lateness patterns
			var delay time.Duration
			switch event.Source {
			case "TV":
				delay = time.Duration(1+ball) * time.Second // 1-6 seconds delay
			case "RADIO": 
				delay = time.Duration(2+over) * time.Second // 2-7 seconds delay
			case "MOBILE":
				delay = time.Duration(5+ball*2) * time.Second // 5-15 seconds delay
			case "SATELLITE":
				delay = time.Duration(10+over*3) * time.Second // 10-25 seconds delay
			}
			
			// Sometimes add extra random delay to simulate network issues
			if ball%3 == 0 {
				delay += time.Duration(10+over*5) * time.Second
			}
			
			// Sleep to simulate delay
			time.Sleep(delay / 10) // Accelerated for demo
			
			eventJSON, _ := json.Marshal(event)
			
			err := writer.WriteMessages(context.Background(), kafka.Message{
				Key:   []byte(event.EventID),
				Value: eventJSON,
			})
			
			if err != nil {
				fmt.Printf("❌ Error sending event: %v\n", err)
			} else {
				actualLateness := time.Since(event.EventTime)
				fmt.Printf("📤 Sent: Over %d.%d (%s, Lateness: %v)\n", 
					over, ball, event.Source, actualLateness)
			}
		}
	}
	
	fmt.Println("✅ Generated IPL events with lateness patterns!")
}

func main() {
	if len(os.Args) > 1 && os.Args[1] == "--generate-data" {
		GenerateIPLEventsWithLateness()
		return
	}
	
	// Choose watermark strategy
	var strategy WatermarkStrategy
	strategyType := "adaptive" // fixed, percentile, adaptive
	
	switch strategyType {
	case "fixed":
		strategy = &FixedDelayWatermarkStrategy{delay: 15 * time.Second}
	case "percentile":
		strategy = &PercentileWatermarkStrategy{
			percentile: 95.0,
			minDelay:   5 * time.Second,
			maxDelay:   30 * time.Second,
		}
	case "adaptive":
		strategy = &AdaptiveWatermarkStrategy{
			baseDelay:      10 * time.Second,
			adaptionFactor: 1.5,
		}
	}
	
	// Choose late data handling strategy
	lateDataStrategy := "SIDE_OUTPUT" // DROP, REPROCESS, SIDE_OUTPUT
	
	// Create processor
	processor := NewIPLWatermarkProcessor(strategy, lateDataStrategy)
	
	// Start monitoring late data actions
	go MonitorLateDataActions(processor.GetSideOutput())
	
	// Start processing
	go processor.ProcessEvents()
	
	// Start consuming events
	go ConsumeIPLEvents(processor)
	
	// Periodic statistics
	go func() {
		ticker := time.NewTicker(30 * time.Second)
		defer ticker.Stop()
		
		for range ticker.C {
			stats := processor.GetStatistics()
			fmt.Printf("\n📊 PROCESSOR STATISTICS:\n")
			for key, value := range stats {
				fmt.Printf("  %s: %v\n", key, value)
			}
			fmt.Println("---")
		}
	}()
	
	fmt.Printf("🏏 IPL Late Data Handler शुरू हो गया! (Strategy: %s, Late Data: %s)\n", 
		strategy.GetStrategyName(), lateDataStrategy)
	fmt.Println("Press Ctrl+C to stop...")
	
	// Wait for interrupt
	select {}
}
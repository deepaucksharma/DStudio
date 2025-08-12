/*
IPL Replay Synchronization - Event Time Processing in Go
यह system IPL match के replay events को proper time order में synchronize करता है
Example: Different camera feeds, commentary tracks, statistics को sync करना

Mumbai local train scheduling जैसे - सब कुछ time के हिसाब से perfectly aligned होना चाहिए!
*/

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sort"
	"sync"
	"time"

	"github.com/segmentio/kafka-go"
)

// EventTimeData represents time-stamped cricket event
type EventTimeData struct {
	EventID     string    `json:"event_id"`
	MatchID     string    `json:"match_id"`
	EventType   string    `json:"event_type"` // BALL, COMMENTARY, CAMERA_SWITCH, GRAPHICS
	EventTime   time.Time `json:"event_time"`
	ProcessTime time.Time `json:"process_time"`
	Source      string    `json:"source"`      // MAIN_CAMERA, STUMP_CAM, COMMENTARY, STATS
	Data        string    `json:"data"`        // Actual event content
	Priority    int       `json:"priority"`    // 1=Critical, 2=Important, 3=Normal
	Sequence    int64     `json:"sequence"`    // Sequence number for ordering
}

// WatermarkTracker tracks watermarks for different event sources
type WatermarkTracker struct {
	mu         sync.RWMutex
	watermarks map[string]time.Time // source -> watermark
	sources    []string
}

// EventTimeProcessor handles event time processing and synchronization
type EventTimeProcessor struct {
	watermarkTracker *WatermarkTracker
	eventBuffer      []EventTimeData
	bufferMutex      sync.RWMutex
	maxOutOfOrder    time.Duration // Maximum allowed out-of-order delay
	checkpointInterval time.Duration
	outputChannel    chan []EventTimeData
	ctx              context.Context
	cancel           context.CancelFunc
}

// NewEventTimeProcessor creates new event time processor
func NewEventTimeProcessor() *EventTimeProcessor {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &EventTimeProcessor{
		watermarkTracker: &WatermarkTracker{
			watermarks: make(map[string]time.Time),
			sources:    []string{"MAIN_CAMERA", "STUMP_CAM", "COMMENTARY", "STATS", "GRAPHICS"},
		},
		eventBuffer:        make([]EventTimeData, 0),
		maxOutOfOrder:      10 * time.Second, // 10 seconds maximum out-of-order
		checkpointInterval: 5 * time.Second,  // Process every 5 seconds
		outputChannel:      make(chan []EventTimeData, 100),
		ctx:                ctx,
		cancel:             cancel,
	}
}

// UpdateWatermark updates watermark for a source
func (wt *WatermarkTracker) UpdateWatermark(source string, timestamp time.Time) {
	wt.mu.Lock()
	defer wt.mu.Unlock()
	
	// Watermark can only move forward (monotonic property)
	if current, exists := wt.watermarks[source]; !exists || timestamp.After(current) {
		wt.watermarks[source] = timestamp
		fmt.Printf("📊 Watermark updated for %s: %s\n", source, timestamp.Format("15:04:05.000"))
	}
}

// GetGlobalWatermark returns minimum watermark across all sources
func (wt *WatermarkTracker) GetGlobalWatermark() time.Time {
	wt.mu.RLock()
	defer wt.mu.RUnlock()
	
	var minWatermark time.Time
	firstSource := true
	
	for _, source := range wt.sources {
		if watermark, exists := wt.watermarks[source]; exists {
			if firstSource || watermark.Before(minWatermark) {
				minWatermark = watermark
				firstSource = false
			}
		}
	}
	
	return minWatermark
}

// AddEvent adds event to buffer for processing
func (etp *EventTimeProcessor) AddEvent(event EventTimeData) {
	etp.bufferMutex.Lock()
	defer etp.bufferMutex.Unlock()
	
	// Add processing timestamp
	event.ProcessTime = time.Now()
	
	// Insert event maintaining time order
	etp.eventBuffer = append(etp.eventBuffer, event)
	
	// Update watermark for this source
	etp.watermarkTracker.UpdateWatermark(event.Source, event.EventTime)
	
	fmt.Printf("🎬 Event added: %s from %s at %s (Buffer size: %d)\n", 
		event.EventType, event.Source, event.EventTime.Format("15:04:05.000"), len(etp.eventBuffer))
}

// ProcessEvents processes events based on watermarks and event time
func (etp *EventTimeProcessor) ProcessEvents() {
	ticker := time.NewTicker(etp.checkpointInterval)
	defer ticker.Stop()
	
	fmt.println("🚀 Event time processing शुरू हो गई...")
	
	for {
		select {
		case <-ticker.C:
			etp.processBufferedEvents()
		case <-etp.ctx.Done():
			fmt.println("🛑 Event time processor band ho raha hai...")
			return
		}
	}
}

// processBufferedEvents processes events that are ready based on watermarks
func (etp *EventTimeProcessor) processBufferedEvents() {
	etp.bufferMutex.Lock()
	defer etp.bufferMutex.Unlock()
	
	if len(etp.eventBuffer) == 0 {
		return
	}
	
	globalWatermark := etp.watermarkTracker.GetGlobalWatermark()
	if globalWatermark.IsZero() {
		return // No watermarks available yet
	}
	
	// Find events that can be processed (event_time <= watermark - max_out_of_order)
	processThreshold := globalWatermark.Add(-etp.maxOutOfOrder)
	
	var readyEvents []EventTimeData
	var remainingEvents []EventTimeData
	
	for _, event := range etp.eventBuffer {
		if event.EventTime.Before(processThreshold) || event.EventTime.Equal(processThreshold) {
			readyEvents = append(readyEvents, event)
		} else {
			remainingEvents = append(remainingEvents, event)
		}
	}
	
	if len(readyEvents) > 0 {
		// Sort ready events by event time
		sort.Slice(readyEvents, func(i, j int) bool {
			return readyEvents[i].EventTime.Before(readyEvents[j].EventTime)
		})
		
		fmt.Printf("⚡ Processing %d events (Watermark: %s, Threshold: %s)\n", 
			len(readyEvents), globalWatermark.Format("15:04:05.000"), processThreshold.Format("15:04:05.000"))
		
		// Process events in chronological order
		etp.processEventBatch(readyEvents)
		
		// Send to output channel
		select {
		case etp.outputChannel <- readyEvents:
		default:
			fmt.println("⚠️ Output channel full, dropping batch")
		}
	}
	
	// Keep unprocessed events in buffer
	etp.eventBuffer = remainingEvents
}

// processEventBatch processes a batch of time-ordered events
func (etp *EventTimeProcessor) processEventBatch(events []EventTimeData) {
	for _, event := range events {
		etp.processIndividualEvent(event)
	}
}

// processIndividualEvent processes individual event based on type
func (etp *EventTimeProcessor) processIndividualEvent(event EventTimeData) {
	latency := time.Since(event.EventTime)
	
	fmt.Printf("🎯 Processing: %s | %s | %s | Latency: %v\n", 
		event.EventType, event.Source, event.EventTime.Format("15:04:05.000"), latency)
	
	switch event.EventType {
	case "BALL":
		etp.processBallEvent(event)
	case "COMMENTARY":
		etp.processCommentaryEvent(event)
	case "CAMERA_SWITCH":
		etp.processCameraSwitchEvent(event)
	case "GRAPHICS":
		etp.processGraphicsEvent(event)
	case "MILESTONE":
		etp.processMilestoneEvent(event)
	default:
		fmt.Printf("⚠️ Unknown event type: %s\n", event.EventType)
	}
}

// processBallEvent processes cricket ball events
func (etp *EventTimeProcessor) processBallEvent(event EventTimeData) {
	var ballData map[string]interface{}
	if err := json.Unmarshal([]byte(event.Data), &ballData); err != nil {
		fmt.Printf("❌ Error parsing ball data: %v\n", err)
		return
	}
	
	fmt.Printf("🏏 Ball Event: Over %v.%v - %v runs by %s\n", 
		ballData["over"], ballData["ball"], ballData["runs"], ballData["batsman"])
	
	// यहाँ actual ball processing logic होगी
	// जैसे score update, statistics calculation, etc.
}

// processCommentaryEvent processes commentary events
func (etp *EventTimeProcessor) processCommentaryEvent(event EventTimeData) {
	fmt.Printf("🎤 Commentary: %s\n", event.Data)
	
	// Commentary को proper timing पर sync करना
	// Audio/video streams के साथ align करना
}

// processCameraSwitchEvent processes camera switching events
func (etp *EventTimeProcessor) processCameraSwitchEvent(event EventTimeData) {
	var cameraData map[string]interface{}
	if err := json.Unmarshal([]byte(event.Data), &cameraData); err != nil {
		fmt.Printf("❌ Error parsing camera data: %v\n", err)
		return
	}
	
	fmt.Printf("📹 Camera Switch: %s -> %s\n", cameraData["from"], cameraData["to"])
	
	// Video feed switching logic
}

// processGraphicsEvent processes graphics overlay events
func (etp *EventTimeProcessor) processGraphicsEvent(event EventTimeData) {
	fmt.Printf("📊 Graphics: %s\n", event.Data)
	
	// Scoreboard, statistics graphics को display करना
}

// processMilestoneEvent processes milestone events (fifty, wicket, etc.)
func (etp *EventTimeProcessor) processMilestoneEvent(event EventTimeData) {
	var milestoneData map[string]interface{}
	if err := json.Unmarshal([]byte(event.Data), &milestoneData); err != nil {
		fmt.Printf("❌ Error parsing milestone data: %v\n", err)
		return
	}
	
	fmt.Printf("🎉 Milestone: %s achieved %s!\n", milestoneData["player"], milestoneData["achievement"])
	
	// Special graphics, replays, celebrations trigger करना
}

// GetProcessedEvents returns channel for processed events
func (etp *EventTimeProcessor) GetProcessedEvents() <-chan []EventTimeData {
	return etp.outputChannel
}

// Stop stops the event processor
func (etp *EventTimeProcessor) Stop() {
	etp.cancel()
}

// ConsumeKafkaEvents consumes events from Kafka
func ConsumeKafkaEvents(processor *EventTimeProcessor) {
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers:   []string{"localhost:9092"},
		Topic:     "ipl-replay-events",
		GroupID:   "event-time-processor",
		MinBytes:  10e3, // 10KB
		MaxBytes:  10e6, // 10MB
		MaxWait:   1 * time.Second,
	})
	defer reader.Close()
	
	fmt.println("📡 Kafka event consumption शुरू हो गया...")
	
	for {
		msg, err := reader.ReadMessage(context.Background())
		if err != nil {
			fmt.Printf("❌ Error reading message: %v\n", err)
			continue
		}
		
		var event EventTimeData
		if err := json.Unmarshal(msg.Value, &event); err != nil {
			fmt.Printf("❌ Error unmarshaling event: %v\n", err)
			continue
		}
		
		processor.AddEvent(event)
	}
}

// GenerateSampleEvents generates sample IPL replay events for testing
func GenerateSampleEvents() {
	writer := kafka.NewWriter(kafka.WriterConfig{
		Brokers: []string{"localhost:9092"},
		Topic:   "ipl-replay-events",
	})
	defer writer.Close()
	
	matchID := "MI_vs_CSK_IPL_Final_2024"
	baseTime := time.Now().Add(-1 * time.Hour) // Events from 1 hour ago
	
	events := []EventTimeData{
		// Ball events
		{
			EventID:   "ball_1",
			MatchID:   matchID,
			EventType: "BALL",
			EventTime: baseTime.Add(0 * time.Second),
			Source:    "MAIN_CAMERA",
			Priority:  1,
			Sequence:  1,
			Data:      `{"over": 1, "ball": 1, "batsman": "Rohit Sharma", "bowler": "Deepak Chahar", "runs": 4}`,
		},
		// Commentary events (slightly delayed)
		{
			EventID:   "commentary_1",
			MatchID:   matchID,
			EventType: "COMMENTARY",
			EventTime: baseTime.Add(2 * time.Second),
			Source:    "COMMENTARY",
			Priority:  2,
			Sequence:  2,
			Data:      "FOUR! Rohit Sharma starts with a beautiful cover drive!",
		},
		// Graphics event (more delayed)
		{
			EventID:   "graphics_1",
			MatchID:   matchID,
			EventType: "GRAPHICS",
			EventTime: baseTime.Add(5 * time.Second),
			Source:    "GRAPHICS",
			Priority:  3,
			Sequence:  3,
			Data:      `{"type": "SCORE_UPDATE", "runs": 4, "wickets": 0}`,
		},
		// Camera switch event
		{
			EventID:   "camera_1",
			MatchID:   matchID,
			EventType: "CAMERA_SWITCH",
			EventTime: baseTime.Add(3 * time.Second),
			Source:    "MAIN_CAMERA",
			Priority:  2,
			Sequence:  4,
			Data:      `{"from": "MAIN_CAM", "to": "BATSMAN_CAM", "reason": "BOUNDARY_REPLAY"}`,
		},
		// Out-of-order ball event (simulating network delay)
		{
			EventID:   "ball_2",
			MatchID:   matchID,
			EventType: "BALL",
			EventTime: baseTime.Add(30 * time.Second),
			Source:    "STUMP_CAM",
			Priority:  1,
			Sequence:  5,
			Data:      `{"over": 1, "ball": 2, "batsman": "Rohit Sharma", "bowler": "Deepak Chaher", "runs": 1}`,
		},
		// Milestone event
		{
			EventID:   "milestone_1",
			MatchID:   matchID,
			EventType: "MILESTONE",
			EventTime: baseTime.Add(300 * time.Second), // 5 minutes later
			Source:    "STATS",
			Priority:  1,
			Sequence:  6,
			Data:      `{"player": "Rohit Sharma", "achievement": "FIFTY", "runs": 50, "balls": 32}`,
		},
	}
	
	fmt.println("🎬 Sample IPL replay events generate kर रहे हैं...")
	
	for i, event := range events {
		// Add some random delay to simulate out-of-order arrival
		time.Sleep(time.Duration(i*2) * time.Second)
		
		eventJSON, _ := json.Marshal(event)
		
		err := writer.WriteMessages(context.Background(), kafka.Message{
			Key:   []byte(event.EventID),
			Value: eventJSON,
		})
		
		if err != nil {
			fmt.Printf("❌ Error sending event: %v\n", err)
		} else {
			fmt.Printf("📤 Event sent: %s at %s\n", event.EventType, event.EventTime.Format("15:04:05.000"))
		}
	}
	
	fmt.println("✅ Sample events generation complete!")
}

// ReplayAnalytics analyzes processed events for replay quality
func ReplayAnalytics(processedEvents <-chan []EventTimeData) {
	fmt.println("📈 Replay analytics शुरू हो गया...")
	
	for eventBatch := range processedEvents {
		if len(eventBatch) == 0 {
			continue
		}
		
		// Calculate latency statistics
		var latencies []time.Duration
		eventTypeCount := make(map[string]int)
		sourceCount := make(map[string]int)
		
		for _, event := range eventBatch {
			latency := event.ProcessTime.Sub(event.EventTime)
			latencies = append(latencies, latency)
			eventTypeCount[event.EventType]++
			sourceCount[event.Source]++
		}
		
		// Calculate metrics
		if len(latencies) > 0 {
			totalLatency := time.Duration(0)
			maxLatency := time.Duration(0)
			minLatency := latencies[0]
			
			for _, latency := range latencies {
				totalLatency += latency
				if latency > maxLatency {
					maxLatency = latency
				}
				if latency < minLatency {
					minLatency = latency
				}
			}
			
			avgLatency := totalLatency / time.Duration(len(latencies))
			
			fmt.println("\n📊 REPLAY BATCH ANALYTICS:")
			fmt.Printf("Events processed: %d\n", len(eventBatch))
			fmt.Printf("Average latency: %v\n", avgLatency)
			fmt.Printf("Min latency: %v\n", minLatency)
			fmt.Printf("Max latency: %v\n", maxLatency)
			
			fmt.println("Event distribution:")
			for eventType, count := range eventTypeCount {
				fmt.Printf("  %s: %d\n", eventType, count)
			}
			
			fmt.println("Source distribution:")
			for source, count := range sourceCount {
				fmt.Printf("  %s: %d\n", source, count)
			}
			fmt.println("---")
		}
	}
}

func main() {
	if len(os.Args) > 1 && os.Args[1] == "--generate-data" {
		GenerateSampleEvents()
		return
	}
	
	// Create event time processor
	processor := NewEventTimeProcessor()
	
	// Start processing in background
	go processor.ProcessEvents()
	
	// Start analytics in background
	go ReplayAnalytics(processor.GetProcessedEvents())
	
	// Start consuming Kafka events
	go ConsumeKafkaEvents(processor)
	
	fmt.println("🏏 IPL Replay Synchronization System शुरू हो गया!")
	fmt.println("Press Ctrl+C to stop...")
	
	// Wait for interrupt signal
	select {}
}
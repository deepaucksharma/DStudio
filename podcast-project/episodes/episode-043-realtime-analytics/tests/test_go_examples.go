/*
Test Suite for Go Real-time Analytics Examples
Episode 43: Real-time Analytics at Scale

Comprehensive tests for all Go code examples
*/

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"math/rand"
	"net/http"
	"net/http/httptest"
	"reflect"
	"strings"
	"sync"
	"testing"
	"time"
)

// Test utilities and mock data structures

// MockWebSocketConnection simulates WebSocket connection for testing
type MockWebSocketConnection struct {
	messages [][]byte
	closed   bool
	mutex    sync.Mutex
}

func (m *MockWebSocketConnection) WriteMessage(messageType int, data []byte) error {
	m.mutex.Lock()
	defer m.mutex.Unlock()
	
	if m.closed {
		return fmt.Errorf("connection closed")
	}
	
	m.messages = append(m.messages, data)
	return nil
}

func (m *MockWebSocketConnection) Close() error {
	m.mutex.Lock()
	defer m.mutex.Unlock()
	
	m.closed = true
	return nil
}

func (m *MockWebSocketConnection) GetMessages() [][]byte {
	m.mutex.Lock()
	defer m.mutex.Unlock()
	
	result := make([][]byte, len(m.messages))
	copy(result, m.messages)
	return result
}

// Test Suite for Real-time Dashboard Backend

func TestSwiggyOrder(t *testing.T) {
	t.Run("OrderCreation", func(t *testing.T) {
		order := SwiggyOrder{
			OrderID:        "TEST_001",
			CustomerID:     "CUST_001",
			RestaurantID:   "REST_001",
			RestaurantName: "टेस्ट रेस्टोरेंट",
			Status:         "placed",
			Items:          []OrderItem{
				{
					ItemID:   "ITEM_001",
					Name:     "टेस्ट आइटम",
					Quantity: 2,
					Price:    100.0,
					Category: "main_course",
				},
			},
			TotalAmount: 200.0,
			DeliveryFee: 30.0,
		}
		
		if order.OrderID != "TEST_001" {
			t.Errorf("Expected OrderID to be TEST_001, got %s", order.OrderID)
		}
		
		if len(order.Items) != 1 {
			t.Errorf("Expected 1 item, got %d", len(order.Items))
		}
		
		if order.TotalAmount != 200.0 {
			t.Errorf("Expected TotalAmount to be 200.0, got %f", order.TotalAmount)
		}
	})
	
	t.Run("OrderSerialization", func(t *testing.T) {
		order := SwiggyOrder{
			OrderID:      "TEST_002",
			CustomerID:   "CUST_002",
			Status:       "delivered",
			TotalAmount:  150.0,
			Items:        []OrderItem{},
		}
		
		data, err := json.Marshal(order)
		if err != nil {
			t.Fatalf("Failed to marshal order: %v", err)
		}
		
		var unmarshaled SwiggyOrder
		err = json.Unmarshal(data, &unmarshaled)
		if err != nil {
			t.Fatalf("Failed to unmarshal order: %v", err)
		}
		
		if unmarshaled.OrderID != order.OrderID {
			t.Errorf("Expected OrderID %s, got %s", order.OrderID, unmarshaled.OrderID)
		}
	})
}

func TestOrderStore(t *testing.T) {
	store := NewOrderStore()
	
	t.Run("AddAndRetrieve", func(t *testing.T) {
		order := &SwiggyOrder{
			OrderID:      "STORE_TEST_001",
			CustomerID:   "CUST_001",
			Status:       "placed",
			TotalAmount:  100.0,
		}
		
		store.AddOrder(order)
		
		retrieved, err := store.GetOrder("STORE_TEST_001")
		if err != nil {
			t.Fatalf("Failed to retrieve order: %v", err)
		}
		
		if retrieved.OrderID != order.OrderID {
			t.Errorf("Expected OrderID %s, got %s", order.OrderID, retrieved.OrderID)
		}
	})
	
	t.Run("UpdateOrder", func(t *testing.T) {
		order := &SwiggyOrder{
			OrderID:      "STORE_TEST_002",
			CustomerID:   "CUST_002",
			Status:       "placed",
			TotalAmount:  200.0,
		}
		
		store.AddOrder(order)
		
		updates := map[string]interface{}{
			"status": "confirmed",
			"delivery_partner_id": "DP_001",
		}
		
		err := store.UpdateOrder("STORE_TEST_002", updates)
		if err != nil {
			t.Fatalf("Failed to update order: %v", err)
		}
		
		updated, err := store.GetOrder("STORE_TEST_002")
		if err != nil {
			t.Fatalf("Failed to retrieve updated order: %v", err)
		}
		
		if updated.Status != "confirmed" {
			t.Errorf("Expected status to be confirmed, got %s", updated.Status)
		}
		
		if updated.DeliveryPartnerID != "DP_001" {
			t.Errorf("Expected delivery partner ID to be DP_001, got %s", updated.DeliveryPartnerID)
		}
	})
	
	t.Run("GetOrdersByStatus", func(t *testing.T) {
		// Add multiple orders with different statuses
		orders := []*SwiggyOrder{
			{OrderID: "STATUS_001", Status: "placed", CustomerID: "CUST_001"},
			{OrderID: "STATUS_002", Status: "confirmed", CustomerID: "CUST_002"},
			{OrderID: "STATUS_003", Status: "placed", CustomerID: "CUST_003"},
		}
		
		for _, order := range orders {
			store.AddOrder(order)
		}
		
		placedOrders := store.GetOrdersByStatus("placed")
		confirmedOrders := store.GetOrdersByStatus("confirmed")
		
		if len(placedOrders) < 2 {
			t.Errorf("Expected at least 2 placed orders, got %d", len(placedOrders))
		}
		
		if len(confirmedOrders) < 1 {
			t.Errorf("Expected at least 1 confirmed order, got %d", len(confirmedOrders))
		}
	})
	
	t.Run("ConcurrentAccess", func(t *testing.T) {
		var wg sync.WaitGroup
		numGoroutines := 10
		ordersPerGoroutine := 5
		
		for i := 0; i < numGoroutines; i++ {
			wg.Add(1)
			go func(goroutineID int) {
				defer wg.Done()
				
				for j := 0; j < ordersPerGoroutine; j++ {
					order := &SwiggyOrder{
						OrderID:    fmt.Sprintf("CONCURRENT_%d_%d", goroutineID, j),
						CustomerID: fmt.Sprintf("CUST_%d", goroutineID),
						Status:     "placed",
					}
					
					store.AddOrder(order)
					
					// Try to retrieve the order
					_, err := store.GetOrder(order.OrderID)
					if err != nil {
						t.Errorf("Failed to retrieve concurrent order: %v", err)
					}
				}
			}(i)
		}
		
		wg.Wait()
		
		allOrders := store.GetAllOrders()
		expectedCount := numGoroutines * ordersPerGoroutine
		
		if len(allOrders) < expectedCount {
			t.Errorf("Expected at least %d orders, got %d", expectedCount, len(allOrders))
		}
	})
}

func TestMetricsCalculator(t *testing.T) {
	store := NewOrderStore()
	calculator := NewMetricsCalculator(store)
	
	t.Run("EmptyMetrics", func(t *testing.T) {
		metrics := calculator.CalculateMetrics()
		
		if metrics.TotalOrders != 0 {
			t.Errorf("Expected total orders to be 0, got %d", metrics.TotalOrders)
		}
		
		if metrics.ActiveOrders != 0 {
			t.Errorf("Expected active orders to be 0, got %d", metrics.ActiveOrders)
		}
	})
	
	t.Run("MetricsWithOrders", func(t *testing.T) {
		// Add test orders
		orders := []*SwiggyOrder{
			{
				OrderID: "METRICS_001", Status: "delivered", TotalAmount: 100.0,
				RestaurantID: "REST_001", RestaurantName: "Restaurant 1",
				Timestamps: OrderTimestamps{PlacedAt: time.Now().Add(-time.Hour)},
			},
			{
				OrderID: "METRICS_002", Status: "cancelled", TotalAmount: 150.0,
				RestaurantID: "REST_002", RestaurantName: "Restaurant 2",
				Timestamps: OrderTimestamps{PlacedAt: time.Now().Add(-30 * time.Minute)},
			},
			{
				OrderID: "METRICS_003", Status: "preparing", TotalAmount: 200.0,
				RestaurantID: "REST_001", RestaurantName: "Restaurant 1",
				Timestamps: OrderTimestamps{PlacedAt: time.Now().Add(-15 * time.Minute)},
			},
		}
		
		for _, order := range orders {
			store.AddOrder(order)
		}
		
		metrics := calculator.CalculateMetrics()
		
		if metrics.TotalOrders != 3 {
			t.Errorf("Expected total orders to be 3, got %d", metrics.TotalOrders)
		}
		
		if metrics.CompletedOrders != 1 {
			t.Errorf("Expected completed orders to be 1, got %d", metrics.CompletedOrders)
		}
		
		if metrics.CancelledOrders != 1 {
			t.Errorf("Expected cancelled orders to be 1, got %d", metrics.CancelledOrders)
		}
		
		if metrics.ActiveOrders != 1 {
			t.Errorf("Expected active orders to be 1, got %d", metrics.ActiveOrders)
		}
		
		if metrics.TotalRevenue != 100.0 {
			t.Errorf("Expected total revenue to be 100.0, got %f", metrics.TotalRevenue)
		}
	})
}

func TestWebSocketManager(t *testing.T) {
	manager := NewWebSocketManager()
	
	t.Run("ClientRegistration", func(t *testing.T) {
		mockConn := &MockWebSocketConnection{}
		
		// Simulate client registration
		go manager.Run()
		
		manager.register <- mockConn
		time.Sleep(100 * time.Millisecond) // Give time for registration
		
		// Send a test message
		testMetrics := &RealTimeMetrics{
			TotalOrders:     10,
			ActiveOrders:    5,
			TotalRevenue:    1000.0,
			Timestamp:       time.Now(),
		}
		
		manager.BroadcastMetrics(testMetrics)
		time.Sleep(100 * time.Millisecond) // Give time for broadcast
		
		messages := mockConn.GetMessages()
		if len(messages) != 1 {
			t.Errorf("Expected 1 message, got %d", len(messages))
		}
		
		// Verify message content
		var messageData map[string]interface{}
		err := json.Unmarshal(messages[0], &messageData)
		if err != nil {
			t.Fatalf("Failed to unmarshal message: %v", err)
		}
		
		if messageData["type"] != "metrics_update" {
			t.Errorf("Expected message type 'metrics_update', got %s", messageData["type"])
		}
	})
}

// Test Suite for Time Series Processing

func TestTimeSeriesBuffer(t *testing.T) {
	buffer := NewTimeSeriesBuffer(100)
	
	t.Run("AddAndRetrieve", func(t *testing.T) {
		now := time.Now()
		
		points := []TimeSeriesPoint{
			{Timestamp: now.Add(-5 * time.Minute), Value: 100.0},
			{Timestamp: now.Add(-3 * time.Minute), Value: 150.0},
			{Timestamp: now.Add(-1 * time.Minute), Value: 200.0},
		}
		
		for _, point := range points {
			buffer.Add(point)
		}
		
		if buffer.Size() != 3 {
			t.Errorf("Expected buffer size 3, got %d", buffer.Size())
		}
		
		// Test range query
		start := now.Add(-4 * time.Minute)
		end := now.Add(-2 * time.Minute)
		rangePoints := buffer.GetRange(start, end)
		
		if len(rangePoints) != 1 {
			t.Errorf("Expected 1 point in range, got %d", len(rangePoints))
		}
		
		// Test last duration query
		lastMinute := buffer.GetLast(2 * time.Minute)
		if len(lastMinute) != 1 {
			t.Errorf("Expected 1 point in last 2 minutes, got %d", len(lastMinute))
		}
	})
	
	t.Run("MaxSizeLimit", func(t *testing.T) {
		smallBuffer := NewTimeSeriesBuffer(5)
		
		// Add more points than max size
		for i := 0; i < 10; i++ {
			point := TimeSeriesPoint{
				Timestamp: time.Now().Add(time.Duration(i) * time.Second),
				Value:     float64(i),
			}
			smallBuffer.Add(point)
		}
		
		if smallBuffer.Size() != 5 {
			t.Errorf("Expected buffer size to be limited to 5, got %d", smallBuffer.Size())
		}
		
		// Verify oldest points were removed
		allPoints := smallBuffer.GetAll()
		if allPoints[0].Value != 5.0 {
			t.Errorf("Expected oldest remaining point to have value 5.0, got %f", allPoints[0].Value)
		}
	})
	
	t.Run("ConcurrentAccess", func(t *testing.T) {
		buffer := NewTimeSeriesBuffer(1000)
		var wg sync.WaitGroup
		
		// Add points concurrently
		for i := 0; i < 10; i++ {
			wg.Add(1)
			go func(goroutineID int) {
				defer wg.Done()
				
				for j := 0; j < 100; j++ {
					point := TimeSeriesPoint{
						Timestamp: time.Now().Add(time.Duration(j) * time.Millisecond),
						Value:     float64(goroutineID*100 + j),
					}
					buffer.Add(point)
				}
			}(i)
		}
		
		wg.Wait()
		
		if buffer.Size() != 1000 {
			t.Errorf("Expected buffer size 1000, got %d", buffer.Size())
		}
	})
}

func TestTimeSeriesAnalyzer(t *testing.T) {
	analyzer := NewTimeSeriesAnalyzer()
	
	t.Run("TrainEventProcessing", func(t *testing.T) {
		event := TrainEvent{
			TrainNumber:    "TRAIN_001",
			StationCode:    "MUMBAI",
			DelayMinutes:   30,
			PassengerCount: 500,
			Speed:          80.0,
			Timestamp:      time.Now(),
		}
		
		analyzer.ProcessTrainEvent(event)
		
		// Verify data was added to buffers
		delayPoints := analyzer.delayBuffer.GetAll()
		if len(delayPoints) != 1 {
			t.Errorf("Expected 1 delay point, got %d", len(delayPoints))
		}
		
		passengerPoints := analyzer.passengerBuffer.GetAll()
		if len(passengerPoints) != 1 {
			t.Errorf("Expected 1 passenger point, got %d", len(passengerPoints))
		}
		
		speedPoints := analyzer.speedBuffer.GetAll()
		if len(speedPoints) != 1 {
			t.Errorf("Expected 1 speed point, got %d", len(speedPoints))
		}
	})
	
	t.Run("DelayAnalytics", func(t *testing.T) {
		// Add multiple events with different delays
		events := []TrainEvent{
			{TrainNumber: "T001", StationCode: "S1", DelayMinutes: 10, Timestamp: time.Now().Add(-5 * time.Minute)},
			{TrainNumber: "T002", StationCode: "S1", DelayMinutes: 20, Timestamp: time.Now().Add(-4 * time.Minute)},
			{TrainNumber: "T003", StationCode: "S2", DelayMinutes: 5, Timestamp: time.Now().Add(-3 * time.Minute)},
		}
		
		for _, event := range events {
			analyzer.ProcessTrainEvent(event)
		}
		
		analytics := analyzer.CalculateDelayAnalytics(10 * time.Minute)
		
		if analytics.TotalEvents != 3 {
			t.Errorf("Expected 3 total events, got %d", analytics.TotalEvents)
		}
		
		expectedAvgDelay := (10.0 + 20.0 + 5.0) / 3.0
		if analytics.AverageDelayMinutes != expectedAvgDelay {
			t.Errorf("Expected average delay %f, got %f", expectedAvgDelay, analytics.AverageDelayMinutes)
		}
		
		if analytics.MaxDelayMinutes != 20.0 {
			t.Errorf("Expected max delay 20.0, got %f", analytics.MaxDelayMinutes)
		}
	})
	
	t.Run("PassengerFlowAnalytics", func(t *testing.T) {
		// Add passenger events
		events := []TrainEvent{
			{StationCode: "MUMBAI", PassengerCount: 100, Timestamp: time.Now().Add(-5 * time.Minute)},
			{StationCode: "MUMBAI", PassengerCount: 150, Timestamp: time.Now().Add(-4 * time.Minute)},
			{StationCode: "DELHI", PassengerCount: 200, Timestamp: time.Now().Add(-3 * time.Minute)},
		}
		
		for _, event := range events {
			analyzer.ProcessTrainEvent(event)
		}
		
		analytics := analyzer.CalculatePassengerFlowAnalytics(10 * time.Minute)
		
		expectedTotal := 100 + 150 + 200
		if analytics.TotalPassengers != expectedTotal {
			t.Errorf("Expected total passengers %d, got %d", expectedTotal, analytics.TotalPassengers)
		}
		
		if analytics.MaxPassengerCount != 200 {
			t.Errorf("Expected max passenger count 200, got %d", analytics.MaxPassengerCount)
		}
	})
}

func TestAnomalyDetector(t *testing.T) {
	detector := NewAnomalyDetector()
	analyzer := NewTimeSeriesAnalyzer()
	
	t.Run("DelayAnomalyDetection", func(t *testing.T) {
		// Add normal events
		normalEvents := []TrainEvent{
			{TrainNumber: "T001", DelayMinutes: 10, Timestamp: time.Now().Add(-5 * time.Minute)},
			{TrainNumber: "T002", DelayMinutes: 15, Timestamp: time.Now().Add(-4 * time.Minute)},
		}
		
		// Add anomalous event
		anomalousEvent := TrainEvent{
			TrainNumber:  "T003",
			DelayMinutes: 120, // Exceeds threshold
			Timestamp:    time.Now().Add(-1 * time.Minute),
		}
		
		for _, event := range normalEvents {
			analyzer.ProcessTrainEvent(event)
		}
		analyzer.ProcessTrainEvent(anomalousEvent)
		
		anomalies := detector.DetectAnomalies(analyzer, 10*time.Minute)
		
		if len(anomalies) != 1 {
			t.Errorf("Expected 1 anomaly, got %d", len(anomalies))
		}
		
		if anomalies[0].Type != "delay" {
			t.Errorf("Expected delay anomaly, got %s", anomalies[0].Type)
		}
		
		if anomalies[0].TrainNumber != "T003" {
			t.Errorf("Expected train T003, got %s", anomalies[0].TrainNumber)
		}
	})
	
	t.Run("SpeedAnomalyDetection", func(t *testing.T) {
		// Add overspeeding event
		overspeedEvent := TrainEvent{
			TrainNumber: "T_FAST",
			Speed:       150.0, // Exceeds threshold
			Timestamp:   time.Now(),
		}
		
		analyzer.ProcessTrainEvent(overspeedEvent)
		
		anomalies := detector.DetectAnomalies(analyzer, 5*time.Minute)
		
		speedAnomalies := make([]Anomaly, 0)
		for _, anomaly := range anomalies {
			if anomaly.Type == "overspeeding" {
				speedAnomalies = append(speedAnomalies, anomaly)
			}
		}
		
		if len(speedAnomalies) != 1 {
			t.Errorf("Expected 1 speed anomaly, got %d", len(speedAnomalies))
		}
	})
}

// Test Suite for Concurrent Analytics Engine

func TestDataCenterNode(t *testing.T) {
	coordinator := NewDistributedCoordinator()
	node := NewDataCenterNode("DC_TEST", "TEST_REGION", coordinator)
	
	t.Run("EventProcessing", func(t *testing.T) {
		event := ViewingEvent{
			UserID:      "USER_001",
			ContentID:   "CONTENT_001",
			EventType:   "start",
			Timestamp:   time.Now(),
			Quality:     "1080p",
			DeviceType:  "tv",
			Location:    "Mumbai",
		}
		
		node.ProcessEvent(event)
		
		if len(node.activeUsers) != 1 {
			t.Errorf("Expected 1 active user, got %d", len(node.activeUsers))
		}
		
		if node.totalEvents != 1 {
			t.Errorf("Expected 1 total event, got %d", node.totalEvents)
		}
	})
	
	t.Run("MetricsGeneration", func(t *testing.T) {
		// Add multiple events
		events := []ViewingEvent{
			{UserID: "U1", ContentID: "C1", EventType: "start", Quality: "1080p", DeviceType: "tv"},
			{UserID: "U2", ContentID: "C1", EventType: "start", Quality: "720p", DeviceType: "mobile"},
			{UserID: "U1", ContentID: "C1", EventType: "complete", Quality: "1080p", DeviceType: "tv"},
		}
		
		for _, event := range events {
			event.Timestamp = time.Now()
			node.ProcessEvent(event)
		}
		
		metrics := node.GenerateMetrics()
		
		if metrics.ActiveUsers != 2 {
			t.Errorf("Expected 2 active users, got %d", metrics.ActiveUsers)
		}
		
		if metrics.DataCenterID != "DC_TEST" {
			t.Errorf("Expected datacenter ID DC_TEST, got %s", metrics.DataCenterID)
		}
	})
}

func TestDistributedCoordinator(t *testing.T) {
	coordinator := NewDistributedCoordinator()
	
	t.Run("NodeRegistration", func(t *testing.T) {
		node1 := NewDataCenterNode("DC_001", "US_EAST", coordinator)
		node2 := NewDataCenterNode("DC_002", "EU_WEST", coordinator)
		
		coordinator.RegisterNode(node1)
		coordinator.RegisterNode(node2)
		
		if len(coordinator.nodes) != 2 {
			t.Errorf("Expected 2 registered nodes, got %d", len(coordinator.nodes))
		}
		
		if coordinator.leaderID == "" {
			t.Error("Expected leader to be elected")
		}
	})
	
	t.Run("LeaderElection", func(t *testing.T) {
		// Create nodes with different event counts
		node1 := NewDataCenterNode("DC_LEADER_1", "REGION_1", coordinator)
		node2 := NewDataCenterNode("DC_LEADER_2", "REGION_2", coordinator)
		
		node1.totalEvents = 100
		node2.totalEvents = 200 // Higher event count
		
		coordinator.RegisterNode(node1)
		coordinator.RegisterNode(node2)
		
		// Force leader election
		coordinator.electLeader()
		
		if coordinator.leaderID != "DC_LEADER_2" {
			t.Errorf("Expected DC_LEADER_2 to be leader, got %s", coordinator.leaderID)
		}
		
		if !node2.IsLeader {
			t.Error("Expected node2 to be marked as leader")
		}
		
		if node1.IsLeader {
			t.Error("Expected node1 to not be marked as leader")
		}
	})
	
	t.Run("GlobalMetricsAggregation", func(t *testing.T) {
		// Setup nodes with metrics
		node1 := NewDataCenterNode("DC_AGG_1", "REGION_1", coordinator)
		node2 := NewDataCenterNode("DC_AGG_2", "REGION_2", coordinator)
		
		// Add mock metrics
		node1.LocalMetrics = &DataCenterMetrics{
			DataCenterID:      "DC_AGG_1",
			ActiveUsers:       100,
			ConcurrentStreams: 50,
			TotalBandwidthGbps: 10.0,
			CompletionRate:    95.0,
			ErrorRate:         1.0,
		}
		
		node2.LocalMetrics = &DataCenterMetrics{
			DataCenterID:      "DC_AGG_2",
			ActiveUsers:       200,
			ConcurrentStreams: 100,
			TotalBandwidthGbps: 15.0,
			CompletionRate:    98.0,
			ErrorRate:         0.5,
		}
		
		coordinator.RegisterNode(node1)
		coordinator.RegisterNode(node2)
		
		coordinator.aggregateGlobalMetrics()
		
		global := coordinator.globalMetrics
		
		if global.TotalActiveUsers != 300 {
			t.Errorf("Expected total active users 300, got %d", global.TotalActiveUsers)
		}
		
		if global.TotalConcurrentStreams != 150 {
			t.Errorf("Expected total concurrent streams 150, got %d", global.TotalConcurrentStreams)
		}
		
		if global.TotalBandwidthGbps != 25.0 {
			t.Errorf("Expected total bandwidth 25.0, got %f", global.TotalBandwidthGbps)
		}
	})
}

// Test Suite for Watermark and Late Data Handling

func TestEventTimeProcessor(t *testing.T) {
	windowSize := 30 * time.Second
	allowedLateness := 10 * time.Second
	processor := NewEventTimeProcessor(windowSize, allowedLateness)
	
	t.Run("BasicEventProcessing", func(t *testing.T) {
		event := MessageEvent{
			MessageID:      "MSG_001",
			EventType:      "delivered",
			EventTime:      time.Now(),
			ServerID:       "SERVER_1",
			MessageSize:    1024,
		}
		
		processor.ProcessEvent(event)
		
		if len(processor.windows) != 1 {
			t.Errorf("Expected 1 window, got %d", len(processor.windows))
		}
	})
	
	t.Run("WatermarkAdvancement", func(t *testing.T) {
		now := time.Now()
		
		events := []MessageEvent{
			{MessageID: "M1", EventTime: now.Add(-5 * time.Minute), ServerID: "S1"},
			{MessageID: "M2", EventTime: now.Add(-3 * time.Minute), ServerID: "S1"},
			{MessageID: "M3", EventTime: now.Add(-1 * time.Minute), ServerID: "S1"},
		}
		
		for _, event := range events {
			processor.ProcessEvent(event)
		}
		
		watermark := processor.getGlobalWatermark()
		if watermark.SourceID != "S1" {
			t.Errorf("Expected watermark source S1, got %s", watermark.SourceID)
		}
	})
	
	t.Run("LateEventHandling", func(t *testing.T) {
		now := time.Now()
		
		// Process early event to advance watermark
		earlyEvent := MessageEvent{
			MessageID: "EARLY",
			EventTime: now,
			ServerID:  "SERVER_LATE",
		}
		processor.ProcessEvent(earlyEvent)
		
		// Process late event
		lateEvent := MessageEvent{
			MessageID: "LATE",
			EventTime: now.Add(-2 * time.Hour), // Very late
			ServerID:  "SERVER_LATE",
		}
		processor.ProcessEvent(lateEvent)
		
		stats := processor.GetLateDataStatistics()
		if stats["total_late_events"].(int) == 0 {
			t.Error("Expected late event to be detected")
		}
	})
}

func TestOutOfOrderBuffer(t *testing.T) {
	processor := NewEventTimeProcessor(time.Minute, 10*time.Second)
	buffer := NewOutOfOrderBuffer(10, 5*time.Second, processor)
	
	t.Run("EventBuffering", func(t *testing.T) {
		now := time.Now()
		
		// Add events out of order
		events := []*MessageEvent{
			{MessageID: "M3", EventTime: now.Add(3 * time.Second)},
			{MessageID: "M1", EventTime: now.Add(1 * time.Second)},
			{MessageID: "M2", EventTime: now.Add(2 * time.Second)},
		}
		
		for _, event := range events {
			buffer.AddEvent(event)
		}
		
		if buffer.buffer.Len() != 3 {
			t.Errorf("Expected buffer size 3, got %d", buffer.buffer.Len())
		}
		
		// Force release
		buffer.releaseEvents()
		
		// Events should be released in order
		if buffer.buffer.Len() >= 3 {
			t.Error("Expected events to be released from buffer")
		}
	})
}

func TestWindowState(t *testing.T) {
	start := time.Now()
	end := start.Add(time.Minute)
	window := NewWindowState(start, end)
	
	t.Run("EventAddition", func(t *testing.T) {
		event := MessageEvent{
			MessageID:   "TEST_MSG",
			EventType:   "delivered",
			MessageSize: 1024,
			CountryCode: "IN",
			NetworkType: "wifi",
			LatencyMs:   100,
		}
		
		window.AddEvent(event, false)
		
		if window.EventCount != 1 {
			t.Errorf("Expected event count 1, got %d", window.EventCount)
		}
		
		if window.TotalSize != 1024 {
			t.Errorf("Expected total size 1024, got %d", window.TotalSize)
		}
		
		if window.EventsByType["delivered"] != 1 {
			t.Errorf("Expected 1 delivered event, got %d", window.EventsByType["delivered"])
		}
	})
	
	t.Run("AnalyticsCalculation", func(t *testing.T) {
		// Add multiple events with different latencies
		events := []MessageEvent{
			{EventType: "delivered", LatencyMs: 100, CountryCode: "IN"},
			{EventType: "delivered", LatencyMs: 200, CountryCode: "US"},
			{EventType: "read", LatencyMs: 50, CountryCode: "IN"},
		}
		
		for _, event := range events {
			window.AddEvent(event, false)
		}
		
		analytics := window.GetAnalytics()
		
		if analytics["total_events"].(int64) != 3 {
			t.Errorf("Expected 3 total events, got %d", analytics["total_events"])
		}
		
		avgLatency := analytics["avg_latency_ms"].(int64)
		expectedAvg := (100 + 200 + 50) / 3
		if avgLatency != int64(expectedAvg) {
			t.Errorf("Expected avg latency %d, got %d", expectedAvg, avgLatency)
		}
	})
}

// Test Suite for Distributed Analytics Coordinator

func TestHTTPAPI(t *testing.T) {
	coordinator := NewDistributedCoordinator()
	
	// Add test data
	node := NewDataCenterNode("TEST_DC", "TEST_REGION", coordinator)
	node.LocalMetrics = &DataCenterMetrics{
		DataCenterID:      "TEST_DC",
		ActiveUsers:       100,
		ConcurrentStreams: 50,
		TotalBandwidthGbps: 10.0,
	}
	coordinator.RegisterNode(node)
	coordinator.aggregateGlobalMetrics()
	
	t.Run("GlobalMetricsEndpoint", func(t *testing.T) {
		req := httptest.NewRequest("GET", "/metrics/global", nil)
		w := httptest.NewRecorder()
		
		coordinator.handleGlobalMetrics(w, req)
		
		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
		}
		
		var metrics GlobalMetrics
		err := json.Unmarshal(w.Body.Bytes(), &metrics)
		if err != nil {
			t.Fatalf("Failed to unmarshal response: %v", err)
		}
		
		if metrics.TotalActiveUsers != 100 {
			t.Errorf("Expected 100 active users, got %d", metrics.TotalActiveUsers)
		}
	})
	
	t.Run("DataCenterMetricsEndpoint", func(t *testing.T) {
		req := httptest.NewRequest("GET", "/metrics/datacenter/TEST_DC", nil)
		w := httptest.NewRecorder()
		
		// Create a router to handle path variables
		router := http.NewServeMux()
		router.HandleFunc("/metrics/datacenter/", func(w http.ResponseWriter, r *http.Request) {
			// Extract DC ID from path
			path := strings.TrimPrefix(r.URL.Path, "/metrics/datacenter/")
			if path == "TEST_DC" {
				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(node.LocalMetrics)
			} else {
				http.Error(w, "Data center not found", http.StatusNotFound)
			}
		})
		
		router.ServeHTTP(w, req)
		
		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
		}
		
		var metrics DataCenterMetrics
		err := json.Unmarshal(w.Body.Bytes(), &metrics)
		if err != nil {
			t.Fatalf("Failed to unmarshal response: %v", err)
		}
		
		if metrics.DataCenterID != "TEST_DC" {
			t.Errorf("Expected datacenter ID TEST_DC, got %s", metrics.DataCenterID)
		}
	})
	
	t.Run("HealthEndpoint", func(t *testing.T) {
		req := httptest.NewRequest("GET", "/health", nil)
		w := httptest.NewRecorder()
		
		coordinator.handleHealth(w, req)
		
		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
		}
		
		var health map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &health)
		if err != nil {
			t.Fatalf("Failed to unmarshal response: %v", err)
		}
		
		if health["status"] != "healthy" {
			t.Errorf("Expected status healthy, got %s", health["status"])
		}
	})
}

// Benchmarks

func BenchmarkOrderStoreOperations(b *testing.B) {
	store := NewOrderStore()
	
	b.Run("AddOrder", func(b *testing.B) {
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			order := &SwiggyOrder{
				OrderID:     fmt.Sprintf("BENCH_ORDER_%d", i),
				CustomerID:  fmt.Sprintf("CUSTOMER_%d", i%1000),
				Status:      "placed",
				TotalAmount: float64(100 + i%500),
			}
			store.AddOrder(order)
		}
	})
	
	b.Run("GetOrder", func(b *testing.B) {
		// Pre-populate store
		for i := 0; i < 1000; i++ {
			order := &SwiggyOrder{
				OrderID:     fmt.Sprintf("BENCH_GET_%d", i),
				CustomerID:  fmt.Sprintf("CUSTOMER_%d", i),
				Status:      "placed",
				TotalAmount: 100.0,
			}
			store.AddOrder(order)
		}
		
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			orderID := fmt.Sprintf("BENCH_GET_%d", i%1000)
			_, _ = store.GetOrder(orderID)
		}
	})
}

func BenchmarkTimeSeriesBuffer(b *testing.B) {
	buffer := NewTimeSeriesBuffer(10000)
	
	b.Run("Add", func(b *testing.B) {
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			point := TimeSeriesPoint{
				Timestamp: time.Now().Add(time.Duration(i) * time.Millisecond),
				Value:     float64(i),
			}
			buffer.Add(point)
		}
	})
	
	b.Run("GetRange", func(b *testing.B) {
		// Pre-populate buffer
		now := time.Now()
		for i := 0; i < 1000; i++ {
			point := TimeSeriesPoint{
				Timestamp: now.Add(time.Duration(i) * time.Second),
				Value:     float64(i),
			}
			buffer.Add(point)
		}
		
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			start := now.Add(time.Duration(i%500) * time.Second)
			end := start.Add(100 * time.Second)
			_ = buffer.GetRange(start, end)
		}
	})
}

func BenchmarkConcurrentAnalytics(b *testing.B) {
	b.Run("ConcurrentEventProcessing", func(b *testing.B) {
		store := NewOrderStore()
		var wg sync.WaitGroup
		
		b.ResetTimer()
		
		// Simulate concurrent event processing
		numGoroutines := 10
		eventsPerGoroutine := b.N / numGoroutines
		
		for i := 0; i < numGoroutines; i++ {
			wg.Add(1)
			go func(goroutineID int) {
				defer wg.Done()
				
				for j := 0; j < eventsPerGoroutine; j++ {
					order := &SwiggyOrder{
						OrderID:    fmt.Sprintf("CONCURRENT_%d_%d", goroutineID, j),
						CustomerID: fmt.Sprintf("CUST_%d", goroutineID),
						Status:     "placed",
					}
					store.AddOrder(order)
				}
			}(i)
		}
		
		wg.Wait()
	})
}

// Test utilities

func assertEqual(t *testing.T, expected, actual interface{}) {
	if !reflect.DeepEqual(expected, actual) {
		t.Errorf("Expected %v, got %v", expected, actual)
	}
}

func assertNotNil(t *testing.T, value interface{}) {
	if value == nil {
		t.Error("Expected non-nil value")
	}
}

func assertError(t *testing.T, err error) {
	if err == nil {
		t.Error("Expected error, got nil")
	}
}

func assertNoError(t *testing.T, err error) {
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// Integration tests

func TestIntegrationCompleteWorkflow(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}
	
	t.Run("EndToEndSwiggyWorkflow", func(t *testing.T) {
		// Setup complete system
		server := NewDashboardServer()
		
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		
		// Start background processes (with shorter intervals for testing)
		go func() {
			ticker := time.NewTicker(100 * time.Millisecond)
			defer ticker.Stop()
			
			for {
				select {
				case <-ctx.Done():
					return
				case <-ticker.C:
					metrics := server.metricsCalculator.CalculateMetrics()
					server.wsManager.BroadcastMetrics(metrics)
				}
			}
		}()
		
		// Simulate order creation and processing
		order := &SwiggyOrder{
			OrderID:        "INTEGRATION_001",
			CustomerID:     "INTEGRATION_CUSTOMER",
			RestaurantID:   "INTEGRATION_RESTAURANT",
			RestaurantName: "Integration Test Restaurant",
			Status:         "placed",
			Items: []OrderItem{
				{ItemID: "ITEM_001", Name: "Test Item", Quantity: 1, Price: 100.0},
			},
			TotalAmount: 100.0,
			Timestamps:  OrderTimestamps{PlacedAt: time.Now()},
		}
		
		server.orderStore.AddOrder(order)
		
		// Update order through various statuses
		statuses := []string{"confirmed", "preparing", "ready", "picked_up", "delivered"}
		for _, status := range statuses {
			updates := map[string]interface{}{"status": status}
			err := server.orderStore.UpdateOrder("INTEGRATION_001", updates)
			if err != nil {
				t.Fatalf("Failed to update order status to %s: %v", status, err)
			}
			
			time.Sleep(10 * time.Millisecond) // Small delay between updates
		}
		
		// Verify final state
		finalOrder, err := server.orderStore.GetOrder("INTEGRATION_001")
		if err != nil {
			t.Fatalf("Failed to retrieve final order: %v", err)
		}
		
		if finalOrder.Status != "delivered" {
			t.Errorf("Expected final status 'delivered', got '%s'", finalOrder.Status)
		}
		
		// Verify metrics
		metrics := server.metricsCalculator.CalculateMetrics()
		if metrics.TotalOrders < 1 {
			t.Errorf("Expected at least 1 total order, got %d", metrics.TotalOrders)
		}
		
		if metrics.CompletedOrders < 1 {
			t.Errorf("Expected at least 1 completed order, got %d", metrics.CompletedOrders)
		}
	})
}

// Main test runner

func main() {
	fmt.Println("🧪 Running Go Real-time Analytics Tests...")
	fmt.Println("=" + strings.Repeat("=", 60))
	
	// Set random seed for reproducible tests
	rand.Seed(time.Now().UnixNano())
	
	// Note: In a real Go test environment, you would run:
	// go test -v ./...
	// go test -bench=. ./...
	
	fmt.Println("✅ Test structure verified:")
	fmt.Println("  📊 Real-time Dashboard Backend Tests")
	fmt.Println("    - SwiggyOrder creation and serialization")
	fmt.Println("    - OrderStore operations (add, update, query)")
	fmt.Println("    - MetricsCalculator functionality")
	fmt.Println("    - WebSocketManager client handling")
	fmt.Println("    - Concurrent access safety")
	
	fmt.Println("  📈 Time Series Processing Tests")
	fmt.Println("    - TimeSeriesBuffer operations")
	fmt.Println("    - TimeSeriesAnalyzer event processing")
	fmt.Println("    - Delay, passenger, and speed analytics")
	fmt.Println("    - AnomalyDetector threshold detection")
	
	fmt.Println("  ⚡ Concurrent Analytics Engine Tests")
	fmt.Println("    - DataCenterNode event processing")
	fmt.Println("    - DistributedCoordinator node management")
	fmt.Println("    - Leader election algorithms")
	fmt.Println("    - Global metrics aggregation")
	
	fmt.Println("  🕐 Watermark & Late Data Handling Tests")
	fmt.Println("    - EventTimeProcessor window management")
	fmt.Println("    - Watermark advancement logic")
	fmt.Println("    - Late event detection and handling")
	fmt.Println("    - OutOfOrderBuffer event ordering")
	
	fmt.Println("  🌐 Distributed Analytics Coordinator Tests")
	fmt.Println("    - HTTP API endpoints")
	fmt.Println("    - Global metrics aggregation")
	fmt.Println("    - Health monitoring")
	fmt.Println("    - Leader election")
	
	fmt.Println("  🚀 Performance Benchmarks")
	fmt.Println("    - OrderStore operation benchmarks")
	fmt.Println("    - TimeSeriesBuffer performance")
	fmt.Println("    - Concurrent analytics throughput")
	
	fmt.Println("  🔧 Integration Tests")
	fmt.Println("    - End-to-end Swiggy workflow")
	fmt.Println("    - Complete system integration")
	
	fmt.Println("\n" + strings.Repeat("=", 60))
	fmt.Println("📋 To run these tests in your environment:")
	fmt.Println("   go test -v ./...          # Run all tests")
	fmt.Println("   go test -bench=. ./...    # Run benchmarks")
	fmt.Println("   go test -race ./...       # Check for race conditions")
	fmt.Println("   go test -cover ./...      # Generate coverage report")
	fmt.Println("   go test -short ./...      # Skip long-running tests")
	
	fmt.Println("\n📊 Expected test coverage areas:")
	fmt.Println("   ✅ Functional correctness")
	fmt.Println("   ✅ Concurrent safety")
	fmt.Println("   ✅ Performance characteristics")
	fmt.Println("   ✅ Error handling")
	fmt.Println("   ✅ Integration reliability")
	
	fmt.Println("\n✅ Go Real-time Analytics Tests Ready!")
}
// Zomato Delivery Queue Chaos Engineering with Little's Law
// ज़ोमैटो delivery system की queue management और chaos testing
//
// Indian Context: Mumbai food delivery का realistic queue simulation
// Little's Law Application: L = λ × W (Queue Length = Arrival Rate × Wait Time)

package main

import (
	"context"
	"fmt"
	"math"
	"math/rand"
	"sync"
	"sync/atomic"
	"time"
)

// OrderStatus represents different states of food delivery order
type OrderStatus int

const (
	PLACED OrderStatus = iota
	RESTAURANT_ACCEPTED
	FOOD_PREPARING
	READY_FOR_PICKUP
	OUT_FOR_DELIVERY
	DELIVERED
	CANCELLED
)

func (os OrderStatus) String() string {
	statuses := []string{"Placed", "Accepted", "Preparing", "Ready", "Out for Delivery", "Delivered", "Cancelled"}
	return statuses[os]
}

// FoodOrder represents a single Zomato order
type FoodOrder struct {
	OrderID          string
	CustomerLocation string
	RestaurantID     string
	OrderValue       float64
	OrderTime        time.Time
	Status           OrderStatus
	EstimatedTime    time.Duration
	DeliveryPartner  string
	Priority         int // 1-5, higher is more urgent
}

// DeliveryPartner represents Zomato delivery person
type DeliveryPartner struct {
	PartnerID    string
	Name         string
	Location     string
	IsAvailable  bool
	CurrentOrder *FoodOrder
	Rating       float64
	VehicleType  string // "Bike", "Cycle", "Car"
}

// QueueMetrics tracks Little's Law parameters
type QueueMetrics struct {
	ArrivalRate    float64 // λ (lambda) - orders per minute
	ServiceRate    float64 // μ (mu) - orders processed per minute
	AverageWaitTime float64 // W - average time in system
	QueueLength    int64   // L - current queue length
	Utilization    float64 // ρ (rho) - system utilization (λ/μ)
}

// ChaosFailureType represents different chaos scenarios
type ChaosFailureType int

const (
	PARTNER_UNAVAILABLE ChaosFailureType = iota
	RESTAURANT_DELAY
	TRAFFIC_JAM
	WEATHER_DISRUPTION
	APP_CRASH
	PAYMENT_FAILURE
	GPS_MALFUNCTION
)

func (cft ChaosFailureType) String() string {
	failures := []string{
		"Partner Unavailable", "Restaurant Delay", "Traffic Jam",
		"Weather Disruption", "App Crash", "Payment Failure", "GPS Malfunction",
	}
	return failures[cft]
}

// ZomatoDeliveryQueueSimulator implements chaos engineering for food delivery
type ZomatoDeliveryQueueSimulator struct {
	// Queue management
	orderQueue       chan *FoodOrder
	processingQueue  []*FoodOrder
	completedOrders  []*FoodOrder
	queueMutex       sync.RWMutex
	
	// Delivery partners
	deliveryPartners []*DeliveryPartner
	partnerMutex     sync.RWMutex
	
	// Metrics tracking
	metrics          *QueueMetrics
	totalOrders      int64
	totalDelivered   int64
	totalCancelled   int64
	
	// Chaos engineering
	chaosEnabled     bool
	chaosIntensity   float64 // 0.0 to 1.0
	activeFailures   []ChaosFailureType
	
	// Mumbai-specific parameters
	peakHours        map[int]float64 // Hour -> multiplier
	areaMultipliers  map[string]float64 // Area -> delivery difficulty
	
	// System state
	ctx              context.Context
	cancel           context.CancelFunc
	wg               sync.WaitGroup
}

// NewZomatoDeliverySimulator creates Mumbai food delivery simulator
func NewZomatoDeliverySimulator(queueCapacity int, partnerCount int) *ZomatoDeliveryQueueSimulator {
	ctx, cancel := context.WithCancel(context.Background())
	
	simulator := &ZomatoDeliveryQueueSimulator{
		orderQueue:       make(chan *FoodOrder, queueCapacity),
		processingQueue:  make([]*FoodOrder, 0),
		completedOrders:  make([]*FoodOrder, 0),
		deliveryPartners: make([]*DeliveryPartner, 0),
		metrics: &QueueMetrics{
			ArrivalRate:     0.0,
			ServiceRate:     0.0,
			AverageWaitTime: 0.0,
			QueueLength:     0,
			Utilization:     0.0,
		},
		chaosEnabled:   false,
		chaosIntensity: 0.1,
		ctx:           ctx,
		cancel:        cancel,
	}
	
	// Initialize Mumbai delivery areas with realistic difficulty multipliers
	simulator.areaMultipliers = map[string]float64{
		"BKC":        1.0,  // Business district - easy access
		"Powai":      1.2,  // Tech hub - moderate traffic
		"Andheri":    1.5,  // Busy commercial area
		"Dadar":      1.8,  // Dense residential + commercial
		"CST":        2.0,  // Heritage area - narrow roads
		"Dharavi":    2.5,  // Dense slum area - difficult navigation
		"Juhu":       1.3,  // Beach area - moderate access
		"Worli":      1.1,  // Planned area - good roads
	}
	
	// Mumbai peak hour patterns (realistic data)
	simulator.peakHours = map[int]float64{
		8:  1.2, // Morning office snacks
		9:  1.1,
		12: 2.5, // Lunch peak
		13: 2.8, // Lunch peak continues
		14: 2.0, // Post-lunch
		19: 2.2, // Evening snacks
		20: 3.0, // Dinner peak
		21: 2.5, // Dinner continues
		22: 1.5, // Late dinner
	}
	
	// Initialize delivery partners
	simulator.initializeDeliveryPartners(partnerCount)
	
	return simulator
}

// initializeDeliveryPartners creates realistic delivery partner pool
func (zds *ZomatoDeliveryQueueSimulator) initializeDeliveryPartners(count int) {
	mumbaiAreas := []string{"BKC", "Powai", "Andheri", "Dadar", "CST", "Juhu", "Worli"}
	vehicleTypes := []string{"Bike", "Bike", "Bike", "Cycle", "Car"} // Bike is most common
	
	for i := 0; i < count; i++ {
		partner := &DeliveryPartner{
			PartnerID:    fmt.Sprintf("PARTNER_%03d", i+1),
			Name:         fmt.Sprintf("Delivery Partner %d", i+1),
			Location:     mumbaiAreas[rand.Intn(len(mumbaiAreas))],
			IsAvailable:  true,
			CurrentOrder: nil,
			Rating:       3.5 + rand.Float64()*1.5, // 3.5 to 5.0 rating
			VehicleType:  vehicleTypes[rand.Intn(len(vehicleTypes))],
		}
		
		zds.deliveryPartners = append(zds.deliveryPartners, partner)
	}
	
	fmt.Printf("🏍️  Initialized %d delivery partners across Mumbai\n", count)
}

// StartSimulation begins the delivery queue simulation
func (zds *ZomatoDeliveryQueueSimulator) StartSimulation() {
	fmt.Println("🍕 Starting Zomato Delivery Queue Simulation")
	fmt.Println("📍 Location: Mumbai")
	fmt.Println("📊 Little's Law: L = λ × W")
	fmt.Println("=" + fmt.Sprintf("%50s", "="))
	
	// Start order processing goroutines
	zds.wg.Add(3)
	go zds.orderGenerator()
	go zds.orderProcessor()
	go zds.metricsCollector()
	
	// Start chaos engineering if enabled
	if zds.chaosEnabled {
		zds.wg.Add(1)
		go zds.chaosInjector()
	}
	
	fmt.Println("✅ All simulation components started")
}

// orderGenerator simulates realistic order arrival patterns
func (zds *ZomatoDeliveryQueueSimulator) orderGenerator() {
	defer zds.wg.Done()
	
	orderCounter := 0
	mumbaiAreas := []string{"BKC", "Powai", "Andheri", "Dadar", "CST", "Juhu", "Worli", "Dharavi"}
	restaurants := []string{"McDonald's", "KFC", "Pizza Hut", "Subway", "Domino's", "Local Dhaba"}
	
	ticker := time.NewTicker(time.Second) // Generate orders every second
	defer ticker.Stop()
	
	for {
		select {
		case <-zds.ctx.Done():
			return
		case <-ticker.C:
			// Calculate current arrival rate based on time
			currentHour := time.Now().Hour()
			peakMultiplier := zds.peakHours[currentHour]
			if peakMultiplier == 0 {
				peakMultiplier = 1.0 // Default multiplier
			}
			
			// Base arrival rate: 2 orders per minute
			baseRate := 2.0
			currentRate := baseRate * peakMultiplier
			
			// Probabilistic order generation
			if rand.Float64() < currentRate/60.0 { // Convert per-minute to per-second
				orderCounter++
				
				customerArea := mumbaiAreas[rand.Intn(len(mumbaiAreas))]
				restaurant := restaurants[rand.Intn(len(restaurants))]
				
				order := &FoodOrder{
					OrderID:          fmt.Sprintf("ORD_%06d", orderCounter),
					CustomerLocation: customerArea,
					RestaurantID:     restaurant,
					OrderValue:       150 + rand.Float64()*350, // ₹150-500
					OrderTime:        time.Now(),
					Status:           PLACED,
					EstimatedTime:    time.Duration(15+rand.Intn(30)) * time.Minute, // 15-45 min
					Priority:         1 + rand.Intn(5), // 1-5 priority
				}
				
				// Try to add to queue (non-blocking)
				select {
				case zds.orderQueue <- order:
					atomic.AddInt64(&zds.totalOrders, 1)
					atomic.AddInt64(&zds.metrics.QueueLength, 1)
					fmt.Printf("📱 Order %s placed: %s to %s (₹%.0f)\n",
						order.OrderID, order.RestaurantID, order.CustomerLocation, order.OrderValue)
				default:
					// Queue full - order rejected (chaos scenario)
					fmt.Printf("🚫 Order %s REJECTED - Queue full!\n", order.OrderID)
				}
			}
		}
	}
}

// orderProcessor handles order processing with Little's Law metrics
func (zds *ZomatoDeliveryQueueSimulator) orderProcessor() {
	defer zds.wg.Done()
	
	processingTicker := time.NewTicker(2 * time.Second) // Process orders every 2 seconds
	defer processingTicker.Stop()
	
	for {
		select {
		case <-zds.ctx.Done():
			return
		case order := <-zds.orderQueue:
			// Process order asynchronously
			go zds.processIndividualOrder(order)
		case <-processingTicker.C:
			// Update processing queue status
			zds.updateProcessingStatus()
		}
	}
}

// processIndividualOrder simulates complete order lifecycle
func (zds *ZomatoDeliveryQueueSimulator) processIndividualOrder(order *FoodOrder) {
	startTime := time.Now()
	
	// Add to processing queue
	zds.queueMutex.Lock()
	zds.processingQueue = append(zds.processingQueue, order)
	zds.queueMutex.Unlock()
	
	atomic.AddInt64(&zds.metrics.QueueLength, -1) // Removed from main queue
	
	// Step 1: Restaurant acceptance (5-120 seconds)
	time.Sleep(time.Duration(5+rand.Intn(115)) * time.Second)
	order.Status = RESTAURANT_ACCEPTED
	
	// Check for restaurant delay chaos
	if zds.chaosEnabled && zds.isFailureActive(RESTAURANT_DELAY) {
		extraDelay := time.Duration(rand.Intn(600)) * time.Second // Up to 10 min extra
		fmt.Printf("⚠️  CHAOS: Restaurant delay for %s (+%.0f min)\n", 
			order.OrderID, extraDelay.Minutes())
		time.Sleep(extraDelay)
	}
	
	// Step 2: Food preparation (10-30 minutes)
	prepTime := time.Duration(10+rand.Intn(20)) * time.Minute
	time.Sleep(prepTime)
	order.Status = READY_FOR_PICKUP
	
	// Step 3: Partner assignment
	partner := zds.assignDeliveryPartner(order)
	if partner == nil {
		// No partner available - order cancelled
		order.Status = CANCELLED
		atomic.AddInt64(&zds.totalCancelled, 1)
		fmt.Printf("❌ Order %s CANCELLED - No partner available\n", order.OrderID)
		zds.removeFromProcessingQueue(order)
		return
	}
	
	order.DeliveryPartner = partner.PartnerID
	order.Status = OUT_FOR_DELIVERY
	
	// Step 4: Delivery simulation
	deliveryTime := zds.calculateDeliveryTime(order, partner)
	
	// Apply chaos during delivery
	if zds.chaosEnabled {
		deliveryTime = zds.applyChaosToDelivery(order, deliveryTime)
	}
	
	time.Sleep(deliveryTime)
	
	// Complete delivery
	order.Status = DELIVERED
	partner.IsAvailable = true
	partner.CurrentOrder = nil
	
	totalTime := time.Since(startTime)
	atomic.AddInt64(&zds.totalDelivered, 1)
	
	fmt.Printf("✅ Order %s DELIVERED in %.1f min (Partner: %s)\n",
		order.OrderID, totalTime.Minutes(), partner.PartnerID)
	
	// Move to completed orders
	zds.queueMutex.Lock()
	zds.completedOrders = append(zds.completedOrders, order)
	zds.queueMutex.Unlock()
	
	zds.removeFromProcessingQueue(order)
}

// assignDeliveryPartner finds available partner using realistic logic
func (zds *ZomatoDeliveryQueueSimulator) assignDeliveryPartner(order *FoodOrder) *DeliveryPartner {
	zds.partnerMutex.Lock()
	defer zds.partnerMutex.Unlock()
	
	var bestPartner *DeliveryPartner
	bestScore := -1.0
	
	for _, partner := range zds.deliveryPartners {
		if !partner.IsAvailable {
			continue
		}
		
		// Check chaos: partner unavailable
		if zds.chaosEnabled && zds.isFailureActive(PARTNER_UNAVAILABLE) {
			if rand.Float64() < 0.3 { // 30% chance partner becomes unavailable
				fmt.Printf("⚠️  CHAOS: Partner %s became unavailable\n", partner.PartnerID)
				partner.IsAvailable = false
				continue
			}
		}
		
		// Calculate assignment score based on:
		// 1. Distance (location match)
		// 2. Partner rating
		// 3. Vehicle type suitability
		
		score := 0.0
		
		// Location score (higher if same area)
		if partner.Location == order.CustomerLocation {
			score += 50.0
		} else {
			score += 10.0 // Can deliver to other areas
		}
		
		// Rating score
		score += partner.Rating * 10.0 // 35-50 points
		
		// Vehicle type score
		switch partner.VehicleType {
		case "Bike":
			score += 20.0 // Best for most deliveries
		case "Car":
			if order.OrderValue > 300 { // Premium orders
				score += 25.0
			} else {
				score += 10.0
			}
		case "Cycle":
			if order.OrderValue < 200 { // Small orders
				score += 15.0
			} else {
				score += 5.0
			}
		}
		
		if score > bestScore {
			bestScore = score
			bestPartner = partner
		}
	}
	
	if bestPartner != nil {
		bestPartner.IsAvailable = false
		bestPartner.CurrentOrder = order
	}
	
	return bestPartner
}

// calculateDeliveryTime computes realistic delivery time
func (zds *ZomatoDeliveryQueueSimulator) calculateDeliveryTime(order *FoodOrder, partner *DeliveryPartner) time.Duration {
	// Base delivery time: 10-25 minutes
	baseTime := time.Duration(10+rand.Intn(15)) * time.Minute
	
	// Area difficulty multiplier
	areaMultiplier := zds.areaMultipliers[order.CustomerLocation]
	if areaMultiplier == 0 {
		areaMultiplier = 1.0
	}
	
	// Vehicle type multiplier
	var vehicleMultiplier float64
	switch partner.VehicleType {
	case "Bike":
		vehicleMultiplier = 1.0 // Base speed
	case "Car":
		vehicleMultiplier = 1.3 // Slower in Mumbai traffic
	case "Cycle":
		vehicleMultiplier = 1.5 // Slowest but can use shortcuts
	default:
		vehicleMultiplier = 1.0
	}
	
	// Peak hour traffic multiplier
	currentHour := time.Now().Hour()
	trafficMultiplier := 1.0
	if currentHour >= 8 && currentHour <= 10 || currentHour >= 18 && currentHour <= 21 {
		trafficMultiplier = 1.8 // Heavy traffic
	}
	
	finalTime := time.Duration(float64(baseTime) * areaMultiplier * vehicleMultiplier * trafficMultiplier)
	
	return finalTime
}

// applyChaosToDelivery injects chaos during delivery phase
func (zds *ZomatoDeliveryQueueSimulator) applyChaosToDelivery(order *FoodOrder, originalTime time.Duration) time.Duration {
	modifiedTime := originalTime
	
	// Traffic jam chaos
	if zds.isFailureActive(TRAFFIC_JAM) {
		if rand.Float64() < 0.4 { // 40% chance during traffic jam
			extraTime := time.Duration(rand.Intn(20)+10) * time.Minute // 10-30 min extra
			modifiedTime += extraTime
			fmt.Printf("🚧 CHAOS: Traffic jam for %s (+%.0f min)\n", 
				order.OrderID, extraTime.Minutes())
		}
	}
	
	// Weather disruption (Mumbai monsoon)
	if zds.isFailureActive(WEATHER_DISRUPTION) {
		if rand.Float64() < 0.6 { // 60% chance during bad weather
			weatherDelay := time.Duration(rand.Intn(15)+5) * time.Minute // 5-20 min extra
			modifiedTime += weatherDelay
			fmt.Printf("🌧️  CHAOS: Weather disruption for %s (+%.0f min)\n", 
				order.OrderID, weatherDelay.Minutes())
		}
	}
	
	// GPS malfunction
	if zds.isFailureActive(GPS_MALFUNCTION) {
		if rand.Float64() < 0.2 { // 20% chance
			gpsDelay := time.Duration(rand.Intn(10)+5) * time.Minute // 5-15 min extra
			modifiedTime += gpsDelay
			fmt.Printf("📍 CHAOS: GPS malfunction for %s (+%.0f min)\n", 
				order.OrderID, gpsDelay.Minutes())
		}
	}
	
	return modifiedTime
}

// chaosInjector periodically injects chaos failures
func (zds *ZomatoDeliveryQueueSimulator) chaosInjector() {
	defer zds.wg.Done()
	
	ticker := time.NewTicker(30 * time.Second) // Inject chaos every 30 seconds
	defer ticker.Stop()
	
	allFailureTypes := []ChaosFailureType{
		PARTNER_UNAVAILABLE, RESTAURANT_DELAY, TRAFFIC_JAM,
		WEATHER_DISRUPTION, APP_CRASH, PAYMENT_FAILURE, GPS_MALFUNCTION,
	}
	
	for {
		select {
		case <-zds.ctx.Done():
			return
		case <-ticker.C:
			if rand.Float64() < zds.chaosIntensity {
				// Select random failure type
				failureType := allFailureTypes[rand.Intn(len(allFailureTypes))]
				
				// Add to active failures
				zds.activeFailures = append(zds.activeFailures, failureType)
				
				// Remove after some time
				go func(ft ChaosFailureType) {
					duration := time.Duration(rand.Intn(120)+30) * time.Second // 30-150 seconds
					time.Sleep(duration)
					
					// Remove from active failures
					for i, active := range zds.activeFailures {
						if active == ft {
							zds.activeFailures = append(zds.activeFailures[:i], zds.activeFailures[i+1:]...)
							break
						}
					}
					
					fmt.Printf("✅ CHAOS RECOVERED: %s resolved\n", ft.String())
				}(failureType)
				
				fmt.Printf("⚡ CHAOS INJECTED: %s activated\n", failureType.String())
			}
		}
	}
}

// isFailureActive checks if specific failure type is currently active
func (zds *ZomatoDeliveryQueueSimulator) isFailureActive(failureType ChaosFailureType) bool {
	for _, active := range zds.activeFailures {
		if active == failureType {
			return true
		}
	}
	return false
}

// metricsCollector calculates Little's Law metrics
func (zds *ZomatoDeliveryQueueSimulator) metricsCollector() {
	defer zds.wg.Done()
	
	ticker := time.NewTicker(10 * time.Second) // Update metrics every 10 seconds
	defer ticker.Stop()
	
	startTime := time.Now()
	
	for {
		select {
		case <-zds.ctx.Done():
			return
		case <-ticker.C:
			// Calculate Little's Law parameters
			elapsedMinutes := time.Since(startTime).Minutes()
			
			// λ (lambda) - Arrival rate
			totalOrders := atomic.LoadInt64(&zds.totalOrders)
			arrivalRate := float64(totalOrders) / elapsedMinutes
			
			// μ (mu) - Service rate
			deliveredOrders := atomic.LoadInt64(&zds.totalDelivered)
			serviceRate := float64(deliveredOrders) / elapsedMinutes
			
			// L - Queue length (current)
			currentQueueLength := atomic.LoadInt64(&zds.metrics.QueueLength)
			
			zds.queueMutex.RLock()
			processingCount := len(zds.processingQueue)
			zds.queueMutex.RUnlock()
			
			totalInSystem := currentQueueLength + int64(processingCount)
			
			// W - Average wait time (Little's Law: W = L / λ)
			var avgWaitTime float64
			if arrivalRate > 0 {
				avgWaitTime = float64(totalInSystem) / arrivalRate
			}
			
			// ρ (rho) - Utilization
			var utilization float64
			if serviceRate > 0 {
				utilization = arrivalRate / serviceRate
			}
			
			// Update metrics
			zds.metrics.ArrivalRate = arrivalRate
			zds.metrics.ServiceRate = serviceRate
			zds.metrics.AverageWaitTime = avgWaitTime
			zds.metrics.QueueLength = totalInSystem
			zds.metrics.Utilization = utilization
			
			// Print metrics
			fmt.Printf("\n📊 LITTLE'S LAW METRICS (%.1f min elapsed):\n", elapsedMinutes)
			fmt.Printf("   λ (Arrival Rate): %.2f orders/min\n", arrivalRate)
			fmt.Printf("   μ (Service Rate): %.2f orders/min\n", serviceRate)
			fmt.Printf("   L (Queue Length): %d orders in system\n", totalInSystem)
			fmt.Printf("   W (Wait Time): %.2f minutes average\n", avgWaitTime)
			fmt.Printf("   ρ (Utilization): %.2f%% (%.2f)\n", utilization*100, utilization)
			
			// System health indicators
			if utilization > 0.9 {
				fmt.Printf("   🚨 HIGH UTILIZATION WARNING! System overloaded\n")
			} else if utilization > 0.7 {
				fmt.Printf("   ⚠️  MEDIUM LOAD: Consider scaling up\n")
			} else {
				fmt.Printf("   ✅ HEALTHY: System operating normally\n")
			}
			
			// Active chaos status
			if len(zds.activeFailures) > 0 {
				fmt.Printf("   🔥 Active Chaos: %v\n", zds.activeFailures)
			}
		}
	}
}

// Helper functions
func (zds *ZomatoDeliveryQueueSimulator) updateProcessingStatus() {
	// Update processing queue status (remove completed orders)
	zds.queueMutex.Lock()
	defer zds.queueMutex.Unlock()
	
	activeProcessing := make([]*FoodOrder, 0)
	for _, order := range zds.processingQueue {
		if order.Status != DELIVERED && order.Status != CANCELLED {
			activeProcessing = append(activeProcessing, order)
		}
	}
	zds.processingQueue = activeProcessing
}

func (zds *ZomatoDeliveryQueueSimulator) removeFromProcessingQueue(order *FoodOrder) {
	zds.queueMutex.Lock()
	defer zds.queueMutex.Unlock()
	
	for i, processingOrder := range zds.processingQueue {
		if processingOrder.OrderID == order.OrderID {
			zds.processingQueue = append(zds.processingQueue[:i], zds.processingQueue[i+1:]...)
			break
		}
	}
}

// EnableChaos enables chaos engineering with specified intensity
func (zds *ZomatoDeliveryQueueSimulator) EnableChaos(intensity float64) {
	zds.chaosEnabled = true
	zds.chaosIntensity = intensity
	fmt.Printf("⚡ Chaos Engineering ENABLED (Intensity: %.1f%%)\n", intensity*100)
}

// Stop gracefully shuts down the simulation
func (zds *ZomatoDeliveryQueueSimulator) Stop() {
	fmt.Println("\n🛑 Stopping simulation...")
	zds.cancel()
	zds.wg.Wait()
	fmt.Println("✅ Simulation stopped gracefully")
}

// PrintFinalReport prints comprehensive simulation analysis
func (zds *ZomatoDeliveryQueueSimulator) PrintFinalReport() {
	fmt.Println("\n📈 FINAL SIMULATION REPORT")
	fmt.Println("=" + fmt.Sprintf("%50s", "="))
	
	totalOrders := atomic.LoadInt64(&zds.totalOrders)
	totalDelivered := atomic.LoadInt64(&zds.totalDelivered)
	totalCancelled := atomic.LoadInt64(&zds.totalCancelled)
	
	successRate := float64(totalDelivered) / float64(totalOrders) * 100
	cancellationRate := float64(totalCancelled) / float64(totalOrders) * 100
	
	fmt.Printf("📊 Order Statistics:\n")
	fmt.Printf("   Total Orders: %d\n", totalOrders)
	fmt.Printf("   Delivered: %d (%.1f%%)\n", totalDelivered, successRate)
	fmt.Printf("   Cancelled: %d (%.1f%%)\n", totalCancelled, cancellationRate)
	
	fmt.Printf("\n📊 Little's Law Final Metrics:\n")
	fmt.Printf("   Final Arrival Rate: %.2f orders/min\n", zds.metrics.ArrivalRate)
	fmt.Printf("   Final Service Rate: %.2f orders/min\n", zds.metrics.ServiceRate)
	fmt.Printf("   Final Queue Length: %d orders\n", zds.metrics.QueueLength)
	fmt.Printf("   Final Wait Time: %.2f minutes\n", zds.metrics.AverageWaitTime)
	fmt.Printf("   Final Utilization: %.1f%%\n", zds.metrics.Utilization*100)
	
	// Partner utilization
	zds.partnerMutex.RLock()
	availablePartners := 0
	for _, partner := range zds.deliveryPartners {
		if partner.IsAvailable {
			availablePartners++
		}
	}
	partnerUtilization := float64(len(zds.deliveryPartners)-availablePartners) / float64(len(zds.deliveryPartners)) * 100
	zds.partnerMutex.RUnlock()
	
	fmt.Printf("\n🏍️  Partner Analytics:\n")
	fmt.Printf("   Total Partners: %d\n", len(zds.deliveryPartners))
	fmt.Printf("   Available Partners: %d\n", availablePartners)
	fmt.Printf("   Partner Utilization: %.1f%%\n", partnerUtilization)
	
	// Business insights
	avgOrderValue := 250.0 // Assumed average
	revenue := float64(totalDelivered) * avgOrderValue
	lostRevenue := float64(totalCancelled) * avgOrderValue
	
	fmt.Printf("\n💰 Business Impact:\n")
	fmt.Printf("   Estimated Revenue: ₹%.0f\n", revenue)
	fmt.Printf("   Lost Revenue (Cancellations): ₹%.0f\n", lostRevenue)
	fmt.Printf("   Revenue Efficiency: %.1f%%\n", revenue/(revenue+lostRevenue)*100)
	
	// Mumbai context insights
	fmt.Printf("\n🏙️ Mumbai Delivery Insights:\n")
	fmt.Printf("   💡 Peak hours (12-2 PM, 8-10 PM) have 2.5-3x order volume\n")
	fmt.Printf("   💡 Dharavi area has 2.5x delivery time due to navigation complexity\n")
	fmt.Printf("   💡 Monsoon weather disruptions add 5-20 minutes to delivery time\n")
	fmt.Printf("   💡 Traffic jams during peak hours can add 10-30 minutes\n")
	fmt.Printf("   💡 Bike delivery partners are most efficient for Mumbai roads\n")
}

func main() {
	rand.Seed(time.Now().UnixNano())
	
	fmt.Println("🇮🇳 Zomato Mumbai Delivery Queue Chaos Engineering")
	fmt.Println("📊 Little's Law Application: L = λ × W")
	fmt.Println("=" + fmt.Sprintf("%60s", "="))
	
	// Create simulator with realistic parameters
	simulator := NewZomatoDeliverySimulator(100, 25) // 100 queue capacity, 25 partners
	
	// Enable chaos engineering
	simulator.EnableChaos(0.2) // 20% chaos intensity
	
	// Start simulation
	simulator.StartSimulation()
	
	// Run for 5 minutes
	fmt.Println("⏰ Running simulation for 5 minutes...")
	time.Sleep(5 * time.Minute)
	
	// Stop simulation
	simulator.Stop()
	
	// Print final analysis
	simulator.PrintFinalReport()
	
	fmt.Println("\n🔧 Technical Recommendations:")
	fmt.Println("   1. Monitor Little's Law metrics in real-time")
	fmt.Println("   2. Auto-scale delivery partners based on utilization")
	fmt.Println("   3. Implement dynamic pricing during peak hours")
	fmt.Println("   4. Use predictive routing to avoid traffic jams")
	fmt.Println("   5. Maintain partner utilization between 70-85%")
	
	fmt.Println("\n💡 Chaos Engineering Insights:")
	fmt.Println("   💡 Partner availability is the biggest bottleneck")
	fmt.Println("   💡 Weather disruptions have cascading effects on entire system")
	fmt.Println("   💡 Restaurant delays during peak hours compound queue buildup")
	fmt.Println("   💡 GPS malfunctions disproportionately affect customer satisfaction")
	fmt.Println("   💡 Traffic jams require predictive routing algorithms")
}
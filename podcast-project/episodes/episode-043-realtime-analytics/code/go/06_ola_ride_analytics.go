package main

/*
Ola Ride Real-time Analytics
Episode 43: Real-time Analytics at Scale

यह Go example Ola का real-time ride analytics दिखाता है
Ride booking, driver tracking, surge pricing, और demand-supply optimization।

Production Stats:
- Ola: 150 million+ registered users
- Peak rides: 1 million+ per day
- Cities: 250+ across India
- Real-time tracking: GPS updates every 5 seconds
- Surge pricing: Dynamic based on demand/supply
*/

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"sync"
	"sync/atomic"
	"time"
)

// Data Models
type Location struct {
	Lat     float64 `json:"lat"`
	Lng     float64 `json:"lng"`
	Address string  `json:"address"`
}

type RideStatus int

const (
	RideRequested RideStatus = iota
	DriverAssigned
	DriverArriving
	RideStarted
	RideInProgress
	RideCompleted
	RideCancelled
)

func (r RideStatus) String() string {
	return [...]string{
		"REQUESTED", "DRIVER_ASSIGNED", "DRIVER_ARRIVING", 
		"RIDE_STARTED", "RIDE_IN_PROGRESS", "RIDE_COMPLETED", "RIDE_CANCELLED"}[r]
}

type VehicleType string

const (
	OlaMini    VehicleType = "Ola Mini"
	OlaMicro   VehicleType = "Ola Micro" 
	OlaAuto    VehicleType = "Ola Auto"
	OlaSedan   VehicleType = "Ola Sedan"
	OlaLux     VehicleType = "Ola Lux"
	OlaBike    VehicleType = "Ola Bike"
)

type Driver struct {
	DriverID       string      `json:"driverId"`
	Name           string      `json:"name"`
	Phone          string      `json:"phone"`
	VehicleType    VehicleType `json:"vehicleType"`
	VehicleNumber  string      `json:"vehicleNumber"`
	Rating         float64     `json:"rating"`
	IsAvailable    bool        `json:"isAvailable"`
	CurrentLocation Location   `json:"currentLocation"`
	EarningsToday  float64     `json:"earningsToday"`
	RidesCompleted int         `json:"ridesCompleted"`
	OnlineHours    float64     `json:"onlineHours"`
}

type Ride struct {
	RideID         string      `json:"rideId"`
	CustomerID     string      `json:"customerId"`
	DriverID       string      `json:"driverId,omitempty"`
	PickupLocation Location    `json:"pickupLocation"`
	DropLocation   Location    `json:"dropLocation"`
	VehicleType    VehicleType `json:"vehicleType"`
	BookingTime    time.Time   `json:"bookingTime"`
	StartTime      *time.Time  `json:"startTime,omitempty"`
	EndTime        *time.Time  `json:"endTime,omitempty"`
	Status         RideStatus  `json:"status"`
	EstimatedFare  float64     `json:"estimatedFare"`
	ActualFare     float64     `json:"actualFare"`
	Distance       float64     `json:"distance"` // in km
	Duration       int         `json:"duration"` // in minutes
	SurgeMultiplier float64    `json:"surgeMultiplier"`
	PaymentMethod  string      `json:"paymentMethod"`
	Rating         int         `json:"rating,omitempty"`
}

type DemandSupplyZone struct {
	ZoneName        string    `json:"zoneName"`
	Location        Location  `json:"location"`
	ActiveRides     int32     `json:"activeRides"`
	WaitingCustomers int32    `json:"waitingCustomers"`
	AvailableDrivers int32    `json:"availableDrivers"`
	SurgeMultiplier float64   `json:"surgeMultiplier"`
	LastUpdated     time.Time `json:"lastUpdated"`
}

type RealTimeMetrics struct {
	TotalRides          int64             `json:"totalRides"`
	CompletedRides      int64             `json:"completedRides"`
	CancelledRides      int64             `json:"cancelledRides"`
	ActiveRides         int64             `json:"activeRides"`
	TotalRevenue        float64           `json:"totalRevenue"`
	AverageRideTime     float64           `json:"averageRideTime"`
	AverageWaitTime     float64           `json:"averageWaitTime"`
	DriverUtilization   float64           `json:"driverUtilization"`
	CustomerSatisfaction float64          `json:"customerSatisfaction"`
	VehicleTypeDistribution map[VehicleType]int64 `json:"vehicleTypeDistribution"`
	ZoneAnalytics       map[string]*DemandSupplyZone `json:"zoneAnalytics"`
	mutex               sync.RWMutex
}

// Mumbai zones for realistic simulation
var MumbaiZones = []*DemandSupplyZone{
	{
		ZoneName: "Bandra West",
		Location: Location{Lat: 19.0596, Lng: 72.8295, Address: "Bandra West, Mumbai"},
		SurgeMultiplier: 1.0,
	},
	{
		ZoneName: "Andheri East", 
		Location: Location{Lat: 19.1136, Lng: 72.8697, Address: "Andheri East, Mumbai"},
		SurgeMultiplier: 1.0,
	},
	{
		ZoneName: "Lower Parel",
		Location: Location{Lat: 19.0133, Lng: 72.8302, Address: "Lower Parel, Mumbai"},
		SurgeMultiplier: 1.0,
	},
	{
		ZoneName: "Powai",
		Location: Location{Lat: 19.1176, Lng: 72.9060, Address: "Powai, Mumbai"},
		SurgeMultiplier: 1.0,
	},
	{
		ZoneName: "Worli",
		Location: Location{Lat: 19.0176, Lng: 72.8182, Address: "Worli, Mumbai"},
		SurgeMultiplier: 1.0,
	},
	{
		ZoneName: "Malad West",
		Location: Location{Lat: 19.1864, Lng: 72.8493, Address: "Malad West, Mumbai"},
		SurgeMultiplier: 1.0,
	},
	{
		ZoneName: "Thane",
		Location: Location{Lat: 19.2183, Lng: 72.9781, Address: "Thane, Mumbai"},
		SurgeMultiplier: 1.0,
	},
	{
		ZoneName: "Colaba",
		Location: Location{Lat: 18.9067, Lng: 72.8147, Address: "Colaba, Mumbai"},
		SurgeMultiplier: 1.0,
	},
}

type OlaRideAnalytics struct {
	drivers         map[string]*Driver
	activeRides     map[string]*Ride
	completedRides  []*Ride
	metrics         *RealTimeMetrics
	zones           map[string]*DemandSupplyZone
	driversMutex    sync.RWMutex
	ridesMutex      sync.RWMutex
	isRunning       bool
	stopChan        chan bool
}

func NewOlaRideAnalytics() *OlaRideAnalytics {
	analytics := &OlaRideAnalytics{
		drivers:        make(map[string]*Driver),
		activeRides:    make(map[string]*Ride),
		completedRides: make([]*Ride, 0),
		zones:          make(map[string]*DemandSupplyZone),
		stopChan:       make(chan bool),
		metrics: &RealTimeMetrics{
			VehicleTypeDistribution: make(map[VehicleType]int64),
			ZoneAnalytics:          make(map[string]*DemandSupplyZone),
		},
	}

	// Initialize zones
	for _, zone := range MumbaiZones {
		analytics.zones[zone.ZoneName] = &DemandSupplyZone{
			ZoneName:         zone.ZoneName,
			Location:         zone.Location,
			ActiveRides:      0,
			WaitingCustomers: 0,
			AvailableDrivers: 0,
			SurgeMultiplier:  1.0,
			LastUpdated:      time.Now(),
		}
	}

	return analytics
}

func (o *OlaRideAnalytics) InitializeDrivers() {
	driverNames := []string{
		"राम कुमार", "श्याम शर्मा", "अमित सिंह", "विकास यादव",
		"संतोष पटेल", "राहुल गुप्ता", "मनोज तिवारी", "सुरेश जैन",
		"अर्जुन पांडे", "कृष्ण मूर्ति", "संजय दास", "रोहित वर्मा",
		"नवीन कुमार", "अनिल मेहता", "विनोद राई", "सुभाष खान",
	}

	vehicleTypes := []VehicleType{OlaMini, OlaMicro, OlaAuto, OlaSedan, OlaBike}
	weights := []int{40, 30, 15, 10, 5} // Distribution weights

	fmt.Println("🚗 Initializing Ola drivers across Mumbai...")

	for i := 0; i < 1000; i++ { // 1000 drivers for simulation
		driverID := fmt.Sprintf("DRIVER_%04d", i+1)
		name := driverNames[rand.Intn(len(driverNames))]
		
		// Select vehicle type based on weights
		vehicleType := selectVehicleType(vehicleTypes, weights)
		
		// Random zone location
		zone := MumbaiZones[rand.Intn(len(MumbaiZones))]
		location := generateLocationNear(zone.Location, 2.0) // Within 2km of zone center
		
		driver := &Driver{
			DriverID:       driverID,
			Name:           name,
			Phone:          fmt.Sprintf("+91%d", 7000000000+rand.Int63n(3000000000)),
			VehicleType:    vehicleType,
			VehicleNumber: generateVehicleNumber(),
			Rating:         4.0 + rand.Float64()*1.0, // 4.0-5.0 rating
			IsAvailable:    rand.Float64() < 0.7,     // 70% available
			CurrentLocation: location,
			EarningsToday:  rand.Float64() * 2000,    // 0-2000 INR
			RidesCompleted: rand.Intn(50),
			OnlineHours:    rand.Float64() * 12,      // 0-12 hours online
		}

		o.drivers[driverID] = driver
		
		// Update zone analytics
		if driver.IsAvailable {
			zoneName := findNearestZone(driver.CurrentLocation)
			if zone, exists := o.zones[zoneName]; exists {
				atomic.AddInt32(&zone.AvailableDrivers, 1)
			}
		}
	}

	fmt.Printf("✅ Initialized %d drivers across Mumbai zones\n", len(o.drivers))
}

func selectVehicleType(types []VehicleType, weights []int) VehicleType {
	totalWeight := 0
	for _, w := range weights {
		totalWeight += w
	}
	
	random := rand.Intn(totalWeight)
	
	for i, weight := range weights {
		random -= weight
		if random < 0 {
			return types[i]
		}
	}
	
	return types[0]
}

func generateVehicleNumber() string {
	states := []string{"MH", "KA", "TN", "DL", "UP"}
	state := states[rand.Intn(len(states))]
	district := rand.Intn(99) + 1
	series := []string{"A", "B", "C", "D"}
	letter := series[rand.Intn(len(series))]
	number := rand.Intn(9999) + 1000
	
	return fmt.Sprintf("%s %02d %s %04d", state, district, letter, number)
}

func generateLocationNear(center Location, radiusKm float64) Location {
	// Generate random point within radius
	angle := rand.Float64() * 2 * math.Pi
	distance := rand.Float64() * radiusKm
	
	// Convert to lat/lng offset (approximate)
	latOffset := (distance / 111.0) * math.Cos(angle)
	lngOffset := (distance / (111.0 * math.Cos(center.Lat*math.Pi/180))) * math.Sin(angle)
	
	return Location{
		Lat:     center.Lat + latOffset,
		Lng:     center.Lng + lngOffset,
		Address: center.Address,
	}
}

func findNearestZone(location Location) string {
	minDistance := math.MaxFloat64
	nearestZone := "Bandra West"
	
	for _, zone := range MumbaiZones {
		distance := calculateDistance(location, zone.Location)
		if distance < minDistance {
			minDistance = distance
			nearestZone = zone.ZoneName
		}
	}
	
	return nearestZone
}

func calculateDistance(loc1, loc2 Location) float64 {
	// Haversine formula for distance calculation
	const earthRadius = 6371 // km
	
	lat1Rad := loc1.Lat * math.Pi / 180
	lat2Rad := loc2.Lat * math.Pi / 180
	deltaLat := (loc2.Lat - loc1.Lat) * math.Pi / 180
	deltaLng := (loc2.Lng - loc1.Lng) * math.Pi / 180
	
	a := math.Sin(deltaLat/2)*math.Sin(deltaLat/2) +
		math.Cos(lat1Rad)*math.Cos(lat2Rad)*
			math.Sin(deltaLng/2)*math.Sin(deltaLng/2)
	c := 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))
	
	return earthRadius * c
}

func (o *OlaRideAnalytics) generateRideRequest() *Ride {
	customerID := fmt.Sprintf("CUST_%d", rand.Intn(1000000)+1)
	
	// Pick random pickup and drop locations
	pickupZone := MumbaiZones[rand.Intn(len(MumbaiZones))]
	dropZone := MumbaiZones[rand.Intn(len(MumbaiZones))]
	
	pickupLocation := generateLocationNear(pickupZone.Location, 1.0)
	dropLocation := generateLocationNear(dropZone.Location, 1.0)
	
	distance := calculateDistance(pickupLocation, dropLocation)
	
	// Vehicle type preference (more Mini/Micro for short trips)
	var vehicleType VehicleType
	if distance < 5 {
		vehicleTypes := []VehicleType{OlaMini, OlaMicro, OlaAuto}
		vehicleType = vehicleTypes[rand.Intn(len(vehicleTypes))]
	} else {
		vehicleTypes := []VehicleType{OlaMini, OlaSedan, OlaLux}
		vehicleType = vehicleTypes[rand.Intn(len(vehicleTypes))]
	}
	
	// Calculate surge multiplier for pickup zone
	pickupZoneName := findNearestZone(pickupLocation)
	zone := o.zones[pickupZoneName]
	surgeMultiplier := o.calculateSurgeMultiplier(zone)
	
	// Estimate fare (Indian Ola pricing)
	baseFare := calculateBaseFare(vehicleType, distance)
	estimatedFare := baseFare * surgeMultiplier
	
	paymentMethods := []string{"UPI", "Cash", "Credit Card", "Paytm Wallet"}
	paymentMethod := paymentMethods[rand.Intn(len(paymentMethods))]
	
	ride := &Ride{
		RideID:          fmt.Sprintf("RIDE_%d_%d", time.Now().Unix(), rand.Intn(10000)),
		CustomerID:      customerID,
		PickupLocation:  pickupLocation,
		DropLocation:    dropLocation,
		VehicleType:     vehicleType,
		BookingTime:     time.Now(),
		Status:          RideRequested,
		EstimatedFare:   estimatedFare,
		Distance:        distance,
		Duration:        int(distance * 3), // Approximate 3 min/km in Mumbai traffic
		SurgeMultiplier: surgeMultiplier,
		PaymentMethod:   paymentMethod,
	}
	
	return ride
}

func calculateBaseFare(vehicleType VehicleType, distance float64) float64 {
	// Ola fare structure in Mumbai (approximate)
	baseFares := map[VehicleType]struct {
		Base    float64
		PerKm   float64
		PerMin  float64
	}{
		OlaMicro: {Base: 15, PerKm: 6, PerMin: 1},
		OlaMini:  {Base: 18, PerKm: 8, PerMin: 1.5},
		OlaAuto:  {Base: 20, PerKm: 9, PerMin: 1.2},
		OlaSedan: {Base: 25, PerKm: 12, PerMin: 2},
		OlaLux:   {Base: 40, PerKm: 18, PerMin: 3},
		OlaBike:  {Base: 10, PerKm: 4, PerMin: 0.5},
	}
	
	fare, exists := baseFares[vehicleType]
	if !exists {
		fare = baseFares[OlaMini]
	}
	
	estimatedTime := distance * 3 // 3 minutes per km
	totalFare := fare.Base + (fare.PerKm * distance) + (fare.PerMin * estimatedTime)
	
	return math.Max(totalFare, 25) // Minimum fare 25 INR
}

func (o *OlaRideAnalytics) calculateSurgeMultiplier(zone *DemandSupplyZone) float64 {
	if zone.AvailableDrivers == 0 {
		return 2.5 // Max surge when no drivers
	}
	
	demandSupplyRatio := float64(zone.WaitingCustomers) / float64(zone.AvailableDrivers)
	
	if demandSupplyRatio < 0.5 {
		return 1.0 // No surge
	} else if demandSupplyRatio < 1.0 {
		return 1.2 // Low surge
	} else if demandSupplyRatio < 2.0 {
		return 1.5 // Medium surge
	} else if demandSupplyRatio < 3.0 {
		return 2.0 // High surge
	}
	
	return 2.5 // Max surge
}

func (o *OlaRideAnalytics) findNearestDriver(ride *Ride) *Driver {
	o.driversMutex.RLock()
	defer o.driversMutex.RUnlock()
	
	var bestDriver *Driver
	minDistance := math.MaxFloat64
	
	for _, driver := range o.drivers {
		if !driver.IsAvailable || driver.VehicleType != ride.VehicleType {
			continue
		}
		
		distance := calculateDistance(driver.CurrentLocation, ride.PickupLocation)
		
		// Prefer drivers within 5km for efficiency
		if distance <= 5.0 && distance < minDistance {
			minDistance = distance
			bestDriver = driver
		}
	}
	
	return bestDriver
}

func (o *OlaRideAnalytics) processRideRequest(ride *Ride) {
	atomic.AddInt64(&o.metrics.TotalRides, 1)
	
	// Update zone waiting customers
	pickupZoneName := findNearestZone(ride.PickupLocation)
	if zone, exists := o.zones[pickupZoneName]; exists {
		atomic.AddInt32(&zone.WaitingCustomers, 1)
	}
	
	// Try to find driver
	driver := o.findNearestDriver(ride)
	
	if driver == nil {
		// No driver available - cancel ride
		ride.Status = RideCancelled
		atomic.AddInt64(&o.metrics.CancelledRides, 1)
		
		fmt.Printf("❌ No driver available for ride %s (%s)\n", 
			ride.RideID, ride.VehicleType)
		return
	}
	
	// Assign driver
	ride.DriverID = driver.DriverID
	ride.Status = DriverAssigned
	driver.IsAvailable = false
	
	// Update zone analytics
	if zone, exists := o.zones[pickupZoneName]; exists {
		atomic.AddInt32(&zone.WaitingCustomers, -1)
		atomic.AddInt32(&zone.AvailableDrivers, -1)
		atomic.AddInt32(&zone.ActiveRides, 1)
	}
	
	// Store active ride
	o.ridesMutex.Lock()
	o.activeRides[ride.RideID] = ride
	atomic.AddInt64(&o.metrics.ActiveRides, 1)
	o.ridesMutex.Unlock()
	
	fmt.Printf("🚗 Ride %s assigned to %s (%s)\n", 
		ride.RideID, driver.Name, driver.VehicleType)
	
	// Simulate ride lifecycle
	go o.simulateRideLifecycle(ride, driver)
}

func (o *OlaRideAnalytics) simulateRideLifecycle(ride *Ride, driver *Driver) {
	// Driver arriving (2-8 minutes)
	arrivalTime := time.Duration(2+rand.Intn(6)) * time.Minute
	time.Sleep(arrivalTime / 60) // Scale down for demo
	
	ride.Status = DriverArriving
	
	// Ride starts
	startDelay := time.Duration(1+rand.Intn(3)) * time.Minute
	time.Sleep(startDelay / 60)
	
	now := time.Now()
	ride.StartTime = &now
	ride.Status = RideStarted
	
	// Ride in progress
	rideTime := time.Duration(ride.Duration) * time.Minute
	time.Sleep(rideTime / 60) // Scale down for demo
	
	// Ride completed
	endTime := time.Now()
	ride.EndTime = &endTime
	ride.Status = RideCompleted
	
	// Calculate actual fare (may vary from estimate due to traffic, route changes)
	ride.ActualFare = ride.EstimatedFare * (0.9 + rand.Float64()*0.2) // ±10% variation
	
	// Customer rating (mostly good ratings in India)
	ratings := []int{3, 4, 4, 4, 5, 5, 5, 5, 5, 5}
	ride.Rating = ratings[rand.Intn(len(ratings))]
	
	// Update driver stats
	driver.EarningsToday += ride.ActualFare * 0.8 // Driver gets 80%
	driver.RidesCompleted++
	driver.IsAvailable = true
	
	// Move completed ride
	o.ridesMutex.Lock()
	delete(o.activeRides, ride.RideID)
	o.completedRides = append(o.completedRides, ride)
	atomic.AddInt64(&o.metrics.ActiveRides, -1)
	atomic.AddInt64(&o.metrics.CompletedRides, 1)
	o.ridesMutex.Unlock()
	
	// Update metrics
	atomic.AddInt64(&o.metrics.VehicleTypeDistribution[ride.VehicleType], 1)
	
	newRevenue := atomic.LoadInt64((*int64)(&o.metrics.TotalRevenue))
	atomic.StoreInt64((*int64)(&o.metrics.TotalRevenue), newRevenue+int64(ride.ActualFare))
	
	// Update zone analytics
	pickupZoneName := findNearestZone(ride.PickupLocation)
	if zone, exists := o.zones[pickupZoneName]; exists {
		atomic.AddInt32(&zone.ActiveRides, -1)
		atomic.AddInt32(&zone.AvailableDrivers, 1)
	}
	
	fmt.Printf("✅ Ride %s completed - ₹%.2f (%d⭐) by %s\n", 
		ride.RideID, ride.ActualFare, ride.Rating, driver.Name)
}

func (o *OlaRideAnalytics) updateAnalytics() {
	// Update surge multipliers for all zones
	for _, zone := range o.zones {
		zone.SurgeMultiplier = o.calculateSurgeMultiplier(zone)
		zone.LastUpdated = time.Now()
	}
	
	// Calculate average metrics
	completedRides := atomic.LoadInt64(&o.metrics.CompletedRides)
	if completedRides > 0 {
		totalRideTime := 0.0
		totalWaitTime := 0.0
		totalRatings := 0.0
		
		for _, ride := range o.completedRides {
			if ride.StartTime != nil && ride.EndTime != nil {
				totalRideTime += ride.EndTime.Sub(*ride.StartTime).Minutes()
				totalWaitTime += ride.StartTime.Sub(ride.BookingTime).Minutes()
				totalRatings += float64(ride.Rating)
			}
		}
		
		if len(o.completedRides) > 0 {
			o.metrics.mutex.Lock()
			o.metrics.AverageRideTime = totalRideTime / float64(len(o.completedRides))
			o.metrics.AverageWaitTime = totalWaitTime / float64(len(o.completedRides))
			o.metrics.CustomerSatisfaction = totalRatings / float64(len(o.completedRides))
			o.metrics.mutex.Unlock()
		}
	}
	
	// Calculate driver utilization
	totalDrivers := len(o.drivers)
	busyDrivers := 0
	
	for _, driver := range o.drivers {
		if !driver.IsAvailable {
			busyDrivers++
		}
	}
	
	o.metrics.mutex.Lock()
	if totalDrivers > 0 {
		o.metrics.DriverUtilization = (float64(busyDrivers) / float64(totalDrivers)) * 100
	}
	o.metrics.mutex.Unlock()
}

func (o *OlaRideAnalytics) printDashboard() {
	fmt.Println("\n" + strings.Repeat("=", 80))
	fmt.Println("🚗 OLA REAL-TIME RIDE ANALYTICS DASHBOARD 🚗")
	fmt.Println(strings.Repeat("=", 80))
	
	metrics := o.metrics
	
	fmt.Printf("📊 Total Rides: %d\n", atomic.LoadInt64(&metrics.TotalRides))
	fmt.Printf("✅ Completed: %d\n", atomic.LoadInt64(&metrics.CompletedRides))
	fmt.Printf("🚗 Active Rides: %d\n", atomic.LoadInt64(&metrics.ActiveRides))
	fmt.Printf("❌ Cancelled: %d\n", atomic.LoadInt64(&metrics.CancelledRides))
	
	successRate := float64(atomic.LoadInt64(&metrics.CompletedRides)) / 
		math.Max(1, float64(atomic.LoadInt64(&metrics.TotalRides))) * 100
	fmt.Printf("📈 Success Rate: %.1f%%\n", successRate)
	
	fmt.Printf("💰 Total Revenue: ₹%.2f\n", float64(atomic.LoadInt64((*int64)(&metrics.TotalRevenue))))
	
	metrics.mutex.RLock()
	fmt.Printf("⏱️ Avg Ride Time: %.1f minutes\n", metrics.AverageRideTime)
	fmt.Printf("⌛ Avg Wait Time: %.1f minutes\n", metrics.AverageWaitTime)
	fmt.Printf("👥 Driver Utilization: %.1f%%\n", metrics.DriverUtilization)
	fmt.Printf("⭐ Customer Satisfaction: %.1f/5.0\n", metrics.CustomerSatisfaction)
	metrics.mutex.RUnlock()
	
	// Vehicle type distribution
	fmt.Println("\n🚙 Vehicle Type Distribution:")
	for vehicleType, count := range metrics.VehicleTypeDistribution {
		if count > 0 {
			fmt.Printf("  %s: %d rides\n", vehicleType, count)
		}
	}
	
	// Zone analytics with surge pricing
	fmt.Println("\n🌍 Zone Analytics & Surge Pricing:")
	for _, zone := range o.zones {
		surgeIcon := "🟢"
		if zone.SurgeMultiplier >= 2.0 {
			surgeIcon = "🔴"
		} else if zone.SurgeMultiplier >= 1.5 {
			surgeIcon = "🟡"
		}
		
		fmt.Printf("  %s %s: Active: %d | Waiting: %d | Drivers: %d | Surge: %.1fx\n",
			surgeIcon, zone.ZoneName,
			atomic.LoadInt32(&zone.ActiveRides),
			atomic.LoadInt32(&zone.WaitingCustomers),
			atomic.LoadInt32(&zone.AvailableDrivers),
			zone.SurgeMultiplier)
	}
	
	// Top performing drivers
	fmt.Println("\n👨‍💼 Top Drivers Today:")
	topDrivers := o.getTopDriversByEarnings(5)
	for i, driver := range topDrivers {
		fmt.Printf("  %d. %s: ₹%.0f earned, %d rides, %.1f⭐\n",
			i+1, driver.Name, driver.EarningsToday, driver.RidesCompleted, driver.Rating)
	}
	
	fmt.Printf("\n🕐 Last Updated: %s\n", time.Now().Format("15:04:05"))
	fmt.Println(strings.Repeat("=", 80))
}

func (o *OlaRideAnalytics) getTopDriversByEarnings(limit int) []*Driver {
	drivers := make([]*Driver, 0, len(o.drivers))
	
	for _, driver := range o.drivers {
		drivers = append(drivers, driver)
	}
	
	// Sort by earnings (simple bubble sort for demo)
	for i := 0; i < len(drivers)-1; i++ {
		for j := 0; j < len(drivers)-i-1; j++ {
			if drivers[j].EarningsToday < drivers[j+1].EarningsToday {
				drivers[j], drivers[j+1] = drivers[j+1], drivers[j]
			}
		}
	}
	
	if limit > len(drivers) {
		limit = len(drivers)
	}
	
	return drivers[:limit]
}

func (o *OlaRideAnalytics) simulateRushHour(durationMinutes int) {
	fmt.Printf("🔥 Starting Ola rush hour simulation for %d minutes\n", durationMinutes)
	fmt.Println("🚗 Processing ride requests, driver assignments, और surge pricing...\n")
	
	o.isRunning = true
	
	// Start analytics dashboard
	dashboardTicker := time.NewTicker(30 * time.Second)
	go func() {
		for o.isRunning {
			select {
			case <-dashboardTicker.C:
				o.printDashboard()
			case <-o.stopChan:
				dashboardTicker.Stop()
				return
			}
		}
	}()
	
	// Start analytics updates
	analyticsTicker := time.NewTicker(10 * time.Second)
	go func() {
		for o.isRunning {
			select {
			case <-analyticsTicker.C:
				o.updateAnalytics()
			case <-o.stopChan:
				analyticsTicker.Stop()
				return
			}
		}
	}()
	
	// Rush hour patterns
	patterns := []struct {
		startPercent float64
		endPercent   float64
		ridesPerMin  int
		description  string
	}{
		{0.0, 0.2, 50, "Morning Rush - Office goers"},
		{0.2, 0.4, 80, "Peak Morning - Maximum demand"},
		{0.4, 0.6, 60, "Mid-day - Steady demand"},
		{0.6, 0.8, 90, "Evening Rush - Going home"},
		{0.8, 1.0, 40, "Late Evening - Leisure rides"},
	}
	
	startTime := time.Now()
	endTime := startTime.Add(time.Duration(durationMinutes) * time.Minute)
	patternIndex := 0
	
	for time.Now().Before(endTime) && o.isRunning {
		progress := time.Since(startTime).Seconds() / (time.Duration(durationMinutes) * time.Minute).Seconds()
		
		// Update pattern if needed
		if patternIndex < len(patterns) {
			pattern := patterns[patternIndex]
			
			if progress >= pattern.endPercent && patternIndex < len(patterns)-1 {
				patternIndex++
				fmt.Printf("📊 Pattern Change: %s\n", patterns[patternIndex].description)
			}
			
			if progress >= pattern.startPercent && progress <= pattern.endPercent {
				ridesPerSecond := pattern.ridesPerMin / 60
				
				for i := 0; i < ridesPerSecond; i++ {
					ride := o.generateRideRequest()
					go o.processRideRequest(ride)
				}
			}
		}
		
		time.Sleep(1 * time.Second)
	}
	
	o.isRunning = false
	o.stopChan <- true
	o.stopChan <- true // Stop both goroutines
	
	fmt.Println("\n🏁 Rush hour simulation completed!")
	o.printDashboard()
}

func strings.Repeat(s string, count int) string {
	result := ""
	for i := 0; i < count; i++ {
		result += s
	}
	return result
}

func main() {
	fmt.Println("🇮🇳 Ola Real-time Ride Analytics - Mumbai Simulation")
	fmt.Println("🚗 Simulating drivers, rides, surge pricing, और demand-supply dynamics...")
	fmt.Println("📱 Real-time tracking और analytics active...\n")
	
	analytics := NewOlaRideAnalytics()
	
	// Initialize system
	analytics.InitializeDrivers()
	
	// Run rush hour simulation
	analytics.simulateRushHour(5) // 5 minutes demo
	
	// Final summary
	totalRides := atomic.LoadInt64(&analytics.metrics.TotalRides)
	completedRides := atomic.LoadInt64(&analytics.metrics.CompletedRides)
	totalRevenue := atomic.LoadInt64((*int64)(&analytics.metrics.TotalRevenue))
	
	fmt.Printf("\n🎯 SIMULATION SUMMARY\n")
	fmt.Printf("Total Rides: %d\n", totalRides)
	fmt.Printf("Completed: %d\n", completedRides)
	fmt.Printf("Success Rate: %.1f%%\n", (float64(completedRides)/math.Max(1, float64(totalRides)))*100)
	fmt.Printf("Total Revenue: ₹%.2f\n", float64(totalRevenue))
	fmt.Printf("Total Drivers: %d\n", len(analytics.drivers))
	
	fmt.Println("\n💡 Production system would handle:")
	fmt.Println("   - 1M+ rides daily across 250+ cities")
	fmt.Println("   - Real-time GPS tracking every 5 seconds")
	fmt.Println("   - Dynamic surge pricing based on demand")
	fmt.Println("   - ML-based ETA और route optimization")
}
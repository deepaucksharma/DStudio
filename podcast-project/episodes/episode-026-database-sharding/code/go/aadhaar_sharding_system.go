// Aadhaar-based Database Sharding System
// आधार आधारित डेटाबेस शार्डिंग सिस्टम
//
// यह system दिखाता है कि कैसे भारत के 130 crore citizens के
// Aadhaar records को efficiently distribute करें multiple shards में

package main

import (
	"crypto/md5"
	"fmt"
	"log"
	"math/rand"
	"sort"
	"strconv"
	"sync"
	"time"
)

// AadhaarShardConfig represents configuration for each shard
// प्रत्येक शार्ड के लिए configuration
type AadhaarShardConfig struct {
	ShardID      string `json:"shard_id"`
	ShardName    string `json:"shard_name"`
	Region       string `json:"region"`
	Host         string `json:"host"`
	Port         int    `json:"port"`
	Capacity     int    `json:"capacity"`        // Maximum records
	CurrentLoad  int    `json:"current_load"`    // Current record count
	Languages    []string `json:"languages"`     // Supported languages
	States       []string `json:"states"`        // States covered
	IsActive     bool   `json:"is_active"`
}

// AadhaarRecord represents an Aadhaar record structure
// आधार रिकॉर्ड की संरचना
type AadhaarRecord struct {
	AadhaarNumber string    `json:"aadhaar_number"`
	Name          string    `json:"name"`
	DOB           time.Time `json:"date_of_birth"`
	Gender        string    `json:"gender"`
	Address       struct {
		Line1    string `json:"line1"`
		Line2    string `json:"line2"`
		District string `json:"district"`
		State    string `json:"state"`
		Pincode  string `json:"pincode"`
	} `json:"address"`
	Phone         string    `json:"phone"`
	Email         string    `json:"email"`
	CreatedAt     time.Time `json:"created_at"`
	LastUpdated   time.Time `json:"last_updated"`
	IsVerified    bool      `json:"is_verified"`
}

// AadhaarShardManager manages the sharding system
// शार्डिंग सिस्टम का प्रबंधक
type AadhaarShardManager struct {
	shards          map[string]*AadhaarShardConfig
	consistentHash  *ConsistentHashRing
	mutex           sync.RWMutex
	metricsCollector *ShardMetrics
}

// ConsistentHashRing implements consistent hashing for load distribution
// लोड वितरण के लिए consistent hashing
type ConsistentHashRing struct {
	hashRing []uint32
	shardMap map[uint32]string
	mutex    sync.RWMutex
}

// ShardMetrics collects performance metrics
// प्रदर्शन मेट्रिक्स का संग्रह
type ShardMetrics struct {
	TotalRequests    int64
	SuccessfulWrites int64
	FailedWrites     int64
	AverageLatency   time.Duration
	ShardStats       map[string]*ShardStat
	mutex            sync.RWMutex
}

type ShardStat struct {
	RequestCount int64
	SuccessCount int64
	FailureCount int64
	AvgLatency   time.Duration
}

// NewAadhaarShardManager creates a new sharding manager
// नया शार्डिंग मैनेजर बनाता है
func NewAadhaarShardManager() *AadhaarShardManager {
	manager := &AadhaarShardManager{
		shards:           make(map[string]*AadhaarShardConfig),
		consistentHash:   NewConsistentHashRing(),
		metricsCollector: NewShardMetrics(),
	}
	
	// Initialize Indian regional shards
	// भारतीय क्षेत्रीय शार्ड्स को initialize करें
	manager.initializeIndianShards()
	
	return manager
}

// initializeIndianShards sets up shards for different Indian regions
// विभिन्न भारतीय क्षेत्रों के लिए शार्ड्स स्थापित करता है
func (asm *AadhaarShardManager) initializeIndianShards() {
	shardConfigs := []*AadhaarShardConfig{
		{
			ShardID:     "NORTH_001",
			ShardName:   "North India Primary",
			Region:      "North India",
			Host:        "aadhaar-north-primary.uidai.gov.in",
			Port:        5432,
			Capacity:    30000000, // 3 crore records
			CurrentLoad: 0,
			Languages:   []string{"Hindi", "Punjabi", "Urdu"},
			States:      []string{"Delhi", "Punjab", "Haryana", "Uttar Pradesh", "Rajasthan"},
			IsActive:    true,
		},
		{
			ShardID:     "SOUTH_001",
			ShardName:   "South India Primary", 
			Region:      "South India",
			Host:        "aadhaar-south-primary.uidai.gov.in",
			Port:        5432,
			Capacity:    35000000, // 3.5 crore records
			CurrentLoad: 0,
			Languages:   []string{"Tamil", "Telugu", "Kannada", "Malayalam"},
			States:      []string{"Tamil Nadu", "Karnataka", "Andhra Pradesh", "Telangana", "Kerala"},
			IsActive:    true,
		},
		{
			ShardID:     "WEST_001",
			ShardName:   "West India Primary",
			Region:      "West India", 
			Host:        "aadhaar-west-primary.uidai.gov.in",
			Port:        5432,
			Capacity:    40000000, // 4 crore records (includes Mumbai)
			CurrentLoad: 0,
			Languages:   []string{"Marathi", "Gujarati", "Hindi"},
			States:      []string{"Maharashtra", "Gujarat", "Goa"},
			IsActive:    true,
		},
		{
			ShardID:     "EAST_001",
			ShardName:   "East India Primary",
			Region:      "East India",
			Host:        "aadhaar-east-primary.uidai.gov.in", 
			Port:        5432,
			Capacity:    25000000, // 2.5 crore records
			CurrentLoad: 0,
			Languages:   []string{"Bengali", "Odia", "Hindi"},
			States:      []string{"West Bengal", "Odisha", "Bihar", "Jharkhand"},
			IsActive:    true,
		},
	}
	
	for _, config := range shardConfigs {
		asm.addShard(config)
	}
	
	log.Printf("✅ भारतीय शार्ड्स initialized: %d shards ready", len(shardConfigs))
}

// addShard adds a new shard to the system
// सिस्टम में नया शार्ड जोड़ता है
func (asm *AadhaarShardManager) addShard(config *AadhaarShardConfig) {
	asm.mutex.Lock()
	defer asm.mutex.Unlock()
	
	asm.shards[config.ShardID] = config
	asm.consistentHash.AddShard(config.ShardID)
	
	// Initialize metrics for this shard
	asm.metricsCollector.initializeShardStat(config.ShardID)
	
	log.Printf("🔧 Added shard: %s (%s) - Capacity: %d", 
		config.ShardName, config.Region, config.Capacity)
}

// GetShardForAadhaar determines which shard should store the given Aadhaar
// दिए गए आधार के लिए उपयुक्त शार्ड का निर्धारण करता है
func (asm *AadhaarShardManager) GetShardForAadhaar(aadhaarNumber string) (*AadhaarShardConfig, error) {
	if !isValidAadhaar(aadhaarNumber) {
		return nil, fmt.Errorf("invalid Aadhaar number: %s", aadhaarNumber)
	}
	
	shardID := asm.consistentHash.GetShard(aadhaarNumber)
	
	asm.mutex.RLock()
	shard, exists := asm.shards[shardID]
	asm.mutex.RUnlock()
	
	if !exists {
		return nil, fmt.Errorf("shard not found for ID: %s", shardID)
	}
	
	log.Printf("📍 Aadhaar %s mapped to shard: %s (%s)", 
		maskAadhaar(aadhaarNumber), shard.ShardName, shard.Region)
	
	return shard, nil
}

// StoreAadhaarRecord stores an Aadhaar record in appropriate shard
// उपयुक्त शार्ड में आधार रिकॉर्ड संग्रहीत करता है
func (asm *AadhaarShardManager) StoreAadhaarRecord(record *AadhaarRecord) error {
	startTime := time.Now()
	
	shard, err := asm.GetShardForAadhaar(record.AadhaarNumber)
	if err != nil {
		asm.metricsCollector.recordFailure("UNKNOWN", time.Since(startTime))
		return fmt.Errorf("failed to get shard: %w", err)
	}
	
	// Check shard capacity
	if shard.CurrentLoad >= shard.Capacity {
		asm.metricsCollector.recordFailure(shard.ShardID, time.Since(startTime))
		return fmt.Errorf("shard %s is at full capacity", shard.ShardName)
	}
	
	// Simulate database write operation
	// डेटाबेस राइट ऑपरेशन की अनुकृति
	err = asm.simulateShardWrite(shard, record)
	if err != nil {
		asm.metricsCollector.recordFailure(shard.ShardID, time.Since(startTime))
		return fmt.Errorf("failed to write to shard %s: %w", shard.ShardName, err)
	}
	
	// Update shard load
	asm.mutex.Lock()
	shard.CurrentLoad++
	asm.mutex.Unlock()
	
	// Record successful operation
	asm.metricsCollector.recordSuccess(shard.ShardID, time.Since(startTime))
	
	log.Printf("💾 Stored Aadhaar record for %s in %s", 
		record.Name, shard.ShardName)
	
	return nil
}

// simulateShardWrite simulates writing to a database shard
// डेटाबेस शार्ड में लिखने की अनुकृति
func (asm *AadhaarShardManager) simulateShardWrite(shard *AadhaarShardConfig, record *AadhaarRecord) error {
	// Simulate network latency and processing time
	latencyMs := rand.Intn(100) + 10 // 10-110ms
	time.Sleep(time.Duration(latencyMs) * time.Millisecond)
	
	// Simulate occasional failures (5% failure rate)
	if rand.Float32() < 0.05 {
		return fmt.Errorf("database connection timeout")
	}
	
	return nil
}

// GetShardDistributionStats returns distribution statistics
// वितरण आंकड़े वापस करता है
func (asm *AadhaarShardManager) GetShardDistributionStats() map[string]interface{} {
	asm.mutex.RLock()
	defer asm.mutex.RUnlock()
	
	stats := make(map[string]interface{})
	
	var totalCapacity, totalLoad int
	shardDetails := make([]map[string]interface{}, 0)
	
	for shardID, shard := range asm.shards {
		totalCapacity += shard.Capacity
		totalLoad += shard.CurrentLoad
		
		loadPercent := float64(shard.CurrentLoad) / float64(shard.Capacity) * 100
		
		shardDetail := map[string]interface{}{
			"shard_id":       shardID,
			"shard_name":     shard.ShardName,
			"region":         shard.Region,
			"capacity":       shard.Capacity,
			"current_load":   shard.CurrentLoad,
			"load_percent":   fmt.Sprintf("%.1f%%", loadPercent),
			"states":         shard.States,
			"is_active":      shard.IsActive,
		}
		
		shardDetails = append(shardDetails, shardDetail)
	}
	
	stats["total_shards"] = len(asm.shards)
	stats["total_capacity"] = totalCapacity
	stats["total_load"] = totalLoad
	stats["overall_load_percent"] = float64(totalLoad) / float64(totalCapacity) * 100
	stats["shard_details"] = shardDetails
	
	return stats
}

// RebalanceShards adds a new shard and rebalances the system
// नया शार्ड जोड़कर सिस्टम को rebalance करता है
func (asm *AadhaarShardManager) RebalanceShards(newShard *AadhaarShardConfig) {
	log.Printf("🔄 Starting rebalancing with new shard: %s", newShard.ShardName)
	
	// Add the new shard
	asm.addShard(newShard)
	
	// In production, you would migrate data here
	// प्रोडक्शन में, यहाँ डेटा migrate करना होगा
	log.Printf("📊 Rebalancing would migrate approximately %.0f%% of data", 
		100.0/float64(len(asm.shards)))
	
	log.Printf("✅ Rebalancing completed - Now %d shards active", len(asm.shards))
}

// Consistent Hash Ring Implementation
// Consistent Hash Ring का कार्यान्वयन

func NewConsistentHashRing() *ConsistentHashRing {
	return &ConsistentHashRing{
		hashRing: make([]uint32, 0),
		shardMap: make(map[uint32]string),
	}
}

func (chr *ConsistentHashRing) AddShard(shardID string) {
	chr.mutex.Lock()
	defer chr.mutex.Unlock()
	
	// Add multiple virtual nodes for better distribution
	// बेहतर वितरण के लिए कई virtual nodes जोड़ें
	virtualNodes := 150
	
	for i := 0; i < virtualNodes; i++ {
		key := fmt.Sprintf("%s:%d", shardID, i)
		hash := hashString(key)
		
		chr.hashRing = append(chr.hashRing, hash)
		chr.shardMap[hash] = shardID
	}
	
	// Keep the ring sorted
	sort.Slice(chr.hashRing, func(i, j int) bool {
		return chr.hashRing[i] < chr.hashRing[j]
	})
}

func (chr *ConsistentHashRing) GetShard(key string) string {
	chr.mutex.RLock()
	defer chr.mutex.RUnlock()
	
	if len(chr.hashRing) == 0 {
		return ""
	}
	
	hash := hashString(key)
	
	// Find the first hash ring position >= hash
	idx := sort.Search(len(chr.hashRing), func(i int) bool {
		return chr.hashRing[i] >= hash
	})
	
	// Wrap around if necessary (circular ring)
	if idx == len(chr.hashRing) {
		idx = 0
	}
	
	ringPosition := chr.hashRing[idx]
	return chr.shardMap[ringPosition]
}

// Metrics Implementation
// मेट्रिक्स का कार्यान्वयन

func NewShardMetrics() *ShardMetrics {
	return &ShardMetrics{
		ShardStats: make(map[string]*ShardStat),
	}
}

func (sm *ShardMetrics) initializeShardStat(shardID string) {
	sm.mutex.Lock()
	defer sm.mutex.Unlock()
	
	sm.ShardStats[shardID] = &ShardStat{}
}

func (sm *ShardMetrics) recordSuccess(shardID string, latency time.Duration) {
	sm.mutex.Lock()
	defer sm.mutex.Unlock()
	
	sm.TotalRequests++
	sm.SuccessfulWrites++
	
	if stat, exists := sm.ShardStats[shardID]; exists {
		stat.RequestCount++
		stat.SuccessCount++
		stat.AvgLatency = (stat.AvgLatency + latency) / 2
	}
}

func (sm *ShardMetrics) recordFailure(shardID string, latency time.Duration) {
	sm.mutex.Lock()
	defer sm.mutex.Unlock()
	
	sm.TotalRequests++
	sm.FailedWrites++
	
	if stat, exists := sm.ShardStats[shardID]; exists {
		stat.RequestCount++
		stat.FailureCount++
	}
}

func (sm *ShardMetrics) GetMetricsSummary() map[string]interface{} {
	sm.mutex.RLock()
	defer sm.mutex.RUnlock()
	
	successRate := float64(sm.SuccessfulWrites) / float64(sm.TotalRequests) * 100
	
	summary := map[string]interface{}{
		"total_requests":    sm.TotalRequests,
		"successful_writes": sm.SuccessfulWrites,
		"failed_writes":     sm.FailedWrites,
		"success_rate":      fmt.Sprintf("%.2f%%", successRate),
		"shard_stats":       sm.ShardStats,
	}
	
	return summary
}

// Utility functions
// उपयोगिता फंक्शन्स

func isValidAadhaar(aadhaar string) bool {
	// Remove spaces and hyphens
	clean := ""
	for _, r := range aadhaar {
		if r >= '0' && r <= '9' {
			clean += string(r)
		}
	}
	
	// Must be exactly 12 digits
	if len(clean) != 12 {
		return false
	}
	
	// Simple validation - in production, implement Verhoeff checksum
	return true
}

func maskAadhaar(aadhaar string) string {
	if len(aadhaar) < 8 {
		return "****"
	}
	return "****-****-" + aadhaar[len(aadhaar)-4:]
}

func hashString(s string) uint32 {
	h := md5.Sum([]byte(s))
	return uint32(h[0])<<24 | uint32(h[1])<<16 | uint32(h[2])<<8 | uint32(h[3])
}

// generateSampleAadhaar generates sample Aadhaar numbers for testing
// परीक्षण के लिए नमूना आधार संख्या उत्पन्न करता है
func generateSampleAadhaar(count int) []*AadhaarRecord {
	records := make([]*AadhaarRecord, count)
	
	names := []string{
		"राज शर्मा", "प्रिया पटेल", "अमित कुमार", "सुनीता देवी", "विकास यादव",
		"अनिता सिंह", "राहुल गुप्ता", "मीरा शाह", "सुरेश खान", "पूजा अग्रवाल",
	}
	
	states := []string{
		"Maharashtra", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Gujarat",
		"West Bengal", "Delhi", "Punjab", "Haryana", "Rajasthan",
	}
	
	for i := 0; i < count; i++ {
		aadhaarNum := fmt.Sprintf("%012d", rand.Intn(999999999999-100000000000)+100000000000)
		
		record := &AadhaarRecord{
			AadhaarNumber: aadhaarNum,
			Name:          names[rand.Intn(len(names))],
			DOB:           time.Now().AddDate(-rand.Intn(60)-18, -rand.Intn(12), -rand.Intn(30)),
			Gender:        []string{"M", "F"}[rand.Intn(2)],
			Phone:         fmt.Sprintf("9%09d", rand.Intn(999999999)),
			CreatedAt:     time.Now(),
			LastUpdated:   time.Now(),
			IsVerified:    rand.Float32() > 0.1, // 90% verified
		}
		
		// Set address
		record.Address.State = states[rand.Intn(len(states))]
		record.Address.Pincode = fmt.Sprintf("%06d", rand.Intn(799999-100000)+100000)
		record.Address.District = "Sample District"
		record.Address.Line1 = "Sample Address Line 1"
		
		records[i] = record
	}
	
	return records
}

// Main function - demonstration
// मुख्य फंक्शन - प्रदर्शन
func main() {
	fmt.Println("🏛️ भारतीय आधार डेटाबेस शार्डिंग सिस्टम")
	fmt.Println(strings.Repeat("=", 60))
	
	// Initialize the sharding manager
	shardManager := NewAadhaarShardManager()
	
	// Generate sample Aadhaar records
	fmt.Println("\n📝 Generating sample Aadhaar records...")
	sampleRecords := generateSampleAadhaar(100)
	
	fmt.Printf("Generated %d sample records\n", len(sampleRecords))
	
	// Store records and demonstrate sharding
	fmt.Println("\n💾 Storing records across shards...")
	
	storedCount := 0
	for _, record := range sampleRecords {
		err := shardManager.StoreAadhaarRecord(record)
		if err != nil {
			log.Printf("❌ Failed to store record: %v", err)
		} else {
			storedCount++
		}
		
		// Add small delay to simulate real-world usage
		time.Sleep(10 * time.Millisecond)
	}
	
	fmt.Printf("✅ Successfully stored %d out of %d records\n", storedCount, len(sampleRecords))
	
	// Display distribution statistics
	fmt.Println("\n📊 Shard Distribution Statistics:")
	fmt.Println(strings.Repeat("-", 50))
	
	stats := shardManager.GetShardDistributionStats()
	fmt.Printf("Total Shards: %d\n", stats["total_shards"])
	fmt.Printf("Total Capacity: %d records\n", stats["total_capacity"])
	fmt.Printf("Total Load: %d records\n", stats["total_load"])
	fmt.Printf("Overall Load: %.2f%%\n", stats["overall_load_percent"])
	
	fmt.Println("\nPer-Shard Details:")
	if shardDetails, ok := stats["shard_details"].([]map[string]interface{}); ok {
		for _, shard := range shardDetails {
			fmt.Printf("  %s (%s):\n", shard["shard_name"], shard["region"])
			fmt.Printf("    Load: %s (%d/%d records)\n", 
				shard["load_percent"], shard["current_load"], shard["capacity"])
			fmt.Printf("    States: %v\n", shard["states"])
		}
	}
	
	// Display performance metrics
	fmt.Println("\n⚡ Performance Metrics:")
	fmt.Println(strings.Repeat("-", 30))
	
	metrics := shardManager.metricsCollector.GetMetricsSummary()
	fmt.Printf("Total Requests: %d\n", metrics["total_requests"])
	fmt.Printf("Success Rate: %s\n", metrics["success_rate"])
	fmt.Printf("Successful Writes: %d\n", metrics["successful_writes"])
	fmt.Printf("Failed Writes: %d\n", metrics["failed_writes"])
	
	// Demonstrate adding a new shard (Northeast India)
	fmt.Println("\n🔄 Adding Northeast India Shard...")
	
	northeastShard := &AadhaarShardConfig{
		ShardID:     "NORTHEAST_001",
		ShardName:   "Northeast India Primary",
		Region:      "Northeast India",
		Host:        "aadhaar-northeast-primary.uidai.gov.in",
		Port:        5432,
		Capacity:    10000000, // 1 crore records
		CurrentLoad: 0,
		Languages:   []string{"Assamese", "Bengali", "Hindi"},
		States:      []string{"Assam", "Meghalaya", "Manipur", "Nagaland", "Tripura", "Mizoram", "Arunachal Pradesh"},
		IsActive:    true,
	}
	
	shardManager.RebalanceShards(northeastShard)
	
	// Final statistics after rebalancing
	fmt.Println("\n📈 Final Statistics after Rebalancing:")
	fmt.Println(strings.Repeat("-", 45))
	
	finalStats := shardManager.GetShardDistributionStats()
	fmt.Printf("Active Shards: %d\n", finalStats["total_shards"])
	fmt.Printf("Total System Capacity: %d records (%.1f crore)\n", 
		finalStats["total_capacity"], float64(finalStats["total_capacity"].(int))/10000000.0)
	
	fmt.Println("\n💡 Production Recommendations:")
	fmt.Println(strings.Repeat("-", 35))
	fmt.Println("✅ Implement proper Verhoeff checksum validation")
	fmt.Println("✅ Add read replicas for each shard")  
	fmt.Println("✅ Set up cross-region backup shards")
	fmt.Println("✅ Implement automatic failover mechanisms")
	fmt.Println("✅ Add comprehensive audit logging")
	fmt.Println("✅ Monitor shard health with real-time alerts")
	
	fmt.Println("\n🔐 Security Considerations:")
	fmt.Println("❗ Encrypt Aadhaar data at rest and in transit")
	fmt.Println("❗ Implement strict access controls")
	fmt.Println("❗ Log all access attempts")
	fmt.Println("❗ Regular security audits required")
}
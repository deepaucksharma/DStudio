/*
UPI Failure Analysis System
===========================

Advanced UPI transaction failure analysis with probability calculations.
Real examples: PhonePe, GooglePay, Paytm failure pattern analysis during festivals

मुख्य concepts:
1. Go-based probability analysis for UPI systems
2. Statistical failure pattern detection
3. Indian festival season impact modeling
4. Real-time UPI reliability monitoring

Mumbai analogy: Like analyzing Mumbai local train delay patterns - predictable failures!
Author: Hindi Tech Podcast Series
*/

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"sort"
	"strconv"
	"strings"
	"time"
)

// Hindi comments के साथ comprehensive UPI failure analyzer

// UPITransaction represents a single UPI transaction record
// UPI transaction का individual record
type UPITransaction struct {
	TransactionID    string    `json:"transaction_id"`
	Provider         string    `json:"provider"`          // PhonePe, GooglePay, Paytm, etc.
	Amount           float64   `json:"amount"`            // Transaction amount in INR
	Timestamp        time.Time `json:"timestamp"`
	Success          bool      `json:"success"`
	FailureReason    string    `json:"failure_reason,omitempty"`
	ProcessingTime   int64     `json:"processing_time_ms"` // Processing time in milliseconds
	UserLocation     string    `json:"user_location"`      // City/State
	MerchantCategory string    `json:"merchant_category"`  // Food, Shopping, Recharge, etc.
	
	// Indian context factors - भारतीय context के factors
	IsMonsoonSeason  bool `json:"is_monsoon_season"`
	IsFestivalSeason bool `json:"is_festival_season"`
	IsPeakHour       bool `json:"is_peak_hour"`
	IsWeekend        bool `json:"is_weekend"`
}

// UPIFailureMetrics represents comprehensive failure analysis metrics
// UPI failure analysis की comprehensive metrics
type UPIFailureMetrics struct {
	Provider              string             `json:"provider"`
	TotalTransactions     int64              `json:"total_transactions"`
	SuccessfulTransactions int64             `json:"successful_transactions"`
	FailedTransactions    int64              `json:"failed_transactions"`
	SuccessRate           float64            `json:"success_rate"`
	AverageProcessingTime float64            `json:"avg_processing_time_ms"`
	
	// Context-specific success rates
	MonsoonSuccessRate   float64 `json:"monsoon_success_rate"`
	FestivalSuccessRate  float64 `json:"festival_success_rate"`
	PeakHourSuccessRate  float64 `json:"peak_hour_success_rate"`
	WeekendSuccessRate   float64 `json:"weekend_success_rate"`
	
	// Failure analysis
	FailureReasons       map[string]int64   `json:"failure_reasons"`
	LocationSuccessRates map[string]float64 `json:"location_success_rates"`
	
	// Indian insights
	MumbaiAnalogy        string             `json:"mumbai_analogy"`
	ReliabilityScore     float64            `json:"reliability_score"`
	RecommendationLevel  string             `json:"recommendation_level"`
}

// UPIFailureAnalyzer main analyzer struct
// मुख्य UPI failure analyzer struct
type UPIFailureAnalyzer struct {
	transactions      []UPITransaction
	providerMetrics   map[string]*UPIFailureMetrics
	analysisStartTime time.Time
	
	// Indian cities with high UPI volume - UPI volume वाले भारतीय शहर
	majorIndianCities []string
	
	// Festival months in India - भारत में festival के महीने
	festivalMonths map[int]bool
	
	// Monsoon months - Monsoon के महीने
	monsoonMonths map[int]bool
}

// NewUPIFailureAnalyzer creates a new analyzer instance
// नया analyzer instance बनाते हैं
func NewUPIFailureAnalyzer() *UPIFailureAnalyzer {
	analyzer := &UPIFailureAnalyzer{
		transactions:      make([]UPITransaction, 0),
		providerMetrics:   make(map[string]*UPIFailureMetrics),
		analysisStartTime: time.Now(),
		majorIndianCities: []string{
			"Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad",
			"Pune", "Kolkata", "Ahmedabad", "Surat", "Jaipur",
			"Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
		},
		festivalMonths: map[int]bool{
			3:  true, // Holi season
			8:  true, // Ganesh Chaturthi
			10: true, // Diwali season
			11: true, // Extended Diwali season
		},
		monsoonMonths: map[int]bool{
			6: true, // June
			7: true, // July
			8: true, // August
			9: true, // September
		},
	}
	
	fmt.Println("🇮🇳 UPI Failure Analyzer initialized")
	fmt.Println("💳 Ready to analyze UPI transaction patterns with Indian context!")
	
	return analyzer
}

// AddTransaction adds a new transaction to the analyzer
// Analyzer में नया transaction add करते हैं
func (ufa *UPIFailureAnalyzer) AddTransaction(transaction UPITransaction) {
	// Set Indian context factors automatically
	transaction.IsMonsoonSeason = ufa.isMonsoonSeason(transaction.Timestamp)
	transaction.IsFestivalSeason = ufa.isFestivalSeason(transaction.Timestamp)
	transaction.IsPeakHour = ufa.isPeakHour(transaction.Timestamp)
	transaction.IsWeekend = ufa.isWeekend(transaction.Timestamp)
	
	ufa.transactions = append(ufa.transactions, transaction)
	
	// Auto-update metrics every 100 transactions
	if len(ufa.transactions)%100 == 0 {
		ufa.updateProviderMetrics()
	}
}

// GenerateDemoTransactions creates realistic Indian UPI transaction data
// Realistic Indian UPI transaction data generate करते हैं
func (ufa *UPIFailureAnalyzer) GenerateDemoTransactions(count int) {
	fmt.Printf("📊 Generating %d realistic Indian UPI transactions...\n", count)
	
	providers := []string{"PhonePe", "GooglePay", "Paytm", "BHIM", "AmazonPay", "Mobikwik"}
	categories := []string{"Food", "Shopping", "Recharge", "Travel", "Utilities", "P2P"}
	failureReasons := []string{
		"NETWORK_ERROR", "BANK_TIMEOUT", "INSUFFICIENT_FUNDS",
		"TRANSACTION_LIMIT_EXCEEDED", "INVALID_PIN", "SYSTEM_MAINTENANCE",
		"MERCHANT_UNAVAILABLE", "CARD_BLOCKED", "SERVER_ERROR",
	}
	
	rand.Seed(time.Now().UnixNano())
	
	// Generate transactions over last 30 days
	startDate := time.Now().AddDate(0, 0, -30)
	
	for i := 0; i < count; i++ {
		// Random timestamp in last 30 days
		randomMinutes := rand.Intn(30 * 24 * 60) // Random minute in 30 days
		timestamp := startDate.Add(time.Duration(randomMinutes) * time.Minute)
		
		provider := providers[rand.Intn(len(providers))]
		category := categories[rand.Intn(len(categories))]
		city := ufa.majorIndianCities[rand.Intn(len(ufa.majorIndianCities))]
		
		// Generate realistic amount based on category
		amount := ufa.generateRealisticAmount(category)
		
		// Calculate success probability based on context
		baseSuccessRate := ufa.getProviderBaseSuccessRate(provider)
		contextAdjustedRate := ufa.adjustSuccessRateForContext(
			baseSuccessRate, timestamp, city, amount,
		)
		
		success := rand.Float64() < contextAdjustedRate
		var failureReason string
		if !success {
			failureReason = failureReasons[rand.Intn(len(failureReasons))]
		}
		
		// Processing time based on success and context
		processingTime := ufa.calculateProcessingTime(success, timestamp, provider)
		
		transaction := UPITransaction{
			TransactionID:    fmt.Sprintf("TXN_%d_%05d", timestamp.Unix(), i),
			Provider:         provider,
			Amount:           amount,
			Timestamp:        timestamp,
			Success:          success,
			FailureReason:    failureReason,
			ProcessingTime:   processingTime,
			UserLocation:     city,
			MerchantCategory: category,
		}
		
		ufa.AddTransaction(transaction)
	}
	
	fmt.Printf("✅ Generated %d UPI transactions successfully!\n", count)
}

// generateRealisticAmount creates realistic transaction amounts for different categories
// Different categories के लिए realistic transaction amounts generate करते हैं
func (ufa *UPIFailureAnalyzer) generateRealisticAmount(category string) float64 {
	switch category {
	case "Food":
		return float64(100 + rand.Intn(500)) // ₹100-600
	case "Shopping":
		return float64(500 + rand.Intn(2500)) // ₹500-3000
	case "Recharge":
		return float64(50 + rand.Intn(200)) // ₹50-250
	case "Travel":
		return float64(200 + rand.Intn(1800)) // ₹200-2000
	case "Utilities":
		return float64(300 + rand.Intn(1700)) // ₹300-2000
	case "P2P":
		return float64(100 + rand.Intn(4900)) // ₹100-5000
	default:
		return float64(100 + rand.Intn(900)) // ₹100-1000
	}
}

// getProviderBaseSuccessRate returns base success rate for each provider
// हर provider का base success rate return करते हैं
func (ufa *UPIFailureAnalyzer) getProviderBaseSuccessRate(provider string) float64 {
	// Based on industry observations (approximate values)
	switch provider {
	case "PhonePe":
		return 0.984 // 98.4%
	case "GooglePay":
		return 0.981 // 98.1%
	case "Paytm":
		return 0.976 // 97.6%
	case "BHIM":
		return 0.973 // 97.3%
	case "AmazonPay":
		return 0.979 // 97.9%
	case "Mobikwik":
		return 0.971 // 97.1%
	default:
		return 0.975 // 97.5% default
	}
}

// adjustSuccessRateForContext adjusts success rate based on Indian context factors
// Indian context factors के अनुसार success rate adjust करते हैं
func (ufa *UPIFailureAnalyzer) adjustSuccessRateForContext(baseRate float64, timestamp time.Time, city string, amount float64) float64 {
	adjustedRate := baseRate
	
	// Monsoon impact - network issues during rains
	if ufa.isMonsoonSeason(timestamp) {
		adjustedRate *= 0.95 // 5% decrease
	}
	
	// Festival impact - high load during festivals
	if ufa.isFestivalSeason(timestamp) {
		adjustedRate *= 0.92 // 8% decrease
	}
	
	// Peak hour impact - server load during peak hours
	if ufa.isPeakHour(timestamp) {
		adjustedRate *= 0.97 // 3% decrease
	}
	
	// Weekend impact - generally better performance
	if ufa.isWeekend(timestamp) {
		adjustedRate *= 1.01 // 1% improvement
	}
	
	// City impact - tier 1 cities have better infrastructure
	tier1Cities := map[string]bool{
		"Mumbai": true, "Delhi": true, "Bangalore": true,
		"Chennai": true, "Hyderabad": true, "Pune": true,
	}
	if tier1Cities[city] {
		adjustedRate *= 1.005 // 0.5% bonus
	}
	
	// High-value transaction impact
	if amount > 2000 {
		adjustedRate *= 0.98 // 2% decrease for high-value transactions
	}
	
	// Keep rate between 85% and 99.5%
	if adjustedRate < 0.85 {
		adjustedRate = 0.85
	}
	if adjustedRate > 0.995 {
		adjustedRate = 0.995
	}
	
	return adjustedRate
}

// calculateProcessingTime calculates realistic processing time
// Realistic processing time calculate करते हैं
func (ufa *UPIFailureAnalyzer) calculateProcessingTime(success bool, timestamp time.Time, provider string) int64 {
	baseTime := int64(1500) // 1.5 seconds base
	
	// Provider-specific processing times
	switch provider {
	case "PhonePe":
		baseTime = 1200 // Faster processing
	case "GooglePay":
		baseTime = 1300
	case "Paytm":
		baseTime = 1600
	case "BHIM":
		baseTime = 1800 // Government app, slower
	}
	
	// Peak hour impact
	if ufa.isPeakHour(timestamp) {
		baseTime += int64(500) // Additional 500ms
	}
	
	// Monsoon impact
	if ufa.isMonsoonSeason(timestamp) {
		baseTime += int64(300) // Additional 300ms
	}
	
	// Festival impact
	if ufa.isFestivalSeason(timestamp) {
		baseTime += int64(800) // Additional 800ms
	}
	
	// Failure takes longer
	if !success {
		baseTime += int64(rand.Intn(2000)) // 0-2 seconds additional
	}
	
	// Add randomness
	randomVariation := int64(rand.Intn(1000)) // ±500ms variation
	baseTime += randomVariation - 500
	
	if baseTime < 500 {
		baseTime = 500 // Minimum 500ms
	}
	
	return baseTime
}

// Helper methods for Indian context detection
// Indian context detect करने के लिए helper methods

func (ufa *UPIFailureAnalyzer) isMonsoonSeason(timestamp time.Time) bool {
	return ufa.monsoonMonths[int(timestamp.Month())]
}

func (ufa *UPIFailureAnalyzer) isFestivalSeason(timestamp time.Time) bool {
	return ufa.festivalMonths[int(timestamp.Month())]
}

func (ufa *UPIFailureAnalyzer) isPeakHour(timestamp time.Time) bool {
	hour := timestamp.Hour()
	// Peak hours: 9-11 AM (morning), 6-9 PM (evening), 12-2 PM (lunch)
	return (hour >= 9 && hour <= 11) || (hour >= 12 && hour <= 14) || (hour >= 18 && hour <= 21)
}

func (ufa *UPIFailureAnalyzer) isWeekend(timestamp time.Time) bool {
	weekday := timestamp.Weekday()
	return weekday == time.Saturday || weekday == time.Sunday
}

// updateProviderMetrics updates metrics for all providers
// सभी providers के लिए metrics update करते हैं
func (ufa *UPIFailureAnalyzer) updateProviderMetrics() {
	// Group transactions by provider
	providerTransactions := make(map[string][]UPITransaction)
	for _, transaction := range ufa.transactions {
		providerTransactions[transaction.Provider] = append(
			providerTransactions[transaction.Provider], transaction,
		)
	}
	
	// Calculate metrics for each provider
	for provider, transactions := range providerTransactions {
		metrics := ufa.calculateMetricsForProvider(provider, transactions)
		ufa.providerMetrics[provider] = metrics
	}
}

// calculateMetricsForProvider calculates comprehensive metrics for a provider
// Provider के लिए comprehensive metrics calculate करते हैं
func (ufa *UPIFailureAnalyzer) calculateMetricsForProvider(provider string, transactions []UPITransaction) *UPIFailureMetrics {
	totalTxns := int64(len(transactions))
	var successfulTxns int64
	var totalProcessingTime int64
	failureReasons := make(map[string]int64)
	locationSuccessMap := make(map[string][]bool)
	
	// Context-specific counters
	var monsoonTxns, monsoonSuccess int64
	var festivalTxns, festivalSuccess int64
	var peakHourTxns, peakHourSuccess int64
	var weekendTxns, weekendSuccess int64
	
	for _, txn := range transactions {
		totalProcessingTime += txn.ProcessingTime
		
		if txn.Success {
			successfulTxns++
		} else {
			failureReasons[txn.FailureReason]++
		}
		
		// Location-wise tracking
		locationSuccessMap[txn.UserLocation] = append(
			locationSuccessMap[txn.UserLocation], txn.Success,
		)
		
		// Context-specific tracking
		if txn.IsMonsoonSeason {
			monsoonTxns++
			if txn.Success {
				monsoonSuccess++
			}
		}
		
		if txn.IsFestivalSeason {
			festivalTxns++
			if txn.Success {
				festivalSuccess++
			}
		}
		
		if txn.IsPeakHour {
			peakHourTxns++
			if txn.Success {
				peakHourSuccess++
			}
		}
		
		if txn.IsWeekend {
			weekendTxns++
			if txn.Success {
				weekendSuccess++
			}
		}
	}
	
	successRate := float64(successfulTxns) / float64(totalTxns)
	avgProcessingTime := float64(totalProcessingTime) / float64(totalTxns)
	
	// Calculate context-specific success rates
	monsoonSuccessRate := ufa.calculateContextSuccessRate(monsoonSuccess, monsoonTxns)
	festivalSuccessRate := ufa.calculateContextSuccessRate(festivalSuccess, festivalTxns)
	peakHourSuccessRate := ufa.calculateContextSuccessRate(peakHourSuccess, peakHourTxns)
	weekendSuccessRate := ufa.calculateContextSuccessRate(weekendSuccess, weekendTxns)
	
	// Calculate location-wise success rates
	locationSuccessRates := make(map[string]float64)
	for location, successList := range locationSuccessMap {
		var successes int64
		for _, success := range successList {
			if success {
				successes++
			}
		}
		locationSuccessRates[location] = float64(successes) / float64(len(successList))
	}
	
	// Calculate reliability score (composite metric)
	reliabilityScore := ufa.calculateReliabilityScore(successRate, avgProcessingTime, failureReasons)
	
	// Generate Mumbai analogy and recommendation level
	mumbaiAnalogy := ufa.generateMumbaiAnalogy(provider, successRate, reliabilityScore)
	recommendationLevel := ufa.getRecommendationLevel(reliabilityScore)
	
	return &UPIFailureMetrics{
		Provider:              provider,
		TotalTransactions:     totalTxns,
		SuccessfulTransactions: successfulTxns,
		FailedTransactions:    totalTxns - successfulTxns,
		SuccessRate:           successRate,
		AverageProcessingTime: avgProcessingTime,
		MonsoonSuccessRate:   monsoonSuccessRate,
		FestivalSuccessRate:  festivalSuccessRate,
		PeakHourSuccessRate:  peakHourSuccessRate,
		WeekendSuccessRate:   weekendSuccessRate,
		FailureReasons:       failureReasons,
		LocationSuccessRates: locationSuccessRates,
		MumbaiAnalogy:        mumbaiAnalogy,
		ReliabilityScore:     reliabilityScore,
		RecommendationLevel:  recommendationLevel,
	}
}

// calculateContextSuccessRate calculates success rate for a specific context
// Specific context के लिए success rate calculate करते हैं
func (ufa *UPIFailureAnalyzer) calculateContextSuccessRate(successes, total int64) float64 {
	if total == 0 {
		return 0.0
	}
	return float64(successes) / float64(total)
}

// calculateReliabilityScore calculates composite reliability score
// Composite reliability score calculate करते हैं
func (ufa *UPIFailureAnalyzer) calculateReliabilityScore(successRate, avgProcessingTime float64, failureReasons map[string]int64) float64 {
	// Base score from success rate (70% weight)
	score := successRate * 0.7
	
	// Processing time impact (20% weight)
	// Ideal processing time is 1500ms, penalize deviations
	timeScore := 1.0 - math.Min(0.3, math.Abs(avgProcessingTime-1500)/5000)
	score += timeScore * 0.2
	
	// Failure reason diversity impact (10% weight)
	// Fewer failure types = better (more predictable failures)
	diversityPenalty := math.Min(0.1, float64(len(failureReasons))*0.01)
	score += (1.0 - diversityPenalty) * 0.1
	
	return math.Max(0.0, math.Min(1.0, score))
}

// generateMumbaiAnalogy generates Mumbai-based analogy for provider performance
// Provider performance के लिए Mumbai-based analogy generate करते हैं
func (ufa *UPIFailureAnalyzer) generateMumbaiAnalogy(provider string, successRate, reliabilityScore float64) string {
	if reliabilityScore >= 0.95 {
		return fmt.Sprintf("जैसे Mumbai local trains के dry season में - %s बहुत reliable है!", provider)
	} else if reliabilityScore >= 0.9 {
		return fmt.Sprintf("जैसे Mumbai BEST buses - %s generally reliable लेकिन occasional delays", provider)
	} else if reliabilityScore >= 0.8 {
		return fmt.Sprintf("जैसे Mumbai traffic during peak hours - %s में कुछ congestion issues हैं", provider)
	} else if reliabilityScore >= 0.7 {
		return fmt.Sprintf("जैसे Mumbai auto-rickshaws - %s unpredictable है, कभी चलता है कभी नहीं", provider)
	} else {
		return fmt.Sprintf("जैसे Mumbai monsoon flooding - %s में serious reliability issues हैं!", provider)
	}
}

// getRecommendationLevel determines recommendation level based on reliability score
// Reliability score के base पर recommendation level determine करते हैं
func (ufa *UPIFailureAnalyzer) getRecommendationLevel(score float64) string {
	if score >= 0.95 {
		return "EXCELLENT"
	} else if score >= 0.9 {
		return "GOOD"
	} else if score >= 0.8 {
		return "ACCEPTABLE"
	} else if score >= 0.7 {
		return "NEEDS_IMPROVEMENT"
	} else {
		return "CRITICAL"
	}
}

// GenerateFailureAnalysisReport generates comprehensive failure analysis report
// Comprehensive failure analysis report generate करते हैं
func (ufa *UPIFailureAnalyzer) GenerateFailureAnalysisReport() string {
	if len(ufa.transactions) == 0 {
		return "❌ No transaction data available. Generate transaction data first!"
	}
	
	ufa.updateProviderMetrics() // Ensure latest metrics
	
	var report strings.Builder
	
	report.WriteString("🇮🇳 UPI FAILURE ANALYSIS REPORT\n")
	report.WriteString(strings.Repeat("=", 60) + "\n")
	report.WriteString(fmt.Sprintf("📊 Total Transactions Analyzed: %d\n", len(ufa.transactions)))
	report.WriteString(fmt.Sprintf("💳 UPI Providers: %d\n", len(ufa.providerMetrics)))
	report.WriteString(fmt.Sprintf("📅 Report Generated: %s IST\n\n", time.Now().Format("2006-01-02 15:04:05")))
	
	// Overall statistics
	var totalTxns, totalSuccessful int64
	var totalProcessingTime float64
	
	for _, metrics := range ufa.providerMetrics {
		totalTxns += metrics.TotalTransactions
		totalSuccessful += metrics.SuccessfulTransactions
		totalProcessingTime += metrics.AverageProcessingTime
	}
	
	overallSuccessRate := float64(totalSuccessful) / float64(totalTxns)
	avgSystemProcessingTime := totalProcessingTime / float64(len(ufa.providerMetrics))
	
	report.WriteString("📈 OVERALL UPI ECOSYSTEM STATISTICS\n")
	report.WriteString(strings.Repeat("-", 40) + "\n")
	report.WriteString(fmt.Sprintf("Overall Success Rate: %.2f%%\n", overallSuccessRate*100))
	report.WriteString(fmt.Sprintf("Average Processing Time: %.0fms\n", avgSystemProcessingTime))
	report.WriteString(fmt.Sprintf("Failed Transactions: %d (%.2f%%)\n\n", 
		totalTxns-totalSuccessful, (1-overallSuccessRate)*100))
	
	// Provider-wise analysis
	report.WriteString("💳 PROVIDER-WISE ANALYSIS\n")
	report.WriteString(strings.Repeat("-", 40) + "\n")
	
	// Sort providers by reliability score
	type providerScore struct {
		provider string
		metrics  *UPIFailureMetrics
	}
	
	var providerList []providerScore
	for provider, metrics := range ufa.providerMetrics {
		providerList = append(providerList, providerScore{provider, metrics})
	}
	
	sort.Slice(providerList, func(i, j int) bool {
		return providerList[i].metrics.ReliabilityScore > providerList[j].metrics.ReliabilityScore
	})
	
	for i, ps := range providerList {
		metrics := ps.metrics
		report.WriteString(fmt.Sprintf("\n%d. %s (%s)\n", i+1, ps.provider, metrics.RecommendationLevel))
		report.WriteString(fmt.Sprintf("   Success Rate: %.2f%%\n", metrics.SuccessRate*100))
		report.WriteString(fmt.Sprintf("   Reliability Score: %.3f\n", metrics.ReliabilityScore))
		report.WriteString(fmt.Sprintf("   Avg Processing Time: %.0fms\n", metrics.AverageProcessingTime))
		report.WriteString(fmt.Sprintf("   Total Transactions: %d\n", metrics.TotalTransactions))
		report.WriteString(fmt.Sprintf("   🏙️ %s\n", metrics.MumbaiAnalogy))
	}
	
	// Indian context analysis
	report.WriteString("\n\n🇮🇳 INDIAN CONTEXT ANALYSIS\n")
	report.WriteString(strings.Repeat("-", 40) + "\n")
	
	// Calculate overall context impact
	var overallMonsoon, overallFestival, overallPeakHour, overallWeekend float64
	count := 0
	
	for _, metrics := range ufa.providerMetrics {
		if metrics.MonsoonSuccessRate > 0 {
			overallMonsoon += metrics.MonsoonSuccessRate
			count++
		}
	}
	if count > 0 {
		overallMonsoon /= float64(count)
	}
	
	count = 0
	for _, metrics := range ufa.providerMetrics {
		if metrics.FestivalSuccessRate > 0 {
			overallFestival += metrics.FestivalSuccessRate
			count++
		}
	}
	if count > 0 {
		overallFestival /= float64(count)
	}
	
	count = 0
	for _, metrics := range ufa.providerMetrics {
		if metrics.PeakHourSuccessRate > 0 {
			overallPeakHour += metrics.PeakHourSuccessRate
			count++
		}
	}
	if count > 0 {
		overallPeakHour /= float64(count)
	}
	
	count = 0
	for _, metrics := range ufa.providerMetrics {
		if metrics.WeekendSuccessRate > 0 {
			overallWeekend += metrics.WeekendSuccessRate
			count++
		}
	}
	if count > 0 {
		overallWeekend /= float64(count)
	}
	
	report.WriteString("🌧️ Seasonal Impact Analysis:\n")
	if overallMonsoon > 0 {
		normalRate := overallSuccessRate
		monsoonImpact := (normalRate - overallMonsoon) * 100
		report.WriteString(fmt.Sprintf("   Monsoon Success Rate: %.2f%% (%.1f%% decrease)\n", 
			overallMonsoon*100, monsoonImpact))
	}
	
	if overallFestival > 0 {
		normalRate := overallSuccessRate
		festivalImpact := (normalRate - overallFestival) * 100
		report.WriteString(fmt.Sprintf("   Festival Success Rate: %.2f%% (%.1f%% decrease)\n", 
			overallFestival*100, festivalImpact))
	}
	
	if overallPeakHour > 0 {
		normalRate := overallSuccessRate
		peakImpact := (normalRate - overallPeakHour) * 100
		report.WriteString(fmt.Sprintf("   Peak Hour Success Rate: %.2f%% (%.1f%% decrease)\n", 
			overallPeakHour*100, peakImpact))
	}
	
	if overallWeekend > 0 {
		weekendImpact := (overallWeekend - overallSuccessRate) * 100
		report.WriteString(fmt.Sprintf("   Weekend Success Rate: %.2f%% (%.1f%% improvement)\n", 
			overallWeekend*100, weekendImpact))
	}
	
	// Top failure reasons across all providers
	report.WriteString("\n\n🚨 TOP FAILURE REASONS ACROSS ALL PROVIDERS\n")
	report.WriteString(strings.Repeat("-", 40) + "\n")
	
	combinedFailureReasons := make(map[string]int64)
	for _, metrics := range ufa.providerMetrics {
		for reason, count := range metrics.FailureReasons {
			combinedFailureReasons[reason] += count
		}
	}
	
	// Sort failure reasons by frequency
	type reasonCount struct {
		reason string
		count  int64
	}
	
	var reasonList []reasonCount
	for reason, count := range combinedFailureReasons {
		reasonList = append(reasonList, reasonCount{reason, count})
	}
	
	sort.Slice(reasonList, func(i, j int) bool {
		return reasonList[i].count > reasonList[j].count
	})
	
	for i, rc := range reasonList {
		if i >= 5 { // Top 5 reasons
			break
		}
		percentage := float64(rc.count) / float64(totalTxns-totalSuccessful) * 100
		report.WriteString(fmt.Sprintf("%d. %s: %d occurrences (%.1f%% of failures)\n", 
			i+1, rc.reason, rc.count, percentage))
	}
	
	// Mumbai insights and recommendations
	report.WriteString("\n\n🏙️ MUMBAI-STYLE INSIGHTS & RECOMMENDATIONS\n")
	report.WriteString(strings.Repeat("-", 40) + "\n")
	
	bestProvider := providerList[0].provider
	worstProvider := providerList[len(providerList)-1].provider
	
	report.WriteString(fmt.Sprintf("🏆 Most Reliable (like Mumbai locals): %s (%.2f%% success)\n", 
		bestProvider, providerList[0].metrics.SuccessRate*100))
	report.WriteString(fmt.Sprintf("⚠️ Needs Improvement (like Mumbai traffic): %s (%.2f%% success)\n\n", 
		worstProvider, providerList[len(providerList)-1].metrics.SuccessRate*100))
	
	report.WriteString("💡 ACTIONABLE RECOMMENDATIONS\n")
	report.WriteString(strings.Repeat("-", 40) + "\n")
	
	if overallMonsoon > 0 && (overallSuccessRate-overallMonsoon) > 0.03 {
		report.WriteString("🌧️ Monsoon Preparation:\n")
		report.WriteString("   • Increase server capacity during June-September\n")
		report.WriteString("   • Implement better network redundancy for rainy regions\n")
		report.WriteString("   • Set up monsoon-specific retry mechanisms\n\n")
	}
	
	if overallFestival > 0 && (overallSuccessRate-overallFestival) > 0.05 {
		report.WriteString("🎉 Festival Season Optimization:\n")
		report.WriteString("   • Auto-scaling for Diwali, Holi, and Ganesh Chaturthi\n")
		report.WriteString("   • Load balancing across multiple data centers\n")
		report.WriteString("   • Pre-emptive capacity planning for festival months\n\n")
	}
	
	if overallPeakHour > 0 && (overallSuccessRate-overallPeakHour) > 0.02 {
		report.WriteString("⏰ Peak Hour Management:\n")
		report.WriteString("   • Dynamic resource allocation during 9-11 AM and 6-9 PM\n")
		report.WriteString("   • Priority queues for critical transactions\n")
		report.WriteString("   • Real-time load monitoring and alerting\n\n")
	}
	
	report.WriteString("🎯 General Recommendations:\n")
	report.WriteString("   • Like Mumbai dabbawalas - consistency is key!\n")
	report.WriteString("   • Monitor success rates like Mumbai traffic updates\n")
	report.WriteString("   • Plan for worst-case scenarios (like Mumbai monsoon)\n")
	report.WriteString("   • Build redundancy like Mumbai's multiple train lines\n")
	
	report.WriteString("\n🚀 Happy UPI processing! May your transactions be faster than Mumbai locals!")
	
	return report.String()
}

// Main demonstration function
// Main demonstration function
func main() {
	fmt.Println("🚀 Starting UPI Failure Analysis Demo")
	fmt.Println(strings.Repeat("=", 60))
	
	// Create analyzer
	analyzer := NewUPIFailureAnalyzer()
	
	// Generate demo transactions
	analyzer.GenerateDemoTransactions(3000)
	
	// Generate and print comprehensive report
	fmt.Println("📋 GENERATING COMPREHENSIVE UPI FAILURE ANALYSIS REPORT...\n")
	report := analyzer.GenerateFailureAnalysisReport()
	fmt.Println(report)
	
	fmt.Println("\n🎉 UPI failure analysis completed!")
	fmt.Println("🏙️ Just like analyzing Mumbai traffic patterns - understanding failures helps prevent them!")
	fmt.Println("💡 Use these insights to improve UPI transaction success rates!")
}
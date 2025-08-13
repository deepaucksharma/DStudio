/**
 * Work-Life Balance Monitor - Episode 3: Human Factor in Tech
 * ===========================================================
 * 
 * Indian IT industry में work-life balance tracking
 * TCS, Infosys, Wipro जैसी companies के real scenarios के साथ
 * 
 * Features:
 * - Long working hours detection (Indian office culture)
 * - Festival time work analysis
 * - Family obligation conflict detection
 * - Regional pattern analysis (Mumbai traffic vs Bangalore)
 * - Burnout prediction with family context
 */

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"sort"
	"time"
)

// WorkDay represents एक engineer के working day का data
type WorkDay struct {
	Date        time.Time `json:"date"`
	StartTime   time.Time `json:"start_time"`
	EndTime     time.Time `json:"end_time"`
	BreakHours  float64   `json:"break_hours"`
	Location    string    `json:"location"` // Office, Home, Client site
	WeekendWork bool      `json:"weekend_work"`
	LateNight   bool      `json:"late_night"` // Work after 9 PM
	EarlyMorning bool     `json:"early_morning"` // Work before 8 AM
}

// FamilyObligation represents family commitments
type FamilyObligation struct {
	Type        string    `json:"type"`        // school_pickup, elderly_care, festival
	Time        time.Time `json:"time"`
	Duration    float64   `json:"duration"`    // in hours
	Priority    int       `json:"priority"`    // 1-5, 5 being highest
	Flexible    bool      `json:"flexible"`
	Description string    `json:"description"`
}

// Engineer profile with Indian context
type Engineer struct {
	ID               string              `json:"id"`
	Name             string              `json:"name"`
	Role             string              `json:"role"`
	City             string              `json:"city"` // Mumbai, Bangalore, Pune, etc.
	ExperienceYears  int                 `json:"experience_years"`
	MaritalStatus    string              `json:"marital_status"`
	HasChildren      bool                `json:"has_children"`
	ElderlyParents   bool                `json:"elderly_parents"`
	CommuteTime      float64             `json:"commute_time"` // hours per day
	WorkDays         []WorkDay           `json:"work_days"`
	FamilyObligations []FamilyObligation `json:"family_obligations"`
	PreferredWorkHours struct {
		Start time.Time `json:"start"`
		End   time.Time `json:"end"`
	} `json:"preferred_work_hours"`
}

// Regional patterns for different Indian cities
type RegionalPattern struct {
	City                string  `json:"city"`
	AverageCommuteTime  float64 `json:"average_commute_time"`
	MonsoonImpact       float64 `json:"monsoon_impact"` // 0-1, traffic increase
	CostOfLiving        float64 `json:"cost_of_living"` // relative to national average
	WorkCultureScore    float64 `json:"work_culture_score"` // 0-10, higher = more intense
	FamilyProximity     float64 `json:"family_proximity"` // 0-1, how close family lives
}

// Festival calendar for India
type Festival struct {
	Name        string    `json:"name"`
	Date        time.Time `json:"date"`
	Duration    int       `json:"duration"` // days
	Importance  int       `json:"importance"` // 1-5
	Region      string    `json:"region"` // All-India, North, South, West, East
	WorkImpact  float64   `json:"work_impact"` // 0-1, how much it affects work
}

// WorkLifeBalanceMonitor main system
type WorkLifeBalanceMonitor struct {
	Engineers        []Engineer         `json:"engineers"`
	RegionalPatterns []RegionalPattern  `json:"regional_patterns"`
	FestivalCalendar []Festival         `json:"festival_calendar"`
	AnalysisPeriod   struct {
		Start time.Time `json:"start"`
		End   time.Time `json:"end"`
	} `json:"analysis_period"`
}

// Initialize the monitoring system
func NewWorkLifeBalanceMonitor() *WorkLifeBalanceMonitor {
	monitor := &WorkLifeBalanceMonitor{
		Engineers:        []Engineer{},
		RegionalPatterns: getRegionalPatterns(),
		FestivalCalendar: getFestivalCalendar(),
	}
	
	// Set analysis period to last 30 days
	monitor.AnalysisPeriod.End = time.Now()
	monitor.AnalysisPeriod.Start = time.Now().AddDate(0, 0, -30)
	
	return monitor
}

// Get regional patterns for major Indian cities
func getRegionalPatterns() []RegionalPattern {
	return []RegionalPattern{
		{
			City:               "Mumbai",
			AverageCommuteTime: 2.5, // Hours per day due to local trains
			MonsoonImpact:      0.8, // Massive traffic during monsoon
			CostOfLiving:       1.4,
			WorkCultureScore:   8.5, // High pressure finance hub
			FamilyProximity:    0.3, // Many live away from family
		},
		{
			City:               "Bangalore",
			AverageCommuteTime: 2.0,
			MonsoonImpact:      0.4,
			CostOfLiving:       1.2,
			WorkCultureScore:   9.0, // Silicon Valley of India
			FamilyProximity:    0.4,
		},
		{
			City:               "Pune",
			AverageCommuteTime: 1.5,
			MonsoonImpact:      0.5,
			CostOfLiving:       1.1,
			WorkCultureScore:   7.5,
			FamilyProximity:    0.6, // Closer to home for many
		},
		{
			City:               "Hyderabad",
			AverageCommuteTime: 1.8,
			MonsoonImpact:      0.3,
			CostOfLiving:       1.0,
			WorkCultureScore:   7.0,
			FamilyProximity:    0.7,
		},
		{
			City:               "Delhi NCR",
			AverageCommuteTime: 2.2,
			MonsoonImpact:      0.6,
			CostOfLiving:       1.3,
			WorkCultureScore:   8.0,
			FamilyProximity:    0.5,
		},
	}
}

// Get Indian festival calendar
func getFestivalCalendar() []Festival {
	// Using 2024 dates as example
	festivals := []Festival{
		{"Makar Sankranti", time.Date(2024, 1, 14, 0, 0, 0, 0, time.UTC), 1, 4, "All-India", 0.6},
		{"Holi", time.Date(2024, 3, 8, 0, 0, 0, 0, time.UTC), 2, 5, "North", 0.8},
		{"Ram Navami", time.Date(2024, 4, 17, 0, 0, 0, 0, time.UTC), 1, 4, "All-India", 0.5},
		{"Eid ul-Fitr", time.Date(2024, 4, 21, 0, 0, 0, 0, time.UTC), 1, 5, "All-India", 0.7},
		{"Independence Day", time.Date(2024, 8, 15, 0, 0, 0, 0, time.UTC), 1, 5, "All-India", 0.3},
		{"Ganesh Chaturthi", time.Date(2024, 9, 7, 0, 0, 0, 0, time.UTC), 11, 5, "West", 0.9},
		{"Dussehra", time.Date(2024, 10, 12, 0, 0, 0, 0, time.UTC), 1, 5, "All-India", 0.8},
		{"Diwali", time.Date(2024, 11, 1, 0, 0, 0, 0, time.UTC), 5, 5, "All-India", 1.0},
		{"Christmas", time.Date(2024, 12, 25, 0, 0, 0, 0, time.UTC), 1, 4, "All-India", 0.4},
	}
	
	return festivals
}

// Add engineer to monitoring system
func (monitor *WorkLifeBalanceMonitor) AddEngineer(engineer Engineer) {
	monitor.Engineers = append(monitor.Engineers, engineer)
	fmt.Printf("✅ Added engineer: %s from %s\n", engineer.Name, engineer.City)
}

// Calculate work-life balance score for an engineer
func (monitor *WorkLifeBalanceMonitor) CalculateBalanceScore(engineerID string) float64 {
	engineer := monitor.findEngineer(engineerID)
	if engineer == nil {
		return 0.0
	}
	
	score := 10.0 // Start with perfect score
	
	// Analyze working hours pattern
	averageHours := monitor.calculateAverageWorkingHours(engineer)
	if averageHours > 9 {
		score -= float64(averageHours-9) * 0.5 // Penalty for long hours
	}
	
	// Weekend work penalty
	weekendWorkDays := monitor.countWeekendWorkDays(engineer)
	score -= float64(weekendWorkDays) * 0.3
	
	// Late night work penalty (Indian family dinner time context)
	lateNightDays := monitor.countLateNightWork(engineer)
	score -= float64(lateNightDays) * 0.4
	
	// Festival work penalty (very important in Indian context)
	festivalWorkDays := monitor.countFestivalWorkDays(engineer)
	score -= float64(festivalWorkDays) * 0.6
	
	// Family obligation conflicts
	conflicts := monitor.calculateFamilyConflicts(engineer)
	score -= float64(conflicts) * 0.5
	
	// Regional adjustment (Mumbai has worse work-life balance due to commute)
	regionalPattern := monitor.getRegionalPattern(engineer.City)
	if regionalPattern != nil {
		commuteImpact := regionalPattern.AverageCommuteTime * 0.2
		cultureImpact := (regionalPattern.WorkCultureScore - 7.0) * 0.1
		score -= commuteImpact + cultureImpact
	}
	
	// Family responsibility bonus/penalty
	if engineer.HasChildren && engineer.ElderlyParents {
		score -= 0.5 // More family responsibilities
	}
	
	// Ensure score stays within 0-10 range
	if score < 0 {
		score = 0
	}
	if score > 10 {
		score = 10
	}
	
	return score
}

func (monitor *WorkLifeBalanceMonitor) calculateAverageWorkingHours(engineer *Engineer) float64 {
	if len(engineer.WorkDays) == 0 {
		return 0
	}
	
	totalHours := 0.0
	for _, day := range engineer.WorkDays {
		hours := day.EndTime.Sub(day.StartTime).Hours() - day.BreakHours
		totalHours += hours
	}
	
	return totalHours / float64(len(engineer.WorkDays))
}

func (monitor *WorkLifeBalanceMonitor) countWeekendWorkDays(engineer *Engineer) int {
	count := 0
	for _, day := range engineer.WorkDays {
		if day.WeekendWork {
			count++
		}
	}
	return count
}

func (monitor *WorkLifeBalanceMonitor) countLateNightWork(engineer *Engineer) int {
	count := 0
	for _, day := range engineer.WorkDays {
		if day.LateNight {
			count++
		}
	}
	return count
}

func (monitor *WorkLifeBalanceMonitor) countFestivalWorkDays(engineer *Engineer) int {
	count := 0
	
	for _, day := range engineer.WorkDays {
		for _, festival := range monitor.FestivalCalendar {
			// Check if work day falls on or around festival
			if day.Date.Format("2006-01-02") == festival.Date.Format("2006-01-02") {
				if festival.WorkImpact > 0.5 { // Important festivals
					count++
				}
			}
		}
	}
	
	return count
}

func (monitor *WorkLifeBalanceMonitor) calculateFamilyConflicts(engineer *Engineer) int {
	conflicts := 0
	
	for _, workDay := range engineer.WorkDays {
		for _, obligation := range engineer.FamilyObligations {
			// Check if work hours overlap with family obligations
			if monitor.isTimeConflict(workDay, obligation) {
				conflicts++
			}
		}
	}
	
	return conflicts
}

func (monitor *WorkLifeBalanceMonitor) isTimeConflict(workDay WorkDay, obligation FamilyObligation) bool {
	// Simplified conflict detection
	workStart := workDay.StartTime.Hour()
	workEnd := workDay.EndTime.Hour()
	obligationHour := obligation.Time.Hour()
	
	return obligationHour >= workStart && obligationHour <= workEnd && !obligation.Flexible
}

func (monitor *WorkLifeBalanceMonitor) getRegionalPattern(city string) *RegionalPattern {
	for i, pattern := range monitor.RegionalPatterns {
		if pattern.City == city {
			return &monitor.RegionalPatterns[i]
		}
	}
	return nil
}

func (monitor *WorkLifeBalanceMonitor) findEngineer(engineerID string) *Engineer {
	for i, engineer := range monitor.Engineers {
		if engineer.ID == engineerID {
			return &monitor.Engineers[i]
		}
	}
	return nil
}

// Generate comprehensive report
func (monitor *WorkLifeBalanceMonitor) GenerateReport() {
	fmt.Println("\n⚖️ Work-Life Balance Analysis Report")
	fmt.Println("=====================================")
	fmt.Printf("Analysis Period: %s to %s\n", 
		monitor.AnalysisPeriod.Start.Format("2006-01-02"), 
		monitor.AnalysisPeriod.End.Format("2006-01-02"))
	fmt.Printf("Engineers Analyzed: %d\n\n", len(monitor.Engineers))
	
	// Individual engineer analysis
	for _, engineer := range monitor.Engineers {
		balance := monitor.CalculateBalanceScore(engineer.ID)
		
		fmt.Printf("👤 Engineer: %s (%s)\n", engineer.Name, engineer.City)
		fmt.Printf("   Role: %s | Experience: %d years\n", engineer.Role, engineer.ExperienceYears)
		fmt.Printf("   Balance Score: %.1f/10 %s\n", balance, monitor.getBalanceEmoji(balance))
		
		// Detailed metrics
		avgHours := monitor.calculateAverageWorkingHours(&engineer)
		weekendDays := monitor.countWeekendWorkDays(&engineer)
		lateNights := monitor.countLateNightWork(&engineer)
		festivalWork := monitor.countFestivalWorkDays(&engineer)
		familyConflicts := monitor.calculateFamilyConflicts(&engineer)
		
		fmt.Printf("   Avg Daily Hours: %.1f\n", avgHours)
		fmt.Printf("   Weekend Work Days: %d\n", weekendDays)
		fmt.Printf("   Late Night Work: %d days\n", lateNights)
		fmt.Printf("   Festival Work Days: %d\n", festivalWork)
		fmt.Printf("   Family Conflicts: %d\n", familyConflicts)
		
		// Regional context
		regional := monitor.getRegionalPattern(engineer.City)
		if regional != nil {
			fmt.Printf("   Commute Impact: %.1f hours/day\n", regional.AverageCommuteTime)
			fmt.Printf("   City Work Culture: %.1f/10\n", regional.WorkCultureScore)
		}
		
		// Recommendations
		monitor.generateRecommendations(engineer, balance)
		fmt.Println()
	}
	
	// Team-level analysis
	monitor.generateTeamAnalysis()
	
	// Regional comparison
	monitor.generateRegionalComparison()
	
	// Festival impact analysis
	monitor.generateFestivalImpactAnalysis()
}

func (monitor *WorkLifeBalanceMonitor) getBalanceEmoji(score float64) string {
	if score >= 8 {
		return "✅ Excellent"
	} else if score >= 6 {
		return "⚠️ Needs Attention"
	} else {
		return "🚨 Critical"
	}
}

func (monitor *WorkLifeBalanceMonitor) generateRecommendations(engineer Engineer, score float64) {
	fmt.Println("   📋 Recommendations:")
	
	avgHours := monitor.calculateAverageWorkingHours(&engineer)
	if avgHours > 10 {
		fmt.Println("      🕐 Reduce daily working hours - currently exceeding healthy limits")
	}
	
	weekendWork := monitor.countWeekendWorkDays(&engineer)
	if weekendWork > 4 {
		fmt.Println("      🏖️ Avoid weekend work - family time is important")
	}
	
	lateNights := monitor.countLateNightWork(&engineer)
	if lateNights > 10 {
		fmt.Println("      🌙 Reduce late night work - affects family dinner time")
	}
	
	festivalWork := monitor.countFestivalWorkDays(&engineer)
	if festivalWork > 0 {
		fmt.Println("      🎉 Respect festival time - cultural celebrations are important")
	}
	
	regional := monitor.getRegionalPattern(engineer.City)
	if regional != nil && regional.AverageCommuteTime > 2.0 {
		fmt.Println("      🏠 Consider remote work options to reduce commute stress")
	}
	
	if engineer.HasChildren && engineer.ElderlyParents {
		fmt.Println("      👨‍👩‍👧‍👦 Family support system needed - high caregiving responsibility")
	}
	
	if score < 6 {
		fmt.Println("      🚨 URGENT: Consider workload redistribution and manager discussion")
	}
}

func (monitor *WorkLifeBalanceMonitor) generateTeamAnalysis() {
	fmt.Println("📊 Team-Level Analysis")
	fmt.Println("======================")
	
	// Calculate team averages
	totalScore := 0.0
	totalHours := 0.0
	totalWeekendDays := 0
	criticalCases := 0
	
	for _, engineer := range monitor.Engineers {
		score := monitor.CalculateBalanceScore(engineer.ID)
		totalScore += score
		totalHours += monitor.calculateAverageWorkingHours(&engineer)
		totalWeekendDays += monitor.countWeekendWorkDays(&engineer)
		
		if score < 6 {
			criticalCases++
		}
	}
	
	teamCount := float64(len(monitor.Engineers))
	fmt.Printf("Team Average Balance Score: %.1f/10\n", totalScore/teamCount)
	fmt.Printf("Team Average Daily Hours: %.1f\n", totalHours/teamCount)
	fmt.Printf("Average Weekend Work Days: %.1f\n", float64(totalWeekendDays)/teamCount)
	fmt.Printf("Engineers Needing Attention: %d/%d (%.1f%%)\n", 
		criticalCases, len(monitor.Engineers), float64(criticalCases)/teamCount*100)
	
	// Risk assessment
	if float64(criticalCases)/teamCount > 0.3 {
		fmt.Println("🚨 TEAM RISK: High burnout risk detected - immediate intervention needed")
	} else if float64(criticalCases)/teamCount > 0.1 {
		fmt.Println("⚠️ TEAM WARNING: Some team members need work-life balance support")
	} else {
		fmt.Println("✅ TEAM HEALTH: Good overall work-life balance")
	}
	fmt.Println()
}

func (monitor *WorkLifeBalanceMonitor) generateRegionalComparison() {
	fmt.Println("🗺️ Regional Analysis")
	fmt.Println("===================")
	
	cityScores := make(map[string][]float64)
	
	// Group engineers by city and calculate scores
	for _, engineer := range monitor.Engineers {
		score := monitor.CalculateBalanceScore(engineer.ID)
		cityScores[engineer.City] = append(cityScores[engineer.City], score)
	}
	
	// Calculate city averages
	type CityAverage struct {
		City  string
		Avg   float64
		Count int
	}
	
	var cityAverages []CityAverage
	for city, scores := range cityScores {
		if len(scores) > 0 {
			sum := 0.0
			for _, score := range scores {
				sum += score
			}
			avg := sum / float64(len(scores))
			cityAverages = append(cityAverages, CityAverage{city, avg, len(scores)})
		}
	}
	
	// Sort by average score
	sort.Slice(cityAverages, func(i, j int) bool {
		return cityAverages[i].Avg > cityAverages[j].Avg
	})
	
	fmt.Println("City Rankings (Best to Worst Work-Life Balance):")
	for i, cityAvg := range cityAverages {
		regional := monitor.getRegionalPattern(cityAvg.City)
		fmt.Printf("%d. %s: %.1f/10 (%d engineers)", 
			i+1, cityAvg.City, cityAvg.Avg, cityAvg.Count)
		
		if regional != nil {
			fmt.Printf(" | Commute: %.1fh | Work Culture: %.1f/10", 
				regional.AverageCommuteTime, regional.WorkCultureScore)
		}
		fmt.Println()
	}
	
	fmt.Println()
}

func (monitor *WorkLifeBalanceMonitor) generateFestivalImpactAnalysis() {
	fmt.Println("🎉 Festival Impact Analysis")
	fmt.Println("===========================")
	
	festivalWorkCount := make(map[string]int)
	
	for _, engineer := range monitor.Engineers {
		for _, workDay := range engineer.WorkDays {
			for _, festival := range monitor.FestivalCalendar {
				if workDay.Date.Format("2006-01-02") == festival.Date.Format("2006-01-02") {
					festivalWorkCount[festival.Name]++
				}
			}
		}
	}
	
	fmt.Println("Engineers Working During Festivals:")
	for festival, count := range festivalWorkCount {
		if count > 0 {
			percentage := float64(count) / float64(len(monitor.Engineers)) * 100
			fmt.Printf("  %s: %d engineers (%.1f%%)", festival, count, percentage)
			
			if percentage > 30 {
				fmt.Print(" 🚨 HIGH")
			} else if percentage > 10 {
				fmt.Print(" ⚠️ MODERATE")
			} else {
				fmt.Print(" ✅ LOW")
			}
			fmt.Println()
		}
	}
	
	if len(festivalWorkCount) > 0 {
		fmt.Println("\n💡 Festival Recommendations:")
		fmt.Println("   • Implement festival leave policies")
		fmt.Println("   • Reduce non-critical work during major festivals")
		fmt.Println("   • Respect regional festival preferences")
		fmt.Println("   • Plan project timelines around festival calendar")
	}
}

// Demo function to show the system in action
func main() {
	fmt.Println("⚖️ Work-Life Balance Monitor Demo - Indian Context")
	fmt.Println("==================================================")
	
	monitor := NewWorkLifeBalanceMonitor()
	
	// Add sample engineers from different cities
	engineers := []Engineer{
		{
			ID:               "ENG001",
			Name:            "Rajesh Sharma",
			Role:            "Senior Developer",
			City:            "Mumbai",
			ExperienceYears: 8,
			MaritalStatus:   "Married",
			HasChildren:     true,
			ElderlyParents:  true,
			CommuteTime:     2.5,
			WorkDays:        generateSampleWorkDays(30, 10.5, true, true), // Long hours, weekend work
		},
		{
			ID:               "ENG002", 
			Name:            "Priya Nair",
			Role:            "Tech Lead",
			City:            "Bangalore",
			ExperienceYears: 6,
			MaritalStatus:   "Single",
			HasChildren:     false,
			ElderlyParents:  false,
			CommuteTime:     1.8,
			WorkDays:        generateSampleWorkDays(30, 9.2, false, false), // Better balance
		},
		{
			ID:               "ENG003",
			Name:            "Amit Patel", 
			Role:            "DevOps Engineer",
			City:            "Pune",
			ExperienceYears: 4,
			MaritalStatus:   "Married",
			HasChildren:     true,
			ElderlyParents:  false,
			CommuteTime:     1.2,
			WorkDays:        generateSampleWorkDays(30, 8.8, false, true), // Some late nights
		},
	}
	
	// Add family obligations
	engineers[0].FamilyObligations = []FamilyObligation{
		{"school_pickup", time.Date(2024, 1, 1, 16, 0, 0, 0, time.UTC), 1.0, 5, false, "Daily school pickup"},
		{"elderly_care", time.Date(2024, 1, 1, 18, 30, 0, 0, time.UTC), 2.0, 4, true, "Evening elderly care"},
	}
	
	engineers[2].FamilyObligations = []FamilyObligation{
		{"school_pickup", time.Date(2024, 1, 1, 15, 45, 0, 0, time.UTC), 1.0, 5, false, "School pickup"},
	}
	
	// Add engineers to monitor
	for _, engineer := range engineers {
		monitor.AddEngineer(engineer)
	}
	
	// Generate comprehensive report
	monitor.GenerateReport()
	
	// JSON export for integration with other systems
	jsonData, err := json.MarshalIndent(monitor, "", "  ")
	if err != nil {
		log.Printf("Error marshaling to JSON: %v", err)
	} else {
		fmt.Println("\n💾 JSON Export Preview (first 500 chars):")
		fmt.Println("==========================================")
		if len(jsonData) > 500 {
			fmt.Printf("%s...\n", string(jsonData[:500]))
		} else {
			fmt.Println(string(jsonData))
		}
	}
	
	fmt.Println("\n✅ Work-Life Balance Analysis Complete!")
	fmt.Println("📊 Use this data to improve team wellbeing and productivity")
}

// Helper function to generate sample work days
func generateSampleWorkDays(days int, avgHours float64, weekendWork bool, lateNight bool) []WorkDay {
	var workDays []WorkDay
	
	baseDate := time.Now().AddDate(0, 0, -days)
	
	for i := 0; i < days; i++ {
		date := baseDate.AddDate(0, 0, i)
		
		// Skip some Sundays unless weekendWork is true
		if date.Weekday() == time.Sunday && !weekendWork && rand.Float64() > 0.3 {
			continue
		}
		
		// Start time varies
		startHour := 9 + rand.Intn(2) // 9-10 AM start
		startTime := time.Date(date.Year(), date.Month(), date.Day(), startHour, 0, 0, 0, time.UTC)
		
		// Calculate end time based on average hours
		hoursVariation := avgHours + (rand.Float64()-0.5)*2 // ±1 hour variation
		endTime := startTime.Add(time.Duration(hoursVariation * float64(time.Hour)))
		
		isWeekend := date.Weekday() == time.Saturday || date.Weekday() == time.Sunday
		isLateNight := lateNight && (endTime.Hour() > 21 || rand.Float64() > 0.7)
		
		workDay := WorkDay{
			Date:         date,
			StartTime:    startTime,
			EndTime:      endTime,
			BreakHours:   1.0, // Standard lunch break
			Location:     "Office",
			WeekendWork:  isWeekend,
			LateNight:    isLateNight,
			EarlyMorning: startHour < 8,
		}
		
		workDays = append(workDays, workDay)
	}
	
	return workDays
}
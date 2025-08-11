/*
Work-Life Balance Monitor - Episode 3: Human Factor in Tech
==========================================================

Indian workplace mein work-life balance monitor karna - extended family aur festival obligations
ke saath. Mumbai local train ki timing ki tarah, work hours bhi predictable hone chahiye.

Features:
- Extended family obligation tracking
- Festival season workload adjustment
- Regional commute time consideration
- Multiple family role tracking (son/daughter, parent, spouse)
- Cultural event accommodation
- Flexible working arrangement scoring

Indian Context:
- Joint family considerations
- Festival responsibilities
- Regional commute challenges  
- Marriage/family event leaves
- Elder care obligations
- Cultural celebration participation
*/

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"sort"
	"time"
)

// WorkEvent represents a work-related activity
type WorkEvent struct {
	ID          string    `json:"id"`
	EmployeeID  string    `json:"employee_id"`
	EventType   EventType `json:"event_type"`
	StartTime   time.Time `json:"start_time"`
	EndTime     time.Time `json:"end_time"`
	Description string    `json:"description"`
	Location    string    `json:"location"` // "office", "home", "client_site"
	IsEmergency bool      `json:"is_emergency"`
}

// EventType represents different types of work activities
type EventType string

const (
	RegularWork    EventType = "regular_work"
	Meeting        EventType = "meeting"
	OnCallDuty     EventType = "oncall_duty" 
	EmergencyWork  EventType = "emergency_work"
	Travel         EventType = "travel"
	Training       EventType = "training"
	CodeReview     EventType = "code_review"
	ClientCall     EventType = "client_call"
)

// FamilyObligation represents family responsibilities
type FamilyObligation struct {
	Type        FamilyObligationType `json:"type"`
	Description string               `json:"description"`
	Priority    Priority             `json:"priority"`
	Frequency   string               `json:"frequency"` // "daily", "weekly", "monthly", "yearly"
	TimeSlots   []TimeSlot           `json:"time_slots"`
	Duration    time.Duration        `json:"duration"`
}

type FamilyObligationType string

const (
	ElderCare        FamilyObligationType = "elder_care"
	ChildCare        FamilyObligationType = "child_care"
	SchoolEvents     FamilyObligationType = "school_events"
	FamilyFunctions  FamilyObligationType = "family_functions"
	ReligiousDuties  FamilyObligationType = "religious_duties"
	FestivalPrep     FamilyObligationType = "festival_preparation"
	MarriageCeremony FamilyObligationType = "marriage_ceremony"
	MedicalCare      FamilyObligationType = "medical_care"
)

type Priority string

const (
	Low      Priority = "low"
	Medium   Priority = "medium"
	High     Priority = "high"
	Critical Priority = "critical"
)

// TimeSlot represents a time period
type TimeSlot struct {
	StartHour int `json:"start_hour"`
	EndHour   int `json:"end_hour"`
	Days      []time.Weekday `json:"days"`
}

// Employee with Indian context considerations
type Employee struct {
	ID                string              `json:"id"`
	Name              string              `json:"name"`
	Email             string              `json:"email"`
	Role              string              `json:"role"`
	Team              string              `json:"team"`
	Location          EmployeeLocation    `json:"location"`
	FamilyStatus      FamilyStatus        `json:"family_status"`
	FamilyObligations []FamilyObligation  `json:"family_obligations"`
	CommuteInfo       CommuteInfo         `json:"commute_info"`
	PreferredHours    TimeSlot            `json:"preferred_hours"`
	CulturalContext   CulturalContext     `json:"cultural_context"`
	WorkPreferences   WorkPreferences     `json:"work_preferences"`
	
	// Balance tracking
	WorkEvents        []WorkEvent         `json:"work_events"`
	BurnoutRisk       float64             `json:"burnout_risk"`
	BalanceScore      float64             `json:"balance_score"`
	LastAssessment    time.Time           `json:"last_assessment"`
}

type EmployeeLocation struct {
	City      string  `json:"city"`
	State     string  `json:"state"`
	IsMetro   bool    `json:"is_metro"`
	Timezone  string  `json:"timezone"`
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
}

type FamilyStatus struct {
	MaritalStatus    string `json:"marital_status"`
	HasChildren      bool   `json:"has_children"`
	ChildrenAges     []int  `json:"children_ages"`
	LivesWithParents bool   `json:"lives_with_parents"`
	PrimaryCaregiver bool   `json:"primary_caregiver"`
	SpouseWorking    bool   `json:"spouse_working"`
}

type CommuteInfo struct {
	Mode             string        `json:"mode"` // "local_train", "bus", "car", "bike", "walking"
	AverageTime      time.Duration `json:"average_time"`
	PeakTimeMultiplier float64     `json:"peak_time_multiplier"` // Mumbai local train factor
	WeatherImpact    float64       `json:"weather_impact"` // Monsoon factor
	CostPerDay       float64       `json:"cost_per_day"`
}

type CulturalContext struct {
	Religion             string   `json:"religion"`
	RegionalFestivals    []string `json:"regional_festivals"`
	LanguagePreference   string   `json:"language_preference"`
	FamilyTraditions     []string `json:"family_traditions"`
	CommunityObligations []string `json:"community_obligations"`
}

type WorkPreferences struct {
	PreferredWorkLocation string    `json:"preferred_work_location"` // "office", "home", "hybrid"
	FlexibleHours         bool      `json:"flexible_hours"`
	RemoteWorkDays        []time.Weekday `json:"remote_work_days"`
	QuietHours            TimeSlot  `json:"quiet_hours"` // No meetings/calls
	EnergyPeakHours       TimeSlot  `json:"energy_peak_hours"`
}

// BalanceMetrics represents work-life balance measurements
type BalanceMetrics struct {
	EmployeeID           string            `json:"employee_id"`
	AssessmentDate       time.Time         `json:"assessment_date"`
	
	// Time metrics
	WeeklyWorkHours      float64           `json:"weekly_work_hours"`
	OverTimeHours        float64           `json:"overtime_hours"`
	WeekendWorkHours     float64           `json:"weekend_work_hours"`
	EveningWorkHours     float64           `json:"evening_work_hours"`
	
	// Family metrics
	FamilyTimeHours      float64           `json:"family_time_hours"`
	FamilyObligationsMet float64           `json:"family_obligations_met"` // percentage
	FestivalParticipation float64          `json:"festival_participation"` // percentage
	
	// Well-being indicators
	CommuteStressScore   float64           `json:"commute_stress_score"`
	WorkloadPressure     float64           `json:"workload_pressure"`
	FlexibilityUtilized  float64           `json:"flexibility_utilized"`
	
	// Balance scoring
	OverallBalanceScore  float64           `json:"overall_balance_score"`
	BurnoutRiskLevel     string            `json:"burnout_risk_level"`
	Recommendations      []string          `json:"recommendations"`
	
	// Cultural considerations
	CulturalSupportScore float64           `json:"cultural_support_score"`
	FamilyAccommodation  float64           `json:"family_accommodation"`
}

// WorkLifeBalanceMonitor main system
type WorkLifeBalanceMonitor struct {
	employees     map[string]*Employee
	assessments   map[string][]BalanceMetrics
	
	// Indian holiday calendar
	festivals     map[string]time.Time
	regionalDays  map[string][]time.Time
	
	// Scoring weights for Indian context
	scoringWeights ScoringWeights
}

type ScoringWeights struct {
	WorkHours        float64 `json:"work_hours"`
	FamilyTime       float64 `json:"family_time"`
	CommuteStress    float64 `json:"commute_stress"`
	CulturalSupport  float64 `json:"cultural_support"`
	Flexibility      float64 `json:"flexibility"`
	FamilyObligations float64 `json:"family_obligations"`
}

// NewWorkLifeBalanceMonitor creates a new monitor instance
func NewWorkLifeBalanceMonitor() *WorkLifeBalanceMonitor {
	monitor := &WorkLifeBalanceMonitor{
		employees:   make(map[string]*Employee),
		assessments: make(map[string][]BalanceMetrics),
		festivals:   make(map[string]time.Time),
		regionalDays: make(map[string][]time.Time),
		scoringWeights: ScoringWeights{
			WorkHours:         0.25,
			FamilyTime:        0.20,
			CommuteStress:     0.15,
			CulturalSupport:   0.15, // Important in Indian context
			Flexibility:       0.15,
			FamilyObligations: 0.10, // Extended family considerations
		},
	}
	
	monitor.loadIndianFestivals()
	return monitor
}

// loadIndianFestivals loads major Indian festivals for 2024
func (wlm *WorkLifeBalanceMonitor) loadIndianFestivals() {
	// Sample 2024 festivals - in production, this would be from a proper calendar API
	wlm.festivals = map[string]time.Time{
		"Holi":           time.Date(2024, 3, 25, 0, 0, 0, 0, time.UTC),
		"Ram Navami":     time.Date(2024, 4, 17, 0, 0, 0, 0, time.UTC),
		"Eid ul-Fitr":    time.Date(2024, 4, 11, 0, 0, 0, 0, time.UTC),
		"Independence Day": time.Date(2024, 8, 15, 0, 0, 0, 0, time.UTC),
		"Janmashtami":    time.Date(2024, 8, 26, 0, 0, 0, 0, time.UTC),
		"Ganesh Chaturthi": time.Date(2024, 9, 7, 0, 0, 0, 0, time.UTC),
		"Dussehra":       time.Date(2024, 10, 12, 0, 0, 0, 0, time.UTC),
		"Diwali":         time.Date(2024, 11, 1, 0, 0, 0, 0, time.UTC),
		"Christmas":      time.Date(2024, 12, 25, 0, 0, 0, 0, time.UTC),
	}
	
	fmt.Printf("🪔 Loaded %d major Indian festivals for work-life balance consideration\n", len(wlm.festivals))
}

// AddEmployee adds an employee to the monitoring system
func (wlm *WorkLifeBalanceMonitor) AddEmployee(employee *Employee) {
	wlm.employees[employee.ID] = employee
	wlm.assessments[employee.ID] = make([]BalanceMetrics, 0)
	
	fmt.Printf("👤 Added employee %s (%s) to work-life balance monitoring\n", 
		employee.Name, employee.Location.City)
	
	// Special considerations for different family situations
	if employee.FamilyStatus.LivesWithParents {
		fmt.Printf("   🏠 Lives with parents - extended family obligations considered\n")
	}
	if employee.FamilyStatus.HasChildren {
		fmt.Printf("   👶 Has children - childcare obligations factored in\n")
	}
	if len(employee.FamilyObligations) > 0 {
		fmt.Printf("   👨‍👩‍👧‍👦 %d family obligations tracked\n", len(employee.FamilyObligations))
	}
}

// RecordWorkEvent records a work activity for an employee
func (wlm *WorkLifeBalanceMonitor) RecordWorkEvent(event WorkEvent) {
	employee, exists := wlm.employees[event.EmployeeID]
	if !exists {
		log.Printf("❌ Employee %s not found", event.EmployeeID)
		return
	}
	
	employee.WorkEvents = append(employee.WorkEvents, event)
	
	// Check for after-hours work
	if wlm.isAfterHours(event, employee) {
		fmt.Printf("⏰ After-hours work detected for %s: %s\n", 
			employee.Name, event.Description)
	}
	
	// Check for weekend work
	if wlm.isWeekendWork(event) {
		fmt.Printf("📅 Weekend work detected for %s: %s\n", 
			employee.Name, event.Description)
	}
	
	// Check for commute impact
	if event.Location == "office" && wlm.isHighCommuteStress(employee) {
		fmt.Printf("🚂 High commute stress day for %s (Mumbai local train factor)\n", 
			employee.Name)
	}
}

// isAfterHours checks if work event is outside preferred hours
func (wlm *WorkLifeBalanceMonitor) isAfterHours(event WorkEvent, employee *Employee) bool {
	hour := event.StartTime.Hour()
	return hour < employee.PreferredHours.StartHour || hour > employee.PreferredHours.EndHour
}

// isWeekendWork checks if work event is on weekend
func (wlm *WorkLifeBalanceMonitor) isWeekendWork(event WorkEvent) bool {
	weekday := event.StartTime.Weekday()
	return weekday == time.Saturday || weekday == time.Sunday
}

// isHighCommuteStress determines if commute stress is high on given day
func (wlm *WorkLifeBalanceMonitor) isHighCommuteStress(employee *Employee) bool {
	// Simulate high stress based on Mumbai local train conditions
	if employee.CommuteInfo.Mode == "local_train" {
		// Monsoon season impact
		month := time.Now().Month()
		if month >= 6 && month <= 9 { // Monsoon months
			return employee.CommuteInfo.WeatherImpact > 0.5
		}
		// Peak hour travel
		return employee.CommuteInfo.PeakTimeMultiplier > 1.5
	}
	return false
}

// CalculateBalanceMetrics calculates comprehensive work-life balance metrics
func (wlm *WorkLifeBalanceMonitor) CalculateBalanceMetrics(employeeID string, 
	startDate, endDate time.Time) (*BalanceMetrics, error) {
	
	employee, exists := wlm.employees[employeeID]
	if !exists {
		return nil, fmt.Errorf("employee %s not found", employeeID)
	}
	
	// Filter work events for the time period
	events := wlm.filterEventsByDateRange(employee.WorkEvents, startDate, endDate)
	
	metrics := &BalanceMetrics{
		EmployeeID:     employeeID,
		AssessmentDate: time.Now(),
	}
	
	// Calculate time-based metrics
	metrics.WeeklyWorkHours = wlm.calculateWeeklyWorkHours(events)
	metrics.OverTimeHours = math.Max(0, metrics.WeeklyWorkHours-40) // Standard 40-hour week
	metrics.WeekendWorkHours = wlm.calculateWeekendWorkHours(events)
	metrics.EveningWorkHours = wlm.calculateEveningWorkHours(events, employee)
	
	// Calculate family and cultural metrics
	metrics.FamilyTimeHours = wlm.estimateFamilyTime(employee, metrics.WeeklyWorkHours)
	metrics.FamilyObligationsMet = wlm.calculateFamilyObligationFulfillment(employee, events)
	metrics.FestivalParticipation = wlm.calculateFestivalParticipation(employee, startDate, endDate)
	
	// Calculate stress and well-being indicators
	metrics.CommuteStressScore = wlm.calculateCommuteStress(employee, events)
	metrics.WorkloadPressure = wlm.calculateWorkloadPressure(events, employee)
	metrics.FlexibilityUtilized = wlm.calculateFlexibilityUtilization(employee, events)
	
	// Cultural support scoring
	metrics.CulturalSupportScore = wlm.calculateCulturalSupport(employee)
	metrics.FamilyAccommodation = wlm.calculateFamilyAccommodation(employee)
	
	// Calculate overall balance score
	metrics.OverallBalanceScore = wlm.calculateOverallBalanceScore(metrics)
	metrics.BurnoutRiskLevel = wlm.assessBurnoutRisk(metrics)
	metrics.Recommendations = wlm.generateRecommendations(employee, metrics)
	
	// Store the assessment
	wlm.assessments[employeeID] = append(wlm.assessments[employeeID], *metrics)
	
	return metrics, nil
}

// filterEventsByDateRange filters work events by date range
func (wlm *WorkLifeBalanceMonitor) filterEventsByDateRange(events []WorkEvent, 
	start, end time.Time) []WorkEvent {
	var filtered []WorkEvent
	for _, event := range events {
		if event.StartTime.After(start) && event.StartTime.Before(end) {
			filtered = append(filtered, event)
		}
	}
	return filtered
}

// calculateWeeklyWorkHours calculates average weekly work hours
func (wlm *WorkLifeBalanceMonitor) calculateWeeklyWorkHours(events []WorkEvent) float64 {
	if len(events) == 0 {
		return 0
	}
	
	totalHours := 0.0
	for _, event := range events {
		if event.EventType == RegularWork || event.EventType == Meeting || 
		   event.EventType == CodeReview || event.EventType == ClientCall {
			duration := event.EndTime.Sub(event.StartTime).Hours()
			totalHours += duration
		}
	}
	
	// Calculate weeks in the period
	if len(events) > 0 {
		timeSpan := events[len(events)-1].StartTime.Sub(events[0].StartTime)
		weeks := timeSpan.Hours() / (24 * 7)
		if weeks > 0 {
			return totalHours / weeks
		}
	}
	
	return totalHours
}

// calculateWeekendWorkHours calculates weekend work hours
func (wlm *WorkLifeBalanceMonitor) calculateWeekendWorkHours(events []WorkEvent) float64 {
	weekendHours := 0.0
	for _, event := range events {
		if wlm.isWeekendWork(event) {
			duration := event.EndTime.Sub(event.StartTime).Hours()
			weekendHours += duration
		}
	}
	return weekendHours
}

// calculateEveningWorkHours calculates after-hours work
func (wlm *WorkLifeBalanceMonitor) calculateEveningWorkHours(events []WorkEvent, 
	employee *Employee) float64 {
	eveningHours := 0.0
	for _, event := range events {
		if wlm.isAfterHours(event, employee) {
			duration := event.EndTime.Sub(event.StartTime).Hours()
			eveningHours += duration
		}
	}
	return eveningHours
}

// estimateFamilyTime estimates available family time
func (wlm *WorkLifeBalanceMonitor) estimateFamilyTime(employee *Employee, 
	workHours float64) float64 {
	
	// Base calculation: total waking hours - work hours - commute
	wakingHours := 16.0 * 7 // 16 hours awake per day, 7 days a week
	commuteHours := employee.CommuteInfo.AverageTime.Hours() * 5 // 5 working days
	
	// Adjust for peak time multiplier (Mumbai local train delays)
	commuteHours *= employee.CommuteInfo.PeakTimeMultiplier
	
	familyTime := wakingHours - workHours - commuteHours
	
	// Adjust for family obligations
	obligationHours := 0.0
	for _, obligation := range employee.FamilyObligations {
		obligationHours += obligation.Duration.Hours()
	}
	
	return math.Max(0, familyTime-obligationHours)
}

// calculateFamilyObligationFulfillment calculates how well family obligations are met
func (wlm *WorkLifeBalanceMonitor) calculateFamilyObligationFulfillment(
	employee *Employee, events []WorkEvent) float64 {
	
	if len(employee.FamilyObligations) == 0 {
		return 1.0 // No obligations to fulfill
	}
	
	// Check work event conflicts with family obligations
	conflicts := 0.0
	totalObligations := float64(len(employee.FamilyObligations))
	
	for _, obligation := range employee.FamilyObligations {
		hasConflict := wlm.checkObligationConflict(obligation, events)
		if hasConflict {
			conflicts += 1.0
		}
	}
	
	fulfillmentRate := (totalObligations - conflicts) / totalObligations
	return math.Max(0, fulfillmentRate)
}

// checkObligationConflict checks if work events conflict with family obligations
func (wlm *WorkLifeBalanceMonitor) checkObligationConflict(obligation FamilyObligation, 
	events []WorkEvent) bool {
	
	for _, event := range events {
		for _, timeSlot := range obligation.TimeSlots {
			eventHour := event.StartTime.Hour()
			eventDay := event.StartTime.Weekday()
			
			// Check if event time overlaps with obligation time
			if eventHour >= timeSlot.StartHour && eventHour <= timeSlot.EndHour {
				for _, day := range timeSlot.Days {
					if day == eventDay {
						return true // Conflict found
					}
				}
			}
		}
	}
	return false
}

// calculateFestivalParticipation calculates festival participation rate
func (wlm *WorkLifeBalanceMonitor) calculateFestivalParticipation(employee *Employee, 
	startDate, endDate time.Time) float64 {
	
	festivalsInPeriod := 0.0
	participatedFestivals := 0.0
	
	for festivalName, festivalDate := range wlm.festivals {
		if festivalDate.After(startDate) && festivalDate.Before(endDate) {
			festivalsInPeriod += 1.0
			
			// Check if employee worked during festival (indicates non-participation)
			worked := wlm.workedOnDate(employee, festivalDate)
			if !worked {
				participatedFestivals += 1.0
			}
		}
	}
	
	if festivalsInPeriod == 0 {
		return 1.0 // No festivals in period
	}
	
	return participatedFestivals / festivalsInPeriod
}

// workedOnDate checks if employee worked on a specific date
func (wlm *WorkLifeBalanceMonitor) workedOnDate(employee *Employee, date time.Time) bool {
	for _, event := range employee.WorkEvents {
		eventDate := event.StartTime.Truncate(24 * time.Hour)
		checkDate := date.Truncate(24 * time.Hour)
		if eventDate.Equal(checkDate) {
			return true
		}
	}
	return false
}

// calculateCommuteStress calculates commute-related stress
func (wlm *WorkLifeBalanceMonitor) calculateCommuteStress(employee *Employee, 
	events []WorkEvent) float64 {
	
	officeEvents := 0.0
	totalEvents := float64(len(events))
	
	if totalEvents == 0 {
		return 0.0
	}
	
	for _, event := range events {
		if event.Location == "office" {
			officeEvents += 1.0
		}
	}
	
	officeRatio := officeEvents / totalEvents
	
	// Calculate stress based on commute factors
	baseStress := employee.CommuteInfo.AverageTime.Hours() / 3.0 // 3 hours = max stress
	peakMultiplier := employee.CommuteInfo.PeakTimeMultiplier
	weatherImpact := employee.CommuteInfo.WeatherImpact
	
	stressScore := baseStress * peakMultiplier * (1 + weatherImpact) * officeRatio
	
	return math.Min(1.0, stressScore)
}

// calculateWorkloadPressure calculates workload pressure
func (wlm *WorkLifeBalanceMonitor) calculateWorkloadPressure(events []WorkEvent, 
	employee *Employee) float64 {
	
	emergencyEvents := 0.0
	totalEvents := float64(len(events))
	
	if totalEvents == 0 {
		return 0.0
	}
	
	for _, event := range events {
		if event.IsEmergency || event.EventType == EmergencyWork {
			emergencyEvents += 1.0
		}
	}
	
	emergencyRatio := emergencyEvents / totalEvents
	
	// Factor in on-call duty frequency
	onCallEvents := 0.0
	for _, event := range events {
		if event.EventType == OnCallDuty {
			onCallEvents += 1.0
		}
	}
	
	onCallRatio := onCallEvents / totalEvents
	
	pressure := (emergencyRatio * 0.7) + (onCallRatio * 0.3)
	return math.Min(1.0, pressure)
}

// calculateFlexibilityUtilization calculates how much flexibility is utilized
func (wlm *WorkLifeBalanceMonitor) calculateFlexibilityUtilization(employee *Employee, 
	events []WorkEvent) float64 {
	
	if !employee.WorkPreferences.FlexibleHours {
		return 0.0 // No flexibility available
	}
	
	flexibleEvents := 0.0
	totalEvents := float64(len(events))
	
	if totalEvents == 0 {
		return 0.0
	}
	
	for _, event := range events {
		// Check if work is done at home or during flexible hours
		if event.Location == "home" {
			flexibleEvents += 0.5 // Remote work counts as flexibility
		}
		
		// Check if work is during non-standard hours by choice
		hour := event.StartTime.Hour()
		if hour < 9 || hour > 17 { // Outside standard hours
			flexibleEvents += 0.3
		}
	}
	
	utilization := flexibleEvents / totalEvents
	return math.Min(1.0, utilization)
}

// calculateCulturalSupport calculates cultural support provided by workplace
func (wlm *WorkLifeBalanceMonitor) calculateCulturalSupport(employee *Employee) float64 {
	score := 0.0
	
	// Festival accommodation
	if len(employee.CulturalContext.RegionalFestivals) > 0 {
		score += 0.3
	}
	
	// Language accommodation
	if employee.CulturalContext.LanguagePreference != "English" {
		score += 0.2 // Assuming workplace supports regional languages
	}
	
	// Community obligations consideration
	if len(employee.CulturalContext.CommunityObligations) > 0 {
		score += 0.2
	}
	
	// Family tradition accommodation
	if len(employee.CulturalContext.FamilyTraditions) > 0 {
		score += 0.3
	}
	
	return math.Min(1.0, score)
}

// calculateFamilyAccommodation calculates family accommodation score
func (wlm *WorkLifeBalanceMonitor) calculateFamilyAccommodation(employee *Employee) float64 {
	score := 0.0
	
	// Childcare accommodation
	if employee.FamilyStatus.HasChildren {
		score += 0.3
	}
	
	// Elder care accommodation
	if employee.FamilyStatus.LivesWithParents {
		score += 0.2
	}
	
	// Extended family accommodation
	if len(employee.FamilyObligations) > 0 {
		score += 0.3
	}
	
	// Spouse working consideration
	if employee.FamilyStatus.SpouseWorking {
		score += 0.2
	}
	
	return math.Min(1.0, score)
}

// calculateOverallBalanceScore calculates weighted overall balance score
func (wlm *WorkLifeBalanceMonitor) calculateOverallBalanceScore(metrics *BalanceMetrics) float64 {
	weights := wlm.scoringWeights
	
	// Normalize work hours (40 hours = optimal, >50 = poor)
	workHoursScore := math.Max(0, 1-(metrics.WeeklyWorkHours-40)/20)
	
	// Family time score (higher is better)
	familyTimeScore := math.Min(1.0, metrics.FamilyTimeHours/35) // 35 hours = good family time
	
	// Commute stress (lower is better)
	commuteScore := 1.0 - metrics.CommuteStressScore
	
	// Cultural and family scores (higher is better)
	culturalScore := metrics.CulturalSupportScore
	familyScore := metrics.FamilyAccommodation
	
	// Flexibility score (higher is better)
	flexibilityScore := metrics.FlexibilityUtilized
	
	// Family obligations score (higher is better)
	obligationsScore := metrics.FamilyObligationsMet
	
	overallScore := (workHoursScore * weights.WorkHours) +
		(familyTimeScore * weights.FamilyTime) +
		(commuteScore * weights.CommuteStress) +
		(culturalScore * weights.CulturalSupport) +
		(flexibilityScore * weights.Flexibility) +
		(obligationsScore * weights.FamilyObligations)
	
	return math.Min(1.0, overallScore)
}

// assessBurnoutRisk assesses burnout risk level
func (wlm *WorkLifeBalanceMonitor) assessBurnoutRisk(metrics *BalanceMetrics) string {
	riskFactors := 0
	
	if metrics.WeeklyWorkHours > 50 {
		riskFactors++
	}
	if metrics.WeekendWorkHours > 8 {
		riskFactors++
	}
	if metrics.CommuteStressScore > 0.7 {
		riskFactors++
	}
	if metrics.FamilyObligationsMet < 0.5 {
		riskFactors++
	}
	if metrics.WorkloadPressure > 0.6 {
		riskFactors++
	}
	
	switch riskFactors {
	case 0, 1:
		return "Low Risk"
	case 2, 3:
		return "Medium Risk"
	case 4, 5:
		return "High Risk"
	default:
		return "Critical Risk"
	}
}

// generateRecommendations generates personalized recommendations
func (wlm *WorkLifeBalanceMonitor) generateRecommendations(employee *Employee, 
	metrics *BalanceMetrics) []string {
	
	var recommendations []string
	
	// Work hours recommendations
	if metrics.WeeklyWorkHours > 50 {
		recommendations = append(recommendations, 
			"🕐 Consider reducing weekly work hours - current: %.1f hours (target: 40-45 hours)")
	}
	
	// Commute stress recommendations
	if metrics.CommuteStressScore > 0.6 {
		if employee.WorkPreferences.PreferredWorkLocation != "home" {
			recommendations = append(recommendations,
				"🏠 Consider work-from-home options to reduce commute stress, especially during monsoon")
		}
		recommendations = append(recommendations,
			"🚂 Explore flexible timing to avoid peak hours (Mumbai local train rush)")
	}
	
	// Family obligations recommendations
	if metrics.FamilyObligationsMet < 0.7 {
		recommendations = append(recommendations,
			"👨‍👩‍👧‍👦 Schedule work around family obligations - current fulfillment: %.1f%%")
		
		if employee.FamilyStatus.LivesWithParents {
			recommendations = append(recommendations,
				"🏠 Consider discussing elder care support options with manager")
		}
	}
	
	// Cultural participation recommendations
	if metrics.FestivalParticipation < 0.8 {
		recommendations = append(recommendations,
			"🪔 Take time off during festivals - cultural participation improves overall well-being")
	}
	
	// Flexibility recommendations
	if metrics.FlexibilityUtilized < 0.3 && employee.WorkPreferences.FlexibleHours {
		recommendations = append(recommendations,
			"⏰ Utilize available flexible work options to better balance personal and professional commitments")
	}
	
	// Weekend work recommendations
	if metrics.WeekendWorkHours > 5 {
		recommendations = append(recommendations,
			"📅 Limit weekend work - family time is crucial for long-term productivity")
	}
	
	return recommendations
}

// GetTeamBalanceReport generates team-wide balance report
func (wlm *WorkLifeBalanceMonitor) GetTeamBalanceReport(teamName string) map[string]interface{} {
	teamMembers := make([]*Employee, 0)
	
	// Find team members
	for _, employee := range wlm.employees {
		if employee.Team == teamName {
			teamMembers = append(teamMembers, employee)
		}
	}
	
	if len(teamMembers) == 0 {
		return map[string]interface{}{"error": "No team members found"}
	}
	
	// Calculate team statistics
	totalBalance := 0.0
	highRiskCount := 0
	averageWorkHours := 0.0
	
	for _, member := range teamMembers {
		assessments := wlm.assessments[member.ID]
		if len(assessments) > 0 {
			latest := assessments[len(assessments)-1]
			totalBalance += latest.OverallBalanceScore
			averageWorkHours += latest.WeeklyWorkHours
			
			if latest.BurnoutRiskLevel == "High Risk" || latest.BurnoutRiskLevel == "Critical Risk" {
				highRiskCount++
			}
		}
	}
	
	teamSize := float64(len(teamMembers))
	
	return map[string]interface{}{
		"team_name":            teamName,
		"team_size":            len(teamMembers),
		"average_balance_score": totalBalance / teamSize,
		"average_work_hours":   averageWorkHours / teamSize,
		"high_risk_members":    highRiskCount,
		"risk_percentage":      float64(highRiskCount) / teamSize * 100,
		"assessment_date":      time.Now().Format("2006-01-02"),
	}
}

// Demo function
func demoWorkLifeBalanceMonitor() {
	fmt.Println("⚖️ Work-Life Balance Monitor Demo - Indian Workplace Context")
	fmt.Println(strings.Repeat("=", 70))
	
	monitor := NewWorkLifeBalanceMonitor()
	
	// Create sample employees with diverse Indian contexts
	employees := []*Employee{
		{
			ID:    "EMP001",
			Name:  "Rajesh Kumar",
			Email: "rajesh@company.com",
			Role:  "Senior Software Engineer",
			Team:  "Backend Engineering",
			Location: EmployeeLocation{
				City:     "Mumbai",
				State:    "Maharashtra", 
				IsMetro:  true,
				Timezone: "Asia/Kolkata",
			},
			FamilyStatus: FamilyStatus{
				MaritalStatus:    "Married",
				HasChildren:      true,
				ChildrenAges:     []int{8, 12},
				LivesWithParents: true,
				PrimaryCaregiver: false,
				SpouseWorking:    true,
			},
			CommuteInfo: CommuteInfo{
				Mode:               "local_train",
				AverageTime:        90 * time.Minute, // 1.5 hours each way
				PeakTimeMultiplier: 1.8,              // Mumbai rush hour
				WeatherImpact:      0.7,              // Monsoon impact
				CostPerDay:         50.0,             // INR
			},
			PreferredHours: TimeSlot{
				StartHour: 9,
				EndHour:   18,
			},
			FamilyObligations: []FamilyObligation{
				{
					Type:        ElderCare,
					Description: "Evening time with parents",
					Priority:    High,
					Frequency:   "daily",
					Duration:    2 * time.Hour,
					TimeSlots: []TimeSlot{{
						StartHour: 19,
						EndHour:   21,
						Days: []time.Weekday{
							time.Monday, time.Tuesday, time.Wednesday, 
							time.Thursday, time.Friday,
						},
					}},
				},
				{
					Type:        SchoolEvents,
					Description: "Children's school activities",
					Priority:    High,
					Frequency:   "weekly",
					Duration:    3 * time.Hour,
				},
			},
			CulturalContext: CulturalContext{
				Religion:             "Hindu",
				RegionalFestivals:    []string{"Ganesh Chaturthi", "Navratri"},
				LanguagePreference:   "Hindi",
				FamilyTraditions:     []string{"Daily prayers", "Family dinner"},
				CommunityObligations: []string{"Society committee"},
			},
			WorkPreferences: WorkPreferences{
				PreferredWorkLocation: "hybrid",
				FlexibleHours:         true,
				RemoteWorkDays:        []time.Weekday{time.Tuesday, time.Thursday},
				QuietHours: TimeSlot{
					StartHour: 14,
					EndHour:   16,
				},
			},
		},
		
		{
			ID:    "EMP002",
			Name:  "Priya Menon",
			Email: "priya@company.com", 
			Role:  "Product Manager",
			Team:  "Product",
			Location: EmployeeLocation{
				City:     "Bangalore",
				State:    "Karnataka",
				IsMetro:  true,
				Timezone: "Asia/Kolkata",
			},
			FamilyStatus: FamilyStatus{
				MaritalStatus:    "Single",
				HasChildren:      false,
				LivesWithParents: false,
				PrimaryCaregiver: true, // Caring for elderly parents remotely
				SpouseWorking:    false,
			},
			CommuteInfo: CommuteInfo{
				Mode:               "car",
				AverageTime:        45 * time.Minute,
				PeakTimeMultiplier: 1.4,
				WeatherImpact:      0.2, // Less weather impact in Bangalore
				CostPerDay:         200.0,
			},
			PreferredHours: TimeSlot{
				StartHour: 10,
				EndHour:   19,
			},
			FamilyObligations: []FamilyObligation{
				{
					Type:        MedicalCare,
					Description: "Weekly calls with parents' doctors",
					Priority:    Critical,
					Frequency:   "weekly",
					Duration:    1 * time.Hour,
				},
			},
			CulturalContext: CulturalContext{
				Religion:             "Hindu",
				RegionalFestivals:    []string{"Onam", "Vishu"},
				LanguagePreference:   "Malayalam",
				FamilyTraditions:     []string{"Weekly family video calls"},
				CommunityObligations: []string{"Kerala cultural association"},
			},
			WorkPreferences: WorkPreferences{
				PreferredWorkLocation: "office",
				FlexibleHours:         true,
				RemoteWorkDays:        []time.Weekday{time.Friday},
			},
		},
	}
	
	// Add employees to monitor
	for _, emp := range employees {
		monitor.AddEmployee(emp)
	}
	
	fmt.Println("\n" + strings.Repeat("=", 50))
	
	// Simulate work events for Rajesh (showing work-life balance challenges)
	rajeshEvents := []WorkEvent{
		{
			ID:          "WE001",
			EmployeeID:  "EMP001",
			EventType:   RegularWork,
			StartTime:   time.Now().AddDate(0, 0, -5).Add(9 * time.Hour),
			EndTime:     time.Now().AddDate(0, 0, -5).Add(18 * time.Hour),
			Description: "Regular development work",
			Location:    "office",
		},
		{
			ID:          "WE002", 
			EmployeeID:  "EMP001",
			EventType:   EmergencyWork,
			StartTime:   time.Now().AddDate(0, 0, -3).Add(20 * time.Hour),
			EndTime:     time.Now().AddDate(0, 0, -3).Add(23 * time.Hour),
			Description: "Production incident response",
			Location:    "home",
			IsEmergency: true,
		},
		{
			ID:          "WE003",
			EmployeeID:  "EMP001",
			EventType:   Meeting,
			StartTime:   time.Now().AddDate(0, 0, -1).Add(19 * time.Hour),
			EndTime:     time.Now().AddDate(0, 0, -1).Add(20 * time.Hour),
			Description: "Client call with US team",
			Location:    "home",
		},
	}
	
	fmt.Println("📊 Recording work events...")
	for _, event := range rajeshEvents {
		monitor.RecordWorkEvent(event)
	}
	
	fmt.Println("\n" + strings.Repeat("=", 50))
	
	// Calculate balance metrics for Rajesh
	fmt.Println("⚖️ Calculating work-life balance metrics...")
	startDate := time.Now().AddDate(0, 0, -7)  // Last week
	endDate := time.Now()
	
	metrics, err := monitor.CalculateBalanceMetrics("EMP001", startDate, endDate)
	if err != nil {
		log.Printf("Error calculating metrics: %v", err)
		return
	}
	
	// Display results
	fmt.Printf("\n📋 Work-Life Balance Report for %s\n", employees[0].Name)
	fmt.Printf("Assessment Date: %s\n", metrics.AssessmentDate.Format("2006-01-02"))
	fmt.Printf("Overall Balance Score: %.2f/1.00\n", metrics.OverallBalanceScore)
	fmt.Printf("Burnout Risk Level: %s\n", metrics.BurnoutRiskLevel)
	
	fmt.Printf("\n⏰ Time Metrics:\n")
	fmt.Printf("   Weekly Work Hours: %.1f hours\n", metrics.WeeklyWorkHours)
	fmt.Printf("   Overtime Hours: %.1f hours\n", metrics.OverTimeHours)
	fmt.Printf("   Weekend Work: %.1f hours\n", metrics.WeekendWorkHours)
	fmt.Printf("   Evening Work: %.1f hours\n", metrics.EveningWorkHours)
	fmt.Printf("   Family Time: %.1f hours\n", metrics.FamilyTimeHours)
	
	fmt.Printf("\n👨‍👩‍👧‍👦 Family & Cultural Metrics:\n")
	fmt.Printf("   Family Obligations Met: %.1f%%\n", metrics.FamilyObligationsMet*100)
	fmt.Printf("   Festival Participation: %.1f%%\n", metrics.FestivalParticipation*100)
	fmt.Printf("   Cultural Support Score: %.2f/1.00\n", metrics.CulturalSupportScore)
	fmt.Printf("   Family Accommodation: %.2f/1.00\n", metrics.FamilyAccommodation)
	
	fmt.Printf("\n🚂 Stress & Well-being:\n")
	fmt.Printf("   Commute Stress Score: %.2f/1.00\n", metrics.CommuteStressScore)
	fmt.Printf("   Workload Pressure: %.2f/1.00\n", metrics.WorkloadPressure)
	fmt.Printf("   Flexibility Utilized: %.2f/1.00\n", metrics.FlexibilityUtilized)
	
	fmt.Printf("\n💡 Personalized Recommendations:\n")
	for i, rec := range metrics.Recommendations {
		fmt.Printf("   %d. %s\n", i+1, rec)
	}
	
	// Team balance report
	fmt.Printf("\n" + strings.Repeat("=", 50))
	fmt.Printf("\n👥 Team Balance Report:\n")
	teamReport := monitor.GetTeamBalanceReport("Backend Engineering")
	
	for key, value := range teamReport {
		switch key {
		case "average_balance_score":
			fmt.Printf("   Average Balance Score: %.2f/1.00\n", value)
		case "average_work_hours":
			fmt.Printf("   Average Work Hours: %.1f hours/week\n", value)
		case "high_risk_members":
			fmt.Printf("   High Risk Members: %v\n", value)
		case "risk_percentage":
			fmt.Printf("   Risk Percentage: %.1f%%\n", value)
		}
	}
}

func main() {
	demoWorkLifeBalanceMonitor()
}
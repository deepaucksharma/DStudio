/*
Diversity & Inclusion Dashboard - Episode 3: Human Factor in Tech
================================================================

Indian workplace mein diversity metrics aur inclusion score tracking.
Regional, linguistic, gender, aur educational background diversity ko measure karna.

Features:
- Multi-dimensional diversity tracking
- Inclusion sentiment analysis
- Pay gap identification
- Promotion pattern analysis  
- Cultural celebration participation
- Bias incident tracking
- Regional representation metrics
*/

package main

import (
	"encoding/json"
	"fmt"
	"math"
	"sort"
	"strings"
	"time"
)

// Employee represents an employee with diversity attributes
type Employee struct {
	ID                     string    `json:"id"`
	Name                   string    `json:"name"`
	Gender                 string    `json:"gender"`
	Age                    int       `json:"age"`
	Region                 string    `json:"region"`
	State                  string    `json:"state"`
	PrimaryLanguage        string    `json:"primary_language"`
	Religion               string    `json:"religion"`
	EducationBackground    string    `json:"education_background"`
	CollegeType            string    `json:"college_type"` // "IIT", "NIT", "Private", "Regional"
	SocioEconomicBackground string   `json:"socio_economic_background"`
	
	// Professional attributes
	Department       string    `json:"department"`
	Level           int       `json:"level"` // 1-7 hierarchy
	Salary          float64   `json:"salary"`
	JoiningDate     time.Time `json:"joining_date"`
	LastPromotion   time.Time `json:"last_promotion"`
	
	// Inclusion metrics
	InclusionScore        float64 `json:"inclusion_score"` // 0-100
	MentorshipOpportunities int    `json:"mentorship_opportunities"`
	LeadershipRoles       int     `json:"leadership_roles"`
	VisibilityScore       float64 `json:"visibility_score"` // 0-100
}

// DiversityMetrics represents comprehensive diversity analysis
type DiversityMetrics struct {
	TeamID                string                 `json:"team_id"`
	AnalysisDate         time.Time              `json:"analysis_date"`
	
	// Overall diversity scores (0-100)
	OverallDiversityScore float64               `json:"overall_diversity_score"`
	GenderDiversity       float64               `json:"gender_diversity"`
	RegionalDiversity     float64               `json:"regional_diversity"`
	LanguageDiversity     float64               `json:"language_diversity"`
	EducationDiversity    float64               `json:"education_diversity"`
	SocioEconomicDiversity float64              `json:"socio_economic_diversity"`
	
	// Representation analysis
	GenderDistribution    map[string]float64    `json:"gender_distribution"`
	RegionalDistribution  map[string]float64    `json:"regional_distribution"`
	LanguageDistribution  map[string]float64    `json:"language_distribution"`
	
	// Inclusion metrics
	AverageInclusionScore float64               `json:"average_inclusion_score"`
	PayGapAnalysis       PayGapAnalysis         `json:"pay_gap_analysis"`
	PromotionFairness    PromotionFairness      `json:"promotion_fairness"`
	
	// Improvement areas
	UnderrepresentedGroups []string             `json:"underrepresented_groups"`
	InclusionChallenges   []string              `json:"inclusion_challenges"`
	Recommendations       []string              `json:"recommendations"`
}

// PayGapAnalysis represents pay equity analysis
type PayGapAnalysis struct {
	GenderPayGap    map[string]float64 `json:"gender_pay_gap"` // % difference from baseline
	RegionalPayGap  map[string]float64 `json:"regional_pay_gap"`
	EducationPayGap map[string]float64 `json:"education_pay_gap"`
	OverallFairness float64            `json:"overall_fairness"` // 0-100
}

// PromotionFairness represents promotion pattern analysis
type PromotionFairness struct {
	GenderPromotionRate    map[string]float64 `json:"gender_promotion_rate"`
	RegionalPromotionRate  map[string]float64 `json:"regional_promotion_rate"`
	EducationPromotionRate map[string]float64 `json:"education_promotion_rate"`
	FairnessScore         float64            `json:"fairness_score"` // 0-100
}

// DiversityInclusionDashboard main system
type DiversityInclusionDashboard struct {
	employees []Employee
	metrics   []DiversityMetrics
}

// NewDiversityInclusionDashboard creates new dashboard instance
func NewDiversityInclusionDashboard() *DiversityInclusionDashboard {
	return &DiversityInclusionDashboard{
		employees: make([]Employee, 0),
		metrics:   make([]DiversityMetrics, 0),
	}
}

// AddEmployee adds employee to diversity tracking
func (d *DiversityInclusionDashboard) AddEmployee(employee Employee) {
	d.employees = append(d.employees, employee)
	fmt.Printf("👤 Added %s (%s, %s) to diversity tracking\n", 
		employee.Name, employee.Gender, employee.Region)
}

// CalculateDiversityIndex calculates Shannon diversity index for a group
func (d *DiversityInclusionDashboard) CalculateDiversityIndex(distribution map[string]int) float64 {
	total := 0
	for _, count := range distribution {
		total += count
	}
	
	if total <= 1 {
		return 0.0
	}
	
	diversity := 0.0
	for _, count := range distribution {
		if count > 0 {
			proportion := float64(count) / float64(total)
			diversity -= proportion * math.Log2(proportion)
		}
	}
	
	// Normalize to 0-100 scale (log2(n) is maximum diversity)
	maxDiversity := math.Log2(float64(len(distribution)))
	if maxDiversity > 0 {
		return (diversity / maxDiversity) * 100
	}
	
	return 0.0
}

// AnalyzeGenderDiversity analyzes gender representation
func (d *DiversityInclusionDashboard) AnalyzeGenderDiversity() (float64, map[string]float64) {
	genderCount := make(map[string]int)
	total := len(d.employees)
	
	for _, emp := range d.employees {
		genderCount[emp.Gender]++
	}
	
	diversityScore := d.CalculateDiversityIndex(genderCount)
	
	// Calculate distribution percentages
	distribution := make(map[string]float64)
	for gender, count := range genderCount {
		distribution[gender] = (float64(count) / float64(total)) * 100
	}
	
	return diversityScore, distribution
}

// AnalyzeRegionalDiversity analyzes regional representation
func (d *DiversityInclusionDashboard) AnalyzeRegionalDiversity() (float64, map[string]float64) {
	regionCount := make(map[string]int)
	total := len(d.employees)
	
	for _, emp := range d.employees {
		regionCount[emp.Region]++
	}
	
	diversityScore := d.CalculateDiversityIndex(regionCount)
	
	distribution := make(map[string]float64)
	for region, count := range regionCount {
		distribution[region] = (float64(count) / float64(total)) * 100
	}
	
	return diversityScore, distribution
}

// AnalyzeLanguageDiversity analyzes linguistic diversity
func (d *DiversityInclusionDashboard) AnalyzeLanguageDiversity() (float64, map[string]float64) {
	langCount := make(map[string]int)
	total := len(d.employees)
	
	for _, emp := range d.employees {
		langCount[emp.PrimaryLanguage]++
	}
	
	diversityScore := d.CalculateDiversityIndex(langCount)
	
	distribution := make(map[string]float64)
	for lang, count := range langCount {
		distribution[lang] = (float64(count) / float64(total)) * 100
	}
	
	return diversityScore, distribution
}

// AnalyzePayGap analyzes pay equity across different dimensions
func (d *DiversityInclusionDashboard) AnalyzePayGap() PayGapAnalysis {
	// Gender pay gap analysis
	genderSalaries := make(map[string][]float64)
	for _, emp := range d.employees {
		genderSalaries[emp.Gender] = append(genderSalaries[emp.Gender], emp.Salary)
	}
	
	genderPayGap := make(map[string]float64)
	var baselineSalary float64
	
	// Use male salary as baseline if available, otherwise use overall average
	if salaries, exists := genderSalaries["Male"]; exists && len(salaries) > 0 {
		baselineSalary = average(salaries)
	} else {
		allSalaries := make([]float64, 0)
		for _, emp := range d.employees {
			allSalaries = append(allSalaries, emp.Salary)
		}
		baselineSalary = average(allSalaries)
	}
	
	for gender, salaries := range genderSalaries {
		if len(salaries) > 0 {
			avgSalary := average(salaries)
			gapPercent := ((avgSalary - baselineSalary) / baselineSalary) * 100
			genderPayGap[gender] = gapPercent
		}
	}
	
	// Regional pay gap analysis
	regionalSalaries := make(map[string][]float64)
	for _, emp := range d.employees {
		regionalSalaries[emp.Region] = append(regionalSalaries[emp.Region], emp.Salary)
	}
	
	regionalPayGap := make(map[string]float64)
	for region, salaries := range regionalSalaries {
		if len(salaries) > 0 {
			avgSalary := average(salaries)
			gapPercent := ((avgSalary - baselineSalary) / baselineSalary) * 100
			regionalPayGap[region] = gapPercent
		}
	}
	
	// Education pay gap analysis
	educationSalaries := make(map[string][]float64)
	for _, emp := range d.employees {
		educationSalaries[emp.CollegeType] = append(educationSalaries[emp.CollegeType], emp.Salary)
	}
	
	educationPayGap := make(map[string]float64)
	for education, salaries := range educationSalaries {
		if len(salaries) > 0 {
			avgSalary := average(salaries)
			gapPercent := ((avgSalary - baselineSalary) / baselineSalary) * 100
			educationPayGap[education] = gapPercent
		}
	}
	
	// Calculate overall fairness (lower gaps = higher fairness)
	allGaps := make([]float64, 0)
	for _, gap := range genderPayGap {
		allGaps = append(allGaps, math.Abs(gap))
	}
	for _, gap := range regionalPayGap {
		allGaps = append(allGaps, math.Abs(gap))
	}
	
	avgGap := average(allGaps)
	fairness := math.Max(0, 100-(avgGap*2)) // Convert gap to fairness score
	
	return PayGapAnalysis{
		GenderPayGap:    genderPayGap,
		RegionalPayGap:  regionalPayGap,
		EducationPayGap: educationPayGap,
		OverallFairness: fairness,
	}
}

// AnalyzePromotionFairness analyzes promotion patterns across groups
func (d *DiversityInclusionDashboard) AnalyzePromotionFairness() PromotionFairness {
	// Calculate promotion rates by gender
	genderPromotions := make(map[string]int)
	genderTotal := make(map[string]int)
	
	for _, emp := range d.employees {
		genderTotal[emp.Gender]++
		
		// Consider promotion if happened in last 2 years
		if !emp.LastPromotion.IsZero() && 
		   time.Since(emp.LastPromotion) <= 2*365*24*time.Hour {
			genderPromotions[emp.Gender]++
		}
	}
	
	genderPromotionRate := make(map[string]float64)
	for gender, total := range genderTotal {
		if total > 0 {
			promotions := genderPromotions[gender]
			genderPromotionRate[gender] = (float64(promotions) / float64(total)) * 100
		}
	}
	
	// Calculate promotion rates by region
	regionalPromotions := make(map[string]int)
	regionalTotal := make(map[string]int)
	
	for _, emp := range d.employees {
		regionalTotal[emp.Region]++
		
		if !emp.LastPromotion.IsZero() && 
		   time.Since(emp.LastPromotion) <= 2*365*24*time.Hour {
			regionalPromotions[emp.Region]++
		}
	}
	
	regionalPromotionRate := make(map[string]float64)
	for region, total := range regionalTotal {
		if total > 0 {
			promotions := regionalPromotions[region]
			regionalPromotionRate[region] = (float64(promotions) / float64(total)) * 100
		}
	}
	
	// Calculate promotion rates by education
	educationPromotions := make(map[string]int)
	educationTotal := make(map[string]int)
	
	for _, emp := range d.employees {
		educationTotal[emp.CollegeType]++
		
		if !emp.LastPromotion.IsZero() && 
		   time.Since(emp.LastPromotion) <= 2*365*24*time.Hour {
			educationPromotions[emp.CollegeType]++
		}
	}
	
	educationPromotionRate := make(map[string]float64)
	for education, total := range educationTotal {
		if total > 0 {
			promotions := educationPromotions[education]
			educationPromotionRate[education] = (float64(promotions) / float64(total)) * 100
		}
	}
	
	// Calculate fairness score based on variance in promotion rates
	allRates := make([]float64, 0)
	for _, rate := range genderPromotionRate {
		allRates = append(allRates, rate)
	}
	for _, rate := range regionalPromotionRate {
		allRates = append(allRates, rate)
	}
	
	variance := calculateVariance(allRates)
	fairnessScore := math.Max(0, 100-(variance/10)) // Lower variance = higher fairness
	
	return PromotionFairness{
		GenderPromotionRate:    genderPromotionRate,
		RegionalPromotionRate:  regionalPromotionRate,
		EducationPromotionRate: educationPromotionRate,
		FairnessScore:         fairnessScore,
	}
}

// GenerateComprehensiveMetrics generates full diversity and inclusion analysis
func (d *DiversityInclusionDashboard) GenerateComprehensiveMetrics(teamID string) DiversityMetrics {
	if len(d.employees) == 0 {
		return DiversityMetrics{
			TeamID:       teamID,
			AnalysisDate: time.Now(),
			Recommendations: []string{"No employee data available for analysis"},
		}
	}
	
	// Calculate diversity scores
	genderDiversity, genderDist := d.AnalyzeGenderDiversity()
	regionalDiversity, regionalDist := d.AnalyzeRegionalDiversity()  
	languageDiversity, languageDist := d.AnalyzeLanguageDiversity()
	
	// Calculate education and socio-economic diversity
	educationDiversity := d.calculateEducationDiversity()
	socioEconomicDiversity := d.calculateSocioEconomicDiversity()
	
	// Overall diversity score (weighted average)
	overallDiversity := (genderDiversity*0.25 + regionalDiversity*0.25 + 
		languageDiversity*0.20 + educationDiversity*0.15 + socioEconomicDiversity*0.15)
	
	// Calculate inclusion metrics
	avgInclusionScore := d.calculateAverageInclusionScore()
	payGapAnalysis := d.AnalyzePayGap()
	promotionFairness := d.AnalyzePromotionFairness()
	
	// Identify underrepresented groups and challenges
	underrepresented := d.identifyUnderrepresentedGroups(genderDist, regionalDist)
	challenges := d.identifyInclusionChallenges(payGapAnalysis, promotionFairness)
	recommendations := d.generateRecommendations(overallDiversity, avgInclusionScore, challenges)
	
	return DiversityMetrics{
		TeamID:                teamID,
		AnalysisDate:         time.Now(),
		OverallDiversityScore: overallDiversity,
		GenderDiversity:       genderDiversity,
		RegionalDiversity:     regionalDiversity,
		LanguageDiversity:     languageDiversity,
		EducationDiversity:    educationDiversity,
		SocioEconomicDiversity: socioEconomicDiversity,
		GenderDistribution:    genderDist,
		RegionalDistribution:  regionalDist,
		LanguageDistribution:  languageDist,
		AverageInclusionScore: avgInclusionScore,
		PayGapAnalysis:       payGapAnalysis,
		PromotionFairness:    promotionFairness,
		UnderrepresentedGroups: underrepresented,
		InclusionChallenges:   challenges,
		Recommendations:       recommendations,
	}
}

// Helper functions
func (d *DiversityInclusionDashboard) calculateEducationDiversity() float64 {
	eduCount := make(map[string]int)
	for _, emp := range d.employees {
		eduCount[emp.CollegeType]++
	}
	return d.CalculateDiversityIndex(eduCount)
}

func (d *DiversityInclusionDashboard) calculateSocioEconomicDiversity() float64 {
	seCount := make(map[string]int)
	for _, emp := range d.employees {
		seCount[emp.SocioEconomicBackground]++
	}
	return d.CalculateDiversityIndex(seCount)
}

func (d *DiversityInclusionDashboard) calculateAverageInclusionScore() float64 {
	if len(d.employees) == 0 {
		return 0
	}
	
	total := 0.0
	for _, emp := range d.employees {
		total += emp.InclusionScore
	}
	return total / float64(len(d.employees))
}

func (d *DiversityInclusionDashboard) identifyUnderrepresentedGroups(genderDist, regionalDist map[string]float64) []string {
	underrepresented := make([]string, 0)
	
	// Check for gender underrepresentation (< 20%)
	for gender, percentage := range genderDist {
		if percentage < 20.0 {
			underrepresented = append(underrepresented, fmt.Sprintf("%s employees (%.1f%%)", gender, percentage))
		}
	}
	
	// Check for regional underrepresentation (< 10%)
	for region, percentage := range regionalDist {
		if percentage < 10.0 && percentage > 0 {
			underrepresented = append(underrepresented, fmt.Sprintf("%s region (%.1f%%)", region, percentage))
		}
	}
	
	return underrepresented
}

func (d *DiversityInclusionDashboard) identifyInclusionChallenges(payGap PayGapAnalysis, promotion PromotionFairness) []string {
	challenges := make([]string, 0)
	
	if payGap.OverallFairness < 70 {
		challenges = append(challenges, "Significant pay gaps detected across groups")
	}
	
	if promotion.FairnessScore < 70 {
		challenges = append(challenges, "Unequal promotion patterns identified")
	}
	
	// Check for specific pay gaps > 15%
	for group, gap := range payGap.GenderPayGap {
		if math.Abs(gap) > 15 {
			challenges = append(challenges, fmt.Sprintf("Large pay gap for %s (%.1f%%)", group, gap))
		}
	}
	
	return challenges
}

func (d *DiversityInclusionDashboard) generateRecommendations(diversityScore, inclusionScore float64, challenges []string) []string {
	recommendations := make([]string, 0)
	
	if diversityScore < 60 {
		recommendations = append(recommendations, "🌍 Expand recruitment to underrepresented regions and communities")
		recommendations = append(recommendations, "🎯 Set diversity targets for hiring and leadership positions")
	}
	
	if inclusionScore < 70 {
		recommendations = append(recommendations, "🤝 Implement inclusion training and awareness programs")
		recommendations = append(recommendations, "📊 Conduct regular inclusion surveys and feedback sessions")
	}
	
	if len(challenges) > 0 {
		recommendations = append(recommendations, "⚖️ Conduct comprehensive pay equity review and adjustments")
		recommendations = append(recommendations, "📈 Review promotion criteria and processes for bias")
	}
	
	// Indian context specific recommendations
	recommendations = append(recommendations, "🪔 Celebrate diverse cultural festivals and traditions")
	recommendations = append(recommendations, "🗣️ Support multilingual communication in appropriate contexts")
	recommendations = append(recommendations, "👥 Create employee resource groups for different communities")
	
	return recommendations
}

// Utility functions
func average(numbers []float64) float64 {
	if len(numbers) == 0 {
		return 0
	}
	sum := 0.0
	for _, num := range numbers {
		sum += num
	}
	return sum / float64(len(numbers))
}

func calculateVariance(numbers []float64) float64 {
	if len(numbers) <= 1 {
		return 0
	}
	
	avg := average(numbers)
	sumSquares := 0.0
	for _, num := range numbers {
		diff := num - avg
		sumSquares += diff * diff
	}
	return sumSquares / float64(len(numbers))
}

func demoDiversityInclusionDashboard() {
	fmt.Println("📊 Diversity & Inclusion Dashboard Demo - Indian Context")
	fmt.Println(strings.Repeat("=", 60))
	
	dashboard := NewDiversityInclusionDashboard()
	
	// Create sample employees representing Indian workplace diversity
	employees := []Employee{
		{
			ID: "E001", Name: "Rajesh Kumar", Gender: "Male", Age: 32,
			Region: "North India", State: "Delhi", PrimaryLanguage: "Hindi",
			Religion: "Hindu", EducationBackground: "Computer Science", CollegeType: "IIT",
			SocioEconomicBackground: "Middle Class", Department: "Engineering", Level: 5,
			Salary: 1200000, JoiningDate: time.Now().AddDate(-3, 0, 0),
			LastPromotion: time.Now().AddDate(-1, 0, 0), InclusionScore: 85,
			MentorshipOpportunities: 2, LeadershipRoles: 1, VisibilityScore: 80,
		},
		{
			ID: "E002", Name: "Priya Menon", Gender: "Female", Age: 29,
			Region: "South India", State: "Kerala", PrimaryLanguage: "Malayalam",
			Religion: "Hindu", EducationBackground: "Computer Science", CollegeType: "NIT",
			SocioEconomicBackground: "Middle Class", Department: "Engineering", Level: 4,
			Salary: 950000, JoiningDate: time.Now().AddDate(-2, 0, 0),
			LastPromotion: time.Now().AddDate(-8, 0, 0), InclusionScore: 75,
			MentorshipOpportunities: 1, LeadershipRoles: 0, VisibilityScore: 70,
		},
		{
			ID: "E003", Name: "Amit Patel", Gender: "Male", Age: 27,
			Region: "West India", State: "Gujarat", PrimaryLanguage: "Gujarati", 
			Religion: "Hindu", EducationBackground: "Computer Science", CollegeType: "Private",
			SocioEconomicBackground: "Upper Middle Class", Department: "Engineering", Level: 3,
			Salary: 750000, JoiningDate: time.Now().AddDate(-1, -6, 0),
			InclusionScore: 80, MentorshipOpportunities: 1, LeadershipRoles: 0, VisibilityScore: 75,
		},
		{
			ID: "E004", Name: "Sneha Singh", Gender: "Female", Age: 25,
			Region: "North India", State: "Uttar Pradesh", PrimaryLanguage: "Hindi",
			Religion: "Hindu", EducationBackground: "Computer Science", CollegeType: "Regional",
			SocioEconomicBackground: "Lower Middle Class", Department: "Engineering", Level: 2,
			Salary: 600000, JoiningDate: time.Now().AddDate(-1, 0, 0),
			InclusionScore: 65, MentorshipOpportunities: 0, LeadershipRoles: 0, VisibilityScore: 60,
		},
		{
			ID: "E005", Name: "Mohammed Ali", Gender: "Male", Age: 30,
			Region: "South India", State: "Karnataka", PrimaryLanguage: "Urdu",
			Religion: "Muslim", EducationBackground: "Computer Science", CollegeType: "Private",
			SocioEconomicBackground: "Middle Class", Department: "Engineering", Level: 4,
			Salary: 900000, JoiningDate: time.Now().AddDate(-2, -3, 0),
			LastPromotion: time.Now().AddDate(-6, 0, 0), InclusionScore: 70,
			MentorshipOpportunities: 1, LeadershipRoles: 0, VisibilityScore: 65,
		},
	}
	
	// Add employees to dashboard
	for _, emp := range employees {
		dashboard.AddEmployee(emp)
	}
	
	fmt.Println("\n" + strings.Repeat("=", 50))
	
	// Generate comprehensive metrics
	fmt.Println("📈 Generating diversity and inclusion analysis...")
	metrics := dashboard.GenerateComprehensiveMetrics("ENGINEERING_TEAM")
	
	// Display results
	fmt.Printf("\n🎯 Diversity & Inclusion Report\n")
	fmt.Printf("Team: %s\n", metrics.TeamID)
	fmt.Printf("Analysis Date: %s\n", metrics.AnalysisDate.Format("2006-01-02"))
	
	fmt.Printf("\n📊 Diversity Scores (0-100):\n")
	fmt.Printf("   Overall Diversity: %.1f\n", metrics.OverallDiversityScore)
	fmt.Printf("   Gender Diversity: %.1f\n", metrics.GenderDiversity)
	fmt.Printf("   Regional Diversity: %.1f\n", metrics.RegionalDiversity)
	fmt.Printf("   Language Diversity: %.1f\n", metrics.LanguageDiversity)
	fmt.Printf("   Education Diversity: %.1f\n", metrics.EducationDiversity)
	fmt.Printf("   Socio-Economic Diversity: %.1f\n", metrics.SocioEconomicDiversity)
	
	fmt.Printf("\n👥 Representation Analysis:\n")
	fmt.Printf("Gender Distribution:\n")
	for gender, percentage := range metrics.GenderDistribution {
		fmt.Printf("   %s: %.1f%%\n", gender, percentage)
	}
	
	fmt.Printf("Regional Distribution:\n")
	for region, percentage := range metrics.RegionalDistribution {
		fmt.Printf("   %s: %.1f%%\n", region, percentage)
	}
	
	fmt.Printf("Language Distribution:\n")
	for language, percentage := range metrics.LanguageDistribution {
		fmt.Printf("   %s: %.1f%%\n", language, percentage)
	}
	
	fmt.Printf("\n💚 Inclusion Metrics:\n")
	fmt.Printf("   Average Inclusion Score: %.1f/100\n", metrics.AverageInclusionScore)
	fmt.Printf("   Pay Equity Score: %.1f/100\n", metrics.PayGapAnalysis.OverallFairness)
	fmt.Printf("   Promotion Fairness: %.1f/100\n", metrics.PromotionFairness.FairnessScore)
	
	fmt.Printf("\n💰 Pay Gap Analysis:\n")
	fmt.Printf("Gender Pay Gaps:\n")
	for gender, gap := range metrics.PayGapAnalysis.GenderPayGap {
		fmt.Printf("   %s: %+.1f%%\n", gender, gap)
	}
	
	fmt.Printf("Regional Pay Gaps:\n")
	for region, gap := range metrics.PayGapAnalysis.RegionalPayGap {
		fmt.Printf("   %s: %+.1f%%\n", region, gap)
	}
	
	fmt.Printf("\n📈 Promotion Analysis:\n")
	for gender, rate := range metrics.PromotionFairness.GenderPromotionRate {
		fmt.Printf("   %s promotion rate: %.1f%%\n", gender, rate)
	}
	
	if len(metrics.UnderrepresentedGroups) > 0 {
		fmt.Printf("\n⚠️  Underrepresented Groups:\n")
		for _, group := range metrics.UnderrepresentedGroups {
			fmt.Printf("   • %s\n", group)
		}
	}
	
	if len(metrics.InclusionChallenges) > 0 {
		fmt.Printf("\n🚧 Inclusion Challenges:\n")
		for _, challenge := range metrics.InclusionChallenges {
			fmt.Printf("   • %s\n", challenge)
		}
	}
	
	fmt.Printf("\n💡 Recommendations:\n")
	for _, recommendation := range metrics.Recommendations {
		fmt.Printf("   • %s\n", recommendation)
	}
}

func main() {
	demoDiversityInclusionDashboard()
}
/**
 * Diversity & Inclusion Dashboard - Episode 3: Human Factor in Tech
 * =================================================================
 * 
 * भारत की diversity को celebrate करने वाला dashboard
 * 26+ states, 100+ languages, different cultures का representation
 * 
 * Features:
 * - Regional diversity tracking (North, South, East, West, Northeast)
 * - Language diversity monitoring (Hindi, English, Tamil, Telugu, etc.)
 * - Gender representation analysis
 * - Educational background diversity (IIT/NIT vs Local colleges)
 * - Inclusion culture measurement
 * - Bias detection and mitigation recommendations
 */

package main

import (
	"encoding/json"
	"fmt"
	"math"
	"sort"
	"time"
)

// Employee represents team member with diversity attributes
type Employee struct {
	ID                string   `json:"id"`
	Name             string   `json:"name"`
	Gender           string   `json:"gender"` // Male, Female, Other
	State            string   `json:"state"` // Karnataka, Maharashtra, etc.
	Region           string   `json:"region"` // North, South, East, West, Northeast
	Languages        []string `json:"languages"` // Hindi, English, Tamil, etc.
	Religion         string   `json:"religion"` // Hindu, Muslim, Christian, Sikh, etc.
	EducationalBg    string   `json:"educational_bg"` // IIT, NIT, Private, Local
	YearsOfExperience int     `json:"years_of_experience"`
	Role             string   `json:"role"`
	Department       string   `json:"department"`
	JoinDate         time.Time `json:"join_date"`
	CurrentLevel     string   `json:"current_level"` // Junior, Senior, Lead, Manager
	MentorshipGiven  int      `json:"mentorship_given"` // Number of people mentored
	MentorshipReceived bool   `json:"mentorship_received"`
}

// Team represents a tech team with diversity metrics
type Team struct {
	TeamID       string     `json:"team_id"`
	TeamName     string     `json:"team_name"`
	Department   string     `json:"department"`
	TeamLead     string     `json:"team_lead"`
	Members      []Employee `json:"members"`
	CreationDate time.Time  `json:"creation_date"`
}

// DiversityMetrics contains calculated diversity statistics
type DiversityMetrics struct {
	TotalEmployees      int                       `json:"total_employees"`
	GenderDistribution  map[string]int           `json:"gender_distribution"`
	RegionalDistribution map[string]int          `json:"regional_distribution"`
	StateDistribution   map[string]int           `json:"state_distribution"`
	LanguageDistribution map[string]int          `json:"language_distribution"`
	ReligionDistribution map[string]int          `json:"religion_distribution"`
	EducationDistribution map[string]int         `json:"education_distribution"`
	ExperienceDistribution map[string]int        `json:"experience_distribution"`
	LeadershipDiversity map[string]int           `json:"leadership_diversity"`
	DiversityIndex      float64                  `json:"diversity_index"` // Shannon Diversity Index
	InclusionScore      float64                  `json:"inclusion_score"` // 0-100 scale
}

// BiasAlert represents detected bias in team composition or processes
type BiasAlert struct {
	Type        string  `json:"type"` // Gender, Regional, Educational, etc.
	Severity    string  `json:"severity"` // Low, Medium, High, Critical
	Description string  `json:"description"`
	Impact      float64 `json:"impact"` // 0-1 scale
	Recommendation string `json:"recommendation"`
	DetectionDate time.Time `json:"detection_date"`
}

// DiversityDashboard main system
type DiversityDashboard struct {
	Organization  string             `json:"organization"`
	Teams         []Team            `json:"teams"`
	AllEmployees  []Employee        `json:"all_employees"`
	Metrics       DiversityMetrics  `json:"metrics"`
	BiasAlerts    []BiasAlert       `json:"bias_alerts"`
	LastUpdated   time.Time         `json:"last_updated"`
}

// Indian states and regions mapping
var StateRegionMapping = map[string]string{
	// North
	"Delhi": "North", "Punjab": "North", "Haryana": "North", "Uttar Pradesh": "North",
	"Uttarakhand": "North", "Himachal Pradesh": "North", "Jammu and Kashmir": "North",
	"Rajasthan": "North",
	
	// South  
	"Karnataka": "South", "Tamil Nadu": "South", "Andhra Pradesh": "South",
	"Telangana": "South", "Kerala": "South", "Puducherry": "South",
	
	// West
	"Maharashtra": "West", "Gujarat": "West", "Goa": "West", "Rajasthan": "West",
	"Madhya Pradesh": "West",
	
	// East
	"West Bengal": "East", "Odisha": "East", "Jharkhand": "East", "Bihar": "East",
	
	// Northeast
	"Assam": "Northeast", "Arunachal Pradesh": "Northeast", "Manipur": "Northeast",
	"Meghalaya": "Northeast", "Mizoram": "Northeast", "Nagaland": "Northeast", "Tripura": "Northeast",
	"Sikkim": "Northeast",
	
	// Central
	"Chhattisgarh": "Central",
}

// Common Indian languages
var IndianLanguages = []string{
	"Hindi", "English", "Tamil", "Telugu", "Bengali", "Marathi", "Gujarati",
	"Kannada", "Malayalam", "Punjabi", "Oriya", "Assamese", "Urdu",
}

// Initialize new diversity dashboard
func NewDiversityDashboard(orgName string) *DiversityDashboard {
	return &DiversityDashboard{
		Organization: orgName,
		Teams:        []Team{},
		AllEmployees: []Employee{},
		BiasAlerts:   []BiasAlert{},
		LastUpdated:  time.Now(),
	}
}

// Add team to dashboard
func (dd *DiversityDashboard) AddTeam(team Team) {
	// Set region for each member based on state
	for i := range team.Members {
		if region, exists := StateRegionMapping[team.Members[i].State]; exists {
			team.Members[i].Region = region
		} else {
			team.Members[i].Region = "Other"
		}
		dd.AllEmployees = append(dd.AllEmployees, team.Members[i])
	}
	
	dd.Teams = append(dd.Teams, team)
	dd.LastUpdated = time.Now()
	
	fmt.Printf("✅ Added team: %s with %d members\n", team.TeamName, len(team.Members))
}

// Calculate comprehensive diversity metrics
func (dd *DiversityDashboard) CalculateMetrics() {
	dd.Metrics = DiversityMetrics{
		TotalEmployees:        len(dd.AllEmployees),
		GenderDistribution:    make(map[string]int),
		RegionalDistribution:  make(map[string]int),
		StateDistribution:     make(map[string]int),
		LanguageDistribution:  make(map[string]int),
		ReligionDistribution:  make(map[string]int),
		EducationDistribution: make(map[string]int),
		ExperienceDistribution: make(map[string]int),
		LeadershipDiversity:   make(map[string]int),
	}
	
	// Count distributions
	for _, employee := range dd.AllEmployees {
		// Gender
		dd.Metrics.GenderDistribution[employee.Gender]++
		
		// Regional
		dd.Metrics.RegionalDistribution[employee.Region]++
		
		// State
		dd.Metrics.StateDistribution[employee.State]++
		
		// Languages
		for _, lang := range employee.Languages {
			dd.Metrics.LanguageDistribution[lang]++
		}
		
		// Religion
		dd.Metrics.ReligionDistribution[employee.Religion]++
		
		// Education
		dd.Metrics.EducationDistribution[employee.EducationalBg]++
		
		// Experience brackets
		var expBracket string
		switch {
		case employee.YearsOfExperience <= 2:
			expBracket = "0-2 years"
		case employee.YearsOfExperience <= 5:
			expBracket = "3-5 years"
		case employee.YearsOfExperience <= 10:
			expBracket = "6-10 years"
		default:
			expBracket = "10+ years"
		}
		dd.Metrics.ExperienceDistribution[expBracket]++
		
		// Leadership diversity (Manager level and above)
		if employee.CurrentLevel == "Manager" || employee.CurrentLevel == "Lead" {
			dd.Metrics.LeadershipDiversity[employee.Gender]++
		}
	}
	
	// Calculate Shannon Diversity Index
	dd.Metrics.DiversityIndex = dd.calculateShannonIndex()
	
	// Calculate Inclusion Score
	dd.Metrics.InclusionScore = dd.calculateInclusionScore()
}

// Shannon Diversity Index calculation
func (dd *DiversityDashboard) calculateShannonIndex() float64 {
	// Calculate based on regional diversity as primary measure
	total := float64(dd.Metrics.TotalEmployees)
	if total == 0 {
		return 0
	}
	
	shannonIndex := 0.0
	for _, count := range dd.Metrics.RegionalDistribution {
		if count > 0 {
			proportion := float64(count) / total
			shannonIndex -= proportion * math.Log(proportion)
		}
	}
	
	return shannonIndex
}

// Calculate inclusion score based on multiple factors
func (dd *DiversityDashboard) calculateInclusionScore() float64 {
	score := 100.0 // Start with perfect score
	
	// Gender balance penalty
	genderBalance := dd.calculateGenderBalance()
	score -= (50.0 - genderBalance) * 0.5 // Penalty for imbalance
	
	// Regional representation penalty
	regionalBalance := dd.calculateRegionalBalance()
	score -= (50.0 - regionalBalance) * 0.3
	
	// Educational diversity penalty  
	educationalBalance := dd.calculateEducationalBalance()
	score -= (50.0 - educationalBalance) * 0.4
	
	// Leadership diversity penalty
	leadershipBalance := dd.calculateLeadershipDiversity()
	score -= (50.0 - leadershipBalance) * 0.6
	
	// Language diversity bonus (Indian context)
	languageCount := len(dd.Metrics.LanguageDistribution)
	if languageCount > 3 {
		score += float64(languageCount-3) * 2 // Bonus for multilingual teams
	}
	
	if score < 0 {
		score = 0
	}
	if score > 100 {
		score = 100
	}
	
	return score
}

// Calculate gender balance (closer to 50-50 is better)
func (dd *DiversityDashboard) calculateGenderBalance() float64 {
	total := float64(dd.Metrics.TotalEmployees)
	if total == 0 {
		return 50.0
	}
	
	maleCount := float64(dd.Metrics.GenderDistribution["Male"])
	femaleCount := float64(dd.Metrics.GenderDistribution["Female"])
	
	malePercent := (maleCount / total) * 100
	femalePercent := (femaleCount / total) * 100
	
	// Calculate deviation from 50-50
	deviation := math.Abs(malePercent - femalePercent)
	return 50.0 - (deviation / 2.0)
}

// Calculate regional balance
func (dd *DiversityDashboard) calculateRegionalBalance() float64 {
	total := float64(dd.Metrics.TotalEmployees)
	if total == 0 {
		return 50.0
	}
	
	// Ideal would be representation from all major regions
	regionCount := len(dd.Metrics.RegionalDistribution)
	maxRegions := 5.0 // North, South, East, West, Northeast
	
	representationScore := (float64(regionCount) / maxRegions) * 100
	
	// Also consider balance within represented regions
	variance := 0.0
	expectedPerRegion := total / float64(regionCount)
	
	for _, count := range dd.Metrics.RegionalDistribution {
		variance += math.Pow(float64(count)-expectedPerRegion, 2)
	}
	variance = variance / float64(regionCount)
	balanceScore := math.Max(0, 100.0-(variance/total)*100)
	
	return (representationScore + balanceScore) / 2.0
}

// Calculate educational diversity balance
func (dd *DiversityDashboard) calculateEducationalBalance() float64 {
	total := float64(dd.Metrics.TotalEmployees)
	if total == 0 {
		return 50.0
	}
	
	// Bias towards IIT/NIT should be penalized for diversity
	iitNitCount := float64(dd.Metrics.EducationDistribution["IIT"] + dd.Metrics.EducationDistribution["NIT"])
	otherCount := total - iitNitCount
	
	if total == 0 {
		return 50.0
	}
	
	iitNitPercent := (iitNitCount / total) * 100
	
	// Ideal would be around 30-40% from premium institutes
	if iitNitPercent > 60 {
		return math.Max(0, 100.0-(iitNitPercent-40)*2) // Penalty for over-representation
	} else if iitNitPercent < 20 {
		return math.Max(0, 100.0-(20-iitNitPercent)*1.5) // Small penalty for under-representation
	} else {
		return 100.0
	}
}

// Calculate leadership diversity
func (dd *DiversityDashboard) calculateLeadershipDiversity() float64 {
	totalLeaders := 0
	for _, count := range dd.Metrics.LeadershipDiversity {
		totalLeaders += count
	}
	
	if totalLeaders == 0 {
		return 50.0
	}
	
	femaleLeaders := float64(dd.Metrics.LeadershipDiversity["Female"])
	femaleLeaderPercent := (femaleLeaders / float64(totalLeaders)) * 100
	
	// Ideal would be closer to population gender ratio (~30-35% female leaders)
	target := 35.0
	deviation := math.Abs(femaleLeaderPercent - target)
	return math.Max(0, 100.0-deviation*2)
}

// Detect and generate bias alerts
func (dd *DiversityDashboard) DetectBias() {
	dd.BiasAlerts = []BiasAlert{} // Reset alerts
	
	// Gender bias in leadership
	if dd.calculateLeadershipDiversity() < 40 {
		alert := BiasAlert{
			Type:           "Gender",
			Severity:       dd.getSeverity(dd.calculateLeadershipDiversity()),
			Description:    "Significant gender imbalance in leadership positions",
			Impact:         (60.0 - dd.calculateLeadershipDiversity()) / 100.0,
			Recommendation: "Implement mentorship programs for underrepresented genders",
			DetectionDate:  time.Now(),
		}
		dd.BiasAlerts = append(dd.BiasAlerts, alert)
	}
	
	// Regional bias
	if dd.calculateRegionalBalance() < 40 {
		alert := BiasAlert{
			Type:           "Regional",
			Severity:       dd.getSeverity(dd.calculateRegionalBalance()),
			Description:    "Limited regional representation in team composition",
			Impact:         (60.0 - dd.calculateRegionalBalance()) / 100.0,
			Recommendation: "Expand recruitment to underrepresented regions",
			DetectionDate:  time.Now(),
		}
		dd.BiasAlerts = append(dd.BiasAlerts, alert)
	}
	
	// Educational bias (over-representation of premium institutes)
	iitNitTotal := dd.Metrics.EducationDistribution["IIT"] + dd.Metrics.EducationDistribution["NIT"]
	if float64(iitNitTotal)/float64(dd.Metrics.TotalEmployees) > 0.7 {
		alert := BiasAlert{
			Type:           "Educational",
			Severity:       "High",
			Description:    "Over-representation of IIT/NIT graduates, potential bias against other institutions",
			Impact:         0.6,
			Recommendation: "Implement blind resume screening and diversify recruitment sources",
			DetectionDate:  time.Now(),
		}
		dd.BiasAlerts = append(dd.BiasAlerts, alert)
	}
	
	// Language diversity alert
	if len(dd.Metrics.LanguageDistribution) < 3 {
		alert := BiasAlert{
			Type:           "Language",
			Severity:       "Medium",
			Description:    "Limited language diversity may impact communication inclusivity",
			Impact:         0.4,
			Recommendation: "Encourage multilingual communication and diverse hiring",
			DetectionDate:  time.Now(),
		}
		dd.BiasAlerts = append(dd.BiasAlerts, alert)
	}
}

func (dd *DiversityDashboard) getSeverity(score float64) string {
	if score < 30 {
		return "Critical"
	} else if score < 50 {
		return "High"
	} else if score < 70 {
		return "Medium"
	} else {
		return "Low"
	}
}

// Generate comprehensive diversity report
func (dd *DiversityDashboard) GenerateReport() {
	fmt.Println("\n🌈 Diversity & Inclusion Dashboard")
	fmt.Printf("Organization: %s\n", dd.Organization)
	fmt.Println("==================================")
	fmt.Printf("Total Employees: %d\n", dd.Metrics.TotalEmployees)
	fmt.Printf("Total Teams: %d\n", len(dd.Teams))
	fmt.Printf("Last Updated: %s\n\n", dd.LastUpdated.Format("2006-01-02 15:04:05"))
	
	// Overall scores
	fmt.Printf("📊 Overall Diversity Index: %.2f (Higher is better)\n", dd.Metrics.DiversityIndex)
	fmt.Printf("🤝 Inclusion Score: %.1f/100 %s\n\n", dd.Metrics.InclusionScore, dd.getScoreEmoji(dd.Metrics.InclusionScore))
	
	// Gender distribution
	fmt.Println("👥 Gender Distribution:")
	dd.printDistribution(dd.Metrics.GenderDistribution)
	fmt.Printf("   Balance Score: %.1f/100\n\n", dd.calculateGenderBalance())
	
	// Regional distribution
	fmt.Println("🗺️ Regional Distribution:")
	dd.printDistribution(dd.Metrics.RegionalDistribution)
	fmt.Printf("   Balance Score: %.1f/100\n\n", dd.calculateRegionalBalance())
	
	// Top states
	fmt.Println("🏛️ Top 5 States Represented:")
	dd.printTopStates()
	
	// Language diversity
	fmt.Println("🗣️ Language Diversity:")
	dd.printDistribution(dd.Metrics.LanguageDistribution)
	
	// Educational background
	fmt.Println("🎓 Educational Background:")
	dd.printDistribution(dd.Metrics.EducationDistribution)
	fmt.Printf("   Balance Score: %.1f/100\n\n", dd.calculateEducationalBalance())
	
	// Leadership diversity
	fmt.Println("👔 Leadership Diversity:")
	dd.printDistribution(dd.Metrics.LeadershipDiversity)
	fmt.Printf("   Leadership Balance Score: %.1f/100\n\n", dd.calculateLeadershipDiversity())
	
	// Experience distribution
	fmt.Println("⏳ Experience Distribution:")
	dd.printDistribution(dd.Metrics.ExperienceDistribution)
	
	// Bias alerts
	fmt.Println("🚨 Bias Alerts:")
	if len(dd.BiasAlerts) == 0 {
		fmt.Println("   ✅ No significant bias detected")
	} else {
		for i, alert := range dd.BiasAlerts {
			fmt.Printf("   %d. %s Bias (%s severity)\n", i+1, alert.Type, alert.Severity)
			fmt.Printf("      %s\n", alert.Description)
			fmt.Printf("      💡 %s\n", alert.Recommendation)
			fmt.Printf("      Impact: %.1f%% | Detected: %s\n\n", 
				alert.Impact*100, alert.DetectionDate.Format("2006-01-02"))
		}
	}
	
	// Team-wise analysis
	dd.generateTeamAnalysis()
	
	// Recommendations
	dd.generateRecommendations()
}

func (dd *DiversityDashboard) printDistribution(distribution map[string]int) {
	type kv struct {
		Key   string
		Value int
	}
	
	var sorted []kv
	total := 0
	for k, v := range distribution {
		sorted = append(sorted, kv{k, v})
		total += v
	}
	
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].Value > sorted[j].Value
	})
	
	for _, item := range sorted {
		percentage := float64(item.Value) / float64(total) * 100
		fmt.Printf("   %s: %d (%.1f%%)\n", item.Key, item.Value, percentage)
	}
	fmt.Println()
}

func (dd *DiversityDashboard) printTopStates() {
	type stateCount struct {
		State string
		Count int
	}
	
	var states []stateCount
	for state, count := range dd.Metrics.StateDistribution {
		states = append(states, stateCount{state, count})
	}
	
	sort.Slice(states, func(i, j int) bool {
		return states[i].Count > states[j].Count
	})
	
	limit := 5
	if len(states) < 5 {
		limit = len(states)
	}
	
	for i := 0; i < limit; i++ {
		percentage := float64(states[i].Count) / float64(dd.Metrics.TotalEmployees) * 100
		fmt.Printf("   %d. %s: %d (%.1f%%)\n", i+1, states[i].State, states[i].Count, percentage)
	}
	fmt.Println()
}

func (dd *DiversityDashboard) getScoreEmoji(score float64) string {
	if score >= 80 {
		return "✅ Excellent"
	} else if score >= 60 {
		return "⚠️ Good"
	} else if score >= 40 {
		return "🟡 Needs Improvement"
	} else {
		return "🚨 Critical"
	}
}

func (dd *DiversityDashboard) generateTeamAnalysis() {
	fmt.Println("🏗️ Team-wise Analysis:")
	fmt.Println("======================")
	
	for _, team := range dd.Teams {
		fmt.Printf("Team: %s (%d members)\n", team.TeamName, len(team.Members))
		
		// Team gender balance
		genderCount := make(map[string]int)
		regionCount := make(map[string]int)
		langCount := make(map[string]int)
		
		for _, member := range team.Members {
			genderCount[member.Gender]++
			regionCount[member.Region]++
			for _, lang := range member.Languages {
				langCount[lang]++
			}
		}
		
		// Calculate team diversity score
		teamSize := float64(len(team.Members))
		teamDiversityScore := 0.0
		
		// Gender diversity component
		if len(genderCount) > 1 {
			teamDiversityScore += 25.0
		}
		
		// Regional diversity component
		regionDiversity := float64(len(regionCount)) / 5.0 * 25.0 // Max 5 regions
		teamDiversityScore += regionDiversity
		
		// Language diversity component
		langDiversity := math.Min(float64(len(langCount))/3.0, 1.0) * 25.0
		teamDiversityScore += langDiversity
		
		// Experience mix component
		juniorCount := 0
		seniorCount := 0
		for _, member := range team.Members {
			if member.YearsOfExperience <= 3 {
				juniorCount++
			} else {
				seniorCount++
			}
		}
		if juniorCount > 0 && seniorCount > 0 {
			teamDiversityScore += 25.0
		}
		
		fmt.Printf("   Diversity Score: %.1f/100 %s\n", teamDiversityScore, dd.getScoreEmoji(teamDiversityScore))
		fmt.Printf("   Gender Mix: %v\n", genderCount)
		fmt.Printf("   Regional Mix: %v\n", regionCount)
		fmt.Printf("   Languages: %d different languages\n", len(langCount))
		fmt.Println()
	}
}

func (dd *DiversityDashboard) generateRecommendations() {
	fmt.Println("💡 Recommendations for Improving D&I:")
	fmt.Println("=====================================")
	
	recommendations := []string{}
	
	// Gender recommendations
	if dd.calculateGenderBalance() < 60 {
		recommendations = append(recommendations, "🎯 Increase gender diversity through targeted recruitment campaigns")
		recommendations = append(recommendations, "👩‍💼 Implement mentorship programs for underrepresented genders")
	}
	
	// Regional recommendations
	if dd.calculateRegionalBalance() < 60 {
		recommendations = append(recommendations, "🗺️ Expand recruitment to underrepresented regions (especially Northeast)")
		recommendations = append(recommendations, "🏫 Partner with universities across different states")
	}
	
	// Educational recommendations
	if dd.calculateEducationalBalance() < 60 {
		recommendations = append(recommendations, "🎓 Diversify recruitment beyond IIT/NIT - focus on local talent")
		recommendations = append(recommendations, "👀 Implement blind resume screening to reduce educational bias")
	}
	
	// Leadership recommendations
	if dd.calculateLeadershipDiversity() < 60 {
		recommendations = append(recommendations, "📈 Create leadership development programs for underrepresented groups")
		recommendations = append(recommendations, "🤝 Establish sponsorship (not just mentorship) programs")
	}
	
	// General recommendations
	recommendations = append(recommendations, "🎉 Celebrate regional festivals and cultural diversity")
	recommendations = append(recommendations, "📚 Conduct unconscious bias training for all employees")
	recommendations = append(recommendations, "📊 Set up diversity metrics in hiring and promotion processes")
	recommendations = append(recommendations, "🗣️ Form Employee Resource Groups (ERGs) for different communities")
	
	for i, rec := range recommendations {
		fmt.Printf("%d. %s\n", i+1, rec)
	}
	
	fmt.Println("\n🌟 Key Success Factors:")
	fmt.Println("- Leadership commitment to diversity goals")
	fmt.Println("- Data-driven approach to track progress")
	fmt.Println("- Inclusive culture that values different perspectives")
	fmt.Println("- Regular assessment and course correction")
	fmt.Println("- Celebration of India's rich cultural diversity")
}

// Demo function
func main() {
	fmt.Println("🌈 Diversity & Inclusion Dashboard Demo")
	fmt.Println("========================================")
	
	dashboard := NewDiversityDashboard("Tech Innovators India Pvt Ltd")
	
	// Create sample teams with diverse composition
	teams := []Team{
		{
			TeamID:   "TEAM001",
			TeamName: "Backend Engineering",
			Department: "Engineering",
			TeamLead: "EMP003",
			Members: []Employee{
				{"EMP001", "Rajesh Sharma", "Male", "Maharashtra", "", []string{"Hindi", "English", "Marathi"}, "Hindu", "IIT", 8, "Senior Developer", "Engineering", time.Date(2018, 1, 15, 0, 0, 0, 0, time.UTC), "Senior", 2, true},
				{"EMP002", "Priya Nair", "Female", "Kerala", "", []string{"Malayalam", "English", "Hindi"}, "Hindu", "NIT", 6, "Developer", "Engineering", time.Date(2020, 3, 10, 0, 0, 0, 0, time.UTC), "Senior", 1, true},
				{"EMP003", "Amit Singh", "Male", "Uttar Pradesh", "", []string{"Hindi", "English"}, "Hindu", "Private", 10, "Tech Lead", "Engineering", time.Date(2016, 8, 20, 0, 0, 0, 0, time.UTC), "Lead", 3, false},
				{"EMP004", "Sneha Reddy", "Female", "Telangana", "", []string{"Telugu", "English", "Hindi"}, "Hindu", "Local", 4, "Developer", "Engineering", time.Date(2021, 6, 5, 0, 0, 0, 0, time.UTC), "Junior", 0, true},
				{"EMP005", "Mohammed Ali", "Male", "West Bengal", "", []string{"Bengali", "Hindi", "English", "Urdu"}, "Muslim", "IIT", 7, "Senior Developer", "Engineering", time.Date(2019, 2, 12, 0, 0, 0, 0, time.UTC), "Senior", 1, true},
			},
		},
		{
			TeamID:   "TEAM002", 
			TeamName: "Frontend Engineering",
			Department: "Engineering",
			TeamLead: "EMP008",
			Members: []Employee{
				{"EMP006", "Kavya Iyer", "Female", "Tamil Nadu", "", []string{"Tamil", "English", "Hindi"}, "Hindu", "Private", 5, "Developer", "Engineering", time.Date(2020, 9, 8, 0, 0, 0, 0, time.UTC), "Senior", 0, true},
				{"EMP007", "Vikram Patel", "Male", "Gujarat", "", []string{"Gujarati", "Hindi", "English"}, "Hindu", "NIT", 9, "Senior Developer", "Engineering", time.Date(2017, 4, 3, 0, 0, 0, 0, time.UTC), "Senior", 2, false},
				{"EMP008", "Riya Gupta", "Female", "Delhi", "", []string{"Hindi", "English", "Punjabi"}, "Hindu", "IIT", 11, "Engineering Manager", "Engineering", time.Date(2015, 11, 25, 0, 0, 0, 0, time.UTC), "Manager", 4, false},
				{"EMP009", "Arjun Das", "Male", "Assam", "", []string{"Assamese", "Bengali", "Hindi", "English"}, "Hindu", "Local", 3, "Junior Developer", "Engineering", time.Date(2022, 1, 10, 0, 0, 0, 0, time.UTC), "Junior", 0, true},
				{"EMP010", "Fatima Khan", "Female", "Karnataka", "", []string{"Kannada", "Urdu", "Hindi", "English"}, "Muslim", "Private", 6, "Developer", "Engineering", time.Date(2019, 7, 18, 0, 0, 0, 0, time.UTC), "Senior", 1, true},
			},
		},
	}
	
	// Add teams to dashboard
	for _, team := range teams {
		dashboard.AddTeam(team)
	}
	
	// Calculate metrics and detect bias
	dashboard.CalculateMetrics()
	dashboard.DetectBias()
	
	// Generate comprehensive report
	dashboard.GenerateReport()
	
	// Export to JSON for integration
	jsonData, err := json.MarshalIndent(dashboard, "", "  ")
	if err != nil {
		fmt.Printf("Error generating JSON: %v\n", err)
	} else {
		fmt.Println("\n💾 JSON Export Sample (first 500 characters):")
		fmt.Println("==============================================")
		if len(jsonData) > 500 {
			fmt.Printf("%s...\n", string(jsonData[:500]))
		} else {
			fmt.Println(string(jsonData))
		}
	}
	
	fmt.Println("\n✅ Diversity & Inclusion Analysis Complete!")
	fmt.Println("🎯 Use these insights to build more inclusive teams")
	fmt.Println("🌟 भारत की विविधता ही हमारी ताकत है!")
}
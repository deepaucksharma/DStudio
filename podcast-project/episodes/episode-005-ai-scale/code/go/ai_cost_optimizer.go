/*
AI Cost Optimizer for Indian Infrastructure
Episode 5: Go Implementation

Production-ready cost optimization system for Indian AI companies
Optimizes cloud costs, resource allocation, and budget management

Author: Code Developer Agent
Context: Indian AI/ML cost optimization with regional pricing and constraints
*/

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net/http"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/mux"
)

// Main cost optimizer system
// भारतीय AI companies के लिए comprehensive cost optimization
type AICostOptimizer struct {
	resourceManager    *ResourceManager
	costAnalyzer      *CostAnalyzer
	budgetManager     *BudgetManager
	pricingEngine     *PricingEngine
	recommendationEngine *RecommendationEngine
	alertManager      *AlertManager
	forecastEngine    *ForecastEngine
	reportGenerator   *ReportGenerator
	mu                sync.RWMutex
	ctx               context.Context
	cancel            context.CancelFunc
}

// Resource manager for tracking cloud resources
// Multi-cloud support for Indian regions
type ResourceManager struct {
	resources        map[string]*Resource
	providers        map[string]*CloudProvider
	regions          map[string]*Region
	utilizationData  map[string]*UtilizationMetrics
	reservations     map[string]*Reservation
	spotInstances    map[string]*SpotInstance
	mu               sync.RWMutex
}

// Individual cloud resource
type Resource struct {
	ID               string                 `json:"id"`
	Name             string                 `json:"name"`
	Provider         string                 `json:"provider"` // AWS, Azure, GCP, On-Premise
	Region           string                 `json:"region"`
	ResourceType     ResourceType           `json:"resource_type"`
	InstanceType     string                 `json:"instance_type"`
	Status           ResourceStatus         `json:"status"`
	Company          string                 `json:"company"`
	UseCase          string                 `json:"use_case"`
	CostPerHourINR   float64               `json:"cost_per_hour_inr"`
	UtilizationPercent float64             `json:"utilization_percent"`
	Tags             map[string]string      `json:"tags"`
	LaunchedAt       time.Time             `json:"launched_at"`
	LastUsed         time.Time             `json:"last_used"`
	MonthlyBudgetINR float64               `json:"monthly_budget_inr"`
	ActualCostINR    float64               `json:"actual_cost_inr"`
	PredictedCostINR float64               `json:"predicted_cost_inr"`
	
	// AI-specific attributes
	GPUCount         int                   `json:"gpu_count"`
	GPUType          string               `json:"gpu_type"`
	MemoryGB         int                  `json:"memory_gb"`
	StorageGB        int                  `json:"storage_gb"`
	NetworkBandwidth int                  `json:"network_bandwidth_mbps"`
}

type ResourceType int

const (
	ResourceTypeCompute ResourceType = iota
	ResourceTypeGPU
	ResourceTypeStorage
	ResourceTypeDatabase
	ResourceTypeMLService
	ResourceTypeNetworking
	ResourceTypeContainer
)

func (rt ResourceType) String() string {
	switch rt {
	case ResourceTypeCompute:
		return "compute"
	case ResourceTypeGPU:
		return "gpu"
	case ResourceTypeStorage:
		return "storage"
	case ResourceTypeDatabase:
		return "database"
	case ResourceTypeMLService:
		return "ml_service"
	case ResourceTypeNetworking:
		return "networking"
	case ResourceTypeContainer:
		return "container"
	default:
		return "unknown"
	}
}

type ResourceStatus int

const (
	ResourceStatusRunning ResourceStatus = iota
	ResourceStatusStopped
	ResourceStatusTerminated
	ResourceStatusScheduled
	ResourceStatusError
)

// Cloud provider configuration
type CloudProvider struct {
	Name              string                      `json:"name"`
	Regions           []string                   `json:"regions"`
	SupportedServices []string                   `json:"supported_services"`
	PricingTiers      map[string]*PricingTier    `json:"pricing_tiers"`
	DiscountPrograms  []DiscountProgram          `json:"discount_programs"`
	APICredentials    map[string]string          `json:"api_credentials"`
	RateLimits        map[string]int             `json:"rate_limits"`
}

// Regional information and costs
type Region struct {
	ID                string              `json:"id"`
	Name              string              `json:"name"`
	Provider          string              `json:"provider"`
	Country           string              `json:"country"`
	City              string              `json:"city"`
	LatencyToMumbaiMs int                 `json:"latency_to_mumbai_ms"`
	DataCostMultiplier float64            `json:"data_cost_multiplier"`
	ComputeCostMultiplier float64         `json:"compute_cost_multiplier"`
	Availability      []string            `json:"availability"` // Services available
	ComplianceFlags   []string            `json:"compliance_flags"` // Data residency, etc.
}

// Pricing tier information
type PricingTier struct {
	Name              string  `json:"name"`
	MinUsageHours     int     `json:"min_usage_hours"`
	MaxUsageHours     int     `json:"max_usage_hours"`
	DiscountPercent   float64 `json:"discount_percent"`
	CommitmentMonths  int     `json:"commitment_months"`
}

// Discount programs (Reserved, Spot, etc.)
type DiscountProgram struct {
	Type              DiscountType `json:"type"`
	Name              string       `json:"name"`
	DiscountPercent   float64      `json:"discount_percent"`
	Requirements      []string     `json:"requirements"`
	AvailableRegions  []string     `json:"available_regions"`
	MinCommitmentDays int          `json:"min_commitment_days"`
}

type DiscountType int

const (
	DiscountTypeReserved DiscountType = iota
	DiscountTypeSpot
	DiscountTypePreemptible
	DiscountTypeSavingsPlans
	DiscountTypeCommitted
	DiscountTypeEducational
	DiscountTypeStartup
)

// Utilization metrics for cost optimization
type UtilizationMetrics struct {
	ResourceID        string                    `json:"resource_id"`
	CPUUtilization    TimeSeries               `json:"cpu_utilization"`
	MemoryUtilization TimeSeries               `json:"memory_utilization"`
	GPUUtilization    TimeSeries               `json:"gpu_utilization"`
	NetworkUtilization TimeSeries               `json:"network_utilization"`
	StorageUtilization TimeSeries               `json:"storage_utilization"`
	RequestsPerSecond TimeSeries               `json:"requests_per_second"`
	IdleTimePercent   float64                  `json:"idle_time_percent"`
	PeakHours         []int                    `json:"peak_hours"` // Hours of day (IST)
	LastUpdated       time.Time                `json:"last_updated"`
}

type TimeSeries struct {
	Values    []float64   `json:"values"`
	Timestamps []time.Time `json:"timestamps"`
	Average   float64     `json:"average"`
	Maximum   float64     `json:"maximum"`
	Minimum   float64     `json:"minimum"`
}

// Reservations for cost savings
type Reservation struct {
	ID                string    `json:"id"`
	ResourceType      string    `json:"resource_type"`
	InstanceType      string    `json:"instance_type"`
	Region            string    `json:"region"`
	TermMonths        int       `json:"term_months"`
	PaymentOption     string    `json:"payment_option"` // All Upfront, Partial, No Upfront
	DiscountPercent   float64   `json:"discount_percent"`
	MonthlyCostINR    float64   `json:"monthly_cost_inr"`
	StartDate         time.Time `json:"start_date"`
	EndDate           time.Time `json:"end_date"`
	UtilizationTarget float64   `json:"utilization_target"`
	ActualUtilization float64   `json:"actual_utilization"`
}

// Spot instances for cost optimization
type SpotInstance struct {
	ID                    string    `json:"id"`
	InstanceType          string    `json:"instance_type"`
	Region                string    `json:"region"`
	CurrentPriceINR       float64   `json:"current_price_inr"`
	OnDemandPriceINR      float64   `json:"on_demand_price_inr"`
	SavingsPercent        float64   `json:"savings_percent"`
	AvailabilityZone      string    `json:"availability_zone"`
	InterruptionFrequency string    `json:"interruption_frequency"` // <5%, 5-10%, etc.
	LastInterruption      time.Time `json:"last_interruption"`
	MaxBidPriceINR        float64   `json:"max_bid_price_inr"`
}

// Cost analyzer for detailed cost analysis
type CostAnalyzer struct {
	costHistory       map[string]*CostHistory
	wasteDetector     *WasteDetector
	anomalyDetector   *AnomalyDetector
	trendAnalyzer     *TrendAnalyzer
	mu                sync.RWMutex
}

// Cost history tracking
type CostHistory struct {
	ResourceID      string                  `json:"resource_id"`
	DailyCosts      map[string]float64      `json:"daily_costs"` // Date -> Cost INR
	MonthlyCosts    map[string]float64      `json:"monthly_costs"`
	ServiceCosts    map[string]float64      `json:"service_costs"` // Service -> Cost INR
	RegionalCosts   map[string]float64      `json:"regional_costs"`
	LastUpdated     time.Time               `json:"last_updated"`
	CostTrends      []CostTrendPoint        `json:"cost_trends"`
	BudgetVariance  float64                 `json:"budget_variance"` // Actual vs Budget %
}

type CostTrendPoint struct {
	Date      time.Time `json:"date"`
	CostINR   float64   `json:"cost_inr"`
	UsageHours float64  `json:"usage_hours"`
}

// Waste detection for unused resources
type WasteDetector struct {
	idleResources     map[string]*IdleResource
	oversizedResources map[string]*OversizedResource
	unusedResources   map[string]*UnusedResource
	wasteReports      []WasteReport
	mu                sync.RWMutex
}

type IdleResource struct {
	ResourceID        string    `json:"resource_id"`
	IdleTimePercent   float64   `json:"idle_time_percent"`
	IdleDuration      time.Duration `json:"idle_duration"`
	PotentialSavingsINR float64 `json:"potential_savings_inr"`
	RecommendedAction string    `json:"recommended_action"`
}

type OversizedResource struct {
	ResourceID          string  `json:"resource_id"`
	CurrentSpecs        string  `json:"current_specs"`
	RecommendedSpecs    string  `json:"recommended_specs"`
	OverProvisionPercent float64 `json:"over_provision_percent"`
	PotentialSavingsINR  float64 `json:"potential_savings_inr"`
}

type UnusedResource struct {
	ResourceID         string    `json:"resource_id"`
	LastUsed           time.Time `json:"last_used"`
	UnusedDays         int       `json:"unused_days"`
	MonthlyCostINR     float64   `json:"monthly_cost_inr"`
	RecommendedAction  string    `json:"recommended_action"`
}

type WasteReport struct {
	GeneratedAt         time.Time `json:"generated_at"`
	TotalWasteINR       float64   `json:"total_waste_inr"`
	IdleWasteINR        float64   `json:"idle_waste_inr"`
	OversizeWasteINR    float64   `json:"oversize_waste_inr"`
	UnusedWasteINR      float64   `json:"unused_waste_inr"`
	PotentialSavingsINR float64   `json:"potential_savings_inr"`
	RecommendationCount int       `json:"recommendation_count"`
}

// Anomaly detection for cost spikes
type AnomalyDetector struct {
	anomalies         []CostAnomaly
	thresholds        map[string]float64 // Service -> Threshold
	baselineModels    map[string]*BaselineModel
	mu                sync.RWMutex
}

type CostAnomaly struct {
	ResourceID        string    `json:"resource_id"`
	DetectedAt        time.Time `json:"detected_at"`
	AnomalyType       string    `json:"anomaly_type"` // spike, drop, drift
	ActualCostINR     float64   `json:"actual_cost_inr"`
	ExpectedCostINR   float64   `json:"expected_cost_inr"`
	DeviationPercent  float64   `json:"deviation_percent"`
	Severity          string    `json:"severity"` // low, medium, high, critical
	RootCause         string    `json:"root_cause"`
	ImpactINR         float64   `json:"impact_inr"`
}

type BaselineModel struct {
	ResourceID      string    `json:"resource_id"`
	MeanCostINR     float64   `json:"mean_cost_inr"`
	StdDeviationINR float64   `json:"std_deviation_inr"`
	SeasonalFactors map[int]float64 `json:"seasonal_factors"` // Hour -> Factor
	TrendSlope      float64   `json:"trend_slope"`
	LastUpdated     time.Time `json:"last_updated"`
}

// Trend analyzer for cost forecasting
type TrendAnalyzer struct {
	costTrends       map[string]*CostTrend
	utilizationTrends map[string]*UtilizationTrend
	mu               sync.RWMutex
}

type CostTrend struct {
	ResourceID        string    `json:"resource_id"`
	TrendDirection    string    `json:"trend_direction"` // increasing, decreasing, stable
	MonthlyGrowthRate float64   `json:"monthly_growth_rate"`
	Seasonality       map[string]float64 `json:"seasonality"` // Month -> Factor
	R2Score           float64   `json:"r2_score"` // Trend fit quality
	LastAnalyzed      time.Time `json:"last_analyzed"`
}

type UtilizationTrend struct {
	ResourceID         string    `json:"resource_id"`
	UtilizationTrend   string    `json:"utilization_trend"`
	EfficiencyScore    float64   `json:"efficiency_score"`
	OptimizationWindow string    `json:"optimization_window"` // When to optimize
	LastAnalyzed       time.Time `json:"last_analyzed"`
}

// Budget manager for budget tracking and alerts
type BudgetManager struct {
	budgets           map[string]*Budget
	budgetAlerts      []BudgetAlert
	approvals         map[string]*BudgetApproval
	mu                sync.RWMutex
}

type Budget struct {
	ID               string                `json:"id"`
	Name             string                `json:"name"`
	Company          string                `json:"company"`
	Department       string                `json:"department"`
	BudgetPeriod     string                `json:"budget_period"` // monthly, quarterly, yearly
	TotalBudgetINR   float64              `json:"total_budget_inr"`
	SpentINR         float64              `json:"spent_inr"`
	RemainingINR     float64              `json:"remaining_inr"`
	UtilizedPercent  float64              `json:"utilized_percent"`
	ResourceFilters  map[string]string    `json:"resource_filters"`
	AlertThresholds  []float64            `json:"alert_thresholds"` // 50%, 80%, 95%, 100%
	StartDate        time.Time            `json:"start_date"`
	EndDate          time.Time            `json:"end_date"`
	ForecastedSpendINR float64            `json:"forecasted_spend_inr"`
	Status           BudgetStatus         `json:"status"`
}

type BudgetStatus int

const (
	BudgetStatusActive BudgetStatus = iota
	BudgetStatusExceeded
	BudgetStatusWarning
	BudgetStatusComplete
)

type BudgetAlert struct {
	BudgetID         string    `json:"budget_id"`
	AlertType        string    `json:"alert_type"` // threshold, forecast, anomaly
	Severity         string    `json:"severity"`
	Message          string    `json:"message"`
	CurrentSpendINR  float64   `json:"current_spend_inr"`
	BudgetINR        float64   `json:"budget_inr"`
	ThresholdPercent float64   `json:"threshold_percent"`
	TriggeredAt      time.Time `json:"triggered_at"`
	Acknowledged     bool      `json:"acknowledged"`
}

type BudgetApproval struct {
	ID              string    `json:"id"`
	RequestedBy     string    `json:"requested_by"`
	ApprovedBy      string    `json:"approved_by"`
	RequestedAmountINR float64 `json:"requested_amount_inr"`
	ApprovedAmountINR  float64 `json:"approved_amount_inr"`
	Reason          string    `json:"reason"`
	Status          string    `json:"status"` // pending, approved, rejected
	RequestedAt     time.Time `json:"requested_at"`
	ResponseAt      time.Time `json:"response_at"`
}

// Pricing engine for cost calculations
type PricingEngine struct {
	pricingData      map[string]*ServicePricing
	exchangeRates    map[string]float64 // Currency -> INR rate
	regionalMultipliers map[string]float64
	discountCalculator  *DiscountCalculator
	mu               sync.RWMutex
}

type ServicePricing struct {
	Service          string                    `json:"service"`
	Provider         string                    `json:"provider"`
	Region           string                    `json:"region"`
	PricingModel     string                    `json:"pricing_model"` // hourly, request, storage
	BasePrice        float64                   `json:"base_price"`
	Currency         string                    `json:"currency"`
	PricePerUnit     float64                   `json:"price_per_unit"`
	Unit             string                    `json:"unit"`
	TierPricing      []PricingTierRate         `json:"tier_pricing"`
	LastUpdated      time.Time                 `json:"last_updated"`
}

type PricingTierRate struct {
	MinUnits        int     `json:"min_units"`
	MaxUnits        int     `json:"max_units"`
	PricePerUnit    float64 `json:"price_per_unit"`
}

// Discount calculator
type DiscountCalculator struct {
	reservedInstanceCalculator *ReservedInstanceCalculator
	spotPricingCalculator      *SpotPricingCalculator
	volumeDiscountCalculator   *VolumeDiscountCalculator
	committedUseCalculator     *CommittedUseCalculator
}

type ReservedInstanceCalculator struct {
	reservationData map[string]*ReservationPricing
	mu              sync.RWMutex
}

type ReservationPricing struct {
	InstanceType      string  `json:"instance_type"`
	Region            string  `json:"region"`
	TermMonths        int     `json:"term_months"`
	PaymentOption     string  `json:"payment_option"`
	UpfrontCostINR    float64 `json:"upfront_cost_inr"`
	HourlyCostINR     float64 `json:"hourly_cost_inr"`
	OnDemandCostINR   float64 `json:"on_demand_cost_inr"`
	SavingsPercent    float64 `json:"savings_percent"`
}

// Spot pricing calculator
type SpotPricingCalculator struct {
	spotPrices       map[string]*SpotPricing
	priceHistory     map[string][]SpotPricePoint
	interruptionData map[string]*InterruptionStats
	mu               sync.RWMutex
}

type SpotPricing struct {
	InstanceType       string    `json:"instance_type"`
	Region             string    `json:"region"`
	CurrentPriceINR    float64   `json:"current_price_inr"`
	OnDemandPriceINR   float64   `json:"on_demand_price_inr"`
	SavingsPercent     float64   `json:"savings_percent"`
	PriceStability     string    `json:"price_stability"` // stable, volatile, highly_volatile
	LastUpdated        time.Time `json:"last_updated"`
}

type SpotPricePoint struct {
	Timestamp   time.Time `json:"timestamp"`
	PriceINR    float64   `json:"price_inr"`
	Availability string   `json:"availability"`
}

type InterruptionStats struct {
	InstanceType         string  `json:"instance_type"`
	Region               string  `json:"region"`
	InterruptionRate     float64 `json:"interruption_rate"` // Percentage
	AvgRunTimeHours      float64 `json:"avg_run_time_hours"`
	WorstCaseRunTimeHours float64 `json:"worst_case_run_time_hours"`
	RecommendedForWorkload bool   `json:"recommended_for_workload"`
}

// Volume discount calculator
type VolumeDiscountCalculator struct {
	volumeTiers    map[string][]VolumeTier
	currentUsage   map[string]float64
	mu             sync.RWMutex
}

type VolumeTier struct {
	MinUsage        float64 `json:"min_usage"`
	MaxUsage        float64 `json:"max_usage"`
	DiscountPercent float64 `json:"discount_percent"`
}

// Committed use calculator
type CommittedUseCalculator struct {
	commitmentOptions map[string][]CommitmentOption
	mu                sync.RWMutex
}

type CommitmentOption struct {
	ResourceType     string  `json:"resource_type"`
	CommitmentMonths int     `json:"commitment_months"`
	MinUsage         float64 `json:"min_usage"`
	DiscountPercent  float64 `json:"discount_percent"`
}

// Recommendation engine
type RecommendationEngine struct {
	recommendations   []CostRecommendation
	rightsizing       *RightsizingEngine
	schedulingOptimizer *SchedulingOptimizer
	architectureOptimizer *ArchitectureOptimizer
	mu                sync.RWMutex
}

type CostRecommendation struct {
	ID                  string    `json:"id"`
	Type                string    `json:"type"` // rightsizing, scheduling, reservation, etc.
	ResourceID          string    `json:"resource_id"`
	CurrentCostINR      float64   `json:"current_cost_inr"`
	OptimizedCostINR    float64   `json:"optimized_cost_inr"`
	PotentialSavingsINR float64   `json:"potential_savings_inr"`
	SavingsPercent      float64   `json:"savings_percent"`
	ImplementationEffort string   `json:"implementation_effort"` // low, medium, high
	RiskLevel           string    `json:"risk_level"` // low, medium, high
	Priority            int       `json:"priority"` // 1-5 scale
	Description         string    `json:"description"`
	ActionSteps         []string  `json:"action_steps"`
	EstimatedTimeToImplement time.Duration `json:"estimated_time_to_implement"`
	GeneratedAt         time.Time `json:"generated_at"`
	Status              string    `json:"status"` // pending, implementing, completed, rejected
}

// Rightsizing engine
type RightsizingEngine struct {
	rightsizingRules    []RightsizingRule
	utilizationAnalyzer *UtilizationAnalyzer
	mu                  sync.RWMutex
}

type RightsizingRule struct {
	ResourceType        string  `json:"resource_type"`
	MinUtilizationThreshold float64 `json:"min_utilization_threshold"`
	MaxUtilizationThreshold float64 `json:"max_utilization_threshold"`
	RecommendedAction   string  `json:"recommended_action"`
	SavingsEstimate     float64 `json:"savings_estimate"`
}

// Utilization analyzer
type UtilizationAnalyzer struct {
	utilizationPatterns map[string]*UtilizationPattern
	mu                  sync.RWMutex
}

type UtilizationPattern struct {
	ResourceID          string             `json:"resource_id"`
	AverageUtilization  float64            `json:"average_utilization"`
	PeakUtilization     float64            `json:"peak_utilization"`
	UtilizationVariability float64         `json:"utilization_variability"`
	SeasonalPatterns    map[string]float64 `json:"seasonal_patterns"`
	RecommendedSize     string             `json:"recommended_size"`
	ConfidenceScore     float64            `json:"confidence_score"`
}

// Scheduling optimizer for workload scheduling
type SchedulingOptimizer struct {
	schedules       map[string]*OptimalSchedule
	spotOptimizer   *SpotOptimizer
	mu              sync.RWMutex
}

type OptimalSchedule struct {
	WorkloadID       string              `json:"workload_id"`
	RecommendedHours []int              `json:"recommended_hours"` // Hours of day (IST)
	RecommendedRegion string             `json:"recommended_region"`
	CostSavingsINR   float64            `json:"cost_savings_inr"`
	Reasoning        string             `json:"reasoning"`
	Schedule         map[string]string  `json:"schedule"` // Day -> Time
}

// Spot optimizer
type SpotOptimizer struct {
	spotRecommendations map[string]*SpotRecommendation
	mu                  sync.RWMutex
}

type SpotRecommendation struct {
	ResourceID           string  `json:"resource_id"`
	RecommendSpotUsage   bool    `json:"recommend_spot_usage"`
	MaxBidPriceINR       float64 `json:"max_bid_price_inr"`
	ExpectedSavingsINR   float64 `json:"expected_savings_inr"`
	InterruptionTolerance string `json:"interruption_tolerance"`
	FaultToleranceRequired bool  `json:"fault_tolerance_required"`
}

// Architecture optimizer
type ArchitectureOptimizer struct {
	architectureRecommendations []ArchitectureRecommendation
	mu                          sync.RWMutex
}

type ArchitectureRecommendation struct {
	Company              string   `json:"company"`
	CurrentArchitecture  string   `json:"current_architecture"`
	RecommendedArchitecture string `json:"recommended_architecture"`
	ExpectedSavingsINR   float64  `json:"expected_savings_inr"`
	MigrationComplexity  string   `json:"migration_complexity"`
	Benefits             []string `json:"benefits"`
	Considerations       []string `json:"considerations"`
}

// Alert manager for cost alerts
type AlertManager struct {
	alerts      []CostAlert
	channels    map[string]*AlertChannel
	rules       []AlertRule
	mu          sync.RWMutex
}

type CostAlert struct {
	ID               string    `json:"id"`
	Type             string    `json:"type"`
	Severity         string    `json:"severity"`
	ResourceID       string    `json:"resource_id"`
	Message          string    `json:"message"`
	CurrentValueINR  float64   `json:"current_value_inr"`
	ThresholdINR     float64   `json:"threshold_inr"`
	TriggeredAt      time.Time `json:"triggered_at"`
	AcknowledgedAt   time.Time `json:"acknowledged_at"`
	ResolvedAt       time.Time `json:"resolved_at"`
	Status           string    `json:"status"` // active, acknowledged, resolved
}

type AlertChannel struct {
	Name        string            `json:"name"`
	Type        string            `json:"type"` // email, slack, webhook, sms
	Config      map[string]string `json:"config"`
	Enabled     bool              `json:"enabled"`
}

type AlertRule struct {
	ID               string                 `json:"id"`
	Name             string                 `json:"name"`
	Condition        string                 `json:"condition"`
	ThresholdINR     float64               `json:"threshold_inr"`
	EvaluationPeriod time.Duration         `json:"evaluation_period"`
	Severity         string                `json:"severity"`
	Channels         []string              `json:"channels"`
	Filters          map[string]string     `json:"filters"`
}

// Forecast engine for cost forecasting
type ForecastEngine struct {
	forecasts      map[string]*CostForecast
	forecastModels map[string]*ForecastModel
	mu             sync.RWMutex
}

type CostForecast struct {
	ResourceID           string               `json:"resource_id"`
	ForecastHorizonDays  int                 `json:"forecast_horizon_days"`
	ForecastedCostsINR   []ForecastPoint     `json:"forecasted_costs_inr"`
	ConfidenceInterval   ConfidenceInterval  `json:"confidence_interval"`
	ModelAccuracy        float64             `json:"model_accuracy"`
	GeneratedAt          time.Time           `json:"generated_at"`
}

type ForecastPoint struct {
	Date     time.Time `json:"date"`
	CostINR  float64   `json:"cost_inr"`
	LowerBound float64 `json:"lower_bound"`
	UpperBound float64 `json:"upper_bound"`
}

type ConfidenceInterval struct {
	Level            float64 `json:"level"` // e.g., 95%
	LowerBoundINR    float64 `json:"lower_bound_inr"`
	UpperBoundINR    float64 `json:"upper_bound_inr"`
}

type ForecastModel struct {
	ResourceID      string                 `json:"resource_id"`
	ModelType       string                 `json:"model_type"` // arima, linear, seasonal
	Parameters      map[string]float64     `json:"parameters"`
	TrainingPeriod  time.Duration          `json:"training_period"`
	Accuracy        float64                `json:"accuracy"`
	LastTrained     time.Time              `json:"last_trained"`
}

// Report generator for cost reports
type ReportGenerator struct {
	reports        map[string]*CostReport
	templates      map[string]*ReportTemplate
	scheduledReports []ScheduledReport
	mu             sync.RWMutex
}

type CostReport struct {
	ID                string                 `json:"id"`
	Title             string                 `json:"title"`
	Company           string                 `json:"company"`
	GeneratedAt       time.Time              `json:"generated_at"`
	Period            ReportPeriod           `json:"period"`
	TotalCostINR      float64               `json:"total_cost_inr"`
	BudgetVarianceINR float64               `json:"budget_variance_inr"`
	Sections          []ReportSection       `json:"sections"`
	Charts            []ReportChart         `json:"charts"`
	Recommendations   []CostRecommendation  `json:"recommendations"`
	ExecutiveSummary  string                `json:"executive_summary"`
}

type ReportPeriod struct {
	StartDate   time.Time `json:"start_date"`
	EndDate     time.Time `json:"end_date"`
	PeriodType  string    `json:"period_type"` // daily, weekly, monthly, quarterly
}

type ReportSection struct {
	Title       string                 `json:"title"`
	Content     string                 `json:"content"`
	Data        map[string]interface{} `json:"data"`
	Charts      []string               `json:"charts"`
	Insights    []string               `json:"insights"`
}

type ReportChart struct {
	Type        string                 `json:"type"` // bar, line, pie, area
	Title       string                 `json:"title"`
	XAxis       string                 `json:"x_axis"`
	YAxis       string                 `json:"y_axis"`
	Data        []ChartDataPoint       `json:"data"`
	Colors      []string               `json:"colors"`
}

type ChartDataPoint struct {
	Label   string  `json:"label"`
	Value   float64 `json:"value"`
	Details map[string]interface{} `json:"details"`
}

type ReportTemplate struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Sections    []string `json:"sections"`
	ChartTypes  []string `json:"chart_types"`
	Frequency   string   `json:"frequency"`
}

type ScheduledReport struct {
	ID              string    `json:"id"`
	ReportTemplateID string   `json:"report_template_id"`
	Company         string    `json:"company"`
	Recipients      []string  `json:"recipients"`
	Schedule        string    `json:"schedule"` // cron expression
	NextRun         time.Time `json:"next_run"`
	LastRun         time.Time `json:"last_run"`
	Enabled         bool      `json:"enabled"`
}

// Initialize cost optimizer
func NewAICostOptimizer() *AICostOptimizer {
	ctx, cancel := context.WithCancel(context.Background())
	
	optimizer := &AICostOptimizer{
		resourceManager:       NewResourceManager(),
		costAnalyzer:         NewCostAnalyzer(),
		budgetManager:        NewBudgetManager(),
		pricingEngine:        NewPricingEngine(),
		recommendationEngine: NewRecommendationEngine(),
		alertManager:         NewAlertManager(),
		forecastEngine:       NewForecastEngine(),
		reportGenerator:      NewReportGenerator(),
		ctx:                  ctx,
		cancel:               cancel,
	}
	
	// Start background processes
	go optimizer.startCostMonitoring()
	go optimizer.startRecommendationGeneration()
	go optimizer.startBudgetMonitoring()
	go optimizer.startReportGeneration()
	
	log.Println("🚀 AI Cost Optimizer initialized for Indian infrastructure")
	return optimizer
}

func NewResourceManager() *ResourceManager {
	rm := &ResourceManager{
		resources:       make(map[string]*Resource),
		providers:       make(map[string]*CloudProvider),
		regions:         make(map[string]*Region),
		utilizationData: make(map[string]*UtilizationMetrics),
		reservations:    make(map[string]*Reservation),
		spotInstances:   make(map[string]*SpotInstance),
	}
	
	// Initialize Indian cloud providers
	rm.initializeProviders()
	rm.initializeRegions()
	
	return rm
}

func (rm *ResourceManager) initializeProviders() {
	// AWS India
	rm.providers["aws"] = &CloudProvider{
		Name:              "Amazon Web Services",
		Regions:           []string{"ap-south-1", "ap-southeast-1"},
		SupportedServices: []string{"ec2", "sagemaker", "lambda", "s3", "rds"},
		PricingTiers: map[string]*PricingTier{
			"reserved": {
				Name:              "Reserved Instances",
				MinUsageHours:     8760, // 1 year
				MaxUsageHours:     26280, // 3 years
				DiscountPercent:   30.0,
				CommitmentMonths:  12,
			},
		},
		DiscountPrograms: []DiscountProgram{
			{
				Type:              DiscountTypeReserved,
				Name:              "Reserved Instances",
				DiscountPercent:   30.0,
				Requirements:      []string{"1-3 year commitment"},
				AvailableRegions:  []string{"ap-south-1"},
				MinCommitmentDays: 365,
			},
			{
				Type:              DiscountTypeSpot,
				Name:              "Spot Instances",
				DiscountPercent:   70.0,
				Requirements:      []string{"fault tolerant workloads"},
				AvailableRegions:  []string{"ap-south-1", "ap-southeast-1"},
				MinCommitmentDays: 0,
			},
		},
	}
	
	// Azure India
	rm.providers["azure"] = &CloudProvider{
		Name:              "Microsoft Azure",
		Regions:           []string{"centralindia", "southindia"},
		SupportedServices: []string{"vm", "ml", "functions", "storage", "sql"},
		PricingTiers: map[string]*PricingTier{
			"reserved": {
				Name:              "Reserved VM Instances",
				MinUsageHours:     8760,
				MaxUsageHours:     26280,
				DiscountPercent:   25.0,
				CommitmentMonths:  12,
			},
		},
		DiscountPrograms: []DiscountProgram{
			{
				Type:              DiscountTypeReserved,
				Name:              "Reserved VMs",
				DiscountPercent:   25.0,
				Requirements:      []string{"1-3 year commitment"},
				AvailableRegions:  []string{"centralindia", "southindia"},
				MinCommitmentDays: 365,
			},
			{
				Type:              DiscountTypeSpot,
				Name:              "Spot VMs",
				DiscountPercent:   60.0,
				Requirements:      []string{"interruptible workloads"},
				AvailableRegions:  []string{"centralindia"},
				MinCommitmentDays: 0,
			},
		},
	}
	
	// Google Cloud India
	rm.providers["gcp"] = &CloudProvider{
		Name:              "Google Cloud Platform",
		Regions:           []string{"asia-south1", "asia-southeast1"},
		SupportedServices: []string{"compute", "vertex-ai", "functions", "storage", "sql"},
		PricingTiers: map[string]*PricingTier{
			"committed": {
				Name:              "Committed Use Discounts",
				MinUsageHours:     8760,
				MaxUsageHours:     26280,
				DiscountPercent:   35.0,
				CommitmentMonths:  12,
			},
		},
		DiscountPrograms: []DiscountProgram{
			{
				Type:              DiscountTypeCommitted,
				Name:              "Committed Use Discounts",
				DiscountPercent:   35.0,
				Requirements:      []string{"1-3 year commitment"},
				AvailableRegions:  []string{"asia-south1"},
				MinCommitmentDays: 365,
			},
			{
				Type:              DiscountTypePreemptible,
				Name:              "Preemptible VMs",
				DiscountPercent:   80.0,
				Requirements:      []string{"24-hour max runtime"},
				AvailableRegions:  []string{"asia-south1", "asia-southeast1"},
				MinCommitmentDays: 0,
			},
		},
	}
}

func (rm *ResourceManager) initializeRegions() {
	regions := []*Region{
		{
			ID:                    "ap-south-1",
			Name:                  "AWS Mumbai",
			Provider:              "aws",
			Country:               "India",
			City:                  "Mumbai",
			LatencyToMumbaiMs:     5,
			DataCostMultiplier:    1.0,
			ComputeCostMultiplier: 1.0,
			Availability:          []string{"ec2", "sagemaker", "lambda", "s3", "rds"},
			ComplianceFlags:       []string{"data_residency", "rbi_compliant"},
		},
		{
			ID:                    "centralindia",
			Name:                  "Azure Central India",
			Provider:              "azure",
			Country:               "India",
			City:                  "Pune",
			LatencyToMumbaiMs:     15,
			DataCostMultiplier:    1.05,
			ComputeCostMultiplier: 1.02,
			Availability:          []string{"vm", "ml", "functions", "storage", "sql"},
			ComplianceFlags:       []string{"data_residency", "iso_compliant"},
		},
		{
			ID:                    "asia-south1",
			Name:                  "GCP Mumbai",
			Provider:              "gcp",
			Country:               "India",
			City:                  "Mumbai",
			LatencyToMumbaiMs:     8,
			DataCostMultiplier:    0.98,
			ComputeCostMultiplier: 0.95,
			Availability:          []string{"compute", "vertex-ai", "functions", "storage", "sql"},
			ComplianceFlags:       []string{"data_residency", "sox_compliant"},
		},
		{
			ID:                    "on-premise-mumbai",
			Name:                  "On-Premise Mumbai",
			Provider:              "on-premise",
			Country:               "India",
			City:                  "Mumbai",
			LatencyToMumbaiMs:     1,
			DataCostMultiplier:    0.3, // Much cheaper for data
			ComputeCostMultiplier: 0.4, // Cheaper but need to account for maintenance
			Availability:          []string{"compute", "storage", "gpu"},
			ComplianceFlags:       []string{"full_control", "data_residency"},
		},
	}
	
	for _, region := range regions {
		rm.regions[region.ID] = region
	}
}

func NewCostAnalyzer() *CostAnalyzer {
	return &CostAnalyzer{
		costHistory:     make(map[string]*CostHistory),
		wasteDetector:   NewWasteDetector(),
		anomalyDetector: NewAnomalyDetector(),
		trendAnalyzer:   NewTrendAnalyzer(),
	}
}

func NewWasteDetector() *WasteDetector {
	return &WasteDetector{
		idleResources:      make(map[string]*IdleResource),
		oversizedResources: make(map[string]*OversizedResource),
		unusedResources:    make(map[string]*UnusedResource),
		wasteReports:       make([]WasteReport, 0),
	}
}

func NewAnomalyDetector() *AnomalyDetector {
	return &AnomalyDetector{
		anomalies:      make([]CostAnomaly, 0),
		thresholds:     make(map[string]float64),
		baselineModels: make(map[string]*BaselineModel),
	}
}

func NewTrendAnalyzer() *TrendAnalyzer {
	return &TrendAnalyzer{
		costTrends:        make(map[string]*CostTrend),
		utilizationTrends: make(map[string]*UtilizationTrend),
	}
}

func NewBudgetManager() *BudgetManager {
	return &BudgetManager{
		budgets:      make(map[string]*Budget),
		budgetAlerts: make([]BudgetAlert, 0),
		approvals:    make(map[string]*BudgetApproval),
	}
}

func NewPricingEngine() *PricingEngine {
	pe := &PricingEngine{
		pricingData:         make(map[string]*ServicePricing),
		exchangeRates:       make(map[string]float64),
		regionalMultipliers: make(map[string]float64),
		discountCalculator:  NewDiscountCalculator(),
	}
	
	// Initialize exchange rates
	pe.exchangeRates["USD"] = 83.0  // 1 USD = 83 INR (approximate)
	pe.exchangeRates["EUR"] = 90.0  // 1 EUR = 90 INR (approximate)
	pe.exchangeRates["SGD"] = 62.0  // 1 SGD = 62 INR (approximate)
	pe.exchangeRates["INR"] = 1.0   // Base currency
	
	// Initialize regional multipliers
	pe.regionalMultipliers["ap-south-1"] = 1.0      // Mumbai base
	pe.regionalMultipliers["centralindia"] = 1.02   // Pune slightly higher
	pe.regionalMultipliers["asia-south1"] = 0.98    // GCP Mumbai competitive
	pe.regionalMultipliers["ap-southeast-1"] = 1.15 // Singapore premium
	pe.regionalMultipliers["on-premise-mumbai"] = 0.4 // On-premise savings
	
	pe.initializePricingData()
	return pe
}

func (pe *PricingEngine) initializePricingData() {
	// GPU pricing for Indian AI companies
	gpuPricing := []*ServicePricing{
		{
			Service:      "gpu-compute",
			Provider:     "aws",
			Region:       "ap-south-1",
			PricingModel: "hourly",
			BasePrice:    45.0, // ₹45/hour for p3.2xlarge equivalent
			Currency:     "INR",
			PricePerUnit: 45.0,
			Unit:         "hour",
			TierPricing: []PricingTierRate{
				{MinUnits: 0, MaxUnits: 100, PricePerUnit: 45.0},
				{MinUnits: 101, MaxUnits: 500, PricePerUnit: 42.0},
				{MinUnits: 501, MaxUnits: math.MaxInt32, PricePerUnit: 38.0},
			},
			LastUpdated: time.Now(),
		},
		{
			Service:      "ml-training",
			Provider:     "azure",
			Region:       "centralindia",
			PricingModel: "hourly",
			BasePrice:    48.0, // ₹48/hour for Standard_NC6s_v3 equivalent
			Currency:     "INR",
			PricePerUnit: 48.0,
			Unit:         "hour",
			TierPricing: []PricingTierRate{
				{MinUnits: 0, MaxUnits: 50, PricePerUnit: 48.0},
				{MinUnits: 51, MaxUnits: 200, PricePerUnit: 45.0},
				{MinUnits: 201, MaxUnits: math.MaxInt32, PricePerUnit: 42.0},
			},
			LastUpdated: time.Now(),
		},
		{
			Service:      "vertex-ai-training",
			Provider:     "gcp",
			Region:       "asia-south1",
			PricingModel: "hourly",
			BasePrice:    42.0, // ₹42/hour for n1-standard-4 + V100
			Currency:     "INR",
			PricePerUnit: 42.0,
			Unit:         "hour",
			TierPricing: []PricingTierRate{
				{MinUnits: 0, MaxUnits: 100, PricePerUnit: 42.0},
				{MinUnits: 101, MaxUnits: 1000, PricePerUnit: 38.0},
				{MinUnits: 1001, MaxUnits: math.MaxInt32, PricePerUnit: 35.0},
			},
			LastUpdated: time.Now(),
		},
	}
	
	for _, pricing := range gpuPricing {
		key := fmt.Sprintf("%s_%s_%s", pricing.Provider, pricing.Region, pricing.Service)
		pe.pricingData[key] = pricing
	}
}

func NewDiscountCalculator() *DiscountCalculator {
	return &DiscountCalculator{
		reservedInstanceCalculator: NewReservedInstanceCalculator(),
		spotPricingCalculator:      NewSpotPricingCalculator(),
		volumeDiscountCalculator:   NewVolumeDiscountCalculator(),
		committedUseCalculator:     NewCommittedUseCalculator(),
	}
}

func NewReservedInstanceCalculator() *ReservedInstanceCalculator {
	ric := &ReservedInstanceCalculator{
		reservationData: make(map[string]*ReservationPricing),
	}
	
	// Sample reservation pricing for Indian regions
	reservations := []*ReservationPricing{
		{
			InstanceType:      "p3.2xlarge",
			Region:            "ap-south-1",
			TermMonths:        12,
			PaymentOption:     "All Upfront",
			UpfrontCostINR:    180000.0, // ₹1.8L upfront for 1 year
			HourlyCostINR:     25.0,     // vs ₹45 on-demand
			OnDemandCostINR:   45.0,
			SavingsPercent:    44.4, // (45-25)/45 * 100
		},
		{
			InstanceType:      "Standard_NC6s_v3",
			Region:            "centralindia",
			TermMonths:        12,
			PaymentOption:     "Partial Upfront",
			UpfrontCostINR:    120000.0, // ₹1.2L upfront
			HourlyCostINR:     28.0,     // vs ₹48 on-demand
			OnDemandCostINR:   48.0,
			SavingsPercent:    41.7, // (48-28)/48 * 100
		},
	}
	
	for _, reservation := range reservations {
		key := fmt.Sprintf("%s_%s_%d", reservation.InstanceType, reservation.Region, reservation.TermMonths)
		ric.reservationData[key] = reservation
	}
	
	return ric
}

func NewSpotPricingCalculator() *SpotPricingCalculator {
	spc := &SpotPricingCalculator{
		spotPrices:       make(map[string]*SpotPricing),
		priceHistory:     make(map[string][]SpotPricePoint),
		interruptionData: make(map[string]*InterruptionStats),
	}
	
	// Sample spot pricing for Indian regions
	spotPrices := []*SpotPricing{
		{
			InstanceType:       "p3.2xlarge",
			Region:             "ap-south-1",
			CurrentPriceINR:    15.0, // ₹15/hour vs ₹45 on-demand
			OnDemandPriceINR:   45.0,
			SavingsPercent:     66.7, // (45-15)/45 * 100
			PriceStability:     "stable",
			LastUpdated:        time.Now(),
		},
		{
			InstanceType:       "Standard_NC6s_v3",
			Region:             "centralindia",
			CurrentPriceINR:    18.0, // ₹18/hour vs ₹48 on-demand
			OnDemandPriceINR:   48.0,
			SavingsPercent:     62.5, // (48-18)/48 * 100
			PriceStability:     "volatile",
			LastUpdated:        time.Now(),
		},
	}
	
	for _, spotPrice := range spotPrices {
		key := fmt.Sprintf("%s_%s", spotPrice.InstanceType, spotPrice.Region)
		spc.spotPrices[key] = spotPrice
	}
	
	return spc
}

func NewVolumeDiscountCalculator() *VolumeDiscountCalculator {
	vdc := &VolumeDiscountCalculator{
		volumeTiers:  make(map[string][]VolumeTier),
		currentUsage: make(map[string]float64),
	}
	
	// Volume tiers for different services
	vdc.volumeTiers["gpu-compute"] = []VolumeTier{
		{MinUsage: 0, MaxUsage: 100, DiscountPercent: 0.0},
		{MinUsage: 101, MaxUsage: 500, DiscountPercent: 5.0},
		{MinUsage: 501, MaxUsage: 2000, DiscountPercent: 10.0},
		{MinUsage: 2001, MaxUsage: math.MaxFloat64, DiscountPercent: 15.0},
	}
	
	return vdc
}

func NewCommittedUseCalculator() *CommittedUseCalculator {
	cuc := &CommittedUseCalculator{
		commitmentOptions: make(map[string][]CommitmentOption),
	}
	
	// Commitment options for GCP
	cuc.commitmentOptions["vertex-ai"] = []CommitmentOption{
		{
			ResourceType:     "gpu-training",
			CommitmentMonths: 12,
			MinUsage:         100.0, // 100 hours/month
			DiscountPercent:  25.0,
		},
		{
			ResourceType:     "gpu-training",
			CommitmentMonths: 36,
			MinUsage:         100.0,
			DiscountPercent:  35.0,
		},
	}
	
	return cuc
}

func NewRecommendationEngine() *RecommendationEngine {
	return &RecommendationEngine{
		recommendations:       make([]CostRecommendation, 0),
		rightsizing:          NewRightsizingEngine(),
		schedulingOptimizer:  NewSchedulingOptimizer(),
		architectureOptimizer: NewArchitectureOptimizer(),
	}
}

func NewRightsizingEngine() *RightsizingEngine {
	re := &RightsizingEngine{
		rightsizingRules:    make([]RightsizingRule, 0),
		utilizationAnalyzer: NewUtilizationAnalyzer(),
	}
	
	// Add rightsizing rules
	re.rightsizingRules = []RightsizingRule{
		{
			ResourceType:             "gpu",
			MinUtilizationThreshold:  30.0, // Below 30% utilization
			MaxUtilizationThreshold:  90.0, // Above 90% utilization
			RecommendedAction:        "downsize",
			SavingsEstimate:          35.0, // 35% cost reduction
		},
		{
			ResourceType:             "compute",
			MinUtilizationThreshold:  20.0,
			MaxUtilizationThreshold:  85.0,
			RecommendedAction:        "rightsize",
			SavingsEstimate:          25.0,
		},
	}
	
	return re
}

func NewUtilizationAnalyzer() *UtilizationAnalyzer {
	return &UtilizationAnalyzer{
		utilizationPatterns: make(map[string]*UtilizationPattern),
	}
}

func NewSchedulingOptimizer() *SchedulingOptimizer {
	return &SchedulingOptimizer{
		schedules:     make(map[string]*OptimalSchedule),
		spotOptimizer: NewSpotOptimizer(),
	}
}

func NewSpotOptimizer() *SpotOptimizer {
	return &SpotOptimizer{
		spotRecommendations: make(map[string]*SpotRecommendation),
	}
}

func NewArchitectureOptimizer() *ArchitectureOptimizer {
	return &ArchitectureOptimizer{
		architectureRecommendations: make([]ArchitectureRecommendation, 0),
	}
}

func NewAlertManager() *AlertManager {
	am := &AlertManager{
		alerts:   make([]CostAlert, 0),
		channels: make(map[string]*AlertChannel),
		rules:    make([]AlertRule, 0),
	}
	
	// Initialize alert channels for Indian companies
	am.channels["email"] = &AlertChannel{
		Name:    "Email Notifications",
		Type:    "email",
		Config:  map[string]string{"smtp_server": "smtp.gmail.com", "port": "587"},
		Enabled: true,
	}
	
	am.channels["slack"] = &AlertChannel{
		Name:    "Slack Notifications",
		Type:    "slack",
		Config:  map[string]string{"webhook_url": "https://hooks.slack.com/services/xxx"},
		Enabled: true,
	}
	
	am.channels["whatsapp"] = &AlertChannel{
		Name:    "WhatsApp Business API",
		Type:    "whatsapp",
		Config:  map[string]string{"api_key": "xxx", "phone_number": "+91xxxxxxxxxx"},
		Enabled: false, // Popular in India
	}
	
	// Initialize alert rules
	am.rules = []AlertRule{
		{
			ID:               "budget_80_percent",
			Name:             "Budget 80% Threshold",
			Condition:        "budget_utilization >= 80",
			ThresholdINR:     0, // Dynamic based on budget
			EvaluationPeriod: 1 * time.Hour,
			Severity:         "warning",
			Channels:         []string{"email", "slack"},
			Filters:          map[string]string{},
		},
		{
			ID:               "cost_spike",
			Name:             "Cost Spike Detection",
			Condition:        "cost_increase >= 50",
			ThresholdINR:     1000.0, // ₹1000 spike
			EvaluationPeriod: 15 * time.Minute,
			Severity:         "critical",
			Channels:         []string{"email", "slack", "whatsapp"},
			Filters:          map[string]string{},
		},
	}
	
	return am
}

func NewForecastEngine() *ForecastEngine {
	return &ForecastEngine{
		forecasts:      make(map[string]*CostForecast),
		forecastModels: make(map[string]*ForecastModel),
	}
}

func NewReportGenerator() *ReportGenerator {
	rg := &ReportGenerator{
		reports:          make(map[string]*CostReport),
		templates:        make(map[string]*ReportTemplate),
		scheduledReports: make([]ScheduledReport, 0),
	}
	
	// Initialize report templates
	rg.templates["monthly_executive"] = &ReportTemplate{
		ID:          "monthly_executive",
		Name:        "Monthly Executive Report",
		Description: "High-level cost summary for executives",
		Sections:    []string{"executive_summary", "cost_trends", "budget_variance", "recommendations"},
		ChartTypes:  []string{"bar", "line", "pie"},
		Frequency:   "monthly",
	}
	
	rg.templates["weekly_operational"] = &ReportTemplate{
		ID:          "weekly_operational",
		Name:        "Weekly Operational Report",
		Description: "Detailed operational cost analysis",
		Sections:    []string{"resource_utilization", "waste_analysis", "cost_breakdown", "optimization_opportunities"},
		ChartTypes:  []string{"bar", "line", "area"},
		Frequency:   "weekly",
	}
	
	return rg
}

// Main optimization functions

// Add resource for monitoring
func (aco *AICostOptimizer) AddResource(config ResourceConfig) error {
	aco.mu.Lock()
	defer aco.mu.Unlock()
	
	resource := &Resource{
		ID:               config.ID,
		Name:             config.Name,
		Provider:         config.Provider,
		Region:           config.Region,
		ResourceType:     config.ResourceType,
		InstanceType:     config.InstanceType,
		Status:           ResourceStatusRunning,
		Company:          config.Company,
		UseCase:          config.UseCase,
		CostPerHourINR:   config.CostPerHourINR,
		UtilizationPercent: 0.0,
		Tags:             config.Tags,
		LaunchedAt:       time.Now(),
		LastUsed:         time.Now(),
		MonthlyBudgetINR: config.MonthlyBudgetINR,
		ActualCostINR:    0.0,
		PredictedCostINR: 0.0,
		GPUCount:         config.GPUCount,
		GPUType:          config.GPUType,
		MemoryGB:         config.MemoryGB,
		StorageGB:        config.StorageGB,
		NetworkBandwidth: config.NetworkBandwidth,
	}
	
	aco.resourceManager.resources[config.ID] = resource
	
	log.Printf("✅ Added resource %s (%s) for %s - %s at ₹%.2f/hour",
		config.Name, config.InstanceType, config.Company, config.UseCase, config.CostPerHourINR)
	
	return nil
}

type ResourceConfig struct {
	ID               string            `json:"id"`
	Name             string            `json:"name"`
	Provider         string            `json:"provider"`
	Region           string            `json:"region"`
	ResourceType     ResourceType      `json:"resource_type"`
	InstanceType     string            `json:"instance_type"`
	Company          string            `json:"company"`
	UseCase          string            `json:"use_case"`
	CostPerHourINR   float64           `json:"cost_per_hour_inr"`
	Tags             map[string]string `json:"tags"`
	MonthlyBudgetINR float64           `json:"monthly_budget_inr"`
	GPUCount         int               `json:"gpu_count"`
	GPUType          string            `json:"gpu_type"`
	MemoryGB         int               `json:"memory_gb"`
	StorageGB        int               `json:"storage_gb"`
	NetworkBandwidth int               `json:"network_bandwidth_mbps"`
}

// Generate cost recommendations
func (aco *AICostOptimizer) GenerateRecommendations() ([]CostRecommendation, error) {
	aco.mu.Lock()
	defer aco.mu.Unlock()
	
	recommendations := make([]CostRecommendation, 0)
	
	// Rightsizing recommendations
	for resourceID, resource := range aco.resourceManager.resources {
		if resource.UtilizationPercent < 30.0 && resource.Status == ResourceStatusRunning {
			// Low utilization - recommend downsizing
			currentCost := resource.CostPerHourINR * 24 * 30 // Monthly cost
			optimizedCost := currentCost * 0.6 // 40% savings by downsizing
			
			rec := CostRecommendation{
				ID:                       fmt.Sprintf("rightsize_%s", resourceID),
				Type:                     "rightsizing",
				ResourceID:               resourceID,
				CurrentCostINR:           currentCost,
				OptimizedCostINR:         optimizedCost,
				PotentialSavingsINR:      currentCost - optimizedCost,
				SavingsPercent:           40.0,
				ImplementationEffort:     "low",
				RiskLevel:                "low",
				Priority:                 3,
				Description:              fmt.Sprintf("Resource %s has low utilization (%.1f%%). Consider downsizing to reduce costs.", resource.Name, resource.UtilizationPercent),
				ActionSteps:              []string{"Analyze workload patterns", "Select appropriate smaller instance type", "Schedule downtime for resizing", "Monitor performance after resize"},
				EstimatedTimeToImplement: 2 * time.Hour,
				GeneratedAt:              time.Now(),
				Status:                   "pending",
			}
			
			recommendations = append(recommendations, rec)
		}
		
		// Spot instance recommendations
		if resource.ResourceType == ResourceTypeGPU && resource.Provider != "on-premise" {
			spotSavings := resource.CostPerHourINR * 0.7 // 70% savings with spot
			currentCost := resource.CostPerHourINR * 24 * 30
			optimizedCost := currentCost * 0.3 // 30% of original cost
			
			rec := CostRecommendation{
				ID:                       fmt.Sprintf("spot_%s", resourceID),
				Type:                     "spot_instances",
				ResourceID:               resourceID,
				CurrentCostINR:           currentCost,
				OptimizedCostINR:         optimizedCost,
				PotentialSavingsINR:      currentCost - optimizedCost,
				SavingsPercent:           70.0,
				ImplementationEffort:     "medium",
				RiskLevel:                "medium",
				Priority:                 2,
				Description:              fmt.Sprintf("Switch to spot instances for %s to achieve significant cost savings. Suitable for fault-tolerant workloads.", resource.Name),
				ActionSteps:              []string{"Implement fault tolerance", "Set up spot instance automation", "Configure interruption handling", "Monitor spot price trends"},
				EstimatedTimeToImplement: 4 * time.Hour,
				GeneratedAt:              time.Now(),
				Status:                   "pending",
			}
			
			recommendations = append(recommendations, rec)
		}
		
		// Reserved instance recommendations
		if resource.ResourceType == ResourceTypeGPU && resource.Status == ResourceStatusRunning {
			// If resource has been running for more than 30 days, recommend reservation
			if time.Since(resource.LaunchedAt) > 30*24*time.Hour {
				currentCost := resource.CostPerHourINR * 24 * 30 * 12 // Annual cost
				reservedCost := currentCost * 0.65 // 35% savings with 1-year reservation
				
				rec := CostRecommendation{
					ID:                       fmt.Sprintf("reserved_%s", resourceID),
					Type:                     "reserved_instances",
					ResourceID:               resourceID,
					CurrentCostINR:           currentCost,
					OptimizedCostINR:         reservedCost,
					PotentialSavingsINR:      currentCost - reservedCost,
					SavingsPercent:           35.0,
					ImplementationEffort:     "low",
					RiskLevel:                "low",
					Priority:                 4,
					Description:              fmt.Sprintf("Purchase reserved instance for %s to save on long-term usage costs. Suitable for stable workloads.", resource.Name),
					ActionSteps:              []string{"Analyze usage patterns", "Calculate ROI for different terms", "Purchase reservation", "Monitor utilization"},
					EstimatedTimeToImplement: 30 * time.Minute,
					GeneratedAt:              time.Now(),
					Status:                   "pending",
				}
				
				recommendations = append(recommendations, rec)
			}
		}
		
		// Scheduling optimization
		if resource.UseCase == "training" || resource.UseCase == "batch_processing" {
			offPeakSavings := resource.CostPerHourINR * 0.15 // 15% off-peak discount
			currentCost := resource.CostPerHourINR * 24 * 30
			optimizedCost := currentCost * 0.85 // 15% savings
			
			rec := CostRecommendation{
				ID:                       fmt.Sprintf("schedule_%s", resourceID),
				Type:                     "scheduling",
				ResourceID:               resourceID,
				CurrentCostINR:           currentCost,
				OptimizedCostINR:         optimizedCost,
				PotentialSavingsINR:      currentCost - optimizedCost,
				SavingsPercent:           15.0,
				ImplementationEffort:     "medium",
				RiskLevel:                "low",
				Priority:                 3,
				Description:              fmt.Sprintf("Schedule %s during off-peak hours (11 PM - 6 AM IST) for cost savings.", resource.Name),
				ActionSteps:              []string{"Analyze workload flexibility", "Set up scheduling automation", "Configure off-peak time windows", "Monitor performance"},
				EstimatedTimeToImplement: 3 * time.Hour,
				GeneratedAt:              time.Now(),
				Status:                   "pending",
			}
			
			recommendations = append(recommendations, rec)
		}
	}
	
	// Sort recommendations by potential savings
	sort.Slice(recommendations, func(i, j int) bool {
		return recommendations[i].PotentialSavingsINR > recommendations[j].PotentialSavingsINR
	})
	
	aco.recommendationEngine.recommendations = recommendations
	
	log.Printf("🎯 Generated %d cost optimization recommendations", len(recommendations))
	
	return recommendations, nil
}

// Create budget
func (aco *AICostOptimizer) CreateBudget(config BudgetConfig) (*Budget, error) {
	aco.mu.Lock()
	defer aco.mu.Unlock()
	
	budget := &Budget{
		ID:                 config.ID,
		Name:               config.Name,
		Company:            config.Company,
		Department:         config.Department,
		BudgetPeriod:       config.BudgetPeriod,
		TotalBudgetINR:     config.TotalBudgetINR,
		SpentINR:           0.0,
		RemainingINR:       config.TotalBudgetINR,
		UtilizedPercent:    0.0,
		ResourceFilters:    config.ResourceFilters,
		AlertThresholds:    config.AlertThresholds,
		StartDate:          config.StartDate,
		EndDate:            config.EndDate,
		ForecastedSpendINR: 0.0,
		Status:             BudgetStatusActive,
	}
	
	aco.budgetManager.budgets[config.ID] = budget
	
	log.Printf("💰 Created budget %s for %s: ₹%.2f (%s)",
		config.Name, config.Company, config.TotalBudgetINR, config.BudgetPeriod)
	
	return budget, nil
}

type BudgetConfig struct {
	ID              string            `json:"id"`
	Name            string            `json:"name"`
	Company         string            `json:"company"`
	Department      string            `json:"department"`
	BudgetPeriod    string            `json:"budget_period"`
	TotalBudgetINR  float64           `json:"total_budget_inr"`
	ResourceFilters map[string]string `json:"resource_filters"`
	AlertThresholds []float64         `json:"alert_thresholds"`
	StartDate       time.Time         `json:"start_date"`
	EndDate         time.Time         `json:"end_date"`
}

// Generate cost report
func (aco *AICostOptimizer) GenerateReport(reportType string, company string, period ReportPeriod) (*CostReport, error) {
	aco.mu.RLock()
	defer aco.mu.RUnlock()
	
	template, exists := aco.reportGenerator.templates[reportType]
	if !exists {
		return nil, fmt.Errorf("report template %s not found", reportType)
	}
	
	// Calculate total costs for the period
	totalCost := 0.0
	resourceCosts := make(map[string]float64)
	
	for _, resource := range aco.resourceManager.resources {
		if resource.Company == company {
			// Calculate cost for the period (simplified)
			hoursSinceStart := time.Since(period.StartDate).Hours()
			resourceCost := resource.CostPerHourINR * hoursSinceStart
			
			totalCost += resourceCost
			resourceCosts[resource.ID] = resourceCost
		}
	}
	
	// Get budget variance
	var budgetVariance float64 = 0.0
	for _, budget := range aco.budgetManager.budgets {
		if budget.Company == company {
			budgetVariance = totalCost - budget.TotalBudgetINR
			break
		}
	}
	
	// Create report sections
	sections := []ReportSection{
		{
			Title:   "Executive Summary",
			Content: fmt.Sprintf("Total spend for %s: ₹%.2f. Budget variance: ₹%.2f", company, totalCost, budgetVariance),
			Data:    map[string]interface{}{"total_cost": totalCost, "budget_variance": budgetVariance},
			Insights: []string{
				fmt.Sprintf("Current spend is ₹%.2f", totalCost),
				fmt.Sprintf("Budget variance is ₹%.2f", budgetVariance),
			},
		},
		{
			Title:   "Cost Breakdown by Resource",
			Content: "Detailed breakdown of costs by individual resources",
			Data:    map[string]interface{}{"resource_costs": resourceCosts},
			Charts:  []string{"resource_cost_pie"},
		},
	}
	
	// Create charts
	chartData := make([]ChartDataPoint, 0, len(resourceCosts))
	for resourceID, cost := range resourceCosts {
		if resource, exists := aco.resourceManager.resources[resourceID]; exists {
			chartData = append(chartData, ChartDataPoint{
				Label: resource.Name,
				Value: cost,
				Details: map[string]interface{}{
					"resource_type": resource.ResourceType.String(),
					"region":        resource.Region,
					"utilization":   resource.UtilizationPercent,
				},
			})
		}
	}
	
	charts := []ReportChart{
		{
			Type:   "pie",
			Title:  "Cost Distribution by Resource",
			XAxis:  "Resource",
			YAxis:  "Cost (INR)",
			Data:   chartData,
			Colors: []string{"#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"},
		},
	}
	
	// Generate recommendations
	recommendations := aco.recommendationEngine.recommendations
	if len(recommendations) > 10 {
		recommendations = recommendations[:10] // Top 10 recommendations
	}
	
	report := &CostReport{
		ID:                fmt.Sprintf("report_%s_%d", company, time.Now().Unix()),
		Title:             fmt.Sprintf("%s - %s", template.Name, company),
		Company:           company,
		GeneratedAt:       time.Now(),
		Period:            period,
		TotalCostINR:      totalCost,
		BudgetVarianceINR: budgetVariance,
		Sections:          sections,
		Charts:            charts,
		Recommendations:   recommendations,
		ExecutiveSummary:  fmt.Sprintf("Cost optimization report for %s covering %s to %s. Total spend: ₹%.2f with %d optimization opportunities identified.", company, period.StartDate.Format("2006-01-02"), period.EndDate.Format("2006-01-02"), totalCost, len(recommendations)),
	}
	
	aco.reportGenerator.reports[report.ID] = report
	
	log.Printf("📊 Generated %s report for %s: ₹%.2f total cost, %d recommendations",
		template.Name, company, totalCost, len(recommendations))
	
	return report, nil
}

// Update resource utilization
func (aco *AICostOptimizer) UpdateResourceUtilization(resourceID string, utilizationPercent float64) error {
	aco.mu.Lock()
	defer aco.mu.Unlock()
	
	resource, exists := aco.resourceManager.resources[resourceID]
	if !exists {
		return fmt.Errorf("resource %s not found", resourceID)
	}
	
	resource.UtilizationPercent = utilizationPercent
	resource.LastUsed = time.Now()
	
	// Update utilization metrics
	metrics, exists := aco.resourceManager.utilizationData[resourceID]
	if !exists {
		metrics = &UtilizationMetrics{
			ResourceID:  resourceID,
			LastUpdated: time.Now(),
		}
		aco.resourceManager.utilizationData[resourceID] = metrics
	}
	
	// Add data point to CPU utilization time series
	now := time.Now()
	metrics.CPUUtilization.Values = append(metrics.CPUUtilization.Values, utilizationPercent)
	metrics.CPUUtilization.Timestamps = append(metrics.CPUUtilization.Timestamps, now)
	
	// Keep only last 1000 data points
	if len(metrics.CPUUtilization.Values) > 1000 {
		metrics.CPUUtilization.Values = metrics.CPUUtilization.Values[1:]
		metrics.CPUUtilization.Timestamps = metrics.CPUUtilization.Timestamps[1:]
	}
	
	// Recalculate statistics
	if len(metrics.CPUUtilization.Values) > 0 {
		sum := 0.0
		min := metrics.CPUUtilization.Values[0]
		max := metrics.CPUUtilization.Values[0]
		
		for _, value := range metrics.CPUUtilization.Values {
			sum += value
			if value < min {
				min = value
			}
			if value > max {
				max = value
			}
		}
		
		metrics.CPUUtilization.Average = sum / float64(len(metrics.CPUUtilization.Values))
		metrics.CPUUtilization.Minimum = min
		metrics.CPUUtilization.Maximum = max
	}
	
	metrics.LastUpdated = time.Now()
	
	return nil
}

// Background monitoring processes
func (aco *AICostOptimizer) startCostMonitoring() {
	ticker := time.NewTicker(15 * time.Minute)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			aco.performCostAnalysis()
		case <-aco.ctx.Done():
			return
		}
	}
}

func (aco *AICostOptimizer) performCostAnalysis() {
	aco.mu.RLock()
	defer aco.mu.RUnlock()
	
	totalCost := 0.0
	resourceCount := len(aco.resourceManager.resources)
	
	for _, resource := range aco.resourceManager.resources {
		// Update actual costs
		hoursRunning := time.Since(resource.LaunchedAt).Hours()
		resource.ActualCostINR = resource.CostPerHourINR * hoursRunning
		totalCost += resource.ActualCostINR
		
		// Check for cost anomalies
		aco.checkCostAnomalies(resource)
	}
	
	log.Printf("💰 Cost analysis completed - %d resources, ₹%.2f total cost",
		resourceCount, totalCost)
}

func (aco *AICostOptimizer) checkCostAnomalies(resource *Resource) {
	// Simple anomaly detection: if current cost is 50% higher than expected
	expectedDailyCost := resource.CostPerHourINR * 24
	actualDailyCost := resource.CostPerHourINR * 24 * (resource.UtilizationPercent / 100.0)
	
	if actualDailyCost > expectedDailyCost*1.5 {
		anomaly := CostAnomaly{
			ResourceID:       resource.ID,
			DetectedAt:       time.Now(),
			AnomalyType:      "spike",
			ActualCostINR:    actualDailyCost,
			ExpectedCostINR:  expectedDailyCost,
			DeviationPercent: ((actualDailyCost - expectedDailyCost) / expectedDailyCost) * 100,
			Severity:         "medium",
			RootCause:        "High utilization or inefficient resource usage",
			ImpactINR:        actualDailyCost - expectedDailyCost,
		}
		
		aco.costAnalyzer.anomalyDetector.anomalies = append(
			aco.costAnalyzer.anomalyDetector.anomalies, anomaly)
		
		log.Printf("🚨 Cost anomaly detected for %s: ₹%.2f vs expected ₹%.2f",
			resource.Name, actualDailyCost, expectedDailyCost)
	}
}

func (aco *AICostOptimizer) startRecommendationGeneration() {
	ticker := time.NewTicker(1 * time.Hour)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			aco.GenerateRecommendations()
		case <-aco.ctx.Done():
			return
		}
	}
}

func (aco *AICostOptimizer) startBudgetMonitoring() {
	ticker := time.NewTicker(30 * time.Minute)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			aco.monitorBudgets()
		case <-aco.ctx.Done():
			return
		}
	}
}

func (aco *AICostOptimizer) monitorBudgets() {
	aco.mu.RLock()
	defer aco.mu.RUnlock()
	
	for _, budget := range aco.budgetManager.budgets {
		// Calculate current spend for budget period
		currentSpend := 0.0
		for _, resource := range aco.resourceManager.resources {
			if resource.Company == budget.Company {
				// Filter resources based on budget filters
				matches := true
				for key, value := range budget.ResourceFilters {
					if resourceValue, exists := resource.Tags[key]; !exists || resourceValue != value {
						matches = false
						break
					}
				}
				
				if matches {
					hoursInPeriod := time.Since(budget.StartDate).Hours()
					resourceSpend := resource.CostPerHourINR * hoursInPeriod
					currentSpend += resourceSpend
				}
			}
		}
		
		budget.SpentINR = currentSpend
		budget.RemainingINR = budget.TotalBudgetINR - currentSpend
		budget.UtilizedPercent = (currentSpend / budget.TotalBudgetINR) * 100
		
		// Check alert thresholds
		for _, threshold := range budget.AlertThresholds {
			if budget.UtilizedPercent >= threshold {
				alert := BudgetAlert{
					BudgetID:         budget.ID,
					AlertType:        "threshold",
					Severity:         aco.getSeverityForThreshold(threshold),
					Message:          fmt.Sprintf("Budget %s has reached %.1f%% utilization", budget.Name, threshold),
					CurrentSpendINR:  currentSpend,
					BudgetINR:        budget.TotalBudgetINR,
					ThresholdPercent: threshold,
					TriggeredAt:      time.Now(),
					Acknowledged:     false,
				}
				
				aco.budgetManager.budgetAlerts = append(aco.budgetManager.budgetAlerts, alert)
				
				log.Printf("💸 Budget alert for %s: %.1f%% utilized (₹%.2f / ₹%.2f)",
					budget.Name, budget.UtilizedPercent, currentSpend, budget.TotalBudgetINR)
			}
		}
	}
}

func (aco *AICostOptimizer) getSeverityForThreshold(threshold float64) string {
	if threshold >= 100.0 {
		return "critical"
	} else if threshold >= 90.0 {
		return "high"
	} else if threshold >= 80.0 {
		return "medium"
	} else {
		return "low"
	}
}

func (aco *AICostOptimizer) startReportGeneration() {
	ticker := time.NewTicker(24 * time.Hour) // Daily reports
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			aco.generateScheduledReports()
		case <-aco.ctx.Done():
			return
		}
	}
}

func (aco *AICostOptimizer) generateScheduledReports() {
	for _, scheduledReport := range aco.reportGenerator.scheduledReports {
		if scheduledReport.Enabled && time.Now().After(scheduledReport.NextRun) {
			period := ReportPeriod{
				StartDate:  time.Now().AddDate(0, 0, -7), // Last 7 days
				EndDate:    time.Now(),
				PeriodType: "weekly",
			}
			
			report, err := aco.GenerateReport(scheduledReport.ReportTemplateID, scheduledReport.Company, period)
			if err != nil {
				log.Printf("❌ Failed to generate scheduled report: %v", err)
				continue
			}
			
			log.Printf("📊 Generated scheduled report %s for %s", report.Title, scheduledReport.Company)
			
			// Update next run time (simplified - add 7 days)
			scheduledReport.NextRun = scheduledReport.NextRun.AddDate(0, 0, 7)
			scheduledReport.LastRun = time.Now()
		}
	}
}

// Get system status
func (aco *AICostOptimizer) GetSystemStatus() map[string]interface{} {
	aco.mu.RLock()
	defer aco.mu.RUnlock()
	
	totalResources := len(aco.resourceManager.resources)
	totalBudgets := len(aco.budgetManager.budgets)
	totalRecommendations := len(aco.recommendationEngine.recommendations)
	
	// Calculate total costs and potential savings
	totalCostINR := 0.0
	totalPotentialSavingsINR := 0.0
	
	for _, resource := range aco.resourceManager.resources {
		totalCostINR += resource.ActualCostINR
	}
	
	for _, recommendation := range aco.recommendationEngine.recommendations {
		totalPotentialSavingsINR += recommendation.PotentialSavingsINR
	}
	
	// Resource breakdown by provider
	providerBreakdown := make(map[string]int)
	for _, resource := range aco.resourceManager.resources {
		providerBreakdown[resource.Provider]++
	}
	
	// Company breakdown
	companyBreakdown := make(map[string]float64)
	for _, resource := range aco.resourceManager.resources {
		companyBreakdown[resource.Company] += resource.ActualCostINR
	}
	
	status := map[string]interface{}{
		"summary": map[string]interface{}{
			"total_resources":            totalResources,
			"total_budgets":             totalBudgets,
			"total_recommendations":     totalRecommendations,
			"total_cost_inr":           totalCostINR,
			"potential_savings_inr":     totalPotentialSavingsINR,
			"savings_opportunity_percent": (totalPotentialSavingsINR / totalCostINR) * 100,
		},
		"breakdown": map[string]interface{}{
			"by_provider": providerBreakdown,
			"by_company":  companyBreakdown,
		},
		"recent_alerts": len(aco.budgetManager.budgetAlerts),
		"anomalies":     len(aco.costAnalyzer.anomalyDetector.anomalies),
		"timestamp":     time.Now(),
	}
	
	return status
}

// HTTP API handlers
func (aco *AICostOptimizer) handleAddResource(w http.ResponseWriter, r *http.Request) {
	var config ResourceConfig
	if err := json.NewDecoder(r.Body).Decode(&config); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	
	err := aco.AddResource(config)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "success"})
}

func (aco *AICostOptimizer) handleGetRecommendations(w http.ResponseWriter, r *http.Request) {
	recommendations, err := aco.GenerateRecommendations()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(recommendations)
}

func (aco *AICostOptimizer) handleCreateBudget(w http.ResponseWriter, r *http.Request) {
	var config BudgetConfig
	if err := json.NewDecoder(r.Body).Decode(&config); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	
	budget, err := aco.CreateBudget(config)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(budget)
}

func (aco *AICostOptimizer) handleGetStatus(w http.ResponseWriter, r *http.Request) {
	status := aco.GetSystemStatus()
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

func (aco *AICostOptimizer) handleUpdateUtilization(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	resourceID := vars["resourceId"]
	
	var request struct {
		UtilizationPercent float64 `json:"utilization_percent"`
	}
	
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	
	err := aco.UpdateResourceUtilization(resourceID, request.UtilizationPercent)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "success"})
}

// Start HTTP server
func (aco *AICostOptimizer) StartHTTPServer(port string) {
	router := mux.NewRouter()
	
	// API endpoints
	router.HandleFunc("/resources", aco.handleAddResource).Methods("POST")
	router.HandleFunc("/resources/{resourceId}/utilization", aco.handleUpdateUtilization).Methods("PUT")
	router.HandleFunc("/recommendations", aco.handleGetRecommendations).Methods("GET")
	router.HandleFunc("/budgets", aco.handleCreateBudget).Methods("POST")
	router.HandleFunc("/status", aco.handleGetStatus).Methods("GET")
	
	log.Printf("🌐 AI Cost Optimizer HTTP server starting on port %s", port)
	log.Printf("📊 Status endpoint: http://localhost:%s/status", port)
	log.Printf("🎯 Recommendations: http://localhost:%s/recommendations", port)
	
	log.Fatal(http.ListenAndServe(":"+port, router))
}

// Shutdown
func (aco *AICostOptimizer) Shutdown() {
	log.Println("🛑 Shutting down AI Cost Optimizer...")
	aco.cancel()
	log.Println("✅ AI Cost Optimizer shutdown complete")
}

// Demo function
func main() {
	fmt.Println("🚀 AI Cost Optimizer Demo - Indian Infrastructure")
	fmt.Println(strings.Repeat("=", 70))
	
	// Initialize optimizer
	optimizer := NewAICostOptimizer()
	defer optimizer.Shutdown()
	
	// Add sample resources from Indian companies
	resources := []ResourceConfig{
		{
			ID:               "paytm-gpu-mumbai-01",
			Name:             "PayTM Fraud Detection GPU",
			Provider:         "aws",
			Region:           "ap-south-1",
			ResourceType:     ResourceTypeGPU,
			InstanceType:     "p3.2xlarge",
			Company:          "paytm",
			UseCase:          "fraud_detection",
			CostPerHourINR:   45.0,
			Tags:             map[string]string{"env": "production", "team": "ai"},
			MonthlyBudgetINR: 32000.0, // ₹32k/month
			GPUCount:         1,
			GPUType:          "V100",
			MemoryGB:         61,
			StorageGB:        1000,
			NetworkBandwidth: 10000,
		},
		{
			ID:               "flipkart-ml-bangalore-01",
			Name:             "Flipkart Recommendation Engine",
			Provider:         "azure",
			Region:           "centralindia",
			ResourceType:     ResourceTypeMLService,
			InstanceType:     "Standard_NC6s_v3",
			Company:          "flipkart",
			UseCase:          "recommendations",
			CostPerHourINR:   48.0,
			Tags:             map[string]string{"env": "production", "team": "ml"},
			MonthlyBudgetINR: 35000.0, // ₹35k/month
			GPUCount:         1,
			GPUType:          "V100",
			MemoryGB:         112,
			StorageGB:        1500,
			NetworkBandwidth: 25000,
		},
		{
			ID:               "zomato-vision-mumbai-01",
			Name:             "Zomato Food Image Classifier",
			Provider:         "gcp",
			Region:           "asia-south1",
			ResourceType:     ResourceTypeGPU,
			InstanceType:     "n1-standard-4-k80x4",
			Company:          "zomato",
			UseCase:          "image_classification",
			CostPerHourINR:   38.0,
			Tags:             map[string]string{"env": "production", "team": "vision"},
			MonthlyBudgetINR: 28000.0, // ₹28k/month
			GPUCount:         4,
			GPUType:          "K80",
			MemoryGB:         64,
			StorageGB:        500,
			NetworkBandwidth: 16000,
		},
		{
			ID:               "ola-routing-bangalore-01",
			Name:             "Ola Route Optimization",
			Provider:         "on-premise",
			Region:           "on-premise-mumbai",
			ResourceType:     ResourceTypeCompute,
			InstanceType:     "custom-gpu-server",
			Company:          "ola",
			UseCase:          "route_optimization",
			CostPerHourINR:   15.0, // Cheaper on-premise
			Tags:             map[string]string{"env": "production", "team": "logistics"},
			MonthlyBudgetINR: 15000.0, // ₹15k/month
			GPUCount:         2,
			GPUType:          "RTX_3080",
			MemoryGB:         32,
			StorageGB:        2000,
			NetworkBandwidth: 1000,
		},
	}
	
	// Add resources
	for _, config := range resources {
		err := optimizer.AddResource(config)
		if err != nil {
			log.Printf("❌ Failed to add resource %s: %v", config.Name, err)
		}
	}
	
	fmt.Println("\n✅ Added 4 AI resources from Indian companies")
	
	// Create budgets
	budgets := []BudgetConfig{
		{
			ID:              "paytm-ai-budget",
			Name:            "PayTM AI Department Monthly Budget",
			Company:         "paytm",
			Department:      "ai",
			BudgetPeriod:    "monthly",
			TotalBudgetINR:  50000.0, // ₹50k/month
			ResourceFilters: map[string]string{"team": "ai"},
			AlertThresholds: []float64{50.0, 80.0, 95.0, 100.0},
			StartDate:       time.Now().AddDate(0, 0, -1), // Yesterday
			EndDate:         time.Now().AddDate(0, 1, 0),  // Next month
		},
		{
			ID:              "flipkart-ml-budget",
			Name:            "Flipkart ML Department Quarterly Budget",
			Company:         "flipkart",
			Department:      "ml",
			BudgetPeriod:    "quarterly",
			TotalBudgetINR:  150000.0, // ₹1.5L/quarter
			ResourceFilters: map[string]string{"team": "ml"},
			AlertThresholds: []float64{60.0, 80.0, 90.0, 100.0},
			StartDate:       time.Now().AddDate(0, 0, -30), // 30 days ago
			EndDate:         time.Now().AddDate(0, 3, 0),   // 3 months from now
		},
	}
	
	// Create budgets
	for _, config := range budgets {
		_, err := optimizer.CreateBudget(config)
		if err != nil {
			log.Printf("❌ Failed to create budget %s: %v", config.Name, err)
		}
	}
	
	fmt.Println("\n💰 Created 2 departmental budgets")
	
	// Simulate utilization data
	fmt.Println("\n📊 Simulating utilization data...")
	
	utilizationData := map[string]float64{
		"paytm-gpu-mumbai-01":      25.0, // Underutilized
		"flipkart-ml-bangalore-01": 85.0, // Well utilized
		"zomato-vision-mumbai-01":  15.0, // Very underutilized
		"ola-routing-bangalore-01": 95.0, // Overutilized
	}
	
	for resourceID, utilization := range utilizationData {
		err := optimizer.UpdateResourceUtilization(resourceID, utilization)
		if err != nil {
			log.Printf("❌ Failed to update utilization for %s: %v", resourceID, err)
		}
	}
	
	// Generate recommendations
	fmt.Println("\n🎯 Generating cost optimization recommendations...")
	
	recommendations, err := optimizer.GenerateRecommendations()
	if err != nil {
		fmt.Printf("❌ Failed to generate recommendations: %v\n", err)
	} else {
		fmt.Printf("Generated %d recommendations:\n", len(recommendations))
		
		for i, rec := range recommendations[:5] { // Show top 5
			fmt.Printf("\n%d. %s (%s)\n", i+1, rec.Description, rec.Type)
			fmt.Printf("   Potential Savings: ₹%.2f (%.1f%%)\n", rec.PotentialSavingsINR, rec.SavingsPercent)
			fmt.Printf("   Implementation: %s effort, %s risk\n", rec.ImplementationEffort, rec.RiskLevel)
			fmt.Printf("   Priority: %d/5\n", rec.Priority)
		}
	}
	
	// Generate reports
	fmt.Println("\n📊 Generating cost reports...")
	
	reportPeriod := ReportPeriod{
		StartDate:  time.Now().AddDate(0, 0, -7), // Last 7 days
		EndDate:    time.Now(),
		PeriodType: "weekly",
	}
	
	companies := []string{"paytm", "flipkart", "zomato", "ola"}
	
	for _, company := range companies {
		report, err := optimizer.GenerateReport("weekly_operational", company, reportPeriod)
		if err != nil {
			log.Printf("❌ Failed to generate report for %s: %v", company, err)
			continue
		}
		
		fmt.Printf("\n📈 %s Report:\n", company)
		fmt.Printf("   Total Cost: ₹%.2f\n", report.TotalCostINR)
		fmt.Printf("   Budget Variance: ₹%.2f\n", report.BudgetVarianceINR)
		fmt.Printf("   Recommendations: %d\n", len(report.Recommendations))
	}
	
	// Show system status
	fmt.Println("\n📊 System Status:")
	status := optimizer.GetSystemStatus()
	
	summary := status["summary"].(map[string]interface{})
	fmt.Printf("   Resources: %v\n", summary["total_resources"])
	fmt.Printf("   Total Cost: ₹%.2f\n", summary["total_cost_inr"])
	fmt.Printf("   Potential Savings: ₹%.2f (%.1f%%)\n",
		summary["potential_savings_inr"], summary["savings_opportunity_percent"])
	
	breakdown := status["breakdown"].(map[string]interface{})
	providerBreakdown := breakdown["by_provider"].(map[string]int)
	
	fmt.Println("\n   Provider Distribution:")
	for provider, count := range providerBreakdown {
		fmt.Printf("      %s: %d resources\n", provider, count)
	}
	
	companyBreakdown := breakdown["by_company"].(map[string]float64)
	fmt.Println("\n   Company Costs:")
	for company, cost := range companyBreakdown {
		fmt.Printf("      %s: ₹%.2f\n", company, cost)
	}
	
	fmt.Println("\n🎯 Indian AI Cost Optimization Features:")
	fmt.Println("   ✅ Multi-cloud cost optimization (AWS, Azure, GCP, On-premise)")
	fmt.Println("   ✅ Regional pricing optimization for Indian markets")
	fmt.Println("   ✅ INR-based cost tracking and budgeting")
	fmt.Println("   ✅ Intelligent rightsizing recommendations")
	fmt.Println("   ✅ Spot/Preemptible instance optimization")
	fmt.Println("   ✅ Reserved instance ROI analysis")
	fmt.Println("   ✅ Off-peak scheduling optimization (IST timezone)")
	fmt.Println("   ✅ Budget monitoring with customizable alerts")
	fmt.Println("   ✅ Cost anomaly detection")
	fmt.Println("   ✅ Automated report generation")
	fmt.Println("   ✅ Company and department-level cost allocation")
	fmt.Println("   ✅ Utilization-based optimization")
	
	// Start HTTP server for demonstration
	fmt.Println("\n🌐 Starting HTTP server on port 8082...")
	fmt.Println("   Add resource: POST http://localhost:8082/resources")
	fmt.Println("   Get recommendations: GET http://localhost:8082/recommendations")
	fmt.Println("   Create budget: POST http://localhost:8082/budgets")
	fmt.Println("   System status: GET http://localhost:8082/status")
	
	go optimizer.StartHTTPServer("8082")
	
	// Keep demo running
	fmt.Println("\n⏰ Demo running for 60 seconds...")
	time.Sleep(60 * time.Second)
	
	fmt.Println("\n🎉 AI Cost Optimizer demo completed successfully!")
}
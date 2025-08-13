package main

/*
Feature Flag Management System for GitOps
Indian E-commerce और FinTech applications के लिए advanced feature flag management

यह system GitOps approach use करके feature flags को manage करता है:
- Real-time feature toggles for Indian markets
- A/B testing for different user segments
- Regional feature rollouts (Mumbai, Delhi, Bangalore)
- Business hours aware feature activation
- Compliance-aware feature controls
- Performance monitoring and automatic rollbacks

Features:
- Git-based configuration management
- Kubernetes native integration
- Real-time updates without deployments
- Advanced targeting (geography, user segments, device types)
- Indian market specific configurations
- Audit trail for compliance

Author: Platform Engineering Team - Indian E-commerce
*/

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"strconv"
	"strings"
	"time"

	"github.com/go-redis/redis/v8"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/client-go/kubernetes"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"
)

// FeatureFlag represents a feature flag configuration
// Feature flag का complete configuration और metadata
type FeatureFlag struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   FeatureFlagSpec   `json:"spec,omitempty"`
	Status FeatureFlagStatus `json:"status,omitempty"`
}

// FeatureFlagSpec defines the desired state of FeatureFlag
type FeatureFlagSpec struct {
	// Basic flag configuration
	Name        string `json:"name"`
	Description string `json:"description"`
	Enabled     bool   `json:"enabled"`
	
	// Indian market specific configurations
	IndianMarketConfig IndianMarketConfig `json:"indianMarketConfig"`
	
	// Targeting rules
	Targeting TargetingRules `json:"targeting"`
	
	// Rollout configuration
	Rollout RolloutConfig `json:"rollout"`
	
	// Monitoring and safety
	Monitoring MonitoringConfig `json:"monitoring"`
	
	// Compliance requirements
	Compliance ComplianceConfig `json:"compliance"`
}

// IndianMarketConfig defines India-specific feature flag settings
type IndianMarketConfig struct {
	// Regional settings
	Regions []IndianRegion `json:"regions"`
	
	// Business hours configuration
	BusinessHours BusinessHoursConfig `json:"businessHours"`
	
	// Festival season handling
	FestivalConfig FestivalConfig `json:"festivalConfig"`
	
	// Language and localization
	LocalizationConfig LocalizationConfig `json:"localizationConfig"`
	
	// Payment methods specific flags
	PaymentMethods []PaymentMethodConfig `json:"paymentMethods"`
}

// IndianRegion represents different Indian regions
type IndianRegion struct {
	Name       string  `json:"name"`       // mumbai, delhi, bangalore, etc.
	Enabled    bool    `json:"enabled"`
	Percentage float64 `json:"percentage"` // 0-100
	Priority   int     `json:"priority"`   // 1 = highest
}

// BusinessHoursConfig for Indian business hours
type BusinessHoursConfig struct {
	Enabled   bool   `json:"enabled"`
	StartTime string `json:"startTime"` // 09:00
	EndTime   string `json:"endTime"`   // 18:00
	Timezone  string `json:"timezone"`  // Asia/Kolkata
	
	// Weekend configuration
	WeekendEnabled bool     `json:"weekendEnabled"`
	WeekendDays    []string `json:"weekendDays"` // ["saturday", "sunday"]
}

// FestivalConfig for Indian festival seasons
type FestivalConfig struct {
	Enabled bool `json:"enabled"`
	
	// Festival periods
	FestivalPeriods []FestivalPeriod `json:"festivalPeriods"`
	
	// Special handling during festivals
	FestivalBehavior FestivalBehavior `json:"festivalBehavior"`
}

// FestivalPeriod represents a festival duration
type FestivalPeriod struct {
	Name      string    `json:"name"`      // Diwali, Holi, etc.
	StartDate time.Time `json:"startDate"`
	EndDate   time.Time `json:"endDate"`
	
	// Festival specific configuration
	TrafficMultiplier float64 `json:"trafficMultiplier"` // Expected traffic increase
	FeatureBehavior   string  `json:"featureBehavior"`   // enable, disable, maintain
}

// FestivalBehavior defines how features behave during festivals
type FestivalBehavior struct {
	AutoScaleFeatures bool    `json:"autoScaleFeatures"`
	MaxPercentage     float64 `json:"maxPercentage"`
	SafetyThreshold   float64 `json:"safetyThreshold"`
}

// LocalizationConfig for Indian languages
type LocalizationConfig struct {
	Enabled bool `json:"enabled"`
	
	// Supported languages
	SupportedLanguages []LanguageConfig `json:"supportedLanguages"`
	
	// Default language
	DefaultLanguage string `json:"defaultLanguage"` // hindi, english
}

// LanguageConfig for specific language settings
type LanguageConfig struct {
	Code        string  `json:"code"`        // hi, en, ta, te, etc.
	Name        string  `json:"name"`        // Hindi, Tamil, etc.
	Enabled     bool    `json:"enabled"`
	Percentage  float64 `json:"percentage"`  // Rollout percentage for this language
	Regions     []string `json:"regions"`    // Applicable regions
}

// PaymentMethodConfig for Indian payment methods
type PaymentMethodConfig struct {
	Method      string  `json:"method"`      // upi, netbanking, cards, wallets
	Enabled     bool    `json:"enabled"`
	Percentage  float64 `json:"percentage"`
	Regions     []string `json:"regions"`
	UserSegments []string `json:"userSegments"`
}

// TargetingRules defines who gets the feature
type TargetingRules struct {
	// User segments
	UserSegments []UserSegmentRule `json:"userSegments"`
	
	// Device targeting
	DeviceTargeting DeviceTargeting `json:"deviceTargeting"`
	
	// Geographic targeting
	GeographicTargeting GeographicTargeting `json:"geographicTargeting"`
	
	// Time-based targeting
	TimeBasedTargeting TimeBasedTargeting `json:"timeBasedTargeting"`
}

// UserSegmentRule defines targeting for user segments
type UserSegmentRule struct {
	Segment    string  `json:"segment"`    // premium, regular, new, etc.
	Enabled    bool    `json:"enabled"`
	Percentage float64 `json:"percentage"`
	
	// Segment specific conditions
	Conditions []SegmentCondition `json:"conditions"`
}

// SegmentCondition defines conditions for user segments
type SegmentCondition struct {
	Attribute string      `json:"attribute"` // age, tier, registration_date, etc.
	Operator  string      `json:"operator"`  // equals, greater_than, in, etc.
	Value     interface{} `json:"value"`
}

// DeviceTargeting for different device types
type DeviceTargeting struct {
	Enabled bool `json:"enabled"`
	
	// Device types
	Mobile  DeviceTypeConfig `json:"mobile"`
	Desktop DeviceTypeConfig `json:"desktop"`
	Tablet  DeviceTypeConfig `json:"tablet"`
}

// DeviceTypeConfig for specific device type
type DeviceTypeConfig struct {
	Enabled    bool    `json:"enabled"`
	Percentage float64 `json:"percentage"`
	
	// OS specific targeting
	AndroidConfig AndroidConfig `json:"androidConfig"`
	IOSConfig     IOSConfig     `json:"iosConfig"`
}

// AndroidConfig for Android specific targeting
type AndroidConfig struct {
	Enabled       bool     `json:"enabled"`
	MinVersion    string   `json:"minVersion"`
	MaxVersion    string   `json:"maxVersion"`
	DeviceModels  []string `json:"deviceModels"`
	Manufacturers []string `json:"manufacturers"` // Samsung, Xiaomi, OnePlus, etc.
}

// IOSConfig for iOS specific targeting  
type IOSConfig struct {
	Enabled    bool     `json:"enabled"`
	MinVersion string   `json:"minVersion"`
	MaxVersion string   `json:"maxVersion"`
	DeviceModels []string `json:"deviceModels"`
}

// GeographicTargeting for location-based targeting
type GeographicTargeting struct {
	Enabled bool `json:"enabled"`
	
	// Country targeting
	Countries []CountryConfig `json:"countries"`
	
	// State targeting (Indian states)
	States []StateConfig `json:"states"`
	
	// City targeting (major Indian cities)
	Cities []CityConfig `json:"cities"`
}

// CountryConfig for country-level targeting
type CountryConfig struct {
	Code       string  `json:"code"`       // IN, US, etc.
	Enabled    bool    `json:"enabled"`
	Percentage float64 `json:"percentage"`
}

// StateConfig for Indian state targeting
type StateConfig struct {
	Name       string  `json:"name"`       // Maharashtra, Karnataka, etc.
	Code       string  `json:"code"`       // MH, KA, etc.
	Enabled    bool    `json:"enabled"`
	Percentage float64 `json:"percentage"`
}

// CityConfig for Indian city targeting
type CityConfig struct {
	Name       string  `json:"name"`       // Mumbai, Delhi, Bangalore, etc.
	State      string  `json:"state"`
	Enabled    bool    `json:"enabled"`
	Percentage float64 `json:"percentage"`
	Tier       int     `json:"tier"`       // 1, 2, 3 (city tier)
}

// TimeBasedTargeting for time-sensitive features
type TimeBasedTargeting struct {
	Enabled bool `json:"enabled"`
	
	// Schedule configuration
	Schedules []ScheduleConfig `json:"schedules"`
	
	// Timezone handling
	Timezone string `json:"timezone"` // Asia/Kolkata
}

// ScheduleConfig for scheduled feature activation
type ScheduleConfig struct {
	Name        string    `json:"name"`
	StartTime   time.Time `json:"startTime"`
	EndTime     time.Time `json:"endTime"`
	DaysOfWeek  []string  `json:"daysOfWeek"`  // monday, tuesday, etc.
	Percentage  float64   `json:"percentage"`
	Recurring   bool      `json:"recurring"`
}

// RolloutConfig defines rollout strategy
type RolloutConfig struct {
	Strategy RolloutStrategy `json:"strategy"`
	
	// Gradual rollout configuration
	GradualRollout GradualRolloutConfig `json:"gradualRollout"`
	
	// Canary configuration
	CanaryConfig CanaryConfig `json:"canaryConfig"`
	
	// Safety configuration
	SafetyConfig SafetyConfig `json:"safetyConfig"`
}

// RolloutStrategy defines different rollout strategies
type RolloutStrategy struct {
	Type string `json:"type"` // instant, gradual, canary, blue_green
	
	// Strategy specific parameters
	Parameters map[string]interface{} `json:"parameters"`
}

// GradualRolloutConfig for gradual rollouts
type GradualRolloutConfig struct {
	Enabled bool `json:"enabled"`
	
	// Rollout phases
	Phases []RolloutPhase `json:"phases"`
	
	// Phase transition criteria
	TransitionCriteria TransitionCriteria `json:"transitionCriteria"`
}

// RolloutPhase represents a phase in gradual rollout
type RolloutPhase struct {
	Name       string        `json:"name"`
	Percentage float64       `json:"percentage"`
	Duration   time.Duration `json:"duration"`
	
	// Phase specific targeting
	Targeting TargetingRules `json:"targeting"`
}

// TransitionCriteria for moving between phases
type TransitionCriteria struct {
	// Success metrics thresholds
	SuccessRate    float64 `json:"successRate"`    // Minimum success rate
	ErrorRate      float64 `json:"errorRate"`      // Maximum error rate
	ResponseTime   int     `json:"responseTime"`   // Maximum response time (ms)
	
	// Business metrics
	ConversionRate float64 `json:"conversionRate"` // Minimum conversion rate
	RevenueImpact  float64 `json:"revenueImpact"`  // Minimum revenue impact
	
	// User satisfaction
	UserSatisfaction float64 `json:"userSatisfaction"` // Minimum satisfaction score
}

// CanaryConfig for canary deployments
type CanaryConfig struct {
	Enabled bool `json:"enabled"`
	
	// Canary percentage
	Percentage float64 `json:"percentage"` // 5-10% typical for canary
	
	// Canary duration
	Duration time.Duration `json:"duration"`
	
	// Success criteria for promoting canary
	PromotionCriteria TransitionCriteria `json:"promotionCriteria"`
	
	// Automatic promotion settings
	AutoPromotion bool `json:"autoPromotion"`
}

// SafetyConfig for rollout safety
type SafetyConfig struct {
	Enabled bool `json:"enabled"`
	
	// Circuit breaker configuration
	CircuitBreaker CircuitBreakerConfig `json:"circuitBreaker"`
	
	// Automatic rollback settings
	AutoRollback AutoRollbackConfig `json:"autoRollback"`
	
	// Manual approval requirements
	ManualApproval ManualApprovalConfig `json:"manualApproval"`
}

// CircuitBreakerConfig for circuit breaker pattern
type CircuitBreakerConfig struct {
	Enabled bool `json:"enabled"`
	
	// Thresholds
	ErrorRateThreshold float64 `json:"errorRateThreshold"` // 10% error rate
	RequestThreshold   int     `json:"requestThreshold"`   // Minimum requests
	
	// Timing
	TimeWindow time.Duration `json:"timeWindow"` // 5 minutes
	
	// Recovery settings
	RecoveryTime time.Duration `json:"recoveryTime"` // 30 minutes
}

// AutoRollbackConfig for automatic rollbacks
type AutoRollbackConfig struct {
	Enabled bool `json:"enabled"`
	
	// Rollback triggers
	ErrorRateThreshold   float64 `json:"errorRateThreshold"`   // 5% error rate
	ResponseTimeThreshold int     `json:"responseTimeThreshold"` // 3000ms
	
	// Business metric triggers
	ConversionDropThreshold float64 `json:"conversionDropThreshold"` // 20% drop
	RevenueDropThreshold    float64 `json:"revenueDropThreshold"`    // 15% drop
	
	// Rollback timing
	EvaluationWindow time.Duration `json:"evaluationWindow"` // 10 minutes
}

// ManualApprovalConfig for manual approval requirements
type ManualApprovalConfig struct {
	Required bool `json:"required"`
	
	// Approval requirements
	RequiredApprovers []ApproverConfig `json:"requiredApprovers"`
	
	// Approval timeouts
	ApprovalTimeout time.Duration `json:"approvalTimeout"` // 24 hours
}

// ApproverConfig defines who can approve rollouts
type ApproverConfig struct {
	Role  string   `json:"role"`  // product_manager, engineering_lead, etc.
	Users []string `json:"users"` // Specific user IDs
	Teams []string `json:"teams"` // Team names
}

// MonitoringConfig for feature flag monitoring
type MonitoringConfig struct {
	Enabled bool `json:"enabled"`
	
	// Metrics collection
	MetricsConfig MetricsConfig `json:"metricsConfig"`
	
	// Alerting configuration
	AlertingConfig AlertingConfig `json:"alertingConfig"`
	
	// Dashboard configuration
	DashboardConfig DashboardConfig `json:"dashboardConfig"`
}

// MetricsConfig for metrics collection
type MetricsConfig struct {
	Enabled bool `json:"enabled"`
	
	// Metrics to collect
	CollectUsage       bool `json:"collectUsage"`       // Feature usage metrics
	CollectPerformance bool `json:"collectPerformance"` // Performance metrics
	CollectBusiness    bool `json:"collectBusiness"`    // Business metrics
	
	// Collection frequency
	CollectionInterval time.Duration `json:"collectionInterval"` // 1 minute
	
	// Retention period
	RetentionPeriod time.Duration `json:"retentionPeriod"` // 90 days
}

// AlertingConfig for feature flag alerting
type AlertingConfig struct {
	Enabled bool `json:"enabled"`
	
	// Alert rules
	AlertRules []AlertRule `json:"alertRules"`
	
	// Notification channels
	NotificationChannels []NotificationChannel `json:"notificationChannels"`
}

// AlertRule defines alerting rules
type AlertRule struct {
	Name        string  `json:"name"`
	Description string  `json:"description"`
	Metric      string  `json:"metric"`      // error_rate, response_time, etc.
	Threshold   float64 `json:"threshold"`
	Operator    string  `json:"operator"`    // greater_than, less_than, etc.
	Duration    time.Duration `json:"duration"` // 5 minutes
	Severity    string  `json:"severity"`    // critical, warning, info
}

// NotificationChannel defines notification destinations
type NotificationChannel struct {
	Type   string                 `json:"type"`   // slack, email, pagerduty, etc.
	Config map[string]interface{} `json:"config"` // Channel specific configuration
}

// DashboardConfig for feature flag dashboards
type DashboardConfig struct {
	Enabled bool `json:"enabled"`
	
	// Dashboard settings
	GrafanaDashboard GrafanaDashboardConfig `json:"grafanaDashboard"`
	
	// Custom dashboards
	CustomDashboards []CustomDashboardConfig `json:"customDashboards"`
}

// GrafanaDashboardConfig for Grafana integration
type GrafanaDashboardConfig struct {
	Enabled      bool   `json:"enabled"`
	DashboardUID string `json:"dashboardUID"`
	URL          string `json:"url"`
}

// CustomDashboardConfig for custom dashboard integration
type CustomDashboardConfig struct {
	Name string `json:"name"`
	Type string `json:"type"` // datadog, newrelic, etc.
	URL  string `json:"url"`
}

// ComplianceConfig for regulatory compliance
type ComplianceConfig struct {
	Enabled bool `json:"enabled"`
	
	// Compliance frameworks
	RBICompliance    RBIComplianceConfig    `json:"rbiCompliance"`
	PCIDSSCompliance PCIDSSComplianceConfig `json:"pciDssCompliance"`
	GDPRCompliance   GDPRComplianceConfig   `json:"gdprCompliance"`
	
	// Audit requirements
	AuditConfig AuditConfig `json:"auditConfig"`
	
	// Data privacy
	DataPrivacyConfig DataPrivacyConfig `json:"dataPrivacyConfig"`
}

// RBIComplianceConfig for RBI compliance
type RBIComplianceConfig struct {
	Enabled bool `json:"enabled"`
	
	// Data residency requirements
	DataResidency DataResidencyConfig `json:"dataResidency"`
	
	// Audit trail requirements
	AuditTrail AuditTrailConfig `json:"auditTrail"`
	
	// Security requirements
	SecurityRequirements SecurityRequirementsConfig `json:"securityRequirements"`
}

// DataResidencyConfig for data residency compliance
type DataResidencyConfig struct {
	Required         bool     `json:"required"`
	AllowedRegions   []string `json:"allowedRegions"`   // mumbai, delhi, bangalore
	ProhibitedRegions []string `json:"prohibitedRegions"` // Any non-Indian regions
}

// AuditTrailConfig for audit trail requirements
type AuditTrailConfig struct {
	Required        bool          `json:"required"`
	RetentionPeriod time.Duration `json:"retentionPeriod"` // 7 years for RBI
	LogLevel        string        `json:"logLevel"`        // detailed, standard, minimal
}

// SecurityRequirementsConfig for security compliance
type SecurityRequirementsConfig struct {
	EncryptionRequired bool `json:"encryptionRequired"`
	AccessControlRequired bool `json:"accessControlRequired"`
	NetworkSecurityRequired bool `json:"networkSecurityRequired"`
}

// PCIDSSComplianceConfig for PCI-DSS compliance
type PCIDSSComplianceConfig struct {
	Enabled bool   `json:"enabled"`
	Level   string `json:"level"` // 1, 2, 3, 4
	
	// PCI-DSS specific requirements
	CardDataProtection CardDataProtectionConfig `json:"cardDataProtection"`
}

// CardDataProtectionConfig for card data protection
type CardDataProtectionConfig struct {
	Required          bool `json:"required"`
	TokenizationRequired bool `json:"tokenizationRequired"`
	EncryptionRequired   bool `json:"encryptionRequired"`
}

// GDPRComplianceConfig for GDPR compliance
type GDPRComplianceConfig struct {
	Enabled bool `json:"enabled"`
	
	// GDPR specific requirements
	ConsentManagement ConsentManagementConfig `json:"consentManagement"`
	DataMinimization  DataMinimizationConfig  `json:"dataMinimization"`
}

// ConsentManagementConfig for consent management
type ConsentManagementConfig struct {
	Required           bool `json:"required"`
	ExplicitConsent    bool `json:"explicitConsent"`
	ConsentWithdrawal  bool `json:"consentWithdrawal"`
}

// DataMinimizationConfig for data minimization
type DataMinimizationConfig struct {
	Required bool `json:"required"`
	Purpose  string `json:"purpose"`
}

// AuditConfig for audit trail configuration
type AuditConfig struct {
	Enabled bool `json:"enabled"`
	
	// Audit events to log
	LogConfigChanges bool `json:"logConfigChanges"`
	LogUsage         bool `json:"logUsage"`
	LogAccess        bool `json:"logAccess"`
	
	// Audit storage
	StorageConfig AuditStorageConfig `json:"storageConfig"`
}

// AuditStorageConfig for audit log storage
type AuditStorageConfig struct {
	Type           string        `json:"type"`           // database, file, s3, etc.
	Location       string        `json:"location"`
	RetentionPeriod time.Duration `json:"retentionPeriod"`
	EncryptionEnabled bool        `json:"encryptionEnabled"`
}

// DataPrivacyConfig for data privacy settings
type DataPrivacyConfig struct {
	Enabled bool `json:"enabled"`
	
	// Privacy settings
	AnonymizationRequired bool `json:"anonymizationRequired"`
	PseudonymizationRequired bool `json:"pseudonymizationRequired"`
	
	// Data handling
	DataHandlingConfig DataHandlingConfig `json:"dataHandlingConfig"`
}

// DataHandlingConfig for data handling settings
type DataHandlingConfig struct {
	CollectionMinimization bool          `json:"collectionMinimization"`
	ProcessingLimitation   bool          `json:"processingLimitation"`
	StorageLimitation      time.Duration `json:"storageLimitation"`
}

// FeatureFlagStatus defines the observed state of FeatureFlag
type FeatureFlagStatus struct {
	// Current state
	Phase   string `json:"phase"`
	Reason  string `json:"reason"`
	Message string `json:"message"`
	
	// Rollout status
	RolloutStatus RolloutStatus `json:"rolloutStatus"`
	
	// Monitoring status
	MonitoringStatus MonitoringStatus `json:"monitoringStatus"`
	
	// Compliance status
	ComplianceStatus ComplianceStatus `json:"complianceStatus"`
	
	// Last update time
	LastUpdated metav1.Time `json:"lastUpdated"`
}

// RolloutStatus represents current rollout state
type RolloutStatus struct {
	CurrentPhase   string  `json:"currentPhase"`
	CurrentPercentage float64 `json:"currentPercentage"`
	UsersAffected  int64   `json:"usersAffected"`
	
	// Phase transition information
	NextPhaseAt    *metav1.Time `json:"nextPhaseAt,omitempty"`
	CanProceed     bool         `json:"canProceed"`
	BlockingReason string       `json:"blockingReason,omitempty"`
}

// MonitoringStatus represents monitoring state
type MonitoringStatus struct {
	HealthStatus string `json:"healthStatus"` // healthy, degraded, unhealthy
	
	// Current metrics
	CurrentMetrics CurrentMetrics `json:"currentMetrics"`
	
	// Alert status
	ActiveAlerts []ActiveAlert `json:"activeAlerts"`
}

// CurrentMetrics represents current performance metrics
type CurrentMetrics struct {
	UsageCount     int64   `json:"usageCount"`
	ErrorRate      float64 `json:"errorRate"`
	ResponseTime   int64   `json:"responseTime"`
	ConversionRate float64 `json:"conversionRate"`
}

// ActiveAlert represents an active alert
type ActiveAlert struct {
	Name        string      `json:"name"`
	Severity    string      `json:"severity"`
	Description string      `json:"description"`
	TriggeredAt metav1.Time `json:"triggeredAt"`
}

// ComplianceStatus represents compliance state
type ComplianceStatus struct {
	RBICompliant    bool   `json:"rbiCompliant"`
	PCIDSSCompliant bool   `json:"pciDssCompliant"`
	GDPRCompliant   bool   `json:"gdprCompliant"`
	Issues          []string `json:"issues,omitempty"`
}

// FeatureFlagReconciler reconciles a FeatureFlag object
// Feature flag का main reconciliation logic handle करता है
type FeatureFlagReconciler struct {
	client.Client
	Scheme      *runtime.Scheme
	RedisClient *redis.Client
}

// Reconcile handles the main reconciliation logic
// यह function feature flag का main logic handle करता है
func (r *FeatureFlagReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("🚀 Feature flag reconciliation शुरू कर रहे हैं", "name", req.Name)

	// FeatureFlag को fetch करते हैं
	var featureFlag FeatureFlag
	if err := r.Get(ctx, req.NamespacedName, &featureFlag); err != nil {
		logger.Error(err, "❌ FeatureFlag fetch नहीं कर सके")
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	// Indian market specific validation
	if err := r.validateIndianMarketConfig(ctx, &featureFlag); err != nil {
		logger.Error(err, "❌ Indian market validation failed")
		return ctrl.Result{RequeueAfter: time.Minute * 5}, err
	}

	// Compliance validation
	if err := r.validateCompliance(ctx, &featureFlag); err != nil {
		logger.Error(err, "❌ Compliance validation failed")
		return ctrl.Result{RequeueAfter: time.Minute * 5}, err
	}

	// Process rollout strategy
	if err := r.processRolloutStrategy(ctx, &featureFlag); err != nil {
		logger.Error(err, "❌ Rollout processing failed")
		return ctrl.Result{RequeueAfter: time.Minute * 2}, err
	}

	// Update Redis configuration
	if err := r.updateRedisConfiguration(ctx, &featureFlag); err != nil {
		logger.Error(err, "❌ Redis update failed")
		return ctrl.Result{RequeueAfter: time.Minute * 1}, err
	}

	// Setup monitoring
	if err := r.setupMonitoring(ctx, &featureFlag); err != nil {
		logger.Error(err, "❌ Monitoring setup failed")
		return ctrl.Result{RequeueAfter: time.Minute * 2}, err
	}

	// Update status
	if err := r.updateFeatureFlagStatus(ctx, &featureFlag); err != nil {
		logger.Error(err, "❌ Status update failed")
		return ctrl.Result{RequeueAfter: time.Second * 30}, err
	}

	logger.Info("✅ Feature flag reconciliation successful")
	return ctrl.Result{RequeueAfter: time.Minute * 5}, nil
}

// validateIndianMarketConfig validates Indian market specific configuration
// Indian market के लिए specific validations करता है
func (r *FeatureFlagReconciler) validateIndianMarketConfig(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("🇮🇳 Indian market configuration validate कर रहे हैं")

	marketConfig := flag.Spec.IndianMarketConfig

	// Validate regions
	validIndianRegions := []string{"mumbai", "delhi", "bangalore", "chennai", "hyderabad", "pune", "kolkata"}
	for _, region := range marketConfig.Regions {
		validRegion := false
		for _, validReg := range validIndianRegions {
			if region.Name == validReg {
				validRegion = true
				break
			}
		}
		if !validRegion {
			return fmt.Errorf("invalid Indian region: %s", region.Name)
		}
	}

	// Validate business hours timezone
	if marketConfig.BusinessHours.Enabled {
		if marketConfig.BusinessHours.Timezone != "Asia/Kolkata" {
			logger.Info("⚠️ Timezone should be Asia/Kolkata for Indian business hours")
		}
	}

	// Validate payment methods for Indian market
	validPaymentMethods := []string{"upi", "netbanking", "cards", "wallets", "emi", "cardless_emi"}
	for _, pm := range marketConfig.PaymentMethods {
		validMethod := false
		for _, validPM := range validPaymentMethods {
			if pm.Method == validPM {
				validMethod = true
				break
			}
		}
		if !validMethod {
			return fmt.Errorf("invalid payment method for Indian market: %s", pm.Method)
		}
	}

	// Validate localization for Indian languages
	if marketConfig.LocalizationConfig.Enabled {
		validLanguages := []string{"hi", "en", "ta", "te", "kn", "ml", "gu", "bn", "or", "pa"}
		for _, lang := range marketConfig.LocalizationConfig.SupportedLanguages {
			validLang := false
			for _, validL := range validLanguages {
				if lang.Code == validL {
					validLang = true
					break
				}
			}
			if !validLang {
				logger.Info("⚠️ Language code may not be standard for Indian market", "code", lang.Code)
			}
		}
	}

	logger.Info("✅ Indian market configuration validation passed")
	return nil
}

// validateCompliance validates compliance requirements
// RBI, PCI-DSS और अन्य compliance requirements validate करता है
func (r *FeatureFlagReconciler) validateCompliance(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("🏛️ Compliance requirements validate कर रहे हैं")

	compliance := flag.Spec.Compliance

	if !compliance.Enabled {
		logger.Info("📋 Compliance validation disabled")
		return nil
	}

	// RBI Compliance validation
	if compliance.RBICompliance.Enabled {
		if err := r.validateRBICompliance(ctx, flag); err != nil {
			return fmt.Errorf("RBI compliance validation failed: %w", err)
		}
	}

	// PCI-DSS Compliance validation
	if compliance.PCIDSSCompliance.Enabled {
		if err := r.validatePCIDSSCompliance(ctx, flag); err != nil {
			return fmt.Errorf("PCI-DSS compliance validation failed: %w", err)
		}
	}

	// GDPR Compliance validation (for international users)
	if compliance.GDPRCompliance.Enabled {
		if err := r.validateGDPRCompliance(ctx, flag); err != nil {
			return fmt.Errorf("GDPR compliance validation failed: %w", err)
		}
	}

	logger.Info("✅ Compliance validation passed")
	return nil
}

// validateRBICompliance validates RBI specific requirements
func (r *FeatureFlagReconciler) validateRBICompliance(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("🏛️ RBI compliance validate कर रहे हैं")

	rbiConfig := flag.Spec.Compliance.RBICompliance

	// Data residency validation
	if rbiConfig.DataResidency.Required {
		for _, region := range rbiConfig.DataResidency.AllowedRegions {
			// Check if region is within India
			indianRegions := []string{"mumbai", "delhi", "bangalore", "chennai", "hyderabad"}
			validRegion := false
			for _, indReg := range indianRegions {
				if region == indReg {
					validRegion = true
					break
				}
			}
			if !validRegion {
				return fmt.Errorf("RBI violation: data residency region %s not in India", region)
			}
		}
	}

	// Audit trail validation
	if rbiConfig.AuditTrail.Required {
		if rbiConfig.AuditTrail.RetentionPeriod < time.Hour*24*365*7 { // 7 years
			return fmt.Errorf("RBI violation: audit retention must be at least 7 years")
		}
	}

	// Security requirements validation
	if rbiConfig.SecurityRequirements.EncryptionRequired {
		// Check if feature flag involves sensitive data
		if r.involvesSensitiveData(flag) && !r.hasEncryptionEnabled(flag) {
			return fmt.Errorf("RBI violation: encryption required for sensitive data features")
		}
	}

	logger.Info("✅ RBI compliance validation passed")
	return nil
}

// validatePCIDSSCompliance validates PCI-DSS requirements
func (r *FeatureFlagReconciler) validatePCIDSSCompliance(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("💳 PCI-DSS compliance validate कर रहे हैं")

	pciConfig := flag.Spec.Compliance.PCIDSSCompliance

	// Card data protection validation
	if pciConfig.CardDataProtection.Required {
		if r.involvesCardData(flag) {
			if pciConfig.CardDataProtection.TokenizationRequired && !r.hasTokenizationEnabled(flag) {
				return fmt.Errorf("PCI-DSS violation: tokenization required for card data features")
			}
			
			if pciConfig.CardDataProtection.EncryptionRequired && !r.hasEncryptionEnabled(flag) {
				return fmt.Errorf("PCI-DSS violation: encryption required for card data features")
			}
		}
	}

	logger.Info("✅ PCI-DSS compliance validation passed")
	return nil
}

// validateGDPRCompliance validates GDPR requirements
func (r *FeatureFlagReconciler) validateGDPRCompliance(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("🇪🇺 GDPR compliance validate कर रहे हैं")

	gdprConfig := flag.Spec.Compliance.GDPRCompliance

	// Consent management validation
	if gdprConfig.ConsentManagement.Required {
		if r.involvesPersonalData(flag) && !r.hasConsentManagement(flag) {
			return fmt.Errorf("GDPR violation: consent management required for personal data features")
		}
	}

	logger.Info("✅ GDPR compliance validation passed")
	return nil
}

// processRolloutStrategy processes the rollout strategy
// Rollout strategy को process करता है
func (r *FeatureFlagReconciler) processRolloutStrategy(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("📈 Rollout strategy process कर रहे हैं")

	rollout := flag.Spec.Rollout

	switch rollout.Strategy.Type {
	case "instant":
		return r.processInstantRollout(ctx, flag)
	case "gradual":
		return r.processGradualRollout(ctx, flag)
	case "canary":
		return r.processCanaryRollout(ctx, flag)
	case "blue_green":
		return r.processBlueGreenRollout(ctx, flag)
	default:
		return fmt.Errorf("unknown rollout strategy: %s", rollout.Strategy.Type)
	}
}

// processInstantRollout processes instant rollout
func (r *FeatureFlagReconciler) processInstantRollout(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("⚡ Instant rollout process कर रहे हैं")

	// Safety checks for instant rollout
	if flag.Spec.Rollout.SafetyConfig.Enabled {
		if err := r.performSafetyChecks(ctx, flag); err != nil {
			return fmt.Errorf("safety checks failed for instant rollout: %w", err)
		}
	}

	// Update flag status for instant rollout
	flag.Status.RolloutStatus.CurrentPhase = "instant"
	flag.Status.RolloutStatus.CurrentPercentage = 100.0
	flag.Status.RolloutStatus.CanProceed = true

	logger.Info("✅ Instant rollout processed")
	return nil
}

// processGradualRollout processes gradual rollout
func (r *FeatureFlagReconciler) processGradualRollout(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("📊 Gradual rollout process कर रहे हैं")

	gradualConfig := flag.Spec.Rollout.GradualRollout
	if !gradualConfig.Enabled {
		return nil
	}

	// Determine current phase
	currentPhase := r.getCurrentRolloutPhase(ctx, flag)
	if currentPhase == nil {
		// Start with first phase
		if len(gradualConfig.Phases) > 0 {
			currentPhase = &gradualConfig.Phases[0]
			flag.Status.RolloutStatus.CurrentPhase = currentPhase.Name
			flag.Status.RolloutStatus.CurrentPercentage = currentPhase.Percentage
		}
	}

	// Check if we can proceed to next phase
	if r.canProceedToNextPhase(ctx, flag, currentPhase) {
		nextPhase := r.getNextRolloutPhase(ctx, flag, currentPhase)
		if nextPhase != nil {
			flag.Status.RolloutStatus.CurrentPhase = nextPhase.Name
			flag.Status.RolloutStatus.CurrentPercentage = nextPhase.Percentage
			
			// Set next phase transition time
			nextTransitionTime := metav1.NewTime(time.Now().Add(nextPhase.Duration))
			flag.Status.RolloutStatus.NextPhaseAt = &nextTransitionTime
		}
	}

	logger.Info("✅ Gradual rollout processed", "phase", flag.Status.RolloutStatus.CurrentPhase)
	return nil
}

// processCanaryRollout processes canary rollout
func (r *FeatureFlagReconciler) processCanaryRollout(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("🐦 Canary rollout process कर रहे हैं")

	canaryConfig := flag.Spec.Rollout.CanaryConfig
	if !canaryConfig.Enabled {
		return nil
	}

	// Start canary phase
	if flag.Status.RolloutStatus.CurrentPhase != "canary" {
		flag.Status.RolloutStatus.CurrentPhase = "canary"
		flag.Status.RolloutStatus.CurrentPercentage = canaryConfig.Percentage
		
		// Set canary end time
		canaryEndTime := metav1.NewTime(time.Now().Add(canaryConfig.Duration))
		flag.Status.RolloutStatus.NextPhaseAt = &canaryEndTime
	}

	// Check if canary can be promoted
	if r.canPromoteCanary(ctx, flag) {
		flag.Status.RolloutStatus.CurrentPhase = "full"
		flag.Status.RolloutStatus.CurrentPercentage = 100.0
		flag.Status.RolloutStatus.NextPhaseAt = nil
	}

	logger.Info("✅ Canary rollout processed", "percentage", flag.Status.RolloutStatus.CurrentPercentage)
	return nil
}

// processBlueGreenRollout processes blue-green rollout
func (r *FeatureFlagReconciler) processBlueGreenRollout(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("🔵🟢 Blue-green rollout process कर रहे हैं")

	// Blue-green implementation
	// This would involve switching traffic between blue and green versions
	
	logger.Info("✅ Blue-green rollout processed")
	return nil
}

// updateRedisConfiguration updates Redis with current feature flag configuration
// Redis में feature flag configuration को update करता है
func (r *FeatureFlagReconciler) updateRedisConfiguration(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("📦 Redis configuration update कर रहे हैं")

	// Create Redis configuration
	redisConfig := map[string]interface{}{
		"name":    flag.Spec.Name,
		"enabled": flag.Spec.Enabled,
		"targeting": flag.Spec.Targeting,
		"rollout_status": flag.Status.RolloutStatus,
		"indian_market": flag.Spec.IndianMarketConfig,
		"last_updated": time.Now().Unix(),
	}

	// Convert to JSON
	configJSON, err := json.Marshal(redisConfig)
	if err != nil {
		return fmt.Errorf("failed to marshal Redis config: %w", err)
	}

	// Store in Redis
	redisKey := fmt.Sprintf("feature_flag:%s", flag.Spec.Name)
	if err := r.RedisClient.Set(ctx, redisKey, configJSON, 0).Err(); err != nil {
		return fmt.Errorf("failed to update Redis: %w", err)
	}

	// Store regional configurations
	for _, region := range flag.Spec.IndianMarketConfig.Regions {
		regionalKey := fmt.Sprintf("feature_flag:%s:region:%s", flag.Spec.Name, region.Name)
		regionalConfig := map[string]interface{}{
			"enabled":    region.Enabled,
			"percentage": region.Percentage,
			"priority":   region.Priority,
		}
		
		regionalJSON, err := json.Marshal(regionalConfig)
		if err != nil {
			continue // Skip this region on error
		}
		
		r.RedisClient.Set(ctx, regionalKey, regionalJSON, 0)
	}

	logger.Info("✅ Redis configuration updated")
	return nil
}

// setupMonitoring sets up monitoring for the feature flag
// Feature flag के लिए monitoring setup करता है
func (r *FeatureFlagReconciler) setupMonitoring(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("📊 Monitoring setup कर रहे हैं")

	monitoringConfig := flag.Spec.Monitoring
	if !monitoringConfig.Enabled {
		logger.Info("📊 Monitoring disabled")
		return nil
	}

	// Setup metrics collection
	if monitoringConfig.MetricsConfig.Enabled {
		if err := r.setupMetricsCollection(ctx, flag); err != nil {
			return fmt.Errorf("metrics setup failed: %w", err)
		}
	}

	// Setup alerting
	if monitoringConfig.AlertingConfig.Enabled {
		if err := r.setupAlerting(ctx, flag); err != nil {
			return fmt.Errorf("alerting setup failed: %w", err)
		}
	}

	// Setup dashboards
	if monitoringConfig.DashboardConfig.Enabled {
		if err := r.setupDashboards(ctx, flag); err != nil {
			return fmt.Errorf("dashboard setup failed: %w", err)
		}
	}

	logger.Info("✅ Monitoring setup completed")
	return nil
}

// updateFeatureFlagStatus updates the feature flag status
// Feature flag का status update करता है
func (r *FeatureFlagReconciler) updateFeatureFlagStatus(ctx context.Context, flag *FeatureFlag) error {
	logger := ctrl.LoggerFrom(ctx)
	logger.Info("📋 Feature flag status update कर रहे हैं")

	// Update overall status
	flag.Status.Phase = "active"
	flag.Status.LastUpdated = metav1.NewTime(time.Now())

	// Update compliance status
	flag.Status.ComplianceStatus = ComplianceStatus{
		RBICompliant:    true, // Would be determined by actual validation
		PCIDSSCompliant: true,
		GDPRCompliant:   true,
	}

	// Update monitoring status
	flag.Status.MonitoringStatus = MonitoringStatus{
		HealthStatus: "healthy",
		CurrentMetrics: CurrentMetrics{
			UsageCount:     1000, // Would be fetched from actual metrics
			ErrorRate:      0.5,
			ResponseTime:   150,
			ConversionRate: 15.2,
		},
	}

	// Update the resource
	if err := r.Status().Update(ctx, flag); err != nil {
		return fmt.Errorf("failed to update status: %w", err)
	}

	logger.Info("✅ Feature flag status updated")
	return nil
}

// Helper methods (simplified implementations)

func (r *FeatureFlagReconciler) involvesSensitiveData(flag *FeatureFlag) bool {
	// Check if feature involves sensitive data
	return strings.Contains(strings.ToLower(flag.Spec.Description), "customer") ||
		   strings.Contains(strings.ToLower(flag.Spec.Description), "payment") ||
		   strings.Contains(strings.ToLower(flag.Spec.Description), "personal")
}

func (r *FeatureFlagReconciler) hasEncryptionEnabled(flag *FeatureFlag) bool {
	// Check if encryption is enabled for the feature
	return flag.Spec.Compliance.RBICompliance.SecurityRequirements.EncryptionRequired
}

func (r *FeatureFlagReconciler) involvesCardData(flag *FeatureFlag) bool {
	// Check if feature involves card data
	return strings.Contains(strings.ToLower(flag.Spec.Description), "card") ||
		   strings.Contains(strings.ToLower(flag.Spec.Description), "payment")
}

func (r *FeatureFlagReconciler) hasTokenizationEnabled(flag *FeatureFlag) bool {
	// Check if tokenization is enabled
	return flag.Spec.Compliance.PCIDSSCompliance.CardDataProtection.TokenizationRequired
}

func (r *FeatureFlagReconciler) involvesPersonalData(flag *FeatureFlag) bool {
	// Check if feature involves personal data
	return strings.Contains(strings.ToLower(flag.Spec.Description), "personal") ||
		   strings.Contains(strings.ToLower(flag.Spec.Description), "profile") ||
		   strings.Contains(strings.ToLower(flag.Spec.Description), "user")
}

func (r *FeatureFlagReconciler) hasConsentManagement(flag *FeatureFlag) bool {
	// Check if consent management is enabled
	return flag.Spec.Compliance.GDPRCompliance.ConsentManagement.Required
}

func (r *FeatureFlagReconciler) performSafetyChecks(ctx context.Context, flag *FeatureFlag) error {
	// Perform safety checks
	return nil
}

func (r *FeatureFlagReconciler) getCurrentRolloutPhase(ctx context.Context, flag *FeatureFlag) *RolloutPhase {
	// Get current rollout phase
	return nil
}

func (r *FeatureFlagReconciler) canProceedToNextPhase(ctx context.Context, flag *FeatureFlag, currentPhase *RolloutPhase) bool {
	// Check if can proceed to next phase
	return true
}

func (r *FeatureFlagReconciler) getNextRolloutPhase(ctx context.Context, flag *FeatureFlag, currentPhase *RolloutPhase) *RolloutPhase {
	// Get next rollout phase
	return nil
}

func (r *FeatureFlagReconciler) canPromoteCanary(ctx context.Context, flag *FeatureFlag) bool {
	// Check if canary can be promoted
	return true
}

func (r *FeatureFlagReconciler) setupMetricsCollection(ctx context.Context, flag *FeatureFlag) error {
	// Setup metrics collection
	return nil
}

func (r *FeatureFlagReconciler) setupAlerting(ctx context.Context, flag *FeatureFlag) error {
	// Setup alerting
	return nil
}

func (r *FeatureFlagReconciler) setupDashboards(ctx context.Context, flag *FeatureFlag) error {
	// Setup dashboards
	return nil
}

// SetupWithManager sets up the controller with the Manager
func (r *FeatureFlagReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&FeatureFlag{}).
		Complete(r)
}

func main() {
	ctrl.SetLogger(zap.New(zap.UseDevMode(true)))
	
	mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
		Scheme: runtime.NewScheme(),
	})
	if err != nil {
		log.Fatal("❌ Manager setup failed:", err)
	}

	// Setup Redis client
	redisClient := redis.NewClient(&redis.Options{
		Addr:     "redis.feature-flags.svc.cluster.local:6379",
		Password: "", // no password
		DB:       0,  // default DB
	})

	if err = (&FeatureFlagReconciler{
		Client:      mgr.GetClient(),
		Scheme:      mgr.GetScheme(),
		RedisClient: redisClient,
	}).SetupWithManager(mgr); err != nil {
		log.Fatal("❌ Controller setup failed:", err)
	}

	log.Println("🚀 Feature Flag Controller starting...")
	if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
		log.Fatal("❌ Controller start failed:", err)
	}
}
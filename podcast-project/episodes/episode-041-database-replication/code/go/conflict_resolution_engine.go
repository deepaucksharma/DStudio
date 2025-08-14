/*
Episode 41: Database Replication Strategies - Conflict Resolution Engine
Advanced conflict resolution for multi-master replication systems

यह implementation demonstrate करती है कि कैसे multi-master replication systems में
conflicts को intelligently resolve किया जाता है। जैसे Mumbai traffic में multiple
routes से same destination पहुंचने पर traffic police decisions लेता है कि कौन सा
vehicle पहले जाएगा, वैसे ही database conflicts में भी rules-based decisions लेने पड़ते हैं।

Real-world Usage:
- UPI Systems: Multiple banks simultaneously updating transaction status
- Flipkart: Inventory updates from different warehouses for same product
- HDFC Bank: Account balance updates from different branches/ATMs

Author: Hindi Tech Podcast Team
Episode: 41 - Database Replication Strategies
*/

package main

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"sort"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// ConflictType represents different types of conflicts
type ConflictType string

const (
	UpdateUpdateConflict ConflictType = "UPDATE_UPDATE"
	InsertInsertConflict ConflictType = "INSERT_INSERT" 
	DeleteUpdateConflict ConflictType = "DELETE_UPDATE"
	SchemaConflict       ConflictType = "SCHEMA_CONFLICT"
	ConstraintConflict   ConflictType = "CONSTRAINT_CONFLICT"
)

// ConflictResolutionStrategy represents different resolution strategies
type ConflictResolutionStrategy string

const (
	LastWriteWins       ConflictResolutionStrategy = "LAST_WRITE_WINS"
	FirstWriteWins      ConflictResolutionStrategy = "FIRST_WRITE_WINS"
	BusinessRules       ConflictResolutionStrategy = "BUSINESS_RULES"
	VectorClocks        ConflictResolutionStrategy = "VECTOR_CLOCKS"
	ApplicationMerge    ConflictResolutionStrategy = "APPLICATION_MERGE"
	ManualResolution    ConflictResolutionStrategy = "MANUAL_RESOLUTION"
	CRDTMerge          ConflictResolutionStrategy = "CRDT_MERGE"
)

// DataChange represents a change to data
type DataChange struct {
	ChangeID    string                 `json:"change_id"`
	NodeID      string                 `json:"node_id"`
	Table       string                 `json:"table"`
	PrimaryKey  map[string]interface{} `json:"primary_key"`
	Operation   string                 `json:"operation"` // INSERT, UPDATE, DELETE
	OldValues   map[string]interface{} `json:"old_values"`
	NewValues   map[string]interface{} `json:"new_values"`
	Timestamp   time.Time             `json:"timestamp"`
	VectorClock map[string]int        `json:"vector_clock"`
	Checksum    string                `json:"checksum"`
	Metadata    map[string]interface{} `json:"metadata"`
	Priority    int                   `json:"priority"` // Higher number = higher priority
}

// Conflict represents a detected conflict between changes
type Conflict struct {
	ConflictID   string              `json:"conflict_id"`
	Type         ConflictType        `json:"type"`
	Table        string             `json:"table"`
	PrimaryKey   map[string]interface{} `json:"primary_key"`
	LocalChange  *DataChange        `json:"local_change"`
	RemoteChange *DataChange        `json:"remote_change"`
	DetectedAt   time.Time          `json:"detected_at"`
	Severity     ConflictSeverity   `json:"severity"`
	
	// Resolution information
	Strategy     ConflictResolutionStrategy `json:"strategy"`
	Resolution   *ConflictResolution       `json:"resolution,omitempty"`
	Status       ConflictStatus            `json:"status"`
	ResolvedAt   *time.Time               `json:"resolved_at,omitempty"`
	ResolvedBy   string                   `json:"resolved_by,omitempty"`
}

// ConflictSeverity represents the severity of a conflict
type ConflictSeverity string

const (
	SeverityLow      ConflictSeverity = "LOW"
	SeverityMedium   ConflictSeverity = "MEDIUM" 
	SeverityHigh     ConflictSeverity = "HIGH"
	SeverityCritical ConflictSeverity = "CRITICAL"
)

// ConflictStatus represents the status of conflict resolution
type ConflictStatus string

const (
	StatusDetected   ConflictStatus = "DETECTED"
	StatusResolving  ConflictStatus = "RESOLVING"
	StatusResolved   ConflictStatus = "RESOLVED"
	StatusFailed     ConflictStatus = "FAILED"
	StatusManual     ConflictStatus = "MANUAL"
)

// ConflictResolution contains the resolution result
type ConflictResolution struct {
	ResolvedChange   *DataChange            `json:"resolved_change"`
	Strategy         ConflictResolutionStrategy `json:"strategy"`
	Confidence       float64                `json:"confidence"` // 0.0 to 1.0
	Explanation      string                 `json:"explanation"`
	BusinessRuleUsed string                 `json:"business_rule_used,omitempty"`
	ManualInput      map[string]interface{} `json:"manual_input,omitempty"`
}

// ConflictResolutionEngine manages conflict detection and resolution
type ConflictResolutionEngine struct {
	// Core components
	conflicts      map[string]*Conflict
	conflictsMux   sync.RWMutex
	
	// Business rules
	businessRules  map[string]*BusinessRule
	rulesMux       sync.RWMutex
	
	// Resolution strategies
	strategies     map[ConflictResolutionStrategy]ResolutionHandler
	
	// CRDT operations
	crdtOperations map[string]CRDTOperation
	
	// Metrics
	metrics struct {
		conflictsDetected  *prometheus.CounterVec
		conflictsResolved  *prometheus.CounterVec
		resolutionDuration *prometheus.HistogramVec
		manualInterventions *prometheus.CounterVec
	}
	
	// Statistics
	stats struct {
		totalConflicts      int64
		resolvedConflicts   int64
		manualConflicts     int64
		averageResolutionMs int64
	}
	
	// Configuration
	config ConflictEngineConfig
}

// ConflictEngineConfig holds configuration options
type ConflictEngineConfig struct {
	DefaultStrategy         ConflictResolutionStrategy `json:"default_strategy"`
	AutoResolveThreshold    float64                   `json:"auto_resolve_threshold"`
	ManualReviewThreshold   float64                   `json:"manual_review_threshold"`
	MaxResolutionTime       time.Duration             `json:"max_resolution_time"`
	EnableVectorClocks      bool                      `json:"enable_vector_clocks"`
	EnableBusinessRules     bool                      `json:"enable_business_rules"`
	CRDTEnabled            bool                      `json:"crdt_enabled"`
}

// BusinessRule represents a business-specific conflict resolution rule
type BusinessRule struct {
	RuleID      string                 `json:"rule_id"`
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Table       string                 `json:"table"`
	Conditions  map[string]interface{} `json:"conditions"`
	Resolution  ResolutionAction       `json:"resolution"`
	Priority    int                   `json:"priority"`
	Enabled     bool                  `json:"enabled"`
}

// ResolutionAction defines how to resolve a conflict
type ResolutionAction struct {
	Strategy    ConflictResolutionStrategy `json:"strategy"`
	FieldRules  map[string]string         `json:"field_rules"`  // field -> rule (sum, max, min, concat, etc.)
	Precedence  string                    `json:"precedence"`   // which change takes precedence
	CustomLogic string                    `json:"custom_logic,omitempty"`
}

// ResolutionHandler is a function that resolves conflicts
type ResolutionHandler func(*Conflict) (*ConflictResolution, error)

// CRDTOperation defines CRDT operations for different data types
type CRDTOperation interface {
	Merge(local, remote interface{}) interface{}
	Type() string
}

// CounterCRDT implements CRDT for counter operations (like inventory quantities)
type CounterCRDT struct{}

func (c CounterCRDT) Merge(local, remote interface{}) interface{} {
	localVal, localOk := local.(float64)
	remoteVal, remoteOk := remote.(float64)
	
	if !localOk || !remoteOk {
		return local // Fallback to local if types don't match
	}
	
	// For counters, we sum the values
	return localVal + remoteVal
}

func (c CounterCRDT) Type() string { return "counter" }

// SetCRDT implements CRDT for set operations
type SetCRDT struct{}

func (s SetCRDT) Merge(local, remote interface{}) interface{} {
	localSet, localOk := local.([]interface{})
	remoteSet, remoteOk := remote.([]interface{})
	
	if !localOk || !remoteOk {
		return local
	}
	
	// Merge sets (union)
	merged := make(map[interface{}]bool)
	for _, item := range localSet {
		merged[item] = true
	}
	for _, item := range remoteSet {
		merged[item] = true
	}
	
	result := make([]interface{}, 0, len(merged))
	for item := range merged {
		result = append(result, item)
	}
	
	return result
}

func (s SetCRDT) Type() string { return "set" }

// MaxCRDT implements CRDT for max operations (like highest price)
type MaxCRDT struct{}

func (m MaxCRDT) Merge(local, remote interface{}) interface{} {
	localVal, localOk := local.(float64)
	remoteVal, remoteOk := remote.(float64)
	
	if !localOk || !remoteOk {
		return local
	}
	
	if remoteVal > localVal {
		return remoteVal
	}
	return localVal
}

func (m MaxCRDT) Type() string { return "max" }

// NewConflictResolutionEngine creates a new conflict resolution engine
func NewConflictResolutionEngine(config ConflictEngineConfig) *ConflictResolutionEngine {
	engine := &ConflictResolutionEngine{
		conflicts:      make(map[string]*Conflict),
		businessRules:  make(map[string]*BusinessRule),
		strategies:     make(map[ConflictResolutionStrategy]ResolutionHandler),
		crdtOperations: make(map[string]CRDTOperation),
		config:        config,
	}
	
	// Initialize metrics
	engine.initMetrics()
	
	// Register default resolution strategies
	engine.registerDefaultStrategies()
	
	// Register CRDT operations
	engine.registerCRDTOperations()
	
	return engine
}

// initMetrics initializes Prometheus metrics
func (e *ConflictResolutionEngine) initMetrics() {
	e.metrics.conflictsDetected = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "conflicts_detected_total",
			Help: "Total number of conflicts detected",
		},
		[]string{"table", "type", "severity"},
	)
	
	e.metrics.conflictsResolved = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "conflicts_resolved_total", 
			Help: "Total number of conflicts resolved",
		},
		[]string{"table", "strategy", "status"},
	)
	
	e.metrics.resolutionDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "conflict_resolution_duration_seconds",
			Help: "Time taken to resolve conflicts",
		},
		[]string{"strategy", "table"},
	)
	
	e.metrics.manualInterventions = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "manual_interventions_total",
			Help: "Total number of manual interventions required",
		},
		[]string{"table", "reason"},
	)
	
	prometheus.MustRegister(
		e.metrics.conflictsDetected,
		e.metrics.conflictsResolved, 
		e.metrics.resolutionDuration,
		e.metrics.manualInterventions,
	)
}

// registerDefaultStrategies registers built-in resolution strategies
func (e *ConflictResolutionEngine) registerDefaultStrategies() {
	e.strategies[LastWriteWins] = e.lastWriteWinsResolver
	e.strategies[FirstWriteWins] = e.firstWriteWinsResolver
	e.strategies[BusinessRules] = e.businessRulesResolver
	e.strategies[VectorClocks] = e.vectorClockResolver
	e.strategies[ApplicationMerge] = e.applicationMergeResolver
	e.strategies[CRDTMerge] = e.crdtMergeResolver
}

// registerCRDTOperations registers CRDT operations
func (e *ConflictResolutionEngine) registerCRDTOperations() {
	e.crdtOperations["counter"] = CounterCRDT{}
	e.crdtOperations["set"] = SetCRDT{}
	e.crdtOperations["max"] = MaxCRDT{}
}

// DetectConflict detects conflicts between local and remote changes
func (e *ConflictResolutionEngine) DetectConflict(local, remote *DataChange) *Conflict {
	// Skip if changes are from the same node
	if local.NodeID == remote.NodeID {
		return nil
	}
	
	// Skip if changes are to different records
	if !e.sameRecord(local, remote) {
		return nil
	}
	
	// Detect conflict type
	conflictType := e.determineConflictType(local, remote)
	if conflictType == "" {
		return nil // No conflict
	}
	
	conflict := &Conflict{
		ConflictID:   e.generateConflictID(local, remote),
		Type:         conflictType,
		Table:        local.Table,
		PrimaryKey:   local.PrimaryKey,
		LocalChange:  local,
		RemoteChange: remote,
		DetectedAt:   time.Now(),
		Severity:     e.calculateSeverity(local, remote, conflictType),
		Status:       StatusDetected,
	}
	
	// Store conflict
	e.conflictsMux.Lock()
	e.conflicts[conflict.ConflictID] = conflict
	e.conflictsMux.Unlock()
	
	// Update metrics
	atomic.AddInt64(&e.stats.totalConflicts, 1)
	e.metrics.conflictsDetected.WithLabelValues(
		conflict.Table, string(conflict.Type), string(conflict.Severity)).Inc()
	
	log.Printf("🔥 Conflict detected: %s (%s) in table %s", 
		conflict.ConflictID, conflict.Type, conflict.Table)
	
	return conflict
}

// sameRecord checks if two changes affect the same record
func (e *ConflictResolutionEngine) sameRecord(local, remote *DataChange) bool {
	if local.Table != remote.Table {
		return false
	}
	
	// Compare primary keys
	for key, localValue := range local.PrimaryKey {
		remoteValue, exists := remote.PrimaryKey[key]
		if !exists || localValue != remoteValue {
			return false
		}
	}
	
	return true
}

// determineConflictType determines the type of conflict
func (e *ConflictResolutionEngine) determineConflictType(local, remote *DataChange) ConflictType {
	switch {
	case local.Operation == "UPDATE" && remote.Operation == "UPDATE":
		// Check if they modify the same fields
		if e.hasOverlappingFields(local.NewValues, remote.NewValues) {
			return UpdateUpdateConflict
		}
	case local.Operation == "INSERT" && remote.Operation == "INSERT":
		return InsertInsertConflict
	case (local.Operation == "DELETE" && remote.Operation == "UPDATE") ||
		 (local.Operation == "UPDATE" && remote.Operation == "DELETE"):
		return DeleteUpdateConflict
	}
	
	return "" // No conflict
}

// hasOverlappingFields checks if two change sets modify the same fields
func (e *ConflictResolutionEngine) hasOverlappingFields(local, remote map[string]interface{}) bool {
	for field := range local {
		if _, exists := remote[field]; exists {
			return true
		}
	}
	return false
}

// calculateSeverity calculates the severity of a conflict
func (e *ConflictResolutionEngine) calculateSeverity(local, remote *DataChange, conflictType ConflictType) ConflictSeverity {
	// Base severity on conflict type
	baseSeverity := SeverityMedium
	
	switch conflictType {
	case DeleteUpdateConflict:
		baseSeverity = SeverityHigh
	case InsertInsertConflict:
		baseSeverity = SeverityCritical // Can cause constraint violations
	case UpdateUpdateConflict:
		baseSeverity = SeverityMedium
	}
	
	// Increase severity based on business importance
	if e.isFinancialData(local.Table) {
		baseSeverity = SeverityCritical
	}
	
	if e.isInventoryData(local.Table) {
		baseSeverity = SeverityHigh
	}
	
	return baseSeverity
}

// isFinancialData checks if the table contains financial data
func (e *ConflictResolutionEngine) isFinancialData(tableName string) bool {
	financialTables := []string{"accounts", "transactions", "payments", "balances"}
	for _, table := range financialTables {
		if strings.Contains(strings.ToLower(tableName), table) {
			return true
		}
	}
	return false
}

// isInventoryData checks if the table contains inventory data
func (e *ConflictResolutionEngine) isInventoryData(tableName string) bool {
	inventoryTables := []string{"inventory", "stock", "products", "warehouse"}
	for _, table := range inventoryTables {
		if strings.Contains(strings.ToLower(tableName), table) {
			return true
		}
	}
	return false
}

// ResolveConflict resolves a conflict using the appropriate strategy
func (e *ConflictResolutionEngine) ResolveConflict(conflictID string) error {
	e.conflictsMux.Lock()
	conflict, exists := e.conflicts[conflictID]
	if !exists {
		e.conflictsMux.Unlock()
		return fmt.Errorf("conflict %s not found", conflictID)
	}
	conflict.Status = StatusResolving
	e.conflictsMux.Unlock()
	
	startTime := time.Now()
	
	// Select resolution strategy
	strategy := e.selectResolutionStrategy(conflict)
	conflict.Strategy = strategy
	
	log.Printf("🔧 Resolving conflict %s using strategy %s", conflictID, strategy)
	
	// Get resolution handler
	handler, exists := e.strategies[strategy]
	if !exists {
		return fmt.Errorf("no handler for strategy %s", strategy)
	}
	
	// Resolve conflict
	resolution, err := handler(conflict)
	if err != nil {
		conflict.Status = StatusFailed
		log.Printf("❌ Failed to resolve conflict %s: %v", conflictID, err)
		return err
	}
	
	// Check confidence level
	if resolution.Confidence < e.config.ManualReviewThreshold {
		conflict.Status = StatusManual
		atomic.AddInt64(&e.stats.manualConflicts, 1)
		e.metrics.manualInterventions.WithLabelValues(
			conflict.Table, "low_confidence").Inc()
		
		log.Printf("⚠️ Conflict %s requires manual review (confidence: %.2f)", 
			conflictID, resolution.Confidence)
		return nil
	}
	
	// Apply resolution
	conflict.Resolution = resolution
	conflict.Status = StatusResolved
	resolvedAt := time.Now()
	conflict.ResolvedAt = &resolvedAt
	conflict.ResolvedBy = "auto_resolver"
	
	duration := time.Since(startTime)
	atomic.AddInt64(&e.stats.resolvedConflicts, 1)
	atomic.StoreInt64(&e.stats.averageResolutionMs, duration.Milliseconds())
	
	// Update metrics
	e.metrics.conflictsResolved.WithLabelValues(
		conflict.Table, string(strategy), string(conflict.Status)).Inc()
	e.metrics.resolutionDuration.WithLabelValues(
		string(strategy), conflict.Table).Observe(duration.Seconds())
	
	log.Printf("✅ Resolved conflict %s in %v (confidence: %.2f)", 
		conflictID, duration, resolution.Confidence)
	
	return nil
}

// selectResolutionStrategy selects the best strategy for a conflict
func (e *ConflictResolutionEngine) selectResolutionStrategy(conflict *Conflict) ConflictResolutionStrategy {
	// Check if business rules are enabled and available
	if e.config.EnableBusinessRules {
		if e.hasApplicableBusinessRule(conflict) {
			return BusinessRules
		}
	}
	
	// Check if CRDT merge is applicable
	if e.config.CRDTEnabled {
		if e.canUseCRDT(conflict) {
			return CRDTMerge
		}
	}
	
	// Check if vector clocks are enabled
	if e.config.EnableVectorClocks {
		if e.hasVectorClockInfo(conflict) {
			return VectorClocks
		}
	}
	
	// Use severity-based strategy selection
	switch conflict.Severity {
	case SeverityCritical:
		return ManualResolution
	case SeverityHigh:
		return BusinessRules
	case SeverityMedium:
		return ApplicationMerge
	default:
		return e.config.DefaultStrategy
	}
}

// hasApplicableBusinessRule checks if there's a business rule for this conflict
func (e *ConflictResolutionEngine) hasApplicableBusinessRule(conflict *Conflict) bool {
	e.rulesMux.RLock()
	defer e.rulesMux.RUnlock()
	
	for _, rule := range e.businessRules {
		if rule.Enabled && rule.Table == conflict.Table {
			return true
		}
	}
	return false
}

// canUseCRDT checks if CRDT merge can be used
func (e *ConflictResolutionEngine) canUseCRDT(conflict *Conflict) bool {
	// Check if any fields have CRDT operations defined
	for field := range conflict.LocalChange.NewValues {
		if _, exists := e.crdtOperations[field]; exists {
			return true
		}
	}
	
	// Check for known CRDT-compatible fields
	crdtFields := []string{"quantity", "count", "amount", "tags", "score"}
	for _, field := range crdtFields {
		if _, localExists := conflict.LocalChange.NewValues[field]; localExists {
			if _, remoteExists := conflict.RemoteChange.NewValues[field]; remoteExists {
				return true
			}
		}
	}
	
	return false
}

// hasVectorClockInfo checks if vector clock information is available
func (e *ConflictResolutionEngine) hasVectorClockInfo(conflict *Conflict) bool {
	return len(conflict.LocalChange.VectorClock) > 0 && len(conflict.RemoteChange.VectorClock) > 0
}

// Resolution strategy implementations

// lastWriteWinsResolver resolves conflicts using last-write-wins
func (e *ConflictResolutionEngine) lastWriteWinsResolver(conflict *Conflict) (*ConflictResolution, error) {
	var winner *DataChange
	var explanation string
	
	if conflict.RemoteChange.Timestamp.After(conflict.LocalChange.Timestamp) {
		winner = conflict.RemoteChange
		explanation = fmt.Sprintf("Remote change is newer (%v vs %v)", 
			conflict.RemoteChange.Timestamp, conflict.LocalChange.Timestamp)
	} else {
		winner = conflict.LocalChange
		explanation = fmt.Sprintf("Local change is newer (%v vs %v)", 
			conflict.LocalChange.Timestamp, conflict.RemoteChange.Timestamp)
	}
	
	return &ConflictResolution{
		ResolvedChange: winner,
		Strategy:       LastWriteWins,
		Confidence:     0.8,
		Explanation:    explanation,
	}, nil
}

// firstWriteWinsResolver resolves conflicts using first-write-wins
func (e *ConflictResolutionEngine) firstWriteWinsResolver(conflict *Conflict) (*ConflictResolution, error) {
	var winner *DataChange
	var explanation string
	
	if conflict.LocalChange.Timestamp.Before(conflict.RemoteChange.Timestamp) {
		winner = conflict.LocalChange
		explanation = fmt.Sprintf("Local change is older (%v vs %v)", 
			conflict.LocalChange.Timestamp, conflict.RemoteChange.Timestamp)
	} else {
		winner = conflict.RemoteChange
		explanation = fmt.Sprintf("Remote change is older (%v vs %v)", 
			conflict.RemoteChange.Timestamp, conflict.LocalChange.Timestamp)
	}
	
	return &ConflictResolution{
		ResolvedChange: winner,
		Strategy:       FirstWriteWins,
		Confidence:     0.7,
		Explanation:    explanation,
	}, nil
}

// businessRulesResolver resolves conflicts using business rules
func (e *ConflictResolutionEngine) businessRulesResolver(conflict *Conflict) (*ConflictResolution, error) {
	e.rulesMux.RLock()
	defer e.rulesMux.RUnlock()
	
	// Find applicable business rule
	var applicableRule *BusinessRule
	for _, rule := range e.businessRules {
		if rule.Enabled && rule.Table == conflict.Table {
			if e.matchesConditions(conflict, rule) {
				if applicableRule == nil || rule.Priority > applicableRule.Priority {
					applicableRule = rule
				}
			}
		}
	}
	
	if applicableRule == nil {
		return nil, fmt.Errorf("no applicable business rule found")
	}
	
	// Apply business rule
	resolvedChange, err := e.applyBusinessRule(conflict, applicableRule)
	if err != nil {
		return nil, err
	}
	
	return &ConflictResolution{
		ResolvedChange:   resolvedChange,
		Strategy:         BusinessRules,
		Confidence:       0.9,
		Explanation:      fmt.Sprintf("Applied business rule: %s", applicableRule.Name),
		BusinessRuleUsed: applicableRule.RuleID,
	}, nil
}

// matchesConditions checks if conflict matches rule conditions
func (e *ConflictResolutionEngine) matchesConditions(conflict *Conflict, rule *BusinessRule) bool {
	for key, expectedValue := range rule.Conditions {
		switch key {
		case "conflict_type":
			if string(conflict.Type) != expectedValue.(string) {
				return false
			}
		case "severity":
			if string(conflict.Severity) != expectedValue.(string) {
				return false
			}
		case "field":
			field := expectedValue.(string)
			if _, exists := conflict.LocalChange.NewValues[field]; !exists {
				return false
			}
		}
	}
	return true
}

// applyBusinessRule applies a business rule to resolve conflict
func (e *ConflictResolutionEngine) applyBusinessRule(conflict *Conflict, rule *BusinessRule) (*DataChange, error) {
	switch rule.Resolution.Strategy {
	case LastWriteWins:
		if conflict.RemoteChange.Timestamp.After(conflict.LocalChange.Timestamp) {
			return conflict.RemoteChange, nil
		}
		return conflict.LocalChange, nil
		
	case FirstWriteWins:
		if conflict.LocalChange.Timestamp.Before(conflict.RemoteChange.Timestamp) {
			return conflict.LocalChange, nil
		}
		return conflict.RemoteChange, nil
		
	case ApplicationMerge:
		return e.mergeChanges(conflict, rule.Resolution.FieldRules)
		
	default:
		return nil, fmt.Errorf("unsupported resolution strategy in business rule: %s", rule.Resolution.Strategy)
	}
}

// mergeChanges merges two changes using field-specific rules
func (e *ConflictResolutionEngine) mergeChanges(conflict *Conflict, fieldRules map[string]string) (*DataChange, error) {
	merged := &DataChange{
		ChangeID:    e.generateChangeID(),
		NodeID:      "resolver",
		Table:       conflict.Table,
		PrimaryKey:  conflict.LocalChange.PrimaryKey,
		Operation:   "UPDATE",
		OldValues:   conflict.LocalChange.OldValues,
		NewValues:   make(map[string]interface{}),
		Timestamp:   time.Now(),
		VectorClock: e.mergeVectorClocks(conflict.LocalChange.VectorClock, conflict.RemoteChange.VectorClock),
	}
	
	// Start with local values
	for k, v := range conflict.LocalChange.NewValues {
		merged.NewValues[k] = v
	}
	
	// Apply remote values based on field rules
	for field, remoteValue := range conflict.RemoteChange.NewValues {
		localValue, hasLocal := conflict.LocalChange.NewValues[field]
		rule, hasRule := fieldRules[field]
		
		if !hasLocal {
			// Field only exists in remote, use it
			merged.NewValues[field] = remoteValue
			continue
		}
		
		if !hasRule {
			// No specific rule, use last-write-wins
			if conflict.RemoteChange.Timestamp.After(conflict.LocalChange.Timestamp) {
				merged.NewValues[field] = remoteValue
			}
			continue
		}
		
		// Apply field-specific rule
		mergedValue, err := e.applyFieldRule(localValue, remoteValue, rule)
		if err != nil {
			log.Printf("Error applying field rule for %s: %v", field, err)
			// Fallback to last-write-wins
			if conflict.RemoteChange.Timestamp.After(conflict.LocalChange.Timestamp) {
				merged.NewValues[field] = remoteValue
			}
		} else {
			merged.NewValues[field] = mergedValue
		}
	}
	
	return merged, nil
}

// applyFieldRule applies a specific rule to merge field values
func (e *ConflictResolutionEngine) applyFieldRule(local, remote interface{}, rule string) (interface{}, error) {
	switch rule {
	case "sum":
		localVal, localOk := local.(float64)
		remoteVal, remoteOk := remote.(float64)
		if localOk && remoteOk {
			return localVal + remoteVal, nil
		}
		
	case "max":
		localVal, localOk := local.(float64)
		remoteVal, remoteOk := remote.(float64)
		if localOk && remoteOk {
			if remoteVal > localVal {
				return remoteVal, nil
			}
			return localVal, nil
		}
		
	case "min":
		localVal, localOk := local.(float64)
		remoteVal, remoteOk := remote.(float64)
		if localOk && remoteOk {
			if remoteVal < localVal {
				return remoteVal, nil
			}
			return localVal, nil
		}
		
	case "concat":
		localStr := fmt.Sprintf("%v", local)
		remoteStr := fmt.Sprintf("%v", remote)
		return localStr + " | " + remoteStr, nil
		
	case "remote_wins":
		return remote, nil
		
	case "local_wins":
		return local, nil
	}
	
	return nil, fmt.Errorf("unknown field rule: %s", rule)
}

// vectorClockResolver resolves conflicts using vector clocks
func (e *ConflictResolutionEngine) vectorClockResolver(conflict *Conflict) (*ConflictResolution, error) {
	localClock := conflict.LocalChange.VectorClock
	remoteClock := conflict.RemoteChange.VectorClock
	
	// Compare vector clocks
	localDominates := true
	remoteDominates := true
	
	// Check all nodes in both clocks
	allNodes := make(map[string]bool)
	for node := range localClock {
		allNodes[node] = true
	}
	for node := range remoteClock {
		allNodes[node] = true
	}
	
	for node := range allNodes {
		localVersion := localClock[node]
		remoteVersion := remoteClock[node]
		
		if localVersion < remoteVersion {
			localDominates = false
		}
		if remoteVersion < localVersion {
			remoteDominates = false
		}
	}
	
	var winner *DataChange
	var explanation string
	var confidence float64
	
	if localDominates && !remoteDominates {
		winner = conflict.LocalChange
		explanation = "Local change dominates according to vector clock"
		confidence = 0.95
	} else if remoteDominates && !localDominates {
		winner = conflict.RemoteChange
		explanation = "Remote change dominates according to vector clock"
		confidence = 0.95
	} else {
		// Concurrent updates - fall back to last-write-wins
		if conflict.RemoteChange.Timestamp.After(conflict.LocalChange.Timestamp) {
			winner = conflict.RemoteChange
		} else {
			winner = conflict.LocalChange
		}
		explanation = "Concurrent updates detected, using timestamp as tiebreaker"
		confidence = 0.6
	}
	
	return &ConflictResolution{
		ResolvedChange: winner,
		Strategy:       VectorClocks,
		Confidence:     confidence,
		Explanation:    explanation,
	}, nil
}

// applicationMergeResolver resolves conflicts by merging application data
func (e *ConflictResolutionEngine) applicationMergeResolver(conflict *Conflict) (*ConflictResolution, error) {
	// Use intelligent field merging
	defaultRules := map[string]string{
		"quantity":    "sum",
		"amount":      "sum", 
		"price":       "max",
		"score":       "max",
		"description": "concat",
		"tags":        "concat",
		"updated_by":  "remote_wins",
		"version":     "max",
	}
	
	merged, err := e.mergeChanges(conflict, defaultRules)
	if err != nil {
		return nil, err
	}
	
	return &ConflictResolution{
		ResolvedChange: merged,
		Strategy:       ApplicationMerge,
		Confidence:     0.8,
		Explanation:    "Merged using intelligent field-level rules",
	}, nil
}

// crdtMergeResolver resolves conflicts using CRDT operations
func (e *ConflictResolutionEngine) crdtMergeResolver(conflict *Conflict) (*ConflictResolution, error) {
	merged := &DataChange{
		ChangeID:   e.generateChangeID(),
		NodeID:     "crdt_resolver",
		Table:      conflict.Table,
		PrimaryKey: conflict.LocalChange.PrimaryKey,
		Operation:  "UPDATE",
		OldValues:  conflict.LocalChange.OldValues,
		NewValues:  make(map[string]interface{}),
		Timestamp:  time.Now(),
		VectorClock: e.mergeVectorClocks(conflict.LocalChange.VectorClock, conflict.RemoteChange.VectorClock),
	}
	
	// Start with local values
	for k, v := range conflict.LocalChange.NewValues {
		merged.NewValues[k] = v
	}
	
	// Apply CRDT merging
	mergedFields := 0
	for field, remoteValue := range conflict.RemoteChange.NewValues {
		localValue, hasLocal := conflict.LocalChange.NewValues[field]
		if !hasLocal {
			merged.NewValues[field] = remoteValue
			continue
		}
		
		// Try to find CRDT operation for this field
		var crdtOp CRDTOperation
		
		// Direct field mapping
		if op, exists := e.crdtOperations[field]; exists {
			crdtOp = op
		} else {
			// Pattern-based mapping
			switch {
			case strings.Contains(field, "quantity") || strings.Contains(field, "count"):
				crdtOp = e.crdtOperations["counter"]
			case strings.Contains(field, "tags") || strings.Contains(field, "list"):
				crdtOp = e.crdtOperations["set"]
			case strings.Contains(field, "score") || strings.Contains(field, "rating"):
				crdtOp = e.crdtOperations["max"]
			}
		}
		
		if crdtOp != nil {
			merged.NewValues[field] = crdtOp.Merge(localValue, remoteValue)
			mergedFields++
		} else {
			// Fallback to last-write-wins
			if conflict.RemoteChange.Timestamp.After(conflict.LocalChange.Timestamp) {
				merged.NewValues[field] = remoteValue
			}
		}
	}
	
	confidence := 0.7
	if mergedFields > 0 {
		confidence = 0.9 // Higher confidence if we actually used CRDT operations
	}
	
	return &ConflictResolution{
		ResolvedChange: merged,
		Strategy:       CRDTMerge,
		Confidence:     confidence,
		Explanation:    fmt.Sprintf("CRDT merge applied to %d fields", mergedFields),
	}, nil
}

// Helper functions

// generateConflictID generates a unique conflict ID
func (e *ConflictResolutionEngine) generateConflictID(local, remote *DataChange) string {
	data := fmt.Sprintf("%s-%s-%s-%d-%d", 
		local.ChangeID, remote.ChangeID, local.Table,
		local.Timestamp.Unix(), remote.Timestamp.Unix())
	
	hash := sha256.Sum256([]byte(data))
	return fmt.Sprintf("conflict_%x", hash[:8])
}

// generateChangeID generates a unique change ID
func (e *ConflictResolutionEngine) generateChangeID() string {
	return fmt.Sprintf("change_%d_%d", time.Now().Unix(), rand.Int63())
}

// mergeVectorClocks merges two vector clocks
func (e *ConflictResolutionEngine) mergeVectorClocks(local, remote map[string]int) map[string]int {
	merged := make(map[string]int)
	
	// Start with local clock
	for node, version := range local {
		merged[node] = version
	}
	
	// Merge remote clock (take max version for each node)
	for node, version := range remote {
		if existing, exists := merged[node]; !exists || version > existing {
			merged[node] = version
		}
	}
	
	return merged
}

// AddBusinessRule adds a new business rule
func (e *ConflictResolutionEngine) AddBusinessRule(rule *BusinessRule) {
	e.rulesMux.Lock()
	defer e.rulesMux.Unlock()
	
	e.businessRules[rule.RuleID] = rule
	log.Printf("Added business rule: %s for table %s", rule.Name, rule.Table)
}

// GetConflictStats returns conflict resolution statistics
func (e *ConflictResolutionEngine) GetConflictStats() map[string]interface{} {
	e.conflictsMux.RLock()
	defer e.conflictsMux.RUnlock()
	
	stats := map[string]interface{}{
		"total_conflicts":         atomic.LoadInt64(&e.stats.totalConflicts),
		"resolved_conflicts":      atomic.LoadInt64(&e.stats.resolvedConflicts),
		"manual_conflicts":        atomic.LoadInt64(&e.stats.manualConflicts),
		"average_resolution_ms":   atomic.LoadInt64(&e.stats.averageResolutionMs),
		"pending_conflicts":       len(e.conflicts),
	}
	
	// Count by status
	statusCounts := make(map[ConflictStatus]int)
	severityCounts := make(map[ConflictSeverity]int)
	typeCounts := make(map[ConflictType]int)
	
	for _, conflict := range e.conflicts {
		statusCounts[conflict.Status]++
		severityCounts[conflict.Severity]++
		typeCounts[conflict.Type]++
	}
	
	stats["by_status"] = statusCounts
	stats["by_severity"] = severityCounts
	stats["by_type"] = typeCounts
	
	return stats
}

// SetupHTTPEndpoints sets up HTTP endpoints for monitoring
func (e *ConflictResolutionEngine) SetupHTTPEndpoints() {
	http.HandleFunc("/conflicts", e.conflictsHandler)
	http.HandleFunc("/conflicts/stats", e.statsHandler)
	http.HandleFunc("/conflicts/resolve", e.resolveHandler)
	http.Handle("/metrics", promhttp.Handler())
}

// conflictsHandler provides conflict listing endpoint
func (e *ConflictResolutionEngine) conflictsHandler(w http.ResponseWriter, r *http.Request) {
	e.conflictsMux.RLock()
	conflicts := make([]*Conflict, 0, len(e.conflicts))
	for _, conflict := range e.conflicts {
		conflicts = append(conflicts, conflict)
	}
	e.conflictsMux.RUnlock()
	
	// Sort by detected time (newest first)
	sort.Slice(conflicts, func(i, j int) bool {
		return conflicts[i].DetectedAt.After(conflicts[j].DetectedAt)
	})
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(conflicts)
}

// statsHandler provides conflict statistics
func (e *ConflictResolutionEngine) statsHandler(w http.ResponseWriter, r *http.Request) {
	stats := e.GetConflictStats()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

// resolveHandler provides conflict resolution endpoint
func (e *ConflictResolutionEngine) resolveHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}
	
	conflictID := r.URL.Query().Get("conflict_id")
	if conflictID == "" {
		http.Error(w, "conflict_id is required", http.StatusBadRequest)
		return
	}
	
	err := e.ResolveConflict(conflictID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "resolved"})
}

// Demo functions for Indian business scenarios

func setupHDFCBankingRules(engine *ConflictResolutionEngine) {
	// Banking rule: For account balance conflicts, always sum the amounts
	balanceRule := &BusinessRule{
		RuleID:      "hdfc_balance_sum",
		Name:        "HDFC Account Balance Summation",
		Description: "Sum account balance changes from multiple sources",
		Table:       "accounts",
		Conditions: map[string]interface{}{
			"field": "balance",
		},
		Resolution: ResolutionAction{
			Strategy: ApplicationMerge,
			FieldRules: map[string]string{
				"balance": "sum",
				"updated_by": "concat",
				"last_transaction_id": "remote_wins",
			},
		},
		Priority: 10,
		Enabled:  true,
	}
	
	// Banking rule: For transaction conflicts, use timestamp priority
	transactionRule := &BusinessRule{
		RuleID:      "hdfc_transaction_timestamp",
		Name:        "HDFC Transaction Timestamp Priority",
		Description: "Resolve transaction conflicts using timestamp ordering",
		Table:       "transactions",
		Conditions: map[string]interface{}{
			"conflict_type": "UPDATE_UPDATE",
		},
		Resolution: ResolutionAction{
			Strategy: LastWriteWins,
		},
		Priority: 9,
		Enabled:  true,
	}
	
	engine.AddBusinessRule(balanceRule)
	engine.AddBusinessRule(transactionRule)
}

func setupFlipkartInventoryRules(engine *ConflictResolutionEngine) {
	// Inventory rule: For quantity conflicts, use conservative minimum
	quantityRule := &BusinessRule{
		RuleID:      "flipkart_quantity_conservative",
		Name:        "Flipkart Conservative Inventory",
		Description: "Use minimum quantity to prevent overselling",
		Table:       "inventory",
		Conditions: map[string]interface{}{
			"field": "quantity",
		},
		Resolution: ResolutionAction{
			Strategy: ApplicationMerge,
			FieldRules: map[string]string{
				"quantity": "min",
				"reserved": "max",
				"updated_by": "concat",
			},
		},
		Priority: 10,
		Enabled:  true,
	}
	
	// Product rule: For price conflicts, use maximum price
	priceRule := &BusinessRule{
		RuleID:      "flipkart_price_max",
		Name:        "Flipkart Maximum Price Rule",
		Description: "Use maximum price for product conflicts",
		Table:       "products",
		Conditions: map[string]interface{}{
			"field": "price",
		},
		Resolution: ResolutionAction{
			Strategy: ApplicationMerge,
			FieldRules: map[string]string{
				"price": "max",
				"description": "concat",
				"tags": "concat",
			},
		},
		Priority: 8,
		Enabled:  true,
	}
	
	engine.AddBusinessRule(quantityRule)
	engine.AddBusinessRule(priceRule)
}

func simulateConflicts(engine *ConflictResolutionEngine) {
	log.Println("🔥 Simulating real-world conflicts...")
	
	conflicts := []struct {
		name         string
		localChange  *DataChange
		remoteChange *DataChange
	}{
		{
			name: "HDFC Account Balance Conflict",
			localChange: &DataChange{
				ChangeID: "local_hdfc_001",
				NodeID:   "mumbai_branch",
				Table:    "accounts",
				PrimaryKey: map[string]interface{}{
					"account_id": "HDFC123456789",
				},
				Operation: "UPDATE",
				OldValues: map[string]interface{}{
					"balance": 50000.0,
				},
				NewValues: map[string]interface{}{
					"balance":    52000.0,
					"updated_by": "ATM_DEPOSIT",
				},
				Timestamp:   time.Now().Add(-2 * time.Minute),
				VectorClock: map[string]int{"mumbai": 5, "bangalore": 3},
			},
			remoteChange: &DataChange{
				ChangeID: "remote_hdfc_001", 
				NodeID:   "bangalore_branch",
				Table:    "accounts",
				PrimaryKey: map[string]interface{}{
					"account_id": "HDFC123456789",
				},
				Operation: "UPDATE",
				OldValues: map[string]interface{}{
					"balance": 50000.0,
				},
				NewValues: map[string]interface{}{
					"balance":    48000.0,
					"updated_by": "ONLINE_PAYMENT",
				},
				Timestamp:   time.Now().Add(-1 * time.Minute),
				VectorClock: map[string]int{"mumbai": 4, "bangalore": 4},
			},
		},
		{
			name: "Flipkart Inventory Quantity Conflict",
			localChange: &DataChange{
				ChangeID: "local_fk_001",
				NodeID:   "mumbai_warehouse",
				Table:    "inventory", 
				PrimaryKey: map[string]interface{}{
					"product_id":   "FKRT1234567890",
					"warehouse_id": "WH_MUM_001",
				},
				Operation: "UPDATE",
				OldValues: map[string]interface{}{
					"quantity": 100,
				},
				NewValues: map[string]interface{}{
					"quantity":   85,
					"reserved":   10,
					"updated_by": "SALE_ORDER",
				},
				Timestamp:   time.Now().Add(-30 * time.Second),
				VectorClock: map[string]int{"mumbai": 8, "bangalore": 6},
			},
			remoteChange: &DataChange{
				ChangeID: "remote_fk_001",
				NodeID:   "bangalore_warehouse",
				Table:    "inventory",
				PrimaryKey: map[string]interface{}{
					"product_id":   "FKRT1234567890", 
					"warehouse_id": "WH_MUM_001",
				},
				Operation: "UPDATE",
				OldValues: map[string]interface{}{
					"quantity": 100,
				},
				NewValues: map[string]interface{}{
					"quantity":   95,
					"reserved":   5,
					"updated_by": "STOCK_ADJUSTMENT",
				},
				Timestamp:   time.Now().Add(-45 * time.Second),
				VectorClock: map[string]int{"mumbai": 7, "bangalore": 7},
			},
		},
		{
			name: "UPI Transaction Status Conflict",
			localChange: &DataChange{
				ChangeID: "local_upi_001",
				NodeID:   "upi_switch_mumbai",
				Table:    "upi_transactions",
				PrimaryKey: map[string]interface{}{
					"transaction_id": "UPI2024031512345678",
				},
				Operation: "UPDATE",
				OldValues: map[string]interface{}{
					"status": "PENDING",
				},
				NewValues: map[string]interface{}{
					"status":      "SUCCESS",
					"completed_at": time.Now().Format(time.RFC3339),
					"response_code": "00",
				},
				Timestamp:   time.Now().Add(-5 * time.Second),
				VectorClock: map[string]int{"mumbai": 12, "delhi": 10},
			},
			remoteChange: &DataChange{
				ChangeID: "remote_upi_001",
				NodeID:   "upi_switch_delhi",
				Table:    "upi_transactions",
				PrimaryKey: map[string]interface{}{
					"transaction_id": "UPI2024031512345678",
				},
				Operation: "UPDATE",
				OldValues: map[string]interface{}{
					"status": "PENDING",
				},
				NewValues: map[string]interface{}{
					"status":       "FAILED",
					"failed_at":    time.Now().Format(time.RFC3339),
					"error_code":   "U30",
					"error_message": "Insufficient balance",
				},
				Timestamp:   time.Now().Add(-3 * time.Second),
				VectorClock: map[string]int{"mumbai": 11, "delhi": 11},
			},
		},
	}
	
	for i, scenario := range conflicts {
		log.Printf("Scenario %d: %s", i+1, scenario.name)
		
		// Detect conflict
		conflict := engine.DetectConflict(scenario.localChange, scenario.remoteChange)
		if conflict != nil {
			log.Printf("  ✅ Conflict detected: %s (%s)", conflict.ConflictID, conflict.Type)
			
			// Resolve conflict
			err := engine.ResolveConflict(conflict.ConflictID)
			if err != nil {
				log.Printf("  ❌ Resolution failed: %v", err)
			} else {
				engine.conflictsMux.RLock()
				if resolvedConflict, exists := engine.conflicts[conflict.ConflictID]; exists {
					log.Printf("  ✅ Resolved using %s (confidence: %.2f)", 
						resolvedConflict.Strategy, 
						resolvedConflict.Resolution.Confidence)
				}
				engine.conflictsMux.RUnlock()
			}
		} else {
			log.Printf("  ℹ️ No conflict detected")
		}
		
		time.Sleep(time.Second)
	}
}

func main() {
	fmt.Println("🔥 Conflict Resolution Engine")
	fmt.Println("Episode 41: Advanced Multi-Master Conflict Resolution")
	fmt.Println(strings.Repeat("=", 65))
	
	// Configuration
	config := ConflictEngineConfig{
		DefaultStrategy:         LastWriteWins,
		AutoResolveThreshold:    0.7,
		ManualReviewThreshold:   0.5,
		MaxResolutionTime:       30 * time.Second,
		EnableVectorClocks:      true,
		EnableBusinessRules:     true,
		CRDTEnabled:            true,
	}
	
	// Create engine
	engine := NewConflictResolutionEngine(config)
	
	// Setup HTTP endpoints
	engine.SetupHTTPEndpoints()
	go func() {
		log.Printf("Starting HTTP server on :8081")
		if err := http.ListenAndServe(":8081", nil); err != nil {
			log.Printf("HTTP server error: %v", err)
		}
	}()
	
	fmt.Printf("\n🏦 Setting up HDFC Banking business rules...")
	setupHDFCBankingRules(engine)
	
	fmt.Printf("\n🛒 Setting up Flipkart Inventory business rules...")
	setupFlipkartInventoryRules(engine)
	
	fmt.Printf("\n📊 System Configuration:")
	fmt.Printf("  • Default Strategy: %s\n", config.DefaultStrategy)
	fmt.Printf("  • Auto-resolve Threshold: %.2f\n", config.AutoResolveThreshold)
	fmt.Printf("  • Manual Review Threshold: %.2f\n", config.ManualReviewThreshold)
	fmt.Printf("  • Vector Clocks: %t\n", config.EnableVectorClocks)
	fmt.Printf("  • Business Rules: %t\n", config.EnableBusinessRules)
	fmt.Printf("  • CRDT Support: %t\n", config.CRDTEnabled)
	fmt.Printf("  • Monitoring: http://localhost:8081\n")
	
	// Run conflict simulation
	fmt.Println("\n🔄 Running conflict simulation...")
	simulateConflicts(engine)
	
	// Show statistics
	fmt.Println("\n📊 Final Statistics:")
	stats := engine.GetConflictStats()
	
	fmt.Printf("Total Conflicts: %v\n", stats["total_conflicts"])
	fmt.Printf("Resolved Conflicts: %v\n", stats["resolved_conflicts"])
	fmt.Printf("Manual Interventions: %v\n", stats["manual_conflicts"])
	fmt.Printf("Average Resolution Time: %vms\n", stats["average_resolution_ms"])
	
	if byType, ok := stats["by_type"].(map[ConflictType]int); ok {
		fmt.Println("\nConflicts by Type:")
		for conflictType, count := range byType {
			fmt.Printf("  %s: %d\n", conflictType, count)
		}
	}
	
	if bySeverity, ok := stats["by_severity"].(map[ConflictSeverity]int); ok {
		fmt.Println("\nConflicts by Severity:")
		for severity, count := range bySeverity {
			fmt.Printf("  %s: %d\n", severity, count)
		}
	}
	
	if byStatus, ok := stats["by_status"].(map[ConflictStatus]int); ok {
		fmt.Println("\nConflicts by Status:")
		for status, count := range byStatus {
			fmt.Printf("  %s: %d\n", status, count)
		}
	}
	
	fmt.Println("\n✅ Demo completed successfully!")
	fmt.Println("\n💡 Key Features Demonstrated:")
	fmt.Println("  • Multi-strategy conflict resolution")
	fmt.Println("  • Business rules for Indian banking/e-commerce")
	fmt.Println("  • Vector clock-based resolution")
	fmt.Println("  • CRDT merge operations")
	fmt.Println("  • Automatic confidence scoring")
	fmt.Println("  • Real-time conflict detection")
	fmt.Println("  • Production-ready monitoring")
	
	// Keep server running for monitoring
	fmt.Println("\n⏳ Server running for monitoring (30 seconds)...")
	time.Sleep(30 * time.Second)
}

/*
Key Learning Points from Conflict Resolution Engine:

1. **Multi-Strategy Resolution**:
   - Last-Write-Wins for simple timestamp-based resolution
   - Vector Clocks for causality-aware resolution
   - Business Rules for domain-specific resolution
   - CRDT Merge for mathematical conflict-free resolution

2. **Indian Business Context**:
   - HDFC Banking: Account balance conflicts with summation rules
   - Flipkart Inventory: Conservative quantity resolution to prevent overselling
   - UPI Transactions: Critical transaction status conflict resolution
   - Business-specific field rules (sum, min, max, concat)

3. **Production Features**:
   - Confidence scoring for resolution quality
   - Manual intervention thresholds
   - Comprehensive metrics and monitoring
   - REST API for conflict management
   - Severity-based conflict prioritization

4. **Advanced Techniques**:
   - Vector clock comparison for causality
   - CRDT operations for different data types
   - Application-level field merging
   - Business rule priority system

This implementation provides a production-ready conflict resolution
system that can handle the complexity and scale of Indian financial
and e-commerce multi-master replication scenarios.
*/
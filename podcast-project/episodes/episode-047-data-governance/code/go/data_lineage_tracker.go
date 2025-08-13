// Data Lineage Tracker
// डेटा वंशावली ट्रैकर
//
// Real-world example: Swiggy's data lineage tracking system
// Tracks data flow from source to destination across systems

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"sort"
	"strings"
	"time"
)

// DataSource represents a data source
// डेटा स्रोत का प्रतिनिधित्व करता है
type DataSource struct {
	ID          string            `json:"id"`
	Name        string            `json:"name"`
	Type        string            `json:"type"` // database, api, file, stream
	Location    string            `json:"location"`
	Owner       string            `json:"owner"`
	Metadata    map[string]string `json:"metadata"`
	CreatedAt   time.Time         `json:"created_at"`
	UpdatedAt   time.Time         `json:"updated_at"`
	IsActive    bool              `json:"is_active"`
	Sensitivity string            `json:"sensitivity"` // public, internal, confidential, restricted
}

// DataTransformation represents a data transformation step
// डेटा रूपांतरण चरण का प्रतिनिधित्व करता है
type DataTransformation struct {
	ID              string            `json:"id"`
	Name            string            `json:"name"`
	Type            string            `json:"type"` // etl, stream_processing, aggregation, filtering
	Description     string            `json:"description"`
	TransformSQL    string            `json:"transform_sql,omitempty"`
	TransformCode   string            `json:"transform_code,omitempty"`
	BusinessLogic   string            `json:"business_logic"`
	Owner           string            `json:"owner"`
	ProcessingTime  time.Duration     `json:"processing_time"`
	Metadata        map[string]string `json:"metadata"`
	CreatedAt       time.Time         `json:"created_at"`
	IsActive        bool              `json:"is_active"`
	QualityRules    []string          `json:"quality_rules"`
	ComplianceFlags []string          `json:"compliance_flags"`
}

// DataLineageNode represents a node in the lineage graph
// वंशावली ग्राफ में एक नोड का प्रतिनिधित्व करता है
type DataLineageNode struct {
	ID         string                 `json:"id"`
	Name       string                 `json:"name"`
	Type       string                 `json:"type"` // source, transformation, destination
	Level      int                    `json:"level"`
	Attributes map[string]interface{} `json:"attributes"`
	CreatedAt  time.Time              `json:"created_at"`
	UpdatedAt  time.Time              `json:"updated_at"`
}

// DataLineageEdge represents a connection between nodes
// नोड्स के बीच कनेक्शन का प्रतिनिधित्व करता है
type DataLineageEdge struct {
	ID                string            `json:"id"`
	SourceNodeID      string            `json:"source_node_id"`
	DestinationNodeID string            `json:"destination_node_id"`
	RelationshipType  string            `json:"relationship_type"` // reads_from, writes_to, transforms
	DataVolume        int64             `json:"data_volume"`
	LastProcessed     time.Time         `json:"last_processed"`
	Metadata          map[string]string `json:"metadata"`
	IsActive          bool              `json:"is_active"`
}

// LineageGraph represents the complete data lineage graph
// संपूर्ण डेटा वंशावली ग्राफ का प्रतिनिधित्व करता है
type LineageGraph struct {
	Nodes map[string]*DataLineageNode `json:"nodes"`
	Edges map[string]*DataLineageEdge `json:"edges"`
}

// ImpactAnalysisResult represents impact analysis results
// प्रभाव विश्लेषण परिणाम का प्रतिनिधित्व करता है
type ImpactAnalysisResult struct {
	SourceNode      string   `json:"source_node"`
	ImpactedNodes   []string `json:"impacted_nodes"`
	ImpactLevel     string   `json:"impact_level"` // low, medium, high, critical
	AffectedSystems []string `json:"affected_systems"`
	BusinessImpact  string   `json:"business_impact"`
	RecommendedActions []string `json:"recommended_actions"`
}

// SwiggyDataLineageTracker tracks data lineage for Swiggy's systems
// स्विगी डेटा लाइनेज ट्रैकर स्विगी के सिस्टम के लिए डेटा वंशावली को ट्रैक करता है
type SwiggyDataLineageTracker struct {
	lineageGraph    LineageGraph
	dataSources     map[string]*DataSource
	transformations map[string]*DataTransformation
	auditLog        []map[string]interface{}
}

// NewSwiggyDataLineageTracker creates a new data lineage tracker
// नया डेटा लाइनेज ट्रैकर बनाता है
func NewSwiggyDataLineageTracker() *SwiggyDataLineageTracker {
	tracker := &SwiggyDataLineageTracker{
		lineageGraph: LineageGraph{
			Nodes: make(map[string]*DataLineageNode),
			Edges: make(map[string]*DataLineageEdge),
		},
		dataSources:     make(map[string]*DataSource),
		transformations: make(map[string]*DataTransformation),
		auditLog:        make([]map[string]interface{}, 0),
	}
	
	tracker.initializeSwiggyDataSources()
	return tracker
}

// initializeSwiggyDataSources sets up Swiggy's data sources
// स्विगी के डेटा स्रोत सेट करता है
func (slt *SwiggyDataLineageTracker) initializeSwiggyDataSources() {
	fmt.Println("🔧 Initializing Swiggy data sources...")
	
	// Customer data source
	customerSource := &DataSource{
		ID:          "src_customers",
		Name:        "Customer Database",
		Type:        "database",
		Location:    "mysql://customers.swiggy.in",
		Owner:       "customer-team@swiggy.com",
		Sensitivity: "confidential",
		Metadata: map[string]string{
			"schema_version": "2.1",
			"encryption":     "AES-256",
			"region":         "ap-south-1",
			"compliance":     "DPDP_Act",
		},
		CreatedAt: time.Now().AddDate(0, -6, 0),
		UpdatedAt: time.Now(),
		IsActive:  true,
	}
	
	// Restaurant data source
	restaurantSource := &DataSource{
		ID:          "src_restaurants",
		Name:        "Restaurant Partner Database",
		Type:        "database",
		Location:    "postgres://restaurants.swiggy.in",
		Owner:       "partner-team@swiggy.com",
		Sensitivity: "internal",
		Metadata: map[string]string{
			"schema_version": "3.0",
			"backup_policy":  "daily",
			"region":         "ap-south-1",
			"data_residency": "India",
		},
		CreatedAt: time.Now().AddDate(0, -12, 0),
		UpdatedAt: time.Now(),
		IsActive:  true,
	}
	
	// Order stream source
	orderStream := &DataSource{
		ID:          "src_order_stream",
		Name:        "Real-time Order Stream",
		Type:        "stream",
		Location:    "kafka://orders.swiggy.in/order-events",
		Owner:       "platform-team@swiggy.com",
		Sensitivity: "confidential",
		Metadata: map[string]string{
			"retention_days": "7",
			"partitions":     "50",
			"replication":    "3",
			"format":         "avro",
		},
		CreatedAt: time.Now().AddDate(0, -2, 0),
		UpdatedAt: time.Now(),
		IsActive:  true,
	}
	
	// Delivery tracking source
	deliverySource := &DataSource{
		ID:          "src_delivery_tracking",
		Name:        "Delivery Tracking API",
		Type:        "api",
		Location:    "https://tracking.swiggy.in/api/v2",
		Owner:       "delivery-team@swiggy.com",
		Sensitivity: "internal",
		Metadata: map[string]string{
			"api_version":    "2.0",
			"rate_limit":     "1000/min",
			"authentication": "oauth2",
			"sla":            "99.9%",
		},
		CreatedAt: time.Now().AddDate(0, -4, 0),
		UpdatedAt: time.Now(),
		IsActive:  true,
	}
	
	// Register sources
	sources := []*DataSource{customerSource, restaurantSource, orderStream, deliverySource}
	for _, source := range sources {
		slt.RegisterDataSource(source)
	}
}

// RegisterDataSource registers a new data source
// नया डेटा स्रोत पंजीकृत करता है
func (slt *SwiggyDataLineageTracker) RegisterDataSource(source *DataSource) {
	slt.dataSources[source.ID] = source
	
	// Create lineage node
	node := &DataLineageNode{
		ID:   source.ID,
		Name: source.Name,
		Type: "source",
		Attributes: map[string]interface{}{
			"data_type":    source.Type,
			"location":     source.Location,
			"owner":        source.Owner,
			"sensitivity":  source.Sensitivity,
			"is_active":    source.IsActive,
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	
	slt.lineageGraph.Nodes[source.ID] = node
	
	// Audit log
	slt.auditLog = append(slt.auditLog, map[string]interface{}{
		"timestamp": time.Now(),
		"action":    "source_registered",
		"source_id": source.ID,
		"source_name": source.Name,
		"metadata":  source.Metadata,
	})
	
	fmt.Printf("📊 Registered data source: %s (%s)\n", source.Name, source.Type)
}

// RegisterTransformation registers a data transformation
// डेटा रूपांतरण पंजीकृत करता है
func (slt *SwiggyDataLineageTracker) RegisterTransformation(transformation *DataTransformation) {
	slt.transformations[transformation.ID] = transformation
	
	// Create lineage node
	node := &DataLineageNode{
		ID:   transformation.ID,
		Name: transformation.Name,
		Type: "transformation",
		Attributes: map[string]interface{}{
			"transform_type":   transformation.Type,
			"description":      transformation.Description,
			"owner":            transformation.Owner,
			"processing_time":  transformation.ProcessingTime.String(),
			"business_logic":   transformation.BusinessLogic,
			"quality_rules":    transformation.QualityRules,
			"compliance_flags": transformation.ComplianceFlags,
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	
	slt.lineageGraph.Nodes[transformation.ID] = node
	
	// Audit log
	slt.auditLog = append(slt.auditLog, map[string]interface{}{
		"timestamp":        time.Now(),
		"action":          "transformation_registered",
		"transformation_id": transformation.ID,
		"name":            transformation.Name,
		"type":            transformation.Type,
	})
	
	fmt.Printf("🔄 Registered transformation: %s (%s)\n", transformation.Name, transformation.Type)
}

// CreateDataFlow creates a data flow between nodes
// नोड्स के बीच डेटा फ्लो बनाता है
func (slt *SwiggyDataLineageTracker) CreateDataFlow(sourceNodeID, destNodeID, relationshipType string, dataVolume int64) string {
	edgeID := fmt.Sprintf("edge_%s_to_%s", sourceNodeID, destNodeID)
	
	edge := &DataLineageEdge{
		ID:                edgeID,
		SourceNodeID:      sourceNodeID,
		DestinationNodeID: destNodeID,
		RelationshipType:  relationshipType,
		DataVolume:        dataVolume,
		LastProcessed:     time.Now(),
		Metadata:          make(map[string]string),
		IsActive:          true,
	}
	
	slt.lineageGraph.Edges[edgeID] = edge
	
	// Update node levels for graph visualization
	slt.updateNodeLevels()
	
	// Audit log
	slt.auditLog = append(slt.auditLog, map[string]interface{}{
		"timestamp":         time.Now(),
		"action":           "data_flow_created",
		"edge_id":          edgeID,
		"source_node":      sourceNodeID,
		"destination_node": destNodeID,
		"relationship":     relationshipType,
		"data_volume":      dataVolume,
	})
	
	fmt.Printf("🔗 Created data flow: %s -> %s (%s)\n", sourceNodeID, destNodeID, relationshipType)
	return edgeID
}

// updateNodeLevels calculates and updates node levels for visualization
// विज़ुअलाइज़ेशन के लिए नोड लेवल की गणना और अपडेट करता है
func (slt *SwiggyDataLineageTracker) updateNodeLevels() {
	// Simple topological sorting to assign levels
	inDegree := make(map[string]int)
	
	// Initialize in-degrees
	for nodeID := range slt.lineageGraph.Nodes {
		inDegree[nodeID] = 0
	}
	
	// Calculate in-degrees
	for _, edge := range slt.lineageGraph.Edges {
		if edge.IsActive {
			inDegree[edge.DestinationNodeID]++
		}
	}
	
	// Assign levels using BFS-like approach
	queue := make([]string, 0)
	level := 0
	
	// Start with nodes having no incoming edges (sources)
	for nodeID, degree := range inDegree {
		if degree == 0 {
			queue = append(queue, nodeID)
			slt.lineageGraph.Nodes[nodeID].Level = level
		}
	}
	
	for len(queue) > 0 {
		levelSize := len(queue)
		level++
		
		for i := 0; i < levelSize; i++ {
			currentNode := queue[0]
			queue = queue[1:]
			
			// Process outgoing edges
			for _, edge := range slt.lineageGraph.Edges {
				if edge.SourceNodeID == currentNode && edge.IsActive {
					inDegree[edge.DestinationNodeID]--
					if inDegree[edge.DestinationNodeID] == 0 {
						queue = append(queue, edge.DestinationNodeID)
						slt.lineageGraph.Nodes[edge.DestinationNodeID].Level = level
					}
				}
			}
		}
	}
}

// TraceDataLineage traces lineage for a specific data element
// विशिष्ट डेटा तत्व के लिए वंशावली का पता लगाता है
func (slt *SwiggyDataLineageTracker) TraceDataLineage(nodeID string, direction string) []string {
	visited := make(map[string]bool)
	lineage := make([]string, 0)
	
	slt.traceRecursive(nodeID, direction, visited, &lineage)
	
	return lineage
}

// traceRecursive performs recursive lineage tracing
// रिकर्सिव लाइनेज ट्रेसिंग करता है
func (slt *SwiggyDataLineageTracker) traceRecursive(nodeID string, direction string, visited map[string]bool, lineage *[]string) {
	if visited[nodeID] {
		return
	}
	
	visited[nodeID] = true
	*lineage = append(*lineage, nodeID)
	
	// Trace based on direction
	for _, edge := range slt.lineageGraph.Edges {
		if !edge.IsActive {
			continue
		}
		
		if direction == "upstream" && edge.DestinationNodeID == nodeID {
			slt.traceRecursive(edge.SourceNodeID, direction, visited, lineage)
		} else if direction == "downstream" && edge.SourceNodeID == nodeID {
			slt.traceRecursive(edge.DestinationNodeID, direction, visited, lineage)
		}
	}
}

// PerformImpactAnalysis performs impact analysis for changes
// परिवर्तनों के लिए प्रभाव विश्लेषण करता है
func (slt *SwiggyDataLineageTracker) PerformImpactAnalysis(nodeID string) *ImpactAnalysisResult {
	fmt.Printf("🔍 Performing impact analysis for: %s\n", nodeID)
	
	node := slt.lineageGraph.Nodes[nodeID]
	if node == nil {
		return nil
	}
	
	// Find all downstream nodes
	downstreamNodes := slt.TraceDataLineage(nodeID, "downstream")
	
	// Analyze impact level
	impactLevel := "low"
	affectedSystems := make([]string, 0)
	recommendedActions := make([]string, 0)
	
	// Count critical downstream nodes
	criticalCount := 0
	for _, downstreamID := range downstreamNodes {
		downstreamNode := slt.lineageGraph.Nodes[downstreamID]
		if downstreamNode != nil {
			// Check if it's a critical system
			if sensitivity, ok := downstreamNode.Attributes["sensitivity"].(string); ok {
				if sensitivity == "critical" || sensitivity == "confidential" {
					criticalCount++
				}
			}
			
			// Collect affected systems
			if owner, ok := downstreamNode.Attributes["owner"].(string); ok {
				affectedSystems = append(affectedSystems, owner)
			}
		}
	}
	
	// Determine impact level
	if len(downstreamNodes) > 10 || criticalCount > 3 {
		impactLevel = "critical"
		recommendedActions = append(recommendedActions, 
			"Schedule maintenance window",
			"Notify all downstream teams 48 hours in advance",
			"Prepare rollback plan",
			"Set up monitoring for affected systems")
	} else if len(downstreamNodes) > 5 || criticalCount > 1 {
		impactLevel = "high"
		recommendedActions = append(recommendedActions,
			"Notify downstream teams 24 hours in advance",
			"Test changes in staging environment",
			"Monitor key metrics during deployment")
	} else if len(downstreamNodes) > 2 {
		impactLevel = "medium"
		recommendedActions = append(recommendedActions,
			"Inform relevant teams",
			"Validate data quality post-change")
	} else {
		recommendedActions = append(recommendedActions,
			"Standard change process applicable")
	}
	
	// Business impact assessment
	businessImpact := "Low business impact expected"
	if impactLevel == "critical" {
		businessImpact = "Critical business systems may be affected. Revenue impact possible."
	} else if impactLevel == "high" {
		businessImpact = "Important business processes may be disrupted temporarily."
	} else if impactLevel == "medium" {
		businessImpact = "Some business workflows may experience minor delays."
	}
	
	result := &ImpactAnalysisResult{
		SourceNode:         nodeID,
		ImpactedNodes:      downstreamNodes,
		ImpactLevel:        impactLevel,
		AffectedSystems:    removeDuplicates(affectedSystems),
		BusinessImpact:     businessImpact,
		RecommendedActions: recommendedActions,
	}
	
	// Log the analysis
	slt.auditLog = append(slt.auditLog, map[string]interface{}{
		"timestamp":      time.Now(),
		"action":        "impact_analysis",
		"source_node":   nodeID,
		"impact_level":  impactLevel,
		"affected_count": len(downstreamNodes),
	})
	
	return result
}

// GenerateLineageReport generates comprehensive lineage report
// व्यापक वंशावली रिपोर्ट जेनरेट करता है
func (slt *SwiggyDataLineageTracker) GenerateLineageReport() map[string]interface{} {
	report := make(map[string]interface{})
	
	// Summary statistics
	summary := map[string]interface{}{
		"total_nodes":         len(slt.lineageGraph.Nodes),
		"total_edges":         len(slt.lineageGraph.Edges),
		"data_sources":        len(slt.dataSources),
		"transformations":     len(slt.transformations),
		"active_flows":        slt.countActiveFlows(),
		"report_generated_at": time.Now(),
	}
	report["summary"] = summary
	
	// Node analysis by type
	nodesByType := make(map[string]int)
	nodesBySensitivity := make(map[string]int)
	
	for _, node := range slt.lineageGraph.Nodes {
		nodesByType[node.Type]++
		
		if sensitivity, ok := node.Attributes["sensitivity"].(string); ok {
			nodesBySensitivity[sensitivity]++
		}
	}
	
	report["nodes_by_type"] = nodesByType
	report["nodes_by_sensitivity"] = nodesBySensitivity
	
	// Most connected nodes (hubs)
	connectionCounts := make(map[string]int)
	for _, edge := range slt.lineageGraph.Edges {
		if edge.IsActive {
			connectionCounts[edge.SourceNodeID]++
			connectionCounts[edge.DestinationNodeID]++
		}
	}
	
	// Sort by connection count
	type nodeConnection struct {
		NodeID string
		Count  int
	}
	
	connections := make([]nodeConnection, 0)
	for nodeID, count := range connectionCounts {
		connections = append(connections, nodeConnection{NodeID: nodeID, Count: count})
	}
	
	sort.Slice(connections, func(i, j int) bool {
		return connections[i].Count > connections[j].Count
	})
	
	topHubs := make([]map[string]interface{}, 0)
	for i, conn := range connections {
		if i >= 5 { // Top 5 hubs
			break
		}
		
		node := slt.lineageGraph.Nodes[conn.NodeID]
		topHubs = append(topHubs, map[string]interface{}{
			"node_id":     conn.NodeID,
			"node_name":   node.Name,
			"connections": conn.Count,
			"node_type":   node.Type,
		})
	}
	report["top_connected_nodes"] = topHubs
	
	// Data flow analysis
	totalDataVolume := int64(0)
	for _, edge := range slt.lineageGraph.Edges {
		if edge.IsActive {
			totalDataVolume += edge.DataVolume
		}
	}
	report["total_data_volume"] = totalDataVolume
	
	// Compliance analysis
	complianceFlags := make(map[string]int)
	for _, transformation := range slt.transformations {
		for _, flag := range transformation.ComplianceFlags {
			complianceFlags[flag]++
		}
	}
	report["compliance_flags"] = complianceFlags
	
	return report
}

// Helper functions
func (slt *SwiggyDataLineageTracker) countActiveFlows() int {
	count := 0
	for _, edge := range slt.lineageGraph.Edges {
		if edge.IsActive {
			count++
		}
	}
	return count
}

func removeDuplicates(slice []string) []string {
	keys := make(map[string]bool)
	result := make([]string, 0)
	
	for _, item := range slice {
		if !keys[item] {
			keys[item] = true
			result = append(result, item)
		}
	}
	
	return result
}

// Main demonstration function
func main() {
	fmt.Println("🍜 Swiggy Data Lineage Tracker Demo")
	fmt.Println("===================================")
	
	tracker := NewSwiggyDataLineageTracker()
	
	// Register transformations
	fmt.Println("\n🔄 Registering data transformations...")
	
	// Customer analytics transformation
	customerAnalytics := &DataTransformation{
		ID:          "transform_customer_analytics",
		Name:        "Customer Behavior Analytics",
		Type:        "etl",
		Description: "Aggregate customer order patterns for analytics",
		TransformSQL: `
			SELECT customer_id, 
			       COUNT(*) as order_count,
			       AVG(order_value) as avg_order_value,
			       DATE_TRUNC('month', order_date) as month
			FROM orders o 
			JOIN customers c ON o.customer_id = c.id
			GROUP BY customer_id, month
		`,
		BusinessLogic:   "Calculate monthly customer metrics for business intelligence",
		Owner:           "analytics-team@swiggy.com",
		ProcessingTime:  time.Minute * 15,
		QualityRules:    []string{"non_null_customer_id", "positive_order_count", "valid_date_range"},
		ComplianceFlags: []string{"DPDP_Act", "customer_consent_required"},
		CreatedAt:       time.Now(),
		IsActive:        true,
	}
	tracker.RegisterTransformation(customerAnalytics)
	
	// Real-time order processing
	orderProcessing := &DataTransformation{
		ID:          "transform_order_processing",
		Name:        "Real-time Order Processing",
		Type:        "stream_processing",
		Description: "Process incoming orders from stream and update restaurant data",
		TransformCode: `
			orders.filter(order -> order.status == "confirmed")
			     .map(order -> enrichWithRestaurantInfo(order))
			     .to("processed-orders-topic")
		`,
		BusinessLogic:   "Enrich orders with restaurant information and route to processing",
		Owner:           "platform-team@swiggy.com",
		ProcessingTime:  time.Second * 5,
		QualityRules:    []string{"valid_order_status", "restaurant_exists", "order_completeness"},
		ComplianceFlags: []string{"real_time_processing", "order_privacy"},
		CreatedAt:       time.Now(),
		IsActive:        true,
	}
	tracker.RegisterTransformation(orderProcessing)
	
	// Delivery optimization
	deliveryOptimization := &DataTransformation{
		ID:          "transform_delivery_optimization",
		Name:        "Delivery Route Optimization",
		Type:        "aggregation",
		Description: "Optimize delivery routes based on real-time tracking data",
		BusinessLogic:   "Calculate optimal delivery routes to minimize delivery time",
		Owner:           "delivery-team@swiggy.com",
		ProcessingTime:  time.Minute * 2,
		QualityRules:    []string{"valid_coordinates", "realistic_distance", "driver_availability"},
		ComplianceFlags: []string{"location_privacy", "driver_consent"},
		CreatedAt:       time.Now(),
		IsActive:        true,
	}
	tracker.RegisterTransformation(deliveryOptimization)
	
	// Create data flows
	fmt.Println("\n🔗 Creating data flows...")
	
	// Customer data to analytics
	tracker.CreateDataFlow("src_customers", "transform_customer_analytics", "reads_from", 1000000)
	
	// Order stream to processing
	tracker.CreateDataFlow("src_order_stream", "transform_order_processing", "reads_from", 5000000)
	
	// Restaurant data to order processing
	tracker.CreateDataFlow("src_restaurants", "transform_order_processing", "reads_from", 500000)
	
	// Delivery tracking to optimization
	tracker.CreateDataFlow("src_delivery_tracking", "transform_delivery_optimization", "reads_from", 2000000)
	
	// Processing to optimization (processed orders feed into delivery)
	tracker.CreateDataFlow("transform_order_processing", "transform_delivery_optimization", "writes_to", 1500000)
	
	// Trace lineage
	fmt.Println("\n🔍 Tracing data lineage...")
	
	// Upstream lineage for delivery optimization
	upstreamLineage := tracker.TraceDataLineage("transform_delivery_optimization", "upstream")
	fmt.Printf("Upstream lineage for delivery optimization: %v\n", upstreamLineage)
	
	// Downstream lineage from customer source
	downstreamLineage := tracker.TraceDataLineage("src_customers", "downstream")
	fmt.Printf("Downstream lineage from customer source: %v\n", downstreamLineage)
	
	// Impact analysis
	fmt.Println("\n⚠️  Impact Analysis:")
	
	// Analyze impact of changing customer database
	impact := tracker.PerformImpactAnalysis("src_customers")
	if impact != nil {
		impactJSON, _ := json.MarshalIndent(impact, "", "  ")
		fmt.Printf("Impact analysis for customer database changes:\n%s\n", impactJSON)
	}
	
	// Analyze impact of changing order stream
	streamImpact := tracker.PerformImpactAnalysis("src_order_stream")
	if streamImpact != nil {
		fmt.Printf("\nImpact Level for Order Stream: %s\n", streamImpact.ImpactLevel)
		fmt.Printf("Business Impact: %s\n", streamImpact.BusinessImpact)
		fmt.Printf("Recommended Actions:\n")
		for i, action := range streamImpact.RecommendedActions {
			fmt.Printf("  %d. %s\n", i+1, action)
		}
	}
	
	// Generate comprehensive report
	fmt.Println("\n📊 Lineage Report:")
	report := tracker.GenerateLineageReport()
	reportJSON, _ := json.MarshalIndent(report, "", "  ")
	fmt.Println(reportJSON)
}
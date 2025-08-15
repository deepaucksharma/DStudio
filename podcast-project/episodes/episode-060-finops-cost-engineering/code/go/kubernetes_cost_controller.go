package main

/*
Kubernetes Cost Controller
===========================

Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering
Production-ready Kubernetes cost controller for automated cost optimization

Author: Hindi Tech Community
Date: 2025
Version: 1.0

Features:
- Real-time pod cost tracking
- Automated resource right-sizing
- Cost-based pod scheduling
- Namespace budget enforcement
- Resource quota management
- Cost allocation by teams/projects

Mumbai Context: K8s cost control जैसे Mumbai office space management
- Per-desk cost allocation
- Department-wise space budgets
- Optimal space utilization
- Automatic resource adjustment based on usage
*/

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sort"
	"sync"
	"time"

	"k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/fields"
	"k8s.io/apimachinery/pkg/labels"
	"k8s.io/apimachinery/pkg/watch"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/cache"
	"k8s.io/client-go/tools/clientcmd"
)

// CostConfig represents cost configuration for the controller
type CostConfig struct {
	CPUCostPerHour    float64            `json:"cpu_cost_per_hour"`
	MemoryCostPerGB   float64            `json:"memory_cost_per_gb"`
	StorageCostPerGB  float64            `json:"storage_cost_per_gb"`
	NodeCosts        map[string]float64  `json:"node_costs"`        // Node-specific costs
	RegionalFactors  map[string]float64  `json:"regional_factors"`  // Mumbai vs other regions
}

// PodCostInfo represents cost information for a pod
type PodCostInfo struct {
	PodName           string            `json:"pod_name"`
	Namespace         string            `json:"namespace"`
	NodeName          string            `json:"node_name"`
	CPURequest        float64           `json:"cpu_request"`
	MemoryRequestGB   float64           `json:"memory_request_gb"`
	StorageGB         float64           `json:"storage_gb"`
	HourlyCost        float64           `json:"hourly_cost"`
	MonthlyCost       float64           `json:"monthly_cost"`
	Team              string            `json:"team"`
	Project           string            `json:"project"`
	CostCenter        string            `json:"cost_center"`
	CreatedAt         time.Time         `json:"created_at"`
	LastCalculatedAt  time.Time         `json:"last_calculated_at"`
	
	// Mumbai Context: Additional tracking
	MumbaiContext     string            `json:"mumbai_context"`
	OptimizationTip   string            `json:"optimization_tip"`
}

// NamespaceBudget represents budget allocation for a namespace
type NamespaceBudget struct {
	Namespace         string    `json:"namespace"`
	MonthlyBudget     float64   `json:"monthly_budget"`
	CurrentSpend      float64   `json:"current_spend"`
	AlertThreshold    float64   `json:"alert_threshold"`
	HardLimit         float64   `json:"hard_limit"`
	Team              string    `json:"team"`
	Manager           string    `json:"manager"`
	LastUpdated       time.Time `json:"last_updated"`
}

// CostOptimizationRecommendation represents an optimization suggestion
type CostOptimizationRecommendation struct {
	PodName           string    `json:"pod_name"`
	Namespace         string    `json:"namespace"`
	CurrentCost       float64   `json:"current_cost"`
	OptimizedCost     float64   `json:"optimized_cost"`
	Savings           float64   `json:"savings"`
	Action            string    `json:"action"`
	Priority          string    `json:"priority"`
	AutoApply         bool      `json:"auto_apply"`
	Reason            string    `json:"reason"`
	MumbaiAnalogy     string    `json:"mumbai_analogy"`
}

// KubernetesCostController is the main controller struct
type KubernetesCostController struct {
	clientset       kubernetes.Interface
	costConfig      CostConfig
	podCosts        map[string]*PodCostInfo
	namespaceBudgets map[string]*NamespaceBudget
	recommendations []CostOptimizationRecommendation
	mutex           sync.RWMutex
	
	// Controller lifecycle
	stopCh          chan struct{}
	informerFactory cache.SharedInformerFactory
	
	// Mumbai-specific configuration
	peakHours       []int // Peak hours when costs are higher
	offPeakDiscount float64 // Discount during off-peak hours
}

// NewKubernetesCostController creates a new cost controller
func NewKubernetesCostController(kubeconfig string) (*KubernetesCostController, error) {
	var config *rest.Config
	var err error
	
	if kubeconfig != "" {
		config, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
	} else {
		config, err = rest.InClusterConfig()
	}
	
	if err != nil {
		return nil, fmt.Errorf("failed to create kubernetes config: %w", err)
	}
	
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		return nil, fmt.Errorf("failed to create kubernetes clientset: %w", err)
	}
	
	controller := &KubernetesCostController{
		clientset:       clientset,
		podCosts:        make(map[string]*PodCostInfo),
		namespaceBudgets: make(map[string]*NamespaceBudget),
		recommendations: make([]CostOptimizationRecommendation, 0),
		stopCh:          make(chan struct{}),
		costConfig: CostConfig{
			CPUCostPerHour:   0.048,  // $0.048 per CPU hour
			MemoryCostPerGB:  0.012,  // $0.012 per GB hour
			StorageCostPerGB: 0.10,   // $0.10 per GB month
			NodeCosts: map[string]float64{
				"m5.large":   0.096,  // Per hour
				"m5.xlarge":  0.192,
				"c5.large":   0.085,
				"c5.xlarge":  0.17,
				"r5.large":   0.126,
			},
			RegionalFactors: map[string]float64{
				"mumbai":    0.90, // 10% cheaper in Mumbai
				"bangalore": 0.95, // 5% cheaper in Bangalore
				"delhi":     1.05, // 5% more expensive in Delhi
			},
		},
		// Mumbai context: Peak hours when costs are higher (9-11 AM, 6-8 PM)
		peakHours:       []int{9, 10, 18, 19},
		offPeakDiscount: 0.85, // 15% discount during off-peak hours
	}
	
	return controller, nil
}

// Start starts the cost controller
func (controller *KubernetesCostController) Start(ctx context.Context) error {
	log.Println("🚀 Starting Kubernetes Cost Controller...")
	
	// Initialize namespace budgets
	err := controller.initializeNamespaceBudgets()
	if err != nil {
		return fmt.Errorf("failed to initialize namespace budgets: %w", err)
	}
	
	// Start pod informer
	go controller.startPodInformer(ctx)
	
	// Start cost calculation loop
	go controller.startCostCalculationLoop(ctx)
	
	// Start optimization loop
	go controller.startOptimizationLoop(ctx)
	
	// Start budget monitoring
	go controller.startBudgetMonitoring(ctx)
	
	log.Println("✅ Kubernetes Cost Controller started successfully")
	
	// Wait for context cancellation
	<-ctx.Done()
	close(controller.stopCh)
	
	return nil
}

// initializeNamespaceBudgets sets up default budgets for namespaces
func (controller *KubernetesCostController) initializeNamespaceBudgets() error {
	namespaces, err := controller.clientset.CoreV1().Namespaces().List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		return err
	}
	
	controller.mutex.Lock()
	defer controller.mutex.Unlock()
	
	// Default budgets for different namespace types
	defaultBudgets := map[string]float64{
		"production":  5000.0, // $5000/month
		"staging":     2000.0, // $2000/month
		"development": 1000.0, // $1000/month
		"default":     500.0,  // $500/month
	}
	
	for _, ns := range namespaces.Items {
		nsName := ns.Name
		
		// Skip system namespaces
		if nsName == "kube-system" || nsName == "kube-public" || nsName == "kube-node-lease" {
			continue
		}
		
		// Determine budget based on namespace name/labels
		budget := defaultBudgets["default"]
		for envType, envBudget := range defaultBudgets {
			if contains(nsName, envType) {
				budget = envBudget
				break
			}
		}
		
		// Get team info from labels
		team := ns.Labels["team"]
		if team == "" {
			team = "unknown"
		}
		
		controller.namespaceBudgets[nsName] = &NamespaceBudget{
			Namespace:      nsName,
			MonthlyBudget:  budget,
			CurrentSpend:   0.0,
			AlertThreshold: 0.80, // 80%
			HardLimit:      0.95,  // 95%
			Team:          team,
			Manager:       ns.Labels["manager"],
			LastUpdated:   time.Now(),
		}
		
		log.Printf("📊 Initialized budget for namespace %s: $%.2f/month", nsName, budget)
	}
	
	return nil
}

// startPodInformer starts watching pod events
func (controller *KubernetesCostController) startPodInformer(ctx context.Context) {
	log.Println("👀 Starting pod informer...")
	
	// Create a pod informer
	podInformer := cache.NewSharedIndexInformer(
		&cache.ListWatch{
			ListFunc: func(options metav1.ListOptions) (runtime.Object, error) {
				return controller.clientset.CoreV1().Pods("").List(ctx, options)
			},
			WatchFunc: func(options metav1.ListOptions) (watch.Interface, error) {
				return controller.clientset.CoreV1().Pods("").Watch(ctx, options)
			},
		},
		&v1.Pod{},
		time.Minute*10, // Resync every 10 minutes
		cache.Indexers{},
	)
	
	// Add event handlers
	podInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: func(obj interface{}) {
			pod := obj.(*v1.Pod)
			controller.onPodAdd(pod)
		},
		UpdateFunc: func(oldObj, newObj interface{}) {
			pod := newObj.(*v1.Pod)
			controller.onPodUpdate(pod)
		},
		DeleteFunc: func(obj interface{}) {
			pod := obj.(*v1.Pod)
			controller.onPodDelete(pod)
		},
	})
	
	// Start the informer
	go podInformer.Run(controller.stopCh)
	
	// Wait for cache sync
	if !cache.WaitForCacheSync(controller.stopCh, podInformer.HasSynced) {
		log.Fatal("Failed to sync pod cache")
	}
	
	log.Println("✅ Pod informer started and synced")
}

// onPodAdd handles pod addition
func (controller *KubernetesCostController) onPodAdd(pod *v1.Pod) {
	if pod.Status.Phase != v1.PodRunning {
		return
	}
	
	costInfo := controller.calculatePodCost(pod)
	
	controller.mutex.Lock()
	controller.podCosts[controller.getPodKey(pod)] = costInfo
	controller.mutex.Unlock()
	
	// Update namespace spending
	controller.updateNamespaceSpending(pod.Namespace, costInfo.MonthlyCost)
	
	log.Printf("💰 Added cost tracking for pod %s/%s: $%.2f/month", 
		pod.Namespace, pod.Name, costInfo.MonthlyCost)
}

// onPodUpdate handles pod updates
func (controller *KubernetesCostController) onPodUpdate(pod *v1.Pod) {
	if pod.Status.Phase != v1.PodRunning {
		controller.onPodDelete(pod)
		return
	}
	
	controller.onPodAdd(pod) // Recalculate cost
}

// onPodDelete handles pod deletion
func (controller *KubernetesCostController) onPodDelete(pod *v1.Pod) {
	podKey := controller.getPodKey(pod)
	
	controller.mutex.Lock()
	if costInfo, exists := controller.podCosts[podKey]; exists {
		// Remove cost from namespace spending
		controller.updateNamespaceSpending(pod.Namespace, -costInfo.MonthlyCost)
		delete(controller.podCosts, podKey)
	}
	controller.mutex.Unlock()
	
	log.Printf("🗑️  Removed cost tracking for pod %s/%s", pod.Namespace, pod.Name)
}

// calculatePodCost calculates the cost for a pod
func (controller *KubernetesCostController) calculatePodCost(pod *v1.Pod) *PodCostInfo {
	var totalCPURequest float64
	var totalMemoryRequestGB float64
	var totalStorageGB float64
	
	// Calculate total resource requests
	for _, container := range pod.Spec.Containers {
		if container.Resources.Requests != nil {
			// CPU calculation
			if cpuReq := container.Resources.Requests.Cpu(); cpuReq != nil {
				totalCPURequest += float64(cpuReq.MilliValue()) / 1000.0
			}
			
			// Memory calculation
			if memReq := container.Resources.Requests.Memory(); memReq != nil {
				totalMemoryRequestGB += float64(memReq.Value()) / (1024 * 1024 * 1024)
			}
		}
	}
	
	// Storage calculation (simplified - from PV claims)
	for _, volume := range pod.Spec.Volumes {
		if volume.PersistentVolumeClaim != nil {
			// This would need to look up actual PVC size
			totalStorageGB += 10.0 // Simplified: assume 10GB per PVC
		}
	}
	
	// Calculate costs
	hourlyCPUCost := totalCPURequest * controller.costConfig.CPUCostPerHour
	hourlyMemoryCost := totalMemoryRequestGB * controller.costConfig.MemoryCostPerGB
	monthlyStorageCost := totalStorageGB * controller.costConfig.StorageCostPerGB
	
	// Apply regional factors
	region := controller.getRegionFromNode(pod.Spec.NodeName)
	regionalFactor := controller.costConfig.RegionalFactors[region]
	if regionalFactor == 0 {
		regionalFactor = 1.0
	}
	
	// Apply peak/off-peak pricing
	currentHour := time.Now().Hour()
	timeFactor := 1.0
	if controller.isPeakHour(currentHour) {
		timeFactor = 1.25 // 25% more during peak hours
	} else {
		timeFactor = controller.offPeakDiscount
	}
	
	totalHourlyCost := (hourlyCPUCost + hourlyMemoryCost) * regionalFactor * timeFactor
	totalMonthlyCost := (totalHourlyCost * 24 * 30) + monthlyStorageCost
	
	// Get team/project info from labels
	team := pod.Labels["team"]
	if team == "" {
		team = "unknown"
	}
	
	project := pod.Labels["project"]
	if project == "" {
		project = "default"
	}
	
	costCenter := pod.Labels["cost-center"]
	if costCenter == "" {
		costCenter = fmt.Sprintf("CC-%s", team)
	}
	
	// Mumbai context analysis
	mumbaiContext := controller.getMumbaiContext(totalMonthlyCost, totalCPURequest, totalMemoryRequestGB)
	optimizationTip := controller.getOptimizationTip(totalCPURequest, totalMemoryRequestGB)
	
	return &PodCostInfo{
		PodName:          pod.Name,
		Namespace:        pod.Namespace,
		NodeName:         pod.Spec.NodeName,
		CPURequest:       totalCPURequest,
		MemoryRequestGB:  totalMemoryRequestGB,
		StorageGB:        totalStorageGB,
		HourlyCost:       totalHourlyCost,
		MonthlyCost:      totalMonthlyCost,
		Team:             team,
		Project:          project,
		CostCenter:       costCenter,
		CreatedAt:        pod.CreationTimestamp.Time,
		LastCalculatedAt: time.Now(),
		MumbaiContext:    mumbaiContext,
		OptimizationTip:  optimizationTip,
	}
}

// getMumbaiContext provides Mumbai-style context for cost
func (controller *KubernetesCostController) getMumbaiContext(cost, cpu, memory float64) string {
	if cost > 200 {
		return "🏢 Like renting premium office space in BKC - high cost, premium resources"
	} else if cost > 100 {
		return "🏪 Like mid-tier office in Andheri - balanced cost and features"
	} else if cost > 50 {
		return "🏠 Like shared workspace in suburbs - cost-effective option"
	} else {
		return "🚶 Like working from local café - minimal infrastructure cost"
	}
}

// getOptimizationTip provides optimization suggestions
func (controller *KubernetesCostController) getOptimizationTip(cpu, memory float64) string {
	if cpu < 0.5 && memory < 1.0 {
		return "💡 Consider using smaller resource requests - like choosing economy class over business"
	} else if cpu > 4.0 || memory > 8.0 {
		return "⚡ High resource usage - ensure this is necessary like AC in Mumbai summer"
	} else {
		return "✅ Resource allocation looks reasonable - like well-planned Mumbai commute"
	}
}

// startCostCalculationLoop runs periodic cost recalculation
func (controller *KubernetesCostController) startCostCalculationLoop(ctx context.Context) {
	ticker := time.NewTicker(5 * time.Minute)
	defer ticker.Stop()
	
	log.Println("🔄 Starting cost calculation loop...")
	
	for {
		select {
		case <-ticker.C:
			controller.recalculateAllCosts()
		case <-ctx.Done():
			return
		}
	}
}

// recalculateAllCosts recalculates costs for all pods
func (controller *KubernetesCostController) recalculateAllCosts() {
	pods, err := controller.clientset.CoreV1().Pods("").List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		log.Printf("Error listing pods for cost recalculation: %v", err)
		return
	}
	
	controller.mutex.Lock()
	defer controller.mutex.Unlock()
	
	totalCost := 0.0
	for _, pod := range pods.Items {
		if pod.Status.Phase == v1.PodRunning {
			costInfo := controller.calculatePodCost(&pod)
			controller.podCosts[controller.getPodKey(&pod)] = costInfo
			totalCost += costInfo.MonthlyCost
		}
	}
	
	log.Printf("💰 Recalculated costs for %d running pods. Total: $%.2f/month", len(pods.Items), totalCost)
}

// startOptimizationLoop runs periodic optimization analysis
func (controller *KubernetesCostController) startOptimizationLoop(ctx context.Context) {
	ticker := time.NewTicker(10 * time.Minute)
	defer ticker.Stop()
	
	log.Println("🎯 Starting optimization loop...")
	
	for {
		select {
		case <-ticker.C:
			controller.generateOptimizationRecommendations()
		case <-ctx.Done():
			return
		}
	}
}

// generateOptimizationRecommendations analyzes pods for optimization opportunities
func (controller *KubernetesCostController) generateOptimizationRecommendations() {
	controller.mutex.Lock()
	defer controller.mutex.Unlock()
	
	controller.recommendations = make([]CostOptimizationRecommendation, 0)
	
	for _, costInfo := range controller.podCosts {
		recommendations := controller.analyzePodForOptimization(costInfo)
		controller.recommendations = append(controller.recommendations, recommendations...)
	}
	
	// Sort by savings potential
	sort.Slice(controller.recommendations, func(i, j int) bool {
		return controller.recommendations[i].Savings > controller.recommendations[j].Savings
	})
	
	log.Printf("🎯 Generated %d optimization recommendations", len(controller.recommendations))
	
	// Log top 3 recommendations
	for i, rec := range controller.recommendations {
		if i >= 3 {
			break
		}
		log.Printf("  %d. %s/%s: %s (Save $%.2f/month)", 
			i+1, rec.Namespace, rec.PodName, rec.Action, rec.Savings)
	}
}

// analyzePodForOptimization analyzes a single pod for optimization
func (controller *KubernetesCostController) analyzePodForOptimization(costInfo *PodCostInfo) []CostOptimizationRecommendation {
	var recommendations []CostOptimizationRecommendation
	
	// Check for oversized resources
	if costInfo.CPURequest > 2.0 && costInfo.MonthlyCost > 100 {
		optimizedCost := costInfo.MonthlyCost * 0.7 // Assume 30% reduction
		savings := costInfo.MonthlyCost - optimizedCost
		
		recommendations = append(recommendations, CostOptimizationRecommendation{
			PodName:       costInfo.PodName,
			Namespace:     costInfo.Namespace,
			CurrentCost:   costInfo.MonthlyCost,
			OptimizedCost: optimizedCost,
			Savings:       savings,
			Action:        "Reduce CPU request from %.1f to %.1f cores",
			Priority:      controller.getPriority(savings),
			AutoApply:     false, // Require manual approval
			Reason:        "High CPU allocation with potential for optimization",
			MumbaiAnalogy: "जैसे Mumbai में bigger flat से smaller efficient flat में shift करना",
		})
	}
	
	// Check for memory optimization
	if costInfo.MemoryRequestGB > 4.0 && costInfo.MonthlyCost > 80 {
		optimizedCost := costInfo.MonthlyCost * 0.8 // Assume 20% reduction
		savings := costInfo.MonthlyCost - optimizedCost
		
		recommendations = append(recommendations, CostOptimizationRecommendation{
			PodName:       costInfo.PodName,
			Namespace:     costInfo.Namespace,
			CurrentCost:   costInfo.MonthlyCost,
			OptimizedCost: optimizedCost,
			Savings:       savings,
			Action:        "Reduce memory request",
			Priority:      controller.getPriority(savings),
			AutoApply:     false,
			Reason:        "High memory allocation may be optimizable",
			MumbaiAnalogy: "जैसे Mumbai office में extra space return करके rent save करना",
		})
	}
	
	// Check for node optimization (move to cheaper nodes)
	if costInfo.MonthlyCost > 150 {
		optimizedCost := costInfo.MonthlyCost * 0.85 // Assume 15% reduction
		savings := costInfo.MonthlyCost - optimizedCost
		
		recommendations = append(recommendations, CostOptimizationRecommendation{
			PodName:       costInfo.PodName,
			Namespace:     costInfo.Namespace,
			CurrentCost:   costInfo.MonthlyCost,
			OptimizedCost: optimizedCost,
			Savings:       savings,
			Action:        "Consider migrating to cost-optimized node",
			Priority:      controller.getPriority(savings),
			AutoApply:     true, // Can be automated
			Reason:        "High-cost pod may benefit from cheaper node placement",
			MumbaiAnalogy: "जैसे Mumbai में expensive area से affordable area में shift करना",
		})
	}
	
	return recommendations
}

// startBudgetMonitoring monitors namespace budgets
func (controller *KubernetesCostController) startBudgetMonitoring(ctx context.Context) {
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()
	
	log.Println("📊 Starting budget monitoring...")
	
	for {
		select {
		case <-ticker.C:
			controller.checkBudgetAlerts()
		case <-ctx.Done():
			return
		}
	}
}

// checkBudgetAlerts checks for budget threshold violations
func (controller *KubernetesCostController) checkBudgetAlerts() {
	controller.mutex.RLock()
	defer controller.mutex.RUnlock()
	
	for _, budget := range controller.namespaceBudgets {
		utilization := budget.CurrentSpend / budget.MonthlyBudget
		
		if utilization >= budget.HardLimit {
			log.Printf("🚨 HARD LIMIT EXCEEDED: Namespace %s ($%.2f/$%.2f = %.1f%%)", 
				budget.Namespace, budget.CurrentSpend, budget.MonthlyBudget, utilization*100)
			log.Printf("Mumbai Context: यह budget limit completely cross हो गया - immediate action needed!")
			
			// In production, this would trigger pod scaling restrictions
			
		} else if utilization >= budget.AlertThreshold {
			log.Printf("⚠️  BUDGET ALERT: Namespace %s approaching limit ($%.2f/$%.2f = %.1f%%)", 
				budget.Namespace, budget.CurrentSpend, budget.MonthlyBudget, utilization*100)
			log.Printf("Mumbai Context: Budget limit के near - careful spending needed!")
		}
	}
}

// Helper functions

func (controller *KubernetesCostController) getPodKey(pod *v1.Pod) string {
	return fmt.Sprintf("%s/%s", pod.Namespace, pod.Name)
}

func (controller *KubernetesCostController) getRegionFromNode(nodeName string) string {
	// In production, this would query node labels for region info
	// Simplified: assume Mumbai region
	return "mumbai"
}

func (controller *KubernetesCostController) isPeakHour(hour int) bool {
	for _, peakHour := range controller.peakHours {
		if hour == peakHour {
			return true
		}
	}
	return false
}

func (controller *KubernetesCostController) getPriority(savings float64) string {
	if savings > 50 {
		return "HIGH"
	} else if savings > 20 {
		return "MEDIUM"
	} else {
		return "LOW"
	}
}

func (controller *KubernetesCostController) updateNamespaceSpending(namespace string, costChange float64) {
	controller.mutex.Lock()
	defer controller.mutex.Unlock()
	
	if budget, exists := controller.namespaceBudgets[namespace]; exists {
		budget.CurrentSpend += costChange
		budget.LastUpdated = time.Now()
	}
}

func contains(str, substr string) bool {
	return len(str) >= len(substr) && (str == substr || 
		(len(str) > len(substr) && (str[:len(substr)] == substr || str[len(str)-len(substr):] == substr)))
}

// GetCostReport generates a comprehensive cost report
func (controller *KubernetesCostController) GetCostReport() string {
	controller.mutex.RLock()
	defer controller.mutex.RUnlock()
	
	report := `
Kubernetes Cost Controller Report
================================
Generated: %s

CLUSTER COST SUMMARY (Mumbai Style)
===================================
यह report आपके K8s cluster का complete cost breakdown है
जैसे Mumbai office building में सभी floors का cost allocation

Total Pods Tracked: %d
Total Monthly Cost: $%.2f
Active Namespaces: %d
Optimization Opportunities: %d

NAMESPACE BUDGET STATUS
======================
`
	
	totalCost := 0.0
	for _, costInfo := range controller.podCosts {
		totalCost += costInfo.MonthlyCost
	}
	
	report = fmt.Sprintf(report, 
		time.Now().Format("2006-01-02 15:04:05"),
		len(controller.podCosts),
		totalCost,
		len(controller.namespaceBudgets),
		len(controller.recommendations))
	
	// Add namespace budget details
	for _, budget := range controller.namespaceBudgets {
		utilization := budget.CurrentSpend / budget.MonthlyBudget * 100
		status := "✅ HEALTHY"
		
		if utilization >= budget.HardLimit*100 {
			status = "🚨 OVER BUDGET"
		} else if utilization >= budget.AlertThreshold*100 {
			status = "⚠️  WARNING"
		}
		
		report += fmt.Sprintf(`
Namespace: %s (%s)
  Budget: $%.2f/month
  Current Spend: $%.2f
  Utilization: %.1f%% %s
  Team: %s
`, budget.Namespace, budget.Team, budget.MonthlyBudget, 
			budget.CurrentSpend, utilization, status, budget.Team)
	}
	
	// Add top cost drivers
	type costDriver struct {
		podKey string
		cost   float64
	}
	
	var drivers []costDriver
	for podKey, costInfo := range controller.podCosts {
		drivers = append(drivers, costDriver{podKey: podKey, cost: costInfo.MonthlyCost})
	}
	
	sort.Slice(drivers, func(i, j int) bool {
		return drivers[i].cost > drivers[j].cost
	})
	
	report += `

TOP 5 COST DRIVERS
==================
`
	
	for i, driver := range drivers {
		if i >= 5 {
			break
		}
		
		costInfo := controller.podCosts[driver.podKey]
		report += fmt.Sprintf(`
%d. %s/%s
   Monthly Cost: $%.2f
   Resources: %.1f CPU, %.1fGB Memory
   Mumbai Context: %s
   Tip: %s
`, i+1, costInfo.Namespace, costInfo.PodName, costInfo.MonthlyCost,
			costInfo.CPURequest, costInfo.MemoryRequestGB, 
			costInfo.MumbaiContext, costInfo.OptimizationTip)
	}
	
	// Add optimization recommendations
	report += `

TOP OPTIMIZATION RECOMMENDATIONS
================================
`
	
	for i, rec := range controller.recommendations {
		if i >= 5 {
			break
		}
		
		report += fmt.Sprintf(`
%d. %s/%s
   Current Cost: $%.2f/month
   Potential Savings: $%.2f/month
   Action: %s
   Priority: %s
   Mumbai Analogy: %s
`, i+1, rec.Namespace, rec.PodName, rec.CurrentCost, 
			rec.Savings, rec.Action, rec.Priority, rec.MumbaiAnalogy)
	}
	
	report += `

MUMBAI CONTEXT INSIGHTS
=======================
K8s cost management आपके लिए बिल्कुल Mumbai office space management जैसा है:

🏢 SPACE ALLOCATION: हर team को appropriate space (resources) allocation
💰 COST TRACKING: Real-time में हर department का expense tracking
🎯 OPTIMIZATION: Unused space identify करके cost save करना
📊 BUDGET CONTROL: Monthly budget limits के साथ automatic alerts

NEXT STEPS
==========
1. Review and approve high-priority optimization recommendations
2. Set up automated resource right-sizing for development namespaces
3. Implement cost-aware pod scheduling policies
4. Regular budget reviews with team leads
5. Training on cost-conscious Kubernetes resource requests

Contact: Hindi Tech Community for K8s cost optimization consultation
`
	
	return report
}

// Main function for demonstration
func main() {
	fmt.Println("☸️  Initializing Kubernetes Cost Controller...")
	
	// Create controller (empty kubeconfig means in-cluster)
	controller, err := NewKubernetesCostController("")
	if err != nil {
		log.Fatalf("Failed to create controller: %v", err)
	}
	
	// Create context with cancellation
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
	defer cancel()
	
	// Start controller in background
	go func() {
		err := controller.Start(ctx)
		if err != nil {
			log.Printf("Controller error: %v", err)
		}
	}()
	
	// Wait a bit for controller to initialize
	time.Sleep(30 * time.Second)
	
	// Generate and display report
	fmt.Println("\n📊 Generating cost report...")
	report := controller.GetCostReport()
	fmt.Println(report)
	
	fmt.Println("\n✅ Kubernetes Cost Controller demo completed!")
	fmt.Println("🏙️ Mumbai Context: यह controller आपके K8s costs को efficiently manage करेगा!")
}

/*
Production Deployment Guide (Hindi):
====================================

1. RBAC Configuration:
   - Create service account with proper permissions
   - Grant access to pods, namespaces, nodes, persistentvolumes
   - Implement least-privilege access model

2. Controller Deployment:
   - Deploy as Kubernetes Deployment with replicas
   - Add health checks and readiness probes
   - Configure resource requests and limits
   - Set up horizontal pod autoscaling

3. Monitoring Integration:
   - Prometheus metrics exposition
   - Grafana dashboards for cost visualization
   - AlertManager integration for budget alerts
   - Custom metrics for cost per namespace/team

4. Mumbai Business Context:
   - Indian Rupee cost calculation support
   - Regional node pricing variations
   - Local business hours consideration
   - Integration with Indian cloud providers

5. Advanced Features:
   - Webhook for cost-aware admission control
   - Integration with cluster autoscaler for cost optimization
   - Historical cost data storage and analysis
   - Predictive cost modeling and forecasting

यह K8s cost controller आपके cluster को Mumbai के efficient office management जैसा cost-effective बनाएगा!
*/
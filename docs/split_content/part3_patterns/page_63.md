Page 63: Cost Guardrails & FinOps
Make money problems visible before they're problems
THE PROBLEM
Cloud bills surprise:
- Autoscaling goes wild
- Forgotten resources
- Data transfer costs
- Reserved capacity unused
THE SOLUTION
Automated cost controls:
- Real-time spend tracking
- Automatic resource limits
- Anomaly detection
- Optimization recommendations
PSEUDO CODE IMPLEMENTATION
CostGuardian:
    monitor_realtime_spend():
        current_spend = 0
        
        for service in all_services:
            // Real-time cost calculation
            compute_cost = calculate_compute_cost(service)
            storage_cost = calculate_storage_cost(service)
            network_cost = calculate_network_cost(service)
            
            service_cost = compute_cost + storage_cost + network_cost
            current_spend += service_cost
            
            // Check limits
            if service_cost > service.budget_limit:
                trigger_cost_alert(service)
                
            if service_cost > service.hard_limit:
                apply_cost_controls(service)
                
        return current_spend
        
    apply_cost_controls(service):
        controls = service.cost_control_policy
        
        if 'scale_down' in controls:
            reduce_instances(service, controls.min_instances)
            
        if 'switch_to_spot' in controls:
            migrate_to_spot_instances(service)
            
        if 'disable_features' in controls:
            disable_expensive_features(service)
            
        if 'throttle' in controls:
            apply_rate_limiting(service)

CostAnomalyDetector:
    detect_anomalies():
        // Historical baseline
        baseline = calculate_rolling_average(30_days)
        std_dev = calculate_std_deviation(30_days)
        
        current = get_current_spend_rate()
        
        if current > baseline + (2 * std_dev):
            anomaly = {
                'severity': calculate_severity(current, baseline),
                'services': identify_culprit_services(),
                'likely_cause': analyze_recent_changes()
            }
            
            alert_on_call(anomaly)

OptimizationEngine:
    find_savings():
        recommendations = []
        
        // Unused resources
        unused = find_unused_resources()
        for resource in unused:
            recommendations.append({
                'action': 'delete',
                'resource': resource,
                'monthly_savings': calculate_savings(resource)
            })
            
        // Right-sizing
        oversized = find_oversized_instances()
        for instance in oversized:
            recommendations.append({
                'action': 'resize',
                'current': instance.type,
                'recommended': recommend_size(instance),
                'monthly_savings': calculate_resize_savings(instance)
            })
            
        // Reserved instances
        on_demand = find_steady_workloads()
        recommendations.append({
            'action': 'reserve',
            'instances': on_demand,
            'monthly_savings': calculate_ri_savings(on_demand)
        })
        
        return sorted(recommendations, key=lambda r: r.monthly_savings)
Cost Control Patterns:
1. BUDGET ALERTS
   daily_spend > daily_budget * 0.8:
       send_warning()
   
   daily_spend > daily_budget:
       page_on_call()

2. AUTOMATIC SCALING LIMITS
   autoscaling_group.max_size = calculate_from_budget(
       hourly_budget / instance_cost_per_hour
   )

3. SPOT INSTANCE FALLBACK
   on_demand_too_expensive():
       bid_on_spot_instances()
       accept_interruption_risk()

4. FEATURE FLAGS FOR COST
   if monthly_spend > premium_features_budget:
       disable_ml_inference()
       disable_real_time_analytics()
✓ CHOOSE THIS WHEN:

Variable workloads
Multiple teams/projects
Cloud-native architecture
Cost optimization matters
Prevent bill shock

⚠️ BEWARE OF:

Over-optimization affecting SLA
Hidden costs (data transfer)
Reserved capacity waste
Complexity of chargeback
Tool proliferation

REAL EXAMPLES

Netflix: Automated cost anomaly detection
Airbnb: Per-team cost allocation
Spotify: Spot instance orchestration

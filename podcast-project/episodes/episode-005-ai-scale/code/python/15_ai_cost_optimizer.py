#!/usr/bin/env python3
"""
AI Cost Optimizer for Indian Cloud Providers
Episode 5: Code Example 15

Production-ready cost optimization system for AI workloads
Optimized for Indian cloud providers and INR pricing

Author: Code Developer Agent
Context: Cost optimization for Indian AI/ML companies at scale
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from datetime import datetime, timedelta
import asyncio
import aiohttp
import pandas as pd
from abc import ABC, abstractmethod
import schedule
import threading

# Production logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CloudProvider(Enum):
    AWS_MUMBAI = "aws_mumbai"
    AZURE_PUNE = "azure_pune"
    GCP_MUMBAI = "gcp_mumbai"
    ORACLE_HYDERABAD = "oracle_hyderabad"
    ALIBABA_MUMBAI = "alibaba_mumbai"
    # Indian providers
    TATA_COMMUNICATIONS = "tata_communications"
    RELIANCE_JIO = "reliance_jio"
    BHARTI_AIRTEL = "bharti_airtel"

class InstanceType(Enum):
    CPU_SMALL = "cpu_small"
    CPU_LARGE = "cpu_large"
    GPU_T4 = "gpu_t4"
    GPU_V100 = "gpu_v100"
    GPU_A100 = "gpu_a100"
    SPOT_INSTANCE = "spot_instance"

class OptimizationStrategy(Enum):
    COST_FIRST = "cost_first"
    PERFORMANCE_FIRST = "performance_first"
    BALANCED = "balanced"
    SUSTAINABILITY = "sustainability"

@dataclass
class ResourcePricing:
    """Resource pricing information in INR"""
    provider: CloudProvider
    instance_type: InstanceType
    hourly_rate_inr: float
    monthly_rate_inr: float
    spot_rate_inr: Optional[float] = None
    setup_cost_inr: float = 0.0
    data_transfer_cost_per_gb_inr: float = 0.0
    storage_cost_per_gb_month_inr: float = 0.0
    
    # Indian specific
    gst_rate: float = 0.18  # 18% GST in India
    includes_support: bool = False
    data_residency_compliant: bool = True
    availability_zones: List[str] = None
    
    def __post_init__(self):
        if self.availability_zones is None:
            self.availability_zones = ["zone-a", "zone-b"]

@dataclass
class WorkloadProfile:
    """AI workload characteristics for optimization"""
    workload_id: str
    workload_type: str  # training, inference, batch_processing
    avg_cpu_utilization: float
    avg_memory_gb: float
    avg_gpu_utilization: float
    network_io_gb_per_hour: float
    storage_gb: float
    
    # Performance requirements
    max_latency_ms: Optional[float] = None
    min_throughput_rps: Optional[float] = None
    availability_requirement: float = 0.99  # 99% uptime
    
    # Cost constraints
    budget_limit_inr_monthly: Optional[float] = None
    cost_preference: OptimizationStrategy = OptimizationStrategy.BALANCED
    
    # Indian context
    data_residency_required: bool = True
    preferred_regions: List[str] = None
    
    def __post_init__(self):
        if self.preferred_regions is None:
            self.preferred_regions = ["mumbai", "hyderabad", "chennai"]

@dataclass
class OptimizationRecommendation:
    """Cost optimization recommendation"""
    recommendation_id: str
    workload_id: str
    current_cost_inr_monthly: float
    optimized_cost_inr_monthly: float
    savings_inr_monthly: float
    savings_percentage: float
    
    # Recommended configuration
    recommended_provider: CloudProvider
    recommended_instance: InstanceType
    recommended_instances_count: int
    use_spot_instances: bool
    use_reserved_instances: bool
    
    # Performance impact
    performance_impact: str  # "none", "minimal", "moderate", "significant"
    latency_change_ms: Optional[float] = None
    throughput_change_rps: Optional[float] = None
    
    # Implementation details
    migration_cost_inr: float = 0.0
    implementation_complexity: str = "low"  # low, medium, high
    estimated_setup_time_hours: float = 2.0
    
    # Risk assessment
    risks: List[str] = None
    mitigation_strategies: List[str] = None
    
    def __post_init__(self):
        if self.risks is None:
            self.risks = []
        if self.mitigation_strategies is None:
            self.mitigation_strategies = []

class PricingDatabase:
    """Database of cloud pricing for Indian providers"""
    
    def __init__(self):
        self.pricing_data = {}
        self.last_updated = None
        self._initialize_pricing_data()
    
    def _initialize_pricing_data(self):
        """Initialize pricing data for Indian cloud providers"""
        
        # AWS Mumbai pricing (converted to INR, approximate rates)
        self.pricing_data[CloudProvider.AWS_MUMBAI] = {
            InstanceType.CPU_SMALL: ResourcePricing(
                provider=CloudProvider.AWS_MUMBAI,
                instance_type=InstanceType.CPU_SMALL,
                hourly_rate_inr=15.0,  # ~$0.18/hour
                monthly_rate_inr=10800.0,
                spot_rate_inr=5.0,
                data_transfer_cost_per_gb_inr=7.5,
                storage_cost_per_gb_month_inr=8.0
            ),
            InstanceType.GPU_T4: ResourcePricing(
                provider=CloudProvider.AWS_MUMBAI,
                instance_type=InstanceType.GPU_T4,
                hourly_rate_inr=50.0,
                monthly_rate_inr=36000.0,
                spot_rate_inr=20.0,
                data_transfer_cost_per_gb_inr=7.5,
                storage_cost_per_gb_month_inr=8.0
            ),
            InstanceType.GPU_V100: ResourcePricing(
                provider=CloudProvider.AWS_MUMBAI,
                instance_type=InstanceType.GPU_V100,
                hourly_rate_inr=200.0,
                monthly_rate_inr=144000.0,
                spot_rate_inr=80.0,
                data_transfer_cost_per_gb_inr=7.5,
                storage_cost_per_gb_month_inr=8.0
            )
        }
        
        # Azure Pune pricing
        self.pricing_data[CloudProvider.AZURE_PUNE] = {
            InstanceType.CPU_SMALL: ResourcePricing(
                provider=CloudProvider.AZURE_PUNE,
                instance_type=InstanceType.CPU_SMALL,
                hourly_rate_inr=18.0,
                monthly_rate_inr=12960.0,
                spot_rate_inr=6.0,
                data_transfer_cost_per_gb_inr=8.0,
                storage_cost_per_gb_month_inr=7.0
            ),
            InstanceType.GPU_T4: ResourcePricing(
                provider=CloudProvider.AZURE_PUNE,
                instance_type=InstanceType.GPU_T4,
                hourly_rate_inr=55.0,
                monthly_rate_inr=39600.0,
                spot_rate_inr=22.0,
                data_transfer_cost_per_gb_inr=8.0,
                storage_cost_per_gb_month_inr=7.0
            )
        }
        
        # GCP Mumbai pricing
        self.pricing_data[CloudProvider.GCP_MUMBAI] = {
            InstanceType.CPU_SMALL: ResourcePricing(
                provider=CloudProvider.GCP_MUMBAI,
                instance_type=InstanceType.CPU_SMALL,
                hourly_rate_inr=16.0,
                monthly_rate_inr=11520.0,
                spot_rate_inr=4.5,
                data_transfer_cost_per_gb_inr=6.0,
                storage_cost_per_gb_month_inr=6.0
            ),
            InstanceType.GPU_T4: ResourcePricing(
                provider=CloudProvider.GCP_MUMBAI,
                instance_type=InstanceType.GPU_T4,
                hourly_rate_inr=48.0,
                monthly_rate_inr=34560.0,
                spot_rate_inr=18.0,
                data_transfer_cost_per_gb_inr=6.0,
                storage_cost_per_gb_month_inr=6.0
            )
        }
        
        # Indian cloud providers (competitive pricing)
        self.pricing_data[CloudProvider.TATA_COMMUNICATIONS] = {
            InstanceType.CPU_SMALL: ResourcePricing(
                provider=CloudProvider.TATA_COMMUNICATIONS,
                instance_type=InstanceType.CPU_SMALL,
                hourly_rate_inr=12.0,  # 20% cheaper than global providers
                monthly_rate_inr=8640.0,
                data_transfer_cost_per_gb_inr=5.0,
                storage_cost_per_gb_month_inr=5.0,
                includes_support=True
            ),
            InstanceType.GPU_T4: ResourcePricing(
                provider=CloudProvider.TATA_COMMUNICATIONS,
                instance_type=InstanceType.GPU_T4,
                hourly_rate_inr=40.0,
                monthly_rate_inr=28800.0,
                data_transfer_cost_per_gb_inr=5.0,
                storage_cost_per_gb_month_inr=5.0,
                includes_support=True
            )
        }
        
        self.last_updated = time.time()
        logger.info(f"Initialized pricing data for {len(self.pricing_data)} cloud providers")
    
    def get_pricing(self, provider: CloudProvider, instance_type: InstanceType) -> Optional[ResourcePricing]:
        """Get pricing for specific provider and instance type"""
        return self.pricing_data.get(provider, {}).get(instance_type)
    
    def get_all_options_for_workload(self, workload: WorkloadProfile) -> List[Tuple[CloudProvider, InstanceType, ResourcePricing]]:
        """Get all viable options for a workload"""
        
        options = []
        
        for provider, instances in self.pricing_data.items():
            for instance_type, pricing in instances.items():
                # Check data residency requirements
                if workload.data_residency_required and not pricing.data_residency_compliant:
                    continue
                
                # Check if instance can handle the workload
                if self._can_handle_workload(instance_type, workload):
                    options.append((provider, instance_type, pricing))
        
        return options
    
    def _can_handle_workload(self, instance_type: InstanceType, workload: WorkloadProfile) -> bool:
        """Check if instance type can handle the workload"""
        
        # Simple capacity mapping (in production, use detailed specs)
        capacity_map = {
            InstanceType.CPU_SMALL: {"cpu": 4, "memory_gb": 16, "gpu": 0},
            InstanceType.CPU_LARGE: {"cpu": 16, "memory_gb": 64, "gpu": 0},
            InstanceType.GPU_T4: {"cpu": 8, "memory_gb": 32, "gpu": 1},
            InstanceType.GPU_V100: {"cpu": 16, "memory_gb": 64, "gpu": 1},
            InstanceType.GPU_A100: {"cpu": 32, "memory_gb": 128, "gpu": 1}
        }
        
        capacity = capacity_map.get(instance_type, {"cpu": 0, "memory_gb": 0, "gpu": 0})
        
        # Check requirements
        memory_needed = workload.avg_memory_gb
        gpu_needed = 1 if workload.avg_gpu_utilization > 0 else 0
        
        return (capacity["memory_gb"] >= memory_needed and 
                capacity["gpu"] >= gpu_needed)

class CostOptimizer:
    """Main cost optimization engine"""
    
    def __init__(self):
        self.pricing_db = PricingDatabase()
        self.optimization_history = []
        self.current_workloads = {}
    
    def register_workload(self, workload: WorkloadProfile):
        """Register a workload for optimization tracking"""
        self.current_workloads[workload.workload_id] = workload
        logger.info(f"Registered workload: {workload.workload_id} ({workload.workload_type})")
    
    def optimize_workload(self, workload_id: str, current_setup: Optional[Dict] = None) -> OptimizationRecommendation:
        """Generate optimization recommendation for a workload"""
        
        if workload_id not in self.current_workloads:
            raise ValueError(f"Workload {workload_id} not found")
        
        workload = self.current_workloads[workload_id]
        
        # Get all viable options
        options = self.pricing_db.get_all_options_for_workload(workload)
        
        if not options:
            raise ValueError(f"No viable cloud options found for workload {workload_id}")
        
        # Calculate current cost if provided
        current_monthly_cost = self._calculate_current_cost(current_setup) if current_setup else 50000.0
        
        # Find optimal configuration based on strategy
        optimal_config = self._find_optimal_configuration(workload, options)
        
        # Calculate optimized cost
        optimized_cost = self._calculate_workload_cost(workload, optimal_config)
        
        # Create recommendation
        recommendation = self._create_recommendation(
            workload, optimal_config, current_monthly_cost, optimized_cost
        )
        
        # Store in history
        self.optimization_history.append(recommendation)
        
        logger.info(f"Generated optimization for {workload_id}: "
                   f"₹{current_monthly_cost:,.0f} -> ₹{optimized_cost:,.0f} "
                   f"({recommendation.savings_percentage:.1f}% savings)")
        
        return recommendation
    
    def _find_optimal_configuration(self, workload: WorkloadProfile, options: List[Tuple[CloudProvider, InstanceType, ResourcePricing]]) -> Tuple[CloudProvider, InstanceType, ResourcePricing]:
        """Find optimal configuration based on workload strategy"""
        
        if workload.cost_preference == OptimizationStrategy.COST_FIRST:
            # Sort by total monthly cost
            return min(options, key=lambda x: self._calculate_workload_cost(workload, x))
        
        elif workload.cost_preference == OptimizationStrategy.PERFORMANCE_FIRST:
            # Prefer GPU instances and higher-tier providers
            gpu_options = [opt for opt in options if "gpu" in opt[1].value.lower()]
            if gpu_options:
                return max(gpu_options, key=lambda x: self._get_performance_score(x[1]))
            else:
                return max(options, key=lambda x: self._get_performance_score(x[1]))
        
        else:  # BALANCED or SUSTAINABILITY
            # Score based on cost-performance ratio
            scored_options = []
            for option in options:
                cost = self._calculate_workload_cost(workload, option)
                performance_score = self._get_performance_score(option[1])
                
                # Add sustainability bonus for Indian providers
                sustainability_bonus = 1.1 if "tata" in option[0].value or "jio" in option[0].value else 1.0
                
                balanced_score = (performance_score * sustainability_bonus) / cost
                scored_options.append((option, balanced_score))
            
            return max(scored_options, key=lambda x: x[1])[0]
    
    def _calculate_current_cost(self, current_setup: Dict) -> float:
        """Calculate current monthly cost from setup description"""
        
        # Mock calculation based on setup description
        base_cost = current_setup.get('base_monthly_cost', 30000.0)
        instance_count = current_setup.get('instance_count', 2)
        
        return base_cost * instance_count
    
    def _calculate_workload_cost(self, workload: WorkloadProfile, config: Tuple[CloudProvider, InstanceType, ResourcePricing]) -> float:
        """Calculate total monthly cost for workload with specific configuration"""
        
        provider, instance_type, pricing = config
        
        # Base compute cost
        base_monthly_cost = pricing.monthly_rate_inr
        
        # Storage cost
        storage_cost = workload.storage_gb * pricing.storage_cost_per_gb_month_inr
        
        # Data transfer cost (estimate)
        monthly_transfer_gb = workload.network_io_gb_per_hour * 24 * 30
        transfer_cost = monthly_transfer_gb * pricing.data_transfer_cost_per_gb_inr
        
        # Add GST
        subtotal = base_monthly_cost + storage_cost + transfer_cost
        total_with_gst = subtotal * (1 + pricing.gst_rate)
        
        return total_with_gst
    
    def _get_performance_score(self, instance_type: InstanceType) -> float:
        """Get performance score for instance type"""
        
        performance_scores = {
            InstanceType.CPU_SMALL: 1.0,
            InstanceType.CPU_LARGE: 3.0,
            InstanceType.GPU_T4: 5.0,
            InstanceType.GPU_V100: 8.0,
            InstanceType.GPU_A100: 12.0
        }
        
        return performance_scores.get(instance_type, 1.0)
    
    def _create_recommendation(self, workload: WorkloadProfile, optimal_config: Tuple[CloudProvider, InstanceType, ResourcePricing], current_cost: float, optimized_cost: float) -> OptimizationRecommendation:
        """Create detailed optimization recommendation"""
        
        provider, instance_type, pricing = optimal_config
        
        savings = current_cost - optimized_cost
        savings_percentage = (savings / current_cost) * 100 if current_cost > 0 else 0
        
        # Estimate performance impact
        performance_impact = "minimal" if savings_percentage < 20 else "moderate"
        
        # Calculate migration cost
        migration_cost = 2000.0  # Base migration cost in INR
        if provider.value.startswith(('tata', 'reliance', 'bharti')):
            migration_cost *= 1.5  # Higher migration cost for local providers
        
        # Assess risks
        risks = []
        mitigation_strategies = []
        
        if "spot" in instance_type.value:
            risks.append("Spot instance interruption risk")
            mitigation_strategies.append("Implement checkpointing and auto-restart")
        
        if provider.value.startswith(('tata', 'reliance', 'bharti')):
            risks.append("Limited global presence for multi-region deployments")
            mitigation_strategies.append("Use hybrid cloud strategy for global reach")
        
        if savings_percentage > 30:
            risks.append("Significant cost reduction may impact performance")
            mitigation_strategies.append("Thorough testing in staging environment")
        
        recommendation = OptimizationRecommendation(
            recommendation_id=f"opt_{workload.workload_id}_{int(time.time())}",
            workload_id=workload.workload_id,
            current_cost_inr_monthly=current_cost,
            optimized_cost_inr_monthly=optimized_cost,
            savings_inr_monthly=savings,
            savings_percentage=savings_percentage,
            recommended_provider=provider,
            recommended_instance=instance_type,
            recommended_instances_count=1,
            use_spot_instances=pricing.spot_rate_inr is not None and savings_percentage > 40,
            use_reserved_instances=workload.workload_type == "training",
            performance_impact=performance_impact,
            migration_cost_inr=migration_cost,
            implementation_complexity="medium" if len(risks) > 1 else "low",
            estimated_setup_time_hours=4.0 if len(risks) > 1 else 2.0,
            risks=risks,
            mitigation_strategies=mitigation_strategies
        )
        
        return recommendation
    
    def get_portfolio_optimization(self) -> Dict[str, Any]:
        """Get optimization recommendations for entire workload portfolio"""
        
        if not self.current_workloads:
            return {"error": "No workloads registered"}
        
        total_current_cost = 0
        total_optimized_cost = 0
        recommendations = []
        
        for workload_id in self.current_workloads:
            try:
                recommendation = self.optimize_workload(workload_id)
                recommendations.append(recommendation)
                total_current_cost += recommendation.current_cost_inr_monthly
                total_optimized_cost += recommendation.optimized_cost_inr_monthly
            except Exception as e:
                logger.error(f"Failed to optimize workload {workload_id}: {e}")
        
        total_savings = total_current_cost - total_optimized_cost
        total_savings_percentage = (total_savings / total_current_cost) * 100 if total_current_cost > 0 else 0
        
        # Provider distribution analysis
        provider_distribution = {}
        for rec in recommendations:
            provider = rec.recommended_provider.value
            provider_distribution[provider] = provider_distribution.get(provider, 0) + 1
        
        return {
            "portfolio_summary": {
                "total_workloads": len(self.current_workloads),
                "total_current_cost_inr_monthly": f"₹{total_current_cost:,.0f}",
                "total_optimized_cost_inr_monthly": f"₹{total_optimized_cost:,.0f}",
                "total_savings_inr_monthly": f"₹{total_savings:,.0f}",
                "total_savings_percentage": f"{total_savings_percentage:.1f}%",
                "annual_savings_inr": f"₹{total_savings * 12:,.0f}"
            },
            "recommendations": recommendations,
            "provider_distribution": provider_distribution,
            "optimization_summary": {
                "high_impact_optimizations": len([r for r in recommendations if r.savings_percentage > 30]),
                "spot_instance_opportunities": len([r for r in recommendations if r.use_spot_instances]),
                "indian_provider_recommendations": len([r for r in recommendations if "tata" in r.recommended_provider.value or "jio" in r.recommended_provider.value])
            }
        }
    
    def generate_cost_report(self) -> str:
        """Generate comprehensive cost optimization report"""
        
        portfolio_data = self.get_portfolio_optimization()
        
        if "error" in portfolio_data:
            return "No data available for cost report"
        
        summary = portfolio_data["portfolio_summary"]
        recommendations = portfolio_data["recommendations"]
        
        report = f"""
AI Cost Optimization Report - Indian Cloud Infrastructure
========================================================

Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S IST')}

Executive Summary:
-----------------
• Total Workloads Analyzed: {summary['total_workloads']}
• Current Monthly Cost: {summary['total_current_cost_inr_monthly']}
• Optimized Monthly Cost: {summary['total_optimized_cost_inr_monthly']}
• Monthly Savings: {summary['total_savings_inr_monthly']} ({summary['total_savings_percentage']})
• Annual Savings Potential: {summary['annual_savings_inr']}

Top Optimization Opportunities:
------------------------------
"""
        
        # Sort recommendations by savings percentage
        top_recommendations = sorted(recommendations, key=lambda x: x.savings_percentage, reverse=True)[:5]
        
        for i, rec in enumerate(top_recommendations, 1):
            report += f"""
{i}. {rec.workload_id}
   Current Cost: ₹{rec.current_cost_inr_monthly:,.0f}/month
   Optimized Cost: ₹{rec.optimized_cost_inr_monthly:,.0f}/month
   Savings: ₹{rec.savings_inr_monthly:,.0f}/month ({rec.savings_percentage:.1f}%)
   Recommended: {rec.recommended_provider.value} - {rec.recommended_instance.value}
   Implementation: {rec.implementation_complexity} complexity
   
"""
        
        report += f"""
Provider Recommendations:
------------------------
{chr(10).join(f"• {provider}: {count} workloads" for provider, count in portfolio_data["provider_distribution"].items())}

Implementation Priorities:
-------------------------
1. High Impact Optimizations: {portfolio_data["optimization_summary"]["high_impact_optimizations"]} workloads
2. Spot Instance Opportunities: {portfolio_data["optimization_summary"]["spot_instance_opportunities"]} workloads  
3. Indian Provider Migration: {portfolio_data["optimization_summary"]["indian_provider_recommendations"]} workloads

Key Benefits of Optimization:
----------------------------
• Significant cost reduction while maintaining performance
• Enhanced data residency compliance with Indian providers
• Improved sustainability with local cloud infrastructure
• Better support and reduced latency for Indian operations
• GST optimization and simplified billing in INR

Next Steps:
----------
1. Review and prioritize high-impact optimizations
2. Conduct proof-of-concept with top recommendations
3. Implement gradual migration strategy
4. Monitor performance and cost post-implementation
5. Schedule regular optimization reviews (quarterly)

Note: All costs include 18% GST as applicable in India.
Contact: AI Infrastructure Team for implementation support.
"""
        
        return report.strip()

# Example usage and testing
def test_ai_cost_optimizer():
    """Test AI cost optimizer with Indian cloud scenarios"""
    
    print("💰 AI Cost Optimizer Test - Indian Cloud Infrastructure")
    print("=" * 65)
    
    # Initialize optimizer
    optimizer = CostOptimizer()
    
    # Create sample workloads representing different AI scenarios
    workloads = [
        WorkloadProfile(
            workload_id="hindi_nlp_training",
            workload_type="training",
            avg_cpu_utilization=70,
            avg_memory_gb=32,
            avg_gpu_utilization=85,
            network_io_gb_per_hour=10,
            storage_gb=500,
            budget_limit_inr_monthly=80000,
            cost_preference=OptimizationStrategy.BALANCED,
            data_residency_required=True,
            preferred_regions=["mumbai", "hyderabad"]
        ),
        WorkloadProfile(
            workload_id="recommendation_inference",
            workload_type="inference",
            avg_cpu_utilization=40,
            avg_memory_gb=16,
            avg_gpu_utilization=30,
            network_io_gb_per_hour=50,
            storage_gb=100,
            max_latency_ms=100,
            min_throughput_rps=1000,
            budget_limit_inr_monthly=50000,
            cost_preference=OptimizationStrategy.COST_FIRST,
            data_residency_required=True
        ),
        WorkloadProfile(
            workload_id="batch_processing",
            workload_type="batch_processing",
            avg_cpu_utilization=60,
            avg_memory_gb=64,
            avg_gpu_utilization=0,
            network_io_gb_per_hour=5,
            storage_gb=1000,
            budget_limit_inr_monthly=30000,
            cost_preference=OptimizationStrategy.COST_FIRST,
            data_residency_required=False
        ),
        WorkloadProfile(
            workload_id="research_experiment",
            workload_type="training",
            avg_cpu_utilization=80,
            avg_memory_gb=128,
            avg_gpu_utilization=95,
            network_io_gb_per_hour=2,
            storage_gb=200,
            budget_limit_inr_monthly=200000,
            cost_preference=OptimizationStrategy.PERFORMANCE_FIRST,
            data_residency_required=False
        )
    ]
    
    # Register workloads
    print(f"📝 Registering {len(workloads)} AI workloads...")
    for workload in workloads:
        optimizer.register_workload(workload)
    
    print(f"✅ Workloads registered:")
    for workload in workloads:
        print(f"   • {workload.workload_id} ({workload.workload_type})")
        print(f"     Strategy: {workload.cost_preference.value}")
        print(f"     Budget: ₹{workload.budget_limit_inr_monthly or 'No limit'}")
        print(f"     Data residency: {workload.data_residency_required}")
    
    # Generate individual optimizations
    print(f"\n🔍 Generating optimization recommendations...")
    
    current_setups = [
        {"base_monthly_cost": 60000, "instance_count": 2},  # Current expensive setup
        {"base_monthly_cost": 40000, "instance_count": 3},
        {"base_monthly_cost": 25000, "instance_count": 4},
        {"base_monthly_cost": 150000, "instance_count": 1}
    ]
    
    individual_results = []
    for i, workload in enumerate(workloads):
        try:
            recommendation = optimizer.optimize_workload(workload.workload_id, current_setups[i])
            individual_results.append(recommendation)
            
            print(f"\n   🎯 {workload.workload_id}:")
            print(f"      Current: ₹{recommendation.current_cost_inr_monthly:,.0f}/month")
            print(f"      Optimized: ₹{recommendation.optimized_cost_inr_monthly:,.0f}/month")
            print(f"      Savings: ₹{recommendation.savings_inr_monthly:,.0f} ({recommendation.savings_percentage:.1f}%)")
            print(f"      Provider: {recommendation.recommended_provider.value}")
            print(f"      Instance: {recommendation.recommended_instance.value}")
            print(f"      Spot instances: {recommendation.use_spot_instances}")
            print(f"      Migration cost: ₹{recommendation.migration_cost_inr:,.0f}")
            
            if recommendation.risks:
                print(f"      Risks: {len(recommendation.risks)} identified")
                
        except Exception as e:
            print(f"   ❌ Failed to optimize {workload.workload_id}: {e}")
    
    # Portfolio optimization
    print(f"\n📊 Portfolio Optimization Analysis...")
    portfolio_results = optimizer.get_portfolio_optimization()
    
    if "error" not in portfolio_results:
        summary = portfolio_results["portfolio_summary"]
        print(f"   Total Current Cost: {summary['total_current_cost_inr_monthly']}")
        print(f"   Total Optimized Cost: {summary['total_optimized_cost_inr_monthly']}")
        print(f"   Total Monthly Savings: {summary['total_savings_inr_monthly']}")
        print(f"   Annual Savings: {summary['annual_savings_inr']}")
        
        print(f"\n   Provider Distribution:")
        for provider, count in portfolio_results["provider_distribution"].items():
            print(f"     • {provider}: {count} workloads")
        
        opt_summary = portfolio_results["optimization_summary"]
        print(f"\n   Optimization Opportunities:")
        print(f"     • High Impact: {opt_summary['high_impact_optimizations']} workloads")
        print(f"     • Spot Instance: {opt_summary['spot_instance_opportunities']} workloads")
        print(f"     • Indian Providers: {opt_summary['indian_provider_recommendations']} workloads")
    
    # Generate comprehensive report
    print(f"\n📄 Generating Cost Optimization Report...")
    report = optimizer.generate_cost_report()
    
    # Save report to file
    report_file = f"/tmp/ai_cost_optimization_report_{int(time.time())}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"   Report saved to: {report_file}")
    print(f"\n📋 Report Summary (first 500 characters):")
    print(f"{report[:500]}...")
    
    print(f"\n🎯 Cost Optimization Features Demonstrated:")
    print(f"   ✅ Multi-provider cost comparison (AWS, Azure, GCP, Indian providers)")
    print(f"   ✅ Workload-specific optimization strategies")
    print(f"   ✅ INR pricing with GST calculations")
    print(f"   ✅ Data residency compliance for Indian regulations")
    print(f"   ✅ Spot instance and reserved instance recommendations")
    print(f"   ✅ Risk assessment and mitigation strategies")
    print(f"   ✅ Portfolio-level optimization analysis")
    print(f"   ✅ Implementation complexity assessment")
    print(f"   ✅ Comprehensive cost optimization reporting")

if __name__ == "__main__":
    test_ai_cost_optimizer()
#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 12: Capacity Planning Metrics for Indian Scale

भारतीय context: Diwali shopping season capacity planning
जैसे BBD के लिए infrastructure scaling predict करना

Real-world scenario: IRCTC Tatkal capacity planning  
Challenge: Festival peaks, Regional variations, Cost optimization
"""

import time
import json
import asyncio
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import pandas as pd
import structlog

# भारतीय capacity planning categories
class ResourceType(Enum):
    """Resource types for capacity planning"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage" 
    NETWORK = "network"
    DATABASE_CONNECTIONS = "database_connections"
    QUEUE_CAPACITY = "queue_capacity"
    CACHE_MEMORY = "cache_memory"
    CDN_BANDWIDTH = "cdn_bandwidth"

class EventType(Enum):
    """Indian business events that drive capacity needs"""
    BIG_BILLION_DAYS = "big_billion_days"
    DIWALI = "diwali"
    HOLI = "holi"
    EID = "eid"
    NEW_YEAR = "new_year"
    CRICKET_MATCH = "cricket_match"
    MOVIE_RELEASE = "movie_release"
    TATKAL_BOOKING = "tatkal_booking"
    SALARY_DAY = "salary_day"
    WEEKEND_RUSH = "weekend_rush"

class ScalingStrategy(Enum):
    """Scaling strategies for different scenarios"""
    HORIZONTAL = "horizontal"      # Add more instances
    VERTICAL = "vertical"          # Upgrade instance sizes
    HYBRID = "hybrid"             # Combination approach
    CLOUD_BURST = "cloud_burst"   # Temporary cloud expansion
    REGIONAL = "regional"         # Scale specific regions only

@dataclass
class CapacityMetric:
    """Individual capacity metric"""
    resource_type: ResourceType
    current_utilization: float    # Current usage percentage
    current_capacity: float       # Current total capacity
    timestamp: datetime
    region: str
    service: str
    predicted_demand: float       # Predicted future demand
    recommendation: str
    confidence_score: float       # Prediction confidence 0-1
    cost_impact_inr: float       # Cost impact in INR

@dataclass
class CapacityForecast:
    """Capacity forecast for specific time period"""
    resource_type: ResourceType
    time_horizon: str            # "1_week", "1_month", "3_months"
    base_demand: float
    peak_demand: float
    growth_rate: float
    seasonal_multiplier: float
    event_multiplier: float
    recommended_capacity: float
    scaling_strategy: ScalingStrategy
    implementation_timeline: str
    estimated_cost_inr: float

class IndianCapacityPlanningSystem:
    """
    Indian Scale Capacity Planning System
    
    Features:
    - Festival season predictions
    - Regional demand variations
    - Cost-optimized scaling
    - Multi-cloud resource planning
    - Business event correlation
    - Auto-scaling recommendations
    """
    
    def __init__(self, service_name: str, region: str = "india"):
        self.service_name = service_name
        self.region = region
        self.current_time = datetime.now()
        
        # Historical data storage
        self.historical_metrics = defaultdict(lambda: deque(maxlen=10080))  # 7 days at 1-min resolution
        self.capacity_forecasts = {}
        
        # Configuration
        self.planning_config = self._initialize_planning_config()
        self.indian_events_calendar = self._initialize_indian_events_calendar()
        self.regional_patterns = self._initialize_regional_patterns()
        self.cost_models = self._initialize_cost_models()
        
        # Machine learning models (simplified for demo)
        self.demand_models = self._initialize_demand_models()
        
        # Logger
        self.logger = structlog.get_logger("indian-capacity-planning")
        
    def _initialize_planning_config(self) -> Dict[str, Any]:
        """Initialize capacity planning configuration"""
        
        return {
            "utilization_thresholds": {
                "cpu": {"safe": 70, "warning": 80, "critical": 90},
                "memory": {"safe": 75, "warning": 85, "critical": 95},
                "storage": {"safe": 80, "warning": 90, "critical": 95},
                "network": {"safe": 60, "warning": 75, "critical": 85},
                "database_connections": {"safe": 70, "warning": 85, "critical": 95}
            },
            
            "scaling_parameters": {
                "min_scale_up_percentage": 20,      # Minimum 20% scale-up
                "max_scale_up_percentage": 300,     # Maximum 300% scale-up
                "scale_down_threshold": 40,         # Scale down if utilization < 40%
                "cooldown_period_minutes": 15,     # Wait 15 minutes between scaling
                "prediction_confidence_threshold": 0.7  # Require 70% confidence
            },
            
            "business_constraints": {
                "budget_limit_monthly_inr": 10000000,  # ₹1Cr monthly budget
                "peak_budget_multiplier": 3,           # 3x budget during peaks
                "cost_optimization_priority": True,    # Prioritize cost optimization
                "compliance_requirements": ["data_localization", "rbi_guidelines"]
            },
            
            "time_horizons": {
                "short_term": "1_week",
                "medium_term": "1_month", 
                "long_term": "3_months",
                "annual": "1_year"
            }
        }
        
    def _initialize_indian_events_calendar(self) -> Dict[str, Dict]:
        """Initialize Indian business events calendar"""
        
        return {
            "big_billion_days_2024": {
                "event_type": EventType.BIG_BILLION_DAYS,
                "start_date": "2024-09-29",
                "end_date": "2024-10-06",
                "traffic_multiplier": 12.0,     # 12x normal traffic
                "duration_days": 8,
                "affected_services": ["web", "mobile", "payments", "logistics"],
                "peak_hours": ["00:00", "12:00", "20:00"],
                "regional_impact": {"mumbai": 15.0, "bangalore": 12.0, "delhi": 14.0}
            },
            
            "diwali_2024": {
                "event_type": EventType.DIWALI,
                "start_date": "2024-10-31",
                "end_date": "2024-11-03",
                "traffic_multiplier": 8.0,
                "duration_days": 4,
                "affected_services": ["payments", "web", "mobile"],
                "peak_hours": ["18:00", "19:00", "20:00"],
                "regional_impact": {"north_india": 10.0, "west_india": 9.0}
            },
            
            "new_year_2024": {
                "event_type": EventType.NEW_YEAR,
                "start_date": "2024-12-31",
                "end_date": "2025-01-01", 
                "traffic_multiplier": 15.0,     # Highest for food delivery
                "duration_days": 2,
                "affected_services": ["food_delivery", "ride_booking", "payments"],
                "peak_hours": ["23:00", "23:30", "00:00", "00:30"],
                "regional_impact": {"metros": 20.0, "tier1_cities": 12.0}
            },
            
            "cricket_world_cup_final": {
                "event_type": EventType.CRICKET_MATCH,
                "start_date": "2024-11-19",
                "end_date": "2024-11-19",
                "traffic_multiplier": 25.0,     # Massive spike for streaming
                "duration_days": 1,
                "affected_services": ["streaming", "social_media", "payments"],
                "peak_hours": ["14:00", "15:00", "16:00", "17:00"],
                "regional_impact": {"all_india": 25.0}
            },
            
            "monthly_salary_days": {
                "event_type": EventType.SALARY_DAY,
                "recurring": "monthly",
                "dates": ["last_working_day", "1st", "2nd"],
                "traffic_multiplier": 3.0,
                "affected_services": ["banking", "payments", "shopping"],
                "peak_hours": ["10:00", "14:00", "19:00"],
                "regional_impact": {"all_india": 3.0}
            },
            
            "tatkal_booking_daily": {
                "event_type": EventType.TATKAL_BOOKING,
                "recurring": "daily",
                "time": "10:00",
                "traffic_multiplier": 50.0,     # Extreme spike for 30 minutes
                "duration_minutes": 30,
                "affected_services": ["irctc_booking"],
                "regional_impact": {"all_india": 50.0}
            }
        }
        
    def _initialize_regional_patterns(self) -> Dict[str, Dict]:
        """Initialize regional demand patterns"""
        
        return {
            "mumbai": {
                "base_multiplier": 1.5,          # 1.5x base traffic
                "peak_hours": ["09:00-12:00", "18:00-22:00"],
                "growth_rate_monthly": 8.0,      # 8% monthly growth
                "festival_sensitivity": 1.2,     # 20% more sensitive to festivals
                "infrastructure_cost_multiplier": 1.3  # 30% higher costs
            },
            
            "bangalore": {
                "base_multiplier": 1.3,
                "peak_hours": ["08:00-11:00", "17:00-21:00"],
                "growth_rate_monthly": 12.0,     # Higher growth rate
                "festival_sensitivity": 1.0,
                "infrastructure_cost_multiplier": 1.1  # 10% higher costs
            },
            
            "delhi": {
                "base_multiplier": 1.4,
                "peak_hours": ["09:00-12:00", "19:00-23:00"],
                "growth_rate_monthly": 6.0,
                "festival_sensitivity": 1.3,     # Very festival sensitive
                "infrastructure_cost_multiplier": 1.2  # 20% higher costs
            },
            
            "tier2_cities": {
                "base_multiplier": 0.8,
                "peak_hours": ["18:00-22:00"],
                "growth_rate_monthly": 15.0,     # Highest growth
                "festival_sensitivity": 1.5,     # Most festival sensitive
                "infrastructure_cost_multiplier": 0.8  # 20% lower costs
            },
            
            "tier3_cities": {
                "base_multiplier": 0.4,
                "peak_hours": ["19:00-21:00"],
                "growth_rate_monthly": 20.0,     # Explosive growth
                "festival_sensitivity": 2.0,     # 2x sensitivity
                "infrastructure_cost_multiplier": 0.6  # 40% lower costs
            }
        }
        
    def _initialize_cost_models(self) -> Dict[str, Dict]:
        """Initialize cost models for different resources"""
        
        return {
            "aws": {
                "cpu": {"cost_per_vcpu_per_hour": 8.5},      # ₹8.5 per vCPU hour
                "memory": {"cost_per_gb_per_hour": 1.2},     # ₹1.2 per GB hour
                "storage": {"cost_per_gb_per_month": 2.3},   # ₹2.3 per GB month
                "network": {"cost_per_gb": 0.5},             # ₹0.5 per GB transfer
                "database": {"cost_per_hour": 400}           # ₹400 per hour for db.r5.large
            },
            
            "azure": {
                "cpu": {"cost_per_vcpu_per_hour": 9.0},      # Slightly higher
                "memory": {"cost_per_gb_per_hour": 1.3},
                "storage": {"cost_per_gb_per_month": 2.1},   # Slightly lower
                "network": {"cost_per_gb": 0.4},
                "database": {"cost_per_hour": 380}
            },
            
            "gcp": {
                "cpu": {"cost_per_vcpu_per_hour": 8.0},      # Competitive pricing
                "memory": {"cost_per_gb_per_hour": 1.1},
                "storage": {"cost_per_gb_per_month": 2.0},
                "network": {"cost_per_gb": 0.3},             # Best network pricing
                "database": {"cost_per_hour": 360}
            },
            
            "on_premise": {
                "cpu": {"cost_per_vcpu_per_hour": 4.0},      # Lower operational cost
                "memory": {"cost_per_gb_per_hour": 0.6},
                "storage": {"cost_per_gb_per_month": 1.0},
                "network": {"cost_per_gb": 0.1},
                "database": {"cost_per_hour": 200},
                "initial_capex_multiplier": 24              # 24x higher upfront cost
            }
        }
        
    def _initialize_demand_models(self) -> Dict[str, Any]:
        """Initialize demand prediction models (simplified)"""
        
        return {
            "linear_trend": {
                "enabled": True,
                "accuracy": 0.75,
                "best_for": ["steady_growth", "seasonal_patterns"]
            },
            
            "exponential_smoothing": {
                "enabled": True,
                "accuracy": 0.80,
                "best_for": ["trending_data", "seasonal_variations"]
            },
            
            "arima": {
                "enabled": True,
                "accuracy": 0.85,
                "best_for": ["time_series", "complex_patterns"]
            },
            
            "festival_multiplier": {
                "enabled": True,
                "accuracy": 0.70,
                "best_for": ["event_driven_spikes"]
            }
        }
        
    def collect_capacity_metrics(self, service: str, region: str) -> List[CapacityMetric]:
        """Collect current capacity metrics for a service"""
        
        current_time = datetime.now()
        metrics = []
        
        # CPU Metrics
        cpu_utilization = self._simulate_cpu_utilization(service, region)
        cpu_capacity = self._get_current_capacity(service, region, ResourceType.CPU)
        
        cpu_metric = CapacityMetric(
            resource_type=ResourceType.CPU,
            current_utilization=cpu_utilization,
            current_capacity=cpu_capacity,
            timestamp=current_time,
            region=region,
            service=service,
            predicted_demand=self._predict_demand(ResourceType.CPU, service, region),
            recommendation=self._generate_scaling_recommendation(ResourceType.CPU, cpu_utilization),
            confidence_score=0.85,
            cost_impact_inr=self._calculate_cost_impact(ResourceType.CPU, service, region)
        )
        metrics.append(cpu_metric)
        
        # Memory Metrics
        memory_utilization = self._simulate_memory_utilization(service, region)
        memory_capacity = self._get_current_capacity(service, region, ResourceType.MEMORY)
        
        memory_metric = CapacityMetric(
            resource_type=ResourceType.MEMORY,
            current_utilization=memory_utilization,
            current_capacity=memory_capacity,
            timestamp=current_time,
            region=region,
            service=service,
            predicted_demand=self._predict_demand(ResourceType.MEMORY, service, region),
            recommendation=self._generate_scaling_recommendation(ResourceType.MEMORY, memory_utilization),
            confidence_score=0.80,
            cost_impact_inr=self._calculate_cost_impact(ResourceType.MEMORY, service, region)
        )
        metrics.append(memory_metric)
        
        # Storage Metrics (for data-heavy services)
        if service in ["database", "analytics", "logs"]:
            storage_utilization = self._simulate_storage_utilization(service, region)
            storage_capacity = self._get_current_capacity(service, region, ResourceType.STORAGE)
            
            storage_metric = CapacityMetric(
                resource_type=ResourceType.STORAGE,
                current_utilization=storage_utilization,
                current_capacity=storage_capacity,
                timestamp=current_time,
                region=region,
                service=service,
                predicted_demand=self._predict_demand(ResourceType.STORAGE, service, region),
                recommendation=self._generate_scaling_recommendation(ResourceType.STORAGE, storage_utilization),
                confidence_score=0.90,
                cost_impact_inr=self._calculate_cost_impact(ResourceType.STORAGE, service, region)
            )
            metrics.append(storage_metric)
        
        # Network Metrics
        network_utilization = self._simulate_network_utilization(service, region)
        network_capacity = self._get_current_capacity(service, region, ResourceType.NETWORK)
        
        network_metric = CapacityMetric(
            resource_type=ResourceType.NETWORK,
            current_utilization=network_utilization,
            current_capacity=network_capacity,
            timestamp=current_time,
            region=region,
            service=service,
            predicted_demand=self._predict_demand(ResourceType.NETWORK, service, region),
            recommendation=self._generate_scaling_recommendation(ResourceType.NETWORK, network_utilization),
            confidence_score=0.75,
            cost_impact_inr=self._calculate_cost_impact(ResourceType.NETWORK, service, region)
        )
        metrics.append(network_metric)
        
        # Store metrics for historical analysis
        for metric in metrics:
            key = f"{service}_{region}_{metric.resource_type.value}"
            self.historical_metrics[key].append(metric)
        
        return metrics
        
    def _simulate_cpu_utilization(self, service: str, region: str) -> float:
        """Simulate CPU utilization based on service and region"""
        
        base_utilization = {
            "web": 45.0,
            "mobile_api": 55.0,
            "database": 65.0,
            "cache": 35.0,
            "payments": 70.0,
            "analytics": 80.0
        }.get(service, 50.0)
        
        # Regional adjustments
        regional_multiplier = self.regional_patterns.get(region, {}).get("base_multiplier", 1.0)
        
        # Time-based variations (higher during peak hours)
        hour = datetime.now().hour
        if 9 <= hour <= 22:  # Peak hours
            time_multiplier = 1.3
        else:
            time_multiplier = 0.7
        
        # Add some randomness
        random_factor = random.uniform(0.8, 1.2)
        
        utilization = base_utilization * regional_multiplier * time_multiplier * random_factor
        return min(100.0, max(0.0, utilization))
        
    def _simulate_memory_utilization(self, service: str, region: str) -> float:
        """Simulate memory utilization"""
        
        base_utilization = {
            "web": 40.0,
            "mobile_api": 50.0,
            "database": 75.0,
            "cache": 85.0,      # Cache services use more memory
            "payments": 60.0,
            "analytics": 90.0   # Analytics services are memory-heavy
        }.get(service, 55.0)
        
        regional_multiplier = self.regional_patterns.get(region, {}).get("base_multiplier", 1.0)
        utilization = base_utilization * regional_multiplier * random.uniform(0.9, 1.1)
        return min(100.0, max(0.0, utilization))
        
    def _simulate_storage_utilization(self, service: str, region: str) -> float:
        """Simulate storage utilization"""
        
        base_utilization = {
            "database": 60.0,
            "analytics": 85.0,
            "logs": 70.0,
            "backup": 45.0
        }.get(service, 40.0)
        
        # Storage grows more predictably
        utilization = base_utilization * random.uniform(0.95, 1.05)
        return min(100.0, max(0.0, utilization))
        
    def _simulate_network_utilization(self, service: str, region: str) -> float:
        """Simulate network utilization"""
        
        base_utilization = {
            "web": 35.0,
            "mobile_api": 45.0,
            "cdn": 60.0,
            "streaming": 80.0,
            "payments": 25.0    # Payment APIs are lightweight
        }.get(service, 40.0)
        
        # Network utilization varies more with time
        hour = datetime.now().hour
        if 19 <= hour <= 22:  # Peak evening hours for streaming/entertainment
            time_multiplier = 1.8
        elif 9 <= hour <= 18:  # Business hours
            time_multiplier = 1.2
        else:
            time_multiplier = 0.6
        
        utilization = base_utilization * time_multiplier * random.uniform(0.7, 1.3)
        return min(100.0, max(0.0, utilization))
        
    def _get_current_capacity(self, service: str, region: str, resource_type: ResourceType) -> float:
        """Get current provisioned capacity"""
        
        # Simulate current capacity based on service type
        capacity_configs = {
            ResourceType.CPU: {"web": 100, "mobile_api": 80, "database": 64, "analytics": 128},
            ResourceType.MEMORY: {"web": 512, "mobile_api": 256, "database": 1024, "analytics": 2048},  # GB
            ResourceType.STORAGE: {"database": 2048, "analytics": 10240, "logs": 5120},  # GB
            ResourceType.NETWORK: {"web": 10, "cdn": 100, "streaming": 1000}  # Gbps
        }
        
        base_capacity = capacity_configs.get(resource_type, {}).get(service, 50)
        
        # Regional capacity variations
        regional_multiplier = self.regional_patterns.get(region, {}).get("base_multiplier", 1.0)
        
        return base_capacity * regional_multiplier
        
    def _predict_demand(self, resource_type: ResourceType, service: str, region: str, 
                       time_horizon_days: int = 30) -> float:
        """Predict future demand using simple models"""
        
        # Get historical data
        key = f"{service}_{region}_{resource_type.value}"
        historical_data = list(self.historical_metrics[key])
        
        if len(historical_data) < 10:  # Not enough data
            # Use growth-based prediction
            current_utilization = self._simulate_cpu_utilization(service, region)  # Simplified
            growth_rate = self.regional_patterns.get(region, {}).get("growth_rate_monthly", 10.0)
            
            # Apply growth over time horizon
            months = time_horizon_days / 30.0
            predicted_demand = current_utilization * (1 + (growth_rate / 100)) ** months
            
            return min(200.0, predicted_demand)  # Cap at 200% utilization
        
        # Use historical trend
        utilizations = [m.current_utilization for m in historical_data[-30:]]  # Last 30 points
        
        if len(utilizations) > 1:
            # Simple linear trend
            x = np.arange(len(utilizations))
            coefficients = np.polyfit(x, utilizations, 1)
            
            # Predict future point
            future_point = len(utilizations) + time_horizon_days
            predicted = np.polyval(coefficients, future_point)
            
            return max(0.0, min(200.0, predicted))
        
        return utilizations[-1] if utilizations else 50.0  # Fallback
        
    def _generate_scaling_recommendation(self, resource_type: ResourceType, 
                                       current_utilization: float) -> str:
        """Generate scaling recommendation based on utilization"""
        
        thresholds = self.planning_config["utilization_thresholds"][resource_type.value]
        
        if current_utilization >= thresholds["critical"]:
            return f"IMMEDIATE SCALE UP: {resource_type.value} at {current_utilization:.1f}% (critical threshold: {thresholds['critical']}%)"
            
        elif current_utilization >= thresholds["warning"]:
            return f"PLAN SCALE UP: {resource_type.value} at {current_utilization:.1f}% (warning threshold: {thresholds['warning']}%)"
            
        elif current_utilization < 40:  # Scale down threshold
            return f"CONSIDER SCALE DOWN: {resource_type.value} at {current_utilization:.1f}% (under-utilized)"
            
        else:
            return f"OPTIMAL: {resource_type.value} at {current_utilization:.1f}% (within safe range)"
            
    def _calculate_cost_impact(self, resource_type: ResourceType, service: str, region: str) -> float:
        """Calculate cost impact of scaling decisions"""
        
        # Use AWS costs as baseline
        cost_model = self.cost_models["aws"]
        
        base_cost_per_hour = {
            ResourceType.CPU: 8.5,      # ₹8.5 per vCPU hour
            ResourceType.MEMORY: 1.2,   # ₹1.2 per GB hour
            ResourceType.STORAGE: 2.3 / (24 * 30),  # Convert monthly to hourly
            ResourceType.NETWORK: 0.5,  # ₹0.5 per GB
        }.get(resource_type, 5.0)
        
        current_capacity = self._get_current_capacity(service, region, resource_type)
        regional_multiplier = self.regional_patterns.get(region, {}).get("infrastructure_cost_multiplier", 1.0)
        
        # Monthly cost for current capacity
        monthly_cost = base_cost_per_hour * current_capacity * 24 * 30 * regional_multiplier
        
        return monthly_cost
        
    def generate_festival_capacity_forecast(self, event_name: str, services: List[str]) -> Dict[str, Any]:
        """Generate capacity forecast for Indian festival/event"""
        
        if event_name not in self.indian_events_calendar:
            self.logger.warning(f"Unknown event: {event_name}")
            return {}
        
        event_config = self.indian_events_calendar[event_name]
        forecasts = {}
        
        for service in services:
            service_forecasts = {}
            
            for resource_type in ResourceType:
                # Skip irrelevant resources for service
                if resource_type == ResourceType.STORAGE and service not in ["database", "analytics", "logs"]:
                    continue
                
                forecast = self._generate_event_forecast(service, resource_type, event_config)
                service_forecasts[resource_type.value] = forecast
            
            forecasts[service] = service_forecasts
        
        # Generate overall recommendations
        overall_recommendations = self._generate_festival_recommendations(event_name, forecasts)
        
        return {
            "event_name": event_name,
            "event_config": event_config,
            "service_forecasts": forecasts,
            "overall_recommendations": overall_recommendations,
            "total_estimated_cost_inr": self._calculate_total_event_cost(forecasts),
            "implementation_timeline": self._generate_implementation_timeline(event_config),
            "risk_assessment": self._assess_festival_risks(event_config, forecasts)
        }
        
    def _generate_event_forecast(self, service: str, resource_type: ResourceType, 
                               event_config: Dict) -> CapacityForecast:
        """Generate forecast for specific service and resource during event"""
        
        # Get current baseline
        current_utilization = getattr(self, f"_simulate_{resource_type.value}_utilization")(service, "mumbai")
        current_capacity = self._get_current_capacity(service, "mumbai", resource_type)
        
        # Apply event multiplier
        traffic_multiplier = event_config["traffic_multiplier"]
        
        # Different resources scale differently
        resource_scaling_factor = {
            ResourceType.CPU: 0.8,          # CPU scales sub-linearly
            ResourceType.MEMORY: 0.6,       # Memory scales less
            ResourceType.STORAGE: 0.1,      # Storage barely scales with traffic
            ResourceType.NETWORK: 1.0,      # Network scales linearly
        }.get(resource_type, 0.8)
        
        expected_multiplier = 1 + (traffic_multiplier - 1) * resource_scaling_factor
        peak_demand = current_utilization * expected_multiplier
        
        # Recommended capacity with safety buffer
        safety_buffer = 1.3  # 30% safety buffer
        recommended_capacity = (peak_demand / 100) * current_capacity * safety_buffer
        
        # Determine scaling strategy
        scale_up_factor = recommended_capacity / current_capacity
        
        if scale_up_factor > 2.0:
            scaling_strategy = ScalingStrategy.HYBRID  # Both horizontal and vertical
        elif scale_up_factor > 1.5:
            scaling_strategy = ScalingStrategy.HORIZONTAL  # Add more instances
        elif scale_up_factor > 1.2:
            scaling_strategy = ScalingStrategy.VERTICAL  # Upgrade instances
        else:
            scaling_strategy = ScalingStrategy.HORIZONTAL  # Small scale-up
        
        # Cost calculation
        base_cost = self._calculate_cost_impact(resource_type, service, "mumbai")
        estimated_cost = base_cost * scale_up_factor * (event_config["duration_days"] / 30)
        
        return CapacityForecast(
            resource_type=resource_type,
            time_horizon="event_duration",
            base_demand=current_utilization,
            peak_demand=peak_demand,
            growth_rate=0.0,  # Event-driven, not growth
            seasonal_multiplier=1.0,
            event_multiplier=expected_multiplier,
            recommended_capacity=recommended_capacity,
            scaling_strategy=scaling_strategy,
            implementation_timeline=f"{14 - event_config['duration_days']} days before event",
            estimated_cost_inr=estimated_cost
        )
        
    def _generate_festival_recommendations(self, event_name: str, forecasts: Dict) -> List[str]:
        """Generate actionable recommendations for festival preparation"""
        
        recommendations = []
        
        # High-level event preparation
        if "big_billion_days" in event_name.lower():
            recommendations.append(
                "Pre-provision 3x web servers and 2x payment processing capacity 1 week before BBD. "
                "Setup auto-scaling triggers at 60% utilization instead of 80%."
            )
            
        elif "diwali" in event_name.lower():
            recommendations.append(
                "Focus on payment infrastructure scaling. Expected 8x payment volume. "
                "Coordinate with payment partners for capacity alignment."
            )
            
        elif "new_year" in event_name.lower():
            recommendations.append(
                "Massive food delivery spike expected. Scale delivery tracking and notification systems. "
                "Prepare for 15x traffic at midnight."
            )
        
        # Resource-specific recommendations
        total_cpu_scaling_needed = 0
        total_memory_scaling_needed = 0
        
        for service, service_forecasts in forecasts.items():
            cpu_forecast = service_forecasts.get("cpu")
            memory_forecast = service_forecasts.get("memory")
            
            if cpu_forecast and cpu_forecast.recommended_capacity > cpu_forecast.base_demand * 1.5:
                total_cpu_scaling_needed += 1
                recommendations.append(
                    f"Scale {service} CPU capacity by {((cpu_forecast.recommended_capacity / cpu_forecast.base_demand) - 1) * 100:.0f}% "
                    f"using {cpu_forecast.scaling_strategy.value} strategy"
                )
                
            if memory_forecast and memory_forecast.recommended_capacity > memory_forecast.base_demand * 1.5:
                total_memory_scaling_needed += 1
        
        # Multi-cloud recommendations for large events
        if total_cpu_scaling_needed >= 3:
            recommendations.append(
                "Consider multi-cloud deployment. Use AWS for primary traffic, "
                "Azure/GCP for overflow. Setup traffic routing automation."
            )
        
        # Cost optimization recommendations
        recommendations.append(
            "Use spot instances for non-critical batch jobs during event. "
            "Can save 60-70% on compute costs for analytics and reporting workloads."
        )
        
        return recommendations
        
    def _calculate_total_event_cost(self, forecasts: Dict) -> float:
        """Calculate total estimated cost for event"""
        
        total_cost = 0.0
        
        for service, service_forecasts in forecasts.items():
            for resource_type, forecast in service_forecasts.items():
                if hasattr(forecast, 'estimated_cost_inr'):
                    total_cost += forecast.estimated_cost_inr
        
        return total_cost
        
    def _generate_implementation_timeline(self, event_config: Dict) -> List[Dict[str, str]]:
        """Generate implementation timeline for event preparation"""
        
        event_date = datetime.strptime(event_config["start_date"], "%Y-%m-%d")
        duration = event_config["duration_days"]
        
        timeline = [
            {
                "milestone": "Capacity Planning Complete",
                "deadline": (event_date - timedelta(days=21)).strftime("%Y-%m-%d"),
                "description": "Finalize capacity requirements and scaling strategy"
            },
            {
                "milestone": "Infrastructure Procurement",
                "deadline": (event_date - timedelta(days=14)).strftime("%Y-%m-%d"),
                "description": "Procure additional cloud resources, setup accounts"
            },
            {
                "milestone": "Deployment and Configuration",
                "deadline": (event_date - timedelta(days=7)).strftime("%Y-%m-%d"),
                "description": "Deploy scaled infrastructure, configure auto-scaling"
            },
            {
                "milestone": "Load Testing",
                "deadline": (event_date - timedelta(days=3)).strftime("%Y-%m-%d"),
                "description": "Conduct load tests at expected peak traffic"
            },
            {
                "milestone": "Go-Live Readiness",
                "deadline": (event_date - timedelta(days=1)).strftime("%Y-%m-%d"),
                "description": "Final checks, team briefing, monitoring setup"
            },
            {
                "milestone": "Scale-Down Planning",
                "deadline": (event_date + timedelta(days=duration + 2)).strftime("%Y-%m-%d"),
                "description": "Scale down resources, cost optimization"
            }
        ]
        
        return timeline
        
    def _assess_festival_risks(self, event_config: Dict, forecasts: Dict) -> Dict[str, Any]:
        """Assess risks for festival capacity planning"""
        
        risks = {
            "high_risk_factors": [],
            "medium_risk_factors": [],
            "mitigation_strategies": [],
            "contingency_plans": []
        }
        
        traffic_multiplier = event_config["traffic_multiplier"]
        
        # High traffic multiplier risks
        if traffic_multiplier > 10:
            risks["high_risk_factors"].append(
                f"Extreme traffic spike ({traffic_multiplier}x) may overwhelm downstream dependencies"
            )
            risks["mitigation_strategies"].append(
                "Setup circuit breakers and graceful degradation for non-critical features"
            )
        
        # Multi-service scaling risks
        services_needing_scaling = len([s for s in forecasts.keys()])
        if services_needing_scaling > 5:
            risks["medium_risk_factors"].append(
                f"{services_needing_scaling} services need scaling - coordination complexity high"
            )
            risks["mitigation_strategies"].append(
                "Implement phased scaling approach, monitor service dependencies"
            )
        
        # Cost risks
        total_cost = self._calculate_total_event_cost(forecasts)
        monthly_budget = self.planning_config["business_constraints"]["budget_limit_monthly_inr"]
        
        if total_cost > monthly_budget * 0.5:  # More than 50% of monthly budget
            risks["high_risk_factors"].append(
                f"Event cost (₹{total_cost:,.0f}) exceeds 50% of monthly budget"
            )
            risks["contingency_plans"].append(
                "Prepare scale-down procedures if ROI targets not met within first 24 hours"
            )
        
        return risks
        
    def get_capacity_planning_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive capacity planning dashboard data"""
        
        dashboard_data = {
            "service_name": self.service_name,
            "region": self.region,
            "last_updated": datetime.now().isoformat(),
            "current_capacity_status": self._get_current_capacity_status(),
            "upcoming_events": self._get_upcoming_events(),
            "scaling_recommendations": self._get_immediate_scaling_recommendations(),
            "cost_projections": self._get_cost_projections(),
            "resource_utilization_trends": self._get_utilization_trends(),
            "regional_capacity_breakdown": self._get_regional_breakdown(),
            "auto_scaling_status": self._get_auto_scaling_status(),
            "budget_tracking": self._get_budget_tracking(),
            "capacity_alerts": self._get_capacity_alerts()
        }
        
        return dashboard_data
        
    def _get_current_capacity_status(self) -> Dict[str, Any]:
        """Get current capacity status across all resources"""
        
        services = ["web", "mobile_api", "database", "payments"]
        regions = ["mumbai", "bangalore", "delhi"]
        
        status_summary = {
            "services_monitored": len(services),
            "regions_monitored": len(regions),
            "resources_at_capacity": 0,
            "resources_under_utilized": 0,
            "overall_health": "healthy"
        }
        
        resource_details = {}
        
        for service in services:
            for region in regions:
                metrics = self.collect_capacity_metrics(service, region)
                
                for metric in metrics:
                    key = f"{service}_{region}_{metric.resource_type.value}"
                    resource_details[key] = {
                        "utilization": metric.current_utilization,
                        "capacity": metric.current_capacity,
                        "recommendation": metric.recommendation,
                        "cost_impact": metric.cost_impact_inr
                    }
                    
                    # Count resources at capacity
                    if metric.current_utilization > 85:
                        status_summary["resources_at_capacity"] += 1
                    elif metric.current_utilization < 40:
                        status_summary["resources_under_utilized"] += 1
        
        # Determine overall health
        if status_summary["resources_at_capacity"] > 5:
            status_summary["overall_health"] = "critical"
        elif status_summary["resources_at_capacity"] > 2:
            status_summary["overall_health"] = "warning"
        
        return {
            "summary": status_summary,
            "resource_details": resource_details
        }
        
    def _get_upcoming_events(self) -> List[Dict[str, Any]]:
        """Get upcoming Indian business events"""
        
        current_date = datetime.now()
        upcoming_events = []
        
        for event_name, event_config in self.indian_events_calendar.items():
            if "recurring" not in event_config:
                event_date = datetime.strptime(event_config["start_date"], "%Y-%m-%d")
                days_until = (event_date - current_date).days
                
                if 0 <= days_until <= 90:  # Next 3 months
                    upcoming_events.append({
                        "event_name": event_name,
                        "event_type": event_config["event_type"].value,
                        "start_date": event_config["start_date"],
                        "days_until": days_until,
                        "traffic_multiplier": event_config["traffic_multiplier"],
                        "preparation_status": "not_started" if days_until > 21 else "in_progress" if days_until > 7 else "final_prep"
                    })
        
        # Sort by days until event
        upcoming_events.sort(key=lambda x: x["days_until"])
        
        return upcoming_events
        
    def _get_immediate_scaling_recommendations(self) -> List[Dict[str, Any]]:
        """Get immediate scaling recommendations"""
        
        recommendations = []
        
        # Check recent metrics for immediate needs
        services = ["web", "mobile_api", "database", "payments"]
        regions = ["mumbai", "bangalore"]
        
        for service in services:
            for region in regions:
                metrics = self.collect_capacity_metrics(service, region)
                
                for metric in metrics:
                    if metric.current_utilization > 85:  # High utilization
                        recommendations.append({
                            "priority": "high",
                            "service": service,
                            "region": region,
                            "resource_type": metric.resource_type.value,
                            "current_utilization": metric.current_utilization,
                            "recommendation": metric.recommendation,
                            "estimated_cost_inr": metric.cost_impact_inr * 0.3,  # 30% increase
                            "timeline": "immediate"
                        })
        
        # Sort by priority and utilization
        recommendations.sort(key=lambda x: x["current_utilization"], reverse=True)
        
        return recommendations[:10]  # Top 10 recommendations
        
    def _get_cost_projections(self) -> Dict[str, Any]:
        """Get cost projections for different time horizons"""
        
        current_monthly_cost = 0
        
        # Calculate current cost across all services and regions
        services = ["web", "mobile_api", "database", "payments"]
        regions = ["mumbai", "bangalore", "delhi"]
        
        for service in services:
            for region in regions:
                for resource_type in ResourceType:
                    if resource_type == ResourceType.STORAGE and service not in ["database"]:
                        continue
                    cost = self._calculate_cost_impact(resource_type, service, region)
                    current_monthly_cost += cost
        
        return {
            "current_monthly_inr": current_monthly_cost,
            "projected_1_month_inr": current_monthly_cost * 1.1,    # 10% growth
            "projected_3_months_inr": current_monthly_cost * 1.35,  # 35% growth over 3 months
            "projected_1_year_inr": current_monthly_cost * 2.5,     # 150% growth over 1 year
            "festival_season_spike_inr": current_monthly_cost * 3.0, # 3x during festivals
            "budget_limit_inr": self.planning_config["business_constraints"]["budget_limit_monthly_inr"],
            "optimization_potential_inr": current_monthly_cost * 0.25  # 25% optimization potential
        }
        
    def _get_utilization_trends(self) -> Dict[str, List[float]]:
        """Get resource utilization trends"""
        
        trends = {}
        
        # Generate sample trend data (in production, use real historical data)
        for resource_type in ResourceType:
            # Generate 30 days of trend data
            base_utilization = random.uniform(40, 70)
            trend_data = []
            
            for day in range(30):
                # Add growth trend
                growth_factor = 1 + (day * 0.01)  # 1% daily growth
                
                # Add daily variations
                daily_variation = random.uniform(0.9, 1.1)
                
                utilization = base_utilization * growth_factor * daily_variation
                trend_data.append(min(100, max(0, utilization)))
            
            trends[resource_type.value] = trend_data
        
        return trends
        
    def _get_regional_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Get capacity breakdown by region"""
        
        regional_data = {}
        regions = ["mumbai", "bangalore", "delhi", "tier2_cities"]
        
        for region in regions:
            regional_data[region] = {
                "total_services": 4,  # web, api, db, payments
                "avg_cpu_utilization": random.uniform(50, 80),
                "avg_memory_utilization": random.uniform(45, 75),
                "monthly_cost_inr": random.uniform(500000, 2000000),  # ₹5L to ₹20L
                "growth_rate": self.regional_patterns.get(region, {}).get("growth_rate_monthly", 10),
                "scaling_needed": random.choice([True, False]),
                "cost_optimization_potential": random.uniform(15, 30)  # 15-30% savings possible
            }
        
        return regional_data
        
    def _get_auto_scaling_status(self) -> Dict[str, Any]:
        """Get auto-scaling status and configuration"""
        
        return {
            "enabled_services": ["web", "mobile_api"],
            "disabled_services": ["database", "cache"],
            "scaling_policies": {
                "scale_up_threshold": 80,
                "scale_down_threshold": 40,
                "cooldown_period_minutes": 15,
                "max_instances": 50,
                "min_instances": 5
            },
            "recent_scaling_events": [
                {"timestamp": "2024-01-15 14:30", "action": "scale_up", "service": "web", "instances": "10->15"},
                {"timestamp": "2024-01-15 11:20", "action": "scale_down", "service": "mobile_api", "instances": "8->6"}
            ],
            "scaling_effectiveness": 85.0  # 85% of scaling events were successful
        }
        
    def _get_budget_tracking(self) -> Dict[str, Any]:
        """Get budget tracking information"""
        
        monthly_budget = self.planning_config["business_constraints"]["budget_limit_monthly_inr"]
        current_spend = random.uniform(0.4, 0.8) * monthly_budget  # 40-80% of budget used
        
        return {
            "monthly_budget_inr": monthly_budget,
            "current_spend_inr": current_spend,
            "budget_utilization_percentage": (current_spend / monthly_budget) * 100,
            "projected_month_end_spend_inr": current_spend * 1.3,  # Projected
            "variance_from_budget": current_spend - (monthly_budget * 0.75),  # Target 75% utilization
            "cost_centers": {
                "compute": current_spend * 0.4,
                "storage": current_spend * 0.2,
                "network": current_spend * 0.15,
                "database": current_spend * 0.2,
                "monitoring": current_spend * 0.05
            }
        }
        
    def _get_capacity_alerts(self) -> List[Dict[str, Any]]:
        """Get current capacity-related alerts"""
        
        alerts = []
        
        # Simulate some alerts
        alert_scenarios = [
            {
                "severity": "high",
                "resource": "database_cpu",
                "message": "Database CPU utilization above 85% for 15 minutes",
                "service": "payments",
                "region": "mumbai",
                "recommendation": "Scale up database instance or optimize queries"
            },
            {
                "severity": "medium", 
                "resource": "storage",
                "message": "Storage utilization growing at 2GB/day, will reach capacity in 30 days",
                "service": "analytics",
                "region": "bangalore",
                "recommendation": "Plan storage expansion or implement data archival"
            },
            {
                "severity": "low",
                "resource": "network",
                "message": "Network utilization consistently below 30%",
                "service": "web",
                "region": "delhi",
                "recommendation": "Consider downgrading network tier to save costs"
            }
        ]
        
        for i, scenario in enumerate(alert_scenarios):
            alerts.append({
                "alert_id": f"CAP_{i+1:03d}",
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(5, 120))).isoformat(),
                **scenario
            })
        
        return alerts

# Test and simulation functions
async def simulate_big_billion_days_capacity_planning():
    """Simulate BBD capacity planning scenario"""
    print("🛒 Simulating Big Billion Days capacity planning...")
    
    capacity_planner = IndianCapacityPlanningSystem("flipkart-bbd", "india")
    
    # Services that need scaling for BBD
    bbd_services = ["web", "mobile_api", "payments", "database", "analytics"]
    
    print(f"📊 Planning capacity for {len(bbd_services)} services...")
    
    # Generate festival forecast
    festival_forecast = capacity_planner.generate_festival_capacity_forecast("big_billion_days_2024", bbd_services)
    
    print(f"\n🎯 Big Billion Days 2024 Capacity Forecast:")
    print(f"Event Duration: {festival_forecast['event_config']['duration_days']} days")
    print(f"Traffic Multiplier: {festival_forecast['event_config']['traffic_multiplier']}x")
    print(f"Total Estimated Cost: ₹{festival_forecast['total_estimated_cost_inr']:,.0f}")
    
    print(f"\n📈 Service-wise Scaling Requirements:")
    for service, forecasts in festival_forecast['service_forecasts'].items():
        print(f"\n{service.upper()}:")
        for resource_type, forecast in forecasts.items():
            scale_factor = forecast.recommended_capacity / forecast.base_demand if forecast.base_demand > 0 else 1
            print(f"  {resource_type}: {scale_factor:.1f}x scaling ({forecast.scaling_strategy.value})")
    
    print(f"\n💡 Key Recommendations:")
    for i, rec in enumerate(festival_forecast['overall_recommendations'][:5], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n📅 Implementation Timeline:")
    for milestone in festival_forecast['implementation_timeline'][:3]:
        print(f"  {milestone['deadline']}: {milestone['milestone']}")
    
    return capacity_planner, festival_forecast

def test_regional_capacity_variations():
    """Test capacity planning across different Indian regions"""
    print("\n🗺️ Testing regional capacity variations...")
    
    capacity_planner = IndianCapacityPlanningSystem("zomato-delivery")
    
    regions = ["mumbai", "bangalore", "delhi", "tier2_cities", "tier3_cities"]
    
    print("\n📊 Regional Capacity Analysis:")
    for region in regions:
        print(f"\n{region.replace('_', ' ').title()}:")
        
        # Collect metrics for web service in this region
        metrics = capacity_planner.collect_capacity_metrics("web", region)
        
        for metric in metrics:
            print(f"  {metric.resource_type.value}: {metric.current_utilization:.1f}% utilization")
            print(f"    Prediction: {metric.predicted_demand:.1f}% demand")
            print(f"    Cost Impact: ₹{metric.cost_impact_inr:,.0f}/month")

def test_capacity_dashboard_generation():
    """Test capacity planning dashboard data generation"""
    print("\n📋 Testing capacity dashboard generation...")
    
    capacity_planner = IndianCapacityPlanningSystem("paytm-gateway")
    
    # Generate dashboard data
    dashboard_data = capacity_planner.get_capacity_planning_dashboard_data()
    
    print(f"\n📊 Dashboard Summary:")
    current_status = dashboard_data['current_capacity_status']['summary']
    print(f"Services Monitored: {current_status['services_monitored']}")
    print(f"Overall Health: {current_status['overall_health'].upper()}")
    print(f"Resources at Capacity: {current_status['resources_at_capacity']}")
    
    print(f"\n💰 Cost Projections:")
    cost_proj = dashboard_data['cost_projections']
    print(f"Current Monthly: ₹{cost_proj['current_monthly_inr']:,.0f}")
    print(f"Festival Spike: ₹{cost_proj['festival_season_spike_inr']:,.0f}")
    print(f"Optimization Potential: ₹{cost_proj['optimization_potential_inr']:,.0f}")
    
    print(f"\n🔮 Upcoming Events:")
    for event in dashboard_data['upcoming_events'][:3]:
        print(f"  {event['event_name']}: {event['days_until']} days ({event['traffic_multiplier']}x traffic)")

async def test_tatkal_booking_capacity_scenario():
    """Test IRCTC Tatkal booking capacity scenario"""
    print("\n🚂 Testing IRCTC Tatkal booking capacity scenario...")
    
    capacity_planner = IndianCapacityPlanningSystem("irctc-tatkal")
    
    # Simulate Tatkal booking spike (daily at 10 AM)
    print("⏰ Simulating 10 AM Tatkal booking rush...")
    
    # Collect metrics during normal time
    print("📊 Normal capacity (9:59 AM):")
    normal_metrics = capacity_planner.collect_capacity_metrics("irctc_booking", "all_india")
    for metric in normal_metrics[:2]:  # Show first 2 metrics
        print(f"  {metric.resource_type.value}: {metric.current_utilization:.1f}%")
    
    # Simulate the 50x spike at 10 AM
    print("\n🔥 Tatkal booking spike (10:00 AM - 50x traffic!):")
    
    # In reality, you'd see metrics spike, here we simulate the recommendation
    tatkal_event = capacity_planner.indian_events_calendar["tatkal_booking_daily"]
    print(f"Traffic Multiplier: {tatkal_event['traffic_multiplier']}x")
    print(f"Duration: {tatkal_event['duration_minutes']} minutes")
    
    print("\n💡 Tatkal Capacity Strategy:")
    print("  - Pre-scale servers 5 minutes before 10 AM")
    print("  - Use queue-based load balancing")
    print("  - Implement user rate limiting")
    print("  - Auto-scale down after 30 minutes")

if __name__ == "__main__":
    print("🚀 Episode 16: Capacity Planning Metrics for Indian Scale")
    print("🇮🇳 BBD se Tatkal tak, sab ka capacity plan karte hain!")
    print("=" * 60)
    
    # Run comprehensive testing
    asyncio.run(simulate_big_billion_days_capacity_planning())
    test_regional_capacity_variations()
    test_capacity_dashboard_generation()
    asyncio.run(test_tatkal_booking_capacity_scenario())
    
    print("\n" + "=" * 60)
    print("✅ Capacity planning testing completed!")
    print("📊 Key Insights:")
    print("  - Festival events require 3-12x capacity scaling")
    print("  - Regional variations can be 2x between metro and tier-3")
    print("  - Cost optimization can save 25-30% monthly spend")
    print("  - Auto-scaling policies need event-aware configurations")
    print("🔍 Next: Implement capacity planning automation and alerts")
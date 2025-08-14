#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 9: APM (Application Performance Monitoring) for Indian Apps

भारतीय context: Swiggy app की तरह real-time performance tracking
जैसे order placement se delivery tracking tak का complete APM

Real-world scenario: Zomato app performance during dinner rush (7-9 PM)
Challenge: Mobile network variations, device diversity, regional performance
"""

import time
import json
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import structlog
from contextlib import asynccontextmanager

# भारतीय mobile app performance categories
class PerformanceCategory(Enum):
    """Performance categories for Indian mobile apps"""
    APP_LAUNCH = "app_launch"                    # App startup time
    SCREEN_LOAD = "screen_load"                  # Screen rendering time
    API_RESPONSE = "api_response"                # Backend API latency
    DATABASE_QUERY = "database_query"            # DB performance
    NETWORK_REQUEST = "network_request"          # Network operations
    USER_INTERACTION = "user_interaction"        # Tap to response time
    PAYMENT_FLOW = "payment_flow"               # Payment process time
    LOCATION_SERVICE = "location_service"        # GPS and location services
    IMAGE_LOAD = "image_load"                   # Image loading performance
    SEARCH_OPERATION = "search_operation"        # Search functionality

class DeviceCategory(Enum):
    """Indian smartphone categories"""
    FLAGSHIP = "flagship"        # OnePlus, Samsung Galaxy S series
    PREMIUM = "premium"          # iPhone, Pixel, Samsung A series  
    MID_RANGE = "mid_range"      # Redmi Note, Realme, Vivo
    BUDGET = "budget"            # Entry level smartphones
    FEATURE_PHONE = "feature_phone"  # JioPhone, basic phones

class NetworkType(Enum):
    """Indian network types"""
    WIFI = "wifi"
    FOUR_G = "4g"
    THREE_G = "3g"
    TWO_G = "2g"
    JIO_FIBER = "jio_fiber"
    BSNL_BROADBAND = "bsnl_broadband"

@dataclass
class PerformanceMetric:
    """Performance metric definition for Indian apps"""
    name: str
    category: PerformanceCategory
    value: float
    unit: str
    timestamp: datetime
    user_id: str
    session_id: str
    device_info: Dict[str, Any]
    network_info: Dict[str, Any]
    location_info: Dict[str, Any]
    app_version: str
    additional_context: Dict[str, Any] = field(default_factory=dict)

class IndianAPMMonitor:
    """
    Indian Mobile App Performance Monitor
    
    Features:
    - Device-specific performance tracking
    - Network condition impact analysis
    - Regional performance variations
    - Business transaction monitoring
    - Real user monitoring (RUM)
    - Synthetic monitoring integration
    """
    
    def __init__(self, app_name: str, version: str = "1.0.0"):
        self.app_name = app_name
        self.app_version = version
        self.session_data = {}
        
        # Performance data storage
        self.performance_data = defaultdict(lambda: deque(maxlen=10000))
        self.user_sessions = {}
        
        # Indian-specific configurations
        self.indian_config = self._initialize_indian_config()
        self.device_profiles = self._initialize_device_profiles()
        self.network_profiles = self._initialize_network_profiles()
        
        # Business transaction definitions
        self.business_transactions = self._define_business_transactions()
        
        # Logger
        self.logger = structlog.get_logger("indian-apm-monitor")
        
    def _initialize_indian_config(self) -> Dict[str, Any]:
        """Initialize Indian market specific configurations"""
        
        return {
            "peak_hours": {
                "breakfast": {"start": "08:00", "end": "10:00"},
                "lunch": {"start": "12:00", "end": "14:00"}, 
                "dinner": {"start": "19:00", "end": "22:00"},
                "late_night": {"start": "23:00", "end": "01:00"}
            },
            
            "regional_characteristics": {
                "mumbai": {
                    "avg_network_speed_mbps": 25.0,
                    "device_mix": {"flagship": 15, "premium": 25, "mid_range": 45, "budget": 15},
                    "peak_usage_multiplier": 2.5
                },
                "bangalore": {
                    "avg_network_speed_mbps": 35.0,
                    "device_mix": {"flagship": 20, "premium": 30, "mid_range": 40, "budget": 10},
                    "peak_usage_multiplier": 2.2
                },
                "delhi": {
                    "avg_network_speed_mbps": 20.0, 
                    "device_mix": {"flagship": 12, "premium": 23, "mid_range": 50, "budget": 15},
                    "peak_usage_multiplier": 2.8
                },
                "tier2_cities": {
                    "avg_network_speed_mbps": 15.0,
                    "device_mix": {"flagship": 5, "premium": 15, "mid_range": 60, "budget": 20},
                    "peak_usage_multiplier": 2.0
                },
                "tier3_cities": {
                    "avg_network_speed_mbps": 8.0,
                    "device_mix": {"flagship": 2, "premium": 8, "mid_range": 50, "budget": 40},
                    "peak_usage_multiplier": 1.5
                }
            },
            
            "performance_budgets": {
                "app_launch_ms": {"target": 3000, "max": 8000},
                "screen_load_ms": {"target": 1500, "max": 5000},
                "api_response_ms": {"target": 200, "max": 1000},
                "payment_flow_ms": {"target": 5000, "max": 15000},
                "search_ms": {"target": 500, "max": 2000}
            },
            
            "business_impact_thresholds": {
                "app_launch_abandonment_ms": 10000,  # Users abandon after 10s
                "checkout_abandonment_ms": 30000,    # Checkout timeout
                "search_abandonment_ms": 5000        # Search timeout
            }
        }
        
    def _initialize_device_profiles(self) -> Dict[str, Dict]:
        """Initialize device performance profiles for Indian market"""
        
        return {
            DeviceCategory.FLAGSHIP.value: {
                "cpu_performance_multiplier": 1.0,
                "memory_gb": 8,
                "storage_type": "ufs_3.0",
                "expected_app_launch_ms": 2000,
                "expected_screen_load_ms": 800,
                "market_share_percent": 12,
                "example_devices": ["OnePlus 11", "Samsung S23", "iPhone 14"]
            },
            
            DeviceCategory.PREMIUM.value: {
                "cpu_performance_multiplier": 0.85,
                "memory_gb": 6,
                "storage_type": "ufs_2.1",
                "expected_app_launch_ms": 2500,
                "expected_screen_load_ms": 1000,
                "market_share_percent": 25,
                "example_devices": ["Pixel 7a", "Samsung A54", "iPhone 12"]
            },
            
            DeviceCategory.MID_RANGE.value: {
                "cpu_performance_multiplier": 0.6,
                "memory_gb": 4,
                "storage_type": "emmc_5.1",
                "expected_app_launch_ms": 4000,
                "expected_screen_load_ms": 1500,
                "market_share_percent": 45,
                "example_devices": ["Redmi Note 12", "Realme 10", "Vivo V27"]
            },
            
            DeviceCategory.BUDGET.value: {
                "cpu_performance_multiplier": 0.35,
                "memory_gb": 3,
                "storage_type": "emmc_5.1",
                "expected_app_launch_ms": 6000,
                "expected_screen_load_ms": 2500,
                "market_share_percent": 18,
                "example_devices": ["Redmi A2", "Realme C55", "Samsung M13"]
            }
        }
        
    def _initialize_network_profiles(self) -> Dict[str, Dict]:
        """Initialize network performance profiles"""
        
        return {
            NetworkType.WIFI.value: {
                "avg_speed_mbps": 25.0,
                "latency_ms": 20,
                "reliability_percent": 95,
                "usage_percent": 40
            },
            
            NetworkType.FOUR_G.value: {
                "avg_speed_mbps": 12.0,
                "latency_ms": 50,
                "reliability_percent": 85,
                "usage_percent": 50
            },
            
            NetworkType.THREE_G.value: {
                "avg_speed_mbps": 2.0,
                "latency_ms": 200,
                "reliability_percent": 70,
                "usage_percent": 8
            },
            
            NetworkType.JIO_FIBER.value: {
                "avg_speed_mbps": 100.0,
                "latency_ms": 10,
                "reliability_percent": 98,
                "usage_percent": 15
            }
        }
        
    def _define_business_transactions(self) -> Dict[str, Dict]:
        """Define critical business transactions for monitoring"""
        
        return {
            "user_onboarding": {
                "steps": ["app_launch", "splash_screen", "login_screen", "otp_verification", "home_screen"],
                "max_duration_ms": 15000,
                "business_impact": "critical",
                "conversion_impact": "high"
            },
            
            "food_ordering": {
                "steps": ["restaurant_search", "menu_load", "add_to_cart", "checkout_init", "payment", "order_confirmation"],
                "max_duration_ms": 45000,
                "business_impact": "critical",
                "conversion_impact": "high"
            },
            
            "ride_booking": {
                "steps": ["location_detect", "ride_options_load", "ride_select", "driver_matching", "ride_confirmation"],
                "max_duration_ms": 30000,
                "business_impact": "critical",
                "conversion_impact": "high"
            },
            
            "payment_flow": {
                "steps": ["payment_method_select", "amount_entry", "authentication", "processing", "confirmation"],
                "max_duration_ms": 20000,
                "business_impact": "critical",
                "conversion_impact": "very_high"
            },
            
            "product_search": {
                "steps": ["search_query", "results_load", "filters_apply", "product_details"],
                "max_duration_ms": 10000,
                "business_impact": "high",
                "conversion_impact": "medium"
            }
        }
        
    def start_user_session(self, user_id: str, device_info: Dict, location: str) -> str:
        """Start a new user session for performance tracking"""
        
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "start_time": datetime.now(),
            "device_info": device_info,
            "location": location,
            "network_type": self._detect_network_type(),
            "app_version": self.app_version,
            "performance_metrics": [],
            "business_transactions": {},
            "user_interactions": []
        }
        
        self.user_sessions[session_id] = session_data
        
        self.logger.info(
            "user_session_started",
            session_id=session_id,
            user_id=user_id,
            device_category=device_info.get("category"),
            location=location
        )
        
        return session_id
        
    def _detect_network_type(self) -> str:
        """Detect current network type (simulated)"""
        
        # Simulate network type distribution in India
        network_distribution = {
            "wifi": 0.4,
            "4g": 0.5,
            "3g": 0.08,
            "jio_fiber": 0.02
        }
        
        rand = random.random()
        cumulative = 0
        
        for network, probability in network_distribution.items():
            cumulative += probability
            if rand <= cumulative:
                return network
                
        return "4g"  # Default
        
    def record_performance_metric(self, session_id: str, category: PerformanceCategory, 
                                 operation_name: str, duration_ms: float, 
                                 additional_context: Dict = None) -> PerformanceMetric:
        """Record a performance metric for analysis"""
        
        if session_id not in self.user_sessions:
            self.logger.warning(f"Session not found: {session_id}")
            return None
            
        session = self.user_sessions[session_id]
        
        metric = PerformanceMetric(
            name=operation_name,
            category=category,
            value=duration_ms,
            unit="milliseconds",
            timestamp=datetime.now(),
            user_id=session["user_id"],
            session_id=session_id,
            device_info=session["device_info"],
            network_info={"type": session["network_type"]},
            location_info={"region": session["location"]},
            app_version=self.app_version,
            additional_context=additional_context or {}
        )
        
        # Store metric
        self.performance_data[category.value].append(metric)
        session["performance_metrics"].append(metric)
        
        # Check performance against budgets
        self._check_performance_budget(metric)
        
        # Log metric
        self.logger.info(
            "performance_metric_recorded",
            operation=operation_name,
            category=category.value,
            duration_ms=duration_ms,
            session_id=session_id,
            device=session["device_info"].get("category"),
            network=session["network_type"],
            location=session["location"]
        )
        
        return metric
        
    def _check_performance_budget(self, metric: PerformanceMetric):
        """Check if metric violates performance budget"""
        
        budget_key = f"{metric.category.value}_ms"
        budgets = self.indian_config["performance_budgets"]
        
        if budget_key in budgets:
            target = budgets[budget_key]["target"]
            max_allowed = budgets[budget_key]["max"]
            
            if metric.value > max_allowed:
                self._trigger_performance_alert("budget_violation", metric, max_allowed)
            elif metric.value > target:
                self._trigger_performance_alert("budget_warning", metric, target)
                
    def _trigger_performance_alert(self, alert_type: str, metric: PerformanceMetric, threshold: float):
        """Trigger performance alert when thresholds are exceeded"""
        
        alert_data = {
            "alert_type": alert_type,
            "metric_name": metric.name,
            "category": metric.category.value,
            "actual_value_ms": metric.value,
            "threshold_ms": threshold,
            "excess_ms": metric.value - threshold,
            "session_id": metric.session_id,
            "user_id": metric.user_id,
            "device_category": metric.device_info.get("category"),
            "network_type": metric.network_info.get("type"),
            "location": metric.location_info.get("region"),
            "timestamp": metric.timestamp.isoformat()
        }
        
        severity = "critical" if alert_type == "budget_violation" else "warning"
        
        self.logger.bind(severity=severity).warning(
            "performance_alert_triggered",
            **alert_data
        )
        
        return alert_data
        
    async def track_business_transaction(self, session_id: str, transaction_name: str, 
                                       context: Dict = None) -> Dict[str, Any]:
        """Track complete business transaction performance"""
        
        if transaction_name not in self.business_transactions:
            self.logger.warning(f"Unknown business transaction: {transaction_name}")
            return {}
            
        if session_id not in self.user_sessions:
            self.logger.warning(f"Session not found: {session_id}")
            return {}
        
        transaction_def = self.business_transactions[transaction_name]
        session = self.user_sessions[session_id]
        
        transaction_start = datetime.now()
        transaction_id = f"{transaction_name}_{int(time.time())}"
        
        transaction_result = {
            "transaction_id": transaction_id,
            "transaction_name": transaction_name,
            "session_id": session_id,
            "start_time": transaction_start,
            "steps": {},
            "total_duration_ms": 0,
            "success": False,
            "abandonment_reason": None,
            "business_impact": transaction_def["business_impact"]
        }
        
        self.logger.info(
            "business_transaction_started", 
            transaction_name=transaction_name,
            transaction_id=transaction_id,
            session_id=session_id
        )
        
        try:
            # Execute transaction steps
            for step in transaction_def["steps"]:
                step_result = await self._execute_transaction_step(
                    session_id, transaction_name, step, context
                )
                
                transaction_result["steps"][step] = step_result
                transaction_result["total_duration_ms"] += step_result["duration_ms"]
                
                # Check for step failure or timeout
                if not step_result["success"]:
                    transaction_result["abandonment_reason"] = f"Step failed: {step}"
                    break
                    
                # Check for user abandonment patterns
                if self._check_abandonment_risk(transaction_result, transaction_def):
                    transaction_result["abandonment_reason"] = "User abandonment risk"
                    break
                    
            # Transaction completed successfully
            if not transaction_result["abandonment_reason"]:
                transaction_result["success"] = True
                
            transaction_result["end_time"] = datetime.now()
            
            # Store transaction result
            session["business_transactions"][transaction_id] = transaction_result
            
            # Log completion
            self.logger.info(
                "business_transaction_completed",
                transaction_id=transaction_id,
                success=transaction_result["success"],
                total_duration_ms=transaction_result["total_duration_ms"],
                abandonment_reason=transaction_result.get("abandonment_reason")
            )
            
        except Exception as e:
            transaction_result["success"] = False
            transaction_result["abandonment_reason"] = f"Exception: {str(e)}"
            
            self.logger.error(
                "business_transaction_failed",
                transaction_id=transaction_id,
                error=str(e)
            )
            
        return transaction_result
        
    async def _execute_transaction_step(self, session_id: str, transaction_name: str, 
                                       step_name: str, context: Dict) -> Dict[str, Any]:
        """Execute individual transaction step"""
        
        session = self.user_sessions[session_id]
        device_category = session["device_info"].get("category", "mid_range")
        network_type = session["network_type"]
        location = session["location"]
        
        # Get performance expectations based on device and network
        device_profile = self.device_profiles.get(device_category, {})
        network_profile = self.network_profiles.get(network_type, {})
        
        # Simulate step execution with realistic performance
        step_result = {
            "step_name": step_name,
            "start_time": datetime.now(),
            "success": True,
            "duration_ms": 0,
            "error": None
        }
        
        try:
            # Simulate different step types
            if step_name in ["app_launch", "splash_screen"]:
                base_duration = device_profile.get("expected_app_launch_ms", 3000)
                duration = await self._simulate_app_launch(base_duration, device_category, network_type)
                
            elif step_name in ["menu_load", "restaurant_search", "results_load"]:
                base_duration = 1000
                duration = await self._simulate_data_load(base_duration, network_type, location)
                
            elif step_name in ["payment", "authentication", "processing"]:
                base_duration = 2000
                duration = await self._simulate_payment_operation(base_duration, network_type)
                
            elif step_name in ["location_detect", "driver_matching"]:
                base_duration = 3000
                duration = await self._simulate_location_operation(base_duration, location)
                
            else:
                # Generic step
                base_duration = 800
                duration = await self._simulate_generic_operation(base_duration, device_category)
            
            step_result["duration_ms"] = duration
            step_result["end_time"] = datetime.now()
            
            # Record as performance metric
            category = self._get_category_for_step(step_name)
            self.record_performance_metric(
                session_id, category, f"{transaction_name}_{step_name}", 
                duration, {"transaction_step": True}
            )
            
        except Exception as e:
            step_result["success"] = False
            step_result["error"] = str(e)
            step_result["duration_ms"] = 0
            
        return step_result
        
    async def _simulate_app_launch(self, base_duration: float, device_category: str, network_type: str) -> float:
        """Simulate app launch performance"""
        
        # Device impact
        device_multiplier = self.device_profiles[device_category]["cpu_performance_multiplier"]
        
        # Network impact (for initial data loading)
        network_multiplier = 1.0
        if network_type == "3g":
            network_multiplier = 1.5
        elif network_type == "2g":
            network_multiplier = 3.0
        elif network_type == "wifi":
            network_multiplier = 0.8
            
        # Random variation
        random_factor = random.uniform(0.7, 1.8)
        
        duration = base_duration / device_multiplier * network_multiplier * random_factor
        
        # Simulate actual delay
        await asyncio.sleep(min(duration / 1000, 0.1))  # Cap simulation delay
        
        return duration
        
    async def _simulate_data_load(self, base_duration: float, network_type: str, location: str) -> float:
        """Simulate data loading performance"""
        
        network_profile = self.network_profiles[network_type]
        network_speed = network_profile["avg_speed_mbps"]
        network_latency = network_profile["latency_ms"]
        
        # Regional impact
        regional_config = self.indian_config["regional_characteristics"].get(location, {})
        regional_speed_multiplier = regional_config.get("avg_network_speed_mbps", 15) / 15.0
        
        # Calculate duration based on network performance
        duration = base_duration + network_latency + (base_duration * (1 - regional_speed_multiplier))
        duration *= random.uniform(0.8, 2.0)  # Add variation
        
        await asyncio.sleep(min(duration / 1000, 0.05))
        return duration
        
    async def _simulate_payment_operation(self, base_duration: float, network_type: str) -> float:
        """Simulate payment operation performance"""
        
        # Payment operations are more sensitive to network quality
        network_profile = self.network_profiles[network_type]
        reliability = network_profile["reliability_percent"] / 100.0
        
        # Lower reliability increases duration due to retries
        duration = base_duration / reliability
        
        # Add random payment gateway latency
        gateway_latency = random.uniform(500, 2000)
        duration += gateway_latency
        
        # Random failure simulation (affects duration)
        if random.random() > reliability:
            duration *= 2  # Failed operations take longer due to retries
            
        await asyncio.sleep(min(duration / 1000, 0.08))
        return duration
        
    async def _simulate_location_operation(self, base_duration: float, location: str) -> float:
        """Simulate location-based operations"""
        
        # Tier-3 cities have slower GPS and location services
        if "tier3" in location:
            location_multiplier = 2.0
        elif "tier2" in location:
            location_multiplier = 1.5
        else:
            location_multiplier = 1.0
            
        duration = base_duration * location_multiplier * random.uniform(0.5, 2.5)
        
        await asyncio.sleep(min(duration / 1000, 0.06))
        return duration
        
    async def _simulate_generic_operation(self, base_duration: float, device_category: str) -> float:
        """Simulate generic operations"""
        
        device_multiplier = self.device_profiles[device_category]["cpu_performance_multiplier"]
        duration = base_duration / device_multiplier * random.uniform(0.8, 1.5)
        
        await asyncio.sleep(min(duration / 1000, 0.03))
        return duration
        
    def _get_category_for_step(self, step_name: str) -> PerformanceCategory:
        """Map transaction step to performance category"""
        
        step_category_map = {
            "app_launch": PerformanceCategory.APP_LAUNCH,
            "splash_screen": PerformanceCategory.SCREEN_LOAD,
            "login_screen": PerformanceCategory.SCREEN_LOAD,
            "menu_load": PerformanceCategory.SCREEN_LOAD,
            "restaurant_search": PerformanceCategory.SEARCH_OPERATION,
            "results_load": PerformanceCategory.API_RESPONSE,
            "payment": PerformanceCategory.PAYMENT_FLOW,
            "authentication": PerformanceCategory.PAYMENT_FLOW,
            "location_detect": PerformanceCategory.LOCATION_SERVICE,
            "driver_matching": PerformanceCategory.API_RESPONSE
        }
        
        return step_category_map.get(step_name, PerformanceCategory.USER_INTERACTION)
        
    def _check_abandonment_risk(self, transaction_result: Dict, transaction_def: Dict) -> bool:
        """Check if user is likely to abandon based on performance"""
        
        total_duration = transaction_result["total_duration_ms"]
        max_duration = transaction_def["max_duration_ms"]
        
        # Risk increases exponentially after certain thresholds
        if total_duration > max_duration * 0.8:
            return random.random() > 0.7  # 30% chance to continue
        elif total_duration > max_duration * 0.6:
            return random.random() > 0.85  # 15% chance to abandon
        else:
            return False  # Low abandonment risk
            
    def get_performance_insights(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance insights"""
        
        insights = {
            "app_name": self.app_name,
            "analysis_period": {
                "window_hours": time_window_hours,
                "end_time": datetime.now().isoformat()
            },
            "overall_performance": {},
            "device_performance": {},
            "network_performance": {},
            "regional_performance": {},
            "business_transaction_analysis": {},
            "recommendations": []
        }
        
        # Overall performance analysis
        insights["overall_performance"] = self._analyze_overall_performance()
        
        # Device-based performance breakdown
        insights["device_performance"] = self._analyze_device_performance()
        
        # Network impact analysis
        insights["network_performance"] = self._analyze_network_performance()
        
        # Regional performance variations
        insights["regional_performance"] = self._analyze_regional_performance()
        
        # Business transaction performance
        insights["business_transaction_analysis"] = self._analyze_business_transactions()
        
        # Generate recommendations
        insights["recommendations"] = self._generate_performance_recommendations(insights)
        
        return insights
        
    def _analyze_overall_performance(self) -> Dict[str, Any]:
        """Analyze overall app performance"""
        
        overall_stats = {}
        
        for category, metrics in self.performance_data.items():
            if not metrics:
                continue
                
            values = [m.value for m in metrics]
            
            overall_stats[category] = {
                "count": len(values),
                "avg_ms": np.mean(values),
                "p50_ms": np.percentile(values, 50),
                "p90_ms": np.percentile(values, 90),
                "p95_ms": np.percentile(values, 95),
                "p99_ms": np.percentile(values, 99),
                "max_ms": np.max(values),
                "min_ms": np.min(values)
            }
        
        return overall_stats
        
    def _analyze_device_performance(self) -> Dict[str, Any]:
        """Analyze performance by device category"""
        
        device_stats = defaultdict(lambda: defaultdict(list))
        
        for category, metrics in self.performance_data.items():
            for metric in metrics:
                device_cat = metric.device_info.get("category", "unknown")
                device_stats[device_cat][category].append(metric.value)
        
        device_analysis = {}
        
        for device_cat, categories in device_stats.items():
            device_analysis[device_cat] = {}
            
            for category, values in categories.items():
                if values:
                    device_analysis[device_cat][category] = {
                        "avg_ms": np.mean(values),
                        "p90_ms": np.percentile(values, 90),
                        "count": len(values)
                    }
        
        return device_analysis
        
    def _analyze_network_performance(self) -> Dict[str, Any]:
        """Analyze performance by network type"""
        
        network_stats = defaultdict(lambda: defaultdict(list))
        
        for category, metrics in self.performance_data.items():
            for metric in metrics:
                network_type = metric.network_info.get("type", "unknown")
                network_stats[network_type][category].append(metric.value)
        
        network_analysis = {}
        
        for network_type, categories in network_stats.items():
            network_analysis[network_type] = {}
            
            for category, values in categories.items():
                if values:
                    network_analysis[network_type][category] = {
                        "avg_ms": np.mean(values),
                        "p90_ms": np.percentile(values, 90),
                        "count": len(values)
                    }
        
        return network_analysis
        
    def _analyze_regional_performance(self) -> Dict[str, Any]:
        """Analyze performance by region"""
        
        regional_stats = defaultdict(lambda: defaultdict(list))
        
        for category, metrics in self.performance_data.items():
            for metric in metrics:
                region = metric.location_info.get("region", "unknown")
                regional_stats[region][category].append(metric.value)
        
        regional_analysis = {}
        
        for region, categories in regional_stats.items():
            regional_analysis[region] = {}
            
            for category, values in categories.items():
                if values:
                    regional_analysis[region][category] = {
                        "avg_ms": np.mean(values),
                        "p90_ms": np.percentile(values, 90),
                        "count": len(values)
                    }
        
        return regional_analysis
        
    def _analyze_business_transactions(self) -> Dict[str, Any]:
        """Analyze business transaction performance"""
        
        transaction_analysis = {}
        
        for session_id, session in self.user_sessions.items():
            for tx_id, transaction in session["business_transactions"].items():
                tx_name = transaction["transaction_name"]
                
                if tx_name not in transaction_analysis:
                    transaction_analysis[tx_name] = {
                        "total_attempts": 0,
                        "successful_completions": 0,
                        "abandonments": 0,
                        "durations": [],
                        "abandonment_reasons": defaultdict(int),
                        "success_rate": 0,
                        "avg_duration_ms": 0
                    }
                
                stats = transaction_analysis[tx_name]
                stats["total_attempts"] += 1
                
                if transaction["success"]:
                    stats["successful_completions"] += 1
                    stats["durations"].append(transaction["total_duration_ms"])
                else:
                    stats["abandonments"] += 1
                    if transaction["abandonment_reason"]:
                        stats["abandonment_reasons"][transaction["abandonment_reason"]] += 1
        
        # Calculate final statistics
        for tx_name, stats in transaction_analysis.items():
            if stats["total_attempts"] > 0:
                stats["success_rate"] = stats["successful_completions"] / stats["total_attempts"] * 100
                
            if stats["durations"]:
                stats["avg_duration_ms"] = np.mean(stats["durations"])
                stats["p90_duration_ms"] = np.percentile(stats["durations"], 90)
        
        return transaction_analysis
        
    def _generate_performance_recommendations(self, insights: Dict) -> List[str]:
        """Generate actionable performance recommendations"""
        
        recommendations = []
        
        # Overall performance recommendations
        overall = insights["overall_performance"]
        
        for category, stats in overall.items():
            if category == "app_launch" and stats.get("p90_ms", 0) > 5000:
                recommendations.append(
                    f"App launch P90 is {stats['p90_ms']:.0f}ms. Consider app bundle optimization, "
                    "lazy loading, or splash screen improvements."
                )
                
            elif category == "payment_flow" and stats.get("p90_ms", 0) > 8000:
                recommendations.append(
                    f"Payment flow P90 is {stats['p90_ms']:.0f}ms. Review payment gateway integration, "
                    "consider optimistic UI updates, and implement retry mechanisms."
                )
        
        # Device-specific recommendations
        device_perf = insights["device_performance"]
        
        if "budget" in device_perf:
            budget_stats = device_perf["budget"]
            recommendations.append(
                "Budget device performance detected. Consider implementing progressive loading, "
                "reducing memory usage, and optimizing for lower-end processors."
            )
        
        # Network-specific recommendations  
        network_perf = insights["network_performance"]
        
        if "3g" in network_perf:
            recommendations.append(
                "3G network usage detected. Implement aggressive caching, image compression, "
                "and offline-first features for better user experience."
            )
        
        # Business transaction recommendations
        tx_analysis = insights["business_transaction_analysis"]
        
        for tx_name, stats in tx_analysis.items():
            if stats.get("success_rate", 100) < 80:
                recommendations.append(
                    f"{tx_name} success rate is {stats['success_rate']:.1f}%. "
                    "Investigate abandonment reasons and implement improvements."
                )
        
        return recommendations

# Test and simulation functions
async def simulate_swiggy_dinner_rush():
    """Simulate Swiggy app performance during dinner rush"""
    print("🍽️ Simulating Swiggy dinner rush performance...")
    
    apm = IndianAPMMonitor("Swiggy", "8.15.0")
    
    # Simulate multiple user sessions
    sessions = []
    
    for i in range(10):  # 10 concurrent users
        device_types = ["flagship", "premium", "mid_range", "budget"]
        locations = ["mumbai", "bangalore", "delhi", "tier2_cities"]
        
        device_info = {
            "category": random.choice(device_types),
            "model": f"TestDevice_{i}",
            "os_version": "Android 13"
        }
        
        location = random.choice(locations)
        user_id = f"user_{9876543210 + i}"
        
        session_id = apm.start_user_session(user_id, device_info, location)
        sessions.append(session_id)
    
    print(f"📱 Started {len(sessions)} user sessions")
    
    # Simulate food ordering transactions
    tasks = []
    for session_id in sessions:
        task = apm.track_business_transaction(
            session_id, "food_ordering", 
            {"meal_type": "dinner", "rush_hour": True}
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # Analyze results
    successful = sum(1 for r in results if r.get("success", False))
    abandoned = len(results) - successful
    
    print(f"📊 Transaction Results:")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Abandoned: {abandoned}")
    print(f"  📈 Success Rate: {successful/len(results)*100:.1f}%")
    
    # Generate performance insights
    insights = apm.get_performance_insights()
    
    print(f"\n🔍 Performance Insights:")
    print(f"Overall Performance:")
    for category, stats in insights["overall_performance"].items():
        print(f"  {category}: Avg {stats['avg_ms']:.0f}ms, P90 {stats['p90_ms']:.0f}ms")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(insights["recommendations"][:3], 1):
        print(f"  {i}. {rec}")
    
    return apm, insights

def test_device_performance_variations():
    """Test performance variations across device categories"""
    print("\n📱 Testing device performance variations...")
    
    apm = IndianAPMMonitor("Flipkart", "12.0.9")
    
    device_categories = ["flagship", "premium", "mid_range", "budget"]
    
    for device_cat in device_categories:
        print(f"\n🔧 Testing {device_cat} device...")
        
        device_info = {"category": device_cat, "model": f"Test{device_cat}"}
        session_id = apm.start_user_session(f"testuser_{device_cat}", device_info, "mumbai")
        
        # Record some metrics
        apm.record_performance_metric(
            session_id, PerformanceCategory.APP_LAUNCH, 
            "app_launch_test", 
            apm.device_profiles[device_cat]["expected_app_launch_ms"] * random.uniform(0.8, 1.2)
        )
        
        apm.record_performance_metric(
            session_id, PerformanceCategory.SCREEN_LOAD,
            "home_screen_load",
            apm.device_profiles[device_cat]["expected_screen_load_ms"] * random.uniform(0.9, 1.3)
        )
    
    # Analyze device performance
    insights = apm.get_performance_insights()
    device_perf = insights["device_performance"]
    
    for device_cat in device_categories:
        if device_cat in device_perf:
            app_launch = device_perf[device_cat].get("app_launch", {})
            print(f"  {device_cat}: App Launch Avg {app_launch.get('avg_ms', 0):.0f}ms")

async def test_regional_performance_differences():
    """Test performance differences across Indian regions"""
    print("\n🗺️ Testing regional performance differences...")
    
    apm = IndianAPMMonitor("Zomato", "15.2.1")
    
    regions = ["mumbai", "bangalore", "delhi", "tier2_cities", "tier3_cities"]
    
    for region in regions:
        print(f"\n📍 Testing {region}...")
        
        device_info = {"category": "mid_range", "model": "TestDevice"}
        session_id = apm.start_user_session(f"user_{region}", device_info, region)
        
        # Simulate food ordering transaction
        result = await apm.track_business_transaction(session_id, "food_ordering")
        
        print(f"  Success: {result['success']}, Duration: {result['total_duration_ms']:.0f}ms")

if __name__ == "__main__":
    print("🚀 Episode 16: APM Performance Monitoring for Indian Apps")
    print("🇮🇳 Swiggy se Flipkart tak, sab ka performance track karte hain!")
    print("=" * 60)
    
    # Run comprehensive testing
    asyncio.run(simulate_swiggy_dinner_rush())
    test_device_performance_variations()
    asyncio.run(test_regional_performance_differences())
    
    print("\n" + "=" * 60)
    print("✅ APM performance monitoring testing completed!")
    print("📊 Key Insights:")
    print("  - Device category significantly impacts performance")
    print("  - Network type affects transaction success rates")
    print("  - Regional variations require different optimization")
    print("  - Business transaction monitoring reveals user experience")
    print("🔍 Next: Setup APM dashboards and alerting")
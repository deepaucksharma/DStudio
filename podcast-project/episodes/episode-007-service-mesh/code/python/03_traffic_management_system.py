#!/usr/bin/env python3
"""
Traffic Management System for Service Mesh
Mumbai Traffic Control System Inspired Implementation

Context:
Zomato/Swiggy जैसे high-traffic apps के लिए intelligent traffic routing
जैसे Mumbai traffic police signals को coordinate करते हैं peak hours में

Features:
- Canary deployments (like testing new traffic routes)
- Circuit breaking (like traffic diversions)
- Load balancing (like distributing vehicles across lanes)
- A/B testing (like comparing route efficiency)
"""

import time
import json
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import requests
import threading
from collections import defaultdict
import statistics

# Setup Mumbai-style logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [मुंबई-Traffic] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/mumbai-traffic-management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MumbaiTrafficManager')

class TrafficState(Enum):
    """Traffic state like Mumbai roads"""
    NORMAL = "normal"           # सामान्य traffic
    PEAK_HOUR = "peak_hour"     # Rush hour traffic  
    JAM = "jam"                 # Heavy traffic jam
    EMERGENCY = "emergency"     # Emergency situation
    FESTIVAL = "festival"       # Festival traffic (Ganpati, etc.)

class DeploymentStrategy(Enum):
    """Deployment strategies"""
    BLUE_GREEN = "blue_green"
    CANARY = "canary" 
    ROLLING = "rolling"
    IMMEDIATE = "immediate"

@dataclass
class ServiceInstance:
    """Service instance representation"""
    host: str
    port: int
    version: str = "v1"
    weight: int = 100
    healthy: bool = True
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    region: str = "mumbai"
    zone: str = "west"
    
    def __post_init__(self):
        self.id = f"{self.host}:{self.port}"
        self.last_health_check = datetime.now()

@dataclass 
class TrafficRule:
    """Traffic routing rule"""
    name: str
    condition: Dict[str, Any]  # Routing condition
    destination: str
    weight: int = 100
    timeout_ms: int = 5000
    retry_attempts: int = 3
    
@dataclass
class CircuitBreakerState:
    """Circuit breaker state tracking"""
    service_name: str
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    failure_threshold: int = 5
    recovery_timeout: int = 30  # seconds

class MumbaiTrafficManager:
    """
    Traffic Management System for Service Mesh
    Mumbai Traffic Police Control Room की तरह centralized management
    """
    
    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.traffic_rules: List[TrafficRule] = []
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.metrics: Dict[str, Any] = defaultdict(list)
        self.current_traffic_state = TrafficState.NORMAL
        
        # Mumbai specific configurations
        self.peak_hours = [(7, 11), (17, 22)]  # Morning and evening rush
        self.festival_dates = self._load_festival_calendar()
        
        # Traffic management thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._continuous_monitoring)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("🚦 Mumbai Traffic Management System initialized")
    
    def _load_festival_calendar(self) -> List[datetime]:
        """Load Mumbai festival calendar for traffic planning"""
        # Mumbai major festivals - approximate dates
        current_year = datetime.now().year
        festivals = [
            datetime(current_year, 8, 19),   # Ganesh Chaturthi start
            datetime(current_year, 8, 29),   # Ganesh Visarjan
            datetime(current_year, 10, 15),  # Navratri
            datetime(current_year, 11, 5),   # Diwali
            datetime(current_year, 12, 25),  # Christmas
        ]
        return festivals
    
    def register_service(self, service_name: str, instances: List[ServiceInstance]):
        """
        Register service with instances
        नई bus route add करने की तरह
        """
        self.services[service_name] = instances
        
        # Initialize circuit breaker
        self.circuit_breakers[service_name] = CircuitBreakerState(service_name)
        
        logger.info("🚌 Service registered: %s with %d instances", 
                   service_name, len(instances))
        
        # Log instance details  
        for instance in instances:
            logger.info("  📍 Instance: %s (v%s, zone: %s)", 
                       instance.id, instance.version, instance.zone)
    
    def add_traffic_rule(self, rule: TrafficRule):
        """Add traffic routing rule"""
        self.traffic_rules.append(rule)
        logger.info("📋 Traffic rule added: %s", rule.name)
    
    def get_current_traffic_state(self) -> TrafficState:
        """
        Determine current traffic state
        Mumbai traffic condition analysis
        """
        current_hour = datetime.now().hour
        current_date = datetime.now().date()
        
        # Check if it's a festival day
        for festival_date in self.festival_dates:
            if abs((current_date - festival_date.date()).days) <= 1:
                return TrafficState.FESTIVAL
        
        # Check if it's peak hour
        if any(start <= current_hour <= end for start, end in self.peak_hours):
            return TrafficState.PEAK_HOUR
        
        # Check overall system health for jam detection
        total_error_rate = self._calculate_overall_error_rate()
        if total_error_rate > 10:  # 10% error rate indicates jam
            return TrafficState.JAM
        
        return TrafficState.NORMAL
    
    def _calculate_overall_error_rate(self) -> float:
        """Calculate overall system error rate"""
        total_errors = 0
        total_requests = 0
        
        for service_name, instances in self.services.items():
            for instance in instances:
                if hasattr(instance, 'request_count'):
                    total_requests += getattr(instance, 'request_count', 0)
                    total_errors += getattr(instance, 'error_count', 0)
        
        return (total_errors / total_requests * 100) if total_requests > 0 else 0
    
    def route_request(self, service_name: str, request_context: Dict[str, Any]) -> Optional[ServiceInstance]:
        """
        Route request to appropriate service instance
        Mumbai traffic routing algorithm
        """
        if service_name not in self.services:
            logger.error("❌ Service not found: %s", service_name)
            return None
        
        instances = self.services[service_name]
        available_instances = [i for i in instances if i.healthy]
        
        if not available_instances:
            logger.error("❌ No healthy instances for service: %s", service_name)
            return None
        
        # Apply traffic rules
        for rule in self.traffic_rules:
            if self._matches_rule(rule, request_context):
                target_instances = [i for i in available_instances if i.version == rule.destination]
                if target_instances:
                    available_instances = target_instances
                    break
        
        # Choose routing algorithm based on traffic state
        traffic_state = self.get_current_traffic_state()
        
        if traffic_state == TrafficState.PEAK_HOUR:
            return self._peak_hour_routing(available_instances)
        elif traffic_state == TrafficState.JAM:
            return self._emergency_routing(available_instances)
        elif traffic_state == TrafficState.FESTIVAL:
            return self._festival_routing(available_instances)
        else:
            return self._normal_routing(available_instances)
    
    def _matches_rule(self, rule: TrafficRule, request_context: Dict[str, Any]) -> bool:
        """Check if request matches traffic rule"""
        for key, expected_value in rule.condition.items():
            if key not in request_context:
                return False
            
            actual_value = request_context[key]
            
            if isinstance(expected_value, dict):
                # Range check
                if 'min' in expected_value or 'max' in expected_value:
                    min_val = expected_value.get('min', float('-inf'))
                    max_val = expected_value.get('max', float('inf'))
                    if not (min_val <= actual_value <= max_val):
                        return False
                # Regex or exact match
                elif 'pattern' in expected_value:
                    import re
                    if not re.match(expected_value['pattern'], str(actual_value)):
                        return False
            else:
                # Exact match
                if actual_value != expected_value:
                    return False
        
        return True
    
    def _normal_routing(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Normal weighted round-robin routing"""
        # Weighted selection based on instance weights and performance
        weights = []
        for instance in instances:
            # Reduce weight for high response time or error rate
            performance_factor = max(0.1, 1 - (instance.error_rate / 100))
            response_time_factor = max(0.1, 1 / max(1, instance.response_time_ms / 100))
            
            effective_weight = instance.weight * performance_factor * response_time_factor
            weights.append(effective_weight)
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(instances)
        
        pick = random.uniform(0, total_weight)
        current = 0
        
        for i, weight in enumerate(weights):
            current += weight
            if current >= pick:
                return instances[i]
        
        return instances[-1]  # Fallback
    
    def _peak_hour_routing(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Peak hour routing - prefer local instances
        Mumbai rush hour strategy - local trains over long-distance
        """
        # Prefer instances in same zone during peak hours
        local_instances = [i for i in instances if i.zone == "west"]  # Assuming we're in west zone
        
        if local_instances:
            # Use most performant local instance
            return min(local_instances, key=lambda x: (x.response_time_ms, x.error_rate))
        else:
            return self._normal_routing(instances)
    
    def _emergency_routing(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Emergency routing - fastest response only
        Mumbai emergency vehicle routing
        """
        # Select instance with lowest response time
        return min(instances, key=lambda x: x.response_time_ms)
    
    def _festival_routing(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Festival routing - distribute load evenly
        Mumbai festival traffic management
        """
        # Even distribution during festivals
        return random.choice(instances)
    
    def implement_canary_deployment(self, service_name: str, canary_version: str, traffic_percentage: int):
        """
        Implement canary deployment
        नए route को धीरे धीरे test करने की तरह
        """
        logger.info("🐣 Implementing canary deployment for %s (v%s) - %d%% traffic", 
                   service_name, canary_version, traffic_percentage)
        
        # Create traffic rule for canary
        canary_rule = TrafficRule(
            name=f"canary-{service_name}-{canary_version}",
            condition={
                "canary_group": {"pattern": f"canary_{traffic_percentage}"},
                "service": service_name
            },
            destination=canary_version,
            weight=traffic_percentage
        )
        
        self.add_traffic_rule(canary_rule)
        
        # Monitor canary performance
        self._monitor_canary_deployment(service_name, canary_version)
    
    def _monitor_canary_deployment(self, service_name: str, canary_version: str):
        """Monitor canary deployment health"""
        def monitor():
            time.sleep(60)  # Monitor for 1 minute
            
            canary_instances = [i for i in self.services.get(service_name, []) 
                              if i.version == canary_version]
            
            if not canary_instances:
                return
            
            avg_error_rate = statistics.mean([i.error_rate for i in canary_instances])
            avg_response_time = statistics.mean([i.response_time_ms for i in canary_instances])
            
            if avg_error_rate > 5 or avg_response_time > 1000:  # Thresholds
                logger.warning("⚠️ Canary deployment showing high error rate or latency")
                self.rollback_canary_deployment(service_name, canary_version)
            else:
                logger.info("✅ Canary deployment healthy for %s v%s", service_name, canary_version)
        
        # Run monitoring in background
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def rollback_canary_deployment(self, service_name: str, canary_version: str):
        """Rollback canary deployment"""
        logger.warning("🔄 Rolling back canary deployment: %s v%s", service_name, canary_version)
        
        # Remove canary traffic rules
        self.traffic_rules = [rule for rule in self.traffic_rules 
                             if not (rule.name.startswith(f"canary-{service_name}") and 
                                   rule.destination == canary_version)]
        
        # Mark canary instances as unhealthy
        for instance in self.services.get(service_name, []):
            if instance.version == canary_version:
                instance.healthy = False
        
        logger.info("✅ Canary rollback completed for %s v%s", service_name, canary_version)
    
    def check_circuit_breaker(self, service_name: str) -> bool:
        """
        Check circuit breaker state
        Mumbai traffic signal status check
        """
        if service_name not in self.circuit_breakers:
            return True  # Allow if no circuit breaker configured
        
        cb_state = self.circuit_breakers[service_name]
        
        if cb_state.state == "OPEN":
            # Check if recovery timeout has passed
            if (cb_state.last_failure_time and 
                datetime.now() - cb_state.last_failure_time > timedelta(seconds=cb_state.recovery_timeout)):
                cb_state.state = "HALF_OPEN"
                logger.info("🔄 Circuit breaker half-open for %s", service_name)
                return True
            else:
                logger.warning("🚫 Circuit breaker OPEN for %s", service_name)
                return False  # Block requests
        
        return True  # CLOSED or HALF_OPEN - allow requests
    
    def record_request_result(self, service_name: str, success: bool, response_time_ms: float):
        """
        Record request result for circuit breaker and metrics
        Mumbai traffic data collection
        """
        if service_name not in self.circuit_breakers:
            return
        
        cb_state = self.circuit_breakers[service_name]
        
        if success:
            cb_state.success_count += 1
            cb_state.failure_count = max(0, cb_state.failure_count - 1)  # Gradually reduce failure count
            
            # If in HALF_OPEN, consider closing if we have enough successful requests
            if cb_state.state == "HALF_OPEN" and cb_state.success_count >= 3:
                cb_state.state = "CLOSED"
                logger.info("✅ Circuit breaker CLOSED for %s", service_name)
        else:
            cb_state.failure_count += 1
            cb_state.last_failure_time = datetime.now()
            
            # Open circuit breaker if failure threshold reached
            if cb_state.failure_count >= cb_state.failure_threshold:
                cb_state.state = "OPEN"
                logger.warning("🚫 Circuit breaker OPENED for %s", service_name)
        
        # Record metrics
        self.metrics[service_name].append({
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'response_time_ms': response_time_ms,
            'traffic_state': self.current_traffic_state.value
        })
    
    def _continuous_monitoring(self):
        """Continuous monitoring of traffic conditions"""
        while self.monitoring_active:
            try:
                # Update traffic state
                old_state = self.current_traffic_state
                new_state = self.get_current_traffic_state()
                
                if old_state != new_state:
                    logger.info("🚦 Traffic state changed: %s -> %s", old_state.value, new_state.value)
                    self.current_traffic_state = new_state
                    self._adapt_to_traffic_state(new_state)
                
                # Health check all instances
                self._health_check_instances()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error("❌ Monitoring error: %s", e)
                time.sleep(60)  # Wait longer on error
    
    def _adapt_to_traffic_state(self, traffic_state: TrafficState):
        """Adapt system configuration based on traffic state"""
        if traffic_state == TrafficState.PEAK_HOUR:
            # Tighten circuit breaker thresholds
            for cb in self.circuit_breakers.values():
                cb.failure_threshold = 3
                cb.recovery_timeout = 15
        elif traffic_state == TrafficState.JAM:
            # Very conservative settings
            for cb in self.circuit_breakers.values():
                cb.failure_threshold = 2
                cb.recovery_timeout = 60
        else:
            # Normal settings
            for cb in self.circuit_breakers.values():
                cb.failure_threshold = 5
                cb.recovery_timeout = 30
    
    def _health_check_instances(self):
        """Health check all service instances"""
        for service_name, instances in self.services.items():
            for instance in instances:
                try:
                    # Simulate health check
                    health_check_url = f"http://{instance.host}:{instance.port}/health"
                    response = requests.get(health_check_url, timeout=5)
                    
                    was_healthy = instance.healthy
                    instance.healthy = response.status_code == 200
                    instance.last_health_check = datetime.now()
                    
                    if response.status_code == 200:
                        # Update performance metrics
                        instance.response_time_ms = response.elapsed.total_seconds() * 1000
                    
                    # Log health state changes
                    if was_healthy != instance.healthy:
                        status = "healthy" if instance.healthy else "unhealthy"
                        logger.info("🏥 Instance %s changed to %s", instance.id, status)
                        
                except Exception as e:
                    instance.healthy = False
                    logger.warning("⚠️ Health check failed for %s: %s", instance.id, e)
    
    def get_traffic_metrics(self) -> Dict[str, Any]:
        """Get traffic metrics dashboard"""
        metrics_summary = {}
        
        for service_name, metrics_list in self.metrics.items():
            if not metrics_list:
                continue
                
            recent_metrics = metrics_list[-100:]  # Last 100 requests
            
            success_rate = sum(1 for m in recent_metrics if m['success']) / len(recent_metrics) * 100
            avg_response_time = statistics.mean([m['response_time_ms'] for m in recent_metrics])
            
            circuit_breaker_state = self.circuit_breakers.get(service_name)
            
            metrics_summary[service_name] = {
                'success_rate': round(success_rate, 2),
                'avg_response_time_ms': round(avg_response_time, 2),
                'total_requests': len(metrics_list),
                'circuit_breaker_state': circuit_breaker_state.state if circuit_breaker_state else 'N/A',
                'healthy_instances': len([i for i in self.services.get(service_name, []) if i.healthy]),
                'total_instances': len(self.services.get(service_name, []))
            }
        
        return {
            'current_traffic_state': self.current_traffic_state.value,
            'services': metrics_summary,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """
    Demo: Mumbai Food Delivery Traffic Management
    Zomato/Swiggy style service mesh traffic management
    """
    print("🚦 Mumbai Service Mesh Traffic Management System")
    print("=" * 55)
    
    # Initialize traffic manager
    traffic_manager = MumbaiTrafficManager()
    
    # Register Zomato-style services
    print("\n🍕 Registering food delivery services...")
    
    # Order service instances
    order_instances = [
        ServiceInstance("10.0.1.10", 8080, version="v1", zone="west", weight=100),
        ServiceInstance("10.0.1.11", 8080, version="v1", zone="west", weight=100),
        ServiceInstance("10.0.2.10", 8080, version="v2", zone="east", weight=50),  # Canary
    ]
    traffic_manager.register_service("order-service", order_instances)
    
    # Restaurant service instances
    restaurant_instances = [
        ServiceInstance("10.0.1.20", 8081, version="v1", zone="west"),
        ServiceInstance("10.0.1.21", 8081, version="v1", zone="west"),
        ServiceInstance("10.0.2.20", 8081, version="v1", zone="east"),
    ]
    traffic_manager.register_service("restaurant-service", restaurant_instances)
    
    # Add traffic rules
    print("\n📋 Adding traffic routing rules...")
    
    # Premium users get newer version
    premium_rule = TrafficRule(
        name="premium-users-v2",
        condition={"user_type": "premium"},
        destination="v2",
        timeout_ms=3000
    )
    traffic_manager.add_traffic_rule(premium_rule)
    
    # Canary deployment for 10% of traffic
    print("\n🐣 Setting up canary deployment...")
    traffic_manager.implement_canary_deployment("order-service", "v2", 10)
    
    # Simulate traffic scenarios
    print("\n🚛 Simulating traffic scenarios...")
    
    scenarios = [
        {"user_type": "regular", "service": "order-service"},
        {"user_type": "premium", "service": "order-service"},
        {"user_type": "regular", "service": "restaurant-service"},
        {"canary_group": "canary_10", "service": "order-service"},
    ]
    
    for scenario in scenarios:
        # Check circuit breaker
        service_name = scenario["service"]
        if traffic_manager.check_circuit_breaker(service_name):
            # Route request
            selected_instance = traffic_manager.route_request(service_name, scenario)
            if selected_instance:
                # Simulate request execution
                success = random.random() > 0.1  # 90% success rate
                response_time = random.uniform(50, 500)  # 50-500ms
                
                print(f"  📍 {scenario} -> {selected_instance.id} (v{selected_instance.version}) "
                      f"[{response_time:.0f}ms, {'✅' if success else '❌'}]")
                
                # Record result
                traffic_manager.record_request_result(service_name, success, response_time)
            else:
                print(f"  ❌ No instance available for {service_name}")
        else:
            print(f"  🚫 Circuit breaker OPEN for {service_name}")
    
    # Show traffic metrics
    print("\n📊 Traffic Metrics Dashboard:")
    metrics = traffic_manager.get_traffic_metrics()
    
    print(f"Current Traffic State: 🚦 {metrics['current_traffic_state'].upper()}")
    
    for service_name, service_metrics in metrics['services'].items():
        print(f"\n🔧 {service_name}:")
        print(f"  Success Rate: {service_metrics['success_rate']}%")
        print(f"  Avg Response Time: {service_metrics['avg_response_time_ms']}ms")
        print(f"  Circuit Breaker: {service_metrics['circuit_breaker_state']}")
        print(f"  Healthy Instances: {service_metrics['healthy_instances']}/{service_metrics['total_instances']}")
    
    print(f"\n⏰ Last Updated: {metrics['timestamp']}")
    
    print("\n🚀 Traffic management system active!")
    print("Monitor logs at: /var/log/mumbai-traffic-management.log")

if __name__ == "__main__":
    main()
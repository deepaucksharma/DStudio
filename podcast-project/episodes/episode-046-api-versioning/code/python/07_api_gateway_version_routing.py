#!/usr/bin/env python3
"""
API Gateway Version Routing System
Inspired by Swiggy's API gateway for handling multiple app versions

Example: Swiggy ne kaise handle kiya different mobile app versions ka routing
"""

from flask import Flask, request, jsonify, redirect
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re
import time
import random
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RoutingStrategy(Enum):
    """API routing strategies"""
    HEADER_BASED = "header_based"          # Route by API-Version header
    URL_BASED = "url_based"               # Route by URL path (/v1/, /v2/)
    QUERY_PARAM = "query_param"           # Route by ?version=v1
    USER_AGENT = "user_agent"             # Route by app version in User-Agent
    CANARY_RELEASE = "canary_release"     # Gradual rollout
    A_B_TESTING = "a_b_testing"           # Split traffic for testing

@dataclass
class VersionRoute:
    """Version routing configuration"""
    version: str
    target_host: str
    target_port: int
    weight: float = 1.0  # For load balancing
    active: bool = True
    deprecated: bool = False
    sunset_date: Optional[str] = None

@dataclass
class RoutingRule:
    """Routing rule configuration"""
    name: str
    strategy: RoutingStrategy
    pattern: str
    target_version: str
    condition: Optional[str] = None  # Additional conditions
    priority: int = 10  # Lower number = higher priority

@dataclass
class RequestMetrics:
    """Request routing metrics"""
    timestamp: float
    version: str
    endpoint: str
    response_time_ms: float
    status_code: int
    user_agent: str
    routing_strategy: str

class APIGatewayRouter:
    """
    API Gateway for version-based routing
    Swiggy style routing for different mobile app versions
    """
    
    def __init__(self):
        self.version_routes = self._initialize_version_routes()
        self.routing_rules = self._initialize_routing_rules()
        self.request_metrics = []
        self.canary_config = {
            "v3_rollout_percentage": 20,  # 20% traffic to v3
            "enabled": True
        }
        self.ab_test_config = {
            "test_name": "new_search_algorithm",
            "control_version": "v2",
            "treatment_version": "v3",
            "traffic_split": 50,  # 50-50 split
            "enabled": False
        }
    
    def _initialize_version_routes(self) -> Dict[str, VersionRoute]:
        """Initialize version routing configuration"""
        return {
            "v1": VersionRoute(
                version="v1",
                target_host="swiggy-api-v1.internal",
                target_port=8001,
                weight=0.1,  # Reduced weight for deprecated version
                deprecated=True,
                sunset_date="2024-06-30"
            ),
            "v2": VersionRoute(
                version="v2",
                target_host="swiggy-api-v2.internal",
                target_port=8002,
                weight=0.7  # Most traffic still on stable v2
            ),
            "v3": VersionRoute(
                version="v3",
                target_host="swiggy-api-v3.internal",
                target_port=8003,
                weight=0.2  # Gradual rollout of v3
            )
        }
    
    def _initialize_routing_rules(self) -> List[RoutingRule]:
        """Initialize routing rules with priorities"""
        return [
            # High priority - explicit version headers
            RoutingRule(
                name="explicit_v3_header",
                strategy=RoutingStrategy.HEADER_BASED,
                pattern="3.0|v3",
                target_version="v3",
                priority=1
            ),
            RoutingRule(
                name="explicit_v2_header",
                strategy=RoutingStrategy.HEADER_BASED,
                pattern="2.0|v2",
                target_version="v2",
                priority=1
            ),
            RoutingRule(
                name="explicit_v1_header",
                strategy=RoutingStrategy.HEADER_BASED,
                pattern="1.0|v1",
                target_version="v1",
                priority=1
            ),
            
            # URL-based routing
            RoutingRule(
                name="url_v3_routing",
                strategy=RoutingStrategy.URL_BASED,
                pattern="^/v3/",
                target_version="v3",
                priority=2
            ),
            RoutingRule(
                name="url_v2_routing",
                strategy=RoutingStrategy.URL_BASED,
                pattern="^/v2/",
                target_version="v2",
                priority=2
            ),
            RoutingRule(
                name="url_v1_routing",
                strategy=RoutingStrategy.URL_BASED,
                pattern="^/v1/",
                target_version="v1",
                priority=2
            ),
            
            # User-Agent based routing (mobile app versions)
            RoutingRule(
                name="swiggy_app_v4_to_v3_api",
                strategy=RoutingStrategy.USER_AGENT,
                pattern="SwiggyApp/4\\.",
                target_version="v3",
                priority=3
            ),
            RoutingRule(
                name="swiggy_app_v3_to_v2_api",
                strategy=RoutingStrategy.USER_AGENT,
                pattern="SwiggyApp/3\\.",
                target_version="v2",
                priority=3
            ),
            RoutingRule(
                name="swiggy_app_old_to_v1_api",
                strategy=RoutingStrategy.USER_AGENT,
                pattern="SwiggyApp/[12]\\.",
                target_version="v1",
                priority=3
            ),
            
            # Query parameter routing
            RoutingRule(
                name="query_param_routing",
                strategy=RoutingStrategy.QUERY_PARAM,
                pattern="version",
                target_version="dynamic",  # Determined by param value
                priority=4
            ),
            
            # Default routing (lowest priority)
            RoutingRule(
                name="default_to_v2",
                strategy=RoutingStrategy.HEADER_BASED,
                pattern=".*",  # Match everything
                target_version="v2",
                priority=10
            )
        ]
    
    def determine_target_version(self, request_headers: Dict[str, str], 
                                request_path: str, query_params: Dict[str, str],
                                user_id: Optional[str] = None) -> str:
        """
        Determine target API version based on routing rules
        """
        # Sort rules by priority
        sorted_rules = sorted(self.routing_rules, key=lambda x: x.priority)
        
        for rule in sorted_rules:
            if self._matches_rule(rule, request_headers, request_path, query_params):
                target_version = rule.target_version
                
                # Handle dynamic routing
                if target_version == "dynamic":
                    if rule.strategy == RoutingStrategy.QUERY_PARAM:
                        target_version = query_params.get("version", "v2")
                
                # Apply canary release logic
                if self.canary_config["enabled"] and target_version == "v2":
                    if self._should_route_to_canary(user_id):
                        target_version = "v3"
                        logger.info(f"Canary routing: User {user_id} routed to v3")
                
                # Apply A/B testing logic
                if self.ab_test_config["enabled"]:
                    if self._should_route_to_ab_test(user_id, target_version):
                        target_version = self._get_ab_test_version(user_id)
                        logger.info(f"A/B test routing: User {user_id} routed to {target_version}")
                
                logger.info(f"Routing decision: {rule.name} -> {target_version}")
                return target_version
        
        # Fallback to default
        return "v2"
    
    def _matches_rule(self, rule: RoutingRule, headers: Dict[str, str], 
                     path: str, query_params: Dict[str, str]) -> bool:
        """Check if request matches routing rule"""
        
        if rule.strategy == RoutingStrategy.HEADER_BASED:
            # Check API-Version header
            api_version = headers.get("API-Version", "")
            return bool(re.search(rule.pattern, api_version, re.IGNORECASE))
        
        elif rule.strategy == RoutingStrategy.URL_BASED:
            return bool(re.match(rule.pattern, path))
        
        elif rule.strategy == RoutingStrategy.USER_AGENT:
            user_agent = headers.get("User-Agent", "")
            return bool(re.search(rule.pattern, user_agent))
        
        elif rule.strategy == RoutingStrategy.QUERY_PARAM:
            return rule.pattern in query_params
        
        return False
    
    def _should_route_to_canary(self, user_id: Optional[str]) -> bool:
        """Determine if request should go to canary version"""
        if not user_id:
            return False
        
        # Use hash of user_id for consistent routing
        user_hash = hash(user_id) % 100
        return user_hash < self.canary_config["v3_rollout_percentage"]
    
    def _should_route_to_ab_test(self, user_id: Optional[str], current_version: str) -> bool:
        """Check if request should participate in A/B test"""
        if not user_id or not self.ab_test_config["enabled"]:
            return False
        
        # Only include control and treatment versions
        valid_versions = [self.ab_test_config["control_version"], 
                         self.ab_test_config["treatment_version"]]
        return current_version in valid_versions
    
    def _get_ab_test_version(self, user_id: str) -> str:
        """Get A/B test version for user"""
        user_hash = hash(user_id) % 100
        
        if user_hash < self.ab_test_config["traffic_split"]:
            return self.ab_test_config["treatment_version"]
        else:
            return self.ab_test_config["control_version"]
    
    def get_target_endpoint(self, version: str, path: str) -> Dict[str, Any]:
        """Get target endpoint configuration for version"""
        route_config = self.version_routes.get(version)
        
        if not route_config or not route_config.active:
            # Fallback to v2 if version not available
            route_config = self.version_routes["v2"]
            version = "v2"
        
        # Remove version prefix from path if it exists
        cleaned_path = re.sub(r"^/v[0-9]+", "", path)
        if not cleaned_path.startswith("/"):
            cleaned_path = "/" + cleaned_path
        
        target_url = f"http://{route_config.target_host}:{route_config.target_port}{cleaned_path}"
        
        return {
            "version": version,
            "target_url": target_url,
            "target_host": route_config.target_host,
            "target_port": route_config.target_port,
            "deprecated": route_config.deprecated,
            "sunset_date": route_config.sunset_date
        }
    
    def log_request_metrics(self, version: str, endpoint: str, response_time_ms: float,
                          status_code: int, user_agent: str, routing_strategy: str):
        """Log request metrics for monitoring"""
        metrics = RequestMetrics(
            timestamp=time.time(),
            version=version,
            endpoint=endpoint,
            response_time_ms=response_time_ms,
            status_code=status_code,
            user_agent=user_agent,
            routing_strategy=routing_strategy
        )
        
        self.request_metrics.append(metrics)
        
        # Keep only last 1000 requests for memory efficiency
        if len(self.request_metrics) > 1000:
            self.request_metrics = self.request_metrics[-1000:]
    
    def get_routing_analytics(self) -> Dict[str, Any]:
        """Get routing analytics and metrics"""
        if not self.request_metrics:
            return {"message": "No metrics available"}
        
        # Version distribution
        version_counts = {}
        total_requests = len(self.request_metrics)
        
        for metric in self.request_metrics:
            version_counts[metric.version] = version_counts.get(metric.version, 0) + 1
        
        version_distribution = {
            v: {"count": count, "percentage": round((count/total_requests)*100, 2)}
            for v, count in version_counts.items()
        }
        
        # Response time analytics
        response_times = [m.response_time_ms for m in self.request_metrics]
        avg_response_time = sum(response_times) / len(response_times)
        
        # Error rate
        error_count = len([m for m in self.request_metrics if m.status_code >= 400])
        error_rate = (error_count / total_requests) * 100
        
        # Recent traffic (last 5 minutes)
        current_time = time.time()
        recent_metrics = [
            m for m in self.request_metrics 
            if current_time - m.timestamp <= 300  # 5 minutes
        ]
        
        return {
            "total_requests": total_requests,
            "version_distribution": version_distribution,
            "performance": {
                "avg_response_time_ms": round(avg_response_time, 2),
                "error_rate_percentage": round(error_rate, 2)
            },
            "recent_traffic": {
                "last_5_minutes": len(recent_metrics),
                "requests_per_minute": len(recent_metrics) / 5
            },
            "canary_status": {
                "enabled": self.canary_config["enabled"],
                "rollout_percentage": self.canary_config["v3_rollout_percentage"]
            },
            "ab_test_status": {
                "enabled": self.ab_test_config["enabled"],
                "test_name": self.ab_test_config["test_name"],
                "traffic_split": self.ab_test_config["traffic_split"]
            }
        }

# Flask app demonstrating API Gateway routing
app = Flask(__name__)
router = APIGatewayRouter()

@app.before_request
def route_request():
    """Route requests before processing"""
    start_time = time.time()
    
    # Extract routing information
    headers = dict(request.headers)
    path = request.path
    query_params = dict(request.args)
    user_id = request.headers.get('X-User-ID')
    
    # Determine target version
    target_version = router.determine_target_version(headers, path, query_params, user_id)
    
    # Get target endpoint
    target_info = router.get_target_endpoint(target_version, path)
    
    # Store routing info in request context
    request.routing_info = {
        "target_version": target_version,
        "target_info": target_info,
        "start_time": start_time
    }
    
    # Add routing headers
    request.routing_headers = {
        "X-Routed-Version": target_version,
        "X-Target-Host": target_info["target_host"],
        "X-Gateway": "swiggy-api-gateway"
    }
    
    # Log deprecation warning if needed
    if target_info["deprecated"]:
        logger.warning(f"Deprecated version {target_version} accessed. Sunset date: {target_info['sunset_date']}")

@app.after_request
def log_routing_metrics(response):
    """Log metrics after request processing"""
    if hasattr(request, 'routing_info'):
        routing_info = request.routing_info
        response_time = (time.time() - routing_info["start_time"]) * 1000
        
        router.log_request_metrics(
            version=routing_info["target_version"],
            endpoint=request.path,
            response_time_ms=response_time,
            status_code=response.status_code,
            user_agent=request.headers.get("User-Agent", ""),
            routing_strategy="gateway"
        )
        
        # Add routing headers to response
        if hasattr(request, 'routing_headers'):
            for key, value in request.routing_headers.items():
                response.headers[key] = value
        
        # Add deprecation warning to response headers
        if routing_info["target_info"]["deprecated"]:
            response.headers["Warning"] = f'299 - "API version {routing_info["target_version"]} is deprecated"'
            response.headers["Sunset"] = routing_info["target_info"]["sunset_date"]
    
    return response

# Mock API endpoints for different versions
@app.route('/restaurants', methods=['GET'])
@app.route('/v<int:version>/restaurants', methods=['GET'])
def get_restaurants(version=None):
    """Mock restaurant listing endpoint"""
    target_version = getattr(request, 'routing_info', {}).get('target_version', 'v2')
    
    # Different response formats based on version
    if target_version == "v1":
        return jsonify({
            "restaurants": [
                {"id": 1, "name": "Domino's Pizza", "rating": 4.2},
                {"id": 2, "name": "KFC", "rating": 4.0}
            ],
            "version": "v1"
        })
    elif target_version == "v2":
        return jsonify({
            "restaurants": [
                {
                    "id": 1, 
                    "name": "Domino's Pizza", 
                    "rating": 4.2,
                    "delivery_time": "25-30 mins",
                    "cuisines": ["Pizza", "Italian"]
                },
                {
                    "id": 2, 
                    "name": "KFC", 
                    "rating": 4.0,
                    "delivery_time": "20-25 mins",
                    "cuisines": ["Chicken", "Fast Food"]
                }
            ],
            "pagination": {"page": 1, "total": 2},
            "version": "v2"
        })
    else:  # v3
        return jsonify({
            "data": {
                "restaurants": [
                    {
                        "id": 1,
                        "name": "Domino's Pizza",
                        "rating": 4.2,
                        "delivery_time": "25-30 mins",
                        "cuisines": ["Pizza", "Italian"],
                        "offers": ["Buy 1 Get 1 Free"],
                        "sustainability_score": 4.5,
                        "estimated_cost_for_two": 600
                    }
                ]
            },
            "meta": {
                "page": 1,
                "total_pages": 1,
                "total_restaurants": 1,
                "applied_filters": [],
                "search_time_ms": 45
            },
            "version": "v3"
        })

@app.route('/gateway/analytics', methods=['GET'])
def get_gateway_analytics():
    """Get gateway routing analytics"""
    analytics = router.get_routing_analytics()
    return jsonify(analytics)

@app.route('/gateway/config', methods=['GET'])
def get_gateway_config():
    """Get current gateway configuration"""
    return jsonify({
        "version_routes": {
            v: {
                "target_host": route.target_host,
                "weight": route.weight,
                "active": route.active,
                "deprecated": route.deprecated
            }
            for v, route in router.version_routes.items()
        },
        "canary_config": router.canary_config,
        "ab_test_config": router.ab_test_config,
        "total_routing_rules": len(router.routing_rules)
    })

@app.route('/gateway/config/canary', methods=['POST'])
def update_canary_config():
    """Update canary release configuration"""
    data = request.get_json()
    
    if 'rollout_percentage' in data:
        router.canary_config['v3_rollout_percentage'] = data['rollout_percentage']
    
    if 'enabled' in data:
        router.canary_config['enabled'] = data['enabled']
    
    return jsonify({
        "message": "Canary configuration updated",
        "new_config": router.canary_config
    })

def demonstrate_api_gateway_routing():
    """
    Demonstrate API gateway routing with various scenarios
    """
    print("🔥 API Gateway Version Routing - Swiggy Style")
    print("=" * 60)
    
    # Simulate different request scenarios
    scenarios = [
        {
            "name": "Mobile App v4 (latest)",
            "headers": {"User-Agent": "SwiggyApp/4.1.2", "X-User-ID": "user123"},
            "path": "/restaurants",
            "query_params": {}
        },
        {
            "name": "Mobile App v3 (stable)",
            "headers": {"User-Agent": "SwiggyApp/3.8.1", "X-User-ID": "user456"},
            "path": "/restaurants",
            "query_params": {}
        },
        {
            "name": "Old Mobile App v2",
            "headers": {"User-Agent": "SwiggyApp/2.9.0", "X-User-ID": "user789"},
            "path": "/restaurants",
            "query_params": {}
        },
        {
            "name": "Explicit API version header",
            "headers": {"API-Version": "v3", "X-User-ID": "user321"},
            "path": "/restaurants",
            "query_params": {}
        },
        {
            "name": "URL-based versioning",
            "headers": {"X-User-ID": "user654"},
            "path": "/v2/restaurants",
            "query_params": {}
        },
        {
            "name": "Query parameter versioning",
            "headers": {"X-User-ID": "user987"},
            "path": "/restaurants",
            "query_params": {"version": "v1"}
        }
    ]
    
    print("\n📱 Routing Scenarios:")
    for scenario in scenarios:
        target_version = router.determine_target_version(
            scenario["headers"],
            scenario["path"],
            scenario["query_params"],
            scenario["headers"].get("X-User-ID")
        )
        
        target_info = router.get_target_endpoint(target_version, scenario["path"])
        
        print(f"\n{scenario['name']}:")
        print(f"  Target Version: {target_version}")
        print(f"  Target Host: {target_info['target_host']}")
        if target_info["deprecated"]:
            print(f"  ⚠️  DEPRECATED - Sunset: {target_info['sunset_date']}")
        
        # Simulate metrics logging
        router.log_request_metrics(
            version=target_version,
            endpoint=scenario["path"],
            response_time_ms=random.uniform(50, 200),
            status_code=200,
            user_agent=scenario["headers"].get("User-Agent", "Unknown"),
            routing_strategy="gateway"
        )
    
    # Display analytics
    print("\n📊 Gateway Analytics:")
    analytics = router.get_routing_analytics()
    print(f"Total Requests: {analytics['total_requests']}")
    print("Version Distribution:")
    for version, stats in analytics['version_distribution'].items():
        print(f"  {version}: {stats['count']} requests ({stats['percentage']}%)")
    
    print(f"\nPerformance:")
    print(f"  Avg Response Time: {analytics['performance']['avg_response_time_ms']} ms")
    print(f"  Error Rate: {analytics['performance']['error_rate_percentage']}%")
    
    print("\n🎯 API Gateway Benefits:")
    print("1. Centralized version management")
    print("2. Gradual rollout with canary releases")
    print("3. A/B testing capabilities")
    print("4. Backward compatibility for old apps")
    print("5. Real-time routing analytics")
    print("6. Deprecation management")

if __name__ == "__main__":
    # Run demonstration
    demonstrate_api_gateway_routing()
    
    # Start Flask app for testing
    # app.run(debug=True, port=5004)
#!/usr/bin/env python3
"""
Latency Optimizer - एज vs क्लाउड लेटेंसी तुलना और ऑप्टिमाइज़ेशन
Mumbai local train vs long-distance train की तरह - distance matters!

Real-world inspired by gaming companies like Dream11, MPL optimizing for Indian users
Network latency analysis: Mumbai to Singapore (150ms) vs Local Edge (5ms)
"""

import time
import asyncio
import statistics
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np
import logging
import random
import requests
from concurrent.futures import ThreadPoolExecutor
import ping3
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """Different types of services with different latency requirements"""
    REALTIME_GAMING = "रियल-टाइम गेमिंग"        # <50ms critical
    VIDEO_STREAMING = "वीडियो स्ट्रीमिंग"         # <100ms good
    API_CALLS = "एपीआई कॉल"                    # <200ms acceptable  
    FILE_UPLOAD = "फाइल अपलोड"                  # <500ms ok
    BATCH_PROCESSING = "बैच प्रोसेसिंग"           # >1000ms acceptable

class LocationTier(Enum):
    """Different tiers of computing locations"""
    DEVICE_EDGE = "डिवाइस एज"          # On-device processing
    LOCAL_EDGE = "लोकल एज"            # Local area edge server  
    REGIONAL_EDGE = "रीजनल एज"        # Regional data center
    CLOUD_NEAR = "नियर क्लाउड"        # Nearby cloud region
    CLOUD_FAR = "दूर क्लाउड"          # Distant cloud region

@dataclass
class LatencyMeasurement:
    """Single latency measurement result"""
    service_type: ServiceType
    location: LocationTier
    latency_ms: float
    timestamp: datetime
    payload_size_kb: float
    processing_time_ms: float
    network_time_ms: float
    success: bool
    error_message: Optional[str] = None

class LatencyProfiler:
    """
    Latency Profiler - Mumbai traffic analysis की तरह
    Different routes और different times पे latency measure करना
    """
    
    def __init__(self, location: str = "Mumbai"):
        """Initialize latency profiler for specific location"""
        self.location = location
        self.measurements: List[LatencyMeasurement] = []
        
        # Mumbai-specific network characteristics  
        self.network_profiles = {
            LocationTier.DEVICE_EDGE: {
                'base_latency_ms': 1.0,      # Device processing
                'variance_factor': 0.2,       # Low variance
                'availability': 0.99,         # High availability
                'bandwidth_mbps': 1000        # Local bus speed
            },
            LocationTier.LOCAL_EDGE: {
                'base_latency_ms': 5.0,       # Local network
                'variance_factor': 0.5,       
                'availability': 0.98,
                'bandwidth_mbps': 100         # LAN speed
            },
            LocationTier.REGIONAL_EDGE: {
                'base_latency_ms': 15.0,      # Regional network
                'variance_factor': 1.0,
                'availability': 0.97,
                'bandwidth_mbps': 50          # Regional connectivity
            },
            LocationTier.CLOUD_NEAR: {
                'base_latency_ms': 45.0,      # Mumbai to Delhi
                'variance_factor': 2.0,
                'availability': 0.99,
                'bandwidth_mbps': 20          # Internet connectivity
            },
            LocationTier.CLOUD_FAR: {
                'base_latency_ms': 150.0,     # Mumbai to Singapore
                'variance_factor': 3.0,
                'availability': 0.98,
                'bandwidth_mbps': 10          # International connectivity
            }
        }
        
        # Service-specific processing requirements
        self.service_profiles = {
            ServiceType.REALTIME_GAMING: {
                'processing_time_ms': 2.0,    # Minimal processing
                'payload_size_kb': 1.0,       # Small packets
                'critical_latency_ms': 50     # Critical threshold
            },
            ServiceType.VIDEO_STREAMING: {
                'processing_time_ms': 10.0,   # Video processing
                'payload_size_kb': 500.0,     # Video chunks
                'critical_latency_ms': 100
            },
            ServiceType.API_CALLS: {
                'processing_time_ms': 25.0,   # DB queries
                'payload_size_kb': 10.0,      # JSON responses
                'critical_latency_ms': 200
            },
            ServiceType.FILE_UPLOAD: {
                'processing_time_ms': 50.0,   # File processing
                'payload_size_kb': 1000.0,    # Larger files
                'critical_latency_ms': 500
            },
            ServiceType.BATCH_PROCESSING: {
                'processing_time_ms': 500.0,  # Heavy processing
                'payload_size_kb': 100.0,     # Batch data
                'critical_latency_ms': 2000
            }
        }
        
        logger.info(f"Latency Profiler initialized for {location}")
    
    async def measure_latency(self, service_type: ServiceType, location_tier: LocationTier, 
                            num_samples: int = 10) -> List[LatencyMeasurement]:
        """
        Measure latency for specific service and location combination
        Mumbai local train timing की तरह - multiple samples लेकर accurate measurement
        """
        measurements = []
        
        network_profile = self.network_profiles[location_tier]
        service_profile = self.service_profiles[service_type]
        
        logger.info(f"Measuring latency: {service_type.value} at {location_tier.value}")
        
        for i in range(num_samples):
            try:
                start_time = time.time()
                
                # Simulate network latency
                base_latency = network_profile['base_latency_ms']
                variance = base_latency * network_profile['variance_factor']
                network_latency = random.gauss(base_latency, variance)
                network_latency = max(0.1, network_latency)  # Minimum 0.1ms
                
                # Simulate processing time
                processing_time = service_profile['processing_time_ms']
                processing_variance = processing_time * 0.2  # 20% variance
                actual_processing_time = random.gauss(processing_time, processing_variance) 
                actual_processing_time = max(0.1, actual_processing_time)
                
                # Calculate payload transfer time
                payload_size = service_profile['payload_size_kb']
                bandwidth_mbps = network_profile['bandwidth_mbps']
                transfer_time_ms = (payload_size * 8) / (bandwidth_mbps * 1000) * 1000  # Convert to ms
                
                # Total latency
                total_latency = network_latency + actual_processing_time + transfer_time_ms
                
                # Simulate availability (some requests might fail)
                availability = network_profile['availability']
                success = random.random() < availability
                
                if not success:
                    total_latency *= 5  # Failed requests take much longer
                
                # Create measurement
                measurement = LatencyMeasurement(
                    service_type=service_type,
                    location=location_tier,
                    latency_ms=total_latency,
                    timestamp=datetime.now(),
                    payload_size_kb=payload_size,
                    processing_time_ms=actual_processing_time,
                    network_time_ms=network_latency + transfer_time_ms,
                    success=success,
                    error_message=None if success else "Network timeout"
                )
                
                measurements.append(measurement)
                self.measurements.append(measurement)
                
                # Simulate actual network delay
                await asyncio.sleep(total_latency / 1000.0 / 10.0)  # Scaled down for demo
                
            except Exception as e:
                logger.error(f"Measurement failed: {str(e)}")
                error_measurement = LatencyMeasurement(
                    service_type=service_type,
                    location=location_tier,
                    latency_ms=5000.0,  # Timeout value
                    timestamp=datetime.now(),
                    payload_size_kb=service_profile['payload_size_kb'],
                    processing_time_ms=0,
                    network_time_ms=5000.0,
                    success=False,
                    error_message=str(e)
                )
                measurements.append(error_measurement)
                self.measurements.append(error_measurement)
        
        logger.info(f"Completed {len(measurements)} measurements")
        return measurements
    
    def calculate_statistics(self, measurements: List[LatencyMeasurement]) -> Dict[str, Any]:
        """Calculate comprehensive statistics from measurements"""
        if not measurements:
            return {"error": "No measurements available"}
        
        successful_measurements = [m for m in measurements if m.success]
        failed_measurements = [m for m in measurements if not m.success]
        
        if not successful_measurements:
            return {"error": "All measurements failed"}
        
        latencies = [m.latency_ms for m in successful_measurements]
        processing_times = [m.processing_time_ms for m in successful_measurements]
        network_times = [m.network_time_ms for m in successful_measurements]
        
        stats = {
            "sample_count": len(measurements),
            "success_count": len(successful_measurements),
            "failure_count": len(failed_measurements),
            "success_rate_percent": (len(successful_measurements) / len(measurements)) * 100,
            
            "latency_stats": {
                "min_ms": min(latencies),
                "max_ms": max(latencies),
                "mean_ms": statistics.mean(latencies),
                "median_ms": statistics.median(latencies),
                "std_dev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
                "p95_ms": np.percentile(latencies, 95),
                "p99_ms": np.percentile(latencies, 99)
            },
            
            "processing_stats": {
                "mean_processing_ms": statistics.mean(processing_times),
                "mean_network_ms": statistics.mean(network_times)
            },
            
            "service_type": measurements[0].service_type.value,
            "location_tier": measurements[0].location.value
        }
        
        return stats

class LatencyOptimizer:
    """
    Latency Optimizer - सबसे अच्छा route find करना
    Mumbai metro route planning की तरह - fastest path selection
    """
    
    def __init__(self):
        """Initialize latency optimizer"""
        self.profiler = LatencyProfiler()
        self.optimization_rules = {}
        self.performance_cache = {}
        
        # Define optimization rules based on service requirements
        self._setup_optimization_rules()
        
        logger.info("Latency Optimizer initialized")
    
    def _setup_optimization_rules(self):
        """Setup optimization rules for different services"""
        
        # Gaming requires ultra-low latency - prefer device/local edge
        self.optimization_rules[ServiceType.REALTIME_GAMING] = {
            'max_acceptable_latency_ms': 50,
            'preferred_locations': [
                LocationTier.DEVICE_EDGE,
                LocationTier.LOCAL_EDGE
            ],
            'fallback_locations': [LocationTier.REGIONAL_EDGE],
            'weight_latency': 0.8,      # 80% weight for latency
            'weight_reliability': 0.2   # 20% weight for reliability
        }
        
        # Video streaming needs consistent performance
        self.optimization_rules[ServiceType.VIDEO_STREAMING] = {
            'max_acceptable_latency_ms': 100,
            'preferred_locations': [
                LocationTier.LOCAL_EDGE,
                LocationTier.REGIONAL_EDGE
            ],
            'fallback_locations': [LocationTier.CLOUD_NEAR],
            'weight_latency': 0.6,
            'weight_reliability': 0.4
        }
        
        # APIs can tolerate moderate latency
        self.optimization_rules[ServiceType.API_CALLS] = {
            'max_acceptable_latency_ms': 200,
            'preferred_locations': [
                LocationTier.REGIONAL_EDGE,
                LocationTier.CLOUD_NEAR
            ],
            'fallback_locations': [LocationTier.CLOUD_FAR],
            'weight_latency': 0.5,
            'weight_reliability': 0.5
        }
        
        # File uploads - throughput matters more than latency
        self.optimization_rules[ServiceType.FILE_UPLOAD] = {
            'max_acceptable_latency_ms': 500,
            'preferred_locations': [
                LocationTier.CLOUD_NEAR,
                LocationTier.REGIONAL_EDGE
            ],
            'fallback_locations': [LocationTier.CLOUD_FAR],
            'weight_latency': 0.3,
            'weight_reliability': 0.7
        }
        
        # Batch processing - cost matters most
        self.optimization_rules[ServiceType.BATCH_PROCESSING] = {
            'max_acceptable_latency_ms': 2000,
            'preferred_locations': [
                LocationTier.CLOUD_FAR,
                LocationTier.CLOUD_NEAR
            ],
            'fallback_locations': [LocationTier.REGIONAL_EDGE],
            'weight_latency': 0.2,
            'weight_reliability': 0.8
        }
    
    async def find_optimal_location(self, service_type: ServiceType) -> Tuple[LocationTier, Dict[str, Any]]:
        """
        Find optimal location for service deployment
        Mumbai train route optimization की तरह - best path find करना
        """
        logger.info(f"Finding optimal location for {service_type.value}")
        
        rules = self.optimization_rules[service_type]
        all_locations = list(LocationTier)
        location_scores = {}
        
        # Test all locations
        for location in all_locations:
            cache_key = f"{service_type.value}_{location.value}"
            
            # Check cache first
            if cache_key in self.performance_cache:
                stats = self.performance_cache[cache_key]
                logger.debug(f"Using cached stats for {cache_key}")
            else:
                # Measure performance
                measurements = await self.profiler.measure_latency(
                    service_type, location, num_samples=5
                )
                stats = self.profiler.calculate_statistics(measurements)
                
                # Cache results
                self.performance_cache[cache_key] = stats
            
            if "error" in stats:
                location_scores[location] = 0  # Failed location
                continue
            
            # Calculate composite score
            latency_score = self._calculate_latency_score(
                stats['latency_stats']['mean_ms'], 
                rules['max_acceptable_latency_ms']
            )
            
            reliability_score = stats['success_rate_percent'] / 100.0
            
            composite_score = (
                latency_score * rules['weight_latency'] +
                reliability_score * rules['weight_reliability']
            )
            
            location_scores[location] = composite_score
            
            logger.debug(f"{location.value}: latency={stats['latency_stats']['mean_ms']:.1f}ms, "
                        f"reliability={stats['success_rate_percent']:.1f}%, score={composite_score:.3f}")
        
        # Find best location
        best_location = max(location_scores, key=location_scores.get)
        best_score = location_scores[best_location]
        
        # Prepare detailed analysis
        analysis = {
            "recommended_location": best_location.value,
            "confidence_score": best_score,
            "all_location_scores": {loc.value: score for loc, score in location_scores.items()},
            "service_requirements": {
                "max_acceptable_latency_ms": rules['max_acceptable_latency_ms'],
                "preferred_locations": [loc.value for loc in rules['preferred_locations']],
                "optimization_weights": {
                    "latency_weight": rules['weight_latency'],
                    "reliability_weight": rules['weight_reliability']
                }
            }
        }
        
        # Add detailed stats for recommended location
        cache_key = f"{service_type.value}_{best_location.value}"
        if cache_key in self.performance_cache:
            analysis["performance_stats"] = self.performance_cache[cache_key]
        
        logger.info(f"Optimal location for {service_type.value}: {best_location.value} (score: {best_score:.3f})")
        
        return best_location, analysis
    
    def _calculate_latency_score(self, actual_latency: float, max_acceptable: float) -> float:
        """
        Calculate latency score (0-1, higher is better)
        Mumbai train punctuality की तरह - कितना on-time है
        """
        if actual_latency <= max_acceptable * 0.5:
            return 1.0  # Excellent latency
        elif actual_latency <= max_acceptable:
            return 0.8 - (actual_latency / max_acceptable) * 0.3  # Good to acceptable
        else:
            penalty_factor = actual_latency / max_acceptable
            return max(0.0, 0.5 - (penalty_factor - 1.0) * 0.2)  # Poor latency
    
    async def optimize_service_deployment(self, services: List[ServiceType]) -> Dict[str, Any]:
        """
        Optimize deployment for multiple services
        Mumbai railway network planning की तरह - multiple routes optimize करना
        """
        logger.info(f"Optimizing deployment for {len(services)} services")
        
        optimization_results = {}
        deployment_plan = {}
        cost_analysis = {}
        
        total_optimization_time = time.time()
        
        for service in services:
            start_time = time.time()
            optimal_location, analysis = await self.find_optimal_location(service)
            optimization_time = time.time() - start_time
            
            optimization_results[service.value] = analysis
            deployment_plan[service.value] = optimal_location.value
            
            # Calculate estimated costs (simplified)
            cost_analysis[service.value] = self._calculate_deployment_costs(
                service, optimal_location, analysis
            )
            
            logger.info(f"Service {service.value} -> {optimal_location.value} "
                       f"(optimized in {optimization_time:.2f}s)")
        
        total_optimization_time = time.time() - total_optimization_time
        
        # Generate summary
        summary = {
            "optimization_results": optimization_results,
            "deployment_plan": deployment_plan,
            "cost_analysis": cost_analysis,
            "optimization_time_seconds": total_optimization_time,
            "recommendations": self._generate_deployment_recommendations(optimization_results)
        }
        
        return summary
    
    def _calculate_deployment_costs(self, service: ServiceType, location: LocationTier, 
                                  analysis: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate estimated deployment costs for different locations
        Mumbai ke different areas में office setup करने की cost की तरह
        """
        # Base costs per location tier (monthly, in INR)
        base_costs = {
            LocationTier.DEVICE_EDGE: 0,        # No infrastructure cost
            LocationTier.LOCAL_EDGE: 50000,     # ₹50k/month
            LocationTier.REGIONAL_EDGE: 200000, # ₹2L/month  
            LocationTier.CLOUD_NEAR: 100000,    # ₹1L/month
            LocationTier.CLOUD_FAR: 150000      # ₹1.5L/month
        }
        
        # Traffic-based costs (per 1M requests)
        traffic_costs = {
            LocationTier.DEVICE_EDGE: 0,
            LocationTier.LOCAL_EDGE: 1000,      # ₹1k per 1M requests
            LocationTier.REGIONAL_EDGE: 2000,
            LocationTier.CLOUD_NEAR: 5000,
            LocationTier.CLOUD_FAR: 10000
        }
        
        base_cost = base_costs[location]
        traffic_cost = traffic_costs[location]
        
        # Performance-based adjustments
        performance_stats = analysis.get("performance_stats", {})
        latency_stats = performance_stats.get("latency_stats", {})
        
        # Better performance = higher infrastructure cost but lower operational costs
        if latency_stats:
            mean_latency = latency_stats.get("mean_ms", 100)
            success_rate = performance_stats.get("success_rate_percent", 95)
            
            # Reliability premium/discount
            reliability_factor = success_rate / 100.0
            operational_cost_factor = 2.0 - reliability_factor  # Lower reliability = higher ops cost
        else:
            operational_cost_factor = 1.0
        
        return {
            "base_monthly_cost_inr": base_cost,
            "traffic_cost_per_million_requests_inr": traffic_cost * operational_cost_factor,
            "estimated_monthly_operational_cost_inr": base_cost * operational_cost_factor,
            "cost_factor": operational_cost_factor,
            "location": location.value
        }
    
    def _generate_deployment_recommendations(self, optimization_results: Dict[str, Any]) -> List[str]:
        """Generate human-readable deployment recommendations"""
        recommendations = []
        
        # Analyze location distribution
        location_distribution = {}
        for service, result in optimization_results.items():
            location = result["recommended_location"]
            location_distribution[location] = location_distribution.get(location, 0) + 1
        
        # Infrastructure consolidation opportunities
        if len(location_distribution) > 3:
            recommendations.append(
                "🏗️  Consider consolidating services to fewer locations to reduce infrastructure costs"
            )
        
        # Edge computing adoption
        edge_services = sum(1 for result in optimization_results.values() 
                          if result["recommended_location"] in ["डिवाइस एज", "लोकल एज"])
        
        if edge_services > len(optimization_results) * 0.5:
            recommendations.append(
                "📍 High edge computing adoption recommended - invest in local edge infrastructure"
            )
        
        # Performance concerns
        low_confidence_services = [
            service for service, result in optimization_results.items()
            if result["confidence_score"] < 0.6
        ]
        
        if low_confidence_services:
            recommendations.append(
                f"⚠️  Services need attention: {', '.join(low_confidence_services)} - "
                "consider hybrid deployment or infrastructure upgrades"
            )
        
        # Cost optimization
        cloud_heavy_services = sum(1 for result in optimization_results.values()
                                 if "क्लाउड" in result["recommended_location"])
        
        if cloud_heavy_services > len(optimization_results) * 0.7:
            recommendations.append(
                "💰 High cloud dependency detected - evaluate edge computing ROI for cost optimization"
            )
        
        return recommendations

# Example usage and comprehensive testing
async def main():
    """
    Comprehensive latency optimization demo
    Mumbai traffic route optimization की तरह complete analysis
    """
    print("🚀 Latency Optimizer - Mumbai Edge Computing Analysis")
    print("=" * 70)
    
    # Initialize optimizer
    optimizer = LatencyOptimizer()
    
    # Test individual service optimization
    print("\n🎮 Testing Gaming Service Optimization...")
    gaming_location, gaming_analysis = await optimizer.find_optimal_location(ServiceType.REALTIME_GAMING)
    
    print(f"✅ Gaming Service Optimal Location: {gaming_location.value}")
    print(f"📊 Confidence Score: {gaming_analysis['confidence_score']:.3f}")
    
    if "performance_stats" in gaming_analysis:
        perf = gaming_analysis["performance_stats"]["latency_stats"]
        print(f"📈 Performance: {perf['mean_ms']:.1f}ms avg, {perf['p95_ms']:.1f}ms p95")
    
    # Test multiple services optimization
    print(f"\n🔄 Optimizing Multiple Services...")
    
    services_to_optimize = [
        ServiceType.REALTIME_GAMING,
        ServiceType.VIDEO_STREAMING,
        ServiceType.API_CALLS,
        ServiceType.FILE_UPLOAD,
        ServiceType.BATCH_PROCESSING
    ]
    
    optimization_summary = await optimizer.optimize_service_deployment(services_to_optimize)
    
    # Display deployment plan
    print(f"\n📋 Deployment Plan:")
    print("-" * 50)
    
    for service, location in optimization_summary["deployment_plan"].items():
        cost_info = optimization_summary["cost_analysis"][service]
        base_cost = cost_info["base_monthly_cost_inr"]
        print(f"• {service}: {location}")
        print(f"  💰 Est. Monthly Cost: ₹{base_cost:,}")
        
        # Performance info
        if service in optimization_summary["optimization_results"]:
            confidence = optimization_summary["optimization_results"][service]["confidence_score"]
            print(f"  🎯 Confidence: {confidence:.1%}")
    
    # Cost analysis summary
    print(f"\n💰 Cost Analysis Summary:")
    print("-" * 30)
    
    total_monthly_cost = sum(
        cost["base_monthly_cost_inr"] 
        for cost in optimization_summary["cost_analysis"].values()
    )
    
    print(f"Total Monthly Infrastructure Cost: ₹{total_monthly_cost:,}")
    print(f"Optimization Time: {optimization_summary['optimization_time_seconds']:.2f} seconds")
    
    # Display recommendations
    recommendations = optimization_summary["recommendations"]
    if recommendations:
        print(f"\n💡 Recommendations:")
        print("-" * 20)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
    # Latency comparison visualization (data preparation)
    print(f"\n📊 Latency Comparison Analysis:")
    print("-" * 40)
    
    # Create comparison data for all service-location combinations
    comparison_data = {}
    
    for service in services_to_optimize:
        service_data = {}
        for location in LocationTier:
            # Get cached measurements or use defaults
            cache_key = f"{service.value}_{location.value}"
            if cache_key in optimizer.performance_cache:
                stats = optimizer.performance_cache[cache_key]
                if "error" not in stats:
                    service_data[location.value] = stats["latency_stats"]["mean_ms"]
                else:
                    service_data[location.value] = None
            else:
                # Use network profile defaults for missing data
                network_profile = optimizer.profiler.network_profiles[location]
                service_profile = optimizer.profiler.service_profiles[service]
                estimated_latency = (
                    network_profile['base_latency_ms'] + 
                    service_profile['processing_time_ms']
                )
                service_data[location.value] = estimated_latency
        
        comparison_data[service.value] = service_data
    
    # Display comparison table
    locations = [tier.value for tier in LocationTier]
    
    print(f"\n{'Service':<20} | " + " | ".join(f"{loc:<15}" for loc in locations))
    print("-" * (20 + len(locations) * 18))
    
    for service, location_data in comparison_data.items():
        row = f"{service:<20} |"
        for loc in locations:
            latency = location_data.get(loc)
            if latency is not None:
                if latency < 50:
                    status = "🟢"  # Excellent
                elif latency < 100:
                    status = "🟡"  # Good  
                elif latency < 200:
                    status = "🟠"  # Acceptable
                else:
                    status = "🔴"  # Poor
                row += f" {status}{latency:>6.1f}ms    |"
            else:
                row += f" {'❌ FAILED':<13} |"
        print(row)
    
    # Business impact analysis
    print(f"\n📈 Business Impact Analysis:")
    print("-" * 35)
    
    edge_deployment_cost = sum(
        cost["base_monthly_cost_inr"] 
        for service, cost in optimization_summary["cost_analysis"].items()
        if "एज" in optimization_summary["deployment_plan"][service]
    )
    
    cloud_deployment_cost = sum(
        cost["base_monthly_cost_inr"]
        for service, cost in optimization_summary["cost_analysis"].items()
        if "क्लाउड" in optimization_summary["deployment_plan"][service]
    )
    
    print(f"Edge Computing Investment: ₹{edge_deployment_cost:,}/month")
    print(f"Cloud Computing Cost: ₹{cloud_deployment_cost:,}/month")
    print(f"Total Hybrid Architecture Cost: ₹{total_monthly_cost:,}/month")
    
    # Performance improvements
    edge_services = [
        service for service in services_to_optimize
        if "एज" in optimization_summary["deployment_plan"][service.value]
    ]
    
    if edge_services:
        print(f"\n🚀 Performance Improvements:")
        print(f"• {len(edge_services)}/{len(services_to_optimize)} services moved to edge")
        print(f"• Estimated latency reduction: 60-80% for edge services")
        print(f"• Improved user experience for latency-sensitive applications")
        print(f"• Reduced bandwidth costs for frequent requests")
    
    print(f"\n✅ Latency optimization analysis completed!")
    print(f"🎯 Mumbai edge computing deployment strategy optimized!")

if __name__ == "__main__":
    asyncio.run(main())
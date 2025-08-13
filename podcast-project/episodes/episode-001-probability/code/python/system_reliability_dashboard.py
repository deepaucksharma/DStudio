#!/usr/bin/env python3
"""
Real-time System Reliability Dashboard
=====================================

Production-grade real-time monitoring dashboard for system reliability.
Real examples: IRCTC system health, PhonePe transaction monitoring, Flipkart inventory tracking

मुख्य concepts:
1. Real-time metrics collection and visualization
2. Probability-based alerting system
3. Indian system context awareness (monsoon, festivals, peak hours)
4. Multi-component reliability aggregation

Mumbai analogy: Mumbai Traffic Control Center - real-time city monitoring
Author: Hindi Tech Podcast Series
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, deque
import statistics
import threading
import random
import math

# Hindi comments के साथ comprehensive reliability dashboard

@dataclass
class ComponentMetrics:
    """Individual component metrics"""
    name: str
    timestamp: datetime
    response_time: float      # milliseconds
    success_rate: float      # 0.0 to 1.0  
    error_rate: float        # 0.0 to 1.0
    throughput: float        # requests per second
    cpu_usage: float         # 0.0 to 100.0
    memory_usage: float      # 0.0 to 100.0
    availability: float      # 0.0 to 1.0
    
    # Indian context specific
    monsoon_impact: float    # Monsoon impact factor
    peak_hour_factor: float  # Peak hour load factor
    festival_load: float     # Festival season load

@dataclass
class SystemAlert:
    """System alert definition"""
    component: str
    alert_type: str          # 'WARNING', 'CRITICAL', 'INFO'
    message: str
    timestamp: datetime
    probability: float       # Probability of issue occurring
    indian_context: str      # Mumbai analogy or context

class IndianReliabilityDashboard:
    """
    Real-time system reliability dashboard with Indian context
    Mumbai के traffic control center जैसा real-time monitoring
    """
    
    def __init__(self, refresh_interval: int = 5):
        self.refresh_interval = refresh_interval
        self.components = {}
        self.alerts = deque(maxlen=100)  # Keep last 100 alerts
        self.metrics_history = defaultdict(lambda: deque(maxlen=200))  # 200 data points per component
        
        # System health aggregation
        self.overall_health_score = 1.0
        self.reliability_trend = "STABLE"
        
        # Indian context factors
        self.monsoon_season = self._is_monsoon_season()
        self.current_festival = self._detect_festival_season()
        self.peak_hour_active = False
        
        # Alert thresholds with Indian context
        self.alert_thresholds = {
            'response_time': {'warning': 1000, 'critical': 5000},    # milliseconds
            'error_rate': {'warning': 0.05, 'critical': 0.15},       # 5%, 15%
            'availability': {'warning': 0.95, 'critical': 0.90},     # 95%, 90%
            'cpu_usage': {'warning': 70, 'critical': 90},            # 70%, 90%
            'memory_usage': {'warning': 80, 'critical': 95}          # 80%, 95%
        }
        
        # Running state
        self.running = False
        self.dashboard_thread = None
        
        print("🖥️ Indian System Reliability Dashboard initialized")
        print("📊 Ready to monitor desi systems with Mumbai context!")
        
    def _is_monsoon_season(self) -> bool:
        """Check if current time is monsoon season"""
        current_month = datetime.now().month
        return current_month in [6, 7, 8, 9]
        
    def _detect_festival_season(self) -> str:
        """Detect current festival season"""
        current_month = datetime.now().month
        current_day = datetime.now().day
        
        # Simplified festival detection
        if current_month == 10:  # October - Diwali season
            return "DIWALI"
        elif current_month == 3:  # March - Holi
            return "HOLI"
        elif current_month == 8:  # August - Ganesh Chaturthi
            return "GANESH"
        elif current_month == 7 and current_day > 20:  # End July - Eid
            return "EID"
        elif current_month == 8 and current_day == 15:  # Independence Day
            return "INDEPENDENCE"
        else:
            return "REGULAR"
            
    def _is_peak_hour(self) -> bool:
        """Check if current time is peak hour"""
        current_hour = datetime.now().hour
        # Mumbai peak hours: 9-11 AM, 6-8 PM
        return (9 <= current_hour <= 11) or (18 <= current_hour <= 20)
        
    def register_component(self, component_name: str, endpoint: str = None) -> None:
        """
        Register a component for monitoring
        Component को monitoring के लिए register करते हैं
        """
        self.components[component_name] = {
            'endpoint': endpoint,
            'last_seen': None,
            'status': 'UNKNOWN'
        }
        print(f"📝 Registered component: {component_name}")
        
    async def collect_metrics(self, component_name: str) -> ComponentMetrics:
        """
        Collect metrics for a specific component
        Component के लिए metrics collect करते हैं
        """
        # Simulate realistic Indian system metrics
        current_time = datetime.now()
        
        # Base metrics with realistic Indian system characteristics
        base_response_time = random.uniform(200, 800)  # 200-800ms base
        base_success_rate = random.uniform(0.92, 0.99)  # 92-99% base success
        base_throughput = random.uniform(50, 200)      # 50-200 RPS
        
        # Apply Indian context factors
        monsoon_impact = self._calculate_monsoon_impact()
        peak_hour_factor = self._calculate_peak_hour_factor()
        festival_load = self._calculate_festival_load()
        
        # Adjust metrics based on context
        adjusted_response_time = base_response_time * peak_hour_factor * monsoon_impact
        adjusted_success_rate = base_success_rate / (1 + (monsoon_impact - 1) * 0.3)  # Monsoon reduces success
        adjusted_throughput = base_throughput * festival_load * peak_hour_factor
        
        # System resource metrics
        cpu_usage = random.uniform(20, 85) * peak_hour_factor
        memory_usage = random.uniform(30, 70) * festival_load
        
        # Calculate availability based on success rate and response time
        availability = adjusted_success_rate * (1 - min(0.2, adjusted_response_time / 10000))
        
        metrics = ComponentMetrics(
            name=component_name,
            timestamp=current_time,
            response_time=adjusted_response_time,
            success_rate=adjusted_success_rate,
            error_rate=1.0 - adjusted_success_rate,
            throughput=adjusted_throughput,
            cpu_usage=min(100, cpu_usage),
            memory_usage=min(100, memory_usage),
            availability=availability,
            monsoon_impact=monsoon_impact,
            peak_hour_factor=peak_hour_factor,
            festival_load=festival_load
        )
        
        # Store metrics in history
        self.metrics_history[component_name].append(metrics)
        
        # Update component status
        self.components[component_name]['last_seen'] = current_time
        self.components[component_name]['status'] = 'HEALTHY' if availability > 0.95 else 'DEGRADED'
        
        return metrics
        
    def _calculate_monsoon_impact(self) -> float:
        """Calculate monsoon impact factor"""
        if not self.monsoon_season:
            return 1.0
            
        # Monsoon intensity varies during the day
        current_hour = datetime.now().hour
        base_monsoon_impact = 1.4  # 40% increase in issues
        
        # Higher impact during peak monsoon hours (afternoon/evening)
        if 14 <= current_hour <= 18:  # 2 PM to 6 PM
            return base_monsoon_impact * 1.3
        elif 10 <= current_hour <= 14:  # Morning rain
            return base_monsoon_impact * 1.1
        else:
            return base_monsoon_impact
            
    def _calculate_peak_hour_factor(self) -> float:
        """Calculate peak hour load factor"""
        self.peak_hour_active = self._is_peak_hour()
        
        if not self.peak_hour_active:
            return 1.0
            
        current_hour = datetime.now().hour
        
        # Morning peak (9-11 AM) - office going crowd
        if 9 <= current_hour <= 11:
            return 1.6  # 60% increase
        # Evening peak (6-8 PM) - return crowd  
        elif 18 <= current_hour <= 20:
            return 1.8  # 80% increase - heavier return traffic
        else:
            return 1.0
            
    def _calculate_festival_load(self) -> float:
        """Calculate festival season load multiplier"""
        festival_multipliers = {
            'DIWALI': 2.5,      # Highest shopping load
            'HOLI': 1.8,        # Moderate celebration load
            'GANESH': 2.0,      # High religious activity
            'EID': 1.9,         # High celebration load
            'INDEPENDENCE': 1.4, # Moderate patriotic activity
            'REGULAR': 1.0      # Normal days
        }
        
        return festival_multipliers.get(self.current_festival, 1.0)
        
    def analyze_metrics(self, metrics: ComponentMetrics) -> List[SystemAlert]:
        """
        Analyze metrics and generate alerts
        Metrics का analysis करके alerts generate करते हैं
        """
        alerts = []
        
        # Response time analysis
        if metrics.response_time > self.alert_thresholds['response_time']['critical']:
            alert = SystemAlert(
                component=metrics.name,
                alert_type='CRITICAL',
                message=f"Response time {metrics.response_time:.0f}ms exceeds critical threshold",
                timestamp=metrics.timestamp,
                probability=0.9,
                indian_context="Mumbai traffic jam जैसी slow response - immediate action needed!"
            )
            alerts.append(alert)
            
        elif metrics.response_time > self.alert_thresholds['response_time']['warning']:
            alert = SystemAlert(
                component=metrics.name,
                alert_type='WARNING',
                message=f"Response time {metrics.response_time:.0f}ms is high",
                timestamp=metrics.timestamp,
                probability=0.6,
                indian_context="BEST bus delay जैसी - monitor करते रहें"
            )
            alerts.append(alert)
            
        # Error rate analysis  
        if metrics.error_rate > self.alert_thresholds['error_rate']['critical']:
            alert = SystemAlert(
                component=metrics.name,
                alert_type='CRITICAL',
                message=f"Error rate {metrics.error_rate:.1%} is critically high",
                timestamp=metrics.timestamp,
                probability=0.95,
                indian_context="IRCTC booking failure जैसी critical situation!"
            )
            alerts.append(alert)
            
        elif metrics.error_rate > self.alert_thresholds['error_rate']['warning']:
            alert = SystemAlert(
                component=metrics.name,
                alert_type='WARNING', 
                message=f"Error rate {metrics.error_rate:.1%} is elevated",
                timestamp=metrics.timestamp,
                probability=0.7,
                indian_context="PhonePe transaction glitch जैसी - investigate करें"
            )
            alerts.append(alert)
            
        # Availability analysis
        if metrics.availability < self.alert_thresholds['availability']['critical']:
            alert = SystemAlert(
                component=metrics.name,
                alert_type='CRITICAL',
                message=f"Availability {metrics.availability:.1%} is critically low",
                timestamp=metrics.timestamp,
                probability=0.9,
                indian_context="Mumbai local train strike जैसी - service disruption!"
            )
            alerts.append(alert)
            
        # Context-specific alerts
        if self.monsoon_season and metrics.monsoon_impact > 1.5:
            alert = SystemAlert(
                component=metrics.name,
                alert_type='WARNING',
                message="High monsoon impact detected on system performance",
                timestamp=metrics.timestamp,
                probability=0.8,
                indian_context="Monsoon flooding जैसा infrastructure impact"
            )
            alerts.append(alert)
            
        if self.current_festival != 'REGULAR' and metrics.festival_load > 2.0:
            alert = SystemAlert(
                component=metrics.name,
                alert_type='INFO',
                message=f"High {self.current_festival} season load detected",
                timestamp=metrics.timestamp,
                probability=0.5,
                indian_context=f"{self.current_festival} shopping rush - expected high load"
            )
            alerts.append(alert)
            
        return alerts
        
    def calculate_overall_health(self) -> float:
        """
        Calculate overall system health score
        Complete system की health score calculate करते हैं
        """
        if not self.components:
            return 1.0
            
        component_healths = []
        
        for component_name in self.components:
            if component_name in self.metrics_history and self.metrics_history[component_name]:
                latest_metrics = self.metrics_history[component_name][-1]
                
                # Calculate component health based on multiple factors
                availability_score = latest_metrics.availability
                performance_score = max(0, 1.0 - (latest_metrics.response_time / 10000))  # Normalize to 0-1
                reliability_score = latest_metrics.success_rate
                
                # Apply weights
                component_health = (
                    availability_score * 0.4 +    # 40% weight to availability
                    performance_score * 0.3 +     # 30% weight to performance  
                    reliability_score * 0.3       # 30% weight to reliability
                )
                
                component_healths.append(component_health)
                
        if component_healths:
            self.overall_health_score = statistics.mean(component_healths)
        else:
            self.overall_health_score = 1.0
            
        return self.overall_health_score
        
    def detect_trends(self) -> str:
        """
        Detect system reliability trends
        System की reliability trends detect करते हैं
        """
        if len(list(self.metrics_history.values())[0]) < 10:  # Need enough data
            return "INSUFFICIENT_DATA"
            
        # Calculate health scores for last 10 and previous 10 data points
        recent_healths = []
        previous_healths = []
        
        for component_name in self.components:
            if component_name in self.metrics_history:
                metrics_list = list(self.metrics_history[component_name])
                
                if len(metrics_list) >= 20:
                    # Recent 10 data points
                    for metrics in metrics_list[-10:]:
                        health = metrics.availability * metrics.success_rate
                        recent_healths.append(health)
                        
                    # Previous 10 data points  
                    for metrics in metrics_list[-20:-10]:
                        health = metrics.availability * metrics.success_rate
                        previous_healths.append(health)
                        
        if recent_healths and previous_healths:
            recent_avg = statistics.mean(recent_healths)
            previous_avg = statistics.mean(previous_healths)
            
            change = recent_avg - previous_avg
            
            if abs(change) < 0.02:  # Less than 2% change
                self.reliability_trend = "STABLE"
            elif change > 0.05:  # More than 5% improvement
                self.reliability_trend = "IMPROVING"
            elif change < -0.05:  # More than 5% degradation
                self.reliability_trend = "DEGRADING"
            else:
                self.reliability_trend = "STABLE"
        else:
            self.reliability_trend = "STABLE"
            
        return self.reliability_trend
        
    def generate_dashboard_view(self) -> Dict:
        """
        Generate complete dashboard view
        Complete dashboard का data generate करते हैं
        """
        # Update health and trends
        overall_health = self.calculate_overall_health()
        trend = self.detect_trends()
        
        # Get latest metrics for each component
        component_status = {}
        for component_name in self.components:
            if component_name in self.metrics_history and self.metrics_history[component_name]:
                latest_metrics = self.metrics_history[component_name][-1]
                component_status[component_name] = asdict(latest_metrics)
            else:
                component_status[component_name] = {"status": "NO_DATA"}
                
        # Recent alerts
        recent_alerts = [asdict(alert) for alert in list(self.alerts)[-10:]]  # Last 10 alerts
        
        # Indian context summary
        indian_context = {
            'monsoon_season': self.monsoon_season,
            'current_festival': self.current_festival,
            'peak_hour_active': self.peak_hour_active,
            'context_message': self._get_context_message()
        }
        
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'overall_health_score': overall_health,
            'reliability_trend': trend,
            'total_components': len(self.components),
            'healthy_components': len([c for c in self.components.values() if c['status'] == 'HEALTHY']),
            'component_metrics': component_status,
            'recent_alerts': recent_alerts,
            'indian_context': indian_context,
            'health_indicator': self._get_health_indicator(overall_health),
            'recommendations': self._get_recommendations()
        }
        
        return dashboard_data
        
    def _get_context_message(self) -> str:
        """Get contextual message for current Indian conditions"""
        messages = []
        
        if self.monsoon_season:
            messages.append("🌧️ Monsoon season active - expect higher latency")
            
        if self.peak_hour_active:
            messages.append("🚊 Peak hour traffic - Mumbai local train rush!")
            
        if self.current_festival != 'REGULAR':
            messages.append(f"🎉 {self.current_festival} season - festival shopping load")
            
        return " | ".join(messages) if messages else "☀️ Normal operating conditions"
        
    def _get_health_indicator(self, health_score: float) -> str:
        """Get health indicator emoji and text"""
        if health_score >= 0.95:
            return "EXCELLENT 🟢"
        elif health_score >= 0.85:
            return "GOOD 🟡"
        elif health_score >= 0.70:
            return "CONCERNING 🟠"
        else:
            return "CRITICAL 🔴"
            
    def _get_recommendations(self) -> List[str]:
        """Get actionable recommendations based on current state"""
        recommendations = []
        
        if self.overall_health_score < 0.8:
            recommendations.append("🔧 Investigate failing components immediately")
            
        if self.monsoon_season:
            recommendations.append("🌧️ Enable monsoon mode - increased timeouts and retries")
            
        if self.peak_hour_active:
            recommendations.append("⚡ Scale up resources for peak hour traffic")
            
        if self.current_festival != 'REGULAR':
            recommendations.append("🎊 Festival mode active - monitor payment gateways closely")
            
        if len(self.alerts) > 5:
            recommendations.append("🚨 High alert volume - check for systemic issues")
            
        return recommendations
        
    async def start_monitoring(self) -> None:
        """
        Start real-time monitoring
        Real-time monitoring शुरू करते हैं
        """
        self.running = True
        print("🚀 Starting real-time reliability monitoring...")
        print("📊 Mumbai-style system monitoring active!")
        
        try:
            while self.running:
                # Collect metrics for all registered components
                for component_name in self.components:
                    try:
                        metrics = await self.collect_metrics(component_name)
                        
                        # Analyze and generate alerts
                        new_alerts = self.analyze_metrics(metrics)
                        self.alerts.extend(new_alerts)
                        
                        # Print alerts as they occur
                        for alert in new_alerts:
                            alert_emoji = "🚨" if alert.alert_type == "CRITICAL" else "⚠️" if alert.alert_type == "WARNING" else "ℹ️"
                            print(f"{alert_emoji} {alert.component}: {alert.message}")
                            print(f"    🏙️ {alert.indian_context}")
                            
                    except Exception as e:
                        print(f"❌ Error collecting metrics for {component_name}: {e}")
                        
                # Sleep for refresh interval
                await asyncio.sleep(self.refresh_interval)
                
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
        finally:
            print("🛑 Reliability monitoring stopped")
            
    def stop_monitoring(self) -> None:
        """Stop monitoring"""
        self.running = False
        
    def print_dashboard(self) -> None:
        """
        Print formatted dashboard to console
        Console पर dashboard print करते हैं
        """
        dashboard = self.generate_dashboard_view()
        
        print("\n" + "="*70)
        print("🇮🇳 INDIAN SYSTEM RELIABILITY DASHBOARD")
        print("="*70)
        print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"🏥 Overall Health: {dashboard['health_indicator']}")
        print(f"📈 Trend: {dashboard['reliability_trend']}")
        print(f"🔧 Components: {dashboard['healthy_components']}/{dashboard['total_components']} healthy")
        print(f"🏙️ Context: {dashboard['indian_context']['context_message']}")
        print("")
        
        # Component status
        print("📊 COMPONENT STATUS")
        print("-" * 50)
        for comp_name, metrics in dashboard['component_metrics'].items():
            if 'availability' in metrics:
                status_emoji = "🟢" if metrics['availability'] > 0.95 else "🟡" if metrics['availability'] > 0.8 else "🔴"
                print(f"{status_emoji} {comp_name:15s}: {metrics['availability']:.1%} available, {metrics['response_time']:.0f}ms response")
            else:
                print(f"⚪ {comp_name:15s}: No data")
                
        # Recent alerts
        if dashboard['recent_alerts']:
            print("\n🚨 RECENT ALERTS")
            print("-" * 50)
            for alert in dashboard['recent_alerts'][-5:]:  # Last 5 alerts
                alert_time = alert['timestamp'][:19].replace('T', ' ')  # Format timestamp
                print(f"{alert['alert_type']:8s} | {alert['component']:12s} | {alert['message']}")
                
        # Recommendations
        if dashboard['recommendations']:
            print("\n💡 RECOMMENDATIONS")
            print("-" * 50)
            for rec in dashboard['recommendations']:
                print(f"• {rec}")
                
        print("="*70)

async def demo_reliability_dashboard():
    """
    Comprehensive reliability dashboard demonstration
    Complete demo with Indian e-commerce system monitoring
    """
    print("🖥️ Indian System Reliability Dashboard Demo")
    print("=" * 60)
    
    # Create dashboard
    dashboard = IndianReliabilityDashboard(refresh_interval=3)
    
    # Register components (typical Indian e-commerce system)
    components = [
        "PaymentGateway",
        "UserService", 
        "InventoryService",
        "OrderService",
        "NotificationService",
        "RecommendationEngine",
        "SearchService",
        "CartService"
    ]
    
    for component in components:
        dashboard.register_component(component)
        
    print(f"📝 Registered {len(components)} components for monitoring")
    print("🚀 Starting reliability monitoring simulation...")
    print("💡 Watch for monsoon, peak hour, and festival impacts!\n")
    
    # Simulate monitoring for 1 minute (20 cycles at 3-second intervals)
    monitoring_cycles = 20
    
    try:
        for cycle in range(monitoring_cycles):
            print(f"🔄 Monitoring cycle {cycle + 1}/{monitoring_cycles}")
            
            # Collect metrics for all components
            for component in components:
                await dashboard.collect_metrics(component)
                
            # Print dashboard every 5 cycles
            if (cycle + 1) % 5 == 0:
                dashboard.print_dashboard()
                
            await asyncio.sleep(dashboard.refresh_interval)
            
    except KeyboardInterrupt:
        print("\n⚠️ Monitoring interrupted by user")
        
    # Final dashboard
    print("\n🎯 FINAL DASHBOARD STATE")
    dashboard.print_dashboard()
    
    # Generate summary report
    final_dashboard = dashboard.generate_dashboard_view()
    
    print("\n📋 MONITORING SUMMARY")
    print("-" * 40)
    print(f"Total monitoring time: {monitoring_cycles * dashboard.refresh_interval} seconds")
    print(f"Total alerts generated: {len(dashboard.alerts)}")
    print(f"Final health score: {final_dashboard['overall_health_score']:.3f}")
    print(f"Final trend: {final_dashboard['reliability_trend']}")
    
    # Alert type breakdown
    alert_types = defaultdict(int)
    for alert in dashboard.alerts:
        alert_types[alert.alert_type] += 1
        
    if alert_types:
        print("\n🚨 Alert Breakdown:")
        for alert_type, count in alert_types.items():
            print(f"   {alert_type}: {count} alerts")
            
    print("\n🎉 Reliability dashboard demo completed!")
    print("🏙️ Just like Mumbai traffic control - continuous monitoring is key!")
    print("💡 Real-time dashboards prevent small issues from becoming big problems!")

async def main():
    """Main demonstration function"""
    await demo_reliability_dashboard()

if __name__ == "__main__":
    asyncio.run(main())
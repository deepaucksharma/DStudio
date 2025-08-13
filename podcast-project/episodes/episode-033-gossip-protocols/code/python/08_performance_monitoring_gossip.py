#!/usr/bin/env python3
"""
Performance Monitoring using Gossip Protocols
==============================================

Zomato Delivery Performance Monitoring: जब thousands of delivery partners हों
तो कैसे real-time में सबका performance monitor करें gossip के through?

This implements a gossip-based performance monitoring system that collects
and aggregates metrics across a distributed system efficiently.

Author: Code Developer Agent
Episode: 33 - Gossip Protocols
"""

import random
import time
import math
import asyncio
import statistics
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class MetricType(Enum):
    """Types of performance metrics"""
    COUNTER = "counter"         # Orders delivered
    GAUGE = "gauge"            # Current orders in queue
    HISTOGRAM = "histogram"     # Delivery times
    RATE = "rate"              # Orders per minute


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    metric_name: str
    metric_type: MetricType
    value: float
    timestamp: float
    source_id: str
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = "count"
    
    def age_seconds(self) -> float:
        """Get age of metric in seconds"""
        return time.time() - self.timestamp


@dataclass
class MetricAggregate:
    """Aggregated metric across multiple sources"""
    metric_name: str
    count: int
    sum_value: float
    min_value: float
    max_value: float
    avg_value: float
    std_dev: float
    percentiles: Dict[str, float] = field(default_factory=dict)
    last_updated: float = 0.0
    sources: Set[str] = field(default_factory=set)
    
    def add_metric(self, metric: PerformanceMetric):
        """Add a metric to this aggregate"""
        self.sources.add(metric.source_id)
        self.last_updated = max(self.last_updated, metric.timestamp)


@dataclass
class AlertRule:
    """Performance alert rule"""
    rule_id: str
    metric_name: str
    condition: str  # "gt", "lt", "eq"
    threshold: float
    level: AlertLevel
    description: str
    cooldown_seconds: float = 300.0  # 5 minutes


@dataclass
class Alert:
    """Performance alert"""
    alert_id: str
    rule_id: str
    metric_name: str
    current_value: float
    threshold: float
    level: AlertLevel
    description: str
    timestamp: float
    source_id: str
    resolved: bool = False


class ZomatoDeliveryAgent:
    """
    Zomato Delivery Agent Performance Monitor
    
    हर delivery agent अपना performance track करता है और
    gossip के through दूसरे agents के साथ share करता है
    """
    
    def __init__(self, agent_id: str, city: str, zone: str):
        self.agent_id = agent_id
        self.city = city
        self.zone = zone
        
        # Performance metrics storage
        self.local_metrics: Dict[str, List[PerformanceMetric]] = {}
        self.aggregated_metrics: Dict[str, MetricAggregate] = {}
        self.metric_retention_hours = 24
        
        # Gossip protocol settings
        self.peers: Set[str] = set()
        self.gossip_fanout = 3
        self.gossip_interval = 10.0  # seconds
        self.metric_batch_size = 50
        
        # Alert system
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Performance simulation
        self.delivery_count = 0
        self.avg_delivery_time = random.uniform(15, 45)  # minutes
        self.current_orders = 0
        self.rating = random.uniform(3.5, 5.0)
        
        # Gossip statistics
        self.metrics_sent = 0
        self.metrics_received = 0
        self.aggregation_rounds = 0
        
        # Initialize default alert rules
        self.setup_default_alert_rules()
        
    def setup_default_alert_rules(self):
        """Setup default performance alert rules"""
        rules = [
            AlertRule(
                rule_id="high_delivery_time",
                metric_name="avg_delivery_time",
                condition="gt",
                threshold=60.0,  # > 60 minutes
                level=AlertLevel.WARNING,
                description="Average delivery time is high"
            ),
            AlertRule(
                rule_id="critical_delivery_time",
                metric_name="avg_delivery_time", 
                condition="gt",
                threshold=90.0,  # > 90 minutes
                level=AlertLevel.CRITICAL,
                description="Average delivery time is critically high"
            ),
            AlertRule(
                rule_id="low_rating",
                metric_name="rating",
                condition="lt",
                threshold=3.0,  # < 3.0 stars
                level=AlertLevel.WARNING,
                description="Agent rating is low"
            ),
            AlertRule(
                rule_id="high_queue",
                metric_name="current_orders",
                condition="gt",
                threshold=5.0,  # > 5 orders in queue
                level=AlertLevel.INFO,
                description="High order queue"
            )
        ]
        
        for rule in rules:
            self.alert_rules[rule.rule_id] = rule
            
    def add_peer(self, peer_id: str):
        """Add peer agent for gossip"""
        self.peers.add(peer_id)
        
    def record_metric(self, metric_name: str, value: float, 
                     metric_type: MetricType, tags: Dict[str, str] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            metric_name=metric_name,
            metric_type=metric_type,
            value=value,
            timestamp=time.time(),
            source_id=self.agent_id,
            tags=tags or {}
        )
        
        if metric_name not in self.local_metrics:
            self.local_metrics[metric_name] = []
            
        self.local_metrics[metric_name].append(metric)
        
        # Clean old metrics
        self.cleanup_old_metrics()
        
        # Check for alerts
        self.check_alert_rules(metric)
        
    def cleanup_old_metrics(self):
        """Remove metrics older than retention period"""
        cutoff_time = time.time() - (self.metric_retention_hours * 3600)
        
        for metric_name in list(self.local_metrics.keys()):
            self.local_metrics[metric_name] = [
                metric for metric in self.local_metrics[metric_name]
                if metric.timestamp > cutoff_time
            ]
            
            if not self.local_metrics[metric_name]:
                del self.local_metrics[metric_name]
                
    def check_alert_rules(self, metric: PerformanceMetric):
        """Check if metric triggers any alert rules"""
        for rule in self.alert_rules.values():
            if rule.metric_name != metric.metric_name:
                continue
                
            # Check if alert is already active (cooldown)
            if rule.rule_id in self.active_alerts:
                last_alert = self.active_alerts[rule.rule_id]
                if time.time() - last_alert.timestamp < rule.cooldown_seconds:
                    continue  # Still in cooldown
                    
            # Evaluate condition
            triggered = False
            if rule.condition == "gt" and metric.value > rule.threshold:
                triggered = True
            elif rule.condition == "lt" and metric.value < rule.threshold:
                triggered = True
            elif rule.condition == "eq" and metric.value == rule.threshold:
                triggered = True
                
            if triggered:
                alert = Alert(
                    alert_id=f"{rule.rule_id}_{int(time.time())}",
                    rule_id=rule.rule_id,
                    metric_name=metric.metric_name,
                    current_value=metric.value,
                    threshold=rule.threshold,
                    level=rule.level,
                    description=rule.description,
                    timestamp=time.time(),
                    source_id=self.agent_id
                )
                
                self.active_alerts[rule.rule_id] = alert
                self.alert_history.append(alert)
                
                print(f"🚨 {rule.level.value.upper()}: {self.agent_id} - {rule.description} "
                      f"(value: {metric.value:.2f}, threshold: {rule.threshold:.2f})")
                      
    def simulate_delivery_activity(self):
        """Simulate delivery agent activity"""
        # Simulate completing a delivery
        if random.random() < 0.3:  # 30% chance
            self.delivery_count += 1
            delivery_time = random.gauss(self.avg_delivery_time, 10)
            delivery_time = max(5, delivery_time)  # Minimum 5 minutes
            
            self.record_metric("deliveries_completed", 1, MetricType.COUNTER)
            self.record_metric("delivery_time", delivery_time, MetricType.HISTOGRAM)
            
            # Update current orders
            self.current_orders = max(0, self.current_orders - 1)
            
        # Simulate receiving new orders
        if random.random() < 0.4:  # 40% chance
            new_orders = random.randint(1, 3)
            self.current_orders += new_orders
            self.record_metric("new_orders", new_orders, MetricType.COUNTER)
            
        # Record current state metrics
        self.record_metric("current_orders", self.current_orders, MetricType.GAUGE)
        self.record_metric("rating", self.rating, MetricType.GAUGE)
        
        # Calculate and record derived metrics
        if self.delivery_count > 0:
            recent_delivery_times = []
            if "delivery_time" in self.local_metrics:
                recent_times = [
                    m.value for m in self.local_metrics["delivery_time"]
                    if time.time() - m.timestamp < 3600  # Last hour
                ]
                if recent_times:
                    avg_time = statistics.mean(recent_times)
                    self.record_metric("avg_delivery_time", avg_time, MetricType.GAUGE)
                    
        # Orders per hour rate
        hour_ago = time.time() - 3600
        if "deliveries_completed" in self.local_metrics:
            recent_deliveries = [
                m for m in self.local_metrics["deliveries_completed"]
                if m.timestamp > hour_ago
            ]
            orders_per_hour = len(recent_deliveries)
            self.record_metric("orders_per_hour", orders_per_hour, MetricType.RATE)
            
    def create_metric_summary(self) -> Dict[str, Any]:
        """Create summary of local metrics for gossip"""
        summary = {}
        
        for metric_name, metrics in self.local_metrics.items():
            if not metrics:
                continue
                
            recent_metrics = [
                m for m in metrics
                if time.time() - m.timestamp < 300  # Last 5 minutes
            ]
            
            if recent_metrics:
                values = [m.value for m in recent_metrics]
                
                summary[metric_name] = {
                    "count": len(values),
                    "sum": sum(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": statistics.mean(values),
                    "last_value": values[-1],
                    "timestamp": recent_metrics[-1].timestamp,
                    "source": self.agent_id
                }
                
                if len(values) > 1:
                    summary[metric_name]["std_dev"] = statistics.stdev(values)
                else:
                    summary[metric_name]["std_dev"] = 0.0
                    
        return summary
        
    def merge_metric_summary(self, peer_summary: Dict[str, Any], peer_id: str):
        """Merge peer's metric summary with local aggregates"""
        for metric_name, peer_data in peer_summary.items():
            if metric_name not in self.aggregated_metrics:
                # Create new aggregate
                self.aggregated_metrics[metric_name] = MetricAggregate(
                    metric_name=metric_name,
                    count=0,
                    sum_value=0.0,
                    min_value=float('inf'),
                    max_value=float('-inf'),
                    avg_value=0.0,
                    std_dev=0.0
                )
                
            aggregate = self.aggregated_metrics[metric_name]
            
            # Update aggregate with peer data
            old_count = aggregate.count
            old_sum = aggregate.sum_value
            
            aggregate.count += peer_data["count"]
            aggregate.sum_value += peer_data["sum"]
            aggregate.min_value = min(aggregate.min_value, peer_data["min"])
            aggregate.max_value = max(aggregate.max_value, peer_data["max"])
            
            # Recalculate average
            if aggregate.count > 0:
                aggregate.avg_value = aggregate.sum_value / aggregate.count
                
            aggregate.sources.add(peer_data["source"])
            aggregate.last_updated = max(aggregate.last_updated, peer_data["timestamp"])
            
        self.metrics_received += len(peer_summary)
        
    def select_gossip_peers(self) -> List[str]:
        """Select peers for gossip based on zone proximity"""
        if not self.peers:
            return []
            
        # Prioritize peers in same zone, then same city
        same_zone_peers = []
        same_city_peers = []
        other_peers = []
        
        for peer_id in self.peers:
            # This is simplified - in real system, would have peer metadata
            if self.zone in peer_id:
                same_zone_peers.append(peer_id)
            elif self.city in peer_id:
                same_city_peers.append(peer_id)
            else:
                other_peers.append(peer_id)
                
        # Select from prioritized groups
        selected = []
        for peer_group in [same_zone_peers, same_city_peers, other_peers]:
            remaining = self.gossip_fanout - len(selected)
            if remaining <= 0:
                break
                
            selected.extend(random.sample(
                peer_group, 
                min(remaining, len(peer_group))
            ))
            
        return selected
        
    def gossip_round(self) -> Dict[str, Dict]:
        """Perform one gossip round for performance metrics"""
        self.aggregation_rounds += 1
        
        # Select peers for this round
        peers = self.select_gossip_peers()
        if not peers:
            return {}
            
        # Create metric summary for transmission
        metric_summary = self.create_metric_summary()
        
        # Create gossip messages
        gossip_messages = {}
        for peer_id in peers:
            gossip_messages[peer_id] = {
                "type": "metric_gossip",
                "sender_id": self.agent_id,
                "city": self.city,
                "zone": self.zone,
                "metrics": metric_summary,
                "timestamp": time.time(),
                "round": self.aggregation_rounds
            }
            
        self.metrics_sent += len(metric_summary) * len(peers)
        return gossip_messages
        
    def process_gossip_message(self, message: Dict) -> bool:
        """Process incoming gossip message"""
        if message["type"] != "metric_gossip":
            return False
            
        sender_id = message["sender_id"]
        peer_metrics = message["metrics"]
        
        # Merge peer metrics with local aggregates
        self.merge_metric_summary(peer_metrics, sender_id)
        
        return True
        
    def get_zone_performance_summary(self) -> Dict:
        """Get performance summary for the zone"""
        zone_summary = {}
        
        for metric_name, aggregate in self.aggregated_metrics.items():
            zone_summary[metric_name] = {
                "avg": aggregate.avg_value,
                "min": aggregate.min_value,
                "max": aggregate.max_value,
                "sources": len(aggregate.sources),
                "last_updated": aggregate.last_updated
            }
            
        return zone_summary
        
    def get_agent_stats(self) -> Dict:
        """Get agent performance statistics"""
        active_alert_count = len(self.active_alerts)
        total_alerts = len(self.alert_history)
        
        return {
            "agent_id": self.agent_id,
            "city": self.city,
            "zone": self.zone,
            "delivery_count": self.delivery_count,
            "current_orders": self.current_orders,
            "rating": self.rating,
            "metrics_tracked": len(self.local_metrics),
            "aggregated_metrics": len(self.aggregated_metrics),
            "active_alerts": active_alert_count,
            "total_alerts": total_alerts,
            "gossip_rounds": self.aggregation_rounds,
            "peers": len(self.peers)
        }


class ZomatoMonitoringNetwork:
    """Zomato Delivery Monitoring Network"""
    
    def __init__(self):
        self.agents: Dict[str, ZomatoDeliveryAgent] = {}
        self.connections: List[Tuple[str, str]] = []
        self.simulation_round = 0
        
    def create_delivery_network(self, agents_per_city: int = 8):
        """Create Zomato delivery agent network"""
        # Indian cities with zones
        cities_zones = [
            ("Mumbai", ["Bandra", "Andheri", "Borivali", "Thane"]),
            ("Delhi", ["CP", "Gurgaon", "Noida", "Dwarka"]),
            ("Bangalore", ["Koramangala", "Whitefield", "JP Nagar", "Electronic City"]),
            ("Hyderabad", ["Hitech City", "Begumpet", "Secunderabad", "Jubilee Hills"]),
            ("Chennai", ["T Nagar", "Anna Nagar", "Velachery", "OMR"])
        ]
        
        agent_counter = 1
        for city, zones in cities_zones:
            for zone in zones:
                for i in range(agents_per_city // len(zones)):
                    agent_id = f"agent_{agent_counter:03d}_{city}_{zone}"
                    self.agents[agent_id] = ZomatoDeliveryAgent(agent_id, city, zone)
                    agent_counter += 1
                    
        # Create zone-based connectivity
        for agent_id, agent in self.agents.items():
            # Connect to other agents in same zone
            same_zone_agents = [
                aid for aid, a in self.agents.items()
                if a.zone == agent.zone and aid != agent_id
            ]
            
            for peer_id in same_zone_agents:
                agent.add_peer(peer_id)
                
            # Connect to some agents in same city
            same_city_agents = [
                aid for aid, a in self.agents.items()
                if a.city == agent.city and a.zone != agent.zone and aid != agent_id
            ]
            
            for peer_id in random.sample(same_city_agents, min(2, len(same_city_agents))):
                agent.add_peer(peer_id)
                
            # Connect to some agents in other cities
            other_city_agents = [
                aid for aid, a in self.agents.items()
                if a.city != agent.city and aid != agent_id
            ]
            
            for peer_id in random.sample(other_city_agents, min(1, len(other_city_agents))):
                agent.add_peer(peer_id)
                
    def simulate_round(self) -> Dict:
        """Simulate one round of monitoring and gossip"""
        self.simulation_round += 1
        
        round_stats = {
            "total_deliveries": 0,
            "total_alerts": 0,
            "gossip_messages": 0,
            "active_agents": 0
        }
        
        # Simulate agent activity
        for agent in self.agents.values():
            agent.simulate_delivery_activity()
            round_stats["total_deliveries"] += agent.delivery_count
            round_stats["total_alerts"] += len(agent.active_alerts)
            
            if agent.current_orders > 0 or agent.delivery_count > 0:
                round_stats["active_agents"] += 1
                
        # Collect gossip messages
        all_gossip_messages = {}
        for agent_id, agent in self.agents.items():
            gossip_messages = agent.gossip_round()
            if gossip_messages:
                all_gossip_messages[agent_id] = gossip_messages
                round_stats["gossip_messages"] += len(gossip_messages)
                
        # Process gossip messages
        for sender_id, peer_messages in all_gossip_messages.items():
            for peer_id, message in peer_messages.items():
                if peer_id in self.agents:
                    self.agents[peer_id].process_gossip_message(message)
                    
        return round_stats
        
    def print_network_status(self):
        """Print current network monitoring status"""
        print(f"\n📊 Monitoring Network Status (Round {self.simulation_round}):")
        
        # Overall statistics
        total_deliveries = sum(agent.delivery_count for agent in self.agents.values())
        total_active_alerts = sum(len(agent.active_alerts) for agent in self.agents.values())
        total_agents = len(self.agents)
        
        print(f"  Total Agents: {total_agents}")
        print(f"  Total Deliveries: {total_deliveries}")
        print(f"  Active Alerts: {total_active_alerts}")
        
        # City-wise performance
        city_stats = {}
        for agent in self.agents.values():
            if agent.city not in city_stats:
                city_stats[agent.city] = {
                    "agents": 0,
                    "deliveries": 0,
                    "alerts": 0,
                    "avg_rating": 0.0
                }
                
            city_stats[agent.city]["agents"] += 1
            city_stats[agent.city]["deliveries"] += agent.delivery_count
            city_stats[agent.city]["alerts"] += len(agent.active_alerts)
            city_stats[agent.city]["avg_rating"] += agent.rating
            
        print(f"\n🏙️  City Performance:")
        for city, stats in city_stats.items():
            avg_rating = stats["avg_rating"] / stats["agents"]
            print(f"  {city}: Agents={stats['agents']}, "
                  f"Deliveries={stats['deliveries']}, "
                  f"Alerts={stats['alerts']}, "
                  f"Avg Rating={avg_rating:.2f}")
                  
        # Top performing agents
        top_agents = sorted(
            self.agents.values(),
            key=lambda a: a.delivery_count,
            reverse=True
        )[:3]
        
        print(f"\n🏆 Top Performing Agents:")
        for i, agent in enumerate(top_agents, 1):
            print(f"  {i}. {agent.agent_id}: "
                  f"Deliveries={agent.delivery_count}, "
                  f"Rating={agent.rating:.2f}, "
                  f"Current Orders={agent.current_orders}")


async def main():
    """Main simulation function"""
    print("🇮🇳 Zomato Performance Monitoring via Gossip Protocol")
    print("=" * 55)
    
    # Create network
    network = ZomatoMonitoringNetwork()
    network.create_delivery_network(8)
    
    print(f"Created monitoring network with {len(network.agents)} delivery agents")
    
    # Simulate for 15 rounds
    for round_num in range(15):
        round_stats = network.simulate_round()
        
        if round_num % 3 == 0:  # Print status every 3 rounds
            network.print_network_status()
            print(f"Round stats: {round_stats}")
            
        await asyncio.sleep(0.7)
        
    # Final performance analysis
    print(f"\n📈 Final Performance Analysis:")
    
    # Network-wide metrics
    all_agents = list(network.agents.values())
    total_deliveries = sum(agent.delivery_count for agent in all_agents)
    total_gossip_rounds = sum(agent.aggregation_rounds for agent in all_agents)
    total_metrics_exchanged = sum(agent.metrics_sent + agent.metrics_received for agent in all_agents)
    
    print(f"Total deliveries completed: {total_deliveries}")
    print(f"Total gossip rounds: {total_gossip_rounds}")
    print(f"Total metrics exchanged: {total_metrics_exchanged}")
    
    # Alert analysis
    all_alerts = []
    for agent in all_agents:
        all_alerts.extend(agent.alert_history)
        
    alert_by_level = {}
    for alert in all_alerts:
        level = alert.level.value
        alert_by_level[level] = alert_by_level.get(level, 0) + 1
        
    print(f"\n🚨 Alert Summary:")
    for level, count in alert_by_level.items():
        print(f"  {level.upper()}: {count} alerts")
        
    # Convergence analysis
    print(f"\n🔄 Gossip Convergence:")
    avg_aggregated_metrics = sum(len(agent.aggregated_metrics) for agent in all_agents) / len(all_agents)
    print(f"Average aggregated metrics per agent: {avg_aggregated_metrics:.1f}")
    
    # Show sample aggregated metrics from one agent
    sample_agent = all_agents[0]
    if sample_agent.aggregated_metrics:
        print(f"\n📋 Sample Aggregated Metrics ({sample_agent.city}):")
        for metric_name, aggregate in list(sample_agent.aggregated_metrics.items())[:3]:
            print(f"  {metric_name}: Avg={aggregate.avg_value:.2f}, "
                  f"Sources={len(aggregate.sources)}, "
                  f"Min={aggregate.min_value:.2f}, "
                  f"Max={aggregate.max_value:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
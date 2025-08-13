#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-scaling for Food Delivery Services
Episode 17: Container Orchestration

यह example दिखाता है कि कैसे Swiggy/Zomato जैसी companies
peak demand के दौरान automatically scale करती हैं।

Real-world scenario: Lunch time में traffic spike handling
"""

import time
import json
import math
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import numpy as np
from collections import deque
import logging
from loguru import logger

class ScalingDirection(Enum):
    """Scaling direction enumeration"""
    UP = "scale_up"
    DOWN = "scale_down"
    STABLE = "stable"

@dataclass
class MetricData:
    """Metric data structure for autoscaling decisions"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    request_rate: float
    response_time: float
    error_rate: float
    queue_length: int

@dataclass
class ScalingEvent:
    """Scaling event record"""
    timestamp: float
    service_name: str
    old_replicas: int
    new_replicas: int
    reason: str
    trigger_metric: str
    trigger_value: float

class SwiggyAutoScaler:
    """
    Swiggy-style Auto Scaler for Food Delivery Services
    Production-ready with Indian peak hour patterns
    """
    
    def __init__(self, service_name: str, namespace: str = "swiggy-prod"):
        self.service_name = service_name
        self.namespace = namespace
        
        # Scaling configuration - Indian context
        self.min_replicas = 2
        self.max_replicas = 50  # Peak dinner time में max scaling
        self.current_replicas = self.min_replicas
        
        # Metric thresholds - Production tuned
        self.cpu_scale_up_threshold = 70.0      # 70% CPU usage
        self.cpu_scale_down_threshold = 30.0    # 30% CPU usage
        self.memory_scale_up_threshold = 80.0   # 80% Memory usage
        self.response_time_threshold = 2000.0   # 2 seconds
        self.error_rate_threshold = 5.0         # 5% error rate
        
        # Indian peak hours configuration
        self.peak_hours = {
            "breakfast": (8, 11),    # 8 AM to 11 AM
            "lunch": (12, 15),       # 12 PM to 3 PM  
            "evening_snacks": (16, 18), # 4 PM to 6 PM
            "dinner": (19, 23)       # 7 PM to 11 PM
        }
        
        # Metric history for trend analysis
        self.metrics_history = deque(maxlen=100)  # Last 100 data points
        self.scaling_events = []
        
        # Scaling cooldown (prevent thrashing)
        self.scale_up_cooldown = 300    # 5 minutes
        self.scale_down_cooldown = 900  # 15 minutes
        self.last_scaling_time = 0
        
        # Monitoring thread control
        self.monitoring_active = False
        self.monitoring_thread = None
        
        logger.info(f"🍔 Swiggy AutoScaler initialized for {service_name}")
        logger.info(f"   Min replicas: {self.min_replicas}, Max replicas: {self.max_replicas}")
    
    def get_current_metrics(self) -> MetricData:
        """
        Get current metrics from monitoring system
        In production, this would query Prometheus/CloudWatch
        """
        # Simulate realistic metrics with Indian traffic patterns
        current_hour = datetime.now().hour
        
        # Base load
        base_cpu = 25.0
        base_memory = 40.0
        base_requests = 10.0
        base_response_time = 500.0
        
        # Peak hour multipliers
        peak_multiplier = 1.0
        for peak_name, (start_hour, end_hour) in self.peak_hours.items():
            if start_hour <= current_hour <= end_hour:
                if peak_name == "lunch":
                    peak_multiplier = 4.5  # Heavy lunch traffic
                elif peak_name == "dinner":
                    peak_multiplier = 5.0  # Heaviest dinner traffic
                elif peak_name == "breakfast":
                    peak_multiplier = 2.5  # Moderate breakfast traffic
                elif peak_name == "evening_snacks":
                    peak_multiplier = 2.0  # Light evening snacks
                break
        
        # Add some randomness for realistic simulation
        import random
        noise = random.uniform(0.8, 1.2)
        
        # Calculate metrics
        cpu_usage = min(95.0, base_cpu * peak_multiplier * noise)
        memory_usage = min(90.0, base_memory * peak_multiplier * 0.8 * noise)
        request_rate = base_requests * peak_multiplier * noise
        response_time = base_response_time * (peak_multiplier * 0.6) * noise
        error_rate = max(0.0, min(15.0, (peak_multiplier - 1) * 2 * noise))
        queue_length = int(request_rate * (response_time / 1000) * peak_multiplier)
        
        return MetricData(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            request_rate=request_rate,
            response_time=response_time,
            error_rate=error_rate,
            queue_length=queue_length
        )
    
    def analyze_scaling_decision(self, metrics: MetricData) -> Tuple[ScalingDirection, str, float]:
        """
        Analyze metrics and decide scaling action
        """
        reasons = []
        
        # CPU-based scaling
        if metrics.cpu_usage > self.cpu_scale_up_threshold:
            reasons.append(f"High CPU usage: {metrics.cpu_usage:.1f}%")
            return ScalingDirection.UP, reasons[0], metrics.cpu_usage
        elif metrics.cpu_usage < self.cpu_scale_down_threshold and len(self.metrics_history) > 5:
            # Check if consistently low for past 5 minutes
            recent_cpu = [m.cpu_usage for m in list(self.metrics_history)[-5:]]
            if all(cpu < self.cpu_scale_down_threshold for cpu in recent_cpu):
                reasons.append(f"Consistently low CPU: {metrics.cpu_usage:.1f}%")
                return ScalingDirection.DOWN, reasons[0], metrics.cpu_usage
        
        # Memory-based scaling
        if metrics.memory_usage > self.memory_scale_up_threshold:
            reasons.append(f"High memory usage: {metrics.memory_usage:.1f}%")
            return ScalingDirection.UP, reasons[0], metrics.memory_usage
        
        # Response time-based scaling
        if metrics.response_time > self.response_time_threshold:
            reasons.append(f"High response time: {metrics.response_time:.0f}ms")
            return ScalingDirection.UP, reasons[0], metrics.response_time
        
        # Error rate-based scaling
        if metrics.error_rate > self.error_rate_threshold:
            reasons.append(f"High error rate: {metrics.error_rate:.1f}%")
            return ScalingDirection.UP, reasons[0], metrics.error_rate
        
        # Queue length-based scaling (Indian traffic pattern specific)
        if metrics.queue_length > 100:  # Queue too long
            reasons.append(f"Long queue: {metrics.queue_length} requests")
            return ScalingDirection.UP, reasons[0], metrics.queue_length
        
        return ScalingDirection.STABLE, "All metrics within normal range", 0.0
    
    def calculate_target_replicas(self, current_metrics: MetricData, 
                                 scaling_direction: ScalingDirection) -> int:
        """
        Calculate target replica count based on metrics and scaling direction
        """
        if scaling_direction == ScalingDirection.STABLE:
            return self.current_replicas
        
        # Calculate scaling factor based on current load
        cpu_factor = current_metrics.cpu_usage / 50.0  # Target 50% CPU
        memory_factor = current_metrics.memory_usage / 60.0  # Target 60% memory
        
        # Use the higher factor for scaling up
        scaling_factor = max(cpu_factor, memory_factor)
        
        if scaling_direction == ScalingDirection.UP:
            # Aggressive scaling during peak hours
            current_hour = datetime.now().hour
            is_peak_hour = any(
                start <= current_hour <= end 
                for start, end in self.peak_hours.values()
            )
            
            if is_peak_hour:
                target_replicas = math.ceil(self.current_replicas * scaling_factor * 1.5)
            else:
                target_replicas = math.ceil(self.current_replicas * scaling_factor)
            
            # Ensure we don't exceed max replicas
            target_replicas = min(target_replicas, self.max_replicas)
            
        else:  # Scale down
            # Conservative scaling down
            target_replicas = max(
                self.min_replicas,
                math.floor(self.current_replicas * 0.7)  # Reduce by 30%
            )
        
        return target_replicas
    
    def check_cooldown(self, scaling_direction: ScalingDirection) -> bool:
        """
        Check if we're in cooldown period to prevent thrashing
        """
        current_time = time.time()
        time_since_last_scaling = current_time - self.last_scaling_time
        
        if scaling_direction == ScalingDirection.UP:
            return time_since_last_scaling >= self.scale_up_cooldown
        else:
            return time_since_last_scaling >= self.scale_down_cooldown
    
    def execute_scaling(self, target_replicas: int, reason: str, 
                       trigger_metric: str, trigger_value: float) -> bool:
        """
        Execute the actual scaling operation
        In production, this would call Kubernetes API
        """
        try:
            old_replicas = self.current_replicas
            
            # Simulate Kubernetes scaling API call
            # kubectl scale deployment {self.service_name} --replicas={target_replicas} -n {self.namespace}
            
            # For demo, we'll just update our internal state
            self.current_replicas = target_replicas
            self.last_scaling_time = time.time()
            
            # Record scaling event
            scaling_event = ScalingEvent(
                timestamp=time.time(),
                service_name=self.service_name,
                old_replicas=old_replicas,
                new_replicas=target_replicas,
                reason=reason,
                trigger_metric=trigger_metric,
                trigger_value=trigger_value
            )
            self.scaling_events.append(scaling_event)
            
            logger.info(f"🎯 Scaling executed: {old_replicas} → {target_replicas} replicas")
            logger.info(f"   Reason: {reason}")
            logger.info(f"   Trigger: {trigger_metric} = {trigger_value}")
            
            return True
        
        except Exception as e:
            logger.error(f"Scaling execution failed: {str(e)}")
            return False
    
    def get_predictive_scaling_factor(self) -> float:
        """
        Predictive scaling based on historical patterns
        Mumbai dinner rush prediction!
        """
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Predict scaling factor based on time patterns
        if 18 <= current_hour <= 19:  # Pre-dinner preparation
            return 1.3  # Scale up 30% in preparation
        elif 11 <= current_hour <= 12:  # Pre-lunch preparation
            return 1.2  # Scale up 20% in preparation
        else:
            return 1.0  # No predictive scaling
    
    def monitor_and_scale(self):
        """
        Main monitoring and scaling loop
        """
        logger.info("🔄 Starting autoscaling monitoring...")
        
        while self.monitoring_active:
            try:
                # Get current metrics
                metrics = self.get_current_metrics()
                self.metrics_history.append(metrics)
                
                # Log current status
                logger.info(f"📊 Metrics - CPU: {metrics.cpu_usage:.1f}%, "
                          f"Memory: {metrics.memory_usage:.1f}%, "
                          f"Requests/s: {metrics.request_rate:.1f}, "
                          f"Response: {metrics.response_time:.0f}ms, "
                          f"Errors: {metrics.error_rate:.1f}%, "
                          f"Queue: {metrics.queue_length}")
                
                # Analyze scaling decision
                scaling_direction, reason, trigger_value = self.analyze_scaling_decision(metrics)
                
                if scaling_direction != ScalingDirection.STABLE:
                    # Check cooldown
                    if self.check_cooldown(scaling_direction):
                        # Calculate target replicas
                        target_replicas = self.calculate_target_replicas(metrics, scaling_direction)
                        
                        # Apply predictive scaling factor
                        predictive_factor = self.get_predictive_scaling_factor()
                        if predictive_factor > 1.0 and scaling_direction == ScalingDirection.UP:
                            target_replicas = math.ceil(target_replicas * predictive_factor)
                            target_replicas = min(target_replicas, self.max_replicas)
                            reason += f" (Predictive scaling: {predictive_factor}x)"
                        
                        if target_replicas != self.current_replicas:
                            # Execute scaling
                            trigger_metric = reason.split(':')[0]
                            success = self.execute_scaling(
                                target_replicas, reason, trigger_metric, trigger_value
                            )
                            
                            if success:
                                logger.info(f"✅ Scaling successful: {self.current_replicas} replicas")
                            else:
                                logger.error("❌ Scaling failed")
                        else:
                            logger.info("ℹ️ Target replicas same as current, no scaling needed")
                    else:
                        logger.info(f"⏳ Scaling skipped due to cooldown period")
                else:
                    logger.debug("✅ All metrics stable, no scaling needed")
                
                # Sleep before next check
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                time.sleep(30)  # Shorter sleep on error
    
    def start_monitoring(self):
        """Start the autoscaling monitoring in background"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.monitor_and_scale, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("🚀 Autoscaling monitoring started")
    
    def stop_monitoring(self):
        """Stop the autoscaling monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("🛑 Autoscaling monitoring stopped")
    
    def get_scaling_report(self) -> Dict:
        """
        Generate scaling report for analysis
        """
        if not self.scaling_events:
            return {"message": "No scaling events recorded"}
        
        # Calculate statistics
        total_scale_ups = sum(1 for event in self.scaling_events 
                            if event.new_replicas > event.old_replicas)
        total_scale_downs = sum(1 for event in self.scaling_events 
                              if event.new_replicas < event.old_replicas)
        
        max_replicas_reached = max(event.new_replicas for event in self.scaling_events)
        min_replicas_reached = min(event.new_replicas for event in self.scaling_events)
        
        # Recent metrics average
        if self.metrics_history:
            recent_metrics = list(self.metrics_history)[-10:]  # Last 10 readings
            avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
            avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        else:
            avg_cpu = avg_memory = avg_response_time = 0
        
        return {
            "service_name": self.service_name,
            "current_replicas": self.current_replicas,
            "total_scaling_events": len(self.scaling_events),
            "scale_ups": total_scale_ups,
            "scale_downs": total_scale_downs,
            "max_replicas_reached": max_replicas_reached,
            "min_replicas_reached": min_replicas_reached,
            "recent_avg_cpu": round(avg_cpu, 1),
            "recent_avg_memory": round(avg_memory, 1),
            "recent_avg_response_time": round(avg_response_time, 1),
            "last_scaling_time": datetime.fromtimestamp(self.last_scaling_time).isoformat() if self.last_scaling_time else None
        }

def simulate_traffic_spike():
    """
    Simulate Indian food delivery traffic patterns
    """
    autoscaler = SwiggyAutoScaler("swiggy-order-service")
    
    print("🍔 Starting Swiggy Auto-scaling Simulation")
    print("Simulating Indian food delivery traffic patterns...")
    print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Start monitoring
    autoscaler.start_monitoring()
    
    try:
        # Let it run for demonstration
        simulation_duration = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < simulation_duration:
            current_time = datetime.now()
            
            # Print status every 30 seconds
            if int(time.time()) % 30 == 0:
                report = autoscaler.get_scaling_report()
                print(f"\\n📊 Status at {current_time.strftime('%H:%M:%S')}:")
                print(f"   Current replicas: {report['current_replicas']}")
                print(f"   Total scaling events: {report['total_scaling_events']}")
                print(f"   Recent CPU: {report['recent_avg_cpu']}%")
                print(f"   Recent Memory: {report['recent_avg_memory']}%")
                print(f"   Recent Response Time: {report['recent_avg_response_time']:.0f}ms")
            
            time.sleep(10)  # Check every 10 seconds for demo
    
    except KeyboardInterrupt:
        print("\\n🛑 Simulation interrupted by user")
    
    finally:
        # Stop monitoring
        autoscaler.stop_monitoring()
        
        # Final report
        print("\\n📋 Final Scaling Report:")
        final_report = autoscaler.get_scaling_report()
        for key, value in final_report.items():
            print(f"   {key}: {value}")
        
        # Show scaling events
        print("\\n📈 Scaling Events:")
        for i, event in enumerate(autoscaler.scaling_events[-5:], 1):  # Last 5 events
            event_time = datetime.fromtimestamp(event.timestamp).strftime('%H:%M:%S')
            print(f"   {i}. {event_time}: {event.old_replicas} → {event.new_replicas} ({event.reason})")

def main():
    """Main demonstration function"""
    
    print("🇮🇳 Welcome to Swiggy Auto-scaling Demo!")
    print("This simulates auto-scaling during Indian peak hours")
    print("=" * 60)
    
    # Run traffic simulation
    simulate_traffic_spike()
    
    print("\\n✅ Auto-scaling demonstration completed!")
    print("In production, this would:")
    print("  - Connect to Kubernetes API for actual scaling")
    print("  - Use Prometheus for real metrics")
    print("  - Integrate with alerting systems")
    print("  - Support multi-region scaling")

if __name__ == "__main__":
    main()

# Production deployment notes:
"""
# Kubernetes HPA configuration:
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: swiggy-order-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: swiggy-order-service
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

# Custom metrics autoscaling:
kubectl apply -f swiggy-hpa.yaml

# Monitor scaling:
kubectl get hpa swiggy-order-service-hpa -w

# Check scaling events:
kubectl describe hpa swiggy-order-service-hpa
"""
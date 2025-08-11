#!/usr/bin/env python3
"""
Queue Depth Monitor - Episode 2
क्यू गहराई मॉनिटर

Real-time queue monitoring with predictive warnings for Indian scale systems
भारतीय पैमाने की प्रणालियों के लिए predictive warnings के साथ real-time queue monitoring

जैसे Mumbai local train stations पर crowd monitoring होती है -
यह भी queue depth monitor करके predict करता है कि कब overflow होगा!

Author: Code Developer Agent A5-C-002
Indian Context: IRCTC queue monitoring, Zomato order queues, festival booking rushes
"""

import time
import threading
import logging
import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import matplotlib.pyplot as plt
from collections import deque
import asyncio
from concurrent.futures import ThreadPoolExecutor
import psutil
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert levels - अलर्ट स्तर"""
    NORMAL = "normal"      # सामान्य - All good
    WARNING = "warning"    # चेतावनी - Getting busy
    CRITICAL = "critical"  # गंभीर - Near capacity
    EMERGENCY = "emergency" # आपातकाल - Overflow imminent

class QueueType(Enum):
    """Types of queues to monitor - निगरानी करने वाले queue के प्रकार"""
    WEB_REQUESTS = "web_requests"        # वेब अनुरोध
    DATABASE_QUERIES = "database_queries" # डेटाबेस queries
    PAYMENT_PROCESSING = "payment_processing" # पेमेंट प्रोसेसिंग
    NOTIFICATION_DELIVERY = "notification_delivery" # नोटिफिकेशन डिलिवरी
    BACKGROUND_JOBS = "background_jobs"   # बैकग्राउंड कार्य
    TATKAL_BOOKING = "tatkal_booking"     # तत्काल बुकिंग
    FOOD_ORDERS = "food_orders"           # खाना ऑर्डर

@dataclass
class QueueMetrics:
    """Queue metrics data point - Queue metrics डेटा पॉइंट"""
    timestamp: datetime
    queue_depth: int
    arrival_rate: float      # items/second
    processing_rate: float   # items/second  
    average_wait_time: float # seconds
    oldest_item_age: float   # seconds
    memory_usage_mb: float
    cpu_usage_percent: float
    
    # Predictive metrics
    predicted_overflow_time: Optional[float] = None  # seconds until overflow
    trend_direction: str = "stable"  # "increasing", "decreasing", "stable"
    confidence_score: float = 0.5    # 0.0 to 1.0

@dataclass
class QueueAlert:
    """Queue alert information - Queue alert जानकारी"""
    alert_id: str
    timestamp: datetime
    queue_name: str
    alert_level: AlertLevel
    current_depth: int
    max_capacity: int
    predicted_overflow_seconds: Optional[float]
    message: str
    
    # Indian context
    regional_impact: List[str] = field(default_factory=list)
    business_impact: str = ""
    suggested_actions: List[str] = field(default_factory=list)

class QueueDepthMonitor:
    """Real-time queue depth monitor - Real-time queue depth monitor"""
    
    def __init__(self, queue_name: str, queue_type: QueueType, max_capacity: int = 1000):
        self.queue_name = queue_name
        self.queue_type = queue_type  
        self.max_capacity = max_capacity
        
        # Monitoring data
        self.metrics_history: deque = deque(maxlen=1000)  # Keep last 1000 data points
        self.current_queue_depth = 0
        self.alerts: List[QueueAlert] = []
        
        # Monitoring controls
        self.is_monitoring = False
        self.monitor_interval = 1.0  # Check every second
        self.monitor_thread = None
        self.alert_callbacks: List[Callable] = []
        
        # Prediction models
        self.trend_window = 60  # seconds for trend analysis
        self.prediction_horizon = 300  # predict 5 minutes ahead
        
        # Indian context settings
        self.peak_hours = [(9, 11), (18, 21)]  # Morning and evening peaks
        self.festival_multiplier = 1.5
        self.regional_load_factors = {
            'mumbai': 1.3,
            'delhi': 1.2, 
            'bangalore': 1.1,
            'tier2': 0.8
        }
        
        # Alert thresholds
        self.thresholds = {
            AlertLevel.WARNING: 0.6,     # 60% capacity
            AlertLevel.CRITICAL: 0.8,    # 80% capacity  
            AlertLevel.EMERGENCY: 0.95   # 95% capacity
        }
        
        logger.info(f"📊 Queue monitor initialized: {queue_name} | Queue monitor शुरू: {queue_name}")
        logger.info(f"   Type: {queue_type.value} | प्रकार: {queue_type.value}")
        logger.info(f"   Max capacity: {max_capacity} | अधिकतम क्षमता: {max_capacity}")
    
    def start_monitoring(self):
        """Start real-time monitoring - Real-time monitoring शुरू करें"""
        if self.is_monitoring:
            logger.warning("Monitoring already running")
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"🔄 Started monitoring {self.queue_name} | Monitoring शुरू: {self.queue_name}")
    
    def stop_monitoring(self):
        """Stop monitoring - Monitoring बंद करें"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info(f"⏹️ Stopped monitoring {self.queue_name} | Monitoring बंद: {self.queue_name}")
    
    def _monitoring_loop(self):
        """Main monitoring loop - मुख्य monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect current metrics
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Analyze trends and predict
                self._analyze_trends(metrics)
                
                # Check for alerts
                self._check_alerts(metrics)
                
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)
    
    def _collect_metrics(self) -> QueueMetrics:
        """Collect current queue metrics - वर्तमान queue metrics एकत्रित करें"""
        
        # Simulate realistic queue behavior
        current_hour = datetime.now().hour
        is_peak_hour = any(start <= current_hour <= end for start, end in self.peak_hours)
        is_festival_season = datetime.now().month in [3, 4, 10, 11]  # Festival months
        
        # Base metrics with some randomness
        base_arrival_rate = self._get_base_arrival_rate()
        base_processing_rate = self._get_base_processing_rate()
        
        # Apply contextual adjustments
        if is_peak_hour:
            arrival_rate = base_arrival_rate * random.uniform(2.0, 3.5)
            processing_rate = base_processing_rate * random.uniform(1.0, 1.2)  # Processing slower during peaks
        else:
            arrival_rate = base_arrival_rate * random.uniform(0.5, 1.5)
            processing_rate = base_processing_rate * random.uniform(0.8, 1.3)
        
        if is_festival_season:
            arrival_rate *= self.festival_multiplier
        
        # Update queue depth based on arrival/processing rates
        net_rate = arrival_rate - processing_rate
        self.current_queue_depth = max(0, self.current_queue_depth + int(net_rate * self.monitor_interval))
        
        # Calculate other metrics
        avg_wait_time = (self.current_queue_depth / max(processing_rate, 1)) if processing_rate > 0 else 0
        oldest_item_age = avg_wait_time * 1.5  # Approximate oldest item age
        
        # System resource usage
        memory_usage = psutil.virtual_memory().percent * 10  # Scale to MB approximation
        cpu_usage = psutil.cpu_percent(interval=None)
        
        metrics = QueueMetrics(
            timestamp=datetime.now(),
            queue_depth=self.current_queue_depth,
            arrival_rate=arrival_rate,
            processing_rate=processing_rate,
            average_wait_time=avg_wait_time,
            oldest_item_age=oldest_item_age,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage
        )
        
        return metrics
    
    def _get_base_arrival_rate(self) -> float:
        """Get base arrival rate based on queue type - Queue type के आधार पर base arrival rate"""
        
        base_rates = {
            QueueType.WEB_REQUESTS: 50.0,          # 50 requests/sec
            QueueType.DATABASE_QUERIES: 30.0,      # 30 queries/sec
            QueueType.PAYMENT_PROCESSING: 10.0,    # 10 payments/sec
            QueueType.NOTIFICATION_DELIVERY: 100.0, # 100 notifications/sec
            QueueType.BACKGROUND_JOBS: 5.0,        # 5 jobs/sec
            QueueType.TATKAL_BOOKING: 200.0,       # 200 bookings/sec (peak)
            QueueType.FOOD_ORDERS: 25.0            # 25 orders/sec
        }
        
        return base_rates.get(self.queue_type, 20.0)
    
    def _get_base_processing_rate(self) -> float:
        """Get base processing rate - Base processing rate प्राप्त करें"""
        
        base_rates = {
            QueueType.WEB_REQUESTS: 45.0,          # Slightly slower than arrival
            QueueType.DATABASE_QUERIES: 35.0,      # Faster processing for DB
            QueueType.PAYMENT_PROCESSING: 8.0,     # Slower due to external calls
            QueueType.NOTIFICATION_DELIVERY: 120.0, # Fast notification sending
            QueueType.BACKGROUND_JOBS: 4.0,        # Slow background processing
            QueueType.TATKAL_BOOKING: 150.0,       # Fast booking processing
            QueueType.FOOD_ORDERS: 20.0            # Order processing time
        }
        
        return base_rates.get(self.queue_type, 18.0)
    
    def _analyze_trends(self, current_metrics: QueueMetrics):
        """Analyze trends and make predictions - Trends का विश्लेषण और भविष्यवाणी करें"""
        
        if len(self.metrics_history) < 10:  # Need minimum data points
            return
        
        # Get recent data for trend analysis
        recent_metrics = list(self.metrics_history)[-min(self.trend_window, len(self.metrics_history)):]
        depths = [m.queue_depth for m in recent_metrics]
        times = [(m.timestamp - recent_metrics[0].timestamp).total_seconds() for m in recent_metrics]
        
        # Calculate trend using linear regression
        if len(depths) >= 2:
            slope, _ = np.polyfit(times, depths, 1)
            
            if slope > 0.5:
                current_metrics.trend_direction = "increasing"
                # Predict overflow time
                if slope > 0:
                    remaining_capacity = self.max_capacity - current_metrics.queue_depth
                    predicted_time = remaining_capacity / slope
                    current_metrics.predicted_overflow_time = predicted_time
                    current_metrics.confidence_score = min(0.9, len(recent_metrics) / 60.0)
            elif slope < -0.5:
                current_metrics.trend_direction = "decreasing"
                current_metrics.confidence_score = min(0.8, len(recent_metrics) / 60.0)
            else:
                current_metrics.trend_direction = "stable"
                current_metrics.confidence_score = 0.5
    
    def _check_alerts(self, metrics: QueueMetrics):
        """Check for alert conditions - Alert conditions की जांच करें"""
        
        capacity_ratio = metrics.queue_depth / self.max_capacity
        current_alert_level = None
        
        # Determine alert level
        if capacity_ratio >= self.thresholds[AlertLevel.EMERGENCY]:
            current_alert_level = AlertLevel.EMERGENCY
        elif capacity_ratio >= self.thresholds[AlertLevel.CRITICAL]:
            current_alert_level = AlertLevel.CRITICAL
        elif capacity_ratio >= self.thresholds[AlertLevel.WARNING]:
            current_alert_level = AlertLevel.WARNING
        
        # Create alert if needed
        if current_alert_level:
            alert = self._create_alert(metrics, current_alert_level)
            self.alerts.append(alert)
            
            # Trigger callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
    
    def _create_alert(self, metrics: QueueMetrics, level: AlertLevel) -> QueueAlert:
        """Create an alert - Alert बनाएं"""
        
        alert_id = f"alert_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Generate contextual message
        messages = {
            AlertLevel.WARNING: f"{self.queue_name} queue at {(metrics.queue_depth/self.max_capacity)*100:.1f}% capacity",
            AlertLevel.CRITICAL: f"CRITICAL: {self.queue_name} queue nearly full at {(metrics.queue_depth/self.max_capacity)*100:.1f}%", 
            AlertLevel.EMERGENCY: f"EMERGENCY: {self.queue_name} queue overflow imminent!"
        }
        
        # Indian context specific suggestions
        suggestions = self._get_indian_context_suggestions(level, metrics)
        business_impact = self._assess_business_impact(level, metrics)
        regional_impact = self._get_regional_impact(level)
        
        alert = QueueAlert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            queue_name=self.queue_name,
            alert_level=level,
            current_depth=metrics.queue_depth,
            max_capacity=self.max_capacity,
            predicted_overflow_seconds=metrics.predicted_overflow_time,
            message=messages[level],
            regional_impact=regional_impact,
            business_impact=business_impact,
            suggested_actions=suggestions
        )
        
        logger.warning(f"🚨 ALERT: {alert.message} | चेतावनी: {alert.message}")
        
        return alert
    
    def _get_indian_context_suggestions(self, level: AlertLevel, metrics: QueueMetrics) -> List[str]:
        """Get India-specific suggestions - भारत-विशिष्ट सुझाव प्राप्त करें"""
        
        suggestions = []
        
        if self.queue_type == QueueType.TATKAL_BOOKING:
            suggestions.extend([
                "Scale up Tatkal booking servers immediately",
                "Enable queue-based booking system",
                "Show estimated wait time to users",
                "तत्काल बुकिंग सर्वर तुरंत बढ़ाएं"
            ])
        elif self.queue_type == QueueType.FOOD_ORDERS:
            suggestions.extend([
                "Notify delivery partners to be ready", 
                "Enable surge pricing if needed",
                "Inform restaurants about order volume",
                "डिलिवरी पार्टनर्स को तैयार रहने को कहें"
            ])
        elif self.queue_type == QueueType.PAYMENT_PROCESSING:
            suggestions.extend([
                "Switch to backup payment gateway",
                "Enable UPI as primary payment method", 
                "Notify users about processing delays",
                "बैकअप पेमेंट गेटवे पर स्विच करें"
            ])
        
        # Common suggestions based on level
        if level == AlertLevel.CRITICAL:
            suggestions.extend([
                "Scale horizontally - add more workers",
                "Enable load shedding for non-critical requests",
                "Alert on-call engineers"
            ])
        elif level == AlertLevel.EMERGENCY:
            suggestions.extend([
                "IMMEDIATE: Scale up capacity by 50%",
                "Activate disaster recovery procedures", 
                "Notify customer support team"
            ])
        
        return suggestions
    
    def _assess_business_impact(self, level: AlertLevel, metrics: QueueMetrics) -> str:
        """Assess business impact - व्यापारिक प्रभाव का आकलन करें"""
        
        if level == AlertLevel.WARNING:
            return "Minor impact - slightly slower response times"
        elif level == AlertLevel.CRITICAL:
            return "Moderate impact - significant delays, user frustration possible"
        elif level == AlertLevel.EMERGENCY:
            if self.queue_type in [QueueType.PAYMENT_PROCESSING, QueueType.TATKAL_BOOKING]:
                return "SEVERE: Revenue loss imminent, critical user flows affected"
            else:
                return "High impact - service degradation, potential customer churn"
        
        return "Low impact"
    
    def _get_regional_impact(self, level: AlertLevel) -> List[str]:
        """Get regional impact assessment - क्षेत्रीय प्रभाव आकलन प्राप्त करें"""
        
        if level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
            # High impact affects all regions
            return ["mumbai", "delhi", "bangalore", "hyderabad", "chennai"]
        elif level == AlertLevel.WARNING:
            # Lower impact affects major metros first
            return ["mumbai", "delhi", "bangalore"]
        
        return []
    
    def add_alert_callback(self, callback: Callable[[QueueAlert], None]):
        """Add alert callback function - Alert callback function जोड़ें"""
        self.alert_callbacks.append(callback)
        logger.info("Alert callback registered")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current queue status - वर्तमान queue स्थिति प्राप्त करें"""
        
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        latest_metrics = self.metrics_history[-1]
        capacity_ratio = latest_metrics.queue_depth / self.max_capacity
        
        # Determine current status
        if capacity_ratio < 0.6:
            status = "HEALTHY"
            status_hindi = "स्वस्थ"
        elif capacity_ratio < 0.8:
            status = "BUSY"
            status_hindi = "व्यस्त"
        elif capacity_ratio < 0.95:
            status = "OVERLOADED"
            status_hindi = "अधिभारित"
        else:
            status = "CRITICAL" 
            status_hindi = "गंभीर"
        
        return {
            "queue_name": self.queue_name,
            "status": f"{status} | {status_hindi}",
            "current_depth": latest_metrics.queue_depth,
            "max_capacity": self.max_capacity,
            "capacity_percentage": capacity_ratio * 100,
            "arrival_rate": latest_metrics.arrival_rate,
            "processing_rate": latest_metrics.processing_rate,
            "average_wait_time_seconds": latest_metrics.average_wait_time,
            "trend": latest_metrics.trend_direction,
            "predicted_overflow_seconds": latest_metrics.predicted_overflow_time,
            "confidence_score": latest_metrics.confidence_score,
            "recent_alerts": len([a for a in self.alerts if a.timestamp > datetime.now() - timedelta(minutes=5)])
        }
    
    def generate_visualization(self, filename: str = None):
        """Generate queue metrics visualization - Queue metrics visualization जेनरेट करें"""
        
        if len(self.metrics_history) < 2:
            logger.warning("Not enough data for visualization")
            return
        
        # Extract data for plotting
        timestamps = [m.timestamp for m in self.metrics_history]
        depths = [m.queue_depth for m in self.metrics_history]
        arrival_rates = [m.arrival_rate for m in self.metrics_history]
        processing_rates = [m.processing_rate for m in self.metrics_history]
        wait_times = [m.average_wait_time for m in self.metrics_history]
        
        # Create time series relative to start
        start_time = timestamps[0]
        time_seconds = [(t - start_time).total_seconds() for t in timestamps]
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Queue Monitor: {self.queue_name} | Queue Monitor: {self.queue_name}', fontsize=16)
        
        # Queue depth over time
        ax1.plot(time_seconds, depths, 'b-', linewidth=2, label='Queue Depth')
        ax1.axhline(y=self.max_capacity, color='r', linestyle='--', alpha=0.7, label='Max Capacity')
        ax1.axhline(y=self.max_capacity*0.8, color='orange', linestyle='--', alpha=0.7, label='Critical (80%)')
        ax1.axhline(y=self.max_capacity*0.6, color='yellow', linestyle='--', alpha=0.7, label='Warning (60%)')
        ax1.set_title('Queue Depth Over Time | समय के साथ Queue की गहराई')
        ax1.set_xlabel('Time (seconds) | समय (सेकंड)')
        ax1.set_ylabel('Queue Depth | Queue की गहराई')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Arrival vs Processing rates
        ax2.plot(time_seconds, arrival_rates, 'g-', linewidth=2, label='Arrival Rate')
        ax2.plot(time_seconds, processing_rates, 'r-', linewidth=2, label='Processing Rate')
        ax2.set_title('Arrival vs Processing Rates | आगमन बनाम प्रसंस्करण दरें')
        ax2.set_xlabel('Time (seconds) | समय (सेकंड)')
        ax2.set_ylabel('Rate (items/sec) | दर (items/सेकंड)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Wait time trend
        ax3.plot(time_seconds, wait_times, 'purple', linewidth=2)
        ax3.set_title('Average Wait Time | औसत प्रतीक्षा समय')
        ax3.set_xlabel('Time (seconds) | समय (सेकंड)')  
        ax3.set_ylabel('Wait Time (seconds) | प्रतीक्षा समय (सेकंड)')
        ax3.grid(True, alpha=0.3)
        
        # Alert timeline
        alert_times = [(a.timestamp - start_time).total_seconds() for a in self.alerts]
        alert_levels = [a.alert_level.value for a in self.alerts]
        
        if alert_times:
            level_colors = {
                'warning': 'yellow',
                'critical': 'orange', 
                'emergency': 'red'
            }
            
            for i, (t, level) in enumerate(zip(alert_times, alert_levels)):
                ax4.axvline(x=t, color=level_colors.get(level, 'gray'), alpha=0.7, linewidth=2)
                ax4.text(t, i*0.1, level, rotation=90, fontsize=8)
        
        ax4.set_title('Alert Timeline | Alert समयावधि')
        ax4.set_xlabel('Time (seconds) | समय (सेकंड)')
        ax4.set_ylabel('Alerts | Alerts')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            logger.info(f"Visualization saved: {filename}")
        
        return fig
    
    def export_metrics(self, filename: str):
        """Export metrics to JSON file - Metrics को JSON file में export करें"""
        
        export_data = {
            'queue_name': self.queue_name,
            'queue_type': self.queue_type.value,
            'max_capacity': self.max_capacity,
            'export_timestamp': datetime.now().isoformat(),
            'metrics': [
                {
                    **asdict(m),
                    'timestamp': m.timestamp.isoformat()
                } for m in self.metrics_history
            ],
            'alerts': [
                {
                    **asdict(a),
                    'timestamp': a.timestamp.isoformat(),
                    'alert_level': a.alert_level.value
                } for a in self.alerts
            ],
            'summary': self.get_current_status()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metrics exported to: {filename}")

def alert_handler_example(alert: QueueAlert):
    """Example alert handler - Alert handler का उदाहरण"""
    
    print(f"\n🚨 QUEUE ALERT RECEIVED | QUEUE ALERT प्राप्त हुआ")
    print(f"   Queue: {alert.queue_name}")
    print(f"   Level: {alert.alert_level.value.upper()}")
    print(f"   Message: {alert.message}")
    print(f"   Current Depth: {alert.current_depth}/{alert.max_capacity}")
    print(f"   Business Impact: {alert.business_impact}")
    
    if alert.predicted_overflow_seconds:
        print(f"   Predicted Overflow: {alert.predicted_overflow_seconds:.1f}s")
    
    if alert.suggested_actions:
        print(f"   Suggested Actions:")
        for action in alert.suggested_actions[:3]:  # Show first 3
            print(f"     • {action}")
    
    print()

def main():
    """Main function to demonstrate queue depth monitoring - मुख्य function"""
    
    print("📊 Queue Depth Monitor Demo - Episode 2")
    print("Queue Depth Monitor डेमो - एपिसोड 2\n")
    
    # Create different types of queue monitors
    monitors = [
        QueueDepthMonitor("IRCTC_Tatkal_Queue", QueueType.TATKAL_BOOKING, 500),
        QueueDepthMonitor("Zomato_Orders_Mumbai", QueueType.FOOD_ORDERS, 300), 
        QueueDepthMonitor("Payment_Gateway", QueueType.PAYMENT_PROCESSING, 200),
        QueueDepthMonitor("Web_API_Requests", QueueType.WEB_REQUESTS, 1000)
    ]
    
    print(f"Created {len(monitors)} queue monitors:")
    for i, monitor in enumerate(monitors, 1):
        print(f"  {i}. {monitor.queue_name} ({monitor.queue_type.value}) - Capacity: {monitor.max_capacity}")
    
    # Add alert handlers
    for monitor in monitors:
        monitor.add_alert_callback(alert_handler_example)
    
    print(f"\n{'='*80}")
    print("STARTING MONITORING | MONITORING शुरू करना")
    print('='*80)
    
    # Start all monitors
    for monitor in monitors:
        monitor.start_monitoring()
        time.sleep(0.5)  # Stagger starts
    
    print("All monitors started. Running for 60 seconds...")
    print("सभी monitors शुरू हो गए। 60 सेकंड के लिए चल रहे हैं...")
    
    # Run monitoring for 60 seconds with periodic status updates
    start_time = time.time()
    duration = 60
    
    try:
        while time.time() - start_time < duration:
            time.sleep(10)  # Update every 10 seconds
            
            elapsed = time.time() - start_time
            remaining = duration - elapsed
            
            print(f"\n⏱️  Time: {elapsed:.0f}s elapsed, {remaining:.0f}s remaining")
            print("Current Status | वर्तमान स्थिति:")
            
            for monitor in monitors:
                status = monitor.get_current_status()
                if 'error' not in status:
                    print(f"   {monitor.queue_name}: {status['capacity_percentage']:.1f}% full, " +
                          f"trend: {status['trend']}, alerts: {status['recent_alerts']}")
    
    except KeyboardInterrupt:
        print("\n🛑 Monitoring interrupted by user | उपयोगकर्ता द्वारा monitoring बाधित")
    
    # Stop all monitors
    print(f"\n{'='*80}")
    print("STOPPING MONITORING AND GENERATING REPORTS")
    print("MONITORING बंद करना और REPORTS जेनरेट करना")
    print('='*80)
    
    for monitor in monitors:
        monitor.stop_monitoring()
    
    # Generate reports and visualizations
    print("\nGenerating reports and visualizations...")
    print("Reports और visualizations जेनरेट कर रहे हैं...")
    
    for i, monitor in enumerate(monitors, 1):
        # Print final status
        print(f"\n📋 FINAL REPORT: {monitor.queue_name}")
        final_status = monitor.get_current_status()
        
        if 'error' not in final_status:
            print(f"   Final Status: {final_status['status']}")
            print(f"   Final Depth: {final_status['current_depth']}/{final_status['max_capacity']}")
            print(f"   Capacity: {final_status['capacity_percentage']:.1f}%") 
            print(f"   Average Wait Time: {final_status['average_wait_time_seconds']:.1f}s")
            print(f"   Total Alerts: {len(monitor.alerts)}")
            
            # Alert breakdown
            alert_counts = {}
            for alert in monitor.alerts:
                level = alert.alert_level.value
                alert_counts[level] = alert_counts.get(level, 0) + 1
            
            if alert_counts:
                print(f"   Alert Breakdown:")
                for level, count in alert_counts.items():
                    print(f"     {level}: {count}")
        
        # Generate visualization
        viz_filename = f"queue_monitor_{monitor.queue_name.lower()}.png"
        try:
            monitor.generate_visualization(viz_filename)
            print(f"   📊 Visualization saved: {viz_filename}")
        except Exception as e:
            print(f"   ⚠️  Visualization failed: {e}")
        
        # Export metrics
        metrics_filename = f"queue_metrics_{monitor.queue_name.lower()}.json"
        try:
            monitor.export_metrics(metrics_filename)
            print(f"   📁 Metrics exported: {metrics_filename}")
        except Exception as e:
            print(f"   ⚠️  Export failed: {e}")
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS | सारांश आंकड़े")
    print('='*80)
    
    total_alerts = sum(len(m.alerts) for m in monitors)
    critical_alerts = sum(len([a for a in m.alerts if a.alert_level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]]) 
                         for m in monitors)
    
    print(f"Total Queue Monitors: {len(monitors)}")
    print(f"Total Alerts Generated: {total_alerts}")
    print(f"Critical/Emergency Alerts: {critical_alerts}")
    print(f"Monitoring Duration: {duration} seconds")
    
    # Queue type analysis
    queue_type_stats = {}
    for monitor in monitors:
        queue_type = monitor.queue_type.value
        if queue_type not in queue_type_stats:
            queue_type_stats[queue_type] = {'monitors': 0, 'alerts': 0}
        
        queue_type_stats[queue_type]['monitors'] += 1
        queue_type_stats[queue_type]['alerts'] += len(monitor.alerts)
    
    print(f"\nQueue Type Analysis:")
    for queue_type, stats in queue_type_stats.items():
        avg_alerts = stats['alerts'] / stats['monitors']
        print(f"   {queue_type}: {stats['monitors']} monitors, {avg_alerts:.1f} avg alerts")
    
    print(f"\n🎉 Queue Depth Monitoring demonstration completed!")
    print("Queue Depth Monitoring प्रदर्शन पूर्ण!")
    
    print(f"\n💡 KEY LEARNINGS | मुख्य शिक्षाएं:")
    print("1. Real-time monitoring prevents queue overflows")
    print("   Real-time monitoring queue overflows को रोकती है")
    print("2. Predictive alerts give time to scale before issues occur")
    print("   Predictive alerts समस्याओं से पहले scale करने का समय देते हैं")
    print("3. Indian context matters - peak hours, festivals affect patterns")
    print("   भारतीय संदर्भ मायने रखता है - peak hours, त्योहार patterns को प्रभावित करते हैं")
    print("4. Different queue types need different monitoring strategies")
    print("   अलग-अलग queue types को अलग monitoring strategies चाहिए")

if __name__ == "__main__":
    main()
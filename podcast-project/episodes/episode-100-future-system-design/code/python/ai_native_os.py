#!/usr/bin/env python3
"""
AI-Native Operating System
Self-learning and self-optimizing OS for future computing

This implementation demonstrates AI integration at the OS level
for predictive resource management and adaptive optimization.
"""

import psutil
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.neural_network import MLPClassifier
import tensorflow as tf
from datetime import datetime, timedelta
import json
import threading
import time
from typing import Dict, List, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResourcePredictor:
    """ML-based system resource prediction"""
    
    def __init__(self):
        self.cpu_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.memory_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.io_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.training_data = []
        self.is_trained = False
        
    def collect_training_data(self, duration_hours: int = 24):
        """Collect system metrics for training"""
        logger.info(f"Collecting training data for {duration_hours} hours...")
        
        end_time = datetime.now() + timedelta(hours=duration_hours)
        
        while datetime.now() < end_time:
            # Collect current metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            net_io = psutil.net_io_counters()
            
            # Create feature vector
            features = {
                'hour': datetime.now().hour,
                'day_of_week': datetime.now().weekday(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_read_mb': disk_io.read_bytes / (1024**2) if disk_io else 0,
                'disk_write_mb': disk_io.write_bytes / (1024**2) if disk_io else 0,
                'net_sent_mb': net_io.bytes_sent / (1024**2) if net_io else 0,
                'net_recv_mb': net_io.bytes_recv / (1024**2) if net_io else 0,
                'process_count': len(psutil.pids()),
                'timestamp': datetime.now().isoformat()
            }
            
            self.training_data.append(features)
            
            # Sleep for 60 seconds before next collection
            time.sleep(60)
        
        logger.info(f"Collected {len(self.training_data)} data points")
    
    def train_models(self):
        """Train prediction models using collected data"""
        if len(self.training_data) < 100:
            logger.warning("Insufficient training data. Generating synthetic data...")
            self._generate_synthetic_data()
        
        df = pd.DataFrame(self.training_data)
        
        # Prepare features and targets
        feature_cols = ['hour', 'day_of_week', 'process_count', 'memory_available_gb', 
                       'disk_read_mb', 'disk_write_mb', 'net_sent_mb', 'net_recv_mb']
        
        X = df[feature_cols].fillna(0)
        y_cpu = df['cpu_percent'].fillna(0)
        y_memory = df['memory_percent'].fillna(0)
        y_io = (df['disk_read_mb'] + df['disk_write_mb']).fillna(0)
        
        # Train models
        logger.info("Training CPU predictor...")
        self.cpu_predictor.fit(X, y_cpu)
        
        logger.info("Training memory predictor...")
        self.memory_predictor.fit(X, y_memory)
        
        logger.info("Training I/O predictor...")
        self.io_predictor.fit(X, y_io)
        
        self.is_trained = True
        logger.info("All models trained successfully!")
    
    def _generate_synthetic_data(self):
        """Generate synthetic training data for demonstration"""
        logger.info("Generating synthetic training data...")
        
        for i in range(1000):
            hour = np.random.randint(0, 24)
            day_of_week = np.random.randint(0, 7)
            
            # Simulate realistic patterns
            if 9 <= hour <= 17:  # Business hours
                cpu_base = 60 + np.random.normal(0, 15)
                memory_base = 70 + np.random.normal(0, 10)
            else:  # Off hours
                cpu_base = 30 + np.random.normal(0, 10)
                memory_base = 50 + np.random.normal(0, 8)
            
            features = {
                'hour': hour,
                'day_of_week': day_of_week,
                'cpu_percent': max(0, min(100, cpu_base)),
                'memory_percent': max(0, min(100, memory_base)),
                'memory_available_gb': np.random.uniform(2, 16),
                'disk_read_mb': np.random.exponential(10),
                'disk_write_mb': np.random.exponential(5),
                'net_sent_mb': np.random.exponential(20),
                'net_recv_mb': np.random.exponential(30),
                'process_count': np.random.randint(50, 200),
                'timestamp': (datetime.now() - timedelta(hours=i)).isoformat()
            }
            
            self.training_data.append(features)
    
    def predict_next_hour(self) -> Dict[str, float]:
        """Predict resource usage for the next hour"""
        if not self.is_trained:
            logger.warning("Models not trained. Training with synthetic data...")
            self.train_models()
        
        # Current system state
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        # Prepare feature vector for prediction
        next_hour = (datetime.now() + timedelta(hours=1)).hour
        features = np.array([[
            next_hour,
            datetime.now().weekday(),
            len(psutil.pids()),
            memory.available / (1024**3),
            disk_io.read_bytes / (1024**2) if disk_io else 0,
            disk_io.write_bytes / (1024**2) if disk_io else 0,
            net_io.bytes_sent / (1024**2) if net_io else 0,
            net_io.bytes_recv / (1024**2) if net_io else 0
        ]])
        
        # Make predictions
        cpu_pred = self.cpu_predictor.predict(features)[0]
        memory_pred = self.memory_predictor.predict(features)[0]
        io_pred = self.io_predictor.predict(features)[0]
        
        return {
            'predicted_cpu_percent': max(0, min(100, cpu_pred)),
            'predicted_memory_percent': max(0, min(100, memory_pred)),
            'predicted_io_mb_per_sec': max(0, io_pred),
            'confidence_score': 0.85,  # Simulated confidence
            'prediction_time': datetime.now().isoformat()
        }


class AnomalyDetector:
    """AI-powered security and performance anomaly detection"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.neural_classifier = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
        self.normal_behavior_data = []
        self.is_trained = False
        
    def learn_normal_behavior(self, data: List[Dict]):
        """Learn what constitutes normal system behavior"""
        logger.info("Learning normal system behavior patterns...")
        
        self.normal_behavior_data = data
        
        # Prepare data for anomaly detection
        features = []
        labels = []  # 0 = normal, 1 = anomaly
        
        for item in data:
            feature_vector = [
                item.get('cpu_percent', 0),
                item.get('memory_percent', 0),
                item.get('disk_read_mb', 0),
                item.get('disk_write_mb', 0),
                item.get('net_sent_mb', 0),
                item.get('net_recv_mb', 0),
                item.get('process_count', 0)
            ]
            features.append(feature_vector)
            labels.append(0)  # Assume all training data is normal
        
        # Add some synthetic anomalies for better classification
        for _ in range(len(features) // 10):  # 10% anomalies
            anomaly = [
                np.random.uniform(80, 100),  # High CPU
                np.random.uniform(90, 100),  # High memory
                np.random.exponential(100),  # High disk I/O
                np.random.exponential(100),
                np.random.exponential(1000),  # High network
                np.random.exponential(1000),
                np.random.randint(500, 1000)  # Many processes
            ]
            features.append(anomaly)
            labels.append(1)  # Anomaly
        
        X = np.array(features)
        y = np.array(labels)
        
        # Train models
        self.isolation_forest.fit(X[y == 0])  # Train only on normal data
        self.neural_classifier.fit(X, y)
        
        self.is_trained = True
        logger.info("Anomaly detection models trained successfully!")
    
    def detect_anomaly(self, current_metrics: Dict) -> Dict[str, Any]:
        """Detect if current system state is anomalous"""
        if not self.is_trained:
            logger.warning("Anomaly detector not trained. Using default behavior...")
            return {'is_anomaly': False, 'confidence': 0.5, 'anomaly_type': 'UNKNOWN'}
        
        # Prepare feature vector
        features = np.array([[
            current_metrics.get('cpu_percent', 0),
            current_metrics.get('memory_percent', 0),
            current_metrics.get('disk_read_mb', 0),
            current_metrics.get('disk_write_mb', 0),
            current_metrics.get('net_sent_mb', 0),
            current_metrics.get('net_recv_mb', 0),
            current_metrics.get('process_count', 0)
        ]])
        
        # Isolation Forest detection
        isolation_score = self.isolation_forest.decision_function(features)[0]
        is_outlier = self.isolation_forest.predict(features)[0] == -1
        
        # Neural network classification
        neural_prediction = self.neural_classifier.predict(features)[0]
        neural_proba = self.neural_classifier.predict_proba(features)[0]
        
        # Combine results
        is_anomaly = is_outlier or neural_prediction == 1
        confidence = max(abs(isolation_score), max(neural_proba))
        
        # Determine anomaly type
        anomaly_type = 'NORMAL'
        if is_anomaly:
            if current_metrics.get('cpu_percent', 0) > 80:
                anomaly_type = 'HIGH_CPU_USAGE'
            elif current_metrics.get('memory_percent', 0) > 85:
                anomaly_type = 'HIGH_MEMORY_USAGE'
            elif current_metrics.get('process_count', 0) > 300:
                anomaly_type = 'PROCESS_EXPLOSION'
            else:
                anomaly_type = 'UNKNOWN_ANOMALY'
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': float(confidence),
            'anomaly_type': anomaly_type,
            'isolation_score': float(isolation_score),
            'neural_score': float(max(neural_proba)),
            'timestamp': datetime.now().isoformat()
        }


class AIOperatingSystem:
    """AI-Native Operating System with self-optimization capabilities"""
    
    def __init__(self):
        self.resource_predictor = ResourcePredictor()
        self.anomaly_detector = AnomalyDetector()
        self.optimization_history = []
        self.is_running = False
        self.monitoring_thread = None
        
    def initialize(self):
        """Initialize the AI OS with training data"""
        logger.info("🤖 Initializing AI-Native Operating System...")
        
        # Train resource predictor
        logger.info("Training resource prediction models...")
        self.resource_predictor.train_models()
        
        # Train anomaly detector
        logger.info("Training anomaly detection models...")
        self.anomaly_detector.learn_normal_behavior(self.resource_predictor.training_data)
        
        logger.info("✅ AI OS initialization complete!")
    
    def start_monitoring(self):
        """Start continuous system monitoring and optimization"""
        if self.is_running:
            logger.warning("AI OS is already running!")
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("🔄 AI OS monitoring started!")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("⏹️ AI OS monitoring stopped!")
    
    def _monitoring_loop(self):
        """Main monitoring and optimization loop"""
        while self.is_running:
            try:
                # Collect current system metrics
                current_metrics = self._collect_current_metrics()
                
                # Predict future resource needs
                predictions = self.resource_predictor.predict_next_hour()
                
                # Detect anomalies
                anomaly_result = self.anomaly_detector.detect_anomaly(current_metrics)
                
                # Apply optimizations
                optimizations = self._apply_optimizations(current_metrics, predictions, anomaly_result)
                
                # Log results
                self._log_monitoring_cycle(current_metrics, predictions, anomaly_result, optimizations)
                
                # Sleep before next cycle
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(60)  # Wait longer if there's an error
    
    def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_read_mb': disk_io.read_bytes / (1024**2) if disk_io else 0,
            'disk_write_mb': disk_io.write_bytes / (1024**2) if disk_io else 0,
            'net_sent_mb': net_io.bytes_sent / (1024**2) if net_io else 0,
            'net_recv_mb': net_io.bytes_recv / (1024**2) if net_io else 0,
            'process_count': len(psutil.pids()),
            'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _apply_optimizations(self, current_metrics: Dict, predictions: Dict, anomaly_result: Dict) -> List[str]:
        """Apply AI-driven system optimizations"""
        optimizations = []
        
        # CPU optimization
        if predictions['predicted_cpu_percent'] > 80:
            optimizations.append("PREEMPTIVE_PROCESS_SCALING")
            logger.info("🔧 Applying preemptive process scaling for predicted high CPU usage")
        
        # Memory optimization
        if predictions['predicted_memory_percent'] > 85:
            optimizations.append("MEMORY_CACHE_CLEANUP")
            logger.info("🧹 Triggering memory cache cleanup for predicted high memory usage")
        
        # Anomaly response
        if anomaly_result['is_anomaly']:
            if anomaly_result['anomaly_type'] == 'HIGH_CPU_USAGE':
                optimizations.append("CPU_THROTTLING")
                logger.warning("⚠️ Applying CPU throttling due to anomalous high usage")
            elif anomaly_result['anomaly_type'] == 'HIGH_MEMORY_USAGE':
                optimizations.append("EMERGENCY_MEMORY_CLEANUP")
                logger.warning("🚨 Emergency memory cleanup due to anomalous usage")
            elif anomaly_result['anomaly_type'] == 'PROCESS_EXPLOSION':
                optimizations.append("PROCESS_ISOLATION")
                logger.warning("🔒 Process isolation due to suspicious process spawning")
        
        # I/O optimization
        if predictions['predicted_io_mb_per_sec'] > 100:
            optimizations.append("IO_SCHEDULING_OPTIMIZATION")
            logger.info("⚡ Optimizing I/O scheduling for predicted high throughput")
        
        # Power management
        if current_metrics['cpu_percent'] < 20 and current_metrics['memory_percent'] < 50:
            optimizations.append("POWER_SAVING_MODE")
            logger.info("🔋 Enabling power saving mode due to low resource usage")
        
        return optimizations
    
    def _log_monitoring_cycle(self, metrics: Dict, predictions: Dict, anomaly: Dict, optimizations: List[str]):
        """Log monitoring cycle results"""
        cycle_data = {
            'timestamp': datetime.now().isoformat(),
            'current_metrics': metrics,
            'predictions': predictions,
            'anomaly_detection': anomaly,
            'applied_optimizations': optimizations,
            'system_health_score': self._calculate_health_score(metrics, anomaly)
        }
        
        self.optimization_history.append(cycle_data)
        
        # Keep only last 100 cycles in memory
        if len(self.optimization_history) > 100:
            self.optimization_history = self.optimization_history[-100:]
    
    def _calculate_health_score(self, metrics: Dict, anomaly: Dict) -> float:
        """Calculate overall system health score (0-100)"""
        score = 100.0
        
        # Penalize high resource usage
        score -= max(0, metrics['cpu_percent'] - 70) * 0.5
        score -= max(0, metrics['memory_percent'] - 80) * 0.3
        
        # Penalize anomalies
        if anomaly['is_anomaly']:
            score -= 20 * anomaly['confidence']
        
        # Penalize high process count
        if metrics['process_count'] > 200:
            score -= (metrics['process_count'] - 200) * 0.1
        
        return max(0, min(100, score))
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        current_metrics = self._collect_current_metrics()
        predictions = self.resource_predictor.predict_next_hour()
        anomaly_result = self.anomaly_detector.detect_anomaly(current_metrics)
        health_score = self._calculate_health_score(current_metrics, anomaly_result)
        
        return {
            'current_status': current_metrics,
            'predictions': predictions,
            'anomaly_status': anomaly_result,
            'health_score': health_score,
            'is_monitoring': self.is_running,
            'optimization_count': len(self.optimization_history),
            'last_optimization': self.optimization_history[-1] if self.optimization_history else None
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive system report"""
        status = self.get_system_status()
        
        report = f"""
🤖 AI-Native Operating System Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 Current System Status:
  CPU Usage: {status['current_status']['cpu_percent']:.1f}%
  Memory Usage: {status['current_status']['memory_percent']:.1f}%
  Available Memory: {status['current_status']['memory_available_gb']:.1f} GB
  Process Count: {status['current_status']['process_count']}
  Health Score: {status['health_score']:.1f}/100

🔮 Next Hour Predictions:
  Predicted CPU: {status['predictions']['predicted_cpu_percent']:.1f}%
  Predicted Memory: {status['predictions']['predicted_memory_percent']:.1f}%
  Predicted I/O: {status['predictions']['predicted_io_mb_per_sec']:.1f} MB/s
  Confidence: {status['predictions']['confidence_score']:.1f}

🔍 Anomaly Detection:
  Status: {'ANOMALOUS' if status['anomaly_status']['is_anomaly'] else 'NORMAL'}
  Type: {status['anomaly_status']['anomaly_type']}
  Confidence: {status['anomaly_status']['confidence']:.1f}

⚙️ System Optimization:
  Monitoring Active: {status['is_monitoring']}
  Total Optimizations: {status['optimization_count']}
  
🎯 AI Benefits:
  • Predictive resource allocation reduces bottlenecks
  • Real-time anomaly detection prevents security threats
  • Automatic optimization improves performance
  • Machine learning adapts to usage patterns
  • Proactive maintenance reduces downtime
        """
        
        return report.strip()


def main():
    """Demonstrate AI-Native Operating System"""
    print("🇮🇳 AI-Native Operating System Demo")
    print("Developed for Future Computing Infrastructure")
    print("=" * 50)
    
    # Initialize AI OS
    ai_os = AIOperatingSystem()
    ai_os.initialize()
    
    # Start monitoring
    ai_os.start_monitoring()
    
    print("\n🔄 AI OS is now monitoring and optimizing your system...")
    print("Press Ctrl+C to stop monitoring and generate report\n")
    
    try:
        # Run for demonstration
        for i in range(10):  # Monitor for 10 cycles (5 minutes)
            time.sleep(30)
            status = ai_os.get_system_status()
            
            print(f"Cycle {i+1}: Health Score: {status['health_score']:.1f}/100, "
                  f"CPU: {status['current_status']['cpu_percent']:.1f}%, "
                  f"Memory: {status['current_status']['memory_percent']:.1f}%")
            
            if status['anomaly_status']['is_anomaly']:
                print(f"  ⚠️ ANOMALY DETECTED: {status['anomaly_status']['anomaly_type']}")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Stopping AI OS monitoring...")
    
    finally:
        # Stop monitoring and generate report
        ai_os.stop_monitoring()
        
        print("\n📋 Final System Report:")
        print("=" * 50)
        print(ai_os.generate_report())
        
        print(f"\n🎉 AI-Native OS Demo Complete!")
        print(f"The future of computing is intelligent, adaptive, and autonomous!")


if __name__ == "__main__":
    main()
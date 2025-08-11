#!/usr/bin/env python3
"""
FIT Platform Mock - Episode 2
FIT प्लेटफॉर्म मॉक implementation

Facebook's FIT (Failure Injection Testing) platform mock for chaos engineering
Facebook के FIT प्लेटफॉर्म जैसा chaos engineering टूल

FIT = Failure Injection Testing - systematic way to inject failures into production
जैसे Mumbai local train में कभी कभी deliberately signals check करते हैं emergency के लिए!

Author: Code Developer Agent A5-C-002
Indian Context: Flipkart GameDay, Zomato Chaos Testing, IRCTC Load Testing
"""

import random
import time
import json
import threading
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from contextlib import contextmanager
import queue
import subprocess
import os

# Setup logging with Hindi support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s | समय: %(asctime)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fit_platform.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class ExperimentStatus(Enum):
    """Experiment status - प्रयोग की स्थिति"""
    PENDING = "pending"       # प्रतीक्षारत - Waiting to be executed
    RUNNING = "running"       # चल रहा है - Currently executing
    COMPLETED = "completed"   # पूर्ण - Successfully completed
    FAILED = "failed"         # असफल - Failed during execution
    ABORTED = "aborted"       # रद्द - Manually aborted
    ROLLBACK = "rollback"     # वापसी - Rolling back changes

class FailureType(Enum):
    """Types of failures to inject - inject करने वाली failures के प्रकार"""
    NETWORK_LATENCY = "network_latency"       # नेटवर्क विलंब
    NETWORK_LOSS = "network_loss"             # नेटवर्क पैकेट लॉस
    SERVICE_DOWN = "service_down"             # सर्विस बंद
    DATABASE_SLOW = "database_slow"           # डेटाबेस धीमा
    MEMORY_LEAK = "memory_leak"               # मेमोरी लीक
    CPU_SPIKE = "cpu_spike"                   # CPU अधिक उपयोग
    DISK_FULL = "disk_full"                   # डिस्क भरा
    DEPENDENCY_TIMEOUT = "dependency_timeout" # निर्भरता timeout

class SafetyLevel(Enum):
    """Safety levels for experiments - प्रयोगों के लिए सुरक्षा स्तर"""
    LOW_RISK = "low_risk"       # कम जोखिम - Non-critical services
    MEDIUM_RISK = "medium_risk" # मध्यम जोखिम - Important but recoverable
    HIGH_RISK = "high_risk"     # उच्च जोखिम - Critical services
    CRITICAL = "critical"       # अति महत्वपूर्ण - Payment/Security services

@dataclass
class TargetService:
    """Target service for chaos experiment - chaos प्रयोग के लिए लक्षित सर्विस"""
    name: str
    environment: str  # "development", "staging", "production"
    region: str       # "mumbai", "delhi", "bangalore", "us-west", etc.
    instances: List[str]
    service_type: str # "web", "api", "database", "cache", "queue"
    criticality: SafetyLevel
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # Indian service naming validation
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Service name cannot be empty")
        
        # Add region-specific validation
        valid_regions = ["mumbai", "delhi", "bangalore", "hyderabad", "chennai", 
                        "pune", "us-west", "us-east", "europe", "singapore"]
        if self.region not in valid_regions:
            logger.warning(f"Unknown region: {self.region}")

@dataclass
class ExperimentConfig:
    """Configuration for chaos experiment - chaos प्रयोग की कॉन्फ़िगरेशन"""
    experiment_id: str
    name: str
    description: str
    failure_type: FailureType
    target_service: TargetService
    duration_seconds: int
    impact_percentage: float  # 0.0 to 1.0 - what % of instances to affect
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Safety controls
    max_duration_seconds: int = 3600  # 1 hour max
    requires_approval: bool = True
    rollback_triggers: List[str] = field(default_factory=lambda: ["error_rate > 5%", "latency > 2s"])
    
    # Scheduling
    start_time: Optional[datetime] = None
    created_by: str = "fit-platform"
    indian_context_notes: str = ""

@dataclass
class ExperimentResult:
    """Results from chaos experiment - chaos प्रयोग के परिणाम"""
    experiment_id: str
    status: ExperimentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0
    
    # Metrics before experiment
    baseline_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Metrics during experiment
    experiment_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Impact analysis
    error_rate_increase: float = 0
    latency_increase: float = 0
    availability_impact: float = 0
    
    # Recovery information
    recovery_time_seconds: Optional[float] = None
    rollback_triggered: bool = False
    rollback_reason: Optional[str] = None
    
    # Lessons learned
    observations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    error_message: Optional[str] = None

class SafetyController:
    """Safety controller for FIT platform - FIT प्लेटफॉर्म के लिए सुरक्षा नियंत्रक"""
    
    def __init__(self):
        self.active_experiments: Dict[str, ExperimentConfig] = {}
        self.safety_lock = threading.Lock()
        self.max_concurrent_experiments = 3
        self.business_hours = (9, 18)  # 9 AM to 6 PM IST
        
        # Indian festival calendar - भारतीय त्योहार कैलेंडर
        self.restricted_periods = [
            "diwali", "holi", "dussehra", "ganesh_chaturthi",
            "eid", "christmas", "new_year", "republic_day",
            "independence_day", "ipl_final", "world_cup_final"
        ]
        
        logger.info("🛡️ Safety Controller initialized | सुरक्षा नियंत्रक शुरू")
    
    def can_run_experiment(self, config: ExperimentConfig) -> tuple[bool, str]:
        """Check if experiment can be safely run - क्या प्रयोग सुरक्षित रूप से चलाया जा सकता है"""
        
        with self.safety_lock:
            # Check concurrent experiments limit
            if len(self.active_experiments) >= self.max_concurrent_experiments:
                return False, f"Maximum concurrent experiments reached: {self.max_concurrent_experiments}"
            
            # Check business hours for production
            if config.target_service.environment == "production":
                current_hour = datetime.now().hour
                if not (self.business_hours[0] <= current_hour <= self.business_hours[1]):
                    return False, "Production experiments only allowed during business hours (9 AM - 6 PM IST)"
            
            # Check criticality vs environment
            if (config.target_service.criticality == SafetyLevel.CRITICAL and 
                config.target_service.environment == "production"):
                return False, "Critical services cannot be tested directly in production"
            
            # Check duration limits
            if config.duration_seconds > config.max_duration_seconds:
                return False, f"Experiment duration exceeds maximum allowed: {config.max_duration_seconds}s"
            
            # Check impact percentage
            if config.impact_percentage > 0.5 and config.target_service.environment == "production":
                return False, "Production experiments cannot affect more than 50% of instances"
            
            # Mumbai monsoon check - during monsoon, reduce chaos frequency
            current_month = datetime.now().month
            if current_month in [6, 7, 8, 9] and config.target_service.region == "mumbai":
                if random.random() < 0.3:  # 30% chance to skip
                    return False, "Monsoon season - reduced experiment frequency for Mumbai region"
            
            # Check for conflicting experiments on same service
            for active_config in self.active_experiments.values():
                if (active_config.target_service.name == config.target_service.name and
                    active_config.target_service.environment == config.target_service.environment):
                    return False, f"Another experiment already running on {config.target_service.name}"
            
            return True, "Safety checks passed"
    
    def register_experiment(self, config: ExperimentConfig):
        """Register active experiment - सक्रिय प्रयोग रजिस्टर करें"""
        with self.safety_lock:
            self.active_experiments[config.experiment_id] = config
            logger.info(f"🔒 Experiment registered: {config.name} | प्रयोग रजिस्टर: {config.name}")
    
    def unregister_experiment(self, experiment_id: str):
        """Unregister completed experiment - पूर्ण प्रयोग अनरजिस्टर करें"""
        with self.safety_lock:
            if experiment_id in self.active_experiments:
                config = self.active_experiments.pop(experiment_id)
                logger.info(f"🔓 Experiment unregistered: {config.name} | प्रयोग अनरजिस्टर: {config.name}")

class MetricsCollector:
    """Collects metrics before, during, and after experiments - प्रयोग के दौरान metrics एकत्रित करता है"""
    
    def __init__(self):
        self.baseline_data = {}
        self.current_data = {}
        
    def collect_baseline_metrics(self, service: TargetService) -> Dict[str, float]:
        """Collect baseline metrics - आधारभूत metrics एकत्रित करें"""
        
        # Simulate collecting real metrics
        # In production, this would integrate with monitoring systems like:
        # - Prometheus, Grafana, DataDog, New Relic
        # - Indian monitoring: Site24x7, ManageEngine
        
        baseline = {
            'response_time_ms': random.uniform(100, 200),
            'error_rate_percentage': random.uniform(0.1, 0.5),
            'requests_per_second': random.uniform(1000, 5000),
            'cpu_utilization_percentage': random.uniform(20, 40),
            'memory_utilization_percentage': random.uniform(30, 50),
            'availability_percentage': 99.9
        }
        
        # Regional adjustments
        if service.region == "mumbai":
            baseline['requests_per_second'] *= 1.5  # Higher traffic in Mumbai
        elif service.region in ["delhi", "bangalore"]:
            baseline['requests_per_second'] *= 1.2
        
        # Service type adjustments
        if service.service_type == "database":
            baseline['response_time_ms'] *= 1.5
        elif service.service_type == "cache":
            baseline['response_time_ms'] *= 0.5
        
        logger.info(f"📊 Baseline metrics collected for {service.name} | Baseline metrics: {service.name}")
        return baseline
    
    def collect_current_metrics(self, service: TargetService) -> Dict[str, float]:
        """Collect current metrics during experiment - प्रयोग के दौरान वर्तमान metrics"""
        
        # Get baseline for comparison
        if service.name not in self.baseline_data:
            self.baseline_data[service.name] = self.collect_baseline_metrics(service)
        
        baseline = self.baseline_data[service.name]
        
        # Simulate degraded metrics during chaos
        current = {
            'response_time_ms': baseline['response_time_ms'] * random.uniform(1.2, 3.0),
            'error_rate_percentage': baseline['error_rate_percentage'] * random.uniform(2.0, 10.0),
            'requests_per_second': baseline['requests_per_second'] * random.uniform(0.7, 0.9),
            'cpu_utilization_percentage': baseline['cpu_utilization_percentage'] * random.uniform(0.8, 1.5),
            'memory_utilization_percentage': baseline['memory_utilization_percentage'] * random.uniform(1.0, 1.3),
            'availability_percentage': baseline['availability_percentage'] * random.uniform(0.95, 0.99)
        }
        
        logger.info(f"📈 Current metrics collected for {service.name} | Current metrics: {service.name}")
        return current

class ChaosInjector:
    """Injects chaos into target services - लक्षित सर्विसों में chaos inject करता है"""
    
    def __init__(self):
        self.active_injections = {}
        self.injection_lock = threading.Lock()
    
    def inject_failure(self, config: ExperimentConfig) -> bool:
        """Inject failure into target service - लक्षित सर्विस में failure inject करें"""
        
        service = config.target_service
        failure_type = config.failure_type
        
        logger.info(f"💥 Injecting {failure_type.value} into {service.name} | "
                   f"{failure_type.value} inject कर रहे हैं: {service.name}")
        
        # In production, this would use tools like:
        # - Chaos Monkey, Gremlin, Litmus Chaos
        # - Traffic control (tc), iptables for network chaos
        # - Kubernetes pod deletion, CPU/Memory stress
        
        try:
            if failure_type == FailureType.NETWORK_LATENCY:
                return self._inject_network_latency(config)
            elif failure_type == FailureType.NETWORK_LOSS:
                return self._inject_network_loss(config)
            elif failure_type == FailureType.SERVICE_DOWN:
                return self._inject_service_down(config)
            elif failure_type == FailureType.DATABASE_SLOW:
                return self._inject_database_slow(config)
            elif failure_type == FailureType.MEMORY_LEAK:
                return self._inject_memory_leak(config)
            elif failure_type == FailureType.CPU_SPIKE:
                return self._inject_cpu_spike(config)
            elif failure_type == FailureType.DISK_FULL:
                return self._inject_disk_full(config)
            elif failure_type == FailureType.DEPENDENCY_TIMEOUT:
                return self._inject_dependency_timeout(config)
            else:
                logger.error(f"Unknown failure type: {failure_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to inject chaos: {e} | Chaos inject नहीं हो सका: {e}")
            return False
    
    def _inject_network_latency(self, config: ExperimentConfig) -> bool:
        """Inject network latency - नेटवर्क विलंब inject करें"""
        
        latency_ms = config.parameters.get('latency_ms', 500)
        
        # For demo, we simulate the command
        # Real command: tc qdisc add dev eth0 root netem delay 500ms
        logger.info(f"🐌 Adding {latency_ms}ms network latency | {latency_ms}ms नेटवर्क विलंब")
        logger.info(f"   Command (simulated): tc qdisc add dev eth0 root netem delay {latency_ms}ms")
        
        with self.injection_lock:
            self.active_injections[config.experiment_id] = {
                'type': 'network_latency',
                'command': f'tc qdisc add dev eth0 root netem delay {latency_ms}ms',
                'cleanup_command': 'tc qdisc del dev eth0 root'
            }
        
        return True
    
    def _inject_network_loss(self, config: ExperimentConfig) -> bool:
        """Inject network packet loss - नेटवर्क पैकेट लॉस inject करें"""
        
        loss_percentage = config.parameters.get('loss_percentage', 10)
        
        logger.info(f"📉 Adding {loss_percentage}% packet loss | {loss_percentage}% पैकेट लॉस")
        logger.info(f"   Command (simulated): tc qdisc add dev eth0 root netem loss {loss_percentage}%")
        
        with self.injection_lock:
            self.active_injections[config.experiment_id] = {
                'type': 'network_loss',
                'command': f'tc qdisc add dev eth0 root netem loss {loss_percentage}%',
                'cleanup_command': 'tc qdisc del dev eth0 root'
            }
        
        return True
    
    def _inject_service_down(self, config: ExperimentConfig) -> bool:
        """Bring down service instances - सर्विस instances बंद करें"""
        
        instances_count = int(len(config.target_service.instances) * config.impact_percentage)
        instances_to_kill = config.target_service.instances[:instances_count]
        
        logger.info(f"🔻 Stopping {instances_count} instances | {instances_count} instances बंद कर रहे हैं")
        
        # For Kubernetes: kubectl delete pod <pod-name>
        # For Docker: docker stop <container-id>
        # For systemd: systemctl stop <service>
        
        for instance in instances_to_kill:
            logger.info(f"   Stopping instance: {instance}")
            logger.info(f"   Command (simulated): kubectl delete pod {instance}")
        
        with self.injection_lock:
            self.active_injections[config.experiment_id] = {
                'type': 'service_down',
                'instances': instances_to_kill,
                'cleanup_command': f'kubectl scale deployment {config.target_service.name} --replicas={len(config.target_service.instances)}'
            }
        
        return True
    
    def _inject_database_slow(self, config: ExperimentConfig) -> bool:
        """Make database queries slow - डेटाबेस queries धीमी करें"""
        
        delay_ms = config.parameters.get('delay_ms', 2000)
        
        logger.info(f"🗄️ Adding {delay_ms}ms database delay | डेटाबेस में {delay_ms}ms विलंब")
        
        # This would typically involve:
        # - Adding artificial delays in application code
        # - Using database proxy to slow queries
        # - Network shaping for database connections
        
        with self.injection_lock:
            self.active_injections[config.experiment_id] = {
                'type': 'database_slow',
                'delay_ms': delay_ms
            }
        
        return True
    
    def _inject_memory_leak(self, config: ExperimentConfig) -> bool:
        """Simulate memory leak - मेमोरी लीक simulate करें"""
        
        memory_mb = config.parameters.get('memory_mb', 1000)
        
        logger.info(f"🧠 Consuming {memory_mb}MB memory | {memory_mb}MB मेमोरी consume कर रहे हैं")
        
        with self.injection_lock:
            self.active_injections[config.experiment_id] = {
                'type': 'memory_leak',
                'memory_mb': memory_mb,
                'command': f'stress-ng --vm 1 --vm-bytes {memory_mb}M --timeout {config.duration_seconds}s'
            }
        
        return True
    
    def _inject_cpu_spike(self, config: ExperimentConfig) -> bool:
        """Create CPU spike - CPU spike बनाएं"""
        
        cpu_percentage = config.parameters.get('cpu_percentage', 80)
        
        logger.info(f"⚡ Creating {cpu_percentage}% CPU load | {cpu_percentage}% CPU लोड")
        
        with self.injection_lock:
            self.active_injections[config.experiment_id] = {
                'type': 'cpu_spike',
                'cpu_percentage': cpu_percentage,
                'command': f'stress-ng --cpu 4 --cpu-load {cpu_percentage} --timeout {config.duration_seconds}s'
            }
        
        return True
    
    def _inject_disk_full(self, config: ExperimentConfig) -> bool:
        """Fill up disk space - डिस्क स्पेस भरें"""
        
        disk_size_mb = config.parameters.get('disk_size_mb', 5000)
        
        logger.info(f"💽 Filling {disk_size_mb}MB disk space | {disk_size_mb}MB डिस्क भर रहे हैं")
        
        with self.injection_lock:
            self.active_injections[config.experiment_id] = {
                'type': 'disk_full',
                'disk_size_mb': disk_size_mb,
                'command': f'dd if=/dev/zero of=/tmp/chaos_fill_{config.experiment_id} bs=1M count={disk_size_mb}',
                'cleanup_command': f'rm -f /tmp/chaos_fill_{config.experiment_id}'
            }
        
        return True
    
    def _inject_dependency_timeout(self, config: ExperimentConfig) -> bool:
        """Cause dependency timeouts - dependency timeouts का कारण बनें"""
        
        timeout_ms = config.parameters.get('timeout_ms', 5000)
        
        logger.info(f"🔗 Creating {timeout_ms}ms dependency timeouts | {timeout_ms}ms dependency timeouts")
        
        with self.injection_lock:
            self.active_injections[config.experiment_id] = {
                'type': 'dependency_timeout',
                'timeout_ms': timeout_ms
            }
        
        return True
    
    def cleanup_injection(self, experiment_id: str) -> bool:
        """Clean up injected chaos - inject किया गया chaos साफ करें"""
        
        with self.injection_lock:
            if experiment_id not in self.active_injections:
                return True
            
            injection = self.active_injections[experiment_id]
            logger.info(f"🧹 Cleaning up {injection['type']} injection | {injection['type']} injection साफ कर रहे हैं")
            
            # Execute cleanup command if present
            if 'cleanup_command' in injection:
                logger.info(f"   Cleanup command (simulated): {injection['cleanup_command']}")
            
            del self.active_injections[experiment_id]
            
        return True

class FITPlatform:
    """Main FIT Platform class - मुख्य FIT प्लेटफॉर्म क्लास"""
    
    def __init__(self):
        self.safety_controller = SafetyController()
        self.metrics_collector = MetricsCollector()
        self.chaos_injector = ChaosInjector()
        self.experiment_results: Dict[str, ExperimentResult] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        logger.info("🚀 FIT Platform initialized | FIT प्लेटफॉर्म शुरू")
        logger.info("   Safety controls enabled | सुरक्षा नियंत्रण सक्षम")
    
    def create_experiment(self, 
                         name: str,
                         description: str,
                         target_service: TargetService,
                         failure_type: FailureType,
                         duration_seconds: int,
                         impact_percentage: float,
                         parameters: Dict[str, Any] = None,
                         indian_context_notes: str = "") -> ExperimentConfig:
        """Create new chaos experiment - नया chaos प्रयोग बनाएं"""
        
        experiment_id = f"exp_{uuid.uuid4().hex[:8]}"
        
        config = ExperimentConfig(
            experiment_id=experiment_id,
            name=name,
            description=description,
            failure_type=failure_type,
            target_service=target_service,
            duration_seconds=duration_seconds,
            impact_percentage=impact_percentage,
            parameters=parameters or {},
            indian_context_notes=indian_context_notes
        )
        
        logger.info(f"📋 Created experiment: {name} | प्रयोग बनाया: {name}")
        logger.info(f"   ID: {experiment_id}")
        logger.info(f"   Target: {target_service.name} ({target_service.environment})")
        logger.info(f"   Type: {failure_type.value}")
        logger.info(f"   Duration: {duration_seconds}s")
        logger.info(f"   Impact: {impact_percentage*100:.1f}%")
        
        return config
    
    def run_experiment(self, config: ExperimentConfig) -> Future[ExperimentResult]:
        """Run chaos experiment asynchronously - chaos प्रयोग async में चलाएं"""
        
        return self.executor.submit(self._execute_experiment, config)
    
    def _execute_experiment(self, config: ExperimentConfig) -> ExperimentResult:
        """Execute single experiment - एकल प्रयोग निष्पादित करें"""
        
        result = ExperimentResult(
            experiment_id=config.experiment_id,
            status=ExperimentStatus.PENDING,
            start_time=datetime.now()
        )
        
        try:
            logger.info(f"🧪 Starting experiment: {config.name} | प्रयोग शुरू: {config.name}")
            
            # Safety check
            can_run, reason = self.safety_controller.can_run_experiment(config)
            if not can_run:
                result.status = ExperimentStatus.FAILED
                result.error_message = f"Safety check failed: {reason}"
                logger.error(f"❌ Safety check failed: {reason} | सुरक्षा जांच असफल: {reason}")
                return result
            
            # Register with safety controller
            self.safety_controller.register_experiment(config)
            
            # Collect baseline metrics
            result.status = ExperimentStatus.RUNNING
            logger.info("📊 Collecting baseline metrics | Baseline metrics एकत्रित कर रहे हैं")
            result.baseline_metrics = self.metrics_collector.collect_baseline_metrics(config.target_service)
            
            # Inject chaos
            logger.info("💥 Injecting chaos | Chaos inject कर रहे हैं")
            if not self.chaos_injector.inject_failure(config):
                result.status = ExperimentStatus.FAILED
                result.error_message = "Failed to inject chaos"
                return result
            
            # Monitor during experiment
            start_monitoring = time.time()
            monitoring_duration = config.duration_seconds
            
            logger.info(f"⏱️ Monitoring for {monitoring_duration} seconds | {monitoring_duration} सेकंड निगरानी")
            
            # Simulate monitoring loop
            monitor_interval = min(30, monitoring_duration / 4)  # Check every 30s or 4 times
            elapsed = 0
            
            while elapsed < monitoring_duration:
                time.sleep(min(monitor_interval, monitoring_duration - elapsed))
                elapsed = time.time() - start_monitoring
                
                # Collect current metrics
                current_metrics = self.metrics_collector.collect_current_metrics(config.target_service)
                result.experiment_metrics.update(current_metrics)
                
                # Check rollback triggers
                if self._should_rollback(result, config):
                    logger.warning("🚨 Rollback triggered | Rollback trigger हुआ")
                    result.rollback_triggered = True
                    result.rollback_reason = "Metrics exceeded safety thresholds"
                    break
                
                progress = (elapsed / monitoring_duration) * 100
                logger.info(f"📈 Experiment progress: {progress:.1f}% | प्रगति: {progress:.1f}%")
            
            # Cleanup chaos injection
            logger.info("🧹 Cleaning up chaos injection | Chaos injection साफ कर रहे हैं")
            self.chaos_injector.cleanup_injection(config.experiment_id)
            
            # Wait for recovery and collect post-experiment metrics
            logger.info("🔄 Waiting for service recovery | सर्विस recovery का इंतज़ार")
            recovery_start = time.time()
            time.sleep(30)  # Wait for recovery
            recovery_end = time.time()
            
            result.recovery_time_seconds = recovery_end - recovery_start
            
            # Calculate impact
            self._calculate_impact(result)
            
            # Generate observations and recommendations
            self._generate_insights(result, config)
            
            # Mark as completed
            result.status = ExperimentStatus.COMPLETED
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            
            logger.info(f"✅ Experiment completed: {config.name} | प्रयोग पूर्ण: {config.name}")
            
        except Exception as e:
            result.status = ExperimentStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.now()
            logger.error(f"❌ Experiment failed: {e} | प्रयोग असफल: {e}")
            
            # Ensure cleanup happens even on failure
            try:
                self.chaos_injector.cleanup_injection(config.experiment_id)
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")
        
        finally:
            # Unregister from safety controller
            self.safety_controller.unregister_experiment(config.experiment_id)
            
            # Store result
            self.experiment_results[config.experiment_id] = result
        
        return result
    
    def _should_rollback(self, result: ExperimentResult, config: ExperimentConfig) -> bool:
        """Check if experiment should be rolled back - क्या प्रयोग को rollback करना चाहिए"""
        
        if not result.experiment_metrics or not result.baseline_metrics:
            return False
        
        # Check error rate threshold
        current_error_rate = result.experiment_metrics.get('error_rate_percentage', 0)
        baseline_error_rate = result.baseline_metrics.get('error_rate_percentage', 0)
        
        if current_error_rate > baseline_error_rate * 10:  # 10x increase
            logger.warning(f"Error rate spiked: {current_error_rate:.2f}% vs baseline {baseline_error_rate:.2f}%")
            return True
        
        # Check response time threshold
        current_latency = result.experiment_metrics.get('response_time_ms', 0)
        baseline_latency = result.baseline_metrics.get('response_time_ms', 0)
        
        if current_latency > baseline_latency * 5:  # 5x increase
            logger.warning(f"Latency spiked: {current_latency:.1f}ms vs baseline {baseline_latency:.1f}ms")
            return True
        
        # Check availability threshold
        current_availability = result.experiment_metrics.get('availability_percentage', 100)
        
        if current_availability < 95.0:  # Below 95%
            logger.warning(f"Availability dropped: {current_availability:.2f}%")
            return True
        
        return False
    
    def _calculate_impact(self, result: ExperimentResult):
        """Calculate experiment impact - प्रयोग का प्रभाव गणना करें"""
        
        if not result.experiment_metrics or not result.baseline_metrics:
            return
        
        # Error rate impact
        current_error = result.experiment_metrics.get('error_rate_percentage', 0)
        baseline_error = result.baseline_metrics.get('error_rate_percentage', 0)
        result.error_rate_increase = current_error - baseline_error
        
        # Latency impact
        current_latency = result.experiment_metrics.get('response_time_ms', 0)
        baseline_latency = result.baseline_metrics.get('response_time_ms', 0)
        result.latency_increase = current_latency - baseline_latency
        
        # Availability impact
        current_availability = result.experiment_metrics.get('availability_percentage', 100)
        baseline_availability = result.baseline_metrics.get('availability_percentage', 100)
        result.availability_impact = baseline_availability - current_availability
    
    def _generate_insights(self, result: ExperimentResult, config: ExperimentConfig):
        """Generate insights and recommendations - अंतर्दृष्टि और सिफारिशें बनाएं"""
        
        # Observations based on results
        observations = []
        recommendations = []
        
        if result.error_rate_increase > 5:
            observations.append(f"Error rate increased by {result.error_rate_increase:.2f}%")
            recommendations.append("Implement better error handling and circuit breakers")
        
        if result.latency_increase > 500:
            observations.append(f"Response time increased by {result.latency_increase:.1f}ms")
            recommendations.append("Add caching layer and optimize slow queries")
        
        if result.availability_impact > 1:
            observations.append(f"Availability dropped by {result.availability_impact:.2f}%")
            recommendations.append("Increase redundancy and implement auto-scaling")
        
        if result.recovery_time_seconds and result.recovery_time_seconds > 60:
            observations.append(f"Service took {result.recovery_time_seconds:.1f}s to recover")
            recommendations.append("Improve health checks and reduce recovery time")
        
        # Indian context specific insights
        if config.target_service.region in ["mumbai", "delhi"]:
            recommendations.append("Consider Mumbai/Delhi traffic patterns during peak hours")
        
        if config.target_service.service_type == "web":
            recommendations.append("Add CDN support for better performance across Indian regions")
        
        # Default insights if no major issues
        if not observations:
            observations.append("Service handled the chaos experiment well")
            recommendations.append("System shows good resilience - continue regular chaos testing")
        
        result.observations = observations
        result.recommendations = recommendations
    
    def get_experiment_result(self, experiment_id: str) -> Optional[ExperimentResult]:
        """Get experiment result - प्रयोग का परिणाम प्राप्त करें"""
        return self.experiment_results.get(experiment_id)
    
    def list_experiments(self) -> List[ExperimentResult]:
        """List all experiments - सभी प्रयोग सूची"""
        return list(self.experiment_results.values())
    
    def abort_experiment(self, experiment_id: str) -> bool:
        """Abort running experiment - चल रहे प्रयोग को रद्द करें"""
        
        if experiment_id in self.experiment_results:
            result = self.experiment_results[experiment_id]
            if result.status == ExperimentStatus.RUNNING:
                # Cleanup chaos injection
                self.chaos_injector.cleanup_injection(experiment_id)
                
                # Update status
                result.status = ExperimentStatus.ABORTED
                result.end_time = datetime.now()
                
                # Unregister from safety controller
                self.safety_controller.unregister_experiment(experiment_id)
                
                logger.info(f"🛑 Experiment aborted: {experiment_id} | प्रयोग रद्द: {experiment_id}")
                return True
        
        return False
    
    def generate_report(self, experiment_id: str) -> Dict[str, Any]:
        """Generate detailed experiment report - विस्तृत प्रयोग रिपोर्ट"""
        
        result = self.get_experiment_result(experiment_id)
        if not result:
            return {"error": "Experiment not found"}
        
        report = {
            "experiment_id": result.experiment_id,
            "status": result.status.value,
            "duration_seconds": result.duration_seconds,
            "start_time": result.start_time.isoformat(),
            "end_time": result.end_time.isoformat() if result.end_time else None,
            
            "impact_analysis": {
                "error_rate_increase_percentage": result.error_rate_increase,
                "latency_increase_ms": result.latency_increase,
                "availability_impact_percentage": result.availability_impact,
                "recovery_time_seconds": result.recovery_time_seconds
            },
            
            "metrics": {
                "baseline": result.baseline_metrics,
                "during_experiment": result.experiment_metrics
            },
            
            "insights": {
                "observations": result.observations,
                "recommendations": result.recommendations
            },
            
            "safety": {
                "rollback_triggered": result.rollback_triggered,
                "rollback_reason": result.rollback_reason
            },
            
            "report_generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def shutdown(self):
        """Shutdown FIT platform - FIT प्लेटफॉर्म बंद करें"""
        
        logger.info("🛑 Shutting down FIT Platform | FIT प्लेटफॉर्म बंद कर रहे हैं")
        
        # Abort all running experiments
        for experiment_id, result in self.experiment_results.items():
            if result.status == ExperimentStatus.RUNNING:
                self.abort_experiment(experiment_id)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("✅ FIT Platform shutdown complete | FIT प्लेटफॉर्म बंद पूर्ण")

def main():
    """Main function to demonstrate FIT platform - मुख्य function"""
    
    print("🧪 FIT Platform Mock Demo - Episode 2")
    print("FIT प्लेटफॉर्म मॉक डेमो - एपिसोड 2\n")
    
    # Initialize FIT platform
    fit_platform = FITPlatform()
    
    # Create target services
    flipkart_api = TargetService(
        name="flipkart_product_api",
        environment="staging",
        region="mumbai",
        instances=["api-1", "api-2", "api-3", "api-4", "api-5"],
        service_type="api",
        criticality=SafetyLevel.MEDIUM_RISK,
        dependencies=["product_database", "recommendation_service"]
    )
    
    zomato_orders = TargetService(
        name="zomato_order_service",
        environment="staging", 
        region="bangalore",
        instances=["order-1", "order-2", "order-3"],
        service_type="web",
        criticality=SafetyLevel.HIGH_RISK,
        dependencies=["payment_gateway", "delivery_service"]
    )
    
    irctc_booking = TargetService(
        name="irctc_booking_service",
        environment="production",
        region="delhi",
        instances=["booking-1", "booking-2"],
        service_type="web", 
        criticality=SafetyLevel.CRITICAL,
        dependencies=["ticket_database", "payment_service"]
    )
    
    # Define experiments
    experiments = [
        # 1. Network latency experiment on Flipkart API
        fit_platform.create_experiment(
            name="Flipkart API Network Latency",
            description="Test how Flipkart product API handles network latency",
            target_service=flipkart_api,
            failure_type=FailureType.NETWORK_LATENCY,
            duration_seconds=300,  # 5 minutes
            impact_percentage=0.4,  # 40% of instances
            parameters={"latency_ms": 1000},
            indian_context_notes="Testing during non-peak hours to avoid Big Billion Days impact"
        ),
        
        # 2. Database slowness on Zomato orders
        fit_platform.create_experiment(
            name="Zomato Database Slowness",
            description="Test order service resilience with slow database",
            target_service=zomato_orders,
            failure_type=FailureType.DATABASE_SLOW,
            duration_seconds=180,  # 3 minutes
            impact_percentage=0.3,  # 30% impact
            parameters={"delay_ms": 5000},
            indian_context_notes="Simulating lunch rush database load in Bangalore"
        ),
        
        # 3. CPU spike experiment
        fit_platform.create_experiment(
            name="Service CPU Spike Test",
            description="Test service behavior under high CPU load",
            target_service=flipkart_api,
            failure_type=FailureType.CPU_SPIKE,
            duration_seconds=120,  # 2 minutes
            impact_percentage=0.2,  # 20% impact
            parameters={"cpu_percentage": 85},
            indian_context_notes="Testing autoscaling during festival season load"
        )
    ]
    
    print(f"Created {len(experiments)} chaos experiments:")
    for i, exp in enumerate(experiments, 1):
        print(f"  {i}. {exp.name} ({exp.failure_type.value})")
    
    print(f"\n{'='*80}")
    print("RUNNING EXPERIMENTS | प्रयोग चलाए जा रहे हैं")
    print('='*80)
    
    # Run experiments
    futures = []
    for experiment in experiments:
        print(f"\n🚀 Starting: {experiment.name}")
        future = fit_platform.run_experiment(experiment)
        futures.append((experiment, future))
        time.sleep(2)  # Stagger experiment starts
    
    # Wait for all experiments to complete
    results = []
    for experiment, future in futures:
        print(f"\n⏳ Waiting for: {experiment.name}")
        try:
            result = future.result(timeout=600)  # 10 minutes max
            results.append(result)
            
            print(f"✅ Completed: {experiment.name}")
            print(f"   Status: {result.status.value}")
            print(f"   Duration: {result.duration_seconds:.1f}s")
            if result.error_message:
                print(f"   Error: {result.error_message}")
            
        except Exception as e:
            print(f"❌ Failed: {experiment.name} - {e}")
    
    # Generate detailed reports
    print(f"\n{'='*80}")
    print("EXPERIMENT REPORTS | प्रयोग रिपोर्ट")
    print('='*80)
    
    for result in results:
        if result.status == ExperimentStatus.COMPLETED:
            report = fit_platform.generate_report(result.experiment_id)
            
            print(f"\n📊 REPORT: {result.experiment_id}")
            print(f"   Duration: {report['duration_seconds']:.1f}s")
            
            # Impact analysis
            impact = report['impact_analysis']
            print(f"   Error Rate Impact: {impact['error_rate_increase_percentage']:.2f}%")
            print(f"   Latency Impact: {impact['latency_increase_ms']:.1f}ms")
            print(f"   Availability Impact: {impact['availability_impact_percentage']:.2f}%")
            print(f"   Recovery Time: {impact['recovery_time_seconds']:.1f}s")
            
            # Insights
            insights = report['insights']
            print(f"   Observations: {len(insights['observations'])}")
            for obs in insights['observations']:
                print(f"     • {obs}")
            
            print(f"   Recommendations: {len(insights['recommendations'])}")
            for rec in insights['recommendations'][:2]:  # Show first 2
                print(f"     • {rec}")
            
            # Save detailed report to file
            report_file = f"fit_report_{result.experiment_id}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"   📁 Detailed report saved: {report_file}")
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY | सारांश")
    print('='*80)
    
    total_experiments = len(results)
    completed_experiments = len([r for r in results if r.status == ExperimentStatus.COMPLETED])
    failed_experiments = len([r for r in results if r.status == ExperimentStatus.FAILED])
    
    print(f"   Total Experiments: {total_experiments}")
    print(f"   Completed: {completed_experiments}")
    print(f"   Failed: {failed_experiments}")
    print(f"   Success Rate: {(completed_experiments/max(total_experiments,1))*100:.1f}%")
    
    # Shutdown platform
    fit_platform.shutdown()
    
    print(f"\n🎉 FIT Platform demo completed!")
    print(f"   All experiment reports saved as JSON files")
    print(f"   सभी प्रयोग रिपोर्ट JSON फाइलों में सेव हो गई")

if __name__ == "__main__":
    main()
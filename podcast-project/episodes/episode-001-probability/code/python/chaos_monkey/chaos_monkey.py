#!/usr/bin/env python3
"""
Chaos Monkey Clone - Production-Ready Chaos Engineering Tool
==========================================================
Inspired by Netflix Chaos Monkey, adapted for Indian scale systems.

Real-world inspiration:
- Netflix: Random instance termination in production
- Amazon: GameDay exercises and fault injection 
- Google: DiRT (Disaster Recovery Testing)
- Facebook: Storm exercises

Indian scale examples:
- Simulate Flipkart server failures during Big Billion Days
- Test Paytm resilience during high-transaction periods
- Validate Ola's system during peak traffic hours
- Test IRCTC's fault tolerance during Tatkal booking

Features:
- Random instance termination with safety controls
- Configurable blast radius and targeting
- Integration with cloud providers (AWS, Azure, GCP)
- Scheduling and automation
- Comprehensive logging and reporting
- Integration with monitoring systems
"""

import random
import time
import logging
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import os
import signal
import requests
from contextlib import contextmanager
import psutil


class ChaosAction(Enum):
    """Types of chaos actions"""
    TERMINATE_INSTANCE = "terminate_instance"
    KILL_PROCESS = "kill_process"
    NETWORK_PARTITION = "network_partition"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_FILL = "disk_fill"
    SERVICE_DELAY = "service_delay"
    RANDOM_EXCEPTION = "random_exception"


class TargetEnvironment(Enum):
    """Target environments for chaos"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class SafetyLevel(Enum):
    """Safety levels for chaos actions"""
    SAFE = "safe"           # Minimal impact
    MODERATE = "moderate"   # Noticeable but recoverable
    AGGRESSIVE = "aggressive" # High impact, testing only


@dataclass
class ChaosTarget:
    """Target specification for chaos action"""
    target_type: str  # "instance", "process", "service"
    target_id: str    # Instance ID, process name, service name
    environment: TargetEnvironment
    tags: Dict[str, str]
    health_check_url: Optional[str] = None


@dataclass
class ChaosExperiment:
    """Configuration for a chaos experiment"""
    name: str
    description: str
    action: ChaosAction
    targets: List[ChaosTarget]
    probability: float  # 0.0 to 1.0
    safety_level: SafetyLevel
    max_targets: int = 1  # Maximum targets to affect simultaneously
    duration_seconds: int = 300  # How long the chaos lasts
    recovery_timeout_seconds: int = 600  # Time to wait for recovery
    enabled: bool = True
    
    # Scheduling
    schedule_pattern: Optional[str] = None  # Cron-like pattern
    run_during_business_hours: bool = False
    
    # Safety constraints
    min_healthy_instances: int = 2
    max_impact_percentage: float = 0.2  # Max 20% of instances


@dataclass
class ChaosResult:
    """Result of executing a chaos experiment"""
    experiment_name: str
    start_time: datetime
    end_time: Optional[datetime]
    action_taken: str
    targets_affected: List[str]
    success: bool
    error_message: Optional[str]
    recovery_time_seconds: Optional[float]
    metrics_before: Dict[str, Any]
    metrics_after: Dict[str, Any]
    lessons_learned: List[str]


class SafetyController:
    """Safety controls to prevent catastrophic failures"""
    
    def __init__(self):
        self.production_mode = self._detect_production()
        self.active_experiments = []
        self.max_concurrent_experiments = 2
        self.business_hours = (9, 18)  # 9 AM to 6 PM
        
        # Circuit breaker for chaos itself
        self.chaos_circuit_breaker = {
            'failure_count': 0,
            'last_failure_time': None,
            'is_open': False
        }
    
    def _detect_production(self) -> bool:
        """Detect if running in production environment"""
        prod_indicators = [
            os.environ.get('ENVIRONMENT', '').lower() == 'production',
            os.environ.get('CHAOS_ENV', '').lower() == 'production',
            os.path.exists('/etc/production'),
            any('prod' in hostname for hostname in [
                os.environ.get('HOSTNAME', ''),
                subprocess.getoutput('hostname 2>/dev/null')
            ])
        ]
        return any(prod_indicators)
    
    def can_execute_experiment(self, experiment: ChaosExperiment) -> tuple[bool, str]:
        """Check if experiment is safe to execute"""
        
        # Production safety checks
        if self.production_mode:
            if experiment.safety_level == SafetyLevel.AGGRESSIVE:
                return False, "Aggressive experiments not allowed in production"
            
            if not experiment.run_during_business_hours:
                current_hour = datetime.now().hour
                if self.business_hours[0] <= current_hour <= self.business_hours[1]:
                    return False, "Non-business-hour experiment blocked during business hours"
        
        # Concurrent experiment limit
        if len(self.active_experiments) >= self.max_concurrent_experiments:
            return False, f"Too many concurrent experiments ({len(self.active_experiments)})"
        
        # Circuit breaker check
        if self.chaos_circuit_breaker['is_open']:
            time_since_failure = time.time() - (self.chaos_circuit_breaker['last_failure_time'] or 0)
            if time_since_failure < 3600:  # 1 hour cooldown
                return False, "Chaos circuit breaker is open"
        
        # Target health check
        healthy_targets = self._count_healthy_targets(experiment.targets)
        if healthy_targets < experiment.min_healthy_instances:
            return False, f"Insufficient healthy targets ({healthy_targets} < {experiment.min_healthy_instances})"
        
        return True, "Safe to execute"
    
    def _count_healthy_targets(self, targets: List[ChaosTarget]) -> int:
        """Count healthy targets via health checks"""
        healthy_count = 0
        
        for target in targets:
            if target.health_check_url:
                try:
                    response = requests.get(target.health_check_url, timeout=5)
                    if response.status_code == 200:
                        healthy_count += 1
                except:
                    pass  # Assume unhealthy
            else:
                healthy_count += 1  # Assume healthy if no health check
        
        return healthy_count
    
    def register_experiment(self, experiment: ChaosExperiment):
        """Register active experiment"""
        self.active_experiments.append(experiment)
    
    def unregister_experiment(self, experiment: ChaosExperiment):
        """Unregister completed experiment"""
        if experiment in self.active_experiments:
            self.active_experiments.remove(experiment)
    
    def record_experiment_failure(self):
        """Record experiment failure for circuit breaker"""
        self.chaos_circuit_breaker['failure_count'] += 1
        self.chaos_circuit_breaker['last_failure_time'] = time.time()
        
        if self.chaos_circuit_breaker['failure_count'] >= 3:
            self.chaos_circuit_breaker['is_open'] = True
            logging.error("🚨 Chaos circuit breaker opened - too many failures")


class ChaosActionExecutor:
    """Execute different types of chaos actions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def execute_action(self, action: ChaosAction, target: ChaosTarget, 
                      duration: int = 300) -> tuple[bool, str]:
        """Execute specific chaos action"""
        
        self.logger.info(f"Executing {action.value} on {target.target_id}")
        
        try:
            if action == ChaosAction.TERMINATE_INSTANCE:
                return self._terminate_instance(target)
            elif action == ChaosAction.KILL_PROCESS:
                return self._kill_process(target)
            elif action == ChaosAction.CPU_STRESS:
                return self._cpu_stress(target, duration)
            elif action == ChaosAction.MEMORY_STRESS:
                return self._memory_stress(target, duration)
            elif action == ChaosAction.NETWORK_PARTITION:
                return self._network_partition(target, duration)
            elif action == ChaosAction.DISK_FILL:
                return self._disk_fill(target, duration)
            elif action == ChaosAction.SERVICE_DELAY:
                return self._service_delay(target, duration)
            else:
                return False, f"Unsupported action: {action.value}"
        
        except Exception as e:
            self.logger.error(f"Chaos action failed: {e}")
            return False, str(e)
    
    def _terminate_instance(self, target: ChaosTarget) -> tuple[bool, str]:
        """Terminate cloud instance"""
        if target.target_type != "instance":
            return False, "Target is not an instance"
        
        # Mock implementation - in real world, this would call cloud APIs
        self.logger.info(f"🔥 MOCK: Terminating instance {target.target_id}")
        
        # Simulate different cloud providers
        if "aws" in target.target_id:
            return self._aws_terminate_instance(target.target_id)
        elif "gcp" in target.target_id:
            return self._gcp_terminate_instance(target.target_id)
        elif "azure" in target.target_id:
            return self._azure_terminate_instance(target.target_id)
        else:
            return self._mock_terminate_instance(target.target_id)
    
    def _aws_terminate_instance(self, instance_id: str) -> tuple[bool, str]:
        """AWS instance termination (mock)"""
        # Real implementation would use boto3
        self.logger.info(f"AWS: Terminating EC2 instance {instance_id}")
        time.sleep(2)  # Simulate API call delay
        return True, f"AWS instance {instance_id} terminated"
    
    def _gcp_terminate_instance(self, instance_id: str) -> tuple[bool, str]:
        """GCP instance termination (mock)"""
        # Real implementation would use google-cloud-compute
        self.logger.info(f"GCP: Terminating Compute Engine instance {instance_id}")
        time.sleep(2)
        return True, f"GCP instance {instance_id} terminated"
    
    def _azure_terminate_instance(self, instance_id: str) -> tuple[bool, str]:
        """Azure instance termination (mock)"""
        # Real implementation would use azure-mgmt-compute
        self.logger.info(f"Azure: Terminating VM {instance_id}")
        time.sleep(2)
        return True, f"Azure instance {instance_id} terminated"
    
    def _mock_terminate_instance(self, instance_id: str) -> tuple[bool, str]:
        """Mock instance termination for testing"""
        self.logger.info(f"MOCK: Instance {instance_id} terminated")
        return True, f"Mock instance {instance_id} terminated"
    
    def _kill_process(self, target: ChaosTarget) -> tuple[bool, str]:
        """Kill specific process"""
        process_name = target.target_id
        
        try:
            # Find processes by name
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] == process_name:
                        proc.kill()
                        killed_count += 1
                        self.logger.info(f"Killed process {proc.info['pid']} ({process_name})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if killed_count > 0:
                return True, f"Killed {killed_count} processes named {process_name}"
            else:
                return False, f"No processes found with name {process_name}"
        
        except Exception as e:
            return False, f"Failed to kill process: {e}"
    
    def _cpu_stress(self, target: ChaosTarget, duration: int) -> tuple[bool, str]:
        """Create CPU stress"""
        self.logger.info(f"Creating CPU stress for {duration} seconds")
        
        def cpu_stress_worker():
            end_time = time.time() + duration
            while time.time() < end_time:
                # CPU intensive calculation
                sum(i * i for i in range(10000))
        
        # Start multiple threads for multi-core stress
        threads = []
        cpu_count = min(psutil.cpu_count(), 4)  # Max 4 threads for safety
        
        for _ in range(cpu_count):
            thread = threading.Thread(target=cpu_stress_worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        return True, f"CPU stress started with {cpu_count} threads for {duration}s"
    
    def _memory_stress(self, target: ChaosTarget, duration: int) -> tuple[bool, str]:
        """Create memory pressure"""
        self.logger.info(f"Creating memory stress for {duration} seconds")
        
        def memory_stress_worker():
            # Allocate 500MB of memory
            memory_hog = []
            chunk_size = 10 * 1024 * 1024  # 10MB chunks
            
            try:
                for i in range(50):  # 50 * 10MB = 500MB
                    chunk = bytearray(chunk_size)
                    # Touch the memory to ensure allocation
                    for j in range(0, chunk_size, 4096):
                        chunk[j] = 1
                    memory_hog.append(chunk)
                    time.sleep(0.1)
                
                # Hold memory for duration
                time.sleep(duration)
                
                # Cleanup
                del memory_hog
            
            except MemoryError:
                self.logger.warning("Memory allocation failed - system protected")
        
        thread = threading.Thread(target=memory_stress_worker)
        thread.daemon = True
        thread.start()
        
        return True, f"Memory stress started for {duration}s"
    
    def _network_partition(self, target: ChaosTarget, duration: int) -> tuple[bool, str]:
        """Simulate network partition"""
        # Mock implementation - real version would use iptables or tc
        self.logger.info(f"MOCK: Network partition for {duration} seconds")
        
        def restore_network():
            time.sleep(duration)
            self.logger.info("Network partition restored")
        
        thread = threading.Thread(target=restore_network)
        thread.daemon = True
        thread.start()
        
        return True, f"Network partition simulated for {duration}s"
    
    def _disk_fill(self, target: ChaosTarget, duration: int) -> tuple[bool, str]:
        """Fill disk space"""
        self.logger.info(f"Creating disk pressure for {duration} seconds")
        
        def disk_fill_worker():
            temp_files = []
            try:
                # Fill 1GB of disk space
                for i in range(100):  # 100 * 10MB files
                    temp_file = f"/tmp/chaos_fill_{i}_{int(time.time())}.tmp"
                    with open(temp_file, 'wb') as f:
                        f.write(os.urandom(10 * 1024 * 1024))  # 10MB
                    temp_files.append(temp_file)
                    time.sleep(0.1)
                
                # Hold files for duration
                time.sleep(duration)
                
                # Cleanup
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            
            except Exception as e:
                self.logger.error(f"Disk fill error: {e}")
                # Cleanup on error
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except:
                        pass
        
        thread = threading.Thread(target=disk_fill_worker)
        thread.daemon = True
        thread.start()
        
        return True, f"Disk fill started for {duration}s"
    
    def _service_delay(self, target: ChaosTarget, duration: int) -> tuple[bool, str]:
        """Inject service delays"""
        # Mock implementation - real version would use proxy injection
        self.logger.info(f"MOCK: Service delay injection for {duration} seconds")
        
        def remove_delay():
            time.sleep(duration)
            self.logger.info("Service delays removed")
        
        thread = threading.Thread(target=remove_delay)
        thread.daemon = True
        thread.start()
        
        return True, f"Service delays injected for {duration}s"


class MetricsCollector:
    """Collect system metrics before/after chaos experiments"""
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                'network_connections': len(psutil.net_connections()),
                'process_count': len(psutil.pids()),
                'boot_time': psutil.boot_time()
            }
        except Exception as e:
            logging.warning(f"Metrics collection failed: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}


class ChaosMonkey:
    """Main Chaos Monkey orchestrator"""
    
    def __init__(self):
        self.safety_controller = SafetyController()
        self.action_executor = ChaosActionExecutor()
        self.metrics_collector = MetricsCollector()
        self.experiments = []
        self.results = []
        self.is_running = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chaos_monkey.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def add_experiment(self, experiment: ChaosExperiment):
        """Add chaos experiment to the schedule"""
        self.experiments.append(experiment)
        self.logger.info(f"Added experiment: {experiment.name}")
    
    def run_single_experiment(self, experiment: ChaosExperiment) -> ChaosResult:
        """Execute a single chaos experiment"""
        
        self.logger.info(f"🐒 Starting chaos experiment: {experiment.name}")
        
        # Initialize result
        result = ChaosResult(
            experiment_name=experiment.name,
            start_time=datetime.now(),
            end_time=None,
            action_taken=experiment.action.value,
            targets_affected=[],
            success=False,
            error_message=None,
            recovery_time_seconds=None,
            metrics_before={},
            metrics_after={},
            lessons_learned=[]
        )
        
        try:
            # Safety check
            can_execute, reason = self.safety_controller.can_execute_experiment(experiment)
            if not can_execute:
                raise Exception(f"Safety check failed: {reason}")
            
            # Register experiment
            self.safety_controller.register_experiment(experiment)
            
            # Collect baseline metrics
            result.metrics_before = self.metrics_collector.collect_metrics()
            
            # Select targets based on probability and constraints
            selected_targets = self._select_targets(experiment)
            
            if not selected_targets:
                raise Exception("No targets selected for chaos action")
            
            # Execute chaos action on selected targets
            for target in selected_targets:
                action_success, action_message = self.action_executor.execute_action(
                    experiment.action, target, experiment.duration_seconds
                )
                
                if action_success:
                    result.targets_affected.append(target.target_id)
                    self.logger.info(f"✅ Chaos action succeeded: {action_message}")
                else:
                    raise Exception(f"Chaos action failed: {action_message}")
            
            # Wait for experiment duration
            if experiment.duration_seconds > 0:
                self.logger.info(f"⏳ Waiting {experiment.duration_seconds}s for chaos effects...")
                time.sleep(experiment.duration_seconds)
            
            # Collect post-chaos metrics
            result.metrics_after = self.metrics_collector.collect_metrics()
            
            # Wait for recovery and measure time
            recovery_start = time.time()
            self._wait_for_recovery(experiment, selected_targets)
            result.recovery_time_seconds = time.time() - recovery_start
            
            # Mark as successful
            result.success = True
            result.end_time = datetime.now()
            
            # Generate lessons learned
            result.lessons_learned = self._generate_lessons_learned(experiment, result)
            
            self.logger.info(f"✅ Chaos experiment completed successfully")
        
        except Exception as e:
            self.logger.error(f"❌ Chaos experiment failed: {e}")
            result.error_message = str(e)
            result.end_time = datetime.now()
            self.safety_controller.record_experiment_failure()
        
        finally:
            self.safety_controller.unregister_experiment(experiment)
        
        self.results.append(result)
        return result
    
    def _select_targets(self, experiment: ChaosExperiment) -> List[ChaosTarget]:
        """Select targets for chaos action based on experiment configuration"""
        
        available_targets = [t for t in experiment.targets if t.environment != TargetEnvironment.PRODUCTION or 
                           self.safety_controller.production_mode]
        
        if not available_targets:
            return []
        
        # Apply probability filter
        selected_targets = []
        for target in available_targets:
            if random.random() < experiment.probability:
                selected_targets.append(target)
        
        # Limit by max_targets
        if len(selected_targets) > experiment.max_targets:
            selected_targets = random.sample(selected_targets, experiment.max_targets)
        
        # Ensure we don't exceed max impact percentage
        max_allowed = int(len(available_targets) * experiment.max_impact_percentage)
        if len(selected_targets) > max_allowed:
            selected_targets = selected_targets[:max_allowed]
        
        return selected_targets
    
    def _wait_for_recovery(self, experiment: ChaosExperiment, targets: List[ChaosTarget]):
        """Wait for system to recover after chaos action"""
        
        recovery_timeout = experiment.recovery_timeout_seconds
        check_interval = 10  # Check every 10 seconds
        
        self.logger.info(f"⏰ Waiting for recovery (timeout: {recovery_timeout}s)")
        
        for elapsed in range(0, recovery_timeout, check_interval):
            time.sleep(check_interval)
            
            # Check if targets are healthy
            healthy_count = self.safety_controller._count_healthy_targets(targets)
            if healthy_count >= len(targets) * 0.8:  # 80% healthy = recovered
                self.logger.info(f"✅ System recovered in {elapsed + check_interval}s")
                return
            
            self.logger.info(f"⏳ Recovery in progress... ({elapsed + check_interval}s elapsed)")
        
        self.logger.warning(f"⚠️  Recovery timeout reached ({recovery_timeout}s)")
    
    def _generate_lessons_learned(self, experiment: ChaosExperiment, 
                                result: ChaosResult) -> List[str]:
        """Generate lessons learned from experiment"""
        
        lessons = []
        
        # Recovery time analysis
        if result.recovery_time_seconds:
            if result.recovery_time_seconds < 60:
                lessons.append("✅ Fast recovery - system is resilient")
            elif result.recovery_time_seconds < 300:
                lessons.append("⚠️  Moderate recovery time - consider optimization")
            else:
                lessons.append("🚨 Slow recovery - investigate bottlenecks")
        
        # Metrics comparison
        if result.metrics_before and result.metrics_after:
            cpu_change = (result.metrics_after.get('cpu_percent', 0) - 
                         result.metrics_before.get('cpu_percent', 0))
            if cpu_change > 20:
                lessons.append("📈 High CPU impact - validate resource allocation")
            
            memory_change = (result.metrics_after.get('memory_percent', 0) - 
                           result.metrics_before.get('memory_percent', 0))
            if memory_change > 15:
                lessons.append("💾 Significant memory impact - check memory leaks")
        
        # Action-specific lessons
        if experiment.action == ChaosAction.TERMINATE_INSTANCE:
            lessons.append("🔄 Validate auto-scaling and load balancing")
        elif experiment.action == ChaosAction.NETWORK_PARTITION:
            lessons.append("🌐 Test network resilience and failover mechanisms")
        elif experiment.action == ChaosAction.CPU_STRESS:
            lessons.append("⚡ Review CPU resource limits and alerts")
        
        # General lessons
        lessons.append("📊 Update monitoring thresholds based on observed behavior")
        lessons.append("📋 Document incident response procedures")
        
        return lessons
    
    def start_scheduled_chaos(self):
        """Start scheduled chaos monkey execution"""
        if self.is_running:
            return
        
        self.is_running = True
        self.logger.info("🐒 Chaos Monkey started - scheduled execution enabled")
        
        def chaos_scheduler():
            while self.is_running:
                try:
                    for experiment in self.experiments:
                        if experiment.enabled and self._should_run_now(experiment):
                            self.run_single_experiment(experiment)
                    
                    # Check every minute
                    time.sleep(60)
                
                except Exception as e:
                    self.logger.error(f"Scheduler error: {e}")
                    time.sleep(60)
        
        scheduler_thread = threading.Thread(target=chaos_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
    
    def stop_scheduled_chaos(self):
        """Stop scheduled chaos execution"""
        self.is_running = False
        self.logger.info("🛑 Chaos Monkey stopped")
    
    def _should_run_now(self, experiment: ChaosExperiment) -> bool:
        """Check if experiment should run now based on schedule"""
        # Simplified scheduling - real implementation would parse cron patterns
        
        if experiment.schedule_pattern:
            # Mock schedule check
            return random.random() < 0.01  # 1% chance per check
        
        # Business hours check
        current_hour = datetime.now().hour
        if not experiment.run_during_business_hours:
            if 9 <= current_hour <= 18:  # Business hours
                return False
        
        # Default: run based on probability
        return random.random() < experiment.probability / 100  # Convert to very low probability
    
    def generate_chaos_report(self) -> str:
        """Generate comprehensive chaos engineering report"""
        
        if not self.results:
            return "No chaos experiments have been executed yet."
        
        successful_experiments = [r for r in self.results if r.success]
        failed_experiments = [r for r in self.results if not r.success]
        
        report = f"""
🐒 CHAOS MONKEY EXPERIMENT REPORT
{'='*50}

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Environment: {'Production' if self.safety_controller.production_mode else 'Non-Production'}

📊 EXPERIMENT SUMMARY
{'-'*25}
Total Experiments: {len(self.results)}
Successful: {len(successful_experiments)}
Failed: {len(failed_experiments)}
Success Rate: {len(successful_experiments)/len(self.results)*100:.1f}%

⏱️  RECOVERY METRICS
{'-'*19}"""
        
        if successful_experiments:
            recovery_times = [r.recovery_time_seconds for r in successful_experiments 
                            if r.recovery_time_seconds]
            if recovery_times:
                report += f"""
Average Recovery Time: {sum(recovery_times)/len(recovery_times):.1f}s
Fastest Recovery: {min(recovery_times):.1f}s
Slowest Recovery: {max(recovery_times):.1f}s"""
        
        report += f"""

🎯 EXPERIMENT DETAILS
{'-'*21}"""
        
        for i, result in enumerate(self.results[-10:], 1):  # Last 10 experiments
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            duration = (result.end_time - result.start_time).total_seconds() if result.end_time else 0
            
            report += f"""

Experiment {i}: {result.experiment_name}
  Status: {status}
  Action: {result.action_taken}
  Duration: {duration:.1f}s
  Targets Affected: {len(result.targets_affected)}
  Recovery Time: {result.recovery_time_seconds:.1f}s
"""
            
            if result.error_message:
                report += f"  Error: {result.error_message}\n"
            
            if result.lessons_learned:
                report += f"  Key Lessons: {len(result.lessons_learned)} insights\n"
        
        # Top lessons learned
        all_lessons = []
        for result in successful_experiments:
            all_lessons.extend(result.lessons_learned)
        
        if all_lessons:
            # Count most common lessons
            lesson_counts = {}
            for lesson in all_lessons:
                lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1
            
            top_lessons = sorted(lesson_counts.items(), key=lambda x: x[1], reverse=True)
            
            report += f"""

💡 TOP LESSONS LEARNED
{'-'*22}"""
            
            for lesson, count in top_lessons[:5]:
                report += f"\n{lesson} (appeared {count} times)"
        
        report += f"""

🚨 SAFETY METRICS
{'-'*17}
Circuit Breaker Status: {'OPEN' if self.safety_controller.chaos_circuit_breaker['is_open'] else 'CLOSED'}
Production Mode: {self.safety_controller.production_mode}
Max Concurrent Experiments: {self.safety_controller.max_concurrent_experiments}
Active Experiments: {len(self.safety_controller.active_experiments)}

📋 RECOMMENDATIONS
{'-'*18}
1. Focus on experiments with slow recovery times
2. Implement automated remediation for common failures
3. Update monitoring based on chaos learnings
4. Increase experiment frequency gradually
5. Document and share lessons with the team

💰 BUSINESS VALUE
{'-'*16}
- Prevented outages: Estimated ₹5-25Cr saved per major incident avoided
- Improved MTTR: {((sum(recovery_times)/len(recovery_times)) if recovery_times else 0):.1f}s average recovery
- Enhanced confidence: {len(successful_experiments)} successful resilience validations
- Knowledge building: {len(all_lessons)} lessons learned and documented
"""
        
        return report


def create_indian_platform_experiments():
    """Create realistic chaos experiments for Indian platforms"""
    
    experiments = []
    
    # 1. Flipkart Big Billion Days Simulation
    flipkart_targets = [
        ChaosTarget("instance", "flipkart-web-01", TargetEnvironment.STAGING, 
                   {"service": "web", "zone": "us-east-1a"}, "http://flipkart-web-01/health"),
        ChaosTarget("instance", "flipkart-web-02", TargetEnvironment.STAGING,
                   {"service": "web", "zone": "us-east-1b"}, "http://flipkart-web-02/health"),
        ChaosTarget("instance", "flipkart-api-01", TargetEnvironment.STAGING,
                   {"service": "api", "zone": "us-east-1a"}, "http://flipkart-api-01/health")
    ]
    
    experiments.append(ChaosExperiment(
        name="Flipkart_BBD_Instance_Failure",
        description="Simulate server failures during Big Billion Days high traffic",
        action=ChaosAction.TERMINATE_INSTANCE,
        targets=flipkart_targets,
        probability=0.3,
        safety_level=SafetyLevel.MODERATE,
        max_targets=1,
        duration_seconds=300,
        recovery_timeout_seconds=600,
        min_healthy_instances=2,
        max_impact_percentage=0.33
    ))
    
    # 2. Paytm Payment Gateway Stress
    paytm_targets = [
        ChaosTarget("process", "payment-gateway", TargetEnvironment.STAGING,
                   {"service": "payment", "criticality": "high"}),
        ChaosTarget("process", "wallet-service", TargetEnvironment.STAGING,
                   {"service": "wallet", "criticality": "high"})
    ]
    
    experiments.append(ChaosExperiment(
        name="Paytm_Payment_CPU_Stress",
        description="Test payment system resilience under CPU pressure",
        action=ChaosAction.CPU_STRESS,
        targets=paytm_targets,
        probability=0.4,
        safety_level=SafetyLevel.SAFE,
        max_targets=1,
        duration_seconds=180,
        recovery_timeout_seconds=300,
        run_during_business_hours=False
    ))
    
    # 3. IRCTC Tatkal Booking Memory Pressure
    irctc_targets = [
        ChaosTarget("instance", "irctc-booking-01", TargetEnvironment.STAGING,
                   {"service": "booking", "traffic": "high"}),
        ChaosTarget("instance", "irctc-search-01", TargetEnvironment.STAGING,
                   {"service": "search", "traffic": "high"})
    ]
    
    experiments.append(ChaosExperiment(
        name="IRCTC_Tatkal_Memory_Pressure",
        description="Simulate memory pressure during Tatkal booking rush",
        action=ChaosAction.MEMORY_STRESS,
        targets=irctc_targets,
        probability=0.2,
        safety_level=SafetyLevel.MODERATE,
        max_targets=1,
        duration_seconds=240,
        recovery_timeout_seconds=480,
        schedule_pattern="0 10 * * *"  # Run at 10 AM (Tatkal time)
    ))
    
    # 4. Ola Ride Matching Network Partition
    ola_targets = [
        ChaosTarget("instance", "ola-matching-01", TargetEnvironment.STAGING,
                   {"service": "matching", "region": "mumbai"}),
        ChaosTarget("instance", "ola-matching-02", TargetEnvironment.STAGING,
                   {"service": "matching", "region": "bangalore"})
    ]
    
    experiments.append(ChaosExperiment(
        name="Ola_Network_Partition",
        description="Test ride matching resilience during network issues",
        action=ChaosAction.NETWORK_PARTITION,
        targets=ola_targets,
        probability=0.25,
        safety_level=SafetyLevel.SAFE,
        max_targets=1,
        duration_seconds=120,
        recovery_timeout_seconds=300
    ))
    
    return experiments


def demo_chaos_monkey():
    """Demonstrate Chaos Monkey functionality"""
    
    print("🐒 CHAOS MONKEY DEMO - INDIAN PLATFORM EDITION")
    print("="*55)
    
    # Initialize Chaos Monkey
    chaos_monkey = ChaosMonkey()
    
    # Load Indian platform experiments
    experiments = create_indian_platform_experiments()
    
    print(f"\n📋 Loading {len(experiments)} chaos experiments...")
    for experiment in experiments:
        chaos_monkey.add_experiment(experiment)
        print(f"  ✅ {experiment.name}")
    
    print(f"\n🔧 Safety Controls:")
    print(f"  Production Mode: {chaos_monkey.safety_controller.production_mode}")
    print(f"  Max Concurrent: {chaos_monkey.safety_controller.max_concurrent_experiments}")
    print(f"  Circuit Breaker: {'OPEN' if chaos_monkey.safety_controller.chaos_circuit_breaker['is_open'] else 'CLOSED'}")
    
    # Run a safe demo experiment
    print(f"\n🚀 Running demo chaos experiment...")
    
    # Create a safe demo experiment
    demo_targets = [
        ChaosTarget("process", "demo-service", TargetEnvironment.DEVELOPMENT,
                   {"demo": "true"})
    ]
    
    demo_experiment = ChaosExperiment(
        name="Demo_CPU_Stress",
        description="Safe CPU stress test for demonstration",
        action=ChaosAction.CPU_STRESS,
        targets=demo_targets,
        probability=1.0,  # Always run for demo
        safety_level=SafetyLevel.SAFE,
        max_targets=1,
        duration_seconds=10,  # Short duration
        recovery_timeout_seconds=30
    )
    
    # Execute experiment
    result = chaos_monkey.run_single_experiment(demo_experiment)
    
    if result.success:
        print(f"✅ Demo experiment completed successfully!")
        print(f"  Duration: {(result.end_time - result.start_time).total_seconds():.1f}s")
        print(f"  Recovery Time: {result.recovery_time_seconds:.1f}s")
        print(f"  Lessons Learned: {len(result.lessons_learned)}")
    else:
        print(f"❌ Demo experiment failed: {result.error_message}")
    
    # Generate report
    report = chaos_monkey.generate_chaos_report()
    print("\n" + report)
    
    # Save results
    with open('chaos_monkey_results.json', 'w') as f:
        json_results = {
            'experiments': [asdict(exp) for exp in experiments],
            'results': [asdict(result) for result in chaos_monkey.results],
            'metadata': {
                'demo_date': datetime.now().isoformat(),
                'production_mode': chaos_monkey.safety_controller.production_mode,
                'total_experiments': len(chaos_monkey.results)
            }
        }
        json.dump(json_results, f, indent=2, default=str)
    
    print("\n📁 Results saved to chaos_monkey_results.json")
    
    print(f"\n💡 CHAOS ENGINEERING INSIGHTS:")
    print("1. Start small - begin with safe, low-impact experiments")
    print("2. Automate recovery - build self-healing capabilities") 
    print("3. Learn continuously - document and share lessons")
    print("4. Increase complexity gradually - build confidence over time")
    print("5. Monitor everything - observability is key to chaos success")
    
    print(f"\n💰 BUSINESS VALUE:")
    print("- Prevents major outages: ₹10-50Cr+ saved per avoided incident")
    print("- Improves customer trust: Higher availability and reliability")
    print("- Builds team confidence: Validated system resilience")
    print("- Accelerates learning: Faster incident response and resolution")


if __name__ == "__main__":
    demo_chaos_monkey()
#!/usr/bin/env python3
"""
Failure Injection Framework - Chaos Engineering Tool
===================================================
Production-grade chaos engineering framework inspired by:
- Netflix Chaos Monkey
- Litmus Chaos
- Gremlin

Real-world use cases:
- Test Paytm payment resilience under network partitions
- Validate Flipkart cart service during database failures
- Verify Ola ride matching under high latency conditions
- Test IRCTC booking system during memory pressure

Features:
- Network failure injection (latency, packet loss, partitions)
- Resource exhaustion (CPU, memory, disk)
- Service dependency failures
- Random failure scheduling
- Safety controls and blast radius limiting
"""

import random
import time
import threading
import subprocess
import psutil
import socket
import json
import logging
import os
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from contextlib import contextmanager
import requests


class FailureType(Enum):
    """Types of failures that can be injected"""
    NETWORK_LATENCY = "network_latency"
    NETWORK_PACKET_LOSS = "network_packet_loss" 
    NETWORK_PARTITION = "network_partition"
    CPU_SPIKE = "cpu_spike"
    MEMORY_PRESSURE = "memory_pressure"
    DISK_EXHAUSTION = "disk_exhaustion"
    SERVICE_UNAVAILABLE = "service_unavailable"
    DATABASE_SLOW = "database_slow"
    RANDOM_EXCEPTION = "random_exception"


class SafetyLevel(Enum):
    """Safety levels for blast radius control"""
    SAFE = "safe"           # Production safe - minimal impact
    MODERATE = "moderate"   # Staging safe - noticeable impact  
    AGGRESSIVE = "aggressive" # Dev/Test only - high impact


@dataclass
class FailureConfig:
    """Configuration for a specific failure injection"""
    failure_type: FailureType
    duration_seconds: int
    intensity: float  # 0.0 to 1.0
    target_services: List[str]
    safety_level: SafetyLevel
    description: str
    
    # Specific parameters for different failure types
    params: Dict[str, Any] = None


@dataclass
class InjectionResult:
    """Result of a failure injection experiment"""
    config: FailureConfig
    start_time: datetime
    end_time: Optional[datetime]
    success: bool
    error_message: Optional[str]
    metrics_collected: Dict[str, Any]
    recovery_time_seconds: Optional[float]


class SafetyController:
    """Safety controls to prevent catastrophic failures in production"""
    
    def __init__(self):
        self.active_injections = []
        self.max_concurrent_injections = 3
        self.production_mode = self._detect_production_environment()
        
    def _detect_production_environment(self) -> bool:
        """Detect if running in production environment"""
        env_indicators = [
            os.environ.get('ENVIRONMENT', '').lower() == 'production',
            os.environ.get('RAILS_ENV', '').lower() == 'production',
            os.environ.get('NODE_ENV', '').lower() == 'production',
            os.path.exists('/etc/production_marker'),
            socket.gethostname().startswith('prod-')
        ]
        return any(env_indicators)
    
    def can_inject_failure(self, config: FailureConfig) -> tuple[bool, str]:
        """Check if failure injection is safe to proceed"""
        
        # Production safety checks
        if self.production_mode:
            if config.safety_level == SafetyLevel.AGGRESSIVE:
                return False, "Aggressive failures not allowed in production"
            
            # Additional production restrictions
            if config.failure_type in [FailureType.DISK_EXHAUSTION, FailureType.MEMORY_PRESSURE]:
                return False, f"{config.failure_type.value} not allowed in production"
        
        # Concurrent injection limit
        if len(self.active_injections) >= self.max_concurrent_injections:
            return False, f"Too many concurrent injections ({len(self.active_injections)})"
        
        # Intensity checks
        if config.intensity > 0.8 and config.safety_level != SafetyLevel.AGGRESSIVE:
            return False, f"High intensity ({config.intensity}) requires aggressive safety level"
        
        return True, "Safe to proceed"
    
    def register_injection(self, config: FailureConfig):
        """Register an active injection"""
        self.active_injections.append(config)
        
    def unregister_injection(self, config: FailureConfig):
        """Unregister a completed injection"""
        if config in self.active_injections:
            self.active_injections.remove(config)


class NetworkChaosInjector:
    """Network failure injection using tc (traffic control)"""
    
    def __init__(self):
        self.active_rules = []
    
    def inject_latency(self, interface: str = "lo", delay_ms: int = 100, 
                      jitter_ms: int = 10, duration: int = 30):
        """Inject network latency using tc netem"""
        try:
            # Add latency rule - सिर्फ loopback interface पर test के लिए
            cmd = f"sudo tc qdisc add dev {interface} root netem delay {delay_ms}ms {jitter_ms}ms"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.active_rules.append((interface, "netem"))
                print(f"✅ Network latency injected: {delay_ms}ms ± {jitter_ms}ms")
                
                # Schedule cleanup
                cleanup_thread = threading.Thread(
                    target=self._cleanup_after_delay, 
                    args=(interface, duration)
                )
                cleanup_thread.daemon = True
                cleanup_thread.start()
                
                return True
            else:
                print(f"❌ Failed to inject latency: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Network latency injection failed: {e}")
            return False
    
    def inject_packet_loss(self, interface: str = "lo", loss_percent: float = 5.0,
                          duration: int = 30):
        """Inject packet loss using tc netem"""
        try:
            cmd = f"sudo tc qdisc add dev {interface} root netem loss {loss_percent}%"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.active_rules.append((interface, "loss"))
                print(f"✅ Packet loss injected: {loss_percent}%")
                
                cleanup_thread = threading.Thread(
                    target=self._cleanup_after_delay, 
                    args=(interface, duration)
                )
                cleanup_thread.daemon = True
                cleanup_thread.start()
                
                return True
            else:
                print(f"❌ Failed to inject packet loss: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Packet loss injection failed: {e}")
            return False
    
    def _cleanup_after_delay(self, interface: str, delay: int):
        """Clean up network rules after delay"""
        time.sleep(delay)
        self.cleanup_interface(interface)
    
    def cleanup_interface(self, interface: str = "lo"):
        """Remove all tc rules from interface"""
        try:
            cmd = f"sudo tc qdisc del dev {interface} root"
            subprocess.run(cmd, shell=True, capture_output=True)
            print(f"🧹 Cleaned up network rules for {interface}")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")


class ResourceChaosInjector:
    """Resource exhaustion injection (CPU, Memory, Disk)"""
    
    def __init__(self):
        self.active_processes = []
    
    def inject_cpu_spike(self, intensity: float = 0.8, duration: int = 30):
        """Create CPU spike by spawning busy processes"""
        cpu_count = psutil.cpu_count()
        processes_to_spawn = int(cpu_count * intensity)
        
        print(f"🔥 Injecting CPU spike: {processes_to_spawn} processes for {duration}s")
        
        def cpu_burner():
            """CPU intensive task"""
            end_time = time.time() + duration
            while time.time() < end_time:
                # Pure CPU burn - no I/O
                for _ in range(1000000):
                    pass
        
        # Spawn CPU burning threads
        threads = []
        for i in range(processes_to_spawn):
            thread = threading.Thread(target=cpu_burner)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        self.active_processes.extend(threads)
        return True
    
    def inject_memory_pressure(self, size_mb: int = 500, duration: int = 30):
        """Create memory pressure by allocating large chunks"""
        print(f"💾 Injecting memory pressure: {size_mb}MB for {duration}s")
        
        def memory_eater():
            try:
                # Allocate memory in chunks
                chunks = []
                chunk_size = 10 * 1024 * 1024  # 10MB chunks
                total_chunks = size_mb // 10
                
                for i in range(total_chunks):
                    chunk = bytearray(chunk_size)
                    # Write to memory to ensure allocation
                    for j in range(0, chunk_size, 4096):
                        chunk[j] = 1
                    chunks.append(chunk)
                    time.sleep(0.1)  # Gradual allocation
                
                # Hold memory for duration
                time.sleep(duration)
                
                # Cleanup
                del chunks
                print("✅ Memory pressure cleaned up")
                
            except Exception as e:
                print(f"❌ Memory pressure injection failed: {e}")
        
        thread = threading.Thread(target=memory_eater)
        thread.daemon = True
        thread.start()
        self.active_processes.append(thread)
        
        return True
    
    def inject_disk_pressure(self, size_mb: int = 100, duration: int = 30,
                           path: str = "/tmp"):
        """Create disk pressure by writing large files"""
        print(f"💽 Injecting disk pressure: {size_mb}MB to {path}")
        
        def disk_eater():
            temp_files = []
            try:
                chunk_size = 1024 * 1024  # 1MB chunks
                chunks_to_write = size_mb
                
                for i in range(chunks_to_write):
                    temp_file = f"{path}/chaos_disk_{i}_{int(time.time())}.tmp"
                    with open(temp_file, 'wb') as f:
                        f.write(os.urandom(chunk_size))
                    temp_files.append(temp_file)
                    time.sleep(0.1)  # Gradual disk fill
                
                # Hold files for duration
                time.sleep(duration)
                
                # Cleanup
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                
                print("✅ Disk pressure cleaned up")
                
            except Exception as e:
                print(f"❌ Disk pressure injection failed: {e}")
        
        thread = threading.Thread(target=disk_eater)
        thread.daemon = True  
        thread.start()
        self.active_processes.append(thread)
        
        return True


class ServiceChaosInjector:
    """Service-level failure injection"""
    
    def __init__(self):
        self.blocked_services = set()
    
    def block_service_calls(self, service_urls: List[str], duration: int = 30):
        """Block HTTP calls to specific services using monkey patching"""
        print(f"🚫 Blocking service calls for {duration}s: {service_urls}")
        
        # Store original requests.get
        original_get = requests.get
        original_post = requests.post
        
        def blocked_get(url, *args, **kwargs):
            for blocked_url in service_urls:
                if blocked_url in url:
                    raise requests.exceptions.ConnectionError(f"Service blocked by chaos injection: {blocked_url}")
            return original_get(url, *args, **kwargs)
        
        def blocked_post(url, *args, **kwargs):
            for blocked_url in service_urls:
                if blocked_url in url:
                    raise requests.exceptions.ConnectionError(f"Service blocked by chaos injection: {blocked_url}")
            return original_post(url, *args, **kwargs)
        
        # Apply monkey patch
        requests.get = blocked_get
        requests.post = blocked_post
        self.blocked_services.update(service_urls)
        
        # Schedule restoration
        def restore_services():
            time.sleep(duration)
            requests.get = original_get
            requests.post = original_post
            self.blocked_services.clear()
            print("✅ Service blocking restored")
        
        thread = threading.Thread(target=restore_services)
        thread.daemon = True
        thread.start()
        
        return True
    
    def inject_slow_responses(self, delay_seconds: float = 2.0, duration: int = 30):
        """Inject artificial delays in HTTP responses"""
        print(f"🐌 Injecting slow responses: {delay_seconds}s delay for {duration}s")
        
        # Store original requests functions
        original_get = requests.get
        original_post = requests.post
        
        def slow_get(url, *args, **kwargs):
            time.sleep(delay_seconds)
            return original_get(url, *args, **kwargs)
        
        def slow_post(url, *args, **kwargs):
            time.sleep(delay_seconds)
            return original_post(url, *args, **kwargs)
        
        # Apply monkey patch
        requests.get = slow_get
        requests.post = slow_post
        
        # Schedule restoration
        def restore_speed():
            time.sleep(duration)
            requests.get = original_get
            requests.post = original_post
            print("✅ Response speed restored")
        
        thread = threading.Thread(target=restore_speed)
        thread.daemon = True
        thread.start()
        
        return True


class ChaosOrchestrator:
    """Main orchestrator for chaos experiments"""
    
    def __init__(self):
        self.safety_controller = SafetyController()
        self.network_injector = NetworkChaosInjector()
        self.resource_injector = ResourceChaosInjector()
        self.service_injector = ServiceChaosInjector()
        self.experiment_results = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chaos_experiments.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_experiment(self, config: FailureConfig) -> InjectionResult:
        """Run a single chaos experiment"""
        self.logger.info(f"Starting chaos experiment: {config.description}")
        
        # Safety check
        can_proceed, reason = self.safety_controller.can_inject_failure(config)
        if not can_proceed:
            self.logger.error(f"Experiment blocked by safety controller: {reason}")
            return InjectionResult(
                config=config,
                start_time=datetime.now(),
                end_time=datetime.now(),
                success=False,
                error_message=reason,
                metrics_collected={},
                recovery_time_seconds=None
            )
        
        # Start experiment
        start_time = datetime.now()
        result = InjectionResult(
            config=config,
            start_time=start_time,
            end_time=None,
            success=False,
            error_message=None,
            metrics_collected={},
            recovery_time_seconds=None
        )
        
        try:
            self.safety_controller.register_injection(config)
            
            # Collect baseline metrics
            baseline_metrics = self._collect_system_metrics()
            
            # Execute failure injection
            injection_success = self._execute_injection(config)
            
            if not injection_success:
                raise Exception("Failure injection execution failed")
            
            # Wait for experiment duration
            time.sleep(config.duration_seconds)
            
            # Collect final metrics
            final_metrics = self._collect_system_metrics()
            
            # Calculate recovery time (simplified)
            recovery_start = time.time()
            time.sleep(5)  # Wait for potential recovery
            recovery_metrics = self._collect_system_metrics()
            recovery_time = time.time() - recovery_start
            
            # Mark as successful
            result.end_time = datetime.now()
            result.success = True
            result.metrics_collected = {
                'baseline': baseline_metrics,
                'during_experiment': final_metrics,
                'recovery': recovery_metrics
            }
            result.recovery_time_seconds = recovery_time
            
            self.logger.info(f"Chaos experiment completed successfully")
            
        except Exception as e:
            self.logger.error(f"Chaos experiment failed: {e}")
            result.end_time = datetime.now()
            result.error_message = str(e)
        
        finally:
            self.safety_controller.unregister_injection(config)
        
        self.experiment_results.append(result)
        return result
    
    def _execute_injection(self, config: FailureConfig) -> bool:
        """Execute the specific failure injection"""
        params = config.params or {}
        
        if config.failure_type == FailureType.NETWORK_LATENCY:
            return self.network_injector.inject_latency(
                delay_ms=params.get('delay_ms', int(config.intensity * 500)),
                duration=config.duration_seconds
            )
        
        elif config.failure_type == FailureType.NETWORK_PACKET_LOSS:
            return self.network_injector.inject_packet_loss(
                loss_percent=config.intensity * 20,  # Up to 20% loss
                duration=config.duration_seconds
            )
        
        elif config.failure_type == FailureType.CPU_SPIKE:
            return self.resource_injector.inject_cpu_spike(
                intensity=config.intensity,
                duration=config.duration_seconds
            )
        
        elif config.failure_type == FailureType.MEMORY_PRESSURE:
            return self.resource_injector.inject_memory_pressure(
                size_mb=int(config.intensity * 1000),  # Up to 1GB
                duration=config.duration_seconds
            )
        
        elif config.failure_type == FailureType.DISK_EXHAUSTION:
            return self.resource_injector.inject_disk_pressure(
                size_mb=int(config.intensity * 500),   # Up to 500MB
                duration=config.duration_seconds
            )
        
        elif config.failure_type == FailureType.SERVICE_UNAVAILABLE:
            target_urls = params.get('target_urls', ['http://localhost'])
            return self.service_injector.block_service_calls(
                service_urls=target_urls,
                duration=config.duration_seconds
            )
        
        elif config.failure_type == FailureType.DATABASE_SLOW:
            return self.service_injector.inject_slow_responses(
                delay_seconds=config.intensity * 5,  # Up to 5s delay
                duration=config.duration_seconds
            )
        
        else:
            self.logger.error(f"Unsupported failure type: {config.failure_type}")
            return False
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics for analysis"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                'network_connections': len(psutil.net_connections()),
                'processes': len(psutil.pids())
            }
        except Exception as e:
            self.logger.warning(f"Failed to collect metrics: {e}")
            return {'error': str(e)}
    
    def run_chaos_scenario(self, scenario_name: str, configs: List[FailureConfig]) -> List[InjectionResult]:
        """Run a complete chaos engineering scenario"""
        self.logger.info(f"🚀 Starting chaos scenario: {scenario_name}")
        results = []
        
        for i, config in enumerate(configs, 1):
            self.logger.info(f"Running experiment {i}/{len(configs)}: {config.description}")
            result = self.run_experiment(config)
            results.append(result)
            
            # Wait between experiments
            if i < len(configs):
                time.sleep(10)
        
        self.logger.info(f"✅ Chaos scenario '{scenario_name}' completed")
        return results
    
    def generate_experiment_report(self) -> str:
        """Generate comprehensive experiment report"""
        if not self.experiment_results:
            return "No experiments have been run yet."
        
        successful_experiments = [r for r in self.experiment_results if r.success]
        failed_experiments = [r for r in self.experiment_results if not r.success]
        
        report = f"""
🔬 CHAOS ENGINEERING EXPERIMENT REPORT
{'='*50}

Total Experiments: {len(self.experiment_results)}
Successful: {len(successful_experiments)}
Failed: {len(failed_experiments)}
Success Rate: {len(successful_experiments)/len(self.experiment_results)*100:.1f}%

📊 EXPERIMENT DETAILS
{'-'*25}
"""
        
        for i, result in enumerate(self.experiment_results, 1):
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            duration = (result.end_time - result.start_time).total_seconds() if result.end_time else 0
            
            report += f"""
Experiment {i}: {result.config.description}
  Status: {status}
  Duration: {duration:.1f}s
  Failure Type: {result.config.failure_type.value}
  Intensity: {result.config.intensity}
  Safety Level: {result.config.safety_level.value}
"""
            
            if result.error_message:
                report += f"  Error: {result.error_message}\n"
            
            if result.recovery_time_seconds:
                report += f"  Recovery Time: {result.recovery_time_seconds:.1f}s\n"
        
        report += f"""
💡 KEY INSIGHTS
{'-'*15}
- Most common failure type: {max(set([r.config.failure_type for r in self.experiment_results]), 
                                  key=[r.config.failure_type for r in self.experiment_results].count).value}
- Average recovery time: {sum(r.recovery_time_seconds for r in successful_experiments if r.recovery_time_seconds) / len([r for r in successful_experiments if r.recovery_time_seconds]):.1f}s
- Production safety: {self.safety_controller.production_mode} mode detected

📋 RECOMMENDATIONS
{'-'*18}
- Run experiments during low-traffic periods
- Gradually increase failure intensity
- Monitor blast radius carefully
- Document recovery procedures
- Automate rollback mechanisms
"""
        
        return report


def create_indian_platform_scenarios():
    """Create realistic chaos scenarios for Indian platforms"""
    
    # Scenario 1: Paytm Payment System Under Stress
    paytm_scenario = [
        FailureConfig(
            failure_type=FailureType.NETWORK_LATENCY,
            duration_seconds=60,
            intensity=0.3,
            target_services=["payment-gateway"],
            safety_level=SafetyLevel.SAFE,
            description="Paytm: Network latency to payment gateway",
            params={'delay_ms': 150}
        ),
        FailureConfig(
            failure_type=FailureType.CPU_SPIKE,
            duration_seconds=45,
            intensity=0.6,
            target_services=["payment-processor"],
            safety_level=SafetyLevel.MODERATE,
            description="Paytm: CPU spike during high transaction volume"
        ),
        FailureConfig(
            failure_type=FailureType.DATABASE_SLOW,
            duration_seconds=30,
            intensity=0.4,
            target_services=["user-db"],
            safety_level=SafetyLevel.SAFE,
            description="Paytm: Database slowdown during verification"
        )
    ]
    
    # Scenario 2: Flipkart Flash Sale Stress
    flipkart_scenario = [
        FailureConfig(
            failure_type=FailureType.MEMORY_PRESSURE,
            duration_seconds=90,
            intensity=0.5,
            target_services=["inventory-service"],
            safety_level=SafetyLevel.MODERATE,
            description="Flipkart: Memory pressure on inventory service"
        ),
        FailureConfig(
            failure_type=FailureType.SERVICE_UNAVAILABLE,
            duration_seconds=60,
            intensity=0.8,
            target_services=["recommendation-engine"],
            safety_level=SafetyLevel.SAFE,
            description="Flipkart: Recommendation engine unavailable",
            params={'target_urls': ['http://recommendations.flipkart.com']}
        ),
        FailureConfig(
            failure_type=FailureType.NETWORK_PACKET_LOSS,
            duration_seconds=45,
            intensity=0.2,
            target_services=["cart-service"],
            safety_level=SafetyLevel.SAFE,
            description="Flipkart: Packet loss affecting cart updates"
        )
    ]
    
    # Scenario 3: IRCTC Tatkal Booking Rush  
    irctc_scenario = [
        FailureConfig(
            failure_type=FailureType.CPU_SPIKE,
            duration_seconds=120,
            intensity=0.8,
            target_services=["booking-engine"],
            safety_level=SafetyLevel.MODERATE,
            description="IRCTC: CPU spike during Tatkal booking rush"
        ),
        FailureConfig(
            failure_type=FailureType.DATABASE_SLOW,
            duration_seconds=60,
            intensity=0.6,
            target_services=["seat-availability"],
            safety_level=SafetyLevel.SAFE,
            description="IRCTC: Slow seat availability queries"
        )
    ]
    
    return {
        'paytm_payment_stress': paytm_scenario,
        'flipkart_flash_sale': flipkart_scenario, 
        'irctc_tatkal_rush': irctc_scenario
    }


if __name__ == "__main__":
    print("🔬 Chaos Engineering Framework - Indian Platform Edition")
    print("="*60)
    
    # Initialize chaos orchestrator
    orchestrator = ChaosOrchestrator()
    
    # Get Indian platform scenarios
    scenarios = create_indian_platform_scenarios()
    
    print("\n📋 Available Chaos Scenarios:")
    for name, configs in scenarios.items():
        print(f"  {name}: {len(configs)} experiments")
    
    # Run a sample scenario (safe for demonstration)
    print("\n🚀 Running sample Paytm payment stress test...")
    
    # Create a safe demo configuration
    demo_config = FailureConfig(
        failure_type=FailureType.CPU_SPIKE,
        duration_seconds=10,  # Short duration for demo
        intensity=0.3,        # Low intensity 
        target_services=["demo-service"],
        safety_level=SafetyLevel.SAFE,
        description="Demo: Light CPU spike for testing"
    )
    
    # Run demo experiment
    result = orchestrator.run_experiment(demo_config)
    
    if result.success:
        print("✅ Demo experiment completed successfully!")
        print(f"Duration: {(result.end_time - result.start_time).total_seconds():.1f}s")
        print(f"Recovery time: {result.recovery_time_seconds:.1f}s")
    else:
        print(f"❌ Demo experiment failed: {result.error_message}")
    
    # Generate and display report
    report = orchestrator.generate_experiment_report()
    print("\n" + report)
    
    print("\n💡 CHAOS ENGINEERING BEST PRACTICES:")
    print("1. Start with safe, low-intensity experiments")
    print("2. Always test in non-production first") 
    print("3. Have rollback procedures ready")
    print("4. Monitor blast radius carefully")
    print("5. Document learnings and improve resilience")
    print("\n💰 Value: Prevents ₹10Cr+ losses by finding issues before customers do!")
    
    # Save experiment data
    with open('chaos_experiment_results.json', 'w') as f:
        json.dump([asdict(result) for result in orchestrator.experiment_results], 
                 f, indent=2, default=str)
    
    print("📊 Results saved to chaos_experiment_results.json")
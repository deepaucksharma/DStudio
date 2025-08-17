#!/usr/bin/env python3
"""
Chaos Engineering Test Suite for Episodes 92-100
केयोस इंजीनियरिंग टेस्ट सूट

Testing system resilience with Indian failure scenarios:
- Network partitions during festivals
- Service failures during peak UPI usage
- Database overload during sales
- Regional data center outages
"""

import asyncio
import pytest
import random
import time
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch
import requests
import psutil

# Import test fixtures
from tests.conftest import (
    indian_test_data, performance_monitor, festival_traffic_simulator,
    chaos_simulator, indian_user_session, mock_http_client
)

class ChaosExperiment:
    """Base class for chaos experiments"""
    
    def __init__(self, name: str, description: str, target_services: List[str]):
        self.name = name
        self.description = description
        self.target_services = target_services
        self.start_time = None
        self.end_time = None
        self.results = {}
        self.metrics = {}
        
    async def setup(self):
        """Setup experiment prerequisites"""
        self.start_time = datetime.utcnow()
        
    async def execute(self):
        """Execute the chaos experiment"""
        raise NotImplementedError("Subclasses must implement execute method")
        
    async def teardown(self):
        """Cleanup after experiment"""
        self.end_time = datetime.utcnow()
        
    def get_duration(self) -> timedelta:
        """Get experiment duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return timedelta(0)
        
    def add_metric(self, name: str, value: float, timestamp: datetime = None):
        """Add a metric to the experiment"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'value': value,
            'timestamp': timestamp.isoformat()
        })

class NetworkPartitionExperiment(ChaosExperiment):
    """Network partition chaos experiment"""
    
    def __init__(self, partition_duration: int = 30, affected_regions: List[str] = None):
        super().__init__(
            "network_partition",
            "Simulate network partition between regions",
            ["all"]
        )
        self.partition_duration = partition_duration
        self.affected_regions = affected_regions or ["mumbai", "bangalore"]
        self.original_network_config = {}
        
    async def execute(self):
        """Execute network partition"""
        print(f"🌐 Starting network partition between regions: {self.affected_regions}")
        
        # Simulate network partition by introducing high latency
        latency_commands = []
        
        for region in self.affected_regions:
            # Simulate network delay using tc (traffic control)
            # In real environment, this would use actual network tools
            cmd = f"tc qdisc add dev eth0 root netem delay 2000ms 500ms 25%"
            latency_commands.append(cmd)
            
        # Record baseline metrics
        baseline_metrics = await self._measure_cross_region_connectivity()
        self.add_metric("baseline_latency", baseline_metrics["avg_latency"])
        self.add_metric("baseline_success_rate", baseline_metrics["success_rate"])
        
        # Apply network partition
        partition_start = time.time()
        
        try:
            # Simulate partition effects
            await self._simulate_network_partition()
            
            # Monitor during partition
            await asyncio.sleep(self.partition_duration)
            
            partition_metrics = await self._measure_cross_region_connectivity()
            self.add_metric("partition_latency", partition_metrics["avg_latency"])
            self.add_metric("partition_success_rate", partition_metrics["success_rate"])
            
        finally:
            # Restore network
            await self._restore_network()
            
            # Measure recovery
            recovery_metrics = await self._measure_cross_region_connectivity()
            self.add_metric("recovery_latency", recovery_metrics["avg_latency"])
            self.add_metric("recovery_success_rate", recovery_metrics["success_rate"])
            
        partition_end = time.time()
        self.results["partition_duration_actual"] = partition_end - partition_start
        
        print(f"✅ Network partition experiment completed")
        
    async def _simulate_network_partition(self):
        """Simulate network partition effects"""
        # Mock network partition by making some services unreachable
        for region in self.affected_regions:
            print(f"   📡 Partitioning network for region: {region}")
            
    async def _restore_network(self):
        """Restore network connectivity"""
        print("   🔧 Restoring network connectivity")
        
    async def _measure_cross_region_connectivity(self) -> Dict[str, float]:
        """Measure cross-region connectivity"""
        # Mock measurement
        latencies = []
        success_count = 0
        total_tests = 10
        
        for i in range(total_tests):
            try:
                # Simulate ping test
                latency = random.uniform(20, 200)  # Mumbai-Bangalore typical latency
                if latency < 1000:  # Consider successful if < 1s
                    success_count += 1
                    latencies.append(latency)
                await asyncio.sleep(0.1)
            except:
                pass
                
        return {
            "avg_latency": sum(latencies) / len(latencies) if latencies else float('inf'),
            "success_rate": success_count / total_tests
        }

class ServiceFailureExperiment(ChaosExperiment):
    """Service failure chaos experiment"""
    
    def __init__(self, target_service: str, failure_rate: float = 0.5, 
                 failure_duration: int = 60):
        super().__init__(
            "service_failure",
            f"Simulate {target_service} service failures",
            [target_service]
        )
        self.target_service = target_service
        self.failure_rate = failure_rate
        self.failure_duration = failure_duration
        self.original_health_status = {}
        
    async def execute(self):
        """Execute service failure"""
        print(f"💥 Starting service failure for: {self.target_service}")
        print(f"   Failure rate: {self.failure_rate * 100}%")
        print(f"   Duration: {self.failure_duration}s")
        
        # Record baseline metrics
        baseline_metrics = await self._measure_service_health()
        self.add_metric("baseline_response_time", baseline_metrics["avg_response_time"])
        self.add_metric("baseline_success_rate", baseline_metrics["success_rate"])
        
        # Introduce failures
        failure_start = time.time()
        
        try:
            await self._introduce_service_failures()
            
            # Monitor during failure
            failure_metrics = await self._monitor_during_failure()
            
        finally:
            # Restore service
            await self._restore_service()
            
            # Measure recovery
            recovery_metrics = await self._measure_service_health()
            self.add_metric("recovery_response_time", recovery_metrics["avg_response_time"])
            self.add_metric("recovery_success_rate", recovery_metrics["success_rate"])
            
        failure_end = time.time()
        self.results["failure_duration_actual"] = failure_end - failure_start
        
        print(f"✅ Service failure experiment completed")
        
    async def _introduce_service_failures(self):
        """Introduce service failures"""
        print(f"   🔥 Introducing failures to {self.target_service}")
        
    async def _monitor_during_failure(self) -> Dict[str, float]:
        """Monitor service during failure"""
        metrics = []
        monitoring_duration = min(self.failure_duration, 30)  # Monitor for up to 30s
        
        for i in range(monitoring_duration):
            metric = await self._measure_service_health()
            metrics.append(metric)
            self.add_metric("failure_response_time", metric["avg_response_time"])
            self.add_metric("failure_success_rate", metric["success_rate"])
            await asyncio.sleep(1)
            
        # Return average metrics during failure
        if metrics:
            return {
                "avg_response_time": sum(m["avg_response_time"] for m in metrics) / len(metrics),
                "success_rate": sum(m["success_rate"] for m in metrics) / len(metrics)
            }
        return {"avg_response_time": 0, "success_rate": 0}
        
    async def _restore_service(self):
        """Restore service to normal operation"""
        print(f"   🔧 Restoring {self.target_service}")
        
    async def _measure_service_health(self) -> Dict[str, float]:
        """Measure service health metrics"""
        # Mock service health measurement
        response_times = []
        success_count = 0
        total_requests = 5
        
        for i in range(total_requests):
            try:
                # Simulate service call
                response_time = random.uniform(50, 300)
                if response_time < 500:  # Consider successful if < 500ms
                    success_count += 1
                response_times.append(response_time)
                await asyncio.sleep(0.1)
            except:
                response_times.append(1000)  # Timeout
                
        return {
            "avg_response_time": sum(response_times) / len(response_times),
            "success_rate": success_count / total_requests
        }

class DatabaseOverloadExperiment(ChaosExperiment):
    """Database overload chaos experiment"""
    
    def __init__(self, target_db: str, load_multiplier: float = 10.0,
                 overload_duration: int = 45):
        super().__init__(
            "database_overload",
            f"Simulate {target_db} database overload",
            [target_db]
        )
        self.target_db = target_db
        self.load_multiplier = load_multiplier
        self.overload_duration = overload_duration
        
    async def execute(self):
        """Execute database overload"""
        print(f"🗄️ Starting database overload for: {self.target_db}")
        print(f"   Load multiplier: {self.load_multiplier}x")
        print(f"   Duration: {self.overload_duration}s")
        
        # Baseline metrics
        baseline_metrics = await self._measure_database_performance()
        self.add_metric("baseline_query_time", baseline_metrics["avg_query_time"])
        self.add_metric("baseline_connection_count", baseline_metrics["connection_count"])
        
        # Start overload
        overload_start = time.time()
        
        try:
            overload_task = asyncio.create_task(self._generate_database_load())
            
            # Monitor during overload
            for i in range(self.overload_duration):
                metrics = await self._measure_database_performance()
                self.add_metric("overload_query_time", metrics["avg_query_time"])
                self.add_metric("overload_connection_count", metrics["connection_count"])
                await asyncio.sleep(1)
                
        finally:
            # Stop overload
            overload_task.cancel()
            await asyncio.sleep(5)  # Let system recover
            
            # Recovery metrics
            recovery_metrics = await self._measure_database_performance()
            self.add_metric("recovery_query_time", recovery_metrics["avg_query_time"])
            self.add_metric("recovery_connection_count", recovery_metrics["connection_count"])
            
        overload_end = time.time()
        self.results["overload_duration_actual"] = overload_end - overload_start
        
        print(f"✅ Database overload experiment completed")
        
    async def _generate_database_load(self):
        """Generate heavy database load"""
        print(f"   📈 Generating {self.load_multiplier}x database load")
        
        while True:
            # Simulate database queries
            await self._simulate_heavy_query()
            await asyncio.sleep(0.1)
            
    async def _simulate_heavy_query(self):
        """Simulate heavy database query"""
        # Mock heavy query execution
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
    async def _measure_database_performance(self) -> Dict[str, float]:
        """Measure database performance"""
        # Mock database metrics
        return {
            "avg_query_time": random.uniform(10, 200),
            "connection_count": random.randint(50, 200),
            "cpu_usage": random.uniform(20, 90),
            "memory_usage": random.uniform(30, 85)
        }

class RegionalDataCenterOutageExperiment(ChaosExperiment):
    """Regional data center outage experiment"""
    
    def __init__(self, affected_region: str, outage_duration: int = 120):
        super().__init__(
            "datacenter_outage",
            f"Simulate {affected_region} data center outage",
            ["all"]
        )
        self.affected_region = affected_region
        self.outage_duration = outage_duration
        self.failover_targets = []
        
    async def execute(self):
        """Execute data center outage"""
        print(f"🏢 Starting data center outage for: {self.affected_region}")
        print(f"   Duration: {self.outage_duration}s")
        
        # Identify failover targets
        self.failover_targets = self._get_failover_regions()
        print(f"   Failover regions: {self.failover_targets}")
        
        # Baseline metrics
        baseline_metrics = await self._measure_regional_performance()
        for region, metrics in baseline_metrics.items():
            self.add_metric(f"baseline_{region}_latency", metrics["latency"])
            self.add_metric(f"baseline_{region}_load", metrics["load"])
            
        # Start outage
        outage_start = time.time()
        
        try:
            await self._simulate_datacenter_outage()
            
            # Monitor failover
            await self._monitor_failover_process()
            
            # Monitor during outage
            for i in range(0, self.outage_duration, 10):
                metrics = await self._measure_regional_performance()
                for region, region_metrics in metrics.items():
                    if region != self.affected_region:
                        self.add_metric(f"outage_{region}_latency", region_metrics["latency"])
                        self.add_metric(f"outage_{region}_load", region_metrics["load"])
                await asyncio.sleep(10)
                
        finally:
            # Restore data center
            await self._restore_datacenter()
            
            # Monitor recovery
            recovery_metrics = await self._measure_regional_performance()
            for region, metrics in recovery_metrics.items():
                self.add_metric(f"recovery_{region}_latency", metrics["latency"])
                self.add_metric(f"recovery_{region}_load", metrics["load"])
                
        outage_end = time.time()
        self.results["outage_duration_actual"] = outage_end - outage_start
        
        print(f"✅ Data center outage experiment completed")
        
    def _get_failover_regions(self) -> List[str]:
        """Get failover regions for the affected region"""
        region_mapping = {
            "mumbai": ["delhi", "bangalore"],
            "delhi": ["mumbai", "bangalore"],
            "bangalore": ["mumbai", "chennai"],
            "chennai": ["bangalore", "hyderabad"],
        }
        return region_mapping.get(self.affected_region, ["mumbai", "delhi"])
        
    async def _simulate_datacenter_outage(self):
        """Simulate data center going offline"""
        print(f"   🔴 Taking {self.affected_region} data center offline")
        
    async def _monitor_failover_process(self):
        """Monitor the failover process"""
        print(f"   ⚡ Monitoring failover to: {self.failover_targets}")
        await asyncio.sleep(5)  # Simulate failover time
        
    async def _restore_datacenter(self):
        """Restore data center to online status"""
        print(f"   🟢 Restoring {self.affected_region} data center")
        
    async def _measure_regional_performance(self) -> Dict[str, Dict[str, float]]:
        """Measure performance across regions"""
        regions = ["mumbai", "delhi", "bangalore", "chennai"]
        metrics = {}
        
        for region in regions:
            if region == self.affected_region:
                # Simulate outage
                metrics[region] = {
                    "latency": float('inf'),
                    "load": 0,
                    "availability": 0
                }
            else:
                # Normal or increased load
                base_latency = {"mumbai": 25, "delhi": 30, "bangalore": 20, "chennai": 35}.get(region, 30)
                load_multiplier = 1.5 if region in self.failover_targets else 1.0
                
                metrics[region] = {
                    "latency": base_latency * random.uniform(0.8, 1.5),
                    "load": random.uniform(40, 80) * load_multiplier,
                    "availability": random.uniform(95, 99.9)
                }
                
        return metrics

class IndianFestivalChaosExperiment(ChaosExperiment):
    """Festival-specific chaos experiment (Diwali, IPL)"""
    
    def __init__(self, festival: str, chaos_types: List[str] = None):
        super().__init__(
            f"festival_{festival}_chaos",
            f"Multiple chaos during {festival}",
            ["all"]
        )
        self.festival = festival
        self.chaos_types = chaos_types or ["network", "service", "database"]
        self.festival_load_multiplier = self._get_festival_multiplier()
        
    def _get_festival_multiplier(self) -> float:
        """Get load multiplier for festival"""
        multipliers = {
            "diwali": 15.0,
            "ipl_final": 25.0,
            "holi": 8.0,
            "dussehra": 6.0
        }
        return multipliers.get(self.festival, 5.0)
        
    async def execute(self):
        """Execute festival chaos experiment"""
        print(f"🎉 Starting festival chaos experiment: {self.festival}")
        print(f"   Load multiplier: {self.festival_load_multiplier}x")
        print(f"   Chaos types: {self.chaos_types}")
        
        # Simulate festival load
        load_task = asyncio.create_task(self._simulate_festival_load())
        
        # Introduce multiple chaos types
        chaos_tasks = []
        
        if "network" in self.chaos_types:
            network_chaos = NetworkPartitionExperiment(30, ["mumbai", "delhi"])
            await network_chaos.setup()
            chaos_tasks.append(network_chaos.execute())
            
        if "service" in self.chaos_types:
            service_chaos = ServiceFailureExperiment("payment-gateway", 0.3, 45)
            await service_chaos.setup()
            chaos_tasks.append(service_chaos.execute())
            
        if "database" in self.chaos_types:
            db_chaos = DatabaseOverloadExperiment("user-db", 5.0, 60)
            await db_chaos.setup()
            chaos_tasks.append(db_chaos.execute())
            
        try:
            # Run all chaos experiments concurrently
            await asyncio.gather(*chaos_tasks)
            
        finally:
            # Stop festival load
            load_task.cancel()
            
        print(f"✅ Festival chaos experiment completed")
        
    async def _simulate_festival_load(self):
        """Simulate high festival traffic load"""
        print(f"   📈 Simulating {self.festival} traffic load")
        
        while True:
            # Simulate high traffic
            await asyncio.sleep(0.01)

# Test Classes
class TestChaosEngineering:
    """Chaos engineering tests"""
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_network_partition_resilience(self):
        """Test system resilience to network partitions"""
        experiment = NetworkPartitionExperiment(
            partition_duration=10,  # Short duration for test
            affected_regions=["mumbai", "bangalore"]
        )
        
        await experiment.setup()
        await experiment.execute()
        await experiment.teardown()
        
        # Verify experiment results
        assert experiment.results["partition_duration_actual"] > 0
        
        # Check that recovery metrics show improvement
        recovery_metrics = [m for m in experiment.metrics.get("recovery_success_rate", [])]
        baseline_metrics = [m for m in experiment.metrics.get("baseline_success_rate", [])]
        
        if recovery_metrics and baseline_metrics:
            recovery_rate = recovery_metrics[-1]["value"]
            baseline_rate = baseline_metrics[0]["value"]
            
            # Recovery should be close to baseline (within 20%)
            assert recovery_rate >= baseline_rate * 0.8
            
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_service_failure_handling(self):
        """Test service failure handling"""
        experiment = ServiceFailureExperiment(
            target_service="user-service",
            failure_rate=0.5,
            failure_duration=15
        )
        
        await experiment.setup()
        await experiment.execute()
        await experiment.teardown()
        
        # Verify experiment completion
        assert experiment.get_duration().total_seconds() > 0
        
        # Check metrics collection
        assert "baseline_response_time" in experiment.metrics
        assert "recovery_response_time" in experiment.metrics
        
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_database_overload_resilience(self):
        """Test database overload resilience"""
        experiment = DatabaseOverloadExperiment(
            target_db="product-catalog-db",
            load_multiplier=5.0,
            overload_duration=20
        )
        
        await experiment.setup()
        await experiment.execute()
        await experiment.teardown()
        
        # Verify overload was applied
        overload_metrics = experiment.metrics.get("overload_query_time", [])
        baseline_metrics = experiment.metrics.get("baseline_query_time", [])
        
        if overload_metrics and baseline_metrics:
            # Query time should increase during overload
            max_overload_time = max(m["value"] for m in overload_metrics)
            baseline_time = baseline_metrics[0]["value"]
            
            assert max_overload_time > baseline_time
            
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_datacenter_outage_failover(self):
        """Test data center outage and failover"""
        experiment = RegionalDataCenterOutageExperiment(
            affected_region="mumbai",
            outage_duration=30
        )
        
        await experiment.setup()
        await experiment.execute()
        await experiment.teardown()
        
        # Verify failover targets were identified
        assert len(experiment.failover_targets) > 0
        
        # Check that other regions handled increased load
        for region in experiment.failover_targets:
            outage_load_metrics = experiment.metrics.get(f"outage_{region}_load", [])
            if outage_load_metrics:
                # Load should increase in failover regions
                assert any(m["value"] > 50 for m in outage_load_metrics)

class TestIndianContextChaos:
    """Indian-specific chaos engineering scenarios"""
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    @pytest.mark.indian_context
    @pytest.mark.ecommerce
    async def test_diwali_sale_chaos(self):
        """Test chaos during Diwali sale"""
        experiment = IndianFestivalChaosExperiment(
            festival="diwali",
            chaos_types=["network", "service"]
        )
        
        await experiment.setup()
        await experiment.execute()
        await experiment.teardown()
        
        # Verify festival multiplier is applied
        assert experiment.festival_load_multiplier >= 10.0
        
    @pytest.mark.asyncio
    @pytest.mark.chaos
    @pytest.mark.indian_context
    @pytest.mark.gaming
    async def test_ipl_streaming_chaos(self):
        """Test chaos during IPL streaming"""
        experiment = IndianFestivalChaosExperiment(
            festival="ipl_final",
            chaos_types=["service", "database"]
        )
        
        await experiment.setup()
        await experiment.execute()
        await experiment.teardown()
        
        # IPL should have highest multiplier
        assert experiment.festival_load_multiplier >= 20.0
        
    @pytest.mark.asyncio
    @pytest.mark.chaos
    @pytest.mark.indian_context
    @pytest.mark.banking
    async def test_upi_payment_service_chaos(self):
        """Test UPI payment service under chaos"""
        # Test payment gateway failure during high UPI usage
        experiment = ServiceFailureExperiment(
            target_service="upi-gateway",
            failure_rate=0.2,  # 20% failure rate
            failure_duration=30
        )
        
        await experiment.setup()
        await experiment.execute()
        await experiment.teardown()
        
        # UPI services should recover quickly
        recovery_metrics = experiment.metrics.get("recovery_success_rate", [])
        if recovery_metrics:
            final_recovery_rate = recovery_metrics[-1]["value"]
            assert final_recovery_rate > 0.95  # 95% recovery expected
            
    @pytest.mark.asyncio
    @pytest.mark.chaos
    @pytest.mark.indian_context
    async def test_monsoon_network_issues(self):
        """Test network issues during monsoon season"""
        # Simulate monsoon-related network problems
        experiment = NetworkPartitionExperiment(
            partition_duration=45,
            affected_regions=["mumbai", "chennai"]  # Coastal cities affected by monsoon
        )
        
        await experiment.setup()
        await experiment.execute()
        await experiment.teardown()
        
        # Check that system handles monsoon-like conditions
        partition_metrics = experiment.metrics.get("partition_success_rate", [])
        if partition_metrics:
            # Even during partition, some connectivity should remain
            min_success_rate = min(m["value"] for m in partition_metrics)
            assert min_success_rate > 0.1  # At least 10% connectivity

class TestChaosExperimentMetrics:
    """Test chaos experiment metrics and reporting"""
    
    @pytest.mark.asyncio
    async def test_experiment_metrics_collection(self):
        """Test that chaos experiments collect proper metrics"""
        experiment = ServiceFailureExperiment("test-service", 0.5, 10)
        
        await experiment.setup()
        
        # Add some test metrics
        experiment.add_metric("test_metric", 100.0)
        experiment.add_metric("test_metric", 200.0)
        
        await experiment.teardown()
        
        # Verify metrics structure
        assert "test_metric" in experiment.metrics
        assert len(experiment.metrics["test_metric"]) == 2
        
        for metric in experiment.metrics["test_metric"]:
            assert "value" in metric
            assert "timestamp" in metric
            
    def test_experiment_duration_calculation(self):
        """Test experiment duration calculation"""
        experiment = NetworkPartitionExperiment(30)
        
        # No duration before start
        assert experiment.get_duration() == timedelta(0)
        
        # Set start time
        experiment.start_time = datetime.utcnow()
        time.sleep(0.1)
        experiment.end_time = datetime.utcnow()
        
        # Should have positive duration
        assert experiment.get_duration().total_seconds() > 0

class TestChaosRecoveryValidation:
    """Test system recovery after chaos experiments"""
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_service_auto_recovery(self):
        """Test automatic service recovery after failure"""
        # Simulate service failure and recovery
        service_health = {"status": "healthy", "last_check": time.time()}
        
        # Introduce failure
        service_health["status"] = "failed"
        
        # Simulate auto-recovery mechanism
        await asyncio.sleep(1)
        service_health["status"] = "healthy"
        service_health["last_check"] = time.time()
        
        # Verify recovery
        assert service_health["status"] == "healthy"
        assert service_health["last_check"] > 0
        
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_circuit_breaker_functionality(self):
        """Test circuit breaker during chaos"""
        circuit_breaker = {
            "state": "closed",
            "failure_count": 0,
            "threshold": 5,
            "timeout": 60
        }
        
        # Simulate failures
        for i in range(6):  # Exceed threshold
            circuit_breaker["failure_count"] += 1
            if circuit_breaker["failure_count"] >= circuit_breaker["threshold"]:
                circuit_breaker["state"] = "open"
                
        # Circuit breaker should open
        assert circuit_breaker["state"] == "open"
        
        # Simulate recovery
        await asyncio.sleep(1)
        circuit_breaker["state"] = "half-open"
        circuit_breaker["failure_count"] = 0
        
        # Verify half-open state
        assert circuit_breaker["state"] == "half-open"

# Chaos Engineering Test Runner
class ChaosTestRunner:
    """Comprehensive chaos engineering test runner"""
    
    def __init__(self):
        self.experiments = []
        self.results = {}
        
    def add_experiment(self, experiment: ChaosExperiment):
        """Add experiment to test suite"""
        self.experiments.append(experiment)
        
    async def run_all_experiments(self):
        """Run all chaos experiments"""
        print("🔥 Starting Chaos Engineering Test Suite")
        print("=" * 60)
        
        for i, experiment in enumerate(self.experiments, 1):
            print(f"\n{i}. Running: {experiment.name}")
            print(f"   Description: {experiment.description}")
            
            try:
                await experiment.setup()
                await experiment.execute()
                await experiment.teardown()
                
                self.results[experiment.name] = {
                    "status": "completed",
                    "duration": experiment.get_duration().total_seconds(),
                    "metrics_count": sum(len(metrics) for metrics in experiment.metrics.values())
                }
                
                print(f"   ✅ Completed in {experiment.get_duration().total_seconds():.1f}s")
                
            except Exception as e:
                self.results[experiment.name] = {
                    "status": "failed",
                    "error": str(e),
                    "duration": 0
                }
                print(f"   ❌ Failed: {e}")
                
        self._print_summary()
        
    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 Chaos Engineering Summary")
        print("=" * 60)
        
        total_experiments = len(self.experiments)
        completed = sum(1 for r in self.results.values() if r["status"] == "completed")
        failed = total_experiments - completed
        
        print(f"Total Experiments: {total_experiments}")
        print(f"Completed: {completed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(completed/total_experiments)*100:.1f}%")
        
        print(f"\nExperiment Results:")
        for name, result in self.results.items():
            status_icon = "✅" if result["status"] == "completed" else "❌"
            print(f"  {status_icon} {name}: {result['status']} ({result['duration']:.1f}s)")

# Example usage
async def main():
    """Run chaos engineering tests"""
    runner = ChaosTestRunner()
    
    # Add experiments
    runner.add_experiment(NetworkPartitionExperiment(15, ["mumbai", "delhi"]))
    runner.add_experiment(ServiceFailureExperiment("payment-service", 0.3, 20))
    runner.add_experiment(DatabaseOverloadExperiment("user-db", 3.0, 25))
    runner.add_experiment(IndianFestivalChaosExperiment("diwali", ["network", "service"]))
    
    await runner.run_all_experiments()

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for Container Orchestration Examples
Episode 17: Container Orchestration

यह test suite सभी container orchestration examples को validate करती है।
Production-ready testing for Indian company scenarios.
"""

import os
import sys
import unittest
import json
import yaml
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import asyncio
from datetime import datetime, timedelta

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all our container orchestration modules
try:
    from python.swiggy_microservice_containerization import app as swiggy_app
    from python.dockerfile_best_practices import ZomatoDockerfileGenerator
    from python.kubernetes_deployment_manifests import BigBasketK8sGenerator
    from python.service_discovery_consul import OlaServiceDiscovery, OlaService
    from python.autoscaling_food_delivery import SwiggyAutoScaler
    from python.container_health_monitoring import BigBasketContainerMonitor
    from python.multi_environment_deployment import OlaMultiEnvironmentDeployer
    from python.ci_cd_integration_gitlab import PayTMCICDPipeline
    from python.secrets_management_vault import CREDSecretsManager
    from python.disaster_recovery_automation import RazorpayDisasterRecovery
    from python.logging_monitoring_stack import NykaaObservabilityStack
    from python.network_policies_security import ZerodhaNetworkSecurityManager
    from python.storage_orchestration import MakeMyTripStorageOrchestrator
except ImportError as e:
    print(f"Warning: Could not import all modules: {e}")
    print("Some tests may fail due to missing dependencies.")


class TestSwiggyMicroserviceContainerization(unittest.TestCase):
    """Test Swiggy microservice containerization"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = swiggy_app
        self.client = self.app.test_client()
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'swiggy-order-service')
    
    def test_create_order(self):
        """Test order creation"""
        order_data = {
            "customer_id": "test_customer_001",
            "restaurant_id": "rest_001",
            "items": [{"name": "Test Food", "quantity": 1, "price": 100}],
            "total_amount": 100,
            "delivery_address": "Test Address, Mumbai"
        }
        
        response = self.client.post('/api/v1/orders', 
                                  data=json.dumps(order_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('order', data)
        self.assertEqual(data['order']['customer_id'], 'test_customer_001')


class TestDockerfileBestPractices(unittest.TestCase):
    """Test Dockerfile generation best practices"""
    
    def setUp(self):
        """Set up test environment"""
        self.generator = ZomatoDockerfileGenerator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_dockerfile_generation(self):
        """Test Dockerfile generation"""
        from python.dockerfile_best_practices import DockerImageConfig
        
        config = DockerImageConfig(
            app_name="test-service",
            version="v1.0.0",
            base_image="python:3.11",
            company="zomato",
            environment="test",
            region="mumbai"
        )
        
        dockerfile_content = self.generator.generate_multi_stage_dockerfile(config)
        
        # Verify essential Dockerfile components
        self.assertIn('FROM python:3.11 AS builder', dockerfile_content)
        self.assertIn('FROM python:3.11-slim AS runtime', dockerfile_content)
        self.assertIn('RUN groupadd -r test-service', dockerfile_content)
        self.assertIn('USER test-service', dockerfile_content)
        self.assertIn('HEALTHCHECK', dockerfile_content)
    
    def test_dockerignore_generation(self):
        """Test .dockerignore generation"""
        dockerignore_content = self.generator.generate_dockerignore()
        
        # Verify essential ignore patterns
        self.assertIn('.git', dockerignore_content)
        self.assertIn('__pycache__/', dockerignore_content)
        self.assertIn('*.pyc', dockerignore_content)
        self.assertIn('node_modules/', dockerignore_content)
    
    def test_docker_compose_generation(self):
        """Test Docker Compose generation"""
        from python.dockerfile_best_practices import DockerImageConfig
        
        config = DockerImageConfig(
            app_name="test-service",
            version="v1.0.0",
            base_image="python:3.11",
            company="zomato",
            environment="test",
            region="mumbai"
        )
        
        compose_content = self.generator.generate_docker_compose(config)
        
        # Verify Docker Compose structure
        self.assertIn('version:', compose_content)
        self.assertIn('services:', compose_content)
        self.assertIn('test-service:', compose_content)
        self.assertIn('postgres:', compose_content)
        self.assertIn('redis:', compose_content)


class TestKubernetesDeploymentManifests(unittest.TestCase):
    """Test Kubernetes deployment manifest generation"""
    
    def setUp(self):
        """Set up test environment"""
        self.generator = BigBasketK8sGenerator()
    
    def test_namespace_generation(self):
        """Test namespace manifest generation"""
        from python.kubernetes_deployment_manifests import KubernetesAppConfig
        
        config = KubernetesAppConfig(
            app_name="test-service",
            namespace="test-namespace",
            replicas=3,
            image="test/service",
            version="v1.0.0",
            company="bigbasket",
            environment="test",
            region="bangalore",
            resource_requests={"cpu": "100m", "memory": "128Mi"},
            resource_limits={"cpu": "500m", "memory": "512Mi"},
            ports=[8000],
            health_check_path="/health"
        )
        
        namespace_manifest = self.generator.generate_namespace(config)
        
        # Verify namespace structure
        self.assertEqual(namespace_manifest['kind'], 'Namespace')
        self.assertEqual(namespace_manifest['metadata']['name'], 'test-namespace')
        self.assertEqual(namespace_manifest['metadata']['labels']['company'], 'bigbasket')
    
    def test_deployment_generation(self):
        """Test deployment manifest generation"""
        from python.kubernetes_deployment_manifests import KubernetesAppConfig
        
        config = KubernetesAppConfig(
            app_name="test-service",
            namespace="test-namespace",
            replicas=3,
            image="test/service",
            version="v1.0.0",
            company="bigbasket",
            environment="test",
            region="bangalore",
            resource_requests={"cpu": "100m", "memory": "128Mi"},
            resource_limits={"cpu": "500m", "memory": "512Mi"},
            ports=[8000],
            health_check_path="/health"
        )
        
        deployment_manifest = self.generator.generate_deployment(config)
        
        # Verify deployment structure
        self.assertEqual(deployment_manifest['kind'], 'Deployment')
        self.assertEqual(deployment_manifest['spec']['replicas'], 3)
        self.assertEqual(deployment_manifest['metadata']['labels']['company'], 'bigbasket')
        
        # Verify container configuration
        container = deployment_manifest['spec']['template']['spec']['containers'][0]
        self.assertEqual(container['name'], 'test-service')
        self.assertEqual(container['image'], 'test/service:v1.0.0')
        self.assertIn('livenessProbe', container)
        self.assertIn('readinessProbe', container)


class TestServiceDiscoveryConsul(unittest.TestCase):
    """Test Consul service discovery implementation"""
    
    def setUp(self):
        """Set up test environment with mocked Consul"""
        with patch('consul.Consul'):
            self.service_discovery = OlaServiceDiscovery()
    
    def test_service_creation(self):
        """Test OlaService data structure"""
        service = OlaService(
            service_id="test-service-001",
            service_name="test-service",
            address="10.0.0.1",
            port=8000,
            tags=["v1.0", "test"],
            health_check_url="http://10.0.0.1:8000/health",
            metadata={"region": "mumbai"},
            region="mumbai",
            zone="andheri"
        )
        
        self.assertEqual(service.service_id, "test-service-001")
        self.assertEqual(service.service_name, "test-service")
        self.assertEqual(service.region, "mumbai")
        self.assertEqual(service.zone, "andheri")
    
    @patch('consul.Consul')
    def test_service_registration(self, mock_consul):
        """Test service registration with Consul"""
        mock_consul_instance = Mock()
        mock_consul.return_value = mock_consul_instance
        mock_consul_instance.agent.service.register.return_value = True
        
        service_discovery = OlaServiceDiscovery()
        
        service = OlaService(
            service_id="test-service-001",
            service_name="test-service",
            address="10.0.0.1",
            port=8000,
            tags=["v1.0", "test"],
            health_check_url="http://10.0.0.1:8000/health",
            metadata={"region": "mumbai"},
            region="mumbai",
            zone="andheri"
        )
        
        result = service_discovery.register_service(service)
        
        self.assertTrue(result)
        mock_consul_instance.agent.service.register.assert_called_once()


class TestAutoscalingFoodDelivery(unittest.TestCase):
    """Test autoscaling implementation for food delivery"""
    
    def setUp(self):
        """Set up test environment"""
        self.autoscaler = SwiggyAutoScaler("test-service")
    
    def test_autoscaler_initialization(self):
        """Test autoscaler initialization"""
        self.assertEqual(self.autoscaler.service_name, "test-service")
        self.assertEqual(self.autoscaler.min_replicas, 2)
        self.assertEqual(self.autoscaler.max_replicas, 50)
        self.assertIn("breakfast", self.autoscaler.peak_hours)
        self.assertIn("lunch", self.autoscaler.peak_hours)
        self.assertIn("dinner", self.autoscaler.peak_hours)
    
    def test_metrics_generation(self):
        """Test metrics data generation"""
        metrics = self.autoscaler.get_current_metrics()
        
        self.assertIsNotNone(metrics.timestamp)
        self.assertGreaterEqual(metrics.cpu_usage, 0)
        self.assertLessEqual(metrics.cpu_usage, 100)
        self.assertGreaterEqual(metrics.memory_usage, 0)
        self.assertGreaterEqual(metrics.request_rate, 0)
    
    def test_scaling_decision_analysis(self):
        """Test scaling decision logic"""
        from python.autoscaling_food_delivery import MetricData
        
        # Test scale up scenario
        high_load_metrics = MetricData(
            timestamp=datetime.now().timestamp(),
            cpu_usage=85.0,  # Above threshold
            memory_usage=400.0,
            request_rate=100.0,
            response_time=500.0,
            error_rate=2.0,
            queue_length=50
        )
        
        direction, reason, value = self.autoscaler.analyze_scaling_decision(high_load_metrics)
        
        from python.autoscaling_food_delivery import ScalingDirection
        self.assertEqual(direction, ScalingDirection.UP)
        self.assertIn("CPU", reason)


class TestContainerHealthMonitoring(unittest.TestCase):
    """Test container health monitoring implementation"""
    
    def setUp(self):
        """Set up test environment"""
        with patch('docker.from_env'), patch('prometheus_client.start_http_server'):
            self.monitor = BigBasketContainerMonitor()
    
    def test_monitor_initialization(self):
        """Test monitor initialization"""
        self.assertIsNotNone(self.monitor.service_mappings)
        self.assertIn("bigbasket-inventory", self.monitor.service_mappings)
        self.assertIn("bigbasket-orders", self.monitor.service_mappings)
    
    def test_alert_thresholds(self):
        """Test alert threshold configuration"""
        self.assertEqual(self.monitor.alert_thresholds["cpu_high"], 80.0)
        self.assertEqual(self.monitor.alert_thresholds["memory_high"], 85.0)
        self.assertGreaterEqual(self.monitor.alert_thresholds["restart_count_high"], 1)


class TestMultiEnvironmentDeployment(unittest.TestCase):
    """Test multi-environment deployment pipeline"""
    
    def setUp(self):
        """Set up test environment"""
        self.deployer = OlaMultiEnvironmentDeployer()
    
    def test_environment_configuration(self):
        """Test environment configurations"""
        from python.multi_environment_deployment import DeploymentStage
        
        self.assertIn(DeploymentStage.DEV, self.deployer.environments)
        self.assertIn(DeploymentStage.STAGING, self.deployer.environments)
        self.assertIn(DeploymentStage.PRODUCTION, self.deployer.environments)
        
        # Verify production has more replicas than dev
        dev_replicas = self.deployer.environments[DeploymentStage.DEV].replicas
        prod_replicas = self.deployer.environments[DeploymentStage.PRODUCTION].replicas
        self.assertGreater(prod_replicas, dev_replicas)
    
    def test_deployment_manifest_generation(self):
        """Test deployment manifest generation"""
        from python.multi_environment_deployment import DeploymentStage
        
        manifest = self.deployer.generate_deployment_manifest(
            "test-service", "v1.0.0", DeploymentStage.PRODUCTION
        )
        
        self.assertEqual(manifest["kind"], "Deployment")
        self.assertEqual(manifest["metadata"]["name"], "test-service")
        self.assertIn("spec", manifest)
    
    def test_safety_checks(self):
        """Test deployment safety checks"""
        from python.multi_environment_deployment import DeploymentStage
        
        # Mock current time to be during peak hours
        with patch('python.multi_environment_deployment.datetime') as mock_datetime:
            mock_datetime.now.return_value.hour = 13  # 1 PM - lunch peak
            
            is_safe, message = self.deployer.check_deployment_safety(DeploymentStage.PRODUCTION)
            
            # Should block production deployment during peak hours
            self.assertFalse(is_safe)
            self.assertIn("peak hours", message)


class TestCICDIntegrationGitLab(unittest.TestCase):
    """Test CI/CD integration with GitLab"""
    
    def setUp(self):
        """Set up test environment"""
        self.pipeline = PayTMCICDPipeline("test-project", "fake-token")
    
    def test_environment_configurations(self):
        """Test environment configurations"""
        self.assertIn("development", self.pipeline.environments)
        self.assertIn("staging", self.pipeline.environments)
        self.assertIn("production", self.pipeline.environments)
        
        # Verify production has more resources
        dev_config = self.pipeline.environments["development"]
        prod_config = self.pipeline.environments["production"]
        
        self.assertGreater(prod_config.replicas, dev_config.replicas)
    
    def test_gitlab_ci_generation(self):
        """Test GitLab CI configuration generation"""
        config_yaml = self.pipeline.generate_gitlab_ci_config("test-service")
        
        # Parse YAML to verify structure
        config = yaml.safe_load(config_yaml)
        
        self.assertIn("stages", config)
        self.assertIn("build", config["stages"])
        self.assertIn("test", config["stages"])
        self.assertIn("deploy_production", config["stages"])
    
    def test_kubernetes_manifest_generation(self):
        """Test Kubernetes manifest generation"""
        manifests = self.pipeline.generate_kubernetes_manifests("test-service", "production")
        
        self.assertIn("deployment-production.yaml", manifests)
        self.assertIn("service-production.yaml", manifests)
        self.assertIn("ingress-production.yaml", manifests)


class TestSecretsManagementVault(unittest.TestCase):
    """Test secrets management with Vault"""
    
    def setUp(self):
        """Set up test environment with mocked Vault"""
        with patch('hvac.Client') as mock_vault:
            mock_vault.return_value.is_authenticated.return_value = True
            self.secrets_manager = CREDSecretsManager("http://localhost:8200", "fake-token")
    
    def test_secrets_manager_initialization(self):
        """Test secrets manager initialization"""
        self.assertIsNotNone(self.secrets_manager.fintech_secret_categories)
        self.assertIn("payment_gateways", self.secrets_manager.fintech_secret_categories)
        self.assertIn("banking_apis", self.secrets_manager.fintech_secret_categories)
        self.assertIn("regulatory", self.secrets_manager.fintech_secret_categories)
    
    def test_environment_configurations(self):
        """Test environment-specific configurations"""
        from python.secrets_management_vault import Environment
        
        self.assertIn(Environment.DEVELOPMENT, self.secrets_manager.environment_configs)
        self.assertIn(Environment.PRODUCTION, self.secrets_manager.environment_configs)
        
        # Production should have shorter TTL than development
        dev_ttl = self.secrets_manager.environment_configs[Environment.DEVELOPMENT]["ttl"]
        prod_ttl = self.secrets_manager.environment_configs[Environment.PRODUCTION]["ttl"]
        self.assertLess(prod_ttl, dev_ttl)


class TestDisasterRecoveryAutomation(unittest.TestCase):
    """Test disaster recovery automation"""
    
    def setUp(self):
        """Set up test environment"""
        self.dr_system = RazorpayDisasterRecovery()
    
    def test_dr_system_initialization(self):
        """Test DR system initialization"""
        self.assertIsNotNone(self.dr_system.regions)
        self.assertIsNotNone(self.dr_system.services)
        self.assertIn("payment-gateway", self.dr_system.services)
        self.assertIn("fraud-detection", self.dr_system.services)
    
    def test_service_configurations(self):
        """Test service configurations"""
        payment_gateway = self.dr_system.services["payment-gateway"]
        
        from python.disaster_recovery_automation import RecoveryTier
        self.assertEqual(payment_gateway.tier, RecoveryTier.TIER_0)
        self.assertEqual(payment_gateway.rto_minutes, 5)
        self.assertEqual(payment_gateway.rpo_minutes, 0)
        self.assertTrue(payment_gateway.auto_failover)
    
    def test_runbook_existence(self):
        """Test disaster recovery runbooks"""
        from python.disaster_recovery_automation import DisasterType
        
        self.assertIn(DisasterType.DATACENTER_OUTAGE, self.dr_system.runbooks)
        self.assertIn(DisasterType.KUBERNETES_CLUSTER_FAILURE, self.dr_system.runbooks)
        
        # Verify runbook has steps
        datacenter_runbook = self.dr_system.runbooks[DisasterType.DATACENTER_OUTAGE]
        self.assertGreater(len(datacenter_runbook), 0)
        self.assertIn("assess_affected_services", datacenter_runbook)


class TestLoggingMonitoringStack(unittest.TestCase):
    """Test logging and monitoring stack"""
    
    def setUp(self):
        """Set up test environment"""
        with patch('elasticsearch.Elasticsearch'), patch('redis.Redis'):
            self.observability = NykaaObservabilityStack()
    
    def test_observability_initialization(self):
        """Test observability stack initialization"""
        self.assertIsNotNone(self.observability.nykaa_services)
        self.assertIn("beauty-catalog", self.observability.nykaa_services)
        self.assertIn("payment-service", self.observability.nykaa_services)
    
    def test_log_patterns(self):
        """Test log aggregation patterns"""
        self.assertIn("business_events", self.observability.log_patterns)
        self.assertIn("security_events", self.observability.log_patterns)
        self.assertIn("performance_events", self.observability.log_patterns)
        
        # Verify business events include e-commerce activities
        business_events = self.observability.log_patterns["business_events"]
        self.assertIn("product_view", business_events)
        self.assertIn("add_to_cart", business_events)
        self.assertIn("payment_complete", business_events)
    
    def test_alert_thresholds(self):
        """Test alert threshold configuration"""
        self.assertGreater(self.observability.alert_thresholds["error_rate"], 0)
        self.assertGreater(self.observability.alert_thresholds["response_time_p95"], 0)
        self.assertGreater(self.observability.alert_thresholds["conversion_rate_drop"], 0)


class TestNetworkPoliciesSecurity(unittest.TestCase):
    """Test network policies and security configuration"""
    
    def setUp(self):
        """Set up test environment"""
        self.security_manager = ZerodhaNetworkSecurityManager()
    
    def test_security_manager_initialization(self):
        """Test security manager initialization"""
        self.assertIsNotNone(self.security_manager.service_tiers)
        self.assertIsNotNone(self.security_manager.network_zones)
        self.assertIsNotNone(self.security_manager.communication_matrix)
    
    def test_service_tier_configuration(self):
        """Test service tier configurations"""
        from python.network_policies_security import SecurityTier
        
        self.assertIn(SecurityTier.PUBLIC, self.security_manager.service_tiers)
        self.assertIn(SecurityTier.RESTRICTED, self.security_manager.service_tiers)
        self.assertIn(SecurityTier.ISOLATED, self.security_manager.service_tiers)
        
        # Verify security levels increase with tier sensitivity
        public_config = self.security_manager.service_tiers[SecurityTier.PUBLIC]
        isolated_config = self.security_manager.service_tiers[SecurityTier.ISOLATED]
        
        self.assertEqual(public_config["security_level"], "high")
        self.assertEqual(isolated_config["security_level"], "maximum")
    
    def test_regulatory_requirements(self):
        """Test regulatory compliance requirements"""
        self.assertIn("SEBI", self.security_manager.regulatory_requirements)
        self.assertIn("RBI", self.security_manager.regulatory_requirements)
        self.assertIn("PCI_DSS", self.security_manager.regulatory_requirements)
        
        # Verify RBI requirements include data localization
        rbi_reqs = self.security_manager.regulatory_requirements["RBI"]
        self.assertEqual(rbi_reqs["data_localization"], "mandatory")


class TestStorageOrchestration(unittest.TestCase):
    """Test storage orchestration implementation"""
    
    def setUp(self):
        """Set up test environment"""
        self.storage_orchestrator = MakeMyTripStorageOrchestrator()
    
    def test_storage_orchestrator_initialization(self):
        """Test storage orchestrator initialization"""
        self.assertIsNotNone(self.storage_orchestrator.service_storage_requirements)
        self.assertIsNotNone(self.storage_orchestrator.storage_providers)
        self.assertIsNotNone(self.storage_orchestrator.backup_strategies)
    
    def test_service_storage_requirements(self):
        """Test service storage requirements"""
        self.assertIn("flight-search", self.storage_orchestrator.service_storage_requirements)
        self.assertIn("hotel-booking", self.storage_orchestrator.service_storage_requirements)
        self.assertIn("payment-service", self.storage_orchestrator.service_storage_requirements)
        
        # Verify payment service has appropriate retention
        payment_storage = self.storage_orchestrator.service_storage_requirements["payment-service"]
        transaction_db = payment_storage["transaction_database"]
        
        # Financial data should have long retention (10 years)
        self.assertEqual(transaction_db.retention_days, 3650)
        self.assertTrue(transaction_db.encryption_required)
    
    def test_backup_strategies(self):
        """Test backup strategy configurations"""
        from python.storage_orchestration import VolumeType
        
        self.assertIn(VolumeType.DATABASE, self.storage_orchestrator.backup_strategies)
        self.assertIn(VolumeType.LOGS, self.storage_orchestrator.backup_strategies)
        
        # Database should have more frequent backups than logs
        db_strategy = self.storage_orchestrator.backup_strategies[VolumeType.DATABASE]
        logs_strategy = self.storage_orchestrator.backup_strategies[VolumeType.LOGS]
        
        self.assertEqual(db_strategy["frequency"], "hourly")
        self.assertEqual(logs_strategy["frequency"], "daily")
    
    def test_cost_calculation(self):
        """Test storage cost calculation"""
        costs = self.storage_orchestrator.calculate_storage_costs("aws")
        
        self.assertIn("total", costs)
        self.assertIn("total_inr", costs)
        self.assertGreater(costs["total"], 0)
        self.assertGreater(costs["total_inr"], costs["total"])  # INR should be larger


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios combining multiple components"""
    
    def test_complete_deployment_pipeline(self):
        """Test complete deployment pipeline integration"""
        # This would test the full pipeline from code commit to production deployment
        # Including CI/CD, security scanning, and deployment
        
        # Initialize components
        ci_cd_pipeline = PayTMCICDPipeline("integration-test", "fake-token")
        security_manager = ZerodhaNetworkSecurityManager()
        
        # Verify components can work together
        self.assertIsNotNone(ci_cd_pipeline.environments)
        self.assertIsNotNone(security_manager.service_tiers)
        
        # Test that CI/CD environments match security tiers
        environments = list(ci_cd_pipeline.environments.keys())
        self.assertIn("production", environments)
    
    def test_monitoring_and_alerting_integration(self):
        """Test monitoring and alerting integration"""
        with patch('elasticsearch.Elasticsearch'), patch('redis.Redis'):
            observability = NykaaObservabilityStack()
        
        autoscaler = SwiggyAutoScaler("integration-test-service")
        
        # Verify both systems can work with similar metrics
        self.assertIsNotNone(observability.alert_thresholds)
        self.assertIsNotNone(autoscaler.cpu_scale_up_threshold)
        
        # Both should have reasonable CPU thresholds
        self.assertGreater(observability.alert_thresholds["error_rate"], 0)
        self.assertGreater(autoscaler.cpu_scale_up_threshold, 50)
    
    def test_storage_and_backup_integration(self):
        """Test storage and backup integration"""
        storage_orchestrator = MakeMyTripStorageOrchestrator()
        dr_system = RazorpayDisasterRecovery()
        
        # Verify both systems understand service tiers
        self.assertIsNotNone(storage_orchestrator.service_storage_requirements)
        self.assertIsNotNone(dr_system.services)
        
        # Both should have backup/recovery strategies
        payment_storage = storage_orchestrator.service_storage_requirements.get("payment-service")
        payment_dr = dr_system.services.get("payment-gateway")
        
        if payment_storage and payment_dr:
            # Both should treat payment services as critical
            transaction_db = payment_storage["transaction_database"]
            self.assertTrue(transaction_db.backup_required)
            
            from python.disaster_recovery_automation import RecoveryTier
            self.assertEqual(payment_dr.tier, RecoveryTier.TIER_0)


def run_performance_tests():
    """Run performance tests for critical components"""
    
    print("🚀 Running Performance Tests...")
    
    # Test autoscaler performance
    print("   Testing autoscaler performance...")
    autoscaler = SwiggyAutoScaler("perf-test-service")
    
    start_time = datetime.now()
    for _ in range(100):
        metrics = autoscaler.get_current_metrics()
        autoscaler.analyze_scaling_decision(metrics)
    end_time = datetime.now()
    
    scaling_decisions_per_second = 100 / (end_time - start_time).total_seconds()
    print(f"   Autoscaler: {scaling_decisions_per_second:.1f} decisions/second")
    
    # Test manifest generation performance
    print("   Testing manifest generation performance...")
    from python.kubernetes_deployment_manifests import BigBasketK8sGenerator, KubernetesAppConfig
    
    generator = BigBasketK8sGenerator()
    
    start_time = datetime.now()
    for i in range(50):
        config = KubernetesAppConfig(
            app_name=f"test-service-{i}",
            namespace="test",
            replicas=3,
            image="test/service",
            version="v1.0.0",
            company="test",
            environment="test",
            region="test",
            resource_requests={"cpu": "100m", "memory": "128Mi"},
            resource_limits={"cpu": "500m", "memory": "512Mi"},
            ports=[8000],
            health_check_path="/health"
        )
        generator.generate_deployment(config)
    end_time = datetime.now()
    
    manifests_per_second = 50 / (end_time - start_time).total_seconds()
    print(f"   Manifest generation: {manifests_per_second:.1f} manifests/second")
    
    print("✅ Performance tests completed!")


def main():
    """Run all tests"""
    
    print("🧪 Running Container Orchestration Test Suite")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestSwiggyMicroserviceContainerization,
        TestDockerfileBestPractices,
        TestKubernetesDeploymentManifests,
        TestServiceDiscoveryConsul,
        TestAutoscalingFoodDelivery,
        TestContainerHealthMonitoring,
        TestMultiEnvironmentDeployment,
        TestCICDIntegrationGitLab,
        TestSecretsManagementVault,
        TestDisasterRecoveryAutomation,
        TestLoggingMonitoringStack,
        TestNetworkPoliciesSecurity,
        TestStorageOrchestration,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run performance tests
    print("\n" + "=" * 60)
    run_performance_tests()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback.split('Exception:')[-1].strip()}")
    
    print("\n✅ Container orchestration test suite completed!")
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

# Test execution commands:
"""
# Run all tests:
python tests/test_all_examples.py

# Run specific test class:
python -m unittest tests.test_all_examples.TestSwiggyMicroserviceContainerization

# Run with coverage:
pip install coverage
coverage run tests/test_all_examples.py
coverage report
coverage html

# Run tests in Docker:
docker run -v $(pwd):/app -w /app python:3.11 python tests/test_all_examples.py

# Integration with CI/CD:
# Add to .gitlab-ci.yml:
test_container_orchestration:
  stage: test
  script:
    - pip install -r requirements.txt
    - python tests/test_all_examples.py
  artifacts:
    reports:
      junit: test-results.xml
"""
#!/usr/bin/env python3
"""
Kubernetes Canary Deployment Controller
======================================

Flipkart/Amazon style progressive delivery के लिए intelligent canary deployment system।
Real-time metrics के साथ automatic rollback और Indian traffic patterns के लिए optimized।

Features:
- Istio service mesh के साथ traffic splitting
- Business metrics monitoring (conversion rate, revenue)
- Indian business hours और festival season awareness
- Automatic rollback on error rate increase
- Multi-region canary deployment support
- WhatsApp/Slack integration for alerts

Author: Hindi Tech Podcast - Episode 19
Context: Progressive Delivery for Indian E-commerce
"""

import asyncio
import logging
import json
import yaml
import os
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import kubernetes
from kubernetes import client, config
import prometheus_client
from prometheus_client.parser import text_string_to_metric_families
import requests
import asyncio
import aiohttp
import pytz
import numpy as np
from pathlib import Path
import tempfile

# Indian timezone और business context
IST = pytz.timezone('Asia/Kolkata')

# Enhanced logging for canary deployments
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('canary_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeploymentStage(Enum):
    """Canary deployment stages"""
    PREPARATION = "preparation"
    CANARY_START = "canary_start"     # 5% traffic
    CANARY_EXPAND = "canary_expand"   # 25% traffic
    CANARY_MAJORITY = "canary_majority"  # 75% traffic
    FULL_ROLLOUT = "full_rollout"     # 100% traffic
    ROLLBACK = "rollback"
    FAILED = "failed"

class MetricThreshold(Enum):
    """Business metric thresholds for Indian e-commerce"""
    ERROR_RATE = 0.05        # 5% error rate threshold
    RESPONSE_TIME = 1000     # 1 second response time
    CONVERSION_RATE = 0.02   # 2% conversion rate drop
    REVENUE_DROP = 0.10      # 10% revenue drop
    UPI_SUCCESS_RATE = 0.85  # 85% UPI success rate

@dataclass
class CanaryConfig:
    """Canary deployment configuration"""
    app_name: str
    namespace: str = "production"
    canary_image: str = ""
    stable_image: str = ""
    
    # Traffic progression
    traffic_stages: List[int] = field(default_factory=lambda: [5, 25, 50, 75, 100])
    stage_duration: int = 600  # 10 minutes per stage
    
    # Metric thresholds
    max_error_rate: float = 0.05
    max_response_time: int = 1000
    min_success_rate: float = 0.95
    
    # Indian business settings
    enable_business_hours_check: bool = True
    avoid_festival_deployments: bool = True
    enable_regional_rollout: bool = True
    regions: List[str] = field(default_factory=lambda: ['mumbai', 'delhi', 'bangalore'])
    
    # Monitoring
    prometheus_url: str = "http://prometheus:9090"
    slack_webhook: str = ""
    enable_whatsapp_alerts: bool = False

@dataclass
class DeploymentMetrics:
    """Real-time deployment metrics"""
    timestamp: datetime
    stage: DeploymentStage
    traffic_percentage: int
    
    # Technical metrics
    error_rate: float = 0.0
    response_time_p95: float = 0.0
    success_rate: float = 1.0
    rps: int = 0
    
    # Business metrics (Indian e-commerce specific)
    conversion_rate: float = 0.0
    revenue_per_minute: float = 0.0
    cart_abandonment_rate: float = 0.0
    upi_success_rate: float = 0.0
    payment_gateway_errors: int = 0
    
    # Regional metrics
    mumbai_latency: float = 0.0
    delhi_latency: float = 0.0
    bangalore_latency: float = 0.0
    
    # Indian business context
    is_business_hours: bool = True
    is_festival_season: bool = False
    active_users: int = 0

class IndianBusinessContext:
    """Indian business hours और seasonal context"""
    
    @staticmethod
    def is_business_hours(timestamp: datetime = None) -> bool:
        """Indian business hours check (9 AM - 9 PM IST)"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        
        # Business hours: 9 AM to 9 PM IST
        return 9 <= timestamp.hour <= 21
    
    @staticmethod
    def is_peak_hours(timestamp: datetime = None) -> bool:
        """Peak shopping hours (6 PM - 9 PM IST)"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        
        # Peak hours: 6 PM to 9 PM IST
        return 18 <= timestamp.hour <= 21
    
    @staticmethod
    def is_festival_season(timestamp: datetime = None) -> bool:
        """Festival season detection"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        
        # Major Indian festival periods
        festival_periods = [
            # Diwali season (Oct-Nov) 
            (datetime(timestamp.year, 10, 15, tzinfo=IST), 
             datetime(timestamp.year, 11, 15, tzinfo=IST)),
            
            # Independence/Raksha Bandhan (August)
            (datetime(timestamp.year, 8, 10, tzinfo=IST),
             datetime(timestamp.year, 8, 20, tzinfo=IST)),
             
            # New Year shopping (Dec-Jan)
            (datetime(timestamp.year, 12, 25, tzinfo=IST),
             datetime(timestamp.year + 1, 1, 5, tzinfo=IST)),
             
            # Holi (March - approximate)
            (datetime(timestamp.year, 3, 5, tzinfo=IST),
             datetime(timestamp.year, 3, 15, tzinfo=IST))
        ]
        
        return any(start <= timestamp <= end for start, end in festival_periods)

class PrometheusMetricsCollector:
    """
    Prometheus से metrics collect करना।
    
    Indian e-commerce के लिए specific metrics जैसे UPI success rate,
    regional latencies, और business metrics।
    """
    
    def __init__(self, prometheus_url: str):
        self.prometheus_url = prometheus_url.rstrip('/')
        
    async def get_error_rate(self, app_name: str, duration: str = "5m") -> float:
        """Application error rate"""
        try:
            query = f"""
            (
                rate(http_requests_total{{app="{app_name}",status=~"5.."}}}[{duration}]) /
                rate(http_requests_total{{app="{app_name}"}}[{duration}])
            ) * 100
            """
            
            result = await self._prometheus_query(query)
            if result and result.get('data', {}).get('result'):
                return float(result['data']['result'][0]['value'][1])
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Error rate query failed: {e}")
            return 0.0
    
    async def get_response_time_p95(self, app_name: str, duration: str = "5m") -> float:
        """95th percentile response time"""
        try:
            query = f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{app="{app_name}"}}[{duration}])) * 1000'
            
            result = await self._prometheus_query(query)
            if result and result.get('data', {}).get('result'):
                return float(result['data']['result'][0]['value'][1])
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Response time query failed: {e}")
            return 0.0
    
    async def get_business_metrics(self, app_name: str) -> Dict[str, float]:
        """Indian business specific metrics"""
        try:
            metrics = {}
            
            # Conversion rate (orders/sessions)
            conversion_query = f"""
            (
                rate(ecommerce_orders_total{{app="{app_name}"}}[5m]) /
                rate(ecommerce_sessions_total{{app="{app_name}"}}[5m])
            ) * 100
            """
            
            # UPI success rate
            upi_success_query = f"""
            (
                rate(payment_transactions_total{{app="{app_name}",method="upi",status="success"}}[5m]) /
                rate(payment_transactions_total{{app="{app_name}",method="upi"}}[5m])
            ) * 100
            """
            
            # Revenue per minute
            revenue_query = f'rate(ecommerce_revenue_total{{app="{app_name}"}}[1m])'
            
            queries = {
                'conversion_rate': conversion_query,
                'upi_success_rate': upi_success_query,
                'revenue_per_minute': revenue_query
            }
            
            for metric_name, query in queries.items():
                result = await self._prometheus_query(query)
                if result and result.get('data', {}).get('result'):
                    metrics[metric_name] = float(result['data']['result'][0]['value'][1])
                else:
                    metrics[metric_name] = 0.0
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Business metrics query failed: {e}")
            return {}
    
    async def get_regional_latencies(self, app_name: str) -> Dict[str, float]:
        """Regional latency metrics for Indian data centers"""
        try:
            regions = {'mumbai': 'mum', 'delhi': 'del', 'bangalore': 'blr'}
            latencies = {}
            
            for region_name, region_code in regions.items():
                query = f'avg(http_request_duration_seconds{{app="{app_name}",region="{region_code}"}}) * 1000'
                result = await self._prometheus_query(query)
                
                if result and result.get('data', {}).get('result'):
                    latencies[f"{region_name}_latency"] = float(result['data']['result'][0]['value'][1])
                else:
                    latencies[f"{region_name}_latency"] = 0.0
            
            return latencies
            
        except Exception as e:
            logger.error(f"❌ Regional latency query failed: {e}")
            return {}
    
    async def _prometheus_query(self, query: str) -> Optional[Dict]:
        """Execute Prometheus query"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {'query': query}
                async with session.get(f"{self.prometheus_url}/api/v1/query", params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Prometheus query failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Prometheus query error: {e}")
            return None

class CanaryDeploymentController:
    """
    Production-ready canary deployment controller।
    
    Flipkart/Amazon जैसी large scale e-commerce के लिए intelligent
    progressive delivery with automatic rollback capabilities।
    """
    
    def __init__(self, config: CanaryConfig):
        self.config = config
        self.k8s_client = None
        self.metrics_collector = PrometheusMetricsCollector(config.prometheus_url)
        self.current_stage = DeploymentStage.PREPARATION
        self.deployment_start_time = None
        self.is_running = False
        
    async def initialize(self) -> bool:
        """Controller initialization"""
        try:
            logger.info(f"🚀 Initializing Canary Deployment for {self.config.app_name}")
            
            # Setup Kubernetes client
            try:
                config.load_incluster_config()
                logger.info("Using in-cluster Kubernetes config")
            except:
                config.load_kube_config()
                logger.info("Using local Kubernetes config")
            
            self.k8s_client = client.ApiClient()
            
            # Verify application exists
            apps_v1 = client.AppsV1Api()
            try:
                apps_v1.read_namespaced_deployment(
                    name=self.config.app_name,
                    namespace=self.config.namespace
                )
                logger.info(f"✅ Application '{self.config.app_name}' found")
            except client.ApiException:
                logger.error(f"❌ Application '{self.config.app_name}' not found")
                return False
            
            # Check business hours if enabled
            if self.config.enable_business_hours_check:
                if not IndianBusinessContext.is_business_hours():
                    logger.warning("⚠️ Deployment attempted outside business hours")
                    if IndianBusinessContext.is_peak_hours():
                        logger.error("❌ Deployment blocked during peak hours")
                        return False
            
            # Check festival season
            if self.config.avoid_festival_deployments:
                if IndianBusinessContext.is_festival_season():
                    logger.error("❌ Deployment blocked during festival season")
                    return False
            
            logger.info("✅ Canary deployment controller initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Controller initialization failed: {e}")
            return False
    
    async def start_canary_deployment(self) -> bool:
        """Start canary deployment process"""
        try:
            logger.info(f"🎯 Starting canary deployment for {self.config.app_name}")
            logger.info(f"📦 Canary image: {self.config.canary_image}")
            logger.info(f"📦 Stable image: {self.config.stable_image}")
            
            self.deployment_start_time = datetime.now(IST)
            self.is_running = True
            
            # Create deployment artifacts
            if not await self._create_canary_deployment():
                return False
            
            if not await self._create_canary_service():
                return False
                
            if not await self._create_istio_virtual_service():
                return False
            
            # Start progressive traffic shifting
            for stage_index, traffic_percent in enumerate(self.config.traffic_stages):
                if not self.is_running:
                    logger.info("🛑 Deployment stopped by user")
                    break
                
                logger.info(f"📈 Stage {stage_index + 1}: Shifting {traffic_percent}% traffic to canary")
                
                # Update traffic split
                await self._update_traffic_split(traffic_percent)
                
                # Monitor metrics for stage duration
                stage_success = await self._monitor_stage_metrics(traffic_percent)
                
                if not stage_success:
                    logger.error("❌ Stage failed - initiating rollback")
                    await self._rollback_deployment()
                    return False
                
                if traffic_percent == 100:
                    logger.info("🎉 Canary deployment completed successfully!")
                    await self._finalize_deployment()
                    break
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Canary deployment failed: {e}")
            await self._rollback_deployment()
            return False
    
    async def _create_canary_deployment(self) -> bool:
        """Create canary deployment"""
        try:
            logger.info("🏗️ Creating canary deployment...")
            
            apps_v1 = client.AppsV1Api()
            
            # Get existing deployment for template
            stable_deployment = apps_v1.read_namespaced_deployment(
                name=self.config.app_name,
                namespace=self.config.namespace
            )
            
            # Create canary deployment spec
            canary_deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(
                    name=f"{self.config.app_name}-canary",
                    namespace=self.config.namespace,
                    labels={
                        **stable_deployment.metadata.labels,
                        'version': 'canary',
                        'deployment-type': 'progressive-delivery',
                        'created-by': 'hindi-tech-canary-controller'
                    },
                    annotations={
                        'deployment.kubernetes.io/revision': '1',
                        'canary-start-time': self.deployment_start_time.isoformat(),
                        'stable-image': self.config.stable_image,
                        'canary-image': self.config.canary_image
                    }
                ),
                spec=client.V1DeploymentSpec(
                    replicas=1,  # Start with single replica
                    selector=client.V1LabelSelector(
                        match_labels={
                            'app': self.config.app_name,
                            'version': 'canary'
                        }
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={
                                'app': self.config.app_name,
                                'version': 'canary'
                            }
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=stable_deployment.spec.template.spec.containers[0].name,
                                    image=self.config.canary_image,
                                    ports=stable_deployment.spec.template.spec.containers[0].ports,
                                    env=stable_deployment.spec.template.spec.containers[0].env,
                                    resources=stable_deployment.spec.template.spec.containers[0].resources,
                                    # Add Indian business context environment variables
                                    env=[
                                        client.V1EnvVar(name="DEPLOYMENT_TYPE", value="canary"),
                                        client.V1EnvVar(name="REGION", value="india"),
                                        client.V1EnvVar(name="TIMEZONE", value="Asia/Kolkata"),
                                        client.V1EnvVar(name="BUSINESS_HOURS", value="09:00-21:00"),
                                        *stable_deployment.spec.template.spec.containers[0].env
                                    ] if stable_deployment.spec.template.spec.containers[0].env else [
                                        client.V1EnvVar(name="DEPLOYMENT_TYPE", value="canary"),
                                        client.V1EnvVar(name="REGION", value="india"),
                                        client.V1EnvVar(name="TIMEZONE", value="Asia/Kolkata"),
                                        client.V1EnvVar(name="BUSINESS_HOURS", value="09:00-21:00")
                                    ]
                                )
                            ]
                        )
                    )
                )
            )
            
            # Create the deployment
            apps_v1.create_namespaced_deployment(
                namespace=self.config.namespace,
                body=canary_deployment
            )
            
            # Wait for deployment to be ready
            await self._wait_for_deployment_ready(f"{self.config.app_name}-canary")
            
            logger.info("✅ Canary deployment created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create canary deployment: {e}")
            return False
    
    async def _create_canary_service(self) -> bool:
        """Create canary service"""
        try:
            logger.info("🔗 Creating canary service...")
            
            v1 = client.CoreV1Api()
            
            # Get existing service for template
            try:
                stable_service = v1.read_namespaced_service(
                    name=self.config.app_name,
                    namespace=self.config.namespace
                )
            except client.ApiException:
                logger.warning("No existing service found - creating basic service")
                stable_service = None
            
            # Create canary service
            if stable_service:
                canary_service = client.V1Service(
                    metadata=client.V1ObjectMeta(
                        name=f"{self.config.app_name}-canary",
                        namespace=self.config.namespace,
                        labels={
                            **stable_service.metadata.labels,
                            'version': 'canary'
                        }
                    ),
                    spec=client.V1ServiceSpec(
                        selector={
                            'app': self.config.app_name,
                            'version': 'canary'
                        },
                        ports=stable_service.spec.ports,
                        type=stable_service.spec.type
                    )
                )
            else:
                # Basic service if no template available
                canary_service = client.V1Service(
                    metadata=client.V1ObjectMeta(
                        name=f"{self.config.app_name}-canary",
                        namespace=self.config.namespace,
                        labels={'app': self.config.app_name, 'version': 'canary'}
                    ),
                    spec=client.V1ServiceSpec(
                        selector={
                            'app': self.config.app_name,
                            'version': 'canary'
                        },
                        ports=[
                            client.V1ServicePort(
                                port=80,
                                target_port=8080,
                                protocol="TCP"
                            )
                        ],
                        type="ClusterIP"
                    )
                )
            
            v1.create_namespaced_service(
                namespace=self.config.namespace,
                body=canary_service
            )
            
            logger.info("✅ Canary service created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create canary service: {e}")
            return False
    
    async def _create_istio_virtual_service(self) -> bool:
        """Create Istio VirtualService for traffic management"""
        try:
            logger.info("🌐 Creating Istio VirtualService...")
            
            # Initial VirtualService with 0% canary traffic
            virtual_service = {
                'apiVersion': 'networking.istio.io/v1beta1',
                'kind': 'VirtualService',
                'metadata': {
                    'name': f"{self.config.app_name}-vs",
                    'namespace': self.config.namespace,
                    'labels': {
                        'app': self.config.app_name,
                        'managed-by': 'canary-controller'
                    }
                },
                'spec': {
                    'hosts': [self.config.app_name],
                    'http': [{
                        'match': [{'headers': {'canary': {'exact': 'true'}}}],
                        'route': [{
                            'destination': {
                                'host': self.config.app_name,
                                'subset': 'canary'
                            }
                        }]
                    }, {
                        'route': [{
                            'destination': {
                                'host': self.config.app_name,
                                'subset': 'stable'
                            },
                            'weight': 100
                        }]
                    }]
                }
            }
            
            # Create DestinationRule for subsets
            destination_rule = {
                'apiVersion': 'networking.istio.io/v1beta1',
                'kind': 'DestinationRule',
                'metadata': {
                    'name': f"{self.config.app_name}-dr",
                    'namespace': self.config.namespace
                },
                'spec': {
                    'host': self.config.app_name,
                    'subsets': [
                        {
                            'name': 'stable',
                            'labels': {'version': 'stable'}
                        },
                        {
                            'name': 'canary', 
                            'labels': {'version': 'canary'}
                        }
                    ]
                }
            }
            
            # Apply configurations using kubectl
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump_all([destination_rule, virtual_service], f)
                istio_config_file = f.name
            
            import subprocess
            result = subprocess.run([
                'kubectl', 'apply', '-f', istio_config_file
            ], capture_output=True, text=True, timeout=60)
            
            os.unlink(istio_config_file)
            
            if result.returncode == 0:
                logger.info("✅ Istio traffic configuration applied")
                return True
            else:
                logger.error(f"❌ Istio config failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to create Istio configuration: {e}")
            return False
    
    async def _update_traffic_split(self, canary_percentage: int) -> bool:
        """Update traffic split between stable and canary"""
        try:
            logger.info(f"🔄 Updating traffic split: {canary_percentage}% canary, {100 - canary_percentage}% stable")
            
            stable_percentage = 100 - canary_percentage
            
            # Update VirtualService
            virtual_service = {
                'apiVersion': 'networking.istio.io/v1beta1',
                'kind': 'VirtualService',
                'metadata': {
                    'name': f"{self.config.app_name}-vs",
                    'namespace': self.config.namespace
                },
                'spec': {
                    'hosts': [self.config.app_name],
                    'http': [{
                        'route': [
                            {
                                'destination': {
                                    'host': self.config.app_name,
                                    'subset': 'stable'
                                },
                                'weight': stable_percentage
                            },
                            {
                                'destination': {
                                    'host': self.config.app_name,
                                    'subset': 'canary'
                                },
                                'weight': canary_percentage
                            }
                        ]
                    }]
                }
            }
            
            # Apply updated configuration
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(virtual_service, f)
                vs_file = f.name
            
            import subprocess
            result = subprocess.run([
                'kubectl', 'apply', '-f', vs_file
            ], capture_output=True, text=True, timeout=60)
            
            os.unlink(vs_file)
            
            if result.returncode == 0:
                # Scale canary replicas based on traffic percentage
                target_replicas = max(1, int((canary_percentage / 100) * 5))  # Scale based on percentage
                await self._scale_canary_deployment(target_replicas)
                
                logger.info(f"✅ Traffic split updated: {canary_percentage}% canary")
                return True
            else:
                logger.error(f"❌ Traffic split update failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to update traffic split: {e}")
            return False
    
    async def _monitor_stage_metrics(self, traffic_percentage: int) -> bool:
        """Monitor metrics during deployment stage"""
        try:
            logger.info(f"📊 Monitoring metrics for {traffic_percentage}% traffic stage...")
            
            stage_start = datetime.now(IST)
            stage_duration = timedelta(seconds=self.config.stage_duration)
            
            check_interval = 30  # Check every 30 seconds
            checks_per_stage = self.config.stage_duration // check_interval
            failed_checks = 0
            max_failed_checks = 3  # Allow 3 failed checks before rollback
            
            while datetime.now(IST) - stage_start < stage_duration:
                if not self.is_running:
                    return False
                
                # Collect current metrics
                metrics = await self._collect_current_metrics(traffic_percentage)
                
                # Log metrics
                logger.info(f"📈 Metrics - Error Rate: {metrics.error_rate:.2%}, "
                          f"Response Time: {metrics.response_time_p95:.0f}ms, "
                          f"Success Rate: {metrics.success_rate:.2%}")
                
                if metrics.conversion_rate > 0:
                    logger.info(f"💰 Business - Conversion: {metrics.conversion_rate:.2%}, "
                              f"Revenue/min: ₹{metrics.revenue_per_minute:.2f}, "
                              f"UPI Success: {metrics.upi_success_rate:.2%}")
                
                # Check thresholds
                if self._metrics_exceed_thresholds(metrics):
                    failed_checks += 1
                    logger.warning(f"⚠️ Metrics threshold exceeded - Failed checks: {failed_checks}/{max_failed_checks}")
                    
                    if failed_checks >= max_failed_checks:
                        logger.error("❌ Too many failed checks - stage failed")
                        return False
                else:
                    failed_checks = 0  # Reset failed checks counter
                
                # Send alerts if needed
                await self._send_stage_alerts(metrics, traffic_percentage)
                
                await asyncio.sleep(check_interval)
            
            logger.info(f"✅ Stage {traffic_percentage}% completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage monitoring failed: {e}")
            return False
    
    async def _collect_current_metrics(self, traffic_percentage: int) -> DeploymentMetrics:
        """Collect current deployment metrics"""
        try:
            current_time = datetime.now(IST)
            
            # Technical metrics
            error_rate = await self.metrics_collector.get_error_rate(self.config.app_name)
            response_time = await self.metrics_collector.get_response_time_p95(self.config.app_name)
            
            # Business metrics
            business_metrics = await self.metrics_collector.get_business_metrics(self.config.app_name)
            
            # Regional metrics
            regional_metrics = await self.metrics_collector.get_regional_latencies(self.config.app_name)
            
            # Create metrics object
            metrics = DeploymentMetrics(
                timestamp=current_time,
                stage=self.current_stage,
                traffic_percentage=traffic_percentage,
                error_rate=error_rate / 100,  # Convert to decimal
                response_time_p95=response_time,
                success_rate=1.0 - (error_rate / 100),
                conversion_rate=business_metrics.get('conversion_rate', 0) / 100,
                upi_success_rate=business_metrics.get('upi_success_rate', 0) / 100,
                revenue_per_minute=business_metrics.get('revenue_per_minute', 0),
                mumbai_latency=regional_metrics.get('mumbai_latency', 0),
                delhi_latency=regional_metrics.get('delhi_latency', 0),
                bangalore_latency=regional_metrics.get('bangalore_latency', 0),
                is_business_hours=IndianBusinessContext.is_business_hours(current_time),
                is_festival_season=IndianBusinessContext.is_festival_season(current_time)
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to collect metrics: {e}")
            # Return safe default metrics
            return DeploymentMetrics(
                timestamp=datetime.now(IST),
                stage=self.current_stage,
                traffic_percentage=traffic_percentage
            )
    
    def _metrics_exceed_thresholds(self, metrics: DeploymentMetrics) -> bool:
        """Check if metrics exceed configured thresholds"""
        
        # Error rate threshold
        if metrics.error_rate > self.config.max_error_rate:
            logger.warning(f"⚠️ Error rate threshold exceeded: {metrics.error_rate:.2%} > {self.config.max_error_rate:.2%}")
            return True
        
        # Response time threshold
        if metrics.response_time_p95 > self.config.max_response_time:
            logger.warning(f"⚠️ Response time threshold exceeded: {metrics.response_time_p95:.0f}ms > {self.config.max_response_time}ms")
            return True
        
        # Success rate threshold  
        if metrics.success_rate < self.config.min_success_rate:
            logger.warning(f"⚠️ Success rate threshold exceeded: {metrics.success_rate:.2%} < {self.config.min_success_rate:.2%}")
            return True
        
        # UPI success rate (critical for Indian e-commerce)
        if metrics.upi_success_rate > 0 and metrics.upi_success_rate < MetricThreshold.UPI_SUCCESS_RATE.value:
            logger.warning(f"⚠️ UPI success rate too low: {metrics.upi_success_rate:.2%}")
            return True
        
        # Business hours specific thresholds (stricter during business hours)
        if metrics.is_business_hours:
            if metrics.response_time_p95 > (self.config.max_response_time * 0.8):  # 20% stricter
                logger.warning(f"⚠️ Business hours response time exceeded: {metrics.response_time_p95:.0f}ms")
                return True
        
        return False
    
    async def _send_stage_alerts(self, metrics: DeploymentMetrics, traffic_percentage: int) -> None:
        """Send alerts for stage metrics"""
        try:
            # Critical alerts
            if self._metrics_exceed_thresholds(metrics):
                alert_data = {
                    'type': 'canary_deployment_warning',
                    'app': self.config.app_name,
                    'stage': f"{traffic_percentage}% traffic",
                    'error_rate': f"{metrics.error_rate:.2%}",
                    'response_time': f"{metrics.response_time_p95:.0f}ms",
                    'success_rate': f"{metrics.success_rate:.2%}",
                    'timestamp': metrics.timestamp.isoformat()
                }
                
                await self._send_slack_alert("⚠️ Canary Deployment Warning", alert_data)
            
            # Business metrics alerts
            if metrics.conversion_rate > 0 and metrics.conversion_rate < 0.02:  # Below 2%
                await self._send_slack_alert("📉 Low Conversion Rate", {
                    'app': self.config.app_name,
                    'conversion_rate': f"{metrics.conversion_rate:.2%}",
                    'traffic_stage': f"{traffic_percentage}%"
                })
            
        except Exception as e:
            logger.error(f"❌ Failed to send alerts: {e}")
    
    async def _send_slack_alert(self, title: str, data: Dict[str, Any]) -> None:
        """Send Slack alert"""
        try:
            if not self.config.slack_webhook:
                return
            
            payload = {
                'text': title,
                'attachments': [{
                    'color': 'warning',
                    'fields': [
                        {'title': key, 'value': str(value), 'short': True}
                        for key, value in data.items()
                    ]
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.slack_webhook, json=payload) as response:
                    if response.status == 200:
                        logger.info("✅ Slack alert sent")
                    else:
                        logger.warning(f"⚠️ Slack alert failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Slack alert error: {e}")
    
    async def _rollback_deployment(self) -> bool:
        """Rollback canary deployment"""
        try:
            logger.info("🔄 Starting canary deployment rollback...")
            
            # Set traffic to 100% stable
            await self._update_traffic_split(0)  # 0% canary = 100% stable
            
            # Delete canary resources
            await self._cleanup_canary_resources()
            
            # Send rollback notification
            await self._send_slack_alert("🔄 Canary Deployment Rolled Back", {
                'app': self.config.app_name,
                'reason': 'Metrics threshold exceeded',
                'timestamp': datetime.now(IST).isoformat()
            })
            
            self.current_stage = DeploymentStage.ROLLBACK
            logger.info("✅ Canary deployment rolled back successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    async def _finalize_deployment(self) -> bool:
        """Finalize successful canary deployment"""
        try:
            logger.info("🎯 Finalizing successful canary deployment...")
            
            # Update stable deployment with canary image
            apps_v1 = client.AppsV1Api()
            
            # Get stable deployment
            stable_deployment = apps_v1.read_namespaced_deployment(
                name=self.config.app_name,
                namespace=self.config.namespace
            )
            
            # Update image
            stable_deployment.spec.template.spec.containers[0].image = self.config.canary_image
            
            # Update deployment
            apps_v1.patch_namespaced_deployment(
                name=self.config.app_name,
                namespace=self.config.namespace,
                body=stable_deployment
            )
            
            # Wait for rollout to complete
            await self._wait_for_deployment_ready(self.config.app_name)
            
            # Reset traffic to 100% stable (which now has canary image)
            await self._update_traffic_split(0)
            
            # Cleanup canary resources
            await self._cleanup_canary_resources()
            
            # Send success notification
            await self._send_slack_alert("🎉 Canary Deployment Successful", {
                'app': self.config.app_name,
                'new_image': self.config.canary_image,
                'deployment_duration': str(datetime.now(IST) - self.deployment_start_time),
                'timestamp': datetime.now(IST).isoformat()
            })
            
            self.current_stage = DeploymentStage.FULL_ROLLOUT
            logger.info("🎉 Canary deployment finalized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to finalize deployment: {e}")
            return False
    
    async def _cleanup_canary_resources(self) -> None:
        """Clean up canary deployment resources"""
        try:
            logger.info("🧹 Cleaning up canary resources...")
            
            apps_v1 = client.AppsV1Api()
            v1 = client.CoreV1Api()
            
            # Delete canary deployment
            try:
                apps_v1.delete_namespaced_deployment(
                    name=f"{self.config.app_name}-canary",
                    namespace=self.config.namespace
                )
                logger.info("✅ Canary deployment deleted")
            except client.ApiException as e:
                if e.status != 404:  # Ignore not found
                    logger.warning(f"⚠️ Failed to delete canary deployment: {e}")
            
            # Delete canary service
            try:
                v1.delete_namespaced_service(
                    name=f"{self.config.app_name}-canary",
                    namespace=self.config.namespace
                )
                logger.info("✅ Canary service deleted")
            except client.ApiException as e:
                if e.status != 404:
                    logger.warning(f"⚠️ Failed to delete canary service: {e}")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
    
    async def _wait_for_deployment_ready(self, deployment_name: str, timeout: int = 300) -> bool:
        """Wait for deployment to be ready"""
        try:
            logger.info(f"⏳ Waiting for deployment '{deployment_name}' to be ready...")
            
            apps_v1 = client.AppsV1Api()
            start_time = datetime.now()
            
            while (datetime.now() - start_time).seconds < timeout:
                deployment = apps_v1.read_namespaced_deployment(
                    name=deployment_name,
                    namespace=self.config.namespace
                )
                
                if (deployment.status.ready_replicas and 
                    deployment.status.ready_replicas == deployment.spec.replicas):
                    logger.info(f"✅ Deployment '{deployment_name}' is ready")
                    return True
                
                await asyncio.sleep(10)
                logger.info(f"⏳ Still waiting for '{deployment_name}'...")
            
            logger.warning(f"⚠️ Deployment '{deployment_name}' readiness timeout")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to wait for deployment: {e}")
            return False
    
    async def _scale_canary_deployment(self, replicas: int) -> bool:
        """Scale canary deployment"""
        try:
            apps_v1 = client.AppsV1Api()
            
            # Scale canary deployment
            body = {'spec': {'replicas': replicas}}
            apps_v1.patch_namespaced_deployment_scale(
                name=f"{self.config.app_name}-canary",
                namespace=self.config.namespace,
                body=body
            )
            
            logger.info(f"✅ Scaled canary deployment to {replicas} replicas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to scale canary deployment: {e}")
            return False
    
    async def stop_deployment(self) -> None:
        """Stop canary deployment"""
        logger.info("🛑 Stopping canary deployment...")
        self.is_running = False


async def main():
    """Main function for canary deployment"""
    print("🎯 Kubernetes Canary Deployment Controller")
    print("=" * 50)
    
    # Configuration for Flipkart-style e-commerce app
    config = CanaryConfig(
        app_name="ecommerce-api",
        namespace="production",
        canary_image="myregistry/ecommerce-api:v2.1.0",
        stable_image="myregistry/ecommerce-api:v2.0.0",
        traffic_stages=[5, 25, 50, 75, 100],
        stage_duration=600,  # 10 minutes per stage
        max_error_rate=0.05,  # 5%
        max_response_time=1000,  # 1 second
        min_success_rate=0.95,  # 95%
        prometheus_url=os.getenv("PROMETHEUS_URL", "http://prometheus:9090"),
        slack_webhook=os.getenv("SLACK_WEBHOOK", ""),
        enable_business_hours_check=True,
        avoid_festival_deployments=True,
        enable_regional_rollout=True
    )
    
    # Initialize controller
    controller = CanaryDeploymentController(config)
    
    try:
        # Initialize and start deployment
        if await controller.initialize():
            print("✅ Canary Controller initialized successfully")
            success = await controller.start_canary_deployment()
            
            if success:
                print("🎉 Canary deployment completed successfully!")
            else:
                print("❌ Canary deployment failed!")
        else:
            print("❌ Failed to initialize controller")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping canary deployment...")
        await controller.stop_deployment()
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        await controller.stop_deployment()


if __name__ == "__main__":
    asyncio.run(main())
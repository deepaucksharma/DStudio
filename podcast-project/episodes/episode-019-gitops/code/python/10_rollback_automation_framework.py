#!/usr/bin/env python3
"""
GitOps Rollback Automation Framework
====================================

Intelligent automatic rollback system for GitOps deployments।
Business metrics monitoring के साथ automated rollback decisions for Indian e-commerce।

Features:
- Multi-metric rollback triggers (error rate, latency, conversion)
- Indian business hours और festival season awareness
- Progressive rollback with traffic shifting
- Business impact assessment और automated decisions
- Manual override और approval workflows
- Complete audit trails for compliance

Author: Hindi Tech Podcast - Episode 19
Context: Automated Rollback for Indian E-commerce
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
import aiohttp
import asyncpg
import pytz
from pathlib import Path
import statistics
import numpy as np

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

# Enhanced logging for rollback operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('rollback_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RollbackTrigger(Enum):
    """Types of rollback triggers"""
    ERROR_RATE = "error_rate"
    LATENCY_SPIKE = "latency_spike"
    CONVERSION_DROP = "conversion_drop"
    REVENUE_DROP = "revenue_drop"
    UPI_FAILURE = "upi_failure"
    CIRCUIT_BREAKER = "circuit_breaker"
    MANUAL = "manual"

class RollbackStatus(Enum):
    """Rollback operation status"""
    EVALUATING = "evaluating"
    TRIGGERED = "triggered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    MANUAL_INTERVENTION_REQUIRED = "manual_intervention_required"

class BusinessImpactLevel(Enum):
    """Business impact assessment levels"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class MetricThreshold:
    """Metric threshold configuration"""
    metric_name: str
    threshold_value: float
    comparison: str  # '>', '<', '=='
    duration_minutes: int = 5
    
    # Business context adjustments
    business_hours_multiplier: float = 1.0
    peak_hours_multiplier: float = 1.2  # Stricter during peak
    festival_season_multiplier: float = 0.8  # Much stricter during festivals
    
    # Regional variations
    mumbai_multiplier: float = 1.0
    delhi_multiplier: float = 1.1
    bangalore_multiplier: float = 1.2

@dataclass
class DeploymentSnapshot:
    """Snapshot of deployment state"""
    deployment_id: str
    application: str
    namespace: str
    image_tag: str
    replicas: int
    
    # Previous state (for rollback)
    previous_image_tag: str
    previous_replicas: int
    previous_config: Dict[str, Any] = field(default_factory=dict)
    
    # Deployment info
    deployed_at: datetime = field(default_factory=lambda: datetime.now(IST))
    deployed_by: str = ""
    deployment_method: str = "gitops"
    
    # Traffic management
    traffic_percentage: float = 100.0
    canary_enabled: bool = False

@dataclass
class BusinessMetrics:
    """Current business metrics snapshot"""
    timestamp: datetime
    
    # Technical metrics
    error_rate: float = 0.0  # %
    response_time_p95: float = 0.0  # ms
    throughput_rps: float = 0.0
    availability: float = 100.0  # %
    
    # Business metrics for Indian e-commerce
    conversion_rate: float = 0.0  # %
    revenue_per_minute: float = 0.0  # INR
    cart_abandonment_rate: float = 0.0  # %
    upi_success_rate: float = 0.0  # %
    payment_failure_rate: float = 0.0  # %
    
    # Regional metrics
    mumbai_latency: float = 0.0
    delhi_latency: float = 0.0
    bangalore_latency: float = 0.0
    
    # User experience
    active_users: int = 0
    bounce_rate: float = 0.0  # %
    page_load_time: float = 0.0  # ms

@dataclass
class RollbackEvent:
    """Rollback event tracking"""
    event_id: str
    deployment_id: str
    trigger: RollbackTrigger
    status: RollbackStatus
    
    # Metrics that triggered rollback
    triggering_metrics: BusinessMetrics = None
    threshold_breached: str = ""
    
    # Decision info
    business_impact: BusinessImpactLevel = BusinessImpactLevel.MEDIUM
    auto_rollback_enabled: bool = True
    requires_approval: bool = False
    
    # Execution
    started_at: datetime = field(default_factory=lambda: datetime.now(IST))
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Results
    success: bool = False
    error_message: Optional[str] = None
    rollback_steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Approval workflow
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_notes: str = ""

@dataclass
class RollbackConfig:
    """Rollback automation configuration"""
    # Monitoring
    prometheus_url: str = "http://prometheus:9090"
    metrics_check_interval: int = 30  # seconds
    
    # Database
    postgres_url: str = "postgresql://user:pass@postgres:5432/rollback"
    
    # Kubernetes
    namespace_patterns: List[str] = field(default_factory=lambda: ['production', 'prod'])
    
    # Thresholds
    error_rate_threshold: float = 5.0  # %
    latency_threshold_ms: int = 2000
    conversion_drop_threshold: float = 20.0  # %
    revenue_drop_threshold: float = 15.0  # %
    upi_failure_threshold: float = 10.0  # %
    
    # Business rules
    enable_business_hours_protection: bool = True
    enable_festival_season_protection: bool = True
    enable_auto_rollback: bool = True
    max_auto_rollbacks_per_day: int = 3
    
    # Approval requirements
    require_approval_for_critical_impact: bool = True
    require_approval_during_business_hours: bool = False
    
    # Notifications
    slack_webhook: str = ""
    teams_webhook: str = ""
    oncall_phone: str = "+91-9999999999"
    
    # Regional settings
    primary_region: str = "mumbai"
    secondary_regions: List[str] = field(default_factory=lambda: ["delhi", "bangalore"])

class IndianBusinessContext:
    """Indian business context for rollback decisions"""
    
    @staticmethod
    def is_business_hours(timestamp: datetime = None) -> bool:
        """Check if current time is business hours"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        return 9 <= timestamp.hour <= 21
    
    @staticmethod
    def is_peak_hours(timestamp: datetime = None) -> bool:
        """Check if current time is peak business hours"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        return 18 <= timestamp.hour <= 22  # Peak shopping hours
    
    @staticmethod
    def is_festival_season(timestamp: datetime = None) -> bool:
        """Check if current time is during festival season"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        
        festival_periods = [
            # Diwali season - highest sales
            (datetime(timestamp.year, 10, 15, tzinfo=IST), 
             datetime(timestamp.year, 11, 15, tzinfo=IST)),
             
            # Independence Day sales
            (datetime(timestamp.year, 8, 10, tzinfo=IST),
             datetime(timestamp.year, 8, 20, tzinfo=IST)),
             
            # New Year shopping
            (datetime(timestamp.year, 12, 25, tzinfo=IST),
             datetime(timestamp.year + 1, 1, 5, tzinfo=IST))
        ]
        
        return any(start <= timestamp <= end for start, end in festival_periods)
    
    @staticmethod
    def get_business_multiplier(timestamp: datetime = None) -> float:
        """Get business impact multiplier based on time"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        
        multiplier = 1.0
        
        # Festival season - much higher impact
        if IndianBusinessContext.is_festival_season(timestamp):
            multiplier *= 3.0
        
        # Peak hours - higher impact
        elif IndianBusinessContext.is_peak_hours(timestamp):
            multiplier *= 2.0
        
        # Business hours - moderate impact
        elif IndianBusinessContext.is_business_hours(timestamp):
            multiplier *= 1.5
        
        return multiplier

class MetricsCollector:
    """
    Business metrics collector।
    
    Prometheus और other sources से Indian business metrics collect करके
    rollback decisions के लिए comprehensive data provide करता है।
    """
    
    def __init__(self, prometheus_url: str):
        self.prometheus_url = prometheus_url.rstrip('/')
        
    async def collect_current_metrics(self) -> BusinessMetrics:
        """Collect current business metrics"""
        try:
            current_time = datetime.now(IST)
            metrics = BusinessMetrics(timestamp=current_time)
            
            # Technical metrics
            metrics.error_rate = await self._get_error_rate()
            metrics.response_time_p95 = await self._get_response_time_p95()
            metrics.throughput_rps = await self._get_throughput()
            metrics.availability = await self._get_availability()
            
            # Business metrics
            metrics.conversion_rate = await self._get_conversion_rate()
            metrics.revenue_per_minute = await self._get_revenue_per_minute()
            metrics.cart_abandonment_rate = await self._get_cart_abandonment_rate()
            metrics.upi_success_rate = await self._get_upi_success_rate()
            metrics.payment_failure_rate = await self._get_payment_failure_rate()
            
            # Regional metrics
            regional_latencies = await self._get_regional_latencies()
            metrics.mumbai_latency = regional_latencies.get('mumbai', 0)
            metrics.delhi_latency = regional_latencies.get('delhi', 0)
            metrics.bangalore_latency = regional_latencies.get('bangalore', 0)
            
            # User experience
            metrics.active_users = await self._get_active_users()
            metrics.bounce_rate = await self._get_bounce_rate()
            metrics.page_load_time = await self._get_page_load_time()
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to collect metrics: {e}")
            return BusinessMetrics(timestamp=datetime.now(IST))
    
    async def _prometheus_query(self, query: str) -> Optional[float]:
        """Execute Prometheus query and return single value"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {'query': query}
                async with session.get(f"{self.prometheus_url}/api/v1/query", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get('data', {}).get('result', [])
                        if result:
                            return float(result[0]['value'][1])
            return 0.0
        except Exception as e:
            logger.error(f"❌ Prometheus query failed: {e}")
            return 0.0
    
    async def _get_error_rate(self) -> float:
        """Get current error rate"""
        query = 'rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100'
        return await self._prometheus_query(query)
    
    async def _get_response_time_p95(self) -> float:
        """Get 95th percentile response time"""
        query = 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) * 1000'
        return await self._prometheus_query(query)
    
    async def _get_throughput(self) -> float:
        """Get requests per second"""
        query = 'rate(http_requests_total[5m])'
        return await self._prometheus_query(query)
    
    async def _get_availability(self) -> float:
        """Get service availability"""
        query = 'avg(up) * 100'
        return await self._prometheus_query(query)
    
    async def _get_conversion_rate(self) -> float:
        """Get e-commerce conversion rate"""
        query = 'rate(ecommerce_orders_total[5m]) / rate(ecommerce_sessions_total[5m]) * 100'
        return await self._prometheus_query(query)
    
    async def _get_revenue_per_minute(self) -> float:
        """Get revenue per minute in INR"""
        query = 'rate(ecommerce_revenue_total[1m])'
        return await self._prometheus_query(query)
    
    async def _get_cart_abandonment_rate(self) -> float:
        """Get cart abandonment rate"""
        query = '(rate(ecommerce_cart_created_total[5m]) - rate(ecommerce_orders_total[5m])) / rate(ecommerce_cart_created_total[5m]) * 100'
        return await self._prometheus_query(query)
    
    async def _get_upi_success_rate(self) -> float:
        """Get UPI payment success rate"""
        query = 'rate(payment_transactions_total{method="upi",status="success"}[5m]) / rate(payment_transactions_total{method="upi"}[5m]) * 100'
        return await self._prometheus_query(query)
    
    async def _get_payment_failure_rate(self) -> float:
        """Get overall payment failure rate"""
        query = 'rate(payment_transactions_total{status="failed"}[5m]) / rate(payment_transactions_total[5m]) * 100'
        return await self._prometheus_query(query)
    
    async def _get_regional_latencies(self) -> Dict[str, float]:
        """Get regional latency metrics"""
        regions = ['mumbai', 'delhi', 'bangalore']
        latencies = {}
        
        for region in regions:
            query = f'avg(http_request_duration_seconds{{region="{region}"}}) * 1000'
            latencies[region] = await self._prometheus_query(query)
        
        return latencies
    
    async def _get_active_users(self) -> int:
        """Get current active users"""
        query = 'sum(active_users_current)'
        result = await self._prometheus_query(query)
        return int(result) if result else 0
    
    async def _get_bounce_rate(self) -> float:
        """Get bounce rate"""
        query = 'rate(web_bounces_total[5m]) / rate(web_sessions_total[5m]) * 100'
        return await self._prometheus_query(query)
    
    async def _get_page_load_time(self) -> float:
        """Get average page load time"""
        query = 'avg(web_page_load_time_seconds) * 1000'
        return await self._prometheus_query(query)

class RollbackDecisionEngine:
    """
    Intelligent rollback decision engine।
    
    Business metrics, Indian market context, और risk assessment के साथ
    automatic rollback decisions लेता है।
    """
    
    def __init__(self, config: RollbackConfig):
        self.config = config
        self.metrics_collector = MetricsCollector(config.prometheus_url)
        self.baseline_metrics = {}  # Store baseline metrics for comparison
        
    async def should_trigger_rollback(self, current_metrics: BusinessMetrics,
                                    deployment: DeploymentSnapshot) -> Tuple[bool, RollbackTrigger, str]:
        """Evaluate if rollback should be triggered"""
        try:
            current_time = current_metrics.timestamp
            business_multiplier = IndianBusinessContext.get_business_multiplier(current_time)
            
            # Check error rate
            error_threshold = self.config.error_rate_threshold
            if IndianBusinessContext.is_festival_season(current_time):
                error_threshold *= 0.5  # Much stricter during festivals
            
            if current_metrics.error_rate > error_threshold:
                return True, RollbackTrigger.ERROR_RATE, f"Error rate {current_metrics.error_rate:.2f}% > {error_threshold:.2f}%"
            
            # Check latency
            latency_threshold = self.config.latency_threshold_ms
            if IndianBusinessContext.is_peak_hours(current_time):
                latency_threshold *= 0.8  # Stricter during peak hours
            
            if current_metrics.response_time_p95 > latency_threshold:
                return True, RollbackTrigger.LATENCY_SPIKE, f"P95 latency {current_metrics.response_time_p95:.0f}ms > {latency_threshold}ms"
            
            # Check business metrics (if we have baseline)
            baseline = self.baseline_metrics.get(deployment.application)
            if baseline:
                # Conversion rate drop
                if baseline.conversion_rate > 0:
                    conversion_drop = ((baseline.conversion_rate - current_metrics.conversion_rate) / baseline.conversion_rate) * 100
                    conversion_threshold = self.config.conversion_drop_threshold * business_multiplier
                    
                    if conversion_drop > conversion_threshold:
                        return True, RollbackTrigger.CONVERSION_DROP, f"Conversion drop {conversion_drop:.1f}% > {conversion_threshold:.1f}%"
                
                # Revenue drop
                if baseline.revenue_per_minute > 0:
                    revenue_drop = ((baseline.revenue_per_minute - current_metrics.revenue_per_minute) / baseline.revenue_per_minute) * 100
                    revenue_threshold = self.config.revenue_drop_threshold * business_multiplier
                    
                    if revenue_drop > revenue_threshold:
                        return True, RollbackTrigger.REVENUE_DROP, f"Revenue drop {revenue_drop:.1f}% > {revenue_threshold:.1f}%"
            
            # Check UPI failures (critical for Indian market)
            upi_failure_threshold = self.config.upi_failure_threshold
            if IndianBusinessContext.is_festival_season(current_time):
                upi_failure_threshold *= 0.5  # Much stricter during festivals
            
            if current_metrics.payment_failure_rate > upi_failure_threshold:
                return True, RollbackTrigger.UPI_FAILURE, f"UPI failure rate {current_metrics.payment_failure_rate:.2f}% > {upi_failure_threshold:.2f}%"
            
            return False, None, ""
            
        except Exception as e:
            logger.error(f"❌ Rollback evaluation failed: {e}")
            return False, None, f"Evaluation error: {str(e)}"
    
    def assess_business_impact(self, metrics: BusinessMetrics, trigger: RollbackTrigger) -> BusinessImpactLevel:
        """Assess business impact of the issue"""
        try:
            current_time = metrics.timestamp
            
            # Base impact by trigger type
            base_impact = {
                RollbackTrigger.ERROR_RATE: BusinessImpactLevel.HIGH,
                RollbackTrigger.LATENCY_SPIKE: BusinessImpactLevel.MEDIUM,
                RollbackTrigger.CONVERSION_DROP: BusinessImpactLevel.CRITICAL,
                RollbackTrigger.REVENUE_DROP: BusinessImpactLevel.CRITICAL,
                RollbackTrigger.UPI_FAILURE: BusinessImpactLevel.CRITICAL,
                RollbackTrigger.CIRCUIT_BREAKER: BusinessImpactLevel.HIGH,
                RollbackTrigger.MANUAL: BusinessImpactLevel.MEDIUM
            }.get(trigger, BusinessImpactLevel.MEDIUM)
            
            # Adjust based on business context
            if IndianBusinessContext.is_festival_season(current_time):
                # Everything is critical during festival season
                if base_impact in [BusinessImpactLevel.MEDIUM, BusinessImpactLevel.HIGH]:
                    return BusinessImpactLevel.CRITICAL
            
            elif IndianBusinessContext.is_peak_hours(current_time):
                # Escalate during peak hours
                if base_impact == BusinessImpactLevel.MEDIUM:
                    return BusinessImpactLevel.HIGH
                elif base_impact == BusinessImpactLevel.HIGH:
                    return BusinessImpactLevel.CRITICAL
            
            # Consider user impact
            if metrics.active_users > 100000:  # High traffic
                if base_impact == BusinessImpactLevel.MEDIUM:
                    return BusinessImpactLevel.HIGH
            
            return base_impact
            
        except Exception as e:
            logger.error(f"❌ Business impact assessment failed: {e}")
            return BusinessImpactLevel.MEDIUM
    
    def should_require_approval(self, impact: BusinessImpactLevel, 
                              metrics: BusinessMetrics) -> bool:
        """Determine if manual approval is required"""
        
        # Always require approval for critical impact
        if (self.config.require_approval_for_critical_impact and 
            impact == BusinessImpactLevel.CRITICAL):
            return True
        
        # Require approval during business hours if configured
        if (self.config.require_approval_during_business_hours and
            IndianBusinessContext.is_business_hours(metrics.timestamp)):
            return True
        
        # Require approval during festival season for safety
        if IndianBusinessContext.is_festival_season(metrics.timestamp):
            return True
        
        return False

class RollbackExecutor:
    """
    Rollback execution engine।
    
    Progressive rollback के साथ safe deployment state restore करता है।
    """
    
    def __init__(self, config: RollbackConfig):
        self.config = config
        self.k8s_client = None
        
    async def initialize(self) -> bool:
        """Initialize rollback executor"""
        try:
            # Setup Kubernetes client
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            
            self.k8s_client = client.ApiClient()
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback executor initialization failed: {e}")
            return False
    
    async def execute_rollback(self, event: RollbackEvent, 
                             deployment: DeploymentSnapshot) -> bool:
        """Execute rollback operation"""
        try:
            logger.info(f"🔄 Starting rollback execution: {event.event_id}")
            
            event.status = RollbackStatus.IN_PROGRESS
            rollback_steps = []
            
            # Step 1: Reduce traffic to new version (if canary)
            if deployment.canary_enabled and deployment.traffic_percentage > 0:
                step_result = await self._reduce_canary_traffic(deployment)
                rollback_steps.append({
                    'step': 'reduce_canary_traffic',
                    'success': step_result,
                    'timestamp': datetime.now(IST).isoformat()
                })
                
                if not step_result:
                    event.error_message = "Failed to reduce canary traffic"
                    return False
            
            # Step 2: Update deployment to previous version
            step_result = await self._rollback_deployment(deployment)
            rollback_steps.append({
                'step': 'rollback_deployment',
                'success': step_result,
                'timestamp': datetime.now(IST).isoformat(),
                'details': {
                    'from_image': deployment.image_tag,
                    'to_image': deployment.previous_image_tag,
                    'from_replicas': deployment.replicas,
                    'to_replicas': deployment.previous_replicas
                }
            })
            
            if not step_result:
                event.error_message = "Failed to rollback deployment"
                return False
            
            # Step 3: Wait for rollout completion
            step_result = await self._wait_for_rollout_completion(deployment)
            rollback_steps.append({
                'step': 'wait_for_rollout',
                'success': step_result,
                'timestamp': datetime.now(IST).isoformat()
            })
            
            if not step_result:
                event.error_message = "Rollout completion timeout"
                return False
            
            # Step 4: Verify health after rollback
            step_result = await self._verify_post_rollback_health(deployment)
            rollback_steps.append({
                'step': 'verify_health',
                'success': step_result,
                'timestamp': datetime.now(IST).isoformat()
            })
            
            if not step_result:
                event.error_message = "Post-rollback health check failed"
                return False
            
            # Step 5: Update DNS/Load balancer if needed
            step_result = await self._update_traffic_routing(deployment)
            rollback_steps.append({
                'step': 'update_traffic_routing',
                'success': step_result,
                'timestamp': datetime.now(IST).isoformat()
            })
            
            event.rollback_steps = rollback_steps
            event.success = True
            event.status = RollbackStatus.COMPLETED
            event.completed_at = datetime.now(IST)
            event.duration_seconds = (event.completed_at - event.started_at).total_seconds()
            
            logger.info(f"✅ Rollback completed successfully: {event.event_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback execution failed: {e}")
            event.success = False
            event.status = RollbackStatus.FAILED
            event.error_message = str(e)
            event.completed_at = datetime.now(IST)
            event.duration_seconds = (event.completed_at - event.started_at).total_seconds()
            return False
    
    async def _reduce_canary_traffic(self, deployment: DeploymentSnapshot) -> bool:
        """Reduce traffic to canary version"""
        try:
            logger.info(f"📉 Reducing canary traffic for {deployment.application}")
            
            # Update Istio VirtualService to reduce traffic
            # This is a simplified implementation
            
            # In real implementation, update VirtualService
            await asyncio.sleep(2)  # Simulate traffic update
            
            deployment.traffic_percentage = 0.0
            logger.info(f"✅ Canary traffic reduced to 0%")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to reduce canary traffic: {e}")
            return False
    
    async def _rollback_deployment(self, deployment: DeploymentSnapshot) -> bool:
        """Rollback Kubernetes deployment to previous version"""
        try:
            logger.info(f"🔄 Rolling back deployment {deployment.application}")
            
            apps_v1 = client.AppsV1Api()
            
            # Get current deployment
            current_deployment = apps_v1.read_namespaced_deployment(
                name=deployment.application,
                namespace=deployment.namespace
            )
            
            # Update to previous image
            current_deployment.spec.template.spec.containers[0].image = deployment.previous_image_tag
            current_deployment.spec.replicas = deployment.previous_replicas
            
            # Add rollback annotations
            if not current_deployment.metadata.annotations:
                current_deployment.metadata.annotations = {}
            
            current_deployment.metadata.annotations.update({
                'rollback.gitops/trigger-time': datetime.now(IST).isoformat(),
                'rollback.gitops/from-image': deployment.image_tag,
                'rollback.gitops/to-image': deployment.previous_image_tag,
                'rollback.gitops/automated': 'true'
            })
            
            # Apply the rollback
            apps_v1.patch_namespaced_deployment(
                name=deployment.application,
                namespace=deployment.namespace,
                body=current_deployment
            )
            
            logger.info(f"✅ Deployment rolled back: {deployment.application}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment rollback failed: {e}")
            return False
    
    async def _wait_for_rollout_completion(self, deployment: DeploymentSnapshot, 
                                         timeout: int = 300) -> bool:
        """Wait for deployment rollout to complete"""
        try:
            logger.info(f"⏳ Waiting for rollout completion: {deployment.application}")
            
            apps_v1 = client.AppsV1Api()
            start_time = datetime.now()
            
            while (datetime.now() - start_time).seconds < timeout:
                current_deployment = apps_v1.read_namespaced_deployment(
                    name=deployment.application,
                    namespace=deployment.namespace
                )
                
                # Check if rollout is complete
                if (current_deployment.status.ready_replicas and
                    current_deployment.status.ready_replicas == current_deployment.spec.replicas and
                    current_deployment.status.updated_replicas == current_deployment.spec.replicas):
                    
                    logger.info(f"✅ Rollout completed: {deployment.application}")
                    return True
                
                await asyncio.sleep(10)
                logger.info(f"⏳ Still waiting for rollout: {deployment.application}")
            
            logger.warning(f"⏰ Rollout timeout: {deployment.application}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Rollout wait failed: {e}")
            return False
    
    async def _verify_post_rollback_health(self, deployment: DeploymentSnapshot) -> bool:
        """Verify application health after rollback"""
        try:
            logger.info(f"🏥 Verifying health after rollback: {deployment.application}")
            
            # Check pod readiness
            v1 = client.CoreV1Api()
            pods = v1.list_namespaced_pod(
                namespace=deployment.namespace,
                label_selector=f"app={deployment.application}"
            )
            
            ready_pods = 0
            for pod in pods.items:
                if pod.status.phase == "Running":
                    ready_conditions = [condition for condition in pod.status.conditions 
                                      if condition.type == "Ready" and condition.status == "True"]
                    if ready_conditions:
                        ready_pods += 1
            
            if ready_pods < deployment.previous_replicas:
                logger.warning(f"Not all pods ready: {ready_pods}/{deployment.previous_replicas}")
                return False
            
            # Wait a bit and check basic metrics
            await asyncio.sleep(30)  # Let metrics stabilize
            
            # Basic health check would go here
            # In real implementation, check error rates, response times etc.
            
            logger.info(f"✅ Health verification passed: {deployment.application}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Health verification failed: {e}")
            return False
    
    async def _update_traffic_routing(self, deployment: DeploymentSnapshot) -> bool:
        """Update traffic routing after rollback"""
        try:
            logger.info(f"🌐 Updating traffic routing: {deployment.application}")
            
            # Update load balancer configurations
            # Update DNS entries if needed
            # Update service mesh routing
            
            # Simplified implementation
            await asyncio.sleep(2)
            
            logger.info(f"✅ Traffic routing updated: {deployment.application}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Traffic routing update failed: {e}")
            return False

class RollbackAutomationFramework:
    """
    Complete rollback automation framework।
    
    Monitoring, decision making, execution, और reporting के साथ end-to-end
    automated rollback system for Indian e-commerce deployments।
    """
    
    def __init__(self, config: RollbackConfig):
        self.config = config
        self.metrics_collector = MetricsCollector(config.prometheus_url)
        self.decision_engine = RollbackDecisionEngine(config)
        self.rollback_executor = RollbackExecutor(config)
        self.pg_pool = None
        self.active_deployments = {}  # Track active deployments
        self.is_running = False
        
    async def initialize(self) -> bool:
        """Initialize rollback automation framework"""
        try:
            logger.info("🚀 Initializing Rollback Automation Framework")
            
            # Initialize components
            if not await self.rollback_executor.initialize():
                return False
            
            # Setup database connection
            self.pg_pool = await asyncpg.create_pool(
                self.config.postgres_url,
                min_size=5,
                max_size=20
            )
            
            # Initialize database schema
            await self._initialize_database()
            
            logger.info("✅ Rollback Automation Framework initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback framework initialization failed: {e}")
            return False
    
    async def _initialize_database(self) -> None:
        """Initialize rollback tracking database"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS deployments (
            id SERIAL PRIMARY KEY,
            deployment_id VARCHAR(255) UNIQUE NOT NULL,
            application VARCHAR(255) NOT NULL,
            namespace VARCHAR(255) NOT NULL,
            image_tag VARCHAR(255) NOT NULL,
            previous_image_tag VARCHAR(255),
            replicas INTEGER DEFAULT 1,
            previous_replicas INTEGER DEFAULT 1,
            deployed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            deployed_by VARCHAR(255),
            deployment_data JSONB DEFAULT '{}'::jsonb,
            
            INDEX idx_deployment_app (application),
            INDEX idx_deployment_deployed (deployed_at)
        );
        
        CREATE TABLE IF NOT EXISTS rollback_events (
            id SERIAL PRIMARY KEY,
            event_id VARCHAR(255) UNIQUE NOT NULL,
            deployment_id VARCHAR(255) NOT NULL,
            trigger_type VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            business_impact VARCHAR(50) NOT NULL,
            started_at TIMESTAMP WITH TIME ZONE NOT NULL,
            completed_at TIMESTAMP WITH TIME ZONE,
            duration_seconds FLOAT DEFAULT 0,
            success BOOLEAN DEFAULT FALSE,
            error_message TEXT,
            approved_by VARCHAR(255),
            approved_at TIMESTAMP WITH TIME ZONE,
            event_data JSONB DEFAULT '{}'::jsonb,
            
            INDEX idx_rollback_deployment (deployment_id),
            INDEX idx_rollback_started (started_at),
            INDEX idx_rollback_status (status)
        );
        
        CREATE TABLE IF NOT EXISTS baseline_metrics (
            id SERIAL PRIMARY KEY,
            application VARCHAR(255) NOT NULL,
            metric_date DATE NOT NULL,
            metrics_data JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            INDEX idx_baseline_app_date (application, metric_date)
        );
        """
        
        async with self.pg_pool.acquire() as conn:
            await conn.execute(schema_sql)
        
        logger.info("✅ Rollback database schema initialized")
    
    async def start_monitoring(self) -> None:
        """Start continuous deployment monitoring"""
        logger.info("🔍 Starting rollback monitoring...")
        self.is_running = True
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitoring_loop()),
            asyncio.create_task(self._baseline_metrics_collection()),
            asyncio.create_task(self._cleanup_old_records())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
            self.is_running = False
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Collect current metrics
                current_metrics = await self.metrics_collector.collect_current_metrics()
                
                # Check each active deployment
                for deployment_id, deployment in self.active_deployments.items():
                    try:
                        # Check if rollback is needed
                        should_rollback, trigger, reason = await self.decision_engine.should_trigger_rollback(
                            current_metrics, deployment
                        )
                        
                        if should_rollback:
                            logger.warning(f"🚨 Rollback trigger detected: {deployment.application} - {reason}")
                            
                            # Assess business impact
                            impact = self.decision_engine.assess_business_impact(current_metrics, trigger)
                            
                            # Check if approval required
                            requires_approval = self.decision_engine.should_require_approval(impact, current_metrics)
                            
                            # Create rollback event
                            event = RollbackEvent(
                                event_id=f"RB-{datetime.now(IST).strftime('%Y%m%d%H%M%S')}-{deployment.application}",
                                deployment_id=deployment_id,
                                trigger=trigger,
                                status=RollbackStatus.TRIGGERED,
                                triggering_metrics=current_metrics,
                                threshold_breached=reason,
                                business_impact=impact,
                                auto_rollback_enabled=self.config.enable_auto_rollback,
                                requires_approval=requires_approval
                            )
                            
                            # Save event
                            await self._save_rollback_event(event)
                            
                            # Execute or request approval
                            if requires_approval:
                                await self._request_rollback_approval(event)
                            elif self.config.enable_auto_rollback:
                                await self._execute_automatic_rollback(event, deployment)
                            
                    except Exception as e:
                        logger.error(f"❌ Error monitoring deployment {deployment_id}: {e}")
                
                # Wait before next check
                await asyncio.sleep(self.config.metrics_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _execute_automatic_rollback(self, event: RollbackEvent, 
                                        deployment: DeploymentSnapshot) -> None:
        """Execute automatic rollback"""
        try:
            logger.info(f"🔄 Executing automatic rollback: {event.event_id}")
            
            # Check daily rollback limit
            if await self._check_rollback_limit_exceeded():
                logger.warning("⚠️ Daily rollback limit exceeded - requiring manual approval")
                event.requires_approval = True
                await self._request_rollback_approval(event)
                return
            
            # Execute rollback
            success = await self.rollback_executor.execute_rollback(event, deployment)
            
            if success:
                # Send success notification
                await self._send_rollback_notification(event, "Automatic rollback completed successfully")
                
                # Remove from active deployments (as it's now rolled back)
                if event.deployment_id in self.active_deployments:
                    del self.active_deployments[event.deployment_id]
            else:
                # Send failure notification
                await self._send_rollback_notification(event, "Automatic rollback failed - manual intervention required")
                event.status = RollbackStatus.MANUAL_INTERVENTION_REQUIRED
            
            # Update event
            await self._save_rollback_event(event)
            
        except Exception as e:
            logger.error(f"❌ Automatic rollback execution failed: {e}")
            event.status = RollbackStatus.FAILED
            event.error_message = str(e)
            await self._save_rollback_event(event)
    
    async def _check_rollback_limit_exceeded(self) -> bool:
        """Check if daily rollback limit is exceeded"""
        try:
            today = datetime.now(IST).date()
            
            async with self.pg_pool.acquire() as conn:
                count = await conn.fetchval("""
                    SELECT COUNT(*) FROM rollback_events
                    WHERE DATE(started_at) = $1 AND success = true
                """, today)
                
                return count >= self.config.max_auto_rollbacks_per_day
                
        except Exception as e:
            logger.error(f"❌ Failed to check rollback limit: {e}")
            return False
    
    async def _baseline_metrics_collection(self) -> None:
        """Collect baseline metrics for comparison"""
        while self.is_running:
            try:
                # Collect metrics during stable periods (non-peak hours)
                current_time = datetime.now(IST)
                
                if (not IndianBusinessContext.is_peak_hours(current_time) and
                    not IndianBusinessContext.is_festival_season(current_time)):
                    
                    metrics = await self.metrics_collector.collect_current_metrics()
                    
                    # Store as baseline for each application
                    for deployment in self.active_deployments.values():
                        self.decision_engine.baseline_metrics[deployment.application] = metrics
                        
                        # Also store in database for persistence
                        await self._save_baseline_metrics(deployment.application, metrics)
                
                # Update baseline every hour during stable periods
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Baseline metrics collection error: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_records(self) -> None:
        """Cleanup old records to manage database size"""
        while self.is_running:
            try:
                # Clean up every 24 hours
                await asyncio.sleep(86400)
                
                cutoff_date = datetime.now(IST) - timedelta(days=30)
                
                async with self.pg_pool.acquire() as conn:
                    # Archive old rollback events
                    await conn.execute("""
                        DELETE FROM rollback_events 
                        WHERE started_at < $1
                    """, cutoff_date)
                    
                    # Keep baseline metrics for 90 days
                    baseline_cutoff = datetime.now(IST).date() - timedelta(days=90)
                    await conn.execute("""
                        DELETE FROM baseline_metrics 
                        WHERE metric_date < $1
                    """, baseline_cutoff)
                
                logger.info("🧹 Old records cleaned up")
                
            except Exception as e:
                logger.error(f"❌ Cleanup error: {e}")
    
    async def register_deployment(self, deployment: DeploymentSnapshot) -> None:
        """Register new deployment for monitoring"""
        try:
            logger.info(f"📝 Registering deployment for monitoring: {deployment.application}")
            
            # Save deployment to database
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO deployments 
                    (deployment_id, application, namespace, image_tag, previous_image_tag,
                     replicas, previous_replicas, deployed_at, deployed_by, deployment_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (deployment_id) DO UPDATE SET
                        image_tag = EXCLUDED.image_tag,
                        replicas = EXCLUDED.replicas,
                        deployed_at = EXCLUDED.deployed_at
                """,
                deployment.deployment_id, deployment.application, deployment.namespace,
                deployment.image_tag, deployment.previous_image_tag, deployment.replicas,
                deployment.previous_replicas, deployment.deployed_at, deployment.deployed_by,
                json.dumps(deployment.__dict__, default=str))
            
            # Add to active monitoring
            self.active_deployments[deployment.deployment_id] = deployment
            
            logger.info(f"✅ Deployment registered: {deployment.deployment_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to register deployment: {e}")
    
    async def _save_rollback_event(self, event: RollbackEvent) -> None:
        """Save rollback event to database"""
        try:
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO rollback_events
                    (event_id, deployment_id, trigger_type, status, business_impact,
                     started_at, completed_at, duration_seconds, success, error_message,
                     approved_by, approved_at, event_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    ON CONFLICT (event_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        completed_at = EXCLUDED.completed_at,
                        duration_seconds = EXCLUDED.duration_seconds,
                        success = EXCLUDED.success,
                        error_message = EXCLUDED.error_message,
                        approved_by = EXCLUDED.approved_by,
                        approved_at = EXCLUDED.approved_at
                """,
                event.event_id, event.deployment_id, event.trigger.value, event.status.value,
                event.business_impact.value, event.started_at, event.completed_at,
                event.duration_seconds, event.success, event.error_message,
                event.approved_by, event.approved_at, json.dumps(event.__dict__, default=str))
                
        except Exception as e:
            logger.error(f"❌ Failed to save rollback event: {e}")
    
    async def _save_baseline_metrics(self, application: str, metrics: BusinessMetrics) -> None:
        """Save baseline metrics"""
        try:
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO baseline_metrics (application, metric_date, metrics_data)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (application, metric_date) DO UPDATE SET
                        metrics_data = EXCLUDED.metrics_data
                """,
                application, datetime.now(IST).date(), json.dumps(metrics.__dict__, default=str))
                
        except Exception as e:
            logger.error(f"❌ Failed to save baseline metrics: {e}")
    
    async def _request_rollback_approval(self, event: RollbackEvent) -> None:
        """Request manual approval for rollback"""
        logger.info(f"👨‍💻 Requesting rollback approval: {event.event_id}")
        # Send approval request via Slack, email, SMS
        await self._send_rollback_notification(event, "Manual approval required for rollback")
    
    async def _send_rollback_notification(self, event: RollbackEvent, message: str) -> None:
        """Send rollback notifications"""
        logger.info(f"📢 Rollback notification: {event.event_id} - {message}")
        # Implementation would send to Slack, Teams, email, SMS
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring"""
        logger.info("🛑 Stopping rollback monitoring...")
        self.is_running = False
        
        if self.pg_pool:
            await self.pg_pool.close()
        
        logger.info("✅ Rollback monitoring stopped")


async def main():
    """Main function for rollback automation"""
    print("🔄 GitOps Rollback Automation Framework")
    print("=" * 50)
    
    # Configuration
    config = RollbackConfig(
        prometheus_url=os.getenv("PROMETHEUS_URL", "http://prometheus:9090"),
        postgres_url=os.getenv("DATABASE_URL", "postgresql://user:pass@postgres:5432/rollback"),
        namespace_patterns=['production', 'prod'],
        error_rate_threshold=5.0,
        latency_threshold_ms=2000,
        conversion_drop_threshold=20.0,
        revenue_drop_threshold=15.0,
        upi_failure_threshold=10.0,
        enable_business_hours_protection=True,
        enable_festival_season_protection=True,
        enable_auto_rollback=True,
        max_auto_rollbacks_per_day=3,
        require_approval_for_critical_impact=True,
        slack_webhook=os.getenv("SLACK_WEBHOOK", ""),
        primary_region="mumbai"
    )
    
    # Initialize framework
    framework = RollbackAutomationFramework(config)
    
    try:
        if await framework.initialize():
            print("✅ Rollback Automation Framework initialized successfully")
            
            # Example: Register a deployment for monitoring
            example_deployment = DeploymentSnapshot(
                deployment_id="DEPLOY-2024-001",
                application="ecommerce-api",
                namespace="production",
                image_tag="v2.1.0",
                replicas=5,
                previous_image_tag="v2.0.0",
                previous_replicas=3,
                deployed_by="gitops-controller"
            )
            
            await framework.register_deployment(example_deployment)
            print(f"📝 Registered deployment: {example_deployment.deployment_id}")
            
            # Start monitoring (this would run indefinitely in production)
            print("🔍 Starting rollback monitoring...")
            await framework.start_monitoring()
            
        else:
            print("❌ Failed to initialize Rollback Automation Framework")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping rollback automation...")
        await framework.stop_monitoring()
    except Exception as e:
        print(f"❌ Rollback automation error: {e}")
        await framework.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
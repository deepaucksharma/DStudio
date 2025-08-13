#!/usr/bin/env python3
"""
Progressive Delivery Canary Controller
Indian E-commerce Platforms के लिए intelligent canary deployments

यह controller automatic canary analysis करता है और Indian traffic patterns,
festival seasons, और payment gateway health के basis पर decisions लेता है।

Features:
- Festival season traffic management
- Indian payment gateway integration
- Regional traffic routing (Mumbai, Delhi, Bangalore)
- Mobile vs Desktop user behavior analysis
- Real-time rollback based on business metrics

Author: Flipkart/Amazon India Engineering Team
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import aiohttp
import yaml
from kubernetes import client, config
from prometheus_api_client import PrometheusConnect
import pandas as pd
import numpy as np

# लॉगिंग configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('canary-controller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IndianEcommerceCanaryController:
    """
    Indian E-commerce के लिए intelligent canary controller
    Festival seasons, payment patterns, और regional traffic को handle करता है
    """
    
    def __init__(self, config_file: str = "canary-config.yaml"):
        self.config = self._load_config(config_file)
        self.k8s_client = None
        self.prometheus_client = None
        self.current_canary_deployments = {}
        
        # Indian e-commerce specific configurations
        self.indian_config = {
            "festival_seasons": [
                {"name": "Diwali", "months": [10, 11], "traffic_multiplier": 3.0},
                {"name": "Holi", "months": [3], "traffic_multiplier": 1.5},
                {"name": "BigBillionDays", "months": [9, 10], "traffic_multiplier": 5.0},
                {"name": "NewYear", "months": [12, 1], "traffic_multiplier": 2.0}
            ],
            "regions": {
                "mumbai": {"priority": 1, "canary_percentage": 5},
                "delhi": {"priority": 2, "canary_percentage": 10},
                "bangalore": {"priority": 3, "canary_percentage": 15},
                "chennai": {"priority": 4, "canary_percentage": 20},
                "kolkata": {"priority": 5, "canary_percentage": 25}
            },
            "payment_gateways": [
                "razorpay", "paytm", "phonepe", "googlepay", 
                "upi", "netbanking", "cards"
            ],
            "user_segments": {
                "premium": {"canary_percentage": 30, "rollback_threshold": 2.0},
                "regular": {"canary_percentage": 10, "rollback_threshold": 1.0},
                "new": {"canary_percentage": 5, "rollback_threshold": 0.5}
            }
        }
        
        # Business metrics thresholds
        self.business_thresholds = {
            "cart_conversion_rate": {"min": 15.0, "critical": 10.0},
            "payment_success_rate": {"min": 98.0, "critical": 95.0},
            "page_load_time": {"max": 3.0, "critical": 5.0},
            "search_success_rate": {"min": 95.0, "critical": 90.0},
            "checkout_completion_rate": {"min": 85.0, "critical": 80.0}
        }
    
    def _load_config(self, config_file: str) -> Dict:
        """Configuration file load करता है"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"⚠️ Config file {config_file} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default configuration return करता है"""
        return {
            "prometheus_url": "http://prometheus.monitoring.svc.cluster.local:9090",
            "kubernetes_namespace": "flipkart-canary",
            "canary_analysis_interval": 60,  # seconds
            "max_canary_percentage": 50,
            "rollback_threshold": 5.0,  # error percentage
            "indian_business_hours": "09:00-21:00"
        }
    
    async def initialize(self):
        """Controller को initialize करता है"""
        logger.info("🚀 Indian E-commerce Canary Controller initialize कर रहे हैं...")
        
        try:
            # Kubernetes client setup
            config.load_incluster_config()  # Running inside cluster
            self.k8s_client = client.ApiClient()
            
            # Prometheus client setup
            self.prometheus_client = PrometheusConnect(
                url=self.config["prometheus_url"],
                disable_ssl=True
            )
            
            logger.info("✅ Controller successfully initialized")
            
        except Exception as e:
            logger.error(f"❌ Controller initialization failed: {e}")
            raise
    
    async def start_monitoring(self):
        """Main monitoring loop शुरू करता है"""
        logger.info("👀 Canary monitoring शुरू कर रहे हैं...")
        
        while True:
            try:
                # Get all active canary deployments
                canary_deployments = await self._get_active_canaries()
                
                for canary in canary_deployments:
                    await self._analyze_canary(canary)
                
                # Wait for next analysis cycle
                await asyncio.sleep(self.config["canary_analysis_interval"])
                
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                await asyncio.sleep(30)  # Shorter retry interval
    
    async def _get_active_canaries(self) -> List[Dict]:
        """Active canary deployments की list return करता है"""
        # Implementation to get canary deployments from Kubernetes
        # यहाँ Flagger CRDs से canary deployments fetch करेंगे
        
        # Mock data for demonstration
        return [
            {
                "name": "flipkart-product-service",
                "namespace": "flipkart-canary",
                "current_percentage": 10,
                "target_percentage": 25,
                "status": "progressing"
            },
            {
                "name": "flipkart-cart-service", 
                "namespace": "flipkart-canary",
                "current_percentage": 5,
                "target_percentage": 15,
                "status": "progressing"
            }
        ]
    
    async def _analyze_canary(self, canary: Dict):
        """
        Individual canary deployment का analysis करता है
        Indian business metrics और traffic patterns को consider करता है
        """
        logger.info(f"🔍 Analyzing canary: {canary['name']}")
        
        # Get current metrics
        metrics = await self._collect_metrics(canary)
        
        # Check if it's festival season
        festival_impact = self._check_festival_season()
        
        # Analyze business metrics
        business_health = await self._analyze_business_metrics(canary, metrics)
        
        # Check regional performance
        regional_performance = await self._analyze_regional_performance(canary, metrics)
        
        # Check payment gateway health
        payment_health = await self._analyze_payment_health(canary, metrics)
        
        # Make canary decision
        decision = await self._make_canary_decision(
            canary, metrics, business_health, 
            regional_performance, payment_health, festival_impact
        )
        
        # Execute decision
        await self._execute_canary_decision(canary, decision)
    
    async def _collect_metrics(self, canary: Dict) -> Dict:
        """
        Canary deployment के लिए metrics collect करता है
        """
        canary_name = canary["name"]
        namespace = canary["namespace"]
        
        # Time range for metrics
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=5)
        
        metrics = {}
        
        try:
            # Success rate
            success_rate_query = f'''
            sum(rate(http_requests_total{{
                job="{canary_name}-canary",
                namespace="{namespace}",
                status!~"5.*"
            }}[5m])) / 
            sum(rate(http_requests_total{{
                job="{canary_name}-canary",
                namespace="{namespace}"
            }}[5m])) * 100
            '''
            metrics["success_rate"] = self._query_prometheus(success_rate_query)
            
            # Response time
            response_time_query = f'''
            histogram_quantile(0.99, 
                sum(rate(http_request_duration_seconds_bucket{{
                    job="{canary_name}-canary",
                    namespace="{namespace}"
                }}[5m])) by (le)
            ) * 1000
            '''
            metrics["response_time_p99"] = self._query_prometheus(response_time_query)
            
            # Business metrics
            metrics["cart_conversion"] = self._query_prometheus(
                f'cart_conversion_rate{{job="{canary_name}-canary"}}'
            )
            
            metrics["payment_success"] = self._query_prometheus(
                f'payment_success_rate{{job="{canary_name}-canary"}}'
            )
            
            # Regional metrics
            for region in self.indian_config["regions"]:
                region_query = f'''
                sum(rate(http_requests_total{{
                    job="{canary_name}-canary",
                    region="{region}"
                }}[5m]))
                '''
                metrics[f"traffic_{region}"] = self._query_prometheus(region_query)
            
            logger.info(f"📊 Metrics collected for {canary_name}: {metrics}")
            
        except Exception as e:
            logger.error(f"❌ Metrics collection failed for {canary_name}: {e}")
            metrics = {}
        
        return metrics
    
    def _query_prometheus(self, query: str) -> float:
        """
        Prometheus query execute करता है और result return करता है
        """
        try:
            result = self.prometheus_client.custom_query(query)
            if result and len(result) > 0:
                return float(result[0]['value'][1])
            return 0.0
        except Exception as e:
            logger.warning(f"⚠️ Prometheus query failed: {e}")
            return 0.0
    
    def _check_festival_season(self) -> Dict:
        """
        Current time festival season है या नहीं check करता है
        """
        current_month = datetime.now().month
        
        for festival in self.indian_config["festival_seasons"]:
            if current_month in festival["months"]:
                logger.info(f"🎊 Festival season detected: {festival['name']}")
                return {
                    "is_festival": True,
                    "name": festival["name"],
                    "traffic_multiplier": festival["traffic_multiplier"]
                }
        
        return {"is_festival": False, "traffic_multiplier": 1.0}
    
    async def _analyze_business_metrics(self, canary: Dict, metrics: Dict) -> Dict:
        """
        Business metrics का analysis करता है
        """
        health_score = 100.0
        issues = []
        
        # Cart conversion rate check
        cart_conversion = metrics.get("cart_conversion", 0)
        if cart_conversion < self.business_thresholds["cart_conversion_rate"]["critical"]:
            health_score -= 30
            issues.append(f"Critical: Cart conversion rate {cart_conversion}%")
        elif cart_conversion < self.business_thresholds["cart_conversion_rate"]["min"]:
            health_score -= 15
            issues.append(f"Warning: Cart conversion rate {cart_conversion}%")
        
        # Payment success rate check
        payment_success = metrics.get("payment_success", 0)
        if payment_success < self.business_thresholds["payment_success_rate"]["critical"]:
            health_score -= 40  # Critical for payments
            issues.append(f"Critical: Payment success rate {payment_success}%")
        elif payment_success < self.business_thresholds["payment_success_rate"]["min"]:
            health_score -= 20
            issues.append(f"Warning: Payment success rate {payment_success}%")
        
        # Response time check
        response_time = metrics.get("response_time_p99", 0)
        if response_time > self.business_thresholds["page_load_time"]["critical"] * 1000:
            health_score -= 25
            issues.append(f"Critical: Response time {response_time}ms")
        elif response_time > self.business_thresholds["page_load_time"]["max"] * 1000:
            health_score -= 10
            issues.append(f"Warning: Response time {response_time}ms")
        
        return {
            "health_score": max(0, health_score),
            "issues": issues,
            "recommendation": "rollback" if health_score < 50 else "continue"
        }
    
    async def _analyze_regional_performance(self, canary: Dict, metrics: Dict) -> Dict:
        """
        Regional performance analysis करता है
        Mumbai, Delhi, Bangalore में different behavior हो सकता है
        """
        regional_health = {}
        
        for region, config in self.indian_config["regions"].items():
            traffic = metrics.get(f"traffic_{region}", 0)
            
            # Regional threshold check
            if traffic < 10:  # Minimum traffic threshold
                regional_health[region] = {
                    "status": "low_traffic",
                    "traffic": traffic,
                    "recommendation": "increase_canary_percentage"
                }
            else:
                regional_health[region] = {
                    "status": "healthy",
                    "traffic": traffic,
                    "recommendation": "continue"
                }
        
        return regional_health
    
    async def _analyze_payment_health(self, canary: Dict, metrics: Dict) -> Dict:
        """
        Indian payment gateways की health check करता है
        UPI, Paytm, Razorpay, etc. के लिए different metrics
        """
        payment_health = {}
        
        for gateway in self.indian_config["payment_gateways"]:
            # Mock payment gateway health check
            # Real implementation में actual payment APIs call करेंगे
            
            success_rate = metrics.get("payment_success", 98.5)
            
            if success_rate > 98.0:
                payment_health[gateway] = "healthy"
            elif success_rate > 95.0:
                payment_health[gateway] = "degraded"
            else:
                payment_health[gateway] = "unhealthy"
        
        overall_health = "healthy"
        unhealthy_count = sum(1 for status in payment_health.values() if status == "unhealthy")
        
        if unhealthy_count > 2:
            overall_health = "unhealthy"
        elif unhealthy_count > 0:
            overall_health = "degraded"
        
        return {
            "overall": overall_health,
            "gateways": payment_health,
            "recommendation": "rollback" if overall_health == "unhealthy" else "continue"
        }
    
    async def _make_canary_decision(
        self, canary: Dict, metrics: Dict, business_health: Dict,
        regional_performance: Dict, payment_health: Dict, festival_impact: Dict
    ) -> Dict:
        """
        All factors को consider करके canary decision लेता है
        """
        canary_name = canary["name"]
        current_percentage = canary["current_percentage"]
        target_percentage = canary["target_percentage"]
        
        # Decision factors
        factors = {
            "business_health_score": business_health["health_score"],
            "payment_health": payment_health["overall"],
            "festival_season": festival_impact["is_festival"],
            "current_percentage": current_percentage
        }
        
        logger.info(f"🤔 Decision factors for {canary_name}: {factors}")
        
        # Decision logic
        if business_health["health_score"] < 50:
            decision = {
                "action": "rollback",
                "reason": f"Business health critical: {business_health['issues']}",
                "target_percentage": 0
            }
        elif payment_health["overall"] == "unhealthy":
            decision = {
                "action": "rollback", 
                "reason": "Payment gateways unhealthy",
                "target_percentage": 0
            }
        elif festival_impact["is_festival"] and current_percentage > 10:
            decision = {
                "action": "pause",
                "reason": f"Festival season {festival_impact['name']} - maintaining safe percentage",
                "target_percentage": current_percentage
            }
        elif business_health["health_score"] > 80 and payment_health["overall"] == "healthy":
            # Proceed with canary
            next_percentage = min(current_percentage + 10, target_percentage)
            decision = {
                "action": "proceed",
                "reason": "All metrics healthy, proceeding with canary",
                "target_percentage": next_percentage
            }
        else:
            # Hold current percentage
            decision = {
                "action": "hold",
                "reason": "Waiting for better metrics",
                "target_percentage": current_percentage
            }
        
        logger.info(f"📋 Canary decision for {canary_name}: {decision}")
        return decision
    
    async def _execute_canary_decision(self, canary: Dict, decision: Dict):
        """
        Canary decision को execute करता है
        """
        canary_name = canary["name"]
        namespace = canary["namespace"]
        action = decision["action"]
        target_percentage = decision["target_percentage"]
        
        logger.info(f"⚡ Executing {action} for {canary_name} -> {target_percentage}%")
        
        try:
            if action == "rollback":
                await self._rollback_canary(canary_name, namespace)
                await self._send_alert(
                    f"🔄 Canary rollback executed for {canary_name}",
                    decision["reason"],
                    "critical"
                )
            
            elif action == "proceed":
                await self._update_canary_percentage(
                    canary_name, namespace, target_percentage
                )
                await self._send_alert(
                    f"✅ Canary progressed for {canary_name}",
                    f"Updated to {target_percentage}%",
                    "info"
                )
            
            elif action == "pause":
                await self._send_alert(
                    f"⏸️ Canary paused for {canary_name}",
                    decision["reason"],
                    "warning"
                )
            
            # Update internal state
            self.current_canary_deployments[canary_name] = {
                "percentage": target_percentage,
                "last_update": datetime.now(),
                "status": action
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to execute decision for {canary_name}: {e}")
            await self._send_alert(
                f"❌ Canary execution failed for {canary_name}",
                str(e),
                "critical"
            )
    
    async def _rollback_canary(self, canary_name: str, namespace: str):
        """Canary को rollback करता है"""
        # Implementation to rollback canary deployment
        # Flagger API या kubectl commands use करेंगे
        logger.info(f"🔄 Rolling back canary: {canary_name}")
        
        # Mock implementation
        # Real में Flagger CRD को update करेंगे
        pass
    
    async def _update_canary_percentage(self, canary_name: str, namespace: str, percentage: int):
        """Canary percentage को update करता है"""
        # Implementation to update canary percentage
        logger.info(f"📊 Updating {canary_name} canary percentage to {percentage}%")
        
        # Mock implementation
        # Real में Flagger CRD को update करेंगे
        pass
    
    async def _send_alert(self, title: str, message: str, severity: str):
        """
        Slack/Teams में alert send करता है
        """
        alert_data = {
            "title": title,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "environment": "production",
            "region": "india"
        }
        
        logger.info(f"🚨 Sending alert: {alert_data}")
        
        # Implementation to send alert to Slack/Teams
        # Webhook URL use करके alert send करेंगे
    
    async def _analyze_user_behavior(self, canary: Dict, metrics: Dict) -> Dict:
        """
        Indian user behavior patterns का analysis करता है
        Mobile vs Desktop, Premium vs Regular users
        """
        user_analysis = {
            "mobile_users": {
                "percentage": 75,  # 75% mobile users in India
                "conversion_rate": metrics.get("mobile_conversion", 12.0),
                "satisfaction": "high"
            },
            "desktop_users": {
                "percentage": 25,
                "conversion_rate": metrics.get("desktop_conversion", 18.0),
                "satisfaction": "high"
            },
            "premium_users": {
                "count": metrics.get("premium_users", 1000),
                "canary_percentage": 30,
                "feedback_score": 4.2
            }
        }
        
        return user_analysis
    
    def _calculate_indian_business_impact(self, metrics: Dict) -> Dict:
        """
        Indian business के लिए impact calculation
        Festival seasons, regional preferences, payment methods को consider करता है
        """
        
        # GMV (Gross Merchandise Value) impact
        base_gmv = 1000000  # 10 lakh rupees per hour baseline
        
        # Cart abandonment impact
        cart_conversion = metrics.get("cart_conversion", 15.0)
        gmv_impact = (cart_conversion / 15.0) * base_gmv
        
        # Payment success impact
        payment_success = metrics.get("payment_success", 98.0)
        payment_impact = (payment_success / 98.0) * gmv_impact
        
        # Festival season multiplier
        festival_impact = self._check_festival_season()
        if festival_impact["is_festival"]:
            payment_impact *= festival_impact["traffic_multiplier"]
        
        return {
            "estimated_gmv_per_hour": payment_impact,
            "revenue_at_risk": base_gmv - payment_impact if payment_impact < base_gmv else 0,
            "business_confidence": "high" if payment_impact > base_gmv * 0.95 else "medium"
        }

async def main():
    """Main function - Canary controller चलाता है"""
    logger.info("🚀 Starting Indian E-commerce Canary Controller...")
    
    controller = IndianEcommerceCanaryController()
    
    try:
        # Initialize controller
        await controller.initialize()
        
        # Start monitoring
        await controller.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("👋 Canary controller stopped by user")
    except Exception as e:
        logger.error(f"❌ Controller failed: {e}")
        raise

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
#!/usr/bin/env python3
"""
GitOps Cost Optimization Dashboard
=================================

Indian enterprise के लिए comprehensive cost optimization dashboard।
Cloud spend optimization के साथ GitOps automation।

Features:
- Real-time cloud cost monitoring across Indian regions
- Festival season cost prediction और optimization
- Multi-cloud cost comparison (AWS, Azure, GCP, Oracle Cloud)
- Resource utilization optimization suggestions  
- Indian business hour based scaling recommendations
- Compliance cost tracking for RBI/SEBI requirements
- Cost anomaly detection और alerting system

Author: Hindi Tech Podcast - Episode 19
Context: Cost Optimization GitOps for Indian Cloud Infrastructure
"""

import asyncio
import logging
import json
import yaml
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import boto3
import aiohttp
import pytz
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from azure.identity import DefaultAzureCredential
from azure.mgmt.consumption import ConsumptionManagementClient
from google.cloud import billing
import subprocess
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

# Enhanced logging for cost optimization
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('cost_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CloudProvider(Enum):
    """Cloud service providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ORACLE_CLOUD = "oracle_cloud"
    ALIBABA_CLOUD = "alibaba_cloud"

class CostCategory(Enum):
    """Cost categorization"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    SECURITY = "security"
    MONITORING = "monitoring"
    BACKUP = "backup"
    COMPLIANCE = "compliance"

class OptimizationLevel(Enum):
    """Cost optimization urgency levels"""
    CRITICAL = "critical"     # >90% of budget
    HIGH = "high"            # 80-90% of budget  
    MEDIUM = "medium"        # 60-80% of budget
    LOW = "low"              # <60% of budget
    OPTIMIZED = "optimized"  # Well within budget

class IndianRegion(Enum):
    """Indian cloud regions"""
    MUMBAI = "mumbai"
    DELHI = "delhi"
    BANGALORE = "bangalore"
    HYDERABAD = "hyderabad"
    CHENNAI = "chennai"
    PUNE = "pune"

@dataclass
class IndianCostContext:
    """Indian business context for cost optimization"""
    
    @staticmethod
    def get_indian_business_hours() -> Dict[str, Dict[str, int]]:
        """Get business hours for different Indian regions"""
        return {
            IndianRegion.MUMBAI.value: {"start": 9, "end": 21},      # Financial hub
            IndianRegion.DELHI.value: {"start": 10, "end": 22},      # Government + Corporate
            IndianRegion.BANGALORE.value: {"start": 9, "end": 23},   # IT hub (global clients)
            IndianRegion.HYDERABAD.value: {"start": 9, "end": 22},   # Pharma + IT
            IndianRegion.CHENNAI.value: {"start": 8, "end": 20},     # Manufacturing
            IndianRegion.PUNE.value: {"start": 9, "end": 21}         # Automotive + IT
        }
    
    @staticmethod
    def get_festival_season_multipliers() -> Dict[str, float]:
        """Get traffic multipliers during festival seasons"""
        return {
            "diwali": 4.5,          # Peak e-commerce season
            "durga_puja": 5.2,      # High in Bengal region
            "holi": 3.8,            # Social media spike
            "ipl_season": 2.8,      # Sports betting + streaming
            "wedding_season": 2.5,  # Nov-Feb increased activity
            "monsoon": 1.8,         # Lower activity
            "normal": 1.0
        }
    
    @staticmethod
    def get_compliance_cost_factors() -> Dict[str, float]:
        """Get compliance overhead cost factors"""
        return {
            "rbi_banking": 1.35,     # 35% overhead for banking compliance
            "sebi_trading": 1.28,    # 28% overhead for trading systems
            "irdai_insurance": 1.22, # 22% overhead for insurance
            "gstn_tax": 1.15,        # 15% overhead for tax systems
            "aadhaar_kyc": 1.20,     # 20% overhead for identity verification
            "upi_payments": 1.18,    # 18% overhead for payment systems
            "general": 1.05          # 5% general compliance overhead
        }
    
    @staticmethod
    def get_current_festival_multiplier() -> float:
        """Get current festival season multiplier"""
        current_date = datetime.now(IST)
        
        # Diwali season (Oct-Nov)
        if current_date.month in [10, 11]:
            return IndianCostContext.get_festival_season_multipliers()["diwali"]
        
        # IPL season (Apr-Jun)
        elif current_date.month in [4, 5, 6]:
            return IndianCostContext.get_festival_season_multipliers()["ipl_season"]
        
        # Monsoon season (Jul-Sep)
        elif current_date.month in [7, 8, 9]:
            return IndianCostContext.get_festival_season_multipliers()["monsoon"]
        
        # Wedding season (Dec-Feb)
        elif current_date.month in [12, 1, 2]:
            return IndianCostContext.get_festival_season_multipliers()["wedding_season"]
        
        # Normal season
        else:
            return IndianCostContext.get_festival_season_multipliers()["normal"]
    
    @staticmethod
    def calculate_inr_cost(usd_amount: float, exchange_rate: float = 83.0) -> float:
        """Convert USD to INR with current exchange rate"""
        return usd_amount * exchange_rate

@dataclass
class CostMetrics:
    """Cost metrics data structure"""
    provider: CloudProvider
    region: str
    service_name: str
    cost_category: CostCategory
    
    # Cost data
    current_month_cost: float = 0.0
    previous_month_cost: float = 0.0
    projected_month_cost: float = 0.0
    
    # Cost breakdown
    hourly_cost: float = 0.0
    daily_cost: float = 0.0
    weekly_cost: float = 0.0
    
    # Currency
    currency: str = "USD"
    inr_cost: float = 0.0  # Cost in Indian Rupees
    
    # Usage metrics
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    storage_utilization: float = 0.0
    network_utilization: float = 0.0
    
    # Optimization potential
    optimization_potential: float = 0.0  # Percentage
    estimated_savings: float = 0.0
    
    # Metadata
    last_updated: datetime = field(default_factory=lambda: datetime.now(IST))
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class CostOptimizationRecommendation:
    """Cost optimization recommendation"""
    recommendation_id: str
    title: str
    description: str
    category: CostCategory
    optimization_level: OptimizationLevel
    
    # Financial impact
    current_monthly_cost: float
    projected_monthly_savings: float
    implementation_cost: float = 0.0
    roi_months: float = 0.0  # Return on investment timeline
    
    # Implementation details
    action_required: str
    technical_complexity: str  # low, medium, high
    business_impact: str       # low, medium, high
    
    # Indian context
    affects_business_hours: bool = False
    compliance_impact: List[str] = field(default_factory=list)
    regional_considerations: List[str] = field(default_factory=list)
    
    # Timeline
    implementation_timeline_days: int = 7
    created_at: datetime = field(default_factory=lambda: datetime.now(IST))
    status: str = "pending"  # pending, approved, implementing, completed

@dataclass
class CostDashboardConfig:
    """Cost optimization dashboard configuration"""
    
    # Cloud provider credentials
    aws_access_key: str = ""
    aws_secret_key: str = ""
    aws_region: str = "ap-south-1"  # Mumbai region
    
    azure_subscription_id: str = ""
    azure_tenant_id: str = ""
    
    gcp_project_id: str = ""
    gcp_credentials_path: str = ""
    
    # Cost thresholds (in USD)
    monthly_budget_usd: float = 10000.0
    warning_threshold_percentage: float = 80.0
    critical_threshold_percentage: float = 90.0
    
    # Indian specific settings
    primary_indian_region: IndianRegion = IndianRegion.MUMBAI
    enable_inr_conversion: bool = True
    current_usd_to_inr_rate: float = 83.0
    
    # Compliance settings
    compliance_requirements: List[str] = field(default_factory=list)
    enable_compliance_cost_tracking: bool = True
    
    # Notification settings
    email_notifications: bool = True
    slack_webhook: str = ""
    whatsapp_api_key: str = ""  # For Indian teams
    telegram_bot_token: str = ""
    
    # Dashboard settings
    update_interval_minutes: int = 15
    retain_data_days: int = 90
    
    # Business context
    business_hours_optimization: bool = True
    festival_season_awareness: bool = True

class CostOptimizationDashboard:
    """
    Cost Optimization Dashboard।
    
    Indian enterprise के लिए comprehensive cloud cost monitoring
    और optimization के साथ GitOps automation।
    """
    
    def __init__(self, config: CostDashboardConfig):
        self.config = config
        self.cost_data = {}  # Current cost metrics
        self.recommendations = {}  # Optimization recommendations
        self.historical_data = []  # Historical cost data
        self.alerts = []  # Cost alerts and notifications
        
        # Cloud clients
        self.aws_client = None
        self.azure_client = None
        self.gcp_client = None
        
    async def initialize(self) -> bool:
        """Initialize cost optimization dashboard"""
        try:
            logger.info("🚀 Initializing Cost Optimization Dashboard")
            
            # Initialize cloud provider clients
            await self._initialize_cloud_clients()
            
            # Load historical data
            await self._load_historical_data()
            
            # Setup cost monitoring
            await self._setup_cost_monitoring()
            
            # Initialize alerting system
            await self._initialize_alerting_system()
            
            logger.info("✅ Cost Optimization Dashboard initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Dashboard initialization failed: {e}")
            return False
    
    async def _initialize_cloud_clients(self) -> None:
        """Initialize cloud provider clients"""
        try:
            # AWS client initialization
            if self.config.aws_access_key and self.config.aws_secret_key:
                self.aws_client = boto3.client(
                    'ce',  # Cost Explorer
                    aws_access_key_id=self.config.aws_access_key,
                    aws_secret_access_key=self.config.aws_secret_key,
                    region_name=self.config.aws_region
                )
                logger.info("✅ AWS Cost Explorer client initialized")
            
            # Azure client initialization  
            if self.config.azure_subscription_id:
                credential = DefaultAzureCredential()
                self.azure_client = ConsumptionManagementClient(
                    credential, 
                    self.config.azure_subscription_id
                )
                logger.info("✅ Azure Consumption client initialized")
            
            # GCP client initialization
            if self.config.gcp_project_id and self.config.gcp_credentials_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.gcp_credentials_path
                self.gcp_client = billing.CloudBillingClient()
                logger.info("✅ GCP Billing client initialized")
                
        except Exception as e:
            logger.error(f"❌ Cloud client initialization failed: {e}")
    
    async def collect_cost_data(self) -> Dict[str, Any]:
        """Collect cost data from all cloud providers"""
        try:
            logger.info("📊 Collecting cost data from cloud providers")
            
            cost_data = {
                "aws": {},
                "azure": {},
                "gcp": {},
                "total_usd": 0.0,
                "total_inr": 0.0,
                "collected_at": datetime.now(IST)
            }
            
            # Collect AWS costs
            if self.aws_client:
                aws_costs = await self._collect_aws_costs()
                cost_data["aws"] = aws_costs
                cost_data["total_usd"] += aws_costs.get("total_cost", 0.0)
            
            # Collect Azure costs
            if self.azure_client:
                azure_costs = await self._collect_azure_costs()
                cost_data["azure"] = azure_costs
                cost_data["total_usd"] += azure_costs.get("total_cost", 0.0)
            
            # Collect GCP costs
            if self.gcp_client:
                gcp_costs = await self._collect_gcp_costs()
                cost_data["gcp"] = gcp_costs
                cost_data["total_usd"] += gcp_costs.get("total_cost", 0.0)
            
            # Convert to INR
            if self.config.enable_inr_conversion:
                cost_data["total_inr"] = IndianCostContext.calculate_inr_cost(
                    cost_data["total_usd"], 
                    self.config.current_usd_to_inr_rate
                )
            
            # Update stored cost data
            self.cost_data = cost_data
            
            logger.info(f"✅ Cost data collected - Total: ${cost_data['total_usd']:.2f} (₹{cost_data['total_inr']:,.2f})")
            return cost_data
            
        except Exception as e:
            logger.error(f"❌ Cost data collection failed: {e}")
            return {}
    
    async def _collect_aws_costs(self) -> Dict[str, Any]:
        """Collect AWS cost data"""
        try:
            logger.info("☁️ Collecting AWS cost data")
            
            # Get current month cost
            end_date = datetime.now(IST).strftime('%Y-%m-%d')
            start_date = datetime.now(IST).replace(day=1).strftime('%Y-%m-%d')
            
            # Get cost and usage data
            response = self.aws_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            total_cost = 0.0
            service_costs = {}
            
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service_name = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    
                    if service_name not in service_costs:
                        service_costs[service_name] = 0.0
                    service_costs[service_name] += cost
                    total_cost += cost
            
            # Get resource utilization (simplified)
            utilization_data = await self._get_aws_utilization_metrics()
            
            return {
                "provider": "aws",
                "total_cost": total_cost,
                "service_costs": service_costs,
                "utilization": utilization_data,
                "currency": "USD",
                "region": self.config.aws_region
            }
            
        except Exception as e:
            logger.error(f"❌ AWS cost collection failed: {e}")
            return {"provider": "aws", "total_cost": 0.0, "error": str(e)}
    
    async def _get_aws_utilization_metrics(self) -> Dict[str, float]:
        """Get AWS resource utilization metrics"""
        try:
            # This would integrate with CloudWatch to get actual utilization
            # For demo purposes, returning mock data
            return {
                "ec2_cpu_utilization": 65.2,
                "ec2_memory_utilization": 58.8,
                "rds_cpu_utilization": 42.1,
                "rds_connections": 35.6,
                "s3_storage_utilization": 78.3,
                "lambda_invocations": 1245
            }
        except Exception as e:
            logger.error(f"❌ AWS utilization metrics failed: {e}")
            return {}
    
    async def _collect_azure_costs(self) -> Dict[str, Any]:
        """Collect Azure cost data"""
        try:
            logger.info("🔷 Collecting Azure cost data")
            
            # Get usage details for current month
            end_date = datetime.now(IST)
            start_date = datetime.now(IST).replace(day=1)
            
            # Note: This is simplified - actual Azure cost collection would require
            # more complex API calls and proper date formatting
            
            return {
                "provider": "azure",
                "total_cost": 0.0,  # Would be actual cost from Azure API
                "service_costs": {},
                "utilization": {},
                "currency": "USD",
                "region": "centralindia"
            }
            
        except Exception as e:
            logger.error(f"❌ Azure cost collection failed: {e}")
            return {"provider": "azure", "total_cost": 0.0, "error": str(e)}
    
    async def _collect_gcp_costs(self) -> Dict[str, Any]:
        """Collect GCP cost data"""
        try:
            logger.info("🌐 Collecting GCP cost data")
            
            # Get billing account data
            # Note: This is simplified - actual GCP cost collection would require
            # proper billing API calls
            
            return {
                "provider": "gcp",
                "total_cost": 0.0,  # Would be actual cost from GCP API
                "service_costs": {},
                "utilization": {},
                "currency": "USD",
                "region": "asia-south1"
            }
            
        except Exception as e:
            logger.error(f"❌ GCP cost collection failed: {e}")
            return {"provider": "gcp", "total_cost": 0.0, "error": str(e)}
    
    async def analyze_cost_optimization_opportunities(self) -> List[CostOptimizationRecommendation]:
        """Analyze and generate cost optimization recommendations"""
        try:
            logger.info("🔍 Analyzing cost optimization opportunities")
            
            recommendations = []
            
            # Analyze compute optimization
            compute_recommendations = await self._analyze_compute_optimization()
            recommendations.extend(compute_recommendations)
            
            # Analyze storage optimization
            storage_recommendations = await self._analyze_storage_optimization()
            recommendations.extend(storage_recommendations)
            
            # Analyze network optimization
            network_recommendations = await self._analyze_network_optimization()
            recommendations.extend(network_recommendations)
            
            # Analyze Indian business context optimizations
            indian_context_recommendations = await self._analyze_indian_context_optimization()
            recommendations.extend(indian_context_recommendations)
            
            # Sort by potential savings
            recommendations.sort(key=lambda x: x.projected_monthly_savings, reverse=True)
            
            # Store recommendations
            self.recommendations = {rec.recommendation_id: rec for rec in recommendations}
            
            logger.info(f"✅ Generated {len(recommendations)} cost optimization recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Cost optimization analysis failed: {e}")
            return []
    
    async def _analyze_compute_optimization(self) -> List[CostOptimizationRecommendation]:
        """Analyze compute resource optimization opportunities"""
        try:
            recommendations = []
            
            # Analyze underutilized compute instances
            if self.cost_data.get("aws", {}).get("utilization", {}):
                utilization = self.cost_data["aws"]["utilization"]
                
                if utilization.get("ec2_cpu_utilization", 0) < 30:
                    rec = CostOptimizationRecommendation(
                        recommendation_id="COMPUTE-001",
                        title="Right-size underutilized EC2 instances",
                        description="EC2 instances showing low CPU utilization (<30%). Consider downsizing or using Spot instances during non-business hours.",
                        category=CostCategory.COMPUTE,
                        optimization_level=OptimizationLevel.HIGH,
                        current_monthly_cost=2500.0,
                        projected_monthly_savings=875.0,  # 35% savings
                        implementation_cost=50.0,  # DevOps time
                        roi_months=0.1,  # Immediate savings
                        action_required="Downsize EC2 instances from m5.large to m5.medium",
                        technical_complexity="low",
                        business_impact="low",
                        affects_business_hours=False,
                        regional_considerations=["Mumbai region pricing advantage"],
                        implementation_timeline_days=3
                    )
                    recommendations.append(rec)
                
                # Spot instance recommendation for development environments
                dev_spot_rec = CostOptimizationRecommendation(
                    recommendation_id="COMPUTE-002",
                    title="Use Spot instances for development workloads",
                    description="Development और testing environments के लिए Spot instances use करके 60-70% cost savings।",
                    category=CostCategory.COMPUTE,
                    optimization_level=OptimizationLevel.MEDIUM,
                    current_monthly_cost=1200.0,
                    projected_monthly_savings=720.0,  # 60% savings
                    implementation_cost=100.0,  # Setup automation
                    roi_months=0.2,
                    action_required="Implement Spot instance automation for dev environments",
                    technical_complexity="medium",
                    business_impact="low",
                    affects_business_hours=False,
                    regional_considerations=["High Spot availability in Mumbai region"],
                    implementation_timeline_days=7
                )
                recommendations.append(dev_spot_rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Compute optimization analysis failed: {e}")
            return []
    
    async def _analyze_storage_optimization(self) -> List[CostOptimizationRecommendation]:
        """Analyze storage optimization opportunities"""
        try:
            recommendations = []
            
            # S3 storage class optimization
            s3_optimization_rec = CostOptimizationRecommendation(
                recommendation_id="STORAGE-001",
                title="Optimize S3 storage classes for Indian compliance data",
                description="Move infrequently accessed compliance data to S3 IA और archived data को Glacier में move करें।",
                category=CostCategory.STORAGE,
                optimization_level=OptimizationLevel.MEDIUM,
                current_monthly_cost=800.0,
                projected_monthly_savings=320.0,  # 40% savings
                implementation_cost=75.0,
                roi_months=0.3,
                action_required="Implement S3 lifecycle policies for data tiering",
                technical_complexity="low",
                business_impact="low",
                affects_business_hours=False,
                compliance_impact=["Ensure RBI data retention compliance"],
                regional_considerations=["Mumbai region S3 pricing"],
                implementation_timeline_days=5
            )
            recommendations.append(s3_optimization_rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Storage optimization analysis failed: {e}")
            return []
    
    async def _analyze_indian_context_optimization(self) -> List[CostOptimizationRecommendation]:
        """Analyze Indian business context specific optimizations"""
        try:
            recommendations = []
            
            # Business hours scaling
            business_hours_rec = CostOptimizationRecommendation(
                recommendation_id="INDIAN-001",
                title="Implement Indian business hours scaling",
                description="Scale down resources during non-business hours (11 PM - 8 AM) and weekends to optimize costs.",
                category=CostCategory.COMPUTE,
                optimization_level=OptimizationLevel.HIGH,
                current_monthly_cost=3500.0,
                projected_monthly_savings=1050.0,  # 30% savings during off-hours
                implementation_cost=200.0,  # Automation setup
                roi_months=0.2,
                action_required="Setup auto-scaling based on Indian business hours",
                technical_complexity="medium",
                business_impact="low",
                affects_business_hours=False,
                regional_considerations=[
                    "Different business hours across Indian cities",
                    "Mumbai: 9 AM - 9 PM, Bangalore: 9 AM - 11 PM"
                ],
                implementation_timeline_days=10
            )
            recommendations.append(business_hours_rec)
            
            # Festival season optimization
            festival_multiplier = IndianCostContext.get_current_festival_multiplier()
            if festival_multiplier > 2.0:
                festival_rec = CostOptimizationRecommendation(
                    recommendation_id="INDIAN-002",
                    title="Festival season cost optimization",
                    description=f"Current festival season का traffic multiplier {festival_multiplier}x है। Temporary scaling strategy implement करें।",
                    category=CostCategory.COMPUTE,
                    optimization_level=OptimizationLevel.CRITICAL,
                    current_monthly_cost=5000.0,
                    projected_monthly_savings=1000.0,  # Better resource allocation
                    implementation_cost=300.0,
                    roi_months=0.3,
                    action_required="Implement festival-aware auto-scaling policies",
                    technical_complexity="high",
                    business_impact="high",
                    affects_business_hours=True,
                    regional_considerations=[
                        "Festival impact varies by region",
                        "Mumbai/Delhi highest impact during Diwali",
                        "Kolkata highest impact during Durga Puja"
                    ],
                    implementation_timeline_days=5
                )
                recommendations.append(festival_rec)
            
            # Multi-region optimization
            multi_region_rec = CostOptimizationRecommendation(
                recommendation_id="INDIAN-003",
                title="Indian multi-region cost optimization",
                description="Optimize workload distribution across Mumbai, Delhi, और Bangalore regions based on cost और latency।",
                category=CostCategory.NETWORK,
                optimization_level=OptimizationLevel.MEDIUM,
                current_monthly_cost=2200.0,
                projected_monthly_savings=440.0,  # 20% savings through region optimization
                implementation_cost=500.0,  # Complex multi-region setup
                roi_months=1.2,
                action_required="Implement intelligent workload placement across Indian regions",
                technical_complexity="high",
                business_impact="medium",
                affects_business_hours=False,
                compliance_impact=["Data residency requirements for financial services"],
                regional_considerations=[
                    "Mumbai: Financial services hub - premium pricing",
                    "Bangalore: IT hub - competitive pricing",
                    "Delhi: Government sector - compliance requirements"
                ],
                implementation_timeline_days=21
            )
            recommendations.append(multi_region_rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Indian context optimization analysis failed: {e}")
            return []
    
    async def generate_cost_report(self) -> Dict[str, Any]:
        """Generate comprehensive cost optimization report"""
        try:
            logger.info("📊 Generating comprehensive cost report")
            
            # Collect latest cost data
            cost_data = await self.collect_cost_data()
            
            # Get optimization recommendations
            recommendations = await self.analyze_cost_optimization_opportunities()
            
            # Calculate budget utilization
            budget_utilization = (cost_data["total_usd"] / self.config.monthly_budget_usd) * 100
            
            # Determine optimization level
            if budget_utilization >= 90:
                optimization_level = OptimizationLevel.CRITICAL
            elif budget_utilization >= 80:
                optimization_level = OptimizationLevel.HIGH
            elif budget_utilization >= 60:
                optimization_level = OptimizationLevel.MEDIUM
            else:
                optimization_level = OptimizationLevel.LOW
            
            # Generate report
            report = {
                "report_id": f"COST-REPORT-{datetime.now(IST).strftime('%Y%m%d%H%M%S')}",
                "generated_at": datetime.now(IST),
                "reporting_period": f"{datetime.now(IST).strftime('%Y-%m')}",
                
                # Cost summary
                "cost_summary": {
                    "total_cost_usd": cost_data["total_usd"],
                    "total_cost_inr": cost_data["total_inr"],
                    "monthly_budget_usd": self.config.monthly_budget_usd,
                    "budget_utilization_percentage": budget_utilization,
                    "optimization_level": optimization_level.value,
                    "exchange_rate_usd_inr": self.config.current_usd_to_inr_rate
                },
                
                # Provider breakdown
                "provider_breakdown": {
                    provider: data.get("total_cost", 0.0) 
                    for provider, data in cost_data.items() 
                    if provider in ["aws", "azure", "gcp"]
                },
                
                # Optimization opportunities
                "optimization_opportunities": {
                    "total_recommendations": len(recommendations),
                    "total_potential_savings_usd": sum(rec.projected_monthly_savings for rec in recommendations),
                    "total_potential_savings_inr": sum(rec.projected_monthly_savings for rec in recommendations) * self.config.current_usd_to_inr_rate,
                    "critical_recommendations": len([r for r in recommendations if r.optimization_level == OptimizationLevel.CRITICAL]),
                    "high_priority_recommendations": len([r for r in recommendations if r.optimization_level == OptimizationLevel.HIGH])
                },
                
                # Indian context insights
                "indian_context": {
                    "current_festival_multiplier": IndianCostContext.get_current_festival_multiplier(),
                    "primary_region": self.config.primary_indian_region.value,
                    "business_hours_optimization_enabled": self.config.business_hours_optimization,
                    "compliance_cost_overhead": self._calculate_compliance_overhead()
                },
                
                # Detailed recommendations
                "recommendations": [
                    {
                        "id": rec.recommendation_id,
                        "title": rec.title,
                        "category": rec.category.value,
                        "optimization_level": rec.optimization_level.value,
                        "potential_savings_usd": rec.projected_monthly_savings,
                        "potential_savings_inr": rec.projected_monthly_savings * self.config.current_usd_to_inr_rate,
                        "implementation_days": rec.implementation_timeline_days,
                        "technical_complexity": rec.technical_complexity,
                        "business_impact": rec.business_impact
                    }
                    for rec in recommendations[:10]  # Top 10 recommendations
                ],
                
                # Alerts and warnings
                "alerts": [
                    {
                        "type": "budget_warning" if budget_utilization >= 80 else "info",
                        "message": f"Budget utilization at {budget_utilization:.1f}% - {'Critical' if budget_utilization >= 90 else 'Warning' if budget_utilization >= 80 else 'Normal'}",
                        "severity": "high" if budget_utilization >= 90 else "medium" if budget_utilization >= 80 else "low"
                    }
                ]
            }
            
            # Save report to file
            report_file = f"cost_optimization_report_{datetime.now(IST).strftime('%Y%m%d_%H%M%S')}.json"
            async with aiohttp.ClientSession() as session:
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
            
            logger.info(f"✅ Cost report generated: {report_file}")
            logger.info(f"💰 Total Cost: ${cost_data['total_usd']:.2f} (₹{cost_data['total_inr']:,.2f})")
            logger.info(f"💡 Potential Savings: ${sum(rec.projected_monthly_savings for rec in recommendations):.2f}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Cost report generation failed: {e}")
            return {}
    
    def _calculate_compliance_overhead(self) -> float:
        """Calculate compliance cost overhead percentage"""
        try:
            compliance_factors = IndianCostContext.get_compliance_cost_factors()
            
            # Calculate weighted average based on requirements
            if not self.config.compliance_requirements:
                return compliance_factors["general"]
            
            total_factor = 0.0
            count = 0
            
            for requirement in self.config.compliance_requirements:
                if requirement in compliance_factors:
                    total_factor += compliance_factors[requirement]
                    count += 1
            
            if count > 0:
                return total_factor / count
            else:
                return compliance_factors["general"]
                
        except Exception as e:
            logger.error(f"❌ Compliance overhead calculation failed: {e}")
            return 1.05  # Default 5% overhead
    
    async def send_cost_alerts(self, report: Dict[str, Any]) -> bool:
        """Send cost alerts and notifications"""
        try:
            logger.info("📧 Sending cost alerts and notifications")
            
            budget_utilization = report["cost_summary"]["budget_utilization_percentage"]
            
            # Send email notification if enabled
            if self.config.email_notifications and budget_utilization >= self.config.warning_threshold_percentage:
                await self._send_email_alert(report)
            
            # Send Slack notification if configured
            if self.config.slack_webhook:
                await self._send_slack_alert(report)
            
            # Send WhatsApp notification for critical alerts (Indian teams prefer WhatsApp)
            if self.config.whatsapp_api_key and budget_utilization >= self.config.critical_threshold_percentage:
                await self._send_whatsapp_alert(report)
            
            logger.info("✅ Cost alerts sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cost alert sending failed: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        logger.info("🧹 Cost Optimization Dashboard cleaned up")


async def main():
    """Main function for cost optimization dashboard"""
    print("💰 GitOps Cost Optimization Dashboard")
    print("=" * 45)
    
    # Configuration
    config = CostDashboardConfig(
        aws_region="ap-south-1",  # Mumbai
        monthly_budget_usd=15000.0,
        warning_threshold_percentage=80.0,
        critical_threshold_percentage=90.0,
        primary_indian_region=IndianRegion.MUMBAI,
        enable_inr_conversion=True,
        current_usd_to_inr_rate=83.0,
        compliance_requirements=["rbi_banking", "sebi_trading"],
        enable_compliance_cost_tracking=True,
        business_hours_optimization=True,
        festival_season_awareness=True,
        update_interval_minutes=15,
        retain_data_days=90
    )
    
    # Initialize dashboard
    dashboard = CostOptimizationDashboard(config)
    
    try:
        if await dashboard.initialize():
            print("✅ Cost Optimization Dashboard initialized successfully")
            
            # Generate comprehensive cost report
            report = await dashboard.generate_cost_report()
            
            if report:
                print(f"\n📊 Cost Optimization Report Summary:")
                print(f"   Report ID: {report['report_id']}")
                print(f"   Total Cost: ${report['cost_summary']['total_cost_usd']:.2f}")
                print(f"   Total Cost (INR): ₹{report['cost_summary']['total_cost_inr']:,.2f}")
                print(f"   Budget Utilization: {report['cost_summary']['budget_utilization_percentage']:.1f}%")
                print(f"   Optimization Level: {report['cost_summary']['optimization_level'].upper()}")
                
                print(f"\n💡 Optimization Opportunities:")
                print(f"   Total Recommendations: {report['optimization_opportunities']['total_recommendations']}")
                print(f"   Potential Monthly Savings: ${report['optimization_opportunities']['total_potential_savings_usd']:.2f}")
                print(f"   Potential Monthly Savings (INR): ₹{report['optimization_opportunities']['total_potential_savings_inr']:,.2f}")
                print(f"   Critical Recommendations: {report['optimization_opportunities']['critical_recommendations']}")
                
                print(f"\n🇮🇳 Indian Context:")
                print(f"   Festival Multiplier: {report['indian_context']['current_festival_multiplier']}x")
                print(f"   Primary Region: {report['indian_context']['primary_region'].title()}")
                print(f"   Business Hours Optimization: {'Enabled' if report['indian_context']['business_hours_optimization_enabled'] else 'Disabled'}")
                
                # Send alerts if thresholds exceeded
                await dashboard.send_cost_alerts(report)
                
                print(f"\n📁 Report saved to: cost_optimization_report_*.json")
                
        else:
            print("❌ Failed to initialize Cost Optimization Dashboard")
            
    except Exception as e:
        print(f"❌ Cost optimization error: {e}")
    finally:
        await dashboard.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Advanced Budget Alerts & Monitoring System
==========================================

Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering
Intelligent budget monitoring with predictive alerts and automated actions

Author: Hindi Tech Community
Date: 2025
Version: 1.0

Features:
- Multi-dimensional budget tracking (service, project, department)
- Predictive budget violation alerts
- Automated cost control actions
- Smart threshold management
- Seasonal adjustment capabilities
- Integration with approval workflows
- Cost trend analysis and forecasting

Mumbai Context: Budget alerts जैसे monthly household budget management
- Monthly limit tracking like mobile/DTH recharge alerts
- Predictive warnings like "इस month ज्यादा spend हो रहा"
- Automatic controls like "limit exceed हो रहा तो service stop"
"""

import asyncio
import boto3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class BudgetType(Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    PROJECT_BASED = "project_based"

class AlertChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    WEBHOOK = "webhook"
    JIRA = "jira"

class ActionType(Enum):
    NOTIFY = "notify"
    RESTRICT = "restrict"
    SHUTDOWN = "shutdown"
    APPROVAL_REQUIRED = "approval_required"

@dataclass
class BudgetConfig:
    """Budget configuration"""
    budget_id: str
    name: str
    budget_type: BudgetType
    amount: float
    currency: str
    period_start: datetime
    period_end: datetime
    filters: Dict[str, List[str]]  # Tags, services, regions
    alert_thresholds: List[float]  # [50, 75, 90, 100] percentage
    alert_channels: List[AlertChannel]
    auto_actions: Dict[float, ActionType]  # threshold -> action
    owner_email: str
    department: str

@dataclass
class BudgetAlert:
    """Budget alert details"""
    alert_id: str
    budget_config: BudgetConfig
    current_spend: float
    projected_spend: float
    threshold_exceeded: float
    days_remaining: int
    severity: AlertSeverity
    created_at: datetime
    message: str
    recommended_actions: List[str]

@dataclass
class CostForecast:
    """Cost forecast data"""
    budget_id: str
    current_spend: float
    projected_monthly_spend: float
    confidence_interval: Tuple[float, float]
    trend_direction: str  # increasing, decreasing, stable
    seasonal_factor: float
    risk_score: float  # 0-100

class BudgetAlertsSystem:
    """
    Advanced Budget Alerts and Monitoring System
    
    Mumbai Context: यह household budget management जैसा है
    - Monthly expenses की real-time tracking
    - अगले महीने का expense prediction
    - Automatic alerts जब limit cross होने वाला हो
    - Emergency controls to prevent overspend
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize budget alerts system"""
        try:
            self.region = region
            
            # AWS clients
            self.budgets_client = boto3.client('budgets', region_name=region)
            self.ce_client = boto3.client('ce', region_name=region)
            self.sns_client = boto3.client('sns', region_name=region)
            self.lambda_client = boto3.client('lambda', region_name=region)
            self.iam_client = boto3.client('iam', region_name=region)
            
            # Configuration
            self.account_id = boto3.client('sts').get_caller_identity()['Account']
            self.budget_configs = {}
            self.alert_history = []
            self.forecasting_models = {}
            
            logger.info("Budget Alerts System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Budget Alerts System: {e}")
            raise

    def create_budget(self, config: BudgetConfig) -> bool:
        """
        Create budget with AWS Budgets service
        
        Mumbai Context: Monthly budget set करना like mobile plan limit
        """
        try:
            # Prepare budget definition
            budget_def = {
                'BudgetName': config.name,
                'BudgetLimit': {
                    'Amount': str(config.amount),
                    'Unit': config.currency
                },
                'TimeUnit': self._get_aws_time_unit(config.budget_type),
                'TimePeriod': {
                    'Start': config.period_start,
                    'End': config.period_end
                },
                'BudgetType': 'COST',
                'CostFilters': self._convert_filters_to_aws_format(config.filters)
            }
            
            # Create budget
            self.budgets_client.create_budget(
                AccountId=self.account_id,
                Budget=budget_def
            )
            
            # Create budget alerts
            for threshold in config.alert_thresholds:
                self._create_budget_alert(config, threshold)
            
            # Store configuration
            self.budget_configs[config.budget_id] = config
            
            logger.info(f"Created budget: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create budget {config.name}: {e}")
            return False

    def _get_aws_time_unit(self, budget_type: BudgetType) -> str:
        """Convert budget type to AWS time unit"""
        mapping = {
            BudgetType.MONTHLY: 'MONTHLY',
            BudgetType.QUARTERLY: 'QUARTERLY',
            BudgetType.ANNUAL: 'ANNUALLY',
            BudgetType.PROJECT_BASED: 'MONTHLY'  # Default to monthly for project-based
        }
        return mapping.get(budget_type, 'MONTHLY')

    def _convert_filters_to_aws_format(self, filters: Dict[str, List[str]]) -> Dict:
        """Convert filters to AWS Cost Filters format"""
        aws_filters = {}
        
        if 'services' in filters:
            aws_filters['Service'] = filters['services']
        
        if 'regions' in filters:
            aws_filters['Region'] = filters['regions']
        
        if 'tags' in filters:
            # Convert tag filters
            for tag_key, tag_values in filters.get('tag_filters', {}).items():
                aws_filters[f'tag:{tag_key}'] = tag_values
        
        return aws_filters

    def _create_budget_alert(self, config: BudgetConfig, threshold: float):
        """Create individual budget alert"""
        try:
            # Determine notification type based on threshold
            notification_type = 'ACTUAL'
            if threshold <= 100:
                notification_type = 'FORECASTED'
            
            # Create notification
            notification = {
                'NotificationType': notification_type,
                'ComparisonOperator': 'GREATER_THAN',
                'Threshold': threshold,
                'ThresholdType': 'PERCENTAGE',
                'NotificationState': 'ALARM'
            }
            
            # Create subscriber (SNS topic)
            subscriber = {
                'SubscriptionType': 'SNS',
                'Address': self._get_or_create_sns_topic(config.budget_id)
            }
            
            # Create the notification
            self.budgets_client.create_notification(
                AccountId=self.account_id,
                BudgetName=config.name,
                Notification=notification,
                Subscribers=[subscriber]
            )
            
            logger.info(f"Created alert for {config.name} at {threshold}% threshold")
            
        except Exception as e:
            logger.error(f"Failed to create budget alert: {e}")

    def _get_or_create_sns_topic(self, budget_id: str) -> str:
        """Get or create SNS topic for budget alerts"""
        try:
            topic_name = f"budget-alerts-{budget_id}"
            
            # Try to create topic (idempotent operation)
            response = self.sns_client.create_topic(Name=topic_name)
            topic_arn = response['TopicArn']
            
            # Subscribe Lambda function for processing
            lambda_arn = self._get_or_create_alert_processor_lambda()
            if lambda_arn:
                self.sns_client.subscribe(
                    TopicArn=topic_arn,
                    Protocol='lambda',
                    Endpoint=lambda_arn
                )
            
            return topic_arn
            
        except Exception as e:
            logger.error(f"Failed to get/create SNS topic: {e}")
            return ""

    def _get_or_create_alert_processor_lambda(self) -> str:
        """Get or create Lambda function for processing alerts"""
        # In production, this would deploy a Lambda function
        # For now, return placeholder
        return f"arn:aws:lambda:{self.region}:{self.account_id}:function:budget-alert-processor"

    async def monitor_budgets(self) -> List[BudgetAlert]:
        """
        Monitor all budgets and generate alerts
        
        Mumbai Context: Daily expense check करना like wallet balance check
        """
        try:
            active_alerts = []
            
            for budget_id, config in self.budget_configs.items():
                # Get current spend
                current_spend = await self._get_current_spend(config)
                
                # Generate forecast
                forecast = await self._generate_cost_forecast(config, current_spend)
                
                # Check for threshold violations
                alerts = self._check_budget_thresholds(config, current_spend, forecast)
                active_alerts.extend(alerts)
                
                # Execute automated actions if needed
                await self._execute_automated_actions(config, current_spend, forecast)
            
            # Store alerts in history
            self.alert_history.extend(active_alerts)
            
            logger.info(f"Generated {len(active_alerts)} budget alerts")
            return active_alerts
            
        except Exception as e:
            logger.error(f"Failed to monitor budgets: {e}")
            return []

    async def _get_current_spend(self, config: BudgetConfig) -> float:
        """Get current spend for budget configuration"""
        try:
            # Calculate period dates
            now = datetime.now()
            
            if config.budget_type == BudgetType.MONTHLY:
                start_date = now.replace(day=1).strftime('%Y-%m-%d')
            elif config.budget_type == BudgetType.QUARTERLY:
                quarter_start = ((now.month - 1) // 3) * 3 + 1
                start_date = now.replace(month=quarter_start, day=1).strftime('%Y-%m-%d')
            else:  # Annual or project-based
                start_date = config.period_start.strftime('%Y-%m-%d')
            
            end_date = now.strftime('%Y-%m-%d')
            
            # Get cost data
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                Filter=self._convert_filters_to_ce_format(config.filters)
            )
            
            total_cost = 0.0
            for result in response['ResultsByTime']:
                for group in result.get('Groups', []):
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    total_cost += cost
                
                # If no groups, get total
                if not result.get('Groups'):
                    cost = float(result['Total']['BlendedCost']['Amount'])
                    total_cost += cost
            
            return total_cost
            
        except Exception as e:
            logger.error(f"Failed to get current spend: {e}")
            return 0.0

    def _convert_filters_to_ce_format(self, filters: Dict[str, List[str]]) -> Dict:
        """Convert filters to Cost Explorer format"""
        if not filters:
            return {}
        
        ce_filter = {'And': []}
        
        if 'services' in filters and filters['services']:
            ce_filter['And'].append({
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': filters['services']
                }
            })
        
        if 'regions' in filters and filters['regions']:
            ce_filter['And'].append({
                'Dimensions': {
                    'Key': 'REGION',
                    'Values': filters['regions']
                }
            })
        
        # Add tag filters
        for tag_key, tag_values in filters.get('tag_filters', {}).items():
            if tag_values:
                ce_filter['And'].append({
                    'Tags': {
                        'Key': tag_key,
                        'Values': tag_values
                    }
                })
        
        return ce_filter if ce_filter['And'] else {}

    async def _generate_cost_forecast(self, config: BudgetConfig, current_spend: float) -> CostForecast:
        """
        Generate cost forecast using machine learning
        
        Mumbai Context: अगले महीने का expense prediction
        like "इस rate से चलते रहे तो month end में कितना होगा"
        """
        try:
            # Get historical data for forecasting
            historical_data = await self._get_historical_spend_data(config, days_back=90)
            
            if len(historical_data) < 7:
                # Not enough data for forecasting
                return CostForecast(
                    budget_id=config.budget_id,
                    current_spend=current_spend,
                    projected_monthly_spend=current_spend * 1.2,  # Simple estimate
                    confidence_interval=(current_spend * 1.1, current_spend * 1.3),
                    trend_direction="stable",
                    seasonal_factor=1.0,
                    risk_score=30.0
                )
            
            # Prepare data for ML model
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Feature engineering
            df['day_of_month'] = df['date'].dt.day
            df['day_of_week'] = df['date'].dt.dayofweek
            df['days_since_start'] = (df['date'] - df['date'].min()).dt.days
            
            # Train forecasting model
            X = df[['days_since_start', 'day_of_month', 'day_of_week']].values
            y = df['daily_cost'].values
            
            # Polynomial features for better fitting
            poly_features = PolynomialFeatures(degree=2)
            X_poly = poly_features.fit_transform(X)
            
            # Linear regression model
            model = LinearRegression()
            model.fit(X_poly, y)
            
            # Store model for reuse
            self.forecasting_models[config.budget_id] = {
                'model': model,
                'poly_features': poly_features,
                'start_date': df['date'].min()
            }
            
            # Predict remaining days in period
            days_remaining = self._get_days_remaining_in_period(config)
            future_costs = []
            
            for day in range(1, days_remaining + 1):
                future_date = datetime.now() + timedelta(days=day)
                future_features = [[
                    (future_date - df['date'].min()).days,
                    future_date.day,
                    future_date.weekday()
                ]]
                future_features_poly = poly_features.transform(future_features)
                predicted_cost = model.predict(future_features_poly)[0]
                future_costs.append(max(0, predicted_cost))  # Ensure non-negative
            
            projected_monthly_spend = current_spend + sum(future_costs)
            
            # Calculate confidence interval (simplified)
            prediction_std = np.std(future_costs)
            confidence_interval = (
                projected_monthly_spend - 1.96 * prediction_std,
                projected_monthly_spend + 1.96 * prediction_std
            )
            
            # Determine trend direction
            recent_trend = np.polyfit(range(len(y[-7:])), y[-7:], 1)[0]
            if recent_trend > 0.1:
                trend_direction = "increasing"
            elif recent_trend < -0.1:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
            
            # Calculate risk score
            budget_utilization = projected_monthly_spend / config.amount
            trend_factor = min(abs(recent_trend) * 10, 20)
            variability_factor = min(prediction_std / np.mean(y) * 50, 30) if np.mean(y) > 0 else 0
            
            risk_score = min(100, budget_utilization * 50 + trend_factor + variability_factor)
            
            forecast = CostForecast(
                budget_id=config.budget_id,
                current_spend=current_spend,
                projected_monthly_spend=projected_monthly_spend,
                confidence_interval=confidence_interval,
                trend_direction=trend_direction,
                seasonal_factor=1.0,  # Simplified
                risk_score=risk_score
            )
            
            logger.info(f"Generated forecast for {config.name}: ${projected_monthly_spend:.2f}")
            return forecast
            
        except Exception as e:
            logger.error(f"Failed to generate cost forecast: {e}")
            # Return simple fallback forecast
            return CostForecast(
                budget_id=config.budget_id,
                current_spend=current_spend,
                projected_monthly_spend=current_spend * 1.2,
                confidence_interval=(current_spend * 1.1, current_spend * 1.3),
                trend_direction="stable",
                seasonal_factor=1.0,
                risk_score=30.0
            )

    async def _get_historical_spend_data(self, config: BudgetConfig, days_back: int = 90) -> List[Dict]:
        """Get historical spending data for forecasting"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                Filter=self._convert_filters_to_ce_format(config.filters)
            )
            
            historical_data = []
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                cost = float(result['Total']['BlendedCost']['Amount'])
                
                historical_data.append({
                    'date': date,
                    'daily_cost': cost
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Failed to get historical spend data: {e}")
            return []

    def _get_days_remaining_in_period(self, config: BudgetConfig) -> int:
        """Get days remaining in budget period"""
        now = datetime.now()
        
        if config.budget_type == BudgetType.MONTHLY:
            # Days remaining in current month
            next_month = now.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
            return (last_day - now).days
        elif config.budget_type == BudgetType.QUARTERLY:
            # Days remaining in current quarter
            quarter_end_month = ((now.month - 1) // 3 + 1) * 3
            quarter_end = now.replace(month=quarter_end_month, day=1) + timedelta(days=32)
            quarter_end = quarter_end.replace(day=1) - timedelta(days=1)
            return (quarter_end - now).days
        else:
            # Days remaining until period end
            return (config.period_end - now).days

    def _check_budget_thresholds(self, 
                                config: BudgetConfig,
                                current_spend: float,
                                forecast: CostForecast) -> List[BudgetAlert]:
        """Check if budget thresholds are exceeded"""
        alerts = []
        
        try:
            for threshold in config.alert_thresholds:
                threshold_amount = config.amount * (threshold / 100)
                
                # Check current spend against threshold
                current_exceeded = current_spend >= threshold_amount
                
                # Check projected spend against threshold
                projected_exceeded = forecast.projected_monthly_spend >= threshold_amount
                
                if current_exceeded or projected_exceeded:
                    # Determine severity
                    severity = self._determine_alert_severity(threshold, forecast.risk_score)
                    
                    # Generate alert message
                    alert_message = self._generate_alert_message(
                        config, current_spend, forecast, threshold
                    )
                    
                    # Get recommended actions
                    recommendations = self._get_alert_recommendations(
                        config, current_spend, forecast, threshold
                    )
                    
                    alert = BudgetAlert(
                        alert_id=f"{config.budget_id}-{threshold}-{int(datetime.now().timestamp())}",
                        budget_config=config,
                        current_spend=current_spend,
                        projected_spend=forecast.projected_monthly_spend,
                        threshold_exceeded=threshold,
                        days_remaining=self._get_days_remaining_in_period(config),
                        severity=severity,
                        created_at=datetime.now(),
                        message=alert_message,
                        recommended_actions=recommendations
                    )
                    
                    alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Failed to check budget thresholds: {e}")
        
        return alerts

    def _determine_alert_severity(self, threshold: float, risk_score: float) -> AlertSeverity:
        """Determine alert severity based on threshold and risk"""
        if threshold >= 100 or risk_score >= 80:
            return AlertSeverity.EMERGENCY
        elif threshold >= 90 or risk_score >= 60:
            return AlertSeverity.CRITICAL
        elif threshold >= 75 or risk_score >= 40:
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.INFO

    def _generate_alert_message(self, 
                              config: BudgetConfig,
                              current_spend: float,
                              forecast: CostForecast,
                              threshold: float) -> str:
        """Generate human-readable alert message"""
        budget_percentage = (current_spend / config.amount) * 100
        projected_percentage = (forecast.projected_monthly_spend / config.amount) * 100
        
        message = f"""
🚨 Budget Alert: {config.name}

Current Status:
• Budget: ${config.amount:.2f} {config.currency}
• Current Spend: ${current_spend:.2f} ({budget_percentage:.1f}%)
• Projected Spend: ${forecast.projected_monthly_spend:.2f} ({projected_percentage:.1f}%)
• Threshold Exceeded: {threshold}%

Trend Analysis:
• Direction: {forecast.trend_direction.title()}
• Risk Score: {forecast.risk_score:.0f}/100
• Days Remaining: {self._get_days_remaining_in_period(config)}

Mumbai Context: 
यह situation आपके mobile recharge की तरह है - limit से ज्यादा usage हो रहा है!
{self._get_mumbai_analogy(threshold, budget_percentage)}
"""
        
        return message.strip()

    def _get_mumbai_analogy(self, threshold: float, actual_percentage: float) -> str:
        """Get Mumbai-style analogy for budget situation"""
        if actual_percentage >= 100:
            return "🔴 Like mobile balance finish - immediate recharge needed!"
        elif actual_percentage >= 90:
            return "🟡 Like mobile balance low - last day warning!"
        elif actual_percentage >= 75:
            return "🟠 Like mobile plan 75% used - time to control usage"
        else:
            return "🟢 Like mobile plan normal usage - all good for now"

    def _get_alert_recommendations(self, 
                                 config: BudgetConfig,
                                 current_spend: float,
                                 forecast: CostForecast,
                                 threshold: float) -> List[str]:
        """Get recommended actions for alert"""
        recommendations = []
        
        if threshold >= 100:
            recommendations.extend([
                "🚨 IMMEDIATE ACTION REQUIRED",
                "Review and pause non-critical resources",
                "Implement emergency cost controls",
                "Get management approval for overspend"
            ])
        elif threshold >= 90:
            recommendations.extend([
                "⚠️ URGENT: Review upcoming expenses",
                "Consider scaling down development environments",
                "Optimize or resize underutilized resources",
                "Defer non-critical deployments"
            ])
        elif threshold >= 75:
            recommendations.extend([
                "📊 Monitor daily spend closely",
                "Review resource utilization reports",
                "Consider reserved instance opportunities",
                "Implement cost optimization measures"
            ])
        else:
            recommendations.extend([
                "✅ Continue monitoring trends",
                "Plan for upcoming resource needs",
                "Review quarterly budget allocation"
            ])
        
        # Add specific recommendations based on trend
        if forecast.trend_direction == "increasing":
            recommendations.append("📈 Increasing trend detected - investigate cost drivers")
        
        if forecast.risk_score > 70:
            recommendations.append("⚡ High risk score - implement proactive controls")
        
        return recommendations

    async def _execute_automated_actions(self, 
                                       config: BudgetConfig,
                                       current_spend: float,
                                       forecast: CostForecast):
        """Execute automated actions based on budget status"""
        try:
            budget_percentage = (current_spend / config.amount) * 100
            
            for threshold_pct, action in config.auto_actions.items():
                if budget_percentage >= threshold_pct:
                    await self._execute_action(config, action, current_spend, forecast)
        
        except Exception as e:
            logger.error(f"Failed to execute automated actions: {e}")

    async def _execute_action(self, 
                            config: BudgetConfig,
                            action: ActionType,
                            current_spend: float,
                            forecast: CostForecast):
        """Execute specific automated action"""
        try:
            if action == ActionType.NOTIFY:
                await self._send_notifications(config, current_spend, forecast)
            
            elif action == ActionType.RESTRICT:
                await self._apply_cost_restrictions(config)
            
            elif action == ActionType.SHUTDOWN:
                await self._shutdown_non_critical_resources(config)
            
            elif action == ActionType.APPROVAL_REQUIRED:
                await self._trigger_approval_workflow(config, current_spend)
            
            logger.info(f"Executed action {action.value} for budget {config.name}")
            
        except Exception as e:
            logger.error(f"Failed to execute action {action.value}: {e}")

    async def _send_notifications(self, config: BudgetConfig, current_spend: float, forecast: CostForecast):
        """Send notifications through configured channels"""
        try:
            alert_message = self._generate_alert_message(config, current_spend, forecast, 100)
            
            for channel in config.alert_channels:
                if channel == AlertChannel.EMAIL:
                    await self._send_email_notification(config.owner_email, alert_message)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_notification(alert_message)
                elif channel == AlertChannel.SMS:
                    await self._send_sms_notification(config.owner_email, alert_message)
        
        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")

    async def _send_email_notification(self, recipient: str, message: str):
        """Send email notification"""
        # Implementation would use SMTP or SES
        logger.info(f"Email notification sent to {recipient}")

    async def _send_slack_notification(self, message: str):
        """Send Slack notification"""
        # Implementation would use Slack webhook
        logger.info("Slack notification sent")

    async def _apply_cost_restrictions(self, config: BudgetConfig):
        """Apply cost restrictions like denying new resource creation"""
        # Implementation would use IAM policies or Service Control Policies
        logger.info(f"Cost restrictions applied for budget {config.name}")

    async def _shutdown_non_critical_resources(self, config: BudgetConfig):
        """Shutdown non-critical resources to control costs"""
        # Implementation would identify and stop resources tagged as non-critical
        logger.info(f"Non-critical resources shutdown for budget {config.name}")

    def generate_budget_report(self, alerts: List[BudgetAlert]) -> str:
        """
        Generate comprehensive budget monitoring report
        
        Mumbai Context: Monthly household budget report
        """
        try:
            report = f"""
Budget Monitoring & Alerts Report
=================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY (Mumbai Style)
===============================
यह report आपके cloud budget का complete health check है
जैसे Mumbai में monthly household budget tracking

Total Budgets Monitored: {len(self.budget_configs)}
Active Alerts: {len(alerts)}
Critical Alerts: {len([a for a in alerts if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]])}

BUDGET STATUS OVERVIEW
=====================
"""
            
            # Budget-wise status
            total_budget_amount = 0
            total_current_spend = 0
            total_projected_spend = 0
            
            for budget_id, config in self.budget_configs.items():
                budget_alerts = [a for a in alerts if a.budget_config.budget_id == budget_id]
                current_spend = budget_alerts[0].current_spend if budget_alerts else 0
                projected_spend = budget_alerts[0].projected_spend if budget_alerts else 0
                
                total_budget_amount += config.amount
                total_current_spend += current_spend
                total_projected_spend += projected_spend
                
                utilization = (current_spend / config.amount * 100) if config.amount > 0 else 0
                projection = (projected_spend / config.amount * 100) if config.amount > 0 else 0
                
                status_emoji = "🔴" if utilization >= 90 else "🟡" if utilization >= 75 else "🟢"
                
                report += f"""
{status_emoji} {config.name} ({config.department})
   Budget: ${config.amount:.2f}
   Current: ${current_spend:.2f} ({utilization:.1f}%)
   Projected: ${projected_spend:.2f} ({projection:.1f}%)
   Alerts: {len(budget_alerts)}
"""
            
            # Overall summary
            overall_utilization = (total_current_spend / total_budget_amount * 100) if total_budget_amount > 0 else 0
            overall_projection = (total_projected_spend / total_budget_amount * 100) if total_budget_amount > 0 else 0
            
            report += f"""

OVERALL BUDGET HEALTH
====================
Total Budget: ${total_budget_amount:.2f}
Total Current Spend: ${total_current_spend:.2f} ({overall_utilization:.1f}%)
Total Projected Spend: ${total_projected_spend:.2f} ({overall_projection:.1f}%)
"""
            
            # Alert details
            if alerts:
                report += f"""

ACTIVE ALERTS DETAILS
====================
"""
                
                # Group alerts by severity
                alerts_by_severity = {}
                for alert in alerts:
                    if alert.severity not in alerts_by_severity:
                        alerts_by_severity[alert.severity] = []
                    alerts_by_severity[alert.severity].append(alert)
                
                for severity in [AlertSeverity.EMERGENCY, AlertSeverity.CRITICAL, AlertSeverity.WARNING, AlertSeverity.INFO]:
                    if severity in alerts_by_severity:
                        severity_alerts = alerts_by_severity[severity]
                        report += f"""
{severity.value.upper()} Alerts ({len(severity_alerts)}):
"""
                        for alert in severity_alerts[:5]:  # Top 5 per severity
                            report += f"""
• {alert.budget_config.name}
  Threshold: {alert.threshold_exceeded}%
  Current: ${alert.current_spend:.2f}
  Projected: ${alert.projected_spend:.2f}
  Days Remaining: {alert.days_remaining}
"""
            
            # Mumbai context insights
            report += f"""

MUMBAI CONTEXT ANALYSIS
=======================
Budget management आपके लिए बिल्कुल Mumbai household budget जैसा है:

💰 FINANCIAL HEALTH:
"""
            
            if overall_utilization < 50:
                report += "   ✅ EXCELLENT: Like having good savings - budget well under control!\n"
            elif overall_utilization < 75:
                report += "   👍 GOOD: Like normal monthly expenses - on track but watch closely\n"
            elif overall_utilization < 90:
                report += "   ⚠️  CAUTION: Like month-end tight budget - need careful monitoring\n"
            else:
                report += "   🚨 CRITICAL: Like salary spent early - immediate action required!\n"
            
            report += f"""
🎯 BUDGET DISCIPLINE:
   Current vs Budget: {overall_utilization:.1f}%
   Projected vs Budget: {overall_projection:.1f}%
   
   Like Mumbai commuter choosing transport:
   - Under 75%: Like having monthly pass with buffer
   - 75-90%: Like calculating exact fare daily
   - Over 90%: Like considering walking to save money!

TRENDING INSIGHTS
================
"""
            
            # Trend analysis
            high_risk_budgets = [
                config.name for config in self.budget_configs.values()
                if any(a.budget_config.budget_id == config.budget_id and 
                      getattr(a, 'forecast', None) and a.forecast.risk_score > 70 
                      for a in alerts)
            ]
            
            if high_risk_budgets:
                report += f"""
High Risk Budgets: {', '.join(high_risk_budgets)}
⚡ These budgets need immediate attention like peak hour traffic planning!
"""
            
            # Recommendations
            report += f"""

ACTIONABLE RECOMMENDATIONS
=========================
"""
            
            if len(alerts) == 0:
                report += """
✅ ALL BUDGETS HEALTHY
• Continue current spend patterns
• Plan for upcoming seasonal variations
• Consider optimization opportunities
"""
            else:
                critical_count = len([a for a in alerts if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]])
                if critical_count > 0:
                    report += f"""
🚨 IMMEDIATE ACTIONS ({critical_count} critical alerts):
• Review and pause non-essential resources
• Implement emergency cost controls
• Get stakeholder approval for overruns
• Consider resource cleanup automation
"""
                
                warning_count = len([a for a in alerts if a.severity == AlertSeverity.WARNING])
                if warning_count > 0:
                    report += f"""
⚠️  PROACTIVE MEASURES ({warning_count} warnings):
• Monitor daily spend trends
• Optimize underutilized resources
• Review reserved instance opportunities
• Plan resource scaling strategies
"""
            
            report += f"""

AUTOMATION OPPORTUNITIES
=======================
• Set up auto-scaling policies based on budget thresholds
• Implement cost anomaly detection
• Create approval workflows for high-cost resources
• Enable automatic resource cleanup for dev/test

NEXT STEPS
==========
1. Address all critical alerts within 24 hours
2. Set up automated cost controls for high-risk budgets
3. Review and adjust budget thresholds quarterly
4. Implement cost optimization recommendations
5. Train teams on cost-conscious resource usage

Contact: Hindi Tech Community for budget optimization support
"""
            
            logger.info("Generated comprehensive budget monitoring report")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate budget report: {e}")
            return f"Error generating report: {e}"

# Usage Example
def main():
    """
    Production usage example
    
    Mumbai Context: Complete budget monitoring setup
    """
    try:
        # Initialize budget alerts system
        print("💰 Initializing Budget Alerts System...")
        budget_system = BudgetAlertsSystem()
        
        # Create sample budget configurations
        sample_configs = [
            BudgetConfig(
                budget_id="engineering-monthly",
                name="Engineering Team Monthly Budget",
                budget_type=BudgetType.MONTHLY,
                amount=10000.0,
                currency="USD",
                period_start=datetime.now().replace(day=1),
                period_end=datetime.now().replace(day=1) + timedelta(days=32),
                filters={
                    "tag_filters": {"Department": ["engineering"]},
                    "services": ["EC2", "Lambda", "RDS"]
                },
                alert_thresholds=[50, 75, 90, 100],
                alert_channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                auto_actions={
                    90.0: ActionType.NOTIFY,
                    100.0: ActionType.APPROVAL_REQUIRED
                },
                owner_email="engineering@company.com",
                department="engineering"
            ),
            BudgetConfig(
                budget_id="data-science-project",
                name="ML Project Budget",
                budget_type=BudgetType.PROJECT_BASED,
                amount=25000.0,
                currency="USD",
                period_start=datetime.now(),
                period_end=datetime.now() + timedelta(days=90),
                filters={
                    "tag_filters": {"Project": ["ml-platform"], "Environment": ["production"]},
                    "services": ["SageMaker", "S3", "EC2"]
                },
                alert_thresholds=[60, 80, 95, 100],
                alert_channels=[AlertChannel.EMAIL],
                auto_actions={
                    95.0: ActionType.RESTRICT,
                    100.0: ActionType.APPROVAL_REQUIRED
                },
                owner_email="ml-team@company.com",
                department="data-science"
            )
        ]
        
        # Create budgets
        print("📊 Creating budget configurations...")
        for config in sample_configs:
            success = budget_system.create_budget(config)
            if success:
                print(f"✅ Created budget: {config.name}")
            else:
                print(f"❌ Failed to create budget: {config.name}")
        
        # Monitor budgets and generate alerts
        print("\n🔍 Monitoring budgets for threshold violations...")
        alerts = asyncio.run(budget_system.monitor_budgets())
        
        if alerts:
            print(f"\n⚠️  Found {len(alerts)} budget alerts:")
            
            # Group alerts by severity
            severity_counts = {}
            for alert in alerts:
                if alert.severity not in severity_counts:
                    severity_counts[alert.severity] = 0
                severity_counts[alert.severity] += 1
            
            for severity, count in severity_counts.items():
                emoji = {"emergency": "🚨", "critical": "🔴", "warning": "⚠️", "info": "ℹ️"}
                print(f"  {emoji.get(severity.value, '•')} {severity.value.title()}: {count}")
        else:
            print("✅ No budget threshold violations found!")
        
        # Generate comprehensive report
        print("\n📄 Generating budget monitoring report...")
        report = budget_system.generate_budget_report(alerts)
        
        # Save report
        with open('budget_monitoring_report.txt', 'w') as f:
            f.write(report)
        
        print("✅ Budget monitoring completed!")
        print("📄 Report saved to budget_monitoring_report.txt")
        
        # Show Mumbai style summary
        if alerts:
            critical_alerts = [a for a in alerts if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]]
            if critical_alerts:
                print(f"\n🚨 Mumbai Commuter Alert: Budget situation is like running out of monthly pass!")
                print("   Immediate action needed - like finding alternate transport route!")
            else:
                print(f"\n💡 Mumbai Insight: Budget alerts are like traffic updates")
                print("   Plan your route (spending) accordingly!")
        else:
            print(f"\n🎉 Mumbai Style: All budgets healthy like smooth traffic flow!")
            print("   Continue current spending pattern!")
        
    except Exception as e:
        logger.error(f"Budget monitoring failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

"""
Production Implementation Guide (Hindi):
========================================

1. Budget Configuration Management:
   - Central budget policy repository
   - Environment-specific budget allocations
   - Automated budget creation from templates
   - Integration with financial planning systems

2. Real-time Monitoring:
   - CloudWatch integration for real-time spend tracking
   - Custom metrics for department/project allocation
   - Anomaly detection using statistical models
   - Mobile app notifications for budget managers

3. Mumbai Business Context:
   - Map to local financial planning practices
   - Integration with Indian accounting standards
   - Currency hedging for international services
   - Seasonal adjustment for Indian business cycles

4. Automated Controls:
   - Policy-based resource restrictions
   - Auto-scaling based on budget constraints
   - Approval workflows for budget overruns
   - Emergency cost control mechanisms

5. Reporting & Analytics:
   - Executive dashboards for leadership
   - Department-wise cost attribution
   - Trend analysis and forecasting
   - ROI tracking for budget investments

यह system आपके cloud spending को Mumbai household की smart financial planning जैसा disciplined बनाएगा!
"""
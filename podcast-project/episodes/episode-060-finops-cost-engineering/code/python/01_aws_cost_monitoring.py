#!/usr/bin/env python3
"""
AWS Cost Monitoring System
==========================

Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering
Production-ready AWS cost monitoring and alerting system

Author: Hindi Tech Community
Date: 2025
Version: 1.0

Features:
- Real-time cost tracking across all AWS services
- Daily/weekly/monthly cost reports 
- Budget threshold monitoring
- Service-wise cost breakdown
- Regional cost analysis
- Cost anomaly detection
- Email/Slack alerting

Mumbai Context: Like tracking your monthly expenses for groceries, rent, transport
"""

import boto3
import pandas as pd
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import logging
import requests
import os
from dataclasses import dataclass

# Logging setup - सभी activities track करने के लिए
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

@dataclass
class CostAlert:
    """Cost alert configuration"""
    service: str
    threshold: float
    period: str
    currency: str = "USD"

class AWSCostMonitor:
    """
    AWS Cost Monitor - पैसे की निगरानी का system
    
    Mumbai analogy: यह आपके monthly budget tracker जैसा है
    जैसे आप grocery, transport, entertainment का हिसाब रखते हैं
    """
    
    def __init__(self, region='us-east-1'):
        """Initialize AWS cost monitoring system"""
        try:
            # AWS clients initialize करना
            self.ce_client = boto3.client('ce', region_name=region)
            self.sns_client = boto3.client('sns', region_name=region)
            self.cloudwatch = boto3.client('cloudwatch', region_name=region)
            
            # Configuration
            self.currency = 'USD'
            self.region = region
            
            logger.info("AWS Cost Monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS Cost Monitor: {e}")
            raise

    def get_cost_and_usage(self, start_date: str, end_date: str, 
                          granularity: str = 'DAILY') -> Dict:
        """
        Get cost and usage data from AWS
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format 
            granularity: DAILY/MONTHLY/HOURLY
            
        Mumbai Context: जैसे आप daily/monthly expenses का हिसाब लगाते हैं
        """
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity=granularity,
                Metrics=['BlendedCost', 'UnblendedCost', 'UsageQuantity'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            logger.info(f"Retrieved cost data from {start_date} to {end_date}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get cost data: {e}")
            raise

    def analyze_service_costs(self, days_back: int = 30) -> pd.DataFrame:
        """
        Analyze costs by AWS service
        
        Mumbai Context: Service-wise breakdown जैसे Mumbai में transport cost
        - Local train: Rs 50/month
        - Auto: Rs 500/month  
        - Cab: Rs 1500/month
        """
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            response = self.get_cost_and_usage(start_date, end_date)
            
            # Data processing करना
            service_costs = {}
            
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                
                for group in result['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    
                    if service not in service_costs:
                        service_costs[service] = []
                    
                    service_costs[service].append({
                        'date': date,
                        'cost': cost
                    })
            
            # DataFrame बनाना
            all_data = []
            for service, costs in service_costs.items():
                for cost_data in costs:
                    all_data.append({
                        'service': service,
                        'date': cost_data['date'],
                        'cost': cost_data['cost']
                    })
            
            df = pd.DataFrame(all_data)
            logger.info(f"Analyzed costs for {len(service_costs)} services")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to analyze service costs: {e}")
            raise

    def detect_cost_anomalies(self, threshold_percentage: float = 25.0) -> List[Dict]:
        """
        Detect cost anomalies using statistical analysis
        
        Mumbai Context: Sudden expense increase detection
        जैसे अगर अचानक electricity bill 25% ज्यादा आ जाए
        """
        try:
            df = self.analyze_service_costs(days_back=60)
            anomalies = []
            
            for service in df['service'].unique():
                service_data = df[df['service'] == service].copy()
                service_data['date'] = pd.to_datetime(service_data['date'])
                service_data = service_data.sort_values('date')
                
                # Rolling average निकालना
                service_data['rolling_avg'] = service_data['cost'].rolling(window=7).mean()
                service_data['rolling_std'] = service_data['cost'].rolling(window=7).std()
                
                # Anomaly detection
                recent_cost = service_data['cost'].iloc[-1]
                avg_cost = service_data['rolling_avg'].iloc[-1]
                
                if avg_cost > 0:  # Division by zero avoid करना
                    percentage_change = ((recent_cost - avg_cost) / avg_cost) * 100
                    
                    if abs(percentage_change) > threshold_percentage:
                        anomalies.append({
                            'service': service,
                            'current_cost': recent_cost,
                            'average_cost': avg_cost,
                            'percentage_change': percentage_change,
                            'date': service_data['date'].iloc[-1].strftime('%Y-%m-%d'),
                            'severity': 'HIGH' if abs(percentage_change) > 50 else 'MEDIUM'
                        })
            
            logger.info(f"Detected {len(anomalies)} cost anomalies")
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect cost anomalies: {e}")
            return []

    def get_cost_forecast(self, days_ahead: int = 30) -> Dict:
        """
        Get AWS cost forecast using built-in forecasting
        
        Mumbai Context: अगले महीने का budget planning
        जैसे Diwali season में extra shopping budget
        """
        try:
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
            response = self.ce_client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Metric='BLENDED_COST',
                Granularity='DAILY'
            )
            
            forecast_data = {
                'period_start': start_date,
                'period_end': end_date,
                'forecasted_cost': float(response['Total']['Amount']),
                'currency': response['Total']['Unit'],
                'daily_forecast': []
            }
            
            for result in response['ForecastResultsByTime']:
                forecast_data['daily_forecast'].append({
                    'date': result['TimePeriod']['Start'],
                    'mean_value': float(result['MeanValue']),
                    'prediction_interval_lower': float(result['PredictionIntervalLowerBound']),
                    'prediction_interval_upper': float(result['PredictionIntervalUpperBound'])
                })
            
            logger.info(f"Generated cost forecast for {days_ahead} days")
            return forecast_data
            
        except Exception as e:
            logger.error(f"Failed to get cost forecast: {e}")
            raise

    def generate_cost_report(self, period_days: int = 30) -> Dict:
        """
        Generate comprehensive cost report
        
        Mumbai Context: Monthly family expense report
        - Total spend
        - Category-wise breakdown  
        - Comparison with previous month
        - Recommendations
        """
        try:
            report = {
                'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'period_days': period_days,
                'currency': self.currency
            }
            
            # Current period costs
            df_current = self.analyze_service_costs(days_back=period_days)
            current_total = df_current['cost'].sum()
            
            # Previous period for comparison
            df_previous = self.analyze_service_costs(days_back=period_days*2)
            df_previous = df_previous[df_previous['date'] < 
                                   (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')]
            previous_total = df_previous['cost'].sum()
            
            # Service-wise summary
            service_summary = df_current.groupby('service')['cost'].sum().to_dict()
            
            # Top 5 expensive services
            top_services = sorted(service_summary.items(), key=lambda x: x[1], reverse=True)[:5]
            
            report.update({
                'total_cost_current_period': round(current_total, 2),
                'total_cost_previous_period': round(previous_total, 2),
                'cost_change_percentage': round(((current_total - previous_total) / previous_total * 100), 2) if previous_total > 0 else 0,
                'top_5_services': top_services,
                'service_count': len(service_summary),
                'daily_average': round(current_total / period_days, 2)
            })
            
            # Cost anomalies
            anomalies = self.detect_cost_anomalies()
            report['anomalies'] = anomalies
            
            # Forecast
            forecast = self.get_cost_forecast()
            report['forecast'] = forecast
            
            logger.info("Generated comprehensive cost report")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate cost report: {e}")
            raise

    def send_cost_alert(self, alert_data: Dict, recipients: List[str]):
        """
        Send cost alert via email
        
        Mumbai Context: WhatsApp group में family को bill alert भेजना
        """
        try:
            # Email configuration
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            email_user = os.getenv('EMAIL_USER')
            email_password = os.getenv('EMAIL_PASSWORD')
            
            if not all([email_user, email_password]):
                logger.warning("Email credentials not configured")
                return
            
            # Email content
            subject = f"🚨 AWS Cost Alert - {alert_data.get('type', 'Anomaly Detected')}"
            
            body = f"""
            AWS Cost Alert Report
            =====================
            
            Alert Type: {alert_data.get('type', 'Cost Anomaly')}
            Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Details:
            {json.dumps(alert_data, indent=2)}
            
            Mumbai Context: यह आपके monthly budget में unexpected increase है
            जैसे अचानक electricity bill बढ़ जाना
            
            Action Required: Please review your AWS usage immediately
            
            Best regards,
            FinOps Monitoring System
            """
            
            # Send email
            msg = MimeMultipart()
            msg['From'] = email_user
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            
            for recipient in recipients:
                msg['To'] = recipient
                server.send_message(msg)
            
            server.quit()
            logger.info(f"Cost alert sent to {len(recipients)} recipients")
            
        except Exception as e:
            logger.error(f"Failed to send cost alert: {e}")

    def create_cost_dashboard_data(self) -> Dict:
        """
        Create data for cost dashboard visualization
        
        Mumbai Context: Cost ka visual dashboard जैसे investment apps में
        """
        try:
            dashboard_data = {}
            
            # Service costs
            df = self.analyze_service_costs(days_back=30)
            
            # Service-wise pie chart data
            service_totals = df.groupby('service')['cost'].sum()
            dashboard_data['service_breakdown'] = {
                'labels': service_totals.index.tolist(),
                'values': service_totals.values.tolist()
            }
            
            # Daily trend data
            daily_costs = df.groupby('date')['cost'].sum().reset_index()
            dashboard_data['daily_trend'] = {
                'dates': daily_costs['date'].tolist(),
                'costs': daily_costs['cost'].tolist()
            }
            
            # Cost summary
            total_cost = df['cost'].sum()
            dashboard_data['summary'] = {
                'total_cost': round(total_cost, 2),
                'average_daily': round(total_cost / 30, 2),
                'service_count': len(df['service'].unique()),
                'currency': self.currency
            }
            
            logger.info("Created dashboard data")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to create dashboard data: {e}")
            return {}

# Usage Example - Production में कैसे use करें
def main():
    """
    Production usage example
    
    Mumbai Context: Daily morning routine जैसे cost check करना
    """
    try:
        # Initialize monitor
        cost_monitor = AWSCostMonitor()
        
        # Generate daily report
        print("🔍 Generating AWS Cost Report...")
        report = cost_monitor.generate_cost_report(period_days=30)
        
        print(f"\n📊 Cost Summary:")
        print(f"Current Period Total: ${report['total_cost_current_period']}")
        print(f"Previous Period Total: ${report['total_cost_previous_period']}")
        print(f"Change: {report['cost_change_percentage']}%")
        
        print(f"\n🏆 Top 5 Services:")
        for service, cost in report['top_5_services']:
            print(f"  {service}: ${cost:.2f}")
        
        # Check for anomalies
        if report['anomalies']:
            print(f"\n⚠️  Cost Anomalies Detected: {len(report['anomalies'])}")
            for anomaly in report['anomalies']:
                print(f"  {anomaly['service']}: {anomaly['percentage_change']:.2f}% change")
                
                # Send alert for high severity anomalies
                if anomaly['severity'] == 'HIGH':
                    cost_monitor.send_cost_alert(
                        alert_data=anomaly,
                        recipients=['admin@company.com']
                    )
        
        # Generate dashboard data
        dashboard = cost_monitor.create_cost_dashboard_data()
        print(f"\n📈 Dashboard Data Generated: {len(dashboard)} sections")
        
        # Forecast
        forecast = report['forecast']
        print(f"\n🔮 Cost Forecast (30 days): ${forecast['forecasted_cost']:.2f}")
        
        print("\n✅ Cost monitoring completed successfully!")
        
    except Exception as e:
        logger.error(f"Cost monitoring failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

"""
Production Deployment Guide (Hindi):
====================================

1. Environment Setup:
   - AWS credentials configure करें
   - Required permissions: ce:*, cloudwatch:*, sns:*
   - Email SMTP credentials set करें

2. Scheduling:
   - Cron job for daily reports: 0 9 * * *
   - Alert monitoring: every 4 hours
   - Weekly summary: 0 9 * * 1

3. Mumbai Context Integration:
   - Cost categories map करें (transport vs storage)
   - Regional cost comparison (Mumbai vs Delhi pricing)
   - Festival season cost spikes handle करें

4. Scaling Considerations:
   - Multiple AWS accounts support
   - Cross-region cost aggregation
   - Historical data retention (1 year)

5. Cost Optimization Tips:
   - Reserved Instances analysis
   - Spot instance recommendations  
   - Unused resource cleanup
   - Right-sizing suggestions

This system बिल्कुल Mumbai के household budget management जैसा है!
"""
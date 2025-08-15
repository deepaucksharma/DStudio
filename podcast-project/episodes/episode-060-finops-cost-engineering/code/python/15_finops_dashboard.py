#!/usr/bin/env python3
"""
FinOps Dashboard - Comprehensive Cost Management
===============================================

Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering
Real-time FinOps dashboard with multi-cloud cost visualization

Author: Hindi Tech Community
Date: 2025
Version: 1.0

Features:
- Real-time cost monitoring
- Multi-cloud cost aggregation
- Interactive visualizations
- Cost trend analysis
- Budget vs actual tracking
- Anomaly detection alerts
- Cost optimization recommendations

Mumbai Context: FinOps dashboard जैसे Mumbai household budget tracker app
- Daily expense tracking with categories
- Monthly budget vs actual comparison
- Smart recommendations for cost saving
- Real-time alerts for overspending
"""

import asyncio
import boto3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from datetime import date
import warnings
warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DashboardMetrics:
    """Dashboard metrics data"""
    total_monthly_cost: float
    budget_utilization: float
    month_over_month_change: float
    cost_per_service: Dict[str, float]
    top_cost_drivers: List[Dict[str, Any]]
    optimization_opportunities: float
    anomaly_count: int
    forecast_next_month: float

class FinOpsDashboard:
    """
    Comprehensive FinOps Dashboard
    
    Mumbai Context: यह complete household budget management app जैसा है
    - Real-time expense tracking
    - Category-wise spending analysis
    - Monthly budget monitoring
    - Smart cost-saving recommendations
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize FinOps Dashboard"""
        try:
            self.region = region
            
            # AWS clients
            self.ce_client = boto3.client('ce', region_name=region)
            self.cloudwatch = boto3.client('cloudwatch', region_name=region)
            self.budgets_client = boto3.client('budgets', region_name=region)
            
            # Dashboard configuration
            self.account_id = boto3.client('sts').get_caller_identity()['Account']
            self.currency = 'USD'
            
            # Color scheme for Mumbai theme
            self.colors = {
                'primary': '#FF6B35',      # Mumbai sunset orange
                'secondary': '#004B87',    # Mumbai local train blue
                'success': '#2ECC71',      # Success green
                'warning': '#F39C12',      # Warning amber
                'danger': '#E74C3C',       # Danger red
                'info': '#3498DB'          # Info blue
            }
            
            logger.info("FinOps Dashboard initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize FinOps Dashboard: {e}")
            raise

    async def collect_dashboard_metrics(self) -> DashboardMetrics:
        """
        Collect all metrics for dashboard
        
        Mumbai Context: सभी financial data को एक जगह collect करना
        जैसे monthly expenses का complete summary
        """
        try:
            # Get current month cost
            current_month_cost = await self._get_current_month_cost()
            
            # Get previous month for comparison
            previous_month_cost = await self._get_previous_month_cost()
            
            # Calculate month-over-month change
            mom_change = ((current_month_cost - previous_month_cost) / previous_month_cost * 100) if previous_month_cost > 0 else 0
            
            # Get service-wise costs
            service_costs = await self._get_service_wise_costs()
            
            # Get top cost drivers
            top_drivers = await self._get_top_cost_drivers()
            
            # Get budget information
            budget_utilization = await self._get_budget_utilization()
            
            # Calculate optimization opportunities
            optimization_opportunities = await self._calculate_optimization_opportunities()
            
            # Get anomaly count
            anomaly_count = await self._get_anomaly_count()
            
            # Forecast next month
            forecast = await self._forecast_next_month_cost(current_month_cost, mom_change)
            
            metrics = DashboardMetrics(
                total_monthly_cost=current_month_cost,
                budget_utilization=budget_utilization,
                month_over_month_change=mom_change,
                cost_per_service=service_costs,
                top_cost_drivers=top_drivers,
                optimization_opportunities=optimization_opportunities,
                anomaly_count=anomaly_count,
                forecast_next_month=forecast
            )
            
            logger.info("Dashboard metrics collected successfully")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect dashboard metrics: {e}")
            # Return default metrics
            return DashboardMetrics(
                total_monthly_cost=0.0,
                budget_utilization=0.0,
                month_over_month_change=0.0,
                cost_per_service={},
                top_cost_drivers=[],
                optimization_opportunities=0.0,
                anomaly_count=0,
                forecast_next_month=0.0
            )

    async def _get_current_month_cost(self) -> float:
        """Get current month total cost"""
        try:
            now = datetime.now()
            start_date = now.replace(day=1).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='MONTHLY',
                Metrics=['BlendedCost']
            )
            
            if response['ResultsByTime']:
                return float(response['ResultsByTime'][0]['Total']['BlendedCost']['Amount'])
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to get current month cost: {e}")
            return 0.0

    async def _get_previous_month_cost(self) -> float:
        """Get previous month total cost"""
        try:
            now = datetime.now()
            # Previous month start and end
            first_day_current = now.replace(day=1)
            last_day_previous = first_day_current - timedelta(days=1)
            first_day_previous = last_day_previous.replace(day=1)
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': first_day_previous.strftime('%Y-%m-%d'),
                    'End': first_day_current.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost']
            )
            
            if response['ResultsByTime']:
                return float(response['ResultsByTime'][0]['Total']['BlendedCost']['Amount'])
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to get previous month cost: {e}")
            return 0.0

    async def _get_service_wise_costs(self) -> Dict[str, float]:
        """Get cost breakdown by AWS service"""
        try:
            now = datetime.now()
            start_date = now.replace(day=1).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            
            service_costs = {}
            if response['ResultsByTime']:
                for group in response['ResultsByTime'][0]['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    if cost > 0:
                        service_costs[service] = cost
            
            return service_costs
            
        except Exception as e:
            logger.error(f"Failed to get service-wise costs: {e}")
            return {}

    async def _get_top_cost_drivers(self) -> List[Dict[str, Any]]:
        """Get top cost drivers with details"""
        service_costs = await self._get_service_wise_costs()
        
        top_drivers = []
        for service, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5]:
            driver = {
                'service': service,
                'cost': cost,
                'percentage': 0.0,  # Will be calculated
                'trend': 'stable'   # Simplified
            }
            top_drivers.append(driver)
        
        # Calculate percentages
        total_cost = sum(service_costs.values())
        for driver in top_drivers:
            driver['percentage'] = (driver['cost'] / total_cost * 100) if total_cost > 0 else 0
        
        return top_drivers

    async def _get_budget_utilization(self) -> float:
        """Get budget utilization percentage"""
        try:
            # This would integrate with AWS Budgets API
            # For demo, return simulated value
            return 75.5
        except Exception as e:
            logger.error(f"Failed to get budget utilization: {e}")
            return 0.0

    async def _calculate_optimization_opportunities(self) -> float:
        """Calculate potential cost optimization opportunities"""
        try:
            # Simplified calculation based on common optimization patterns
            current_cost = await self._get_current_month_cost()
            
            # Estimate 15-25% optimization potential (typical for unoptimized infrastructure)
            optimization_potential = current_cost * 0.20  # 20% average
            
            return optimization_potential
            
        except Exception as e:
            logger.error(f"Failed to calculate optimization opportunities: {e}")
            return 0.0

    async def _get_anomaly_count(self) -> int:
        """Get count of cost anomalies detected"""
        try:
            # This would integrate with anomaly detection system
            # For demo, return simulated value
            return 3
        except Exception as e:
            logger.error(f"Failed to get anomaly count: {e}")
            return 0

    async def _forecast_next_month_cost(self, current_cost: float, mom_change: float) -> float:
        """Forecast next month cost based on trends"""
        try:
            # Simple linear projection
            growth_factor = 1 + (mom_change / 100)
            forecast = current_cost * growth_factor
            
            # Add some randomness for realistic forecasting
            import random
            variance = random.uniform(0.95, 1.05)
            forecast *= variance
            
            return forecast
            
        except Exception as e:
            logger.error(f"Failed to forecast next month cost: {e}")
            return current_cost

    def create_cost_trend_chart(self, historical_data: List[Dict]) -> go.Figure:
        """
        Create cost trend visualization
        
        Mumbai Context: Monthly expense trend जैसे chart
        """
        try:
            if not historical_data:
                # Create sample data for demo
                dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
                costs = np.random.uniform(8000, 12000, len(dates))
                historical_data = [{'date': date.strftime('%Y-%m'), 'cost': cost} for date, cost in zip(dates, costs)]
            
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            
            fig = go.Figure()
            
            # Add cost trend line
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['cost'],
                mode='lines+markers',
                name='Monthly Cost',
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=8)
            ))
            
            # Add trend line
            z = np.polyfit(range(len(df)), df['cost'], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=p(range(len(df))),
                mode='lines',
                name='Trend',
                line=dict(color=self.colors['secondary'], width=2, dash='dash')
            ))
            
            fig.update_layout(
                title={
                    'text': '💰 Monthly Cost Trend (Mumbai Style)',
                    'x': 0.5,
                    'font': {'size': 20, 'color': self.colors['primary']}
                },
                xaxis_title='Month',
                yaxis_title='Cost (USD)',
                template='plotly_white',
                height=400,
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create cost trend chart: {e}")
            return go.Figure()

    def create_service_breakdown_chart(self, service_costs: Dict[str, float]) -> go.Figure:
        """
        Create service cost breakdown pie chart
        
        Mumbai Context: Expense categories जैसे pie chart
        """
        try:
            if not service_costs:
                # Demo data
                service_costs = {
                    'EC2': 3500, 'RDS': 1200, 'S3': 800, 
                    'Lambda': 400, 'CloudFront': 300, 'Others': 800
                }
            
            # Prepare data
            services = list(service_costs.keys())
            costs = list(service_costs.values())
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=services,
                values=costs,
                hole=0.4,
                marker_colors=px.colors.qualitative.Set3
            )])
            
            fig.update_layout(
                title={
                    'text': '🎯 Service-wise Cost Breakdown',
                    'x': 0.5,
                    'font': {'size': 18, 'color': self.colors['primary']}
                },
                height=400,
                showlegend=True,
                annotations=[dict(text='Total<br>Services', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create service breakdown chart: {e}")
            return go.Figure()

    def create_budget_gauge(self, budget_utilization: float) -> go.Figure:
        """
        Create budget utilization gauge
        
        Mumbai Context: Budget meter जैसे speedometer
        """
        try:
            # Determine color based on utilization
            if budget_utilization <= 70:
                color = 'green'
            elif budget_utilization <= 90:
                color = 'yellow'
            else:
                color = 'red'
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = budget_utilization,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "🎯 Budget Utilization", 'font': {'size': 18}},
                delta = {'reference': 80, 'increasing': {'color': "red"}},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 70], 'color': "lightgreen"},
                        {'range': [70, 90], 'color': "yellow"},
                        {'range': [90, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=300)
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create budget gauge: {e}")
            return go.Figure()

    def render_streamlit_dashboard(self, metrics: DashboardMetrics):
        """
        Render complete Streamlit dashboard
        
        Mumbai Context: Complete dashboard जैसे smart home app
        """
        try:
            # Page configuration
            st.set_page_config(
                page_title="FinOps Dashboard - Mumbai Style",
                page_icon="💰",
                layout="wide",
                initial_sidebar_state="expanded"
            )
            
            # Custom CSS for Mumbai theme
            st.markdown("""
            <style>
            .main-header {
                font-size: 3rem;
                color: #FF6B35;
                text-align: center;
                margin-bottom: 2rem;
            }
            .metric-card {
                background: linear-gradient(90deg, #FF6B35, #004B87);
                color: white;
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem 0;
            }
            .mumbai-insight {
                background: #f0f8ff;
                border-left: 5px solid #FF6B35;
                padding: 1rem;
                margin: 1rem 0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Main header
            st.markdown('<h1 class="main-header">💰 FinOps Dashboard - Mumbai Style</h1>', unsafe_allow_html=True)
            st.markdown("**यह आपके cloud costs का complete real-time analysis है - जैसे Mumbai household budget tracker!**")
            
            # Sidebar
            with st.sidebar:
                st.image("https://via.placeholder.com/300x100/FF6B35/FFFFFF?text=FinOps+Dashboard", width=300)
                st.markdown("## 📊 Dashboard Controls")
                
                # Date range selector
                start_date = st.date_input("Start Date", value=date(2024, 1, 1))
                end_date = st.date_input("End Date", value=date.today())
                
                # Refresh button
                if st.button("🔄 Refresh Data"):
                    st.experimental_rerun()
                
                # Quick insights
                st.markdown("## 🎯 Quick Insights")
                st.info(f"💰 Monthly Spend: ${metrics.total_monthly_cost:.2f}")
                st.info(f"📈 Month-over-Month: {metrics.month_over_month_change:.1f}%")
                st.info(f"⚠️ Anomalies: {metrics.anomaly_count}")
            
            # Main dashboard content
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="💰 Monthly Cost",
                    value=f"${metrics.total_monthly_cost:.2f}",
                    delta=f"{metrics.month_over_month_change:.1f}%"
                )
            
            with col2:
                st.metric(
                    label="🎯 Budget Used",
                    value=f"{metrics.budget_utilization:.1f}%",
                    delta="Safe" if metrics.budget_utilization < 80 else "Caution"
                )
            
            with col3:
                st.metric(
                    label="💡 Savings Potential",
                    value=f"${metrics.optimization_opportunities:.2f}",
                    delta="Opportunities"
                )
            
            with col4:
                st.metric(
                    label="🔮 Next Month Forecast",
                    value=f"${metrics.forecast_next_month:.2f}",
                    delta="Predicted"
                )
            
            # Charts section
            st.markdown("## 📈 Cost Analysis Charts")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Cost trend chart
                trend_chart = self.create_cost_trend_chart([])
                st.plotly_chart(trend_chart, use_container_width=True)
            
            with col2:
                # Service breakdown chart
                breakdown_chart = self.create_service_breakdown_chart(metrics.cost_per_service)
                st.plotly_chart(breakdown_chart, use_container_width=True)
            
            # Budget gauge
            st.markdown("## 🎯 Budget Monitoring")
            budget_gauge = self.create_budget_gauge(metrics.budget_utilization)
            st.plotly_chart(budget_gauge, use_container_width=True)
            
            # Top cost drivers
            st.markdown("## 🏆 Top Cost Drivers")
            if metrics.top_cost_drivers:
                for i, driver in enumerate(metrics.top_cost_drivers, 1):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{i}. {driver['service']}**")
                    with col2:
                        st.write(f"${driver['cost']:.2f}")
                    with col3:
                        st.write(f"{driver['percentage']:.1f}%")
            
            # Mumbai Context Insights
            st.markdown("## 🏙️ Mumbai Context Insights")
            st.markdown('<div class="mumbai-insight">', unsafe_allow_html=True)
            st.markdown("""
            **आपके cloud costs का Mumbai household budget analysis:**
            
            🚄 **Transportation Budget (Compute)**: जैसे monthly train pass vs daily tickets
            🏠 **Utilities (Storage)**: जैसे electricity, water bills
            📱 **Communication (Networking)**: जैसे mobile, internet bills
            🛒 **Groceries (Databases)**: जैसे monthly grocery shopping
            
            **Smart Mumbai Financial Tips:**
            - Peak hours में extra charges (like surge pricing)
            - Monthly passes are cheaper for regular usage (Reserved Instances)
            - Share resources where possible (like shared auto vs solo)
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Action items
            st.markdown("## ✅ Recommended Actions")
            actions = [
                "🔍 Review top 3 cost drivers for optimization opportunities",
                "💳 Consider Reserved Instances for predictable workloads",
                "📊 Set up automated cost anomaly alerts",
                "🎯 Implement tag-based cost allocation",
                "📈 Schedule monthly cost optimization reviews"
            ]
            
            for action in actions:
                st.markdown(f"- {action}")
            
            # Footer
            st.markdown("---")
            st.markdown("**📞 Contact Hindi Tech Community for FinOps optimization support**")
            
        except Exception as e:
            logger.error(f"Failed to render Streamlit dashboard: {e}")
            st.error(f"Dashboard rendering failed: {e}")

# Usage Example for Streamlit
def main_streamlit():
    """Main function for Streamlit dashboard"""
    try:
        # Initialize dashboard
        dashboard = FinOpsDashboard()
        
        # Collect metrics (this would be cached in production)
        if 'metrics' not in st.session_state:
            with st.spinner('Loading dashboard metrics...'):
                st.session_state.metrics = asyncio.run(dashboard.collect_dashboard_metrics())
        
        # Render dashboard
        dashboard.render_streamlit_dashboard(st.session_state.metrics)
        
    except Exception as e:
        st.error(f"Dashboard initialization failed: {e}")

# Usage Example for standalone script
def main():
    """Production usage example"""
    try:
        print("📊 Initializing FinOps Dashboard...")
        dashboard = FinOpsDashboard()
        
        print("📈 Collecting dashboard metrics...")
        metrics = asyncio.run(dashboard.collect_dashboard_metrics())
        
        print("\n💰 FinOps Dashboard Summary:")
        print(f"Total Monthly Cost: ${metrics.total_monthly_cost:.2f}")
        print(f"Budget Utilization: {metrics.budget_utilization:.1f}%")
        print(f"Month-over-Month Change: {metrics.month_over_month_change:.1f}%")
        print(f"Optimization Opportunities: ${metrics.optimization_opportunities:.2f}")
        print(f"Cost Anomalies: {metrics.anomaly_count}")
        print(f"Next Month Forecast: ${metrics.forecast_next_month:.2f}")
        
        print("\n🏆 Top 3 Cost Drivers:")
        for i, driver in enumerate(metrics.top_cost_drivers[:3], 1):
            print(f"  {i}. {driver['service']}: ${driver['cost']:.2f} ({driver['percentage']:.1f}%)")
        
        print("\n🏙️ Mumbai Style Summary:")
        if metrics.budget_utilization > 90:
            print("🚨 Like month-end budget crisis - immediate action needed!")
        elif metrics.budget_utilization > 75:
            print("⚠️  Like mid-month budget check - monitor closely")
        else:
            print("✅ Like well-planned monthly budget - good control!")
        
        print("\n✅ FinOps dashboard analysis completed!")
        print("💡 Run with Streamlit for interactive dashboard: streamlit run finops_dashboard.py")
        
    except Exception as e:
        logger.error(f"FinOps dashboard failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check if running in Streamlit
    try:
        import streamlit as st
        main_streamlit()
    except ImportError:
        main()

"""
Production Deployment Guide (Hindi):
====================================

1. Streamlit Dashboard Deployment:
   - Deploy on AWS ECS/Fargate for scalability
   - Use Application Load Balancer for high availability
   - Implement authentication with AWS Cognito
   - Set up SSL certificates for secure access

2. Real-time Data Integration:
   - EventBridge for real-time cost event processing
   - Lambda functions for data aggregation
   - DynamoDB for caching dashboard metrics
   - CloudWatch for monitoring dashboard performance

3. Mumbai Business Context:
   - Multi-currency support (USD, INR)
   - Regional cost comparison dashboards
   - Local business hours for alerts
   - Integration with Indian financial systems

4. Advanced Features:
   - Machine learning for cost forecasting
   - Automated cost optimization recommendations
   - Integration with ITSM tools (ServiceNow, JIRA)
   - Mobile app for on-the-go monitoring

5. Monitoring & Alerting:
   - Dashboard uptime monitoring
   - Data freshness alerts
   - Performance optimization
   - User analytics and engagement tracking

यह dashboard आपके FinOps practice को Mumbai के smart financial planning जैसा intelligent बनाएगा!
"""
#!/usr/bin/env python3
"""
Database Cost Optimizer
=======================

Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering
Advanced database cost optimization with intelligent recommendations

Author: Hindi Tech Community
Date: 2025
Version: 1.0

Features:
- RDS cost optimization
- DynamoDB cost analysis
- Reserved instance recommendations
- Right-sizing analysis
- Storage optimization
- Query performance impact on costs

Mumbai Context: Database optimization जैसे Mumbai office space optimization
- Right-size करना (न ज्यादा बड़ा, न छोटा)
- Peak vs off-peak usage patterns
- Shared resources vs dedicated resources costing
"""

import asyncio
import boto3
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DatabaseCostInfo:
    """Database cost information and optimization recommendations"""
    db_identifier: str
    db_type: str  # RDS, DynamoDB, etc.
    engine: str
    instance_class: str
    storage_gb: int
    monthly_cost: float
    utilization_cpu: float
    utilization_connections: float
    optimization_potential: float
    recommended_action: str
    estimated_savings: float

class DatabaseCostOptimizer:
    """
    Database Cost Optimization System
    
    Mumbai Context: Office space optimization जैसा
    - Proper size selection based on actual usage
    - Shared vs dedicated resource costing
    - Peak time vs normal time usage patterns
    """
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.rds_client = boto3.client('rds', region_name=region)
        self.dynamodb_client = boto3.client('dynamodb', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        
        # RDS pricing (simplified)
        self.rds_pricing = {
            'db.t3.micro': 15.33, 'db.t3.small': 30.66, 'db.t3.medium': 61.32,
            'db.t3.large': 122.64, 'db.m5.large': 140.16, 'db.m5.xlarge': 280.32
        }
    
    async def analyze_rds_costs(self) -> List[DatabaseCostInfo]:
        """Analyze RDS database costs and optimization opportunities"""
        db_costs = []
        
        try:
            # Get all RDS instances
            response = self.rds_client.describe_db_instances()
            
            for db in response['DBInstances']:
                if db['DBInstanceStatus'] != 'available':
                    continue
                
                db_identifier = db['DBInstanceIdentifier']
                
                # Get utilization metrics
                cpu_util = await self._get_db_cpu_utilization(db_identifier)
                connection_util = await self._get_db_connection_utilization(db_identifier)
                
                # Calculate current cost
                instance_class = db['DBInstanceClass']
                monthly_cost = self.rds_pricing.get(instance_class, 100.0)
                
                # Storage cost
                storage_gb = db.get('AllocatedStorage', 0)
                storage_cost = storage_gb * 0.115  # $0.115 per GB-month for gp2
                monthly_cost += storage_cost
                
                # Analyze optimization potential
                optimization_analysis = self._analyze_rds_optimization(db, cpu_util, connection_util)
                
                db_cost = DatabaseCostInfo(
                    db_identifier=db_identifier,
                    db_type='RDS',
                    engine=db['Engine'],
                    instance_class=instance_class,
                    storage_gb=storage_gb,
                    monthly_cost=monthly_cost,
                    utilization_cpu=cpu_util,
                    utilization_connections=connection_util,
                    optimization_potential=optimization_analysis['potential_percentage'],
                    recommended_action=optimization_analysis['recommendation'],
                    estimated_savings=optimization_analysis['estimated_savings']
                )
                
                db_costs.append(db_cost)
            
            logger.info(f"Analyzed {len(db_costs)} RDS instances")
            return db_costs
            
        except Exception as e:
            logger.error(f"Failed to analyze RDS costs: {e}")
            return []
    
    async def _get_db_cpu_utilization(self, db_identifier: str) -> float:
        """Get average CPU utilization for RDS instance"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_identifier}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Average']
            )
            
            if response['Datapoints']:
                return sum(dp['Average'] for dp in response['Datapoints']) / len(response['Datapoints'])
            return 0.0
            
        except Exception as e:
            logger.warning(f"Failed to get CPU utilization for {db_identifier}: {e}")
            return 50.0  # Default assumption
    
    async def _get_db_connection_utilization(self, db_identifier: str) -> float:
        """Get database connection utilization"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='DatabaseConnections',
                Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_identifier}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average']
            )
            
            if response['Datapoints']:
                avg_connections = sum(dp['Average'] for dp in response['Datapoints']) / len(response['Datapoints'])
                # Assume max connections based on instance class (simplified)
                max_connections = 1000  # This would be calculated based on instance class
                return (avg_connections / max_connections) * 100
            return 0.0
            
        except Exception as e:
            logger.warning(f"Failed to get connection utilization for {db_identifier}: {e}")
            return 20.0  # Default assumption
    
    def _analyze_rds_optimization(self, db_instance: dict, cpu_util: float, connection_util: float) -> dict:
        """Analyze RDS optimization opportunities"""
        current_class = db_instance['DBInstanceClass']
        current_cost = self.rds_pricing.get(current_class, 100.0)
        
        recommendation = "No optimization needed"
        estimated_savings = 0.0
        potential_percentage = 0.0
        
        # Downsize if underutilized
        if cpu_util < 20 and connection_util < 30:
            # Suggest smaller instance
            downsize_mapping = {
                'db.m5.xlarge': 'db.m5.large',
                'db.m5.large': 'db.t3.large',
                'db.t3.large': 'db.t3.medium',
                'db.t3.medium': 'db.t3.small'
            }
            
            if current_class in downsize_mapping:
                recommended_class = downsize_mapping[current_class]
                new_cost = self.rds_pricing.get(recommended_class, current_cost)
                estimated_savings = current_cost - new_cost
                potential_percentage = (estimated_savings / current_cost) * 100
                recommendation = f"Downsize to {recommended_class}"
        
        # Suggest Reserved Instances for stable workloads
        elif cpu_util > 30 and connection_util > 20:
            estimated_savings = current_cost * 0.30  # 30% savings with RI
            potential_percentage = 30.0
            recommendation = "Consider Reserved Instance for 30% savings"
        
        # Storage optimization
        if db_instance.get('StorageType') == 'gp2':
            recommendation += " | Consider gp3 storage for better performance/cost"
            estimated_savings += db_instance.get('AllocatedStorage', 0) * 0.02  # Small savings
        
        return {
            'recommendation': recommendation,
            'estimated_savings': estimated_savings,
            'potential_percentage': potential_percentage
        }
    
    def generate_database_optimization_report(self, db_costs: List[DatabaseCostInfo]) -> str:
        """Generate database cost optimization report"""
        
        if not db_costs:
            return "No databases found for optimization analysis."
        
        df = pd.DataFrame([asdict(cost) for cost in db_costs])
        
        total_cost = df['monthly_cost'].sum()
        total_savings = df['estimated_savings'].sum()
        
        # High-cost databases
        top_costs = df.nlargest(10, 'monthly_cost')
        
        # High optimization potential
        top_optimization = df.nlargest(5, 'estimated_savings')
        
        report = f"""
Database Cost Optimization Report
=================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY (Mumbai Style)
===============================
यह report आपके database costs का complete optimization analysis है
जैसे Mumbai office space की efficient utilization और cost management

Total Monthly Database Cost: ${total_cost:.2f}
Total Databases Analyzed: {len(db_costs)}
Optimization Potential: ${total_savings:.2f} ({(total_savings/total_cost*100):.1f}%)

COST BREAKDOWN BY DATABASE TYPE
==============================
"""
        
        # Group by database type
        type_costs = df.groupby('db_type')['monthly_cost'].sum()
        for db_type, cost in type_costs.items():
            percentage = (cost / total_cost) * 100
            count = len(df[df['db_type'] == db_type])
            report += f"{db_type}: ${cost:.2f} ({percentage:.1f}%) - {count} instances\n"
        
        report += f"""

TOP 5 HIGHEST COST DATABASES
============================
"""
        
        for _, db in top_costs.head().iterrows():
            report += f"""
{db['db_identifier']} ({db['engine']}):
   Instance Class: {db['instance_class']}
   Monthly Cost: ${db['monthly_cost']:.2f}
   CPU Utilization: {db['utilization_cpu']:.1f}%
   Storage: {db['storage_gb']} GB
   Optimization Potential: ${db['estimated_savings']:.2f}
   Recommendation: {db['recommended_action']}
"""
        
        report += f"""

TOP 5 OPTIMIZATION OPPORTUNITIES
================================
"""
        
        for _, db in top_optimization.iterrows():
            report += f"""
{db['db_identifier']}:
   Current Cost: ${db['monthly_cost']:.2f}
   Potential Savings: ${db['estimated_savings']:.2f}
   Optimization: {db['optimization_potential']:.1f}%
   Action: {db['recommended_action']}
"""
        
        # Utilization analysis
        underutilized = df[(df['utilization_cpu'] < 30) & (df['utilization_connections'] < 40)]
        overutilized = df[(df['utilization_cpu'] > 80) | (df['utilization_connections'] > 80)]
        
        report += f"""

UTILIZATION ANALYSIS
===================
Underutilized Databases: {len(underutilized)} (downsize candidates)
Overutilized Databases: {len(overutilized)} (upsize candidates)
Well-utilized Databases: {len(df) - len(underutilized) - len(overutilized)}

MUMBAI CONTEXT ANALYSIS
=======================
Database optimization आपके लिए बिल्कुल Mumbai office space जैसा है:

🏢 SPACE UTILIZATION:
   - Right-sizing instances (like choosing correct office size for team)
   - Storage optimization (like efficient file management)
   - Resource sharing (like shared vs dedicated resources)

💰 COST PATTERNS:
   - Underutilized: {len(underutilized)} databases using <30% capacity
   - Overutilized: {len(overutilized)} databases at >80% capacity
   - Optimized: {len(df) - len(underutilized) - len(overutilized)} databases well-sized

📊 OPTIMIZATION STRATEGIES:
   1. Downsize underutilized instances
   2. Consider Reserved Instances for stable workloads
   3. Optimize storage types (gp2 → gp3)
   4. Implement read replicas for read-heavy workloads

IMMEDIATE ACTIONS
================
"""
        
        if len(underutilized) > 0:
            report += f"🔽 DOWNSIZE: {len(underutilized)} databases can be downsized for ${underutilized['estimated_savings'].sum():.2f}/month savings\n"
        
        if len(overutilized) > 0:
            report += f"🔼 UPSIZE: {len(overutilized)} databases need scaling to avoid performance issues\n"
        
        ri_candidates = df[df['recommended_action'].str.contains('Reserved Instance', na=False)]
        if len(ri_candidates) > 0:
            report += f"💳 RESERVED INSTANCES: {len(ri_candidates)} databases suitable for RI purchase\n"
        
        report += f"""

COST OPTIMIZATION ROADMAP
=========================
Month 1: Implement high-impact optimizations (${top_optimization.head(3)['estimated_savings'].sum():.2f} savings)
Month 2: Reserved Instance strategy for stable workloads
Month 3: Storage optimization and right-sizing review
Month 4: Quarterly utilization review and adjustments

NEXT STEPS
==========
1. Start with highest savings opportunities
2. Test downsizing in development environments first
3. Monitor performance after changes
4. Set up automated utilization alerts
5. Review optimization quarterly

Contact: Hindi Tech Community for database optimization support
"""
        
        return report

# Usage Example  
def main():
    """Production usage example"""
    try:
        print("🗄️  Initializing Database Cost Optimizer...")
        optimizer = DatabaseCostOptimizer()
        
        print("📊 Analyzing RDS database costs...")
        db_costs = asyncio.run(optimizer.analyze_rds_costs())
        
        if db_costs:
            total_cost = sum(db.monthly_cost for db in db_costs)
            total_savings = sum(db.estimated_savings for db in db_costs)
            
            print(f"💰 Total Monthly Cost: ${total_cost:.2f}")
            print(f"🎯 Optimization Potential: ${total_savings:.2f}")
            
            # Generate report
            report = optimizer.generate_database_optimization_report(db_costs)
            
            with open('database_cost_optimization_report.txt', 'w') as f:
                f.write(report)
            
            print("✅ Database cost optimization completed!")
            print("📄 Report saved to database_cost_optimization_report.txt")
            
            # Mumbai style summary
            if total_savings > 500:
                print("\n🏢 Mumbai Office Analogy: Significant space wastage - immediate optimization needed!")
            elif total_savings > 100:
                print("\n📊 Mumbai Office Analogy: Good optimization opportunities available")
            else:
                print("\n✅ Mumbai Office Analogy: Efficient space utilization!")
        
        else:
            print("⚠️  No RDS databases found for analysis")
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
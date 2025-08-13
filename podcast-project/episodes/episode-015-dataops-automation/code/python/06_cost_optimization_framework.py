#!/usr/bin/env python3
"""
DataOps Example 06: Cost Optimization Framework
Intelligent cost optimization for Indian data operations
Focus: Cloud cost management, resource optimization, budget alerts

Author: DataOps Architecture Series
Episode: 015 - DataOps Automation
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import boto3
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CostOptimizer:
    """Cost optimization for Indian companies"""
    
    def __init__(self, company_name: str, monthly_budget_inr: float):
        self.company_name = company_name
        self.monthly_budget_inr = monthly_budget_inr
        self.aws_session = boto3.Session(region_name='ap-south-1')
        
    def analyze_compute_costs(self) -> Dict[str, float]:
        """Analyze compute resource costs"""
        try:
            # Simulate cost analysis for Indian companies
            cost_breakdown = {
                'ec2_instances': np.random.uniform(15000, 50000),
                'rds_databases': np.random.uniform(8000, 25000),
                'lambda_functions': np.random.uniform(2000, 8000),
                'ecs_containers': np.random.uniform(5000, 20000),
                'emr_clusters': np.random.uniform(10000, 35000)
            }
            
            total_cost = sum(cost_breakdown.values())
            
            logger.info(f"Total monthly compute cost: ₹{total_cost:,.2f}")
            
            # Check budget compliance
            if total_cost > self.monthly_budget_inr:
                logger.warning(f"Cost exceeds budget by ₹{total_cost - self.monthly_budget_inr:,.2f}")
            
            return cost_breakdown
            
        except Exception as e:
            logger.error(f"Cost analysis failed: {e}")
            return {}
    
    def recommend_optimizations(self, cost_breakdown: Dict[str, float]) -> List[str]:
        """Recommend cost optimizations for Indian infrastructure"""
        recommendations = []
        
        try:
            # EC2 optimization recommendations
            if cost_breakdown.get('ec2_instances', 0) > 30000:
                recommendations.extend([
                    "Consider Reserved Instances for 40-60% savings",
                    "Use Spot Instances for batch processing workloads",
                    "Right-size instances based on actual usage",
                    "Schedule non-production instances (9 AM - 6 PM IST)"
                ])
            
            # Database optimization
            if cost_breakdown.get('rds_databases', 0) > 20000:
                recommendations.extend([
                    "Enable automated backups with shorter retention",
                    "Use Read Replicas in same AZ to reduce data transfer costs",
                    "Consider Aurora Serverless for variable workloads"
                ])
            
            # Data transfer optimization
            recommendations.extend([
                "Use CloudFront for content delivery to reduce bandwidth costs",
                "Keep data processing in ap-south-1 (Mumbai) region",
                "Use VPC endpoints to avoid NAT Gateway charges",
                "Compress data before S3 storage"
            ])
            
            # Indian-specific recommendations
            recommendations.extend([
                "Consider Indian cloud providers (Tata Communications, Sify) for cost comparison",
                "Use multi-AZ only for production workloads",
                "Implement data lifecycle policies for long-term storage",
                "Set up billing alerts for ₹10,000 increments"
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return []
    
    def calculate_potential_savings(self, cost_breakdown: Dict[str, float]) -> Dict[str, float]:
        """Calculate potential savings from optimizations"""
        savings = {}
        
        try:
            # Reserved Instance savings (40-60%)
            ec2_cost = cost_breakdown.get('ec2_instances', 0)
            savings['reserved_instances'] = ec2_cost * 0.5
            
            # Spot Instance savings (70-90%)
            savings['spot_instances'] = ec2_cost * 0.3 * 0.8  # 30% workload on spot
            
            # Right-sizing savings (20-30%)
            savings['right_sizing'] = ec2_cost * 0.25
            
            # Scheduling savings (60% for non-prod)
            savings['scheduling'] = ec2_cost * 0.4 * 0.6  # 40% non-prod workload
            
            # Storage optimization (30%)
            savings['storage_optimization'] = cost_breakdown.get('emr_clusters', 0) * 0.3
            
            total_savings = sum(savings.values())
            savings['total_potential'] = total_savings
            
            logger.info(f"Total potential monthly savings: ₹{total_savings:,.2f}")
            
            return savings
            
        except Exception as e:
            logger.error(f"Savings calculation failed: {e}")
            return {}

def main():
    """Demonstrate cost optimization for Indian companies"""
    
    print("💰 DataOps Cost Optimization Demo")
    print("=" * 50)
    
    companies = [
        {'name': 'paytm', 'budget': 200000},
        {'name': 'flipkart', 'budget': 500000},
        {'name': 'zomato', 'budget': 150000}
    ]
    
    for company in companies:
        print(f"\n🏢 Analyzing costs for {company['name'].upper()}")
        
        optimizer = CostOptimizer(company['name'], company['budget'])
        
        # Analyze current costs
        costs = optimizer.analyze_compute_costs()
        
        print(f"   💸 Current monthly costs:")
        for service, cost in costs.items():
            print(f"      {service}: ₹{cost:,.2f}")
        
        total_cost = sum(costs.values())
        print(f"   📊 Total: ₹{total_cost:,.2f} (Budget: ₹{company['budget']:,.2f})")
        
        # Get recommendations
        recommendations = optimizer.recommend_optimizations(costs)
        
        print(f"   💡 Top recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"      {i}. {rec}")
        
        # Calculate savings
        savings = optimizer.calculate_potential_savings(costs)
        
        print(f"   💵 Potential savings: ₹{savings.get('total_potential', 0):,.2f}/month")
        
        budget_utilization = (total_cost / company['budget']) * 100
        print(f"   📈 Budget utilization: {budget_utilization:.1f}%")
        
        if budget_utilization > 80:
            print(f"   ⚠️  High budget utilization - implement optimizations ASAP")
        elif budget_utilization > 60:
            print(f"   ⚡ Moderate usage - monitor and optimize")
        else:
            print(f"   ✅ Within budget - continue monitoring")
    
    print("\n✅ Cost optimization analysis completed!")

if __name__ == "__main__":
    main()
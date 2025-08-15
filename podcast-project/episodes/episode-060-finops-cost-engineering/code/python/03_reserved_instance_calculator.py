#!/usr/bin/env python3
"""
Reserved Instance Calculator & Optimizer
========================================

Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering
Advanced Reserved Instance/Reserved Capacity calculator for AWS, Azure, GCP

Author: Hindi Tech Community
Date: 2025
Version: 1.0

Features:
- Multi-cloud RI analysis (AWS, Azure, GCP)
- ROI calculation with break-even analysis
- Usage pattern analysis
- Recommendation engine
- Cost comparison scenarios
- Family coverage optimization
- Upfront vs partial payment analysis

Mumbai Context: RI purchase जैसे Mumbai local train season pass
- Monthly pass vs daily ticket
- 1st class vs 2nd class value analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import math

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

class PaymentOption(Enum):
    NO_UPFRONT = "no_upfront"
    PARTIAL_UPFRONT = "partial_upfront" 
    ALL_UPFRONT = "all_upfront"

class InstanceFamily(Enum):
    GENERAL_PURPOSE = "general_purpose"
    COMPUTE_OPTIMIZED = "compute_optimized"
    MEMORY_OPTIMIZED = "memory_optimized"
    STORAGE_OPTIMIZED = "storage_optimized"

@dataclass
class UsagePattern:
    """Instance usage pattern analysis"""
    instance_type: str
    region: str
    avg_hours_per_day: float
    avg_days_per_month: float
    utilization_percentage: float
    current_monthly_cost: float
    usage_variability: float  # Standard deviation

@dataclass
class ReservedInstanceOption:
    """Reserved Instance option details"""
    provider: CloudProvider
    instance_type: str
    region: str
    term_years: int
    payment_option: PaymentOption
    upfront_cost: float
    hourly_rate: float
    on_demand_hourly_rate: float
    discount_percentage: float

@dataclass
class ROIAnalysis:
    """ROI analysis for Reserved Instance"""
    break_even_months: float
    total_3_year_savings: float
    monthly_savings: float
    roi_percentage: float
    payback_period_months: float
    net_present_value: float

class ReservedInstanceCalculator:
    """
    Advanced Reserved Instance Calculator
    
    Mumbai Context: यह local train pass calculator जैसा है
    - Daily ticket vs Monthly pass vs Quarterly pass
    - कब कौन सा option सबसे economical है
    """
    
    def __init__(self):
        """Initialize RI calculator with market data"""
        self.pricing_data = self._load_pricing_data()
        self.discount_rates = {
            1: {'no_upfront': 0.25, 'partial_upfront': 0.35, 'all_upfront': 0.40},
            3: {'no_upfront': 0.40, 'partial_upfront': 0.50, 'all_upfront': 0.60}
        }
        logger.info("Reserved Instance Calculator initialized")

    def _load_pricing_data(self) -> Dict:
        """Load current market pricing data"""
        # In production, this would connect to cloud provider APIs
        # Simulated pricing data for demonstration
        return {
            'aws': {
                'us-east-1': {
                    't3.medium': {'on_demand': 0.0416, 'family': InstanceFamily.GENERAL_PURPOSE},
                    't3.large': {'on_demand': 0.0832, 'family': InstanceFamily.GENERAL_PURPOSE},
                    't3.xlarge': {'on_demand': 0.1664, 'family': InstanceFamily.GENERAL_PURPOSE},
                    'c5.large': {'on_demand': 0.085, 'family': InstanceFamily.COMPUTE_OPTIMIZED},
                    'c5.xlarge': {'on_demand': 0.17, 'family': InstanceFamily.COMPUTE_OPTIMIZED},
                    'm5.large': {'on_demand': 0.096, 'family': InstanceFamily.GENERAL_PURPOSE},
                    'm5.xlarge': {'on_demand': 0.192, 'family': InstanceFamily.GENERAL_PURPOSE},
                    'r5.large': {'on_demand': 0.126, 'family': InstanceFamily.MEMORY_OPTIMIZED},
                    'r5.xlarge': {'on_demand': 0.252, 'family': InstanceFamily.MEMORY_OPTIMIZED}
                },
                'ap-south-1': {  # Mumbai region
                    't3.medium': {'on_demand': 0.037, 'family': InstanceFamily.GENERAL_PURPOSE},
                    't3.large': {'on_demand': 0.074, 'family': InstanceFamily.GENERAL_PURPOSE},
                    'c5.large': {'on_demand': 0.076, 'family': InstanceFamily.COMPUTE_OPTIMIZED},
                    'm5.large': {'on_demand': 0.086, 'family': InstanceFamily.GENERAL_PURPOSE},
                    'r5.large': {'on_demand': 0.113, 'family': InstanceFamily.MEMORY_OPTIMIZED}
                }
            },
            'azure': {
                'eastus': {
                    'Standard_D2s_v3': {'on_demand': 0.096, 'family': InstanceFamily.GENERAL_PURPOSE},
                    'Standard_D4s_v3': {'on_demand': 0.192, 'family': InstanceFamily.GENERAL_PURPOSE},
                    'Standard_F2s_v2': {'on_demand': 0.085, 'family': InstanceFamily.COMPUTE_OPTIMIZED},
                    'Standard_F4s_v2': {'on_demand': 0.169, 'family': InstanceFamily.COMPUTE_OPTIMIZED},
                    'Standard_E2s_v3': {'on_demand': 0.134, 'family': InstanceFamily.MEMORY_OPTIMIZED}
                },
                'centralindia': {  # Mumbai equivalent
                    'Standard_D2s_v3': {'on_demand': 0.086, 'family': InstanceFamily.GENERAL_PURPOSE},
                    'Standard_D4s_v3': {'on_demand': 0.172, 'family': InstanceFamily.GENERAL_PURPOSE},
                    'Standard_F2s_v2': {'on_demand': 0.076, 'family': InstanceFamily.COMPUTE_OPTIMIZED}
                }
            }
        }

    def analyze_usage_pattern(self, instance_logs: List[Dict]) -> UsagePattern:
        """
        Analyze historical usage patterns
        
        Mumbai Context: Travel pattern analysis जैसे
        - Peak hours में travel
        - Weekend usage
        - Monthly variation
        """
        try:
            if not instance_logs:
                raise ValueError("No usage data provided")
            
            df = pd.DataFrame(instance_logs)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day'] = df['timestamp'].dt.day
            df['month'] = df['timestamp'].dt.month
            
            # Calculate daily usage hours
            daily_usage = df.groupby(df['timestamp'].dt.date).agg({
                'running': 'sum',  # Total running hours per day
                'cpu_utilization': 'mean'
            }).reset_index()
            
            avg_hours_per_day = daily_usage['running'].mean()
            avg_days_per_month = len(daily_usage) * 30 / len(daily_usage)  # Normalize to monthly
            utilization_percentage = daily_usage['cpu_utilization'].mean()
            
            # Current cost calculation
            instance_type = instance_logs[0]['instance_type']
            region = instance_logs[0]['region']
            provider = instance_logs[0]['provider']
            
            hourly_rate = self.pricing_data[provider][region][instance_type]['on_demand']
            current_monthly_cost = avg_hours_per_day * avg_days_per_month * hourly_rate
            
            # Usage variability
            usage_variability = daily_usage['running'].std()
            
            pattern = UsagePattern(
                instance_type=instance_type,
                region=region,
                avg_hours_per_day=avg_hours_per_day,
                avg_days_per_month=avg_days_per_month,
                utilization_percentage=utilization_percentage,
                current_monthly_cost=current_monthly_cost,
                usage_variability=usage_variability
            )
            
            logger.info(f"Analyzed usage pattern for {instance_type}")
            return pattern
            
        except Exception as e:
            logger.error(f"Failed to analyze usage pattern: {e}")
            raise

    def calculate_reserved_instance_options(self, 
                                          provider: CloudProvider,
                                          instance_type: str,
                                          region: str) -> List[ReservedInstanceOption]:
        """
        Calculate all available RI options
        
        Mumbai Context: सभी pass options compare करना
        - 1 year vs 3 year
        - Full payment vs installments
        """
        try:
            if provider.value not in self.pricing_data:
                raise ValueError(f"Provider {provider.value} not supported")
            
            if region not in self.pricing_data[provider.value]:
                raise ValueError(f"Region {region} not available for {provider.value}")
            
            if instance_type not in self.pricing_data[provider.value][region]:
                raise ValueError(f"Instance type {instance_type} not available")
            
            on_demand_rate = self.pricing_data[provider.value][region][instance_type]['on_demand']
            options = []
            
            # Generate options for different terms and payment options
            for term_years in [1, 3]:
                for payment_option in PaymentOption:
                    discount = self.discount_rates[term_years][payment_option.value]
                    discounted_hourly = on_demand_rate * (1 - discount)
                    
                    # Calculate upfront cost based on payment option
                    total_hours = term_years * 365 * 24
                    total_cost = discounted_hourly * total_hours
                    
                    if payment_option == PaymentOption.ALL_UPFRONT:
                        upfront_cost = total_cost
                        hourly_rate = 0.0
                    elif payment_option == PaymentOption.PARTIAL_UPFRONT:
                        upfront_cost = total_cost * 0.5
                        hourly_rate = (total_cost * 0.5) / total_hours
                    else:  # NO_UPFRONT
                        upfront_cost = 0.0
                        hourly_rate = discounted_hourly
                    
                    option = ReservedInstanceOption(
                        provider=provider,
                        instance_type=instance_type,
                        region=region,
                        term_years=term_years,
                        payment_option=payment_option,
                        upfront_cost=upfront_cost,
                        hourly_rate=hourly_rate,
                        on_demand_hourly_rate=on_demand_rate,
                        discount_percentage=discount * 100
                    )
                    options.append(option)
            
            logger.info(f"Generated {len(options)} RI options for {instance_type}")
            return options
            
        except Exception as e:
            logger.error(f"Failed to calculate RI options: {e}")
            return []

    def calculate_roi_analysis(self, 
                             usage_pattern: UsagePattern,
                             ri_option: ReservedInstanceOption,
                             discount_rate: float = 0.08) -> ROIAnalysis:
        """
        Calculate comprehensive ROI analysis for RI option
        
        Mumbai Context: Investment return calculation जैसे
        - FD vs Mutual Fund returns
        - Payback period analysis
        """
        try:
            # Monthly usage and costs
            monthly_hours = usage_pattern.avg_hours_per_day * usage_pattern.avg_days_per_month
            monthly_on_demand_cost = monthly_hours * ri_option.on_demand_hourly_rate
            monthly_reserved_cost = (monthly_hours * ri_option.hourly_rate) + (ri_option.upfront_cost / (ri_option.term_years * 12))
            monthly_savings = monthly_on_demand_cost - monthly_reserved_cost
            
            # Break-even analysis
            if monthly_savings > 0:
                break_even_months = ri_option.upfront_cost / monthly_savings if monthly_savings > 0 else float('inf')
            else:
                break_even_months = float('inf')
            
            # 3-year total savings
            total_months = ri_option.term_years * 12
            total_on_demand_cost = monthly_on_demand_cost * total_months
            total_reserved_cost = (monthly_hours * ri_option.hourly_rate * total_months) + ri_option.upfront_cost
            total_3_year_savings = total_on_demand_cost - total_reserved_cost
            
            # ROI calculation
            if ri_option.upfront_cost > 0:
                roi_percentage = (total_3_year_savings / ri_option.upfront_cost) * 100
            else:
                roi_percentage = float('inf') if total_3_year_savings > 0 else 0
            
            # Net Present Value (NPV) calculation
            npv = self._calculate_npv(monthly_savings, ri_option.upfront_cost, 
                                    ri_option.term_years * 12, discount_rate)
            
            analysis = ROIAnalysis(
                break_even_months=break_even_months,
                total_3_year_savings=total_3_year_savings,
                monthly_savings=monthly_savings,
                roi_percentage=roi_percentage,
                payback_period_months=break_even_months,
                net_present_value=npv
            )
            
            logger.info(f"Calculated ROI analysis for {ri_option.instance_type}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to calculate ROI analysis: {e}")
            raise

    def _calculate_npv(self, monthly_savings: float, initial_investment: float, 
                      months: int, discount_rate: float) -> float:
        """Calculate Net Present Value"""
        monthly_discount_rate = discount_rate / 12
        npv = -initial_investment
        
        for month in range(1, months + 1):
            npv += monthly_savings / ((1 + monthly_discount_rate) ** month)
        
        return npv

    def find_optimal_ri_strategy(self, usage_patterns: List[UsagePattern]) -> Dict:
        """
        Find optimal RI strategy across multiple instances
        
        Mumbai Context: Complete transport optimization strategy
        - कौन से routes के लिए pass लेना
        - कितने पैसे save होंगे
        """
        try:
            optimization_results = {
                'total_current_monthly_cost': 0,
                'total_optimized_monthly_cost': 0,
                'total_monthly_savings': 0,
                'total_upfront_investment': 0,
                'recommendations': [],
                'summary': {}
            }
            
            for pattern in usage_patterns:
                # Get all RI options for this instance
                provider = CloudProvider.AWS  # Default to AWS for demo
                ri_options = self.calculate_reserved_instance_options(
                    provider, pattern.instance_type, pattern.region
                )
                
                best_option = None
                best_roi = None
                best_score = -float('inf')
                
                # Evaluate each RI option
                for option in ri_options:
                    roi = self.calculate_roi_analysis(pattern, option)
                    
                    # Scoring algorithm (weighted by savings and ROI)
                    score = (roi.monthly_savings * 0.7) + (roi.roi_percentage * 0.3)
                    
                    if score > best_score and roi.break_even_months < 18:  # Max 18 months break-even
                        best_score = score
                        best_option = option
                        best_roi = roi
                
                # Add to results
                optimization_results['total_current_monthly_cost'] += pattern.current_monthly_cost
                
                if best_option and best_roi:
                    optimized_monthly_cost = pattern.current_monthly_cost - best_roi.monthly_savings
                    optimization_results['total_optimized_monthly_cost'] += optimized_monthly_cost
                    optimization_results['total_monthly_savings'] += best_roi.monthly_savings
                    optimization_results['total_upfront_investment'] += best_option.upfront_cost
                    
                    recommendation = {
                        'instance_type': pattern.instance_type,
                        'region': pattern.region,
                        'current_monthly_cost': pattern.current_monthly_cost,
                        'recommended_option': asdict(best_option),
                        'roi_analysis': asdict(best_roi),
                        'recommendation_reason': self._get_recommendation_reason(best_roi)
                    }
                    optimization_results['recommendations'].append(recommendation)
                else:
                    # No RI recommended
                    optimization_results['total_optimized_monthly_cost'] += pattern.current_monthly_cost
                    
                    recommendation = {
                        'instance_type': pattern.instance_type,
                        'region': pattern.region,
                        'current_monthly_cost': pattern.current_monthly_cost,
                        'recommended_option': None,
                        'roi_analysis': None,
                        'recommendation_reason': "No profitable RI option found - continue on-demand"
                    }
                    optimization_results['recommendations'].append(recommendation)
            
            # Calculate summary metrics
            total_annual_savings = optimization_results['total_monthly_savings'] * 12
            total_investment = optimization_results['total_upfront_investment']
            
            optimization_results['summary'] = {
                'total_instances_analyzed': len(usage_patterns),
                'instances_with_ri_recommendation': len([r for r in optimization_results['recommendations'] if r['recommended_option']]),
                'total_annual_savings': total_annual_savings,
                'total_upfront_investment': total_investment,
                'payback_period_months': total_investment / optimization_results['total_monthly_savings'] if optimization_results['total_monthly_savings'] > 0 else float('inf'),
                'annual_roi_percentage': (total_annual_savings / total_investment * 100) if total_investment > 0 else 0
            }
            
            logger.info(f"Optimized RI strategy for {len(usage_patterns)} instances")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Failed to find optimal RI strategy: {e}")
            raise

    def _get_recommendation_reason(self, roi_analysis: ROIAnalysis) -> str:
        """Get human-readable recommendation reason"""
        if roi_analysis.break_even_months <= 6:
            return f"STRONG BUY: Break-even in {roi_analysis.break_even_months:.1f} months, excellent ROI"
        elif roi_analysis.break_even_months <= 12:
            return f"BUY: Break-even in {roi_analysis.break_even_months:.1f} months, good savings"
        elif roi_analysis.break_even_months <= 18:
            return f"CONSIDER: Break-even in {roi_analysis.break_even_months:.1f} months, moderate savings"
        else:
            return "NOT RECOMMENDED: Break-even period too long"

    def generate_comparison_report(self, usage_patterns: List[UsagePattern]) -> str:
        """
        Generate detailed comparison report
        
        Mumbai Context: Complete financial planning report
        """
        try:
            optimization = self.find_optimal_ri_strategy(usage_patterns)
            
            report = f"""
Reserved Instance Optimization Report
====================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY (Mumbai Style)
===============================
Yeh report आपके cloud infrastructure का complete financial analysis है
जैसे आप अपने monthly transport expense optimize करते हैं

Current Monthly Cost: ${optimization['total_current_monthly_cost']:,.2f}
Optimized Monthly Cost: ${optimization['total_optimized_monthly_cost']:,.2f}
Monthly Savings: ${optimization['total_monthly_savings']:,.2f}
Annual Savings: ${optimization['summary']['total_annual_savings']:,.2f}

Investment Required: ${optimization['summary']['total_upfront_investment']:,.2f}
Payback Period: {optimization['summary']['payback_period_months']:.1f} months
Annual ROI: {optimization['summary']['annual_roi_percentage']:.2f}%

DETAILED RECOMMENDATIONS
=======================
"""
            
            for i, rec in enumerate(optimization['recommendations'], 1):
                report += f"""
Instance {i}: {rec['instance_type']} in {rec['region']}
----------------------------------------------------
Current Monthly Cost: ${rec['current_monthly_cost']:,.2f}
"""
                
                if rec['recommended_option']:
                    option = rec['recommended_option']
                    roi = rec['roi_analysis']
                    
                    report += f"""Recommended: {option['term_years']}-year {option['payment_option']}
Upfront Cost: ${option['upfront_cost']:,.2f}
Hourly Rate: ${option['hourly_rate']:.4f}
Monthly Savings: ${roi['monthly_savings']:,.2f}
Break-even: {roi['break_even_months']:.1f} months
Total 3-year Savings: ${roi['total_3_year_savings']:,.2f}
Reason: {rec['recommendation_reason']}
"""
                else:
                    report += f"""Recommended: Continue On-Demand
Reason: {rec['recommendation_reason']}
"""
            
            report += f"""

SUMMARY METRICS
==============
• Total Instances Analyzed: {optimization['summary']['total_instances_analyzed']}
• Instances with RI Recommendation: {optimization['summary']['instances_with_ri_recommendation']}
• Overall Annual ROI: {optimization['summary']['annual_roi_percentage']:.2f}%

Mumbai Context: यह analysis बिल्कुल Mumbai local train pass decision जैसा है
- अगर आप daily travel करते हैं तो monthly pass beneficial है
- अगर occasional travel है तो per-trip ticket better है
- यही logic cloud resources पर भी apply होता है!

NEXT STEPS
==========
1. Review recommendations with your team
2. Analyze cash flow impact of upfront investments
3. Start with highest ROI instances
4. Monitor usage patterns after RI purchase
5. Set up automated RI utilization monitoring

Contact: Hindi Tech Community for implementation support
"""
            
            logger.info("Generated comprehensive RI comparison report")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate comparison report: {e}")
            return f"Error generating report: {e}"

# Usage Example
def main():
    """
    Production usage example
    
    Mumbai Context: Monthly cost optimization review
    """
    try:
        # Initialize calculator
        print("🧮 Initializing Reserved Instance Calculator...")
        calculator = ReservedInstanceCalculator()
        
        # Sample usage patterns (in production, get from cloud monitoring)
        sample_usage_patterns = [
            UsagePattern(
                instance_type='t3.large',
                region='us-east-1',
                avg_hours_per_day=20,
                avg_days_per_month=30,
                utilization_percentage=65,
                current_monthly_cost=1199.04,  # 20 * 30 * 0.832 * 24
                usage_variability=2.5
            ),
            UsagePattern(
                instance_type='m5.xlarge',
                region='us-east-1', 
                avg_hours_per_day=24,
                avg_days_per_month=30,
                utilization_percentage=80,
                current_monthly_cost=3317.76,  # 24 * 30 * 0.192 * 24
                usage_variability=1.2
            ),
            UsagePattern(
                instance_type='c5.xlarge',
                region='us-east-1',
                avg_hours_per_day=18,
                avg_days_per_month=25,
                utilization_percentage=70,
                current_monthly_cost=1836.0,  # 18 * 25 * 0.17 * 24
                usage_variability=3.8
            )
        ]
        
        print("📊 Analyzing Reserved Instance opportunities...")
        
        # Find optimal strategy
        optimization = calculator.find_optimal_ri_strategy(sample_usage_patterns)
        
        # Display summary
        print(f"\n💰 Optimization Summary:")
        print(f"Current Monthly Cost: ${optimization['total_current_monthly_cost']:,.2f}")
        print(f"Optimized Monthly Cost: ${optimization['total_optimized_monthly_cost']:,.2f}")
        print(f"Monthly Savings: ${optimization['total_monthly_savings']:,.2f}")
        print(f"Annual Savings: ${optimization['summary']['total_annual_savings']:,.2f}")
        print(f"Investment Required: ${optimization['summary']['total_upfront_investment']:,.2f}")
        print(f"Payback Period: {optimization['summary']['payback_period_months']:.1f} months")
        print(f"Annual ROI: {optimization['summary']['annual_roi_percentage']:.2f}%")
        
        # Show top recommendations
        print(f"\n🏆 Top Recommendations:")
        for i, rec in enumerate(optimization['recommendations'][:3], 1):
            if rec['recommended_option']:
                roi = rec['roi_analysis']
                print(f"{i}. {rec['instance_type']}: ${roi['monthly_savings']:,.2f}/month savings")
        
        # Generate detailed report
        print("\n📄 Generating detailed report...")
        report = calculator.generate_comparison_report(sample_usage_patterns)
        
        # Save report
        with open('ri_optimization_report.txt', 'w') as f:
            f.write(report)
        
        print("✅ Reserved Instance analysis completed!")
        print("📄 Detailed report saved to ri_optimization_report.txt")
        
        # Show Mumbai context summary
        print(f"\n🚄 Mumbai Local Train Analogy:")
        print(f"Like buying monthly train pass:")
        if optimization['summary']['payback_period_months'] <= 6:
            print("✅ MUST BUY - You travel daily, pass is definitely worth it!")
        elif optimization['summary']['payback_period_months'] <= 12:
            print("👍 GOOD IDEA - Regular travel, pass makes sense")
        else:
            print("🤔 THINK AGAIN - Occasional travel, per-ticket might be better")
        
    except Exception as e:
        logger.error(f"RI analysis failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

"""
Production Integration Guide (Hindi):
=====================================

1. Data Sources:
   - AWS Cost Explorer API for usage patterns
   - Azure Consumption API for utilization data
   - GCP Billing API for cost analysis
   - CloudWatch/Azure Monitor for performance metrics

2. Automated Analysis:
   - Daily usage pattern collection
   - Weekly RI opportunity analysis  
   - Monthly optimization reports
   - Quarterly strategy reviews

3. Mumbai Business Context:
   - Map to local analogies (train pass, DTH plans)
   - Currency conversion for Indian teams
   - Regional pricing considerations
   - Compliance with local procurement policies

4. Integration Points:
   - JIRA tickets for RI purchase approvals
   - Slack notifications for recommendations
   - Email reports for finance teams
   - Dashboard integration for executives

5. Risk Management:
   - Usage pattern variability analysis
   - Business continuity considerations
   - Budget impact assessment
   - Change management process

यह calculator आपके cloud costs को efficiently manage करने में मदद करेगा!
"""
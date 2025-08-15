#!/usr/bin/env python3
"""
Data Transfer Cost Optimizer
============================

Mumbai Context: Data transfer optimization जैसे Mumbai logistics
- Regional vs inter-regional transfer costs
- Peak vs off-peak data transfer pricing
- Route optimization for cost efficiency
"""

import boto3
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DataTransferCost:
    source_region: str
    destination_region: str
    transfer_gb: float
    cost_per_gb: float
    monthly_cost: float
    transfer_type: str
    optimization_suggestion: str

class DataTransferOptimizer:
    """Data transfer cost optimization system"""
    
    def __init__(self):
        self.ce_client = boto3.client('ce')
        
        # Data transfer pricing (simplified)
        self.pricing = {
            'out_to_internet': 0.09,  # First 1GB free, then $0.09/GB
            'inter_region': 0.02,     # Between regions
            'intra_region': 0.01,     # Within same region
            'cloudfront': 0.085       # To CloudFront
        }
    
    def analyze_data_transfer_costs(self) -> List[DataTransferCost]:
        """Analyze data transfer patterns and costs"""
        transfer_costs = []
        
        try:
            # Get data transfer costs from Cost Explorer
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'REGION'}
                ],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['AmazonCloudFront', 'AmazonS3', 'AmazonEC2']
                    }
                }
            )
            
            # Process transfer costs (simplified analysis)
            for result in response['ResultsByTime']:
                for group in result.get('Groups', []):
                    service = group['Keys'][0]
                    region = group['Keys'][1]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    
                    if cost > 0:
                        # Estimate data transfer volume
                        estimated_gb = cost / self.pricing['out_to_internet']
                        
                        # Generate optimization suggestions
                        optimization = self._get_optimization_suggestion(service, region, cost)
                        
                        transfer_cost = DataTransferCost(
                            source_region=region,
                            destination_region='internet',
                            transfer_gb=estimated_gb,
                            cost_per_gb=self.pricing['out_to_internet'],
                            monthly_cost=cost,
                            transfer_type=service,
                            optimization_suggestion=optimization
                        )
                        
                        transfer_costs.append(transfer_cost)
            
            return transfer_costs
            
        except Exception as e:
            logger.error(f"Failed to analyze data transfer costs: {e}")
            return []
    
    def _get_optimization_suggestion(self, service: str, region: str, cost: float) -> str:
        """Get optimization suggestions for data transfer"""
        suggestions = []
        
        if cost > 100:
            suggestions.append("Consider CloudFront for global content delivery")
        
        if service == 'AmazonS3':
            suggestions.append("Implement S3 Transfer Acceleration")
            suggestions.append("Use VPC endpoints to avoid internet charges")
        
        if service == 'AmazonEC2':
            suggestions.append("Optimize instance placement for regional traffic")
            suggestions.append("Use Elastic Load Balancer for efficient routing")
        
        return " | ".join(suggestions) if suggestions else "Monitor usage patterns"
    
    def generate_transfer_optimization_report(self, transfer_costs: List[DataTransferCost]) -> str:
        """Generate data transfer optimization report"""
        
        if not transfer_costs:
            return "No significant data transfer costs found."
        
        total_cost = sum(t.monthly_cost for t in transfer_costs)
        total_gb = sum(t.transfer_gb for t in transfer_costs)
        
        # Sort by highest cost
        top_costs = sorted(transfer_costs, key=lambda x: x.monthly_cost, reverse=True)
        
        return f"""
Data Transfer Cost Optimization Report
=====================================
Generated: {datetime.now().strftime('%Y-%m-%d')}

EXECUTIVE SUMMARY (Mumbai Style)
===============================
यह report आपके data transfer costs का analysis है
जैसे Mumbai में goods transport का cost optimization

Total Monthly Transfer Cost: ${total_cost:.2f}
Total Data Transferred: {total_gb:.2f} GB
Average Cost per GB: ${(total_cost/total_gb):.4f}

TOP 5 TRANSFER COST SOURCES:
============================
{chr(10).join([f"• {t.source_region} ({t.transfer_type}): ${t.monthly_cost:.2f}" for t in top_costs[:5]])}

OPTIMIZATION OPPORTUNITIES:
==========================
{chr(10).join([f"• {t.source_region}: {t.optimization_suggestion}" for t in top_costs[:5]])}

MUMBAI CONTEXT ANALYSIS:
========================
Data transfer billing आपके लिए बिल्कुल Mumbai logistics जैसा है:

🚛 TRANSFER PATTERNS:
   - Local delivery (intra-region): Cheapest option
   - Inter-city delivery (inter-region): Moderate cost
   - International delivery (to internet): Most expensive

💰 COST OPTIMIZATION:
   - Use CDN for frequently accessed content (like local distribution centers)
   - Implement regional caching (like Mumbai godowns)
   - Optimize data placement (like strategic warehouse locations)

RECOMMENDATIONS:
===============
1. Implement CloudFront for global content delivery
2. Use VPC endpoints to reduce internet transfer costs
3. Consider regional data placement strategies
4. Monitor and optimize large file transfer patterns
5. Implement compression and caching strategies

NEXT STEPS:
==========
• Set up data transfer monitoring and alerting
• Implement cost-optimized content delivery strategies
• Review and optimize inter-region data flows
• Consider dedicated network connections for high-volume transfers

Contact: Hindi Tech Community for transfer optimization support
"""

# Usage Example
def main():
    try:
        print("📡 Initializing Data Transfer Optimizer...")
        optimizer = DataTransferOptimizer()
        
        print("📊 Analyzing data transfer costs...")
        transfer_costs = optimizer.analyze_data_transfer_costs()
        
        if transfer_costs:
            total_cost = sum(t.monthly_cost for t in transfer_costs)
            total_gb = sum(t.transfer_gb for t in transfer_costs)
            
            print(f"💰 Total Monthly Transfer Cost: ${total_cost:.2f}")
            print(f"📊 Total Data Transferred: {total_gb:.2f} GB")
            
            # Generate report
            report = optimizer.generate_transfer_optimization_report(transfer_costs)
            
            with open('data_transfer_optimization_report.txt', 'w') as f:
                f.write(report)
            
            print("✅ Data transfer optimization completed!")
            print("📄 Report saved to data_transfer_optimization_report.txt")
            
            # Mumbai style insight
            avg_cost_per_gb = total_cost / total_gb if total_gb > 0 else 0
            if avg_cost_per_gb > 0.05:
                print("\n🚛 Mumbai Logistics Insight: High per-GB cost - optimize routes!")
            else:
                print("\n✅ Mumbai Logistics Insight: Efficient transfer costs!")
        
        else:
            print("⚠️  No significant data transfer costs found")
        
    except Exception as e:
        logger.error(f"Data transfer optimization failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
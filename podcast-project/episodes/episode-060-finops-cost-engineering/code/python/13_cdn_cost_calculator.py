#!/usr/bin/env python3
"""
CDN Cost Calculator & Optimizer
===============================

Mumbai Context: CDN cost optimization जैसे delivery optimization
- Local vs central distribution points
- Peak time vs normal time delivery rates
- Regional delivery cost variations
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
class CDNCostInfo:
    distribution_id: str
    domain_name: str
    requests: int
    data_transfer_gb: float
    monthly_cost: float
    origin_region: str
    price_class: str
    optimization_potential: float

class CDNCostCalculator:
    """CDN cost analysis and optimization"""
    
    def __init__(self):
        self.cloudfront = boto3.client('cloudfront')
        self.cloudwatch = boto3.client('cloudwatch')
        
        # CloudFront pricing (simplified)
        self.pricing = {
            'requests_per_10k': 0.0075,  # First 10B requests
            'data_transfer_gb': {
                'PriceClass_100': 0.085,  # US, Canada, Europe
                'PriceClass_200': 0.090,  # Above + Asia
                'PriceClass_All': 0.095   # All edge locations
            }
        }
    
    async def analyze_cdn_costs(self) -> List[CDNCostInfo]:
        """Analyze CloudFront distribution costs"""
        cdn_costs = []
        
        try:
            distributions = self.cloudfront.list_distributions()
            
            for dist in distributions.get('DistributionList', {}).get('Items', []):
                dist_id = dist['Id']
                domain = dist['DomainName']
                
                # Get metrics from CloudWatch
                requests = await self._get_requests(dist_id)
                data_transfer = await self._get_data_transfer(dist_id)
                
                # Calculate costs
                price_class = dist.get('PriceClass', 'PriceClass_All')
                monthly_cost = self._calculate_cost(requests, data_transfer, price_class)
                
                # Optimization analysis
                optimization = self._analyze_optimization(dist, requests, data_transfer)
                
                cdn_cost = CDNCostInfo(
                    distribution_id=dist_id,
                    domain_name=domain,
                    requests=requests,
                    data_transfer_gb=data_transfer,
                    monthly_cost=monthly_cost,
                    origin_region=self._get_origin_region(dist),
                    price_class=price_class,
                    optimization_potential=optimization
                )
                
                cdn_costs.append(cdn_cost)
            
            return cdn_costs
            
        except Exception as e:
            logger.error(f"Failed to analyze CDN costs: {e}")
            return []
    
    def _calculate_cost(self, requests: int, data_transfer_gb: float, price_class: str) -> float:
        """Calculate monthly CDN cost"""
        request_cost = (requests / 10000) * self.pricing['requests_per_10k']
        transfer_rate = self.pricing['data_transfer_gb'][price_class]
        transfer_cost = data_transfer_gb * transfer_rate
        return request_cost + transfer_cost
    
    def generate_cdn_report(self, cdn_costs: List[CDNCostInfo]) -> str:
        """Generate CDN cost optimization report"""
        total_cost = sum(c.monthly_cost for c in cdn_costs)
        total_optimization = sum(c.optimization_potential for c in cdn_costs)
        
        return f"""
CDN Cost Analysis Report
=======================
Generated: {datetime.now().strftime('%Y-%m-%d')}

Mumbai Context: यह delivery optimization जैसा है
- Central warehouse vs local distribution points
- Peak time vs normal delivery rates

Total Monthly CDN Cost: ${total_cost:.2f}
Distributions Analyzed: {len(cdn_costs)}
Optimization Potential: ${total_optimization:.2f}

TOP COST DISTRIBUTIONS:
{chr(10).join([f"• {c.domain_name}: ${c.monthly_cost:.2f}" for c in sorted(cdn_costs, key=lambda x: x.monthly_cost, reverse=True)[:5]])}

OPTIMIZATION RECOMMENDATIONS:
• Consider price class optimization for regional content
• Implement caching strategies for frequently accessed content
• Review origin server optimization opportunities
• Analyze request patterns for cost-effective routing

Contact: Hindi Tech Community for CDN optimization
"""

# Usage Example
def main():
    try:
        print("🌐 Initializing CDN Cost Calculator...")
        calculator = CDNCostCalculator()
        
        print("📊 Analyzing CloudFront distributions...")
        # cdn_costs = asyncio.run(calculator.analyze_cdn_costs())
        
        # Simulate some data for demo
        cdn_costs = [
            CDNCostInfo("E123", "api.example.com", 1000000, 500.0, 67.5, "us-east-1", "PriceClass_All", 15.0),
            CDNCostInfo("E456", "static.example.com", 2000000, 1000.0, 245.0, "eu-west-1", "PriceClass_200", 25.0)
        ]
        
        if cdn_costs:
            total_cost = sum(c.monthly_cost for c in cdn_costs)
            print(f"💰 Total Monthly CDN Cost: ${total_cost:.2f}")
            
            # Generate report
            report = calculator.generate_cdn_report(cdn_costs)
            
            with open('cdn_cost_report.txt', 'w') as f:
                f.write(report)
            
            print("✅ CDN cost analysis completed!")
            print("📄 Report saved to cdn_cost_report.txt")
        else:
            print("⚠️  No CDN distributions found")
        
    except Exception as e:
        logger.error(f"CDN analysis failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
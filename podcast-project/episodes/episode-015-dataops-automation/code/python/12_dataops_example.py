#!/usr/bin/env python3
"""
DataOps Example 12: Advanced DataOps Component
Production-ready example for Indian data operations

Author: DataOps Architecture Series
Episode: 015 - DataOps Automation
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataOpsComponent12:
    """Advanced DataOps component for Indian companies"""
    
    def __init__(self, company_name: str):
        self.company_name = company_name
        logger.info(f"DataOps Component 12 initialized for {company_name}")
    
    def process_indian_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process data with Indian context"""
        try:
            # Sample processing logic
            processed_data = data.copy()
            
            # Add Indian specific processing
            if 'amount' in processed_data.columns:
                processed_data['amount_inr'] = processed_data['amount']
                processed_data['amount_category'] = pd.cut(
                    processed_data['amount'], 
                    bins=[0, 1000, 10000, 100000, float('inf')],
                    labels=['Small', 'Medium', 'Large', 'Very Large']
                )
            
            # Add timestamp
            processed_data['processed_at'] = datetime.now()
            
            logger.info(f"Processed {len(processed_data)} records for {self.company_name}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            return pd.DataFrame()
    
    def generate_insights(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate business insights for Indian market"""
        try:
            insights = {
                'total_records': len(data),
                'processing_time': datetime.now().isoformat(),
                'data_quality_score': np.random.uniform(85, 98),
                'cost_impact_inr': np.random.uniform(1000, 50000),
                'recommendations': [
                    'Optimize data pipeline for Indian traffic patterns',
                    'Implement cost controls for cloud resources',
                    'Enhance data quality monitoring'
                ]
            }
            
            if 'amount_inr' in data.columns:
                insights['transaction_stats'] = {
                    'total_amount_inr': float(data['amount_inr'].sum()),
                    'avg_amount_inr': float(data['amount_inr'].mean()),
                    'max_amount_inr': float(data['amount_inr'].max())
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return {}

def main():
    """Demonstrate DataOps Component 12"""
    
    print(f"🚀 DataOps Component 12 Demo")
    print("=" * 40)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'id': range(1000),
        'amount': np.random.uniform(100, 100000, 1000),
        'category': np.random.choice(['A', 'B', 'C'], 1000),
        'timestamp': [datetime.now() - timedelta(days=i) for i in range(1000)]
    })
    
    # Initialize component
    component = DataOpsComponent12('indian_fintech_12')
    
    # Process data
    processed_data = component.process_indian_data(sample_data)
    
    # Generate insights
    insights = component.generate_insights(processed_data)
    
    print(f"📊 Processing Results:")
    print(f"   Records processed: {insights.get('total_records', 0)}")
    print(f"   Data quality score: {insights.get('data_quality_score', 0):.1f}%")
    print(f"   Cost impact: ₹{insights.get('cost_impact_inr', 0):,.2f}")
    
    if 'transaction_stats' in insights:
        stats = insights['transaction_stats']
        print(f"   Total amount: ₹{stats['total_amount_inr']:,.2f}")
        print(f"   Average amount: ₹{stats['avg_amount_inr']:,.2f}")
    
    print(f"✅ Component 12 demo completed!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Spot Instance Manager & Optimizer
=================================

Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering
Advanced Spot Instance management system for AWS/Azure/GCP

Author: Hindi Tech Community
Date: 2025
Version: 1.0

Features:
- Spot price tracking and prediction
- Automated bidding strategies
- Interruption handling and recovery
- Workload suitability analysis
- Multi-AZ spot orchestration
- Cost savings calculation
- Risk assessment and mitigation

Mumbai Context: Spot instances जैसे Mumbai auto bargaining
- Market rate vs negotiated price
- Risk of availability
- Backup options ready
"""

import asyncio
import aiohttp
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
import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import seaborn as sns

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

class SpotStrategy(Enum):
    AGGRESSIVE = "aggressive"  # Lowest price, high risk
    BALANCED = "balanced"     # Balance price and availability
    CONSERVATIVE = "conservative"  # Higher price, better availability

class WorkloadType(Enum):
    BATCH_PROCESSING = "batch_processing"
    WEB_SERVICES = "web_services" 
    DATA_ANALYTICS = "data_analytics"
    ML_TRAINING = "ml_training"
    CI_CD = "ci_cd"

@dataclass
class SpotPriceHistory:
    """Spot price historical data"""
    instance_type: str
    availability_zone: str
    price: float
    timestamp: datetime
    product_description: str

@dataclass
class SpotInstanceConfig:
    """Spot instance configuration"""
    instance_type: str
    max_price: float
    min_instances: int
    max_instances: int
    availability_zones: List[str]
    strategy: SpotStrategy
    workload_type: WorkloadType
    interruption_behavior: str  # terminate, stop, hibernate

@dataclass
class InterruptionEvent:
    """Spot instance interruption event"""
    instance_id: str
    instance_type: str
    availability_zone: str
    interruption_time: datetime
    warning_time: datetime
    workload_type: WorkloadType
    recovery_time: Optional[datetime] = None

class SpotInstanceManager:
    """
    Advanced Spot Instance Management System
    
    Mumbai Context: यह auto bargaining system जैसा है
    - सबसे कम rate पर ride book करना
    - अगर auto cancel हो जाए तो दूसरा option ready रखना
    - Peak time vs normal time pricing
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize spot instance manager"""
        try:
            self.region = region
            self.ec2_client = boto3.client('ec2', region_name=region)
            self.autoscaling_client = boto3.client('autoscaling', region_name=region)
            self.cloudwatch = boto3.client('cloudwatch', region_name=region)
            
            # Internal state
            self.active_requests = {}
            self.interruption_history = []
            self.price_cache = {}
            self.prediction_models = {}
            
            # Start background monitoring
            self.monitoring_enabled = True
            self.monitoring_thread = threading.Thread(target=self._monitor_spot_instances)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            logger.info("Spot Instance Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Spot Instance Manager: {e}")
            raise

    async def get_spot_price_history(self, 
                                   instance_types: List[str],
                                   days_back: int = 7) -> List[SpotPriceHistory]:
        """
        Get historical spot pricing data
        
        Mumbai Context: Historical auto fare tracking
        - Morning peak vs evening peak rates
        - Monsoon vs normal season pricing
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)
            
            price_history = []
            
            response = self.ec2_client.describe_spot_price_history(
                InstanceTypes=instance_types,
                ProductDescriptions=['Linux/UNIX'],
                StartTime=start_time,
                EndTime=end_time
            )
            
            for price_data in response['SpotPriceHistory']:
                history_entry = SpotPriceHistory(
                    instance_type=price_data['InstanceType'],
                    availability_zone=price_data['AvailabilityZone'],
                    price=float(price_data['SpotPrice']),
                    timestamp=price_data['Timestamp'],
                    product_description=price_data['ProductDescription']
                )
                price_history.append(history_entry)
            
            logger.info(f"Retrieved {len(price_history)} spot price records")
            return price_history
            
        except Exception as e:
            logger.error(f"Failed to get spot price history: {e}")
            return []

    def analyze_spot_price_trends(self, 
                                price_history: List[SpotPriceHistory]) -> Dict[str, Any]:
        """
        Analyze spot price trends and volatility
        
        Mumbai Context: Market trend analysis जैसे
        - Seasonal auto fare patterns
        - Peak hour pricing trends  
        - Weekend vs weekday rates
        """
        try:
            if not price_history:
                return {}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame([asdict(p) for p in price_history])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            analysis_results = {}
            
            for instance_type in df['instance_type'].unique():
                instance_data = df[df['instance_type'] == instance_type].copy()
                instance_data = instance_data.sort_values('timestamp')
                
                # Basic statistics
                current_price = instance_data['price'].iloc[-1]
                avg_price = instance_data['price'].mean()
                min_price = instance_data['price'].min()
                max_price = instance_data['price'].max()
                price_volatility = instance_data['price'].std()
                
                # Trend analysis
                instance_data['price_ma_3h'] = instance_data['price'].rolling(window=3).mean()
                instance_data['price_trend'] = instance_data['price'].pct_change()
                
                # Peak hour analysis
                peak_hours = instance_data.groupby('hour')['price'].mean().to_dict()
                peak_days = instance_data.groupby('day_of_week')['price'].mean().to_dict()
                
                # Availability zone comparison
                az_analysis = instance_data.groupby('availability_zone')['price'].agg([
                    'mean', 'min', 'max', 'std', 'count'
                ]).to_dict()
                
                # Price prediction (simple moving average)
                recent_prices = instance_data['price'].tail(24).values  # Last 24 hours
                predicted_price = np.mean(recent_prices) if len(recent_prices) > 0 else current_price
                
                analysis_results[instance_type] = {
                    'current_price': current_price,
                    'average_price': avg_price,
                    'min_price': min_price,
                    'max_price': max_price,
                    'volatility': price_volatility,
                    'volatility_percentage': (price_volatility / avg_price * 100) if avg_price > 0 else 0,
                    'predicted_next_hour': predicted_price,
                    'price_trend_24h': instance_data['price_trend'].tail(24).mean(),
                    'peak_hours': peak_hours,
                    'peak_days': peak_days,
                    'availability_zones': az_analysis,
                    'recommendation': self._get_pricing_recommendation(
                        current_price, avg_price, price_volatility
                    )
                }
            
            logger.info(f"Analyzed spot price trends for {len(analysis_results)} instance types")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Failed to analyze spot price trends: {e}")
            return {}

    def _get_pricing_recommendation(self, 
                                  current_price: float,
                                  avg_price: float, 
                                  volatility: float) -> str:
        """Get pricing recommendation based on analysis"""
        cv = volatility / avg_price if avg_price > 0 else 0
        price_ratio = current_price / avg_price if avg_price > 0 else 1
        
        if price_ratio < 0.8 and cv < 0.2:
            return "BUY_NOW: Price below average with low volatility"
        elif price_ratio < 0.9 and cv < 0.3:
            return "GOOD_TIME: Reasonable price with moderate volatility"
        elif price_ratio > 1.2:
            return "WAIT: Price above average, consider waiting"
        elif cv > 0.5:
            return "HIGH_RISK: Very volatile pricing, use conservative bidding"
        else:
            return "MODERATE: Standard market conditions"

    def create_spot_fleet_request(self, config: SpotInstanceConfig) -> str:
        """
        Create optimized spot fleet request
        
        Mumbai Context: Multiple auto booking strategy
        - एक साथ कई auto से quotation लेना
        - सबसे अच्छा rate वाला select करना
        """
        try:
            # Prepare launch configurations for multiple AZs
            launch_specs = []
            
            for az in config.availability_zones:
                # Get current spot price for this AZ
                current_price = self._get_current_spot_price(config.instance_type, az)
                
                # Calculate bid price based on strategy
                bid_price = self._calculate_bid_price(
                    current_price, config.max_price, config.strategy
                )
                
                launch_spec = {
                    'InstanceType': config.instance_type,
                    'ImageId': self._get_latest_ami_id(),
                    'KeyName': 'your-key-pair',  # Configure as needed
                    'SecurityGroups': [{'GroupId': 'sg-xxxxxxxx'}],  # Configure as needed
                    'SubnetId': self._get_subnet_for_az(az),
                    'SpotPrice': str(bid_price),
                    'WeightedCapacity': 1,
                    'UserData': self._get_user_data_script(config.workload_type)
                }
                launch_specs.append(launch_spec)
            
            # Create spot fleet configuration
            spot_fleet_config = {
                'IamFleetRole': 'arn:aws:iam::123456789012:role/aws-ec2-spot-fleet-role',
                'TargetCapacity': config.max_instances,
                'SpotPrice': str(config.max_price),
                'LaunchSpecifications': launch_specs,
                'Type': 'maintain',
                'AllocationStrategy': self._get_allocation_strategy(config.strategy),
                'InstanceInterruptionBehavior': config.interruption_behavior,
                'ReplaceUnhealthyInstances': True,
                'ExcessCapacityTerminationPolicy': 'diversification'
            }
            
            # Request spot fleet
            response = self.ec2_client.request_spot_fleet(
                SpotFleetRequestConfig=spot_fleet_config
            )
            
            spot_fleet_id = response['SpotFleetRequestId']
            
            # Store request details
            self.active_requests[spot_fleet_id] = {
                'config': config,
                'created_at': datetime.now(),
                'status': 'active'
            }
            
            logger.info(f"Created spot fleet request: {spot_fleet_id}")
            return spot_fleet_id
            
        except Exception as e:
            logger.error(f"Failed to create spot fleet request: {e}")
            raise

    def _calculate_bid_price(self, 
                           current_price: float, 
                           max_price: float,
                           strategy: SpotStrategy) -> float:
        """Calculate optimal bid price based on strategy"""
        if strategy == SpotStrategy.AGGRESSIVE:
            # Bid just above current price
            return min(current_price * 1.05, max_price)
        elif strategy == SpotStrategy.BALANCED:
            # Bid moderate premium above current price
            return min(current_price * 1.15, max_price)
        else:  # CONSERVATIVE
            # Bid significant premium for better availability
            return min(current_price * 1.3, max_price)

    def _get_allocation_strategy(self, strategy: SpotStrategy) -> str:
        """Get allocation strategy based on spot strategy"""
        if strategy == SpotStrategy.AGGRESSIVE:
            return 'lowestPrice'
        elif strategy == SpotStrategy.BALANCED:
            return 'diversified'
        else:  # CONSERVATIVE
            return 'diversified'

    def _get_current_spot_price(self, instance_type: str, az: str) -> float:
        """Get current spot price for instance type in AZ"""
        try:
            response = self.ec2_client.describe_spot_price_history(
                InstanceTypes=[instance_type],
                AvailabilityZones=[az],
                ProductDescriptions=['Linux/UNIX'],
                MaxResults=1
            )
            
            if response['SpotPriceHistory']:
                return float(response['SpotPriceHistory'][0]['SpotPrice'])
            else:
                return 0.1  # Default fallback price
                
        except Exception as e:
            logger.warning(f"Failed to get current spot price: {e}")
            return 0.1

    def _get_latest_ami_id(self) -> str:
        """Get latest Amazon Linux 2 AMI ID"""
        try:
            response = self.ec2_client.describe_images(
                Owners=['amazon'],
                Filters=[
                    {'Name': 'name', 'Values': ['amzn2-ami-hvm-*']},
                    {'Name': 'architecture', 'Values': ['x86_64']},
                    {'Name': 'virtualization-type', 'Values': ['hvm']},
                    {'Name': 'state', 'Values': ['available']}
                ]
            )
            
            # Sort by creation date and get latest
            images = sorted(response['Images'], 
                          key=lambda x: x['CreationDate'], reverse=True)
            return images[0]['ImageId'] if images else 'ami-0abcdef1234567890'
            
        except Exception as e:
            logger.warning(f"Failed to get latest AMI: {e}")
            return 'ami-0abcdef1234567890'  # Fallback AMI

    def _get_subnet_for_az(self, az: str) -> str:
        """Get subnet ID for availability zone"""
        # In production, this would query VPC subnets
        # For demo, return placeholder
        subnet_mapping = {
            f"{self.region}a": "subnet-12345a",
            f"{self.region}b": "subnet-12345b", 
            f"{self.region}c": "subnet-12345c"
        }
        return subnet_mapping.get(az, "subnet-default")

    def _get_user_data_script(self, workload_type: WorkloadType) -> str:
        """Get user data script based on workload type"""
        base_script = """#!/bin/bash
yum update -y
yum install -y awscli docker
systemctl start docker
systemctl enable docker

# Setup interruption monitoring
cat > /opt/monitor_interruption.sh << 'EOF'
#!/bin/bash
while true; do
    TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
    RESPONSE=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/spot/instance-action)
    if [ $? -eq 0 ]; then
        echo "$(date): Spot interruption warning received" >> /var/log/spot-interruption.log
        # Graceful shutdown logic here
        /opt/graceful_shutdown.sh
        break
    fi
    sleep 5
done
EOF

chmod +x /opt/monitor_interruption.sh
nohup /opt/monitor_interruption.sh &
"""
        
        workload_scripts = {
            WorkloadType.BATCH_PROCESSING: base_script + """
# Setup batch processing environment
yum install -y python3 python3-pip
pip3 install pandas numpy boto3
""",
            WorkloadType.WEB_SERVICES: base_script + """
# Setup web service environment  
yum install -y nginx
systemctl start nginx
systemctl enable nginx
""",
            WorkloadType.DATA_ANALYTICS: base_script + """
# Setup data analytics environment
yum install -y python3-pip R
pip3 install jupyter pandas numpy scipy scikit-learn
""",
            WorkloadType.ML_TRAINING: base_script + """
# Setup ML training environment
yum install -y python3-pip
pip3 install tensorflow pytorch scikit-learn
""",
            WorkloadType.CI_CD: base_script + """
# Setup CI/CD environment
yum install -y git jenkins
"""
        }
        
        return workload_scripts.get(workload_type, base_script)

    def handle_spot_interruption(self, instance_id: str, interruption_event: InterruptionEvent):
        """
        Handle spot instance interruption gracefully
        
        Mumbai Context: Auto breakdown handling
        - दूसरा auto book करना
        - Data backup करना
        - Graceful shutdown
        """
        try:
            logger.warning(f"Handling spot interruption for instance: {instance_id}")
            
            # Record interruption event
            self.interruption_history.append(interruption_event)
            
            # Get instance details
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            instance_data = response['Reservations'][0]['Instances'][0]
            
            # Implement graceful shutdown based on workload type
            if interruption_event.workload_type == WorkloadType.BATCH_PROCESSING:
                self._handle_batch_interruption(instance_id, instance_data)
            elif interruption_event.workload_type == WorkloadType.WEB_SERVICES:
                self._handle_web_service_interruption(instance_id, instance_data)
            elif interruption_event.workload_type == WorkloadType.DATA_ANALYTICS:
                self._handle_analytics_interruption(instance_id, instance_data)
            elif interruption_event.workload_type == WorkloadType.ML_TRAINING:
                self._handle_ml_training_interruption(instance_id, instance_data)
            elif interruption_event.workload_type == WorkloadType.CI_CD:
                self._handle_cicd_interruption(instance_id, instance_data)
            
            # Launch replacement instance if needed
            self._launch_replacement_instance(interruption_event)
            
            logger.info(f"Successfully handled interruption for {instance_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle spot interruption: {e}")

    def _handle_batch_interruption(self, instance_id: str, instance_data: Dict):
        """Handle batch processing workload interruption"""
        try:
            # Save current state to S3
            self._save_batch_state_to_s3(instance_id)
            
            # Send notification about interruption
            self._send_interruption_notification(
                instance_id, "Batch processing job interrupted, state saved"
            )
            
        except Exception as e:
            logger.error(f"Failed to handle batch interruption: {e}")

    def _handle_web_service_interruption(self, instance_id: str, instance_data: Dict):
        """Handle web service workload interruption"""
        try:
            # Drain traffic from load balancer
            self._drain_load_balancer_traffic(instance_id)
            
            # Wait for existing connections to complete
            time.sleep(30)
            
            # Shutdown gracefully
            logger.info(f"Web service {instance_id} drained and shutting down")
            
        except Exception as e:
            logger.error(f"Failed to handle web service interruption: {e}")

    def _monitor_spot_instances(self):
        """Background monitoring for spot instance interruptions"""
        while self.monitoring_enabled:
            try:
                # Check for interruption warnings via metadata API on each instance
                # This would be implemented as CloudWatch Events in production
                
                # Check spot fleet status
                for fleet_id in list(self.active_requests.keys()):
                    try:
                        response = self.ec2_client.describe_spot_fleet_requests(
                            SpotFleetRequestIds=[fleet_id]
                        )
                        
                        fleet_data = response['SpotFleetRequestConfigs'][0]
                        if fleet_data['SpotFleetRequestState'] == 'cancelled_terminating':
                            logger.warning(f"Spot fleet {fleet_id} is terminating")
                            # Handle fleet termination
                        
                    except Exception as e:
                        logger.error(f"Error monitoring fleet {fleet_id}: {e}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in spot monitoring: {e}")
                time.sleep(60)

    def calculate_spot_savings(self, config: SpotInstanceConfig, 
                             usage_hours: int = 730) -> Dict[str, float]:
        """
        Calculate spot instance cost savings vs on-demand
        
        Mumbai Context: Auto vs taxi savings calculation
        """
        try:
            # Get on-demand pricing (simplified)
            on_demand_prices = {
                't3.micro': 0.0104, 't3.small': 0.0208, 't3.medium': 0.0416,
                't3.large': 0.0832, 't3.xlarge': 0.1664, 't3.2xlarge': 0.3328,
                'm5.large': 0.096, 'm5.xlarge': 0.192, 'm5.2xlarge': 0.384,
                'c5.large': 0.085, 'c5.xlarge': 0.17, 'c5.2xlarge': 0.34
            }
            
            on_demand_hourly = on_demand_prices.get(config.instance_type, 0.1)
            
            # Get average spot price for the instance type
            price_history = asyncio.run(self.get_spot_price_history([config.instance_type]))
            if price_history:
                avg_spot_price = sum(p.price for p in price_history) / len(price_history)
            else:
                avg_spot_price = on_demand_hourly * 0.3  # Assume 70% discount
            
            # Calculate costs
            on_demand_monthly_cost = on_demand_hourly * usage_hours
            spot_monthly_cost = avg_spot_price * usage_hours
            monthly_savings = on_demand_monthly_cost - spot_monthly_cost
            savings_percentage = (monthly_savings / on_demand_monthly_cost * 100) if on_demand_monthly_cost > 0 else 0
            
            # Annual calculations
            annual_on_demand = on_demand_monthly_cost * 12
            annual_spot = spot_monthly_cost * 12
            annual_savings = annual_on_demand - annual_spot
            
            savings_analysis = {
                'on_demand_hourly_rate': on_demand_hourly,
                'average_spot_rate': avg_spot_price,
                'monthly_on_demand_cost': on_demand_monthly_cost,
                'monthly_spot_cost': spot_monthly_cost,
                'monthly_savings': monthly_savings,
                'savings_percentage': savings_percentage,
                'annual_on_demand_cost': annual_on_demand,
                'annual_spot_cost': annual_spot,
                'annual_savings': annual_savings,
                'usage_hours_analyzed': usage_hours
            }
            
            logger.info(f"Calculated spot savings for {config.instance_type}")
            return savings_analysis
            
        except Exception as e:
            logger.error(f"Failed to calculate spot savings: {e}")
            return {}

    def generate_spot_report(self, configs: List[SpotInstanceConfig]) -> str:
        """
        Generate comprehensive spot instance analysis report
        
        Mumbai Context: Complete transport cost analysis report
        """
        try:
            report = f"""
Spot Instance Analysis Report
============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY (Mumbai Style)
===============================
यह report आपके spot instance strategy का complete analysis है
जैसे Mumbai में auto vs taxi vs Uber pool का cost comparison

SPOT INSTANCE RECOMMENDATIONS
============================
"""
            
            total_monthly_savings = 0
            total_annual_savings = 0
            
            for i, config in enumerate(configs, 1):
                # Get price analysis
                price_history = asyncio.run(self.get_spot_price_history([config.instance_type]))
                price_trends = self.analyze_spot_price_trends(price_history)
                
                # Calculate savings
                savings = self.calculate_spot_savings(config)
                
                total_monthly_savings += savings.get('monthly_savings', 0)
                total_annual_savings += savings.get('annual_savings', 0)
                
                report += f"""
Configuration {i}: {config.instance_type}
-----------------------------------------
Strategy: {config.strategy.value}
Workload Type: {config.workload_type.value}
Max Price: ${config.max_price:.4f}/hour
Availability Zones: {', '.join(config.availability_zones)}

COST ANALYSIS:
On-Demand Rate: ${savings.get('on_demand_hourly_rate', 0):.4f}/hour
Average Spot Rate: ${savings.get('average_spot_rate', 0):.4f}/hour
Monthly Savings: ${savings.get('monthly_savings', 0):.2f}
Savings Percentage: {savings.get('savings_percentage', 0):.1f}%
Annual Savings: ${savings.get('annual_savings', 0):.2f}

PRICE ANALYSIS:
"""
                
                if config.instance_type in price_trends:
                    trend = price_trends[config.instance_type]
                    report += f"""Current Price: ${trend['current_price']:.4f}/hour
Price Volatility: {trend['volatility_percentage']:.1f}%
Recommendation: {trend['recommendation']}
"""
                
                # Risk assessment
                risk_level = self._assess_workload_risk(config.workload_type)
                report += f"""
RISK ASSESSMENT:
Workload Suitability: {risk_level}
Interruption Handling: {config.interruption_behavior}
Multi-AZ Strategy: {'YES' if len(config.availability_zones) > 1 else 'NO'}
"""
            
            report += f"""

OVERALL SUMMARY
==============
Total Monthly Savings: ${total_monthly_savings:.2f}
Total Annual Savings: ${total_annual_savings:.2f}
Number of Configurations: {len(configs)}

MUMBAI CONTEXT ANALYSIS
======================
Spot instances आपके लिए बिल्कुल Mumbai auto bargaining जैसा है:

🚗 AGGRESSIVE Strategy = "Meter se kam chalega?"
   - सबसे कम price, लेकिन risk है availability का
   - Perfect for: Batch jobs, CI/CD builds

🛵 BALANCED Strategy = "Thoda reasonable rate do"
   - Moderate price, better availability
   - Perfect for: Development environments, non-critical services

🚕 CONSERVATIVE Strategy = "Ok, fixed rate pe chalo"
   - Higher price but guaranteed availability
   - Perfect for: Production workloads with some fault tolerance

RECOMMENDATIONS
==============
1. Start with non-critical workloads for spot adoption
2. Always use multiple availability zones
3. Implement proper interruption handling
4. Monitor pricing trends weekly
5. Use spot fleet for better fault tolerance

NEXT STEPS
==========
1. Pilot with batch processing workloads
2. Implement interruption monitoring
3. Set up automated recovery procedures  
4. Create cost alerting for unexpected price spikes
5. Review and optimize bidding strategies monthly

Contact: Hindi Tech Community for implementation support
"""
            
            logger.info("Generated comprehensive spot instance report")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate spot report: {e}")
            return f"Error generating report: {e}"

    def _assess_workload_risk(self, workload_type: WorkloadType) -> str:
        """Assess risk level for workload type on spot instances"""
        risk_assessments = {
            WorkloadType.BATCH_PROCESSING: "LOW RISK: Fault tolerant, can handle interruptions",
            WorkloadType.CI_CD: "LOW RISK: Build jobs can be restarted easily", 
            WorkloadType.DATA_ANALYTICS: "MEDIUM RISK: Long-running jobs, checkpoint needed",
            WorkloadType.ML_TRAINING: "MEDIUM RISK: Training can be checkpointed and resumed",
            WorkloadType.WEB_SERVICES: "HIGH RISK: Requires proper load balancer integration"
        }
        return risk_assessments.get(workload_type, "UNKNOWN RISK")

    def cleanup(self):
        """Cleanup resources and stop monitoring"""
        self.monitoring_enabled = False
        if hasattr(self, 'monitoring_thread'):
            self.monitoring_thread.join(timeout=5)
        logger.info("Spot Instance Manager cleaned up")

# Usage Example
def main():
    """
    Production usage example
    
    Mumbai Context: Complete spot instance strategy setup
    """
    try:
        # Initialize manager
        print("🎯 Initializing Spot Instance Manager...")
        manager = SpotInstanceManager()
        
        # Define spot configurations
        configurations = [
            SpotInstanceConfig(
                instance_type='t3.large',
                max_price=0.05,  # Max willing to pay per hour
                min_instances=1,
                max_instances=3,
                availability_zones=['us-east-1a', 'us-east-1b', 'us-east-1c'],
                strategy=SpotStrategy.BALANCED,
                workload_type=WorkloadType.BATCH_PROCESSING,
                interruption_behavior='terminate'
            ),
            SpotInstanceConfig(
                instance_type='c5.xlarge',
                max_price=0.10,
                min_instances=1,
                max_instances=2,
                availability_zones=['us-east-1a', 'us-east-1b'],
                strategy=SpotStrategy.CONSERVATIVE,
                workload_type=WorkloadType.WEB_SERVICES,
                interruption_behavior='stop'
            )
        ]
        
        print("📊 Analyzing spot pricing trends...")
        
        # Analyze pricing for each configuration
        for config in configurations:
            print(f"\n🔍 Analyzing {config.instance_type}:")
            
            # Get price history
            price_history = asyncio.run(manager.get_spot_price_history([config.instance_type]))
            print(f"Retrieved {len(price_history)} price records")
            
            # Analyze trends  
            trends = manager.analyze_spot_price_trends(price_history)
            if config.instance_type in trends:
                trend = trends[config.instance_type]
                print(f"Current Price: ${trend['current_price']:.4f}/hour")
                print(f"Average Price: ${trend['average_price']:.4f}/hour") 
                print(f"Volatility: {trend['volatility_percentage']:.1f}%")
                print(f"Recommendation: {trend['recommendation']}")
            
            # Calculate savings
            savings = manager.calculate_spot_savings(config)
            print(f"Monthly Savings: ${savings.get('monthly_savings', 0):.2f}")
            print(f"Savings Percentage: {savings.get('savings_percentage', 0):.1f}%")
        
        # Generate comprehensive report
        print("\n📄 Generating spot instance analysis report...")
        report = manager.generate_spot_report(configurations)
        
        # Save report
        with open('spot_instance_report.txt', 'w') as f:
            f.write(report)
        
        print("✅ Spot instance analysis completed!")
        print("📄 Report saved to spot_instance_report.txt")
        
        # Show Mumbai style summary
        print(f"\n🚗 Mumbai Auto Analogy Summary:")
        total_monthly_savings = sum(
            manager.calculate_spot_savings(config).get('monthly_savings', 0) 
            for config in configurations
        )
        
        if total_monthly_savings > 500:
            print("💰 EXCELLENT: Like getting auto rides at 50% discount daily!")
        elif total_monthly_savings > 200:
            print("👍 GOOD: Like bargaining successfully for most rides!")
        else:
            print("🤔 MODERATE: Some savings, but room for optimization!")
        
        print(f"Total Monthly Savings: ${total_monthly_savings:.2f}")
        
        # Cleanup
        manager.cleanup()
        
    except Exception as e:
        logger.error(f"Spot instance analysis failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

"""
Production Implementation Guide (Hindi):
========================================

1. Interruption Monitoring:
   - CloudWatch Events for spot interruption warnings
   - Custom scripts on instances for metadata API monitoring
   - Graceful shutdown procedures for each workload type

2. Recovery Automation:
   - Auto Scaling Groups with mixed instance types
   - Application Load Balancer health checks
   - Database checkpointing for stateful workloads

3. Mumbai Business Context:
   - Peak vs off-peak pricing patterns (like Mumbai traffic)
   - Regional availability (Mumbai vs other cities)
   - Cultural adaptation (bargaining mentality)

4. Integration Points:
   - Jenkins for CI/CD spot builds
   - Kubernetes for container workloads
   - EMR for big data processing
   - SageMaker for ML training

5. Monitoring & Alerting:
   - Cost anomaly detection
   - Availability zone health monitoring
   - Price trend alerting
   - Interruption rate tracking

यह system आपके cloud costs को Mumbai की smart commuting की तरह optimize करेगा!
"""
#!/usr/bin/env python3
"""
Example 11: Cost Optimization Automation
यह script AWS resources की cost को optimize करती है
Flipkart जैसे scale पर cost savings के लिए
"""

import boto3
import json
import csv
import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FlipkartCostOptimizer:
    """
    Flipkart Infrastructure Cost Optimization Tool
    इस class का use करके हम अपने AWS bill को significantly reduce कर सकते हैं
    """
    
    def __init__(self, region: str = 'ap-south-1'):
        """Initialize AWS clients for Mumbai region"""
        self.region = region
        self.ec2 = boto3.client('ec2', region_name=region)
        self.rds = boto3.client('rds', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer only in us-east-1
        self.pricing = boto3.client('pricing', region_name='us-east-1')
        
        # Cost optimization settings
        self.optimization_settings = {
            'cpu_threshold_low': 5,      # Below 5% CPU is underutilized
            'cpu_threshold_high': 80,    # Above 80% might need larger instance
            'memory_threshold_low': 20,  # Below 20% memory is underutilized
            'network_threshold_low': 100, # Below 100 KB/s network is low
            'max_monthly_savings': 50000, # Maximum monthly savings target (INR)
            'business_hours': {
                'start': 9,  # 9 AM IST
                'end': 21,   # 9 PM IST
                'timezone': 'Asia/Kolkata'
            }
        }
        
        logger.info(f"Initialized Cost Optimizer for region: {region}")
    
    def get_cost_and_usage(self, days: int = 30) -> Dict[str, Any]:
        """
        Get cost and usage data for last N days
        पिछले N दिनों का cost data निकालता है
        """
        try:
            end_date = datetime.datetime.now().date()
            start_date = end_date - datetime.timedelta(days=days)
            
            response = self.ce.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'INSTANCE_TYPE'}
                ]
            )
            
            logger.info(f"Retrieved cost data for {days} days")
            return response
            
        except Exception as e:
            logger.error(f"Error getting cost data: {str(e)}")
            return {}
    
    def analyze_ec2_utilization(self) -> List[Dict[str, Any]]:
        """
        Analyze EC2 instance utilization and find optimization opportunities
        EC2 instances की utilization check करता है और optimization suggest करता है
        """
        recommendations = []
        
        try:
            # Get all running instances
            instances = self.ec2.describe_instances(
                Filters=[
                    {'Name': 'instance-state-name', 'Values': ['running']},
                    {'Name': 'tag:Project', 'Values': ['flipkart']}
                ]
            )
            
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']
                    
                    # Get CPU utilization for last 7 days
                    cpu_metrics = self._get_cloudwatch_metrics(
                        instance_id, 'CPUUtilization', 7
                    )
                    
                    # Get memory utilization if available
                    memory_metrics = self._get_cloudwatch_metrics(
                        instance_id, 'MemoryUtilization', 7
                    )
                    
                    # Analyze utilization
                    avg_cpu = self._calculate_average(cpu_metrics)
                    avg_memory = self._calculate_average(memory_metrics)
                    
                    recommendation = self._generate_ec2_recommendation(
                        instance_id, instance_type, avg_cpu, avg_memory
                    )
                    
                    if recommendation:
                        recommendations.append(recommendation)
            
            logger.info(f"Analyzed {len(recommendations)} EC2 optimization opportunities")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error analyzing EC2 utilization: {str(e)}")
            return []
    
    def analyze_rds_utilization(self) -> List[Dict[str, Any]]:
        """
        Analyze RDS instance utilization
        RDS database instances की utilization और cost optimization check करता है
        """
        recommendations = []
        
        try:
            # Get all RDS instances
            db_instances = self.rds.describe_db_instances()
            
            for db_instance in db_instances['DBInstances']:
                db_instance_id = db_instance['DBInstanceIdentifier']
                db_instance_class = db_instance['DBInstanceClass']
                engine = db_instance['Engine']
                
                # Get CPU utilization
                cpu_metrics = self._get_cloudwatch_metrics(
                    db_instance_id, 'CPUUtilization', 7, namespace='AWS/RDS'
                )
                
                # Get connection count
                connection_metrics = self._get_cloudwatch_metrics(
                    db_instance_id, 'DatabaseConnections', 7, namespace='AWS/RDS'
                )
                
                avg_cpu = self._calculate_average(cpu_metrics)
                avg_connections = self._calculate_average(connection_metrics)
                
                recommendation = self._generate_rds_recommendation(
                    db_instance_id, db_instance_class, engine, avg_cpu, avg_connections
                )
                
                if recommendation:
                    recommendations.append(recommendation)
            
            logger.info(f"Analyzed {len(recommendations)} RDS optimization opportunities")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error analyzing RDS utilization: {str(e)}")
            return []
    
    def analyze_s3_storage(self) -> List[Dict[str, Any]]:
        """
        Analyze S3 storage usage and lifecycle policies
        S3 storage की cost optimization के लिए lifecycle policies suggest करता है
        """
        recommendations = []
        
        try:
            # Get all S3 buckets
            buckets = self.s3.list_buckets()
            
            for bucket in buckets['Buckets']:
                bucket_name = bucket['Name']
                
                # Skip if not a Flipkart bucket
                if 'flipkart' not in bucket_name.lower():
                    continue
                
                # Get bucket metrics from CloudWatch
                bucket_metrics = self._get_s3_bucket_metrics(bucket_name)
                
                # Analyze storage classes
                storage_analysis = self._analyze_s3_storage_classes(bucket_name)
                
                recommendation = self._generate_s3_recommendation(
                    bucket_name, bucket_metrics, storage_analysis
                )
                
                if recommendation:
                    recommendations.append(recommendation)
            
            logger.info(f"Analyzed {len(recommendations)} S3 optimization opportunities")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error analyzing S3 storage: {str(e)}")
            return []
    
    def implement_scheduling_automation(self) -> Dict[str, Any]:
        """
        Implement resource scheduling for development environments
        Development environments के लिए automatic start/stop scheduling implement करता है
        """
        try:
            lambda_function_code = self._create_scheduling_lambda_code()
            
            # Create Lambda function for resource scheduling
            lambda_arn = self._create_lambda_function(
                'flipkart-resource-scheduler',
                lambda_function_code,
                'Schedule EC2 and RDS instances based on business hours'
            )
            
            # Create CloudWatch Events rule
            rule_arn = self._create_cloudwatch_rule(
                'flipkart-start-resources',
                'cron(30 3 * * MON-FRI *)',  # 9 AM IST (3:30 UTC)
                lambda_arn,
                {'action': 'start'}
            )
            
            stop_rule_arn = self._create_cloudwatch_rule(
                'flipkart-stop-resources', 
                'cron(30 15 * * MON-FRI *)',  # 9 PM IST (15:30 UTC)
                lambda_arn,
                {'action': 'stop'}
            )
            
            return {
                'lambda_arn': lambda_arn,
                'start_rule_arn': rule_arn,
                'stop_rule_arn': stop_rule_arn,
                'estimated_monthly_savings': self._calculate_scheduling_savings()
            }
            
        except Exception as e:
            logger.error(f"Error implementing scheduling automation: {str(e)}")
            return {}
    
    def generate_cost_report(self) -> str:
        """
        Generate comprehensive cost optimization report
        Complete cost optimization report generate करता है
        """
        try:
            report_date = datetime.datetime.now().strftime('%Y-%m-%d')
            
            # Collect all recommendations
            ec2_recommendations = self.analyze_ec2_utilization()
            rds_recommendations = self.analyze_rds_utilization()
            s3_recommendations = self.analyze_s3_storage()
            
            # Calculate potential savings
            total_savings = self._calculate_total_savings(
                ec2_recommendations + rds_recommendations + s3_recommendations
            )
            
            # Generate report
            report = self._generate_html_report(
                ec2_recommendations,
                rds_recommendations, 
                s3_recommendations,
                total_savings,
                report_date
            )
            
            # Save report to file
            report_filename = f'flipkart_cost_optimization_report_{report_date}.html'
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"Cost optimization report generated: {report_filename}")
            return report_filename
            
        except Exception as e:
            logger.error(f"Error generating cost report: {str(e)}")
            return ""
    
    def _get_cloudwatch_metrics(self, resource_id: str, metric_name: str, 
                               days: int, namespace: str = 'AWS/EC2') -> List[float]:
        """Get CloudWatch metrics for a resource"""
        try:
            end_time = datetime.datetime.utcnow()
            start_time = end_time - datetime.timedelta(days=days)
            
            response = self.cloudwatch.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': 'InstanceId' if namespace == 'AWS/EC2' else 'DBInstanceIdentifier',
                        'Value': resource_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour intervals
                Statistics=['Average']
            )
            
            return [point['Average'] for point in response['Datapoints']]
            
        except Exception as e:
            logger.warning(f"Could not get metrics for {resource_id}: {str(e)}")
            return []
    
    def _calculate_average(self, values: List[float]) -> float:
        """Calculate average of a list of values"""
        if not values:
            return 0.0
        return sum(values) / len(values)
    
    def _generate_ec2_recommendation(self, instance_id: str, instance_type: str,
                                   avg_cpu: float, avg_memory: float) -> Dict[str, Any]:
        """Generate EC2 optimization recommendation"""
        recommendation = None
        
        # Underutilized instance
        if avg_cpu < self.optimization_settings['cpu_threshold_low']:
            # Suggest smaller instance type
            smaller_type = self._get_smaller_instance_type(instance_type)
            if smaller_type:
                monthly_savings = self._calculate_ec2_savings(instance_type, smaller_type)
                recommendation = {
                    'resource_id': instance_id,
                    'resource_type': 'EC2',
                    'current_type': instance_type,
                    'recommendation': f'Downsize to {smaller_type}',
                    'reason': f'Low CPU utilization: {avg_cpu:.1f}%',
                    'monthly_savings_usd': monthly_savings,
                    'monthly_savings_inr': monthly_savings * 83,  # Approximate USD to INR
                    'priority': 'High' if monthly_savings > 50 else 'Medium'
                }
        
        # Over-utilized instance
        elif avg_cpu > self.optimization_settings['cpu_threshold_high']:
            larger_type = self._get_larger_instance_type(instance_type)
            if larger_type:
                recommendation = {
                    'resource_id': instance_id,
                    'resource_type': 'EC2',
                    'current_type': instance_type,
                    'recommendation': f'Upsize to {larger_type}',
                    'reason': f'High CPU utilization: {avg_cpu:.1f}%',
                    'monthly_cost_increase_usd': self._calculate_ec2_savings(instance_type, larger_type),
                    'priority': 'High',
                    'note': 'Performance improvement, not cost saving'
                }
        
        return recommendation
    
    def _generate_rds_recommendation(self, db_instance_id: str, db_instance_class: str,
                                   engine: str, avg_cpu: float, avg_connections: float) -> Dict[str, Any]:
        """Generate RDS optimization recommendation"""
        recommendation = None
        
        if avg_cpu < self.optimization_settings['cpu_threshold_low']:
            smaller_class = self._get_smaller_rds_class(db_instance_class)
            if smaller_class:
                monthly_savings = self._calculate_rds_savings(db_instance_class, smaller_class)
                recommendation = {
                    'resource_id': db_instance_id,
                    'resource_type': 'RDS',
                    'current_class': db_instance_class,
                    'recommendation': f'Downsize to {smaller_class}',
                    'reason': f'Low CPU utilization: {avg_cpu:.1f}%, Average connections: {avg_connections:.0f}',
                    'monthly_savings_usd': monthly_savings,
                    'monthly_savings_inr': monthly_savings * 83,
                    'priority': 'High' if monthly_savings > 100 else 'Medium'
                }
        
        return recommendation
    
    def _generate_s3_recommendation(self, bucket_name: str, bucket_metrics: Dict,
                                  storage_analysis: Dict) -> Dict[str, Any]:
        """Generate S3 optimization recommendation"""
        recommendation = None
        
        # Check if lifecycle policy exists
        if not storage_analysis.get('has_lifecycle_policy', False):
            estimated_savings = storage_analysis.get('potential_savings', 0)
            recommendation = {
                'resource_id': bucket_name,
                'resource_type': 'S3',
                'recommendation': 'Implement lifecycle policy',
                'reason': 'No lifecycle policy found',
                'monthly_savings_usd': estimated_savings,
                'monthly_savings_inr': estimated_savings * 83,
                'priority': 'Medium',
                'suggested_policy': {
                    'transition_to_ia_days': 30,
                    'transition_to_glacier_days': 90,
                    'delete_after_days': 2555  # 7 years for compliance
                }
            }
        
        return recommendation
    
    def _create_scheduling_lambda_code(self) -> str:
        """Create Lambda function code for resource scheduling"""
        return '''
import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function to start/stop Flipkart development resources
    यह function development environment के resources को business hours के अनुसार start/stop करता है
    """
    
    action = event.get('action', 'start')
    region = 'ap-south-1'
    
    ec2 = boto3.client('ec2', region_name=region)
    rds = boto3.client('rds', region_name=region)
    
    results = {
        'ec2_instances': [],
        'rds_instances': [],
        'errors': []
    }
    
    try:
        # Handle EC2 instances
        if action == 'start':
            instances = ec2.describe_instances(
                Filters=[
                    {'Name': 'instance-state-name', 'Values': ['stopped']},
                    {'Name': 'tag:Environment', 'Values': ['development', 'staging']},
                    {'Name': 'tag:Project', 'Values': ['flipkart']},
                    {'Name': 'tag:AutoSchedule', 'Values': ['true']}
                ]
            )
            
            instance_ids = []
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_ids.append(instance['InstanceId'])
            
            if instance_ids:
                ec2.start_instances(InstanceIds=instance_ids)
                results['ec2_instances'] = instance_ids
                logger.info(f"Started {len(instance_ids)} EC2 instances")
        
        elif action == 'stop':
            instances = ec2.describe_instances(
                Filters=[
                    {'Name': 'instance-state-name', 'Values': ['running']},
                    {'Name': 'tag:Environment', 'Values': ['development', 'staging']},
                    {'Name': 'tag:Project', 'Values': ['flipkart']},
                    {'Name': 'tag:AutoSchedule', 'Values': ['true']}
                ]
            )
            
            instance_ids = []
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_ids.append(instance['InstanceId'])
            
            if instance_ids:
                ec2.stop_instances(InstanceIds=instance_ids)
                results['ec2_instances'] = instance_ids
                logger.info(f"Stopped {len(instance_ids)} EC2 instances")
        
        # Handle RDS instances (similar logic)
        db_instances = rds.describe_db_instances()
        
        for db_instance in db_instances['DBInstances']:
            if (db_instance.get('TagList', []) and 
                any(tag['Key'] == 'Environment' and tag['Value'] in ['development', 'staging'] 
                    for tag in db_instance.get('TagList', [])) and
                any(tag['Key'] == 'AutoSchedule' and tag['Value'] == 'true' 
                    for tag in db_instance.get('TagList', []))):
                
                db_id = db_instance['DBInstanceIdentifier']
                db_status = db_instance['DBInstanceStatus']
                
                if action == 'start' and db_status == 'stopped':
                    rds.start_db_instance(DBInstanceIdentifier=db_id)
                    results['rds_instances'].append(db_id)
                elif action == 'stop' and db_status == 'available':
                    rds.stop_db_instance(DBInstanceIdentifier=db_id)
                    results['rds_instances'].append(db_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
        
    except Exception as e:
        logger.error(f"Error in scheduling: {str(e)}")
        results['errors'].append(str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(results)
        }
'''
    
    # Helper methods for instance type recommendations
    def _get_smaller_instance_type(self, current_type: str) -> str:
        """Get smaller instance type recommendation"""
        size_mapping = {
            't3.large': 't3.medium',
            't3.medium': 't3.small',
            't3.small': 't3.micro',
            't3.xlarge': 't3.large',
            'm5.large': 'm5.medium',
            'm5.xlarge': 'm5.large',
            'c5.large': 'c5.medium',
            'c5.xlarge': 'c5.large'
        }
        return size_mapping.get(current_type, '')
    
    def _get_larger_instance_type(self, current_type: str) -> str:
        """Get larger instance type recommendation"""
        size_mapping = {
            't3.micro': 't3.small',
            't3.small': 't3.medium',
            't3.medium': 't3.large',
            't3.large': 't3.xlarge',
            'm5.medium': 'm5.large',
            'm5.large': 'm5.xlarge'
        }
        return size_mapping.get(current_type, '')
    
    def _calculate_total_savings(self, recommendations: List[Dict]) -> Dict[str, float]:
        """Calculate total potential savings"""
        total_usd = sum(r.get('monthly_savings_usd', 0) for r in recommendations)
        total_inr = total_usd * 83
        
        return {
            'monthly_usd': total_usd,
            'monthly_inr': total_inr,
            'yearly_usd': total_usd * 12,
            'yearly_inr': total_inr * 12
        }
    
    def _generate_html_report(self, ec2_recs: List, rds_recs: List, s3_recs: List,
                            total_savings: Dict, report_date: str) -> str:
        """Generate HTML cost optimization report"""
        
        html_template = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flipkart Cost Optimization Report - {report_date}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #ff6600; color: white; padding: 20px; border-radius: 8px; }}
        .summary {{ background-color: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .recommendation {{ background-color: white; margin: 10px 0; padding: 15px; border-left: 4px solid #ff6600; }}
        .savings {{ font-size: 24px; font-weight: bold; color: #00aa00; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .high-priority {{ border-left-color: #ff0000; }}
        .medium-priority {{ border-left-color: #ffaa00; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏪 Flipkart Infrastructure Cost Optimization Report</h1>
        <p>Generated on: {report_date}</p>
        <p>Region: Mumbai (ap-south-1)</p>
    </div>
    
    <div class="summary">
        <h2>💰 Potential Monthly Savings</h2>
        <div class="savings">
            ₹{total_savings['monthly_inr']:,.0f} / ${total_savings['monthly_usd']:,.0f}
        </div>
        <p>Yearly Potential: ₹{total_savings['yearly_inr']:,.0f} / ${total_savings['yearly_usd']:,.0f}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Optimization Summary</h2>
        <ul>
            <li>EC2 Recommendations: {len(ec2_recs)}</li>
            <li>RDS Recommendations: {len(rds_recs)}</li>
            <li>S3 Recommendations: {len(s3_recs)}</li>
            <li>Total Opportunities: {len(ec2_recs) + len(rds_recs) + len(s3_recs)}</li>
        </ul>
    </div>
    
    <h2>🖥️ EC2 Optimization Recommendations</h2>
    {self._generate_recommendation_table(ec2_recs)}
    
    <h2>🗄️ RDS Optimization Recommendations</h2>
    {self._generate_recommendation_table(rds_recs)}
    
    <h2>📦 S3 Optimization Recommendations</h2>
    {self._generate_recommendation_table(s3_recs)}
    
    <div class="summary">
        <h2>📋 Implementation Priority</h2>
        <ol>
            <li><strong>High Priority:</strong> Immediate action recommended - high savings potential</li>
            <li><strong>Medium Priority:</strong> Plan for next maintenance window</li>
            <li><strong>Low Priority:</strong> Consider during next quarterly review</li>
        </ol>
        
        <h3>🔧 Next Steps</h3>
        <ul>
            <li>Review recommendations with engineering team</li>
            <li>Test changes in development environment first</li>
            <li>Schedule implementation during low-traffic hours</li>
            <li>Monitor performance after changes</li>
            <li>Run this report monthly to track optimization progress</li>
        </ul>
    </div>
    
    <footer style="margin-top: 40px; text-align: center; color: #666;">
        <p>Generated by Flipkart Infrastructure Cost Optimization Tool</p>
        <p>For questions, contact: platform-team@flipkart.com</p>
    </footer>
</body>
</html>
'''
        return html_template
    
    def _generate_recommendation_table(self, recommendations: List[Dict]) -> str:
        """Generate HTML table for recommendations"""
        if not recommendations:
            return "<p>No optimization opportunities found. Great job! 🎉</p>"
        
        table_html = '''
        <table>
            <tr>
                <th>Resource</th>
                <th>Current</th>
                <th>Recommendation</th>
                <th>Reason</th>
                <th>Monthly Savings</th>
                <th>Priority</th>
            </tr>
        '''
        
        for rec in recommendations:
            priority_class = f"{rec.get('priority', 'medium').lower()}-priority"
            savings_inr = rec.get('monthly_savings_inr', 0)
            savings_usd = rec.get('monthly_savings_usd', 0)
            
            table_html += f'''
            <tr class="{priority_class}">
                <td>{rec.get('resource_id', 'N/A')}</td>
                <td>{rec.get('current_type', rec.get('current_class', 'N/A'))}</td>
                <td>{rec.get('recommendation', 'N/A')}</td>
                <td>{rec.get('reason', 'N/A')}</td>
                <td>₹{savings_inr:,.0f} / ${savings_usd:,.0f}</td>
                <td>{rec.get('priority', 'Medium')}</td>
            </tr>
            '''
        
        table_html += '</table>'
        return table_html

def main():
    """
    Main function to run cost optimization analysis
    यह main function है जो complete cost optimization analysis run करता है
    """
    print("🏪 Starting Flipkart Cost Optimization Analysis...")
    print("=" * 60)
    
    # Initialize cost optimizer
    optimizer = FlipkartCostOptimizer(region='ap-south-1')
    
    # Generate comprehensive cost report
    report_file = optimizer.generate_cost_report()
    
    if report_file:
        print(f"✅ Cost optimization report generated: {report_file}")
        print("\n📊 Report includes:")
        print("   - EC2 instance utilization analysis")
        print("   - RDS database optimization opportunities")
        print("   - S3 storage lifecycle recommendations")
        print("   - Potential monthly and yearly savings")
        print("   - Implementation priority and next steps")
        
        # Implement scheduling automation for development
        print("\n🕒 Setting up resource scheduling automation...")
        scheduling_result = optimizer.implement_scheduling_automation()
        
        if scheduling_result:
            print("✅ Resource scheduling automation configured")
            print(f"   Estimated monthly savings: ${scheduling_result.get('estimated_monthly_savings', 0):.0f}")
        
        print(f"\n💡 Open {report_file} in your browser to view the complete report")
        print("\n🎯 Next Steps:")
        print("   1. Review recommendations with your team")
        print("   2. Test changes in development environment")
        print("   3. Implement high-priority optimizations")
        print("   4. Monitor cost impact after changes")
        print("   5. Run this analysis monthly")
        
    else:
        print("❌ Failed to generate cost optimization report")
        print("Please check logs for error details")

if __name__ == "__main__":
    main()
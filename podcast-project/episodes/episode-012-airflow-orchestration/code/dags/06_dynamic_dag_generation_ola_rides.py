#!/usr/bin/env python3
"""
Dynamic DAG Generation for Ola Ride Analytics
Focus: Runtime DAG creation, dynamic task generation, configuration-driven workflows

Ye DAG Ola ke different cities ke liye dynamically create hota hai.
Mumbai ke auto-rickshaw routes jaise flexible aur adaptive!

Production Ready: Yes
Testing Required: Yes
Dependencies: Apache Airflow, Configuration Management
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import json
import yaml
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from airflow.utils.decorators import task
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from airflow.configuration import conf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# City configuration for Ola operations
CITY_CONFIGS = {
    'mumbai': {
        'display_name': 'Mumbai',
        'timezone': 'Asia/Kolkata',
        'peak_hours': ['07:00-10:00', '18:00-21:00'],
        'zones': ['Andheri', 'Bandra', 'Lower Parel', 'Powai', 'Thane'],
        'ride_types': ['Mini', 'Prime', 'Auto', 'Bike'],
        'processing_priority': 'high',
        'data_sources': ['rides', 'drivers', 'customers', 'payments'],
        'special_events': ['local_train_strikes', 'monsoon_alerts'],
        'min_rides_threshold': 10000,
        'surge_multiplier_max': 3.0
    },
    'delhi': {
        'display_name': 'Delhi NCR',
        'timezone': 'Asia/Kolkata',
        'peak_hours': ['08:00-11:00', '17:00-20:00'],
        'zones': ['Connaught Place', 'Gurgaon', 'Noida', 'Dwarka', 'Nehru Place'],
        'ride_types': ['Mini', 'Prime', 'Auto', 'Share'],
        'processing_priority': 'high',
        'data_sources': ['rides', 'drivers', 'customers', 'payments'],
        'special_events': ['air_pollution_alerts', 'metro_disruptions'],
        'min_rides_threshold': 15000,
        'surge_multiplier_max': 4.0
    },
    'bangalore': {
        'display_name': 'Bangalore',
        'timezone': 'Asia/Kolkata',
        'peak_hours': ['08:30-10:30', '18:30-21:00'],
        'zones': ['Koramangala', 'Indiranagar', 'Whitefield', 'Electronic City', 'HSR Layout'],
        'ride_types': ['Mini', 'Prime', 'Auto', 'Share', 'Bike'],
        'processing_priority': 'medium',
        'data_sources': ['rides', 'drivers', 'customers', 'payments', 'traffic'],
        'special_events': ['tech_events', 'traffic_congestion'],
        'min_rides_threshold': 8000,
        'surge_multiplier_max': 2.5
    },
    'hyderabad': {
        'display_name': 'Hyderabad',
        'timezone': 'Asia/Kolkata',
        'peak_hours': ['09:00-11:00', '18:00-20:00'],
        'zones': ['Hitech City', 'Gachibowli', 'Begumpet', 'Secunderabad', 'Madhapur'],
        'ride_types': ['Mini', 'Prime', 'Auto', 'Share'],
        'processing_priority': 'medium',
        'data_sources': ['rides', 'drivers', 'customers', 'payments'],
        'special_events': ['metro_integration', 'it_campus_events'],
        'min_rides_threshold': 6000,
        'surge_multiplier_max': 2.0
    },
    'chennai': {
        'display_name': 'Chennai',
        'timezone': 'Asia/Kolkata',
        'peak_hours': ['08:00-10:00', '17:30-20:00'],
        'zones': ['T Nagar', 'Anna Nagar', 'Velachery', 'OMR', 'Adyar'],
        'ride_types': ['Mini', 'Prime', 'Auto', 'Share'],
        'processing_priority': 'low',
        'data_sources': ['rides', 'drivers', 'customers'],
        'special_events': ['monsoon_season', 'beach_events'],
        'min_rides_threshold': 4000,
        'surge_multiplier_max': 1.8
    }
}

def create_city_analytics_dag(city_code: str, city_config: Dict[str, Any]) -> DAG:
    """Create a dynamic DAG for city-specific Ola analytics"""
    
    dag_id = f'ola_city_analytics_{city_code}'
    
    # Dynamic DAG arguments based on city config
    default_args = {
        'owner': f'ola-{city_code}-analytics',
        'depends_on_past': False,
        'start_date': days_ago(1),
        'email': [f'analytics-{city_code}@ola.com', 'ops@ola.com'],
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 2 if city_config['processing_priority'] == 'high' else 1,
        'retry_delay': timedelta(minutes=3),
        'catchup': False
    }
    
    # Schedule based on priority
    if city_config['processing_priority'] == 'high':
        schedule_interval = '*/10 * * * *'  # Every 10 minutes
    elif city_config['processing_priority'] == 'medium':
        schedule_interval = '*/30 * * * *'  # Every 30 minutes
    else:
        schedule_interval = '0 * * * *'     # Every hour
    
    # Create DAG
    dag = DAG(
        dag_id,
        default_args=default_args,
        description=f'Dynamic Analytics DAG for {city_config["display_name"]}',
        schedule_interval=schedule_interval,
        tags=['ola', 'city-analytics', city_code, city_config['processing_priority']],
        catchup=False,
        max_active_runs=2,
        doc_md=f\"\"\"
        # Ola {city_config['display_name']} Analytics DAG
        
        **City:** {city_config['display_name']}
        **Priority:** {city_config['processing_priority'].upper()}
        **Zones:** {', '.join(city_config['zones'])}
        **Ride Types:** {', '.join(city_config['ride_types'])}
        **Peak Hours:** {', '.join(city_config['peak_hours'])}
        
        This DAG processes ride analytics for {city_config['display_name']} 
        with {len(city_config['zones'])} zones and {len(city_config['ride_types'])} ride types.
        \"\"\",
    )
    
    def create_data_ingestion_tasks() -> TaskGroup:
        """Create data ingestion tasks for each data source"""
        
        with TaskGroup(group_id='data_ingestion', dag=dag) as group:
            
            ingestion_tasks = []
            
            for data_source in city_config['data_sources']:
                
                @task(task_id=f'ingest_{data_source}_data')
                def ingest_data_source(source=data_source, city=city_code, **context):
                    """Ingest data from specific source"""
                    import random
                    
                    logger.info(f"Ingesting {source} data for {city}")
                    
                    # Simulate data ingestion with city-specific volumes
                    base_volume = {
                        'rides': city_config['min_rides_threshold'],
                        'drivers': city_config['min_rides_threshold'] // 10,
                        'customers': city_config['min_rides_threshold'] // 5,
                        'payments': city_config['min_rides_threshold'],
                        'traffic': 1000
                    }
                    
                    volume = base_volume.get(source, 1000)
                    actual_volume = random.randint(int(volume * 0.8), int(volume * 1.5))
                    
                    ingestion_result = {
                        'source': source,
                        'city': city,
                        'records_ingested': actual_volume,
                        'ingestion_timestamp': datetime.now().isoformat(),
                        'data_quality_score': random.uniform(85.0, 99.5)
                    }
                    
                    logger.info(f"Ingested {actual_volume} {source} records for {city}")
                    
                    # Store in XCom with dynamic key
                    context['task_instance'].xcom_push(
                        key=f'{source}_ingestion_result',
                        value=ingestion_result
                    )
                    
                    return ingestion_result
                
                task_instance = ingest_data_source()
                ingestion_tasks.append(task_instance)
            
            # Data validation task that depends on all ingestion tasks
            @task(task_id='validate_ingested_data')
            def validate_data_quality(**context):
                \"\"\"Validate quality of all ingested data\"\"\"
                
                validation_results = {
                    'city': city_code,
                    'validation_timestamp': datetime.now().isoformat(),
                    'source_validations': {},
                    'overall_score': 0.0,
                    'issues': []
                }
                
                total_score = 0.0
                source_count = 0
                
                for source in city_config['data_sources']:
                    try:
                        ingestion_result = context['task_instance'].xcom_pull(
                            task_ids=f'data_ingestion.ingest_{source}_data',
                            key=f'{source}_ingestion_result'
                        )
                        
                        if ingestion_result:
                            quality_score = ingestion_result['data_quality_score']
                            record_count = ingestion_result['records_ingested']
                            
                            validation_results['source_validations'][source] = {
                                'quality_score': quality_score,
                                'record_count': record_count,
                                'status': 'PASSED' if quality_score >= 90.0 else 'WARNING'
                            }
                            
                            total_score += quality_score
                            source_count += 1
                            
                            if quality_score < 90.0:
                                validation_results['issues'].append(
                                    f'{source} data quality below threshold: {quality_score:.1f}%'
                                )
                        
                    except Exception as e:
                        validation_results['source_validations'][source] = {
                            'status': 'FAILED',
                            'error': str(e)
                        }
                        validation_results['issues'].append(f'{source} validation failed: {str(e)}')
                
                if source_count > 0:
                    validation_results['overall_score'] = total_score / source_count
                
                logger.info(f"Data validation completed for {city_code}: {validation_results['overall_score']:.1f}%")
                
                return validation_results
            
            data_validation = validate_data_quality()
            
            # Set dependencies
            ingestion_tasks >> data_validation
        
        return group
    
    def create_zone_analysis_tasks() -> TaskGroup:
        \"\"\"Create zone-specific analysis tasks\"\"\"
        
        with TaskGroup(group_id='zone_analysis', dag=dag) as group:
            
            zone_tasks = []
            
            for zone in city_config['zones']:
                
                @task(task_id=f'analyze_zone_{zone.lower().replace(" ", "_")}')
                def analyze_zone_data(zone_name=zone, **context):
                    \"\"\"Analyze ride patterns for specific zone\"\"\"
                    import random
                    
                    logger.info(f"Analyzing zone data for {zone_name} in {city_code}")
                    
                    # Simulate zone analysis
                    analysis_result = {
                        'zone': zone_name,
                        'city': city_code,
                        'total_rides': random.randint(500, 2000),
                        'avg_ride_duration': random.uniform(15.0, 45.0),
                        'avg_ride_distance': random.uniform(3.0, 15.0),
                        'peak_demand_times': random.sample(city_config['peak_hours'], 1)[0],
                        'dominant_ride_type': random.choice(city_config['ride_types']),
                        'surge_incidents': random.randint(0, 5),
                        'driver_availability_score': random.uniform(70.0, 95.0),
                        'customer_rating_avg': random.uniform(4.0, 4.8),
                        'analysis_timestamp': datetime.now().isoformat()
                    }
                    
                    logger.info(f"Zone {zone_name}: {analysis_result['total_rides']} rides, "
                              f"{analysis_result['driver_availability_score']:.1f}% driver availability")
                    
                    return analysis_result
                
                zone_task = analyze_zone_data()
                zone_tasks.append(zone_task)
            
            # Aggregate zone analysis
            @task(task_id='aggregate_zone_insights')
            def aggregate_zone_analysis(**context):
                \"\"\"Aggregate insights from all zones\"\"\"
                
                zone_analyses = []
                
                for zone in city_config['zones']:
                    zone_task_id = f'zone_analysis.analyze_zone_{zone.lower().replace(" ", "_")}'
                    try:
                        zone_data = context['task_instance'].xcom_pull(task_ids=zone_task_id)
                        if zone_data:
                            zone_analyses.append(zone_data)
                    except Exception as e:
                        logger.warning(f"Failed to get data for zone {zone}: {e}")
                
                if not zone_analyses:
                    return {'error': 'No zone data available for aggregation'}
                
                # Calculate city-wide metrics
                city_metrics = {
                    'city': city_code,
                    'total_zones_analyzed': len(zone_analyses),
                    'total_rides': sum(z['total_rides'] for z in zone_analyses),
                    'avg_ride_duration': sum(z['avg_ride_duration'] for z in zone_analyses) / len(zone_analyses),
                    'avg_ride_distance': sum(z['avg_ride_distance'] for z in zone_analyses) / len(zone_analyses),
                    'total_surge_incidents': sum(z['surge_incidents'] for z in zone_analyses),
                    'overall_driver_availability': sum(z['driver_availability_score'] for z in zone_analyses) / len(zone_analyses),
                    'overall_customer_rating': sum(z['customer_rating_avg'] for z in zone_analyses) / len(zone_analyses),
                    'busiest_zone': max(zone_analyses, key=lambda x: x['total_rides'])['zone'],
                    'highest_rated_zone': max(zone_analyses, key=lambda x: x['customer_rating_avg'])['zone'],
                    'aggregation_timestamp': datetime.now().isoformat()
                }
                
                # Identify insights
                insights = []
                
                if city_metrics['total_surge_incidents'] > len(city_config['zones']) * 2:
                    insights.append('High surge activity detected across multiple zones')
                
                if city_metrics['overall_driver_availability'] < 80:
                    insights.append('Driver shortage detected - consider incentives')
                
                if city_metrics['overall_customer_rating'] < 4.2:
                    insights.append('Customer satisfaction below target - review service quality')
                
                city_metrics['insights'] = insights
                
                logger.info(f"City aggregation for {city_code}: {city_metrics['total_rides']} total rides, "
                          f"{city_metrics['overall_driver_availability']:.1f}% driver availability")
                
                return city_metrics
            
            zone_aggregation = aggregate_zone_analysis()
            
            # Dependencies
            zone_tasks >> zone_aggregation
        
        return group
    
    def create_ride_type_analysis_tasks() -> TaskGroup:
        \"\"\"Create ride type specific analysis\"\"\"
        
        with TaskGroup(group_id='ride_type_analysis', dag=dag) as group:
            
            ride_type_tasks = []
            
            for ride_type in city_config['ride_types']:
                
                @task(task_id=f'analyze_{ride_type.lower()}_rides')
                def analyze_ride_type(ride_type_name=ride_type, **context):
                    \"\"\"Analyze specific ride type performance\"\"\"
                    import random
                    
                    logger.info(f"Analyzing {ride_type_name} rides in {city_code}")
                    
                    # Ride type specific analysis
                    base_volume = city_config['min_rides_threshold'] // len(city_config['ride_types'])
                    
                    analysis = {
                        'ride_type': ride_type_name,
                        'city': city_code,
                        'total_bookings': random.randint(int(base_volume * 0.5), int(base_volume * 1.5)),
                        'completed_rides': 0,
                        'cancellation_rate': random.uniform(5.0, 25.0),
                        'avg_fare': random.uniform(50.0, 300.0),
                        'avg_waiting_time': random.uniform(2.0, 8.0),
                        'driver_earnings_avg': random.uniform(200.0, 800.0),
                        'popular_hours': random.sample(city_config['peak_hours'], 1),
                        'market_share': random.uniform(10.0, 40.0),
                        'analysis_timestamp': datetime.now().isoformat()
                    }
                    
                    # Calculate completed rides based on cancellation rate
                    analysis['completed_rides'] = int(
                        analysis['total_bookings'] * (1 - analysis['cancellation_rate'] / 100)
                    )
                    
                    # Ride type specific adjustments
                    if ride_type_name == 'Auto':
                        analysis['avg_fare'] *= 0.7  # Autos are cheaper
                        analysis['avg_waiting_time'] *= 1.2  # Longer wait times
                    elif ride_type_name == 'Prime':
                        analysis['avg_fare'] *= 1.5  # Premium pricing
                        analysis['avg_waiting_time'] *= 0.8  # Better availability
                    elif ride_type_name == 'Share':
                        analysis['avg_fare'] *= 0.6  # Shared rides cheaper
                        analysis['avg_waiting_time'] *= 1.5  # Longer matching time
                    elif ride_type_name == 'Bike':
                        analysis['avg_fare'] *= 0.5  # Cheapest option
                        analysis['avg_waiting_time'] *= 0.6  # Quick booking
                    
                    logger.info(f"{ride_type_name} analysis: {analysis['completed_rides']} rides, "
                              f"₹{analysis['avg_fare']:.0f} avg fare, {analysis['cancellation_rate']:.1f}% cancellation")
                    
                    return analysis
                
                ride_type_task = analyze_ride_type()
                ride_type_tasks.append(ride_type_task)
            
            # Ride type comparison
            @task(task_id='compare_ride_types')
            def compare_ride_type_performance(**context):
                \"\"\"Compare performance across different ride types\"\"\"
                
                ride_type_data = []
                
                for ride_type in city_config['ride_types']:
                    task_id = f'ride_type_analysis.analyze_{ride_type.lower()}_rides'
                    try:
                        data = context['task_instance'].xcom_pull(task_ids=task_id)
                        if data:
                            ride_type_data.append(data)
                    except Exception as e:
                        logger.warning(f"Failed to get {ride_type} data: {e}")
                
                if not ride_type_data:
                    return {'error': 'No ride type data available'}
                
                # Performance comparison
                comparison = {
                    'city': city_code,
                    'total_ride_types_analyzed': len(ride_type_data),
                    'most_popular': max(ride_type_data, key=lambda x: x['completed_rides'])['ride_type'],
                    'highest_revenue': max(ride_type_data, key=lambda x: x['avg_fare'])['ride_type'],
                    'fastest_booking': min(ride_type_data, key=lambda x: x['avg_waiting_time'])['ride_type'],
                    'lowest_cancellation': min(ride_type_data, key=lambda x: x['cancellation_rate'])['ride_type'],
                    'total_completed_rides': sum(r['completed_rides'] for r in ride_type_data),
                    'overall_cancellation_rate': sum(r['cancellation_rate'] * r['total_bookings'] for r in ride_type_data) / sum(r['total_bookings'] for r in ride_type_data),
                    'weighted_avg_fare': sum(r['avg_fare'] * r['completed_rides'] for r in ride_type_data) / sum(r['completed_rides'] for r in ride_type_data),
                    'comparison_timestamp': datetime.now().isoformat()
                }
                
                # Strategic recommendations
                recommendations = []
                
                # Check if cancellation rate is high for any ride type
                high_cancellation = [r for r in ride_type_data if r['cancellation_rate'] > 20]
                if high_cancellation:
                    recommendations.append(f"High cancellation rates in: {', '.join([r['ride_type'] for r in high_cancellation])}")
                
                # Check waiting times
                long_wait = [r for r in ride_type_data if r['avg_waiting_time'] > 6]
                if long_wait:
                    recommendations.append(f"Long waiting times for: {', '.join([r['ride_type'] for r in long_wait])}")
                
                # Market share analysis
                if any(r['market_share'] > 50 for r in ride_type_data):
                    dominant = max(ride_type_data, key=lambda x: x['market_share'])['ride_type']
                    recommendations.append(f"{dominant} dominates market - consider diversification")
                
                comparison['recommendations'] = recommendations
                
                logger.info(f"Ride type comparison for {city_code}: {comparison['most_popular']} most popular, "
                          f"₹{comparison['weighted_avg_fare']:.0f} weighted avg fare")
                
                return comparison
            
            ride_type_comparison = compare_ride_type_performance()
            
            # Dependencies
            ride_type_tasks >> ride_type_comparison
        
        return group
    
    def create_special_events_analysis() -> TaskGroup:
        \"\"\"Create special events analysis tasks\"\"\"
        
        with TaskGroup(group_id='special_events', dag=dag) as group:
            
            @task(task_id='analyze_special_events')
            def analyze_city_special_events(**context):
                \"\"\"Analyze impact of special events on ride patterns\"\"\"
                import random
                
                logger.info(f"Analyzing special events impact for {city_code}")
                
                events_analysis = {
                    'city': city_code,
                    'monitored_events': city_config['special_events'],
                    'analysis_timestamp': datetime.now().isoformat(),
                    'event_impacts': {}
                }
                
                for event_type in city_config['special_events']:
                    # Simulate event impact analysis
                    impact = {
                        'event_type': event_type,
                        'probability_today': random.uniform(0.0, 0.3),
                        'impact_on_demand': random.uniform(-20.0, 50.0),  # % change
                        'affected_zones': random.sample(city_config['zones'], 
                                                       random.randint(1, len(city_config['zones'])//2)),
                        'recommended_surge_multiplier': min(random.uniform(1.0, 2.0), 
                                                          city_config['surge_multiplier_max']),
                        'driver_incentive_needed': random.choice([True, False])
                    }
                    
                    events_analysis['event_impacts'][event_type] = impact
                
                # Generate alerts if needed
                alerts = []
                for event, impact in events_analysis['event_impacts'].items():
                    if impact['probability_today'] > 0.2:
                        alerts.append(f"High probability of {event} - prepare for {impact['impact_on_demand']:.0f}% demand change")
                    
                    if impact['driver_incentive_needed']:
                        alerts.append(f"Driver incentives recommended for {event} in {', '.join(impact['affected_zones'])}")
                
                events_analysis['alerts'] = alerts
                
                logger.info(f"Special events analysis for {city_code}: {len(alerts)} alerts generated")
                
                return events_analysis
            
            special_events_task = analyze_special_events()
        
        return group
    
    # Create final reporting task
    @task(task_id='generate_city_report')
    def generate_comprehensive_city_report(**context):
        \"\"\"Generate comprehensive report for the city\"\"\"
        
        report = {
            'city_code': city_code,
            'city_name': city_config['display_name'],
            'report_timestamp': datetime.now().isoformat(),
            'dag_execution_date': context['ds'],
            'processing_priority': city_config['processing_priority']
        }
        
        # Collect data from all task groups
        try:
            # Data validation results
            validation_data = context['task_instance'].xcom_pull(
                task_ids='data_ingestion.validate_ingested_data'
            )
            report['data_quality'] = validation_data
            
            # Zone analysis aggregation
            zone_data = context['task_instance'].xcom_pull(
                task_ids='zone_analysis.aggregate_zone_insights'
            )
            report['zone_analysis'] = zone_data
            
            # Ride type comparison
            ride_type_data = context['task_instance'].xcom_pull(
                task_ids='ride_type_analysis.compare_ride_types'
            )
            report['ride_type_analysis'] = ride_type_data
            
            # Special events analysis
            events_data = context['task_instance'].xcom_pull(
                task_ids='special_events.analyze_special_events'
            )
            report['special_events'] = events_data
            
        except Exception as e:
            logger.error(f"Error collecting report data: {e}")
            report['data_collection_error'] = str(e)
        
        # Generate executive summary
        summary_points = []
        
        if report.get('zone_analysis', {}).get('total_rides'):
            total_rides = report['zone_analysis']['total_rides']
            summary_points.append(f"Processed {total_rides:,} rides across {len(city_config['zones'])} zones")
        
        if report.get('data_quality', {}).get('overall_score'):
            quality_score = report['data_quality']['overall_score']
            summary_points.append(f"Data quality score: {quality_score:.1f}%")
        
        if report.get('ride_type_analysis', {}).get('most_popular'):
            popular_type = report['ride_type_analysis']['most_popular']
            summary_points.append(f"Most popular ride type: {popular_type}")
        
        if report.get('special_events', {}).get('alerts'):
            alert_count = len(report['special_events']['alerts'])
            if alert_count > 0:
                summary_points.append(f"{alert_count} special event alerts")
        
        report['executive_summary'] = summary_points
        
        logger.info(f"Generated comprehensive report for {city_code} with {len(summary_points)} summary points")
        
        return report
    
    # Create all task groups
    data_ingestion = create_data_ingestion_tasks()
    zone_analysis = create_zone_analysis_tasks()
    ride_type_analysis = create_ride_type_analysis_tasks()
    special_events = create_special_events_analysis()
    city_report = generate_comprehensive_city_report()
    
    # Set DAG structure
    data_ingestion >> [zone_analysis, ride_type_analysis, special_events] >> city_report
    
    return dag

# Generate DAGs for each city
for city_code, city_config in CITY_CONFIGS.items():
    # Create the DAG and add it to globals so Airflow can discover it
    dag_instance = create_city_analytics_dag(city_code, city_config)
    globals()[dag_instance.dag_id] = dag_instance

# Additional utility functions for DAG management
def get_active_cities() -> List[str]:
    \"\"\"Get list of active cities from configuration\"\"\"
    return list(CITY_CONFIGS.keys())

def update_city_config(city_code: str, updates: Dict[str, Any]) -> bool:
    \"\"\"Update city configuration (would be used by admin interface)\"\"\"
    if city_code in CITY_CONFIGS:
        CITY_CONFIGS[city_code].update(updates)
        logger.info(f"Updated configuration for {city_code}: {updates}")
        return True
    return False

def validate_city_config(city_config: Dict[str, Any]) -> List[str]:
    \"\"\"Validate city configuration structure\"\"\"
    required_fields = [
        'display_name', 'timezone', 'peak_hours', 'zones', 
        'ride_types', 'processing_priority', 'data_sources'
    ]
    
    errors = []
    for field in required_fields:
        if field not in city_config:
            errors.append(f"Missing required field: {field}")
    
    # Validate processing priority
    if city_config.get('processing_priority') not in ['high', 'medium', 'low']:
        errors.append("Invalid processing_priority - must be 'high', 'medium', or 'low'")
    
    # Validate lists are not empty
    for list_field in ['zones', 'ride_types', 'data_sources']:
        if not city_config.get(list_field):
            errors.append(f"{list_field} cannot be empty")
    
    return errors

# Example of how to add a new city dynamically
def add_new_city(city_code: str, city_config: Dict[str, Any]) -> bool:
    \"\"\"Add a new city configuration and create its DAG\"\"\"
    
    # Validate configuration
    errors = validate_city_config(city_config)
    if errors:
        logger.error(f"City config validation failed: {errors}")
        return False
    
    # Add to global config
    CITY_CONFIGS[city_code] = city_config
    
    # Create and register DAG
    try:
        dag_instance = create_city_analytics_dag(city_code, city_config)
        globals()[dag_instance.dag_id] = dag_instance
        logger.info(f"Successfully added new city: {city_code}")
        return True
    except Exception as e:
        logger.error(f"Failed to create DAG for {city_code}: {e}")
        # Remove from config if DAG creation failed
        if city_code in CITY_CONFIGS:
            del CITY_CONFIGS[city_code]
        return False

logger.info(f"Generated {len(CITY_CONFIGS)} dynamic DAGs for Ola city analytics")
logger.info(f"Active cities: {', '.join(CITY_CONFIGS.keys())}")

\"\"\"
Mumbai Learning Notes:
1. Dynamic DAG generation based on configuration
2. Runtime task creation with city-specific parameters
3. Configuration-driven workflow design patterns
4. Scalable architecture for multi-city operations
5. Task group organization for complex workflows
6. Indian city-specific business logic implementation
7. Flexible scheduling based on business priorities
8. Comprehensive reporting and analytics aggregation
9. Special events handling for Indian market conditions
10. Production-ready dynamic DAG management

Production Considerations:
- Store city configurations in external configuration management system
- Implement proper validation and error handling for dynamic DAGs
- Set up monitoring for dynamically generated DAGs
- Add configuration versioning and rollback capabilities
- Implement proper access controls for configuration changes
- Set up automated testing for dynamic DAG generation
- Add comprehensive logging for configuration changes
- Monitor resource usage across dynamically generated DAGs
- Implement proper cleanup for deprecated city configurations
\"\"\"
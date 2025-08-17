#!/usr/bin/env python3
"""
Mumbai Local Train Operator - Kubernetes Operator Pattern Example
Demonstrates how Mumbai's local train system can inspire Kubernetes operators

Author: Episode 092 - Advanced Container Orchestration
"""

import asyncio
import kopf
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MumbaiLocalOperator:
    """
    Mumbai Local Train inspired Kubernetes Operator
    Manages train schedules based on time, demand, and events
    """
    
    def __init__(self):
        self.train_lines = {
            'western': {
                'capacity': 1800,  # Passengers per train
                'frequency': {
                    'peak': '3min',
                    'off_peak': '6min'
                },
                'stations': ['Churchgate', 'Marine Lines', 'Charni Road', 'Grant Road', 
                           'Mumbai Central', 'Mahalaxmi', 'Lower Parel', 'Elphinstone',
                           'Dadar', 'Matunga', 'Mahim', 'Bandra', 'Khar', 'Andheri']
            },
            'central': {
                'capacity': 1600,
                'frequency': {
                    'peak': '3min', 
                    'off_peak': '7min'
                },
                'stations': ['CST', 'Masjid', 'Sandhurst Road', 'Byculla', 'Chinchpokli',
                           'Currey Road', 'Parel', 'Dadar', 'Matunga', 'Sion', 'Kurla',
                           'Ghatkopar', 'Vikhroli', 'Thane']
            },
            'harbour': {
                'capacity': 1400,
                'frequency': {
                    'peak': '4min',
                    'off_peak': '8min'  
                },
                'stations': ['CST', 'Dockyard Road', 'Reay Road', 'Cotton Green',
                           'Sewri', 'Wadala', 'Kings Circle', 'Mahim', 'Bandra',
                           'Kurla', 'Chembur', 'Govandi', 'Mankhurd']
            }
        }
        
        # Peak hours configuration
        self.peak_hours = [
            {'start': 7, 'end': 11, 'type': 'morning'},
            {'start': 17, 'end': 21, 'type': 'evening'}
        ]
        
        # Special event configurations
        self.special_events = {}

@kopf.on.create('mumbai.railway.gov.in', 'v1', 'trainschedule')
async def create_train_schedule(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """
    Create new train schedule based on requirements
    Similar to how operators create deployments based on custom resources
    """
    logger.info(f"🚂 Creating train schedule: {name}")
    
    operator = MumbaiLocalOperator()
    
    # Extract schedule requirements
    line = spec.get('line')  # western, central, harbour
    service_type = spec.get('serviceType', 'regular')  # regular, express, fast
    expected_passengers = spec.get('expectedPassengers', 1000)
    time_constraints = spec.get('timeConstraints', {})
    
    # Validate line exists
    if line not in operator.train_lines:
        return {
            'status': {
                'phase': 'failed',
                'reason': f'Invalid railway line: {line}',
                'message': 'Supported lines: western, central, harbour'
            }
        }
    
    line_config = operator.train_lines[line]
    
    # Determine current time period
    current_hour = datetime.now().hour
    is_peak_hour = any(
        peak['start'] <= current_hour <= peak['end'] 
        for peak in operator.peak_hours
    )
    
    # Calculate required trains based on demand
    trains_needed = calculate_trains_needed(
        expected_passengers, 
        line_config['capacity'], 
        is_peak_hour
    )
    
    # Create train deployment configuration
    train_deployment = await create_train_deployment(
        name, namespace, line, service_type, trains_needed, line_config
    )
    
    # Setup monitoring for the schedule
    monitoring_config = await setup_schedule_monitoring(name, namespace, line)
    
    # Calculate frequency based on demand
    frequency = calculate_frequency(is_peak_hour, trains_needed, line_config)
    
    status = {
        'phase': 'operational',
        'line': line,
        'serviceType': service_type,
        'trainsDeployed': trains_needed,
        'frequency': frequency,
        'currentMode': 'peak_hour' if is_peak_hour else 'off_peak',
        'monitoringEnabled': monitoring_config['enabled'],
        'lastUpdated': datetime.now().isoformat()
    }
    
    logger.info(f"✅ Train schedule {name} created successfully on {line} line")
    return {'status': status}

def calculate_trains_needed(passengers: int, capacity: int, is_peak: bool) -> int:
    """
    Calculate number of trains needed based on passenger demand
    Similar to how HPA calculates replicas based on metrics
    """
    # Base calculation
    base_trains = max(1, (passengers // capacity) + 1)
    
    # Peak hour multiplier (more trains for reliability)
    if is_peak:
        base_trains = int(base_trains * 1.5)
    
    # Mumbai local train operational limits
    max_trains = 50  # Maximum trains per line
    min_trains = 5   # Minimum service level
    
    return max(min_trains, min(max_trains, base_trains))

def calculate_frequency(is_peak: bool, trains_needed: int, line_config: Dict) -> str:
    """
    Calculate train frequency based on current conditions
    """
    if is_peak:
        base_frequency = 3  # 3 minutes during peak
    else:
        base_frequency = 6  # 6 minutes off-peak
    
    # Adjust frequency based on train availability
    if trains_needed > 30:
        frequency = max(2, base_frequency - 1)  # More frequent
    elif trains_needed < 10:
        frequency = base_frequency + 2  # Less frequent
    else:
        frequency = base_frequency
    
    return f"{frequency}min"

async def create_train_deployment(name: str, namespace: str, line: str, 
                                service_type: str, trains_needed: int, 
                                line_config: Dict) -> Dict:
    """
    Create Kubernetes deployment for train services
    Each train is represented as a pod
    """
    deployment_config = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': f'mumbai-local-{line}-{name}',
            'namespace': namespace,
            'labels': {
                'app': 'mumbai-local-train',
                'line': line,
                'service-type': service_type,
                'managed-by': 'mumbai-local-operator'
            }
        },
        'spec': {
            'replicas': trains_needed,
            'selector': {
                'matchLabels': {
                    'app': 'mumbai-local-train',
                    'line': line,
                    'schedule': name
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': 'mumbai-local-train',
                        'line': line,
                        'schedule': name
                    }
                },
                'spec': {
                    'containers': [{
                        'name': 'train-service',
                        'image': f'mumbai-railway/local-train:{line}-v2.1',
                        'env': [
                            {'name': 'RAILWAY_LINE', 'value': line},
                            {'name': 'SERVICE_TYPE', 'value': service_type},
                            {'name': 'CAPACITY', 'value': str(line_config['capacity'])},
                            {'name': 'STATIONS', 'value': json.dumps(line_config['stations'])},
                            {'name': 'MONSOON_MODE', 'value': 'auto'},
                            {'name': 'CROWD_MANAGEMENT', 'value': 'enabled'}
                        ],
                        'resources': {
                            'requests': {'cpu': '250m', 'memory': '512Mi'},
                            'limits': {'cpu': '500m', 'memory': '1Gi'}
                        },
                        'ports': [
                            {'containerPort': 8080, 'name': 'passenger-info'},
                            {'containerPort': 8081, 'name': 'metrics'},
                            {'containerPort': 8082, 'name': 'emergency'}
                        ],
                        'livenessProbe': {
                            'httpGet': {'path': '/health', 'port': 8080},
                            'initialDelaySeconds': 30,
                            'periodSeconds': 10
                        },
                        'readinessProbe': {
                            'httpGet': {'path': '/ready', 'port': 8080},
                            'initialDelaySeconds': 5,
                            'periodSeconds': 5
                        }
                    }],
                    'affinity': {
                        'nodeAffinity': {
                            'requiredDuringSchedulingIgnoredDuringExecution': {
                                'nodeSelectorTerms': [{
                                    'matchExpressions': [{
                                        'key': f'mumbai.railway/{line}-line',
                                        'operator': 'In',
                                        'values': ['true']
                                    }]
                                }]
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Apply deployment to Kubernetes
    await apply_kubernetes_resource(deployment_config)
    
    return {
        'deployment_name': f'mumbai-local-{line}-{name}',
        'trains_deployed': trains_needed,
        'status': 'created'
    }

async def setup_schedule_monitoring(name: str, namespace: str, line: str) -> Dict:
    """
    Setup monitoring and alerting for train schedule
    """
    # Prometheus monitoring rules
    monitoring_rules = {
        'apiVersion': 'monitoring.coreos.com/v1',
        'kind': 'PrometheusRule',
        'metadata': {
            'name': f'mumbai-local-{line}-{name}-monitoring',
            'namespace': namespace
        },
        'spec': {
            'groups': [{
                'name': f'mumbai_local_{line}_alerts',
                'rules': [
                    {
                        'alert': 'TrainDelayed',
                        'expr': f'train_departure_delay_seconds{{line="{line}"}} > 300',  # 5 min delay
                        'for': '2m',
                        'labels': {'severity': 'warning', 'line': line},
                        'annotations': {
                            'summary': f'Train delays on {line} line',
                            'description': f'Trains on {line} line are delayed by more than 5 minutes'
                        }
                    },
                    {
                        'alert': 'TrainOvercrowded',
                        'expr': f'train_passenger_count{{line="{line}"}} / train_capacity{{line="{line}"}} > 1.2',
                        'for': '1m',
                        'labels': {'severity': 'critical', 'line': line},
                        'annotations': {
                            'summary': f'Overcrowding on {line} line',
                            'description': f'Passenger count exceeds 120% of capacity on {line} line'
                        }
                    },
                    {
                        'alert': 'TrainBreakdown',
                        'expr': f'train_service_status{{line="{line}"}} == 0',
                        'for': '30s',
                        'labels': {'severity': 'critical', 'line': line},
                        'annotations': {
                            'summary': f'Train breakdown on {line} line',
                            'description': f'Train service disruption detected on {line} line'
                        }
                    }
                ]
            }]
        }
    }
    
    await apply_kubernetes_resource(monitoring_rules)
    
    return {'enabled': True, 'monitoring_rules': 3}

@kopf.timer('mumbai.railway.gov.in', 'v1', 'trainschedule', interval=60)  # Every minute
async def monitor_train_schedule(spec: Dict, status: Dict, name: str, **kwargs):
    """
    Continuous monitoring and adjustment of train schedules
    Similar to how operators reconcile desired state
    """
    line = spec.get('line')
    current_time = datetime.now()
    
    # Check for special events affecting the schedule
    special_conditions = await check_special_conditions(line, current_time)
    
    # Get current passenger demand metrics
    demand_metrics = await get_passenger_demand_metrics(line)
    
    # Determine if schedule adjustment is needed
    adjustment_needed = False
    adjustments = []
    
    # Check for monsoon conditions
    if special_conditions.get('monsoon', {}).get('heavy_rain', False):
        adjustment_needed = True
        adjustments.append({
            'type': 'monsoon_adjustment',
            'action': 'reduce_frequency',
            'reason': 'Heavy rain affecting operations'
        })
    
    # Check for overcrowding
    if demand_metrics.get('overcrowding_ratio', 0) > 1.3:
        adjustment_needed = True
        adjustments.append({
            'type': 'capacity_adjustment',
            'action': 'increase_trains',
            'reason': 'High passenger demand detected'
        })
    
    # Check for festival/event impact
    if special_conditions.get('festival_traffic', False):
        adjustment_needed = True
        adjustments.append({
            'type': 'festival_adjustment',
            'action': 'increase_frequency',
            'reason': 'Festival crowd management'
        })
    
    if adjustment_needed:
        # Apply adjustments
        await apply_schedule_adjustments(name, line, adjustments)
        
        # Update status
        updated_status = status.copy()
        updated_status.update({
            'lastAdjustment': current_time.isoformat(),
            'adjustments': adjustments,
            'specialConditions': special_conditions,
            'demandMetrics': demand_metrics
        })
        
        return {'status': updated_status}

async def check_special_conditions(line: str, current_time: datetime) -> Dict:
    """
    Check for special conditions affecting train operations
    """
    conditions = {}
    
    # Monsoon check (June to September)
    if 6 <= current_time.month <= 9:
        # Mock weather API call
        weather_data = await get_mumbai_weather()
        conditions['monsoon'] = {
            'active': True,
            'heavy_rain': weather_data.get('rainfall_mm', 0) > 50,
            'flooding_risk': weather_data.get('flood_warning', False)
        }
    
    # Festival check
    festivals = await get_mumbai_festivals(current_time)
    conditions['festival_traffic'] = len(festivals) > 0
    
    # Cricket match check (Wankhede Stadium affects Harbour line)
    if line == 'harbour':
        cricket_events = await get_cricket_schedule(current_time)
        conditions['cricket_traffic'] = len(cricket_events) > 0
    
    # Office hours check
    current_hour = current_time.hour
    conditions['office_hours'] = 9 <= current_hour <= 18
    
    return conditions

async def apply_schedule_adjustments(name: str, line: str, adjustments: List[Dict]):
    """
    Apply schedule adjustments based on real-time conditions
    """
    for adjustment in adjustments:
        adjustment_type = adjustment['type']
        action = adjustment['action']
        
        if action == 'increase_trains':
            await scale_train_deployment(name, line, scale_factor=1.3)
        elif action == 'reduce_frequency':
            await update_train_frequency(name, line, frequency_multiplier=1.5)
        elif action == 'increase_frequency':
            await update_train_frequency(name, line, frequency_multiplier=0.8)
        
        logger.info(f"Applied {adjustment_type}: {action} for {line} line schedule {name}")

async def scale_train_deployment(name: str, line: str, scale_factor: float):
    """
    Scale train deployment (add/remove trains)
    Similar to HPA scaling deployments
    """
    # Implementation would scale the Kubernetes deployment
    # This is a simplified version
    logger.info(f"Scaling {line} line trains by factor {scale_factor}")

async def update_train_frequency(name: str, line: str, frequency_multiplier: float):
    """
    Update train frequency based on conditions
    """
    logger.info(f"Updating {line} line frequency by {frequency_multiplier}x")

# Emergency handling - Mumbai local train style
@kopf.on.create('mumbai.railway.gov.in', 'v1', 'emergency')
async def handle_emergency(spec: Dict[str, Any], name: str, **kwargs):
    """
    Handle railway emergencies - immediate response required
    """
    emergency_type = spec.get('type')  # accident, technical_failure, security
    affected_line = spec.get('affectedLine')
    affected_stations = spec.get('affectedStations', [])
    severity = spec.get('severity', 'medium')  # low, medium, high, critical
    
    logger.critical(f"🚨 Emergency detected: {emergency_type} on {affected_line} line")
    
    if severity in ['high', 'critical']:
        # Stop affected services immediately
        await emergency_stop_trains(affected_line, affected_stations)
        
        # Activate backup routes
        await activate_backup_routes(affected_line, affected_stations)
        
        # Notify passengers
        await send_emergency_notifications(affected_line, emergency_type)
        
        # Alert operations team
        await alert_operations_team(emergency_type, affected_line, severity)
    
    return {
        'status': {
            'phase': 'emergency_response_activated',
            'emergencyType': emergency_type,
            'affectedLine': affected_line,
            'responseTime': datetime.now().isoformat(),
            'backupRoutesActivated': True
        }
    }

async def emergency_stop_trains(line: str, stations: List[str]):
    """Emergency stop trains on affected sections"""
    logger.critical(f"Emergency stop activated for {line} line at stations: {stations}")

async def activate_backup_routes(line: str, stations: List[str]):
    """Activate backup transportation routes"""
    logger.info(f"Activating backup routes for {line} line disruption")

async def send_emergency_notifications(line: str, emergency_type: str):
    """Send emergency notifications to passengers"""
    logger.info(f"Sending emergency notifications for {line} line - {emergency_type}")

async def alert_operations_team(emergency_type: str, line: str, severity: str):
    """Alert operations team about emergency"""
    logger.critical(f"Operations team alerted: {emergency_type} on {line} line - {severity}")

# Helper functions (mock implementations)
async def apply_kubernetes_resource(resource_config: Dict):
    """Apply Kubernetes resource configuration"""
    # In real implementation, this would use Kubernetes API
    logger.info(f"Applied Kubernetes resource: {resource_config['kind']}")

async def get_mumbai_weather() -> Dict:
    """Get current Mumbai weather conditions"""
    # Mock weather data
    return {
        'rainfall_mm': 25,
        'flood_warning': False,
        'temperature': 28,
        'humidity': 85
    }

async def get_mumbai_festivals(current_time: datetime) -> List[str]:
    """Get current festivals affecting Mumbai traffic"""
    # Mock festival data
    festivals = []
    if current_time.month == 8:  # Ganesh Chaturthi season
        festivals.append('Ganesh Chaturthi')
    return festivals

async def get_cricket_schedule(current_time: datetime) -> List[Dict]:
    """Get cricket match schedule affecting Harbour line"""
    # Mock cricket schedule
    return []

async def get_passenger_demand_metrics(line: str) -> Dict:
    """Get real-time passenger demand metrics"""
    # Mock demand metrics
    return {
        'current_passengers': 15000,
        'capacity_utilization': 0.85,
        'overcrowding_ratio': 1.1,
        'average_wait_time': '4min'
    }

if __name__ == "__main__":
    # This would normally be run by kopf
    print("Mumbai Local Train Operator - Kubernetes Controller")
    print("Inspired by Mumbai's efficient local train system")
    print("Run with: kopf run mumbai-local-operator.py")
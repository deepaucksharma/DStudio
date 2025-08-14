#!/usr/bin/env python3
"""
IoT Edge Gateway - आईओटी एज गेटवे
Mumbai building society security system की तरह - सभी IoT devices का central management

Real-world inspired by AWS IoT Greengrass, Azure IoT Edge, Google Cloud IoT Core
Use cases: Smart city sensors, industrial monitoring, home automation
Cost: Edge processing ₹1 per device vs Cloud processing ₹10 per device monthly
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque
import statistics
import hashlib
import uuid
import random
import sqlite3
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """Types of IoT devices"""
    SENSOR = "सेंसर"              # Temperature, humidity, light sensors
    ACTUATOR = "एक्चुएटर"         # Motors, switches, valves
    CAMERA = "कैमरा"              # Security/monitoring cameras  
    SMART_METER = "स्मार्ट मीटर"    # Electricity, water, gas meters
    BEACON = "बीकन"               # Bluetooth/WiFi beacons
    CONTROLLER = "नियंत्रक"        # Industrial controllers
    TRACKER = "ट्रैकर"             # GPS/location trackers

class DeviceStatus(Enum):
    """IoT device status"""
    ONLINE = "ऑनलाइन"           # Device is online and responsive
    OFFLINE = "ऑफलाइन"          # Device is not responding
    MAINTENANCE = "रखरखाव"       # Device in maintenance mode
    ERROR = "त्रुटि"             # Device has errors
    LOW_BATTERY = "कम बैटरी"      # Device battery is low

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = "निम्न"               # Low priority (sensor readings)
    NORMAL = "सामान्य"           # Normal priority (regular updates)
    HIGH = "उच्च"               # High priority (alerts)
    CRITICAL = "गंभीर"           # Critical priority (emergencies)

class ProcessingMode(Enum):
    """Data processing modes"""
    REAL_TIME = "रियल-टाइम"      # Process immediately
    BATCH = "बैच"                # Process in batches
    EDGE_ONLY = "केवल एज"        # Process only at edge
    CLOUD_SYNC = "क्लाउड सिंक"     # Sync with cloud

@dataclass
class IoTDevice:
    """IoT device representation"""
    device_id: str
    device_name: str
    device_type: DeviceType
    mac_address: str
    ip_address: Optional[str]
    firmware_version: str
    location: str
    status: DeviceStatus = DeviceStatus.OFFLINE
    last_seen: Optional[datetime] = None
    battery_level: Optional[float] = None  # 0-100%
    signal_strength: Optional[int] = None  # RSSI in dBm
    data_rate: float = 0.0  # Messages per minute
    total_messages: int = 0
    error_count: int = 0
    
    def __post_init__(self):
        self.device_hash = hashlib.md5(f"{self.device_id}_{self.mac_address}".encode()).hexdigest()[:8]

@dataclass
class IoTMessage:
    """IoT message/telemetry data"""
    message_id: str
    device_id: str
    timestamp: datetime
    message_type: str  # telemetry, command, event, alert
    priority: MessagePriority
    payload: Dict[str, Any]
    size_bytes: int = 0
    processing_mode: ProcessingMode = ProcessingMode.REAL_TIME
    processed: bool = False
    cloud_synced: bool = False
    
    def __post_init__(self):
        if self.size_bytes == 0:
            self.size_bytes = len(json.dumps(self.payload).encode('utf-8'))

@dataclass
class EdgeRule:
    """Edge processing rule"""
    rule_id: str
    name: str
    description: str
    device_filter: Optional[str] = None  # Device ID pattern
    message_filter: Optional[str] = None  # Message type pattern
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True
    execution_count: int = 0

class IoTEdgeGateway:
    """
    IoT Edge Gateway - Mumbai society security control room की तरह
    सभी IoT devices को manage करना और intelligent processing करना
    """
    
    def __init__(self, gateway_id: str, location: str = "Mumbai", max_devices: int = 1000):
        """
        Initialize IoT Edge Gateway
        Args:
            gateway_id: Unique gateway identifier
            location: Geographic location
            max_devices: Maximum number of devices this gateway can handle
        """
        self.gateway_id = gateway_id
        self.location = location
        self.max_devices = max_devices
        
        # Device management
        self.connected_devices: Dict[str, IoTDevice] = {}
        self.device_discovery_enabled = True
        
        # Message processing
        self.message_queue = asyncio.Queue(maxsize=10000)
        self.processed_messages: deque = deque(maxlen=50000)
        self.message_buffer: Dict[str, List[IoTMessage]] = defaultdict(list)
        
        # Edge processing rules
        self.processing_rules: Dict[str, EdgeRule] = {}
        self.rule_engine_enabled = True
        
        # Local storage
        self.db_path = f"iot_gateway_{gateway_id}.db"
        self.db_connection = None
        
        # Performance metrics
        self.stats = {
            'total_devices': 0,
            'active_devices': 0,
            'total_messages': 0,
            'processed_messages': 0,
            'cloud_synced_messages': 0,
            'bytes_processed': 0,
            'rule_executions': 0,
            'alerts_generated': 0,
            'device_discoveries': 0,
            'uptime_start': datetime.now(),
            'message_rates': deque(maxlen=300),  # Last 5 minutes
            'processing_times': deque(maxlen=1000),
            'error_counts': defaultdict(int)
        }
        
        # Threading and async
        self.running = False
        self.worker_tasks = []
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Mumbai-specific IoT scenarios
        self._initialize_mumbai_rules()
        
        logger.info(f"IoT Edge Gateway initialized: {gateway_id} @ {location}")
    
    def _initialize_mumbai_rules(self):
        """Initialize Mumbai-specific IoT processing rules"""
        
        # Rule 1: Temperature alert for servers/equipment
        temp_alert_rule = EdgeRule(
            rule_id="mumbai_temp_alert",
            name="High Temperature Alert",
            description="Alert when temperature sensors exceed safe limits",
            device_filter="temp_sensor_*",
            message_filter="telemetry",
            conditions=[
                {
                    'field': 'temperature',
                    'operator': '>',
                    'value': 35.0,  # 35°C threshold for Mumbai climate
                    'unit': 'celsius'
                }
            ],
            actions=[
                {
                    'type': 'alert',
                    'severity': 'high',
                    'message': 'Temperature threshold exceeded in Mumbai heat'
                },
                {
                    'type': 'command',
                    'target': 'cooling_system',
                    'action': 'increase_cooling'
                }
            ]
        )
        
        # Rule 2: Air quality monitoring during pollution season
        air_quality_rule = EdgeRule(
            rule_id="mumbai_air_quality",
            name="Air Quality Monitor",
            description="Monitor air quality levels in Mumbai",
            device_filter="air_quality_*",
            conditions=[
                {
                    'field': 'pm2_5',
                    'operator': '>',
                    'value': 60,  # WHO guidelines for PM2.5
                    'unit': 'µg/m³'
                }
            ],
            actions=[
                {
                    'type': 'alert',
                    'severity': 'medium',
                    'message': 'Poor air quality detected'
                },
                {
                    'type': 'data_aggregation',
                    'interval': '5_minutes'
                }
            ]
        )
        
        # Rule 3: Water level monitoring (monsoon season)
        water_level_rule = EdgeRule(
            rule_id="mumbai_flood_monitor",
            name="Flood Water Level Monitor", 
            description="Monitor water levels during Mumbai monsoons",
            device_filter="water_level_*",
            conditions=[
                {
                    'field': 'water_level',
                    'operator': '>',
                    'value': 2.0,  # 2 meters
                    'unit': 'meters'
                }
            ],
            actions=[
                {
                    'type': 'alert',
                    'severity': 'critical',
                    'message': 'Flood warning - high water level detected'
                },
                {
                    'type': 'emergency_notification',
                    'recipients': ['mumbai_bmc', 'local_authorities']
                }
            ]
        )
        
        # Rule 4: Energy consumption optimization
        energy_optimization_rule = EdgeRule(
            rule_id="mumbai_energy_optimization",
            name="Energy Consumption Optimizer",
            description="Optimize energy usage in Mumbai buildings",
            device_filter="smart_meter_*",
            conditions=[
                {
                    'field': 'power_consumption',
                    'operator': '>',
                    'value': 80,  # 80% of capacity
                    'unit': 'percent'
                }
            ],
            actions=[
                {
                    'type': 'command',
                    'target': 'load_balancer',
                    'action': 'distribute_load'
                },
                {
                    'type': 'notification',
                    'message': 'High energy consumption detected'
                }
            ]
        )
        
        # Rule 5: Security camera motion detection
        security_rule = EdgeRule(
            rule_id="mumbai_security_motion",
            name="Security Motion Detection",
            description="Process motion detection from security cameras",
            device_filter="security_camera_*",
            message_filter="event",
            conditions=[
                {
                    'field': 'motion_detected',
                    'operator': '==',
                    'value': True
                },
                {
                    'field': 'confidence',
                    'operator': '>',
                    'value': 0.8
                }
            ],
            actions=[
                {
                    'type': 'alert',
                    'severity': 'medium',
                    'message': 'Motion detected by security camera'
                },
                {
                    'type': 'video_recording',
                    'duration': 30  # seconds
                }
            ]
        )
        
        # Register all rules
        rules = [temp_alert_rule, air_quality_rule, water_level_rule, 
                energy_optimization_rule, security_rule]
        
        for rule in rules:
            self.processing_rules[rule.rule_id] = rule
        
        logger.info(f"Initialized {len(rules)} Mumbai IoT processing rules")
    
    async def start(self):
        """Start the IoT Edge Gateway"""
        if self.running:
            logger.warning("IoT Gateway already running")
            return
        
        self.running = True
        
        # Initialize database
        await self._init_database()
        
        # Start worker tasks
        self.worker_tasks = [
            asyncio.create_task(self._message_processor_loop()),
            asyncio.create_task(self._device_monitor_loop()),
            asyncio.create_task(self._rule_engine_loop()),
            asyncio.create_task(self._device_discovery_loop()),
            asyncio.create_task(self._cloud_sync_loop()),
            asyncio.create_task(self._metrics_collector_loop())
        ]
        
        logger.info("IoT Edge Gateway started")
    
    async def stop(self):
        """Stop the IoT Edge Gateway"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        try:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error stopping worker tasks: {str(e)}")
        
        # Close database connection
        if self.db_connection:
            self.db_connection.close()
        
        logger.info("IoT Edge Gateway stopped")
    
    async def _init_database(self):
        """Initialize local SQLite database"""
        try:
            self.db_connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self.db_connection.execute("PRAGMA journal_mode=WAL")
            
            # Create tables
            self.db_connection.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    device_data TEXT,
                    last_updated TEXT,
                    status TEXT
                )
            """)
            
            self.db_connection.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    device_id TEXT,
                    timestamp TEXT,
                    message_type TEXT,
                    priority TEXT,
                    payload TEXT,
                    processed BOOLEAN,
                    cloud_synced BOOLEAN
                )
            """)
            
            self.db_connection.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id TEXT PRIMARY KEY,
                    device_id TEXT,
                    rule_id TEXT,
                    timestamp TEXT,
                    severity TEXT,
                    message TEXT,
                    acknowledged BOOLEAN DEFAULT FALSE
                )
            """)
            
            self.db_connection.commit()
            logger.info("IoT Gateway database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    async def register_device(self, device: IoTDevice) -> bool:
        """
        Register IoT device with gateway
        Mumbai society में new resident registration की तरह
        """
        try:
            if len(self.connected_devices) >= self.max_devices:
                logger.error(f"Maximum device limit ({self.max_devices}) reached")
                return False
            
            if device.device_id in self.connected_devices:
                logger.info(f"Device {device.device_id} already registered, updating...")
            else:
                self.stats['total_devices'] += 1
                self.stats['device_discoveries'] += 1
            
            device.last_seen = datetime.now()
            device.status = DeviceStatus.ONLINE
            
            # Store device
            self.connected_devices[device.device_id] = device
            
            # Save to database
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO devices 
                (device_id, device_data, last_updated, status)
                VALUES (?, ?, ?, ?)
            """, (
                device.device_id,
                json.dumps(asdict(device), default=str),
                datetime.now().isoformat(),
                device.status.value
            ))
            self.db_connection.commit()
            
            logger.info(f"IoT device registered: {device.device_id} ({device.device_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Device registration failed: {str(e)}")
            return False
    
    async def unregister_device(self, device_id: str) -> bool:
        """Unregister IoT device"""
        try:
            if device_id not in self.connected_devices:
                logger.warning(f"Device {device_id} not found")
                return False
            
            # Remove device
            del self.connected_devices[device_id]
            self.stats['total_devices'] -= 1
            
            # Update database
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM devices WHERE device_id = ?", (device_id,))
            self.db_connection.commit()
            
            logger.info(f"IoT device unregistered: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Device unregistration failed: {str(e)}")
            return False
    
    async def process_message(self, message: IoTMessage) -> bool:
        """
        Process incoming IoT message
        Mumbai traffic signal की तरह - intelligent message routing
        """
        try:
            # Validate device is registered
            if message.device_id not in self.connected_devices:
                logger.warning(f"Message from unregistered device: {message.device_id}")
                return False
            
            # Update device activity
            device = self.connected_devices[message.device_id]
            device.last_seen = datetime.now()
            device.total_messages += 1
            device.data_rate = self._calculate_data_rate(device)
            
            # Add to processing queue
            await self.message_queue.put(message)
            
            # Update statistics
            self.stats['total_messages'] += 1
            self.stats['bytes_processed'] += message.size_bytes
            
            return True
            
        except Exception as e:
            logger.error(f"Message processing failed: {str(e)}")
            self.stats['error_counts']['message_processing'] += 1
            return False
    
    def _calculate_data_rate(self, device: IoTDevice) -> float:
        """Calculate device data rate (messages per minute)"""
        try:
            # Get recent messages from this device
            recent_messages = [
                msg for msg in list(self.processed_messages)[-1000:]
                if msg.device_id == device.device_id
            ]
            
            if len(recent_messages) < 2:
                return 0.0
            
            # Calculate rate over last 5 minutes
            cutoff_time = datetime.now() - timedelta(minutes=5)
            recent_count = sum(
                1 for msg in recent_messages 
                if msg.timestamp > cutoff_time
            )
            
            return recent_count / 5.0  # Messages per minute
            
        except Exception as e:
            logger.error(f"Data rate calculation failed: {str(e)}")
            return 0.0
    
    async def _message_processor_loop(self):
        """
        Main message processing loop
        Mumbai post office की तरह - continuous message processing
        """
        logger.info("Message processor started")
        
        while self.running:
            try:
                # Get message from queue
                try:
                    message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process message
                start_time = time.time()
                
                # Apply processing rules
                if self.rule_engine_enabled:
                    await self._apply_processing_rules(message)
                
                # Store processed message
                await self._store_message(message)
                
                # Add to processed messages
                message.processed = True
                self.processed_messages.append(message)
                
                # Update statistics
                processing_time = (time.time() - start_time) * 1000
                self.stats['processed_messages'] += 1
                self.stats['processing_times'].append(processing_time)
                
                # Mark task as done
                self.message_queue.task_done()
                
            except Exception as e:
                logger.error(f"Message processor error: {str(e)}")
                await asyncio.sleep(1)
        
        logger.info("Message processor stopped")
    
    async def _apply_processing_rules(self, message: IoTMessage):
        """Apply edge processing rules to message"""
        try:
            for rule_id, rule in self.processing_rules.items():
                if not rule.enabled:
                    continue
                
                # Check if rule applies to this message
                if not self._rule_matches_message(rule, message):
                    continue
                
                # Check rule conditions
                if await self._evaluate_rule_conditions(rule, message):
                    # Execute rule actions
                    await self._execute_rule_actions(rule, message)
                    rule.execution_count += 1
                    self.stats['rule_executions'] += 1
                    
        except Exception as e:
            logger.error(f"Rule processing failed: {str(e)}")
    
    def _rule_matches_message(self, rule: EdgeRule, message: IoTMessage) -> bool:
        """Check if rule matches message"""
        try:
            # Check device filter
            if rule.device_filter:
                device_pattern = rule.device_filter.replace('*', '.*')
                if not message.device_id.startswith(device_pattern.replace('.*', '')):
                    return False
            
            # Check message filter
            if rule.message_filter:
                if rule.message_filter != message.message_type:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rule matching failed: {str(e)}")
            return False
    
    async def _evaluate_rule_conditions(self, rule: EdgeRule, message: IoTMessage) -> bool:
        """Evaluate rule conditions against message"""
        try:
            if not rule.conditions:
                return True  # No conditions = always match
            
            for condition in rule.conditions:
                field = condition.get('field')
                operator = condition.get('operator')
                expected_value = condition.get('value')
                
                if field not in message.payload:
                    continue
                
                actual_value = message.payload[field]
                
                # Evaluate condition
                if operator == '>':
                    if not (actual_value > expected_value):
                        return False
                elif operator == '<':
                    if not (actual_value < expected_value):
                        return False
                elif operator == '>=':
                    if not (actual_value >= expected_value):
                        return False
                elif operator == '<=':
                    if not (actual_value <= expected_value):
                        return False
                elif operator == '==':
                    if not (actual_value == expected_value):
                        return False
                elif operator == '!=':
                    if not (actual_value != expected_value):
                        return False
            
            return True  # All conditions passed
            
        except Exception as e:
            logger.error(f"Rule condition evaluation failed: {str(e)}")
            return False
    
    async def _execute_rule_actions(self, rule: EdgeRule, message: IoTMessage):
        """Execute rule actions"""
        try:
            for action in rule.actions:
                action_type = action.get('type')
                
                if action_type == 'alert':
                    await self._generate_alert(rule, message, action)
                elif action_type == 'command':
                    await self._send_device_command(action, message)
                elif action_type == 'data_aggregation':
                    await self._aggregate_data(action, message)
                elif action_type == 'notification':
                    await self._send_notification(action, message)
                elif action_type == 'emergency_notification':
                    await self._send_emergency_notification(action, message)
                else:
                    logger.info(f"Executed action: {action_type}")
                    
        except Exception as e:
            logger.error(f"Rule action execution failed: {str(e)}")
    
    async def _generate_alert(self, rule: EdgeRule, message: IoTMessage, action: Dict[str, Any]):
        """Generate alert based on rule"""
        try:
            alert_id = f"alert_{rule.rule_id}_{message.device_id}_{int(time.time())}"
            
            alert_data = {
                'alert_id': alert_id,
                'device_id': message.device_id,
                'rule_id': rule.rule_id,
                'timestamp': datetime.now().isoformat(),
                'severity': action.get('severity', 'medium'),
                'message': action.get('message', f'Alert from rule {rule.name}'),
                'payload_data': message.payload
            }
            
            # Store alert in database
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO alerts 
                (alert_id, device_id, rule_id, timestamp, severity, message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alert_id, message.device_id, rule.rule_id,
                alert_data['timestamp'], alert_data['severity'], alert_data['message']
            ))
            self.db_connection.commit()
            
            self.stats['alerts_generated'] += 1
            
            logger.warning(f"Alert generated: {alert_id} - {alert_data['message']}")
            
        except Exception as e:
            logger.error(f"Alert generation failed: {str(e)}")
    
    async def _send_device_command(self, action: Dict[str, Any], message: IoTMessage):
        """Send command to device (simulated)"""
        target_device = action.get('target')
        command_action = action.get('action')
        
        logger.info(f"Device command sent: {command_action} to {target_device}")
        # In production, this would send actual commands to devices
    
    async def _aggregate_data(self, action: Dict[str, Any], message: IoTMessage):
        """Aggregate data for batch processing"""
        interval = action.get('interval', '1_minute')
        
        # Add message to buffer for aggregation
        buffer_key = f"{message.device_id}_{interval}"
        self.message_buffer[buffer_key].append(message)
        
        logger.debug(f"Data aggregated for {buffer_key}")
    
    async def _send_notification(self, action: Dict[str, Any], message: IoTMessage):
        """Send notification (simulated)"""
        notification_message = action.get('message', 'IoT notification')
        logger.info(f"Notification sent: {notification_message}")
    
    async def _send_emergency_notification(self, action: Dict[str, Any], message: IoTMessage):
        """Send emergency notification (simulated)"""
        recipients = action.get('recipients', [])
        logger.error(f"EMERGENCY NOTIFICATION sent to {recipients}: Critical IoT event detected")
    
    async def _store_message(self, message: IoTMessage):
        """Store message in local database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO messages 
                (message_id, device_id, timestamp, message_type, priority, payload, processed, cloud_synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message.message_id,
                message.device_id,
                message.timestamp.isoformat(),
                message.message_type,
                message.priority.value,
                json.dumps(message.payload),
                message.processed,
                message.cloud_synced
            ))
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Message storage failed: {str(e)}")
    
    async def _device_monitor_loop(self):
        """Monitor device health and connectivity"""
        logger.info("Device monitor started")
        
        while self.running:
            try:
                current_time = datetime.now()
                active_devices = 0
                
                for device_id, device in list(self.connected_devices.items()):
                    # Check device connectivity
                    if device.last_seen:
                        time_since_last_seen = current_time - device.last_seen
                        
                        if time_since_last_seen.total_seconds() > 300:  # 5 minutes
                            if device.status == DeviceStatus.ONLINE:
                                device.status = DeviceStatus.OFFLINE
                                logger.warning(f"Device {device_id} went offline")
                        else:
                            if device.status == DeviceStatus.OFFLINE:
                                device.status = DeviceStatus.ONLINE
                                logger.info(f"Device {device_id} back online")
                            active_devices += 1
                    
                    # Check battery level
                    if (device.battery_level is not None and 
                        device.battery_level < 20.0 and 
                        device.status != DeviceStatus.LOW_BATTERY):
                        
                        device.status = DeviceStatus.LOW_BATTERY
                        logger.warning(f"Device {device_id} low battery: {device.battery_level}%")
                
                self.stats['active_devices'] = active_devices
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Device monitor error: {str(e)}")
                await asyncio.sleep(30)
        
        logger.info("Device monitor stopped")
    
    async def _rule_engine_loop(self):
        """Background rule engine maintenance"""
        logger.info("Rule engine started")
        
        while self.running:
            try:
                # Process aggregated data buffers
                current_time = datetime.now()
                
                for buffer_key, messages in list(self.message_buffer.items()):
                    if not messages:
                        continue
                    
                    # Check if buffer should be processed
                    oldest_message = min(messages, key=lambda m: m.timestamp)
                    age_seconds = (current_time - oldest_message.timestamp).total_seconds()
                    
                    # Process buffer if it's old enough (5 minutes)
                    if age_seconds > 300:
                        await self._process_aggregated_buffer(buffer_key, messages)
                        self.message_buffer[buffer_key] = []
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Rule engine error: {str(e)}")
                await asyncio.sleep(30)
        
        logger.info("Rule engine stopped")
    
    async def _process_aggregated_buffer(self, buffer_key: str, messages: List[IoTMessage]):
        """Process aggregated message buffer"""
        try:
            if not messages:
                return
            
            # Calculate aggregated metrics
            device_id = messages[0].device_id
            message_count = len(messages)
            
            # Extract numeric values for aggregation
            numeric_fields = {}
            for message in messages:
                for key, value in message.payload.items():
                    if isinstance(value, (int, float)):
                        if key not in numeric_fields:
                            numeric_fields[key] = []
                        numeric_fields[key].append(value)
            
            # Calculate aggregated values
            aggregated_data = {}
            for field, values in numeric_fields.items():
                aggregated_data[field] = {
                    'avg': statistics.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
            
            logger.info(f"Processed aggregated buffer {buffer_key}: {message_count} messages")
            logger.debug(f"Aggregated data: {aggregated_data}")
            
        except Exception as e:
            logger.error(f"Buffer processing failed: {str(e)}")
    
    async def _device_discovery_loop(self):
        """Simulate device discovery"""
        logger.info("Device discovery started")
        
        while self.running:
            try:
                if self.device_discovery_enabled and random.random() < 0.1:  # 10% chance
                    await self._simulate_device_discovery()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Device discovery error: {str(e)}")
                await asyncio.sleep(60)
        
        logger.info("Device discovery stopped")
    
    async def _simulate_device_discovery(self):
        """Simulate discovering new IoT devices"""
        try:
            if len(self.connected_devices) >= self.max_devices:
                return
            
            # Generate random device
            device_types = list(DeviceType)
            device_type = random.choice(device_types)
            
            device_id = f"{device_type.name.lower()}_{uuid.uuid4().hex[:8]}"
            
            new_device = IoTDevice(
                device_id=device_id,
                device_name=f"Mumbai {device_type.value} Sensor",
                device_type=device_type,
                mac_address=f"00:11:22:33:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                ip_address=f"192.168.1.{random.randint(100, 254)}",
                firmware_version=f"v{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}",
                location=f"Mumbai Zone {random.randint(1,5)}",
                battery_level=random.uniform(20, 100) if device_type != DeviceType.SMART_METER else None,
                signal_strength=random.randint(-80, -30)
            )
            
            success = await self.register_device(new_device)
            if success:
                logger.info(f"Discovered new device: {device_id}")
                
        except Exception as e:
            logger.error(f"Device discovery simulation failed: {str(e)}")
    
    async def _cloud_sync_loop(self):
        """Simulate cloud synchronization"""
        logger.info("Cloud sync started")
        
        while self.running:
            try:
                # Find unsynced messages
                unsynced_messages = [
                    msg for msg in list(self.processed_messages)[-1000:]
                    if not msg.cloud_synced and msg.processing_mode == ProcessingMode.CLOUD_SYNC
                ]
                
                if unsynced_messages:
                    # Simulate cloud sync
                    for message in unsynced_messages[:50]:  # Sync 50 at a time
                        # Simulate sync delay
                        await asyncio.sleep(0.01)
                        
                        message.cloud_synced = True
                        self.stats['cloud_synced_messages'] += 1
                    
                    logger.info(f"Synced {min(50, len(unsynced_messages))} messages to cloud")
                
                await asyncio.sleep(60)  # Sync every minute
                
            except Exception as e:
                logger.error(f"Cloud sync error: {str(e)}")
                await asyncio.sleep(120)
        
        logger.info("Cloud sync stopped")
    
    async def _metrics_collector_loop(self):
        """Collect performance metrics"""
        logger.info("Metrics collector started")
        
        while self.running:
            try:
                # Calculate current message rate
                current_time = datetime.now()
                recent_messages = sum(
                    1 for msg in list(self.processed_messages)[-300:]  # Last 5 minutes
                    if (current_time - msg.timestamp).total_seconds() < 300
                )
                messages_per_minute = recent_messages / 5.0
                self.stats['message_rates'].append(messages_per_minute)
                
                # Clean up old data
                cutoff_time = current_time - timedelta(hours=1)
                while (self.processed_messages and 
                       self.processed_messages[0].timestamp < cutoff_time):
                    self.processed_messages.popleft()
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Metrics collector error: {str(e)}")
                await asyncio.sleep(60)
        
        logger.info("Metrics collector stopped")
    
    def get_gateway_stats(self) -> Dict[str, Any]:
        """Get comprehensive gateway statistics"""
        try:
            current_time = datetime.now()
            uptime = current_time - self.stats['uptime_start']
            
            # Calculate performance metrics
            avg_processing_time = (
                statistics.mean(self.stats['processing_times'])
                if self.stats['processing_times'] else 0
            )
            
            current_message_rate = (
                self.stats['message_rates'][-1]
                if self.stats['message_rates'] else 0
            )
            
            # Device statistics
            device_status_counts = defaultdict(int)
            device_type_counts = defaultdict(int)
            
            for device in self.connected_devices.values():
                device_status_counts[device.status.value] += 1
                device_type_counts[device.device_type.value] += 1
            
            return {
                "gateway_info": {
                    "gateway_id": self.gateway_id,
                    "location": self.location,
                    "max_devices": self.max_devices,
                    "uptime_hours": round(uptime.total_seconds() / 3600, 2),
                    "status": "running" if self.running else "stopped"
                },
                "device_statistics": {
                    "total_devices": self.stats['total_devices'],
                    "active_devices": self.stats['active_devices'],
                    "device_discoveries": self.stats['device_discoveries'],
                    "devices_by_status": dict(device_status_counts),
                    "devices_by_type": dict(device_type_counts)
                },
                "message_statistics": {
                    "total_messages": self.stats['total_messages'],
                    "processed_messages": self.stats['processed_messages'],
                    "cloud_synced_messages": self.stats['cloud_synced_messages'],
                    "current_message_rate_per_minute": round(current_message_rate, 2),
                    "bytes_processed": self.stats['bytes_processed'],
                    "avg_processing_time_ms": round(avg_processing_time, 2)
                },
                "rule_engine_statistics": {
                    "active_rules": len([r for r in self.processing_rules.values() if r.enabled]),
                    "total_rules": len(self.processing_rules),
                    "rule_executions": self.stats['rule_executions'],
                    "alerts_generated": self.stats['alerts_generated']
                },
                "performance_metrics": {
                    "queue_size": self.message_queue.qsize(),
                    "processed_message_history": len(self.processed_messages),
                    "error_counts": dict(self.stats['error_counts'])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get gateway stats: {str(e)}")
            return {"error": str(e)}

# Example usage and comprehensive testing
async def main():
    """
    Comprehensive IoT Edge Gateway testing  
    Mumbai smart city IoT network demonstration
    """
    print("🌐 IoT Edge Gateway - Mumbai Smart City Network")
    print("=" * 55)
    
    # Initialize IoT gateway
    gateway = IoTEdgeGateway("mumbai-iot-gateway-01", "Mumbai Central", max_devices=500)
    await gateway.start()
    
    print(f"✅ IoT Gateway started: {gateway.gateway_id}")
    print(f"📍 Location: {gateway.location}")
    print(f"📱 Max Devices: {gateway.max_devices}")
    
    # Register sample Mumbai IoT devices
    print(f"\n📡 Registering Mumbai IoT Devices...")
    
    mumbai_devices = [
        IoTDevice(
            device_id="temp_sensor_mumbai_01",
            device_name="Mumbai Office Temperature Sensor",
            device_type=DeviceType.SENSOR,
            mac_address="00:11:22:33:44:01",
            ip_address="192.168.1.101",
            firmware_version="v2.1.3",
            location="Mumbai BKC Office",
            battery_level=85.0,
            signal_strength=-45
        ),
        IoTDevice(
            device_id="air_quality_mumbai_01",
            device_name="Mumbai Air Quality Monitor",
            device_type=DeviceType.SENSOR,
            mac_address="00:11:22:33:44:02",
            ip_address="192.168.1.102",
            firmware_version="v1.8.2",
            location="Mumbai Dadar Station",
            battery_level=92.0,
            signal_strength=-52
        ),
        IoTDevice(
            device_id="water_level_mumbai_01",
            device_name="Mumbai Flood Monitor",
            device_type=DeviceType.SENSOR,
            mac_address="00:11:22:33:44:03",
            ip_address="192.168.1.103",
            firmware_version="v3.0.1",
            location="Mumbai Hindmata",
            battery_level=78.0,
            signal_strength=-38
        ),
        IoTDevice(
            device_id="smart_meter_mumbai_01",
            device_name="Mumbai Building Energy Meter",
            device_type=DeviceType.SMART_METER,
            mac_address="00:11:22:33:44:04",
            ip_address="192.168.1.104",
            firmware_version="v4.2.0",
            location="Mumbai Residential Complex",
            signal_strength=-41
        ),
        IoTDevice(
            device_id="security_camera_mumbai_01",
            device_name="Mumbai Security Camera",
            device_type=DeviceType.CAMERA,
            mac_address="00:11:22:33:44:05",
            ip_address="192.168.1.105",
            firmware_version="v2.5.1",
            location="Mumbai Entrance Gate",
            signal_strength=-48
        )
    ]
    
    # Register devices
    for device in mumbai_devices:
        success = await gateway.register_device(device)
        status_emoji = "✅" if success else "❌"
        print(f"{status_emoji} {device.device_name}: {device.device_id}")
        print(f"   Type: {device.device_type.value} | Battery: {device.battery_level}% | Signal: {device.signal_strength}dBm")
    
    # Simulate IoT messages
    print(f"\n📨 Simulating Mumbai IoT Messages...")
    
    # Generate various types of messages
    test_messages = [
        # Temperature sensor data (normal)
        IoTMessage(
            message_id="msg_temp_001",
            device_id="temp_sensor_mumbai_01",
            timestamp=datetime.now(),
            message_type="telemetry",
            priority=MessagePriority.NORMAL,
            payload={"temperature": 28.5, "humidity": 65.0, "location": "office_floor_3"}
        ),
        # Temperature sensor alert (high temp)
        IoTMessage(
            message_id="msg_temp_002",
            device_id="temp_sensor_mumbai_01",
            timestamp=datetime.now(),
            message_type="telemetry",
            priority=MessagePriority.HIGH,
            payload={"temperature": 36.5, "humidity": 70.0, "location": "server_room"}  # Triggers temp alert rule
        ),
        # Air quality data (poor quality)
        IoTMessage(
            message_id="msg_air_001",
            device_id="air_quality_mumbai_01",
            timestamp=datetime.now(),
            message_type="telemetry",
            priority=MessagePriority.NORMAL,
            payload={"pm2_5": 75, "pm10": 120, "aqi": 180}  # Triggers air quality rule
        ),
        # Water level normal
        IoTMessage(
            message_id="msg_water_001",
            device_id="water_level_mumbai_01",
            timestamp=datetime.now(),
            message_type="telemetry",
            priority=MessagePriority.NORMAL,
            payload={"water_level": 0.8, "flow_rate": 15.2, "sensor_status": "ok"}
        ),
        # Water level critical (flood warning)
        IoTMessage(
            message_id="msg_water_002",
            device_id="water_level_mumbai_01",
            timestamp=datetime.now(),
            message_type="telemetry",
            priority=MessagePriority.CRITICAL,
            payload={"water_level": 2.5, "flow_rate": 45.8, "sensor_status": "warning"}  # Triggers flood rule
        ),
        # Energy meter data (high consumption)
        IoTMessage(
            message_id="msg_energy_001",
            device_id="smart_meter_mumbai_01",
            timestamp=datetime.now(),
            message_type="telemetry",
            priority=MessagePriority.NORMAL,
            payload={"power_consumption": 85, "voltage": 220, "current": 15.5}  # Triggers energy rule
        ),
        # Security camera motion detection
        IoTMessage(
            message_id="msg_security_001",
            device_id="security_camera_mumbai_01",
            timestamp=datetime.now(),
            message_type="event",
            priority=MessagePriority.HIGH,
            payload={"motion_detected": True, "confidence": 0.87, "object_count": 2}  # Triggers security rule
        )
    ]
    
    # Process messages
    for message in test_messages:
        success = await gateway.process_message(message)
        priority_emoji = {"निम्न": "🟡", "सामान्य": "🟢", "उच्च": "🟠", "गंभीर": "🔴"}
        status_emoji = "✅" if success else "❌"
        
        print(f"{status_emoji} {priority_emoji[message.priority.value]} {message.message_id}: {message.message_type}")
        print(f"   Device: {message.device_id} | Size: {message.size_bytes} bytes")
    
    # Wait for message processing
    print(f"\n⏱️ Processing IoT messages...")
    await asyncio.sleep(5)
    
    # Check if alerts were generated
    print(f"\n🚨 Checking Generated Alerts...")
    
    # Query alerts from database
    cursor = gateway.db_connection.cursor()
    cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10")
    alerts = cursor.fetchall()
    
    if alerts:
        for alert in alerts:
            severity_emoji = {"low": "🟡", "medium": "🟠", "high": "🔴", "critical": "🚨"}
            alert_id, device_id, rule_id, timestamp, severity, message, acknowledged = alert
            
            print(f"{severity_emoji.get(severity, '🔵')} Alert: {alert_id}")
            print(f"   Device: {device_id}")
            print(f"   Rule: {rule_id}")
            print(f"   Message: {message}")
            print(f"   Time: {timestamp}")
            print()
    else:
        print("No alerts generated")
    
    # Let gateway run for monitoring
    print(f"\n🔄 Running IoT gateway for 30 seconds...")
    await asyncio.sleep(30)
    
    # Get comprehensive statistics
    stats = gateway.get_gateway_stats()
    
    print(f"\n📊 IoT Gateway Performance Report:")
    print("=" * 45)
    
    # Gateway info
    gateway_info = stats["gateway_info"]
    print(f"Gateway: {gateway_info['gateway_id']}")
    print(f"Location: {gateway_info['location']}")
    print(f"Uptime: {gateway_info['uptime_hours']} hours")
    print(f"Status: {gateway_info['status']}")
    
    # Device statistics
    device_stats = stats["device_statistics"]
    print(f"\n📱 Device Statistics:")
    print(f"• Total Devices: {device_stats['total_devices']}")
    print(f"• Active Devices: {device_stats['active_devices']}")
    print(f"• Device Discoveries: {device_stats['device_discoveries']}")
    
    if device_stats['devices_by_status']:
        print(f"\n• Devices by Status:")
        status_emojis = {"ऑनलाइन": "🟢", "ऑफलाइन": "🔴", "रखरखाव": "🟡", "त्रुटि": "🔴", "कम बैटरी": "🟠"}
        for status, count in device_stats['devices_by_status'].items():
            print(f"  {status_emojis.get(status, '🔵')} {status}: {count}")
    
    if device_stats['devices_by_type']:
        print(f"\n• Devices by Type:")
        for device_type, count in device_stats['devices_by_type'].items():
            print(f"  - {device_type}: {count}")
    
    # Message statistics
    message_stats = stats["message_statistics"]
    print(f"\n📨 Message Statistics:")
    print(f"• Total Messages: {message_stats['total_messages']}")
    print(f"• Processed Messages: {message_stats['processed_messages']}")
    print(f"• Cloud Synced: {message_stats['cloud_synced_messages']}")
    print(f"• Message Rate: {message_stats['current_message_rate_per_minute']:.1f}/min")
    print(f"• Bytes Processed: {message_stats['bytes_processed']:,}")
    print(f"• Avg Processing Time: {message_stats['avg_processing_time_ms']:.2f}ms")
    
    # Rule engine statistics
    rule_stats = stats["rule_engine_statistics"]
    print(f"\n🔧 Rule Engine Statistics:")
    print(f"• Active Rules: {rule_stats['active_rules']}")
    print(f"• Total Rules: {rule_stats['total_rules']}")
    print(f"• Rule Executions: {rule_stats['rule_executions']}")
    print(f"• Alerts Generated: {rule_stats['alerts_generated']}")
    
    # Performance metrics
    performance = stats["performance_metrics"]
    print(f"\n⚡ Performance Metrics:")
    print(f"• Queue Size: {performance['queue_size']}")
    print(f"• Message History: {performance['processed_message_history']}")
    
    if performance['error_counts']:
        print(f"• Error Counts:")
        for error_type, count in performance['error_counts'].items():
            print(f"  - {error_type}: {count}")
    
    # Cost analysis
    print(f"\n💰 Cost Analysis (Monthly):")
    print("-" * 25)
    
    total_devices = device_stats['total_devices']
    edge_processing_cost = total_devices * 1      # ₹1 per device per month
    cloud_processing_cost = total_devices * 10    # ₹10 per device per month
    savings = cloud_processing_cost - edge_processing_cost
    
    print(f"Edge Processing Cost: ₹{edge_processing_cost:,}/month")
    print(f"Cloud Processing Cost: ₹{cloud_processing_cost:,}/month")
    print(f"Monthly Savings: ₹{savings:,}")
    print(f"Savings Percentage: {(savings/cloud_processing_cost)*100:.1f}%")
    
    # Business benefits
    print(f"\n🎯 Business Benefits:")
    print("• Local IoT data processing and rule engine")
    print("• Real-time alert generation for critical events")
    print("• Reduced cloud bandwidth and processing costs")
    print("• Mumbai-specific environmental monitoring")
    print("• Automated device discovery and management")
    print("• Edge intelligence for smart city applications")
    
    # Mumbai-specific insights
    print(f"\n🏙️ Mumbai Smart City Insights:")
    print("• Temperature monitoring for server rooms in hot climate")
    print("• Air quality tracking during pollution seasons")
    print("• Flood monitoring system for monsoon preparedness")
    print("• Energy optimization for Mumbai's power grid")
    print("• Security automation for residential complexes")
    
    # Stop gateway
    print(f"\n🛑 Stopping IoT gateway...")
    await gateway.stop()
    
    print(f"\n✅ IoT Edge Gateway demonstration completed!")
    print(f"🌐 Mumbai smart city IoT network optimized with edge intelligence!")

if __name__ == "__main__":
    asyncio.run(main())
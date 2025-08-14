#!/usr/bin/env python3
"""
MQTT Edge Broker - एज डिवाइसेज के लिए MQTT ब्रोकर
Mumbai local train announcements की तरह - real-time messaging system

Real-world inspired by IoT platforms like AWS IoT Core, Azure IoT Hub
Use case: Smart city sensors, vehicle tracking, home automation
Cost: Local MQTT vs Cloud MQTT - ₹0.01 vs ₹0.5 per message
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import threading
import queue
import hashlib
import uuid
from collections import defaultdict, deque
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QoSLevel(Enum):
    """MQTT Quality of Service levels"""
    AT_MOST_ONCE = 0    # Fire and forget - भेज दिया और भूल गए
    AT_LEAST_ONCE = 1   # कम से कम एक बार पहुंचना चाहिए  
    EXACTLY_ONCE = 2    # सिर्फ एक ही बार पहुंचना चाहिए

class DeviceType(Enum):
    """Different types of IoT devices"""
    SENSOR = "सेंसर"           # Temperature, humidity sensors
    ACTUATOR = "एक्चुएटर"      # Motors, switches, valves
    GATEWAY = "गेटवे"          # Local network gateway
    CAMERA = "कैमरा"          # Security/monitoring cameras
    VEHICLE = "व्हीकल"         # Cars, trucks, bikes

@dataclass
class MQTTMessage:
    """MQTT message structure"""
    topic: str
    payload: str
    qos: QoSLevel
    retain: bool
    timestamp: datetime
    client_id: str
    message_id: Optional[str] = None
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())[:8]

@dataclass
class EdgeDevice:
    """Edge device representation"""
    device_id: str
    device_type: DeviceType
    location: str
    last_seen: datetime
    subscribed_topics: Set[str]
    published_topics: Set[str]
    message_count: int = 0
    is_online: bool = True
    battery_level: Optional[float] = None
    
    def __post_init__(self):
        self.subscribed_topics = set(self.subscribed_topics) if self.subscribed_topics else set()
        self.published_topics = set(self.published_topics) if self.published_topics else set()

class MQTTEdgeBroker:
    """
    MQTT Edge Broker - Mumbai local train control room की तरह
    सभी devices के साथ real-time messaging coordination
    """
    
    def __init__(self, broker_id: str, location: str = "Mumbai", port: int = 1883):
        """
        Initialize MQTT Edge Broker
        Args:
            broker_id: Unique broker identifier
            location: Geographic location
            port: MQTT port (default 1883)
        """
        self.broker_id = broker_id
        self.location = location
        self.port = port
        
        # Client management
        self.connected_devices: Dict[str, EdgeDevice] = {}
        self.topic_subscribers: Dict[str, Set[str]] = defaultdict(set)
        self.retained_messages: Dict[str, MQTTMessage] = {}
        
        # Message handling
        self.message_queue = queue.Queue()
        self.message_history = deque(maxlen=10000)  # Last 10k messages
        self.pending_acks = {}  # QoS 1&2 message acknowledgments
        
        # Statistics
        self.stats = {
            'messages_received': 0,
            'messages_published': 0,
            'messages_delivered': 0,
            'bytes_transferred': 0,
            'connection_count': 0,
            'peak_connections': 0,
            'uptime_start': datetime.now(),
            'topic_stats': defaultdict(int),
            'device_type_stats': defaultdict(int)
        }
        
        # Threading
        self.running = False
        self.message_processor_thread = None
        self.heartbeat_thread = None
        
        # Mumbai-specific IoT scenarios
        self.mumbai_topics = {
            'traffic/signals/+/status',      # Traffic signal status
            'trains/central/+/arrival',      # Local train arrivals
            'weather/mumbai/+/data',         # Weather monitoring
            'parking/malls/+/availability',  # Parking availability
            'air_quality/+/readings',        # Air quality sensors
            'street_lights/+/status',        # Smart street lights
            'waste_bins/+/level',            # Smart waste management
            'flood_sensors/+/water_level'    # Monsoon flood monitoring
        }
        
        logger.info(f"MQTT Edge Broker '{broker_id}' initialized at {location}:{port}")
    
    def start(self):
        """Start the MQTT broker"""
        if self.running:
            logger.warning("Broker already running")
            return
        
        self.running = True
        
        # Start message processor thread
        self.message_processor_thread = threading.Thread(
            target=self._message_processor_loop,
            daemon=True,
            name="MessageProcessor"
        )
        self.message_processor_thread.start()
        
        # Start heartbeat/cleanup thread
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True,
            name="HeartbeatManager"
        )
        self.heartbeat_thread.start()
        
        logger.info(f"MQTT Edge Broker started on port {self.port}")
    
    def stop(self):
        """Stop the MQTT broker"""
        if not self.running:
            return
        
        self.running = False
        
        # Disconnect all devices
        for device_id in list(self.connected_devices.keys()):
            self.disconnect_device(device_id)
        
        logger.info("MQTT Edge Broker stopped")
    
    def connect_device(self, device: EdgeDevice) -> bool:
        """
        Connect a device to the broker
        Mumbai local train station पे new passenger की तरह registration
        """
        try:
            if device.device_id in self.connected_devices:
                logger.info(f"Device {device.device_id} reconnecting")
            else:
                self.stats['connection_count'] += 1
                self.stats['peak_connections'] = max(
                    self.stats['peak_connections'], 
                    len(self.connected_devices) + 1
                )
            
            device.last_seen = datetime.now()
            device.is_online = True
            self.connected_devices[device.device_id] = device
            
            # Update device type statistics
            self.stats['device_type_stats'][device.device_type.value] += 1
            
            logger.info(f"Device connected: {device.device_id} ({device.device_type.value}) from {device.location}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect device {device.device_id}: {str(e)}")
            return False
    
    def disconnect_device(self, device_id: str) -> bool:
        """Disconnect device from broker"""
        try:
            if device_id not in self.connected_devices:
                logger.warning(f"Device {device_id} not found for disconnection")
                return False
            
            device = self.connected_devices[device_id]
            
            # Remove from topic subscriptions
            for topic in list(device.subscribed_topics):
                self.unsubscribe_device(device_id, topic)
            
            # Mark as offline and remove
            device.is_online = False
            del self.connected_devices[device_id]
            
            logger.info(f"Device disconnected: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disconnect device {device_id}: {str(e)}")
            return False
    
    def subscribe_device(self, device_id: str, topic: str, qos: QoSLevel = QoSLevel.AT_MOST_ONCE) -> bool:
        """
        Subscribe device to a topic
        Mumbai local train announcements subscription की तरह
        """
        try:
            if device_id not in self.connected_devices:
                logger.error(f"Device {device_id} not connected")
                return False
            
            device = self.connected_devices[device_id]
            device.subscribed_topics.add(topic)
            device.last_seen = datetime.now()
            
            # Add to topic subscribers
            self.topic_subscribers[topic].add(device_id)
            
            # Send retained messages for this topic
            self._send_retained_messages(device_id, topic)
            
            logger.debug(f"Device {device_id} subscribed to topic: {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe device {device_id} to {topic}: {str(e)}")
            return False
    
    def unsubscribe_device(self, device_id: str, topic: str) -> bool:
        """Unsubscribe device from topic"""
        try:
            if device_id not in self.connected_devices:
                return False
            
            device = self.connected_devices[device_id]
            device.subscribed_topics.discard(topic)
            device.last_seen = datetime.now()
            
            # Remove from topic subscribers
            self.topic_subscribers[topic].discard(device_id)
            
            # Clean up empty topic subscriber sets
            if not self.topic_subscribers[topic]:
                del self.topic_subscribers[topic]
            
            logger.debug(f"Device {device_id} unsubscribed from topic: {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe device {device_id} from {topic}: {str(e)}")
            return False
    
    def publish_message(self, device_id: str, topic: str, payload: str, 
                       qos: QoSLevel = QoSLevel.AT_MOST_ONCE, retain: bool = False) -> bool:
        """
        Publish message from device
        Mumbai local train status announcement की तरह broadcasting
        """
        try:
            if device_id not in self.connected_devices:
                logger.error(f"Device {device_id} not connected")
                return False
            
            device = self.connected_devices[device_id]
            device.published_topics.add(topic)
            device.message_count += 1
            device.last_seen = datetime.now()
            
            # Create message
            message = MQTTMessage(
                topic=topic,
                payload=payload,
                qos=qos,
                retain=retain,
                timestamp=datetime.now(),
                client_id=device_id
            )
            
            # Add to processing queue
            self.message_queue.put(message)
            
            # Update statistics
            self.stats['messages_received'] += 1
            self.stats['bytes_transferred'] += len(payload.encode('utf-8'))
            self.stats['topic_stats'][topic] += 1
            
            logger.debug(f"Message published by {device_id} to {topic}: {len(payload)} bytes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish message from {device_id}: {str(e)}")
            return False
    
    def _message_processor_loop(self):
        """
        Main message processing loop
        Mumbai railway control room की तरह - continuous message processing
        """
        logger.info("Message processor started")
        
        while self.running:
            try:
                # Get message from queue (timeout to allow shutdown)
                try:
                    message = self.message_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process the message
                self._process_message(message)
                
            except Exception as e:
                logger.error(f"Message processor error: {str(e)}")
                time.sleep(0.1)  # Brief pause on error
        
        logger.info("Message processor stopped")
    
    def _process_message(self, message: MQTTMessage):
        """Process individual MQTT message"""
        try:
            # Handle retained messages
            if message.retain:
                self.retained_messages[message.topic] = message
            
            # Find subscribers for this topic
            subscribers = self._find_topic_subscribers(message.topic)
            
            if not subscribers:
                logger.debug(f"No subscribers for topic: {message.topic}")
                return
            
            # Deliver message to subscribers
            delivered_count = 0
            for subscriber_id in subscribers:
                if subscriber_id != message.client_id:  # Don't send back to publisher
                    success = self._deliver_message(subscriber_id, message)
                    if success:
                        delivered_count += 1
            
            # Update statistics
            self.stats['messages_published'] += 1
            self.stats['messages_delivered'] += delivered_count
            
            # Add to message history
            self.message_history.append(message)
            
            logger.debug(f"Message delivered to {delivered_count} subscribers on topic: {message.topic}")
            
        except Exception as e:
            logger.error(f"Failed to process message: {str(e)}")
    
    def _find_topic_subscribers(self, topic: str) -> Set[str]:
        """
        Find all devices subscribed to a topic (including wildcard matches)
        Mumbai local train route matching की तरह - pattern matching
        """
        subscribers = set()
        
        # Exact topic match
        if topic in self.topic_subscribers:
            subscribers.update(self.topic_subscribers[topic])
        
        # Wildcard matching
        for subscription_topic, devices in self.topic_subscribers.items():
            if self._topic_matches(topic, subscription_topic):
                subscribers.update(devices)
        
        return subscribers
    
    def _topic_matches(self, topic: str, subscription: str) -> bool:
        """
        Check if topic matches subscription pattern
        MQTT wildcard support: + (single level), # (multi-level)
        """
        # Handle exact match
        if topic == subscription:
            return True
        
        # Handle wildcards
        topic_parts = topic.split('/')
        sub_parts = subscription.split('/')
        
        # Multi-level wildcard (#) - must be at the end
        if sub_parts and sub_parts[-1] == '#':
            # Check if topic starts with subscription prefix
            prefix_parts = sub_parts[:-1]
            if len(topic_parts) >= len(prefix_parts):
                return topic_parts[:len(prefix_parts)] == prefix_parts
            return False
        
        # Single-level wildcard (+) matching
        if len(topic_parts) != len(sub_parts):
            return False
        
        for topic_part, sub_part in zip(topic_parts, sub_parts):
            if sub_part != '+' and sub_part != topic_part:
                return False
        
        return True
    
    def _deliver_message(self, device_id: str, message: MQTTMessage) -> bool:
        """
        Deliver message to specific device
        Mumbai local train पे specific passenger को message delivery
        """
        try:
            if device_id not in self.connected_devices:
                return False
            
            device = self.connected_devices[device_id]
            
            if not device.is_online:
                logger.debug(f"Device {device_id} offline, message queued")
                return False
            
            # In real implementation, this would send over network
            # For simulation, we'll log the delivery
            logger.debug(f"Message delivered to {device_id}: {message.topic}")
            
            # Handle QoS levels
            if message.qos == QoSLevel.AT_LEAST_ONCE:
                # Store for acknowledgment
                ack_id = f"{device_id}_{message.message_id}"
                self.pending_acks[ack_id] = {
                    'message': message,
                    'device_id': device_id,
                    'timestamp': datetime.now(),
                    'retry_count': 0
                }
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deliver message to {device_id}: {str(e)}")
            return False
    
    def _send_retained_messages(self, device_id: str, topic: str):
        """Send retained messages to newly subscribed device"""
        try:
            for retained_topic, retained_message in self.retained_messages.items():
                if self._topic_matches(retained_topic, topic):
                    self._deliver_message(device_id, retained_message)
            
        except Exception as e:
            logger.error(f"Failed to send retained messages to {device_id}: {str(e)}")
    
    def _heartbeat_loop(self):
        """
        Heartbeat and cleanup loop
        Mumbai local train punctuality check की तरह
        """
        logger.info("Heartbeat manager started")
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check for offline devices (no activity for 5 minutes)
                timeout_threshold = current_time - timedelta(minutes=5)
                offline_devices = []
                
                for device_id, device in self.connected_devices.items():
                    if device.last_seen < timeout_threshold and device.is_online:
                        offline_devices.append(device_id)
                
                # Mark offline devices
                for device_id in offline_devices:
                    device = self.connected_devices[device_id]
                    device.is_online = False
                    logger.warning(f"Device {device_id} marked offline due to inactivity")
                
                # Clean up old pending acknowledgments
                expired_acks = []
                ack_timeout = current_time - timedelta(minutes=2)
                
                for ack_id, ack_info in self.pending_acks.items():
                    if ack_info['timestamp'] < ack_timeout:
                        expired_acks.append(ack_id)
                
                for ack_id in expired_acks:
                    del self.pending_acks[ack_id]
                
                # Clean up old message history
                if len(self.message_history) > 8000:
                    # Remove oldest 2000 messages
                    for _ in range(2000):
                        if self.message_history:
                            self.message_history.popleft()
                
                time.sleep(30)  # Run every 30 seconds
                
            except Exception as e:
                logger.error(f"Heartbeat loop error: {str(e)}")
                time.sleep(5)
        
        logger.info("Heartbeat manager stopped")
    
    def get_broker_stats(self) -> Dict[str, Any]:
        """Get comprehensive broker statistics"""
        try:
            current_time = datetime.now()
            uptime = current_time - self.stats['uptime_start']
            
            # Calculate rates
            uptime_hours = uptime.total_seconds() / 3600
            if uptime_hours > 0:
                message_rate = self.stats['messages_received'] / uptime_hours
                throughput_mbps = (self.stats['bytes_transferred'] / 1024 / 1024) / uptime_hours
            else:
                message_rate = 0
                throughput_mbps = 0
            
            # Device statistics
            online_devices = sum(1 for device in self.connected_devices.values() if device.is_online)
            offline_devices = len(self.connected_devices) - online_devices
            
            # Topic statistics
            active_topics = len(self.topic_subscribers)
            total_subscriptions = sum(len(subs) for subs in self.topic_subscribers.values())
            
            return {
                "broker_info": {
                    "broker_id": self.broker_id,
                    "location": self.location,
                    "port": self.port,
                    "uptime_hours": round(uptime_hours, 2),
                    "status": "running" if self.running else "stopped"
                },
                "device_stats": {
                    "total_devices": len(self.connected_devices),
                    "online_devices": online_devices,
                    "offline_devices": offline_devices,
                    "peak_connections": self.stats['peak_connections'],
                    "device_types": dict(self.stats['device_type_stats'])
                },
                "message_stats": {
                    "messages_received": self.stats['messages_received'],
                    "messages_published": self.stats['messages_published'], 
                    "messages_delivered": self.stats['messages_delivered'],
                    "message_rate_per_hour": round(message_rate, 2),
                    "pending_acks": len(self.pending_acks),
                    "message_history_size": len(self.message_history)
                },
                "topic_stats": {
                    "active_topics": active_topics,
                    "total_subscriptions": total_subscriptions,
                    "retained_messages": len(self.retained_messages),
                    "popular_topics": dict(list(self.stats['topic_stats'].most_common(5)))
                },
                "performance_stats": {
                    "bytes_transferred": self.stats['bytes_transferred'],
                    "throughput_mb_per_hour": round(throughput_mbps, 2),
                    "queue_size": self.message_queue.qsize()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get broker stats: {str(e)}")
            return {"error": str(e)}
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about specific device"""
        try:
            if device_id not in self.connected_devices:
                return None
            
            device = self.connected_devices[device_id]
            
            return {
                "device_id": device.device_id,
                "device_type": device.device_type.value,
                "location": device.location,
                "is_online": device.is_online,
                "last_seen": device.last_seen.isoformat(),
                "message_count": device.message_count,
                "subscribed_topics": list(device.subscribed_topics),
                "published_topics": list(device.published_topics),
                "battery_level": device.battery_level
            }
            
        except Exception as e:
            logger.error(f"Failed to get device info for {device_id}: {str(e)}")
            return None

# Simulation classes for testing
class MQTTDeviceSimulator:
    """
    MQTT Device Simulator - Mumbai IoT devices की तरह behavior simulate करना
    """
    
    def __init__(self, device: EdgeDevice, broker: MQTTEdgeBroker):
        """Initialize device simulator"""
        self.device = device
        self.broker = broker
        self.running = False
        self.simulation_thread = None
        
        # Mumbai-specific device behaviors
        self.device_behaviors = {
            DeviceType.SENSOR: {
                'publish_interval_seconds': 30,    # Every 30 seconds
                'topics': [f'sensors/{device.location}/temperature', f'sensors/{device.location}/humidity'],
                'payload_generator': self._generate_sensor_data
            },
            DeviceType.ACTUATOR: {
                'publish_interval_seconds': 60,    # Every minute
                'topics': [f'actuators/{device.location}/status'],
                'payload_generator': self._generate_actuator_data
            },
            DeviceType.GATEWAY: {
                'publish_interval_seconds': 120,   # Every 2 minutes
                'topics': [f'gateways/{device.location}/stats'],
                'payload_generator': self._generate_gateway_data
            },
            DeviceType.CAMERA: {
                'publish_interval_seconds': 300,   # Every 5 minutes
                'topics': [f'cameras/{device.location}/status'],
                'payload_generator': self._generate_camera_data
            },
            DeviceType.VEHICLE: {
                'publish_interval_seconds': 10,    # Every 10 seconds
                'topics': [f'vehicles/{device.device_id}/location', f'vehicles/{device.device_id}/status'],
                'payload_generator': self._generate_vehicle_data
            }
        }
    
    def start_simulation(self):
        """Start device simulation"""
        if self.running:
            return
        
        self.running = True
        
        # Connect to broker
        success = self.broker.connect_device(self.device)
        if not success:
            logger.error(f"Failed to connect device {self.device.device_id}")
            return
        
        # Subscribe to relevant topics
        self._setup_subscriptions()
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(
            target=self._simulation_loop,
            daemon=True,
            name=f"DeviceSim-{self.device.device_id}"
        )
        self.simulation_thread.start()
        
        logger.info(f"Device simulation started: {self.device.device_id}")
    
    def stop_simulation(self):
        """Stop device simulation"""
        if not self.running:
            return
        
        self.running = False
        self.broker.disconnect_device(self.device.device_id)
        
        logger.info(f"Device simulation stopped: {self.device.device_id}")
    
    def _setup_subscriptions(self):
        """Setup topic subscriptions for device"""
        # Subscribe to device-specific command topics
        command_topic = f'commands/{self.device.device_id}/+'
        self.broker.subscribe_device(self.device.device_id, command_topic)
        
        # Subscribe to broadcast topics
        broadcast_topics = [
            'broadcast/emergency',
            'broadcast/weather_alert',
            f'local/{self.device.location}/announcements'
        ]
        
        for topic in broadcast_topics:
            self.broker.subscribe_device(self.device.device_id, topic)
    
    def _simulation_loop(self):
        """Main device simulation loop"""
        behavior = self.device_behaviors.get(self.device.device_type)
        if not behavior:
            logger.error(f"No behavior defined for device type: {self.device.device_type}")
            return
        
        interval = behavior['publish_interval_seconds']
        topics = behavior['topics']
        payload_generator = behavior['payload_generator']
        
        while self.running:
            try:
                # Generate and publish data
                for topic in topics:
                    payload = payload_generator()
                    self.broker.publish_message(
                        self.device.device_id,
                        topic,
                        payload,
                        qos=QoSLevel.AT_LEAST_ONCE
                    )
                
                # Update battery level simulation
                if self.device.battery_level is not None:
                    self.device.battery_level = max(0, self.device.battery_level - 0.1)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Device simulation error for {self.device.device_id}: {str(e)}")
                time.sleep(5)  # Brief pause on error
    
    def _generate_sensor_data(self) -> str:
        """Generate sensor data payload"""
        import random
        
        # Mumbai weather simulation
        base_temp = 28 + random.gauss(0, 3)  # 28°C ± 3°C
        humidity = 70 + random.gauss(0, 10)   # 70% ± 10%
        
        data = {
            "device_id": self.device.device_id,
            "timestamp": datetime.now().isoformat(),
            "temperature": round(base_temp, 1),
            "humidity": round(max(0, min(100, humidity)), 1),
            "battery": self.device.battery_level
        }
        
        return json.dumps(data)
    
    def _generate_actuator_data(self) -> str:
        """Generate actuator status data"""
        import random
        
        data = {
            "device_id": self.device.device_id,
            "timestamp": datetime.now().isoformat(),
            "status": random.choice(["on", "off", "standby"]),
            "power_consumption": round(random.uniform(10, 100), 2),
            "cycles_completed": random.randint(0, 1000)
        }
        
        return json.dumps(data)
    
    def _generate_gateway_data(self) -> str:
        """Generate gateway statistics"""
        import random
        
        data = {
            "device_id": self.device.device_id,
            "timestamp": datetime.now().isoformat(),
            "connected_devices": random.randint(5, 50),
            "cpu_usage": round(random.uniform(20, 80), 1),
            "memory_usage": round(random.uniform(30, 90), 1),
            "network_throughput_mbps": round(random.uniform(1, 100), 2)
        }
        
        return json.dumps(data)
    
    def _generate_camera_data(self) -> str:
        """Generate camera status data"""
        import random
        
        data = {
            "device_id": self.device.device_id,
            "timestamp": datetime.now().isoformat(),
            "status": "recording" if random.random() > 0.3 else "idle",
            "storage_used_gb": round(random.uniform(100, 500), 1),
            "resolution": random.choice(["720p", "1080p", "4K"]),
            "motion_detected": random.random() > 0.7
        }
        
        return json.dumps(data)
    
    def _generate_vehicle_data(self) -> str:
        """Generate vehicle tracking data"""
        import random
        
        # Mumbai coordinates (approximate)
        base_lat = 19.0760  # Mumbai latitude
        base_lon = 72.8777  # Mumbai longitude
        
        data = {
            "device_id": self.device.device_id,
            "timestamp": datetime.now().isoformat(),
            "latitude": base_lat + random.uniform(-0.1, 0.1),
            "longitude": base_lon + random.uniform(-0.1, 0.1),
            "speed_kmh": round(random.uniform(0, 60), 1),
            "fuel_level": round(random.uniform(20, 100), 1),
            "engine_status": "running" if random.random() > 0.2 else "stopped"
        }
        
        return json.dumps(data)

# Example usage and comprehensive testing
async def main():
    """
    Comprehensive MQTT Edge Broker testing
    Mumbai IoT ecosystem simulation
    """
    print("📡 MQTT Edge Broker - Mumbai IoT Network Simulation")
    print("=" * 65)
    
    # Initialize broker
    broker = MQTTEdgeBroker("mumbai-edge-01", "Mumbai Central")
    broker.start()
    
    print(f"✅ MQTT Broker started: {broker.broker_id}")
    
    # Create various Mumbai IoT devices
    devices = [
        EdgeDevice(
            device_id="temp_sensor_andheri_01",
            device_type=DeviceType.SENSOR,
            location="Andheri East",
            last_seen=datetime.now(),
            subscribed_topics=set(),
            published_topics=set(),
            battery_level=95.0
        ),
        EdgeDevice(
            device_id="traffic_camera_bandra_01", 
            device_type=DeviceType.CAMERA,
            location="Bandra West",
            last_seen=datetime.now(),
            subscribed_topics=set(),
            published_topics=set()
        ),
        EdgeDevice(
            device_id="gateway_thane_central",
            device_type=DeviceType.GATEWAY,
            location="Thane",
            last_seen=datetime.now(),
            subscribed_topics=set(),
            published_topics=set()
        ),
        EdgeDevice(
            device_id="taxi_mumbai_4587",
            device_type=DeviceType.VEHICLE,
            location="South Mumbai",
            last_seen=datetime.now(),
            subscribed_topics=set(),
            published_topics=set(),
            battery_level=87.5
        ),
        EdgeDevice(
            device_id="street_light_controller_01",
            device_type=DeviceType.ACTUATOR,
            location="Powai",
            last_seen=datetime.now(),
            subscribed_topics=set(),
            published_topics=set()
        )
    ]
    
    # Start device simulations
    simulators = []
    for device in devices:
        simulator = MQTTDeviceSimulator(device, broker)
        simulator.start_simulation()
        simulators.append(simulator)
        
        print(f"🔌 Device connected: {device.device_id} ({device.device_type.value})")
    
    print(f"\n🚀 Simulating Mumbai IoT network for 30 seconds...")
    
    # Let simulation run
    await asyncio.sleep(30)
    
    # Get broker statistics
    stats = broker.get_broker_stats()
    
    print(f"\n📊 MQTT Broker Performance Report:")
    print("=" * 45)
    
    # Broker info
    broker_info = stats["broker_info"]
    print(f"Broker: {broker_info['broker_id']} @ {broker_info['location']}")
    print(f"Uptime: {broker_info['uptime_hours']} hours")
    print(f"Status: {broker_info['status']}")
    
    # Device statistics
    device_stats = stats["device_stats"]
    print(f"\n🔗 Device Statistics:")
    print(f"• Total Devices: {device_stats['total_devices']}")
    print(f"• Online Devices: {device_stats['online_devices']}")
    print(f"• Peak Connections: {device_stats['peak_connections']}")
    
    print(f"• Device Types:")
    for device_type, count in device_stats['device_types'].items():
        print(f"  - {device_type}: {count}")
    
    # Message statistics
    message_stats = stats["message_stats"]
    print(f"\n📬 Message Statistics:")
    print(f"• Messages Received: {message_stats['messages_received']}")
    print(f"• Messages Published: {message_stats['messages_published']}")
    print(f"• Messages Delivered: {message_stats['messages_delivered']}")
    print(f"• Message Rate: {message_stats['message_rate_per_hour']:.1f}/hour")
    print(f"• Pending Acknowledgments: {message_stats['pending_acks']}")
    
    # Topic statistics
    topic_stats = stats["topic_stats"]
    print(f"\n📢 Topic Statistics:")
    print(f"• Active Topics: {topic_stats['active_topics']}")
    print(f"• Total Subscriptions: {topic_stats['total_subscriptions']}")
    print(f"• Retained Messages: {topic_stats['retained_messages']}")
    
    if topic_stats['popular_topics']:
        print(f"• Popular Topics:")
        for topic, count in topic_stats['popular_topics'].items():
            print(f"  - {topic}: {count} messages")
    
    # Performance statistics
    performance_stats = stats["performance_stats"]
    print(f"\n⚡ Performance Statistics:")
    print(f"• Bytes Transferred: {performance_stats['bytes_transferred']:,}")
    print(f"• Throughput: {performance_stats['throughput_mb_per_hour']:.2f} MB/hour")
    print(f"• Queue Size: {performance_stats['queue_size']}")
    
    # Individual device information
    print(f"\n👥 Individual Device Status:")
    print("-" * 40)
    
    for device in devices:
        device_info = broker.get_device_info(device.device_id)
        if device_info:
            status_emoji = "🟢" if device_info['is_online'] else "🔴"
            print(f"{status_emoji} {device_info['device_id']}")
            print(f"   Type: {device_info['device_type']}")
            print(f"   Location: {device_info['location']}")
            print(f"   Messages Sent: {device_info['message_count']}")
            print(f"   Topics Published: {len(device_info['published_topics'])}")
            print(f"   Topics Subscribed: {len(device_info['subscribed_topics'])}")
            if device_info['battery_level'] is not None:
                print(f"   Battery: {device_info['battery_level']:.1f}%")
    
    # Cost analysis
    print(f"\n💰 Cost Analysis (30-second simulation):")
    print("-" * 35)
    
    local_mqtt_cost = message_stats['messages_received'] * 0.01  # ₹0.01 per message
    cloud_mqtt_cost = message_stats['messages_received'] * 0.5   # ₹0.5 per message
    savings = cloud_mqtt_cost - local_mqtt_cost
    
    print(f"Local MQTT Cost: ₹{local_mqtt_cost:.2f}")
    print(f"Cloud MQTT Cost: ₹{cloud_mqtt_cost:.2f}")
    print(f"Cost Savings: ₹{savings:.2f}")
    print(f"Savings Percentage: {(savings/cloud_mqtt_cost)*100:.1f}%")
    
    # Scale to daily estimates
    daily_messages = message_stats['messages_received'] * (24 * 60 * 60) / 30
    daily_savings = savings * (24 * 60 * 60) / 30
    
    print(f"\n📈 Daily Projections:")
    print(f"Estimated Daily Messages: {daily_messages:,.0f}")
    print(f"Estimated Daily Savings: ₹{daily_savings:,.2f}")
    print(f"Monthly Savings: ₹{daily_savings * 30:,.2f}")
    
    # Business benefits
    print(f"\n🎯 Business Benefits:")
    print("• Reduced cloud messaging costs by 98%")
    print("• Improved message delivery latency")  
    print("• Better reliability during network issues")
    print("• Local data processing capabilities")
    print("• Compliance with data sovereignty requirements")
    
    # Stop simulations
    print(f"\n🛑 Stopping device simulations...")
    for simulator in simulators:
        simulator.stop_simulation()
    
    broker.stop()
    
    print(f"\n✅ MQTT Edge Broker simulation completed successfully!")
    print(f"📡 Mumbai IoT network demonstrated edge messaging benefits!")

if __name__ == "__main__":
    asyncio.run(main())
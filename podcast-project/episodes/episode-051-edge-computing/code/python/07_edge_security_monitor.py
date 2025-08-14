#!/usr/bin/env python3
"""
Edge Security Monitor - एज कंप्यूटिंग सिक्यूरिटी मॉनिटरिंग
Mumbai police chowki की तरह - local area security monitoring

Real-world inspired by Cisco Edge Security, Palo Alto Networks Prisma
Use cases: IoT device security, intrusion detection, anomaly monitoring
Cost: Edge security ₹5 per device vs Cloud security ₹50 per device monthly
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import threading
from collections import defaultdict, deque
import statistics
import ipaddress
import re
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = "निम्न"          # Low risk
    MEDIUM = "मध्यम"       # Medium risk
    HIGH = "उच्च"          # High risk
    CRITICAL = "गंभीर"     # Critical risk

class SecurityEventType(Enum):
    """Types of security events"""
    INTRUSION_ATTEMPT = "घुसपैठ प्रयास"           # Unauthorized access attempt
    MALWARE_DETECTED = "मालवेयर का पता लगाया"    # Malware detection
    ANOMALOUS_BEHAVIOR = "असामान्य व्यवहार"       # Unusual behavior pattern
    DATA_BREACH = "डेटा उल्लंघन"                  # Data breach attempt
    DDoS_ATTACK = "डीडॉएस हमला"                   # DDoS attack
    PRIVILEGE_ESCALATION = "विशेषाधिकार वृद्धि"   # Privilege escalation
    SUSPICIOUS_NETWORK = "संदिग्ध नेटवर्क"        # Suspicious network activity

class DeviceStatus(Enum):
    """Device security status"""
    SECURE = "सुरक्षित"           # Device is secure
    VULNERABLE = "असुरक्षित"      # Device has vulnerabilities
    COMPROMISED = "संक्रमित"      # Device is compromised
    QUARANTINED = "क्वारंटीन"     # Device is quarantined

@dataclass
class SecurityEvent:
    """Security event representation"""
    event_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    source_device: str
    source_ip: str
    target_device: Optional[str]
    target_ip: Optional[str]
    timestamp: datetime
    description: str
    details: Dict[str, Any]
    resolved: bool = False
    response_actions: List[str] = field(default_factory=list)

@dataclass
class SecurityDevice:
    """Device under security monitoring"""
    device_id: str
    device_name: str
    device_type: str
    ip_address: str
    mac_address: str
    location: str
    status: DeviceStatus
    last_seen: datetime
    security_score: float  # 0-100 score
    vulnerabilities: List[str] = field(default_factory=list)
    installed_patches: List[str] = field(default_factory=list)
    network_activity: Dict[str, Any] = field(default_factory=dict)

class EdgeSecurityMonitor:
    """
    Edge Security Monitor - Mumbai police station की तरह
    Local area में सभी devices की security monitoring
    """
    
    def __init__(self, monitor_id: str, location: str = "Mumbai", network_range: str = "192.168.1.0/24"):
        """
        Initialize Edge Security Monitor
        Args:
            monitor_id: Unique monitor identifier
            location: Geographic location
            network_range: Network range to monitor (CIDR notation)
        """
        self.monitor_id = monitor_id
        self.location = location
        self.network_range = ipaddress.IPv4Network(network_range)
        
        # Device tracking
        self.monitored_devices: Dict[str, SecurityDevice] = {}
        self.device_baselines: Dict[str, Dict[str, Any]] = {}
        
        # Security events
        self.security_events: deque = deque(maxlen=10000)  # Last 10k events
        self.active_threats: Dict[str, SecurityEvent] = {}
        self.quarantined_devices: Set[str] = set()
        
        # Monitoring rules
        self.security_rules = {}
        self.threat_signatures = {}
        self.anomaly_thresholds = {}
        
        # Performance metrics
        self.stats = {
            'total_events': 0,
            'events_by_type': defaultdict(int),
            'events_by_threat_level': defaultdict(int),
            'devices_scanned': 0,
            'vulnerabilities_found': 0,
            'threats_blocked': 0,
            'false_positives': 0,
            'response_times': deque(maxlen=1000),
            'uptime_start': datetime.now()
        }
        
        # Threading
        self.running = False
        self.monitor_tasks = []
        
        # Mumbai-specific security patterns
        self._initialize_mumbai_security_rules()
        
        logger.info(f"Edge Security Monitor initialized: {monitor_id} @ {location}")
        logger.info(f"Monitoring network range: {network_range}")
    
    def _initialize_mumbai_security_rules(self):
        """Initialize Mumbai-specific security monitoring rules"""
        
        # Rule 1: High-frequency authentication failures (common in Mumbai offices)
        self.security_rules['auth_failure_burst'] = {
            'name': 'Authentication Failure Burst',
            'description': 'Multiple auth failures from same IP within 5 minutes',
            'threshold': 5,  # 5 failures
            'time_window_seconds': 300,  # 5 minutes
            'threat_level': ThreatLevel.HIGH,
            'event_type': SecurityEventType.INTRUSION_ATTEMPT,
            'response_actions': ['block_ip', 'alert_admin', 'log_incident']
        }
        
        # Rule 2: Unusual data transfer patterns (data exfiltration)
        self.security_rules['data_exfiltration'] = {
            'name': 'Potential Data Exfiltration',
            'description': 'Unusually large data upload from device',
            'threshold': 1000,  # 1GB
            'time_window_seconds': 1800,  # 30 minutes
            'threat_level': ThreatLevel.CRITICAL,
            'event_type': SecurityEventType.DATA_BREACH,
            'response_actions': ['quarantine_device', 'block_traffic', 'emergency_alert']
        }
        
        # Rule 3: IoT device communication anomalies
        self.security_rules['iot_anomaly'] = {
            'name': 'IoT Device Anomaly',
            'description': 'IoT device communicating with unknown servers',
            'threshold': 3,  # 3 unknown destinations
            'time_window_seconds': 600,  # 10 minutes
            'threat_level': ThreatLevel.MEDIUM,
            'event_type': SecurityEventType.ANOMALOUS_BEHAVIOR,
            'response_actions': ['investigate_traffic', 'update_whitelist']
        }
        
        # Rule 4: Port scanning detection
        self.security_rules['port_scan'] = {
            'name': 'Port Scanning Activity',
            'description': 'Device scanning multiple ports on network',
            'threshold': 20,  # 20 different ports
            'time_window_seconds': 120,  # 2 minutes
            'threat_level': ThreatLevel.HIGH,
            'event_type': SecurityEventType.INTRUSION_ATTEMPT,
            'response_actions': ['block_scanner', 'alert_security_team']
        }
        
        # Rule 5: Time-based access violations (after office hours)
        self.security_rules['after_hours_access'] = {
            'name': 'After Hours Access',
            'description': 'Device access outside business hours',
            'business_hours_start': 9,  # 9 AM
            'business_hours_end': 18,   # 6 PM
            'threat_level': ThreatLevel.MEDIUM,
            'event_type': SecurityEventType.SUSPICIOUS_NETWORK,
            'response_actions': ['log_access', 'verify_user']
        }
        
        # Threat signatures (simplified)
        self.threat_signatures = {
            'sql_injection': r'(union|select|insert|delete|drop|create|alter)\s+.*from',
            'xss_attempt': r'<script.*?>.*?</script>|javascript:|onload=|onerror=',
            'path_traversal': r'\.\./.*\.\./|\.\.\\.*\.\.\\',
            'command_injection': r'(;|\||\&\&|\|\|).*?(ls|dir|cat|type|ping|nslookup)',
            'malware_signature': r'(wannacry|petya|locky|zeus|conficker)'
        }
        
        # Anomaly detection thresholds
        self.anomaly_thresholds = {
            'cpu_usage': 85.0,           # 85% CPU usage
            'memory_usage': 90.0,        # 90% memory usage
            'network_connections': 100,   # 100+ concurrent connections
            'bandwidth_usage': 1000,     # 1Gbps usage
            'login_frequency': 10        # 10+ logins per hour
        }
        
        logger.info(f"Initialized {len(self.security_rules)} security rules")
    
    async def start_monitoring(self):
        """Start security monitoring"""
        if self.running:
            logger.warning("Security monitor already running")
            return
        
        self.running = True
        
        # Start monitoring tasks
        self.monitor_tasks = [
            asyncio.create_task(self._device_discovery_loop()),
            asyncio.create_task(self._threat_detection_loop()),
            asyncio.create_task(self._vulnerability_scanning_loop()),
            asyncio.create_task(self._anomaly_detection_loop()),
            asyncio.create_task(self._incident_response_loop())
        ]
        
        logger.info("Edge Security Monitor started")
    
    async def stop_monitoring(self):
        """Stop security monitoring"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel monitoring tasks
        for task in self.monitor_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        try:
            await asyncio.gather(*self.monitor_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error stopping monitoring tasks: {str(e)}")
        
        logger.info("Edge Security Monitor stopped")
    
    async def register_device(self, device: SecurityDevice) -> bool:
        """
        Register device for security monitoring
        Mumbai area में new resident registration की तरह
        """
        try:
            # Validate IP address is in monitored range
            device_ip = ipaddress.IPv4Address(device.ip_address)
            if device_ip not in self.network_range:
                logger.warning(f"Device IP {device.ip_address} outside monitored range")
                return False
            
            # Store device
            self.monitored_devices[device.device_id] = device
            
            # Initialize baseline behavior
            self.device_baselines[device.device_id] = {
                'normal_traffic_patterns': {},
                'typical_connections': set(),
                'average_cpu_usage': 0.0,
                'average_memory_usage': 0.0,
                'login_patterns': {},
                'baseline_established': False,
                'baseline_start_time': datetime.now()
            }
            
            # Perform initial security assessment
            await self._perform_initial_security_scan(device)
            
            logger.info(f"Device registered for monitoring: {device.device_id} ({device.ip_address})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register device {device.device_id}: {str(e)}")
            return False
    
    async def _perform_initial_security_scan(self, device: SecurityDevice):
        """Perform initial security assessment of device"""
        try:
            scan_results = {
                'open_ports': [],
                'running_services': [],
                'os_fingerprint': 'Unknown',
                'vulnerabilities': [],
                'security_score': 100.0
            }
            
            # Simulate port scanning
            common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
            for port in common_ports:
                # Simulate 30% chance of port being open
                if hash(f"{device.device_id}_{port}") % 10 < 3:
                    scan_results['open_ports'].append(port)
                    
                    # Map ports to services
                    service_map = {
                        22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
                        80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
                        993: 'IMAPS', 995: 'POP3S'
                    }
                    if port in service_map:
                        scan_results['running_services'].append(service_map[port])
            
            # Simulate vulnerability detection
            potential_vulnerabilities = [
                'Outdated SSL/TLS version',
                'Weak SSH configuration',
                'Missing security patches',
                'Default credentials',
                'Unnecessary services running',
                'Weak firewall rules'
            ]
            
            # Random vulnerabilities based on device type
            vuln_count = hash(device.device_id) % 4  # 0-3 vulnerabilities
            device.vulnerabilities = potential_vulnerabilities[:vuln_count]
            scan_results['vulnerabilities'] = device.vulnerabilities
            
            # Calculate security score
            score_deductions = {
                'open_ports': len(scan_results['open_ports']) * 5,
                'vulnerabilities': len(device.vulnerabilities) * 15,
                'telnet_open': 20 if 23 in scan_results['open_ports'] else 0,
                'default_services': 10 if 'SSH' in scan_results['running_services'] and 22 in scan_results['open_ports'] else 0
            }
            
            total_deduction = sum(score_deductions.values())
            device.security_score = max(20.0, 100.0 - total_deduction)
            
            # Update device status based on score
            if device.security_score >= 80:
                device.status = DeviceStatus.SECURE
            elif device.security_score >= 60:
                device.status = DeviceStatus.VULNERABLE
            else:
                device.status = DeviceStatus.COMPROMISED
            
            # Log scan results
            logger.info(f"Initial scan completed for {device.device_id}:")
            logger.info(f"  Security Score: {device.security_score:.1f}")
            logger.info(f"  Open Ports: {len(scan_results['open_ports'])}")
            logger.info(f"  Vulnerabilities: {len(device.vulnerabilities)}")
            logger.info(f"  Status: {device.status.value}")
            
            self.stats['devices_scanned'] += 1
            self.stats['vulnerabilities_found'] += len(device.vulnerabilities)
            
        except Exception as e:
            logger.error(f"Initial security scan failed for {device.device_id}: {str(e)}")
    
    async def _device_discovery_loop(self):
        """
        Continuous device discovery and monitoring
        Mumbai police patrol की तरह - regular area checking
        """
        logger.info("Device discovery loop started")
        
        while self.running:
            try:
                # Simulate discovering new devices on network
                await self._discover_network_devices()
                
                # Check for devices that have gone offline
                await self._check_device_connectivity()
                
                # Update device baselines for established devices
                await self._update_device_baselines()
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Device discovery error: {str(e)}")
                await asyncio.sleep(10)
        
        logger.info("Device discovery loop stopped")
    
    async def _discover_network_devices(self):
        """Simulate network device discovery"""
        try:
            # Simulate finding new devices (in production, this would use actual network scanning)
            import random
            
            # Occasionally discover new devices
            if random.random() < 0.1:  # 10% chance per minute
                device_types = ['laptop', 'phone', 'tablet', 'iot_sensor', 'smart_tv', 'printer']
                device_type = random.choice(device_types)
                
                # Generate new device
                device_id = f"device_{device_type}_{uuid.uuid4().hex[:8]}"
                ip_octets = str(self.network_range).split('.')
                ip_address = f"{'.'.join(ip_octets[:3])}.{random.randint(100, 254)}"
                
                # Check if device already discovered
                if not any(d.ip_address == ip_address for d in self.monitored_devices.values()):
                    new_device = SecurityDevice(
                        device_id=device_id,
                        device_name=f"Mumbai {device_type.title()}",
                        device_type=device_type,
                        ip_address=ip_address,
                        mac_address=f"00:11:22:33:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                        location=self.location,
                        status=DeviceStatus.SECURE,
                        last_seen=datetime.now(),
                        security_score=100.0
                    )
                    
                    await self.register_device(new_device)
                    logger.info(f"New device discovered: {device_id} ({ip_address})")
                    
        except Exception as e:
            logger.error(f"Device discovery failed: {str(e)}")
    
    async def _check_device_connectivity(self):
        """Check if monitored devices are still connected"""
        try:
            current_time = datetime.now()
            offline_threshold = current_time - timedelta(minutes=5)
            
            for device_id, device in self.monitored_devices.items():
                # Simulate device connectivity check
                import random
                if random.random() < 0.95:  # 95% devices remain online
                    device.last_seen = current_time
                else:
                    if device.last_seen < offline_threshold:
                        logger.warning(f"Device {device_id} appears to be offline")
                        
                        # Create security event for unexpected disconnection
                        if device.status == DeviceStatus.COMPROMISED:
                            event = SecurityEvent(
                                event_id=f"disconnect_{device_id}_{int(time.time())}",
                                event_type=SecurityEventType.SUSPICIOUS_NETWORK,
                                threat_level=ThreatLevel.HIGH,
                                source_device=device_id,
                                source_ip=device.ip_address,
                                target_device=None,
                                target_ip=None,
                                timestamp=current_time,
                                description="Compromised device went offline unexpectedly",
                                details={'last_seen': device.last_seen.isoformat()}
                            )
                            await self._handle_security_event(event)
                        
        except Exception as e:
            logger.error(f"Device connectivity check failed: {str(e)}")
    
    async def _update_device_baselines(self):
        """Update baseline behavior patterns for devices"""
        try:
            for device_id, baseline in self.device_baselines.items():
                if device_id in self.monitored_devices:
                    device = self.monitored_devices[device_id]
                    
                    # Simulate updating baseline patterns
                    import random
                    
                    # Update traffic patterns
                    baseline['normal_traffic_patterns'] = {
                        'avg_bytes_per_hour': random.randint(10000, 100000),
                        'peak_hours': [9, 10, 11, 14, 15, 16],  # Business hours
                        'common_protocols': ['HTTP', 'HTTPS', 'DNS'],
                        'connection_frequency': random.randint(10, 50)
                    }
                    
                    # Update typical connections
                    baseline['typical_connections'].update([
                        '8.8.8.8',  # Google DNS
                        '1.1.1.1',  # Cloudflare DNS
                        '10.0.0.1'  # Local gateway
                    ])
                    
                    # Update resource usage
                    baseline['average_cpu_usage'] = random.uniform(20, 60)
                    baseline['average_memory_usage'] = random.uniform(30, 70)
                    
                    # Mark baseline as established after 24 hours
                    if not baseline['baseline_established']:
                        time_since_start = datetime.now() - baseline['baseline_start_time']
                        if time_since_start.total_seconds() > 86400:  # 24 hours
                            baseline['baseline_established'] = True
                            logger.info(f"Baseline established for device {device_id}")
                            
        except Exception as e:
            logger.error(f"Baseline update failed: {str(e)}")
    
    async def _threat_detection_loop(self):
        """
        Main threat detection loop
        Mumbai security patrol की तरह - continuous threat monitoring
        """
        logger.info("Threat detection loop started")
        
        while self.running:
            try:
                # Simulate network traffic analysis
                await self._analyze_network_traffic()
                
                # Check for rule violations
                await self._check_security_rules()
                
                # Scan for malware signatures
                await self._scan_for_malware()
                
                await asyncio.sleep(30)  # Run every 30 seconds
                
            except Exception as e:
                logger.error(f"Threat detection error: {str(e)}")
                await asyncio.sleep(10)
        
        logger.info("Threat detection loop stopped")
    
    async def _analyze_network_traffic(self):
        """Analyze network traffic for threats"""
        try:
            import random
            
            for device_id, device in self.monitored_devices.items():
                if device.status == DeviceStatus.QUARANTINED:
                    continue
                
                # Simulate traffic analysis
                traffic_data = {
                    'bytes_sent': random.randint(1000, 50000),
                    'bytes_received': random.randint(5000, 100000),
                    'connections': random.randint(1, 20),
                    'protocols': random.choices(['HTTP', 'HTTPS', 'DNS', 'FTP', 'SSH'], k=3),
                    'destinations': [f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}" for _ in range(3)]
                }
                
                device.network_activity = traffic_data
                
                # Check for suspicious patterns
                if traffic_data['bytes_sent'] > 40000:  # High upload volume
                    # Potential data exfiltration
                    if await self._check_rule_violation('data_exfiltration', device, traffic_data):
                        event = SecurityEvent(
                            event_id=f"exfiltration_{device_id}_{int(time.time())}",
                            event_type=SecurityEventType.DATA_BREACH,
                            threat_level=ThreatLevel.CRITICAL,
                            source_device=device_id,
                            source_ip=device.ip_address,
                            target_device=None,
                            target_ip=None,
                            timestamp=datetime.now(),
                            description="Potential data exfiltration detected",
                            details=traffic_data
                        )
                        await self._handle_security_event(event)
                
                # Check for unusual destinations
                baseline = self.device_baselines.get(device_id, {})
                if baseline.get('baseline_established', False):
                    typical_destinations = baseline.get('typical_connections', set())
                    unknown_destinations = [dest for dest in traffic_data['destinations'] if dest not in typical_destinations]
                    
                    if len(unknown_destinations) > 2:  # Too many unknown destinations
                        event = SecurityEvent(
                            event_id=f"unknown_dest_{device_id}_{int(time.time())}",
                            event_type=SecurityEventType.ANOMALOUS_BEHAVIOR,
                            threat_level=ThreatLevel.MEDIUM,
                            source_device=device_id,
                            source_ip=device.ip_address,
                            target_device=None,
                            target_ip=None,
                            timestamp=datetime.now(),
                            description="Device communicating with unknown destinations",
                            details={'unknown_destinations': unknown_destinations}
                        )
                        await self._handle_security_event(event)
                        
        except Exception as e:
            logger.error(f"Network traffic analysis failed: {str(e)}")
    
    async def _check_rule_violation(self, rule_name: str, device: SecurityDevice, data: Dict[str, Any]) -> bool:
        """Check if device data violates security rule"""
        try:
            rule = self.security_rules.get(rule_name)
            if not rule:
                return False
            
            # Simple rule checking logic (can be extended)
            if rule_name == 'data_exfiltration':
                return data.get('bytes_sent', 0) > rule['threshold']
            elif rule_name == 'iot_anomaly':
                return len(data.get('destinations', [])) > rule['threshold']
            
            return False
            
        except Exception as e:
            logger.error(f"Rule violation check failed: {str(e)}")
            return False
    
    async def _check_security_rules(self):
        """Check all security rules against current device states"""
        try:
            current_time = datetime.now()
            
            # Check time-based rules
            for rule_name, rule in self.security_rules.items():
                if rule_name == 'after_hours_access':
                    current_hour = current_time.hour
                    
                    if not (rule['business_hours_start'] <= current_hour <= rule['business_hours_end']):
                        # Outside business hours - check for unusual activity
                        for device_id, device in self.monitored_devices.items():
                            if device.network_activity.get('connections', 0) > 0:
                                event = SecurityEvent(
                                    event_id=f"after_hours_{device_id}_{int(time.time())}",
                                    event_type=rule['event_type'],
                                    threat_level=rule['threat_level'],
                                    source_device=device_id,
                                    source_ip=device.ip_address,
                                    target_device=None,
                                    target_ip=None,
                                    timestamp=current_time,
                                    description=rule['description'],
                                    details={'current_hour': current_hour, 'activity': device.network_activity},
                                    response_actions=rule['response_actions']
                                )
                                await self._handle_security_event(event)
                                
        except Exception as e:
            logger.error(f"Security rule checking failed: {str(e)}")
    
    async def _scan_for_malware(self):
        """Scan for malware signatures in network traffic"""
        try:
            import random
            
            for device_id, device in self.monitored_devices.items():
                if random.random() < 0.02:  # 2% chance of malware detection per scan
                    malware_types = ['Trojan', 'Ransomware', 'Spyware', 'Adware', 'Rootkit']
                    detected_malware = random.choice(malware_types)
                    
                    event = SecurityEvent(
                        event_id=f"malware_{device_id}_{int(time.time())}",
                        event_type=SecurityEventType.MALWARE_DETECTED,
                        threat_level=ThreatLevel.CRITICAL,
                        source_device=device_id,
                        source_ip=device.ip_address,
                        target_device=None,
                        target_ip=None,
                        timestamp=datetime.now(),
                        description=f"Malware detected: {detected_malware}",
                        details={'malware_type': detected_malware, 'signature_match': True},
                        response_actions=['quarantine_device', 'scan_full_system', 'alert_security']
                    )
                    await self._handle_security_event(event)
                    
        except Exception as e:
            logger.error(f"Malware scanning failed: {str(e)}")
    
    async def _vulnerability_scanning_loop(self):
        """Regular vulnerability scanning of devices"""
        logger.info("Vulnerability scanning loop started")
        
        while self.running:
            try:
                # Scan each device for vulnerabilities
                for device_id, device in list(self.monitored_devices.items()):
                    await self._scan_device_vulnerabilities(device)
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Vulnerability scanning error: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
        
        logger.info("Vulnerability scanning loop stopped")
    
    async def _scan_device_vulnerabilities(self, device: SecurityDevice):
        """Scan individual device for vulnerabilities"""
        try:
            import random
            
            # Simulate vulnerability scan
            new_vulnerabilities = []
            
            # Check for new vulnerabilities (10% chance)
            if random.random() < 0.1:
                potential_new_vulns = [
                    'CVE-2024-001: Buffer overflow in network driver',
                    'CVE-2024-002: SQL injection in web interface',
                    'CVE-2024-003: Cross-site scripting vulnerability',
                    'CVE-2024-004: Privilege escalation in system service',
                    'CVE-2024-005: Remote code execution vulnerability'
                ]
                
                new_vuln = random.choice(potential_new_vulns)
                if new_vuln not in device.vulnerabilities:
                    new_vulnerabilities.append(new_vuln)
                    device.vulnerabilities.append(new_vuln)
                    
                    # Create security event for new vulnerability
                    event = SecurityEvent(
                        event_id=f"vuln_{device.device_id}_{int(time.time())}",
                        event_type=SecurityEventType.ANOMALOUS_BEHAVIOR,
                        threat_level=ThreatLevel.MEDIUM,
                        source_device=device.device_id,
                        source_ip=device.ip_address,
                        target_device=None,
                        target_ip=None,
                        timestamp=datetime.now(),
                        description=f"New vulnerability discovered: {new_vuln}",
                        details={'vulnerability': new_vuln, 'scan_type': 'automatic'},
                        response_actions=['patch_system', 'update_monitoring']
                    )
                    await self._handle_security_event(event)
            
            # Simulate patch installation (20% chance)
            if random.random() < 0.2 and device.vulnerabilities:
                patched_vuln = random.choice(device.vulnerabilities)
                device.vulnerabilities.remove(patched_vuln)
                device.installed_patches.append(f"Patch for {patched_vuln}")
                
                logger.info(f"Vulnerability patched on {device.device_id}: {patched_vuln}")
            
            # Recalculate security score
            base_score = 100.0
            score_deductions = len(device.vulnerabilities) * 10
            device.security_score = max(20.0, base_score - score_deductions)
            
            # Update device status
            if device.security_score >= 80:
                device.status = DeviceStatus.SECURE
            elif device.security_score >= 60:
                device.status = DeviceStatus.VULNERABLE
            else:
                if device.device_id not in self.quarantined_devices:
                    device.status = DeviceStatus.COMPROMISED
                    
        except Exception as e:
            logger.error(f"Vulnerability scan failed for {device.device_id}: {str(e)}")
    
    async def _anomaly_detection_loop(self):
        """Detect anomalous behavior patterns"""
        logger.info("Anomaly detection loop started")
        
        while self.running:
            try:
                await self._detect_behavioral_anomalies()
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Anomaly detection error: {str(e)}")
                await asyncio.sleep(60)
        
        logger.info("Anomaly detection loop stopped")
    
    async def _detect_behavioral_anomalies(self):
        """Detect anomalous behavior in device patterns"""
        try:
            for device_id, device in self.monitored_devices.items():
                baseline = self.device_baselines.get(device_id, {})
                
                if not baseline.get('baseline_established', False):
                    continue  # Skip devices without established baselines
                
                # Check traffic anomalies
                current_traffic = device.network_activity
                baseline_traffic = baseline.get('normal_traffic_patterns', {})
                
                if current_traffic and baseline_traffic:
                    # Compare current vs baseline traffic
                    current_bytes = current_traffic.get('bytes_sent', 0) + current_traffic.get('bytes_received', 0)
                    baseline_bytes = baseline_traffic.get('avg_bytes_per_hour', 50000)
                    
                    # Check for traffic spikes (3x normal)
                    if current_bytes > baseline_bytes * 3:
                        event = SecurityEvent(
                            event_id=f"traffic_spike_{device_id}_{int(time.time())}",
                            event_type=SecurityEventType.ANOMALOUS_BEHAVIOR,
                            threat_level=ThreatLevel.MEDIUM,
                            source_device=device_id,
                            source_ip=device.ip_address,
                            target_device=None,
                            target_ip=None,
                            timestamp=datetime.now(),
                            description="Unusual traffic spike detected",
                            details={
                                'current_bytes': current_bytes,
                                'baseline_bytes': baseline_bytes,
                                'spike_factor': current_bytes / baseline_bytes
                            }
                        )
                        await self._handle_security_event(event)
                
                # Check for unusual connection patterns
                current_connections = current_traffic.get('connections', 0)
                if current_connections > self.anomaly_thresholds['network_connections']:
                    event = SecurityEvent(
                        event_id=f"conn_anomaly_{device_id}_{int(time.time())}",
                        event_type=SecurityEventType.ANOMALOUS_BEHAVIOR,
                        threat_level=ThreatLevel.MEDIUM,
                        source_device=device_id,
                        source_ip=device.ip_address,
                        target_device=None,
                        target_ip=None,
                        timestamp=datetime.now(),
                        description="Unusual number of network connections",
                        details={'connection_count': current_connections}
                    )
                    await self._handle_security_event(event)
                    
        except Exception as e:
            logger.error(f"Behavioral anomaly detection failed: {str(e)}")
    
    async def _handle_security_event(self, event: SecurityEvent):
        """
        Handle detected security event
        Mumbai police response की तरह - immediate action
        """
        try:
            start_time = time.time()
            
            # Store event
            self.security_events.append(event)
            self.active_threats[event.event_id] = event
            
            # Update statistics
            self.stats['total_events'] += 1
            self.stats['events_by_type'][event.event_type.value] += 1
            self.stats['events_by_threat_level'][event.threat_level.value] += 1
            
            # Execute response actions
            for action in event.response_actions:
                await self._execute_response_action(action, event)
            
            response_time = (time.time() - start_time) * 1000
            self.stats['response_times'].append(response_time)
            
            logger.warning(f"Security event handled: {event.event_id}")
            logger.warning(f"  Type: {event.event_type.value}")
            logger.warning(f"  Threat Level: {event.threat_level.value}")
            logger.warning(f"  Source: {event.source_device} ({event.source_ip})")
            logger.warning(f"  Response Time: {response_time:.1f}ms")
            
        except Exception as e:
            logger.error(f"Security event handling failed: {str(e)}")
    
    async def _execute_response_action(self, action: str, event: SecurityEvent):
        """Execute specific response action"""
        try:
            if action == 'quarantine_device':
                await self._quarantine_device(event.source_device)
            elif action == 'block_ip':
                await self._block_ip_address(event.source_ip)
            elif action == 'alert_admin':
                await self._send_admin_alert(event)
            elif action == 'emergency_alert':
                await self._send_emergency_alert(event)
            elif action == 'block_traffic':
                await self._block_device_traffic(event.source_device)
            elif action == 'investigate_traffic':
                await self._investigate_network_traffic(event.source_device)
            else:
                logger.info(f"Response action executed: {action}")
                
        except Exception as e:
            logger.error(f"Response action '{action}' failed: {str(e)}")
    
    async def _quarantine_device(self, device_id: str):
        """Quarantine a compromised device"""
        try:
            if device_id in self.monitored_devices:
                device = self.monitored_devices[device_id]
                device.status = DeviceStatus.QUARANTINED
                self.quarantined_devices.add(device_id)
                
                logger.warning(f"Device quarantined: {device_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Device quarantine failed: {str(e)}")
            return False
    
    async def _block_ip_address(self, ip_address: str):
        """Block specific IP address"""
        logger.warning(f"IP address blocked: {ip_address}")
        # In production, this would update firewall rules
        
    async def _send_admin_alert(self, event: SecurityEvent):
        """Send alert to administrator"""
        logger.warning(f"Admin alert sent for event: {event.event_id}")
        # In production, this would send email/SMS/Slack notification
    
    async def _send_emergency_alert(self, event: SecurityEvent):
        """Send emergency alert for critical threats"""
        logger.error(f"EMERGENCY ALERT: {event.description}")
        # In production, this would trigger immediate notifications
        
    async def _block_device_traffic(self, device_id: str):
        """Block all traffic from specific device"""
        logger.warning(f"Traffic blocked for device: {device_id}")
        # In production, this would update network ACLs
        
    async def _investigate_network_traffic(self, device_id: str):
        """Start detailed investigation of device traffic"""
        logger.info(f"Network investigation started for device: {device_id}")
        # In production, this would enable detailed packet capture
    
    async def _incident_response_loop(self):
        """Handle ongoing incident response"""
        logger.info("Incident response loop started")
        
        while self.running:
            try:
                # Review active threats
                current_time = datetime.now()
                resolved_threats = []
                
                for threat_id, threat in self.active_threats.items():
                    # Auto-resolve threats older than 1 hour (simplified)
                    if (current_time - threat.timestamp).total_seconds() > 3600:
                        threat.resolved = True
                        resolved_threats.append(threat_id)
                        logger.info(f"Threat auto-resolved: {threat_id}")
                
                # Remove resolved threats
                for threat_id in resolved_threats:
                    del self.active_threats[threat_id]
                
                await asyncio.sleep(600)  # Run every 10 minutes
                
            except Exception as e:
                logger.error(f"Incident response error: {str(e)}")
                await asyncio.sleep(60)
        
        logger.info("Incident response loop stopped")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get comprehensive security monitoring statistics"""
        try:
            current_time = datetime.now()
            uptime = current_time - self.stats['uptime_start']
            
            # Calculate performance metrics
            avg_response_time = (
                statistics.mean(self.stats['response_times'])
                if self.stats['response_times'] else 0
            )
            
            # Device status distribution
            status_distribution = defaultdict(int)
            for device in self.monitored_devices.values():
                status_distribution[device.status.value] += 1
            
            # Threat level distribution
            threat_distribution = dict(self.stats['events_by_threat_level'])
            
            return {
                "monitor_info": {
                    "monitor_id": self.monitor_id,
                    "location": self.location,
                    "network_range": str(self.network_range),
                    "uptime_hours": round(uptime.total_seconds() / 3600, 2),
                    "status": "running" if self.running else "stopped"
                },
                "device_statistics": {
                    "total_devices": len(self.monitored_devices),
                    "devices_by_status": dict(status_distribution),
                    "quarantined_devices": len(self.quarantined_devices),
                    "devices_scanned": self.stats['devices_scanned'],
                    "vulnerabilities_found": self.stats['vulnerabilities_found']
                },
                "security_events": {
                    "total_events": self.stats['total_events'],
                    "active_threats": len(self.active_threats),
                    "events_by_type": dict(self.stats['events_by_type']),
                    "events_by_threat_level": threat_distribution,
                    "threats_blocked": self.stats['threats_blocked'],
                    "false_positives": self.stats['false_positives']
                },
                "performance_metrics": {
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "security_rules_active": len(self.security_rules),
                    "baseline_established_devices": sum(
                        1 for baseline in self.device_baselines.values()
                        if baseline.get('baseline_established', False)
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get security stats: {str(e)}")
            return {"error": str(e)}

# Example usage and testing
async def main():
    """
    Comprehensive Edge Security Monitor testing
    Mumbai local area network security demonstration
    """
    print("🛡️ Edge Security Monitor - Mumbai Network Security")
    print("=" * 55)
    
    # Initialize security monitor
    security_monitor = EdgeSecurityMonitor("mumbai-security-01", "Mumbai Central", "192.168.1.0/24")
    await security_monitor.start_monitoring()
    
    print(f"✅ Security Monitor started: {security_monitor.monitor_id}")
    print(f"🌐 Monitoring network: {security_monitor.network_range}")
    print(f"📍 Location: {security_monitor.location}")
    
    # Register sample Mumbai devices
    print(f"\n📱 Registering Mumbai Devices...")
    
    mumbai_devices = [
        SecurityDevice(
            device_id="mumbai_office_laptop_01",
            device_name="Office Laptop",
            device_type="laptop",
            ip_address="192.168.1.101",
            mac_address="00:11:22:33:44:55",
            location="Mumbai Office",
            status=DeviceStatus.SECURE,
            last_seen=datetime.now(),
            security_score=85.0
        ),
        SecurityDevice(
            device_id="mumbai_iot_sensor_01",
            device_name="Temperature Sensor",
            device_type="iot_sensor",
            ip_address="192.168.1.102",
            mac_address="00:11:22:33:44:56",
            location="Mumbai Factory",
            status=DeviceStatus.SECURE,
            last_seen=datetime.now(),
            security_score=92.0
        ),
        SecurityDevice(
            device_id="mumbai_printer_shared",
            device_name="Network Printer",
            device_type="printer",
            ip_address="192.168.1.103",
            mac_address="00:11:22:33:44:57",
            location="Mumbai Office",
            status=DeviceStatus.VULNERABLE,
            last_seen=datetime.now(),
            security_score=65.0,
            vulnerabilities=["Default admin password", "Outdated firmware"]
        ),
        SecurityDevice(
            device_id="mumbai_security_camera",
            device_name="Security Camera",
            device_type="camera",
            ip_address="192.168.1.104",
            mac_address="00:11:22:33:44:58",
            location="Mumbai Entrance",
            status=DeviceStatus.SECURE,
            last_seen=datetime.now(),
            security_score=88.0
        ),
        SecurityDevice(
            device_id="mumbai_smart_tv",
            device_name="Conference Room TV",
            device_type="smart_tv",
            ip_address="192.168.1.105",
            mac_address="00:11:22:33:44:59",
            location="Mumbai Conference Room",
            status=DeviceStatus.VULNERABLE,
            last_seen=datetime.now(),
            security_score=70.0,
            vulnerabilities=["Weak encryption", "Unnecessary network services"]
        )
    ]
    
    # Register devices
    for device in mumbai_devices:
        success = await security_monitor.register_device(device)
        status_emoji = {"सुरक्षित": "🟢", "असुरक्षित": "🟡", "संक्रमित": "🔴", "क्वारंटीन": "⚫"}
        print(f"{status_emoji[device.status.value]} {device.device_name}: {device.ip_address} "
              f"(Score: {device.security_score:.1f})")
    
    print(f"\n🔍 Running security monitoring for 60 seconds...")
    
    # Let monitoring run
    await asyncio.sleep(60)
    
    # Get security statistics
    stats = security_monitor.get_security_stats()
    
    print(f"\n📊 Security Monitoring Report:")
    print("=" * 40)
    
    # Monitor info
    monitor_info = stats["monitor_info"]
    print(f"Monitor: {monitor_info['monitor_id']}")
    print(f"Network: {monitor_info['network_range']}")
    print(f"Uptime: {monitor_info['uptime_hours']} hours")
    print(f"Status: {monitor_info['status']}")
    
    # Device statistics
    device_stats = stats["device_statistics"]
    print(f"\n🖥️ Device Statistics:")
    print(f"• Total Devices: {device_stats['total_devices']}")
    print(f"• Quarantined: {device_stats['quarantined_devices']}")
    print(f"• Scanned: {device_stats['devices_scanned']}")
    print(f"• Vulnerabilities Found: {device_stats['vulnerabilities_found']}")
    
    print(f"\n• Device Status Distribution:")
    for status, count in device_stats['devices_by_status'].items():
        status_emoji = {"सुरक्षित": "🟢", "असुरक्षित": "🟡", "संक्रमित": "🔴", "क्वारंटीन": "⚫"}
        print(f"  {status_emoji.get(status, '🔵')} {status}: {count}")
    
    # Security events
    security_events = stats["security_events"]
    print(f"\n🚨 Security Events:")
    print(f"• Total Events: {security_events['total_events']}")
    print(f"• Active Threats: {security_events['active_threats']}")
    print(f"• Threats Blocked: {security_events['threats_blocked']}")
    print(f"• False Positives: {security_events['false_positives']}")
    
    if security_events['events_by_type']:
        print(f"\n• Events by Type:")
        for event_type, count in security_events['events_by_type'].items():
            print(f"  - {event_type}: {count}")
    
    if security_events['events_by_threat_level']:
        print(f"\n• Events by Threat Level:")
        threat_emojis = {"निम्न": "🟡", "मध्यम": "🟠", "उच्च": "🔴", "गंभीर": "🚨"}
        for level, count in security_events['events_by_threat_level'].items():
            print(f"  {threat_emojis.get(level, '🔵')} {level}: {count}")
    
    # Performance metrics
    performance = stats["performance_metrics"]
    print(f"\n⚡ Performance Metrics:")
    print(f"• Avg Response Time: {performance['avg_response_time_ms']:.2f}ms")
    print(f"• Active Security Rules: {performance['security_rules_active']}")
    print(f"• Devices with Baseline: {performance['baseline_established_devices']}")
    
    # Display recent security events
    if security_monitor.security_events:
        print(f"\n📋 Recent Security Events:")
        print("-" * 35)
        
        recent_events = list(security_monitor.security_events)[-5:]  # Last 5 events
        for event in recent_events:
            threat_emoji = {"निम्न": "🟡", "मध्यम": "🟠", "उच्च": "🔴", "गंभीर": "🚨"}
            print(f"{threat_emoji[event.threat_level.value]} {event.timestamp.strftime('%H:%M:%S')}")
            print(f"   Type: {event.event_type.value}")
            print(f"   Source: {event.source_device}")
            print(f"   Description: {event.description}")
            print()
    
    # Cost analysis
    print(f"\n💰 Cost Analysis (Monthly):")
    print("-" * 25)
    
    total_devices = device_stats['total_devices']
    edge_security_cost = total_devices * 5    # ₹5 per device per month
    cloud_security_cost = total_devices * 50  # ₹50 per device per month
    savings = cloud_security_cost - edge_security_cost
    
    print(f"Edge Security Cost: ₹{edge_security_cost:,}/month")
    print(f"Cloud Security Cost: ₹{cloud_security_cost:,}/month")
    print(f"Monthly Savings: ₹{savings:,}")
    print(f"Savings Percentage: {(savings/cloud_security_cost)*100:.1f}%")
    
    # Business benefits
    print(f"\n🎯 Business Benefits:")
    print("• Real-time threat detection and response")
    print("• Local network security without cloud dependency")
    print("• Automated device vulnerability scanning")
    print("• Mumbai-specific security rule optimization")
    print("• Cost-effective security for IoT devices")
    print("• Privacy-compliant local data processing")
    
    # Security recommendations
    print(f"\n💡 Security Recommendations:")
    vulnerable_devices = sum(
        1 for device in security_monitor.monitored_devices.values()
        if device.status == DeviceStatus.VULNERABLE
    )
    
    if vulnerable_devices > 0:
        print(f"• {vulnerable_devices} vulnerable devices need attention")
        print("• Regular security patches and updates required")
        print("• Consider network segmentation for IoT devices")
        
    if device_stats['quarantined_devices'] > 0:
        print(f"• {device_stats['quarantined_devices']} quarantined devices need investigation")
        
    print("• Implement regular security awareness training")
    print("• Consider multi-factor authentication for critical devices")
    
    # Stop monitoring
    print(f"\n🛑 Stopping security monitoring...")
    await security_monitor.stop_monitoring()
    
    print(f"\n✅ Edge Security Monitor demonstration completed!")
    print(f"🛡️ Mumbai network security optimized with local monitoring!")

if __name__ == "__main__":
    asyncio.run(main())
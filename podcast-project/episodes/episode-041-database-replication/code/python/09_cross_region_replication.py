#!/usr/bin/env python3
"""
Episode 41: Database Replication Strategies - Cross-Region Replication
Advanced cross-region replication for global Indian businesses

यह implementation demonstrate करती है कि कैसे Indian businesses अपने data को
multiple regions में replicate करके global scalability achieve कर सकती हैं।
जैसे Indian Railways का network पूरे India में फैला है और different regions के
stations आपस में coordinate करते हैं, वैसे ही database replication भी काम करती है।

Real-world Usage:
- Flipkart: Global expansion के लिए multi-region setup
- HDFC Bank: Dubai, Singapore, UK branches के लिए cross-region replication
- Zomato: International markets में expansion के लिए

Author: Hindi Tech Podcast Team
Episode: 41 - Database Replication Strategies
"""

import asyncio
import json
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging
import uuid
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import ssl
import requests
from collections import defaultdict, deque
import heapq
import traceback

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(region)s] %(message)s',
    handlers=[
        logging.FileHandler('/var/log/replication/cross_region.log'),
        logging.StreamHandler()
    ]
)

class RegionAdapter(logging.LoggerAdapter):
    """Logger adapter to add region context"""
    def process(self, msg, kwargs):
        return f"[{self.extra['region']}] {msg}", kwargs

class ReplicationTopology(Enum):
    """Cross-region replication topologies"""
    HUB_AND_SPOKE = "hub_and_spoke"      # Central hub with regional spokes
    MESH = "mesh"                        # All regions connected to all
    RING = "ring"                        # Circular replication chain
    TREE = "tree"                        # Hierarchical structure
    HYBRID = "hybrid"                    # Combination approach

class ReplicationMode(Enum):
    """Replication modes"""
    ACTIVE_PASSIVE = "active_passive"    # Master-slave across regions
    ACTIVE_ACTIVE = "active_active"      # Multi-master across regions
    DISASTER_RECOVERY = "disaster_recovery"  # DR-focused replication
    ANALYTICS = "analytics"              # Analytics-focused replication

class ConsistencyLevel(Enum):
    """Cross-region consistency levels"""
    STRONG = "strong"                    # Synchronous across all regions
    BOUNDED_STALENESS = "bounded_staleness"  # Time/version bounded
    SESSION = "session"                  # Session consistency
    EVENTUAL = "eventual"                # Eventually consistent
    CAUSAL = "causal"                   # Causal consistency

@dataclass
class Region:
    """Region configuration"""
    id: str
    name: str
    location: str
    timezone: str
    primary_datacenter: str
    backup_datacenters: List[str] = field(default_factory=list)
    network_latency_ms: Dict[str, int] = field(default_factory=dict)
    cost_multiplier: float = 1.0
    compliance_requirements: List[str] = field(default_factory=list)
    peak_hours: List[Tuple[int, int]] = field(default_factory=list)

@dataclass
class ReplicationEvent:
    """Cross-region replication event"""
    event_id: str
    timestamp: datetime
    source_region: str
    target_regions: List[str]
    database_name: str
    table_name: str
    operation_type: str
    data: Dict[str, Any]
    consistency_level: ConsistencyLevel
    priority: int = 5  # 1-10, 1 being highest
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)

class FlipkartGlobalReplication:
    """
    Flipkart के global expansion के लिए cross-region replication
    India, Singapore, UAE, US markets के लिए optimized
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.regions = self._setup_flipkart_regions()
        self.topology = ReplicationTopology.HYBRID
        self.replication_queues = defaultdict(deque)
        self.conflict_resolver = self._setup_conflict_resolver()
        self.network_monitor = self._setup_network_monitor()
        self.compliance_manager = self._setup_compliance_manager()
        
        # Setup region-specific loggers
        self.loggers = {}
        for region_id in self.regions:
            self.loggers[region_id] = RegionAdapter(
                logging.getLogger(f'flipkart_replication'),
                {'region': region_id}
            )
        
        self.logger = self.loggers.get('india', logging.getLogger(__name__))
        self.logger.info("Flipkart Global Replication initialized")
    
    def _setup_flipkart_regions(self) -> Dict[str, Region]:
        """Setup Flipkart's global regions"""
        regions = {
            'india': Region(
                id='india',
                name='India Primary',
                location='Bangalore',
                timezone='Asia/Kolkata',
                primary_datacenter='BLR-DC-01',
                backup_datacenters=['MUM-DC-01', 'DEL-DC-01'],
                network_latency_ms={
                    'singapore': 45,
                    'uae': 120,
                    'us_east': 180
                },
                cost_multiplier=0.8,  # Lower costs in India
                compliance_requirements=['RBI', 'GDPR'],
                peak_hours=[(9, 11), (14, 16), (19, 21)]
            ),
            'singapore': Region(
                id='singapore',
                name='Singapore Hub',
                location='Singapore',
                timezone='Asia/Singapore',
                primary_datacenter='SG-DC-01',
                network_latency_ms={
                    'india': 45,
                    'uae': 180,
                    'us_east': 200
                },
                cost_multiplier=1.5,
                compliance_requirements=['PDPA', 'GDPR'],
                peak_hours=[(10, 12), (15, 17), (20, 22)]
            ),
            'uae': Region(
                id='uae',
                name='UAE Regional',
                location='Dubai',
                timezone='Asia/Dubai',
                primary_datacenter='DXB-DC-01',
                network_latency_ms={
                    'india': 120,
                    'singapore': 180,
                    'us_east': 220
                },
                cost_multiplier=1.8,
                compliance_requirements=['UAE_DPA', 'GDPR'],
                peak_hours=[(11, 13), (16, 18), (21, 23)]
            ),
            'us_east': Region(
                id='us_east',
                name='US East Coast',
                location='Virginia',
                timezone='America/New_York',
                primary_datacenter='IAD-DC-01',
                network_latency_ms={
                    'india': 180,
                    'singapore': 200,
                    'uae': 220
                },
                cost_multiplier=2.0,
                compliance_requirements=['CCPA', 'GDPR'],
                peak_hours=[(12, 14), (17, 19), (22, 24)]
            )
        }
        
        return regions
    
    def _setup_conflict_resolver(self):
        """Setup conflict resolution for multi-region writes"""
        return {
            'last_write_wins': self._resolve_last_write_wins,
            'business_rules': self._resolve_business_rules,
            'vector_clock': self._resolve_vector_clock,
            'application_merge': self._resolve_application_merge
        }
    
    def _setup_network_monitor(self):
        """Setup network latency monitoring between regions"""
        return {
            'ping_interval': 60,  # seconds
            'timeout': 5,  # seconds
            'retry_count': 3,
            'latency_history': defaultdict(deque),
            'quality_thresholds': {
                'excellent': 50,    # < 50ms
                'good': 100,        # 50-100ms
                'acceptable': 200,  # 100-200ms
                'poor': 500         # 200-500ms
            }
        }
    
    def _setup_compliance_manager(self):
        """Setup compliance management for different regions"""
        return {
            'data_residency_rules': {
                'india': ['customer_data', 'financial_data'],
                'singapore': ['regional_inventory', 'logistics_data'],
                'uae': ['local_preferences', 'payment_data'],
                'us_east': ['analytics_data', 'marketing_data']
            },
            'encryption_requirements': {
                'india': 'AES-256',
                'singapore': 'AES-256',
                'uae': 'AES-256',
                'us_east': 'AES-256'
            },
            'audit_retention_days': {
                'india': 2555,      # 7 years (Indian compliance)
                'singapore': 2190,  # 6 years
                'uae': 1825,        # 5 years
                'us_east': 2555     # 7 years
            }
        }
    
    async def start_cross_region_replication(self):
        """Start cross-region replication with hybrid topology"""
        self.logger.info("Starting Flipkart cross-region replication...")
        
        tasks = [
            self._run_network_monitoring(),
            self._process_replication_queues(),
            self._monitor_replication_lag(),
            self._handle_product_catalog_replication(),
            self._handle_inventory_replication(),
            self._handle_customer_data_replication(),
            self._generate_replication_metrics()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_network_monitoring(self):
        """Continuous network latency monitoring"""
        while True:
            try:
                for source_region in self.regions:
                    for target_region, expected_latency in self.regions[source_region].network_latency_ms.items():
                        if target_region in self.regions:
                            actual_latency = await self._measure_latency(source_region, target_region)
                            
                            # Update latency history
                            history = self.network_monitor['latency_history'][f"{source_region}_{target_region}"]
                            history.append({
                                'timestamp': datetime.now(),
                                'latency_ms': actual_latency,
                                'expected_ms': expected_latency
                            })
                            
                            # Keep only last 100 measurements
                            if len(history) > 100:
                                history.popleft()
                            
                            # Alert on high latency
                            if actual_latency > expected_latency * 2:
                                self.loggers[source_region].warning(
                                    f"High latency to {target_region}: {actual_latency}ms"
                                )
                
                await asyncio.sleep(self.network_monitor['ping_interval'])
                
            except Exception as e:
                self.logger.error(f"Network monitoring failed: {e}")
                await asyncio.sleep(30)
    
    async def _measure_latency(self, source_region: str, target_region: str) -> float:
        """Measure network latency between regions"""
        try:
            # Simulate latency measurement (production में actual ping/HTTP calls होंगे)
            base_latency = self.regions[source_region].network_latency_ms.get(target_region, 100)
            
            # Add random variation (±20%)
            variation = random.uniform(-0.2, 0.2)
            actual_latency = base_latency * (1 + variation)
            
            # Add occasional spikes to simulate real network conditions
            if random.random() < 0.05:  # 5% chance of spike
                actual_latency *= random.uniform(2, 5)
            
            return max(1, actual_latency)
            
        except Exception as e:
            self.logger.error(f"Latency measurement failed {source_region}->{target_region}: {e}")
            return 1000  # Return high latency on error
    
    async def _process_replication_queues(self):
        """Process replication events from queues"""
        while True:
            try:
                for region_id in self.regions:
                    queue = self.replication_queues[region_id]
                    processed_count = 0
                    
                    # Process up to 100 events per batch
                    while queue and processed_count < 100:
                        event = queue.popleft()
                        await self._process_replication_event(event)
                        processed_count += 1
                
                await asyncio.sleep(1)  # Process every second
                
            except Exception as e:
                self.logger.error(f"Queue processing failed: {e}")
                await asyncio.sleep(5)
    
    async def _process_replication_event(self, event: ReplicationEvent):
        """Process individual replication event"""
        try:
            source_logger = self.loggers.get(event.source_region, self.logger)
            source_logger.info(f"Processing replication event: {event.event_id}")
            
            # Apply compliance checks
            if not self._check_compliance(event):
                source_logger.error(f"Compliance check failed for event: {event.event_id}")
                return
            
            # Replicate to target regions based on consistency level
            if event.consistency_level == ConsistencyLevel.STRONG:
                await self._replicate_synchronously(event)
            else:
                await self._replicate_asynchronously(event)
            
            # Update replication metrics
            self._update_replication_metrics(event)
            
        except Exception as e:
            self.logger.error(f"Failed to process replication event {event.event_id}: {e}")
            
            # Retry logic
            if event.retry_count < event.max_retries:
                event.retry_count += 1
                event.metadata['last_error'] = str(e)
                event.metadata['retry_timestamp'] = datetime.now()
                
                # Add back to queue with exponential backoff
                delay = 2 ** event.retry_count
                await asyncio.sleep(delay)
                self.replication_queues[event.source_region].append(event)
    
    def _check_compliance(self, event: ReplicationEvent) -> bool:
        """Check data compliance for cross-region replication"""
        source_region = event.source_region
        table_name = event.table_name
        
        # Check data residency requirements
        residency_rules = self.compliance_manager['data_residency_rules']
        
        for target_region in event.target_regions:
            if target_region in residency_rules:
                allowed_tables = residency_rules[target_region]
                if table_name not in allowed_tables and 'all_tables' not in allowed_tables:
                    self.loggers[source_region].warning(
                        f"Data residency violation: {table_name} cannot be replicated to {target_region}"
                    )
                    return False
        
        return True
    
    async def _replicate_synchronously(self, event: ReplicationEvent):
        """Synchronous replication for strong consistency"""
        success_count = 0
        total_targets = len(event.target_regions)
        
        # Replicate to all target regions
        tasks = []
        for target_region in event.target_regions:
            task = self._replicate_to_region(event, target_region)
            tasks.append(task)
        
        # Wait for all replications to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            target_region = event.target_regions[i]
            if isinstance(result, Exception):
                self.loggers[event.source_region].error(
                    f"Sync replication failed to {target_region}: {result}"
                )
            else:
                success_count += 1
        
        # Strong consistency requires all replicas to succeed
        if success_count < total_targets:
            raise Exception(f"Synchronous replication failed: {success_count}/{total_targets} succeeded")
        
        self.loggers[event.source_region].info(
            f"Synchronous replication completed: {event.event_id}"
        )
    
    async def _replicate_asynchronously(self, event: ReplicationEvent):
        """Asynchronous replication for eventual consistency"""
        tasks = []
        
        for target_region in event.target_regions:
            # Create async task for each target region
            task = asyncio.create_task(self._replicate_to_region(event, target_region))
            tasks.append(task)
        
        # Don't wait for completion - fire and forget
        self.loggers[event.source_region].info(
            f"Asynchronous replication started: {event.event_id} -> {event.target_regions}"
        )
    
    async def _replicate_to_region(self, event: ReplicationEvent, target_region: str):
        """Replicate event to specific target region"""
        try:
            source_region = event.source_region
            
            # Calculate expected latency
            expected_latency = self.regions[source_region].network_latency_ms.get(target_region, 100)
            
            # Simulate network delay
            actual_delay = expected_latency / 1000.0  # Convert to seconds
            await asyncio.sleep(actual_delay)
            
            # Apply data transformation for target region
            transformed_data = await self._transform_data_for_region(event.data, target_region)
            
            # Simulate replication operation
            replication_result = await self._execute_replication(
                event, target_region, transformed_data
            )
            
            self.loggers[source_region].info(
                f"Replication successful: {event.event_id} -> {target_region}"
            )
            
            return replication_result
            
        except Exception as e:
            self.loggers[event.source_region].error(
                f"Replication failed: {event.event_id} -> {target_region}: {e}"
            )
            raise
    
    async def _transform_data_for_region(self, data: Dict[str, Any], target_region: str) -> Dict[str, Any]:
        """Transform data based on regional requirements"""
        transformed_data = data.copy()
        
        # Regional price conversion
        if 'price' in transformed_data:
            base_price = transformed_data['price']
            cost_multiplier = self.regions[target_region].cost_multiplier
            transformed_data['regional_price'] = base_price * cost_multiplier
        
        # Currency conversion
        currency_mapping = {
            'india': 'INR',
            'singapore': 'SGD',
            'uae': 'AED',
            'us_east': 'USD'
        }
        transformed_data['currency'] = currency_mapping.get(target_region, 'USD')
        
        # Regional compliance data redaction
        if target_region == 'india' and 'pii_data' in transformed_data:
            # Additional protection for Indian PII
            transformed_data['pii_data'] = self._encrypt_pii_data(transformed_data['pii_data'])
        
        # Regional localization
        if 'description' in transformed_data:
            transformed_data['localized_description'] = await self._localize_content(
                transformed_data['description'], target_region
            )
        
        return transformed_data
    
    def _encrypt_pii_data(self, pii_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt PII data for compliance"""
        encrypted_data = {}
        
        for key, value in pii_data.items():
            if isinstance(value, str):
                # Simple encryption (production में proper encryption library use करें)
                encrypted_value = hashlib.sha256(value.encode()).hexdigest()[:16]
                encrypted_data[key] = f"encrypted_{encrypted_value}"
            else:
                encrypted_data[key] = value
        
        return encrypted_data
    
    async def _localize_content(self, content: str, target_region: str) -> str:
        """Localize content for target region"""
        localization_mapping = {
            'india': {'size': 'Size (Indian Standard)', 'price': 'Price (₹)'},
            'singapore': {'size': 'Size (Asian Fit)', 'price': 'Price (S$)'},
            'uae': {'size': 'Size (Middle East)', 'price': 'Price (AED)'},
            'us_east': {'size': 'Size (US Standard)', 'price': 'Price ($)'}
        }
        
        localized_content = content
        if target_region in localization_mapping:
            for key, replacement in localization_mapping[target_region].items():
                localized_content = localized_content.replace(key, replacement)
        
        return localized_content
    
    async def _execute_replication(self, event: ReplicationEvent, target_region: str, data: Dict[str, Any]):
        """Execute actual replication operation"""
        # Simulate database operation
        operation_time = random.uniform(0.1, 0.5)  # 100-500ms
        await asyncio.sleep(operation_time)
        
        # Simulate occasional failures (5% failure rate)
        if random.random() < 0.05:
            raise Exception(f"Simulated network/database error for {target_region}")
        
        return {
            'success': True,
            'target_region': target_region,
            'timestamp': datetime.now(),
            'operation_time_ms': operation_time * 1000
        }
    
    async def _handle_product_catalog_replication(self):
        """Handle product catalog replication across regions"""
        while True:
            try:
                # Simulate product catalog updates
                await asyncio.sleep(10)  # Every 10 seconds
                
                # Create product catalog update event
                event = ReplicationEvent(
                    event_id=f"product_{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now(),
                    source_region='india',
                    target_regions=['singapore', 'uae', 'us_east'],
                    database_name='flipkart_catalog',
                    table_name='products',
                    operation_type='UPDATE',
                    data={
                        'product_id': f'FKRT{random.randint(1000000000, 9999999999)}',
                        'name': 'Premium Smartphone',
                        'description': 'Latest smartphone with advanced features',
                        'price': random.uniform(10000, 50000),
                        'category': 'Electronics',
                        'availability': True,
                        'pii_data': {'user_preferences': 'electronics, premium brands'}
                    },
                    consistency_level=ConsistencyLevel.EVENTUAL,
                    priority=3
                )
                
                # Add to replication queue
                self.replication_queues['india'].append(event)
                
            except Exception as e:
                self.logger.error(f"Product catalog replication failed: {e}")
    
    async def _handle_inventory_replication(self):
        """Handle inventory replication with regional optimization"""
        while True:
            try:
                # Simulate inventory updates
                await asyncio.sleep(5)  # Every 5 seconds
                
                # Create inventory update event
                event = ReplicationEvent(
                    event_id=f"inventory_{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now(),
                    source_region='india',
                    target_regions=['singapore', 'uae'],  # Regional inventory
                    database_name='flipkart_inventory',
                    table_name='warehouse_inventory',
                    operation_type='UPDATE',
                    data={
                        'product_id': f'FKRT{random.randint(1000000000, 9999999999)}',
                        'warehouse_id': 'WH_BLR_001',
                        'quantity': random.randint(0, 1000),
                        'reserved': random.randint(0, 100),
                        'last_updated': datetime.now().isoformat()
                    },
                    consistency_level=ConsistencyLevel.BOUNDED_STALENESS,
                    priority=2,
                    metadata={'staleness_bound_seconds': 30}
                )
                
                # Add to replication queue
                self.replication_queues['india'].append(event)
                
            except Exception as e:
                self.logger.error(f"Inventory replication failed: {e}")
    
    async def _handle_customer_data_replication(self):
        """Handle customer data replication with compliance"""
        while True:
            try:
                # Simulate customer data updates
                await asyncio.sleep(15)  # Every 15 seconds
                
                # Create customer data update event
                event = ReplicationEvent(
                    event_id=f"customer_{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now(),
                    source_region='india',
                    target_regions=['singapore'],  # Limited replication for PII
                    database_name='flipkart_customers',
                    table_name='customer_profiles',
                    operation_type='UPDATE',
                    data={
                        'customer_id': f'CUST{random.randint(100000000, 999999999)}',
                        'region': 'india',
                        'preferences': {'categories': ['electronics', 'fashion']},
                        'pii_data': {
                            'email_domain': 'gmail.com',
                            'city': 'Bangalore',
                            'age_group': '25-35'
                        }
                    },
                    consistency_level=ConsistencyLevel.STRONG,  # Strong consistency for customer data
                    priority=1
                )
                
                # Add to replication queue
                self.replication_queues['india'].append(event)
                
            except Exception as e:
                self.logger.error(f"Customer data replication failed: {e}")
    
    async def _monitor_replication_lag(self):
        """Monitor replication lag across regions"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                lag_report = {}
                for region_id in self.regions:
                    queue_size = len(self.replication_queues[region_id])
                    
                    # Calculate average processing time (simplified)
                    avg_processing_time = self._calculate_average_processing_time(region_id)
                    estimated_lag = queue_size * avg_processing_time
                    
                    lag_report[region_id] = {
                        'queue_size': queue_size,
                        'estimated_lag_seconds': estimated_lag,
                        'status': 'HEALTHY' if estimated_lag < 60 else 'LAGGING'
                    }
                
                self.logger.info(f"Replication Lag Report: {json.dumps(lag_report, indent=2)}")
                
                # Alert on high lag
                for region_id, stats in lag_report.items():
                    if stats['estimated_lag_seconds'] > 300:  # 5 minutes
                        self.loggers[region_id].error(
                            f"High replication lag detected: {stats['estimated_lag_seconds']}s"
                        )
                
            except Exception as e:
                self.logger.error(f"Lag monitoring failed: {e}")
    
    def _calculate_average_processing_time(self, region_id: str) -> float:
        """Calculate average event processing time"""
        # Simplified calculation based on network latency
        region = self.regions[region_id]
        
        if not region.network_latency_ms:
            return 1.0  # Default 1 second
        
        avg_latency = sum(region.network_latency_ms.values()) / len(region.network_latency_ms)
        return avg_latency / 1000.0 + 0.5  # Convert to seconds + processing overhead
    
    async def _generate_replication_metrics(self):
        """Generate comprehensive replication metrics"""
        metrics = {
            'events_processed': defaultdict(int),
            'events_failed': defaultdict(int),
            'average_latency_ms': defaultdict(float),
            'queue_sizes': defaultdict(int),
            'compliance_violations': defaultdict(int)
        }
        
        while True:
            try:
                await asyncio.sleep(60)  # Generate metrics every minute
                
                # Update queue sizes
                for region_id in self.regions:
                    metrics['queue_sizes'][region_id] = len(self.replication_queues[region_id])
                
                # Calculate network quality metrics
                network_quality = {}
                for region_pair, history in self.network_monitor['latency_history'].items():
                    if history:
                        recent_latencies = [entry['latency_ms'] for entry in list(history)[-10:]]
                        avg_latency = sum(recent_latencies) / len(recent_latencies)
                        network_quality[region_pair] = {
                            'average_latency_ms': avg_latency,
                            'quality': self._classify_network_quality(avg_latency)
                        }
                
                # Generate comprehensive report
                report = {
                    'timestamp': datetime.now().isoformat(),
                    'replication_metrics': dict(metrics),
                    'network_quality': network_quality,
                    'regional_status': {
                        region_id: {
                            'queue_size': metrics['queue_sizes'][region_id],
                            'status': 'ACTIVE'
                        }
                        for region_id in self.regions
                    }
                }
                
                self.logger.info(f"Replication Metrics: {json.dumps(report, indent=2)}")
                
            except Exception as e:
                self.logger.error(f"Metrics generation failed: {e}")
    
    def _classify_network_quality(self, latency_ms: float) -> str:
        """Classify network quality based on latency"""
        thresholds = self.network_monitor['quality_thresholds']
        
        if latency_ms < thresholds['excellent']:
            return 'EXCELLENT'
        elif latency_ms < thresholds['good']:
            return 'GOOD'
        elif latency_ms < thresholds['acceptable']:
            return 'ACCEPTABLE'
        elif latency_ms < thresholds['poor']:
            return 'POOR'
        else:
            return 'CRITICAL'
    
    def _update_replication_metrics(self, event: ReplicationEvent):
        """Update replication metrics after event processing"""
        # This would update internal metrics in production
        pass
    
    # Conflict resolution methods
    def _resolve_last_write_wins(self, local_data, remote_data, metadata):
        """Last Write Wins conflict resolution"""
        local_timestamp = metadata.get('local_timestamp', datetime.min)
        remote_timestamp = metadata.get('remote_timestamp', datetime.min)
        
        return remote_data if remote_timestamp > local_timestamp else local_data
    
    def _resolve_business_rules(self, local_data, remote_data, metadata):
        """Business rules based conflict resolution"""
        # Flipkart specific business rules
        if 'price' in local_data and 'price' in remote_data:
            # Always take lower price for customer benefit
            if remote_data['price'] < local_data['price']:
                return remote_data
        
        return local_data
    
    def _resolve_vector_clock(self, local_data, remote_data, metadata):
        """Vector clock based conflict resolution"""
        # Simplified vector clock implementation
        local_clock = metadata.get('local_vector_clock', {})
        remote_clock = metadata.get('remote_vector_clock', {})
        
        # If remote clock is newer, use remote data
        for region, remote_version in remote_clock.items():
            local_version = local_clock.get(region, 0)
            if remote_version > local_version:
                return remote_data
        
        return local_data
    
    def _resolve_application_merge(self, local_data, remote_data, metadata):
        """Application-level merge resolution"""
        merged_data = local_data.copy()
        
        # Merge inventory quantities (additive)
        if 'quantity' in local_data and 'quantity' in remote_data:
            merged_data['quantity'] = local_data['quantity'] + remote_data['quantity']
        
        # Take latest product information
        if 'last_updated' in remote_data:
            remote_updated = datetime.fromisoformat(remote_data['last_updated'])
            local_updated = datetime.fromisoformat(local_data.get('last_updated', '1970-01-01'))
            
            if remote_updated > local_updated:
                merged_data.update(remote_data)
        
        return merged_data

class HDFCGlobalBankingReplication:
    """
    HDFC Bank के global operations के लिए cross-region replication
    India, Singapore, Dubai, London branches के लिए
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.banking_regions = self._setup_hdfc_regions()
        self.compliance_framework = self._setup_banking_compliance()
        self.disaster_recovery = self._setup_disaster_recovery()
        self.audit_logger = self._setup_audit_logging()
        
        self.logger = logging.getLogger('hdfc_global_replication')
        self.logger.info("HDFC Global Banking Replication initialized")
    
    def _setup_hdfc_regions(self) -> Dict[str, Region]:
        """Setup HDFC's global banking regions"""
        return {
            'india': Region(
                id='india',
                name='HDFC India (Mumbai HQ)',
                location='Mumbai',
                timezone='Asia/Kolkata',
                primary_datacenter='BKC-DC-01',
                backup_datacenters=['BLR-DC-01', 'DEL-DC-01'],
                network_latency_ms={
                    'singapore': 50,
                    'dubai': 90,
                    'london': 130
                },
                cost_multiplier=1.0,
                compliance_requirements=['RBI', 'SEBI', 'FIU-IND'],
                peak_hours=[(9, 11), (14, 16)]
            ),
            'singapore': Region(
                id='singapore',
                name='HDFC Singapore Branch',
                location='Singapore',
                timezone='Asia/Singapore',
                primary_datacenter='SG-HDFC-DC-01',
                network_latency_ms={
                    'india': 50,
                    'dubai': 140,
                    'london': 180
                },
                cost_multiplier=1.8,
                compliance_requirements=['MAS', 'PDPA'],
                peak_hours=[(10, 12), (15, 17)]
            ),
            'dubai': Region(
                id='dubai',
                name='HDFC Dubai Branch',
                location='Dubai',
                timezone='Asia/Dubai',
                primary_datacenter='DXB-HDFC-DC-01',
                network_latency_ms={
                    'india': 90,
                    'singapore': 140,
                    'london': 100
                },
                cost_multiplier=2.0,
                compliance_requirements=['CBUAE', 'UAE-AML'],
                peak_hours=[(11, 13), (16, 18)]
            ),
            'london': Region(
                id='london',
                name='HDFC London Branch',
                location='London',
                timezone='Europe/London',
                primary_datacenter='LON-HDFC-DC-01',
                network_latency_ms={
                    'india': 130,
                    'singapore': 180,
                    'dubai': 100
                },
                cost_multiplier=2.5,
                compliance_requirements=['FCA', 'PRA', 'GDPR'],
                peak_hours=[(13, 15), (18, 20)]
            )
        }
    
    def _setup_banking_compliance(self):
        """Setup banking compliance framework"""
        return {
            'transaction_limits': {
                'india': {'max_amount': 1000000, 'currency': 'INR'},
                'singapore': {'max_amount': 50000, 'currency': 'SGD'},
                'dubai': {'max_amount': 200000, 'currency': 'AED'},
                'london': {'max_amount': 100000, 'currency': 'GBP'}
            },
            'data_classification': {
                'highly_confidential': ['account_balance', 'transaction_history'],
                'confidential': ['customer_profile', 'loan_details'],
                'internal': ['branch_performance', 'operational_metrics'],
                'public': ['interest_rates', 'branch_locations']
            },
            'encryption_standards': {
                'in_transit': 'TLS 1.3',
                'at_rest': 'AES-256-GCM',
                'key_management': 'HSM-backed'
            }
        }
    
    def _setup_disaster_recovery(self):
        """Setup disaster recovery configuration"""
        return {
            'rto_requirements': {  # Recovery Time Objective
                'critical_systems': 15,    # 15 minutes
                'important_systems': 60,   # 1 hour
                'standard_systems': 240    # 4 hours
            },
            'rpo_requirements': {  # Recovery Point Objective
                'critical_systems': 0,     # Zero data loss
                'important_systems': 5,    # 5 minutes max data loss
                'standard_systems': 60     # 1 hour max data loss
            },
            'failover_priorities': [
                'account_transactions',
                'customer_authentication',
                'regulatory_reporting',
                'internal_operations'
            ]
        }
    
    def _setup_audit_logging(self):
        """Setup comprehensive audit logging"""
        audit_logger = logging.getLogger('hdfc_audit')
        audit_handler = logging.FileHandler('/var/log/hdfc/global_audit.log')
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(logging.INFO)
        
        return audit_logger
    
    async def start_banking_replication(self):
        """Start HDFC global banking replication"""
        self.logger.info("Starting HDFC Global Banking Replication...")
        
        tasks = [
            self._replicate_account_transactions(),
            self._replicate_customer_data(),
            self._replicate_regulatory_reports(),
            self._monitor_compliance_violations(),
            self._handle_disaster_recovery_scenarios()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _replicate_account_transactions(self):
        """Replicate account transactions across regions"""
        while True:
            try:
                await asyncio.sleep(2)  # Every 2 seconds for critical transactions
                
                # Simulate transaction from different regions
                source_region = random.choice(list(self.banking_regions.keys()))
                
                transaction_event = ReplicationEvent(
                    event_id=f"bank_txn_{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now(),
                    source_region=source_region,
                    target_regions=[r for r in self.banking_regions.keys() if r != source_region],
                    database_name='hdfc_core_banking',
                    table_name='account_transactions',
                    operation_type='INSERT',
                    data={
                        'transaction_id': f'TXN{random.randint(10000000000, 99999999999)}',
                        'account_number': f'HDFC{random.randint(100000000000, 999999999999)}',
                        'amount': random.uniform(1000, 100000),
                        'currency': self._get_region_currency(source_region),
                        'transaction_type': random.choice(['DEBIT', 'CREDIT', 'TRANSFER']),
                        'timestamp': datetime.now().isoformat(),
                        'branch_code': f'{source_region.upper()}_001'
                    },
                    consistency_level=ConsistencyLevel.STRONG,  # Banking requires strong consistency
                    priority=1,  # Highest priority
                    metadata={
                        'compliance_level': 'highly_confidential',
                        'audit_required': True,
                        'regulatory_reporting': True
                    }
                )
                
                await self._process_banking_transaction(transaction_event)
                
            except Exception as e:
                self.logger.error(f"Transaction replication failed: {e}")
    
    def _get_region_currency(self, region: str) -> str:
        """Get currency for region"""
        currency_mapping = {
            'india': 'INR',
            'singapore': 'SGD',
            'dubai': 'AED',
            'london': 'GBP'
        }
        return currency_mapping.get(region, 'USD')
    
    async def _process_banking_transaction(self, event: ReplicationEvent):
        """Process banking transaction with compliance checks"""
        try:
            # Banking compliance validation
            if not self._validate_banking_compliance(event):
                self.logger.error(f"Banking compliance failed for {event.event_id}")
                return
            
            # Audit logging
            self.audit_logger.info(
                f"TRANSACTION_REPLICATION: {event.event_id} | "
                f"SOURCE: {event.source_region} | "
                f"TARGETS: {event.target_regions} | "
                f"AMOUNT: {event.data.get('amount')} {event.data.get('currency')}"
            )
            
            # Synchronous replication for banking (strong consistency required)
            await self._replicate_banking_transaction_sync(event)
            
            self.logger.info(f"Banking transaction replicated successfully: {event.event_id}")
            
        except Exception as e:
            self.logger.error(f"Banking transaction processing failed: {e}")
            
            # Alert banking operations team
            await self._alert_banking_operations(event, str(e))
    
    def _validate_banking_compliance(self, event: ReplicationEvent) -> bool:
        """Validate banking transaction compliance"""
        amount = event.data.get('amount', 0)
        currency = event.data.get('currency', 'USD')
        source_region = event.source_region
        
        # Check transaction limits
        limits = self.compliance_framework['transaction_limits'].get(source_region, {})
        max_amount = limits.get('max_amount', 0)
        
        if amount > max_amount:
            self.logger.warning(
                f"Transaction amount {amount} {currency} exceeds limit for {source_region}"
            )
            return False
        
        # Check data classification
        if 'account_balance' in event.data:
            classification = self.compliance_framework['data_classification']
            if 'account_balance' in classification['highly_confidential']:
                event.metadata['encryption_required'] = True
        
        return True
    
    async def _replicate_banking_transaction_sync(self, event: ReplicationEvent):
        """Synchronous replication for banking transactions"""
        successful_replications = 0
        total_targets = len(event.target_regions)
        
        for target_region in event.target_regions:
            try:
                # Apply regional transformations
                regional_data = await self._transform_banking_data(event.data, target_region)
                
                # Simulate banking database replication
                await self._execute_banking_replication(event, target_region, regional_data)
                
                successful_replications += 1
                
            except Exception as e:
                self.logger.error(f"Banking replication failed to {target_region}: {e}")
        
        # Banking requires all replications to succeed
        if successful_replications < total_targets:
            raise Exception(f"Banking transaction replication failed: {successful_replications}/{total_targets}")
    
    async def _transform_banking_data(self, data: Dict[str, Any], target_region: str) -> Dict[str, Any]:
        """Transform banking data for target region"""
        transformed_data = data.copy()
        
        # Currency conversion (simplified)
        if 'amount' in data and 'currency' in data:
            source_currency = data['currency']
            target_currency = self._get_region_currency(target_region)
            
            if source_currency != target_currency:
                # Simplified currency conversion (production में real FX rates होंगे)
                conversion_rate = self._get_exchange_rate(source_currency, target_currency)
                transformed_data['amount'] = data['amount'] * conversion_rate
                transformed_data['currency'] = target_currency
                transformed_data['original_amount'] = data['amount']
                transformed_data['original_currency'] = source_currency
                transformed_data['exchange_rate'] = conversion_rate
        
        # Regional compliance adjustments
        if target_region in self.compliance_framework['transaction_limits']:
            regional_limits = self.compliance_framework['transaction_limits'][target_region]
            transformed_data['regional_limit'] = regional_limits['max_amount']
        
        return transformed_data
    
    def _get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate between currencies (simplified)"""
        # Simplified exchange rates (production में real FX API use करें)
        rates = {
            ('INR', 'SGD'): 0.016,
            ('INR', 'AED'): 0.044,
            ('INR', 'GBP'): 0.0095,
            ('SGD', 'INR'): 62.5,
            ('AED', 'INR'): 22.7,
            ('GBP', 'INR'): 105.3
        }
        
        return rates.get((from_currency, to_currency), 1.0)
    
    async def _execute_banking_replication(self, event: ReplicationEvent, target_region: str, data: Dict[str, Any]):
        """Execute banking database replication"""
        # Simulate banking database operation with higher reliability
        operation_time = random.uniform(0.5, 1.0)  # 500ms to 1s for banking operations
        await asyncio.sleep(operation_time)
        
        # Banking systems have very low failure rates (0.1%)
        if random.random() < 0.001:
            raise Exception(f"Banking system temporary unavailability in {target_region}")
        
        # Log successful replication
        self.audit_logger.info(
            f"REPLICATION_SUCCESS: {event.event_id} -> {target_region} | "
            f"OPERATION_TIME: {operation_time*1000:.2f}ms"
        )
        
        return {'success': True, 'target_region': target_region, 'operation_time_ms': operation_time * 1000}
    
    async def _alert_banking_operations(self, event: ReplicationEvent, error_message: str):
        """Alert banking operations team about replication failures"""
        alert_data = {
            'alert_type': 'BANKING_REPLICATION_FAILURE',
            'severity': 'CRITICAL',
            'event_id': event.event_id,
            'source_region': event.source_region,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat(),
            'notification_channels': ['email', 'sms', 'pager']
        }
        
        self.audit_logger.error(f"CRITICAL_ALERT: {json.dumps(alert_data)}")
        
        # In production, यह actual alerting system को integrate करेगा
        self.logger.critical(f"Banking Operations Alert: {alert_data}")
    
    async def _replicate_customer_data(self):
        """Replicate customer data with privacy compliance"""
        while True:
            try:
                await asyncio.sleep(30)  # Every 30 seconds for customer data
                
                # Customer data replication with privacy considerations
                customer_event = ReplicationEvent(
                    event_id=f"customer_{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now(),
                    source_region='india',
                    target_regions=['singapore', 'dubai'],  # Limited replication for privacy
                    database_name='hdfc_customers',
                    table_name='customer_profiles',
                    operation_type='UPDATE',
                    data={
                        'customer_id': f'CUST{random.randint(1000000000, 9999999999)}',
                        'account_type': random.choice(['SAVINGS', 'CURRENT', 'FIXED_DEPOSIT']),
                        'region': 'india',
                        'risk_profile': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                        'kyc_status': 'VERIFIED',
                        'last_activity': datetime.now().isoformat()
                    },
                    consistency_level=ConsistencyLevel.BOUNDED_STALENESS,
                    priority=2,
                    metadata={
                        'compliance_level': 'confidential',
                        'privacy_requirements': ['GDPR', 'PDPA'],
                        'staleness_bound_minutes': 10
                    }
                )
                
                await self._process_customer_data_replication(customer_event)
                
            except Exception as e:
                self.logger.error(f"Customer data replication failed: {e}")
    
    async def _process_customer_data_replication(self, event: ReplicationEvent):
        """Process customer data replication with privacy compliance"""
        # Apply privacy compliance checks
        if not self._check_privacy_compliance(event):
            self.logger.warning(f"Privacy compliance check failed for {event.event_id}")
            return
        
        # Process with bounded staleness
        await self._replicate_with_bounded_staleness(event)
    
    def _check_privacy_compliance(self, event: ReplicationEvent) -> bool:
        """Check privacy compliance for customer data"""
        privacy_requirements = event.metadata.get('privacy_requirements', [])
        
        # GDPR compliance check
        if 'GDPR' in privacy_requirements:
            if any(region in ['london'] for region in event.target_regions):
                # Additional GDPR protections required
                event.metadata['gdpr_protection'] = True
        
        # PDPA compliance check
        if 'PDPA' in privacy_requirements:
            if any(region in ['singapore'] for region in event.target_regions):
                # Additional PDPA protections required
                event.metadata['pdpa_protection'] = True
        
        return True
    
    async def _replicate_with_bounded_staleness(self, event: ReplicationEvent):
        """Replicate with bounded staleness guarantee"""
        staleness_bound = event.metadata.get('staleness_bound_minutes', 10)
        
        # Check if replication can meet staleness bound
        for target_region in event.target_regions:
            expected_latency_ms = self.banking_regions[event.source_region].network_latency_ms.get(target_region, 100)
            expected_latency_minutes = expected_latency_ms / 1000 / 60
            
            if expected_latency_minutes > staleness_bound:
                self.logger.warning(
                    f"Cannot meet staleness bound for {target_region}: "
                    f"expected {expected_latency_minutes:.2f}min > bound {staleness_bound}min"
                )
                continue
            
            # Execute replication within staleness bound
            await self._execute_banking_replication(event, target_region, event.data)
    
    async def _replicate_regulatory_reports(self):
        """Replicate regulatory reports across regions"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes for regulatory reports
                
                regulatory_event = ReplicationEvent(
                    event_id=f"regulatory_{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now(),
                    source_region='india',
                    target_regions=['singapore', 'dubai', 'london'],
                    database_name='hdfc_compliance',
                    table_name='regulatory_reports',
                    operation_type='INSERT',
                    data={
                        'report_id': f'RPT{random.randint(100000, 999999)}',
                        'report_type': random.choice(['AML', 'CTR', 'STR', 'KYC']),
                        'period': datetime.now().strftime('%Y-%m'),
                        'status': 'GENERATED',
                        'file_size_mb': random.uniform(1, 50),
                        'checksum': hashlib.md5(f"report_{datetime.now()}".encode()).hexdigest()
                    },
                    consistency_level=ConsistencyLevel.STRONG,
                    priority=1,
                    metadata={
                        'compliance_level': 'highly_confidential',
                        'regulatory_deadline': (datetime.now() + timedelta(days=1)).isoformat()
                    }
                )
                
                self.audit_logger.info(f"REGULATORY_REPORT_REPLICATION: {regulatory_event.event_id}")
                await self._replicate_banking_transaction_sync(regulatory_event)
                
            except Exception as e:
                self.logger.error(f"Regulatory report replication failed: {e}")
    
    async def _monitor_compliance_violations(self):
        """Monitor for compliance violations"""
        while True:
            try:
                await asyncio.sleep(120)  # Check every 2 minutes
                
                # Simulate compliance monitoring
                violation_detected = random.random() < 0.05  # 5% chance
                
                if violation_detected:
                    violation_alert = {
                        'violation_id': f'VIO_{uuid.uuid4().hex[:8]}',
                        'type': random.choice(['DATA_RESIDENCY', 'TRANSACTION_LIMIT', 'ENCRYPTION']),
                        'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                        'region': random.choice(list(self.banking_regions.keys())),
                        'timestamp': datetime.now().isoformat(),
                        'description': 'Automated compliance violation detected'
                    }
                    
                    self.audit_logger.error(f"COMPLIANCE_VIOLATION: {json.dumps(violation_alert)}")
                    self.logger.error(f"Compliance violation detected: {violation_alert}")
                
            except Exception as e:
                self.logger.error(f"Compliance monitoring failed: {e}")
    
    async def _handle_disaster_recovery_scenarios(self):
        """Handle disaster recovery scenarios"""
        while True:
            try:
                await asyncio.sleep(600)  # Check every 10 minutes
                
                # Simulate disaster recovery scenario
                dr_scenario = random.random() < 0.02  # 2% chance
                
                if dr_scenario:
                    affected_region = random.choice(list(self.banking_regions.keys()))
                    
                    dr_event = {
                        'event_id': f'DR_{uuid.uuid4().hex[:8]}',
                        'type': 'REGION_FAILURE_SIMULATION',
                        'affected_region': affected_region,
                        'timestamp': datetime.now().isoformat(),
                        'rto_requirement': self.disaster_recovery['rto_requirements']['critical_systems'],
                        'rpo_requirement': self.disaster_recovery['rpo_requirements']['critical_systems']
                    }
                    
                    self.audit_logger.critical(f"DISASTER_RECOVERY_EVENT: {json.dumps(dr_event)}")
                    self.logger.critical(f"DR scenario activated: {dr_event}")
                    
                    # Simulate DR procedures
                    await self._execute_disaster_recovery(affected_region)
                
            except Exception as e:
                self.logger.error(f"Disaster recovery monitoring failed: {e}")
    
    async def _execute_disaster_recovery(self, affected_region: str):
        """Execute disaster recovery procedures"""
        self.logger.critical(f"Executing disaster recovery for region: {affected_region}")
        
        # Simulate DR steps
        dr_steps = [
            "Detecting region failure",
            "Initiating failover procedures",
            "Redirecting traffic to backup region",
            "Validating data consistency",
            "Notifying stakeholders",
            "Updating DNS records",
            "Completing failover"
        ]
        
        for step in dr_steps:
            await asyncio.sleep(2)  # Simulate step execution time
            self.logger.info(f"DR Step: {step}")
        
        self.audit_logger.info(f"DISASTER_RECOVERY_COMPLETED: {affected_region}")
        self.logger.info(f"Disaster recovery completed for {affected_region}")

async def main():
    """
    Main function demonstrating cross-region replication
    """
    print("🌍 Cross-Region Database Replication")
    print("Episode 41: Global Indian Business Scaling")
    print("=" * 50)
    
    # Configuration
    flipkart_config = {
        'replication_mode': 'hybrid',
        'consistency_default': 'eventual',
        'monitoring_enabled': True
    }
    
    hdfc_config = {
        'replication_mode': 'active_passive',
        'consistency_default': 'strong',
        'compliance_strict': True
    }
    
    print("Starting cross-region replication systems...")
    
    try:
        # Initialize systems
        flipkart_replication = FlipkartGlobalReplication(flipkart_config)
        hdfc_replication = HDFCGlobalBankingReplication(hdfc_config)
        
        # Start replication systems
        tasks = [
            flipkart_replication.start_cross_region_replication(),
            hdfc_replication.start_banking_replication()
        ]
        
        # Run for demo duration
        demo_task = asyncio.create_task(asyncio.gather(*tasks, return_exceptions=True))
        await asyncio.sleep(120)  # Run for 2 minutes
        
        demo_task.cancel()
        
        print("\n🏆 Cross-Region Replication Demo Summary:")
        print(f"✅ Flipkart Global: E-commerce scaling across 4 regions")
        print(f"✅ HDFC Banking: Financial services in 4 countries")
        print(f"✅ Compliance: Regional data protection laws")
        print(f"✅ Disaster Recovery: Automated failover procedures")
        print(f"✅ Performance: Optimized for regional latencies")
        
    except KeyboardInterrupt:
        print("\nCross-region replication stopped by user")
    except Exception as e:
        logging.error(f"Main execution error: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

"""
Key Learning Points from Cross-Region Replication:

1. **Global Scaling Strategies**:
   - Hybrid topology for e-commerce (performance + reliability)
   - Active-passive for banking (consistency + compliance)
   - Regional data placement optimization

2. **Indian Business Context**:
   - Flipkart: Global expansion with regional optimization
   - HDFC Bank: International banking with compliance
   - Cost optimization based on regional infrastructure

3. **Compliance & Governance**:
   - Data residency requirements per region
   - Regional privacy laws (GDPR, PDPA, etc.)
   - Banking regulations across countries

4. **Technical Excellence**:
   - Network latency monitoring और optimization
   - Disaster recovery automation
   - Conflict resolution strategies
   - Performance metrics और alerting

This implementation shows how Indian companies can scale globally
while maintaining compliance and performance standards.
"""
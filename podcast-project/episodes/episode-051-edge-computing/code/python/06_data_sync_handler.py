#!/usr/bin/env python3
"""
Data Sync Handler - एज और क्लाउड के बीच डेटा सिंक्रोनाइज़ेशन
Mumbai local train और long-distance train के बीच coordination की तरह

Real-world inspired by AWS IoT Device Sync, Google Cloud IoT Core
Use cases: Offline-first applications, eventual consistency, conflict resolution
Cost: Local sync ₹0.01 vs Cloud sync ₹1.0 per GB transferred
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
import sqlite3
import threading
from collections import defaultdict, deque
import aiofiles
import aiohttp
import uuid
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncDirection(Enum):
    """Data synchronization directions"""
    EDGE_TO_CLOUD = "एज से क्लाउड"      # Upload from edge to cloud
    CLOUD_TO_EDGE = "क्लाउड से एज"      # Download from cloud to edge
    BIDIRECTIONAL = "द्विदिशीय"        # Both directions

class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    LAST_WRITE_WINS = "अंतिम लेखन जीतता है"     # Latest timestamp wins
    CLOUD_WINS = "क्लाउड जीतता है"            # Cloud version always wins
    EDGE_WINS = "एज जीतता है"               # Edge version always wins
    MERGE = "मर्ज करें"                       # Attempt to merge changes
    MANUAL = "मैन्युअल"                      # Require manual resolution

class SyncStatus(Enum):
    """Synchronization status"""
    PENDING = "लंबित"          # Waiting to sync
    IN_PROGRESS = "प्रगति में"   # Currently syncing
    COMPLETED = "पूर्ण"         # Successfully synced
    FAILED = "असफल"           # Sync failed
    CONFLICT = "संघर्ष"        # Conflict detected

@dataclass
class DataRecord:
    """Individual data record with sync metadata"""
    record_id: str
    data: Dict[str, Any]
    timestamp: datetime
    version: int
    checksum: str
    source: str  # edge or cloud
    last_sync: Optional[datetime] = None
    sync_status: SyncStatus = SyncStatus.PENDING
    conflict_resolution: Optional[ConflictResolution] = None
    
    def __post_init__(self):
        # Calculate checksum if not provided
        if not self.checksum:
            data_str = json.dumps(self.data, sort_keys=True)
            self.checksum = hashlib.md5(data_str.encode()).hexdigest()

@dataclass
class SyncRule:
    """Synchronization rule configuration"""
    rule_id: str
    table_name: str
    sync_direction: SyncDirection
    conflict_resolution: ConflictResolution
    sync_interval_seconds: int
    batch_size: int
    filters: Optional[Dict[str, Any]] = None
    priority: int = 1  # 1=low, 2=medium, 3=high
    enabled: bool = True
    
    def matches_record(self, record: DataRecord) -> bool:
        """Check if record matches this sync rule"""
        if not self.filters:
            return True
        
        # Simple filter matching (can be extended)
        for key, expected_value in self.filters.items():
            if key in record.data:
                if record.data[key] != expected_value:
                    return False
        
        return True

class DataSyncHandler:
    """
    Data Synchronization Handler - Mumbai Railway Time Table की तरह
    Edge और cloud के बीच data को coordinate करना
    """
    
    def __init__(self, device_id: str, location: str = "Mumbai", 
                 edge_db_path: str = "edge_data.db"):
        """
        Initialize Data Sync Handler
        Args:
            device_id: Unique device identifier
            location: Geographic location
            edge_db_path: Path to local SQLite database
        """
        self.device_id = device_id
        self.location = location
        self.edge_db_path = edge_db_path
        
        # Database connections
        self.edge_db = None
        self.cloud_endpoint = "https://api.mumbai-cloud.com/sync"  # Mock endpoint
        
        # Sync management
        self.sync_rules: Dict[str, SyncRule] = {}
        self.active_syncs: Dict[str, asyncio.Task] = {}
        self.sync_queue = deque()
        self.conflict_queue = deque()
        
        # Performance tracking
        self.stats = {
            'total_syncs_attempted': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'conflicts_detected': 0,
            'conflicts_resolved': 0,
            'bytes_uploaded': 0,
            'bytes_downloaded': 0,
            'last_sync_time': None,
            'sync_durations': deque(maxlen=100),
            'active_connections': 0,
            'bandwidth_usage': deque(maxlen=1000)
        }
        
        # Threading
        self.running = False
        self.sync_executor = ThreadPoolExecutor(max_workers=5)
        self.background_tasks = []
        
        # Mumbai-specific sync rules
        self._initialize_mumbai_sync_rules()
        
        logger.info(f"Data Sync Handler initialized: {device_id} @ {location}")
    
    async def start(self):
        """Start the data sync handler"""
        if self.running:
            logger.warning("Sync handler already running")
            return
        
        self.running = True
        
        # Initialize edge database
        await self._init_edge_database()
        
        # Start background sync tasks
        self.background_tasks = [
            asyncio.create_task(self._sync_scheduler_loop()),
            asyncio.create_task(self._conflict_resolver_loop()),
            asyncio.create_task(self._performance_monitor_loop())
        ]
        
        logger.info("Data Sync Handler started")
    
    async def stop(self):
        """Stop the data sync handler"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for active syncs to complete (with timeout)
        if self.active_syncs:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.active_syncs.values(), return_exceptions=True),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                logger.warning("Some sync operations timed out during shutdown")
        
        # Close database connection
        if self.edge_db:
            self.edge_db.close()
        
        logger.info("Data Sync Handler stopped")
    
    def _initialize_mumbai_sync_rules(self):
        """Initialize Mumbai-specific synchronization rules"""
        
        # High-priority: Payment transactions (immediate sync)
        payment_rule = SyncRule(
            rule_id="mumbai_payments_sync",
            table_name="payment_transactions",
            sync_direction=SyncDirection.EDGE_TO_CLOUD,
            conflict_resolution=ConflictResolution.CLOUD_WINS,
            sync_interval_seconds=5,  # Every 5 seconds
            batch_size=50,
            priority=3,  # High priority
            filters={"location": "Mumbai", "status": "completed"}
        )
        
        # Medium-priority: Traffic data (periodic sync)
        traffic_rule = SyncRule(
            rule_id="mumbai_traffic_sync", 
            table_name="traffic_data",
            sync_direction=SyncDirection.BIDIRECTIONAL,
            conflict_resolution=ConflictResolution.LAST_WRITE_WINS,
            sync_interval_seconds=60,  # Every minute
            batch_size=100,
            priority=2,
            filters={"city": "Mumbai"}
        )
        
        # Low-priority: Analytics data (batch sync)
        analytics_rule = SyncRule(
            rule_id="mumbai_analytics_sync",
            table_name="user_analytics", 
            sync_direction=SyncDirection.EDGE_TO_CLOUD,
            conflict_resolution=ConflictResolution.MERGE,
            sync_interval_seconds=300,  # Every 5 minutes
            batch_size=500,
            priority=1,
            filters={"region": "Mumbai"}
        )
        
        # Configuration sync (cloud to edge)
        config_rule = SyncRule(
            rule_id="mumbai_config_sync",
            table_name="app_configurations",
            sync_direction=SyncDirection.CLOUD_TO_EDGE, 
            conflict_resolution=ConflictResolution.CLOUD_WINS,
            sync_interval_seconds=3600,  # Every hour
            batch_size=10,
            priority=2
        )
        
        # User profile sync (bidirectional)
        profile_rule = SyncRule(
            rule_id="mumbai_profile_sync",
            table_name="user_profiles",
            sync_direction=SyncDirection.BIDIRECTIONAL,
            conflict_resolution=ConflictResolution.MANUAL,  # Requires user input
            sync_interval_seconds=1800,  # Every 30 minutes
            batch_size=25,
            priority=2,
            filters={"active": True}
        )
        
        # Register all rules
        rules = [payment_rule, traffic_rule, analytics_rule, config_rule, profile_rule]
        for rule in rules:
            self.sync_rules[rule.rule_id] = rule
        
        logger.info(f"Initialized {len(rules)} Mumbai sync rules")
    
    async def _init_edge_database(self):
        """Initialize local SQLite database for edge data storage"""
        try:
            self.edge_db = sqlite3.connect(
                self.edge_db_path, 
                check_same_thread=False,
                timeout=30.0
            )
            self.edge_db.execute("PRAGMA journal_mode=WAL")
            self.edge_db.execute("PRAGMA synchronous=NORMAL")
            
            # Create sync metadata table
            self.edge_db.execute("""
                CREATE TABLE IF NOT EXISTS sync_metadata (
                    record_id TEXT PRIMARY KEY,
                    table_name TEXT,
                    data_json TEXT,
                    timestamp TEXT,
                    version INTEGER,
                    checksum TEXT,
                    source TEXT,
                    last_sync TEXT,
                    sync_status TEXT,
                    conflict_data TEXT
                )
            """)
            
            # Create sync rules table
            self.edge_db.execute("""
                CREATE TABLE IF NOT EXISTS sync_rules (
                    rule_id TEXT PRIMARY KEY,
                    rule_config TEXT,
                    last_executed TEXT,
                    execution_count INTEGER DEFAULT 0
                )
            """)
            
            # Create conflict log table
            self.edge_db.execute("""
                CREATE TABLE IF NOT EXISTS conflict_log (
                    conflict_id TEXT PRIMARY KEY,
                    record_id TEXT,
                    timestamp TEXT,
                    edge_version TEXT,
                    cloud_version TEXT,
                    resolution_strategy TEXT,
                    resolved_at TEXT,
                    resolved_by TEXT
                )
            """)
            
            self.edge_db.commit()
            logger.info("Edge database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize edge database: {str(e)}")
            raise
    
    async def add_record(self, table_name: str, record_id: str, data: Dict[str, Any],
                        source: str = "edge") -> bool:
        """
        Add new record to edge database
        Mumbai local train ticket booking की तरह - local record creation
        """
        try:
            record = DataRecord(
                record_id=record_id,
                data=data,
                timestamp=datetime.now(),
                version=1,
                checksum="",  # Will be calculated in __post_init__
                source=source
            )
            
            # Store in edge database
            cursor = self.edge_db.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sync_metadata 
                (record_id, table_name, data_json, timestamp, version, checksum, source, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.record_id,
                table_name,
                json.dumps(record.data),
                record.timestamp.isoformat(),
                record.version,
                record.checksum,
                record.source,
                record.sync_status.value
            ))
            
            self.edge_db.commit()
            
            # Check if record matches any sync rules for immediate sync
            await self._check_immediate_sync(table_name, record)
            
            logger.debug(f"Record added: {record_id} to {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add record {record_id}: {str(e)}")
            return False
    
    async def _check_immediate_sync(self, table_name: str, record: DataRecord):
        """Check if record needs immediate synchronization"""
        for rule in self.sync_rules.values():
            if (rule.table_name == table_name and 
                rule.priority >= 3 and  # High priority only
                rule.matches_record(record)):
                
                # Add to immediate sync queue
                sync_task_id = f"immediate_{rule.rule_id}_{record.record_id}"
                if sync_task_id not in self.active_syncs:
                    task = asyncio.create_task(self._execute_sync_rule(rule, [record]))
                    self.active_syncs[sync_task_id] = task
                    
                    logger.info(f"Immediate sync triggered for {record.record_id}")
                break
    
    async def _sync_scheduler_loop(self):
        """
        Main sync scheduling loop
        Mumbai train schedule की तरह - periodic sync operations
        """
        logger.info("Sync scheduler started")
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check each sync rule
                for rule in self.sync_rules.values():
                    if not rule.enabled:
                        continue
                    
                    # Check if it's time to execute this rule
                    last_execution = await self._get_last_execution_time(rule.rule_id)
                    
                    if (last_execution is None or 
                        (current_time - last_execution).total_seconds() >= rule.sync_interval_seconds):
                        
                        # Execute sync rule
                        task_id = f"scheduled_{rule.rule_id}_{int(time.time())}"
                        task = asyncio.create_task(self._execute_sync_rule_batch(rule))
                        self.active_syncs[task_id] = task
                        
                        # Update last execution time
                        await self._update_last_execution_time(rule.rule_id, current_time)
                        
                        logger.debug(f"Scheduled sync for rule: {rule.rule_id}")
                
                # Clean up completed tasks
                completed_tasks = [
                    task_id for task_id, task in self.active_syncs.items() 
                    if task.done()
                ]
                for task_id in completed_tasks:
                    del self.active_syncs[task_id]
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Sync scheduler error: {str(e)}")
                await asyncio.sleep(5)
        
        logger.info("Sync scheduler stopped")
    
    async def _get_last_execution_time(self, rule_id: str) -> Optional[datetime]:
        """Get last execution time for sync rule"""
        try:
            cursor = self.edge_db.cursor()
            cursor.execute(
                "SELECT last_executed FROM sync_rules WHERE rule_id = ?",
                (rule_id,)
            )
            result = cursor.fetchone()
            
            if result and result[0]:
                return datetime.fromisoformat(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get last execution time for {rule_id}: {str(e)}")
            return None
    
    async def _update_last_execution_time(self, rule_id: str, execution_time: datetime):
        """Update last execution time for sync rule"""
        try:
            cursor = self.edge_db.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sync_rules (rule_id, last_executed, execution_count)
                VALUES (?, ?, COALESCE((SELECT execution_count FROM sync_rules WHERE rule_id = ?), 0) + 1)
            """, (rule_id, execution_time.isoformat(), rule_id))
            
            self.edge_db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update execution time for {rule_id}: {str(e)}")
    
    async def _execute_sync_rule_batch(self, rule: SyncRule):
        """Execute sync rule for a batch of records"""
        try:
            self.stats['total_syncs_attempted'] += 1
            start_time = time.time()
            
            # Get records that need syncing for this rule
            records = await self._get_records_for_sync(rule)
            
            if not records:
                logger.debug(f"No records to sync for rule: {rule.rule_id}")
                return
            
            # Execute sync based on direction
            if rule.sync_direction == SyncDirection.EDGE_TO_CLOUD:
                success = await self._sync_edge_to_cloud(rule, records)
            elif rule.sync_direction == SyncDirection.CLOUD_TO_EDGE:
                success = await self._sync_cloud_to_edge(rule, records)
            elif rule.sync_direction == SyncDirection.BIDIRECTIONAL:
                success = await self._sync_bidirectional(rule, records)
            else:
                success = False
            
            # Update statistics
            sync_duration = (time.time() - start_time) * 1000
            self.stats['sync_durations'].append(sync_duration)
            
            if success:
                self.stats['successful_syncs'] += 1
                self.stats['last_sync_time'] = datetime.now()
                logger.info(f"Sync completed: {rule.rule_id} ({len(records)} records, {sync_duration:.1f}ms)")
            else:
                self.stats['failed_syncs'] += 1
                logger.error(f"Sync failed: {rule.rule_id}")
            
        except Exception as e:
            self.stats['failed_syncs'] += 1
            logger.error(f"Sync execution error for {rule.rule_id}: {str(e)}")
    
    async def _get_records_for_sync(self, rule: SyncRule) -> List[DataRecord]:
        """Get records that need synchronization for given rule"""
        try:
            cursor = self.edge_db.cursor()
            
            # Build query based on rule criteria
            query = """
                SELECT record_id, table_name, data_json, timestamp, version, 
                       checksum, source, last_sync, sync_status
                FROM sync_metadata 
                WHERE table_name = ? AND (sync_status = ? OR sync_status = ?)
                ORDER BY timestamp ASC
                LIMIT ?
            """
            
            cursor.execute(query, (
                rule.table_name,
                SyncStatus.PENDING.value,
                SyncStatus.FAILED.value,
                rule.batch_size
            ))
            
            results = cursor.fetchall()
            records = []
            
            for row in results:
                record = DataRecord(
                    record_id=row[0],
                    data=json.loads(row[2]) if row[2] else {},
                    timestamp=datetime.fromisoformat(row[3]),
                    version=row[4],
                    checksum=row[5],
                    source=row[6],
                    last_sync=datetime.fromisoformat(row[7]) if row[7] else None,
                    sync_status=SyncStatus(row[8])
                )
                
                # Check if record matches rule filters
                if rule.matches_record(record):
                    records.append(record)
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get records for sync rule {rule.rule_id}: {str(e)}")
            return []
    
    async def _sync_edge_to_cloud(self, rule: SyncRule, records: List[DataRecord]) -> bool:
        """
        Sync records from edge to cloud
        Mumbai local से main line पे transfer की तरह
        """
        try:
            if not records:
                return True
            
            # Prepare batch data for upload
            batch_data = {
                'device_id': self.device_id,
                'location': self.location,
                'table_name': rule.table_name,
                'sync_rule_id': rule.rule_id,
                'records': []
            }
            
            for record in records:
                batch_data['records'].append({
                    'record_id': record.record_id,
                    'data': record.data,
                    'timestamp': record.timestamp.isoformat(),
                    'version': record.version,
                    'checksum': record.checksum
                })
            
            # Simulate cloud upload (in production, this would be actual HTTP request)
            upload_success = await self._mock_cloud_upload(batch_data, len(records))
            
            if upload_success:
                # Update sync status for all records
                await self._update_records_sync_status(records, SyncStatus.COMPLETED)
                
                # Update bandwidth statistics
                data_size = len(json.dumps(batch_data).encode('utf-8'))
                self.stats['bytes_uploaded'] += data_size
                self.stats['bandwidth_usage'].append({
                    'timestamp': datetime.now(),
                    'direction': 'upload',
                    'bytes': data_size
                })
                
                return True
            else:
                # Mark records as failed
                await self._update_records_sync_status(records, SyncStatus.FAILED)
                return False
                
        except Exception as e:
            logger.error(f"Edge to cloud sync failed: {str(e)}")
            await self._update_records_sync_status(records, SyncStatus.FAILED)
            return False
    
    async def _sync_cloud_to_edge(self, rule: SyncRule, records: List[DataRecord]) -> bool:
        """
        Sync records from cloud to edge
        Main line से local train पे data transfer की तरह
        """
        try:
            # Simulate cloud data fetch
            cloud_data = await self._mock_cloud_fetch(rule.table_name, rule.batch_size)
            
            if not cloud_data:
                return True  # No data to sync
            
            updated_records = 0
            data_size = 0
            
            for cloud_record in cloud_data:
                # Convert cloud data to DataRecord
                record = DataRecord(
                    record_id=cloud_record['record_id'],
                    data=cloud_record['data'],
                    timestamp=datetime.fromisoformat(cloud_record['timestamp']),
                    version=cloud_record['version'],
                    checksum=cloud_record['checksum'],
                    source="cloud"
                )
                
                # Check for conflicts with existing edge data
                conflict = await self._detect_conflict(record, rule.table_name)
                
                if conflict:
                    await self._handle_conflict(record, conflict, rule.conflict_resolution)
                else:
                    # Update edge database
                    await self._update_edge_record(rule.table_name, record)
                    updated_records += 1
                
                data_size += len(json.dumps(record.data).encode('utf-8'))
            
            # Update bandwidth statistics
            self.stats['bytes_downloaded'] += data_size
            self.stats['bandwidth_usage'].append({
                'timestamp': datetime.now(),
                'direction': 'download',
                'bytes': data_size
            })
            
            logger.info(f"Cloud to edge sync: {updated_records} records updated")
            return True
            
        except Exception as e:
            logger.error(f"Cloud to edge sync failed: {str(e)}")
            return False
    
    async def _sync_bidirectional(self, rule: SyncRule, records: List[DataRecord]) -> bool:
        """Bidirectional sync - both edge to cloud and cloud to edge"""
        try:
            # First sync edge to cloud
            edge_to_cloud_success = await self._sync_edge_to_cloud(rule, records)
            
            # Then sync cloud to edge
            cloud_to_edge_success = await self._sync_cloud_to_edge(rule, records)
            
            return edge_to_cloud_success and cloud_to_edge_success
            
        except Exception as e:
            logger.error(f"Bidirectional sync failed: {str(e)}")
            return False
    
    async def _mock_cloud_upload(self, batch_data: Dict[str, Any], record_count: int) -> bool:
        """Mock cloud upload simulation"""
        try:
            # Simulate network latency
            latency = 0.1 + (record_count * 0.01)  # Base latency + per-record delay
            await asyncio.sleep(latency)
            
            # Simulate 95% success rate
            import random
            success = random.random() < 0.95
            
            if success:
                logger.debug(f"Mock cloud upload successful: {record_count} records")
            else:
                logger.warning(f"Mock cloud upload failed: {record_count} records")
            
            return success
            
        except Exception as e:
            logger.error(f"Mock cloud upload error: {str(e)}")
            return False
    
    async def _mock_cloud_fetch(self, table_name: str, batch_size: int) -> List[Dict[str, Any]]:
        """Mock cloud data fetch simulation"""
        try:
            # Simulate network latency
            await asyncio.sleep(0.2)
            
            # Generate mock cloud data
            import random
            
            cloud_records = []
            record_count = random.randint(0, batch_size // 2)  # Random number of records
            
            for i in range(record_count):
                record = {
                    'record_id': f"cloud_{table_name}_{uuid.uuid4().hex[:8]}",
                    'data': {
                        'cloud_field': f"cloud_value_{i}",
                        'sync_timestamp': datetime.now().isoformat(),
                        'source': 'cloud_backend'
                    },
                    'timestamp': (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
                    'version': random.randint(1, 5),
                    'checksum': hashlib.md5(f"cloud_data_{i}".encode()).hexdigest()
                }
                cloud_records.append(record)
            
            logger.debug(f"Mock cloud fetch: {len(cloud_records)} records from {table_name}")
            return cloud_records
            
        except Exception as e:
            logger.error(f"Mock cloud fetch error: {str(e)}")
            return []
    
    async def _detect_conflict(self, cloud_record: DataRecord, table_name: str) -> Optional[DataRecord]:
        """Detect conflicts between cloud and edge data"""
        try:
            cursor = self.edge_db.cursor()
            cursor.execute("""
                SELECT record_id, data_json, timestamp, version, checksum, source
                FROM sync_metadata
                WHERE record_id = ? AND table_name = ?
            """, (cloud_record.record_id, table_name))
            
            result = cursor.fetchone()
            
            if not result:
                return None  # No conflict - record doesn't exist on edge
            
            edge_record = DataRecord(
                record_id=result[0],
                data=json.loads(result[1]) if result[1] else {},
                timestamp=datetime.fromisoformat(result[2]),
                version=result[3],
                checksum=result[4],
                source=result[5]
            )
            
            # Check for actual conflicts
            if (edge_record.checksum != cloud_record.checksum and
                edge_record.version != cloud_record.version):
                
                self.stats['conflicts_detected'] += 1
                logger.warning(f"Conflict detected for record {cloud_record.record_id}")
                return edge_record
            
            return None
            
        except Exception as e:
            logger.error(f"Conflict detection failed: {str(e)}")
            return None
    
    async def _handle_conflict(self, cloud_record: DataRecord, edge_record: DataRecord, 
                             resolution_strategy: ConflictResolution):
        """
        Handle data conflicts based on resolution strategy
        Mumbai traffic conflict resolution की तरह - rules-based decision
        """
        try:
            conflict_id = f"conflict_{edge_record.record_id}_{int(time.time())}"
            
            # Log conflict
            cursor = self.edge_db.cursor()
            cursor.execute("""
                INSERT INTO conflict_log 
                (conflict_id, record_id, timestamp, edge_version, cloud_version, resolution_strategy)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                conflict_id,
                edge_record.record_id,
                datetime.now().isoformat(),
                json.dumps(asdict(edge_record)),
                json.dumps(asdict(cloud_record)),
                resolution_strategy.value
            ))
            
            resolved_record = None
            
            if resolution_strategy == ConflictResolution.LAST_WRITE_WINS:
                # Choose record with latest timestamp
                if cloud_record.timestamp > edge_record.timestamp:
                    resolved_record = cloud_record
                else:
                    resolved_record = edge_record
                    
            elif resolution_strategy == ConflictResolution.CLOUD_WINS:
                # Always choose cloud version
                resolved_record = cloud_record
                
            elif resolution_strategy == ConflictResolution.EDGE_WINS:
                # Always choose edge version
                resolved_record = edge_record
                
            elif resolution_strategy == ConflictResolution.MERGE:
                # Attempt to merge data (simplified merge)
                merged_data = {**edge_record.data, **cloud_record.data}
                resolved_record = DataRecord(
                    record_id=edge_record.record_id,
                    data=merged_data,
                    timestamp=max(edge_record.timestamp, cloud_record.timestamp),
                    version=max(edge_record.version, cloud_record.version) + 1,
                    checksum="",  # Will be recalculated
                    source="merged"
                )
                
            elif resolution_strategy == ConflictResolution.MANUAL:
                # Add to manual resolution queue
                self.conflict_queue.append({
                    'conflict_id': conflict_id,
                    'edge_record': edge_record,
                    'cloud_record': cloud_record,
                    'timestamp': datetime.now()
                })
                logger.info(f"Conflict queued for manual resolution: {conflict_id}")
                return
            
            if resolved_record:
                # Update edge database with resolved record
                await self._update_edge_record("", resolved_record)  # Table will be determined from context
                
                # Mark conflict as resolved
                cursor.execute("""
                    UPDATE conflict_log 
                    SET resolved_at = ?, resolved_by = ?
                    WHERE conflict_id = ?
                """, (datetime.now().isoformat(), "automatic", conflict_id))
                
                self.stats['conflicts_resolved'] += 1
                logger.info(f"Conflict resolved automatically: {conflict_id}")
            
            self.edge_db.commit()
            
        except Exception as e:
            logger.error(f"Conflict resolution failed: {str(e)}")
    
    async def _update_edge_record(self, table_name: str, record: DataRecord):
        """Update record in edge database"""
        try:
            cursor = self.edge_db.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sync_metadata
                (record_id, table_name, data_json, timestamp, version, checksum, source, last_sync, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.record_id,
                table_name,
                json.dumps(record.data),
                record.timestamp.isoformat(),
                record.version,
                record.checksum,
                record.source,
                datetime.now().isoformat(),
                SyncStatus.COMPLETED.value
            ))
            
            self.edge_db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update edge record {record.record_id}: {str(e)}")
    
    async def _update_records_sync_status(self, records: List[DataRecord], status: SyncStatus):
        """Update sync status for multiple records"""
        try:
            cursor = self.edge_db.cursor()
            
            for record in records:
                cursor.execute("""
                    UPDATE sync_metadata 
                    SET sync_status = ?, last_sync = ?
                    WHERE record_id = ?
                """, (status.value, datetime.now().isoformat(), record.record_id))
            
            self.edge_db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update records sync status: {str(e)}")
    
    async def _conflict_resolver_loop(self):
        """Background loop for handling manual conflict resolution"""
        logger.info("Conflict resolver started")
        
        while self.running:
            try:
                if self.conflict_queue:
                    # Process conflicts that have been waiting too long
                    current_time = datetime.now()
                    
                    # Auto-resolve conflicts older than 1 hour using LAST_WRITE_WINS
                    while self.conflict_queue:
                        conflict = self.conflict_queue[0]
                        conflict_age = (current_time - conflict['timestamp']).total_seconds()
                        
                        if conflict_age > 3600:  # 1 hour
                            conflict_item = self.conflict_queue.popleft()
                            
                            # Auto-resolve using LAST_WRITE_WINS
                            await self._handle_conflict(
                                conflict_item['cloud_record'],
                                conflict_item['edge_record'], 
                                ConflictResolution.LAST_WRITE_WINS
                            )
                            
                            logger.info(f"Auto-resolved aged conflict: {conflict_item['conflict_id']}")
                        else:
                            break
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Conflict resolver error: {str(e)}")
                await asyncio.sleep(10)
        
        logger.info("Conflict resolver stopped")
    
    async def _performance_monitor_loop(self):
        """Background performance monitoring loop"""
        logger.info("Performance monitor started")
        
        while self.running:
            try:
                # Clean up old bandwidth usage data
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(hours=1)
                
                # Remove bandwidth entries older than 1 hour
                self.stats['bandwidth_usage'] = deque([
                    entry for entry in self.stats['bandwidth_usage']
                    if entry['timestamp'] > cutoff_time
                ], maxlen=1000)
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance monitor error: {str(e)}")
                await asyncio.sleep(30)
        
        logger.info("Performance monitor stopped")
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """Get comprehensive synchronization statistics"""
        try:
            current_time = datetime.now()
            
            # Calculate bandwidth usage
            total_upload = sum(
                entry['bytes'] for entry in self.stats['bandwidth_usage']
                if entry['direction'] == 'upload'
            )
            total_download = sum(
                entry['bytes'] for entry in self.stats['bandwidth_usage']  
                if entry['direction'] == 'download'
            )
            
            # Calculate sync performance
            avg_sync_duration = (
                sum(self.stats['sync_durations']) / len(self.stats['sync_durations'])
                if self.stats['sync_durations'] else 0
            )
            
            # Get active sync rules
            active_rules = sum(1 for rule in self.sync_rules.values() if rule.enabled)
            
            return {
                "device_info": {
                    "device_id": self.device_id,
                    "location": self.location,
                    "status": "running" if self.running else "stopped"
                },
                "sync_performance": {
                    "total_syncs_attempted": self.stats['total_syncs_attempted'],
                    "successful_syncs": self.stats['successful_syncs'],
                    "failed_syncs": self.stats['failed_syncs'],
                    "success_rate_percent": (
                        (self.stats['successful_syncs'] / self.stats['total_syncs_attempted'] * 100)
                        if self.stats['total_syncs_attempted'] > 0 else 0
                    ),
                    "avg_sync_duration_ms": round(avg_sync_duration, 2),
                    "last_sync_time": self.stats['last_sync_time'].isoformat() if self.stats['last_sync_time'] else None
                },
                "conflict_management": {
                    "conflicts_detected": self.stats['conflicts_detected'],
                    "conflicts_resolved": self.stats['conflicts_resolved'],
                    "pending_conflicts": len(self.conflict_queue),
                    "conflict_resolution_rate_percent": (
                        (self.stats['conflicts_resolved'] / self.stats['conflicts_detected'] * 100)
                        if self.stats['conflicts_detected'] > 0 else 100
                    )
                },
                "bandwidth_usage": {
                    "bytes_uploaded_total": self.stats['bytes_uploaded'],
                    "bytes_downloaded_total": self.stats['bytes_downloaded'],
                    "bytes_uploaded_hour": total_upload,
                    "bytes_downloaded_hour": total_download,
                    "upload_rate_kbps": round(total_upload / 1024 / 3600, 2),
                    "download_rate_kbps": round(total_download / 1024 / 3600, 2)
                },
                "sync_rules": {
                    "total_rules": len(self.sync_rules),
                    "active_rules": active_rules,
                    "active_syncs": len(self.active_syncs)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync stats: {str(e)}")
            return {"error": str(e)}

# Example usage and testing
async def main():
    """
    Comprehensive Data Sync Handler testing
    Mumbai edge-cloud data synchronization demonstration
    """
    print("🔄 Data Sync Handler - Mumbai Edge-Cloud Synchronization")
    print("=" * 65)
    
    # Initialize sync handler
    sync_handler = DataSyncHandler("mumbai-sync-01", "Mumbai Central")
    await sync_handler.start()
    
    print(f"✅ Data Sync Handler started: {sync_handler.device_id}")
    print(f"📋 Sync Rules configured: {len(sync_handler.sync_rules)}")
    
    # Display configured sync rules
    print(f"\n📚 Configured Mumbai Sync Rules:")
    print("-" * 45)
    
    for rule_id, rule in sync_handler.sync_rules.items():
        direction_emoji = {"एज से क्लाउड": "⬆️", "क्लाउड से एज": "⬇️", "द्विदिशीय": "↕️"}
        priority_emoji = {1: "🟡", 2: "🟠", 3: "🔴"}
        
        print(f"{direction_emoji[rule.sync_direction.value]} {rule.table_name}")
        print(f"   Priority: {priority_emoji[rule.priority]} | Interval: {rule.sync_interval_seconds}s")
        print(f"   Batch Size: {rule.batch_size} | Conflict Resolution: {rule.conflict_resolution.value}")
    
    # Simulate adding various types of data
    print(f"\n💾 Simulating Mumbai Data Generation...")
    
    # Payment transactions (high priority)
    payment_data = [
        {
            "transaction_id": "pay_mumbai_001",
            "amount": 250.0,
            "merchant": "Mumbai Local Ticket",
            "location": "Mumbai",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        },
        {
            "transaction_id": "pay_mumbai_002", 
            "amount": 1500.0,
            "merchant": "Cafe Coffee Day",
            "location": "Mumbai",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    for i, payment in enumerate(payment_data):
        await sync_handler.add_record("payment_transactions", f"payment_{i+1}", payment)
        print(f"💳 Payment transaction added: {payment['transaction_id']}")
    
    # Traffic data (medium priority)
    traffic_data = [
        {
            "location": "Western Express Highway",
            "density": "Heavy",
            "speed_kmph": 15.5,
            "city": "Mumbai",
            "timestamp": datetime.now().isoformat()
        },
        {
            "location": "Bandra-Worli Sea Link",
            "density": "Moderate", 
            "speed_kmph": 45.2,
            "city": "Mumbai",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    for i, traffic in enumerate(traffic_data):
        await sync_handler.add_record("traffic_data", f"traffic_{i+1}", traffic)
        print(f"🚗 Traffic data added: {traffic['location']}")
    
    # User analytics (low priority)
    analytics_data = [
        {
            "user_id": "user_mumbai_001",
            "event": "app_opened",
            "region": "Mumbai",
            "timestamp": datetime.now().isoformat()
        },
        {
            "user_id": "user_mumbai_002",
            "event": "purchase_made",
            "region": "Mumbai", 
            "amount": 500.0,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    for i, analytics in enumerate(analytics_data):
        await sync_handler.add_record("user_analytics", f"analytics_{i+1}", analytics)
        print(f"📊 Analytics data added: {analytics['event']}")
    
    # Wait for immediate syncs to process
    print(f"\n⏱️ Waiting for immediate syncs to complete...")
    await asyncio.sleep(10)
    
    # Get initial statistics
    stats = sync_handler.get_sync_stats()
    
    print(f"\n📊 Initial Sync Statistics:")
    print("-" * 30)
    
    perf = stats["sync_performance"]
    print(f"Total Sync Attempts: {perf['total_syncs_attempted']}")
    print(f"Successful Syncs: {perf['successful_syncs']}")
    print(f"Failed Syncs: {perf['failed_syncs']}")
    print(f"Success Rate: {perf['success_rate_percent']:.1f}%")
    
    if perf['avg_sync_duration_ms'] > 0:
        print(f"Average Sync Duration: {perf['avg_sync_duration_ms']:.1f}ms")
    
    # Bandwidth usage
    bandwidth = stats["bandwidth_usage"]
    print(f"\n📡 Bandwidth Usage:")
    print(f"Data Uploaded: {bandwidth['bytes_uploaded_total']:,} bytes")
    print(f"Data Downloaded: {bandwidth['bytes_downloaded_total']:,} bytes")
    print(f"Upload Rate: {bandwidth['upload_rate_kbps']} KB/s")
    print(f"Download Rate: {bandwidth['download_rate_kbps']} KB/s")
    
    # Conflict management
    conflicts = stats["conflict_management"]
    print(f"\n⚡ Conflict Management:")
    print(f"Conflicts Detected: {conflicts['conflicts_detected']}")
    print(f"Conflicts Resolved: {conflicts['conflicts_resolved']}")
    print(f"Pending Conflicts: {conflicts['pending_conflicts']}")
    
    # Let sync scheduler run for a while
    print(f"\n🔄 Running sync scheduler for 30 seconds...")
    await asyncio.sleep(30)
    
    # Get updated statistics
    final_stats = sync_handler.get_sync_stats()
    
    print(f"\n📊 Final Sync Performance Report:")
    print("=" * 40)
    
    final_perf = final_stats["sync_performance"]
    final_bandwidth = final_stats["bandwidth_usage"]
    
    print(f"Device: {final_stats['device_info']['device_id']}")
    print(f"Location: {final_stats['device_info']['location']}")
    print(f"Status: {final_stats['device_info']['status']}")
    
    print(f"\n⚡ Performance Metrics:")
    print(f"• Total Syncs: {final_perf['total_syncs_attempted']}")
    print(f"• Success Rate: {final_perf['success_rate_percent']:.1f}%") 
    print(f"• Avg Duration: {final_perf['avg_sync_duration_ms']:.1f}ms")
    print(f"• Last Sync: {final_perf['last_sync_time']}")
    
    print(f"\n📊 Data Transfer:")
    print(f"• Total Uploaded: {final_bandwidth['bytes_uploaded_total']:,} bytes")
    print(f"• Total Downloaded: {final_bandwidth['bytes_downloaded_total']:,} bytes")
    print(f"• Hourly Upload Rate: {final_bandwidth['upload_rate_kbps']:.2f} KB/s")
    print(f"• Hourly Download Rate: {final_bandwidth['download_rate_kbps']:.2f} KB/s")
    
    # Cost analysis
    print(f"\n💰 Cost Analysis:")
    print("-" * 20)
    
    total_data_gb = (final_bandwidth['bytes_uploaded_total'] + final_bandwidth['bytes_downloaded_total']) / (1024**3)
    edge_sync_cost = total_data_gb * 0.01  # ₹0.01 per GB for edge sync
    cloud_sync_cost = total_data_gb * 1.0  # ₹1.0 per GB for cloud sync
    savings = cloud_sync_cost - edge_sync_cost
    
    print(f"Edge Sync Cost: ₹{edge_sync_cost:.3f}")
    print(f"Cloud Sync Cost: ₹{cloud_sync_cost:.2f}")
    print(f"Cost Savings: ₹{savings:.2f}")
    print(f"Savings Percentage: {(savings/cloud_sync_cost)*100:.1f}%")
    
    # Business benefits
    print(f"\n🎯 Business Benefits:")
    print("• Offline-first data availability")
    print("• Automatic conflict resolution") 
    print("• Bandwidth-efficient synchronization")
    print("• Prioritized sync for critical data")
    print("• Mumbai-optimized sync patterns")
    
    # Stop sync handler
    print(f"\n🛑 Stopping data sync handler...")
    await sync_handler.stop()
    
    print(f"\n✅ Data Sync Handler demonstration completed!")
    print(f"🔄 Mumbai edge-cloud synchronization optimized!")

if __name__ == "__main__":
    asyncio.run(main())
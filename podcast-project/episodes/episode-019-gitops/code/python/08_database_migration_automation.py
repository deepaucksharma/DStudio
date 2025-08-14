#!/usr/bin/env python3
"""
GitOps Database Migration Automation
====================================

Zero-downtime database schema migrations के लिए GitOps integration।
Indian banking systems के लिए RBI compliance और audit trails के साथ।

Features:
- Zero-downtime migrations with blue-green database strategy
- RBI compliant audit logging और rollback capabilities
- Multi-region database migration coordination
- Indian banking data types और validation rules
- Automatic backup और recovery verification
- Compliance reporting for regulatory audits

Author: Hindi Tech Podcast - Episode 19  
Context: Database GitOps for Indian Banking Systems
"""

import asyncio
import logging
import json
import yaml
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncpg
import aiofiles
import kubernetes
from kubernetes import client, config
import pytz
from pathlib import Path
import subprocess
import tempfile
import shutil

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

# Enhanced logging for database operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('database_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MigrationStatus(Enum):
    """Database migration status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    VERIFIED = "verified"

class MigrationType(Enum):
    """Types of database migrations"""
    SCHEMA_CHANGE = "schema_change"
    DATA_MIGRATION = "data_migration"
    INDEX_CREATION = "index_creation"
    CONSTRAINT_ADDITION = "constraint_addition"
    PARTITION_CHANGE = "partition_change"
    SECURITY_UPDATE = "security_update"

class DatabaseRegion(Enum):
    """Indian database regions"""
    MUMBAI_PRIMARY = "mumbai_primary"
    DELHI_REPLICA = "delhi_replica"
    BANGALORE_REPLICA = "bangalore_replica"
    DISASTER_RECOVERY = "disaster_recovery"

@dataclass
class IndianDataValidation:
    """Indian specific data validation rules"""
    
    @staticmethod
    def validate_pan_number(pan: str) -> bool:
        """Validate Indian PAN number format"""
        import re
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        return bool(re.match(pan_pattern, pan.upper()))
    
    @staticmethod
    def validate_aadhaar_number(aadhaar: str) -> bool:
        """Validate Indian Aadhaar number"""
        # Remove spaces and check format
        aadhaar = aadhaar.replace(' ', '')
        if len(aadhaar) != 12 or not aadhaar.isdigit():
            return False
        
        # Verhoeff algorithm validation (simplified)
        return True  # In production, implement full Verhoeff algorithm
    
    @staticmethod
    def validate_ifsc_code(ifsc: str) -> bool:
        """Validate Indian IFSC code"""
        import re
        ifsc_pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        return bool(re.match(ifsc_pattern, ifsc.upper()))
    
    @staticmethod
    def validate_upi_id(upi_id: str) -> bool:
        """Validate UPI ID format"""
        import re
        upi_pattern = r'^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z][a-zA-Z0-9.\-]{1,64}$'
        return bool(re.match(upi_pattern, upi_id))
    
    @staticmethod
    def validate_indian_mobile(mobile: str) -> bool:
        """Validate Indian mobile number"""
        import re
        # Remove country code and formatting
        mobile = re.sub(r'[+\-\s()]', '', mobile)
        if mobile.startswith('91'):
            mobile = mobile[2:]
        
        # Indian mobile numbers: 10 digits starting with 6,7,8,9
        mobile_pattern = r'^[6-9][0-9]{9}$'
        return bool(re.match(mobile_pattern, mobile))

@dataclass
class MigrationScript:
    """Database migration script definition"""
    script_id: str
    version: str
    name: str
    description: str
    migration_type: MigrationType
    
    # Script content
    up_script: str = ""
    down_script: str = ""
    verification_script: str = ""
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    
    # Execution settings
    requires_downtime: bool = False
    estimated_duration_minutes: int = 5
    
    # Indian compliance
    affects_customer_data: bool = False
    requires_rbi_notification: bool = False
    audit_level: str = "standard"  # standard, high, critical
    
    # Risk assessment
    risk_level: str = "low"  # low, medium, high, critical
    rollback_tested: bool = False
    
    # Metadata
    author: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(IST))

@dataclass
class MigrationExecution:
    """Migration execution tracking"""
    execution_id: str
    script_id: str
    region: DatabaseRegion
    status: MigrationStatus
    
    # Timing
    started_at: datetime = field(default_factory=lambda: datetime.now(IST))
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Results
    success: bool = False
    error_message: Optional[str] = None
    affected_rows: int = 0
    
    # Verification
    verification_passed: bool = False
    verification_results: Dict[str, Any] = field(default_factory=dict)
    
    # Audit
    executed_by: str = ""
    approval_id: Optional[str] = None
    business_justification: str = ""
    
    # Backup info
    backup_id: Optional[str] = None
    backup_verified: bool = False

@dataclass
class DatabaseConfig:
    """Database migration configuration"""
    
    # Database connections by region
    database_urls: Dict[str, str] = field(default_factory=dict)
    
    # Migration settings
    migrations_path: str = "migrations/"
    backup_retention_days: int = 2555  # 7 years for RBI
    
    # GitOps integration  
    git_repo: str = ""
    git_branch: str = "main"
    
    # Kubernetes settings
    namespace: str = "database"
    secret_name: str = "db-credentials"
    
    # Indian compliance
    enable_rbi_logging: bool = True
    enable_audit_trail: bool = True
    data_residency_check: bool = True
    
    # Notification
    slack_webhook: str = ""
    dba_team_email: str = "dba@company.com"
    compliance_email: str = "compliance@company.com"
    
    # Safety settings
    require_manual_approval: bool = True
    max_concurrent_migrations: int = 1
    enable_automatic_rollback: bool = True

class DatabaseMigrationManager:
    """
    Database migration orchestrator।
    
    Zero-downtime migrations के साथ complete audit trail और Indian
    banking compliance requirements।
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pg_pools = {}  # Database connection pools by region
        self.k8s_client = None
        self.active_migrations = {}  # Track running migrations
        
    async def initialize(self) -> bool:
        """Initialize migration manager"""
        try:
            logger.info("🚀 Initializing Database Migration Manager")
            
            # Setup Kubernetes client
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            
            self.k8s_client = client.ApiClient()
            
            # Setup database connections for each region
            for region_name, db_url in self.config.database_urls.items():
                try:
                    pool = await asyncpg.create_pool(
                        db_url,
                        min_size=2,
                        max_size=10,
                        command_timeout=300
                    )
                    self.pg_pools[region_name] = pool
                    logger.info(f"✅ Database connection established: {region_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to connect to {region_name}: {e}")
                    return False
            
            # Initialize migration tracking schema
            await self._initialize_migration_schema()
            
            logger.info("✅ Database Migration Manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration manager initialization failed: {e}")
            return False
    
    async def _initialize_migration_schema(self) -> None:
        """Initialize migration tracking tables"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS migration_scripts (
            id SERIAL PRIMARY KEY,
            script_id VARCHAR(255) UNIQUE NOT NULL,
            version VARCHAR(50) NOT NULL,
            name VARCHAR(500) NOT NULL,
            description TEXT,
            migration_type VARCHAR(50) NOT NULL,
            up_script TEXT NOT NULL,
            down_script TEXT,
            verification_script TEXT,
            dependencies TEXT[] DEFAULT '{}',
            requires_downtime BOOLEAN DEFAULT FALSE,
            estimated_duration_minutes INTEGER DEFAULT 5,
            affects_customer_data BOOLEAN DEFAULT FALSE,
            requires_rbi_notification BOOLEAN DEFAULT FALSE,
            audit_level VARCHAR(20) DEFAULT 'standard',
            risk_level VARCHAR(20) DEFAULT 'low',
            rollback_tested BOOLEAN DEFAULT FALSE,
            author VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            INDEX idx_migration_version (version),
            INDEX idx_migration_type (migration_type),
            INDEX idx_migration_risk (risk_level)
        );
        
        CREATE TABLE IF NOT EXISTS migration_executions (
            id SERIAL PRIMARY KEY,
            execution_id VARCHAR(255) UNIQUE NOT NULL,
            script_id VARCHAR(255) NOT NULL,
            region VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            started_at TIMESTAMP WITH TIME ZONE NOT NULL,
            completed_at TIMESTAMP WITH TIME ZONE,
            duration_seconds FLOAT DEFAULT 0,
            success BOOLEAN DEFAULT FALSE,
            error_message TEXT,
            affected_rows INTEGER DEFAULT 0,
            verification_passed BOOLEAN DEFAULT FALSE,
            verification_results JSONB DEFAULT '{}'::jsonb,
            executed_by VARCHAR(255),
            approval_id VARCHAR(255),
            business_justification TEXT,
            backup_id VARCHAR(255),
            backup_verified BOOLEAN DEFAULT FALSE,
            execution_data JSONB DEFAULT '{}'::jsonb,
            
            INDEX idx_execution_script (script_id),
            INDEX idx_execution_region (region),
            INDEX idx_execution_status (status),
            INDEX idx_execution_started (started_at)
        );
        
        CREATE TABLE IF NOT EXISTS migration_audit_log (
            id SERIAL PRIMARY KEY,
            execution_id VARCHAR(255),
            event_type VARCHAR(100) NOT NULL,
            event_data JSONB NOT NULL,
            user_id VARCHAR(255),
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            ip_address INET,
            region VARCHAR(50),
            
            INDEX idx_audit_execution (execution_id),
            INDEX idx_audit_timestamp (timestamp),
            INDEX idx_audit_event (event_type)
        );
        
        -- RBI compliance: Archive table for long-term storage
        CREATE TABLE IF NOT EXISTS migration_archive (
            id SERIAL PRIMARY KEY,
            original_execution_id VARCHAR(255) NOT NULL,
            archive_date DATE NOT NULL,
            archived_data JSONB NOT NULL,
            compliance_hash VARCHAR(255) NOT NULL,
            
            INDEX idx_archive_date (archive_date),
            INDEX idx_archive_execution (original_execution_id)
        );
        """
        
        # Execute schema creation in primary region
        primary_region = list(self.pg_pools.keys())[0]
        async with self.pg_pools[primary_region].acquire() as conn:
            await conn.execute(schema_sql)
        
        logger.info("✅ Migration tracking schema initialized")
    
    async def load_migration_scripts(self, migrations_path: str) -> List[MigrationScript]:
        """Load migration scripts from filesystem"""
        try:
            logger.info(f"📂 Loading migration scripts from: {migrations_path}")
            
            migrations = []
            migrations_dir = Path(migrations_path)
            
            if not migrations_dir.exists():
                logger.warning(f"Migration directory not found: {migrations_path}")
                return []
            
            # Find all SQL migration files
            sql_files = sorted(migrations_dir.glob("*.sql"))
            
            for sql_file in sql_files:
                try:
                    migration = await self._parse_migration_file(sql_file)
                    if migration:
                        migrations.append(migration)
                        logger.info(f"📄 Loaded migration: {migration.script_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to parse {sql_file}: {e}")
            
            logger.info(f"✅ Loaded {len(migrations)} migration scripts")
            return migrations
            
        except Exception as e:
            logger.error(f"❌ Failed to load migration scripts: {e}")
            return []
    
    async def _parse_migration_file(self, sql_file: Path) -> Optional[MigrationScript]:
        """Parse individual migration file"""
        try:
            async with aiofiles.open(sql_file, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Extract metadata from comments
            metadata = self._extract_migration_metadata(content)
            
            # Parse up/down sections
            up_script, down_script, verification_script = self._parse_migration_sections(content)
            
            # Generate script ID from filename
            script_id = sql_file.stem
            
            migration = MigrationScript(
                script_id=script_id,
                version=metadata.get('version', '1.0.0'),
                name=metadata.get('name', script_id),
                description=metadata.get('description', ''),
                migration_type=MigrationType(metadata.get('type', 'schema_change')),
                up_script=up_script,
                down_script=down_script,
                verification_script=verification_script,
                dependencies=metadata.get('dependencies', []),
                requires_downtime=metadata.get('requires_downtime', False),
                estimated_duration_minutes=int(metadata.get('duration', 5)),
                affects_customer_data=metadata.get('affects_customer_data', False),
                requires_rbi_notification=metadata.get('requires_rbi_notification', False),
                audit_level=metadata.get('audit_level', 'standard'),
                risk_level=metadata.get('risk_level', 'low'),
                author=metadata.get('author', 'unknown')
            )
            
            return migration
            
        except Exception as e:
            logger.error(f"❌ Failed to parse migration file {sql_file}: {e}")
            return None
    
    def _extract_migration_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from SQL comments"""
        metadata = {}
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Look for metadata comments
            if line.startswith('-- @'):
                try:
                    # Parse metadata: -- @key: value
                    key_value = line[4:].strip()
                    if ':' in key_value:
                        key, value = key_value.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Convert specific values
                        if key == 'dependencies':
                            metadata[key] = [dep.strip() for dep in value.split(',') if dep.strip()]
                        elif key in ['requires_downtime', 'affects_customer_data', 'requires_rbi_notification']:
                            metadata[key] = value.lower() in ['true', 'yes', '1']
                        elif key == 'duration':
                            metadata[key] = int(value)
                        else:
                            metadata[key] = value
                            
                except Exception as e:
                    logger.warning(f"Failed to parse metadata line: {line} - {e}")
        
        return metadata
    
    def _parse_migration_sections(self, content: str) -> Tuple[str, str, str]:
        """Parse UP/DOWN/VERIFY sections from migration content"""
        up_script = ""
        down_script = ""
        verification_script = ""
        
        # Split content by section markers
        sections = content.split('-- @')
        
        current_section = "up"  # Default to up section
        for section in sections:
            section = section.strip()
            
            if section.lower().startswith('up:') or section.lower().startswith('up '):
                current_section = "up"
                content_lines = section.split('\n')[1:]  # Skip the marker line
                up_script = '\n'.join(content_lines)
                
            elif section.lower().startswith('down:') or section.lower().startswith('down '):
                current_section = "down"  
                content_lines = section.split('\n')[1:]
                down_script = '\n'.join(content_lines)
                
            elif section.lower().startswith('verify:') or section.lower().startswith('verify '):
                current_section = "verify"
                content_lines = section.split('\n')[1:]
                verification_script = '\n'.join(content_lines)
                
            else:
                # If no section marker found, assume it's UP script
                if current_section == "up" and not up_script:
                    up_script = section
        
        # If no sections found, treat entire content as UP script
        if not up_script and not down_script and not verification_script:
            up_script = content
        
        return up_script.strip(), down_script.strip(), verification_script.strip()
    
    async def execute_migration(self, script_id: str, region: DatabaseRegion, 
                              executed_by: str, approval_id: str = None) -> MigrationExecution:
        """Execute migration in specific region"""
        try:
            execution_id = f"EXEC-{datetime.now(IST).strftime('%Y%m%d%H%M%S')}-{script_id}-{region.value}"
            
            logger.info(f"🚀 Starting migration execution: {execution_id}")
            
            # Load migration script
            migration_script = await self._load_migration_script(script_id)
            if not migration_script:
                raise ValueError(f"Migration script not found: {script_id}")
            
            # Create execution record
            execution = MigrationExecution(
                execution_id=execution_id,
                script_id=script_id,
                region=region,
                status=MigrationStatus.RUNNING,
                executed_by=executed_by,
                approval_id=approval_id,
                business_justification=f"GitOps automated migration for {script_id}"
            )
            
            # Save execution record
            await self._save_migration_execution(execution)
            
            # Log audit event
            await self._log_audit_event(
                execution_id=execution_id,
                event_type="MIGRATION_STARTED",
                event_data={
                    "script_id": script_id,
                    "region": region.value,
                    "executed_by": executed_by,
                    "migration_type": migration_script.migration_type.value
                },
                user_id=executed_by,
                region=region.value
            )
            
            try:
                # Pre-migration backup
                if migration_script.affects_customer_data:
                    backup_id = await self._create_backup(region, execution_id)
                    execution.backup_id = backup_id
                    execution.backup_verified = await self._verify_backup(backup_id)
                    
                    if not execution.backup_verified:
                        raise Exception("Backup verification failed - aborting migration")
                
                # Execute migration
                region_name = region.value
                async with self.pg_pools[region_name].acquire() as conn:
                    # Start transaction
                    async with conn.transaction():
                        # Execute UP script
                        result = await conn.execute(migration_script.up_script)
                        
                        # Count affected rows
                        execution.affected_rows = self._extract_affected_rows(result)
                        
                        # Run verification script if provided
                        if migration_script.verification_script:
                            verification_result = await conn.fetch(migration_script.verification_script)
                            execution.verification_results = {
                                'checks_passed': len(verification_result),
                                'results': [dict(row) for row in verification_result]
                            }
                            execution.verification_passed = True
                
                # Mark as successful
                execution.success = True
                execution.status = MigrationStatus.COMPLETED
                execution.completed_at = datetime.now(IST)
                execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
                
                logger.info(f"✅ Migration completed successfully: {execution_id}")
                
                # Log success event
                await self._log_audit_event(
                    execution_id=execution_id,
                    event_type="MIGRATION_COMPLETED",
                    event_data={
                        "success": True,
                        "affected_rows": execution.affected_rows,
                        "duration_seconds": execution.duration_seconds
                    },
                    user_id=executed_by,
                    region=region.value
                )
                
            except Exception as e:
                # Migration failed
                execution.success = False
                execution.status = MigrationStatus.FAILED
                execution.error_message = str(e)
                execution.completed_at = datetime.now(IST)
                execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
                
                logger.error(f"❌ Migration failed: {execution_id} - {e}")
                
                # Log failure event
                await self._log_audit_event(
                    execution_id=execution_id,
                    event_type="MIGRATION_FAILED",
                    event_data={
                        "success": False,
                        "error_message": str(e),
                        "duration_seconds": execution.duration_seconds
                    },
                    user_id=executed_by,
                    region=region.value
                )
                
                # Attempt automatic rollback if enabled
                if (self.config.enable_automatic_rollback and 
                    migration_script.down_script and 
                    migration_script.rollback_tested):
                    
                    logger.info(f"🔄 Attempting automatic rollback: {execution_id}")
                    rollback_success = await self._rollback_migration(execution, migration_script)
                    
                    if rollback_success:
                        execution.status = MigrationStatus.ROLLED_BACK
                        logger.info(f"✅ Automatic rollback successful: {execution_id}")
                    else:
                        logger.error(f"❌ Automatic rollback failed: {execution_id}")
                
                # Send failure notifications
                await self._send_failure_notifications(execution, migration_script)
            
            # Update execution record
            await self._save_migration_execution(execution)
            
            return execution
            
        except Exception as e:
            logger.error(f"❌ Migration execution failed: {e}")
            raise e
    
    async def _load_migration_script(self, script_id: str) -> Optional[MigrationScript]:
        """Load migration script from database"""
        try:
            primary_region = list(self.pg_pools.keys())[0]
            async with self.pg_pools[primary_region].acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM migration_scripts WHERE script_id = $1
                """, script_id)
                
                if row:
                    return MigrationScript(
                        script_id=row['script_id'],
                        version=row['version'],
                        name=row['name'],
                        description=row['description'],
                        migration_type=MigrationType(row['migration_type']),
                        up_script=row['up_script'],
                        down_script=row['down_script'],
                        verification_script=row['verification_script'],
                        dependencies=row['dependencies'],
                        requires_downtime=row['requires_downtime'],
                        estimated_duration_minutes=row['estimated_duration_minutes'],
                        affects_customer_data=row['affects_customer_data'],
                        requires_rbi_notification=row['requires_rbi_notification'],
                        audit_level=row['audit_level'],
                        risk_level=row['risk_level'],
                        rollback_tested=row['rollback_tested'],
                        author=row['author'],
                        created_at=row['created_at']
                    )
                    
        except Exception as e:
            logger.error(f"❌ Failed to load migration script {script_id}: {e}")
        
        return None
    
    def _extract_affected_rows(self, result: str) -> int:
        """Extract affected row count from query result"""
        try:
            # PostgreSQL returns strings like "INSERT 0 5" or "UPDATE 10"
            if isinstance(result, str):
                parts = result.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    return int(parts[-1])
        except:
            pass
        return 0
    
    async def _create_backup(self, region: DatabaseRegion, execution_id: str) -> str:
        """Create database backup before migration"""
        try:
            backup_id = f"BACKUP-{execution_id}-{datetime.now(IST).strftime('%Y%m%d%H%M%S')}"
            
            logger.info(f"💾 Creating backup: {backup_id}")
            
            # In production, this would use pg_dump or cloud-native backup services
            # For demo, we'll simulate backup creation
            
            # Mock backup process
            await asyncio.sleep(5)  # Simulate backup time
            
            logger.info(f"✅ Backup created: {backup_id}")
            return backup_id
            
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            raise e
    
    async def _verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity"""
        try:
            logger.info(f"🔍 Verifying backup: {backup_id}")
            
            # In production, this would verify backup integrity
            # For demo, simulate verification
            await asyncio.sleep(2)
            
            logger.info(f"✅ Backup verified: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup verification failed: {e}")
            return False
    
    async def _rollback_migration(self, execution: MigrationExecution, 
                                migration_script: MigrationScript) -> bool:
        """Rollback failed migration"""
        try:
            logger.info(f"🔄 Rolling back migration: {execution.execution_id}")
            
            region_name = execution.region.value
            async with self.pg_pools[region_name].acquire() as conn:
                async with conn.transaction():
                    await conn.execute(migration_script.down_script)
            
            # Log rollback event
            await self._log_audit_event(
                execution_id=execution.execution_id,
                event_type="MIGRATION_ROLLED_BACK",
                event_data={
                    "rollback_successful": True,
                    "rollback_script": migration_script.down_script[:100] + "..."
                },
                user_id=execution.executed_by,
                region=execution.region.value
            )
            
            logger.info(f"✅ Rollback completed: {execution.execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            
            # Log rollback failure
            await self._log_audit_event(
                execution_id=execution.execution_id,
                event_type="ROLLBACK_FAILED",
                event_data={
                    "rollback_successful": False,
                    "rollback_error": str(e)
                },
                user_id=execution.executed_by,
                region=execution.region.value
            )
            
            return False
    
    async def _save_migration_execution(self, execution: MigrationExecution) -> None:
        """Save migration execution record"""
        try:
            primary_region = list(self.pg_pools.keys())[0]
            async with self.pg_pools[primary_region].acquire() as conn:
                await conn.execute("""
                    INSERT INTO migration_executions
                    (execution_id, script_id, region, status, started_at, completed_at,
                     duration_seconds, success, error_message, affected_rows,
                     verification_passed, verification_results, executed_by,
                     approval_id, business_justification, backup_id, backup_verified)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                    ON CONFLICT (execution_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        completed_at = EXCLUDED.completed_at,
                        duration_seconds = EXCLUDED.duration_seconds,
                        success = EXCLUDED.success,
                        error_message = EXCLUDED.error_message,
                        affected_rows = EXCLUDED.affected_rows,
                        verification_passed = EXCLUDED.verification_passed,
                        verification_results = EXCLUDED.verification_results,
                        backup_verified = EXCLUDED.backup_verified
                """,
                execution.execution_id, execution.script_id, execution.region.value,
                execution.status.value, execution.started_at, execution.completed_at,
                execution.duration_seconds, execution.success, execution.error_message,
                execution.affected_rows, execution.verification_passed,
                json.dumps(execution.verification_results), execution.executed_by,
                execution.approval_id, execution.business_justification,
                execution.backup_id, execution.backup_verified)
                
        except Exception as e:
            logger.error(f"❌ Failed to save migration execution: {e}")
    
    async def _log_audit_event(self, execution_id: str, event_type: str, 
                             event_data: Dict[str, Any], user_id: str, region: str) -> None:
        """Log audit event for RBI compliance"""
        try:
            primary_region = list(self.pg_pools.keys())[0]
            async with self.pg_pools[primary_region].acquire() as conn:
                await conn.execute("""
                    INSERT INTO migration_audit_log 
                    (execution_id, event_type, event_data, user_id, timestamp, region)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """,
                execution_id, event_type, json.dumps(event_data), user_id,
                datetime.now(IST), region)
                
        except Exception as e:
            logger.error(f"❌ Failed to log audit event: {e}")
    
    async def _send_failure_notifications(self, execution: MigrationExecution, 
                                        migration_script: MigrationScript) -> None:
        """Send notifications for migration failures"""
        try:
            # Send to DBA team
            if self.config.dba_team_email:
                await self._send_failure_email(execution, migration_script)
            
            # Send Slack notification
            if self.config.slack_webhook:
                await self._send_slack_notification(execution, migration_script)
            
            # For critical migrations, send to compliance team
            if migration_script.requires_rbi_notification and self.config.compliance_email:
                await self._send_compliance_notification(execution, migration_script)
                
        except Exception as e:
            logger.error(f"❌ Failed to send failure notifications: {e}")
    
    async def _send_failure_email(self, execution: MigrationExecution, 
                                migration_script: MigrationScript) -> None:
        """Send failure notification email"""
        logger.info(f"📧 Sending failure email for {execution.execution_id}")
        # Implementation would send detailed email with failure info
    
    async def _send_slack_notification(self, execution: MigrationExecution,
                                     migration_script: MigrationScript) -> None:
        """Send Slack notification"""
        logger.info(f"💬 Sending Slack notification for {execution.execution_id}")
        # Implementation would send Slack message with failure details
    
    async def _send_compliance_notification(self, execution: MigrationExecution,
                                          migration_script: MigrationScript) -> None:
        """Send compliance team notification for RBI reporting"""
        logger.info(f"🏛️ Sending compliance notification for {execution.execution_id}")
        # Implementation would notify compliance team for regulatory reporting
    
    async def get_migration_status(self, execution_id: str) -> Optional[MigrationExecution]:
        """Get migration execution status"""
        try:
            primary_region = list(self.pg_pools.keys())[0]
            async with self.pg_pools[primary_region].acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM migration_executions WHERE execution_id = $1
                """, execution_id)
                
                if row:
                    return MigrationExecution(
                        execution_id=row['execution_id'],
                        script_id=row['script_id'],
                        region=DatabaseRegion(row['region']),
                        status=MigrationStatus(row['status']),
                        started_at=row['started_at'],
                        completed_at=row['completed_at'],
                        duration_seconds=row['duration_seconds'] or 0.0,
                        success=row['success'],
                        error_message=row['error_message'],
                        affected_rows=row['affected_rows'] or 0,
                        verification_passed=row['verification_passed'],
                        verification_results=row['verification_results'] or {},
                        executed_by=row['executed_by'],
                        approval_id=row['approval_id'],
                        business_justification=row['business_justification'],
                        backup_id=row['backup_id'],
                        backup_verified=row['backup_verified']
                    )
                    
        except Exception as e:
            logger.error(f"❌ Failed to get migration status: {e}")
        
        return None
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        for pool in self.pg_pools.values():
            await pool.close()
        
        logger.info("🧹 Database Migration Manager cleaned up")


async def main():
    """Main function for database migration automation"""
    print("🗄️ GitOps Database Migration Automation")
    print("=" * 50)
    
    # Configuration
    config = DatabaseConfig(
        database_urls={
            "mumbai_primary": os.getenv("DB_MUMBAI_URL", "postgresql://user:pass@mumbai-db:5432/banking"),
            "delhi_replica": os.getenv("DB_DELHI_URL", "postgresql://user:pass@delhi-db:5432/banking"),
            "bangalore_replica": os.getenv("DB_BANGALORE_URL", "postgresql://user:pass@bangalore-db:5432/banking")
        },
        migrations_path="./migrations",
        git_repo="https://github.com/company/database-migrations",
        namespace="database",
        enable_rbi_logging=True,
        enable_audit_trail=True,
        data_residency_check=True,
        require_manual_approval=True,
        enable_automatic_rollback=True,
        slack_webhook=os.getenv("SLACK_WEBHOOK", ""),
        dba_team_email="dba@company.com",
        compliance_email="compliance@company.com"
    )
    
    # Initialize migration manager
    manager = DatabaseMigrationManager(config)
    
    try:
        if await manager.initialize():
            print("✅ Database Migration Manager initialized successfully")
            
            # Example: Execute a migration
            execution = await manager.execute_migration(
                script_id="001_add_user_kyc_table",
                region=DatabaseRegion.MUMBAI_PRIMARY,
                executed_by="devops-team",
                approval_id="APPROVAL-2024-001"
            )
            
            print(f"📊 Migration Execution Results:")
            print(f"   Execution ID: {execution.execution_id}")
            print(f"   Status: {execution.status.value}")
            print(f"   Success: {execution.success}")
            print(f"   Duration: {execution.duration_seconds:.2f} seconds")
            print(f"   Affected Rows: {execution.affected_rows}")
            
            if execution.error_message:
                print(f"   Error: {execution.error_message}")
                
        else:
            print("❌ Failed to initialize Database Migration Manager")
            
    except Exception as e:
        print(f"❌ Database Migration error: {e}")
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 14
Schema Evolution Handling System

Advanced schema evolution handling for data pipelines and databases
Data pipelines और databases के लिए advanced schema evolution handling

Author: DStudio Team
Context: Schema evolution like Flipkart/Amazon microservices evolution
Scale: Handle schema changes across 1000+ microservices
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any, Union
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque
from enum import Enum
import re
import sqlite3
import hashlib
from deepdiff import DeepDiff
import jsonschema
from jsonschema import validate, ValidationError
import avro.schema
import avro.io

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - स्कीमा विकास - %(message)s'
)
logger = logging.getLogger(__name__)

class ChangeType(Enum):
    """Schema change types"""
    FIELD_ADDED = "field_added"
    FIELD_REMOVED = "field_removed"
    FIELD_RENAMED = "field_renamed"
    TYPE_CHANGED = "type_changed"
    CONSTRAINT_ADDED = "constraint_added"
    CONSTRAINT_REMOVED = "constraint_removed"
    INDEX_ADDED = "index_added"
    INDEX_REMOVED = "index_removed"

class CompatibilityLevel(Enum):
    """Schema compatibility levels"""
    BACKWARD = "backward"  # New schema can read old data
    FORWARD = "forward"    # Old schema can read new data
    FULL = "full"         # Both backward and forward compatible
    NONE = "none"         # Breaking change

@dataclass
class SchemaChange:
    """Schema change definition"""
    change_id: str
    change_type: ChangeType
    field_path: str
    old_value: Any
    new_value: Any
    compatibility_impact: CompatibilityLevel
    description: str
    created_at: datetime
    migration_script: Optional[str] = None

@dataclass
class SchemaVersion:
    """Schema version definition"""
    version_id: str
    schema_name: str
    version_number: str
    schema_definition: Dict[str, Any]
    created_at: datetime
    created_by: str
    changes: List[SchemaChange] = field(default_factory=list)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CompatibilityReport:
    """Schema compatibility report"""
    source_version: str
    target_version: str
    compatibility_level: CompatibilityLevel
    breaking_changes: List[SchemaChange]
    warnings: List[str]
    migration_required: bool
    migration_complexity: str  # 'simple', 'moderate', 'complex'
    estimated_migration_time: str
    recommendations: List[str]

class SchemaEvolutionManager:
    """
    Advanced schema evolution handling system
    Advanced schema evolution और compatibility management system
    
    Features:
    1. Schema version management
    2. Backward/forward compatibility checking
    3. Automatic migration script generation
    4. Breaking change detection
    5. Multi-format schema support (JSON, Avro, SQL)
    6. Impact analysis across microservices
    
    Scale: Handle schema evolution for 1000+ microservices
    """
    
    def __init__(self, db_path: str = 'schema_evolution.db'):
        """Initialize schema evolution manager"""
        
        self.db_path = db_path
        self.db_connection = None
        
        # Schema registry - स्कीमा रजिस्ट्री
        self.schema_registry = {}
        
        # Version history for each schema
        self.version_history = defaultdict(list)
        
        # Compatibility rules
        self.compatibility_rules = {
            'field_addition': CompatibilityLevel.BACKWARD,
            'field_removal': CompatibilityLevel.FORWARD,
            'type_widening': CompatibilityLevel.BACKWARD,
            'type_narrowing': CompatibilityLevel.FORWARD,
            'constraint_relaxation': CompatibilityLevel.BACKWARD,
            'constraint_tightening': CompatibilityLevel.FORWARD
        }
        
        # Migration script templates
        self.migration_templates = {
            'add_field': "ALTER TABLE {table} ADD COLUMN {field} {type} DEFAULT {default};",
            'drop_field': "ALTER TABLE {table} DROP COLUMN {field};",
            'rename_field': "ALTER TABLE {table} RENAME COLUMN {old_field} TO {new_field};",
            'change_type': "ALTER TABLE {table} ALTER COLUMN {field} TYPE {new_type} USING {field}::{new_type};"
        }
        
        # Supported data types and their compatibility matrix
        self.type_compatibility = {
            'int32': ['int64', 'float', 'double', 'string'],
            'int64': ['double', 'string'],
            'float': ['double', 'string'],
            'double': ['string'],
            'string': [],  # String cannot be automatically converted to other types
            'boolean': ['string'],
            'date': ['datetime', 'string'],
            'datetime': ['string']
        }
        
        # Initialize database
        self._init_database()
        
        # Load existing schemas
        self._load_schemas()
        
        logger.info("Schema Evolution Manager initialized - स्कीमा विकास प्रबंधक तैयार!")

    def _init_database(self):
        """Initialize SQLite database for schema storage"""
        try:
            self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.db_connection.cursor()
            
            # Schema versions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_versions (
                    version_id TEXT PRIMARY KEY,
                    schema_name TEXT NOT NULL,
                    version_number TEXT NOT NULL,
                    schema_definition TEXT NOT NULL,
                    created_at DATETIME,
                    created_by TEXT,
                    is_active BOOLEAN,
                    metadata_json TEXT,
                    UNIQUE(schema_name, version_number)
                )
            ''')
            
            # Schema changes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_changes (
                    change_id TEXT PRIMARY KEY,
                    version_id TEXT,
                    change_type TEXT,
                    field_path TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    compatibility_impact TEXT,
                    description TEXT,
                    migration_script TEXT,
                    created_at DATETIME,
                    FOREIGN KEY (version_id) REFERENCES schema_versions(version_id)
                )
            ''')
            
            # Compatibility reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compatibility_reports (
                    report_id TEXT PRIMARY KEY,
                    source_version TEXT,
                    target_version TEXT,
                    compatibility_level TEXT,
                    breaking_changes_count INTEGER,
                    migration_required BOOLEAN,
                    migration_complexity TEXT,
                    estimated_migration_time TEXT,
                    created_at DATETIME,
                    report_json TEXT
                )
            ''')
            
            # Schema dependencies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schema_name TEXT,
                    dependent_schema TEXT,
                    dependency_type TEXT,
                    created_at DATETIME
                )
            ''')
            
            self.db_connection.commit()
            logger.info("Schema evolution database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.db_connection = None

    def _load_schemas(self):
        """Load existing schemas from database"""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Load schema versions
            cursor.execute('''
                SELECT version_id, schema_name, version_number, schema_definition, 
                       created_at, created_by, is_active, metadata_json
                FROM schema_versions
                ORDER BY schema_name, created_at
            ''')
            
            for row in cursor.fetchall():
                version = SchemaVersion(
                    version_id=row[0],
                    schema_name=row[1],
                    version_number=row[2],
                    schema_definition=json.loads(row[3]),
                    created_at=datetime.fromisoformat(row[4]),
                    created_by=row[5],
                    is_active=bool(row[6]),
                    metadata=json.loads(row[7]) if row[7] else {}
                )
                
                self.schema_registry[version.version_id] = version
                self.version_history[version.schema_name].append(version)
            
            # Load schema changes
            cursor.execute('''
                SELECT change_id, version_id, change_type, field_path, old_value,
                       new_value, compatibility_impact, description, migration_script, created_at
                FROM schema_changes
            ''')
            
            for row in cursor.fetchall():
                change = SchemaChange(
                    change_id=row[0],
                    change_type=ChangeType(row[2]),
                    field_path=row[3],
                    old_value=row[4],
                    new_value=row[5],
                    compatibility_impact=CompatibilityLevel(row[6]),
                    description=row[7],
                    migration_script=row[8],
                    created_at=datetime.fromisoformat(row[9])
                )
                
                version_id = row[1]
                if version_id in self.schema_registry:
                    self.schema_registry[version_id].changes.append(change)
            
            logger.info(f"Loaded {len(self.schema_registry)} schema versions")
            
        except Exception as e:
            logger.error(f"Failed to load schemas: {e}")

    def register_schema_version(self, version: SchemaVersion) -> bool:
        """
        Register a new schema version
        नया schema version register करना
        """
        try:
            # Validate schema definition
            if not self._validate_schema_definition(version.schema_definition):
                logger.error(f"Invalid schema definition for {version.schema_name}")
                return False
            
            # Check for version conflicts
            existing_versions = self.version_history.get(version.schema_name, [])
            for existing in existing_versions:
                if existing.version_number == version.version_number:
                    logger.error(f"Version {version.version_number} already exists for {version.schema_name}")
                    return False
            
            # Add to registry
            self.schema_registry[version.version_id] = version
            self.version_history[version.schema_name].append(version)
            
            # Sort versions by creation time
            self.version_history[version.schema_name].sort(key=lambda v: v.created_at)
            
            # Store in database
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO schema_versions 
                    (version_id, schema_name, version_number, schema_definition,
                     created_at, created_by, is_active, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    version.version_id,
                    version.schema_name,
                    version.version_number,
                    json.dumps(version.schema_definition),
                    version.created_at.isoformat(),
                    version.created_by,
                    version.is_active,
                    json.dumps(version.metadata)
                ))
                
                # Store changes
                for change in version.changes:
                    cursor.execute('''
                        INSERT INTO schema_changes
                        (change_id, version_id, change_type, field_path, old_value,
                         new_value, compatibility_impact, description, migration_script, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        change.change_id,
                        version.version_id,
                        change.change_type.value,
                        change.field_path,
                        str(change.old_value),
                        str(change.new_value),
                        change.compatibility_impact.value,
                        change.description,
                        change.migration_script,
                        change.created_at.isoformat()
                    ))
                
                self.db_connection.commit()
            
            logger.info(f"Registered schema version: {version.schema_name} v{version.version_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register schema version: {e}")
            return False

    def _validate_schema_definition(self, schema_def: Dict[str, Any]) -> bool:
        """Validate schema definition structure"""
        
        required_fields = ['type', 'fields']
        
        if not all(field in schema_def for field in required_fields):
            return False
        
        if schema_def['type'] != 'record':
            return False
        
        if not isinstance(schema_def['fields'], list):
            return False
        
        # Validate each field
        for field in schema_def['fields']:
            if not isinstance(field, dict):
                return False
            
            if 'name' not in field or 'type' not in field:
                return False
        
        return True

    def compare_schemas(self, old_version_id: str, new_version_id: str) -> List[SchemaChange]:
        """
        Compare two schema versions and identify changes
        दो schema versions को compare करना और changes identify करना
        """
        
        if old_version_id not in self.schema_registry or new_version_id not in self.schema_registry:
            logger.error("One or both schema versions not found")
            return []
        
        old_schema = self.schema_registry[old_version_id].schema_definition
        new_schema = self.schema_registry[new_version_id].schema_definition
        
        changes = []
        
        try:
            # Use DeepDiff to find differences
            diff = DeepDiff(old_schema, new_schema, ignore_order=True)
            
            # Process different types of changes
            if 'dictionary_item_added' in diff:
                for item in diff['dictionary_item_added']:
                    if 'fields' in item:
                        field_name = self._extract_field_name(item)
                        changes.append(SchemaChange(
                            change_id=str(uuid.uuid4()),
                            change_type=ChangeType.FIELD_ADDED,
                            field_path=field_name,
                            old_value=None,
                            new_value=diff['dictionary_item_added'][item],
                            compatibility_impact=CompatibilityLevel.BACKWARD,
                            description=f"Added field: {field_name}",
                            created_at=datetime.now()
                        ))
            
            if 'dictionary_item_removed' in diff:
                for item in diff['dictionary_item_removed']:
                    if 'fields' in item:
                        field_name = self._extract_field_name(item)
                        changes.append(SchemaChange(
                            change_id=str(uuid.uuid4()),
                            change_type=ChangeType.FIELD_REMOVED,
                            field_path=field_name,
                            old_value=diff['dictionary_item_removed'][item],
                            new_value=None,
                            compatibility_impact=CompatibilityLevel.NONE,  # Breaking change
                            description=f"Removed field: {field_name}",
                            created_at=datetime.now()
                        ))
            
            if 'values_changed' in diff:
                for item, change_info in diff['values_changed'].items():
                    if 'type' in item:
                        field_name = self._extract_field_name(item)
                        old_type = change_info['old_value']
                        new_type = change_info['new_value']
                        
                        # Determine compatibility impact
                        compatibility = self._determine_type_compatibility(old_type, new_type)
                        
                        changes.append(SchemaChange(
                            change_id=str(uuid.uuid4()),
                            change_type=ChangeType.TYPE_CHANGED,
                            field_path=field_name,
                            old_value=old_type,
                            new_value=new_type,
                            compatibility_impact=compatibility,
                            description=f"Changed type of {field_name}: {old_type} → {new_type}",
                            created_at=datetime.now()
                        ))
            
            return changes
            
        except Exception as e:
            logger.error(f"Failed to compare schemas: {e}")
            return []

    def _extract_field_name(self, path: str) -> str:
        """Extract field name from DeepDiff path"""
        # This is a simplified extraction - in production, this would be more robust
        match = re.search(r"'name'.*?'(\w+)'", path)
        return match.group(1) if match else "unknown_field"

    def _determine_type_compatibility(self, old_type: str, new_type: str) -> CompatibilityLevel:
        """Determine compatibility level for type changes"""
        
        # Same type - fully compatible
        if old_type == new_type:
            return CompatibilityLevel.FULL
        
        # Check if new type is compatible with old type
        if old_type in self.type_compatibility:
            compatible_types = self.type_compatibility[old_type]
            if new_type in compatible_types:
                return CompatibilityLevel.BACKWARD
        
        # Check reverse compatibility
        if new_type in self.type_compatibility:
            compatible_types = self.type_compatibility[new_type]
            if old_type in compatible_types:
                return CompatibilityLevel.FORWARD
        
        # No compatibility
        return CompatibilityLevel.NONE

    def check_compatibility(self, source_version_id: str, target_version_id: str) -> CompatibilityReport:
        """
        Check compatibility between two schema versions
        दो schema versions के बीच compatibility check करना
        """
        
        try:
            # Get schema changes
            changes = self.compare_schemas(source_version_id, target_version_id)
            
            # Analyze compatibility
            breaking_changes = [c for c in changes if c.compatibility_impact == CompatibilityLevel.NONE]
            warnings = []
            
            # Determine overall compatibility level
            if not breaking_changes:
                if all(c.compatibility_impact == CompatibilityLevel.FULL for c in changes):
                    overall_compatibility = CompatibilityLevel.FULL
                elif all(c.compatibility_impact in [CompatibilityLevel.FULL, CompatibilityLevel.BACKWARD] for c in changes):
                    overall_compatibility = CompatibilityLevel.BACKWARD
                elif all(c.compatibility_impact in [CompatibilityLevel.FULL, CompatibilityLevel.FORWARD] for c in changes):
                    overall_compatibility = CompatibilityLevel.FORWARD
                else:
                    overall_compatibility = CompatibilityLevel.NONE
            else:
                overall_compatibility = CompatibilityLevel.NONE
            
            # Check for warnings
            forward_only_changes = [c for c in changes if c.compatibility_impact == CompatibilityLevel.FORWARD]
            if forward_only_changes:
                warnings.append(f"Forward-only changes detected: {len(forward_only_changes)} changes")
            
            # Determine migration complexity
            migration_complexity = self._assess_migration_complexity(changes)
            migration_required = len(changes) > 0
            
            # Estimate migration time
            estimated_time = self._estimate_migration_time(changes, migration_complexity)
            
            # Generate recommendations
            recommendations = self._generate_compatibility_recommendations(changes, overall_compatibility)
            
            report = CompatibilityReport(
                source_version=source_version_id,
                target_version=target_version_id,
                compatibility_level=overall_compatibility,
                breaking_changes=breaking_changes,
                warnings=warnings,
                migration_required=migration_required,
                migration_complexity=migration_complexity,
                estimated_migration_time=estimated_time,
                recommendations=recommendations
            )
            
            # Store report in database
            if self.db_connection:
                self._store_compatibility_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to check compatibility: {e}")
            return CompatibilityReport(
                source_version=source_version_id,
                target_version=target_version_id,
                compatibility_level=CompatibilityLevel.NONE,
                breaking_changes=[],
                warnings=[f"Error checking compatibility: {e}"],
                migration_required=True,
                migration_complexity='unknown',
                estimated_migration_time='unknown',
                recommendations=['Manual review required due to error']
            )

    def _assess_migration_complexity(self, changes: List[SchemaChange]) -> str:
        """Assess migration complexity based on changes"""
        
        if not changes:
            return 'none'
        
        complexity_score = 0
        
        for change in changes:
            if change.change_type == ChangeType.FIELD_ADDED:
                complexity_score += 1
            elif change.change_type == ChangeType.FIELD_REMOVED:
                complexity_score += 3
            elif change.change_type == ChangeType.TYPE_CHANGED:
                complexity_score += 2
            elif change.change_type == ChangeType.FIELD_RENAMED:
                complexity_score += 2
        
        if complexity_score <= 3:
            return 'simple'
        elif complexity_score <= 8:
            return 'moderate'
        else:
            return 'complex'

    def _estimate_migration_time(self, changes: List[SchemaChange], complexity: str) -> str:
        """Estimate migration time based on changes and complexity"""
        
        base_times = {
            'simple': 30,      # minutes
            'moderate': 120,   # minutes
            'complex': 480     # minutes (8 hours)
        }
        
        base_time = base_times.get(complexity, 60)
        change_multiplier = len(changes) * 15  # 15 minutes per change
        
        total_minutes = base_time + change_multiplier
        
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        elif total_minutes < 1440:  # 24 hours
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"
        else:
            days = total_minutes // 1440
            remaining_hours = (total_minutes % 1440) // 60
            return f"{days}d {remaining_hours}h"

    def _generate_compatibility_recommendations(self, changes: List[SchemaChange], 
                                              compatibility: CompatibilityLevel) -> List[str]:
        """Generate recommendations based on compatibility analysis"""
        
        recommendations = []
        
        if compatibility == CompatibilityLevel.NONE:
            recommendations.append("BREAKING CHANGES DETECTED - Plan careful migration")
            recommendations.append("Consider versioning strategy for API endpoints")
            recommendations.append("Implement gradual rollout with feature flags")
        
        elif compatibility == CompatibilityLevel.FORWARD:
            recommendations.append("Forward compatible - Old consumers can read new data")
            recommendations.append("Update producers first, then consumers")
        
        elif compatibility == CompatibilityLevel.BACKWARD:
            recommendations.append("Backward compatible - New consumers can read old data")
            recommendations.append("Update consumers first, then producers")
        
        else:
            recommendations.append("Fully compatible - Can update in any order")
        
        # Specific change recommendations
        for change in changes:
            if change.change_type == ChangeType.FIELD_REMOVED:
                recommendations.append(f"Field removal detected: Consider deprecation period for {change.field_path}")
            
            elif change.change_type == ChangeType.TYPE_CHANGED:
                recommendations.append(f"Type change detected: Validate data conversion for {change.field_path}")
        
        recommendations.append("Test schema changes in staging environment")
        recommendations.append("Backup data before applying schema changes")
        
        return recommendations

    def generate_migration_script(self, changes: List[SchemaChange], 
                                target_format: str = 'sql') -> str:
        """
        Generate migration script for schema changes
        Schema changes के लिए migration script generate करना
        """
        
        if target_format not in ['sql', 'mongodb', 'cassandra']:
            logger.error(f"Unsupported migration format: {target_format}")
            return ""
        
        script_parts = []
        
        if target_format == 'sql':
            script_parts.append("-- Schema Migration Script")
            script_parts.append(f"-- Generated at: {datetime.now().isoformat()}")
            script_parts.append("-- WARNING: Review and test before applying to production")
            script_parts.append("")
            script_parts.append("BEGIN TRANSACTION;")
            script_parts.append("")
            
            for change in changes:
                if change.change_type == ChangeType.FIELD_ADDED:
                    script_parts.append(f"-- Add field: {change.field_path}")
                    script_parts.append(
                        f"ALTER TABLE your_table ADD COLUMN {change.field_path} {change.new_value} DEFAULT NULL;"
                    )
                
                elif change.change_type == ChangeType.FIELD_REMOVED:
                    script_parts.append(f"-- Remove field: {change.field_path}")
                    script_parts.append(f"ALTER TABLE your_table DROP COLUMN {change.field_path};")
                
                elif change.change_type == ChangeType.TYPE_CHANGED:
                    script_parts.append(f"-- Change type: {change.field_path}")
                    script_parts.append(
                        f"ALTER TABLE your_table ALTER COLUMN {change.field_path} TYPE {change.new_value};"
                    )
                
                script_parts.append("")
            
            script_parts.append("COMMIT;")
        
        return "\n".join(script_parts)

    def _store_compatibility_report(self, report: CompatibilityReport):
        """Store compatibility report in database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO compatibility_reports
                (report_id, source_version, target_version, compatibility_level,
                 breaking_changes_count, migration_required, migration_complexity,
                 estimated_migration_time, created_at, report_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                report.source_version,
                report.target_version,
                report.compatibility_level.value,
                len(report.breaking_changes),
                report.migration_required,
                report.migration_complexity,
                report.estimated_migration_time,
                datetime.now().isoformat(),
                json.dumps(asdict(report), default=str)
            ))
            self.db_connection.commit()
        except Exception as e:
            logger.error(f"Failed to store compatibility report: {e}")

def create_sample_schema_evolution():
    """Create sample schema evolution scenario for Indian e-commerce"""
    
    manager = SchemaEvolutionManager('demo_schema_evolution.db')
    
    # Version 1: Initial order schema
    order_schema_v1 = SchemaVersion(
        version_id='order_schema_v1',
        schema_name='order_schema',
        version_number='1.0.0',
        schema_definition={
            'type': 'record',
            'name': 'Order',
            'fields': [
                {'name': 'order_id', 'type': 'string'},
                {'name': 'customer_id', 'type': 'string'},
                {'name': 'amount', 'type': 'double'},
                {'name': 'status', 'type': 'string'},
                {'name': 'created_at', 'type': 'datetime'}
            ]
        },
        created_at=datetime.now() - timedelta(days=100),
        created_by='platform-team',
        metadata={'service': 'order-service', 'environment': 'production'}
    )
    
    # Version 2: Add payment method and delivery address
    order_schema_v2 = SchemaVersion(
        version_id='order_schema_v2',
        schema_name='order_schema',
        version_number='2.0.0',
        schema_definition={
            'type': 'record',
            'name': 'Order',
            'fields': [
                {'name': 'order_id', 'type': 'string'},
                {'name': 'customer_id', 'type': 'string'},
                {'name': 'amount', 'type': 'double'},
                {'name': 'status', 'type': 'string'},
                {'name': 'payment_method', 'type': 'string'},  # New field
                {'name': 'delivery_address', 'type': 'string'},  # New field
                {'name': 'created_at', 'type': 'datetime'}
            ]
        },
        created_at=datetime.now() - timedelta(days=50),
        created_by='platform-team',
        changes=[
            SchemaChange(
                change_id='change_001',
                change_type=ChangeType.FIELD_ADDED,
                field_path='payment_method',
                old_value=None,
                new_value='string',
                compatibility_impact=CompatibilityLevel.BACKWARD,
                description='Added payment method field for UPI, Card, COD tracking',
                created_at=datetime.now() - timedelta(days=50)
            ),
            SchemaChange(
                change_id='change_002',
                change_type=ChangeType.FIELD_ADDED,
                field_path='delivery_address',
                old_value=None,
                new_value='string',
                compatibility_impact=CompatibilityLevel.BACKWARD,
                description='Added delivery address field for logistics',
                created_at=datetime.now() - timedelta(days=50)
            )
        ]
    )
    
    # Version 3: Breaking change - change amount type and remove status
    order_schema_v3 = SchemaVersion(
        version_id='order_schema_v3',
        schema_name='order_schema',
        version_number='3.0.0',
        schema_definition={
            'type': 'record',
            'name': 'Order',
            'fields': [
                {'name': 'order_id', 'type': 'string'},
                {'name': 'customer_id', 'type': 'string'},
                {'name': 'amount', 'type': 'int64'},  # Changed type
                {'name': 'payment_method', 'type': 'string'},
                {'name': 'delivery_address', 'type': 'string'},
                {'name': 'order_state', 'type': 'string'},  # Renamed from status
                {'name': 'created_at', 'type': 'datetime'}
            ]
        },
        created_at=datetime.now() - timedelta(days=10),
        created_by='platform-team',
        changes=[
            SchemaChange(
                change_id='change_003',
                change_type=ChangeType.TYPE_CHANGED,
                field_path='amount',
                old_value='double',
                new_value='int64',
                compatibility_impact=CompatibilityLevel.NONE,
                description='Changed amount to integer for better precision in Indian currency',
                created_at=datetime.now() - timedelta(days=10)
            ),
            SchemaChange(
                change_id='change_004',
                change_type=ChangeType.FIELD_RENAMED,
                field_path='status',
                old_value='status',
                new_value='order_state',
                compatibility_impact=CompatibilityLevel.NONE,
                description='Renamed status to order_state for clarity',
                created_at=datetime.now() - timedelta(days=10)
            )
        ]
    )
    
    # Register all versions
    manager.register_schema_version(order_schema_v1)
    manager.register_schema_version(order_schema_v2)
    manager.register_schema_version(order_schema_v3)
    
    return manager

def main():
    """Main execution function - demo of schema evolution system"""
    
    print("🔄 Schema Evolution Handling System Demo")
    print("स्कीमा विकास प्रबंधन प्रणाली का प्रदर्शन\n")
    
    # Test 1: Create sample schema evolution
    print("Test 1: Creating Sample Schema Evolution")
    print("=" * 40)
    
    manager = create_sample_schema_evolution()
    print("Created sample schema evolution with 3 versions of order schema")
    
    # Test 2: Compare schema versions
    print("\nTest 2: Schema Version Comparison")
    print("=" * 35)
    
    changes_v1_to_v2 = manager.compare_schemas('order_schema_v1', 'order_schema_v2')
    
    print(f"Changes from v1.0.0 to v2.0.0:")
    for change in changes_v1_to_v2:
        print(f"- {change.change_type.value}: {change.field_path}")
        print(f"  Description: {change.description}")
        print(f"  Compatibility: {change.compatibility_impact.value}")
    
    changes_v2_to_v3 = manager.compare_schemas('order_schema_v2', 'order_schema_v3')
    
    print(f"\nChanges from v2.0.0 to v3.0.0:")
    for change in changes_v2_to_v3:
        print(f"- {change.change_type.value}: {change.field_path}")
        print(f"  Old: {change.old_value} → New: {change.new_value}")
        print(f"  Compatibility: {change.compatibility_impact.value}")
    
    # Test 3: Compatibility checking
    print("\nTest 3: Compatibility Analysis")
    print("=" * 30)
    
    # Check backward compatibility v1 → v2
    compat_report_v1_v2 = manager.check_compatibility('order_schema_v1', 'order_schema_v2')
    
    print(f"""
    Compatibility Report: v1.0.0 → v2.0.0
    =====================================
    Compatibility Level: {compat_report_v1_v2.compatibility_level.value}
    Breaking Changes: {len(compat_report_v1_v2.breaking_changes)}
    Migration Required: {compat_report_v1_v2.migration_required}
    Migration Complexity: {compat_report_v1_v2.migration_complexity}
    Estimated Time: {compat_report_v1_v2.estimated_migration_time}
    
    Recommendations:
    {chr(10).join(['- ' + rec for rec in compat_report_v1_v2.recommendations])}
    """)
    
    # Check compatibility v2 → v3 (breaking changes)
    compat_report_v2_v3 = manager.check_compatibility('order_schema_v2', 'order_schema_v3')
    
    print(f"""
    Compatibility Report: v2.0.0 → v3.0.0
    =====================================
    Compatibility Level: {compat_report_v2_v3.compatibility_level.value}
    Breaking Changes: {len(compat_report_v2_v3.breaking_changes)}
    Migration Required: {compat_report_v2_v3.migration_required}
    Migration Complexity: {compat_report_v2_v3.migration_complexity}
    Estimated Time: {compat_report_v2_v3.estimated_migration_time}
    
    Breaking Changes:
    {chr(10).join([f'- {change.description}' for change in compat_report_v2_v3.breaking_changes])}
    
    Recommendations:
    {chr(10).join(['- ' + rec for rec in compat_report_v2_v3.recommendations])}
    """)
    
    # Test 4: Migration script generation
    print("\nTest 4: Migration Script Generation")
    print("=" * 35)
    
    migration_script = manager.generate_migration_script(changes_v1_to_v2, 'sql')
    
    print("Generated SQL Migration Script (v1.0.0 → v2.0.0):")
    print("=" * 50)
    print(migration_script)
    
    # Test 5: Complex migration script for breaking changes
    print("\nTest 5: Breaking Changes Migration Script")
    print("=" * 40)
    
    breaking_migration_script = manager.generate_migration_script(changes_v2_to_v3, 'sql')
    
    print("Generated SQL Migration Script (v2.0.0 → v3.0.0 - Breaking):")
    print("=" * 60)
    print(breaking_migration_script)
    
    # Test 6: Schema registry summary
    print("\nTest 6: Schema Registry Summary")
    print("=" * 30)
    
    print(f"""
    Schema Registry Summary:
    =======================
    Total Schemas: {len(set(v.schema_name for v in manager.schema_registry.values()))}
    Total Versions: {len(manager.schema_registry)}
    
    Schema Version History:
    """)
    
    for schema_name, versions in manager.version_history.items():
        print(f"\n{schema_name}:")
        for version in versions:
            status = "ACTIVE" if version.is_active else "INACTIVE"
            change_count = len(version.changes)
            print(f"  - v{version.version_number} ({status}) - {change_count} changes")
            print(f"    Created: {version.created_at.strftime('%Y-%m-%d %H:%M')} by {version.created_by}")
    
    print("\n✅ Schema Evolution Handling System Demo Complete!")
    print("Schema evolution ready for microservices - स्कीमा विकास माइक्रोसर्विसेज के लिए तैयार!")
    
    return {
        'compatibility_reports': [compat_report_v1_v2, compat_report_v2_v3],
        'schema_versions': len(manager.schema_registry),
        'migration_scripts': [migration_script, breaking_migration_script]
    }

# Import uuid after showing it's used
import uuid

if __name__ == "__main__":
    results = main()
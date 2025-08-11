#!/usr/bin/env python3
"""
Episode 13: CDC & Real-Time Data Pipelines
Example 8: Schema Evolution Handling System

यह example schema evolution को gracefully handle करता है।
Production systems में schema changes के साथ backward/forward compatibility।

Author: Distributed Systems Podcast Team
Context: Schema registry, Avro, backward compatibility in Indian tech companies
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
import uuid
from dataclasses import dataclass, field
from enum import Enum
import avro.schema
import avro.io
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import requests
import io
import hashlib

# Hindi logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('schema_evolution.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CompatibilityType(Enum):
    """Schema compatibility types"""
    BACKWARD = "BACKWARD"
    FORWARD = "FORWARD"
    FULL = "FULL"
    NONE = "NONE"

class ChangeType(Enum):
    """Types of schema changes"""
    ADD_FIELD = "ADD_FIELD"
    REMOVE_FIELD = "REMOVE_FIELD"
    RENAME_FIELD = "RENAME_FIELD"
    CHANGE_TYPE = "CHANGE_TYPE"
    ADD_DEFAULT = "ADD_DEFAULT"

@dataclass
class SchemaVersion:
    """Schema version information"""
    version_id: int
    schema_json: str
    compatibility: CompatibilityType
    created_at: datetime
    created_by: str
    description: str
    hash_code: str = field(init=False)
    
    def __post_init__(self):
        self.hash_code = hashlib.sha256(self.schema_json.encode()).hexdigest()[:8]

@dataclass 
class SchemaChange:
    """Individual schema change record"""
    change_id: str
    change_type: ChangeType
    field_name: str
    old_value: Optional[Any]
    new_value: Optional[Any]
    impact_assessment: str
    breaking_change: bool
    migration_required: bool
    created_at: datetime = field(default_factory=datetime.now)

class IndianEcommerceSchemaRegistry:
    """
    Schema Registry for Indian e-commerce platforms
    Flipkart, Myntra जैसे platforms के लिए schema evolution management
    """
    
    def __init__(self, registry_url: str = "http://localhost:8081"):
        self.registry_url = registry_url
        self.session = requests.Session()
        self.local_schemas: Dict[str, List[SchemaVersion]] = {}
        self.compatibility_cache: Dict[str, Dict[str, bool]] = {}
        
        # Indian e-commerce specific schemas
        self.initialize_base_schemas()
        
    def initialize_base_schemas(self):
        """
        Indian e-commerce के लिए base schemas initialize करो
        """
        logger.info("🏗️ Initializing base schemas for Indian e-commerce")
        
        # Flipkart Order Schema V1
        flipkart_order_v1 = {
            "type": "record",
            "name": "FlipkartOrder",
            "namespace": "com.flipkart.orders",
            "fields": [
                {"name": "order_id", "type": "string"},
                {"name": "user_id", "type": "string"},
                {"name": "total_amount", "type": "double"},
                {"name": "currency", "type": "string", "default": "INR"},
                {"name": "order_date", "type": "long"},
                {"name": "status", "type": {"type": "enum", "name": "OrderStatus", 
                                           "symbols": ["PLACED", "CONFIRMED", "SHIPPED", "DELIVERED"]}},
                {"name": "payment_method", "type": {"type": "enum", "name": "PaymentMethod",
                                                   "symbols": ["UPI", "CARD", "COD", "WALLET"]}}
            ]
        }
        
        # UPI Transaction Schema V1
        upi_transaction_v1 = {
            "type": "record", 
            "name": "UPITransaction",
            "namespace": "com.npci.upi",
            "fields": [
                {"name": "transaction_id", "type": "string"},
                {"name": "payer_vpa", "type": "string"},
                {"name": "payee_vpa", "type": "string"},
                {"name": "amount", "type": "double"},
                {"name": "currency", "type": "string", "default": "INR"},
                {"name": "timestamp", "type": "long"},
                {"name": "status", "type": {"type": "enum", "name": "TransactionStatus",
                                            "symbols": ["SUCCESS", "FAILED", "PENDING"]}}
            ]
        }
        
        # Restaurant Order Schema V1 (Zomato/Swiggy)
        restaurant_order_v1 = {
            "type": "record",
            "name": "RestaurantOrder",
            "namespace": "com.zomato.orders",
            "fields": [
                {"name": "order_id", "type": "string"},
                {"name": "restaurant_id", "type": "string"},
                {"name": "customer_id", "type": "string"},
                {"name": "items", "type": {"type": "array", "items": "string"}},
                {"name": "total_price", "type": "double"},
                {"name": "delivery_address", "type": "string"},
                {"name": "order_time", "type": "long"}
            ]
        }
        
        # Register initial schemas
        try:
            self.register_schema("flipkart-orders", json.dumps(flipkart_order_v1), "V1 - Initial order schema")
            self.register_schema("upi-transactions", json.dumps(upi_transaction_v1), "V1 - Initial UPI schema") 
            self.register_schema("restaurant-orders", json.dumps(restaurant_order_v1), "V1 - Initial restaurant order schema")
            
            logger.info("✅ Base schemas initialized successfully")
            
        except Exception as e:
            logger.error(f"💥 Base schema initialization failed: {str(e)}")
            raise
    
    def register_schema(self, subject: str, schema_json: str, description: str) -> SchemaVersion:
        """
        New schema version register करो
        """
        logger.info(f"📝 Registering schema for subject: {subject}")
        
        try:
            # Validate Avro schema
            schema = avro.schema.parse(schema_json)
            
            # Get current version
            current_version = len(self.local_schemas.get(subject, []))
            new_version = current_version + 1
            
            # Check compatibility if not first version
            if current_version > 0:
                compatibility_result = self.check_compatibility(subject, schema_json)
                if not compatibility_result['is_compatible']:
                    raise ValueError(f"Schema compatibility check failed: {compatibility_result['errors']}")
            
            # Create schema version
            schema_version = SchemaVersion(
                version_id=new_version,
                schema_json=schema_json,
                compatibility=CompatibilityType.BACKWARD,  # Default compatibility
                created_at=datetime.now(),
                created_by="schema-admin",
                description=description
            )
            
            # Store locally
            if subject not in self.local_schemas:
                self.local_schemas[subject] = []
            self.local_schemas[subject].append(schema_version)
            
            # Register with remote registry (if available)
            self._register_with_remote_registry(subject, schema_version)
            
            logger.info(f"✅ Schema registered: {subject} v{new_version}")
            return schema_version
            
        except Exception as e:
            logger.error(f"💥 Schema registration failed: {str(e)}")
            raise
    
    def check_compatibility(self, subject: str, new_schema_json: str) -> Dict[str, Any]:
        """
        Schema compatibility check करो - breaking changes detect करो
        """
        logger.info(f"🔍 Checking compatibility for subject: {subject}")
        
        try:
            if subject not in self.local_schemas or not self.local_schemas[subject]:
                return {'is_compatible': True, 'errors': []}
            
            # Get latest schema
            latest_schema_version = self.local_schemas[subject][-1]
            old_schema = avro.schema.parse(latest_schema_version.schema_json)
            new_schema = avro.schema.parse(new_schema_json)
            
            # Analyze changes
            changes = self._analyze_schema_changes(old_schema, new_schema)
            
            # Check compatibility based on changes
            compatibility_result = self._evaluate_compatibility(changes)
            
            logger.info(f"📊 Compatibility check result: {compatibility_result['is_compatible']}")
            
            return compatibility_result
            
        except Exception as e:
            logger.error(f"💥 Compatibility check failed: {str(e)}")
            return {'is_compatible': False, 'errors': [str(e)]}
    
    def _analyze_schema_changes(self, old_schema: avro.schema.Schema, new_schema: avro.schema.Schema) -> List[SchemaChange]:
        """
        Schema changes को analyze करो - detailed change detection
        """
        changes = []
        
        try:
            # Convert schemas to dictionaries for easier comparison
            old_dict = json.loads(str(old_schema))
            new_dict = json.loads(str(new_schema))
            
            # Compare fields
            old_fields = {f['name']: f for f in old_dict.get('fields', [])}
            new_fields = {f['name']: f for f in new_dict.get('fields', [])}
            
            # Check for added fields
            for field_name, field_def in new_fields.items():
                if field_name not in old_fields:
                    # Check if field has default value
                    has_default = 'default' in field_def
                    
                    change = SchemaChange(
                        change_id=str(uuid.uuid4()),
                        change_type=ChangeType.ADD_FIELD,
                        field_name=field_name,
                        old_value=None,
                        new_value=field_def,
                        impact_assessment=f"Field '{field_name}' added" + (" with default" if has_default else " without default"),
                        breaking_change=not has_default,  # Breaking if no default
                        migration_required=not has_default
                    )
                    changes.append(change)
            
            # Check for removed fields
            for field_name, field_def in old_fields.items():
                if field_name not in new_fields:
                    change = SchemaChange(
                        change_id=str(uuid.uuid4()),
                        change_type=ChangeType.REMOVE_FIELD,
                        field_name=field_name,
                        old_value=field_def,
                        new_value=None,
                        impact_assessment=f"Field '{field_name}' removed",
                        breaking_change=True,  # Always breaking
                        migration_required=True
                    )
                    changes.append(change)
            
            # Check for field type changes
            for field_name in old_fields:
                if field_name in new_fields:
                    old_type = old_fields[field_name].get('type')
                    new_type = new_fields[field_name].get('type')
                    
                    if old_type != new_type:
                        is_compatible_change = self._is_type_change_compatible(old_type, new_type)
                        
                        change = SchemaChange(
                            change_id=str(uuid.uuid4()),
                            change_type=ChangeType.CHANGE_TYPE,
                            field_name=field_name,
                            old_value=old_type,
                            new_value=new_type,
                            impact_assessment=f"Field '{field_name}' type changed from {old_type} to {new_type}",
                            breaking_change=not is_compatible_change,
                            migration_required=not is_compatible_change
                        )
                        changes.append(change)
            
            logger.info(f"🔍 Found {len(changes)} schema changes")
            
            return changes
            
        except Exception as e:
            logger.error(f"💥 Schema analysis failed: {str(e)}")
            return []
    
    def _is_type_change_compatible(self, old_type: Any, new_type: Any) -> bool:
        """
        Type change की compatibility check करो
        """
        # Simplified compatibility rules
        compatible_changes = {
            ('int', 'long'),
            ('int', 'float'), 
            ('int', 'double'),
            ('long', 'float'),
            ('long', 'double'),
            ('float', 'double'),
            ('string', 'bytes')  # In some contexts
        }
        
        if isinstance(old_type, str) and isinstance(new_type, str):
            return (old_type, new_type) in compatible_changes
        
        # For complex types, assume incompatible for safety
        return False
    
    def _evaluate_compatibility(self, changes: List[SchemaChange]) -> Dict[str, Any]:
        """
        Changes के based पर compatibility evaluate करो
        """
        breaking_changes = [c for c in changes if c.breaking_change]
        
        if not breaking_changes:
            return {
                'is_compatible': True,
                'compatibility_type': CompatibilityType.FULL.value,
                'errors': [],
                'warnings': [c.impact_assessment for c in changes],
                'migration_required': any(c.migration_required for c in changes)
            }
        else:
            return {
                'is_compatible': False,
                'compatibility_type': CompatibilityType.NONE.value,
                'errors': [c.impact_assessment for c in breaking_changes],
                'warnings': [],
                'migration_required': True
            }
    
    def evolve_schema_safely(self, subject: str, new_schema_json: str, description: str) -> Dict[str, Any]:
        """
        Schema को safely evolve करो - migration plan के साथ
        """
        logger.info(f"🔄 Safely evolving schema for subject: {subject}")
        
        try:
            # Check compatibility first
            compatibility_result = self.check_compatibility(subject, new_schema_json)
            
            if not compatibility_result['is_compatible']:
                # Generate migration plan
                migration_plan = self.generate_migration_plan(subject, new_schema_json)
                
                return {
                    'success': False,
                    'reason': 'Breaking changes detected',
                    'compatibility_result': compatibility_result,
                    'migration_plan': migration_plan
                }
            
            # If compatible, register new version
            new_version = self.register_schema(subject, new_schema_json, description)
            
            return {
                'success': True,
                'new_version': new_version.version_id,
                'hash_code': new_version.hash_code,
                'compatibility_result': compatibility_result
            }
            
        except Exception as e:
            logger.error(f"💥 Schema evolution failed: {str(e)}")
            return {
                'success': False,
                'reason': str(e)
            }
    
    def generate_migration_plan(self, subject: str, new_schema_json: str) -> Dict[str, Any]:
        """
        Breaking changes के लिए migration plan generate करो
        """
        logger.info(f"📋 Generating migration plan for subject: {subject}")
        
        try:
            if subject not in self.local_schemas:
                return {'error': 'Subject not found'}
            
            latest_version = self.local_schemas[subject][-1]
            old_schema = avro.schema.parse(latest_version.schema_json)
            new_schema = avro.schema.parse(new_schema_json)
            
            changes = self._analyze_schema_changes(old_schema, new_schema)
            breaking_changes = [c for c in changes if c.breaking_change]
            
            migration_steps = []
            
            for change in breaking_changes:
                if change.change_type == ChangeType.REMOVE_FIELD:
                    migration_steps.append({
                        'step': len(migration_steps) + 1,
                        'type': 'DATA_MIGRATION',
                        'description': f"Backup data for field '{change.field_name}' before removal",
                        'sql': f"ALTER TABLE backup_table ADD COLUMN {change.field_name}_backup;",
                        'estimated_time': '5-10 minutes',
                        'rollback_plan': f"Restore field '{change.field_name}' from backup"
                    })
                
                elif change.change_type == ChangeType.CHANGE_TYPE:
                    migration_steps.append({
                        'step': len(migration_steps) + 1,
                        'type': 'DATA_TRANSFORMATION',
                        'description': f"Transform '{change.field_name}' from {change.old_value} to {change.new_value}",
                        'transformation_logic': self._generate_transformation_logic(change),
                        'estimated_time': '10-30 minutes',
                        'rollback_plan': f"Revert transformation for field '{change.field_name}'"
                    })
                
                elif change.change_type == ChangeType.ADD_FIELD and change.breaking_change:
                    migration_steps.append({
                        'step': len(migration_steps) + 1,
                        'type': 'SCHEMA_UPDATE',
                        'description': f"Add required field '{change.field_name}' with default value",
                        'action': 'Add default value or make field nullable',
                        'estimated_time': '2-5 minutes',
                        'rollback_plan': f"Remove field '{change.field_name}'"
                    })
            
            # Add deployment steps
            migration_steps.extend([
                {
                    'step': len(migration_steps) + 1,
                    'type': 'DEPLOYMENT',
                    'description': 'Deploy new schema version to staging',
                    'validation': 'Run integration tests with new schema',
                    'estimated_time': '15-30 minutes'
                },
                {
                    'step': len(migration_steps) + 2,
                    'type': 'PRODUCTION_DEPLOYMENT',
                    'description': 'Deploy to production with blue-green deployment',
                    'monitoring': 'Monitor error rates and data quality metrics',
                    'estimated_time': '30-60 minutes'
                }
            ])
            
            total_estimated_time = sum([self._parse_time_estimate(step.get('estimated_time', '5 minutes')) for step in migration_steps])
            
            migration_plan = {
                'subject': subject,
                'current_version': latest_version.version_id,
                'target_schema_hash': hashlib.sha256(new_schema_json.encode()).hexdigest()[:8],
                'breaking_changes_count': len(breaking_changes),
                'migration_steps': migration_steps,
                'total_estimated_time_minutes': total_estimated_time,
                'risk_level': 'HIGH' if len(breaking_changes) > 2 else 'MEDIUM',
                'recommended_approach': 'Blue-green deployment with rollback capability',
                'testing_requirements': [
                    'Unit tests for data transformations',
                    'Integration tests with downstream systems',
                    'Load testing with production data volume',
                    'Rollback testing'
                ]
            }
            
            logger.info(f"📋 Migration plan generated with {len(migration_steps)} steps")
            return migration_plan
            
        except Exception as e:
            logger.error(f"💥 Migration plan generation failed: {str(e)}")
            return {'error': str(e)}
    
    def _generate_transformation_logic(self, change: SchemaChange) -> str:
        """
        Field transformation logic generate करो
        """
        old_type = change.old_value
        new_type = change.new_value
        field_name = change.field_name
        
        if old_type == 'string' and new_type == 'int':
            return f"CAST({field_name} AS INTEGER) -- Ensure string contains valid integer"
        elif old_type == 'int' and new_type == 'string':
            return f"CAST({field_name} AS STRING)"
        elif old_type == 'double' and new_type == 'string':
            return f"CAST({field_name} AS STRING)"
        else:
            return f"-- Custom transformation needed for {field_name}: {old_type} -> {new_type}"
    
    def _parse_time_estimate(self, time_str: str) -> int:
        """
        Time estimate string को minutes में parse करो
        """
        if 'minutes' in time_str:
            # Extract number from "5-10 minutes" -> take average
            parts = time_str.split(' ')[0]
            if '-' in parts:
                min_time, max_time = map(int, parts.split('-'))
                return (min_time + max_time) // 2
            else:
                return int(parts)
        return 10  # Default 10 minutes
    
    def get_schema_evolution_history(self, subject: str) -> Dict[str, Any]:
        """
        Subject का complete evolution history return करो
        """
        if subject not in self.local_schemas:
            return {'error': 'Subject not found'}
        
        versions = self.local_schemas[subject]
        
        history = {
            'subject': subject,
            'total_versions': len(versions),
            'current_version': versions[-1].version_id if versions else 0,
            'versions': [
                {
                    'version': v.version_id,
                    'created_at': v.created_at.isoformat(),
                    'created_by': v.created_by,
                    'description': v.description,
                    'hash_code': v.hash_code,
                    'compatibility': v.compatibility.value
                }
                for v in versions
            ]
        }
        
        return history
    
    def _register_with_remote_registry(self, subject: str, schema_version: SchemaVersion):
        """
        Remote schema registry के साथ sync करो
        """
        try:
            # This would integrate with Confluent Schema Registry or similar
            url = f"{self.registry_url}/subjects/{subject}/versions"
            payload = {
                'schema': schema_version.schema_json,
                'schemaType': 'AVRO'
            }
            
            # In production, you would actually make this call
            logger.info(f"🔄 Would sync with remote registry: {url}")
            
        except Exception as e:
            logger.warning(f"⚠️ Remote registry sync failed: {str(e)}")

class SchemaEvolutionDemo:
    """
    Schema evolution का demo - Indian e-commerce context में
    """
    
    def __init__(self):
        self.registry = IndianEcommerceSchemaRegistry()
    
    def run_demo(self):
        """
        Complete schema evolution demo run करो
        """
        logger.info("🚀 Starting Schema Evolution Demo")
        
        # Demo 1: Compatible schema evolution (adding optional field)
        logger.info("\n📝 Demo 1: Adding optional field (compatible change)")
        self.demo_compatible_evolution()
        
        # Demo 2: Incompatible schema evolution (removing field)
        logger.info("\n⚠️ Demo 2: Removing field (breaking change)")
        self.demo_breaking_evolution()
        
        # Demo 3: Complex evolution with migration plan
        logger.info("\n🔧 Demo 3: Complex evolution with type changes")
        self.demo_complex_evolution()
        
        # Demo 4: Schema history
        logger.info("\n📚 Demo 4: Schema evolution history")
        self.demo_schema_history()
    
    def demo_compatible_evolution(self):
        """
        Compatible schema evolution demo
        """
        try:
            # Evolve Flipkart order schema - add optional delivery_partner field
            flipkart_order_v2 = {
                "type": "record",
                "name": "FlipkartOrder",
                "namespace": "com.flipkart.orders",
                "fields": [
                    {"name": "order_id", "type": "string"},
                    {"name": "user_id", "type": "string"},
                    {"name": "total_amount", "type": "double"},
                    {"name": "currency", "type": "string", "default": "INR"},
                    {"name": "order_date", "type": "long"},
                    {"name": "status", "type": {"type": "enum", "name": "OrderStatus", 
                                               "symbols": ["PLACED", "CONFIRMED", "SHIPPED", "DELIVERED"]}},
                    {"name": "payment_method", "type": {"type": "enum", "name": "PaymentMethod",
                                                       "symbols": ["UPI", "CARD", "COD", "WALLET"]}},
                    # New optional field with default
                    {"name": "delivery_partner", "type": ["null", "string"], "default": None},
                    {"name": "estimated_delivery", "type": ["null", "long"], "default": None}
                ]
            }
            
            result = self.registry.evolve_schema_safely(
                "flipkart-orders",
                json.dumps(flipkart_order_v2),
                "V2 - Added delivery partner tracking"
            )
            
            if result['success']:
                logger.info("✅ Compatible evolution successful")
                logger.info(f"📊 New version: {result['new_version']}")
            else:
                logger.error(f"❌ Evolution failed: {result['reason']}")
                
        except Exception as e:
            logger.error(f"💥 Compatible evolution demo failed: {str(e)}")
    
    def demo_breaking_evolution(self):
        """
        Breaking schema evolution demo
        """
        try:
            # Try to remove required field - this should fail
            upi_transaction_v2_breaking = {
                "type": "record",
                "name": "UPITransaction", 
                "namespace": "com.npci.upi",
                "fields": [
                    {"name": "transaction_id", "type": "string"},
                    {"name": "payer_vpa", "type": "string"},
                    {"name": "payee_vpa", "type": "string"},
                    {"name": "amount", "type": "double"},
                    # Removed currency field - breaking change!
                    {"name": "timestamp", "type": "long"},
                    {"name": "status", "type": {"type": "enum", "name": "TransactionStatus",
                                                "symbols": ["SUCCESS", "FAILED", "PENDING"]}},
                    # Changed field type - breaking change!
                    {"name": "merchant_id", "type": "string"}  # New required field without default
                ]
            }
            
            result = self.registry.evolve_schema_safely(
                "upi-transactions",
                json.dumps(upi_transaction_v2_breaking),
                "V2 - Attempted breaking changes"
            )
            
            if not result['success']:
                logger.warning("⚠️ Breaking evolution correctly rejected")
                logger.info("📋 Migration plan generated:")
                if 'migration_plan' in result:
                    plan = result['migration_plan']
                    logger.info(f"  - Steps: {len(plan.get('migration_steps', []))}")
                    logger.info(f"  - Risk level: {plan.get('risk_level', 'UNKNOWN')}")
                    logger.info(f"  - Estimated time: {plan.get('total_estimated_time_minutes', 0)} minutes")
                    
                    # Show first few migration steps
                    for step in plan.get('migration_steps', [])[:3]:
                        logger.info(f"  Step {step['step']}: {step['description']}")
            else:
                logger.error("❌ Breaking evolution should have been rejected!")
                
        except Exception as e:
            logger.error(f"💥 Breaking evolution demo failed: {str(e)}")
    
    def demo_complex_evolution(self):
        """
        Complex schema evolution with type changes
        """
        try:
            # Restaurant order with complex changes
            restaurant_order_v2_complex = {
                "type": "record",
                "name": "RestaurantOrder",
                "namespace": "com.zomato.orders", 
                "fields": [
                    {"name": "order_id", "type": "string"},
                    {"name": "restaurant_id", "type": "string"},
                    {"name": "customer_id", "type": "string"},
                    # Changed from array of strings to array of records
                    {"name": "items", "type": {
                        "type": "array", 
                        "items": {
                            "type": "record",
                            "name": "OrderItem",
                            "fields": [
                                {"name": "item_id", "type": "string"},
                                {"name": "name", "type": "string"},
                                {"name": "price", "type": "double"},
                                {"name": "quantity", "type": "int"}
                            ]
                        }
                    }},
                    {"name": "total_price", "type": "double"},
                    # Changed from string to structured address
                    {"name": "delivery_address", "type": {
                        "type": "record",
                        "name": "Address",
                        "fields": [
                            {"name": "street", "type": "string"},
                            {"name": "city", "type": "string"},
                            {"name": "pincode", "type": "string"},
                            {"name": "coordinates", "type": ["null", {
                                "type": "record",
                                "name": "Coordinates", 
                                "fields": [
                                    {"name": "lat", "type": "double"},
                                    {"name": "lng", "type": "double"}
                                ]
                            }], "default": None}
                        ]
                    }},
                    {"name": "order_time", "type": "long"},
                    # New tracking fields
                    {"name": "delivery_partner_id", "type": ["null", "string"], "default": None},
                    {"name": "estimated_delivery_time", "type": ["null", "long"], "default": None}
                ]
            }
            
            result = self.registry.evolve_schema_safely(
                "restaurant-orders",
                json.dumps(restaurant_order_v2_complex),
                "V2 - Complex structural changes"
            )
            
            if not result['success']:
                logger.warning("⚠️ Complex evolution requires migration")
                logger.info("🔧 Detailed migration plan available")
                
                if 'migration_plan' in result:
                    plan = result['migration_plan']
                    logger.info(f"📊 Migration complexity: {plan.get('risk_level', 'UNKNOWN')}")
                    logger.info(f"⏱️ Estimated time: {plan.get('total_estimated_time_minutes', 0)} minutes")
                    
                    # Show testing requirements
                    testing_reqs = plan.get('testing_requirements', [])
                    logger.info("🧪 Testing requirements:")
                    for req in testing_reqs[:3]:
                        logger.info(f"  - {req}")
            
        except Exception as e:
            logger.error(f"💥 Complex evolution demo failed: {str(e)}")
    
    def demo_schema_history(self):
        """
        Schema evolution history demo
        """
        try:
            # Get evolution history for all subjects
            subjects = ["flipkart-orders", "upi-transactions", "restaurant-orders"]
            
            for subject in subjects:
                history = self.registry.get_schema_evolution_history(subject)
                
                if 'error' not in history:
                    logger.info(f"📚 {subject} evolution history:")
                    logger.info(f"  - Total versions: {history['total_versions']}")
                    logger.info(f"  - Current version: {history['current_version']}")
                    
                    # Show last few versions
                    for version in history['versions'][-2:]:
                        logger.info(f"  V{version['version']}: {version['description']} ({version['created_at'][:19]})")
                else:
                    logger.warning(f"⚠️ No history found for {subject}")
                    
        except Exception as e:
            logger.error(f"💥 Schema history demo failed: {str(e)}")

def main():
    """Main function for demo"""
    demo = SchemaEvolutionDemo()
    demo.run_demo()
    
    logger.info("✅ Schema Evolution Demo completed")

if __name__ == "__main__":
    main()

"""
Production Implementation Guide:

1. Schema Registry Integration:
   - Confluent Schema Registry or Apache Avro
   - Version control integration (Git hooks)
   - Automated compatibility checking in CI/CD
   - Schema governance policies

2. Migration Automation:
   - Automated data migration scripts
   - Blue-green deployment strategies
   - Rollback capabilities
   - Data validation pipelines

3. Monitoring & Alerting:
   - Schema compatibility metrics
   - Migration success/failure tracking
   - Data quality monitoring post-migration
   - Consumer lag monitoring during evolution

4. Indian Context Considerations:
   - Multi-language field support
   - Regional data compliance
   - Currency and locale handling
   - Timezone evolution considerations

5. Best Practices:
   - Always add default values for new fields
   - Use union types for optional fields
   - Avoid renaming fields (use aliases instead)
   - Document breaking changes thoroughly
   - Test with production data volumes
"""
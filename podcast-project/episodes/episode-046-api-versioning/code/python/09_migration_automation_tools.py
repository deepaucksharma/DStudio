#!/usr/bin/env python3
"""
API Migration Automation Tools
Inspired by Razorpay's automated migration system for merchant APIs

Example: Razorpay ne kaise automate kiya merchant onboarding aur API migration process
"""

import json
import yaml
import requests
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import time
import re
from concurrent.futures import ThreadPoolExecutor
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationStatus(Enum):
    """Migration status tracking"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK_REQUIRED = "rollback_required"
    CANCELLED = "cancelled"

class MigrationPhase(Enum):
    """Migration phases"""
    PREPARATION = "preparation"
    VALIDATION = "validation"
    MIGRATION = "migration"
    TESTING = "testing"
    ROLLBACK = "rollback"
    CLEANUP = "cleanup"

@dataclass
class MigrationTask:
    """Individual migration task"""
    task_id: str
    name: str
    description: str
    phase: MigrationPhase
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 3
    rollback_commands: List[str] = field(default_factory=list)

@dataclass
class MerchantMigration:
    """Merchant API migration configuration"""
    merchant_id: str
    merchant_name: str
    from_version: str
    to_version: str
    scheduled_time: str
    status: MigrationStatus = MigrationStatus.PENDING
    tasks: List[MigrationTask] = field(default_factory=list)
    progress_percentage: float = 0.0
    error_messages: List[str] = field(default_factory=list)
    rollback_plan: Optional[Dict[str, Any]] = None

@dataclass
class MigrationResult:
    """Migration execution result"""
    task_id: str
    success: bool
    duration_seconds: float
    message: str
    details: Optional[Dict[str, Any]] = None

class APISchemaTransformer:
    """
    Transform API requests/responses between versions
    Razorpay style request transformation
    """
    
    def __init__(self):
        self.transformation_rules = self._initialize_transformation_rules()
    
    def _initialize_transformation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize transformation rules between versions"""
        return {
            "v1_to_v2": {
                "payment_request": {
                    "field_mappings": {
                        "amount": "amount_in_paise",  # v2 uses paise instead of rupees
                        "phone": "contact",           # Field renamed
                        "email": "customer.email",   # Nested structure in v2
                        "name": "customer.name"
                    },
                    "transformations": {
                        "amount": lambda x: int(x * 100),  # Convert rupees to paise
                        "currency": lambda x: x.upper()    # Uppercase currency
                    },
                    "new_required_fields": {
                        "callback_url": "https://merchant.com/callback",
                        "method": "netbanking"
                    }
                },
                "payment_response": {
                    "field_mappings": {
                        "status": "payment_status",
                        "txn_id": "transaction_id"
                    },
                    "transformations": {
                        "payment_status": lambda x: x.lower(),  # Lowercase status in v2
                        "amount_in_paise": lambda x: x / 100    # Convert back to rupees for display
                    }
                }
            },
            "v2_to_v3": {
                "payment_request": {
                    "field_mappings": {
                        "customer.email": "customer_details.email",
                        "customer.name": "customer_details.name",
                        "amount_in_paise": "payment.amount"
                    },
                    "new_required_fields": {
                        "payment.currency": "INR",
                        "customer_details.phone": "+91"
                    },
                    "removed_fields": ["method"]  # Removed in v3
                }
            }
        }
    
    def transform_request(self, data: Dict[str, Any], from_version: str, 
                         to_version: str, endpoint: str) -> Dict[str, Any]:
        """Transform request data between versions"""
        rule_key = f"{from_version}_to_{to_version}"
        
        if rule_key not in self.transformation_rules:
            logger.warning(f"No transformation rules found for {rule_key}")
            return data
        
        endpoint_rules = self.transformation_rules[rule_key].get(endpoint, {})
        
        transformed_data = data.copy()
        
        # Apply field mappings
        field_mappings = endpoint_rules.get("field_mappings", {})
        for old_field, new_field in field_mappings.items():
            if old_field in transformed_data:
                value = transformed_data[old_field]
                
                # Handle nested field creation
                if "." in new_field:
                    self._set_nested_field(transformed_data, new_field, value)
                    del transformed_data[old_field]
                else:
                    transformed_data[new_field] = value
                    del transformed_data[old_field]
        
        # Apply transformations
        transformations = endpoint_rules.get("transformations", {})
        for field, transform_func in transformations.items():
            if field in transformed_data:
                try:
                    transformed_data[field] = transform_func(transformed_data[field])
                except Exception as e:
                    logger.error(f"Transformation failed for field {field}: {e}")
        
        # Add new required fields
        new_fields = endpoint_rules.get("new_required_fields", {})
        for field, default_value in new_fields.items():
            if "." in field:
                self._set_nested_field(transformed_data, field, default_value)
            else:
                transformed_data[field] = default_value
        
        # Remove deprecated fields
        removed_fields = endpoint_rules.get("removed_fields", [])
        for field in removed_fields:
            transformed_data.pop(field, None)
        
        return transformed_data
    
    def _set_nested_field(self, data: Dict[str, Any], field_path: str, value: Any):
        """Set nested field in dictionary"""
        keys = field_path.split(".")
        current = data
        
        # Navigate to the parent object
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value

class MigrationOrchestrator:
    """
    Orchestrate automated API migrations for multiple merchants
    Razorpay style batch migration management
    """
    
    def __init__(self):
        self.schema_transformer = APISchemaTransformer()
        self.active_migrations = {}
        self.migration_history = []
        self.test_endpoints = {
            "v1": "https://api-v1.razorpay.com",
            "v2": "https://api-v2.razorpay.com", 
            "v3": "https://api-v3.razorpay.com"
        }
    
    def create_migration_plan(self, merchant_id: str, merchant_name: str,
                            from_version: str, to_version: str) -> MerchantMigration:
        """
        Create comprehensive migration plan for merchant
        """
        tasks = self._generate_migration_tasks(from_version, to_version)
        rollback_plan = self._generate_rollback_plan(from_version, to_version)
        
        migration = MerchantMigration(
            merchant_id=merchant_id,
            merchant_name=merchant_name,
            from_version=from_version,
            to_version=to_version,
            scheduled_time=datetime.now().isoformat(),
            tasks=tasks,
            rollback_plan=rollback_plan
        )
        
        return migration
    
    def _generate_migration_tasks(self, from_version: str, to_version: str) -> List[MigrationTask]:
        """Generate ordered migration tasks"""
        tasks = []
        
        # Phase 1: Preparation
        tasks.extend([
            MigrationTask(
                task_id="prep_backup_config",
                name="Backup Current Configuration",
                description="Create backup of merchant's current API configuration",
                phase=MigrationPhase.PREPARATION,
                rollback_commands=["restore_merchant_config"]
            ),
            MigrationTask(
                task_id="prep_validate_merchant",
                name="Validate Merchant Status",
                description="Verify merchant is eligible for migration",
                phase=MigrationPhase.PREPARATION,
                dependencies=["prep_backup_config"]
            )
        ])
        
        # Phase 2: Validation
        tasks.extend([
            MigrationTask(
                task_id="val_test_connectivity",
                name="Test API Connectivity",
                description=f"Test connectivity to {to_version} endpoints",
                phase=MigrationPhase.VALIDATION,
                dependencies=["prep_validate_merchant"]
            ),
            MigrationTask(
                task_id="val_schema_compatibility",
                name="Validate Schema Compatibility",
                description="Check if current usage is compatible with new version",
                phase=MigrationPhase.VALIDATION,
                dependencies=["val_test_connectivity"]
            )
        ])
        
        # Phase 3: Migration
        tasks.extend([
            MigrationTask(
                task_id="mig_update_endpoints",
                name="Update API Endpoints",
                description=f"Switch endpoints from {from_version} to {to_version}",
                phase=MigrationPhase.MIGRATION,
                dependencies=["val_schema_compatibility"],
                rollback_commands=["revert_endpoints"]
            ),
            MigrationTask(
                task_id="mig_transform_webhooks",
                name="Transform Webhook Configuration",
                description="Update webhook payloads for new version",
                phase=MigrationPhase.MIGRATION,
                dependencies=["mig_update_endpoints"],
                rollback_commands=["revert_webhook_config"]
            )
        ])
        
        # Phase 4: Testing
        tasks.extend([
            MigrationTask(
                task_id="test_payment_flow",
                name="Test Payment Flow",
                description="Execute test payments in new version",
                phase=MigrationPhase.TESTING,
                dependencies=["mig_transform_webhooks"]
            ),
            MigrationTask(
                task_id="test_webhook_delivery",
                name="Test Webhook Delivery",
                description="Verify webhook delivery in new format",
                phase=MigrationPhase.TESTING,
                dependencies=["test_payment_flow"]
            )
        ])
        
        return tasks
    
    def _generate_rollback_plan(self, from_version: str, to_version: str) -> Dict[str, Any]:
        """Generate rollback plan in case of migration failure"""
        return {
            "rollback_version": from_version,
            "rollback_steps": [
                "Stop processing new requests",
                "Revert endpoint URLs",
                "Restore webhook configuration",
                "Verify connectivity to old version",
                "Resume processing",
                "Notify merchant of rollback"
            ],
            "rollback_timeout_minutes": 15,
            "notification_channels": ["email", "sms", "slack"]
        }
    
    async def execute_migration(self, migration: MerchantMigration) -> bool:
        """
        Execute migration for a single merchant
        """
        logger.info(f"Starting migration for {migration.merchant_name} ({migration.merchant_id})")
        
        migration.status = MigrationStatus.IN_PROGRESS
        self.active_migrations[migration.merchant_id] = migration
        
        completed_tasks = 0
        total_tasks = len(migration.tasks)
        
        try:
            # Execute tasks in dependency order
            for task in migration.tasks:
                # Check dependencies
                if not self._are_dependencies_satisfied(task, migration):
                    raise Exception(f"Dependencies not satisfied for task {task.name}")
                
                logger.info(f"Executing task: {task.name}")
                
                result = await self._execute_task(task, migration)
                
                if not result.success:
                    migration.error_messages.append(f"Task {task.name} failed: {result.message}")
                    
                    # Attempt rollback
                    logger.error(f"Task {task.name} failed, initiating rollback")
                    await self._execute_rollback(migration)
                    migration.status = MigrationStatus.ROLLBACK_REQUIRED
                    return False
                
                completed_tasks += 1
                migration.progress_percentage = (completed_tasks / total_tasks) * 100
                
                logger.info(f"Task {task.name} completed. Progress: {migration.progress_percentage:.1f}%")
            
            # All tasks completed successfully
            migration.status = MigrationStatus.COMPLETED
            migration.progress_percentage = 100.0
            
            logger.info(f"Migration completed successfully for {migration.merchant_name}")
            
            # Move to history
            self.migration_history.append(migration)
            del self.active_migrations[migration.merchant_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed for {migration.merchant_name}: {str(e)}")
            migration.error_messages.append(str(e))
            migration.status = MigrationStatus.FAILED
            
            # Attempt rollback
            await self._execute_rollback(migration)
            return False
    
    def _are_dependencies_satisfied(self, task: MigrationTask, 
                                  migration: MerchantMigration) -> bool:
        """Check if task dependencies are satisfied"""
        if not task.dependencies:
            return True
        
        # For this demo, assume dependencies are satisfied
        # In real implementation, track completed tasks
        return True
    
    async def _execute_task(self, task: MigrationTask, 
                          migration: MerchantMigration) -> MigrationResult:
        """Execute a single migration task"""
        start_time = time.time()
        
        try:
            # Simulate task execution based on task type
            if "backup" in task.task_id:
                await self._backup_merchant_config(migration)
            elif "validate" in task.task_id:
                await self._validate_merchant_status(migration)
            elif "connectivity" in task.task_id:
                await self._test_api_connectivity(migration)
            elif "schema" in task.task_id:
                await self._validate_schema_compatibility(migration)
            elif "endpoints" in task.task_id:
                await self._update_api_endpoints(migration)
            elif "webhooks" in task.task_id:
                await self._transform_webhooks(migration)
            elif "payment" in task.task_id:
                await self._test_payment_flow(migration)
            elif "webhook_delivery" in task.task_id:
                await self._test_webhook_delivery(migration)
            
            duration = time.time() - start_time
            
            return MigrationResult(
                task_id=task.task_id,
                success=True,
                duration_seconds=duration,
                message="Task completed successfully"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return MigrationResult(
                task_id=task.task_id,
                success=False,
                duration_seconds=duration,
                message=str(e)
            )
    
    async def _backup_merchant_config(self, migration: MerchantMigration):
        """Backup merchant configuration"""
        await asyncio.sleep(1)  # Simulate backup time
        logger.info(f"Backed up configuration for {migration.merchant_name}")
    
    async def _validate_merchant_status(self, migration: MerchantMigration):
        """Validate merchant is eligible for migration"""
        await asyncio.sleep(0.5)
        
        # Simulate validation logic
        if "test_fail" in migration.merchant_id:
            raise Exception("Merchant has pending KYC verification")
        
        logger.info(f"Merchant {migration.merchant_name} validated for migration")
    
    async def _test_api_connectivity(self, migration: MerchantMigration):
        """Test connectivity to new API version"""
        target_url = self.test_endpoints.get(migration.to_version)
        
        if not target_url:
            raise Exception(f"No endpoint configured for version {migration.to_version}")
        
        # Simulate API call
        await asyncio.sleep(1)
        
        # Mock connectivity test
        if "unreachable" in migration.merchant_id:
            raise Exception(f"Cannot reach {target_url}")
        
        logger.info(f"API connectivity verified for {migration.to_version}")
    
    async def _validate_schema_compatibility(self, migration: MerchantMigration):
        """Check schema compatibility"""
        await asyncio.sleep(1.5)
        
        # Simulate schema validation
        sample_request = {
            "amount": 100.00,
            "phone": "9876543210",
            "email": "customer@example.com",
            "name": "Test Customer"
        }
        
        # Test transformation
        transformed = self.schema_transformer.transform_request(
            sample_request, 
            migration.from_version, 
            migration.to_version,
            "payment_request"
        )
        
        logger.info(f"Schema compatibility verified. Sample transformation: {json.dumps(transformed, indent=2)}")
    
    async def _update_api_endpoints(self, migration: MerchantMigration):
        """Update merchant's API endpoints"""
        await asyncio.sleep(2)
        logger.info(f"Updated API endpoints for {migration.merchant_name}")
    
    async def _transform_webhooks(self, migration: MerchantMigration):
        """Transform webhook configuration"""
        await asyncio.sleep(1)
        logger.info(f"Transformed webhook configuration for {migration.merchant_name}")
    
    async def _test_payment_flow(self, migration: MerchantMigration):
        """Test end-to-end payment flow"""
        await asyncio.sleep(3)  # Payment tests take longer
        
        # Simulate payment test
        test_payment = {
            "amount": 1,  # ₹1 test payment
            "currency": "INR",
            "customer_details": {
                "email": "test@razorpay.com",
                "name": "Test Customer",
                "phone": "+919999999999"
            },
            "payment": {
                "amount": 100,  # 1 rupee in paise
                "currency": "INR"
            }
        }
        
        logger.info(f"Payment flow test completed for {migration.merchant_name}")
    
    async def _test_webhook_delivery(self, migration: MerchantMigration):
        """Test webhook delivery in new format"""
        await asyncio.sleep(2)
        logger.info(f"Webhook delivery test completed for {migration.merchant_name}")
    
    async def _execute_rollback(self, migration: MerchantMigration):
        """Execute rollback plan"""
        logger.warning(f"Executing rollback for {migration.merchant_name}")
        
        rollback_plan = migration.rollback_plan
        if not rollback_plan:
            logger.error("No rollback plan defined")
            return
        
        for step in rollback_plan["rollback_steps"]:
            logger.info(f"Rollback step: {step}")
            await asyncio.sleep(0.5)  # Simulate rollback time
        
        migration.status = MigrationStatus.ROLLBACK_REQUIRED
        logger.info(f"Rollback completed for {migration.merchant_name}")
    
    async def batch_migrate_merchants(self, migrations: List[MerchantMigration], 
                                    max_concurrent: int = 5) -> Dict[str, Any]:
        """
        Execute batch migration for multiple merchants
        """
        logger.info(f"Starting batch migration for {len(migrations)} merchants")
        
        # Execute migrations with concurrency limit
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def migrate_with_semaphore(migration):
            async with semaphore:
                return await self.execute_migration(migration)
        
        # Start all migrations
        tasks = [migrate_with_semaphore(migration) for migration in migrations]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful = sum(1 for r in results if r is True)
        failed = len(results) - successful
        
        return {
            "total_migrations": len(migrations),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / len(migrations)) * 100,
            "migration_details": [
                {
                    "merchant_id": migration.merchant_id,
                    "merchant_name": migration.merchant_name,
                    "status": migration.status.value,
                    "progress": migration.progress_percentage,
                    "errors": migration.error_messages
                }
                for migration in migrations
            ]
        }
    
    def get_migration_status(self, merchant_id: str) -> Optional[Dict[str, Any]]:
        """Get current migration status for merchant"""
        if merchant_id in self.active_migrations:
            migration = self.active_migrations[merchant_id]
            return {
                "merchant_id": migration.merchant_id,
                "status": migration.status.value,
                "progress_percentage": migration.progress_percentage,
                "current_phase": self._get_current_phase(migration),
                "errors": migration.error_messages
            }
        
        # Check migration history
        for migration in self.migration_history:
            if migration.merchant_id == merchant_id:
                return {
                    "merchant_id": migration.merchant_id,
                    "status": migration.status.value,
                    "progress_percentage": migration.progress_percentage,
                    "completed_at": migration.scheduled_time,
                    "errors": migration.error_messages
                }
        
        return None
    
    def _get_current_phase(self, migration: MerchantMigration) -> str:
        """Get current migration phase"""
        completed_tasks = int(migration.progress_percentage / 100 * len(migration.tasks))
        
        if completed_tasks < len(migration.tasks):
            current_task = migration.tasks[completed_tasks]
            return current_task.phase.value
        
        return "completed"

def demonstrate_migration_automation():
    """
    Demonstrate automated migration system with Razorpay examples
    """
    print("🔥 API Migration Automation - Razorpay Style")
    print("=" * 60)
    
    orchestrator = MigrationOrchestrator()
    
    # Create sample merchant migrations
    merchants = [
        {
            "merchant_id": "merchant_001",
            "merchant_name": "Delhi Electronics Store",
            "from_version": "v1",
            "to_version": "v2"
        },
        {
            "merchant_id": "merchant_002", 
            "merchant_name": "Mumbai Fashion Hub",
            "from_version": "v1",
            "to_version": "v3"
        },
        {
            "merchant_id": "merchant_test_fail",
            "merchant_name": "Test Failure Merchant",
            "from_version": "v2",
            "to_version": "v3"
        }
    ]
    
    migrations = []
    
    print("\n📋 Creating Migration Plans...")
    for merchant_data in merchants:
        migration = orchestrator.create_migration_plan(**merchant_data)
        migrations.append(migration)
        
        print(f"\n✅ Migration plan created for {merchant_data['merchant_name']}")
        print(f"   Migration: {merchant_data['from_version']} → {merchant_data['to_version']}")
        print(f"   Total tasks: {len(migration.tasks)}")
        print(f"   Phases: {set(task.phase.value for task in migration.tasks)}")
    
    print("\n🔧 Schema Transformation Example:")
    transformer = APISchemaTransformer()
    
    # Example transformation
    v1_request = {
        "amount": 500.00,
        "phone": "9876543210",
        "email": "customer@example.com",
        "name": "Rajesh Kumar"
    }
    
    v2_request = transformer.transform_request(v1_request, "v1", "v2", "payment_request")
    
    print(f"V1 Request: {json.dumps(v1_request, indent=2)}")
    print(f"V2 Request: {json.dumps(v2_request, indent=2)}")
    
    # Run batch migration (async demo)
    async def run_batch_migration():
        print("\n🚀 Executing Batch Migration...")
        
        results = await orchestrator.batch_migrate_merchants(migrations, max_concurrent=2)
        
        print(f"\n📊 Migration Results:")
        print(f"Total Migrations: {results['total_migrations']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        
        print(f"\n📝 Detailed Results:")
        for detail in results['migration_details']:
            status_icon = "✅" if detail['status'] == 'completed' else "❌" if detail['status'] == 'failed' else "⚠️"
            print(f"{status_icon} {detail['merchant_name']}: {detail['status']} ({detail['progress']:.1f}%)")
            
            if detail['errors']:
                for error in detail['errors']:
                    print(f"      Error: {error}")
    
    # Run the async demo
    import asyncio
    asyncio.run(run_batch_migration())
    
    print("\n💡 Migration Automation Benefits:")
    print("1. Zero-downtime merchant migrations")
    print("2. Automated rollback on failure")
    print("3. Parallel processing for faster completion")
    print("4. Comprehensive validation and testing")
    print("5. Real-time progress tracking")
    
    print("\n🎯 Razorpay Implementation Insights:")
    print("1. Batch processing reduces operational overhead")
    print("2. Schema transformation enables seamless upgrades")
    print("3. Dependency management ensures correct execution order")
    print("4. Automated testing catches issues before production")
    print("5. Rollback capability minimizes merchant impact")

if __name__ == "__main__":
    demonstrate_migration_automation()
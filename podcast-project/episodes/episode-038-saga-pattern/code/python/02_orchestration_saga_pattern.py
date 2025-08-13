#!/usr/bin/env python3
"""
Orchestration Saga Pattern Implementation
========================================

Production-ready orchestration-based saga implementation for distributed transactions.
In orchestration pattern, a central coordinator manages the entire saga workflow.

Mumbai Context: यह Mumbai Railway का Central Control Room जैसा है! सभी trains,
signals, platforms को एक central system coordinate करता है. Orchestrator
सभी services को command करता है और failures को handle करता है.

Real-world usage:
- Complex business workflows
- Multi-step transaction processing  
- Order fulfillment systems
- Financial transaction processing
"""

import time
import threading
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from abc import ABC, abstractmethod
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SagaStepType(Enum):
    """Types of saga steps"""
    SERVICE_CALL = "SERVICE_CALL"
    COMPENSATION = "COMPENSATION"
    DECISION = "DECISION"
    PARALLEL = "PARALLEL"

class SagaStepStatus(Enum):
    """Status of saga steps"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATED = "COMPENSATED"
    SKIPPED = "SKIPPED"

class SagaStatus(Enum):
    """Overall saga status"""
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"

@dataclass
class SagaStep:
    """Definition of a saga step"""
    step_id: str
    step_type: SagaStepType
    service_name: str
    action: str
    compensation_action: Optional[str] = None
    retry_count: int = 3
    timeout_seconds: int = 30
    depends_on: List[str] = None  # Dependencies on other steps
    parallel_group: Optional[str] = None  # For parallel execution

@dataclass
class SagaStepExecution:
    """Runtime execution of a saga step"""
    step_id: str
    status: SagaStepStatus
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_attempts: int = 0

@dataclass
class SagaDefinition:
    """Complete saga definition"""
    saga_name: str
    steps: List[SagaStep]
    description: str = ""
    timeout_seconds: int = 300  # 5 minutes default

@dataclass
class SagaExecution:
    """Runtime saga execution state"""
    saga_id: str
    saga_name: str
    status: SagaStatus
    input_data: Dict[str, Any]
    step_executions: Dict[str, SagaStepExecution]
    started_at: float
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    compensation_steps: List[str] = None

class ServiceInterface(ABC):
    """Interface for services that participate in sagas"""
    
    @abstractmethod
    def execute_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a service action"""
        pass
    
    @abstractmethod
    def compensate_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compensate a previously executed action"""
        pass

class SagaOrchestrator:
    """
    Saga Orchestrator - Central coordinator for saga execution
    
    Mumbai Metaphor: यह Mumbai Railway का Master Control Room है! सभी trains,
    signals, platforms को coordinate करता है. अगर कहीं problem आए तो proper
    recovery और rollback करता है.
    """
    
    def __init__(self, db_path: str = "saga_orchestrator.db"):
        self.services: Dict[str, ServiceInterface] = {}
        self.saga_definitions: Dict[str, SagaDefinition] = {}
        self.active_sagas: Dict[str, SagaExecution] = {}
        self.db_path = db_path
        
        self._init_database()
        self._load_active_sagas()
        
        # Statistics
        self.stats = {
            'sagas_started': 0,
            'sagas_completed': 0,
            'sagas_failed': 0,
            'sagas_compensated': 0,
            'total_steps_executed': 0,
            'total_compensations_executed': 0
        }
        
        logger.info("🎯 Saga Orchestrator initialized")
    
    def _init_database(self):
        """Initialize database for saga persistence"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS saga_executions (
                    saga_id TEXT PRIMARY KEY,
                    saga_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    input_data TEXT,
                    step_executions TEXT,
                    started_at REAL,
                    completed_at REAL,
                    error_message TEXT,
                    compensation_steps TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_saga_status 
                ON saga_executions(status, started_at)
            """)
    
    def _load_active_sagas(self):
        """Load active sagas from database for recovery"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT saga_id, saga_name, status, input_data, step_executions,
                       started_at, completed_at, error_message, compensation_steps
                FROM saga_executions
                WHERE status IN ('STARTED', 'IN_PROGRESS', 'COMPENSATING')
                ORDER BY started_at
            """)
            
            for row in cursor.fetchall():
                (saga_id, saga_name, status, input_data_json, step_executions_json,
                 started_at, completed_at, error_message, compensation_steps_json) = row
                
                try:
                    input_data = json.loads(input_data_json) if input_data_json else {}
                    
                    step_executions = {}
                    if step_executions_json:
                        step_exec_data = json.loads(step_executions_json)
                        for step_id, step_data in step_exec_data.items():
                            step_executions[step_id] = SagaStepExecution(
                                step_id=step_data['step_id'],
                                status=SagaStepStatus(step_data['status']),
                                started_at=step_data.get('started_at'),
                                completed_at=step_data.get('completed_at'),
                                result=step_data.get('result'),
                                error_message=step_data.get('error_message'),
                                retry_attempts=step_data.get('retry_attempts', 0)
                            )
                    
                    compensation_steps = json.loads(compensation_steps_json) if compensation_steps_json else []
                    
                    saga_execution = SagaExecution(
                        saga_id=saga_id,
                        saga_name=saga_name,
                        status=SagaStatus(status),
                        input_data=input_data,
                        step_executions=step_executions,
                        started_at=started_at,
                        completed_at=completed_at,
                        error_message=error_message,
                        compensation_steps=compensation_steps
                    )
                    
                    self.active_sagas[saga_id] = saga_execution
                    logger.info(f"🔄 Recovered active saga: {saga_id} in state {status}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to recover saga {saga_id}: {e}")
    
    def register_service(self, service_name: str, service: ServiceInterface):
        """Register a service with the orchestrator"""
        self.services[service_name] = service
        logger.info(f"📝 Service registered: {service_name}")
    
    def define_saga(self, definition: SagaDefinition):
        """Define a new saga workflow"""
        self.saga_definitions[definition.saga_name] = definition
        logger.info(f"📋 Saga defined: {definition.saga_name} with {len(definition.steps)} steps")
    
    def start_saga(self, saga_name: str, input_data: Dict[str, Any]) -> str:
        """Start a new saga execution"""
        if saga_name not in self.saga_definitions:
            raise ValueError(f"Unknown saga: {saga_name}")
        
        saga_id = f"SAGA_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        definition = self.saga_definitions[saga_name]
        
        # Initialize step executions
        step_executions = {}
        for step in definition.steps:
            step_executions[step.step_id] = SagaStepExecution(
                step_id=step.step_id,
                status=SagaStepStatus.PENDING
            )
        
        # Create saga execution
        saga_execution = SagaExecution(
            saga_id=saga_id,
            saga_name=saga_name,
            status=SagaStatus.STARTED,
            input_data=input_data,
            step_executions=step_executions,
            started_at=time.time(),
            compensation_steps=[]
        )
        
        self.active_sagas[saga_id] = saga_execution
        self.stats['sagas_started'] += 1
        
        # Persist to database
        self._persist_saga(saga_execution)
        
        logger.info(f"🚀 Saga started: {saga_id} ({saga_name})")
        
        # Execute saga asynchronously
        threading.Thread(target=self._execute_saga, args=(saga_id,)).start()
        
        return saga_id
    
    def _execute_saga(self, saga_id: str):
        """Execute the saga workflow"""
        try:
            saga_execution = self.active_sagas[saga_id]
            definition = self.saga_definitions[saga_execution.saga_name]
            
            saga_execution.status = SagaStatus.IN_PROGRESS
            self._persist_saga(saga_execution)
            
            # Execute steps according to dependencies
            completed_steps = set()
            failed_step = None
            
            while len(completed_steps) < len(definition.steps) and not failed_step:
                # Find steps ready to execute
                ready_steps = []
                
                for step in definition.steps:
                    if (step.step_id not in completed_steps and 
                        saga_execution.step_executions[step.step_id].status == SagaStepStatus.PENDING):
                        
                        # Check dependencies
                        if not step.depends_on or all(dep in completed_steps for dep in step.depends_on):
                            ready_steps.append(step)
                
                if not ready_steps:
                    break  # No more steps can be executed
                
                # Execute ready steps (handle parallel execution)
                parallel_groups = {}
                single_steps = []
                
                for step in ready_steps:
                    if step.parallel_group:
                        if step.parallel_group not in parallel_groups:
                            parallel_groups[step.parallel_group] = []
                        parallel_groups[step.parallel_group].append(step)
                    else:
                        single_steps.append(step)
                
                # Execute single steps
                for step in single_steps:
                    success = self._execute_step(saga_execution, step)
                    if success:
                        completed_steps.add(step.step_id)
                    else:
                        failed_step = step
                        break
                
                # Execute parallel groups
                if not failed_step:
                    for group_name, group_steps in parallel_groups.items():
                        group_success = self._execute_parallel_steps(saga_execution, group_steps)
                        if group_success:
                            completed_steps.update(step.step_id for step in group_steps)
                        else:
                            failed_step = group_steps[0]  # Mark first step as failed
                            break
            
            # Check final status
            if failed_step:
                # Saga failed, start compensation
                logger.warning(f"❌ Saga failed at step {failed_step.step_id}: {saga_id}")
                self._compensate_saga(saga_execution)
            else:
                # Saga completed successfully
                saga_execution.status = SagaStatus.COMPLETED
                saga_execution.completed_at = time.time()
                self.stats['sagas_completed'] += 1
                
                logger.info(f"🎉 Saga completed successfully: {saga_id}")
            
            self._persist_saga(saga_execution)
            
        except Exception as e:
            logger.error(f"❌ Saga execution error for {saga_id}: {e}")
            if saga_id in self.active_sagas:
                self.active_sagas[saga_id].status = SagaStatus.FAILED
                self.active_sagas[saga_id].error_message = str(e)
                self.stats['sagas_failed'] += 1
                self._persist_saga(self.active_sagas[saga_id])
    
    def _execute_step(self, saga_execution: SagaExecution, step: SagaStep) -> bool:
        """Execute a single saga step"""
        step_execution = saga_execution.step_executions[step.step_id]
        step_execution.status = SagaStepStatus.IN_PROGRESS
        step_execution.started_at = time.time()
        
        self._persist_saga(saga_execution)
        
        logger.info(f"⚙️ Executing step: {step.step_id} ({step.service_name}.{step.action})")
        
        for attempt in range(step.retry_count + 1):
            try:
                # Get service
                if step.service_name not in self.services:
                    raise Exception(f"Service not found: {step.service_name}")
                
                service = self.services[step.service_name]
                
                # Prepare step input data
                step_input = {
                    'saga_id': saga_execution.saga_id,
                    'step_id': step.step_id,
                    'saga_input': saga_execution.input_data.copy()
                }
                
                # Add results from previous steps
                for other_step_id, other_execution in saga_execution.step_executions.items():
                    if other_execution.status == SagaStepStatus.COMPLETED and other_execution.result:
                        step_input[f'step_{other_step_id}_result'] = other_execution.result
                
                # Execute the action
                result = service.execute_action(step.action, step_input)
                
                # Step completed successfully
                step_execution.status = SagaStepStatus.COMPLETED
                step_execution.completed_at = time.time()
                step_execution.result = result
                step_execution.retry_attempts = attempt
                
                self.stats['total_steps_executed'] += 1
                
                # Add to compensation list if compensation action exists
                if step.compensation_action:
                    saga_execution.compensation_steps.insert(0, step.step_id)  # LIFO order
                
                logger.info(f"✅ Step completed: {step.step_id}")
                self._persist_saga(saga_execution)
                return True
                
            except Exception as e:
                step_execution.retry_attempts = attempt
                step_execution.error_message = str(e)
                
                if attempt < step.retry_count:
                    logger.warning(f"⚠️ Step retry {attempt + 1}/{step.retry_count}: {step.step_id} - {e}")
                    time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                else:
                    # All retries exhausted
                    step_execution.status = SagaStepStatus.FAILED
                    step_execution.completed_at = time.time()
                    
                    logger.error(f"❌ Step failed after {step.retry_count} retries: {step.step_id} - {e}")
                    self._persist_saga(saga_execution)
                    return False
        
        return False
    
    def _execute_parallel_steps(self, saga_execution: SagaExecution, steps: List[SagaStep]) -> bool:
        """Execute multiple steps in parallel"""
        logger.info(f"🔄 Executing {len(steps)} steps in parallel")
        
        results = []
        threads = []
        
        def step_worker(step):
            return self._execute_step(saga_execution, step)
        
        # Start threads
        for step in steps:
            thread = threading.Thread(target=lambda s=step: results.append((s, step_worker(s))))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check if all steps succeeded
        return all(result[1] for result in results)
    
    def _compensate_saga(self, saga_execution: SagaExecution):
        """Execute compensation for failed saga"""
        logger.info(f"🔄 Starting compensation for saga: {saga_execution.saga_id}")
        
        saga_execution.status = SagaStatus.COMPENSATING
        self._persist_saga(saga_execution)
        
        # Execute compensations in reverse order
        for step_id in saga_execution.compensation_steps:
            definition = self.saga_definitions[saga_execution.saga_name]
            step_def = next((s for s in definition.steps if s.step_id == step_id), None)
            
            if not step_def or not step_def.compensation_action:
                continue
            
            step_execution = saga_execution.step_executions[step_id]
            if step_execution.status != SagaStepStatus.COMPLETED:
                continue
            
            logger.info(f"↩️ Compensating step: {step_id} ({step_def.service_name}.{step_def.compensation_action})")
            
            try:
                service = self.services[step_def.service_name]
                
                # Prepare compensation data
                compensation_input = {
                    'saga_id': saga_execution.saga_id,
                    'step_id': step_id,
                    'original_result': step_execution.result,
                    'saga_input': saga_execution.input_data.copy()
                }
                
                # Execute compensation
                result = service.compensate_action(step_def.compensation_action, compensation_input)
                
                step_execution.status = SagaStepStatus.COMPENSATED
                self.stats['total_compensations_executed'] += 1
                
                logger.info(f"✅ Step compensated: {step_id}")
                
            except Exception as e:
                logger.error(f"❌ Compensation failed for step {step_id}: {e}")
                # Continue with other compensations
        
        saga_execution.status = SagaStatus.COMPENSATED
        saga_execution.completed_at = time.time()
        self.stats['sagas_compensated'] += 1
        
        self._persist_saga(saga_execution)
        
        logger.info(f"🔄 Saga compensation completed: {saga_execution.saga_id}")
    
    def _persist_saga(self, saga_execution: SagaExecution):
        """Persist saga state to database"""
        step_executions_json = {}
        for step_id, step_exec in saga_execution.step_executions.items():
            step_executions_json[step_id] = {
                'step_id': step_exec.step_id,
                'status': step_exec.status.value,
                'started_at': step_exec.started_at,
                'completed_at': step_exec.completed_at,
                'result': step_exec.result,
                'error_message': step_exec.error_message,
                'retry_attempts': step_exec.retry_attempts
            }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO saga_executions 
                (saga_id, saga_name, status, input_data, step_executions,
                 started_at, completed_at, error_message, compensation_steps)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                saga_execution.saga_id,
                saga_execution.saga_name,
                saga_execution.status.value,
                json.dumps(saga_execution.input_data),
                json.dumps(step_executions_json),
                saga_execution.started_at,
                saga_execution.completed_at,
                saga_execution.error_message,
                json.dumps(saga_execution.compensation_steps or [])
            ))
    
    def get_saga_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a saga"""
        if saga_id not in self.active_sagas:
            return None
        
        saga_execution = self.active_sagas[saga_id]
        
        step_statuses = {}
        for step_id, step_exec in saga_execution.step_executions.items():
            step_statuses[step_id] = {
                'status': step_exec.status.value,
                'started_at': step_exec.started_at,
                'completed_at': step_exec.completed_at,
                'retry_attempts': step_exec.retry_attempts,
                'error_message': step_exec.error_message
            }
        
        return {
            'saga_id': saga_id,
            'saga_name': saga_execution.saga_name,
            'status': saga_execution.status.value,
            'started_at': saga_execution.started_at,
            'completed_at': saga_execution.completed_at,
            'step_statuses': step_statuses,
            'error_message': saga_execution.error_message
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            **self.stats,
            'active_sagas': len(self.active_sagas),
            'defined_sagas': len(self.saga_definitions),
            'registered_services': len(self.services)
        }

# Mock services for demonstration
class ZomatoOrderService(ServiceInterface):
    """Zomato order service implementation"""
    
    def __init__(self):
        self.orders = {}
    
    def execute_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == "create_order":
            order_id = f"ORD_{int(time.time() * 1000)}"
            
            # Simulate order validation
            items = data['saga_input'].get('items', [])
            if not items:
                raise Exception("No items in order")
            
            order_data = {
                'order_id': order_id,
                'customer_id': data['saga_input'].get('customer_id'),
                'restaurant_id': data['saga_input'].get('restaurant_id'),
                'items': items,
                'total_amount': data['saga_input'].get('total_amount'),
                'status': 'CREATED',
                'created_at': time.time()
            }
            
            self.orders[order_id] = order_data
            logger.info(f"📝 Order created: {order_id}")
            
            return {'order_id': order_id, 'order_data': order_data}
        
        elif action == "confirm_order":
            payment_result = data.get('step_payment_result')
            if not payment_result:
                raise Exception("Payment result not available")
            
            order_result = data.get('step_create_order_result')
            if not order_result:
                raise Exception("Order creation result not available")
            
            order_id = order_result['order_id']
            self.orders[order_id]['status'] = 'CONFIRMED'
            
            logger.info(f"✅ Order confirmed: {order_id}")
            return {'order_id': order_id, 'status': 'CONFIRMED'}
        
        raise ValueError(f"Unknown action: {action}")
    
    def compensate_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == "cancel_order":
            order_result = data.get('original_result')
            if order_result:
                order_id = order_result['order_id']
                if order_id in self.orders:
                    self.orders[order_id]['status'] = 'CANCELLED'
                    logger.info(f"🚫 Order cancelled: {order_id}")
                    return {'order_id': order_id, 'status': 'CANCELLED'}
        
        return {}

class ZomatoPaymentService(ServiceInterface):
    """Zomato payment service implementation"""
    
    def __init__(self):
        self.payments = {}
    
    def execute_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == "process_payment":
            payment_id = f"PAY_{int(time.time() * 1000)}"
            
            customer_id = data['saga_input'].get('customer_id')
            total_amount = data['saga_input'].get('total_amount', 0)
            
            # Simulate payment processing (90% success rate)
            if (hash(data['saga_id']) % 10) < 9:
                payment_data = {
                    'payment_id': payment_id,
                    'customer_id': customer_id,
                    'amount': total_amount,
                    'status': 'COMPLETED',
                    'processed_at': time.time()
                }
                
                self.payments[payment_id] = payment_data
                logger.info(f"💰 Payment processed: {payment_id} - ₹{total_amount:.2f}")
                
                return payment_data
            else:
                raise Exception("Payment failed - insufficient balance")
        
        raise ValueError(f"Unknown action: {action}")
    
    def compensate_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == "refund_payment":
            payment_result = data.get('original_result')
            if payment_result:
                payment_id = payment_result['payment_id']
                amount = payment_result['amount']
                
                refund_id = f"REF_{int(time.time() * 1000)}"
                
                refund_data = {
                    'refund_id': refund_id,
                    'original_payment_id': payment_id,
                    'amount': amount,
                    'status': 'COMPLETED',
                    'processed_at': time.time()
                }
                
                logger.info(f"💸 Payment refunded: {refund_id} - ₹{amount:.2f}")
                return refund_data
        
        return {}

class ZomatoDeliveryService(ServiceInterface):
    """Zomato delivery service implementation"""
    
    def __init__(self):
        self.deliveries = {}
    
    def execute_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == "assign_delivery":
            delivery_id = f"DEL_{int(time.time() * 1000)}"
            
            order_result = data.get('step_create_order_result')
            if not order_result:
                raise Exception("Order data not available")
            
            # Simulate delivery assignment (85% success rate)
            if (hash(data['saga_id']) % 20) < 17:
                delivery_data = {
                    'delivery_id': delivery_id,
                    'order_id': order_result['order_id'],
                    'delivery_partner_id': f"partner_{(hash(data['saga_id']) % 100):03d}",
                    'estimated_time': 25,  # minutes
                    'status': 'ASSIGNED',
                    'assigned_at': time.time()
                }
                
                self.deliveries[delivery_id] = delivery_data
                logger.info(f"🛵 Delivery assigned: {delivery_id}")
                
                return delivery_data
            else:
                raise Exception("No delivery partner available")
        
        raise ValueError(f"Unknown action: {action}")
    
    def compensate_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == "cancel_delivery":
            delivery_result = data.get('original_result')
            if delivery_result:
                delivery_id = delivery_result['delivery_id']
                if delivery_id in self.deliveries:
                    self.deliveries[delivery_id]['status'] = 'CANCELLED'
                    logger.info(f"🚫 Delivery cancelled: {delivery_id}")
                    return {'delivery_id': delivery_id, 'status': 'CANCELLED'}
        
        return {}

class ZomatoNotificationService(ServiceInterface):
    """Zomato notification service implementation"""
    
    def execute_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == "send_confirmation":
            customer_id = data['saga_input'].get('customer_id')
            order_result = data.get('step_create_order_result')
            
            if order_result:
                notification_id = f"NOT_{int(time.time() * 1000)}"
                
                logger.info(f"📱 Confirmation sent to {customer_id}: Order {order_result['order_id']}")
                
                return {
                    'notification_id': notification_id,
                    'customer_id': customer_id,
                    'type': 'order_confirmation',
                    'sent_at': time.time()
                }
            
            raise Exception("Order data not available for notification")
        
        raise ValueError(f"Unknown action: {action}")
    
    def compensate_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        # Notifications don't need compensation
        return {}

def create_zomato_order_saga() -> SagaDefinition:
    """Create Zomato order processing saga definition"""
    
    steps = [
        SagaStep(
            step_id="create_order",
            step_type=SagaStepType.SERVICE_CALL,
            service_name="order_service",
            action="create_order",
            compensation_action="cancel_order",
            retry_count=2
        ),
        
        SagaStep(
            step_id="payment",
            step_type=SagaStepType.SERVICE_CALL,
            service_name="payment_service",
            action="process_payment",
            compensation_action="refund_payment",
            depends_on=["create_order"],
            retry_count=1
        ),
        
        # These two can run in parallel after payment
        SagaStep(
            step_id="delivery",
            step_type=SagaStepType.SERVICE_CALL,
            service_name="delivery_service",
            action="assign_delivery",
            compensation_action="cancel_delivery",
            depends_on=["payment"],
            parallel_group="post_payment",
            retry_count=2
        ),
        
        SagaStep(
            step_id="notification",
            step_type=SagaStepType.SERVICE_CALL,
            service_name="notification_service",
            action="send_confirmation",
            depends_on=["payment"],
            parallel_group="post_payment",
            retry_count=3
        ),
        
        SagaStep(
            step_id="confirm_order",
            step_type=SagaStepType.SERVICE_CALL,
            service_name="order_service",
            action="confirm_order",
            depends_on=["delivery", "notification"]
        )
    ]
    
    return SagaDefinition(
        saga_name="zomato_order_processing",
        description="Complete Zomato order processing workflow",
        steps=steps,
        timeout_seconds=180
    )

def simulate_zomato_orchestration_saga():
    """
    Simulate Zomato order processing using orchestration saga
    
    Mumbai Scenario: Zomato का central system सभी order processing steps को
    orchestrate करता है - order creation, payment, delivery assignment, notifications.
    अगर कोई step fail हो जाए तो proper compensation करता है!
    """
    logger.info("🍽️ Starting Zomato Orchestration Saga simulation...")
    
    # Initialize orchestrator
    orchestrator = SagaOrchestrator()
    
    # Register services
    orchestrator.register_service("order_service", ZomatoOrderService())
    orchestrator.register_service("payment_service", ZomatoPaymentService())
    orchestrator.register_service("delivery_service", ZomatoDeliveryService())
    orchestrator.register_service("notification_service", ZomatoNotificationService())
    
    # Define saga
    saga_definition = create_zomato_order_saga()
    orchestrator.define_saga(saga_definition)
    
    logger.info("🎯 Orchestrator initialized and saga defined")
    
    # Sample orders to process
    sample_orders = [
        {
            'customer_id': 'customer_001',
            'restaurant_id': 'rest_mumbai_001',
            'items': [
                {'item_id': 'butter_chicken', 'name': 'Butter Chicken', 'price': 350.0, 'quantity': 1},
                {'item_id': 'garlic_naan', 'name': 'Garlic Naan', 'price': 80.0, 'quantity': 2}
            ],
            'total_amount': 510.0,
            'delivery_address': 'Bandra West, Mumbai'
        },
        {
            'customer_id': 'customer_002',
            'restaurant_id': 'rest_mumbai_002',
            'items': [
                {'item_id': 'biryani', 'name': 'Chicken Biryani', 'price': 400.0, 'quantity': 2}
            ],
            'total_amount': 800.0,
            'delivery_address': 'Andheri East, Mumbai'
        },
        {
            'customer_id': 'customer_003',
            'restaurant_id': 'rest_mumbai_003',
            'items': [
                {'item_id': 'pizza', 'name': 'Margherita Pizza', 'price': 450.0, 'quantity': 1}
            ],
            'total_amount': 450.0,
            'delivery_address': 'Powai, Mumbai'
        }
    ]
    
    # Start sagas
    saga_ids = []
    for i, order_data in enumerate(sample_orders):
        saga_id = orchestrator.start_saga("zomato_order_processing", order_data)
        saga_ids.append(saga_id)
        
        logger.info(f"🚀 Saga {i+1} started: {saga_id} for {order_data['customer_id']}")
        time.sleep(0.5)  # Small delay between orders
    
    # Wait for sagas to complete
    logger.info("⏳ Waiting for all sagas to complete...")
    time.sleep(8)  # Allow time for execution and potential retries
    
    # Check results
    logger.info("\n📊 Final Saga Results:")
    completed = 0
    failed = 0
    compensated = 0
    
    for saga_id in saga_ids:
        status = orchestrator.get_saga_status(saga_id)
        if status:
            saga_status = status['status']
            customer_id = status.get('saga_input', {}).get('customer_id', 'unknown')
            
            if saga_status == 'COMPLETED':
                completed += 1
                logger.info(f"✅ {saga_id}: COMPLETED - {customer_id}")
            elif saga_status == 'FAILED':
                failed += 1
                logger.info(f"❌ {saga_id}: FAILED - {customer_id}")
            elif saga_status == 'COMPENSATED':
                compensated += 1
                logger.info(f"🔄 {saga_id}: COMPENSATED - {customer_id}")
            else:
                logger.info(f"⏳ {saga_id}: {saga_status} - {customer_id}")
            
            # Show step details for completed/failed sagas
            if saga_status in ['COMPLETED', 'FAILED', 'COMPENSATED']:
                logger.info(f"    Step details:")
                for step_id, step_status in status['step_statuses'].items():
                    logger.info(f"      {step_id}: {step_status['status']}")
    
    # Show final statistics
    stats = orchestrator.get_statistics()
    logger.info(f"\n📈 Orchestration Statistics:")
    logger.info(f"Sagas started: {stats['sagas_started']}")
    logger.info(f"Sagas completed: {stats['sagas_completed']}")
    logger.info(f"Sagas failed: {stats['sagas_failed']}")
    logger.info(f"Sagas compensated: {stats['sagas_compensated']}")
    logger.info(f"Total steps executed: {stats['total_steps_executed']}")
    logger.info(f"Total compensations: {stats['total_compensations_executed']}")
    
    success_rate = (stats['sagas_completed'] / max(1, stats['sagas_started'])) * 100
    logger.info(f"Success rate: {success_rate:.2f}%")

if __name__ == "__main__":
    try:
        simulate_zomato_orchestration_saga()
        logger.info("\n🎊 Zomato Orchestration Saga simulation completed!")
    except KeyboardInterrupt:
        logger.info("\nSimulation interrupted by user")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()
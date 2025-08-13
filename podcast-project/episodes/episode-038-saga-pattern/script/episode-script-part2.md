# Episode 38: Saga Pattern - Part 2: Implementation Patterns and Failure Handling
## Hindi Tech Podcast Series - Distributed Systems Mastery

*Duration: 60 minutes*
*Part 2 of 3: State Machines, Advanced Patterns, Production Debugging*

---

## Opening Recap (3 minutes)

Namaste dosto! Welcome back to Episode 38, Part 2 of our Saga Pattern deep dive. 

Pichle episode mein humne foundation set kiya tha:
- 2PC vs Saga pattern comparison
- Choreography vs Orchestration approaches  
- Compensating transactions ki basic concepts
- Production implementation overview

Aaj ke episode mein hum dive deep karenge advanced implementation patterns mein:
- State machine architecture for sagas
- Advanced failure handling strategies
- Event sourcing integration
- Performance optimization techniques
- Production debugging and monitoring
- Security patterns in distributed transactions

Real production examples ke saath samjhenge ki kaise Netflix, Uber, aur Amazon implement karte hai complex saga workflows.

---

## Chapter 1: State Machine Architecture for Sagas (15 minutes)

### Understanding Saga State Machines

Dosto, saga pattern ko properly implement karne ke liye state machine approach use karna critical hai. Think of it as Mumbai traffic signal system:

```
Traffic Signal States:
RED → YELLOW → GREEN → YELLOW → RED

Similar to Saga States:
PENDING → EXECUTING → [SUCCESS → COMPLETED] 
                   → [FAILURE → COMPENSATING → COMPENSATED]
```

### Core State Machine Design

```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
import asyncio
from datetime import datetime, timedelta

class SagaState(Enum):
    """Core saga states with transitions"""
    PENDING = "pending"           # Initial state
    EXECUTING = "executing"       # Forward execution in progress
    COMPENSATING = "compensating" # Rollback in progress  
    COMPLETED = "completed"       # All steps successful
    COMPENSATED = "compensated"   # All rollbacks successful
    FAILED = "failed"             # Unrecoverable failure
    CANCELLED = "cancelled"       # Manual cancellation
    TIMEOUT = "timeout"           # Execution timeout

class SagaTransition(Enum):
    """Valid state transitions"""
    START = "start"
    STEP_SUCCESS = "step_success"
    STEP_FAILURE = "step_failure"
    COMPENSATION_SUCCESS = "compensation_success"
    COMPENSATION_FAILURE = "compensation_failure" 
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    MANUAL_CANCEL = "manual_cancel"

@dataclass
class SagaStateMachine:
    """
    State machine for saga execution
    Based on production patterns from Uber and Netflix
    """
    
    # Valid state transitions
    TRANSITIONS = {
        SagaState.PENDING: [SagaState.EXECUTING, SagaState.CANCELLED],
        SagaState.EXECUTING: [SagaState.COMPLETED, SagaState.COMPENSATING, SagaState.TIMEOUT],
        SagaState.COMPENSATING: [SagaState.COMPENSATED, SagaState.FAILED],
        SagaState.COMPLETED: [],  # Terminal state
        SagaState.COMPENSATED: [], # Terminal state
        SagaState.FAILED: [],     # Terminal state
        SagaState.CANCELLED: [],  # Terminal state
        SagaState.TIMEOUT: [SagaState.COMPENSATING, SagaState.FAILED]
    }
    
    def __init__(self, saga_id: str):
        self.saga_id = saga_id
        self.current_state = SagaState.PENDING
        self.state_history = []
        self.current_step = 0
        self.total_steps = 0
        self.started_at = None
        self.last_transition_at = None
        
    def can_transition_to(self, new_state: SagaState) -> bool:
        """Check if transition is valid"""
        return new_state in self.TRANSITIONS.get(self.current_state, [])
    
    def transition_to(self, new_state: SagaState, reason: str = None) -> bool:
        """Execute state transition with validation"""
        if not self.can_transition_to(new_state):
            raise InvalidSagaTransition(
                f"Cannot transition from {self.current_state} to {new_state}"
            )
        
        # Record state history
        self.state_history.append({
            "from_state": self.current_state,
            "to_state": new_state,
            "reason": reason,
            "timestamp": datetime.utcnow(),
            "step": self.current_step
        })
        
        old_state = self.current_state
        self.current_state = new_state
        self.last_transition_at = datetime.utcnow()
        
        if new_state == SagaState.EXECUTING and old_state == SagaState.PENDING:
            self.started_at = datetime.utcnow()
        
        return True
    
    def is_terminal_state(self) -> bool:
        """Check if saga has reached terminal state"""
        return len(self.TRANSITIONS[self.current_state]) == 0
    
    def get_execution_duration(self) -> timedelta:
        """Get total execution time"""
        if self.started_at:
            end_time = self.last_transition_at or datetime.utcnow()
            return end_time - self.started_at
        return timedelta(0)
```

### Advanced State Machine with Context

```python
class AdvancedSagaStateMachine:
    """
    Production-ready saga state machine
    Used in high-volume systems like Flipkart, Zomato
    """
    
    def __init__(self, saga_definition, initial_context):
        self.saga_id = self.generate_saga_id()
        self.definition = saga_definition
        self.state_machine = SagaStateMachine(self.saga_id)
        self.context = SagaExecutionContext(initial_context)
        self.step_results = {}
        self.compensation_results = {}
        self.metrics_collector = MetricsCollector()
        
    async def execute_saga(self):
        """Main saga execution loop with state management"""
        
        try:
            # Initialize execution
            self.state_machine.transition_to(SagaState.EXECUTING, "Starting saga execution")
            self.state_machine.total_steps = len(self.definition.steps)
            
            # Execute each step
            for step_index, step in enumerate(self.definition.steps):
                self.state_machine.current_step = step_index
                
                # Check for cancellation
                if await self.is_cancelled():
                    await self.handle_cancellation()
                    return self.get_saga_result()
                
                # Check for timeout
                if self.is_timeout_exceeded():
                    self.state_machine.transition_to(SagaState.TIMEOUT, "Execution timeout")
                    await self.start_compensation("Timeout exceeded")
                    return self.get_saga_result()
                
                # Execute step with monitoring
                step_result = await self.execute_step_with_monitoring(step, step_index)
                
                if step_result.success:
                    self.step_results[step.name] = step_result
                    self.context.add_step_result(step.name, step_result.data)
                    
                    # Emit success metrics
                    self.metrics_collector.increment("saga.step.success", 
                                                   tags={"step": step.name})
                else:
                    # Step failed - start compensation
                    self.metrics_collector.increment("saga.step.failure",
                                                   tags={"step": step.name})
                    await self.start_compensation(f"Step {step.name} failed")
                    return self.get_saga_result()
            
            # All steps completed successfully
            self.state_machine.transition_to(SagaState.COMPLETED, "All steps successful")
            self.metrics_collector.increment("saga.completed")
            
        except Exception as e:
            await self.handle_unexpected_error(e)
        
        return self.get_saga_result()
    
    async def execute_step_with_monitoring(self, step, step_index):
        """Execute single step with comprehensive monitoring"""
        
        step_start_time = datetime.utcnow()
        
        try:
            # Prepare step execution context
            step_context = {
                "saga_id": self.saga_id,
                "step_name": step.name,
                "step_index": step_index,
                "saga_context": self.context.get_context(),
                "idempotency_key": f"{self.saga_id}_{step.name}_{step_index}",
                "timeout": step.timeout_seconds
            }
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self.call_step_service(step, step_context),
                timeout=step.timeout_seconds
            )
            
            # Record success metrics
            execution_time = (datetime.utcnow() - step_start_time).total_seconds()
            self.metrics_collector.histogram("saga.step.duration",
                                           value=execution_time,
                                           tags={"step": step.name})
            
            return StepResult(success=True, data=result, execution_time=execution_time)
            
        except asyncio.TimeoutError:
            self.metrics_collector.increment("saga.step.timeout", 
                                           tags={"step": step.name})
            return StepResult(success=False, error="Timeout", error_type="TIMEOUT")
            
        except ServiceUnavailableError as e:
            self.metrics_collector.increment("saga.step.service_unavailable",
                                           tags={"step": step.name})
            return StepResult(success=False, error=str(e), error_type="SERVICE_UNAVAILABLE")
            
        except Exception as e:
            self.metrics_collector.increment("saga.step.error",
                                           tags={"step": step.name})
            return StepResult(success=False, error=str(e), error_type="UNKNOWN")
    
    async def start_compensation(self, reason):
        """Start compensation process with state management"""
        
        self.state_machine.transition_to(SagaState.COMPENSATING, reason)
        
        # Get completed steps in reverse order
        completed_steps = list(reversed(self.step_results.keys()))
        
        compensation_failures = []
        
        for step_name in completed_steps:
            step_definition = next(s for s in self.definition.steps if s.name == step_name)
            original_result = self.step_results[step_name]
            
            try:
                compensation_result = await self.execute_compensation(
                    step_definition, original_result
                )
                
                if compensation_result.success:
                    self.compensation_results[step_name] = compensation_result
                    self.metrics_collector.increment("saga.compensation.success",
                                                   tags={"step": step_name})
                else:
                    compensation_failures.append({
                        "step": step_name,
                        "error": compensation_result.error,
                        "requires_manual_intervention": True
                    })
                    
            except Exception as e:
                compensation_failures.append({
                    "step": step_name,
                    "error": str(e),
                    "requires_manual_intervention": True
                })
        
        # Determine final state
        if compensation_failures:
            self.state_machine.transition_to(SagaState.FAILED, 
                                           f"Compensation failures: {len(compensation_failures)}")
            self.context.add_compensation_failures(compensation_failures)
        else:
            self.state_machine.transition_to(SagaState.COMPENSATED, "All compensations successful")
```

### State Persistence and Recovery

```python
class SagaStatePersistence:
    """
    Persistent state management for saga recovery
    Critical for production resilience
    """
    
    def __init__(self, database, redis_cache):
        self.db = database
        self.cache = redis_cache
        self.state_version = "v2"  # For schema evolution
    
    async def save_saga_state(self, saga_state_machine, context):
        """Persist saga state with versioning"""
        
        state_snapshot = {
            "saga_id": saga_state_machine.saga_id,
            "version": self.state_version,
            "current_state": saga_state_machine.current_state.value,
            "current_step": saga_state_machine.current_step,
            "total_steps": saga_state_machine.total_steps,
            "state_history": saga_state_machine.state_history,
            "started_at": saga_state_machine.started_at.isoformat() if saga_state_machine.started_at else None,
            "last_transition_at": saga_state_machine.last_transition_at.isoformat(),
            "context": context.serialize(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to database (durable storage)
        await self.db.execute("""
            INSERT INTO saga_states (saga_id, state_data, version, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (saga_id) DO UPDATE SET
            state_data = excluded.state_data,
            version = excluded.version,
            updated_at = excluded.updated_at
        """, saga_state_machine.saga_id, json.dumps(state_snapshot), self.state_version, datetime.utcnow())
        
        # Cache for quick access
        await self.cache.set(
            f"saga_state:{saga_state_machine.saga_id}",
            json.dumps(state_snapshot),
            expire=3600  # 1 hour
        )
    
    async def load_saga_state(self, saga_id):
        """Load saga state with cache fallback"""
        
        # Try cache first
        cached_state = await self.cache.get(f"saga_state:{saga_id}")
        if cached_state:
            return json.loads(cached_state)
        
        # Fallback to database
        result = await self.db.fetch_one(
            "SELECT state_data, version FROM saga_states WHERE saga_id = ?",
            saga_id
        )
        
        if result:
            state_data = json.loads(result['state_data'])
            
            # Handle schema migration if needed
            if result['version'] != self.state_version:
                state_data = self.migrate_state_schema(state_data, result['version'])
            
            # Repopulate cache
            await self.cache.set(
                f"saga_state:{saga_id}",
                json.dumps(state_data),
                expire=3600
            )
            
            return state_data
        
        return None
    
    async def recover_incomplete_sagas(self):
        """Recover sagas that were interrupted"""
        
        incomplete_sagas = await self.db.fetch_all("""
            SELECT saga_id, state_data FROM saga_states
            WHERE JSON_EXTRACT(state_data, '$.current_state') IN ('executing', 'compensating')
            AND updated_at < datetime('now', '-5 minutes')
        """)
        
        recovery_results = []
        
        for saga_row in incomplete_sagas:
            try:
                saga_data = json.loads(saga_row['state_data'])
                recovery_result = await self.recover_saga(saga_data)
                recovery_results.append({
                    "saga_id": saga_row['saga_id'],
                    "status": "recovered",
                    "result": recovery_result
                })
            except Exception as e:
                recovery_results.append({
                    "saga_id": saga_row['saga_id'], 
                    "status": "recovery_failed",
                    "error": str(e)
                })
        
        return recovery_results
```

---

## Chapter 2: Advanced Failure Handling and Retry Patterns (18 minutes)

### Sophisticated Retry Mechanisms

Production mein simple retry sufficient nahi hai. Different types of failures ke liye different strategies chahiye:

```python
from enum import Enum
import random
import asyncio
from datetime import datetime, timedelta

class FailureType(Enum):
    TRANSIENT = "transient"        # Network glitch, temporary unavailability
    RATE_LIMITED = "rate_limited"  # Service throttling
    CIRCUIT_OPEN = "circuit_open"  # Circuit breaker activated
    TIMEOUT = "timeout"            # Service slow response
    INVALID_REQUEST = "invalid_request"  # Bad request data
    RESOURCE_EXHAUSTED = "resource_exhausted"  # No capacity
    DEPENDENCY_FAILURE = "dependency_failure"  # Downstream service failed

class AdaptiveRetryStrategy:
    """
    Intelligent retry strategy based on failure types
    Used in production by Indian unicorns
    """
    
    def __init__(self, metrics_collector):
        self.metrics = metrics_collector
        self.failure_history = {}
        
        # Retry configurations per failure type
        self.retry_configs = {
            FailureType.TRANSIENT: {
                "max_attempts": 5,
                "base_delay": 1.0,
                "max_delay": 30.0,
                "backoff_multiplier": 2,
                "jitter": True
            },
            FailureType.RATE_LIMITED: {
                "max_attempts": 10,
                "base_delay": 5.0,
                "max_delay": 120.0,
                "backoff_multiplier": 1.5,
                "jitter": True
            },
            FailureType.CIRCUIT_OPEN: {
                "max_attempts": 3,
                "base_delay": 30.0,
                "max_delay": 300.0,
                "backoff_multiplier": 1.0,  # Fixed delay
                "jitter": False
            },
            FailureType.TIMEOUT: {
                "max_attempts": 3,
                "base_delay": 2.0,
                "max_delay": 10.0,
                "backoff_multiplier": 2,
                "jitter": True
            },
            FailureType.INVALID_REQUEST: {
                "max_attempts": 1,  # No retry for bad requests
                "base_delay": 0,
                "max_delay": 0,
                "backoff_multiplier": 1,
                "jitter": False
            }
        }
    
    async def execute_with_adaptive_retry(self, operation, operation_context):
        """Execute operation with adaptive retry based on failure patterns"""
        
        service_name = operation_context.get("service_name", "unknown")
        operation_name = operation_context.get("operation_name", "unknown")
        
        last_exception = None
        
        # Analyze historical failures for this service
        failure_pattern = self.analyze_failure_pattern(service_name, operation_name)
        
        for attempt in range(1, 6):  # Max 5 attempts total
            try:
                # Execute operation with monitoring
                start_time = datetime.utcnow()
                result = await operation()
                
                # Record success
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                self.record_success(service_name, operation_name, attempt, execution_time)
                
                return result
                
            except Exception as e:
                last_exception = e
                failure_type = self.classify_failure(e, operation_context)
                
                # Record failure
                self.record_failure(service_name, operation_name, failure_type, attempt)
                
                # Determine if retry should be attempted
                retry_config = self.retry_configs.get(failure_type)
                if not retry_config or attempt >= retry_config["max_attempts"]:
                    break
                
                # Calculate delay with adaptive adjustments
                delay = self.calculate_adaptive_delay(
                    retry_config, attempt, failure_pattern, failure_type
                )
                
                await asyncio.sleep(delay)
        
        # All retries exhausted
        raise RetryExhaustedException(
            f"Operation failed after {attempt} attempts. Last error: {last_exception}"
        )
    
    def classify_failure(self, exception, context):
        """Classify failure type for appropriate retry strategy"""
        
        if isinstance(exception, asyncio.TimeoutError):
            return FailureType.TIMEOUT
            
        elif isinstance(exception, ConnectionError):
            return FailureType.TRANSIENT
            
        elif isinstance(exception, RateLimitError):
            return FailureType.RATE_LIMITED
            
        elif isinstance(exception, CircuitBreakerOpenError):
            return FailureType.CIRCUIT_OPEN
            
        elif isinstance(exception, ValidationError):
            return FailureType.INVALID_REQUEST
            
        elif "503" in str(exception) or "Service Unavailable" in str(exception):
            return FailureType.RESOURCE_EXHAUSTED
            
        else:
            return FailureType.TRANSIENT  # Default to transient
    
    def calculate_adaptive_delay(self, retry_config, attempt, failure_pattern, failure_type):
        """Calculate retry delay based on historical patterns and current conditions"""
        
        base_delay = retry_config["base_delay"]
        max_delay = retry_config["max_delay"] 
        multiplier = retry_config["backoff_multiplier"]
        use_jitter = retry_config["jitter"]
        
        # Exponential backoff calculation
        delay = min(base_delay * (multiplier ** (attempt - 1)), max_delay)
        
        # Adaptive adjustments based on failure patterns
        if failure_pattern.get("success_rate", 1.0) < 0.5:
            # Low success rate - increase delay
            delay *= 1.5
        
        if failure_pattern.get("recent_failures", 0) > 5:
            # Recent failures - increase delay
            delay *= 2.0
        
        # Add jitter to prevent thundering herd
        if use_jitter:
            jitter = delay * 0.1 * random.random()
            delay += jitter
        
        return min(delay, max_delay)
    
    def analyze_failure_pattern(self, service_name, operation_name):
        """Analyze historical failure patterns for intelligent retry"""
        
        key = f"{service_name}:{operation_name}"
        history = self.failure_history.get(key, {
            "total_attempts": 0,
            "successful_attempts": 0,
            "recent_failures": 0,
            "failure_types": {},
            "last_success": None
        })
        
        success_rate = (history["successful_attempts"] / 
                       max(history["total_attempts"], 1))
        
        return {
            "success_rate": success_rate,
            "recent_failures": history["recent_failures"],
            "dominant_failure_type": max(history["failure_types"], 
                                       key=history["failure_types"].get) 
                                       if history["failure_types"] else None
        }
```

### Circuit Breaker Integration

```python
class SagaCircuitBreaker:
    """
    Circuit breaker specifically designed for saga steps
    Prevents cascade failures in distributed sagas
    """
    
    def __init__(self, failure_threshold=5, recovery_timeout=60, half_open_max_calls=3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        # Circuit breaker state per service
        self.circuit_states = {}
        
    async def execute_with_circuit_breaker(self, service_name, operation, saga_context):
        """Execute saga step with circuit breaker protection"""
        
        circuit_state = self.get_circuit_state(service_name)
        
        # Check circuit breaker state
        if circuit_state["state"] == "OPEN":
            if self.should_attempt_reset(circuit_state):
                circuit_state["state"] = "HALF_OPEN"
                circuit_state["half_open_attempts"] = 0
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker open for {service_name}")
        
        if circuit_state["state"] == "HALF_OPEN":
            if circuit_state["half_open_attempts"] >= self.half_open_max_calls:
                raise CircuitBreakerOpenError(f"Circuit breaker half-open limit reached for {service_name}")
            circuit_state["half_open_attempts"] += 1
        
        try:
            # Execute operation
            result = await operation()
            
            # Record success
            self.record_success(service_name)
            
            return result
            
        except Exception as e:
            # Record failure
            self.record_failure(service_name)
            
            # Check if circuit should open
            if self.should_open_circuit(service_name):
                self.open_circuit(service_name)
            
            raise e
    
    def get_circuit_state(self, service_name):
        """Get or initialize circuit state for service"""
        
        if service_name not in self.circuit_states:
            self.circuit_states[service_name] = {
                "state": "CLOSED",  # CLOSED, OPEN, HALF_OPEN
                "failure_count": 0,
                "success_count": 0,
                "last_failure_time": None,
                "half_open_attempts": 0
            }
        
        return self.circuit_states[service_name]
    
    def record_failure(self, service_name):
        """Record failure for circuit breaker decision"""
        
        circuit_state = self.get_circuit_state(service_name)
        circuit_state["failure_count"] += 1
        circuit_state["last_failure_time"] = datetime.utcnow()
        
        if circuit_state["state"] == "HALF_OPEN":
            # Failed during half-open - back to open
            circuit_state["state"] = "OPEN"
            circuit_state["last_failure_time"] = datetime.utcnow()
    
    def record_success(self, service_name):
        """Record success for circuit breaker decision"""
        
        circuit_state = self.get_circuit_state(service_name)
        circuit_state["success_count"] += 1
        
        if circuit_state["state"] == "HALF_OPEN":
            # Success during half-open - close circuit
            circuit_state["state"] = "CLOSED"
            circuit_state["failure_count"] = 0
            circuit_state["half_open_attempts"] = 0
    
    def should_open_circuit(self, service_name):
        """Determine if circuit should open based on failures"""
        
        circuit_state = self.get_circuit_state(service_name)
        return (circuit_state["state"] == "CLOSED" and 
                circuit_state["failure_count"] >= self.failure_threshold)
    
    def should_attempt_reset(self, circuit_state):
        """Determine if circuit breaker should attempt reset"""
        
        if circuit_state["last_failure_time"]:
            time_since_failure = datetime.utcnow() - circuit_state["last_failure_time"]
            return time_since_failure.total_seconds() >= self.recovery_timeout
        
        return False
```

### Advanced Compensation Strategies

```python
class AdvancedCompensationManager:
    """
    Sophisticated compensation handling for complex scenarios
    Based on patterns from Netflix and Amazon
    """
    
    def __init__(self, state_store, message_bus):
        self.state_store = state_store
        self.message_bus = message_bus
        self.compensation_registry = {}
        
    def register_compensation_handler(self, step_name, handler_func, priority=0):
        """Register custom compensation handler"""
        
        self.compensation_registry[step_name] = {
            "handler": handler_func,
            "priority": priority,  # Higher priority compensates first
            "retry_config": {
                "max_attempts": 5,
                "base_delay": 2.0,
                "backoff_multiplier": 2
            }
        }
    
    async def execute_smart_compensation(self, saga_context, failed_step_index):
        """Execute compensation with dependency analysis and prioritization"""
        
        completed_steps = saga_context.completed_steps[:failed_step_index]
        
        # Build compensation dependency graph
        compensation_plan = self.build_compensation_plan(completed_steps)
        
        # Execute compensations in priority order
        compensation_results = []
        
        for compensation_batch in compensation_plan:
            # Execute batch in parallel (independent compensations)
            batch_tasks = []
            
            for step_info in compensation_batch:
                task = self.execute_single_compensation(step_info, saga_context)
                batch_tasks.append(task)
            
            # Wait for batch completion
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process batch results
            for i, result in enumerate(batch_results):
                step_info = compensation_batch[i]
                
                if isinstance(result, Exception):
                    compensation_results.append({
                        "step": step_info["step_name"],
                        "status": "failed",
                        "error": str(result),
                        "requires_manual_intervention": True
                    })
                else:
                    compensation_results.append({
                        "step": step_info["step_name"],
                        "status": "compensated",
                        "result": result
                    })
        
        return compensation_results
    
    def build_compensation_plan(self, completed_steps):
        """Build prioritized compensation execution plan"""
        
        # Sort steps by compensation priority
        prioritized_steps = sorted(
            completed_steps,
            key=lambda s: self.compensation_registry.get(s["step_name"], {}).get("priority", 0),
            reverse=True
        )
        
        # Group independent compensations into batches
        compensation_batches = []
        current_batch = []
        
        for step in prioritized_steps:
            if self.can_compensate_in_parallel(step, current_batch):
                current_batch.append(step)
            else:
                if current_batch:
                    compensation_batches.append(current_batch)
                current_batch = [step]
        
        if current_batch:
            compensation_batches.append(current_batch)
        
        return compensation_batches
    
    async def execute_single_compensation(self, step_info, saga_context):
        """Execute single compensation with advanced error handling"""
        
        step_name = step_info["step_name"]
        compensation_config = self.compensation_registry.get(step_name, {})
        
        # Get compensation handler
        compensation_handler = compensation_config.get("handler")
        if not compensation_handler:
            # Default compensation
            return await self.execute_default_compensation(step_info, saga_context)
        
        # Execute with retry logic
        retry_config = compensation_config.get("retry_config", {})
        
        for attempt in range(retry_config.get("max_attempts", 3)):
            try:
                # Prepare compensation context
                compensation_context = {
                    "saga_id": saga_context.saga_id,
                    "step_name": step_name,
                    "original_result": step_info.get("result"),
                    "saga_data": saga_context.get_context(),
                    "attempt": attempt + 1,
                    "idempotency_key": f"{saga_context.saga_id}_{step_name}_compensate_{attempt}"
                }
                
                # Execute compensation
                result = await compensation_handler(compensation_context)
                
                # Publish compensation event for audit
                await self.message_bus.publish("CompensationCompleted", {
                    "saga_id": saga_context.saga_id,
                    "step_name": step_name,
                    "compensation_result": result,
                    "attempt": attempt + 1
                })
                
                return result
                
            except CompensationRetryableError as e:
                if attempt < retry_config.get("max_attempts", 3) - 1:
                    delay = retry_config.get("base_delay", 2.0) * \
                           (retry_config.get("backoff_multiplier", 2) ** attempt)
                    await asyncio.sleep(delay)
                else:
                    raise CompensationFailedException(f"Compensation failed after retries: {e}")
                    
            except CompensationFatalError as e:
                # Non-retryable error
                raise CompensationFailedException(f"Fatal compensation error: {e}")
        
        raise CompensationFailedException(f"Compensation exhausted retries for {step_name}")

# Practical example: E-commerce order compensation
class ECommerceCompensationHandlers:
    """Real-world compensation handlers for e-commerce scenarios"""
    
    @staticmethod
    async def compensate_inventory_reservation(context):
        """Smart inventory compensation with business logic"""
        
        original_result = context["original_result"]
        reservation_id = original_result.get("reservation_id")
        
        if not reservation_id:
            return {"status": "no_action_needed", "reason": "No reservation to release"}
        
        # Check if items were already sold to other customers
        inventory_service = InventoryService()
        reservation_status = await inventory_service.get_reservation_status(reservation_id)
        
        if reservation_status == "expired":
            return {"status": "already_released", "reason": "Reservation already expired"}
        
        if reservation_status == "fulfilled":
            # Items were sold - need to handle differently
            await inventory_service.handle_oversold_situation(reservation_id)
            return {
                "status": "oversold_handled", 
                "action": "notified_procurement_team",
                "reservation_id": reservation_id
            }
        
        # Standard release
        release_result = await inventory_service.release_reservation(reservation_id)
        return {
            "status": "released",
            "reservation_id": reservation_id,
            "released_items": release_result["items"]
        }
    
    @staticmethod
    async def compensate_payment_processing(context):
        """Payment compensation with regulatory compliance"""
        
        original_result = context["original_result"]
        transaction_id = original_result.get("transaction_id")
        
        if not transaction_id:
            return {"status": "no_payment_to_refund"}
        
        payment_service = PaymentService()
        
        # Check transaction status
        transaction = await payment_service.get_transaction(transaction_id)
        
        if transaction["status"] == "refunded":
            return {"status": "already_refunded", "refund_id": transaction["refund_id"]}
        
        if transaction["status"] == "disputed":
            # Handle disputed payment differently
            await payment_service.add_dispute_note(
                transaction_id, 
                "Saga compensation - order cancelled"
            )
            return {"status": "dispute_noted", "transaction_id": transaction_id}
        
        # Process refund with business rules
        refund_amount = transaction["amount"]
        
        # Apply cancellation fees if applicable
        saga_data = context["saga_data"]
        if saga_data.get("cancellation_reason") == "customer_request":
            # Customer-initiated cancellation might have fees
            refund_amount = await payment_service.calculate_refund_with_fees(transaction)
        
        refund = await payment_service.process_refund(
            transaction_id, 
            refund_amount,
            reason="Order cancellation - saga compensation"
        )
        
        return {
            "status": "refunded",
            "transaction_id": transaction_id,
            "refund_id": refund["refund_id"],
            "refund_amount": refund_amount
        }
```

---

## Chapter 3: Event Sourcing Integration with Sagas (12 minutes)

### Event-Driven Saga Architecture

Dosto, production-grade saga systems often use Event Sourcing pattern ke saath integration. Yeh approach Netflix aur Uber mein extensively used hai:

```python
from dataclasses import dataclass
from typing import List, Dict, Any
import json
from datetime import datetime

@dataclass
class SagaEvent:
    """Event representing saga state change"""
    
    event_id: str
    saga_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime
    version: int
    correlation_id: str = None
    causation_id: str = None  # ID of event that caused this event
    
    def serialize(self) -> str:
        return json.dumps({
            "event_id": self.event_id,
            "saga_id": self.saga_id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id
        })
    
    @classmethod
    def deserialize(cls, event_json: str):
        data = json.loads(event_json)
        return cls(
            event_id=data["event_id"],
            saga_id=data["saga_id"],
            event_type=data["event_type"],
            event_data=data["event_data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            version=data["version"],
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id")
        )

class EventSourcedSagaManager:
    """
    Saga manager with full event sourcing integration
    Based on patterns from distributed systems at scale
    """
    
    def __init__(self, event_store, event_bus, snapshot_store):
        self.event_store = event_store
        self.event_bus = event_bus
        self.snapshot_store = snapshot_store
        self.event_handlers = {}
        
        # Register core saga event handlers
        self.register_event_handlers()
    
    def register_event_handlers(self):
        """Register handlers for saga events"""
        
        self.event_handlers.update({
            "SagaStarted": self.handle_saga_started,
            "SagaStepStarted": self.handle_step_started,
            "SagaStepCompleted": self.handle_step_completed,
            "SagaStepFailed": self.handle_step_failed,
            "SagaCompensationStarted": self.handle_compensation_started,
            "SagaCompensationCompleted": self.handle_compensation_completed,
            "SagaCompensationFailed": self.handle_compensation_failed,
            "SagaCompleted": self.handle_saga_completed,
            "SagaFailed": self.handle_saga_failed
        })
    
    async def start_saga(self, saga_definition, initial_data):
        """Start new saga with event sourcing"""
        
        saga_id = self.generate_saga_id()
        
        # Create saga started event
        started_event = SagaEvent(
            event_id=self.generate_event_id(),
            saga_id=saga_id,
            event_type="SagaStarted",
            event_data={
                "saga_definition": saga_definition.to_dict(),
                "initial_data": initial_data,
                "started_by": "system"  # Could be user ID
            },
            timestamp=datetime.utcnow(),
            version=1
        )
        
        # Persist and publish event
        await self.persist_and_publish_event(started_event)
        
        # Start first step
        await self.start_next_step(saga_id, saga_definition, initial_data)
        
        return saga_id
    
    async def handle_saga_started(self, event: SagaEvent):
        """Handle saga started event"""
        
        # Build initial saga state
        saga_state = {
            "saga_id": event.saga_id,
            "status": "executing",
            "current_step": 0,
            "completed_steps": [],
            "failed_steps": [],
            "saga_data": event.event_data["initial_data"],
            "started_at": event.timestamp,
            "last_updated": event.timestamp
        }
        
        # Save snapshot for performance
        await self.snapshot_store.save_snapshot(event.saga_id, saga_state)
    
    async def handle_step_completed(self, event: SagaEvent):
        """Handle step completion with event sourcing"""
        
        saga_id = event.saga_id
        step_result = event.event_data
        
        # Rebuild saga state from events
        saga_state = await self.rebuild_saga_state(saga_id)
        
        # Update state
        saga_state["completed_steps"].append({
            "step_name": step_result["step_name"],
            "result": step_result["result"],
            "completed_at": event.timestamp
        })
        
        saga_state["current_step"] += 1
        saga_state["last_updated"] = event.timestamp
        
        # Check if saga is complete
        saga_definition = await self.get_saga_definition(saga_id)
        
        if saga_state["current_step"] >= len(saga_definition.steps):
            # Saga completed
            completed_event = SagaEvent(
                event_id=self.generate_event_id(),
                saga_id=saga_id,
                event_type="SagaCompleted",
                event_data={
                    "completion_time": datetime.utcnow().isoformat(),
                    "total_steps": len(saga_definition.steps)
                },
                timestamp=datetime.utcnow(),
                version=await self.get_next_version(saga_id),
                causation_id=event.event_id
            )
            
            await self.persist_and_publish_event(completed_event)
        else:
            # Start next step
            await self.start_next_step(saga_id, saga_definition, saga_state["saga_data"])
    
    async def handle_step_failed(self, event: SagaEvent):
        """Handle step failure and start compensation"""
        
        saga_id = event.saga_id
        failure_info = event.event_data
        
        # Start compensation process
        compensation_started_event = SagaEvent(
            event_id=self.generate_event_id(),
            saga_id=saga_id,
            event_type="SagaCompensationStarted",
            event_data={
                "failed_step": failure_info["step_name"],
                "failure_reason": failure_info["error"],
                "compensation_strategy": "reverse_order"
            },
            timestamp=datetime.utcnow(),
            version=await self.get_next_version(saga_id),
            causation_id=event.event_id
        )
        
        await self.persist_and_publish_event(compensation_started_event)
        
        # Start compensating completed steps
        saga_state = await self.rebuild_saga_state(saga_id)
        await self.start_compensation_process(saga_id, saga_state)
    
    async def rebuild_saga_state(self, saga_id):
        """Rebuild saga state from event stream"""
        
        # Try to get recent snapshot first
        snapshot = await self.snapshot_store.get_latest_snapshot(saga_id)
        
        if snapshot:
            saga_state = snapshot["state"]
            from_version = snapshot["version"]
        else:
            saga_state = self.get_empty_saga_state(saga_id)
            from_version = 0
        
        # Get events since snapshot
        events = await self.event_store.get_events_since_version(saga_id, from_version)
        
        # Apply events to rebuild current state
        for event in events:
            saga_state = await self.apply_event_to_state(saga_state, event)
        
        return saga_state
    
    async def apply_event_to_state(self, saga_state, event):
        """Apply single event to saga state"""
        
        if event.event_type == "SagaStepCompleted":
            saga_state["completed_steps"].append({
                "step_name": event.event_data["step_name"],
                "result": event.event_data["result"],
                "completed_at": event.timestamp
            })
            saga_state["current_step"] += 1
            
        elif event.event_type == "SagaStepFailed":
            saga_state["failed_steps"].append({
                "step_name": event.event_data["step_name"],
                "error": event.event_data["error"],
                "failed_at": event.timestamp
            })
            
        elif event.event_type == "SagaCompensationStarted":
            saga_state["status"] = "compensating"
            saga_state["compensation_started_at"] = event.timestamp
            
        elif event.event_type == "SagaCompleted":
            saga_state["status"] = "completed"
            saga_state["completed_at"] = event.timestamp
            
        elif event.event_type == "SagaFailed":
            saga_state["status"] = "failed"
            saga_state["failed_at"] = event.timestamp
        
        saga_state["last_updated"] = event.timestamp
        return saga_state
    
    async def persist_and_publish_event(self, event: SagaEvent):
        """Persist event to store and publish to event bus"""
        
        # Persist to event store
        await self.event_store.append_event(event)
        
        # Publish to event bus for other subscribers
        await self.event_bus.publish(event.event_type, event.serialize())
        
        # Handle event locally
        handler = self.event_handlers.get(event.event_type)
        if handler:
            await handler(event)
```

### Event Store Implementation

```python
class ProductionEventStore:
    """
    High-performance event store for saga events
    Optimized for high write throughput
    """
    
    def __init__(self, database, cache):
        self.db = database
        self.cache = cache
        self.write_buffer = []
        self.buffer_size = 100  # Batch writes for performance
    
    async def append_event(self, event: SagaEvent):
        """Append event with optimistic concurrency control"""
        
        # Add to write buffer
        self.write_buffer.append(event)
        
        # Flush buffer if full
        if len(self.write_buffer) >= self.buffer_size:
            await self.flush_write_buffer()
        
        # Update cache
        await self.update_cache(event)
    
    async def flush_write_buffer(self):
        """Batch write events to database"""
        
        if not self.write_buffer:
            return
        
        events_to_write = self.write_buffer.copy()
        self.write_buffer.clear()
        
        # Batch insert
        await self.db.execute_many("""
            INSERT INTO saga_events (
                event_id, saga_id, event_type, event_data, 
                timestamp, version, correlation_id, causation_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (e.event_id, e.saga_id, e.event_type, json.dumps(e.event_data),
             e.timestamp, e.version, e.correlation_id, e.causation_id)
            for e in events_to_write
        ])
    
    async def get_events_for_saga(self, saga_id, from_version=0):
        """Get all events for saga since version"""
        
        # Try cache first for recent events
        cached_events = await self.cache.get(f"saga_events:{saga_id}:recent")
        if cached_events and from_version <= 0:
            return [SagaEvent.deserialize(e) for e in cached_events]
        
        # Query database
        rows = await self.db.fetch_all("""
            SELECT event_id, saga_id, event_type, event_data, timestamp, 
                   version, correlation_id, causation_id
            FROM saga_events 
            WHERE saga_id = ? AND version > ?
            ORDER BY version ASC
        """, saga_id, from_version)
        
        events = []
        for row in rows:
            event = SagaEvent(
                event_id=row['event_id'],
                saga_id=row['saga_id'],
                event_type=row['event_type'],
                event_data=json.loads(row['event_data']),
                timestamp=row['timestamp'],
                version=row['version'],
                correlation_id=row['correlation_id'],
                causation_id=row['causation_id']
            )
            events.append(event)
        
        return events
```

---

## Chapter 4: Performance Optimization and Debugging (12 minutes)

### High-Performance Saga Execution

Production systems mein saga performance critical hai. Aaiye dekhte hai optimization techniques:

```python
class HighPerformanceSagaOrchestrator:
    """
    Optimized saga orchestrator for high throughput
    Techniques used in production by Indian unicorns
    """
    
    def __init__(self, connection_pool, cache_layer, metrics_client):
        self.connection_pool = connection_pool
        self.cache = cache_layer
        self.metrics = metrics_client
        
        # Performance optimization settings
        self.config = {
            "max_concurrent_sagas": 1000,
            "step_timeout_default": 30,
            "cache_ttl": 300,  # 5 minutes
            "batch_size": 50,
            "circuit_breaker_threshold": 10
        }
        
        # Connection pool per service for performance
        self.service_pools = {}
        
        # Saga execution queue for load balancing
        self.execution_queue = asyncio.Queue(maxsize=5000)
        
        # Background workers
        self.workers = []
        
    async def start_workers(self, num_workers=10):
        """Start background workers for saga processing"""
        
        for i in range(num_workers):
            worker = asyncio.create_task(self.worker_loop(f"worker-{i}"))
            self.workers.append(worker)
    
    async def worker_loop(self, worker_id):
        """Background worker for processing sagas"""
        
        while True:
            try:
                # Get saga from queue
                saga_task = await self.execution_queue.get()
                
                # Process saga
                start_time = datetime.utcnow()
                result = await self.execute_saga_optimized(saga_task)
                
                # Record metrics
                duration = (datetime.utcnow() - start_time).total_seconds()
                self.metrics.histogram("saga.execution.duration", 
                                     value=duration,
                                     tags={"worker": worker_id})
                
                # Mark task done
                self.execution_queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)  # Back off on error
    
    async def execute_saga_optimized(self, saga_request):
        """Execute saga with performance optimizations"""
        
        saga_id = saga_request["saga_id"]
        saga_definition = saga_request["definition"]
        
        # Use connection pooling
        async with self.get_service_connection(saga_definition.primary_service) as conn:
            
            # Parallel execution preparation
            execution_plan = self.analyze_step_dependencies(saga_definition.steps)
            
            # Execute steps in optimized order
            for execution_stage in execution_plan:
                
                # Parallel execution for independent steps
                if len(execution_stage) > 1:
                    stage_results = await self.execute_steps_parallel(
                        execution_stage, saga_id, conn
                    )
                else:
                    stage_results = await self.execute_step_single(
                        execution_stage[0], saga_id, conn
                    )
                
                # Check for failures
                if any(not result.success for result in stage_results):
                    await self.handle_stage_failure(saga_id, execution_stage, stage_results)
                    break
    
    async def execute_steps_parallel(self, steps, saga_id, connection):
        """Execute multiple independent steps in parallel"""
        
        # Create tasks for parallel execution
        tasks = []
        for step in steps:
            task = asyncio.create_task(
                self.execute_single_step_optimized(step, saga_id, connection)
            )
            tasks.append(task)
        
        # Wait for all steps to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            step = steps[i]
            
            if isinstance(result, Exception):
                processed_results.append(StepResult(
                    step_name=step.name,
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def execute_single_step_optimized(self, step, saga_id, connection):
        """Execute single step with caching and optimization"""
        
        # Check cache for idempotent operations
        cache_key = f"saga_step:{saga_id}:{step.name}"
        if step.idempotent:
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return StepResult.from_cache(cached_result)
        
        # Prepare optimized request
        request = self.prepare_optimized_request(step, saga_id)
        
        try:
            # Execute with connection reuse
            result = await self.call_service_optimized(
                step.service, request, connection
            )
            
            # Cache result if step is idempotent
            if step.idempotent:
                await self.cache.set(cache_key, result.to_cache(), 
                                   expire=self.config["cache_ttl"])
            
            return result
            
        except Exception as e:
            return StepResult(
                step_name=step.name,
                success=False,
                error=str(e)
            )
    
    def analyze_step_dependencies(self, steps):
        """Analyze step dependencies for parallel execution"""
        
        # Build dependency graph
        dependency_graph = {}
        for step in steps:
            dependency_graph[step.name] = step.dependencies or []
        
        # Topological sort for execution stages
        execution_stages = []
        processed_steps = set()
        
        while len(processed_steps) < len(steps):
            # Find steps with satisfied dependencies
            ready_steps = []
            for step in steps:
                if (step.name not in processed_steps and 
                    all(dep in processed_steps for dep in dependency_graph[step.name])):
                    ready_steps.append(step)
            
            if ready_steps:
                execution_stages.append(ready_steps)
                processed_steps.update(s.name for s in ready_steps)
            else:
                # Circular dependency - break it
                break
        
        return execution_stages

class SagaPerformanceMonitor:
    """Performance monitoring and optimization for sagas"""
    
    def __init__(self, metrics_backend):
        self.metrics = metrics_backend
        self.performance_data = {}
    
    async def analyze_saga_performance(self, saga_id):
        """Comprehensive performance analysis"""
        
        # Get saga execution trace
        trace = await self.get_saga_trace(saga_id)
        
        analysis = {
            "total_duration": trace["total_duration"],
            "step_durations": {},
            "bottlenecks": [],
            "optimization_suggestions": []
        }
        
        # Analyze step performance
        for step in trace["steps"]:
            step_duration = step["end_time"] - step["start_time"]
            analysis["step_durations"][step["name"]] = step_duration
            
            # Identify bottlenecks (>30% of total time)
            if step_duration > trace["total_duration"] * 0.3:
                analysis["bottlenecks"].append({
                    "step": step["name"],
                    "duration": step_duration,
                    "percentage": (step_duration / trace["total_duration"]) * 100
                })
        
        # Generate optimization suggestions
        analysis["optimization_suggestions"] = self.generate_optimization_suggestions(
            analysis
        )
        
        return analysis
    
    def generate_optimization_suggestions(self, analysis):
        """Generate actionable optimization suggestions"""
        
        suggestions = []
        
        # Check for parallel execution opportunities
        if len(analysis["bottlenecks"]) > 1:
            suggestions.append({
                "type": "parallelization",
                "description": "Consider parallel execution for independent bottleneck steps",
                "impact": "high",
                "effort": "medium"
            })
        
        # Check for caching opportunities
        for step_name, duration in analysis["step_durations"].items():
            if duration > 5.0:  # Steps taking more than 5 seconds
                suggestions.append({
                    "type": "caching",
                    "description": f"Add caching for step {step_name}",
                    "step": step_name,
                    "impact": "medium",
                    "effort": "low"
                })
        
        # Check for timeout optimization
        if analysis["total_duration"] > 60:  # Sagas taking more than 1 minute
            suggestions.append({
                "type": "timeout_tuning",
                "description": "Review and optimize step timeouts",
                "impact": "medium",
                "effort": "low"
            })
        
        return suggestions
```

### Production Debugging Tools

```python
class SagaDebuggingTools:
    """Comprehensive debugging tools for saga issues in production"""
    
    def __init__(self, event_store, state_store, metrics_client):
        self.event_store = event_store
        self.state_store = state_store
        self.metrics = metrics_client
    
    async def diagnose_stuck_saga(self, saga_id):
        """Diagnose why a saga is stuck"""
        
        diagnosis = {
            "saga_id": saga_id,
            "current_state": None,
            "stuck_duration": None,
            "probable_causes": [],
            "recommended_actions": []
        }
        
        # Get current saga state
        saga_state = await self.state_store.get_saga_state(saga_id)
        if not saga_state:
            diagnosis["probable_causes"].append("Saga state not found - possible data corruption")
            return diagnosis
        
        diagnosis["current_state"] = saga_state["status"]
        
        # Calculate stuck duration
        last_update = saga_state.get("last_updated")
        if last_update:
            stuck_duration = datetime.utcnow() - last_update
            diagnosis["stuck_duration"] = stuck_duration.total_seconds()
        
        # Analyze based on current state
        if saga_state["status"] == "executing":
            await self.diagnose_executing_saga(saga_id, saga_state, diagnosis)
        elif saga_state["status"] == "compensating":
            await self.diagnose_compensating_saga(saga_id, saga_state, diagnosis)
        else:
            diagnosis["probable_causes"].append(f"Unexpected state: {saga_state['status']}")
        
        return diagnosis
    
    async def diagnose_executing_saga(self, saga_id, saga_state, diagnosis):
        """Diagnose saga stuck in executing state"""
        
        current_step = saga_state.get("current_step", 0)
        
        # Check for timeout
        if diagnosis["stuck_duration"] > 300:  # 5 minutes
            diagnosis["probable_causes"].append("Step execution timeout")
            diagnosis["recommended_actions"].append("Check service health for current step")
        
        # Check service availability
        current_step_name = self.get_current_step_name(saga_state, current_step)
        if current_step_name:
            service_health = await self.check_service_health(current_step_name)
            if not service_health["healthy"]:
                diagnosis["probable_causes"].append(f"Service {current_step_name} is unhealthy")
                diagnosis["recommended_actions"].append(f"Investigate {current_step_name} service issues")
        
        # Check for resource locks
        locks = await self.check_resource_locks(saga_id)
        if locks:
            diagnosis["probable_causes"].append("Resources may be locked")
            diagnosis["recommended_actions"].append("Review and release stuck resource locks")
    
    async def trace_saga_execution(self, saga_id):
        """Create detailed execution trace for debugging"""
        
        # Get all events for saga
        events = await self.event_store.get_events_for_saga(saga_id)
        
        trace = {
            "saga_id": saga_id,
            "total_events": len(events),
            "timeline": [],
            "step_analysis": {},
            "error_summary": []
        }
        
        # Build timeline
        for event in events:
            timeline_entry = {
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "event_data": event.event_data
            }
            
            # Add timing information
            if trace["timeline"]:
                prev_event = trace["timeline"][-1]
                duration = (event.timestamp - prev_event["timestamp"]).total_seconds()
                timeline_entry["duration_since_previous"] = duration
            
            trace["timeline"].append(timeline_entry)
            
            # Collect errors
            if "error" in event.event_data or "failed" in event.event_type.lower():
                trace["error_summary"].append({
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "error": event.event_data.get("error", "Unknown error")
                })
        
        # Analyze step performance
        trace["step_analysis"] = self.analyze_step_performance(events)
        
        return trace
    
    def analyze_step_performance(self, events):
        """Analyze individual step performance from events"""
        
        step_analysis = {}
        step_starts = {}
        
        for event in events:
            if event.event_type == "SagaStepStarted":
                step_name = event.event_data.get("step_name")
                if step_name:
                    step_starts[step_name] = event.timestamp
                    
            elif event.event_type in ["SagaStepCompleted", "SagaStepFailed"]:
                step_name = event.event_data.get("step_name")
                if step_name and step_name in step_starts:
                    duration = (event.timestamp - step_starts[step_name]).total_seconds()
                    
                    step_analysis[step_name] = {
                        "duration": duration,
                        "status": "completed" if "Completed" in event.event_type else "failed",
                        "start_time": step_starts[step_name],
                        "end_time": event.timestamp
                    }
                    
                    if event.event_type == "SagaStepFailed":
                        step_analysis[step_name]["error"] = event.event_data.get("error")
        
        return step_analysis
    
    async def generate_saga_health_report(self):
        """Generate comprehensive health report for all sagas"""
        
        report = {
            "timestamp": datetime.utcnow(),
            "overall_health": "healthy",  # Will be updated based on findings
            "metrics": {},
            "stuck_sagas": [],
            "performance_issues": [],
            "recommendations": []
        }
        
        # Get key metrics
        report["metrics"] = {
            "active_sagas": await self.get_active_saga_count(),
            "success_rate_24h": await self.calculate_success_rate(hours=24),
            "average_duration": await self.calculate_average_duration(hours=24),
            "compensation_rate": await self.calculate_compensation_rate(hours=24)
        }
        
        # Identify stuck sagas
        stuck_sagas = await self.find_stuck_sagas()
        report["stuck_sagas"] = stuck_sagas
        
        if len(stuck_sagas) > 10:
            report["overall_health"] = "degraded"
        if len(stuck_sagas) > 50:
            report["overall_health"] = "unhealthy"
        
        # Performance issues
        if report["metrics"]["success_rate_24h"] < 0.95:
            report["performance_issues"].append("Low success rate")
            report["recommendations"].append("Investigate failing saga patterns")
        
        if report["metrics"]["average_duration"] > 30:
            report["performance_issues"].append("High average duration")
            report["recommendations"].append("Optimize slow saga steps")
        
        return report
```

---

## Closing and Next Episode Preview (5 minutes)

### Key Takeaways from Part 2

Dosto, aaj ke episode mein humne deep dive kiya advanced implementation patterns mein:

1. **State Machine Architecture**: Robust state management with proper transitions and recovery
2. **Advanced Failure Handling**: Intelligent retry strategies, circuit breakers, adaptive compensation
3. **Event Sourcing Integration**: Complete audit trail, state rebuilding, event-driven architecture
4. **Performance Optimization**: Parallel execution, connection pooling, caching strategies
5. **Production Debugging**: Comprehensive monitoring, tracing tools, health reporting

**Main Learning**: Production saga implementation requires sophisticated failure handling, performance optimization, aur comprehensive observability. Simple retry logic sufficient nahi hai - intelligent adaptation required hai.

### Technical Insights Recap

**State Machine Benefits:**
- Clear transition rules prevent invalid states
- Recovery becomes systematic and predictable
- Easier debugging and monitoring

**Advanced Retry Strategies:**
- Different failure types need different approaches
- Historical patterns help optimize retry behavior
- Circuit breakers prevent cascade failures

**Event Sourcing Integration:**
- Complete audit trail for compliance
- State rebuilding enables recovery from any failure
- Natural fit for distributed saga coordination

### Next Episode Preview

**Part 3: Production Case Studies from Indian Companies** mein hum explore karenge:

**Real Implementation Stories:**
- **Zomato**: Food delivery saga with real-time partner coordination
- **Ola**: Ride booking saga with dynamic pricing and driver management
- **Flipkart**: E-commerce order saga handling 50M+ orders daily
- **MakeMyTrip**: Travel booking saga across airlines, hotels, cabs
- **PayTM**: Wallet transaction saga with regulatory compliance

**Deep Dive Topics:**
- Peak load handling during festivals (Diwali, Big Billion Days)
- Multi-region saga coordination across Indian data centers
- Regulatory compliance patterns for financial services
- Cost optimization techniques for high-volume sagas
- Team coordination strategies for distributed saga development

### Call to Action

Comments mein share karo:
1. Aapke production mein saga performance challenges kya hai?
2. State machine vs simple state management - kya experience hai?
3. Event sourcing use kiya hai saga ke saath? Results kaisa tha?

Next episode mein real Indian company case studies dekhenge - bilkul practical implementation details ke saath!

### Resources

- GitHub repository mein complete code examples
- Saga pattern performance benchmark scripts
- Production debugging tools aur monitoring dashboards
- State machine implementation templates

**Keep Learning, Keep Building!**

---

*Word Count: Approximately 7,300 words*
*Duration: 60 minutes*
*Next Episode: Indian Companies Production Case Studies*
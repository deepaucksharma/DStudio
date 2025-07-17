# Control Distribution Exercises

!!! info "Prerequisites"
    - Completed [Control Distribution Concepts](index.md)
    - Reviewed [Control Distribution Examples](examples.md)
    - Understanding of control systems

!!! tip "Quick Navigation"
    [← Examples](examples.md) |
    [↑ Pillars Overview](../index.md) |
    [Pillar 5 →](../pillar-5-intelligence/index.md)

## Learning Objectives

By completing these exercises, you will:

1. **Build** autonomous control systems
2. **Implement** hierarchical control structures
3. **Design** feedback control loops
4. **Create** chaos engineering frameworks
5. **Practice** incident response automation

---

## Exercise 1: Build a Self-Healing Service

Create a service that detects and recovers from failures automatically.

### Requirements

1. Health check mechanism
2. Automatic restart on failure
3. Circuit breaker integration
4. Metrics collection
5. Alert suppression during recovery

### Implementation

```python
import asyncio
import time
from enum import Enum
from typing import Optional, Callable
import logging

class ServiceState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RECOVERING = "recovering"

class SelfHealingService:
    def __init__(self, 
                 name: str,
                 health_check: Callable,
                 restart_func: Callable,
                 recovery_timeout: int = 30):
        self.name = name
        self.health_check = health_check
        self.restart_func = restart_func
        self.recovery_timeout = recovery_timeout
        
        self.state = ServiceState.HEALTHY
        self.consecutive_failures = 0
        self.last_restart_time = 0
        self.recovery_attempts = 0
        
    async def monitor(self):
        """Main monitoring loop"""
        while True:
            try:
                # Perform health check
                is_healthy = await self.health_check()
                
                if is_healthy:
                    self.handle_healthy()
                else:
                    await self.handle_unhealthy()
                    
            except Exception as e:
                logging.error(f"Monitor error: {e}")
                await self.handle_unhealthy()
                
            await asyncio.sleep(5)  # Check every 5 seconds
            
    def handle_healthy(self):
        """Handle healthy state"""
        if self.state != ServiceState.HEALTHY:
            logging.info(f"{self.name} recovered")
            self.state = ServiceState.HEALTHY
            self.consecutive_failures = 0
            self.recovery_attempts = 0
            
    async def handle_unhealthy(self):
        """Handle unhealthy state with self-healing"""
        self.consecutive_failures += 1
        
        if self.consecutive_failures >= 3:
            if self.should_attempt_recovery():
                await self.attempt_recovery()
            else:
                self.state = ServiceState.UNHEALTHY
                logging.error(f"{self.name} is unhealthy, manual intervention required")
                
    def should_attempt_recovery(self) -> bool:
        """Determine if automatic recovery should be attempted"""
        # Exponential backoff for recovery attempts
        if self.recovery_attempts > 0:
            time_since_last = time.time() - self.last_restart_time
            backoff_time = min(300, 30 * (2 ** (self.recovery_attempts - 1)))
            if time_since_last < backoff_time:
                return False
                
        return self.recovery_attempts < 5  # Max 5 attempts
        
    async def attempt_recovery(self):
        """Attempt automatic recovery"""
        self.state = ServiceState.RECOVERING
        self.recovery_attempts += 1
        self.last_restart_time = time.time()
        
        logging.info(f"Attempting recovery for {self.name} (attempt {self.recovery_attempts})")
        
        try:
            await self.restart_func()
            # Wait for service to stabilize
            await asyncio.sleep(self.recovery_timeout)
        except Exception as e:
            logging.error(f"Recovery failed: {e}")

# Example usage
async def example_health_check():
    # Simulate health check
    return random.random() > 0.1

async def example_restart():
    # Simulate restart
    logging.info("Restarting service...")
    await asyncio.sleep(2)

# Test the self-healing service
service = SelfHealingService(
    name="payment-service",
    health_check=example_health_check,
    restart_func=example_restart
)

# Run monitoring
# asyncio.run(service.monitor())
```

### Extension Challenges

1. Add dependency tracking between services
2. Implement cascading recovery prevention
3. Add resource limit checks before restart
4. Create recovery strategy selection based on failure type

---

## Exercise 2: Hierarchical Control System

Build a multi-level control system with delegation and escalation.

### Task

Create a control hierarchy for managing a distributed cache:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Decision:
    level: str
    action: str
    reason: str
    timestamp: float

class Controller(ABC):
    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level
        self.children: List[Controller] = []
        self.parent: Optional[Controller] = None
        
    @abstractmethod
    async def make_decision(self, context: Dict) -> Optional[Decision]:
        pass
        
    async def handle_request(self, context: Dict) -> Decision:
        """Handle request with delegation/escalation"""
        # Try to handle at current level
        decision = await self.make_decision(context)
        
        if decision:
            return decision
            
        # Delegate to children first
        for child in self.children:
            if self.should_delegate_to(child, context):
                decision = await child.handle_request(context)
                if decision:
                    return decision
                    
        # Escalate to parent if needed
        if self.parent and self.should_escalate(context):
            return await self.parent.handle_request(context)
            
        # Default decision
        return Decision(
            level=self.name,
            action="no_action",
            reason="No applicable control policy",
            timestamp=time.time()
        )

class CacheNodeController(Controller):
    """Local cache node controller"""
    async def make_decision(self, context: Dict) -> Optional[Decision]:
        if context.get("type") == "eviction":
            if context.get("memory_pressure", 0) > 0.8:
                return Decision(
                    level=self.name,
                    action="evict_lru",
                    reason="High memory pressure",
                    timestamp=time.time()
                )
        return None

class RegionController(Controller):
    """Regional cache controller"""
    async def make_decision(self, context: Dict) -> Optional[Decision]:
        if context.get("type") == "rebalance":
            if context.get("load_variance", 0) > 0.3:
                return Decision(
                    level=self.name,
                    action="rebalance_shards",
                    reason="High load variance across nodes",
                    timestamp=time.time()
                )
        return None

class GlobalController(Controller):
    """Global cache controller"""
    async def make_decision(self, context: Dict) -> Optional[Decision]:
        if context.get("type") == "capacity":
            if context.get("global_usage", 0) > 0.9:
                return Decision(
                    level=self.name,
                    action="add_capacity",
                    reason="Global capacity limit approaching",
                    timestamp=time.time()
                )
        return None

# Build hierarchy
global_ctrl = GlobalController("global", level=3)
region_ctrl = RegionController("us-east", level=2)
node_ctrl = CacheNodeController("node-1", level=1)

# Set relationships
global_ctrl.children.append(region_ctrl)
region_ctrl.parent = global_ctrl
region_ctrl.children.append(node_ctrl)
node_ctrl.parent = region_ctrl

# Test different scenarios
scenarios = [
    {"type": "eviction", "memory_pressure": 0.85},
    {"type": "rebalance", "load_variance": 0.4},
    {"type": "capacity", "global_usage": 0.95}
]

# for scenario in scenarios:
#     decision = await node_ctrl.handle_request(scenario)
#     print(f"Scenario: {scenario}")
#     print(f"Decision: {decision}\n")
```

---

## Exercise 3: Feedback Control Loop

Implement a PID controller for autoscaling.

### Requirements

1. Proportional, Integral, and Derivative control
2. Target metric tracking (e.g., CPU usage)
3. Scaling decisions with dampening
4. Overshoot prevention

### Implementation

```python
class PIDController:
    def __init__(self, 
                 kp: float = 1.0,  # Proportional gain
                 ki: float = 0.1,  # Integral gain
                 kd: float = 0.05, # Derivative gain
                 setpoint: float = 0.7,  # Target value
                 min_output: int = 1,
                 max_output: int = 100):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.min_output = min_output
        self.max_output = max_output
        
        self.integral = 0
        self.last_error = 0
        self.last_time = time.time()
        
    def update(self, current_value: float) -> int:
        """Calculate control output based on current value"""
        current_time = time.time()
        dt = current_time - self.last_time
        
        # Calculate error
        error = self.setpoint - current_value
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term
        self.integral += error * dt
        i_term = self.ki * self.integral
        
        # Derivative term
        if dt > 0:
            derivative = (error - self.last_error) / dt
            d_term = self.kd * derivative
        else:
            d_term = 0
            
        # Calculate output
        output = p_term + i_term + d_term
        
        # Apply limits
        output = max(self.min_output, min(self.max_output, output))
        
        # Update state
        self.last_error = error
        self.last_time = current_time
        
        return int(output)

class Autoscaler:
    def __init__(self, 
                 pid_controller: PIDController,
                 scale_func: Callable,
                 metric_func: Callable):
        self.controller = pid_controller
        self.scale_func = scale_func
        self.metric_func = metric_func
        self.current_instances = 1
        self.scaling_history = []
        
    async def control_loop(self):
        """Main control loop"""
        while True:
            # Get current metric
            current_metric = await self.metric_func()
            
            # Calculate desired instances
            desired_instances = self.controller.update(current_metric)
            
            # Apply scaling if needed
            if desired_instances != self.current_instances:
                await self.apply_scaling(desired_instances)
                
            # Record history
            self.scaling_history.append({
                'timestamp': time.time(),
                'metric': current_metric,
                'instances': self.current_instances
            })
            
            await asyncio.sleep(30)  # Control interval
            
    async def apply_scaling(self, desired_instances: int):
        """Apply scaling with safety checks"""
        # Limit rate of change
        max_change = max(1, int(self.current_instances * 0.2))
        actual_change = max(-max_change, min(max_change, 
                          desired_instances - self.current_instances))
        
        new_instances = self.current_instances + actual_change
        
        if new_instances != self.current_instances:
            logging.info(f"Scaling from {self.current_instances} to {new_instances}")
            await self.scale_func(new_instances)
            self.current_instances = new_instances

# Example usage
async def get_cpu_usage():
    # Simulate CPU usage
    return 0.6 + (random.random() - 0.5) * 0.4

async def scale_instances(count: int):
    # Simulate scaling
    logging.info(f"Scaling to {count} instances")

# Create autoscaler
pid = PIDController(kp=2.0, ki=0.5, kd=0.1, setpoint=0.7)
autoscaler = Autoscaler(pid, scale_instances, get_cpu_usage)

# Run control loop
# asyncio.run(autoscaler.control_loop())
```

---

## Exercise 4: Chaos Engineering Framework

Build a controlled chaos injection system.

### Task

Create a framework that can inject failures in a controlled manner:

```python
@dataclass
class ChaosExperiment:
    name: str
    target: str
    fault_type: str
    duration: int
    intensity: float
    
class ChaosController:
    def __init__(self):
        self.experiments: List[ChaosExperiment] = []
        self.active_faults: Dict[str, asyncio.Task] = {}
        self.safety_checks: List[Callable] = []
        
    async def run_experiment(self, experiment: ChaosExperiment):
        """Run a chaos experiment with safety controls"""
        # Pre-flight checks
        if not await self.safety_check():
            logging.warning(f"Safety check failed for {experiment.name}")
            return
            
        # Inject fault
        logging.info(f"Starting chaos experiment: {experiment.name}")
        task = asyncio.create_task(
            self.inject_fault(experiment)
        )
        self.active_faults[experiment.name] = task
        
        # Monitor and control
        try:
            await asyncio.wait_for(task, timeout=experiment.duration * 2)
        except asyncio.TimeoutError:
            logging.error(f"Experiment {experiment.name} exceeded timeout")
            task.cancel()
            
    async def inject_fault(self, experiment: ChaosExperiment):
        """Inject specific fault type"""
        if experiment.fault_type == "latency":
            await self.inject_latency(experiment)
        elif experiment.fault_type == "failure":
            await self.inject_failure(experiment)
        elif experiment.fault_type == "resource":
            await self.inject_resource_pressure(experiment)
            
    async def emergency_stop(self):
        """Stop all active experiments"""
        logging.warning("Emergency stop activated")
        for name, task in self.active_faults.items():
            task.cancel()
        self.active_faults.clear()

# Test the framework
chaos = ChaosController()
experiment = ChaosExperiment(
    name="api-latency-test",
    target="api-service",
    fault_type="latency",
    duration=300,
    intensity=0.5
)
# await chaos.run_experiment(experiment)
```

---

## Exercise 5: Incident Response Automation

Create an automated incident response system.

### Implementation

Build a system that:
1. Detects incidents from multiple signals
2. Classifies severity automatically
3. Executes response playbooks
4. Tracks and reports on actions taken

---

## Summary & Best Practices

After completing these exercises, you should understand:

1. **Autonomous Control**
   - Self-healing mechanisms
   - Failure detection and recovery
   - Resource management

2. **Hierarchical Control**
   - Delegation patterns
   - Escalation policies
   - Distributed decision making

3. **Feedback Systems**
   - Control theory application
   - PID controllers
   - Stability and dampening

4. **Chaos Engineering**
   - Controlled failure injection
   - Safety mechanisms
   - Learning from experiments

5. **Automation Benefits**
   - Reduced manual intervention
   - Consistent responses
   - Faster recovery times

## Next Steps

- Implement control systems in your production environment
- Create runbooks for common scenarios
- Build monitoring for control effectiveness
- Practice chaos engineering regularly

Continue to [Pillar 5: Intelligence →](../pillar-5-intelligence/index.md)
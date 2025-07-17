# Recovery-Oriented Computing

!!! info "Philosophy"
    "The question is not if failures will happen, but when. Design systems to recover quickly rather than trying to prevent all failures."

!!! tip "Quick Navigation"
    [← Reference](index.md) | 
    [Security Considerations →](security-considerations.md)

## Core Principles

<div class="recovery-principles">

Recovery-Oriented Computing (ROC) represents a fundamental shift in how we think about system reliability:

| Traditional Approach | ROC Approach |
|---------------------|--------------|
| Prevent all failures | Accept failures as inevitable |
| Maximize MTBF | Minimize MTTR |
| Perfect components | Resilient systems |
| Avoid errors | Recover gracefully |
| Binary up/down | Degraded operation |

</div>

## The ROC Framework

### 1. Fast Recovery is Better Than Failure Prevention

<div class="principle-box">

**The Math Behind It:**

```
Availability = MTBF / (MTBF + MTTR)

Where:
- MTBF = Mean Time Between Failures
- MTTR = Mean Time To Recovery

If MTBF = 1000 hours and MTTR = 1 hour:
Availability = 1000 / 1001 = 99.9%

If we improve recovery to MTTR = 0.1 hour:
Availability = 1000 / 1000.1 = 99.99%

10x faster recovery = 10x better availability!
```

</div>

### 2. Design for Recovery

<div class="design-patterns">

#### Checkpoint and Restart
```python
class RecoverableService:
    def __init__(self):
        self.checkpoint_interval = timedelta(minutes=5)
        self.last_checkpoint = None
        
    async def run(self):
        # Try to recover from checkpoint
        state = await self.load_checkpoint()
        if state:
            logger.info(f"Recovered from checkpoint: {state.timestamp}")
            self.restore_state(state)
        
        while True:
            try:
                await self.process_work()
                
                # Periodic checkpointing
                if self.should_checkpoint():
                    await self.save_checkpoint()
                    
            except Exception as e:
                logger.error(f"Process failed: {e}")
                await self.recover_from_error(e)
    
    async def save_checkpoint(self):
        state = self.capture_state()
        await self.checkpoint_store.save(state)
        self.last_checkpoint = datetime.now()
```

#### Progressive Rollout
```yaml
# Canary deployment with automatic rollback
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: api-service
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  progressDeadlineSeconds: 60
  service:
    port: 80
  analysis:
    interval: 30s
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: error-rate
      thresholdRange:
        max: 1  # Max 1% error rate
      interval: 30s
    - name: latency
      thresholdRange:
        max: 500  # Max 500ms p99
      interval: 30s
  # Automatic rollback on failure
  rollbackOnFailure:
    enabled: true
```

</div>

### 3. Failure Detection and Diagnosis

<div class="detection-patterns">

#### Circuit Breaker Pattern
```java
public class CircuitBreaker {
    private final int failureThreshold;
    private final Duration timeout;
    private final Duration retryAfter;
    
    private State state = State.CLOSED;
    private int failureCount = 0;
    private Instant lastFailureTime;
    
    public <T> T execute(Supplier<T> operation) {
        if (state == State.OPEN) {
            if (shouldAttemptReset()) {
                state = State.HALF_OPEN;
            } else {
                throw new CircuitBreakerOpenException();
            }
        }
        
        try {
            T result = operation.get();
            onSuccess();
            return result;
        } catch (Exception e) {
            onFailure();
            throw e;
        }
    }
    
    private void onSuccess() {
        failureCount = 0;
        state = State.CLOSED;
    }
    
    private void onFailure() {
        failureCount++;
        lastFailureTime = Instant.now();
        
        if (failureCount >= failureThreshold) {
            state = State.OPEN;
            // Trigger recovery procedures
            notifyRecoverySystem();
        }
    }
}
```

#### Health Check Hierarchy
```python
class HealthCheckSystem:
    def __init__(self):
        self.checks = {
            'critical': [],    # System can't function
            'degraded': [],    # Reduced functionality
            'maintenance': []  # Needs attention
        }
    
    async def check_health(self):
        results = {
            'status': 'healthy',
            'checks': {},
            'recovery_actions': []
        }
        
        # Run checks in priority order
        for level in ['critical', 'degraded', 'maintenance']:
            for check in self.checks[level]:
                try:
                    result = await check.execute()
                    results['checks'][check.name] = result
                    
                    if not result.healthy:
                        results['status'] = level
                        if result.recovery_action:
                            results['recovery_actions'].append(
                                result.recovery_action
                            )
                except Exception as e:
                    results['checks'][check.name] = {
                        'healthy': False,
                        'error': str(e)
                    }
                    results['status'] = 'critical'
        
        # Trigger automatic recovery if needed
        if results['recovery_actions']:
            await self.execute_recovery(results['recovery_actions'])
            
        return results
```

</div>

### 4. Recovery Procedures

<div class="recovery-procedures">

#### Automated Recovery Playbook
```python
class RecoveryOrchestrator:
    def __init__(self):
        self.playbooks = {}
        self.recovery_history = []
        
    def register_playbook(self, failure_type, playbook):
        self.playbooks[failure_type] = playbook
    
    async def handle_failure(self, failure_event):
        playbook = self.match_playbook(failure_event)
        if not playbook:
            await self.escalate_to_human(failure_event)
            return
        
        recovery_id = str(uuid.uuid4())
        logger.info(f"Starting recovery {recovery_id} for {failure_event.type}")
        
        try:
            # Execute recovery steps
            for step in playbook.steps:
                logger.info(f"Executing step: {step.name}")
                
                # Pre-checks
                if not await step.pre_check():
                    raise RecoveryException(f"Pre-check failed: {step.name}")
                
                # Execute with timeout
                await asyncio.wait_for(
                    step.execute(),
                    timeout=step.timeout
                )
                
                # Verify success
                if not await step.verify():
                    raise RecoveryException(f"Verification failed: {step.name}")
                
                # Record progress
                await self.record_progress(recovery_id, step)
            
            # Final validation
            if await playbook.validate_recovery():
                logger.info(f"Recovery {recovery_id} successful")
                await self.record_success(recovery_id)
            else:
                raise RecoveryException("Final validation failed")
                
        except Exception as e:
            logger.error(f"Recovery {recovery_id} failed: {e}")
            await self.escalate_to_human(failure_event, recovery_id)
```

#### State Reconstruction
```go
type StateReconstructor struct {
    eventStore EventStore
    snapshots  SnapshotStore
}

func (sr *StateReconstructor) RecoverState(stateID string, targetTime time.Time) (*State, error) {
    // Find nearest snapshot before target time
    snapshot, err := sr.snapshots.GetNearestBefore(stateID, targetTime)
    if err != nil {
        // No snapshot, rebuild from beginning
        snapshot = &Snapshot{
            State:     NewEmptyState(stateID),
            Timestamp: time.Time{},
        }
    }
    
    // Replay events from snapshot to target time
    events, err := sr.eventStore.GetEventsBetween(
        stateID,
        snapshot.Timestamp,
        targetTime,
    )
    if err != nil {
        return nil, fmt.Errorf("failed to fetch events: %w", err)
    }
    
    state := snapshot.State
    for _, event := range events {
        if err := state.Apply(event); err != nil {
            // Handle poisoned events
            log.Printf("Skipping poisoned event %s: %v", event.ID, err)
            continue
        }
    }
    
    // Validate reconstructed state
    if err := state.Validate(); err != nil {
        return nil, fmt.Errorf("invalid state after reconstruction: %w", err)
    }
    
    return state, nil
}
```

</div>

## Recovery Patterns

### 1. Microreboot

<div class="pattern-box">

**Concept**: Restart just the failing component, not the entire system.

```python
class MicrorebootManager:
    def __init__(self):
        self.component_registry = {}
        self.reboot_history = defaultdict(list)
        self.max_reboots_per_hour = 3
        
    async def handle_component_failure(self, component_id: str):
        # Check reboot limit
        recent_reboots = self.get_recent_reboots(component_id)
        if len(recent_reboots) >= self.max_reboots_per_hour:
            # Escalate - too many reboots
            return await self.escalate_failure(component_id)
        
        # Perform microreboot
        component = self.component_registry[component_id]
        
        # 1. Checkpoint current state
        state = await component.checkpoint()
        
        # 2. Gracefully stop
        await component.stop(timeout=5)
        
        # 3. Clean up resources
        await component.cleanup()
        
        # 4. Restart with saved state
        await component.start(state)
        
        # 5. Verify health
        if await component.health_check():
            self.record_successful_reboot(component_id)
        else:
            await self.escalate_failure(component_id)
```

</div>

### 2. Bulkheading

<div class="pattern-box">

**Concept**: Isolate failures to prevent cascade.

```java
public class BulkheadedSystem {
    private final Map<String, ExecutorService> bulkheads;
    private final Map<String, Semaphore> resourceLimits;
    
    public BulkheadedSystem() {
        // Create isolated thread pools for each subsystem
        bulkheads = Map.of(
            "critical", Executors.newFixedThreadPool(20),
            "standard", Executors.newFixedThreadPool(50),
            "batch", Executors.newFixedThreadPool(10)
        );
        
        // Resource limits per bulkhead
        resourceLimits = Map.of(
            "critical", new Semaphore(100),  // Max 100 concurrent
            "standard", new Semaphore(500),
            "batch", new Semaphore(50)
        );
    }
    
    public CompletableFuture<Result> execute(
        Request request,
        String bulkhead
    ) {
        ExecutorService executor = bulkheads.get(bulkhead);
        Semaphore limit = resourceLimits.get(bulkhead);
        
        if (!limit.tryAcquire()) {
            // Bulkhead full - reject to prevent cascade
            return CompletableFuture.failedFuture(
                new BulkheadFullException(bulkhead)
            );
        }
        
        return CompletableFuture
            .supplyAsync(() -> processRequest(request), executor)
            .whenComplete((result, error) -> limit.release());
    }
}
```

</div>

### 3. Crash-Only Software

<div class="pattern-box">

**Concept**: Design software that can only be stopped by crashing and recovers correctly from crashes.

```go
type CrashOnlyService struct {
    state      *PersistentState
    wal        *WriteAheadLog
    checksum   uint64
}

func (s *CrashOnlyService) Start() error {
    // Always assume we're recovering from a crash
    log.Println("Starting recovery process...")
    
    // 1. Verify and repair WAL
    if err := s.wal.Verify(); err != nil {
        log.Printf("WAL corrupted, truncating: %v", err)
        s.wal.TruncateCorrupted()
    }
    
    // 2. Replay WAL to rebuild state
    s.state = NewPersistentState()
    entries, err := s.wal.ReadAll()
    if err != nil {
        return fmt.Errorf("failed to read WAL: %w", err)
    }
    
    for _, entry := range entries {
        if err := s.state.Apply(entry); err != nil {
            log.Printf("Skipping bad entry: %v", err)
            continue
        }
    }
    
    // 3. Verify state integrity
    actualChecksum := s.state.Checksum()
    if actualChecksum != s.checksum {
        log.Printf("Checksum mismatch, rebuilding indices...")
        s.state.RebuildIndices()
    }
    
    // 4. Ready to serve
    log.Println("Recovery complete, ready to serve")
    return s.serve()
}

// No graceful shutdown - just crash
func (s *CrashOnlyService) Stop() {
    os.Exit(0)
}
```

</div>

## Recovery Metrics

### Key Metrics to Track

<div class="metrics-grid">

| Metric | Description | Target |
|--------|-------------|--------|
| **MTTR** | Mean Time To Recovery | <5 minutes |
| **Recovery Success Rate** | % of automated recoveries that succeed | >95% |
| **Blast Radius** | % of system affected by failure | <10% |
| **Recovery Debt** | Backlog of manual recovery tasks | <1 hour |
| **False Positive Rate** | % of unnecessary recoveries triggered | <5% |

</div>

### Recovery Dashboard Example

```python
class RecoveryDashboard:
    def __init__(self):
        self.metrics = PrometheusMetrics()
        
    def record_recovery(self, recovery_event):
        # Track recovery time
        duration = recovery_event.end_time - recovery_event.start_time
        self.metrics.histogram(
            'recovery_duration_seconds',
            duration.total_seconds(),
            labels={
                'component': recovery_event.component,
                'failure_type': recovery_event.failure_type,
                'automated': recovery_event.automated
            }
        )
        
        # Track success/failure
        self.metrics.counter(
            'recovery_attempts_total',
            labels={
                'component': recovery_event.component,
                'status': 'success' if recovery_event.success else 'failure'
            }
        )
        
        # Track blast radius
        self.metrics.gauge(
            'recovery_blast_radius_percent',
            recovery_event.affected_users_percent,
            labels={'component': recovery_event.component}
        )
```

## Case Studies

### Netflix: Chaos Engineering for Recovery

<div class="case-study">

Netflix pioneered using controlled failures to improve recovery:

- **Chaos Monkey**: Randomly kills instances
- **Chaos Kong**: Simulates entire region failures
- **FIT (Failure Injection Testing)**: Injects specific failures

**Results:**
- Reduced MTTR from hours to minutes
- Improved recovery automation from 60% to 95%
- Decreased customer impact during real failures

</div>

### Google: SRE and Error Budgets

<div class="case-study">

Google's approach focuses on balancing reliability with velocity:

- **Error Budgets**: Acceptable failure rate allows for innovation
- **Blameless Postmortems**: Focus on system improvement
- **Playbook Automation**: Encode recovery procedures

**Key Insight**: "100% reliability is the wrong target—it's too expensive and slows innovation."

</div>

## Implementation Checklist

<div class="checklist-box">

### Getting Started with ROC

- [ ] **Measure current MTTR** for common failures
- [ ] **Identify top 3 failure modes** from incidents
- [ ] **Create automated playbooks** for each failure mode
- [ ] **Implement health checks** with clear degradation levels
- [ ] **Add circuit breakers** to critical dependencies
- [ ] **Set up recovery metrics** and dashboards
- [ ] **Practice failure scenarios** monthly
- [ ] **Document recovery procedures** as code
- [ ] **Train team** on recovery-first mindset
- [ ] **Celebrate fast recoveries** not just uptime

</div>

## Key Takeaways

!!! success "Recovery-Oriented Mindset"
    
    1. **Accept failure as normal** - Design assuming things will break
    2. **Optimize for recovery speed** - MTTR > MTBF
    3. **Automate recovery procedures** - Humans are too slow
    4. **Practice recovery regularly** - Muscle memory matters
    5. **Measure recovery effectiveness** - What gets measured gets improved

## Next Steps

Ready to implement recovery-oriented patterns?

- Review [Axiom 3: Partial Failure](../part1-axioms/axiom-3-failure/index.md)
- Explore [Chaos Engineering Tools](tools.md#chaos-engineering)
- Read the [SRE Book](https://sre.google/sre-book/table-of-contents/) by Google
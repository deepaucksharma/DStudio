---
title: Edge Computing/IoT Patterns
description: "Optimize distributed systems for edge devices and IoT deployments where latency and connectivity matter"
type: pattern
difficulty: intermediate
reading_time: 15 min
prerequisites: []
pattern_type: "infrastructure"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part III: Patterns](index.md) → **Edge Computing/IoT Patterns**

# Edge Computing/IoT Patterns

**Computing at the speed of physics**

## THE PROBLEM

```
Centralized cloud has physics limits:
- Camera → Cloud → Decision = 100ms+ latency
- Self-driving car at 60mph = 8.8 feet blind
- 1000 IoT devices × 1KB/sec = 1MB/sec upstream
- Remote oil rig satellite link = $10/MB

When milliseconds = meters, edge matters
```bash
## THE SOLUTION

```
Push compute to the edge:

Device     Edge Node    Regional DC    Cloud
 [ML]  →   [Cache]  →  [Process]  →  [Store]
  ↓          ↓            ↓            ↓
<1ms       <10ms        <50ms        <200ms
```bash
## Edge Architecture Patterns

```
1. FOG COMPUTING (3-tier)
   Device → Fog → Cloud

2. MOBILE EDGE COMPUTING
   Phone → Cell Tower → Regional

3. CLOUDLETS
   Device → Mini-DC → Cloud

4. HIERARCHICAL PROCESSING
   Sense → Filter → Aggregate → Analyze
```bash
## IMPLEMENTATION

```python
# Edge node implementation
class EdgeNode:
    def __init__(self, node_id, location):
        self.node_id = node_id
        self.location = location
        self.local_cache = LRUCache(capacity=1000)
        self.ml_models = {}
        self.device_registry = {}

    def process_locally(self, data):
        """Process data at edge when possible"""

        # 1. Check if we can handle locally
        if self.can_process_locally(data):
            result = self.run_edge_inference(data)

            # Only send summary to cloud
            self.send_summary_to_cloud({
                'node_id': self.node_id,
                'timestamp': time.time(),
                'result': result.summary,
                'confidence': result.confidence
            })

            return result

        # 2. Forward to cloud if needed
        return self.forward_to_cloud(data)

    def run_edge_inference(self, data):
        """Run ML model at edge"""
        model_name = self.select_model(data.type)

        if model_name not in self.ml_models:
            # Download model from cloud
            self.ml_models[model_name] = self.download_model(model_name)

        model = self.ml_models[model_name]

        # Quantized inference for edge
        with torch.no_grad():
            # Convert to INT8 for edge efficiency
            quantized_input = self.quantize(data.tensor)
            prediction = model(quantized_input)

        return EdgeResult(
            prediction=prediction,
            latency_ms=0.5,
            processed_at='edge'
        )

# Hierarchical data processing
class HierarchicalProcessor:
    def __init__(self):
        self.levels = {
            'sensor': SensorLevel(),      # Raw data
            'edge': EdgeLevel(),          # Filter/compress
            'fog': FogLevel(),           # Aggregate
            'cloud': CloudLevel()        # Deep analysis
        }

    def process_iot_stream(self, sensor_data):
        """Process through hierarchy"""

        # Level 1: Sensor (immediate response)
        if sensor_data.is_critical():
            self.levels['sensor'].immediate_action(sensor_data)

        # Level 2: Edge (filter noise)
        filtered = self.levels['edge'].filter_data(sensor_data)
        if not filtered.is_significant():
            return  # Drop insignificant data

        # Level 3: Fog (aggregate)
        aggregated = self.levels['fog'].aggregate(filtered)

        # Level 4: Cloud (deep analysis)
        if aggregated.requires_analysis():
            self.levels['cloud'].analyze(aggregated)

# Edge-specific data structures
class EdgeDataManager:
    def __init__(self, storage_limit_mb=100):
        self.storage_limit = storage_limit_mb * 1024 * 1024
        self.data_tiers = {
            'hot': CircularBuffer(size=1000),      # Recent data
            'warm': CompressedStore(size=10000),   # Compressed
            'cold': None  # Uploaded to cloud
        }

    def ingest(self, data):
        """Smart data tiering at edge"""

        # Hot tier: Keep recent raw data
        self.data_tiers['hot'].append(data)

        # Warm tier: Compress older data
        if self.data_tiers['hot'].is_full():
            old_data = self.data_tiers['hot'].evict_oldest()
            compressed = self.compress(old_data)
            self.data_tiers['warm'].store(compressed)

        # Cold tier: Upload to cloud
        if self.get_storage_used() > self.storage_limit * 0.8:
            self.upload_cold_data()

    def query(self, time_range):
        """Query across tiers"""
        results = []

        # Check hot tier first
        hot_results = self.data_tiers['hot'].query(time_range)
        results.extend(hot_results)

        # Check warm tier if needed
        if not time_range.satisfied_by(hot_results):
            warm_results = self.data_tiers['warm'].query(time_range)
            results.extend(self.decompress(warm_results))

        # Fetch from cloud if needed
        if not time_range.satisfied_by(results):
            cold_results = self.fetch_from_cloud(time_range)
            results.extend(cold_results)

        return results

# Edge ML optimization
class EdgeMLOptimizer:
    @staticmethod
    def prepare_model_for_edge(cloud_model):
        """Optimize model for edge deployment"""

        # 1. Quantization (FP32 → INT8)
        quantized = torch.quantization.quantize_dynamic(
            cloud_model,
            {nn.Linear, nn.Conv2d},
            dtype=torch.qint8
        )

        # 2. Pruning (remove small weights)
        pruned = prune_model(quantized, sparsity=0.5)

        # 3. Knowledge distillation
        edge_model = create_student_model(
            teacher=cloud_model,
            compression_ratio=0.1
        )

        # 4. Compile for edge hardware
        if has_edge_accelerator():
            edge_model = compile_for_accelerator(edge_model)

        return EdgeModel(
            model=edge_model,
            size_mb=get_model_size(edge_model),
            latency_ms=benchmark_latency(edge_model)
        )

# Edge-cloud synchronization
class EdgeCloudSync:
    def __init__(self, edge_node, cloud_endpoint):
        self.edge_node = edge_node
        self.cloud = cloud_endpoint
        self.sync_queue = PriorityQueue()
        self.bandwidth_monitor = BandwidthMonitor()

    async def sync_with_backpressure(self):
        """Adaptive sync based on bandwidth"""

        while True:
            # Monitor available bandwidth
            bandwidth_kbps = self.bandwidth_monitor.get_current()

            # Adjust sync strategy
            if bandwidth_kbps < 100:
                # Low bandwidth: Only critical data
                await self.sync_critical_only()
            elif bandwidth_kbps < 1000:
                # Medium bandwidth: Batched updates
                await self.sync_batched()
            else:
                # Good bandwidth: Full sync
                await self.sync_full()

            await asyncio.sleep(self.calculate_sync_interval())

    async def sync_critical_only(self):
        """Only sync critical alerts"""
        critical_data = self.sync_queue.get_priority('critical')
        if critical_data:
            await self.cloud.send(critical_data, priority='high')

    async def sync_batched(self):
        """Batch and compress updates"""
        batch = []
        batch_size = 0
        max_batch_size = 1024 * 100  # 100KB

        while not self.sync_queue.empty() and batch_size < max_batch_size:
            item = self.sync_queue.get()
            batch.append(item)
            batch_size += len(item)

        if batch:
            compressed = compress(batch)
            await self.cloud.send(compressed)

# Edge orchestration
class EdgeOrchestrator:
    def __init__(self):
        self.nodes = {}
        self.workloads = {}

    def deploy_workload(self, workload):
        """Deploy workload to optimal edge node"""

        # Find best node based on:
        # - Proximity to data source
        # - Available compute resources
        # - Network latency
        # - Power availability

        scores = {}
        for node_id, node in self.nodes.items():
            score = self.calculate_placement_score(workload, node)
            scores[node_id] = score

        best_node = max(scores, key=scores.get)

        # Deploy with resource limits
        deployment = EdgeDeployment(
            workload=workload,
            node=self.nodes[best_node],
            resources={
                'cpu_shares': 100,  # Limited CPU
                'memory_mb': 50,    # Limited RAM
                'storage_mb': 10    # Limited storage
            }
        )

        return deployment.deploy()
```bash
## Edge-Specific Patterns

```python
# Store-and-forward for intermittent connectivity
class StoreAndForward:
    def __init__(self, storage_path):
        self.storage = PersistentQueue(storage_path)
        self.connection_monitor = ConnectionMonitor()

    async def send(self, data):
        # Always store first
        self.storage.put(data)

        # Try to forward if connected
        if self.connection_monitor.is_connected():
            await self.forward_stored_data()
        else:
            # Will retry when connection restored
            self.connection_monitor.on_connected(self.forward_stored_data)

    async def forward_stored_data(self):
        """Forward all stored data when connected"""
        while not self.storage.empty():
            data = self.storage.get()
            try:
                await self.cloud.send(data)
                self.storage.commit()  # Remove from queue
            except Exception:
                self.storage.rollback()  # Keep in queue
                break

# Edge federation
class EdgeFederation:
    """Collaborate across edge nodes"""

    def __init__(self, node_id):
        self.node_id = node_id
        self.peers = {}

    async def federated_learning(self, local_model):
        """Train model across edge nodes"""

        # 1. Train on local data
        local_update = self.train_local(local_model)

        # 2. Share with peers
        peer_updates = await self.exchange_updates(local_update)

        # 3. Aggregate updates
        global_update = self.federated_average([local_update] + peer_updates)

        # 4. Apply to local model
        self.apply_update(local_model, global_update)

        return local_model
```

## ✓ CHOOSE THIS WHEN:
• Ultra-low latency required (<10ms)
• Bandwidth is limited/expensive
• Privacy/data sovereignty matters
• Intermittent connectivity
• Real-time decision making

## ⚠️ BEWARE OF:
• Limited compute at edge
• Hardware heterogeneity
• Security of edge nodes
• Update/maintenance complexity
• Cost of edge infrastructure

## REAL EXAMPLES
• **Tesla**: Autopilot edge inference
• **AWS Wavelength**: 5G edge computing
• **Azure IoT Edge**: Factory automation

---

**Previous**: [← Distributed Lock Pattern](distributed-lock.md) | **Next**: [Event-Driven Architecture →](event-driven.md)
---

## ✅ When to Use

### Ideal Scenarios
- **Distributed systems** with external dependencies
- **High-availability services** requiring reliability
- **External service integration** with potential failures
- **High-traffic applications** needing protection

### Environmental Factors
- **High Traffic**: System handles significant load
- **External Dependencies**: Calls to other services or systems
- **Reliability Requirements**: Uptime is critical to business
- **Resource Constraints**: Limited connections, threads, or memory

### Team Readiness
- Team understands distributed systems concepts
- Monitoring and alerting infrastructure exists
- Operations team can respond to pattern-related alerts

### Business Context
- Cost of downtime is significant
- User experience is a priority
- System is customer-facing or business-critical

## ❌ When NOT to Use

### Inappropriate Scenarios
- **Simple applications** with minimal complexity
- **Development environments** where reliability isn't critical
- **Single-user systems** without scale requirements
- **Internal tools** with relaxed availability needs

### Technical Constraints
- **Simple Systems**: Overhead exceeds benefits
- **Development/Testing**: Adds unnecessary complexity
- **Performance Critical**: Pattern overhead is unacceptable
- **Legacy Systems**: Cannot be easily modified

### Resource Limitations
- **No Monitoring**: Cannot observe pattern effectiveness
- **Limited Expertise**: Team lacks distributed systems knowledge
- **Tight Coupling**: System design prevents pattern implementation

### Anti-Patterns
- Adding complexity without clear benefit
- Implementing without proper monitoring
- Using as a substitute for fixing root causes
- Over-engineering simple problems

## ⚖️ Trade-offs

### Benefits vs Costs

| Benefit | Cost | Mitigation |
|---------|------|------------|
| **Improved Reliability** | Implementation complexity | Use proven libraries/frameworks |
| **Better Performance** | Resource overhead | Monitor and tune parameters |
| **Faster Recovery** | Operational complexity | Invest in monitoring and training |
| **Clearer Debugging** | Additional logging | Use structured logging |

### Performance Impact
- **Latency**: Small overhead per operation
- **Memory**: Additional state tracking
- **CPU**: Monitoring and decision logic
- **Network**: Possible additional monitoring calls

### Operational Complexity
- **Monitoring**: Need dashboards and alerts
- **Configuration**: Parameters must be tuned
- **Debugging**: Additional failure modes to understand
- **Testing**: More scenarios to validate

### Development Trade-offs
- **Initial Cost**: More time to implement correctly
- **Maintenance**: Ongoing tuning and monitoring
- **Testing**: Complex failure scenarios to validate
- **Documentation**: More concepts for team to understand

## 💻 Code Sample

### Basic Implementation

```python
class Edge_ComputingPattern:
    def __init__(self, config):
        self.config = config
        self.metrics = Metrics()
        self.state = "ACTIVE"

    def process(self, request):
        """Main processing logic with pattern protection"""
        if not self._is_healthy():
            return self._fallback(request)

        try:
            result = self._protected_operation(request)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            return self._fallback(request)

    def _is_healthy(self):
        """Check if the protected resource is healthy"""
        return self.metrics.error_rate < self.config.threshold

    def _protected_operation(self, request):
        """The operation being protected by this pattern"""
        # Implementation depends on specific use case
        pass

    def _fallback(self, request):
        """Fallback behavior when protection activates"""
        return {"status": "fallback", "message": "Service temporarily unavailable"}

    def _record_success(self):
        self.metrics.record_success()

    def _record_failure(self, error):
        self.metrics.record_failure(error)

# Usage example
pattern = Edge_ComputingPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
edge_computing:
  enabled: true
  thresholds:
    failure_rate: 50%
    response_time: 5s
    error_count: 10
  timeouts:
    operation: 30s
    recovery: 60s
  fallback:
    enabled: true
    strategy: "cached_response"
  monitoring:
    metrics_enabled: true
    health_check_interval: 30s
```

### Testing the Implementation

```python
def test_edge_computing_behavior():
    pattern = Edge_ComputingPattern(test_config)

    # Test normal operation
    result = pattern.process(normal_request)
    assert result['status'] == 'success'

    # Test failure handling
    with mock.patch('external_service.call', side_effect=Exception):
        result = pattern.process(failing_request)
        assert result['status'] == 'fallback'

    # Test recovery
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
```

## 💪 Hands-On Exercises

### Exercise 1: Pattern Recognition ⭐⭐
**Time**: ~15 minutes
**Objective**: Identify Edge Computing/IoT s in existing systems

**Task**:
Find 2 real-world examples where Edge Computing/IoT s is implemented:
1. **Example 1**: A well-known tech company or service
2. **Example 2**: An open-source project or tool you've used

For each example:
- Describe how the pattern is implemented
- What problems it solves in that context
- What alternatives could have been used

### Exercise 2: Implementation Planning ⭐⭐⭐
**Time**: ~25 minutes
**Objective**: Design an implementation of Edge Computing/IoT s

**Scenario**: You need to implement Edge Computing/IoT s for an e-commerce checkout system processing 10,000 orders/hour.

**Requirements**:
- 99.9% availability required
- Payment processing must be reliable
- Orders must not be lost or duplicated

**Your Task**:
1. Design the architecture using Edge Computing/IoT s
2. Identify key components and their responsibilities
3. Define interfaces between components
4. Consider failure scenarios and mitigation strategies

**Deliverable**: Architecture diagram + 1-page implementation plan

### Exercise 3: Trade-off Analysis ⭐⭐⭐⭐
**Time**: ~20 minutes
**Objective**: Evaluate when NOT to use Edge Computing/IoT s

**Challenge**: You're consulting for a startup building their first product.

**Analysis Required**:
1. **Context Assessment**: Under what conditions would Edge Computing/IoT s be overkill?
2. **Cost-Benefit**: Compare implementation costs vs. benefits
3. **Alternatives**: What simpler approaches could work initially?
4. **Evolution Path**: How would you migrate to Edge Computing/IoT s later?

**Anti-Pattern Warning**: Identify one common mistake teams make when implementing this pattern.

---

## 🛠️ Code Challenge

### Beginner: Basic Implementation
Implement a minimal version of Edge Computing/IoT s in your preferred language.
- Focus on core functionality
- Include basic error handling
- Add simple logging

### Intermediate: Production Features
Extend the basic implementation with:
- Configuration management
- Metrics collection
- Unit tests
- Documentation

### Advanced: Performance & Scale
Optimize for production use:
- Handle concurrent access
- Implement backpressure
- Add monitoring hooks
- Performance benchmarks

---

## 🎯 Real-World Application

**Project Integration**:
- How would you introduce Edge Computing/IoT s to an existing system?
- What migration strategy would minimize risk?
- How would you measure success?

**Team Discussion Points**:
1. When team members suggest this pattern, what questions should you ask?
2. How would you explain the value to non-technical stakeholders?
3. What monitoring would indicate the pattern is working well?

---

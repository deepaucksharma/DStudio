# Control Distribution Examples & Case Studies

!!! info "Prerequisites"
    - [Distribution of Control Core Concepts](index.md)

!!! tip "Quick Navigation"
    [← Control Distribution Concepts](index.md) | 
    [Exercises →](exercises.md) |
    [↑ Pillars Overview](../index.md)

## Real-World Control Plane Failures

<div class="failure-vignette">

### 🎬 The Kubernetes API Server Meltdown

```yaml
Company: Major tech company
Date: December 2021
Duration: 4 hours
Impact: Complete cluster paralysis

What happened:
- 10,000 node Kubernetes cluster
- Someone created a DaemonSet with a bug
- Each pod continuously updated its status
- 10,000 pods × updates/sec = API overload

The cascade:
09:00 - DaemonSet deployed
09:02 - API server latency increasing
09:05 - etcd write latency spiking
09:10 - API server OOM killed
09:15 - Control plane unreachable
09:20 - No new pods can be scheduled
09:30 - Existing pods continue running (data plane OK!)

Why it got worse:
- kubectl commands timeout
- Can't delete the bad DaemonSet
- Can't access logs
- Monitoring uses same API
- Even kubectl delete times out

Recovery attempts:
1. Scale API servers (can't - need API)
2. Direct etcd access (risky)
3. Increase API server memory (no access)
4. Wait for OOM to clear (keeps recurring)

Final solution:
- SSH to master nodes
- Manually edit etcd
- Remove DaemonSet key
- Restart API servers
- Add rate limiting

Lessons learned:
1. Control plane needs rate limiting
2. Break-glass etcd access important
3. Data plane survived (good separation!)
4. Need out-of-band management
5. Resource quotas are critical
```

</div>

<div class="failure-vignette">

### 🎬 The Service Mesh Config Explosion

```yaml
Company: E-commerce platform
Service Mesh: Istio
Date: Black Friday 2022

Initial state:
- 500 microservices
- Istio service mesh
- 15,000 Envoy sidecars
- Config size: 2MB per sidecar

What triggered it:
- Added detailed routing rules
- Per-customer traffic shaping
- Fine-grained security policies
- Config size: 25MB per sidecar

The math of doom:
- 15,000 sidecars × 25MB = 375GB
- Config updates every 30s
- Network traffic: 12.5GB/s (!!)
- Control plane CPU: 100%

Timeline:
14:00 - New config pushed
14:01 - Config distribution starts
14:05 - Network saturated
14:10 - Sidecars can't get configs
14:15 - Health checks failing
14:20 - Services marked unhealthy
14:30 - Cascading failures

Why it's hard to fix:
- Can't push new config (network saturated)
- Can't roll back (same problem)
- Sidecars keep retrying (thundering herd)
- Control plane unresponsive

Emergency fix:
1. Block config endpoint at network level
2. Manually SSH to nodes
3. Edit Envoy bootstrap config
4. Restart sidecars with local config
5. Gradually restore service

Permanent fix:
- Incremental config updates (xDS)
- Config compression
- Rate limiting on config API
- Lazy loading of routes
- Config sharding by service

Cost: $8M in lost sales
```

</div>

<div class="failure-vignette">

### 🎬 The Terraform State Corruption

```yaml
Company: Financial services
Tool: Terraform Enterprise
Date: March 2023
Impact: Infrastructure frozen for 48 hours

Setup:
- 2000+ AWS resources
- Terraform Enterprise
- GitOps workflow
- State stored in S3

The mistake:
- Two engineers worked on same module
- Both ran 'terraform apply'
- Race condition in state locking
- State file corrupted

What broke:
{
  "version": 4,
  "terraform_version": "1.3.0",
  "serial": 18293,
  "lineage": "a1b2c3d4",
  "resources": [
    {
      "mode": "managed",
      "type": "aws_instance",
      "name": "web",
      "instances": [
        null,  // Corruption here!
        {
          "schema_version": 1,
          "attributes": {
            "id": "i-1234567890abcdef0",
            "ami": "ami-...",
            // Half the attributes missing
          }
        }
      ]
    }
  ]
}

Symptoms:
- terraform plan: "Error loading state"
- Resources exist in AWS
- Terraform wants to recreate everything
- 2000 resources = $$$$ mistake

Recovery attempts:
1. Restore from S3 versioning
   - Last good version: 1 week old
   - 100s of manual changes since

2. Terraform import everything
   - 2000 resources = weeks of work
   - Complex dependencies

3. Fix state manually
   - JSON surgery on 100MB file
   - One mistake = more corruption

Actual recovery:
Day 1:
- Freeze all infrastructure changes
- Download state file
- Write state repair tool
- Cross-reference with AWS

Day 2:
- Manually reconstruct state
- Test each resource type
- Validate against reality
- 48 hours of engineering time

Prevention:
- DynamoDB state locking
- State file backups every hour
- Terraform workspaces
- Better RBAC
- Pre-apply state validation
```

</div>

## Control Implementation Examples

### 1. Service Registry with Health Checking

```python
import asyncio
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import aiohttp

class HealthStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"

@dataclass
class ServiceInstance:
    service_name: str
    instance_id: str
    host: str
    port: int
    metadata: Dict
    health_status: HealthStatus
    last_heartbeat: float
    last_health_check: float
    consecutive_failures: int

class ServiceRegistry:
    def __init__(self, health_check_interval=10, heartbeat_timeout=30):
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.health_check_interval = health_check_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.watchers: Dict[str, Set[asyncio.Queue]] = {}
        
    async def register(self, service_name: str, host: str, port: int, 
                      metadata: Optional[Dict] = None) -> str:
        """Register a service instance"""
        instance_id = f"{service_name}-{host}:{port}-{int(time.time())}"
        
        instance = ServiceInstance(
            service_name=service_name,
            instance_id=instance_id,
            host=host,
            port=port,
            metadata=metadata or {},
            health_status=HealthStatus.HEALTHY,
            last_heartbeat=time.time(),
            last_health_check=time.time(),
            consecutive_failures=0
        )
        
        if service_name not in self.services:
            self.services[service_name] = []
            self.watchers[service_name] = set()
            
        self.services[service_name].append(instance)
        
        # Notify watchers
        await self._notify_watchers(service_name, "instance_added", instance)
        
        return instance_id
        
    async def discover(self, service_name: str, 
                      only_healthy: bool = True) -> List[ServiceInstance]:
        """Discover service instances"""
        if service_name not in self.services:
            return []
            
        instances = self.services[service_name]
        
        if only_healthy:
            instances = [
                i for i in instances 
                if i.health_status == HealthStatus.HEALTHY
            ]
            
        return instances
        
    async def watch(self, service_name: str) -> asyncio.Queue:
        """Watch for service changes"""
        if service_name not in self.watchers:
            self.watchers[service_name] = set()
            
        queue = asyncio.Queue()
        self.watchers[service_name].add(queue)
        
        # Send initial state
        instances = await self.discover(service_name, only_healthy=False)
        await queue.put({
            'type': 'initial_state',
            'instances': instances
        })
        
        return queue
        
    async def health_check_loop(self):
        """Continuously health check all instances"""
        while True:
            await self._check_all_instances()
            await asyncio.sleep(self.health_check_interval)
            
    async def _check_all_instances(self):
        """Health check all registered instances"""
        tasks = []
        
        for service_name, instances in self.services.items():
            for instance in instances:
                task = self._health_check_instance(instance)
                tasks.append(task)
                
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def _health_check_instance(self, instance: ServiceInstance):
        """Health check a single instance"""
        url = f"http://{instance.host}:{instance.port}/health"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    instance.last_health_check = time.time()
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check detailed health
                        if data.get('status') == 'healthy':
                            await self._mark_healthy(instance)
                        elif data.get('status') == 'degraded':
                            await self._mark_degraded(instance)
                        else:
                            await self._mark_unhealthy(instance)
                    else:
                        await self._mark_unhealthy(instance)
                        
        except Exception as e:
            await self._mark_unhealthy(instance)
            
    async def _mark_healthy(self, instance: ServiceInstance):
        """Mark instance as healthy"""
        if instance.health_status != HealthStatus.HEALTHY:
            instance.health_status = HealthStatus.HEALTHY
            instance.consecutive_failures = 0
            await self._notify_watchers(
                instance.service_name, 
                "instance_healthy", 
                instance
            )
            
    async def _mark_unhealthy(self, instance: ServiceInstance):
        """Mark instance as unhealthy"""
        instance.consecutive_failures += 1
        
        if instance.consecutive_failures >= 3:
            if instance.health_status != HealthStatus.UNHEALTHY:
                instance.health_status = HealthStatus.UNHEALTHY
                await self._notify_watchers(
                    instance.service_name,
                    "instance_unhealthy",
                    instance
                )
                
    async def _notify_watchers(self, service_name: str, 
                              event_type: str, instance: ServiceInstance):
        """Notify all watchers of a service"""
        if service_name not in self.watchers:
            return
            
        notification = {
            'type': event_type,
            'instance': instance,
            'timestamp': time.time()
        }
        
        # Send to all watchers
        dead_watchers = set()
        
        for queue in self.watchers[service_name]:
            try:
                queue.put_nowait(notification)
            except asyncio.QueueFull:
                dead_watchers.add(queue)
                
        # Clean up dead watchers
        self.watchers[service_name] -= dead_watchers

# Usage example
async def main():
    registry = ServiceRegistry()
    
    # Start health check loop
    asyncio.create_task(registry.health_check_loop())
    
    # Register services
    api_id = await registry.register(
        "api-service",
        "10.0.1.10",
        8080,
        {"version": "1.2.3", "region": "us-east"}
    )
    
    # Watch for changes
    watcher = await registry.watch("api-service")
    
    while True:
        event = await watcher.get()
        print(f"Service event: {event['type']}")
```

### 2. GitOps Controller Implementation

```python
import git
import yaml
import asyncio
import hashlib
from typing import Dict, List, Any
from dataclasses import dataclass
from kubernetes import client, config

@dataclass
class Resource:
    apiVersion: str
    kind: str
    metadata: Dict
    spec: Dict
    
@dataclass
class SyncStatus:
    resource: Resource
    desired_hash: str
    actual_hash: str
    in_sync: bool
    error: Optional[str]

class GitOpsController:
    def __init__(self, repo_url: str, branch: str = "main", 
                 sync_interval: int = 60):
        self.repo_url = repo_url
        self.branch = branch
        self.sync_interval = sync_interval
        self.repo_path = "/tmp/gitops-repo"
        self.k8s_client = None
        
        # Initialize Kubernetes client
        config.load_incluster_config()  # In cluster
        self.k8s_client = client.ApiClient()
        
    async def run(self):
        """Main control loop"""
        while True:
            try:
                await self.sync_cycle()
            except Exception as e:
                print(f"Sync cycle error: {e}")
                
            await asyncio.sleep(self.sync_interval)
            
    async def sync_cycle(self):
        """Single sync cycle"""
        # Pull latest from git
        self._pull_repo()
        
        # Load desired state
        desired_resources = self._load_resources()
        
        # Get actual state
        actual_resources = await self._get_actual_state(desired_resources)
        
        # Compare and sync
        sync_status = self._compare_states(desired_resources, actual_resources)
        
        # Apply changes
        await self._apply_changes(sync_status)
        
    def _pull_repo(self):
        """Pull latest from git repository"""
        if not os.path.exists(self.repo_path):
            git.Repo.clone_from(self.repo_url, self.repo_path)
        else:
            repo = git.Repo(self.repo_path)
            origin = repo.remotes.origin
            origin.pull(self.branch)
            
    def _load_resources(self) -> List[Resource]:
        """Load all resources from git repo"""
        resources = []
        
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    path = os.path.join(root, file)
                    
                    with open(path) as f:
                        docs = yaml.safe_load_all(f)
                        
                        for doc in docs:
                            if doc:
                                resource = Resource(
                                    apiVersion=doc['apiVersion'],
                                    kind=doc['kind'],
                                    metadata=doc['metadata'],
                                    spec=doc.get('spec', {})
                                )
                                resources.append(resource)
                                
        return resources
        
    async def _get_actual_state(self, 
                               desired: List[Resource]) -> Dict[str, Any]:
        """Get actual state from Kubernetes"""
        actual = {}
        
        for resource in desired:
            key = self._resource_key(resource)
            
            try:
                # Dynamic client based on resource type
                api = self._get_api_client(resource)
                
                name = resource.metadata['name']
                namespace = resource.metadata.get('namespace', 'default')
                
                if resource.kind == "Deployment":
                    obj = api.read_namespaced_deployment(name, namespace)
                elif resource.kind == "Service":
                    obj = api.read_namespaced_service(name, namespace)
                # ... handle other types
                
                actual[key] = obj
                
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    actual[key] = None
                else:
                    raise
                    
        return actual
        
    def _compare_states(self, desired: List[Resource], 
                       actual: Dict[str, Any]) -> List[SyncStatus]:
        """Compare desired vs actual state"""
        status_list = []
        
        for resource in desired:
            key = self._resource_key(resource)
            actual_resource = actual.get(key)
            
            desired_hash = self._hash_resource(resource)
            
            if actual_resource:
                # Normalize and hash actual
                actual_normalized = self._normalize_resource(actual_resource)
                actual_hash = self._hash_resource(actual_normalized)
                in_sync = desired_hash == actual_hash
            else:
                actual_hash = None
                in_sync = False
                
            status = SyncStatus(
                resource=resource,
                desired_hash=desired_hash,
                actual_hash=actual_hash,
                in_sync=in_sync,
                error=None
            )
            
            status_list.append(status)
            
        return status_list
        
    async def _apply_changes(self, sync_status: List[SyncStatus]):
        """Apply changes to make actual match desired"""
        for status in sync_status:
            if status.in_sync:
                continue
                
            try:
                if status.actual_hash is None:
                    # Create resource
                    await self._create_resource(status.resource)
                    print(f"Created {status.resource.kind}/{status.resource.metadata['name']}")
                else:
                    # Update resource
                    await self._update_resource(status.resource)
                    print(f"Updated {status.resource.kind}/{status.resource.metadata['name']}")
                    
            except Exception as e:
                status.error = str(e)
                print(f"Error syncing {status.resource.kind}/{status.resource.metadata['name']}: {e}")
                
    def _resource_key(self, resource: Resource) -> str:
        """Generate unique key for resource"""
        return f"{resource.kind}/{resource.metadata.get('namespace', 'default')}/{resource.metadata['name']}"
        
    def _hash_resource(self, resource: Any) -> str:
        """Generate hash of resource for comparison"""
        # Normalize and hash
        if isinstance(resource, Resource):
            data = {
                'spec': resource.spec,
                'metadata': {
                    k: v for k, v in resource.metadata.items()
                    if k not in ['resourceVersion', 'uid', 'generation']
                }
            }
        else:
            # Kubernetes object
            data = resource.to_dict()
            
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

# Run the GitOps controller
async def main():
    controller = GitOpsController(
        repo_url="https://github.com/myorg/gitops-config",
        branch="main",
        sync_interval=60
    )
    
    await controller.run()
```

### 3. Circuit Breaker for Control Plane

```python
import time
import asyncio
from enum import Enum
from typing import Callable, Optional, Any
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitStats:
    failures: int
    successes: int
    consecutive_failures: int
    last_failure_time: Optional[float]
    last_success_time: Optional[float]

class CircuitBreaker:
    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60,
                 expected_exception: type = Exception,
                 half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats(0, 0, 0, None, None)
        self.half_open_calls = 0
        self._lock = asyncio.Lock()
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        async with self._lock:
            if not await self._acquire_permission():
                raise Exception(f"Circuit breaker is {self.state.value}")
                
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
            
        except self.expected_exception as e:
            await self._on_failure()
            raise
            
    async def _acquire_permission(self) -> bool:
        """Check if call is allowed"""
        if self.state == CircuitState.CLOSED:
            return True
            
        elif self.state == CircuitState.OPEN:
            if await self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
            
        else:  # HALF_OPEN
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False
            
    async def _should_attempt_reset(self) -> bool:
        """Check if we should try half-open"""
        return (
            self.stats.last_failure_time and
            time.time() - self.stats.last_failure_time >= self.recovery_timeout
        )
        
    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            self.stats.successes += 1
            self.stats.last_success_time = time.time()
            self.stats.consecutive_failures = 0
            
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    # All test calls succeeded
                    self.state = CircuitState.CLOSED
                    self.stats.failures = 0
                    
    async def _on_failure(self):
        """Handle failed call"""
        async with self._lock:
            self.stats.failures += 1
            self.stats.consecutive_failures += 1
            self.stats.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                # Failed during test - reopen
                self.state = CircuitState.OPEN
                
            elif (self.state == CircuitState.CLOSED and
                  self.stats.consecutive_failures >= self.failure_threshold):
                # Too many failures - open circuit
                self.state = CircuitState.OPEN

# Use circuit breaker for control plane calls
class ControlPlaneClient:
    def __init__(self, api_endpoint: str):
        self.api_endpoint = api_endpoint
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30
        )
        
    async def get_config(self, service_name: str) -> Dict:
        """Get configuration with circuit breaker"""
        return await self.circuit_breaker.call(
            self._do_get_config,
            service_name
        )
        
    async def _do_get_config(self, service_name: str) -> Dict:
        """Actual API call"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.api_endpoint}/config/{service_name}"
            
            async with session.get(url, timeout=5) as response:
                if response.status != 200:
                    raise Exception(f"API error: {response.status}")
                    
                return await response.json()
```

## Production Control Systems

### Kubernetes Control Plane

```yaml
Architecture:
- API Server: REST API gateway
- etcd: Distributed KV store
- Scheduler: Pod placement
- Controller Manager: Control loops
- Cloud Controller: Cloud integration

Scale characteristics:
- etcd: 8GB size limit
- API: 1000 writes/sec
- Watchers: 10K concurrent
- Nodes: 5000 per cluster

Key optimizations:
- Protobuf encoding
- Watch caching
- Informer pattern
- Leader election
- Rate limiting

Common issues:
1. etcd size limits
2. API server OOM
3. Thundering herd
4. Webhook timeouts
5. Certificate rotation
```

### Envoy Control Plane (xDS)

```yaml
Protocol: xDS (discovery service)
Types:
- LDS: Listener discovery
- RDS: Route discovery
- CDS: Cluster discovery
- EDS: Endpoint discovery
- SDS: Secret discovery

Design principles:
- Eventually consistent
- Incremental updates
- Resource versioning
- ACK/NACK protocol

Scale approach:
- Delta updates
- Resource watching
- Caching layers
- Horizontal sharding
```

## Key Insights from Failures

!!! danger "Common Patterns"
    
    1. **Control plane overload cascades** - One bad config affects all
    2. **State corruption is catastrophic** - Always have recovery plan
    3. **Config size explosion** - Complexity grows exponentially
    4. **Missing rate limits** - Control planes need protection too
    5. **Poor separation fails** - Data plane must survive control failure

## Navigation

!!! tip "Continue Learning"
    
    **Practice**: [Try Control Distribution Exercises](exercises.md) →
    
    **Next Pillar**: [Distribution of Intelligence](../pillar-5-intelligence/index.md) →
    
    **Related**: [Human Interface](../../part1-axioms/axiom-7-human-interface/index.md)
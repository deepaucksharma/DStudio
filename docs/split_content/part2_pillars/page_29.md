Page 29: EXTENSION PILLAR IV – Control
Learning Objective: Control planes are the nervous system of distributed systems.
Control Plane vs Data Plane:
┌─────────────────────────────────────┐
│         CONTROL PLANE               │
│  • Service discovery                │
│  • Configuration management         │
│  • Health monitoring               │
│  • Traffic routing rules           │
│  • Autoscaling decisions          │
└────────────┬───────────────────────┘
             │ Commands
             ↓
┌─────────────────────────────────────┐
│          DATA PLANE                 │
│  • Handle user requests            │
│  • Process data                    │
│  • Forward packets                 │
│  • Execute business logic          │
│  • Store and retrieve              │
└─────────────────────────────────────┘
Orchestration vs Choreography:
Orchestration (Central Conductor):
                 Orchestrator
                /     |      \
             /        |         \
          /           |            \
    Service A    Service B    Service C
         ↑            ↑            ↑
         └────────────┴────────────┘
            Commands flow down
Examples: Kubernetes, Airflow, Temporal
Choreography (Peer Dance):
    Service A ←→ Service B
         ↓  ↖    ↗  ↓
           Service C
     
     Events trigger reactions
Examples: Event-driven, Pub/sub, Actors
Decision Framework:
Choose ORCHESTRATION when:
- Clear workflow steps
- Central visibility needed
- Rollback requirements
- Complex error handling

Choose CHOREOGRAPHY when:
- Loose coupling required
- Services independently owned
- Event-driven nature
- Scale requirements high
Control Loop Dynamics:
Observe → Orient → Decide → Act
   ↑                          ↓
   └──────── Feedback ────────┘

Observe: Metrics, logs, traces
Orient: Anomaly detection
Decide: Policy engine
Act: API calls, configs
🔧 Try This: Build a Service Registry
pythonimport time
import threading
from datetime import datetime

class ServiceRegistry:
    def __init__(self, ttl=30):
        self.services = {}
        self.ttl = ttl
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def register(self, name, host, port, metadata=None):
        with self.lock:
            self.services[name] = self.services.get(name, [])
            
            # Update or add instance
            instance = {
                'host': host,
                'port': port,
                'metadata': metadata or {},
                'last_heartbeat': time.time(),
                'healthy': True
            }
            
            # Find and update existing
            found = False
            for i, svc in enumerate(self.services[name]):
                if svc['host'] == host and svc['port'] == port:
                    self.services[name][i] = instance
                    found = True
                    break
            
            if not found:
                self.services[name].append(instance)
    
    def discover(self, name, healthy_only=True):
        with self.lock:
            if name not in self.services:
                return []
            
            instances = self.services[name]
            if healthy_only:
                instances = [i for i in instances if i['healthy']]
            
            return instances
    
    def heartbeat(self, name, host, port):
        with self.lock:
            if name in self.services:
                for instance in self.services[name]:
                    if (instance['host'] == host and 
                        instance['port'] == port):
                        instance['last_heartbeat'] = time.time()
                        instance['healthy'] = True
    
    def _cleanup_loop(self):
        while True:
            time.sleep(5)
            with self.lock:
                now = time.time()
                
                for name, instances in list(self.services.items()):
                    # Mark unhealthy
                    for instance in instances:
                        if now - instance['last_heartbeat'] > self.ttl:
                            instance['healthy'] = False
                    
                    # Remove long-dead instances
                    self.services[name] = [
                        i for i in instances 
                        if now - i['last_heartbeat'] < self.ttl * 3
                    ]
                    
                    # Clean up empty services
                    if not self.services[name]:
                        del self.services[name]

# Usage example
registry = ServiceRegistry(ttl=10)

# Service registers itself
registry.register('api', 'host1', 8080, {'version': '1.2.3'})
registry.register('api', 'host2', 8080, {'version': '1.2.3'})

# Client discovers services
services = registry.discover('api')
print(f"Found {len(services)} healthy instances")

# Simulate heartbeats
for _ in range(3):
    time.sleep(3)
    registry.heartbeat('api', 'host1', 8080)
    # host2 stops heartbeating
    
# Check health after timeout
time.sleep(12)
healthy = registry.discover('api', healthy_only=True)
print(f"Healthy instances: {len(healthy)}")
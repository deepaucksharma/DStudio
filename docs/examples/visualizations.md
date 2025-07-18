# Interactive Visualizations

This page demonstrates the advanced visualization capabilities of the Distributed Systems Compendium.

## Network Topology Visualizations

### Star Topology
<div data-viz="network-topology" data-topology="star" data-nodes="7"></div>

In a star topology, all nodes connect to a central hub. This is common in client-server architectures.

### Ring Topology
<div data-viz="network-topology" data-topology="ring" data-nodes="6"></div>

Ring topology connects each node to exactly two others, forming a circle. Used in token ring networks.

### Mesh Topology
<div data-viz="network-topology" data-topology="mesh" data-nodes="8"></div>

Mesh topology provides multiple paths between nodes, offering redundancy and fault tolerance.

## Consistency Timeline

Visualize how consistency events propagate across distributed nodes:

<div data-viz="consistency-timeline" data-events='[
  {"time": 0, "node": "Node-A", "type": "write", "value": "x=1"},
  {"time": 10, "node": "Node-B", "type": "read", "value": "x=?"},
  {"time": 20, "node": "Node-A", "type": "sync", "value": "sync", "causes": {"time": 0, "node": "Node-A"}},
  {"time": 30, "node": "Node-B", "type": "commit", "value": "x=1"},
  {"time": 40, "node": "Node-C", "type": "read", "value": "x=1"},
  {"time": 50, "node": "Node-A", "type": "write", "value": "x=2"},
  {"time": 60, "node": "Node-C", "type": "read", "value": "x=1"},
  {"time": 70, "node": "Node-A", "type": "sync", "value": "sync", "causes": {"time": 50, "node": "Node-A"}},
  {"time": 80, "node": "Node-B", "type": "commit", "value": "x=2"},
  {"time": 90, "node": "Node-C", "type": "commit", "value": "x=2"}
]'></div>

## Load Distribution

Monitor real-time load distribution across servers:

<div data-viz="load-distribution" data-animate="true" data-distribution='[
  {"server": "Server-1", "load": 45},
  {"server": "Server-2", "load": 72},
  {"server": "Server-3", "load": 38},
  {"server": "Server-4", "load": 85},
  {"server": "Server-5", "load": 61}
]'></div>

The red dashed line indicates the critical threshold (80%). Servers above this line may need load balancing.

## Latency Heatmap

Visualize network latency between different regions:

<div data-viz="latency-heatmap" 
     data-regions='["US-East", "US-West", "EU-West", "Asia-Pacific", "South-America"]'
     data-latencies='[
       {"from": "US-East", "to": "US-East", "value": 1},
       {"from": "US-East", "to": "US-West", "value": 40},
       {"from": "US-East", "to": "EU-West", "value": 85},
       {"from": "US-East", "to": "Asia-Pacific", "value": 180},
       {"from": "US-East", "to": "South-America", "value": 120},
       {"from": "US-West", "to": "US-East", "value": 40},
       {"from": "US-West", "to": "US-West", "value": 1},
       {"from": "US-West", "to": "EU-West", "value": 140},
       {"from": "US-West", "to": "Asia-Pacific", "value": 120},
       {"from": "US-West", "to": "South-America", "value": 160},
       {"from": "EU-West", "to": "US-East", "value": 85},
       {"from": "EU-West", "to": "US-West", "value": 140},
       {"from": "EU-West", "to": "EU-West", "value": 1},
       {"from": "EU-West", "to": "Asia-Pacific", "value": 220},
       {"from": "EU-West", "to": "South-America", "value": 190},
       {"from": "Asia-Pacific", "to": "US-East", "value": 180},
       {"from": "Asia-Pacific", "to": "US-West", "value": 120},
       {"from": "Asia-Pacific", "to": "EU-West", "value": 220},
       {"from": "Asia-Pacific", "to": "Asia-Pacific", "value": 1},
       {"from": "Asia-Pacific", "to": "South-America", "value": 340},
       {"from": "South-America", "to": "US-East", "value": 120},
       {"from": "South-America", "to": "US-West", "value": 160},
       {"from": "South-America", "to": "EU-West", "value": 190},
       {"from": "South-America", "to": "Asia-Pacific", "value": 340},
       {"from": "South-America", "to": "South-America", "value": 1}
     ]'></div>

## Failure Cascade Animation

Watch how failures propagate through a system with dependencies:

<div data-viz="failure-cascade" data-animate="true" 
     data-nodes='[
       {"id": "api", "name": "API", "status": "healthy"},
       {"id": "auth", "name": "Auth", "status": "healthy"},
       {"id": "db", "name": "Database", "status": "healthy"},
       {"id": "cache", "name": "Cache", "status": "healthy"},
       {"id": "queue", "name": "Queue", "status": "healthy"},
       {"id": "worker", "name": "Worker", "status": "healthy"}
     ]'
     data-dependencies='[
       {"source": "api", "target": "auth"},
       {"source": "api", "target": "db"},
       {"source": "api", "target": "cache"},
       {"source": "auth", "target": "db"},
       {"source": "worker", "target": "queue"},
       {"source": "worker", "target": "db"}
     ]'></div>

The animation shows how a failure in one component can cascade to dependent services. This demonstrates the importance of circuit breakers and graceful degradation.

## Usage in Your Documentation

To use these visualizations in your own pages, include a div with the appropriate data attributes:

```html
<!-- Network Topology -->
<div data-viz="network-topology" 
     data-topology="star|ring|mesh" 
     data-nodes="6"></div>

<!-- Consistency Timeline -->
<div data-viz="consistency-timeline" 
     data-events='[{"time": 0, "node": "A", "type": "write", "value": "x=1"}]'></div>

<!-- Load Distribution -->
<div data-viz="load-distribution" 
     data-animate="true"
     data-distribution='[{"server": "S1", "load": 50}]'></div>

<!-- Latency Heatmap -->
<div data-viz="latency-heatmap" 
     data-regions='["Region1", "Region2"]'
     data-latencies='[{"from": "Region1", "to": "Region2", "value": 50}]'></div>

<!-- Failure Cascade -->
<div data-viz="failure-cascade" 
     data-animate="true"
     data-nodes='[{"id": "n1", "name": "Node1", "status": "healthy"}]'
     data-dependencies='[{"source": "n1", "target": "n2"}]'></div>
```

The visualization engine automatically detects and enhances these containers when the page loads.
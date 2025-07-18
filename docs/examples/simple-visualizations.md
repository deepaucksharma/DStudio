# Simple Visualizations

This page demonstrates lightweight visualization capabilities that work without external dependencies.

## Network Diagrams

### Star Topology
<div data-viz="network-simple" data-type="star" data-nodes="7"></div>

Star topology is commonly used in client-server architectures where all communication goes through a central hub.

### Ring Topology
<div data-viz="network-simple" data-type="ring" data-nodes="6"></div>

Ring topology connects each node to exactly two others, forming a circular data path.

## Load Distribution Chart

<div data-viz="bar-chart" data-values='[
  {"label": "Server-1", "value": 45},
  {"label": "Server-2", "value": 72},
  {"label": "Server-3", "value": 38},
  {"label": "Server-4", "value": 85},
  {"label": "Server-5", "value": 61}
]'></div>

The color coding indicates load levels:
- 🟢 Green: Under 60% (healthy)
- 🟡 Yellow: 60-80% (warning)
- 🔴 Red: Over 80% (critical)

## Event Timeline

<div data-viz="timeline" data-events='[
  {"time": 0, "node": "Node-A", "type": "write", "value": "x=1"},
  {"time": 10, "node": "Node-B", "type": "read", "value": "x=?"},
  {"time": 20, "node": "Node-A", "type": "sync", "value": "sync started"},
  {"time": 30, "node": "Node-B", "type": "commit", "value": "x=1"},
  {"time": 40, "node": "Node-C", "type": "read", "value": "x=1"}
]'></div>

This timeline shows how consistency events propagate across distributed nodes over time.

## Usage

To use these visualizations in your documentation:

```html
<!-- Network Diagram -->
<div data-viz="network-simple" 
     data-type="star|ring" 
     data-nodes="5"></div>

<!-- Bar Chart -->
<div data-viz="bar-chart" 
     data-values='[{"label": "Item1", "value": 50}]'></div>

<!-- Timeline -->
<div data-viz="timeline" 
     data-events='[{"time": 0, "node": "A", "type": "write", "value": "data"}]'></div>
```

These visualizations are automatically enhanced when the page loads and work across all modern browsers without requiring external libraries.
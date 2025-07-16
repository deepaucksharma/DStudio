Page 30: Control-Plane vs Data-Plane Diagram
Service Mesh Architecture Example:
┌─────────────────────── CONTROL PLANE ───────────────────────┐
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Policy Engine│  │Config Server │  │ Service Registry │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘ │
│         │                  │                    │           │
│         └──────────────────┼────────────────────┘           │
│                            ↓                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │            Control Plane API (gRPC)                  │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │ xDS APIs
═══════════════════════════════╪═══════════════════════════════
                              ↓
┌─────────────────────── DATA PLANE ──────────────────────────┐
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Service A     │  │   Service B     │                  │
│  │  ┌───────────┐ │  │  ┌───────────┐ │                  │
│  │  │   App     │ │  │  │   App     │ │                  │
│  │  └─────┬─────┘ │  │  └─────┬─────┘ │                  │
│  │        ↓       │  │        ↓       │                  │
│  │  ┌───────────┐ │  │  ┌───────────┐ │                  │
│  │  │Envoy Proxy│ │  │  │Envoy Proxy│ │                  │
│  │  └─────┬─────┘ │  │  └─────┬─────┘ │                  │
│  └────────┼────────┘  └────────┼────────┘                  │
│           │                    │                            │
│           └────────────────────┘                            │
│                   Traffic Flow                              │
└──────────────────────────────────────────────────────────────┘
Control/Data Plane Separation Benefits:

Independent scaling: Control plane can be smaller
Failure isolation: Data plane continues if control fails
Update safety: Control changes don't affect traffic
Security: Different access controls

Real Example: Envoy Configuration:
yaml# Control Plane pushes this config
static_resources:
  listeners:
  - name: listener_0
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 10000
    filter_chains:
    - filters:
      - name: envoy.http_connection_manager
        typed_config:
          route_config:
            virtual_hosts:
            - name: backend
              domains: ["*"]
              routes:
              - match: 
                  prefix: "/"
                route:
                  weighted_clusters:
                    clusters:
                    - name: service_blue
                      weight: 90
                    - name: service_green
                      weight: 10  # Canary!
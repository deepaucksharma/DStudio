Page 50: Service Mesh
The network is now programmable
THE PROBLEM
Microservices create networking complexity:
- Service discovery
- Load balancing  
- Encryption (mTLS)
- Observability
- Retry/timeout/circuit breaking
Each service reimplements these
THE SOLUTION
Sidecar proxy handles all network concerns:

App Container ←→ Envoy Proxy ←→ Network ←→ Envoy Proxy ←→ App Container
                     ↓                           ↓
                Control Plane (config, policies, certificates)
Core Service Mesh Features:
1. TRAFFIC MANAGEMENT
   - Load balancing strategies
   - Canary deployments (10% to v2)
   - Circuit breaking per service
   - Retries with jitter

2. SECURITY
   - Automatic mTLS between services
   - Service identity (SPIFFE)
   - Policy enforcement
   - Zero-trust networking

3. OBSERVABILITY  
   - Distributed tracing injection
   - Metrics collection
   - Access logging
   - Service topology maps
PSEUDO CODE IMPLEMENTATION
ServiceMeshProxy:
    config = load_from_control_plane()
    
    on_request(request):
        // Add tracing headers
        request.headers['x-trace-id'] = generate_trace_id()
        
        // Service discovery
        endpoints = discover_service(request.destination)
        
        // Load balancing
        endpoint = load_balance(endpoints, config.lb_policy)
        
        // Circuit breaking
        if circuit_breaker.is_open(endpoint):
            return error_503_service_unavailable()
            
        // mTLS
        connection = establish_mtls(endpoint, service_identity)
        
        // Send with retry
        response = retry_with_backoff(
            send_request(connection, request),
            config.retry_policy
        )
        
        // Metrics
        record_metrics(request, response)
        
        return response

ControlPlane:
    on_config_change():
        new_config = generate_proxy_configs()
        for proxy in all_proxies:
            push_config(proxy, new_config)
    
    on_certificate_rotation():
        new_certs = issue_certificates()
        distribute_certs(new_certs)
Service Mesh Patterns:
1. CANARY DEPLOYMENT
   route_rules:
     - match: headers['x-user-group'] == 'beta'
       route: service-v2
     - default:
       weighted:
         - service-v1: 90%
         - service-v2: 10%

2. CIRCUIT BREAKER CONFIG
   outlier_detection:
     consecutive_errors: 5
     interval: 30s
     base_ejection_time: 30s
     max_ejection_percent: 50

3. RETRY POLICY
   retry:
     attempts: 3
     timeout: 10s
     retry_on: "5xx,reset,refused"
     backoff:
       base_interval: 1s
       max_interval: 10s
✓ CHOOSE THIS WHEN:

Many microservices (>10)
Need uniform network policies
Zero-trust security required
Complex traffic management
Consistent observability needed

⚠️ BEWARE OF:

Additional latency (proxy hop)
Resource overhead (sidecar per pod)
Control plane becomes critical
Debugging complexity
Version compatibility issues

REAL EXAMPLES

Google: Istio on GKE
Netflix: Custom mesh for streaming
Lyft: Envoy originated here

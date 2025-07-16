Page 62: Observability Sidecar
Every service needs a copilot
THE PROBLEM
Observability requirements:
- Metrics collection
- Log aggregation
- Trace injection
- Health checking

Each service reimplements these
THE SOLUTION
Sidecar container handles observability:

Pod:
├── Application Container
│   └── Business logic only
└── Sidecar Container
    ├── Metrics scraping
    ├── Log forwarding
    ├── Trace injection
    └── Health proxy
PSEUDO CODE IMPLEMENTATION
ObservabilitySidecar:
    components = {
        'metrics': MetricsCollector(),
        'logs': LogForwarder(),
        'traces': TraceInjector(),
        'health': HealthProxy()
    }
    
    start():
        // Intercept application traffic
        setup_iptables_redirect()
        
        // Start components
        for component in components.values():
            component.start()
            
        // Main proxy loop
        while running:
            request = intercept_request()
            
            // Inject tracing
            request = inject_trace_headers(request)
            
            // Forward to app
            response = forward_to_app(request)
            
            // Collect metrics
            record_request_metrics(request, response)
            
            return response

MetricsCollector:
    scrape_application_metrics():
        // Prometheus format
        metrics = http_get('http://localhost:8080/metrics')
        
        // Enrich with metadata
        enriched = add_pod_labels(metrics)
        
        // Forward to aggregator
        prometheus_pushgateway.push(enriched)

LogForwarder:
    tail_and_forward():
        // Tail container logs
        for line in tail('/var/log/app/*.log'):
            // Parse and structure
            structured = parse_log_line(line)
            
            // Add context
            structured['pod'] = POD_NAME
            structured['node'] = NODE_NAME
            structured['trace_id'] = extract_trace_id(line)
            
            // Ship to aggregator
            fluentd.forward(structured)

TraceInjector:
    inject_headers(request):
        // Continue or create trace
        trace_id = request.headers.get('x-trace-id') 
                  || generate_trace_id()
        
        span_id = generate_span_id()
        parent_span = request.headers.get('x-span-id')
        
        // Inject headers
        request.headers['x-trace-id'] = trace_id
        request.headers['x-span-id'] = span_id
        request.headers['x-parent-span'] = parent_span
        
        // Record span
        tracer.start_span(span_id, parent_span)
        
        return request
Sidecar Patterns:
1. AMBASSADOR
   App → Sidecar → External Service
   (Protocol translation, retry, auth)

2. ADAPTER
   App → Sidecar → Monitoring
   (Metric format conversion)

3. PROXY
   Internet → Sidecar → App
   (TLS termination, rate limiting)
✓ CHOOSE THIS WHEN:

Kubernetes environment
Polyglot services
Standardized observability
Separation of concerns
Service mesh adoption

⚠️ BEWARE OF:

Resource overhead
Startup coordination
Version compatibility
Network complexity
Debugging sidecar issues

REAL EXAMPLES

Envoy: Universal sidecar
Linkerd: Service mesh sidecar
Fluentbit: Log forwarding sidecar

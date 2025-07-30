# Episode 28: Cloudflare's Edge Computing Revolution - 71 Million Requests Per Second and the Future of the Internet

## Introduction (10 minutes)

**Alex (Host):** Welcome back to Architecture Deep Dives! Today, we're exploring how Cloudflare handles mind-boggling scale - 71 million requests per second during DDoS attacks, Workers running at the edge in 310 cities, and protecting 20% of the internet. I'm joined by Dr. Sarah Chen, Principal Engineer at Cloudflare who architected their edge computing platform.

**Sarah (Expert):** Thanks Alex! What excites me most is we're not just handling traffic - we're fundamentally reimagining where computation happens on the internet.

**Alex:** Let's start with that incredible DDoS number - 71 million requests per second. How is that even possible?

**Sarah:** That was during the Mantis botnet attack in 2022. To put it in perspective:
- 71.1 million requests per second peak
- 26 million requests per second sustained
- Originated from 5,067 devices
- Across 1,476 different networks
- In 121 countries

And here's the kicker - we mitigated it without any customer impact.

**Alex:** Walk us through how you architect for that scale.

## Part 1: The Architecture Story (1 hour)

### Chapter 1: Anycast and Global Load Distribution (20 minutes)

**Sarah:** The foundation is our Anycast network. Unlike traditional hosting where an IP address maps to one location, with Anycast, one IP address routes to our nearest data center out of 310 globally.

```yaml
# Cloudflare's Anycast Architecture
network_topology:
  total_locations: 310
  countries: 120
  network_capacity: 192_tbps
  
  anycast_ranges:
    ipv4: 
      - 104.16.0.0/12
      - 172.64.0.0/13
      - 198.41.128.0/17
    ipv6:
      - 2606:4700::/32
      - 2803:f800::/32
      - 2c0f:f248::/32
  
  routing_strategy:
    primary: bgp_shortest_path
    secondary: capacity_aware_routing
    tertiary: latency_optimized_paths
```

**Alex:** How does the traffic actually get distributed during an attack?

**Sarah:** Here's where it gets interesting. BGP and our intelligent routing:

```python
# Intelligent Traffic Distribution
class EdgeRouter:
    def __init__(self):
        self.locations = self.load_edge_locations()
        self.capacity_model = CapacityPredictor()
        
    def route_request(self, request, current_load):
        # Step 1: Find nearby locations via BGP
        nearby_pops = self.get_nearby_pops(request.source_ip)
        
        # Step 2: Check capacity at each PoP
        available_pops = []
        for pop in nearby_pops:
            if self.can_handle_request(pop, request):
                available_pops.append({
                    'location': pop,
                    'latency': self.estimate_latency(request.source_ip, pop),
                    'capacity': pop.available_capacity(),
                    'health_score': pop.health_score()
                })
        
        # Step 3: Intelligent selection
        if self.is_likely_attack_traffic(request):
            # For attack traffic, prioritize capacity
            return self.select_by_capacity(available_pops)
        else:
            # For legitimate traffic, prioritize latency
            return self.select_by_latency(available_pops)
    
    def is_likely_attack_traffic(self, request):
        features = self.extract_features(request)
        attack_probability = self.ml_classifier.predict(features)
        return attack_probability > 0.7
```

### Chapter 2: DDoS Mitigation Architecture (20 minutes)

**Sarah:** DDoS mitigation happens in multiple layers, starting at the network edge:

```rust
// Kernel-level DDoS Mitigation (XDP/eBPF)
use redbpf_probes::xdp::prelude::*;

#[xdp]
pub fn ddos_filter(ctx: XdpContext) -> XdpResult {
    let (ip_header, transport) = match parse_headers(&ctx) {
        Ok(headers) => headers,
        Err(_) => return Ok(XdpAction::Drop),
    };
    
    // Layer 1: Rate limiting per source
    let source_ip = ip_header.source_addr();
    let current_rate = RATE_MAP.get(&source_ip).unwrap_or(&0);
    
    if *current_rate > THRESHOLD_PPS {
        // Drop packet in kernel, never reaches userspace
        return Ok(XdpAction::Drop);
    }
    
    // Layer 2: Pattern matching
    if is_attack_pattern(&ctx) {
        // Add to blocklist and drop
        BLOCKLIST.insert(&source_ip, &1, 0)?;
        return Ok(XdpAction::Drop);
    }
    
    // Layer 3: SYN flood protection
    if is_syn_flood(&transport, source_ip) {
        // Activate SYN cookies
        return handle_syn_cookie(&ctx, &ip_header);
    }
    
    // Pass legitimate traffic
    Ok(XdpAction::Pass)
}

// Pattern detection in eBPF
#[inline(always)]
fn is_attack_pattern(ctx: &XdpContext) -> bool {
    // Check for common attack signatures
    let data = ctx.data();
    let data_end = ctx.data_end();
    
    // NTP amplification check
    if let Some(udp) = get_udp_header(data, data_end) {
        if udp.dest_port == 123 && payload_contains_monlist(data, data_end) {
            return true;
        }
    }
    
    // DNS amplification check
    if let Some(dns) = parse_dns_query(data, data_end) {
        if dns.query_type == ANY && dns.payload_size > 512 {
            return true;
        }
    }
    
    false
}
```

**Alex:** 71 million packets per second - that's per data center or globally?

**Sarah:** That's globally, but during that attack, some data centers saw 3-4 million PPS. Here's how we handle it:

```go
// Distributed DDoS Mitigation System
package ddos

type MitigationPipeline struct {
    kernelFilter   *XDPFilter
    edgeFilter     *EdgeFilter
    mlClassifier   *MLClassifier
    globalView     *GlobalCoordinator
}

func (m *MitigationPipeline) ProcessPacket(pkt *Packet) Decision {
    // Already filtered in kernel? (XDP/eBPF)
    // This code handles what passes through
    
    // Stage 1: Edge-local decisions (microseconds)
    if decision := m.edgeFilter.QuickDecision(pkt); decision != UNKNOWN {
        return decision
    }
    
    // Stage 2: ML classification (milliseconds)
    features := extractPacketFeatures(pkt)
    if m.mlClassifier.IsAttackTraffic(features) > 0.95 {
        m.updateLocalRules(pkt)
        return DROP
    }
    
    // Stage 3: Global correlation (10s of milliseconds)
    pattern := m.globalView.CorrelateTraffic(pkt)
    if pattern.IsCoordinatedAttack() {
        m.deployGlobalMitigation(pattern)
        return DROP
    }
    
    return ACCEPT
}

// Global coordination across all PoPs
func (m *MitigationPipeline) deployGlobalMitigation(pattern AttackPattern) {
    // Generate mitigation rules
    rules := m.generateMitigationRules(pattern)
    
    // Deploy to all edges within 1 second
    deployment := &RuleDeployment{
        Rules:     rules,
        Priority:  CRITICAL,
        ExpiresIn: 5 * time.Minute,
    }
    
    // Use Quicksilver for instant global propagation
    m.globalView.PropagateRules(deployment)
}
```

### Chapter 3: Workers Platform Architecture (20 minutes)

**Sarah:** Now let's talk about Workers - our edge computing platform. Code runs in 310 cities, within 50ms of 95% of the world's population.

```javascript
// Cloudflare Worker Example
export default {
  async fetch(request, env, ctx) {
    // This runs at the edge, not in a central data center
    const country = request.cf.country;
    
    // Edge-side personalization
    if (country === 'JP') {
      return handleJapaneseUser(request, env);
    }
    
    // Edge-side A/B testing
    const bucket = await getABTestBucket(request, env.KV);
    if (bucket === 'experiment') {
      return serveExperiment(request, env);
    }
    
    // Edge-side caching with compute
    const cached = await env.CACHE.match(request);
    if (cached) {
      return addPersonalizedHeaders(cached, request);
    }
    
    // Origin fetch with modification
    const response = await fetch(request);
    ctx.waitUntil(
      processAnalytics(request, response, env.ANALYTICS)
    );
    
    return response;
  }
};
```

**Alex:** How do you isolate Workers at that scale?

**Sarah:** V8 isolates - not containers, not VMs. Here's the architecture:

```rust
// Workers Runtime Architecture
pub struct WorkersRuntime {
    isolate_pool: IsolatePool,
    scheduler: WorkScheduler,
    resource_limiter: ResourceLimiter,
}

impl WorkersRuntime {
    pub async fn handle_request(&self, req: Request) -> Response {
        // Get or create isolate (microseconds, not seconds)
        let isolate = self.isolate_pool.get_isolate(&req.script_id).await?;
        
        // Set resource limits
        isolate.set_limits(ResourceLimits {
            cpu_time: Duration::from_millis(50),
            memory: 128 * MB,
            subrequests: 50,
        });
        
        // Execute with automatic termination
        let result = timeout(
            Duration::from_millis(50),
            isolate.execute(req)
        ).await;
        
        match result {
            Ok(response) => response,
            Err(TimeoutError) => Response::error("CPU time exceeded", 524),
            Err(MemoryError) => Response::error("Memory limit exceeded", 524),
        }
    }
}

// Isolate pooling for efficiency
pub struct IsolatePool {
    warm_isolates: HashMap<ScriptId, Vec<V8Isolate>>,
    cold_start_time: Histogram,
}

impl IsolatePool {
    pub async fn get_isolate(&self, script_id: &ScriptId) -> Result<V8Isolate> {
        // Check warm pool first (sub-millisecond)
        if let Some(isolate) = self.warm_isolates.get(script_id).pop() {
            self.cold_start_time.record(0);
            return Ok(isolate);
        }
        
        // Cold start (5-10ms)
        let start = Instant::now();
        let isolate = self.create_isolate(script_id).await?;
        self.cold_start_time.record(start.elapsed().as_micros());
        
        Ok(isolate)
    }
}
```

## Part 2: Implementation Deep Dive (1 hour)

### Chapter 4: BGP and Traffic Engineering (20 minutes)

**Sarah:** Let's dive into how we use BGP for both normal routing and DDoS mitigation:

```python
# BGP Traffic Engineering
class BGPController:
    def __init__(self):
        self.bgp_sessions = self.establish_sessions()
        self.route_optimizer = RouteOptimizer()
        self.attack_detector = AttackDetector()
        
    def advertise_routes(self):
        """Advertise our prefixes with intelligent communities"""
        for prefix in self.our_prefixes:
            announcement = BGPAnnouncement(
                prefix=prefix,
                as_path=[13335],  # Cloudflare's ASN
                communities=self.calculate_communities(prefix)
            )
            
            # Advertise to all peers
            for session in self.bgp_sessions:
                session.announce(announcement)
    
    def calculate_communities(self, prefix):
        """Dynamic community calculation based on conditions"""
        communities = []
        
        # Geographic steering
        if self.should_regionalize(prefix):
            communities.extend([
                "13335:region:us-west",
                "13335:region:eu-central"
            ])
        
        # Capacity-based steering  
        if self.is_under_attack(prefix):
            communities.append("13335:blackhole")  # Last resort
        elif self.high_load(prefix):
            communities.append("13335:anycast:spread")
        
        return communities
    
    def handle_attack_traffic(self, attack_profile):
        """Real-time BGP manipulation during attack"""
        if attack_profile.severity > AttackSeverity.CRITICAL:
            # Withdraw routes from overwhelmed locations
            for pop in self.overloaded_pops():
                self.withdraw_routes_from_pop(pop)
            
            # Steer traffic to high-capacity locations
            self.advertise_to_scrubbing_centers(attack_profile)
        
        # More specific advertisements to control traffic flow
        self.advertise_deaggregated_prefixes(attack_profile.target_ips)
```

**Alex:** How quickly can you reroute traffic during an attack?

**Sarah:** BGP convergence is typically 30-90 seconds, but we have faster mechanisms:

```go
// Quicksilver - Cloudflare's Control Plane
type Quicksilver struct {
    nodes map[string]*EdgeNode
    raft  *RaftConsensus
}

func (q *Quicksilver) DeployMitigation(rule MitigationRule) error {
    // Phase 1: Prepare (1-5ms)
    prepare := &PrepareMessage{
        Rule:      rule,
        Version:   q.nextVersion(),
        Timestamp: time.Now(),
    }
    
    // Phase 2: Global consensus (10-50ms)
    if err := q.raft.Propose(prepare); err != nil {
        return err
    }
    
    // Phase 3: Parallel deployment (50-200ms total)
    errors := make(chan error, len(q.nodes))
    for _, node := range q.nodes {
        go func(n *EdgeNode) {
            errors <- n.ApplyRule(rule)
        }(node)
    }
    
    // Wait for majority success
    successCount := 0
    for i := 0; i < len(q.nodes); i++ {
        if err := <-errors; err == nil {
            successCount++
        }
        
        // Continue once we have majority
        if successCount > len(q.nodes)/2 {
            break
        }
    }
    
    return nil
}

// Edge node rule application
func (n *EdgeNode) ApplyRule(rule MitigationRule) error {
    // Update XDP/eBPF programs (microseconds)
    if err := n.updateKernelFilters(rule); err != nil {
        return err
    }
    
    // Update userspace filters (milliseconds)
    n.filterEngine.UpdateRules(rule)
    
    // Update Workers KV for application-layer rules
    return n.workersKV.Put(rule.Key(), rule.Serialize())
}
```

### Chapter 5: WASM Isolation in Workers (20 minutes)

**Sarah:** Workers now support WASM, enabling languages beyond JavaScript:

```rust
// WASM Worker Example (Rust)
use worker::*;

#[event(fetch)]
pub async fn main(req: Request, env: Env, _ctx: Context) -> Result<Response> {
    // Parse request at the edge
    let url = req.url()?;
    
    // Edge-side rate limiting
    let client_ip = req.headers().get("CF-Connecting-IP")?
        .ok_or_else(|| Error::from("No client IP"))?;
    
    let rate_limit = RateLimiter::new(&env);
    if !rate_limit.check(&client_ip, 100).await? {
        return Response::error("Rate limited", 429);
    }
    
    // Edge-side data processing
    match url.path() {
        "/api/transform" => handle_transformation(req, env).await,
        "/api/aggregate" => handle_aggregation(req, env).await,
        _ => fetch_from_origin(req, env).await,
    }
}

async fn handle_transformation(mut req: Request, env: Env) -> Result<Response> {
    // Read body at edge
    let body = req.json::<TransformRequest>().await?;
    
    // CPU-intensive operation at edge
    let transformed = transform_data(&body.data);
    
    // Store result in Durable Object
    let namespace = env.durable_object("TRANSFORMER")?;
    let stub = namespace.id_from_name(&body.user_id)?.get_stub()?;
    
    stub.fetch_with_request(
        Request::new_with_init(
            "https://fake-host/store",
            RequestInit::new()
                .with_method(Method::Post)
                .with_body(Some(JsValue::from_str(&transformed)))?
        )?
    ).await
}
```

**Alex:** How does WASM isolation compare to V8 isolates?

**Sarah:** Different trade-offs. Here's the architecture:

```rust
// WASM Isolation Architecture
pub struct WasmRuntime {
    engine: wasmtime::Engine,
    compiler: Compiler,
    instance_pool: InstancePool,
}

impl WasmRuntime {
    pub fn instantiate(&self, wasm_bytes: &[u8]) -> Result<Instance> {
        // Compile with streaming compilation
        let module = self.compile_streaming(wasm_bytes)?;
        
        // Create instance with limits
        let instance = Instance::new(
            &self.engine,
            &module,
            &self.create_limits(),
        )?;
        
        // Bind imports (host functions)
        self.bind_imports(&instance)?;
        
        Ok(instance)
    }
    
    fn create_limits(&self) -> Limits {
        Limits {
            memory_pages: 2048,        // 128MB max
            table_elements: 10000,     
            instances: 1000,
            memories: 1,
            tables: 5,
            globals: 1000,
            functions: 10000,
            data_segments: 1000,
            element_segments: 1000,
            // Linear memory growth
            memory_growth_delta: 1,    // Grow 1 page at a time
        }
    }
    
    pub fn execute_with_timeout(&self, instance: &Instance, timeout: Duration) -> Result<Response> {
        // Create fuel-based execution limits
        let mut store = Store::new(&self.engine, ());
        store.add_fuel(1_000_000)?; // ~50ms of CPU time
        
        // Execute with interrupt handle
        let handle = store.interrupt_handle()?;
        let timeout_handle = handle.clone();
        
        // Timeout thread
        thread::spawn(move || {
            thread::sleep(timeout);
            timeout_handle.interrupt();
        });
        
        // Execute WASM
        let func = instance.get_typed_func::<(), ()>(&mut store, "fetch")?;
        match func.call(&mut store, ()) {
            Ok(result) => Ok(result),
            Err(Trap::Interrupt) => Err(Error::Timeout),
            Err(e) => Err(Error::Execution(e)),
        }
    }
}
```

### Chapter 6: Durable Objects Architecture (20 minutes)

**Sarah:** Durable Objects provide distributed state at the edge:

```javascript
// Durable Object for Collaborative Editing
export class DocumentEditor {
  constructor(state, env) {
    this.state = state;
    this.env = env;
    // Guaranteed to run in single threaded environment
    this.document = null;
    this.clients = new Map();
  }

  async fetch(request) {
    const url = new URL(request.url);
    
    switch (url.pathname) {
      case "/websocket":
        return this.handleWebSocket(request);
      case "/document":
        return this.getDocument();
      case "/operation":
        return this.applyOperation(request);
    }
  }
  
  async handleWebSocket(request) {
    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    
    await this.state.acceptWebSocket(server);
    
    // Track connected clients
    const clientId = crypto.randomUUID();
    this.clients.set(clientId, {
      websocket: server,
      lastSeen: Date.now()
    });
    
    // Send current document state
    server.send(JSON.stringify({
      type: 'document',
      content: await this.getDocumentContent()
    }));
    
    return new Response(null, {
      status: 101,
      webSocket: client
    });
  }
  
  async applyOperation(request) {
    const operation = await request.json();
    
    // Apply operational transform
    const transformed = await this.transformOperation(operation);
    
    // Store in transactional storage
    await this.state.storage.put('document', transformed);
    
    // Broadcast to all clients
    this.broadcast({
      type: 'operation',
      operation: transformed
    });
    
    return new Response('OK');
  }
  
  broadcast(message) {
    const msg = JSON.stringify(message);
    for (const [id, client] of this.clients) {
      try {
        client.websocket.send(msg);
      } catch (err) {
        // Client disconnected
        this.clients.delete(id);
      }
    }
  }
}
```

**Alex:** How does Durable Objects guarantee consistency?

**Sarah:** Single-threaded execution with transactional storage:

```typescript
// Durable Objects Consistency Model
class DurableObjectsRuntime {
  private objects: Map<string, DurableObjectInstance> = new Map();
  
  async routeRequest(objectId: string, request: Request): Promise<Response> {
    // Step 1: Find object location (consistent hashing)
    const location = this.findObjectLocation(objectId);
    
    // Step 2: Route to correct data center if needed
    if (location !== this.currentLocation) {
      return this.forwardRequest(location, objectId, request);
    }
    
    // Step 3: Get or create object instance
    let instance = this.objects.get(objectId);
    if (!instance) {
      instance = await this.createInstance(objectId);
      this.objects.set(objectId, instance);
    }
    
    // Step 4: Execute in single-threaded context
    return this.executeInActor(instance, request);
  }
  
  private async executeInActor(
    instance: DurableObjectInstance, 
    request: Request
  ): Promise<Response> {
    // Acquire exclusive lock
    await instance.lock.acquire();
    
    try {
      // Load state if needed
      if (!instance.initialized) {
        await instance.loadState();
        instance.initialized = true;
      }
      
      // Execute request handler
      const response = await instance.fetch(request);
      
      // Persist state changes transactionally
      if (instance.stateChanged) {
        await instance.persistState();
      }
      
      return response;
    } finally {
      instance.lock.release();
    }
  }
  
  // Automatic migration on failure
  private async handleObjectFailure(objectId: string): Promise<void> {
    const newLocation = this.selectNewLocation(objectId);
    
    // Migrate state
    const state = await this.loadObjectState(objectId);
    await this.migrateState(objectId, state, newLocation);
    
    // Update routing table
    await this.updateRoutingTable(objectId, newLocation);
  }
}
```

## Part 3: Production War Stories (40 minutes)

### Chapter 7: The Mantis Botnet Attack (15 minutes)

**Sarah:** June 2022, we saw traffic ramping up unusually fast. Within minutes, we hit 71.1 million requests per second.

**Alex:** Walk me through those critical minutes.

**Sarah:** Here's the timeline:

```yaml
# Mantis Botnet Attack Timeline
timeline:
  "14:32:00": "Normal traffic patterns"
  "14:32:30": "Slight uptick detected - 2M RPS"
  "14:33:00": "Rapid escalation - 15M RPS"
  "14:33:30": "Attack confirmed - 35M RPS"
  "14:34:00": "Peak traffic - 71.1M RPS"
  "14:34:30": "Mitigation fully active"
  "14:35:00": "Traffic normalized - attack blocked"

attack_characteristics:
  type: "HTTPS flood"
  sources: 5067
  countries: 121
  requests_per_bot: "5,000-10,000 RPS"
  sophistication: "Very high"
  
mitigation_deployed:
  - kernel_level_filtering    # XDP/eBPF
  - pattern_recognition       # ML models
  - geographic_distribution   # Anycast spread
  - rate_limiting            # Per-source limits
  - challenge_pages          # Bot verification
```

**Sarah:** The key was our autonomous systems kicked in immediately:

```go
// Autonomous Mitigation During Mantis
func (a *AttackMitigator) HandleMantisAttack() {
    // Detection within 500ms
    detection := a.anomalyDetector.Detect(TrafficPattern{
        RPS:             71_100_000,
        UniqueIPs:       5_067,
        RequestPattern:  "/*",
        UserAgents:      []string{"legitimate-looking"},
    })
    
    if detection.Confidence > 0.99 {
        // Deploy immediate mitigations
        mitigations := []Mitigation{
            // 1. Kernel-level drops
            KernelFilter{
                Type:      "xdp",
                Action:    "drop",
                Condition: "rate > 1000",
            },
            
            // 2. Activate challenge
            ChallengeFilter{
                Type:       "js_challenge",
                Complexity: "high",
                ValidFor:   24 * time.Hour,
            },
            
            // 3. Geographic spread
            BGPAction{
                Type:        "withdraw",
                Locations:   a.getOverloadedPops(),
                Duration:    5 * time.Minute,
            },
        }
        
        a.deployGlobally(mitigations)
    }
}
```

### Chapter 8: The Encrypted Attack Evolution (15 minutes)

**Sarah:** Attackers evolved. They started using encrypted payloads to evade detection:

```rust
// Dealing with Encrypted DDoS
impl EncryptedAttackMitigation {
    fn detect_encrypted_attack(&self, flow: &Flow) -> bool {
        // Can't inspect payload, so use traffic analysis
        let features = TrafficFeatures {
            packet_sizes: self.analyze_packet_sizes(flow),
            timing_pattern: self.analyze_timing(flow),
            tls_fingerprint: self.extract_ja3(flow),
            behavioral_score: self.analyze_behavior(flow),
        };
        
        // ML model trained on encrypted attack patterns
        self.encrypted_attack_model.predict(&features) > 0.9
    }
    
    fn mitigate_without_decryption(&self, flow: &Flow) {
        // Rate limiting based on TLS fingerprint
        if let Some(ja3) = flow.tls_fingerprint() {
            self.rate_limiter.limit_by_ja3(ja3, 100);
        }
        
        // Behavioral analysis
        if self.is_automated_pattern(flow) {
            self.challenge_solver.require_proof_of_work(flow);
        }
        
        // Connection state tracking
        if flow.connections_per_second() > 1000 {
            self.connection_limiter.throttle(flow.source_ip());
        }
    }
}
```

**Alex:** How do you handle legitimate traffic during these attacks?

**Sarah:** Priority queues and intelligent challenges:

```javascript
// Legitimate Traffic Protection
export default {
  async fetch(request, env, ctx) {
    const ip = request.headers.get('CF-Connecting-IP');
    
    // Check if under attack
    if (await env.ATTACK_STATUS.get('active') === 'true') {
      // Reputation check
      const reputation = await getReputation(ip, env);
      
      if (reputation.score > 0.8) {
        // Fast path for known good traffic
        return fetch(request);
      } else if (reputation.score > 0.5) {
        // Lightweight challenge
        return serveJSChallenge(request, 'simple');
      } else {
        // Complex challenge for suspicious traffic
        return serveJSChallenge(request, 'complex');
      }
    }
    
    // Normal processing
    return fetch(request);
  }
};

async function serveJSChallenge(request, complexity) {
  const challenge = generateChallenge(complexity);
  
  return new Response(challengeHTML(challenge), {
    headers: {
      'Content-Type': 'text/html',
      'Cache-Control': 'no-cache',
    }
  });
}
```

### Chapter 9: Building Internet-Scale Systems (10 minutes)

**Sarah:** Let me share lessons from building systems that protect 20% of the internet:

```yaml
# Internet-Scale Architecture Principles
principles:
  1_assume_failure:
    description: "Everything fails at scale"
    implementation:
      - No single points of failure
      - Graceful degradation everywhere
      - Automatic failover systems
      
  2_distributed_by_default:
    description: "Centralization doesn't scale"
    implementation:
      - 310 independent data centers
      - Each can operate autonomously
      - Consensus only when necessary
      
  3_attack_resilient_design:
    description: "Attacks are normal operating conditions"
    implementation:
      - Over-provision by 10x minimum
      - Defense in depth architecture
      - Automated response systems
      
  4_performance_at_scale:
    description: "Milliseconds matter globally"
    implementation:
      - Code runs <50ms from users
      - P99 latency targets globally
      - Edge computing by default
```

## Part 4: Modern Edge Computing Patterns (30 minutes)

### Chapter 10: Edge-First Architecture Patterns (10 minutes)

**Sarah:** We're seeing a shift to edge-first architectures:

```javascript
// Edge-First Application Architecture
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Pattern 1: Edge-side rendering
    if (url.pathname.startsWith('/product/')) {
      return renderProductPage(request, env);
    }
    
    // Pattern 2: Edge-side API aggregation
    if (url.pathname === '/api/dashboard') {
      return aggregateAPIs(request, env);
    }
    
    // Pattern 3: Edge-side personalization
    if (url.pathname === '/home') {
      return personalizeHomepage(request, env);
    }
  }
};

async function aggregateAPIs(request, env) {
  // Parallel API calls from edge
  const [user, recommendations, inventory] = await Promise.all([
    fetch('https://api.users.internal/current', {
      headers: request.headers
    }),
    fetch('https://api.recommendations.internal/user', {
      headers: request.headers  
    }),
    fetch('https://api.inventory.internal/available')
  ]);
  
  // Combine at edge
  const dashboard = {
    user: await user.json(),
    recommendations: await recommendations.json(),
    inventory: await inventory.json()
  };
  
  // Cache personalized result
  const cacheKey = new Request(request.url, {
    headers: {
      'User-ID': dashboard.user.id
    }
  });
  
  ctx.waitUntil(
    env.CACHE.put(cacheKey, new Response(JSON.stringify(dashboard), {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'private, max-age=300'
      }
    }))
  );
  
  return new Response(JSON.stringify(dashboard));
}
```

### Chapter 11: Zero Trust at the Edge (10 minutes)

**Sarah:** Security is fundamental to edge computing:

```rust
// Zero Trust Edge Security
use cloudflare_workers::*;

#[event(fetch)]
async fn main(req: Request, env: Env, _ctx: Context) -> Result<Response> {
    // Every request is untrusted
    let security_context = SecurityContext::new(&req, &env).await?;
    
    // Layer 1: Network validation
    if !security_context.validate_network().await? {
        return Response::error("Network validation failed", 403);
    }
    
    // Layer 2: Identity verification  
    let identity = match security_context.verify_identity().await {
        Ok(id) => id,
        Err(_) => return Response::redirect("/login"),
    };
    
    // Layer 3: Authorization check
    if !security_context.authorize(&identity, &req.url()?).await? {
        return Response::error("Unauthorized", 401);
    }
    
    // Layer 4: Request validation
    if !validate_request(&req).await? {
        return Response::error("Invalid request", 400);
    }
    
    // Process with security context
    process_secure_request(req, identity, env).await
}

struct SecurityContext {
    ip_reputation: f32,
    geo_risk_score: f32,
    device_fingerprint: String,
    behavioral_score: f32,
}

impl SecurityContext {
    async fn validate_network(&self) -> Result<bool> {
        // Check IP reputation
        if self.ip_reputation < 0.3 {
            return Ok(false);
        }
        
        // Geo-risk assessment
        if self.geo_risk_score > 0.8 {
            return Ok(false);
        }
        
        Ok(true)
    }
}
```

### Chapter 12: Workshop - Build Your Edge System (10 minutes)

**Alex:** Let's design an edge computing system. Requirements:
- 100M users globally
- <50ms latency worldwide
- 10M requests/second peak
- DDoS resistant

**Sarah:** Here's your framework:

```yaml
# Edge Computing Design Workshop
design_exercise:
  requirements:
    users: 100_000_000
    latency_target: 50ms
    peak_rps: 10_000_000
    ddos_protection: required
    
  architecture_decisions:
    1_edge_locations:
      question: "How many PoPs needed?"
      calculation: |
        - Major cities: 150
        - Coverage radius: 1000km
        - Redundancy factor: 2x
        Answer: ~200 locations
        
    2_capacity_planning:
      question: "Capacity per PoP?"
      calculation: |
        - Peak RPS: 10M globally
        - Distribution: 60% top 20 PoPs
        - Safety margin: 3x
        Answer: 150K RPS per major PoP
        
    3_ddos_strategy:
      layers:
        - Network layer (XDP/eBPF)
        - Application layer (Workers)
        - Behavioral analysis (ML)
        - Geographic distribution
        
    4_state_management:
      options:
        - Durable Objects for consistency
        - KV for eventual consistency
        - R2 for object storage
        - D1 for SQL at edge
```

## Part 5: Interactive Exercises (20 minutes)

### Exercise 1: DDoS Mitigation Simulator

**Sarah:** Try building a basic DDoS detector:

```python
class DDoSDetector:
    def __init__(self):
        self.window_size = 60  # seconds
        self.threshold_multiplier = 10
        self.baseline = self.calculate_baseline()
        
    def detect_attack(self, current_metrics):
        # Your implementation:
        # 1. Compare to baseline
        # 2. Detect anomalies
        # 3. Check attack patterns
        # 4. Return confidence score
        pass
    
    def calculate_baseline(self):
        # Historical average
        return {
            'rps': 50_000,
            'unique_ips': 10_000,
            'error_rate': 0.001,
            'avg_request_size': 1024
        }

# Test your detector
detector = DDoSDetector()
attack_metrics = {
    'rps': 5_000_000,
    'unique_ips': 5_000,
    'error_rate': 0.0001,
    'avg_request_size': 512
}

confidence = detector.detect_attack(attack_metrics)
print(f"Attack confidence: {confidence}")
```

### Exercise 2: Edge Computing Cost Calculator

**Sarah:** Calculate edge vs traditional hosting costs:

```javascript
function calculateEdgeCosts(requirements) {
  const edgeCost = {
    workers: {
      requests: requirements.requests * 0.0000005,  // $0.50 per million
      cpuTime: requirements.cpuMs * 0.00001,       // $0.01 per 1000ms
    },
    kv: {
      reads: requirements.kvReads * 0.0000005,
      writes: requirements.kvWrites * 0.000005,
      storage: requirements.kvStorage * 0.50,      // per GB/month
    },
    bandwidth: requirements.bandwidth * 0.08,      // per GB
  };
  
  const traditionalCost = {
    servers: Math.ceil(requirements.requests / 50000) * 200,  // VMs
    loadBalancer: 500,
    bandwidth: requirements.bandwidth * 0.12,
    database: 2000,
  };
  
  return {
    edge: Object.values(edgeCost).flat().reduce((a,b) => a+b),
    traditional: Object.values(traditionalCost).reduce((a,b) => a+b),
    savings: traditionalCost - edgeCost
  };
}
```

## Conclusion (10 minutes)

**Alex:** Sarah, what's the biggest paradigm shift with edge computing?

**Sarah:** Computing becomes geography-aware. Instead of users coming to your servers, your code runs where your users are. This fundamentally changes how we architect systems.

Three key principles:
1. **Distributed by design** - No central point of failure
2. **Security at every layer** - Zero trust from kernel to application
3. **Performance through proximity** - Physics always wins

**Alex:** What's next for Cloudflare's edge platform?

**Sarah:** We're pushing computing even closer to users:
- Browser-based edge compute
- 5G network edge integration  
- IoT device edge processing
- AI inference at the edge

The goal is sub-millisecond latency globally. We're not just accelerating the internet - we're becoming the internet's nervous system.

**Alex:** Thanks Sarah! Next week, we dive into Spotify's architecture. How do you stream 65 million songs to 500 million users with personalization at scale?

## Show Notes & Resources

### Key Statistics
- 71.1M requests/second peak (Mantis botnet)
- 310 global data centers
- 192 Tbps network capacity
- <50ms from 95% of internet users

### Architecture Patterns Discussed
1. Anycast networking
2. XDP/eBPF filtering
3. V8 isolate architecture
4. WASM isolation
5. Durable Objects consistency
6. Edge-first computing

### Code Repository
github.com/cloudflare/workers-examples

### References
- "How we mitigated the Mantis botnet attack" - Cloudflare Blog
- "The architecture of Cloudflare Workers" - Systems @Scale
- "XDP and eBPF for DDoS mitigation" - Netdev Conference
- "Building Durable Objects" - Cloudflare Engineering

### Try It Yourself
- workers.cloudflare.com - Free tier available
- Cloudflare Workers documentation
- DDoS simulation toolkit
- Edge computing tutorials

---

*Next Episode: Spotify's Music Streaming Architecture - 65 million songs, ML personalization, and P2P delivery at scale*
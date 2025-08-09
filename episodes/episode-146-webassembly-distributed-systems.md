# Episode 146: WebAssembly in Distributed Systems - Complete Technical Deep Dive

## Episode Overview
**Duration**: 2.5 hours (150 minutes)
**Level**: Advanced
**Prerequisites**: Systems programming, distributed systems fundamentals, basic knowledge of WebAssembly

WebAssembly (WASM) has evolved from a browser compilation target to a foundational technology for distributed systems. This episode explores the mathematical foundations, implementation strategies, and production deployments of WebAssembly in distributed architectures.

---

## Part 1: Mathematical Foundations (45 minutes)

### 1.1 WebAssembly Formal Semantics and Type System

#### Core Type System

WebAssembly's type system provides the mathematical foundation for its safety guarantees. The formal semantics define a stack machine with structured control flow.

**Value Types:**
```
valtype ::= i32 | i64 | f32 | f64 | v128 | funcref | externref
```

**Function Types:**
```
functype ::= [t1*] -> [t2*]
```

Where `[t1*]` represents parameter types and `[t2*]` represents result types.

**Mathematical Definition of Type Safety:**

Let Γ be a typing context, and ⊢ denote the typing judgment. Type safety is expressed as:

```
Theorem (Type Safety): 
If Γ ⊢ e : τ, then either:
1. e is a value, or
2. ∃ e' such that e → e' and Γ ⊢ e' : τ
```

**Proof Sketch:**
The proof proceeds by induction on the typing derivation. The key insight is that WebAssembly's structured control flow prevents arbitrary jumps that could violate type invariants.

#### Stack Machine Semantics

WebAssembly execution is modeled as a state machine:

```
State = (Stack, Locals, Memory, Globals, PC)
```

Where:
- Stack: operand stack for computation
- Locals: function-local variables
- Memory: linear memory space
- Globals: global variables
- PC: program counter

**Execution Rules:**

```
(i32.const c) : [] → [i32]
Stack: [] → [c]

(i32.add) : [i32, i32] → [i32]
Stack: [v1, v2] → [v1 + v2]
```

#### Advanced Type System Features

**Reference Types:**
```rust
// Formal definition of reference type validity
struct RefType {
    nullable: bool,
    heap_type: HeapType,
}

enum HeapType {
    Func(FuncType),
    Extern,
    Any,
}
```

**Subtyping Relations:**
```
i32 <: i32
funcref <: anyref
(ref null func) <: (ref func)
```

### 1.2 Performance Models and Computational Complexity

#### Execution Model Analysis

WebAssembly's performance characteristics can be analyzed through computational complexity theory.

**Time Complexity Model:**

Let T(n) be the execution time for a WebAssembly program of size n.

```
T(n) = O(Σ(i=1 to n) w_i * c_i)
```

Where:
- w_i: frequency of instruction i
- c_i: cost of instruction i

**Memory Access Complexity:**

Linear memory access in WebAssembly follows:
```
Access_time = O(1) for aligned access
Access_time = O(1) for unaligned access (with potential penalty)
```

**Compilation Complexity:**

For ahead-of-time compilation:
```
Compile_time = O(n * log n)
```

For just-in-time compilation:
```
JIT_time = O(n) + Runtime_optimization_cost
```

#### Performance Bounds

**Theorem (Performance Lower Bound):**
For any WebAssembly program P computing function f, if f requires time T(n) on a RAM machine, then P requires time Ω(T(n)) on the WebAssembly abstract machine.

**Proof:**
This follows from the fact that WebAssembly can simulate a RAM machine with constant overhead per operation.

#### Cache Performance Analysis

WebAssembly's linear memory model affects cache performance:

```rust
// Cache-friendly memory access pattern
fn cache_optimal_traversal(data: &[i32], size: usize) -> i32 {
    let mut sum = 0;
    for i in 0..size {
        sum += data[i]; // Sequential access, cache-friendly
    }
    sum
}

// Cache-unfriendly pattern
fn cache_poor_traversal(data: &[i32], size: usize) -> i32 {
    let mut sum = 0;
    for i in (0..size).step_by(1024) { // Large stride, cache-unfriendly
        sum += data[i];
    }
    sum
}
```

**Mathematical Model:**
```
Cache_misses = ⌈Working_set_size / Cache_size⌉ * Access_frequency
```

### 1.3 Memory Safety Guarantees and Formal Verification

#### Memory Safety Theorem

**Theorem (Memory Safety):**
A well-typed WebAssembly program cannot:
1. Access memory outside allocated bounds
2. Corrupt the execution stack
3. Jump to arbitrary code locations

**Formal Proof Structure:**

```
Lemma 1 (Bounds Checking): 
∀ memory access (load/store) at address a:
if bounds_check(a, memory_size) fails, then trap

Lemma 2 (Stack Integrity):
∀ function call/return:
stack_pointer remains within allocated stack bounds

Lemma 3 (Control Flow Integrity):
∀ branch/jump instruction:
target ∈ valid_branch_targets
```

**Memory Model Formalization:**

```rust
struct LinearMemory {
    data: Vec<u8>,
    size: usize,
    max_size: Option<usize>,
}

impl LinearMemory {
    fn load<T>(&self, addr: usize) -> Result<T, Trap> {
        if addr + size_of::<T>() > self.size {
            return Err(Trap::OutOfBounds);
        }
        // Safe to load
        unsafe { Ok(*(self.data.as_ptr().add(addr) as *const T)) }
    }
}
```

#### Sandboxing Guarantees

WebAssembly provides strong isolation through:

1. **Capability-based Security:**
```rust
// Host functions are explicitly imported
extern "C" {
    fn host_function(param: i32) -> i32;
}

// No access to arbitrary system calls
```

2. **Resource Limits:**
```rust
struct RuntimeLimits {
    max_memory: usize,
    max_stack: usize,
    max_execution_time: Duration,
}
```

### 1.4 Sandboxing and Isolation Theorems

#### Isolation Properties

**Theorem (Process Isolation):**
Two WebAssembly instances I1 and I2 running in the same runtime cannot directly access each other's:
1. Linear memory
2. Local variables
3. Private globals

**Proof Outline:**
Each instance maintains separate address spaces. The runtime enforces access controls at the instruction level.

**Mathematical Formalization:**
```
∀ instances I1, I2:
Memory(I1) ∩ Memory(I2) = ∅
Globals(I1) ∩ Globals(I2) = ∅
```

#### Information Flow Analysis

We can model information flow using lattice theory:

```
Security_Level = {Public, Confidential, Secret}
```

With ordering: Public ≤ Confidential ≤ Secret

**Non-interference Property:**
```
∀ programs P, inputs (L_input, H_input):
P(L_input, H_1) ≡_L P(L_input, H_2)
```

Where ≡_L denotes low-equivalence (observable behavior at low security level).

#### Resource Isolation

**Computation Bounds:**
```rust
struct ResourceMetrics {
    instructions_executed: u64,
    memory_allocated: usize,
    execution_time: Duration,
}

fn enforce_limits(metrics: &ResourceMetrics, limits: &RuntimeLimits) -> Result<(), ResourceExhaustion> {
    if metrics.memory_allocated > limits.max_memory {
        return Err(ResourceExhaustion::Memory);
    }
    if metrics.execution_time > limits.max_execution_time {
        return Err(ResourceExhaustion::Time);
    }
    Ok(())
}
```

---

## Part 2: Implementation Details (60 minutes)

### 2.1 WASM Runtime Architectures

#### V8 WebAssembly Implementation

V8's WebAssembly implementation uses a multi-tier compilation strategy:

```cpp
// Simplified V8 WASM compilation pipeline
class WasmCompiler {
    // Liftoff: Fast baseline compiler
    std::unique_ptr<WasmCode> CompileLiftoff(const WasmModule* module) {
        // Generate code quickly for fast startup
        return GenerateBaselineCode(module);
    }
    
    // TurboFan: Optimizing compiler
    std::unique_ptr<WasmCode> CompileTurboFan(const WasmModule* module) {
        // Heavy optimizations for hot code
        return GenerateOptimizedCode(module);
    }
};
```

**Tiered Compilation Strategy:**
1. **Liftoff (Tier 1):** Fast compilation for immediate execution
2. **TurboFan (Tier 2):** Optimizing compilation for hot code paths

**Performance Metrics:**
- Liftoff: ~100,000 bytes/second compilation speed
- TurboFan: 5-10x slower compilation, 2-3x faster execution

#### Wasmtime Architecture

Wasmtime uses Cranelift as its code generator:

```rust
use wasmtime::*;
use cranelift_codegen::settings;

// Wasmtime runtime configuration
fn create_optimized_engine() -> Result<Engine, Box<dyn std::error::Error>> {
    let mut config = Config::new();
    config.strategy(Strategy::Cranelift)?;
    config.cranelift_opt_level(OptLevel::Speed)?;
    config.cranelift_debug_verifier(false)?; // Disable for production
    
    Ok(Engine::new(&config)?)
}

// Instance creation with resource limits
fn create_limited_instance(engine: &Engine, module: &Module) -> Result<Instance, Box<dyn std::error::Error>> {
    let mut store = Store::new(engine, ());
    
    // Configure resource limits
    store.limiter(|_| ResourceLimiterConfig {
        memory_size: 64 * 1024 * 1024, // 64 MB
        table_elements: 1000,
        instances: 1,
        tables: 1,
        memories: 1,
    });
    
    Instance::new(&mut store, module, &[])
}
```

**Cranelift Optimization Pipeline:**
```rust
// Simplified optimization pipeline
fn optimize_function(func: &mut Function) {
    // Control flow graph construction
    let cfg = ControlFlowGraph::with_function(func);
    
    // Dead code elimination
    eliminate_dead_code(func, &cfg);
    
    // Common subexpression elimination
    eliminate_common_subexpressions(func);
    
    // Register allocation
    allocate_registers(func);
}
```

#### Wasmer Runtime

Wasmer supports multiple compilation backends:

```rust
use wasmer::{Engine, Store, Module, Instance, Value, imports};
use wasmer_compiler_cranelift::Cranelift;
use wasmer_compiler_llvm::LLVM;
use wasmer_compiler_singlepass::Singlepass;

// Multi-backend support
fn create_engine_for_workload(workload_type: WorkloadType) -> Engine {
    match workload_type {
        WorkloadType::Development => {
            // Fast compilation for development
            Engine::new(Box::new(Singlepass::default()), Target::default(), Features::default())
        },
        WorkloadType::Production => {
            // Optimized compilation for production
            Engine::new(Box::new(LLVM::default()), Target::default(), Features::default())
        },
        WorkloadType::Balanced => {
            // Balanced compilation speed and performance
            Engine::new(Box::new(Cranelift::default()), Target::default(), Features::default())
        }
    }
}
```

### 2.2 Edge Computing with WASM

#### Cloudflare Workers Architecture

Cloudflare Workers runs WebAssembly at the edge with impressive performance characteristics:

```javascript
// Cloudflare Worker example
export default {
    async fetch(request, env, ctx) {
        // This runs in a WebAssembly sandbox
        const startTime = Date.now();
        
        // Process request with <1ms cold start
        const response = await processRequest(request);
        
        const duration = Date.now() - startTime;
        response.headers.set('CF-Processing-Time', duration.toString());
        
        return response;
    }
}

// Advanced routing with WASM
async function processRequest(request) {
    const url = new URL(request.url);
    
    // Route based on path
    switch (url.pathname) {
        case '/api/auth':
            return handleAuth(request);
        case '/api/data':
            return handleData(request);
        default:
            return new Response('Not Found', { status: 404 });
    }
}
```

**Performance Characteristics:**
- Cold start: <1ms (compared to 100-1000ms for containers)
- Memory overhead: ~1MB per isolate
- CPU overhead: ~5% compared to native execution

**Implementation Details:**
```rust
// Simplified Cloudflare Workers isolate management
struct WorkerIsolate {
    runtime: V8Runtime,
    memory_limit: usize,
    cpu_time_limit: Duration,
    request_count: AtomicU64,
}

impl WorkerIsolate {
    fn execute_request(&self, request: Request) -> Result<Response, WorkerError> {
        let start = Instant::now();
        
        // Enforce CPU time limit
        let timeout = Timer::new(self.cpu_time_limit);
        
        // Execute in isolated context
        let result = self.runtime.execute_with_timeout(request, timeout)?;
        
        // Update metrics
        let duration = start.elapsed();
        self.record_execution_time(duration);
        
        Ok(result)
    }
}
```

#### Fastly Compute@Edge

Fastly's implementation focuses on instant startup and HTTP processing:

```rust
use fastly::http::{Method, StatusCode};
use fastly::{Error, Request, Response};

#[fastly::main]
fn main(req: Request) -> Result<Response, Error> {
    match req.get_method() {
        &Method::GET => handle_get(req),
        &Method::POST => handle_post(req),
        _ => Ok(Response::from_status(StatusCode::METHOD_NOT_ALLOWED)),
    }
}

fn handle_get(req: Request) -> Result<Response, Error> {
    let url = req.get_url();
    
    // Edge-side includes (ESI) processing
    if url.path().starts_with("/api/") {
        process_api_request(req)
    } else {
        serve_static_content(req)
    }
}

// Advanced caching with WASM
fn process_api_request(req: Request) -> Result<Response, Error> {
    use std::time::Duration;
    
    // Check edge cache first
    let cache_key = generate_cache_key(&req);
    
    if let Some(cached_response) = get_cached_response(&cache_key) {
        return Ok(cached_response);
    }
    
    // Fetch from origin with timeout
    let backend_response = Request::builder()
        .method(req.get_method())
        .uri(req.get_url())
        .body(req.into_body())?
        .send_async("origin")?
        .with_ttl(Duration::from_secs(60))?;
    
    // Cache the response
    cache_response(&cache_key, &backend_response);
    
    Ok(backend_response)
}
```

**Performance Metrics:**
- Cold start: <100ms guaranteed
- Memory isolation: Complete process isolation
- Throughput: 1M+ requests/second per edge location

### 2.3 WASM in Service Mesh

#### Envoy Proxy WASM Filters

Envoy supports WebAssembly filters for extensible proxy functionality:

```cpp
// C++ host implementation for WASM filter
class WasmFilter : public Http::StreamFilter {
public:
    Http::FilterHeadersStatus decodeHeaders(Http::RequestHeaderMap& headers, bool) override {
        // Load WASM module
        auto wasm_vm = createWasm(vm_config_);
        
        // Execute WASM filter function
        auto result = wasm_vm->call("on_request_headers", &headers);
        
        return parseFilterResult(result);
    }
    
private:
    WasmVmConfig vm_config_;
};
```

**WASM Filter Implementation:**
```rust
use proxy_wasm::traits::*;
use proxy_wasm::types::*;

#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_http_context(|_, _| -> Box<dyn HttpContext> {
        Box::new(CustomFilter)
    });
}

struct CustomFilter;

impl HttpContext for CustomFilter {
    fn on_http_request_headers(&mut self, num_headers: usize) -> Action {
        // Custom authentication logic
        if let Some(auth_header) = self.get_http_request_header("authorization") {
            if validate_token(&auth_header) {
                Action::Continue
            } else {
                self.send_http_response(401, vec![("content-type", "text/plain")], Some(b"Unauthorized"));
                Action::Pause
            }
        } else {
            Action::Continue
        }
    }
    
    fn on_http_response_headers(&mut self, num_headers: usize) -> Action {
        // Add custom headers to response
        self.add_http_response_header("x-processed-by", "wasm-filter");
        self.add_http_response_header("x-request-id", &generate_request_id());
        Action::Continue
    }
}

fn validate_token(token: &str) -> bool {
    // JWT validation logic
    match decode_jwt(token) {
        Ok(claims) => !claims.is_expired(),
        Err(_) => false,
    }
}
```

**Advanced Filter Chaining:**
```rust
// Multi-filter pipeline
struct FilterChain {
    filters: Vec<Box<dyn WasmFilter>>,
}

impl FilterChain {
    fn process_request(&mut self, request: &mut Request) -> FilterResult {
        for filter in &mut self.filters {
            match filter.on_request(request)? {
                FilterAction::Continue => continue,
                FilterAction::Stop => return Ok(FilterResult::Stopped),
                FilterAction::StopAndBuffer => {
                    // Buffer request body for further processing
                    return Ok(FilterResult::Buffered);
                }
            }
        }
        Ok(FilterResult::Completed)
    }
}
```

#### Istio WASM Extensions

Istio integrates WebAssembly through Envoy's WASM support:

```yaml
# Istio WasmPlugin configuration
apiVersion: extensions.istio.io/v1alpha1
kind: WasmPlugin
metadata:
  name: custom-auth
  namespace: default
spec:
  selector:
    matchLabels:
      app: productpage
  url: oci://registry.example.com/wasm-filters/auth:v1.0.0
  phase: AUTHN
  pluginConfig:
    jwt_issuer: "https://auth.example.com"
    allowed_audiences: ["api.example.com"]
```

**WASM Extension Implementation:**
```rust
use istio_proxy_wasm::*;

struct IstioAuthFilter {
    config: AuthConfig,
}

impl Context for IstioAuthFilter {
    fn on_configure(&mut self, _: usize) -> bool {
        // Load configuration from Istio
        if let Some(config) = self.get_property(vec!["plugin_config"]) {
            self.config = serde_json::from_slice(&config).unwrap();
            true
        } else {
            false
        }
    }
}

impl HttpContext for IstioAuthFilter {
    fn on_http_request_headers(&mut self, _: usize) -> Action {
        // Integrate with Istio's security model
        let headers = self.get_http_request_headers();
        
        // Check mTLS certificate
        if let Some(cert) = self.get_property(vec!["connection", "mtls", "peer_cert"]) {
            if !self.validate_peer_certificate(&cert) {
                return self.send_http_response(401, vec![], Some(b"Certificate validation failed"));
            }
        }
        
        // Perform JWT validation
        match self.validate_jwt_token(&headers) {
            Ok(_) => Action::Continue,
            Err(e) => {
                log::warn!("JWT validation failed: {}", e);
                self.send_http_response(401, vec![], Some(b"Invalid token"));
                Action::Pause
            }
        }
    }
}
```

### 2.4 Cross-Platform Deployment Strategies

#### Container Integration

WebAssembly can be integrated with container orchestration:

```dockerfile
# Multi-stage Docker build for WASM
FROM rust:1.70 as builder
WORKDIR /app
COPY . .
RUN rustup target add wasm32-wasi
RUN cargo build --target wasm32-wasi --release

FROM wasmtime/wasmtime:latest
COPY --from=builder /app/target/wasm32-wasi/release/app.wasm /app.wasm
EXPOSE 8080
CMD ["wasmtime", "run", "--invoke", "_start", "/app.wasm"]
```

**Kubernetes Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wasm-app
spec:
  replicas: 10
  selector:
    matchLabels:
      app: wasm-app
  template:
    metadata:
      labels:
        app: wasm-app
    spec:
      containers:
      - name: wasm-runtime
        image: wasmtime/wasmtime:latest
        args: ["wasmtime", "run", "/app/service.wasm"]
        resources:
          limits:
            memory: "64Mi"
            cpu: "100m"
          requests:
            memory: "32Mi"
            cpu: "50m"
        volumeMounts:
        - name: wasm-code
          mountPath: /app
        env:
        - name: WASMTIME_BACKTRACE_DETAILS
          value: "1"
      volumes:
      - name: wasm-code
        configMap:
          name: wasm-app-code
```

#### Serverless Platforms

**AWS Lambda with WASM:**
```rust
use lambda_runtime::{service_fn, Error, LambdaEvent};
use serde_json::{json, Value};
use wasmtime::*;

#[tokio::main]
async fn main() -> Result<(), Error> {
    let func = service_fn(function_handler);
    lambda_runtime::run(func).await
}

async fn function_handler(event: LambdaEvent<Value>) -> Result<Value, Error> {
    // Load WASM module
    let engine = Engine::default();
    let module = Module::from_file(&engine, "function.wasm")?;
    let mut store = Store::new(&engine, ());
    
    // Create instance
    let instance = Instance::new(&mut store, &module, &[])?;
    
    // Get exported function
    let process_event = instance.get_typed_func::<i32, i32>(&mut store, "process_event")?;
    
    // Convert event to WASM format
    let event_data = serialize_event(&event.payload)?;
    let result = process_event.call(&mut store, event_data)?;
    
    Ok(json!({
        "statusCode": 200,
        "body": result
    }))
}
```

### 2.5 Code Examples

#### Rust to WASM Compilation

```rust
// src/lib.rs - High-performance data processing
use wasm_bindgen::prelude::*;
use js_sys::Array;

#[wasm_bindgen]
pub struct DataProcessor {
    data: Vec<f64>,
    processed: bool,
}

#[wasm_bindgen]
impl DataProcessor {
    #[wasm_bindgen(constructor)]
    pub fn new(data: &Array) -> DataProcessor {
        let data: Vec<f64> = data
            .iter()
            .map(|v| v.as_f64().unwrap_or(0.0))
            .collect();
        
        DataProcessor {
            data,
            processed: false,
        }
    }
    
    #[wasm_bindgen]
    pub fn process_parallel(&mut self) -> Array {
        use rayon::prelude::*;
        
        // Parallel processing with Rayon
        let processed: Vec<f64> = self.data
            .par_iter()
            .map(|&x| complex_calculation(x))
            .collect();
        
        self.processed = true;
        processed.into_iter().map(JsValue::from).collect()
    }
    
    #[wasm_bindgen]
    pub fn get_statistics(&self) -> Statistics {
        if !self.processed {
            panic!("Data must be processed first");
        }
        
        let sum: f64 = self.data.iter().sum();
        let mean = sum / self.data.len() as f64;
        
        let variance: f64 = self.data
            .iter()
            .map(|&x| (x - mean).powi(2))
            .sum::<f64>() / self.data.len() as f64;
        
        Statistics {
            mean,
            variance,
            std_dev: variance.sqrt(),
            count: self.data.len(),
        }
    }
}

#[wasm_bindgen]
pub struct Statistics {
    pub mean: f64,
    pub variance: f64,
    pub std_dev: f64,
    pub count: usize,
}

fn complex_calculation(x: f64) -> f64 {
    // Simulate computationally intensive operation
    (x * x + x.sin() * x.cos()).sqrt()
}

// Build configuration in Cargo.toml
/*
[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
js-sys = "0.3"
rayon = "1.7"

[dependencies.web-sys]
version = "0.3"
features = [
  "console",
  "Performance",
  "Window",
]
*/
```

#### Go to WASM with TinyGo

```go
package main

import (
    "encoding/json"
    "syscall/js"
    "sync"
    "time"
)

type Server struct {
    routes map[string]HandlerFunc
    mutex  sync.RWMutex
}

type HandlerFunc func(Request) Response

type Request struct {
    Method  string            `json:"method"`
    Path    string            `json:"path"`
    Headers map[string]string `json:"headers"`
    Body    string            `json:"body"`
}

type Response struct {
    Status  int               `json:"status"`
    Headers map[string]string `json:"headers"`
    Body    string            `json:"body"`
}

func NewServer() *Server {
    return &Server{
        routes: make(map[string]HandlerFunc),
    }
}

func (s *Server) Handle(path string, handler HandlerFunc) {
    s.mutex.Lock()
    defer s.mutex.Unlock()
    s.routes[path] = handler
}

func (s *Server) ServeHTTP(this js.Value, args []js.Value) interface{} {
    if len(args) == 0 {
        return map[string]interface{}{
            "error": "No request provided",
        }
    }
    
    // Parse request from JavaScript
    requestData := args[0].String()
    var req Request
    if err := json.Unmarshal([]byte(requestData), &req); err != nil {
        return map[string]interface{}{
            "error": "Invalid request format",
        }
    }
    
    // Find handler
    s.mutex.RLock()
    handler, exists := s.routes[req.Path]
    s.mutex.RUnlock()
    
    if !exists {
        return Response{
            Status: 404,
            Headers: map[string]string{"Content-Type": "text/plain"},
            Body:   "Not Found",
        }
    }
    
    // Execute handler
    response := handler(req)
    
    // Convert response to JavaScript-friendly format
    responseData, _ := json.Marshal(response)
    return js.Global().Get("JSON").Call("parse", string(responseData))
}

// Example handlers
func apiHandler(req Request) Response {
    switch req.Method {
    case "GET":
        return Response{
            Status: 200,
            Headers: map[string]string{
                "Content-Type": "application/json",
                "X-Powered-By": "WebAssembly",
            },
            Body: `{"message": "Hello from WASM", "timestamp": "` + time.Now().Format(time.RFC3339) + `"}`,
        }
    case "POST":
        // Process POST data
        processed := processData(req.Body)
        return Response{
            Status: 200,
            Headers: map[string]string{"Content-Type": "application/json"},
            Body:   processed,
        }
    default:
        return Response{
            Status: 405,
            Headers: map[string]string{"Allow": "GET, POST"},
            Body:   "Method Not Allowed",
        }
    }
}

func processData(data string) string {
    // Simulate data processing
    var input map[string]interface{}
    json.Unmarshal([]byte(data), &input)
    
    result := map[string]interface{}{
        "processed": true,
        "input":     input,
        "timestamp": time.Now().Unix(),
    }
    
    output, _ := json.Marshal(result)
    return string(output)
}

func main() {
    server := NewServer()
    
    // Register routes
    server.Handle("/api/data", apiHandler)
    server.Handle("/health", func(req Request) Response {
        return Response{
            Status: 200,
            Headers: map[string]string{"Content-Type": "text/plain"},
            Body:   "OK",
        }
    })
    
    // Export server to JavaScript
    js.Global().Set("wasmServer", js.FuncOf(server.ServeHTTP))
    
    // Keep the main goroutine alive
    select {}
}
```

#### AssemblyScript Implementation

```typescript
// High-performance image processing in AssemblyScript
export class ImageProcessor {
    private data: Uint8ClampedArray;
    private width: i32;
    private height: i32;
    
    constructor(width: i32, height: i32) {
        this.width = width;
        this.height = height;
        this.data = new Uint8ClampedArray(width * height * 4); // RGBA
    }
    
    setPixel(x: i32, y: i32, r: u8, g: u8, b: u8, a: u8): void {
        const index = (y * this.width + x) * 4;
        this.data[index] = r;
        this.data[index + 1] = g;
        this.data[index + 2] = b;
        this.data[index + 3] = a;
    }
    
    getPixel(x: i32, y: i32): StaticArray<u8> {
        const index = (y * this.width + x) * 4;
        const pixel = new StaticArray<u8>(4);
        pixel[0] = this.data[index];
        pixel[1] = this.data[index + 1];
        pixel[2] = this.data[index + 2];
        pixel[3] = this.data[index + 3];
        return pixel;
    }
    
    // Gaussian blur filter implementation
    gaussianBlur(radius: i32): void {
        const kernel = this.generateGaussianKernel(radius);
        const kernelSize = kernel.length;
        const half = kernelSize >> 1;
        
        // Create temporary buffer
        const temp = new Uint8ClampedArray(this.data.length);
        
        // Horizontal pass
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                let r: f32 = 0, g: f32 = 0, b: f32 = 0, a: f32 = 0;
                let weightSum: f32 = 0;
                
                for (let i = 0; i < kernelSize; i++) {
                    const sampleX = x + i - half;
                    if (sampleX >= 0 && sampleX < this.width) {
                        const pixel = this.getPixel(sampleX, y);
                        const weight = kernel[i];
                        
                        r += pixel[0] * weight;
                        g += pixel[1] * weight;
                        b += pixel[2] * weight;
                        a += pixel[3] * weight;
                        weightSum += weight;
                    }
                }
                
                const index = (y * this.width + x) * 4;
                temp[index] = u8(r / weightSum);
                temp[index + 1] = u8(g / weightSum);
                temp[index + 2] = u8(b / weightSum);
                temp[index + 3] = u8(a / weightSum);
            }
        }
        
        // Vertical pass
        for (let x = 0; x < this.width; x++) {
            for (let y = 0; y < this.height; y++) {
                let r: f32 = 0, g: f32 = 0, b: f32 = 0, a: f32 = 0;
                let weightSum: f32 = 0;
                
                for (let i = 0; i < kernelSize; i++) {
                    const sampleY = y + i - half;
                    if (sampleY >= 0 && sampleY < this.height) {
                        const index = (sampleY * this.width + x) * 4;
                        const weight = kernel[i];
                        
                        r += temp[index] * weight;
                        g += temp[index + 1] * weight;
                        b += temp[index + 2] * weight;
                        a += temp[index + 3] * weight;
                        weightSum += weight;
                    }
                }
                
                const index = (y * this.width + x) * 4;
                this.data[index] = u8(r / weightSum);
                this.data[index + 1] = u8(g / weightSum);
                this.data[index + 2] = u8(b / weightSum);
                this.data[index + 3] = u8(a / weightSum);
            }
        }
    }
    
    private generateGaussianKernel(radius: i32): StaticArray<f32> {
        const size = radius * 2 + 1;
        const kernel = new StaticArray<f32>(size);
        const sigma: f32 = radius / 3.0;
        const twoSigmaSq: f32 = 2 * sigma * sigma;
        let sum: f32 = 0;
        
        for (let i = 0; i < size; i++) {
            const x: f32 = i - radius;
            const value = <f32>Math.exp(-(x * x) / twoSigmaSq);
            kernel[i] = value;
            sum += value;
        }
        
        // Normalize
        for (let i = 0; i < size; i++) {
            kernel[i] /= sum;
        }
        
        return kernel;
    }
    
    // Edge detection using Sobel operator
    sobelEdgeDetection(): void {
        const sobelX: StaticArray<StaticArray<i8>> = [
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ];
        
        const sobelY: StaticArray<StaticArray<i8>> = [
            [-1, -2, -1],
            [ 0,  0,  0],
            [ 1,  2,  1]
        ];
        
        const result = new Uint8ClampedArray(this.data.length);
        
        for (let y = 1; y < this.height - 1; y++) {
            for (let x = 1; x < this.width - 1; x++) {
                let gx: f32 = 0, gy: f32 = 0;
                
                for (let ky = 0; ky < 3; ky++) {
                    for (let kx = 0; kx < 3; kx++) {
                        const pixel = this.getPixel(x + kx - 1, y + ky - 1);
                        const intensity = (pixel[0] + pixel[1] + pixel[2]) / 3;
                        
                        gx += intensity * sobelX[ky][kx];
                        gy += intensity * sobelY[ky][kx];
                    }
                }
                
                const magnitude = <f32>Math.sqrt(gx * gx + gy * gy);
                const value = u8(Math.min(255, magnitude));
                
                const index = (y * this.width + x) * 4;
                result[index] = value;
                result[index + 1] = value;
                result[index + 2] = value;
                result[index + 3] = 255;
            }
        }
        
        this.data = result;
    }
    
    getData(): Uint8ClampedArray {
        return this.data;
    }
}

// Export memory management functions
export function allocate(size: i32): i32 {
    return heap.alloc(size);
}

export function deallocate(ptr: i32): void {
    heap.free(ptr);
}

// Performance monitoring
export class PerformanceMonitor {
    private startTime: i64;
    
    start(): void {
        this.startTime = Date.now();
    }
    
    end(): f64 {
        return Date.now() - this.startTime;
    }
    
    benchmark(iterations: i32, fn: () => void): f64 {
        this.start();
        for (let i = 0; i < iterations; i++) {
            fn();
        }
        return this.end() / iterations;
    }
}
```

---

## Part 3: Production Systems (30 minutes)

### 3.1 Cloudflare Workers: 10 Million+ Requests/Second

Cloudflare Workers represents one of the most successful large-scale WebAssembly deployments, handling over 10 million requests per second globally.

#### Architecture Overview

```rust
// Simplified Cloudflare Workers runtime architecture
pub struct WorkersRuntime {
    isolate_pool: IsolatePool,
    request_router: RequestRouter,
    performance_monitor: PerformanceMonitor,
}

impl WorkersRuntime {
    pub fn new(config: RuntimeConfig) -> Self {
        Self {
            isolate_pool: IsolatePool::new(config.max_isolates),
            request_router: RequestRouter::new(),
            performance_monitor: PerformanceMonitor::new(),
        }
    }
    
    pub async fn handle_request(&self, request: HttpRequest) -> Result<HttpResponse, RuntimeError> {
        let start_time = Instant::now();
        
        // Get or create isolate
        let isolate = self.isolate_pool.get_or_create(&request).await?;
        
        // Route to appropriate script
        let script = self.request_router.find_script(&request)?;
        
        // Execute with resource limits
        let response = isolate.execute_script(script, request).await?;
        
        // Record performance metrics
        let duration = start_time.elapsed();
        self.performance_monitor.record_request(duration, response.status());
        
        Ok(response)
    }
}

pub struct IsolatePool {
    active_isolates: DashMap<String, Arc<Isolate>>,
    max_isolates: usize,
    isolate_factory: IsolateFactory,
}

impl IsolatePool {
    pub async fn get_or_create(&self, request: &HttpRequest) -> Result<Arc<Isolate>, RuntimeError> {
        let script_id = self.extract_script_id(request);
        
        // Check for existing isolate
        if let Some(isolate) = self.active_isolates.get(&script_id) {
            if isolate.is_healthy() {
                return Ok(isolate.clone());
            }
        }
        
        // Create new isolate if needed
        let isolate = self.isolate_factory.create(script_id.clone()).await?;
        self.active_isolates.insert(script_id, isolate.clone());
        
        Ok(isolate)
    }
}
```

#### Performance Characteristics

**Cold Start Performance:**
```rust
pub struct ColdStartMetrics {
    pub script_parse_time: Duration,     // ~0.1ms
    pub isolate_creation_time: Duration, // ~0.5ms
    pub first_execution_time: Duration,  // ~0.4ms
    pub total_cold_start: Duration,      // ~1.0ms
}

impl ColdStartMetrics {
    pub fn measure_cold_start<F, T>(f: F) -> (T, Self) 
    where F: FnOnce() -> T 
    {
        let overall_start = Instant::now();
        
        let parse_start = Instant::now();
        // Script parsing happens here
        let script_parse_time = parse_start.elapsed();
        
        let isolate_start = Instant::now();
        // Isolate creation happens here
        let isolate_creation_time = isolate_start.elapsed();
        
        let execution_start = Instant::now();
        let result = f();
        let first_execution_time = execution_start.elapsed();
        
        let total_cold_start = overall_start.elapsed();
        
        let metrics = Self {
            script_parse_time,
            isolate_creation_time,
            first_execution_time,
            total_cold_start,
        };
        
        (result, metrics)
    }
}
```

**Production Metrics:**
- **Requests/second**: 10M+ globally across 200+ edge locations
- **Cold start latency**: <1ms (99th percentile)
- **Memory per isolate**: ~1MB overhead
- **CPU overhead**: ~5% compared to native code
- **Concurrent isolates per server**: 10,000+

#### Request Processing Pipeline

```javascript
// Example high-performance Workers script
export default {
    async fetch(request, env, ctx) {
        const startTime = Date.now();
        
        try {
            // Fast path for static content
            if (request.method === 'GET' && isStaticAsset(request.url)) {
                return serveStaticAsset(request, env);
            }
            
            // API request processing
            if (request.url.includes('/api/')) {
                return handleApiRequest(request, env, ctx);
            }
            
            // Default handling
            return new Response('Not Found', { status: 404 });
            
        } finally {
            // Record processing time
            const processingTime = Date.now() - startTime;
            console.log(`Request processed in ${processingTime}ms`);
        }
    }
}

async function handleApiRequest(request, env, ctx) {
    const url = new URL(request.url);
    
    // Rate limiting with Durable Objects
    const rateLimiter = env.RATE_LIMITER.get(env.RATE_LIMITER.idFromName(getClientId(request)));
    const isAllowed = await rateLimiter.fetch('/check');
    
    if (!isAllowed.ok) {
        return new Response('Rate limit exceeded', { status: 429 });
    }
    
    // Database query with connection pooling
    const result = await env.DATABASE.prepare(`
        SELECT data FROM cache 
        WHERE key = ? AND expires_at > ?
    `).bind(url.pathname, Date.now()).first();
    
    if (result) {
        return new Response(result.data, {
            headers: { 
                'Content-Type': 'application/json',
                'Cache-Control': 'public, max-age=300',
                'X-Cache': 'HIT'
            }
        });
    }
    
    // Fetch from origin with intelligent routing
    const origin = determineOrigin(request);
    const response = await fetch(request, {
        cf: {
            cacheTtl: 300,
            cacheEverything: true,
            cacheTtlByStatus: { '200-299': 600, '300-399': 300, '400-499': 60 }
        }
    });
    
    return response;
}
```

### 3.2 Fastly Compute@Edge: <100ms Cold Starts

Fastly's Compute@Edge platform guarantees sub-100ms cold starts while providing full HTTP processing capabilities.

#### Runtime Architecture

```rust
// Fastly's WASM runtime implementation
pub struct ComputeEdgeRuntime {
    wasm_engine: WasmEngine,
    http_context: HttpContext,
    resource_limiter: ResourceLimiter,
}

impl ComputeEdgeRuntime {
    pub fn new() -> Result<Self, RuntimeError> {
        let config = EngineConfig {
            // Optimized for fast startup
            compiler: CompilerType::Baseline, // Fast compilation
            optimization_level: OptLevel::None, // Skip heavy optimizations for faster startup
            memory_limits: MemoryLimits {
                max_memory: 128 * 1024 * 1024, // 128MB
                max_stack: 1024 * 1024,        // 1MB
            },
        };
        
        Ok(Self {
            wasm_engine: WasmEngine::new(config)?,
            http_context: HttpContext::new(),
            resource_limiter: ResourceLimiter::new(),
        })
    }
    
    pub async fn execute_request(&mut self, wasm_module: &[u8], request: HttpRequest) -> Result<HttpResponse, RuntimeError> {
        let execution_start = Instant::now();
        
        // Fast module instantiation
        let instance = self.wasm_engine.instantiate_streaming(wasm_module).await?;
        
        // Set up execution context
        let mut execution_context = ExecutionContext::new(
            &self.http_context,
            &self.resource_limiter,
            request,
        );
        
        // Execute main function
        let response = instance.call_main(&mut execution_context).await?;
        
        let execution_time = execution_start.elapsed();
        
        // Guarantee: execution_time < Duration::from_millis(100)
        if execution_time > Duration::from_millis(100) {
            return Err(RuntimeError::ColdStartTimeoutExceeded);
        }
        
        Ok(response)
    }
}

pub struct ExecutionContext {
    http_context: HttpContextRef,
    resource_limiter: ResourceLimiterRef,
    request: HttpRequest,
    start_time: Instant,
}

impl ExecutionContext {
    pub fn enforce_time_limit(&self) -> Result<(), RuntimeError> {
        if self.start_time.elapsed() > Duration::from_millis(90) {
            Err(RuntimeError::ExecutionTimeout)
        } else {
            Ok(())
        }
    }
}
```

#### Performance Optimizations

**Streaming Compilation:**
```rust
pub struct StreamingCompiler {
    parser: WasmParser,
    compiler: BaselineCompiler,
    code_buffer: CodeBuffer,
}

impl StreamingCompiler {
    pub async fn compile_streaming(&mut self, wasm_bytes: &[u8]) -> Result<CompiledModule, CompilerError> {
        let mut offset = 0;
        let mut compiled_functions = Vec::new();
        
        // Parse and compile functions as they arrive
        while offset < wasm_bytes.len() {
            if let Some(function) = self.parser.try_parse_function(&wasm_bytes[offset..])? {
                // Compile immediately without waiting for full module
                let compiled_fn = self.compiler.compile_function(function)?;
                compiled_functions.push(compiled_fn);
                offset += function.byte_size();
            } else {
                // Wait for more data
                yield_to_runtime().await;
            }
        }
        
        Ok(CompiledModule::new(compiled_functions))
    }
}
```

**Optimized Memory Management:**
```rust
pub struct FastAllocator {
    memory_pool: MemoryPool,
    allocation_tracker: AllocationTracker,
}

impl FastAllocator {
    pub fn allocate(&mut self, size: usize) -> Result<*mut u8, AllocationError> {
        // Fast path: use pre-allocated pools
        if size <= 64 {
            return self.memory_pool.allocate_small(size);
        }
        if size <= 4096 {
            return self.memory_pool.allocate_medium(size);
        }
        
        // Fallback to system allocator for large allocations
        self.allocate_large(size)
    }
    
    pub fn deallocate(&mut self, ptr: *mut u8, size: usize) {
        self.allocation_tracker.record_deallocation(ptr, size);
        
        if size <= 4096 {
            // Return to pool for reuse
            self.memory_pool.deallocate(ptr, size);
        } else {
            // Return to system
            unsafe { std::alloc::dealloc(ptr, Layout::from_size_align_unchecked(size, 8)) };
        }
    }
}
```

#### Production Examples

**Edge-side Authentication:**
```rust
use fastly::http::{Method, StatusCode};
use fastly::{Error, Request, Response};
use serde_json::{json, Value};

#[fastly::main]
fn main(mut req: Request) -> Result<Response, Error> {
    match req.get_method() {
        &Method::POST if req.get_path() == "/auth/login" => handle_login(req),
        &Method::GET if req.get_path().starts_with("/protected/") => handle_protected(req),
        _ => proxy_to_origin(req),
    }
}

fn handle_login(mut req: Request) -> Result<Response, Error> {
    let body = req.take_body_str();
    let credentials: Value = serde_json::from_str(&body)
        .map_err(|_| Error::msg("Invalid JSON"))?;
    
    let username = credentials["username"].as_str()
        .ok_or_else(|| Error::msg("Missing username"))?;
    let password = credentials["password"].as_str()
        .ok_or_else(|| Error::msg("Missing password"))?;
    
    // Validate credentials against edge database
    let user_record = lookup_user_in_edge_db(username)?;
    
    if verify_password(password, &user_record.password_hash) {
        // Generate JWT token at the edge
        let token = generate_jwt_token(&user_record)?;
        
        Ok(Response::from_body(json!({
            "token": token,
            "expires_in": 3600
        }).to_string())
        .with_header("content-type", "application/json")
        .with_status(StatusCode::OK))
    } else {
        Ok(Response::from_status(StatusCode::UNAUTHORIZED))
    }
}

fn handle_protected(req: Request) -> Result<Response, Error> {
    // Extract JWT from Authorization header
    let auth_header = req.get_header("authorization")
        .and_then(|h| h.to_str().ok())
        .ok_or_else(|| Error::msg("Missing authorization header"))?;
    
    if !auth_header.starts_with("Bearer ") {
        return Ok(Response::from_status(StatusCode::UNAUTHORIZED));
    }
    
    let token = &auth_header[7..];
    
    // Verify JWT at the edge (no origin round-trip needed)
    match verify_jwt_token(token) {
        Ok(claims) => {
            // Add user context to request
            let mut modified_req = req;
            modified_req.set_header("x-user-id", &claims.user_id);
            modified_req.set_header("x-user-role", &claims.role);
            
            // Forward to origin with user context
            modified_req.send("origin")
        },
        Err(_) => Ok(Response::from_status(StatusCode::UNAUTHORIZED))
    }
}

// Optimized database operations
fn lookup_user_in_edge_db(username: &str) -> Result<UserRecord, Error> {
    // Use Fastly's edge-side key-value store
    let store = fastly::kv_store::KVStore::open("users")?;
    
    match store.lookup(username)? {
        Some(data) => {
            let user: UserRecord = serde_json::from_slice(&data)
                .map_err(|_| Error::msg("Invalid user record"))?;
            Ok(user)
        },
        None => Err(Error::msg("User not found"))
    }
}

#[derive(serde::Deserialize)]
struct UserRecord {
    user_id: String,
    password_hash: String,
    role: String,
}

#[derive(serde::Serialize, serde::Deserialize)]
struct JwtClaims {
    user_id: String,
    role: String,
    exp: u64,
}
```

### 3.3 Shopify Functions: Custom Checkout Logic

Shopify Functions uses WebAssembly to enable merchants to customize checkout logic with guaranteed performance and safety.

#### Architecture

```rust
// Shopify Functions runtime
pub struct ShopifyFunctionsRuntime {
    function_registry: FunctionRegistry,
    execution_engine: WasmExecutionEngine,
    checkout_context: CheckoutContext,
}

pub struct CheckoutFunction {
    wasm_module: CompiledModule,
    function_type: FunctionType,
    resource_limits: ResourceLimits,
}

pub enum FunctionType {
    DiscountCalculation,
    ShippingRates,
    PaymentValidation,
    TaxCalculation,
    InventoryCheck,
}

impl ShopifyFunctionsRuntime {
    pub async fn execute_discount_function(
        &self,
        function_id: &str,
        cart: &ShoppingCart,
        customer: &Customer
    ) -> Result<DiscountResult, ExecutionError> {
        let function = self.function_registry.get_function(function_id)?;
        
        // Ensure this is a discount calculation function
        match function.function_type {
            FunctionType::DiscountCalculation => {},
            _ => return Err(ExecutionError::InvalidFunctionType),
        }
        
        // Prepare execution context
        let input = DiscountInput {
            cart: cart.clone(),
            customer: customer.clone(),
            current_timestamp: SystemTime::now(),
        };
        
        // Execute with strict resource limits
        let execution_context = ExecutionContext::new()
            .with_memory_limit(16 * 1024 * 1024)  // 16MB
            .with_execution_time_limit(Duration::from_millis(50))  // 50ms max
            .with_network_access(false)  // No network access for security
            .with_file_system_access(false);  // No file system access
        
        let result = self.execution_engine
            .execute_function(&function.wasm_module, "calculate_discount", input, execution_context)
            .await?;
        
        Ok(result)
    }
}
```

#### Implementation Examples

**Discount Calculation Function (Rust):**
```rust
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct DiscountInput {
    cart: ShoppingCart,
    customer: Customer,
}

#[derive(Serialize)]
struct DiscountResult {
    discounts: Vec<Discount>,
    total_discount_amount: i64, // In cents
}

#[derive(Serialize)]
struct Discount {
    title: String,
    amount: i64,
    target: DiscountTarget,
}

#[derive(Serialize)]
enum DiscountTarget {
    OrderSubtotal,
    Product { product_id: String },
    Shipping,
}

#[no_mangle]
pub extern "C" fn calculate_discount(input_ptr: i32, input_len: i32) -> i32 {
    let input_data = unsafe {
        std::slice::from_raw_parts(input_ptr as *const u8, input_len as usize)
    };
    
    let input: DiscountInput = serde_json::from_slice(input_data)
        .expect("Invalid input format");
    
    let mut discounts = Vec::new();
    let mut total_discount = 0i64;
    
    // Volume discount logic
    if input.cart.total_quantity() >= 10 {
        let volume_discount = Discount {
            title: "Volume Discount (10+ items)".to_string(),
            amount: input.cart.subtotal_cents() * 10 / 100, // 10% off
            target: DiscountTarget::OrderSubtotal,
        };
        total_discount += volume_discount.amount;
        discounts.push(volume_discount);
    }
    
    // Customer loyalty discount
    if input.customer.loyalty_tier == "gold" {
        let loyalty_discount = Discount {
            title: "Gold Member Discount".to_string(),
            amount: input.cart.subtotal_cents() * 15 / 100, // 15% off
            target: DiscountTarget::OrderSubtotal,
        };
        total_discount += loyalty_discount.amount;
        discounts.push(loyalty_discount);
    }
    
    // Product-specific discounts
    for item in &input.cart.line_items {
        if item.product.tags.contains(&"sale".to_string()) {
            let product_discount = Discount {
                title: format!("Sale Price: {}", item.product.title),
                amount: item.original_price_cents - item.sale_price_cents,
                target: DiscountTarget::Product {
                    product_id: item.product.id.clone(),
                },
            };
            total_discount += product_discount.amount;
            discounts.push(product_discount);
        }
    }
    
    let result = DiscountResult {
        discounts,
        total_discount_amount: total_discount,
    };
    
    let result_json = serde_json::to_string(&result)
        .expect("Failed to serialize result");
    
    // Allocate memory for result and return pointer
    let result_bytes = result_json.as_bytes();
    let result_ptr = allocate(result_bytes.len());
    unsafe {
        std::ptr::copy_nonoverlapping(
            result_bytes.as_ptr(),
            result_ptr,
            result_bytes.len()
        );
    }
    
    result_ptr as i32
}

// Memory management functions
static mut HEAP: Vec<u8> = Vec::new();
static mut HEAP_OFFSET: usize = 0;

#[no_mangle]
pub extern "C" fn allocate(size: usize) -> *mut u8 {
    unsafe {
        if HEAP.len() < HEAP_OFFSET + size {
            HEAP.resize(HEAP_OFFSET + size + 1024, 0);
        }
        let ptr = HEAP.as_mut_ptr().add(HEAP_OFFSET);
        HEAP_OFFSET += size;
        ptr
    }
}

// Data structures
#[derive(Deserialize)]
struct ShoppingCart {
    line_items: Vec<LineItem>,
}

impl ShoppingCart {
    fn total_quantity(&self) -> i32 {
        self.line_items.iter().map(|item| item.quantity).sum()
    }
    
    fn subtotal_cents(&self) -> i64 {
        self.line_items.iter()
            .map(|item| item.price_cents * item.quantity as i64)
            .sum()
    }
}

#[derive(Deserialize)]
struct LineItem {
    product: Product,
    quantity: i32,
    price_cents: i64,
    original_price_cents: i64,
    sale_price_cents: i64,
}

#[derive(Deserialize)]
struct Product {
    id: String,
    title: String,
    tags: Vec<String>,
}

#[derive(Deserialize)]
struct Customer {
    id: String,
    email: String,
    loyalty_tier: String,
    total_orders: i32,
}
```

**Shipping Rate Calculator:**
```rust
use geo::{Point, distance::Distance};

#[derive(Deserialize)]
struct ShippingInput {
    cart: ShoppingCart,
    shipping_address: Address,
    merchant_location: Address,
}

#[derive(Serialize)]
struct ShippingResult {
    shipping_rates: Vec<ShippingRate>,
}

#[derive(Serialize)]
struct ShippingRate {
    name: String,
    price_cents: i64,
    estimated_delivery_days: i32,
    carrier: String,
}

#[no_mangle]
pub extern "C" fn calculate_shipping(input_ptr: i32, input_len: i32) -> i32 {
    let input_data = unsafe {
        std::slice::from_raw_parts(input_ptr as *const u8, input_len as usize)
    };
    
    let input: ShippingInput = serde_json::from_slice(input_data)
        .expect("Invalid input format");
    
    let mut rates = Vec::new();
    
    // Calculate distance
    let merchant_point = Point::new(input.merchant_location.longitude, input.merchant_location.latitude);
    let customer_point = Point::new(input.shipping_address.longitude, input.shipping_address.latitude);
    let distance_km = merchant_point.distance(&customer_point) / 1000.0;
    
    // Calculate package weight and dimensions
    let total_weight = calculate_total_weight(&input.cart);
    let package_dimensions = calculate_package_dimensions(&input.cart);
    
    // Standard shipping
    let standard_rate = ShippingRate {
        name: "Standard Shipping".to_string(),
        price_cents: calculate_standard_shipping_cost(distance_km, total_weight),
        estimated_delivery_days: estimate_standard_delivery_time(distance_km),
        carrier: "Local Carrier".to_string(),
    };
    rates.push(standard_rate);
    
    // Express shipping
    if distance_km < 500.0 { // Only available for nearby locations
        let express_rate = ShippingRate {
            name: "Express Shipping".to_string(),
            price_cents: calculate_express_shipping_cost(distance_km, total_weight),
            estimated_delivery_days: 1,
            carrier: "Express Carrier".to_string(),
        };
        rates.push(express_rate);
    }
    
    // Free shipping for orders over $100
    if input.cart.subtotal_cents() >= 10000 { // $100 in cents
        rates.push(ShippingRate {
            name: "Free Shipping".to_string(),
            price_cents: 0,
            estimated_delivery_days: estimate_standard_delivery_time(distance_km) + 1,
            carrier: "Standard Carrier".to_string(),
        });
    }
    
    let result = ShippingResult {
        shipping_rates: rates,
    };
    
    serialize_and_return(result)
}

fn calculate_standard_shipping_cost(distance_km: f64, weight_kg: f64) -> i64 {
    // Base rate + distance rate + weight rate
    let base_rate = 500; // $5.00 in cents
    let distance_rate = (distance_km * 0.1) as i64; // $0.10 per km
    let weight_rate = (weight_kg * 200.0) as i64; // $2.00 per kg
    
    base_rate + distance_rate + weight_rate
}

fn calculate_express_shipping_cost(distance_km: f64, weight_kg: f64) -> i64 {
    calculate_standard_shipping_cost(distance_km, weight_kg) * 2
}

#[derive(Deserialize)]
struct Address {
    street: String,
    city: String,
    province: String,
    postal_code: String,
    country: String,
    latitude: f64,
    longitude: f64,
}
```

### 3.4 Figma: Multiplayer Collaboration Engine

Figma uses WebAssembly for real-time collaborative editing with complex geometric operations.

#### Real-time Collaboration Architecture

```rust
// Figma's collaborative editing engine
pub struct CollaborationEngine {
    document_state: Arc<RwLock<DocumentState>>,
    operation_transformer: OperationalTransform,
    conflict_resolver: ConflictResolver,
    network_manager: NetworkManager,
}

pub struct DocumentState {
    objects: HashMap<ObjectId, DrawingObject>,
    layers: Vec<LayerId>,
    version: DocumentVersion,
    active_selections: HashMap<UserId, Selection>,
}

#[derive(Clone, Debug)]
pub struct Operation {
    id: OperationId,
    user_id: UserId,
    timestamp: SystemTime,
    operation_type: OperationType,
    affected_objects: Vec<ObjectId>,
}

#[derive(Clone, Debug)]
pub enum OperationType {
    CreateObject {
        object: DrawingObject,
    },
    MoveObject {
        object_id: ObjectId,
        delta: Vector2D,
    },
    ResizeObject {
        object_id: ObjectId,
        new_bounds: Rect,
    },
    ChangeProperty {
        object_id: ObjectId,
        property: String,
        old_value: PropertyValue,
        new_value: PropertyValue,
    },
    DeleteObject {
        object_id: ObjectId,
    },
}

impl CollaborationEngine {
    pub async fn apply_operation(&self, operation: Operation) -> Result<DocumentDelta, CollaborationError> {
        let mut document = self.document_state.write().await;
        
        // Check for conflicts with concurrent operations
        let conflicting_ops = self.detect_conflicts(&operation, &document).await;
        
        if !conflicting_ops.is_empty() {
            // Resolve conflicts using operational transformation
            let resolved_op = self.conflict_resolver.resolve_conflicts(operation, conflicting_ops)?;
            
            // Apply transformed operation
            let delta = self.apply_operation_internal(&mut document, resolved_op)?;
            
            // Broadcast to other clients
            self.network_manager.broadcast_operation(&delta).await?;
            
            Ok(delta)
        } else {
            // No conflicts, apply directly
            let delta = self.apply_operation_internal(&mut document, operation)?;
            
            // Broadcast to other clients
            self.network_manager.broadcast_operation(&delta).await?;
            
            Ok(delta)
        }
    }
    
    fn apply_operation_internal(
        &self,
        document: &mut DocumentState,
        operation: Operation
    ) -> Result<DocumentDelta, CollaborationError> {
        match operation.operation_type {
            OperationType::CreateObject { object } => {
                document.objects.insert(object.id, object.clone());
                Ok(DocumentDelta::ObjectCreated { object })
            },
            OperationType::MoveObject { object_id, delta } => {
                if let Some(object) = document.objects.get_mut(&object_id) {
                    let old_position = object.bounds.origin;
                    object.bounds.origin += delta;
                    
                    Ok(DocumentDelta::ObjectMoved {
                        object_id,
                        old_position,
                        new_position: object.bounds.origin,
                    })
                } else {
                    Err(CollaborationError::ObjectNotFound(object_id))
                }
            },
            OperationType::ResizeObject { object_id, new_bounds } => {
                if let Some(object) = document.objects.get_mut(&object_id) {
                    let old_bounds = object.bounds;
                    object.bounds = new_bounds;
                    
                    Ok(DocumentDelta::ObjectResized {
                        object_id,
                        old_bounds,
                        new_bounds,
                    })
                } else {
                    Err(CollaborationError::ObjectNotFound(object_id))
                }
            },
            // ... other operation types
            _ => todo!("Implement other operation types"),
        }
    }
}

// Geometric operations for design tools
#[no_mangle]
pub extern "C" fn calculate_bezier_intersection(
    curve1_ptr: i32, curve1_len: i32,
    curve2_ptr: i32, curve2_len: i32
) -> i32 {
    let curve1_data = unsafe {
        std::slice::from_raw_parts(curve1_ptr as *const u8, curve1_len as usize)
    };
    let curve2_data = unsafe {
        std::slice::from_raw_parts(curve2_ptr as *const u8, curve2_len as usize)
    };
    
    let curve1: BezierCurve = bincode::deserialize(curve1_data).unwrap();
    let curve2: BezierCurve = bincode::deserialize(curve2_data).unwrap();
    
    let intersections = find_bezier_intersections(&curve1, &curve2);
    
    let result = IntersectionResult {
        points: intersections,
    };
    
    let result_data = bincode::serialize(&result).unwrap();
    
    // Allocate memory and return result
    let result_ptr = allocate(result_data.len());
    unsafe {
        std::ptr::copy_nonoverlapping(
            result_data.as_ptr(),
            result_ptr,
            result_data.len()
        );
    }
    
    result_ptr as i32
}

// High-performance geometric calculations
fn find_bezier_intersections(curve1: &BezierCurve, curve2: &BezierCurve) -> Vec<Point2D> {
    let mut intersections = Vec::new();
    
    // Use recursive subdivision for precise intersection finding
    let tolerance = 1e-6;
    
    find_intersections_recursive(
        curve1, 0.0, 1.0,
        curve2, 0.0, 1.0,
        tolerance,
        &mut intersections
    );
    
    // Remove duplicate points
    deduplicate_points(&mut intersections, tolerance);
    
    intersections
}

fn find_intersections_recursive(
    curve1: &BezierCurve, t1_start: f64, t1_end: f64,
    curve2: &BezierCurve, t2_start: f64, t2_end: f64,
    tolerance: f64,
    intersections: &mut Vec<Point2D>
) {
    // Calculate bounding boxes for current curve segments
    let bbox1 = calculate_bezier_bbox(curve1, t1_start, t1_end);
    let bbox2 = calculate_bezier_bbox(curve2, t2_start, t2_end);
    
    // Quick rejection test
    if !bbox1.intersects(&bbox2) {
        return;
    }
    
    // Check if we've reached sufficient precision
    let segment1_size = (t1_end - t1_start).abs();
    let segment2_size = (t2_end - t2_start).abs();
    
    if segment1_size < tolerance && segment2_size < tolerance {
        // Found an intersection point
        let t1_mid = (t1_start + t1_end) * 0.5;
        let intersection_point = evaluate_bezier(curve1, t1_mid);
        intersections.push(intersection_point);
        return;
    }
    
    // Subdivide the longer curve
    if segment1_size > segment2_size {
        let t1_mid = (t1_start + t1_end) * 0.5;
        
        find_intersections_recursive(
            curve1, t1_start, t1_mid,
            curve2, t2_start, t2_end,
            tolerance, intersections
        );
        
        find_intersections_recursive(
            curve1, t1_mid, t1_end,
            curve2, t2_start, t2_end,
            tolerance, intersections
        );
    } else {
        let t2_mid = (t2_start + t2_end) * 0.5;
        
        find_intersections_recursive(
            curve1, t1_start, t1_end,
            curve2, t2_start, t2_mid,
            tolerance, intersections
        );
        
        find_intersections_recursive(
            curve1, t1_start, t1_end,
            curve2, t2_mid, t2_end,
            tolerance, intersections
        );
    }
}

#[derive(serde::Serialize, serde::Deserialize)]
struct BezierCurve {
    p0: Point2D,
    p1: Point2D,
    p2: Point2D,
    p3: Point2D,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Copy, Debug)]
struct Point2D {
    x: f64,
    y: f64,
}

#[derive(serde::Serialize, serde::Deserialize)]
struct Rect {
    origin: Point2D,
    size: Size2D,
}

#[derive(serde::Serialize, serde::Deserialize)]
struct Size2D {
    width: f64,
    height: f64,
}

impl Rect {
    fn intersects(&self, other: &Rect) -> bool {
        self.origin.x < other.origin.x + other.size.width &&
        self.origin.x + self.size.width > other.origin.x &&
        self.origin.y < other.origin.y + other.size.height &&
        self.origin.y + self.size.height > other.origin.y
    }
}
```

### 3.5 Discord: Activity Platform

Discord uses WebAssembly for their Activities platform, enabling safe execution of third-party mini-applications within the Discord client.

#### Security-First Architecture

```rust
// Discord Activities WASM runtime
pub struct DiscordActivitiesRuntime {
    sandbox_manager: SandboxManager,
    permission_system: PermissionSystem,
    resource_monitor: ResourceMonitor,
    api_gateway: ApiGateway,
}

pub struct ActivitySandbox {
    isolate: WasmIsolate,
    permissions: ActivityPermissions,
    resource_limits: ResourceLimits,
    api_bindings: ApiBindings,
}

#[derive(Debug, Clone)]
pub struct ActivityPermissions {
    can_access_user_info: bool,
    can_access_voice_channel: bool,
    can_send_messages: bool,
    can_access_guild_info: bool,
    max_network_requests_per_minute: u32,
    allowed_domains: Vec<String>,
}

impl DiscordActivitiesRuntime {
    pub async fn create_activity_sandbox(
        &self,
        activity_id: &str,
        wasm_code: &[u8],
        permissions: ActivityPermissions
    ) -> Result<ActivitySandbox, RuntimeError> {
        // Validate WASM code for security
        self.validate_wasm_security(wasm_code)?;
        
        // Create isolated execution environment
        let isolate = WasmIsolate::new_with_limits(ResourceLimits {
            max_memory: 32 * 1024 * 1024, // 32MB
            max_execution_time: Duration::from_secs(5),
            max_file_descriptors: 0, // No file access
            max_network_connections: 5,
        })?;
        
        // Set up API bindings based on permissions
        let api_bindings = self.create_api_bindings(&permissions)?;
        
        Ok(ActivitySandbox {
            isolate,
            permissions,
            resource_limits: ResourceLimits::default(),
            api_bindings,
        })
    }
    
    pub async fn execute_activity_function(
        &self,
        sandbox: &mut ActivitySandbox,
        function_name: &str,
        args: &[u8]
    ) -> Result<Vec<u8>, RuntimeError> {
        // Check resource usage before execution
        self.resource_monitor.check_limits(&sandbox.resource_limits)?;
        
        // Execute with security context
        let execution_context = SecurityContext::new()
            .with_permissions(sandbox.permissions.clone())
            .with_api_bindings(sandbox.api_bindings.clone());
        
        sandbox.isolate.call_function_with_context(
            function_name,
            args,
            execution_context
        ).await
    }
}

// Example Discord Activity implementation
#[no_mangle]
pub extern "C" fn activity_main() {
    // Initialize activity
    register_event_handlers();
    
    // Set up UI
    create_activity_ui();
    
    // Start activity loop
    activity_loop();
}

#[no_mangle]
pub extern "C" fn on_user_join(user_data_ptr: i32, user_data_len: i32) {
    let user_data = unsafe {
        std::slice::from_raw_parts(user_data_ptr as *const u8, user_data_len as usize)
    };
    
    let user: DiscordUser = serde_json::from_slice(user_data).unwrap();
    
    // Welcome new user to activity
    send_activity_message(&format!("Welcome {}! 🎉", user.username));
    
    // Update activity state
    update_participant_list(user);
}

#[no_mangle]
pub extern "C" fn on_activity_command(command_ptr: i32, command_len: i32) -> i32 {
    let command_data = unsafe {
        std::slice::from_raw_parts(command_ptr as *const u8, command_len as usize)
    };
    
    let command: ActivityCommand = serde_json::from_slice(command_data).unwrap();
    
    let response = match command.command_type.as_str() {
        "start_game" => handle_start_game(command),
        "make_move" => handle_make_move(command),
        "get_leaderboard" => handle_get_leaderboard(command),
        _ => ActivityResponse::error("Unknown command"),
    };
    
    let response_data = serde_json::to_vec(&response).unwrap();
    
    // Allocate and return response
    let response_ptr = allocate(response_data.len());
    unsafe {
        std::ptr::copy_nonoverlapping(
            response_data.as_ptr(),
            response_ptr,
            response_data.len()
        );
    }
    
    response_ptr as i32
}

// Game logic example - multiplayer tic-tac-toe
static mut GAME_STATE: Option<TicTacToeGame> = None;

struct TicTacToeGame {
    board: [Option<Player>; 9],
    current_player: Player,
    players: Vec<DiscordUser>,
    game_status: GameStatus,
}

#[derive(Clone, Copy, PartialEq)]
enum Player {
    X,
    O,
}

enum GameStatus {
    WaitingForPlayers,
    InProgress,
    Finished { winner: Option<Player> },
}

fn handle_start_game(command: ActivityCommand) -> ActivityResponse {
    unsafe {
        if GAME_STATE.is_some() {
            return ActivityResponse::error("Game already in progress");
        }
        
        if command.participants.len() < 2 {
            return ActivityResponse::error("Need at least 2 players");
        }
        
        GAME_STATE = Some(TicTacToeGame {
            board: [None; 9],
            current_player: Player::X,
            players: command.participants,
            game_status: GameStatus::InProgress,
        });
        
        // Notify all participants
        broadcast_game_state();
        
        ActivityResponse::success("Game started!")
    }
}

fn handle_make_move(command: ActivityCommand) -> ActivityResponse {
    unsafe {
        let game = match &mut GAME_STATE {
            Some(game) => game,
            None => return ActivityResponse::error("No active game"),
        };
        
        // Validate move
        let position: usize = command.data["position"].as_u64().unwrap() as usize;
        
        if position >= 9 {
            return ActivityResponse::error("Invalid position");
        }
        
        if game.board[position].is_some() {
            return ActivityResponse::error("Position already taken");
        }
        
        // Check if it's the player's turn
        let player_index = game.players.iter()
            .position(|p| p.id == command.user.id);
        
        match player_index {
            Some(0) if game.current_player == Player::X => {},
            Some(1) if game.current_player == Player::O => {},
            _ => return ActivityResponse::error("Not your turn"),
        }
        
        // Make the move
        game.board[position] = Some(game.current_player);
        
        // Check for winner
        if let Some(winner) = check_winner(&game.board) {
            game.game_status = GameStatus::Finished { winner: Some(winner) };
            
            let winner_name = match winner {
                Player::X => &game.players[0].username,
                Player::O => &game.players[1].username,
            };
            
            send_activity_message(&format!("🎉 {} wins!", winner_name));
        } else if game.board.iter().all(|&cell| cell.is_some()) {
            // Draw
            game.game_status = GameStatus::Finished { winner: None };
            send_activity_message("It's a draw! 🤝");
        } else {
            // Switch turns
            game.current_player = match game.current_player {
                Player::X => Player::O,
                Player::O => Player::X,
            };
        }
        
        broadcast_game_state();
        ActivityResponse::success("Move made")
    }
}

fn check_winner(board: &[Option<Player>; 9]) -> Option<Player> {
    let winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
        [0, 4, 8], [2, 4, 6],             // Diagonals
    ];
    
    for combination in &winning_combinations {
        match (board[combination[0]], board[combination[1]], board[combination[2]]) {
            (Some(player), Some(p2), Some(p3)) if player == p2 && player == p3 => {
                return Some(player);
            }
            _ => continue,
        }
    }
    
    None
}

// Discord API bindings (safe wrappers)
extern "C" {
    fn discord_send_message(message_ptr: *const u8, message_len: usize);
    fn discord_update_activity_state(state_ptr: *const u8, state_len: usize);
    fn discord_get_voice_channel_users() -> i32;
}

fn send_activity_message(message: &str) {
    let message_bytes = message.as_bytes();
    unsafe {
        discord_send_message(message_bytes.as_ptr(), message_bytes.len());
    }
}

fn broadcast_game_state() {
    unsafe {
        if let Some(game) = &GAME_STATE {
            let state = serde_json::to_string(game).unwrap();
            let state_bytes = state.as_bytes();
            discord_update_activity_state(state_bytes.as_ptr(), state_bytes.len());
        }
    }
}

#[derive(serde::Deserialize)]
struct DiscordUser {
    id: String,
    username: String,
    avatar: String,
}

#[derive(serde::Deserialize)]
struct ActivityCommand {
    command_type: String,
    user: DiscordUser,
    participants: Vec<DiscordUser>,
    data: serde_json::Value,
}

#[derive(serde::Serialize)]
struct ActivityResponse {
    success: bool,
    message: String,
    data: Option<serde_json::Value>,
}

impl ActivityResponse {
    fn success(message: &str) -> Self {
        Self {
            success: true,
            message: message.to_string(),
            data: None,
        }
    }
    
    fn error(message: &str) -> Self {
        Self {
            success: false,
            message: message.to_string(),
            data: None,
        }
    }
}
```

---

## Part 4: Research & Extensions (15 minutes)

### 4.1 WASI (WebAssembly System Interface)

WASI provides standardized system interfaces for WebAssembly, enabling portable system programming.

#### WASI Architecture

```rust
// WASI implementation example
use wasi_common::{WasiCtx, WasiCtxBuilder};
use wasmtime::{Engine, Linker, Module, Store};
use wasmtime_wasi::WasiCtxBuilder as WasmtimeWasiCtxBuilder;

struct WasiRuntime {
    engine: Engine,
    linker: Linker<WasiCtx>,
}

impl WasiRuntime {
    fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let engine = Engine::default();
        let mut linker = Linker::new(&engine);
        
        // Add WASI functions to linker
        wasmtime_wasi::add_to_linker(&mut linker, |s| s)?;
        
        Ok(Self { engine, linker })
    }
    
    async fn run_wasi_program(&self, wasm_bytes: &[u8], args: Vec<String>) -> Result<i32, Box<dyn std::error::Error>> {
        let module = Module::new(&self.engine, wasm_bytes)?;
        
        // Set up WASI context
        let wasi_ctx = WasmtimeWasiCtxBuilder::new()
            .inherit_stdio()
            .args(&args)?
            .build();
        
        let mut store = Store::new(&self.engine, wasi_ctx);
        
        // Instantiate and run
        let instance = self.linker.instantiate_async(&mut store, &module).await?;
        let start = instance.get_typed_func::<(), ()>(&mut store, "_start")?;
        
        match start.call_async(&mut store, ()).await {
            Ok(()) => Ok(0),
            Err(trap) => {
                if let Some(exit_code) = trap.downcast_ref::<wasmtime_wasi::I32Exit>() {
                    Ok(exit_code.0)
                } else {
                    Err(trap.into())
                }
            }
        }
    }
}

// WASI program example
use std::env;
use std::fs;
use std::io::Write;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    
    if args.len() != 3 {
        eprintln!("Usage: {} <input_file> <output_file>", args[0]);
        return Ok(());
    }
    
    let input_path = &args[1];
    let output_path = &args[2];
    
    // Read input file
    let content = fs::read_to_string(input_path)?;
    
    // Process content (example: convert to uppercase)
    let processed = content.to_uppercase();
    
    // Write output file
    let mut output_file = fs::File::create(output_path)?;
    output_file.write_all(processed.as_bytes())?;
    
    println!("Successfully processed {} -> {}", input_path, output_path);
    
    Ok(())
}
```

#### WASI Security Model

```rust
// Capability-based security in WASI
use cap_std::fs::{Dir, DirBuilder};
use cap_std::net::TcpListener;

struct SecureWasiContext {
    allowed_dirs: Vec<Dir>,
    allowed_network: bool,
    resource_limits: ResourceLimits,
}

impl SecureWasiContext {
    fn new() -> Self {
        Self {
            allowed_dirs: Vec::new(),
            allowed_network: false,
            resource_limits: ResourceLimits::default(),
        }
    }
    
    fn allow_directory_access<P: AsRef<std::path::Path>>(&mut self, path: P) -> Result<(), std::io::Error> {
        let dir = Dir::open_ambient_dir(path, cap_std::ambient_authority())?;
        self.allowed_dirs.push(dir);
        Ok(())
    }
    
    fn allow_network_access(&mut self) {
        self.allowed_network = true;
    }
    
    fn build_wasi_ctx(&self) -> Result<WasiCtx, Box<dyn std::error::Error>> {
        let mut builder = WasiCtxBuilder::new();
        
        // Add directory capabilities
        for (index, dir) in self.allowed_dirs.iter().enumerate() {
            builder = builder.preopened_dir(dir.try_clone()?, format!("/dir{}", index))?;
        }
        
        // Configure network access
        if self.allowed_network {
            // Allow network access with restrictions
            builder = builder.inherit_network();
        }
        
        Ok(builder.build())
    }
}
```

### 4.2 Component Model and Interface Types

The WebAssembly Component Model enables composition of WASM modules with type-safe interfaces.

#### Component Interface Types (WIT)

```wit
// world.wit - Interface definition
package example:calculator;

interface math {
  add: func(a: f64, b: f64) -> f64;
  subtract: func(a: f64, b: f64) -> f64;
  multiply: func(a: f64, b: f64) -> f64;
  divide: func(a: f64, b: f64) -> result<f64, string>;
}

interface statistics {
  record dataset {
    values: list<f64>,
    name: string,
  }
  
  mean: func(data: dataset) -> f64;
  variance: func(data: dataset) -> f64;
  correlation: func(x: dataset, y: dataset) -> f64;
}

world calculator {
  export math;
  export statistics;
  import console: interface {
    log: func(message: string);
  }
}
```

#### Component Implementation

```rust
// Component implementation using wit-bindgen
wit_bindgen::generate!({
    world: "calculator",
    exports: {
        "example:calculator/math": Math,
        "example:calculator/statistics": Statistics,
    },
});

struct Math;

impl exports::example::calculator::math::Guest for Math {
    fn add(a: f64, b: f64) -> f64 {
        a + b
    }
    
    fn subtract(a: f64, b: f64) -> f64 {
        a - b
    }
    
    fn multiply(a: f64, b: f64) -> f64 {
        a * b
    }
    
    fn divide(a: f64, b: f64) -> Result<f64, String> {
        if b == 0.0 {
            Err("Division by zero".to_string())
        } else {
            Ok(a / b)
        }
    }
}

struct Statistics;

impl exports::example::calculator::statistics::Guest for Statistics {
    fn mean(data: exports::example::calculator::statistics::Dataset) -> f64 {
        if data.values.is_empty() {
            return 0.0;
        }
        
        let sum: f64 = data.values.iter().sum();
        sum / data.values.len() as f64
    }
    
    fn variance(data: exports::example::calculator::statistics::Dataset) -> f64 {
        if data.values.len() < 2 {
            return 0.0;
        }
        
        let mean = Self::mean(data.clone());
        let sum_squared_diff: f64 = data.values
            .iter()
            .map(|&x| (x - mean).powi(2))
            .sum();
        
        sum_squared_diff / (data.values.len() - 1) as f64
    }
    
    fn correlation(
        x: exports::example::calculator::statistics::Dataset,
        y: exports::example::calculator::statistics::Dataset
    ) -> f64 {
        if x.values.len() != y.values.len() || x.values.len() < 2 {
            return 0.0;
        }
        
        let mean_x = Self::mean(x.clone());
        let mean_y = Self::mean(y.clone());
        
        let numerator: f64 = x.values
            .iter()
            .zip(y.values.iter())
            .map(|(&xi, &yi)| (xi - mean_x) * (yi - mean_y))
            .sum();
        
        let sum_x_squared: f64 = x.values
            .iter()
            .map(|&xi| (xi - mean_x).powi(2))
            .sum();
        
        let sum_y_squared: f64 = y.values
            .iter()
            .map(|&yi| (yi - mean_y).powi(2))
            .sum();
        
        let denominator = (sum_x_squared * sum_y_squared).sqrt();
        
        if denominator == 0.0 {
            0.0
        } else {
            numerator / denominator
        }
    }
}

// Using imported console interface
fn log_calculation(operation: &str, result: f64) {
    let message = format!("Calculation: {} = {}", operation, result);
    example::calculator::console::log(&message);
}
```

#### Component Composition

```rust
// Composing components
use wasmtime::{Engine, Store, component::{Component, Linker}};

struct ComponentRuntime {
    engine: Engine,
    linker: Linker,
}

impl ComponentRuntime {
    fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let engine = Engine::default();
        let mut linker = Linker::new(&engine);
        
        // Add host implementations
        Self::add_host_functions(&mut linker)?;
        
        Ok(Self { engine, linker })
    }
    
    fn add_host_functions(linker: &mut Linker) -> Result<(), Box<dyn std::error::Error>> {
        // Implement console interface
        linker.root().func_wrap("log", |message: String| {
            println!("[Component]: {}", message);
        })?;
        
        Ok(())
    }
    
    async fn run_calculator_component(&self, wasm_bytes: &[u8]) -> Result<(), Box<dyn std::error::Error>> {
        let component = Component::new(&self.engine, wasm_bytes)?;
        let mut store = Store::new(&self.engine, ());
        
        let instance = self.linker.instantiate_async(&mut store, &component).await?;
        
        // Get exported interfaces
        let math_interface = instance.get_export(&mut store, None, "example:calculator/math");
        let stats_interface = instance.get_export(&mut store, None, "example:calculator/statistics");
        
        // Use the calculator
        self.demo_calculator_usage(&mut store, math_interface, stats_interface).await?;
        
        Ok(())
    }
    
    async fn demo_calculator_usage(
        &self,
        store: &mut Store<()>,
        math: Option<wasmtime::component::Export>,
        stats: Option<wasmtime::component::Export>
    ) -> Result<(), Box<dyn std::error::Error>> {
        // Example usage of component interfaces
        if let (Some(math), Some(stats)) = (math, stats) {
            // Perform calculations
            println!("Component calculator demo");
            
            // This would be implemented with proper component interface calls
            // The actual implementation depends on the specific component model runtime
        }
        
        Ok(())
    }
}
```

### 4.3 Shared Memory and Threading

WebAssembly threads enable parallel computation with shared memory.

#### Shared Memory Implementation

```rust
// Shared memory WebAssembly implementation
use std::sync::atomic::{AtomicI32, AtomicUsize, Ordering};
use std::sync::Arc;
use rayon::prelude::*;

#[repr(C)]
struct SharedBuffer {
    data: *mut f64,
    length: usize,
    reference_count: AtomicI32,
}

static mut SHARED_BUFFERS: Vec<Arc<SharedBuffer>> = Vec::new();
static BUFFER_COUNT: AtomicUsize = AtomicUsize::new(0);

#[no_mangle]
pub extern "C" fn create_shared_buffer(size: usize) -> i32 {
    let data = unsafe {
        let layout = std::alloc::Layout::from_size_align_unchecked(
            size * std::mem::size_of::<f64>(),
            std::mem::align_of::<f64>()
        );
        std::alloc::alloc(layout) as *mut f64
    };
    
    if data.is_null() {
        return -1; // Allocation failed
    }
    
    let buffer = Arc::new(SharedBuffer {
        data,
        length: size,
        reference_count: AtomicI32::new(1),
    });
    
    unsafe {
        let buffer_id = BUFFER_COUNT.fetch_add(1, Ordering::SeqCst);
        
        // Ensure we have enough space
        while SHARED_BUFFERS.len() <= buffer_id {
            SHARED_BUFFERS.push(Arc::new(SharedBuffer {
                data: std::ptr::null_mut(),
                length: 0,
                reference_count: AtomicI32::new(0),
            }));
        }
        
        SHARED_BUFFERS[buffer_id] = buffer;
        buffer_id as i32
    }
}

#[no_mangle]
pub extern "C" fn parallel_matrix_multiply(
    a_buffer_id: i32,
    b_buffer_id: i32,
    result_buffer_id: i32,
    rows_a: usize,
    cols_a: usize,
    cols_b: usize
) -> i32 {
    unsafe {
        let buffer_a = &SHARED_BUFFERS[a_buffer_id as usize];
        let buffer_b = &SHARED_BUFFERS[b_buffer_id as usize];
        let buffer_result = &SHARED_BUFFERS[result_buffer_id as usize];
        
        // Verify buffer dimensions
        if buffer_a.length != rows_a * cols_a ||
           buffer_b.length != cols_a * cols_b ||
           buffer_result.length != rows_a * cols_b {
            return -1; // Dimension mismatch
        }
        
        let a_slice = std::slice::from_raw_parts(buffer_a.data, buffer_a.length);
        let b_slice = std::slice::from_raw_parts(buffer_b.data, buffer_b.length);
        let result_slice = std::slice::from_raw_parts_mut(buffer_result.data, buffer_result.length);
        
        // Parallel matrix multiplication using Rayon
        (0..rows_a).into_par_iter().for_each(|i| {
            for j in 0..cols_b {
                let mut sum = 0.0;
                for k in 0..cols_a {
                    sum += a_slice[i * cols_a + k] * b_slice[k * cols_b + j];
                }
                result_slice[i * cols_b + j] = sum;
            }
        });
        
        0 // Success
    }
}

// Thread-safe operations
#[no_mangle]
pub extern "C" fn parallel_reduce_sum(buffer_id: i32) -> f64 {
    unsafe {
        let buffer = &SHARED_BUFFERS[buffer_id as usize];
        let slice = std::slice::from_raw_parts(buffer.data, buffer.length);
        
        // Parallel reduction
        slice.par_iter().sum()
    }
}

#[no_mangle]
pub extern "C" fn parallel_map_sqrt(buffer_id: i32) -> i32 {
    unsafe {
        let buffer = &SHARED_BUFFERS[buffer_id as usize];
        let slice = std::slice::from_raw_parts_mut(buffer.data, buffer.length);
        
        // Parallel map operation
        slice.par_iter_mut().for_each(|x| *x = x.sqrt());
        
        0 // Success
    }
}

// Memory barrier operations
#[no_mangle]
pub extern "C" fn memory_barrier() {
    std::sync::atomic::fence(Ordering::SeqCst);
}

// Lock-free data structures
use std::sync::atomic::AtomicPtr;

struct LockFreeQueue<T> {
    head: AtomicPtr<Node<T>>,
    tail: AtomicPtr<Node<T>>,
}

struct Node<T> {
    data: Option<T>,
    next: AtomicPtr<Node<T>>,
}

impl<T> LockFreeQueue<T> {
    fn new() -> Self {
        let dummy = Box::into_raw(Box::new(Node {
            data: None,
            next: AtomicPtr::new(std::ptr::null_mut()),
        }));
        
        Self {
            head: AtomicPtr::new(dummy),
            tail: AtomicPtr::new(dummy),
        }
    }
    
    fn enqueue(&self, item: T) {
        let new_node = Box::into_raw(Box::new(Node {
            data: Some(item),
            next: AtomicPtr::new(std::ptr::null_mut()),
        }));
        
        loop {
            let tail = self.tail.load(Ordering::Acquire);
            let next = unsafe { (*tail).next.load(Ordering::Acquire) };
            
            if tail == self.tail.load(Ordering::Acquire) {
                if next.is_null() {
                    if unsafe { (*tail).next.compare_exchange_weak(
                        next,
                        new_node,
                        Ordering::Release,
                        Ordering::Relaxed
                    ).is_ok() } {
                        break;
                    }
                } else {
                    let _ = self.tail.compare_exchange_weak(
                        tail,
                        next,
                        Ordering::Release,
                        Ordering::Relaxed
                    );
                }
            }
        }
        
        let _ = self.tail.compare_exchange(
            self.tail.load(Ordering::Acquire),
            new_node,
            Ordering::Release,
            Ordering::Relaxed
        );
    }
    
    fn dequeue(&self) -> Option<T> {
        loop {
            let head = self.head.load(Ordering::Acquire);
            let tail = self.tail.load(Ordering::Acquire);
            let next = unsafe { (*head).next.load(Ordering::Acquire) };
            
            if head == self.head.load(Ordering::Acquire) {
                if head == tail {
                    if next.is_null() {
                        return None;
                    }
                    
                    let _ = self.tail.compare_exchange_weak(
                        tail,
                        next,
                        Ordering::Release,
                        Ordering::Relaxed
                    );
                } else {
                    if next.is_null() {
                        continue;
                    }
                    
                    let data = unsafe { (*next).data.take() };
                    
                    if self.head.compare_exchange_weak(
                        head,
                        next,
                        Ordering::Release,
                        Ordering::Relaxed
                    ).is_ok() {
                        unsafe { drop(Box::from_raw(head)) };
                        return data;
                    }
                }
            }
        }
    }
}
```

### 4.4 Future: WASM in Kernel Space

Research into running WebAssembly in kernel space for safe kernel extensions.

#### eBPF-style Kernel WASM

```rust
// Kernel-space WASM runtime (conceptual)
pub struct KernelWasmRuntime {
    verifier: WasmVerifier,
    compiler: KernelSafeCompiler,
    sandbox: KernelSandbox,
}

pub struct KernelSandbox {
    memory_limits: KernelMemoryLimits,
    instruction_limits: InstructionLimits,
    allowed_syscalls: Vec<SyscallId>,
}

pub struct WasmKernelModule {
    compiled_code: CompiledKernelCode,
    metadata: KernelModuleMetadata,
    verification_proof: VerificationProof,
}

impl KernelWasmRuntime {
    pub fn load_kernel_module(&mut self, wasm_bytes: &[u8]) -> Result<WasmKernelModule, KernelError> {
        // Step 1: Verify WASM for kernel safety
        let verification_result = self.verifier.verify_kernel_safety(wasm_bytes)?;
        
        // Step 2: Prove memory safety
        let memory_safety_proof = self.verifier.prove_memory_safety(wasm_bytes)?;
        
        // Step 3: Compile to kernel-safe native code
        let compiled_code = self.compiler.compile_for_kernel(
            wasm_bytes,
            &verification_result.safe_operations
        )?;
        
        // Step 4: Create sandbox
        let sandbox = KernelSandbox {
            memory_limits: KernelMemoryLimits {
                max_pages: 16, // 1MB maximum
                stack_size: 4096, // 4KB stack
            },
            instruction_limits: InstructionLimits {
                max_instructions_per_invocation: 100_000,
                max_loop_iterations: 10_000,
            },
            allowed_syscalls: verification_result.required_syscalls,
        };
        
        Ok(WasmKernelModule {
            compiled_code,
            metadata: KernelModuleMetadata {
                module_name: verification_result.module_name,
                hook_points: verification_result.kernel_hooks,
                resource_usage: verification_result.resource_requirements,
            },
            verification_proof: VerificationProof {
                memory_safety_proof,
                termination_proof: verification_result.termination_proof,
                resource_bound_proof: verification_result.resource_bound_proof,
            },
        })
    }
    
    pub fn install_kernel_hook(
        &mut self,
        module: &WasmKernelModule,
        hook_point: KernelHookPoint
    ) -> Result<KernelHookHandle, KernelError> {
        // Verify hook compatibility
        if !module.metadata.hook_points.contains(&hook_point) {
            return Err(KernelError::IncompatibleHook);
        }
        
        // Install hook with runtime checks
        let hook_handle = self.install_verified_hook(module, hook_point)?;
        
        Ok(hook_handle)
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum KernelHookPoint {
    PacketFilter,
    FileSystemAccess,
    ProcessScheduling,
    MemoryAllocation,
    NetworkInterface,
    SystemCall,
}

// Example kernel module: Packet filter
#[no_mangle]
pub extern "C" fn packet_filter(packet_ptr: i32, packet_len: i32) -> i32 {
    let packet_data = unsafe {
        std::slice::from_raw_parts(packet_ptr as *const u8, packet_len as usize)
    };
    
    // Parse Ethernet header
    if packet_len < 14 {
        return 0; // Drop packet (too short)
    }
    
    let eth_type = u16::from_be_bytes([packet_data[12], packet_data[13]]);
    
    match eth_type {
        0x0800 => filter_ipv4_packet(&packet_data[14..]),
        0x86DD => filter_ipv6_packet(&packet_data[14..]),
        _ => 1, // Allow other protocols
    }
}

fn filter_ipv4_packet(ip_packet: &[u8]) -> i32 {
    if ip_packet.len() < 20 {
        return 0; // Drop malformed packet
    }
    
    let version = ip_packet[0] >> 4;
    if version != 4 {
        return 0; // Not IPv4
    }
    
    let protocol = ip_packet[9];
    let src_ip = u32::from_be_bytes([ip_packet[12], ip_packet[13], ip_packet[14], ip_packet[15]]);
    let dst_ip = u32::from_be_bytes([ip_packet[16], ip_packet[17], ip_packet[18], ip_packet[19]]);
    
    // Apply filtering rules
    match protocol {
        6 => filter_tcp_packet(ip_packet, src_ip, dst_ip), // TCP
        17 => filter_udp_packet(ip_packet, src_ip, dst_ip), // UDP
        1 => 1, // Allow ICMP
        _ => 0, // Drop unknown protocols
    }
}

fn filter_tcp_packet(ip_packet: &[u8], src_ip: u32, dst_ip: u32) -> i32 {
    let header_len = ((ip_packet[0] & 0x0F) * 4) as usize;
    
    if ip_packet.len() < header_len + 20 {
        return 0; // Malformed TCP packet
    }
    
    let tcp_header = &ip_packet[header_len..];
    let src_port = u16::from_be_bytes([tcp_header[0], tcp_header[1]]);
    let dst_port = u16::from_be_bytes([tcp_header[2], tcp_header[3]]);
    
    // Block connections to suspicious ports
    if dst_port == 22 && !is_authorized_ssh_client(src_ip) {
        return 0; // Block unauthorized SSH attempts
    }
    
    // Rate limiting for SYN packets
    let flags = tcp_header[13];
    if flags & 0x02 != 0 { // SYN flag
        if exceeds_syn_rate_limit(src_ip) {
            return 0; // Drop SYN flood packets
        }
    }
    
    1 // Allow packet
}

// Simple rate limiting (would be more sophisticated in practice)
static mut SYN_COUNT: [u32; 1024] = [0; 1024];
static mut LAST_RESET: u64 = 0;

fn exceeds_syn_rate_limit(src_ip: u32) -> bool {
    unsafe {
        let current_time = get_kernel_time();
        
        // Reset counters every second
        if current_time - LAST_RESET > 1000 {
            SYN_COUNT = [0; 1024];
            LAST_RESET = current_time;
        }
        
        let hash = (src_ip as usize) % 1024;
        SYN_COUNT[hash] += 1;
        
        SYN_COUNT[hash] > 100 // Max 100 SYN packets per second per IP
    }
}

extern "C" {
    fn get_kernel_time() -> u64;
    fn is_authorized_ssh_client(ip: u32) -> bool;
}
```

---

## Conclusion

WebAssembly has evolved from a browser compilation target into a foundational technology for distributed systems. Its mathematical foundations provide strong security guarantees through formal type systems and memory safety proofs. The implementation across different runtimes (V8, Wasmtime, Wasmer) demonstrates the versatility and performance characteristics that make it suitable for production use.

Key production deployments showcase WebAssembly's capabilities:
- **Cloudflare Workers**: 10M+ requests/second with <1ms cold starts
- **Fastly Compute@Edge**: Sub-100ms guaranteed startup times
- **Shopify Functions**: Safe merchant customization with strict resource limits
- **Figma**: Real-time collaborative editing with complex geometric operations
- **Discord Activities**: Secure third-party application platform

The research frontier includes WASI standardization, component model composition, shared memory threading, and potential kernel-space applications. These developments position WebAssembly as a critical technology for the future of distributed computing, providing the safety, performance, and portability needed for next-generation systems.

**Performance Summary:**
- Cold start latency: <1-100ms depending on runtime
- Memory overhead: 1-5MB per isolate
- Execution performance: 5-15% overhead vs. native code
- Compilation speed: 100K+ bytes/second (baseline) to optimized compilation
- Concurrent isolates: 1K-10K+ per server depending on workload

**Security Guarantees:**
- Memory safety through bounds checking
- Control flow integrity via structured control flow
- Capability-based security through explicit imports
- Resource isolation with configurable limits
- Formal verification support for critical applications

The combination of performance, security, and portability makes WebAssembly an ideal choice for distributed systems requiring safe execution of untrusted code, efficient edge computing, and composable system architectures.
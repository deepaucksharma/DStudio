---
title: Code Example Framework for Pattern Documentation
description: Comprehensive standards for production-ready code examples across all distributed systems patterns
icon: material/code-braces
tags:
- framework
- code-standards
- documentation
- patterns
---

# Code Example Framework for Pattern Documentation

## Table of Contents

- [Overview](#overview)
- [1. Language Selection Criteria](#1-language-selection-criteria)
  - [Primary Languages (All Patterns)](#primary-languages-all-patterns)
  - [Secondary Languages (Pattern-Specific)](#secondary-languages-pattern-specific)
  - [Framework Selection Standards](#framework-selection-standards)
- [2. Code Quality Standards](#2-code-quality-standards)
  - [Production-Ready Requirements](#production-ready-requirements)
- [✅ GOOD - Externalized configuration](#good-externalized-configuration)
  - [Logging Standards](#logging-standards)
  - [Performance Considerations](#performance-considerations)
  - [Security Best Practices](#security-best-practices)
- [✅ GOOD - Secure auth implementation](#good-secure-auth-implementation)
- [3. Standard Code Structure Template](#3-standard-code-structure-template)
  - [Component Structure](#component-structure)
  - [Configuration Section Template](#configuration-section-template)
- [Standard configuration structure](#standard-configuration-structure)
  - [Core Implementation Template](#core-implementation-template)
  - [Error Handling Template](#error-handling-template)
- [Standard error handling structure](#standard-error-handling-structure)
  - [Monitoring/Metrics Template](#monitoringmetrics-template)
  - [Test Examples Template](#test-examples-template)
- [4. Cloud Provider Integration Examples](#4-cloud-provider-integration-examples)
  - [AWS Integration](#aws-integration)
  - [Google Cloud Integration](#google-cloud-integration)
- [GCP-specific implementation](#gcp-specific-implementation)
  - [Azure Integration](#azure-integration)
- [5. Code Presentation Standards](#5-code-presentation-standards)
  - [Syntax Highlighting & Line Length](#syntax-highlighting-line-length)
- [Code block standards](#code-block-standards)
  - [Comment Standards](#comment-standards)
  - [Variable Naming Conventions](#variable-naming-conventions)
- [✅ GOOD - Clear, descriptive naming](#good-clear-descriptive-naming)
- [6. Reusable Code Templates](#6-reusable-code-templates)
  - [Circuit Breaker Template](#circuit-breaker-template)
  - [API Gateway Template](#api-gateway-template)
  - [Event Sourcing Template](#event-sourcing-template)
- [Example aggregate implementation](#example-aggregate-implementation)
- [Usage example](#usage-example)
- [7. Integration Examples Summary](#7-integration-examples-summary)
  - [Framework Integration Matrix](#framework-integration-matrix)
  - [Cloud Platform Examples](#cloud-platform-examples)
- [Implementation Guidelines](#implementation-guidelines)
  - [Phase 1: Pattern Assessment (Week 1)](#phase-1-pattern-assessment-week-1)
  - [Phase 2: Core Templates (Week 2-3)](#phase-2-core-templates-week-2-3)
  - [Phase 3: Pattern Implementation (Week 4-8)](#phase-3-pattern-implementation-week-4-8)
  - [Phase 4: Testing & Validation (Week 9-10)](#phase-4-testing-validation-week-9-10)

## Overview

This framework establishes comprehensive standards for code examples in all 91 distributed systems patterns. The goal is to provide production-ready, concise, and complete implementations that demonstrate real-world usage.

## 1. Language Selection Criteria

### Primary Languages (All Patterns)

| Language | Justification | Use Cases |
|----------|---------------|-----------|
| **Java** | Enterprise standard, Spring ecosystem | Microservices, Enterprise systems, Kafka, Kubernetes operators |
| **Python** | Rapid prototyping, ML/AI, clear syntax | Data processing, APIs, DevOps automation |  
| **Go** | Cloud-native, performance, concurrency | Infrastructure, containers, distributed systems |
| **JavaScript/TypeScript** | Full-stack, event-driven, async | Frontend integration, Node.js backends, real-time systems |

### Secondary Languages (Pattern-Specific)

| Language | When to Include | Patterns |
|----------|-----------------|----------|
| **Rust** | High-performance, systems programming | Low-latency patterns, consensus algorithms |
| **C#** | Microsoft ecosystem | Azure integrations, .NET microservices |
| **Kotlin** | Android, JVM alternative | Mobile-first patterns, JVM microservices |
| **Elixir** | Actor model, fault tolerance | Resilience patterns, real-time messaging |

### Framework Selection Standards

#### Java Frameworks
- **Spring Boot**: Default for microservices, REST APIs
- **Quarkus**: Cloud-native, serverless patterns
- **Kafka Streams**: Stream processing patterns
- **Reactor/RxJava**: Reactive patterns

#### Python Frameworks  
- **FastAPI**: Modern APIs, async patterns
- **Flask**: Simple services, middleware patterns
- **Celery**: Background processing, queue patterns
- **Pydantic**: Data validation, schema patterns

#### Go Frameworks
- **Gin/Echo**: Web services, API gateway patterns
- **gRPC**: Service communication patterns
- **Consul/etcd**: Service discovery, coordination
- **Prometheus**: Monitoring, observability patterns

#### JavaScript/TypeScript Frameworks
- **Express.js**: Traditional APIs, middleware patterns
- **NestJS**: Enterprise Node.js, decorator patterns
- **Socket.io**: Real-time communication patterns
- **React**: UI patterns, state management

## 2. Code Quality Standards

### Production-Ready Requirements

#### Error Handling
```java
/ ✅ GOOD - Comprehensive error handling
@Service
public class CircuitBreakerService {
    private final CircuitBreaker circuitBreaker;
    private final MetricRegistry metrics;
    private final Logger logger;
    
    public CompletableFuture<String> callExternalService(String request) {
        return circuitBreaker.executeSupplier(() -> {
            try {
                return externalApiClient.call(request);
            } catch (TimeoutException e) {
                metrics.counter("circuit.breaker.timeouts").increment();
                logger.warn("External service timeout for request: {}", request, e);
                throw new ServiceUnavailableException("External service timeout", e);
            } catch (Exception e) {
                metrics.counter("circuit.breaker.failures").increment();
                logger.error("External service failure for request: {}", request, e);
                throw new ServiceException("External service error", e);
            }
        }).recover(throwable -> {
            / Fallback logic
            return getCachedResponse(request)
                .orElse(getDefaultResponse());
        });
    }
}
```

#### Configuration Management
```python
## ✅ GOOD - Externalized configuration
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = int(os.getenv('CB_FAILURE_THRESHOLD', '5'))
    recovery_timeout: int = int(os.getenv('CB_RECOVERY_TIMEOUT', '30'))
    half_open_max_calls: int = int(os.getenv('CB_HALF_OPEN_CALLS', '3'))
    
    def validate(self):
        if self.failure_threshold <= 0:
            raise ValueError("Failure threshold must be positive")
        if self.recovery_timeout <= 0:
            raise ValueError("Recovery timeout must be positive")
```

### Logging Standards
```go
/ ✅ GOOD - Structured logging with context
func (cb *CircuitBreaker) Execute(ctx context.Context, operation func() (interface{}, error)) (interface{}, error) {
    logger := cb.logger.With(
        "component", "circuit_breaker",
        "operation_id", generateOperationID(),
        "state", cb.GetState().String(),
    )
    
    start := time.Now()
    result, err := cb.doExecute(ctx, operation)
    duration := time.Since(start)
    
    if err != nil {
        logger.Error("Circuit breaker operation failed",
            "error", err,
            "duration_ms", duration.Milliseconds(),
            "failure_count", cb.GetFailureCount(),
        )
    } else {
        logger.Info("Circuit breaker operation succeeded",
            "duration_ms", duration.Milliseconds(),
        )
    }
    
    return result, err
}
```

### Performance Considerations

#### Memory Management
```rust
/ ✅ GOOD - Efficient memory usage
use std::sync::Arc;
use tokio::sync::RwLock;

pub struct CircuitBreaker {
    config: Arc<CircuitBreakerConfig>,
    state: Arc<RwLock<CircuitBreakerState>>,
    metrics: Arc<Metrics>,
}

impl CircuitBreaker {
    pub async fn execute<F, T, E>(&self, operation: F) -> Result<T, CircuitBreakerError<E>>
    where
        F: FnOnce() -> Result<T, E>,
        T: Send + 'static,
        E: Send + 'static,
    {
        / Avoid unnecessary clones, use references where possible
        let state_guard = self.state.read().await;
        if matches!(*state_guard, CircuitBreakerState::Open { .. }) {
            drop(state_guard); / Release read lock early
            return Err(CircuitBreakerError::Open);
        }
        drop(state_guard);
        
        / Execute with proper error handling and metrics
        let start = Instant::now();
        let result = operation();
        let duration = start.elapsed();
        
        self.metrics.record_execution_time(duration);
        result.map_err(|e| {
            self.record_failure();
            CircuitBreakerError::Operation(e)
        })
    }
}
```

#### Thread/Async Safety
```typescript
/ ✅ GOOD - Proper async/await with cancellation
export class CircuitBreaker {
    private readonly config: CircuitBreakerConfig;
    private state: CircuitBreakerState = CircuitBreakerState.Closed;
    private readonly failureCount = new AtomicCounter();
    private readonly stateChangeMutex = new Mutex();

    async execute<T>(
        operation: () => Promise<T>,
        signal?: AbortSignal
    ): Promise<T> {
        / Check cancellation early
        signal?.throwIfAborted();
        
        const currentState = await this.getCurrentState();
        
        if (currentState === CircuitBreakerState.Open) {
            throw new CircuitBreakerOpenError('Circuit breaker is open');
        }
        
        try {
            / Create timeout promise that respects cancellation
            const timeoutPromise = new Promise<never>((_, reject) => {
                const timeout = setTimeout(() => {
                    reject(new TimeoutError('Operation timed out'));
                }, this.config.timeout);
                
                signal?.addEventListener('abort', () => {
                    clearTimeout(timeout);
                    reject(new AbortError('Operation aborted'));
                });
            });
            
            const result = await Promise.race([
                operation(),
                timeoutPromise
            ]);
            
            this.recordSuccess();
            return result;
            
        } catch (error) {
            signal?.throwIfAborted();
            this.recordFailure();
            throw error;
        }
    }
}
```

### Security Best Practices

#### Input Validation
```java
/ ✅ GOOD - Comprehensive input validation
@Component
public class ApiGatewayValidator {
    
    public void validateRequest(HttpServletRequest request) throws ValidationException {
        / Validate headers
        String contentType = request.getHeader("Content-Type");
        if (!isValidContentType(contentType)) {
            throw new ValidationException("Invalid content type: " + contentType);
        }
        
        / Validate request size
        int contentLength = request.getContentLength();
        if (contentLength > MAX_REQUEST_SIZE) {
            throw new ValidationException("Request too large: " + contentLength);
        }
        
        / Validate path traversal
        String path = request.getRequestURI();
        if (path.contains("../") || path.contains("..\\")) {
            throw new SecurityException("Path traversal attempt detected");
        }
        
        / Rate limiting validation
        String clientId = extractClientId(request);
        if (!rateLimiter.tryAcquire(clientId)) {
            throw new RateLimitException("Rate limit exceeded for client: " + clientId);
        }
    }
    
    private boolean isValidContentType(String contentType) {
        return ALLOWED_CONTENT_TYPES.contains(contentType);
    }
}
```

#### Authentication/Authorization
```python
## ✅ GOOD - Secure auth implementation
from functools import wraps
import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class JWTAuthenticator:
    def __init__(self, public_key: str, algorithm: str = "RS256"):
        self.public_key = public_key
        self.algorithm = algorithm
        
    def verify_token(self, token: str) -> dict:
        try:
            # Verify token with proper error handling
            payload = jwt.decode(
                token, 
                self.public_key, 
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True
                }
            )
            
            # Additional business logic validation
            if 'sub' not in payload:
                raise AuthenticationError("Missing subject claim")
                
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")

def require_auth(scopes: List[str] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract and verify token
            token = extract_bearer_token(request)
            payload = authenticator.verify_token(token)
            
            # Check scopes if provided
            if scopes:
                user_scopes = payload.get('scopes', [])
                if not any(scope in user_scopes for scope in scopes):
                    raise AuthorizationError("Insufficient permissions")
            
            # Add user context to request
            request.user = User.from_jwt_payload(payload)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## 3. Standard Code Structure Template

### Component Structure

```
pattern-implementation/
├── config/
│   ├── Configuration.{java|py|go|ts}
│   └── Validation.{java|py|go|ts}
├── core/
│   ├── PatternInterface.{java|py|go|ts}
│   ├── Implementation.{java|py|go|ts}
│   └── StateManager.{java|py|go|ts}
├── monitoring/
│   ├── Metrics.{java|py|go|ts}
│   ├── Health.{java|py|go|ts}
│   └── Logging.{java|py|go|ts}
├── integration/
│   ├── SpringBoot.java
│   ├── FastAPI.py
│   ├── Gin.go
│   └── Express.ts
└── tests/
    ├── unit/
    ├── integration/
    └── performance/
```

### Configuration Section Template

```yaml
## Standard configuration structure
pattern_name:
  # Core functionality
  enabled: true
  timeout_ms: 5000
  
  # Performance tuning
  thread_pool_size: 10
  queue_capacity: 1000
  
  # Monitoring
  metrics:
    enabled: true
    export_interval_seconds: 30
  
  # Integration points
  integrations:
    spring:
      auto_configuration: true
    kafka:
      bootstrap_servers: "localhost:9092"
    redis:
      url: "redis://localhost:6379"
```

### Core Implementation Template

```java
/**
 * Template for pattern core implementation
 */
@Component
@ConditionalOnProperty(name = "pattern.enabled", havingValue = "true", matchIfMissing = true)
public class PatternImplementation implements PatternInterface {
    
    private final PatternConfig config;
    private final MetricsCollector metrics;
    private final HealthIndicator health;
    private final Logger logger;
    
    public PatternImplementation(
        PatternConfig config,
        MetricsCollector metrics,
        HealthIndicator health
    ) {
        this.config = validateConfig(config);
        this.metrics = metrics;
        this.health = health;
        this.logger = LoggerFactory.getLogger(getClass());
    }
    
    @Override
    public CompletableFuture<Result> execute(Request request) {
        / Input validation
        validateRequest(request);
        
        / Metrics recording
        Timer.Sample sample = Timer.start();
        
        try {
            / Core logic implementation
            Result result = doExecute(request);
            
            / Success metrics
            metrics.incrementSuccess();
            sample.stop(metrics.getExecutionTimer());
            
            return CompletableFuture.completedFuture(result);
            
        } catch (Exception e) {
            / Error handling and metrics
            metrics.incrementFailure(e.getClass().getSimpleName());
            sample.stop(metrics.getExecutionTimer());
            
            logger.error("Pattern execution failed", e);
            health.markUnhealthy(e);
            
            return CompletableFuture.failedFuture(e);
        }
    }
    
    private Result doExecute(Request request) {
        / Implementation details
        return new Result();
    }
    
    private void validateRequest(Request request) {
        if (request == null) {
            throw new IllegalArgumentException("Request cannot be null");
        }
        / Additional validation
    }
    
    private PatternConfig validateConfig(PatternConfig config) {
        config.validate();
        return config;
    }
}
```

### Error Handling Template

```python
## Standard error handling structure
class PatternException(Exception):
    """Base exception for pattern-related errors"""
    
    def __init__(self, message: str, cause: Exception = None):
        super().__init__(message)
        self.cause = cause
        self.timestamp = datetime.utcnow()

class ConfigurationError(PatternException):
    """Configuration-related errors"""
    pass

class ExecutionError(PatternException):
    """Runtime execution errors"""
    pass

class TimeoutError(PatternException):
    """Timeout-related errors"""
    pass

def handle_pattern_errors(func):
    """Decorator for consistent error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PatternException:
            # Re-raise pattern-specific exceptions
            raise
        except Exception as e:
            # Convert generic exceptions
            logger.exception("Unexpected error in pattern execution")
            raise ExecutionError(f"Pattern execution failed: {str(e)}", e)
    return wrapper
```

### Monitoring/Metrics Template

```go
/ Standard metrics structure
type PatternMetrics struct {
    ExecutionCount    prometheus.Counter
    ExecutionDuration prometheus.Histogram
    ErrorCount        *prometheus.CounterVec
    SuccessRate       prometheus.Gauge
    HealthStatus      prometheus.Gauge
}

func NewPatternMetrics() *PatternMetrics {
    return &PatternMetrics{
        ExecutionCount: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "pattern_executions_total",
            Help: "Total number of pattern executions",
        }),
        
        ExecutionDuration: prometheus.NewHistogram(prometheus.HistogramOpts{
            Name:    "pattern_execution_duration_seconds",
            Help:    "Pattern execution duration",
            Buckets: []float64{0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0},
        }),
        
        ErrorCount: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "pattern_errors_total",
                Help: "Total number of pattern errors by type",
            },
            []string{"error_type"},
        ),
        
        SuccessRate: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "pattern_success_rate",
            Help: "Current success rate of pattern executions",
        }),
        
        HealthStatus: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "pattern_health_status",
            Help: "Health status of the pattern (1=healthy, 0=unhealthy)",
        }),
    }
}

func (m *PatternMetrics) RecordExecution(duration time.Duration, err error) {
    m.ExecutionCount.Inc()
    m.ExecutionDuration.Observe(duration.Seconds())
    
    if err != nil {
        m.ErrorCount.WithLabelValues(getErrorType(err)).Inc()
        m.HealthStatus.Set(0)
    } else {
        m.HealthStatus.Set(1)
    }
    
    / Update success rate (rolling average)
    m.updateSuccessRate()
}
```

### Test Examples Template

```typescript
/ Standard test structure
describe('PatternImplementation', () => {
    let pattern: PatternImplementation;
    let mockConfig: PatternConfig;
    let mockMetrics: MetricsCollector;
    
    beforeEach(() => {
        mockConfig = {
            enabled: true,
            timeout: 5000,
            retries: 3
        };
        
        mockMetrics = createMockMetrics();
        pattern = new PatternImplementation(mockConfig, mockMetrics);
    });
    
    describe('execute', () => {
        it('should execute successfully with valid input', async () => {
            const request = createValidRequest();
            
            const result = await pattern.execute(request);
            
            expect(result).toBeDefined();
            expect(result.status).toBe('success');
            expect(mockMetrics.incrementSuccess).toHaveBeenCalled();
        });
        
        it('should handle timeout gracefully', async () => {
            const request = createSlowRequest();
            
            await expect(pattern.execute(request))
                .rejects
                .toThrow(TimeoutError);
                
            expect(mockMetrics.incrementFailure).toHaveBeenCalledWith('TimeoutError');
        });
        
        it('should validate input parameters', async () => {
            const invalidRequest = null;
            
            await expect(pattern.execute(invalidRequest))
                .rejects
                .toThrow(ValidationError);
        });
    });
    
    describe('configuration', () => {
        it('should reject invalid configuration', () => {
            const invalidConfig = { ...mockConfig, timeout: -1 };
            
            expect(() => new PatternImplementation(invalidConfig, mockMetrics))
                .toThrow(ConfigurationError);
        });
    });
    
    describe('performance', () => {
        it('should handle high concurrent load', async () => {
            const requests = Array(1000).fill(null).map(() => createValidRequest());
            const promises = requests.map(req => pattern.execute(req));
            
            const results = await Promise.all(promises);
            
            expect(results).toHaveLength(1000);
            expect(results.every(r => r.status === 'success')).toBe(true);
        });
        
        it('should maintain performance under stress', async () => {
            const startTime = performance.now();
            
            / Execute many operations
            for (let i = 0; i < 10000; i++) {
                await pattern.execute(createValidRequest());
            }
            
            const duration = performance.now() - startTime;
            const avgDuration = duration / 10000;
            
            expect(avgDuration).toBeLessThan(10); / < 10ms average
        });
    });
});
```

## 4. Cloud Provider Integration Examples

### AWS Integration

```java
/ AWS-specific implementation
@Configuration
@ConditionalOnProperty(name = "pattern.cloud.provider", havingValue = "aws")
public class AwsPatternConfiguration {
    
    @Bean
    public PatternImplementation awsPatternImplementation(
        @Value("${aws.region}") String region,
        @Value("${pattern.aws.lambda.function-name}") String functionName
    ) {
        AWSLambda lambdaClient = AWSLambdaClientBuilder.standard()
            .withRegion(region)
            .build();
            
        DynamoDBClient dynamoClient = DynamoDbClient.builder()
            .region(Region.of(region))
            .build();
            
        CloudWatchClient cloudWatchClient = CloudWatchClient.builder()
            .region(Region.of(region))
            .build();
            
        return new AwsPatternImplementation(lambdaClient, dynamoClient, cloudWatchClient);
    }
}

@Service
public class AwsPatternImplementation implements PatternInterface {
    
    private final AWSLambda lambdaClient;
    private final DynamoDbClient dynamoClient; 
    private final CloudWatchClient cloudWatchClient;
    
    @Override
    public CompletableFuture<Result> execute(Request request) {
        / Publish custom metrics to CloudWatch
        cloudWatchClient.putMetricData(PutMetricDataRequest.builder()
            .namespace("CustomApp/Pattern")
            .metricData(MetricDatum.builder()
                .metricName("ExecutionCount")
                .value(1.0)
                .timestamp(Instant.now())
                .build())
            .build());
            
        / Store state in DynamoDB
        dynamoClient.putItem(PutItemRequest.builder()
            .tableName("pattern-state")
            .item(Map.of(
                "id", AttributeValue.builder().s(request.getId()).build(),
                "status", AttributeValue.builder().s("processing").build(),
                "timestamp", AttributeValue.builder().n(String.valueOf(System.currentTimeMillis())).build()
            ))
            .build());
            
        / Execute business logic via Lambda
        InvokeRequest invokeRequest = new InvokeRequest()
            .withFunctionName("pattern-processor")
            .withPayload(objectMapper.writeValueAsString(request));
            
        InvokeResult result = lambdaClient.invoke(invokeRequest);
        
        return CompletableFuture.completedFuture(
            objectMapper.readValue(result.getPayload().array(), Result.class)
        );
    }
}
```

### Google Cloud Integration

```python
## GCP-specific implementation
from google.cloud import pubsub_v1, firestore, monitoring_v3
from google.cloud.functions_v1 import CloudFunctionsServiceClient

class GcpPatternImplementation:
    def __init__(self, project_id: str, region: str):
        self.project_id = project_id
        self.region = region
        
        # Initialize GCP clients
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.firestore_client = firestore.Client(project=project_id)
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.functions_client = CloudFunctionsServiceClient()
        
    async def execute(self, request: Request) -> Result:
        # Publish to Pub/Sub for async processing
        topic_path = self.publisher.topic_path(self.project_id, "pattern-events")
        
        message_data = json.dumps({
            "request_id": request.id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": request.to_dict()
        }).encode("utf-8")
        
        future = self.publisher.publish(topic_path, message_data)
        message_id = future.result()
        
        # Store in Firestore
        doc_ref = self.firestore_client.collection("pattern-executions").document(request.id)
        doc_ref.set({
            "status": "processing",
            "message_id": message_id,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        
        # Send custom metrics to Cloud Monitoring
        series = monitoring_v3.TimeSeries()
        series.metric.type = "custom.googleapis.com/pattern/executions"
        series.resource.type = "global"
        
        point = series.points.add()
        point.value.int64_value = 1
        point.interval.end_time.seconds = int(time.time())
        
        project_name = f"projects/{self.project_id}"
        self.monitoring_client.create_time_series(
            name=project_name,
            time_series=[series]
        )
        
        return Result(message_id=message_id, status="queued")
```

### Azure Integration

```csharp
/ Azure-specific implementation
using Microsoft.Azure.ServiceBus;
using Microsoft.Azure.Cosmos;
using Microsoft.ApplicationInsights;
using Microsoft.Azure.Functions.Worker;

[Function("PatternProcessor")]
public class AzurePatternImplementation
{
    private readonly IServiceBusClient serviceBusClient;
    private readonly CosmosClient cosmosClient;
    private readonly TelemetryClient telemetryClient;
    private readonly ILogger<AzurePatternImplementation> logger;
    
    public AzurePatternImplementation(
        IServiceBusClient serviceBusClient,
        CosmosClient cosmosClient,
        TelemetryClient telemetryClient,
        ILogger<AzurePatternImplementation> logger)
    {
        this.serviceBusClient = serviceBusClient;
        this.cosmosClient = cosmosClient;
        this.telemetryClient = telemetryClient;
        this.logger = logger;
    }
    
    [Function("ExecutePattern")]
    public async Task<Result> Execute([HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequest req)
    {
        var request = await JsonSerializer.DeserializeAsync<Request>(req.Body);
        
        / Track custom event in Application Insights
        telemetryClient.TrackEvent("PatternExecution", new Dictionary<string, string>
        {
            ["RequestId"] = request.Id,
            ["Operation"] = request.Operation,
            ["Source"] = "AzureFunction"
        });
        
        / Send message to Service Bus for processing
        var sender = serviceBusClient.CreateSender("pattern-queue");
        var message = new ServiceBusMessage(JsonSerializer.Serialize(request))
        {
            MessageId = request.Id,
            Subject = request.Operation,
            TimeToLive = TimeSpan.FromMinutes(30)
        };
        
        await sender.SendMessageAsync(message);
        
        / Store in Cosmos DB
        var container = cosmosClient.GetContainer("PatternDB", "Executions");
        await container.CreateItemAsync(new
        {
            id = request.Id,
            status = "queued",
            timestamp = DateTimeOffset.UtcNow,
            request = request
        });
        
        logger.LogInformation("Pattern execution queued for request {RequestId}", request.Id);
        
        return new Result { MessageId = message.MessageId, Status = "queued" };
    }
}
```

## 5. Code Presentation Standards

### Syntax Highlighting & Line Length

```yaml
## Code block standards
code_standards:
  max_line_length: 100  # Characters per line
  indentation: 2        # Spaces for YAML, 4 for most languages
  
  syntax_highlighting:
    - java
    - python  
    - go
    - typescript
    - javascript
    - yaml
    - json
    - sql
    - bash
    - dockerfile
    
  formatting:
    show_line_numbers: true
    collapsible_sections: true  # For long examples
    copy_button: true
```

### Comment Standards

```java
/**
 * Circuit Breaker implementation following Netflix Hystrix patterns.
 * 
 * Key Design Decisions:
 * - Uses enum-based state machine for thread safety
 * - Exponential backoff for recovery attempts  
 * - Separate failure counting per operation type
 * - Fallback chain with multiple strategies
 * 
 * Production Considerations:
 * - Configure failure thresholds based on service SLA
 * - Monitor state transitions and business impact
 * - Test circuit behavior under various failure modes
 * - Consider distributed state for multi-instance deployments
 * 
 * @see https://netflix.github.io/Hystrix/
 */
@Component
public class ProductionCircuitBreaker {
    
    / Configuration with sensible defaults
    private final CircuitBreakerConfig config;
    
    / Thread-safe state management
    private final AtomicReference<State> state = new AtomicReference<>(State.CLOSED);
    
    /**
     * Execute operation with circuit breaker protection.
     * 
     * @param operation The operation to execute
     * @return CompletableFuture with result or fallback
     * @throws CircuitBreakerOpenException when circuit is open
     */
    public <T> CompletableFuture<T> execute(Supplier<CompletableFuture<T>> operation) {
        / Implementation details...
    }
}
```

### Variable Naming Conventions

```python
## ✅ GOOD - Clear, descriptive naming
class EventSourcingRepository:
    def __init__(self, event_store_client: EventStoreClient, snapshot_frequency: int = 100):
        self._event_store_client = event_store_client
        self._snapshot_frequency = snapshot_frequency
        self._aggregate_cache = LRUCache(maxsize=1000)
        
    async def save_events(
        self, 
        aggregate_id: AggregateId, 
        expected_version: int, 
        events: List[DomainEvent]
    ) -> None:
        """
        Save events with optimistic concurrency control.
        
        Args:
            aggregate_id: Unique identifier for the aggregate
            expected_version: Expected current version for concurrency control
            events: List of domain events to persist
            
        Raises:
            ConcurrencyException: When expected version doesn't match actual
            EventStoreException: When persistence fails
        """
        current_version = await self._get_current_version(aggregate_id)
        
        if current_version != expected_version:
            raise ConcurrencyException(
                f"Expected version {expected_version}, got {current_version}"
            )
            
        # Persist events with proper error handling
        await self._persist_events_atomically(aggregate_id, events)
```

## 6. Reusable Code Templates

### Circuit Breaker Template

<details>
<summary>📄 View complete Circuit Breaker implementations (4 languages)</summary>

#### Java Implementation
```java
@Component
@Slf4j
public class ProductionCircuitBreaker {
    
    public enum State { CLOSED, OPEN, HALF_OPEN }
    
    private final CircuitBreakerConfig config;
    private final AtomicReference<State> state = new AtomicReference<>(State.CLOSED);
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private final AtomicInteger successCount = new AtomicInteger(0);
    private final AtomicLong lastFailureTime = new AtomicLong(0);
    private final MeterRegistry meterRegistry;
    
    public ProductionCircuitBreaker(CircuitBreakerConfig config, MeterRegistry meterRegistry) {
        this.config = config;
        this.meterRegistry = meterRegistry;
    }
    
    public <T> CompletableFuture<T> execute(Supplier<CompletableFuture<T>> operation) {
        if (!canExecute()) {
            meterRegistry.counter("circuit.breaker.rejected").increment();
            return CompletableFuture.failedFuture(
                new CircuitBreakerOpenException("Circuit breaker is open")
            );
        }
        
        Timer.Sample sample = Timer.start(meterRegistry);
        
        return operation.get()
            .thenApply(result -> {
                onSuccess();
                sample.stop(Timer.builder("circuit.breaker.execution")
                    .tag("result", "success")
                    .register(meterRegistry));
                return result;
            })
            .exceptionally(throwable -> {
                onFailure();
                sample.stop(Timer.builder("circuit.breaker.execution")
                    .tag("result", "failure")
                    .register(meterRegistry));
                throw new RuntimeException(throwable);
            });
    }
    
    private boolean canExecute() {
        State currentState = state.get();
        
        switch (currentState) {
            case CLOSED:
                return true;
            case OPEN:
                if (shouldAttemptReset()) {
                    state.compareAndSet(State.OPEN, State.HALF_OPEN);
                    return true;
                }
                return false;
            case HALF_OPEN:
                return successCount.get() < config.getHalfOpenMaxCalls();
            default:
                return false;
        }
    }
    
    private void onSuccess() {
        failureCount.set(0);
        
        if (state.get() == State.HALF_OPEN) {
            int currentSuccessCount = successCount.incrementAndGet();
            if (currentSuccessCount >= config.getHalfOpenSuccessThreshold()) {
                state.set(State.CLOSED);
                successCount.set(0);
                log.info("Circuit breaker reset to CLOSED state");
            }
        }
    }
    
    private void onFailure() {
        int failures = failureCount.incrementAndGet();
        lastFailureTime.set(System.currentTimeMillis());
        
        if (failures >= config.getFailureThreshold()) {
            state.set(State.OPEN);
            log.warn("Circuit breaker opened due to {} failures", failures);
        }
    }
    
    private boolean shouldAttemptReset() {
        return System.currentTimeMillis() - lastFailureTime.get() >= config.getRecoveryTimeout();
    }
}
```

#### Python Implementation
```python
import asyncio
import time
from enum import Enum
from typing import Callable, TypeVar, Awaitable
from dataclasses import dataclass

T = TypeVar('T')

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    half_open_success_threshold: int = 2

class CircuitBreakerOpenException(Exception):
    pass

class AsyncCircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0
        self._lock = asyncio.Lock()
        
    async def execute(self, operation: Callable[[], Awaitable[T]]) -> T:
        """Execute operation with circuit breaker protection"""
        
        if not await self._can_execute():
            raise CircuitBreakerOpenException("Circuit breaker is open")
            
        start_time = time.time()
        
        try:
            result = await operation()
            await self._on_success()
            
            # Record success metrics
            execution_time = time.time() - start_time
            await self._record_metrics("success", execution_time)
            
            return result
            
        except Exception as e:
            await self._on_failure()
            
            # Record failure metrics  
            execution_time = time.time() - start_time
            await self._record_metrics("failure", execution_time)
            
            raise e
    
    async def _can_execute(self) -> bool:
        async with self._lock:
            if self._state == CircuitBreakerState.CLOSED:
                return True
            elif self._state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitBreakerState.HALF_OPEN
                    return True
                return False
            elif self._state == CircuitBreakerState.HALF_OPEN:
                return self._success_count < self.config.half_open_max_calls
                
        return False
    
    async def _on_success(self):
        async with self._lock:
            self._failure_count = 0
            
            if self._state == CircuitBreakerState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.half_open_success_threshold:
                    self._state = CircuitBreakerState.CLOSED
                    self._success_count = 0
    
    async def _on_failure(self):
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._failure_count >= self.config.failure_threshold:
                self._state = CircuitBreakerState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        return time.time() - self._last_failure_time >= self.config.recovery_timeout
        
    async def _record_metrics(self, result: str, execution_time: float):
        # Implement metrics recording (Prometheus, CloudWatch, etc.)
        pass
```

#### Go Implementation
```go
package circuitbreaker

import (
    "context"
    "fmt"
    "sync"
    "time"
    
    "go.uber.org/zap"
    "github.com/prometheus/client_golang/prometheus"
)

type State int

const (
    Closed State = iota
    Open
    HalfOpen
)

type Config struct {
    FailureThreshold          int           `json:"failure_threshold"`
    RecoveryTimeout           time.Duration `json:"recovery_timeout"`
    HalfOpenMaxCalls         int           `json:"half_open_max_calls"`
    HalfOpenSuccessThreshold int           `json:"half_open_success_threshold"`
}

type CircuitBreaker struct {
    config    Config
    state     State
    mutex     sync.RWMutex
    
    failureCount int
    successCount int
    lastFailureTime time.Time
    
    logger *zap.Logger
    metrics *Metrics
}

type Metrics struct {
    ExecutionTotal    prometheus.Counter
    ExecutionDuration prometheus.Histogram
    StateTransitions  *prometheus.CounterVec
    CurrentState      prometheus.Gauge
}

func New(config Config, logger *zap.Logger) *CircuitBreaker {
    return &CircuitBreaker{
        config:  config,
        state:   Closed,
        logger:  logger,
        metrics: newMetrics(),
    }
}

func (cb *CircuitBreaker) Execute(ctx context.Context, operation func() (interface{}, error)) (interface{}, error) {
    if !cb.canExecute() {
        cb.metrics.ExecutionTotal.Inc()
        return nil, fmt.Errorf("circuit breaker is open")
    }
    
    start := time.Now()
    result, err := operation()
    duration := time.Since(start)
    
    cb.metrics.ExecutionTotal.Inc()
    cb.metrics.ExecutionDuration.Observe(duration.Seconds())
    
    if err != nil {
        cb.onFailure()
        cb.logger.Error("Circuit breaker operation failed",
            zap.Error(err),
            zap.Duration("duration", duration),
        )
        return nil, err
    }
    
    cb.onSuccess()
    cb.logger.Info("Circuit breaker operation succeeded",
        zap.Duration("duration", duration),
    )
    
    return result, nil
}

func (cb *CircuitBreaker) canExecute() bool {
    cb.mutex.RLock()
    defer cb.mutex.RUnlock()
    
    switch cb.state {
    case Closed:
        return true
    case Open:
        return cb.shouldAttemptReset()
    case HalfOpen:
        return cb.successCount < cb.config.HalfOpenMaxCalls
    }
    return false
}

func (cb *CircuitBreaker) onSuccess() {
    cb.mutex.Lock()
    defer cb.mutex.Unlock()
    
    cb.failureCount = 0
    
    if cb.state == HalfOpen {
        cb.successCount++
        if cb.successCount >= cb.config.HalfOpenSuccessThreshold {
            cb.setState(Closed)
            cb.successCount = 0
        }
    }
}

func (cb *CircuitBreaker) onFailure() {
    cb.mutex.Lock()
    defer cb.mutex.Unlock()
    
    cb.failureCount++
    cb.lastFailureTime = time.Now()
    
    if cb.failureCount >= cb.config.FailureThreshold {
        cb.setState(Open)
    }
}

func (cb *CircuitBreaker) shouldAttemptReset() bool {
    return time.Since(cb.lastFailureTime) >= cb.config.RecoveryTimeout
}

func (cb *CircuitBreaker) setState(newState State) {
    if cb.state != newState {
        oldState := cb.state
        cb.state = newState
        
        cb.metrics.StateTransitions.WithLabelValues(
            stateToString(oldState),
            stateToString(newState),
        ).Inc()
        
        cb.metrics.CurrentState.Set(float64(newState))
        
        cb.logger.Info("Circuit breaker state changed",
            zap.String("from", stateToString(oldState)),
            zap.String("to", stateToString(newState)),
        )
    }
}

func stateToString(state State) string {
    switch state {
    case Closed:
        return "closed"
    case Open:
        return "open"
    case HalfOpen:
        return "half_open"
    default:
        return "unknown"
    }
}

func newMetrics() *Metrics {
    return &Metrics{
        ExecutionTotal: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "circuit_breaker_executions_total",
            Help: "Total number of circuit breaker executions",
        }),
        
        ExecutionDuration: prometheus.NewHistogram(prometheus.HistogramOpts{
            Name: "circuit_breaker_execution_duration_seconds", 
            Help: "Circuit breaker execution duration",
            Buckets: []float64{0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0},
        }),
        
        StateTransitions: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "circuit_breaker_state_transitions_total",
                Help: "Total number of circuit breaker state transitions",
            },
            []string{"from", "to"},
        ),
        
        CurrentState: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "circuit_breaker_current_state",
            Help: "Current state of the circuit breaker (0=closed, 1=open, 2=half_open)",
        }),
    }
}
```

#### TypeScript Implementation
```typescript
export enum CircuitBreakerState {
  CLOSED = 'closed',
  OPEN = 'open', 
  HALF_OPEN = 'half_open'
}

export interface CircuitBreakerConfig {
  failureThreshold: number;
  recoveryTimeout: number;
  halfOpenMaxCalls: number;
  halfOpenSuccessThreshold: number;
}

export class CircuitBreakerOpenError extends Error {
  constructor(message: string = 'Circuit breaker is open') {
    super(message);
    this.name = 'CircuitBreakerOpenError';
  }
}

export class CircuitBreaker {
  private state: CircuitBreakerState = CircuitBreakerState.CLOSED;
  private failureCount = 0;
  private successCount = 0;
  private lastFailureTime = 0;
  private readonly stateMutex = new Mutex();
  
  constructor(
    private readonly config: CircuitBreakerConfig,
    private readonly logger: Logger,
    private readonly metrics: MetricsCollector
  ) {}
  
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (!(await this.canExecute())) {
      this.metrics.incrementRejected();
      throw new CircuitBreakerOpenError();
    }
    
    const startTime = performance.now();
    
    try {
      const result = await operation();
      await this.onSuccess();
      
      const duration = performance.now() - startTime;
      this.metrics.recordExecution('success', duration);
      
      return result;
      
    } catch (error) {
      await this.onFailure();
      
      const duration = performance.now() - startTime;
      this.metrics.recordExecution('failure', duration);
      
      throw error;
    }
  }
  
  private async canExecute(): Promise<boolean> {
    return this.stateMutex.runExclusive(async () => {
      switch (this.state) {
        case CircuitBreakerState.CLOSED:
          return true;
          
        case CircuitBreakerState.OPEN:
          if (this.shouldAttemptReset()) {
            this.setState(CircuitBreakerState.HALF_OPEN);
            return true;
          }
          return false;
          
        case CircuitBreakerState.HALF_OPEN:
          return this.successCount < this.config.halfOpenMaxCalls;
          
        default:
          return false;
      }
    });
  }
  
  private async onSuccess(): Promise<void> {
    await this.stateMutex.runExclusive(async () => {
      this.failureCount = 0;
      
      if (this.state === CircuitBreakerState.HALF_OPEN) {
        this.successCount++;
        if (this.successCount >= this.config.halfOpenSuccessThreshold) {
          this.setState(CircuitBreakerState.CLOSED);
          this.successCount = 0;
        }
      }
    });
  }
  
  private async onFailure(): Promise<void> {
    await this.stateMutex.runExclusive(async () => {
      this.failureCount++;
      this.lastFailureTime = Date.now();
      
      if (this.failureCount >= this.config.failureThreshold) {
        this.setState(CircuitBreakerState.OPEN);
      }
    });
  }
  
  private shouldAttemptReset(): boolean {
    return Date.now() - this.lastFailureTime >= this.config.recoveryTimeout;
  }
  
  private setState(newState: CircuitBreakerState): void {
    if (this.state !== newState) {
      const oldState = this.state;
      this.state = newState;
      
      this.logger.info('Circuit breaker state changed', {
        from: oldState,
        to: newState,
        failureCount: this.failureCount
      });
      
      this.metrics.recordStateTransition(oldState, newState);
    }
  }
  
  getState(): CircuitBreakerState {
    return this.state;
  }
  
  getFailureCount(): number {
    return this.failureCount;
  }
  
  / Health check endpoint
  getHealthStatus() {
    return {
      state: this.state,
      failureCount: this.failureCount,
      lastFailureTime: this.lastFailureTime,
      isHealthy: this.state !== CircuitBreakerState.OPEN
    };
  }
}

/ Utility Mutex class for TypeScript
class Mutex {
  private locked = false;
  private readonly waiting: Array<() => void> = [];
  
  async runExclusive<T>(operation: () => Promise<T>): Promise<T> {
    await this.acquire();
    try {
      return await operation();
    } finally {
      this.release();
    }
  }
  
  private async acquire(): Promise<void> {
    return new Promise<void>(resolve => {
      if (!this.locked) {
        this.locked = true;
        resolve();
      } else {
        this.waiting.push(resolve);
      }
    });
  }
  
  private release(): void {
    if (this.waiting.length > 0) {
      const next = this.waiting.shift()!;
      next();
    } else {
      this.locked = false;
    }
  }
}
```

</details>

### API Gateway Template

<details>
<summary>📄 View complete API Gateway implementations</summary>

#### Spring Boot Implementation
```java
@RestController
@RequestMapping("/api/v1")
@Slf4j
public class ApiGatewayController {
    
    private final RouteRegistry routeRegistry;
    private final AuthenticationService authService;
    private final RateLimitService rateLimitService;
    private final CircuitBreakerFactory circuitBreakerFactory;
    private final MetricsService metricsService;
    
    @PostMapping("/**")
    public ResponseEntity<Object> handleRequest(
        HttpServletRequest request,
        @RequestBody(required = false) String body,
        HttpHeaders headers
    ) {
        String path = extractPath(request);
        String method = request.getMethod();
        
        / Authentication
        AuthContext authContext = authService.authenticate(headers);
        
        / Rate limiting
        if (!rateLimitService.allow(authContext.getClientId())) {
            return ResponseEntity.status(429).body("Rate limit exceeded");
        }
        
        / Route resolution
        Route route = routeRegistry.findRoute(path, method);
        if (route == null) {
            return ResponseEntity.notFound().build();
        }
        
        / Circuit breaker protection
        CircuitBreaker circuitBreaker = circuitBreakerFactory.create(route.getServiceName());
        
        return circuitBreaker.executeSupplier(() -> {
            / Request transformation
            String transformedBody = transformRequest(body, route);
            HttpHeaders transformedHeaders = transformHeaders(headers, route, authContext);
            
            / Downstream service call
            ResponseEntity<String> response = restTemplate.exchange(
                route.getTargetUrl() + path,
                HttpMethod.valueOf(method),
                new HttpEntity<>(transformedBody, transformedHeaders),
                String.class
            );
            
            / Response transformation
            Object transformedResponse = transformResponse(response.getBody(), route);
            
            / Metrics recording
            metricsService.recordRequest(route.getServiceName(), response.getStatusCodeValue());
            
            return ResponseEntity.status(response.getStatusCode())
                .headers(response.getHeaders())
                .body(transformedResponse);
                
        }).recover(throwable -> {
            log.error("Service call failed for route: " + route.getServiceName(), throwable);
            metricsService.recordFailure(route.getServiceName(), throwable.getClass().getSimpleName());
            
            / Fallback response
            return ResponseEntity.status(503)
                .body(Map.of("error", "Service temporarily unavailable"));
        });
    }
}

@Component
public class RouteRegistry {
    private final Map<String, Route> routes = new ConcurrentHashMap<>();
    
    @PostConstruct
    public void loadRoutes() {
        / Load routes from configuration
        routes.put("/users/**", Route.builder()
            .serviceName("user-service")
            .targetUrl("http://user-service:8080")
            .authRequired(true)
            .rateLimit(1000)
            .build());
            
        routes.put("/orders/**", Route.builder()
            .serviceName("order-service") 
            .targetUrl("http://order-service:8080")
            .authRequired(true)
            .rateLimit(500)
            .build());
    }
    
    public Route findRoute(String path, String method) {
        return routes.entrySet().stream()
            .filter(entry -> pathMatches(path, entry.getKey()))
            .map(Map.Entry::getValue)
            .findFirst()
            .orElse(null);
    }
    
    private boolean pathMatches(String requestPath, String routePattern) {
        return AntPathMatcher().match(routePattern, requestPath);
    }
}
```

#### Express.js Implementation  
```typescript
import express from 'express';
import httpProxy from 'http-proxy-middleware';
import rateLimit from 'express-rate-limit';
import { authenticate } from './middleware/auth';
import { metrics } from './middleware/metrics';
import { circuitBreaker } from './middleware/circuit-breaker';
import { requestLogger } from './middleware/logging';

const app = express();

/ Global middleware
app.use(express.json({ limit: '1mb' }));
app.use(requestLogger());
app.use(metrics());

/ Rate limiting
const createRateLimit = (windowMs: number, max: number) => rateLimit({
  windowMs,
  max,
  message: { error: 'Too many requests' },
  standardHeaders: true,
  legacyHeaders: false,
});

/ Routes configuration
const routes = [
  {
    path: '/api/users',
    target: 'http://user-service:3000',
    auth: true,
    rateLimit: createRateLimit(15 * 60 * 1000, 100), / 100 requests per 15 minutes
  },
  {
    path: '/api/orders', 
    target: 'http://order-service:3000',
    auth: true,
    rateLimit: createRateLimit(15 * 60 * 1000, 200),
  },
  {
    path: '/api/public',
    target: 'http://content-service:3000', 
    auth: false,
    rateLimit: createRateLimit(15 * 60 * 1000, 1000),
  }
];

/ Setup routes
routes.forEach(route => {
  const middlewares = [];
  
  / Add rate limiting
  if (route.rateLimit) {
    middlewares.push(route.rateLimit);
  }
  
  / Add authentication
  if (route.auth) {
    middlewares.push(authenticate);
  }
  
  / Add circuit breaker
  middlewares.push(circuitBreaker(route.target));
  
  / Create proxy middleware
  const proxyMiddleware = httpProxy({
    target: route.target,
    changeOrigin: true,
    pathRewrite: {
      [`^${route.path}`]: '',
    },
    
    / Request transformation
    onProxyReq: (proxyReq, req, res) => {
      / Add correlation ID
      proxyReq.setHeader('X-Correlation-ID', req.headers['x-correlation-id'] || generateId());
      
      / Add user context
      if (req.user) {
        proxyReq.setHeader('X-User-ID', req.user.id);
        proxyReq.setHeader('X-User-Roles', req.user.roles.join(','));
      }
      
      / Request logging
      console.log(`Proxying ${req.method} ${req.url} to ${route.target}`);
    },
    
    / Response transformation
    onProxyRes: (proxyRes, req, res) => {
      / Add CORS headers
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
      
      / Security headers
      res.header('X-Content-Type-Options', 'nosniff');
      res.header('X-Frame-Options', 'DENY');
    },
    
    / Error handling
    onError: (err, req, res) => {
      console.error('Proxy error:', err);
      res.status(502).json({
        error: 'Bad Gateway',
        message: 'Service temporarily unavailable'
      });
    }
  });
  
  / Register route with all middleware
  app.use(route.path, ...middlewares, proxyMiddleware);
});

/ Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

/ Global error handler
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: 'Something went wrong'
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});
```

</details>

### Event Sourcing Template

<details>
<summary>📄 View Event Sourcing implementation templates</summary>

#### Python Event Store Implementation
```python
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import asyncio

@dataclass
class DomainEvent:
    """Base class for all domain events"""
    aggregate_id: str
    event_type: str
    event_data: Dict[str, Any]
    event_version: int
    occurred_at: datetime
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        return cls(**data)

class EventStore(ABC):
    """Abstract event store interface"""
    
    @abstractmethod
    async def save_events(
        self, 
        aggregate_id: str, 
        expected_version: int, 
        events: List[DomainEvent]
    ) -> None:
        pass
    
    @abstractmethod
    async def get_events(
        self, 
        aggregate_id: str, 
        from_version: int = 0
    ) -> List[DomainEvent]:
        pass
    
    @abstractmethod
    async def get_events_by_type(
        self, 
        event_type: str, 
        from_timestamp: Optional[datetime] = None
    ) -> List[DomainEvent]:
        pass

class PostgresEventStore(EventStore):
    """PostgreSQL-based event store implementation"""
    
    def __init__(self, connection_pool):
        self.pool = connection_pool
    
    async def save_events(
        self, 
        aggregate_id: str, 
        expected_version: int, 
        events: List[DomainEvent]
    ) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Check current version for optimistic concurrency
                current_version = await self._get_current_version(conn, aggregate_id)
                
                if current_version != expected_version:
                    raise ConcurrencyException(
                        f"Expected version {expected_version}, got {current_version}"
                    )
                
                # Insert events
                for i, event in enumerate(events):
                    await conn.execute("""
                        INSERT INTO events (
                            aggregate_id, event_type, event_data, 
                            event_version, occurred_at, correlation_id, causation_id
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, 
                        aggregate_id,
                        event.event_type,
                        json.dumps(event.event_data),
                        expected_version + i + 1,
                        event.occurred_at,
                        event.correlation_id,
                        event.causation_id
                    )
    
    async def get_events(
        self, 
        aggregate_id: str, 
        from_version: int = 0
    ) -> List[DomainEvent]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT aggregate_id, event_type, event_data, 
                       event_version, occurred_at, correlation_id, causation_id
                FROM events 
                WHERE aggregate_id = $1 AND event_version > $2
                ORDER BY event_version
            """, aggregate_id, from_version)
            
            return [self._row_to_event(row) for row in rows]
    
    async def get_events_by_type(
        self, 
        event_type: str, 
        from_timestamp: Optional[datetime] = None
    ) -> List[DomainEvent]:
        async with self.pool.acquire() as conn:
            query = """
                SELECT aggregate_id, event_type, event_data,
                       event_version, occurred_at, correlation_id, causation_id
                FROM events 
                WHERE event_type = $1
            """
            params = [event_type]
            
            if from_timestamp:
                query += " AND occurred_at >= $2"
                params.append(from_timestamp)
                
            query += " ORDER BY occurred_at"
            
            rows = await conn.fetch(query, *params)
            return [self._row_to_event(row) for row in rows]
    
    async def _get_current_version(self, conn, aggregate_id: str) -> int:
        row = await conn.fetchrow("""
            SELECT COALESCE(MAX(event_version), 0) as version
            FROM events 
            WHERE aggregate_id = $1
        """, aggregate_id)
        
        return row['version']
    
    def _row_to_event(self, row) -> DomainEvent:
        return DomainEvent(
            aggregate_id=row['aggregate_id'],
            event_type=row['event_type'],
            event_data=json.loads(row['event_data']),
            event_version=row['event_version'],
            occurred_at=row['occurred_at'],
            correlation_id=row['correlation_id'],
            causation_id=row['causation_id']
        )

class AggregateRoot(ABC):
    """Base class for aggregate roots in event sourcing"""
    
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.version = 0
        self._uncommitted_events: List[DomainEvent] = []
    
    def get_uncommitted_events(self) -> List[DomainEvent]:
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self):
        self._uncommitted_events.clear()
    
    def load_from_history(self, events: List[DomainEvent]):
        """Rebuild aggregate state from event history"""
        for event in events:
            self.apply_event(event, is_new=False)
            self.version = event.event_version
    
    def apply_event(self, event: DomainEvent, is_new: bool = True):
        """Apply an event to the aggregate"""
        # Call the appropriate handler method
        handler_name = f"_handle_{event.event_type.lower()}"
        handler = getattr(self, handler_name, None)
        
        if handler:
            handler(event.event_data)
        
        if is_new:
            self._uncommitted_events.append(event)
    
    def raise_event(self, event_type: str, event_data: Dict[str, Any], 
                   correlation_id: Optional[str] = None, causation_id: Optional[str] = None):
        """Raise a new domain event"""
        event = DomainEvent(
            aggregate_id=self.aggregate_id,
            event_type=event_type,
            event_data=event_data,
            event_version=self.version + len(self._uncommitted_events) + 1,
            occurred_at=datetime.utcnow(),
            correlation_id=correlation_id,
            causation_id=causation_id
        )
        
        self.apply_event(event)

class Repository:
    """Generic repository for event-sourced aggregates"""
    
    def __init__(self, event_store: EventStore, aggregate_class: type):
        self.event_store = event_store
        self.aggregate_class = aggregate_class
    
    async def get_by_id(self, aggregate_id: str) -> Optional[AggregateRoot]:
        """Load aggregate by ID from event store"""
        events = await self.event_store.get_events(aggregate_id)
        
        if not events:
            return None
        
        aggregate = self.aggregate_class(aggregate_id)
        aggregate.load_from_history(events)
        return aggregate
    
    async def save(self, aggregate: AggregateRoot):
        """Save aggregate changes to event store"""
        uncommitted_events = aggregate.get_uncommitted_events()
        
        if not uncommitted_events:
            return
        
        await self.event_store.save_events(
            aggregate.aggregate_id,
            aggregate.version,
            uncommitted_events
        )
        
        aggregate.mark_events_as_committed()

## Example aggregate implementation
class BankAccount(AggregateRoot):
    def __init__(self, account_id: str):
        super().__init__(account_id)
        self.balance = 0.0
        self.is_closed = False
    
    def open_account(self, initial_balance: float, owner_name: str):
        if self.version > 0:
            raise ValueError("Account already exists")
        
        self.raise_event("AccountOpened", {
            "initial_balance": initial_balance,
            "owner_name": owner_name
        })
    
    def deposit(self, amount: float, description: str = ""):
        if self.is_closed:
            raise ValueError("Cannot deposit to closed account")
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self.raise_event("MoneyDeposited", {
            "amount": amount,
            "description": description
        })
    
    def withdraw(self, amount: float, description: str = ""):
        if self.is_closed:
            raise ValueError("Cannot withdraw from closed account")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        
        self.raise_event("MoneyWithdrawn", {
            "amount": amount,
            "description": description
        })
    
    def close_account(self):
        if self.is_closed:
            raise ValueError("Account already closed")
        
        self.raise_event("AccountClosed", {})
    
    # Event handlers
    def _handle_accountopened(self, event_data: Dict[str, Any]):
        self.balance = event_data["initial_balance"]
        self.owner_name = event_data["owner_name"]
    
    def _handle_moneydeposited(self, event_data: Dict[str, Any]):
        self.balance += event_data["amount"]
    
    def _handle_moneywithdrawn(self, event_data: Dict[str, Any]):
        self.balance -= event_data["amount"]
    
    def _handle_accountclosed(self, event_data: Dict[str, Any]):
        self.is_closed = True

## Usage example
async def example_usage():
    # Setup
    event_store = PostgresEventStore(connection_pool)
    repository = Repository(event_store, BankAccount)
    
    # Create new account
    account = BankAccount("account-123")
    account.open_account(100.0, "John Doe")
    account.deposit(50.0, "Initial deposit")
    
    # Save to event store
    await repository.save(account)
    
    # Load from event store
    loaded_account = await repository.get_by_id("account-123")
    print(f"Account balance: {loaded_account.balance}")  # 150.0
```

</details>

## 7. Integration Examples Summary

### Framework Integration Matrix

| Pattern Category | Java (Spring) | Python (FastAPI) | Go (Gin) | TypeScript (Express) |
|------------------|---------------|------------------|-----------|----------------------|
| **Resilience** | Hystrix, Resilience4j | tenacity, circuit-breaker-py | go-breaker, go-resiliency | opossum, cockatiel |
| **Communication** | Spring Cloud Gateway | httpx, aiohttp | gin, echo, fiber | express, fastify, koa |
| **Data Management** | Spring Data, Hibernate | SQLAlchemy, asyncpg | gorm, sqlx | TypeORM, Prisma |
| **Monitoring** | Micrometer, Actuator | prometheus-client | prometheus/client_golang | prom-client |
| **Configuration** | Spring Config | pydantic, dynaconf | viper, envconfig | dotenv, config |

### Cloud Platform Examples

| Platform | Primary Services | Pattern Applications |
|----------|------------------|---------------------|
| **AWS** | Lambda, DynamoDB, SQS, CloudWatch | Serverless patterns, Event sourcing, Queue-based patterns |
| **GCP** | Cloud Functions, Firestore, Pub/Sub, Cloud Monitoring | Event-driven architecture, Stream processing |
| **Azure** | Azure Functions, Cosmos DB, Service Bus, Application Insights | Microservices, Message queues |

## Implementation Guidelines

### Phase 1: Pattern Assessment (Week 1)
1. **Audit Existing Examples**: Review current code examples across all 91 patterns
2. **Identify Gaps**: Note patterns missing production-ready examples
3. **Prioritize by Tier**: Start with Gold tier patterns (highest impact)

### Phase 2: Core Templates (Week 2-3)
1. **Create Base Templates**: Implement the 6 core template categories
2. **Establish Standards**: Define code quality, formatting, and documentation standards
3. **Build Integration Examples**: Create cloud provider and framework integrations

### Phase 3: Pattern Implementation (Week 4-8)
1. **Gold Patterns First**: Complete all 31 Gold patterns with full implementations
2. **Silver Patterns**: Add essential Silver pattern examples  
3. **Bronze Patterns**: Provide migration examples for legacy patterns

### Phase 4: Testing & Validation (Week 9-10)
1. **Code Review**: Ensure all examples meet production standards
2. **Integration Testing**: Validate framework and cloud integrations
3. **Documentation Review**: Verify examples align with pattern documentation

This framework provides a comprehensive foundation for creating consistent, production-ready code examples across all distributed systems patterns. The multi-language approach ensures broad applicability while maintaining high quality standards suitable for enterprise adoption.
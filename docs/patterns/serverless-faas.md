---
title: Serverless/FaaS (Function-as-a-Service)
description: Request → API Gateway → Lambda → Response
              ↓           ↓
         Auto-scale    Millisecond
         to millions   billing
```dockerfile
type: pattern
difficulty: beginner
reading_time: 10 min
prerequisites: []
pattern_type: "general"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Serverless/FaaS (Function-as-a-Service)**


# Serverless/FaaS (Function-as-a-Service)

**No servers, just functions (that run on servers you don't see)**

## THE PROBLEM

```
Traditional scaling challenges:
- Provision for peak = waste money on idle
- Provision for average = crash on peak
- Managing servers = operational overhead
- 0→1 scaling = cold start pain
- 1→0 scaling = paying for idle
```bash
## THE SOLUTION

```
Serverless: Pay only for execution time

Request → API Gateway → Lambda → Response
              ↓           ↓
         Auto-scale    Millisecond
         to millions   billing
```bash
## Serverless Patterns

```
1. REQUEST/RESPONSE
   HTTP → Function → Response
   
2. EVENT-DRIVEN
   S3 Upload → Function → Process
   
3. STREAM PROCESSING
   Kinesis → Function → Transform
   
4. SCHEDULED
   Cron → Function → Batch Job
```bash
## IMPLEMENTATION

```python
# Basic Lambda function
def lambda_handler(event, context):
    """
    event: Input data (JSON)
    context: Runtime information
    """
    
    # Parse input
    body = json.loads(event.get('body', '{}'))
    
    # Business logic
    result = process_request(body)
    
    # Return API Gateway formatted response
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(result)
    }

# Serverless framework abstraction
class ServerlessFunction:
    def __init__(self, handler, runtime='python3.9'):
        self.handler = handler
        self.runtime = runtime
        self.environment = {}
        self.triggers = []
        self.layers = []
        
    def add_http_trigger(self, method, path):
        self.triggers.append({
            'type': 'http',
            'method': method,
            'path': path,
            'cors': True
        })
        
    def add_event_trigger(self, event_source):
        self.triggers.append({
            'type': 'event',
            'source': event_source
        })
        
    def with_environment(self, env_vars):
        self.environment.update(env_vars)
        return self
        
    def with_layer(self, layer_arn):
        self.layers.append(layer_arn)
        return self

# Cold start optimization
class ColdStartOptimizer:
    def __init__(self):
        self.connections = {}
        self.initialized = False
        
    def get_connection(self, key, factory):
        """Reuse connections across invocations"""
        if key not in self.connections:
            self.connections[key] = factory()
        return self.connections[key]
    
    def initialize_once(self, init_fn):
        """Run expensive initialization only on cold start"""
        if not self.initialized:
            init_fn()
            self.initialized = True

# Global scope for connection reuse
optimizer = ColdStartOptimizer()

def optimized_handler(event, context):
    # Reuse database connection
    db = optimizer.get_connection('postgres', 
        lambda: psycopg2.connect(os.environ['DATABASE_URL'])
    )
    
    # Initialize ML model once
    optimizer.initialize_once(lambda: load_ml_model())
    
    # Fast path for warm invocations
    return process_with_connections(event, db)

# Event-driven patterns
class EventProcessor:
    def __init__(self):
        self.handlers = {}
        
    def register(self, event_type, handler):
        self.handlers[event_type] = handler
        
    def process(self, event, context):
        # Route based on event source
        if 's3' in event:
            return self.process_s3_event(event)
        elif 'Records' in event and event['Records'][0].get('eventSource') == 'aws:sqs':
            return self.process_sqs_event(event)
        elif 'Records' in event and event['Records'][0].get('eventSource') == 'aws:dynamodb':
            return self.process_dynamodb_stream(event)
        else:
            return self.process_api_request(event)
    
    def process_s3_event(self, event):
        """Handle S3 upload events"""
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            # Download and process file
            s3 = boto3.client('s3')
            obj = s3.get_object(Bucket=bucket, Key=key)
            
            # Process based on file type
            if key.endswith('.jpg'):
                return self.process_image(obj['Body'])
            elif key.endswith('.csv'):
                return self.process_csv(obj['Body'])
    
    def process_sqs_event(self, event):
        """Handle SQS messages"""
        results = []
        
        for record in event['Records']:
            message = json.loads(record['body'])
            
            try:
                result = self.handlers[message['type']](message['payload'])
                results.append(result)
            except Exception as e:
                # Failed messages go back to queue
                raise
                
        return {'batchItemFailures': []}

# Orchestration with Step Functions
class StepFunctionWorkflow:
    def __init__(self, name):
        self.name = name
        self.states = {}
        self.start_state = None
        
    def add_task(self, name, function_arn, next_state=None):
        self.states[name] = {
            'Type': 'Task',
            'Resource': function_arn,
            'Next': next_state,
            'Retry': [{
                'ErrorEquals': ['States.TaskFailed'],
                'IntervalSeconds': 2,
                'MaxAttempts': 3,
                'BackoffRate': 2.0
            }]
        }
        
    def add_parallel(self, name, branches, next_state=None):
        self.states[name] = {
            'Type': 'Parallel',
            'Branches': branches,
            'Next': next_state
        }
        
    def add_choice(self, name, choices):
        self.states[name] = {
            'Type': 'Choice',
            'Choices': choices
        }
        
    def to_json(self):
        return {
            'Comment': f'{self.name} workflow',
            'StartAt': self.start_state,
            'States': self.states
        }

# Example: Image processing pipeline
def create_image_pipeline():
    workflow = StepFunctionWorkflow('ImageProcessing')
    
    # Step 1: Validate image
    workflow.add_task('ValidateImage', 
        'arn:aws:lambda:region:account:function:validate-image',
        next_state='ProcessingChoice'
    )
    
    # Step 2: Choose processing path
    workflow.add_choice('ProcessingChoice', [
        {
            'Variable': '$.imageType',
            'StringEquals': 'photo',
            'Next': 'ProcessPhoto'
        },
        {
            'Variable': '$.imageType',
            'StringEquals': 'document',
            'Next': 'ProcessDocument'
        }
    ])
    
    # Step 3a: Photo processing
    workflow.add_parallel('ProcessPhoto', [
        {'StartAt': 'ResizeImage', 'States': {...}},
        {'StartAt': 'ExtractMetadata', 'States': {...}},
        {'StartAt': 'DetectFaces', 'States': {...}}
    ], next_state='SaveResults')
    
    # Step 3b: Document processing
    workflow.add_task('ProcessDocument',
        'arn:aws:lambda:region:account:function:ocr-document',
        next_state='SaveResults'
    )
    
    # Step 4: Save results
    workflow.add_task('SaveResults',
        'arn:aws:lambda:region:account:function:save-to-dynamodb'
    )
    
    workflow.start_state = 'ValidateImage'
    return workflow

# Performance patterns
class ServerlessPerformance:
    @staticmethod
    def minimize_cold_starts():
        """Strategies to reduce cold start impact"""
        return {
            'provisioned_concurrency': {
                'keeps_warm': 100,  # Keep 100 instances warm
                'cost': 'higher',
                'latency': 'consistent'
            },
            'smaller_deployment_package': {
                'use_layers': True,
                'exclude_dev_dependencies': True,
                'tree_shake': True
            },
            'runtime_choice': {
                'fastest_cold_start': 'go',
                'fast': ['rust', 'nodejs'],
                'slower': ['python', 'java']
            },
            'connection_pooling': {
                'reuse_across_invocations': True,
                'lazy_initialization': True
            }
        }
    
    @staticmethod
    def optimize_memory():
        """Memory = CPU in Lambda"""
        def find_optimal_memory(function_name):
            memories = [128, 256, 512, 1024, 1536, 2048, 3008]
            results = []
            
            for memory in memories:
                # Update function configuration
                lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    MemorySize=memory
                )
                
                # Run performance test
                durations = []
                for _ in range(10):
                    response = lambda_client.invoke(
                        FunctionName=function_name,
                        InvocationType='RequestResponse'
                    )
                    durations.append(response['Duration'])
                
                avg_duration = sum(durations) / len(durations)
                cost = (memory / 1024) * (avg_duration / 1000) * 0.0000166667
                
                results.append({
                    'memory': memory,
                    'duration': avg_duration,
                    'cost': cost
                })
            
            # Find sweet spot
            return min(results, key=lambda x: x['cost'])
```bash
## Advanced Patterns

```python
# Fan-out/Fan-in pattern
class FanOutFanIn:
    def __init__(self, mapper_fn, reducer_fn):
        self.mapper = mapper_fn
        self.reducer = reducer_fn
        
    async def execute(self, items):
        # Fan-out: Process items in parallel
        sns = boto3.client('sns')
        topic_arn = os.environ['MAPPER_TOPIC']
        
        futures = []
        for item in items:
            response = sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps({
                    'item': item,
                    'job_id': str(uuid4())
                })
            )
            futures.append(response)
            
        # Wait for all mappers to complete
        # (In practice, use SQS/DynamoDB to track)
        
        # Fan-in: Collect and reduce results
        results = await self.collect_results()
        return self.reducer(results)

# Saga pattern with Lambda
class LambdaSaga:
    def __init__(self, table_name):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        
    def start_saga(self, saga_id, steps):
        # Initialize saga state
        self.table.put_item(Item={
            'saga_id': saga_id,
            'status': 'RUNNING',
            'current_step': 0,
            'steps': steps,
            'completed_steps': []
        })
        
        # Trigger first step
        self.execute_step(saga_id, 0)
        
    def execute_step(self, saga_id, step_index):
        # Get saga state
        response = self.table.get_item(Key={'saga_id': saga_id})
        saga = response['Item']
        
        if saga['status'] != 'RUNNING':
            return
            
        step = saga['steps'][step_index]
        
        try:
            # Invoke step function
            lambda_client = boto3.client('lambda')
            result = lambda_client.invoke(
                FunctionName=step['function'],
                InvocationType='RequestResponse',
                Payload=json.dumps(step['payload'])
            )
            
            # Update saga state
            saga['completed_steps'].append({
                'index': step_index,
                'result': json.loads(result['Payload'].read())
            })
            
            # Next step or complete
            if step_index + 1 < len(saga['steps']):
                saga['current_step'] = step_index + 1
                self.execute_step(saga_id, step_index + 1)
            else:
                saga['status'] = 'COMPLETED'
                
            self.table.put_item(Item=saga)
            
        except Exception as e:
            # Compensation logic
            self.compensate_saga(saga_id, step_index)
```

## ✓ CHOOSE THIS WHEN:
• Variable/unpredictable load
• Event-driven processing
• Microservices without servers
• Cost optimization important
• Rapid development needed

## ⚠️ BEWARE OF:
• Cold start latency
• 15-minute timeout limit
• Vendor lock-in
• Local development challenges
• Debugging distributed functions

## REAL EXAMPLES
• **iRobot**: 100% serverless architecture
• **Coca-Cola**: Vending machine backends
• **Financial Times**: Content pipeline

---

**Previous**: [← Saga (Distributed Transactions)](saga.md) | **Next**: [Service Discovery Pattern →](service-discovery.md)
## ✅ When to Use

### Ideal Scenarios
- **Distributed systems** with external dependencies
- **High-availability services** requiring reliability
- **External service integration** with potential failures
- **High-traffic applications** needing protection

### Environmental Factors
- **High Traffic**: System handles significant load
- **External Dependencies**: Calls to other services or systems
- **Reliability Requirements**: Uptime is critical to business
- **Resource Constraints**: Limited connections, threads, or memory

### Team Readiness
- Team understands distributed systems concepts
- Monitoring and alerting infrastructure exists
- Operations team can respond to pattern-related alerts

### Business Context
- Cost of downtime is significant
- User experience is a priority
- System is customer-facing or business-critical



## ❌ When NOT to Use

### Inappropriate Scenarios
- **Simple applications** with minimal complexity
- **Development environments** where reliability isn't critical
- **Single-user systems** without scale requirements
- **Internal tools** with relaxed availability needs

### Technical Constraints
- **Simple Systems**: Overhead exceeds benefits
- **Development/Testing**: Adds unnecessary complexity
- **Performance Critical**: Pattern overhead is unacceptable
- **Legacy Systems**: Cannot be easily modified

### Resource Limitations
- **No Monitoring**: Cannot observe pattern effectiveness
- **Limited Expertise**: Team lacks distributed systems knowledge
- **Tight Coupling**: System design prevents pattern implementation

### Anti-Patterns
- Adding complexity without clear benefit
- Implementing without proper monitoring
- Using as a substitute for fixing root causes
- Over-engineering simple problems



## ⚖️ Trade-offs

### Benefits vs Costs

| Benefit | Cost | Mitigation |
|---------|------|------------|
| **Improved Reliability** | Implementation complexity | Use proven libraries/frameworks |
| **Better Performance** | Resource overhead | Monitor and tune parameters |
| **Faster Recovery** | Operational complexity | Invest in monitoring and training |
| **Clearer Debugging** | Additional logging | Use structured logging |

### Performance Impact
- **Latency**: Small overhead per operation
- **Memory**: Additional state tracking
- **CPU**: Monitoring and decision logic
- **Network**: Possible additional monitoring calls

### Operational Complexity
- **Monitoring**: Need dashboards and alerts
- **Configuration**: Parameters must be tuned
- **Debugging**: Additional failure modes to understand
- **Testing**: More scenarios to validate

### Development Trade-offs
- **Initial Cost**: More time to implement correctly
- **Maintenance**: Ongoing tuning and monitoring
- **Testing**: Complex failure scenarios to validate
- **Documentation**: More concepts for team to understand



## 💻 Code Sample

### Basic Implementation

```python
class Serverless_FaasPattern:
    def __init__(self, config):
        self.config = config
        self.metrics = Metrics()
        self.state = "ACTIVE"
    
    def process(self, request):
        """Main processing logic with pattern protection"""
        if not self._is_healthy():
            return self._fallback(request)
        
        try:
            result = self._protected_operation(request)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            return self._fallback(request)
    
    def _is_healthy(self):
        """Check if the protected resource is healthy"""
        return self.metrics.error_rate < self.config.threshold
    
    def _protected_operation(self, request):
        """The operation being protected by this pattern"""
        # Implementation depends on specific use case
        pass
    
    def _fallback(self, request):
        """Fallback behavior when protection activates"""
        return {"status": "fallback", "message": "Service temporarily unavailable"}
    
    def _record_success(self):
        self.metrics.record_success()
    
    def _record_failure(self, error):
        self.metrics.record_failure(error)

# Usage example
pattern = Serverless_FaasPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
serverless_faas:
  enabled: true
  thresholds:
    failure_rate: 50%
    response_time: 5s
    error_count: 10
  timeouts:
    operation: 30s
    recovery: 60s
  fallback:
    enabled: true
    strategy: "cached_response"
  monitoring:
    metrics_enabled: true
    health_check_interval: 30s
```

### Testing the Implementation

```python
def test_serverless_faas_behavior():
    pattern = Serverless_FaasPattern(test_config)
    
    # Test normal operation
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
    
    # Test failure handling
    with mock.patch('external_service.call', side_effect=Exception):
        result = pattern.process(failing_request)
        assert result['status'] == 'fallback'
    
    # Test recovery
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
```




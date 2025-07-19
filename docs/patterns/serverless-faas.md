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
```

## THE SOLUTION

```
Serverless: Pay only for execution time

Request → API Gateway → Lambda → Response
              ↓           ↓
         Auto-scale    Millisecond
         to millions   billing
```

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
```

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
```

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
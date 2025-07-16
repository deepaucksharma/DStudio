Page 52: Serverless (FaaS)
NoOps: The server is dead, long live the function
THE PROBLEM
Traditional servers:
- Pay for idle time
- Manual scaling
- OS patching
- Complex deployment
- Over-provisioning
THE SOLUTION
Functions as a Service:
- Pay per invocation
- Auto-scaling to zero
- No infrastructure management
- Deploy code, not servers
- Event-driven execution
Serverless Patterns:
1. REQUEST/RESPONSE
   API Gateway → Lambda → Response
   
2. EVENT PROCESSING
   S3 Upload → Lambda → Process → DynamoDB
   
3. SCHEDULED TASKS
   CloudWatch Event → Lambda → Batch Job
   
4. STREAM PROCESSING
   Kinesis → Lambda → Analytics
PSEUDO CODE IMPLEMENTATION
ServerlessRuntime:
    handle_invocation(event, context):
        // Cold start if needed
        if not container_warm:
            container = create_container()
            runtime = initialize_runtime()
            user_code = load_user_function()
            container_warm = true
            
        // Set execution context
        context.remaining_time = calculate_timeout()
        context.request_id = generate_request_id()
        context.memory_limit = allocated_memory
        
        // Execute with limits
        try:
            result = with_timeout(
                user_code.handler(event, context),
                context.remaining_time
            )
            return success_response(result)
        catch error:
            return error_response(error)
        finally:
            log_execution_metrics()

ColdStartOptimization:
    // Minimize cold starts
    strategies:
        - Provisioned concurrency (keep N warm)
        - Smaller deployment packages
        - Lazy loading of dependencies
        - Connection pooling across invocations
        - Native runtime vs interpreted

EventSourceMapping:
    // Connect event sources to functions
    mappings = {
        's3:ObjectCreated': image_processor,
        'dynamodb:INSERT': stream_processor,
        'api:/users/*': user_handler,
        'schedule:rate(5 min)': health_checker
    }
    
    on_event(source, event):
        handler = mappings.get(source)
        if handler:
            invoke_async(handler, event)
Serverless Best Practices:
1. IDEMPOTENCY
   // Functions may retry
   handler(event):
       if already_processed(event.id):
           return cached_result(event.id)
       result = process(event)
       cache_result(event.id, result)
       return result

2. CONNECTION REUSE
   // Initialize outside handler
   db_connection = null
   
   handler(event):
       if not db_connection:
           db_connection = create_connection()
       return db_connection.query(...)

3. ASYNC PATTERNS
   // Don't wait if not needed
   handler(event):
       // Quick response
       send_to_queue(event)
       return {status: 'accepted'}
       
   // Separate processor
   processor(queue_event):
       // Heavy lifting here
✓ CHOOSE THIS WHEN:

Variable/unpredictable load
Event-driven workloads
Prototype/MVP development
Batch processing
Webhook handlers

⚠️ BEWARE OF:

Cold start latency
15-minute timeout limit
Vendor lock-in
Limited local testing
Complex debugging

REAL EXAMPLES

Netflix: Video encoding pipeline
iRobot: IoT data processing
Coca-Cola: Vending machine backends

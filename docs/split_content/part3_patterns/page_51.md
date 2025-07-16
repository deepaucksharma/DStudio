Page 51: GraphQL & API Gateway
One endpoint to rule them all
THE PROBLEM
REST APIs lead to:
- Over-fetching (getting unused fields)
- Under-fetching (N+1 queries)
- Multiple round trips
- Version proliferation
- No type safety
THE SOLUTION
GraphQL provides:
- Single endpoint
- Client specifies exact needs
- Type system
- Introspection

API Gateway adds:
- Authentication
- Rate limiting
- Caching
- Protocol translation
GraphQL Architecture:
Client Query:              Server Resolution:
{                         1. Parse & Validate
  user(id: 123) {        2. Execute resolvers
    name                 3. N+1 prevention
    posts {              4. Return exact shape
      title
      comments {
        text
      }
    }
  }
}
PSEUDO CODE IMPLEMENTATION
GraphQLServer:
    schema = build_schema(type_definitions)
    
    execute_query(query, context):
        // Parse and validate
        document = parse(query)
        errors = validate(document, schema)
        if errors:
            return {errors}
            
        // Build execution plan
        plan = build_execution_plan(document)
        
        // Execute with DataLoader for batching
        result = await execute_plan(plan, context)
        
        return {data: result}

DataLoader:
    // Prevents N+1 queries
    batch_load_fn = null
    cache = {}
    batch = []
    
    load(key):
        if key in cache:
            return cache[key]
            
        batch.append(key)
        
        // Batch execution on next tick
        schedule_batch_execution()
        
        return promise_for(key)
    
    execute_batch():
        keys = unique(batch)
        results = batch_load_fn(keys)
        
        for key, result in zip(keys, results):
            cache[key] = result
            resolve_promise(key, result)

APIGateway:
    handle_request(request):
        // Authentication
        auth = authenticate(request.headers['authorization'])
        if not auth.valid:
            return 401_unauthorized()
            
        // Rate limiting
        if not rate_limiter.allow(auth.client_id):
            return 429_too_many_requests()
            
        // Route to appropriate backend
        if request.path.startswith('/graphql'):
            return graphql_handler(request, auth)
        elif request.path.startswith('/rest'):
            return rest_handler(request, auth)
        elif request.is_websocket:
            return websocket_handler(request, auth)
            
        // Transform protocols if needed
        if request.is_grpc:
            return grpc_to_rest_bridge(request)
Common Patterns:
1. SCHEMA STITCHING
   // Combine multiple GraphQL services
   gateway_schema = stitch_schemas([
       user_service_schema,
       product_service_schema,
       order_service_schema
   ])

2. FEDERATION
   // Each service owns its types
   UserService:
     type User @key(fields: "id") {
       id: ID!
       name: String
     }
   
   OrderService:
     extend type User @key(fields: "id") {
       id: ID! @external
       orders: [Order]
     }

3. PERSISTED QUERIES
   // Client sends hash instead of query
   client.query({id: "query_hash_123"})
   // Server looks up pre-registered query
✓ CHOOSE THIS WHEN:

Multiple client types (web, mobile)
Complex data requirements
Need to reduce requests
Rapid API evolution
Type safety important

⚠️ BEWARE OF:

Complex queries can overload
Caching is harder
Query complexity attacks
Learning curve
Monitoring/debugging tools

REAL EXAMPLES

GitHub: Entire API is GraphQL
Netflix: Federated GraphQL
Shopify: GraphQL for merchants

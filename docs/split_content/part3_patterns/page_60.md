Page 60: Bulkhead Isolation
Compartmentalize failure like ships do
THE PROBLEM
Shared resources mean shared failure:
- One bad endpoint uses all threads
- One customer floods the system
- One feature kills entire service
THE SOLUTION
Isolate resources by:
- Thread pools per endpoint
- Connection pools per service
- Rate limits per customer
- Separate deployment units
PSEUDO CODE IMPLEMENTATION
BulkheadManager:
    thread_pools = {}
    
    create_bulkhead(name, config):
        thread_pools[name] = ThreadPool(
            core_size=config.core_size,
            max_size=config.max_size,
            queue_size=config.queue_size,
            rejection_policy=config.rejection_policy
        )
        
    execute(bulkhead_name, operation):
        pool = thread_pools[bulkhead_name]
        
        if pool.active_count() >= pool.max_size:
            return handle_rejection()
            
        return pool.submit(operation)

MultiTenantBulkhead:
    // Isolate by customer
    limits_per_tenant = load_tenant_limits()
    
    handle_request(tenant_id, request):
        limiter = get_limiter(tenant_id)
        
        if not limiter.try_acquire():
            return rate_limit_exceeded()
            
        bulkhead = get_tenant_bulkhead(tenant_id)
        return bulkhead.execute(request)

ResourceIsolation:
    // Different pools for different operations
    pools = {
        'critical': ThreadPool(size=50),   // Payments
        'normal': ThreadPool(size=100),    // Regular API
        'batch': ThreadPool(size=20),      // Reports
        'admin': ThreadPool(size=10)       // Admin ops
    }
    
    route_request(request):
        pool_name = classify_request(request)
        return pools[pool_name].execute(request)

DeploymentBulkhead:
    // Physical isolation
    deployments = {
        'api-critical': {
            instances: 20,
            resources: 'dedicated-hosts',
            isolation: 'separate-vpc'
        },
        'api-batch': {
            instances: 10,
            resources: 'spot-instances',
            isolation: 'shared-vpc'
        }
    }
Bulkhead Patterns:
1. THREAD POOL ISOLATION
   Each dependency gets own pool
   Failure isolated to that pool

2. SEMAPHORE ISOLATION
   Lighter weight than threads
   Good for I/O bound operations

3. CONNECTION POOL ISOLATION
   Separate pools per downstream
   Prevents connection exhaustion

4. PROCESS ISOLATION
   Different processes/containers
   Complete failure isolation
✓ CHOOSE THIS WHEN:

Multiple types of workload
Multi-tenant system
Varying SLAs per operation
Protection from bad actors
Resource limits needed

⚠️ BEWARE OF:

Resource overhead
Configuration complexity
Monitoring many pools
Sizing pools correctly
Coordination between bulkheads

REAL EXAMPLES

Netflix: Hystrix thread pools
Amazon: Service isolation
Kubernetes: Resource quotas

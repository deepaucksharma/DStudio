# Bulkhead Pattern

**Isolate failures like ships isolate water**

## THE PROBLEM

```
One bad feature takes down everything:

/api/search → Uses 100% threads → 
/api/checkout → No threads left → Site down!

Resource exhaustion spreads like water in a ship
```

## THE SOLUTION

```
Bulkheads: Isolate resources by function

Thread Pool 1 (Search): 20 threads
Thread Pool 2 (Checkout): 50 threads  
Thread Pool 3 (Analytics): 10 threads

Search floods? Only search drowns!
```

## Bulkhead Types

```
1. THREAD ISOLATION
   Separate thread pools per function
   
2. SEMAPHORE ISOLATION
   Limit concurrent requests
   
3. CONNECTION ISOLATION  
   Separate connection pools
   
4. PROCESS ISOLATION
   Separate processes/containers
```

## IMPLEMENTATION

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Callable, Any, Dict
import threading
from contextlib import asynccontextmanager

class ThreadPoolBulkhead:
    """Isolate operations in separate thread pools"""
    
    def __init__(self, name: str, size: int = 10):
        self.name = name
        self.size = size
        self.pool = ThreadPoolExecutor(
            max_workers=size,
            thread_name_prefix=f"bulkhead-{name}-"
        )
        self.active_count = 0
        self.rejected_count = 0
        self.lock = threading.Lock()
        
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function in isolated thread pool"""
        
        with self.lock:
            if self.active_count >= self.size:
                self.rejected_count += 1
                raise BulkheadFullError(f"Bulkhead '{self.name}' is full")
                
            self.active_count += 1
            
        try:
            future = self.pool.submit(func, *args, **kwargs)
            return future.result()
        finally:
            with self.lock:
                self.active_count -= 1
    
    def get_stats(self) -> dict:
        """Get bulkhead statistics"""
        return {
            'name': self.name,
            'size': self.size,
            'active': self.active_count,
            'rejected': self.rejected_count,
            'utilization': self.active_count / self.size
        }

class SemaphoreBulkhead:
    """Limit concurrent operations with semaphore"""
    
    def __init__(self, name: str, permits: int = 10):
        self.name = name
        self.permits = permits
        self.semaphore = asyncio.Semaphore(permits)
        self.active_count = 0
        self.rejected_count = 0
        self.total_count = 0
        
    @asynccontextmanager
    async def acquire(self, timeout: Optional[float] = None):
        """Acquire permit with optional timeout"""
        
        acquired = False
        try:
            if timeout:
                # Try to acquire with timeout
                try:
                    await asyncio.wait_for(
                        self.semaphore.acquire(), 
                        timeout=timeout
                    )
                    acquired = True
                except asyncio.TimeoutError:
                    self.rejected_count += 1
                    raise BulkheadTimeoutError(
                        f"Timeout acquiring permit for '{self.name}'"
                    )
            else:
                # Try to acquire without blocking
                acquired = self.semaphore.locked() == False
                if acquired:
                    await self.semaphore.acquire()
                else:
                    self.rejected_count += 1
                    raise BulkheadFullError(f"Bulkhead '{self.name}' is full")
                    
            self.active_count += 1
            self.total_count += 1
            yield
            
        finally:
            if acquired:
                self.active_count -= 1
                self.semaphore.release()

class BulkheadManager:
    """Manage multiple bulkheads"""
    
    def __init__(self):
        self.bulkheads: Dict[str, SemaphoreBulkhead] = {}
        self.default_permits = 10
        
    def create_bulkhead(self, name: str, permits: int = None) -> SemaphoreBulkhead:
        """Create or get bulkhead"""
        
        if name not in self.bulkheads:
            self.bulkheads[name] = SemaphoreBulkhead(
                name=name,
                permits=permits or self.default_permits
            )
        return self.bulkheads[name]
    
    def get_all_stats(self) -> Dict[str, dict]:
        """Get stats for all bulkheads"""
        return {
            name: bulkhead.get_stats()
            for name, bulkhead in self.bulkheads.items()
        }

# Connection pool bulkhead
class ConnectionPoolBulkhead:
    """Isolate database connections by function"""
    
    def __init__(self, pools_config: dict):
        self.pools = {}
        
        for name, config in pools_config.items():
            self.pools[name] = self._create_pool(name, config)
            
    def _create_pool(self, name: str, config: dict):
        """Create isolated connection pool"""
        
        return ConnectionPool(
            host=config['host'],
            port=config['port'],
            min_size=config.get('min_size', 1),
            max_size=config.get('max_size', 10),
            name=f"bulkhead-{name}"
        )
    
    async def execute(self, bulkhead_name: str, query: str, *args):
        """Execute query in specific bulkhead"""
        
        if bulkhead_name not in self.pools:
            raise ValueError(f"Unknown bulkhead: {bulkhead_name}")
            
        pool = self.pools[bulkhead_name]
        
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

# HTTP client with bulkheads
class BulkheadHTTPClient:
    """HTTP client with endpoint isolation"""
    
    def __init__(self):
        self.bulkheads = {}
        self.default_config = {
            'max_connections': 10,
            'timeout': 5.0
        }
        
    def configure_endpoint(self, pattern: str, **config):
        """Configure bulkhead for endpoint pattern"""
        
        merged_config = {**self.default_config, **config}
        
        self.bulkheads[pattern] = {
            'connector': aiohttp.TCPConnector(
                limit=merged_config['max_connections']
            ),
            'timeout': aiohttp.ClientTimeout(
                total=merged_config['timeout']
            ),
            'semaphore': asyncio.Semaphore(
                merged_config['max_connections']
            )
        }
    
    async def request(self, method: str, url: str, **kwargs):
        """Make request with appropriate bulkhead"""
        
        # Find matching bulkhead
        bulkhead = self._find_bulkhead(url)
        
        if not bulkhead:
            raise ValueError(f"No bulkhead configured for {url}")
            
        # Acquire semaphore
        async with bulkhead['semaphore']:
            # Create session with bulkhead connector
            async with aiohttp.ClientSession(
                connector=bulkhead['connector'],
                timeout=bulkhead['timeout']
            ) as session:
                async with session.request(method, url, **kwargs) as response:
                    return await response.json()
    
    def _find_bulkhead(self, url: str):
        """Find bulkhead for URL"""
        
        for pattern, bulkhead in self.bulkheads.items():
            if pattern in url:
                return bulkhead
        return None

# Process isolation with containers
class ContainerBulkhead:
    """Run operations in isolated containers"""
    
    def __init__(self, docker_client):
        self.docker = docker_client
        self.containers = {}
        
    async def execute_in_container(
        self, 
        bulkhead_name: str,
        image: str,
        command: str,
        resources: dict = None
    ):
        """Execute command in isolated container"""
        
        # Default resource limits
        if not resources:
            resources = {
                'mem_limit': '512m',
                'cpu_quota': 50000,  # 0.5 CPU
                'cpu_period': 100000
            }
            
        # Run container with resource limits
        container = self.docker.containers.run(
            image=image,
            command=command,
            detach=True,
            remove=True,
            name=f"bulkhead-{bulkhead_name}-{time.time()}",
            **resources
        )
        
        # Wait for completion
        result = container.wait()
        logs = container.logs().decode('utf-8')
        
        if result['StatusCode'] != 0:
            raise ContainerExecutionError(
                f"Container failed with status {result['StatusCode']}: {logs}"
            )
            
        return logs

# Adaptive bulkhead that adjusts size based on load
class AdaptiveBulkhead:
    """Dynamically adjust bulkhead size"""
    
    def __init__(
        self, 
        name: str,
        min_size: int = 5,
        max_size: int = 50,
        target_utilization: float = 0.7
    ):
        self.name = name
        self.min_size = min_size
        self.max_size = max_size
        self.target_utilization = target_utilization
        
        self.current_size = min_size
        self.semaphore = asyncio.Semaphore(min_size)
        self.active_count = 0
        
        # Metrics for adaptation
        self.utilization_history = []
        self.rejection_count = 0
        
        # Start adaptation loop
        asyncio.create_task(self._adapt_loop())
        
    async def _adapt_loop(self):
        """Periodically adjust bulkhead size"""
        
        while True:
            await asyncio.sleep(10)  # Adjust every 10 seconds
            
            # Calculate average utilization
            if self.utilization_history:
                avg_utilization = sum(self.utilization_history) / len(self.utilization_history)
                
                if avg_utilization > self.target_utilization + 0.1:
                    # Increase size
                    await self._resize(min(
                        self.max_size,
                        int(self.current_size * 1.5)
                    ))
                elif avg_utilization < self.target_utilization - 0.1:
                    # Decrease size
                    await self._resize(max(
                        self.min_size,
                        int(self.current_size * 0.8)
                    ))
                    
            # Reset history
            self.utilization_history = []
            
    async def _resize(self, new_size: int):
        """Resize bulkhead"""
        
        if new_size == self.current_size:
            return
            
        print(f"Resizing bulkhead '{self.name}' from {self.current_size} to {new_size}")
        
        # Create new semaphore
        new_semaphore = asyncio.Semaphore(new_size)
        
        # Copy current permits
        for _ in range(self.current_size - self.active_count):
            await self.semaphore.acquire()
            
        self.semaphore = new_semaphore
        self.current_size = new_size
```

## Usage Examples

```python
# Example 1: API endpoint isolation
bulkhead_manager = BulkheadManager()

# Configure bulkheads for different endpoints
search_bulkhead = bulkhead_manager.create_bulkhead('search', permits=20)
checkout_bulkhead = bulkhead_manager.create_bulkhead('checkout', permits=50)
analytics_bulkhead = bulkhead_manager.create_bulkhead('analytics', permits=10)

async def handle_search_request(query: str):
    async with search_bulkhead.acquire(timeout=1.0):
        # Search operations isolated
        return await search_service.search(query)

async def handle_checkout_request(cart_id: str):
    async with checkout_bulkhead.acquire(timeout=5.0):
        # Checkout operations isolated
        return await checkout_service.process(cart_id)

# Example 2: Database connection isolation
db_bulkheads = ConnectionPoolBulkhead({
    'transactional': {
        'host': 'db-primary',
        'port': 5432,
        'min_size': 10,
        'max_size': 50
    },
    'analytics': {
        'host': 'db-analytics',
        'port': 5432,
        'min_size': 5,
        'max_size': 20
    },
    'batch': {
        'host': 'db-batch',
        'port': 5432,
        'min_size': 2,
        'max_size': 10
    }
})

# Use appropriate bulkhead for operation type
await db_bulkheads.execute('transactional', 
    "UPDATE orders SET status = $1 WHERE id = $2",
    'completed', order_id
)

await db_bulkheads.execute('analytics',
    "INSERT INTO metrics (timestamp, value) VALUES ($1, $2)",
    datetime.now(), metric_value
)
```

## ✓ CHOOSE THIS WHEN:
• Preventing cascade failures
• Resource isolation needed
• Multi-tenant systems
• Mixed workload types
• Protecting critical paths

## ⚠️ BEWARE OF:
• Resource overhead
• Configuration complexity
• Bulkhead sizing
• Monitoring many bulkheads
• Cross-bulkhead dependencies

## REAL EXAMPLES
• **Netflix Hystrix**: Thread pool isolation
• **Kubernetes**: Resource quotas/limits
• **AWS Lambda**: Function concurrency limits
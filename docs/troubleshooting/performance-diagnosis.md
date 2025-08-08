# Performance Diagnosis in Distributed Systems

## Overview
Performance issues in distributed systems can stem from various sources including network latency, resource contention, inefficient algorithms, and architectural bottlenecks. This guide provides systematic approaches to identify, diagnose, and resolve performance problems.

## Performance Metrics Hierarchy

### System-Level Metrics
- **Throughput**: Requests processed per second
- **Latency**: Response time percentiles (P50, P95, P99, P99.9)
- **Error Rate**: Percentage of failed requests
- **Resource Utilization**: CPU, memory, disk, network usage

### Application-Level Metrics
- **Business Transaction Performance**: End-to-end user journey timing
- **Database Query Performance**: Query execution time and frequency
- **Cache Hit Rates**: Cache effectiveness metrics
- **Queue Depths**: Message queue backlogs

## Diagnostic Tools and Techniques

### 1. Application Performance Monitoring (APM)

```python
import time
import functools
import asyncio
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict
import statistics

@dataclass
class PerformanceMetric:
    operation: str
    duration_ms: float
    timestamp: float
    success: bool
    metadata: Dict = field(default_factory=dict)

class PerformanceProfiler:
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.operation_stats: Dict[str, List[float]] = defaultdict(list)
        self.active_operations: Dict[str, float] = {}
    
    @contextmanager
    def measure_operation(self, operation_name: str, **metadata):
        start_time = time.time()
        operation_id = f"{operation_name}_{id(self)}"
        self.active_operations[operation_id] = start_time
        
        success = True
        try:
            yield
        except Exception as e:
            success = False
            metadata['error'] = str(e)
            raise
        finally:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            metric = PerformanceMetric(
                operation=operation_name,
                duration_ms=duration_ms,
                timestamp=end_time,
                success=success,
                metadata=metadata
            )
            
            self.metrics.append(metric)
            self.operation_stats[operation_name].append(duration_ms)
            self.active_operations.pop(operation_id, None)
    
    def performance_decorator(self, operation_name: str = None):
        def decorator(func):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self.measure_operation(op_name):
                    return await func(*args, **kwargs)
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                with self.measure_operation(op_name):
                    return func(*args, **kwargs)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def get_performance_summary(self, time_window_minutes: int = 5) -> Dict:
        cutoff_time = time.time() - (time_window_minutes * 60)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        
        summary = {}
        operations = set(m.operation for m in recent_metrics)
        
        for operation in operations:
            op_metrics = [m for m in recent_metrics if m.operation == operation]
            durations = [m.duration_ms for m in op_metrics]
            errors = [m for m in op_metrics if not m.success]
            
            if durations:
                summary[operation] = {
                    'count': len(durations),
                    'error_count': len(errors),
                    'error_rate': len(errors) / len(durations),
                    'avg_duration_ms': statistics.mean(durations),
                    'p50_ms': statistics.median(durations),
                    'p95_ms': statistics.quantiles(durations, n=20)[18] if len(durations) > 1 else durations[0],
                    'p99_ms': statistics.quantiles(durations, n=100)[98] if len(durations) > 1 else durations[0],
                    'max_duration_ms': max(durations),
                    'min_duration_ms': min(durations)
                }
        
        return summary

# Global profiler instance
profiler = PerformanceProfiler()

# Usage examples
@profiler.performance_decorator("database_query")
async def fetch_user_data(user_id: str):
    async with database.connection() as conn:
        return await conn.fetch("SELECT * FROM users WHERE id = $1", user_id)

@profiler.performance_decorator("external_api_call")
def call_payment_service(payment_data):
    with profiler.measure_operation("payment_validation"):
        validate_payment_data(payment_data)
    
    response = requests.post(
        "https://payment-service/process",
        json=payment_data,
        timeout=30
    )
    return response.json()
```

### 2. Database Performance Analysis

```python
import psycopg2
import time
from contextlib import contextmanager

class DatabasePerformanceAnalyzer:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.slow_queries: List[Dict] = []
        self.query_stats: Dict = defaultdict(list)
    
    @contextmanager
    def monitored_query(self, query: str, params=None):
        start_time = time.time()
        query_id = hash(query.strip())
        
        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + query, params)
                    explain_result = cursor.fetchone()[0]
                    
                    cursor.execute(query, params)
                    result = cursor.fetchall()
                    
                    end_time = time.time()
                    execution_time = (end_time - start_time) * 1000
                    
                    query_info = {
                        'query': query,
                        'params': params,
                        'execution_time_ms': execution_time,
                        'timestamp': end_time,
                        'explain_plan': explain_result,
                        'rows_returned': len(result)
                    }
                    
                    self.query_stats[query_id].append(execution_time)
                    
                    if execution_time > 1000:  # Slow query threshold: 1 second
                        self.slow_queries.append(query_info)
                    
                    yield result
        except Exception as e:
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000
            
            query_info = {
                'query': query,
                'params': params,
                'execution_time_ms': execution_time,
                'timestamp': end_time,
                'error': str(e),
                'rows_returned': 0
            }
            
            self.slow_queries.append(query_info)
            raise
    
    def get_slow_query_report(self) -> Dict:
        if not self.slow_queries:
            return {"message": "No slow queries detected"}
        
        # Group by similar queries
        query_groups = defaultdict(list)
        for query_info in self.slow_queries:
            # Normalize query for grouping
            normalized = self._normalize_query(query_info['query'])
            query_groups[normalized].append(query_info)
        
        report = {}
        for normalized_query, queries in query_groups.items():
            execution_times = [q['execution_time_ms'] for q in queries]
            report[normalized_query] = {
                'occurrences': len(queries),
                'avg_execution_time_ms': statistics.mean(execution_times),
                'max_execution_time_ms': max(execution_times),
                'total_time_ms': sum(execution_times),
                'examples': queries[:3]  # Show first 3 examples
            }
        
        return report
    
    def _normalize_query(self, query: str) -> str:
        # Remove parameter values and normalize whitespace
        import re
        normalized = re.sub(r'\$\d+', '?', query)
        normalized = re.sub(r'\s+', ' ', normalized.strip())
        return normalized

# Usage
db_analyzer = DatabasePerformanceAnalyzer("postgresql://user:pass@localhost/db")

async def get_user_orders(user_id: str):
    query = """
        SELECT o.*, p.name as product_name
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.user_id = $1
        ORDER BY o.created_at DESC
    """
    
    with db_analyzer.monitored_query(query, [user_id]) as results:
        return results
```

### 3. Network Performance Diagnostics

```python
import httpx
import asyncio
import time
from typing import Dict, List
import statistics

class NetworkPerformanceDiagnostics:
    def __init__(self):
        self.latency_measurements: Dict[str, List[float]] = defaultdict(list)
        self.connection_pool_stats: Dict = {}
    
    async def measure_service_latency(self, service_url: str, endpoints: List[str], 
                                     samples: int = 10) -> Dict:
        """Measure latency to various endpoints of a service"""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            results = {}
            
            for endpoint in endpoints:
                latencies = []
                errors = 0
                
                for _ in range(samples):
                    try:
                        start_time = time.time()
                        response = await client.get(f"{service_url}{endpoint}")
                        end_time = time.time()
                        
                        latency_ms = (end_time - start_time) * 1000
                        latencies.append(latency_ms)
                        
                        # Also measure DNS resolution and connection time
                        # (This would require lower-level HTTP client instrumentation)
                        
                    except Exception as e:
                        errors += 1
                    
                    await asyncio.sleep(0.1)  # Small delay between requests
                
                if latencies:
                    results[endpoint] = {
                        'samples': len(latencies),
                        'errors': errors,
                        'avg_latency_ms': statistics.mean(latencies),
                        'p50_latency_ms': statistics.median(latencies),
                        'p95_latency_ms': statistics.quantiles(latencies, n=20)[18] if len(latencies) > 1 else latencies[0],
                        'max_latency_ms': max(latencies),
                        'min_latency_ms': min(latencies)
                    }
                else:
                    results[endpoint] = {'errors': errors, 'message': 'All requests failed'}
            
            return results
    
    async def diagnose_connection_pool(self, service_urls: List[str]) -> Dict:
        """Diagnose HTTP connection pool performance"""
        
        # Configure connection pool with monitoring
        limits = httpx.Limits(max_keepalive_connections=10, max_connections=100)
        
        async with httpx.AsyncClient(limits=limits) as client:
            # Measure connection pool efficiency
            start_time = time.time()
            
            # Make concurrent requests to test pool behavior
            tasks = []
            for url in service_urls:
                for _ in range(5):  # 5 requests per service
                    task = self._timed_request(client, url)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            successful_requests = [r for r in results if not isinstance(r, Exception)]
            failed_requests = [r for r in results if isinstance(r, Exception)]
            
            if successful_requests:
                latencies = [r['latency_ms'] for r in successful_requests]
                connection_times = [r['connection_time_ms'] for r in successful_requests if 'connection_time_ms' in r]
                
                return {
                    'total_requests': len(results),
                    'successful_requests': len(successful_requests),
                    'failed_requests': len(failed_requests),
                    'total_time_ms': (end_time - start_time) * 1000,
                    'avg_latency_ms': statistics.mean(latencies),
                    'avg_connection_time_ms': statistics.mean(connection_times) if connection_times else 0,
                    'connection_pool_efficiency': len([r for r in successful_requests if r.get('reused_connection', False)]) / len(successful_requests)
                }
            else:
                return {'error': 'All requests failed', 'failed_requests': len(failed_requests)}
    
    async def _timed_request(self, client: httpx.AsyncClient, url: str) -> Dict:
        start_time = time.time()
        
        try:
            response = await client.get(url)
            end_time = time.time()
            
            return {
                'url': url,
                'status_code': response.status_code,
                'latency_ms': (end_time - start_time) * 1000,
                'reused_connection': hasattr(response, 'connection_info') and response.connection_info.get('reused_connection', False)
            }
        except Exception as e:
            end_time = time.time()
            return {
                'url': url,
                'error': str(e),
                'latency_ms': (end_time - start_time) * 1000
            }

# Usage
network_diagnostics = NetworkPerformanceDiagnostics()

async def diagnose_service_performance():
    # Test individual service latencies
    user_service_results = await network_diagnostics.measure_service_latency(
        "http://user-service:8080",
        ["/health", "/api/users/123", "/api/users/search?q=test"],
        samples=20
    )
    
    # Test connection pool performance
    service_urls = [
        "http://user-service:8080/health",
        "http://payment-service:8080/health",
        "http://order-service:8080/health"
    ]
    
    pool_results = await network_diagnostics.diagnose_connection_pool(service_urls)
    
    return {
        'service_latencies': user_service_results,
        'connection_pool_performance': pool_results
    }
```

### 4. Resource Utilization Analysis

```python
import psutil
import asyncio
import time
from dataclasses import dataclass
from typing import List, Dict
import threading

@dataclass
class ResourceSnapshot:
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    process_count: int

class ResourceMonitor:
    def __init__(self, interval_seconds: int = 5):
        self.interval_seconds = interval_seconds
        self.snapshots: List[ResourceSnapshot] = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start continuous resource monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        last_disk_io = psutil.disk_io_counters()
        last_network_io = psutil.net_io_counters()
        
        while self.monitoring:
            try:
                # Get current resource usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Calculate disk I/O delta
                current_disk_io = psutil.disk_io_counters()
                disk_read_mb = (current_disk_io.read_bytes - last_disk_io.read_bytes) / (1024 * 1024)
                disk_write_mb = (current_disk_io.write_bytes - last_disk_io.write_bytes) / (1024 * 1024)
                last_disk_io = current_disk_io
                
                # Calculate network I/O
                current_network_io = psutil.net_io_counters()
                network_sent = current_network_io.bytes_sent - last_network_io.bytes_sent
                network_recv = current_network_io.bytes_recv - last_network_io.bytes_recv
                last_network_io = current_network_io
                
                # Get connection count
                connections = len(psutil.net_connections())
                
                # Get process count
                process_count = len(psutil.pids())
                
                snapshot = ResourceSnapshot(
                    timestamp=time.time(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_available_mb=memory.available / (1024 * 1024),
                    disk_io_read_mb=disk_read_mb,
                    disk_io_write_mb=disk_write_mb,
                    network_bytes_sent=network_sent,
                    network_bytes_recv=network_recv,
                    active_connections=connections,
                    process_count=process_count
                )
                
                self.snapshots.append(snapshot)
                
                # Keep only last 1000 snapshots
                if len(self.snapshots) > 1000:
                    self.snapshots = self.snapshots[-1000:]
                
                time.sleep(self.interval_seconds)
                
            except Exception as e:
                print(f"Error in resource monitoring: {e}")
                time.sleep(self.interval_seconds)
    
    def get_resource_analysis(self, time_window_minutes: int = 10) -> Dict:
        """Analyze resource usage patterns"""
        cutoff_time = time.time() - (time_window_minutes * 60)
        recent_snapshots = [s for s in self.snapshots if s.timestamp > cutoff_time]
        
        if not recent_snapshots:
            return {"error": "No data available"}
        
        cpu_values = [s.cpu_percent for s in recent_snapshots]
        memory_values = [s.memory_percent for s in recent_snapshots]
        
        analysis = {
            'time_window_minutes': time_window_minutes,
            'sample_count': len(recent_snapshots),
            'cpu_usage': {
                'avg_percent': statistics.mean(cpu_values),
                'max_percent': max(cpu_values),
                'p95_percent': statistics.quantiles(cpu_values, n=20)[18] if len(cpu_values) > 1 else cpu_values[0]
            },
            'memory_usage': {
                'avg_percent': statistics.mean(memory_values),
                'max_percent': max(memory_values),
                'p95_percent': statistics.quantiles(memory_values, n=20)[18] if len(memory_values) > 1 else memory_values[0]
            },
            'network_io': {
                'total_bytes_sent': sum(s.network_bytes_sent for s in recent_snapshots),
                'total_bytes_recv': sum(s.network_bytes_recv for s in recent_snapshots)
            },
            'disk_io': {
                'total_read_mb': sum(s.disk_io_read_mb for s in recent_snapshots),
                'total_write_mb': sum(s.disk_io_write_mb for s in recent_snapshots)
            }
        }
        
        # Detect resource bottlenecks
        bottlenecks = []
        if analysis['cpu_usage']['p95_percent'] > 80:
            bottlenecks.append("CPU usage is consistently high (>80%)")
        if analysis['memory_usage']['p95_percent'] > 85:
            bottlenecks.append("Memory usage is critically high (>85%)")
        
        analysis['potential_bottlenecks'] = bottlenecks
        
        return analysis

# Global resource monitor
resource_monitor = ResourceMonitor()
```

## Performance Analysis Workflows

### 1. Systematic Performance Investigation

```python
class PerformanceInvestigator:
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.db_analyzer = DatabasePerformanceAnalyzer()
        self.network_diagnostics = NetworkPerformanceDiagnostics()
        self.resource_monitor = ResourceMonitor()
    
    async def comprehensive_performance_analysis(self) -> Dict:
        """Run comprehensive performance analysis"""
        
        # Start resource monitoring
        self.resource_monitor.start_monitoring()
        
        try:
            # Wait for some baseline data
            await asyncio.sleep(30)
            
            # Collect various performance metrics
            app_performance = self.profiler.get_performance_summary(time_window_minutes=5)
            db_performance = self.db_analyzer.get_slow_query_report()
            network_performance = await self.network_diagnostics.diagnose_service_performance()
            resource_analysis = self.resource_monitor.get_resource_analysis(time_window_minutes=5)
            
            # Analyze patterns and correlations
            analysis_report = self._analyze_performance_patterns(
                app_performance,
                db_performance,
                network_performance,
                resource_analysis
            )
            
            return analysis_report
            
        finally:
            self.resource_monitor.stop_monitoring()
    
    def _analyze_performance_patterns(self, app_perf, db_perf, network_perf, resource_analysis) -> Dict:
        """Analyze performance data for patterns and root causes"""
        
        issues = []
        recommendations = []
        
        # Application performance analysis
        for operation, metrics in app_perf.items():
            if metrics['p95_ms'] > 1000:  # 1 second threshold
                issues.append(f"Slow operation: {operation} (P95: {metrics['p95_ms']:.2f}ms)")
                
            if metrics['error_rate'] > 0.05:  # 5% error rate threshold
                issues.append(f"High error rate in {operation}: {metrics['error_rate']:.2%}")
        
        # Database performance analysis
        if isinstance(db_perf, dict) and 'message' not in db_perf:
            for query, stats in db_perf.items():
                if stats['avg_execution_time_ms'] > 500:
                    issues.append(f"Slow database query detected: {stats['avg_execution_time_ms']:.2f}ms average")
                    recommendations.append("Consider query optimization or indexing")
        
        # Resource utilization analysis
        if resource_analysis.get('potential_bottlenecks'):
            issues.extend(resource_analysis['potential_bottlenecks'])
            
            if 'CPU usage is consistently high' in str(resource_analysis['potential_bottlenecks']):
                recommendations.extend([
                    "Consider horizontal scaling",
                    "Profile CPU-intensive operations",
                    "Implement caching for expensive computations"
                ])
            
            if 'Memory usage is critically high' in str(resource_analysis['potential_bottlenecks']):
                recommendations.extend([
                    "Investigate potential memory leaks",
                    "Optimize data structures and algorithms",
                    "Implement pagination for large datasets"
                ])
        
        # Network performance analysis
        if network_perf and network_perf.get('connection_pool_performance'):
            pool_stats = network_perf['connection_pool_performance']
            if pool_stats.get('connection_pool_efficiency', 1.0) < 0.8:
                issues.append("Low connection pool efficiency detected")
                recommendations.append("Tune HTTP connection pool settings")
        
        return {
            'timestamp': time.time(),
            'issues_detected': issues,
            'recommendations': recommendations,
            'detailed_metrics': {
                'application': app_perf,
                'database': db_perf,
                'network': network_perf,
                'resources': resource_analysis
            }
        }

# Usage
investigator = PerformanceInvestigator()

async def run_performance_investigation():
    report = await investigator.comprehensive_performance_analysis()
    
    print("=== Performance Investigation Report ===")
    print(f"Issues detected: {len(report['issues_detected'])}")
    for issue in report['issues_detected']:
        print(f"- {issue}")
    
    print(f"\nRecommendations: {len(report['recommendations'])}")
    for rec in report['recommendations']:
        print(f"- {rec}")
    
    return report
```

### 2. Load Testing Integration

```bash
#!/bin/bash
# performance_load_test.sh - Automated load testing with performance monitoring

LOAD_TEST_DURATION="5m"
TARGET_URL="$1"
CONCURRENT_USERS="${2:-10}"
RAMP_UP_TIME="${3:-30s}"

if [ -z "$TARGET_URL" ]; then
    echo "Usage: $0 <target_url> [concurrent_users] [ramp_up_time]"
    exit 1
fi

echo "=== Starting Performance Load Test ==="
echo "Target: $TARGET_URL"
echo "Concurrent Users: $CONCURRENT_USERS"
echo "Duration: $LOAD_TEST_DURATION"
echo "Ramp-up: $RAMP_UP_TIME"

# Start resource monitoring
python3 -c "
import sys
sys.path.append('.')
from performance_diagnosis import resource_monitor
resource_monitor.start_monitoring()
print('Resource monitoring started')
" &
MONITOR_PID=$!

# Run load test with wrk
echo "Running load test..."
wrk -t12 -c$CONCURRENT_USERS -d$LOAD_TEST_DURATION \
    --timeout 30s \
    --latency \
    -s load_test_script.lua \
    $TARGET_URL > load_test_results.txt

# Collect additional metrics during load test
echo "Collecting performance metrics..."

# Database performance
python3 -c "
from performance_diagnosis import db_analyzer
report = db_analyzer.get_slow_query_report()
print('Database Performance:', report)
" > db_performance_report.json

# Application performance
curl -s http://localhost:8080/metrics/performance > app_performance.json

# Network diagnostics
python3 -c "
import asyncio
from performance_diagnosis import network_diagnostics
async def run():
    results = await network_diagnostics.diagnose_service_performance()
    print('Network Performance:', results)
asyncio.run(run())
" > network_performance.json

# Stop monitoring and get resource report
kill $MONITOR_PID 2>/dev/null

python3 -c "
from performance_diagnosis import resource_monitor
resource_monitor.stop_monitoring()
analysis = resource_monitor.get_resource_analysis(time_window_minutes=10)
print('Resource Analysis:', analysis)
" > resource_analysis.json

echo "=== Load Test Complete ==="
echo "Results saved to:"
echo "- load_test_results.txt"
echo "- db_performance_report.json"
echo "- app_performance.json"
echo "- network_performance.json"
echo "- resource_analysis.json"

# Generate summary report
python3 -c "
import json
import re

# Parse load test results
with open('load_test_results.txt', 'r') as f:
    load_results = f.read()

# Extract key metrics
latency_match = re.search(r'Latency\s+(\d+\.\d+ms)\s+(\d+\.\d+ms)\s+(\d+\.\d+ms)\s+(\d+\.\d+%)', load_results)
requests_match = re.search(r'(\d+) requests in', load_results)
transfer_match = re.search(r'(\d+\.\d+MB) read', load_results)

summary = {
    'load_test': {
        'requests_total': requests_match.group(1) if requests_match else 'N/A',
        'data_transferred': transfer_match.group(1) if transfer_match else 'N/A'
    }
}

if latency_match:
    summary['load_test']['latency'] = {
        'avg': latency_match.group(1),
        'stdev': latency_match.group(2),
        'max': latency_match.group(3)
    }

print('Load Test Summary:')
print(json.dumps(summary, indent=2))
"
```

## Performance Optimization Strategies

### 1. Database Query Optimization

```sql
-- Performance optimization queries

-- Identify slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
WHERE mean_time > 100  -- queries averaging more than 100ms
ORDER BY mean_time DESC
LIMIT 20;

-- Find missing indexes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND n_distinct > 100
  AND correlation < 0.1;

-- Analyze table sizes and bloat
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_stat_get_tuples_returned(c.oid) as tuples_returned,
    pg_stat_get_tuples_fetched(c.oid) as tuples_fetched
FROM pg_tables pt
JOIN pg_class c ON c.relname = pt.tablename
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 2. Application-Level Optimizations

```python
# Caching strategies
import redis
import pickle
from functools import wraps
import asyncio

class PerformanceCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.hit_count = 0
        self.miss_count = 0
    
    def cached(self, ttl_seconds: int = 300, key_prefix: str = ""):
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                try:
                    cached_result = await self.redis.get(cache_key)
                    if cached_result:
                        self.hit_count += 1
                        return pickle.loads(cached_result)
                except Exception as e:
                    pass  # Cache miss or error
                
                # Cache miss - execute function
                self.miss_count += 1
                result = await func(*args, **kwargs)
                
                # Store in cache
                try:
                    await self.redis.setex(
                        cache_key,
                        ttl_seconds,
                        pickle.dumps(result)
                    )
                except Exception as e:
                    pass  # Cache storage error
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                try:
                    cached_result = self.redis.get(cache_key)
                    if cached_result:
                        self.hit_count += 1
                        return pickle.loads(cached_result)
                except Exception:
                    pass
                
                self.miss_count += 1
                result = func(*args, **kwargs)
                
                try:
                    self.redis.setex(cache_key, ttl_seconds, pickle.dumps(result))
                except Exception:
                    pass
                
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def get_cache_stats(self):
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate
        }

# Connection pooling optimization
import asyncpg
import asyncio

class OptimizedConnectionPool:
    def __init__(self, database_url: str, min_size: int = 5, max_size: int = 20):
        self.database_url = database_url
        self.min_size = min_size
        self.max_size = max_size
        self.pool = None
        self.pool_stats = {
            'created_connections': 0,
            'active_connections': 0,
            'total_queries': 0,
            'failed_queries': 0
        }
    
    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=self.min_size,
            max_size=self.max_size,
            command_timeout=60
        )
    
    async def execute_query(self, query: str, *args):
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as connection:
                self.pool_stats['active_connections'] += 1
                result = await connection.fetch(query, *args)
                self.pool_stats['total_queries'] += 1
                return result
        except Exception as e:
            self.pool_stats['failed_queries'] += 1
            raise
        finally:
            self.pool_stats['active_connections'] -= 1
            execution_time = time.time() - start_time
            
            # Log slow queries
            if execution_time > 1.0:
                print(f"Slow query detected: {query[:100]}... took {execution_time:.2f}s")
    
    def get_pool_stats(self):
        return self.pool_stats
```

## Troubleshooting Checklist

### Performance Investigation Steps
- [ ] **Establish Baseline**: Measure current performance metrics
- [ ] **Identify Bottlenecks**: Use APM tools to find slow operations
- [ ] **Analyze Resource Usage**: Check CPU, memory, disk, network utilization
- [ ] **Examine Database Performance**: Look for slow queries and missing indexes
- [ ] **Review Network Latency**: Measure service-to-service communication
- [ ] **Check Cache Effectiveness**: Analyze cache hit rates
- [ ] **Validate Load Balancing**: Ensure traffic distribution is even
- [ ] **Monitor Queue Depths**: Check for message queue backlogs

### Common Performance Issues and Solutions

| Issue | Symptoms | Solutions |
|-------|----------|-----------|
| **Database Bottleneck** | High query latency, connection pool exhaustion | Query optimization, indexing, read replicas |
| **Memory Leaks** | Increasing memory usage over time | Profile memory allocation, fix object lifecycle |
| **CPU Intensive Operations** | High CPU utilization, slow response times | Algorithm optimization, asynchronous processing |
| **Network Latency** | Variable response times, timeouts | Connection pooling, circuit breakers, caching |
| **Cache Inefficiency** | Low cache hit rates, redundant computations | Cache warming, TTL optimization, cache partitioning |
| **Inefficient Serialization** | High CPU during JSON processing | Use faster serializers, reduce payload size |

## Conclusion

Performance diagnosis in distributed systems requires systematic approaches combining multiple monitoring techniques. The key is to establish comprehensive observability, use data-driven analysis, and implement targeted optimizations based on evidence rather than assumptions.

Regular performance monitoring and proactive optimization help prevent issues before they impact users. Build performance considerations into your development lifecycle and maintain performance budgets for critical operations.
---
title: Chunking
description: Break large datasets or operations into smaller, manageable pieces for improved performance, memory usage, and fault tolerance
type: pattern
category: performance
difficulty: intermediate
reading_time: 30 min
prerequisites: [streaming, batching, memory-management]
when_to_use: Large data processing, file uploads/downloads, streaming data, memory-constrained environments
when_not_to_use: Small datasets, atomic operations requiring full consistency, real-time processing with strict latency requirements
status: complete
last_updated: 2025-07-24
---

# Chunking


## Overview

Chunking divides large datasets, files, or operations into smaller, manageable pieces that can be processed independently. This pattern improves memory efficiency, enables parallel processing, provides fault tolerance, and creates better user experiences through progressive loading and processing.

<div class="axiom-box">
<strong>Axiom 2: Finite Capacity</strong>: Systems have limited memory, bandwidth, and processing power. Chunking allows systems to handle arbitrarily large data by processing it in bounded segments that fit within system constraints.
</div>

## The Large Data Problem

Processing large datasets in memory leads to resource exhaustion:

```python
# ❌ Processing entire dataset in memory
def process_large_file_bad(filename):
    with open(filename, 'r') as f:
        entire_file = f.read()  # Could be GBs - memory explosion!
        
    lines = entire_file.split('\n')
    processed_data = []
    
    for line in lines:
        result = expensive_processing(line)
        processed_data.append(result)
    
    return processed_data  # Doubles memory usage!

# Problems:
# 1. Memory usage grows linearly with file size
# 2. No progress indication for users
# 3. All work lost if process crashes
# 4. Can't start processing until entire file is loaded
```

**Chunking Requirements**:
- **Bounded Memory**: Constant memory usage regardless of data size
- **Fault Tolerance**: Resume processing from failure points
- **Progress Tracking**: Show completion status to users
- **Parallel Processing**: Process chunks concurrently
- **Early Results**: Start delivering results before completion

## Core Implementation

### File Processing Chunking

```python
import io
import os
import asyncio
import hashlib
from typing import Iterator, Optional, Callable, Any, List
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class ChunkMetadata:
    chunk_id: str
    size: int
    offset: int
    checksum: str
    processed: bool = False
    
class FileChunker:
    """Process large files in memory-efficient chunks"""
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB chunks
        self.chunk_size = chunk_size
        self.processed_chunks = set()
        
    def chunk_file(self, filename: str) -> Iterator[tuple[bytes, ChunkMetadata]]:
        """Generate file chunks with metadata"""
        
        file_size = os.path.getsize(filename)
        
        with open(filename, 'rb') as f:
            offset = 0
            chunk_id = 0
            
            while offset < file_size:
# Read chunk
                chunk_data = f.read(self.chunk_size)
                if not chunk_data:
                    break
                
# Generate metadata
                checksum = hashlib.md5(chunk_data).hexdigest()
                metadata = ChunkMetadata(
                    chunk_id=f"chunk_{chunk_id:06d}",
                    size=len(chunk_data),
                    offset=offset,
                    checksum=checksum
                )
                
                yield chunk_data, metadata
                
                offset += len(chunk_data)
                chunk_id += 1
    
    def process_file_chunked(self, filename: str, 
                           processor: Callable[[bytes], Any],
                           progress_callback: Optional[Callable] = None) -> List[Any]:
        """Process file in chunks with progress tracking"""
        
        results = []
        file_size = os.path.getsize(filename)
        bytes_processed = 0
        
        for chunk_data, metadata in self.chunk_file(filename):
            try:
# Process chunk
                result = processor(chunk_data)
                results.append({
                    'chunk_id': metadata.chunk_id,
                    'result': result,
                    'metadata': metadata
                })
                
# Mark as processed
                self.processed_chunks.add(metadata.chunk_id)
                metadata.processed = True
                
# Update progress
                bytes_processed += metadata.size
                progress = (bytes_processed / file_size) * 100
                
                if progress_callback:
                    progress_callback(progress, metadata.chunk_id, bytes_processed, file_size)
                    
            except Exception as e:
                print(f"Failed to process chunk {metadata.chunk_id}: {e}")
# Continue with other chunks instead of failing entirely
                
        return results
    
    async def process_file_async(self, filename: str,
                               processor: Callable[[bytes], Any],
                               max_workers: int = 4,
                               progress_callback: Optional[Callable] = None) -> List[Any]:
        """Process file chunks asynchronously"""
        
        file_size = os.path.getsize(filename)
        bytes_processed = 0
        results = []
        
# Prepare chunks
        chunks = list(self.chunk_file(filename))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
# Submit all chunks for processing
            future_to_chunk = {
                executor.submit(processor, chunk_data): (chunk_data, metadata)
                for chunk_data, metadata in chunks
            }
            
# Process completed chunks
            for future in as_completed(future_to_chunk):
                chunk_data, metadata = future_to_chunk[future]
                
                try:
                    result = future.result()
                    results.append({
                        'chunk_id': metadata.chunk_id,
                        'result': result,
                        'metadata': metadata
                    })
                    
                    self.processed_chunks.add(metadata.chunk_id)
                    bytes_processed += metadata.size
                    
# Update progress
                    progress = (bytes_processed / file_size) * 100
                    if progress_callback:
                        progress_callback(progress, metadata.chunk_id, bytes_processed, file_size)
                        
                except Exception as e:
                    print(f"Failed to process chunk {metadata.chunk_id}: {e}")
        
# Sort results by chunk order
        results.sort(key=lambda x: x['chunk_id'])
        return results

# Usage example
def process_chunk(chunk_data: bytes) -> dict:
    """Example chunk processor - count lines and characters"""
    
# Simulate expensive processing
    import time
    time.sleep(0.1)
    
    text = chunk_data.decode('utf-8', errors='ignore')
    return {
        'lines': text.count('\n'),
        'chars': len(text),
        'words': len(text.split())
    }

def progress_callback(progress: float, chunk_id: str, bytes_done: int, total_bytes: int):
    """Progress callback for user feedback"""
    print(f"Progress: {progress:.1f}% - Processed {chunk_id} ({bytes_done}/{total_bytes} bytes)")

# Process large file
chunker = FileChunker(chunk_size=64*1024)  # 64KB chunks
results = chunker.process_file_chunked(
    'large_file.txt',
    process_chunk,
    progress_callback
)

print(f"Processed {len(results)} chunks")
print(f"Total lines: {sum(r['result']['lines'] for r in results)}")
print(f"Total words: {sum(r['result']['words'] for r in results)}")
```

### Stream Processing Chunking

```python
import asyncio
from collections import deque
from typing import AsyncIterator, List, Optional

class StreamChunker:
    """Process streaming data in fixed-size chunks"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 0):
        self.chunk_size = chunk_size
        self.overlap = overlap  # For sliding window processing
        self.buffer = deque()
        
    async def chunk_stream(self, stream: AsyncIterator) -> AsyncIterator[List]:
        """Convert stream into chunks"""
        
        chunk = []
        
        async for item in stream:
            chunk.append(item)
            
            if len(chunk) >= self.chunk_size:
# Yield complete chunk
                yield chunk.copy()
                
# Handle overlap for sliding window
                if self.overlap > 0:
                    chunk = chunk[-self.overlap:]
                else:
                    chunk = []
        
# Yield final partial chunk if any
        if chunk:
            yield chunk
    
    async def process_stream_chunked(self, 
                                   stream: AsyncIterator,
                                   processor: Callable[[List], Any]) -> AsyncIterator[Any]:
        """Process stream in chunks"""
        
        async for chunk in self.chunk_stream(stream):
            try:
                result = await processor(chunk) if asyncio.iscoroutinefunction(processor) else processor(chunk)
                yield result
            except Exception as e:
                print(f"Error processing chunk: {e}")
# Continue with next chunk

# Example: Time-series data processing
async def data_stream():
    """Simulate streaming time-series data"""
    for i in range(10000):
        yield {
            'timestamp': i,
            'value': i * 0.1 + (i % 100) * 0.01,
            'sensor_id': f'sensor_{i % 10}'
        }
        await asyncio.sleep(0.001)  # Simulate real-time data

async def process_timeseries_chunk(chunk: List[dict]) -> dict:
    """Process chunk of time-series data"""
    
    if not chunk:
        return {}
    
    values = [item['value'] for item in chunk]
    
    return {
        'chunk_size': len(chunk),
        'avg_value': sum(values) / len(values),
        'min_value': min(values),
        'max_value': max(values),
        'timestamp_range': (chunk[0]['timestamp'], chunk[-1]['timestamp'])
    }

# Process streaming data
async def process_realtime_data():
    chunker = StreamChunker(chunk_size=100, overlap=10)  # 10% overlap
    
    async for result in chunker.process_stream_chunked(data_stream(), process_timeseries_chunk):
        print(f"Processed chunk: avg={result['avg_value']:.2f}, range={result['timestamp_range']}")

# asyncio.run(process_realtime_data())
```

### Database Query Chunking

```python
import sqlite3
from typing import Generator, Any, List, Optional

class DatabaseChunker:
    """Process large database queries in chunks"""
    
    def __init__(self, db_path: str, chunk_size: int = 1000):
        self.db_path = db_path
        self.chunk_size = chunk_size
        
    def chunk_query(self, query: str, params: tuple = ()) -> Generator[List[Any], None, None]:
        """Execute query in chunks using LIMIT/OFFSET"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            offset = 0
            
            while True:
# Add LIMIT/OFFSET to query
                chunked_query = f"{query} LIMIT {self.chunk_size} OFFSET {offset}"
                
                cursor.execute(chunked_query, params)
                chunk = cursor.fetchall()
                
                if not chunk:
                    break
                    
                yield chunk
                offset += self.chunk_size
                
        finally:
            conn.close()
    
    def chunk_query_keyset(self, table: str, key_column: str, 
                          where_clause: str = "", params: tuple = (),
                          order_by: str = "ASC") -> Generator[List[Any], None, None]:
        """More efficient keyset pagination for large datasets"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            last_key = None
            
            while True:
# Build query with keyset pagination
                if last_key is None:
                    if where_clause:
                        query = f"SELECT * FROM {table} WHERE {where_clause} ORDER BY {key_column} {order_by} LIMIT {self.chunk_size}"
                    else:
                        query = f"SELECT * FROM {table} ORDER BY {key_column} {order_by} LIMIT {self.chunk_size}"
                    query_params = params
                else:
                    operator = ">" if order_by == "ASC" else "<"
                    if where_clause:
                        query = f"SELECT * FROM {table} WHERE {where_clause} AND {key_column} {operator} ? ORDER BY {key_column} {order_by} LIMIT {self.chunk_size}"
                        query_params = params + (last_key,)
                    else:
                        query = f"SELECT * FROM {table} WHERE {key_column} {operator} ? ORDER BY {key_column} {order_by} LIMIT {self.chunk_size}"
                        query_params = (last_key,)
                
                cursor.execute(query, query_params)
                chunk = cursor.fetchall()
                
                if not chunk:
                    break
                
                yield chunk
                
# Update last_key for next iteration
                last_key = chunk[-1][0]  # Assuming key_column is first column
                
        finally:
            conn.close()
    
    def process_table_chunked(self, table: str, 
                            processor: Callable[[List], Any],
                            key_column: str = "id",
                            progress_callback: Optional[Callable] = None) -> List[Any]:
        """Process entire table in chunks"""
        
        results = []
        total_processed = 0
        
# Get total count for progress tracking
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total_count = cursor.fetchone()[0]
        conn.close()
        
        for chunk in self.chunk_query_keyset(table, key_column):
            try:
                result = processor(chunk)
                results.append(result)
                
                total_processed += len(chunk)
                
                if progress_callback:
                    progress = (total_processed / total_count) * 100
                    progress_callback(progress, len(chunk), total_processed, total_count)
                    
            except Exception as e:
                print(f"Error processing chunk: {e}")
        
        return results

# Example usage
def process_users_chunk(chunk: List[tuple]) -> dict:
    """Process chunk of user records"""
    
    active_users = sum(1 for user in chunk if user[3])  # Assuming column 3 is 'active'
    
    return {
        'chunk_size': len(chunk),
        'active_users': active_users,
        'inactive_users': len(chunk) - active_users
    }

db_chunker = DatabaseChunker('users.db', chunk_size=5000)
results = db_chunker.process_table_chunked(
    'users',
    process_users_chunk,
    progress_callback=lambda p, c, done, total: print(f"Progress: {p:.1f}% ({done}/{total})")
)

print(f"Total active users: {sum(r['active_users'] for r in results)}")
```

## Advanced Chunking Strategies

### Adaptive Chunking

```python
import time
import statistics
from typing import List, Callable

class AdaptiveChunker:
    """Automatically adjust chunk size based on processing time"""
    
    def __init__(self, initial_chunk_size: int = 1000, 
                 target_time: float = 1.0,  # Target 1 second per chunk
                 min_chunk_size: int = 100,
                 max_chunk_size: int = 10000):
        self.chunk_size = initial_chunk_size
        self.target_time = target_time
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.processing_times = []
        
    def adjust_chunk_size(self, processing_time: float):
        """Adjust chunk size based on processing time"""
        
        self.processing_times.append(processing_time)
        
# Keep only recent measurements
        if len(self.processing_times) > 10:
            self.processing_times = self.processing_times[-10:]
        
# Calculate average processing time
        avg_time = statistics.mean(self.processing_times)
        
# Adjust chunk size
        if avg_time > self.target_time * 1.2:  # Too slow
            self.chunk_size = max(self.min_chunk_size, int(self.chunk_size * 0.8))
        elif avg_time < self.target_time * 0.8:  # Too fast
            self.chunk_size = min(self.max_chunk_size, int(self.chunk_size * 1.2))
            
        print(f"Adjusted chunk size to {self.chunk_size} (avg time: {avg_time:.2f}s)")
    
    def process_adaptive(self, data: List, processor: Callable) -> List:
        """Process data with adaptive chunking"""
        
        results = []
        i = 0
        
        while i < len(data):
            chunk = data[i:i + self.chunk_size]
            
            start_time = time.time()
            result = processor(chunk)
            processing_time = time.time() - start_time
            
            results.append(result)
            self.adjust_chunk_size(processing_time)
            
            i += self.chunk_size
        
        return results

# Example: Processing time varies with data complexity
def variable_complexity_processor(chunk: List[int]) -> dict:
    """Simulate processor with variable complexity"""
    
# Simulate complex processing for large numbers
    total_work = sum(x * 0.001 for x in chunk if x > 5000)
    time.sleep(total_work)  # Simulated work
    
    return {
        'chunk_size': len(chunk),
        'max_value': max(chunk) if chunk else 0,
        'processing_time': total_work
    }

# Test adaptive chunking
import random
test_data = [random.randint(1, 10000) for _ in range(50000)]

adaptive_chunker = AdaptiveChunker(initial_chunk_size=2000, target_time=0.5)
results = adaptive_chunker.process_adaptive(test_data, variable_complexity_processor)

print(f"Final chunk size: {adaptive_chunker.chunk_size}")
print(f"Average processing time: {statistics.mean(adaptive_chunker.processing_times):.2f}s")
```

### Parallel Chunking with Dependencies

```python
import asyncio
from typing import Dict, Set, List, Any
from dataclasses import dataclass, field

@dataclass
class ChunkTask:
    chunk_id: str
    data: Any
    dependencies: Set[str] = field(default_factory=set)
    completed: bool = False
    result: Any = None

class DependencyAwareChunker:
    """Process chunks with dependencies in correct order"""
    
    def __init__(self, max_parallel: int = 4):
        self.max_parallel = max_parallel
        self.tasks: Dict[str, ChunkTask] = {}
        self.completed_tasks: Set[str] = set()
        
    def add_chunk(self, chunk_id: str, data: Any, dependencies: Set[str] = None):
        """Add chunk with optional dependencies"""
        self.tasks[chunk_id] = ChunkTask(
            chunk_id=chunk_id,
            data=data,
            dependencies=dependencies or set()
        )
    
    async def process_with_dependencies(self, processor: Callable) -> Dict[str, Any]:
        """Process chunks respecting dependencies"""
        
        results = {}
        active_tasks = set()
        
        while len(self.completed_tasks) < len(self.tasks):
# Find ready tasks (dependencies satisfied)
            ready_tasks = [
                task for task in self.tasks.values()
                if (not task.completed and 
                    task.dependencies.issubset(self.completed_tasks) and
                    task.chunk_id not in active_tasks)
            ]
            
# Start new tasks up to parallel limit
            while len(active_tasks) < self.max_parallel and ready_tasks:
                task = ready_tasks.pop(0)
                active_tasks.add(task.chunk_id)
                
# Start processing
                asyncio.create_task(self._process_task(task, processor))
            
# Check for completed tasks
            completed_this_round = []
            for task_id in active_tasks:
                task = self.tasks[task_id]
                if task.completed:
                    completed_this_round.append(task_id)
                    results[task_id] = task.result
                    self.completed_tasks.add(task_id)
            
# Remove completed tasks from active set
            for task_id in completed_this_round:
                active_tasks.remove(task_id)
            
# Wait a bit before checking again
            await asyncio.sleep(0.1)
        
        return results
    
    async def _process_task(self, task: ChunkTask, processor: Callable):
        """Process individual task"""
        try:
            if asyncio.iscoroutinefunction(processor):
                result = await processor(task.data)
            else:
                result = processor(task.data)
            
            task.result = result
            task.completed = True
            
        except Exception as e:
            print(f"Error processing task {task.chunk_id}: {e}")
            task.result = None
            task.completed = True

# Example: Processing a dependency chain
async def process_step(data: dict) -> dict:
    """Simulate processing step with variable time"""
    
    processing_time = data.get('complexity', 1) * 0.5
    await asyncio.sleep(processing_time)
    
    return {
        'step': data['step'],
        'result': data['value'] * 2,
        'processing_time': processing_time
    }

async def run_dependency_example():
    chunker = DependencyAwareChunker(max_parallel=3)
    
# Build dependency chain: A -> B -> C, D (independent), E depends on B and D
    chunker.add_chunk('A', {'step': 'A', 'value': 10, 'complexity': 1})
    chunker.add_chunk('B', {'step': 'B', 'value': 20, 'complexity': 2}, {'A'})
    chunker.add_chunk('C', {'step': 'C', 'value': 30, 'complexity': 1}, {'B'})
    chunker.add_chunk('D', {'step': 'D', 'value': 40, 'complexity': 3})  # Independent
    chunker.add_chunk('E', {'step': 'E', 'value': 50, 'complexity': 1}, {'B', 'D'})
    
    print("Starting dependency-aware processing...")
    results = await chunker.process_with_dependencies(process_step)
    
    print("Results:")
    for chunk_id, result in results.items():
        print(f"  {chunk_id}: {result}")

# asyncio.run(run_dependency_example())
```

## Memory-Efficient Chunking

```python
import mmap
import tempfile
from contextlib import contextmanager

class MemoryEfficientChunker:
    """Ultra-low memory chunking using memory mapping"""
    
    def __init__(self, chunk_size: int = 1024 * 1024):
        self.chunk_size = chunk_size
    
    @contextmanager
    def mmap_file(self, filename: str):
        """Memory map file for efficient access"""
        with open(filename, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                yield mm
    
    def process_large_file_mmap(self, filename: str, processor: Callable) -> List[Any]:
        """Process file using memory mapping - O(1) memory"""
        
        results = []
        
        with self.mmap_file(filename) as mm:
            file_size = len(mm)
            
            for offset in range(0, file_size, self.chunk_size):
                end_offset = min(offset + self.chunk_size, file_size)
                chunk_data = mm[offset:end_offset]
                
                try:
                    result = processor(chunk_data)
                    results.append({
                        'offset': offset,
                        'size': len(chunk_data),
                        'result': result
                    })
                except Exception as e:
                    print(f"Error processing chunk at offset {offset}: {e}")
        
        return results
    
    def create_temp_chunked_file(self, large_data: bytes, 
                               processor: Callable) -> str:
        """Process data too large for memory by using temp files"""
        
# Write to temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(large_data)
            temp_filename = temp_file.name
        
        try:
# Process using memory mapping
            results = self.process_large_file_mmap(temp_filename, processor)
            return results
        finally:
# Cleanup
            import os
            os.unlink(temp_filename)

# Example: Processing gigabyte-sized files with constant memory
def count_patterns_in_chunk(chunk_data: bytes) -> dict:
    """Count patterns in chunk"""
    
    text = chunk_data.decode('utf-8', errors='ignore')
    
    return {
        'newlines': text.count('\n'),
        'tabs': text.count('\t'),
        'spaces': text.count(' '),
        'size': len(chunk_data)
    }

# Process 10GB file with only ~1MB memory usage
efficient_chunker = MemoryEfficientChunker(chunk_size=1024*1024)  # 1MB chunks
# results = efficient_chunker.process_large_file_mmap('huge_file.txt', count_patterns_in_chunk)
```

<div class="decision-box">
<strong>Chunking Strategy Selection</strong>:

- **File processing**: Fixed-size chunks with progress tracking
- **Stream processing**: Time-based or count-based chunks
- **Database queries**: Keyset pagination for efficiency
- **Variable complexity**: Adaptive chunking
- **Dependencies**: Dependency-aware parallel processing
- **Memory constraints**: Memory-mapped chunking
</div>

## Performance Considerations

### Chunk Size Optimization

```python
def optimize_chunk_size(data_size: int, memory_limit: int, 
                       processing_overhead: float = 0.1) -> int:
    """Calculate optimal chunk size based on constraints"""
    
# Consider memory limit
    max_chunk_by_memory = int(memory_limit * 0.8)  # Leave 20% buffer
    
# Consider processing overhead (smaller chunks = more overhead)
    min_chunk_for_efficiency = int(data_size * processing_overhead)
    
# Consider parallelism (want multiple chunks for parallel processing)
    import multiprocessing
    cpu_count = multiprocessing.cpu_count()
    chunk_count_target = cpu_count * 4  # 4 chunks per CPU
    chunk_by_parallelism = max(1024, data_size // chunk_count_target)
    
# Choose optimal size
    optimal_size = min(
        max_chunk_by_memory,
        max(min_chunk_for_efficiency, chunk_by_parallelism)
    )
    
    return optimal_size

# Example optimization
data_size = 100 * 1024 * 1024  # 100MB
memory_limit = 16 * 1024 * 1024  # 16MB available
optimal_chunk = optimize_chunk_size(data_size, memory_limit)
print(f"Optimal chunk size: {optimal_chunk // 1024}KB")
```

### Monitoring and Metrics

```python
import time
from collections import defaultdict

class ChunkingMetrics:
    """Track chunking performance metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_times = {}
    
    def start_chunk(self, chunk_id: str):
        self.start_times[chunk_id] = time.time()
    
    def end_chunk(self, chunk_id: str, chunk_size: int, result_size: int = 0):
        if chunk_id in self.start_times:
            duration = time.time() - self.start_times[chunk_id]
            
            self.metrics['processing_times'].append(duration)
            self.metrics['chunk_sizes'].append(chunk_size)
            self.metrics['throughput'].append(chunk_size / duration)
            self.metrics['result_sizes'].append(result_size)
            
            del self.start_times[chunk_id]
    
    def get_stats(self) -> dict:
        """Get performance statistics"""
        
        if not self.metrics['processing_times']:
            return {}
        
        import statistics
        
        return {
            'avg_processing_time': statistics.mean(self.metrics['processing_times']),
            'total_chunks': len(self.metrics['processing_times']),
            'avg_throughput': statistics.mean(self.metrics['throughput']),
            'total_data_processed': sum(self.metrics['chunk_sizes']),
            'efficiency_ratio': sum(self.metrics['result_sizes']) / sum(self.metrics['chunk_sizes'])
        }

# Usage in chunked processor
metrics = ChunkingMetrics()

def monitored_chunk_processor(chunk_data: bytes, chunk_id: str) -> dict:
    metrics.start_chunk(chunk_id)
    
# Process chunk
    result = process_chunk(chunk_data)
    
    metrics.end_chunk(chunk_id, len(chunk_data), len(str(result)))
    return result

# After processing
stats = metrics.get_stats()
print(f"Average processing time: {stats['avg_processing_time']:.3f}s")
print(f"Average throughput: {stats['avg_throughput']:.0f} bytes/s")
```

## Related Patterns
- [Streaming](streaming.md) - Real-time data processing
- [Batching](batching.md) - Grouping operations for efficiency
- [Pagination](pagination.md) - Chunking for user interfaces
- [Load Balancing](load-balancing.md) - Distributing chunked work
- [Circuit Breaker](circuit-breaker.md) - Handling chunk processing failures

## References
- [Stream Processing Fundamentals](https://www.oreilly.com/library/view/stream-processing-with/9781491974285/)
- [Memory-Mapped Files](https://en.wikipedia.org/wiki/Memory-mapped_file)
- [Database Pagination Best Practices](https://use-the-index-luke.com/sql/partial-results/fetch-next-page)
- [Chunked Transfer Encoding](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding)
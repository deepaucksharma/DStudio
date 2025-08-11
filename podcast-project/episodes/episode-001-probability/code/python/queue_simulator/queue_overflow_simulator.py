#!/usr/bin/env python3
"""
Queue Overflow Simulator - Model Queue Behavior Under Load
=========================================================
Simulate queue overflow conditions and backpressure mechanisms for Indian scale systems.

Real-world examples:
- IRCTC Tatkal booking: Queue overflow when 50L+ users hit "Book Now"
- Paytm during IPL match end: Payment queue overflow during surge
- Flipkart flash sale: Order processing queue overflow
- Ola/Uber surge pricing: Ride request queue overflow

Features:
- Queue overflow prediction and modeling
- Backpressure implementation strategies  
- Multiple queue types (FIFO, Priority, Weighted Fair)
- Load balancing across multiple queues
- Performance metrics and alerting
- Indian scale traffic pattern simulation
"""

import random
import time
import threading
import queue
import heapq
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque, defaultdict
import json
import math


class QueueType(Enum):
    """Types of queues to simulate"""
    FIFO = "fifo"                    # First In First Out
    LIFO = "lifo"                    # Last In First Out (Stack)
    PRIORITY = "priority"            # Priority Queue
    WEIGHTED_FAIR = "weighted_fair"  # Weighted Fair Queuing
    ROUND_ROBIN = "round_robin"      # Round Robin
    RATE_LIMITED = "rate_limited"    # Rate Limited Queue


class BackpressureStrategy(Enum):
    """Backpressure handling strategies"""
    DROP_TAIL = "drop_tail"          # Drop new requests when full
    DROP_HEAD = "drop_head"          # Drop oldest requests
    DROP_RANDOM = "drop_random"      # Drop random requests
    REJECT_NEW = "reject_new"        # Reject new requests with error
    QUEUE_EXPANSION = "queue_expansion"  # Dynamically expand queue
    LOAD_SHEDDING = "load_shedding"  # Shed load based on priority


@dataclass
class QueueRequest:
    """Represents a request in the queue"""
    request_id: str
    arrival_time: datetime
    priority: int = 0  # Higher number = higher priority
    processing_time_ms: int = 100  # Expected processing time
    customer_tier: str = "regular"  # regular, premium, vip
    source_service: str = "unknown"
    payload_size_bytes: int = 1024
    
    def __lt__(self, other):
        """For priority queue ordering (higher priority first)"""
        return self.priority > other.priority


@dataclass
class QueueMetrics:
    """Queue performance metrics"""
    queue_name: str
    current_size: int = 0
    max_size_reached: int = 0
    total_requests: int = 0
    processed_requests: int = 0
    dropped_requests: int = 0
    rejected_requests: int = 0
    
    # Timing metrics
    total_wait_time_ms: float = 0.0
    total_processing_time_ms: float = 0.0
    max_wait_time_ms: float = 0.0
    
    # Throughput metrics  
    requests_per_second: float = 0.0
    processing_rate: float = 0.0
    
    # Overflow metrics
    overflow_events: int = 0
    backpressure_activations: int = 0
    
    def get_average_wait_time_ms(self) -> float:
        """Calculate average wait time"""
        if self.processed_requests == 0:
            return 0.0
        return self.total_wait_time_ms / self.processed_requests
    
    def get_drop_rate(self) -> float:
        """Calculate request drop rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.dropped_requests / self.total_requests) * 100


class QueueSimulator:
    """Main queue overflow simulator"""
    
    def __init__(self, queue_type: QueueType, max_size: int = 1000,
                 backpressure_strategy: BackpressureStrategy = BackpressureStrategy.DROP_TAIL):
        self.queue_type = queue_type
        self.max_size = max_size
        self.backpressure_strategy = backpressure_strategy
        
        # Initialize appropriate queue structure
        self.queue = self._create_queue()
        self.metrics = QueueMetrics(f"{queue_type.value}_queue")
        
        # Processing configuration
        self.processing_threads = []
        self.is_processing = False
        self.processing_rate_per_second = 10  # Requests per second
        
        # Backpressure controls
        self.backpressure_threshold = 0.8  # 80% of max size
        self.backpressure_active = False
        
        # Indian scale configuration
        self.peak_traffic_multiplier = 10.0  # Peak vs normal traffic
        self.flash_sale_mode = False
        
    def _create_queue(self) -> Any:
        """Create appropriate queue data structure"""
        if self.queue_type == QueueType.FIFO:
            return deque()
        elif self.queue_type == QueueType.LIFO:
            return []  # Use as stack
        elif self.queue_type == QueueType.PRIORITY:
            return []  # Heapq
        elif self.queue_type == QueueType.WEIGHTED_FAIR:
            return defaultdict(deque)  # Multiple queues by weight
        else:
            return deque()  # Default to FIFO
    
    def enqueue(self, request: QueueRequest) -> bool:
        """Add request to queue with overflow handling"""
        self.metrics.total_requests += 1
        
        # Check for overflow
        if self._is_queue_full():
            return self._handle_overflow(request)
        
        # Add to queue based on type
        if self.queue_type == QueueType.FIFO:
            self.queue.append(request)
        elif self.queue_type == QueueType.LIFO:
            self.queue.append(request)
        elif self.queue_type == QueueType.PRIORITY:
            heapq.heappush(self.queue, request)
        elif self.queue_type == QueueType.WEIGHTED_FAIR:
            # Route to appropriate sub-queue based on customer tier
            weight = self._get_customer_weight(request.customer_tier)
            self.queue[weight].append(request)
        else:
            self.queue.append(request)
        
        # Update metrics
        self._update_size_metrics()
        
        # Check backpressure
        self._check_backpressure()
        
        return True
    
    def dequeue(self) -> Optional[QueueRequest]:
        """Remove and return next request from queue"""
        if self._is_queue_empty():
            return None
        
        # Dequeue based on type
        request = None
        if self.queue_type == QueueType.FIFO:
            request = self.queue.popleft()
        elif self.queue_type == QueueType.LIFO:
            request = self.queue.pop()
        elif self.queue_type == QueueType.PRIORITY:
            request = heapq.heappop(self.queue)
        elif self.queue_type == QueueType.WEIGHTED_FAIR:
            request = self._weighted_fair_dequeue()
        else:
            request = self.queue.popleft()
        
        if request:
            # Calculate wait time
            wait_time_ms = (datetime.now() - request.arrival_time).total_seconds() * 1000
            self.metrics.total_wait_time_ms += wait_time_ms
            self.metrics.max_wait_time_ms = max(self.metrics.max_wait_time_ms, wait_time_ms)
            
            self._update_size_metrics()
        
        return request
    
    def _is_queue_full(self) -> bool:
        """Check if queue is at capacity"""
        current_size = self._get_current_size()
        return current_size >= self.max_size
    
    def _is_queue_empty(self) -> bool:
        """Check if queue is empty"""
        return self._get_current_size() == 0
    
    def _get_current_size(self) -> int:
        """Get current queue size"""
        if self.queue_type == QueueType.WEIGHTED_FAIR:
            return sum(len(q) for q in self.queue.values())
        else:
            return len(self.queue)
    
    def _handle_overflow(self, request: QueueRequest) -> bool:
        """Handle queue overflow based on strategy"""
        self.metrics.overflow_events += 1
        
        if self.backpressure_strategy == BackpressureStrategy.DROP_TAIL:
            # Drop new request
            self.metrics.dropped_requests += 1
            return False
            
        elif self.backpressure_strategy == BackpressureStrategy.DROP_HEAD:
            # Drop oldest request and add new one
            if not self._is_queue_empty():
                dropped = self.dequeue()
                if dropped:
                    self.metrics.dropped_requests += 1
            return self.enqueue(request)
            
        elif self.backpressure_strategy == BackpressureStrategy.DROP_RANDOM:
            # Drop random request
            self._drop_random_request()
            return self.enqueue(request)
            
        elif self.backpressure_strategy == BackpressureStrategy.REJECT_NEW:
            # Reject with explicit error
            self.metrics.rejected_requests += 1
            return False
            
        elif self.backpressure_strategy == BackpressureStrategy.QUEUE_EXPANSION:
            # Temporarily expand queue (dangerous!)
            self.max_size = int(self.max_size * 1.2)  # 20% expansion
            return self.enqueue(request)
            
        elif self.backpressure_strategy == BackpressureStrategy.LOAD_SHEDDING:
            # Drop lower priority requests
            return self._shed_load_and_enqueue(request)
        
        return False
    
    def _drop_random_request(self):
        """Drop a random request from queue"""
        if self._is_queue_empty():
            return
        
        if self.queue_type == QueueType.FIFO:
            # Convert to list, remove random, convert back
            items = list(self.queue)
            if items:
                removed = items.pop(random.randint(0, len(items) - 1))
                self.queue = deque(items)
                self.metrics.dropped_requests += 1
    
    def _shed_load_and_enqueue(self, new_request: QueueRequest) -> bool:
        """Shed lower priority load and add new request"""
        if self.queue_type == QueueType.PRIORITY:
            # Find lowest priority request
            if self.queue:
                # Convert heap to list to find minimum
                items = list(self.queue)
                min_priority_req = min(items, key=lambda x: x.priority)
                
                if new_request.priority > min_priority_req.priority:
                    # Remove low priority request
                    items.remove(min_priority_req)
                    self.queue = items
                    heapq.heapify(self.queue)
                    self.metrics.dropped_requests += 1
                    
                    # Add new higher priority request
                    heapq.heappush(self.queue, new_request)
                    return True
        
        return False
    
    def _weighted_fair_dequeue(self) -> Optional[QueueRequest]:
        """Weighted fair queuing dequeue logic"""
        # Simple weighted round-robin
        weights = sorted(self.queue.keys(), reverse=True)  # Higher weight first
        
        for weight in weights:
            if self.queue[weight]:
                return self.queue[weight].popleft()
        
        return None
    
    def _get_customer_weight(self, customer_tier: str) -> int:
        """Get weight based on customer tier"""
        weights = {
            "vip": 10,
            "premium": 5,
            "regular": 1
        }
        return weights.get(customer_tier, 1)
    
    def _update_size_metrics(self):
        """Update size-related metrics"""
        current_size = self._get_current_size()
        self.metrics.current_size = current_size
        self.metrics.max_size_reached = max(self.metrics.max_size_reached, current_size)
    
    def _check_backpressure(self):
        """Check and activate backpressure if needed"""
        utilization = self.metrics.current_size / self.max_size
        
        if utilization >= self.backpressure_threshold and not self.backpressure_active:
            self.backpressure_active = True
            self.metrics.backpressure_activations += 1
            print(f"🔥 Backpressure activated - Queue {utilization*100:.1f}% full")
        
        elif utilization < (self.backpressure_threshold - 0.1) and self.backpressure_active:
            self.backpressure_active = False
            print(f"✅ Backpressure deactivated - Queue {utilization*100:.1f}% full")
    
    def start_processing(self, num_threads: int = 3):
        """Start processing threads"""
        if self.is_processing:
            return
        
        self.is_processing = True
        print(f"🚀 Starting {num_threads} processing threads")
        
        for i in range(num_threads):
            thread = threading.Thread(target=self._process_requests, args=(i,))
            thread.daemon = True
            thread.start()
            self.processing_threads.append(thread)
    
    def stop_processing(self):
        """Stop processing threads"""
        self.is_processing = False
        print("⏹️  Stopping processing threads")
    
    def _process_requests(self, thread_id: int):
        """Process requests from queue"""
        while self.is_processing:
            request = self.dequeue()
            
            if request:
                # Simulate processing time
                processing_start = time.time()
                time.sleep(request.processing_time_ms / 1000.0)  # Convert to seconds
                processing_time = (time.time() - processing_start) * 1000  # Convert back to ms
                
                # Update metrics
                self.metrics.processed_requests += 1
                self.metrics.total_processing_time_ms += processing_time
                
                # Optional: Log processing
                # print(f"Thread {thread_id}: Processed {request.request_id}")
            else:
                # No requests to process, sleep briefly
                time.sleep(1.0 / self.processing_rate_per_second)
    
    def simulate_traffic_load(self, duration_seconds: int = 60, base_rps: float = 5.0):
        """Simulate realistic traffic load"""
        print(f"📈 Simulating traffic for {duration_seconds}s at {base_rps} base RPS")
        
        start_time = time.time()
        request_counter = 0
        
        while time.time() - start_time < duration_seconds:
            # Calculate current load (simulate traffic patterns)
            elapsed_ratio = (time.time() - start_time) / duration_seconds
            
            # Simulate Indian traffic patterns
            current_rps = self._calculate_indian_traffic_pattern(base_rps, elapsed_ratio)
            
            # Generate requests
            inter_request_delay = 1.0 / current_rps
            
            # Create request
            request = QueueRequest(
                request_id=f"REQ-{request_counter:06d}",
                arrival_time=datetime.now(),
                priority=random.randint(1, 10),
                processing_time_ms=random.randint(50, 500),
                customer_tier=random.choice(["regular", "regular", "regular", "premium", "vip"]),
                source_service=random.choice(["web", "mobile", "api", "partner"]),
                payload_size_bytes=random.randint(512, 4096)
            )
            
            # Enqueue request
            success = self.enqueue(request)
            if not success:
                print(f"⚠️  Request {request.request_id} failed to enqueue")
            
            request_counter += 1
            time.sleep(inter_request_delay)
        
        print(f"✅ Traffic simulation completed: {request_counter} requests generated")
    
    def _calculate_indian_traffic_pattern(self, base_rps: float, elapsed_ratio: float) -> float:
        """Calculate realistic Indian traffic patterns"""
        
        # Flash sale pattern (exponential growth then decay)
        if self.flash_sale_mode:
            if elapsed_ratio < 0.1:  # First 10% - explosive growth
                multiplier = 1 + (self.peak_traffic_multiplier - 1) * (elapsed_ratio / 0.1)
            elif elapsed_ratio < 0.3:  # Next 20% - peak sustained
                multiplier = self.peak_traffic_multiplier
            else:  # Remaining 70% - exponential decay
                decay_progress = (elapsed_ratio - 0.3) / 0.7
                multiplier = self.peak_traffic_multiplier * math.exp(-3 * decay_progress)
        else:
            # Normal daily pattern - sine wave with random spikes
            daily_cycle = 1 + 0.5 * math.sin(2 * math.pi * elapsed_ratio)  # Daily traffic cycle
            random_spikes = 1 + 0.3 * random.random() if random.random() < 0.1 else 1  # 10% chance of spike
            multiplier = daily_cycle * random_spikes
        
        return base_rps * multiplier
    
    def get_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        
        # Calculate derived metrics
        if self.metrics.processed_requests > 0:
            avg_processing_time = self.metrics.total_processing_time_ms / self.metrics.processed_requests
        else:
            avg_processing_time = 0.0
        
        utilization = (self.metrics.current_size / self.max_size) * 100
        
        report = f"""
📊 QUEUE PERFORMANCE REPORT
{'='*40}

Queue Configuration:
  Type: {self.queue_type.value}
  Max Size: {self.max_size:,}
  Backpressure Strategy: {self.backpressure_strategy.value}
  Backpressure Threshold: {self.backpressure_threshold*100:.1f}%

Current Status:
  Queue Size: {self.metrics.current_size:,}
  Utilization: {utilization:.1f}%
  Backpressure Active: {'Yes' if self.backpressure_active else 'No'}

Request Metrics:
  Total Requests: {self.metrics.total_requests:,}
  Processed: {self.metrics.processed_requests:,}
  Dropped: {self.metrics.dropped_requests:,}
  Rejected: {self.metrics.rejected_requests:,}
  Drop Rate: {self.metrics.get_drop_rate():.2f}%

Performance Metrics:
  Average Wait Time: {self.metrics.get_average_wait_time_ms():.1f}ms
  Max Wait Time: {self.metrics.max_wait_time_ms:.1f}ms
  Average Processing Time: {avg_processing_time:.1f}ms
  Max Queue Size Reached: {self.metrics.max_size_reached:,}

Overflow Events:
  Total Overflows: {self.metrics.overflow_events:,}
  Backpressure Activations: {self.metrics.backpressure_activations:,}

💡 Performance Assessment:
"""
        
        # Performance assessment
        if self.metrics.get_drop_rate() > 5:
            report += "  🚨 HIGH DROP RATE - Consider increasing queue size or processing capacity\n"
        elif self.metrics.get_drop_rate() > 1:
            report += "  ⚠️  MODERATE DROP RATE - Monitor and optimize\n"
        else:
            report += "  ✅ LOW DROP RATE - Good performance\n"
        
        if self.metrics.get_average_wait_time_ms() > 5000:
            report += "  🚨 HIGH WAIT TIME - Queue processing too slow\n"
        elif self.metrics.get_average_wait_time_ms() > 1000:
            report += "  ⚠️  MODERATE WAIT TIME - Room for improvement\n"
        else:
            report += "  ✅ LOW WAIT TIME - Good responsiveness\n"
        
        if utilization > 90:
            report += "  🚨 HIGH UTILIZATION - Risk of overflow\n"
        elif utilization > 70:
            report += "  ⚠️  MODERATE UTILIZATION - Monitor closely\n"
        else:
            report += "  ✅ LOW UTILIZATION - Good capacity headroom\n"
        
        return report


def simulate_indian_platform_scenarios():
    """Simulate realistic Indian platform queue scenarios"""
    
    scenarios = []
    
    # 1. IRCTC Tatkal Booking Queue
    print("\n🚂 SCENARIO 1: IRCTC TATKAL BOOKING QUEUE")
    print("-" * 45)
    
    irctc_queue = QueueSimulator(
        queue_type=QueueType.PRIORITY,
        max_size=50000,  # 50k concurrent requests
        backpressure_strategy=BackpressureStrategy.LOAD_SHEDDING
    )
    irctc_queue.flash_sale_mode = True
    irctc_queue.peak_traffic_multiplier = 50.0  # 50x normal traffic
    
    irctc_queue.start_processing(num_threads=5)
    irctc_queue.simulate_traffic_load(duration_seconds=30, base_rps=100.0)
    irctc_queue.stop_processing()
    
    scenarios.append(("IRCTC_Tatkal", irctc_queue))
    
    # 2. Paytm Payment Processing Queue
    print("\n💳 SCENARIO 2: PAYTM PAYMENT PROCESSING")
    print("-" * 42)
    
    paytm_queue = QueueSimulator(
        queue_type=QueueType.WEIGHTED_FAIR,
        max_size=20000,
        backpressure_strategy=BackpressureStrategy.DROP_TAIL
    )
    paytm_queue.processing_rate_per_second = 50
    
    paytm_queue.start_processing(num_threads=8)
    paytm_queue.simulate_traffic_load(duration_seconds=25, base_rps=80.0)
    paytm_queue.stop_processing()
    
    scenarios.append(("Paytm_Payments", paytm_queue))
    
    # 3. Flipkart Order Processing
    print("\n📦 SCENARIO 3: FLIPKART ORDER PROCESSING")
    print("-" * 42)
    
    flipkart_queue = QueueSimulator(
        queue_type=QueueType.FIFO,
        max_size=30000,
        backpressure_strategy=BackpressureStrategy.QUEUE_EXPANSION
    )
    flipkart_queue.flash_sale_mode = True
    flipkart_queue.peak_traffic_multiplier = 20.0
    
    flipkart_queue.start_processing(num_threads=6)
    flipkart_queue.simulate_traffic_load(duration_seconds=35, base_rps=60.0)
    flipkart_queue.stop_processing()
    
    scenarios.append(("Flipkart_Orders", flipkart_queue))
    
    return scenarios


def demo_queue_overflow_simulator():
    """Demonstrate queue overflow simulator"""
    
    print("📊 QUEUE OVERFLOW SIMULATOR - INDIAN PLATFORM EDITION")
    print("=" * 60)
    
    # Run multiple scenarios
    scenarios = simulate_indian_platform_scenarios()
    
    # Generate reports for each scenario
    results = {}
    total_requests_processed = 0
    total_requests_dropped = 0
    
    for scenario_name, queue_sim in scenarios:
        print(f"\n📈 REPORT: {scenario_name}")
        print("=" * 50)
        
        report = queue_sim.get_performance_report()
        print(report)
        
        # Collect summary metrics
        metrics = queue_sim.metrics
        results[scenario_name] = {
            'queue_type': queue_sim.queue_type.value,
            'max_size': queue_sim.max_size,
            'total_requests': metrics.total_requests,
            'processed_requests': metrics.processed_requests,
            'dropped_requests': metrics.dropped_requests,
            'drop_rate': metrics.get_drop_rate(),
            'avg_wait_time_ms': metrics.get_average_wait_time_ms(),
            'max_queue_size': metrics.max_size_reached,
            'overflow_events': metrics.overflow_events
        }
        
        total_requests_processed += metrics.processed_requests
        total_requests_dropped += metrics.dropped_requests
    
    # Overall summary
    print(f"\n🎯 OVERALL SIMULATION SUMMARY")
    print("=" * 35)
    print(f"Scenarios Tested: {len(scenarios)}")
    print(f"Total Requests Processed: {total_requests_processed:,}")
    print(f"Total Requests Dropped: {total_requests_dropped:,}")
    
    if total_requests_processed + total_requests_dropped > 0:
        overall_success_rate = (total_requests_processed / (total_requests_processed + total_requests_dropped)) * 100
        print(f"Overall Success Rate: {overall_success_rate:.2f}%")
    
    # Best and worst performing scenarios
    if results:
        best_scenario = min(results.items(), key=lambda x: x[1]['drop_rate'])
        worst_scenario = max(results.items(), key=lambda x: x[1]['drop_rate'])
        
        print(f"\n🏆 BEST PERFORMING: {best_scenario[0]} ({best_scenario[1]['drop_rate']:.2f}% drop rate)")
        print(f"🚨 WORST PERFORMING: {worst_scenario[0]} ({worst_scenario[1]['drop_rate']:.2f}% drop rate)")
    
    # Save results
    with open('queue_simulation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to queue_simulation_results.json")
    
    print(f"\n💡 KEY INSIGHTS:")
    print("1. Priority queues handle VIP customers better during overload")
    print("2. Load shedding prevents complete system breakdown")
    print("3. Queue expansion is risky but can handle short spikes")  
    print("4. Backpressure mechanisms are critical for stability")
    print("5. Indian traffic patterns show extreme spikes requiring robust design")
    
    print(f"\n💰 BUSINESS IMPACT:")
    print("- Queue overflow = lost customers and revenue")
    print("- 1% drop rate improvement = ₹10L-1Cr additional revenue/month")
    print("- Proper queue design prevents system crashes during peak events")
    print("- Backpressure mechanisms maintain service quality under load")


if __name__ == "__main__":
    demo_queue_overflow_simulator()
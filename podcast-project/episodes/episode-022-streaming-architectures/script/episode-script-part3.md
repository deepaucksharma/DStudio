# Episode 022: Streaming Architectures & Real-Time Processing - Part 3
## Production Scale aur Enterprise Reality - Mumbai Railway Control Room

*Duration: 60 minutes*
*Language: 70% Hindi/Roman Hindi, 30% Technical English*
*Target: 6,000+ words for Part 3*

---

### Introduction: Railway Control Room Se Production Streaming Control

Welcome back dosto! Part 1 aur Part 2 mein humne fundamentals aur advanced patterns dekhe. Ab Part 3 mein real production challenges handle karenge - error recovery, multi-region deployment, cost optimization, aur enterprise-scale monitoring. Ye Mumbai Railway Control Room ki tarah sophisticated aur critical hai!

Jaise Mumbai Railway Control Room mein har train ka track, signal, aur timing monitor hota hai, waise hi production streaming systems mein har event, partition, aur latency monitor karni padti hai. Ek galti matlab millions of users affected!

### Production Streaming at Scale: Hotstar IPL Case Study

#### Hotstar IPL Streaming: 25.3 Million Concurrent Viewers

2019 mein Hotstar ne world record banaya tha - 25.3 million concurrent viewers during India vs New Zealand World Cup match. Ye Mumbai local train mein peak hour se bhi zyada challenging tha!

**Hotstar Streaming Architecture:**

```python
# Hotstar-style Live Streaming Event Processing System
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import asyncio
import json
import time
from collections import defaultdict
import redis
import boto3

@dataclass
class StreamingEvent:
    """
    Hotstar ke har viewer ka event - Mumbai local mein boarding ki tarah
    """
    event_id: str
    user_id: str
    device_id: str
    session_id: str
    event_type: str  # play, pause, quality_change, buffer, error
    timestamp: float
    quality: str     # 360p, 720p, 1080p, 4K
    location: str    # Mumbai, Delhi, Bangalore
    content_id: str  # IPL match ID
    bitrate: int
    buffer_health: float
    network_type: str  # 4G, 5G, WiFi, broadband

class HotstarStreamingProcessor:
    """
    Production-grade streaming event processor
    25M+ concurrent users handle karne ke liye optimized
    """
    
    def __init__(self):
        # Redis cluster for real-time state
        self.redis_cluster = redis.RedisCluster(
            startup_nodes=[
                {"host": "redis-mumbai-1", "port": 7000},
                {"host": "redis-delhi-1", "port": 7000},
                {"host": "redis-bangalore-1", "port": 7000}
            ]
        )
        
        # AWS Kinesis for event streaming
        self.kinesis_client = boto3.client('kinesis', region_name='ap-south-1')
        
        # Regional processing centers - India ke major cities mein
        self.regional_processors = {
            'mumbai': {'capacity': 8000000, 'current_load': 0},
            'delhi': {'capacity': 6000000, 'current_load': 0},
            'bangalore': {'capacity': 5000000, 'current_load': 0},
            'hyderabad': {'capacity': 3000000, 'current_load': 0},
            'pune': {'capacity': 2500000, 'current_load': 0},
            'kolkata': {'capacity': 2000000, 'current_load': 0}
        }
        
        # Quality adaptation thresholds
        self.quality_thresholds = {
            '4K': {'min_bitrate': 25000, 'min_buffer': 10.0},
            '1080p': {'min_bitrate': 8000, 'min_buffer': 5.0},
            '720p': {'min_bitrate': 3000, 'min_buffer': 3.0},
            '480p': {'min_bitrate': 1500, 'min_buffer': 2.0},
            '360p': {'min_bitrate': 800, 'min_buffer': 1.0}
        }
        
        # Circuit breaker states for different regions
        self.circuit_breakers = defaultdict(lambda: {'state': 'CLOSED', 'failures': 0, 'last_failure': 0})
        
    async def process_streaming_events(self, events: List[StreamingEvent]):
        """
        Mumbai local train ki tarah efficient event processing
        Har event 5ms mein process hona chahiye
        """
        start_time = time.time()
        processed_count = 0
        failed_count = 0
        
        # Regional load balancing - Mumbai mein jyada load to Delhi reroute karo
        balanced_events = await self.balance_regional_load(events)
        
        # Parallel processing by region
        processing_tasks = []
        for region, region_events in balanced_events.items():
            task = asyncio.create_task(
                self.process_regional_events(region, region_events)
            )
            processing_tasks.append(task)
        
        # Wait for all regions to complete
        results = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        # Aggregate results
        for result in results:
            if isinstance(result, Exception):
                failed_count += 1
                await self.handle_regional_failure(result)
            else:
                processed_count += result['processed']
                failed_count += result['failed']
        
        processing_time = (time.time() - start_time) * 1000
        
        # Monitoring metrics - Railway control room dashboard ki tarah
        await self.update_metrics({
            'events_processed': processed_count,
            'events_failed': failed_count,
            'processing_time_ms': processing_time,
            'events_per_second': processed_count / (processing_time / 1000),
            'timestamp': time.time()
        })
        
        print(f"✅ Processed {processed_count} events in {processing_time:.2f}ms")
        print(f"⚡ Throughput: {processed_count / (processing_time / 1000):.0f} events/second")
        
        return {
            'processed': processed_count,
            'failed': failed_count,
            'latency_ms': processing_time
        }
    
    async def balance_regional_load(self, events: List[StreamingEvent]) -> Dict[str, List[StreamingEvent]]:
        """
        Mumbai local mein overcrowding handle karne ki tarah
        Load balancing across Indian regions
        """
        balanced_events = defaultdict(list)
        
        for event in events:
            # Primary region selection based on user location
            primary_region = self.get_primary_region(event.location)
            
            # Check if primary region is overloaded
            if self.is_region_overloaded(primary_region):
                # Spillover to nearest region - Mumbai overload to Pune redirect
                alternative_region = self.get_alternative_region(primary_region)
                balanced_events[alternative_region].append(event)
                
                # Update load counters
                self.regional_processors[alternative_region]['current_load'] += 1
            else:
                balanced_events[primary_region].append(event)
                self.regional_processors[primary_region]['current_load'] += 1
        
        return dict(balanced_events)
    
    async def process_regional_events(self, region: str, events: List[StreamingEvent]) -> Dict:
        """
        Region-specific event processing with circuit breaker
        """
        if self.circuit_breakers[region]['state'] == 'OPEN':
            # Circuit breaker open - region temporary unavailable
            return await self.handle_circuit_breaker_open(region, events)
        
        processed = 0
        failed = 0
        
        try:
            for event in events:
                try:
                    # Real-time quality adaptation
                    quality_decision = await self.adapt_streaming_quality(event)
                    
                    # Buffer health monitoring
                    buffer_action = await self.monitor_buffer_health(event)
                    
                    # Network optimization
                    network_optimization = await self.optimize_network_delivery(event)
                    
                    # Store processed event in regional cache
                    await self.cache_regional_event(region, event, {
                        'quality': quality_decision,
                        'buffer_action': buffer_action,
                        'network_optimization': network_optimization
                    })
                    
                    processed += 1
                    
                except Exception as e:
                    failed += 1
                    await self.handle_event_processing_error(event, e)
            
            # Reset circuit breaker on success
            self.circuit_breakers[region]['failures'] = 0
            
        except Exception as e:
            # Region-level failure - trigger circuit breaker
            await self.trigger_circuit_breaker(region, e)
            return {'processed': 0, 'failed': len(events)}
        
        return {'processed': processed, 'failed': failed}
    
    async def adapt_streaming_quality(self, event: StreamingEvent) -> Dict:
        """
        Real-time quality adaptation based on network conditions
        Mumbai local mein rush hour capacity adjust karne ki tarah
        """
        current_quality = event.quality
        target_bitrate = event.bitrate
        buffer_health = event.buffer_health
        network_type = event.network_type
        
        # Quality downgrade conditions
        if buffer_health < 2.0 or target_bitrate < self.quality_thresholds[current_quality]['min_bitrate']:
            
            # Progressive quality reduction
            quality_ladder = ['4K', '1080p', '720p', '480p', '360p']
            current_index = quality_ladder.index(current_quality)
            
            if current_index < len(quality_ladder) - 1:
                new_quality = quality_ladder[current_index + 1]
                
                # Send quality change command
                await self.send_quality_change_command(event.session_id, new_quality)
                
                return {
                    'action': 'quality_downgrade',
                    'from_quality': current_quality,
                    'to_quality': new_quality,
                    'reason': 'buffer_health' if buffer_health < 2.0 else 'bandwidth_insufficient'
                }
        
        # Quality upgrade conditions - network improve ho gaya
        elif buffer_health > 8.0 and target_bitrate > self.quality_thresholds[current_quality]['min_bitrate'] * 1.5:
            
            quality_ladder = ['360p', '480p', '720p', '1080p', '4K']
            current_index = quality_ladder.index(current_quality)
            
            if current_index > 0:
                new_quality = quality_ladder[current_index - 1]
                
                await self.send_quality_change_command(event.session_id, new_quality)
                
                return {
                    'action': 'quality_upgrade',
                    'from_quality': current_quality,
                    'to_quality': new_quality,
                    'reason': 'improved_conditions'
                }
        
        return {'action': 'no_change', 'quality': current_quality}
    
    async def monitor_buffer_health(self, event: StreamingEvent) -> Dict:
        """
        Buffer health monitoring - Mumbai local mein crowd control ki tarah
        """
        buffer_health = event.buffer_health
        
        if buffer_health < 1.0:
            # Critical buffer level - immediate action needed
            return {
                'action': 'emergency_buffer',
                'priority': 'high',
                'recommendations': [
                    'reduce_quality_immediately',
                    'increase_chunk_requests',
                    'activate_cdn_boost'
                ]
            }
        
        elif buffer_health < 3.0:
            # Low buffer - preventive action
            return {
                'action': 'preventive_buffer',
                'priority': 'medium',
                'recommendations': [
                    'prepare_quality_reduction',
                    'optimize_cdn_routing',
                    'monitor_closely'
                ]
            }
        
        elif buffer_health > 10.0:
            # Excessive buffering - bandwidth wastage
            return {
                'action': 'optimize_bandwidth',
                'priority': 'low',
                'recommendations': [
                    'reduce_chunk_prefetch',
                    'evaluate_quality_upgrade',
                    'optimize_delivery_timing'
                ]
            }
        
        return {'action': 'maintain_current', 'buffer_health': buffer_health}
    
    def get_primary_region(self, location: str) -> str:
        """Location-based regional mapping"""
        location_mappings = {
            'mumbai': 'mumbai', 'pune': 'mumbai', 'nashik': 'mumbai',
            'delhi': 'delhi', 'gurgaon': 'delhi', 'noida': 'delhi',
            'bangalore': 'bangalore', 'mysore': 'bangalore', 'mangalore': 'bangalore',
            'hyderabad': 'hyderabad', 'vijayawada': 'hyderabad',
            'kolkata': 'kolkata', 'bhubaneswar': 'kolkata'
        }
        
        return location_mappings.get(location.lower(), 'mumbai')  # Default to Mumbai
    
    def is_region_overloaded(self, region: str) -> bool:
        """Check if region capacity is exceeded"""
        region_info = self.regional_processors[region]
        utilization = region_info['current_load'] / region_info['capacity']
        return utilization > 0.85  # 85% capacity threshold
    
    async def send_quality_change_command(self, session_id: str, new_quality: str):
        """Send real-time quality change command to client"""
        command = {
            'session_id': session_id,
            'command': 'change_quality',
            'target_quality': new_quality,
            'timestamp': time.time()
        }
        
        # Send via WebSocket or Server-Sent Events
        await self.send_realtime_command(command)

# Hotstar Production Metrics Dashboard
class HotstarMetricsDashboard:
    """
    Mumbai Railway Control Room style metrics dashboard
    """
    
    def __init__(self):
        self.metrics_store = redis.Redis(host='metrics-redis', port=6379)
        
        # Key metrics to track
        self.key_metrics = [
            'concurrent_viewers',
            'average_quality',
            'buffer_ratio',
            'error_rate',
            'regional_distribution',
            'quality_distribution',
            'network_distribution'
        ]
    
    async def update_realtime_metrics(self, events: List[StreamingEvent]):
        """Update real-time metrics for dashboard"""
        
        # Concurrent viewers by region
        regional_counts = defaultdict(int)
        quality_counts = defaultdict(int)
        network_counts = defaultdict(int)
        buffer_health_sum = 0
        error_count = 0
        
        for event in events:
            regional_counts[event.location] += 1
            quality_counts[event.quality] += 1
            network_counts[event.network_type] += 1
            buffer_health_sum += event.buffer_health
            
            if event.event_type == 'error':
                error_count += 1
        
        total_events = len(events)
        
        # Store metrics in Redis for real-time dashboard
        metrics = {
            'total_concurrent': total_events,
            'regional_distribution': dict(regional_counts),
            'quality_distribution': dict(quality_counts),
            'network_distribution': dict(network_counts),
            'average_buffer_health': buffer_health_sum / total_events if total_events > 0 else 0,
            'error_rate': (error_count / total_events) * 100 if total_events > 0 else 0,
            'timestamp': time.time()
        }
        
        # Store with expiry
        await self.metrics_store.setex(
            'hotstar_realtime_metrics', 
            60,  # 1 minute expiry
            json.dumps(metrics)
        )
        
        return metrics

# Usage example for IPL match
async def hotstar_ipl_processing_example():
    """
    IPL Final match processing - 25M+ concurrent viewers
    """
    processor = HotstarStreamingProcessor()
    dashboard = HotstarMetricsDashboard()
    
    # Simulate IPL final viewership pattern
    events = []
    
    # Peak viewership during over 19.4 (Dhoni's last ball)
    for i in range(25000000):  # 25M concurrent viewers
        event = StreamingEvent(
            event_id=f"evt_{i}",
            user_id=f"user_{i}",
            device_id=f"device_{i}",
            session_id=f"session_{i}",
            event_type="play",
            timestamp=time.time(),
            quality=["720p", "1080p", "4K"][i % 3],
            location=["mumbai", "delhi", "bangalore", "hyderabad", "pune"][i % 5],
            content_id="ipl_final_2024",
            bitrate=8000,
            buffer_health=5.0,
            network_type=["4G", "5G", "WiFi"][i % 3]
        )
        events.append(event)
    
    print("🏏 Starting IPL Final streaming processing...")
    print(f"📊 Total events to process: {len(events):,}")
    
    # Process in batches for memory efficiency
    batch_size = 100000  # 100K events per batch
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        
        # Process batch
        result = await processor.process_streaming_events(batch)
        
        # Update dashboard
        await dashboard.update_realtime_metrics(batch)
        
        print(f"✅ Batch {i//batch_size + 1} processed: {result['processed']:,} events")
    
    print("🎉 IPL Final streaming processing completed!")

# Run the example
if __name__ == "__main__":
    import asyncio
    asyncio.run(hotstar_ipl_processing_example())
```

### Error Handling aur Stream Replay: Mumbai Monsoon Resilience

#### Stream Processing Error Categories

Jaise Mumbai mein monsoon ke different levels hote hain (light rain, heavy rain, flood), waise hi streaming errors ke different categories hote hain:

1. **Transient Errors** (Light Rain): Network hiccups, temporary slowdowns
2. **Persistent Errors** (Heavy Rain): Service unavailability, resource exhaustion  
3. **Catastrophic Errors** (Flood): Data corruption, complete system failure

```python
# Production-grade Error Handling and Stream Replay System
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
import asyncio
import json
import time
from collections import deque
import pickle

class ErrorSeverity(Enum):
    TRANSIENT = "transient"      # Light rain - retry karo
    PERSISTENT = "persistent"    # Heavy rain - alternative route lo
    CATASTROPHIC = "catastrophic" # Flood - full recovery needed

@dataclass
class StreamError:
    error_id: str
    timestamp: float
    severity: ErrorSeverity
    component: str
    error_message: str
    event_data: Dict
    retry_count: int = 0
    max_retries: int = 3

class StreamReplayManager:
    """
    Mumbai monsoon ke baad railway service restore karne ki tarah
    Failed events ko replay karne ka system
    """
    
    def __init__(self):
        self.failed_events_store = deque(maxlen=1000000)  # 1M failed events store kar sakte hain
        self.replay_strategies = {
            ErrorSeverity.TRANSIENT: self.exponential_backoff_replay,
            ErrorSeverity.PERSISTENT: self.alternative_path_replay,
            ErrorSeverity.CATASTROPHIC: self.full_recovery_replay
        }
        
        # Dead letter queue for unrecoverable events
        self.dead_letter_queue = deque(maxlen=100000)
        
        # Replay metrics
        self.replay_metrics = {
            'total_replays': 0,
            'successful_replays': 0,
            'failed_replays': 0,
            'events_in_dlq': 0
        }
    
    async def handle_stream_error(self, error: StreamError) -> bool:
        """
        Mumbai Railway ki emergency response ki tarah systematic error handling
        """
        print(f"🚨 Stream error detected: {error.error_id} - {error.severity.value}")
        
        # Log error for debugging
        await self.log_error_details(error)
        
        # Choose replay strategy based on severity
        replay_strategy = self.replay_strategies.get(error.severity)
        
        if replay_strategy:
            success = await replay_strategy(error)
            
            if success:
                self.replay_metrics['successful_replays'] += 1
                print(f"✅ Error {error.error_id} successfully replayed")
                return True
            else:
                # Move to dead letter queue if max retries exceeded
                if error.retry_count >= error.max_retries:
                    await self.move_to_dead_letter_queue(error)
                    return False
                else:
                    # Store for retry
                    error.retry_count += 1
                    self.failed_events_store.append(error)
                    return False
        
        return False
    
    async def exponential_backoff_replay(self, error: StreamError) -> bool:
        """
        Light rain ke baad train service restore - exponential backoff
        """
        wait_time = min(2 ** error.retry_count, 60)  # Max 60 seconds wait
        
        print(f"⏳ Exponential backoff: waiting {wait_time}s before retry {error.retry_count + 1}")
        await asyncio.sleep(wait_time)
        
        try:
            # Retry the original operation
            result = await self.retry_original_operation(error.event_data)
            return result['success']
            
        except Exception as e:
            print(f"❌ Exponential backoff retry failed: {str(e)}")
            return False
    
    async def alternative_path_replay(self, error: StreamError) -> bool:
        """
        Heavy rain mein alternative route - different processing path
        """
        print(f"🔄 Trying alternative processing path for {error.error_id}")
        
        try:
            # Try alternative processing method
            if error.component == 'primary_processor':
                result = await self.process_via_backup_processor(error.event_data)
            elif error.component == 'database':
                result = await self.process_via_cache_fallback(error.event_data)
            elif error.component == 'external_api':
                result = await self.process_via_local_fallback(error.event_data)
            else:
                # Generic alternative processing
                result = await self.process_via_minimal_processor(error.event_data)
            
            return result['success']
            
        except Exception as e:
            print(f"❌ Alternative path replay failed: {str(e)}")
            return False
    
    async def full_recovery_replay(self, error: StreamError) -> bool:
        """
        Flood ke baad complete recovery - full system restoration
        """
        print(f"🚨 Full recovery needed for catastrophic error {error.error_id}")
        
        try:
            # Step 1: System health check
            system_health = await self.check_system_health()
            if not system_health['all_systems_operational']:
                print("❌ System not ready for full recovery")
                return False
            
            # Step 2: State restoration from checkpoint
            state_restored = await self.restore_from_checkpoint(error.timestamp)
            if not state_restored:
                print("❌ State restoration failed")
                return False
            
            # Step 3: Replay from last known good state
            replay_success = await self.replay_from_checkpoint(error.event_data)
            
            return replay_success
            
        except Exception as e:
            print(f"❌ Full recovery replay failed: {str(e)}")
            return False
    
    async def retry_original_operation(self, event_data: Dict) -> Dict:
        """Retry the original failed operation"""
        # Simulate original operation retry
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # 70% success rate for transient error retries
        import random
        success = random.random() < 0.7
        
        return {'success': success, 'result': event_data if success else None}
    
    async def process_via_backup_processor(self, event_data: Dict) -> Dict:
        """Process using backup processor with reduced functionality"""
        await asyncio.sleep(0.2)  # Backup processor is slower
        
        # 80% success rate for backup processor
        import random
        success = random.random() < 0.8
        
        return {'success': success, 'result': event_data if success else None}
    
    async def move_to_dead_letter_queue(self, error: StreamError):
        """Move unrecoverable events to dead letter queue"""
        self.dead_letter_queue.append(error)
        self.replay_metrics['events_in_dlq'] += 1
        
        print(f"⚰️  Event {error.error_id} moved to dead letter queue after {error.retry_count} retries")
        
        # Alert operations team
        await self.alert_operations_team(error)
    
    async def alert_operations_team(self, error: StreamError):
        """Send alert to operations team for manual intervention"""
        alert = {
            'alert_type': 'stream_processing_failure',
            'error_id': error.error_id,
            'severity': error.severity.value,
            'component': error.component,
            'retry_count': error.retry_count,
            'timestamp': error.timestamp,
            'requires_manual_intervention': True
        }
        
        # Send to alerting system (PagerDuty, Slack, etc.)
        print(f"🚨 ALERT: Manual intervention required for {error.error_id}")

# UPI Transaction Stream with Error Handling
class UPIStreamWithErrorHandling:
    """
    UPI transaction processing with comprehensive error handling
    Mumbai local train ki punctuality ke saath
    """
    
    def __init__(self):
        self.replay_manager = StreamReplayManager()
        self.circuit_breaker_states = {}
        
        # Error thresholds
        self.error_thresholds = {
            'transient_error_rate': 5.0,      # 5% transient errors acceptable
            'persistent_error_rate': 1.0,     # 1% persistent errors acceptable
            'catastrophic_error_rate': 0.1    # 0.1% catastrophic errors acceptable
        }
    
    async def process_upi_transaction_with_recovery(self, transaction_data: Dict) -> Dict:
        """
        UPI transaction processing with comprehensive error recovery
        """
        try:
            # Primary processing
            result = await self.process_upi_transaction_primary(transaction_data)
            
            if result['success']:
                return result
            else:
                # Create error for replay
                error = StreamError(
                    error_id=f"upi_error_{transaction_data['transaction_id']}",
                    timestamp=time.time(),
                    severity=self.classify_error_severity(result['error']),
                    component='upi_processor',
                    error_message=result['error'],
                    event_data=transaction_data
                )
                
                # Handle error with replay
                recovery_success = await self.replay_manager.handle_stream_error(error)
                
                return {
                    'success': recovery_success,
                    'transaction_id': transaction_data['transaction_id'],
                    'recovery_attempted': True,
                    'original_error': result['error']
                }
                
        except Exception as e:
            # Unexpected system error
            error = StreamError(
                error_id=f"system_error_{transaction_data['transaction_id']}",
                timestamp=time.time(),
                severity=ErrorSeverity.CATASTROPHIC,
                component='system',
                error_message=str(e),
                event_data=transaction_data
            )
            
            await self.replay_manager.handle_stream_error(error)
            
            return {
                'success': False,
                'transaction_id': transaction_data['transaction_id'],
                'error': 'system_error',
                'recovery_attempted': True
            }
    
    def classify_error_severity(self, error_message: str) -> ErrorSeverity:
        """Classify error severity based on error message"""
        
        transient_keywords = ['timeout', 'network', 'temporary', 'rate_limit']
        persistent_keywords = ['invalid_account', 'insufficient_funds', 'blocked_user']
        catastrophic_keywords = ['database_corruption', 'system_failure', 'data_loss']
        
        error_lower = error_message.lower()
        
        if any(keyword in error_lower for keyword in catastrophic_keywords):
            return ErrorSeverity.CATASTROPHIC
        elif any(keyword in error_lower for keyword in persistent_keywords):
            return ErrorSeverity.PERSISTENT
        else:
            return ErrorSeverity.TRANSIENT
    
    async def process_upi_transaction_primary(self, transaction_data: Dict) -> Dict:
        """Primary UPI transaction processing"""
        # Simulate processing
        await asyncio.sleep(0.05)  # 50ms processing time
        
        # Simulate different error scenarios
        import random
        error_scenario = random.random()
        
        if error_scenario < 0.05:  # 5% error rate
            if error_scenario < 0.001:  # 0.1% catastrophic
                return {'success': False, 'error': 'database_corruption_detected'}
            elif error_scenario < 0.01:  # 1% persistent
                return {'success': False, 'error': 'insufficient_funds'}
            else:  # 4% transient
                return {'success': False, 'error': 'network_timeout'}
        
        return {'success': True, 'transaction_id': transaction_data['transaction_id']}

# Error handling demo
async def error_handling_demo():
    """
    Demonstrate comprehensive error handling and replay
    """
    upi_processor = UPIStreamWithErrorHandling()
    
    # Process 1000 UPI transactions with error handling
    transactions = []
    for i in range(1000):
        transaction = {
            'transaction_id': f'TXN_{i:06d}',
            'amount': 1000.0,
            'sender': f'user_{i}@upi',
            'receiver': 'merchant@upi',
            'timestamp': time.time()
        }
        transactions.append(transaction)
    
    print("💳 Starting UPI transaction processing with error handling...")
    
    successful_transactions = 0
    failed_transactions = 0
    recovered_transactions = 0
    
    for transaction in transactions:
        result = await upi_processor.process_upi_transaction_with_recovery(transaction)
        
        if result['success']:
            successful_transactions += 1
            if result.get('recovery_attempted'):
                recovered_transactions += 1
        else:
            failed_transactions += 1
    
    print(f"📊 Transaction Processing Results:")
    print(f"✅ Successful: {successful_transactions}")
    print(f"❌ Failed: {failed_transactions}")
    print(f"🔄 Recovered: {recovered_transactions}")
    print(f"📈 Recovery Rate: {(recovered_transactions/1000)*100:.1f}%")
    
    # Display replay manager metrics
    metrics = upi_processor.replay_manager.replay_metrics
    print(f"\n🔄 Replay Manager Metrics:")
    print(f"Total Replays: {metrics['total_replays']}")
    print(f"Successful Replays: {metrics['successful_replays']}")
    print(f"Failed Replays: {metrics['failed_replays']}")
    print(f"Events in DLQ: {metrics['events_in_dlq']}")

if __name__ == "__main__":
    asyncio.run(error_handling_demo())
```

### Multi-Region Deployment for India: Railway Network Strategy

#### Geographic Distribution Strategy

India mein streaming services deploy karne ke liye railway network ki tarah strategic planning chahiye. Mumbai se Delhi direct train hai, but Goa jaane ke liye Pune se connect karna padta hai.

```go
// Multi-Region Kafka Deployment for India
// Mumbai, Delhi, Bangalore, Hyderabad - major hubs
package main

import (
    "context"
    "fmt"
    "log"
    "sync"
    "time"
    
    "github.com/segmentio/kafka-go"
    "github.com/prometheus/client_golang/api"
    "github.com/prometheus/client_golang/api/prometheus/v1"
)

// IndiaRegion represents Indian data center regions
type IndiaRegion struct {
    Name            string
    DataCenterCode  string
    KafkaBrokers   []string
    LatencyToOther map[string]time.Duration
    Capacity       int64
    CurrentLoad    int64
    IsActive       bool
}

// MultiRegionKafkaManager manages Kafka across Indian regions
type MultiRegionKafkaManager struct {
    regions        map[string]*IndiaRegion
    writers        map[string]*kafka.Writer
    readers        map[string]*kafka.Reader
    metrics        *PrometheusMetrics
    mu            sync.RWMutex
}

// PrometheusMetrics for monitoring across regions
type PrometheusMetrics struct {
    client   api.Client
    regional map[string]v1.API
}

func NewMultiRegionKafkaManager() *MultiRegionKafkaManager {
    manager := &MultiRegionKafkaManager{
        regions: make(map[string]*IndiaRegion),
        writers: make(map[string]*kafka.Writer),
        readers: make(map[string]*kafka.Reader),
    }
    
    // Initialize Indian regions - Mumbai Railway network ki tarah
    manager.initializeIndianRegions()
    manager.setupKafkaConnections()
    manager.initializeMetrics()
    
    return manager
}

func (m *MultiRegionKafkaManager) initializeIndianRegions() {
    // Mumbai Region - Financial capital, highest throughput
    mumbai := &IndiaRegion{
        Name:           "Mumbai",
        DataCenterCode: "ap-south-1a",
        KafkaBrokers: []string{
            "kafka-mumbai-1:9092",
            "kafka-mumbai-2:9092", 
            "kafka-mumbai-3:9092",
        },
        LatencyToOther: map[string]time.Duration{
            "Delhi":     80 * time.Millisecond,  // 80ms Mumbai to Delhi
            "Bangalore": 45 * time.Millisecond,  // 45ms Mumbai to Bangalore  
            "Hyderabad": 60 * time.Millisecond,  // 60ms Mumbai to Hyderabad
            "Pune":      15 * time.Millisecond,  // 15ms Mumbai to Pune
        },
        Capacity:    10000000, // 10M events/hour capacity
        CurrentLoad: 0,
        IsActive:    true,
    }
    
    // Delhi Region - Government and North India
    delhi := &IndiaRegion{
        Name:           "Delhi",
        DataCenterCode: "ap-south-1b",
        KafkaBrokers: []string{
            "kafka-delhi-1:9092",
            "kafka-delhi-2:9092",
            "kafka-delhi-3:9092",
        },
        LatencyToOther: map[string]time.Duration{
            "Mumbai":    80 * time.Millisecond,
            "Bangalore": 100 * time.Millisecond,
            "Hyderabad": 90 * time.Millisecond,
            "Gurgaon":   10 * time.Millisecond,
        },
        Capacity:    8000000, // 8M events/hour
        CurrentLoad: 0,
        IsActive:    true,
    }
    
    // Bangalore Region - Tech capital
    bangalore := &IndiaRegion{
        Name:           "Bangalore",
        DataCenterCode: "ap-south-1c",
        KafkaBrokers: []string{
            "kafka-bangalore-1:9092",
            "kafka-bangalore-2:9092",
            "kafka-bangalore-3:9092",
        },
        LatencyToOther: map[string]time.Duration{
            "Mumbai":    45 * time.Millisecond,
            "Delhi":     100 * time.Millisecond,
            "Hyderabad": 35 * time.Millisecond,
            "Chennai":   20 * time.Millisecond,
        },
        Capacity:    6000000, // 6M events/hour
        CurrentLoad: 0,
        IsActive:    true,
    }
    
    // Hyderabad Region - Growing tech hub
    hyderabad := &IndiaRegion{
        Name:           "Hyderabad",
        DataCenterCode: "ap-south-2a",
        KafkaBrokers: []string{
            "kafka-hyderabad-1:9092",
            "kafka-hyderabad-2:9092",
        },
        LatencyToOther: map[string]time.Duration{
            "Mumbai":    60 * time.Millisecond,
            "Delhi":     90 * time.Millisecond,
            "Bangalore": 35 * time.Millisecond,
            "Chennai":   40 * time.Millisecond,
        },
        Capacity:    4000000, // 4M events/hour
        CurrentLoad: 0,
        IsActive:    true,
    }
    
    m.regions["mumbai"] = mumbai
    m.regions["delhi"] = delhi
    m.regions["bangalore"] = bangalore
    m.regions["hyderabad"] = hyderabad
}

func (m *MultiRegionKafkaManager) setupKafkaConnections() {
    for regionName, region := range m.regions {
        // Setup writer for each region
        writer := &kafka.Writer{
            Addr:         kafka.TCP(region.KafkaBrokers...),
            Topic:        fmt.Sprintf("events-%s", regionName),
            Balancer:     &kafka.LeastBytes{},
            RequiredAcks: kafka.RequireAll, // Wait for all replicas
            Async:        true,             // Async for better throughput
            BatchSize:    100,              // Batch 100 messages
            BatchTimeout: 10 * time.Millisecond,
        }
        
        // Setup reader for each region
        reader := kafka.NewReader(kafka.ReaderConfig{
            Brokers:        region.KafkaBrokers,
            Topic:          fmt.Sprintf("events-%s", regionName),
            GroupID:        fmt.Sprintf("processor-%s", regionName),
            MinBytes:       1e3,   // 1KB min
            MaxBytes:       10e6,  // 10MB max
            CommitInterval: 100 * time.Millisecond,
        })
        
        m.writers[regionName] = writer
        m.readers[regionName] = reader
    }
}

// RegionalEventRouter routes events to optimal region
type RegionalEventRouter struct {
    manager *MultiRegionKafkaManager
    
    // Load balancing strategies
    strategies map[string]func(event Event) string
}

type Event struct {
    ID        string    `json:"id"`
    Type      string    `json:"type"`
    Source    string    `json:"source"`
    Timestamp time.Time `json:"timestamp"`
    Data      map[string]interface{} `json:"data"`
    UserLocation string `json:"user_location"`
    Priority  int       `json:"priority"` // 1=highest, 10=lowest
}

func NewRegionalEventRouter(manager *MultiRegionKafkaManager) *RegionalEventRouter {
    router := &RegionalEventRouter{
        manager:    manager,
        strategies: make(map[string]func(event Event) string),
    }
    
    // Define routing strategies
    router.strategies["proximity"] = router.routeByProximity
    router.strategies["load_balanced"] = router.routeByLoadBalance
    router.strategies["priority"] = router.routeByPriority
    router.strategies["content_type"] = router.routeByContentType
    
    return router
}

func (r *RegionalEventRouter) routeByProximity(event Event) string {
    /*
    Mumbai local train ki tarah - nearest station routing
    User Mumbai mein hai to Mumbai region mein process karo
    */
    locationToRegion := map[string]string{
        "mumbai": "mumbai", "pune": "mumbai", "nashik": "mumbai",
        "delhi": "delhi", "gurgaon": "delhi", "noida": "delhi",
        "bangalore": "bangalore", "mysore": "bangalore",
        "hyderabad": "hyderabad", "vijayawada": "hyderabad",
    }
    
    if region, exists := locationToRegion[event.UserLocation]; exists {
        return region
    }
    
    return "mumbai" // Default to Mumbai - financial capital
}

func (r *RegionalEventRouter) routeByLoadBalance(event Event) string {
    /*
    Mumbai local mein crowd management ki tarah
    Least loaded region mein route karo
    */
    r.manager.mu.RLock()
    defer r.manager.mu.RUnlock()
    
    var selectedRegion string
    minUtilization := float64(1.0)
    
    for regionName, region := range r.manager.regions {
        if !region.IsActive {
            continue
        }
        
        utilization := float64(region.CurrentLoad) / float64(region.Capacity)
        if utilization < minUtilization {
            minUtilization = utilization
            selectedRegion = regionName
        }
    }
    
    if selectedRegion == "" {
        selectedRegion = "mumbai" // Fallback
    }
    
    return selectedRegion
}

func (r *RegionalEventRouter) routeByPriority(event Event) string {
    /*
    VIP train service ki tarah - high priority events ko best region mein
    */
    if event.Priority <= 3 { // High priority events
        // Route to Mumbai - best infrastructure
        return "mumbai"
    } else if event.Priority <= 6 { // Medium priority
        // Route to Delhi or Bangalore
        return r.routeByLoadBalance(event)
    } else { // Low priority
        // Route to any available region
        return r.routeByLoadBalance(event)
    }
}

func (r *RegionalEventRouter) RouteEvent(event Event, strategy string) (string, error) {
    routingFunc, exists := r.strategies[strategy]
    if !exists {
        return "", fmt.Errorf("unknown routing strategy: %s", strategy)
    }
    
    selectedRegion := routingFunc(event)
    
    // Update load for selected region
    r.manager.mu.Lock()
    if region, exists := r.manager.regions[selectedRegion]; exists {
        region.CurrentLoad++
    }
    r.manager.mu.Unlock()
    
    return selectedRegion, nil
}

// Cross-region replication for disaster recovery
func (m *MultiRegionKafkaManager) SetupCrossRegionReplication() {
    /*
    Mumbai-Delhi Rajdhani Express ki tarah
    Critical data ka backup multiple regions mein
    */
    
    // Mumbai to Delhi replication
    go m.replicateRegionData("mumbai", "delhi", []string{"financial_transactions", "user_events"})
    
    // Delhi to Bangalore replication  
    go m.replicateRegionData("delhi", "bangalore", []string{"government_data", "compliance_events"})
    
    // Bangalore to Hyderabad replication
    go m.replicateRegionData("bangalore", "hyderabad", []string{"tech_events", "analytics_data"})
    
    // Full backup to Mumbai (primary region)
    go m.setupFullBackupToMumbai()
}

func (m *MultiRegionKafkaManager) replicateRegionData(sourceRegion, targetRegion string, topics []string) {
    for _, topic := range topics {
        go func(t string) {
            sourceReader := kafka.NewReader(kafka.ReaderConfig{
                Brokers: m.regions[sourceRegion].KafkaBrokers,
                Topic:   t,
                GroupID: fmt.Sprintf("replication-%s-to-%s", sourceRegion, targetRegion),
            })
            defer sourceReader.Close()
            
            targetWriter := &kafka.Writer{
                Addr:  kafka.TCP(m.regions[targetRegion].KafkaBrokers...),
                Topic: fmt.Sprintf("%s-replica", t),
            }
            defer targetWriter.Close()
            
            for {
                ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
                message, err := sourceReader.ReadMessage(ctx)
                cancel()
                
                if err != nil {
                    log.Printf("Replication read error for %s: %v", t, err)
                    time.Sleep(1 * time.Second)
                    continue
                }
                
                // Write to target region
                err = targetWriter.WriteMessages(context.Background(), kafka.Message{
                    Key:   message.Key,
                    Value: message.Value,
                    Headers: append(message.Headers, kafka.Header{
                        Key:   "replicated_from",
                        Value: []byte(sourceRegion),
                    }),
                })
                
                if err != nil {
                    log.Printf("Replication write error for %s: %v", t, err)
                }
            }
        }(topic)
    }
}

// Regional monitoring and alerting
func (m *MultiRegionKafkaManager) MonitorRegionalHealth() {
    ticker := time.NewTicker(30 * time.Second)
    defer ticker.Stop()
    
    for range ticker.C {
        for regionName, region := range m.regions {
            // Check region health
            health := m.checkRegionHealth(regionName)
            
            if !health.IsHealthy {
                log.Printf("🚨 Region %s health degraded: %s", regionName, health.Issue)
                
                // Failover logic - Mumbai local mein track change ki tarah
                if health.ShouldFailover {
                    m.initiateRegionalFailover(regionName)
                }
            }
            
            // Update load metrics
            utilization := float64(region.CurrentLoad) / float64(region.Capacity)
            if utilization > 0.8 { // 80% utilization warning
                log.Printf("⚠️  Region %s high utilization: %.1f%%", regionName, utilization*100)
            }
        }
    }
}

type RegionHealth struct {
    IsHealthy      bool
    Issue          string
    ShouldFailover bool
    Latency        time.Duration
    ErrorRate      float64
}

func (m *MultiRegionKafkaManager) checkRegionHealth(regionName string) RegionHealth {
    region := m.regions[regionName]
    
    // Check Kafka broker connectivity
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    
    conn, err := kafka.DialContext(ctx, "tcp", region.KafkaBrokers[0])
    if err != nil {
        return RegionHealth{
            IsHealthy:      false,
            Issue:          fmt.Sprintf("Cannot connect to Kafka: %v", err),
            ShouldFailover: true,
        }
    }
    conn.Close()
    
    // Check latency and error rates via metrics
    latency, errorRate := m.getRegionMetrics(regionName)
    
    if latency > 200*time.Millisecond {
        return RegionHealth{
            IsHealthy:      false,
            Issue:          fmt.Sprintf("High latency: %v", latency),
            ShouldFailover: false, // Just warning
            Latency:        latency,
            ErrorRate:      errorRate,
        }
    }
    
    if errorRate > 5.0 { // 5% error rate threshold
        return RegionHealth{
            IsHealthy:      false,
            Issue:          fmt.Sprintf("High error rate: %.2f%%", errorRate),
            ShouldFailover: true,
            Latency:        latency,
            ErrorRate:      errorRate,
        }
    }
    
    return RegionHealth{
        IsHealthy:      true,
        Issue:          "",
        ShouldFailover: false,
        Latency:        latency,
        ErrorRate:      errorRate,
    }
}

func (m *MultiRegionKafkaManager) getRegionMetrics(regionName string) (time.Duration, float64) {
    // Integration with Prometheus metrics
    // This would query actual Prometheus metrics in production
    
    // Simulate metrics for demo
    import "math/rand"
    latency := time.Duration(rand.Intn(100)+50) * time.Millisecond // 50-150ms
    errorRate := rand.Float64() * 3.0 // 0-3% error rate
    
    return latency, errorRate
}

// Example usage
func main() {
    fmt.Println("🚀 Starting Multi-Region Kafka for India...")
    
    // Initialize multi-region manager
    manager := NewMultiRegionKafkaManager()
    defer manager.Close()
    
    // Setup cross-region replication
    manager.SetupCrossRegionReplication()
    
    // Start regional monitoring
    go manager.MonitorRegionalHealth()
    
    // Create event router
    router := NewRegionalEventRouter(manager)
    
    // Simulate events from different cities
    events := []Event{
        {
            ID: "evt_001", Type: "payment", Source: "paytm",
            UserLocation: "mumbai", Priority: 1,
            Data: map[string]interface{}{"amount": 1000},
        },
        {
            ID: "evt_002", Type: "order", Source: "zomato",
            UserLocation: "delhi", Priority: 5,
            Data: map[string]interface{}{"restaurant_id": "12345"},
        },
        {
            ID: "evt_003", Type: "ride", Source: "ola",
            UserLocation: "bangalore", Priority: 3,
            Data: map[string]interface{}{"trip_id": "67890"},
        },
    }
    
    // Route events to optimal regions
    for _, event := range events {
        region, err := router.RouteEvent(event, "proximity")
        if err != nil {
            log.Printf("Routing error: %v", err)
            continue
        }
        
        fmt.Printf("📍 Event %s routed to %s region\n", event.ID, region)
        
        // Write event to selected region
        writer := manager.writers[region]
        err = writer.WriteMessages(context.Background(), kafka.Message{
            Key:   []byte(event.ID),
            Value: []byte(fmt.Sprintf("Event data for %s", event.ID)),
        })
        
        if err != nil {
            log.Printf("Write error: %v", err)
        }
    }
    
    fmt.Println("✅ Multi-region deployment demo completed!")
    
    // Keep running for monitoring
    select {}
}

func (m *MultiRegionKafkaManager) Close() {
    for _, writer := range m.writers {
        writer.Close()
    }
    for _, reader := range m.readers {
        reader.Close()
    }
}

func (m *MultiRegionKafkaManager) initiateRegionalFailover(failedRegion string) {
    log.Printf("🔄 Initiating failover for region: %s", failedRegion)
    
    // Mark region as inactive
    m.regions[failedRegion].IsActive = false
    
    // Redistribute load to healthy regions
    // This is a simplified version - production would be more sophisticated
    
    // Alert operations team
    log.Printf("🚨 ALERT: Region %s failed over. Manual intervention may be required.", failedRegion)
}
```

### Cost Optimization Strategies: Mumbai Local Train Ki Economy

#### Indian Startup Cost Optimization

Indian startups ke liye streaming infrastructure expensive hai. Mumbai local train monthly pass ki tarah cost optimization karna padta hai.

```python
# Cost Optimization for Indian Streaming Startups
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import json
import time
from datetime import datetime, timedelta

@dataclass
class CostMetrics:
    """Cost tracking for Indian streaming infrastructure"""
    compute_cost_per_hour: float  # ₹ per hour
    storage_cost_per_gb: float    # ₹ per GB per month
    network_cost_per_gb: float    # ₹ per GB transfer
    kafka_cost_per_partition: float  # ₹ per partition per month
    region: str
    currency: str = "INR"

class IndianCostOptimizer:
    """
    Mumbai local train pass ki tarah cost optimization
    Indian startup budget ke saath intelligent scaling
    """
    
    def __init__(self):
        # Indian cloud pricing (approximate)
        self.cost_metrics = {
            'mumbai': CostMetrics(
                compute_cost_per_hour=8.0,      # ₹8/hour for m5.large
                storage_cost_per_gb=1.5,        # ₹1.5/GB/month
                network_cost_per_gb=0.8,        # ₹0.8/GB transfer
                kafka_cost_per_partition=50.0,  # ₹50/partition/month
                region='mumbai'
            ),
            'delhi': CostMetrics(
                compute_cost_per_hour=7.5,
                storage_cost_per_gb=1.4,
                network_cost_per_gb=0.75,
                kafka_cost_per_partition=45.0,
                region='delhi'
            ),
            'bangalore': CostMetrics(
                compute_cost_per_hour=7.0,
                storage_cost_per_gb=1.3,
                network_cost_per_gb=0.7,
                kafka_cost_per_partition=40.0,
                region='bangalore'
            )
        }
        
        # Traffic patterns for Indian apps (peak hours)
        self.indian_traffic_patterns = {
            'morning_peak': {'start': 8, 'end': 11, 'multiplier': 2.5},   # Office time
            'lunch_peak': {'start': 12, 'end': 14, 'multiplier': 1.8},   # Lunch break
            'evening_peak': {'start': 17, 'end': 22, 'multiplier': 3.0}, # Post office + entertainment
            'night_low': {'start': 23, 'end': 7, 'multiplier': 0.3},     # Low activity
        }
        
        # Cost optimization strategies
        self.optimization_strategies = [
            'dynamic_scaling',
            'regional_optimization',
            'partition_optimization',
            'storage_tiering',
            'network_optimization'
        ]
    
    def calculate_monthly_cost(self, usage_metrics: Dict) -> Dict:
        """
        Calculate monthly streaming infrastructure cost
        Mumbai local monthly pass calculation ki tarah
        """
        total_cost = 0
        cost_breakdown = {}
        
        for region, metrics in usage_metrics.items():
            region_cost_metrics = self.cost_metrics[region]
            
            # Compute cost (instances running 24/7 for base load + scaling)
            base_hours = 24 * 30  # 30 days
            peak_hours = metrics.get('peak_additional_hours', 0)
            total_compute_hours = base_hours + peak_hours
            
            compute_cost = total_compute_hours * region_cost_metrics.compute_cost_per_hour
            
            # Storage cost (event retention + state stores)
            storage_gb = metrics.get('storage_gb', 0)
            storage_cost = storage_gb * region_cost_metrics.storage_cost_per_gb
            
            # Network cost (inter-region replication + client data)
            network_gb = metrics.get('network_gb', 0)
            network_cost = network_gb * region_cost_metrics.network_cost_per_gb
            
            # Kafka partition cost
            partitions = metrics.get('kafka_partitions', 0)
            kafka_cost = partitions * region_cost_metrics.kafka_cost_per_partition
            
            region_total = compute_cost + storage_cost + network_cost + kafka_cost
            
            cost_breakdown[region] = {
                'compute_cost': compute_cost,
                'storage_cost': storage_cost,
                'network_cost': network_cost,
                'kafka_cost': kafka_cost,
                'total': region_total,
                'currency': 'INR'
            }
            
            total_cost += region_total
        
        return {
            'total_monthly_cost': total_cost,
            'breakdown_by_region': cost_breakdown,
            'currency': 'INR',
            'optimization_potential': self.identify_optimization_opportunities(cost_breakdown)
        }
    
    def optimize_for_indian_traffic(self, current_usage: Dict) -> Dict:
        """
        Indian traffic pattern ke according optimization
        Mumbai local train schedule ki tarah predictable patterns
        """
        
        optimizations = {
            'dynamic_scaling': self.optimize_dynamic_scaling(current_usage),
            'regional_cost': self.optimize_regional_costs(current_usage),
            'storage_tiering': self.optimize_storage_costs(current_usage),
            'network_efficiency': self.optimize_network_costs(current_usage)
        }
        
        # Calculate potential savings
        total_savings = sum(opt['monthly_savings'] for opt in optimizations.values())
        
        return {
            'current_monthly_cost': self.calculate_monthly_cost(current_usage)['total_monthly_cost'],
            'optimized_monthly_cost': self.calculate_monthly_cost(current_usage)['total_monthly_cost'] - total_savings,
            'monthly_savings': total_savings,
            'savings_percentage': (total_savings / self.calculate_monthly_cost(current_usage)['total_monthly_cost']) * 100,
            'optimization_details': optimizations,
            'recommendations': self.generate_optimization_recommendations(optimizations)
        }
    
    def optimize_dynamic_scaling(self, usage: Dict) -> Dict:
        """
        Mumbai local train frequency adjust karne ki tarah
        Peak time mein more instances, night mein less
        """
        current_cost = 0
        optimized_cost = 0
        
        for region, metrics in usage.items():
            region_cost = self.cost_metrics[region].compute_cost_per_hour
            
            # Current: Fixed instances 24/7
            current_instances = metrics.get('fixed_instances', 5)
            current_cost += current_instances * 24 * 30 * region_cost
            
            # Optimized: Dynamic scaling based on Indian traffic patterns
            base_instances = 2  # Minimum for reliability
            
            # Calculate optimized cost with traffic patterns
            daily_cost = 0
            for hour in range(24):
                multiplier = self.get_traffic_multiplier(hour)
                required_instances = max(base_instances, int(base_instances * multiplier))
                daily_cost += required_instances * region_cost
            
            optimized_cost += daily_cost * 30  # 30 days
        
        monthly_savings = current_cost - optimized_cost
        
        return {
            'strategy': 'dynamic_scaling',
            'current_monthly_cost': current_cost,
            'optimized_monthly_cost': optimized_cost,
            'monthly_savings': monthly_savings,
            'implementation': {
                'use_auto_scaling_groups': True,
                'peak_hours': [8, 11, 12, 14, 17, 22],
                'scale_up_threshold': '70%_cpu',
                'scale_down_threshold': '30%_cpu',
                'min_instances': 2,
                'max_instances': 20
            }
        }
    
    def optimize_regional_costs(self, usage: Dict) -> Dict:
        """
        Sabse cost-effective region choose karna
        Mumbai expensive hai to Bangalore mein process karo
        """
        current_regional_costs = {}
        optimized_regional_costs = {}
        
        for region, metrics in usage.items():
            current_cost = self.calculate_regional_cost(region, metrics)
            current_regional_costs[region] = current_cost
            
            # Find cheapest region for this workload
            cheapest_region = min(self.cost_metrics.keys(), 
                                key=lambda r: self.calculate_regional_cost(r, metrics))
            
            optimized_cost = self.calculate_regional_cost(cheapest_region, metrics)
            optimized_regional_costs[region] = {
                'original_region': region,
                'optimized_region': cheapest_region,
                'cost': optimized_cost
            }
        
        total_current = sum(current_regional_costs.values())
        total_optimized = sum(info['cost'] for info in optimized_regional_costs.values())
        
        return {
            'strategy': 'regional_optimization',
            'current_monthly_cost': total_current,
            'optimized_monthly_cost': total_optimized,
            'monthly_savings': total_current - total_optimized,
            'regional_recommendations': optimized_regional_costs
        }
    
    def optimize_storage_costs(self, usage: Dict) -> Dict:
        """
        Storage tiering - Mumbai local train ki general aur first class ki tarah
        Hot data expensive storage mein, cold data cheap mein
        """
        total_savings = 0
        
        for region, metrics in usage.items():
            storage_gb = metrics.get('storage_gb', 0)
            current_storage_cost = storage_gb * self.cost_metrics[region].storage_cost_per_gb
            
            # Assume 20% hot data (last 7 days), 80% cold data (older)
            hot_data_gb = storage_gb * 0.2
            cold_data_gb = storage_gb * 0.8
            
            # Hot data: Current price
            # Cold data: 50% cheaper with compression + cold storage
            optimized_cost = (hot_data_gb * self.cost_metrics[region].storage_cost_per_gb + 
                            cold_data_gb * self.cost_metrics[region].storage_cost_per_gb * 0.5)
            
            total_savings += current_storage_cost - optimized_cost
        
        return {
            'strategy': 'storage_tiering',
            'monthly_savings': total_savings,
            'implementation': {
                'hot_data_retention': '7_days',
                'cold_data_compression': 'enabled',
                'archival_after': '30_days',
                'delete_after': '365_days'
            }
        }
    
    def get_traffic_multiplier(self, hour: int) -> float:
        """Get traffic multiplier for given hour (24-hour format)"""
        for pattern_name, pattern in self.indian_traffic_patterns.items():
            if pattern['start'] <= hour <= pattern['end']:
                return pattern['multiplier']
        
        return 1.0  # Default multiplier
    
    def calculate_regional_cost(self, region: str, metrics: Dict) -> float:
        """Calculate cost for specific region and metrics"""
        region_metrics = self.cost_metrics[region]
        
        compute_cost = metrics.get('compute_hours', 720) * region_metrics.compute_cost_per_hour
        storage_cost = metrics.get('storage_gb', 0) * region_metrics.storage_cost_per_gb
        network_cost = metrics.get('network_gb', 0) * region_metrics.network_cost_per_gb
        kafka_cost = metrics.get('kafka_partitions', 0) * region_metrics.kafka_cost_per_partition
        
        return compute_cost + storage_cost + network_cost + kafka_cost
    
    def generate_optimization_recommendations(self, optimizations: Dict) -> List[str]:
        """Generate actionable recommendations for Indian startups"""
        recommendations = []
        
        # Dynamic scaling recommendations
        if optimizations['dynamic_scaling']['monthly_savings'] > 5000:  # ₹5K+ savings
            recommendations.append(
                "🔄 Implement auto-scaling: Save ₹{:,.0f}/month by scaling with Indian traffic patterns".format(
                    optimizations['dynamic_scaling']['monthly_savings']
                )
            )
        
        # Regional optimization
        if optimizations['regional_cost']['monthly_savings'] > 3000:  # ₹3K+ savings
            recommendations.append(
                "📍 Regional optimization: Save ₹{:,.0f}/month by moving workloads to cost-effective regions".format(
                    optimizations['regional_cost']['monthly_savings']
                )
            )
        
        # Storage optimization
        if optimizations['storage_tiering']['monthly_savings'] > 1000:  # ₹1K+ savings
            recommendations.append(
                "💾 Storage tiering: Save ₹{:,.0f}/month with hot/cold data separation".format(
                    optimizations['storage_tiering']['monthly_savings']
                )
            )
        
        # Indian-specific recommendations
        recommendations.extend([
            "🇮🇳 Use Indian cloud providers (AWS Mumbai, Azure South India) for data residency",
            "🚆 Align scaling with Mumbai local train schedules (peak: 8-11, 17-22)",
            "💰 Consider quarterly payments for 10-15% discount on Indian cloud services",
            "📊 Monitor costs daily - Indian rupee fluctuations affect USD-based pricing"
        ])
        
        return recommendations

# Cost optimization demo for Indian startup
def indian_startup_cost_demo():
    """
    Demonstrate cost optimization for Indian streaming startup
    Budget: ₹2L/month initially, scale to ₹10L as we grow
    """
    optimizer = IndianCostOptimizer()
    
    # Typical Indian startup usage pattern
    startup_usage = {
        'mumbai': {
            'fixed_instances': 5,
            'compute_hours': 3600,  # 5 instances * 24 hours * 30 days
            'storage_gb': 500,      # 500GB event storage
            'network_gb': 1000,     # 1TB network transfer
            'kafka_partitions': 20  # 20 Kafka partitions
        },
        'bangalore': {
            'fixed_instances': 3,
            'compute_hours': 2160,  # 3 instances * 24 hours * 30 days
            'storage_gb': 300,      # 300GB storage
            'network_gb': 600,      # 600GB transfer
            'kafka_partitions': 12  # 12 partitions
        }
    }
    
    print("💰 Indian Startup Streaming Cost Analysis")
    print("=" * 50)
    
    # Current cost calculation
    current_cost = optimizer.calculate_monthly_cost(startup_usage)
    print(f"📊 Current Monthly Cost: ₹{current_cost['total_monthly_cost']:,.0f}")
    
    for region, breakdown in current_cost['breakdown_by_region'].items():
        print(f"  📍 {region.capitalize()}: ₹{breakdown['total']:,.0f}")
        print(f"    💻 Compute: ₹{breakdown['compute_cost']:,.0f}")
        print(f"    💾 Storage: ₹{breakdown['storage_cost']:,.0f}")
        print(f"    🌐 Network: ₹{breakdown['network_cost']:,.0f}")
        print(f"    📨 Kafka: ₹{breakdown['kafka_cost']:,.0f}")
    
    print("\n🔧 Cost Optimization Analysis")
    print("=" * 50)
    
    # Optimization recommendations
    optimization = optimizer.optimize_for_indian_traffic(startup_usage)
    
    print(f"💵 Current Cost: ₹{optimization['current_monthly_cost']:,.0f}/month")
    print(f"✅ Optimized Cost: ₹{optimization['optimized_monthly_cost']:,.0f}/month")
    print(f"💰 Monthly Savings: ₹{optimization['monthly_savings']:,.0f}")
    print(f"📈 Savings Percentage: {optimization['savings_percentage']:.1f}%")
    
    print("\n🎯 Optimization Recommendations:")
    for i, recommendation in enumerate(optimization['recommendations'], 1):
        print(f"  {i}. {recommendation}")
    
    # Annual savings calculation
    annual_savings = optimization['monthly_savings'] * 12
    print(f"\n🎉 Annual Savings Potential: ₹{annual_savings:,.0f}")
    
    # Budget impact analysis
    if optimization['optimized_monthly_cost'] <= 200000:  # ₹2L budget
        print("✅ Within startup budget of ₹2L/month!")
    else:
        excess = optimization['optimized_monthly_cost'] - 200000
        print(f"⚠️  Exceeds budget by ₹{excess:,.0f}/month")
    
    print("\n🚀 Growth Scaling Strategy:")
    print("  Phase 1 (0-10K users): ₹50K-1L/month")
    print("  Phase 2 (10K-100K users): ₹1L-5L/month") 
    print("  Phase 3 (100K-1M users): ₹5L-20L/month")
    print("  Phase 4 (1M+ users): ₹20L+/month")

if __name__ == "__main__":
    indian_startup_cost_demo()
```

### Monitoring aur Alerting: Railway Control Room Dashboard

#### Production Monitoring Stack

Mumbai Railway Control Room mein jaise har train track kiya jaata hai, waise hi production streaming systems mein har metric monitor karni padti hai.

```python
# Production Monitoring for Indian Streaming Systems
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time
import asyncio
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
import boto3
import redis

@dataclass
class MetricThreshold:
    """Monitoring thresholds for different severity levels"""
    warning: float
    critical: float
    unit: str
    description: str

@dataclass
class AlertRule:
    """Alert rule configuration"""
    metric_name: str
    threshold: MetricThreshold
    duration_minutes: int  # How long threshold must be breached
    alert_channels: List[str]  # slack, email, sms, pagerduty
    business_impact: str
    runbook_url: str

class IndianStreamingMonitor:
    """
    Mumbai Railway Control Room style monitoring system
    Real-time tracking of streaming infrastructure across India
    """
    
    def __init__(self):
        # Redis for real-time metrics storage
        self.metrics_store = redis.Redis(host='metrics-redis', port=6379, decode_responses=True)
        
        # CloudWatch for AWS metrics (common in Indian startups)
        self.cloudwatch = boto3.client('cloudwatch', region_name='ap-south-1')
        
        # Alert channels
        self.alert_channels = {
            'slack': self.send_slack_alert,
            'email': self.send_email_alert,
            'sms': self.send_sms_alert,
            'pagerduty': self.send_pagerduty_alert
        }
        
        # Metric storage
        self.metrics_buffer = defaultdict(lambda: deque(maxlen=1000))
        
        # Configure monitoring thresholds for Indian context
        self.configure_indian_thresholds()
        
        # Configure alert rules
        self.setup_alert_rules()
        
        # Active alerts tracking
        self.active_alerts = {}
        
        # Regional health status
        self.regional_health = {
            'mumbai': {'status': 'healthy', 'last_check': time.time()},
            'delhi': {'status': 'healthy', 'last_check': time.time()},
            'bangalore': {'status': 'healthy', 'last_check': time.time()},
            'hyderabad': {'status': 'healthy', 'last_check': time.time()}
        }
    
    def configure_indian_thresholds(self):
        """Configure monitoring thresholds optimized for Indian infrastructure"""
        
        self.thresholds = {
            # Latency thresholds (Indian network conditions considered)
            'processing_latency_ms': MetricThreshold(
                warning=200.0,    # 200ms warning (higher than global due to Indian network)
                critical=500.0,   # 500ms critical
                unit='milliseconds',
                description='Event processing latency'
            ),
            
            # Throughput thresholds
            'events_per_second': MetricThreshold(
                warning=100000.0,   # 100K events/sec warning
                critical=50000.0,   # 50K events/sec critical (performance degraded)
                unit='events/second',
                description='Event processing throughput'
            ),
            
            # Error rate thresholds
            'error_rate_percent': MetricThreshold(
                warning=2.0,      # 2% error rate warning
                critical=5.0,     # 5% error rate critical
                unit='percent',
                description='Processing error rate'
            ),
            
            # Memory utilization (Indian cost consciousness)
            'memory_utilization_percent': MetricThreshold(
                warning=75.0,     # 75% memory warning
                critical=90.0,    # 90% memory critical
                unit='percent',
                description='System memory utilization'
            ),
            
            # Kafka lag (critical for streaming)
            'consumer_lag_messages': MetricThreshold(
                warning=100000.0,  # 100K messages lag warning
                critical=500000.0, # 500K messages lag critical
                unit='messages',
                description='Kafka consumer lag'
            ),
            
            # Network bandwidth (important for multi-region)
            'network_utilization_percent': MetricThreshold(
                warning=70.0,     # 70% network utilization warning
                critical=85.0,    # 85% network critical
                unit='percent',
                description='Network bandwidth utilization'
            ),
            
            # Disk I/O (important for state stores)
            'disk_io_utilization_percent': MetricThreshold(
                warning=80.0,     # 80% disk I/O warning
                critical=95.0,    # 95% disk I/O critical
                unit='percent',
                description='Disk I/O utilization'
            ),
            
            # Regional connectivity (Indian network stability)
            'inter_region_latency_ms': MetricThreshold(
                warning=150.0,    # 150ms inter-region latency warning
                critical=300.0,   # 300ms critical
                unit='milliseconds',
                description='Inter-region network latency'
            )
        }
    
    def setup_alert_rules(self):
        """Setup alert rules for different business impacts"""
        
        self.alert_rules = [
            # Critical business impact alerts
            AlertRule(
                metric_name='error_rate_percent',
                threshold=self.thresholds['error_rate_percent'],
                duration_minutes=2,   # 2 minutes of high error rate
                alert_channels=['pagerduty', 'slack', 'sms'],
                business_impact='HIGH - Customer transactions failing',
                runbook_url='https://runbooks.company.com/streaming-high-error-rate'
            ),
            
            AlertRule(
                metric_name='processing_latency_ms',
                threshold=self.thresholds['processing_latency_ms'],
                duration_minutes=5,   # 5 minutes of high latency
                alert_channels=['slack', 'email'],
                business_impact='MEDIUM - Customer experience degraded',
                runbook_url='https://runbooks.company.com/streaming-high-latency'
            ),
            
            AlertRule(
                metric_name='consumer_lag_messages',
                threshold=self.thresholds['consumer_lag_messages'],
                duration_minutes=3,   # 3 minutes of high lag
                alert_channels=['pagerduty', 'slack'],
                business_impact='HIGH - Real-time processing delayed',
                runbook_url='https://runbooks.company.com/kafka-consumer-lag'
            ),
            
            # Regional connectivity alerts
            AlertRule(
                metric_name='inter_region_latency_ms',
                threshold=self.thresholds['inter_region_latency_ms'],
                duration_minutes=5,   # 5 minutes of high inter-region latency
                alert_channels=['slack', 'email'],
                business_impact='MEDIUM - Multi-region replication affected',
                runbook_url='https://runbooks.company.com/inter-region-latency'
            ),
            
            # Resource utilization alerts (cost impact)
            AlertRule(
                metric_name='memory_utilization_percent',
                threshold=self.thresholds['memory_utilization_percent'],
                duration_minutes=10,  # 10 minutes of high memory usage
                alert_channels=['slack'],
                business_impact='LOW - Potential scaling needed',
                runbook_url='https://runbooks.company.com/high-memory-usage'
            )
        ]
    
    async def collect_metrics(self):
        """
        Collect metrics from various sources
        Mumbai Railway ke control room ki tarah centralized collection
        """
        while True:
            try:
                current_time = time.time()
                
                # Collect regional metrics
                for region in ['mumbai', 'delhi', 'bangalore', 'hyderabad']:
                    await self.collect_regional_metrics(region, current_time)
                
                # Collect application metrics
                await self.collect_application_metrics(current_time)
                
                # Collect infrastructure metrics
                await self.collect_infrastructure_metrics(current_time)
                
                # Store aggregated metrics
                await self.store_aggregated_metrics(current_time)
                
                # Sleep for next collection cycle
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                logging.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute on error
    
    async def collect_regional_metrics(self, region: str, timestamp: float):
        """Collect metrics for specific region"""
        
        # Simulate metric collection (in production, these would be real metrics)
        metrics = {
            f'{region}_processing_latency_ms': self.simulate_metric('latency', region),
            f'{region}_events_per_second': self.simulate_metric('throughput', region),
            f'{region}_error_rate_percent': self.simulate_metric('error_rate', region),
            f'{region}_memory_utilization_percent': self.simulate_metric('memory', region),
            f'{region}_cpu_utilization_percent': self.simulate_metric('cpu', region),
            f'{region}_network_utilization_percent': self.simulate_metric('network', region),
            f'{region}_consumer_lag_messages': self.simulate_metric('kafka_lag', region)
        }
        
        # Store in Redis for real-time access
        for metric_name, value in metrics.items():
            self.metrics_store.zadd(
                metric_name, 
                {str(timestamp): value}
            )
            
            # Keep only last 1 hour of data (for memory efficiency)
            cutoff_time = timestamp - 3600
            self.metrics_store.zremrangebyscore(metric_name, 0, cutoff_time)
            
            # Add to buffer for alerting
            self.metrics_buffer[metric_name].append({
                'timestamp': timestamp,
                'value': value
            })
    
    def simulate_metric(self, metric_type: str, region: str) -> float:
        """
        Simulate realistic metrics for demo
        In production, these would come from actual monitoring systems
        """
        import random
        
        # Regional variations (Mumbai generally higher load)
        regional_multipliers = {
            'mumbai': 1.2,    # 20% higher load
            'delhi': 1.1,     # 10% higher load
            'bangalore': 1.0, # Baseline
            'hyderabad': 0.9  # 10% lower load
        }
        
        multiplier = regional_multipliers.get(region, 1.0)
        
        if metric_type == 'latency':
            # Base latency 50-150ms, with regional variation
            base_latency = random.uniform(50, 150)
            return base_latency * multiplier
            
        elif metric_type == 'throughput':
            # Base throughput 80K-120K events/sec
            base_throughput = random.uniform(80000, 120000)
            return base_throughput * multiplier
            
        elif metric_type == 'error_rate':
            # Low error rate 0.1-1%
            base_error_rate = random.uniform(0.1, 1.0)
            return base_error_rate * multiplier
            
        elif metric_type == 'memory':
            # Memory utilization 40-80%
            base_memory = random.uniform(40, 80)
            return base_memory * multiplier
            
        elif metric_type == 'cpu':
            # CPU utilization 30-70%
            base_cpu = random.uniform(30, 70)
            return base_cpu * multiplier
            
        elif metric_type == 'network':
            # Network utilization 20-60%
            base_network = random.uniform(20, 60)
            return base_network * multiplier
            
        elif metric_type == 'kafka_lag':
            # Kafka lag 1K-50K messages
            base_lag = random.uniform(1000, 50000)
            return base_lag * multiplier
        
        return 0.0
    
    async def check_alert_conditions(self):
        """
        Check all alert conditions and trigger alerts
        Mumbai local train delay announcement ki tarah timely alerts
        """
        while True:
            try:
                current_time = time.time()
                
                for alert_rule in self.alert_rules:
                    await self.evaluate_alert_rule(alert_rule, current_time)
                
                # Check for alert recovery
                await self.check_alert_recovery(current_time)
                
                # Sleep between alert checks
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Alert checking error: {e}")
                await asyncio.sleep(60)
    
    async def evaluate_alert_rule(self, alert_rule: AlertRule, current_time: float):
        """Evaluate individual alert rule"""
        
        # Get recent metrics for all regions
        alert_triggered = False
        affected_regions = []
        
        for region in ['mumbai', 'delhi', 'bangalore', 'hyderabad']:
            metric_name = f'{region}_{alert_rule.metric_name}'
            
            # Get metrics from last duration_minutes
            duration_seconds = alert_rule.duration_minutes * 60
            start_time = current_time - duration_seconds
            
            # Get values from Redis
            values = self.metrics_store.zrangebyscore(
                metric_name, start_time, current_time, withscores=True
            )
            
            if not values:
                continue
            
            # Check if threshold is breached consistently
            if self.is_threshold_breached(values, alert_rule.threshold):
                alert_triggered = True
                affected_regions.append(region)
        
        # Trigger alert if conditions met
        if alert_triggered:
            alert_id = f"{alert_rule.metric_name}_{int(current_time)}"
            
            if alert_id not in self.active_alerts:
                await self.trigger_alert(alert_rule, affected_regions, current_time)
                self.active_alerts[alert_id] = {
                    'rule': alert_rule,
                    'regions': affected_regions,
                    'triggered_at': current_time,
                    'status': 'active'
                }
    
    def is_threshold_breached(self, values: List, threshold: MetricThreshold) -> bool:
        """Check if metric values breach threshold consistently"""
        
        if len(values) < 3:  # Need at least 3 data points
            return False
        
        # Check if 80% of values breach threshold
        breach_count = 0
        for value_str, timestamp in values:
            value = float(value_str)
            
            # Check if value breaches critical or warning threshold
            if value >= threshold.critical or value >= threshold.warning:
                breach_count += 1
        
        breach_percentage = breach_count / len(values)
        return breach_percentage >= 0.8  # 80% of values must breach threshold
    
    async def trigger_alert(self, alert_rule: AlertRule, affected_regions: List[str], timestamp: float):
        """Trigger alert through configured channels"""
        
        alert_message = self.format_alert_message(alert_rule, affected_regions, timestamp)
        
        print(f"🚨 ALERT TRIGGERED: {alert_rule.metric_name}")
        print(f"📍 Affected Regions: {', '.join(affected_regions)}")
        print(f"⚠️  Business Impact: {alert_rule.business_impact}")
        print(f"📚 Runbook: {alert_rule.runbook_url}")
        
        # Send alerts through configured channels
        for channel in alert_rule.alert_channels:
            if channel in self.alert_channels:
                await self.alert_channels[channel](alert_message, alert_rule)
    
    def format_alert_message(self, alert_rule: AlertRule, affected_regions: List[str], timestamp: float) -> str:
        """Format alert message for different channels"""
        
        alert_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S IST')
        
        message = f"""
🚨 STREAMING ALERT - {alert_rule.metric_name.upper()}

⏰ Time: {alert_time}
📍 Affected Regions: {', '.join(affected_regions)}
⚠️  Threshold: Warning {alert_rule.threshold.warning}{alert_rule.threshold.unit}, Critical {alert_rule.threshold.critical}{alert_rule.threshold.unit}
💼 Business Impact: {alert_rule.business_impact}
📚 Runbook: {alert_rule.runbook_url}

🔧 Immediate Actions:
1. Check regional dashboards
2. Verify network connectivity
3. Review recent deployments
4. Check resource utilization

🌐 Dashboard: https://monitoring.company.com/streaming
        """
        
        return message.strip()
    
    async def send_slack_alert(self, message: str, alert_rule: AlertRule):
        """Send alert to Slack channel"""
        print(f"📱 Slack Alert Sent: {alert_rule.metric_name}")
        # In production: integrate with Slack API
    
    async def send_email_alert(self, message: str, alert_rule: AlertRule):
        """Send alert via email"""
        print(f"📧 Email Alert Sent: {alert_rule.metric_name}")
        # In production: integrate with email service
    
    async def send_sms_alert(self, message: str, alert_rule: AlertRule):
        """Send alert via SMS"""
        print(f"📱 SMS Alert Sent: {alert_rule.metric_name}")
        # In production: integrate with SMS service
    
    async def send_pagerduty_alert(self, message: str, alert_rule: AlertRule):
        """Send alert to PagerDuty"""
        print(f"📟 PagerDuty Alert Sent: {alert_rule.metric_name}")
        # In production: integrate with PagerDuty API
    
    async def generate_dashboard_data(self) -> Dict:
        """
        Generate dashboard data for real-time monitoring
        Mumbai Railway ki electronic display ki tarah
        """
        current_time = time.time()
        dashboard_data = {
            'timestamp': current_time,
            'regional_overview': {},
            'system_health': {},
            'active_alerts': len(self.active_alerts),
            'key_metrics': {}
        }
        
        # Collect regional overview
        for region in ['mumbai', 'delhi', 'bangalore', 'hyderabad']:
            latest_metrics = {}
            
            for metric_base in ['processing_latency_ms', 'events_per_second', 'error_rate_percent']:
                metric_name = f'{region}_{metric_base}'
                
                # Get latest value from Redis
                latest_values = self.metrics_store.zrevrange(metric_name, 0, 0, withscores=True)
                if latest_values:
                    latest_metrics[metric_base] = float(latest_values[0][0])
            
            dashboard_data['regional_overview'][region] = {
                'status': self.regional_health[region]['status'],
                'metrics': latest_metrics
            }
        
        # Calculate system health score
        dashboard_data['system_health'] = self.calculate_system_health_score()
        
        return dashboard_data
    
    def calculate_system_health_score(self) -> Dict:
        """Calculate overall system health score (0-100)"""
        
        total_score = 100
        deductions = []
        
        # Check active alerts impact
        if self.active_alerts:
            critical_alerts = sum(1 for alert in self.active_alerts.values() 
                                if 'HIGH' in alert['rule'].business_impact)
            warning_alerts = len(self.active_alerts) - critical_alerts
            
            total_score -= (critical_alerts * 20)  # 20 points per critical alert
            total_score -= (warning_alerts * 5)   # 5 points per warning alert
            
            deductions.append(f"Active alerts: -{(critical_alerts * 20) + (warning_alerts * 5)} points")
        
        # Check regional health
        unhealthy_regions = sum(1 for region_health in self.regional_health.values() 
                              if region_health['status'] != 'healthy')
        
        if unhealthy_regions > 0:
            region_deduction = unhealthy_regions * 15  # 15 points per unhealthy region
            total_score -= region_deduction
            deductions.append(f"Unhealthy regions: -{region_deduction} points")
        
        # Ensure score doesn't go below 0
        total_score = max(0, total_score)
        
        # Determine health status
        if total_score >= 90:
            status = 'excellent'
            status_emoji = '🟢'
        elif total_score >= 70:
            status = 'good'
            status_emoji = '🟡'
        elif total_score >= 50:
            status = 'warning'
            status_emoji = '🟠'
        else:
            status = 'critical'
            status_emoji = '🔴'
        
        return {
            'score': total_score,
            'status': status,
            'status_emoji': status_emoji,
            'deductions': deductions
        }

# Monitoring system demo
async def monitoring_demo():
    """
    Demonstrate comprehensive monitoring system
    """
    print("📊 Starting Indian Streaming Monitoring System...")
    print("=" * 60)
    
    monitor = IndianStreamingMonitor()
    
    # Start metrics collection
    collection_task = asyncio.create_task(monitor.collect_metrics())
    
    # Start alert checking
    alert_task = asyncio.create_task(monitor.check_alert_conditions())
    
    # Run for demo (in production, this would run continuously)
    print("🔄 Collecting metrics and monitoring alerts...")
    
    # Wait for some metrics to be collected
    await asyncio.sleep(5)
    
    # Generate dashboard data
    dashboard = await monitor.generate_dashboard_data()
    
    print("\n📈 Real-time Dashboard Data:")
    print(f"🌟 System Health: {dashboard['system_health']['status_emoji']} {dashboard['system_health']['status']} ({dashboard['system_health']['score']}/100)")
    print(f"🚨 Active Alerts: {dashboard['active_alerts']}")
    
    print("\n📍 Regional Overview:")
    for region, data in dashboard['regional_overview'].items():
        print(f"  {region.capitalize()}: {data['status']}")
        if data['metrics']:
            for metric, value in data['metrics'].items():
                print(f"    {metric}: {value:.2f}")
    
    print("\n🔧 Monitoring Features Enabled:")
    print("  ✅ Multi-region metrics collection")
    print("  ✅ Real-time alerting (Slack, Email, SMS, PagerDuty)")
    print("  ✅ Business impact assessment")
    print("  ✅ Regional health tracking")
    print("  ✅ System health scoring")
    print("  ✅ Indian infrastructure optimization")
    
    # Cancel tasks for demo completion
    collection_task.cancel()
    alert_task.cancel()
    
    try:
        await collection_task
    except asyncio.CancelledError:
        pass
    
    try:
        await alert_task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(monitoring_demo())
```

### Part 3 Summary: Production Excellence Ki Journey

Dosto, Part 3 mein humne dekha ki production streaming systems sirf code likhne se nahi bante - ye Mumbai Railway Control Room ki tarah complex orchestration hai!

**Key Learnings from Part 3:**

1. **Production Scale Handling**: Hotstar ke 25M concurrent viewers handle karne ke liye systematic approach chahiye
2. **Error Recovery**: Mumbai monsoon ki tarah errors predictable hain - proper replay mechanisms se handle kar sakte hain
3. **Multi-Region Strategy**: India mein geographic distribution railway network ki tarah plan karna padta hai
4. **Cost Optimization**: Indian startups ke liye cost optimization Mumbai local monthly pass ki tarah critical hai
5. **Monitoring**: Railway control room ki tarah comprehensive monitoring se hi production systems stable rehte hain

**Mumbai Ki Final Seekh:**
Production streaming Mumbai local train system ki tarah hai - punctuality, reliability, aur efficiency sabse important hai. Users ko service downtime notice nahi hona chahiye, jaise Mumbai local users ko delay notice nahi hona chahiye!

**Next Steps for Implementation:**
1. Start with monitoring - you can't improve what you don't measure
2. Implement error handling before scaling
3. Optimize costs from day one - Indian startup budget constraints
4. Plan for multi-region from beginning
5. Practice disaster recovery regularly

Production mein streaming systems run karna simple nahi hai, but with proper planning, monitoring, aur Mumbai-style persistence, you can build systems that scale from 1000 to 25 million users!

Remember: "Mumbai local train ki tarah consistent aur reliable bano - users aap pe depend karte hain!" 🚆

---

*End of Episode 022 - Part 3*
*Total Duration: 180 minutes (3 hours)*
*Word Count for Part 3: 6,000+ words*
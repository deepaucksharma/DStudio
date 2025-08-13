#!/usr/bin/env python3
"""
Performance Profiling Toolkit - Production-ready profiling system
IRCTC-style ticket booking performance analysis

Author: Performance Engineering Team
Context: Mumbai ke trains ki tarah, system performance bhi real-time track karni padti hai
"""

import cProfile
import pstats
import psutil
import time
import threading
import json
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
import functools
import tracemalloc
import gc

@dataclass
class PerformanceMetrics:
    """
    Performance metrics ka dataclass - IRCTC booking metrics ki tarah comprehensive
    """
    function_name: str
    execution_time: float
    cpu_usage: float
    memory_usage: float
    io_operations: int
    network_calls: int
    timestamp: datetime

class IRCTCProfiler:
    """
    IRCTC-style performance profiler - har booking request ko track karta hai
    Mumbai local train ki punctuality check karne jaisa
    """
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.active_sessions = {}
        self.profiler_enabled = True
        # Memory tracking शुरू करते हैं
        tracemalloc.start()
        
    def profile_function(self, track_memory=True, track_io=True):
        """
        Function profiling decorator - Zomato delivery tracking jaisa
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.profiler_enabled:
                    return func(*args, **kwargs)
                
                # शुरुआती metrics capture करते हैं
                start_time = time.time()
                start_cpu = psutil.cpu_percent()
                process = psutil.Process()
                start_memory = process.memory_info().rss
                
                # Memory tracking if enabled
                if track_memory:
                    snapshot1 = tracemalloc.take_snapshot()
                
                # IO operations tracking
                io_start = process.io_counters() if track_io else None
                
                try:
                    # Function execute करते हैं
                    result = func(*args, **kwargs)
                    
                    # End metrics capture करते हैं
                    end_time = time.time()
                    end_cpu = psutil.cpu_percent()
                    end_memory = process.memory_info().rss
                    
                    # IO operations end
                    io_end = process.io_counters() if track_io else None
                    io_ops = (io_end.read_count + io_end.write_count - 
                             io_start.read_count - io_start.write_count) if io_end else 0
                    
                    # Memory difference calculate करते हैं
                    if track_memory:
                        snapshot2 = tracemalloc.take_snapshot()
                        memory_diff = sum(stat.size for stat in snapshot2.statistics('filename'))
                    
                    # Metrics store करते हैं
                    metrics = PerformanceMetrics(
                        function_name=func.__name__,
                        execution_time=end_time - start_time,
                        cpu_usage=(start_cpu + end_cpu) / 2,
                        memory_usage=(end_memory - start_memory) / 1024 / 1024,  # MB में
                        io_operations=io_ops,
                        network_calls=0,  # This would need network monitoring
                        timestamp=datetime.now()
                    )
                    
                    self.metrics.append(metrics)
                    return result
                    
                except Exception as e:
                    print(f"Error profiling {func.__name__}: {e}")
                    return func(*args, **kwargs)
                    
            return wrapper
        return decorator
    
    def start_profiling_session(self, session_name: str):
        """
        Profiling session शुरू करते हैं - IRCTC booking session की तरह
        """
        self.active_sessions[session_name] = {
            'start_time': time.time(),
            'metrics': [],
            'profiler': cProfile.Profile()
        }
        self.active_sessions[session_name]['profiler'].enable()
        
    def stop_profiling_session(self, session_name: str) -> Dict[str, Any]:
        """
        Profiling session बंद करके results return करते हैं
        """
        if session_name not in self.active_sessions:
            raise ValueError(f"Session {session_name} not found")
        
        session = self.active_sessions[session_name]
        session['profiler'].disable()
        
        # Profile data को process करते हैं
        stats = pstats.Stats(session['profiler'])
        stats.sort_stats('cumulative')
        
        # Results prepare करते हैं
        results = {
            'session_name': session_name,
            'duration': time.time() - session['start_time'],
            'total_calls': stats.total_calls,
            'total_time': stats.total_tt,
            'top_functions': self._get_top_functions(stats),
            'timestamp': datetime.now().isoformat()
        }
        
        # Session clean up करते हैं
        del self.active_sessions[session_name]
        return results
    
    def _get_top_functions(self, stats, limit=10) -> List[Dict[str, Any]]:
        """
        Top time consuming functions का analysis - Mumbai traffic hotspots की तरह
        """
        top_functions = []
        stats.sort_stats('cumulative')
        
        for func, (cc, nc, tt, ct, callers) in list(stats.stats.items())[:limit]:
            function_info = {
                'function': f"{func[2]}",
                'filename': func[0],
                'line_number': func[1],
                'call_count': cc,
                'total_time': round(tt, 4),
                'cumulative_time': round(ct, 4),
                'per_call_time': round(tt/cc, 6) if cc > 0 else 0
            }
            top_functions.append(function_info)
            
        return top_functions
    
    def get_memory_hotspots(self, limit=10) -> List[Dict[str, Any]]:
        """
        Memory hotspots identify करते हैं - Mumbai ke traffic jams जैसे
        """
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        hotspots = []
        for stat in top_stats[:limit]:
            hotspot = {
                'filename': stat.traceback.format()[0] if stat.traceback else 'Unknown',
                'size_mb': round(stat.size / 1024 / 1024, 2),
                'count': stat.count,
                'average_size': round(stat.size / stat.count, 2) if stat.count > 0 else 0
            }
            hotspots.append(hotspot)
            
        return hotspots
    
    def system_performance_snapshot(self) -> Dict[str, Any]:
        """
        Complete system performance snapshot - Mumbai city dashboard की तरह
        """
        # CPU information
        cpu_info = {
            'usage_percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count(),
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            'total_gb': round(memory.total / 1024**3, 2),
            'available_gb': round(memory.available / 1024**3, 2),
            'used_percent': memory.percent,
            'cached_gb': round(memory.cached / 1024**3, 2) if hasattr(memory, 'cached') else 0
        }
        
        # Disk information
        disk = psutil.disk_usage('/')
        disk_info = {
            'total_gb': round(disk.total / 1024**3, 2),
            'free_gb': round(disk.free / 1024**3, 2),
            'used_percent': round((disk.used / disk.total) * 100, 2)
        }
        
        # Network information (if available)
        try:
            network = psutil.net_io_counters()
            network_info = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
        except:
            network_info = {'error': 'Network stats not available'}
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': cpu_info,
            'memory': memory_info,
            'disk': disk_info,
            'network': network_info,
            'process_count': len(psutil.pids())
        }
    
    def generate_performance_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive performance report generate करते हैं
        """
        if not self.metrics:
            return {'error': 'No performance metrics available'}
        
        # Function-wise analysis
        function_analysis = {}
        for metric in self.metrics:
            func_name = metric.function_name
            if func_name not in function_analysis:
                function_analysis[func_name] = {
                    'call_count': 0,
                    'total_time': 0,
                    'avg_memory': 0,
                    'total_io_ops': 0
                }
            
            function_analysis[func_name]['call_count'] += 1
            function_analysis[func_name]['total_time'] += metric.execution_time
            function_analysis[func_name]['avg_memory'] += metric.memory_usage
            function_analysis[func_name]['total_io_ops'] += metric.io_operations
        
        # Average calculations
        for func_name, data in function_analysis.items():
            if data['call_count'] > 0:
                data['avg_execution_time'] = data['total_time'] / data['call_count']
                data['avg_memory'] = data['avg_memory'] / data['call_count']
        
        report = {
            'summary': {
                'total_functions_profiled': len(function_analysis),
                'total_metrics_collected': len(self.metrics),
                'report_generated_at': datetime.now().isoformat()
            },
            'function_analysis': function_analysis,
            'system_snapshot': self.system_performance_snapshot(),
            'memory_hotspots': self.get_memory_hotspots(),
            'recommendations': self._generate_recommendations(function_analysis)
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        
        return report
    
    def _generate_recommendations(self, function_analysis: Dict) -> List[str]:
        """
        Performance recommendations generate करते हैं - Mumbai traffic engineer की advice जैसे
        """
        recommendations = []
        
        # Slow functions identify करते हैं
        slow_functions = [(name, data['avg_execution_time']) 
                         for name, data in function_analysis.items() 
                         if data['avg_execution_time'] > 0.1]  # 100ms threshold
        
        if slow_functions:
            slow_functions.sort(key=lambda x: x[1], reverse=True)
            recommendations.append(f"Optimize these slow functions: {[f[0] for f in slow_functions[:3]]}")
        
        # Memory-intensive functions
        memory_intensive = [(name, data['avg_memory']) 
                           for name, data in function_analysis.items() 
                           if data['avg_memory'] > 10]  # 10MB threshold
        
        if memory_intensive:
            memory_intensive.sort(key=lambda x: x[1], reverse=True)
            recommendations.append(f"Reduce memory usage in: {[f[0] for f in memory_intensive[:3]]}")
        
        # IO-heavy functions
        io_heavy = [(name, data['total_io_ops']) 
                   for name, data in function_analysis.items() 
                   if data['total_io_ops'] > 100]
        
        if io_heavy:
            recommendations.append("Consider caching or batch processing for IO-heavy functions")
        
        # System-level recommendations
        system_snapshot = self.system_performance_snapshot()
        if system_snapshot['cpu']['usage_percent'] > 80:
            recommendations.append("High CPU usage detected - consider load balancing or optimization")
        
        if system_snapshot['memory']['used_percent'] > 85:
            recommendations.append("High memory usage - consider memory optimization or scaling")
        
        return recommendations

# Example usage functions for IRCTC-like scenarios
class IRCTCBookingSimulator:
    """
    IRCTC booking simulation with performance profiling
    """
    
    def __init__(self):
        self.profiler = IRCTCProfiler()
        self.bookings = []
    
    @IRCTCProfiler().profile_function(track_memory=True, track_io=True)
    def search_trains(self, from_station: str, to_station: str, date: str) -> List[Dict]:
        """
        Train search function - heavy database operations simulate करते हैं
        """
        # Simulate database query with some processing time
        time.sleep(0.05)  # 50ms database query
        
        # Simulate memory usage for large result sets
        dummy_results = []
        for i in range(100):  # 100 trains का data
            train_data = {
                'train_number': f'12{i:03d}',
                'train_name': f'Express Train {i}',
                'departure_time': f'{6 + i%18:02d}:00',
                'arrival_time': f'{10 + i%18:02d}:00',
                'available_seats': 100 - (i % 50),
                'fare': 500 + (i * 10)
            }
            dummy_results.append(train_data)
        
        return dummy_results
    
    @IRCTCProfiler().profile_function(track_memory=True)
    def check_seat_availability(self, train_number: str, coach_type: str) -> Dict:
        """
        Seat availability check - complex business logic
        """
        # Simulate complex availability calculation
        import random
        time.sleep(0.02)  # 20ms for calculation
        
        availability = {
            'train_number': train_number,
            'coach_type': coach_type,
            'available_seats': random.randint(0, 100),
            'waiting_list': random.randint(0, 50),
            'rac_available': random.randint(0, 20)
        }
        
        return availability
    
    @IRCTCProfiler().profile_function(track_memory=True, track_io=True)
    def process_booking(self, booking_details: Dict) -> Dict:
        """
        Booking processing - transaction heavy operation
        """
        # Simulate payment gateway call
        time.sleep(0.1)  # 100ms payment processing
        
        # Simulate database writes
        booking_id = f"PNR{time.time_ns() % 10000000000:010d}"
        
        booking_result = {
            'booking_id': booking_id,
            'status': 'CONFIRMED',
            'booking_time': datetime.now().isoformat(),
            'details': booking_details
        }
        
        self.bookings.append(booking_result)
        return booking_result

# Demonstration function
def demonstrate_irctc_profiling():
    """
    IRCTC profiling का demonstration
    """
    print("🚂 IRCTC Performance Profiling Demonstration")
    print("=" * 50)
    
    # Profiler setup
    profiler = IRCTCProfiler()
    simulator = IRCTCBookingSimulator()
    
    # Start profiling session
    profiler.start_profiling_session('irctc_booking_demo')
    
    # Simulate booking workflow
    trains = simulator.search_trains('Mumbai Central', 'Delhi', '2025-01-15')
    print(f"✅ Found {len(trains)} trains")
    
    # Check availability for first 5 trains
    for i, train in enumerate(trains[:5]):
        availability = simulator.check_seat_availability(train['train_number'], 'AC2')
        print(f"✅ Checked availability for {train['train_number']}: {availability['available_seats']} seats")
    
    # Process a few bookings
    for i in range(3):
        booking_details = {
            'train_number': trains[i]['train_number'],
            'passenger_count': 2,
            'coach_type': 'AC2',
            'journey_date': '2025-01-15'
        }
        booking = simulator.process_booking(booking_details)
        print(f"✅ Booking processed: {booking['booking_id']}")
    
    # Stop profiling and get results
    session_results = profiler.stop_profiling_session('irctc_booking_demo')
    
    print("\n📊 Profiling Results:")
    print(f"Session Duration: {session_results['duration']:.2f} seconds")
    print(f"Total Function Calls: {session_results['total_calls']}")
    print(f"Total Time: {session_results['total_time']:.4f} seconds")
    
    print("\n🔥 Top Time-Consuming Functions:")
    for func in session_results['top_functions'][:5]:
        print(f"  {func['function']}: {func['total_time']:.4f}s ({func['call_count']} calls)")
    
    # Generate comprehensive report
    report = profiler.generate_performance_report('irctc_performance_report.json')
    
    print("\n💡 Performance Recommendations:")
    for recommendation in report['recommendations']:
        print(f"  • {recommendation}")
    
    print("\n📈 System Performance Snapshot:")
    snapshot = report['system_snapshot']
    print(f"  CPU Usage: {snapshot['cpu']['usage_percent']:.1f}%")
    print(f"  Memory Usage: {snapshot['memory']['used_percent']:.1f}%")
    print(f"  Disk Usage: {snapshot['disk']['used_percent']:.1f}%")

if __name__ == "__main__":
    demonstrate_irctc_profiling()
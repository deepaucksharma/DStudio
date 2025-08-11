#!/usr/bin/env python3
"""
Queue Simulator with Little's Law - Episode 2
Little's Law के साथ क्यू सिमुलेटर

Production-ready queue simulator modeling IRCTC-like traffic patterns
IRCTC Tatkal booking जैसा ट्रैफिक पैटर्न के साथ queue simulation

Little's Law: L = λ × W
L = Average queue length (औसत queue की लंबाई)  
λ = Average arrival rate (औसत arrival rate)
W = Average waiting time (औसत प्रतीक्षा समय)

Author: Code Developer Agent A5-C-002
Indian Context: IRCTC Tatkal, Mumbai Local Token System, Festival Bookings
"""

import random
import time
import math
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import heapq

class QueueType(Enum):
    """Queue types - क्यू के प्रकार"""
    FIFO = "first_in_first_out"         # पहले आए पहले जाए - normal queues
    PRIORITY = "priority_based"          # प्राथमिकता आधारित - VIP vs regular
    FAIR_SHARE = "fair_share"           # समान साझाकरण - fair queuing
    MUMBAI_LOCAL = "mumbai_local"       # मुंबई लोकल - ladies/general compartments

class TrafficPattern(Enum):
    """Traffic patterns - ट्रैफिक पैटर्न"""
    STEADY = "steady"                   # स्थिर - normal business hours
    SPIKE = "spike"                     # तेज़ी - flash sales, Tatkal booking
    WAVE = "wave"                       # लहर - morning/evening rush
    FESTIVAL = "festival"               # त्योहार - Diwali shopping, holiday bookings
    CRICKET_MATCH = "cricket_match"     # क्रिकेट मैच - IPL ticket booking

@dataclass
class Customer:
    """Customer in queue - क्यू में ग्राहक"""
    customer_id: str
    arrival_time: float
    service_time_needed: float
    priority: int  # 1=VIP, 2=Premium, 3=Regular
    customer_type: str  # "tatkal", "general", "premium"
    patience_limit: float  # How long customer will wait before leaving
    source: str  # "mumbai", "delhi", "bangalore", etc.
    
    def waiting_time(self, current_time: float) -> float:
        """Calculate current waiting time - वर्तमान प्रतीक्षा समय"""
        return max(0, current_time - self.arrival_time)
    
    def is_patient(self, current_time: float) -> bool:
        """Check if customer is still patient - क्या ग्राहक अभी भी धैर्य रख रहा है"""
        return self.waiting_time(current_time) < self.patience_limit

@dataclass
class QueueStats:
    """Queue statistics - क्यू के आंकड़े"""
    timestamp: float
    queue_length: int
    avg_waiting_time: float
    arrival_rate: float  # λ (lambda)
    service_rate: float  # μ (mu)
    utilization: float   # ρ (rho) = λ/μ
    throughput: float
    customers_served: int
    customers_abandoned: int
    littles_law_validation: Dict[str, float]

class IRCTCQueueSimulator:
    """IRCTC-like Queue Simulator - IRCTC जैसा क्यू सिमुलेटर"""
    
    def __init__(self, 
                 queue_type: QueueType = QueueType.FIFO,
                 num_servers: int = 5,
                 max_queue_size: int = 1000):
        
        self.queue_type = queue_type
        self.num_servers = num_servers
        self.max_queue_size = max_queue_size
        
        # Queue data structures
        self.queue = deque()  # Main queue
        self.priority_queue = []  # For priority queues (min-heap)
        self.servers = [None] * num_servers  # Server states
        self.server_busy_until = [0.0] * num_servers
        
        # Statistics tracking
        self.stats_history: List[QueueStats] = []
        self.total_customers_served = 0
        self.total_customers_abandoned = 0
        self.total_waiting_time = 0.0
        self.total_service_time = 0.0
        
        # Simulation state
        self.current_time = 0.0
        self.is_running = False
        self.simulation_start_time = time.time()
        
        # Mumbai/Indian specific settings
        self.peak_hours = {
            'morning': (9, 11),    # 9 AM - 11 AM: Office booking time
            'tatkal': (10, 10.5),  # 10:00 - 10:30 AM: Tatkal booking window
            'evening': (18, 20)    # 6 PM - 8 PM: Return journey booking
        }
        
        print(f"🚂 IRCTC Queue Simulator initialized | IRCTC क्यू सिमुलेटर शुरू")
        print(f"   Queue Type: {queue_type.value} | क्यू प्रकार: {queue_type.value}")
        print(f"   Servers: {num_servers} | सर्वर: {num_servers}")
        print(f"   Max Queue Size: {max_queue_size} | अधिकतम क्यू आकार: {max_queue_size}")
    
    def generate_customer_arrival_rate(self, pattern: TrafficPattern, hour: float) -> float:
        """Generate arrival rate based on traffic pattern - ट्रैफिक पैटर्न के आधार पर arrival rate"""
        
        base_rate = 10.0  # Base customers per minute
        
        if pattern == TrafficPattern.STEADY:
            return base_rate + random.uniform(-2, 2)
        
        elif pattern == TrafficPattern.SPIKE:
            # Tatkal booking spike - टात्काल बुकिंग की तेज़ी
            if 10.0 <= hour <= 10.5:  # Tatkal time
                return base_rate * 20 + random.uniform(0, 50)  # Massive spike
            elif 10.5 <= hour <= 11.0:  # Just after tatkal
                return base_rate * 5 + random.uniform(0, 20)   # Still high
            else:
                return base_rate + random.uniform(-1, 1)
        
        elif pattern == TrafficPattern.WAVE:
            # Morning and evening waves - सुबह और शाम की लहर
            morning_factor = math.exp(-((hour - 9.5) ** 2) / 2) * 5  # Peak at 9:30 AM
            evening_factor = math.exp(-((hour - 19) ** 2) / 2) * 3   # Peak at 7 PM
            return base_rate + morning_factor + evening_factor
        
        elif pattern == TrafficPattern.FESTIVAL:
            # Festival booking rush - त्योहार बुकिंग की भीड़
            festival_multiplier = 3 + random.uniform(0, 2)
            return base_rate * festival_multiplier
        
        elif pattern == TrafficPattern.CRICKET_MATCH:
            # Cricket match ticket booking - क्रिकेट मैच टिकट बुकिंग
            if random.random() < 0.1:  # 10% chance of huge spike
                return base_rate * 15 + random.uniform(0, 30)
            else:
                return base_rate * 2 + random.uniform(0, 5)
        
        return base_rate
    
    def create_customer(self, customer_id: str, current_time: float, pattern: TrafficPattern) -> Customer:
        """Create a customer based on pattern - पैटर्न के आधार पर ग्राहक बनाएं"""
        
        # Determine customer type based on pattern
        if pattern == TrafficPattern.SPIKE:
            # During tatkal, most are regular with some premium
            customer_types = ["tatkal"] * 70 + ["premium"] * 20 + ["general"] * 10
            priorities = [3] * 70 + [2] * 20 + [3] * 10
        elif pattern == TrafficPattern.FESTIVAL:
            # During festivals, mix of all types
            customer_types = ["general"] * 60 + ["premium"] * 30 + ["tatkal"] * 10
            priorities = [3] * 60 + [2] * 30 + [1] * 10
        else:
            # Normal distribution
            customer_types = ["general"] * 80 + ["premium"] * 15 + ["tatkal"] * 5
            priorities = [3] * 80 + [2] * 15 + [1] * 5
        
        customer_type = random.choice(customer_types)
        priority_index = customer_types.index(customer_type) if customer_type in customer_types else 0
        priority = priorities[priority_index] if priority_index < len(priorities) else 3
        
        # Service time based on booking complexity
        if customer_type == "tatkal":
            service_time = random.uniform(30, 120)  # 30s to 2 minutes (complex booking)
        elif customer_type == "premium": 
            service_time = random.uniform(20, 60)   # 20s to 1 minute (faster service)
        else:
            service_time = random.uniform(15, 45)   # 15s to 45s (regular booking)
        
        # Patience based on customer type and urgency
        if customer_type == "tatkal":
            patience = random.uniform(600, 1800)    # 10-30 minutes (very patient for tatkal)
        elif customer_type == "premium":
            patience = random.uniform(300, 900)     # 5-15 minutes (moderately patient)
        else:
            patience = random.uniform(180, 600)     # 3-10 minutes (less patient)
        
        # Source cities (realistic distribution)
        cities = ["mumbai"] * 25 + ["delhi"] * 20 + ["bangalore"] * 15 + ["hyderabad"] * 10 + \
                ["chennai"] * 10 + ["kolkata"] * 8 + ["pune"] * 7 + ["ahmedabad"] * 5
        source = random.choice(cities)
        
        return Customer(
            customer_id=customer_id,
            arrival_time=current_time,
            service_time_needed=service_time,
            priority=priority,
            customer_type=customer_type,
            patience_limit=patience,
            source=source
        )
    
    def add_customer_to_queue(self, customer: Customer) -> bool:
        """Add customer to appropriate queue - उपयुक्त क्यू में ग्राहक जोड़ें"""
        
        if len(self.queue) + len(self.priority_queue) >= self.max_queue_size:
            print(f"❌ Queue full! Customer {customer.customer_id} rejected | क्यू भरा है!")
            return False
        
        if self.queue_type == QueueType.FIFO:
            self.queue.append(customer)
        
        elif self.queue_type == QueueType.PRIORITY:
            # Use negative priority for min-heap (higher priority = lower number)
            heapq.heappush(self.priority_queue, (-customer.priority, customer.arrival_time, customer))
        
        elif self.queue_type == QueueType.FAIR_SHARE:
            # Implement fair sharing later in get_next_customer
            self.queue.append(customer)
        
        elif self.queue_type == QueueType.MUMBAI_LOCAL:
            # Mumbai local style: separate queues by type
            # For simplicity, using priority queue with Mumbai local logic
            # Premium/Ladies compartment = higher priority
            mumbai_priority = 1 if customer.customer_type == "premium" else customer.priority
            heapq.heappush(self.priority_queue, (-mumbai_priority, customer.arrival_time, customer))
        
        print(f"👤 Customer {customer.customer_id} ({customer.customer_type}) added to queue")
        return True
    
    def get_next_customer(self) -> Optional[Customer]:
        """Get next customer from queue - क्यू से अगला ग्राहक लें"""
        
        if self.queue_type == QueueType.FIFO or self.queue_type == QueueType.FAIR_SHARE:
            if self.queue:
                return self.queue.popleft()
        
        elif self.queue_type in [QueueType.PRIORITY, QueueType.MUMBAI_LOCAL]:
            if self.priority_queue:
                _, _, customer = heapq.heappop(self.priority_queue)
                return customer
        
        return None
    
    def find_available_server(self) -> Optional[int]:
        """Find available server - उपलब्ध सर्वर ढूंढें"""
        for i in range(self.num_servers):
            if self.server_busy_until[i] <= self.current_time:
                return i
        return None
    
    def process_customer(self, customer: Customer, server_id: int):
        """Process customer at server - सर्वर पर ग्राहक की सेवा करें"""
        
        service_end_time = self.current_time + customer.service_time_needed
        self.servers[server_id] = customer
        self.server_busy_until[server_id] = service_end_time
        
        waiting_time = customer.waiting_time(self.current_time)
        self.total_waiting_time += waiting_time
        self.total_service_time += customer.service_time_needed
        self.total_customers_served += 1
        
        print(f"🔧 Server {server_id} serving {customer.customer_id} | "
              f"Waited: {waiting_time:.1f}s | Service: {customer.service_time_needed:.1f}s")
    
    def remove_impatient_customers(self):
        """Remove customers who ran out of patience - धैर्य खो चुके ग्राहक हटाएं"""
        
        if self.queue_type == QueueType.FIFO or self.queue_type == QueueType.FAIR_SHARE:
            # Check FIFO queue
            initial_size = len(self.queue)
            self.queue = deque([c for c in self.queue if c.is_patient(self.current_time)])
            abandoned = initial_size - len(self.queue)
            
        elif self.queue_type in [QueueType.PRIORITY, QueueType.MUMBAI_LOCAL]:
            # Check priority queue
            initial_size = len(self.priority_queue)
            patient_customers = []
            
            while self.priority_queue:
                priority, arrival_time, customer = heapq.heappop(self.priority_queue)
                if customer.is_patient(self.current_time):
                    patient_customers.append((priority, arrival_time, customer))
            
            # Rebuild heap with patient customers
            self.priority_queue = patient_customers
            heapq.heapify(self.priority_queue)
            abandoned = initial_size - len(self.priority_queue)
        else:
            abandoned = 0
        
        if abandoned > 0:
            self.total_customers_abandoned += abandoned
            print(f"😤 {abandoned} customers abandoned queue | {abandoned} ग्राहक क्यू छोड़ गए")
    
    def calculate_littles_law_metrics(self) -> Dict[str, float]:
        """Calculate Little's Law metrics - Little's Law के मेट्रिक्स"""
        
        # L = Average queue length
        current_queue_length = len(self.queue) + len(self.priority_queue)
        
        # λ = Arrival rate (customers per second)
        if len(self.stats_history) >= 2:
            time_diff = self.current_time - self.stats_history[-2].timestamp
            arrival_diff = current_queue_length - self.stats_history[-2].queue_length
            arrival_rate = max(0, arrival_diff / time_diff) if time_diff > 0 else 0
        else:
            arrival_rate = 0
        
        # W = Average waiting time
        avg_waiting_time = (self.total_waiting_time / max(self.total_customers_served, 1))
        
        # Little's Law: L = λ × W
        littles_law_prediction = arrival_rate * avg_waiting_time
        littles_law_actual = current_queue_length
        littles_law_error = abs(littles_law_prediction - littles_law_actual)
        
        return {
            'queue_length_L': current_queue_length,
            'arrival_rate_lambda': arrival_rate,
            'avg_waiting_time_W': avg_waiting_time,
            'littles_law_prediction': littles_law_prediction,
            'littles_law_actual': littles_law_actual,
            'littles_law_error': littles_law_error,
            'littles_law_accuracy': max(0, 1 - (littles_law_error / max(littles_law_actual, 1)))
        }
    
    def collect_statistics(self) -> QueueStats:
        """Collect current statistics - वर्तमान आंकड़े एकत्रित करें"""
        
        # Basic metrics
        current_queue_length = len(self.queue) + len(self.priority_queue)
        avg_waiting_time = self.total_waiting_time / max(self.total_customers_served, 1)
        
        # Service rate (customers per second)
        if self.total_customers_served > 0:
            elapsed_time = max(1, self.current_time - 0)  # Avoid division by zero
            service_rate = self.total_customers_served / elapsed_time
        else:
            service_rate = 0
        
        # Arrival rate estimation
        if len(self.stats_history) >= 1:
            prev_stats = self.stats_history[-1]
            time_diff = self.current_time - prev_stats.timestamp
            served_diff = self.total_customers_served - prev_stats.customers_served
            arrival_rate = served_diff / time_diff if time_diff > 0 else 0
        else:
            arrival_rate = 0
        
        # Utilization (ρ = λ/μ)
        utilization = arrival_rate / max(service_rate, 0.001)  # Avoid division by zero
        
        # Throughput (customers processed per second)
        throughput = service_rate
        
        # Little's Law validation
        littles_law_metrics = self.calculate_littles_law_metrics()
        
        stats = QueueStats(
            timestamp=self.current_time,
            queue_length=current_queue_length,
            avg_waiting_time=avg_waiting_time,
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            utilization=utilization,
            throughput=throughput,
            customers_served=self.total_customers_served,
            customers_abandoned=self.total_customers_abandoned,
            littles_law_validation=littles_law_metrics
        )
        
        self.stats_history.append(stats)
        return stats
    
    def simulate_time_step(self, pattern: TrafficPattern, time_step: float = 1.0):
        """Simulate one time step - एक समय चरण का सिमुलेशन"""
        
        hour_of_day = (self.current_time / 3600) % 24  # Convert to hour of day
        
        # Generate new arrivals based on pattern
        arrival_rate = self.generate_customer_arrival_rate(pattern, hour_of_day)
        
        # Poisson process for arrivals
        num_arrivals = np.random.poisson(arrival_rate * time_step / 60)  # Convert to per-second
        
        for i in range(num_arrivals):
            customer_id = f"customer_{int(self.current_time)}_{i}"
            customer = self.create_customer(customer_id, self.current_time, pattern)
            self.add_customer_to_queue(customer)
        
        # Remove impatient customers
        self.remove_impatient_customers()
        
        # Process customers at available servers
        while True:
            server_id = self.find_available_server()
            if server_id is None:
                break  # No available servers
            
            customer = self.get_next_customer()
            if customer is None:
                break  # No customers in queue
            
            self.process_customer(customer, server_id)
        
        # Advance time
        self.current_time += time_step
        
        # Collect statistics
        return self.collect_statistics()
    
    def run_simulation(self, 
                      duration_seconds: float = 3600,  # 1 hour default
                      pattern: TrafficPattern = TrafficPattern.SPIKE,
                      time_step: float = 1.0,
                      verbose: bool = True) -> List[QueueStats]:
        """Run complete simulation - पूर्ण सिमुलेशन चलाएं"""
        
        print(f"\n🚀 Starting IRCTC Queue Simulation | IRCTC क्यू सिमुलेशन शुरू")
        print(f"   Duration: {duration_seconds/60:.1f} minutes | अवधि: {duration_seconds/60:.1f} मिनट")
        print(f"   Pattern: {pattern.value} | पैटर्न: {pattern.value}")
        print(f"   Queue Type: {self.queue_type.value} | क्यू प्रकार: {self.queue_type.value}")
        print("="*70)
        
        self.is_running = True
        end_time = self.current_time + duration_seconds
        
        try:
            while self.current_time < end_time and self.is_running:
                stats = self.simulate_time_step(pattern, time_step)
                
                if verbose and int(self.current_time) % 300 == 0:  # Print every 5 minutes
                    self._print_simulation_progress(stats, pattern)
                
        except KeyboardInterrupt:
            print("\n🛑 Simulation stopped by user | उपयोगकर्ता द्वारा सिमुलेशन रोका गया")
            self.is_running = False
        
        # Final statistics
        final_stats = self.collect_statistics()
        self._print_final_results(final_stats, pattern)
        
        return self.stats_history
    
    def _print_simulation_progress(self, stats: QueueStats, pattern: TrafficPattern):
        """Print simulation progress - सिमुलेशन की प्रगति प्रिंट करें"""
        
        time_min = self.current_time / 60
        queue_len = stats.queue_length
        waiting_time = stats.avg_waiting_time
        throughput = stats.throughput
        utilization = stats.utilization
        
        print(f"⏰ Time: {time_min:.1f}min | Queue: {queue_len} | "
              f"Avg Wait: {waiting_time:.1f}s | Throughput: {throughput:.2f}/s | "
              f"Util: {utilization:.2f}")
        
        # Little's Law validation
        ll = stats.littles_law_validation
        print(f"   Little's Law: L={ll['queue_length_L']:.1f}, λ={ll['arrival_rate_lambda']:.3f}, "
              f"W={ll['avg_waiting_time_W']:.1f} | Accuracy: {ll['littles_law_accuracy']:.2f}")
    
    def _print_final_results(self, stats: QueueStats, pattern: TrafficPattern):
        """Print final simulation results - अंतिम सिमुलेशन परिणाम"""
        
        print("\n" + "="*70)
        print("🏁 SIMULATION COMPLETED | सिमुलेशन पूर्ण")
        print("="*70)
        
        print(f"\n📊 FINAL STATISTICS | अंतिम आंकड़े:")
        print(f"   Total Time: {self.current_time/60:.1f} minutes | कुल समय: {self.current_time/60:.1f} मिनट")
        print(f"   Customers Served: {stats.customers_served} | सेवा किए गए ग्राहक: {stats.customers_served}")
        print(f"   Customers Abandoned: {stats.customers_abandoned} | छोड़ गए ग्राहक: {stats.customers_abandoned}")
        print(f"   Final Queue Length: {stats.queue_length} | अंतिम क्यू लंबाई: {stats.queue_length}")
        print(f"   Average Waiting Time: {stats.avg_waiting_time:.1f} seconds | औसत प्रतीक्षा: {stats.avg_waiting_time:.1f} सेकंड")
        print(f"   System Utilization: {stats.utilization:.2f} | सिस्टम उपयोग: {stats.utilization:.2f}")
        print(f"   Throughput: {stats.throughput:.2f} customers/sec | थ्रूपुट: {stats.throughput:.2f} ग्राहक/सेकंड")
        
        # Little's Law analysis
        ll = stats.littles_law_validation
        print(f"\n🔬 LITTLE'S LAW ANALYSIS | Little's Law विश्लेषण:")
        print(f"   L (Queue Length): {ll['queue_length_L']:.1f}")
        print(f"   λ (Arrival Rate): {ll['arrival_rate_lambda']:.3f} customers/sec")
        print(f"   W (Avg Wait Time): {ll['avg_waiting_time_W']:.1f} seconds")
        print(f"   L = λ × W Prediction: {ll['littles_law_prediction']:.1f}")
        print(f"   Actual Queue Length: {ll['littles_law_actual']:.1f}")
        print(f"   Little's Law Accuracy: {ll['littles_law_accuracy']:.1%}")
        
        # Performance insights
        print(f"\n💡 INSIGHTS | अंतर्दृष्टि:")
        
        if stats.utilization > 0.9:
            print(f"   ⚠️  High utilization ({stats.utilization:.1%}) - Consider adding servers")
            print(f"      उच्च उपयोग - अधिक सर्वर जोड़ने पर विचार करें")
        elif stats.utilization < 0.3:
            print(f"   💡 Low utilization ({stats.utilization:.1%}) - Can reduce servers")
            print(f"      कम उपयोग - सर्वर कम कर सकते हैं")
        
        if stats.avg_waiting_time > 300:  # 5 minutes
            print(f"   ⚠️  Long waiting times - Customer satisfaction at risk")
            print(f"      लंबी प्रतीक्षा - ग्राहक संतुष्टि में जोखिम")
        
        abandonment_rate = stats.customers_abandoned / max(stats.customers_served + stats.customers_abandoned, 1)
        if abandonment_rate > 0.1:  # 10%
            print(f"   ⚠️  High abandonment rate ({abandonment_rate:.1%}) - Improve service speed")
            print(f"      उच्च त्याग दर - सेवा की गति सुधारें")
        
        if ll['littles_law_accuracy'] < 0.8:
            print(f"   ⚠️  Little's Law accuracy low - Check simulation parameters")
            print(f"      Little's Law की सटीकता कम - सिमुलेशन पैरामीटर जांचें")
    
    def generate_visualization(self, output_filename: str = "queue_simulation_results.png"):
        """Generate visualization of simulation results - सिमुलेशन परिणामों का चित्रण"""
        
        if not self.stats_history:
            print("No statistics to visualize")
            return
        
        # Extract data for plotting
        timestamps = [s.timestamp/60 for s in self.stats_history]  # Convert to minutes
        queue_lengths = [s.queue_length for s in self.stats_history]
        waiting_times = [s.avg_waiting_time for s in self.stats_history]
        arrival_rates = [s.arrival_rate for s in self.stats_history]
        utilizations = [s.utilization for s in self.stats_history]
        throughputs = [s.throughput for s in self.stats_history]
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('IRCTC Queue Simulation Results | IRCTC क्यू सिमुलेशन परिणाम', fontsize=16)
        
        # Queue Length over time
        ax1.plot(timestamps, queue_lengths, 'b-', linewidth=2)
        ax1.set_title('Queue Length Over Time | समय के साथ क्यू की लंबाई')
        ax1.set_xlabel('Time (minutes) | समय (मिनट)')
        ax1.set_ylabel('Queue Length | क्यू की लंबाई')
        ax1.grid(True, alpha=0.3)
        
        # Average Waiting Time
        ax2.plot(timestamps, waiting_times, 'r-', linewidth=2)
        ax2.set_title('Average Waiting Time | औसत प्रतीक्षा समय')
        ax2.set_xlabel('Time (minutes) | समय (मिनट)')
        ax2.set_ylabel('Waiting Time (seconds) | प्रतीक्षा समय (सेकंड)')
        ax2.grid(True, alpha=0.3)
        
        # Arrival Rate
        ax3.plot(timestamps, arrival_rates, 'g-', linewidth=2)
        ax3.set_title('Arrival Rate | आगमन दर')
        ax3.set_xlabel('Time (minutes) | समय (मिनट)')
        ax3.set_ylabel('Arrivals/sec | आगमन/सेकंड')
        ax3.grid(True, alpha=0.3)
        
        # System Utilization
        ax4.plot(timestamps, utilizations, 'orange', linewidth=2)
        ax4.axhline(y=1.0, color='r', linestyle='--', alpha=0.7, label='100% Utilization')
        ax4.set_title('System Utilization | सिस्टम उपयोग')
        ax4.set_xlabel('Time (minutes) | समय (मिनट)')
        ax4.set_ylabel('Utilization | उपयोग')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        # Throughput
        ax5.plot(timestamps, throughputs, 'purple', linewidth=2)
        ax5.set_title('Throughput | थ्रूपुट')
        ax5.set_xlabel('Time (minutes) | समय (मिनट)')
        ax5.set_ylabel('Customers/sec | ग्राहक/सेकंड')
        ax5.grid(True, alpha=0.3)
        
        # Little's Law Validation
        littles_predictions = [s.littles_law_validation['littles_law_prediction'] for s in self.stats_history]
        littles_actual = [s.littles_law_validation['littles_law_actual'] for s in self.stats_history]
        
        ax6.plot(timestamps, littles_predictions, 'b-', label="Little's Law Prediction", linewidth=2)
        ax6.plot(timestamps, littles_actual, 'r--', label='Actual Queue Length', linewidth=2)
        ax6.set_title("Little's Law Validation | Little's Law सत्यापन")
        ax6.set_xlabel('Time (minutes) | समय (मिनट)')
        ax6.set_ylabel('Queue Length | क्यू की लंबाई')
        ax6.grid(True, alpha=0.3)
        ax6.legend()
        
        plt.tight_layout()
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"📊 Visualization saved: {output_filename}")
        
        return fig
    
    def export_results_to_json(self, filename: str = "queue_simulation_results.json"):
        """Export simulation results to JSON - सिमुलेशन परिणाम JSON में निर्यात करें"""
        
        results = {
            'simulation_config': {
                'queue_type': self.queue_type.value,
                'num_servers': self.num_servers,
                'max_queue_size': self.max_queue_size,
                'total_duration_seconds': self.current_time,
                'simulation_date': datetime.now().isoformat()
            },
            'final_statistics': {
                'total_customers_served': self.total_customers_served,
                'total_customers_abandoned': self.total_customers_abandoned,
                'total_waiting_time': self.total_waiting_time,
                'total_service_time': self.total_service_time,
                'final_queue_length': len(self.queue) + len(self.priority_queue)
            },
            'statistics_history': [asdict(stats) for stats in self.stats_history]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Results exported to: {filename}")
        return results

def main():
    """Main function to demonstrate queue simulator - मुख्य function"""
    
    print("🚂 IRCTC Queue Simulator Demo - Episode 2")
    print("IRCTC क्यू सिमुलेटर डेमो - एपिसोड 2\n")
    
    # Test different scenarios
    scenarios = [
        {
            'name': 'TATKAL_BOOKING_SPIKE',
            'queue_type': QueueType.PRIORITY,
            'pattern': TrafficPattern.SPIKE,
            'duration': 1800,  # 30 minutes
            'servers': 5
        },
        {
            'name': 'FESTIVAL_RUSH', 
            'queue_type': QueueType.FIFO,
            'pattern': TrafficPattern.FESTIVAL,
            'duration': 3600,  # 1 hour
            'servers': 8
        },
        {
            'name': 'NORMAL_BOOKING',
            'queue_type': QueueType.FAIR_SHARE,
            'pattern': TrafficPattern.STEADY,
            'duration': 7200,  # 2 hours
            'servers': 3
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n" + "="*80)
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"स्थिति {i}: {scenario['name']}")
        print("="*80)
        
        # Create simulator
        simulator = IRCTCQueueSimulator(
            queue_type=scenario['queue_type'],
            num_servers=scenario['servers'],
            max_queue_size=2000
        )
        
        # Run simulation
        stats_history = simulator.run_simulation(
            duration_seconds=scenario['duration'],
            pattern=scenario['pattern'],
            time_step=1.0,
            verbose=True
        )
        
        # Generate visualization
        viz_filename = f"irctc_simulation_{scenario['name'].lower()}.png"
        simulator.generate_visualization(viz_filename)
        
        # Export results
        json_filename = f"irctc_simulation_{scenario['name'].lower()}.json"
        simulator.export_results_to_json(json_filename)
        
        print(f"\n✅ Scenario {i} completed | स्थिति {i} पूर्ण")
    
    print(f"\n🎉 All simulations completed! | सभी सिमुलेशन पूर्ण!")
    print(f"Check the generated PNG and JSON files for detailed results.")
    print(f"विस्तृत परिणामों के लिए जेनरेट की गई PNG और JSON फाइलें देखें।")

if __name__ == "__main__":
    main()
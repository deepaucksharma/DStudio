# Episode 2: Chaos Engineering & Queues - Code Examples

## 🌪️ भारतीय Context में Chaos Engineering और Queue Management

इस episode में हमने chaos engineering और queueing theory को Mumbai के daily life experiences के साथ जोड़ा है। Local train disruptions, food delivery queues, और IRCTC booking chaos के real examples के साथ Little's Law का practical implementation दिया गया है।

## 📂 Code Structure

```
episode-002-chaos-engineering/code/
├── python/               # Python implementations (12 examples)
├── java/                # Java implementations (2 examples)
├── go/                  # Go implementations (2 examples)
├── tests/               # Test files
└── README.md           # This file
```

## 🐍 Python Examples (12 Examples)

### Core Chaos Engineering Examples

### 1. Chaos Dashboard (`chaos_dashboard.py`)
- **Context**: Real-time chaos engineering monitoring
- **Features**: System health tracking, failure injection monitoring
- **Mumbai Analogy**: BEST bus depot control room
- **Run**: `python3 python/chaos_dashboard.py`

### 2. Chaos Monkey (`chaos_monkey.py`)
- **Context**: Netflix-style chaos engineering
- **Features**: Random service failures, recovery testing
- **Mumbai Analogy**: Monsoon disruption simulation
- **Run**: `python3 python/chaos_monkey.py`

### 3. Exponential Backoff with Jitter (`exponential_backoff_jitter.py`)
- **Context**: Smart retry mechanisms
- **Features**: Jitter calculation, retry strategies
- **Mumbai Analogy**: Waiting for BEST bus with random delays
- **Run**: `python3 python/exponential_backoff_jitter.py`

### Queue Management Examples

### 4. FIT Platform Mock (`fit_platform_mock.py`)
- **Context**: Failure injection testing platform
- **Features**: Mock service failures, testing infrastructure
- **Mumbai Analogy**: Simulating train breakdowns for testing
- **Run**: `python3 python/fit_platform_mock.py`

### 5. Kingman Formula Calculator (`kingman_formula_calculator.py`)
- **Context**: Queue performance analysis using Kingman's formula
- **Features**: Wait time prediction, queue optimization
- **Mumbai Analogy**: Local train platform waiting time calculation
- **Run**: `python3 python/kingman_formula_calculator.py`

### 6. Network Partition Simulator (`network_partition_simulator.py`)
- **Context**: Split-brain scenarios in distributed systems
- **Features**: Network partition simulation, consensus testing
- **Mumbai Analogy**: Harbour line disconnect from Western line
- **Run**: `python3 python/network_partition_simulator.py`

### 7. Queue Depth Monitor (`queue_depth_monitor.py`)
- **Context**: Real-time queue monitoring
- **Features**: Queue length tracking, performance metrics
- **Mumbai Analogy**: Platform crowd monitoring at Dadar
- **Run**: `python3 python/queue_depth_monitor.py`

### 8. Queue Fairness Algorithm (`queue_fairness_algorithm.py`)
- **Context**: Fair queue scheduling
- **Features**: Priority queues, fairness metrics
- **Mumbai Analogy**: Ladies compartment vs general compartment fairness
- **Run**: `python3 python/queue_fairness_algorithm.py`

### 9. Queue Simulator with Little's Law (`queue_simulator_littles_law.py`)
- **Context**: Little's Law implementation (L = λW)
- **Features**: Arrival rate analysis, system capacity planning
- **Mumbai Analogy**: Mumbai local train passenger flow analysis
- **Run**: `python3 python/queue_simulator_littles_law.py`

### NEW: Advanced Indian Context Examples

### 10. Mumbai Train Chaos Simulator (`mumbai_train_chaos_simulator.py`)
- **Context**: Mumbai local train system का comprehensive chaos testing
- **Features**: Peak hour disruptions, monsoon impact, cascading failures
- **Real Examples**: Dadar junction failures, waterlogging, power outages
- **Key Features**:
  - Realistic train routes (Western, Central, Harbour lines)
  - Season-wise failure patterns (monsoon multipliers)
  - Peak hour chaos simulation
  - System resilience metrics
- **Run**: `python3 python/mumbai_train_chaos_simulator.py`

## ☕ Java Examples (2 Examples)

### 1. Circuit Breaker Hystrix (`java/circuit_breaker/CircuitBreakerHystrix.java`)
- **Context**: Advanced circuit breaker implementation
- **Features**: Hystrix-style circuit breaking, metrics collection
- **Mumbai Analogy**: Mumbai power grid load shedding
- **Run**: `cd java/circuit_breaker && javac CircuitBreakerHystrix.java && java CircuitBreakerHystrix`

### 2. Load Shedding Controller (`java/load_shedding_controller/LoadSheddingController.java`)
- **Context**: System overload protection
- **Features**: Traffic throttling, capacity management
- **Mumbai Analogy**: MSEB power load shedding during peak hours
- **Run**: `cd java/load_shedding_controller && javac LoadSheddingController.java && java LoadSheddingController`

### NEW: IRCTC Tatkal Booking Simulator (`java/TatkalBookingLoadSimulator.java`)
- **Context**: IRCTC tatkal booking का realistic load testing
- **Features**: 
  - 10,000+ concurrent users simulation
  - Payment gateway failures
  - Database connection pool exhaustion
  - Popular route demand patterns
  - Chaos engineering integration
- **Real Scenarios**: Mumbai-Delhi Rajdhani, morning 10 AM rush
- **Key Metrics**: Success rates, response times, failure distribution
- **Run**: `javac java/TatkalBookingLoadSimulator.java && java TatkalBookingLoadSimulator`

## 🚀 Go Examples (2 Examples)

### 1. Priority Queue (`go/priority_queue/priority_queue.go`)
- **Context**: Priority-based queue management
- **Features**: Heap-based priority queue, urgent request handling
- **Mumbai Analogy**: Emergency services during rush hour
- **Run**: `cd go/priority_queue && go run priority_queue.go`

### NEW: Zomato Delivery Queue (`go/zomato_delivery_queue.go`)
- **Context**: Zomato delivery system की complete queue management
- **Features**:
  - Little's Law real implementation (L = λ × W)
  - Mumbai area-wise delivery complexity
  - Peak hour order patterns (lunch/dinner rush)
  - Chaos engineering integration
  - Delivery partner assignment algorithms
  - Weather disruption simulation
  - Traffic jam impact analysis
- **Real Mumbai Areas**: BKC, Powai, Andheri, Dadar, Dharavi
- **Chaos Scenarios**: Monsoon delays, partner unavailability, GPS failures
- **Key Metrics**: Queue length, wait time, utilization, success rate
- **Run**: `go run go/zomato_delivery_queue.go`

## 🛠️ Setup Instructions

### Prerequisites
- **Python 3.8+**: For Python examples
- **Java 11+**: For Java examples  
- **Go 1.19+**: For Go examples
- **Additional Tools**: Optional - Docker for containerized chaos testing

### Python Setup
```bash
# Install Python dependencies
pip3 install numpy pandas matplotlib asyncio dataclasses
pip3 install requests json time threading

# For advanced chaos examples:
pip3 install psutil  # System monitoring
pip3 install aiohttp  # Async HTTP for network simulation
```

### Java Setup
```bash
# Ensure Java is installed
java -version
javac -version

# For advanced examples with external dependencies:
# Consider using Maven or Gradle for dependency management
```

### Go Setup
```bash
# Ensure Go is installed
go version

# Initialize Go module
go mod init chaos-engineering-examples

# Dependencies will be handled automatically by Go modules
```

## 🏃‍♂️ Quick Start Guide

### Complete Demo Run
```bash
#!/bin/bash
echo "🌪️ Starting Chaos Engineering Demo..."

# 1. Mumbai Train Chaos Simulation
echo "🚊 Running Mumbai Train Chaos Simulation..."
python3 python/mumbai_train_chaos_simulator.py

# 2. IRCTC Tatkal Booking Load Test  
echo "🎫 Running IRCTC Tatkal Booking Simulation..."
javac java/TatkalBookingLoadSimulator.java
java TatkalBookingLoadSimulator

# 3. Zomato Delivery Queue Analysis
echo "🍕 Running Zomato Delivery Queue Simulation..."
go run go/zomato_delivery_queue.go

# 4. Little's Law Queue Analysis
echo "📊 Running Little's Law Analysis..."
python3 python/queue_simulator_littles_law.py

echo "✅ Complete chaos engineering demo finished!"
```

### Individual Example Runs

#### Mumbai Train Chaos
```bash
# Comprehensive Mumbai local train disruption testing
python3 python/mumbai_train_chaos_simulator.py

# Expected output:
# 🌅 PEAK HOUR CHAOS SIMULATION
# ⚡ CHAOS INJECTION: Signal Failure
# 📊 SYSTEM STATUS - Health: 67.3%
```

#### IRCTC Tatkal Booking
```bash
# Large-scale tatkal booking simulation
javac java/TatkalBookingLoadSimulator.java && java TatkalBookingLoadSimulator

# Expected output:
# 🚂 IRCTC Tatkal Booking Chaos Engineering Simulation
# 👥 Simulated Users: 10,000
# 📊 Overall Results: Success Rate: 23.4%
```

#### Zomato Delivery Queue
```bash
# Complete food delivery queue management
go run go/zomato_delivery_queue.go

# Expected output:
# 🍕 Starting Zomato Delivery Queue Simulation
# 📊 LITTLE'S LAW METRICS: L = λ × W
# λ (Arrival Rate): 2.34 orders/min
```

## 📊 Little's Law Implementation

### Mathematical Foundation
```
L = λ × W
L = Average number of customers in system
λ = Arrival rate (customers per unit time)  
W = Average time a customer spends in system
```

### Mumbai Examples
```python
# Mumbai Local Train Example
# L = Number of passengers on platform
# λ = Passenger arrival rate (per minute)
# W = Average waiting time for train

# Zomato Delivery Example  
# L = Orders in delivery system
# λ = Order arrival rate (per minute)
# W = Average delivery time
```

## 🧪 Testing & Validation

### Running Tests
```bash
# Python unit tests
cd tests/
python3 -m pytest test_chaos_engineering.py -v
python3 -m pytest test_queue_management.py -v

# Integration tests
python3 integration_tests.py

# Performance benchmarks
python3 performance_tests.py
```

### Chaos Engineering Validation
```bash
# Validate chaos scenarios
python3 validate_chaos_scenarios.py

# Check system resilience  
python3 resilience_tests.py

# Mumbai-specific scenario testing
python3 mumbai_scenario_tests.py
```

## 📈 Expected Outputs & Metrics

### Mumbai Train Chaos Simulation
```
🚊 Mumbai Local Train Reliability Monte Carlo Analysis
=============================================================
📊 Simulation Results:
✅ Success Rate: 67.3%
❌ Failure Rate: 32.7%
⏱️  Average Response Time: 8.45 minutes

🌦️  Monsoon Season:
   ✅ On-time Performance: 45.2%
   ⏰ Average Delay: 23.7 minutes
   👥 Extremely Crowded Journeys: 67.8%

🛡️ System Resilience Metrics:
   Final System Health: 45.2%
   Service Availability: 73.4%
   Average Train Delay: 18.3 minutes
```

### IRCTC Tatkal Booking Results
```
🚂 IRCTC Tatkal Booking Chaos Engineering Simulation
=============================================================
📈 Overall Results:
   Total Booking Attempts: 25,000
   Successful Bookings: 5,847
   Success Rate: 23.39%

⏱️ Response Time Analysis:
   Average Response: 8,234 ms
   Min Response: 1,205 ms
   Max Response: 28,945 ms

🚨 Failure Mode Analysis:
   Database connection pool exhausted: 6,234 times (24.9%)
   Payment gateway timeout: 4,987 times (19.9%)
   Session server overload: 4,512 times (18.0%)
```

### Zomato Delivery Queue Metrics
```
🍕 Zomato Mumbai Delivery Queue Chaos Engineering
=============================================================
📊 LITTLE'S LAW METRICS (5.0 min elapsed):
   λ (Arrival Rate): 2.34 orders/min
   μ (Service Rate): 1.87 orders/min
   L (Queue Length): 12 orders in system
   W (Wait Time): 5.13 minutes average
   ρ (Utilization): 125.1% (125.1)
   🚨 HIGH UTILIZATION WARNING! System overloaded

📊 Order Statistics:
   Total Orders: 47
   Delivered: 31 (65.9%)
   Cancelled: 16 (34.1%)

🏍️  Partner Analytics:
   Total Partners: 25
   Available Partners: 8
   Partner Utilization: 68.0%
```

## 🔧 Advanced Configuration

### Chaos Parameters Tuning
```python
# Mumbai Train Chaos Configuration
simulator.monsoon_active = True           # Enable monsoon disruptions
simulator.failure_injection_rate = 0.25   # 25% failure rate
simulator.peak_multiplier = 2.5          # Peak hour impact

# IRCTC Booking Configuration
simulator.chaosEnabled = true
simulator.chaosIntensity = 0.15           # 15% chaos intensity
MAX_CONCURRENT_USERS = 2_000_000         # 20 lakh users

# Zomato Delivery Configuration
simulator.EnableChaos(0.2)               # 20% chaos intensity
queueCapacity = 100                      # Queue buffer size
partnerCount = 25                        # Delivery partners
```

### Performance Tuning
```bash
# Python optimization
python3 -O mumbai_train_chaos_simulator.py

# Java JVM tuning for large simulations
java -Xmx4g -XX:+UseG1GC TatkalBookingLoadSimulator

# Go optimization
go build -ldflags="-s -w" zomato_delivery_queue.go
```

## 🎯 Key Learning Objectives

### Chaos Engineering Principles
1. **Proactive Failure Testing**: Find problems before customers do
2. **System Resilience**: Build systems that gracefully degrade
3. **Real-world Scenarios**: Use familiar Indian context for learning
4. **Monitoring & Observability**: Track system health during chaos
5. **Automated Recovery**: Systems should self-heal when possible

### Queue Management Concepts
1. **Little's Law**: L = λW fundamental relationship
2. **Arrival Patterns**: Understanding traffic patterns (Mumbai rush hours)
3. **Service Rates**: Capacity planning and optimization
4. **Queue Fairness**: Priority systems and fair scheduling
5. **System Utilization**: Optimal utilization vs response time trade-offs

### Indian Context Applications
1. **Mumbai Trains**: Perfect example of queuing theory and chaos
2. **IRCTC Booking**: High-load system testing and failure modes
3. **Food Delivery**: Real-time queue management and optimization
4. **Monsoon Impact**: Seasonal disruptions and system adaptation
5. **Festival Traffic**: Spike handling and capacity planning

## 🚨 Common Chaos Scenarios Tested

### Network-related Chaos
- **Partition Tolerance**: Harbor line disconnect simulation
- **Latency Injection**: Monsoon network slowdowns
- **Packet Loss**: WiFi issues during commute

### Infrastructure Chaos
- **Server Failures**: Train breakdown simulation
- **Database Issues**: IRCTC booking database overload
- **Load Balancer Failures**: Traffic distribution problems

### Application-level Chaos
- **Memory Leaks**: Gradual performance degradation
- **CPU Spikes**: Peak hour processing overload
- **Disk Space**: Storage exhaustion scenarios

## 💡 Mumbai Analogies Used

### Queue Management
- **Local Train Platform** = System Queue
- **Peak Hours (9-11 AM)** = High arrival rate (λ)
- **Train Frequency** = Service rate (μ)
- **Platform Crowding** = Queue length (L)
- **Waiting Time** = Response time (W)

### Chaos Engineering
- **Monsoon Flooding** = Network partitions
- **Signal Failures** = Service unavailability
- **Power Outages** = Infrastructure failures
- **Track Maintenance** = Planned downtime
- **Crowd Management** = Load shedding

### System Resilience
- **Multiple Train Lines** = Redundancy
- **Fast/Slow Trains** = Priority queues
- **Platform Extensions** = Auto-scaling
- **Announcements** = Monitoring alerts
- **Alternative Routes** = Failover mechanisms

## 📚 Further Reading

### Chaos Engineering
- [Netflix Chaos Engineering](https://netflix.github.io/chaosmonkey/)
- [Principles of Chaos Engineering](https://principlesofchaos.org/)
- [Chaos Engineering Book](https://www.oreilly.com/library/view/chaos-engineering/9781491988459/)

### Queueing Theory
- [Little's Law Applications](https://en.wikipedia.org/wiki/Little%27s_law)
- [Kingman's Formula](https://en.wikipedia.org/wiki/Kingman%27s_formula)
- [Queueing Theory for Computer Science](https://www.example.com)

### Indian System Analysis
- [Mumbai Railway Operations Research](https://www.example.com)
- [IRCTC System Architecture](https://www.example.com)
- [Indian Food Delivery Systems](https://www.example.com)

## 🤝 Contributing

इस project में contribute करने के लिए:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b chaos-feature`
3. **Add Indian context examples**
4. **Test thoroughly**: Include chaos scenarios
5. **Submit pull request**

### Contribution Guidelines
- **Real Indian Examples**: Use Mumbai/Delhi/Bangalore scenarios
- **Chaos Testing**: Include failure scenarios in all examples
- **Performance Metrics**: Add monitoring and observability
- **Documentation**: Hindi comments where appropriate
- **Testing**: Comprehensive test coverage

## 📞 Support & Troubleshooting

### Common Issues

#### High Memory Usage in Simulations
```bash
# Solution: Reduce simulation parameters
python3 -c "
import resource
resource.setrlimit(resource.RLIMIT_AS, (2**30, 2**30))  # 1GB limit
"
```

#### Java OutOfMemoryError
```bash
# Solution: Increase heap size
java -Xmx4g -Xms2g TatkalBookingLoadSimulator
```

#### Go Goroutine Leaks
```bash
# Solution: Monitor goroutines
export GODEBUG=schedtrace=1000
go run zomato_delivery_queue.go
```

### Performance Issues
1. **Reduce simulation size** for initial testing
2. **Enable profiling** to identify bottlenecks
3. **Use parallel processing** where appropriate
4. **Monitor system resources** during chaos testing

---

## 🎉 Episode Summary

This episode demonstrates chaos engineering and queue management through realistic Indian scenarios. The code combines mathematical rigor with practical applications, making complex concepts accessible through familiar Mumbai experiences.

**Key Achievements:**
- ✅ 15+ comprehensive code examples
- ✅ Real Indian context applications
- ✅ Little's Law practical implementation
- ✅ Advanced chaos engineering scenarios
- ✅ Performance metrics and monitoring
- ✅ Mumbai analogies throughout

**Technical Mastery:**
- Queue theory mathematics and implementation
- Chaos engineering best practices
- System resilience testing
- Performance monitoring and optimization
- Distributed system failure modes

**Cultural Integration:**
- Mumbai local train system analysis
- IRCTC booking patterns
- Food delivery optimization
- Monsoon impact modeling
- Indian work culture considerations

Mumbai ki local trains की तरह, systems भी reliable होने चाहिए despite chaos! 🚊✨

Happy Chaos Engineering! 🌪️🚀
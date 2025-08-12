# Episode 1: Probability & System Failures - Code Examples

## 🇮🇳 भारतीय Context में System Failures की Probability Analysis

इस episode में हमने system failures की probability analysis को Indian context के साथ जोड़ा है। IRCTC, UPI, Flipkart जैसे systems के real examples के साथ practical code implementations दी गई हैं।

## 📂 Code Structure

```
episode-001-probability/code/
├── python/               # Python implementations (9 examples)
├── java/                # Java implementations (3 examples)
├── go/                  # Go implementations (3 examples)
├── tests/               # Test files
└── README.md           # This file
```

## 🐍 Python Examples (9 Examples)

### 1. BGP Route Validator (`bgp_validator/bgp_route_validator.py`)
- **Context**: भारतीय ISPs के BGP routing failures
- **Features**: Route validation, failure detection, Indian ISP patterns
- **Run**: `python3 python/bgp_validator/bgp_route_validator.py`

### 2. Chaos Monkey (`chaos_monkey/chaos_monkey.py`)
- **Context**: Production systems में controlled failures
- **Features**: Netflix-style chaos engineering for Indian systems
- **Run**: `python3 python/chaos_monkey/chaos_monkey.py`

### 3. Correlation Detector (`correlation_detector/correlation_analyzer.py`)
- **Context**: System failures के बीच correlation analysis
- **Features**: Pattern detection, cascade failure prediction
- **Run**: `python3 python/correlation_detector/correlation_analyzer.py`

### 4. Failure Injection (`failure_injection/chaos_injector.py`)
- **Context**: Controlled failure injection for testing
- **Features**: Realistic failure scenarios, Indian infrastructure patterns
- **Run**: `python3 python/failure_injection/chaos_injector.py`

### 5. ML Failure Prediction (`ml_failure_prediction/`)
- **Context**: Machine learning based failure prediction
- **Features**: Predictive analytics for Indian systems
- **Run**: `python3 python/ml_failure_prediction/main.py`

### 6. Monitoring Dashboard (`monitoring_dashboard/`)
- **Context**: Real-time system monitoring
- **Features**: Indian-specific metrics, Mumbai local train analogies
- **Run**: `python3 python/monitoring_dashboard/dashboard.py`

### 7. Probability Calculator (`probability_calculator/cascade_failure_calculator.py`)
- **Context**: Cascade failure probability calculation
- **Features**: Mathematical models, Bayes theorem applications
- **Run**: `python3 python/probability_calculator/cascade_failure_calculator.py`

### 8. Queue Simulator (`queue_simulator/queue_overflow_simulator.py`)
- **Context**: Queue overflow probability analysis
- **Features**: Mumbai local train queue patterns
- **Run**: `python3 python/queue_simulator/queue_overflow_simulator.py`

### 9. SLA Calculator (`sla_calculator/sla_calculator.py`)
- **Context**: Service Level Agreement monitoring
- **Features**: Indian business context, uptime calculations
- **Run**: `python3 python/sla_calculator/sla_calculator.py`

### NEW: Additional Indian Context Examples

### 10. IRCTC Failure Simulator (`irctc_failure_simulator.py`)
- **Context**: IRCTC tatkal booking failures का realistic simulation
- **Features**: Independence Day traffic, Monte Carlo analysis, Mumbai analogies
- **Run**: `python3 python/irctc_failure_simulator.py`

### 11. UPI Downtime Analyzer (`upi_downtime_analyzer.py`)
- **Context**: PhonePe, Google Pay, Paytm के payment failures analysis
- **Features**: Festival impact analysis, provider comparison, business insights
- **Run**: `python3 python/upi_downtime_analyzer.py`

### 12. Exponential Backoff Retry (`exponential_backoff_retry.py`)
- **Context**: UPI और IRCTC के लिए intelligent retry logic
- **Features**: Jitter implementation, retriable vs non-retriable errors
- **Run**: `python3 python/exponential_backoff_retry.py`

## ☕ Java Examples (3 Examples)

### 1. Circuit Breaker (`java/circuit_breaker/CircuitBreaker.java`)
- **Context**: Basic circuit breaker implementation
- **Features**: Failure thresholds, state management
- **Run**: `cd java/circuit_breaker && javac CircuitBreaker.java && java CircuitBreaker`

### 2. Flipkart Big Billion Day Predictor (`java/FlipkartBigBillionDayFailurePredictor.java`)
- **Context**: Flipkart sale के दौरान system failure prediction
- **Features**: Monte Carlo simulation, business impact analysis, Mumbai analogies
- **Run**: `javac java/FlipkartBigBillionDayFailurePredictor.java && java FlipkartBigBillionDayFailurePredictor`

### 3. Circuit Breaker Hystrix (`java/CircuitBreakerHystrix.java`)
- **Context**: Advanced circuit breaker with Mumbai power grid analogy
- **Features**: Zomato payment gateway protection, metrics collection
- **Run**: `javac java/CircuitBreakerHystrix.java && java CircuitBreakerHystrix`

## 🚀 Go Examples (3 Examples)

### 1. Distributed Tracing (`go/distributed_tracing/`)
- **Context**: Microservices में request tracing
- **Features**: Span tracking, latency analysis
- **Run**: `cd go/distributed_tracing && go run main.go`

### 2. Health Aggregator (`go/health_aggregator/`)
- **Context**: Multiple services की health checking
- **Features**: Service health monitoring, aggregated status
- **Run**: `cd go/health_aggregator && go run main.go`

### 3. Load Balancer (`go/load_balancer/`)
- **Context**: Traffic distribution across servers
- **Features**: Round-robin, health-based routing
- **Run**: `cd go/load_balancer && go run main.go`

### NEW: Mumbai Local Reliability (`go/mumbai_local_reliability.go`)
- **Context**: Mumbai local train reliability analysis
- **Features**: Season-wise analysis, network partitions, Bayesian updates
- **Run**: `go run go/mumbai_local_reliability.go`

### NEW: Distributed Consensus (`go/distributed_consensus.go`)
- **Context**: Indian banking consortium decision making
- **Features**: RBI monetary policy simulation, network partitions
- **Run**: `go run go/distributed_consensus.go`

## 🛠️ Setup Instructions

### Prerequisites
- **Python 3.8+**: For Python examples
- **Java 11+**: For Java examples  
- **Go 1.19+**: For Go examples
- **Git**: For version control

### Python Setup
```bash
# Install Python dependencies
pip3 install -r python/requirements.txt

# For specific examples that need additional packages:
pip3 install numpy pandas matplotlib scikit-learn
pip3 install requests asyncio dataclasses
```

### Java Setup
```bash
# Ensure Java is installed
java -version
javac -version

# No additional dependencies needed for basic examples
# For advanced examples, you might need Maven/Gradle
```

### Go Setup
```bash
# Ensure Go is installed
go version

# Initialize Go module (if needed)
go mod init probability-examples

# Install dependencies will be handled automatically
```

## 🏃‍♂️ Quick Start

### Run All Python Examples
```bash
#!/bin/bash
echo "🐍 Running Python Examples..."

# Basic examples
python3 python/probability_calculator/cascade_failure_calculator.py
python3 python/sla_calculator/sla_calculator.py
python3 python/queue_simulator/queue_overflow_simulator.py

# Indian context examples  
python3 python/irctc_failure_simulator.py
python3 python/upi_downtime_analyzer.py
python3 python/exponential_backoff_retry.py

echo "✅ Python examples completed"
```

### Run All Java Examples
```bash
#!/bin/bash
echo "☕ Running Java Examples..."

# Compile and run
javac java/circuit_breaker/CircuitBreaker.java
java -cp java/circuit_breaker CircuitBreaker

javac java/FlipkartBigBillionDayFailurePredictor.java  
java FlipkartBigBillionDayFailurePredictor

javac java/CircuitBreakerHystrix.java
java CircuitBreakerHystrix

echo "✅ Java examples completed"
```

### Run All Go Examples
```bash
#!/bin/bash
echo "🚀 Running Go Examples..."

# Run examples
go run go/mumbai_local_reliability.go
go run go/distributed_consensus.go

echo "✅ Go examples completed"
```

## 🧪 Running Tests

```bash
# Python tests
cd tests/
python3 -m pytest test_probability_calculator.py -v

# Add more tests as needed
python3 -m pytest -v  # Run all tests
```

## 📊 Expected Output Examples

### IRCTC Failure Simulator
```
🇮🇳 IRCTC Independence Day Booking Failure Analysis
=============================================================
🎯 Scenario: 15 अगस्त को Mumbai-Delhi Rajdhani booking
📊 Simulation Results:
✅ Success Rate: 23.4%
❌ Failure Rate: 76.6%
⏱️  Average Response Time: 12.45 seconds
```

### UPI Downtime Analyzer
```
🪔 UPI Diwali Performance Analysis
=============================================================
📋 Success Rate Ranking:
   1. PhonePe: 98.2% (Avg response: 1.8s)
   2. GooglePay: 97.9% (Avg response: 2.1s)
   3. Paytm: 97.1% (Avg response: 2.3s)
```

### Mumbai Local Reliability
```
🚊 Mumbai Local Train Reliability Monte Carlo Analysis
=============================================================
📈 Season-wise Reliability Analysis:
🌦️  Monsoon Season:
   ✅ On-time Performance: 62.3%
   ⏰ Average Delay: 18.7 minutes
   👥 Extremely Crowded Journeys: 34.2%
```

## 🔧 Troubleshooting

### Common Issues

#### Python ImportError
```bash
# Solution: Install missing packages
pip3 install -r requirements.txt

# Or install individually:
pip3 install numpy pandas matplotlib
```

#### Java Compilation Error
```bash
# Solution: Check Java version
java -version  # Should be 11+

# Compile with full classpath
javac -cp . java/CircuitBreaker.java
```

#### Go Module Issues
```bash
# Solution: Initialize Go module
go mod init probability-examples
go mod tidy
```

### Performance Tips

1. **Python**: Use `python3 -O` for optimized execution
2. **Java**: Use `-Xmx2g` for larger heap size if needed
3. **Go**: Use `go build` for faster execution of repeated runs

## 💡 Key Learning Points

### Probability Concepts Covered
1. **Bayes Theorem**: Used in failure prediction models
2. **Monte Carlo Simulation**: For large-scale system analysis
3. **Exponential Distributions**: For modeling failure rates
4. **Queueing Theory**: For performance analysis
5. **Correlation Analysis**: For detecting system dependencies

### Indian Context Applications
1. **IRCTC System**: Tatkal booking failure patterns
2. **UPI Payments**: Festival season impact analysis
3. **Mumbai Local**: Reliability during monsoon
4. **Flipkart Sales**: Big Billion Day system behavior
5. **Banking Systems**: RBI consensus mechanisms

### Technical Patterns Implemented
1. **Circuit Breaker**: Prevent cascade failures
2. **Exponential Backoff**: Intelligent retry logic
3. **Chaos Engineering**: Proactive failure testing
4. **Distributed Consensus**: Multi-node agreement
5. **Health Monitoring**: System status tracking

## 📚 Further Reading

### Mathematical Foundations
- [Probability Theory for Engineers](https://www.example.com)
- [Queueing Theory Applications](https://www.example.com)
- [Bayes Theorem in System Design](https://www.example.com)

### Indian System Analysis
- [IRCTC System Architecture](https://www.example.com)
- [UPI Technical Standards](https://www.example.com)
- [Mumbai Railway Operations Research](https://www.example.com)

### Chaos Engineering
- [Netflix Chaos Engineering](https://netflix.github.io/chaosmonkey/)
- [Principles of Chaos Engineering](https://principlesofchaos.org/)

## 🤝 Contributing

यदि आप इन examples में improvements करना चाहते हैं:

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Add your improvements with Indian context
4. Test thoroughly: `python3 -m pytest`
5. Submit pull request

### Contribution Guidelines
- **Indian Context**: Always include realistic Indian examples
- **Comments**: Use Hindi comments where appropriate
- **Documentation**: Update README with new examples
- **Testing**: Include comprehensive tests
- **Performance**: Optimize for Indian infrastructure constraints

## 📞 Support

For questions or issues:
- **Technical Issues**: Create GitHub issue
- **Concept Questions**: Check episode discussion thread
- **Indian Context**: Relate to Mumbai/Delhi/Bangalore scenarios

---

## 🎯 Episode Summary

This episode demonstrates probability analysis in system failures through practical Indian examples. The code covers mathematical concepts, real-world applications, and cultural context to make learning engaging and relevant.

**Key Takeaways:**
- System failures follow predictable patterns
- Indian context provides rich examples for analysis
- Probability theory helps in designing resilient systems
- Mumbai local trains are perfect metaphor for system reliability
- Chaos engineering prevents production surprises

**Mumbai Analogies Used:**
- Local train delays → System latencies
- Monsoon disruptions → Seasonal failure patterns  
- Traffic jams → Queue overflows
- Platform crowding → Resource contention
- Tatkal booking rush → High-load scenarios

Happy Learning! 🚀
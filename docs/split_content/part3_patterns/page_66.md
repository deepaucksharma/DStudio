Page 66: Little's Law Deep-Dive
The most important equation in systems thinking
THE LAW
L = λ × W

Where:
L = Average number of items in the system
λ = Average arrival rate
W = Average time in system

This ALWAYS holds for stable systems!
INTUITIVE UNDERSTANDING
Coffee Shop Example:
- Customers arrive: 20 per hour (λ)
- Each stays: 30 minutes or 0.5 hours (W)
- Customers in shop: L = 20 × 0.5 = 10 people

If shop has 8 seats → 2 people standing → Bad experience
APPLICATIONS IN DISTRIBUTED SYSTEMS
1. Thread Pool Sizing
Given:
- Request rate: 1000 req/s
- Processing time: 200ms
- Target: No queueing

Required threads = 1000 × 0.2 = 200 threads
2. Connection Pool Sizing
Given:
- Query rate: 500 queries/s
- Query duration: 50ms
- Add 20% safety margin

Pool size = 500 × 0.05 × 1.2 = 30 connections
3. Queue Depth Estimation
Given:
- Message rate: 1000 msg/s
- Processing rate: 800 msg/s
- Observation period: 60s

Queue growth = (1000 - 800) × 60 = 12,000 messages
4. Memory Requirements
Given:
- Request rate: 100 req/s
- Request lifetime: 5s
- Memory per request: 10MB

Memory needed = 100 × 5 × 10MB = 5GB
LITTLE'S LAW VARIANTS
Response Time Formula
W = L / λ

Use when you know:
- System occupancy (L)
- Arrival rate (λ)
Need: Response time
Throughput Formula
λ = L / W

Use when you know:
- Queue length (L)
- Processing time (W)
Need: Maximum throughput
PRACTICAL CALCULATIONS
Microservice Capacity
Service constraints:
- CPU cores: 8
- Time per request: 100ms CPU
- Target utilization: 70%

Max concurrent requests = 8 cores × (1000ms/100ms) × 0.7 = 56
Max throughput = 56 / 0.1s = 560 req/s
Database Connection Needs
Application servers: 20
Requests per server: 50 req/s
Query time: 30ms
Queries per request: 3

Total query rate = 20 × 50 × 3 = 3000 queries/s
Connections needed = 3000 × 0.03 = 90 connections
Add safety: 90 × 1.5 = 135 connections
LITTLE'S LAW IN PRACTICE
Debugging Performance Issues
Symptom: Response times increasing

Measure:
1. Current requests in system (L) = 500
2. Arrival rate (λ) = 100 req/s
3. Calculate W = 500/100 = 5 seconds

If normal W = 1 second → System is 5x overloaded
Capacity Planning
Future state:
- Expected traffic: 2x current
- Same response time target
- Current L = 100

New L needed = 100 × 2 = 200
Need to double resources (servers, threads, connections)
COMMON MISCONCEPTIONS
Misconception 1: Only for Queues
Reality: Applies to ANY system with flow
- Cache entries
- TCP connections  
- Database locks
- Memory pages
- User sessions
Misconception 2: Requires Steady State
Reality: True for long-term average
Use windowed measurements for varying load
Misconception 3: Simple Systems Only
Reality: Applies to complex systems too
Decompose into subsystems, apply to each
Page 4: Saturation Graph & Little's Law Primer
Learning Objective: Understand why systems cliff-dive at high utilization.
Little's Law - The Universal Queue Equation:
L = λ × W

Where:
L = Average number of items in system
λ = Average arrival rate
W = Average time in system

This law is ALWAYS true for stable systems, regardless of:
- Distribution of arrivals
- Service time variance  
- Number of servers
- Queue discipline
The Saturation Curve Visualization:
Response Time
    │
400ms│                                    ╱
    │                                  ╱│ 
300ms│                               ╱  │ THE CLIFF
    │                            ╱     │
200ms│                        ╱        │
    │                     ╱           │
100ms│              ╱ ─ ─             │
    │      ─ ─ ─                     │
  0ms└────────────────────────────────┴─────
    0%   20%   40%   60%   80%  90% 95% 100%
                    Utilization →
Why The Cliff Exists (First Principles):

At 0% util: Service time only
At 50% util: Service time + small queue wait
At 80% util: Queue wait ≈ service time
At 90% util: Queue wait = 9 × service time
At 95% util: Queue wait = 19 × service time
At 99% util: Queue wait = 99 × service time!

Mathematical Proof:
For M/M/1 queue:
W = 1/(μ - λ)

Where μ = service rate, λ = arrival rate
Utilization ρ = λ/μ

Therefore:
W = 1/(μ(1 - ρ))

As ρ → 1, W → ∞
🎬 Real-World Manifestation:
Uber's Surge Pricing Algorithm (2018)
- Normal: 70% driver utilization, 2 min wait
- Rush hour: 85% utilization, 5 min wait  
- Big event: 95% utilization, 20 min wait
- System breaks: 99% utilization, infinite wait
- Solution: Surge pricing reduces λ (demand)
Practical Applications Table:
Component         Safe Util    Danger Zone    Action at Danger
---------         ---------    -----------    ----------------
CPU               70%          >85%           Add cores/nodes
Memory            80%          >90%           Increase RAM/swap
Network           60%          >75%           Upgrade bandwidth
Disk I/O          50%          >70%           Add SSDs/RAID
Thread Pool       60%          >80%           Increase pool size
Database Conn     50%          >70%           Add read replicas
🔧 Try This: Visualize Your Queue
pythonimport matplotlib.pyplot as plt
import numpy as np

def response_time(utilization, service_time=100):
    """Calculate response time using M/M/1 model"""
    if utilization >= 1:
        return float('inf')
    return service_time / (1 - utilization)

# Plot the cliff
utils = np.linspace(0, 0.99, 100)
response_times = [response_time(u) for u in utils]

plt.figure(figsize=(10, 6))
plt.plot(utils * 100, response_times)
plt.axvline(x=80, color='orange', linestyle='--', label='Warning')
plt.axvline(x=90, color='red', linestyle='--', label='Danger')
plt.xlabel('Utilization %')
plt.ylabel('Response Time (ms)')
plt.title('The Utilization Cliff')
plt.ylim(0, 1000)
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
Queue Taxonomy:
FIFO:     Fair but can cause head-of-line blocking
LIFO:     Unfair but better for timeout scenarios  
Priority: Can starve low-priority indefinitely
WFQ:      Weighted fair queuing, prevents starvation
RED:      Random early drop, prevents congestion
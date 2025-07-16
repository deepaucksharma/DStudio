Page 73: Capacity Planning Worksheet
Right-sizing for the future
CAPACITY PLANNING FRAMEWORK
Step 1: Baseline Measurement
Current State:
- Peak traffic: _______ requests/second
- Average traffic: _______ requests/second  
- Storage used: _______ GB
- Growth rate: _______% monthly

Resource Usage at Peak:
- CPU: _______%
- Memory: _______%
- Network: _______ Mbps
- Disk I/O: _______ IOPS
Step 2: Growth Projection
Linear Growth:
Future = Current × (1 + monthly_rate × months)

Exponential Growth:
Future = Current × (1 + monthly_rate)^months

S-Curve Growth:
Future = Capacity / (1 + e^(-k×(t-t0)))
Step 3: Safety Margins
Component          Margin    Reason
---------          ------    ------
CPU                40%       Burst handling
Memory             30%       GC headroom
Network            50%       DDoS/spikes
Storage            50%       Log growth
Database Conn      30%       Connection storms
WORKLOAD CHARACTERIZATION
Traffic Patterns
Daily Pattern:
- Peak hour: _____ (e.g., 2 PM)
- Peak/average ratio: _____ (e.g., 3x)
- Weekend factor: _____ (e.g., 0.6x)

Seasonal Pattern:
- Black Friday: _____x normal
- Holiday season: _____x normal
- Summer lull: _____x normal
Request Mix
Operation         % of Traffic    Resource Impact
---------         ------------    ---------------
Read (cached)     60%            Low
Read (DB)         20%            Medium
Write             15%            High
Analytics         5%             Very High

Weighted resource usage:
0.6×1 + 0.2×3 + 0.15×5 + 0.05×10 = 2.45 units/request
SCALING STRATEGIES
Vertical vs Horizontal
Vertical (Bigger boxes):
Current: 8 CPU, 32GB RAM
Next: 16 CPU, 64GB RAM
Cost: 2.2x (not linear!)
Limit: 96 CPU, 768GB RAM

Horizontal (More boxes):
Current: 10 × small instances
Next: 15 × small instances
Cost: 1.5x (linear)
Limit: Practically unlimited
Resource Planning Table
Month    Traffic    CPU Need    Instances    Cost
-----    -------    --------    ---------    ----
0        1000 rps   800 cores   100          $10k
3        1500 rps   1200 cores  150          $15k
6        2250 rps   1800 cores  225          $22k
12       5000 rps   4000 cores  500          $50k

Decision point: Month 6 - need architecture change
CAPACITY PLANNING TOOLS
Little's Law Application
Concurrent users = Requests/sec × Session duration
Database connections = Queries/sec × Query time
Memory needed = Objects/sec × Object lifetime × Size
Queue Theory Application
If utilization > 70%:
  Response time increases exponentially
  Plan for maximum 70% steady state
  
Servers needed = Load / (Capacity × 0.7)
REAL EXAMPLE: E-COMMERCE PLATFORM
Current Baseline
- 10,000 concurrent users
- 100 requests/second average
- 300 requests/second peak
- 50GB database
- 1TB object storage
Growth Assumptions
- User growth: 20% monthly
- Data growth: 30% monthly
- Feature complexity: +10% resources
6-Month Projection
Users: 10,000 × 1.2^6 = 30,000
Requests: 300 × 3 = 900 peak
Database: 50 × 1.3^6 = 230GB
Storage: 1 × 1.3^6 = 4.6TB

Required Infrastructure:
- App servers: 10 → 30
- Database: Needs sharding
- Cache: 10GB → 50GB
- CDN: Essential
CAPACITY PLANNING CHECKLIST
□ Current metrics collected
□ Growth rates calculated
□ Peak patterns identified
□ Resource limits known
□ Scaling triggers defined
□ Budget approved
□ Architecture reviewed
□ Runbooks updated
□ Team trained
□ Vendors notified
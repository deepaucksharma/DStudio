Page 72: Availability Math & Nines
Building reliable systems from unreliable parts
THE NINES
Availability    Downtime/Year    Downtime/Month    Downtime/Day
-----------    -------------    --------------    ------------
90% (1 nine)    36.5 days       3 days            2.4 hours
99% (2 nines)   3.65 days       7.2 hours         14.4 minutes
99.9% (3 nines) 8.76 hours      43.8 minutes      1.44 minutes
99.99% (4 nines) 52.56 minutes  4.38 minutes      8.64 seconds
99.999% (5 nines) 5.26 minutes  26.3 seconds      0.864 seconds
AVAILABILITY CALCULATIONS
Series (AND) - Multiply
System works = A works AND B works AND C works
Availability = A × B × C

Example:
Load Balancer (99.99%) → App (99.9%) → Database (99.9%)
System = 0.9999 × 0.999 × 0.999 = 99.79%
Parallel (OR) - Complement
System fails = A fails AND B fails
Availability = 1 - (1-A) × (1-B)

Example:
Two databases (99.9% each) in failover:
System = 1 - (0.001 × 0.001) = 99.9999%
COMPLEX SYSTEM MODELING
Active-Active with Load Balancer
     LB (99.99%)
    /           \
App1 (99.9%)  App2 (99.9%)
    \           /
     DB (99.9%)

App tier: 1 - (0.001)² = 99.9999%
Full system: 0.9999 × 0.999999 × 0.999 = 99.89%
IMPROVING AVAILABILITY
Strategy Comparison
Approach                Cost    Improvement
--------                ----    -----------
Better hardware         $$$     99% → 99.9%
Redundant hardware      $$      99% → 99.99%
Multiple regions        $$$$    99.9% → 99.99%
Reduce dependencies     $       Big impact
Faster recovery         $       Big impact
ERROR BUDGETS
SLO: 99.9% availability
Error budget: 0.1% = 43.8 minutes/month

Spending the budget:
- Deployment downtime: 10 min
- Unexpected outage: 20 min
- Remaining: 13.8 min

Decision framework:
If budget remains: Ship features
If budget exhausted: Focus on reliability
REAL-WORLD AVAILABILITY
Cloud Provider SLAs
Service              SLA      Reality
-------              ---      -------
AWS EC2              99.99%   99.995%
AWS S3               99.99%   99.99%+
AWS RDS Multi-AZ     99.95%   99.97%
Google GCE           99.99%   99.99%
Azure VMs            99.99%   99.98%
Building on Cloud
Your app on AWS:
- Your code: 99.9%
- EC2: 99.99%
- ELB: 99.99%
- RDS: 99.95%

Theoretical max: 99.83%
Reality with issues: 99.5-99.7%
MTBF AND MTTR
Availability = MTBF / (MTBF + MTTR)

Where:
MTBF = Mean Time Between Failures
MTTR = Mean Time To Recovery

Example:
MTBF = 30 days
MTTR = 30 minutes
Availability = 720 hours / 720.5 hours = 99.93%

Halving MTTR:
New MTTR = 15 minutes
Availability = 720 / 720.25 = 99.97%
AVAILABILITY PATTERNS
Failover Time Impact
Failover Time    Monthly Impact    Nines Lost
-------------    --------------    ----------
10 seconds       Negligible        None
1 minute         1-2 incidents     0.1
5 minutes        5-10 incidents    0.5
30 minutes       30-60 incidents   1.0
Redundancy Strategies
N+1: Minimum redundancy
     Cost: +33% (for N=3)
     Improvement: 10x

N+2: Maintenance + failure
     Cost: +66%
     Improvement: 100x

2N: Full redundancy
    Cost: +100%
    Improvement: 1000x
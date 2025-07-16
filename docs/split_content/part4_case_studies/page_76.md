Page 76: Chaos Engineering
Breaking things on purpose to build confidence
CHAOS ENGINEERING PRINCIPLES
1. Build hypothesis around steady state
2. Vary real-world events
3. Run experiments in production
4. Automate experiments
5. Minimize blast radius

Not random destruction, but scientific discovery
CHAOS EXPERIMENT LIFECYCLE
1. Steady State Definition
Key metrics that define "working":
- Success rate > 99.9%
- p99 latency < 100ms
- Zero data loss
- No customer complaints

Baseline measurement:
- Week of normal operation
- Capture variance
- Document assumptions
2. Hypothesis Formation
"We believe that [SYSTEM] can tolerate [FAILURE]
 as measured by [METRICS] staying within [BOUNDS]"

Examples:
- "Payment service can tolerate 1 database replica failure
   with <10ms p99 latency increase"
   
- "Recommendation API can lose 50% of cache nodes
   with <5% error rate increase"
   
- "Order system can handle primary region failure
   with <30 second recovery time"
3. Experiment Design
Scope:
- Blast radius (% of traffic/users affected)
- Duration (how long to run)
- Severity (partial vs complete failure)
- Rollback plan (how to stop)

Safety mechanisms:
- Automatic abort on SLO breach
- Manual kill switch
- Gradual rollout
- Business hours only (initially)
CHAOS EXPERIMENTS CATALOG
Infrastructure Chaos
1. Instance Termination
   - Random EC2 instance shutdown
   - Tests: Auto-scaling, service discovery
   
2. Network Partitions
   - Isolate availability zones
   - Tests: Quorum logic, split-brain handling
   
3. Clock Skew
   - Advance/delay system clocks
   - Tests: Time-dependent logic, ordering

4. Resource Exhaustion
   - Fill disk, consume memory
   - Tests: Degradation handling, alerts

Code example:
def chaos_fill_disk(fill_percent=90):
    available = get_disk_space()
    to_fill = available * fill_percent / 100
    with open('/tmp/chaos_disk', 'wb') as f:
        f.write(b'0' * to_fill)
Application Chaos
1. Latency Injection
   - Add delays to specific calls
   - Tests: Timeout handling, circuit breakers
   
2. Error Injection  
   - Return errors from dependencies
   - Tests: Retry logic, fallbacks
   
3. Data Corruption
   - Modify responses in flight
   - Tests: Validation, error detection
   
4. Rate Limiting
   - Simulate API quotas
   - Tests: Backoff, queueing

Implementation:
class ChaosProxy:
    def inject_latency(self, percent=10, delay_ms=1000):
        if random.random() < percent/100:
            sleep(delay_ms/1000)
            
    def inject_error(self, percent=5, error_code=500):
        if random.random() < percent/100:
            raise HttpError(error_code)
GAMEDAY PLANNING
Pre-GameDay Checklist
□ Hypothesis documented
□ Success criteria defined
□ Monitoring dashboards ready
□ Abort procedures tested
□ Team roles assigned
□ Communication plan ready
□ Customer support warned
□ Rollback tested
□ Business stakeholders informed
□ Runbooks updated
GameDay Roles
Game Master: Runs the experiment
Observer: Watches metrics
Communicator: Updates stakeholders
Fixer: Ready to intervene
Scribe: Documents everything
GameDay Timeline
T-30min: Final checks, team assembly
T-15min: Monitoring verification
T-0: Begin experiment
T+5min: First health check
T+15min: Evaluate continue/abort
T+30min: Planned end
T+45min: Debrief starts
T+2hr: Report published
REAL GAMEDAY EXAMPLE
Scenario: Payment Service Region Failure
Hypothesis: 
"Payment service can failover to secondary region 
 within 60 seconds with zero transaction loss"

Experiment:
1. Block all traffic to us-east-1
2. Monitor failover behavior
3. Verify no payments lost

Results:
- Failover time: 47 seconds ✓
- Transactions lost: 0 ✓
- Unexpected finding: 15% timeout errors
- Root cause: Connection pool size

Improvements:
- Increase connection pool warmup
- Add pre-flight checks
- Reduce health check interval
CHAOS MATURITY MODEL
Level 1: In Development
- Chaos in test environment only
- Manual experiments
- Known failures only
- Team-initiated
Level 2: In Staging
- Staging environment chaos
- Some automation
- Broader failure modes
- Weekly schedule
Level 3: In Production
- Production experiments
- Automated suite
- Business hours only
- Monthly GameDays
Level 4: Continuous Chaos
- Always-on chaos
- Random scheduling
- Full automation
- Part of CI/CD
CHAOS ENGINEERING TOOLS
Tool Comparison
Chaos Monkey (Netflix):
- Scope: AWS instances
- Maturity: Very high
- Use case: Instance failures

Gremlin:
- Scope: Full infrastructure
- Maturity: Commercial product
- Use case: Enterprise chaos

Litmus:
- Scope: Kubernetes
- Maturity: CNCF project
- Use case: Container chaos

Chaos Toolkit:
- Scope: Extensible
- Maturity: Growing
- Use case: Custom experiments
MEASURING CHAOS SUCCESS
Metrics
1. Experiments Run
   - Target: 1 per service per month
   
2. Issues Discovered
   - Track: Unknown failure modes found
   
3. MTTR Improvement
   - Before/after chaos findings
   
4. Confidence Score
   - Team survey on system reliability
   
5. Incident Reduction
   - Correlation with real incidents
ROI Calculation
Investment:
- 2 engineers × 20% time = $100k/year
- Tools and infrastructure = $20k/year

Returns:
- Prevented outages: 5 × $200k = $1M
- Reduced MTTR: 50% × $500k = $250k
- Team confidence: Priceless

ROI = 940% first year
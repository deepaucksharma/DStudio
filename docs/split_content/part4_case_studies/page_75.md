Page 75: Consistency Tuning in Production
The art of dialing consistency without breaking production
THE PRODUCTION REALITY
Theory: "Just set consistency level to QUORUM"
Reality: "Our p99 latency just tripled and we're losing $10k/minute"

Production is where theory meets:
- Real network latencies
- Actual failure rates
- Business requirements
- Cost constraints
- Human patience
CONSISTENCY TUNING FRAMEWORK
Step 1: Map Operations to Requirements
Operation Type         Consistency Need    Rationale
--------------        ----------------    ---------
User login            STRONG              Security critical
Password change       ALL                 Must replicate immediately
Shopping cart add     SESSION             User's view matters
Product browse        EVENTUAL            Can be stale
Analytics write       ANY                 Some loss OK
Payment processing    STRONG              Money matters
Inventory check       LOCAL_QUORUM        Regional accuracy OK
User preferences      EVENTUAL            Not critical
Audit logs           ALL                 Compliance required
Step 2: Measure Current Impact
Baseline metrics per consistency level:

Operation: getUserProfile
LOCAL_ONE:    p50=5ms,   p99=15ms,   success=99.9%
LOCAL_QUORUM: p50=12ms,  p99=40ms,   success=99.7%
QUORUM:       p50=45ms,  p99=120ms,  success=99.5%
ALL:          p50=80ms,  p99=250ms,  success=98.9%

Business impact:
+10ms latency = -1% conversion rate = -$50k/day
Step 3: Dynamic Tuning Strategy
ConsistencyManager:
    def select_consistency(operation, context):
        # User-based
        if context.user.is_premium:
            return upgrade_consistency(operation.default)
            
        # Time-based
        if is_peak_hours():
            return downgrade_consistency(operation.default)
            
        # Health-based
        if replica_lag > threshold:
            return LOCAL_ONE  # Degrade gracefully
            
        # SLO-based
        if error_budget_remaining < 10%:
            return strongest_available()
            
        return operation.default

Real implementation:
- Start conservative (QUORUM)
- Measure actual behavior
- Gradually relax where possible
- Monitor business metrics
- Rollback if issues
PRODUCTION TUNING PATTERNS
1. Read-Your-Writes Consistency
Problem: User updates profile, refresh shows old data

Solution:
write_result = db.write(QUORUM, data)
session.last_write_timestamp = write_result.timestamp

# On subsequent read:
if session.last_write_timestamp:
    # Ensure we read from up-to-date replica
    consistency = LOCAL_QUORUM
    min_timestamp = session.last_write_timestamp
else:
    consistency = LOCAL_ONE
2. Gradual Consistency Degradation
Degradation ladder:
1. Try ALL (strongest)
2. On timeout → Try QUORUM
3. On timeout → Try LOCAL_QUORUM  
4. On timeout → Try ONE
5. On failure → Return cached/default

Track degradation rate:
- Normal: <1% degraded reads
- Warning: 1-5% degraded
- Alert: >5% degraded
3. Consistency SLOs
Define per operation:
- Login: 99% strong consistency
- Cart: 95% session consistency
- Browse: 90% eventual consistency

Monitor compliance:
consistency_slo_met = (
    strong_reads_succeeded / total_reads_attempted
)

if consistency_slo_met < target:
    page_oncall("Consistency SLO violation")
REAL-WORLD TUNING EXAMPLE
E-commerce Platform Timeline
Day 1: Launch with ALL writes, QUORUM reads
- Latency: p99 = 200ms
- Errors: 0.5%
- Cost: $10k/day

Day 7: Analyze patterns
- 90% of reads are browsing (can be eventual)
- 5% are cart operations (need session)
- 5% are checkout (need strong)

Day 14: Implement per-operation consistency
- Browse: ONE (p99 = 20ms)
- Cart: LOCAL_QUORUM (p99 = 50ms)
- Checkout: QUORUM (p99 = 100ms)
- Latency: Overall p99 = 45ms
- Cost: $6k/day

Day 30: Add dynamic tuning
- Degrade during traffic spikes
- Upgrade for premium users
- Overall availability: 99.95%
- Cost: $5k/day
MONITORING CONSISTENCY
Key Metrics
1. Consistency Level Distribution
   - What % of operations at each level
   - Trend over time
   - Correlation with errors

2. Consistency Violations
   - Read-your-write failures
   - Stale read detection
   - Out-of-order operations

3. Business Impact
   - Conversion rate by consistency
   - User complaints about stale data
   - Revenue impact of degradation

4. Infrastructure Cost
   - $/operation by consistency level
   - Cross-region traffic costs
   - Resource utilization
ROLLOUT STRATEGY
Week 1: Shadow mode
- Log what consistency would be used
- No actual changes
- Analyze impact

Week 2: 1% experiment
- Enable for 1% of traffic
- A/B test results
- Monitor all metrics

Week 3: Regional rollout
- Enable in lowest-traffic region
- Full monitoring
- Rollback plan ready

Week 4: Global rollout
- Gradual increase
- Watch for regional differences
- Tune based on results
COMMON PITFALLS
1. Consistency Whiplash
Problem: Rapidly changing consistency levels
Impact: Cache thrashing, unpredictable behavior

Solution: Hysteresis
if current == QUORUM and load < 0.7:
    stay at QUORUM  # Don't thrash
elif current == ONE and load > 0.9:
    upgrade to QUORUM
2. Silent Degradation
Problem: System silently serves stale data
Impact: Business logic errors, user confusion

Solution: Make it visible
response.headers['X-Consistency-Level'] = actual_level
response.headers['X-Data-Freshness'] = staleness_ms
3. All-or-Nothing Thinking
Problem: "We need strong consistency everywhere"
Reality: 10% of operations need 90% of consistency

Solution: Data-driven decisions
- Measure actual requirements
- Test with real users
- Optimize the 90% case
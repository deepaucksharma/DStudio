---
title: "The Operations: Living with Approximate Truth"
description: "Build dashboards that expose uncertainty, create runbooks for split-brain scenarios, and operate systems that thrive on partial knowledge."
---

# The Operations: Living with Approximate Truth

<div class="axiom-box">
<h2>Stop Lying to Your Dashboards</h2>
<p>Your monitoring shows "Status: ✓ Healthy" while your distributed system has three different versions of truth. Time to build dashboards that expose reality, not fantasy.</p>
</div>

## The Truth Health Dashboard

```
DISTRIBUTED TRUTH VITAL SIGNS
═════════════════════════════

┌─────────────────────────────────────────────────────┐
│ CONSENSUS LAG                    🔴 CRITICAL        │
│ Time for truth to propagate                        │
│ ┌─────────────────────────────────────────────┐   │
│ │  NOW: 847ms    BASELINE: 200ms              │   │
│ │  ████████████████████░░░░  420% of normal   │   │
│ └─────────────────────────────────────────────┘   │
│ ALERT: User-visible inconsistency likely           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ DIVERGENCE SCORE                 ⚠️  WARNING        │
│ How much nodes disagree                            │
│ ┌─────────────────────────────────────────────┐   │
│ │ AGREEING: ████████░░░░  65% (13/20 nodes)   │   │
│ │ DIVERGENT: ████░░░░░░░░  20% (4 nodes)      │   │
│ │ UNKNOWN:   ███░░░░░░░░░  15% (3 nodes)      │   │
│ └─────────────────────────────────────────────┘   │
│ DANGER: Approaching split-brain threshold          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ CONFLICT RATE                    📈 TRENDING UP    │
│ Concurrent updates requiring reconciliation        │
│ ┌─────────────────────────────────────────────┐   │
│ │ Last hour:  ████████████  847 conflicts     │   │
│ │ Yesterday:  ████░░░░░░░░  234 conflicts     │   │
│ │ Last week:  ██░░░░░░░░░░  89 conflicts/day  │   │
│ └─────────────────────────────────────────────┘   │
│ ACTION: Consider sharding hot keys                 │
└─────────────────────────────────────────────────────┘
```

## Building Truth-Aware Metrics

### Prometheus Metrics for Distributed Truth

```yaml
# prometheus_rules.yml
groups:
  - name: distributed_truth
    interval: 10s
    rules:
      # Consensus lag
      - record: truth:consensus_lag_ms
        expr: |
          histogram_quantile(0.99,
            sum(rate(consensus_duration_bucket[5m])) by (le)
          )
      
      # Node divergence
      - record: truth:divergence_ratio
        expr: |
          1 - (
            count(group by (key) (
              distributed_state_version == max(distributed_state_version)
            )) / 
            count(distributed_state_version)
          )
      
      # Split brain detection
      - alert: PossibleSplitBrain
        expr: |
          count(count by (partition) (
            node_view_of_cluster_size
          )) > 1
        for: 30s
        annotations:
          summary: "Multiple cluster views detected"
          description: "{{ $value }} different cluster views exist"
      
      # Byzantine node detection
      - alert: ByzantineNodeDetected
        expr: |
          rate(conflicting_responses_total[5m]) > 0.1
        annotations:
          summary: "Node {{ $labels.node }} giving conflicting responses"
```

### Grafana Dashboard Queries

```python
class TruthMonitoringDashboard:
    """
    Grafana dashboard configuration for truth monitoring
    """
    
    def consensus_lag_panel(self):
        return {
            "title": "Consensus Lag Heatmap",
            "query": """
                sum by (node_pair) (
                    rate(consensus_lag_ms_bucket[5m])
                )
            """,
            "visualization": "heatmap",
            "alert_threshold": 500,  # ms
            "description": "Time for nodes to agree on values"
        }
    
    def version_divergence_panel(self):
        return {
            "title": "Version Vector Divergence",
            "query": """
                max by (key) (
                    distributed_state_version
                ) - 
                min by (key) (
                    distributed_state_version
                )
            """,
            "visualization": "graph",
            "alert_threshold": 5,  # versions
            "description": "How far apart are node versions"
        }
    
    def conflict_resolution_panel(self):
        return {
            "title": "Conflict Resolution Rate",
            "query": """
                sum(rate(conflicts_resolved_total[5m])) by (resolution_type)
            """,
            "visualization": "stacked",
            "legend": ["last_write_wins", "vector_clock", "application_merge"],
            "description": "How conflicts are being resolved"
        }
```

## Truth Verification Runbooks

### Runbook: Split-Brain Response

<div class="failure-vignette">
<h3>WHEN: Cluster Has Multiple Primary Nodes</h3>

```
SPLIT-BRAIN EMERGENCY RESPONSE
═════════════════════════════

VERIFY (1 minute):
─────────────────
$ kubectl exec -it node-1 -- check-primary-status
$ kubectl exec -it node-2 -- check-primary-status
$ kubectl exec -it node-3 -- check-primary-status

If multiple report "PRIMARY" → CONFIRMED SPLIT-BRAIN

IMMEDIATE ACTIONS (5 minutes):
─────────────────────────────
1. STOP WRITES (prevent further divergence)
   $ kubectl patch service api -p '{"spec":{"selector":{"mode":"readonly"}}}'

2. IDENTIFY PARTITIONS
   $ for node in $(get_all_nodes); do
       echo "=== $node ==="
       check_reachability $node
     done

3. DOCUMENT SPLIT TIME
   Split detected: $(date)
   Write stop time: $(date)
   Affected nodes: [list]

RECONCILIATION (30 minutes):
───────────────────────────
1. CHOOSE AUTHORITATIVE PARTITION
   Usually: Partition with most nodes
   Sometimes: Partition with most recent writes
   Never: Arbitrary choice

2. EXTRACT DIVERGENT DATA
   $ extract_writes_since $SPLIT_TIME > divergent_data.json

3. RECONCILE CONFLICTS
   - Account balances: Manual review required
   - User profiles: Last write wins  
   - Analytics: Sum all values
   - Audit logs: Merge all entries

4. FORCE CONVERGENCE
   $ promote_to_primary $CHOSEN_NODE
   $ force_rejoin_cluster $OTHER_NODES

PREVENTION:
──────────
□ Add witness nodes for odd total
□ Implement proper fencing
□ Use quorum-based decisions
□ Add split-brain detection
```
</div>

### Runbook: Byzantine Node Isolation

```python
class ByzantineNodeHandler:
    """
    Automated Byzantine node detection and isolation
    """
    
    def detect_byzantine_behavior(self, node_id):
        """
        Check for Byzantine symptoms
        """
        checks = {
            'conflicting_responses': self.check_response_consistency(node_id),
            'impossible_values': self.check_value_sanity(node_id),
            'time_travel': self.check_temporal_consistency(node_id),
            'vote_flipping': self.check_vote_consistency(node_id)
        }
        
        byzantine_score = sum(1 for check in checks.values() if check)
        
        if byzantine_score >= 2:
            self.isolate_byzantine_node(node_id)
            
    def isolate_byzantine_node(self, node_id):
        """
        Emergency Byzantine node isolation
        """
        print(f"BYZANTINE NODE DETECTED: {node_id}")
        
        # Step 1: Remove from consensus group
        self.consensus_group.remove_member(node_id)
        
        # Step 2: Redirect traffic away
        self.load_balancer.remove_backend(node_id)
        
        # Step 3: Fence the node
        self.fencing_service.fence_node(node_id)
        
        # Step 4: Alert humans
        self.alert_oncall(
            severity="CRITICAL",
            title=f"Byzantine node {node_id} isolated",
            runbook_url="https://wiki/byzantine-node-response"
        )
        
        # Step 5: Collect forensics
        self.collect_node_diagnostics(node_id)
```

## Production Chaos Testing

<div class="decision-box">
<h3>Trust but Verify: Chaos Engineering for Truth</h3>

```python
class TruthChaosExperiments:
    """
    Chaos experiments to verify truth handling
    """
    
    def experiment_introduce_clock_skew(self):
        """
        Gradually introduce clock skew between nodes
        """
        experiment = {
            "name": "clock-skew-resilience",
            "hypothesis": "System maintains consistency with 100ms clock skew",
            "method": """
                for node in nodes[:len(nodes)//2]:
                    # Skew half the nodes forward
                    node.adjust_clock(+50_000)  # +50ms
                for node in nodes[len(nodes)//2:]:
                    # Skew other half backward
                    node.adjust_clock(-50_000)  # -50ms
            """,
            "rollback": "node.reset_clock() for all nodes",
            "metrics": [
                "truth:consensus_lag_ms",
                "truth:divergence_ratio",
                "user_visible_inconsistencies"
            ],
            "abort_conditions": [
                "consensus_lag_ms > 1000",
                "user_visible_inconsistencies > 0"
            ]
        }
        return self.run_experiment(experiment)
    
    def experiment_partition_minority(self):
        """
        Partition minority of nodes
        """
        experiment = {
            "name": "minority-partition-handling",
            "hypothesis": "Minority partition becomes read-only",
            "method": """
                # Partition 40% of nodes
                minority = nodes[:int(len(nodes) * 0.4)]
                majority = nodes[int(len(nodes) * 0.4):]
                
                network.partition([minority, majority])
                
                # Verify minority can't accept writes
                try:
                    minority[0].write("test", "value")
                    assert False, "Minority accepted write!"
                except QuorumException:
                    pass  # Expected
            """,
            "duration": "5 minutes",
            "success_criteria": [
                "Minority nodes reject writes",
                "Majority continues operating",
                "No data loss after healing"
            ]
        }
        return self.run_experiment(experiment)
```
</div>

## Observability Stack for Truth

```yaml
# docker-compose.yml for truth observability
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules.yml:/etc/prometheus/rules.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    
  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./dashboards:/var/lib/grafana/dashboards
      - ./datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    environment:
      - GF_DASHBOARD_JSON_ENABLED=true
      - GF_DASHBOARD_JSON_PATH=/var/lib/grafana/dashboards
    
  vector-clock-visualizer:
    image: distributed-truth/vector-clock-viz:latest
    ports:
      - "8080:8080"
    environment:
      - REFRESH_INTERVAL=1s
      - SHOW_CONFLICTS=true
      
  consensus-debugger:
    image: distributed-truth/consensus-debug:latest
    ports:
      - "8081:8081"
    environment:
      - TRACE_ALL_MESSAGES=true
      - SHOW_TERM_CHANGES=true
```

## Truth SLIs and SLOs

<div class="truth-box">
<h3>Service Level Indicators for Distributed Truth</h3>

```
TRUTH SLIS AND TARGETS
═════════════════════

1. Consensus Lag (p99)
   SLI: Time from write to global agreement
   SLO: < 500ms for 99.9% of writes
   Alert: > 1000ms for 5 minutes

2. Read Consistency
   SLI: % of reads returning latest value
   SLO: > 99.5% within 200ms of write
   Alert: < 95% for 1 minute

3. Conflict Rate
   SLI: Conflicts per 1000 operations
   SLO: < 1 conflict per 1000 ops
   Alert: > 10 conflicts per 1000 ops

4. Split-Brain Duration
   SLI: Total minutes in split-brain per month
   SLO: < 5 minutes per month
   Alert: Any split-brain detected

5. Byzantine Node MTTR
   SLI: Time to detect and isolate Byzantine node
   SLO: < 30 seconds
   Alert: Byzantine behavior unresolved for 60s
```
</div>

## The Daily Truth Ritual

```bash
#!/bin/bash
# daily_truth_health_check.sh

echo "=== Daily Distributed Truth Health Check ==="
echo "Date: $(date)"
echo

echo "1. Checking consensus lag..."
kubectl exec -it prometheus -- \
  promtool query instant \
  'histogram_quantile(0.99, truth:consensus_lag_ms)'

echo "2. Checking node agreement..."
for node in $(kubectl get pods -l app=distributed-db -o name); do
  echo -n "$node: "
  kubectl exec -it $node -- get-version-vector
done | sort | uniq -c

echo "3. Recent conflicts..."
kubectl logs -l app=conflict-resolver --since=24h | \
  grep "CONFLICT" | wc -l

echo "4. Clock synchronization..."
for node in $(kubectl get pods -l app=distributed-db -o name); do
  echo -n "$node: "
  kubectl exec -it $node -- date +%s.%N
done | awk '{
  if(NR==1) {min=max=$2} 
  if($2<min) {min=$2} 
  if($2>max) {max=$2}
} END {
  print "Max clock skew: " (max-min)*1000 "ms"
}'

echo "5. Truth budget status..."
echo "Consensus operations today: $(get_consensus_count)"
echo "Estimated cost: \$$(get_consensus_cost)"
echo "Remaining budget: \$$(get_remaining_budget)"
```

<div class="axiom-box">
<h3>The Ultimate Truth About Operations</h3>
<p>Operating distributed systems means accepting that you'll never have perfect truth. Your job isn't to achieve certainty—it's to manage uncertainty gracefully, detect divergence quickly, and reconcile conflicts intelligently.</p>
</div>

## Your Operational Checklist

- [ ] Dashboard shows truth confidence, not binary health
- [ ] Alerts fire on divergence, not just failures  
- [ ] Runbooks handle split-brain scenarios
- [ ] Chaos tests verify truth assumptions
- [ ] SLOs reflect acceptable uncertainty
- [ ] Team trained on CAP theorem implications

<div class="decision-box">
<h3>You've Mastered Distributed Truth!</h3>
<p>You now see truth as probability, recognize the patterns of divergence, know the engineering solutions, and can operate systems that thrive on uncertainty. <strong>You'll never look at distributed systems the same way again.</strong></p>

<p>Ready for the next law? <a href="../law6-human-api/">Law 6: Cognitive Load</a> explores how human limits shape system design.</p>
</div>
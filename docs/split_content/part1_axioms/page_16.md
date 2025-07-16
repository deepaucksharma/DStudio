Page 16: FinOps Quick-Win Checklist
The 20% Effort, 80% Savings Checklist:
□ IMMEDIATE WINS (This week)
  □ Find and terminate unused resources
    - EC2 instances with 0% CPU for 7 days
    - Unattached EBS volumes
    - Unused Elastic IPs
    - Empty S3 buckets
    Typical savings: 10-20%

  □ Right-size over-provisioned resources  
    - Instances using <20% CPU consistently
    - Over-provisioned RDS instances
    - Oversized caches
    Typical savings: 20-30%

  □ Delete old snapshots and backups
    - EBS snapshots >30 days
    - RDS snapshots (keep only required)
    - S3 lifecycle policies
    Typical savings: 5-10%

□ QUICK WINS (This month)
  □ Move to spot instances for non-critical
    - Dev/test environments
    - Batch processing
    - CI/CD runners
    Typical savings: 70-90% on those workloads

  □ Enable auto-scaling with schedules
    - Scale down nights/weekends
    - Scale up for known peaks
    Typical savings: 30-40%

  □ Compress and dedupe data
    - Enable S3 compression
    - CloudFront compression
    - Database compression
    Typical savings: 20-50% on storage/transfer

□ STRATEGIC WINS (This quarter)
  □ Reserved instances for steady workloads
    - 1-year for likely stable
    - 3-year for definitely stable
    Typical savings: 30-70%

  □ Re-architect chatty services
    - Batch API calls
    - Move to events vs polling
    - Cache repeated queries
    Typical savings: 50%+ on data transfer

  □ Region optimization
    - Move workloads to cheaper regions
    - Use regional services
    Typical savings: 10-30%
Cost Optimization vs Performance Trade-offs:
Optimization         Performance Impact    Worth it?
-----------         -----------------    ---------
Spot instances      Can be interrupted   Yes for batch
Smaller instances   Less burst capacity  Yes if sized right
Cross-AZ traffic    Added latency        No for sync calls
Cold storage        Slower retrieval     Yes for archives
Aggressive caching  Stale data risk      Yes with TTL
Single AZ           No HA                No for critical
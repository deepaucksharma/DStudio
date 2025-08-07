---
title: "Law 7: Economic Reality - Quick Assessment"
description: Objective assessment on cost, ROI, and business constraints in distributed systems
type: test
difficulty: advanced
time_limit: 30 minutes
question_count: 30
passing_score: 75
---

# Law 7: The Law of Economic Reality

⏱️ **Time:** 30 minutes | 📝 **30 questions** | ✅ **Passing:** 75%

!!! abstract "Core Principle"
    Technical excellence must be economically viable. Every architectural decision has a cost, and perfection is economically impossible.

---

## Section A: Fundamentals (10 questions)

### 1. [Multiple Choice] Availability Cost
What's the typical cost multiplier for each additional "9" of availability?
- A) 2x
- B) 5x
- C) 10x ✓
- D) 100x

### 2. [One-line] Cost vs Benefit
When does investing in reliability stop making economic sense?
- **Answer:** When cost exceeds revenue impact

### 3. [True/False] Perfect System
It's economically feasible to build a perfect system with no failures.
- **Answer:** False
- **Reason:** Perfection requires infinite resources; diminishing returns apply.

### 4. [Fill in Blank] Cloud Pricing
The largest cost component in cloud infrastructure is typically _______.
- **Answer:** compute (or data transfer for some workloads)

### 5. [Multiple Choice] Technical Debt
Technical debt is best viewed as:
- A) Always bad
- B) A financial loan with interest ✓
- C) Free money
- D) Irrelevant to business

### 6. [Calculate] Downtime Cost
If a service makes $1M/day, what's the cost of 1 hour downtime?
- **Answer:** ~$42,000

### 7. [True/False] Over-engineering
Over-engineering always saves money in the long run.
- **Answer:** False
- **Reason:** May never recoup investment if requirements don't materialize.

### 8. [Multiple Choice] Build vs Buy
The primary factor in build vs buy decisions should be:
- A) Technical challenge
- B) Total cost of ownership ✓
- C) Developer preference
- D) Latest technology

### 9. [One-line] Opportunity Cost
What is opportunity cost in engineering decisions?
- **Answer:** Value of the best alternative not chosen

### 10. [Fill in Blank] The 80/20 rule states that 80% of _______ comes from 20% of _______.
- **Answer:** value/results, effort/features

---

## Section B: Application (10 questions)

### 11. [Pattern Matching] Cost Optimization
Match the technique to its cost benefit:
1. Auto-scaling         A. Reduce idle resources
2. Caching             B. Reduce compute costs
3. CDN                 C. Reduce bandwidth costs
4. Spot instances      D. Reduce instance costs

**Answers:** 1-A, 2-B, 3-C, 4-D

### 12. [Multiple Choice] Multi-region Cost
Multi-region deployment typically increases costs by:
- A) 10-20%
- B) 50-100%
- C) 2-3x ✓
- D) 10x

### 13. [True/False] Free Tier
Using free tier services in production is always cost-effective.
- **Answer:** False
- **Reason:** Hidden costs in migration, limits, and support.

### 14. [Calculate] Storage Tiers
If hot storage costs $0.10/GB and cold storage $0.01/GB, savings for 1TB moved to cold?
- **Answer:** $90/month

### 15. [Multiple Choice] Monitoring ROI
Comprehensive monitoring typically:
- A) Costs more than it saves
- B) Pays for itself through incident prevention ✓
- C) Is purely overhead
- D) Has no measurable ROI

### 16. [One-line] Reserved Instances
What's the typical break-even point for reserved instances?
- **Answer:** 60-70% utilization

### 17. [Fill in Blank] Database costs often grow _______ with data size due to performance requirements.
- **Answer:** exponentially (or non-linearly)

### 18. [Multiple Choice] Developer Time
If a developer costs $200k/year, their hourly cost is approximately:
- A) $50
- B) $100 ✓
- C) $200
- D) $500

### 19. [Pattern Match] Cost Centers
Match the service to its primary cost driver:
1. Video streaming      A. Storage
2. API gateway         B. Bandwidth
3. Data warehouse      C. Compute
4. CI/CD pipeline      D. Compute time

**Answers:** 1-B, 2-C, 3-A, 4-D

### 20. [True/False] Kubernetes Cost
Kubernetes always reduces infrastructure costs.
- **Answer:** False
- **Reason:** Overhead and complexity can increase costs for small deployments.

---

## Section C: Business Decisions (10 questions)

### 21. [Best Choice] Startup Architecture
For an early-stage startup, prioritize:
- A) Perfect scalability
- B) Lowest initial cost with iteration capability ✓
- C) Most advanced technology
- D) Zero technical debt

### 22. [Multiple Choice] SLA Penalties
SLA breach penalties should be:
- A) Unlimited
- B) Proportional to customer impact ✓
- C) Zero
- D) Fixed regardless of impact

### 23. [Rank Order] Cost Optimization Priority
Order by typical ROI (highest first):
- Fix memory leaks
- Implement caching
- Negotiate vendor contracts
- Optimize database queries

**Answer:** Fix memory leaks, Optimize queries, Implement caching, Negotiate contracts

### 24. [One-line] FinOps Purpose
What's the primary goal of FinOps practices?
- **Answer:** Optimize cloud spending while maintaining performance

### 25. [True/False] Cheapest Option
Always choosing the cheapest option minimizes total cost.
- **Answer:** False
- **Reason:** May increase operational costs or technical debt.

### 26. [Calculate] Team Efficiency
If automation saves 2 hours/week for a 10-person team at $100/hour, annual savings?
- **Answer:** $104,000

### 27. [Multiple Choice] Cost Attribution
Accurate cost attribution per service/team:
- A) Is unnecessary overhead
- B) Drives accountability and optimization ✓
- C) Is technically impossible
- D) Reduces team morale

### 28. [Fill in Blank] The "last mile" of optimization typically yields _______ returns.
- **Answer:** diminishing

### 29. [Best Choice] Enterprise Architecture
For a large enterprise with regulatory requirements:
- A) Minimize all costs
- B) Balance compliance, reliability, and cost ✓
- C) Use only open-source
- D) Outsource everything

### 30. [Identify] Economic Anti-pattern
Which represents poor economic thinking?
- A) Gradual migration strategy
- B) Proof of concept before full implementation
- C) Rebuilding everything with latest technology ✓
- D) Regular cost reviews

---

## Answer Key Summary

**Section A (Fundamentals):** 1-C, 2-When cost exceeds revenue impact, 3-False, 4-compute, 5-B, 6-$42,000, 7-False, 8-B, 9-Value of best alternative, 10-value/effort

**Section B (Application):** 11-(1-A,2-B,3-C,4-D), 12-C, 13-False, 14-$90, 15-B, 16-60-70% utilization, 17-exponentially, 18-B, 19-(1-B,2-C,3-A,4-D), 20-False

**Section C (Business):** 21-B, 22-B, 23-Leaks/Queries/Cache/Contracts, 24-Optimize spending while maintaining performance, 25-False, 26-$104,000, 27-B, 28-diminishing, 29-B, 30-C

---

## Quick Reference Card

### Cost Scaling Factors

| Factor | Typical Impact |
|--------|---------------|
| **Each 9 of availability** | 10x cost |
| **Multi-region** | 2-3x cost |
| **Strong consistency** | 2-5x cost |
| **Real-time processing** | 3-10x cost |
| **Zero downtime deployment** | 2-4x complexity cost |

### ROI Calculations

```
ROI = (Benefit - Cost) / Cost × 100%

Developer Hour = Annual Salary / 2000
Downtime Cost = Revenue per Hour × Hours Down
Automation ROI = (Time Saved × Hourly Rate) - Development Cost
```

### Cost Optimization Hierarchy

1. **Eliminate waste:** Unused resources, overprovisioning
2. **Optimize usage:** Right-sizing, scheduling
3. **Leverage discounts:** Reserved capacity, spot instances
4. **Architectural changes:** Caching, async processing
5. **Renegotiate contracts:** Volume discounts, commitments

### Economic Principles

- **Diminishing returns:** Each improvement costs more
- **Opportunity cost:** Consider alternatives
- **Total cost of ownership:** Include operational costs
- **Time value:** Earlier savings worth more
- **Risk-adjusted returns:** Factor in probability

### Remember
- **Perfect is the enemy of good** - And economically impossible
- **Measure ROI** - Not all improvements are worth it
- **Technical debt has interest** - Pay it strategically
- **People cost more than servers** - Optimize developer productivity

---

*Continue to [Pillar 1: Work Distribution →](../pillars/tests/work-distribution-test.md)*
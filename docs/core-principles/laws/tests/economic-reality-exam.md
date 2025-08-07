---
title: "Law 7 Exam: Economic Reality Mastery Assessment"
description: "Comprehensive examination testing deep understanding of financial decision-making in distributed systems architecture"
type: exam
difficulty: hard
prerequisites:
  - core-principles/laws/economic-reality.md
  - core-principles/laws/module-7-economic-reality.md
time_limit:
  hard: 90m
  very_hard: 180m
open_book: true
calculator: recommended
status: complete
last_updated: 2025-01-30
---

# Law 7 Mastery Exam: Economic Reality

!!! warning "Exam Instructions"
    **Format:** Open book | **Calculator:** Recommended
    
    - Focus on **financial analysis** and **economic trade-offs**
    - Answers should include **calculations** and **business justification**
    - Grading focuses on **ROI thinking** and **practical economics**
    - Reference formulas are provided - apply them to real scenarios

## Quick Reference Formulas

!!! info "Core Economic Formulas"
    - **True Cloud Cost:** `Actual Cost = Sticker Price × 1.85`
    - **Technical Debt:** `Future Cost = Initial Shortcut × (1.78)^years`
    - **Build vs Buy Threshold:** Consider building when annual spend > $10M
    - **Unit Economics:** `Cost per User = Fixed Costs/Users + Variable Cost per User`
    - **ROI:** `ROI = (Benefit - Cost) / Cost × 100%`
    - **Payback Period:** `Time when Cumulative Benefits = Investment`

---

## Section 1: Hard Questions (90 minutes)

=== "H-1: Hidden Cost Analysis"
    
    ### Scenario
    Your AWS bill shows $50,000/month for your microservices infrastructure. The CFO wants to know the "real" cost.
    
    **Question A:** Calculate the true monthly cost using industry multipliers.
    
    **Question B:** Identify the top 3 hidden cost categories and their monthly impact.
    
    **Question C:** Propose one optimization that could reduce hidden costs by 20%.
    
    ??? tip "Hint"
        Remember the 1.85x multiplier and its breakdown. Think about which hidden costs are easiest to optimize.
    
    ??? success "Expected Answer"
        **A: True Monthly Cost**
        - Sticker price: $50,000
        - True cost: $50,000 × 1.85 = **$92,500/month**
        - Hidden costs: $42,500/month
        
        **B: Top 3 Hidden Cost Categories**
        1. **Operations overhead (28%):** $50,000 × 0.28 = $14,000/month
        2. **Data transfer (15%):** $50,000 × 0.15 = $7,500/month
        3. **Backup/DR (14%):** $50,000 × 0.14 = $7,000/month
        
        **C: Optimization Proposal**
        **Target: Reduce operations overhead from 28% to 20%**
        - Implement infrastructure as code (reduces manual operations)
        - Add comprehensive monitoring automation
        - Create self-healing systems for common issues
        - **Savings:** $50,000 × 0.08 = $4,000/month (48K/year)
        - **Investment:** $100K for automation tools
        - **Payback:** 25 months

=== "H-2: Technical Debt Compound Interest"
    
    ### Scenario
    Three years ago, your team skipped proper error handling to meet a deadline, saving 3 weeks of work ($15,000). Now you spend 10 hours/week dealing with production issues from this decision.
    
    **Question A:** Calculate the total cost of this technical debt after 3 years.
    
    **Question B:** What's the break-even point for fixing it now vs. continuing to pay the "interest"?
    
    ??? tip "Hint"
        Use the 78% compound interest formula for technical debt. Consider both past costs and future projections.
    
    ??? success "Expected Answer"
        **A: Total Cost After 3 Years**
        Using formula: Cost = $15,000 × (1.78)^3
        - Year 1: $15,000 × 1.78 = $26,700
        - Year 2: $26,700 × 1.78 = $47,526
        - Year 3: $47,526 × 1.78 = **$84,596**
        
        Current weekly cost: 10 hours × $150/hour = $1,500/week = $78,000/year
        
        **B: Break-Even Analysis**
        - Cost to fix now: 4 weeks × 40 hours × $150 = $24,000
        - Current burn rate: $78,000/year
        - If we fix it: Save $78,000/year - $24,000 investment
        - **Break-even: 3.7 months**
        - Every month delayed costs an additional $6,500
        - **Decision: Fix immediately**

=== "H-3: Build vs Buy Decision"
    
    ### Scenario
    Your team needs a real-time analytics platform. Options:
    - **Build:** 6 engineers for 9 months, then 1.5 engineers maintenance
    - **Buy:** Datadog at $200K/year plus $50K integration
    
    **Question:** Create a 5-year TCO comparison and make a recommendation.
    
    ??? tip "Hint"
        Remember to include opportunity costs and apply realistic multipliers for custom development.
    
    ??? success "Expected Answer"
        **BUILD Option:**
        - Development: 6 engineers × 9 months × $15K/month = $810,000
        - Realistic multiplier (2.5x for complexity): $2,025,000
        - Annual maintenance: 1.5 engineers × $180K = $270,000
        - 5-year TCO: $2,025,000 + (4 × $270,000) = **$3,105,000**
        - Opportunity cost: 6 engineers could build $3M+ of other features
        
        **BUY Option:**
        - Integration: $50,000 (one-time)
        - Annual license: $200,000
        - 5-year TCO: $50,000 + (5 × $200,000) = **$1,050,000**
        
        **Recommendation: BUY**
        - Saves $2,055,000 over 5 years
        - Faster time to market (3 months vs 9 months)
        - Regular updates and support included
        - Unless analytics is core differentiator, building makes no sense

=== "H-4: Unit Economics at Scale"
    
    ### Scenario
    Your SaaS currently serves 10,000 users at $50K/month infrastructure cost. You're planning to scale to 100,000 users.
    
    **Question A:** Calculate current cost per user.
    
    **Question B:** Project cost per user at 100K users (consider scale economies).
    
    **Question C:** What architecture change would have the biggest impact on unit economics?
    
    ??? tip "Hint"
        Fixed costs amortize with scale, but complexity costs increase. The sweet spot is around 60-75% utilization.
    
    ??? success "Expected Answer"
        **A: Current Cost per User**
        - Monthly cost: $50,000
        - Users: 10,000
        - **Cost per user: $5.00/month**
        
        **B: Projected Cost at 100K Users**
        - Fixed costs (40%): $20,000 (amortizes to $0.20/user)
        - Variable costs (60%): $30,000 (scales linearly to $300,000)
        - Additional complexity overhead (20%): $64,000
        - Total at 100K: $20,000 + $300,000 + $64,000 = $384,000
        - **Cost per user: $3.84/month** (23% reduction)
        
        **C: Biggest Impact Architecture Change**
        **Implement multi-tenant architecture with resource pooling:**
        - Reduces per-tenant overhead by 60%
        - Better resource utilization (from 40% to 70%)
        - Projected cost per user: $2.30/month
        - Annual savings at 100K users: $1.85M

=== "H-5: ROI Analysis for Refactoring"
    
    ### Scenario
    Your monolith has become a bottleneck. Proposed microservices migration:
    - Cost: $2M over 12 months
    - Benefits: 50% performance improvement, 30% operational cost reduction
    
    **Question:** Calculate the ROI and determine if this investment makes sense.
    
    ??? tip "Hint"
        Quantify all benefits in dollar terms. Consider both direct savings and revenue impact.
    
    ??? success "Expected Answer"
        **Investment Analysis:**
        - Development: $2,000,000
        - Opportunity cost (20%): $400,000
        - Training and transition: $100,000
        - **Total Investment: $2,500,000**
        
        **Annual Benefits:**
        - Performance (50% faster → 20% more revenue): $800,000
        - Operational savings (30% of $1M): $300,000
        - Developer productivity (25% improvement): $450,000
        - Reduced incidents (40% fewer): $200,000
        - **Total Annual Benefit: $1,750,000**
        
        **ROI Calculation:**
        - Year 1 ROI: ($1,750,000 - $2,500,000) / $2,500,000 = **-30%**
        - Year 2 ROI: ($3,500,000 - $2,500,000) / $2,500,000 = **40%**
        - Payback period: **17 months**
        - 3-year ROI: **110%**
        
        **Decision: PROCEED with conditions:**
        - Phase the migration to reduce risk
        - Start with highest-value services
        - Measure and validate benefits at each phase

=== "H-6: Cloud vs On-Premise"
    
    ### Scenario
    Your company spends $500K/month on AWS. Someone proposes moving back to data centers.
    
    **Question:** At what utilization rate would data centers become more economical?
    
    ??? tip "Hint"
        Consider CapEx amortization, operational overhead, and the hidden costs of running data centers.
    
    ??? success "Expected Answer"
        **Cloud Costs:**
        - Monthly: $500,000
        - Annual: $6,000,000
        - True cost (1.85x): $11,100,000
        
        **Data Center Analysis:**
        - CapEx (servers, network, facility): $15,000,000
        - 3-year amortization: $5,000,000/year
        - OpEx (power, cooling, space): $1,800,000/year
        - Staff (8 engineers): $1,600,000/year
        - Total annual: $8,400,000
        
        **Break-even Utilization:**
        - Data center is cheaper if: $8.4M < $11.1M × Utilization
        - **Break-even: 76% utilization**
        
        **Recommendation:**
        - Below 76% utilization: Stay in cloud
        - Above 76% steady-state: Consider hybrid
        - Above 85% predictable: Data center viable
        - Most companies achieve 40-60%, so cloud remains optimal

=== "H-7: Opportunity Cost Evaluation"
    
    ### Scenario
    Your team of 5 engineers wants to spend 6 months building a custom CI/CD pipeline instead of using GitHub Actions ($500/month).
    
    **Question:** Calculate the true opportunity cost of this decision.
    
    ??? tip "Hint"
        Consider not just the development cost, but what else those engineers could build.
    
    ??? success "Expected Answer"
        **Custom Build Costs:**
        - Development: 5 engineers × 6 months × $15K = $450,000
        - Annual maintenance (30%): $135,000
        - 3-year TCO: $450,000 + (2 × $135,000) = **$720,000**
        
        **GitHub Actions Costs:**
        - Monthly: $500
        - Setup: $10,000
        - 3-year TCO: $10,000 + (36 × $500) = **$28,000**
        
        **Opportunity Cost Analysis:**
        - Direct cost difference: $692,000
        - What 5 engineers could build in 6 months:
          - New feature revenue potential: $2,000,000
          - Technical debt reduction: $500,000
          - Performance improvements: $300,000
        - **Total opportunity cost: $3,492,000**
        
        **Decision: Absolutely use GitHub Actions**
        - Building CI/CD is not a differentiator
        - Opportunity cost is 125x the vendor cost
        - Engineers should focus on business value

=== "H-8: Economic Trade-off Matrix"
    
    ### Scenario
    Design choices for a new service:
    - Option A: Serverless (Higher per-request cost, zero idle cost)
    - Option B: Containers (Lower per-request cost, idle cost exists)
    
    **Question:** At what request volume does each option become optimal?
    
    ??? tip "Hint"
        Create a cost function for each option and find the intersection point.
    
    ??? success "Expected Answer"
        **Serverless Cost Model:**
        - Cost per million requests: $3.50
        - Cost per GB-second: $0.00001667
        - Average request: 200ms, 256MB
        - Cost per request: $0.0000035 + $0.00000085 = $0.0000044
        
        **Container Cost Model:**
        - Fixed cost (2 containers minimum): $100/month
        - Variable cost per request: $0.0000015
        - Cost = $100 + (requests × $0.0000015)
        
        **Break-even Calculation:**
        - Serverless = Containers when:
        - Requests × $0.0000044 = $100 + (Requests × $0.0000015)
        - Requests × $0.0000029 = $100
        - **Break-even: 34.5 million requests/month**
        
        **Recommendation:**
        - < 34.5M requests/month: Use Serverless
        - > 34.5M requests/month: Use Containers
        - Consider hybrid: Serverless for variable, Containers for baseline

---

## Section 2: Very Hard Questions (3 hours)

=== "VH-1: Multi-Dimensional Economic Analysis"
    
    ### Challenge
    Your startup has $2M runway. Options:
    1. Build MVP with full team (burn $200K/month)
    2. Outsource MVP, keep core team (burn $100K/month)
    3. Use no-code/low-code platform (burn $50K/month)
    
    Create a comprehensive economic analysis considering time-to-market, quality, and technical debt.
    
    ??? example "Model Answer"
        **Option 1: Full Team Build**
        - Time to MVP: 4 months
        - Cost to MVP: $800,000
        - Quality: High (custom, scalable)
        - Technical debt: Low
        - Remaining runway: 6 months
        - Success probability: 60%
        
        **Option 2: Outsource**
        - Time to MVP: 6 months  
        - Cost to MVP: $600,000
        - Quality: Medium (communication overhead)
        - Technical debt: Medium (knowledge transfer issues)
        - Remaining runway: 14 months
        - Success probability: 45%
        
        **Option 3: No-Code Platform**
        - Time to MVP: 2 months
        - Cost to MVP: $100,000
        - Quality: Low (platform limitations)
        - Technical debt: High (platform lock-in)
        - Remaining runway: 38 months
        - Success probability: 70%
        
        **Economic Decision Matrix:**
        ```
        Factor          | Weight | Opt 1 | Opt 2 | Opt 3
        ----------------|--------|-------|-------|-------
        Time to Market  |  30%   |  7    |  5    |  10
        Cost Efficiency |  25%   |  3    |  5    |  10
        Quality         |  20%   |  10   |  6    |  4
        Runway          |  15%   |  3    |  6    |  10
        Flexibility     |  10%   |  10   |  7    |  3
        ----------------|--------|-------|-------|-------
        Weighted Score  |        |  6.35 |  5.65 |  8.05
        ```
        
        **Recommendation: Option 3 (No-Code) with Migration Plan**
        1. Launch MVP in 2 months for $100K
        2. Validate product-market fit with real users
        3. Use extended runway to iterate rapidly
        4. Plan migration to custom solution after validation
        5. Total success probability: 70% × 90% (migration) = 63%
        
        **Economic Rationale:**
        - Maximizes learning per dollar spent
        - 38-month runway allows multiple pivots
        - Technical debt is acceptable for validation phase
        - Migration cost ($500K) only incurred after validation

=== "VH-2: Complex TCO Comparison"
    
    ### Challenge
    Compare 5-year TCO for three database architectures:
    1. Single PostgreSQL RDS instance
    2. Aurora Serverless  
    3. DynamoDB
    
    For a workload growing from 1M to 100M records with 1000 to 50,000 TPS.
    
    ??? example "Model Answer"
        **Workload Evolution:**
        - Year 1: 1M records, 1000 TPS
        - Year 2: 5M records, 5000 TPS
        - Year 3: 20M records, 15000 TPS
        - Year 4: 50M records, 30000 TPS
        - Year 5: 100M records, 50000 TPS
        
        **Option 1: PostgreSQL RDS**
        ```
        Year | Instance Type | Storage | Cost/Month | Annual
        -----|---------------|---------|------------|--------
        1    | db.r6g.xlarge | 100GB   | $500      | $6,000
        2    | db.r6g.2xlarge| 500GB   | $1,200    | $14,400
        3    | db.r6g.4xlarge| 2TB     | $3,500    | $42,000
        4    | db.r6g.8xlarge| 5TB     | $8,000    | $96,000
        5    | Multi-master  | 10TB    | $18,000   | $216,000
        ```
        - 5-year TCO: $374,400
        - Plus migration costs: $50,000
        - **Total: $424,400**
        
        **Option 2: Aurora Serverless v2**
        ```
        Year | ACUs    | Storage | Cost/Month | Annual
        -----|---------|---------|------------|--------
        1    | 2-4     | 100GB   | $800      | $9,600
        2    | 4-16    | 500GB   | $2,500    | $30,000
        3    | 8-32    | 2TB     | $5,200    | $62,400
        4    | 16-64   | 5TB     | $10,500   | $126,000
        5    | 32-128  | 10TB    | $21,000   | $252,000
        ```
        - 5-year TCO: $480,000
        - Auto-scaling benefit: -$50,000
        - **Total: $430,000**
        
        **Option 3: DynamoDB**
        ```
        Year | WCU/RCU | Storage | Cost/Month | Annual
        -----|---------|---------|------------|--------
        1    | 100/500 | 1GB     | $400      | $4,800
        2    | 500/2500| 5GB     | $1,800    | $21,600
        3    | 1500/7500| 20GB   | $5,500    | $66,000
        4    | 3000/15000| 50GB  | $11,000   | $132,000
        5    | 5000/25000| 100GB | $18,500   | $222,000
        ```
        - 5-year TCO: $446,400
        - No maintenance windows: -$30,000
        - **Total: $416,400**
        
        **Recommendation: DynamoDB**
        - Lowest 5-year TCO
        - Best scaling characteristics
        - No maintenance overhead
        - Serverless operation model
        - Trade-off: Must design for NoSQL patterns

=== "VH-3: Economic Architecture Redesign"
    
    ### Challenge
    Current architecture costs $1M/year and supports 1M users. Design a new architecture that can support 10M users for less than $5M/year. Show your economic reasoning.
    
    ??? example "Model Answer"
        **Current Architecture Analysis:**
        - Cost per user: $1.00/month
        - Linear scaling would cost: $10M/year for 10M users
        - Target: $5M/year = $0.50/user/month
        - Required efficiency gain: 50%
        
        **Redesign Strategy:**
        
        **1. Caching Layer (30% reduction)**
        - Add Redis/Memcached: $50K/year
        - Reduce database load by 70%
        - Save on database costs: $300K/year
        - Net savings: $250K/year
        
        **2. CDN Implementation (20% reduction)**
        - CloudFront/Fastly: $100K/year
        - Reduce origin traffic by 80%
        - Save on bandwidth: $300K/year
        - Net savings: $200K/year
        
        **3. Auto-scaling + Spot Instances (25% reduction)**
        - Replace fixed capacity with auto-scaling
        - Use spot instances for batch jobs
        - Savings: $250K/year
        
        **4. Multi-tenant Architecture (35% reduction)**
        - Consolidate per-customer resources
        - Improve density from 100 to 1000 users/instance
        - Savings: $350K/year
        
        **5. Serverless for Variable Workloads (15% reduction)**
        - Move batch processing to Lambda
        - API Gateway for spiky endpoints
        - Savings: $150K/year
        
        **New Architecture Costs at 10M users:**
        - Base infrastructure: $2,000,000
        - Caching layer: $100,000
        - CDN: $400,000
        - Auto-scaling overhead: $100,000
        - Serverless compute: $300,000
        - Monitoring/Operations: $500,000
        - **Total: $3,400,000/year**
        - **Cost per user: $0.34/month**
        
        **Economic Validation:**
        - Target: $5M/year ✓ (Achieved $3.4M)
        - Per-user cost: $0.34 < $0.50 ✓
        - ROI on redesign: 250% in year 1
        - Break-even: Month 5

=== "VH-4: Technical Debt Portfolio Management"
    
    ### Challenge
    You've inherited a system with multiple technical debts. Create a paydown strategy that maximizes ROI given a $500K annual budget.
    
    Technical Debts:
    1. Database schema issues: $50K to fix, costs $100K/year
    2. Missing tests: $200K to fix, costs $150K/year
    3. Monolith coupling: $500K to fix, costs $300K/year
    4. Poor monitoring: $30K to fix, costs $80K/year
    5. Manual deployments: $100K to fix, costs $200K/year
    
    ??? example "Model Answer"
        **Debt Analysis Matrix:**
        ```
        Debt         | Fix Cost | Annual Cost | Interest Rate | ROI    | Priority
        -------------|----------|-------------|---------------|--------|----------
        DB Schema    | $50K     | $100K       | 200%          | 100%   | 2
        Missing Tests| $200K    | $150K       | 75%           | -25%   | 5
        Monolith     | $500K    | $300K       | 60%           | -40%   | 4
        Monitoring   | $30K     | $80K        | 267%          | 167%   | 1
        Deployments  | $100K    | $200K       | 200%          | 100%   | 3
        ```
        
        **Year 1 Strategy ($500K budget):**
        1. **Fix Monitoring** (Month 1)
           - Cost: $30K
           - Saves: $80K/year
           - ROI: 167%
        
        2. **Fix DB Schema** (Month 2-3)
           - Cost: $50K  
           - Saves: $100K/year
           - ROI: 100%
        
        3. **Fix Deployments** (Month 4-6)
           - Cost: $100K
           - Saves: $200K/year
           - ROI: 100%
        
        4. **Partial Test Coverage** (Month 7-12)
           - Cost: $200K
           - Saves: $150K/year
           - ROI: -25% year 1, 50% year 2
        
        5. **Begin Monolith Decomposition** (Month 11-12)
           - Cost: $120K (remaining budget)
           - Saves: $72K/year (partial)
           
        **Results:**
        - Year 1 investment: $500K
        - Year 1 savings: $602K
        - Year 1 ROI: 20.4%
        - Cumulative 3-year savings: $2.1M
        - All debts cleared by year 2
        
        **Key Insights:**
        - Prioritize by interest rate, not fix cost
        - Quick wins fund larger improvements
        - Partial fixes can be valuable
        - Compound savings accelerate paydown

=== "VH-5: Economic Decision Tree"
    
    ### Challenge
    Create a decision tree for choosing between serverless, containers, and VMs based on economic factors. Include specific thresholds and calculations.
    
    ??? example "Model Answer"
        **Economic Decision Tree:**
        
        ```
        START: What's your workload pattern?
        │
        ├─> Highly Variable (>10x daily variation)
        │   │
        │   └─> Request volume?
        │       ├─> <1M/month → SERVERLESS
        │       │   Reason: Pay only for actual use
        │       │   Cost: ~$5-50/month
        │       │
        │       ├─> 1M-50M/month → Evaluate duration
        │       │   ├─> <1 second → SERVERLESS
        │       │   │   Cost: ~$50-500/month
        │       │   └─> >1 second → CONTAINERS with auto-scaling
        │       │       Cost: ~$200-2000/month
        │       │
        │       └─> >50M/month → CONTAINERS
        │           Reason: Serverless becomes expensive
        │           Cost: ~$1000-5000/month
        │
        ├─> Steady State (<2x daily variation)
        │   │
        │   └─> Predictable growth?
        │       ├─> Yes → VMs with reserved instances
        │       │   Savings: 40-70% vs on-demand
        │       │   Cost: Most economical for steady loads
        │       │
        │       └─> No → CONTAINERS
        │           Reason: Balance of flexibility and cost
        │           Cost: 20-30% premium vs VMs
        │
        └─> Batch/Scheduled
            │
            └─> Run frequency?
                ├─> <Daily → SERVERLESS
                │   Reason: No idle costs
                │   Example: $10 for 1hr/day vs $730 for VM
                │
                ├─> Daily-Hourly → CONTAINERS with CronJobs
                │   Reason: Warm start benefits
                │   Cost: ~$100-500/month
                │
                └─> Continuous → VMs
                    Reason: Lowest per-hour cost
                    Cost: Reserved instances optimal
        
        ECONOMIC THRESHOLDS:
        - Serverless → Containers: ~30M requests/month
        - Containers → VMs: >70% utilization
        - On-demand → Reserved: >40% utilization
        - Single region → Multi-region: >$100K monthly spend
        ```
        
        **Cost Calculation Examples:**
        
        1. **API with 10M requests/month, 200ms average:**
           - Serverless: 10M × $0.0000035 + compute = $385/month
           - Containers: 3 × t3.medium = $120/month
           - **Winner: Containers (69% cheaper)**
        
        2. **Batch job running 2 hours daily:**
           - Serverless: 2hr × $0.05 × 30 = $90/month
           - Container: Limited by minimum cluster = $200/month
           - VM: t3.large reserved = $38/month
           - **Winner: VM (58% cheaper than serverless)**
        
        3. **Microservice with 100 requests/minute:**
           - Serverless: 4.3M × $0.0000035 = $15/month
           - Container: Minimum viable = $40/month
           - **Winner: Serverless (63% cheaper)**

---

## Grading Rubric

!!! abstract "Assessment Criteria"
    
    ### Hard Section (80 points total)
    | Criterion | Points | What We Look For |
    |-----------|--------|-------------------|
    | **Accurate Calculations** | 30 | Correct application of formulas and multipliers |
    | **Economic Reasoning** | 25 | Clear financial thinking and trade-off analysis |
    | **Practical Solutions** | 15 | Realistic, implementable recommendations |
    | **ROI Thinking** | 10 | Considers returns and payback periods |
    
    **Passing Score:** 60/80 (75%)
    
    ### Very Hard Section (120 points total)
    | Criterion | Points | What We Look For |
    |-----------|--------|-------------------|
    | **Comprehensive Analysis** | 40 | Considers all economic factors |
    | **Strategic Thinking** | 30 | Long-term economic planning |
    | **Quantitative Rigor** | 30 | Detailed calculations and models |
    | **Business Alignment** | 20 | Links technical decisions to business value |
    
    **Passing Score:** 90/120 (75%)

## Study Tips

!!! tip "Exam Preparation"
    1. **Master the Multipliers**
       - Memorize the 1.85x cloud multiplier
       - Understand the 78% technical debt rate
       - Know the $10M build vs buy threshold
    
    2. **Practice Financial Calculations**
       - Work through TCO comparisons
       - Calculate ROI for real decisions
       - Build cost models in spreadsheets
    
    3. **Think Like a CFO**
       - Every decision has opportunity cost
       - Time value of money matters
       - Risk has economic value
    
    4. **Use Real Examples**
       - Analyze your current infrastructure costs
       - Calculate technical debt in your systems
       - Practice making business cases

## Answer Submission

!!! info "How to Submit"
    For self-study, structure your answers as:
    ```
    /tests/answers/law7-exam/
    ├── h1-hidden-costs.md
    ├── h2-technical-debt.md
    ├── h3-build-vs-buy.md
    ├── h4-unit-economics.md
    ├── h5-roi-analysis.md
    ├── h6-cloud-vs-onprem.md
    ├── h7-opportunity-cost.md
    ├── h8-economic-tradeoff.md
    ├── vh1-multi-dimensional.md
    ├── vh2-complex-tco.md
    ├── vh3-architecture-redesign.md
    ├── vh4-debt-portfolio.md
    └── vh5-decision-tree.md
    ```

---

*Remember: This exam tests your ability to think economically about technical decisions. The best engineers understand that technology serves business value, not the other way around.*
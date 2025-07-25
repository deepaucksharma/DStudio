# Amazon System Design Interview Guide

<div class="axiom-box">
<h3>⚡ Quick Reference</h3>
<ul>
<li><strong>Focus:</strong> Leadership Principles + Technical Excellence</li>
<li><strong>Unique:</strong> Operational rigor, cost consciousness, customer obsession</li>
<li><strong>Scale:</strong> Design for 10x growth, millions of RPS</li>
<li><strong>Mindset:</strong> Day 1 mentality, two-pizza teams, working backwards</li>
</ul>
</div>

## Amazon vs Other Tech Companies

| Aspect | Amazon | Google/Meta | Microsoft |
|--------|---------|-------------|------------|
| **Primary Focus** | Customer + Operations | Technical Innovation | Enterprise Integration |
| **Scale Philosophy** | Frugal, constraint-driven | Unlimited resources | Hybrid cloud |
| **Team Structure** | Two-pizza teams | Large eng teams | Cross-functional |
| **Design Approach** | Working backwards | Technology first | Platform thinking |
| **Key Metrics** | Cost, latency, availability | Innovation, scale | Compatibility, security |
| **Failure Handling** | Mechanisms > intentions | Redundancy | Graceful degradation |

## Leadership Principles → System Design Matrix

<div class="decision-box">
<h3>🎯 Leadership Principles Quick Reference</h3>
<table>
<tr>
<th>Principle</th>
<th>System Design Application</th>
<th>Key Questions</th>
</tr>
<tr>
<td><strong>Customer Obsession</strong></td>
<td>Start with use cases, optimize for CX metrics</td>
<td>What's the customer impact? Latency SLA?</td>
</tr>
<tr>
<td><strong>Ownership</strong></td>
<td>Design for operations, long-term thinking</td>
<td>Who owns this at 3am? 5-year TCO?</td>
</tr>
<tr>
<td><strong>Invent & Simplify</strong></td>
<td>Remove complexity, innovate through constraints</td>
<td>Can we eliminate this component?</td>
</tr>
<tr>
<td><strong>Are Right, A Lot</strong></td>
<td>Data-driven decisions, learn from prod</td>
<td>What data supports this choice?</td>
</tr>
<tr>
<td><strong>Think Big</strong></td>
<td>Design for 10x scale from day one</td>
<td>What breaks at 10x load?</td>
</tr>
<tr>
<td><strong>Bias for Action</strong></td>
<td>MVP first, iterate fast, reversible decisions</td>
<td>Can we ship v1 in 2 weeks?</td>
</tr>
<tr>
<td><strong>Frugality</strong></td>
<td>Cost-aware architecture, do more with less</td>
<td>What's the cost per transaction?</td>
</tr>
<tr>
<td><strong>Dive Deep</strong></td>
<td>Know bottlenecks, understand failure modes</td>
<td>What's the p99 latency breakdown?</td>
</tr>
</table>
</div>

```mermaid
graph LR
    A[Customer Problem] -->|Working Backwards| B[Press Release]
    B --> C[System Requirements]
    C --> D{Design Decisions}
    D -->|Customer Obsession| E[Latency < 100ms]
    D -->|Frugality| F[Cost < $0.01/req]
    D -->|Think Big| G[Scale to 1M RPS]
    D -->|Ownership| H[24/7 Operations]
    E & F & G & H --> I[Final Architecture]
```

## Amazon's Unique Design Philosophy

<div class="truth-box">
<h3>💡 The Amazon Difference</h3>
<table>
<tr>
<th>Concept</th>
<th>Implementation</th>
<th>Anti-Pattern</th>
</tr>
<tr>
<td><strong>Operational Excellence</strong></td>
<td>• Runbooks for every alert<br>• Metrics dashboard from day 1<br>• On-call rotation planned</td>
<td>"We'll add monitoring later"</td>
</tr>
<tr>
<td><strong>Cost Consciousness</strong></td>
<td>• $/request calculated<br>• Auto-scaling policies<br>• Reserved capacity planning</td>
<td>"Hardware is cheap"</td>
</tr>
<tr>
<td><strong>Working Backwards</strong></td>
<td>• Start with press release<br>• Define success metrics<br>• MVP in 2 weeks</td>
<td>"Let's build it and see"</td>
</tr>
<tr>
<td><strong>Two-Pizza Teams</strong></td>
<td>• 6-10 person ownership<br>• Full stack responsibility<br>• Independent deployment</td>
<td>"The platform team handles that"</td>
</tr>
<tr>
<td><strong>Mechanisms > Intentions</strong></td>
<td>• Automated deployments<br>• Self-healing systems<br>• Policy as code</td>
<td>"The team will remember"</td>
</tr>
</table>
<p style="margin-top: 10px; font-style: italic;">Related: <a href="/part2-pillars/control/">Control Distribution</a>, <a href="/part1-axioms/law1-failure/">Correlated Failure</a></p>
</div>

```mermaid
graph TB
    subgraph "Two-Pizza Team Structure"
        A[Product Manager] --> B[Team Lead]
        B --> C[2-3 Backend Engineers]
        B --> D[1-2 Frontend Engineers]
        B --> E[1 DevOps/SRE]
        B --> F[1 Data Engineer]
        
        G[Full Ownership] --> H[Design]
        G --> I[Build]
        G --> J[Deploy]
        G --> K[Operate]
        G --> L[Iterate]
    end
```

## System Design Questions by Category

<div class="decision-box">
<h3>📋 Question Difficulty & Focus Areas</h3>
<table>
<tr>
<th>Category</th>
<th>Example Questions</th>
<th>Key Challenges</th>
<th>Leadership Focus</th>
</tr>
<tr>
<td><strong>E-Commerce</strong></td>
<td>• Product Catalog<br>• Shopping Cart<br>• Order System</td>
<td>Scale, consistency, latency</td>
<td>Customer Obsession, Frugality</td>
</tr>
<tr>
<td><strong>AWS Services</strong></td>
<td>• <a href="s3.md">S3</a><br>• <a href="dynamodb.md">DynamoDB</a><br>• Lambda</td>
<td>Multi-tenancy, durability, cost</td>
<td>Think Big, Dive Deep</td>
</tr>
<tr>
<td><strong>Logistics</strong></td>
<td>• Last-mile delivery<br>• Route optimization<br>• Inventory</td>
<td>Real-time optimization, constraints</td>
<td>Deliver Results, Ownership</td>
</tr>
<tr>
<td><strong>Streaming</strong></td>
<td>• <a href="prime-video.md">Prime Video</a><br>• Twitch<br>• Music</td>
<td>CDN, buffering, quality adaptation</td>
<td>Customer Obsession, Innovation</td>
</tr>
</table>
<p style="margin-top: 10px; font-style: italic;">See also: <a href="/part2-pillars/work/">Work Distribution</a> for scaling strategies</p>
</div>

```mermaid
graph TB
    subgraph "Common Architecture Pattern"
        Client[Client Apps] --> ALB[Application Load Balancer]
        ALB --> API[API Gateway]
        API --> MS1[Microservice 1<br/>Product Catalog]
        API --> MS2[Microservice 2<br/>Shopping Cart]
        API --> MS3[Microservice 3<br/>Order Service]
        
        MS1 --> Cache1[ElastiCache]
        MS1 --> DB1[(DynamoDB)]
        
        MS2 --> Cache2[ElastiCache]
        MS2 --> DB2[(DynamoDB)]
        
        MS3 --> Queue[SQS/Kinesis]
        Queue --> Worker[Workers]
        Worker --> DB3[(Aurora)]
        
        MS1 & MS2 & MS3 --> S3[S3 Storage]
        MS1 & MS2 & MS3 --> CW[CloudWatch]
    end
```

## Interview Process Timeline

```mermaid
gantt
    title Amazon Interview Process
    dateFormat X
    axisFormat %s
    
    section Phone Screen
    System Design (45-60min) :active, 0, 60
    
    section Onsite Loop
    System Design 1 :active, 0, 60
    System Design 2 :active, 70, 60
    Coding 1 :140, 60
    Coding 2 :210, 60
    Behavioral :280, 60
    Bar Raiser :350, 60
```

<div class="axiom-box">
<h3>⏱️ System Design Round Breakdown</h3>
<table>
<tr>
<th>Phase</th>
<th>Time</th>
<th>Focus</th>
<th>Deliverables</th>
</tr>
<tr>
<td><strong>1. Requirements</strong></td>
<td>5-10 min</td>
<td>• Functional/Non-functional<br>• Scale (QPS, storage)<br>• Constraints (cost, latency)</td>
<td>• Use cases list<br>• Numbers (100M users, 10K QPS)<br>• SLAs (99.9%, <100ms)</td>
</tr>
<tr>
<td><strong>2. High-Level</strong></td>
<td>10-15 min</td>
<td>• Architecture diagram<br>• Component interaction<br>• API design</td>
<td>• Box & arrow diagram<br>• REST/gRPC APIs<br>• Data flow</td>
</tr>
<tr>
<td><strong>3. Deep Dive</strong></td>
<td>15-20 min</td>
<td>• Data models<br>• Algorithms<br>• Technology choices</td>
<td>• Schema design<br>• Consistency strategy<br>• Tech stack justification</td>
</tr>
<tr>
<td><strong>4. Scale</strong></td>
<td>10-15 min</td>
<td>• Bottlenecks<br>• Optimization<br>• Cost analysis</td>
<td>• Performance calculations<br>• Caching strategy<br>• $/request analysis</td>
</tr>
<tr>
<td><strong>5. Operations</strong></td>
<td>5-10 min</td>
<td>• Monitoring<br>• Deployment<br>• Failure modes</td>
<td>• Metrics & alerts<br>• Rollout strategy<br>• Disaster recovery</td>
</tr>
</table>
<p style="margin-top: 10px; font-style: italic;">Master <a href="/part1-axioms/law2-asynchrony/">Asynchronous Reality</a> before deep dives</p>
</div>

## 12-Week Preparation Roadmap

```mermaid
gantt
    title Amazon Interview Prep Timeline
    dateFormat YYYY-MM-DD
    axisFormat Week %W
    
    section Foundations
    7 Laws & 5 Pillars :done, 2024-01-01, 14d
    Consistency & CAP :active, 2024-01-08, 7d
    
    section Amazon Core
    Leadership Principles :2024-01-15, 7d
    Operational Excellence :2024-01-22, 7d
    
    section Patterns
    Sharding & Caching :2024-01-29, 7d
    Event-Driven & Mesh :2024-02-05, 7d
    
    section AWS Deep Dive
    DynamoDB & S3 :2024-02-12, 7d
    Lambda & Kinesis :2024-02-19, 7d
    
    section Practice
    System Designs :2024-02-26, 14d
    Mock Interviews :2024-03-12, 14d
```

<div class="decision-box">
<h3>📚 Priority Study Matrix</h3>
<table>
<tr>
<th>Week</th>
<th>Must Do</th>
<th>Should Do</th>
<th>Nice to Have</th>
</tr>
<tr>
<td><strong>1-2</strong></td>
<td>• <a href="/part1-axioms/">7 Laws</a><br>• <a href="/part2-pillars/">5 Pillars</a></td>
<td>• CAP Theorem<br>• Consistency Models</td>
<td>• Failure stories</td>
</tr>
<tr>
<td><strong>3-4</strong></td>
<td>• <a href="leadership-principles.md">Leadership Principles</a><br>• Two-pizza teams</td>
<td>• Working Backwards<br>• Day 1 mentality</td>
<td>• Amazon history</td>
</tr>
<tr>
<td><strong>5-6</strong></td>
<td>• <a href="/patterns/sharding">Sharding</a><br>• <a href="/patterns/caching-strategies">Caching</a></td>
<td>• Event sourcing<br>• CQRS</td>
<td>• Service mesh</td>
</tr>
<tr>
<td><strong>7-8</strong></td>
<td>• <a href="dynamodb.md">DynamoDB</a><br>• <a href="s3.md">S3</a></td>
<td>• Lambda<br>• SQS/SNS</td>
<td>• Kinesis</td>
</tr>
<tr>
<td><strong>9-12</strong></td>
<td>• 10 practice problems<br>• 5 mock interviews</td>
<td>• Behavioral stories<br>• Failure scenarios</td>
<td>• Edge cases</td>
</tr>
</table>
<p style="margin-top: 10px; font-style: italic;">Foundation: <a href="/part1-axioms/">7 Laws</a> → <a href="/part2-pillars/">5 Pillars</a> → Patterns → Practice</p>
</div>

## Amazon Technology Stack

<div class="truth-box">
<h3>🛠️ Core Technologies Comparison</h3>
<table>
<tr>
<th>Service</th>
<th>Use Case</th>
<th>Scale</th>
<th>Trade-offs</th>
</tr>
<tr>
<td><strong>DynamoDB</strong></td>
<td>NoSQL, high throughput</td>
<td>Millions TPS</td>
<td>✅ Predictable performance<br>❌ Query flexibility</td>
</tr>
<tr>
<td><strong>S3</strong></td>
<td>Object storage</td>
<td>Trillions of objects</td>
<td>✅ 11 9s durability<br>❌ Not for small files</td>
</tr>
<tr>
<td><strong>SQS</strong></td>
<td>Message queue</td>
<td>Unlimited</td>
<td>✅ Simple, reliable<br>❌ No ordering (standard)</td>
</tr>
<tr>
<td><strong>Lambda</strong></td>
<td>Event-driven compute</td>
<td>1000s concurrent</td>
<td>✅ No servers<br>❌ 15min limit, cold starts</td>
</tr>
<tr>
<td><strong>Kinesis</strong></td>
<td>Real-time streaming</td>
<td>GB/sec</td>
<td>✅ Real-time processing<br>❌ 7-day retention</td>
</tr>
</table>
<p style="margin-top: 10px; font-style: italic;">Applies <a href="/part2-pillars/state/">State Distribution</a> & <a href="/part2-pillars/truth/">Truth Distribution</a> principles</p>
</div>

```mermaid
graph LR
    subgraph "Amazon Internal Stack"
        A[Coral Service Framework] --> B[Service Mesh]
        C[Brazil Build] --> D[Package Management]
        E[Apollo Deploy] --> F[Blue-Green Deployment]
        G[Slapshot] --> H[Load Testing]
        I[Datapath] --> J[ETL Pipelines]
    end
    
    subgraph "Maps to AWS"
        B --> K[App Mesh]
        D --> L[CodeBuild]
        F --> M[CodeDeploy]
        H --> N[Distributed Load Testing]
        J --> O[Glue/EMR]
    end
```

## Success Checklist

<div class="failure-vignette">
<h3>🚨 Common Failure Modes</h3>
<table>
<tr>
<th>Mistake</th>
<th>Why It Fails</th>
<th>Do Instead</th>
</tr>
<tr>
<td>"We'll use Kubernetes"</td>
<td>Over-engineering, high operational cost</td>
<td>Start with EC2 + ALB, evolve if needed</td>
</tr>
<tr>
<td>"Infinite scale design"</td>
<td>Ignores cost, unrealistic</td>
<td>Design for 10x with cost targets</td>
</tr>
<tr>
<td>"Perfect consistency"</td>
<td>Impossible in distributed systems</td>
<td>Define consistency boundaries</td>
</tr>
<tr>
<td>"We'll monitor later"</td>
<td>Violates operational excellence</td>
<td>Metrics from day 1</td>
</tr>
<tr>
<td>"The team will handle it"</td>
<td>No mechanisms</td>
<td>Automate everything possible</td>
</tr>
</table>
<p style="margin-top: 10px; font-style: italic;">Violates <a href="/part1-axioms/law5-epistemology/">Distributed Knowledge</a> principles</p>
</div>

<div class="axiom-box">
<h3>✅ Success Formula</h3>
<ol>
<li><strong>Customer First:</strong> "This reduces checkout time from 3 clicks to 1"</li>
<li><strong>Numbers Always:</strong> "At 100K QPS, this costs $0.002/request"</li>
<li><strong>Failure Planning:</strong> "When AZ fails, we failover in <30s"</li>
<li><strong>Operations Ready:</strong> "P99 latency dashboard, PagerDuty integration"</li>
<li><strong>Team Ownership:</strong> "6-person team owns build/run/iterate"</li>
</ol>
</div>  

## Quick Reference Architecture Patterns

```mermaid
graph TB
    subgraph "Cell-Based Architecture"
        LB[Load Balancer] --> Cell1[Cell 1<br/>Complete Stack]
        LB --> Cell2[Cell 2<br/>Complete Stack]
        LB --> Cell3[Cell 3<br/>Complete Stack]
        
        Cell1 --> DB1[(Cell 1 DB)]
        Cell2 --> DB2[(Cell 2 DB)]
        Cell3 --> DB3[(Cell 3 DB)]
    end
    
    subgraph "Benefits"
        B1[Blast Radius Reduction]
        B2[Independent Scaling]
        B3[Simplified Testing]
    end
```

<div class="decision-box">
<h3>🎯 Pattern Selection Guide</h3>
<table>
<tr>
<th>Pattern</th>
<th>When to Use</th>
<th>Amazon Example</th>
<th>Key Benefit</th>
</tr>
<tr>
<td><strong>Cell-Based</strong></td>
<td>Multi-tenant isolation</td>
<td>Route 53, DynamoDB</td>
<td>Blast radius control</td>
</tr>
<tr>
<td><strong>Shuffle Sharding</strong></td>
<td>Shared resource pools</td>
<td>ALB target groups</td>
<td>Failure isolation</td>
</tr>
<tr>
<td><strong>Backpressure</strong></td>
<td>Async processing</td>
<td>Kinesis, SQS</td>
<td>System stability</td>
</tr>
<tr>
<td><strong>Circuit Breaker</strong></td>
<td>External dependencies</td>
<td>Service calls</td>
<td>Fast failure</td>
</tr>
</table>
<p style="margin-top: 10px; font-style: italic;">Implements <a href="/patterns/circuit-breaker">Circuit Breaker</a> & <a href="/patterns/bulkhead">Bulkhead</a> patterns</p>
</div>

## Final Success Formula

<div class="axiom-box">
<h3>🎯 The Amazon System Design Equation</h3>
<p style="text-align: center; font-size: 1.2em; font-weight: bold;">
Customer Value × Operational Excellence × Cost Efficiency = Success
</p>
</div>

```mermaid
graph LR
    A[Start] --> B{Customer Problem?}
    B -->|Yes| C[Working Backwards]
    B -->|No| X[❌ Stop]
    C --> D{Can we build it?}
    D -->|Yes| E[Design for Operations]
    D -->|No| C
    E --> F{Cost < Value?}
    F -->|Yes| G[✅ Ship It!]
    F -->|No| H[Simplify & Iterate]
    H --> C
    G --> I[Monitor & Optimize]
    I --> J[Day 1 Forever]
```

<div class="truth-box">
<h3>💪 Remember: It's Always Day 1</h3>
<ul>
<li><strong>Customer Obsession:</strong> Every decision starts and ends with customer impact</li>
<li><strong>Long-term Value:</strong> Build for decades, not quarters</li>
<li><strong>Mechanisms:</strong> Automate good intentions into systems</li>
<li><strong>Frugality:</strong> Constraints breed innovation</li>
<li><strong>Ownership:</strong> You build it, you run it</li>
</ul>
<p style="margin-top: 10px;">Success = Mastery of <a href="/part1-axioms/law7-economics/">Economic Reality</a> + <a href="/part2-pillars/intelligence/">Intelligence Distribution</a></p>
</div>
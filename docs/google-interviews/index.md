# Google System Design Interview Guide

<div class="google-interview-hero">
<h1>🚀 Master Google System Design Interviews</h1>
<p>Comprehensive guide to Google's unique approach to system design interviews</p>
</div>

## 🎯 Quick Decision Guide

```mermaid
graph TD
    Start["Starting Your Prep Journey"] --> Level{What's Your Level?}
    
    Level -->|New Grad| NG[Focus on Fundamentals]
    Level -->|Mid-Level| ML[Balance Theory & Practice]
    Level -->|Senior+| SR[Deep Dive & Leadership]
    
    NG --> Time1{Time Available?}
    ML --> Time2{Time Available?}
    SR --> Time3{Time Available?}
    
    Time1 -->|< 4 weeks| Express1[Express Track]
    Time1 -->|4-8 weeks| Standard1[Standard Track]
    Time1 -->|> 8 weeks| Deep1[Deep Track]
    
    Time2 -->|< 4 weeks| Express2[Express Track]
    Time2 -->|4-8 weeks| Standard2[Standard Track]
    Time2 -->|> 8 weeks| Deep2[Deep Track]
    
    Time3 -->|< 4 weeks| Express3[Express Track]
    Time3 -->|4-8 weeks| Standard3[Standard Track]
    Time3 -->|> 8 weeks| Deep3[Deep Track]
    
    Express1 --> Plan1["✅ Core Systems Only<br/>✅ 3 Mock Interviews<br/>✅ Cheat Sheets"]
    Standard1 --> Plan2["✅ All Fundamentals<br/>✅ 5 System Designs<br/>✅ 5 Mock Interviews"]
    Deep1 --> Plan3["✅ Read Papers<br/>✅ 10+ Designs<br/>✅ Daily Practice"]
    
    Express2 --> Plan4["✅ Pattern Review<br/>✅ 5 Mock Interviews<br/>✅ Scale Focus"]
    Standard2 --> Plan5["✅ Google Tech Deep Dive<br/>✅ 8 System Designs<br/>✅ Weekly Mocks"]
    Deep2 --> Plan6["✅ Master All Patterns<br/>✅ 15+ Designs<br/>✅ Teach Others"]
    
    Express3 --> Plan7["✅ Leadership Scenarios<br/>✅ Complex Systems<br/>✅ Cost Optimization"]
    Standard3 --> Plan8["✅ Architecture Patterns<br/>✅ Trade-off Analysis<br/>✅ Operational Excellence"]
    Deep3 --> Plan9["✅ Research Papers<br/>✅ Novel Solutions<br/>✅ Mentor Others"]
```

## 📋 Interview Types Comparison

<div class="comparison-table">
<table>
<thead>
<tr>
<th>Interview Type</th>
<th>Focus Areas</th>
<th>Duration</th>
<th>Key Expectations</th>
<th>Common Topics</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Phone Screen</strong></td>
<td>• High-level design<br/>• Basic scale awareness<br/>• Communication skills</td>
<td>45 min</td>
<td>• Clear thinking<br/>• Basic patterns<br/>• Ask good questions</td>
<td>• URL shortener<br/>• Chat system<br/>• Basic storage</td>
</tr>
<tr>
<td><strong>Onsite - Junior</strong></td>
<td>• Fundamentals<br/>• Common patterns<br/>• Learning ability</td>
<td>45 min × 2</td>
<td>• Solid basics<br/>• Growth potential<br/>• Coachability</td>
<td>• Social media feed<br/>• File storage<br/>• Messaging</td>
</tr>
<tr>
<td><strong>Onsite - Senior</strong></td>
<td>• Complex systems<br/>• Trade-offs<br/>• Leadership</td>
<td>45 min × 2-3</td>
<td>• Deep expertise<br/>• Novel solutions<br/>• Mentorship</td>
<td>• YouTube<br/>• Google Search<br/>• AdWords</td>
</tr>
<tr>
<td><strong>Onsite - Staff+</strong></td>
<td>• Architecture<br/>• Cross-system design<br/>• Organizational impact</td>
<td>60 min × 2-3</td>
<td>• Vision<br/>• Innovation<br/>• Business sense</td>
<td>• Platform design<br/>• Infrastructure<br/>• ML systems</td>
</tr>
</tbody>
</table>
</div>

## 📊 Success Metrics Dashboard

<div class="metrics-dashboard">
<div class="metric-card">
<h4>Scale Requirements</h4>
<div class="metric-value">1B+ Users</div>
<div class="metric-detail">Global reach expected</div>
</div>
<div class="metric-card">
<h4>Latency Target</h4>
<div class="metric-value"><100ms</div>
<div class="metric-detail">P99 for user-facing</div>
</div>
<div class="metric-card">
<h4>Availability</h4>
<div class="metric-value">99.99%</div>
<div class="metric-detail">4 nines minimum</div>
</div>
<div class="metric-card">
<h4>Design Time</h4>
<div class="metric-value">45 min</div>
<div class="metric-detail">Complete solution</div>
</div>
</div>

<div class="law-box">
<h3>🎯 Key Insight</h3>
<p>Google values candidates who can think at planetary scale while keeping designs simple and maintainable. The best solutions often leverage Google's existing infrastructure patterns.</p>
</div>

## 🏗️ Google's Infrastructure Philosophy

### Core Design Principles

<div class="decision-box">
<h3>1. Start Simple, Scale Incrementally</h3>
<ul>
<li>Begin with MVP (Minimum Viable Product)</li>
<li>Add complexity only when justified by requirements</li>
<li>Document trade-offs at each scaling step</li>
</ul>
</div>

<div class="decision-box">
<h3>2. Use Proven Patterns</h3>
<ul>
<li>Leverage existing Google infrastructure (Bigtable, Spanner, etc.)</li>
<li>Apply well-tested distributed systems patterns</li>
<li>Avoid reinventing the wheel</li>
</ul>
</div>

<div class="decision-box">
<h3>3. Design for Failure</h3>
<ul>
<li>Assume everything will fail</li>
<li>Build redundancy at every layer</li>
<li>Plan for graceful degradation</li>
</ul>
</div>

<div class="decision-box">
<h3>4. Optimize for the Common Case</h3>
<ul>
<li>Make the typical path fast</li>
<li>Handle edge cases separately</li>
<li>Use caching aggressively</li>
</ul>
</div>

## 📊 Scale Requirements at Google

<div class="failure-vignette">
<h3>🌍 Typical Google Scale</h3>
<p><strong>When designing for Google, assume:</strong></p>
<ul>
<li><strong>Users</strong>: 1-2 billion globally</li>
<li><strong>Requests</strong>: 100K-1M requests/second</li>
<li><strong>Data</strong>: Petabytes to Exabytes</li>
<li><strong>Latency</strong>: &lt;100ms p99</li>
<li><strong>Availability</strong>: 99.99%+ (4 nines)</li>
<li><strong>Geo-distribution</strong>: 20+ regions worldwide</li>
</ul>
</div>

## 🗺️ Visual Preparation Roadmap

```mermaid
gantt
    title Google Interview Prep Timeline
    dateFormat  YYYY-MM-DD
    section Foundation
    Distributed Systems Basics    :a1, 2024-01-01, 7d
    7 Laws & 5 Pillars           :a2, after a1, 7d
    Basic Patterns               :a3, after a2, 5d
    
    section Google Tech
    Read Core Papers             :b1, after a2, 5d
    Study Infrastructure         :b2, after b1, 7d
    Practice with Tools          :b3, after b2, 5d
    
    section System Design
    Simple Systems               :c1, after a3, 5d
    Medium Complexity            :c2, after c1, 7d
    Google-Scale Systems         :c3, after c2, 10d
    
    section Mock Practice
    Self Assessment              :d1, after c2, 2d
    Peer Mocks                   :d2, after d1, 5d
    Expert Mocks                 :d3, after d2, 5d
    
    section Final Prep
    Review & Polish              :e1, after d3, 3d
    Mental Preparation           :e2, after e1, 2d
```

## 🧮 Time Allocation Calculator

<div class="calculator-box">
<h3>Personalized Study Plan Calculator</h3>
<div class="calculator-inputs">
<label>Current Level:
<select id="level">
<option value="junior">Junior (0-3 years)</option>
<option value="mid">Mid-level (3-6 years)</option>
<option value="senior">Senior (6+ years)</option>
</select>
</label>
<label>Available Hours/Week:
<input type="number" id="hours" min="5" max="40" value="10">
</label>
<label>Target Date:
<input type="date" id="target-date">
</label>
<button onclick="calculatePlan()">Generate Plan</button>
</div>
<div id="plan-results" class="plan-output"></div>
</div>

## 🔧 Google's Technology Stack

### 📊 Technology Selection Matrix

<div class="tech-matrix">
<table>
<thead>
<tr>
<th>Use Case</th>
<th>Best Choice</th>
<th>Alternative</th>
<th>When to Use</th>
<th>Scale Limit</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Structured Data</strong></td>
<td>Spanner</td>
<td>Cloud SQL</td>
<td>Global consistency needed</td>
<td>Unlimited</td>
</tr>
<tr>
<td><strong>NoSQL</strong></td>
<td>Bigtable</td>
<td>Firestore</td>
<td>Time-series, high throughput</td>
<td>Petabytes</td>
</tr>
<tr>
<td><strong>Object Storage</strong></td>
<td>Cloud Storage</td>
<td>Persistent Disk</td>
<td>Unstructured data, media</td>
<td>Exabytes</td>
</tr>
<tr>
<td><strong>Caching</strong></td>
<td>Memcached</td>
<td>Redis</td>
<td>Session data, hot data</td>
<td>TB in memory</td>
</tr>
<tr>
<td><strong>Message Queue</strong></td>
<td>Pub/Sub</td>
<td>Cloud Tasks</td>
<td>Async processing</td>
<td>1M msgs/sec</td>
</tr>
<tr>
<td><strong>Stream Processing</strong></td>
<td>Dataflow</td>
<td>Dataproc</td>
<td>Real-time analytics</td>
<td>Unlimited</td>
</tr>
<tr>
<td><strong>Batch Processing</strong></td>
<td>Dataflow</td>
<td>Dataproc</td>
<td>ETL, ML training</td>
<td>Unlimited</td>
</tr>
<tr>
<td><strong>ML Serving</strong></td>
<td>Vertex AI</td>
<td>Cloud Run</td>
<td>Model inference</td>
<td>10K QPS</td>
</tr>
</tbody>
</table>
</div>

### Storage Systems

| Technology | Use Case | Key Features |
| **Bigtable** | NoSQL at scale | - Petabyte scale<br>- Wide column store<br>- Strong consistency per row |
| **Spanner** | Global RDBMS | - Globally distributed<br>- ACID transactions<br>- External consistency |
| **Colossus** | File storage | - Successor to GFS<br>- Exabyte scale<br>- Powers all Google storage |
| **Firestore** | Document DB | - Real-time sync<br>- Offline support<br>- Mobile-friendly |

### Processing & Compute

| Technology | Use Case | Key Features |
|------------|----------|--------------|
| **MapReduce** | Batch processing | - Parallel processing<br>- Fault tolerant<br>- Simple programming model |
| **Dataflow** | Stream processing | - Unified batch/stream<br>- Auto-scaling<br>- Exactly-once processing |
| **Borg** | Container orchestration | - Cluster management<br>- Resource efficiency<br>- Basis for Kubernetes |
| **Cloud Functions** | Serverless | - Event-driven<br>- Auto-scaling<br>- Pay per execution |

### Networking & Communication

| Technology | Use Case | Key Features |
|------------|----------|--------------|
| **Stubby/gRPC** | RPC framework | - Binary protocol<br>- Streaming support<br>- Multi-language |
| **Andromeda** | SDN | - Virtual networking<br>- Global load balancing<br>- DDoS protection |
| **Maglev** | Load balancing | - Consistent hashing<br>- Connection draining<br>- Health checking |

## 🎯 Interview Focus Areas by Role

```mermaid
graph LR
    subgraph "L3/L4 (Junior)"
        A[Basic Patterns]
        B[Simple Systems]
        C[Code Quality]
        A --> D[URL Shortener]
        B --> E[Chat App]
        C --> F[KV Store]
    end
    
    subgraph "L5 (Senior)"
        G[Complex Systems]
        H[Scale Challenges]
        I[Trade-offs]
        G --> J[YouTube]
        H --> K[Gmail]
        I --> L[Maps]
    end
    
    subgraph "L6+ (Staff+)"
        M[Platform Design]
        N[Cross-cutting]
        O[Innovation]
        M --> P[Infrastructure]
        N --> Q[ML Platform]
        O --> R[Next-gen]
    end
```

## 📈 Common Interview Topics

### Most Frequently Asked Systems

<div class="pattern-grid">

<div class="pattern-card">
<div class="pattern-icon">📹</div>
<h4>Video Streaming (YouTube)</h4>
<p>CDN, adaptive bitrate, recommendation engine</p>
</div>

<div class="pattern-card">
<div class="pattern-icon">🗺️</div>
<h4>Maps & Navigation</h4>
<p>Geospatial indexing, route calculation, real-time traffic</p>
</div>

<div class="pattern-card">
<div class="pattern-icon">📧</div>
<h4>Email Service (Gmail)</h4>
<p>Spam detection, search, massive storage</p>
</div>

<div class="pattern-card">
<div class="pattern-icon">🔍</div>
<h4>Search Engine</h4>
<p>Web crawling, indexing, ranking, instant results</p>
</div>

<div class="pattern-card">
<div class="pattern-icon">📝</div>
<h4>Collaborative Docs</h4>
<p>Real-time sync, conflict resolution, offline support</p>
</div>

<div class="pattern-card">
<div class="pattern-icon">💬</div>
<h4>Chat/Messaging</h4>
<p>Real-time delivery, end-to-end encryption, presence</p>
</div>

<div class="pattern-card">
<div class="pattern-icon">☁️</div>
<h4>Cloud Storage (Drive)</h4>
<p>File sync, sharing, versioning, deduplication</p>
</div>

<div class="pattern-card">
<div class="pattern-icon">📱</div>
<h4>App Store (Play Store)</h4>
<p>App distribution, updates, ratings, recommendations</p>
</div>

</div>

### Key Design Patterns to Master

1. **Sharding & Partitioning**
   - Consistent hashing
   - Range-based sharding
   - Geographic partitioning

2. **Caching Strategies**
   - Multi-level caching
   - Cache warming
   - Cache invalidation

3. **Data Consistency**
   - Eventual consistency
   - Strong consistency
   - Tunable consistency

4. **Load Balancing**
   - Round robin
   - Least connections
   - Geographic routing

5. **Service Mesh**
   - Service discovery
   - Circuit breaking
   - Request routing

## 📊 Detailed Scoring Rubric

<div class="scoring-matrix">
<table>
<thead>
<tr>
<th>Dimension</th>
<th>1 - Strong No Hire</th>
<th>2 - No Hire</th>
<th>3 - Hire</th>
<th>4 - Strong Hire</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Problem Analysis</strong></td>
<td>• Misunderstands problem<br/>• No clarifying questions<br/>• Wrong assumptions</td>
<td>• Basic understanding<br/>• Few questions<br/>• Some assumptions stated</td>
<td>• Good understanding<br/>• Good questions<br/>• Clear assumptions</td>
<td>• Deep insight<br/>• Excellent questions<br/>• Challenges assumptions</td>
</tr>
<tr>
<td><strong>System Design</strong></td>
<td>• No coherent design<br/>• Major components missing<br/>• Doesn't work</td>
<td>• Basic design<br/>• Some gaps<br/>• Would work poorly</td>
<td>• Solid design<br/>• All components present<br/>• Would work well</td>
<td>• Elegant design<br/>• Optimal choices<br/>• Production-ready</td>
</tr>
<tr>
<td><strong>Scale Thinking</strong></td>
<td>• Ignores scale<br/>• No calculations<br/>• Single-server mindset</td>
<td>• Mentions scale<br/>• Basic calculations<br/>• Some distribution</td>
<td>• Plans for scale<br/>• Good calculations<br/>• Proper sharding</td>
<td>• Masters scale<br/>• Precise calculations<br/>• Optimal partitioning</td>
</tr>
<tr>
<td><strong>Trade-offs</strong></td>
<td>• No trade-offs discussed<br/>• One-size-fits-all<br/>• Inflexible</td>
<td>• Few trade-offs<br/>• Basic analysis<br/>• Some flexibility</td>
<td>• Good trade-offs<br/>• Clear reasoning<br/>• Adaptable design</td>
<td>• Excellent analysis<br/>• Multiple options<br/>• Future-proof</td>
</tr>
<tr>
<td><strong>Communication</strong></td>
<td>• Unclear explanation<br/>• No diagrams<br/>• Hard to follow</td>
<td>• Basic clarity<br/>• Simple diagrams<br/>• Some confusion</td>
<td>• Clear communication<br/>• Good diagrams<br/>• Easy to follow</td>
<td>• Crystal clear<br/>• Professional diagrams<br/>• Teaches interviewer</td>
</tr>
</tbody>
</table>
</div>

## 🎯 Evaluation Criteria

### What Google Interviewers Look For

<div class="truth-box">
<h3>Core Evaluation Dimensions</h3>
<table>
<tr>
<th>Dimension</th>
<th>What They Assess</th>
<th>How to Excel</th>
</tr>
<tr>
<td><strong>Problem Solving</strong></td>
<td>- Requirement gathering<br>- Trade-off analysis<br>- Iterative refinement</td>
<td>- Ask clarifying questions<br>- State assumptions clearly<br>- Consider multiple approaches</td>
</tr>
<tr>
<td><strong>Technical Depth</strong></td>
<td>- System components<br>- Data flow<br>- Technology choices</td>
<td>- Know common patterns<br>- Understand Google tech<br>- Justify decisions</td>
</tr>
<tr>
<td><strong>Scale Awareness</strong></td>
<td>- Capacity planning<br>- Performance optimization<br>- Cost considerations</td>
<td>- Do back-of-envelope math<br>- Identify bottlenecks<br>- Propose optimizations</td>
</tr>
<tr>
<td><strong>Communication</strong></td>
<td>- Clarity of explanation<br>- Diagram quality<br>- Thought process</td>
<td>- Think out loud<br>- Draw clear diagrams<br>- Summarize decisions</td>
</tr>
</table>
</div>

### Scoring Rubric (1-4 Scale)

- **4 - Strong Hire**: Exceptional design, deep understanding, clear communication
- **3 - Hire**: Solid design, good trade-offs, adequate communication
- **2 - No Hire**: Major gaps, poor trade-offs, unclear communication
- **1 - Strong No Hire**: Fundamental misunderstanding, no viable solution

## 📚 Must-Read Google Papers

<div class="law-box">
<h3>📖 Essential Reading List</h3>
<ol>
<li><strong>MapReduce (2004)</strong> - Simplified data processing on large clusters</li>
<li><strong>Bigtable (2006)</strong> - Distributed storage system for structured data</li>
<li><strong>Spanner (2012)</strong> - Globally distributed database with external consistency</li>
<li><strong>Dapper (2010)</strong> - Large-scale distributed systems tracing</li>
<li><strong>Borg (2015)</strong> - Large-scale cluster management (Kubernetes predecessor)</li>
</ol>
</div>

## 🗺️ Interview Process & Timeline

### Typical Interview Structure

```mermaid
graph LR
    A[Phone Screen<br/>45 min] --> B[Technical Phone<br/>45 min]
    B --> C[Onsite Loop<br/>5 x 45 min]
    C --> D[Hiring Committee<br/>1-2 weeks]
    D --> E[Offer/Decision]
```

### System Design Round Format (45 minutes)

| Time | Phase | Focus |
|------|-------|-------|
| 0-5 min | **Requirements** | Clarify functional & non-functional requirements |
| 5-10 min | **Estimation** | Back-of-envelope calculations for scale |
| 10-25 min | **High-Level Design** | Draw architecture, explain components |
| 25-35 min | **Deep Dive** | Detail 1-2 components, handle edge cases |
| 35-40 min | **Scale & Optimize** | Discuss bottlenecks, propose improvements |
| 40-45 min | **Wrap Up** | Summarize, answer questions |

## 🛠️ Interactive Design Checklist

<div class="checklist-container">
<h3>Pre-Interview Checklist</h3>
<div class="checklist-section">
<h4>Technical Preparation</h4>
<label><input type="checkbox"> Reviewed 7 Laws and 5 Pillars</label>
<label><input type="checkbox"> Read 5+ Google papers</label>
<label><input type="checkbox"> Practiced 10+ system designs</label>
<label><input type="checkbox"> Memorized latency numbers</label>
<label><input type="checkbox"> Understood CAP theorem deeply</label>
</div>
<div class="checklist-section">
<h4>Practice & Skills</h4>
<label><input type="checkbox"> Can draw clear architecture diagrams</label>
<label><input type="checkbox"> Comfortable with back-of-envelope math</label>
<label><input type="checkbox"> Practiced time management (45 min)</label>
<label><input type="checkbox"> Done 5+ mock interviews</label>
<label><input type="checkbox"> Received and incorporated feedback</label>
</div>
<div class="checklist-section">
<h4>Interview Day</h4>
<label><input type="checkbox"> Good night's sleep</label>
<label><input type="checkbox"> Quiet environment setup</label>
<label><input type="checkbox"> Drawing tools ready</label>
<label><input type="checkbox"> Water bottle nearby</label>
<label><input type="checkbox"> Positive mindset</label>
</div>
</div>

## 🔄 Design Process Flowchart

```mermaid
flowchart TD
    Start([Interview Starts]) --> Clarify[Clarify Requirements]
    Clarify --> FR[Functional Requirements]
    Clarify --> NFR[Non-Functional Requirements]
    
    FR --> API[Design API]
    NFR --> Scale[Estimate Scale]
    
    API --> HLD[High-Level Design]
    Scale --> HLD
    
    HLD --> Components[Identify Components]
    Components --> Draw[Draw Architecture]
    
    Draw --> DeepDive{Deep Dive Area?}
    DeepDive -->|Data| DataModel[Data Model & Storage]
    DeepDive -->|Scale| Scaling[Scaling Strategy]
    DeepDive -->|Performance| Perf[Performance Optimization]
    
    DataModel --> Optimize[Optimizations]
    Scaling --> Optimize
    Perf --> Optimize
    
    Optimize --> EdgeCases[Handle Edge Cases]
    EdgeCases --> Monitor[Monitoring & Alerts]
    Monitor --> Summary[Summarize Design]
    Summary --> QA[Q&A]
    QA --> End([Interview Ends])
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style DeepDive fill:#87CEEB
```

## 💡 Pro Tips

<div class="decision-box">
<h3>✅ Do's</h3>
<ul>
<li>Start with a simple, working design</li>
<li>Use Google technologies when appropriate</li>
<li>Draw clear, labeled diagrams</li>
<li>Justify every design decision</li>
<li>Consider cost implications</li>
<li>Think about monitoring & debugging</li>
</ul>
</div>

<div class="failure-vignette">
<h3>❌ Don'ts</h3>
<ul>
<li>Don't over-engineer from the start</li>
<li>Don't ignore latency requirements</li>
<li>Don't forget about failure modes</li>
<li>Don't skip capacity planning</li>
<li>Don't use technologies you can't explain</li>
<li>Don't forget about data consistency</li>
</ul>
</div>

## 📚 Complete Interview Resources

### 🎓 Preparation Materials
<div class="pattern-grid">

<a href="preparation-guide.md" class="pattern-card">
<div class="pattern-icon">📖</div>
<h4>8-Week Study Guide</h4>
<p>Structured preparation plan with daily tasks</p>
</a>

<a href="common-mistakes.md" class="pattern-card">
<div class="pattern-icon">❌</div>
<h4>Common Mistakes</h4>
<p>Learn what to avoid in interviews</p>
</a>

<a href="interview-experiences.md" class="pattern-card">
<div class="pattern-icon">💬</div>
<h4>Interview Experiences & Tips</h4>
<p>Real scenarios, communication strategies, and proven techniques</p>
</a>

<a href="mock-questions.md" class="pattern-card">
<div class="pattern-icon">💯</div>
<h4>Mock Questions</h4>
<p>20+ Google-specific practice problems</p>
</a>

<a href="evaluation-rubric.md" class="pattern-card">
<div class="pattern-icon">📊</div>
<h4>Evaluation Rubric</h4>
<p>Comprehensive scoring guide and self-assessment</p>
</a>

</div>

### 🚶 Example Walkthroughs
<div class="pattern-grid">

<a href="youtube-walkthrough.md" class="pattern-card">
<div class="pattern-icon">🎥</div>
<h4>Design YouTube</h4>
<p>Complete 45-minute interview walkthrough</p>
</a>

<a href="maps-walkthrough.md" class="pattern-card">
<div class="pattern-icon">🗺️</div>
<h4>Design Google Maps</h4>
<p>Geographic systems at planetary scale</p>
</a>

<a href="gmail-walkthrough.md" class="pattern-card">
<div class="pattern-icon">📧</div>
<h4>Design Gmail</h4>
<p>Email system for billions of users</p>
</a>

</div>

### ⚡ Quick References
<div class="pattern-grid">

<a href="scale-cheatsheet.md" class="pattern-card">
<div class="pattern-icon">📊</div>
<h4>Scale Cheat Sheet</h4>
<p>Google scale numbers & calculations</p>
</a>

<a href="tech-mapping.md" class="pattern-card">
<div class="pattern-icon">🔧</div>
<h4>Technology Mapping</h4>
<p>When to use what technology</p>
</a>

<a href="time-management.md" class="pattern-card">
<div class="pattern-icon">⏰</div>
<h4>Time Management</h4>
<p>Optimize your 45 minutes</p>
</a>

</div>

### 🔗 Related Resources
<div class="pattern-grid">

<a href="../patterns/index.md" class="pattern-card">
<div class="pattern-icon">🏗️</div>
<h4>Pattern Library</h4>
<p>Master essential design patterns</p>
</a>

<a href="../case-studies/index.md" class="pattern-card">
<div class="pattern-icon">📚</div>
<h4>Case Studies</h4>
<p>Learn from real system designs</p>
</a>

<a href="../quantitative/index.md" class="pattern-card">
<div class="pattern-icon">🧮</div>
<h4>Quantitative Tools</h4>
<p>Master capacity planning math</p>
</a>

</div>

## 📌 Quick Reference Card

<div class="truth-box">
<h3>Interview Day Checklist</h3>
<ul>
<li>☐ Clarify requirements (functional & non-functional)</li>
<li>☐ Define success metrics (QPS, latency, availability)</li>
<li>☐ Estimate scale (users, data, requests)</li>
<li>☐ Draw high-level architecture</li>
<li>☐ Design data model & API</li>
<li>☐ Address scalability concerns</li>
<li>☐ Discuss failure scenarios</li>
<li>☐ Consider monitoring & alerting</li>
<li>☐ Optimize for performance & cost</li>
<li>☐ Summarize trade-offs made</li>
</ul>
</div>

---

## 📈 Performance Tracking Tool

<div class="performance-tracker">
<h3>Track Your Interview Performance</h3>
<table>
<thead>
<tr>
<th>Date</th>
<th>System</th>
<th>Time Taken</th>
<th>Self Score (1-4)</th>
<th>Areas to Improve</th>
</tr>
</thead>
<tbody>
<tr>
<td><input type="date"></td>
<td><input type="text" placeholder="e.g., YouTube"></td>
<td><input type="text" placeholder="e.g., 45 min"></td>
<td><select><option>1</option><option>2</option><option>3</option><option>4</option></select></td>
<td><input type="text" placeholder="e.g., Scale calculations"></td>
</tr>
<tr>
<td><input type="date"></td>
<td><input type="text"></td>
<td><input type="text"></td>
<td><select><option>1</option><option>2</option><option>3</option><option>4</option></select></td>
<td><input type="text"></td>
</tr>
<tr>
<td><input type="date"></td>
<td><input type="text"></td>
<td><input type="text"></td>
<td><select><option>1</option><option>2</option><option>3</option><option>4</option></select></td>
<td><input type="text"></td>
</tr>
</tbody>
</table>
<button onclick="analyzeProgress()">Analyze Progress</button>
<div id="progress-analysis"></div>
</div>

<div class="navigation-grid">
<a href="../index.md" class="nav-card">
<div class="nav-icon">🏠</div>
<h4>Home</h4>
<p>Back to main page</p>
</a>

<a href="preparation-guide.md" class="nav-card">
<div class="nav-icon">📖</div>
<h4>Start Preparing</h4>
<p>Structured study guide</p>
</a>
</div>

<script>
function calculatePlan() {
    const level = document.getElementById('level').value;
    const hours = parseInt(document.getElementById('hours').value);
    const targetDate = new Date(document.getElementById('target-date').value);
    const today = new Date();
    const weeks = Math.floor((targetDate - today) / (7 * 24 * 60 * 60 * 1000));
    
    let plan = '<h4>Your Personalized Study Plan</h4>';
    
    if (weeks < 4) {
        plan += '<p class="warning">⚠️ Limited time! Focus on essentials only.</p>';
    }
    
    const totalHours = weeks * hours;
    const distribution = {
        fundamentals: level === 'junior' ? 0.4 : 0.2,
        patterns: 0.3,
        practice: level === 'senior' ? 0.4 : 0.3,
        mocks: 0.1
    };
    
    plan += '<ul>';
    plan += `<li>Fundamentals: ${Math.round(totalHours * distribution.fundamentals)} hours</li>`;
    plan += `<li>Design Patterns: ${Math.round(totalHours * distribution.patterns)} hours</li>`;
    plan += `<li>Practice Problems: ${Math.round(totalHours * distribution.practice)} hours</li>`;
    plan += `<li>Mock Interviews: ${Math.round(totalHours * distribution.mocks)} hours</li>`;
    plan += '</ul>';
    
    document.getElementById('plan-results').innerHTML = plan;
}

function analyzeProgress() {
    // Simple progress analysis
    const analysis = document.getElementById('progress-analysis');
    analysis.innerHTML = '<h4>Progress Analysis</h4><p>Track at least 5 designs to see trends!</p>';
}
</script>
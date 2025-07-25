# Visual Cheat Sheets for System Design Interviews

## 🎯 The Ultimate System Design Canvas

```mermaid
graph TB
    subgraph "1. Requirements [5 min]"
        R1[Functional Requirements]
        R2[Non-Functional Requirements]
        R3[Scale Estimates]
        R1 --> API[API Design]
        R2 --> Constraints[Constraints]
        R3 --> Numbers[Back-of-envelope]
    end
    
    subgraph "2. High Level [15 min]"
        Client[Clients]
        LB[Load Balancer]
        API_GW[API Gateway]
        Services[Microservices]
        Cache[Cache Layer]
        DB[Database]
        Queue[Message Queue]
        
        Client --> LB
        LB --> API_GW
        API_GW --> Services
        Services --> Cache
        Services --> DB
        Services --> Queue
    end
    
    subgraph "3. Deep Dive [15 min]"
        Data[Data Model]
        Algo[Key Algorithms]
        Bottle[Bottlenecks]
        Data --> Schema[Schema Design]
        Algo --> Logic[Core Logic]
        Bottle --> Solution[Solutions]
    end
    
    subgraph "4. Scale & Optimize [10 min]"
        Scale[Scaling Strategy]
        Monitor[Monitoring]
        Cost[Cost Analysis]
        Scale --> Horizontal[Horizontal Scale]
        Monitor --> Metrics[Key Metrics]
        Cost --> Optimize[Optimizations]
    end
```

## 📊 Quick Reference: Scale Numbers

<div class="scale-reference">
<table>
<thead>
<tr>
<th>Metric</th>
<th>Small</th>
<th>Medium</th>
<th>Large</th>
<th>Google Scale</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Users</strong></td>
<td>10K</td>
<td>1M</td>
<td>100M</td>
<td>1B+</td>
</tr>
<tr>
<td><strong>Requests/sec</strong></td>
<td>100</td>
<td>10K</td>
<td>100K</td>
<td>1M+</td>
</tr>
<tr>
<td><strong>Data Size</strong></td>
<td>GB</td>
<td>TB</td>
<td>PB</td>
<td>EB</td>
</tr>
<tr>
<td><strong>Servers Needed</strong></td>
<td>1-10</td>
<td>100s</td>
<td>1000s</td>
<td>100K+</td>
</tr>
<tr>
<td><strong>Cache Size</strong></td>
<td>MB</td>
<td>GB</td>
<td>TB</td>
<td>PB</td>
</tr>
<tr>
<td><strong>Bandwidth</strong></td>
<td>Mbps</td>
<td>Gbps</td>
<td>10 Gbps</td>
<td>Tbps</td>
</tr>
</tbody>
</table>
</div>

## 🚀 Latency Numbers Every Engineer Should Know

```mermaid
gantt
    title Latency Comparison (log scale)
    dateFormat X
    axisFormat %s
    
    section Cache
    L1 Cache Reference    :0, 1
    L2 Cache Reference    :0, 10
    
    section Memory
    Main Memory Reference :0, 100
    
    section Storage
    SSD Random Read       :0, 16000
    HDD Seek              :0, 10000000
    
    section Network
    Same DC Round Trip    :0, 500000
    Cross-Coast RT        :0, 150000000
```

### Quick Latency Reference
- **L1 Cache**: 0.5 ns
- **L2 Cache**: 7 ns
- **RAM**: 100 ns
- **SSD Read**: 16 μs
- **Network Same DC**: 0.5 ms
- **Network Cross-Coast**: 150 ms
- **HDD Seek**: 10 ms

## 🏗️ Common Architecture Patterns

<div class="pattern-grid">
<div class="pattern-visual">
<h3>1. Basic Web App</h3>
<pre>
┌─────────┐     ┌──────────┐     ┌────────┐
│ Browser ├────►│ Web Server├────►│   DB   │
└─────────┘     └──────────┘     └────────┘
</pre>
</div>

<div class="pattern-visual">
<h3>2. With Load Balancer</h3>
<pre>
┌─────────┐     ┌────┐     ┌──────────┐
│ Browser ├────►│ LB ├────►│ Server 1 │
└─────────┘     └─┬──┘     └──────────┘
                  │        ┌──────────┐
                  └───────►│ Server 2 │
                           └──────────┘
</pre>
</div>

<div class="pattern-visual">
<h3>3. With Cache</h3>
<pre>
┌─────────┐     ┌──────────┐     ┌───────┐
│ Browser ├────►│   Server  ├────►│ Cache │
└─────────┘     └──────────┘     └───┬───┘
                                      │
                                  ┌───▼───┐
                                  │   DB  │
                                  └───────┘
</pre>
</div>

<div class="pattern-visual">
<h3>4. Microservices</h3>
<pre>
┌─────────┐     ┌──────────┐     ┌─────────┐
│   API   ├────►│ Service A├────►│  DB A   │
│ Gateway │     └──────────┘     └─────────┘
└────┬────┘     ┌──────────┐     ┌─────────┐
     └─────────►│ Service B├────►│  DB B   │
                └──────────┘     └─────────┘
</pre>
</div>
</div>

## 📐 Capacity Planning Formulas

<div class="formula-cards">
<div class="formula-card">
<h4>🔢 QPS Calculation</h4>
<pre>
Daily Active Users = 100M
Avg requests/user/day = 20
Total daily requests = 2B

QPS = 2B / 86400 = ~23K QPS
Peak QPS = 23K × 3 = ~70K QPS
</pre>
</div>

<div class="formula-card">
<h4>💾 Storage Calculation</h4>
<pre>
Users = 100M
Data per user = 10 MB
Total = 100M × 10 MB = 1 PB

With replication (3x) = 3 PB
With backups (+50%) = 4.5 PB
</pre>
</div>

<div class="formula-card">
<h4>🖥️ Server Calculation</h4>
<pre>
Peak QPS = 70K
QPS per server = 1000
Servers needed = 70

With redundancy (2x) = 140
Round up = 150 servers
</pre>
</div>

<div class="formula-card">
<h4>💰 Bandwidth Calculation</h4>
<pre>
QPS = 70K
Request size = 1 KB
Response size = 10 KB

Bandwidth = 70K × 11 KB
= 770 MB/s = 6.2 Gbps
</pre>
</div>
</div>

## 🎨 Database Decision Tree

```mermaid
flowchart TD
    Start[Choose Database] --> Structure{Structured Data?}
    
    Structure -->|Yes| ACID{Need ACID?}
    Structure -->|No| NoSQL[NoSQL Options]
    
    ACID -->|Yes| Scale{Scale Requirements?}
    ACID -->|No| Eventually[Eventually Consistent OK]
    
    Scale -->|Single Region| Traditional[PostgreSQL/MySQL]
    Scale -->|Global| NewSQL[Spanner/CockroachDB]
    
    NoSQL --> Type{Data Type?}
    Type -->|Key-Value| KV[Redis/DynamoDB]
    Type -->|Document| Doc[MongoDB/Firestore]
    Type -->|Wide Column| Wide[Cassandra/Bigtable]
    Type -->|Graph| Graph[Neo4j/Neptune]
    
    Eventually --> Dynamo[DynamoDB/Cassandra]
```

## 🔄 Caching Strategy Selector

<div class="caching-strategies">
<table>
<thead>
<tr>
<th>Pattern</th>
<th>When to Use</th>
<th>Pros</th>
<th>Cons</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Cache Aside</strong></td>
<td>• Read heavy<br/>• Cache misses OK</td>
<td>• Simple<br/>• Flexible</td>
<td>• Cache misses<br/>• Inconsistency risk</td>
</tr>
<tr>
<td><strong>Write Through</strong></td>
<td>• Write heavy<br/>• Need consistency</td>
<td>• No stale data<br/>• Simpler logic</td>
<td>• Write latency<br/>• Cache churn</td>
</tr>
<tr>
<td><strong>Write Behind</strong></td>
<td>• Write heavy<br/>• Latency sensitive</td>
<td>• Fast writes<br/>• Batch updates</td>
<td>• Data loss risk<br/>• Complex</td>
</tr>
<tr>
<td><strong>Refresh Ahead</strong></td>
<td>• Predictable access<br/>• Low latency critical</td>
<td>• No cache misses<br/>• Great performance</td>
<td>• Prediction needed<br/>• Resource intensive</td>
</tr>
</tbody>
</table>
</div>

## 🌐 API Design Patterns

<div class="api-patterns">
<div class="api-card">
<h4>RESTful API</h4>
<pre>
GET    /users/{id}
POST   /users
PUT    /users/{id}
DELETE /users/{id}

GET    /users/{id}/posts
POST   /users/{id}/posts
</pre>
</div>

<div class="api-card">
<h4>GraphQL</h4>
<pre>
query {
  user(id: "123") {
    name
    email
    posts {
      title
      content
    }
  }
}
</pre>
</div>

<div class="api-card">
<h4>gRPC</h4>
<pre>
service UserService {
  rpc GetUser(GetUserRequest) 
      returns (User);
  rpc ListUsers(ListUsersRequest) 
      returns (stream User);
}
</pre>
</div>
</div>

## 🚦 Load Balancing Algorithms

```mermaid
graph LR
    subgraph "Round Robin"
        LB1[Load Balancer] --> S1[Server 1]
        LB1 --> S2[Server 2]
        LB1 --> S3[Server 3]
    end
    
    subgraph "Least Connections"
        LB2[Load Balancer] --> S4[Server: 10 conn]
        LB2 --> S5[Server: 5 conn ✓]
        LB2 --> S6[Server: 15 conn]
    end
    
    subgraph "Consistent Hashing"
        LB3[Load Balancer] --> Ring[Hash Ring]
        Ring --> S7[Server A: 0-120°]
        Ring --> S8[Server B: 120-240°]
        Ring --> S9[Server C: 240-360°]
    end
```

## 📱 Mobile App Architecture

<div class="mobile-arch">
<h3>Offline-First Architecture</h3>
<pre>
┌─────────────────────────────────────┐
│          Mobile App                 │
├─────────────────────────────────────┤
│  ┌─────────┐      ┌──────────────┐ │
│  │   UI    │◄────►│ Local SQLite │ │
│  └─────────┘      └──────────────┘ │
│       ▲                    ▲        │
│       │                    │        │
│  ┌────▼──────┐      ┌─────▼──────┐ │
│  │ View Model│      │ Sync Engine │ │
│  └───────────┘      └─────────────┘ │
└───────────────────────────┬─────────┘
                            │
                     ┌──────▼──────┐
                     │   Backend   │
                     │     API     │
                     └─────────────┘
</pre>
</div>

## 🎯 Interview Time Management

<div class="time-management">
<svg viewBox="0 0 400 400" style="max-width: 400px;">
  <!-- Clock face -->
  <circle cx="200" cy="200" r="180" fill="#f0f0f0" stroke="#333" stroke-width="4"/>
  
  <!-- Time segments -->
  <path d="M 200,200 L 200,20 A 180,180 0 0,1 290,60 z" fill="#FF6B6B" opacity="0.7"/>
  <path d="M 200,200 L 290,60 A 180,180 0 0,1 350,200 z" fill="#4ECDC4" opacity="0.7"/>
  <path d="M 200,200 L 350,200 A 180,180 0 0,1 290,340 z" fill="#FFE66D" opacity="0.7"/>
  <path d="M 200,200 L 290,340 A 180,180 0 0,1 200,380 z" fill="#95E1D3" opacity="0.7"/>
  <path d="M 200,200 L 200,380 A 180,180 0 0,1 110,340 z" fill="#A8E6CF" opacity="0.7"/>
  <path d="M 200,200 L 110,340 A 180,180 0 0,1 200,20 z" fill="#C7CEEA" opacity="0.7"/>
  
  <!-- Labels -->
  <text x="200" y="100" text-anchor="middle" font-size="14" font-weight="bold">Requirements</text>
  <text x="200" y="115" text-anchor="middle" font-size="12">5 min</text>
  
  <text x="320" y="130" text-anchor="middle" font-size="14" font-weight="bold">Estimation</text>
  <text x="320" y="145" text-anchor="middle" font-size="12">5 min</text>
  
  <text x="320" y="270" text-anchor="middle" font-size="14" font-weight="bold">High Level</text>
  <text x="320" y="285" text-anchor="middle" font-size="12">15 min</text>
  
  <text x="200" y="320" text-anchor="middle" font-size="14" font-weight="bold">Deep Dive</text>
  <text x="200" y="335" text-anchor="middle" font-size="12">10 min</text>
  
  <text x="80" y="270" text-anchor="middle" font-size="14" font-weight="bold">Scale</text>
  <text x="80" y="285" text-anchor="middle" font-size="12">5 min</text>
  
  <text x="80" y="130" text-anchor="middle" font-size="14" font-weight="bold">Wrap Up</text>
  <text x="80" y="145" text-anchor="middle" font-size="12">5 min</text>
  
  <!-- Center -->
  <circle cx="200" cy="200" r="10" fill="#333"/>
</svg>
</div>

## 🔍 Common Bottlenecks & Solutions

<div class="bottleneck-solutions">
<table>
<thead>
<tr>
<th>Bottleneck</th>
<th>Symptoms</th>
<th>Solutions</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Database</strong></td>
<td>• Slow queries<br/>• Connection limits<br/>• Lock contention</td>
<td>• Add read replicas<br/>• Implement caching<br/>• Shard data<br/>• Optimize queries</td>
</tr>
<tr>
<td><strong>Network</strong></td>
<td>• High latency<br/>• Packet loss<br/>• Bandwidth limits</td>
<td>• Use CDN<br/>• Compress data<br/>• Regional deployment<br/>• Connection pooling</td>
</tr>
<tr>
<td><strong>CPU</strong></td>
<td>• High CPU usage<br/>• Slow processing<br/>• Request timeouts</td>
<td>• Horizontal scaling<br/>• Optimize algorithms<br/>• Async processing<br/>• Load balancing</td>
</tr>
<tr>
<td><strong>Memory</strong></td>
<td>• OOM errors<br/>• Garbage collection<br/>• Cache misses</td>
<td>• Increase memory<br/>• Optimize data structures<br/>• Implement paging<br/>• Memory-mapped files</td>
</tr>
<tr>
<td><strong>Storage</strong></td>
<td>• Slow I/O<br/>• Full disks<br/>• Hot partitions</td>
<td>• Use SSD<br/>• Implement archiving<br/>• Partition data<br/>• Compress files</td>
</tr>
</tbody>
</table>
</div>

## 📊 Monitoring & Metrics Cheat Sheet

<div class="metrics-grid">
<div class="metric-category">
<h4>🟢 Golden Signals</h4>
<ul>
<li><strong>Latency</strong>: Response time</li>
<li><strong>Traffic</strong>: Requests/sec</li>
<li><strong>Errors</strong>: Error rate %</li>
<li><strong>Saturation</strong>: Resource usage</li>
</ul>
</div>

<div class="metric-category">
<h4>🔵 SLI Examples</h4>
<ul>
<li>P99 latency < 100ms</li>
<li>Availability > 99.9%</li>
<li>Error rate < 0.1%</li>
<li>Throughput > 10K QPS</li>
</ul>
</div>

<div class="metric-category">
<h4>🟡 Key Metrics</h4>
<ul>
<li>CPU utilization</li>
<li>Memory usage</li>
<li>Disk I/O</li>
<li>Network bandwidth</li>
<li>Queue depth</li>
<li>Cache hit rate</li>
</ul>
</div>

<div class="metric-category">
<h4>🔴 Alert Thresholds</h4>
<ul>
<li>CPU > 80% for 5 min</li>
<li>Memory > 90%</li>
<li>Error rate > 1%</li>
<li>Queue depth > 1000</li>
<li>P99 latency > 1s</li>
</ul>
</div>
</div>

<style>
.scale-reference table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}

.scale-reference th {
    background-color: #4285F4;
    color: white;
    padding: 10px;
}

.scale-reference td {
    padding: 10px;
    border: 1px solid #ddd;
    text-align: center;
}

.pattern-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.pattern-visual {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    font-family: monospace;
}

.pattern-visual pre {
    margin: 0;
    font-size: 12px;
    line-height: 1.4;
}

.formula-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.formula-card {
    background: #e8f4f8;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #b8dae8;
}

.formula-card pre {
    margin: 10px 0 0 0;
    font-size: 13px;
    background: white;
    padding: 10px;
    border-radius: 4px;
}

.caching-strategies table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}

.caching-strategies th {
    background-color: #34A853;
    color: white;
    padding: 10px;
}

.caching-strategies td {
    padding: 10px;
    border: 1px solid #ddd;
    vertical-align: top;
}

.api-patterns {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.api-card {
    background: #f0f4f8;
    padding: 15px;
    border-radius: 8px;
}

.api-card pre {
    margin: 10px 0 0 0;
    font-size: 12px;
    background: white;
    padding: 10px;
    border-radius: 4px;
}

.mobile-arch pre {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    font-size: 12px;
    overflow-x: auto;
}

.time-management {
    text-align: center;
    margin: 20px 0;
}

.bottleneck-solutions table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}

.bottleneck-solutions th {
    background-color: #EA4335;
    color: white;
    padding: 10px;
}

.bottleneck-solutions td {
    padding: 10px;
    border: 1px solid #ddd;
    vertical-align: top;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.metric-category {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #4285F4;
}

.metric-category h4 {
    margin-top: 0;
}

.metric-category ul {
    margin: 0;
    padding-left: 20px;
}
</style>
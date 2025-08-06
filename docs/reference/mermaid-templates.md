# Mermaid Diagram Templates Library

This document provides comprehensive, reusable Mermaid templates for all distributed systems patterns in the DStudio documentation.

## Template Usage

Each template includes:
- **Base Template**: Copy-paste ready Mermaid code
- **Customization Guide**: How to adapt for specific patterns
- **Style Classes**: Pre-configured color schemes
- **Example Usage**: Real-world implementation examples

---

## 1. State Machine Templates

### Circuit Breaker State Machine

```mermaid
stateDiagram-v2
    [*] --> CLOSED: Initialize
    
    CLOSED --> OPEN: Failures exceed threshold<br/>(>50% error rate or<br/>5+ consecutive failures)
    OPEN --> HALF_OPEN: Recovery timeout<br/>(30-60 seconds)
    HALF_OPEN --> CLOSED: Success threshold met<br/>(3+ consecutive successes)  
    HALF_OPEN --> OPEN: Any failure occurs
    
    state CLOSED {
        [*] --> MonitoringTraffic: Normal operation
        MonitoringTraffic --> CountingFailures: Track requests
        CountingFailures --> EvaluatingThreshold: Check failure rate
        EvaluatingThreshold --> MonitoringTraffic: Below threshold
        EvaluatingThreshold --> TriggerOpen: Above threshold
    }
    
    state OPEN {
        [*] --> RejectingRequests: Fail fast mode
        RejectingRequests --> WaitingForTimeout: Start recovery timer
        WaitingForTimeout --> RejectingRequests: Timer active
        WaitingForTimeout --> AllowTesting: Timer expired
    }
    
    state HALF_OPEN {
        [*] --> TestingLimitedTraffic: Allow sample requests
        TestingLimitedTraffic --> CountingSuccesses: Track outcomes
        CountingSuccesses --> TestingLimitedTraffic: Continue testing
        CountingSuccesses --> DeclareHealthy: Success threshold
        CountingSuccesses --> DeclareUnhealthy: Any failure
    }
    
    classDef healthy fill:#4caf50,stroke:#2e7d32,color:#fff,stroke-width:2px
    classDef testing fill:#ff9800,stroke:#e65100,color:#fff,stroke-width:2px
    classDef failed fill:#f44336,stroke:#c62828,color:#fff,stroke-width:2px
    classDef transition fill:#2196f3,stroke:#1976d2,color:#fff,stroke-width:2px
    
    class CLOSED,MonitoringTraffic,CountingFailures,EvaluatingThreshold healthy
    class HALF_OPEN,TestingLimitedTraffic,CountingSuccesses,DeclareHealthy testing
    class OPEN,RejectingRequests,WaitingForTimeout,AllowTesting,DeclareUnhealthy failed
    class TriggerOpen transition
```

### Saga Transaction State Machine

```mermaid
stateDiagram-v2
    [*] --> SagaStarted: Begin transaction
    
    SagaStarted --> Step1Executing: Execute step 1
    Step1Executing --> Step1Completed: Success
    Step1Executing --> CompensatingStep1: Failure
    
    Step1Completed --> Step2Executing: Execute step 2
    Step2Executing --> Step2Completed: Success
    Step2Executing --> CompensatingStep2: Failure
    
    Step2Completed --> Step3Executing: Execute step 3
    Step3Executing --> SagaCompleted: Success
    Step3Executing --> CompensatingStep3: Failure
    
    CompensatingStep3 --> CompensatingStep2: Undo step 3
    CompensatingStep2 --> CompensatingStep1: Undo step 2
    CompensatingStep1 --> SagaFailed: Undo step 1
    
    state Step1Executing {
        [*] --> PreparingStep1
        PreparingStep1 --> ExecutingStep1
        ExecutingStep1 --> ValidatingStep1
        ValidatingStep1 --> [*]
    }
    
    classDef active fill:#2196f3,stroke:#1976d2,color:#fff,stroke-width:2px
    classDef success fill:#4caf50,stroke:#2e7d32,color:#fff,stroke-width:2px
    classDef compensating fill:#ff9800,stroke:#e65100,color:#fff,stroke-width:2px
    classDef failed fill:#f44336,stroke:#c62828,color:#fff,stroke-width:2px
    
    class SagaStarted,Step1Executing,Step2Executing,Step3Executing,PreparingStep1,ExecutingStep1,ValidatingStep1 active
    class Step1Completed,Step2Completed,SagaCompleted success
    class CompensatingStep1,CompensatingStep2,CompensatingStep3 compensating
    class SagaFailed failed
```

### Leader Election State Machine

```mermaid
stateDiagram-v2
    [*] --> Follower: Start as follower
    
    Follower --> Candidate: Election timeout<br/>or no heartbeat
    Candidate --> Leader: Receive majority votes<br/>(n/2 + 1 votes)
    Candidate --> Follower: Discover higher term<br/>or another leader
    Leader --> Follower: Discover higher term<br/>or network partition
    
    state Follower {
        [*] --> WaitingForHeartbeat: Listen for leader
        WaitingForHeartbeat --> ResetElectionTimer: Heartbeat received
        ResetElectionTimer --> WaitingForHeartbeat: Continue waiting
        WaitingForHeartbeat --> StartElection: Election timeout
    }
    
    state Candidate {
        [*] --> IncrementTerm: Increment term
        IncrementTerm --> VoteForSelf: Vote for self
        VoteForSelf --> RequestVotes: Send vote requests
        RequestVotes --> CountingVotes: Collect responses
        CountingVotes --> CheckMajority: Evaluate votes
        CheckMajority --> BecomeLeader: Majority achieved
        CheckMajority --> StartNewElection: Split vote
    }
    
    state Leader {
        [*] --> SendingHeartbeats: Maintain leadership
        SendingHeartbeats --> ProcessingClientRequests: Handle requests
        ProcessingClientRequests --> ReplicatingToFollowers: Replicate logs
        ReplicatingToFollowers --> SendingHeartbeats: Continue leadership
        SendingHeartbeats --> StepDown: Higher term discovered
    }
    
    classDef follower fill:#9e9e9e,stroke:#424242,color:#fff,stroke-width:2px
    classDef candidate fill:#ff9800,stroke:#e65100,color:#fff,stroke-width:2px
    classDef leader fill:#4caf50,stroke:#2e7d32,color:#fff,stroke-width:2px
    classDef transition fill:#2196f3,stroke:#1976d2,color:#fff,stroke-width:2px
    
    class Follower,WaitingForHeartbeat,ResetElectionTimer follower
    class Candidate,IncrementTerm,VoteForSelf,RequestVotes,CountingVotes,CheckMajority candidate
    class Leader,SendingHeartbeats,ProcessingClientRequests,ReplicatingToFollowers leader
    class StartElection,StartNewElection,BecomeLeader,StepDown transition
```

---

## 2. Architecture Diagram Templates

### Microservices Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        MobileApp[📱 Mobile App]
        WebApp[🌐 Web Application] 
        ThirdPartyAPI[🔌 Third-party Integration]
    end
    
    subgraph "Gateway Layer"
        APIGateway[🚪 API Gateway<br/>Rate Limiting, Auth, Routing]
        LoadBalancer[⚖️ Load Balancer<br/>Round Robin, Health Checks]
    end
    
    subgraph "Service Mesh"
        AuthService[🔐 Authentication Service<br/>JWT, OAuth, Sessions]
        UserService[👤 User Management Service<br/>Profile, Preferences] 
        OrderService[📦 Order Processing Service<br/>Inventory, Fulfillment]
        PaymentService[💳 Payment Service<br/>Transactions, Billing]
        NotificationService[📧 Notification Service<br/>Email, SMS, Push]
        AnalyticsService[📊 Analytics Service<br/>Metrics, Reporting]
    end
    
    subgraph "Data Layer"
        UserDB[(👤 User Database<br/>PostgreSQL)]
        OrderDB[(📦 Order Database<br/>MongoDB)]
        PaymentDB[(💳 Payment Database<br/>PostgreSQL)]
        AnalyticsDB[(📊 Analytics Database<br/>ClickHouse)]
        RedisCache{{🎯 Redis Cache<br/>Session, Config}}
        MessageQueue[📨 Message Queue<br/>Apache Kafka]
        ObjectStorage[🗄️ Object Storage<br/>AWS S3, Images]
    end
    
    %% Client connections
    MobileApp --> LoadBalancer
    WebApp --> LoadBalancer
    ThirdPartyAPI --> APIGateway
    LoadBalancer --> APIGateway
    
    %% Gateway to services
    APIGateway --> AuthService
    APIGateway --> UserService
    APIGateway --> OrderService
    APIGateway --> PaymentService
    
    %% Service interconnections
    UserService --> AuthService
    OrderService --> UserService
    OrderService --> PaymentService
    PaymentService --> NotificationService
    
    %% Service to data layer
    AuthService --> RedisCache
    UserService --> UserDB
    UserService --> RedisCache
    OrderService --> OrderDB
    OrderService --> MessageQueue
    PaymentService --> PaymentDB
    NotificationService --> MessageQueue
    AnalyticsService --> AnalyticsDB
    AnalyticsService --> MessageQueue
    
    %% External storage
    UserService --> ObjectStorage
    OrderService --> ObjectStorage
    
    classDef client fill:#e3f2fd,stroke:#1976d2,color:#000,stroke-width:2px
    classDef gateway fill:#fff3e0,stroke:#f57c00,color:#000,stroke-width:2px
    classDef service fill:#f3e5f5,stroke:#7b1fa2,color:#000,stroke-width:2px
    classDef database fill:#e8f5e8,stroke:#388e3c,color:#000,stroke-width:2px
    classDef infrastructure fill:#fce4ec,stroke:#c2185b,color:#000,stroke-width:2px
    
    class MobileApp,WebApp,ThirdPartyAPI client
    class APIGateway,LoadBalancer gateway
    class AuthService,UserService,OrderService,PaymentService,NotificationService,AnalyticsService service
    class UserDB,OrderDB,PaymentDB,AnalyticsDB database
    class RedisCache,MessageQueue,ObjectStorage infrastructure
```

### Event-Driven Architecture

```mermaid
graph TB
    subgraph "Event Producers"
        UserService[👤 User Service<br/>User lifecycle events]
        OrderService[📦 Order Service<br/>Order state changes]
        PaymentService[💳 Payment Service<br/>Payment events]
        InventoryService[📋 Inventory Service<br/>Stock level events]
    end
    
    subgraph "Event Infrastructure" 
        EventBus[🚌 Event Bus<br/>Apache Kafka<br/>Partitioned Topics]
        SchemaRegistry[📋 Schema Registry<br/>Confluent Schema Registry<br/>Event Evolution]
        EventStore[📚 Event Store<br/>Event History<br/>Event Sourcing]
    end
    
    subgraph "Event Processors"
        StreamProcessor[🌊 Stream Processor<br/>Kafka Streams<br/>Real-time Processing]
        EventAggregator[🔄 Event Aggregator<br/>Batch Processing<br/>Analytics Pipeline]
    end
    
    subgraph "Event Consumers"
        NotificationService[📧 Notification Service<br/>Email, SMS, Push]
        AnalyticsService[📊 Analytics Service<br/>Business Intelligence]
        AuditService[📝 Audit Service<br/>Compliance Logging]
        RecommendationService[🎯 Recommendation Engine<br/>ML Pipeline]
        SearchIndexer[🔍 Search Indexer<br/>Elasticsearch Sync]
        ReportingService[📈 Reporting Service<br/>Dashboard Updates]
    end
    
    subgraph "Dead Letter Processing"
        DLQ[💀 Dead Letter Queue<br/>Failed Events]
        RetryProcessor[🔁 Retry Processor<br/>Exponential Backoff]
        AlertManager[🚨 Alert Manager<br/>Failure Notifications]
    end
    
    %% Producer to infrastructure
    UserService -->|UserCreated<br/>UserUpdated<br/>UserDeleted| EventBus
    OrderService -->|OrderPlaced<br/>OrderCancelled<br/>OrderShipped| EventBus
    PaymentService -->|PaymentProcessed<br/>PaymentFailed<br/>RefundIssued| EventBus
    InventoryService -->|StockUpdated<br/>LowStockAlert<br/>RestockComplete| EventBus
    
    %% Infrastructure connections
    EventBus --> SchemaRegistry
    EventBus --> EventStore
    EventBus --> StreamProcessor
    EventBus --> EventAggregator
    
    %% Infrastructure to consumers
    StreamProcessor --> NotificationService
    StreamProcessor --> RecommendationService
    EventAggregator --> AnalyticsService
    EventAggregator --> ReportingService
    EventBus --> AuditService
    EventBus --> SearchIndexer
    
    %% Error handling
    NotificationService -.->|Failed Events| DLQ
    AnalyticsService -.->|Failed Events| DLQ
    RecommendationService -.->|Failed Events| DLQ
    DLQ --> RetryProcessor
    DLQ --> AlertManager
    RetryProcessor -.->|Retry| EventBus
    
    classDef producer fill:#e1f5fe,stroke:#0277bd,color:#000,stroke-width:2px
    classDef infrastructure fill:#fff8e1,stroke:#f57c00,color:#000,stroke-width:2px
    classDef processor fill:#f3e5f5,stroke:#7b1fa2,color:#000,stroke-width:2px
    classDef consumer fill:#e8f5e8,stroke:#388e3c,color:#000,stroke-width:2px
    classDef error fill:#ffebee,stroke:#d32f2f,color:#000,stroke-width:2px
    
    class UserService,OrderService,PaymentService,InventoryService producer
    class EventBus,SchemaRegistry,EventStore infrastructure
    class StreamProcessor,EventAggregator processor
    class NotificationService,AnalyticsService,AuditService,RecommendationService,SearchIndexer,ReportingService consumer
    class DLQ,RetryProcessor,AlertManager error
```

### Cell-Based Architecture

```mermaid
graph TB
    subgraph "Global Layer"
        GlobalLB[🌍 Global Load Balancer<br/>GeoDNS, Anycast]
        GlobalGateway[🚪 Global API Gateway<br/>Routing, Rate Limiting]
        GlobalAuth[🔐 Global Auth Service<br/>JWT Validation]
    end
    
    subgraph "Cell 1 - US East"
        subgraph "Cell 1 Gateway"
            Cell1LB[⚖️ Regional LB<br/>Health-based Routing]
            Cell1Gateway[🚪 Cell Gateway<br/>Local Rate Limiting]
        end
        
        subgraph "Cell 1 Services"
            Cell1User[👤 User Service]
            Cell1Order[📦 Order Service]
            Cell1Payment[💳 Payment Service]
            Cell1Inventory[📋 Inventory Service]
        end
        
        subgraph "Cell 1 Data"
            Cell1UserDB[(👤 User DB)]
            Cell1OrderDB[(📦 Order DB)]
            Cell1Cache{{🎯 Redis Cache}}
            Cell1Queue[📨 Local Queue]
        end
    end
    
    subgraph "Cell 2 - US West"
        subgraph "Cell 2 Gateway"
            Cell2LB[⚖️ Regional LB<br/>Health-based Routing]
            Cell2Gateway[🚪 Cell Gateway<br/>Local Rate Limiting]
        end
        
        subgraph "Cell 2 Services"
            Cell2User[👤 User Service]
            Cell2Order[📦 Order Service] 
            Cell2Payment[💳 Payment Service]
            Cell2Inventory[📋 Inventory Service]
        end
        
        subgraph "Cell 2 Data"
            Cell2UserDB[(👤 User DB)]
            Cell2OrderDB[(📦 Order DB)]
            Cell2Cache{{🎯 Redis Cache}}
            Cell2Queue[📨 Local Queue]
        end
    end
    
    subgraph "Cell 3 - Europe"
        subgraph "Cell 3 Gateway"
            Cell3LB[⚖️ Regional LB<br/>Health-based Routing]
            Cell3Gateway[🚪 Cell Gateway<br/>Local Rate Limiting]
        end
        
        subgraph "Cell 3 Services"
            Cell3User[👤 User Service]
            Cell3Order[📦 Order Service]
            Cell3Payment[💳 Payment Service]
            Cell3Inventory[📋 Inventory Service]
        end
        
        subgraph "Cell 3 Data"
            Cell3UserDB[(👤 User DB)]
            Cell3OrderDB[(📦 Order DB)]
            Cell3Cache{{🎯 Redis Cache}}
            Cell3Queue[📨 Local Queue]
        end
    end
    
    subgraph "Global Data Layer"
        GlobalEventStream[🌊 Global Event Stream<br/>Cross-cell Replication]
        GlobalAnalytics[(📊 Global Analytics DB<br/>Data Warehouse)]
        GlobalConfig[⚙️ Global Config Service<br/>Feature Flags, Settings]
    end
    
    %% Global routing
    GlobalLB --> GlobalGateway
    GlobalGateway --> GlobalAuth
    GlobalGateway --> Cell1LB
    GlobalGateway --> Cell2LB
    GlobalGateway --> Cell3LB
    
    %% Cell 1 internal
    Cell1LB --> Cell1Gateway
    Cell1Gateway --> Cell1User
    Cell1Gateway --> Cell1Order
    Cell1Gateway --> Cell1Payment
    Cell1User --> Cell1UserDB
    Cell1Order --> Cell1OrderDB
    Cell1User --> Cell1Cache
    Cell1Order --> Cell1Queue
    
    %% Cell 2 internal  
    Cell2LB --> Cell2Gateway
    Cell2Gateway --> Cell2User
    Cell2Gateway --> Cell2Order
    Cell2Gateway --> Cell2Payment
    Cell2User --> Cell2UserDB
    Cell2Order --> Cell2OrderDB
    Cell2User --> Cell2Cache
    Cell2Order --> Cell2Queue
    
    %% Cell 3 internal
    Cell3LB --> Cell3Gateway
    Cell3Gateway --> Cell3User
    Cell3Gateway --> Cell3Order
    Cell3Gateway --> Cell3Payment
    Cell3User --> Cell3UserDB
    Cell3Order --> Cell3OrderDB
    Cell3User --> Cell3Cache
    Cell3Order --> Cell3Queue
    
    %% Global data connections
    Cell1Queue --> GlobalEventStream
    Cell2Queue --> GlobalEventStream
    Cell3Queue --> GlobalEventStream
    GlobalEventStream --> GlobalAnalytics
    
    Cell1User --> GlobalConfig
    Cell2User --> GlobalConfig
    Cell3User --> GlobalConfig
    
    classDef global fill:#e8eaf6,stroke:#3f51b5,color:#000,stroke-width:3px
    classDef cell1 fill:#e1f5fe,stroke:#0277bd,color:#000,stroke-width:2px
    classDef cell2 fill:#e8f5e8,stroke:#388e3c,color:#000,stroke-width:2px
    classDef cell3 fill:#fff3e0,stroke:#f57c00,color:#000,stroke-width:2px
    classDef globaldata fill:#fce4ec,stroke:#c2185b,color:#000,stroke-width:2px
    
    class GlobalLB,GlobalGateway,GlobalAuth global
    class Cell1LB,Cell1Gateway,Cell1User,Cell1Order,Cell1Payment,Cell1Inventory,Cell1UserDB,Cell1OrderDB,Cell1Cache,Cell1Queue cell1
    class Cell2LB,Cell2Gateway,Cell2User,Cell2Order,Cell2Payment,Cell2Inventory,Cell2UserDB,Cell2OrderDB,Cell2Cache,Cell2Queue cell2  
    class Cell3LB,Cell3Gateway,Cell3User,Cell3Order,Cell3Payment,Cell3Inventory,Cell3UserDB,Cell3OrderDB,Cell3Cache,Cell3Queue cell3
    class GlobalEventStream,GlobalAnalytics,GlobalConfig globaldata
```

---

## 3. Sequence Diagram Templates

### Distributed Transaction (Saga Pattern)

```mermaid
sequenceDiagram
    participant Client as 📱 Client Application
    participant OrderService as 📦 Order Service<br/>(Saga Orchestrator)
    participant PaymentService as 💳 Payment Service
    participant InventoryService as 📋 Inventory Service  
    participant ShippingService as 🚚 Shipping Service
    participant NotificationService as 📧 Notification Service
    participant EventStore as 📚 Event Store
    
    Note over Client,EventStore: Saga Pattern - Distributed Transaction
    
    Client->>+OrderService: CreateOrder(items, payment, address)
    OrderService->>EventStore: Store SagaStarted Event
    
    %% Step 1: Reserve Inventory
    OrderService->>+InventoryService: ReserveItems(orderId, items)
    alt Inventory Available
        InventoryService-->>-OrderService: ✅ Items Reserved (reservationId)
        OrderService->>EventStore: Store InventoryReserved Event
    else Insufficient Stock
        InventoryService-->>-OrderService: ❌ Insufficient Stock
        OrderService->>EventStore: Store SagaFailed Event
        OrderService-->>Client: ❌ Order Failed - Out of Stock
        Note over OrderService: Saga terminates early
    end
    
    %% Step 2: Process Payment
    OrderService->>+PaymentService: ProcessPayment(orderId, amount, paymentMethod)
    alt Payment Successful
        PaymentService-->>-OrderService: ✅ Payment Confirmed (transactionId)
        OrderService->>EventStore: Store PaymentProcessed Event
    else Payment Failed
        PaymentService-->>-OrderService: ❌ Payment Declined
        OrderService->>EventStore: Store PaymentFailed Event
        %% Compensating action for Step 1
        OrderService->>+InventoryService: CancelReservation(reservationId)
        InventoryService-->>-OrderService: ✅ Reservation Cancelled
        OrderService->>EventStore: Store InventoryCompensated Event
        OrderService-->>Client: ❌ Order Failed - Payment Declined
        Note over OrderService: Saga compensation complete
    end
    
    %% Step 3: Arrange Shipping
    OrderService->>+ShippingService: CreateShipment(orderId, items, address)
    alt Shipping Arranged
        ShippingService-->>-OrderService: ✅ Shipment Created (trackingId)
        OrderService->>EventStore: Store ShipmentArranged Event
    else Shipping Failed
        ShippingService-->>-OrderService: ❌ Shipping Unavailable
        OrderService->>EventStore: Store ShippingFailed Event
        %% Compensating actions for Steps 1 & 2
        par Compensate Payment
            OrderService->>+PaymentService: RefundPayment(transactionId)
            PaymentService-->>-OrderService: ✅ Refund Processed
        and Compensate Inventory
            OrderService->>+InventoryService: CancelReservation(reservationId) 
            InventoryService-->>-OrderService: ✅ Reservation Cancelled
        end
        OrderService->>EventStore: Store SagaCompensated Event
        OrderService-->>Client: ❌ Order Failed - Shipping Unavailable
        Note over OrderService: Saga compensation complete
    end
    
    %% Success Path - Complete Saga
    OrderService->>EventStore: Store SagaCompleted Event
    OrderService->>+NotificationService: SendOrderConfirmation(orderId, customerEmail)
    NotificationService-->>-OrderService: ✅ Notification Sent
    OrderService-->>-Client: ✅ Order Created Successfully (orderId, trackingId)
    
    %% Async notifications
    NotificationService->>Client: 📧 Order Confirmation Email
    ShippingService->>Client: 📱 Shipping Updates
    
    Note over Client,EventStore: All operations are idempotent and recoverable
```

### Circuit Breaker Request Flow

```mermaid
sequenceDiagram
    participant Client as 📱 Client
    participant APIGateway as 🚪 API Gateway
    participant CircuitBreaker as 🔄 Circuit Breaker
    participant ServiceA as 🔧 Service A<br/>(Primary)
    participant ServiceB as 🔧 Service B<br/>(Dependency)
    participant Cache as 🎯 Cache
    participant Fallback as 🛡️ Fallback Service
    participant Monitor as 📊 Monitoring
    
    Note over Client,Monitor: Circuit Breaker Protection Pattern
    
    %% Healthy state requests
    loop Normal Operation (Circuit CLOSED)
        Client->>+APIGateway: API Request
        APIGateway->>+CircuitBreaker: Forward Request
        CircuitBreaker->>CircuitBreaker: Check State: CLOSED
        CircuitBreaker->>+ServiceA: Forward Request
        ServiceA->>+ServiceB: Call Dependency
        ServiceB-->>-ServiceA: ✅ Success Response
        ServiceA-->>-CircuitBreaker: ✅ Success
        CircuitBreaker->>CircuitBreaker: Record Success
        CircuitBreaker-->>-APIGateway: ✅ Response
        APIGateway-->>-Client: ✅ Response
        CircuitBreaker->>Monitor: Success Metric
    end
    
    %% Failures start occurring
    Note over Client,Monitor: Dependency begins failing
    
    Client->>+APIGateway: API Request
    APIGateway->>+CircuitBreaker: Forward Request
    CircuitBreaker->>CircuitBreaker: Check State: CLOSED
    CircuitBreaker->>+ServiceA: Forward Request
    ServiceA->>+ServiceB: Call Dependency
    ServiceB-->>-ServiceA: ❌ Error Response (500)
    ServiceA-->>-CircuitBreaker: ❌ Error
    CircuitBreaker->>CircuitBreaker: Record Failure (3/5)
    CircuitBreaker->>+Fallback: Execute Fallback
    Fallback->>+Cache: Get Cached Data
    Cache-->>-Fallback: Cached Response
    Fallback-->>-CircuitBreaker: Fallback Response
    CircuitBreaker-->>-APIGateway: ⚠️ Degraded Response
    APIGateway-->>-Client: ⚠️ Degraded Response
    CircuitBreaker->>Monitor: Failure Metric
    
    %% Circuit opens after threshold
    Client->>+APIGateway: API Request
    APIGateway->>+CircuitBreaker: Forward Request
    CircuitBreaker->>CircuitBreaker: Check State: CLOSED<br/>Failures: 5/5 (Threshold exceeded)
    CircuitBreaker->>CircuitBreaker: State Change: CLOSED → OPEN
    CircuitBreaker->>+Fallback: Fast Fail to Fallback
    Fallback->>+Cache: Get Cached Data
    Cache-->>-Fallback: Cached Response
    Fallback-->>-CircuitBreaker: Fallback Response
    CircuitBreaker-->>-APIGateway: ⚠️ Fast Fail Response
    APIGateway-->>-Client: ⚠️ Fast Fail Response
    CircuitBreaker->>Monitor: Circuit OPEN Event
    
    %% Multiple fast-fail requests
    loop Circuit OPEN (Fast Fail)
        Client->>+APIGateway: API Request
        APIGateway->>+CircuitBreaker: Forward Request
        CircuitBreaker->>CircuitBreaker: Check State: OPEN
        CircuitBreaker->>+Fallback: Immediate Fallback
        Fallback->>+Cache: Get Cached Data
        Cache-->>-Fallback: Cached Response
        Fallback-->>-CircuitBreaker: Fallback Response
        CircuitBreaker-->>-APIGateway: ⚠️ Fast Response
        APIGateway-->>-Client: ⚠️ Fast Response
        Note over CircuitBreaker: No calls to Service B
    end
    
    %% Recovery timeout expires
    Note over Client,Monitor: Recovery timeout (30s) expires
    
    Client->>+APIGateway: API Request
    APIGateway->>+CircuitBreaker: Forward Request
    CircuitBreaker->>CircuitBreaker: Check State: OPEN<br/>Timeout expired
    CircuitBreaker->>CircuitBreaker: State Change: OPEN → HALF_OPEN
    CircuitBreaker->>+ServiceA: Test Request (Single)
    ServiceA->>+ServiceB: Call Dependency
    ServiceB-->>-ServiceA: ✅ Success Response
    ServiceA-->>-CircuitBreaker: ✅ Success
    CircuitBreaker->>CircuitBreaker: Record Success (1/3)
    CircuitBreaker-->>-APIGateway: ✅ Response
    APIGateway-->>-Client: ✅ Response
    CircuitBreaker->>Monitor: Recovery Testing Started
    
    %% Additional test requests
    loop HALF_OPEN Testing (Limited Traffic)
        Client->>+APIGateway: API Request
        APIGateway->>+CircuitBreaker: Forward Request
        CircuitBreaker->>CircuitBreaker: Check State: HALF_OPEN
        CircuitBreaker->>+ServiceA: Test Request
        ServiceA->>+ServiceB: Call Dependency
        ServiceB-->>-ServiceA: ✅ Success Response
        ServiceA-->>-CircuitBreaker: ✅ Success  
        CircuitBreaker->>CircuitBreaker: Record Success (3/3)
        CircuitBreaker->>CircuitBreaker: State Change: HALF_OPEN → CLOSED
        CircuitBreaker-->>-APIGateway: ✅ Response
        APIGateway-->>-Client: ✅ Response
        CircuitBreaker->>Monitor: Circuit CLOSED - Fully Recovered
    end
    
    Note over Client,Monitor: Circuit fully recovered - normal operation resumed
```

### API Gateway Request Processing

```mermaid
sequenceDiagram
    participant Client as 📱 Client
    participant CDN as 🌐 CDN
    participant Gateway as 🚪 API Gateway
    participant Auth as 🔐 Auth Service
    participant RateLimit as ⚡ Rate Limiter
    participant Cache as 🎯 Cache Layer
    participant Router as 🧭 Service Router
    participant ServiceA as 🔧 Service A
    participant ServiceB as 🔧 Service B
    participant Database as 🗄️ Database
    participant Monitor as 📊 Monitoring
    participant Logger as 📝 Logger
    
    Note over Client,Logger: API Gateway Request Processing Flow
    
    Client->>+CDN: HTTPS Request
    CDN->>CDN: Check Static Cache
    
    alt Static Content (Images, CSS, JS)
        CDN-->>-Client: ✅ Cached Static Content
        CDN->>Monitor: Cache Hit Metric
    else Dynamic API Request
        CDN->>+Gateway: Forward to API Gateway
        Gateway->>Logger: Log Request Start
        Gateway->>Monitor: Request Received Metric
        
        %% Request validation
        Gateway->>Gateway: Validate Request Format
        alt Invalid Request Format
            Gateway-->>CDN: ❌ 400 Bad Request
            CDN-->>-Client: ❌ 400 Bad Request
            Gateway->>Logger: Log Invalid Request
            Gateway->>Monitor: Invalid Request Metric
        end
        
        %% Authentication
        Gateway->>+Auth: Validate JWT Token
        alt Valid Token
            Auth-->>-Gateway: ✅ User Claims (userId, roles)
            Gateway->>Logger: Log Authenticated User
        else Invalid/Expired Token
            Auth-->>-Gateway: ❌ Unauthorized
            Gateway-->>CDN: ❌ 401 Unauthorized
            CDN-->>-Client: ❌ 401 Unauthorized
            Gateway->>Logger: Log Auth Failure
            Gateway->>Monitor: Auth Failure Metric
        end
        
        %% Rate limiting
        Gateway->>+RateLimit: Check Rate Limit (userId)
        alt Within Rate Limit
            RateLimit-->>-Gateway: ✅ Allowed (remaining: 95/100)
            Gateway->>Logger: Log Rate Check Pass
        else Rate Limit Exceeded
            RateLimit-->>-Gateway: ❌ Rate Limit Exceeded
            Gateway-->>CDN: ❌ 429 Too Many Requests
            CDN-->>-Client: ❌ 429 Too Many Requests
            Gateway->>Logger: Log Rate Limit Hit
            Gateway->>Monitor: Rate Limit Metric
        end
        
        %% Cache check
        Gateway->>+Cache: Check Cache (request signature)
        alt Cache Hit
            Cache-->>-Gateway: ✅ Cached Response
            Gateway-->>CDN: ✅ Cached Response
            CDN-->>-Client: ✅ Fast Response
            Gateway->>Logger: Log Cache Hit
            Gateway->>Monitor: Cache Hit Metric
        else Cache Miss
            Cache-->>-Gateway: ❌ Cache Miss
            Gateway->>Logger: Log Cache Miss
            
            %% Service routing
            Gateway->>+Router: Route Request
            Router->>Router: Determine Target Service
            
            alt Route to Service A
                Router->>+ServiceA: Forward Request
                ServiceA->>+Database: Query Data
                Database-->>-ServiceA: Data Response
                ServiceA->>ServiceA: Process Business Logic
                ServiceA-->>-Router: Service Response
            else Route to Service B  
                Router->>+ServiceB: Forward Request
                ServiceB->>+Database: Query Data
                Database-->>-ServiceB: Data Response
                ServiceB->>ServiceB: Process Business Logic
                ServiceB-->>-Router: Service Response
            end
            
            Router-->>-Gateway: Processed Response
            
            %% Cache the response
            Gateway->>Cache: Store Response (TTL: 5min)
            Gateway-->>CDN: ✅ Response
            CDN->>CDN: Cache Response (TTL: 1min)
            CDN-->>-Client: ✅ Response
            
            Gateway->>Logger: Log Request Complete
            Gateway->>Monitor: Request Success Metric
        end
    end
    
    Note over Client,Logger: Request processing complete with full observability
```

---

## 4. Flowchart Templates

### Error Handling Decision Tree

```mermaid
graph TD
    Start([🚀 Request Received]) --> ValidateInput{📋 Valid Input?}
    
    ValidateInput -->|❌ Invalid| ValidationError[❌ Return 400<br/>Bad Request]
    ValidateInput -->|✅ Valid| CheckAuth{🔐 Authenticated?}
    
    CheckAuth -->|❌ No| AuthError[❌ Return 401<br/>Unauthorized]
    CheckAuth -->|✅ Yes| CheckPermissions{👤 Has Permissions?}
    
    CheckPermissions -->|❌ No| PermissionError[❌ Return 403<br/>Forbidden]
    CheckPermissions -->|✅ Yes| CheckRateLimit{⚡ Within Rate Limit?}
    
    CheckRateLimit -->|❌ Exceeded| RateLimitError[❌ Return 429<br/>Too Many Requests]
    CheckRateLimit -->|✅ Within Limit| CheckCircuit{🔄 Circuit Healthy?}
    
    CheckCircuit -->|❌ Open| CircuitOpen{🎯 Cache Available?}
    CheckCircuit -->|✅ Closed| ProcessRequest[⚙️ Process Request]
    
    CircuitOpen -->|✅ Yes| ServeCached[📦 Return Cached Data<br/>with 200 OK]
    CircuitOpen -->|❌ No| CircuitError[❌ Return 503<br/>Service Unavailable]
    
    ProcessRequest --> CallDownstream{📡 Call External Service}
    
    CallDownstream -->|✅ Success| UpdateCache[🎯 Update Cache]
    CallDownstream -->|❌ Error| CheckRetries{🔁 Retries Available?}
    
    CheckRetries -->|✅ Yes| ExponentialBackoff[⏱️ Wait with<br/>Exponential Backoff]
    CheckRetries -->|❌ No| CheckFallback{🛡️ Fallback Available?}
    
    ExponentialBackoff --> ProcessRequest
    
    CheckFallback -->|✅ Yes| ExecuteFallback[🛡️ Execute Fallback<br/>Return Degraded Response]
    CheckFallback -->|❌ No| ServiceError[❌ Return 502<br/>Bad Gateway]
    
    UpdateCache --> Success[✅ Return 200<br/>Success Response]
    
    %% Error logging and monitoring
    ValidationError --> LogError[📝 Log Validation Error]
    AuthError --> LogError
    PermissionError --> LogError  
    RateLimitError --> LogError
    CircuitError --> LogError
    ServiceError --> LogError
    
    LogError --> SendAlert[🚨 Send Alert<br/>if Critical]
    SendAlert --> End([🏁 Request Complete])
    
    Success --> End
    ServeCached --> End
    ExecuteFallback --> End
    
    %% Styling
    classDef startEnd fill:#e8f5e8,stroke:#388e3c,color:#000,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#f57c00,color:#000,stroke-width:2px
    classDef process fill:#e3f2fd,stroke:#1976d2,color:#000,stroke-width:2px
    classDef error fill:#ffebee,stroke:#d32f2f,color:#000,stroke-width:2px
    classDef success fill:#e8f5e8,stroke:#388e3c,color:#000,stroke-width:2px
    classDef cache fill:#f3e5f5,stroke:#7b1fa2,color:#000,stroke-width:2px
    classDef monitoring fill:#e0f2f1,stroke:#00796b,color:#000,stroke-width:2px
    
    class Start,End startEnd
    class ValidateInput,CheckAuth,CheckPermissions,CheckRateLimit,CheckCircuit,CircuitOpen,CallDownstream,CheckRetries,CheckFallback decision
    class ProcessRequest,ExponentialBackoff,ExecuteFallback process
    class ValidationError,AuthError,PermissionError,RateLimitError,CircuitError,ServiceError error
    class Success success
    class UpdateCache,ServeCached cache
    class LogError,SendAlert monitoring
```

### Load Balancer Algorithm Selection

```mermaid
graph TD
    IncomingRequest([🌐 Incoming Request]) --> CheckAlgorithm{⚖️ Load Balancing<br/>Algorithm?}
    
    CheckAlgorithm -->|Round Robin| RoundRobin[🔄 Round Robin<br/>Select Next Server<br/>in Sequence]
    CheckAlgorithm -->|Least Connections| LeastConnections[📊 Least Connections<br/>Select Server with<br/>Fewest Active Connections]
    CheckAlgorithm -->|Weighted Round Robin| WeightedRR[⚖️ Weighted Distribution<br/>Select Based on<br/>Server Capacity Weights]
    CheckAlgorithm -->|Response Time| ResponseTime[⚡ Response Time<br/>Select Fastest<br/>Response Server]
    CheckAlgorithm -->|IP Hash| IPHash[🔗 IP Hash<br/>Hash Client IP<br/>for Session Persistence]
    CheckAlgorithm -->|Least Response Time| LeastRT[🎯 Least Response Time<br/>Combine Connections<br/>and Response Time]
    
    RoundRobin --> HealthCheck{❤️ Server Healthy?}
    LeastConnections --> HealthCheck
    WeightedRR --> HealthCheck
    ResponseTime --> HealthCheck
    IPHash --> HealthCheck
    LeastRT --> HealthCheck
    
    HealthCheck -->|✅ Healthy| CheckCapacity{📈 Server at Capacity?}
    HealthCheck -->|❌ Unhealthy| MarkUnhealthy[⚠️ Mark Server Unhealthy<br/>Remove from Pool]
    
    CheckCapacity -->|✅ Available| ForwardRequest[📨 Forward Request<br/>to Selected Server]
    CheckCapacity -->|❌ At Capacity| TryNextServer[🔄 Try Next Available<br/>Server in Algorithm]
    
    TryNextServer --> CheckAlgorithm
    MarkUnhealthy --> CheckOtherServers{🔍 Other Servers<br/>Available?}
    
    CheckOtherServers -->|✅ Yes| CheckAlgorithm
    CheckOtherServers -->|❌ No| AllServersDown[🚨 All Servers Down<br/>Return 503 Service<br/>Unavailable]
    
    ForwardRequest --> MonitorRequest[📊 Monitor Request<br/>Start Response Timer]
    MonitorRequest --> WaitForResponse[⏳ Wait for<br/>Server Response]
    
    WaitForResponse --> ResponseReceived{📨 Response<br/>Received?}
    
    ResponseReceived -->|✅ Success| UpdateMetrics[📈 Update Server Metrics<br/>• Response Time<br/>• Success Rate<br/>• Active Connections]
    ResponseReceived -->|❌ Timeout/Error| HandleFailure[⚠️ Handle Server Failure<br/>• Increment Error Count<br/>• Check Health Threshold]
    
    HandleFailure --> CheckHealthThreshold{🏥 Health Threshold<br/>Exceeded?}
    CheckHealthThreshold -->|✅ Yes| MarkUnhealthy
    CheckHealthThreshold -->|❌ No| RetryRequest[🔁 Retry Request<br/>with Different Server]
    
    RetryRequest --> CheckAlgorithm
    
    UpdateMetrics --> AdjustWeights[⚖️ Adjust Server Weights<br/>Based on Performance]
    AdjustWeights --> ReturnResponse[📤 Return Response<br/>to Client]
    
    AllServersDown --> ReturnResponse
    
    ReturnResponse --> LogMetrics[📝 Log Request Metrics<br/>• Load Balancer Performance<br/>• Server Selection<br/>• Response Time]
    LogMetrics --> EndRequest([🏁 Request Complete])
    
    %% Background health checking
    MarkUnhealthy -.->|Every 30s| HealthCheckCycle[🔄 Background Health Check<br/>Ping Unhealthy Servers]
    HealthCheckCycle -.->|Server Recovers| RestoreToPool[✅ Restore Server<br/>to Available Pool]
    RestoreToPool -.-> CheckAlgorithm
    
    %% Styling
    classDef startEnd fill:#e8f5e8,stroke:#388e3c,color:#000,stroke-width:2px
    classDef algorithm fill:#e1f5fe,stroke:#0277bd,color:#000,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#f57c00,color:#000,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#7b1fa2,color:#000,stroke-width:2px
    classDef monitoring fill:#e0f2f1,stroke:#00796b,color:#000,stroke-width:2px
    classDef error fill:#ffebee,stroke:#d32f2f,color:#000,stroke-width:2px
    classDef success fill:#e8f5e8,stroke:#388e3c,color:#000,stroke-width:2px
    
    class IncomingRequest,EndRequest startEnd
    class RoundRobin,LeastConnections,WeightedRR,ResponseTime,IPHash,LeastRT algorithm
    class CheckAlgorithm,HealthCheck,CheckCapacity,CheckOtherServers,ResponseReceived,CheckHealthThreshold decision
    class ForwardRequest,TryNextServer,MonitorRequest,WaitForResponse,RetryRequest,AdjustWeights,RestoreToPool process
    class UpdateMetrics,LogMetrics,HealthCheckCycle monitoring
    class MarkUnhealthy,HandleFailure,AllServersDown error
    class ReturnResponse success
```

### Caching Strategy Selection

```mermaid
graph TD
    DataRequest([📊 Data Request]) --> AnalyzeRequest{🔍 Analyze Request<br/>Characteristics}
    
    AnalyzeRequest --> CheckDataType{📋 Data Type?}
    
    CheckDataType -->|Static| StaticData[📄 Static Data<br/>• Images, CSS, JS<br/>• Documentation<br/>• Media Files]
    CheckDataType -->|User-Specific| UserData[👤 User-Specific Data<br/>• Profile, Preferences<br/>• Personalized Content<br/>• Session Data]
    CheckDataType -->|Frequently Accessed| HotData[🔥 Hot Data<br/>• Popular Products<br/>• Trending Content<br/>• Global Statistics]
    CheckDataType -->|Computed Results| ComputedData[⚙️ Computed Data<br/>• Report Results<br/>• Aggregations<br/>• Complex Calculations]
    CheckDataType -->|Real-time| RealTimeData[⚡ Real-time Data<br/>• Live Updates<br/>• Stock Prices<br/>• Chat Messages]
    
    StaticData --> CDNStrategy[🌍 CDN Strategy<br/>• Edge Locations<br/>• Long TTL (24h-30d)<br/>• Geographic Distribution]
    
    UserData --> CheckUserScope{👥 User Scope?}
    CheckUserScope -->|Single User| LocalCacheStrategy[💾 Local Cache Strategy<br/>• Browser/App Cache<br/>• Medium TTL (1h-24h)<br/>• User-specific Keys]
    CheckUserScope -->|Multi-User Shared| SharedCacheStrategy[🎯 Shared Cache Strategy<br/>• Redis/Memcached<br/>• User-segmented Keys<br/>• Privacy Controls]
    
    HotData --> CheckAccessPattern{📈 Access Pattern?}
    CheckAccessPattern -->|Read-Heavy| ReadThroughCache[📖 Read-Through Cache<br/>• Cache Aside Pattern<br/>• Auto Population<br/>• High Hit Ratio Target]
    CheckAccessPattern -->|Write-Heavy| WriteBehindCache[📝 Write-Behind Cache<br/>• Async Persistence<br/>• Batch Updates<br/>• Eventual Consistency]
    CheckAccessPattern -->|Read-Write Mixed| WriteAroundCache[🔄 Write-Around Cache<br/>• Cache on Read<br/>• Skip Cache on Write<br/>• Good for Mixed Workload]
    
    ComputedData --> CheckComputeCost{💰 Compute Cost?}
    CheckComputeCost -->|High Cost| MemoizationStrategy[🧠 Memoization Strategy<br/>• Function Result Cache<br/>• Parameter-based Keys<br/>• Long TTL for Expensive Ops]
    CheckComputeCost -->|Low Cost| LazyLoadStrategy[⏳ Lazy Load Strategy<br/>• Compute on Demand<br/>• Short TTL<br/>• Background Refresh]
    
    RealTimeData --> CheckLatencyReq{⚡ Latency Requirements?}
    CheckLatencyReq -->|Ultra-Low (<1ms)| InMemoryStrategy[⚡ In-Memory Strategy<br/>• Local Cache Only<br/>• No Network Calls<br/>• Pre-loaded Data]
    CheckLatencyReq -->|Low (<10ms)| DistributedCacheStrategy[🌐 Distributed Cache<br/>• Redis Cluster<br/>• Consistent Hashing<br/>• Replication]
    CheckLatencyReq -->|Moderate (<100ms)| MultiLayerStrategy[🏗️ Multi-Layer Strategy<br/>• L1: In-Memory<br/>• L2: Distributed Cache<br/>• L3: Database]
    
    %% Cache implementation details
    CDNStrategy --> SetCDNPolicies[⚙️ Set CDN Policies<br/>• Cache-Control Headers<br/>• Purge Strategies<br/>• Compression]
    
    LocalCacheStrategy --> SetLocalPolicies[⚙️ Set Local Policies<br/>• Storage Limits<br/>• Eviction Strategy<br/>• Refresh Logic]
    
    SharedCacheStrategy --> SetSharedPolicies[⚙️ Set Shared Policies<br/>• Key Namespacing<br/>• TTL Management<br/>• Security Controls]
    
    ReadThroughCache --> ConfigureReadThrough[⚙️ Configure Read-Through<br/>• Cache Miss Handling<br/>• Auto-Population<br/>• Concurrent Access]
    
    WriteBehindCache --> ConfigureWriteBehind[⚙️ Configure Write-Behind<br/>• Buffer Management<br/>• Batch Size<br/>• Failure Handling]
    
    WriteAroundCache --> ConfigureWriteAround[⚙️ Configure Write-Around<br/>• Write Policies<br/>• Cache Invalidation<br/>• Consistency Level]
    
    MemoizationStrategy --> ConfigureMemoization[⚙️ Configure Memoization<br/>• Function Signatures<br/>• Parameter Serialization<br/>• Memory Management]
    
    LazyLoadStrategy --> ConfigureLazyLoad[⚙️ Configure Lazy Load<br/>• Trigger Conditions<br/>• Background Refresh<br/>• Fallback Strategy]
    
    InMemoryStrategy --> ConfigureInMemory[⚙️ Configure In-Memory<br/>• Data Preloading<br/>• Update Mechanisms<br/>• Memory Optimization]
    
    DistributedCacheStrategy --> ConfigureDistributed[⚙️ Configure Distributed<br/>• Cluster Setup<br/>• Replication Factor<br/>• Failover Logic]
    
    MultiLayerStrategy --> ConfigureMultiLayer[⚙️ Configure Multi-Layer<br/>• Layer Hierarchy<br/>• Promotion Strategy<br/>• Consistency Model]
    
    %% Final monitoring setup
    SetCDNPolicies --> SetupMonitoring[📊 Setup Monitoring<br/>• Hit Ratio Tracking<br/>• Performance Metrics<br/>• Cost Analysis]
    SetLocalPolicies --> SetupMonitoring
    SetSharedPolicies --> SetupMonitoring
    ConfigureReadThrough --> SetupMonitoring
    ConfigureWriteBehind --> SetupMonitoring
    ConfigureWriteAround --> SetupMonitoring
    ConfigureMemoization --> SetupMonitoring
    ConfigureLazyLoad --> SetupMonitoring
    ConfigureInMemory --> SetupMonitoring
    ConfigureDistributed --> SetupMonitoring
    ConfigureMultiLayer --> SetupMonitoring
    
    SetupMonitoring --> CacheImplemented([✅ Cache Strategy<br/>Implemented])
    
    %% Styling
    classDef startEnd fill:#e8f5e8,stroke:#388e3c,color:#000,stroke-width:2px
    classDef dataType fill:#e3f2fd,stroke:#1976d2,color:#000,stroke-width:2px
    classDef strategy fill:#f3e5f5,stroke:#7b1fa2,color:#000,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#f57c00,color:#000,stroke-width:2px
    classDef configuration fill:#e0f2f1,stroke:#00796b,color:#000,stroke-width:2px
    classDef monitoring fill:#e8eaf6,stroke:#3f51b5,color:#000,stroke-width:2px
    
    class DataRequest,CacheImplemented startEnd
    class StaticData,UserData,HotData,ComputedData,RealTimeData dataType
    class CDNStrategy,LocalCacheStrategy,SharedCacheStrategy,ReadThroughCache,WriteBehindCache,WriteAroundCache,MemoizationStrategy,LazyLoadStrategy,InMemoryStrategy,DistributedCacheStrategy,MultiLayerStrategy strategy
    class AnalyzeRequest,CheckDataType,CheckUserScope,CheckAccessPattern,CheckComputeCost,CheckLatencyReq decision
    class SetCDNPolicies,SetLocalPolicies,SetSharedPolicies,ConfigureReadThrough,ConfigureWriteBehind,ConfigureWriteAround,ConfigureMemoization,ConfigureLazyLoad,ConfigureInMemory,ConfigureDistributed,ConfigureMultiLayer configuration
    class SetupMonitoring monitoring
```

---

## 5. Performance Visualization Templates

### Latency Distribution Visualization

```mermaid
graph LR
    subgraph "📊 Response Time Distribution Analysis"
        P50[P50: 45ms<br/>█████░░░░░<br/>50% of requests<br/>faster than 45ms]
        P90[P90: 120ms<br/>█████████░<br/>90% of requests<br/>faster than 120ms]
        P95[P95: 180ms<br/>██████████<br/>95% of requests<br/>faster than 180ms]
        P99[P99: 350ms<br/>██████████<br/>99% of requests<br/>faster than 350ms]
        P999[P99.9: 800ms<br/>██████████<br/>99.9% of requests<br/>faster than 800ms]
    end
    
    subgraph "🎯 SLA Targets"
        SLA_Target[SLA Target: 200ms<br/>✅ P95 within target<br/>⚠️ P99 above target<br/>❌ P99.9 critical]
        SLA_Status[Overall SLA Status<br/>🟡 Degraded<br/>Action Required]
    end
    
    subgraph "📈 Performance Zones"
        Fast[🟢 Fast Zone<br/>0-100ms<br/>Excellent UX<br/>Users satisfied]
        Acceptable[🟡 Acceptable Zone<br/>100-300ms<br/>Good UX<br/>Minor delays noticed]
        Slow[🟠 Slow Zone<br/>300-1000ms<br/>Poor UX<br/>Users frustrated]
        Critical[🔴 Critical Zone<br/>>1000ms<br/>Unacceptable<br/>Users abandon]
    end
    
    P50 --> Fast
    P90 --> Acceptable
    P95 --> Acceptable
    P99 --> Slow
    P999 --> Critical
    
    Fast --> SLA_Status
    Acceptable --> SLA_Status
    Slow --> SLA_Status
    Critical --> SLA_Status
    
    SLA_Target --> SLA_Status
    
    classDef fast fill:#4caf50,stroke:#2e7d32,color:#fff,stroke-width:2px
    classDef acceptable fill:#ff9800,stroke:#e65100,color:#fff,stroke-width:2px
    classDef slow fill:#ff5722,stroke:#d84315,color:#fff,stroke-width:2px
    classDef critical fill:#f44336,stroke:#c62828,color:#fff,stroke-width:2px
    classDef sla fill:#2196f3,stroke:#1976d2,color:#fff,stroke-width:2px
    classDef status fill:#9c27b0,stroke:#6a1b9a,color:#fff,stroke-width:2px
    
    class P50,Fast fast
    class P90,P95,Acceptable acceptable
    class P99,Slow slow
    class P999,Critical critical
    class SLA_Target sla
    class SLA_Status status
```

### System Scaling Behavior

```mermaid
graph TD
    subgraph "🚀 System Performance Profile"
        Zone1[🟢 Linear Scaling Zone<br/>Load: 0-1,000 RPS<br/>Response Time: <50ms<br/>CPU: <60%<br/>Memory: <70%<br/>Resources: Underutilized]
        
        Zone2[🟡 Optimal Operation Zone<br/>Load: 1,000-2,000 RPS<br/>Response Time: 50-100ms<br/>CPU: 60-80%<br/>Memory: 70-85%<br/>Resources: Well Utilized]
        
        Zone3[🟠 Saturation Zone<br/>Load: 2,000-3,000 RPS<br/>Response Time: 100-300ms<br/>CPU: 80-95%<br/>Memory: 85-95%<br/>Resources: Near Capacity]
        
        Zone4[🔴 Degradation Zone<br/>Load: 3,000+ RPS<br/>Response Time: >300ms<br/>CPU: >95%<br/>Memory: >95%<br/>Resources: Overloaded]
        
        Zone1 --> Zone2
        Zone2 --> Zone3
        Zone3 --> Zone4
    end
    
    subgraph "⚡ Auto-Scaling Triggers"
        Trigger1[Scale-Out Trigger<br/>CPU > 70% for 2 min<br/>Add +2 instances<br/>Target: Maintain Zone 2]
        
        Trigger2[Scale-Up Trigger<br/>CPU > 90% for 30s<br/>Emergency scaling<br/>Add +5 instances]
        
        Trigger3[Scale-In Trigger<br/>CPU < 40% for 10 min<br/>Remove 1 instance<br/>Maintain cost efficiency]
    end
    
    subgraph "📊 Capacity Planning"
        Current[Current Capacity<br/>5 instances<br/>Peak: 2,500 RPS<br/>Average: 1,200 RPS]
        
        Target[Target Capacity<br/>8 instances planned<br/>Peak: 4,000 RPS<br/>Growth: 60% headroom]
        
        Limits[Hard Limits<br/>Max: 20 instances<br/>Budget: $5,000/month<br/>Alert: 15 instances]
    end
    
    Zone2 --> Trigger1
    Zone3 --> Trigger2
    Zone1 --> Trigger3
    
    Current --> Target
    Target --> Limits
    
    Trigger1 --> Current
    Trigger2 --> Current
    Trigger3 --> Current
    
    classDef linear fill:#4caf50,stroke:#2e7d32,color:#fff,stroke-width:2px
    classDef optimal fill:#8bc34a,stroke:#558b2f,color:#fff,stroke-width:2px
    classDef saturation fill:#ff9800,stroke:#e65100,color:#fff,stroke-width:2px
    classDef degradation fill:#f44336,stroke:#c62828,color:#fff,stroke-width:2px
    classDef trigger fill:#2196f3,stroke:#1976d2,color:#fff,stroke-width:2px
    classDef capacity fill:#9c27b0,stroke:#6a1b9a,color:#fff,stroke-width:2px
    
    class Zone1 linear
    class Zone2 optimal
    class Zone3 saturation
    class Zone4 degradation
    class Trigger1,Trigger2,Trigger3 trigger
    class Current,Target,Limits capacity
```

### Multi-Dimensional Resource Dashboard

```mermaid
graph TD
    subgraph "🖥️ Resource Utilization Dashboard"
        CPU[🔥 CPU Usage<br/>Current: 75%<br/>█████████░ 75%<br/>Threshold: 80%<br/>Status: ⚠️ Warning<br/>Trend: ↗️ Increasing]
        
        Memory[🧠 Memory Usage<br/>Current: 68%<br/>███████░░░ 68%<br/>Threshold: 85%<br/>Status: ✅ Healthy<br/>Trend: → Stable]
        
        Network[🌐 Network I/O<br/>Current: 45%<br/>█████░░░░░ 45%<br/>Threshold: 70%<br/>Status: ✅ Healthy<br/>Trend: ↘️ Decreasing]
        
        Disk[💾 Disk I/O<br/>Current: 82%<br/>████████░░ 82%<br/>Threshold: 80%<br/>Status: ❌ Critical<br/>Trend: ↗️ Increasing]
        
        Database[🗄️ Database<br/>Connections: 450/500<br/>██████████ 90%<br/>Query Time: 45ms<br/>Status: ⚠️ Warning<br/>Trend: → Stable]
        
        Cache[🎯 Cache Performance<br/>Hit Ratio: 94%<br/>██████████ 94%<br/>Memory Used: 3.2GB/4GB<br/>Status: ✅ Healthy<br/>Trend: → Stable]
    end
    
    subgraph "🚨 Alert Management"
        CPUAlert[🚨 CPU Alert<br/>Threshold exceeded<br/>Action: Scale out<br/>ETA: 2 minutes]
        
        DiskAlert[🚨 Disk I/O Alert<br/>High disk usage<br/>Action: Investigate<br/>Priority: High]
        
        DBAlert[⚠️ DB Connection Alert<br/>Near connection limit<br/>Action: Monitor<br/>Priority: Medium]
    end
    
    subgraph "⚙️ Auto-Remediation"
        ScaleOut[📈 Auto Scale-Out<br/>Adding 2 instances<br/>Status: In Progress<br/>ETA: 90 seconds]
        
        CacheWarmup[🔄 Cache Warmup<br/>Preloading hot data<br/>Status: Completed<br/>Hit rate improved: 94%]
        
        DiskCleanup[🧹 Disk Cleanup<br/>Removing old logs<br/>Status: Scheduled<br/>Freed: 2.1GB]
    end
    
    subgraph "📊 Performance Trends"
        Trend24h[📈 24-Hour Trend<br/>Peak CPU: 85% (2pm)<br/>Peak Memory: 78% (3pm)<br/>Peak Disk: 88% (midnight)<br/>Average Response: 67ms]
        
        TrendWeekly[📈 Weekly Trend<br/>Growth: +12% load<br/>New Peak: 3,200 RPS<br/>Availability: 99.94%<br/>Cost: +8% infrastructure]
    end
    
    %% Connections
    CPU --> CPUAlert
    Disk --> DiskAlert
    Database --> DBAlert
    
    CPUAlert --> ScaleOut
    Cache --> CacheWarmup
    Disk --> DiskCleanup
    
    CPU --> Trend24h
    Memory --> Trend24h
    Network --> Trend24h
    Disk --> Trend24h
    
    Trend24h --> TrendWeekly
    
    %% Alert escalation
    CPUAlert -.->|If not resolved| TrendWeekly
    DiskAlert -.->|If critical| TrendWeekly
    DBAlert -.->|Pattern analysis| TrendWeekly
    
    classDef healthy fill:#4caf50,stroke:#2e7d32,color:#fff,stroke-width:2px
    classDef warning fill:#ff9800,stroke:#e65100,color:#fff,stroke-width:2px
    classDef critical fill:#f44336,stroke:#c62828,color:#fff,stroke-width:2px
    classDef alert fill:#e91e63,stroke:#ad1457,color:#fff,stroke-width:2px
    classDef action fill:#2196f3,stroke:#1976d2,color:#fff,stroke-width:2px
    classDef trend fill:#9c27b0,stroke:#6a1b9a,color:#fff,stroke-width:2px
    
    class Memory,Network,Cache healthy
    class CPU,Database warning
    class Disk critical
    class CPUAlert,DiskAlert,DBAlert alert
    class ScaleOut,CacheWarmup,DiskCleanup action
    class Trend24h,TrendWeekly trend
```

---

## Template Customization Guide

### 1. State Machine Customization

**For Circuit Breaker variations:**
- Change state names: `CLOSED` → `HEALTHY`, `OPEN` → `BLOCKED`
- Modify thresholds: `50% error rate` → `10 failures in 60s`
- Adjust timeouts: `30-60 seconds` → `5-300 seconds`
- Add custom states: `FORCED_OPEN`, `DISABLED`

**For other patterns:**
- Copy circuit breaker structure
- Replace states with pattern-specific states
- Update transition conditions
- Modify sub-states as needed

### 2. Architecture Diagram Adaptation

**Service Substitution:**
```
Replace:
- UserService → YourDomainService
- OrderService → YourProcessingService
- PaymentService → YourExternalService

Update icons:
- 👤 → 🏠 (for property service)
- 📦 → 🚗 (for vehicle service)  
- 💳 → 📊 (for analytics service)
```

**Database Adaptation:**
```
Replace:
- PostgreSQL → MySQL, Oracle, etc.
- MongoDB → DynamoDB, Cassandra, etc.
- Redis → Memcached, Hazelcast, etc.
```

### 3. Sequence Diagram Customization

**Participant Modification:**
- Update service names and icons
- Add/remove participants as needed
- Modify interaction patterns
- Update message types and protocols

**Error Path Addition:**
- Copy successful flow
- Add error conditions  
- Include compensation logic
- Update notes and annotations

### 4. Performance Template Usage

**Metric Substitution:**
- Replace response time with throughput
- Change percentiles (P95 → P99.9)
- Update SLA targets
- Modify performance zones

**Threshold Customization:**
- Adjust warning/critical levels
- Update scaling triggers
- Modify time windows
- Change alert conditions

---

These templates provide a comprehensive foundation for creating consistent, informative, and visually appealing diagrams across all DStudio documentation. Each template is designed to be easily customizable while maintaining the established visual standards and educational clarity.
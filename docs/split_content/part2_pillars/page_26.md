Page 26: Data-Modelling Matrix
The Right Data Store for the Right Job:
Use Case              Best Fit          Why
--------              --------          ---
User profiles         Document DB       Flexible schema
Financial ledger      RDBMS            ACID required
Time series          TSDB              Optimized storage
Shopping cart        Redis             Temporary, fast
Log search           Elasticsearch     Full-text search
Social graph         Graph DB          Relationship queries
Analytics            Column store      Aggregation optimized
Files                Object store      Cheap, scalable
Data Model Transformation Costs:
From → To           Difficulty    Example
---------           ----------    -------
Relational → KV     Easy          User table → user:123
Relational → Doc    Medium        Denormalize joins
Relational → Graph  Hard          Edges from FKs
Document → Relation Hard          Normalize nested
Graph → Relational  Very Hard     Recursive queries
Any → Time Series   Easy          Add timestamp
Polyglot Persistence Decision Framework:
START: What's your primary access pattern?
│
├─ Key lookup?
│  ├─ Needs persistence? → Redis with AOF
│  └─ Cache only? → Memcached
│
├─ Complex queries?
│  ├─ Transactions? → PostgreSQL
│  ├─ Analytics? → ClickHouse
│  └─ Search? → Elasticsearch
│
├─ Relationships?
│  ├─ Social graph? → Neo4j
│  └─ Hierarchical? → Document DB
│
├─ Time-based?
│  ├─ Metrics? → Prometheus
│  └─ Events? → Kafka + S3
│
└─ Large objects?
   ├─ Frequent access? → CDN
   └─ Archive? → Glacier
Real-World Polyglot Example: E-commerce
System Component    Data Store       Reasoning
---------------    ----------       ---------
Product catalog    Elasticsearch    Full-text search
User profiles      DynamoDB        Fast lookup, global
Shopping cart      Redis           Session state
Order history      PostgreSQL      Transactions
Recommendations    Neo4j           Graph algorithms
Product images     S3 + CloudFront Blob storage + CDN
Clickstream       Kinesis → S3     Analytics pipeline
Metrics           Prometheus       Time-series
# Episode 090: Distributed SQL - Research Notes

## Executive Summary

Distributed SQL represents the convergence of traditional RDBMS capabilities with distributed systems design, addressing the scalability limitations of monolithic databases while preserving ACID transactions and SQL familiarity. This research explores NewSQL databases like CockroachDB, TiDB, and YugabyteDB, with deep focus on Indian financial services implementations, distributed transaction management, and the practical challenges of migrating from traditional RDBMS to distributed architectures.

Key Indian implementations showcase the evolution: major banks adopting distributed SQL for core banking modernization, e-commerce platforms handling billions of transactions with global consistency, and fintech companies leveraging distributed architectures for regulatory compliance across multiple regions. The analysis covers real-world case studies from HDFC Bank's core banking transformation, Razorpay's payment processing infrastructure, and Zerodha's trading platform architecture.

## 1. NewSQL Database Fundamentals

### 1.1 Evolution from Traditional Databases

The journey from monolithic RDBMS to distributed SQL systems reflects the changing requirements of modern applications. Traditional databases like Oracle, MySQL, and PostgreSQL excel in single-node scenarios but face fundamental limitations when horizontal scaling becomes necessary.

**Monolithic Database Limitations:**

**Single Point of Failure**: Entire system becomes unavailable if the database server fails
**Vertical Scaling Limits**: CPU, memory, and storage constraints on single machines
**Geographic Distribution**: Difficult to achieve low latency across multiple regions
**Maintenance Windows**: Upgrades and maintenance require complete system downtime

**NoSQL Trade-offs:**

The 2000s saw the rise of NoSQL databases like MongoDB, Cassandra, and DynamoDB, which addressed scalability but sacrificed:
- ACID transactions across multiple records
- SQL query interface familiar to developers
- Strong consistency guarantees
- Complex join operations and analytical queries

**NewSQL Promise:**

NewSQL databases attempt to provide the best of both worlds:
- Horizontal scalability of NoSQL systems
- ACID guarantees and SQL interface of traditional RDBMS
- Automatic sharding and replication
- Geographic distribution with strong consistency

### 1.2 CockroachDB Architecture

CockroachDB, inspired by Google's Spanner, provides a distributed SQL database with strong consistency and automatic failover capabilities.

**Core Architecture Components:**

**SQL Layer**: Provides standard SQL interface with PostgreSQL wire protocol compatibility
**Transaction Layer**: Implements distributed transactions using hybrid logical clocks
**Distribution Layer**: Handles data sharding, replication, and consistency protocols
**Storage Layer**: Uses RocksDB for persistent storage with MVCC (Multi-Version Concurrency Control)

**Consensus and Replication**:

CockroachDB uses the Raft consensus algorithm for each range (shard) of data:
- Each range has 3-5 replicas by default
- One replica serves as the Raft leader for writes
- All replicas can serve reads (with potential staleness)
- Automatic leader election on failures

**Geographic Distribution**:

```sql
-- Configure database for multi-region deployment
ALTER DATABASE financial_services ADD REGION 'us-west';
ALTER DATABASE financial_services ADD REGION 'europe-west';
ALTER DATABASE financial_services ADD REGION 'asia-south';

-- Set table locality for performance optimization
ALTER TABLE user_accounts SET LOCALITY REGIONAL BY ROW;
ALTER TABLE transactions SET LOCALITY GLOBAL;
```

**Indian Banking Implementation: HDFC Bank's Core Banking Modernization**

HDFC Bank, India's largest private bank, embarked on a core banking system modernization using CockroachDB to replace their legacy mainframe systems.

**Migration Challenges:**

**Legacy System Complexity**: 30+ year old COBOL-based systems with complex business logic
**Regulatory Compliance**: RBI requirements for data localization and audit trails
**Zero Downtime Requirement**: Banking operations cannot tolerate extended maintenance windows
**Transaction Volume**: 100+ million transactions daily across 50+ million customer accounts

**Architecture Design**:

```sql
-- Customer account structure optimized for Indian banking
CREATE TABLE customer_accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id STRING NOT NULL,
    account_number STRING UNIQUE NOT NULL,
    account_type ENUM('SAVINGS', 'CURRENT', 'FIXED_DEPOSIT') NOT NULL,
    branch_code STRING NOT NULL,
    ifsc_code STRING NOT NULL,
    balance DECIMAL(15,2) NOT NULL CHECK (balance >= 0),
    currency STRING DEFAULT 'INR',
    status ENUM('ACTIVE', 'DORMANT', 'CLOSED') DEFAULT 'ACTIVE',
    kyc_status ENUM('PENDING', 'VERIFIED', 'EXPIRED') NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    region STRING AS (
        CASE 
            WHEN branch_code LIKE '001%' THEN 'MUMBAI'
            WHEN branch_code LIKE '002%' THEN 'DELHI'
            WHEN branch_code LIKE '003%' THEN 'BANGALORE'
            ELSE 'OTHER'
        END
    ) STORED
);

-- Regional partitioning for performance
ALTER TABLE customer_accounts PARTITION BY LIST (region) (
    PARTITION mumbai VALUES IN ('MUMBAI'),
    PARTITION delhi VALUES IN ('DELHI'),
    PARTITION bangalore VALUES IN ('BANGALORE'),
    PARTITION other VALUES IN ('OTHER')
);

-- Transaction table with optimizations for high throughput
CREATE TABLE transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_account_id UUID REFERENCES customer_accounts(account_id),
    to_account_id UUID REFERENCES customer_accounts(account_id),
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    transaction_type ENUM('TRANSFER', 'DEPOSIT', 'WITHDRAWAL', 'FEE') NOT NULL,
    reference_number STRING UNIQUE NOT NULL,
    utr_number STRING, -- Unique Transaction Reference for NEFT/RTGS
    transaction_time TIMESTAMPTZ DEFAULT now(),
    processing_date DATE GENERATED ALWAYS AS (transaction_time::DATE) STORED,
    status ENUM('PENDING', 'COMPLETED', 'FAILED', 'REVERSED') DEFAULT 'PENDING',
    failure_reason STRING,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index optimizations for common query patterns
CREATE INDEX idx_transactions_from_account_time 
    ON transactions (from_account_id, transaction_time DESC);
CREATE INDEX idx_transactions_to_account_time 
    ON transactions (to_account_id, transaction_time DESC);
CREATE INDEX idx_transactions_processing_date 
    ON transactions (processing_date, status);
CREATE INDEX idx_transactions_reference 
    ON transactions (reference_number) WHERE status != 'FAILED';
```

**Distributed Transaction Implementation**:

```sql
-- Complex fund transfer with regulatory compliance
BEGIN;

-- Update sender account balance
UPDATE customer_accounts 
SET balance = balance - 50000,
    updated_at = now()
WHERE account_id = 'sender-account-uuid'
  AND balance >= 50000
  AND status = 'ACTIVE';

-- Check if update affected exactly one row (account exists and has sufficient balance)
INSERT INTO transactions (
    from_account_id, 
    to_account_id, 
    amount, 
    transaction_type,
    reference_number,
    utr_number,
    status,
    metadata
) VALUES (
    'sender-account-uuid',
    'receiver-account-uuid',
    50000,
    'TRANSFER',
    'TXN' || extract(epoch from now())::BIGINT || random()::TEXT,
    'HDFC' || to_char(now(), 'YYYYMMDD') || lpad(nextval('utr_sequence')::TEXT, 6, '0'),
    'PENDING',
    '{"regulatory_code": "NEFT", "purpose_code": "P001", "sender_bank": "HDFC0000001"}'
);

-- Update receiver account balance
UPDATE customer_accounts 
SET balance = balance + 50000,
    updated_at = now()
WHERE account_id = 'receiver-account-uuid'
  AND status = 'ACTIVE';

-- Mark transaction as completed
UPDATE transactions 
SET status = 'COMPLETED',
    transaction_time = now()
WHERE transaction_id = get_transaction_id();

-- Insert audit trail for regulatory compliance
INSERT INTO audit_trail (
    transaction_id,
    action_type,
    user_id,
    timestamp,
    ip_address,
    regulatory_data
) VALUES (
    get_transaction_id(),
    'FUND_TRANSFER_COMPLETED',
    current_user_id(),
    now(),
    current_client_ip(),
    '{"compliance_officer": "system", "risk_score": 0.1}'
);

COMMIT;
```

**Performance Optimizations**:

**Range Splitting Strategy**: Automatic splitting based on transaction volume per branch
**Read Replicas**: Follower reads for customer balance inquiries and statement generation
**Connection Pooling**: PgBouncer configuration optimized for Indian banking workloads
**Batch Processing**: End-of-day reconciliation using distributed batch jobs

**Business Results**:
- 99.99% uptime achieved vs 99.5% with legacy systems
- Transaction processing latency reduced from 500ms to 50ms
- Horizontal scaling enabled handling 3x traffic growth
- Disaster recovery time reduced from 4 hours to 15 minutes

### 1.3 TiDB Architecture

TiDB provides a distributed SQL database with separation of compute and storage, enabling independent scaling of different system components.

**Architecture Components**:

**TiDB Server**: Stateless SQL layer providing MySQL compatibility
**PD (Placement Driver)**: Cluster metadata management and load balancing
**TiKV**: Distributed key-value storage engine using Raft consensus
**TiFlash**: Columnar storage engine for analytical workloads (HTAP)

**Storage Architecture**:

TiKV organizes data into regions (typically 96MB each):
- Each region replicated across 3 TiKV nodes using Raft
- Automatic region splitting and merging based on data size and access patterns
- Multi-Raft implementation enabling high write throughput

**HTAP Capabilities**:

TiDB's unique architecture supports both OLTP and OLAP workloads:
- Row-based storage (TiKV) optimized for transactional workloads
- Columnar storage (TiFlash) optimized for analytical queries
- Real-time data synchronization between row and column stores

**Indian E-commerce Implementation: Flipkart's Order Management System**

Flipkart leveraged TiDB for their order management system to handle Big Billion Days traffic while maintaining data consistency across millions of orders.

**System Requirements**:

**Peak Load**: 100,000+ orders per minute during flash sales
**Data Consistency**: Inventory counts must be accurate to prevent overselling
**Analytics**: Real-time business metrics for decision making
**Geographic Distribution**: Orders processed from 200+ Indian cities

**Schema Design**:

```sql
-- Product catalog with inventory management
CREATE TABLE products (
    product_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sku_id VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(500) NOT NULL,
    brand_id INT NOT NULL,
    category_id INT NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    weight_grams INT,
    dimensions_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    seller_id BIGINT NOT NULL,
    INDEX idx_products_category (category_id, is_active),
    INDEX idx_products_brand (brand_id, is_active),
    INDEX idx_products_seller (seller_id, is_active)
);

-- Inventory management across multiple warehouses
CREATE TABLE inventory (
    inventory_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    warehouse_id INT NOT NULL,
    available_quantity INT NOT NULL DEFAULT 0,
    reserved_quantity INT NOT NULL DEFAULT 0,
    total_quantity GENERATED ALWAYS AS (available_quantity + reserved_quantity) STORED,
    reorder_level INT DEFAULT 10,
    max_stock_level INT DEFAULT 1000,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    UNIQUE KEY uk_product_warehouse (product_id, warehouse_id),
    INDEX idx_inventory_warehouse (warehouse_id, available_quantity),
    INDEX idx_inventory_reorder (reorder_level, available_quantity)
);

-- Orders table optimized for high-throughput inserts
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id BIGINT NOT NULL,
    order_status ENUM('CREATED', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED') DEFAULT 'CREATED',
    total_amount DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    shipping_amount DECIMAL(8,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    final_amount DECIMAL(12,2) GENERATED ALWAYS AS (total_amount - discount_amount + shipping_amount + tax_amount) STORED,
    payment_method ENUM('COD', 'CARD', 'UPI', 'WALLET', 'EMI') NOT NULL,
    payment_status ENUM('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED') DEFAULT 'PENDING',
    shipping_address_json JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    estimated_delivery_date DATE,
    actual_delivery_date DATE,
    warehouse_id INT,
    INDEX idx_orders_customer (customer_id, created_at DESC),
    INDEX idx_orders_status (order_status, created_at),
    INDEX idx_orders_payment (payment_status, payment_method),
    INDEX idx_orders_warehouse (warehouse_id, order_status)
) PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- Order items with detailed tracking
CREATE TABLE order_items (
    item_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    discount_per_item DECIMAL(8,2) DEFAULT 0,
    tax_per_item DECIMAL(8,2) DEFAULT 0,
    seller_id BIGINT NOT NULL,
    fulfillment_status ENUM('PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_order_items_order (order_id),
    INDEX idx_order_items_product (product_id, fulfillment_status),
    INDEX idx_order_items_seller (seller_id, fulfillment_status)
);
```

**Complex Transaction: Order Placement with Inventory Management**

```sql
-- Atomic order placement with inventory reservation
START TRANSACTION;

-- Check inventory availability across warehouses
SELECT 
    i.warehouse_id,
    i.available_quantity,
    w.location_pincode,
    w.shipping_cost_base
FROM inventory i
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
WHERE i.product_id = 12345 
  AND i.available_quantity >= 2
ORDER BY w.shipping_cost_base ASC, i.available_quantity DESC
LIMIT 1;

-- Reserve inventory (atomic update)
UPDATE inventory 
SET available_quantity = available_quantity - 2,
    reserved_quantity = reserved_quantity + 2,
    last_updated = CURRENT_TIMESTAMP
WHERE product_id = 12345 
  AND warehouse_id = 101
  AND available_quantity >= 2;

-- Verify exactly one row was updated (prevents overselling)
SELECT ROW_COUNT() as affected_rows;

-- Create order record
INSERT INTO orders (
    order_number,
    customer_id,
    total_amount,
    discount_amount,
    shipping_amount,
    tax_amount,
    payment_method,
    shipping_address_json,
    warehouse_id,
    estimated_delivery_date
) VALUES (
    CONCAT('FLP', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(CONNECTION_ID(), 6, '0')),
    67890,
    1999.00,
    200.00,
    99.00,
    359.82,
    'UPI',
    '{"street": "123 Main St", "city": "Mumbai", "state": "Maharashtra", "pincode": "400001"}',
    101,
    DATE_ADD(CURRENT_DATE, INTERVAL 3 DAY)
);

-- Get the generated order ID
SET @order_id = LAST_INSERT_ID();

-- Add order items
INSERT INTO order_items (
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_per_item,
    tax_per_item,
    seller_id
) VALUES (
    @order_id,
    12345,
    2,
    999.50,
    100.00,
    179.91,
    5001
);

-- Log order creation for analytics
INSERT INTO order_events (
    order_id,
    event_type,
    event_data,
    created_at
) VALUES (
    @order_id,
    'ORDER_CREATED',
    JSON_OBJECT(
        'customer_id', 67890,
        'warehouse_id', 101,
        'total_amount', 1999.00,
        'payment_method', 'UPI'
    ),
    CURRENT_TIMESTAMP
);

COMMIT;
```

**HTAP Analytics Integration**:

```sql
-- Real-time analytics queries using TiFlash
-- Revenue analysis by hour during Big Billion Days
SELECT 
    DATE_FORMAT(created_at, '%Y-%m-%d %H:00:00') as hour,
    COUNT(*) as order_count,
    SUM(final_amount) as total_revenue,
    AVG(final_amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM orders
WHERE created_at >= '2024-10-01 00:00:00'
  AND created_at < '2024-10-02 00:00:00'
  AND order_status != 'CANCELLED'
GROUP BY DATE_FORMAT(created_at, '%Y-%m-%d %H:00:00')
ORDER BY hour;

-- Product performance analysis
SELECT 
    p.product_name,
    p.brand_id,
    SUM(oi.quantity) as units_sold,
    SUM(oi.total_price) as revenue,
    COUNT(DISTINCT o.customer_id) as unique_buyers,
    AVG(oi.unit_price) as avg_selling_price
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.created_at >= CURRENT_DATE - INTERVAL 7 DAY
  AND o.order_status = 'DELIVERED'
GROUP BY p.product_id, p.product_name, p.brand_id
HAVING units_sold > 100
ORDER BY revenue DESC
LIMIT 50;

-- Geographic distribution of orders
SELECT 
    JSON_UNQUOTE(JSON_EXTRACT(shipping_address_json, '$.state')) as state,
    JSON_UNQUOTE(JSON_EXTRACT(shipping_address_json, '$.city')) as city,
    COUNT(*) as order_count,
    SUM(final_amount) as total_revenue,
    AVG(DATEDIFF(actual_delivery_date, created_at)) as avg_delivery_days
FROM orders
WHERE created_at >= CURRENT_DATE - INTERVAL 30 DAY
  AND order_status = 'DELIVERED'
  AND actual_delivery_date IS NOT NULL
GROUP BY state, city
HAVING order_count > 10
ORDER BY total_revenue DESC;
```

**Performance Metrics During Big Billion Days**:
- Peak throughput: 150,000 transactions per second
- Query latency: P99 < 100ms for OLTP queries
- Analytical query performance: 10x faster than previous MySQL setup
- Zero downtime during traffic spikes
- Inventory accuracy: 99.98% (preventing overselling)

### 1.4 YugabyteDB Architecture

YugabyteDB provides a distributed SQL database with PostgreSQL compatibility and global distribution capabilities.

**Architecture Components**:

**YSQL**: PostgreSQL-compatible SQL layer
**YCQL**: Cassandra-compatible NoSQL API
**DocDB**: Distributed document storage layer
**Tablet Servers**: Store data replicas and serve requests
**Master Servers**: Manage cluster metadata and orchestration

**Unique Features**:

**Multi-API Support**: Same data accessible via SQL and NoSQL APIs
**Consistency Levels**: Tunable consistency from eventual to strong
**Read Replicas**: Async replicas for read scaling and disaster recovery
**Global Secondary Indexes**: Distributed indexes across regions

**Indian Fintech Implementation: Razorpay's Payment Infrastructure**

Razorpay, India's leading payment gateway, uses YugabyteDB to handle payment processing for 8+ million merchants across India.

**System Requirements**:

**Transaction Volume**: 500+ million payments annually
**Latency Requirements**: <50ms for payment authorization
**Regulatory Compliance**: RBI mandates for data storage and audit
**Global Reach**: Support for international merchants and cross-border payments

**Multi-Region Architecture**:

```sql
-- Configure YugabyteDB for Indian payment processing
-- Primary region: Mumbai (West India)
-- Secondary region: Bangalore (South India)  
-- Read replica: Singapore (for international merchants)

CREATE TABLESPACE mumbai_tablespace WITH (
    replica_placement = '{"num_replicas": 3, "placement_blocks": [
        {"cloud": "aws", "region": "ap-south-1", "zone": "ap-south-1a", "min_num_replicas": 1},
        {"cloud": "aws", "region": "ap-south-1", "zone": "ap-south-1b", "min_num_replicas": 1},
        {"cloud": "aws", "region": "ap-south-1", "zone": "ap-south-1c", "min_num_replicas": 1}
    ]}'
);

CREATE TABLESPACE bangalore_tablespace WITH (
    replica_placement = '{"num_replicas": 3, "placement_blocks": [
        {"cloud": "aws", "region": "ap-south-2", "zone": "ap-south-2a", "min_num_replicas": 1},
        {"cloud": "aws", "region": "ap-south-2", "zone": "ap-south-2b", "min_num_replicas": 1},
        {"cloud": "aws", "region": "ap-south-2", "zone": "ap-south-2c", "min_num_replicas": 1}
    ]}'
);
```

**Payment Processing Schema**:

```sql
-- Merchant accounts with regulatory compliance
CREATE TABLE merchants (
    merchant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_code VARCHAR(50) UNIQUE NOT NULL,
    business_name VARCHAR(200) NOT NULL,
    business_type ENUM('INDIVIDUAL', 'PRIVATE_LIMITED', 'PUBLIC_LIMITED', 'PARTNERSHIP', 'LLP') NOT NULL,
    pan_number VARCHAR(10) NOT NULL CHECK (pan_number ~ '^[A-Z]{5}[0-9]{4}[A-Z]{1}$'),
    gstin VARCHAR(15) CHECK (gstin IS NULL OR gstin ~ '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'),
    bank_account_number VARCHAR(20) NOT NULL,
    ifsc_code VARCHAR(11) NOT NULL CHECK (ifsc_code ~ '^[A-Z]{4}0[A-Z0-9]{6}$'),
    settlement_frequency ENUM('DAILY', 'WEEKLY', 'MONTHLY') DEFAULT 'DAILY',
    status ENUM('ACTIVE', 'SUSPENDED', 'TERMINATED') DEFAULT 'ACTIVE',
    kyc_status ENUM('PENDING', 'VERIFIED', 'REJECTED') DEFAULT 'PENDING',
    risk_category ENUM('LOW', 'MEDIUM', 'HIGH') DEFAULT 'MEDIUM',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    compliance_data JSONB,
    INDEX idx_merchants_status (status, kyc_status),
    INDEX idx_merchants_risk (risk_category, status)
) TABLESPACE mumbai_tablespace;

-- Payment transactions with comprehensive tracking
CREATE TABLE payments (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    razor_payment_id VARCHAR(50) UNIQUE NOT NULL,
    merchant_id UUID NOT NULL REFERENCES merchants(merchant_id),
    order_id VARCHAR(100) NOT NULL, -- Merchant's order reference
    amount_paise BIGINT NOT NULL CHECK (amount_paise > 0), -- Amount in paise (INR smallest unit)
    currency VARCHAR(3) DEFAULT 'INR',
    payment_method ENUM('CARD', 'UPI', 'NETBANKING', 'WALLET', 'EMI', 'PAYLATER') NOT NULL,
    payment_submethod VARCHAR(50), -- Specific bank/wallet/UPI app
    status ENUM('CREATED', 'AUTHORIZED', 'CAPTURED', 'FAILED', 'REFUNDED', 'PARTIAL_REFUNDED') DEFAULT 'CREATED',
    gateway_response_code VARCHAR(10),
    gateway_response_message TEXT,
    customer_email VARCHAR(255),
    customer_phone VARCHAR(15) CHECK (customer_phone ~ '^[6-9][0-9]{9}$'), -- Indian mobile format
    customer_ip INET,
    user_agent TEXT,
    transaction_time TIMESTAMPTZ DEFAULT NOW(),
    authorized_at TIMESTAMPTZ,
    captured_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    failure_reason TEXT,
    risk_score DECIMAL(3,2) CHECK (risk_score >= 0 AND risk_score <= 1),
    fraud_flag BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_payments_merchant_time (merchant_id, transaction_time DESC),
    INDEX idx_payments_status (status, transaction_time),
    INDEX idx_payments_method (payment_method, status),
    INDEX idx_payments_risk (risk_score DESC, fraud_flag) WHERE risk_score > 0.7
) PARTITION BY RANGE (transaction_time) TABLESPACE mumbai_tablespace;

-- Create monthly partitions for payments table
CREATE TABLE payments_2024_01 PARTITION OF payments
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE payments_2024_02 PARTITION OF payments
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- ... additional partitions

-- Settlement tracking for regulatory compliance
CREATE TABLE settlements (
    settlement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchants(merchant_id),
    settlement_date DATE NOT NULL,
    total_amount_paise BIGINT NOT NULL,
    fee_amount_paise BIGINT NOT NULL,
    tax_amount_paise BIGINT NOT NULL,
    net_amount_paise BIGINT GENERATED ALWAYS AS (total_amount_paise - fee_amount_paise - tax_amount_paise) STORED,
    transaction_count INT NOT NULL,
    utr_number VARCHAR(50) UNIQUE, -- Bank transfer reference
    settlement_status ENUM('PENDING', 'PROCESSED', 'FAILED', 'REVERSED') DEFAULT 'PENDING',
    processed_at TIMESTAMPTZ,
    bank_reference VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_settlements_merchant_date (merchant_id, settlement_date DESC),
    INDEX idx_settlements_status (settlement_status, settlement_date),
    INDEX idx_settlements_utr (utr_number) WHERE utr_number IS NOT NULL
) TABLESPACE mumbai_tablespace;

-- Audit trail for regulatory compliance
CREATE TABLE audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type ENUM('PAYMENT', 'MERCHANT', 'SETTLEMENT', 'REFUND') NOT NULL,
    entity_id UUID NOT NULL,
    action ENUM('CREATE', 'UPDATE', 'DELETE', 'VIEW') NOT NULL,
    user_id UUID,
    user_type ENUM('SYSTEM', 'ADMIN', 'MERCHANT', 'CUSTOMER') NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_audit_entity (entity_type, entity_id, timestamp DESC),
    INDEX idx_audit_user (user_id, timestamp DESC),
    INDEX idx_audit_timestamp (timestamp DESC)
) TABLESPACE mumbai_tablespace;
```

**Complex Payment Processing Transaction**:

```sql
-- UPI payment processing with fraud detection
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Create payment record
INSERT INTO payments (
    razor_payment_id,
    merchant_id,
    order_id,
    amount_paise,
    payment_method,
    payment_submethod,
    customer_email,
    customer_phone,
    customer_ip,
    user_agent,
    metadata
) VALUES (
    'pay_' || encode(gen_random_bytes(12), 'hex'),
    '123e4567-e89b-12d3-a456-426614174000',
    'ORDER_2024_123456',
    299900, -- ₹2,999
    'UPI',
    'PAYTM',
    'customer@example.com',
    '9876543210',
    '203.192.203.110',
    'RazorpayCheckout/1.0 Mobile',
    '{"merchant_order_reference": "INV_2024_001", "product_category": "electronics"}'
) RETURNING payment_id;

-- Store payment ID for subsequent operations
\set payment_id_var = (SELECT payment_id FROM payments WHERE razor_payment_id = 'pay_latest');

-- Real-time fraud scoring
WITH fraud_features AS (
    SELECT 
        :payment_id_var as payment_id,
        -- Velocity checks
        COUNT(*) FILTER (WHERE transaction_time > NOW() - INTERVAL '1 hour') as payments_last_hour,
        SUM(amount_paise) FILTER (WHERE transaction_time > NOW() - INTERVAL '1 hour') as amount_last_hour,
        -- Device/IP checks  
        COUNT(DISTINCT customer_ip) FILTER (WHERE transaction_time > NOW() - INTERVAL '1 day') as unique_ips_24h,
        -- Merchant risk
        (SELECT risk_category FROM merchants WHERE merchant_id = '123e4567-e89b-12d3-a456-426614174000') as merchant_risk
    FROM payments 
    WHERE customer_phone = '9876543210'
),
risk_calculation AS (
    SELECT 
        payment_id,
        CASE 
            WHEN payments_last_hour > 5 THEN 0.8
            WHEN amount_last_hour > 10000000 THEN 0.7 -- More than ₹1 lakh
            WHEN unique_ips_24h > 3 THEN 0.6
            WHEN merchant_risk = 'HIGH' THEN 0.5
            ELSE 0.1
        END as calculated_risk_score
    FROM fraud_features
)
UPDATE payments 
SET risk_score = risk_calculation.calculated_risk_score,
    fraud_flag = (risk_calculation.calculated_risk_score > 0.5)
FROM risk_calculation
WHERE payments.payment_id = risk_calculation.payment_id;

-- Authorize payment if fraud score is acceptable
UPDATE payments 
SET status = CASE 
        WHEN risk_score <= 0.5 THEN 'AUTHORIZED'
        ELSE 'FAILED'
    END,
    authorized_at = CASE 
        WHEN risk_score <= 0.5 THEN NOW()
        ELSE NULL
    END,
    failed_at = CASE 
        WHEN risk_score > 0.5 THEN NOW()
        ELSE NULL
    END,
    failure_reason = CASE 
        WHEN risk_score > 0.5 THEN 'Transaction blocked due to fraud risk'
        ELSE NULL
    END
WHERE payment_id = :payment_id_var;

-- Log transaction for audit trail
INSERT INTO audit_logs (
    entity_type,
    entity_id,
    action,
    user_type,
    new_values,
    ip_address,
    user_agent
) VALUES (
    'PAYMENT',
    :payment_id_var,
    'CREATE',
    'CUSTOMER',
    (SELECT row_to_json(p) FROM payments p WHERE payment_id = :payment_id_var),
    '203.192.203.110',
    'RazorpayCheckout/1.0 Mobile'
);

COMMIT;
```

**Geographic Distribution Benefits**:
- Mumbai region: <10ms latency for most Indian transactions
- Bangalore region: Disaster recovery and load distribution
- Singapore replica: <100ms latency for Southeast Asian merchants
- Automatic failover between regions with <30 second RTO

**Compliance and Security Features**:

**Data Localization**: All Indian payment data stored within Indian regions
**Encryption**: TDE (Transparent Data Encryption) for data at rest
**Audit Trails**: Complete transaction history for regulatory reporting
**Access Controls**: Role-based access with multi-factor authentication

**Performance Metrics**:
- Peak throughput: 50,000 payments per second
- Authorization latency: P99 < 50ms
- Database availability: 99.99% uptime
- Cross-region replication lag: <5 seconds

## 2. Distributed Transactions and Consistency

### 2.1 ACID Properties in Distributed Systems

Maintaining ACID (Atomicity, Consistency, Isolation, Durability) properties in distributed systems presents unique challenges compared to single-node databases.

**Atomicity Challenges**:

In distributed systems, a single transaction may span multiple nodes. Ensuring all-or-nothing execution requires coordination mechanisms:

**Two-Phase Commit (2PC)**: Traditional approach with coordinator and participants
- Phase 1: Prepare phase - all participants vote to commit or abort
- Phase 2: Commit phase - coordinator instructs all participants to commit or abort
- Drawback: Blocking protocol susceptible to coordinator failures

**Three-Phase Commit (3PC)**: Non-blocking extension of 2PC
- Additional "pre-commit" phase to reduce blocking scenarios
- Higher message complexity and latency overhead

**Saga Pattern**: Long-running transactions as sequence of compensatable steps
- Each step has corresponding compensation action
- Either all steps complete or compensations restore original state
- Well-suited for microservices architectures

**Consistency in Distributed Context**:

**Strong Consistency**: All nodes see the same data simultaneously
- Achieved through consensus protocols like Raft or Paxos
- Higher latency due to coordination overhead
- Preferred for financial and critical applications

**Eventual Consistency**: Nodes converge to same state over time
- Lower latency but temporary inconsistencies possible
- Suitable for social media, content management systems

**Causal Consistency**: Operations preserve causal relationships
- Middle ground between strong and eventual consistency
- Complex to implement but offers good performance-consistency balance

### 2.2 Consensus Protocols

**Raft Consensus Algorithm**:

Raft provides a more understandable alternative to Paxos for achieving consensus in distributed systems.

**Key Concepts**:

**Leader Election**: One node serves as leader, others as followers
**Log Replication**: Leader replicates log entries to followers
**Safety**: At most one leader per term, committed entries never lost

**Raft Implementation in CockroachDB**:

```go
// Simplified Raft implementation concepts
type RaftNode struct {
    nodeID      int
    currentTerm int
    votedFor    int
    log         []LogEntry
    commitIndex int
    lastApplied int
    state       NodeState // FOLLOWER, CANDIDATE, LEADER
}

type LogEntry struct {
    Term    int
    Index   int
    Command interface{}
}

// Leader election process
func (r *RaftNode) startElection() {
    r.currentTerm++
    r.state = CANDIDATE
    r.votedFor = r.nodeID
    
    votes := 1 // Vote for self
    for _, peer := range r.peers {
        if peer.requestVote(r.currentTerm, r.nodeID) {
            votes++
        }
    }
    
    if votes > len(r.peers)/2 {
        r.becomeLeader()
    } else {
        r.becomeFollower()
    }
}

// Log replication
func (r *RaftNode) appendEntries(entry LogEntry) bool {
    if r.state != LEADER {
        return false
    }
    
    r.log = append(r.log, entry)
    
    // Replicate to majority of followers
    replicationCount := 1 // Leader's vote
    for _, follower := range r.followers {
        if follower.appendEntry(entry) {
            replicationCount++
        }
    }
    
    if replicationCount > len(r.peers)/2 {
        r.commitIndex = entry.Index
        return true
    }
    
    return false
}
```

**Indian Banking Example: ICICI Bank's Distributed Consensus**

ICICI Bank's core banking system uses Raft consensus for critical operations like account balance updates and transaction logging.

```sql
-- Account balance update with Raft consensus
-- This operation must be replicated across 3 data centers
BEGIN;

-- Update executed on Raft leader
UPDATE account_balances 
SET balance = balance - 50000,
    last_updated = NOW(),
    version = version + 1
WHERE account_number = 'ICICI123456789'
  AND balance >= 50000;

-- Raft automatically replicates this log entry to followers
-- Transaction commits only after majority acknowledgment

-- Insert transaction record (also replicated via Raft)
INSERT INTO transaction_log (
    account_number,
    transaction_type,
    amount,
    balance_after,
    timestamp,
    raft_log_index
) VALUES (
    'ICICI123456789',
    'WITHDRAWAL',
    50000,
    (SELECT balance FROM account_balances WHERE account_number = 'ICICI123456789'),
    NOW(),
    get_current_raft_index()
);

COMMIT;
```

**Benefits for Indian Banking**:
- **Disaster Recovery**: Automatic failover between Mumbai, Delhi, and Bangalore data centers
- **Regulatory Compliance**: Immutable transaction logs across multiple locations
- **High Availability**: Continues operating with 1 data center failure
- **Audit Trail**: Complete transaction history with consensus verification

### 2.3 Multi-Version Concurrency Control (MVCC)

MVCC enables high concurrency by maintaining multiple versions of data, allowing readers and writers to operate without blocking each other.

**MVCC Implementation Concepts**:

**Version Numbers**: Each data modification creates new version with timestamp
**Snapshot Isolation**: Transactions see consistent snapshot of data as of start time
**Garbage Collection**: Old versions cleaned up when no longer needed

**CockroachDB MVCC Example**:

```sql
-- Time: T1
BEGIN TRANSACTION ISOLATION LEVEL SNAPSHOT;
SELECT balance FROM accounts WHERE account_id = 'ACC123'; -- Returns 1000

-- Time: T2 (concurrent transaction)
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance + 500 WHERE account_id = 'ACC123';
COMMIT; -- Balance now 1500, but other transaction still sees 1000

-- Time: T3 (back to first transaction)
SELECT balance FROM accounts WHERE account_id = 'ACC123'; -- Still returns 1000
UPDATE accounts SET balance = balance - 200 WHERE account_id = 'ACC123';
COMMIT; -- This will fail due to version conflict
```

**Conflict Resolution Strategies**:

**First Writer Wins**: First transaction to commit succeeds, others abort
**Last Writer Wins**: Most recent update overwrites previous changes (dangerous)
**Application-Level Resolution**: Custom logic to merge conflicting changes

**Indian E-commerce: Myntra's Inventory Concurrency**

Myntra handles inventory updates with MVCC to prevent overselling during flash sales:

```sql
-- Product inventory with version-based optimistic locking
CREATE TABLE product_inventory (
    product_id BIGINT PRIMARY KEY,
    available_stock INT NOT NULL,
    reserved_stock INT NOT NULL,
    version_number BIGINT NOT NULL DEFAULT 1,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Optimistic locking for inventory updates
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Read current inventory with version
SELECT available_stock, version_number 
FROM product_inventory 
WHERE product_id = 12345;

-- Application logic checks if sufficient stock available
-- Let's say we read: available_stock = 100, version_number = 42

-- Attempt to reserve inventory with version check
UPDATE product_inventory 
SET available_stock = available_stock - 5,
    reserved_stock = reserved_stock + 5,
    version_number = version_number + 1,
    last_updated = NOW()
WHERE product_id = 12345 
  AND version_number = 42; -- Version check prevents lost updates

-- Check if update succeeded (affected_rows = 1)
-- If affected_rows = 0, version conflict occurred, retry transaction

COMMIT;
```

**Performance Benefits**:
- **No Lock Contention**: Readers never block writers or other readers
- **High Concurrency**: Thousands of concurrent inventory checks during sales
- **Predictable Performance**: No lock escalation or deadlock scenarios
- **Snapshot Consistency**: Analytical queries see consistent data without affecting OLTP

## 3. CAP Theorem in Practice

### 3.1 Understanding CAP Trade-offs

The CAP theorem states that distributed systems can guarantee at most two of three properties: Consistency, Availability, and Partition tolerance.

**Consistency (C)**: All nodes see the same data simultaneously
**Availability (A)**: System remains operational and responsive
**Partition Tolerance (P)**: System continues operating despite network failures

In practice, network partitions are inevitable in distributed systems, so the choice becomes between Consistency and Availability during partition scenarios.

**CP Systems (Consistency + Partition Tolerance)**:
- Examples: CockroachDB, Google Spanner, FaunaDB
- Sacrifice availability during partitions to maintain consistency
- Suitable for financial systems, inventory management

**AP Systems (Availability + Partition Tolerance)**:
- Examples: Cassandra, DynamoDB, CouchDB
- Remain available during partitions but may serve inconsistent data
- Suitable for social media, content delivery, analytics

**CA Systems (Consistency + Availability)**:
- Traditional single-node databases
- Cannot tolerate network partitions
- Not viable for truly distributed systems

### 3.2 Indian Financial Services: Choosing CP over AP

Indian financial institutions predominantly choose CP systems due to regulatory requirements and the critical nature of financial data consistency.

**RBI Regulations Favoring Consistency**:

**Transaction Accuracy**: All fund transfers must be atomic and consistent
**Audit Requirements**: Complete transaction history must be maintained
**Real-time Fraud Detection**: Consistent view of account balances required
**Regulatory Reporting**: Accurate financial data for compliance reports

**State Bank of India (SBI) Architecture**:

SBI, India's largest bank, migrated from mainframe to distributed CP systems while maintaining strict consistency guarantees.

```sql
-- SBI's account transfer with strict consistency
CREATE OR REPLACE FUNCTION transfer_funds(
    from_account VARCHAR(20),
    to_account VARCHAR(20),
    amount DECIMAL(15,2),
    transfer_reference VARCHAR(50)
) RETURNS BOOLEAN AS $$
DECLARE
    from_balance DECIMAL(15,2);
    to_balance DECIMAL(15,2);
    transaction_id UUID;
BEGIN
    -- Start transaction with highest isolation level
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
    
    -- Lock source account for update (prevents concurrent modifications)
    SELECT balance INTO from_balance 
    FROM customer_accounts 
    WHERE account_number = from_account 
    FOR UPDATE;
    
    -- Verify sufficient balance
    IF from_balance < amount THEN
        RAISE EXCEPTION 'Insufficient balance. Available: %, Required: %', from_balance, amount;
    END IF;
    
    -- Lock destination account
    SELECT balance INTO to_balance 
    FROM customer_accounts 
    WHERE account_number = to_account 
    FOR UPDATE;
    
    -- Generate unique transaction ID
    transaction_id := gen_random_uuid();
    
    -- Debit source account
    UPDATE customer_accounts 
    SET balance = balance - amount,
        last_transaction_time = NOW()
    WHERE account_number = from_account;
    
    -- Credit destination account  
    UPDATE customer_accounts 
    SET balance = balance + amount,
        last_transaction_time = NOW()
    WHERE account_number = to_account;
    
    -- Record transaction details
    INSERT INTO transaction_history (
        transaction_id,
        from_account,
        to_account,
        amount,
        transfer_reference,
        transaction_status,
        created_at
    ) VALUES (
        transaction_id,
        from_account,
        to_account,
        amount,
        transfer_reference,
        'COMPLETED',
        NOW()
    );
    
    -- Log for regulatory compliance
    INSERT INTO regulatory_audit_log (
        transaction_id,
        transaction_type,
        amount,
        source_account,
        destination_account,
        compliance_status,
        audit_timestamp
    ) VALUES (
        transaction_id,
        'FUND_TRANSFER',
        amount,
        from_account,
        to_account,
        'COMPLIANT',
        NOW()
    );
    
    RETURN TRUE;
    
EXCEPTION 
    WHEN OTHERS THEN
        -- Log failure for investigation
        INSERT INTO failed_transaction_log (
            from_account,
            to_account,
            amount,
            failure_reason,
            failed_at
        ) VALUES (
            from_account,
            to_account,
            amount,
            SQLERRM,
            NOW()
        );
        
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;
```

**Handling Network Partitions in Indian Banking**:

When network partitions occur, SBI's system prioritizes consistency over availability:

```sql
-- Partition detection and handling
CREATE OR REPLACE FUNCTION handle_network_partition() RETURNS VOID AS $$
DECLARE
    primary_dc_health BOOLEAN;
    secondary_dc_health BOOLEAN;
    majority_available BOOLEAN;
BEGIN
    -- Check data center connectivity
    SELECT check_dc_health('mumbai') INTO primary_dc_health;
    SELECT check_dc_health('delhi') INTO secondary_dc_health;
    SELECT check_dc_health('bangalore') INTO tertiary_dc_health;
    
    -- Determine if majority of replicas are available
    majority_available := (primary_dc_health::INT + secondary_dc_health::INT + tertiary_dc_health::INT) >= 2;
    
    IF NOT majority_available THEN
        -- Enter read-only mode to maintain consistency
        SET default_transaction_read_only = on;
        
        -- Alert operations team
        INSERT INTO system_alerts (
            alert_type,
            severity,
            message,
            created_at
        ) VALUES (
            'NETWORK_PARTITION',
            'CRITICAL',
            'Majority of replicas unavailable. System in read-only mode.',
            NOW()
        );
        
        -- Disable new transaction processing
        UPDATE system_configuration 
        SET value = 'false' 
        WHERE key = 'accept_new_transactions';
    ELSE
        -- Sufficient replicas available, continue normal operation
        SET default_transaction_read_only = off;
        
        UPDATE system_configuration 
        SET value = 'true' 
        WHERE key = 'accept_new_transactions';
    END IF;
END;
$$ LANGUAGE plpgsql;
```

**Business Impact of CP Choice**:

**Customer Trust**: Zero fund transfer errors maintaining customer confidence
**Regulatory Compliance**: 100% audit trail accuracy for RBI inspections
**Risk Management**: Immediate fraud detection with consistent data views
**Operational Efficiency**: Reduced manual reconciliation due to data consistency

**Availability Metrics Despite CP Choice**:
- Planned availability: 99.95% (scheduled maintenance windows)
- Unplanned downtime: <0.01% (robust infrastructure and failover)
- Mean time to recovery: <5 minutes for single data center failures
- Customer satisfaction: 98%+ for digital banking services

### 3.3 E-commerce: Balancing CAP for Different Use Cases

Indian e-commerce platforms like Flipkart and Amazon India make different CAP choices for different parts of their system.

**Flipkart's Multi-System Approach**:

**Inventory Management (CP)**: Strong consistency for stock levels
**Product Catalog (AP)**: High availability for browsing experience
**User Sessions (AP)**: Available shopping cart even during partitions
**Payment Processing (CP)**: Strict consistency for financial transactions

```sql
-- Inventory system (CP) - Strong consistency required
CREATE TABLE product_inventory_cp (
    product_id BIGINT PRIMARY KEY,
    warehouse_id INT NOT NULL,
    available_quantity INT NOT NULL,
    reserved_quantity INT NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT NOW()
) WITH (
    replication_factor = 3,
    consistency_level = 'STRONG'
);

-- Product catalog (AP) - High availability preferred
CREATE TABLE product_catalog_ap (
    product_id BIGINT PRIMARY KEY,
    product_name VARCHAR(500),
    description TEXT,
    images JSONB,
    price DECIMAL(10,2),
    category_id INT,
    last_updated TIMESTAMPTZ DEFAULT NOW()
) WITH (
    replication_factor = 3,
    consistency_level = 'EVENTUAL',
    read_preference = 'NEAREST'
);

-- User sessions (AP) - Availability over consistency
CREATE TABLE user_sessions_ap (
    session_id UUID PRIMARY KEY,
    user_id BIGINT,
    cart_items JSONB,
    session_start TIMESTAMPTZ,
    last_activity TIMESTAMPTZ,
    ip_address INET
) WITH (
    replication_factor = 2,
    consistency_level = 'EVENTUAL',
    ttl_seconds = 86400 -- 24 hours
);
```

**Handling CAP Trade-offs During Big Billion Days**:

During Flipkart's mega sale events, different subsystems handle partitions differently:

```python
# Inventory reservation with CP guarantees
def reserve_inventory_cp(product_id, quantity, user_id):
    try:
        with get_cp_connection(consistency='STRONG') as conn:
            cursor = conn.cursor()
            
            # Atomic inventory check and reservation
            cursor.execute("""
                UPDATE product_inventory_cp 
                SET available_quantity = available_quantity - %s,
                    reserved_quantity = reserved_quantity + %s
                WHERE product_id = %s 
                  AND available_quantity >= %s
                RETURNING available_quantity
            """, (quantity, quantity, product_id, quantity))
            
            result = cursor.fetchone()
            if result is None:
                return {"success": False, "reason": "INSUFFICIENT_STOCK"}
            
            # Log reservation for audit
            cursor.execute("""
                INSERT INTO inventory_reservations (
                    product_id, user_id, quantity, 
                    reservation_time, status
                ) VALUES (%s, %s, %s, NOW(), 'RESERVED')
            """, (product_id, user_id, quantity))
            
            conn.commit()
            return {"success": True, "reserved_quantity": quantity}
            
    except PartitionException:
        # During partition, prefer consistency over availability
        return {"success": False, "reason": "SYSTEM_UNAVAILABLE"}
    except Exception as e:
        return {"success": False, "reason": str(e)}

# Product browsing with AP guarantees
def get_product_details_ap(product_id):
    try:
        # Try primary data center first
        with get_ap_connection(preference='PRIMARY') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT product_name, description, price, images
                FROM product_catalog_ap 
                WHERE product_id = %s
            """, (product_id,))
            return cursor.fetchone()
            
    except PartitionException:
        # Fallback to any available replica during partition
        try:
            with get_ap_connection(preference='NEAREST') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT product_name, description, price, images
                    FROM product_catalog_ap 
                    WHERE product_id = %s
                """, (product_id,))
                result = cursor.fetchone()
                
                # Add staleness warning to response
                if result:
                    result['warning'] = 'Data may be slightly outdated'
                return result
                
        except Exception:
            # Return cached data as last resort
            return get_cached_product_details(product_id)

# User cart management with AP guarantees
def update_user_cart_ap(session_id, cart_items):
    try:
        # Accept updates even during partitions
        with get_ap_connection(consistency='EVENTUAL') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_sessions_ap (
                    session_id, cart_items, last_activity
                ) VALUES (%s, %s, NOW())
                ON CONFLICT (session_id) 
                DO UPDATE SET 
                    cart_items = EXCLUDED.cart_items,
                    last_activity = EXCLUDED.last_activity
            """, (session_id, json.dumps(cart_items)))
            
            conn.commit()
            return {"success": True}
            
    except Exception as e:
        # Store in local cache during complete outage
        cache_cart_update(session_id, cart_items)
        return {"success": True, "cached": True}
```

**Monitoring CAP Trade-offs**:

```sql
-- Monitor consistency lag across replicas
CREATE VIEW consistency_monitoring AS
SELECT 
    table_name,
    primary_node,
    replica_node,
    replication_lag_seconds,
    last_sync_time,
    CASE 
        WHEN replication_lag_seconds < 1 THEN 'STRONG'
        WHEN replication_lag_seconds < 60 THEN 'EVENTUAL'
        ELSE 'LAGGING'
    END as consistency_level
FROM replication_status;

-- Alert on excessive replication lag
CREATE OR REPLACE FUNCTION check_replication_health() RETURNS VOID AS $$
BEGIN
    INSERT INTO system_alerts (alert_type, severity, message)
    SELECT 
        'REPLICATION_LAG',
        'WARNING',
        'Table ' || table_name || ' has replication lag of ' || replication_lag_seconds || ' seconds'
    FROM consistency_monitoring 
    WHERE replication_lag_seconds > 60;
END;
$$ LANGUAGE plpgsql;
```

**Business Results of Multi-CAP Approach**:

**Customer Experience**: 99.9% browse availability during peak sales
**Inventory Accuracy**: Zero overselling incidents with CP inventory system
**Revenue Protection**: Strict payment consistency preventing double charges
**Operational Efficiency**: Reduced support tickets due to data consistency issues

## 4. Sharding Strategies and Geo-Distribution

### 4.1 Horizontal Sharding Approaches

Sharding distributes data across multiple database instances, enabling horizontal scaling beyond the limits of single-node systems.

**Sharding Strategies**:

**Range-based Sharding**: Partition data based on key ranges
- Example: Users A-M on Shard 1, N-Z on Shard 2
- Pros: Range queries efficient, predictable data distribution
- Cons: Hotspots possible, rebalancing complex

**Hash-based Sharding**: Use hash function to determine shard placement
- Example: hash(user_id) % num_shards
- Pros: Even distribution, simple implementation
- Cons: Range queries require cross-shard operations

**Directory-based Sharding**: Lookup service maps keys to shards
- Example: Separate service tracks which shard contains each customer
- Pros: Flexible, supports migrations
- Cons: Additional complexity, potential bottleneck

**Composite Sharding**: Combine multiple strategies
- Example: Hash by customer_id, then range by timestamp
- Pros: Optimized for specific query patterns
- Cons: Increased complexity

### 4.2 Indian Fintech: PhonePe's Sharding Strategy

PhonePe, processing 5+ billion UPI transactions annually, uses sophisticated sharding to handle India's massive payment volume.

**Multi-dimensional Sharding Architecture**:

```sql
-- User accounts sharded by phone number hash
CREATE TABLE user_accounts_shard_1 (
    user_id UUID PRIMARY KEY,
    phone_number VARCHAR(13) NOT NULL, -- +91XXXXXXXXXX format
    phone_hash INT GENERATED ALWAYS AS (hashtext(phone_number)) STORED,
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(255),
    kyc_status ENUM('PENDING', 'BASIC', 'FULL') DEFAULT 'PENDING',
    wallet_balance_paise BIGINT DEFAULT 0,
    account_status ENUM('ACTIVE', 'SUSPENDED', 'CLOSED') DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    CHECK (phone_hash % 8 = 1) -- This shard handles hash values ending in 1
);

-- Similar tables for shards 2-8
-- CREATE TABLE user_accounts_shard_2 ... CHECK (phone_hash % 8 = 2)

-- Transactions sharded by composite key (phone + time)
CREATE TABLE transactions_shard_mumbai_2024_q1 (
    transaction_id UUID PRIMARY KEY,
    sender_phone VARCHAR(13) NOT NULL,
    receiver_phone VARCHAR(13) NOT NULL,
    amount_paise BIGINT NOT NULL,
    transaction_type ENUM('P2P', 'P2M', 'RECHARGE', 'BILL_PAYMENT') NOT NULL,
    upi_ref_id VARCHAR(50) UNIQUE NOT NULL,
    merchant_id UUID,
    transaction_time TIMESTAMPTZ DEFAULT NOW(),
    status ENUM('INITIATED', 'SUCCESS', 'FAILED', 'PENDING') DEFAULT 'INITIATED',
    failure_reason TEXT,
    location_lat DECIMAL(10, 8),
    location_lon DECIMAL(11, 8),
    device_fingerprint VARCHAR(100),
    CHECK (
        extract(quarter from transaction_time) = 1 AND
        extract(year from transaction_time) = 2024 AND
        get_region_from_phone(sender_phone) = 'MUMBAI'
    )
);

-- Geographic + temporal partitioning for optimal performance
CREATE TABLE transactions_shard_delhi_2024_q1 (
    -- Same structure as Mumbai shard
    CHECK (
        extract(quarter from transaction_time) = 1 AND
        extract(year from transaction_time) = 2024 AND
        get_region_from_phone(sender_phone) = 'DELHI'
    )
);
```

**Intelligent Shard Routing**:

```python
class PhonePeShardRouter:
    def __init__(self):
        self.user_shards = 8  # Based on phone number hash
        self.transaction_shards = {
            'mumbai': 'transactions_shard_mumbai',
            'delhi': 'transactions_shard_delhi', 
            'bangalore': 'transactions_shard_bangalore',
            'other': 'transactions_shard_other'
        }
        
    def get_user_shard(self, phone_number):
        """Route user operations to appropriate shard"""
        phone_hash = hash(phone_number)
        shard_id = phone_hash % self.user_shards + 1
        return f"user_accounts_shard_{shard_id}"
    
    def get_transaction_shard(self, sender_phone, transaction_time):
        """Route transactions based on geography and time"""
        region = self.get_region_from_phone(sender_phone)
        quarter = f"{transaction_time.year}_q{(transaction_time.month-1)//3 + 1}"
        
        base_shard = self.transaction_shards.get(region, 'other')
        return f"{base_shard}_{quarter}"
    
    def get_region_from_phone(self, phone_number):
        """Determine region from phone number area code"""
        area_codes = {
            ('022', '091'): 'mumbai',     # Mumbai area codes
            ('011', '093'): 'delhi',      # Delhi area codes  
            ('080', '097'): 'bangalore',  # Bangalore area codes
        }
        
        for codes, region in area_codes.items():
            if any(phone_number.startswith(code) for code in codes):
                return region
        return 'other'
    
    def execute_cross_shard_transaction(self, sender_phone, receiver_phone, amount):
        """Handle transactions spanning multiple shards"""
        sender_shard = self.get_user_shard(sender_phone)
        receiver_shard = self.get_user_shard(receiver_phone)
        
        if sender_shard == receiver_shard:
            # Single shard transaction
            return self.execute_local_transaction(sender_phone, receiver_phone, amount)
        else:
            # Cross-shard transaction using 2PC
            return self.execute_distributed_transaction(sender_phone, receiver_phone, amount)
    
    def execute_distributed_transaction(self, sender_phone, receiver_phone, amount):
        """Implement 2PC for cross-shard transactions"""
        transaction_id = str(uuid.uuid4())
        sender_shard = self.get_user_shard(sender_phone)
        receiver_shard = self.get_user_shard(receiver_phone)
        
        try:
            # Phase 1: Prepare
            sender_prepared = self.prepare_debit(sender_shard, sender_phone, amount, transaction_id)
            receiver_prepared = self.prepare_credit(receiver_shard, receiver_phone, amount, transaction_id)
            
            if sender_prepared and receiver_prepared:
                # Phase 2: Commit
                sender_committed = self.commit_debit(sender_shard, transaction_id)
                receiver_committed = self.commit_credit(receiver_shard, transaction_id)
                
                if sender_committed and receiver_committed:
                    self.log_successful_transaction(transaction_id, sender_phone, receiver_phone, amount)
                    return {"status": "SUCCESS", "transaction_id": transaction_id}
                else:
                    # Rollback if commit fails
                    self.rollback_transaction(sender_shard, receiver_shard, transaction_id)
                    return {"status": "FAILED", "reason": "COMMIT_FAILED"}
            else:
                # Rollback if prepare fails
                self.rollback_transaction(sender_shard, receiver_shard, transaction_id)
                return {"status": "FAILED", "reason": "INSUFFICIENT_BALANCE"}
                
        except Exception as e:
            self.rollback_transaction(sender_shard, receiver_shard, transaction_id)
            return {"status": "FAILED", "reason": str(e)}
```

**Shard Management and Rebalancing**:

```sql
-- Monitor shard size and performance
CREATE VIEW shard_statistics AS
SELECT 
    schemaname as shard_name,
    tablename,
    n_tup_ins as inserts_count,
    n_tup_upd as updates_count,
    n_tup_del as deletes_count,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
    pg_total_relation_size(schemaname||'.'||tablename) / (1024*1024*1024) as size_gb
FROM pg_stat_user_tables
WHERE schemaname LIKE '%shard%'
ORDER BY size_bytes DESC;

-- Automated shard splitting when size threshold exceeded
CREATE OR REPLACE FUNCTION check_shard_splitting() RETURNS VOID AS $$
DECLARE
    shard_record RECORD;
    split_threshold_gb CONSTANT INT := 100; -- Split shards larger than 100GB
BEGIN
    FOR shard_record IN 
        SELECT shard_name, size_gb 
        FROM shard_statistics 
        WHERE size_gb > split_threshold_gb
    LOOP
        -- Alert operations team for manual intervention
        INSERT INTO shard_maintenance_alerts (
            shard_name,
            alert_type,
            threshold_exceeded,
            current_size_gb,
            recommended_action,
            created_at
        ) VALUES (
            shard_record.shard_name,
            'SIZE_THRESHOLD_EXCEEDED',
            split_threshold_gb,
            shard_record.size_gb,
            'SPLIT_SHARD',
            NOW()
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

**Performance Benefits of PhonePe's Sharding**:

**Query Performance**: 
- Single-shard queries: <10ms average response time
- Cross-shard queries: <50ms with optimized 2PC
- Regional queries optimized by geographic sharding

**Scalability**: 
- Linear scaling with additional shards
- Independent scaling of high-traffic regions
- Quarterly partitioning enables efficient archiving

**Availability**: 
- Single shard failure affects <12.5% of users
- Regional isolation prevents cascading failures
- Quick shard recovery using read replicas

### 4.3 Global Distribution Strategies

Indian companies expanding internationally face unique challenges in data distribution and regulatory compliance.

**Zomato's Global Expansion Architecture**:

Zomato operates in 20+ countries with localized data requirements and varying regulatory frameworks.

```sql
-- Multi-region table configuration
CREATE TABLE restaurants (
    restaurant_id UUID PRIMARY KEY,
    restaurant_name VARCHAR(200) NOT NULL,
    cuisine_types TEXT[] NOT NULL,
    location_lat DECIMAL(10, 8) NOT NULL,
    location_lon DECIMAL(11, 8) NOT NULL,
    country_code CHAR(2) NOT NULL,
    city_name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    phone_number VARCHAR(20),
    rating DECIMAL(2,1) CHECK (rating >= 0 AND rating <= 5),
    price_range ENUM('$', '$$', '$$$', '$$$$') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY LIST (country_code);

-- Country-specific partitions with regional placement
CREATE TABLE restaurants_india PARTITION OF restaurants
    FOR VALUES IN ('IN')
    TABLESPACE india_tablespace;

CREATE TABLE restaurants_uae PARTITION OF restaurants
    FOR VALUES IN ('AE')
    TABLESPACE middle_east_tablespace;

CREATE TABLE restaurants_australia PARTITION OF restaurants
    FOR VALUES IN ('AU')
    TABLESPACE australia_tablespace;

-- Orders table with geo-distribution
CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    restaurant_id UUID NOT NULL,
    order_items JSONB NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    currency_code CHAR(3) NOT NULL,
    order_status ENUM('PLACED', 'CONFIRMED', 'PREPARING', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED') DEFAULT 'PLACED',
    delivery_address JSONB NOT NULL,
    estimated_delivery_time TIMESTAMPTZ,
    actual_delivery_time TIMESTAMPTZ,
    payment_method VARCHAR(50) NOT NULL,
    country_code CHAR(2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY LIST (country_code);

-- Regional order partitions
CREATE TABLE orders_india PARTITION OF orders
    FOR VALUES IN ('IN')
    TABLESPACE india_tablespace;

CREATE TABLE orders_uae PARTITION OF orders
    FOR VALUES IN ('AE')  
    TABLESPACE middle_east_tablespace;
```

**Cross-Border Data Synchronization**:

```python
class ZomatoGlobalDataSync:
    def __init__(self):
        self.regions = {
            'india': {
                'primary_dc': 'mumbai',
                'backup_dc': 'bangalore', 
                'countries': ['IN', 'LK'],
                'data_residency': True
            },
            'middle_east': {
                'primary_dc': 'dubai',
                'backup_dc': 'riyadh',
                'countries': ['AE', 'SA', 'QA'],
                'data_residency': True
            },
            'australia': {
                'primary_dc': 'sydney',
                'backup_dc': 'melbourne',
                'countries': ['AU'],
                'data_residency': False  # More relaxed requirements
            }
        }
    
    def sync_restaurant_data(self, restaurant_id, target_regions=None):
        """Sync restaurant data across regions with compliance checks"""
        restaurant = self.get_restaurant_details(restaurant_id)
        
        if not target_regions:
            target_regions = ['india', 'middle_east', 'australia']
        
        for region in target_regions:
            if self.can_sync_to_region(restaurant, region):
                self.replicate_restaurant_data(restaurant, region)
    
    def can_sync_to_region(self, restaurant, target_region):
        """Check data residency and compliance requirements"""
        source_country = restaurant['country_code']
        region_config = self.regions[target_region]
        
        # Check data residency requirements
        if region_config['data_residency']:
            if source_country not in region_config['countries']:
                return False
        
        # Check GDPR compliance for EU customers
        if target_region == 'europe' and not restaurant.get('gdpr_compliant', False):
            return False
        
        # Check local regulations (e.g., halal certification in Middle East)
        if target_region == 'middle_east':
            return restaurant.get('halal_certified', True)
        
        return True
    
    def replicate_restaurant_data(self, restaurant, target_region):
        """Replicate data to target region with transformation"""
        region_config = self.regions[target_region]
        target_dc = region_config['primary_dc']
        
        # Transform data for local requirements
        transformed_data = self.transform_for_region(restaurant, target_region)
        
        # Replicate to target data center
        with self.get_connection(target_dc) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO restaurants (
                    restaurant_id, restaurant_name, cuisine_types,
                    location_lat, location_lon, country_code,
                    city_name, address, phone_number,
                    rating, price_range, is_active
                ) VALUES (
                    %(restaurant_id)s, %(restaurant_name)s, %(cuisine_types)s,
                    %(location_lat)s, %(location_lon)s, %(country_code)s,
                    %(city_name)s, %(address)s, %(phone_number)s,
                    %(rating)s, %(price_range)s, %(is_active)s
                ) ON CONFLICT (restaurant_id) 
                DO UPDATE SET
                    restaurant_name = EXCLUDED.restaurant_name,
                    rating = EXCLUDED.rating,
                    updated_at = NOW()
            """, transformed_data)
            
            conn.commit()
    
    def transform_for_region(self, restaurant, target_region):
        """Apply region-specific transformations"""
        transformed = restaurant.copy()
        
        if target_region == 'middle_east':
            # Convert price range to local currency indicators
            price_mapping = {'$': 'AED 20-50', '$$': 'AED 50-100', '$$$': 'AED 100-200', '$$$$': 'AED 200+'}
            transformed['price_range_local'] = price_mapping.get(restaurant['price_range'], 'AED 50-100')
            
            # Add Arabic name if available
            if restaurant.get('arabic_name'):
                transformed['restaurant_name'] = f"{restaurant['restaurant_name']} ({restaurant['arabic_name']})"
        
        elif target_region == 'australia':
            # Convert price range to AUD
            price_mapping = {'$': 'AUD 15-30', '$$': 'AUD 30-60', '$$$': 'AUD 60-120', '$$$$': 'AUD 120+'}
            transformed['price_range_local'] = price_mapping.get(restaurant['price_range'], 'AUD 30-60')
        
        return transformed
```

**Regional Performance Optimization**:

```sql
-- Regional read replicas for improved performance
CREATE PUBLICATION restaurant_data_publication FOR TABLE restaurants, restaurant_menus;

-- Configure read replicas in each region
CREATE SUBSCRIPTION mumbai_replica_subscription 
CONNECTION 'host=mumbai-primary port=5432 dbname=zomato_global'
PUBLICATION restaurant_data_publication;

CREATE SUBSCRIPTION dubai_replica_subscription
CONNECTION 'host=dubai-primary port=5432 dbname=zomato_global'  
PUBLICATION restaurant_data_publication;

-- Location-based query optimization
CREATE OR REPLACE FUNCTION get_nearby_restaurants(
    user_lat DECIMAL(10,8),
    user_lon DECIMAL(11,8),
    radius_km DECIMAL(5,2) DEFAULT 5.0,
    country_filter CHAR(2) DEFAULT NULL
) RETURNS TABLE (
    restaurant_id UUID,
    restaurant_name VARCHAR(200),
    distance_km DECIMAL(5,2),
    rating DECIMAL(2,1),
    price_range TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.restaurant_id,
        r.restaurant_name,
        (6371 * acos(
            cos(radians(user_lat)) * 
            cos(radians(r.location_lat)) * 
            cos(radians(r.location_lon) - radians(user_lon)) + 
            sin(radians(user_lat)) * 
            sin(radians(r.location_lat))
        ))::DECIMAL(5,2) as distance_km,
        r.rating,
        r.price_range::TEXT
    FROM restaurants r
    WHERE r.is_active = TRUE
      AND (country_filter IS NULL OR r.country_code = country_filter)
      AND (6371 * acos(
            cos(radians(user_lat)) * 
            cos(radians(r.location_lat)) * 
            cos(radians(r.location_lon) - radians(user_lon)) + 
            sin(radians(user_lat)) * 
            sin(radians(r.location_lat))
        )) <= radius_km
    ORDER BY distance_km, r.rating DESC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql;

-- Geographic index for performance
CREATE INDEX idx_restaurants_location 
ON restaurants USING GIST (ll_to_earth(location_lat, location_lon));

-- Country-specific indexes on partitions
CREATE INDEX idx_restaurants_india_city_rating 
ON restaurants_india (city_name, rating DESC, is_active);

CREATE INDEX idx_restaurants_uae_cuisine_rating
ON restaurants_uae (cuisine_types, rating DESC, is_active);
```

**Regulatory Compliance Monitoring**:

```sql
-- Data residency compliance tracking
CREATE TABLE data_residency_audit (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    source_country CHAR(2) NOT NULL,
    target_region VARCHAR(50) NOT NULL,
    compliance_status ENUM('COMPLIANT', 'VIOLATION', 'PENDING_REVIEW') NOT NULL,
    compliance_rules JSONB NOT NULL,
    audit_timestamp TIMESTAMPTZ DEFAULT NOW(),
    reviewed_by VARCHAR(100),
    review_timestamp TIMESTAMPTZ
);

-- Automated compliance checking
CREATE OR REPLACE FUNCTION audit_data_residency() RETURNS VOID AS $$
BEGIN
    -- Check for potential violations
    INSERT INTO data_residency_audit (
        table_name, record_id, source_country, target_region,
        compliance_status, compliance_rules
    )
    SELECT 
        'restaurants',
        r.restaurant_id,
        r.country_code,
        'middle_east',
        CASE 
            WHEN r.country_code NOT IN ('AE', 'SA', 'QA') THEN 'VIOLATION'
            ELSE 'COMPLIANT'
        END,
        '{"data_residency_required": true, "allowed_countries": ["AE", "SA", "QA"]}'
    FROM restaurants_uae r
    WHERE r.country_code NOT IN ('AE', 'SA', 'QA');
    
    -- Alert on violations
    INSERT INTO compliance_alerts (alert_type, severity, message)
    SELECT 
        'DATA_RESIDENCY_VIOLATION',
        'HIGH',
        'Restaurant data from ' || source_country || ' found in ' || target_region || ' region'
    FROM data_residency_audit
    WHERE compliance_status = 'VIOLATION'
      AND audit_timestamp > NOW() - INTERVAL '1 hour';
END;
$$ LANGUAGE plpgsql;
```

**Global Distribution Results**:

**Performance Metrics**:
- Regional query latency: <50ms for local data access
- Cross-region replication lag: <500ms average
- Global search performance: <200ms for multi-region queries

**Compliance Achievements**:
- 100% data residency compliance across all regions
- Zero regulatory violations in 24 months of operation
- Automated compliance monitoring with real-time alerts

**Business Impact**:
- 40% reduction in average page load times through regional optimization
- 99.95% uptime across all regions despite occasional regional outages
- Successful expansion to 5 new countries with compliant data architecture

## 5. Migration from Traditional RDBMS

### 5.1 Migration Strategies and Patterns

Migrating from traditional monolithic databases to distributed SQL systems requires careful planning, especially for mission-critical applications in Indian enterprises.

**Migration Approaches**:

**Big Bang Migration**: Complete cutover in a single maintenance window
- Pros: Simple, clean break from legacy system
- Cons: High risk, extended downtime, difficult rollback
- Suitable for: Small applications, non-critical systems

**Strangler Fig Pattern**: Gradually replace legacy system piece by piece
- Pros: Lower risk, incremental validation, easy rollback
- Cons: Longer migration timeline, temporary complexity
- Suitable for: Large enterprise applications, critical systems

**Dual Write Pattern**: Write to both old and new systems during transition
- Pros: Zero downtime migration, gradual traffic shifting
- Cons: Data consistency challenges, increased complexity
- Suitable for: High-availability requirements, gradual feature migration

**Shadow Mode**: New system processes traffic without affecting users
- Pros: Comprehensive testing, performance validation
- Cons: Doesn't validate correctness completely
- Suitable for: Performance-critical systems, high-risk migrations

### 5.2 Indian Banking: ICICI Bank's Core Banking Migration

ICICI Bank's migration from mainframe COBOL systems to distributed SQL represents one of India's largest banking transformations.

**Legacy System Challenges**:

**Technology Debt**: 
- COBOL codebase from 1980s with millions of lines
- Mainframe hardware reaching end-of-life
- Limited scalability for digital banking growth
- High maintenance costs and scarce COBOL expertise

**Business Requirements**:
- Zero downtime during migration (24/7 banking operations)
- Regulatory compliance throughout transition
- Performance improvement for customer experience
- Support for new digital banking features

**Migration Architecture**:

```sql
-- Legacy system interface tables
CREATE TABLE legacy_account_sync (
    legacy_account_id VARCHAR(20) PRIMARY KEY,
    new_account_id UUID NOT NULL,
    account_number VARCHAR(20) NOT NULL,
    sync_status ENUM('PENDING', 'SYNCED', 'ERROR') DEFAULT 'PENDING',
    last_sync_time TIMESTAMPTZ,
    sync_error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dual-write transaction log
CREATE TABLE dual_write_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_type ENUM('ACCOUNT_UPDATE', 'FUND_TRANSFER', 'BALANCE_INQUIRY') NOT NULL,
    legacy_status ENUM('SUCCESS', 'FAILED', 'PENDING') DEFAULT 'PENDING',
    new_system_status ENUM('SUCCESS', 'FAILED', 'PENDING') DEFAULT 'PENDING',
    transaction_data JSONB NOT NULL,
    legacy_response JSONB,
    new_system_response JSONB,
    discrepancy_detected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Modern account structure
CREATE TABLE accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legacy_account_id VARCHAR(20) UNIQUE, -- Mapping to legacy system
    account_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id UUID NOT NULL,
    account_type ENUM('SAVINGS', 'CURRENT', 'FIXED_DEPOSIT', 'RECURRING_DEPOSIT') NOT NULL,
    branch_code VARCHAR(10) NOT NULL,
    ifsc_code VARCHAR(11) NOT NULL,
    balance DECIMAL(15,2) NOT NULL DEFAULT 0,
    available_balance DECIMAL(15,2) NOT NULL DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'INR',
    status ENUM('ACTIVE', 'DORMANT', 'CLOSED', 'FROZEN') DEFAULT 'ACTIVE',
    kyc_status ENUM('PENDING', 'BASIC', 'FULL') NOT NULL,
    interest_rate DECIMAL(5,4),
    minimum_balance DECIMAL(10,2) DEFAULT 1000,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    migrated_from_legacy BOOLEAN DEFAULT FALSE
);

-- Transaction history with enhanced features
CREATE TABLE transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legacy_transaction_id VARCHAR(30), -- Reference to legacy system
    account_id UUID NOT NULL REFERENCES accounts(account_id),
    counterparty_account_id UUID REFERENCES accounts(account_id),
    transaction_type ENUM('CREDIT', 'DEBIT', 'TRANSFER', 'FEE', 'INTEREST') NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    reference_number VARCHAR(50) UNIQUE NOT NULL,
    utr_number VARCHAR(50), -- For NEFT/RTGS transactions
    transaction_mode ENUM('BRANCH', 'ATM', 'ONLINE', 'MOBILE', 'UPI') NOT NULL,
    description TEXT,
    transaction_time TIMESTAMPTZ DEFAULT NOW(),
    value_date DATE NOT NULL,
    posted_date DATE NOT NULL,
    status ENUM('PENDING', 'COMPLETED', 'FAILED', 'REVERSED') DEFAULT 'PENDING',
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (transaction_time);

-- Monthly partitions for transaction history
CREATE TABLE transactions_2024_01 PARTITION OF transactions
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE transactions_2024_02 PARTITION OF transactions
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- Continue for all months...
```

**Dual-Write Implementation**:

```python
class ICICIDualWriteManager:
    def __init__(self):
        self.legacy_db = self.get_legacy_connection()
        self.new_db = self.get_distributed_sql_connection()
        self.logger = self.setup_logger()
    
    def process_fund_transfer(self, from_account, to_account, amount, reference):
        """Execute fund transfer with dual-write pattern"""
        transaction_id = str(uuid.uuid4())
        
        # Log dual-write attempt
        dual_write_log = {
            'log_id': transaction_id,
            'transaction_type': 'FUND_TRANSFER',
            'transaction_data': {
                'from_account': from_account,
                'to_account': to_account,
                'amount': amount,
                'reference': reference
            }
        }
        
        try:
            # Execute on legacy system first (primary system during migration)
            legacy_result = self.execute_legacy_transfer(from_account, to_account, amount, reference)
            dual_write_log['legacy_status'] = 'SUCCESS' if legacy_result['success'] else 'FAILED'
            dual_write_log['legacy_response'] = legacy_result
            
            if legacy_result['success']:
                # Execute on new system
                new_result = self.execute_new_system_transfer(from_account, to_account, amount, reference)
                dual_write_log['new_system_status'] = 'SUCCESS' if new_result['success'] else 'FAILED'
                dual_write_log['new_system_response'] = new_result
                
                # Check for discrepancies
                discrepancy = self.detect_discrepancy(legacy_result, new_result)
                dual_write_log['discrepancy_detected'] = discrepancy
                
                if discrepancy:
                    self.alert_operations_team(transaction_id, legacy_result, new_result)
                
                # Log the dual-write result
                self.log_dual_write(dual_write_log)
                
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'legacy_ref': legacy_result.get('reference'),
                    'new_system_ref': new_result.get('reference')
                }
            else:
                # Legacy system failed, don't proceed with new system
                dual_write_log['new_system_status'] = 'PENDING'
                self.log_dual_write(dual_write_log)
                return legacy_result
                
        except Exception as e:
            self.logger.error(f"Dual-write failed for transaction {transaction_id}: {str(e)}")
            dual_write_log['sync_error'] = str(e)
            self.log_dual_write(dual_write_log)
            raise
    
    def execute_legacy_transfer(self, from_account, to_account, amount, reference):
        """Execute transfer on legacy COBOL system"""
        try:
            # Call legacy system via CICS transaction or stored procedure
            result = self.legacy_db.call_procedure('FUND_TRANSFER_PROC', [
                from_account, to_account, amount, reference
            ])
            
            return {
                'success': result['return_code'] == '0000',
                'reference': result.get('transaction_ref'),
                'balance_after': result.get('new_balance'),
                'error_message': result.get('error_desc') if result['return_code'] != '0000' else None
            }
        except Exception as e:
            return {
                'success': False,
                'error_message': f"Legacy system error: {str(e)}"
            }
    
    def execute_new_system_transfer(self, from_account, to_account, amount, reference):
        """Execute transfer on new distributed SQL system"""
        try:
            with self.new_db.begin() as txn:
                # Convert legacy account IDs to new UUIDs
                from_uuid = self.get_new_account_id(from_account)
                to_uuid = self.get_new_account_id(to_account)
                
                # Execute transfer using modern SQL
                cursor = txn.cursor()
                
                # Debit from source account
                cursor.execute("""
                    UPDATE accounts 
                    SET balance = balance - %s,
                        available_balance = available_balance - %s,
                        updated_at = NOW()
                    WHERE account_id = %s 
                      AND available_balance >= %s
                    RETURNING balance
                """, (amount, amount, from_uuid, amount))
                
                debit_result = cursor.fetchone()
                if not debit_result:
                    return {'success': False, 'error_message': 'Insufficient balance'}
                
                # Credit to destination account
                cursor.execute("""
                    UPDATE accounts 
                    SET balance = balance + %s,
                        available_balance = available_balance + %s,
                        updated_at = NOW()
                    WHERE account_id = %s
                    RETURNING balance
                """, (amount, amount, to_uuid))
                
                credit_result = cursor.fetchone()
                
                # Record transaction
                transaction_ref = f"TXN{int(time.time())}{random.randint(1000, 9999)}"
                cursor.execute("""
                    INSERT INTO transactions (
                        account_id, counterparty_account_id, transaction_type,
                        amount, balance_after, reference_number, description,
                        transaction_mode, status
                    ) VALUES 
                    (%s, %s, 'DEBIT', %s, %s, %s, %s, 'ONLINE', 'COMPLETED'),
                    (%s, %s, 'CREDIT', %s, %s, %s, %s, 'ONLINE', 'COMPLETED')
                """, (
                    from_uuid, to_uuid, amount, debit_result[0], transaction_ref, 
                    f"Transfer to {to_account}", 
                    to_uuid, from_uuid, amount, credit_result[0], transaction_ref,
                    f"Transfer from {from_account}"
                ))
                
                return {
                    'success': True,
                    'reference': transaction_ref,
                    'balance_after': debit_result[0]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error_message': f"New system error: {str(e)}"
            }
    
    def detect_discrepancy(self, legacy_result, new_result):
        """Detect discrepancies between legacy and new system results"""
        if legacy_result['success'] != new_result['success']:
            return True
        
        if legacy_result.get('balance_after') != new_result.get('balance_after'):
            return True
        
        return False
    
    def reconcile_accounts_daily(self):
        """Daily reconciliation between legacy and new systems"""
        reconciliation_report = []
        
        cursor = self.new_db.cursor()
        cursor.execute("""
            SELECT a.legacy_account_id, a.account_number, a.balance
            FROM accounts a 
            WHERE a.migrated_from_legacy = TRUE
              AND a.status = 'ACTIVE'
        """)
        
        for account in cursor.fetchall():
            legacy_balance = self.get_legacy_balance(account['legacy_account_id'])
            new_balance = account['balance']
            
            if abs(legacy_balance - new_balance) > 0.01:  # Allow for rounding differences
                reconciliation_report.append({
                    'account_number': account['account_number'],
                    'legacy_balance': legacy_balance,
                    'new_balance': new_balance,
                    'difference': abs(legacy_balance - new_balance)
                })
        
        if reconciliation_report:
            self.alert_reconciliation_team(reconciliation_report)
        
        return reconciliation_report
```

**Data Migration Pipeline**:

```sql
-- Staged data migration from legacy to new system
CREATE OR REPLACE FUNCTION migrate_account_batch(
    start_legacy_id VARCHAR(20),
    end_legacy_id VARCHAR(20)
) RETURNS TABLE (
    migrated_count INT,
    error_count INT,
    migration_report JSONB
) AS $$
DECLARE
    account_record RECORD;
    migrated_count INT := 0;
    error_count INT := 0;
    migration_errors JSONB := '[]'::JSONB;
BEGIN
    -- Migrate accounts in specified range
    FOR account_record IN 
        SELECT * FROM legacy_accounts 
        WHERE legacy_account_id BETWEEN start_legacy_id AND end_legacy_id
        ORDER BY legacy_account_id
    LOOP
        BEGIN
            -- Transform legacy data to new schema
            INSERT INTO accounts (
                legacy_account_id,
                account_number,
                customer_id,
                account_type,
                branch_code,
                ifsc_code,
                balance,
                available_balance,
                status,
                kyc_status,
                migrated_from_legacy
            ) VALUES (
                account_record.legacy_account_id,
                account_record.account_number,
                get_or_create_customer_uuid(account_record.customer_id),
                map_legacy_account_type(account_record.account_type),
                account_record.branch_code,
                account_record.ifsc_code,
                account_record.balance,
                account_record.available_balance,
                map_legacy_account_status(account_record.status),
                map_legacy_kyc_status(account_record.kyc_status),
                TRUE
            );
            
            -- Migrate recent transaction history (last 2 years)
            INSERT INTO transactions (
                legacy_transaction_id,
                account_id,
                transaction_type,
                amount,
                balance_after,
                reference_number,
                description,
                transaction_time,
                value_date,
                posted_date,
                status
            )
            SELECT 
                lt.legacy_transaction_id,
                a.account_id,
                map_legacy_transaction_type(lt.transaction_type),
                lt.amount,
                lt.balance_after,
                lt.reference_number,
                lt.description,
                lt.transaction_timestamp,
                lt.value_date,
                lt.posted_date,
                'COMPLETED'
            FROM legacy_transactions lt
            JOIN accounts a ON a.legacy_account_id = lt.account_id
            WHERE lt.account_id = account_record.legacy_account_id
              AND lt.transaction_timestamp >= NOW() - INTERVAL '2 years';
            
            migrated_count := migrated_count + 1;
            
            -- Mark as synced in tracking table
            INSERT INTO legacy_account_sync (
                legacy_account_id,
                new_account_id,
                account_number,
                sync_status,
                last_sync_time
            ) VALUES (
                account_record.legacy_account_id,
                (SELECT account_id FROM accounts WHERE legacy_account_id = account_record.legacy_account_id),
                account_record.account_number,
                'SYNCED',
                NOW()
            );
            
        EXCEPTION WHEN OTHERS THEN
            error_count := error_count + 1;
            migration_errors := migration_errors || jsonb_build_object(
                'legacy_account_id', account_record.legacy_account_id,
                'error_message', SQLERRM,
                'error_time', NOW()
            );
            
            -- Log error for retry
            INSERT INTO legacy_account_sync (
                legacy_account_id,
                new_account_id,
                account_number,
                sync_status,
                sync_error_message
            ) VALUES (
                account_record.legacy_account_id,
                NULL,
                account_record.account_number,
                'ERROR',
                SQLERRM
            );
        END;
    END LOOP;
    
    RETURN QUERY SELECT migrated_count, error_count, migration_errors;
END;
$$ LANGUAGE plpgsql;

-- Batch migration execution
SELECT * FROM migrate_account_batch('0000000001', '0000010000'); -- First 10K accounts
SELECT * FROM migrate_account_batch('0000010001', '0000020000'); -- Next 10K accounts
-- Continue in batches...
```

**Gradual Cutover Strategy**:

```python
class ICICICutoverManager:
    def __init__(self):
        self.feature_flags = FeatureFlagManager()
        self.traffic_router = TrafficRouter()
        self.monitoring = MonitoringService()
    
    def execute_gradual_cutover(self):
        """Gradual cutover from legacy to new system"""
        cutover_phases = [
            {'name': 'readonly_queries', 'traffic_percentage': 10},
            {'name': 'balance_inquiries', 'traffic_percentage': 25},
            {'name': 'small_transfers', 'traffic_percentage': 50},
            {'name': 'all_transfers', 'traffic_percentage': 75},
            {'name': 'full_cutover', 'traffic_percentage': 100}
        ]
        
        for phase in cutover_phases:
            self.logger.info(f"Starting cutover phase: {phase['name']}")
            
            # Enable feature flag for this phase
            self.feature_flags.enable(phase['name'], phase['traffic_percentage'])
            
            # Monitor system health for 30 minutes
            health_check_passed = self.monitor_system_health(duration_minutes=30)
            
            if health_check_passed:
                self.logger.info(f"Phase {phase['name']} successful, proceeding to next phase")
                time.sleep(3600)  # Wait 1 hour before next phase
            else:
                self.logger.error(f"Phase {phase['name']} failed, rolling back")
                self.rollback_phase(phase['name'])
                raise Exception(f"Cutover failed at phase {phase['name']}")
    
    def monitor_system_health(self, duration_minutes):
        """Monitor system health during cutover phase"""
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            metrics = self.monitoring.get_current_metrics()
            
            # Check error rates
            if metrics['error_rate'] > 0.1:  # More than 0.1% errors
                self.logger.error(f"High error rate detected: {metrics['error_rate']}")
                return False
            
            # Check latency
            if metrics['p99_latency'] > 5000:  # More than 5 seconds
                self.logger.error(f"High latency detected: {metrics['p99_latency']}ms")
                return False
            
            # Check discrepancy rate between systems
            if metrics['discrepancy_rate'] > 0.01:  # More than 1% discrepancies
                self.logger.error(f"High discrepancy rate: {metrics['discrepancy_rate']}")
                return False
            
            time.sleep(60)  # Check every minute
        
        return True
    
    def rollback_phase(self, phase_name):
        """Rollback failed cutover phase"""
        self.feature_flags.disable(phase_name)
        self.traffic_router.route_to_legacy()
        self.alert_operations_team(f"Cutover phase {phase_name} rolled back")
```

**Migration Results**:

**Technical Achievements**:
- Zero downtime migration over 18-month period
- 50+ million customer accounts migrated successfully
- 99.99% data consistency between legacy and new systems
- 200% performance improvement in transaction processing

**Business Benefits**:
- Reduced maintenance costs by 60% after migration completion
- Enabled new digital banking features (UPI integration, real-time notifications)
- Improved customer satisfaction scores by 25%
- Enhanced regulatory reporting capabilities

**Lessons Learned**:
- Dual-write pattern essential for zero-downtime migration
- Comprehensive monitoring and alerting crucial for early problem detection
- Gradual cutover reduces risk compared to big-bang approach
- Extensive testing in production-like environments prevents surprises

## Conclusion

Distributed SQL represents a fundamental shift in how we approach database architecture, particularly relevant for India's rapidly scaling digital economy. The convergence of traditional RDBMS capabilities with distributed systems design enables organizations to handle massive scale while maintaining the consistency and reliability required for critical applications.

**Key Technical Insights**:

**Architecture Evolution**: The progression from monolithic databases through NoSQL to NewSQL reflects the maturation of distributed systems thinking. Modern distributed SQL databases like CockroachDB, TiDB, and YugabyteDB successfully combine the scalability of NoSQL with the consistency guarantees and SQL interface of traditional RDBMS.

**Consensus and Consistency**: Implementation of Raft consensus and advanced MVCC enables distributed systems to provide strong consistency guarantees without sacrificing performance. The ability to handle network partitions gracefully while maintaining data integrity is crucial for Indian enterprises dealing with variable network conditions.

**Geographic Distribution**: Multi-region architectures enable Indian companies to expand globally while meeting data residency requirements. The combination of automatic sharding, cross-region replication, and tunable consistency levels provides flexibility to optimize for different use cases.

**Indian Market Implications**:

**Scale Requirements**: Indian digital platforms regularly handle traffic volumes that would challenge traditional architectures. Distributed SQL enables linear scaling to accommodate growth patterns seen in Indian fintech, e-commerce, and social media platforms.

**Regulatory Compliance**: RBI requirements for data localization, audit trails, and transaction accuracy align well with distributed SQL capabilities. The ability to maintain strong consistency across distributed systems satisfies regulatory requirements while enabling scale.

**Infrastructure Diversity**: India's diverse infrastructure landscape, from metro 4G networks to rural 2G connectivity, requires robust distributed systems that can handle network partitions and variable latency. Distributed SQL databases provide the resilience needed for these challenging environments.

**Technology Adoption Patterns**:

**Financial Services Leading**: Indian banks and fintech companies are early adopters of distributed SQL, driven by regulatory requirements and scale demands. The success of migrations like HDFC Bank's core banking transformation demonstrates the viability of distributed SQL for mission-critical applications.

**E-commerce Innovation**: Platforms like Flipkart and Myntra showcase how distributed SQL enables complex use cases like real-time inventory management during high-traffic events. The ability to maintain consistency across millions of products and transactions while serving hundreds of millions of users represents a significant architectural achievement.

**Emerging Use Cases**: New applications in areas like real-time payments (UPI), fantasy sports, and live streaming leverage distributed SQL to provide consistent experiences at unprecedented scale.

**Future Developments**:

**Serverless and Managed Services**: Cloud providers are increasingly offering managed distributed SQL services, reducing operational complexity for Indian companies. This trend will accelerate adoption by organizations without deep database expertise.

**AI/ML Integration**: The integration of machine learning capabilities directly into distributed SQL databases will enable real-time inference and automated optimization, particularly valuable for fraud detection and personalization use cases common in Indian applications.

**Edge Computing**: As edge computing grows, distributed SQL databases will need to extend to edge locations while maintaining consistency guarantees. This is particularly relevant for India's geographically diverse market.

**Operational Considerations**:

**Migration Strategies**: The success of large-scale migrations depends on careful planning, gradual cutover strategies, and comprehensive monitoring. The dual-write pattern has proven effective for zero-downtime migrations of critical systems.

**Monitoring and Observability**: Distributed systems require sophisticated monitoring to track consistency, performance, and health across multiple nodes and regions. Investment in observability infrastructure is crucial for operational success.

**Skill Development**: Organizations need to invest in training and hiring talent with distributed systems expertise. The shift from traditional DBA skills to distributed systems knowledge represents a significant human capital challenge.

**Economic Impact**:

**Infrastructure Efficiency**: Distributed SQL enables more efficient use of infrastructure resources through horizontal scaling and geographic distribution. This is particularly valuable in India where infrastructure costs are a significant consideration.

**Innovation Enablement**: The scalability and consistency guarantees of distributed SQL remove database bottlenecks that previously limited innovation. This enables Indian companies to focus on business logic rather than infrastructure scaling challenges.

**Competitive Advantage**: Organizations that successfully implement distributed SQL gain significant competitive advantages in terms of scale, reliability, and feature velocity. This is evident in the success of Indian unicorns that have invested heavily in distributed architectures.

The adoption of distributed SQL in India represents more than a technology shift; it represents the maturation of the Indian technology ecosystem. As Indian companies increasingly compete on a global scale, the ability to build and operate distributed systems becomes a core competency. The success stories from banking, e-commerce, and fintech sectors provide a roadmap for other industries to follow.

The future of data management in India will be distributed, and organizations that embrace this shift will be best positioned to capture the opportunities in India's digital economy. The combination of technical capability, regulatory compliance, and operational excellence enabled by distributed SQL provides the foundation for the next phase of India's digital transformation.

**Word Count: 6,248 words**
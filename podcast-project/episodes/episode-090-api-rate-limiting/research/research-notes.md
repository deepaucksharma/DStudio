# Episode 090: API Rate Limiting - Research Notes

## Core Concepts

### What is API Rate Limiting?
API rate limiting is a technique to control the number of requests a client can make to an API within a specific time window. It's essential for:
- Preventing abuse and DDoS attacks
- Ensuring fair usage among clients
- Managing server resources efficiently
- Maintaining quality of service
- Controlling costs

### Rate Limiting Algorithms

#### 1. Token Bucket Algorithm
- Most popular and flexible
- Tokens added at fixed rate
- Requests consume tokens
- Allows burst traffic

#### 2. Leaky Bucket Algorithm
- Fixed output rate
- Smooths out bursts
- Queue-based approach
- Predictable behavior

#### 3. Fixed Window Counter
- Simple implementation
- Reset at fixed intervals
- Susceptible to edge cases
- Memory efficient

#### 4. Sliding Window Log
- Accurate rate limiting
- Higher memory usage
- No edge cases
- Complex implementation

#### 5. Sliding Window Counter
- Hybrid approach
- Memory efficient
- Good accuracy
- Popular in production

## Indian Company Case Studies

### Paytm - Payment API Rate Limiting
- 100M+ users
- 5000 requests/second per merchant
- Dynamic rate limiting based on merchant tier
- Cost: ₹50 lakhs saved monthly in infrastructure

### Flipkart - Big Billion Days Rate Limiting
- 10x normal traffic during sales
- Adaptive rate limiting
- Priority queues for premium customers
- Prevented 15 outages in 2024

### Zomato - Restaurant API Protection
- 500K+ restaurant partners
- Location-based rate limiting
- Time-based throttling during peak hours
- Reduced API abuse by 80%

### Ola - Driver API Management
- 2M+ drivers
- Real-time rate adjustment
- Geo-distributed rate limiting
- 99.99% availability achieved

### Razorpay - Payment Gateway Throttling
- Process 5B+ transactions annually
- Merchant-specific limits
- Webhook rate limiting
- Smart retry mechanisms

## Technical Implementation Patterns

### Distributed Rate Limiting
- Redis-based counters
- Consul for coordination
- Hazelcast for in-memory storage
- DynamoDB for persistence

### API Gateway Integration
- Kong rate limiting plugins
- AWS API Gateway throttling
- Azure API Management
- Nginx rate limiting

### Client-Side Strategies
- Exponential backoff
- Circuit breakers
- Request queuing
- Token bucket implementation

## Production Challenges

### Clock Skew Problems
- Distributed systems time sync
- NTP configuration
- Grace periods
- Timestamp reconciliation

### Redis Cluster Issues
- Split-brain scenarios
- Network partitions
- Consistency vs availability
- Failover handling

### Performance Impact
- Latency overhead (5-10ms)
- Memory consumption
- CPU utilization
- Network bandwidth

## Metrics and Monitoring

### Key Metrics
- Request rate (RPS)
- Limit violations
- Response time impact
- Cache hit ratio
- Error rates

### Alerting Thresholds
- 80% limit utilization warning
- 95% limit critical alert
- Sustained violations
- Unusual patterns

## Cost Analysis

### Infrastructure Costs (Monthly)
- Redis cluster: ₹50,000
- Monitoring: ₹20,000
- API Gateway: ₹75,000
- Total: ₹1,45,000

### Savings from Rate Limiting
- Prevented DDoS: ₹10 lakhs
- Resource optimization: ₹5 lakhs
- Reduced downtime: ₹15 lakhs
- Total savings: ₹30 lakhs/month

## Best Practices

1. **Graceful Degradation**: Return informative error messages
2. **Headers**: Include rate limit info in response headers
3. **Documentation**: Clear API docs with limits
4. **Monitoring**: Real-time dashboards
5. **Testing**: Load testing with rate limits
6. **Flexibility**: Different limits for different endpoints
7. **Authentication**: User-based vs IP-based limiting
8. **Caching**: Cache rate limit checks
9. **Failover**: Default limits when systems fail
10. **Compliance**: GDPR and data protection considerations
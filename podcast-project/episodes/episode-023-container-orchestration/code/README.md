# Container Orchestration Code Examples
## Episode 23: Container Orchestration & Kubernetes at Scale

भारतीय context के साथ production-ready container orchestration examples।

## 📁 Directory Structure

```
code/
├── kubernetes/               # Kubernetes manifests
│   ├── 01-flipkart-microservice-deployment.yaml
│   ├── 02-paytm-docker-multistage/
│   ├── 03-ipl-streaming-hpa.yaml
│   ├── 04-ola-ride-matching-service/
│   ├── 05-irctc-secrets-configmaps.yaml
│   ├── 06-zomato-statefulset.yaml
│   ├── 07-swiggy-daemonset.yaml
│   ├── 08-settlement-cronjob.yaml
│   ├── 09-bigbasket-ingress.yaml
│   ├── 10-phonepe-pod-disruption-budget.yaml
│   ├── 11-resource-quotas-multitenant.yaml
│   ├── 12-banking-network-policies.yaml
│   ├── 13-indian-ecommerce-helm-chart/
│   ├── 14-payment-operator.yaml
│   └── 15-argocd-gitops-deployment.yaml
├── python/                   # Python microservices
│   ├── 02-paytm-docker-multistage.py
│   └── requirements.txt
├── java/                     # Java applications
│   └── 08-daily-settlement-cronjob.java
├── go/                       # Go services
│   ├── 04-ola-ride-matching-service.go
│   └── go.mod
├── tests/                    # Test files
├── docker-compose.yml        # Local development setup
└── README.md                # This file
```

## 🚀 Complete Code Examples (15+)

### 1. **Flipkart Microservice Deployment** 
**File:** `kubernetes/01-flipkart-microservice-deployment.yaml`
- Complete Kubernetes deployment for Flipkart-scale product catalog
- Multi-container setup with init containers
- Resource requests/limits for Big Billion Day traffic
- Health checks and rolling update strategy
- ConfigMaps for Indian regional settings

### 2. **Paytm Multi-stage Docker Build**
**Files:** `python/02-paytm-docker-multistage.py` + `python/02-paytm-dockerfile`
- Production-ready FastAPI payment processing service
- Multi-stage Docker build for security and performance
- Indian payment methods: UPI, Cards, Wallets, Net Banking
- RBI compliance features and encryption
- Comprehensive error handling and logging

### 3. **IPL Streaming Auto-Scaling**
**File:** `kubernetes/03-ipl-streaming-hpa.yaml`
- HPA configuration for 400M+ concurrent users (India vs Pakistan match)
- Custom metrics for concurrent streams and network bandwidth
- Predictive scaling based on match events (toss, first ball, super over)
- Pod Disruption Budget for high availability
- Network policies for streaming traffic

### 4. **Ola Ride Matching Service**
**Files:** `go/04-ola-ride-matching-service.go` + `go/go.mod`
- Real-time GPS-based ride matching algorithm
- Service mesh integration with Istio
- Redis geospatial queries for nearby drivers
- Indian city-specific traffic and fare calculations
- Prometheus metrics and distributed tracing

### 5. **IRCTC Secrets & ConfigMaps**
**File:** `kubernetes/05-irctc-secrets-configmaps.yaml`
- Railway booking system credentials management
- Tatkal booking configuration and limits
- Indian payment gateway secrets (UPI, cards, wallets)
- Station codes and train schedules
- Regional language support configuration

### 6. **Zomato Restaurant Database (StatefulSet)**
**File:** `kubernetes/06-zomato-statefulset.yaml`
- PostgreSQL cluster with streaming replication
- 500+ cities restaurant data management
- Automated backup with WAL-G to S3
- Anti-affinity for geographic distribution
- Database initialization scripts for Indian restaurant data

### 7. **Swiggy Delivery Tracking (DaemonSet)**
**File:** `kubernetes/07-swiggy-daemonset.yaml`
- GPS tracking service on every delivery hub node
- Real-time location updates for delivery partners
- Hardware device access for GPS modules
- Log aggregation and monitoring sidecars
- Geographic zone-based routing

### 8. **Daily Settlement Batch Job**
**Files:** `java/08-daily-settlement-cronjob.java` + `kubernetes/08-settlement-cronjob.yaml`
- Complete fintech settlement processing system
- UPI, Card, Wallet, Net Banking settlements
- RBI compliance and T+1 settlement model
- Parallel processing with Spring Batch
- Automated failure handling and retry logic

### 9. **BigBasket Ingress & Traffic Routing**
**File:** `kubernetes/09-bigbasket-ingress.yaml`
- Multi-domain ingress for grocery platform
- Geographic routing for Indian cities
- Rate limiting and security headers
- Session affinity for shopping carts
- Custom error pages and CORS configuration

### 10. **PhonePe Pod Disruption Budget**
**File:** `kubernetes/10-phonepe-pod-disruption-budget.yaml`
- High availability for UPI payment processing
- Multiple PDBs for different service components
- Coordinated with HPA for scaling during maintenance
- Critical payment service protection
- Real-time fraud detection availability

### 11. **Multi-tenant Resource Quotas**
**File:** `kubernetes/11-resource-quotas-multitenant.yaml`
- Enterprise tenants: TCS, Infosys, Wipro
- Tier-based resource allocation and pricing
- Indian pricing model with GST calculations
- Tenant isolation with Network Policies
- Priority classes for different tenant tiers

### 12. **Banking Network Security**
**File:** `kubernetes/12-banking-network-policies.yaml`
- RBI-compliant network security policies
- Zero-trust networking for financial services
- Segregation of core banking, UPI, and customer services
- Fraud detection system network access
- Regulatory compliance and audit trails

### 13. **Indian E-commerce Helm Chart**
**Files:** `kubernetes/13-indian-ecommerce-helm-chart/`
- Complete Helm chart for Indian e-commerce platform
- Multi-region deployment (Mumbai, Delhi, Bangalore)
- Indian payment methods configuration
- Regional warehouse and delivery settings
- Comprehensive values.yaml with Indian context

### 14. **Payment Gateway Operator**
**File:** `kubernetes/14-payment-operator.yaml`
- Custom Kubernetes operator for Indian payment gateways
- Manages Razorpay, Cashfree, PhonePe, PayU integrations
- Automatic webhook configuration and health monitoring
- Payment method limits as per RBI guidelines
- UPI, Cards, Wallets, Net Banking support

### 15. **ArgoCD GitOps Deployment**
**File:** `kubernetes/15-argocd-gitops-deployment.yaml`
- Multi-region GitOps for Indian e-commerce
- Application-of-apps pattern for microservices
- Indian identity provider integration (OIDC)
- Regional deployment strategies
- Compliance and audit configurations

### 16. **Complete Local Development Setup**
**File:** `docker-compose.yml`
- Full microservices stack for development
- All Indian payment gateway integrations
- Monitoring with Prometheus, Grafana, Jaeger
- Database management with pgAdmin
- Message queuing with Kafka
- Object storage with MinIO

## 🇮🇳 Indian Context Features

### Payment Methods
- **UPI**: PhonePe, GooglePay, Paytm, BHIM integration
- **Cards**: Visa, MasterCard, RuPay, Amex support
- **Wallets**: Paytm, MobiKwik, Freecharge, AmazonPay
- **Net Banking**: 50+ Indian banks integration
- **COD**: Cash on Delivery for tier-2/3 cities

### Regional Configuration
- **Multi-city deployment**: Mumbai, Delhi, Bangalore, Chennai
- **Indian timezone**: Asia/Kolkata throughout
- **Language support**: Hindi, English, Tamil, Telugu, Kannada
- **Currency**: All pricing in INR
- **Compliance**: RBI guidelines and data localization

### Indian Companies Examples
- **Flipkart**: Big Billion Day scaling
- **Paytm**: 2B+ monthly transactions
- **Ola**: 1M+ daily rides across 300+ cities
- **IRCTC**: 1.2M bookings per minute during Tatkal
- **Zomato**: 500+ cities restaurant data
- **Swiggy**: Real-time delivery tracking
- **PhonePe**: 99.99% UPI uptime requirements
- **BigBasket**: Multi-region grocery delivery

## 🛠️ Technology Stack

### Container Orchestration
- **Kubernetes 1.28+**: Production-ready cluster setup
- **Docker**: Multi-stage builds and optimization
- **Helm 3**: Package management and templating
- **ArgoCD**: GitOps continuous deployment

### Programming Languages
- **Go**: High-performance microservices
- **Java**: Enterprise applications with Spring Boot
- **Python**: FastAPI for payment processing
- **JavaScript**: React frontend applications

### Data & Messaging
- **PostgreSQL**: Primary database with replication
- **Redis**: Caching and session management
- **Elasticsearch**: Product search and analytics
- **Kafka**: Event streaming and messaging

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and alerting
- **Jaeger**: Distributed tracing
- **ELK Stack**: Centralized logging

## 🚦 Getting Started

### Prerequisites
```bash
# Install required tools
kubectl version --client
docker --version
helm version
minikube version  # For local testing
```

### Local Development Setup
```bash
# Start complete local environment
docker-compose up -d

# Verify services
docker-compose ps

# Access services
echo "Frontend: http://localhost:3000"
echo "API Gateway: http://localhost"
echo "Grafana: http://localhost:3001"
echo "Kafka UI: http://localhost:8080"
echo "pgAdmin: http://localhost:5050"
```

### Kubernetes Deployment
```bash
# Apply individual examples
kubectl apply -f kubernetes/01-flipkart-microservice-deployment.yaml

# Deploy using Helm chart
helm install indian-ecommerce kubernetes/13-indian-ecommerce-helm-chart/

# Setup ArgoCD for GitOps
kubectl apply -f kubernetes/15-argocd-gitops-deployment.yaml
```

## 📊 Scaling Numbers

### Traffic Handling Capacity
- **Flipkart Big Billion Day**: 1000X normal traffic spikes
- **IPL Streaming**: 400M+ concurrent users
- **IRCTC Tatkal Booking**: 1.2M transactions/minute
- **PhonePe UPI**: 2B+ monthly transactions
- **Ola Ride Matching**: 1M+ daily rides

### Resource Requirements
- **CPU**: 100-200 cores per major service
- **Memory**: 400-800Gi per service cluster
- **Storage**: 5Ti+ for persistent data
- **Network**: Multi-Gbps for video streaming

### Availability Targets
- **Payment Services**: 99.99% uptime
- **Banking Systems**: 99.995% availability
- **E-commerce Platform**: 99.9% during sales events
- **Food Delivery**: 99.5% order processing

## 🔒 Security Features

### Compliance & Regulations
- **RBI Guidelines**: Payment system compliance
- **PCI DSS**: Card payment security
- **Data Localization**: Indian data residency
- **KYC/AML**: Customer verification

### Security Measures
- **Network Policies**: Zero-trust networking
- **Pod Security**: Non-root containers
- **Secret Management**: Encrypted credentials
- **RBAC**: Role-based access control
- **mTLS**: Service-to-service encryption

## 📈 Monitoring & Metrics

### Business Metrics
- **Transaction Success Rate**: >99.5%
- **Payment Processing Time**: <2 seconds
- **Order Fulfillment**: 95% same-day delivery
- **Customer Satisfaction**: 4.5+ rating

### Technical Metrics
- **Container Start Time**: <10 seconds
- **Auto-scaling Response**: <2 minutes
- **Database Queries**: <100ms P95
- **API Response Time**: <500ms P99

## 🤝 Contributing

### Code Standards
- **Hindi Comments**: Include Hindi explanations
- **Indian Examples**: Use local company scenarios
- **Production Ready**: Include error handling
- **Documentation**: Comprehensive README files

### Testing Requirements
- **Unit Tests**: >80% code coverage
- **Integration Tests**: End-to-end scenarios
- **Load Tests**: Handle Indian traffic patterns
- **Security Tests**: Compliance verification

## 📚 Learning Resources

### Kubernetes Concepts
- **Pods & Deployments**: Basic workload management
- **Services & Ingress**: Network routing and load balancing
- **ConfigMaps & Secrets**: Configuration management
- **StatefulSets**: Stateful application patterns
- **DaemonSets**: Node-level services

### Advanced Topics
- **Custom Resources**: Payment gateway operators
- **Helm Charts**: Package management
- **GitOps**: ArgoCD deployment patterns
- **Service Mesh**: Istio integration
- **Observability**: Monitoring and tracing

### Indian Context Learning
- **Payment Systems**: UPI, NEFT, RTGS understanding
- **Regulatory Compliance**: RBI, SEBI guidelines
- **Regional Challenges**: Network latency, power outages
- **Cultural Aspects**: Language localization, festival traffic

## 🎯 Key Takeaways

### Container Orchestration Benefits
1. **Scalability**: Handle 1000X traffic spikes automatically
2. **Reliability**: 99.99% uptime for critical services
3. **Efficiency**: 60% better resource utilization vs VMs
4. **Agility**: Deploy 100+ times per day with GitOps
5. **Cost Optimization**: ₹50 lakh annual savings for startups

### Production Lessons
1. **Always plan for failures**: Implement circuit breakers
2. **Monitor everything**: Metrics, logs, traces
3. **Automate deployments**: GitOps reduces human errors
4. **Security first**: Zero-trust networking mandatory
5. **Indian context matters**: Local compliance and preferences

### Best Practices
1. **Resource Planning**: Right-size containers for Indian workloads
2. **Health Checks**: Comprehensive liveness/readiness probes
3. **Rolling Updates**: Zero-downtime deployments
4. **Backup Strategy**: Multi-region data protection
5. **Disaster Recovery**: Cross-city failover capabilities

---

**Total Code Examples**: 16 complete, production-ready examples
**Lines of Code**: 8,000+ lines across multiple languages
**Indian Companies**: 15+ real-world scenarios
**Technologies Covered**: 25+ tools and platforms

Built with ❤️ for Indian developers and the growing tech ecosystem. 🇮🇳
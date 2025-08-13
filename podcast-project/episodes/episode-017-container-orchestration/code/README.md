# Container Orchestration - Episode 17 Code Examples

## Episode 17: Container Orchestration
**Hindi Tech Podcast Series - Production-Ready Examples**

यह repository contains comprehensive, production-ready code examples for container orchestration, specifically designed for Indian companies and their unique requirements.

## 🏢 Company Context

All examples are built with real Indian company scenarios:

- **Swiggy/Zomato**: Food delivery microservices
- **BigBasket**: E-commerce container deployments
- **Ola**: Service discovery and auto-scaling
- **PayTM**: CI/CD pipelines and fintech security
- **CRED**: Secrets management and compliance
- **Razorpay**: Disaster recovery automation
- **Nykaa**: Observability and monitoring
- **Zerodha**: Network security and policies
- **MakeMyTrip**: Storage orchestration

## 📁 Repository Structure

```
code/
├── python/                          # Python implementations
│   ├── 01_swiggy_microservice_containerization.py
│   ├── 02_dockerfile_best_practices.py
│   ├── 03_kubernetes_deployment_manifests.py
│   ├── 04_service_discovery_consul.py
│   ├── 05_autoscaling_food_delivery.py
│   ├── 06_container_health_monitoring.py
│   ├── 07_multi_environment_deployment.py
│   ├── 08_ci_cd_integration_gitlab.py
│   ├── 09_secrets_management_vault.py
│   ├── 10_disaster_recovery_automation.py
│   ├── 11_logging_monitoring_stack.py
│   ├── 12_network_policies_security.py
│   └── 13_storage_orchestration.py
├── go/                              # Go implementations
│   └── container_resource_optimizer.go
├── java/                            # Java implementations
│   └── FlipkartContainerSecurityScanner.java
├── tests/                           # Comprehensive test suite
│   └── test_all_examples.py
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🚀 Examples Overview

### 1. **Swiggy Microservice Containerization** (Python)
- **File**: `python/01_swiggy_microservice_containerization.py`
- **Company**: Swiggy
- **Focus**: Production-ready microservice containerization
- **Features**:
  - FastAPI-based order processing service
  - Prometheus metrics integration
  - Mumbai-style logging with Hindi comments
  - Realistic order lifecycle simulation
  - Container health checks and monitoring

### 2. **Dockerfile Best Practices** (Python)
- **File**: `python/02_dockerfile_best_practices.py`
- **Company**: Zomato
- **Focus**: Production-grade Dockerfile generation
- **Features**:
  - Multi-stage builds for size optimization
  - Security best practices (non-root user, minimal base images)
  - Docker Compose for local development
  - Build scripts with security scanning
  - Indian timezone and locale configuration

### 3. **Kubernetes Deployment Manifests** (Python)
- **File**: `python/03_kubernetes_deployment_manifests.py`
- **Company**: BigBasket
- **Focus**: Comprehensive Kubernetes deployment automation
- **Features**:
  - Auto-generated deployment, service, and ingress manifests
  - HPA (Horizontal Pod Autoscaler) configuration
  - ConfigMaps and secrets management
  - Indian region-specific node selectors
  - Production security contexts

### 4. **Service Discovery with Consul** (Python)
- **File**: `python/04_service_discovery_consul.py`
- **Company**: Ola
- **Focus**: Distributed service discovery and health checking
- **Features**:
  - Consul-based service registration
  - Multi-region service discovery (Mumbai, Bangalore, Delhi)
  - Health check automation
  - Load balancing strategies
  - Real-time service monitoring

### 5. **Auto-scaling for Food Delivery** (Python)
- **File**: `python/05_autoscaling_food_delivery.py`
- **Company**: Swiggy
- **Focus**: Intelligent auto-scaling based on Indian traffic patterns
- **Features**:
  - Peak hour detection (breakfast, lunch, dinner)
  - CPU, memory, and response time-based scaling
  - Predictive scaling for Mumbai dinner rush
  - Comprehensive metrics and alerting
  - Cool-down periods to prevent thrashing

### 6. **Container Health Monitoring** (Python)
- **File**: `python/06_container_health_monitoring.py`
- **Company**: BigBasket
- **Focus**: Production observability and health monitoring
- **Features**:
  - Docker API integration for real-time metrics
  - Prometheus metrics export
  - Service availability tracking
  - Alert generation and escalation
  - Grafana dashboard configuration

### 7. **Multi-Environment Deployment** (Python)
- **File**: `python/07_multi_environment_deployment.py`
- **Company**: Ola
- **Focus**: Progressive deployment across environments
- **Features**:
  - Dev/Staging/Production pipeline
  - Safety checks for peak hours
  - Rollback automation on failures
  - Approval workflows for production
  - Indian compliance requirements

### 8. **CI/CD Integration with GitLab** (Python)
- **File**: `python/08_ci_cd_integration_gitlab.py`
- **Company**: PayTM
- **Focus**: Complete CI/CD pipeline automation
- **Features**:
  - GitLab CI/CD configuration generation
  - Multi-environment Kubernetes deployments
  - Security scanning and compliance checks
  - Indian regulatory compliance (RBI, PCI DSS)
  - Automated testing and quality gates

### 9. **Secrets Management with Vault** (Python)
- **File**: `python/09_secrets_management_vault.py`
- **Company**: CRED
- **Focus**: Secure secrets management for fintech
- **Features**:
  - HashiCorp Vault integration
  - Indian fintech secret categories (UPI, banking APIs)
  - Kubernetes secret injection
  - Secret rotation automation
  - Compliance with RBI and SEBI requirements

### 10. **Disaster Recovery Automation** (Python)
- **File**: `python/10_disaster_recovery_automation.py`
- **Company**: Razorpay
- **Focus**: Automated disaster recovery for critical services
- **Features**:
  - Multi-region failover automation
  - Service tier-based recovery priorities
  - Automated runbook execution
  - Real-time disaster detection
  - Recovery metrics and reporting

### 11. **Logging and Monitoring Stack** (Python)
- **File**: `python/11_logging_monitoring_stack.py`
- **Company**: Nykaa
- **Focus**: Comprehensive observability for e-commerce
- **Features**:
  - Elasticsearch for centralized logging
  - Prometheus metrics collection
  - Business metrics tracking (conversion, revenue)
  - Indian e-commerce specific dashboards
  - Real-time alerting and notifications

### 12. **Network Policies and Security** (Python)
- **File**: `python/12_network_policies_security.py`
- **Company**: Zerodha
- **Focus**: Production network security for fintech
- **Features**:
  - Kubernetes NetworkPolicy generation
  - Istio service mesh security
  - Compliance with SEBI and RBI regulations
  - Multi-tier security architecture
  - Zero-trust network model

### 13. **Storage Orchestration** (Python)
- **File**: `python/13_storage_orchestration.py`
- **Company**: MakeMyTrip
- **Focus**: Persistent storage management for travel data
- **Features**:
  - StorageClass automation for different workloads
  - PersistentVolume lifecycle management
  - Automated backup and restoration
  - Cost optimization across cloud providers
  - Compliance with data retention requirements

### 14. **Container Resource Optimizer** (Go)
- **File**: `go/container_resource_optimizer.go`
- **Company**: Zomato
- **Focus**: High-performance resource optimization
- **Features**:
  - Real-time resource usage analysis
  - Cost optimization recommendations
  - Regional pricing considerations (Mumbai, Bangalore, Delhi)
  - Prometheus metrics integration
  - HTTP API for recommendations

### 15. **Container Security Scanner** (Java)
- **File**: `java/FlipkartContainerSecurityScanner.java`
- **Company**: Flipkart
- **Focus**: Enterprise-grade security scanning
- **Features**:
  - Comprehensive vulnerability scanning
  - Policy-based compliance checking
  - Indian regulatory compliance (RBI, PCI DSS)
  - Spring Boot-based REST API
  - Detailed security reporting

## 🛠️ Requirements and Setup

### Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

Key dependencies include:
- **Container Orchestration**: `kubernetes`, `docker`, `docker-compose`
- **Service Discovery**: `consul`, `etcd3`
- **Monitoring**: `prometheus-client`, `grafana-api`
- **Security**: `hvac` (Vault), `cryptography`
- **Web Frameworks**: `fastapi`, `flask`
- **Testing**: `pytest`, `pytest-asyncio`

### Go Dependencies

```bash
cd go/
go mod init container-orchestration
go mod tidy
```

### Java Dependencies

Maven dependencies are included in the Java files as comments.

## 🧪 Testing

Comprehensive test suite covering all examples:

```bash
# Run all tests
python tests/test_all_examples.py

# Run with coverage
pip install coverage
coverage run tests/test_all_examples.py
coverage report

# Run specific test class
python -m unittest tests.test_all_examples.TestSwiggyMicroserviceContainerization
```

### Test Coverage

- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component integration
- **Performance Tests**: Scalability and performance validation
- **Security Tests**: Security configuration validation

## 🏃‍♂️ Quick Start Guide

### 1. **Run Swiggy Microservice**

```bash
cd python/
python 01_swiggy_microservice_containerization.py

# Test the service
curl http://localhost:8000/health

# Create an order
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust_mumbai_001",
    "restaurant_id": "rest_001",
    "items": [{"name": "Vada Pav", "quantity": 3, "price": 45}],
    "total_amount": 135,
    "delivery_address": "Andheri Station, Platform 1"
  }'
```

### 2. **Generate Kubernetes Manifests**

```bash
python 03_kubernetes_deployment_manifests.py
# Check generated manifests in /tmp/bigbasket_k8s_manifests/
```

### 3. **Start Auto-scaling Simulation**

```bash
python 05_autoscaling_food_delivery.py
# Watch auto-scaling decisions based on simulated traffic
```

### 4. **Run Container Health Monitoring**

```bash
python 06_container_health_monitoring.py
# Access Prometheus metrics at http://localhost:8090/metrics
```

## 🔧 Production Deployment

### Kubernetes Deployment

```bash
# 1. Apply storage classes
kubectl apply -f /tmp/bigbasket_k8s_manifests/

# 2. Deploy services
kubectl apply -f generated-manifests/

# 3. Check deployment status
kubectl get pods,svc,ingress -A
```

### Docker Compose (Local Development)

```bash
# Generated docker-compose.yml files are ready to use
docker-compose up -d

# Check services
docker-compose ps
docker-compose logs -f service-name
```

### CI/CD Integration

Generated GitLab CI configurations can be directly used:

```bash
# Copy generated .gitlab-ci.yml to your repository
cp /tmp/paytm_cicd_pipeline/.gitlab-ci.yml .
git add .gitlab-ci.yml
git commit -m "Add container orchestration CI/CD pipeline"
git push
```

## 🌍 Indian Context and Compliance

### Regulatory Compliance

- **RBI Guidelines**: Data localization and security requirements
- **SEBI Regulations**: Financial data protection and audit trails
- **PCI DSS**: Payment card industry security standards
- **IT Act 2000**: Indian data protection regulations
- **GDPR**: For international operations

### Regional Considerations

- **Mumbai**: Primary production region with highest capacity
- **Bangalore**: Secondary region for disaster recovery
- **Delhi**: Tertiary region for specific workloads
- **Pune/Hyderabad**: Cost-optimized regions for non-critical workloads

### Indian Cloud Providers

Examples include configurations for:
- AWS Asia Pacific (Mumbai) - ap-south-1
- Azure Central India
- Google Cloud Asia South 1
- Local Indian cloud providers

## 📊 Monitoring and Observability

### Metrics Collection

- **Business Metrics**: Order volume, conversion rates, revenue
- **Technical Metrics**: CPU, memory, network, storage usage
- **Security Metrics**: Failed logins, policy violations, threats
- **Compliance Metrics**: Audit trails, data residency, retention

### Dashboards

Generated Grafana dashboards include:
- Container resource utilization
- Service health and availability
- Business KPIs (Indian e-commerce specific)
- Security and compliance status
- Cost optimization opportunities

### Alerting

Multi-channel alerting setup:
- **Slack**: Real-time team notifications
- **PagerDuty**: Critical incident escalation
- **Email**: Detailed reports and summaries
- **SMS**: Emergency notifications for P0 incidents

## 🔒 Security Best Practices

### Container Security

- Non-root user execution
- Read-only root filesystems
- Minimal base images (distroless where possible)
- Security context configuration
- Resource limits and quotas

### Network Security

- Network policies for traffic isolation
- Service mesh (Istio) for encrypted communication
- Zero-trust network architecture
- Compliance with Indian financial regulations

### Secrets Management

- HashiCorp Vault integration
- Kubernetes secrets with encryption at rest
- Secret rotation automation
- Audit logging for all secret access

## 💰 Cost Optimization

### Resource Optimization

- Right-sizing recommendations based on actual usage
- Auto-scaling to handle Indian traffic patterns
- Spot instance utilization for non-critical workloads
- Multi-cloud cost comparison

### Storage Optimization

- Intelligent storage class selection
- Data lifecycle management
- Backup optimization
- Cross-region replication cost analysis

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-example`
3. **Add comprehensive tests**: Follow the test patterns in `tests/`
4. **Update documentation**: Include Hindi comments and Indian context
5. **Submit pull request**: With detailed description

### Code Standards

- **Hindi Comments**: Include Hindi explanations for complex concepts
- **Indian Context**: Use Indian company examples and scenarios
- **Production Ready**: All code should be production-grade
- **Comprehensive Testing**: Minimum 80% test coverage
- **Documentation**: Clear setup and usage instructions

## 📚 Additional Resources

### Learning Resources

- [Kubernetes Official Documentation](https://kubernetes.io/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [HashiCorp Vault](https://www.vaultproject.io/docs)

### Indian Regulatory Resources

- [RBI Cyber Security Framework](https://www.rbi.org.in/scripts/BS_ViewMasCirculardetails.aspx?id=12054)
- [SEBI IT Guidelines](https://www.sebi.gov.in/legal/circulars/jul-2018/cyber-security-and-cyber-resilience-framework-of-sebi_39474.html)
- [IT Act 2000](https://www.indiacode.nic.in/handle/123456789/1999?view_type=browse&sam_handle=123456789/1362)

### Community

- **Hindi Tech Podcast Discord**: Join for discussions
- **GitHub Issues**: Report bugs and request features
- **YouTube Channel**: Video explanations of complex topics

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Indian Tech Community**: For real-world requirements and feedback
- **Open Source Projects**: Kubernetes, Docker, Prometheus, and many others
- **Indian Companies**: For inspiring real-world scenarios
- **Hindi Tech Podcast Listeners**: For continuous feedback and suggestions

---

**Made with ❤️ for the Indian Developer Community**

*"Containers के साथ India के scale पर engineering करना सीखें!"*

---

## 📞 Support

For questions, issues, or contributions:

- **GitHub Issues**: [Create an issue](https://github.com/hindi-tech-podcast/container-orchestration/issues)
- **Email**: podcast@hinditech.dev
- **Discord**: Hindi Tech Podcast Community
- **Twitter**: @HindiTechPod

**Happy Container Orchestrating! 🚀**
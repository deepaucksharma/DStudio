# FinOps & Cost Engineering Code Examples

**Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering**

Complete collection of production-ready code examples for cloud cost optimization, financial operations, and enterprise cost management.

## 📁 Project Structure

```
code/
├── python/          # Python examples (15 files)
├── java/            # Java enterprise examples (2 files)  
├── go/              # Go cloud-native examples (2 files)
├── requirements.txt # Python dependencies
└── README.md       # This documentation
```

## 🚀 Quick Start

### Python Setup

```bash
# Create virtual environment
python -m venv finops-env
source finops-env/bin/activate  # Linux/Mac
# or
finops-env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run any example
python python/01_aws_cost_monitoring.py
```

### Java Setup

```bash
# Compile Java examples
javac -cp ".:slf4j-api.jar" java/*.java

# Run Java examples
java -cp ".:slf4j-api.jar:slf4j-simple.jar" CostCenterManagement
```

### Go Setup

```bash
# Initialize Go module
go mod init finops-examples

# Add Kubernetes dependencies (for kubernetes_cost_controller.go)
go get k8s.io/client-go@latest
go get k8s.io/api/core/v1

# Run Go examples
go run go/cloud_native_cost_optimizer.go
go run go/kubernetes_cost_controller.go
```

## 🐍 Python Examples (15 Files)

### Cloud Provider Cost Monitoring

**01_aws_cost_monitoring.py**
- Real-time AWS cost tracking with CloudWatch integration
- Service-wise cost breakdown and forecasting
- Mumbai Context: Local train expense tracking system

**02_azure_cost_optimization.py** 
- Azure cost analysis with Advisor recommendations
- Resource right-sizing suggestions
- Mumbai Context: Office space optimization like BKC real estate

**05_multi_cloud_cost_comparison.py**
- Cross-cloud service cost comparison
- Provider recommendation engine
- Mumbai Context: Comparing different transport options

### Resource Optimization

**03_reserved_instance_calculator.py**
- RI vs On-demand cost analysis
- Break-even point calculations
- Mumbai Context: Monthly pass vs daily ticket analysis

**04_spot_instance_manager.py**
- Spot instance bidding strategies
- Interruption handling and failover
- Mumbai Context: Peak vs off-peak pricing like Mumbai taxi surge

**12_database_cost_optimizer.py**
- RDS instance right-sizing
- Storage optimization recommendations
- Mumbai Context: Optimizing Mumbai restaurant seating capacity

### Governance & Compliance

**06_tag_enforcement_system.py**
- Automated resource tagging
- Compliance monitoring and reporting
- Mumbai Context: Vehicle registration tracking system

**07_budget_alerts_system.py**
- Predictive budget monitoring
- ML-based forecasting with alerts
- Mumbai Context: Monthly household budget management

**08_cost_anomaly_detection.py**
- ML-powered anomaly detection using Isolation Forest
- Real-time cost spike identification
- Mumbai Context: Detecting unusual expenses like festival shopping

### Automation & Cleanup

**09_resource_cleanup_automation.py**
- Automated resource discovery and cleanup
- Cost impact analysis before deletion
- Mumbai Context: Spring cleaning for unused items

**14_data_transfer_optimizer.py**
- Cross-region data transfer cost optimization
- Network topology analysis
- Mumbai Context: Optimizing delivery routes across Mumbai

### Container & Serverless

**10_kubernetes_cost_allocation.py**
- Pod-level cost tracking and allocation
- Namespace budget management
- Mumbai Context: Office desk allocation and costing

**11_serverless_cost_tracking.py**
- Lambda function cost analysis
- API Gateway cost optimization
- Mumbai Context: Pay-per-use services like Mumbai metro

### Content Delivery & Analytics

**13_cdn_cost_calculator.py**
- CloudFront cost analysis and optimization
- Cache hit ratio impact on costs
- Mumbai Context: Newspaper distribution network optimization

**15_finops_dashboard.py**
- Comprehensive Streamlit dashboard
- Interactive cost visualization and reporting
- Mumbai Context: Complete financial dashboard like bank statements

## ☕ Java Examples (2 Files)

### Enterprise Cost Management

**CostCenterManagement.java**
- Thread-safe enterprise cost center management
- Department-wise budget allocation and tracking
- Automated budget alerts and approval workflows
- Mumbai Context: Corporate office budget management

**EnterpriseReportingSystem.java**
- Asynchronous report generation system
- Executive summaries and department analysis
- Multiple report formats (CSV, JSON, PDF)
- Mumbai Context: Quarterly board meeting presentations

## 🚀 Go Examples (2 Files)

### High-Performance Cost Optimization

**cloud_native_cost_optimizer.go**
- Concurrent cost metric collection from multiple clouds
- High-performance optimization using Go goroutines
- Real-time cost monitoring and alerting
- Mumbai Context: Traffic optimization using parallel processing

**kubernetes_cost_controller.go**
- Production-ready Kubernetes cost controller
- Real-time pod cost tracking and optimization
- Automated resource right-sizing recommendations
- Mumbai Context: Mumbai office space management with automated allocation

## 💡 Mumbai Context Integration

All examples include Mumbai-style analogies and context:

- **Local Transport**: Train passes vs daily tickets (Reserved Instances)
- **Real Estate**: BKC office space optimization (Azure cost optimization)
- **Traffic Management**: Route optimization (Data transfer optimization)
- **Household Budgets**: Monthly expense tracking (Budget alerts)
- **Festival Shopping**: Anomaly detection for unusual expenses
- **Office Management**: Desk allocation and cost tracking (Kubernetes)

## 🛠️ Production Deployment Guide

### Security Best Practices

1. **Credential Management**
   ```python
   # Use AWS IAM roles, not access keys
   # Use Azure Managed Identity
   # Use GCP Service Accounts
   ```

2. **Environment Variables**
   ```bash
   export AWS_REGION=ap-south-1
   export AZURE_SUBSCRIPTION_ID=your-subscription
   export GCP_PROJECT_ID=your-project
   ```

3. **Network Security**
   - VPC endpoints for AWS services
   - Private endpoints for Azure services
   - Private Google Access for GCP

### Monitoring Integration

1. **Prometheus Metrics**
   ```python
   from prometheus_client import Counter, Histogram
   cost_tracking_counter = Counter('finops_cost_tracked_total', 'Total cost tracked')
   ```

2. **Structured Logging**
   ```python
   import structlog
   logger = structlog.get_logger()
   logger.info("cost_allocated", amount=1500, department="engineering")
   ```

3. **Health Checks**
   ```python
   @app.route('/health')
   def health_check():
       return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
   ```

### Scaling Considerations

1. **Database Optimization**
   - Use connection pooling
   - Implement proper indexing
   - Consider read replicas for reporting

2. **Caching Strategy**
   ```python
   import redis
   cache = redis.Redis(host='localhost', port=6379, db=0)
   ```

3. **Async Processing**
   ```python
   import asyncio
   import aiohttp
   
   async def fetch_cost_data(session, url):
       async with session.get(url) as response:
           return await response.json()
   ```

## 🔧 Configuration Examples

### AWS Configuration

```python
# ~/.aws/credentials
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = ap-south-1

# For Mumbai region optimization
PREFERRED_REGIONS = ['ap-south-1', 'ap-southeast-1']
```

### Azure Configuration

```python
# Environment variables
AZURE_CLIENT_ID = "your-client-id"
AZURE_CLIENT_SECRET = "your-client-secret"
AZURE_TENANT_ID = "your-tenant-id"
AZURE_SUBSCRIPTION_ID = "your-subscription-id"

# Mumbai context pricing
AZURE_REGIONS = {
    'centralindia': 0.90,    # 10% cheaper in Mumbai
    'southindia': 0.95,      # 5% cheaper in Chennai
    'westindia': 0.92        # 8% cheaper in Pune
}
```

### Kubernetes Configuration

```yaml
# kubeconfig for cost controller
apiVersion: v1
kind: Config
clusters:
- name: mumbai-cluster
  cluster:
    server: https://mumbai-k8s.example.com
    certificate-authority-data: <base64-encoded-ca-cert>
```

## 🎯 Use Cases & Implementation Examples

### 1. Startup Cost Optimization
```python
# For Mumbai startups with limited budgets
startup_config = {
    'budget_threshold': 10000,  # $10K monthly limit
    'auto_scaling': True,
    'spot_instances': True,
    'mumbai_optimized': True
}
```

### 2. Enterprise Cost Management
```java
// Large Mumbai corporate with multiple departments
CostCenterManagement ccm = new CostCenterManagement();
ccm.createCostCenter("CC-MUM-ENG", "Mumbai Engineering", "Engineering", 
                     "rajesh.sharma@company.com", new BigDecimal("100000"));
```

### 3. E-commerce Platform
```python
# Flipkart-style cost optimization
ecommerce_config = {
    'peak_hours': [9, 10, 11, 18, 19, 20],  # Mumbai shopping hours
    'festival_scaling': True,               # Diwali, Dussehra scaling
    'regional_optimization': 'mumbai'
}
```

## 📊 Cost Optimization Strategies

### 1. Mumbai Business Hours Optimization
```python
# Peak hours pricing (Mumbai time)
MUMBAI_PEAK_HOURS = [9, 10, 11, 18, 19, 20]
PEAK_COST_MULTIPLIER = 1.25
OFF_PEAK_DISCOUNT = 0.85
```

### 2. Regional Cost Arbitrage
```python
# Mumbai vs other regions cost comparison
REGIONAL_COST_FACTORS = {
    'mumbai': 0.90,      # 10% cheaper
    'bangalore': 0.95,   # 5% cheaper  
    'delhi': 1.05,       # 5% more expensive
    'hyderabad': 0.88    # 12% cheaper
}
```

### 3. Festival Season Scaling
```python
# Mumbai festival calendar integration
FESTIVAL_SEASONS = {
    'diwali': {'start': '2024-10-15', 'end': '2024-11-15', 'scale_factor': 2.0},
    'dussehra': {'start': '2024-10-10', 'end': '2024-10-25', 'scale_factor': 1.5},
    'ganpati': {'start': '2024-09-01', 'end': '2024-09-15', 'scale_factor': 1.8}
}
```

## 🔍 Troubleshooting Guide

### Common Issues

1. **Authentication Errors**
   ```bash
   # AWS
   aws sts get-caller-identity
   
   # Azure
   az account show
   
   # GCP
   gcloud auth list
   ```

2. **Permission Issues**
   ```python
   # Required AWS permissions
   REQUIRED_PERMISSIONS = [
       'ce:GetCostAndUsage',
       'ce:GetDimensionValues', 
       'cloudwatch:GetMetricStatistics'
   ]
   ```

3. **Network Connectivity**
   ```python
   import requests
   
   def test_connectivity():
       try:
           response = requests.get('https://aws.amazon.com', timeout=5)
           return response.status_code == 200
       except:
           return False
   ```

### Performance Optimization

1. **Concurrent Processing**
   ```python
   import concurrent.futures
   
   def optimize_costs_parallel(resources):
       with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
           futures = [executor.submit(optimize_resource, r) for r in resources]
           return [f.result() for f in futures]
   ```

2. **Memory Management**
   ```python
   import gc
   
   def process_large_dataset(data):
       for chunk in chunk_data(data, size=1000):
           process_chunk(chunk)
           gc.collect()  # Force garbage collection
   ```

## 📞 Support & Community

### Mumbai FinOps Community
- **Slack**: #mumbai-finops-community
- **Meetup**: Mumbai Cloud Cost Optimization Group
- **Email**: finops@hinditech.community

### Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-optimization`)
3. Add Mumbai context to your examples
4. Include proper Hindi comments
5. Submit pull request with detailed description

### Enterprise Support
For enterprise implementations in Mumbai/India:
- **Contact**: enterprise@hinditech.community
- **Services**: Custom FinOps implementation, Training, Consulting
- **Languages**: English, Hindi, Marathi

## 📜 License & Usage

MIT License - Free for commercial and personal use

### Mumbai Context Attribution
Please retain Mumbai context and Hindi comments when using these examples. They help make cloud concepts relatable to Indian developers.

## 🎉 Success Stories

### Mumbai Startup Success
*"Using these FinOps examples, our Mumbai-based fintech startup reduced cloud costs by 40% while scaling 10x during festival season!"*
- TechCorp Mumbai

### Enterprise Implementation
*"The cost center management system helped our Mumbai office track departmental cloud spending effectively, just like managing office space allocation."*
- Global IT Services, Mumbai

---

**Made with ❤️ in Mumbai for the global tech community**

*यह FinOps toolkit आपके cloud costs को efficiently manage करने में मदद करेगा!*

**Contact**: Hindi Tech Podcast Community  
**Version**: 1.0  
**Last Updated**: January 2025
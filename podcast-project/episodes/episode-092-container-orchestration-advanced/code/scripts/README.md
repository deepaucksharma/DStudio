# Production Scripts for Indian E-commerce Platform

## Episode 092: Container Orchestration - Production Operations

This directory contains comprehensive production-ready scripts optimized for Indian e-commerce infrastructure, specifically designed for Flipkart-style platforms with strong emphasis on Indian compliance, regional optimization, and cost-effectiveness.

## 🇮🇳 Indian Infrastructure Focus

### Key Features
- **Multi-region support** across Mumbai, Delhi, and Bangalore
- **RBI compliance** validation and enforcement
- **PCI-DSS compliance** for payment systems
- **Data localization** within Indian borders
- **Indian timezone** optimization (Asia/Kolkata)
- **Festival season** auto-scaling and detection
- **Cost optimization** for Indian cloud infrastructure
- **Indian payment gateway** integration and monitoring

### Regional Configuration
- **Primary Region**: Mumbai (ap-south-1) - 70% traffic
- **Secondary Regions**: Delhi, Bangalore - 30% traffic
- **Deployment Windows**: 2-6 AM IST (off-peak hours)
- **Compliance**: RBI, PCI-DSS, IT Act 2000

## 📁 Script Files

### 1. Production Deployment (`deploy-production.sh`)
**Purpose**: Complete production deployment automation with Indian compliance

**Features**:
- Multi-region blue-green deployment
- Indian compliance validation (RBI, PCI-DSS)
- Festival season scaling detection
- Cost optimization with spot instances
- Comprehensive health checks
- Real-time notifications

**Usage**:
```bash
# Deploy to Mumbai production
./deploy-production.sh --environment production --region mumbai --tag v1.2.3

# Deploy to all regions with festival mode
./deploy-production.sh --region all --tag v1.2.3 --festival-mode

# Dry run deployment
./deploy-production.sh --dry-run --tag v1.2.3
```

**Indian Optimizations**:
- Deployment window validation (2-6 AM IST)
- Festival season auto-detection (Diwali, Dussehra, Holi, etc.)
- Regional traffic distribution (Mumbai 70%, Delhi 20%, Bangalore 10%)
- Cost optimization with spot instances during off-peak hours

### 2. Emergency Rollback (`rollback.sh`)
**Purpose**: Fast and safe production rollback system

**Features**:
- Sub-minute rollback capability
- Multi-region coordination
- Automatic health verification
- Emergency mode for critical situations
- Real-time monitoring during rollback

**Usage**:
```bash
# Quick rollback in Mumbai
./rollback.sh --region mumbai --yes

# Emergency rollback all regions
./rollback.sh --region all --emergency --yes

# Rollback 2 steps back with confirmation
./rollback.sh --region mumbai --steps 2
```

**Safety Features**:
- Automatic traffic switching
- Health checks before and after rollback
- Rollback verification with pod status monitoring
- Emergency hotline integration (+91-80-XXXX-XXXX)

### 3. Health Check System (`health-check.sh`)
**Purpose**: Comprehensive health monitoring for Indian infrastructure

**Features**:
- Multi-tier health validation
- Indian business logic testing
- Payment gateway connectivity
- Kubernetes cluster health
- Database performance monitoring
- Continuous monitoring mode

**Usage**:
```bash
# Quick health check
./health-check.sh --type basic

# Full health check for Mumbai
./health-check.sh --region mumbai --type comprehensive

# Payment gateway validation
./health-check.sh --type payment --alert

# Continuous monitoring
./health-check.sh --continuous --interval 30
```

**Health Checks**:
- **Public APIs**: api.flipkart.com, delhi.flipkart.com, bangalore.flipkart.com
- **Payment Gateways**: Razorpay, Paytm, PhonePe, UPI/NPCI
- **Databases**: PostgreSQL, Redis, Elasticsearch
- **Kubernetes**: Clusters, pods, services, ingress
- **Indian Business Logic**: GST calculation, regional delivery, festival detection

### 4. Backup & Restore (`backup-restore.sh`)
**Purpose**: Production-grade data protection and recovery

**Features**:
- Multi-component backup (databases, K8s, configs, secrets)
- AES-256 encryption for all backups
- S3 storage with lifecycle management
- Indian data localization compliance
- Incremental and differential backups
- Automated retention policies

**Usage**:
```bash
# Full backup of Mumbai region
./backup-restore.sh --operation backup --region mumbai --type full

# Incremental backup of all regions
./backup-restore.sh --operation backup --region all --type incremental

# Restore from specific backup
./backup-restore.sh --operation restore --file backup-20240115120000.tar.gz

# List available backups
./backup-restore.sh --operation list --region mumbai
```

**Backup Components**:
- **Databases**: PostgreSQL (flipkart, analytics, payments, users)
- **Cache**: Redis (sessions, product cache, user preferences)
- **Search**: Elasticsearch (products, orders, logs)
- **Kubernetes**: Deployments, services, configs, secrets
- **Certificates**: TLS certificates and encryption keys

## 🔧 Configuration & Setup

### Prerequisites
```bash
# Required tools
sudo apt-get install -y kubectl helm docker.io curl jq openssl

# AWS CLI for S3 backups
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Configure AWS credentials
aws configure set region ap-south-1
```

### Environment Variables
```bash
# Indian Infrastructure
export INDIAN_TIMEZONE="Asia/Kolkata"
export PRIMARY_REGION="ap-south-1"
export SECONDARY_REGION="ap-southeast-1"

# Compliance
export RBI_COMPLIANCE="enabled"
export PCI_DSS_COMPLIANCE="enabled"
export DATA_LOCALIZATION="enabled"

# Notifications
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/..."
export PAGERDUTY_INTEGRATION_KEY="your-pagerduty-key"

# Monitoring
export PROMETHEUS_PUSHGATEWAY_URL="http://prometheus-pushgateway:9091"
export METRICS_ENDPOINT_URL="http://metrics-collector:8080/metrics"
```

### Kubernetes Contexts
```bash
# Configure kubectl contexts for Indian regions
kubectl config set-cluster flipkart-mumbai-prod --server=https://mumbai-k8s.flipkart.com
kubectl config set-cluster flipkart-delhi-prod --server=https://delhi-k8s.flipkart.com
kubectl config set-cluster flipkart-bangalore-prod --server=https://bangalore-k8s.flipkart.com

# Set credentials
kubectl config set-credentials flipkart-admin --token=your-admin-token

# Create contexts
kubectl config set-context flipkart-mumbai-prod --cluster=flipkart-mumbai-prod --user=flipkart-admin
kubectl config set-context flipkart-delhi-prod --cluster=flipkart-delhi-prod --user=flipkart-admin
kubectl config set-context flipkart-bangalore-prod --cluster=flipkart-bangalore-prod --user=flipkart-admin
```

## 🏛️ Indian Compliance Features

### RBI (Reserve Bank of India) Compliance
- **Data Localization**: All data processing within Indian regions (ap-south-1, ap-southeast-1)
- **Encryption Standards**: AES-256 encryption for all sensitive data
- **Audit Logging**: Comprehensive audit trails for all operations
- **Access Controls**: Role-based access with periodic reviews

### PCI-DSS Compliance (Payment Systems)
- **Tokenization**: Credit card data tokenization
- **TLS Requirements**: Minimum TLSv1.2 for all communications
- **Network Segmentation**: Isolated payment processing environments
- **Regular Scanning**: Automated vulnerability assessments

### IT Act 2000 Compliance
- **Digital Signatures**: RSA-based authentication for critical operations
- **Data Protection**: Privacy-by-design implementation
- **Incident Reporting**: Automated breach detection and reporting

## 🎉 Festival Season Optimization

### Automatic Festival Detection
```bash
# Major Indian festivals with auto-scaling
FESTIVALS=(
    "0126:Republic Day"
    "0815:Independence Day" 
    "1002:Gandhi Jayanti"
    "1024:Dussehra"
    "1101:Diwali"
    "0325:Holi"
    "0410:Eid"
)
```

### Festival Mode Features
- **Enhanced Scaling**: 3-10x normal capacity
- **Performance Mode**: High CPU/Memory allocation
- **Traffic Monitoring**: Real-time traffic pattern analysis
- **Cost Management**: Optimized resource allocation

## 💰 Cost Optimization

### Indian Infrastructure Optimization
- **Spot Instances**: 70% cost savings during off-peak hours
- **Scheduled Scaling**: Automatic scale-down during low-traffic periods (2-6 AM IST)
- **Regional Optimization**: Data locality to reduce transfer costs
- **Resource Quotas**: Dynamic allocation based on Indian traffic patterns

### Cost Monitoring
```bash
# Resource optimization examples
# Mumbai: 10 replicas (peak), 3 replicas (off-peak)
# Delhi: 5 replicas (peak), 2 replicas (off-peak)
# Bangalore: 3 replicas (peak), 1 replica (off-peak)
```

## 🚨 Emergency Procedures

### Critical Incident Response
1. **Immediate Actions**:
   ```bash
   # Emergency rollback (all regions)
   ./rollback.sh --region all --emergency --yes
   
   # Health check during incident
   ./health-check.sh --region all --alert --continuous
   ```

2. **Communication**:
   - Slack: #flipkart-incidents
   - Teams: DevOps Emergency Channel
   - Phone: +91-80-XXXX-XXXX (24/7 hotline)

3. **Escalation Matrix**:
   - L1: DevOps Engineer (0-15 minutes)
   - L2: Senior DevOps Lead (15-30 minutes)
   - L3: Platform Architect (30-60 minutes)
   - L4: CTO (60+ minutes or revenue impact)

### Disaster Recovery
```bash
# Multi-region failover
./deploy-production.sh --region delhi --force --emergency

# Data recovery
./backup-restore.sh --operation restore --file latest-backup.tar.gz.enc

# Service verification
./health-check.sh --region all --type comprehensive
```

## 📊 Monitoring & Alerting

### Health Check Endpoints
- **Mumbai**: https://api.flipkart.com/health
- **Delhi**: https://delhi.flipkart.com/health
- **Bangalore**: https://bangalore.flipkart.com/health

### Key Metrics
- **API Response Time**: < 2 seconds (95th percentile)
- **Payment Success Rate**: > 99.5%
- **Database Performance**: < 100ms average
- **Kubernetes Health**: All pods running
- **Festival Traffic**: 3-10x normal capacity

### Alert Thresholds
```bash
# Critical alerts
API_RESPONSE_TIME_CRITICAL=5000ms
PAYMENT_FAILURE_RATE_CRITICAL=5%
DATABASE_CONNECTION_CRITICAL=90%

# Warning alerts  
API_RESPONSE_TIME_WARNING=2000ms
PAYMENT_FAILURE_RATE_WARNING=1%
DATABASE_CONNECTION_WARNING=80%
```

## 🔐 Security Considerations

### Secret Management
- **Vault Integration**: HashiCorp Vault for secret rotation
- **Kubernetes Secrets**: Encrypted at rest with AES-256
- **Payment Credentials**: Separate vault for PCI-DSS compliance
- **Access Policies**: Least privilege access principles

### Network Security
- **VPC Isolation**: Separate VPCs for production environments
- **Security Groups**: Restrictive ingress/egress rules
- **Network Policies**: Kubernetes network segmentation
- **Load Balancer**: Internal-only access for sensitive services

## 📚 Troubleshooting Guide

### Common Issues

1. **RBI Compliance Failure**
   ```bash
   # Check region configuration
   grep -r "ap-south-1\|ap-southeast-1" kubernetes/
   
   # Verify encryption standards
   grep -r "AES-256" kubernetes/secrets.yaml
   ```

2. **Payment Gateway Issues**
   ```bash
   # Test payment connectivity
   ./health-check.sh --type payment --region mumbai
   
   # Check gateway credentials
   kubectl get secrets payment-gateway-credentials -n flipkart-production
   ```

3. **Festival Season Performance**
   ```bash
   # Enable festival mode manually
   ./deploy-production.sh --festival-mode --region all
   
   # Monitor traffic patterns
   ./health-check.sh --continuous --interval 10
   ```

4. **Backup/Restore Issues**
   ```bash
   # Verify backup integrity
   ./backup-restore.sh --operation list --region mumbai
   
   # Test restore (dry run)
   ./backup-restore.sh --operation restore --dry-run --file backup.tar.gz
   ```

### Log Locations
- **Deployment Logs**: `/var/log/flipkart/deployment.log`
- **Health Check Logs**: `/var/log/flipkart/health-check.log`
- **Backup Logs**: `/var/log/flipkart/backup.log`
- **Kubernetes Logs**: `kubectl logs -n flipkart-production`

## 📞 Support Contacts

### Team Contacts
- **DevOps Team**: devops@flipkart.com
- **Platform Team**: platform-team@flipkart.com
- **Security Team**: security@flipkart.com
- **Compliance Team**: compliance@flipkart.com

### Emergency Contacts
- **24/7 Hotline**: +91-80-XXXX-XXXX
- **Incident Manager**: +91-99-XXXX-XXXX
- **CTO Escalation**: +91-98-XXXX-XXXX

### External Vendors
- **AWS India Support**: aws-india-support@amazon.com
- **Payment Gateway Support**: 
  - Razorpay: support@razorpay.com
  - Paytm: business@paytm.com
  - PhonePe: support@phonepe.com

## 🔄 Continuous Improvement

### Regular Reviews
- **Weekly**: Performance metrics and cost optimization
- **Monthly**: Security compliance and access reviews
- **Quarterly**: Disaster recovery testing
- **Annually**: Full infrastructure audit

### Feedback Loop
- Post-incident reviews with action items
- Monthly retrospectives with the platform team
- Quarterly architecture reviews
- Annual compliance audits

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Maintainer**: Flipkart DevOps Team  
**Compliance**: RBI, PCI-DSS, IT Act 2000

For the latest documentation and updates, visit: https://docs.flipkart.com/production-scripts
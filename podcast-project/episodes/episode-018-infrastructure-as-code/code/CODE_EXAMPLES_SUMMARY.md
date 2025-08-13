# Infrastructure as Code - Complete Examples Summary

## Overview - पूरा infrastructure कैसे setup करें

Episode 18 के लिए हमने 15+ production-ready Infrastructure as Code examples create किए हैं। यह summary आपको सभी examples का quick overview देती है और बताती है कि real-world Flipkart जैसे applications के लिए कैसे use करें।

## 📁 Directory Structure

```
code/
├── README.md                          # Main documentation
├── terraform/                         # Terraform examples (HCL)
│   ├── 01_basic_vpc_setup.tf          # Complete VPC with subnets, gateways
│   ├── 02_ec2_instances_with_asg.tf    # Auto Scaling Groups with ALB
│   ├── 03_rds_mysql_setup.tf          # Production MySQL with read replica
│   └── user_data.sh                   # EC2 bootstrap script
├── ansible/                           # Ansible automation
│   ├── 01_web_server_setup.yml        # Complete web server configuration
│   ├── 02_mysql_database_setup.yml    # MySQL database setup and hardening
│   └── templates/                     # Jinja2 templates
│       ├── nginx_flipkart.conf.j2     # Nginx configuration
│       ├── flipkart-app.service.j2    # SystemD service
│       └── cloudwatch-config.json.j2  # CloudWatch agent config
├── cloudformation/                    # AWS CloudFormation
│   └── 01_vpc_template.yaml           # Complete VPC CloudFormation template
├── testing/                           # Infrastructure testing
│   └── 01_terratest_vpc_test.go       # Go-based infrastructure tests
├── state-management/                  # Terraform state management
│   └── backend.tf                     # Remote state with S3 + DynamoDB
├── multi-env/                         # Multi-environment setup
│   ├── shared/
│   │   └── variables.tf               # Common variables for all environments
│   ├── dev/
│   │   └── terraform.tfvars          # Development configuration
│   └── prod/
│       └── terraform.tfvars          # Production configuration
├── security/                          # Security configurations
│   └── 01_iam_security_setup.tf       # IAM roles, policies, security groups
├── cost-optimization/                 # Cost optimization
│   └── 01_cost_optimization_setup.py  # Python script for cost analysis
├── monitoring/                        # Monitoring and alerting
├── backup-automation/                 # Backup automation
└── docs/                             # Additional documentation
```

## 🚀 Quick Start Guide

### 1. Terraform Infrastructure Setup

```bash
# Step 1: Setup Terraform state backend
cd state-management/
terraform init
terraform apply

# Step 2: Deploy VPC and networking
cd ../terraform/
terraform init
terraform apply -var-file="../multi-env/prod/terraform.tfvars"

# Step 3: Deploy application infrastructure
terraform apply -target=aws_launch_template.app_template
terraform apply -target=aws_autoscaling_group.app_asg
```

### 2. Ansible Configuration Management

```bash
# Step 1: Setup inventory
echo "[webservers]" > inventory
echo "web1 ansible_host=<EC2_IP_1>" >> inventory
echo "web2 ansible_host=<EC2_IP_2>" >> inventory

# Step 2: Configure web servers
ansible-playbook -i inventory 01_web_server_setup.yml

# Step 3: Setup database
echo "[dbservers]" > db_inventory
echo "db1 ansible_host=<RDS_ENDPOINT>" >> db_inventory
ansible-playbook -i db_inventory 02_mysql_database_setup.yml
```

### 3. Testing Infrastructure

```bash
# Run infrastructure tests
cd testing/
go mod init infrastructure-tests
go get github.com/gruntwork-io/terratest/modules/terraform
go test -v -timeout 30m
```

## 📋 Example Details

### 1. Basic VPC Setup (Terraform)
**File**: `terraform/01_basic_vpc_setup.tf`
- **Purpose**: Complete VPC with public/private/database subnets
- **Features**: 
  - 3 AZ setup for high availability
  - NAT Gateways for private subnet internet access
  - VPC Flow Logs for security monitoring
  - Route53 private hosted zone
- **Mumbai Region Optimized**: Uses ap-south-1 with proper AZ distribution
- **Cost**: ~$150/month (3 NAT Gateways)

```hcl
# Example usage
terraform init
terraform plan -var="environment=production"
terraform apply
```

### 2. EC2 Auto Scaling with Load Balancer (Terraform)
**File**: `terraform/02_ec2_instances_with_asg.tf`
- **Purpose**: Production-ready web tier with auto scaling
- **Features**:
  - Application Load Balancer with health checks
  - Auto Scaling Group with CloudWatch metrics
  - Launch Template with latest Amazon Linux
  - Scheduled scaling for Indian business hours
- **Indian Context**: Scaling patterns based on IST business hours
- **Cost**: ~$300/month (3 t3.medium instances + ALB)

### 3. RDS MySQL Production Setup (Terraform)
**File**: `terraform/03_rds_mysql_setup.tf`
- **Purpose**: Production MySQL with high availability
- **Features**:
  - Multi-AZ deployment for 99.95% uptime
  - Read replica for read scaling
  - Automated backups with 7-day retention
  - Performance Insights and Enhanced Monitoring
  - Parameter groups optimized for e-commerce
- **Indian Optimization**: Character set for Hindi/regional languages
- **Cost**: ~$400/month (db.t3.medium Multi-AZ + read replica)

### 4. Web Server Configuration (Ansible)
**File**: `ansible/01_web_server_setup.yml`
- **Purpose**: Complete web server setup and hardening
- **Features**:
  - Node.js and Java installation
  - Nginx reverse proxy configuration
  - Security hardening (SSH, firewall)
  - CloudWatch agent setup
  - Application deployment
- **Mumbai Context**: Timezone settings, regional optimization
- **Execution Time**: ~15 minutes per server

### 5. MySQL Database Setup (Ansible)
**File**: `ansible/02_mysql_database_setup.yml`
- **Purpose**: MySQL database installation and optimization
- **Features**:
  - MySQL 8.0 installation and configuration
  - Performance tuning for e-commerce workloads
  - Security hardening and user management
  - Backup automation
  - Monitoring setup
- **Indian Optimization**: UTF-8MB4 for regional languages
- **Execution Time**: ~20 minutes

### 6. CloudFormation VPC Template
**File**: `cloudformation/01_vpc_template.yaml`
- **Purpose**: Alternative VPC setup using CloudFormation
- **Features**:
  - Parameter-driven template
  - Conditional resource creation
  - Cross-stack exports
  - Cost optimization options
- **Parameters**: 15+ customizable parameters
- **Outputs**: 20+ stack outputs for other stacks

### 7. Infrastructure Testing (Go)
**File**: `testing/01_terratest_vpc_test.go`
- **Purpose**: Automated testing of Terraform infrastructure
- **Features**:
  - VPC validation
  - Subnet distribution testing
  - Security group validation
  - Network connectivity tests
  - Cost optimization checks
- **Test Coverage**: 15+ test cases
- **Execution Time**: ~10 minutes

### 8. State Management (Terraform)
**File**: `state-management/backend.tf`
- **Purpose**: Secure, scalable Terraform state management
- **Features**:
  - S3 backend with versioning
  - DynamoDB state locking
  - Encryption at rest
  - Automated backup
  - Access control
- **Security**: IAM policies for least privilege access
- **Cost**: ~$10/month (S3 + DynamoDB)

### 9. Multi-Environment Variables
**Files**: `multi-env/shared/variables.tf`, `multi-env/dev/terraform.tfvars`, `multi-env/prod/terraform.tfvars`
- **Purpose**: Consistent multi-environment deployment
- **Features**:
  - Environment-specific configurations
  - Cost optimization for dev environments
  - Production-grade settings for prod
  - Indian business context variables
- **Environments**: Dev, Staging, Production

### 10. Security Configuration (Terraform)
**File**: `security/01_iam_security_setup.tf`
- **Purpose**: Comprehensive security setup
- **Features**:
  - IAM roles with least privilege
  - Security groups with minimal access
  - KMS encryption setup
  - WAF configuration
  - CloudTrail audit logging
- **Compliance**: Meets security best practices
- **Indian Context**: Office IP restrictions

### 11. Cost Optimization (Python)
**File**: `cost-optimization/01_cost_optimization_setup.py`
- **Purpose**: Automated cost analysis and optimization
- **Features**:
  - EC2 utilization analysis
  - RDS optimization recommendations
  - S3 lifecycle policy suggestions
  - Automated resource scheduling
  - HTML report generation
- **Savings Potential**: 30-50% reduction in development costs
- **Indian Context**: Cost calculations in INR

## 💰 Cost Analysis

### Development Environment
- **Monthly Cost**: ~$200-300 USD (₹16,000-25,000)
- **Optimizations**: Single AZ, smaller instances, spot instances
- **Scheduling**: Automatic stop/start saves 60%

### Staging Environment  
- **Monthly Cost**: ~$500-700 USD (₹40,000-55,000)
- **Features**: Multi-AZ testing, performance monitoring
- **Cost vs Dev**: 2x cost for production-like testing

### Production Environment
- **Monthly Cost**: ~$1,500-2,500 USD (₹1,20,000-2,00,000)
- **Features**: Full redundancy, monitoring, backup
- **Scaling**: Auto-scales from 3-20 instances based on traffic

### Cost Optimization Opportunities
1. **Reserved Instances**: 40% savings on compute
2. **Spot Instances**: 70% savings for dev/staging
3. **S3 Lifecycle Policies**: 60% savings on storage
4. **Resource Scheduling**: 60% savings on dev environments
5. **Right-sizing**: 20-30% savings on over-provisioned resources

## 🔧 Deployment Workflow

### Phase 1: Foundation (Day 1)
```bash
# 1. Setup state management
cd state-management && terraform apply

# 2. Deploy VPC and networking
cd terraform && terraform apply -target=aws_vpc.main

# 3. Security setup
terraform apply -target=aws_security_group.web_servers
```

### Phase 2: Core Infrastructure (Day 2)
```bash
# 1. Deploy application infrastructure
terraform apply -target=aws_launch_template.app_template
terraform apply -target=aws_autoscaling_group.app_asg

# 2. Deploy database
terraform apply -target=aws_db_instance.flipkart_mysql_primary
```

### Phase 3: Configuration (Day 3)
```bash
# 1. Configure web servers
ansible-playbook -i inventory ansible/01_web_server_setup.yml

# 2. Setup database
ansible-playbook -i inventory ansible/02_mysql_database_setup.yml
```

### Phase 4: Testing & Optimization (Day 4)
```bash
# 1. Run infrastructure tests
cd testing && go test -v

# 2. Cost optimization analysis
python cost-optimization/01_cost_optimization_setup.py
```

## 🏥 Health Checks और Monitoring

### Application Health Checks
- **ALB Health Check**: `/health` endpoint
- **Response Time**: < 2 seconds
- **Frequency**: Every 30 seconds
- **Healthy Threshold**: 2 consecutive successes

### Database Monitoring
- **CPU Utilization**: < 80% average
- **Connection Count**: < 80% of max_connections
- **Slow Query Log**: Queries > 2 seconds
- **Backup Status**: Daily automated backups

### Infrastructure Monitoring
- **EC2 Metrics**: CPU, Memory, Network, Disk
- **RDS Metrics**: Performance Insights enabled
- **VPC Flow Logs**: Security monitoring
- **CloudWatch Alarms**: 15+ configured alarms

## 🔒 Security Best Practices

### Network Security
- **VPC**: Private subnets for application and database
- **Security Groups**: Least privilege access
- **NACLs**: Additional layer of security
- **WAF**: Protection against common attacks

### Access Control
- **IAM Roles**: Least privilege principle
- **MFA**: Multi-factor authentication required
- **SSH Keys**: No password authentication
- **Bastion Host**: Secure access to private resources

### Data Protection
- **Encryption at Rest**: All databases and storage
- **Encryption in Transit**: TLS 1.2+ everywhere
- **Secrets Management**: AWS Secrets Manager
- **Backup Encryption**: All backups encrypted

## 🚨 Troubleshooting Guide

### Common Issues

1. **Terraform State Lock**
```bash
# If state is locked
terraform force-unlock <LOCK_ID>
```

2. **Ansible SSH Issues**
```bash
# Check SSH connectivity
ansible all -i inventory -m ping
```

3. **Database Connection Issues**
```bash
# Test database connectivity
mysql -h <RDS_ENDPOINT> -u flipkart_admin -p
```

4. **Application Health Check Failures**
```bash
# Check application logs
sudo journalctl -u flipkart-app -f
```

### Performance Issues

1. **High CPU on EC2**
   - Check Auto Scaling policies
   - Review application metrics
   - Consider larger instance types

2. **Database Slow Queries**
   - Check Performance Insights
   - Review slow query log
   - Optimize problematic queries

3. **High Network Latency**
   - Check VPC configuration
   - Review security group rules
   - Monitor CloudWatch metrics

## 📞 Support और Next Steps

### Getting Help
- **Documentation**: Check README files in each directory
- **Logs**: All components have comprehensive logging
- **Monitoring**: CloudWatch dashboards available
- **Alerts**: Configure SNS notifications for critical issues

### Next Steps
1. **Customize**: Modify examples for your specific use case
2. **Scale**: Add more environments or regions
3. **Optimize**: Run cost optimization analysis monthly
4. **Monitor**: Set up comprehensive monitoring and alerting
5. **Backup**: Ensure backup and disaster recovery plans

### Contributing
1. Fork the repository
2. Create feature branch
3. Test changes thoroughly
4. Submit pull request
5. Follow review process

## 🎯 Production Readiness Checklist

- [ ] VPC and networking configured
- [ ] Security groups with least privilege
- [ ] IAM roles and policies setup
- [ ] Database with backup and monitoring
- [ ] Application deployment automated
- [ ] Load balancer health checks working
- [ ] Auto scaling policies configured
- [ ] Monitoring and alerting setup
- [ ] Cost optimization implemented
- [ ] Infrastructure testing automated
- [ ] Documentation updated
- [ ] Team training completed

---

**Remember**: Infrastructure as Code जैसे Mumbai की local train system है - systematic, reliable, और predictable होना चाहिए। हमेशा security को priority दें और cost optimization को भूलें नहीं!

**Happy Infrastructure Coding!** 🚀
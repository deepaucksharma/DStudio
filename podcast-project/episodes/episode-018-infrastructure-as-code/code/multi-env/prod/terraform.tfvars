# Production Environment Configuration
# यह file production environment के लिए specific values define करती है
# High availability, security, और performance के लिए optimized

# Basic Configuration
environment  = "prod"
project_name = "flipkart"
region      = "ap-south-1"  # Mumbai region for Indian customers

# Network Configuration (production-grade)
vpc_cidr            = "10.0.0.0/16"  # Standard production CIDR
availability_zones  = 3              # Full 3 AZs for high availability
enable_nat_gateway  = true
single_nat_gateway  = false          # Multiple NATs for high availability

# Compute Configuration (production instances)
instance_types = {
  web     = "t3.large"    # Sufficient for production web load
  app     = "t3.xlarge"   # Larger for application processing
  worker  = "t3.large"    # Background job processing
  bastion = "t3.micro"    # Minimal for bastion host
}

auto_scaling_config = {
  min_size         = 3   # Always maintain 3 instances minimum
  max_size         = 20  # Scale up to 20 during peak traffic
  desired_capacity = 5   # Normal production capacity
}

# Database Configuration (production-grade)
database_config = {
  engine                  = "mysql"
  engine_version         = "8.0.35"
  instance_class         = "db.r6g.xlarge"   # Production database instance
  allocated_storage      = 500               # 500GB initial storage
  max_allocated_storage  = 5000              # Auto-scale up to 5TB
  backup_retention_period = 30               # 30 days backup retention
  multi_az              = true               # Multi-AZ for high availability
  storage_encrypted     = true               # Encryption mandatory
}

enable_read_replica = true  # Read replica for read scaling

# Monitoring and Logging (comprehensive)
enable_detailed_monitoring = true  # Detailed monitoring for production
log_retention_days        = 90     # 90 days log retention
enable_vpc_flow_logs      = true   # VPC flow logs for security

# Security Configuration (strict)
allowed_cidr_blocks = [
  "203.192.XXX.XXX/32",  # Office IP (replace with actual)
  "49.32.XXX.XXX/32"     # Backup office IP
]

enable_ssl_everywhere     = true   # SSL everywhere in production
kms_key_deletion_window  = 30      # Maximum deletion window

# Cost Optimization (balanced for production)
enable_spot_instances    = false   # No spot instances in production
spot_instance_percentage = 0       # 0% spot instances

resource_scheduling = {
  enabled    = false  # 24x7 availability for production
  start_time = ""
  stop_time  = ""
}

# Backup Configuration (comprehensive)
backup_config = {
  enabled                = true
  backup_window         = "03:00-04:00"  # Low traffic time (IST: 8:30-9:30 AM)
  maintenance_window    = "sun:04:00-sun:05:00"  # Sunday maintenance
  retention_period      = 30             # 30 days backup retention
  cross_region_backup   = true           # Cross-region backup for DR
}

# Notification Configuration (comprehensive)
notification_config = {
  enabled               = true
  email_addresses       = [
    "platform-team@flipkart.com",
    "devops@flipkart.com",
    "sre@flipkart.com"
  ]
  slack_webhook_url     = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
  pagerduty_service_key = "your-pagerduty-service-key"
}

# Feature Flags (all production features enabled)
feature_flags = {
  enable_cdn               = true   # CloudFront CDN for performance
  enable_waf              = true   # WAF for security
  enable_elasticsearch    = true   # Search functionality
  enable_redis_cluster    = true   # Redis cluster for caching
  enable_api_gateway      = true   # API Gateway for management
  enable_lambda_functions = true   # Serverless functions
}

# Common Tags
common_tags = {
  Project     = "flipkart"
  Environment = "production"
  ManagedBy   = "terraform"
  Owner       = "platform-team"
  CostCenter  = "engineering"
  Purpose     = "production-workload"
  Schedule    = "24x7"
  Criticality = "high"
}

# Compliance Configuration (full compliance)
compliance_config = {
  enable_config_rules  = true   # AWS Config rules
  enable_cloudtrail   = true   # CloudTrail for audit
  enable_guardduty    = true   # GuardDuty for threat detection
  enable_security_hub = true   # Security Hub for compliance
  data_classification = "sensitive"
}

# Indian Business Configuration
indian_business_config = {
  data_residency_required = true   # Data must stay in India
  business_hours_ist     = "06:00-24:00"  # Extended business hours
  festival_schedule      = [
    "2024-03-14",  # Holi
    "2024-08-15",  # Independence Day  
    "2024-10-02",  # Gandhi Jayanti
    "2024-10-24",  # Dussehra
    "2024-11-12",  # Diwali
    "2024-12-25"   # Christmas
  ]
  gstin_number          = "29ABCDE1234F1Z5"  # Sample GSTIN
  pan_number            = "ABCDE1234F"       # Sample PAN
}

# Performance Configuration (optimized for production)
performance_config = {
  cpu_target_utilization    = 60   # Conservative for production
  memory_target_utilization = 70   # Conservative for production
  disk_iops_baseline       = 10000 # High IOPS for production
  network_performance      = "enhanced"  # Enhanced networking
}

# Disaster Recovery (full DR setup)
dr_config = {
  enabled             = true
  backup_region      = "ap-southeast-1"  # Singapore as DR region
  rpo_hours          = 1                 # 1 hour RPO
  rto_hours          = 2                 # 2 hour RTO
  automated_failover = false             # Manual failover for control
}

# Production Security Settings
security_config = {
  enable_encryption_at_rest  = true
  enable_encryption_in_transit = true
  enforce_ssl               = true
  min_tls_version          = "1.2"
  enable_secrets_manager   = true
  rotate_secrets_days      = 90
  enable_iam_access_analyzer = true
}

# Production Networking
prod_networking = {
  enable_public_access  = false  # No direct public access
  enable_private_subnets = true
  enable_vpc_endpoints  = true   # VPC endpoints for AWS services
  enable_direct_connect = false  # Can be enabled if needed
  enable_transit_gateway = false # For multi-VPC connectivity
}

# Production Logging
prod_logging = {
  log_level            = "INFO"   # Production log level
  enable_query_logging = false    # Disable query logging for performance
  enable_access_logs   = true
  enable_error_tracking = true
  log_sampling_rate    = 10       # Sample 10% of logs
  enable_log_shipping  = true     # Ship logs to central location
}

# Caching Configuration (production Redis cluster)
caching_config = {
  enable_redis         = true
  redis_instance_type  = "cache.r6g.large"    # Production Redis instance
  enable_memcached     = false
  cache_ttl_seconds    = 3600                  # 1 hour TTL
  enable_cluster_mode  = true                  # Redis cluster mode
  num_cache_nodes      = 3                     # 3-node cluster
}

# Search Configuration (production Elasticsearch)
search_config = {
  enable_elasticsearch = true
  instance_type       = "t3.medium.elasticsearch"
  instance_count      = 3                      # 3-node cluster
  dedicated_master    = true
  master_instance_type = "t3.small.elasticsearch"
  master_instance_count = 3
}

# File Storage Configuration
storage_config = {
  enable_s3           = true
  s3_storage_class    = "INTELLIGENT_TIERING"  # Cost optimization
  enable_cloudfront   = true                   # CDN for performance
  cloudfront_price_class = "PriceClass_All"    # Global distribution
}

# API Configuration (production API limits)
api_config = {
  rate_limit_per_minute = 100     # Conservative rate limiting
  enable_cors           = true
  cors_origins          = [
    "https://flipkart.com",
    "https://www.flipkart.com",
    "https://m.flipkart.com"
  ]
  api_version          = "v1"
  enable_api_keys      = true
}

# Queue Configuration (production SQS)
queue_config = {
  enable_sqs          = true
  enable_redis_queue  = false     # Use SQS for production reliability
  queue_workers       = 5         # Multiple workers
  dead_letter_queue   = true      # DLQ for failed messages
}

# Email Configuration (production)
email_config = {
  provider            = "ses"     # Amazon SES for production
  enable_email_sending = true
  bounce_handling     = true
  complaint_handling  = true
  enable_dkim         = true
}

# Payment Configuration (production)
payment_config = {
  environment         = "production"
  enable_test_payments = false
  payment_providers   = [
    "razorpay",
    "paytm", 
    "phonepe",
    "googlepay",
    "upi"
  ]
  enable_payment_retry = true
  max_retry_attempts  = 3
}

# Analytics Configuration (full analytics)
analytics_config = {
  enable_google_analytics = true
  enable_mixpanel        = true
  enable_custom_events   = true
  event_sampling_rate    = 100    # Track all events in production
  enable_realtime_analytics = true
}

# CDN Configuration
cdn_config = {
  enable_cloudfront     = true
  price_class          = "PriceClass_All"
  compress             = true
  default_ttl          = 86400    # 24 hours
  max_ttl              = 31536000 # 1 year
  viewer_protocol_policy = "redirect-to-https"
}

# WAF Configuration
waf_config = {
  enable_waf           = true
  enable_rate_limiting = true
  rate_limit           = 2000     # Requests per 5 minutes
  enable_geo_blocking  = false    # Don't block countries for e-commerce
  enable_ip_reputation = true
  enable_known_bad_inputs = true
}

# Auto Scaling Configuration (production traffic patterns)
scaling_config = {
  # Scale up during Indian business hours
  business_hours_min    = 5
  business_hours_max    = 15
  business_hours_desired = 8
  
  # Scale down during night hours
  night_hours_min      = 3
  night_hours_max      = 10
  night_hours_desired  = 5
  
  # Special scaling for sales/festivals
  festival_min         = 10
  festival_max         = 50
  festival_desired     = 20
}

# Database Performance (production tuning)
database_performance = {
  connection_pool_size = 100
  query_cache_size    = "256M"
  innodb_buffer_pool  = "75%"     # 75% of available memory
  slow_query_log      = true
  slow_query_time     = 1         # Log queries > 1 second
}

# Maintenance Windows (Indian timezone)
maintenance_config = {
  # Database maintenance: Sunday 3:30-4:30 AM IST (low traffic)
  database_window     = "sun:22:00-sun:23:00"  # UTC time
  
  # Application maintenance: Sunday 4:30-5:30 AM IST
  application_window  = "sun:23:00-mon:00:00"  # UTC time
  
  # OS updates: First Sunday of month 2:30-3:30 AM IST
  os_update_window   = "sun:21:00-sun:22:00"   # UTC time
}

# Alerting Thresholds (production)
alerting_thresholds = {
  cpu_warning         = 70
  cpu_critical        = 85
  memory_warning      = 75
  memory_critical     = 90
  disk_warning        = 80
  disk_critical       = 90
  response_time_warning = 2000   # 2 seconds
  response_time_critical = 5000  # 5 seconds
  error_rate_warning  = 1        # 1%
  error_rate_critical = 5        # 5%
}

# Business Metrics Monitoring
business_metrics = {
  track_revenue       = true
  track_conversions   = true
  track_user_journey  = true
  track_cart_abandonment = true
  track_payment_failures = true
  track_search_queries = true
}

# Runbook Configuration
runbook_config = {
  enable_automated_remediation = false  # Manual intervention for production
  escalation_policy = [
    "level1-oncall@flipkart.com",
    "level2-oncall@flipkart.com", 
    "engineering-manager@flipkart.com"
  ]
  incident_response_time = 15  # 15 minutes response time
}
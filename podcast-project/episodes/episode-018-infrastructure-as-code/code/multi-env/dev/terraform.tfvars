# Development Environment Configuration
# यह file development environment के लिए specific values define करती है
# Cost optimization और quick iterations के लिए optimized

# Basic Configuration
environment  = "dev"
project_name = "flipkart"
region      = "ap-south-1"  # Mumbai region

# Network Configuration (smaller for cost optimization)
vpc_cidr            = "10.1.0.0/16"  # Different CIDR for dev
availability_zones  = 2              # Only 2 AZs for cost saving
enable_nat_gateway  = true
single_nat_gateway  = true           # Single NAT for cost optimization

# Compute Configuration (smaller instances)
instance_types = {
  web     = "t3.micro"   # Free tier eligible
  app     = "t3.small"   # Minimal for development
  worker  = "t3.micro"   # Free tier eligible
  bastion = "t3.nano"    # Smallest for bastion
}

auto_scaling_config = {
  min_size         = 1  # Minimal instances
  max_size         = 3  # Limited scaling
  desired_capacity = 1  # Start with single instance
}

# Database Configuration (cost optimized)
database_config = {
  engine                  = "mysql"
  engine_version         = "8.0.35"
  instance_class         = "db.t3.micro"  # Free tier eligible
  allocated_storage      = 20             # Minimal storage
  max_allocated_storage  = 100            # Limited auto-scaling
  backup_retention_period = 1             # Minimal backup retention
  multi_az              = false           # Single AZ for cost saving
  storage_encrypted     = false           # Disable encryption for dev
}

enable_read_replica = false  # No read replica for dev

# Monitoring and Logging (basic)
enable_detailed_monitoring = false  # Basic monitoring for cost saving
log_retention_days        = 7       # Short retention for dev
enable_vpc_flow_logs      = false   # Disable for cost saving

# Security Configuration (relaxed for development)
allowed_cidr_blocks = [
  "203.192.XXX.XXX/32",  # Office IP (replace with actual)
  "10.1.0.0/16"          # VPC CIDR for internal access
]

enable_ssl_everywhere     = false  # Relaxed for development
kms_key_deletion_window  = 7       # Shorter deletion window

# Cost Optimization (aggressive for dev)
enable_spot_instances    = true   # Use spot instances
spot_instance_percentage = 70     # 70% spot instances

resource_scheduling = {
  enabled    = true
  start_time = "0 8 * * MON-FRI"   # 8 AM IST on weekdays
  stop_time  = "0 20 * * MON-FRI"  # 8 PM IST on weekdays
}

# Backup Configuration (minimal)
backup_config = {
  enabled                = true
  backup_window         = "03:00-04:00"  # Low usage time
  maintenance_window    = "sun:04:00-sun:05:00"
  retention_period      = 1              # 1 day retention only
  cross_region_backup   = false          # No cross-region backup
}

# Notification Configuration (basic)
notification_config = {
  enabled               = true
  email_addresses       = ["dev-team@flipkart.com"]
  slack_webhook_url     = ""  # Configure if needed
  pagerduty_service_key = ""  # No PagerDuty for dev
}

# Feature Flags (minimal features for dev)
feature_flags = {
  enable_cdn               = false  # No CDN for dev
  enable_waf              = false  # No WAF for dev
  enable_elasticsearch    = false  # No ES for dev
  enable_redis_cluster    = false  # Simple Redis instead
  enable_api_gateway      = false  # Direct access for dev
  enable_lambda_functions = false  # No serverless for dev
}

# Common Tags
common_tags = {
  Project     = "flipkart"
  Environment = "development"
  ManagedBy   = "terraform"
  Owner       = "dev-team"
  CostCenter  = "engineering"
  Purpose     = "development-testing"
  Schedule    = "business-hours-only"
}

# Compliance Configuration (relaxed for dev)
compliance_config = {
  enable_config_rules  = false  # No Config rules for dev
  enable_cloudtrail   = false  # No CloudTrail for dev
  enable_guardduty    = false  # No GuardDuty for dev
  enable_security_hub = false  # No Security Hub for dev
  data_classification = "development"
}

# Indian Business Configuration
indian_business_config = {
  data_residency_required = false  # Relaxed for dev
  business_hours_ist     = "09:00-18:00"  # Standard business hours
  festival_schedule      = []             # No special schedule for dev
  gstin_number          = ""              # Not required for dev
  pan_number            = ""              # Not required for dev
}

# Performance Configuration (relaxed)
performance_config = {
  cpu_target_utilization    = 80  # Higher threshold for dev
  memory_target_utilization = 85  # Higher threshold for dev
  disk_iops_baseline       = 1000 # Lower IOPS for dev
  network_performance      = "standard"  # Standard networking
}

# Disaster Recovery (disabled for dev)
dr_config = {
  enabled             = false
  backup_region      = ""
  rpo_hours          = 24
  rto_hours          = 4
  automated_failover = false
}

# Development-specific variables
developer_access = {
  enable_ssh_access     = true
  enable_debug_mode     = true
  enable_hot_reload     = true
  enable_development_tools = true
}

# Testing Configuration
testing_config = {
  enable_test_data      = true
  reset_data_daily      = true
  mock_external_services = true
  enable_chaos_testing  = false  # Can be enabled for resilience testing
}

# Development Database Seeds
database_seeds = {
  enable_sample_data    = true
  user_count           = 100
  product_count        = 1000
  order_count          = 500
  category_count       = 20
}

# CI/CD Configuration
cicd_config = {
  enable_auto_deploy    = true
  deploy_on_pr_merge   = true
  run_tests_on_deploy  = true
  enable_rollback      = true
  notification_channel = "slack"
}

# Development Tools
dev_tools = {
  enable_swagger_ui     = true
  enable_admin_panel    = true
  enable_debug_toolbar  = true
  enable_profiler       = true
  enable_log_viewer     = true
}

# Resource Limits (for cost control)
resource_limits = {
  max_ec2_instances     = 5
  max_rds_instances     = 2
  max_storage_gb        = 100
  max_monthly_cost_usd  = 200
}

# Development Networking
dev_networking = {
  enable_public_access  = true   # Allow public access for testing
  whitelist_ips = [
    "203.192.XXX.XXX/32",        # Office IP
    "49.32.XXX.XXX/32"           # Home IP (example)
  ]
  enable_vpn_access     = false  # No VPN required for dev
}

# Logging Configuration (development specific)
dev_logging = {
  log_level            = "DEBUG"
  enable_query_logging = true
  enable_access_logs   = true
  enable_error_tracking = true
  log_sampling_rate    = 100    # Log everything in dev
}

# Caching Configuration (simple for dev)
caching_config = {
  enable_redis         = true
  redis_instance_type  = "cache.t3.micro"  # Smallest instance
  enable_memcached     = false
  cache_ttl_seconds    = 300               # 5 minutes TTL
}

# Search Configuration (if needed)
search_config = {
  enable_elasticsearch = false
  enable_opensearch   = false
  enable_simple_search = true  # File-based search for dev
}

# File Storage Configuration
storage_config = {
  enable_s3           = true
  s3_storage_class    = "STANDARD"  # No lifecycle rules for dev
  enable_cloudfront   = false      # No CDN for dev
  local_storage_path  = "/tmp/uploads"  # Local storage for dev
}

# API Configuration
api_config = {
  rate_limit_per_minute = 1000    # Higher limits for dev testing
  enable_cors           = true
  cors_origins          = ["*"]   # Allow all origins for dev
  api_version          = "v1"
}

# Queue Configuration (simple for dev)
queue_config = {
  enable_sqs          = false     # Use in-memory queues for dev
  enable_redis_queue  = true
  queue_workers       = 1         # Single worker for dev
}

# Email Configuration (dev/test)
email_config = {
  provider            = "smtp"    # Local SMTP for dev
  enable_email_sending = false    # Disable actual sending
  log_emails_to_file  = true     # Log emails instead of sending
}

# Payment Configuration (sandbox)
payment_config = {
  environment         = "sandbox"
  enable_test_payments = true
  payment_providers   = ["razorpay_test", "paytm_test"]
}

# Analytics Configuration (minimal)
analytics_config = {
  enable_google_analytics = false
  enable_mixpanel        = false
  enable_custom_events   = true
  event_sampling_rate    = 100    # Track all events in dev
}

# Feature Toggles for Development
feature_toggles = {
  new_checkout_flow     = true   # Test new features in dev
  experimental_ui       = true
  beta_features         = true
  legacy_compatibility  = false
}
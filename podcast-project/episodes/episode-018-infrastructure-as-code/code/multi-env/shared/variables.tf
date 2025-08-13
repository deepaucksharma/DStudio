# Example 9: Multi-Environment Infrastructure Variables
# यह file सभी environments के लिए common variables define करती है
# Flipkart के different environments (dev, staging, prod) के लिए

# Environment Configuration
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "flipkart"
  
  validation {
    condition     = length(var.project_name) > 0 && length(var.project_name) <= 20
    error_message = "Project name must be between 1 and 20 characters."
  }
}

variable "region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-south-1"  # Mumbai region
  
  validation {
    condition = contains([
      "ap-south-1",     # Mumbai
      "ap-southeast-1", # Singapore  
      "us-east-1",      # Virginia
      "eu-west-1"       # Ireland
    ], var.region)
    error_message = "Region must be one of the supported regions."
  }
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "availability_zones" {
  description = "Number of availability zones to use"
  type        = number
  default     = 3
  
  validation {
    condition     = var.availability_zones >= 2 && var.availability_zones <= 3
    error_message = "Must use between 2 and 3 availability zones for high availability."
  }
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway for cost optimization"
  type        = bool
  default     = false
}

# Compute Configuration
variable "instance_types" {
  description = "Instance types for different workloads"
  type = object({
    web         = string
    app         = string
    worker      = string
    bastion     = string
  })
  
  default = {
    web     = "t3.medium"
    app     = "t3.large" 
    worker  = "t3.medium"
    bastion = "t3.micro"
  }
}

variable "auto_scaling_config" {
  description = "Auto scaling configuration"
  type = object({
    min_size         = number
    max_size         = number
    desired_capacity = number
  })
  
  default = {
    min_size         = 2
    max_size         = 10
    desired_capacity = 3
  }
}

# Database Configuration
variable "database_config" {
  description = "Database configuration"
  type = object({
    engine               = string
    engine_version       = string
    instance_class       = string
    allocated_storage    = number
    max_allocated_storage = number
    backup_retention_period = number
    multi_az            = bool
    storage_encrypted   = bool
  })
  
  default = {
    engine                  = "mysql"
    engine_version         = "8.0.35"
    instance_class         = "db.t3.medium"
    allocated_storage      = 100
    max_allocated_storage  = 1000
    backup_retention_period = 7
    multi_az              = true
    storage_encrypted     = true
  }
}

variable "enable_read_replica" {
  description = "Enable RDS read replica"
  type        = bool
  default     = true
}

# Monitoring and Logging
variable "enable_detailed_monitoring" {
  description = "Enable detailed CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
  
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.log_retention_days)
    error_message = "Log retention must be a valid CloudWatch retention period."
  }
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = true
}

# Security Configuration
variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = []
  
  validation {
    condition = alltrue([
      for cidr in var.allowed_cidr_blocks : can(cidrhost(cidr, 0))
    ])
    error_message = "All CIDR blocks must be valid IPv4 CIDR blocks."
  }
}

variable "enable_ssl_everywhere" {
  description = "Enable SSL/TLS for all communications"
  type        = bool
  default     = true
}

variable "kms_key_deletion_window" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 30
  
  validation {
    condition     = var.kms_key_deletion_window >= 7 && var.kms_key_deletion_window <= 30
    error_message = "KMS key deletion window must be between 7 and 30 days."
  }
}

# Cost Optimization
variable "enable_spot_instances" {
  description = "Enable spot instances for cost optimization"
  type        = bool
  default     = false
}

variable "spot_instance_percentage" {
  description = "Percentage of spot instances in ASG"
  type        = number
  default     = 50
  
  validation {
    condition     = var.spot_instance_percentage >= 0 && var.spot_instance_percentage <= 100
    error_message = "Spot instance percentage must be between 0 and 100."
  }
}

variable "resource_scheduling" {
  description = "Enable resource scheduling for cost optimization"
  type = object({
    enabled    = bool
    start_time = string  # Cron expression
    stop_time  = string  # Cron expression
  })
  
  default = {
    enabled    = false
    start_time = "0 8 * * MON-FRI"   # 8 AM on weekdays
    stop_time  = "0 20 * * MON-FRI"  # 8 PM on weekdays
  }
}

# Backup Configuration
variable "backup_config" {
  description = "Backup configuration"
  type = object({
    enabled                = bool
    backup_window         = string
    maintenance_window    = string
    retention_period      = number
    cross_region_backup   = bool
  })
  
  default = {
    enabled                = true
    backup_window         = "03:00-04:00"  # IST: 8:30-9:30 AM
    maintenance_window    = "sun:04:00-sun:05:00"  # IST: Sunday 9:30-10:30 AM
    retention_period      = 7
    cross_region_backup   = false
  }
}

# Notification Configuration
variable "notification_config" {
  description = "Notification configuration"
  type = object({
    enabled           = bool
    email_addresses   = list(string)
    slack_webhook_url = string
    pagerduty_service_key = string
  })
  
  default = {
    enabled               = true
    email_addresses       = []
    slack_webhook_url     = ""
    pagerduty_service_key = ""
  }
}

# Feature Flags
variable "feature_flags" {
  description = "Feature flags for optional components"
  type = object({
    enable_cdn               = bool
    enable_waf              = bool
    enable_elasticsearch    = bool
    enable_redis_cluster    = bool
    enable_api_gateway      = bool
    enable_lambda_functions = bool
  })
  
  default = {
    enable_cdn               = true
    enable_waf              = true
    enable_elasticsearch    = false
    enable_redis_cluster    = true
    enable_api_gateway      = true
    enable_lambda_functions = false
  }
}

# Environment-specific Overrides
variable "environment_config" {
  description = "Environment-specific configuration overrides"
  type = map(object({
    instance_count        = number
    instance_type        = string
    enable_multi_az      = bool
    backup_retention     = number
    monitoring_level     = string
  }))
  
  default = {
    dev = {
      instance_count    = 1
      instance_type    = "t3.micro"
      enable_multi_az  = false
      backup_retention = 3
      monitoring_level = "basic"
    }
    staging = {
      instance_count    = 2
      instance_type    = "t3.small"
      enable_multi_az  = true
      backup_retention = 5
      monitoring_level = "detailed"
    }
    prod = {
      instance_count    = 3
      instance_type    = "t3.medium"
      enable_multi_az  = true
      backup_retention = 7
      monitoring_level = "detailed"
    }
  }
}

# Tagging Strategy
variable "common_tags" {
  description = "Common tags applied to all resources"
  type        = map(string)
  default = {
    Project    = "flipkart"
    ManagedBy  = "terraform"
    Owner      = "platform-team"
    CostCenter = "engineering"
  }
}

variable "environment_tags" {
  description = "Environment-specific tags"
  type        = map(map(string))
  
  default = {
    dev = {
      Environment = "development"
      Purpose     = "development-testing"
      Schedule    = "business-hours-only"
      Backup      = "basic"
    }
    staging = {
      Environment = "staging"
      Purpose     = "pre-production-testing"
      Schedule    = "business-hours-extended"
      Backup      = "standard"
    }
    prod = {
      Environment = "production"
      Purpose     = "production-workload"
      Schedule    = "24x7"
      Backup      = "comprehensive"
    }
  }
}

# Compliance and Governance
variable "compliance_config" {
  description = "Compliance and governance configuration"
  type = object({
    enable_config_rules     = bool
    enable_cloudtrail      = bool
    enable_guardduty       = bool
    enable_security_hub    = bool
    data_classification    = string
  })
  
  default = {
    enable_config_rules  = true
    enable_cloudtrail   = true
    enable_guardduty    = true
    enable_security_hub = true
    data_classification = "internal"
  }
}

# Indian Business Context
variable "indian_business_config" {
  description = "Configuration specific to Indian business requirements"
  type = object({
    data_residency_required = bool
    business_hours_ist     = string
    festival_schedule      = list(string)
    gstin_number          = string
    pan_number            = string
  })
  
  default = {
    data_residency_required = true
    business_hours_ist     = "09:00-21:00"  # 9 AM to 9 PM IST
    festival_schedule      = ["2024-03-14", "2024-08-15", "2024-10-02"]  # Holi, Independence Day, Gandhi Jayanti
    gstin_number          = ""
    pan_number            = ""
  }
}

# Performance Configuration
variable "performance_config" {
  description = "Performance tuning configuration"
  type = object({
    cpu_target_utilization    = number
    memory_target_utilization = number
    disk_iops_baseline       = number
    network_performance      = string
  })
  
  default = {
    cpu_target_utilization    = 70
    memory_target_utilization = 80
    disk_iops_baseline       = 3000
    network_performance      = "enhanced"
  }
}

# Disaster Recovery Configuration
variable "dr_config" {
  description = "Disaster recovery configuration"
  type = object({
    enabled              = bool
    backup_region       = string
    rpo_hours           = number  # Recovery Point Objective
    rto_hours           = number  # Recovery Time Objective
    automated_failover  = bool
  })
  
  default = {
    enabled             = false
    backup_region      = "ap-southeast-1"  # Singapore as DR region
    rpo_hours          = 4
    rto_hours          = 2
    automated_failover = false
  }
}

# Local values for derived configurations
locals {
  # Environment-specific naming
  name_prefix = "${var.project_name}-${var.environment}"
  
  # Derived network configuration
  public_subnet_cidrs = [
    for i in range(var.availability_zones) : 
    cidrsubnet(var.vpc_cidr, 8, i + 1)
  ]
  
  private_subnet_cidrs = [
    for i in range(var.availability_zones) : 
    cidrsubnet(var.vpc_cidr, 8, i + 10)
  ]
  
  database_subnet_cidrs = [
    for i in range(var.availability_zones) : 
    cidrsubnet(var.vpc_cidr, 8, i + 20)
  ]
  
  # Environment-specific configuration
  env_config = var.environment_config[var.environment]
  
  # Combined tags
  tags = merge(
    var.common_tags,
    var.environment_tags[var.environment],
    {
      Environment = var.environment
      Region      = var.region
      Terraform   = "true"
    }
  )
  
  # Cost optimization settings
  use_spot_instances = var.environment != "prod" ? var.enable_spot_instances : false
  
  # Monitoring level
  monitoring_enabled = contains(["staging", "prod"], var.environment) || var.enable_detailed_monitoring
  
  # Security settings
  encryption_enabled = var.environment == "prod" || var.enable_ssl_everywhere
  
  # Resource naming convention
  resource_names = {
    vpc                = "${local.name_prefix}-vpc"
    public_subnet     = "${local.name_prefix}-public"
    private_subnet    = "${local.name_prefix}-private"
    database_subnet   = "${local.name_prefix}-database"
    internet_gateway  = "${local.name_prefix}-igw"
    nat_gateway       = "${local.name_prefix}-nat"
    security_group    = "${local.name_prefix}-sg"
    load_balancer     = "${local.name_prefix}-alb"
    auto_scaling      = "${local.name_prefix}-asg"
    database          = "${local.name_prefix}-db"
    cache             = "${local.name_prefix}-cache"
  }
}
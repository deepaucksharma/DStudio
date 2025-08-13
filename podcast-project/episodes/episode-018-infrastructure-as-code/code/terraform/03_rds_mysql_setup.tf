# Example 6: RDS MySQL Setup with High Availability
# यह example production-ready MySQL RDS instance setup करता है
# Flipkart के database requirements के साथ

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

# Random password generation for database
resource "random_password" "db_password" {
  length  = 16
  special = true
  
  # Avoid characters that cause issues in URLs or scripts
  override_special = "!@#$%^&*()-_=+[]{}"
  
  lifecycle {
    ignore_changes = [length, special, override_special]
  }
}

# Store password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "flipkart/database/master-password"
  description             = "Master password for Flipkart RDS instances"
  recovery_window_in_days = 7  # Cost optimization - shorter recovery window
  
  tags = {
    Name        = "flipkart-db-master-password"
    Environment = "production"
    Purpose     = "RDS master password"
    Application = "flipkart"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = "flipkart_admin"
    password = random_password.db_password.result
  })
}

# DB Subnet Group (uses subnets from VPC example)
resource "aws_db_subnet_group" "flipkart_db" {
  name       = "flipkart-db-subnet-group"
  subnet_ids = aws_subnet.database[*].id  # Database subnets from VPC example
  
  tags = {
    Name        = "flipkart-db-subnet-group"
    Environment = "production"
    Purpose     = "RDS subnet group for database isolation"
  }
}

# Security Group for RDS
resource "aws_security_group" "rds_mysql" {
  name_prefix = "flipkart-rds-mysql-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for Flipkart MySQL RDS instances"
  
  # MySQL port from application servers only
  ingress {
    description     = "MySQL from application servers"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.web_servers.id]  # From web servers SG
  }
  
  # MySQL port from private subnets (for admin access)
  ingress {
    description = "MySQL from private subnets"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [for subnet in aws_subnet.private : subnet.cidr_block]
  }
  
  # No outbound rules needed for RDS
  egress {
    description = "No outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name        = "flipkart-rds-mysql-sg"
    Environment = "production"
    Purpose     = "Security group for MySQL RDS instances"
  }
}

# Parameter Group for MySQL optimization
resource "aws_db_parameter_group" "flipkart_mysql" {
  family = "mysql8.0"
  name   = "flipkart-mysql80-params"
  
  # InnoDB optimizations for Indian e-commerce workload
  parameter {
    name  = "innodb_buffer_pool_size"
    value = "{DBInstanceClassMemory*3/4}"  # Use 75% of available memory
  }
  
  parameter {
    name  = "innodb_buffer_pool_instances"
    value = "8"  # Multiple buffer pool instances for better concurrency
  }
  
  parameter {
    name  = "innodb_log_file_size"
    value = "536870912"  # 512MB log files
  }
  
  parameter {
    name  = "innodb_log_buffer_size"
    value = "67108864"  # 64MB log buffer
  }
  
  parameter {
    name  = "innodb_flush_log_at_trx_commit"
    value = "2"  # Better performance for non-critical data
  }
  
  parameter {
    name  = "max_connections"
    value = "1000"  # Support high concurrency
  }
  
  parameter {
    name  = "query_cache_type"
    value = "1"  # Enable query cache
  }
  
  parameter {
    name  = "query_cache_size"
    value = "268435456"  # 256MB query cache
  }
  
  parameter {
    name  = "tmp_table_size"
    value = "134217728"  # 128MB temp table size
  }
  
  parameter {
    name  = "max_heap_table_size"
    value = "134217728"  # 128MB heap table size
  }
  
  parameter {
    name  = "slow_query_log"
    value = "1"  # Enable slow query log
  }
  
  parameter {
    name  = "long_query_time"
    value = "2"  # Log queries taking more than 2 seconds
  }
  
  parameter {
    name  = "binlog_format"
    value = "ROW"  # Better for replication
  }
  
  # Character set for Indian languages
  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }
  
  parameter {
    name  = "collation_server"
    value = "utf8mb4_unicode_ci"
  }
  
  tags = {
    Name        = "flipkart-mysql-parameters"
    Environment = "production"
    Purpose     = "Optimized MySQL parameters for e-commerce workload"
  }
}

# Option Group for additional features
resource "aws_db_option_group" "flipkart_mysql" {
  name                     = "flipkart-mysql80-options"
  option_group_description = "Option group for Flipkart MySQL instances"
  engine_name              = "mysql"
  major_engine_version     = "8.0"
  
  # Enable MariaDB Audit Plugin for compliance
  option {
    option_name = "MARIADB_AUDIT_PLUGIN"
    
    option_settings {
      name  = "SERVER_AUDIT_EVENTS"
      value = "CONNECT,QUERY,TABLE"
    }
    
    option_settings {
      name  = "SERVER_AUDIT_LOGGING"
      value = "ON"
    }
  }
  
  tags = {
    Name        = "flipkart-mysql-options"
    Environment = "production"
    Purpose     = "MySQL options for audit and compliance"
  }
}

# Primary RDS Instance
resource "aws_db_instance" "flipkart_mysql_primary" {
  # Basic Configuration
  identifier = "flipkart-mysql-primary"
  engine     = "mysql"
  engine_version = "8.0.35"  # Latest stable version
  
  # Instance specifications
  instance_class        = "db.t3.medium"  # Start with smaller instance for cost optimization
  allocated_storage     = 100             # 100GB initial storage
  max_allocated_storage = 1000            # Auto-scaling up to 1TB
  storage_type          = "gp3"           # Latest generation storage
  storage_encrypted     = true            # Encryption at rest
  
  # Database configuration
  db_name  = "flipkart_production"
  username = "flipkart_admin"
  password = random_password.db_password.result
  port     = 3306
  
  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.flipkart_db.name
  vpc_security_group_ids = [aws_security_group.rds_mysql.id]
  publicly_accessible    = false  # Security best practice
  
  # Parameter and option groups
  parameter_group_name = aws_db_parameter_group.flipkart_mysql.name
  option_group_name    = aws_db_option_group.flipkart_mysql.name
  
  # Backup configuration
  backup_retention_period = 7     # 7 days backup retention
  backup_window          = "03:00-04:00"  # IST: 8:30-9:30 AM (low traffic time)
  maintenance_window     = "sun:04:00-sun:05:00"  # IST: Sunday 9:30-10:30 AM
  
  # High Availability
  multi_az               = true   # Enable Multi-AZ for high availability
  availability_zone      = null   # Let AWS choose when multi_az is true
  
  # Monitoring
  monitoring_interval = 60  # Enhanced monitoring every minute
  monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring.arn
  
  # Performance Insights
  performance_insights_enabled = true
  performance_insights_retention_period = 7  # 7 days retention for cost optimization
  
  # Logs to export to CloudWatch
  enabled_cloudwatch_logs_exports = ["error", "general", "slow-query"]
  
  # Deletion protection
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "flipkart-mysql-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  
  # Auto minor version upgrade during maintenance window
  auto_minor_version_upgrade = true
  
  # Copy tags to snapshots
  copy_tags_to_snapshot = true
  
  tags = {
    Name        = "flipkart-mysql-primary"
    Environment = "production"
    Purpose     = "Primary MySQL database for Flipkart application"
    Backup      = "enabled"
    Monitoring  = "enhanced"
  }
  
  depends_on = [
    aws_cloudwatch_log_group.rds_logs
  ]
}

# Read Replica for read-heavy workloads
resource "aws_db_instance" "flipkart_mysql_replica" {
  identifier = "flipkart-mysql-replica"
  
  # Replica configuration
  replicate_source_db = aws_db_instance.flipkart_mysql_primary.identifier
  
  # Instance specifications (can be different from primary)
  instance_class = "db.t3.medium"  # Same size for now
  
  # Network configuration
  vpc_security_group_ids = [aws_security_group.rds_mysql.id]
  publicly_accessible    = false
  
  # Monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring.arn
  
  # Performance Insights
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  
  # Auto minor version upgrade
  auto_minor_version_upgrade = true
  
  tags = {
    Name        = "flipkart-mysql-replica"
    Environment = "production"
    Purpose     = "Read replica for Flipkart application"
    Role        = "read-only"
  }
}

# CloudWatch Log Groups for RDS logs
resource "aws_cloudwatch_log_group" "rds_logs" {
  for_each = toset(["error", "general", "slow-query"])
  
  name              = "/aws/rds/instance/flipkart-mysql-primary/${each.key}"
  retention_in_days = 30  # 30 days log retention
  
  tags = {
    Name        = "flipkart-mysql-${each.key}-logs"
    Environment = "production"
    Purpose     = "RDS ${each.key} logs"
  }
}

# IAM Role for Enhanced Monitoring
resource "aws_iam_role" "rds_enhanced_monitoring" {
  name = "rds-monitoring-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name        = "rds-enhanced-monitoring-role"
    Environment = "production"
    Purpose     = "IAM role for RDS enhanced monitoring"
  }
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch Alarms for RDS Monitoring
resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "flipkart-mysql-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors RDS CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.flipkart_mysql_primary.id
  }
  
  tags = {
    Name        = "flipkart-mysql-cpu-alarm"
    Environment = "production"
    Purpose     = "Monitor RDS CPU usage"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_connections_high" {
  alarm_name          = "flipkart-mysql-high-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "800"  # 80% of max_connections
  alarm_description   = "This metric monitors RDS connection count"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.flipkart_mysql_primary.id
  }
  
  tags = {
    Name        = "flipkart-mysql-connections-alarm"
    Environment = "production"
    Purpose     = "Monitor RDS connection count"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_free_storage_low" {
  alarm_name          = "flipkart-mysql-low-storage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "10737418240"  # 10GB in bytes
  alarm_description   = "This metric monitors RDS free storage space"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.flipkart_mysql_primary.id
  }
  
  tags = {
    Name        = "flipkart-mysql-storage-alarm"
    Environment = "production"
    Purpose     = "Monitor RDS free storage"
  }
}

# SNS Topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "flipkart-infrastructure-alerts"
  
  tags = {
    Name        = "flipkart-infrastructure-alerts"
    Environment = "production"
    Purpose     = "SNS topic for infrastructure alerts"
  }
}

# Database connection endpoint configuration
resource "aws_route53_record" "mysql_primary" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "mysql-primary.flipkart.local"
  type    = "CNAME"
  ttl     = 60
  records = [aws_db_instance.flipkart_mysql_primary.address]
}

resource "aws_route53_record" "mysql_replica" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "mysql-replica.flipkart.local"
  type    = "CNAME"
  ttl     = 60
  records = [aws_db_instance.flipkart_mysql_replica.address]
}

# Private hosted zone for internal DNS
resource "aws_route53_zone" "private" {
  name = "flipkart.local"
  
  vpc {
    vpc_id = aws_vpc.main.id
  }
  
  tags = {
    Name        = "flipkart-private-zone"
    Environment = "production"
    Purpose     = "Private DNS zone for internal services"
  }
}

# Outputs
output "rds_primary_endpoint" {
  description = "RDS instance primary endpoint"
  value       = aws_db_instance.flipkart_mysql_primary.endpoint
  sensitive   = true
}

output "rds_replica_endpoint" {
  description = "RDS instance read replica endpoint"
  value       = aws_db_instance.flipkart_mysql_replica.endpoint
  sensitive   = true
}

output "rds_primary_address" {
  description = "RDS instance primary address"
  value       = aws_db_instance.flipkart_mysql_primary.address
  sensitive   = true
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.flipkart_mysql_primary.db_name
}

output "rds_username" {
  description = "RDS master username"
  value       = aws_db_instance.flipkart_mysql_primary.username
  sensitive   = true
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.flipkart_mysql_primary.port
}

output "secrets_manager_secret_arn" {
  description = "ARN of the Secrets Manager secret containing database credentials"
  value       = aws_secretsmanager_secret.db_password.arn
}

# Connection string for application configuration
output "database_connection_info" {
  description = "Database connection information"
  value = {
    primary_endpoint = aws_db_instance.flipkart_mysql_primary.endpoint
    replica_endpoint = aws_db_instance.flipkart_mysql_replica.endpoint
    database_name    = aws_db_instance.flipkart_mysql_primary.db_name
    port            = aws_db_instance.flipkart_mysql_primary.port
    secret_arn      = aws_secretsmanager_secret.db_password.arn
  }
  sensitive = true
}

# Local values for configuration management
locals {
  rds_tags = {
    Environment = "production"
    Project     = "flipkart-infrastructure"
    Component   = "database"
    Backup      = "enabled"
    Monitoring  = "enhanced"
    CreatedBy   = "terraform"
  }
  
  # Database size recommendations based on environment
  db_instance_sizes = {
    development = "db.t3.micro"
    staging     = "db.t3.small"
    production  = "db.t3.medium"
  }
  
  # Backup configurations for different environments
  backup_retention_days = {
    development = 3
    staging     = 5
    production  = 7
  }
}
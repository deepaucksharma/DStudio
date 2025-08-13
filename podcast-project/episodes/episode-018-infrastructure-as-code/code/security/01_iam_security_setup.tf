# Example 10: IAM Security Setup with Least Privilege
# यह example comprehensive IAM security setup करता है
# Flipkart जैसे enterprise applications के लिए

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# IAM Password Policy (enforce strong passwords)
resource "aws_iam_account_password_policy" "strict_policy" {
  minimum_password_length        = 14
  require_lowercase_characters   = true
  require_numbers               = true
  require_uppercase_characters   = true
  require_symbols               = true
  allow_users_to_change_password = true
  max_password_age              = 90   # Rotate every 90 days
  password_reuse_prevention     = 12   # Prevent reuse of last 12 passwords
  hard_expiry                   = false # Allow self-service password reset
}

# KMS Key for encryption
resource "aws_kms_key" "flipkart_main" {
  description             = "Main KMS key for Flipkart infrastructure encryption"
  deletion_window_in_days = 30
  
  # Key policy
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
  
  tags = {
    Name        = "flipkart-main-kms-key"
    Environment = "production"
    Purpose     = "Infrastructure encryption"
  }
}

resource "aws_kms_alias" "flipkart_main" {
  name          = "alias/flipkart-main"
  target_key_id = aws_kms_key.flipkart_main.key_id
}

# IAM Roles for different components

# 1. EC2 Application Role (for web servers)
resource "aws_iam_role" "ec2_application_role" {
  name = "flipkart-ec2-application-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name        = "flipkart-ec2-application-role"
    Purpose     = "Role for EC2 application instances"
    Environment = "production"
  }
}

# EC2 Application Policy (least privilege)
resource "aws_iam_role_policy" "ec2_application_policy" {
  name = "flipkart-ec2-application-policy"
  role = aws_iam_role.ec2_application_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = [
          "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/ec2/flipkart*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = [
          "arn:aws:s3:::flipkart-application-assets/*",
          "arn:aws:s3:::flipkart-configuration/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = [
          "arn:aws:s3:::flipkart-application-logs/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:flipkart/application/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = [
          aws_kms_key.flipkart_main.arn
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_application_profile" {
  name = "flipkart-ec2-application-profile"
  role = aws_iam_role.ec2_application_role.name
}

# 2. RDS Enhanced Monitoring Role
resource "aws_iam_role" "rds_monitoring_role" {
  name = "flipkart-rds-monitoring-role"
  
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
    Name        = "flipkart-rds-monitoring-role"
    Purpose     = "RDS enhanced monitoring"
    Environment = "production"
  }
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# 3. Lambda Execution Role (for automation functions)
resource "aws_iam_role" "lambda_execution_role" {
  name = "flipkart-lambda-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name        = "flipkart-lambda-execution-role"
    Purpose     = "Lambda function execution"
    Environment = "production"
  }
}

resource "aws_iam_role_policy" "lambda_execution_policy" {
  name = "flipkart-lambda-execution-policy"
  role = aws_iam_role.lambda_execution_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceStatus",
          "ec2:StartInstances",
          "ec2:StopInstances"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "ec2:ResourceTag/Project" = "flipkart"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:StopDBInstance",
          "rds:StartDBInstance"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "rds:ResourceTag/Project" = "flipkart"
          }
        }
      }
    ]
  })
}

# 4. CI/CD Pipeline Role
resource "aws_iam_role" "cicd_pipeline_role" {
  name = "flipkart-cicd-pipeline-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codepipeline.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name        = "flipkart-cicd-pipeline-role"
    Purpose     = "CI/CD pipeline execution"
    Environment = "production"
  }
}

resource "aws_iam_role_policy" "cicd_pipeline_policy" {
  name = "flipkart-cicd-pipeline-policy"
  role = aws_iam_role.cicd_pipeline_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:GetBucketVersioning"
        ]
        Resource = [
          "arn:aws:s3:::flipkart-cicd-artifacts",
          "arn:aws:s3:::flipkart-cicd-artifacts/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices"
        ]
        Resource = [
          "arn:aws:ecs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:service/flipkart-*"
        ]
      }
    ]
  })
}

# 5. Developer Access Role (for development team)
resource "aws_iam_role" "developer_access_role" {
  name = "flipkart-developer-access-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Condition = {
          StringEquals = {
            "sts:ExternalId" = "flipkart-developer-access"
          }
          IpAddress = {
            "aws:SourceIp" = [
              "203.192.XXX.XXX/32",  # Office IP
              "49.32.XXX.XXX/32"     # Backup office IP
            ]
          }
        }
      }
    ]
  })
  
  tags = {
    Name        = "flipkart-developer-access-role"
    Purpose     = "Developer access to AWS resources"
    Environment = "development"
  }
}

resource "aws_iam_role_policy" "developer_access_policy" {
  name = "flipkart-developer-access-policy"
  role = aws_iam_role.developer_access_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "ec2:GetConsole*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:RebootInstances"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "ec2:ResourceTag/Environment" = "development"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "rds:Describe*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetObject"
        ]
        Resource = [
          "arn:aws:s3:::flipkart-development-*",
          "arn:aws:s3:::flipkart-development-*/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "cloudwatch:GetDashboard"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:Describe*",
          "logs:FilterLogEvents",
          "logs:GetLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Security Groups with least privilege

# Web Tier Security Group
resource "aws_security_group" "web_tier" {
  name_prefix = "flipkart-web-tier-"
  vpc_id      = var.vpc_id  # Reference from VPC module
  description = "Security group for web tier with strict access controls"
  
  # HTTP from load balancer only
  ingress {
    description     = "HTTP from load balancer"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.load_balancer.id]
  }
  
  # HTTPS from load balancer only
  ingress {
    description     = "HTTPS from load balancer"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.load_balancer.id]
  }
  
  # SSH from bastion host only
  ingress {
    description     = "SSH from bastion host"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }
  
  # Outbound HTTPS for updates and API calls
  egress {
    description = "HTTPS outbound"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Outbound HTTP for package updates
  egress {
    description = "HTTP outbound"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Database access
  egress {
    description     = "MySQL to database tier"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.database_tier.id]
  }
  
  # Cache access
  egress {
    description     = "Redis to cache tier"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.cache_tier.id]
  }
  
  tags = {
    Name        = "flipkart-web-tier-sg"
    Tier        = "web"
    Environment = "production"
  }
}

# Load Balancer Security Group
resource "aws_security_group" "load_balancer" {
  name_prefix = "flipkart-load-balancer-"
  vpc_id      = var.vpc_id
  description = "Security group for application load balancer"
  
  # HTTP from internet
  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # HTTPS from internet
  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Outbound to web tier
  egress {
    description     = "HTTP to web tier"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.web_tier.id]
  }
  
  egress {
    description     = "HTTPS to web tier"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.web_tier.id]
  }
  
  tags = {
    Name        = "flipkart-load-balancer-sg"
    Tier        = "load-balancer"
    Environment = "production"
  }
}

# Database Tier Security Group
resource "aws_security_group" "database_tier" {
  name_prefix = "flipkart-database-tier-"
  vpc_id      = var.vpc_id
  description = "Security group for database tier"
  
  # MySQL from web tier only
  ingress {
    description     = "MySQL from web tier"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.web_tier.id]
  }
  
  # MySQL from bastion for maintenance
  ingress {
    description     = "MySQL from bastion"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }
  
  # No outbound rules (databases don't need internet access)
  
  tags = {
    Name        = "flipkart-database-tier-sg"
    Tier        = "database"
    Environment = "production"
  }
}

# Cache Tier Security Group
resource "aws_security_group" "cache_tier" {
  name_prefix = "flipkart-cache-tier-"
  vpc_id      = var.vpc_id
  description = "Security group for cache tier (Redis/ElastiCache)"
  
  # Redis from web tier only
  ingress {
    description     = "Redis from web tier"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.web_tier.id]
  }
  
  tags = {
    Name        = "flipkart-cache-tier-sg"
    Tier        = "cache"
    Environment = "production"
  }
}

# Bastion Host Security Group
resource "aws_security_group" "bastion" {
  name_prefix = "flipkart-bastion-"
  vpc_id      = var.vpc_id
  description = "Security group for bastion host"
  
  # SSH from office IPs only
  ingress {
    description = "SSH from office"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [
      "203.192.XXX.XXX/32",  # Office IP 1
      "49.32.XXX.XXX/32"     # Office IP 2
    ]
  }
  
  # Outbound SSH to private instances
  egress {
    description = "SSH to private instances"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]  # VPC CIDR
  }
  
  # Outbound HTTPS for updates
  egress {
    description = "HTTPS outbound"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # MySQL for database access
  egress {
    description     = "MySQL to database"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.database_tier.id]
  }
  
  tags = {
    Name        = "flipkart-bastion-sg"
    Tier        = "management"
    Environment = "production"
  }
}

# WAF Web ACL for additional protection
resource "aws_wafv2_web_acl" "flipkart_waf" {
  name  = "flipkart-web-acl"
  scope = "REGIONAL"
  
  default_action {
    allow {}
  }
  
  # Rate limiting rule
  rule {
    name     = "RateLimitRule"
    priority = 1
    
    action {
      block {}
    }
    
    statement {
      rate_based_statement {
        limit              = 2000  # 2000 requests per 5 minutes
        aggregate_key_type = "IP"
      }
    }
    
    visibility_config {
      metric_name                = "RateLimitRule"
      cloudwatch_metrics_enabled = true
      sampled_requests_enabled   = true
    }
  }
  
  # AWS Managed Core Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2
    
    override_action {
      none {}
    }
    
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    
    visibility_config {
      metric_name                = "CommonRuleSetMetric"
      cloudwatch_metrics_enabled = true
      sampled_requests_enabled   = true
    }
  }
  
  # SQL injection protection
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 3
    
    override_action {
      none {}
    }
    
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }
    
    visibility_config {
      metric_name                = "SQLiRuleSetMetric"
      cloudwatch_metrics_enabled = true
      sampled_requests_enabled   = true
    }
  }
  
  tags = {
    Name        = "flipkart-waf"
    Environment = "production"
    Purpose     = "Web application firewall"
  }
  
  visibility_config {
    metric_name                = "FlipkartWAF"
    cloudwatch_metrics_enabled = true
    sampled_requests_enabled   = true
  }
}

# CloudTrail for audit logging
resource "aws_cloudtrail" "flipkart_audit" {
  name                          = "flipkart-audit-trail"
  s3_bucket_name               = aws_s3_bucket.cloudtrail_logs.bucket
  include_global_service_events = true
  is_multi_region_trail        = true
  enable_logging               = true
  
  # Log file validation for integrity
  enable_log_file_validation = true
  
  # KMS encryption
  kms_key_id = aws_kms_key.flipkart_main.arn
  
  event_selector {
    read_write_type                 = "All"
    include_management_events       = true
    exclude_management_event_sources = []
    
    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::flipkart-*/*"]
    }
  }
  
  tags = {
    Name        = "flipkart-audit-trail"
    Environment = "production"
    Purpose     = "Audit logging and compliance"
  }
}

# S3 bucket for CloudTrail logs
resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket        = "flipkart-cloudtrail-logs-${random_string.bucket_suffix.result}"
  force_destroy = false
  
  tags = {
    Name        = "flipkart-cloudtrail-logs"
    Environment = "production"
    Purpose     = "CloudTrail audit logs"
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 bucket policy for CloudTrail
resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_logs.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_logs.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# Variables that need to be defined
variable "vpc_id" {
  description = "VPC ID where security groups will be created"
  type        = string
}

# Outputs
output "iam_roles" {
  description = "IAM roles created"
  value = {
    ec2_application = aws_iam_role.ec2_application_role.arn
    rds_monitoring  = aws_iam_role.rds_monitoring_role.arn
    lambda_execution = aws_iam_role.lambda_execution_role.arn
    cicd_pipeline   = aws_iam_role.cicd_pipeline_role.arn
    developer_access = aws_iam_role.developer_access_role.arn
  }
}

output "security_groups" {
  description = "Security groups created"
  value = {
    web_tier       = aws_security_group.web_tier.id
    load_balancer  = aws_security_group.load_balancer.id
    database_tier  = aws_security_group.database_tier.id
    cache_tier     = aws_security_group.cache_tier.id
    bastion        = aws_security_group.bastion.id
  }
}

output "kms_key_arn" {
  description = "KMS key ARN for encryption"
  value       = aws_kms_key.flipkart_main.arn
}

output "waf_web_acl_arn" {
  description = "WAF Web ACL ARN"
  value       = aws_wafv2_web_acl.flipkart_waf.arn
}

output "cloudtrail_arn" {
  description = "CloudTrail ARN for audit logging"
  value       = aws_cloudtrail.flipkart_audit.arn
}
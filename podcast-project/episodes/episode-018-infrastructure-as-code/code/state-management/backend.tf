# Example 8: Terraform State Management with Remote Backend
# यह example secure और scalable state management setup करता है
# Flipkart जैसे बड़े organizations के लिए

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Remote backend configuration for production
  # यह state को S3 में store करता है और DynamoDB से locking करता है
  backend "s3" {
    # S3 bucket for storing state
    bucket = "flipkart-terraform-state-mumbai"
    key    = "infrastructure/terraform.tfstate"
    region = "ap-south-1"
    
    # DynamoDB table for state locking
    dynamodb_table = "terraform-state-lock"
    
    # Enable server-side encryption
    encrypt = true
    
    # Use versioning for state history
    versioning = true
    
    # Workspace-based state isolation
    workspace_key_prefix = "workspaces"
  }
}

# Provider configuration
provider "aws" {
  region = "ap-south-1"  # Mumbai region
  
  # Default tags for all resources
  default_tags {
    tags = {
      ManagedBy   = "terraform"
      Project     = "flipkart-infrastructure"
      Environment = terraform.workspace
      Owner       = "platform-team"
      CostCenter  = "engineering"
      Terraform   = "true"
    }
  }
}

# S3 Bucket for Terraform State (created separately)
resource "aws_s3_bucket" "terraform_state" {
  bucket = "flipkart-terraform-state-mumbai-${random_string.bucket_suffix.result}"
  
  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }
  
  tags = {
    Name        = "terraform-state-bucket"
    Purpose     = "Terraform state storage"
    Environment = "shared"
    Security    = "sensitive"
  }
}

# Random suffix for unique bucket naming
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Enable versioning on state bucket
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    
    bucket_key_enabled = true
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Bucket policy for secure access
resource "aws_s3_bucket_policy" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyInsecureConnections"
        Effect = "Deny"
        Principal = "*"
        Action = "s3:*"
        Resource = [
          aws_s3_bucket.terraform_state.arn,
          "${aws_s3_bucket.terraform_state.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
      {
        Sid    = "DenyDirectObjectAccess"
        Effect = "Deny"
        Principal = "*"
        Action = [
          "s3:DeleteObject",
          "s3:DeleteObjectVersion"
        ]
        Resource = "${aws_s3_bucket.terraform_state.arn}/*"
        Condition = {
          StringNotEquals = {
            "aws:PrincipalServiceName" = "terraform.io"
          }
        }
      }
    ]
  })
}

# Lifecycle configuration for cost optimization
resource "aws_s3_bucket_lifecycle_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    id     = "terraform_state_lifecycle"
    status = "Enabled"
    
    # Move old versions to IA after 30 days
    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }
    
    # Move old versions to Glacier after 90 days
    noncurrent_version_transition {
      noncurrent_days = 90
      storage_class   = "GLACIER"
    }
    
    # Delete old versions after 1 year
    noncurrent_version_expiration {
      noncurrent_days = 365
    }
    
    # Clean up incomplete multipart uploads
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "terraform-state-lock"
  billing_mode   = "PAY_PER_REQUEST"  # Cost-effective for infrequent access
  hash_key       = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
  
  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }
  
  # Server-side encryption
  server_side_encryption {
    enabled = true
  }
  
  tags = {
    Name        = "terraform-state-lock"
    Purpose     = "Terraform state locking"
    Environment = "shared"
  }
}

# CloudWatch Log Group for Terraform operations
resource "aws_cloudwatch_log_group" "terraform_operations" {
  name              = "/aws/terraform/operations"
  retention_in_days = 30
  
  tags = {
    Name        = "terraform-operations-logs"
    Purpose     = "Terraform operation logging"
    Environment = "shared"
  }
}

# IAM Role for Terraform State Management
resource "aws_iam_role" "terraform_state_role" {
  name = "terraform-state-management-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Condition = {
          StringEquals = {
            "sts:ExternalId" = "terraform-state-access"
          }
        }
      }
    ]
  })
  
  tags = {
    Name        = "terraform-state-role"
    Purpose     = "Terraform state management"
    Environment = "shared"
  }
}

# IAM Policy for Terraform State Access
resource "aws_iam_role_policy" "terraform_state_policy" {
  name = "terraform-state-access-policy"
  role = aws_iam_role.terraform_state_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketVersioning"
        ]
        Resource = aws_s3_bucket.terraform_state.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.terraform_state.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:DescribeTable"
        ]
        Resource = aws_dynamodb_table.terraform_state_lock.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.terraform_operations.arn}*"
      }
    ]
  })
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Data source for current region
data "aws_region" "current" {}

# Local values for configuration
locals {
  # State bucket naming convention
  state_bucket_name = "flipkart-terraform-state-${data.aws_region.current.name}"
  
  # Common tags for state management resources
  state_management_tags = {
    Component   = "state-management"
    Criticality = "high"
    Backup      = "enabled"
    Monitoring  = "enabled"
  }
  
  # Workspace-specific configurations
  workspace_config = {
    dev = {
      retention_days = 7
      lifecycle_days = 30
    }
    staging = {
      retention_days = 14
      lifecycle_days = 60
    }
    production = {
      retention_days = 30
      lifecycle_days = 90
    }
  }
}

# Outputs for use in other configurations
output "terraform_state_bucket" {
  description = "Name of the Terraform state bucket"
  value       = aws_s3_bucket.terraform_state.bucket
}

output "terraform_state_bucket_arn" {
  description = "ARN of the Terraform state bucket"
  value       = aws_s3_bucket.terraform_state.arn
}

output "dynamodb_lock_table" {
  description = "Name of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_state_lock.name
}

output "dynamodb_lock_table_arn" {
  description = "ARN of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_state_lock.arn
}

output "terraform_role_arn" {
  description = "ARN of the IAM role for Terraform operations"
  value       = aws_iam_role.terraform_state_role.arn
}

output "backend_configuration" {
  description = "Backend configuration for Terraform"
  value = {
    bucket         = aws_s3_bucket.terraform_state.bucket
    key            = "infrastructure/terraform.tfstate"
    region         = data.aws_region.current.name
    dynamodb_table = aws_dynamodb_table.terraform_state_lock.name
    encrypt        = true
  }
}

# CloudWatch alarms for monitoring state operations
resource "aws_cloudwatch_metric_alarm" "state_bucket_access" {
  alarm_name          = "terraform-state-bucket-access"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "NumberOfObjects"
  namespace           = "AWS/S3"
  period              = "300"
  statistic           = "Average"
  threshold           = "1000"  # Alert if too many state files
  alarm_description   = "Monitor Terraform state bucket object count"
  
  dimensions = {
    BucketName = aws_s3_bucket.terraform_state.bucket
    StorageType = "AllStorageTypes"
  }
  
  tags = {
    Name        = "terraform-state-monitoring"
    Purpose     = "Monitor state bucket usage"
    Environment = "shared"
  }
}

# SNS Topic for state management alerts
resource "aws_sns_topic" "terraform_state_alerts" {
  name = "terraform-state-management-alerts"
  
  tags = {
    Name        = "terraform-state-alerts"
    Purpose     = "Terraform state management notifications"
    Environment = "shared"
  }
}

# Lambda function for state backup automation
resource "aws_lambda_function" "state_backup" {
  filename         = "state_backup.zip"
  function_name    = "terraform-state-backup"
  role            = aws_iam_role.lambda_state_backup.arn
  handler         = "index.handler"
  runtime         = "python3.9"
  timeout         = 300
  
  # Create a simple backup function
  source_code_hash = data.archive_file.state_backup_zip.output_base64sha256
  
  environment {
    variables = {
      STATE_BUCKET = aws_s3_bucket.terraform_state.bucket
      BACKUP_BUCKET = "${aws_s3_bucket.terraform_state.bucket}-backup"
    }
  }
  
  tags = {
    Name        = "terraform-state-backup"
    Purpose     = "Automate state backups"
    Environment = "shared"
  }
}

# Archive file for Lambda function
data "archive_file" "state_backup_zip" {
  type        = "zip"
  output_path = "state_backup.zip"
  
  source {
    content = <<-EOT
import boto3
import json
import os
from datetime import datetime

def handler(event, context):
    """
    Backup Terraform state files to separate bucket
    """
    s3 = boto3.client('s3')
    
    source_bucket = os.environ['STATE_BUCKET']
    backup_bucket = os.environ['BACKUP_BUCKET']
    
    try:
        # List all objects in state bucket
        response = s3.list_objects_v2(Bucket=source_bucket)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                backup_key = f"backup/{datetime.now().isoformat()}/{key}"
                
                # Copy to backup bucket
                copy_source = {'Bucket': source_bucket, 'Key': key}
                s3.copy_object(CopySource=copy_source, Bucket=backup_bucket, Key=backup_key)
                
                print(f"Backed up {key} to {backup_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Backup completed successfully')
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Backup failed: {str(e)}')
        }
EOT
    filename = "index.py"
  }
}

# IAM Role for Lambda backup function
resource "aws_iam_role" "lambda_state_backup" {
  name = "terraform-state-backup-lambda-role"
  
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
}

# IAM Policy for Lambda backup function
resource "aws_iam_role_policy" "lambda_state_backup" {
  name = "terraform-state-backup-policy"
  role = aws_iam_role.lambda_state_backup.id
  
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
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.terraform_state.arn,
          "${aws_s3_bucket.terraform_state.arn}/*"
        ]
      }
    ]
  })
}

# EventBridge rule for daily state backup
resource "aws_cloudwatch_event_rule" "daily_backup" {
  name                = "terraform-state-daily-backup"
  description         = "Trigger daily backup of Terraform state"
  schedule_expression = "cron(0 6 * * ? *)"  # 6 AM UTC = 11:30 AM IST
  
  tags = {
    Name        = "terraform-state-backup-schedule"
    Purpose     = "Schedule state backups"
    Environment = "shared"
  }
}

# EventBridge target for Lambda function
resource "aws_cloudwatch_event_target" "lambda_backup_target" {
  rule      = aws_cloudwatch_event_rule.daily_backup.name
  target_id = "TerraformStateBackupTarget"
  arn       = aws_lambda_function.state_backup.arn
}

# Lambda permission for EventBridge
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.state_backup.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_backup.arn
}
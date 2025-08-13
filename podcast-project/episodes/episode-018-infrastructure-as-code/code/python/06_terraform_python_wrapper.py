#!/usr/bin/env python3
"""
Terraform Python Wrapper for Infrastructure Management
Episode 18: Infrastructure as Code

Python wrapper around Terraform for easier infrastructure management।
IRCTC-style ticketing system infrastructure के लिए optimized।

Cost Estimate: ₹25,000-45,000 per month for production IRCTC-scale
"""

import os
import json
import subprocess
import tempfile
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import boto3
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TerraformManager:
    """Python wrapper for Terraform operations"""
    
    def __init__(self, 
                 project_name: str = "irctc-booking",
                 environment: str = "dev",
                 region: str = "ap-south-1",
                 working_dir: Optional[str] = None):
        
        self.project_name = project_name
        self.environment = environment
        self.region = region
        self.working_dir = Path(working_dir) if working_dir else Path(f"./terraform-{environment}")
        self.state_file = self.working_dir / "terraform.tfstate"
        
        # Create working directory
        self.working_dir.mkdir(exist_ok=True)
        
        # AWS client for additional operations
        try:
            self.aws_client = boto3.client('ec2', region_name=region)
        except Exception as e:
            logger.warning(f"AWS client not available: {e}")
            self.aws_client = None
        
        logger.info(f"Terraform Manager initialized for {project_name}-{environment}")
    
    def generate_main_tf(self) -> str:
        """Generate main Terraform configuration for IRCTC-style system"""
        
        return f'''
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
    random = {{
      source  = "hashicorp/random"
      version = "~> 3.1"
    }}
  }}
  
  backend "s3" {{
    bucket         = "{self.project_name}-terraform-state-{self.environment}"
    key            = "infrastructure/terraform.tfstate"
    region         = "{self.region}"
    dynamodb_table = "{self.project_name}-terraform-locks-{self.environment}"
    encrypt        = true
  }}
}}

provider "aws" {{
  region = "{self.region}"
  
  default_tags {{
    tags = {{
      Project     = "{self.project_name}"
      Environment = "{self.environment}"
      ManagedBy   = "Terraform"
      Region      = "Mumbai"
      System      = "IRCTC-Booking"
    }}
  }}
}}

# Local values for common configurations
locals {{
  name_prefix = "{self.project_name}-{self.environment}"
  
  # Availability zones in Mumbai region
  azs = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
  
  # Common tags
  common_tags = {{
    Project         = "{self.project_name}"
    Environment     = "{self.environment}"
    ManagedBy       = "Terraform"
    DataResidency   = "India"
    ComplianceZone  = "IN"
    BusinessUnit    = "Railways"
  }}
}}

# Random password for database
resource "random_password" "db_password" {{
  length  = 32
  special = true
}}

# Data sources
data "aws_availability_zones" "available" {{
  state = "available"
}}

# VPC Configuration
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-vpc"
  }})
}}

# Internet Gateway
resource "aws_internet_gateway" "main" {{
  vpc_id = aws_vpc.main.id
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-igw"
  }})
}}

# Public Subnets for Load Balancers
resource "aws_subnet" "public" {{
  count = length(local.azs)
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${{count.index + 1}}.0/24"
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-public-${{count.index + 1}}"
    Type = "Public"
    Tier = "LoadBalancer"
  }})
}}

# Private Subnets for Application Servers
resource "aws_subnet" "private_app" {{
  count = length(local.azs)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${{count.index + 10}}.0/24"
  availability_zone = local.azs[count.index]
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-private-app-${{count.index + 1}}"
    Type = "Private"
    Tier = "Application"
  }})
}}

# Private Subnets for Database
resource "aws_subnet" "private_db" {{
  count = length(local.azs)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${{count.index + 20}}.0/24"
  availability_zone = local.azs[count.index]
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-private-db-${{count.index + 1}}"
    Type = "Private"
    Tier = "Database"
  }})
}}

# NAT Gateways for High Availability
resource "aws_eip" "nat" {{
  count = length(local.azs)
  
  domain = "vpc"
  
  depends_on = [aws_internet_gateway.main]
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-nat-eip-${{count.index + 1}}"
  }})
}}

resource "aws_nat_gateway" "main" {{
  count = length(local.azs)
  
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-nat-${{count.index + 1}}"
  }})
}}

# Route Tables
resource "aws_route_table" "public" {{
  vpc_id = aws_vpc.main.id
  
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }}
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-public-rt"
  }})
}}

resource "aws_route_table" "private_app" {{
  count = length(local.azs)
  
  vpc_id = aws_vpc.main.id
  
  route {{
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }}
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-private-app-rt-${{count.index + 1}}"
  }})
}}

# Route Table Associations
resource "aws_route_table_association" "public" {{
  count = length(aws_subnet.public)
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}}

resource "aws_route_table_association" "private_app" {{
  count = length(aws_subnet.private_app)
  
  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private_app[count.index].id
}}

# Security Groups
resource "aws_security_group" "alb" {{
  name        = "${{local.name_prefix}}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id
  
  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-alb-sg"
  }})
}}

resource "aws_security_group" "app_servers" {{
  name        = "${{local.name_prefix}}-app-sg"
  description = "Security group for application servers"
  vpc_id      = aws_vpc.main.id
  
  ingress {{
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }}
  
  ingress {{
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-app-sg"
  }})
}}

resource "aws_security_group" "database" {{
  name        = "${{local.name_prefix}}-db-sg"
  description = "Security group for database"
  vpc_id      = aws_vpc.main.id
  
  ingress {{
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app_servers.id]
  }}
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-db-sg"
  }})
}}

resource "aws_security_group" "bastion" {{
  name        = "${{local.name_prefix}}-bastion-sg"
  description = "Security group for bastion host"
  vpc_id      = aws_vpc.main.id
  
  ingress {{
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["203.192.xxx.xxx/32"] # Replace with office IP
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-bastion-sg"
  }})
}}

# Application Load Balancer
resource "aws_lb" "main" {{
  name               = "${{local.name_prefix}}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  
  enable_deletion_protection = false
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-alb"
  }})
}}

# Target Group for Application Servers
resource "aws_lb_target_group" "app" {{
  name     = "${{local.name_prefix}}-app-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  
  health_check {{
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }}
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-app-tg"
  }})
}}

# ALB Listener
resource "aws_lb_listener" "app" {{
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {{
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }}
}}

# Launch Template for Application Servers
resource "aws_launch_template" "app" {{
  name_prefix   = "${{local.name_prefix}}-app-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t3.large" # High performance for IRCTC scale
  key_name      = aws_key_pair.main.key_name
  
  vpc_security_group_ids = [aws_security_group.app_servers.id]
  
  user_data = base64encode(<<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    systemctl start docker
    systemctl enable docker
    
    # Install Node.js for IRCTC booking application
    curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
    yum install -y nodejs
    
    # Install application
    mkdir -p /opt/irctc-booking
    cat > /opt/irctc-booking/app.js << 'NODEJS'
const express = require('express');
const app = express();
const port = 8080;

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {{
  res.json({{
    status: 'healthy',
    timestamp: new Date().toISOString(),
    server: require('os').hostname(),
    system: 'IRCTC Booking System',
    region: 'Mumbai'
  }});
}});

// Main booking endpoint
app.get('/', (req, res) => {{
  res.json({{
    message: 'IRCTC Booking System - Mumbai Region',
    server: require('os').hostname(),
    environment: '{self.environment}',
    features: [
      'Train Booking',
      'Seat Availability',
      'Payment Gateway',
      'Ticket Generation',
      'Waitlist Management'
    ],
    hindi_message: 'भारतीय रेल टिकट बुकिंग सिस्टम'
  }});
}});

// Train search endpoint
app.get('/api/trains/search', (req, res) => {{
  res.json({{
    trains: [
      {{
        number: '12951',
        name: 'Mumbai Rajdhani Express',
        source: 'Mumbai Central',
        destination: 'New Delhi',
        duration: '16h 35m',
        available_seats: Math.floor(Math.random() * 100)
      }},
      {{
        number: '12009',
        name: 'Shatabdi Express',
        source: 'Mumbai Central',
        destination: 'Ahmedabad',
        duration: '6h 30m',
        available_seats: Math.floor(Math.random() * 150)
      }}
    ]
  }});
}});

app.listen(port, () => {{
  console.log(`IRCTC Booking System listening at http://localhost:${{port}}`);
}});
NODEJS

    # Install dependencies and start application
    cd /opt/irctc-booking
    npm init -y
    npm install express
    
    # Create systemd service
    cat > /etc/systemd/system/irctc-booking.service << 'SYSTEMD'
[Unit]
Description=IRCTC Booking System
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/irctc-booking
ExecStart=/usr/bin/node app.js
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
SYSTEMD

    systemctl daemon-reload
    systemctl start irctc-booking
    systemctl enable irctc-booking
    
    # Install CloudWatch agent
    yum install -y amazon-cloudwatch-agent
    
    echo "IRCTC Booking System setup completed"
  EOF
  )
  
  tag_specifications {{
    resource_type = "instance"
    tags = merge(local.common_tags, {{
      Name = "${{local.name_prefix}}-app-server"
      Role = "Application"
    }})
  }}
}}

# Auto Scaling Group for Application Servers
resource "aws_autoscaling_group" "app" {{
  name                = "${{local.name_prefix}}-app-asg"
  vpc_zone_identifier = aws_subnet.private_app[*].id
  target_group_arns   = [aws_lb_target_group.app.arn]
  health_check_type   = "ELB"
  
  min_size         = 2
  max_size         = 20  # High scaling for IRCTC traffic
  desired_capacity = 4   # Start with 4 instances
  
  launch_template {{
    id      = aws_launch_template.app.id
    version = "$Latest"
  }}
  
  # Auto scaling policies for Indian peak hours
  tag {{
    key                 = "Name"
    value               = "${{local.name_prefix}}-app-asg"
    propagate_at_launch = false
  }}
}}

# Auto Scaling Policies
resource "aws_autoscaling_policy" "scale_up" {{
  name                   = "${{local.name_prefix}}-scale-up"
  scaling_adjustment     = 2
  adjustment_type        = "ChangeInCapacity"
  cooldown              = 300
  autoscaling_group_name = aws_autoscaling_group.app.name
}}

resource "aws_autoscaling_policy" "scale_down" {{
  name                   = "${{local.name_prefix}}-scale-down"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown              = 300
  autoscaling_group_name = aws_autoscaling_group.app.name
}}

# CloudWatch Alarms for Auto Scaling
resource "aws_cloudwatch_metric_alarm" "cpu_high" {{
  alarm_name          = "${{local.name_prefix}}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "75"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]
  
  dimensions = {{
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }}
}}

resource "aws_cloudwatch_metric_alarm" "cpu_low" {{
  alarm_name          = "${{local.name_prefix}}-cpu-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "25"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_down.arn]
  
  dimensions = {{
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }}
}}

# RDS Subnet Group
resource "aws_db_subnet_group" "main" {{
  name       = "${{local.name_prefix}}-db-subnet-group"
  subnet_ids = aws_subnet.private_db[*].id
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-db-subnet-group"
  }})
}}

# RDS MySQL Instance
resource "aws_db_instance" "main" {{
  identifier     = "${{local.name_prefix}}-mysql"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.r5.2xlarge" # High performance for IRCTC
  
  allocated_storage     = 500
  max_allocated_storage = 2000
  storage_type         = "gp3"
  storage_encrypted    = true
  
  db_name  = "irctc_booking"
  username = "irctc_admin"
  password = random_password.db_password.result
  
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.database.id]
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00" # 8:30 AM IST
  maintenance_window     = "sun:04:00-sun:05:00" # 9:30 AM IST Sunday
  
  skip_final_snapshot = true
  deletion_protection = false
  
  # Performance Insights for monitoring
  performance_insights_enabled = true
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-mysql"
  }})
}}

# ElastiCache Redis for Session Management
resource "aws_elasticache_subnet_group" "main" {{
  name       = "${{local.name_prefix}}-cache-subnet"
  subnet_ids = aws_subnet.private_app[*].id
}}

resource "aws_elasticache_replication_group" "redis" {{
  replication_group_id       = "${{local.name_prefix}}-redis"
  description                = "Redis cluster for IRCTC session management"
  
  port                = 6379
  parameter_group_name = "default.redis7"
  
  num_cache_clusters = 3
  node_type          = "cache.r6g.large"
  
  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.app_servers.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-redis"
  }})
}}

# Key Pair for EC2 instances
resource "aws_key_pair" "main" {{
  key_name   = "${{local.name_prefix}}-keypair"
  public_key = file("~/.ssh/id_rsa.pub") # Make sure this exists
}}

# Data source for latest Amazon Linux AMI
data "aws_ami" "amazon_linux" {{
  most_recent = true
  owners      = ["amazon"]
  
  filter {{
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }}
}}

# Bastion Host for SSH access
resource "aws_instance" "bastion" {{
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  key_name      = aws_key_pair.main.key_name
  subnet_id     = aws_subnet.public[0].id
  
  vpc_security_group_ids = [aws_security_group.bastion.id]
  
  tags = merge(local.common_tags, {{
    Name = "${{local.name_prefix}}-bastion"
    Role = "Bastion"
  }})
}}

# Outputs
output "vpc_id" {{
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}}

output "load_balancer_dns" {{
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}}

output "bastion_ip" {{
  description = "Public IP of bastion host"
  value       = aws_instance.bastion.public_ip
}}

output "database_endpoint" {{
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}}

output "redis_endpoint" {{
  description = "Redis cluster endpoint"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}}
'''
    
    def generate_variables_tf(self) -> str:
        """Generate variables.tf file"""
        
        return '''
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "irctc-booking"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 instance type for application servers"
  type        = string
  default     = "t3.large"
}

variable "min_instances" {
  description = "Minimum number of instances in ASG"
  type        = number
  default     = 2
}

variable "max_instances" {
  description = "Maximum number of instances in ASG"
  type        = number
  default     = 20
}

variable "office_cidr" {
  description = "Office IP CIDR for SSH access"
  type        = string
  default     = "203.192.xxx.xxx/32"
}
'''
    
    def write_terraform_files(self):
        """Write all Terraform configuration files"""
        
        # Write main.tf
        with open(self.working_dir / "main.tf", 'w') as f:
            f.write(self.generate_main_tf())
        
        # Write variables.tf
        with open(self.working_dir / "variables.tf", 'w') as f:
            f.write(self.generate_variables_tf())
        
        logger.info(f"Terraform files written to {self.working_dir}")
    
    def run_terraform_command(self, command: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run terraform command in working directory"""
        
        full_command = ['terraform'] + command
        logger.info(f"Running: {' '.join(full_command)}")
        
        try:
            result = subprocess.run(
                full_command,
                cwd=self.working_dir,
                capture_output=capture_output,
                text=True,
                check=True
            )
            
            if capture_output:
                logger.info(f"Command output: {result.stdout}")
            
            return result
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Terraform command failed: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                logger.error(f"Error output: {e.stderr}")
            raise
    
    def init(self):
        """Initialize Terraform"""
        logger.info("Initializing Terraform...")
        return self.run_terraform_command(['init'])
    
    def plan(self, var_file: Optional[str] = None, out_file: Optional[str] = None) -> str:
        """Generate Terraform plan"""
        logger.info("Generating Terraform plan...")
        
        command = ['plan']
        
        if var_file:
            command.extend(['-var-file', var_file])
        
        if out_file:
            command.extend(['-out', out_file])
        
        # Add default variables
        command.extend([
            '-var', f'environment={self.environment}',
            '-var', f'project_name={self.project_name}',
            '-var', f'region={self.region}'
        ])
        
        result = self.run_terraform_command(command)
        return result.stdout
    
    def apply(self, plan_file: Optional[str] = None, auto_approve: bool = False) -> str:
        """Apply Terraform configuration"""
        logger.info("Applying Terraform configuration...")
        
        command = ['apply']
        
        if plan_file:
            command.append(plan_file)
        elif auto_approve:
            command.append('-auto-approve')
            # Add variables for auto-approve
            command.extend([
                '-var', f'environment={self.environment}',
                '-var', f'project_name={self.project_name}',
                '-var', f'region={self.region}'
            ])
        
        result = self.run_terraform_command(command, capture_output=not auto_approve)
        return result.stdout if result.stdout else "Applied successfully"
    
    def destroy(self, auto_approve: bool = False) -> str:
        """Destroy Terraform infrastructure"""
        logger.info("Destroying Terraform infrastructure...")
        
        command = ['destroy']
        
        if auto_approve:
            command.append('-auto-approve')
        
        # Add variables
        command.extend([
            '-var', f'environment={self.environment}',
            '-var', f'project_name={self.project_name}',
            '-var', f'region={self.region}'
        ])
        
        result = self.run_terraform_command(command, capture_output=not auto_approve)
        return result.stdout if result.stdout else "Destroyed successfully"
    
    def show(self) -> Dict[str, Any]:
        """Show current Terraform state"""
        logger.info("Showing Terraform state...")
        
        result = self.run_terraform_command(['show', '-json'])
        return json.loads(result.stdout)
    
    def output(self, output_name: Optional[str] = None) -> Dict[str, Any]:
        """Get Terraform outputs"""
        logger.info("Getting Terraform outputs...")
        
        command = ['output', '-json']
        
        if output_name:
            command.append(output_name)
        
        result = self.run_terraform_command(command)
        return json.loads(result.stdout)
    
    def refresh(self) -> str:
        """Refresh Terraform state"""
        logger.info("Refreshing Terraform state...")
        
        command = ['refresh', '-var', f'environment={self.environment}']
        result = self.run_terraform_command(command)
        return result.stdout
    
    def validate(self) -> bool:
        """Validate Terraform configuration"""
        logger.info("Validating Terraform configuration...")
        
        try:
            result = self.run_terraform_command(['validate'])
            logger.info("Terraform configuration is valid")
            return True
        except subprocess.CalledProcessError:
            logger.error("Terraform configuration is invalid")
            return False
    
    def fmt(self) -> str:
        """Format Terraform files"""
        logger.info("Formatting Terraform files...")
        
        result = self.run_terraform_command(['fmt', '-recursive'])
        return result.stdout
    
    def get_cost_estimate(self) -> Dict[str, Any]:
        """Get cost estimation for the infrastructure"""
        
        # This is a simplified cost calculation
        # In production, you'd use tools like Infracost or AWS Cost Calculator
        
        cost_estimate = {
            'environment': self.environment,
            'region': self.region,
            'monthly_costs': {
                'vpc_nat_gateways': 3 * 3500,  # 3 NAT Gateways * ₹3500/month
                'application_servers': {
                    'min_instances': 2 * 8000,  # 2 t3.large instances
                    'max_instances': 20 * 8000,  # Up to 20 instances during peak
                    'avg_instances': 4 * 8000   # Average 4 instances
                },
                'load_balancer': 1500,
                'rds_mysql': 25000,  # db.r5.2xlarge is expensive but needed for IRCTC scale
                'elasticache_redis': 12000,  # 3 cache.r6g.large nodes
                'bastion_host': 1000,  # t3.micro
                'data_transfer': 5000,  # Estimated based on traffic
                'cloudwatch_monitoring': 2000,
                'ebs_storage': 3000
            }
        }
        
        # Calculate totals
        monthly_costs = cost_estimate['monthly_costs']
        min_monthly = (monthly_costs['vpc_nat_gateways'] + 
                      monthly_costs['application_servers']['min_instances'] +
                      monthly_costs['load_balancer'] +
                      monthly_costs['rds_mysql'] +
                      monthly_costs['elasticache_redis'] +
                      monthly_costs['bastion_host'] +
                      monthly_costs['data_transfer'] +
                      monthly_costs['cloudwatch_monitoring'] +
                      monthly_costs['ebs_storage'])
        
        avg_monthly = (monthly_costs['vpc_nat_gateways'] + 
                      monthly_costs['application_servers']['avg_instances'] +
                      monthly_costs['load_balancer'] +
                      monthly_costs['rds_mysql'] +
                      monthly_costs['elasticache_redis'] +
                      monthly_costs['bastion_host'] +
                      monthly_costs['data_transfer'] +
                      monthly_costs['cloudwatch_monitoring'] +
                      monthly_costs['ebs_storage'])
        
        max_monthly = (monthly_costs['vpc_nat_gateways'] + 
                      monthly_costs['application_servers']['max_instances'] +
                      monthly_costs['load_balancer'] +
                      monthly_costs['rds_mysql'] +
                      monthly_costs['elasticache_redis'] +
                      monthly_costs['bastion_host'] +
                      monthly_costs['data_transfer'] +
                      monthly_costs['cloudwatch_monitoring'] +
                      monthly_costs['ebs_storage'])
        
        cost_estimate['summary'] = {
            'min_monthly_inr': min_monthly,
            'avg_monthly_inr': avg_monthly,
            'max_monthly_inr': max_monthly,
            'currency': 'INR',
            'note': 'Costs are estimates for Mumbai region and may vary based on actual usage'
        }
        
        return cost_estimate
    
    def create_backend_resources(self):
        """Create S3 bucket and DynamoDB table for Terraform state"""
        
        if not self.aws_client:
            logger.error("AWS client not available")
            return False
        
        try:
            # Create S3 bucket for state
            s3_client = boto3.client('s3', region_name=self.region)
            bucket_name = f"{self.project_name}-terraform-state-{self.environment}"
            
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.region}
            )
            
            # Enable versioning
            s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Create DynamoDB table for locking
            dynamodb_client = boto3.client('dynamodb', region_name=self.region)
            table_name = f"{self.project_name}-terraform-locks-{self.environment}"
            
            dynamodb_client.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': 'LockID', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'LockID', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'Project', 'Value': self.project_name},
                    {'Key': 'Environment', 'Value': self.environment},
                    {'Key': 'Purpose', 'Value': 'Terraform State Locking'}
                ]
            )
            
            logger.info(f"Backend resources created: {bucket_name}, {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backend resources: {e}")
            return False

def main():
    """Main function to demonstrate Terraform management"""
    
    print("🚀 IRCTC-Style Railway Booking Infrastructure")
    print("=" * 55)
    
    # Initialize Terraform manager
    tf_manager = TerraformManager(
        project_name="irctc-booking",
        environment="dev",
        region="ap-south-1"
    )
    
    print("📝 Generating Terraform configurations...")
    tf_manager.write_terraform_files()
    
    print("💰 Cost Estimation:")
    cost_estimate = tf_manager.get_cost_estimate()
    summary = cost_estimate['summary']
    print(f"- Minimum monthly cost: ₹{summary['min_monthly_inr']:,}")
    print(f"- Average monthly cost: ₹{summary['avg_monthly_inr']:,}")
    print(f"- Maximum monthly cost: ₹{summary['max_monthly_inr']:,}")
    
    # Get user choice for deployment
    choice = input("\n🤔 Do you want to proceed with Terraform operations? (y/n): ")
    
    if choice.lower() == 'y':
        try:
            print("\n📦 Creating backend resources...")
            if tf_manager.create_backend_resources():
                print("✅ Backend resources created")
            else:
                print("⚠️ Backend resources creation failed, continuing anyway...")
            
            print("\n🔧 Initializing Terraform...")
            tf_manager.init()
            
            print("✅ Formatting Terraform files...")
            tf_manager.fmt()
            
            print("🔍 Validating configuration...")
            if tf_manager.validate():
                print("✅ Configuration is valid")
            else:
                print("❌ Configuration has errors")
                return
            
            print("\n📋 Generating Terraform plan...")
            plan_output = tf_manager.plan()
            
            print("\n📊 Plan Summary:")
            print("- VPC with 3 AZs in Mumbai region")
            print("- Application Load Balancer")
            print("- Auto Scaling Group (2-20 instances)")
            print("- RDS MySQL (db.r5.2xlarge)")
            print("- ElastiCache Redis cluster")
            print("- CloudWatch monitoring")
            print("- Security groups and NACLs")
            
            apply_choice = input("\n🚀 Do you want to apply this configuration? (y/n): ")
            
            if apply_choice.lower() == 'y':
                print("\n🔨 Applying Terraform configuration...")
                print("⏳ This will take several minutes...")
                
                apply_output = tf_manager.apply(auto_approve=True)
                
                print("\n✅ Infrastructure deployed successfully!")
                
                # Get outputs
                outputs = tf_manager.output()
                
                print("\n🌐 Infrastructure Details:")
                if 'load_balancer_dns' in outputs:
                    print(f"- Load Balancer URL: http://{outputs['load_balancer_dns']['value']}")
                
                if 'bastion_ip' in outputs:
                    print(f"- Bastion Host IP: {outputs['bastion_ip']['value']}")
                
                print(f"- Region: {tf_manager.region}")
                print(f"- Environment: {tf_manager.environment}")
                
                print("\n📈 Scaling Information:")
                print("- Auto scaling based on CPU utilization")
                print("- Scales up when CPU > 75%")
                print("- Scales down when CPU < 25%")
                print("- Maximum 20 instances for peak traffic")
                
                print("\n🔧 Management Commands:")
                print("- SSH to bastion: ssh -i ~/.ssh/id_rsa ec2-user@<bastion_ip>")
                print("- View logs: AWS CloudWatch")
                print("- Monitor: AWS CloudWatch Dashboard")
                
                destroy_choice = input("\n🗑️ Do you want to destroy the infrastructure? (y/n): ")
                
                if destroy_choice.lower() == 'y':
                    print("\n💥 Destroying infrastructure...")
                    tf_manager.destroy(auto_approve=True)
                    print("✅ Infrastructure destroyed successfully!")
        
        except Exception as e:
            logger.error(f"Terraform operations failed: {e}")
            print(f"\n❌ Error: {e}")
    
    print("\n📖 Configuration files generated in:", tf_manager.working_dir)
    print("💡 You can modify the configurations and run terraform commands manually")
    print("✅ Terraform Python wrapper demonstration completed!")

if __name__ == "__main__":
    main()
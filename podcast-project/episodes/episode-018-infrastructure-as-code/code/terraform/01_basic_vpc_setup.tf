# Example 1: Basic VPC Setup for Indian Applications
# यह example Mumbai region में basic VPC setup करता है जो Flipkart जैसे applications के लिए suitable है

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWS Provider configuration - Mumbai region
provider "aws" {
  region = "ap-south-1"  # Mumbai region for low latency
  
  # Default tags जो हर resource पर apply होंगे
  default_tags {
    tags = {
      Environment = "production"
      Project     = "flipkart-infrastructure"
      CreatedBy   = "terraform"
      Owner       = "platform-team"
      CostCenter  = "engineering"
      Region      = "mumbai"
    }
  }
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC - Virtual Private Cloud (हमारा private network)
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"  # 65,536 IP addresses
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "flipkart-main-vpc"
    Description = "Main VPC for Flipkart application infrastructure"
  }
}

# Internet Gateway - बाहरी दुनिया से connection
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "flipkart-main-igw"
    Description = "Internet Gateway for public subnet connectivity"
  }
}

# Public Subnets - Web servers के लिए (internet facing)
resource "aws_subnet" "public" {
  count = min(length(data.aws_availability_zones.available.names), 3)
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"  # 10.0.1.0/24, 10.0.2.0/24, etc.
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "flipkart-public-subnet-${count.index + 1}"
    Type = "public"
    Tier = "web"
    AZ   = data.aws_availability_zones.available.names[count.index]
  }
}

# Private Subnets - Application servers और databases के लिए
resource "aws_subnet" "private" {
  count = min(length(data.aws_availability_zones.available.names), 3)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"  # 10.0.10.0/24, 10.0.11.0/24, etc.
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "flipkart-private-subnet-${count.index + 1}"
    Type = "private"
    Tier = "application"
    AZ   = data.aws_availability_zones.available.names[count.index]
  }
}

# Database Subnets - केवल database traffic के लिए
resource "aws_subnet" "database" {
  count = min(length(data.aws_availability_zones.available.names), 3)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 20}.0/24"  # 10.0.20.0/24, 10.0.21.0/24, etc.
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "flipkart-database-subnet-${count.index + 1}"
    Type = "database"
    Tier = "data"
    AZ   = data.aws_availability_zones.available.names[count.index]
  }
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  count = min(length(data.aws_availability_zones.available.names), 3)
  
  domain = "vpc"
  
  tags = {
    Name = "flipkart-nat-eip-${count.index + 1}"
    Purpose = "NAT Gateway for private subnet internet access"
  }
  
  depends_on = [aws_internet_gateway.main]
}

# NAT Gateway - Private subnets को internet access देने के लिए
resource "aws_nat_gateway" "main" {
  count = min(length(data.aws_availability_zones.available.names), 3)
  
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = {
    Name = "flipkart-nat-gateway-${count.index + 1}"
    AZ   = data.aws_availability_zones.available.names[count.index]
  }
  
  depends_on = [aws_internet_gateway.main]
}

# Route Table for Public Subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "flipkart-public-route-table"
    Type = "public"
  }
}

# Route Table for Private Subnets (per AZ)
resource "aws_route_table" "private" {
  count = min(length(data.aws_availability_zones.available.names), 3)
  
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = {
    Name = "flipkart-private-route-table-${count.index + 1}"
    Type = "private"
    AZ   = data.aws_availability_zones.available.names[count.index]
  }
}

# Route Table for Database Subnets (no internet access)
resource "aws_route_table" "database" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "flipkart-database-route-table"
    Type = "database"
    Purpose = "Isolated database subnet routing"
  }
}

# Route Table Associations - Public Subnets
resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Route Table Associations - Private Subnets
resource "aws_route_table_association" "private" {
  count = length(aws_subnet.private)
  
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Route Table Associations - Database Subnets
resource "aws_route_table_association" "database" {
  count = length(aws_subnet.database)
  
  subnet_id      = aws_subnet.database[count.index].id
  route_table_id = aws_route_table.database.id
}

# Network ACL for Public Subnets (additional security layer)
resource "aws_network_acl" "public" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.public[*].id
  
  # HTTP inbound
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 80
    to_port    = 80
  }
  
  # HTTPS inbound
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }
  
  # SSH inbound (restricted to office IPs in production)
  ingress {
    protocol   = "tcp"
    rule_no    = 120
    action     = "allow"
    cidr_block = "10.0.0.0/16"  # VPC CIDR only
    from_port  = 22
    to_port    = 22
  }
  
  # Ephemeral ports for return traffic
  ingress {
    protocol   = "tcp"
    rule_no    = 130
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }
  
  # All outbound traffic allowed
  egress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
  }
  
  tags = {
    Name = "flipkart-public-nacl"
    Type = "public"
  }
}

# Network ACL for Private Subnets
resource "aws_network_acl" "private" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.private[*].id
  
  # All traffic from VPC allowed
  ingress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "10.0.0.0/16"
  }
  
  # Ephemeral ports for internet return traffic
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }
  
  # All outbound traffic allowed
  egress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
  }
  
  tags = {
    Name = "flipkart-private-nacl"
    Type = "private"
  }
}

# VPC Flow Logs for monitoring network traffic
resource "aws_flow_log" "vpc_flow_log" {
  iam_role_arn    = aws_iam_role.flow_log.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_log.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
  
  tags = {
    Name = "flipkart-vpc-flow-logs"
    Purpose = "Network traffic monitoring and security analysis"
  }
}

# CloudWatch Log Group for VPC Flow Logs
resource "aws_cloudwatch_log_group" "vpc_flow_log" {
  name              = "/aws/vpc/flowlogs"
  retention_in_days = 30  # Cost optimization - 30 days retention
  
  tags = {
    Name = "vpc-flow-logs"
    Purpose = "VPC network traffic logging"
  }
}

# IAM Role for VPC Flow Logs
resource "aws_iam_role" "flow_log" {
  name = "flowlogsRole"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name = "vpc-flow-logs-role"
    Purpose = "IAM role for VPC flow logs"
  }
}

# IAM Role Policy for VPC Flow Logs
resource "aws_iam_role_policy" "flow_log" {
  name = "flowlogsDeliveryRolePolicy"
  role = aws_iam_role.flow_log.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Outputs - अन्य resources में use करने के लिए
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "IDs of database subnets"
  value       = aws_subnet.database[*].id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = "IDs of NAT Gateways"
  value       = aws_nat_gateway.main[*].id
}

output "availability_zones" {
  description = "List of availability zones used"
  value       = data.aws_availability_zones.available.names
}

# Local values for reuse
locals {
  # Common tags for all resources
  common_tags = {
    Environment = "production"
    Project     = "flipkart-infrastructure"
    CreatedBy   = "terraform"
    ManagedBy   = "platform-team"
  }
  
  # Subnet configurations
  public_subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnet_cidrs  = ["10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
  database_subnet_cidrs = ["10.0.20.0/24", "10.0.21.0/24", "10.0.22.0/24"]
}

# Security Group for VPC Endpoints (if needed)
resource "aws_security_group" "vpc_endpoints" {
  name_prefix = "flipkart-vpc-endpoints-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for VPC endpoints"
  
  ingress {
    description = "HTTPS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }
  
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "flipkart-vpc-endpoints-sg"
    Purpose = "Security group for VPC endpoints"
  }
}

# Cost allocation tags for billing
resource "aws_default_tags" "example" {
  tags = {
    Environment = "production"
    Application = "flipkart"
    Team        = "platform"
    CostCenter  = "engineering"
    CreatedBy   = "terraform"
  }
}
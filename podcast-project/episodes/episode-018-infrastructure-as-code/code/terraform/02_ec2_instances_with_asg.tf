# Example 2: EC2 Instances with Auto Scaling Group
# यह example एक complete web application setup करता है Auto Scaling के साथ
# IRCTC की तरह high traffic को handle करने के लिए

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Data source for latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Key Pair for SSH access
resource "aws_key_pair" "app_key" {
  key_name   = "flipkart-app-key"
  public_key = file("~/.ssh/id_rsa.pub")  # आपकी public key का path
  
  tags = {
    Name        = "flipkart-application-key"
    Environment = "production"
    Purpose     = "SSH access to application servers"
  }
}

# Security Group for Web Servers
resource "aws_security_group" "web_servers" {
  name_prefix = "flipkart-web-"
  vpc_id      = aws_vpc.main.id  # Previous example का VPC
  description = "Security group for web servers hosting Flipkart application"
  
  # HTTP access from anywhere
  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # HTTPS access from anywhere
  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # SSH access from office/home (replace with your IP)
  ingress {
    description = "SSH from office"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["203.192.XXX.XXX/32"]  # Replace with your office IP
  }
  
  # Application port (Node.js/Java backend)
  ingress {
    description     = "Application port from ALB"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  
  # All outbound traffic
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name        = "flipkart-web-servers-sg"
    Environment = "production"
    Tier        = "web"
  }
}

# Security Group for Application Load Balancer
resource "aws_security_group" "alb" {
  name_prefix = "flipkart-alb-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for Application Load Balancer"
  
  # HTTP access from anywhere
  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # HTTPS access from anywhere
  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # All outbound traffic
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name        = "flipkart-alb-sg"
    Environment = "production"
    Tier        = "load-balancer"
  }
}

# IAM Role for EC2 instances (CloudWatch logs, S3 access etc.)
resource "aws_iam_role" "ec2_role" {
  name = "flipkart-ec2-role"
  
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
    Name        = "flipkart-ec2-role"
    Environment = "production"
    Purpose     = "IAM role for EC2 instances"
  }
}

# IAM Policy for EC2 instances
resource "aws_iam_role_policy" "ec2_policy" {
  name = "flipkart-ec2-policy"
  role = aws_iam_role.ec2_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "logs:PutLogEvents",
          "logs:CreateLogGroup",
          "logs:CreateLogStream"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "arn:aws:s3:::flipkart-application-logs/*",
          "arn:aws:s3:::flipkart-static-assets/*"
        ]
      }
    ]
  })
}

# IAM Instance Profile for EC2
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "flipkart-ec2-profile"
  role = aws_iam_role.ec2_role.name
  
  tags = {
    Name        = "flipkart-ec2-instance-profile"
    Environment = "production"
  }
}

# User Data Script for EC2 instances
locals {
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    region = "ap-south-1"
  }))
}

# Launch Template for Auto Scaling Group
resource "aws_launch_template" "app_template" {
  name_prefix   = "flipkart-app-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t3.medium"  # Production के लिए suitable size
  key_name      = aws_key_pair.app_key.key_name
  
  vpc_security_group_ids = [aws_security_group.web_servers.id]
  
  # IAM instance profile attach करें
  iam_instance_profile {
    name = aws_iam_instance_profile.ec2_profile.name
  }
  
  # User data for application setup
  user_data = local.user_data
  
  # EBS optimization enable करें
  ebs_optimized = true
  
  # Root volume configuration
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_type           = "gp3"  # Latest generation EBS
      volume_size           = 20     # 20GB root volume
      delete_on_termination = true
      encrypted             = true   # Security के लिए encryption
    }
  }
  
  # Additional volume for application data
  block_device_mappings {
    device_name = "/dev/sdf"
    ebs {
      volume_type           = "gp3"
      volume_size           = 50     # 50GB for application data
      delete_on_termination = true
      encrypted             = true
    }
  }
  
  # Instance metadata options (security)
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"  # IMDSv2 mandatory
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }
  
  # Monitoring enable करें
  monitoring {
    enabled = true
  }
  
  tag_specifications {
    resource_type = "instance"
    tags = {
      Name        = "flipkart-app-server"
      Environment = "production"
      Role        = "web-server"
      Application = "flipkart-main"
      Backup      = "daily"
    }
  }
  
  tag_specifications {
    resource_type = "volume"
    tags = {
      Name        = "flipkart-app-volume"
      Environment = "production"
      Backup      = "daily"
    }
  }
  
  tags = {
    Name        = "flipkart-launch-template"
    Environment = "production"
    Purpose     = "Auto scaling group launch template"
  }
}

# Application Load Balancer
resource "aws_lb" "app_lb" {
  name               = "flipkart-app-lb"
  internal           = false  # Internet-facing
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id  # Public subnets में deploy करें
  
  # Deletion protection enable करें production के लिए
  enable_deletion_protection = true
  
  # Access logs enable करें S3 में
  access_logs {
    bucket  = aws_s3_bucket.alb_logs.id
    prefix  = "alb-logs"
    enabled = true
  }
  
  tags = {
    Name        = "flipkart-application-lb"
    Environment = "production"
    Purpose     = "Load balancer for web application"
  }
}

# S3 Bucket for ALB Access Logs
resource "aws_s3_bucket" "alb_logs" {
  bucket        = "flipkart-alb-logs-${random_string.bucket_suffix.result}"
  force_destroy = false  # Production bucket को accidentally delete न हो
  
  tags = {
    Name        = "flipkart-alb-logs"
    Environment = "production"
    Purpose     = "ALB access logs storage"
  }
}

# Random string for unique bucket naming
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 Bucket versioning
resource "aws_s3_bucket_versioning" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id
  
  rule {
    id     = "log_retention"
    status = "Enabled"
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 60
      storage_class = "GLACIER"
    }
    
    expiration {
      days = 365  # 1 year retention
    }
  }
}

# Target Group for Load Balancer
resource "aws_lb_target_group" "app_tg" {
  name     = "flipkart-app-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  
  # Health check configuration
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"  # Application health endpoint
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
  
  # Stickiness configuration (session affinity)
  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400  # 1 day
    enabled         = true
  }
  
  tags = {
    Name        = "flipkart-app-target-group"
    Environment = "production"
    Purpose     = "Target group for application servers"
  }
}

# Load Balancer Listener
resource "aws_lb_listener" "app_listener" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = "80"
  protocol          = "HTTP"
  
  # Default action - redirect to HTTPS (production best practice)
  default_action {
    type = "redirect"
    
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
  
  tags = {
    Name        = "flipkart-app-listener-http"
    Environment = "production"
  }
}

# HTTPS Listener (production के लिए SSL certificate chahiye)
# resource "aws_lb_listener" "app_listener_https" {
#   load_balancer_arn = aws_lb.app_lb.arn
#   port              = "443"
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
#   certificate_arn   = aws_acm_certificate.app_cert.arn
#   
#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.app_tg.arn
#   }
# }

# Auto Scaling Group
resource "aws_autoscaling_group" "app_asg" {
  name                = "flipkart-app-asg"
  vpc_zone_identifier = aws_subnet.private[*].id  # Private subnets में instances
  target_group_arns   = [aws_lb_target_group.app_tg.arn]
  health_check_type   = "ELB"  # Load balancer health checks
  health_check_grace_period = 300
  
  # Capacity configuration
  min_size         = 2   # Minimum 2 instances for high availability
  max_size         = 10  # Maximum 10 instances for cost control
  desired_capacity = 3   # Normal time में 3 instances
  
  # Launch template configuration
  launch_template {
    id      = aws_launch_template.app_template.id
    version = "$Latest"
  }
  
  # Instance refresh configuration
  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
      instance_warmup        = 300
    }
  }
  
  # Enable metrics collection
  enabled_metrics = [
    "GroupMinSize",
    "GroupMaxSize",
    "GroupDesiredCapacity",
    "GroupInServiceInstances",
    "GroupTotalInstances"
  ]
  
  # Tags propagate to instances
  tag {
    key                 = "Name"
    value               = "flipkart-asg-instance"
    propagate_at_launch = true
  }
  
  tag {
    key                 = "Environment"
    value               = "production"
    propagate_at_launch = true
  }
  
  tag {
    key                 = "Application"
    value               = "flipkart-main"
    propagate_at_launch = true
  }
  
  # Lifecycle hooks for graceful shutdowns
  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Policies
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "flipkart-scale-up"
  scaling_adjustment     = 2  # Add 2 instances
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.app_asg.name
  
  policy_type = "SimpleScaling"
}

resource "aws_autoscaling_policy" "scale_down" {
  name                   = "flipkart-scale-down"
  scaling_adjustment     = -1  # Remove 1 instance
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.app_asg.name
  
  policy_type = "SimpleScaling"
}

# CloudWatch Alarms for Auto Scaling
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "flipkart-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "70"  # 70% CPU utilization
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]
  
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app_asg.name
  }
  
  tags = {
    Name        = "flipkart-high-cpu-alarm"
    Environment = "production"
    Purpose     = "Auto scaling trigger for high CPU"
  }
}

resource "aws_cloudwatch_metric_alarm" "low_cpu" {
  alarm_name          = "flipkart-low-cpu"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "20"  # 20% CPU utilization
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_down.arn]
  
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app_asg.name
  }
  
  tags = {
    Name        = "flipkart-low-cpu-alarm"
    Environment = "production"
    Purpose     = "Auto scaling trigger for low CPU"
  }
}

# Outputs
output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.app_lb.dns_name
}

output "load_balancer_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.app_lb.zone_id
}

output "autoscaling_group_arn" {
  description = "ARN of the Auto Scaling Group"
  value       = aws_autoscaling_group.app_asg.arn
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = aws_lb_target_group.app_tg.arn
}

# Local values for configuration
locals {
  # Auto scaling configuration based on Indian traffic patterns
  indian_business_hours = {
    scale_up_schedule   = "0 8 * * MON-SAT"   # Scale up at 8 AM IST
    scale_down_schedule = "0 23 * * MON-SAT"  # Scale down at 11 PM IST
  }
  
  # Instance types for different workloads
  instance_types = {
    development = "t3.micro"
    staging     = "t3.small"
    production  = "t3.medium"
  }
}

# Scheduled Actions for Auto Scaling (Indian business hours)
resource "aws_autoscaling_schedule" "scale_up_morning" {
  scheduled_action_name  = "scale-up-morning"
  min_size               = 3
  max_size               = 10
  desired_capacity       = 5
  recurrence             = local.indian_business_hours.scale_up_schedule
  autoscaling_group_name = aws_autoscaling_group.app_asg.name
}

resource "aws_autoscaling_schedule" "scale_down_evening" {
  scheduled_action_name  = "scale-down-evening"
  min_size               = 2
  max_size               = 10
  desired_capacity       = 2
  recurrence             = local.indian_business_hours.scale_down_schedule
  autoscaling_group_name = aws_autoscaling_group.app_asg.name
}
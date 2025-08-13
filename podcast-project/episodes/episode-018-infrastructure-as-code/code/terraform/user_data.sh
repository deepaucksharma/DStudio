#!/bin/bash
# User Data Script for Flipkart Application Servers
# यह script EC2 instance launch के time run होती है

# Log all output for debugging
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "Starting user data script execution at $(date)"

# Update system packages
echo "Updating system packages..."
yum update -y

# Install essential packages
echo "Installing essential packages..."
yum install -y \
    wget \
    curl \
    git \
    htop \
    unzip \
    vim \
    awscli \
    amazon-cloudwatch-agent \
    docker

# Start and enable Docker
echo "Setting up Docker..."
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Node.js (for web application)
echo "Installing Node.js..."
curl -sL https://rpm.nodesource.com/setup_18.x | bash -
yum install -y nodejs

# Install Java (for backend services)
echo "Installing Java..."
yum install -y java-11-amazon-corretto-headless

# Install Nginx (as reverse proxy)
echo "Installing Nginx..."
amazon-linux-extras install nginx1 -y

# Create application directories
echo "Creating application directories..."
mkdir -p /opt/flipkart-app
mkdir -p /var/log/flipkart-app
mkdir -p /opt/flipkart-app/config

# Create application user
echo "Creating application user..."
useradd -r -s /bin/false flipkart-app
chown -R flipkart-app:flipkart-app /opt/flipkart-app
chown -R flipkart-app:flipkart-app /var/log/flipkart-app

# Download and setup application (placeholder)
echo "Setting up application..."
cat > /opt/flipkart-app/app.js << 'EOF'
const express = require('express');
const app = express();
const port = 8080;

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    instance: process.env.INSTANCE_ID || 'unknown'
  });
});

// Main application endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Welcome to Flipkart Application',
    version: '1.0.0',
    region: process.env.AWS_REGION || 'ap-south-1',
    instance: process.env.INSTANCE_ID || 'unknown'
  });
});

// Load test endpoint
app.get('/api/products', (req, res) => {
  const products = [];
  for (let i = 1; i <= 100; i++) {
    products.push({
      id: i,
      name: `Product ${i}`,
      price: Math.floor(Math.random() * 10000) + 100,
      category: ['Electronics', 'Clothing', 'Books', 'Home'][Math.floor(Math.random() * 4)]
    });
  }
  res.json({
    products: products,
    total: products.length,
    timestamp: new Date().toISOString()
  });
});

app.listen(port, () => {
  console.log(`Flipkart app listening at http://localhost:${port}`);
});
EOF

# Create package.json
cat > /opt/flipkart-app/package.json << 'EOF'
{
  "name": "flipkart-app",
  "version": "1.0.0",
  "description": "Flipkart application for infrastructure demo",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
EOF

# Install application dependencies
echo "Installing application dependencies..."
cd /opt/flipkart-app
npm install
chown -R flipkart-app:flipkart-app /opt/flipkart-app

# Create systemd service for application
echo "Creating systemd service..."
cat > /etc/systemd/system/flipkart-app.service << 'EOF'
[Unit]
Description=Flipkart Application
After=network.target

[Service]
Type=simple
User=flipkart-app
WorkingDirectory=/opt/flipkart-app
ExecStart=/usr/bin/node app.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production
Environment=PORT=8080

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx as reverse proxy
echo "Configuring Nginx..."
cat > /etc/nginx/conf.d/flipkart-app.conf << 'EOF'
upstream flipkart_backend {
    server localhost:8080;
}

server {
    listen 80;
    server_name _;

    # Health check endpoint
    location /health {
        proxy_pass http://flipkart_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Main application
    location / {
        proxy_pass http://flipkart_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Static files (if any)
    location /static/ {
        alias /opt/flipkart-app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Configure CloudWatch agent
echo "Configuring CloudWatch agent..."
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOF'
{
    "metrics": {
        "namespace": "FlipkartApp/EC2",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_iowait", "cpu_usage_user", "cpu_usage_system"],
                "metrics_collection_interval": 300,
                "totalcpu": false
            },
            "disk": {
                "measurement": ["used_percent"],
                "metrics_collection_interval": 300,
                "resources": ["*"]
            },
            "diskio": {
                "measurement": ["io_time"],
                "metrics_collection_interval": 300,
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": 300
            }
        }
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/flipkart-app/*.log",
                        "log_group_name": "/aws/ec2/flipkart-app",
                        "log_stream_name": "{instance_id}/application"
                    },
                    {
                        "file_path": "/var/log/nginx/access.log",
                        "log_group_name": "/aws/ec2/flipkart-app",
                        "log_stream_name": "{instance_id}/nginx-access"
                    },
                    {
                        "file_path": "/var/log/nginx/error.log",
                        "log_group_name": "/aws/ec2/flipkart-app",
                        "log_stream_name": "{instance_id}/nginx-error"
                    }
                ]
            }
        }
    }
}
EOF

# Create log rotation for application logs
echo "Setting up log rotation..."
cat > /etc/logrotate.d/flipkart-app << 'EOF'
/var/log/flipkart-app/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 flipkart-app flipkart-app
    postrotate
        systemctl reload flipkart-app
    endscript
}
EOF

# Set up cron jobs for maintenance
echo "Setting up cron jobs..."
cat > /etc/cron.d/flipkart-maintenance << 'EOF'
# Clean up old log files
0 2 * * * root find /var/log -name "*.log" -type f -mtime +30 -delete

# Update system packages weekly
0 3 * * 0 root yum update -y

# Health check and restart if needed
*/5 * * * * root curl -f http://localhost:8080/health || systemctl restart flipkart-app
EOF

# Install additional monitoring tools
echo "Installing monitoring tools..."
yum install -y \
    collectd \
    iostat \
    iftop \
    nload

# Configure firewall (if enabled)
echo "Configuring firewall..."
systemctl status firewalld >/dev/null 2>&1
if [ $? -eq 0 ]; then
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=8080/tcp
    firewall-cmd --reload
fi

# Get instance metadata
echo "Retrieving instance metadata..."
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)

# Set environment variables
echo "Setting environment variables..."
echo "export INSTANCE_ID=$INSTANCE_ID" >> /etc/environment
echo "export AWS_REGION=$REGION" >> /etc/environment
echo "export AVAILABILITY_ZONE=$AZ" >> /etc/environment

# Create status file
echo "Creating status file..."
cat > /opt/flipkart-app/instance-info.json << EOF
{
    "instance_id": "$INSTANCE_ID",
    "availability_zone": "$AZ",
    "region": "$REGION",
    "launch_time": "$(date -Iseconds)",
    "application": "flipkart-app",
    "version": "1.0.0"
}
EOF

# Enable and start services
echo "Starting services..."
systemctl daemon-reload
systemctl enable flipkart-app
systemctl enable nginx
systemctl enable amazon-cloudwatch-agent

systemctl start flipkart-app
systemctl start nginx
systemctl start amazon-cloudwatch-agent

# Wait for application to start
echo "Waiting for application to start..."
sleep 30

# Health check
echo "Performing health check..."
if curl -f http://localhost:8080/health; then
    echo "Application health check passed"
else
    echo "Application health check failed"
    systemctl status flipkart-app
fi

# Send success signal to CloudFormation (if using CloudFormation)
# /opt/aws/bin/cfn-signal -e $? --stack ${AWS::StackName} --resource AutoScalingGroup --region ${AWS::Region}

echo "User data script completed successfully at $(date)"

# Final system status
echo "=== Final System Status ==="
echo "Services status:"
systemctl is-active flipkart-app
systemctl is-active nginx
systemctl is-active amazon-cloudwatch-agent

echo "Application response:"
curl -s http://localhost:8080/health | jq . 2>/dev/null || echo "Application not responding"

echo "System resources:"
free -h
df -h

echo "Network status:"
netstat -tlnp | grep -E ':(80|8080)'

echo "Instance metadata:"
cat /opt/flipkart-app/instance-info.json

echo "Setup completed!"
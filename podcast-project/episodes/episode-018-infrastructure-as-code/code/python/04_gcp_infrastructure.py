#!/usr/bin/env python3
"""
Google Cloud Platform Infrastructure Setup using Pulumi
Episode 18: Infrastructure as Code

GCP में comprehensive infrastructure deployment।
Mumbai region (asia-south1) में optimized for Indian companies।

Cost Estimate: ₹18,000-30,000 per month for production setup
"""

import pulumi
import pulumi_gcp as gcp
from pulumi import Config, Output

config = Config()
environment = config.get("environment") or "dev"
project_name = config.get("project_name") or "ola-app"
region = config.get("region") or "asia-south1"  # Mumbai region
zone = config.get("zone") or "asia-south1-a"

# Project ID should be globally unique
project_id = f"{project_name}-{environment}-infra-2024"

# Common labels for all resources
common_labels = {
    "environment": environment,
    "project": project_name.replace("-", "_"),
    "managed_by": "pulumi_iac",
    "region": "mumbai",
    "data_residency": "india",
    "compliance_zone": "in"
}

# Enable necessary APIs
compute_api = gcp.projects.Service(
    "compute-api",
    service="compute.googleapis.com",
    disable_on_destroy=False
)

container_api = gcp.projects.Service(
    "container-api",
    service="container.googleapis.com",
    disable_on_destroy=False,
    opts=pulumi.ResourceOptions(depends_on=[compute_api])
)

sql_api = gcp.projects.Service(
    "sql-api", 
    service="sqladmin.googleapis.com",
    disable_on_destroy=False,
    opts=pulumi.ResourceOptions(depends_on=[compute_api])
)

# VPC Network - Mumbai में optimized
vpc_network = gcp.compute.Network(
    "main-vpc",
    name=f"{project_name}-vpc-{environment}",
    auto_create_subnetworks=False,
    description=f"Main VPC for {project_name} in Mumbai region"
)

# Subnets for different tiers
# Web Tier Subnet
web_subnet = gcp.compute.Subnetwork(
    "web-subnet",
    name=f"{project_name}-web-subnet-{environment}",
    network=vpc_network.id,
    region=region,
    ip_cidr_range="10.0.1.0/24",
    description="Subnet for web servers",
    secondary_ip_ranges=[
        gcp.compute.SubnetworkSecondaryIpRangeArgs(
            range_name="web-pods",
            ip_cidr_range="10.1.0.0/16"
        ),
        gcp.compute.SubnetworkSecondaryIpRangeArgs(
            range_name="web-services", 
            ip_cidr_range="10.2.0.0/16"
        )
    ]
)

# Application Tier Subnet
app_subnet = gcp.compute.Subnetwork(
    "app-subnet",
    name=f"{project_name}-app-subnet-{environment}",
    network=vpc_network.id,
    region=region,
    ip_cidr_range="10.0.2.0/24",
    description="Subnet for application servers",
    secondary_ip_ranges=[
        gcp.compute.SubnetworkSecondaryIpRangeArgs(
            range_name="app-pods",
            ip_cidr_range="10.3.0.0/16"
        ),
        gcp.compute.SubnetworkSecondaryIpRangeArgs(
            range_name="app-services",
            ip_cidr_range="10.4.0.0/16"
        )
    ]
)

# Database Tier Subnet
db_subnet = gcp.compute.Subnetwork(
    "db-subnet",
    name=f"{project_name}-db-subnet-{environment}",
    network=vpc_network.id,
    region=region,
    ip_cidr_range="10.0.3.0/24",
    description="Subnet for database servers"
)

# Cloud NAT Router for private instance internet access
nat_router = gcp.compute.Router(
    "nat-router",
    name=f"{project_name}-nat-router-{environment}",
    region=region,
    network=vpc_network.id,
    description="Router for Cloud NAT"
)

# Cloud NAT Gateway
nat_gateway = gcp.compute.RouterNat(
    "nat-gateway",
    name=f"{project_name}-nat-gateway-{environment}",
    router=nat_router.name,
    region=region,
    nat_ip_allocate_option="AUTO_ONLY",
    source_subnetwork_ip_ranges_to_nat="ALL_SUBNETWORKS_ALL_IP_RANGES",
    log_config=gcp.compute.RouterNatLogConfigArgs(
        enable=True,
        filter="ERRORS_ONLY"
    )
)

# Firewall Rules
# Web tier firewall - Allow HTTP/HTTPS
web_firewall = gcp.compute.Firewall(
    "web-firewall",
    name=f"{project_name}-web-fw-{environment}",
    network=vpc_network.id,
    description="Firewall for web tier",
    allows=[
        gcp.compute.FirewallAllowArgs(
            protocol="tcp",
            ports=["80", "443"]
        )
    ],
    source_ranges=["0.0.0.0/0"],
    target_tags=["web-server"],
    priority=1000
)

# SSH firewall - Office access only
ssh_firewall = gcp.compute.Firewall(
    "ssh-firewall", 
    name=f"{project_name}-ssh-fw-{environment}",
    network=vpc_network.id,
    description="SSH access from office",
    allows=[
        gcp.compute.FirewallAllowArgs(
            protocol="tcp",
            ports=["22"]
        )
    ],
    source_ranges=["203.192.xxx.xxx/32"],  # Office IP
    target_tags=["ssh-allowed"],
    priority=1000
)

# Internal communication firewall
internal_firewall = gcp.compute.Firewall(
    "internal-firewall",
    name=f"{project_name}-internal-fw-{environment}",
    network=vpc_network.id,
    description="Internal communication between tiers",
    allows=[
        gcp.compute.FirewallAllowArgs(
            protocol="tcp",
            ports=["8080", "3306", "6379"]
        ),
        gcp.compute.FirewallAllowArgs(
            protocol="icmp"
        )
    ],
    source_ranges=["10.0.0.0/16"],
    target_tags=["internal-server"],
    priority=1000
)

# Instance Template for Web Servers
web_instance_template = gcp.compute.InstanceTemplate(
    "web-template",
    name=f"{project_name}-web-template-{environment}",
    description="Template for web servers",
    machine_type="e2-medium",  # Cost-effective choice
    region=region,
    tags=["web-server", "ssh-allowed", "internal-server"],
    labels=common_labels,
    disks=[
        gcp.compute.InstanceTemplateDiskArgs(
            source_image="projects/ubuntu-os-cloud/global/images/family/ubuntu-2004-lts",
            auto_delete=True,
            boot=True,
            disk_size_gb=20,
            disk_type="pd-standard"
        )
    ],
    network_interfaces=[
        gcp.compute.InstanceTemplateNetworkInterfaceArgs(
            network=vpc_network.id,
            subnetwork=web_subnet.id,
            # No external IP - will use Cloud NAT
        )
    ],
    metadata_startup_script="""#!/bin/bash
# Web server setup script for Ola application
apt-get update
apt-get install -y nginx nodejs npm

# Install PM2 for Node.js process management
npm install -g pm2

# Create Ola application structure
mkdir -p /var/www/ola-app
cat > /var/www/ola-app/app.js << 'EOF'
const express = require('express');
const app = express();
const port = 8080;

app.get('/', (req, res) => {
  res.json({
    message: 'Ola Ride Service - Mumbai',
    server: require('os').hostname(),
    environment: process.env.NODE_ENV || 'production',
    region: 'asia-south1',
    timestamp: new Date().toISOString(),
    hindi_message: 'ओला में आपका स्वागत है!'
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.listen(port, () => {
  console.log(`Ola app listening at http://localhost:${port}`);
});
EOF

# Create package.json
cat > /var/www/ola-app/package.json << 'EOF'
{
  "name": "ola-ride-service",
  "version": "1.0.0",
  "description": "Ola ride booking service",
  "main": "app.js",
  "dependencies": {
    "express": "^4.18.0"
  },
  "scripts": {
    "start": "node app.js"
  }
}
EOF

# Install dependencies
cd /var/www/ola-app
npm install

# Start application with PM2
pm2 start app.js --name "ola-app"
pm2 startup
pm2 save

# Configure Nginx as reverse proxy
cat > /etc/nginx/sites-available/ola-app << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    location /health {
        proxy_pass http://localhost:8080/health;
    }
}
EOF

ln -s /etc/nginx/sites-available/ola-app /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
systemctl restart nginx
systemctl enable nginx

echo "Web server setup completed for Ola application"
""",
    service_account=gcp.compute.InstanceTemplateServiceAccountArgs(
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform"
        ]
    )
)

# Managed Instance Group for Auto Scaling
web_instance_group = gcp.compute.RegionInstanceGroupManager(
    "web-instance-group",
    name=f"{project_name}-web-ig-{environment}",
    region=region,
    base_instance_name=f"{project_name}-web",
    version=[
        gcp.compute.RegionInstanceGroupManagerVersionArgs(
            instance_template=web_instance_template.id
        )
    ],
    target_size=2,  # Start with 2 instances
    named_ports=[
        gcp.compute.RegionInstanceGroupManagerNamedPortArgs(
            name="http",
            port=80
        )
    ],
    auto_healing_policies=gcp.compute.RegionInstanceGroupManagerAutoHealingPoliciesArgs(
        health_check=web_instance_template.id,
        initial_delay_sec=300
    )
)

# Health Check for Load Balancer
health_check = gcp.compute.HttpHealthCheck(
    "web-health-check",
    name=f"{project_name}-web-hc-{environment}",
    description="Health check for web servers",
    request_path="/health",
    port=80,
    check_interval_sec=10,
    timeout_sec=5,
    healthy_threshold=2,
    unhealthy_threshold=3
)

# Backend Service
backend_service = gcp.compute.RegionBackendService(
    "web-backend-service",
    name=f"{project_name}-web-backend-{environment}",
    region=region,
    description="Backend service for web tier",
    health_checks=[health_check.id],
    backends=[
        gcp.compute.RegionBackendServiceBackendArgs(
            group=web_instance_group.instance_group,
            balancing_mode="UTILIZATION",
            max_utilization=0.8,
            capacity_scaler=1.0
        )
    ],
    session_affinity="NONE",
    timeout_sec=30
)

# URL Map
url_map = gcp.compute.RegionUrlMap(
    "web-url-map",
    name=f"{project_name}-web-urlmap-{environment}",
    region=region,
    description="URL map for web traffic",
    default_service=backend_service.id
)

# HTTP Proxy
http_proxy = gcp.compute.RegionTargetHttpProxy(
    "web-http-proxy",
    name=f"{project_name}-web-proxy-{environment}",
    region=region,
    description="HTTP proxy for web traffic",
    url_map=url_map.id
)

# Static IP for Load Balancer
static_ip = gcp.compute.Address(
    "web-static-ip",
    name=f"{project_name}-web-ip-{environment}",
    region=region,
    description="Static IP for web load balancer"
)

# Regional Load Balancer
load_balancer = gcp.compute.ForwardingRule(
    "web-load-balancer",
    name=f"{project_name}-web-lb-{environment}",
    region=region,
    description="Load balancer for web tier",
    ip_address=static_ip.address,
    ip_protocol="TCP",
    port_range="80",
    target=http_proxy.id
)

# Cloud SQL Instance for MySQL
sql_instance = gcp.sql.DatabaseInstance(
    "mysql-instance",
    name=f"{project_name}-mysql-{environment}",
    region=region,
    database_version="MYSQL_8_0",
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-f1-micro",  # Cost-effective for development
        disk_size=20,
        disk_type="PD_SSD",
        disk_autoresize=True,
        backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
            enabled=True,
            start_time="02:00",  # 2 AM IST backup
            location="asia-south1"
        ),
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            ipv4_enabled=False,  # Private IP only
            private_network=vpc_network.id,
            require_ssl=True
        ),
        availability_type="ZONAL",  # Regional for production
        user_labels=common_labels
    ),
    opts=pulumi.ResourceOptions(depends_on=[sql_api])
)

# Private service connection for Cloud SQL
private_vpc_connection = gcp.servicenetworking.Connection(
    "private-vpc-connection",
    network=vpc_network.id,
    service="servicenetworking.googleapis.com",
    reserved_peering_ranges=["google-managed-services-default"]
)

# Allocate IP range for private services
private_ip_range = gcp.compute.GlobalAddress(
    "private-ip-range",
    name=f"{project_name}-private-ip-range-{environment}",
    purpose="VPC_PEERING",
    address_type="INTERNAL",
    prefix_length=16,
    network=vpc_network.id
)

# Create database
app_database = gcp.sql.Database(
    "app-database",
    name=f"{project_name}_app_db",
    instance=sql_instance.name
)

# Create database user
db_user = gcp.sql.User(
    "app-db-user",
    name="ola_app_user",
    instance=sql_instance.name,
    password="OLA@DB2024#Secure",  # Production में Secret Manager से
    type="BUILT_IN"
)

# Redis (Memorystore) for caching
redis_instance = gcp.redis.Instance(
    "redis-cache",
    name=f"{project_name}-redis-{environment}",
    region=region,
    memory_size_gb=1,  # Small instance for development
    tier="BASIC",
    redis_version="REDIS_6_X",
    display_name="Ola App Redis Cache",
    authorized_network=vpc_network.id,
    labels=common_labels
)

# Cloud Storage bucket for static assets
storage_bucket = gcp.storage.Bucket(
    "app-storage",
    name=f"{project_name}-storage-{environment}-{region}",
    location=region.upper(),
    uniform_bucket_level_access=True,
    labels=common_labels
)

# GKE Cluster for containerized applications
gke_cluster = gcp.container.Cluster(
    "gke-cluster",
    name=f"{project_name}-gke-{environment}",
    location=zone,
    description="GKE cluster for Ola microservices",
    remove_default_node_pool=True,
    initial_node_count=1,
    network=vpc_network.id,
    subnetwork=app_subnet.id,
    ip_allocation_policy=gcp.container.ClusterIpAllocationPolicyArgs(
        cluster_secondary_range_name="app-pods",
        services_secondary_range_name="app-services"
    ),
    networking_mode="VPC_NATIVE",
    release_channel=gcp.container.ClusterReleaseChannelArgs(
        channel="STABLE"
    ),
    workload_identity_config=gcp.container.ClusterWorkloadIdentityConfigArgs(
        workload_pool=f"{project_id}.svc.id.goog"
    ),
    addons_config=gcp.container.ClusterAddonsConfigArgs(
        http_load_balancing=gcp.container.ClusterAddonsConfigHttpLoadBalancingArgs(
            disabled=False
        ),
        horizontal_pod_autoscaling=gcp.container.ClusterAddonsConfigHorizontalPodAutoscalingArgs(
            disabled=False
        )
    ),
    opts=pulumi.ResourceOptions(depends_on=[container_api])
)

# GKE Node Pool
gke_node_pool = gcp.container.NodePool(
    "gke-node-pool",
    name=f"{project_name}-nodes-{environment}",
    location=zone,
    cluster=gke_cluster.name,
    initial_node_count=2,
    management=gcp.container.NodePoolManagementArgs(
        auto_repair=True,
        auto_upgrade=True
    ),
    node_config=gcp.container.NodePoolNodeConfigArgs(
        preemptible=True,  # Cost savings for development
        machine_type="e2-medium",
        disk_size_gb=20,
        disk_type="pd-standard",
        oauth_scopes=[
            "https://www.googleapis.com/auth/cloud-platform"
        ],
        labels=common_labels,
        tags=["gke-node", "internal-server"]
    ),
    autoscaling=gcp.container.NodePoolAutoscalingArgs(
        min_node_count=1,
        max_node_count=5
    )
)

# Cloud Monitoring Alert Policy
alert_policy = gcp.monitoring.AlertPolicy(
    "high-cpu-alert",
    display_name=f"{project_name} High CPU Alert - {environment}",
    description="Alert when CPU usage is high",
    combiner="OR",
    conditions=[
        gcp.monitoring.AlertPolicyConditionArgs(
            display_name="High CPU Usage",
            condition_threshold=gcp.monitoring.AlertPolicyConditionConditionThresholdArgs(
                filter=f'resource.type="gce_instance" AND resource.label.project_id="{project_id}"',
                comparison="COMPARISON_GT",
                threshold_value=0.8,
                duration="300s",
                aggregations=[
                    gcp.monitoring.AlertPolicyConditionConditionThresholdAggregationArgs(
                        alignment_period="300s",
                        per_series_aligner="ALIGN_MEAN",
                        cross_series_reducer="REDUCE_MEAN"
                    )
                ]
            )
        )
    ],
    notification_channels=[],  # Add notification channels as needed
    alert_strategy=gcp.monitoring.AlertPolicyAlertStrategyArgs(
        auto_close="1800s"
    )
)

# Outputs
pulumi.export("vpc_network_id", vpc_network.id)
pulumi.export("vpc_network_name", vpc_network.name)
pulumi.export("web_subnet_id", web_subnet.id)
pulumi.export("app_subnet_id", app_subnet.id)
pulumi.export("load_balancer_ip", static_ip.address)
pulumi.export("sql_instance_ip", sql_instance.private_ip_address)
pulumi.export("redis_host", redis_instance.host)
pulumi.export("storage_bucket_url", storage_bucket.url)
pulumi.export("gke_cluster_name", gke_cluster.name)
pulumi.export("gke_cluster_endpoint", gke_cluster.endpoint)

# Cost estimation for GCP Mumbai region
monthly_cost_estimate = Output.concat(
    f"GCP Infrastructure monthly cost (Mumbai region):\n",
    "- VPC Network: Free (data charges apply)\n",
    "- Compute Instances (2x e2-medium): ₹8,000/month\n",
    "- Load Balancer: ₹1,500/month\n",
    "- Cloud SQL (db-f1-micro): ₹3,000/month\n",
    "- Redis (1GB Basic): ₹4,000/month\n",
    "- Cloud Storage: ₹500/month (estimated)\n",
    "- GKE Cluster: ₹6,000/month (management fee + nodes)\n",
    "- Monitoring & Logging: ₹1,000/month\n",
    "Total estimated: ₹24,000-30,000/month\n",
    "Note: Preemptible instances can reduce costs by 60-80%"
)

pulumi.export("cost_estimate", monthly_cost_estimate)
pulumi.export("region_info", f"Deployed in {region} (Mumbai) for low latency to Indian users")
pulumi.export("setup_complete", "✅ GCP infrastructure deployed successfully in Mumbai region!")
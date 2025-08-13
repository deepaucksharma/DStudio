#!/usr/bin/env python3
"""
AWS VPC Setup using Pulumi - Mumbai Region
Episode 18: Infrastructure as Code

यह example दिखाता है कि कैसे Pulumi के साथ AWS में VPC setup करें।
Mumbai region में optimized setup के साथ Indian companies के लिए।

Cost Estimate: ₹5,000-8,000 per month for production setup
"""

import pulumi
import pulumi_aws as aws
from pulumi import Config, Output

# Configuration - Pulumi.yaml से values
config = Config()
environment = config.get("environment") or "dev"
project_name = config.get("project_name") or "flipkart-vpc"

# Mumbai region me setup karte hain
aws_provider = aws.Provider("mumbai-provider", region="ap-south-1")

# Tags jo har resource par lagenge
common_tags = {
    "Environment": environment,
    "Project": project_name,
    "ManagedBy": "Pulumi",
    "Region": "Mumbai",
    "DataResidency": "India"  # Indian data compliance के लिए
}

# VPC create करें - Mumbai के लिए optimized
main_vpc = aws.ec2.Vpc(
    "flipkart-main-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        **common_tags,
        "Name": f"{project_name}-vpc-{environment}"
    },
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Internet Gateway - बाहरी connectivity के लिए
internet_gateway = aws.ec2.InternetGateway(
    "flipkart-igw",
    vpc_id=main_vpc.id,
    tags={
        **common_tags,
        "Name": f"{project_name}-igw-{environment}"
    },
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Availability Zones - Mumbai में available AZs
availability_zones = aws.get_availability_zones(
    state="available",
    opts=pulumi.InvokeOptions(provider=aws_provider)
)

# Public Subnets - Web servers के लिए
public_subnets = []
for i in range(2):  # 2 AZs में distribute करें
    subnet = aws.ec2.Subnet(
        f"public-subnet-{i+1}",
        vpc_id=main_vpc.id,
        cidr_block=f"10.0.{i+1}.0/24",
        availability_zone=availability_zones.names[i],
        map_public_ip_on_launch=True,
        tags={
            **common_tags,
            "Name": f"{project_name}-public-subnet-{i+1}-{environment}",
            "Type": "Public",
            "Tier": "Web"
        },
        opts=pulumi.ResourceOptions(provider=aws_provider)
    )
    public_subnets.append(subnet)

# Private Subnets - Application servers के लिए
private_subnets = []
for i in range(2):
    subnet = aws.ec2.Subnet(
        f"private-subnet-{i+1}",
        vpc_id=main_vpc.id,
        cidr_block=f"10.0.{i+10}.0/24",
        availability_zone=availability_zones.names[i],
        tags={
            **common_tags,
            "Name": f"{project_name}-private-subnet-{i+1}-{environment}",
            "Type": "Private",
            "Tier": "Application"
        },
        opts=pulumi.ResourceOptions(provider=aws_provider)
    )
    private_subnets.append(subnet)

# Database Subnets - RDS के लिए
db_subnets = []
for i in range(2):
    subnet = aws.ec2.Subnet(
        f"db-subnet-{i+1}",
        vpc_id=main_vpc.id,
        cidr_block=f"10.0.{i+20}.0/24",
        availability_zone=availability_zones.names[i],
        tags={
            **common_tags,
            "Name": f"{project_name}-db-subnet-{i+1}-{environment}",
            "Type": "Private",
            "Tier": "Database"
        },
        opts=pulumi.ResourceOptions(provider=aws_provider)
    )
    db_subnets.append(subnet)

# NAT Gateway - Private subnets के लिए internet access
# Production में 2 NAT Gateways (multi-AZ), dev में 1
nat_gateway_count = 2 if environment == "prod" else 1

nat_gateways = []
for i in range(nat_gateway_count):
    # Elastic IP for NAT Gateway
    eip = aws.ec2.Eip(
        f"nat-eip-{i+1}",
        domain="vpc",
        tags={
            **common_tags,
            "Name": f"{project_name}-nat-eip-{i+1}-{environment}"
        },
        opts=pulumi.ResourceOptions(provider=aws_provider)
    )
    
    # NAT Gateway
    nat_gw = aws.ec2.NatGateway(
        f"nat-gateway-{i+1}",
        allocation_id=eip.id,
        subnet_id=public_subnets[i].id,
        tags={
            **common_tags,
            "Name": f"{project_name}-nat-gateway-{i+1}-{environment}"
        },
        opts=pulumi.ResourceOptions(provider=aws_provider)
    )
    nat_gateways.append(nat_gw)

# Route Tables
# Public Route Table
public_route_table = aws.ec2.RouteTable(
    "public-rt",
    vpc_id=main_vpc.id,
    tags={
        **common_tags,
        "Name": f"{project_name}-public-rt-{environment}",
        "Type": "Public"
    },
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Public route to Internet Gateway
public_route = aws.ec2.Route(
    "public-route",
    route_table_id=public_route_table.id,
    destination_cidr_block="0.0.0.0/0",
    gateway_id=internet_gateway.id,
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Associate public subnets with public route table
for i, subnet in enumerate(public_subnets):
    aws.ec2.RouteTableAssociation(
        f"public-rta-{i+1}",
        subnet_id=subnet.id,
        route_table_id=public_route_table.id,
        opts=pulumi.ResourceOptions(provider=aws_provider)
    )

# Private Route Tables (one per NAT Gateway for HA)
private_route_tables = []
for i in range(len(nat_gateways)):
    rt = aws.ec2.RouteTable(
        f"private-rt-{i+1}",
        vpc_id=main_vpc.id,
        tags={
            **common_tags,
            "Name": f"{project_name}-private-rt-{i+1}-{environment}",
            "Type": "Private"
        },
        opts=pulumi.ResourceOptions(provider=aws_provider)
    )
    
    # Route to NAT Gateway
    aws.ec2.Route(
        f"private-route-{i+1}",
        route_table_id=rt.id,
        destination_cidr_block="0.0.0.0/0",
        nat_gateway_id=nat_gateways[i].id,
        opts=pulumi.ResourceOptions(provider=aws_provider)
    )
    
    private_route_tables.append(rt)

# Associate private subnets with private route tables
for i, subnet in enumerate(private_subnets):
    rt_index = i % len(private_route_tables)  # Distribute across available route tables
    aws.ec2.RouteTableAssociation(
        f"private-rta-{i+1}",
        subnet_id=subnet.id,
        route_table_id=private_route_tables[rt_index].id,
        opts=pulumi.ResourceOptions(provider=aws_provider)
    )

# Database Subnet Group for RDS
db_subnet_group = aws.rds.SubnetGroup(
    "db-subnet-group",
    subnet_ids=[subnet.id for subnet in db_subnets],
    tags={
        **common_tags,
        "Name": f"{project_name}-db-subnet-group-{environment}"
    },
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Security Groups
# Web Server Security Group
web_sg = aws.ec2.SecurityGroup(
    "web-security-group",
    description="Security group for web servers",
    vpc_id=main_vpc.id,
    ingress=[
        # HTTP traffic
        aws.ec2.SecurityGroupIngressArgs(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"]
        ),
        # HTTPS traffic
        aws.ec2.SecurityGroupIngressArgs(
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"]
        ),
        # SSH (केवल office IP से - example)
        aws.ec2.SecurityGroupIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["203.192.xxx.xxx/32"]  # Replace with actual office IP
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"]
        )
    ],
    tags={
        **common_tags,
        "Name": f"{project_name}-web-sg-{environment}"
    },
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Application Server Security Group
app_sg = aws.ec2.SecurityGroup(
    "app-security-group",
    description="Security group for application servers",
    vpc_id=main_vpc.id,
    ingress=[
        # Application port (केवल web servers से)
        aws.ec2.SecurityGroupIngressArgs(
            from_port=8080,
            to_port=8080,
            protocol="tcp",
            security_groups=[web_sg.id]
        ),
        # SSH from web servers
        aws.ec2.SecurityGroupIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            security_groups=[web_sg.id]
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"]
        )
    ],
    tags={
        **common_tags,
        "Name": f"{project_name}-app-sg-{environment}"
    },
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Database Security Group
db_sg = aws.ec2.SecurityGroup(
    "db-security-group",
    description="Security group for database servers",
    vpc_id=main_vpc.id,
    ingress=[
        # MySQL/MariaDB port (केवल app servers से)
        aws.ec2.SecurityGroupIngressArgs(
            from_port=3306,
            to_port=3306,
            protocol="tcp",
            security_groups=[app_sg.id]
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"]
        )
    ],
    tags={
        **common_tags,
        "Name": f"{project_name}-db-sg-{environment}"
    },
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# VPC Endpoints for cost optimization (private connectivity to AWS services)
# S3 VPC Endpoint
s3_endpoint = aws.ec2.VpcEndpoint(
    "s3-endpoint",
    vpc_id=main_vpc.id,
    service_name=f"com.amazonaws.ap-south-1.s3",
    vpc_endpoint_type="Gateway",
    route_table_ids=[rt.id for rt in private_route_tables],
    tags={
        **common_tags,
        "Name": f"{project_name}-s3-endpoint-{environment}"
    },
    opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Outputs - दूसरे stacks में use के लिए
pulumi.export("vpc_id", main_vpc.id)
pulumi.export("vpc_cidr", main_vpc.cidr_block)
pulumi.export("public_subnet_ids", [subnet.id for subnet in public_subnets])
pulumi.export("private_subnet_ids", [subnet.id for subnet in private_subnets])
pulumi.export("db_subnet_ids", [subnet.id for subnet in db_subnets])
pulumi.export("db_subnet_group_name", db_subnet_group.name)
pulumi.export("web_security_group_id", web_sg.id)
pulumi.export("app_security_group_id", app_sg.id)
pulumi.export("db_security_group_id", db_sg.id)
pulumi.export("availability_zones", availability_zones.names)

# Cost estimation output
estimated_monthly_cost = Output.concat(
    "Estimated monthly cost in Mumbai region:\n",
    "- NAT Gateway: ₹", str(len(nat_gateways) * 3500), "/month\n",
    "- Elastic IPs: ₹", str(len(nat_gateways) * 300), "/month\n",
    "- Data Transfer: Variable based on usage\n",
    "Total Infrastructure: ₹", str((len(nat_gateways) * 3800) + 1000), "-", str((len(nat_gateways) * 3800) + 5000), "/month"
)

pulumi.export("cost_estimate", estimated_monthly_cost)

# Print completion message
pulumi.export("setup_complete", f"✅ VPC setup complete for {project_name} in {environment} environment")
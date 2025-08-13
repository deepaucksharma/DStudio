#!/usr/bin/env python3
"""
Azure Infrastructure Setup using Pulumi
Episode 18: Infrastructure as Code

Azure Cloud में comprehensive infrastructure setup।
Central India region में optimized for Indian enterprises।

Cost Estimate: ₹20,000-35,000 per month for production setup
"""

import pulumi
import pulumi_azure as azure
import pulumi_azure_native as azure_native
from pulumi import Config, Output

config = Config()
environment = config.get("environment") or "dev"
project_name = config.get("project_name") or "tcs-app"
location = config.get("location") or "Central India"  # Mumbai भी available है

# Common tags for all resources
common_tags = {
    "Environment": environment,
    "Project": project_name,
    "ManagedBy": "Pulumi-IaC",
    "Location": location,
    "DataResidency": "India",
    "ComplianceZone": "IN"
}

# Resource Group - सभी resources का container
resource_group = azure_native.resources.ResourceGroup(
    "main-rg",
    resource_group_name=f"{project_name}-rg-{environment}",
    location=location,
    tags=common_tags
)

# Virtual Network - Azure में networking
vnet = azure_native.network.VirtualNetwork(
    "main-vnet",
    resource_group_name=resource_group.name,
    virtual_network_name=f"{project_name}-vnet-{environment}",
    location=location,
    address_space=azure_native.network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"]
    ),
    tags=common_tags
)

# Subnets for different tiers
# Web Tier Subnet
web_subnet = azure_native.network.Subnet(
    "web-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    subnet_name="web-subnet",
    address_prefix="10.0.1.0/24"
)

# Application Tier Subnet
app_subnet = azure_native.network.Subnet(
    "app-subnet", 
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    subnet_name="app-subnet",
    address_prefix="10.0.2.0/24"
)

# Database Tier Subnet
db_subnet = azure_native.network.Subnet(
    "db-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    subnet_name="db-subnet", 
    address_prefix="10.0.3.0/24"
)

# Network Security Groups
# Web NSG - Public facing
web_nsg = azure_native.network.NetworkSecurityGroup(
    "web-nsg",
    resource_group_name=resource_group.name,
    network_security_group_name=f"{project_name}-web-nsg-{environment}",
    location=location,
    security_rules=[
        # HTTP Rule
        azure_native.network.SecurityRuleArgs(
            name="Allow-HTTP",
            priority=100,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="80",
            source_address_prefix="*",
            destination_address_prefix="*"
        ),
        # HTTPS Rule
        azure_native.network.SecurityRuleArgs(
            name="Allow-HTTPS",
            priority=110,
            direction="Inbound", 
            access="Allow",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="443",
            source_address_prefix="*",
            destination_address_prefix="*"
        ),
        # SSH Rule (केवल office IP से)
        azure_native.network.SecurityRuleArgs(
            name="Allow-SSH-Office",
            priority=120,
            direction="Inbound",
            access="Allow", 
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="22",
            source_address_prefix="203.192.xxx.xxx/32",  # Office IP
            destination_address_prefix="*"
        )
    ],
    tags=common_tags
)

# Application NSG - Internal traffic
app_nsg = azure_native.network.NetworkSecurityGroup(
    "app-nsg",
    resource_group_name=resource_group.name,
    network_security_group_name=f"{project_name}-app-nsg-{environment}",
    location=location,
    security_rules=[
        # Application port from web tier
        azure_native.network.SecurityRuleArgs(
            name="Allow-App-Port",
            priority=100,
            direction="Inbound",
            access="Allow",
            protocol="Tcp", 
            source_port_range="*",
            destination_port_range="8080",
            source_address_prefix="10.0.1.0/24",  # Web subnet
            destination_address_prefix="*"
        ),
        # SSH from web tier
        azure_native.network.SecurityRuleArgs(
            name="Allow-SSH-Web",
            priority=110,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_port_range="*", 
            destination_port_range="22",
            source_address_prefix="10.0.1.0/24",
            destination_address_prefix="*"
        )
    ],
    tags=common_tags
)

# Database NSG - Most restrictive
db_nsg = azure_native.network.NetworkSecurityGroup(
    "db-nsg",
    resource_group_name=resource_group.name,
    network_security_group_name=f"{project_name}-db-nsg-{environment}",
    location=location,
    security_rules=[
        # MySQL port from app tier only
        azure_native.network.SecurityRuleArgs(
            name="Allow-MySQL-App",
            priority=100,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="3306",
            source_address_prefix="10.0.2.0/24",  # App subnet
            destination_address_prefix="*"
        )
    ],
    tags=common_tags
)

# Associate NSGs with subnets
web_subnet_nsg_association = azure_native.network.SubnetNetworkSecurityGroupAssociation(
    "web-subnet-nsg",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    subnet_name=web_subnet.name,
    network_security_group_id=web_nsg.id
)

app_subnet_nsg_association = azure_native.network.SubnetNetworkSecurityGroupAssociation(
    "app-subnet-nsg",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    subnet_name=app_subnet.name,
    network_security_group_id=app_nsg.id
)

db_subnet_nsg_association = azure_native.network.SubnetNetworkSecurityGroupAssociation(
    "db-subnet-nsg",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    subnet_name=db_subnet.name,
    network_security_group_id=db_nsg.id
)

# Public IP for Load Balancer
public_ip = azure_native.network.PublicIPAddress(
    "lb-public-ip",
    resource_group_name=resource_group.name,
    public_ip_address_name=f"{project_name}-lb-ip-{environment}",
    location=location,
    public_ip_allocation_method="Static",
    sku=azure_native.network.PublicIPAddressSkuArgs(name="Standard"),
    tags=common_tags
)

# Application Gateway (Azure का Load Balancer + WAF)
app_gateway = azure_native.network.ApplicationGateway(
    "app-gateway",
    resource_group_name=resource_group.name,
    application_gateway_name=f"{project_name}-appgw-{environment}",
    location=location,
    sku=azure_native.network.ApplicationGatewaySkuArgs(
        name="WAF_v2",
        tier="WAF_v2",
        capacity=2  # Auto-scaling के लिए
    ),
    gateway_ip_configurations=[
        azure_native.network.ApplicationGatewayIPConfigurationArgs(
            name="appGwIpConfig",
            subnet=azure_native.network.SubResourceArgs(
                id=web_subnet.id
            )
        )
    ],
    frontend_ip_configurations=[
        azure_native.network.ApplicationGatewayFrontendIPConfigurationArgs(
            name="appGwPublicFrontendIp",
            public_ip_address=azure_native.network.SubResourceArgs(
                id=public_ip.id
            )
        )
    ],
    frontend_ports=[
        azure_native.network.ApplicationGatewayFrontendPortArgs(
            name="port_80",
            port=80
        ),
        azure_native.network.ApplicationGatewayFrontendPortArgs(
            name="port_443",
            port=443
        )
    ],
    backend_address_pools=[
        azure_native.network.ApplicationGatewayBackendAddressPoolArgs(
            name="webServerPool"
        )
    ],
    backend_http_settings_collection=[
        azure_native.network.ApplicationGatewayBackendHttpSettingsArgs(
            name="appGwBackendHttpSettings",
            port=80,
            protocol="Http",
            cookie_based_affinity="Disabled"
        )
    ],
    http_listeners=[
        azure_native.network.ApplicationGatewayHttpListenerArgs(
            name="appGwHttpListener",
            frontend_ip_configuration=azure_native.network.SubResourceArgs(
                id="/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Network/applicationGateways/{app-gateway}/frontendIPConfigurations/appGwPublicFrontendIp"
            ),
            frontend_port=azure_native.network.SubResourceArgs(
                id="/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Network/applicationGateways/{app-gateway}/frontendPorts/port_80"
            ),
            protocol="Http"
        )
    ],
    request_routing_rules=[
        azure_native.network.ApplicationGatewayRequestRoutingRuleArgs(
            name="rule1",
            rule_type="Basic",
            http_listener=azure_native.network.SubResourceArgs(
                id="/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Network/applicationGateways/{app-gateway}/httpListeners/appGwHttpListener"
            ),
            backend_address_pool=azure_native.network.SubResourceArgs(
                id="/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Network/applicationGateways/{app-gateway}/backendAddressPools/webServerPool"
            ),
            backend_http_settings=azure_native.network.SubResourceArgs(
                id="/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Network/applicationGateways/{app-gateway}/backendHttpSettingsCollection/appGwBackendHttpSettings"
            )
        )
    ],
    web_application_firewall_configuration=azure_native.network.ApplicationGatewayWebApplicationFirewallConfigurationArgs(
        enabled=True,
        firewall_mode="Prevention",
        rule_set_type="OWASP",
        rule_set_version="3.2"
    ),
    tags=common_tags
)

# Virtual Machine Scale Set for Web Servers
# First, create a custom image or use marketplace image
web_vmss = azure_native.compute.VirtualMachineScaleSet(
    "web-vmss",
    resource_group_name=resource_group.name,
    vm_scale_set_name=f"{project_name}-web-vmss-{environment}",
    location=location,
    sku=azure_native.compute.SkuArgs(
        name="Standard_B2s",  # Cost-effective for development
        tier="Standard",
        capacity=2
    ),
    upgrade_policy=azure_native.compute.UpgradePolicyArgs(
        mode="Automatic"
    ),
    virtual_machine_profile=azure_native.compute.VirtualMachineScaleSetVMProfileArgs(
        os_profile=azure_native.compute.VirtualMachineScaleSetOSProfileArgs(
            computer_name_prefix=f"{project_name}web",
            admin_username="azureuser",
            admin_password="TCS@2024#Secure",  # Production में Key Vault से
            linux_configuration=azure_native.compute.LinuxConfigurationArgs(
                disable_password_authentication=False
            )
        ),
        storage_profile=azure_native.compute.VirtualMachineScaleSetStorageProfileArgs(
            image_reference=azure_native.compute.ImageReferenceArgs(
                publisher="Canonical",
                offer="0001-com-ubuntu-server-focal",
                sku="20_04-lts-gen2", 
                version="latest"
            ),
            os_disk=azure_native.compute.VirtualMachineScaleSetOSDiskArgs(
                create_option="FromImage",
                managed_disk=azure_native.compute.VirtualMachineScaleSetManagedDiskParametersArgs(
                    storage_account_type="Premium_LRS"
                ),
                disk_size_gb=30
            )
        ),
        network_profile=azure_native.compute.VirtualMachineScaleSetNetworkProfileArgs(
            network_interface_configurations=[
                azure_native.compute.VirtualMachineScaleSetNetworkConfigurationArgs(
                    name="web-vmss-nic",
                    primary=True,
                    ip_configurations=[
                        azure_native.compute.VirtualMachineScaleSetIPConfigurationArgs(
                            name="internal",
                            subnet=azure_native.compute.ApiEntityReferenceArgs(
                                id=web_subnet.id
                            ),
                            application_gateway_backend_address_pools=[
                                azure_native.compute.SubResourceArgs(
                                    id=app_gateway.id.apply(lambda id: f"{id}/backendAddressPools/webServerPool")
                                )
                            ]
                        )
                    ],
                    network_security_group=azure_native.compute.SubResourceArgs(
                        id=web_nsg.id
                    )
                )
            ]
        ),
        extension_profile=azure_native.compute.VirtualMachineScaleSetExtensionProfileArgs(
            extensions=[
                # Custom script extension for web server setup
                azure_native.compute.VirtualMachineScaleSetExtensionArgs(
                    name="webServerSetup",
                    publisher="Microsoft.Azure.Extensions",
                    type="CustomScript",
                    type_handler_version="2.1",
                    settings={
                        "script": """
#!/bin/bash
# Web server setup script
apt-get update
apt-get install -y nginx
systemctl start nginx
systemctl enable nginx

# Create a simple HTML page with Indian context
cat > /var/www/html/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>TCS Application - India</title>
</head>
<body>
    <h1>Welcome to TCS Application</h1>
    <p>Server Location: Central India</p>
    <p>Environment: ${environment}</p>
    <p>Hostname: $(hostname)</p>
    <p>नमस्ते from Azure Infrastructure!</p>
</body>
</html>
EOF

# Configure nginx for health checks
cat > /etc/nginx/sites-available/health << EOF
server {
    listen 80;
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

ln -s /etc/nginx/sites-available/health /etc/nginx/sites-enabled/
systemctl reload nginx
"""
                    }
                )
            ]
        )
    ),
    tags=common_tags
)

# Auto-scaling rules for VMSS
autoscale_setting = azure_native.insights.AutoscaleSettingResource(
    "web-autoscale",
    resource_group_name=resource_group.name,
    autoscale_setting_name=f"{project_name}-web-autoscale-{environment}",
    location=location,
    target_resource_uri=web_vmss.id,
    enabled=True,
    profiles=[
        azure_native.insights.AutoscaleProfileArgs(
            name="defaultProfile",
            capacity=azure_native.insights.ScaleCapacityArgs(
                minimum="2",
                maximum="10",
                default="2"
            ),
            rules=[
                # Scale out rule
                azure_native.insights.ScaleRuleArgs(
                    metric_trigger=azure_native.insights.MetricTriggerArgs(
                        metric_name="Percentage CPU",
                        metric_resource_uri=web_vmss.id,
                        time_grain="PT1M",
                        statistic="Average",
                        time_window="PT5M",
                        time_aggregation="Average",
                        operator="GreaterThan",
                        threshold=75.0
                    ),
                    scale_action=azure_native.insights.ScaleActionArgs(
                        direction="Increase",
                        type="ChangeCount",
                        value="1",
                        cooldown="PT5M"
                    )
                ),
                # Scale in rule
                azure_native.insights.ScaleRuleArgs(
                    metric_trigger=azure_native.insights.MetricTriggerArgs(
                        metric_name="Percentage CPU",
                        metric_resource_uri=web_vmss.id,
                        time_grain="PT1M",
                        statistic="Average",
                        time_window="PT5M",
                        time_aggregation="Average",
                        operator="LessThan",
                        threshold=25.0
                    ),
                    scale_action=azure_native.insights.ScaleActionArgs(
                        direction="Decrease",
                        type="ChangeCount", 
                        value="1",
                        cooldown="PT5M"
                    )
                )
            ]
        )
    ],
    tags=common_tags
)

# Azure SQL Database for application data
sql_server = azure_native.sql.Server(
    "sql-server",
    resource_group_name=resource_group.name,
    server_name=f"{project_name}-sqlserver-{environment}",
    location=location,
    administrator_login="tcsadmin",
    administrator_login_password="TCS@SQL2024#Secure",  # Production में Key Vault
    version="12.0",
    tags=common_tags
)

# SQL Database
sql_database = azure_native.sql.Database(
    "sql-database",
    resource_group_name=resource_group.name,
    server_name=sql_server.name,
    database_name=f"{project_name}-db-{environment}",
    location=location,
    sku=azure_native.sql.SkuArgs(
        name="S2",  # Standard tier for development
        tier="Standard"
    ),
    max_size_bytes=268435456000,  # 250GB
    tags=common_tags
)

# Firewall rule for SQL Server (Allow Azure services)
sql_firewall_azure = azure_native.sql.FirewallRule(
    "sql-fw-azure",
    resource_group_name=resource_group.name,
    server_name=sql_server.name,
    firewall_rule_name="AllowAzureServices",
    start_ip_address="0.0.0.0",
    end_ip_address="0.0.0.0"
)

# Firewall rule for application subnet
sql_firewall_app = azure_native.sql.FirewallRule(
    "sql-fw-app",
    resource_group_name=resource_group.name,
    server_name=sql_server.name,
    firewall_rule_name="AllowAppSubnet",
    start_ip_address="10.0.2.0", 
    end_ip_address="10.0.2.255"
)

# Azure Storage Account for static content/backups
storage_account = azure_native.storage.StorageAccount(
    "storage",
    resource_group_name=resource_group.name,
    account_name=f"{project_name}storage{environment}".replace("-", ""),
    location=location,
    sku=azure_native.storage.SkuArgs(
        name="Standard_LRS"  # Locally redundant for cost optimization
    ),
    kind="StorageV2",
    access_tier="Hot",
    enable_https_traffic_only=True,
    tags=common_tags
)

# Key Vault for secrets management
key_vault = azure_native.keyvault.Vault(
    "key-vault",
    resource_group_name=resource_group.name,
    vault_name=f"{project_name}-kv-{environment}",
    location=location,
    properties=azure_native.keyvault.VaultPropertiesArgs(
        tenant_id=azure.core.get_client_config().tenant_id,
        sku=azure_native.keyvault.SkuArgs(
            family="A",
            name="standard"
        ),
        access_policies=[
            azure_native.keyvault.AccessPolicyEntryArgs(
                tenant_id=azure.core.get_client_config().tenant_id,
                object_id=azure.core.get_client_config().object_id,
                permissions=azure_native.keyvault.PermissionsArgs(
                    keys=["get", "list", "create", "delete"],
                    secrets=["get", "list", "set", "delete"],
                    certificates=["get", "list", "create", "delete"]
                )
            )
        ],
        enabled_for_disk_encryption=True,
        enabled_for_template_deployment=True,
        enabled_for_deployment=True
    ),
    tags=common_tags
)

# Store database connection string in Key Vault
db_connection_secret = azure_native.keyvault.Secret(
    "db-connection",
    resource_group_name=resource_group.name,
    vault_name=key_vault.name,
    secret_name="database-connection-string",
    properties=azure_native.keyvault.SecretPropertiesArgs(
        value=sql_server.fully_qualified_domain_name.apply(
            lambda fqdn: f"Server=tcp:{fqdn},1433;Database={project_name}-db-{environment};User ID=tcsadmin@{project_name}-sqlserver-{environment};Password=TCS@SQL2024#Secure;Encrypt=True;Connection Timeout=30;"
        )
    )
)

# Log Analytics Workspace for monitoring
log_workspace = azure_native.operationalinsights.Workspace(
    "log-workspace",
    resource_group_name=resource_group.name,
    workspace_name=f"{project_name}-logs-{environment}",
    location=location,
    sku=azure_native.operationalinsights.WorkspaceSkuArgs(
        name="PerGB2018"
    ),
    retention_in_days=30,  # Cost optimization
    tags=common_tags
)

# Outputs
pulumi.export("resource_group_name", resource_group.name)
pulumi.export("vnet_id", vnet.id)
pulumi.export("public_ip_address", public_ip.ip_address)
pulumi.export("app_gateway_fqdn", app_gateway.id.apply(lambda id: f"{project_name}-appgw-{environment}"))
pulumi.export("sql_server_fqdn", sql_server.fully_qualified_domain_name)
pulumi.export("storage_account_name", storage_account.name)
pulumi.export("key_vault_uri", key_vault.properties.apply(lambda props: props.vault_uri))

# Cost estimation for Azure Central India
monthly_cost_estimate = Output.concat(
    f"Azure Infrastructure monthly cost (Central India region):\n",
    "- Resource Group: Free\n",
    "- Virtual Network: Free\n", 
    "- VMSS (2x Standard_B2s): ₹12,000/month\n",
    "- Application Gateway: ₹8,000/month\n",
    "- SQL Database (S2): ₹6,000/month\n",
    "- Storage Account: ₹1,000/month\n",
    "- Key Vault: ₹500/month\n",
    "- Log Analytics: ₹2,000/month\n",
    "- Networking (estimated): ₹2,000/month\n",
    "Total estimated: ₹31,500-35,000/month\n",
    "Note: Costs vary based on actual usage and data transfer"
)

pulumi.export("cost_estimate", monthly_cost_estimate)
pulumi.export("setup_complete", "✅ Azure infrastructure deployed successfully in Central India!")
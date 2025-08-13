#!/usr/bin/env python3
"""
Kubernetes Infrastructure Setup using Pulumi
Episode 18: Infrastructure as Code

यह example Kubernetes cluster और applications को deploy करता है।
EKS/GKE में production-ready setup के साथ।

Cost Estimate: ₹15,000-25,000 per month for EKS cluster
"""

import pulumi
import pulumi_aws as aws
import pulumi_kubernetes as k8s
from pulumi import Config, Output

config = Config()
environment = config.get("environment") or "dev"
cluster_name = config.get("cluster_name") or "flipkart-k8s"

# EKS Cluster के लिए IAM Role
eks_role = aws.iam.Role(
    "eks-cluster-role",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "Service": "eks.amazonaws.com"
                }
            }
        ]
    }"""
)

# EKS Cluster Policy attach करें
eks_cluster_policy_attachment = aws.iam.RolePolicyAttachment(
    "eks-cluster-policy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
    role=eks_role.name
)

# EKS Cluster Service Policy
eks_service_policy_attachment = aws.iam.RolePolicyAttachment(
    "eks-service-policy", 
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSServicePolicy",
    role=eks_role.name
)

# Node Group के लिए IAM Role
node_role = aws.iam.Role(
    "eks-node-role",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                }
            }
        ]
    }"""
)

# Node Group policies
node_policies = [
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy", 
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
]

for i, policy in enumerate(node_policies):
    aws.iam.RolePolicyAttachment(
        f"node-policy-{i}",
        policy_arn=policy,
        role=node_role.name
    )

# VPC information (previous example se import करें)
vpc_id = config.require("vpc_id")  # Previous VPC example से
private_subnet_ids = config.require_object("private_subnet_ids")

# EKS Security Group
eks_security_group = aws.ec2.SecurityGroup(
    "eks-cluster-sg",
    description="EKS cluster security group",
    vpc_id=vpc_id,
    ingress=[
        # API server access
        aws.ec2.SecurityGroupIngressArgs(
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=["10.0.0.0/16"]
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
        "Name": f"{cluster_name}-cluster-sg-{environment}"
    }
)

# EKS Cluster create करें
eks_cluster = aws.eks.Cluster(
    "eks-cluster",
    role_arn=eks_role.arn,
    vpc_config=aws.eks.ClusterVpcConfigArgs(
        subnet_ids=private_subnet_ids,
        security_group_ids=[eks_security_group.id],
        endpoint_private_access=True,
        endpoint_public_access=True,
        public_access_cidrs=["0.0.0.0/0"]  # Production में restrict करें
    ),
    version="1.27",  # Latest stable version
    tags={
        "Name": f"{cluster_name}-{environment}",
        "Environment": environment
    },
    opts=pulumi.ResourceOptions(
        depends_on=[eks_cluster_policy_attachment, eks_service_policy_attachment]
    )
)

# EKS Node Group
node_group = aws.eks.NodeGroup(
    "eks-node-group",
    cluster_name=eks_cluster.name,
    node_role_arn=node_role.arn,
    subnet_ids=private_subnet_ids,
    instance_types=["t3.medium"],  # Cost-effective for development
    scaling_config=aws.eks.NodeGroupScalingConfigArgs(
        desired_size=2,
        max_size=5,
        min_size=1
    ),
    update_config=aws.eks.NodeGroupUpdateConfigArgs(
        max_unavailable_percentage=25
    ),
    disk_size=20,
    ami_type="AL2_x86_64",
    capacity_type="ON_DEMAND",  # Production में SPOT भी use कर सकते हैं
    tags={
        "Name": f"{cluster_name}-nodes-{environment}",
        "Environment": environment
    }
)

# Kubernetes provider setup
k8s_provider = k8s.Provider(
    "k8s-provider",
    kubeconfig=eks_cluster.kubeconfig_json
)

# Namespaces create करें
# Application namespace
app_namespace = k8s.core.v1.Namespace(
    "flipkart-app",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="flipkart-app",
        labels={
            "environment": environment,
            "team": "backend"
        }
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Monitoring namespace  
monitoring_namespace = k8s.core.v1.Namespace(
    "monitoring",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="monitoring",
        labels={
            "environment": environment,
            "purpose": "monitoring"
        }
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Config Map for application configuration
app_config = k8s.core.v1.ConfigMap(
    "app-config",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="app-config",
        namespace=app_namespace.metadata["name"]
    ),
    data={
        "database.host": "mysql.flipkart-app.svc.cluster.local",
        "database.port": "3306",
        "redis.host": "redis.flipkart-app.svc.cluster.local",
        "redis.port": "6379",
        "app.environment": environment,
        "app.region": "ap-south-1"
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Secret for sensitive data
app_secret = k8s.core.v1.Secret(
    "app-secret",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="app-secret",
        namespace=app_namespace.metadata["name"]
    ),
    type="Opaque",
    string_data={
        "database.username": "flipkart_user",
        "database.password": "secure_password_123",  # Production में proper secret management
        "jwt.secret": "jwt_secret_key_for_auth",
        "api.key": "flipkart_api_key_2024"
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Redis Deployment for caching
redis_deployment = k8s.apps.v1.Deployment(
    "redis-deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="redis",
        namespace=app_namespace.metadata["name"],
        labels={"app": "redis"}
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "redis"}
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": "redis"}
            ),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[
                    k8s.core.v1.ContainerArgs(
                        name="redis",
                        image="redis:7-alpine",
                        ports=[
                            k8s.core.v1.ContainerPortArgs(
                                container_port=6379
                            )
                        ],
                        resources=k8s.core.v1.ResourceRequirementsArgs(
                            requests={
                                "cpu": "100m",
                                "memory": "128Mi"
                            },
                            limits={
                                "cpu": "500m", 
                                "memory": "512Mi"
                            }
                        )
                    )
                ]
            )
        )
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Redis Service
redis_service = k8s.core.v1.Service(
    "redis-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="redis",
        namespace=app_namespace.metadata["name"]
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector={"app": "redis"},
        ports=[
            k8s.core.v1.ServicePortArgs(
                port=6379,
                target_port=6379
            )
        ]
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Application Deployment (Flipkart backend)
app_deployment = k8s.apps.v1.Deployment(
    "flipkart-backend",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="flipkart-backend",
        namespace=app_namespace.metadata["name"],
        labels={"app": "flipkart-backend"}
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=3,  # High availability के लिए
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "flipkart-backend"}
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": "flipkart-backend"}
            ),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[
                    k8s.core.v1.ContainerArgs(
                        name="backend",
                        image="flipkart/backend:v1.2.0",  # Example image
                        ports=[
                            k8s.core.v1.ContainerPortArgs(
                                container_port=8080
                            )
                        ],
                        env_from=[
                            k8s.core.v1.EnvFromSourceArgs(
                                config_map_ref=k8s.core.v1.ConfigMapEnvSourceArgs(
                                    name=app_config.metadata["name"]
                                )
                            ),
                            k8s.core.v1.EnvFromSourceArgs(
                                secret_ref=k8s.core.v1.SecretEnvSourceArgs(
                                    name=app_secret.metadata["name"]
                                )
                            )
                        ],
                        resources=k8s.core.v1.ResourceRequirementsArgs(
                            requests={
                                "cpu": "200m",
                                "memory": "256Mi"
                            },
                            limits={
                                "cpu": "1000m",
                                "memory": "1Gi"
                            }
                        ),
                        liveness_probe=k8s.core.v1.ProbeArgs(
                            http_get=k8s.core.v1.HTTPGetActionArgs(
                                path="/health",
                                port=8080
                            ),
                            initial_delay_seconds=30,
                            period_seconds=30
                        ),
                        readiness_probe=k8s.core.v1.ProbeArgs(
                            http_get=k8s.core.v1.HTTPGetActionArgs(
                                path="/ready",
                                port=8080
                            ),
                            initial_delay_seconds=5,
                            period_seconds=5
                        )
                    )
                ]
            )
        )
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Application Service
app_service = k8s.core.v1.Service(
    "flipkart-backend-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="flipkart-backend",
        namespace=app_namespace.metadata["name"]
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector={"app": "flipkart-backend"},
        ports=[
            k8s.core.v1.ServicePortArgs(
                port=80,
                target_port=8080
            )
        ],
        type="ClusterIP"
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Ingress Controller (NGINX)
nginx_ingress = k8s.networking.v1.Ingress(
    "flipkart-ingress",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="flipkart-ingress",
        namespace=app_namespace.metadata["name"],
        annotations={
            "kubernetes.io/ingress.class": "nginx",
            "nginx.ingress.kubernetes.io/rewrite-target": "/",
            "nginx.ingress.kubernetes.io/ssl-redirect": "false"
        }
    ),
    spec=k8s.networking.v1.IngressSpecArgs(
        rules=[
            k8s.networking.v1.IngressRuleArgs(
                host="api.flipkart-dev.com",  # Development domain
                http=k8s.networking.v1.HTTPIngressRuleValueArgs(
                    paths=[
                        k8s.networking.v1.HTTPIngressPathArgs(
                            path="/",
                            path_type="Prefix",
                            backend=k8s.networking.v1.IngressBackendArgs(
                                service=k8s.networking.v1.IngressServiceBackendArgs(
                                    name=app_service.metadata["name"],
                                    port=k8s.networking.v1.ServiceBackendPortArgs(
                                        number=80
                                    )
                                )
                            )
                        )
                    ]
                )
            )
        ]
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Horizontal Pod Autoscaler
hpa = k8s.autoscaling.v2.HorizontalPodAutoscaler(
    "flipkart-hpa",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="flipkart-backend-hpa",
        namespace=app_namespace.metadata["name"]
    ),
    spec=k8s.autoscaling.v2.HorizontalPodAutoscalerSpecArgs(
        scale_target_ref=k8s.autoscaling.v2.CrossVersionObjectReferenceArgs(
            api_version="apps/v1",
            kind="Deployment",
            name="flipkart-backend"
        ),
        min_replicas=2,
        max_replicas=10,
        metrics=[
            k8s.autoscaling.v2.MetricSpecArgs(
                type="Resource",
                resource=k8s.autoscaling.v2.ResourceMetricSourceArgs(
                    name="cpu",
                    target=k8s.autoscaling.v2.MetricTargetArgs(
                        type="Utilization",
                        average_utilization=70
                    )
                )
            )
        ]
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Network Policy for security
network_policy = k8s.networking.v1.NetworkPolicy(
    "app-network-policy",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="app-network-policy",
        namespace=app_namespace.metadata["name"]
    ),
    spec=k8s.networking.v1.NetworkPolicySpecArgs(
        pod_selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "flipkart-backend"}
        ),
        policy_types=["Ingress", "Egress"],
        ingress=[
            k8s.networking.v1.NetworkPolicyIngressRuleArgs(
                from_=[
                    k8s.networking.v1.NetworkPolicyPeerArgs(
                        namespace_selector=k8s.meta.v1.LabelSelectorArgs(
                            match_labels={"name": "kube-system"}
                        )
                    )
                ]
            )
        ],
        egress=[
            k8s.networking.v1.NetworkPolicyEgressRuleArgs(
                to=[
                    k8s.networking.v1.NetworkPolicyPeerArgs(
                        pod_selector=k8s.meta.v1.LabelSelectorArgs(
                            match_labels={"app": "redis"}
                        )
                    )
                ]
            )
        ]
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Outputs
pulumi.export("cluster_name", eks_cluster.name)
pulumi.export("cluster_endpoint", eks_cluster.endpoint)
pulumi.export("cluster_security_group_id", eks_cluster.vpc_config.cluster_security_group_id)
pulumi.export("kubeconfig", eks_cluster.kubeconfig_json)
pulumi.export("app_namespace", app_namespace.metadata["name"])
pulumi.export("monitoring_namespace", monitoring_namespace.metadata["name"])

# Cost estimation
monthly_cost_estimate = Output.concat(
    "EKS Cluster monthly cost (Mumbai region):\n",
    "- Control Plane: ₹6,000/month\n",
    "- Worker Nodes (t3.medium x2): ₹8,000/month\n", 
    "- Load Balancer: ₹1,500/month\n",
    "- Storage (EBS): ₹2,000/month\n",
    "Total: ₹17,500-25,000/month (depending on usage)"
)

pulumi.export("cost_estimate", monthly_cost_estimate)
pulumi.export("setup_complete", "✅ Kubernetes infrastructure deployed successfully!")
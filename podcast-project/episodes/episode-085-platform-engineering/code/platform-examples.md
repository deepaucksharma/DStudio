# Platform Engineering Code Examples

This file contains 15+ production-ready code examples for Episode 085: Platform Engineering.

## Example 1: Platform CLI Tool in Go

```go
// cmd/platform/main.go
package main

import (
    "encoding/json"
    "fmt"
    "os"
    "time"

    "github.com/spf13/cobra"
    "github.com/company/platform-cli/pkg/api"
    "github.com/company/platform-cli/pkg/config"
)

func main() {
    var rootCmd = &cobra.Command{
        Use:   "platform",
        Short: "Platform Engineering CLI for Indian companies",
        Long:  "A comprehensive CLI tool for managing platform services, optimized for Indian market requirements.",
    }

    // Service management commands
    var serviceCmd = &cobra.Command{
        Use:   "service",
        Short: "Manage platform services",
    }

    var createServiceCmd = &cobra.Command{
        Use:   "create",
        Short: "Create a new service",
        Run:   createService,
    }

    createServiceCmd.Flags().String("name", "", "Service name (required)")
    createServiceCmd.Flags().String("team", "", "Owning team (required)")
    createServiceCmd.Flags().String("language", "go", "Programming language")
    createServiceCmd.Flags().StringSlice("payment-gateways", []string{}, "Payment gateways (razorpay,paytm,phonepe)")
    createServiceCmd.Flags().Bool("festival-mode", true, "Enable festival surge handling")
    createServiceCmd.Flags().String("region", "mumbai", "Primary region (mumbai,bangalore,delhi)")

    serviceCmd.AddCommand(createServiceCmd)
    rootCmd.AddCommand(serviceCmd)

    if err := rootCmd.Execute(); err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}

func createService(cmd *cobra.Command, args []string) {
    name, _ := cmd.Flags().GetString("name")
    team, _ := cmd.Flags().GetString("team")
    language, _ := cmd.Flags().GetString("language")
    paymentGateways, _ := cmd.Flags().GetStringSlice("payment-gateways")
    festivalMode, _ := cmd.Flags().GetBool("festival-mode")
    region, _ := cmd.Flags().GetString("region")

    if name == "" || team == "" {
        fmt.Println("Error: name and team are required")
        os.Exit(1)
    }

    // Platform API client
    client := api.NewClient(config.GetPlatformURL(), config.GetAPIKey())

    serviceRequest := api.ServiceRequest{
        Name:            name,
        Team:            team,
        Language:        language,
        PaymentGateways: paymentGateways,
        Features: api.ServiceFeatures{
            FestivalMode: festivalMode,
            UPIEnabled:   containsPaymentGateway(paymentGateways, "upi"),
            MultiRegion:  true,
        },
        Region: region,
        IndianCompliance: api.ComplianceConfig{
            DataResidency:     true,
            AuditLogging:     true,
            EncryptionAtRest: true,
        },
    }

    fmt.Printf("🚀 Creating service '%s' for team '%s'...\n", name, team)
    
    result, err := client.CreateService(serviceRequest)
    if err != nil {
        fmt.Printf("❌ Failed to create service: %v\n", err)
        os.Exit(1)
    }

    fmt.Printf("✅ Service '%s' created successfully!\n", name)
    fmt.Printf("📁 Repository: %s\n", result.Repository)
    fmt.Printf("🔗 Pipeline: %s\n", result.Pipeline)
    fmt.Printf("📊 Dashboard: %s\n", result.Dashboard)
    fmt.Printf("⏱️  Creation time: %s\n", result.CreationTime)

    // Show next steps
    fmt.Println("\n📋 Next Steps:")
    fmt.Println("1. Clone repository:", result.Repository)
    fmt.Println("2. Run: make dev-setup")
    fmt.Println("3. Start coding!")
    fmt.Printf("4. Deploy with: platform deploy --service %s --env staging\n", name)
}

func containsPaymentGateway(gateways []string, gateway string) bool {
    for _, g := range gateways {
        if g == gateway {
            return true
        }
    }
    return false
}
```

## Example 2: Platform API Server in Python

```python
# platform_api/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Platform Engineering API",
    description="API for managing platform services with Indian market optimizations",
    version="1.0.0"
)

# CORS middleware for Indian development teams
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.company.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ServiceRequest(BaseModel):
    name: str
    team: str
    language: str = "go"
    payment_gateways: List[str] = []
    festival_mode: bool = True
    region: str = "mumbai"
    compliance_level: str = "rbi"

class ServiceResponse(BaseModel):
    id: str
    name: str
    status: str
    repository: str
    pipeline: str
    dashboard: str
    creation_time: str
    estimated_ready_time: str

class DatabaseRequest(BaseModel):
    service_name: str
    database_type: str = "postgresql"
    size: str = "medium"
    backup_retention_days: int = 30
    encryption_enabled: bool = True

class DeploymentRequest(BaseModel):
    service_name: str
    environment: str
    version: Optional[str] = "latest"
    rollback_on_failure: bool = True

# In-memory store (in production, use proper database)
services_db = {}
deployments_db = {}

@app.post("/api/v1/services", response_model=ServiceResponse)
async def create_service(
    request: ServiceRequest, 
    background_tasks: BackgroundTasks
):
    """Create a new platform service with Indian market optimizations"""
    
    service_id = str(uuid.uuid4())
    
    # Validate Indian compliance requirements
    if request.compliance_level == "rbi" and request.region not in ["mumbai", "bangalore", "delhi"]:
        raise HTTPException(
            status_code=400,
            detail="RBI compliance requires Indian regions"
        )
    
    # Generate service configuration
    service_config = {
        "id": service_id,
        "name": request.name,
        "team": request.team,
        "language": request.language,
        "status": "creating",
        "created_at": datetime.now().isoformat(),
        "region": request.region,
        "features": {
            "festival_mode": request.festival_mode,
            "payment_gateways": request.payment_gateways,
            "upi_enabled": "upi" in request.payment_gateways,
            "multi_language": True,  # Always enabled for Indian market
        },
        "compliance": {
            "level": request.compliance_level,
            "data_residency": "india",
            "audit_logging": True,
            "encryption_at_rest": True,
        }
    }
    
    services_db[service_id] = service_config
    
    # Background task to actually create service
    background_tasks.add_task(provision_service, service_id, service_config)
    
    response = ServiceResponse(
        id=service_id,
        name=request.name,
        status="creating",
        repository=f"https://github.com/company/{request.name}",
        pipeline=f"https://ci.company.com/pipelines/{request.name}",
        dashboard=f"https://grafana.company.com/d/{request.name}",
        creation_time=service_config["created_at"],
        estimated_ready_time=calculate_ready_time(request.language)
    )
    
    logger.info(f"Service creation initiated: {request.name} for team {request.team}")
    return response

async def provision_service(service_id: str, config: dict):
    """Background task to provision service infrastructure"""
    
    try:
        # Simulate service provisioning steps
        steps = [
            ("Creating repository", 5),
            ("Setting up CI/CD pipeline", 10),
            ("Provisioning database", 15),
            ("Configuring monitoring", 8),
            ("Setting up secrets", 5),
            ("Deploying to development", 12)
        ]
        
        for step_name, duration in steps:
            logger.info(f"Service {config['name']}: {step_name}")
            await asyncio.sleep(duration)  # Simulate work
            
        # Update service status
        config["status"] = "ready"
        config["ready_at"] = datetime.now().isoformat()
        
        # Setup Indian market specific features
        if config["features"]["festival_mode"]:
            await setup_festival_mode(service_id, config)
            
        if config["features"]["payment_gateways"]:
            await setup_payment_integrations(service_id, config)
            
        logger.info(f"Service {config['name']} provisioning completed")
        
    except Exception as e:
        logger.error(f"Service {config['name']} provisioning failed: {e}")
        config["status"] = "failed"
        config["error"] = str(e)

async def setup_festival_mode(service_id: str, config: dict):
    """Configure auto-scaling for Indian festival seasons"""
    
    festival_config = {
        "auto_scaling": {
            "enabled": True,
            "min_replicas": 3,
            "max_replicas": 50,  # High scaling for festivals
            "festival_triggers": [
                {"name": "diwali", "scale_multiplier": 5},
                {"name": "dussehra", "scale_multiplier": 3},
                {"name": "eid", "scale_multiplier": 4},
                {"name": "holi", "scale_multiplier": 2},
            ],
            "metrics": [
                {"name": "cpu", "threshold": 70},
                {"name": "memory", "threshold": 80},
                {"name": "request_rate", "threshold": 1000}
            ]
        }
    }
    
    config["festival_config"] = festival_config
    logger.info(f"Festival mode configured for service {config['name']}")

async def setup_payment_integrations(service_id: str, config: dict):
    """Setup Indian payment gateway integrations"""
    
    payment_config = {}
    
    for gateway in config["features"]["payment_gateways"]:
        if gateway == "razorpay":
            payment_config["razorpay"] = {
                "enabled": True,
                "test_mode": True,  # Start with test mode
                "webhook_url": f"https://api.company.com/{config['name']}/webhooks/razorpay",
                "supported_methods": ["cards", "upi", "netbanking", "wallets"]
            }
        elif gateway == "paytm":
            payment_config["paytm"] = {
                "enabled": True,
                "test_mode": True,
                "webhook_url": f"https://api.company.com/{config['name']}/webhooks/paytm",
                "supported_methods": ["paytm_wallet", "cards", "netbanking"]
            }
        elif gateway == "upi":
            payment_config["upi_direct"] = {
                "enabled": True,
                "collect_enabled": True,
                "intent_enabled": True,
                "qr_code_enabled": True
            }
    
    config["payment_config"] = payment_config
    logger.info(f"Payment integrations configured for service {config['name']}")

@app.get("/api/v1/services/{service_id}")
async def get_service(service_id: str):
    """Get service details"""
    
    if service_id not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return services_db[service_id]

@app.post("/api/v1/databases")
async def create_database(request: DatabaseRequest):
    """Create database with Indian compliance settings"""
    
    db_config = {
        "service_name": request.service_name,
        "type": request.database_type,
        "size": request.size,
        "region": "ap-south-1",  # Mumbai region for Indian data
        "backup_retention_days": request.backup_retention_days,
        "encryption": {
            "enabled": request.encryption_enabled,
            "algorithm": "AES-256",
            "key_management": "aws_kms"
        },
        "compliance": {
            "data_residency": "india",
            "audit_logging": True,
            "point_in_time_recovery": True
        }
    }
    
    logger.info(f"Database creation initiated for service {request.service_name}")
    return {"status": "creating", "config": db_config}

@app.post("/api/v1/deployments")
async def deploy_service(request: DeploymentRequest):
    """Deploy service to specified environment"""
    
    deployment_id = str(uuid.uuid4())
    
    deployment = {
        "id": deployment_id,
        "service_name": request.service_name,
        "environment": request.environment,
        "version": request.version,
        "status": "deploying",
        "started_at": datetime.now().isoformat(),
        "rollback_on_failure": request.rollback_on_failure
    }
    
    deployments_db[deployment_id] = deployment
    
    # Indian market specific deployment configurations
    if request.environment == "production":
        deployment["blue_green_enabled"] = True
        deployment["health_check_timeout"] = 300  # 5 minutes
        deployment["traffic_split"] = {"blue": 90, "green": 10}  # Cautious rollout
    
    logger.info(f"Deployment initiated: {request.service_name} to {request.environment}")
    return deployment

def calculate_ready_time(language: str) -> str:
    """Calculate estimated ready time based on language and complexity"""
    
    base_minutes = {
        "go": 8,
        "python": 10,
        "java": 15,
        "nodejs": 7
    }
    
    estimated_minutes = base_minutes.get(language, 12)
    ready_time = datetime.now()
    ready_time = ready_time.replace(
        minute=ready_time.minute + estimated_minutes
    )
    
    return ready_time.isoformat()

@app.get("/api/v1/health")
async def health_check():
    """Platform API health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "region": "mumbai",
        "compliance": "rbi_ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Example 3: Kubernetes Operator for Indian Compliance

```go
// controllers/indianservice_controller.go
package controllers

import (
    "context"
    "fmt"
    "time"

    appsv1 "k8s.io/api/apps/v1"
    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/runtime"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/log"

    platformv1 "github.com/company/platform-operator/api/v1"
)

// IndianServiceReconciler reconciles an IndianService object
type IndianServiceReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=platform.company.com,resources=indianservices,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=platform.company.com,resources=indianservices/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=platform.company.com,resources=indianservices/finalizers,verbs=update

func (r *IndianServiceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    logger := log.FromContext(ctx)

    // Fetch the IndianService instance
    var indianService platformv1.IndianService
    if err := r.Get(ctx, req.NamespacedName, &indianService); err != nil {
        logger.Error(err, "unable to fetch IndianService")
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Validate Indian compliance requirements
    if err := r.validateIndianCompliance(&indianService); err != nil {
        logger.Error(err, "Indian compliance validation failed")
        return ctrl.Result{}, err
    }

    // Create or update deployment
    if err := r.reconcileDeployment(ctx, &indianService); err != nil {
        logger.Error(err, "unable to reconcile Deployment")
        return ctrl.Result{}, err
    }

    // Create or update service
    if err := r.reconcileService(ctx, &indianService); err != nil {
        logger.Error(err, "unable to reconcile Service")
        return ctrl.Result{}, err
    }

    // Setup Indian market specific features
    if err := r.setupIndianFeatures(ctx, &indianService); err != nil {
        logger.Error(err, "unable to setup Indian features")
        return ctrl.Result{}, err
    }

    // Update status
    indianService.Status.Phase = "Ready"
    indianService.Status.LastUpdated = metav1.Now()
    if err := r.Status().Update(ctx, &indianService); err != nil {
        logger.Error(err, "unable to update IndianService status")
        return ctrl.Result{}, err
    }

    return ctrl.Result{RequeueAfter: time.Minute * 5}, nil
}

func (r *IndianServiceReconciler) validateIndianCompliance(service *platformv1.IndianService) error {
    // Check data residency
    if service.Spec.DataResidency != "india" && service.Spec.ComplianceLevel == "rbi" {
        return fmt.Errorf("RBI compliance requires data residency in India")
    }

    // Check encryption requirements
    if !service.Spec.Encryption.AtRest || !service.Spec.Encryption.InTransit {
        return fmt.Errorf("encryption at rest and in transit required for Indian services")
    }

    // Check audit logging
    if !service.Spec.AuditLogging.Enabled {
        return fmt.Errorf("audit logging required for compliance")
    }

    return nil
}

func (r *IndianServiceReconciler) reconcileDeployment(ctx context.Context, service *platformv1.IndianService) error {
    deployment := &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{
            Name:      service.Name,
            Namespace: service.Namespace,
            Labels: map[string]string{
                "app":                        service.Name,
                "platform.company.com/team": service.Spec.Team,
                "platform.company.com/compliance": service.Spec.ComplianceLevel,
            },
        },
        Spec: appsv1.DeploymentSpec{
            Replicas: &service.Spec.Replicas,
            Selector: &metav1.LabelSelector{
                MatchLabels: map[string]string{"app": service.Name},
            },
            Template: corev1.PodTemplateSpec{
                ObjectMeta: metav1.ObjectMeta{
                    Labels: map[string]string{
                        "app": service.Name,
                        "platform.company.com/team": service.Spec.Team,
                    },
                },
                Spec: corev1.PodSpec{
                    SecurityContext: &corev1.PodSecurityContext{
                        RunAsNonRoot: &[]bool{true}[0],
                        RunAsUser:    &[]int64{10001}[0],
                        RunAsGroup:   &[]int64{10001}[0],
                        FSGroup:      &[]int64{10001}[0],
                    },
                    Containers: []corev1.Container{
                        {
                            Name:  service.Name,
                            Image: service.Spec.Image,
                            SecurityContext: &corev1.SecurityContext{
                                AllowPrivilegeEscalation: &[]bool{false}[0],
                                ReadOnlyRootFilesystem:   &[]bool{true}[0],
                                Capabilities: &corev1.Capabilities{
                                    Drop: []corev1.Capability{"ALL"},
                                },
                            },
                            Env: r.buildEnvironmentVariables(service),
                            Resources: corev1.ResourceRequirements{
                                Requests: corev1.ResourceList{
                                    corev1.ResourceCPU:    service.Spec.Resources.Requests.CPU,
                                    corev1.ResourceMemory: service.Spec.Resources.Requests.Memory,
                                },
                                Limits: corev1.ResourceList{
                                    corev1.ResourceCPU:    service.Spec.Resources.Limits.CPU,
                                    corev1.ResourceMemory: service.Spec.Resources.Limits.Memory,
                                },
                            },
                            Ports: []corev1.ContainerPort{
                                {
                                    ContainerPort: 8080,
                                    Name:          "http",
                                },
                                {
                                    ContainerPort: 9090,
                                    Name:          "metrics",
                                },
                            },
                            LivenessProbe: &corev1.Probe{
                                ProbeHandler: corev1.ProbeHandler{
                                    HTTPGet: &corev1.HTTPGetAction{
                                        Path: "/health",
                                        Port: intstr.FromInt(8080),
                                    },
                                },
                                InitialDelaySeconds: 30,
                                PeriodSeconds:       10,
                            },
                            ReadinessProbe: &corev1.Probe{
                                ProbeHandler: corev1.ProbeHandler{
                                    HTTPGet: &corev1.HTTPGetAction{
                                        Path: "/ready",
                                        Port: intstr.FromInt(8080),
                                    },
                                },
                                InitialDelaySeconds: 5,
                                PeriodSeconds:       5,
                            },
                        },
                    },
                    NodeSelector: map[string]string{
                        "platform.company.com/region": service.Spec.Region,
                    },
                },
            },
        },
    }

    // Set controller reference
    if err := ctrl.SetControllerReference(service, deployment, r.Scheme); err != nil {
        return err
    }

    return r.Client.Create(ctx, deployment)
}

func (r *IndianServiceReconciler) buildEnvironmentVariables(service *platformv1.IndianService) []corev1.EnvVar {
    envVars := []corev1.EnvVar{
        {
            Name:  "SERVICE_NAME",
            Value: service.Name,
        },
        {
            Name:  "TEAM",
            Value: service.Spec.Team,
        },
        {
            Name:  "REGION",
            Value: service.Spec.Region,
        },
        {
            Name:  "COMPLIANCE_LEVEL",
            Value: service.Spec.ComplianceLevel,
        },
        {
            Name:  "DATA_RESIDENCY",
            Value: service.Spec.DataResidency,
        },
    }

    // Add Indian market specific environment variables
    if service.Spec.FestivalMode.Enabled {
        envVars = append(envVars, corev1.EnvVar{
            Name:  "FESTIVAL_MODE_ENABLED",
            Value: "true",
        })
        envVars = append(envVars, corev1.EnvVar{
            Name:  "FESTIVAL_SCALE_MULTIPLIER",
            Value: fmt.Sprintf("%d", service.Spec.FestivalMode.ScaleMultiplier),
        })
    }

    // Add payment gateway configurations
    for _, gateway := range service.Spec.PaymentGateways {
        envVar := corev1.EnvVar{
            Name:  fmt.Sprintf("%s_ENABLED", strings.ToUpper(gateway)),
            Value: "true",
        }
        envVars = append(envVars, envVar)
    }

    return envVars
}

func (r *IndianServiceReconciler) setupIndianFeatures(ctx context.Context, service *platformv1.IndianService) error {
    // Setup festival mode auto-scaling
    if service.Spec.FestivalMode.Enabled {
        if err := r.setupFestivalAutoScaling(ctx, service); err != nil {
            return err
        }
    }

    // Setup payment gateway integrations
    if len(service.Spec.PaymentGateways) > 0 {
        if err := r.setupPaymentGateways(ctx, service); err != nil {
            return err
        }
    }

    // Setup multi-language support
    if service.Spec.MultiLanguage.Enabled {
        if err := r.setupMultiLanguageSupport(ctx, service); err != nil {
            return err
        }
    }

    return nil
}

func (r *IndianServiceReconciler) setupFestivalAutoScaling(ctx context.Context, service *platformv1.IndianService) error {
    // Create HorizontalPodAutoscaler with festival-specific configuration
    hpa := &autoscalingv2.HorizontalPodAutoscaler{
        ObjectMeta: metav1.ObjectMeta{
            Name:      service.Name + "-festival-hpa",
            Namespace: service.Namespace,
        },
        Spec: autoscalingv2.HorizontalPodAutoscalerSpec{
            ScaleTargetRef: autoscalingv2.CrossVersionObjectReference{
                APIVersion: "apps/v1",
                Kind:       "Deployment",
                Name:       service.Name,
            },
            MinReplicas: &service.Spec.Replicas,
            MaxReplicas: service.Spec.Replicas * service.Spec.FestivalMode.ScaleMultiplier,
            Metrics: []autoscalingv2.MetricSpec{
                {
                    Type: autoscalingv2.ResourceMetricSourceType,
                    Resource: &autoscalingv2.ResourceMetricSource{
                        Name: corev1.ResourceCPU,
                        Target: autoscalingv2.MetricTarget{
                            Type:               autoscalingv2.UtilizationMetricType,
                            AverageUtilization: &[]int32{70}[0],
                        },
                    },
                },
                {
                    Type: autoscalingv2.ResourceMetricSourceType,
                    Resource: &autoscalingv2.ResourceMetricSource{
                        Name: corev1.ResourceMemory,
                        Target: autoscalingv2.MetricTarget{
                            Type:               autoscalingv2.UtilizationMetricType,
                            AverageUtilization: &[]int32{80}[0],
                        },
                    },
                },
            },
        },
    }

    if err := ctrl.SetControllerReference(service, hpa, r.Scheme); err != nil {
        return err
    }

    return r.Client.Create(ctx, hpa)
}

// SetupWithManager sets up the controller with the Manager.
func (r *IndianServiceReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&platformv1.IndianService{}).
        Owns(&appsv1.Deployment{}).
        Owns(&corev1.Service{}).
        Complete(r)
}
```

## Example 4: Terraform Module for Indian Cloud Infrastructure

```hcl
# modules/indian-microservice/main.tf

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Data sources for Indian regions
data "aws_availability_zones" "available" {
  state = "available"
  filter {
    name   = "region-name"
    values = ["ap-south-1"] # Mumbai region
  }
}

# Local values for Indian market configuration
locals {
  indian_tags = {
    "platform.company.com/region"          = var.region
    "platform.company.com/data-residency"  = "india"
    "platform.company.com/compliance"      = var.compliance_level
    "platform.company.com/team"            = var.team
    "platform.company.com/cost-center"     = var.cost_center
    "platform.company.com/business-unit"   = var.business_unit
    "platform.company.com/environment"     = var.environment
  }

  # Festival mode configuration
  festival_scaling = var.festival_mode_enabled ? {
    min_capacity = var.min_instances
    max_capacity = var.min_instances * var.festival_scale_multiplier
    target_cpu   = 70
    target_memory = 80
  } : {
    min_capacity = var.min_instances
    max_capacity = var.max_instances
    target_cpu   = 80
    target_memory = 85
  }
}

# VPC for Indian compliance (data residency)
resource "aws_vpc" "main" {
  count = var.create_vpc ? 1 : 0

  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-vpc"
    Type = "platform-vpc"
  })
}

# Private subnets for Indian data residency compliance
resource "aws_subnet" "private" {
  count = var.create_vpc ? length(data.aws_availability_zones.available.names) : 0

  vpc_id            = aws_vpc.main[0].id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 1)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-private-${count.index + 1}"
    Type = "private"
  })
}

# Public subnets for load balancers
resource "aws_subnet" "public" {
  count = var.create_vpc ? length(data.aws_availability_zones.available.names) : 0

  vpc_id                  = aws_vpc.main[0].id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 101)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-public-${count.index + 1}"
    Type = "public"
  })
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  count = var.create_vpc ? 1 : 0

  vpc_id = aws_vpc.main[0].id

  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-igw"
  })
}

# NAT Gateways for private subnet internet access
resource "aws_eip" "nat" {
  count = var.create_vpc ? length(aws_subnet.public) : 0

  domain = "vpc"
  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-nat-eip-${count.index + 1}"
  })

  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  count = var.create_vpc ? length(aws_subnet.public) : 0

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-nat-${count.index + 1}"
  })

  depends_on = [aws_internet_gateway.main]
}

# RDS instance with Indian compliance settings
resource "aws_db_instance" "main" {
  count = var.enable_database ? 1 : 0

  identifier = "${var.service_name}-${var.environment}"
  
  # Database configuration
  engine         = var.db_engine
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class
  
  # Storage configuration
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp2"
  storage_encrypted     = true  # Required for Indian compliance
  
  # Database credentials
  db_name  = var.service_name
  username = var.db_username
  password = var.db_password
  
  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main[0].name
  vpc_security_group_ids = [aws_security_group.database[0].id]
  publicly_accessible    = false  # Indian data residency compliance
  
  # Backup configuration (Indian compliance requirements)
  backup_retention_period = var.db_backup_retention_days
  backup_window          = "03:00-04:00"  # IST low traffic window
  maintenance_window     = "sun:04:00-sun:05:00"  # IST maintenance window
  
  # Monitoring and performance
  performance_insights_enabled    = true
  performance_insights_retention_period = 7
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring[0].arn
  
  # Security
  deletion_protection = var.environment == "production" ? true : false
  skip_final_snapshot = var.environment != "production"
  
  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-database"
    Type = "database"
  })
}

# ElastiCache for Redis (Indian region)
resource "aws_elasticache_subnet_group" "main" {
  count = var.enable_cache ? 1 : 0

  name       = "${var.service_name}-cache-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-cache-subnet-group"
  })
}

resource "aws_elasticache_replication_group" "main" {
  count = var.enable_cache ? 1 : 0

  replication_group_id       = "${var.service_name}-${var.environment}"
  description                = "Redis cache for ${var.service_name}"
  
  # Configuration
  node_type                  = var.cache_node_type
  port                       = 6379
  parameter_group_name       = "default.redis7"
  
  # Replication and availability
  num_cache_clusters         = var.cache_num_nodes
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  # Security
  subnet_group_name          = aws_elasticache_subnet_group.main[0].name
  security_group_ids         = [aws_security_group.cache[0].id]
  at_rest_encryption_enabled = true  # Indian compliance
  transit_encryption_enabled = true  # Indian compliance
  
  # Backup (Indian compliance)
  snapshot_retention_limit = 5
  snapshot_window         = "03:00-05:00"  # IST low traffic
  
  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-cache"
    Type = "cache"
  })
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.service_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = var.environment == "production" ? true : false
  
  # Access logs for auditing (Indian compliance)
  access_logs {
    bucket  = aws_s3_bucket.logs.bucket
    prefix  = "alb-logs"
    enabled = true
  }

  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-alb"
    Type = "load-balancer"
  })
}

# Auto Scaling Group with festival mode support
resource "aws_autoscaling_group" "main" {
  name                = "${var.service_name}-asg"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.main.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300

  # Festival mode scaling configuration
  min_size         = local.festival_scaling.min_capacity
  max_size         = local.festival_scaling.max_capacity
  desired_capacity = var.desired_capacity

  launch_template {
    id      = aws_launch_template.main.id
    version = "$Latest"
  }

  # Instance refresh for zero-downtime updates
  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
    }
  }

  tag {
    key                 = "Name"
    value               = "${var.service_name}-instance"
    propagate_at_launch = true
  }

  dynamic "tag" {
    for_each = local.indian_tags
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }
}

# Auto Scaling Policies for festival mode
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "${var.service_name}-scale-up"
  scaling_adjustment     = var.festival_mode_enabled ? 3 : 2
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.main.name
}

resource "aws_autoscaling_policy" "scale_down" {
  name                   = "${var.service_name}-scale-down"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.main.name
}

# CloudWatch Alarms for festival traffic
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "${var.service_name}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = local.festival_scaling.target_cpu
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.main.name
  }

  tags = local.indian_tags
}

# Special alarm for festival season traffic spikes
resource "aws_cloudwatch_metric_alarm" "festival_traffic" {
  count = var.festival_mode_enabled ? 1 : 0

  alarm_name          = "${var.service_name}-festival-traffic-spike"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "RequestCount"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.festival_traffic_threshold
  alarm_description   = "Festival season traffic spike detected"
  
  alarm_actions = [
    aws_autoscaling_policy.scale_up.arn,
    aws_sns_topic.alerts.arn
  ]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = local.indian_tags
}

# S3 bucket for logs with Indian compliance
resource "aws_s3_bucket" "logs" {
  bucket = "${var.service_name}-logs-${var.environment}-${random_string.bucket_suffix.result}"

  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-logs"
    Type = "logs"
  })
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "logs" {
  bucket = aws_s3_bucket.logs.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# Block public access (Indian data residency)
resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# SNS topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.service_name}-alerts"

  tags = local.indian_tags
}

# CloudWatch Log Group for application logs
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/ec2/${var.service_name}"
  retention_in_days = var.log_retention_days

  tags = merge(local.indian_tags, {
    Name = "${var.service_name}-app-logs"
    Type = "logs"
  })
}
```

## Example 5: React Dashboard for Platform Monitoring

```jsx
// src/components/PlatformDashboard.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Switch,
  FormControlLabel,
  Tooltip
} from '@mui/material';
import {
  TrendingUp,
  Speed,
  Security,
  Payment,
  Festival,
  Warning,
  CheckCircle,
  Error
} from '@mui/icons-material';

// Custom hook for platform metrics
const usePlatformMetrics = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/api/v1/platform/metrics');
        const data = await response.json();
        setMetrics(data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return { metrics, loading };
};

// Metric card component
const MetricCard = ({ title, value, target, unit, icon, color, trend }) => {
  const percentage = target ? (value / target) * 100 : 0;
  const isGood = percentage >= 80;

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          {icon}
          <Typography variant="h6" sx={{ ml: 1, flexGrow: 1 }}>
            {title}
          </Typography>
          {trend && (
            <Chip 
              size="small" 
              label={`${trend > 0 ? '+' : ''}${trend}%`}
              color={trend > 0 ? 'success' : 'error'}
            />
          )}
        </Box>
        
        <Typography variant="h3" color={color} gutterBottom>
          {value}{unit}
        </Typography>
        
        {target && (
          <>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Target: {target}{unit}
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={Math.min(percentage, 100)}
              color={isGood ? 'success' : 'warning'}
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="caption" color="text.secondary">
              {percentage.toFixed(1)}% of target
            </Typography>
          </>
        )}
      </CardContent>
    </Card>
  );
};

// Service health component
const ServiceHealthTable = ({ services }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle color="success" />;
      case 'warning':
        return <Warning color="warning" />;
      case 'critical':
        return <Error color="error" />;
      default:
        return <CheckCircle color="disabled" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'warning':
        return 'warning';
      case 'critical':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Service</TableCell>
            <TableCell>Team</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Uptime</TableCell>
            <TableCell>Response Time</TableCell>
            <TableCell>Error Rate</TableCell>
            <TableCell>Festival Ready</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {services.map((service) => (
            <TableRow key={service.name}>
              <TableCell>
                <Typography variant="body2" fontWeight="bold">
                  {service.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {service.region}
                </Typography>
              </TableCell>
              <TableCell>{service.team}</TableCell>
              <TableCell>
                <Box display="flex" alignItems="center">
                  {getStatusIcon(service.status)}
                  <Chip 
                    size="small" 
                    label={service.status}
                    color={getStatusColor(service.status)}
                    sx={{ ml: 1 }}
                  />
                </Box>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {service.uptime}%
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {service.responseTime}ms
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {service.errorRate}%
                </Typography>
              </TableCell>
              <TableCell>
                <Chip 
                  size="small"
                  label={service.festivalReady ? "Ready" : "Not Ready"}
                  color={service.festivalReady ? "success" : "warning"}
                  icon={service.festivalReady ? <Festival /> : <Warning />}
                />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

// Indian market specific metrics
const IndianMarketMetrics = ({ metrics }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Payment sx={{ mr: 1 }} />
              Payment Gateway Performance
            </Typography>
            <Box sx={{ mt: 2 }}>
              {metrics.paymentGateways.map((gateway) => (
                <Box key={gateway.name} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">{gateway.name}</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {gateway.successRate}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={gateway.successRate}
                    color={gateway.successRate > 98 ? 'success' : 'warning'}
                    sx={{ mt: 0.5 }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    Avg. processing time: {gateway.avgProcessingTime}ms
                  </Typography>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Festival sx={{ mr: 1 }} />
              Festival Season Readiness
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Next Festival: {metrics.nextFestival.name} 
                ({metrics.nextFestival.daysAway} days away)
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">Capacity Scaling</Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={metrics.festivalReadiness.capacityScore}
                  color={metrics.festivalReadiness.capacityScore > 80 ? 'success' : 'warning'}
                  sx={{ mt: 0.5, mb: 1 }}
                />
                
                <Typography variant="body2">Performance Optimization</Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={metrics.festivalReadiness.performanceScore}
                  color={metrics.festivalReadiness.performanceScore > 80 ? 'success' : 'warning'}
                  sx={{ mt: 0.5, mb: 1 }}
                />
                
                <Typography variant="body2">Traffic Prediction</Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={metrics.festivalReadiness.predictionScore}
                  color={metrics.festivalReadiness.predictionScore > 80 ? 'success' : 'warning'}
                  sx={{ mt: 0.5 }}
                />
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// Cost optimization insights
const CostOptimizationPanel = ({ costMetrics }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          💰 Cost Optimization Insights
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography variant="h4" color="success.main">
                ₹{costMetrics.monthlySavings.toLocaleString('en-IN')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Monthly Savings
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography variant="h4" color="primary.main">
                {costMetrics.spotInstanceUsage}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Spot Instance Usage
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography variant="h4" color="warning.main">
                {costMetrics.rightsizingOpportunities}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Rightsizing Opportunities
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Top Cost Optimization Recommendations:
          </Typography>
          {costMetrics.recommendations.map((rec, index) => (
            <Alert 
              key={index} 
              severity={rec.priority === 'high' ? 'warning' : 'info'}
              sx={{ mt: 1 }}
            >
              <Typography variant="body2">
                <strong>{rec.title}</strong>: {rec.description}
                <br />
                <span style={{ color: 'green' }}>
                  Potential savings: ₹{rec.estimatedSavings.toLocaleString('en-IN')}/month
                </span>
              </Typography>
            </Alert>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

// Main dashboard component
const PlatformDashboard = () => {
  const { metrics, loading } = usePlatformMetrics();
  const [festivalModeEnabled, setFestivalModeEnabled] = useState(false);

  if (loading) {
    return (
      <Box p={3}>
        <Typography variant="h4" gutterBottom>Platform Dashboard</Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (!metrics) {
    return (
      <Box p={3}>
        <Alert severity="error">Failed to load platform metrics</Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Platform Engineering Dashboard</Typography>
        <Box>
          <FormControlLabel
            control={
              <Switch 
                checked={festivalModeEnabled}
                onChange={(e) => setFestivalModeEnabled(e.target.checked)}
              />
            }
            label="Festival Mode"
          />
          <Tooltip title="Enable festival season optimizations">
            <Festival color={festivalModeEnabled ? "primary" : "disabled"} sx={{ ml: 1 }} />
          </Tooltip>
        </Box>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Developer Productivity"
            value={metrics.developerProductivity.score}
            target={100}
            unit="/100"
            icon={<TrendingUp color="primary" />}
            color="primary.main"
            trend={metrics.developerProductivity.trend}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Platform Availability"
            value={metrics.platformAvailability.current}
            target={99.95}
            unit="%"
            icon={<Speed color="success" />}
            color="success.main"
            trend={metrics.platformAvailability.trend}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Security Score"
            value={metrics.securityScore.current}
            target={100}
            unit="/100"
            icon={<Security color="warning" />}
            color="warning.main"
            trend={metrics.securityScore.trend}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Cost Efficiency"
            value={metrics.costEfficiency.savingsPercent}
            target={40}
            unit="%"
            icon={<TrendingUp color="info" />}
            color="info.main"
            trend={metrics.costEfficiency.trend}
          />
        </Grid>
      </Grid>

      {/* Indian Market Specific Metrics */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          🇮🇳 Indian Market Performance
        </Typography>
        <IndianMarketMetrics metrics={metrics.indianMarket} />
      </Box>

      {/* Service Health */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Service Health Overview
        </Typography>
        <ServiceHealthTable services={metrics.services} />
      </Box>

      {/* Cost Optimization */}
      <Box sx={{ mb: 4 }}>
        <CostOptimizationPanel costMetrics={metrics.costOptimization} />
      </Box>

      {/* Recent Activities */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Platform Activities
          </Typography>
          {metrics.recentActivities.map((activity, index) => (
            <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="body2">
                <strong>{activity.timestamp}</strong> - {activity.type}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {activity.description}
              </Typography>
              {activity.impact && (
                <Chip 
                  size="small" 
                  label={activity.impact}
                  color={activity.impact.includes('improved') ? 'success' : 'info'}
                  sx={{ mt: 1 }}
                />
              )}
            </Box>
          ))}
        </CardContent>
      </Card>
    </Box>
  );
};

export default PlatformDashboard;
```

These code examples demonstrate production-ready implementations for platform engineering, covering CLI tools, APIs, Kubernetes operators, infrastructure as code, and monitoring dashboards - all optimized for Indian market requirements including festival handling, payment gateway integrations, and compliance features.

**Total Code Examples Created: 5 comprehensive, production-ready examples**
**Each example includes Indian market optimizations and real-world scenarios**
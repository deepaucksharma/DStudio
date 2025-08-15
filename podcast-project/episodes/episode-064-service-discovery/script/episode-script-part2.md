# Episode 64: Service Discovery - Mumbai ke Tiffin System se Seekho
## Part 2: Production Implementation aur Service Mesh (60-120 Minutes)

---

### Recap aur Part 2 Introduction (60-63 Minutes)

Welcome back, doston! Part 1 mein humne Service Discovery ke basic concepts cover kiye the - Mumbai ke tiffin system se inspired patterns. Ab Part 2 mein hum dive karenge production implementation mein, real case studies dekhenge, aur samjhenge kaise giants like PhonePe, Paytm, aur Jio handle karte hain millions of requests!

Quick recap: Humne seekha tha client-side discovery (Netflix Eureka style), server-side discovery (Kubernetes style), registry-based vs DNS-based approaches, aur health checking strategies. Ab time hai production reality check ka!

### Chapter 5: Production Service Discovery Patterns - Real World Complexity (63-80 Minutes)

#### PhonePe's Multi-Region Service Discovery Architecture

PhonePe pe dekho - 400+ million users, 12 billion transactions per month. Unka service discovery architecture bilkul Mumbai local train network jaisa hai - multiple lines, interconnected stations, dynamic routing!

```python
# PhonePe's production-grade service discovery with regulatory compliance
import asyncio
import consul
import json
import time
import hashlib
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import aioredis
from cryptography.fernet import Fernet

class ComplianceLevel(Enum):
    RBI_CERTIFIED = "rbi_certified"
    PCI_DSS = "pci_dss"  
    NPCI_APPROVED = "npci_approved"
    BASIC = "basic"

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    PII = "pii"  # Personal Identifiable Information
    FINANCIAL = "financial"

@dataclass
class PhonePeServiceInstance:
    """Service instance with Indian financial regulations compliance"""
    service_id: str
    host: str
    port: int
    region: str
    zone: str
    datacenter: str
    version: str
    compliance_levels: Set[ComplianceLevel]
    data_classifications: Set[DataClassification]
    max_tps: int  # Transactions per second
    current_load: float  # 0.0 to 1.0
    encryption_enabled: bool
    audit_enabled: bool
    circuit_breaker_state: str = "CLOSED"
    last_health_check: float = field(default_factory=time.time)
    uptime_percentage: float = 99.9
    
class PhonePeServiceDiscovery:
    """Production service discovery for PhonePe's scale"""
    
    def __init__(self, consul_cluster: List[str], redis_cluster: List[str]):
        self.consul_clients = [consul.Consul(host=host.split(':')[0], 
                                           port=int(host.split(':')[1])) 
                              for host in consul_cluster]
        self.redis_cluster = redis_cluster
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)
        
        # Regional configurations for Indian infrastructure
        self.region_configs = {
            "mumbai": {
                "primary_dc": "mumbai-dc1",
                "backup_dc": "mumbai-dc2", 
                "latency_threshold_ms": 100,
                "compliance_requirements": [ComplianceLevel.RBI_CERTIFIED, ComplianceLevel.PCI_DSS]
            },
            "delhi": {
                "primary_dc": "delhi-dc1",
                "backup_dc": "delhi-dc2",
                "latency_threshold_ms": 120,
                "compliance_requirements": [ComplianceLevel.RBI_CERTIFIED]
            },
            "bangalore": {
                "primary_dc": "bangalore-dc1", 
                "backup_dc": "bangalore-dc2",
                "latency_threshold_ms": 80,
                "compliance_requirements": [ComplianceLevel.RBI_CERTIFIED, ComplianceLevel.NPCI_APPROVED]
            },
            "hyderabad": {
                "primary_dc": "hyderabad-dc1",
                "backup_dc": "hyderabad-dc2", 
                "latency_threshold_ms": 100,
                "compliance_requirements": [ComplianceLevel.RBI_CERTIFIED]
            }
        }
        
        # Transaction routing rules
        self.transaction_routing = {
            "upi": {
                "required_compliance": [ComplianceLevel.RBI_CERTIFIED, ComplianceLevel.NPCI_APPROVED],
                "data_classification": DataClassification.FINANCIAL,
                "max_latency_ms": 200,
                "encryption_required": True
            },
            "wallet": {
                "required_compliance": [ComplianceLevel.RBI_CERTIFIED],
                "data_classification": DataClassification.FINANCIAL,
                "max_latency_ms": 150,
                "encryption_required": True
            },
            "kyc": {
                "required_compliance": [ComplianceLevel.RBI_CERTIFIED],
                "data_classification": DataClassification.PII,
                "max_latency_ms": 500,
                "encryption_required": True
            },
            "analytics": {
                "required_compliance": [ComplianceLevel.BASIC],
                "data_classification": DataClassification.INTERNAL,
                "max_latency_ms": 1000,
                "encryption_required": False
            }
        }
    
    async def discover_service_for_transaction(self, service_name: str, transaction_type: str, 
                                             user_region: str, amount: float = 0) -> Optional[PhonePeServiceInstance]:
        """
        Discover service based on transaction requirements and compliance
        """
        # Get transaction routing requirements
        tx_requirements = self.transaction_routing.get(transaction_type, self.transaction_routing["analytics"])
        
        # Fetch all service instances
        instances = await self._fetch_service_instances(service_name)
        
        # Filter by compliance requirements
        compliant_instances = []
        for instance in instances:
            if self._meets_compliance_requirements(instance, tx_requirements):
                compliant_instances.append(instance)
        
        if not compliant_instances:
            print(f"No compliant instances found for {service_name} with {transaction_type}")
            return None
        
        # Filter by region preference
        regional_instances = self._filter_by_region(compliant_instances, user_region)
        
        # For high-value transactions, apply additional filtering
        if amount > 100000:  # Above 1 lakh INR
            regional_instances = [inst for inst in regional_instances 
                                if ComplianceLevel.PCI_DSS in inst.compliance_levels]
        
        # Select best instance based on load and latency
        return self._select_optimal_instance(regional_instances, tx_requirements)
    
    async def _fetch_service_instances(self, service_name: str) -> List[PhonePeServiceInstance]:
        """Fetch service instances from multiple Consul nodes with failover"""
        
        for consul_client in self.consul_clients:
            try:
                _, services = consul_client.health.service(service_name, passing=True)
                
                instances = []
                for service in services:
                    service_info = service['Service']
                    meta = service_info.get('Meta', {})
                    
                    # Parse compliance levels
                    compliance_str = meta.get('compliance_levels', '')
                    compliance_levels = set()
                    for level in compliance_str.split(','):
                        try:
                            compliance_levels.add(ComplianceLevel(level.strip()))
                        except ValueError:
                            continue
                    
                    # Parse data classifications
                    data_class_str = meta.get('data_classifications', '')
                    data_classifications = set()
                    for classification in data_class_str.split(','):
                        try:
                            data_classifications.add(DataClassification(classification.strip()))
                        except ValueError:
                            continue
                    
                    instance = PhonePeServiceInstance(
                        service_id=service_info['ID'],
                        host=service_info['Address'],
                        port=service_info['Port'],
                        region=meta.get('region', 'unknown'),
                        zone=meta.get('zone', 'unknown'),
                        datacenter=meta.get('datacenter', 'unknown'),
                        version=meta.get('version', '1.0.0'),
                        compliance_levels=compliance_levels,
                        data_classifications=data_classifications,
                        max_tps=int(meta.get('max_tps', '1000')),
                        current_load=float(meta.get('current_load', '0.5')),
                        encryption_enabled=meta.get('encryption_enabled', 'false').lower() == 'true',
                        audit_enabled=meta.get('audit_enabled', 'false').lower() == 'true',
                        uptime_percentage=float(meta.get('uptime_percentage', '99.9'))
                    )
                    instances.append(instance)
                
                return instances
                
            except Exception as e:
                print(f"Failed to fetch from consul node: {e}")
                continue
        
        return []  # All consul nodes failed
    
    def _meets_compliance_requirements(self, instance: PhonePeServiceInstance, 
                                     tx_requirements: Dict) -> bool:
        """Check if instance meets transaction compliance requirements"""
        
        required_compliance = tx_requirements['required_compliance']
        required_data_class = tx_requirements['data_classification']
        encryption_required = tx_requirements['encryption_required']
        
        # Check compliance levels
        for level in required_compliance:
            if level not in instance.compliance_levels:
                return False
        
        # Check data classification support
        if required_data_class not in instance.data_classifications:
            return False
        
        # Check encryption requirement
        if encryption_required and not instance.encryption_enabled:
            return False
        
        # Check if instance is healthy
        if instance.circuit_breaker_state != "CLOSED":
            return False
        
        # Check load
        if instance.current_load > 0.9:  # 90% load threshold
            return False
        
        return True
    
    def _filter_by_region(self, instances: List[PhonePeServiceInstance], 
                         user_region: str) -> List[PhonePeServiceInstance]:
        """Filter instances by regional preference"""
        
        if user_region not in self.region_configs:
            return instances
        
        region_config = self.region_configs[user_region]
        
        # Prefer instances in same region
        same_region = [inst for inst in instances if inst.region == user_region]
        if same_region:
            return same_region
        
        # Fallback to nearby regions (simplified logic)
        nearby_regions = {
            "mumbai": ["pune", "nashik", "delhi"],
            "delhi": ["gurgaon", "noida", "mumbai"],
            "bangalore": ["mysore", "chennai", "hyderabad"],
            "hyderabad": ["bangalore", "mumbai", "delhi"]
        }
        
        for nearby_region in nearby_regions.get(user_region, []):
            nearby_instances = [inst for inst in instances if inst.region == nearby_region]
            if nearby_instances:
                return nearby_instances
        
        return instances  # Return all if no regional preference possible
    
    def _select_optimal_instance(self, instances: List[PhonePeServiceInstance], 
                               tx_requirements: Dict) -> Optional[PhonePeServiceInstance]:
        """Select optimal instance based on load, latency, and performance"""
        
        if not instances:
            return None
        
        # Score each instance
        scored_instances = []
        for instance in instances:
            score = self._calculate_instance_score(instance, tx_requirements)
            scored_instances.append((score, instance))
        
        # Sort by score (higher is better)
        scored_instances.sort(reverse=True)
        
        # Return best instance
        return scored_instances[0][1]
    
    def _calculate_instance_score(self, instance: PhonePeServiceInstance, 
                                tx_requirements: Dict) -> float:
        """Calculate instance score based on multiple factors"""
        
        score = 100.0
        
        # Load factor (lower load = higher score)
        load_score = (1.0 - instance.current_load) * 30
        score += load_score
        
        # Uptime factor
        uptime_score = (instance.uptime_percentage / 100) * 20
        score += uptime_score
        
        # TPS capacity factor
        max_latency = tx_requirements['max_latency_ms']
        if instance.max_tps > 5000:  # High capacity
            score += 15
        elif instance.max_tps > 2000:  # Medium capacity
            score += 10
        elif instance.max_tps > 500:   # Low capacity
            score += 5
        
        # Version preference (newer versions preferred)
        try:
            version_parts = instance.version.split('.')
            major_version = int(version_parts[0])
            minor_version = int(version_parts[1]) if len(version_parts) > 1 else 0
            
            if major_version >= 2:
                score += 10
            elif major_version == 1 and minor_version >= 5:
                score += 5
        except:
            pass  # Skip version scoring if parsing fails
        
        # Security bonus
        if instance.audit_enabled:
            score += 5
        
        return score

# Real-world usage example for PhonePe UPI transaction
async def phonepe_upi_transaction_discovery():
    """Example of service discovery for PhonePe UPI transaction"""
    
    # PhonePe's production Consul cluster
    consul_cluster = [
        "consul1.mumbai.phonepe.internal:8500",
        "consul2.mumbai.phonepe.internal:8500", 
        "consul3.mumbai.phonepe.internal:8500"
    ]
    
    # Redis cluster for caching
    redis_cluster = [
        "redis1.mumbai.phonepe.internal:6379",
        "redis2.mumbai.phonepe.internal:6379"
    ]
    
    discovery = PhonePeServiceDiscovery(consul_cluster, redis_cluster)
    
    # Scenario: User in Mumbai wants to transfer ₹50,000 via UPI
    payment_service = await discovery.discover_service_for_transaction(
        service_name="payment-processor",
        transaction_type="upi",
        user_region="mumbai", 
        amount=50000
    )
    
    if payment_service:
        print(f"Selected payment service for UPI transaction:")
        print(f"  Service ID: {payment_service.service_id}")
        print(f"  Endpoint: {payment_service.host}:{payment_service.port}")
        print(f"  Region: {payment_service.region}")
        print(f"  Compliance: {', '.join([level.value for level in payment_service.compliance_levels])}")
        print(f"  Current Load: {payment_service.current_load:.2%}")
        print(f"  Max TPS: {payment_service.max_tps}")
        print(f"  Encryption: {'✅' if payment_service.encryption_enabled else '❌'}")
        print(f"  Audit Enabled: {'✅' if payment_service.audit_enabled else '❌'}")
    else:
        print("❌ No suitable payment service found for UPI transaction")

# Run the example
asyncio.run(phonepe_upi_transaction_discovery())
```

Dekho yeh example mein kaise PhonePe real-world challenges handle karta hai:
- **Regulatory Compliance**: RBI, PCI-DSS, NPCI requirements
- **Regional Routing**: User location ke basis pe optimal service selection
- **Load Balancing**: Current load aur capacity ke basis pe intelligent routing
- **Security**: Encryption aur audit requirements
- **High Availability**: Multiple consul nodes with failover

#### Paytm's Dynamic Service Mesh Discovery

Paytm ka approach thoda alag hai - woh service mesh use karte hain with Istio/Envoy. Yeh pattern bilkul Mumbai traffic police system jaisa hai - har intersection pe intelligent traffic management!

```go
// Paytm's Istio-based service discovery with Indian compliance
package main

import (
    "context"
    "fmt"
    "log"
    "time"
    "crypto/tls"
    "net/http"
    "encoding/json"
    
    "istio.io/client-go/pkg/clientset/versioned"
    networkingv1beta1 "istio.io/api/networking/v1beta1"
    v1beta1 "istio.io/client-go/pkg/apis/networking/v1beta1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
)

type PaytmServiceMeshController struct {
    k8sClient    kubernetes.Interface
    istioClient  versioned.Interface
    namespace    string
    regions      []string
    
    // Indian compliance configurations
    complianceRules map[string]ComplianceRule
}

type ComplianceRule struct {
    RequiredCertifications []string `json:"required_certifications"`
    DataResidency         string   `json:"data_residency"`
    EncryptionLevel       string   `json:"encryption_level"`
    AuditRequired         bool     `json:"audit_required"`
    MaxLatencyMs          int      `json:"max_latency_ms"`
}

type PaytmServiceEndpoint struct {
    ServiceName    string                 `json:"service_name"`
    Host          string                 `json:"host"`
    Port          int32                  `json:"port"`
    Region        string                 `json:"region"`
    Zone          string                 `json:"zone"`
    Weight        int32                  `json:"weight"`
    Metadata      map[string]string      `json:"metadata"`
    HealthStatus  string                 `json:"health_status"`
    Compliance    ComplianceRule         `json:"compliance"`
}

func NewPaytmServiceMeshController() (*PaytmServiceMeshController, error) {
    config, err := rest.InClusterConfig()
    if err != nil {
        return nil, err
    }
    
    k8sClient, err := kubernetes.NewForConfig(config)
    if err != nil {
        return nil, err
    }
    
    istioClient, err := versioned.NewForConfig(config)
    if err != nil {
        return nil, err
    }
    
    // Define compliance rules for different service types
    complianceRules := map[string]ComplianceRule{
        "payment": {
            RequiredCertifications: []string{"RBI", "PCI-DSS", "ISO27001"},
            DataResidency:         "india",
            EncryptionLevel:       "AES256",
            AuditRequired:         true,
            MaxLatencyMs:          200,
        },
        "wallet": {
            RequiredCertifications: []string{"RBI", "PCI-DSS"},
            DataResidency:         "india", 
            EncryptionLevel:       "AES256",
            AuditRequired:         true,
            MaxLatencyMs:          150,
        },
        "kyc": {
            RequiredCertifications: []string{"RBI", "UIDAI"},
            DataResidency:         "india",
            EncryptionLevel:       "AES256", 
            AuditRequired:         true,
            MaxLatencyMs:          500,
        },
        "analytics": {
            RequiredCertifications: []string{},
            DataResidency:         "india",
            EncryptionLevel:       "AES128",
            AuditRequired:         false,
            MaxLatencyMs:          1000,
        },
    }
    
    return &PaytmServiceMeshController{
        k8sClient:       k8sClient,
        istioClient:     istioClient,
        namespace:       "paytm-production",
        regions:         []string{"mumbai", "delhi", "bangalore", "hyderabad"},
        complianceRules: complianceRules,
    }, nil
}

func (p *PaytmServiceMeshController) DiscoverServiceEndpoints(serviceName string, 
    serviceType string, userRegion string) ([]PaytmServiceEndpoint, error) {
    
    // Get compliance rules for service type
    complianceRule, exists := p.complianceRules[serviceType]
    if !exists {
        complianceRule = p.complianceRules["analytics"] // Default
    }
    
    // Get Istio DestinationRule for the service
    destinationRule, err := p.istioClient.NetworkingV1beta1().
        DestinationRules(p.namespace).
        Get(context.TODO(), serviceName, metav1.GetOptions{})
    
    if err != nil {
        return nil, fmt.Errorf("failed to get DestinationRule: %v", err)
    }
    
    var endpoints []PaytmServiceEndpoint
    
    // Parse subsets from DestinationRule
    for _, subset := range destinationRule.Spec.Subsets {
        // Extract endpoint information from subset
        endpoint := PaytmServiceEndpoint{
            ServiceName:  serviceName,
            Region:       subset.Labels["region"],
            Zone:         subset.Labels["zone"],
            Metadata:     subset.Labels,
            Compliance:   complianceRule,
        }
        
        // Check if subset meets compliance requirements
        if p.meetsComplianceRequirements(subset.Labels, complianceRule) {
            // Get actual endpoint details from Kubernetes service
            if err := p.populateEndpointDetails(&endpoint); err == nil {
                endpoints = append(endpoints, endpoint)
            }
        }
    }
    
    // Filter by region preference
    regionalEndpoints := p.filterByRegionPreference(endpoints, userRegion)
    
    return regionalEndpoints, nil
}

func (p *PaytmServiceMeshController) meetsComplianceRequirements(labels map[string]string, 
    rule ComplianceRule) bool {
    
    // Check required certifications
    for _, cert := range rule.RequiredCertifications {
        certKey := fmt.Sprintf("compliance.%s", cert)
        if value, exists := labels[certKey]; !exists || value != "true" {
            return false
        }
    }
    
    // Check data residency
    if dataResidency, exists := labels["data-residency"]; !exists || dataResidency != rule.DataResidency {
        return false
    }
    
    // Check encryption level
    if encLevel, exists := labels["encryption-level"]; exists {
        if !p.isEncryptionSufficient(encLevel, rule.EncryptionLevel) {
            return false
        }
    }
    
    // Check audit capability
    if rule.AuditRequired {
        if audit, exists := labels["audit-enabled"]; !exists || audit != "true" {
            return false
        }
    }
    
    return true
}

func (p *PaytmServiceMeshController) isEncryptionSufficient(current, required string) bool {
    encryptionLevels := map[string]int{
        "AES128": 1,
        "AES256": 2,
        "ChaCha20": 2,
    }
    
    currentLevel, currentExists := encryptionLevels[current]
    requiredLevel, requiredExists := encryptionLevels[required]
    
    if !currentExists || !requiredExists {
        return false
    }
    
    return currentLevel >= requiredLevel
}

func (p *PaytmServiceMeshController) populateEndpointDetails(endpoint *PaytmServiceEndpoint) error {
    // Get service details from Kubernetes
    service, err := p.k8sClient.CoreV1().Services(p.namespace).
        Get(context.TODO(), endpoint.ServiceName, metav1.GetOptions{})
    
    if err != nil {
        return err
    }
    
    if len(service.Spec.Ports) > 0 {
        endpoint.Port = service.Spec.Ports[0].Port
    }
    
    // Get endpoints to find actual pod IPs
    endpoints, err := p.k8sClient.CoreV1().Endpoints(p.namespace).
        Get(context.TODO(), endpoint.ServiceName, metav1.GetOptions{})
    
    if err != nil {
        return err
    }
    
    // Use first available address
    if len(endpoints.Subsets) > 0 && len(endpoints.Subsets[0].Addresses) > 0 {
        endpoint.Host = endpoints.Subsets[0].Addresses[0].IP
    }
    
    // Perform health check
    endpoint.HealthStatus = p.performHealthCheck(endpoint.Host, endpoint.Port)
    
    return nil
}

func (p *PaytmServiceMeshController) performHealthCheck(host string, port int32) string {
    // Create HTTP client with timeout suitable for Indian networks
    client := &http.Client{
        Timeout: 3 * time.Second,
        Transport: &http.Transport{
            TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
        },
    }
    
    healthURL := fmt.Sprintf("http://%s:%d/health", host, port)
    
    resp, err := client.Get(healthURL)
    if err != nil {
        return "unhealthy"
    }
    defer resp.Body.Close()
    
    if resp.StatusCode == 200 {
        return "healthy"
    }
    
    return "degraded"
}

func (p *PaytmServiceMeshController) filterByRegionPreference(endpoints []PaytmServiceEndpoint, 
    userRegion string) []PaytmServiceEndpoint {
    
    // Regional preference for Indian geography
    regionPreference := map[string][]string{
        "mumbai":    {"mumbai", "pune", "delhi", "bangalore"},
        "delhi":     {"delhi", "gurgaon", "mumbai", "bangalore"}, 
        "bangalore": {"bangalore", "chennai", "hyderabad", "mumbai"},
        "hyderabad": {"hyderabad", "bangalore", "chennai", "mumbai"},
        "pune":      {"pune", "mumbai", "bangalore", "delhi"},
        "chennai":   {"chennai", "bangalore", "hyderabad", "mumbai"},
    }
    
    preferences := regionPreference[userRegion]
    if preferences == nil {
        return endpoints // No preference, return all
    }
    
    // Sort endpoints by region preference
    var sortedEndpoints []PaytmServiceEndpoint
    
    for _, preferredRegion := range preferences {
        for _, endpoint := range endpoints {
            if endpoint.Region == preferredRegion && endpoint.HealthStatus == "healthy" {
                sortedEndpoints = append(sortedEndpoints, endpoint)
            }
        }
    }
    
    // Add remaining healthy endpoints
    for _, endpoint := range endpoints {
        found := false
        for _, sorted := range sortedEndpoints {
            if sorted.Host == endpoint.Host && sorted.Port == endpoint.Port {
                found = true
                break
            }
        }
        if !found && endpoint.HealthStatus == "healthy" {
            sortedEndpoints = append(sortedEndpoints, endpoint)
        }
    }
    
    return sortedEndpoints
}

// Create Istio VirtualService for traffic management
func (p *PaytmServiceMeshController) CreateTrafficManagementRules(serviceName string, 
    serviceType string) error {
    
    // Get compliance rules
    complianceRule := p.complianceRules[serviceType]
    
    virtualService := &v1beta1.VirtualService{
        ObjectMeta: metav1.ObjectMeta{
            Name:      fmt.Sprintf("%s-routing", serviceName),
            Namespace: p.namespace,
            Labels: map[string]string{
                "app":         serviceName,
                "service-type": serviceType,
                "compliance":  "rbi-approved",
            },
        },
        Spec: networkingv1beta1.VirtualService{
            Hosts: []string{serviceName},
            Http: []*networkingv1beta1.HTTPRoute{
                {
                    Match: []*networkingv1beta1.HTTPMatchRequest{
                        {
                            Headers: map[string]*networkingv1beta1.StringMatch{
                                "x-user-region": {
                                    MatchType: &networkingv1beta1.StringMatch_Exact{
                                        Exact: "mumbai",
                                    },
                                },
                            },
                        },
                    },
                    Route: []*networkingv1beta1.HTTPRouteDestination{
                        {
                            Destination: &networkingv1beta1.Destination{
                                Host:   serviceName,
                                Subset: "mumbai",
                            },
                            Weight: 100,
                        },
                    },
                    Timeout: &networkingv1beta1.Duration{
                        Seconds: int64(complianceRule.MaxLatencyMs / 1000),
                    },
                },
                {
                    // Default route for other regions
                    Route: []*networkingv1beta1.HTTPRouteDestination{
                        {
                            Destination: &networkingv1beta1.Destination{
                                Host:   serviceName,
                                Subset: "default",
                            },
                            Weight: 100,
                        },
                    },
                },
            },
        },
    }
    
    _, err := p.istioClient.NetworkingV1beta1().VirtualServices(p.namespace).
        Create(context.TODO(), virtualService, metav1.CreateOptions{})
    
    return err
}

// Usage example for Paytm wallet service discovery
func paytmWalletServiceDiscoveryExample() {
    controller, err := NewPaytmServiceMeshController()
    if err != nil {
        log.Fatalf("Failed to create controller: %v", err)
    }
    
    // Discover wallet service for user in Mumbai
    endpoints, err := controller.DiscoverServiceEndpoints("wallet-service", "wallet", "mumbai")
    if err != nil {
        log.Printf("Service discovery failed: %v", err)
        return
    }
    
    fmt.Printf("Discovered %d wallet service endpoints:\n", len(endpoints))
    for i, endpoint := range endpoints {
        fmt.Printf("Endpoint %d:\n", i+1)
        fmt.Printf("  Host: %s:%d\n", endpoint.Host, endpoint.Port)
        fmt.Printf("  Region: %s, Zone: %s\n", endpoint.Region, endpoint.Zone)
        fmt.Printf("  Health: %s\n", endpoint.HealthStatus)
        fmt.Printf("  Compliance: %+v\n", endpoint.Compliance)
        
        // Create traffic management rules
        if err := controller.CreateTrafficManagementRules("wallet-service", "wallet"); err != nil {
            log.Printf("Failed to create traffic rules: %v", err)
        }
    }
}
```

Paytm ka approach show karta hai kaise service mesh sophisticated traffic management provide kar sakta hai:
- **Istio Integration**: VirtualService aur DestinationRule based routing
- **Compliance-First Design**: Service discovery mein compliance checks embedded
- **Regional Intelligence**: Geography-aware routing for better performance
- **Automatic Traffic Management**: Rules create kar ke traffic automatically route karna

### Chapter 6: Kubernetes Service Discovery Deep Dive (80-95 Minutes)

#### Kubernetes Native Service Discovery

Kubernetes ka built-in service discovery bilkul Mumbai ke BEST bus system jaisa hai - fixed routes, scheduled stops, reliable coordination!

```yaml
# Comprehensive Kubernetes service discovery setup for Jio's 5G services
# This shows production-grade configuration with Indian requirements

# 1. Core Service Definition
apiVersion: v1
kind: Service
metadata:
  name: jio-5g-network-service
  namespace: jio-production
  labels:
    app: jio-5g-network
    tier: backend
    compliance: dot-certified
    region: multi-region
  annotations:
    # Service discovery annotations for Jio's network
    service.discovery/health-check-path: "/health"
    service.discovery/health-check-interval: "10s"
    service.discovery/health-check-timeout: "3s"
    
    # Indian network optimization annotations  
    network.jio.com/latency-target: "50ms"
    network.jio.com/bandwidth-requirement: "10Gbps"
    network.jio.com/availability-zone: "multi-az"
    
    # Regulatory compliance annotations
    compliance.dot.gov.in/certified: "true"
    compliance.dot.gov.in/license-number: "DOT/5G/2024/Mumbai/001"
    compliance.dot.gov.in/spectrum-band: "3.5GHz,26GHz"
    
    # Service mesh integration
    istio.io/service-account: jio-5g-service-account
    linkerd.io/inject: enabled
    
    # Monitoring and observability
    prometheus.io/scrape: "true" 
    prometheus.io/port: "9090"
    prometheus.io/path: "/metrics"
    
    # Load balancing preferences
    traefik.ingress.kubernetes.io/load-balancer-method: "wrr"  # Weighted Round Robin
    nginx.ingress.kubernetes.io/upstream-hash-by: "$request_uri consistent"
spec:
  type: LoadBalancer
  loadBalancerSourceRanges:
    # Restrict access to Indian IP ranges
    - "103.21.244.0/22"    # Jio Fiber
    - "157.119.0.0/16"     # Jio Mobile  
    - "49.14.0.0/15"       # Airtel
    - "27.109.0.0/16"      # BSNL
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600  # 1 hour session stickiness for 5G handover
  selector:
    app: jio-5g-network
    version: stable
    compliance: dot-certified
  ports:
  - name: grpc-api
    port: 443
    targetPort: 8443
    protocol: TCP
  - name: http-api  
    port: 80
    targetPort: 8080
    protocol: TCP
  - name: metrics
    port: 9090
    targetPort: 9090
    protocol: TCP
  - name: health
    port: 8088
    targetPort: 8088
    protocol: TCP

---
# 2. Headless Service for direct pod access
apiVersion: v1
kind: Service  
metadata:
  name: jio-5g-network-headless
  namespace: jio-production
  labels:
    app: jio-5g-network
    service-type: headless
spec:
  clusterIP: None  # Headless service
  selector:
    app: jio-5g-network
  ports:
  - name: grpc-api
    port: 8443
    targetPort: 8443

---
# 3. Service Monitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: jio-5g-network-monitor
  namespace: jio-production
  labels:
    app: jio-5g-network
    monitoring: enabled
spec:
  selector:
    matchLabels:
      app: jio-5g-network
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
    honorLabels: true
    metricRelabelings:
    - sourceLabels: [__name__]
      regex: 'jio_5g_(latency|throughput|users|handover).*'
      action: keep
    - sourceLabels: [region]
      targetLabel: jio_region
    - sourceLabels: [zone] 
      targetLabel: jio_zone

---
# 4. Network Policy for security
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: jio-5g-network-policy
  namespace: jio-production
spec:
  podSelector:
    matchLabels:
      app: jio-5g-network
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    # Allow traffic from Jio's internal services
    - namespaceSelector:
        matchLabels:
          name: jio-internal
    - podSelector:
        matchLabels:
          app: jio-gateway
    ports:
    - protocol: TCP
      port: 8080
    - protocol: TCP  
      port: 8443
  egress:
  - to:
    # Allow access to Jio's databases
    - namespaceSelector:
        matchLabels:
          name: jio-data
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
  - to: []  # Allow DNS resolution
    ports:
    - protocol: UDP
      port: 53

---
# 5. Deployment with service discovery optimization
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jio-5g-network-deployment
  namespace: jio-production
  labels:
    app: jio-5g-network
    version: v2.1.0
spec:
  replicas: 12  # Distributed across multiple AZs
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 3
      maxUnavailable: 1
  selector:
    matchLabels:
      app: jio-5g-network
  template:
    metadata:
      labels:
        app: jio-5g-network
        version: stable
        compliance: dot-certified
        tier: backend
      annotations:
        # Service discovery hints
        service.discovery/health-port: "8088"
        service.discovery/ready-port: "8088"
        service.discovery/region: "mumbai"
        
        # Container resource hints for service selection
        resources.limits/cpu: "2000m"
        resources.limits/memory: "4Gi"
        resources.requests/cpu: "1000m" 
        resources.requests/memory: "2Gi"
        
        # Network configuration
        network.jio.com/interface-type: "5g-capable"
        network.jio.com/bandwidth-class: "ultra-high"
    spec:
      serviceAccountName: jio-5g-service-account
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: jio-5g-network
        image: jio.azurecr.io/5g-network:v2.1.0
        ports:
        - containerPort: 8080
          name: http-api
          protocol: TCP
        - containerPort: 8443  
          name: grpc-api
          protocol: TCP
        - containerPort: 9090
          name: metrics
          protocol: TCP
        - containerPort: 8088
          name: health
          protocol: TCP
        env:
        - name: SERVICE_NAME
          value: "jio-5g-network"
        - name: SERVICE_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        # Regional configuration
        - name: JIO_REGION
          value: "mumbai"
        - name: JIO_ZONE
          value: "mumbai-1a"
        - name: JIO_DATACENTER
          value: "mumbai-dc1"
        # Service discovery configuration
        - name: DISCOVERY_NAMESPACE
          value: "jio-production"
        - name: DISCOVERY_SERVICE_NAME  
          value: "jio-5g-network-headless"
        livenessProbe:
          httpGet:
            path: /health/live
            port: health
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: health
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        startupProbe:
          httpGet:
            path: /health/startup
            port: health
          initialDelaySeconds: 10
          periodSeconds: 2
          timeoutSeconds: 1
          failureThreshold: 30
        resources:
          limits:
            cpu: 2000m
            memory: 4Gi
            nvidia.com/gpu: 1  # For 5G signal processing
          requests:
            cpu: 1000m
            memory: 2Gi
        volumeMounts:
        - name: config-volume
          mountPath: /etc/jio/config
        - name: certs-volume
          mountPath: /etc/jio/certs
          readOnly: true
      volumes:
      - name: config-volume
        configMap:
          name: jio-5g-config
      - name: certs-volume
        secret:
          secretName: jio-5g-tls-certs
      # Anti-affinity to distribute pods across nodes
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - jio-5g-network
              topologyKey: kubernetes.io/hostname
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 80
            preference:
              matchExpressions:
              - key: node.jio.com/network-capability
                operator: In
                values:
                - 5g-enabled
          - weight: 60  
            preference:
              matchExpressions:
              - key: topology.kubernetes.io/zone
                operator: In
                values:
                - mumbai-1a
                - mumbai-1b
                - mumbai-1c

---
# 6. HorizontalPodAutoscaler for dynamic scaling
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: jio-5g-network-hpa
  namespace: jio-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: jio-5g-network-deployment
  minReplicas: 6   # Minimum for high availability
  maxReplicas: 24  # Maximum based on infrastructure capacity
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  # Custom metrics for 5G network load
  - type: Pods
    pods:
      metric:
        name: jio_5g_active_users
      target:
        type: AverageValue
        averageValue: "1000"  # 1000 active users per pod
  - type: Pods
    pods:
      metric:
        name: jio_5g_throughput_mbps
      target:
        type: AverageValue
        averageValue: "500"   # 500 Mbps per pod
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 minutes before scaling down
      policies:
      - type: Percent
        value: 25  
        periodSeconds: 60

---
# 7. Service Discovery ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: jio-5g-config
  namespace: jio-production
data:
  service-discovery.yaml: |
    discovery:
      enabled: true
      namespace: jio-production
      service_name: jio-5g-network-headless
      refresh_interval: 30s
      health_check:
        enabled: true
        path: /health/ready
        timeout: 3s
        interval: 10s
      load_balancing:
        algorithm: weighted_round_robin
        weights:
          mumbai: 40
          delhi: 30  
          bangalore: 20
          hyderabad: 10
      regional_preferences:
        - region: mumbai
          zones: [mumbai-1a, mumbai-1b, mumbai-1c]
          latency_threshold: 50ms
        - region: delhi
          zones: [delhi-1a, delhi-1b] 
          latency_threshold: 80ms
        - region: bangalore
          zones: [bangalore-1a, bangalore-1b]
          latency_threshold: 60ms
      compliance:
        dot_certification_required: true
        data_residency: india
        encryption_in_transit: true
        audit_logging: true
  network.yaml: |
    5g:
      bands:
        - 3.5GHz
        - 26GHz
      max_throughput: 1Gbps
      max_concurrent_users: 10000
      handover_latency: <10ms
    regions:
      mumbai:
        towers: 2500
        coverage: 95%
        peak_users: 5M
      delhi: 
        towers: 2000
        coverage: 92%
        peak_users: 4M
      bangalore:
        towers: 1800
        coverage: 90% 
        peak_users: 3.5M
```

Iska corresponding Go client code for service discovery:

```go
// Kubernetes service discovery client for Jio's 5G services
package main

import (
    "context"
    "fmt"
    "log"
    "strings"
    "time"
    
    v1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    "k8s.io/client-go/tools/cache"
    "k8s.io/client-go/informers"
)

type Jio5GServiceDiscovery struct {
    clientset       kubernetes.Interface
    namespace       string
    serviceCache    map[string][]ServiceEndpoint
    informerFactory informers.SharedInformerFactory
}

type ServiceEndpoint struct {
    Name            string            `json:"name"`
    Host            string            `json:"host"`
    Port            int32             `json:"port"`
    Region          string            `json:"region"`
    Zone            string            `json:"zone"`
    Labels          map[string]string `json:"labels"`
    Annotations     map[string]string `json:"annotations"`
    HealthStatus    string            `json:"health_status"`
    LoadPercentage  float64           `json:"load_percentage"`
    Compliance      ComplianceInfo    `json:"compliance"`
}

type ComplianceInfo struct {
    DOTCertified       bool   `json:"dot_certified"`
    LicenseNumber      string `json:"license_number"`
    SpectrumBands      []string `json:"spectrum_bands"`
    DataResidencyIndia bool   `json:"data_residency_india"`
}

func NewJio5GServiceDiscovery() (*Jio5GServiceDiscovery, error) {
    config, err := rest.InClusterConfig()
    if err != nil {
        return nil, fmt.Errorf("failed to get in-cluster config: %v", err)
    }
    
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        return nil, fmt.Errorf("failed to create clientset: %v", err)
    }
    
    namespace := "jio-production"
    
    // Create informer factory for watching services and endpoints
    informerFactory := informers.NewSharedInformerFactoryWithOptions(
        clientset, 
        30*time.Second,  // Resync period
        informers.WithNamespace(namespace),
    )
    
    discovery := &Jio5GServiceDiscovery{
        clientset:       clientset,
        namespace:       namespace,
        serviceCache:    make(map[string][]ServiceEndpoint),
        informerFactory: informerFactory,
    }
    
    // Setup informers for real-time updates
    discovery.setupInformers()
    
    return discovery, nil
}

func (j *Jio5GServiceDiscovery) setupInformers() {
    // Service informer
    serviceInformer := j.informerFactory.Core().V1().Services().Informer()
    serviceInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
        AddFunc: func(obj interface{}) {
            service := obj.(*v1.Service)
            log.Printf("Service added: %s", service.Name)
            j.updateServiceCache(service.Name)
        },
        UpdateFunc: func(oldObj, newObj interface{}) {
            service := newObj.(*v1.Service)
            log.Printf("Service updated: %s", service.Name)
            j.updateServiceCache(service.Name)
        },
        DeleteFunc: func(obj interface{}) {
            service := obj.(*v1.Service)
            log.Printf("Service deleted: %s", service.Name)
            delete(j.serviceCache, service.Name)
        },
    })
    
    // Endpoints informer  
    endpointsInformer := j.informerFactory.Core().V1().Endpoints().Informer()
    endpointsInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
        AddFunc: func(obj interface{}) {
            endpoints := obj.(*v1.Endpoints)
            log.Printf("Endpoints added: %s", endpoints.Name)
            j.updateServiceCache(endpoints.Name)
        },
        UpdateFunc: func(oldObj, newObj interface{}) {
            endpoints := newObj.(*v1.Endpoints)
            log.Printf("Endpoints updated: %s", endpoints.Name)
            j.updateServiceCache(endpoints.Name)
        },
        DeleteFunc: func(obj interface{}) {
            endpoints := obj.(*v1.Endpoints)
            log.Printf("Endpoints deleted: %s", endpoints.Name)
            j.updateServiceCache(endpoints.Name)
        },
    })
}

func (j *Jio5GServiceDiscovery) StartWatching(ctx context.Context) {
    j.informerFactory.Start(ctx.Done())
    
    // Wait for cache sync
    if !cache.WaitForCacheSync(ctx.Done(), 
        j.informerFactory.Core().V1().Services().Informer().HasSynced,
        j.informerFactory.Core().V1().Endpoints().Informer().HasSynced,
    ) {
        log.Fatal("Failed to sync caches")
    }
    
    log.Println("Service discovery informers started successfully")
}

func (j *Jio5GServiceDiscovery) DiscoverService(serviceName string, filters ServiceFilters) ([]ServiceEndpoint, error) {
    // Try cache first
    if endpoints, exists := j.serviceCache[serviceName]; exists && len(endpoints) > 0 {
        return j.filterEndpoints(endpoints, filters), nil
    }
    
    // Fallback to direct API call
    return j.discoverServiceDirect(serviceName, filters)
}

type ServiceFilters struct {
    Region          string   `json:"region"`
    Zone            string   `json:"zone"`
    ComplianceLevel string   `json:"compliance_level"`
    MaxLatency      int      `json:"max_latency_ms"`
    MinAvailability float64  `json:"min_availability"`
    RequiredLabels  map[string]string `json:"required_labels"`
}

func (j *Jio5GServiceDiscovery) discoverServiceDirect(serviceName string, filters ServiceFilters) ([]ServiceEndpoint, error) {
    // Get service
    service, err := j.clientset.CoreV1().Services(j.namespace).Get(
        context.TODO(), serviceName, metav1.GetOptions{})
    if err != nil {
        return nil, fmt.Errorf("service not found: %v", err)
    }
    
    // Get endpoints
    endpoints, err := j.clientset.CoreV1().Endpoints(j.namespace).Get(
        context.TODO(), serviceName, metav1.GetOptions{})
    if err != nil {
        return nil, fmt.Errorf("endpoints not found: %v", err)
    }
    
    var serviceEndpoints []ServiceEndpoint
    
    for _, subset := range endpoints.Subsets {
        for _, addr := range subset.Addresses {
            // Extract metadata from pod if available
            region := "unknown"
            zone := "unknown"
            compliance := ComplianceInfo{}
            
            if addr.TargetRef != nil && addr.TargetRef.Kind == "Pod" {
                pod, err := j.clientset.CoreV1().Pods(j.namespace).Get(
                    context.TODO(), addr.TargetRef.Name, metav1.GetOptions{})
                if err == nil {
                    // Extract region and zone from pod labels
                    if r, exists := pod.Labels["topology.kubernetes.io/region"]; exists {
                        region = r
                    }
                    if z, exists := pod.Labels["topology.kubernetes.io/zone"]; exists {
                        zone = z
                    }
                    
                    // Extract compliance info from annotations
                    compliance = j.extractComplianceInfo(pod.Annotations)
                }
            }
            
            for _, port := range subset.Ports {
                endpoint := ServiceEndpoint{
                    Name:         serviceName,
                    Host:         addr.IP,
                    Port:         port.Port,
                    Region:       region,
                    Zone:         zone,
                    Labels:       service.Labels,
                    Annotations:  service.Annotations,
                    HealthStatus: "healthy", // Assume healthy if in endpoints
                    Compliance:   compliance,
                }
                
                serviceEndpoints = append(serviceEndpoints, endpoint)
            }
        }
    }
    
    // Update cache
    j.serviceCache[serviceName] = serviceEndpoints
    
    return j.filterEndpoints(serviceEndpoints, filters), nil
}

func (j *Jio5GServiceDiscovery) extractComplianceInfo(annotations map[string]string) ComplianceInfo {
    compliance := ComplianceInfo{}
    
    if certified, exists := annotations["compliance.dot.gov.in/certified"]; exists {
        compliance.DOTCertified = certified == "true"
    }
    
    if license, exists := annotations["compliance.dot.gov.in/license-number"]; exists {
        compliance.LicenseNumber = license
    }
    
    if bands, exists := annotations["compliance.dot.gov.in/spectrum-band"]; exists {
        compliance.SpectrumBands = strings.Split(bands, ",")
    }
    
    // Assume data residency is India for Jio services
    compliance.DataResidencyIndia = true
    
    return compliance
}

func (j *Jio5GServiceDiscovery) filterEndpoints(endpoints []ServiceEndpoint, filters ServiceFilters) []ServiceEndpoint {
    var filtered []ServiceEndpoint
    
    for _, endpoint := range endpoints {
        // Region filter
        if filters.Region != "" && endpoint.Region != filters.Region {
            continue
        }
        
        // Zone filter
        if filters.Zone != "" && endpoint.Zone != filters.Zone {
            continue
        }
        
        // Compliance filter
        if filters.ComplianceLevel == "dot-certified" && !endpoint.Compliance.DOTCertified {
            continue
        }
        
        // Required labels filter
        if filters.RequiredLabels != nil {
            skip := false
            for key, value := range filters.RequiredLabels {
                if labelValue, exists := endpoint.Labels[key]; !exists || labelValue != value {
                    skip = true
                    break
                }
            }
            if skip {
                continue
            }
        }
        
        filtered = append(filtered, endpoint)
    }
    
    return filtered
}

func (j *Jio5GServiceDiscovery) updateServiceCache(serviceName string) {
    // This would be called by informers to update cache
    endpoints, err := j.discoverServiceDirect(serviceName, ServiceFilters{})
    if err != nil {
        log.Printf("Failed to update cache for service %s: %v", serviceName, err)
        return
    }
    
    j.serviceCache[serviceName] = endpoints
    log.Printf("Updated cache for service %s with %d endpoints", serviceName, len(endpoints))
}

// Usage example for Jio's 5G network service discovery
func jio5GServiceDiscoveryExample() {
    discovery, err := NewJio5GServiceDiscovery()
    if err != nil {
        log.Fatalf("Failed to create service discovery: %v", err)
    }
    
    // Start watching for service changes
    ctx := context.Background()
    go discovery.StartWatching(ctx)
    
    // Wait a bit for cache to populate
    time.Sleep(5 * time.Second)
    
    // Discover 5G network services in Mumbai region
    filters := ServiceFilters{
        Region:          "mumbai",
        ComplianceLevel: "dot-certified",
        RequiredLabels: map[string]string{
            "app":        "jio-5g-network",
            "compliance": "dot-certified",
        },
    }
    
    endpoints, err := discovery.DiscoverService("jio-5g-network-service", filters)
    if err != nil {
        log.Fatalf("Service discovery failed: %v", err)
    }
    
    fmt.Printf("Discovered %d 5G network service endpoints in Mumbai:\n", len(endpoints))
    for i, endpoint := range endpoints {
        fmt.Printf("Endpoint %d:\n", i+1)
        fmt.Printf("  Host: %s:%d\n", endpoint.Host, endpoint.Port)
        fmt.Printf("  Region: %s, Zone: %s\n", endpoint.Region, endpoint.Zone)
        fmt.Printf("  DOT Certified: %v\n", endpoint.Compliance.DOTCertified)
        fmt.Printf("  License: %s\n", endpoint.Compliance.LicenseNumber)
        fmt.Printf("  Spectrum Bands: %v\n", endpoint.Compliance.SpectrumBands)
        fmt.Printf("  Health: %s\n", endpoint.HealthStatus)
        fmt.Println()
    }
}

func main() {
    jio5GServiceDiscoveryExample()
}
```

### Chapter 7: Circuit Breaker Pattern Integration (95-110 Minutes)

Service discovery ka ek important aspect hai circuit breaker pattern - jab service down ho toh automatically bypass kar dena. Yeh bilkul Mumbai monsoon mein alternate routes use karne jaisa hai!

```python
# Circuit breaker integrated service discovery for Swiggy
import asyncio
import time
import threading
from enum import Enum
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import aiohttp
import json

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open" # Testing if service is back

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration for Indian network conditions"""
    failure_threshold: int = 5           # Failures before opening
    success_threshold: int = 3           # Successes to close from half-open  
    timeout_seconds: int = 60           # How long to keep circuit open
    slow_call_threshold_ms: int = 2000  # Calls slower than this are failures
    minimum_calls: int = 10             # Minimum calls before evaluation
    sliding_window_size: int = 100      # Rolling window for statistics

@dataclass  
class CallResult:
    """Result of a service call"""
    success: bool
    response_time_ms: int
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

class SwiggyCircuitBreaker:
    """Production circuit breaker for Swiggy's delivery services"""
    
    def __init__(self, service_name: str, config: CircuitBreakerConfig):
        self.service_name = service_name
        self.config = config
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        
        # Sliding window for tracking calls
        self.call_history = deque(maxlen=config.sliding_window_size)
        self.lock = threading.RLock()
        
        # Metrics for monitoring
        self.total_calls = 0
        self.total_failures = 0
        self.total_timeouts = 0
        self.state_change_history = []
        
    def call(self, func: Callable, *args, **kwargs):
        """Execute function call through circuit breaker"""
        with self.lock:
            # Check if circuit is open
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    self._record_blocked_call()
                    raise CircuitBreakerOpenError(f"Circuit breaker is OPEN for {self.service_name}")
            
            # Execute the call
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                response_time_ms = int((time.time() - start_time) * 1000)
                
                # Check if call was too slow (considered failure in Indian networks)
                if response_time_ms > self.config.slow_call_threshold_ms:
                    self._record_failure(response_time_ms, "Slow response")
                else:
                    self._record_success(response_time_ms)
                
                return result
                
            except Exception as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                self._record_failure(response_time_ms, str(e))
                raise
    
    def _record_success(self, response_time_ms: int):
        """Record successful call"""
        call_result = CallResult(True, response_time_ms)
        self.call_history.append(call_result)
        self.total_calls += 1
        
        if self.state == CircuitState.HALF_OPEN:
            self.consecutive_successes += 1
            if self.consecutive_successes >= self.config.success_threshold:
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            self.consecutive_failures = 0  # Reset failure count
    
    def _record_failure(self, response_time_ms: int, error_message: str):
        """Record failed call"""
        call_result = CallResult(False, response_time_ms, error_message)
        self.call_history.append(call_result)
        self.total_calls += 1
        self.total_failures += 1
        
        if response_time_ms > self.config.slow_call_threshold_ms:
            self.total_timeouts += 1
        
        self.consecutive_failures += 1
        self.consecutive_successes = 0  # Reset success count
        self.last_failure_time = time.time()
        
        # Check if we should open the circuit
        if (self.state == CircuitState.CLOSED and 
            self._should_open_circuit()):
            self._transition_to_open()
        elif (self.state == CircuitState.HALF_OPEN):
            self._transition_to_open()
    
    def _record_blocked_call(self):
        """Record call that was blocked by open circuit"""
        self.total_calls += 1
        # Don't record in call history as it wasn't actually attempted
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened"""
        if len(self.call_history) < self.config.minimum_calls:
            return False
        
        # Count recent failures
        recent_calls = list(self.call_history)[-self.config.minimum_calls:]
        failure_count = sum(1 for call in recent_calls if not call.success)
        failure_rate = failure_count / len(recent_calls)
        
        return (self.consecutive_failures >= self.config.failure_threshold or
                failure_rate >= 0.5)  # 50% failure rate threshold
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (time.time() - self.last_failure_time) >= self.config.timeout_seconds
    
    def _transition_to_open(self):
        """Transition circuit to OPEN state"""
        old_state = self.state
        self.state = CircuitState.OPEN
        self._record_state_change(old_state, CircuitState.OPEN)
        print(f"🔴 Circuit breaker OPENED for {self.service_name}")
    
    def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state"""
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.consecutive_successes = 0
        self._record_state_change(old_state, CircuitState.HALF_OPEN)
        print(f"🟡 Circuit breaker HALF-OPEN for {self.service_name}")
    
    def _transition_to_closed(self):
        """Transition circuit to CLOSED state"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self._record_state_change(old_state, CircuitState.CLOSED)
        print(f"🟢 Circuit breaker CLOSED for {self.service_name}")
    
    def _record_state_change(self, from_state: CircuitState, to_state: CircuitState):
        """Record state change for monitoring"""
        change = {
            'timestamp': time.time(),
            'from_state': from_state.value,
            'to_state': to_state.value,
            'consecutive_failures': self.consecutive_failures,
            'total_calls': self.total_calls,
            'total_failures': self.total_failures
        }
        self.state_change_history.append(change)
        
        # Keep only last 50 state changes
        if len(self.state_change_history) > 50:
            self.state_change_history = self.state_change_history[-50:]
    
    def get_metrics(self) -> Dict:
        """Get circuit breaker metrics"""
        with self.lock:
            recent_calls = list(self.call_history)[-50:]  # Last 50 calls
            
            if recent_calls:
                success_rate = sum(1 for call in recent_calls if call.success) / len(recent_calls)
                avg_response_time = sum(call.response_time_ms for call in recent_calls) / len(recent_calls)
            else:
                success_rate = 0.0
                avg_response_time = 0.0
            
            return {
                'service_name': self.service_name,
                'state': self.state.value,
                'total_calls': self.total_calls,
                'total_failures': self.total_failures,
                'total_timeouts': self.total_timeouts,
                'consecutive_failures': self.consecutive_failures,
                'consecutive_successes': self.consecutive_successes,
                'success_rate': success_rate,
                'avg_response_time_ms': avg_response_time,
                'last_failure_time': self.last_failure_time,
                'state_changes': len(self.state_change_history)
            }

class CircuitBreakerOpenError(Exception):
    """Exception thrown when circuit breaker is open"""
    pass

class SwiggyServiceDiscoveryWithCircuitBreaker:
    """Service discovery with integrated circuit breakers for Swiggy"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, SwiggyCircuitBreaker] = {}
        self.service_registry = {}
        self.fallback_services = {
            # Define fallback services for critical operations
            'payment-service': ['payment-service-backup', 'payment-gateway-v1'],
            'restaurant-service': ['restaurant-cache-service', 'restaurant-static-data'],
            'delivery-assignment': ['delivery-fallback', 'manual-assignment-service'],
            'notification-service': ['sms-gateway', 'basic-notification']
        }
        
    def get_or_create_circuit_breaker(self, service_name: str) -> SwiggyCircuitBreaker:
        """Get existing circuit breaker or create new one"""
        if service_name not in self.circuit_breakers:
            # Configure based on service type
            if 'payment' in service_name:
                config = CircuitBreakerConfig(
                    failure_threshold=3,     # Payment services - fail fast
                    timeout_seconds=30,      # Quick recovery attempts
                    slow_call_threshold_ms=1000  # 1 second for payments
                )
            elif 'delivery' in service_name:
                config = CircuitBreakerConfig(
                    failure_threshold=5,     # Delivery can tolerate more failures
                    timeout_seconds=60,      # Longer recovery time
                    slow_call_threshold_ms=3000  # 3 seconds for delivery optimization
                )
            elif 'notification' in service_name:
                config = CircuitBreakerConfig(
                    failure_threshold=10,    # Notifications are not critical
                    timeout_seconds=120,     # Can wait longer for recovery
                    slow_call_threshold_ms=5000  # 5 seconds acceptable
                )
            else:
                config = CircuitBreakerConfig()  # Default config
            
            self.circuit_breakers[service_name] = SwiggyCircuitBreaker(service_name, config)
        
        return self.circuit_breakers[service_name]
    
    async def discover_and_call_service(self, service_name: str, endpoint: str, 
                                      data: Dict = None, region: str = "mumbai") -> Dict:
        """Discover service and make call through circuit breaker"""
        
        circuit_breaker = self.get_or_create_circuit_breaker(service_name)
        
        try:
            # Define the actual service call function
            async def make_service_call():
                # Service discovery to get endpoint
                service_url = await self._discover_service_endpoint(service_name, region)
                if not service_url:
                    raise ServiceDiscoveryError(f"No healthy instances found for {service_name}")
                
                # Make HTTP call
                async with aiohttp.ClientSession() as session:
                    url = f"{service_url}{endpoint}"
                    
                    # Add Swiggy-specific headers
                    headers = {
                        'X-Swiggy-Service': service_name,
                        'X-Swiggy-Region': region,
                        'X-Swiggy-Trace-Id': self._generate_trace_id(),
                        'Content-Type': 'application/json'
                    }
                    
                    if data:
                        async with session.post(url, json=data, headers=headers, timeout=5) as response:
                            if response.status == 200:
                                return await response.json()
                            else:
                                raise ServiceCallError(f"HTTP {response.status}: {await response.text()}")
                    else:
                        async with session.get(url, headers=headers, timeout=5) as response:
                            if response.status == 200:
                                return await response.json()
                            else:
                                raise ServiceCallError(f"HTTP {response.status}: {await response.text()}")
            
            # Execute call through circuit breaker
            return circuit_breaker.call(lambda: asyncio.run(make_service_call()))
            
        except CircuitBreakerOpenError:
            # Try fallback service if available
            return await self._try_fallback_service(service_name, endpoint, data, region)
    
    async def _discover_service_endpoint(self, service_name: str, region: str) -> Optional[str]:
        """Discover healthy service endpoint"""
        # Simplified service discovery - in production this would be more sophisticated
        service_endpoints = {
            'payment-service': {
                'mumbai': ['http://payment-1.mumbai.swiggy.com:8080', 'http://payment-2.mumbai.swiggy.com:8080'],
                'delhi': ['http://payment-1.delhi.swiggy.com:8080'],
                'bangalore': ['http://payment-1.bangalore.swiggy.com:8080']
            },
            'restaurant-service': {
                'mumbai': ['http://restaurant-1.mumbai.swiggy.com:8080', 'http://restaurant-2.mumbai.swiggy.com:8080'],
                'delhi': ['http://restaurant-1.delhi.swiggy.com:8080'],
                'bangalore': ['http://restaurant-1.bangalore.swiggy.com:8080']
            },
            'delivery-assignment': {
                'mumbai': ['http://delivery-1.mumbai.swiggy.com:8080'],
                'delhi': ['http://delivery-1.delhi.swiggy.com:8080'],
                'bangalore': ['http://delivery-1.bangalore.swiggy.com:8080']
            }
        }
        
        endpoints = service_endpoints.get(service_name, {}).get(region, [])
        
        # Return first available endpoint (simplified)
        for endpoint in endpoints:
            # In production, this would include health checking
            return endpoint
        
        return None
    
    async def _try_fallback_service(self, original_service: str, endpoint: str, 
                                  data: Dict, region: str) -> Dict:
        """Try fallback services when primary service is down"""
        fallbacks = self.fallback_services.get(original_service, [])
        
        for fallback_service in fallbacks:
            try:
                print(f"Trying fallback service: {fallback_service}")
                return await self.discover_and_call_service(fallback_service, endpoint, data, region)
            except Exception as e:
                print(f"Fallback service {fallback_service} also failed: {e}")
                continue
        
        # All fallbacks failed
        raise AllServicesDownError(f"All services down for {original_service}")
    
    def _generate_trace_id(self) -> str:
        """Generate trace ID for request tracking"""
        import uuid
        return str(uuid.uuid4())
    
    def get_all_circuit_breaker_metrics(self) -> Dict:
        """Get metrics for all circuit breakers"""
        metrics = {}
        for service_name, circuit_breaker in self.circuit_breakers.items():
            metrics[service_name] = circuit_breaker.get_metrics()
        return metrics

class ServiceDiscoveryError(Exception):
    pass

class ServiceCallError(Exception):
    pass

class AllServicesDownError(Exception):
    pass

# Usage example for Swiggy order processing
async def swiggy_order_processing_example():
    """Example of order processing with circuit breaker protection"""
    
    discovery = SwiggyServiceDiscoveryWithCircuitBreaker()
    
    # Simulate order processing flow
    order_data = {
        'order_id': 'ORD123456',
        'restaurant_id': 'REST789',
        'user_id': 'USER456',
        'items': [
            {'name': 'Butter Chicken', 'quantity': 1, 'price': 350},
            {'name': 'Naan', 'quantity': 2, 'price': 50}
        ],
        'total_amount': 450,
        'region': 'mumbai'
    }
    
    try:
        # Step 1: Validate restaurant availability
        restaurant_response = await discovery.discover_and_call_service(
            service_name='restaurant-service',
            endpoint='/validate',
            data={'restaurant_id': order_data['restaurant_id']},
            region='mumbai'
        )
        print(f"Restaurant validation: {restaurant_response}")
        
        # Step 2: Process payment
        payment_response = await discovery.discover_and_call_service(
            service_name='payment-service',
            endpoint='/charge',
            data={
                'user_id': order_data['user_id'],
                'amount': order_data['total_amount'],
                'currency': 'INR'
            },
            region='mumbai'
        )
        print(f"Payment processing: {payment_response}")
        
        # Step 3: Assign delivery partner
        delivery_response = await discovery.discover_and_call_service(
            service_name='delivery-assignment',
            endpoint='/assign',
            data={
                'order_id': order_data['order_id'],
                'restaurant_id': order_data['restaurant_id'],
                'delivery_location': order_data.get('delivery_address')
            },
            region='mumbai'
        )
        print(f"Delivery assignment: {delivery_response}")
        
        # Step 4: Send notification
        notification_response = await discovery.discover_and_call_service(
            service_name='notification-service',
            endpoint='/send',
            data={
                'user_id': order_data['user_id'],
                'message': f"Order {order_data['order_id']} confirmed!",
                'type': 'sms'
            },
            region='mumbai'
        )
        print(f"Notification sent: {notification_response}")
        
        print("✅ Order processed successfully!")
        
    except Exception as e:
        print(f"❌ Order processing failed: {e}")
    
    # Print circuit breaker metrics
    print("\n📊 Circuit Breaker Metrics:")
    metrics = discovery.get_all_circuit_breaker_metrics()
    for service, metric in metrics.items():
        print(f"{service}:")
        print(f"  State: {metric['state']}")
        print(f"  Success Rate: {metric['success_rate']:.2%}")
        print(f"  Avg Response Time: {metric['avg_response_time_ms']:.0f}ms")
        print(f"  Total Calls: {metric['total_calls']}")
        print(f"  Total Failures: {metric['total_failures']}")

# Run the example
if __name__ == "__main__":
    asyncio.run(swiggy_order_processing_example())
```

---

**Part 2 Summary (60 Minutes Complete)**

Part 2 mein humne cover kiya:

1. **PhonePe's Multi-Region Discovery**: Regulatory compliance aur regional optimization ke saath
2. **Paytm's Service Mesh**: Istio-based sophisticated traffic management  
3. **Kubernetes Native Discovery**: Production-grade configuration aur real-time monitoring
4. **Circuit Breaker Integration**: Automatic failover aur fallback mechanisms

**Up Next in Part 3**: Service mesh deep dive, observability patterns, troubleshooting strategies, aur real production war stories!

---

*Word Count: Part 2 = 7,156 words*
*Running Total: 14,403 / 20,000+ words*
*Time: 60-120 minutes covered*
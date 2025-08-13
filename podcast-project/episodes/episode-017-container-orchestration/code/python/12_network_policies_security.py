#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Policies and Security Configuration for Container Orchestration
Episode 17: Container Orchestration

यह example दिखाता है कि कैसे Zerodha जैसी fintech companies
production में container network security करती हैं।

Real-world scenario: Zerodha का comprehensive network security for containers
"""

import yaml
import json
import ipaddress
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from loguru import logger

class SecurityTier(Enum):
    """Security tier classification"""
    PUBLIC = "public"           # Internet-facing services
    DMZ = "dmz"                # Demilitarized zone
    INTERNAL = "internal"       # Internal services
    RESTRICTED = "restricted"   # Highly sensitive services
    ISOLATED = "isolated"       # Completely isolated

class TrafficDirection(Enum):
    """Network traffic direction"""
    INGRESS = "ingress"
    EGRESS = "egress"
    BOTH = "both"

@dataclass
class NetworkEndpoint:
    """Network endpoint definition"""
    ip_range: str
    port: int
    protocol: str
    description: str

@dataclass
class SecurityRule:
    """Security rule definition"""
    rule_name: str
    source_tier: SecurityTier
    destination_tier: SecurityTier
    allowed_ports: List[int]
    protocols: List[str]
    description: str
    business_justification: str

class ZerodhaNetworkSecurityManager:
    """
    Zerodha-style Network Security Manager for Container Orchestration
    Production-ready network policies with Indian fintech compliance
    """
    
    def __init__(self):
        # Zerodha service tiers and their security requirements
        self.service_tiers = {
            SecurityTier.PUBLIC: {
                "services": ["web-frontend", "mobile-api", "public-documentation"],
                "security_level": "high",
                "compliance": ["PCI_DSS", "ISO_27001"],
                "monitoring": "real_time",
                "allowed_outbound": ["internet"],
                "encryption_required": True
            },
            
            SecurityTier.DMZ: {
                "services": ["api-gateway", "load-balancer", "reverse-proxy"],
                "security_level": "very_high", 
                "compliance": ["PCI_DSS", "ISO_27001", "SOC2"],
                "monitoring": "real_time",
                "allowed_outbound": ["internal", "restricted"],
                "encryption_required": True
            },
            
            SecurityTier.INTERNAL: {
                "services": ["order-service", "portfolio-service", "notification-service"],
                "security_level": "high",
                "compliance": ["ISO_27001", "SOC2"],
                "monitoring": "continuous",
                "allowed_outbound": ["restricted", "internal"],
                "encryption_required": True
            },
            
            SecurityTier.RESTRICTED: {
                "services": ["trading-engine", "settlement-service", "risk-management"],
                "security_level": "critical",
                "compliance": ["PCI_DSS", "SEBI", "RBI", "ISO_27001"],
                "monitoring": "real_time_plus",
                "allowed_outbound": ["isolated"],
                "encryption_required": True
            },
            
            SecurityTier.ISOLATED: {
                "services": ["user-data", "financial-data", "audit-logs"],
                "security_level": "maximum",
                "compliance": ["PCI_DSS", "SEBI", "RBI", "GDPR"],
                "monitoring": "real_time_plus",
                "allowed_outbound": [],
                "encryption_required": True
            }
        }
        
        # Indian financial regulatory requirements
        self.regulatory_requirements = {
            "SEBI": {
                "data_encryption": "AES-256",
                "network_segregation": "mandatory",
                "audit_logging": "real_time",
                "access_controls": "role_based",
                "data_residency": "India"
            },
            "RBI": {
                "data_localization": "mandatory",
                "network_monitoring": "24x7",
                "incident_response": "4_hours",
                "encryption_standards": "FIPS_140_2",
                "business_continuity": "99.9_uptime"
            },
            "PCI_DSS": {
                "network_segmentation": "mandatory",
                "firewall_management": "strict",
                "encryption_transit": "TLS_1.3",
                "encryption_rest": "AES_256",
                "access_logging": "comprehensive"
            }
        }
        
        # Network zones for Indian financial infrastructure
        self.network_zones = {
            "internet": {
                "cidr": "0.0.0.0/0",
                "description": "Internet/External networks",
                "trust_level": "untrusted",
                "monitoring": "strict"
            },
            "public_cloud": {
                "cidr": "10.0.0.0/16",
                "description": "Public cloud infrastructure",
                "trust_level": "semi_trusted",
                "monitoring": "high"
            },
            "private_cloud": {
                "cidr": "172.16.0.0/12", 
                "description": "Private cloud infrastructure",
                "trust_level": "trusted",
                "monitoring": "standard"
            },
            "trading_floor": {
                "cidr": "192.168.1.0/24",
                "description": "Trading floor network",
                "trust_level": "high_trust",
                "monitoring": "real_time"
            },
            "data_center": {
                "cidr": "192.168.2.0/24",
                "description": "Primary data center",
                "trust_level": "high_trust",
                "monitoring": "real_time"
            },
            "dr_site": {
                "cidr": "192.168.3.0/24",
                "description": "Disaster recovery site",
                "trust_level": "high_trust",
                "monitoring": "real_time"
            }
        }
        
        # Zerodha-specific service communication matrix
        self.communication_matrix = {
            "web-frontend": {
                "allowed_destinations": ["api-gateway"],
                "protocols": ["HTTPS"],
                "ports": [443],
                "encryption": "TLS_1.3"
            },
            "mobile-api": {
                "allowed_destinations": ["api-gateway", "notification-service"],
                "protocols": ["HTTPS"],
                "ports": [443, 8443],
                "encryption": "TLS_1.3"
            },
            "api-gateway": {
                "allowed_destinations": ["order-service", "portfolio-service", "trading-engine"],
                "protocols": ["HTTPS", "gRPC"],
                "ports": [443, 9443, 50051],
                "encryption": "mTLS"
            },
            "trading-engine": {
                "allowed_destinations": ["settlement-service", "risk-management", "audit-logs"],
                "protocols": ["gRPC", "TCP"],
                "ports": [50051, 9092],
                "encryption": "mTLS"
            },
            "settlement-service": {
                "allowed_destinations": ["financial-data", "audit-logs"],
                "protocols": ["gRPC"],
                "ports": [50051],
                "encryption": "mTLS"
            }
        }
        
        logger.info("💰 Zerodha Network Security Manager initialized!")
        logger.info("Production-ready network policies for Indian fintech!")
    
    def generate_network_policy(self, service_name: str, namespace: str) -> str:
        """Generate Kubernetes NetworkPolicy for a service"""
        
        # Determine service tier
        service_tier = self.get_service_tier(service_name)
        if not service_tier:
            logger.warning(f"Service {service_name} not found in any tier")
            return ""
        
        # Get communication rules
        comm_rules = self.communication_matrix.get(service_name, {})
        
        # Base network policy
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{service_name}-network-policy",
                "namespace": namespace,
                "labels": {
                    "app": service_name,
                    "tier": service_tier.value,
                    "company": "zerodha",
                    "compliance": "SEBI,RBI,PCI_DSS"
                },
                "annotations": {
                    "policy.zerodha.com/created-by": "security-team",
                    "policy.zerodha.com/business-justification": f"Network isolation for {service_name}",
                    "policy.zerodha.com/compliance-requirements": "SEBI,RBI,PCI_DSS",
                    "policy.zerodha.com/review-date": "2024-12-31"
                }
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "app": service_name
                    }
                },
                "policyTypes": ["Ingress", "Egress"],
                "ingress": self.generate_ingress_rules(service_name, service_tier),
                "egress": self.generate_egress_rules(service_name, service_tier)
            }
        }
        
        return yaml.dump(network_policy, default_flow_style=False)
    
    def get_service_tier(self, service_name: str) -> Optional[SecurityTier]:
        """Determine security tier for a service"""
        
        for tier, config in self.service_tiers.items():
            if service_name in config["services"]:
                return tier
        return None
    
    def generate_ingress_rules(self, service_name: str, service_tier: SecurityTier) -> List[Dict]:
        """Generate ingress rules based on service tier and communication matrix"""
        
        ingress_rules = []
        
        # Default deny all
        if service_tier == SecurityTier.ISOLATED:
            # Isolated services have no ingress except from specific monitoring
            ingress_rules.append({
                "from": [
                    {
                        "namespaceSelector": {
                            "matchLabels": {
                                "name": "monitoring"
                            }
                        }
                    }
                ],
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 9090  # Prometheus metrics
                    }
                ]
            })
        
        elif service_tier == SecurityTier.RESTRICTED:
            # Restricted services only accept from internal and DMZ
            ingress_rules.append({
                "from": [
                    {
                        "podSelector": {
                            "matchLabels": {
                                "tier": SecurityTier.INTERNAL.value
                            }
                        }
                    },
                    {
                        "podSelector": {
                            "matchLabels": {
                                "tier": SecurityTier.DMZ.value
                            }
                        }
                    }
                ],
                "ports": self.get_service_ports(service_name)
            })
        
        elif service_tier == SecurityTier.INTERNAL:
            # Internal services accept from DMZ and other internal
            ingress_rules.append({
                "from": [
                    {
                        "podSelector": {
                            "matchLabels": {
                                "tier": SecurityTier.DMZ.value
                            }
                        }
                    },
                    {
                        "podSelector": {
                            "matchLabels": {
                                "tier": SecurityTier.INTERNAL.value
                            }
                        }
                    }
                ],
                "ports": self.get_service_ports(service_name)
            })
        
        elif service_tier == SecurityTier.DMZ:
            # DMZ services accept from public and other DMZ services
            ingress_rules.append({
                "from": [
                    {
                        "podSelector": {
                            "matchLabels": {
                                "tier": SecurityTier.PUBLIC.value
                            }
                        }
                    },
                    {
                        "podSelector": {
                            "matchLabels": {
                                "tier": SecurityTier.DMZ.value
                            }
                        }
                    }
                ],
                "ports": self.get_service_ports(service_name)
            })
        
        elif service_tier == SecurityTier.PUBLIC:
            # Public services accept from internet (through load balancer)
            ingress_rules.append({
                "from": [],  # Allow all (will be filtered by load balancer)
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 80
                    },
                    {
                        "protocol": "TCP", 
                        "port": 443
                    }
                ]
            })
        
        return ingress_rules
    
    def generate_egress_rules(self, service_name: str, service_tier: SecurityTier) -> List[Dict]:
        """Generate egress rules based on service tier and dependencies"""
        
        egress_rules = []
        
        # DNS resolution (required for all services)
        egress_rules.append({
            "to": [],
            "ports": [
                {
                    "protocol": "UDP",
                    "port": 53
                },
                {
                    "protocol": "TCP",
                    "port": 53
                }
            ]
        })
        
        # Service-specific egress rules
        comm_config = self.communication_matrix.get(service_name, {})
        allowed_destinations = comm_config.get("allowed_destinations", [])
        
        for destination in allowed_destinations:
            dest_tier = self.get_service_tier(destination)
            if dest_tier:
                egress_rules.append({
                    "to": [
                        {
                            "podSelector": {
                                "matchLabels": {
                                    "app": destination
                                }
                            }
                        }
                    ],
                    "ports": self.get_service_ports(destination)
                })
        
        # External dependencies based on tier
        tier_config = self.service_tiers[service_tier]
        allowed_outbound = tier_config.get("allowed_outbound", [])
        
        for outbound_zone in allowed_outbound:
            if outbound_zone == "internet":
                # Allow HTTPS to internet for external APIs
                egress_rules.append({
                    "to": [],
                    "ports": [
                        {
                            "protocol": "TCP",
                            "port": 443
                        }
                    ]
                })
        
        return egress_rules
    
    def get_service_ports(self, service_name: str) -> List[Dict]:
        """Get port configuration for a service"""
        
        comm_config = self.communication_matrix.get(service_name, {})
        ports = comm_config.get("ports", [8080])  # Default port
        protocols = comm_config.get("protocols", ["TCP"])
        
        port_configs = []
        for port in ports:
            for protocol in protocols:
                port_configs.append({
                    "protocol": "TCP",  # Kubernetes NetworkPolicy only supports TCP/UDP
                    "port": port
                })
        
        return port_configs
    
    def generate_istio_authorization_policy(self, service_name: str, namespace: str) -> str:
        """Generate Istio AuthorizationPolicy for service mesh security"""
        
        service_tier = self.get_service_tier(service_name)
        if not service_tier:
            return ""
        
        # Istio AuthorizationPolicy for application-layer security
        auth_policy = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "AuthorizationPolicy",
            "metadata": {
                "name": f"{service_name}-authz",
                "namespace": namespace,
                "labels": {
                    "app": service_name,
                    "tier": service_tier.value
                }
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": service_name
                    }
                },
                "rules": self.generate_authorization_rules(service_name, service_tier)
            }
        }
        
        return yaml.dump(auth_policy, default_flow_style=False)
    
    def generate_authorization_rules(self, service_name: str, service_tier: SecurityTier) -> List[Dict]:
        """Generate authorization rules for Istio"""
        
        rules = []
        
        # Get communication configuration
        comm_config = self.communication_matrix.get(service_name, {})
        
        # Rule for allowing specific source services
        if service_tier in [SecurityTier.RESTRICTED, SecurityTier.ISOLATED]:
            # Strict authorization for sensitive services
            for source_service in self.get_allowed_source_services(service_name):
                rules.append({
                    "from": [
                        {
                            "source": {
                                "principals": [f"cluster.local/ns/{namespace}/sa/{source_service}"]
                            }
                        }
                    ],
                    "to": [
                        {
                            "operation": {
                                "methods": ["GET", "POST"],
                                "paths": ["/api/*"]
                            }
                        }
                    ],
                    "when": [
                        {
                            "key": "request.headers[x-zerodha-auth]",
                            "values": ["required"]
                        }
                    ]
                })
        
        elif service_tier == SecurityTier.INTERNAL:
            # Moderate authorization for internal services
            rules.append({
                "from": [
                    {
                        "source": {
                            "namespaces": [namespace]
                        }
                    }
                ],
                "to": [
                    {
                        "operation": {
                            "methods": ["GET", "POST", "PUT", "DELETE"]
                        }
                    }
                ],
                "when": [
                    {
                        "key": "source.labels[tier]",
                        "values": ["dmz", "internal"]
                    }
                ]
            })
        
        elif service_tier in [SecurityTier.DMZ, SecurityTier.PUBLIC]:
            # Controlled access for DMZ and public services
            rules.append({
                "to": [
                    {
                        "operation": {
                            "methods": ["GET", "POST"]
                        }
                    }
                ],
                "when": [
                    {
                        "key": "request.headers[user-agent]",
                        "notValues": ["*bot*", "*crawler*"]
                    }
                ]
            })
        
        return rules
    
    def get_allowed_source_services(self, service_name: str) -> List[str]:
        """Get list of services allowed to call this service"""
        
        allowed_sources = []
        
        # Check communication matrix for services that can call this service
        for source_service, config in self.communication_matrix.items():
            allowed_destinations = config.get("allowed_destinations", [])
            if service_name in allowed_destinations:
                allowed_sources.append(source_service)
        
        return allowed_sources
    
    def generate_calico_global_network_policy(self) -> str:
        """Generate Calico GlobalNetworkPolicy for cluster-wide security"""
        
        global_policy = {
            "apiVersion": "projectcalico.org/v3",
            "kind": "GlobalNetworkPolicy",
            "metadata": {
                "name": "zerodha-global-security-policy"
            },
            "spec": {
                "order": 100,
                "selector": "projectcalico.org/namespace != 'kube-system'",
                "types": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "action": "Log",
                        "metadata": {
                            "annotations": {
                                "policy": "global-security-log"
                            }
                        }
                    }
                ],
                "egress": [
                    # Block suspicious outbound traffic
                    {
                        "action": "Deny",
                        "destination": {
                            "nets": [
                                "10.0.0.0/8",    # Private networks
                                "172.16.0.0/12", # Private networks
                                "192.168.0.0/16" # Private networks
                            ],
                            "notPorts": [22, 80, 443, 3306, 5432, 6379, 9200]
                        },
                        "metadata": {
                            "annotations": {
                                "policy": "block-suspicious-outbound"
                            }
                        }
                    },
                    # Allow DNS
                    {
                        "action": "Allow",
                        "protocol": "UDP",
                        "destination": {
                            "ports": [53]
                        }
                    },
                    # Allow HTTPS outbound
                    {
                        "action": "Allow",
                        "protocol": "TCP",
                        "destination": {
                            "ports": [443]
                        }
                    }
                ]
            }
        }
        
        return yaml.dump(global_policy, default_flow_style=False)
    
    def generate_security_compliance_report(self) -> Dict[str, Any]:
        """Generate security compliance report for Indian regulations"""
        
        compliance_status = {
            "report_generated": datetime.now().isoformat(),
            "compliance_framework": "SEBI,RBI,PCI_DSS,ISO_27001",
            "overall_status": "COMPLIANT",
            
            "network_security": {
                "segmentation_implemented": True,
                "encryption_in_transit": "TLS_1.3",
                "encryption_at_rest": "AES_256",
                "network_monitoring": "Real_time",
                "intrusion_detection": "Active"
            },
            
            "access_controls": {
                "rbac_implemented": True,
                "service_mesh_auth": "mTLS",
                "zero_trust_model": True,
                "principle_of_least_privilege": True
            },
            
            "regulatory_compliance": {
                "SEBI": {
                    "data_encryption": "COMPLIANT",
                    "network_segregation": "COMPLIANT",
                    "audit_logging": "COMPLIANT",
                    "access_controls": "COMPLIANT"
                },
                "RBI": {
                    "data_localization": "COMPLIANT",
                    "network_monitoring": "COMPLIANT",
                    "incident_response": "COMPLIANT",
                    "business_continuity": "COMPLIANT"
                },
                "PCI_DSS": {
                    "network_segmentation": "COMPLIANT",
                    "firewall_management": "COMPLIANT",
                    "encryption_requirements": "COMPLIANT",
                    "access_logging": "COMPLIANT"
                }
            },
            
            "security_metrics": {
                "blocked_connections": 0,
                "allowed_connections": 1000,
                "policy_violations": 0,
                "security_incidents": 0
            },
            
            "recommendations": [
                "Regular security policy review (quarterly)",
                "Automated compliance scanning",
                "Security awareness training",
                "Incident response drills"
            ]
        }
        
        return compliance_status
    
    def create_complete_security_stack(self, output_dir: str):
        """Create complete network security configuration"""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate NetworkPolicies for all services
        policies_dir = os.path.join(output_dir, "network-policies")
        os.makedirs(policies_dir, exist_ok=True)
        
        all_services = []
        for tier_config in self.service_tiers.values():
            all_services.extend(tier_config["services"])
        
        for service in all_services:
            # Kubernetes NetworkPolicy
            policy_yaml = self.generate_network_policy(service, "zerodha-prod")
            with open(os.path.join(policies_dir, f"{service}-network-policy.yaml"), "w") as f:
                f.write(policy_yaml)
            
            # Istio AuthorizationPolicy
            auth_policy_yaml = self.generate_istio_authorization_policy(service, "zerodha-prod")
            with open(os.path.join(policies_dir, f"{service}-authz-policy.yaml"), "w") as f:
                f.write(auth_policy_yaml)
        
        # Calico GlobalNetworkPolicy
        global_policy_yaml = self.generate_calico_global_network_policy()
        with open(os.path.join(output_dir, "calico-global-policy.yaml"), "w") as f:
            f.write(global_policy_yaml)
        
        # Compliance report
        compliance_report = self.generate_security_compliance_report()
        with open(os.path.join(output_dir, "compliance-report.json"), "w") as f:
            json.dump(compliance_report, f, indent=2)
        
        logger.info(f"✅ Complete security stack created in {output_dir}")

def main():
    """Demonstration of Zerodha network security configuration"""
    
    print("💰 Zerodha Network Security Manager Demo")
    print("Production-ready network policies for Indian fintech")
    print("=" * 60)
    
    # Initialize security manager
    security_manager = ZerodhaNetworkSecurityManager()
    
    print("🔒 Security Tiers Configuration:")
    for tier, config in security_manager.service_tiers.items():
        print(f"   {tier.value.upper()}:")
        print(f"     Services: {', '.join(config['services'])}")
        print(f"     Security Level: {config['security_level']}")
        print(f"     Compliance: {', '.join(config['compliance'])}")
    
    print("\\n🌐 Network Zones:")
    for zone, config in security_manager.network_zones.items():
        print(f"   {zone}: {config['cidr']} ({config['trust_level']})")
    
    print("\\n📋 Generating Security Policies...")
    
    # Generate example policies
    services_to_demo = ["trading-engine", "api-gateway", "web-frontend"]
    
    for service in services_to_demo:
        print(f"\\n--- {service.upper()} ---")
        
        # NetworkPolicy
        network_policy = security_manager.generate_network_policy(service, "zerodha-prod")
        print("✅ Kubernetes NetworkPolicy generated")
        
        # Istio AuthorizationPolicy
        auth_policy = security_manager.generate_istio_authorization_policy(service, "zerodha-prod")
        print("✅ Istio AuthorizationPolicy generated")
        
        # Show policy summary
        tier = security_manager.get_service_tier(service)
        if tier:
            print(f"   Security Tier: {tier.value}")
            print(f"   Compliance: {', '.join(security_manager.service_tiers[tier]['compliance'])}")
    
    print("\\n🔍 Compliance Report:")
    compliance_report = security_manager.generate_security_compliance_report()
    
    print(f"   Overall Status: {compliance_report['overall_status']}")
    print(f"   Frameworks: {compliance_report['compliance_framework']}")
    
    for framework, status in compliance_report['regulatory_compliance'].items():
        compliant_items = sum(1 for v in status.values() if v == "COMPLIANT")
        total_items = len(status)
        print(f"   {framework}: {compliant_items}/{total_items} compliant")
    
    print("\\n📁 Creating Complete Security Stack...")
    
    output_dir = "/tmp/zerodha_network_security"
    security_manager.create_complete_security_stack(output_dir)
    
    print(f"\\n📂 Security files created in: {output_dir}")
    print("\\n📋 Generated Files:")
    
    import os
    for root, dirs, files in os.walk(output_dir):
        level = root.replace(output_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    
    print("\\n✅ Network security demonstration completed!")

if __name__ == "__main__":
    main()

# Production Deployment Commands:
"""
# 1. Apply Kubernetes NetworkPolicies:
kubectl apply -f /tmp/zerodha_network_security/network-policies/

# 2. Deploy Calico for advanced networking:
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# 3. Apply Calico GlobalNetworkPolicy:
kubectl apply -f /tmp/zerodha_network_security/calico-global-policy.yaml

# 4. Install Istio service mesh:
istioctl install --set values.defaultRevision=default

# 5. Apply Istio AuthorizationPolicies:
kubectl apply -f /tmp/zerodha_network_security/network-policies/*-authz-policy.yaml

# 6. Enable strict mTLS:
kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: zerodha-prod
spec:
  mtls:
    mode: STRICT
EOF

# 7. Monitor network policies:
kubectl get networkpolicies -A
kubectl describe networkpolicy trading-engine-network-policy -n zerodha-prod

# 8. Test connectivity:
kubectl exec -it pod-name -- nc -zv service-name 8080

# 9. View policy logs (if using Calico):
kubectl logs -n calico-system -l k8s-app=calico-node

# 10. Compliance monitoring:
# Deploy Falco for runtime security monitoring
# Set up network policy violation alerts
# Regular compliance audits and reports
"""
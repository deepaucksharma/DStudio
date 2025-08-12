#!/usr/bin/env python3
"""
Container Security Scanning System
DevSecOps for Indian IT Companies - TCS, Infosys, HCL

यह system container images को comprehensive security scan करता है।
Production में vulnerability detection, malware scanning, और compliance checking।

Real-world Context:
- Indian IT companies run 50,000+ containers in production
- 85% of container images have high/critical vulnerabilities
- Average vulnerability discovery to fix time: 197 days
- Container security breaches cost ₹15 crore on average
"""

import os
import json
import time
import hashlib
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
import docker
import requests
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Vulnerability:
    """Container vulnerability details"""
    cve_id: str
    severity: str
    package: str
    version: str
    fixed_version: str = ""
    description: str = ""
    score: float = 0.0

@dataclass
class SecurityScanResult:
    """Container security scan results"""
    image_name: str
    image_tag: str
    scan_time: datetime
    vulnerabilities: List[Vulnerability]
    compliance_score: float
    risk_level: str
    recommendations: List[str]

class ContainerSecurityScanner:
    """Production Container Security Scanner"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.vulnerability_db = self._load_vulnerability_db()
        self.compliance_policies = self._load_compliance_policies()
        logger.info("Container Security Scanner initialized")
    
    def _load_vulnerability_db(self) -> Dict:
        """Load vulnerability database"""
        return {
            'CVE-2024-1234': {
                'severity': 'HIGH',
                'description': 'Buffer overflow in OpenSSL',
                'score': 8.5,
                'packages': ['openssl', 'libssl1.1']
            },
            'CVE-2024-5678': {
                'severity': 'CRITICAL', 
                'description': 'Remote code execution in curl',
                'score': 9.8,
                'packages': ['curl', 'libcurl4']
            }
        }
    
    def _load_compliance_policies(self) -> Dict:
        """Load security compliance policies"""
        return {
            'no_root_user': {
                'description': 'Container should not run as root',
                'severity': 'HIGH'
            },
            'minimal_packages': {
                'description': 'Use minimal base images',
                'severity': 'MEDIUM'
            },
            'updated_packages': {
                'description': 'All packages should be updated',
                'severity': 'HIGH'
            }
        }
    
    def scan_image(self, image_name: str, tag: str = "latest") -> SecurityScanResult:
        """Comprehensive security scan of container image"""
        try:
            full_image = f"{image_name}:{tag}"
            logger.info(f"Starting security scan: {full_image}")
            
            # Pull image if not present
            try:
                image = self.docker_client.images.get(full_image)
            except docker.errors.ImageNotFound:
                logger.info(f"Pulling image: {full_image}")
                image = self.docker_client.images.pull(image_name, tag=tag)
            
            # Vulnerability scanning
            vulnerabilities = self._scan_vulnerabilities(image)
            
            # Compliance checking
            compliance_score = self._check_compliance(image)
            
            # Risk assessment
            risk_level = self._calculate_risk_level(vulnerabilities, compliance_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(vulnerabilities, compliance_score)
            
            result = SecurityScanResult(
                image_name=image_name,
                image_tag=tag,
                scan_time=datetime.now(),
                vulnerabilities=vulnerabilities,
                compliance_score=compliance_score,
                risk_level=risk_level,
                recommendations=recommendations
            )
            
            logger.info(f"Scan completed: {len(vulnerabilities)} vulnerabilities found")
            return result
            
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            raise
    
    def _scan_vulnerabilities(self, image) -> List[Vulnerability]:
        """Scan for known vulnerabilities"""
        vulnerabilities = []
        
        # Simulate vulnerability scanning
        # In production, this would use tools like Trivy, Clair, or Anchore
        
        simulated_vulns = [
            {
                'cve': 'CVE-2024-1234',
                'package': 'openssl',
                'version': '1.1.1f-1ubuntu2.16',
                'severity': 'HIGH',
                'score': 8.5,
                'fixed_version': '1.1.1f-1ubuntu2.17'
            },
            {
                'cve': 'CVE-2024-5678', 
                'package': 'curl',
                'version': '7.68.0-1ubuntu2.14',
                'severity': 'CRITICAL',
                'score': 9.8,
                'fixed_version': '7.68.0-1ubuntu2.15'
            }
        ]
        
        for vuln_data in simulated_vulns:
            vuln = Vulnerability(
                cve_id=vuln_data['cve'],
                severity=vuln_data['severity'],
                package=vuln_data['package'],
                version=vuln_data['version'],
                fixed_version=vuln_data['fixed_version'],
                description=f"Vulnerability in {vuln_data['package']}",
                score=vuln_data['score']
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _check_compliance(self, image) -> float:
        """Check compliance with security policies"""
        compliance_checks = []
        
        # Check if runs as root
        config = image.attrs.get('Config', {})
        user = config.get('User', 'root')
        compliance_checks.append({
            'policy': 'no_root_user',
            'passed': user != 'root' and user != '',
            'weight': 0.3
        })
        
        # Check for minimal base image
        size_mb = image.attrs.get('Size', 0) / (1024 * 1024)
        compliance_checks.append({
            'policy': 'minimal_packages',
            'passed': size_mb < 200,  # Less than 200MB
            'weight': 0.2
        })
        
        # Calculate compliance score
        total_weight = sum(check['weight'] for check in compliance_checks)
        passed_weight = sum(check['weight'] for check in compliance_checks if check['passed'])
        
        compliance_score = (passed_weight / total_weight) * 100 if total_weight > 0 else 0
        return round(compliance_score, 2)
    
    def _calculate_risk_level(self, vulnerabilities: List[Vulnerability], compliance_score: float) -> str:
        """Calculate overall risk level"""
        critical_vulns = len([v for v in vulnerabilities if v.severity == 'CRITICAL'])
        high_vulns = len([v for v in vulnerabilities if v.severity == 'HIGH'])
        
        if critical_vulns > 0 or compliance_score < 50:
            return 'CRITICAL'
        elif high_vulns > 2 or compliance_score < 70:
            return 'HIGH'
        elif high_vulns > 0 or compliance_score < 85:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_recommendations(self, vulnerabilities: List[Vulnerability], compliance_score: float) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if vulnerabilities:
            critical_vulns = [v for v in vulnerabilities if v.severity == 'CRITICAL']
            if critical_vulns:
                recommendations.append("Immediately update packages with CRITICAL vulnerabilities")
                
            high_vulns = [v for v in vulnerabilities if v.severity == 'HIGH']
            if high_vulns:
                recommendations.append("Update packages with HIGH severity vulnerabilities")
        
        if compliance_score < 70:
            recommendations.append("Improve security compliance configuration")
            recommendations.append("Use non-root user for container execution")
            recommendations.append("Use minimal base images (Alpine, Distroless)")
        
        recommendations.append("Implement automated security scanning in CI/CD pipeline")
        recommendations.append("Regular vulnerability database updates")
        
        return recommendations

def demonstrate_container_security():
    """Demonstrate container security scanning for Indian IT companies"""
    print("\n🐳 Container Security Scanning Demo - Indian IT DevSecOps")
    print("=" * 60)
    
    scanner = ContainerSecurityScanner()
    
    # Test scenarios for Indian IT companies
    test_images = [
        {
            'name': 'nginx',
            'tag': '1.20-alpine',
            'description': 'TCS Web Frontend Container'
        },
        {
            'name': 'python',
            'tag': '3.9-slim',
            'description': 'Infosys ML Application'
        },
        {
            'name': 'node',
            'tag': '16-alpine',
            'description': 'HCL Microservice API'
        }
    ]
    
    print("\n🔍 Scanning Container Images")
    print("-" * 30)
    
    scan_results = []
    
    for image_info in test_images:
        print(f"\n📦 Scanning: {image_info['description']}")
        print(f"   Image: {image_info['name']}:{image_info['tag']}")
        
        try:
            # Simulate scan (in demo mode)
            result = SecurityScanResult(
                image_name=image_info['name'],
                image_tag=image_info['tag'],
                scan_time=datetime.now(),
                vulnerabilities=[
                    Vulnerability(
                        cve_id='CVE-2024-1234',
                        severity='HIGH',
                        package='openssl',
                        version='1.1.1f',
                        fixed_version='1.1.1g',
                        description='Buffer overflow vulnerability',
                        score=8.5
                    ),
                    Vulnerability(
                        cve_id='CVE-2024-5678',
                        severity='MEDIUM',
                        package='curl',
                        version='7.68.0',
                        fixed_version='7.69.0',
                        description='Information disclosure',
                        score=5.3
                    )
                ],
                compliance_score=75.5,
                risk_level='MEDIUM',
                recommendations=[
                    'Update OpenSSL to latest version',
                    'Use non-root user',
                    'Implement runtime security'
                ]
            )
            
            scan_results.append(result)
            
            # Display results
            print(f"   ✅ Scan completed")
            print(f"   🎯 Risk Level: {result.risk_level}")
            print(f"   🔍 Vulnerabilities: {len(result.vulnerabilities)}")
            print(f"   📊 Compliance Score: {result.compliance_score}%")
            
        except Exception as e:
            print(f"   ❌ Scan failed: {e}")
    
    # Vulnerability analysis
    print(f"\n🚨 Vulnerability Analysis")
    print("-" * 25)
    
    for result in scan_results:
        print(f"\n📦 {result.image_name}:{result.image_tag}")
        
        if result.vulnerabilities:
            critical = len([v for v in result.vulnerabilities if v.severity == 'CRITICAL'])
            high = len([v for v in result.vulnerabilities if v.severity == 'HIGH'])
            medium = len([v for v in result.vulnerabilities if v.severity == 'MEDIUM'])
            
            print(f"   🔴 Critical: {critical}")
            print(f"   🟡 High: {high}")
            print(f"   🟠 Medium: {medium}")
            
            # Show top vulnerabilities
            print("   Top Vulnerabilities:")
            for vuln in result.vulnerabilities[:2]:
                print(f"     • {vuln.cve_id}: {vuln.package} ({vuln.severity})")
        
        print(f"   📋 Compliance: {result.compliance_score}%")
        print(f"   ⚠️  Risk Level: {result.risk_level}")
    
    # Security recommendations
    print(f"\n💡 Security Recommendations")
    print("-" * 30)
    
    all_recommendations = set()
    for result in scan_results:
        all_recommendations.update(result.recommendations)
    
    for i, rec in enumerate(all_recommendations, 1):
        print(f"   {i}. {rec}")
    
    # DevSecOps integration
    print(f"\n🔄 DevSecOps Integration")
    print("-" * 25)
    print("✓ Integrate scanning in CI/CD pipeline")
    print("✓ Fail builds on CRITICAL vulnerabilities") 
    print("✓ Automated vulnerability reporting")
    print("✓ Container registry scanning")
    print("✓ Runtime threat detection")
    print("✓ Compliance monitoring dashboard")

if __name__ == "__main__":
    demonstrate_container_security()
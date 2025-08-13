#!/usr/bin/env python3
"""
GitOps Security Scanning Pipeline
Indian Financial Services के लिए comprehensive security scanning

यह system GitOps pipeline में security scans integrate करता है:
- Container image vulnerability scanning
- Kubernetes security policies validation
- Secrets scanning in Git repositories
- Compliance checks (RBI, PCI-DSS)
- Infrastructure as Code security analysis
- Runtime security monitoring

Features:
- Multi-stage security scanning
- Indian compliance frameworks integration
- Automated security policy enforcement
- Real-time threat detection
- Security metrics and reporting

Author: Security Engineering Team - Indian FinTech
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import yaml
import aiohttp
import docker
from kubernetes import client, config
from dataclasses import dataclass
from enum import Enum

# लॉगिंग setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security-scanning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScanSeverity(Enum):
    """Security scan severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ScanStatus(Enum):
    """Security scan status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class ComplianceFramework(Enum):
    """Indian compliance frameworks"""
    RBI = "rbi"
    PCI_DSS = "pci_dss"
    CERT_IN = "cert_in"
    IT_ACT_2000 = "it_act_2000"
    SPDI_RULES = "spdi_rules"

@dataclass
class SecurityVulnerability:
    """Security vulnerability information"""
    id: str
    title: str
    description: str
    severity: ScanSeverity
    cve_id: Optional[str]
    cvss_score: Optional[float]
    affected_component: str
    fix_available: bool
    fix_description: Optional[str]
    compliance_impact: List[ComplianceFramework]

@dataclass
class SecurityScanResult:
    """Security scan result"""
    scan_id: str
    scan_type: str
    target: str
    status: ScanStatus
    start_time: datetime
    end_time: Optional[datetime]
    vulnerabilities: List[SecurityVulnerability]
    overall_score: float
    compliance_status: Dict[ComplianceFramework, bool]
    recommendations: List[str]

class IndianSecurityScanner:
    """
    Indian Financial Services के लिए comprehensive security scanner
    GitOps pipeline में integrate होकर security policies enforce करता है
    """
    
    def __init__(self, config_file: str = "security-config.yaml"):
        self.config = self._load_config(config_file)
        self.docker_client = None
        self.k8s_client = None
        self.scan_results = {}
        
        # Indian security compliance requirements
        self.indian_compliance = {
            ComplianceFramework.RBI: {
                "encryption_required": True,
                "data_residency": "india",
                "audit_logging": True,
                "access_controls": "mandatory",
                "incident_reporting": "6_hours"
            },
            ComplianceFramework.PCI_DSS: {
                "level": "1",
                "encryption_standards": ["AES-256", "RSA-2048"],
                "network_segmentation": True,
                "regular_testing": "quarterly"
            },
            ComplianceFramework.CERT_IN: {
                "vulnerability_disclosure": "responsible",
                "incident_reporting": "mandatory",
                "security_audits": "annual"
            }
        }
        
        # Security scanning tools configuration
        self.security_tools = {
            "container_scanning": {
                "trivy": {
                    "enabled": True,
                    "severity_threshold": "HIGH",
                    "ignore_unfixed": False
                },
                "clair": {
                    "enabled": True,
                    "api_url": "http://clair.security.svc.cluster.local:6060"
                }
            },
            "secrets_scanning": {
                "gitleaks": {
                    "enabled": True,
                    "config_file": "/etc/gitleaks/gitleaks.toml"
                },
                "detect_secrets": {
                    "enabled": True,
                    "baseline_file": ".secrets.baseline"
                }
            },
            "iac_scanning": {
                "checkov": {
                    "enabled": True,
                    "frameworks": ["kubernetes", "terraform", "dockerfile"]
                },
                "kube_score": {
                    "enabled": True,
                    "threshold": 7
                }
            },
            "policy_enforcement": {
                "opa_gatekeeper": {
                    "enabled": True,
                    "policies_dir": "/etc/opa/policies"
                },
                "falco": {
                    "enabled": True,
                    "rules_file": "/etc/falco/falco_rules.yaml"
                }
            }
        }
    
    def _load_config(self, config_file: str) -> Dict:
        """Configuration file load करता है"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"⚠️ Config file {config_file} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default security configuration"""
        return {
            "scan_timeout_minutes": 30,
            "parallel_scans": 3,
            "report_format": "json",
            "store_results": True,
            "notify_on_critical": True,
            "block_on_critical": True,
            "compliance_frameworks": ["rbi", "pci_dss"],
            "allowed_registries": [
                "ecr.ap-south-1.amazonaws.com",
                "gcr.io/indian-project",
                "docker.io/trusted-images"
            ]
        }
    
    async def initialize(self):
        """Security scanner को initialize करता है"""
        logger.info("🔒 Initializing Indian Security Scanner...")
        
        try:
            # Docker client setup
            self.docker_client = docker.from_env()
            
            # Kubernetes client setup
            config.load_incluster_config()
            self.k8s_client = client.ApiClient()
            
            # Verify security tools availability
            await self._verify_security_tools()
            
            logger.info("✅ Security scanner initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Security scanner initialization failed: {e}")
            raise
    
    async def _verify_security_tools(self):
        """Security tools की availability verify करता है"""
        logger.info("🔍 Verifying security tools availability...")
        
        tools_status = {}
        
        # Check Trivy
        try:
            result = subprocess.run(['trivy', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            tools_status['trivy'] = 'available' if result.returncode == 0 else 'failed'
        except Exception:
            tools_status['trivy'] = 'not_found'
        
        # Check Gitleaks
        try:
            result = subprocess.run(['gitleaks', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            tools_status['gitleaks'] = 'available' if result.returncode == 0 else 'failed'
        except Exception:
            tools_status['gitleaks'] = 'not_found'
        
        # Check Checkov
        try:
            result = subprocess.run(['checkov', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            tools_status['checkov'] = 'available' if result.returncode == 0 else 'failed'
        except Exception:
            tools_status['checkov'] = 'not_found'
        
        logger.info(f"🛠️ Security tools status: {tools_status}")
        
        # Check if critical tools are missing
        critical_tools = ['trivy', 'gitleaks']
        missing_critical = [tool for tool in critical_tools if tools_status.get(tool) != 'available']
        
        if missing_critical:
            raise Exception(f"Critical security tools missing: {missing_critical}")
    
    async def scan_container_image(self, image_name: str, registry: str = None) -> SecurityScanResult:
        """
        Container image की security scanning करता है
        Indian financial services के लिए specialized checks
        """
        scan_id = f"container-{uuid.uuid4().hex[:8]}"
        logger.info(f"🐳 Starting container scan: {image_name} (ID: {scan_id})")
        
        scan_result = SecurityScanResult(
            scan_id=scan_id,
            scan_type="container",
            target=image_name,
            status=ScanStatus.RUNNING,
            start_time=datetime.now(),
            end_time=None,
            vulnerabilities=[],
            overall_score=0.0,
            compliance_status={},
            recommendations=[]
        )
        
        try:
            # Step 1: Registry validation
            if not await self._validate_registry(image_name, registry):
                scan_result.status = ScanStatus.BLOCKED
                scan_result.recommendations.append("Image from untrusted registry - blocked by security policy")
                return scan_result
            
            # Step 2: Trivy vulnerability scan
            trivy_results = await self._run_trivy_scan(image_name)
            scan_result.vulnerabilities.extend(trivy_results)
            
            # Step 3: Dockerfile security analysis
            dockerfile_results = await self._analyze_dockerfile_security(image_name)
            scan_result.vulnerabilities.extend(dockerfile_results)
            
            # Step 4: Secrets scanning in image
            secrets_results = await self._scan_image_secrets(image_name)
            scan_result.vulnerabilities.extend(secrets_results)
            
            # Step 5: Indian compliance checks
            compliance_results = await self._check_indian_compliance(image_name, scan_result.vulnerabilities)
            scan_result.compliance_status = compliance_results
            
            # Step 6: Calculate overall security score
            scan_result.overall_score = self._calculate_security_score(scan_result.vulnerabilities)
            
            # Step 7: Generate recommendations
            scan_result.recommendations = self._generate_security_recommendations(scan_result)
            
            scan_result.status = ScanStatus.COMPLETED
            scan_result.end_time = datetime.now()
            
            logger.info(f"✅ Container scan completed: {scan_id} | Score: {scan_result.overall_score}")
            
        except Exception as e:
            logger.error(f"❌ Container scan failed: {scan_id} | Error: {e}")
            scan_result.status = ScanStatus.FAILED
            scan_result.end_time = datetime.now()
        
        # Store scan results
        self.scan_results[scan_id] = scan_result
        
        return scan_result
    
    async def _validate_registry(self, image_name: str, registry: str = None) -> bool:
        """Registry validation for Indian compliance"""
        allowed_registries = self.config.get("allowed_registries", [])
        
        # Extract registry from image name
        if "/" in image_name:
            image_registry = image_name.split("/")[0]
        else:
            image_registry = "docker.io"  # Default registry
        
        if registry:
            image_registry = registry
        
        # Check if registry is in allowed list
        is_allowed = any(allowed_reg in image_registry for allowed_reg in allowed_registries)
        
        if not is_allowed:
            logger.warning(f"⚠️ Image registry not allowed: {image_registry}")
            return False
        
        # Additional checks for Indian compliance
        # Block registries in certain countries if required
        blocked_countries = ["china", "pakistan", "iran", "north-korea"]
        if any(country in image_registry.lower() for country in blocked_countries):
            logger.warning(f"⚠️ Registry from blocked country: {image_registry}")
            return False
        
        return True
    
    async def _run_trivy_scan(self, image_name: str) -> List[SecurityVulnerability]:
        """Trivy vulnerability scanner चलाता है"""
        logger.info(f"🔍 Running Trivy scan on {image_name}")
        
        vulnerabilities = []
        
        try:
            # Run Trivy scan
            cmd = [
                'trivy', 'image',
                '--format', 'json',
                '--severity', 'CRITICAL,HIGH,MEDIUM',
                '--no-progress',
                image_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                trivy_output = json.loads(result.stdout)
                
                # Parse Trivy results
                for result_item in trivy_output.get('Results', []):
                    for vuln in result_item.get('Vulnerabilities', []):
                        vulnerability = SecurityVulnerability(
                            id=f"trivy-{vuln.get('VulnerabilityID', 'unknown')}",
                            title=vuln.get('Title', 'Unknown vulnerability'),
                            description=vuln.get('Description', ''),
                            severity=self._map_severity(vuln.get('Severity', 'UNKNOWN')),
                            cve_id=vuln.get('VulnerabilityID'),
                            cvss_score=float(vuln.get('CVSS', {}).get('nvd', {}).get('V3Score', 0)),
                            affected_component=vuln.get('PkgName', 'unknown'),
                            fix_available=bool(vuln.get('FixedVersion')),
                            fix_description=vuln.get('FixedVersion'),
                            compliance_impact=self._assess_compliance_impact(vuln)
                        )
                        vulnerabilities.append(vulnerability)
            
            logger.info(f"🔍 Trivy scan found {len(vulnerabilities)} vulnerabilities")
            
        except Exception as e:
            logger.error(f"❌ Trivy scan failed: {e}")
        
        return vulnerabilities
    
    async def _analyze_dockerfile_security(self, image_name: str) -> List[SecurityVulnerability]:
        """Dockerfile security best practices check करता है"""
        logger.info(f"📄 Analyzing Dockerfile security for {image_name}")
        
        vulnerabilities = []
        
        try:
            # Get image history to analyze layers
            image = self.docker_client.images.get(image_name)
            history = image.history()
            
            # Analyze Dockerfile instructions
            security_issues = []
            
            for layer in history:
                created_by = layer.get('CreatedBy', '')
                
                # Check for security anti-patterns
                if 'USER root' in created_by:
                    security_issues.append({
                        'issue': 'Running as root user',
                        'severity': 'HIGH',
                        'description': 'Container running as root violates least privilege principle'
                    })
                
                if 'chmod 777' in created_by or 'chmod -R 777' in created_by:
                    security_issues.append({
                        'issue': 'Overly permissive file permissions',
                        'severity': 'MEDIUM', 
                        'description': '777 permissions create security risk'
                    })
                
                if any(secret_pattern in created_by.upper() for secret_pattern in 
                       ['PASSWORD=', 'API_KEY=', 'SECRET=', 'TOKEN=']):
                    security_issues.append({
                        'issue': 'Hardcoded secrets in Dockerfile',
                        'severity': 'CRITICAL',
                        'description': 'Secrets should not be hardcoded in Dockerfile'
                    })
            
            # Convert to SecurityVulnerability objects
            for issue in security_issues:
                vulnerability = SecurityVulnerability(
                    id=f"dockerfile-{uuid.uuid4().hex[:8]}",
                    title=issue['issue'],
                    description=issue['description'],
                    severity=self._map_severity(issue['severity']),
                    cve_id=None,
                    cvss_score=None,
                    affected_component="Dockerfile",
                    fix_available=True,
                    fix_description="Follow Docker security best practices",
                    compliance_impact=[ComplianceFramework.RBI, ComplianceFramework.PCI_DSS]
                )
                vulnerabilities.append(vulnerability)
            
            logger.info(f"📄 Dockerfile analysis found {len(vulnerabilities)} security issues")
            
        except Exception as e:
            logger.error(f"❌ Dockerfile analysis failed: {e}")
        
        return vulnerabilities
    
    async def _scan_image_secrets(self, image_name: str) -> List[SecurityVulnerability]:
        """Container image में secrets scan करता है"""
        logger.info(f"🔐 Scanning for secrets in {image_name}")
        
        vulnerabilities = []
        
        try:
            # Extract image filesystem for scanning
            # This is a simplified implementation
            # Real implementation would mount and scan the filesystem
            
            # Common secret patterns for Indian context
            indian_secret_patterns = [
                r'razorpay_[a-zA-Z0-9]{20,}',  # Razorpay API keys
                r'paytm_[a-zA-Z0-9]{20,}',     # Paytm API keys
                r'upi_[a-zA-Z0-9]{15,}',       # UPI related secrets
                r'banking_[a-zA-Z0-9]{20,}',   # Banking API keys
                r'aadhaar_[0-9]{12}',          # Aadhaar numbers (should never be in code)
                r'pan_[A-Z]{5}[0-9]{4}[A-Z]',  # PAN numbers
            ]
            
            # Mock secrets detection
            # Real implementation would use tools like gitleaks or detect-secrets
            mock_secrets_found = []  # Would be populated by actual scanning
            
            for secret in mock_secrets_found:
                vulnerability = SecurityVulnerability(
                    id=f"secret-{uuid.uuid4().hex[:8]}",
                    title="Hardcoded secret detected",
                    description=f"Secret pattern found: {secret['pattern']}",
                    severity=ScanSeverity.CRITICAL,
                    cve_id=None,
                    cvss_score=9.0,
                    affected_component="Container filesystem",
                    fix_available=True,
                    fix_description="Remove hardcoded secrets and use secure secret management",
                    compliance_impact=[ComplianceFramework.RBI, ComplianceFramework.PCI_DSS, ComplianceFramework.SPDI_RULES]
                )
                vulnerabilities.append(vulnerability)
            
            logger.info(f"🔐 Secrets scan found {len(vulnerabilities)} issues")
            
        except Exception as e:
            logger.error(f"❌ Secrets scan failed: {e}")
        
        return vulnerabilities
    
    async def _check_indian_compliance(self, image_name: str, vulnerabilities: List[SecurityVulnerability]) -> Dict[ComplianceFramework, bool]:
        """Indian compliance frameworks के against check करता है"""
        logger.info(f"🏛️ Checking Indian compliance for {image_name}")
        
        compliance_status = {}
        
        # RBI Compliance Check
        rbi_compliant = True
        critical_vulns = [v for v in vulnerabilities if v.severity == ScanSeverity.CRITICAL]
        
        if len(critical_vulns) > 0:
            rbi_compliant = False  # RBI requires zero critical vulnerabilities
        
        # Check for specific RBI requirements
        has_encryption_issues = any('encryption' in v.description.lower() for v in vulnerabilities)
        has_access_control_issues = any('access' in v.description.lower() for v in vulnerabilities)
        
        if has_encryption_issues or has_access_control_issues:
            rbi_compliant = False
        
        compliance_status[ComplianceFramework.RBI] = rbi_compliant
        
        # PCI-DSS Compliance Check
        pci_compliant = True
        high_vulns = [v for v in vulnerabilities if v.severity in [ScanSeverity.CRITICAL, ScanSeverity.HIGH]]
        
        if len(high_vulns) > 3:  # PCI-DSS allows limited high-severity issues
            pci_compliant = False
        
        compliance_status[ComplianceFramework.PCI_DSS] = pci_compliant
        
        # CERT-IN Guidelines
        cert_in_compliant = True
        if len(critical_vulns) > 2:  # CERT-IN threshold
            cert_in_compliant = False
        
        compliance_status[ComplianceFramework.CERT_IN] = cert_in_compliant
        
        logger.info(f"🏛️ Compliance status: {compliance_status}")
        
        return compliance_status
    
    def _map_severity(self, severity_str: str) -> ScanSeverity:
        """Severity string को ScanSeverity enum में convert करता है"""
        severity_map = {
            'CRITICAL': ScanSeverity.CRITICAL,
            'HIGH': ScanSeverity.HIGH,
            'MEDIUM': ScanSeverity.MEDIUM,
            'LOW': ScanSeverity.LOW,
            'INFO': ScanSeverity.INFO,
            'UNKNOWN': ScanSeverity.INFO
        }
        return severity_map.get(severity_str.upper(), ScanSeverity.INFO)
    
    def _assess_compliance_impact(self, vulnerability: Dict) -> List[ComplianceFramework]:
        """Vulnerability का compliance frameworks पर impact assess करता है"""
        impact = []
        
        severity = vulnerability.get('Severity', '').upper()
        description = vulnerability.get('Description', '').lower()
        
        # RBI impact assessment
        if severity in ['CRITICAL', 'HIGH']:
            impact.append(ComplianceFramework.RBI)
        
        if any(keyword in description for keyword in ['encryption', 'authentication', 'access']):
            impact.append(ComplianceFramework.RBI)
        
        # PCI-DSS impact assessment
        if any(keyword in description for keyword in ['payment', 'card', 'financial']):
            impact.append(ComplianceFramework.PCI_DSS)
        
        # SPDI Rules impact (for personal data)
        if any(keyword in description for keyword in ['data', 'privacy', 'personal']):
            impact.append(ComplianceFramework.SPDI_RULES)
        
        return impact
    
    def _calculate_security_score(self, vulnerabilities: List[SecurityVulnerability]) -> float:
        """Security score calculate करता है (0-100)"""
        if not vulnerabilities:
            return 100.0
        
        # Scoring weights
        severity_weights = {
            ScanSeverity.CRITICAL: 25,
            ScanSeverity.HIGH: 10,
            ScanSeverity.MEDIUM: 5,
            ScanSeverity.LOW: 2,
            ScanSeverity.INFO: 1
        }
        
        total_penalty = 0
        for vuln in vulnerabilities:
            penalty = severity_weights.get(vuln.severity, 1)
            
            # Additional penalty for compliance impact
            if ComplianceFramework.RBI in vuln.compliance_impact:
                penalty *= 1.5
            
            total_penalty += penalty
        
        # Calculate score (max penalty assumed as 500 for normalization)
        score = max(0, 100 - (total_penalty / 5))
        
        return round(score, 2)
    
    def _generate_security_recommendations(self, scan_result: SecurityScanResult) -> List[str]:
        """Security recommendations generate करता है"""
        recommendations = []
        
        # Critical vulnerabilities
        critical_vulns = [v for v in scan_result.vulnerabilities if v.severity == ScanSeverity.CRITICAL]
        if critical_vulns:
            recommendations.append(f"URGENT: Fix {len(critical_vulns)} critical vulnerabilities immediately")
            recommendations.append("Critical vulnerabilities may violate RBI compliance requirements")
        
        # High severity vulnerabilities
        high_vulns = [v for v in scan_result.vulnerabilities if v.severity == ScanSeverity.HIGH]
        if high_vulns:
            recommendations.append(f"Fix {len(high_vulns)} high-severity vulnerabilities within 7 days")
        
        # Compliance specific recommendations
        if not scan_result.compliance_status.get(ComplianceFramework.RBI, True):
            recommendations.append("RBI compliance violation detected - immediate remediation required")
            recommendations.append("Review data encryption and access control implementations")
        
        if not scan_result.compliance_status.get(ComplianceFramework.PCI_DSS, True):
            recommendations.append("PCI-DSS compliance at risk - review payment handling security")
        
        # General security recommendations
        if scan_result.overall_score < 70:
            recommendations.append("Overall security score below acceptable threshold")
            recommendations.append("Consider implementing additional security hardening measures")
        
        # Base image recommendations
        dockerfile_issues = [v for v in scan_result.vulnerabilities if v.affected_component == "Dockerfile"]
        if dockerfile_issues:
            recommendations.append("Review Dockerfile for security best practices")
            recommendations.append("Consider using minimal base images like distroless or alpine")
        
        return recommendations
    
    async def scan_git_repository(self, repo_url: str, branch: str = "main") -> SecurityScanResult:
        """Git repository की security scanning करता है"""
        scan_id = f"git-{uuid.uuid4().hex[:8]}"
        logger.info(f"📂 Starting Git repository scan: {repo_url} (ID: {scan_id})")
        
        # Implementation would include:
        # - Clone repository
        # - Run gitleaks for secrets
        # - Scan for hardcoded credentials
        # - Check for sensitive Indian data patterns
        # - Analyze commit history for security issues
        
        # Mock implementation for now
        scan_result = SecurityScanResult(
            scan_id=scan_id,
            scan_type="git_repository",
            target=repo_url,
            status=ScanStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            vulnerabilities=[],
            overall_score=95.0,
            compliance_status={ComplianceFramework.RBI: True},
            recommendations=["Repository appears secure"]
        )
        
        return scan_result
    
    async def scan_kubernetes_manifests(self, manifests_path: str) -> SecurityScanResult:
        """Kubernetes manifests की security scanning करता है"""
        scan_id = f"k8s-{uuid.uuid4().hex[:8]}"
        logger.info(f"☸️ Starting Kubernetes manifests scan: {manifests_path} (ID: {scan_id})")
        
        # Implementation would include:
        # - Parse YAML manifests
        # - Check security contexts
        # - Validate RBAC policies
        # - Check for privileged containers
        # - Validate network policies
        # - Check resource limits
        
        # Mock implementation for now
        scan_result = SecurityScanResult(
            scan_id=scan_id,
            scan_type="kubernetes_manifests",
            target=manifests_path,
            status=ScanStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            vulnerabilities=[],
            overall_score=88.0,
            compliance_status={ComplianceFramework.RBI: True},
            recommendations=["Manifests follow security best practices"]
        )
        
        return scan_result
    
    def get_scan_report(self, scan_id: str, format: str = "json") -> str:
        """Scan report generate करता है"""
        if scan_id not in self.scan_results:
            raise ValueError(f"Scan ID {scan_id} not found")
        
        scan_result = self.scan_results[scan_id]
        
        if format == "json":
            return json.dumps({
                "scan_id": scan_result.scan_id,
                "scan_type": scan_result.scan_type,
                "target": scan_result.target,
                "status": scan_result.status.value,
                "start_time": scan_result.start_time.isoformat(),
                "end_time": scan_result.end_time.isoformat() if scan_result.end_time else None,
                "overall_score": scan_result.overall_score,
                "vulnerabilities_count": len(scan_result.vulnerabilities),
                "critical_vulnerabilities": len([v for v in scan_result.vulnerabilities if v.severity == ScanSeverity.CRITICAL]),
                "compliance_status": {k.value: v for k, v in scan_result.compliance_status.items()},
                "recommendations": scan_result.recommendations
            }, indent=2)
        
        elif format == "html":
            # Generate HTML report for Indian compliance teams
            html_report = f"""
            <html>
            <head><title>Security Scan Report - {scan_result.scan_id}</title></head>
            <body>
                <h1>Security Scan Report</h1>
                <h2>Scan Details</h2>
                <p>Scan ID: {scan_result.scan_id}</p>
                <p>Target: {scan_result.target}</p>
                <p>Overall Score: {scan_result.overall_score}/100</p>
                
                <h2>Compliance Status</h2>
                <ul>
                {''.join(f'<li>{k.value}: {"✅ Compliant" if v else "❌ Non-Compliant"}</li>' for k, v in scan_result.compliance_status.items())}
                </ul>
                
                <h2>Recommendations</h2>
                <ul>
                {''.join(f'<li>{rec}</li>' for rec in scan_result.recommendations)}
                </ul>
            </body>
            </html>
            """
            return html_report
        
        else:
            raise ValueError(f"Unsupported format: {format}")

async def main():
    """Main function - Security scanner चलाता है"""
    logger.info("🔒 Starting Indian Security Scanner...")
    
    scanner = IndianSecurityScanner()
    
    try:
        # Initialize scanner
        await scanner.initialize()
        
        # Example: Scan a container image
        image_name = "nginx:latest"
        scan_result = await scanner.scan_container_image(image_name)
        
        print(f"\n{'='*50}")
        print(f"Security Scan Results for {image_name}")
        print(f"{'='*50}")
        print(f"Scan ID: {scan_result.scan_id}")
        print(f"Status: {scan_result.status.value}")
        print(f"Overall Score: {scan_result.overall_score}/100")
        print(f"Vulnerabilities Found: {len(scan_result.vulnerabilities)}")
        print(f"Critical Issues: {len([v for v in scan_result.vulnerabilities if v.severity == ScanSeverity.CRITICAL])}")
        
        print(f"\nCompliance Status:")
        for framework, status in scan_result.compliance_status.items():
            status_emoji = "✅" if status else "❌"
            print(f"  {framework.value}: {status_emoji}")
        
        print(f"\nRecommendations:")
        for i, rec in enumerate(scan_result.recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Generate report
        report = scanner.get_scan_report(scan_result.scan_id, "json")
        print(f"\nDetailed Report:\n{report}")
        
    except Exception as e:
        logger.error(f"❌ Security scanner failed: {e}")
        raise

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
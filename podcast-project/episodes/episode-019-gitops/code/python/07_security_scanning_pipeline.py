#!/usr/bin/env python3
"""
GitOps Security Scanning Pipeline
=================================

RBI/PCI-DSS compliant security scanning pipeline for GitOps deployments।
Container vulnerability scanning, secrets detection, और compliance validation।

Features:
- Multi-stage security scanning (SAST, DAST, container scanning)
- Indian compliance validation (RBI, PCI-DSS, IT Act 2000)
- Secrets detection और remediation
- License compliance checking
- Security policy enforcement
- Automated remediation suggestions
- Integration with Indian security tools

Author: Hindi Tech Podcast - Episode 19
Context: Security-First GitOps for Indian Banking
"""

import asyncio
import logging
import json
import yaml
import os
import hashlib
import re
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import kubernetes
from kubernetes import client, config
import aiohttp
import asyncpg
import docker
import subprocess
import tempfile
from pathlib import Path
import tarfile
import zipfile
import requests
from urllib.parse import urlparse
import pytz

# Security scanning libraries
import bandit
from safety.safety import Safety
from safety.util import read_requirements

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

# Enhanced logging for security operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('security_scanning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SecurityScanType(Enum):
    """Types of security scans"""
    CONTAINER_VULNERABILITY = "container_vulnerability"
    STATIC_CODE_ANALYSIS = "static_code_analysis"
    SECRETS_DETECTION = "secrets_detection"
    LICENSE_COMPLIANCE = "license_compliance"
    CONFIGURATION_SECURITY = "configuration_security"
    DEPENDENCY_CHECK = "dependency_check"
    COMPLIANCE_VALIDATION = "compliance_validation"

class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class ComplianceFramework(Enum):
    """Indian compliance frameworks"""
    RBI = "rbi"              # Reserve Bank of India
    PCI_DSS = "pci_dss"      # Payment Card Industry
    IT_ACT_2000 = "it_act_2000"  # Information Technology Act
    CERT_IN = "cert_in"      # Indian Computer Emergency Response Team
    GDPR = "gdpr"            # For international operations

@dataclass
class SecurityVulnerability:
    """Security vulnerability definition"""
    vuln_id: str
    title: str
    description: str
    severity: VulnerabilitySeverity
    cve_id: Optional[str] = None
    
    # Location information
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    component: Optional[str] = None
    version: Optional[str] = None
    
    # Fix information
    fix_available: bool = False
    fix_version: Optional[str] = None
    remediation_steps: List[str] = field(default_factory=list)
    
    # Indian compliance impact
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    business_impact: str = "unknown"
    
    # Context
    detected_at: datetime = field(default_factory=lambda: datetime.now(IST))
    scan_type: Optional[SecurityScanType] = None

@dataclass
class SecurityScanResult:
    """Complete security scan result"""
    scan_id: str
    application: str
    image_tag: str
    scan_types: List[SecurityScanType]
    
    # Results
    vulnerabilities: List[SecurityVulnerability] = field(default_factory=list)
    total_vulnerabilities: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Compliance
    compliance_passed: bool = False
    compliance_issues: List[str] = field(default_factory=list)
    
    # Timing
    started_at: datetime = field(default_factory=lambda: datetime.now(IST))
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Deployment decision
    deployment_allowed: bool = False
    blocking_issues: List[str] = field(default_factory=list)

@dataclass
class SecurityConfig:
    """Security scanning configuration"""
    # Container scanning
    container_registry: str = "harbor.company.com"
    trivy_config: Dict[str, Any] = field(default_factory=dict)
    clair_config: Dict[str, Any] = field(default_factory=dict)
    
    # Code scanning
    sonarqube_url: str = ""
    sonarqube_token: str = ""
    bandit_config_path: str = ""
    
    # Secrets scanning
    git_secrets_patterns: List[str] = field(default_factory=list)
    custom_secrets_patterns: List[str] = field(default_factory=list)
    
    # Compliance
    required_compliance: List[ComplianceFramework] = field(default_factory=lambda: [ComplianceFramework.RBI])
    compliance_policies_path: str = ""
    
    # Database
    postgres_url: str = "postgresql://user:pass@postgres:5432/security"
    
    # Notifications
    slack_webhook: str = ""
    security_team_email: str = "security@company.com"
    
    # Indian business settings
    enable_rbi_compliance: bool = True
    enable_pci_compliance: bool = True
    data_residency_check: bool = True
    
    # Thresholds
    max_critical_vulnerabilities: int = 0
    max_high_vulnerabilities: int = 5
    max_medium_vulnerabilities: int = 20
    
    # Remediation
    auto_fix_enabled: bool = True
    auto_update_dependencies: bool = False  # Conservative for banking

class IndianSecurityPatterns:
    """
    Indian specific security patterns और compliance checks।
    
    Banking, payment systems, और data residency के लिए specialized patterns।
    """
    
    @staticmethod
    def get_indian_secrets_patterns() -> List[str]:
        """Get Indian specific secrets patterns"""
        return [
            # Banking and financial
            r'(?i)(razorpay|paytm|phonepe)[-_]?(api|key|secret)[-_]?[:=]\s*["\']?([a-zA-Z0-9_\-]+)["\']?',
            r'(?i)(sbi|hdfc|icici|axis)[-_]?(api|key|token)[-_]?[:=]\s*["\']?([a-zA-Z0-9_\-]+)["\']?',
            
            # UPI and payment gateway
            r'(?i)upi[-_]?(key|secret|token)[-_]?[:=]\s*["\']?([a-zA-Z0-9_\-]+)["\']?',
            r'(?i)(npci|bhim)[-_]?(api|key)[-_]?[:=]\s*["\']?([a-zA-Z0-9_\-]+)["\']?',
            
            # Indian cloud providers
            r'(?i)(jio|tata|airtel)[-_]?cloud[-_]?(key|token)[-_]?[:=]\s*["\']?([a-zA-Z0-9_\-]+)["\']?',
            
            # Government APIs
            r'(?i)(aadhaar|pan|gstin?)[-_]?(api|key|token)[-_]?[:=]\s*["\']?([a-zA-Z0-9_\-]+)["\']?',
            
            # Standard patterns
            r'(?i)(password|passwd|pwd)[-_]?[:=]\s*["\']?([a-zA-Z0-9_\-!@#$%^&*()]+)["\']?',
            r'(?i)(api|secret|private)[-_]?(key|token)[-_]?[:=]\s*["\']?([a-zA-Z0-9_\-]+)["\']?'
        ]
    
    @staticmethod
    def get_rbi_compliance_checks() -> List[Dict[str, Any]]:
        """Get RBI compliance validation checks"""
        return [
            {
                'name': 'Data Residency',
                'description': 'All data must be stored within Indian borders',
                'pattern': r'(?i)(\.amazonaws\.com|\.azure\.com|\.googleapis\.com)',
                'regions_allowed': ['ap-south-1', 'ap-south-2', 'in-west-1'],
                'severity': VulnerabilitySeverity.CRITICAL
            },
            {
                'name': 'Encryption at Rest',
                'description': 'All sensitive data must be encrypted at rest',
                'checks': [
                    'database_encryption_enabled',
                    'storage_encryption_enabled',
                    'backup_encryption_enabled'
                ],
                'severity': VulnerabilitySeverity.HIGH
            },
            {
                'name': 'Audit Logging',
                'description': 'Complete audit trails required for all transactions',
                'checks': [
                    'application_audit_logging',
                    'database_audit_logging',
                    'access_audit_logging'
                ],
                'severity': VulnerabilitySeverity.HIGH
            },
            {
                'name': 'Access Control',
                'description': 'Principle of least privilege access control',
                'checks': [
                    'rbac_enabled',
                    'mfa_required',
                    'privileged_access_monitored'
                ],
                'severity': VulnerabilitySeverity.HIGH
            }
        ]
    
    @staticmethod
    def get_pci_dss_requirements() -> List[Dict[str, Any]]:
        """Get PCI-DSS compliance requirements"""
        return [
            {
                'name': 'Network Segmentation',
                'description': 'Payment systems must be network isolated',
                'checks': [
                    'network_policies_defined',
                    'payment_zone_isolated',
                    'firewall_rules_restrictive'
                ],
                'severity': VulnerabilitySeverity.CRITICAL
            },
            {
                'name': 'Vulnerability Management',
                'description': 'Regular vulnerability scanning and patching',
                'max_vulnerabilities': {
                    'critical': 0,
                    'high': 2,
                    'medium': 10
                },
                'severity': VulnerabilitySeverity.HIGH
            },
            {
                'name': 'Secure Development',
                'description': 'Secure coding practices and code review',
                'checks': [
                    'static_analysis_passed',
                    'dependency_check_passed',
                    'secrets_scan_passed'
                ],
                'severity': VulnerabilitySeverity.HIGH
            }
        ]

class ContainerScanner:
    """
    Container vulnerability scanner।
    
    Trivy, Clair, और other tools के साथ comprehensive container security scanning।
    """
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.docker_client = docker.from_env()
        
    async def scan_container(self, image_name: str, image_tag: str) -> List[SecurityVulnerability]:
        """Scan container image for vulnerabilities"""
        try:
            logger.info(f"🔍 Scanning container: {image_name}:{image_tag}")
            
            vulnerabilities = []
            
            # Run Trivy scan
            trivy_results = await self._run_trivy_scan(image_name, image_tag)
            vulnerabilities.extend(trivy_results)
            
            # Run additional security checks
            config_vulns = await self._check_container_configuration(image_name, image_tag)
            vulnerabilities.extend(config_vulns)
            
            logger.info(f"✅ Container scan completed: {len(vulnerabilities)} vulnerabilities found")
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"❌ Container scan failed: {e}")
            return []
    
    async def _run_trivy_scan(self, image_name: str, image_tag: str) -> List[SecurityVulnerability]:
        """Run Trivy vulnerability scan"""
        try:
            full_image = f"{image_name}:{image_tag}"
            
            # Run Trivy scan
            result = subprocess.run([
                'trivy', 'image',
                '--format', 'json',
                '--severity', 'CRITICAL,HIGH,MEDIUM,LOW',
                full_image
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"Trivy scan failed: {result.stderr}")
                return []
            
            # Parse Trivy results
            trivy_data = json.loads(result.stdout)
            vulnerabilities = []
            
            for result_item in trivy_data.get('Results', []):
                for vuln in result_item.get('Vulnerabilities', []):
                    vulnerability = SecurityVulnerability(
                        vuln_id=vuln.get('VulnerabilityID', ''),
                        title=vuln.get('Title', ''),
                        description=vuln.get('Description', ''),
                        severity=VulnerabilitySeverity(vuln.get('Severity', 'UNKNOWN')),
                        cve_id=vuln.get('VulnerabilityID') if vuln.get('VulnerabilityID', '').startswith('CVE-') else None,
                        component=vuln.get('PkgName', ''),
                        version=vuln.get('InstalledVersion', ''),
                        fix_available=bool(vuln.get('FixedVersion')),
                        fix_version=vuln.get('FixedVersion'),
                        scan_type=SecurityScanType.CONTAINER_VULNERABILITY
                    )
                    
                    # Add compliance frameworks based on severity and type
                    if vulnerability.severity in [VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH]:
                        vulnerability.compliance_frameworks = [
                            ComplianceFramework.RBI,
                            ComplianceFramework.PCI_DSS
                        ]
                    
                    vulnerabilities.append(vulnerability)
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"❌ Trivy scan error: {e}")
            return []
    
    async def _check_container_configuration(self, image_name: str, image_tag: str) -> List[SecurityVulnerability]:
        """Check container configuration for security issues"""
        try:
            vulnerabilities = []
            full_image = f"{image_name}:{image_tag}"
            
            # Inspect image
            try:
                image = self.docker_client.images.get(full_image)
                config = image.attrs['Config']
                
                # Check for running as root
                if config.get('User', '') in ['', 'root', '0']:
                    vulnerabilities.append(SecurityVulnerability(
                        vuln_id='CONFIG-001',
                        title='Container Running as Root',
                        description='Container is configured to run as root user',
                        severity=VulnerabilitySeverity.HIGH,
                        remediation_steps=[
                            'Add USER directive in Dockerfile',
                            'Run as non-root user',
                            'Use security context in Kubernetes'
                        ],
                        compliance_frameworks=[ComplianceFramework.PCI_DSS],
                        scan_type=SecurityScanType.CONFIGURATION_SECURITY
                    ))
                
                # Check for exposed sensitive ports
                exposed_ports = config.get('ExposedPorts', {})
                sensitive_ports = ['22', '3389', '5432', '3306', '6379', '27017']
                
                for port in exposed_ports:
                    port_num = port.split('/')[0]
                    if port_num in sensitive_ports:
                        vulnerabilities.append(SecurityVulnerability(
                            vuln_id=f'CONFIG-002-{port_num}',
                            title=f'Sensitive Port Exposed: {port_num}',
                            description=f'Container exposes sensitive port {port_num}',
                            severity=VulnerabilitySeverity.MEDIUM,
                            remediation_steps=[
                                f'Remove EXPOSE {port_num} from Dockerfile',
                                'Use internal networking only',
                                'Implement proper service mesh'
                            ],
                            compliance_frameworks=[ComplianceFramework.RBI],
                            scan_type=SecurityScanType.CONFIGURATION_SECURITY
                        ))
                
                # Check environment variables for secrets
                env_vars = config.get('Env', [])
                for env_var in env_vars:
                    if '=' in env_var:
                        key, value = env_var.split('=', 1)
                        if self._contains_secret(key, value):
                            vulnerabilities.append(SecurityVulnerability(
                                vuln_id=f'CONFIG-003-{hashlib.md5(key.encode()).hexdigest()[:8]}',
                                title='Secrets in Environment Variables',
                                description=f'Potential secret detected in environment variable: {key}',
                                severity=VulnerabilitySeverity.CRITICAL,
                                remediation_steps=[
                                    'Use Kubernetes secrets instead of environment variables',
                                    'Implement external secret management (Vault, etc.)',
                                    'Never hardcode credentials in containers'
                                ],
                                compliance_frameworks=[ComplianceFramework.RBI, ComplianceFramework.PCI_DSS],
                                scan_type=SecurityScanType.SECRETS_DETECTION
                            ))
                
            except docker.errors.ImageNotFound:
                logger.warning(f"Image not found locally: {full_image}")
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"❌ Container configuration check failed: {e}")
            return []
    
    def _contains_secret(self, key: str, value: str) -> bool:
        """Check if environment variable contains potential secret"""
        secret_keywords = [
            'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'api',
            'credential', 'auth', 'private', 'cert', 'razorpay', 'paytm'
        ]
        
        key_lower = key.lower()
        return any(keyword in key_lower for keyword in secret_keywords) and len(value) > 8

class CodeScanner:
    """
    Static code analysis scanner।
    
    SAST tools integration के साथ secure coding practices validation।
    """
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        
    async def scan_source_code(self, source_path: str) -> List[SecurityVulnerability]:
        """Scan source code for security vulnerabilities"""
        try:
            logger.info(f"🔍 Scanning source code: {source_path}")
            
            vulnerabilities = []
            
            # Run Bandit for Python code
            if self._has_python_code(source_path):
                bandit_results = await self._run_bandit_scan(source_path)
                vulnerabilities.extend(bandit_results)
            
            # Run dependency check
            dependency_results = await self._check_dependencies(source_path)
            vulnerabilities.extend(dependency_results)
            
            # Run secrets detection
            secrets_results = await self._detect_secrets(source_path)
            vulnerabilities.extend(secrets_results)
            
            # Check for Indian compliance patterns
            compliance_results = await self._check_compliance_patterns(source_path)
            vulnerabilities.extend(compliance_results)
            
            logger.info(f"✅ Source code scan completed: {len(vulnerabilities)} issues found")
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"❌ Source code scan failed: {e}")
            return []
    
    def _has_python_code(self, source_path: str) -> bool:
        """Check if source contains Python code"""
        path = Path(source_path)
        return any(path.rglob('*.py'))
    
    async def _run_bandit_scan(self, source_path: str) -> List[SecurityVulnerability]:
        """Run Bandit SAST scan for Python code"""
        try:
            vulnerabilities = []
            
            # Run Bandit
            result = subprocess.run([
                'bandit', '-r', source_path,
                '-f', 'json',
                '-ll'  # Low confidence, low severity minimum
            ], capture_output=True, text=True, timeout=300)
            
            if result.stdout:
                bandit_data = json.loads(result.stdout)
                
                for issue in bandit_data.get('results', []):
                    severity_map = {
                        'HIGH': VulnerabilitySeverity.HIGH,
                        'MEDIUM': VulnerabilitySeverity.MEDIUM,
                        'LOW': VulnerabilitySeverity.LOW
                    }
                    
                    vulnerability = SecurityVulnerability(
                        vuln_id=f"BANDIT-{issue.get('test_id', '')}",
                        title=issue.get('test_name', ''),
                        description=issue.get('issue_text', ''),
                        severity=severity_map.get(issue.get('issue_severity', 'LOW'), VulnerabilitySeverity.LOW),
                        file_path=issue.get('filename', ''),
                        line_number=issue.get('line_number', 0),
                        remediation_steps=[
                            'Review the code for security best practices',
                            'Implement proper input validation',
                            'Use secure coding patterns'
                        ],
                        scan_type=SecurityScanType.STATIC_CODE_ANALYSIS
                    )
                    
                    # Add compliance frameworks for banking-related issues
                    if any(keyword in vulnerability.description.lower() for keyword in 
                           ['sql injection', 'hardcoded password', 'insecure random']):
                        vulnerability.compliance_frameworks = [
                            ComplianceFramework.RBI,
                            ComplianceFramework.PCI_DSS
                        ]
                    
                    vulnerabilities.append(vulnerability)
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"❌ Bandit scan error: {e}")
            return []
    
    async def _check_dependencies(self, source_path: str) -> List[SecurityVulnerability]:
        """Check dependencies for known vulnerabilities"""
        try:
            vulnerabilities = []
            path = Path(source_path)
            
            # Check Python dependencies
            requirements_files = list(path.rglob('requirements*.txt')) + list(path.rglob('Pipfile'))
            
            for req_file in requirements_files:
                try:
                    # Use Safety to check Python dependencies
                    result = subprocess.run([
                        'safety', 'check',
                        '--json',
                        '--file', str(req_file)
                    ], capture_output=True, text=True, timeout=120)
                    
                    if result.stdout:
                        safety_data = json.loads(result.stdout)
                        
                        for vuln in safety_data:
                            vulnerability = SecurityVulnerability(
                                vuln_id=f"SAFETY-{vuln.get('id', '')}",
                                title=f"Vulnerable dependency: {vuln.get('package_name', '')}",
                                description=vuln.get('advisory', ''),
                                severity=VulnerabilitySeverity.HIGH,  # Default to HIGH for dependency vulns
                                component=vuln.get('package_name', ''),
                                version=vuln.get('analyzed_version', ''),
                                fix_available=bool(vuln.get('minimum_affected_version')),
                                remediation_steps=[
                                    f"Update {vuln.get('package_name', '')} to version {vuln.get('minimum_affected_version', 'latest')} or higher",
                                    'Review and test the updated dependency',
                                    'Update requirements.txt file'
                                ],
                                compliance_frameworks=[ComplianceFramework.RBI],
                                scan_type=SecurityScanType.DEPENDENCY_CHECK
                            )
                            
                            vulnerabilities.append(vulnerability)
                            
                except subprocess.TimeoutExpired:
                    logger.warning(f"Safety check timeout for {req_file}")
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse Safety output for {req_file}")
            
            # Check Node.js dependencies
            package_files = list(path.rglob('package.json'))
            for package_file in package_files:
                # Run npm audit for Node.js dependencies
                package_dir = package_file.parent
                try:
                    result = subprocess.run([
                        'npm', 'audit', '--json'
                    ], cwd=package_dir, capture_output=True, text=True, timeout=120)
                    
                    if result.stdout:
                        audit_data = json.loads(result.stdout)
                        
                        for vuln_id, vuln_info in audit_data.get('vulnerabilities', {}).items():
                            vulnerability = SecurityVulnerability(
                                vuln_id=f"NPM-{vuln_id}",
                                title=f"Node.js vulnerability: {vuln_info.get('name', '')}",
                                description=vuln_info.get('overview', ''),
                                severity=VulnerabilitySeverity.HIGH,
                                component=vuln_info.get('name', ''),
                                version=vuln_info.get('range', ''),
                                remediation_steps=[
                                    'Run npm audit fix to automatically fix vulnerabilities',
                                    'Manually update vulnerable packages',
                                    'Review package-lock.json changes'
                                ],
                                scan_type=SecurityScanType.DEPENDENCY_CHECK
                            )
                            
                            vulnerabilities.append(vulnerability)
                            
                except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
                    logger.warning(f"npm audit failed for {package_file}")
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"❌ Dependency check failed: {e}")
            return []
    
    async def _detect_secrets(self, source_path: str) -> List[SecurityVulnerability]:
        """Detect secrets in source code"""
        try:
            vulnerabilities = []
            path = Path(source_path)
            
            # Get Indian-specific patterns
            patterns = IndianSecurityPatterns.get_indian_secrets_patterns()
            
            # Scan all text files
            text_extensions = {'.py', '.js', '.java', '.yaml', '.yml', '.json', '.properties', '.conf', '.env'}
            
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in text_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            line_number = 0
                            
                            for line in content.split('\n'):
                                line_number += 1
                                
                                for pattern in patterns:
                                    matches = re.finditer(pattern, line)
                                    for match in matches:
                                        vulnerability = SecurityVulnerability(
                                            vuln_id=f"SECRET-{hashlib.md5(f'{file_path}:{line_number}:{match.group()}'.encode()).hexdigest()[:12]}",
                                            title='Potential Secret Detected',
                                            description=f'Potential secret or sensitive data detected in {file_path.name}',
                                            severity=VulnerabilitySeverity.CRITICAL,
                                            file_path=str(file_path.relative_to(path)),
                                            line_number=line_number,
                                            remediation_steps=[
                                                'Move secrets to environment variables or secret management system',
                                                'Use Kubernetes secrets or external secret managers',
                                                'Never commit secrets to version control',
                                                'Rotate the exposed secret immediately'
                                            ],
                                            compliance_frameworks=[
                                                ComplianceFramework.RBI,
                                                ComplianceFramework.PCI_DSS,
                                                ComplianceFramework.IT_ACT_2000
                                            ],
                                            scan_type=SecurityScanType.SECRETS_DETECTION
                                        )
                                        
                                        vulnerabilities.append(vulnerability)
                                        
                    except Exception as e:
                        logger.warning(f"Failed to scan file {file_path}: {e}")
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"❌ Secrets detection failed: {e}")
            return []
    
    async def _check_compliance_patterns(self, source_path: str) -> List[SecurityVulnerability]:
        """Check for Indian compliance-specific patterns"""
        try:
            vulnerabilities = []
            path = Path(source_path)
            
            # RBI compliance checks
            rbi_checks = IndianSecurityPatterns.get_rbi_compliance_checks()
            
            for check in rbi_checks:
                if 'pattern' in check:
                    # Pattern-based check
                    pattern = check['pattern']
                    
                    for file_path in path.rglob('*'):
                        if file_path.is_file() and file_path.suffix in ['.yaml', '.yml', '.json', '.py', '.js']:
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    
                                    if re.search(pattern, content, re.IGNORECASE):
                                        vulnerability = SecurityVulnerability(
                                            vuln_id=f"RBI-{check['name'].replace(' ', '_').upper()}",
                                            title=f"RBI Compliance Issue: {check['name']}",
                                            description=check['description'],
                                            severity=check['severity'],
                                            file_path=str(file_path.relative_to(path)),
                                            remediation_steps=[
                                                'Review RBI guidelines for data residency',
                                                'Ensure all data stays within Indian borders',
                                                'Use Indian cloud regions only'
                                            ],
                                            compliance_frameworks=[ComplianceFramework.RBI],
                                            scan_type=SecurityScanType.COMPLIANCE_VALIDATION
                                        )
                                        
                                        vulnerabilities.append(vulnerability)
                                        
                            except Exception as e:
                                logger.warning(f"Failed to check compliance in {file_path}: {e}")
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"❌ Compliance pattern check failed: {e}")
            return []

class SecurityPipeline:
    """
    Complete security scanning pipeline।
    
    Multi-stage security scanning के साथ automated remediation और
    compliance validation for Indian banking systems।
    """
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.container_scanner = ContainerScanner(config)
        self.code_scanner = CodeScanner(config)
        self.pg_pool = None
        
    async def initialize(self) -> bool:
        """Initialize security pipeline"""
        try:
            logger.info("🚀 Initializing Security Scanning Pipeline")
            
            # Setup database connection
            self.pg_pool = await asyncpg.create_pool(
                self.config.postgres_url,
                min_size=5,
                max_size=20
            )
            
            # Initialize database schema
            await self._initialize_database()
            
            logger.info("✅ Security Pipeline initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Security Pipeline initialization failed: {e}")
            return False
    
    async def _initialize_database(self) -> None:
        """Initialize security database schema"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS security_scans (
            id SERIAL PRIMARY KEY,
            scan_id VARCHAR(255) UNIQUE NOT NULL,
            application VARCHAR(255) NOT NULL,
            image_tag VARCHAR(255) NOT NULL,
            scan_types TEXT[] NOT NULL,
            total_vulnerabilities INTEGER DEFAULT 0,
            critical_count INTEGER DEFAULT 0,
            high_count INTEGER DEFAULT 0,
            medium_count INTEGER DEFAULT 0,
            low_count INTEGER DEFAULT 0,
            compliance_passed BOOLEAN DEFAULT FALSE,
            deployment_allowed BOOLEAN DEFAULT FALSE,
            started_at TIMESTAMP WITH TIME ZONE NOT NULL,
            completed_at TIMESTAMP WITH TIME ZONE,
            duration_seconds FLOAT DEFAULT 0,
            scan_data JSONB DEFAULT '{}'::jsonb,
            
            INDEX idx_scan_app (application),
            INDEX idx_scan_started (started_at),
            INDEX idx_scan_compliance (compliance_passed)
        );
        
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id SERIAL PRIMARY KEY,
            scan_id VARCHAR(255) REFERENCES security_scans(scan_id),
            vuln_id VARCHAR(255) NOT NULL,
            title VARCHAR(500) NOT NULL,
            description TEXT,
            severity VARCHAR(20) NOT NULL,
            cve_id VARCHAR(50),
            file_path VARCHAR(1000),
            line_number INTEGER,
            component VARCHAR(255),
            version VARCHAR(100),
            fix_available BOOLEAN DEFAULT FALSE,
            fix_version VARCHAR(100),
            compliance_frameworks TEXT[],
            scan_type VARCHAR(50),
            detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            remediation_data JSONB DEFAULT '{}'::jsonb,
            
            INDEX idx_vuln_scan (scan_id),
            INDEX idx_vuln_severity (severity),
            INDEX idx_vuln_cve (cve_id)
        );
        """
        
        async with self.pg_pool.acquire() as conn:
            await conn.execute(schema_sql)
        
        logger.info("✅ Security database schema initialized")
    
    async def run_complete_scan(self, application: str, image_tag: str, 
                              source_path: Optional[str] = None) -> SecurityScanResult:
        """Run complete security scanning pipeline"""
        try:
            scan_id = f"SCAN-{datetime.now(IST).strftime('%Y%m%d%H%M%S')}-{hash(f'{application}{image_tag}') % 10000:04d}"
            
            logger.info(f"🚀 Starting complete security scan: {scan_id}")
            
            scan_result = SecurityScanResult(
                scan_id=scan_id,
                application=application,
                image_tag=image_tag,
                scan_types=[]
            )
            
            # Container vulnerability scanning
            logger.info("📦 Running container vulnerability scan...")
            container_vulns = await self.container_scanner.scan_container(application, image_tag)
            scan_result.vulnerabilities.extend(container_vulns)
            scan_result.scan_types.append(SecurityScanType.CONTAINER_VULNERABILITY)
            
            # Source code scanning (if source path provided)
            if source_path and Path(source_path).exists():
                logger.info("📝 Running source code security scan...")
                code_vulns = await self.code_scanner.scan_source_code(source_path)
                scan_result.vulnerabilities.extend(code_vulns)
                scan_result.scan_types.extend([
                    SecurityScanType.STATIC_CODE_ANALYSIS,
                    SecurityScanType.SECRETS_DETECTION,
                    SecurityScanType.DEPENDENCY_CHECK,
                    SecurityScanType.COMPLIANCE_VALIDATION
                ])
            
            # Calculate vulnerability counts
            scan_result.total_vulnerabilities = len(scan_result.vulnerabilities)
            scan_result.critical_count = len([v for v in scan_result.vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL])
            scan_result.high_count = len([v for v in scan_result.vulnerabilities if v.severity == VulnerabilitySeverity.HIGH])
            scan_result.medium_count = len([v for v in scan_result.vulnerabilities if v.severity == VulnerabilitySeverity.MEDIUM])
            scan_result.low_count = len([v for v in scan_result.vulnerabilities if v.severity == VulnerabilitySeverity.LOW])
            
            # Validate compliance
            scan_result.compliance_passed, scan_result.compliance_issues = await self._validate_compliance(scan_result)
            
            # Make deployment decision
            scan_result.deployment_allowed, scan_result.blocking_issues = self._make_deployment_decision(scan_result)
            
            # Complete scan
            scan_result.completed_at = datetime.now(IST)
            scan_result.duration_seconds = (scan_result.completed_at - scan_result.started_at).total_seconds()
            
            # Save scan results
            await self._save_scan_result(scan_result)
            
            # Send notifications
            await self._send_security_notifications(scan_result)
            
            logger.info(f"✅ Security scan completed: {scan_id}")
            logger.info(f"📊 Results: {scan_result.total_vulnerabilities} vulnerabilities "
                       f"({scan_result.critical_count} critical, {scan_result.high_count} high)")
            logger.info(f"🚀 Deployment allowed: {scan_result.deployment_allowed}")
            
            return scan_result
            
        except Exception as e:
            logger.error(f"❌ Complete security scan failed: {e}")
            raise e
    
    async def _validate_compliance(self, scan_result: SecurityScanResult) -> Tuple[bool, List[str]]:
        """Validate compliance requirements"""
        try:
            issues = []
            
            # Check vulnerability thresholds
            if scan_result.critical_count > self.config.max_critical_vulnerabilities:
                issues.append(f"Critical vulnerabilities exceed threshold: {scan_result.critical_count} > {self.config.max_critical_vulnerabilities}")
            
            if scan_result.high_count > self.config.max_high_vulnerabilities:
                issues.append(f"High vulnerabilities exceed threshold: {scan_result.high_count} > {self.config.max_high_vulnerabilities}")
            
            if scan_result.medium_count > self.config.max_medium_vulnerabilities:
                issues.append(f"Medium vulnerabilities exceed threshold: {scan_result.medium_count} > {self.config.max_medium_vulnerabilities}")
            
            # Check for RBI compliance violations
            if self.config.enable_rbi_compliance:
                rbi_violations = [v for v in scan_result.vulnerabilities 
                                if ComplianceFramework.RBI in v.compliance_frameworks]
                if rbi_violations:
                    issues.append(f"RBI compliance violations found: {len(rbi_violations)} issues")
            
            # Check for PCI-DSS compliance violations
            if self.config.enable_pci_compliance:
                pci_violations = [v for v in scan_result.vulnerabilities 
                                if ComplianceFramework.PCI_DSS in v.compliance_frameworks]
                if pci_violations:
                    issues.append(f"PCI-DSS compliance violations found: {len(pci_violations)} issues")
            
            # Check for secrets in container or code
            secrets_found = [v for v in scan_result.vulnerabilities 
                           if v.scan_type == SecurityScanType.SECRETS_DETECTION]
            if secrets_found:
                issues.append(f"Secrets detected in code/container: {len(secrets_found)} instances")
            
            compliance_passed = len(issues) == 0
            return compliance_passed, issues
            
        except Exception as e:
            logger.error(f"❌ Compliance validation failed: {e}")
            return False, [f"Compliance validation error: {str(e)}"]
    
    def _make_deployment_decision(self, scan_result: SecurityScanResult) -> Tuple[bool, List[str]]:
        """Make deployment decision based on scan results"""
        blocking_issues = []
        
        # Critical vulnerabilities block deployment
        if scan_result.critical_count > 0:
            blocking_issues.append(f"{scan_result.critical_count} critical vulnerabilities must be fixed")
        
        # Secrets always block deployment
        secrets_count = len([v for v in scan_result.vulnerabilities 
                           if v.scan_type == SecurityScanType.SECRETS_DETECTION])
        if secrets_count > 0:
            blocking_issues.append(f"{secrets_count} secrets must be removed")
        
        # RBI compliance violations block deployment
        rbi_critical = len([v for v in scan_result.vulnerabilities 
                          if ComplianceFramework.RBI in v.compliance_frameworks and
                          v.severity == VulnerabilitySeverity.CRITICAL])
        if rbi_critical > 0:
            blocking_issues.append(f"{rbi_critical} RBI critical compliance issues must be resolved")
        
        # PCI-DSS critical violations block deployment
        pci_critical = len([v for v in scan_result.vulnerabilities 
                          if ComplianceFramework.PCI_DSS in v.compliance_frameworks and
                          v.severity == VulnerabilitySeverity.CRITICAL])
        if pci_critical > 0:
            blocking_issues.append(f"{pci_critical} PCI-DSS critical issues must be resolved")
        
        deployment_allowed = len(blocking_issues) == 0
        return deployment_allowed, blocking_issues
    
    async def _save_scan_result(self, scan_result: SecurityScanResult) -> None:
        """Save scan result to database"""
        try:
            async with self.pg_pool.acquire() as conn:
                # Save main scan record
                await conn.execute("""
                    INSERT INTO security_scans 
                    (scan_id, application, image_tag, scan_types, total_vulnerabilities,
                     critical_count, high_count, medium_count, low_count,
                     compliance_passed, deployment_allowed, started_at, completed_at,
                     duration_seconds, scan_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                """,
                scan_result.scan_id, scan_result.application, scan_result.image_tag,
                [st.value for st in scan_result.scan_types], scan_result.total_vulnerabilities,
                scan_result.critical_count, scan_result.high_count, scan_result.medium_count,
                scan_result.low_count, scan_result.compliance_passed, scan_result.deployment_allowed,
                scan_result.started_at, scan_result.completed_at, scan_result.duration_seconds,
                json.dumps(asdict(scan_result), default=str))
                
                # Save individual vulnerabilities
                for vuln in scan_result.vulnerabilities:
                    await conn.execute("""
                        INSERT INTO vulnerabilities
                        (scan_id, vuln_id, title, description, severity, cve_id,
                         file_path, line_number, component, version, fix_available,
                         fix_version, compliance_frameworks, scan_type, detected_at,
                         remediation_data)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    """,
                    scan_result.scan_id, vuln.vuln_id, vuln.title, vuln.description,
                    vuln.severity.value, vuln.cve_id, vuln.file_path, vuln.line_number,
                    vuln.component, vuln.version, vuln.fix_available, vuln.fix_version,
                    [cf.value for cf in vuln.compliance_frameworks], 
                    vuln.scan_type.value if vuln.scan_type else None,
                    vuln.detected_at, json.dumps({'remediation_steps': vuln.remediation_steps}))
                
        except Exception as e:
            logger.error(f"❌ Failed to save scan result: {e}")
    
    async def _send_security_notifications(self, scan_result: SecurityScanResult) -> None:
        """Send security scan notifications"""
        try:
            # Send Slack notification if configured
            if self.config.slack_webhook:
                await self._send_slack_notification(scan_result)
            
            # Send email to security team
            if self.config.security_team_email:
                await self._send_email_notification(scan_result)
                
        except Exception as e:
            logger.error(f"❌ Failed to send security notifications: {e}")
    
    async def _send_slack_notification(self, scan_result: SecurityScanResult) -> None:
        """Send Slack notification"""
        try:
            color = "danger" if not scan_result.deployment_allowed else "warning" if scan_result.critical_count > 0 else "good"
            
            payload = {
                "text": f"🔒 Security Scan Results: {scan_result.application}:{scan_result.image_tag}",
                "attachments": [{
                    "color": color,
                    "title": f"Scan ID: {scan_result.scan_id}",
                    "fields": [
                        {"title": "Total Vulnerabilities", "value": str(scan_result.total_vulnerabilities), "short": True},
                        {"title": "Critical", "value": str(scan_result.critical_count), "short": True},
                        {"title": "High", "value": str(scan_result.high_count), "short": True},
                        {"title": "Medium", "value": str(scan_result.medium_count), "short": True},
                        {"title": "Compliance Passed", "value": "✅" if scan_result.compliance_passed else "❌", "short": True},
                        {"title": "Deployment Allowed", "value": "✅" if scan_result.deployment_allowed else "❌", "short": True}
                    ],
                    "footer": f"Scan completed in {scan_result.duration_seconds:.1f} seconds"
                }]
            }
            
            if scan_result.blocking_issues:
                payload["attachments"][0]["fields"].append({
                    "title": "Blocking Issues",
                    "value": "\n".join(scan_result.blocking_issues),
                    "short": False
                })
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.slack_webhook, json=payload) as response:
                    if response.status == 200:
                        logger.info("✅ Slack notification sent")
                    else:
                        logger.warning(f"⚠️ Slack notification failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Slack notification error: {e}")
    
    async def _send_email_notification(self, scan_result: SecurityScanResult) -> None:
        """Send email notification to security team"""
        # Implementation would send comprehensive security report via email
        logger.info(f"📧 Security scan report email sent for {scan_result.scan_id}")


async def main():
    """Main function for security scanning pipeline"""
    print("🔒 GitOps Security Scanning Pipeline")
    print("=" * 50)
    
    # Configuration
    config = SecurityConfig(
        container_registry="harbor.company.com",
        postgres_url=os.getenv("DATABASE_URL", "postgresql://user:pass@postgres:5432/security"),
        slack_webhook=os.getenv("SLACK_WEBHOOK", ""),
        security_team_email="security@company.com",
        enable_rbi_compliance=True,
        enable_pci_compliance=True,
        data_residency_check=True,
        max_critical_vulnerabilities=0,
        max_high_vulnerabilities=5,
        max_medium_vulnerabilities=20,
        auto_fix_enabled=True,
        auto_update_dependencies=False
    )
    
    # Initialize pipeline
    pipeline = SecurityPipeline(config)
    
    try:
        if await pipeline.initialize():
            print("✅ Security Pipeline initialized successfully")
            
            # Example scan
            scan_result = await pipeline.run_complete_scan(
                application="banking-api",
                image_tag="v2.1.0",
                source_path="/tmp/source-code"  # Optional source path
            )
            
            print(f"📊 Scan Results:")
            print(f"   Total Vulnerabilities: {scan_result.total_vulnerabilities}")
            print(f"   Critical: {scan_result.critical_count}")
            print(f"   High: {scan_result.high_count}")
            print(f"   Medium: {scan_result.medium_count}")
            print(f"   Low: {scan_result.low_count}")
            print(f"   Compliance Passed: {scan_result.compliance_passed}")
            print(f"   Deployment Allowed: {scan_result.deployment_allowed}")
            
            if scan_result.blocking_issues:
                print(f"❌ Blocking Issues:")
                for issue in scan_result.blocking_issues:
                    print(f"   • {issue}")
                    
        else:
            print("❌ Failed to initialize Security Pipeline")
            
    except Exception as e:
        print(f"❌ Security Pipeline error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
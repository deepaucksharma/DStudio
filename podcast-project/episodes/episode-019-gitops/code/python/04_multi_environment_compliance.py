#!/usr/bin/env python3
"""
Multi-Environment GitOps Compliance System
==========================================

RBI/SEBI/IRDAI compliant multi-environment GitOps deployment system।
Banking और financial services के लिए strict compliance controls के साथ।

Features:
- RBI compliance validation और audit trails
- Multi-environment promotion (Dev → UAT → Prod)
- Automated compliance checks और approvals
- Data residency enforcement for Indian markets
- PCI-DSS और security scanning integration
- Regulatory reporting और documentation

Author: Hindi Tech Podcast - Episode 19
Context: Banking and Financial Services Compliance
"""

import asyncio
import logging
import json
import yaml
import os
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import kubernetes
from kubernetes import client, config
import aiohttp
import aiofiles
import asyncpg
import boto3
from pathlib import Path
import tempfile
import subprocess
import re
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Indian timezone और compliance
import pytz
IST = pytz.timezone('Asia/Kolkata')

# Enhanced logging for compliance
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('compliance_controller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    UAT = "uat"
    STAGING = "staging" 
    PRODUCTION = "production"
    DR = "disaster_recovery"

class ComplianceLevel(Enum):
    """Indian regulatory compliance levels"""
    RBI = "rbi"          # Reserve Bank of India
    SEBI = "sebi"        # Securities and Exchange Board
    IRDAI = "irdai"      # Insurance Regulatory Authority
    PCI_DSS = "pci_dss"  # Payment Card Industry
    SOX = "sox"          # Sarbanes-Oxley (for listed companies)
    BASIC = "basic"

class DeploymentStatus(Enum):
    """Deployment status tracking"""
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    COMPLIANCE_CHECK = "compliance_check"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"

@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str
    name: str
    description: str
    compliance_level: ComplianceLevel
    environments: List[Environment]
    mandatory: bool = True
    automated_check: bool = True
    manual_approval_required: bool = False
    remediation_steps: List[str] = field(default_factory=list)

@dataclass
class ComplianceCheck:
    """Individual compliance check result"""
    rule_id: str
    status: str  # PASS, FAIL, WARNING
    message: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(IST))
    checked_by: str = "automated"

@dataclass
class DeploymentRequest:
    """Deployment request with compliance tracking"""
    request_id: str
    app_name: str
    source_environment: Environment
    target_environment: Environment
    image_tag: str
    requested_by: str
    business_justification: str
    
    # Compliance fields
    compliance_level: ComplianceLevel
    approval_required: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Audit trail
    created_at: datetime = field(default_factory=lambda: datetime.now(IST))
    status: DeploymentStatus = DeploymentStatus.PENDING_APPROVAL
    compliance_checks: List[ComplianceCheck] = field(default_factory=list)
    deployment_log: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ComplianceConfig:
    """Multi-environment compliance configuration"""
    namespace_prefix: str = "banking"
    git_repo: str = "https://github.com/company/banking-configs"
    git_branch: str = "main"
    
    # Database connections
    postgres_url: str = "postgresql://user:pass@postgres:5432/compliance"
    redis_url: str = "redis://redis:6379"
    
    # Compliance settings
    default_compliance_level: ComplianceLevel = ComplianceLevel.RBI
    require_manual_approval: bool = True
    audit_retention_years: int = 7  # RBI requirement
    enable_encryption: bool = True
    
    # Notification settings
    slack_webhook: str = ""
    email_notifications: bool = True
    compliance_team_email: str = "compliance@company.com"
    
    # Indian regulatory settings
    data_residency_required: bool = True
    allowed_regions: List[str] = field(default_factory=lambda: ['ap-south-1', 'mumbai', 'delhi'])
    rbi_reporting_enabled: bool = True

class IndianComplianceRules:
    """
    Indian financial services compliance rules।
    
    RBI, SEBI, IRDAI के guidelines के according comprehensive rules।
    """
    
    @staticmethod
    def get_rbi_rules() -> List[ComplianceRule]:
        """RBI compliance rules for banking systems"""
        return [
            ComplianceRule(
                rule_id="RBI-001",
                name="Data Residency Check",
                description="All customer data must remain within Indian borders",
                compliance_level=ComplianceLevel.RBI,
                environments=[Environment.UAT, Environment.PRODUCTION],
                automated_check=True,
                remediation_steps=[
                    "Ensure all databases are hosted in Indian data centers",
                    "Verify cloud region is ap-south-1 (Mumbai)",
                    "Check no data flows to international regions"
                ]
            ),
            ComplianceRule(
                rule_id="RBI-002", 
                name="Audit Trail Completeness",
                description="Complete audit trail for all transactions and system changes",
                compliance_level=ComplianceLevel.RBI,
                environments=[Environment.PRODUCTION],
                automated_check=True,
                remediation_steps=[
                    "Enable detailed application logging",
                    "Ensure database transaction logs are complete",
                    "Configure immutable audit log storage"
                ]
            ),
            ComplianceRule(
                rule_id="RBI-003",
                name="Encryption at Rest",
                description="All sensitive data must be encrypted at rest",
                compliance_level=ComplianceLevel.RBI,
                environments=[Environment.UAT, Environment.PRODUCTION],
                automated_check=True,
                remediation_steps=[
                    "Enable database encryption",
                    "Encrypt application configuration files",
                    "Use encrypted storage volumes"
                ]
            ),
            ComplianceRule(
                rule_id="RBI-004",
                name="Business Hours Deployment",
                description="Production deployments only during approved maintenance windows",
                compliance_level=ComplianceLevel.RBI,
                environments=[Environment.PRODUCTION],
                automated_check=True,
                manual_approval_required=True,
                remediation_steps=[
                    "Schedule deployment during maintenance window",
                    "Get business stakeholder approval",
                    "Ensure minimal customer impact"
                ]
            ),
            ComplianceRule(
                rule_id="RBI-005",
                name="Change Management Approval",
                description="All production changes require proper approval workflow",
                compliance_level=ComplianceLevel.RBI,
                environments=[Environment.PRODUCTION],
                automated_check=False,
                manual_approval_required=True,
                remediation_steps=[
                    "Submit change request to CAB (Change Advisory Board)",
                    "Get technical approval from architecture team",
                    "Get business approval from product owner"
                ]
            )
        ]
    
    @staticmethod
    def get_pci_dss_rules() -> List[ComplianceRule]:
        """PCI-DSS compliance rules for payment systems"""
        return [
            ComplianceRule(
                rule_id="PCI-001",
                name="Container Security Scan",
                description="All container images must pass security vulnerability scan",
                compliance_level=ComplianceLevel.PCI_DSS,
                environments=[Environment.UAT, Environment.PRODUCTION],
                automated_check=True,
                remediation_steps=[
                    "Run Trivy or Clair security scan",
                    "Fix all critical and high vulnerabilities",
                    "Update base images to latest versions"
                ]
            ),
            ComplianceRule(
                rule_id="PCI-002",
                name="Network Segmentation",
                description="Payment systems must be properly network isolated",
                compliance_level=ComplianceLevel.PCI_DSS,
                environments=[Environment.PRODUCTION],
                automated_check=True,
                remediation_steps=[
                    "Configure proper network policies",
                    "Implement service mesh security",
                    "Verify firewall rules"
                ]
            )
        ]

class ComplianceValidator:
    """
    Compliance rules की validation और enforcement।
    
    Automated और manual compliance checks के साथ complete audit trail।
    """
    
    def __init__(self, config: ComplianceConfig):
        self.config = config
        self.rules = self._load_compliance_rules()
    
    def _load_compliance_rules(self) -> Dict[str, ComplianceRule]:
        """Load all compliance rules"""
        all_rules = []
        all_rules.extend(IndianComplianceRules.get_rbi_rules())
        all_rules.extend(IndianComplianceRules.get_pci_dss_rules())
        
        return {rule.rule_id: rule for rule in all_rules}
    
    async def validate_deployment(self, deployment: DeploymentRequest) -> List[ComplianceCheck]:
        """Run comprehensive compliance validation"""
        checks = []
        
        # Get applicable rules for this deployment
        applicable_rules = self._get_applicable_rules(
            deployment.target_environment,
            deployment.compliance_level
        )
        
        logger.info(f"🔍 Running {len(applicable_rules)} compliance checks for {deployment.app_name}")
        
        for rule in applicable_rules:
            if rule.automated_check:
                check_result = await self._run_automated_check(rule, deployment)
                checks.append(check_result)
            else:
                # Manual check - mark as pending
                check_result = ComplianceCheck(
                    rule_id=rule.rule_id,
                    status="PENDING_MANUAL",
                    message=f"Manual approval required: {rule.description}",
                    checked_by="system"
                )
                checks.append(check_result)
        
        return checks
    
    def _get_applicable_rules(self, environment: Environment, compliance_level: ComplianceLevel) -> List[ComplianceRule]:
        """Get rules applicable to specific environment and compliance level"""
        applicable_rules = []
        
        for rule in self.rules.values():
            # Check if rule applies to this environment
            if environment in rule.environments:
                # Check if rule applies to this compliance level
                if (rule.compliance_level == compliance_level or 
                    compliance_level == ComplianceLevel.RBI):  # RBI includes all others
                    applicable_rules.append(rule)
        
        return applicable_rules
    
    async def _run_automated_check(self, rule: ComplianceRule, deployment: DeploymentRequest) -> ComplianceCheck:
        """Run individual automated compliance check"""
        try:
            logger.info(f"🔍 Checking rule {rule.rule_id}: {rule.name}")
            
            # Route to specific check method
            if rule.rule_id == "RBI-001":
                return await self._check_data_residency(rule, deployment)
            elif rule.rule_id == "RBI-002":
                return await self._check_audit_trail(rule, deployment)
            elif rule.rule_id == "RBI-003":
                return await self._check_encryption(rule, deployment)
            elif rule.rule_id == "RBI-004":
                return await self._check_business_hours(rule, deployment)
            elif rule.rule_id == "PCI-001":
                return await self._check_container_security(rule, deployment)
            elif rule.rule_id == "PCI-002":
                return await self._check_network_segmentation(rule, deployment)
            else:
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    status="SKIP",
                    message=f"Check not implemented for {rule.rule_id}"
                )
                
        except Exception as e:
            logger.error(f"❌ Compliance check {rule.rule_id} failed: {e}")
            return ComplianceCheck(
                rule_id=rule.rule_id,
                status="ERROR",
                message=f"Check failed: {str(e)}"
            )
    
    async def _check_data_residency(self, rule: ComplianceRule, deployment: DeploymentRequest) -> ComplianceCheck:
        """Check RBI data residency compliance"""
        try:
            # Check if deployment is targeting Indian regions
            evidence = {}
            
            # Mock check - in real implementation, verify:
            # 1. Database region configuration
            # 2. Cloud provider region settings
            # 3. Data flow configurations
            
            # Simulate region check
            current_region = os.getenv('AWS_REGION', 'ap-south-1')
            evidence['current_region'] = current_region
            evidence['allowed_regions'] = self.config.allowed_regions
            
            if current_region in self.config.allowed_regions:
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    status="PASS",
                    message="Data residency requirement satisfied - deployment in Indian region",
                    evidence=evidence
                )
            else:
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    status="FAIL",
                    message=f"Data residency violation - region {current_region} not allowed",
                    evidence=evidence
                )
                
        except Exception as e:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                status="ERROR",
                message=f"Data residency check failed: {e}"
            )
    
    async def _check_audit_trail(self, rule: ComplianceRule, deployment: DeploymentRequest) -> ComplianceCheck:
        """Check audit trail completeness"""
        try:
            evidence = {}
            
            # Check if audit logging is properly configured
            # In real implementation, verify:
            # 1. Application logging configuration
            # 2. Database audit settings
            # 3. System audit logs
            
            # Mock check
            audit_config_checks = [
                "application_logging_enabled",
                "database_audit_enabled", 
                "system_audit_enabled",
                "log_retention_configured"
            ]
            
            evidence['audit_checks'] = audit_config_checks
            evidence['all_checks_passed'] = True
            
            return ComplianceCheck(
                rule_id=rule.rule_id,
                status="PASS",
                message="Audit trail configuration verified",
                evidence=evidence
            )
            
        except Exception as e:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                status="ERROR",
                message=f"Audit trail check failed: {e}"
            )
    
    async def _check_encryption(self, rule: ComplianceRule, deployment: DeploymentRequest) -> ComplianceCheck:
        """Check encryption at rest compliance"""
        try:
            evidence = {}
            
            # Check encryption settings
            # In real implementation, verify:
            # 1. Database encryption settings
            # 2. Volume encryption
            # 3. Configuration encryption
            
            # Mock check
            encryption_checks = {
                "database_encryption": True,
                "volume_encryption": True,
                "config_encryption": True,
                "transit_encryption": True
            }
            
            evidence['encryption_status'] = encryption_checks
            all_encrypted = all(encryption_checks.values())
            
            if all_encrypted:
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    status="PASS",
                    message="All encryption requirements satisfied",
                    evidence=evidence
                )
            else:
                failed_checks = [k for k, v in encryption_checks.items() if not v]
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    status="FAIL",
                    message=f"Encryption missing for: {', '.join(failed_checks)}",
                    evidence=evidence
                )
                
        except Exception as e:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                status="ERROR",
                message=f"Encryption check failed: {e}"
            )
    
    async def _check_business_hours(self, rule: ComplianceRule, deployment: DeploymentRequest) -> ComplianceCheck:
        """Check business hours deployment restriction"""
        try:
            current_time = datetime.now(IST)
            evidence = {
                'current_time': current_time.isoformat(),
                'is_business_hours': self._is_business_hours(current_time),
                'is_maintenance_window': self._is_maintenance_window(current_time)
            }
            
            # Production deployments only during maintenance windows
            if deployment.target_environment == Environment.PRODUCTION:
                if self._is_maintenance_window(current_time):
                    return ComplianceCheck(
                        rule_id=rule.rule_id,
                        status="PASS",
                        message="Deployment during approved maintenance window",
                        evidence=evidence
                    )
                else:
                    return ComplianceCheck(
                        rule_id=rule.rule_id,
                        status="FAIL",
                        message="Production deployment outside maintenance window",
                        evidence=evidence
                    )
            else:
                # Non-production can deploy anytime
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    status="PASS",
                    message="Non-production deployment - no time restriction",
                    evidence=evidence
                )
                
        except Exception as e:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                status="ERROR",
                message=f"Business hours check failed: {e}"
            )
    
    async def _check_container_security(self, rule: ComplianceRule, deployment: DeploymentRequest) -> ComplianceCheck:
        """Check container security scan results"""
        try:
            evidence = {}
            
            # In real implementation, integrate with:
            # 1. Trivy security scanner
            # 2. Harbor registry scanning
            # 3. Twistlock/Aqua Security
            
            # Mock security scan
            scan_results = {
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 2,
                "medium_vulnerabilities": 5,
                "low_vulnerabilities": 12,
                "scan_timestamp": datetime.now(IST).isoformat(),
                "base_image": "ubuntu:20.04",
                "scan_tool": "trivy"
            }
            
            evidence['security_scan'] = scan_results
            
            # Fail if critical or more than 5 high vulnerabilities
            if (scan_results["critical_vulnerabilities"] > 0 or 
                scan_results["high_vulnerabilities"] > 5):
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    status="FAIL",
                    message="Container has security vulnerabilities requiring remediation",
                    evidence=evidence
                )
            else:
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    status="PASS",
                    message="Container security scan passed",
                    evidence=evidence
                )
                
        except Exception as e:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                status="ERROR",
                message=f"Container security check failed: {e}"
            )
    
    async def _check_network_segmentation(self, rule: ComplianceRule, deployment: DeploymentRequest) -> ComplianceCheck:
        """Check network segmentation for PCI compliance"""
        try:
            evidence = {}
            
            # Check network policies and isolation
            # In real implementation, verify:
            # 1. Kubernetes NetworkPolicy
            # 2. Service mesh policies
            # 3. Firewall rules
            
            # Mock network check
            network_checks = {
                "network_policies_exist": True,
                "payment_zone_isolated": True,
                "ingress_controlled": True,
                "egress_controlled": True
            }
            
            evidence['network_security'] = network_checks
            all_secure = all(network_checks.values())
            
            if all_secure:
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    status="PASS",
                    message="Network segmentation properly configured",
                    evidence=evidence
                )
            else:
                failed_checks = [k for k, v in network_checks.items() if not v]
                return ComplianceCheck(
                    rule_id=rule.rule_id,
                    status="FAIL",
                    message=f"Network segmentation issues: {', '.join(failed_checks)}",
                    evidence=evidence
                )
                
        except Exception as e:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                status="ERROR",
                message=f"Network segmentation check failed: {e}"
            )
    
    def _is_business_hours(self, timestamp: datetime) -> bool:
        """Check if timestamp is during Indian business hours"""
        return 9 <= timestamp.hour <= 18
    
    def _is_maintenance_window(self, timestamp: datetime) -> bool:
        """Check if timestamp is during approved maintenance window"""
        # Maintenance window: Sundays 2 AM - 6 AM IST
        return timestamp.weekday() == 6 and 2 <= timestamp.hour <= 6

class MultiEnvironmentController:
    """
    Multi-environment GitOps deployment controller।
    
    Complete compliance automation के साथ Dev → UAT → Production promotion।
    """
    
    def __init__(self, config: ComplianceConfig):
        self.config = config
        self.k8s_client = None
        self.pg_pool = None
        self.validator = ComplianceValidator(config)
        
    async def initialize(self) -> bool:
        """Initialize controller"""
        try:
            logger.info("🚀 Initializing Multi-Environment Compliance Controller")
            
            # Setup Kubernetes client
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            
            self.k8s_client = client.ApiClient()
            
            # Setup database connection
            self.pg_pool = await asyncpg.create_pool(
                self.config.postgres_url,
                min_size=5,
                max_size=20
            )
            
            # Initialize database schema
            await self._initialize_database()
            
            logger.info("✅ Multi-Environment Controller initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Controller initialization failed: {e}")
            return False
    
    async def _initialize_database(self) -> None:
        """Initialize compliance database schema"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS deployment_requests (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(255) UNIQUE NOT NULL,
            app_name VARCHAR(255) NOT NULL,
            source_environment VARCHAR(50) NOT NULL,
            target_environment VARCHAR(50) NOT NULL,
            image_tag VARCHAR(255) NOT NULL,
            requested_by VARCHAR(255) NOT NULL,
            business_justification TEXT,
            compliance_level VARCHAR(50) NOT NULL,
            approval_required BOOLEAN DEFAULT TRUE,
            approved_by VARCHAR(255),
            approved_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            status VARCHAR(50) NOT NULL,
            deployment_data JSONB DEFAULT '{}'::jsonb,
            
            INDEX idx_request_status (status),
            INDEX idx_request_app (app_name),
            INDEX idx_request_created (created_at)
        );
        
        CREATE TABLE IF NOT EXISTS compliance_checks (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(255) REFERENCES deployment_requests(request_id),
            rule_id VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL,
            message TEXT,
            evidence JSONB DEFAULT '{}'::jsonb,
            checked_by VARCHAR(255) DEFAULT 'automated',
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            INDEX idx_compliance_request (request_id),
            INDEX idx_compliance_rule (rule_id)
        );
        
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(255),
            event_type VARCHAR(100) NOT NULL,
            event_data JSONB NOT NULL,
            user_id VARCHAR(255),
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            ip_address INET,
            user_agent TEXT,
            
            INDEX idx_audit_request (request_id),
            INDEX idx_audit_timestamp (timestamp),
            INDEX idx_audit_event (event_type)
        );
        """
        
        async with self.pg_pool.acquire() as conn:
            await conn.execute(schema_sql)
        
        logger.info("✅ Compliance database schema initialized")
    
    async def create_deployment_request(
        self,
        app_name: str,
        source_env: Environment,
        target_env: Environment, 
        image_tag: str,
        requested_by: str,
        business_justification: str,
        compliance_level: ComplianceLevel = ComplianceLevel.RBI
    ) -> DeploymentRequest:
        """Create new deployment request"""
        try:
            request_id = f"DR-{datetime.now(IST).strftime('%Y%m%d')}-{hash(f'{app_name}{image_tag}{datetime.now(IST)}') % 10000:04d}"
            
            deployment_request = DeploymentRequest(
                request_id=request_id,
                app_name=app_name,
                source_environment=source_env,
                target_environment=target_env,
                image_tag=image_tag,
                requested_by=requested_by,
                business_justification=business_justification,
                compliance_level=compliance_level,
                approval_required=target_env == Environment.PRODUCTION
            )
            
            # Save to database
            await self._save_deployment_request(deployment_request)
            
            # Log creation event
            await self._log_audit_event(
                request_id=request_id,
                event_type="DEPLOYMENT_REQUEST_CREATED",
                event_data={
                    "app_name": app_name,
                    "source_environment": source_env.value,
                    "target_environment": target_env.value,
                    "image_tag": image_tag,
                    "requested_by": requested_by
                },
                user_id=requested_by
            )
            
            logger.info(f"📝 Created deployment request: {request_id}")
            return deployment_request
            
        except Exception as e:
            logger.error(f"❌ Failed to create deployment request: {e}")
            raise e
    
    async def process_deployment_request(self, request_id: str) -> bool:
        """Process deployment request through compliance pipeline"""
        try:
            logger.info(f"🔄 Processing deployment request: {request_id}")
            
            # Load deployment request
            deployment = await self._load_deployment_request(request_id)
            if not deployment:
                logger.error(f"❌ Deployment request {request_id} not found")
                return False
            
            # Update status to compliance check
            deployment.status = DeploymentStatus.COMPLIANCE_CHECK
            await self._update_deployment_status(deployment)
            
            # Run compliance validation
            compliance_checks = await self.validator.validate_deployment(deployment)
            deployment.compliance_checks = compliance_checks
            
            # Save compliance check results
            await self._save_compliance_checks(request_id, compliance_checks)
            
            # Check if all compliance checks passed
            failed_checks = [check for check in compliance_checks if check.status == "FAIL"]
            error_checks = [check for check in compliance_checks if check.status == "ERROR"]
            
            if failed_checks or error_checks:
                # Compliance failed
                deployment.status = DeploymentStatus.FAILED
                await self._update_deployment_status(deployment)
                
                failure_summary = []
                if failed_checks:
                    failure_summary.extend([f"FAILED: {check.message}" for check in failed_checks])
                if error_checks:
                    failure_summary.extend([f"ERROR: {check.message}" for check in error_checks])
                
                await self._send_compliance_failure_notification(deployment, failure_summary)
                
                logger.error(f"❌ Compliance checks failed for {request_id}")
                return False
            
            # Check if manual approval required
            manual_checks = [check for check in compliance_checks if check.status == "PENDING_MANUAL"]
            
            if manual_checks or deployment.approval_required:
                deployment.status = DeploymentStatus.PENDING_APPROVAL
                await self._update_deployment_status(deployment)
                
                await self._send_approval_request_notification(deployment)
                
                logger.info(f"⏳ Deployment {request_id} waiting for approval")
                return True
            
            # All checks passed, proceed with deployment
            deployment.status = DeploymentStatus.APPROVED
            deployment.approved_by = "automated"
            deployment.approved_at = datetime.now(IST)
            await self._update_deployment_status(deployment)
            
            # Execute deployment
            success = await self._execute_deployment(deployment)
            
            if success:
                deployment.status = DeploymentStatus.DEPLOYED
                await self._send_deployment_success_notification(deployment)
                logger.info(f"✅ Deployment {request_id} completed successfully")
            else:
                deployment.status = DeploymentStatus.FAILED
                await self._send_deployment_failure_notification(deployment)
                logger.error(f"❌ Deployment {request_id} failed")
            
            await self._update_deployment_status(deployment)
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to process deployment request {request_id}: {e}")
            return False
    
    async def approve_deployment(self, request_id: str, approved_by: str, comments: str = "") -> bool:
        """Manually approve deployment request"""
        try:
            logger.info(f"✅ Approving deployment request: {request_id}")
            
            deployment = await self._load_deployment_request(request_id)
            if not deployment:
                logger.error(f"❌ Deployment request {request_id} not found")
                return False
            
            if deployment.status != DeploymentStatus.PENDING_APPROVAL:
                logger.error(f"❌ Cannot approve deployment in status: {deployment.status}")
                return False
            
            # Update approval
            deployment.approved_by = approved_by
            deployment.approved_at = datetime.now(IST)
            deployment.status = DeploymentStatus.APPROVED
            
            await self._update_deployment_status(deployment)
            
            # Log approval event
            await self._log_audit_event(
                request_id=request_id,
                event_type="DEPLOYMENT_APPROVED",
                event_data={
                    "approved_by": approved_by,
                    "comments": comments,
                    "approval_timestamp": deployment.approved_at.isoformat()
                },
                user_id=approved_by
            )
            
            # Execute deployment
            success = await self._execute_deployment(deployment)
            
            if success:
                deployment.status = DeploymentStatus.DEPLOYED
                await self._send_deployment_success_notification(deployment)
            else:
                deployment.status = DeploymentStatus.FAILED
                await self._send_deployment_failure_notification(deployment)
            
            await self._update_deployment_status(deployment)
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to approve deployment {request_id}: {e}")
            return False
    
    async def _execute_deployment(self, deployment: DeploymentRequest) -> bool:
        """Execute the actual deployment"""
        try:
            logger.info(f"🚀 Executing deployment for {deployment.app_name}")
            
            # Get target namespace
            target_namespace = f"{self.config.namespace_prefix}-{deployment.target_environment.value}"
            
            # Update deployment with new image
            apps_v1 = client.AppsV1Api()
            
            try:
                # Get existing deployment
                existing_deployment = apps_v1.read_namespaced_deployment(
                    name=deployment.app_name,
                    namespace=target_namespace
                )
                
                # Update image
                existing_deployment.spec.template.spec.containers[0].image = deployment.image_tag
                
                # Add compliance annotations
                if not existing_deployment.metadata.annotations:
                    existing_deployment.metadata.annotations = {}
                
                existing_deployment.metadata.annotations.update({
                    'compliance.company.com/level': deployment.compliance_level.value,
                    'compliance.company.com/request-id': deployment.request_id,
                    'compliance.company.com/approved-by': deployment.approved_by or 'automated',
                    'compliance.company.com/deployment-time': datetime.now(IST).isoformat(),
                    'compliance.company.com/source-env': deployment.source_environment.value
                })
                
                # Update deployment
                apps_v1.patch_namespaced_deployment(
                    name=deployment.app_name,
                    namespace=target_namespace,
                    body=existing_deployment
                )
                
                # Wait for rollout to complete
                rollout_success = await self._wait_for_rollout_complete(
                    deployment.app_name, 
                    target_namespace
                )
                
                if rollout_success:
                    # Log successful deployment
                    await self._log_audit_event(
                        request_id=deployment.request_id,
                        event_type="DEPLOYMENT_EXECUTED",
                        event_data={
                            "app_name": deployment.app_name,
                            "namespace": target_namespace,
                            "image_tag": deployment.image_tag,
                            "rollout_successful": True
                        },
                        user_id=deployment.approved_by or 'automated'
                    )
                    
                    logger.info(f"✅ Deployment successful: {deployment.app_name}")
                    return True
                else:
                    logger.error(f"❌ Rollout failed for {deployment.app_name}")
                    return False
                    
            except client.ApiException as e:
                if e.status == 404:
                    logger.error(f"❌ Deployment {deployment.app_name} not found in {target_namespace}")
                else:
                    logger.error(f"❌ Kubernetes API error: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Deployment execution failed: {e}")
            return False
    
    async def _wait_for_rollout_complete(self, app_name: str, namespace: str, timeout: int = 600) -> bool:
        """Wait for deployment rollout to complete"""
        try:
            apps_v1 = client.AppsV1Api()
            start_time = datetime.now()
            
            while (datetime.now() - start_time).seconds < timeout:
                deployment = apps_v1.read_namespaced_deployment(
                    name=app_name,
                    namespace=namespace
                )
                
                # Check if rollout is complete
                if (deployment.status.ready_replicas and
                    deployment.status.ready_replicas == deployment.spec.replicas and
                    deployment.status.updated_replicas == deployment.spec.replicas):
                    
                    logger.info(f"✅ Rollout completed for {app_name}")
                    return True
                
                await asyncio.sleep(10)
                logger.info(f"⏳ Waiting for rollout: {app_name}")
            
            logger.warning(f"⚠️ Rollout timeout for {app_name}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error waiting for rollout: {e}")
            return False
    
    async def _save_deployment_request(self, deployment: DeploymentRequest) -> None:
        """Save deployment request to database"""
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO deployment_requests 
                (request_id, app_name, source_environment, target_environment, image_tag,
                 requested_by, business_justification, compliance_level, approval_required,
                 approved_by, approved_at, created_at, status, deployment_data)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            """,
            deployment.request_id, deployment.app_name,
            deployment.source_environment.value, deployment.target_environment.value,
            deployment.image_tag, deployment.requested_by, deployment.business_justification,
            deployment.compliance_level.value, deployment.approval_required,
            deployment.approved_by, deployment.approved_at, deployment.created_at,
            deployment.status.value, json.dumps(asdict(deployment), default=str))
    
    async def _load_deployment_request(self, request_id: str) -> Optional[DeploymentRequest]:
        """Load deployment request from database"""
        try:
            async with self.pg_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM deployment_requests WHERE request_id = $1",
                    request_id
                )
                
                if row:
                    return DeploymentRequest(
                        request_id=row['request_id'],
                        app_name=row['app_name'],
                        source_environment=Environment(row['source_environment']),
                        target_environment=Environment(row['target_environment']),
                        image_tag=row['image_tag'],
                        requested_by=row['requested_by'],
                        business_justification=row['business_justification'],
                        compliance_level=ComplianceLevel(row['compliance_level']),
                        approval_required=row['approval_required'],
                        approved_by=row['approved_by'],
                        approved_at=row['approved_at'],
                        created_at=row['created_at'],
                        status=DeploymentStatus(row['status'])
                    )
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to load deployment request: {e}")
            return None
    
    async def _update_deployment_status(self, deployment: DeploymentRequest) -> None:
        """Update deployment status in database"""
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                UPDATE deployment_requests 
                SET status = $1, approved_by = $2, approved_at = $3,
                    deployment_data = $4
                WHERE request_id = $5
            """,
            deployment.status.value, deployment.approved_by, deployment.approved_at,
            json.dumps(asdict(deployment), default=str), deployment.request_id)
    
    async def _save_compliance_checks(self, request_id: str, checks: List[ComplianceCheck]) -> None:
        """Save compliance check results"""
        async with self.pg_pool.acquire() as conn:
            for check in checks:
                await conn.execute("""
                    INSERT INTO compliance_checks 
                    (request_id, rule_id, status, message, evidence, checked_by, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                request_id, check.rule_id, check.status, check.message,
                json.dumps(check.evidence), check.checked_by, check.timestamp)
    
    async def _log_audit_event(self, request_id: str, event_type: str, 
                             event_data: Dict[str, Any], user_id: str = None) -> None:
        """Log audit event"""
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO audit_logs (request_id, event_type, event_data, user_id, timestamp)
                VALUES ($1, $2, $3, $4, $5)
            """,
            request_id, event_type, json.dumps(event_data), user_id, datetime.now(IST))
    
    async def _send_approval_request_notification(self, deployment: DeploymentRequest) -> None:
        """Send approval request notification"""
        # Implementation would send to Slack/Email
        logger.info(f"📧 Approval request notification sent for {deployment.request_id}")
    
    async def _send_compliance_failure_notification(self, deployment: DeploymentRequest, failures: List[str]) -> None:
        """Send compliance failure notification"""
        logger.info(f"📧 Compliance failure notification sent for {deployment.request_id}")
    
    async def _send_deployment_success_notification(self, deployment: DeploymentRequest) -> None:
        """Send deployment success notification"""
        logger.info(f"📧 Deployment success notification sent for {deployment.request_id}")
    
    async def _send_deployment_failure_notification(self, deployment: DeploymentRequest) -> None:
        """Send deployment failure notification"""
        logger.info(f"📧 Deployment failure notification sent for {deployment.request_id}")
    
    async def get_deployment_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed deployment status"""
        try:
            deployment = await self._load_deployment_request(request_id)
            if not deployment:
                return None
            
            # Get compliance check results
            async with self.pg_pool.acquire() as conn:
                checks = await conn.fetch("""
                    SELECT rule_id, status, message, evidence, checked_by, timestamp
                    FROM compliance_checks 
                    WHERE request_id = $1
                    ORDER BY timestamp DESC
                """, request_id)
            
            return {
                'deployment': asdict(deployment),
                'compliance_checks': [dict(check) for check in checks]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get deployment status: {e}")
            return None


async def main():
    """Main function for compliance controller"""
    print("🏛️ Multi-Environment GitOps Compliance System")
    print("=" * 60)
    
    # Configuration
    config = ComplianceConfig(
        namespace_prefix="banking",
        git_repo="https://github.com/company/banking-configs",
        postgres_url=os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/compliance"),
        default_compliance_level=ComplianceLevel.RBI,
        require_manual_approval=True,
        data_residency_required=True,
        rbi_reporting_enabled=True
    )
    
    # Initialize controller
    controller = MultiEnvironmentController(config)
    
    try:
        if await controller.initialize():
            print("✅ Compliance Controller initialized successfully")
            
            # Example: Create deployment request
            deployment_request = await controller.create_deployment_request(
                app_name="banking-api",
                source_env=Environment.UAT,
                target_env=Environment.PRODUCTION,
                image_tag="myregistry/banking-api:v2.1.0",
                requested_by="devops-engineer",
                business_justification="Critical security patch for payment processing",
                compliance_level=ComplianceLevel.RBI
            )
            
            print(f"📝 Created deployment request: {deployment_request.request_id}")
            
            # Process the request
            success = await controller.process_deployment_request(deployment_request.request_id)
            
            if success:
                print("✅ Deployment processing completed")
            else:
                print("❌ Deployment processing failed")
                
        else:
            print("❌ Failed to initialize Compliance Controller")
            
    except Exception as e:
        print(f"❌ Controller error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
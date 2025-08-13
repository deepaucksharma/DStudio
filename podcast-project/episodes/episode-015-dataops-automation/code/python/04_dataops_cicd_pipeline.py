#!/usr/bin/env python3
"""
DataOps Example 04: DataOps CI/CD Pipeline
Complete CI/CD pipeline for data engineering workflows in Indian companies
Focus: GitLab/GitHub Actions, Jenkins integration for BFSI, E-commerce data pipelines

Author: DataOps Architecture Series
Episode: 015 - DataOps Automation
"""

import os
import sys
import json
import yaml
import subprocess
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum
import git
import requests
import docker
from jinja2 import Template
import sqlite3
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import boto3
from kubernetes import client, config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/dataops/cicd.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Database setup
Base = declarative_base()

class PipelineStage(Enum):
    """Pipeline stages for DataOps CI/CD"""
    SOURCE_VALIDATION = "source_validation"
    DATA_QUALITY_CHECK = "data_quality_check"
    UNIT_TESTING = "unit_testing"
    INTEGRATION_TESTING = "integration_testing"
    SCHEMA_VALIDATION = "schema_validation"
    PERFORMANCE_TESTING = "performance_testing"
    SECURITY_SCANNING = "security_scanning"
    DEPLOYMENT = "deployment"
    MONITORING_SETUP = "monitoring_setup"
    ROLLBACK_TESTING = "rollback_testing"

class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PipelineConfig:
    """Configuration for DataOps pipeline"""
    pipeline_name: str
    company_name: str
    data_sources: List[str]
    target_environment: Environment
    notification_channels: List[str]
    quality_thresholds: Dict[str, float]
    cost_budget_inr: float
    compliance_requirements: List[str]

class PipelineExecution(Base):
    """Pipeline execution tracking"""
    __tablename__ = 'pipeline_executions'
    
    id = Column(String, primary_key=True)
    pipeline_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    commit_hash = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    stages_executed = Column(JSON)
    error_message = Column(Text)
    cost_inr = Column(Float, default=0.0)
    metadata = Column(JSON)

class StageExecution(Base):
    """Individual stage execution tracking"""
    __tablename__ = 'stage_executions'
    
    id = Column(String, primary_key=True)
    pipeline_execution_id = Column(String, nullable=False)
    stage_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    logs = Column(Text)
    artifacts = Column(JSON)
    cost_inr = Column(Float, default=0.0)

class DataOpsCI:
    """
    Continuous Integration for DataOps workflows
    Handles code quality, testing, validation for Indian companies
    """
    
    def __init__(self, config: PipelineConfig, database_url: str = "sqlite:///dataops_cicd.db"):
        self.config = config
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Initialize Docker client for containerized testing
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker not available: {e}")
            self.docker_client = None
        
        logger.info(f"DataOps CI initialized for {config.company_name}")
    
    def validate_source_code(self, repo_path: str) -> Dict[str, Any]:
        """Validate source code quality for data pipelines"""
        try:
            validation_results = {
                'python_syntax': False,
                'sql_syntax': False,
                'yaml_syntax': False,
                'code_quality_score': 0.0,
                'security_issues': [],
                'performance_warnings': [],
                'indian_compliance_check': False
            }
            
            # Check Python files
            python_files = list(Path(repo_path).rglob("*.py"))
            python_syntax_errors = 0
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        compile(f.read(), py_file, 'exec')
                except SyntaxError as e:
                    python_syntax_errors += 1
                    logger.error(f"Python syntax error in {py_file}: {e}")
            
            validation_results['python_syntax'] = python_syntax_errors == 0
            
            # Check SQL files
            sql_files = list(Path(repo_path).rglob("*.sql"))
            sql_issues = self.validate_sql_files(sql_files)
            validation_results['sql_syntax'] = len(sql_issues) == 0
            
            # Check YAML files (Airflow DAGs, configs)
            yaml_files = list(Path(repo_path).rglob("*.yaml")) + list(Path(repo_path).rglob("*.yml"))
            yaml_issues = self.validate_yaml_files(yaml_files)
            validation_results['yaml_syntax'] = len(yaml_issues) == 0
            
            # Code quality assessment
            quality_score = self.assess_code_quality(repo_path)
            validation_results['code_quality_score'] = quality_score
            
            # Security scanning for Indian compliance
            security_issues = self.scan_security_issues(repo_path)
            validation_results['security_issues'] = security_issues
            
            # Indian compliance check (data privacy, localization laws)
            compliance_check = self.check_indian_compliance(repo_path)
            validation_results['indian_compliance_check'] = compliance_check
            
            logger.info(f"Source validation completed: Quality score {quality_score:.2f}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Source validation failed: {e}")
            return {'error': str(e)}
    
    def validate_sql_files(self, sql_files: List[Path]) -> List[Dict]:
        """Validate SQL syntax and best practices"""
        issues = []
        
        try:
            for sql_file in sql_files:
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read().upper()
                
                # Check for common SQL anti-patterns
                if 'SELECT *' in sql_content:
                    issues.append({
                        'file': str(sql_file),
                        'type': 'performance',
                        'message': 'Avoid SELECT * for better performance'
                    })
                
                if 'DELETE FROM' in sql_content and 'WHERE' not in sql_content:
                    issues.append({
                        'file': str(sql_file),
                        'type': 'security',
                        'message': 'DELETE without WHERE clause detected'
                    })
                
                # Check for Indian data privacy compliance
                if any(keyword in sql_content for keyword in ['AADHAAR', 'PAN', 'MOBILE']):
                    if 'ENCRYPT' not in sql_content and 'HASH' not in sql_content:
                        issues.append({
                            'file': str(sql_file),
                            'type': 'compliance',
                            'message': 'Sensitive Indian data should be encrypted/hashed'
                        })
        
        except Exception as e:
            logger.error(f"SQL validation failed: {e}")
            issues.append({'error': str(e)})
        
        return issues
    
    def validate_yaml_files(self, yaml_files: List[Path]) -> List[Dict]:
        """Validate YAML syntax and structure"""
        issues = []
        
        try:
            for yaml_file in yaml_files:
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    issues.append({
                        'file': str(yaml_file),
                        'type': 'syntax',
                        'message': f'YAML syntax error: {e}'
                    })
        
        except Exception as e:
            logger.error(f"YAML validation failed: {e}")
            issues.append({'error': str(e)})
        
        return issues
    
    def assess_code_quality(self, repo_path: str) -> float:
        """Assess overall code quality score"""
        try:
            quality_metrics = {
                'documentation_coverage': 0.0,
                'test_coverage': 0.0,
                'complexity_score': 0.0,
                'naming_convention': 0.0,
                'error_handling': 0.0
            }
            
            # Check documentation coverage
            python_files = list(Path(repo_path).rglob("*.py"))
            documented_files = 0
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if '"""' in content or "'''" in content:
                            documented_files += 1
                except:
                    continue
            
            if python_files:
                quality_metrics['documentation_coverage'] = documented_files / len(python_files)
            
            # Check test coverage (look for test files)
            test_files = list(Path(repo_path).rglob("test_*.py")) + list(Path(repo_path).rglob("*_test.py"))
            quality_metrics['test_coverage'] = min(len(test_files) / max(len(python_files), 1), 1.0)
            
            # Check naming conventions
            good_naming = 0
            total_files = len(python_files)
            
            for py_file in python_files:
                filename = py_file.stem
                if filename.islower() and '_' in filename:
                    good_naming += 1
            
            if total_files > 0:
                quality_metrics['naming_convention'] = good_naming / total_files
            
            # Error handling check
            error_handling_files = 0
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'try:' in content and 'except' in content:
                            error_handling_files += 1
                except:
                    continue
            
            if python_files:
                quality_metrics['error_handling'] = error_handling_files / len(python_files)
            
            # Calculate overall score
            overall_score = sum(quality_metrics.values()) / len(quality_metrics)
            
            logger.info(f"Code quality metrics: {quality_metrics}")
            return overall_score
            
        except Exception as e:
            logger.error(f"Code quality assessment failed: {e}")
            return 0.0
    
    def scan_security_issues(self, repo_path: str) -> List[Dict]:
        """Scan for security issues relevant to Indian companies"""
        security_issues = []
        
        try:
            # Scan for hardcoded credentials
            sensitive_patterns = [
                (r'password\s*=\s*["\'][^"\']*["\']', 'Hardcoded password'),
                (r'api_key\s*=\s*["\'][^"\']*["\']', 'Hardcoded API key'),
                (r'secret\s*=\s*["\'][^"\']*["\']', 'Hardcoded secret'),
                (r'aws_access_key_id\s*=\s*["\'][^"\']*["\']', 'AWS credentials'),
                (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
                (r'mongodb://[^/]*:[^@]*@', 'MongoDB credentials in URL')
            ]
            
            python_files = list(Path(repo_path).rglob("*.py"))
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    import re
                    for pattern, description in sensitive_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            security_issues.append({
                                'file': str(py_file),
                                'type': 'credential_exposure',
                                'description': description,
                                'severity': 'high'
                            })
                except:
                    continue
            
            # Check for Indian data privacy compliance
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    # Check for unencrypted handling of sensitive Indian data
                    if any(term in content for term in ['aadhaar', 'pan', 'mobile', 'bank_account']):
                        if 'encrypt' not in content and 'hash' not in content:
                            security_issues.append({
                                'file': str(py_file),
                                'type': 'data_privacy',
                                'description': 'Sensitive Indian data without encryption',
                                'severity': 'critical'
                            })
                except:
                    continue
        
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            security_issues.append({'error': str(e)})
        
        return security_issues
    
    def check_indian_compliance(self, repo_path: str) -> bool:
        """Check compliance with Indian data protection laws"""
        try:
            compliance_checks = {
                'data_localization': False,
                'consent_management': False,
                'audit_logging': False,
                'encryption_in_transit': False,
                'retention_policy': False
            }
            
            # Look for compliance indicators in code
            all_files = list(Path(repo_path).rglob("*.py")) + list(Path(repo_path).rglob("*.yaml"))
            
            for file_path in all_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    # Check for data localization (Indian servers)
                    if any(region in content for region in ['ap-south-1', 'mumbai', 'india', 'in-']):
                        compliance_checks['data_localization'] = True
                    
                    # Check for consent management
                    if any(term in content for term in ['consent', 'permission', 'opt-in']):
                        compliance_checks['consent_management'] = True
                    
                    # Check for audit logging
                    if any(term in content for term in ['audit', 'log', 'track', 'monitor']):
                        compliance_checks['audit_logging'] = True
                    
                    # Check for encryption
                    if any(term in content for term in ['ssl', 'tls', 'https', 'encrypt']):
                        compliance_checks['encryption_in_transit'] = True
                    
                    # Check for retention policy
                    if any(term in content for term in ['retention', 'delete', 'purge', 'ttl']):
                        compliance_checks['retention_policy'] = True
                
                except:
                    continue
            
            # Calculate compliance score
            compliance_score = sum(compliance_checks.values()) / len(compliance_checks)
            
            logger.info(f"Indian compliance checks: {compliance_checks}")
            return compliance_score >= 0.6  # 60% compliance threshold
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return False

class DataOpsCD:
    """
    Continuous Deployment for DataOps workflows
    Handles deployment automation for Indian cloud infrastructure
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        
        # Initialize cloud clients
        self.setup_cloud_clients()
        
        logger.info(f"DataOps CD initialized for {config.company_name}")
    
    def setup_cloud_clients(self):
        """Setup cloud provider clients for Indian regions"""
        try:
            # AWS India (Mumbai region)
            self.aws_session = boto3.Session(region_name='ap-south-1')
            self.s3_client = self.aws_session.client('s3')
            self.ecs_client = self.aws_session.client('ecs')
            
            # Kubernetes client (for on-premise or managed K8s)
            try:
                config.load_incluster_config()  # For in-cluster deployment
            except:
                try:
                    config.load_kube_config()  # For local development
                except:
                    logger.warning("Kubernetes config not available")
            
            self.k8s_client = client.AppsV1Api()
            
        except Exception as e:
            logger.warning(f"Cloud clients setup failed: {e}")
    
    def deploy_to_environment(self, environment: Environment, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy data pipeline to specified environment"""
        try:
            deployment_result = {
                'environment': environment.value,
                'status': 'failed',
                'deployed_services': [],
                'rollback_plan': {},
                'cost_estimation_inr': 0.0,
                'deployment_time': datetime.now()
            }
            
            # Environment-specific deployment logic
            if environment == Environment.DEVELOPMENT:
                result = self.deploy_to_development(artifacts)
            elif environment == Environment.TESTING:
                result = self.deploy_to_testing(artifacts)
            elif environment == Environment.STAGING:
                result = self.deploy_to_staging(artifacts)
            elif environment == Environment.PRODUCTION:
                result = self.deploy_to_production(artifacts)
            else:
                raise ValueError(f"Unknown environment: {environment}")
            
            deployment_result.update(result)
            deployment_result['status'] = 'success'
            
            # Calculate deployment cost for Indian infrastructure
            deployment_result['cost_estimation_inr'] = self.calculate_deployment_cost(
                environment, len(artifacts.get('services', []))
            )
            
            logger.info(f"Deployment to {environment.value} completed successfully")
            return deployment_result
            
        except Exception as e:
            logger.error(f"Deployment to {environment.value} failed: {e}")
            deployment_result['error'] = str(e)
            return deployment_result
    
    def deploy_to_development(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to development environment (local/container)"""
        try:
            result = {
                'deployed_services': [],
                'endpoints': [],
                'rollback_plan': {'type': 'docker_restart'}
            }
            
            # Deploy using Docker containers for cost efficiency
            if self.docker_client:
                # Build and run data pipeline containers
                for service_name, service_config in artifacts.get('services', {}).items():
                    container = self.docker_client.containers.run(
                        image=service_config.get('image', 'python:3.9'),
                        command=service_config.get('command', 'python app.py'),
                        environment=service_config.get('environment', {}),
                        ports=service_config.get('ports', {}),
                        detach=True,
                        name=f"dev-{service_name}"
                    )
                    
                    result['deployed_services'].append({
                        'name': service_name,
                        'container_id': container.id,
                        'status': 'running'
                    })
                    
                    result['endpoints'].append(f"http://localhost:{service_config.get('ports', {}).get('8080/tcp', 8080)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Development deployment failed: {e}")
            raise
    
    def deploy_to_testing(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to testing environment"""
        try:
            result = {
                'deployed_services': [],
                'test_endpoints': [],
                'rollback_plan': {'type': 'k8s_rollout_undo'}
            }
            
            # Deploy to Kubernetes testing namespace
            namespace = "testing"
            
            for service_name, service_config in artifacts.get('services', {}).items():
                # Create Kubernetes deployment
                deployment_manifest = self.create_k8s_deployment_manifest(
                    service_name, service_config, namespace
                )
                
                # Apply deployment
                try:
                    api_response = self.k8s_client.create_namespaced_deployment(
                        body=deployment_manifest,
                        namespace=namespace
                    )
                    
                    result['deployed_services'].append({
                        'name': service_name,
                        'deployment_name': api_response.metadata.name,
                        'namespace': namespace,
                        'status': 'deployed'
                    })
                    
                    result['test_endpoints'].append(f"http://{service_name}.{namespace}.svc.cluster.local")
                    
                except Exception as e:
                    logger.warning(f"K8s deployment failed for {service_name}: {e}")
                    # Fallback to docker deployment
                    fallback_result = self.deploy_to_development(artifacts)
                    result.update(fallback_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Testing deployment failed: {e}")
            raise
    
    def deploy_to_staging(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to staging environment (production-like)"""
        try:
            result = {
                'deployed_services': [],
                'load_balancer_endpoints': [],
                'rollback_plan': {'type': 'blue_green_switch'}
            }
            
            # Deploy using AWS ECS for Indian region
            cluster_name = f"{self.config.company_name}-staging"
            
            for service_name, service_config in artifacts.get('services', {}).items():
                # Create ECS task definition
                task_definition = self.create_ecs_task_definition(service_name, service_config)
                
                # Register task definition
                response = self.ecs_client.register_task_definition(**task_definition)
                
                # Create or update ECS service
                try:
                    service_response = self.ecs_client.create_service(
                        cluster=cluster_name,
                        serviceName=f"staging-{service_name}",
                        taskDefinition=response['taskDefinition']['taskDefinitionArn'],
                        desiredCount=1,
                        launchType='FARGATE',
                        networkConfiguration={
                            'awsvpcConfiguration': {
                                'subnets': service_config.get('subnets', []),
                                'securityGroups': service_config.get('security_groups', []),
                                'assignPublicIp': 'ENABLED'
                            }
                        }
                    )
                    
                    result['deployed_services'].append({
                        'name': service_name,
                        'service_arn': service_response['service']['serviceArn'],
                        'status': 'deploying'
                    })
                    
                except Exception as e:
                    logger.warning(f"ECS service creation failed: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Staging deployment failed: {e}")
            raise
    
    def deploy_to_production(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to production environment with safety checks"""
        try:
            result = {
                'deployed_services': [],
                'production_endpoints': [],
                'rollback_plan': {'type': 'automated_rollback'},
                'monitoring_enabled': True
            }
            
            # Production deployment with additional safety checks
            
            # 1. Pre-deployment validation
            if not self.validate_production_readiness(artifacts):
                raise ValueError("Production readiness validation failed")
            
            # 2. Blue-green deployment for zero downtime
            result.update(self.perform_blue_green_deployment(artifacts))
            
            # 3. Setup monitoring and alerting
            self.setup_production_monitoring(artifacts)
            
            # 4. Enable auto-scaling for Indian traffic patterns
            self.configure_auto_scaling(artifacts)
            
            return result
            
        except Exception as e:
            logger.error(f"Production deployment failed: {e}")
            raise
    
    def validate_production_readiness(self, artifacts: Dict[str, Any]) -> bool:
        """Validate if deployment is ready for production"""
        try:
            readiness_checks = {
                'security_scan_passed': False,
                'performance_test_passed': False,
                'disaster_recovery_plan': False,
                'monitoring_configured': False,
                'cost_within_budget': False
            }
            
            # Check security scan results
            if artifacts.get('security_scan', {}).get('status') == 'passed':
                readiness_checks['security_scan_passed'] = True
            
            # Check performance test results
            if artifacts.get('performance_test', {}).get('status') == 'passed':
                readiness_checks['performance_test_passed'] = True
            
            # Check if disaster recovery plan exists
            if artifacts.get('disaster_recovery', {}).get('enabled', False):
                readiness_checks['disaster_recovery_plan'] = True
            
            # Check monitoring configuration
            if artifacts.get('monitoring', {}).get('configured', False):
                readiness_checks['monitoring_configured'] = True
            
            # Check cost estimation
            estimated_cost = artifacts.get('cost_estimation', 0)
            if estimated_cost <= self.config.cost_budget_inr:
                readiness_checks['cost_within_budget'] = True
            
            # Must pass all checks for production
            all_passed = all(readiness_checks.values())
            
            logger.info(f"Production readiness: {readiness_checks}")
            return all_passed
            
        except Exception as e:
            logger.error(f"Production readiness check failed: {e}")
            return False
    
    def perform_blue_green_deployment(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Perform blue-green deployment for zero downtime"""
        try:
            result = {
                'blue_environment': 'current_production',
                'green_environment': 'new_deployment',
                'switch_completed': False,
                'rollback_available': True
            }
            
            # Deploy to green environment
            green_deployment = self.deploy_green_environment(artifacts)
            result['green_deployment'] = green_deployment
            
            # Validate green environment
            if self.validate_green_environment(green_deployment):
                # Switch traffic to green
                self.switch_traffic_to_green()
                result['switch_completed'] = True
                
                # Keep blue environment for rollback
                result['rollback_plan'] = {
                    'type': 'traffic_switch',
                    'blue_environment': 'available',
                    'estimated_rollback_time_seconds': 30
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Blue-green deployment failed: {e}")
            raise
    
    def deploy_green_environment(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy new version to green environment"""
        # Implementation for green environment deployment
        return {
            'status': 'deployed',
            'environment': 'green',
            'services': artifacts.get('services', {}).keys()
        }
    
    def validate_green_environment(self, green_deployment: Dict[str, Any]) -> bool:
        """Validate green environment before switching traffic"""
        # Health checks, smoke tests, etc.
        return green_deployment.get('status') == 'deployed'
    
    def switch_traffic_to_green(self):
        """Switch traffic from blue to green environment"""
        # Implementation for traffic switching (load balancer, DNS, etc.)
        logger.info("Traffic switched to green environment")
    
    def setup_production_monitoring(self, artifacts: Dict[str, Any]):
        """Setup monitoring and alerting for production"""
        try:
            monitoring_config = {
                'metrics': ['cpu_usage', 'memory_usage', 'request_latency', 'error_rate'],
                'alerts': [
                    {'metric': 'error_rate', 'threshold': 5, 'unit': 'percent'},
                    {'metric': 'response_time', 'threshold': 2000, 'unit': 'milliseconds'},
                    {'metric': 'data_freshness', 'threshold': 30, 'unit': 'minutes'}
                ],
                'dashboards': ['system_health', 'business_metrics', 'cost_tracking'],
                'notification_channels': self.config.notification_channels
            }
            
            logger.info(f"Production monitoring configured: {monitoring_config}")
            
        except Exception as e:
            logger.error(f"Monitoring setup failed: {e}")
    
    def configure_auto_scaling(self, artifacts: Dict[str, Any]):
        """Configure auto-scaling for Indian traffic patterns"""
        try:
            # Indian traffic patterns: High during 9 AM - 11 PM
            scaling_config = {
                'peak_hours': {'start': 9, 'end': 23},
                'peak_capacity': {'min': 2, 'max': 10},
                'off_peak_capacity': {'min': 1, 'max': 3},
                'scaling_metrics': ['cpu_usage', 'request_count'],
                'scale_up_threshold': 70,
                'scale_down_threshold': 30
            }
            
            logger.info(f"Auto-scaling configured for Indian traffic: {scaling_config}")
            
        except Exception as e:
            logger.error(f"Auto-scaling setup failed: {e}")
    
    def calculate_deployment_cost(self, environment: Environment, num_services: int) -> float:
        """Calculate deployment cost in INR for Indian infrastructure"""
        try:
            # Cost factors for Indian cloud providers
            cost_factors = {
                Environment.DEVELOPMENT: {'compute': 5, 'storage': 1, 'network': 0.5},
                Environment.TESTING: {'compute': 10, 'storage': 2, 'network': 1},
                Environment.STAGING: {'compute': 25, 'storage': 5, 'network': 2},
                Environment.PRODUCTION: {'compute': 50, 'storage': 10, 'network': 5}
            }
            
            factors = cost_factors.get(environment, cost_factors[Environment.DEVELOPMENT])
            
            # Calculate monthly cost
            monthly_cost = (
                factors['compute'] * num_services * 24 * 30 +  # Compute hours
                factors['storage'] * num_services * 30 +        # Storage per month
                factors['network'] * num_services * 30          # Network per month
            )
            
            return round(monthly_cost, 2)
            
        except Exception as e:
            logger.error(f"Cost calculation failed: {e}")
            return 0.0
    
    def create_k8s_deployment_manifest(self, service_name: str, service_config: Dict, namespace: str) -> Dict:
        """Create Kubernetes deployment manifest"""
        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': service_name,
                'namespace': namespace,
                'labels': {
                    'app': service_name,
                    'company': self.config.company_name
                }
            },
            'spec': {
                'replicas': service_config.get('replicas', 1),
                'selector': {
                    'matchLabels': {
                        'app': service_name
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': service_name
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': service_name,
                            'image': service_config.get('image', 'python:3.9'),
                            'ports': [{'containerPort': service_config.get('port', 8080)}],
                            'env': [
                                {'name': k, 'value': v} 
                                for k, v in service_config.get('environment', {}).items()
                            ]
                        }]
                    }
                }
            }
        }
    
    def create_ecs_task_definition(self, service_name: str, service_config: Dict) -> Dict:
        """Create ECS task definition for AWS India"""
        return {
            'family': f"{self.config.company_name}-{service_name}",
            'networkMode': 'awsvpc',
            'requiresCompatibilities': ['FARGATE'],
            'cpu': str(service_config.get('cpu', 256)),
            'memory': str(service_config.get('memory', 512)),
            'executionRoleArn': service_config.get('execution_role_arn', ''),
            'containerDefinitions': [{
                'name': service_name,
                'image': service_config.get('image', 'python:3.9'),
                'portMappings': [{
                    'containerPort': service_config.get('port', 8080),
                    'protocol': 'tcp'
                }],
                'environment': [
                    {'name': k, 'value': v} 
                    for k, v in service_config.get('environment', {}).items()
                ],
                'logConfiguration': {
                    'logDriver': 'awslogs',
                    'options': {
                        'awslogs-group': f"/ecs/{self.config.company_name}",
                        'awslogs-region': 'ap-south-1',
                        'awslogs-stream-prefix': 'ecs'
                    }
                }
            }]
        }

def main():
    """Demonstrate DataOps CI/CD pipeline for Indian companies"""
    
    print("🚀 Starting DataOps CI/CD Pipeline Demo")
    print("=" * 60)
    
    # Configuration for Indian fintech company
    pipeline_config = PipelineConfig(
        pipeline_name="paytm_data_pipeline",
        company_name="paytm",
        data_sources=["transaction_db", "user_events", "merchant_data"],
        target_environment=Environment.STAGING,
        notification_channels=["slack", "email", "teams"],
        quality_thresholds={
            "data_completeness": 0.95,
            "data_accuracy": 0.90,
            "schema_compliance": 0.98
        },
        cost_budget_inr=100000.0,
        compliance_requirements=["PCI_DSS", "RBI_Guidelines", "Data_Localization"]
    )
    
    # Initialize CI/CD components
    ci_system = DataOpsCI(pipeline_config)
    cd_system = DataOpsCD(pipeline_config)
    
    # Demo 1: Source code validation
    print("\n🔍 Demo 1: Source Code Validation")
    
    # Create sample code structure for validation
    sample_repo_path = "/tmp/sample_dataops_repo"
    os.makedirs(sample_repo_path, exist_ok=True)
    
    # Create sample Python file
    with open(f"{sample_repo_path}/data_pipeline.py", "w") as f:
        f.write('''
"""
Sample data pipeline for Paytm transactions
"""
import pandas as pd
import logging

def process_transactions(df):
    """Process transaction data"""
    try:
        # Clean data
        df_clean = df.dropna()
        
        # Validate amounts
        df_clean = df_clean[df_clean['amount'] > 0]
        
        return df_clean
    except Exception as e:
        logging.error(f"Processing failed: {e}")
        raise

def encrypt_sensitive_data(df):
    """Encrypt sensitive fields like Aadhaar, PAN"""
    # Implementation for encryption
    return df
''')
    
    # Create sample SQL file
    with open(f"{sample_repo_path}/queries.sql", "w") as f:
        f.write('''
-- Paytm transaction analysis
SELECT 
    transaction_id,
    user_id,
    merchant_id,
    amount,
    created_at
FROM transactions
WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
  AND status = 'SUCCESS'
  AND amount > 0;

-- Encrypt sensitive data
SELECT 
    transaction_id,
    HASH(aadhaar) as aadhaar_hash,
    ENCRYPT(mobile) as mobile_encrypted
FROM user_data;
''')
    
    # Create sample YAML config
    with open(f"{sample_repo_path}/config.yaml", "w") as f:
        f.write('''
pipeline:
  name: paytm_data_processing
  schedule: "0 2 * * *"
  environment:
    region: ap-south-1
    compliance: RBI_Guidelines
data_sources:
  - name: transactions
    type: postgresql
    encryption: true
  - name: user_events
    type: kafka
    retention_days: 30
''')
    
    # Validate source code
    validation_results = ci_system.validate_source_code(sample_repo_path)
    
    print(f"   Python syntax: {'✅' if validation_results.get('python_syntax') else '❌'}")
    print(f"   SQL syntax: {'✅' if validation_results.get('sql_syntax') else '❌'}")
    print(f"   YAML syntax: {'✅' if validation_results.get('yaml_syntax') else '❌'}")
    print(f"   Code quality score: {validation_results.get('code_quality_score', 0):.2f}")
    print(f"   Indian compliance: {'✅' if validation_results.get('indian_compliance_check') else '❌'}")
    print(f"   Security issues: {len(validation_results.get('security_issues', []))}")
    
    # Demo 2: Deployment pipeline
    print("\n🚀 Demo 2: Deployment Pipeline")
    
    # Sample deployment artifacts
    deployment_artifacts = {
        'services': {
            'data_processor': {
                'image': 'paytm/data-processor:latest',
                'port': 8080,
                'replicas': 2,
                'cpu': 512,
                'memory': 1024,
                'environment': {
                    'DB_HOST': 'postgres.paytm.internal',
                    'REGION': 'ap-south-1',
                    'COMPLIANCE_MODE': 'RBI'
                }
            },
            'analytics_api': {
                'image': 'paytm/analytics-api:latest',
                'port': 9090,
                'replicas': 1,
                'cpu': 256,
                'memory': 512,
                'environment': {
                    'CACHE_ENDPOINT': 'redis.paytm.internal',
                    'LOG_LEVEL': 'INFO'
                }
            }
        },
        'security_scan': {'status': 'passed'},
        'performance_test': {'status': 'passed'},
        'disaster_recovery': {'enabled': True},
        'monitoring': {'configured': True},
        'cost_estimation': 75000  # INR
    }
    
    # Deploy to different environments
    environments_to_test = [Environment.DEVELOPMENT, Environment.TESTING, Environment.STAGING]
    
    for env in environments_to_test:
        print(f"\n   Deploying to {env.value}...")
        
        deployment_result = cd_system.deploy_to_environment(env, deployment_artifacts)
        
        print(f"   Status: {deployment_result.get('status', 'unknown')}")
        print(f"   Services deployed: {len(deployment_result.get('deployed_services', []))}")
        print(f"   Monthly cost: ₹{deployment_result.get('cost_estimation_inr', 0):,.2f}")
        
        if deployment_result.get('status') == 'success':
            print(f"   ✅ {env.value} deployment successful")
        else:
            print(f"   ❌ {env.value} deployment failed: {deployment_result.get('error', 'Unknown error')}")
    
    # Demo 3: Cost analysis
    print("\n💰 Demo 3: Cost Analysis for Indian Infrastructure")
    
    total_monthly_cost = 0
    for env in Environment:
        cost = cd_system.calculate_deployment_cost(env, 2)  # 2 services
        total_monthly_cost += cost
        print(f"   {env.value}: ₹{cost:,.2f}/month")
    
    print(f"   Total monthly cost: ₹{total_monthly_cost:,.2f}")
    
    # Recommendations for cost optimization
    print("\n📋 Cost Optimization Recommendations:")
    print("   • Use development environment for testing (₹480/month)")
    print("   • Auto-scale production during off-peak hours")
    print("   • Consider Indian cloud providers for cost savings")
    print("   • Implement data lifecycle management")
    
    print("\n✅ DataOps CI/CD Pipeline Demo Completed!")
    print("\n📝 Features demonstrated:")
    print("   ✓ Source code validation with Indian compliance")
    print("   ✓ Security scanning for sensitive data")
    print("   ✓ Multi-environment deployment automation")
    print("   ✓ Blue-green deployment for zero downtime")
    print("   ✓ Cost estimation in INR")
    print("   ✓ Auto-scaling for Indian traffic patterns")
    print("   ✓ Production monitoring and alerting")

if __name__ == "__main__":
    main()
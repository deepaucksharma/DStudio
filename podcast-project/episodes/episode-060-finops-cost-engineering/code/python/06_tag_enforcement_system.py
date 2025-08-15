#!/usr/bin/env python3
"""
Cloud Resource Tag Enforcement System
=====================================

Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering
Advanced tag governance and cost allocation system

Author: Hindi Tech Community
Date: 2025
Version: 1.0

Features:
- Automated tag enforcement across AWS/Azure/GCP
- Cost allocation by tags
- Tag compliance monitoring
- Automated remediation
- Custom tagging policies
- Department/project cost tracking
- Tag inheritance for related resources

Mumbai Context: Tag enforcement जैसे Mumbai building society maintenance
- हर flat का proper numbering और ownership tracking
- Monthly maintenance का proper allocation
- Common area cost distribution
"""

import boto3
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import re
import yaml
from concurrent.futures import ThreadPoolExecutor
import time

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

class TagEnforcementLevel(Enum):
    WARNING = "warning"
    BLOCKING = "blocking"
    AUTO_REMEDIATE = "auto_remediate"

class ResourceType(Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORKING = "networking"
    ALL = "all"

@dataclass
class TagPolicy:
    """Tag policy definition"""
    tag_key: str
    required: bool
    allowed_values: List[str]
    default_value: Optional[str]
    enforcement_level: TagEnforcementLevel
    resource_types: List[ResourceType]
    description: str

@dataclass
class TagViolation:
    """Tag policy violation"""
    resource_id: str
    resource_type: str
    provider: CloudProvider
    region: str
    violation_type: str  # missing, invalid_value, wrong_format
    policy: TagPolicy
    current_value: Optional[str]
    expected_value: Optional[str]
    discovered_at: datetime
    cost_impact: float = 0.0

@dataclass
class CostAllocation:
    """Cost allocation by tags"""
    tag_key: str
    tag_value: str
    monthly_cost: float
    resource_count: int
    provider: CloudProvider
    department: Optional[str] = None
    project: Optional[str] = None

class TagEnforcementSystem:
    """
    Advanced Tag Enforcement and Cost Allocation System
    
    Mumbai Context: यह society management system जैसा है
    - हर resource का proper tagging (flat number, owner details)
    - Cost allocation for maintenance (electricity, water, security)  
    - Compliance monitoring (society rules enforcement)
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize tag enforcement system"""
        try:
            self.region = region
            
            # Initialize cloud clients
            self.aws_ec2 = boto3.client('ec2', region_name=region)
            self.aws_s3 = boto3.client('s3')
            self.aws_rds = boto3.client('rds', region_name=region)
            self.aws_cost_explorer = boto3.client('ce', region_name=region)
            self.aws_resourcegroupstaggingapi = boto3.client(
                'resourcegroupstaggingapi', region_name=region
            )
            
            # Load policies and configuration
            self.tag_policies = self._load_tag_policies()
            self.cost_allocation_rules = self._load_cost_allocation_rules()
            self.violations_history = []
            
            logger.info("Tag Enforcement System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Tag Enforcement System: {e}")
            raise

    def _load_tag_policies(self) -> List[TagPolicy]:
        """Load tag policies from configuration"""
        # In production, this would come from a database or config file
        policies = [
            TagPolicy(
                tag_key="Environment",
                required=True,
                allowed_values=["production", "staging", "development", "test"],
                default_value="development",
                enforcement_level=TagEnforcementLevel.BLOCKING,
                resource_types=[ResourceType.ALL],
                description="Environment classification for proper cost allocation"
            ),
            TagPolicy(
                tag_key="Department",
                required=True,
                allowed_values=["engineering", "marketing", "sales", "hr", "finance", "operations"],
                default_value=None,
                enforcement_level=TagEnforcementLevel.BLOCKING,
                resource_types=[ResourceType.ALL],
                description="Department ownership for cost tracking"
            ),
            TagPolicy(
                tag_key="Project",
                required=True,
                allowed_values=[],  # Any value allowed
                default_value=None,
                enforcement_level=TagEnforcementLevel.WARNING,
                resource_types=[ResourceType.COMPUTE, ResourceType.DATABASE],
                description="Project identification for resource grouping"
            ),
            TagPolicy(
                tag_key="CostCenter",
                required=True,
                allowed_values=[],  # Pattern validation will be applied
                default_value=None,
                enforcement_level=TagEnforcementLevel.AUTO_REMEDIATE,
                resource_types=[ResourceType.ALL],
                description="Cost center for financial allocation (format: CC-XXXX)"
            ),
            TagPolicy(
                tag_key="Owner",
                required=True,
                allowed_values=[],  # Email format validation
                default_value=None,
                enforcement_level=TagEnforcementLevel.WARNING,
                resource_types=[ResourceType.ALL],
                description="Resource owner email for accountability"
            ),
            TagPolicy(
                tag_key="Application",
                required=False,
                allowed_values=["web-frontend", "api-backend", "database", "analytics", "ml-pipeline"],
                default_value=None,
                enforcement_level=TagEnforcementLevel.WARNING,
                resource_types=[ResourceType.COMPUTE, ResourceType.DATABASE],
                description="Application component identification"
            ),
            TagPolicy(
                tag_key="Backup",
                required=False,
                allowed_values=["enabled", "disabled"],
                default_value="enabled",
                enforcement_level=TagEnforcementLevel.AUTO_REMEDIATE,
                resource_types=[ResourceType.DATABASE, ResourceType.STORAGE],
                description="Backup policy enforcement"
            ),
            TagPolicy(
                tag_key="Schedule",
                required=False,
                allowed_values=["24x7", "business-hours", "dev-hours"],
                default_value="24x7",
                enforcement_level=TagEnforcementLevel.AUTO_REMEDIATE,
                resource_types=[ResourceType.COMPUTE],
                description="Operating schedule for cost optimization"
            )
        ]
        
        logger.info(f"Loaded {len(policies)} tag policies")
        return policies

    def _load_cost_allocation_rules(self) -> Dict[str, Dict]:
        """Load cost allocation rules"""
        return {
            "hierarchy": ["Department", "Project", "Environment", "Application"],
            "default_allocation": {
                "untagged_resources": "shared-services",
                "cost_center": "CC-9999"
            },
            "allocation_methods": {
                "equal_split": ["networking", "security"],
                "usage_based": ["compute", "storage"],
                "owner_based": ["database", "analytics"]
            }
        }

    async def scan_resources_for_compliance(self, 
                                          providers: List[CloudProvider] = None) -> List[TagViolation]:
        """
        Scan all cloud resources for tag compliance
        
        Mumbai Context: Society audit जैसे monthly compliance check
        - सभी flats का documentation check
        - Missing information identify करना
        """
        try:
            if providers is None:
                providers = [CloudProvider.AWS]  # Start with AWS
            
            all_violations = []
            
            for provider in providers:
                if provider == CloudProvider.AWS:
                    violations = await self._scan_aws_resources()
                    all_violations.extend(violations)
                # Add Azure and GCP scanning later
            
            # Store violations for historical tracking
            self.violations_history.extend(all_violations)
            
            logger.info(f"Found {len(all_violations)} tag compliance violations")
            return all_violations
            
        except Exception as e:
            logger.error(f"Failed to scan resources for compliance: {e}")
            return []

    async def _scan_aws_resources(self) -> List[TagViolation]:
        """Scan AWS resources for tag compliance"""
        try:
            violations = []
            
            # Get all resources with their tags
            paginator = self.aws_resourcegroupstaggingapi.get_paginator('get_resources')
            
            for page in paginator.paginate():
                for resource in page['ResourceTagMappingList']:
                    resource_arn = resource['ResourceARN']
                    current_tags = {tag['Key']: tag['Value'] for tag in resource.get('Tags', [])}
                    
                    # Parse resource type from ARN
                    resource_type = self._parse_resource_type_from_arn(resource_arn)
                    
                    # Check each policy
                    for policy in self.tag_policies:
                        if self._policy_applies_to_resource(policy, resource_type):
                            violation = self._check_tag_compliance(
                                resource_arn, current_tags, policy, resource_type
                            )
                            if violation:
                                violations.append(violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"Failed to scan AWS resources: {e}")
            return []

    def _parse_resource_type_from_arn(self, arn: str) -> str:
        """Parse resource type from AWS ARN"""
        try:
            # ARN format: arn:aws:service:region:account:resource-type/resource-name
            parts = arn.split(':')
            if len(parts) >= 6:
                service = parts[2]
                resource_part = parts[5]
                
                # Map AWS services to our resource types
                service_mapping = {
                    'ec2': 'compute',
                    's3': 'storage',
                    'rds': 'database',
                    'elasticloadbalancing': 'networking',
                    'lambda': 'compute',
                    'ecs': 'compute'
                }
                
                return service_mapping.get(service, 'unknown')
            
            return 'unknown'
            
        except Exception as e:
            logger.warning(f"Failed to parse resource type from ARN {arn}: {e}")
            return 'unknown'

    def _policy_applies_to_resource(self, policy: TagPolicy, resource_type: str) -> bool:
        """Check if policy applies to resource type"""
        if ResourceType.ALL in policy.resource_types:
            return True
        
        for rt in policy.resource_types:
            if rt.value == resource_type:
                return True
        
        return False

    def _check_tag_compliance(self, 
                            resource_arn: str,
                            current_tags: Dict[str, str],
                            policy: TagPolicy,
                            resource_type: str) -> Optional[TagViolation]:
        """Check if resource complies with tag policy"""
        try:
            tag_value = current_tags.get(policy.tag_key)
            
            # Check if required tag is missing
            if policy.required and tag_value is None:
                return TagViolation(
                    resource_id=resource_arn,
                    resource_type=resource_type,
                    provider=CloudProvider.AWS,
                    region=self.region,
                    violation_type="missing",
                    policy=policy,
                    current_value=None,
                    expected_value=policy.default_value,
                    discovered_at=datetime.now()
                )
            
            # Check if value is valid
            if tag_value is not None and policy.allowed_values:
                if tag_value not in policy.allowed_values:
                    return TagViolation(
                        resource_id=resource_arn,
                        resource_type=resource_type,
                        provider=CloudProvider.AWS,
                        region=self.region,
                        violation_type="invalid_value",
                        policy=policy,
                        current_value=tag_value,
                        expected_value=f"One of: {', '.join(policy.allowed_values)}",
                        discovered_at=datetime.now()
                    )
            
            # Check format validation for specific tags
            if tag_value is not None:
                format_error = self._validate_tag_format(policy.tag_key, tag_value)
                if format_error:
                    return TagViolation(
                        resource_id=resource_arn,
                        resource_type=resource_type,
                        provider=CloudProvider.AWS,
                        region=self.region,
                        violation_type="wrong_format",
                        policy=policy,
                        current_value=tag_value,
                        expected_value=format_error,
                        discovered_at=datetime.now()
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to check tag compliance: {e}")
            return None

    def _validate_tag_format(self, tag_key: str, tag_value: str) -> Optional[str]:
        """Validate tag value format"""
        format_rules = {
            "CostCenter": {
                "pattern": r"^CC-\d{4}$",
                "error_message": "Format should be CC-XXXX (e.g., CC-1234)"
            },
            "Owner": {
                "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "error_message": "Should be valid email format"
            },
            "Project": {
                "pattern": r"^[a-zA-Z0-9-_]{3,20}$",
                "error_message": "Should be 3-20 characters, alphanumeric with hyphens/underscores"
            }
        }
        
        if tag_key in format_rules:
            rule = format_rules[tag_key]
            if not re.match(rule["pattern"], tag_value):
                return rule["error_message"]
        
        return None

    async def remediate_violations(self, violations: List[TagViolation]) -> Dict[str, int]:
        """
        Automatically remediate tag violations where possible
        
        Mumbai Context: Automatic correction जैसे society rules enforcement
        - Missing tags को default values assign करना
        - Wrong format को correct करना
        """
        try:
            remediation_stats = {
                "attempted": 0,
                "successful": 0,
                "failed": 0,
                "skipped": 0
            }
            
            for violation in violations:
                remediation_stats["attempted"] += 1
                
                if violation.policy.enforcement_level == TagEnforcementLevel.AUTO_REMEDIATE:
                    try:
                        success = await self._apply_remediation(violation)
                        if success:
                            remediation_stats["successful"] += 1
                        else:
                            remediation_stats["failed"] += 1
                    except Exception as e:
                        logger.error(f"Remediation failed for {violation.resource_id}: {e}")
                        remediation_stats["failed"] += 1
                else:
                    remediation_stats["skipped"] += 1
            
            logger.info(f"Remediation completed: {remediation_stats}")
            return remediation_stats
            
        except Exception as e:
            logger.error(f"Failed to remediate violations: {e}")
            return {"attempted": 0, "successful": 0, "failed": 0, "skipped": 0}

    async def _apply_remediation(self, violation: TagViolation) -> bool:
        """Apply remediation for a specific violation"""
        try:
            resource_arn = violation.resource_id
            tag_key = violation.policy.tag_key
            
            # Determine remediation value
            remediation_value = None
            
            if violation.violation_type == "missing" and violation.policy.default_value:
                remediation_value = violation.policy.default_value
            elif violation.violation_type == "wrong_format":
                remediation_value = self._suggest_format_correction(
                    tag_key, violation.current_value
                )
            
            if not remediation_value:
                return False
            
            # Apply the tag
            success = await self._apply_tag_to_resource(
                resource_arn, tag_key, remediation_value
            )
            
            if success:
                logger.info(f"Applied tag {tag_key}={remediation_value} to {resource_arn}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to apply remediation: {e}")
            return False

    def _suggest_format_correction(self, tag_key: str, current_value: str) -> Optional[str]:
        """Suggest corrected format for tag value"""
        if tag_key == "CostCenter" and current_value:
            # Try to extract numbers and format properly
            numbers = re.findall(r'\d+', current_value)
            if numbers:
                return f"CC-{numbers[0].zfill(4)}"
        
        elif tag_key == "Owner" and current_value:
            # If it looks like a name, try to create email format
            if '@' not in current_value and '.' not in current_value:
                # Assume it's a name, create company email format
                clean_name = re.sub(r'[^a-zA-Z]', '', current_value.lower())
                return f"{clean_name}@company.com"
        
        return None

    async def _apply_tag_to_resource(self, resource_arn: str, tag_key: str, tag_value: str) -> bool:
        """Apply tag to AWS resource"""
        try:
            # Use resource groups tagging API for universal tagging
            response = self.aws_resourcegroupstaggingapi.tag_resources(
                ResourceARNList=[resource_arn],
                Tags={tag_key: tag_value}
            )
            
            failed_resources = response.get('FailedResourcesMap', {})
            return len(failed_resources) == 0
            
        except Exception as e:
            logger.error(f"Failed to apply tag to resource {resource_arn}: {e}")
            return False

    def analyze_cost_allocation(self, days_back: int = 30) -> List[CostAllocation]:
        """
        Analyze cost allocation based on tags
        
        Mumbai Context: Society expense allocation
        - Department-wise cost breakdown
        - Project-wise budget tracking
        """
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            cost_allocations = []
            
            # Get cost data grouped by tags
            for tag_key in ["Department", "Project", "Environment", "CostCenter"]:
                try:
                    response = self.aws_cost_explorer.get_cost_and_usage(
                        TimePeriod={
                            'Start': start_date,
                            'End': end_date
                        },
                        Granularity='MONTHLY',
                        Metrics=['BlendedCost'],
                        GroupBy=[
                            {
                                'Type': 'TAG',
                                'Key': tag_key
                            }
                        ]
                    )
                    
                    for result in response['ResultsByTime']:
                        for group in result['Groups']:
                            tag_value = group['Keys'][0] if group['Keys'] else 'untagged'
                            cost = float(group['Metrics']['BlendedCost']['Amount'])
                            
                            if cost > 0:  # Only include resources with actual cost
                                allocation = CostAllocation(
                                    tag_key=tag_key,
                                    tag_value=tag_value,
                                    monthly_cost=cost,
                                    resource_count=1,  # Simplified - would need separate query
                                    provider=CloudProvider.AWS
                                )
                                cost_allocations.append(allocation)
                
                except Exception as e:
                    logger.warning(f"Failed to get cost data for tag {tag_key}: {e}")
            
            logger.info(f"Analyzed cost allocation for {len(cost_allocations)} tag groups")
            return cost_allocations
            
        except Exception as e:
            logger.error(f"Failed to analyze cost allocation: {e}")
            return []

    def generate_compliance_report(self, violations: List[TagViolation]) -> str:
        """
        Generate comprehensive tag compliance report
        
        Mumbai Context: Society compliance report
        """
        try:
            report = f"""
Tag Compliance & Cost Allocation Report
======================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY (Mumbai Style)
===============================
यह report आपके cloud resources का complete tagging analysis है
जैसे Mumbai society में सभी flats का proper documentation और maintenance allocation

Total Resources Scanned: {len(set(v.resource_id for v in violations)) if violations else 0}
Total Violations Found: {len(violations)}
Critical Violations: {len([v for v in violations if v.policy.enforcement_level == TagEnforcementLevel.BLOCKING])}

COMPLIANCE OVERVIEW
==================
"""
            
            if violations:
                # Group violations by type
                violation_by_type = {}
                violation_by_policy = {}
                violation_by_resource_type = {}
                
                for violation in violations:
                    # By violation type
                    if violation.violation_type not in violation_by_type:
                        violation_by_type[violation.violation_type] = 0
                    violation_by_type[violation.violation_type] += 1
                    
                    # By policy
                    policy_name = violation.policy.tag_key
                    if policy_name not in violation_by_policy:
                        violation_by_policy[policy_name] = 0
                    violation_by_policy[policy_name] += 1
                    
                    # By resource type
                    if violation.resource_type not in violation_by_resource_type:
                        violation_by_resource_type[violation.resource_type] = 0
                    violation_by_resource_type[violation.resource_type] += 1
                
                report += f"""
VIOLATION BREAKDOWN:
"""
                
                # Violation types
                report += f"""
By Violation Type:
"""
                for vtype, count in sorted(violation_by_type.items()):
                    percentage = (count / len(violations)) * 100
                    report += f"  {vtype.replace('_', ' ').title()}: {count} ({percentage:.1f}%)\n"
                
                # Policy violations
                report += f"""
By Tag Policy:
"""
                for policy, count in sorted(violation_by_policy.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / len(violations)) * 100
                    report += f"  {policy}: {count} ({percentage:.1f}%)\n"
                
                # Resource type violations
                report += f"""
By Resource Type:
"""
                for rtype, count in sorted(violation_by_resource_type.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / len(violations)) * 100
                    report += f"  {rtype.title()}: {count} ({percentage:.1f}%)\n"
                
                # Top violations details
                report += f"""

TOP 10 CRITICAL VIOLATIONS
==========================
"""
                
                critical_violations = [v for v in violations 
                                     if v.policy.enforcement_level == TagEnforcementLevel.BLOCKING]
                critical_violations.sort(key=lambda x: x.discovered_at, reverse=True)
                
                for i, violation in enumerate(critical_violations[:10], 1):
                    report += f"""
{i}. Resource: {violation.resource_id.split('/')[-1]}
   Type: {violation.resource_type}
   Policy: {violation.policy.tag_key}
   Issue: {violation.violation_type.replace('_', ' ').title()}
   Current: {violation.current_value or 'None'}
   Expected: {violation.expected_value or 'See policy'}
   Enforcement: {violation.policy.enforcement_level.value}
"""
            
            # Cost allocation analysis
            cost_allocations = self.analyze_cost_allocation()
            
            if cost_allocations:
                report += f"""

COST ALLOCATION ANALYSIS
=======================
"""
                
                # Group by tag key
                allocation_by_tag = {}
                for allocation in cost_allocations:
                    if allocation.tag_key not in allocation_by_tag:
                        allocation_by_tag[allocation.tag_key] = []
                    allocation_by_tag[allocation.tag_key].append(allocation)
                
                for tag_key, allocations in allocation_by_tag.items():
                    total_cost = sum(a.monthly_cost for a in allocations)
                    report += f"""
{tag_key} Allocation (Total: ${total_cost:.2f}/month):
"""
                    
                    # Sort by cost and show top allocations
                    allocations.sort(key=lambda x: x.monthly_cost, reverse=True)
                    for allocation in allocations[:5]:  # Top 5
                        percentage = (allocation.monthly_cost / total_cost) * 100 if total_cost > 0 else 0
                        report += f"  {allocation.tag_value}: ${allocation.monthly_cost:.2f} ({percentage:.1f}%)\n"
                    
                    if len(allocations) > 5:
                        others_cost = sum(a.monthly_cost for a in allocations[5:])
                        others_percentage = (others_cost / total_cost) * 100 if total_cost > 0 else 0
                        report += f"  Others: ${others_cost:.2f} ({others_percentage:.1f}%)\n"
            
            # Mumbai context analysis
            report += f"""

MUMBAI CONTEXT ANALYSIS
=======================
Tag compliance आपके लिए बिल्कुल Mumbai society management जैसा है:

🏢 SOCIETY ANALOGY:
   - Proper tagging = हर flat का correct numbering और owner details
   - Cost allocation = Monthly maintenance का fair distribution
   - Compliance = Society rules का proper follow-up

📊 CURRENT STATUS:
"""
            
            if violations:
                compliance_rate = max(0, 100 - (len(violations) / 10))  # Simplified calculation
                if compliance_rate > 90:
                    report += "   ✅ EXCELLENT: Society में सब kuch properly documented है!\n"
                elif compliance_rate > 70:
                    report += "   👍 GOOD: Most resources properly tagged, कुछ छोटी issues हैं\n"
                elif compliance_rate > 50:
                    report += "   ⚠️  NEEDS IMPROVEMENT: Tag governance को serious attention चाहिए\n"
                else:
                    report += "   🚨 CRITICAL: Tag compliance very poor, immediate action required\n"
            
            report += f"""

REMEDIATION RECOMMENDATIONS
===========================
Priority Actions:

1. IMMEDIATE (0-1 week):
   - Fix all BLOCKING level violations
   - Implement auto-remediation for missing required tags
   - Set up alerting for new untagged resources

2. SHORT TERM (1-4 weeks):
   - Train teams on tagging policies
   - Implement tag enforcement in CI/CD pipelines
   - Set up cost allocation dashboards

3. LONG TERM (1-3 months):
   - Implement tag-based access controls
   - Automate cost optimization based on tags
   - Set up regular compliance auditing

AUTOMATION OPPORTUNITIES
========================
- Auto-tag EC2 instances from launch templates
- Inherit tags from parent resources (VPC → Subnets)
- Cost center assignment based on IAM roles
- Schedule-based resource management

COST IMPACT
===========
Proper tagging enables:
- 20-30% cost reduction through better allocation
- Automated resource cleanup (10-15% savings)
- Right-sizing based on usage patterns
- Better budget control and forecasting

NEXT STEPS
==========
1. Implement auto-remediation for {len([v for v in violations if v.policy.enforcement_level == TagEnforcementLevel.AUTO_REMEDIATE])} violations
2. Set up weekly compliance monitoring
3. Create team-specific tagging guidelines
4. Implement cost center approval workflows

Contact: Hindi Tech Community for tag governance implementation
"""
            
            logger.info("Generated comprehensive tag compliance report")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            return f"Error generating report: {e}"

# Usage Example
def main():
    """
    Production usage example
    
    Mumbai Context: Complete tag governance setup
    """
    try:
        # Initialize tag enforcement system
        print("🏷️  Initializing Tag Enforcement System...")
        tag_system = TagEnforcementSystem()
        
        print("🔍 Scanning resources for tag compliance...")
        
        # Scan for violations
        violations = asyncio.run(tag_system.scan_resources_for_compliance())
        
        if violations:
            print(f"\n⚠️  Found {len(violations)} tag compliance violations")
            
            # Group violations by severity
            blocking_violations = [v for v in violations if v.policy.enforcement_level == TagEnforcementLevel.BLOCKING]
            warning_violations = [v for v in violations if v.policy.enforcement_level == TagEnforcementLevel.WARNING]
            auto_remediable = [v for v in violations if v.policy.enforcement_level == TagEnforcementLevel.AUTO_REMEDIATE]
            
            print(f"🚨 Critical (Blocking): {len(blocking_violations)}")
            print(f"⚠️  Warnings: {len(warning_violations)}")
            print(f"🔧 Auto-remediable: {len(auto_remediable)}")
            
            # Auto-remediate where possible
            if auto_remediable:
                print(f"\n🔧 Attempting to auto-remediate {len(auto_remediable)} violations...")
                remediation_stats = asyncio.run(tag_system.remediate_violations(auto_remediable))
                print(f"✅ Successful: {remediation_stats['successful']}")
                print(f"❌ Failed: {remediation_stats['failed']}")
                print(f"⏭️  Skipped: {remediation_stats['skipped']}")
        else:
            print("✅ No tag compliance violations found!")
        
        # Analyze cost allocation
        print("\n💰 Analyzing cost allocation by tags...")
        cost_allocations = tag_system.analyze_cost_allocation()
        
        if cost_allocations:
            # Group by department
            dept_costs = {}
            for allocation in cost_allocations:
                if allocation.tag_key == "Department":
                    dept_costs[allocation.tag_value] = allocation.monthly_cost
            
            if dept_costs:
                print("\n🏢 Department-wise costs:")
                sorted_depts = sorted(dept_costs.items(), key=lambda x: x[1], reverse=True)
                for dept, cost in sorted_depts[:5]:
                    print(f"  {dept}: ${cost:.2f}/month")
        
        # Generate comprehensive report
        print("\n📄 Generating tag compliance report...")
        report = tag_system.generate_compliance_report(violations)
        
        # Save report
        with open('tag_compliance_report.txt', 'w') as f:
            f.write(report)
        
        print("✅ Tag compliance analysis completed!")
        print("📄 Report saved to tag_compliance_report.txt")
        
        # Show Mumbai style summary
        print(f"\n🏢 Mumbai Society Analogy Summary:")
        if len(violations) == 0:
            print("🌟 Perfect! आपका cloud resources सब properly documented हैं")
            print("   Like a well-managed Mumbai society with perfect records!")
        elif len(blocking_violations) == 0:
            print("👍 Good! कुछ minor issues हैं but critical problems नहीं")
            print("   Like society with good records but some pending paperwork")
        else:
            print(f"⚠️  {len(blocking_violations)} critical issues need immediate attention")
            print("   Like society with missing flat ownership documents - fix ASAP!")
        
        # Cost allocation insights
        total_allocated_cost = sum(a.monthly_cost for a in cost_allocations)
        if total_allocated_cost > 0:
            print(f"\n💰 Monthly cost tracked: ${total_allocated_cost:.2f}")
            print("   Proper tagging = better cost control!")
        
    except Exception as e:
        logger.error(f"Tag compliance analysis failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

"""
Production Implementation Guide (Hindi):
========================================

1. Policy Management:
   - Central policy repository (Git/Database)
   - Policy versioning and change management
   - Environment-specific policy variations
   - Approval workflows for policy changes

2. Automation Integration:
   - CloudFormation/Terraform tag enforcement
   - CI/CD pipeline integration
   - Auto-tagging Lambda functions
   - Resource lifecycle management

3. Mumbai Business Context:
   - Department mapping (Engineering=Tech team, Marketing=Business team)
   - Cost center alignment with company structure
   - Project-based resource grouping
   - Compliance with local audit requirements

4. Monitoring & Alerting:
   - Real-time compliance dashboard
   - Slack/Email notifications for violations
   - Cost anomaly detection by tags
   - Weekly compliance reports

5. Access Controls:
   - Tag-based IAM policies
   - Resource access based on department tags
   - Cost approval workflows by tag values
   - Audit trail for tag changes

यह system आपके cloud governance को Mumbai society के efficient management जैसा structured बनाएगा!
"""
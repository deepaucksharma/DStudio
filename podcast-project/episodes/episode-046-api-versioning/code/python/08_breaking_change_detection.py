#!/usr/bin/env python3
"""
Breaking Change Detection System for API Evolution
Inspired by Ola's API evolution monitoring to prevent partner app breakage

Example: Ola ne kaise detect kiya ki koi change driver/rider apps ko break kar dega
"""

import json
import jsonschema
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from deepdiff import DeepDiff
import yaml
import re
from datetime import datetime

class ChangeType(Enum):
    """Types of API changes"""
    BREAKING = "breaking"
    NON_BREAKING = "non_breaking"
    POTENTIALLY_BREAKING = "potentially_breaking"
    UNKNOWN = "unknown"

class ChangeCategory(Enum):
    """Categories of changes"""
    SCHEMA_CHANGE = "schema_change"
    FIELD_REMOVAL = "field_removal"
    FIELD_TYPE_CHANGE = "field_type_change"
    REQUIRED_FIELD_ADDED = "required_field_added"
    ENUM_VALUE_REMOVED = "enum_value_removed"
    RESPONSE_FORMAT_CHANGE = "response_format_change"
    ERROR_CODE_CHANGE = "error_code_change"

@dataclass
class APIChange:
    """Represents a single API change"""
    category: ChangeCategory
    change_type: ChangeType
    field_path: str
    old_value: Any
    new_value: Any
    description: str
    impact_assessment: str
    recommendation: str

@dataclass
class BreakingChangeReport:
    """Complete breaking change analysis report"""
    api_name: str
    old_version: str
    new_version: str
    analysis_timestamp: str
    total_changes: int
    breaking_changes: List[APIChange]
    potentially_breaking: List[APIChange]
    safe_changes: List[APIChange]
    risk_score: float  # 0-10 scale
    compatibility_assessment: str

class BreakingChangeDetector:
    """
    Detect breaking changes in API evolution
    Ola style change detection for partner APIs
    """
    
    def __init__(self):
        self.breaking_change_rules = self._initialize_breaking_change_rules()
    
    def _initialize_breaking_change_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize rules for detecting breaking changes"""
        return {
            "field_removal": {
                "severity": "breaking",
                "description": "Field removed from response",
                "pattern": r"dictionary_item_removed",
                "impact": "Clients depending on this field will break"
            },
            "field_type_change": {
                "severity": "breaking", 
                "description": "Field type changed",
                "pattern": r"type_changes",
                "impact": "Type casting and validation will fail"
            },
            "required_field_added": {
                "severity": "breaking",
                "description": "New required field added to request",
                "pattern": r"required.*added",
                "impact": "Existing requests will fail validation"
            },
            "enum_value_removed": {
                "severity": "breaking",
                "description": "Enum value removed",
                "pattern": r"enum.*removed",
                "impact": "Requests with removed values will be rejected"
            },
            "field_added": {
                "severity": "non_breaking",
                "description": "New optional field added",
                "pattern": r"dictionary_item_added",
                "impact": "Backward compatible addition"
            },
            "enum_value_added": {
                "severity": "potentially_breaking",
                "description": "New enum value added",
                "pattern": r"enum.*added",
                "impact": "May break clients with strict validation"
            }
        }
    
    def analyze_schema_changes(self, old_schema: Dict[str, Any], 
                             new_schema: Dict[str, Any],
                             api_name: str = "Ola API") -> BreakingChangeReport:
        """
        Analyze changes between two API schemas
        """
        # Compare schemas using deep diff
        diff = DeepDiff(old_schema, new_schema, verbose_level=2)
        
        changes = []
        breaking_changes = []
        potentially_breaking = []
        safe_changes = []
        
        # Analyze different types of changes
        changes.extend(self._analyze_removed_fields(diff))
        changes.extend(self._analyze_added_fields(diff))
        changes.extend(self._analyze_type_changes(diff))
        changes.extend(self._analyze_value_changes(diff))
        
        # Categorize changes
        for change in changes:
            if change.change_type == ChangeType.BREAKING:
                breaking_changes.append(change)
            elif change.change_type == ChangeType.POTENTIALLY_BREAKING:
                potentially_breaking.append(change)
            else:
                safe_changes.append(change)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(breaking_changes, potentially_breaking)
        
        # Generate compatibility assessment
        compatibility_assessment = self._generate_compatibility_assessment(
            breaking_changes, potentially_breaking, safe_changes
        )
        
        return BreakingChangeReport(
            api_name=api_name,
            old_version="Previous",
            new_version="Current",
            analysis_timestamp=datetime.now().isoformat(),
            total_changes=len(changes),
            breaking_changes=breaking_changes,
            potentially_breaking=potentially_breaking,
            safe_changes=safe_changes,
            risk_score=risk_score,
            compatibility_assessment=compatibility_assessment
        )
    
    def _analyze_removed_fields(self, diff: DeepDiff) -> List[APIChange]:
        """Analyze removed fields"""
        changes = []
        
        removed_items = diff.get('dictionary_item_removed', [])
        for removed_item in removed_items:
            # Extract field path
            field_path = str(removed_item).replace("root", "").strip("[]'")
            
            # Determine if this is a breaking change
            is_breaking = self._is_field_removal_breaking(field_path)
            
            changes.append(APIChange(
                category=ChangeCategory.FIELD_REMOVAL,
                change_type=ChangeType.BREAKING if is_breaking else ChangeType.NON_BREAKING,
                field_path=field_path,
                old_value="Present",
                new_value="Removed",
                description=f"Field '{field_path}' was removed from the API",
                impact_assessment="High impact - Ola driver apps may crash if they depend on this field",
                recommendation="Keep field with deprecation warning or provide migration path"
            ))
        
        return changes
    
    def _analyze_added_fields(self, diff: DeepDiff) -> List[APIChange]:
        """Analyze added fields"""
        changes = []
        
        added_items = diff.get('dictionary_item_added', [])
        for added_item in added_items:
            field_path = str(added_item).replace("root", "").strip("[]'")
            
            changes.append(APIChange(
                category=ChangeCategory.SCHEMA_CHANGE,
                change_type=ChangeType.NON_BREAKING,
                field_path=field_path,
                old_value="Not Present",
                new_value="Added",
                description=f"New field '{field_path}' added to the API",
                impact_assessment="Low impact - Backward compatible addition",
                recommendation="Safe to deploy, but document the new field"
            ))
        
        return changes
    
    def _analyze_type_changes(self, diff: DeepDiff) -> List[APIChange]:
        """Analyze field type changes"""
        changes = []
        
        type_changes = diff.get('type_changes', {})
        for path, change_info in type_changes.items():
            field_path = str(path).replace("root", "").strip("[]'")
            old_type = change_info.get('old_type', 'Unknown')
            new_type = change_info.get('new_type', 'Unknown')
            
            changes.append(APIChange(
                category=ChangeCategory.FIELD_TYPE_CHANGE,
                change_type=ChangeType.BREAKING,
                field_path=field_path,
                old_value=str(old_type),
                new_value=str(new_type),
                description=f"Field '{field_path}' type changed from {old_type} to {new_type}",
                impact_assessment="Critical impact - Type conversion will fail in partner apps",
                recommendation="Avoid type changes or introduce new field with different name"
            ))
        
        return changes
    
    def _analyze_value_changes(self, diff: DeepDiff) -> List[APIChange]:
        """Analyze value changes"""
        changes = []
        
        value_changes = diff.get('values_changed', {})
        for path, change_info in value_changes.items():
            field_path = str(path).replace("root", "").strip("[]'")
            old_value = change_info.get('old_value')
            new_value = change_info.get('new_value')
            
            # Determine change type based on context
            change_type = self._classify_value_change(field_path, old_value, new_value)
            
            changes.append(APIChange(
                category=ChangeCategory.SCHEMA_CHANGE,
                change_type=change_type,
                field_path=field_path,
                old_value=str(old_value),
                new_value=str(new_value),
                description=f"Field '{field_path}' value changed",
                impact_assessment=self._assess_value_change_impact(change_type),
                recommendation=self._recommend_value_change_action(change_type)
            ))
        
        return changes
    
    def _is_field_removal_breaking(self, field_path: str) -> bool:
        """Determine if field removal is breaking"""
        # Critical fields for Ola that should never be removed
        critical_fields = [
            'driver_id', 'ride_id', 'booking_id', 'passenger_id',
            'fare', 'payment_status', 'ride_status', 'location',
            'estimated_time', 'vehicle_details'
        ]
        
        for critical_field in critical_fields:
            if critical_field in field_path.lower():
                return True
        
        return True  # Assume breaking by default for safety
    
    def _classify_value_change(self, field_path: str, old_value: Any, new_value: Any) -> ChangeType:
        """Classify the type of value change"""
        
        # Check if it's an enum change
        if isinstance(old_value, list) and isinstance(new_value, list):
            old_set = set(old_value)
            new_set = set(new_value)
            
            if old_set - new_set:  # Values removed
                return ChangeType.BREAKING
            elif new_set - old_set:  # Values added
                return ChangeType.POTENTIALLY_BREAKING
        
        # Check for URL or endpoint changes
        if 'url' in field_path.lower() or 'endpoint' in field_path.lower():
            return ChangeType.BREAKING
        
        # Version number changes
        if 'version' in field_path.lower():
            return ChangeType.NON_BREAKING
        
        return ChangeType.POTENTIALLY_BREAKING
    
    def _assess_value_change_impact(self, change_type: ChangeType) -> str:
        """Assess impact of value changes"""
        impact_map = {
            ChangeType.BREAKING: "Critical impact - Will break existing integrations",
            ChangeType.POTENTIALLY_BREAKING: "Medium impact - May affect some partner implementations",
            ChangeType.NON_BREAKING: "Low impact - Safe change with minimal risk"
        }
        return impact_map.get(change_type, "Unknown impact")
    
    def _recommend_value_change_action(self, change_type: ChangeType) -> str:
        """Recommend action for value changes"""
        recommendation_map = {
            ChangeType.BREAKING: "Avoid this change or provide migration path with version bump",
            ChangeType.POTENTIALLY_BREAKING: "Test with major partners before deploying",
            ChangeType.NON_BREAKING: "Safe to deploy with proper documentation"
        }
        return recommendation_map.get(change_type, "Review manually")
    
    def _calculate_risk_score(self, breaking_changes: List[APIChange], 
                            potentially_breaking: List[APIChange]) -> float:
        """Calculate overall risk score (0-10 scale)"""
        base_score = 0.0
        
        # Breaking changes contribute heavily to risk
        base_score += len(breaking_changes) * 3.0
        
        # Potentially breaking changes contribute moderately
        base_score += len(potentially_breaking) * 1.5
        
        # Cap at 10.0
        return min(base_score, 10.0)
    
    def _generate_compatibility_assessment(self, breaking_changes: List[APIChange],
                                         potentially_breaking: List[APIChange],
                                         safe_changes: List[APIChange]) -> str:
        """Generate overall compatibility assessment"""
        
        if len(breaking_changes) > 0:
            return "❌ NOT COMPATIBLE - Contains breaking changes that will impact partner apps"
        elif len(potentially_breaking) > 3:
            return "⚠️  RISKY - Multiple potentially breaking changes require testing"
        elif len(potentially_breaking) > 0:
            return "🟡 CAUTION - Some changes may affect partner implementations"
        else:
            return "✅ COMPATIBLE - All changes are backward compatible"

# Example schemas for demonstration
def get_ola_api_v1_schema():
    """Ola API v1 schema - basic ride booking"""
    return {
        "type": "object",
        "properties": {
            "ride_id": {"type": "string"},
            "driver_id": {"type": "string"},
            "passenger_id": {"type": "string"},
            "status": {
                "type": "string", 
                "enum": ["requested", "assigned", "started", "completed", "cancelled"]
            },
            "fare": {"type": "number"},
            "vehicle_type": {
                "type": "string",
                "enum": ["micro", "mini", "prime", "lux"]
            },
            "pickup_location": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "address": {"type": "string"}
                },
                "required": ["latitude", "longitude"]
            },
            "drop_location": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "address": {"type": "string"}
                },
                "required": ["latitude", "longitude"]
            }
        },
        "required": ["ride_id", "driver_id", "passenger_id", "status", "fare"]
    }

def get_ola_api_v2_schema():
    """Ola API v2 schema - with some breaking changes for demonstration"""
    return {
        "type": "object",
        "properties": {
            "ride_id": {"type": "string"},
            "driver_id": {"type": "string"},
            "passenger_id": {"type": "string"},
            "status": {
                "type": "string",
                # BREAKING: Removed "cancelled" status
                "enum": ["requested", "assigned", "started", "completed", "no_show"]  # Added new status
            },
            "fare": {"type": "number"},
            "vehicle_type": {
                "type": "string",
                "enum": ["micro", "mini", "prime", "lux", "electric"]  # Added new type
            },
            # BREAKING: Changed fare from number to object
            "fare_breakdown": {
                "type": "object",
                "properties": {
                    "base_fare": {"type": "number"},
                    "distance_fare": {"type": "number"},
                    "time_fare": {"type": "number"},
                    "total": {"type": "number"}
                },
                "required": ["base_fare", "total"]
            },
            "pickup_location": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "address": {"type": "string"},
                    "landmark": {"type": "string"}  # New optional field
                },
                "required": ["latitude", "longitude"]
            },
            "drop_location": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "address": {"type": "string"}
                },
                "required": ["latitude", "longitude"]
            },
            # New fields
            "estimated_arrival_time": {"type": "string"},
            "driver_rating": {"type": "number"},
            # BREAKING: New required field
            "payment_method": {"type": "string", "enum": ["cash", "wallet", "card", "upi"]}
        },
        # BREAKING: Added new required field
        "required": ["ride_id", "driver_id", "passenger_id", "status", "fare_breakdown", "payment_method"]
    }

def demonstrate_breaking_change_detection():
    """
    Demonstrate breaking change detection with Ola API evolution
    """
    print("🔥 Breaking Change Detection - Ola API Evolution")
    print("=" * 60)
    
    detector = BreakingChangeDetector()
    
    # Get API schemas
    old_schema = get_ola_api_v1_schema()
    new_schema = get_ola_api_v2_schema()
    
    print("\n📊 Analyzing API Schema Changes...")
    print("Old Schema: Ola API v1 (Basic ride booking)")
    print("New Schema: Ola API v2 (Enhanced with fare breakdown)")
    
    # Analyze changes
    report = detector.analyze_schema_changes(old_schema, new_schema, "Ola Ride Booking API")
    
    print(f"\n📋 Analysis Results:")
    print(f"Total Changes Detected: {report.total_changes}")
    print(f"Breaking Changes: {len(report.breaking_changes)}")
    print(f"Potentially Breaking: {len(report.potentially_breaking)}")
    print(f"Safe Changes: {len(report.safe_changes)}")
    print(f"Risk Score: {report.risk_score}/10.0")
    print(f"Compatibility: {report.compatibility_assessment}")
    
    # Detail breaking changes
    if report.breaking_changes:
        print("\n🚨 Breaking Changes Detected:")
        for i, change in enumerate(report.breaking_changes, 1):
            print(f"\n{i}. {change.category.value.title()}")
            print(f"   Field: {change.field_path}")
            print(f"   Change: {change.old_value} → {change.new_value}")
            print(f"   Description: {change.description}")
            print(f"   Impact: {change.impact_assessment}")
            print(f"   Recommendation: {change.recommendation}")
    
    # Detail potentially breaking changes
    if report.potentially_breaking:
        print("\n⚠️  Potentially Breaking Changes:")
        for i, change in enumerate(report.potentially_breaking, 1):
            print(f"\n{i}. {change.field_path}")
            print(f"   Description: {change.description}")
            print(f"   Recommendation: {change.recommendation}")
    
    # Safe changes
    if report.safe_changes:
        print(f"\n✅ Safe Changes ({len(report.safe_changes)}):")
        for change in report.safe_changes:
            print(f"   + {change.field_path}: {change.description}")
    
    print("\n🎯 Recommendations for Ola:")
    print("1. 🚫 Do not deploy - contains breaking changes")
    print("2. 🔄 Create migration plan for partner apps")
    print("3. 📢 Notify partners 6 weeks in advance")
    print("4. 🧪 Provide sandbox environment for testing")
    print("5. 📊 Monitor partner app crash rates post-deployment")
    
    print("\n💡 Breaking Change Prevention Tips:")
    print("1. Use additive-only changes when possible")
    print("2. Deprecate before removing fields")
    print("3. Maintain backward compatibility for 2+ versions")
    print("4. Use feature flags for risky changes")
    print("5. Implement automated breaking change detection in CI/CD")

def generate_change_report_json(report: BreakingChangeReport) -> str:
    """Generate JSON report for integration with CI/CD systems"""
    
    def convert_change_to_dict(change: APIChange) -> Dict[str, Any]:
        return {
            "category": change.category.value,
            "change_type": change.change_type.value,
            "field_path": change.field_path,
            "old_value": change.old_value,
            "new_value": change.new_value,
            "description": change.description,
            "impact_assessment": change.impact_assessment,
            "recommendation": change.recommendation
        }
    
    report_dict = {
        "api_name": report.api_name,
        "old_version": report.old_version,
        "new_version": report.new_version,
        "analysis_timestamp": report.analysis_timestamp,
        "summary": {
            "total_changes": report.total_changes,
            "breaking_changes": len(report.breaking_changes),
            "potentially_breaking": len(report.potentially_breaking),
            "safe_changes": len(report.safe_changes),
            "risk_score": report.risk_score,
            "compatibility_assessment": report.compatibility_assessment
        },
        "changes": {
            "breaking": [convert_change_to_dict(c) for c in report.breaking_changes],
            "potentially_breaking": [convert_change_to_dict(c) for c in report.potentially_breaking],
            "safe": [convert_change_to_dict(c) for c in report.safe_changes]
        },
        "deployment_recommendation": "BLOCK" if report.breaking_changes else "PROCEED_WITH_CAUTION"
    }
    
    return json.dumps(report_dict, indent=2)

if __name__ == "__main__":
    # Run demonstration
    demonstrate_breaking_change_detection()
    
    # Example of integration with CI/CD
    print("\n" + "="*60)
    print("🔧 CI/CD Integration Example:")
    
    detector = BreakingChangeDetector()
    old_schema = get_ola_api_v1_schema()
    new_schema = get_ola_api_v2_schema()
    
    report = detector.analyze_schema_changes(old_schema, new_schema)
    
    # Generate JSON report
    json_report = generate_change_report_json(report)
    print("JSON Report generated for CI/CD system:")
    print(json_report[:500] + "..." if len(json_report) > 500 else json_report)
    
    # Exit with appropriate code for CI/CD
    if report.breaking_changes:
        print("\n❌ CI/CD Pipeline should FAIL - Breaking changes detected")
        exit(1)
    else:
        print("\n✅ CI/CD Pipeline can PROCEED - No breaking changes")
        exit(0)
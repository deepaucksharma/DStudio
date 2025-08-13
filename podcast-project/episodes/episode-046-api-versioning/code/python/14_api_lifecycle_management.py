"""
API Lifecycle Management System
एपीआई लाइफसाइकिल मैनेजमेंट सिस्टम

Real-world example: IRCTC API lifecycle management
Handles version lifecycle from development to deprecation and sunset
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import asyncio
import logging

class LifecycleStage(Enum):
    """API lifecycle stages - एपीआई लाइफसाइकिल स्टेज"""
    DEVELOPMENT = "development"
    ALPHA = "alpha"
    BETA = "beta"
    RELEASE_CANDIDATE = "release_candidate"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"

class ApiHealth(Enum):
    """API health status - एपीआई हेल्थ स्टेटस"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"

@dataclass
class VersionMetrics:
    """Version performance metrics - वर्जन परफॉर्मेंस मेट्रिक्स"""
    requests_per_day: int = 0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    error_count: int = 0
    unique_clients: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ClientUsage:
    """Client usage information - क्लाइंट यूसेज इन्फॉर्मेशन"""
    client_id: str
    client_name: str
    current_version: str
    daily_requests: int
    last_seen: datetime
    migration_status: str  # pending, in_progress, completed

@dataclass
class ApiVersionLifecycle:
    """API version lifecycle information - एपीआई वर्जन लाइफसाइकिल जानकारी"""
    version: str
    stage: LifecycleStage
    health: ApiHealth
    created_at: datetime
    stage_changed_at: datetime
    deprecation_date: Optional[datetime] = None
    sunset_date: Optional[datetime] = None
    metrics: VersionMetrics = field(default_factory=VersionMetrics)
    clients: List[ClientUsage] = field(default_factory=list)
    migration_deadline: Optional[datetime] = None
    support_contact: str = ""

class IRCTCApiLifecycleManager:
    """
    IRCTC API Lifecycle Manager
    IRCTC एपीआई लाइफसाइकिल मैनेजर
    
    Manages complete API lifecycle from development to sunset
    """
    
    def __init__(self):
        self.versions: Dict[str, ApiVersionLifecycle] = {}
        self.notification_rules: Dict[LifecycleStage, List[str]] = {}
        self.migration_templates: Dict[str, Dict] = {}
        self.setup_notification_rules()
        self.setup_migration_templates()
        
    def setup_notification_rules(self):
        """Setup notification rules - नोटिफिकेशन रूल सेटअप करें"""
        self.notification_rules = {
            LifecycleStage.ALPHA: ["development-team", "qa-team"],
            LifecycleStage.BETA: ["development-team", "qa-team", "beta-testers"],
            LifecycleStage.DEPRECATED: ["all-clients", "support-team"],
            LifecycleStage.SUNSET: ["all-clients", "support-team", "management"]
        }
        
    def setup_migration_templates(self):
        """Setup migration templates - माइग्रेशन टेम्प्लेट सेटअप करें"""
        self.migration_templates = {
            "train_booking": {
                "v1_to_v2": {
                    "changes": [
                        "PNR format changed from 10 digits to 12 digits",
                        "New passenger verification required",
                        "Enhanced seat preference options"
                    ],
                    "code_examples": {
                        "old": "book_train(pnr='1234567890')",
                        "new": "book_train(pnr='123456789012', verification=True)"
                    }
                }
            }
        }
    
    def create_version(self, version: str, stage: LifecycleStage = LifecycleStage.DEVELOPMENT) -> ApiVersionLifecycle:
        """
        Create new API version
        नया एपीआई वर्जन बनाएं
        """
        now = datetime.now()
        
        lifecycle = ApiVersionLifecycle(
            version=version,
            stage=stage,
            health=ApiHealth.HEALTHY,
            created_at=now,
            stage_changed_at=now,
            support_contact="api-support@irctc.co.in"
        )
        
        self.versions[version] = lifecycle
        
        print(f"📱 Created API version {version} in {stage.value} stage")
        self.send_notifications(version, f"New API version {version} created")
        
        return lifecycle
    
    def promote_version(self, version: str, target_stage: LifecycleStage) -> bool:
        """
        Promote version to next lifecycle stage
        वर्जन को अगले लाइफसाइकिल स्टेज में प्रोमोट करें
        """
        if version not in self.versions:
            print(f"❌ Version {version} not found")
            return False
            
        lifecycle = self.versions[version]
        current_stage = lifecycle.stage
        
        # Validate promotion path
        if not self.validate_promotion(current_stage, target_stage):
            print(f"❌ Invalid promotion from {current_stage.value} to {target_stage.value}")
            return False
            
        # Check promotion criteria
        if not self.check_promotion_criteria(version, target_stage):
            print(f"❌ Promotion criteria not met for {version}")
            return False
            
        # Update lifecycle
        lifecycle.stage = target_stage
        lifecycle.stage_changed_at = datetime.now()
        
        # Set dates based on stage
        if target_stage == LifecycleStage.DEPRECATED:
            lifecycle.deprecation_date = datetime.now()
            lifecycle.sunset_date = datetime.now() + timedelta(days=180)  # 6 months
            lifecycle.migration_deadline = datetime.now() + timedelta(days=150)  # 5 months
            
        print(f"🚀 Promoted {version} from {current_stage.value} to {target_stage.value}")
        self.send_notifications(version, f"API version {version} promoted to {target_stage.value}")
        
        return True
    
    def validate_promotion(self, current: LifecycleStage, target: LifecycleStage) -> bool:
        """Validate promotion path - प्रोमोशन पाथ वैलिडेट करें"""
        valid_transitions = {
            LifecycleStage.DEVELOPMENT: [LifecycleStage.ALPHA],
            LifecycleStage.ALPHA: [LifecycleStage.BETA, LifecycleStage.DEVELOPMENT],
            LifecycleStage.BETA: [LifecycleStage.RELEASE_CANDIDATE, LifecycleStage.ALPHA],
            LifecycleStage.RELEASE_CANDIDATE: [LifecycleStage.STABLE, LifecycleStage.BETA],
            LifecycleStage.STABLE: [LifecycleStage.DEPRECATED],
            LifecycleStage.DEPRECATED: [LifecycleStage.SUNSET],
        }
        
        return target in valid_transitions.get(current, [])
    
    def check_promotion_criteria(self, version: str, target_stage: LifecycleStage) -> bool:
        """Check if promotion criteria are met - प्रोमोशन क्राइटेरिया चेक करें"""
        lifecycle = self.versions[version]
        
        criteria_map = {
            LifecycleStage.ALPHA: lambda: True,  # No criteria for alpha
            LifecycleStage.BETA: lambda: lifecycle.health == ApiHealth.HEALTHY,
            LifecycleStage.RELEASE_CANDIDATE: lambda: (
                lifecycle.metrics.success_rate >= 99.0 and
                lifecycle.metrics.avg_response_time < 200
            ),
            LifecycleStage.STABLE: lambda: (
                lifecycle.metrics.success_rate >= 99.9 and
                lifecycle.metrics.avg_response_time < 100 and
                len(lifecycle.clients) >= 5  # At least 5 beta clients
            ),
            LifecycleStage.DEPRECATED: lambda: True,  # Can always deprecate
            LifecycleStage.SUNSET: lambda: (
                datetime.now() > lifecycle.migration_deadline if lifecycle.migration_deadline else False
            )
        }
        
        return criteria_map.get(target_stage, lambda: False)()
    
    def update_metrics(self, version: str, metrics: VersionMetrics):
        """Update version metrics - वर्जन मेट्रिक्स अपडेट करें"""
        if version not in self.versions:
            print(f"❌ Version {version} not found")
            return
            
        self.versions[version].metrics = metrics
        
        # Auto-detect health issues
        if metrics.success_rate < 95.0:
            self.versions[version].health = ApiHealth.DEGRADED
        elif metrics.success_rate < 90.0:
            self.versions[version].health = ApiHealth.UNHEALTHY
        else:
            self.versions[version].health = ApiHealth.HEALTHY
            
        print(f"📊 Updated metrics for {version}: {metrics.success_rate:.1f}% success rate")
    
    def register_client(self, version: str, client: ClientUsage):
        """Register client usage - क्लाइंट यूसेज रजिस्टर करें"""
        if version not in self.versions:
            print(f"❌ Version {version} not found")
            return
            
        # Check if client already exists
        for i, existing_client in enumerate(self.versions[version].clients):
            if existing_client.client_id == client.client_id:
                self.versions[version].clients[i] = client
                return
                
        self.versions[version].clients.append(client)
        print(f"👥 Registered client {client.client_name} for version {version}")
    
    def get_migration_plan(self, from_version: str, to_version: str) -> Dict:
        """
        Generate migration plan
        माइग्रेशन प्लान जेनरेट करें
        """
        if from_version not in self.versions or to_version not in self.versions:
            return {"error": "Version not found"}
            
        from_lifecycle = self.versions[from_version]
        to_lifecycle = self.versions[to_version]
        
        plan = {
            "from_version": from_version,
            "to_version": to_version,
            "migration_deadline": from_lifecycle.migration_deadline.isoformat() if from_lifecycle.migration_deadline else None,
            "affected_clients": len(from_lifecycle.clients),
            "estimated_effort": self.estimate_migration_effort(from_version, to_version),
            "steps": [],
            "risks": [],
            "rollback_plan": {},
            "timeline": {}
        }
        
        # Add version-specific migration steps
        template_key = f"{from_version}_to_{to_version}"
        if template_key in self.migration_templates.get("train_booking", {}):
            template = self.migration_templates["train_booking"][template_key]
            plan["steps"] = template.get("changes", [])
            plan["code_examples"] = template.get("code_examples", {})
            
        # Add timeline
        plan["timeline"] = {
            "preparation": "2 weeks",
            "testing": "2 weeks", 
            "gradual_rollout": "4 weeks",
            "full_migration": "8 weeks"
        }
        
        # Add risks
        plan["risks"] = [
            "Client compatibility issues",
            "Performance degradation during migration",
            "Data format inconsistencies"
        ]
        
        return plan
    
    def estimate_migration_effort(self, from_version: str, to_version: str) -> str:
        """Estimate migration effort - माइग्रेशन एफर्ट एस्टिमेट करें"""
        from_major = int(from_version.split('.')[0])
        to_major = int(to_version.split('.')[0])
        
        if from_major != to_major:
            return "High - Major version change requires significant updates"
        elif from_version != to_version:
            return "Medium - Minor version changes with backward compatibility"
        else:
            return "Low - Patch version with minimal changes"
    
    def send_notifications(self, version: str, message: str):
        """Send notifications - नोटिफिकेशन भेजें"""
        lifecycle = self.versions[version]
        recipients = self.notification_rules.get(lifecycle.stage, [])
        
        for recipient in recipients:
            print(f"📧 Notification to {recipient}: {message}")
            
        # Special notifications for deprecated/sunset
        if lifecycle.stage in [LifecycleStage.DEPRECATED, LifecycleStage.SUNSET]:
            for client in lifecycle.clients:
                print(f"📱 SMS to {client.client_name}: {message}")
    
    def generate_lifecycle_report(self) -> Dict:
        """
        Generate comprehensive lifecycle report
        व्यापक लाइफसाइकिल रिपोर्ट जेनरेट करें
        """
        report = {
            "summary": {
                "total_versions": len(self.versions),
                "by_stage": {},
                "by_health": {},
                "deprecated_versions": [],
                "sunset_versions": []
            },
            "versions": {}
        }
        
        # Collect statistics
        for version, lifecycle in self.versions.items():
            stage = lifecycle.stage.value
            health = lifecycle.health.value
            
            report["summary"]["by_stage"][stage] = report["summary"]["by_stage"].get(stage, 0) + 1
            report["summary"]["by_health"][health] = report["summary"]["by_health"].get(health, 0) + 1
            
            if lifecycle.stage == LifecycleStage.DEPRECATED:
                report["summary"]["deprecated_versions"].append(version)
            elif lifecycle.stage == LifecycleStage.SUNSET:
                report["summary"]["sunset_versions"].append(version)
                
            # Version details
            report["versions"][version] = {
                "stage": stage,
                "health": health,
                "created": lifecycle.created_at.isoformat(),
                "metrics": {
                    "daily_requests": lifecycle.metrics.requests_per_day,
                    "success_rate": lifecycle.metrics.success_rate,
                    "response_time": lifecycle.metrics.avg_response_time,
                    "client_count": len(lifecycle.clients)
                }
            }
            
            if lifecycle.deprecation_date:
                report["versions"][version]["deprecation_date"] = lifecycle.deprecation_date.isoformat()
            if lifecycle.sunset_date:
                report["versions"][version]["sunset_date"] = lifecycle.sunset_date.isoformat()
                
        return report

async def main():
    """
    Main demonstration function
    मुख्य प्रदर्शन फ़ंक्शन
    """
    print("🚂 IRCTC API Lifecycle Management Demo")
    print("=" * 50)
    
    manager = IRCTCApiLifecycleManager()
    
    # Create API versions
    print("\n🏗️ Creating API versions...")
    v1 = manager.create_version("1.0.0", LifecycleStage.STABLE)
    v2 = manager.create_version("2.0.0", LifecycleStage.BETA)
    v3 = manager.create_version("3.0.0", LifecycleStage.DEVELOPMENT)
    
    # Add some metrics
    print("\n📊 Updating metrics...")
    manager.update_metrics("1.0.0", VersionMetrics(
        requests_per_day=50000,
        success_rate=99.5,
        avg_response_time=150,
        error_count=250,
        unique_clients=1500
    ))
    
    manager.update_metrics("2.0.0", VersionMetrics(
        requests_per_day=15000,
        success_rate=98.8,
        avg_response_time=120,
        error_count=180,
        unique_clients=200
    ))
    
    # Register some clients
    print("\n👥 Registering clients...")
    clients = [
        ClientUsage("client_1", "MakeMyTrip", "1.0.0", 10000, datetime.now(), "pending"),
        ClientUsage("client_2", "Goibibo", "1.0.0", 8000, datetime.now(), "in_progress"),
        ClientUsage("client_3", "Yatra", "2.0.0", 5000, datetime.now(), "completed"),
        ClientUsage("client_4", "RedBus", "1.0.0", 3000, datetime.now(), "pending")
    ]
    
    for client in clients:
        manager.register_client(client.current_version, client)
    
    # Promote versions
    print("\n🚀 Promoting versions...")
    manager.promote_version("3.0.0", LifecycleStage.ALPHA)
    manager.promote_version("2.0.0", LifecycleStage.RELEASE_CANDIDATE)
    manager.promote_version("1.0.0", LifecycleStage.DEPRECATED)
    
    # Generate migration plan
    print("\n📋 Migration Plan (v1.0.0 → v2.0.0):")
    migration_plan = manager.get_migration_plan("1.0.0", "2.0.0")
    print(json.dumps(migration_plan, indent=2))
    
    # Generate lifecycle report
    print("\n📊 Lifecycle Report:")
    report = manager.generate_lifecycle_report()
    print(json.dumps(report, indent=2))
    
    # Check sunset requirements
    print("\n🌅 Sunset Analysis:")
    for version, lifecycle in manager.versions.items():
        if lifecycle.stage == LifecycleStage.DEPRECATED:
            if lifecycle.sunset_date:
                days_until_sunset = (lifecycle.sunset_date - datetime.now()).days
                print(f"  {version}: {days_until_sunset} days until sunset")
                
                # Check client migration status
                pending_migrations = [c for c in lifecycle.clients if c.migration_status == "pending"]
                if pending_migrations:
                    print(f"    ⚠️ {len(pending_migrations)} clients still need to migrate")
                    for client in pending_migrations[:3]:  # Show first 3
                        print(f"      - {client.client_name} ({client.daily_requests} daily requests)")

if __name__ == "__main__":
    asyncio.run(main())
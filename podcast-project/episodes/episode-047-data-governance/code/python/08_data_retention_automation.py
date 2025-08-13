"""
Data Retention Automation System
डेटा रिटेंशन ऑटोमेशन सिस्टम

Real-world example: Aadhaar data retention system
Handles automated data deletion based on retention policies and compliance requirements
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import asyncio
import hashlib
import logging

class RetentionPolicy(Enum):
    """Data retention policies - डेटा रिटेंशन पॉलिसियां"""
    IMMEDIATE = "immediate"  # Delete immediately after use
    SHORT_TERM = "short_term"  # 30 days
    MEDIUM_TERM = "medium_term"  # 1 year
    LONG_TERM = "long_term"  # 7 years
    PERMANENT = "permanent"  # Keep forever
    LEGAL_HOLD = "legal_hold"  # On legal hold

class DataClassification(Enum):
    """Data classification levels - डेटा वर्गीकरण स्तर"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"  # Personally Identifiable Information
    FINANCIAL = "financial"
    HEALTH = "health"

@dataclass
class DataRecord:
    """Individual data record - व्यक्तिगत डेटा रिकॉर्ड"""
    record_id: str
    data_type: str
    classification: DataClassification
    created_at: datetime
    last_accessed: datetime
    retention_policy: RetentionPolicy
    legal_hold: bool = False
    deletion_scheduled: Optional[datetime] = None
    anonymized: bool = False
    consent_id: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class RetentionRule:
    """Data retention rule - डेटा रिटेंशन नियम"""
    rule_id: str
    data_types: Set[str]
    classification: DataClassification
    retention_period: timedelta
    action: str  # delete, anonymize, archive
    jurisdiction: str  # IN (India), EU, US, etc.
    regulation: str  # DPDP, GDPR, HIPAA, etc.
    priority: int = 1
    conditions: Dict[str, Any] = field(default_factory=dict)

class AadhaarRetentionManager:
    """
    Aadhaar-style Data Retention Manager
    आधार-स्टाइल डेटा रिटेंशन मैनेजर
    
    Manages automated data retention and deletion for PII and sensitive data
    """
    
    def __init__(self):
        self.retention_rules: Dict[str, RetentionRule] = {}
        self.data_records: Dict[str, DataRecord] = {}
        self.deletion_queue: List[str] = []
        self.audit_log: List[Dict] = []
        self.setup_default_rules()
    
    def setup_default_rules(self):
        """Setup default retention rules - डिफ़ॉल्ट रिटेंशन नियम सेट करें"""
        
        # DPDP Act compliance for Aadhaar data
        self.add_retention_rule(RetentionRule(
            rule_id="dpdp_aadhaar_pii",
            data_types={"aadhaar_number", "biometric_data", "demographic_data"},
            classification=DataClassification.PII,
            retention_period=timedelta(days=365),  # 1 year
            action="anonymize",
            jurisdiction="IN",
            regulation="DPDP Act 2023",
            priority=1
        ))
        
        # Financial transaction data
        self.add_retention_rule(RetentionRule(
            rule_id="rbi_financial",
            data_types={"payment_data", "transaction_log", "bank_details"},
            classification=DataClassification.FINANCIAL,
            retention_period=timedelta(days=2555),  # 7 years as per RBI
            action="archive",
            jurisdiction="IN",
            regulation="RBI Guidelines",
            priority=1
        ))
        
        # Authentication logs
        self.add_retention_rule(RetentionRule(
            rule_id="auth_logs",
            data_types={"authentication_log", "access_log", "session_data"},
            classification=DataClassification.INTERNAL,
            retention_period=timedelta(days=90),  # 3 months
            action="delete",
            jurisdiction="IN",
            regulation="Internal Policy",
            priority=2
        ))
        
        # Health data (if applicable)
        self.add_retention_rule(RetentionRule(
            rule_id="health_data",
            data_types={"medical_record", "health_info", "vaccination_data"},
            classification=DataClassification.HEALTH,
            retention_period=timedelta(days=2555),  # 7 years
            action="anonymize",
            jurisdiction="IN",
            regulation="Digital Health Mission",
            priority=1
        ))
        
        print("🔧 Default retention rules configured")
    
    def add_retention_rule(self, rule: RetentionRule):
        """Add retention rule - रिटेंशन नियम जोड़ें"""
        self.retention_rules[rule.rule_id] = rule
        print(f"📋 Added retention rule: {rule.rule_id} ({rule.regulation})")
    
    def register_data_record(self, record: DataRecord):
        """Register data record - डेटा रिकॉर्ड रजिस्टर करें"""
        # Calculate retention based on applicable rules
        applicable_rules = self.find_applicable_rules(record)
        
        if applicable_rules:
            # Use the most restrictive rule (highest priority, shortest retention)
            applicable_rules.sort(key=lambda r: (r.priority, r.retention_period.days))
            best_rule = applicable_rules[0]
            
            # Set deletion schedule
            record.deletion_scheduled = record.created_at + best_rule.retention_period
            record.retention_policy = self.map_retention_period_to_policy(best_rule.retention_period)
        
        self.data_records[record.record_id] = record
        
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "register",
            "record_id": record.record_id,
            "data_type": record.data_type,
            "classification": record.classification.value,
            "deletion_scheduled": record.deletion_scheduled.isoformat() if record.deletion_scheduled else None
        })
        
        print(f"📝 Registered record {record.record_id} - deletion scheduled for {record.deletion_scheduled}")
    
    def find_applicable_rules(self, record: DataRecord) -> List[RetentionRule]:
        """Find applicable retention rules - लागू होने वाले रिटेंशन नियम खोजें"""
        applicable = []
        
        for rule in self.retention_rules.values():
            if (record.data_type in rule.data_types or 
                record.classification == rule.classification):
                applicable.append(rule)
                
        return applicable
    
    def map_retention_period_to_policy(self, period: timedelta) -> RetentionPolicy:
        """Map retention period to policy enum"""
        days = period.days
        
        if days == 0:
            return RetentionPolicy.IMMEDIATE
        elif days <= 30:
            return RetentionPolicy.SHORT_TERM
        elif days <= 365:
            return RetentionPolicy.MEDIUM_TERM
        else:
            return RetentionPolicy.LONG_TERM
    
    def process_retention_queue(self) -> Dict[str, int]:
        """Process retention queue - रिटेंशन क्यू प्रोसेस करें"""
        now = datetime.now()
        actions_taken = {
            "deleted": 0,
            "anonymized": 0,
            "archived": 0,
            "skipped_legal_hold": 0,
            "errors": 0
        }
        
        records_to_process = []
        
        # Find records due for retention action
        for record_id, record in self.data_records.items():
            if (record.deletion_scheduled and 
                record.deletion_scheduled <= now and 
                not record.legal_hold):
                records_to_process.append((record_id, record))
        
        print(f"🔄 Processing {len(records_to_process)} records for retention")
        
        for record_id, record in records_to_process:
            try:
                # Find applicable rule to determine action
                applicable_rules = self.find_applicable_rules(record)
                
                if not applicable_rules:
                    actions_taken["errors"] += 1
                    continue
                
                rule = applicable_rules[0]  # Use highest priority rule
                
                if record.legal_hold:
                    actions_taken["skipped_legal_hold"] += 1
                    self.audit_log.append({
                        "timestamp": now.isoformat(),
                        "action": "skipped_legal_hold",
                        "record_id": record_id,
                        "rule_id": rule.rule_id
                    })
                    continue
                
                # Perform retention action
                if rule.action == "delete":
                    self.delete_record(record_id, rule.rule_id)
                    actions_taken["deleted"] += 1
                    
                elif rule.action == "anonymize":
                    self.anonymize_record(record_id, rule.rule_id)
                    actions_taken["anonymized"] += 1
                    
                elif rule.action == "archive":
                    self.archive_record(record_id, rule.rule_id)
                    actions_taken["archived"] += 1
                    
            except Exception as e:
                actions_taken["errors"] += 1
                print(f"❌ Error processing record {record_id}: {str(e)}")
                
                self.audit_log.append({
                    "timestamp": now.isoformat(),
                    "action": "error",
                    "record_id": record_id,
                    "error": str(e)
                })
        
        print(f"✅ Retention processing complete: {actions_taken}")
        return actions_taken
    
    def delete_record(self, record_id: str, rule_id: str):
        """Delete record permanently - रिकॉर्ड स्थायी रूप से डिलीट करें"""
        record = self.data_records[record_id]
        
        # Secure deletion simulation
        print(f"🗑️ Securely deleting record {record_id}")
        
        # Remove from system
        del self.data_records[record_id]
        
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "deleted",
            "record_id": record_id,
            "rule_id": rule_id,
            "data_type": record.data_type,
            "classification": record.classification.value
        })
    
    def anonymize_record(self, record_id: str, rule_id: str):
        """Anonymize record - रिकॉर्ड को गुमनाम करें"""
        record = self.data_records[record_id]
        
        print(f"🎭 Anonymizing record {record_id}")
        
        # Mark as anonymized
        record.anonymized = True
        record.user_id = None  # Remove user association
        record.deletion_scheduled = None  # No longer needs deletion
        
        # Generate anonymized ID
        record.record_id = f"anon_{hashlib.sha256(record_id.encode()).hexdigest()[:8]}"
        
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "anonymized",
            "record_id": record_id,
            "new_record_id": record.record_id,
            "rule_id": rule_id
        })
    
    def archive_record(self, record_id: str, rule_id: str):
        """Archive record - रिकॉर्ड आर्काइव करें"""
        record = self.data_records[record_id]
        
        print(f"📦 Archiving record {record_id}")
        
        # Simulate archival to cold storage
        archive_location = f"cold_storage/archive_{datetime.now().strftime('%Y%m%d')}/{record_id}"
        
        # Update record with archive info
        record.deletion_scheduled = None  # Archived, no deletion needed
        
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "archived",
            "record_id": record_id,
            "archive_location": archive_location,
            "rule_id": rule_id
        })
    
    def apply_legal_hold(self, record_ids: List[str], hold_reason: str):
        """Apply legal hold - कानूनी होल्ड लगाएं"""
        held_count = 0
        
        for record_id in record_ids:
            if record_id in self.data_records:
                self.data_records[record_id].legal_hold = True
                held_count += 1
                
                self.audit_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "legal_hold_applied",
                    "record_id": record_id,
                    "reason": hold_reason
                })
        
        print(f"⚖️ Applied legal hold to {held_count} records: {hold_reason}")
        return held_count
    
    def remove_legal_hold(self, record_ids: List[str]):
        """Remove legal hold - कानूनी होल्ड हटाएं"""
        released_count = 0
        
        for record_id in record_ids:
            if record_id in self.data_records:
                self.data_records[record_id].legal_hold = False
                released_count += 1
                
                self.audit_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "legal_hold_removed",
                    "record_id": record_id
                })
        
        print(f"🔓 Removed legal hold from {released_count} records")
        return released_count
    
    def generate_retention_report(self) -> Dict:
        """Generate retention compliance report - रिटेंशन अनुपालन रिपोर्ट जेनरेट करें"""
        now = datetime.now()
        
        report = {
            "generated_at": now.isoformat(),
            "total_records": len(self.data_records),
            "by_classification": {},
            "by_retention_policy": {},
            "due_for_action": {
                "overdue": 0,
                "due_this_week": 0,
                "due_this_month": 0
            },
            "legal_holds": 0,
            "compliance_issues": []
        }
        
        # Analyze records
        for record in self.data_records.values():
            # Classification stats
            classification = record.classification.value
            report["by_classification"][classification] = report["by_classification"].get(classification, 0) + 1
            
            # Retention policy stats
            policy = record.retention_policy.value
            report["by_retention_policy"][policy] = report["by_retention_policy"].get(policy, 0) + 1
            
            # Due for action analysis
            if record.deletion_scheduled:
                days_until_action = (record.deletion_scheduled - now).days
                
                if days_until_action < 0:
                    report["due_for_action"]["overdue"] += 1
                elif days_until_action <= 7:
                    report["due_for_action"]["due_this_week"] += 1
                elif days_until_action <= 30:
                    report["due_for_action"]["due_this_month"] += 1
            
            # Legal holds
            if record.legal_hold:
                report["legal_holds"] += 1
            
            # Compliance issues
            if (record.classification == DataClassification.PII and 
                record.retention_policy not in [RetentionPolicy.SHORT_TERM, RetentionPolicy.MEDIUM_TERM]):
                report["compliance_issues"].append(f"PII record {record.record_id} has long retention")
        
        return report
    
    def get_audit_trail(self, record_id: Optional[str] = None) -> List[Dict]:
        """Get audit trail - ऑडिट ट्रेल प्राप्त करें"""
        if record_id:
            return [log for log in self.audit_log if log.get("record_id") == record_id]
        return self.audit_log

async def main():
    """
    Main demonstration function
    मुख्य प्रदर्शन फ़ंक्शन
    """
    print("🏛️ Aadhaar Data Retention Automation Demo")
    print("=" * 50)
    
    manager = AadhaarRetentionManager()
    
    # Register sample data records
    print("\n📝 Registering sample data records...")
    
    records = [
        DataRecord(
            record_id="aadhaar_001",
            data_type="aadhaar_number",
            classification=DataClassification.PII,
            created_at=datetime.now() - timedelta(days=400),  # Over retention period
            last_accessed=datetime.now() - timedelta(days=100),
            retention_policy=RetentionPolicy.MEDIUM_TERM
        ),
        DataRecord(
            record_id="payment_001",
            data_type="payment_data",
            classification=DataClassification.FINANCIAL,
            created_at=datetime.now() - timedelta(days=50),
            last_accessed=datetime.now() - timedelta(days=5),
            retention_policy=RetentionPolicy.LONG_TERM
        ),
        DataRecord(
            record_id="auth_log_001",
            data_type="authentication_log",
            classification=DataClassification.INTERNAL,
            created_at=datetime.now() - timedelta(days=100),  # Over retention period
            last_accessed=datetime.now() - timedelta(days=50),
            retention_policy=RetentionPolicy.SHORT_TERM
        ),
        DataRecord(
            record_id="health_001",
            data_type="vaccination_data",
            classification=DataClassification.HEALTH,
            created_at=datetime.now() - timedelta(days=200),
            last_accessed=datetime.now() - timedelta(days=30),
            retention_policy=RetentionPolicy.LONG_TERM
        )
    ]
    
    for record in records:
        manager.register_data_record(record)
    
    # Apply legal hold to one record
    print("\n⚖️ Applying legal hold...")
    manager.apply_legal_hold(["payment_001"], "Ongoing investigation case #2024-001")
    
    # Generate initial report
    print("\n📊 Initial Retention Report:")
    report = manager.generate_retention_report()
    print(json.dumps(report, indent=2))
    
    # Process retention queue
    print("\n🔄 Processing retention queue...")
    actions = manager.process_retention_queue()
    print(f"Actions taken: {actions}")
    
    # Remove legal hold
    print("\n🔓 Removing legal hold...")
    manager.remove_legal_hold(["payment_001"])
    
    # Generate final report
    print("\n📊 Final Retention Report:")
    final_report = manager.generate_retention_report()
    print(json.dumps(final_report, indent=2))
    
    # Show audit trail for specific record
    print("\n📜 Audit Trail for aadhaar_001:")
    audit_trail = manager.get_audit_trail("aadhaar_001")
    for entry in audit_trail:
        print(f"  {entry['timestamp']}: {entry['action']}")

if __name__ == "__main__":
    asyncio.run(main())
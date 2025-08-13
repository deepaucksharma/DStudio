#!/usr/bin/env python3
"""
GDPR Consent Management System
Episode 47: Data Governance at Scale

European customers के लिए GDPR compliance और Indian customers के लिए 
DPDP Act compliance manage करने का comprehensive system।

Author: Hindi Podcast Series
Context: Multi-jurisdictional consent management for global businesses
"""

import pandas as pd
import sqlite3
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
import logging
import hashlib
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConsentType(Enum):
    """Types of consent"""
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    PERSONALIZATION = "personalization"
    THIRD_PARTY_SHARING = "third_party_sharing"
    PROFILING = "profiling"
    COOKIES = "cookies"
    LOCATION_TRACKING = "location_tracking"

class ConsentStatus(Enum):
    """Consent status"""
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"
    DECLINED = "declined"

class LegalBasis(Enum):
    """GDPR legal basis for processing"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTEREST = "legitimate_interest"

class DataSubjectRights(Enum):
    """Data subject rights"""
    ACCESS = "right_to_access"
    RECTIFICATION = "right_to_rectification"
    ERASURE = "right_to_erasure"  # Right to be forgotten
    RESTRICT_PROCESSING = "right_to_restrict_processing"
    DATA_PORTABILITY = "right_to_data_portability"
    OBJECT = "right_to_object"

@dataclass
class ConsentRecord:
    """Individual consent record"""
    consent_id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    legal_basis: LegalBasis
    given_at: Optional[datetime]
    withdrawn_at: Optional[datetime]
    expires_at: Optional[datetime]
    purpose: str
    data_categories: List[str]
    third_parties: List[str]
    consent_method: str  # web_form, api, phone, email
    user_agent: Optional[str]
    ip_address: Optional[str]
    jurisdiction: str  # EU, IN, US, etc.
    version: int  # Consent version for audit trail

@dataclass
class DataSubjectRequest:
    """Data subject request record"""
    request_id: str
    user_id: str
    request_type: DataSubjectRights
    requested_at: datetime
    status: str  # pending, processing, completed, rejected
    completed_at: Optional[datetime]
    request_details: Dict[str, Any]
    response_data: Optional[Dict[str, Any]]
    processed_by: Optional[str]
    verification_method: str
    jurisdiction: str

class GDPRConsentManager:
    """
    Comprehensive GDPR and DPDP Act consent management system
    
    Features:
    - Multi-jurisdictional consent handling
    - Granular consent types
    - Automatic expiry management
    - Data subject rights handling
    - Audit trail maintenance
    - Consent withdrawal processing
    - Legal basis tracking
    """
    
    def __init__(self, db_path: str = "consent_manager.db"):
        self.db_path = db_path
        self.init_database()
        self.consent_validity_days = {
            'EU': 730,   # 2 years for GDPR
            'IN': 1095,  # 3 years for DPDP Act
            'US': 1095,  # 3 years for CCPA
            'DEFAULT': 365  # 1 year default
        }
        
        logger.info("GDPR Consent Manager initialized")
    
    def init_database(self):
        """Initialize SQLite database for consent management"""
        self.conn = sqlite3.connect(self.db_path)
        
        # Consent records table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS consent_records (
                consent_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                consent_type TEXT NOT NULL,
                status TEXT NOT NULL,
                legal_basis TEXT NOT NULL,
                given_at TIMESTAMP,
                withdrawn_at TIMESTAMP,
                expires_at TIMESTAMP,
                purpose TEXT NOT NULL,
                data_categories TEXT,  -- JSON array
                third_parties TEXT,    -- JSON array
                consent_method TEXT,
                user_agent TEXT,
                ip_address TEXT,
                jurisdiction TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Data subject requests table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS data_subject_requests (
                request_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                request_type TEXT NOT NULL,
                requested_at TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                completed_at TIMESTAMP,
                request_details TEXT,  -- JSON
                response_data TEXT,    -- JSON
                processed_by TEXT,
                verification_method TEXT,
                jurisdiction TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Consent history for audit trail
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS consent_history (
                history_id TEXT PRIMARY KEY,
                consent_id TEXT NOT NULL,
                action TEXT NOT NULL,  -- granted, withdrawn, expired
                timestamp TIMESTAMP NOT NULL,
                details TEXT,  -- JSON
                FOREIGN KEY (consent_id) REFERENCES consent_records (consent_id)
            )
        ''')
        
        # Create indexes
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON consent_records(user_id)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_consent_type ON consent_records(consent_type)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_status ON consent_records(status)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_jurisdiction ON consent_records(jurisdiction)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON consent_records(expires_at)')
        
        self.conn.commit()
    
    def record_consent(self, consent: ConsentRecord) -> str:
        """Record a new consent or update existing one"""
        
        # Calculate expiry date if not provided
        if not consent.expires_at and consent.given_at:
            validity_days = self.consent_validity_days.get(
                consent.jurisdiction, 
                self.consent_validity_days['DEFAULT']
            )
            consent.expires_at = consent.given_at + timedelta(days=validity_days)
        
        # Insert consent record
        self.conn.execute('''
            INSERT OR REPLACE INTO consent_records 
            (consent_id, user_id, consent_type, status, legal_basis, given_at, 
             withdrawn_at, expires_at, purpose, data_categories, third_parties,
             consent_method, user_agent, ip_address, jurisdiction, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            consent.consent_id,
            consent.user_id,
            consent.consent_type.value,
            consent.status.value,
            consent.legal_basis.value,
            consent.given_at,
            consent.withdrawn_at,
            consent.expires_at,
            consent.purpose,
            json.dumps(consent.data_categories),
            json.dumps(consent.third_parties),
            consent.consent_method,
            consent.user_agent,
            consent.ip_address,
            consent.jurisdiction,
            consent.version
        ))
        
        # Add to history
        self._add_to_history(consent.consent_id, "granted", {
            "consent_type": consent.consent_type.value,
            "purpose": consent.purpose,
            "method": consent.consent_method
        })
        
        self.conn.commit()
        
        logger.info(f"Recorded consent: {consent.consent_id} for user {consent.user_id}")
        
        return consent.consent_id
    
    def withdraw_consent(self, user_id: str, consent_type: ConsentType, 
                        withdrawal_method: str = "user_request") -> bool:
        """Withdraw consent for a specific type"""
        
        # Find active consent
        cursor = self.conn.execute('''
            SELECT consent_id FROM consent_records 
            WHERE user_id = ? AND consent_type = ? AND status = 'given'
        ''', (user_id, consent_type.value))
        
        results = cursor.fetchall()
        
        if not results:
            logger.warning(f"No active consent found for user {user_id}, type {consent_type.value}")
            return False
        
        withdrawal_time = datetime.now()
        
        # Update all matching consent records
        for (consent_id,) in results:
            self.conn.execute('''
                UPDATE consent_records 
                SET status = 'withdrawn', withdrawn_at = ?, updated_at = ?
                WHERE consent_id = ?
            ''', (withdrawal_time, withdrawal_time, consent_id))
            
            # Add to history
            self._add_to_history(consent_id, "withdrawn", {
                "method": withdrawal_method,
                "timestamp": withdrawal_time.isoformat()
            })
        
        self.conn.commit()
        
        logger.info(f"Withdrawn consent for user {user_id}, type {consent_type.value}")
        
        return True
    
    def check_consent_validity(self, user_id: str, consent_type: ConsentType, 
                              purpose: str) -> Dict[str, Any]:
        """Check if user has valid consent for specified purpose"""
        
        cursor = self.conn.execute('''
            SELECT consent_id, status, given_at, expires_at, legal_basis, purpose
            FROM consent_records 
            WHERE user_id = ? AND consent_type = ? AND purpose LIKE ?
            ORDER BY given_at DESC LIMIT 1
        ''', (user_id, consent_type.value, f"%{purpose}%"))
        
        result = cursor.fetchone()
        
        if not result:
            return {
                "has_consent": False,
                "reason": "No consent record found",
                "legal_basis": None
            }
        
        consent_id, status, given_at, expires_at, legal_basis, recorded_purpose = result
        
        current_time = datetime.now()
        
        # Check if consent is withdrawn
        if status == "withdrawn":
            return {
                "has_consent": False,
                "reason": "Consent has been withdrawn",
                "consent_id": consent_id,
                "withdrawn_at": self._get_withdrawal_time(consent_id),
                "legal_basis": legal_basis
            }
        
        # Check if consent has expired
        if expires_at and datetime.fromisoformat(expires_at) < current_time:
            # Mark as expired
            self.conn.execute('''
                UPDATE consent_records 
                SET status = 'expired', updated_at = ?
                WHERE consent_id = ?
            ''', (current_time, consent_id))
            
            self._add_to_history(consent_id, "expired", {
                "expired_at": current_time.isoformat()
            })
            
            self.conn.commit()
            
            return {
                "has_consent": False,
                "reason": "Consent has expired",
                "consent_id": consent_id,
                "expired_at": expires_at,
                "legal_basis": legal_basis
            }
        
        # Valid consent found
        return {
            "has_consent": True,
            "consent_id": consent_id,
            "given_at": given_at,
            "expires_at": expires_at,
            "legal_basis": legal_basis,
            "purpose": recorded_purpose
        }
    
    def process_data_subject_request(self, request: DataSubjectRequest) -> str:
        """Process a data subject rights request"""
        
        # Insert request record
        self.conn.execute('''
            INSERT INTO data_subject_requests 
            (request_id, user_id, request_type, requested_at, status, 
             request_details, verification_method, jurisdiction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.request_id,
            request.user_id,
            request.request_type.value,
            request.requested_at,
            request.status,
            json.dumps(request.request_details),
            request.verification_method,
            request.jurisdiction
        ))
        
        self.conn.commit()
        
        # Process specific request types
        if request.request_type == DataSubjectRights.ACCESS:
            self._process_access_request(request)
        elif request.request_type == DataSubjectRights.ERASURE:
            self._process_erasure_request(request)
        elif request.request_type == DataSubjectRights.DATA_PORTABILITY:
            self._process_portability_request(request)
        
        logger.info(f"Processing data subject request: {request.request_id}")
        
        return request.request_id
    
    def _process_access_request(self, request: DataSubjectRequest):
        """Process right to access request"""
        user_id = request.user_id
        
        # Collect all data for this user
        consent_data = self._get_user_consent_data(user_id)
        processing_data = self._get_user_processing_data(user_id)
        
        response_data = {
            "user_id": user_id,
            "request_type": "data_access",
            "generated_at": datetime.now().isoformat(),
            "consent_records": consent_data,
            "processing_activities": processing_data,
            "data_retention_info": self._get_retention_info(user_id)
        }
        
        # Update request with response
        self.conn.execute('''
            UPDATE data_subject_requests 
            SET status = 'completed', completed_at = ?, response_data = ?
            WHERE request_id = ?
        ''', (datetime.now(), json.dumps(response_data), request.request_id))
        
        self.conn.commit()
    
    def _process_erasure_request(self, request: DataSubjectRequest):
        """Process right to erasure (right to be forgotten) request"""
        user_id = request.user_id
        
        # Check if there are legal obligations to retain data
        retention_requirements = self._check_retention_requirements(user_id)
        
        if retention_requirements:
            # Cannot fully delete - pseudonymize instead
            self._pseudonymize_user_data(user_id)
            
            response_data = {
                "action": "pseudonymized",
                "reason": "Legal retention requirements",
                "retention_details": retention_requirements,
                "processed_at": datetime.now().isoformat()
            }
        else:
            # Can fully delete
            self._delete_user_data(user_id)
            
            response_data = {
                "action": "fully_deleted",
                "processed_at": datetime.now().isoformat(),
                "confirmation": f"All data for user {user_id} has been erased"
            }
        
        # Update request
        self.conn.execute('''
            UPDATE data_subject_requests 
            SET status = 'completed', completed_at = ?, response_data = ?
            WHERE request_id = ?
        ''', (datetime.now(), json.dumps(response_data), request.request_id))
        
        self.conn.commit()
    
    def _process_portability_request(self, request: DataSubjectRequest):
        """Process data portability request"""
        user_id = request.user_id
        
        # Export user data in machine-readable format
        portable_data = {
            "user_id": user_id,
            "export_date": datetime.now().isoformat(),
            "data_format": "JSON",
            "consent_records": self._get_user_consent_data(user_id),
            "personal_data": self._get_user_personal_data(user_id),
            "preferences": self._get_user_preferences(user_id)
        }
        
        # Update request
        self.conn.execute('''
            UPDATE data_subject_requests 
            SET status = 'completed', completed_at = ?, response_data = ?
            WHERE request_id = ?
        ''', (datetime.now(), json.dumps(portable_data), request.request_id))
        
        self.conn.commit()
    
    def get_consent_analytics(self, jurisdiction: str = None, 
                            date_from: datetime = None,
                            date_to: datetime = None) -> Dict[str, Any]:
        """Get analytics on consent patterns"""
        
        where_conditions = []
        params = []
        
        if jurisdiction:
            where_conditions.append("jurisdiction = ?")
            params.append(jurisdiction)
        
        if date_from:
            where_conditions.append("given_at >= ?")
            params.append(date_from)
        
        if date_to:
            where_conditions.append("given_at <= ?")
            params.append(date_to)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Overall consent statistics
        cursor = self.conn.execute(f'''
            SELECT 
                COUNT(*) as total_consents,
                COUNT(CASE WHEN status = 'given' THEN 1 END) as active_consents,
                COUNT(CASE WHEN status = 'withdrawn' THEN 1 END) as withdrawn_consents,
                COUNT(CASE WHEN status = 'expired' THEN 1 END) as expired_consents
            FROM consent_records {where_clause}
        ''', params)
        
        overall_stats = cursor.fetchone()
        
        # Consent by type
        cursor = self.conn.execute(f'''
            SELECT consent_type, status, COUNT(*) as count
            FROM consent_records {where_clause}
            GROUP BY consent_type, status
            ORDER BY consent_type, status
        ''', params)
        
        consent_by_type = {}
        for consent_type, status, count in cursor.fetchall():
            if consent_type not in consent_by_type:
                consent_by_type[consent_type] = {}
            consent_by_type[consent_type][status] = count
        
        # Monthly trends
        cursor = self.conn.execute(f'''
            SELECT 
                strftime('%Y-%m', given_at) as month,
                consent_type,
                COUNT(*) as consents_given
            FROM consent_records 
            WHERE given_at IS NOT NULL {' AND ' + ' AND '.join(where_conditions) if where_conditions else ''}
            GROUP BY strftime('%Y-%m', given_at), consent_type
            ORDER BY month, consent_type
        ''', params)
        
        monthly_trends = {}
        for month, consent_type, count in cursor.fetchall():
            if month not in monthly_trends:
                monthly_trends[month] = {}
            monthly_trends[month][consent_type] = count
        
        # Top withdrawal reasons (from history)
        cursor = self.conn.execute(f'''
            SELECT 
                h.details,
                COUNT(*) as count
            FROM consent_history h
            JOIN consent_records c ON h.consent_id = c.consent_id
            WHERE h.action = 'withdrawn' {' AND ' + ' AND '.join(where_conditions) if where_conditions else ''}
            GROUP BY h.details
            ORDER BY count DESC
            LIMIT 10
        ''', params)
        
        withdrawal_reasons = []
        for details, count in cursor.fetchall():
            try:
                parsed_details = json.loads(details) if details else {}
                withdrawal_reasons.append({
                    "reason": parsed_details.get("method", "unknown"),
                    "count": count
                })
            except:
                withdrawal_reasons.append({"reason": "unknown", "count": count})
        
        return {
            "overall_stats": {
                "total_consents": overall_stats[0],
                "active_consents": overall_stats[1],
                "withdrawn_consents": overall_stats[2],
                "expired_consents": overall_stats[3]
            },
            "consent_by_type": consent_by_type,
            "monthly_trends": monthly_trends,
            "withdrawal_reasons": withdrawal_reasons,
            "analysis_period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None,
                "jurisdiction": jurisdiction
            }
        }
    
    def run_expiry_maintenance(self) -> Dict[str, int]:
        """Run maintenance to mark expired consents"""
        current_time = datetime.now()
        
        # Find expired consents
        cursor = self.conn.execute('''
            SELECT consent_id FROM consent_records 
            WHERE expires_at < ? AND status = 'given'
        ''', (current_time,))
        
        expired_consents = cursor.fetchall()
        
        # Mark as expired
        expired_count = 0
        for (consent_id,) in expired_consents:
            self.conn.execute('''
                UPDATE consent_records 
                SET status = 'expired', updated_at = ?
                WHERE consent_id = ?
            ''', (current_time, consent_id))
            
            self._add_to_history(consent_id, "expired", {
                "expired_at": current_time.isoformat(),
                "auto_expired": True
            })
            
            expired_count += 1
        
        self.conn.commit()
        
        logger.info(f"Expired {expired_count} consent records")
        
        return {
            "expired_count": expired_count,
            "processed_at": current_time.isoformat()
        }
    
    def _add_to_history(self, consent_id: str, action: str, details: Dict[str, Any]):
        """Add entry to consent history"""
        history_id = str(uuid.uuid4())
        
        self.conn.execute('''
            INSERT INTO consent_history (history_id, consent_id, action, timestamp, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (history_id, consent_id, action, datetime.now(), json.dumps(details)))
    
    def _get_user_consent_data(self, user_id: str) -> List[Dict]:
        """Get all consent data for a user"""
        cursor = self.conn.execute('''
            SELECT * FROM consent_records WHERE user_id = ?
        ''', (user_id,))
        
        columns = [description[0] for description in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            record = dict(zip(columns, row))
            # Parse JSON fields
            if record['data_categories']:
                record['data_categories'] = json.loads(record['data_categories'])
            if record['third_parties']:
                record['third_parties'] = json.loads(record['third_parties'])
            results.append(record)
        
        return results
    
    def _get_user_processing_data(self, user_id: str) -> Dict:
        """Get processing activities for a user (mock implementation)"""
        return {
            "activities": [
                "email_marketing",
                "personalized_recommendations", 
                "analytics_tracking"
            ],
            "last_processed": datetime.now().isoformat()
        }
    
    def _get_retention_info(self, user_id: str) -> Dict:
        """Get data retention information"""
        return {
            "retention_periods": {
                "marketing_data": "2 years",
                "transaction_data": "7 years",
                "analytics_data": "3 years"
            },
            "legal_basis": "Compliance with tax and financial regulations"
        }
    
    def _check_retention_requirements(self, user_id: str) -> List[str]:
        """Check if there are legal requirements to retain data"""
        # Mock implementation - in real system, check against compliance requirements
        return ["Financial transaction records must be retained for 7 years"]
    
    def _pseudonymize_user_data(self, user_id: str):
        """Pseudonymize user data instead of full deletion"""
        # Generate pseudonym
        pseudonym = hashlib.sha256(f"{user_id}_{datetime.now()}".encode()).hexdigest()[:16]
        
        # In real implementation, would pseudonymize across all systems
        logger.info(f"Pseudonymized data for user {user_id} -> {pseudonym}")
    
    def _delete_user_data(self, user_id: str):
        """Fully delete user data"""
        # Delete consent records (keeping history for audit)
        self.conn.execute('DELETE FROM consent_records WHERE user_id = ?', (user_id,))
        self.conn.commit()
        
        # In real implementation, would delete from all systems
        logger.info(f"Fully deleted data for user {user_id}")
    
    def _get_user_personal_data(self, user_id: str) -> Dict:
        """Get user's personal data for portability"""
        # Mock implementation
        return {
            "profile_data": "User profile information",
            "preferences": "User preferences",
            "transaction_history": "Transaction records"
        }
    
    def _get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences"""
        # Mock implementation
        return {
            "language": "Hindi",
            "communication_preferences": ["email", "sms"],
            "marketing_topics": ["electronics", "fashion"]
        }
    
    def _get_withdrawal_time(self, consent_id: str) -> Optional[str]:
        """Get withdrawal time from consent record"""
        cursor = self.conn.execute(
            'SELECT withdrawn_at FROM consent_records WHERE consent_id = ?', 
            (consent_id,)
        )
        result = cursor.fetchone()
        return result[0] if result and result[0] else None

def create_sample_consent_data():
    """Create sample consent data for testing"""
    manager = GDPRConsentManager()
    
    # Sample users from different jurisdictions
    users = [
        {"user_id": "user_eu_001", "jurisdiction": "EU"},
        {"user_id": "user_in_001", "jurisdiction": "IN"},
        {"user_id": "user_in_002", "jurisdiction": "IN"},
        {"user_id": "user_us_001", "jurisdiction": "US"}
    ]
    
    consent_types = [
        ConsentType.MARKETING,
        ConsentType.ANALYTICS,
        ConsentType.PERSONALIZATION,
        ConsentType.COOKIES
    ]
    
    # Create sample consent records
    for user in users:
        for consent_type in consent_types:
            # Some users give consent, some don't
            if hash(f"{user['user_id']}{consent_type.value}") % 3 != 0:
                consent = ConsentRecord(
                    consent_id=str(uuid.uuid4()),
                    user_id=user["user_id"],
                    consent_type=consent_type,
                    status=ConsentStatus.GIVEN,
                    legal_basis=LegalBasis.CONSENT,
                    given_at=datetime.now() - timedelta(days=hash(user["user_id"]) % 300),
                    withdrawn_at=None,
                    expires_at=None,  # Will be calculated automatically
                    purpose=f"Processing for {consent_type.value} purposes",
                    data_categories=["personal_info", "behavioral_data"],
                    third_parties=["analytics_provider", "marketing_partner"],
                    consent_method="web_form",
                    user_agent="Mozilla/5.0 Chrome/91.0",
                    ip_address=f"192.168.1.{hash(user['user_id']) % 255}",
                    jurisdiction=user["jurisdiction"],
                    version=1
                )
                
                manager.record_consent(consent)
    
    return manager

def main():
    """Main function demonstrating GDPR consent management"""
    print("🔒 Starting GDPR Consent Management System Demo")
    print("=" * 70)
    
    # Create sample data
    print("Creating sample consent data...")
    manager = create_sample_consent_data()
    
    print("✅ Sample consent data created")
    print()
    
    # Check consent validity
    print("🔍 Checking consent validity...")
    
    test_cases = [
        ("user_eu_001", ConsentType.MARKETING, "email marketing"),
        ("user_in_001", ConsentType.ANALYTICS, "website analytics"),
        ("user_us_001", ConsentType.PERSONALIZATION, "product recommendations")
    ]
    
    for user_id, consent_type, purpose in test_cases:
        validity = manager.check_consent_validity(user_id, consent_type, purpose)
        
        print(f"User: {user_id}, Type: {consent_type.value}")
        print(f"  Has consent: {validity['has_consent']}")
        if validity['has_consent']:
            print(f"  Given at: {validity['given_at']}")
            print(f"  Expires at: {validity['expires_at']}")
        else:
            print(f"  Reason: {validity['reason']}")
        print()
    
    # Withdraw consent
    print("❌ Testing consent withdrawal...")
    success = manager.withdraw_consent("user_eu_001", ConsentType.MARKETING, "user_request")
    print(f"Withdrawal successful: {success}")
    
    # Re-check consent after withdrawal
    validity = manager.check_consent_validity("user_eu_001", ConsentType.MARKETING, "email marketing")
    print(f"Consent after withdrawal: {validity['has_consent']} - {validity['reason']}")
    print()
    
    # Process data subject request
    print("📋 Processing data subject request (Right to Access)...")
    
    access_request = DataSubjectRequest(
        request_id=str(uuid.uuid4()),
        user_id="user_eu_001",
        request_type=DataSubjectRights.ACCESS,
        requested_at=datetime.now(),
        status="pending",
        completed_at=None,
        request_details={"requested_data": "all"},
        response_data=None,
        processed_by=None,
        verification_method="email_verification",
        jurisdiction="EU"
    )
    
    request_id = manager.process_data_subject_request(access_request)
    print(f"Access request processed: {request_id}")
    print()
    
    # Get consent analytics
    print("📊 Generating consent analytics...")
    analytics = manager.get_consent_analytics()
    
    print("Overall Statistics:")
    print(f"  Total consents: {analytics['overall_stats']['total_consents']}")
    print(f"  Active consents: {analytics['overall_stats']['active_consents']}")
    print(f"  Withdrawn consents: {analytics['overall_stats']['withdrawn_consents']}")
    print()
    
    print("Consent by Type:")
    for consent_type, statuses in analytics['consent_by_type'].items():
        print(f"  {consent_type}: {statuses}")
    print()
    
    # Run expiry maintenance
    print("🔄 Running expiry maintenance...")
    expiry_results = manager.run_expiry_maintenance()
    print(f"Expired {expiry_results['expired_count']} consent records")
    print()
    
    # Final analytics after maintenance
    print("📊 Updated analytics after maintenance...")
    final_analytics = manager.get_consent_analytics()
    print(f"Active consents: {final_analytics['overall_stats']['active_consents']}")
    print(f"Expired consents: {final_analytics['overall_stats']['expired_consents']}")
    
    print("\n✅ GDPR Consent Management demo completed successfully!")

if __name__ == "__main__":
    main()
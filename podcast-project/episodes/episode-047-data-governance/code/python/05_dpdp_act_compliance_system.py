#!/usr/bin/env python3
"""
DPDP Act 2023 Compliance System for Indian Businesses
Episode 47: Data Governance at Scale

India की Digital Personal Data Protection Act 2023 के अनुसार comprehensive
compliance system जो Indian businesses के लिए specially designed है।

Author: Hindi Podcast Series
Context: DPDP Act compliance for Indian digital businesses
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Set, Tuple
import re
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
import sqlite3
from pathlib import Path
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataPrincipalRights(Enum):
    """Rights of Data Principal under DPDP Act"""
    RIGHT_TO_INFORMATION = "right_to_information"
    RIGHT_OF_CORRECTION = "right_of_correction"
    RIGHT_OF_ERASURE = "right_of_erasure"
    RIGHT_OF_GRIEVANCE_REDRESSAL = "right_of_grievance_redressal"
    RIGHT_TO_NOMINATE = "right_to_nominate"  # For deceased/incapacitated persons

class LawfulBasisDPDP(Enum):
    """Lawful basis for processing under DPDP Act"""
    CONSENT = "consent"
    LEGITIMATE_USE = "legitimate_use"
    EMPLOYMENT_PURPOSE = "employment_purpose"
    STATE_FUNCTION = "state_function"
    COMPLIANCE_WITH_LAW = "compliance_with_law"
    MEDICAL_EMERGENCY = "medical_emergency"

class DataFiduciaryClass(Enum):
    """Classes of Data Fiduciaries"""
    SIGNIFICANT_DATA_FIDUCIARY = "significant_data_fiduciary"
    REGULAR_DATA_FIDUCIARY = "regular_data_fiduciary"

class NoticeRequirement(Enum):
    """Notice requirements under DPDP Act"""
    IDENTITY_CONTACT = "identity_and_contact_details"
    PURPOSE_DESCRIPTION = "purpose_description"
    PERSONAL_DATA_ITEMS = "personal_data_items_categories"
    RETENTION_PERIOD = "retention_period"
    RIGHTS_AND_GRIEVANCE = "rights_and_grievance_redressal"

@dataclass
class DataPrincipal:
    """Data Principal (Individual whose data is processed)"""
    principal_id: str
    name: str
    email: Optional[str]
    mobile: Optional[str]
    age_category: str  # child, adult, senior_citizen
    is_person_with_disability: bool
    preferred_language: str
    jurisdiction_state: str
    created_at: datetime
    
@dataclass
class ConsentRecord:
    """Consent record under DPDP Act"""
    consent_id: str
    principal_id: str
    fiduciary_id: str
    purpose: str
    data_categories: List[str]
    consent_given_at: datetime
    consent_withdrawn_at: Optional[datetime]
    consent_method: str  # digital_form, voice, written
    language_used: str
    is_informed_consent: bool
    is_freely_given: bool
    specific_purposes: List[str]
    retention_period: int  # days
    third_party_sharing: bool
    cross_border_transfer: bool
    
@dataclass
class BreachNotification:
    """Data breach notification record"""
    breach_id: str
    fiduciary_id: str
    discovered_at: datetime
    reported_to_board_at: Optional[datetime]
    affected_principals_count: int
    breach_type: str
    severity: str  # low, medium, high, critical
    personal_data_affected: List[str]
    potential_harm: str
    mitigation_measures: List[str]
    notification_sent_to_principals: bool
    
@dataclass
class GrievanceRecord:
    """Grievance redressal record"""
    grievance_id: str
    principal_id: str
    fiduciary_id: str
    grievance_type: DataPrincipalRights
    submitted_at: datetime
    description: str
    status: str  # submitted, under_review, resolved, rejected
    resolved_at: Optional[datetime]
    resolution_details: Optional[str]
    escalated_to_board: bool

class DPDPActComplianceSystem:
    """
    Comprehensive DPDP Act 2023 compliance system
    
    Features:
    - Data Principal rights management
    - Consent collection and tracking
    - Notice and transparency requirements
    - Breach notification system
    - Grievance redressal mechanism
    - Cross-border transfer compliance
    - Significant Data Fiduciary obligations
    """
    
    def __init__(self, fiduciary_name: str, fiduciary_class: DataFiduciaryClass,
                 db_path: str = "dpdp_compliance.db"):
        self.fiduciary_name = fiduciary_name
        self.fiduciary_class = fiduciary_class
        self.fiduciary_id = self._generate_fiduciary_id()
        self.db_path = db_path
        self.init_database()
        
        # DPDP Act specific configurations
        self.indian_states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
            "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
            "Delhi", "Jammu and Kashmir", "Ladakh", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
            "Lakshadweep", "Puducherry", "Andaman and Nicobar Islands"
        ]
        
        self.indian_languages = [
            "Hindi", "English", "Bengali", "Telugu", "Marathi", "Tamil", "Gujarati",
            "Urdu", "Kannada", "Odia", "Malayalam", "Punjabi", "Assamese", "Maithili",
            "Santali", "Kashmiri", "Nepali", "Sindhi", "Dogri", "Manipuri", "Bodo", "Sanskrit"
        ]
        
        logger.info(f"DPDP Act Compliance System initialized for {fiduciary_name}")
    
    def _generate_fiduciary_id(self) -> str:
        """Generate unique fiduciary ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        name_hash = hashlib.md5(self.fiduciary_name.encode()).hexdigest()[:8].upper()
        return f"DF-{timestamp}-{name_hash}"
    
    def init_database(self):
        """Initialize compliance database"""
        self.conn = sqlite3.connect(self.db_path)
        
        # Data Principals table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS data_principals (
                principal_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                mobile TEXT,
                age_category TEXT NOT NULL,
                is_person_with_disability BOOLEAN DEFAULT 0,
                preferred_language TEXT DEFAULT 'Hindi',
                jurisdiction_state TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Consent records table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS consent_records (
                consent_id TEXT PRIMARY KEY,
                principal_id TEXT NOT NULL,
                fiduciary_id TEXT NOT NULL,
                purpose TEXT NOT NULL,
                data_categories TEXT NOT NULL,  -- JSON
                consent_given_at TIMESTAMP NOT NULL,
                consent_withdrawn_at TIMESTAMP,
                consent_method TEXT NOT NULL,
                language_used TEXT NOT NULL,
                is_informed_consent BOOLEAN DEFAULT 1,
                is_freely_given BOOLEAN DEFAULT 1,
                specific_purposes TEXT,  -- JSON
                retention_period INTEGER,
                third_party_sharing BOOLEAN DEFAULT 0,
                cross_border_transfer BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (principal_id) REFERENCES data_principals (principal_id)
            )
        ''')
        
        # Breach notifications table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS breach_notifications (
                breach_id TEXT PRIMARY KEY,
                fiduciary_id TEXT NOT NULL,
                discovered_at TIMESTAMP NOT NULL,
                reported_to_board_at TIMESTAMP,
                affected_principals_count INTEGER NOT NULL,
                breach_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                personal_data_affected TEXT,  -- JSON
                potential_harm TEXT,
                mitigation_measures TEXT,  -- JSON
                notification_sent_to_principals BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Grievances table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS grievances (
                grievance_id TEXT PRIMARY KEY,
                principal_id TEXT NOT NULL,
                fiduciary_id TEXT NOT NULL,
                grievance_type TEXT NOT NULL,
                submitted_at TIMESTAMP NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'submitted',
                resolved_at TIMESTAMP,
                resolution_details TEXT,
                escalated_to_board BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (principal_id) REFERENCES data_principals (principal_id)
            )
        ''')
        
        # Processing activities register
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS processing_activities (
                activity_id TEXT PRIMARY KEY,
                fiduciary_id TEXT NOT NULL,
                activity_name TEXT NOT NULL,
                purpose TEXT NOT NULL,
                data_categories TEXT,  -- JSON
                data_sources TEXT,  -- JSON
                recipients TEXT,  -- JSON
                retention_period INTEGER,
                security_measures TEXT,  -- JSON
                cross_border_transfers TEXT,  -- JSON
                lawful_basis TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def register_data_principal(self, principal: DataPrincipal) -> str:
        """Register a new data principal"""
        self.conn.execute('''
            INSERT OR REPLACE INTO data_principals 
            (principal_id, name, email, mobile, age_category, is_person_with_disability,
             preferred_language, jurisdiction_state, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            principal.principal_id,
            principal.name,
            principal.email,
            principal.mobile,
            principal.age_category,
            principal.is_person_with_disability,
            principal.preferred_language,
            principal.jurisdiction_state,
            principal.created_at
        ))
        
        self.conn.commit()
        logger.info(f"Registered data principal: {principal.name}")
        
        return principal.principal_id
    
    def collect_consent(self, consent: ConsentRecord) -> str:
        """Collect and record consent from data principal"""
        
        # Validate consent requirements under DPDP Act
        validation_result = self._validate_consent_requirements(consent)
        if not validation_result['is_valid']:
            raise ValueError(f"Invalid consent: {validation_result['errors']}")
        
        # Insert consent record
        self.conn.execute('''
            INSERT INTO consent_records 
            (consent_id, principal_id, fiduciary_id, purpose, data_categories,
             consent_given_at, consent_method, language_used, is_informed_consent,
             is_freely_given, specific_purposes, retention_period, third_party_sharing,
             cross_border_transfer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            consent.consent_id,
            consent.principal_id,
            consent.fiduciary_id,
            consent.purpose,
            json.dumps(consent.data_categories),
            consent.consent_given_at,
            consent.consent_method,
            consent.language_used,
            consent.is_informed_consent,
            consent.is_freely_given,
            json.dumps(consent.specific_purposes),
            consent.retention_period,
            consent.third_party_sharing,
            consent.cross_border_transfer
        ))
        
        self.conn.commit()
        
        # Generate notice to data principal
        self._generate_privacy_notice(consent)
        
        logger.info(f"Consent collected: {consent.consent_id}")
        
        return consent.consent_id
    
    def _validate_consent_requirements(self, consent: ConsentRecord) -> Dict[str, Any]:
        """Validate consent against DPDP Act requirements"""
        errors = []
        
        # Check if consent is informed
        if not consent.is_informed_consent:
            errors.append("Consent must be informed - all required information must be provided")
        
        # Check if consent is freely given
        if not consent.is_freely_given:
            errors.append("Consent must be freely given without coercion")
        
        # Check if purpose is specific
        if not consent.purpose or len(consent.purpose.strip()) < 10:
            errors.append("Purpose must be specific and clearly defined")
        
        # Check if retention period is specified
        if not consent.retention_period or consent.retention_period <= 0:
            errors.append("Retention period must be specified and reasonable")
        
        # Check if data categories are specified
        if not consent.data_categories:
            errors.append("Data categories being processed must be specified")
        
        # Check language requirement for Indian users
        if consent.language_used not in self.indian_languages:
            errors.append(f"Consent language must be in one of the recognized Indian languages")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _generate_privacy_notice(self, consent: ConsentRecord):
        """Generate privacy notice as required under DPDP Act"""
        notice = {
            'notice_id': str(uuid.uuid4()),
            'fiduciary_name': self.fiduciary_name,
            'fiduciary_contact': "privacy@company.com",  # Should be configured
            'purpose': consent.purpose,
            'data_items': consent.data_categories,
            'retention_period': f"{consent.retention_period} days",
            'data_principal_rights': [right.value for right in DataPrincipalRights],
            'grievance_mechanism': "grievance@company.com",
            'generated_at': datetime.now().isoformat(),
            'language': consent.language_used
        }
        
        # In real implementation, this would be sent to the data principal
        logger.info(f"Privacy notice generated for consent: {consent.consent_id}")
        
        return notice
    
    def withdraw_consent(self, principal_id: str, consent_id: str, 
                        withdrawal_reason: str = "user_request") -> bool:
        """Process consent withdrawal"""
        
        # Check if consent exists and is active
        cursor = self.conn.execute('''
            SELECT consent_id FROM consent_records 
            WHERE principal_id = ? AND consent_id = ? AND consent_withdrawn_at IS NULL
        ''', (principal_id, consent_id))
        
        if not cursor.fetchone():
            logger.warning(f"No active consent found: {consent_id} for principal {principal_id}")
            return False
        
        # Update consent record
        withdrawal_time = datetime.now()
        self.conn.execute('''
            UPDATE consent_records 
            SET consent_withdrawn_at = ?
            WHERE consent_id = ?
        ''', (withdrawal_time, consent_id))
        
        self.conn.commit()
        
        # In real implementation, stop processing personal data for this consent
        self._stop_data_processing(consent_id, withdrawal_reason)
        
        logger.info(f"Consent withdrawn: {consent_id}")
        
        return True
    
    def _stop_data_processing(self, consent_id: str, reason: str):
        """Stop data processing based on withdrawn consent"""
        # This would integrate with actual data processing systems
        logger.info(f"Stopping data processing for consent: {consent_id}, reason: {reason}")
    
    def process_data_principal_request(self, principal_id: str, 
                                     request_type: DataPrincipalRights,
                                     request_details: Dict[str, Any]) -> str:
        """Process data principal rights request"""
        
        request_id = str(uuid.uuid4())
        
        if request_type == DataPrincipalRights.RIGHT_TO_INFORMATION:
            response = self._process_information_request(principal_id, request_details)
        elif request_type == DataPrincipalRights.RIGHT_OF_CORRECTION:
            response = self._process_correction_request(principal_id, request_details)
        elif request_type == DataPrincipalRights.RIGHT_OF_ERASURE:
            response = self._process_erasure_request(principal_id, request_details)
        else:
            response = {"status": "pending", "message": "Request received and under review"}
        
        # Log the request processing
        logger.info(f"Processed {request_type.value} request for principal {principal_id}")
        
        return request_id
    
    def _process_information_request(self, principal_id: str, 
                                   request_details: Dict[str, Any]) -> Dict[str, Any]:
        """Process right to information request"""
        
        # Get all consent records for this principal
        cursor = self.conn.execute('''
            SELECT * FROM consent_records WHERE principal_id = ?
        ''', (principal_id,))
        
        columns = [desc[0] for desc in cursor.description]
        consent_records = []
        
        for row in cursor.fetchall():
            record = dict(zip(columns, row))
            # Parse JSON fields
            if record['data_categories']:
                record['data_categories'] = json.loads(record['data_categories'])
            if record['specific_purposes']:
                record['specific_purposes'] = json.loads(record['specific_purposes'])
            consent_records.append(record)
        
        # Get processing activities
        processing_activities = self._get_processing_activities_for_principal(principal_id)
        
        information_report = {
            "principal_id": principal_id,
            "report_generated_at": datetime.now().isoformat(),
            "consent_records": consent_records,
            "processing_activities": processing_activities,
            "data_retention_info": self._get_retention_schedule(principal_id),
            "third_party_sharing": self._get_third_party_sharing_info(principal_id),
            "rights_available": [right.value for right in DataPrincipalRights],
            "contact_for_queries": "privacy@company.com"
        }
        
        return {
            "status": "completed",
            "information_report": information_report
        }
    
    def _process_correction_request(self, principal_id: str, 
                                  request_details: Dict[str, Any]) -> Dict[str, Any]:
        """Process right of correction request"""
        
        field_to_correct = request_details.get('field')
        new_value = request_details.get('new_value')
        
        if not field_to_correct or new_value is None:
            return {
                "status": "rejected",
                "reason": "Field to correct and new value must be specified"
            }
        
        # Update data principal information
        if field_to_correct in ['name', 'email', 'mobile', 'preferred_language']:
            self.conn.execute(f'''
                UPDATE data_principals 
                SET {field_to_correct} = ?, updated_at = CURRENT_TIMESTAMP
                WHERE principal_id = ?
            ''', (new_value, principal_id))
            
            self.conn.commit()
            
            return {
                "status": "completed",
                "corrected_field": field_to_correct,
                "new_value": new_value,
                "updated_at": datetime.now().isoformat()
            }
        else:
            return {
                "status": "rejected",
                "reason": f"Field {field_to_correct} cannot be corrected through this mechanism"
            }
    
    def _process_erasure_request(self, principal_id: str, 
                               request_details: Dict[str, Any]) -> Dict[str, Any]:
        """Process right of erasure request"""
        
        # Check if there are legal obligations to retain data
        retention_obligations = self._check_legal_retention_obligations(principal_id)
        
        if retention_obligations:
            return {
                "status": "partial_erasure",
                "message": "Some data must be retained due to legal obligations",
                "retained_data": retention_obligations,
                "erased_data": "Marketing and analytics data has been erased"
            }
        else:
            # Full erasure possible
            self._erase_principal_data(principal_id)
            
            return {
                "status": "completed",
                "message": "All personal data has been erased",
                "erased_at": datetime.now().isoformat()
            }
    
    def report_data_breach(self, breach: BreachNotification) -> str:
        """Report a personal data breach"""
        
        self.conn.execute('''
            INSERT INTO breach_notifications 
            (breach_id, fiduciary_id, discovered_at, affected_principals_count,
             breach_type, severity, personal_data_affected, potential_harm,
             mitigation_measures, notification_sent_to_principals)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            breach.breach_id,
            breach.fiduciary_id,
            breach.discovered_at,
            breach.affected_principals_count,
            breach.breach_type,
            breach.severity,
            json.dumps(breach.personal_data_affected),
            breach.potential_harm,
            json.dumps(breach.mitigation_measures),
            breach.notification_sent_to_principals
        ))
        
        # If it's a high-severity breach, automatically report to Data Protection Board
        if breach.severity in ['high', 'critical']:
            self._report_to_data_protection_board(breach)
        
        # Notify affected data principals if required
        if breach.affected_principals_count > 0 and breach.severity != 'low':
            self._notify_affected_principals(breach)
        
        self.conn.commit()
        
        logger.info(f"Data breach reported: {breach.breach_id}")
        
        return breach.breach_id
    
    def _report_to_data_protection_board(self, breach: BreachNotification):
        """Report high-severity breach to Data Protection Board of India"""
        
        # Update reported timestamp
        self.conn.execute('''
            UPDATE breach_notifications 
            SET reported_to_board_at = ?
            WHERE breach_id = ?
        ''', (datetime.now(), breach.breach_id))
        
        # In real implementation, this would integrate with official reporting channels
        logger.info(f"Breach {breach.breach_id} reported to Data Protection Board of India")
    
    def _notify_affected_principals(self, breach: BreachNotification):
        """Notify affected data principals about the breach"""
        
        # In real implementation, this would send notifications via email, SMS, or app
        logger.info(f"Notifying {breach.affected_principals_count} affected data principals")
    
    def submit_grievance(self, grievance: GrievanceRecord) -> str:
        """Submit a grievance from data principal"""
        
        self.conn.execute('''
            INSERT INTO grievances 
            (grievance_id, principal_id, fiduciary_id, grievance_type,
             submitted_at, description, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            grievance.grievance_id,
            grievance.principal_id,
            grievance.fiduciary_id,
            grievance.grievance_type.value,
            grievance.submitted_at,
            grievance.description,
            grievance.status
        ))
        
        self.conn.commit()
        
        # Auto-acknowledge grievance
        self._acknowledge_grievance(grievance.grievance_id)
        
        logger.info(f"Grievance submitted: {grievance.grievance_id}")
        
        return grievance.grievance_id
    
    def _acknowledge_grievance(self, grievance_id: str):
        """Acknowledge grievance receipt"""
        # In real implementation, this would send acknowledgment to data principal
        logger.info(f"Grievance acknowledged: {grievance_id}")
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive DPDP Act compliance report"""
        
        # Consent statistics
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total_consents,
                COUNT(CASE WHEN consent_withdrawn_at IS NULL THEN 1 END) as active_consents,
                COUNT(CASE WHEN consent_withdrawn_at IS NOT NULL THEN 1 END) as withdrawn_consents,
                COUNT(CASE WHEN cross_border_transfer = 1 THEN 1 END) as cross_border_consents
            FROM consent_records
        ''')
        
        consent_stats = cursor.fetchone()
        
        # Data principal statistics
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total_principals,
                COUNT(CASE WHEN age_category = 'child' THEN 1 END) as child_principals,
                COUNT(CASE WHEN is_person_with_disability = 1 THEN 1 END) as disabled_principals
            FROM data_principals
        ''')
        
        principal_stats = cursor.fetchone()
        
        # Breach statistics
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total_breaches,
                COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_breaches,
                COUNT(CASE WHEN reported_to_board_at IS NOT NULL THEN 1 END) as reported_breaches
            FROM breach_notifications
        ''')
        
        breach_stats = cursor.fetchone()
        
        # Grievance statistics
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total_grievances,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_grievances,
                COUNT(CASE WHEN escalated_to_board = 1 THEN 1 END) as escalated_grievances
            FROM grievances
        ''')
        
        grievance_stats = cursor.fetchone()
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(
            consent_stats, principal_stats, breach_stats, grievance_stats
        )
        
        return {
            "fiduciary_id": self.fiduciary_id,
            "fiduciary_name": self.fiduciary_name,
            "fiduciary_class": self.fiduciary_class.value,
            "report_generated_at": datetime.now().isoformat(),
            "compliance_score": compliance_score,
            "consent_statistics": {
                "total_consents": consent_stats[0],
                "active_consents": consent_stats[1],
                "withdrawn_consents": consent_stats[2],
                "cross_border_consents": consent_stats[3]
            },
            "data_principal_statistics": {
                "total_principals": principal_stats[0],
                "child_principals": principal_stats[1],
                "disabled_principals": principal_stats[2]
            },
            "breach_statistics": {
                "total_breaches": breach_stats[0],
                "critical_breaches": breach_stats[1],
                "reported_breaches": breach_stats[2]
            },
            "grievance_statistics": {
                "total_grievances": grievance_stats[0],
                "resolved_grievances": grievance_stats[1],
                "escalated_grievances": grievance_stats[2]
            },
            "recommendations": self._generate_compliance_recommendations(compliance_score)
        }
    
    def _calculate_compliance_score(self, consent_stats, principal_stats, 
                                  breach_stats, grievance_stats) -> float:
        """Calculate overall DPDP Act compliance score"""
        score = 100.0
        
        # Deduct for breaches
        if breach_stats[1] > 0:  # Critical breaches
            score -= breach_stats[1] * 20
        
        if breach_stats[0] > breach_stats[2]:  # Unreported breaches
            score -= (breach_stats[0] - breach_stats[2]) * 10
        
        # Deduct for unresolved grievances
        if grievance_stats[0] > grievance_stats[1]:  # Unresolved grievances
            unresolved_ratio = (grievance_stats[0] - grievance_stats[1]) / max(grievance_stats[0], 1)
            score -= unresolved_ratio * 15
        
        # Bonus for good consent practices
        if consent_stats[0] > 0:
            withdrawal_ratio = consent_stats[2] / consent_stats[0]
            if withdrawal_ratio < 0.1:  # Less than 10% withdrawal rate
                score += 5
        
        return max(0, min(100, score))
    
    def _generate_compliance_recommendations(self, compliance_score: float) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if compliance_score < 60:
            recommendations.extend([
                "🚨 URGENT: Compliance score is below acceptable threshold",
                "📋 Conduct immediate compliance audit",
                "🔧 Implement comprehensive data governance framework"
            ])
        elif compliance_score < 80:
            recommendations.extend([
                "⚠️ Compliance needs improvement",
                "📊 Review consent collection processes",
                "🔍 Enhance breach detection mechanisms"
            ])
        else:
            recommendations.extend([
                "✅ Good compliance posture maintained",
                "🔄 Continue regular compliance monitoring",
                "📈 Consider implementing advanced privacy technologies"
            ])
        
        # General recommendations
        recommendations.extend([
            "📚 Regular staff training on DPDP Act requirements",
            "🔐 Implement Privacy by Design principles",
            "📞 Ensure grievance redressal mechanism is accessible",
            "🌍 Review cross-border transfer agreements"
        ])
        
        return recommendations
    
    def _get_processing_activities_for_principal(self, principal_id: str) -> List[Dict]:
        """Get processing activities affecting this principal"""
        # Mock implementation - in real system, would query actual processing records
        return [
            {
                "activity": "Customer service",
                "purpose": "Responding to customer queries",
                "lawful_basis": "legitimate_use"
            },
            {
                "activity": "Marketing communications",
                "purpose": "Sending promotional offers",
                "lawful_basis": "consent"
            }
        ]
    
    def _get_retention_schedule(self, principal_id: str) -> Dict[str, str]:
        """Get data retention schedule for principal"""
        return {
            "contact_information": "3 years after last transaction",
            "transaction_history": "7 years for financial records",
            "marketing_preferences": "2 years after withdrawal of consent"
        }
    
    def _get_third_party_sharing_info(self, principal_id: str) -> List[Dict]:
        """Get third party sharing information"""
        return [
            {
                "recipient": "Payment processor",
                "purpose": "Transaction processing",
                "data_shared": ["Name", "Payment details"],
                "location": "India"
            }
        ]
    
    def _check_legal_retention_obligations(self, principal_id: str) -> List[str]:
        """Check legal obligations to retain data"""
        return [
            "Income Tax Act - Transaction records (6 years)",
            "Company Law - Customer records (8 years)"
        ]
    
    def _erase_principal_data(self, principal_id: str):
        """Erase all data for a principal (where legally permissible)"""
        # In real implementation, would coordinate across all systems
        logger.info(f"Erasing data for principal: {principal_id}")

def create_sample_dpdp_data():
    """Create sample DPDP compliance data"""
    
    # Create compliance system
    system = DPDPActComplianceSystem(
        "Flipkart India Pvt Ltd", 
        DataFiduciaryClass.SIGNIFICANT_DATA_FIDUCIARY
    )
    
    # Register sample data principals
    principals = [
        DataPrincipal(
            principal_id="DP001",
            name="राज शर्मा",
            email="raj.sharma@email.com",
            mobile="9876543210",
            age_category="adult",
            is_person_with_disability=False,
            preferred_language="Hindi",
            jurisdiction_state="Maharashtra",
            created_at=datetime.now()
        ),
        DataPrincipal(
            principal_id="DP002", 
            name="प्रिया पटेल",
            email="priya.patel@email.com",
            mobile="9876543211",
            age_category="adult",
            is_person_with_disability=False,
            preferred_language="Gujarati",
            jurisdiction_state="Gujarat",
            created_at=datetime.now()
        )
    ]
    
    for principal in principals:
        system.register_data_principal(principal)
    
    # Collect sample consents
    consent1 = ConsentRecord(
        consent_id="CNS001",
        principal_id="DP001",
        fiduciary_id=system.fiduciary_id,
        purpose="E-commerce order processing and customer service",
        data_categories=["Name", "Email", "Mobile", "Address", "Payment info"],
        consent_given_at=datetime.now(),
        consent_withdrawn_at=None,
        consent_method="digital_form",
        language_used="Hindi",
        is_informed_consent=True,
        is_freely_given=True,
        specific_purposes=["Order processing", "Delivery", "Customer support"],
        retention_period=1095,  # 3 years
        third_party_sharing=True,
        cross_border_transfer=False
    )
    
    system.collect_consent(consent1)
    
    return system

def main():
    """Main function demonstrating DPDP Act compliance"""
    print("🇮🇳 Starting DPDP Act 2023 Compliance System Demo")
    print("=" * 70)
    
    # Create sample system
    print("Creating DPDP Act compliance system...")
    system = create_sample_dpdp_data()
    
    print(f"✅ System created for {system.fiduciary_name}")
    print(f"   Fiduciary ID: {system.fiduciary_id}")
    print(f"   Classification: {system.fiduciary_class.value}")
    print()
    
    # Test data principal rights
    print("🔍 Testing data principal rights...")
    
    # Right to information
    info_request = system.process_data_principal_request(
        "DP001", 
        DataPrincipalRights.RIGHT_TO_INFORMATION,
        {"request_type": "full_information"}
    )
    print(f"Information request processed: {info_request}")
    
    # Right of correction
    correction_request = system.process_data_principal_request(
        "DP001",
        DataPrincipalRights.RIGHT_OF_CORRECTION,
        {"field": "email", "new_value": "raj.new@email.com"}
    )
    print(f"Correction request processed: {correction_request}")
    print()
    
    # Test breach notification
    print("🚨 Testing breach notification...")
    
    breach = BreachNotification(
        breach_id="BR001",
        fiduciary_id=system.fiduciary_id,
        discovered_at=datetime.now(),
        reported_to_board_at=None,
        affected_principals_count=1000,
        breach_type="unauthorized_access",
        severity="high",
        personal_data_affected=["Name", "Email", "Mobile"],
        potential_harm="Identity theft, spam calls",
        mitigation_measures=["Password reset", "Account monitoring", "Security enhancement"],
        notification_sent_to_principals=False
    )
    
    breach_id = system.report_data_breach(breach)
    print(f"Breach reported: {breach_id}")
    print()
    
    # Test grievance submission
    print("📝 Testing grievance submission...")
    
    grievance = GrievanceRecord(
        grievance_id="GR001",
        principal_id="DP001",
        fiduciary_id=system.fiduciary_id,
        grievance_type=DataPrincipalRights.RIGHT_OF_CORRECTION,
        submitted_at=datetime.now(),
        description="मेरी profile में गलत जानकारी है, कृपया सुधार करें",
        status="submitted",
        resolved_at=None,
        resolution_details=None,
        escalated_to_board=False
    )
    
    grievance_id = system.submit_grievance(grievance)
    print(f"Grievance submitted: {grievance_id}")
    print()
    
    # Test consent withdrawal
    print("❌ Testing consent withdrawal...")
    withdrawal_success = system.withdraw_consent("DP001", "CNS001", "user_request")
    print(f"Consent withdrawal successful: {withdrawal_success}")
    print()
    
    # Generate compliance report
    print("📊 Generating compliance report...")
    report = system.generate_compliance_report()
    
    print(f"Compliance Score: {report['compliance_score']:.1f}%")
    print(f"Total Data Principals: {report['data_principal_statistics']['total_principals']}")
    print(f"Active Consents: {report['consent_statistics']['active_consents']}")
    print(f"Withdrawn Consents: {report['consent_statistics']['withdrawn_consents']}")
    print(f"Total Breaches: {report['breach_statistics']['total_breaches']}")
    print(f"Total Grievances: {report['grievance_statistics']['total_grievances']}")
    print()
    
    print("🚀 Recommendations:")
    for i, recommendation in enumerate(report['recommendations'], 1):
        print(f"{i}. {recommendation}")
    
    print("\n✅ DPDP Act 2023 Compliance System demo completed successfully!")

if __name__ == "__main__":
    main()
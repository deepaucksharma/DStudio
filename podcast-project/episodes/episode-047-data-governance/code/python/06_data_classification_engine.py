#!/usr/bin/env python3
"""
Automated Data Classification Engine
Episode 47: Data Governance at Scale

AI-powered data classification system जो automatically detect करती है कि
कौन सा data sensitive है और कैसे classify करना चाहिए।

Author: Hindi Podcast Series
Context: ML-based data classification for governance automation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Set, Tuple
import re
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import json
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataSensitivityLevel(Enum):
    """Data sensitivity classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # Highest sensitivity
    PERSONAL = "personal"      # PII data
    SENSITIVE_PERSONAL = "sensitive_personal"  # Special category PII

class DataCategory(Enum):
    """Types of data categories"""
    FINANCIAL = "financial"
    PERSONAL_IDENTITY = "personal_identity"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    CONTACT = "contact_information"
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    BUSINESS = "business_data"
    OPERATIONAL = "operational"

class ComplianceRegime(Enum):
    """Applicable compliance regimes"""
    GDPR = "gdpr"
    DPDP_ACT = "dpdp_act"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    RBI_GUIDELINES = "rbi_guidelines"

@dataclass
class ClassificationResult:
    """Result of data classification"""
    column_name: str
    sensitivity_level: DataSensitivityLevel
    data_category: DataCategory
    confidence_score: float
    applicable_regulations: List[ComplianceRegime]
    encryption_required: bool
    access_restrictions: List[str]
    retention_requirements: Dict[str, Any]
    sample_patterns: List[str]

class DataClassificationEngine:
    """
    AI-powered data classification engine
    
    Features:
    - Pattern-based classification using regex
    - ML-based content classification
    - Statistical analysis for data types
    - Indian regulatory compliance mapping
    - Confidence scoring
    - Automated policy recommendations
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.classification_rules = {}
        self.ml_model = None
        self.vectorizer = None
        self.model_path = model_path
        self.setup_indian_patterns()
        self.setup_classification_rules()
        
        if model_path and Path(model_path).exists():
            self.load_trained_model()
        
        logger.info("Data Classification Engine initialized")
    
    def setup_indian_patterns(self):
        """Setup Indian-specific data patterns"""
        self.indian_patterns = {
            # Identity patterns
            'aadhaar': re.compile(r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b'),
            'pan': re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'),
            'voter_id': re.compile(r'\b[A-Z]{3}[0-9]{7}\b'),
            'passport': re.compile(r'\b[A-Z][0-9]{7}\b'),
            'driving_license': re.compile(r'\b[A-Z]{2}[0-9]{2}[A-Z]?[0-9]{11}\b'),
            
            # Financial patterns
            'bank_account': re.compile(r'\b[0-9]{9,18}\b'),
            'ifsc_code': re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b'),
            'credit_card': re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b'),
            'upi_id': re.compile(r'\b[a-zA-Z0-9.-]{2,256}@[a-zA-Z][a-zA-Z0-9.-]+\b'),
            
            # Contact patterns
            'indian_mobile': re.compile(r'(\+91|91)?[6789]\d{9}'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'pincode': re.compile(r'\b[1-9][0-9]{5}\b'),
            
            # Vehicle and registration
            'vehicle_registration': re.compile(r'\b[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}\b'),
            'gstin': re.compile(r'\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}[Z]{1}[0-9A-Z]{1}\b'),
            
            # Health patterns
            'medical_license': re.compile(r'\b[0-9]{4,7}\b'),  # Simplified pattern
        }
        
        logger.info("Indian data patterns initialized")
    
    def setup_classification_rules(self):
        """Setup rule-based classification logic"""
        self.classification_rules = {
            # Aadhaar - Highest sensitivity
            'aadhaar': {
                'sensitivity': DataSensitivityLevel.RESTRICTED,
                'category': DataCategory.PERSONAL_IDENTITY,
                'regulations': [ComplianceRegime.DPDP_ACT, ComplianceRegime.GDPR],
                'encryption_required': True,
                'access_restrictions': ['legal_team', 'compliance_officer'],
                'retention_days': 2555  # 7 years for KYC compliance
            },
            
            # PAN - High sensitivity
            'pan': {
                'sensitivity': DataSensitivityLevel.CONFIDENTIAL,
                'category': DataCategory.FINANCIAL,
                'regulations': [ComplianceRegime.DPDP_ACT, ComplianceRegime.RBI_GUIDELINES],
                'encryption_required': True,
                'access_restrictions': ['finance_team', 'compliance_officer'],
                'retention_days': 2555
            },
            
            # Credit card - Restricted
            'credit_card': {
                'sensitivity': DataSensitivityLevel.RESTRICTED,
                'category': DataCategory.FINANCIAL,
                'regulations': [ComplianceRegime.PCI_DSS, ComplianceRegime.DPDP_ACT],
                'encryption_required': True,
                'access_restrictions': ['payment_team'],
                'retention_days': 90  # Minimal retention for PCI compliance
            },
            
            # Email - Personal
            'email': {
                'sensitivity': DataSensitivityLevel.PERSONAL,
                'category': DataCategory.CONTACT,
                'regulations': [ComplianceRegime.GDPR, ComplianceRegime.DPDP_ACT],
                'encryption_required': False,
                'access_restrictions': ['marketing_team', 'customer_service'],
                'retention_days': 1095  # 3 years
            },
            
            # Mobile - Personal
            'indian_mobile': {
                'sensitivity': DataSensitivityLevel.PERSONAL,
                'category': DataCategory.CONTACT,
                'regulations': [ComplianceRegime.DPDP_ACT, ComplianceRegime.GDPR],
                'encryption_required': False,
                'access_restrictions': ['customer_service', 'support_team'],
                'retention_days': 1095
            },
            
            # Bank account - Confidential
            'bank_account': {
                'sensitivity': DataSensitivityLevel.CONFIDENTIAL,
                'category': DataCategory.FINANCIAL,
                'regulations': [ComplianceRegime.RBI_GUIDELINES, ComplianceRegime.DPDP_ACT],
                'encryption_required': True,
                'access_restrictions': ['finance_team'],
                'retention_days': 2555
            }
        }
    
    def classify_column(self, df: pd.DataFrame, column_name: str, 
                       sample_size: int = 1000) -> ClassificationResult:
        """Classify a single column"""
        
        if column_name not in df.columns:
            raise ValueError(f"Column {column_name} not found in DataFrame")
        
        # Sample data for analysis
        column_data = df[column_name].dropna()
        if len(column_data) == 0:
            return self._create_empty_classification(column_name)
        
        sample_data = column_data.sample(n=min(sample_size, len(column_data)))
        
        # Pattern-based classification
        pattern_results = self._classify_by_patterns(sample_data, column_name)
        
        # Statistical classification
        stats_results = self._classify_by_statistics(sample_data, column_name)
        
        # Content-based classification (if ML model available)
        content_results = None
        if self.ml_model:
            content_results = self._classify_by_content(sample_data, column_name)
        
        # Combine results and determine final classification
        final_classification = self._combine_classification_results(
            column_name, pattern_results, stats_results, content_results
        )
        
        return final_classification
    
    def _classify_by_patterns(self, sample_data: pd.Series, 
                            column_name: str) -> Dict[str, Any]:
        """Classify using pattern matching"""
        pattern_matches = {}
        total_samples = len(sample_data)
        
        for pattern_name, pattern in self.indian_patterns.items():
            match_count = 0
            sample_matches = []
            
            for value in sample_data:
                if pd.isna(value):
                    continue
                
                matches = pattern.findall(str(value))
                if matches:
                    match_count += 1
                    sample_matches.extend(matches[:2])  # Store first 2 matches
            
            if match_count > 0:
                confidence = match_count / total_samples
                pattern_matches[pattern_name] = {
                    'match_count': match_count,
                    'confidence': confidence,
                    'sample_matches': sample_matches[:5]  # Top 5 samples
                }
        
        return pattern_matches
    
    def _classify_by_statistics(self, sample_data: pd.Series, 
                              column_name: str) -> Dict[str, Any]:
        """Classify using statistical analysis"""
        stats = {
            'data_type': str(sample_data.dtype),
            'unique_values': sample_data.nunique(),
            'total_values': len(sample_data),
            'null_percentage': sample_data.isnull().sum() / len(sample_data) * 100,
            'avg_length': sample_data.astype(str).str.len().mean() if not sample_data.empty else 0,
            'min_length': sample_data.astype(str).str.len().min() if not sample_data.empty else 0,
            'max_length': sample_data.astype(str).str.len().max() if not sample_data.empty else 0
        }
        
        # Infer category based on statistics
        inferred_category = self._infer_category_from_stats(stats, column_name)
        
        return {
            'stats': stats,
            'inferred_category': inferred_category
        }
    
    def _classify_by_content(self, sample_data: pd.Series, 
                           column_name: str) -> Dict[str, Any]:
        """Classify using ML model on content"""
        if not self.ml_model or not self.vectorizer:
            return None
        
        try:
            # Prepare text data for ML model
            text_data = sample_data.astype(str).tolist()
            
            # Transform text using fitted vectorizer
            X = self.vectorizer.transform(text_data)
            
            # Predict using trained model
            predictions = self.ml_model.predict(X)
            prediction_proba = self.ml_model.predict_proba(X)
            
            # Get most common prediction and confidence
            unique_predictions, counts = np.unique(predictions, return_counts=True)
            most_common_prediction = unique_predictions[np.argmax(counts)]
            confidence = np.max(counts) / len(predictions)
            
            return {
                'predicted_category': most_common_prediction,
                'confidence': confidence,
                'all_predictions': predictions.tolist()
            }
        
        except Exception as e:
            logger.warning(f"ML classification failed: {e}")
            return None
    
    def _infer_category_from_stats(self, stats: Dict[str, Any], 
                                 column_name: str) -> DataCategory:
        """Infer data category from statistical properties"""
        
        # Check column name patterns
        column_lower = column_name.lower()
        
        if any(keyword in column_lower for keyword in ['email', 'mail']):
            return DataCategory.CONTACT
        elif any(keyword in column_lower for keyword in ['phone', 'mobile', 'contact']):
            return DataCategory.CONTACT
        elif any(keyword in column_lower for keyword in ['name', 'first_name', 'last_name']):
            return DataCategory.PERSONAL_IDENTITY
        elif any(keyword in column_lower for keyword in ['age', 'dob', 'birth', 'gender']):
            return DataCategory.DEMOGRAPHIC
        elif any(keyword in column_lower for keyword in ['salary', 'income', 'amount', 'price']):
            return DataCategory.FINANCIAL
        elif any(keyword in column_lower for keyword in ['address', 'city', 'state', 'country']):
            return DataCategory.CONTACT
        elif any(keyword in column_lower for keyword in ['id', 'uuid', 'key']):
            return DataCategory.TECHNICAL
        else:
            # Default based on data characteristics
            if stats['data_type'] == 'object' and stats['avg_length'] > 50:
                return DataCategory.BEHAVIORAL  # Likely free text
            elif stats['unique_values'] / stats['total_values'] > 0.8:
                return DataCategory.TECHNICAL  # Likely identifiers
            else:
                return DataCategory.BUSINESS
    
    def _combine_classification_results(self, column_name: str,
                                      pattern_results: Dict,
                                      stats_results: Dict,
                                      content_results: Optional[Dict]) -> ClassificationResult:
        """Combine all classification results into final result"""
        
        # Start with default classification
        sensitivity_level = DataSensitivityLevel.INTERNAL
        data_category = stats_results['inferred_category']
        confidence_score = 0.3  # Low default confidence
        applicable_regulations = []
        encryption_required = False
        access_restrictions = ['all_employees']
        sample_patterns = []
        
        # Check if any pattern matches found
        if pattern_results:
            # Get the highest confidence pattern match
            best_pattern = max(pattern_results.items(), 
                             key=lambda x: x[1]['confidence'])
            pattern_name, pattern_data = best_pattern
            
            if pattern_data['confidence'] > 0.1:  # At least 10% match rate
                # Use pattern-based classification
                rule = self.classification_rules.get(pattern_name, {})
                
                sensitivity_level = rule.get('sensitivity', DataSensitivityLevel.PERSONAL)
                data_category = rule.get('category', data_category)
                confidence_score = min(0.9, pattern_data['confidence'] + 0.1)
                applicable_regulations = rule.get('regulations', [])
                encryption_required = rule.get('encryption_required', False)
                access_restrictions = rule.get('access_restrictions', ['all_employees'])
                sample_patterns = pattern_data.get('sample_matches', [])
        
        # Adjust based on content classification if available
        if content_results and content_results['confidence'] > 0.6:
            # High confidence ML prediction can override pattern matching
            ml_category = content_results['predicted_category']
            if hasattr(DataCategory, ml_category.upper()):
                data_category = DataCategory(ml_category.lower())
                confidence_score = max(confidence_score, content_results['confidence'])
        
        # Determine retention requirements
        retention_requirements = self._determine_retention_requirements(
            sensitivity_level, data_category, applicable_regulations
        )
        
        return ClassificationResult(
            column_name=column_name,
            sensitivity_level=sensitivity_level,
            data_category=data_category,
            confidence_score=confidence_score,
            applicable_regulations=applicable_regulations,
            encryption_required=encryption_required,
            access_restrictions=access_restrictions,
            retention_requirements=retention_requirements,
            sample_patterns=sample_patterns
        )
    
    def _determine_retention_requirements(self, sensitivity_level: DataSensitivityLevel,
                                        data_category: DataCategory,
                                        regulations: List[ComplianceRegime]) -> Dict[str, Any]:
        """Determine data retention requirements"""
        
        base_retention_days = 365  # Default 1 year
        
        # Adjust based on data category
        category_adjustments = {
            DataCategory.FINANCIAL: 2555,  # 7 years for financial data
            DataCategory.PERSONAL_IDENTITY: 1095,  # 3 years for PII
            DataCategory.HEALTH: 1825,  # 5 years for health data
            DataCategory.CONTACT: 1095,  # 3 years for contact info
            DataCategory.BEHAVIORAL: 730,  # 2 years for behavioral data
            DataCategory.TECHNICAL: 365,  # 1 year for technical data
        }
        
        retention_days = category_adjustments.get(data_category, base_retention_days)
        
        # Adjust based on regulations
        regulation_requirements = []
        if ComplianceRegime.RBI_GUIDELINES in regulations:
            retention_days = max(retention_days, 2555)  # RBI requires 7 years
            regulation_requirements.append("RBI Guidelines: 7 years retention")
        
        if ComplianceRegime.PCI_DSS in regulations:
            retention_days = min(retention_days, 365)  # PCI DSS recommends minimal retention
            regulation_requirements.append("PCI DSS: Minimal retention recommended")
        
        if ComplianceRegime.DPDP_ACT in regulations:
            regulation_requirements.append("DPDP Act: Purpose-limited retention")
        
        return {
            'retention_days': retention_days,
            'retention_years': round(retention_days / 365, 1),
            'regulation_requirements': regulation_requirements,
            'review_required': sensitivity_level in [DataSensitivityLevel.RESTRICTED, DataSensitivityLevel.SENSITIVE_PERSONAL]
        }
    
    def _create_empty_classification(self, column_name: str) -> ClassificationResult:
        """Create classification result for empty column"""
        return ClassificationResult(
            column_name=column_name,
            sensitivity_level=DataSensitivityLevel.PUBLIC,
            data_category=DataCategory.TECHNICAL,
            confidence_score=0.0,
            applicable_regulations=[],
            encryption_required=False,
            access_restrictions=['all_employees'],
            retention_requirements={'retention_days': 365, 'retention_years': 1.0, 'regulation_requirements': [], 'review_required': False},
            sample_patterns=[]
        )
    
    def classify_dataset(self, df: pd.DataFrame) -> Dict[str, ClassificationResult]:
        """Classify all columns in a dataset"""
        
        logger.info(f"Starting classification of dataset with {len(df.columns)} columns")
        
        results = {}
        
        for column in df.columns:
            try:
                logger.info(f"Classifying column: {column}")
                classification = self.classify_column(df, column)
                results[column] = classification
                
            except Exception as e:
                logger.error(f"Failed to classify column {column}: {e}")
                results[column] = self._create_empty_classification(column)
        
        logger.info(f"Classification complete. Results: {len(results)} columns")
        
        return results
    
    def generate_governance_policies(self, classifications: Dict[str, ClassificationResult]) -> Dict[str, Any]:
        """Generate data governance policies based on classification results"""
        
        # Aggregate statistics
        sensitivity_counts = {}
        category_counts = {}
        regulation_counts = {}
        encryption_required_count = 0
        
        for classification in classifications.values():
            # Count sensitivity levels
            if classification.sensitivity_level not in sensitivity_counts:
                sensitivity_counts[classification.sensitivity_level] = 0
            sensitivity_counts[classification.sensitivity_level] += 1
            
            # Count categories
            if classification.data_category not in category_counts:
                category_counts[classification.data_category] = 0
            category_counts[classification.data_category] += 1
            
            # Count regulations
            for regulation in classification.applicable_regulations:
                if regulation not in regulation_counts:
                    regulation_counts[regulation] = 0
                regulation_counts[regulation] += 1
            
            # Count encryption requirements
            if classification.encryption_required:
                encryption_required_count += 1
        
        # Generate policy recommendations
        policy_recommendations = []
        
        # High-risk data policies
        restricted_count = sensitivity_counts.get(DataSensitivityLevel.RESTRICTED, 0)
        if restricted_count > 0:
            policy_recommendations.append(f"🔒 {restricted_count} columns contain restricted data - implement field-level encryption")
        
        sensitive_personal_count = sensitivity_counts.get(DataSensitivityLevel.SENSITIVE_PERSONAL, 0)
        if sensitive_personal_count > 0:
            policy_recommendations.append(f"🏥 {sensitive_personal_count} columns contain sensitive personal data - special handling required")
        
        # Encryption policies
        if encryption_required_count > 0:
            policy_recommendations.append(f"🔐 {encryption_required_count} columns require encryption at rest")
        
        # Compliance policies
        if ComplianceRegime.DPDP_ACT in regulation_counts:
            policy_recommendations.append("🇮🇳 DPDP Act compliance required - implement consent management")
        
        if ComplianceRegime.GDPR in regulation_counts:
            policy_recommendations.append("🇪🇺 GDPR compliance required - implement data subject rights")
        
        if ComplianceRegime.PCI_DSS in regulation_counts:
            policy_recommendations.append("💳 PCI DSS compliance required - minimize card data retention")
        
        # Access control policies
        access_control_matrix = self._generate_access_control_matrix(classifications)
        
        return {
            'dataset_summary': {
                'total_columns': len(classifications),
                'sensitivity_distribution': {k.value: v for k, v in sensitivity_counts.items()},
                'category_distribution': {k.value: v for k, v in category_counts.items()},
                'regulation_coverage': {k.value: v for k, v in regulation_counts.items()},
                'encryption_required_columns': encryption_required_count
            },
            'policy_recommendations': policy_recommendations,
            'access_control_matrix': access_control_matrix,
            'retention_schedule': self._generate_retention_schedule(classifications),
            'compliance_checklist': self._generate_compliance_checklist(regulation_counts)
        }
    
    def _generate_access_control_matrix(self, classifications: Dict[str, ClassificationResult]) -> Dict[str, List[str]]:
        """Generate access control matrix"""
        access_matrix = {}
        
        for column_name, classification in classifications.items():
            for role in classification.access_restrictions:
                if role not in access_matrix:
                    access_matrix[role] = []
                access_matrix[role].append(column_name)
        
        return access_matrix
    
    def _generate_retention_schedule(self, classifications: Dict[str, ClassificationResult]) -> Dict[str, Any]:
        """Generate data retention schedule"""
        retention_groups = {}
        
        for column_name, classification in classifications.items():
            retention_days = classification.retention_requirements['retention_days']
            
            if retention_days not in retention_groups:
                retention_groups[retention_days] = []
            retention_groups[retention_days].append({
                'column': column_name,
                'category': classification.data_category.value,
                'regulations': [r.value for r in classification.applicable_regulations]
            })
        
        return {
            'retention_groups': retention_groups,
            'total_retention_policies': len(retention_groups)
        }
    
    def _generate_compliance_checklist(self, regulation_counts: Dict) -> List[str]:
        """Generate compliance checklist"""
        checklist = []
        
        if ComplianceRegime.DPDP_ACT in regulation_counts:
            checklist.extend([
                "☐ Implement DPDP Act consent collection mechanism",
                "☐ Setup data principal rights request handling",
                "☐ Establish grievance redressal process",
                "☐ Configure data localization for Indian users"
            ])
        
        if ComplianceRegime.GDPR in regulation_counts:
            checklist.extend([
                "☐ Implement GDPR consent management",
                "☐ Setup right to erasure (right to be forgotten)",
                "☐ Configure data portability exports",
                "☐ Establish 72-hour breach notification process"
            ])
        
        if ComplianceRegime.PCI_DSS in regulation_counts:
            checklist.extend([
                "☐ Implement PCI DSS encryption requirements",
                "☐ Setup card data tokenization",
                "☐ Establish secure card data transmission",
                "☐ Configure minimal card data retention"
            ])
        
        # General checklist items
        checklist.extend([
            "☐ Setup data quality monitoring",
            "☐ Implement access logging and monitoring",
            "☐ Configure automated data retention deletion",
            "☐ Establish data governance training program"
        ])
        
        return checklist
    
    def export_classification_report(self, classifications: Dict[str, ClassificationResult],
                                   governance_policies: Dict[str, Any],
                                   output_path: str):
        """Export comprehensive classification report"""
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'engine_version': '1.0',
                'total_columns_analyzed': len(classifications)
            },
            'classification_results': {
                column: asdict(result) for column, result in classifications.items()
            },
            'governance_policies': governance_policies,
            'summary_statistics': self._generate_summary_statistics(classifications)
        }
        
        # Convert enums to strings for JSON serialization
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {key: convert_enums(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif hasattr(obj, 'value'):  # Enum
                return obj.value
            else:
                return obj
        
        report = convert_enums(report)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Classification report exported to {output_path}")
    
    def _generate_summary_statistics(self, classifications: Dict[str, ClassificationResult]) -> Dict[str, Any]:
        """Generate summary statistics"""
        
        confidence_scores = [c.confidence_score for c in classifications.values()]
        
        return {
            'average_confidence': np.mean(confidence_scores),
            'min_confidence': np.min(confidence_scores),
            'max_confidence': np.max(confidence_scores),
            'high_confidence_columns': sum(1 for score in confidence_scores if score > 0.7),
            'low_confidence_columns': sum(1 for score in confidence_scores if score < 0.3),
        }

def create_sample_customer_dataset():
    """Create sample customer dataset for testing"""
    np.random.seed(42)
    n_records = 1000
    
    # Generate Indian names
    first_names = ['राज', 'प्रिया', 'अमित', 'सुनीता', 'विकास', 'कविता', 'संजय', 'मीरा']
    last_names = ['शर्मा', 'पटेल', 'कुमार', 'सिंह', 'गुप्ता', 'वर्मा', 'अग्रवाल', 'जैन']
    
    data = {
        'customer_id': [f'CUST{1000 + i:06d}' for i in range(n_records)],
        'first_name': np.random.choice(first_names, n_records),
        'last_name': np.random.choice(last_names, n_records),
        'email': [f'customer{i}@example.com' for i in range(n_records)],
        'mobile_number': [f'9876{np.random.randint(100000, 999999)}' for _ in range(n_records)],
        'aadhaar_number': [f'{np.random.randint(200000000000, 999999999999)}' for _ in range(n_records)],
        'pan_number': [f'ABCDE{np.random.randint(1000, 9999)}F' for _ in range(n_records)],
        'bank_account': [f'{np.random.randint(100000000000, 999999999999999)}' for _ in range(n_records)],
        'credit_card': [f'4{np.random.randint(100000000000000, 999999999999999)}' for _ in range(n_records)],
        'age': np.random.randint(18, 80, n_records),
        'annual_income': np.random.randint(200000, 2000000, n_records),
        'city': np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata'], n_records),
        'registration_date': pd.date_range('2020-01-01', periods=n_records, freq='D')[:n_records],
        'last_login': pd.date_range('2023-01-01', periods=n_records, freq='H')[:n_records],
        'total_purchases': np.random.randint(0, 100, n_records),
        'loyalty_points': np.random.randint(0, 10000, n_records)
    }
    
    return pd.DataFrame(data)

def main():
    """Main function demonstrating data classification engine"""
    print("🤖 Starting AI-Powered Data Classification Engine Demo")
    print("=" * 70)
    
    # Create sample dataset
    print("Creating sample customer dataset...")
    df = create_sample_customer_dataset()
    print(f"✅ Created dataset with {len(df)} records and {len(df.columns)} columns")
    print()
    
    # Initialize classification engine
    print("Initializing data classification engine...")
    engine = DataClassificationEngine()
    print("✅ Classification engine initialized")
    print()
    
    # Classify dataset
    print("🔍 Starting dataset classification...")
    classifications = engine.classify_dataset(df)
    
    # Display classification results
    print("📊 Classification Results:")
    print("-" * 50)
    
    for column_name, result in classifications.items():
        confidence_indicator = "🟢" if result.confidence_score > 0.7 else "🟡" if result.confidence_score > 0.3 else "🔴"
        
        print(f"{confidence_indicator} {column_name}")
        print(f"   Sensitivity: {result.sensitivity_level.value}")
        print(f"   Category: {result.data_category.value}")
        print(f"   Confidence: {result.confidence_score:.2f}")
        print(f"   Encryption Required: {'Yes' if result.encryption_required else 'No'}")
        
        if result.applicable_regulations:
            regulations = [r.value for r in result.applicable_regulations]
            print(f"   Regulations: {', '.join(regulations)}")
        
        if result.sample_patterns:
            print(f"   Sample Patterns: {result.sample_patterns[:2]}")
        
        print()
    
    # Generate governance policies
    print("📋 Generating data governance policies...")
    policies = engine.generate_governance_policies(classifications)
    
    print("Dataset Summary:")
    summary = policies['dataset_summary']
    print(f"  Total Columns: {summary['total_columns']}")
    print(f"  Encryption Required: {summary['encryption_required_columns']} columns")
    print()
    
    print("Policy Recommendations:")
    for i, recommendation in enumerate(policies['policy_recommendations'], 1):
        print(f"  {i}. {recommendation}")
    print()
    
    print("Compliance Checklist:")
    for item in policies['compliance_checklist']:
        print(f"  {item}")
    print()
    
    # Export detailed report
    print("📤 Exporting classification report...")
    engine.export_classification_report(
        classifications, 
        policies, 
        "/tmp/data_classification_report.json"
    )
    print("✅ Report exported to /tmp/data_classification_report.json")
    
    print("\n🚀 Key Insights:")
    
    # High-risk data analysis
    restricted_columns = [name for name, result in classifications.items() 
                         if result.sensitivity_level == DataSensitivityLevel.RESTRICTED]
    if restricted_columns:
        print(f"⚠️ HIGH RISK: {len(restricted_columns)} columns with restricted data:")
        for col in restricted_columns:
            print(f"    - {col}")
    
    # Compliance requirements
    all_regulations = set()
    for result in classifications.values():
        all_regulations.update(result.applicable_regulations)
    
    if all_regulations:
        print(f"📜 COMPLIANCE: Dataset subject to {len(all_regulations)} regulatory frameworks:")
        for regulation in all_regulations:
            print(f"    - {regulation.value}")
    
    print("\n✅ Data Classification Engine demo completed successfully!")

if __name__ == "__main__":
    main()
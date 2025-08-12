#!/usr/bin/env python3
"""
Event Schema Versioning and Evolution
उदाहरण: Paytm transaction events के schema evolution को handle करना

Setup:
pip install jsonschema typing

Indian Context: Paytm app में नए features आते रहते हैं (UPI 2.0, Credit on UPI, etc.)
पुराने transaction events को break किए बिना नए schema support करना:

Version 1.0: Basic transaction (amount, sender, receiver)
Version 2.0: Added merchant_category, transaction_type
Version 3.0: Added cashback_details, loyalty_points
Version 4.0: Added international_transfer, forex_rate

Schema Evolution Strategies:
- Backward compatibility (old consumers can read new events)
- Forward compatibility (new consumers can read old events)
- Schema registry for validation
- Event transformation between versions
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Union, List
from jsonschema import validate, ValidationError
import uuid

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchemaVersion(Enum):
    """Event schema versions"""
    V1_0 = "1.0"
    V2_0 = "2.0"
    V3_0 = "3.0"
    V4_0 = "4.0"

class TransactionType(Enum):
    """Transaction types (introduced in v2.0)"""
    P2P = "peer_to_peer"
    P2M = "peer_to_merchant"
    BILL_PAYMENT = "bill_payment"
    RECHARGE = "recharge"
    INTERNATIONAL = "international"  # v4.0

class MerchantCategory(Enum):
    """Merchant categories (introduced in v2.0)"""
    FOOD_DELIVERY = "food_delivery"
    GROCERY = "grocery"
    FUEL = "fuel"
    MEDICINE = "medicine"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"

# Schema definitions for different versions

TRANSACTION_SCHEMA_V1 = {
    "type": "object",
    "properties": {
        "event_id": {"type": "string"},
        "event_type": {"type": "string"},
        "transaction_id": {"type": "string"},
        "amount": {"type": "number", "minimum": 0},
        "currency": {"type": "string", "enum": ["INR"]},
        "sender_id": {"type": "string"},
        "receiver_id": {"type": "string"},
        "timestamp": {"type": "string"},
        "status": {"type": "string", "enum": ["pending", "completed", "failed"]},
        "schema_version": {"type": "string", "enum": ["1.0"]}
    },
    "required": ["event_id", "transaction_id", "amount", "sender_id", "receiver_id", "schema_version"],
    "additionalProperties": False
}

TRANSACTION_SCHEMA_V2 = {
    "type": "object",
    "properties": {
        "event_id": {"type": "string"},
        "event_type": {"type": "string"},
        "transaction_id": {"type": "string"},
        "amount": {"type": "number", "minimum": 0},
        "currency": {"type": "string", "enum": ["INR"]},
        "sender_id": {"type": "string"},
        "receiver_id": {"type": "string"},
        "timestamp": {"type": "string"},
        "status": {"type": "string", "enum": ["pending", "completed", "failed"]},
        "schema_version": {"type": "string", "enum": ["2.0"]},
        # New fields in v2.0
        "transaction_type": {
            "type": "string", 
            "enum": ["peer_to_peer", "peer_to_merchant", "bill_payment", "recharge"]
        },
        "merchant_category": {
            "type": ["string", "null"],
            "enum": ["food_delivery", "grocery", "fuel", "medicine", "entertainment", "education", None]
        },
        "description": {"type": ["string", "null"]}
    },
    "required": ["event_id", "transaction_id", "amount", "sender_id", "receiver_id", "schema_version", "transaction_type"],
    "additionalProperties": False
}

TRANSACTION_SCHEMA_V3 = {
    "type": "object",
    "properties": {
        "event_id": {"type": "string"},
        "event_type": {"type": "string"},
        "transaction_id": {"type": "string"},
        "amount": {"type": "number", "minimum": 0},
        "currency": {"type": "string", "enum": ["INR"]},
        "sender_id": {"type": "string"},
        "receiver_id": {"type": "string"},
        "timestamp": {"type": "string"},
        "status": {"type": "string", "enum": ["pending", "completed", "failed"]},
        "schema_version": {"type": "string", "enum": ["3.0"]},
        "transaction_type": {
            "type": "string", 
            "enum": ["peer_to_peer", "peer_to_merchant", "bill_payment", "recharge"]
        },
        "merchant_category": {
            "type": ["string", "null"],
            "enum": ["food_delivery", "grocery", "fuel", "medicine", "entertainment", "education", None]
        },
        "description": {"type": ["string", "null"]},
        # New fields in v3.0
        "cashback_details": {
            "type": ["object", "null"],
            "properties": {
                "cashback_amount": {"type": "number", "minimum": 0},
                "cashback_percentage": {"type": "number", "minimum": 0, "maximum": 100},
                "campaign_id": {"type": "string"}
            }
        },
        "loyalty_points": {
            "type": ["object", "null"],
            "properties": {
                "points_earned": {"type": "integer", "minimum": 0},
                "points_redeemed": {"type": "integer", "minimum": 0},
                "tier": {"type": "string", "enum": ["bronze", "silver", "gold", "platinum"]}
            }
        }
    },
    "required": ["event_id", "transaction_id", "amount", "sender_id", "receiver_id", "schema_version", "transaction_type"],
    "additionalProperties": False
}

TRANSACTION_SCHEMA_V4 = {
    "type": "object",
    "properties": {
        "event_id": {"type": "string"},
        "event_type": {"type": "string"},
        "transaction_id": {"type": "string"},
        "amount": {"type": "number", "minimum": 0},
        "currency": {"type": "string", "enum": ["INR", "USD", "EUR", "GBP"]},  # Extended currencies
        "sender_id": {"type": "string"},
        "receiver_id": {"type": "string"},
        "timestamp": {"type": "string"},
        "status": {"type": "string", "enum": ["pending", "completed", "failed"]},
        "schema_version": {"type": "string", "enum": ["4.0"]},
        "transaction_type": {
            "type": "string", 
            "enum": ["peer_to_peer", "peer_to_merchant", "bill_payment", "recharge", "international"]  # Added international
        },
        "merchant_category": {
            "type": ["string", "null"],
            "enum": ["food_delivery", "grocery", "fuel", "medicine", "entertainment", "education", None]
        },
        "description": {"type": ["string", "null"]},
        "cashback_details": {
            "type": ["object", "null"],
            "properties": {
                "cashback_amount": {"type": "number", "minimum": 0},
                "cashback_percentage": {"type": "number", "minimum": 0, "maximum": 100},
                "campaign_id": {"type": "string"}
            }
        },
        "loyalty_points": {
            "type": ["object", "null"],
            "properties": {
                "points_earned": {"type": "integer", "minimum": 0},
                "points_redeemed": {"type": "integer", "minimum": 0},
                "tier": {"type": "string", "enum": ["bronze", "silver", "gold", "platinum"]}
            }
        },
        # New fields in v4.0
        "international_transfer": {
            "type": ["object", "null"],
            "properties": {
                "source_currency": {"type": "string"},
                "target_currency": {"type": "string"},
                "forex_rate": {"type": "number", "minimum": 0},
                "bank_charges": {"type": "number", "minimum": 0},
                "correspondent_bank": {"type": "string"}
            }
        },
        "compliance_details": {
            "type": ["object", "null"],
            "properties": {
                "aml_status": {"type": "string", "enum": ["clear", "under_review", "flagged"]},
                "risk_score": {"type": "integer", "minimum": 0, "maximum": 100},
                "kyc_level": {"type": "string", "enum": ["basic", "full", "enhanced"]}
            }
        }
    },
    "required": ["event_id", "transaction_id", "amount", "sender_id", "receiver_id", "schema_version", "transaction_type"],
    "additionalProperties": False
}

class SchemaRegistry:
    """
    Schema registry - schema versions को manage करता है
    Librarian की तरह - सभी versions organized रखता है
    """
    
    def __init__(self):
        self.schemas = {
            SchemaVersion.V1_0: TRANSACTION_SCHEMA_V1,
            SchemaVersion.V2_0: TRANSACTION_SCHEMA_V2,
            SchemaVersion.V3_0: TRANSACTION_SCHEMA_V3,
            SchemaVersion.V4_0: TRANSACTION_SCHEMA_V4
        }
        self.current_version = SchemaVersion.V4_0
    
    def validate_event(self, event_data: Dict[str, Any]) -> bool:
        """Event को appropriate schema के साथ validate करना"""
        schema_version = event_data.get('schema_version')
        
        if not schema_version:
            logger.error("❌ Schema version missing in event")
            return False
        
        try:
            version_enum = SchemaVersion(schema_version)
            schema = self.schemas[version_enum]
            
            validate(instance=event_data, schema=schema)
            logger.info(f"✅ Event validated against schema v{schema_version}")
            return True
            
        except ValueError:
            logger.error(f"❌ Unknown schema version: {schema_version}")
            return False
        except ValidationError as e:
            logger.error(f"❌ Schema validation failed: {e.message}")
            return False
    
    def get_supported_versions(self) -> List[str]:
        """Supported schema versions list"""
        return [version.value for version in self.schemas.keys()]

class EventTransformer:
    """
    Event transformation between different schema versions
    Translator की तरह - एक version से दूसरे में convert करता है
    """
    
    def __init__(self):
        self.transformers = {
            (SchemaVersion.V1_0, SchemaVersion.V2_0): self._transform_v1_to_v2,
            (SchemaVersion.V2_0, SchemaVersion.V3_0): self._transform_v2_to_v3,
            (SchemaVersion.V3_0, SchemaVersion.V4_0): self._transform_v3_to_v4,
            (SchemaVersion.V2_0, SchemaVersion.V1_0): self._transform_v2_to_v1,
            (SchemaVersion.V3_0, SchemaVersion.V2_0): self._transform_v3_to_v2,
            (SchemaVersion.V4_0, SchemaVersion.V3_0): self._transform_v4_to_v3,
        }
    
    def transform_event(self, event_data: Dict[str, Any], target_version: SchemaVersion) -> Dict[str, Any]:
        """Event को target version में transform करना"""
        current_version = SchemaVersion(event_data.get('schema_version'))
        
        if current_version == target_version:
            return event_data  # No transformation needed
        
        transformer_key = (current_version, target_version)
        
        if transformer_key in self.transformers:
            transformed = self.transformers[transformer_key](event_data.copy())
            logger.info(f"🔄 Event transformed from v{current_version.value} to v{target_version.value}")
            return transformed
        else:
            # Multi-step transformation might be needed
            logger.warning(f"⚠️ Direct transformation from v{current_version.value} to v{target_version.value} not available")
            return self._multi_step_transform(event_data, target_version)
    
    def _transform_v1_to_v2(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """v1.0 to v2.0 transformation"""
        # Add new required fields with default values
        event_data['schema_version'] = "2.0"
        
        # Infer transaction type from receiver_id pattern
        receiver_id = event_data['receiver_id']
        if receiver_id.startswith('MERCHANT_'):
            event_data['transaction_type'] = TransactionType.P2M.value
            # Try to infer merchant category from receiver ID
            if 'FOOD' in receiver_id:
                event_data['merchant_category'] = MerchantCategory.FOOD_DELIVERY.value
            elif 'GROCERY' in receiver_id:
                event_data['merchant_category'] = MerchantCategory.GROCERY.value
            else:
                event_data['merchant_category'] = None
        else:
            event_data['transaction_type'] = TransactionType.P2P.value
            event_data['merchant_category'] = None
        
        event_data['description'] = None
        
        return event_data
    
    def _transform_v2_to_v3(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """v2.0 to v3.0 transformation"""
        event_data['schema_version'] = "3.0"
        
        # Add default values for new fields
        event_data['cashback_details'] = None
        event_data['loyalty_points'] = None
        
        return event_data
    
    def _transform_v3_to_v4(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """v3.0 to v4.0 transformation"""
        event_data['schema_version'] = "4.0"
        
        # Add default values for new fields
        event_data['international_transfer'] = None
        event_data['compliance_details'] = None
        
        return event_data
    
    def _transform_v2_to_v1(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """v2.0 to v1.0 transformation (backward compatibility)"""
        # Remove fields that don't exist in v1.0
        v1_data = {
            'event_id': event_data['event_id'],
            'event_type': event_data.get('event_type'),
            'transaction_id': event_data['transaction_id'],
            'amount': event_data['amount'],
            'currency': event_data['currency'],
            'sender_id': event_data['sender_id'],
            'receiver_id': event_data['receiver_id'],
            'timestamp': event_data.get('timestamp'),
            'status': event_data.get('status'),
            'schema_version': "1.0"
        }
        
        return v1_data
    
    def _transform_v3_to_v2(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """v3.0 to v2.0 transformation"""
        # Remove v3.0 specific fields
        v2_data = event_data.copy()
        v2_data['schema_version'] = "2.0"
        v2_data.pop('cashback_details', None)
        v2_data.pop('loyalty_points', None)
        
        return v2_data
    
    def _transform_v4_to_v3(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """v4.0 to v3.0 transformation"""
        # Remove v4.0 specific fields
        v3_data = event_data.copy()
        v3_data['schema_version'] = "3.0"
        v3_data.pop('international_transfer', None)
        v3_data.pop('compliance_details', None)
        
        # Handle currency restriction
        if v3_data.get('currency') != 'INR':
            v3_data['currency'] = 'INR'  # Default to INR for v3.0
        
        # Handle transaction type restriction
        if v3_data.get('transaction_type') == 'international':
            v3_data['transaction_type'] = 'peer_to_peer'  # Fallback
        
        return v3_data
    
    def _multi_step_transform(self, event_data: Dict[str, Any], target_version: SchemaVersion) -> Dict[str, Any]:
        """Multi-step transformation for complex version jumps"""
        # Example: v1.0 -> v4.0 (via v2.0 and v3.0)
        current_version = SchemaVersion(event_data.get('schema_version'))
        
        # Define transformation path
        version_order = [SchemaVersion.V1_0, SchemaVersion.V2_0, SchemaVersion.V3_0, SchemaVersion.V4_0]
        
        current_index = version_order.index(current_version)
        target_index = version_order.index(target_version)
        
        data = event_data.copy()
        
        if target_index > current_index:
            # Forward transformation
            for i in range(current_index, target_index):
                data = self.transform_event(data, version_order[i + 1])
        else:
            # Backward transformation
            for i in range(current_index, target_index, -1):
                data = self.transform_event(data, version_order[i - 1])
        
        return data

class PaytmTransactionEventGenerator:
    """Sample Paytm transaction event generator"""
    
    def __init__(self):
        self.transformer = EventTransformer()
        self.schema_registry = SchemaRegistry()
    
    def generate_v1_event(self) -> Dict[str, Any]:
        """Generate v1.0 transaction event"""
        return {
            'event_id': str(uuid.uuid4()),
            'event_type': 'transaction.completed',
            'transaction_id': f"PAYTM_{uuid.uuid4().hex[:8].upper()}",
            'amount': 150.0,
            'currency': 'INR',
            'sender_id': 'USER_RAHUL_123',
            'receiver_id': 'MERCHANT_DOMINOS_456',
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'schema_version': '1.0'
        }
    
    def generate_v2_event(self) -> Dict[str, Any]:
        """Generate v2.0 transaction event"""
        return {
            'event_id': str(uuid.uuid4()),
            'event_type': 'transaction.completed',
            'transaction_id': f"PAYTM_{uuid.uuid4().hex[:8].upper()}",
            'amount': 850.0,
            'currency': 'INR',
            'sender_id': 'USER_PRIYA_789',
            'receiver_id': 'MERCHANT_BIGBASKET_123',
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'schema_version': '2.0',
            'transaction_type': TransactionType.P2M.value,
            'merchant_category': MerchantCategory.GROCERY.value,
            'description': 'Monthly grocery shopping'
        }
    
    def generate_v3_event(self) -> Dict[str, Any]:
        """Generate v3.0 transaction event"""
        return {
            'event_id': str(uuid.uuid4()),
            'event_type': 'transaction.completed',
            'transaction_id': f"PAYTM_{uuid.uuid4().hex[:8].upper()}",
            'amount': 1200.0,
            'currency': 'INR',
            'sender_id': 'USER_AMIT_456',
            'receiver_id': 'MERCHANT_SWIGGY_789',
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'schema_version': '3.0',
            'transaction_type': TransactionType.P2M.value,
            'merchant_category': MerchantCategory.FOOD_DELIVERY.value,
            'description': 'Dinner order from restaurant',
            'cashback_details': {
                'cashback_amount': 60.0,
                'cashback_percentage': 5.0,
                'campaign_id': 'FOODIE_FRIDAY'
            },
            'loyalty_points': {
                'points_earned': 12,
                'points_redeemed': 0,
                'tier': 'gold'
            }
        }
    
    def generate_v4_event(self) -> Dict[str, Any]:
        """Generate v4.0 transaction event"""
        return {
            'event_id': str(uuid.uuid4()),
            'event_type': 'transaction.completed',
            'transaction_id': f"PAYTM_{uuid.uuid4().hex[:8].upper()}",
            'amount': 5000.0,
            'currency': 'USD',
            'sender_id': 'USER_NEHA_321',
            'receiver_id': 'INTL_RECEIVER_USA_567',
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'schema_version': '4.0',
            'transaction_type': TransactionType.INTERNATIONAL.value,
            'merchant_category': None,
            'description': 'Remittance to family in USA',
            'cashback_details': None,
            'loyalty_points': {
                'points_earned': 50,
                'points_redeemed': 0,
                'tier': 'platinum'
            },
            'international_transfer': {
                'source_currency': 'INR',
                'target_currency': 'USD',
                'forex_rate': 83.25,
                'bank_charges': 150.0,
                'correspondent_bank': 'JP_MORGAN_CHASE'
            },
            'compliance_details': {
                'aml_status': 'clear',
                'risk_score': 15,
                'kyc_level': 'enhanced'
            }
        }

async def paytm_schema_evolution_demo():
    """Paytm schema evolution demo"""
    print("💳 Paytm Event Schema Evolution Demo")
    print("=" * 50)
    
    generator = PaytmTransactionEventGenerator()
    transformer = EventTransformer()
    schema_registry = SchemaRegistry()
    
    print("🏗️ Schema Registry:")
    supported_versions = schema_registry.get_supported_versions()
    print(f"   📋 Supported Versions: {', '.join(supported_versions)}")
    print()
    
    # Generate events of different versions
    events = {
        'v1.0': generator.generate_v1_event(),
        'v2.0': generator.generate_v2_event(),
        'v3.0': generator.generate_v3_event(),
        'v4.0': generator.generate_v4_event()
    }
    
    print("📄 Generated Events:")
    for version, event in events.items():
        print(f"   ✅ {version}: Transaction {event['transaction_id']} - ₹{event['amount']}")
        
        # Validate event
        is_valid = schema_registry.validate_event(event)
        print(f"      🔍 Schema Validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    
    print()
    
    # Demonstrate backward compatibility
    print("🔄 Schema Transformation Demo:")
    print("=" * 30)
    
    # Transform v4.0 event to older versions
    v4_event = events['v4.0']
    print(f"🎯 Source Event: v4.0 - {v4_event['transaction_id']}")
    print(f"   💰 Amount: ${v4_event['amount']} USD")
    print(f"   🌍 International Transfer: {v4_event['international_transfer']['source_currency']} → {v4_event['international_transfer']['target_currency']}")
    print()
    
    # Transform to v3.0
    v4_to_v3 = transformer.transform_event(v4_event, SchemaVersion.V3_0)
    print(f"📉 Transformed to v3.0:")
    print(f"   💰 Amount: ₹{v4_to_v3['amount']} (currency converted)")
    print(f"   🔄 Transaction Type: {v4_to_v3['transaction_type']}")
    print(f"   ✅ Valid v3.0: {schema_registry.validate_event(v4_to_v3)}")
    print()
    
    # Transform to v2.0
    v4_to_v2 = transformer.transform_event(v4_event, SchemaVersion.V2_0)
    print(f"📉 Transformed to v2.0:")
    print(f"   🔄 Transaction Type: {v4_to_v2['transaction_type']}")
    print(f"   📝 Description: {v4_to_v2.get('description', 'N/A')}")
    print(f"   ✅ Valid v2.0: {schema_registry.validate_event(v4_to_v2)}")
    print()
    
    # Transform to v1.0
    v4_to_v1 = transformer.transform_event(v4_event, SchemaVersion.V1_0)
    print(f"📉 Transformed to v1.0:")
    print(f"   📋 Fields: {list(v4_to_v1.keys())}")
    print(f"   ✅ Valid v1.0: {schema_registry.validate_event(v4_to_v1)}")
    print()
    
    # Demonstrate forward compatibility
    print("🔼 Forward Compatibility Demo:")
    print("=" * 30)
    
    v1_event = events['v1.0']
    print(f"🎯 Source Event: v1.0 - {v1_event['transaction_id']}")
    print(f"   📋 Original Fields: {len(v1_event)} fields")
    
    # Transform to v4.0
    v1_to_v4 = transformer.transform_event(v1_event, SchemaVersion.V4_0)
    print(f"📈 Transformed to v4.0:")
    print(f"   📋 Enhanced Fields: {len(v1_to_v4)} fields")
    print(f"   🔄 Transaction Type: {v1_to_v4['transaction_type']} (inferred)")
    print(f"   🏪 Merchant Category: {v1_to_v4.get('merchant_category', 'N/A')} (inferred)")
    print(f"   ✅ Valid v4.0: {schema_registry.validate_event(v1_to_v4)}")
    print()
    
    # Consumer compatibility demo
    print("👥 Consumer Compatibility Demo:")
    print("=" * 30)
    
    # Simulate different consumers
    consumers = {
        'Legacy Analytics Service': SchemaVersion.V1_0,
        'Fraud Detection Service': SchemaVersion.V2_0,
        'Cashback Service': SchemaVersion.V3_0,
        'Compliance Service': SchemaVersion.V4_0
    }
    
    test_event = events['v4.0']  # Latest event
    
    print(f"📡 Broadcasting event: {test_event['transaction_id']}")
    print()
    
    for consumer_name, required_version in consumers.items():
        print(f"👤 {consumer_name} (requires v{required_version.value}):")
        
        if required_version.value == test_event['schema_version']:
            print("   ✅ Direct consumption - no transformation needed")
        else:
            transformed = transformer.transform_event(test_event, required_version)
            is_valid = schema_registry.validate_event(transformed)
            
            print(f"   🔄 Event transformed to v{required_version.value}")
            print(f"   ✅ Validation: {'PASSED' if is_valid else 'FAILED'}")
            
            # Show relevant fields for the consumer
            if required_version == SchemaVersion.V1_0:
                print(f"   📊 Processed: Amount ₹{transformed['amount']}, Status {transformed['status']}")
            elif required_version == SchemaVersion.V2_0:
                print(f"   🕵️ Processed: {transformed['transaction_type']} transaction")
            elif required_version == SchemaVersion.V3_0:
                cashback = transformed.get('cashback_details')
                if cashback:
                    print(f"   💰 Processed: ₹{cashback['cashback_amount']} cashback")
                else:
                    print("   💰 Processed: No cashback applicable")
        
        print()
    
    print("🎯 Key Benefits Demonstrated:")
    print("   ✅ Backward compatibility - old consumers work with new events")
    print("   ✅ Forward compatibility - new consumers work with old events")
    print("   ✅ Schema validation prevents data corruption")
    print("   ✅ Automatic transformation between versions")
    print("   ✅ Gradual migration path for consumers")
    print("   ✅ No service interruption during schema updates")

if __name__ == "__main__":
    import asyncio
    asyncio.run(paytm_schema_evolution_demo())
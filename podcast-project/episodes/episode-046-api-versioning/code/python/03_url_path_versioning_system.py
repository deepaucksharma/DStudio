#!/usr/bin/env python3
"""
URL Path-based API Versioning System
Inspired by PayTM's API evolution - version in URL path

Example: PayTM ne kaise URL-based versioning use kiya for wallet APIs
/v1/wallet/balance vs /v2/wallet/balance vs /v3/wallet/balance
"""

from flask import Flask, request, jsonify, Blueprint
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EndpointConfig:
    """Configuration for versioned endpoints"""
    version: str
    path: str
    handler: callable
    deprecated: bool = False
    sunset_date: Optional[str] = None

class URLVersionManager:
    """
    URL Path-based API versioning manager
    Example: PayTM wallet API versioning - /v1/wallet, /v2/wallet, /v3/wallet
    """
    
    def __init__(self):
        self.version_patterns = {
            "v1": r"^/v1/",
            "v2": r"^/v2/",
            "v3": r"^/v3/"
        }
        
        self.version_info = {
            "v1": {
                "description": "Initial PayTM wallet API - Basic balance check",
                "deprecated": True,
                "sunset_date": "2024-06-30",
                "features": ["balance_check", "simple_transfer"]
            },
            "v2": {
                "description": "Enhanced wallet API - UPI integration added",
                "deprecated": False,
                "sunset_date": None,
                "features": ["balance_check", "upi_transfer", "qr_payment", "transaction_history"]
            },
            "v3": {
                "description": "Latest wallet API - Advanced features",
                "deprecated": False,
                "sunset_date": None,
                "features": ["balance_check", "upi_transfer", "qr_payment", "transaction_history", 
                           "investment_options", "bill_payments", "loans"]
            }
        }
    
    def extract_version_from_path(self, path: str) -> Optional[str]:
        """Extract API version from URL path"""
        for version, pattern in self.version_patterns.items():
            if re.match(pattern, path):
                return version
        return None
    
    def is_version_deprecated(self, version: str) -> bool:
        """Check if version is deprecated"""
        return self.version_info.get(version, {}).get("deprecated", False)
    
    def get_version_info(self, version: str) -> Dict[str, Any]:
        """Get version information"""
        return self.version_info.get(version, {})

# Initialize Flask app with versioned blueprints
app = Flask(__name__)
version_manager = URLVersionManager()

# Create separate blueprints for each version
v1_bp = Blueprint('v1', __name__, url_prefix='/v1')
v2_bp = Blueprint('v2', __name__, url_prefix='/v2') 
v3_bp = Blueprint('v3', __name__, url_prefix='/v3')

# V1 Endpoints - Basic PayTM wallet functionality
@v1_bp.route('/wallet/balance', methods=['GET'])
def get_balance_v1():
    """
    V1: Basic balance check - Simple response
    PayTM v1 API style
    """
    user_id = request.args.get('user_id', 'USER123')
    
    # Simulate balance fetch
    balance = 5678.50
    
    return jsonify({
        "balance": balance,
        "currency": "INR",
        "user_id": user_id,
        "message": "Balance fetched successfully",
        "api_version": "v1",
        "warning": "⚠️  API v1 is deprecated. Please migrate to v2 or v3",
        "migration_guide": "/docs/migration/v1-to-v2"
    })

@v1_bp.route('/wallet/transfer', methods=['POST'])
def transfer_money_v1():
    """
    V1: Basic money transfer - Limited functionality
    """
    data = request.get_json()
    
    # V1 validation - simple fields only
    required_fields = ['to_user', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "Missing required fields",
            "required": required_fields,
            "api_version": "v1"
        }), 400
    
    # Simulate transfer
    transaction_id = f"TXN_V1_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return jsonify({
        "transaction_id": transaction_id,
        "status": "success",
        "amount": data["amount"],
        "to_user": data["to_user"],
        "message": "Transfer completed successfully",
        "api_version": "v1",
        "warning": "⚠️  Consider using v2 for UPI transfers"
    })

# V2 Endpoints - UPI integrated PayTM wallet
@v2_bp.route('/wallet/balance', methods=['GET'])
def get_balance_v2():
    """
    V2: Enhanced balance check with UPI info
    """
    user_id = request.args.get('user_id', 'USER123')
    
    # Enhanced balance information
    return jsonify({
        "wallet": {
            "balance": 5678.50,
            "currency": "INR",
            "last_updated": datetime.now().isoformat()
        },
        "upi": {
            "id": f"{user_id.lower()}@paytm",
            "linked_banks": ["HDFC", "SBI", "ICICI"],
            "default_bank": "HDFC"
        },
        "user_id": user_id,
        "message": "Enhanced balance information",
        "api_version": "v2"
    })

@v2_bp.route('/wallet/transfer', methods=['POST'])
def transfer_money_v2():
    """
    V2: UPI-enabled money transfer
    """
    data = request.get_json()
    
    # V2 validation - includes UPI fields
    required_fields = ['to_identifier', 'amount', 'transfer_type']
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "Missing required fields",
            "required": required_fields,
            "supported_types": ["wallet", "upi", "bank"],
            "api_version": "v2"
        }), 400
    
    transfer_type = data.get('transfer_type')
    
    if transfer_type == "upi":
        # UPI transfer logic
        transaction_id = f"UPI_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        processing_time = "2-5 minutes"
    elif transfer_type == "wallet":
        # Wallet transfer logic
        transaction_id = f"WALLET_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        processing_time = "Instant"
    else:
        # Bank transfer logic
        transaction_id = f"BANK_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        processing_time = "30 minutes - 2 hours"
    
    return jsonify({
        "transaction_id": transaction_id,
        "status": "initiated",
        "amount": data["amount"],
        "to_identifier": data["to_identifier"],
        "transfer_type": transfer_type,
        "estimated_processing_time": processing_time,
        "fees": 0 if transfer_type == "wallet" else 2.50,
        "message": f"{transfer_type.upper()} transfer initiated",
        "api_version": "v2",
        "tracking_url": f"/v2/transactions/{transaction_id}"
    })

@v2_bp.route('/wallet/qr-payment', methods=['POST'])
def qr_payment_v2():
    """
    V2: QR code payment functionality
    """
    data = request.get_json()
    
    required_fields = ['qr_code', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "Missing required fields for QR payment",
            "required": required_fields,
            "api_version": "v2"
        }), 400
    
    # Simulate QR payment
    transaction_id = f"QR_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return jsonify({
        "transaction_id": transaction_id,
        "status": "completed",
        "amount": data["amount"],
        "merchant": "Decoded from QR",
        "payment_method": "UPI",
        "message": "QR payment successful",
        "api_version": "v2"
    })

# V3 Endpoints - Full-featured PayTM wallet
@v3_bp.route('/wallet/balance', methods=['GET'])
def get_balance_v3():
    """
    V3: Complete balance overview with investments
    """
    user_id = request.args.get('user_id', 'USER123')
    
    return jsonify({
        "wallet": {
            "main_balance": 5678.50,
            "cashback_balance": 123.00,
            "total_balance": 5801.50,
            "currency": "INR",
            "last_updated": datetime.now().isoformat()
        },
        "upi": {
            "primary_id": f"{user_id.lower()}@paytm",
            "secondary_ids": [f"{user_id.lower()}@paytmbank"],
            "linked_accounts": [
                {"bank": "HDFC", "account_type": "Savings", "status": "Active"},
                {"bank": "SBI", "account_type": "Current", "status": "Active"},
                {"bank": "ICICI", "account_type": "Savings", "status": "Inactive"}
            ],
            "monthly_limit": {
                "used": 45000,
                "total": 100000,
                "remaining": 55000
            }
        },
        "investments": {
            "total_invested": 25000.00,
            "current_value": 26750.00,
            "profit_loss": 1750.00,
            "gold": 15000.00,
            "mutual_funds": 10000.00
        },
        "credit": {
            "available_limit": 50000.00,
            "used_limit": 12000.00,
            "due_amount": 3500.00,
            "due_date": "2024-01-25"
        },
        "user_id": user_id,
        "membership_tier": "Gold",
        "api_version": "v3"
    })

@v3_bp.route('/wallet/transfer', methods=['POST'])
def transfer_money_v3():
    """
    V3: Advanced transfer with smart routing
    """
    data = request.get_json()
    
    # V3 validation - comprehensive fields
    required_fields = ['to_identifier', 'amount']
    optional_fields = ['transfer_type', 'source_account', 'scheduling', 'split_payment']
    
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "Missing required fields",
            "required": required_fields,
            "optional": optional_fields,
            "api_version": "v3"
        }), 400
    
    # Smart routing logic
    amount = float(data['amount'])
    if amount <= 2000:
        recommended_method = "wallet"
        fees = 0
    elif amount <= 10000:
        recommended_method = "upi"
        fees = 0
    else:
        recommended_method = "imps"
        fees = amount * 0.005  # 0.5% fees
    
    # Check if scheduling is requested
    scheduled = data.get('scheduling')
    
    transaction_id = f"ADV_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    response = {
        "transaction_id": transaction_id,
        "status": "scheduled" if scheduled else "processing",
        "amount": amount,
        "to_identifier": data["to_identifier"],
        "recommended_method": recommended_method,
        "actual_method": data.get('transfer_type', recommended_method),
        "fees": fees,
        "cashback_earned": amount * 0.001,  # 0.1% cashback
        "api_version": "v3"
    }
    
    if scheduled:
        response.update({
            "scheduled_date": scheduled.get('date'),
            "scheduled_time": scheduled.get('time'),
            "recurring": scheduled.get('recurring', False)
        })
    
    # Split payment handling
    if 'split_payment' in data:
        response['split_details'] = data['split_payment']
        response['total_recipients'] = len(data['split_payment'])
    
    return jsonify(response)

@v3_bp.route('/wallet/investments', methods=['GET'])
def get_investments_v3():
    """
    V3: Investment portfolio overview
    """
    return jsonify({
        "portfolio": {
            "total_value": 26750.00,
            "total_invested": 25000.00,
            "returns": {
                "absolute": 1750.00,
                "percentage": 7.0
            }
        },
        "holdings": [
            {
                "type": "digital_gold",
                "quantity": "5.5g",
                "invested_amount": 15000.00,
                "current_value": 16500.00,
                "returns": 10.0
            },
            {
                "type": "mutual_fund",
                "fund_name": "PayTM Money Fund",
                "units": 1000,
                "invested_amount": 10000.00,
                "current_value": 10250.00,
                "returns": 2.5
            }
        ],
        "recommendations": [
            "Consider SIP in equity funds for long term",
            "Gold allocation looks optimal at current levels"
        ],
        "api_version": "v3"
    })

@v3_bp.route('/wallet/bills', methods=['POST'])
def pay_bills_v3():
    """
    V3: Bill payment functionality
    """
    data = request.get_json()
    
    required_fields = ['bill_type', 'provider', 'account_number', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "Missing required fields for bill payment",
            "required": required_fields,
            "supported_bills": ["electricity", "gas", "water", "mobile", "broadband", "dth"],
            "api_version": "v3"
        }), 400
    
    # Calculate cashback based on bill type
    amount = float(data['amount'])
    bill_type = data['bill_type']
    
    cashback_rates = {
        "electricity": 0.01,  # 1%
        "gas": 0.015,        # 1.5%
        "mobile": 0.02,      # 2%
        "broadband": 0.015,  # 1.5%
        "dth": 0.02         # 2%
    }
    
    cashback = amount * cashback_rates.get(bill_type, 0.005)
    
    transaction_id = f"BILL_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return jsonify({
        "transaction_id": transaction_id,
        "status": "completed",
        "bill_type": bill_type,
        "provider": data['provider'],
        "account_number": data['account_number'],
        "amount": amount,
        "cashback_earned": round(cashback, 2),
        "next_due_date": "2024-02-15",
        "auto_pay_enabled": False,
        "message": f"{bill_type.title()} bill paid successfully",
        "api_version": "v3"
    })

# Register all blueprints
app.register_blueprint(v1_bp)
app.register_blueprint(v2_bp)
app.register_blueprint(v3_bp)

# Version comparison endpoint
@app.route('/api/versions', methods=['GET'])
def compare_versions():
    """
    Compare all available API versions
    Helpful for clients to understand differences
    """
    return jsonify({
        "available_versions": ["v1", "v2", "v3"],
        "version_details": version_manager.version_info,
        "migration_paths": {
            "v1_to_v2": {
                "breaking_changes": [
                    "transfer endpoint requires transfer_type parameter",
                    "response format changed for balance endpoint"
                ],
                "new_features": [
                    "UPI transfer support",
                    "QR code payments",
                    "Enhanced balance information"
                ]
            },
            "v2_to_v3": {
                "breaking_changes": [],
                "new_features": [
                    "Investment portfolio management",
                    "Bill payment integration",
                    "Smart transfer routing",
                    "Scheduled payments",
                    "Split payment support"
                ]
            }
        },
        "recommendation": "Use v3 for new integrations, migrate from v1 before sunset date"
    })

# Health check for each version
@app.route('/<version>/health', methods=['GET'])
def health_check(version):
    """Health check for specific API version"""
    if version not in ['v1', 'v2', 'v3']:
        return jsonify({"error": "Invalid version"}), 404
    
    version_info = version_manager.get_version_info(version)
    is_deprecated = version_manager.is_version_deprecated(version)
    
    return jsonify({
        "version": version,
        "status": "healthy",
        "deprecated": is_deprecated,
        "sunset_date": version_info.get('sunset_date'),
        "features": version_info.get('features', []),
        "timestamp": datetime.now().isoformat()
    })

def demonstrate_url_versioning():
    """
    Demonstrate URL path-based API versioning
    """
    print("🔥 URL Path-based API Versioning - PayTM Style")
    print("=" * 60)
    
    print("\n📱 URL Structure Examples:")
    print("V1: /v1/wallet/balance - Basic functionality")
    print("V2: /v2/wallet/balance - UPI integrated")
    print("V3: /v3/wallet/balance - Full featured")
    
    print("\n🔄 Version Evolution:")
    for version, info in version_manager.version_info.items():
        status = "⚠️  DEPRECATED" if info['deprecated'] else "✅ ACTIVE"
        print(f"{version.upper()}: {info['description']} - {status}")
        if info['sunset_date']:
            print(f"    Sunset Date: {info['sunset_date']}")
        print(f"    Features: {', '.join(info['features'])}")
    
    print("\n💡 URL Versioning Benefits:")
    print("1. Clear version identification in URL")
    print("2. Easy to route different versions")
    print("3. Allows different authentication per version")
    print("4. Simple for API documentation")
    print("5. Easy to test different versions")
    
    print("\n⚠️  Considerations:")
    print("1. URLs change with versions")
    print("2. Need to maintain multiple codebases")
    print("3. Cache strategies need version awareness")
    print("4. Documentation becomes version-specific")
    
    print("\n🎯 Best Practices:")
    print("1. Use consistent version format (v1, v2, v3)")
    print("2. Keep deprecated versions functional during transition")
    print("3. Provide clear migration guides")
    print("4. Use semantic versioning principles")
    print("5. Monitor version usage analytics")

if __name__ == "__main__":
    # Run demonstration
    demonstrate_url_versioning()
    
    # Start Flask app for testing
    # app.run(debug=True, port=5002)
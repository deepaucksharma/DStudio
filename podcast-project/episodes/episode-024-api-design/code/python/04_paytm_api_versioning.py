#!/usr/bin/env python3
"""
Paytm API Versioning System - Wallet Evolution
API versioning strategies को demonstrate करने के लिए Paytm wallet के evolution का example

Versioning Strategies:
1. URI Versioning: /api/v1/, /api/v2/
2. Header Versioning: Accept: application/vnd.paytm.v2+json
3. Query Parameter: ?version=2.0
4. Content-Type Versioning

Paytm Evolution Timeline:
- v1.0 (2010): Basic wallet with add money
- v1.1 (2012): Bill payments added
- v2.0 (2014): Merchant payments + QR codes
- v2.1 (2016): Bank transfers (UPI integration)
- v3.0 (2018): Paytm Bank integration
- v3.1 (2020): Buy Now Pay Later
- v4.0 (2022): Investment features + Insurance

Author: Code Developer Agent for Hindi Tech Podcast  
Episode: 24 - API Design Patterns (API Versioning)
"""

from flask import Flask, request, jsonify, abort
from datetime import datetime, timedelta
import json
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Union
import logging
from functools import wraps

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Version Detection और routing के लिए decorators
def version_route(versions: List[str]):
    """
    API version routing decorator
    Multiple versioning strategies को support करता है
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            detected_version = detect_api_version(request)
            
            if detected_version not in versions:
                return jsonify({
                    "error": f"API version {detected_version} not supported",
                    "supported_versions": versions,
                    "message": "Please update your Paytm app या version header set करें"
                }), 400
                
            # Version को function में pass करना
            return func(detected_version, *args, **kwargs)
        return wrapper
    return decorator

def detect_api_version(request) -> str:
    """
    API version detection - Multiple strategies
    Priority order: Header > Query Param > URI > Default
    """
    
    # Strategy 1: Custom header (Preferred)
    if 'API-Version' in request.headers:
        return request.headers['API-Version']
    
    # Strategy 2: Accept header with vendor media type
    accept_header = request.headers.get('Accept', '')
    if 'application/vnd.paytm.v' in accept_header:
        # Extract version from Accept: application/vnd.paytm.v2+json
        import re
        match = re.search(r'application/vnd\.paytm\.v(\d+\.\d+|\d+)', accept_header)
        if match:
            return f"v{match.group(1)}"
    
    # Strategy 3: Query parameter
    if 'version' in request.args:
        version = request.args.get('version')
        return f"v{version}" if not version.startswith('v') else version
    
    # Strategy 4: URI path (extracted in route handlers)
    # This is handled in route definitions like /api/v2/wallet
    
    # Default to latest stable version
    return "v4.0"

# Data structures for different API versions

@dataclass
class WalletV1:
    """Paytm Wallet v1.0 (2010) - Basic wallet functionality"""
    user_id: str
    balance: float
    currency: str = "INR"
    status: str = "ACTIVE"

@dataclass 
class WalletV2:
    """Paytm Wallet v2.0 (2014) - Added merchant features"""
    user_id: str
    balance: float
    merchant_balance: float  # Separate merchant wallet
    currency: str = "INR"
    status: str = "ACTIVE"
    kyc_status: str = "PENDING"  # KYC compliance added

@dataclass
class WalletV3:
    """Paytm Wallet v3.0 (2018) - Bank integration"""
    user_id: str
    balance: float
    merchant_balance: float
    bank_balance: float      # Paytm Payments Bank
    currency: str = "INR" 
    status: str = "ACTIVE"
    kyc_status: str = "PENDING"
    bank_account_number: str = ""
    ifsc_code: str = "PYTM0123456"

@dataclass
class WalletV4:
    """Paytm Wallet v4.0 (2022) - Investment features"""
    user_id: str
    balance: float
    merchant_balance: float
    bank_balance: float
    investment_balance: float  # Stocks, Mutual Funds
    loan_balance: float        # Buy Now Pay Later
    currency: str = "INR"
    status: str = "ACTIVE"
    kyc_status: str = "COMPLETED"
    bank_account_number: str = ""
    ifsc_code: str = "PYTM0123456"
    credit_score: int = 750
    investment_portfolio: Dict = None

# Sample user data for different versions
USERS_DB = {
    "user_12345": {
        "name": "Rahul Sharma",
        "mobile": "+91-9876543210", 
        "email": "rahul@gmail.com",
        "registration_date": "2010-03-15",
        "v1_wallet": WalletV1("user_12345", 5000.50),
        "v2_wallet": WalletV2("user_12345", 5000.50, 12000.30, "INR", "ACTIVE", "COMPLETED"),
        "v3_wallet": WalletV3("user_12345", 5000.50, 12000.30, 25000.75, "INR", "ACTIVE", "COMPLETED", "98765432101234", "PYTM0123456"),
        "v4_wallet": WalletV4("user_12345", 5000.50, 12000.30, 25000.75, 15000.00, -2500.00, "INR", "ACTIVE", "COMPLETED", "98765432101234", "PYTM0123456", 750, {"stocks": 10000, "mutual_funds": 5000})
    }
}

# API Routes with version support

# VERSION 1.0 - Basic Wallet Operations (Legacy support)
@app.route('/api/v1/wallet/<user_id>', methods=['GET'])
def get_wallet_v1(user_id):
    """
    Paytm Wallet v1.0 - Basic balance check
    2010 के time पे सिर्फ इतना ही था - add money और check balance
    """
    logger.info(f"Wallet v1.0 request for user: {user_id}")
    
    if user_id not in USERS_DB:
        return jsonify({"error": "User not found! Paytm account banao pehle"}), 404
    
    user = USERS_DB[user_id]
    wallet = user["v1_wallet"]
    
    return jsonify({
        "version": "1.0",
        "user_id": wallet.user_id,
        "balance": wallet.balance,
        "currency": wallet.currency,
        "status": wallet.status,
        "message": f"Aapka Paytm wallet balance: ₹{wallet.balance}",
        "features_available": [
            "Add money from bank",
            "Check balance",
            "Basic mobile recharge"
        ]
    })

# VERSION 2.0 - Merchant Payments Added
@app.route('/api/v2/wallet/<user_id>', methods=['GET'])
@version_route(['v2.0', 'v2.1'])
def get_wallet_v2(version, user_id):
    """
    Paytm Wallet v2.0/v2.1 - Merchant payments और QR codes
    2014-2016: Digital India movement के साथ merchant adoption
    """
    logger.info(f"Wallet {version} request for user: {user_id}")
    
    if user_id not in USERS_DB:
        return jsonify({"error": "User not found! Paytm download karo aur signup karo"}), 404
    
    user = USERS_DB[user_id]
    wallet = user["v2_wallet"]
    
    response = {
        "version": version,
        "user_id": wallet.user_id,
        "personal_balance": wallet.balance,
        "merchant_balance": wallet.merchant_balance,
        "total_balance": wallet.balance + wallet.merchant_balance,
        "currency": wallet.currency,
        "status": wallet.status,
        "kyc_status": wallet.kyc_status,
        "message": f"Total Paytm balance: ₹{wallet.balance + wallet.merchant_balance}",
        "features_available": [
            "Mobile & DTH recharge",
            "Bill payments (Electricity, Gas)",
            "Merchant QR payments", 
            "Movie ticket booking",
            "Travel booking"
        ]
    }
    
    # v2.1 specific features (UPI integration)
    if version == "v2.1":
        response["upi_enabled"] = True
        response["bank_transfer_enabled"] = True
        response["features_available"].extend([
            "Bank to bank transfer",
            "UPI payments",
            "Request money from friends"
        ])
    
    return jsonify(response)

# VERSION 3.0 - Paytm Payments Bank
@app.route('/api/v3/wallet/<user_id>', methods=['GET']) 
@version_route(['v3.0', 'v3.1'])
def get_wallet_v3(version, user_id):
    """
    Paytm Wallet v3.0/v3.1 - Payments Bank integration
    2018-2020: Banking license मिला, BNPL शुरू हुआ
    """
    logger.info(f"Wallet {version} request for user: {user_id}")
    
    if user_id not in USERS_DB:
        return jsonify({"error": "User not found! Paytm Payments Bank account खुलवाइये"}), 404
    
    user = USERS_DB[user_id]
    wallet = user["v3_wallet"]
    
    response = {
        "version": version,
        "user_id": wallet.user_id,
        "wallet_balance": wallet.balance,
        "merchant_balance": wallet.merchant_balance,
        "bank_balance": wallet.bank_balance,
        "total_balance": wallet.balance + wallet.merchant_balance + wallet.bank_balance,
        "currency": wallet.currency,
        "status": wallet.status,
        "kyc_status": wallet.kyc_status,
        "bank_details": {
            "account_number": wallet.bank_account_number,
            "ifsc_code": wallet.ifsc_code,
            "bank_name": "Paytm Payments Bank"
        },
        "message": f"Paytm Bank + Wallet combined balance: ₹{wallet.balance + wallet.bank_balance}",
        "features_available": [
            "Savings bank account",
            "Debit card",
            "UPI with Paytm Bank",
            "Fixed deposits",
            "Insurance products",
            "Gold investment"
        ]
    }
    
    # v3.1 specific features (BNPL)
    if version == "v3.1":
        response["bnpl_enabled"] = True
        response["credit_limit"] = 50000
        response["features_available"].extend([
            "Buy Now Pay Later",
            "Paytm Postpaid",
            "Personal loans"
        ])
    
    return jsonify(response)

# VERSION 4.0 - Investment Platform
@app.route('/api/v4/wallet/<user_id>', methods=['GET'])
@version_route(['v4.0'])  
def get_wallet_v4(version, user_id):
    """
    Paytm Wallet v4.0 - Complete financial ecosystem
    2022+: Super app बना - payments, banking, investments, loans, insurance
    """
    logger.info(f"Wallet {version} request for user: {user_id}")
    
    if user_id not in USERS_DB:
        return jsonify({"error": "User not found! Paytm super app install करिये"}), 404
    
    user = USERS_DB[user_id]
    wallet = user["v4_wallet"]
    
    return jsonify({
        "version": version,
        "user_id": wallet.user_id,
        "balances": {
            "wallet": wallet.balance,
            "merchant": wallet.merchant_balance,
            "bank": wallet.bank_balance,
            "investments": wallet.investment_balance,
            "loan_outstanding": abs(wallet.loan_balance) if wallet.loan_balance < 0 else 0
        },
        "total_net_worth": wallet.balance + wallet.merchant_balance + wallet.bank_balance + wallet.investment_balance + wallet.loan_balance,
        "currency": wallet.currency,
        "status": wallet.status,
        "kyc_status": wallet.kyc_status,
        "bank_details": {
            "account_number": wallet.bank_account_number,
            "ifsc_code": wallet.ifsc_code,
            "bank_name": "Paytm Payments Bank"
        },
        "credit_profile": {
            "credit_score": wallet.credit_score,
            "bnpl_limit": 100000,
            "loan_eligibility": "₹5,00,000"
        },
        "investment_portfolio": wallet.investment_portfolio,
        "message": f"Complete financial portfolio worth: ₹{wallet.balance + wallet.bank_balance + wallet.investment_balance}",
        "features_available": [
            "Unified payments interface",
            "Banking services",
            "Stock trading",
            "Mutual fund investments", 
            "Personal & business loans",
            "Insurance (Life, Health, Vehicle)",
            "Gold & Silver investment",
            "Travel & entertainment booking",
            "E-commerce marketplace",
            "Crypto trading (limited)"
        ],
        "super_app_services": {
            "payments": "✅ Active",
            "banking": "✅ Active", 
            "investments": "✅ Active",
            "loans": "✅ Active",
            "insurance": "✅ Active",
            "travel": "✅ Active",
            "shopping": "✅ Active",
            "entertainment": "✅ Active"
        }
    })

# Generic version-agnostic endpoint with intelligent version detection
@app.route('/api/wallet/<user_id>', methods=['GET'])
def get_wallet_intelligent(user_id):
    """
    Intelligent version detection और backward compatibility
    Client का version detect करके appropriate response दे देते हैं
    """
    detected_version = detect_api_version(request)
    logger.info(f"Intelligent routing: Detected version {detected_version} for user {user_id}")
    
    # Route to appropriate version handler
    version_handlers = {
        "v1.0": lambda: get_wallet_v1(user_id),
        "v2.0": lambda: get_wallet_v2("v2.0", user_id),
        "v2.1": lambda: get_wallet_v2("v2.1", user_id), 
        "v3.0": lambda: get_wallet_v3("v3.0", user_id),
        "v3.1": lambda: get_wallet_v3("v3.1", user_id),
        "v4.0": lambda: get_wallet_v4("v4.0", user_id)
    }
    
    if detected_version in version_handlers:
        return version_handlers[detected_version]()
    else:
        return jsonify({
            "error": f"Unsupported API version: {detected_version}",
            "supported_versions": list(version_handlers.keys()),
            "message": "Please update your Paytm app या supported version use करें"
        }), 400

# Add Money endpoint with version differences
@app.route('/api/<version>/wallet/<user_id>/add-money', methods=['POST'])
def add_money_versioned(version, user_id):
    """
    Add money functionality - Different versions में different features
    Version के according different payment methods available
    """
    
    if version not in ['v1', 'v2', 'v3', 'v4']:
        return jsonify({"error": f"Version {version} not supported"}), 400
    
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        payment_method = data.get('payment_method', 'debit_card')
        
        if amount <= 0:
            return jsonify({"error": "Amount should be greater than 0"}), 400
        
        if amount > 100000:  # PPI guidelines
            return jsonify({"error": "Maximum ₹1,00,000 per transaction allowed"}), 400
            
        if user_id not in USERS_DB:
            return jsonify({"error": "User not found"}), 404
        
        user = USERS_DB[user_id]
        
        # Version-specific payment methods
        allowed_methods = {
            'v1': ['debit_card', 'credit_card', 'net_banking'],
            'v2': ['debit_card', 'credit_card', 'net_banking', 'upi'],
            'v3': ['debit_card', 'credit_card', 'net_banking', 'upi', 'bank_transfer'],
            'v4': ['debit_card', 'credit_card', 'net_banking', 'upi', 'bank_transfer', 'crypto', 'bnpl']
        }
        
        if payment_method not in allowed_methods[version]:
            return jsonify({
                "error": f"Payment method {payment_method} not available in {version}",
                "available_methods": allowed_methods[version]
            }), 400
        
        # Process add money based on version
        wallet_key = f"{version}_wallet"
        if version == 'v1':
            user[wallet_key].balance += amount
        elif version in ['v2', 'v3', 'v4']:
            # Later versions have separate balances
            user[wallet_key].balance += amount
            
        # Generate transaction ID
        txn_id = f"TXN{uuid.uuid4().hex[:8].upper()}"
        
        return jsonify({
            "success": True,
            "transaction_id": txn_id,
            "amount_added": amount,
            "payment_method": payment_method,
            "new_balance": getattr(user[wallet_key], 'balance', 0),
            "message": f"₹{amount} successfully added to your Paytm wallet!",
            "version_features": {
                "v1": "Basic wallet top-up",
                "v2": "UPI enabled top-up", 
                "v3": "Bank account integration",
                "v4": "Multi-source funding including crypto"
            }.get(version, "Unknown version")
        })
        
    except Exception as e:
        logger.error(f"Add money error: {str(e)}")
        return jsonify({"error": "Transaction failed! Please try again"}), 500

# API deprecation warning endpoint
@app.route('/api/v1/deprecation-notice', methods=['GET'])
def deprecation_notice():
    """
    API deprecation notice - Old versions को sunset करने से पहले warning
    """
    return jsonify({
        "notice": "Paytm API v1.0 Deprecation Warning",
        "message": "यह API version जल्दी बंद हो जाएगा! Please migrate to v4.0",
        "deprecation_timeline": {
            "warning_period": "6 months",
            "support_ends": "2025-08-01", 
            "complete_shutdown": "2025-12-01"
        },
        "migration_benefits": [
            "Investment features access",
            "Better security",
            "More payment options",
            "Super app functionality",
            "Higher transaction limits"
        ],
        "migration_guide": "/api/migration-guide",
        "support_contact": "developers@paytm.com"
    })

# Health check endpoint with version info
@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check with version information"""
    return jsonify({
        "status": "healthy",
        "service": "Paytm API Versioning Demo",
        "supported_versions": ["v1.0", "v2.0", "v2.1", "v3.0", "v3.1", "v4.0"],
        "default_version": "v4.0",
        "version_detection_methods": [
            "API-Version header (Recommended)",
            "Accept header with vendor media type",
            "Query parameter (?version=4.0)",
            "URI versioning (/api/v4/)"
        ],
        "message": "Paytm API - 2010 से 2025 तक का evolution! Sab versions supported 📱"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "available_versions": ["v1", "v2", "v3", "v4"],
        "example_urls": [
            "/api/v4/wallet/user_12345",
            "/api/wallet/user_12345 (with API-Version header)",
            "/api/wallet/user_12345?version=4.0"
        ],
        "message": "Check URL and API version! Paytm app update kar liye kya?"
    }), 404

if __name__ == '__main__':
    print("💳 Paytm API Versioning Server starting...")
    print("📅 Supporting 12+ years of API evolution (2010-2025)")
    print("🔄 Multiple versioning strategies demonstrated")
    print("\nTesting URLs:")
    print("Legacy:    GET /api/v1/wallet/user_12345")
    print("Current:   GET /api/v4/wallet/user_12345") 
    print("Smart:     GET /api/wallet/user_12345 (with headers)")
    print("Add Money: POST /api/v4/wallet/user_12345/add-money")
    print("Health:    GET /api/health")
    
    app.run(host='0.0.0.0', port=6000, debug=True)
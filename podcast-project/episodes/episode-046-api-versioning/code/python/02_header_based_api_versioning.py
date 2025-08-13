#!/usr/bin/env python3
"""
Header-based API Versioning System
Inspired by Flipkart's API evolution - version in headers instead of URL

Example: Flipkart ne kaise header-based versioning use kiya for seller APIs
"""

from flask import Flask, request, jsonify, make_response
from functools import wraps
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import json
from datetime import datetime
import logging

# Configure logging for Indian context
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class APIVersionConfig:
    """API version configuration"""
    version: str
    deprecated: bool = False
    sunset_date: Optional[str] = None
    description: str = ""

class HeaderVersionManager:
    """
    Header-based API versioning manager
    Example: Flipkart seller API versioning strategy
    """
    
    def __init__(self):
        self.supported_versions = {
            "1.0": APIVersionConfig(
                version="1.0",
                description="Initial Flipkart seller API - Basic product listing"
            ),
            "1.1": APIVersionConfig(
                version="1.1",
                description="Added bulk upload support - Bulk product add करने के लिए"
            ),
            "2.0": APIVersionConfig(
                version="2.0",
                description="New authentication system - OAuth 2.0 ke saath"
            ),
            "2.1": APIVersionConfig(
                version="2.1",
                description="Added analytics endpoints - Sales analytics ke liye"
            )
        }
        
        # Deprecate old version
        self.supported_versions["1.0"].deprecated = True
        self.supported_versions["1.0"].sunset_date = "2024-12-31"
    
    def get_version_from_header(self, headers: Dict[str, str]) -> str:
        """
        Extract API version from headers
        Priority order:
        1. API-Version header
        2. Accept header with version
        3. Default to latest
        """
        # Method 1: Direct API-Version header
        if 'API-Version' in headers:
            return headers['API-Version']
        
        # Method 2: Accept header with version
        accept_header = headers.get('Accept', '')
        if 'application/vnd.flipkart.v' in accept_header:
            # Extract version from: application/vnd.flipkart.v2.1+json
            import re
            match = re.search(r'application/vnd\.flipkart\.v(\d+\.\d+)', accept_header)
            if match:
                return match.group(1)
        
        # Method 3: Custom header used by some Indian companies
        if 'X-API-Version' in headers:
            return headers['X-API-Version']
        
        # Default to latest stable version
        return "2.1"
    
    def is_version_supported(self, version: str) -> bool:
        """Check if version is supported"""
        return version in self.supported_versions
    
    def is_version_deprecated(self, version: str) -> bool:
        """Check if version is deprecated"""
        if version not in self.supported_versions:
            return True
        return self.supported_versions[version].deprecated
    
    def get_version_info(self, version: str) -> Optional[APIVersionConfig]:
        """Get version configuration"""
        return self.supported_versions.get(version)

# Initialize Flask app for demonstration
app = Flask(__name__)
version_manager = HeaderVersionManager()

def version_handler(func: Callable) -> Callable:
    """
    Decorator to handle API versioning based on headers
    यह decorator automatically version detect करता है
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get version from headers
        version = version_manager.get_version_from_header(dict(request.headers))
        
        # Check if version is supported
        if not version_manager.is_version_supported(version):
            return jsonify({
                "error": "Unsupported API version",
                "message": f"Version {version} is not supported",
                "supported_versions": list(version_manager.supported_versions.keys()),
                "hindi_message": f"Version {version} support nahi hai"
            }), 400
        
        # Check if version is deprecated
        if version_manager.is_version_deprecated(version):
            version_info = version_manager.get_version_info(version)
            logger.warning(f"Deprecated API version {version} used")
        
        # Add version info to request context
        request.api_version = version
        request.version_info = version_manager.get_version_info(version)
        
        # Call the actual function
        response = func(*args, **kwargs)
        
        # Add version info to response headers
        if hasattr(response, 'headers'):
            response.headers['API-Version'] = version
            response.headers['API-Supported-Versions'] = ','.join(version_manager.supported_versions.keys())
            
            # Add deprecation warning if needed
            if version_manager.is_version_deprecated(version):
                version_info = version_manager.get_version_info(version)
                response.headers['Deprecation'] = 'true'
                if version_info.sunset_date:
                    response.headers['Sunset'] = version_info.sunset_date
                response.headers['Warning'] = f'299 - "Version {version} is deprecated"'
        
        return response
    
    return wrapper

# Example API endpoints with version-specific behavior

@app.route('/api/products', methods=['GET'])
@version_handler
def get_products():
    """
    Get products with version-specific response format
    Different versions return different data structures
    """
    version = request.api_version
    
    # Sample product data - Flipkart style
    base_products = [
        {
            "id": "PROD001",
            "name": "Samsung Galaxy M31",
            "price": 15999,
            "category": "Electronics",
            "seller_id": "SELLER123"
        },
        {
            "id": "PROD002", 
            "name": "Boat Airdopes 131",
            "price": 1299,
            "category": "Electronics",
            "seller_id": "SELLER456"
        }
    ]
    
    # Version-specific response formatting
    if version == "1.0":
        # V1.0: Simple format
        return jsonify({
            "products": base_products,
            "message": "Products fetched successfully",
            "version_note": "Using API v1.0 - Basic format"
        })
    
    elif version == "1.1":
        # V1.1: Added metadata
        return jsonify({
            "products": base_products,
            "metadata": {
                "total_count": len(base_products),
                "page": 1,
                "per_page": 10
            },
            "message": "Products with metadata fetched",
            "version_note": "Using API v1.1 - With bulk upload support"
        })
    
    elif version == "2.0":
        # V2.0: Enhanced format with seller info
        enhanced_products = []
        for product in base_products:
            enhanced_product = product.copy()
            enhanced_product["seller_info"] = {
                "name": f"Seller {product['seller_id'][-3:]}",
                "rating": 4.2,
                "location": "Mumbai"
            }
            enhanced_products.append(enhanced_product)
        
        return jsonify({
            "data": {
                "products": enhanced_products,
                "pagination": {
                    "current_page": 1,
                    "total_pages": 1,
                    "total_items": len(enhanced_products),
                    "items_per_page": 10
                }
            },
            "meta": {
                "api_version": version,
                "response_time": "45ms",
                "server": "flipkart-api-mumbai"
            },
            "version_note": "Using API v2.0 - OAuth 2.0 authentication"
        })
    
    else:  # version == "2.1" (latest)
        # V2.1: Full format with analytics
        enhanced_products = []
        for product in base_products:
            enhanced_product = product.copy()
            enhanced_product["seller_info"] = {
                "name": f"Seller {product['seller_id'][-3:]}",
                "rating": 4.2,
                "location": "Mumbai",
                "verified": True
            }
            enhanced_product["analytics"] = {
                "views_last_30_days": 1250,
                "orders_last_30_days": 45,
                "conversion_rate": 3.6
            }
            enhanced_products.append(enhanced_product)
        
        return jsonify({
            "data": {
                "products": enhanced_products,
                "pagination": {
                    "current_page": 1,
                    "total_pages": 1,
                    "total_items": len(enhanced_products),
                    "items_per_page": 10,
                    "has_next": False,
                    "has_previous": False
                },
                "filters_applied": []
            },
            "meta": {
                "api_version": version,
                "response_time": "38ms",
                "server": "flipkart-api-mumbai-v2",
                "cache_status": "miss"
            },
            "version_note": "Using API v2.1 - With analytics support"
        })

@app.route('/api/products', methods=['POST'])
@version_handler
def create_product():
    """
    Create product with version-specific validation
    Different versions have different required fields
    """
    version = request.api_version
    data = request.get_json()
    
    # Version-specific validation
    if version == "1.0":
        required_fields = ["name", "price", "category"]
    elif version == "1.1":
        required_fields = ["name", "price", "category", "description"]
    else:  # v2.0+
        required_fields = ["name", "price", "category", "description", "brand", "seller_id"]
    
    # Validate required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields,
            "version": version,
            "hindi_message": f"Required fields missing: {', '.join(missing_fields)}"
        }), 400
    
    # Create product (mock implementation)
    product_id = f"PROD{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    response_data = {
        "product_id": product_id,
        "message": "Product created successfully",
        "hindi_message": "Product successfully create ho gaya"
    }
    
    # Version-specific response
    if version >= "2.0":
        response_data["seller_dashboard_url"] = f"/seller/products/{product_id}"
        response_data["estimated_go_live"] = "2-4 hours"
    
    return jsonify(response_data), 201

@app.route('/api/version-info', methods=['GET'])
@version_handler
def get_version_info():
    """
    Get API version information
    Useful for clients to understand current API status
    """
    version = request.api_version
    version_info = request.version_info
    
    return jsonify({
        "current_version": version,
        "description": version_info.description,
        "deprecated": version_info.deprecated,
        "sunset_date": version_info.sunset_date,
        "all_supported_versions": {
            v: {
                "description": config.description,
                "deprecated": config.deprecated,
                "sunset_date": config.sunset_date
            }
            for v, config in version_manager.supported_versions.items()
        },
        "migration_guide": {
            "from_1.0_to_2.0": "https://docs.flipkart.com/api/migration/v1-to-v2",
            "breaking_changes": "Authentication system changed to OAuth 2.0"
        }
    })

def demonstrate_header_versioning():
    """
    Demonstrate header-based API versioning with various scenarios
    """
    print("🔥 Header-based API Versioning - Flipkart Style")
    print("=" * 60)
    
    import requests
    from unittest.mock import Mock
    
    # Mock request examples
    print("\n📱 Client Request Examples:")
    
    # Example 1: Using API-Version header
    print("\n1. Using API-Version header:")
    print("Headers: {'API-Version': '2.1'}")
    print("Response: Latest format with analytics")
    
    # Example 2: Using Accept header
    print("\n2. Using Accept header:")
    print("Headers: {'Accept': 'application/vnd.flipkart.v2.0+json'}")
    print("Response: Enhanced format with seller info")
    
    # Example 3: Using deprecated version
    print("\n3. Using deprecated version:")
    print("Headers: {'API-Version': '1.0'}")
    print("Response: Simple format + Deprecation warning")
    
    print("\n⚠️  Deprecation Handling:")
    print("- Deprecated versions get Warning header")
    print("- Sunset date is communicated")
    print("- Migration guide is provided")
    
    print("\n🎯 Header-based Versioning Benefits:")
    print("1. Clean URLs - No version in path")
    print("2. Easy to change version per request")
    print("3. Supports multiple version formats")
    print("4. Better for API gateways")
    print("5. Follows HTTP standards")
    
    print("\n🔧 Implementation Tips:")
    print("1. Always set default version")
    print("2. Validate version in middleware")
    print("3. Add version info to response headers")
    print("4. Log version usage for analytics")
    print("5. Provide clear error messages")

if __name__ == "__main__":
    # Run demonstration
    demonstrate_header_versioning()
    
    # Start Flask app for testing
    # app.run(debug=True, port=5001)
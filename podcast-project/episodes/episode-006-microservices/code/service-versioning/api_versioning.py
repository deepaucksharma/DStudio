#!/usr/bin/env python3
"""
API Versioning and Backward Compatibility for Mumbai-scale Services
Multiple versioning strategies with seamless upgrades

जैसे Mumbai local train routes में नए stations add करते हैं पुराने को disturb किये बिना,
वैसे ही API versioning में backward compatibility maintain करते हैं
"""

from flask import Flask, request, jsonify
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("APIVersioning")

class VersioningStrategy(Enum):
    URL_PATH = "url_path"           # /v1/api/products
    QUERY_PARAM = "query_param"     # /api/products?version=1
    HEADER = "header"               # X-API-Version: 1
    ACCEPT_HEADER = "accept_header" # Accept: application/vnd.api+json;version=1
    SUBDOMAIN = "subdomain"         # v1.api.domain.com

@dataclass
class Product:
    """Product model with versioned fields"""
    id: str
    name: str
    price: float
    # v1 fields
    category: str = ""
    # v2 fields  
    description: str = ""
    brand: str = ""
    # v3 fields
    ratings: Dict[str, Any] = None
    inventory: Dict[str, Any] = None
    
    def to_v1_format(self) -> Dict[str, Any]:
        """Convert to v1 API format"""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category
        }
    
    def to_v2_format(self) -> Dict[str, Any]:
        """Convert to v2 API format"""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "description": self.description,
            "brand": self.brand
        }
    
    def to_v3_format(self) -> Dict[str, Any]:
        """Convert to v3 API format"""
        return {
            "product_id": self.id,  # Field renamed in v3
            "product_name": self.name,
            "price_inr": self.price,
            "category": self.category,
            "description": self.description,
            "brand": self.brand,
            "ratings": self.ratings or {
                "average": 4.5,
                "count": 150,
                "distribution": {"5": 75, "4": 50, "3": 20, "2": 3, "1": 2}
            },
            "inventory": self.inventory or {
                "available": True,
                "quantity": 100,
                "warehouse": "mumbai-central"
            }
        }

class APIVersionManager:
    """Manages API versions and routing"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.version_handlers = {
            "1": self.handle_v1,
            "2": self.handle_v2,
            "3": self.handle_v3
        }
        self.default_version = "3"
        
        # Sample data
        self.products = [
            Product("1", "OnePlus 12", 65999.0, "smartphones", "Flagship Android phone", "OnePlus"),
            Product("2", "MacBook Air M2", 119900.0, "laptops", "Apple's lightweight laptop", "Apple"),
            Product("3", "Samsung TV 55\"", 42999.0, "electronics", "4K Smart TV", "Samsung")
        ]
    
    def get_api_version(self, request_obj) -> str:
        """Extract API version from request using multiple strategies"""
        
        # Strategy 1: URL Path versioning (e.g., /v2/products)
        if request_obj.path.startswith('/v'):
            path_parts = request_obj.path.split('/')
            if len(path_parts) > 1 and path_parts[1].startswith('v'):
                version = path_parts[1][1:]  # Remove 'v' prefix
                if version in self.version_handlers:
                    return version
        
        # Strategy 2: Query parameter (e.g., ?version=2)
        version = request_obj.args.get('version')
        if version and version in self.version_handlers:
            return version
        
        # Strategy 3: Custom header (e.g., X-API-Version: 2)
        version = request_obj.headers.get('X-API-Version')
        if version and version in self.version_handlers:
            return version
        
        # Strategy 4: Accept header versioning
        accept_header = request_obj.headers.get('Accept', '')
        if 'version=' in accept_header:
            try:
                version = accept_header.split('version=')[1].split(';')[0].split(',')[0]
                if version in self.version_handlers:
                    return version
            except:
                pass
        
        # Default to latest version
        return self.default_version
    
    def handle_v1(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Handle v1 API requests - Original Mumbai local style"""
        logger.info(f"Handling v1 request for {endpoint}")
        
        if endpoint == "products":
            return {
                "products": [p.to_v1_format() for p in self.products],
                "version": "1.0",
                "message": "Mumbai market products - basic info only"
            }
        elif endpoint == "product":
            product_id = kwargs.get('product_id')
            product = next((p for p in self.products if p.id == product_id), None)
            if product:
                return {
                    "product": product.to_v1_format(),
                    "version": "1.0"
                }
            return {"error": "Product not found", "version": "1.0"}
        
        return {"error": "Endpoint not available in v1", "version": "1.0"}
    
    def handle_v2(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Handle v2 API requests - Enhanced Mumbai market"""
        logger.info(f"Handling v2 request for {endpoint}")
        
        if endpoint == "products":
            return {
                "products": [p.to_v2_format() for p in self.products],
                "version": "2.0",
                "message": "Mumbai market products - with descriptions and brands",
                "meta": {
                    "total": len(self.products),
                    "page": 1,
                    "per_page": 10
                }
            }
        elif endpoint == "product":
            product_id = kwargs.get('product_id')
            product = next((p for p in self.products if p.id == product_id), None)
            if product:
                return {
                    "product": product.to_v2_format(),
                    "version": "2.0",
                    "meta": {
                        "last_updated": "2024-01-15T10:30:00Z"
                    }
                }
            return {"error": "Product not found", "version": "2.0"}
        
        return {"error": "Endpoint not available in v2", "version": "2.0"}
    
    def handle_v3(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Handle v3 API requests - Modern Mumbai digital marketplace"""
        logger.info(f"Handling v3 request for {endpoint}")
        
        if endpoint == "products":
            return {
                "data": [p.to_v3_format() for p in self.products],
                "version": "3.0",
                "message": "Mumbai digital marketplace - complete product information",
                "meta": {
                    "total_count": len(self.products),
                    "page": 1,
                    "per_page": 10,
                    "has_next": False,
                    "currency": "INR",
                    "region": "mumbai"
                },
                "links": {
                    "self": "/v3/products",
                    "next": None,
                    "prev": None
                }
            }
        elif endpoint == "product":
            product_id = kwargs.get('product_id')
            product = next((p for p in self.products if p.id == product_id), None)
            if product:
                return {
                    "data": product.to_v3_format(),
                    "version": "3.0",
                    "meta": {
                        "last_updated": "2024-01-15T10:30:00Z",
                        "cache_ttl": 300,
                        "region": "mumbai"
                    },
                    "links": {
                        "self": f"/v3/products/{product_id}",
                        "reviews": f"/v3/products/{product_id}/reviews",
                        "recommendations": f"/v3/products/{product_id}/related"
                    }
                }
            return {
                "error": {
                    "code": "PRODUCT_NOT_FOUND",
                    "message": "Product not found in Mumbai inventory",
                    "details": f"Product ID {product_id} does not exist"
                },
                "version": "3.0"
            }
        
        return {
            "error": {
                "code": "ENDPOINT_NOT_FOUND",
                "message": "Endpoint not available",
                "available_endpoints": ["/v3/products", "/v3/products/{id}"]
            },
            "version": "3.0"
        }

# Create Flask app with versioning support
app = Flask(__name__)
version_manager = APIVersionManager(app)

@app.before_request
def log_request():
    """Log all requests with version info"""
    version = version_manager.get_api_version(request)
    logger.info(f"Request: {request.method} {request.path} - API Version: {version}")

# URL Path versioning routes
@app.route('/v1/products')
def get_products_v1():
    """V1 Products endpoint - URL path versioning"""
    return jsonify(version_manager.handle_v1("products"))

@app.route('/v2/products')
def get_products_v2():
    """V2 Products endpoint - URL path versioning"""
    return jsonify(version_manager.handle_v2("products"))

@app.route('/v3/products')
def get_products_v3():
    """V3 Products endpoint - URL path versioning"""
    return jsonify(version_manager.handle_v3("products"))

# Generic versioned endpoints
@app.route('/products')
def get_products():
    """Generic products endpoint with version detection"""
    version = version_manager.get_api_version(request)
    handler = version_manager.version_handlers[version]
    return jsonify(handler("products"))

@app.route('/products/<product_id>')
def get_product(product_id):
    """Generic product endpoint with version detection"""
    version = version_manager.get_api_version(request)
    handler = version_manager.version_handlers[version]
    return jsonify(handler("product", product_id=product_id))

@app.route('/v1/products/<product_id>')
def get_product_v1(product_id):
    """V1 Product detail endpoint"""
    return jsonify(version_manager.handle_v1("product", product_id=product_id))

@app.route('/v2/products/<product_id>')
def get_product_v2(product_id):
    """V2 Product detail endpoint"""
    return jsonify(version_manager.handle_v2("product", product_id=product_id))

@app.route('/v3/products/<product_id>')
def get_product_v3(product_id):
    """V3 Product detail endpoint"""
    return jsonify(version_manager.handle_v3("product", product_id=product_id))

# Version discovery endpoint
@app.route('/versions')
def get_api_versions():
    """Get available API versions"""
    return jsonify({
        "supported_versions": list(version_manager.version_handlers.keys()),
        "default_version": version_manager.default_version,
        "latest_version": "3",
        "versioning_strategies": [
            "URL Path: /v{version}/endpoint",
            "Query Parameter: /endpoint?version={version}", 
            "Header: X-API-Version: {version}",
            "Accept Header: Accept: application/json;version={version}"
        ],
        "deprecation_schedule": {
            "v1": "Deprecated - will be removed in 6 months",
            "v2": "Supported - maintenance mode",
            "v3": "Current - actively developed"
        },
        "migration_guide": "/docs/migration",
        "message": "Mumbai API versioning - smooth transitions like local train upgrades!"
    })

# Health check with version info
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "mumbai-product-api",
        "supported_versions": list(version_manager.version_handlers.keys()),
        "default_version": version_manager.default_version,
        "message": "API service running like Mumbai Dabbawalas - reliable and on time!"
    })

# Middleware for backward compatibility
@app.after_request
def add_version_headers(response):
    """Add version information to all responses"""
    version = version_manager.get_api_version(request)
    
    # Add standard versioning headers
    response.headers['X-API-Version'] = version
    response.headers['X-Supported-Versions'] = ','.join(version_manager.version_handlers.keys())
    response.headers['X-Default-Version'] = version_manager.default_version
    
    # Add deprecation warnings for older versions
    if version == "1":
        response.headers['Sunset'] = 'Sat, 01 Jul 2024 00:00:00 GMT'  # RFC 8594
        response.headers['Deprecation'] = 'true'
        response.headers['Link'] = '</v3/products>; rel="successor-version"'
    
    return response

def demo_api_versioning():
    """Demonstrate API versioning strategies"""
    print("\n=== Mumbai API Versioning Demo ===")
    print("Multiple versioning strategies with backward compatibility!")
    
    print("\n--- Available Versioning Strategies ---")
    print("1. URL Path: /v1/products, /v2/products, /v3/products")
    print("2. Query Parameter: /products?version=1")
    print("3. Header: X-API-Version: 2")
    print("4. Accept Header: Accept: application/json;version=3")
    
    print("\n--- Version Evolution ---")
    print("V1 (Legacy): Basic product info - like old Mumbai market stalls")
    print("   - id, name, price, category")
    print("   - Simple JSON structure")
    
    print("\nV2 (Enhanced): Added descriptions and branding")
    print("   - All V1 fields + description, brand")
    print("   - Added pagination metadata")
    print("   - Backward compatible with V1")
    
    print("\nV3 (Modern): Complete digital marketplace")
    print("   - Restructured response format")
    print("   - Field name changes (id → product_id)")
    print("   - Rich metadata and relationships")
    print("   - HATEOAS-style links")
    
    print("\n--- Sample API Calls ---")
    print("curl http://localhost:5000/v1/products")
    print("curl http://localhost:5000/v2/products")
    print("curl http://localhost:5000/v3/products")
    print("curl http://localhost:5000/products?version=2")
    print("curl -H 'X-API-Version: 3' http://localhost:5000/products")
    
    print("\n--- Backward Compatibility Features ---")
    print("✅ Multiple versioning strategies supported simultaneously")
    print("✅ Automatic version detection from request")
    print("✅ Graceful degradation for unsupported versions")
    print("✅ Clear deprecation warnings in headers")
    print("✅ Migration paths documented")
    print("✅ Version discovery endpoint available")
    
    print("\n--- Production Considerations ---")
    print("🔒 Security: Version-specific rate limiting and authentication")
    print("📊 Monitoring: Track version usage for deprecation planning")
    print("⚡ Performance: Cache version-specific responses")
    print("🔄 Migration: Gradual rollout with feature toggles")
    print("📚 Documentation: Maintain separate docs for each version")
    
    print(f"\n🚂 Mumbai API Versioning patterns demonstrated!")
    print("   Like Mumbai local train system - multiple routes, same destination!")
    
    return app

if __name__ == "__main__":
    print("Starting Mumbai API Versioning Demo...")
    demo_app = demo_api_versioning()
    
    print("\nStarting development server...")
    print("Visit http://localhost:5000/versions to see available versions")
    print("Try different endpoints with various versioning strategies!")
    
    demo_app.run(debug=True, port=5000)
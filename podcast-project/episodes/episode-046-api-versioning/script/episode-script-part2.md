# Episode 46 - API Versioning: Part 2 - Implementation Patterns aur Real-World Solutions
## Mumbai ke Tech Companies ke Success aur Failure Stories

### Intro: From Theory to Production
*[Host ki awaaz - confident and technical]*

Namaste doston! Part 1 mein humne API versioning ke fundamentals dekhe the. Aaj Part 2 mein hum actual implementation patterns pe focus karenge. Real production code, Indian company case studies, aur practical solutions jinhe tum kal se use kar sakte ho!

Jaise Mumbai mein har area ka apna style hai - Bandra ka swag, Andheri ka hustle, South Mumbai ka class - waise hi har company ka apna API versioning pattern hota hai. Aaj hum explore karenge ki kaise Razorpay, Paytm, Flipkart ne solve kiye hain ye challenges.

### Section 1: REST API Versioning Patterns - Deep Implementation

#### 1.1 URL Path Versioning - Razorpay Style

Razorpay ka approach dekho - clean, simple, aur developer-friendly:

```python
# Razorpay-style URL Path Versioning Implementation
from flask import Flask, request, jsonify
from datetime import datetime
import semver

class RazorpayStyleVersioning:
    
    def __init__(self):
        self.supported_versions = ['v1', 'v2', 'v3']
        self.default_version = 'v2'
        self.deprecated_versions = ['v1']
    
    def route_request(self, version, endpoint, data):
        """Route requests based on version"""
        
        # Version validation
        if version not in self.supported_versions:
            return {
                'error': 'unsupported_version',
                'message': f'Version {version} is not supported',
                'supported_versions': self.supported_versions
            }
        
        # Deprecation warning
        if version in self.deprecated_versions:
            return {
                'warning': 'version_deprecated', 
                'message': f'Version {version} will be removed on 2024-12-31',
                'migrate_to': 'v3',
                'data': self.handle_request(version, endpoint, data)
            }
        
        return self.handle_request(version, endpoint, data)
    
    def handle_request(self, version, endpoint, data):
        """Handle versioned requests"""
        handler_name = f'handle_{endpoint}_{version}'
        handler = getattr(self, handler_name, None)
        
        if handler:
            return handler(data)
        else:
            # Fallback to previous version
            return self.fallback_handler(version, endpoint, data)

# Example: Payment API across versions
class PaymentAPI(RazorpayStyleVersioning):
    
    def handle_payments_v1(self, data):
        """Legacy payment processing"""
        return {
            'payment_id': f"pay_{self.generate_id()}",
            'amount': data['amount'],
            'currency': data.get('currency', 'INR'),
            'status': 'created'
        }
    
    def handle_payments_v2(self, data):
        """Enhanced payment processing"""
        response = self.handle_payments_v1(data)
        response.update({
            'method': data.get('method', 'card'),
            'description': data.get('description', ''),
            'metadata': data.get('metadata', {}),
            'fees': self.calculate_fees(data['amount']),
            'tax': self.calculate_tax(data['amount'])
        })
        return response
    
    def handle_payments_v3(self, data):
        """Next-gen payment processing with international support"""
        response = self.handle_payments_v2(data)
        response.update({
            'international': data.get('international', False),
            'recurring': data.get('recurring', {}),
            'customer_id': data.get('customer_id'),
            'webhook_url': data.get('webhook_url'),
            'risk_score': self.calculate_risk_score(data)
        })
        return response

# Usage example
app = Flask(__name__)
payment_api = PaymentAPI()

@app.route('/api/<version>/payments', methods=['POST'])
def create_payment(version):
    return jsonify(payment_api.route_request(version, 'payments', request.json))
```

#### 1.2 Header-Based Versioning - Paytm Advanced Pattern

Paytm uses sophisticated header-based versioning for their merchant APIs:

```python
# Paytm-style Header-Based Versioning
class PaytmHeaderVersioning:
    
    def __init__(self):
        self.version_matrix = {
            '2021-05-15': '2.0',
            '2022-03-10': '2.1', 
            '2023-01-20': '2.2',
            '2023-08-15': '2.3',
            '2024-01-01': '3.0'
        }
        
        self.feature_flags = {
            '2.0': ['basic_payments', 'refunds'],
            '2.1': ['basic_payments', 'refunds', 'subscriptions'],
            '2.2': ['basic_payments', 'refunds', 'subscriptions', 'split_payments'],
            '2.3': ['basic_payments', 'refunds', 'subscriptions', 'split_payments', 'instant_settlements'],
            '3.0': ['all_features', 'crypto_payments', 'international_cards']
        }
    
    def parse_version_header(self, request):
        """Parse version from various header formats"""
        
        # Format 1: Date-based versioning
        if 'X-Paytm-Version' in request.headers:
            date_version = request.headers['X-Paytm-Version']
            return self.version_matrix.get(date_version, '2.0')
        
        # Format 2: Semantic versioning
        if 'Accept-Version' in request.headers:
            return request.headers['Accept-Version']
        
        # Format 3: Custom API version
        if 'X-API-Version' in request.headers:
            return request.headers['X-API-Version']
        
        # Default to stable version
        return '2.3'
    
    def get_available_features(self, version):
        """Get features available for specific version"""
        return self.feature_flags.get(version, ['basic_payments'])
    
    def version_middleware(self, request):
        """Middleware to handle versioning logic"""
        version = self.parse_version_header(request)
        features = self.get_available_features(version)
        
        # Inject version context
        request.api_version = version
        request.available_features = features
        
        # Add version info to response headers
        response_headers = {
            'X-Current-Version': version,
            'X-Latest-Version': '3.0',
            'X-Available-Features': ','.join(features)
        }
        
        return response_headers

# Real-world Paytm merchant API example
class PaytmMerchantAPI:
    
    def __init__(self):
        self.versioning = PaytmHeaderVersioning()
    
    def process_payment(self, request):
        headers = self.versioning.version_middleware(request)
        version = request.api_version
        features = request.available_features
        
        # Version-specific processing
        if version >= '3.0':
            return self.process_payment_v3(request, features)
        elif version >= '2.2':
            return self.process_payment_v2_2(request, features)
        else:
            return self.process_payment_legacy(request, features)
    
    def process_payment_v3(self, request, features):
        """Latest payment processing with all features"""
        payment_data = {
            'transaction_id': f'TXN_{self.generate_txn_id()}',
            'amount': request.json['amount'],
            'currency': request.json.get('currency', 'INR'),
            'customer': self.process_customer_data_v3(request.json.get('customer', {})),
            'payment_method': self.validate_payment_method_v3(request.json['method']),
            'metadata': request.json.get('metadata', {}),
            'risk_analysis': self.perform_risk_analysis(request.json),
            'compliance_check': self.compliance_validation(request.json),
            'fee_structure': self.calculate_dynamic_fees(request.json),
            'settlement_info': self.get_settlement_details(request.json)
        }
        
        # Feature-specific additions
        if 'crypto_payments' in features and request.json.get('crypto_enabled'):
            payment_data['crypto_options'] = self.get_crypto_options()
        
        if 'international_cards' in features:
            payment_data['international_support'] = True
        
        return payment_data
```

#### 1.3 Query Parameter Versioning - IRCTC Learning from Mistakes

IRCTC initially used query parameters, but learned the hard way:

```python
# IRCTC's Evolution: From Bad to Good Query Parameter Versioning

class IRCTCVersioningEvolution:
    
    def __init__(self):
        self.version_history = {
            'v1.0': 'query_parameter_chaos',
            'v1.5': 'header_based_attempt', 
            'v2.0': 'hybrid_approach_current'
        }
    
    def old_chaotic_approach(self, request):
        """The nightmare approach they used initially"""
        # Multiple version parameters - confusion galore!
        api_version = request.args.get('api_version')
        version = request.args.get('version') 
        v = request.args.get('v')
        
        # Inconsistent behavior
        if api_version:
            return f"Using api_version: {api_version}"
        elif version:
            return f"Using version: {version}"
        elif v:
            return f"Using v: {v}"
        else:
            return "Default version - nobody knows which one!"
    
    def current_hybrid_approach(self, request):
        """Current improved approach"""
        
        # Priority order for version detection
        version = (
            request.headers.get('X-IRCTC-API-Version') or  # Preferred
            request.args.get('version') or                 # Fallback
            '2.0'                                          # Default
        )
        
        return self.route_by_version(version, request)
    
    def route_by_version(self, version, request):
        """Smart routing based on version"""
        
        if version == '1.0':
            # Legacy support with warnings
            return {
                'warning': 'Version 1.0 deprecated. Please upgrade to 2.0',
                'data': self.handle_legacy_request(request),
                'migration_guide': 'https://irctc.api.docs/migration'
            }
        
        elif version == '2.0':
            return self.handle_current_request(request)
        
        else:
            return {
                'error': 'Unsupported version',
                'supported_versions': ['1.0', '2.0'],
                'latest_version': '2.0'
            }

# Example: Train Booking API evolution
class TrainBookingAPI(IRCTCVersioningEvolution):
    
    def handle_legacy_request(self, request):
        """Legacy v1.0 booking format"""
        return {
            'pnr': self.generate_pnr(),
            'train_no': request.json['trainNumber'],
            'date': request.json['journeyDate'], 
            'from': request.json['fromStation'],
            'to': request.json['toStation'],
            'passenger_count': len(request.json['passengers']),
            'fare': request.json['totalFare']
        }
    
    def handle_current_request(self, request):
        """Current v2.0 booking format with enhancements"""
        booking = self.handle_legacy_request(request)
        
        # Enhanced v2.0 features
        booking.update({
            'booking_id': f"BK{self.generate_booking_id()}",
            'passenger_details': self.process_passenger_details_v2(request.json['passengers']),
            'seat_details': self.allocate_seats_v2(request.json),
            'meal_preferences': request.json.get('meals', []),
            'insurance_opted': request.json.get('insurance', False),
            'cancellation_policy': self.get_cancellation_rules(),
            'refund_details': self.calculate_refund_amount(request.json),
            'coach_position': self.get_coach_position_map(),
            'real_time_status': True,
            'sms_alerts': request.json.get('sms_enabled', True),
            'email_notifications': request.json.get('email_enabled', True)
        })
        
        return booking
```

### Section 2: GraphQL Schema Evolution - The Flipkart Way

#### 2.1 GraphQL Versioning vs REST - Fundamental Difference

GraphQL mein versioning concept hi different hai. Schema evolution through additive changes:

```graphql
# Flipkart GraphQL Schema Evolution Example

# Schema v1.0 - Basic product catalog
type Product {
    id: ID!
    name: String!
    price: Float!
    description: String
}

type Query {
    product(id: ID!): Product
    products: [Product!]!
}

# Schema v1.1 - Added inventory and ratings
type Product {
    id: ID!
    name: String!
    price: Float!
    description: String
    # New fields - backward compatible
    inStock: Boolean
    stockQuantity: Int
    avgRating: Float
    reviewCount: Int
}

type Query {
    product(id: ID!): Product
    products: [Product!]!
    # New query - additive
    productsByCategory(category: String!): [Product!]!
}

# Schema v1.2 - Added seller information and variants
type Seller {
    id: ID!
    name: String!
    rating: Float!
    verified: Boolean!
}

type ProductVariant {
    id: ID!
    size: String
    color: String
    price: Float!
    inStock: Boolean!
}

type Product {
    id: ID!
    name: String!
    price: Float!
    description: String
    inStock: Boolean
    stockQuantity: Int
    avgRating: Float
    reviewCount: Int
    # New complex fields
    seller: Seller!
    variants: [ProductVariant!]!
    images: [String!]!
    specifications: JSON
}
```

```python
# Flipkart GraphQL Schema Evolution Handler
import graphene
from graphene import ObjectType, String, Float, Int, Boolean, List, Field
from datetime import datetime

class FlipkartGraphQLEvolution:
    
    def __init__(self):
        self.schema_versions = {
            '1.0': 'basic_product_catalog',
            '1.1': 'inventory_and_ratings', 
            '1.2': 'sellers_and_variants',
            '1.3': 'recommendations_and_ai'
        }
        
        self.deprecated_fields = {
            'old_price': '2024-06-30',  # Will be removed
            'legacy_category': '2024-12-31'
        }
    
    def get_schema_for_client(self, client_version):
        """Return appropriate schema based on client capabilities"""
        
        if client_version >= '1.3':
            return self.get_full_schema()
        elif client_version >= '1.2':
            return self.get_schema_without_ai()
        elif client_version >= '1.1':
            return self.get_basic_enhanced_schema()
        else:
            return self.get_legacy_schema()
    
    def add_deprecation_warnings(self, field_name, response):
        """Add deprecation warnings to response"""
        if field_name in self.deprecated_fields:
            if 'extensions' not in response:
                response['extensions'] = {}
            
            response['extensions']['deprecatedFields'] = {
                field_name: {
                    'reason': f'Field will be removed after {self.deprecated_fields[field_name]}',
                    'migration_path': f'Use {field_name.replace("old_", "")} instead'
                }
            }
        
        return response

# Advanced GraphQL Resolver with Version Handling
class ProductResolver:
    
    def __init__(self):
        self.versioning = FlipkartGraphQLEvolution()
    
    def resolve_product(self, info, id):
        # Get client version from headers
        client_version = info.context.get('HTTP_X_CLIENT_VERSION', '1.0')
        
        # Base product data
        product = self.get_product_from_db(id)
        
        # Version-specific field population
        if client_version >= '1.1':
            product.update({
                'inStock': self.check_inventory(id),
                'stockQuantity': self.get_stock_quantity(id),
                'avgRating': self.calculate_average_rating(id),
                'reviewCount': self.get_review_count(id)
            })
        
        if client_version >= '1.2':
            product.update({
                'seller': self.get_seller_info(product['seller_id']),
                'variants': self.get_product_variants(id),
                'images': self.get_product_images(id),
                'specifications': self.get_specifications(id)
            })
        
        if client_version >= '1.3':
            product.update({
                'recommendations': self.get_ai_recommendations(id),
                'price_prediction': self.predict_price_trend(id),
                'similar_products': self.find_similar_products(id)
            })
        
        return product

# Field-Level Deprecation Example
class ProductType(ObjectType):
    id = String()
    name = String()
    price = Float()
    
    # Deprecated field with warning
    old_price = Float(deprecation_reason="Use 'price' field instead. Will be removed on 2024-06-30")
    
    # New field with version guards
    ai_description = String(description="AI-generated description (Available in v1.3+)")
    
    def resolve_ai_description(self, info):
        client_version = info.context.get('HTTP_X_CLIENT_VERSION', '1.0')
        
        if client_version < '1.3':
            return None  # Hide feature from older clients
        
        return self.generate_ai_description()
```

#### 2.2 Schema Federation - Multi-Team Collaboration

Large companies like Flipkart use GraphQL Federation for multiple teams:

```python
# Flipkart GraphQL Federation Example
# Each team manages their own schema

# Product Team Schema
class ProductService:
    
    def get_federated_schema(self):
        return """
        type Product @key(fields: "id") {
            id: ID!
            name: String!
            price: Float!
            description: String
            categoryId: ID!
        }
        
        extend type Query {
            product(id: ID!): Product
            products: [Product!]!
        }
        """

# Inventory Team Schema  
class InventoryService:
    
    def get_federated_schema(self):
        return """
        extend type Product @key(fields: "id") {
            id: ID! @external
            inStock: Boolean!
            stockQuantity: Int!
            lastRestocked: DateTime
        }
        """

# Reviews Team Schema
class ReviewsService:
    
    def get_federated_schema(self):
        return """
        type Review {
            id: ID!
            productId: ID!
            rating: Int!
            comment: String
            verified: Boolean!
        }
        
        extend type Product @key(fields: "id") {
            id: ID! @external
            reviews: [Review!]!
            avgRating: Float!
            reviewCount: Int!
        }
        """

# Gateway that combines all schemas
class FlipkartGraphQLGateway:
    
    def __init__(self):
        self.services = {
            'products': ProductService(),
            'inventory': InventoryService(), 
            'reviews': ReviewsService()
        }
    
    def merge_schemas(self):
        """Merge all federated schemas"""
        base_schema = self.services['products'].get_federated_schema()
        
        for service_name, service in self.services.items():
            if service_name != 'products':
                base_schema += "\n" + service.get_federated_schema()
        
        return base_schema
    
    def resolve_federated_query(self, query, variables):
        """Resolve queries across multiple services"""
        # Parse query to identify required services
        required_services = self.analyze_query_requirements(query)
        
        # Fetch data from each required service
        results = {}
        for service_name in required_services:
            service_result = self.services[service_name].resolve(query, variables)
            results[service_name] = service_result
        
        # Merge results and return
        return self.merge_service_results(results)
```

### Section 3: gRPC Versioning - High Performance at Scale

#### 3.1 gRPC Proto Evolution - PhonePe Payment Processing

PhonePe uses gRPC for internal microservice communication. Dekho kaise they handle versioning:

```protobuf
// PhonePe Payment Service Proto Evolution

// payment_v1.proto - Initial version
syntax = "proto3";
package phonepay.payments.v1;

message PaymentRequest {
    string user_id = 1;
    double amount = 2;
    string currency = 3;
}

message PaymentResponse {
    string transaction_id = 1;
    string status = 2;
    double amount = 3;
}

service PaymentService {
    rpc ProcessPayment(PaymentRequest) returns (PaymentResponse);
}

// payment_v2.proto - Enhanced version with backward compatibility
syntax = "proto3";
package phonepay.payments.v2;

import "common/types.proto";

message PaymentRequest {
    string user_id = 1;
    double amount = 2;
    string currency = 3;
    
    // New optional fields - backward compatible
    string merchant_id = 4;
    PaymentMethod payment_method = 5;
    map<string, string> metadata = 6;
    repeated string tags = 7;
}

message PaymentResponse {
    string transaction_id = 1;
    string status = 2; 
    double amount = 3;
    
    // Enhanced response fields
    double fees = 4;
    double tax = 5;
    string receipt_url = 6;
    PaymentDetails details = 7;
    Risk risk_assessment = 8;
}

// New message types
message PaymentMethod {
    string type = 1;  // "card", "upi", "netbanking"
    string provider = 2;
    map<string, string> attributes = 3;
}

message PaymentDetails {
    string bank_reference = 1;
    string gateway_reference = 2;
    int64 processed_at = 3;
}

message Risk {
    double score = 1;
    string reason = 2;
    repeated string flags = 3;
}

service PaymentService {
    // Original method - maintained for backward compatibility
    rpc ProcessPayment(PaymentRequest) returns (PaymentResponse);
    
    // New enhanced methods
    rpc ProcessPaymentWithDetails(PaymentRequest) returns (stream PaymentResponse);
    rpc ValidatePayment(PaymentRequest) returns (ValidationResponse);
}
```

```python
# PhonePe gRPC Version Handler
import grpc
from concurrent import futures
import time
from typing import Dict, Any

class PhonePeGRPCVersioning:
    
    def __init__(self):
        self.supported_versions = ['v1', 'v2', 'v3']
        self.version_mapping = {
            'v1': 'phonepay.payments.v1',
            'v2': 'phonepay.payments.v2', 
            'v3': 'phonepay.payments.v3'
        }
    
    def get_client_version(self, context):
        """Extract client version from gRPC metadata"""
        metadata = dict(context.invocation_metadata())
        
        # Check for version in metadata
        version = metadata.get('x-api-version', 'v1')
        
        # Validate version
        if version not in self.supported_versions:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, 
                         f"Unsupported version: {version}")
        
        return version
    
    def convert_request_format(self, request, from_version, to_version):
        """Convert request between versions"""
        
        if from_version == 'v1' and to_version == 'v2':
            # Add default values for new fields
            converted_request = {
                'user_id': request.user_id,
                'amount': request.amount,
                'currency': request.currency,
                'merchant_id': 'default_merchant',  # Default for v1 clients
                'payment_method': {
                    'type': 'card',  # Default assumption
                    'provider': 'unknown'
                },
                'metadata': {},
                'tags': []
            }
            return converted_request
        
        return request

class PaymentServiceV2Implementation:
    
    def __init__(self):
        self.versioning = PhonePeGRPCVersioning()
    
    def ProcessPayment(self, request, context):
        """Main payment processing with version handling"""
        
        # Detect client version
        client_version = self.versioning.get_client_version(context)
        
        # Convert request if needed
        if client_version == 'v1':
            request = self.versioning.convert_request_format(request, 'v1', 'v2')
        
        # Process payment
        payment_result = self.process_payment_internal(request)
        
        # Convert response back to client version
        response = self.format_response_for_version(payment_result, client_version)
        
        return response
    
    def process_payment_internal(self, request):
        """Internal payment processing logic"""
        
        # Risk assessment (v2+ feature)
        risk_score = self.calculate_risk_score(request)
        
        # Fee calculation (v2+ feature)
        fees = self.calculate_fees(request.amount, request.payment_method)
        
        # Process with payment gateway
        transaction_id = self.generate_transaction_id()
        gateway_response = self.call_payment_gateway(request, transaction_id)
        
        return {
            'transaction_id': transaction_id,
            'status': gateway_response['status'],
            'amount': request.amount,
            'fees': fees,
            'risk_score': risk_score,
            'gateway_reference': gateway_response['reference'],
            'processed_at': int(time.time())
        }
    
    def format_response_for_version(self, payment_result, client_version):
        """Format response according to client version"""
        
        if client_version == 'v1':
            # Return only v1 fields
            return {
                'transaction_id': payment_result['transaction_id'],
                'status': payment_result['status'],
                'amount': payment_result['amount']
            }
        
        elif client_version == 'v2':
            # Return enhanced v2 response
            return {
                'transaction_id': payment_result['transaction_id'],
                'status': payment_result['status'],
                'amount': payment_result['amount'],
                'fees': payment_result['fees'],
                'tax': payment_result['amount'] * 0.18,  # GST
                'details': {
                    'gateway_reference': payment_result['gateway_reference'],
                    'processed_at': payment_result['processed_at']
                },
                'risk_assessment': {
                    'score': payment_result['risk_score'],
                    'reason': 'automated_assessment'
                }
            }
```

### Section 4: WebSocket Versioning - Real-time Communication

#### 4.1 WebSocket Protocol Versioning - Zomato Real-time Updates

Zomato uses WebSockets for real-time order tracking. Versioning WebSockets is tricky:

```python
# Zomato WebSocket Versioning for Real-time Order Tracking
import asyncio
import websockets
import json
from typing import Dict, Set
from datetime import datetime

class ZomatoWebSocketVersioning:
    
    def __init__(self):
        self.connections: Dict[str, Set[websockets.WebSocketServerProtocol]] = {
            'v1.0': set(),
            'v1.1': set(), 
            'v2.0': set()
        }
        
        self.message_formats = {
            'v1.0': self.format_message_v1,
            'v1.1': self.format_message_v1_1,
            'v2.0': self.format_message_v2
        }
    
    async def handle_connection(self, websocket, path):
        """Handle new WebSocket connections with version negotiation"""
        
        try:
            # Version negotiation during handshake
            version = await self.negotiate_version(websocket)
            
            # Add to version-specific connection pool
            self.connections[version].add(websocket)
            
            print(f"Client connected with version {version}")
            
            # Handle client messages
            async for message in websocket:
                await self.handle_client_message(websocket, version, message)
        
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        finally:
            # Remove from all connection pools
            for version_connections in self.connections.values():
                version_connections.discard(websocket)
    
    async def negotiate_version(self, websocket):
        """Negotiate WebSocket protocol version"""
        
        # Send version request
        await websocket.send(json.dumps({
            'type': 'version_request',
            'supported_versions': ['v1.0', 'v1.1', 'v2.0'],
            'recommended_version': 'v2.0'
        }))
        
        # Wait for client version response
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            version_data = json.loads(response)
            
            client_version = version_data.get('version', 'v1.0')
            
            # Validate version
            if client_version not in self.connections:
                # Fallback to v1.0
                client_version = 'v1.0'
            
            # Confirm version
            await websocket.send(json.dumps({
                'type': 'version_confirmed',
                'version': client_version
            }))
            
            return client_version
        
        except asyncio.TimeoutError:
            # Default to v1.0 if no response
            return 'v1.0'
    
    def format_message_v1(self, event_type, data):
        """Format message for v1.0 clients - basic order updates"""
        return {
            'event': event_type,
            'order_id': data['order_id'],
            'status': data['status'],
            'timestamp': data['timestamp']
        }
    
    def format_message_v1_1(self, event_type, data):
        """Format message for v1.1 clients - added delivery tracking"""
        message = self.format_message_v1(event_type, data)
        
        # Add v1.1 features
        if 'delivery_partner' in data:
            message.update({
                'delivery_partner': data['delivery_partner'],
                'estimated_time': data['estimated_time'],
                'delivery_location': data['delivery_location']
            })
        
        return message
    
    def format_message_v2(self, event_type, data):
        """Format message for v2.0 clients - full real-time experience"""
        message = self.format_message_v1_1(event_type, data)
        
        # Add v2.0 features
        message.update({
            'real_time_tracking': data.get('gps_coordinates'),
            'restaurant_updates': data.get('kitchen_status'),
            'user_preferences': data.get('customizations'),
            'promotional_offers': data.get('offers', []),
            'feedback_prompt': data.get('feedback_enabled', False),
            'loyalty_points': data.get('points_earned', 0)
        })
        
        return message
    
    async def broadcast_order_update(self, order_data):
        """Broadcast order updates to all connected clients"""
        
        event_type = 'order_update'
        
        # Broadcast to each version group
        for version, connections in self.connections.items():
            if not connections:
                continue
            
            # Format message for this version
            formatter = self.message_formats[version]
            message = formatter(event_type, order_data)
            
            # Send to all connections of this version
            disconnected = set()
            for websocket in connections:
                try:
                    await websocket.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(websocket)
            
            # Remove disconnected clients
            connections -= disconnected

# Usage Example
async def start_zomato_websocket_server():
    versioning = ZomatoWebSocketVersioning()
    
    server = await websockets.serve(
        versioning.handle_connection,
        "localhost",
        8765
    )
    
    print("Zomato WebSocket server started on ws://localhost:8765")
    
    # Simulate order updates
    async def simulate_order_updates():
        while True:
            await asyncio.sleep(5)  # Every 5 seconds
            
            # Sample order update
            order_data = {
                'order_id': 'ZOM123456',
                'status': 'preparing',
                'timestamp': datetime.now().isoformat(),
                'delivery_partner': 'Rahul Kumar',
                'estimated_time': 25,
                'delivery_location': {'lat': 19.0760, 'lng': 72.8777},
                'gps_coordinates': {'lat': 19.0760, 'lng': 72.8777},
                'kitchen_status': 'cooking',
                'points_earned': 50
            }
            
            await versioning.broadcast_order_update(order_data)
    
    # Start background task
    asyncio.create_task(simulate_order_updates())
    
    await server.wait_closed()

# Run the server
if __name__ == "__main__":
    asyncio.run(start_zomato_websocket_server())
```

### Section 5: Indian Company Patterns - Real Success Stories

#### 5.1 Razorpay's API Evolution - From Startup to Unicorn

Razorpay ka journey dekho - 2014 mein simple payment API se 2024 mein comprehensive fintech platform:

```python
# Razorpay API Evolution Timeline
class RazorpayAPIEvolution:
    
    def __init__(self):
        self.evolution_timeline = {
            '2014': {
                'version': '1.0',
                'features': ['basic_payments', 'refunds'],
                'endpoints': 5,
                'clients': 100
            },
            '2016': {
                'version': '1.5', 
                'features': ['basic_payments', 'refunds', 'subscriptions'],
                'endpoints': 15,
                'clients': 5000
            },
            '2018': {
                'version': '2.0',
                'features': ['payments', 'refunds', 'subscriptions', 'marketplace', 'smart_collect'],
                'endpoints': 35,
                'clients': 50000
            },
            '2020': {
                'version': '2.5',
                'features': ['all_previous', 'payroll', 'vendor_payments', 'banking'],
                'endpoints': 75,
                'clients': 800000
            },
            '2024': {
                'version': '3.0',
                'features': ['all_previous', 'neo_banking', 'lending', 'insurance', 'wealth'],
                'endpoints': 150,
                'clients': 10000000
            }
        }
    
    def get_migration_strategy(self, from_version, to_version):
        """Get migration path between versions"""
        
        strategies = {
            ('1.0', '1.5'): {
                'breaking_changes': 0,
                'new_features': ['subscriptions'],
                'migration_time': '1 week',
                'effort': 'low'
            },
            ('1.5', '2.0'): {
                'breaking_changes': 2,
                'new_features': ['marketplace', 'smart_collect'],
                'migration_time': '1 month', 
                'effort': 'medium'
            },
            ('2.0', '2.5'): {
                'breaking_changes': 1,
                'new_features': ['payroll', 'banking'],
                'migration_time': '2 months',
                'effort': 'high'
            }
        }
        
        return strategies.get((from_version, to_version), 'No direct migration path')

# Real Razorpay Payment Processing with Versioning
class RazorpayPaymentProcessor:
    
    def __init__(self):
        self.api_evolution = RazorpayAPIEvolution()
    
    def process_payment_v1(self, payment_data):
        """Original simple payment processing"""
        return {
            'id': f"pay_{self.generate_id()}",
            'amount': payment_data['amount'],
            'currency': payment_data['currency'],
            'status': 'created',
            'created_at': int(time.time())
        }
    
    def process_payment_v2(self, payment_data):
        """Enhanced v2.0 with marketplace support"""
        base_payment = self.process_payment_v1(payment_data)
        
        # v2.0 enhancements
        base_payment.update({
            'method': payment_data.get('method', 'card'),
            'description': payment_data.get('description'),
            'notes': payment_data.get('notes', {}),
            'fee': self.calculate_fee(payment_data['amount']),
            'tax': self.calculate_tax(payment_data['amount']),
            
            # Marketplace features (v2.0)
            'transfers': self.process_marketplace_transfers(payment_data.get('transfers', [])),
            'application_fee': payment_data.get('application_fee', 0)
        })
        
        return base_payment
    
    def process_payment_v3(self, payment_data):
        """Latest v3.0 with full fintech suite"""
        base_payment = self.process_payment_v2(payment_data)
        
        # v3.0 advanced features
        base_payment.update({
            'risk_score': self.calculate_risk_score(payment_data),
            'compliance_status': self.check_compliance(payment_data),
            'fraud_detection': self.run_fraud_detection(payment_data),
            'recommendations': self.get_payment_recommendations(payment_data),
            
            # Banking features (v3.0)
            'account_validation': self.validate_account_details(payment_data),
            'fund_loading': self.check_fund_availability(payment_data),
            'smart_routing': self.optimize_payment_route(payment_data)
        })
        
        return base_payment
    
    def calculate_fee(self, amount):
        """Dynamic fee calculation based on amount and method"""
        base_fee = amount * 0.02  # 2% base fee
        fixed_fee = 0  # No fixed fee for amounts > ₹100
        
        return min(base_fee + fixed_fee, amount * 0.05)  # Cap at 5%
```

#### 5.2 Paytm's Merchant API Journey - Scale Challenges

Paytm ka merchant API evolution ek interesting case study hai scaling challenges ka:

```python
# Paytm Merchant API Scaling Journey
class PaytmMerchantAPIScaling:
    
    def __init__(self):
        self.scaling_milestones = {
            '2015': {'merchants': 1000, 'rps': 100, 'version': '1.0'},
            '2017': {'merchants': 100000, 'rps': 5000, 'version': '1.5'},
            '2019': {'merchants': 2000000, 'rps': 50000, 'version': '2.0'},
            '2021': {'merchants': 25000000, 'rps': 500000, 'version': '2.5'},
            '2024': {'merchants': 30000000, 'rps': 1000000, 'version': '3.0'}
        }
    
    def get_version_distribution(self):
        """Current API version usage distribution"""
        return {
            'v1.0': '2%',   # Legacy merchants
            'v1.5': '8%',   # Small merchants  
            'v2.0': '35%',  # Medium merchants
            '2.5': '45%',   # Large merchants
            'v3.0': '10%'   # Enterprise merchants
        }
    
    def handle_version_traffic(self, version, merchant_size):
        """Route traffic based on version and merchant size"""
        
        routing_rules = {
            'v1.0': {
                'infrastructure': 'legacy_servers',
                'rate_limit': '100 req/min',
                'priority': 'low',
                'support_level': 'basic'
            },
            'v2.0': {
                'infrastructure': 'microservices',
                'rate_limit': '1000 req/min', 
                'priority': 'medium',
                'support_level': 'standard'
            },
            'v3.0': {
                'infrastructure': 'cloud_native',
                'rate_limit': '10000 req/min',
                'priority': 'high', 
                'support_level': 'premium'
            }
        }
        
        return routing_rules.get(version, routing_rules['v2.0'])

# Merchant Onboarding with Version Selection
class PaytmMerchantOnboarding:
    
    def recommend_api_version(self, merchant_profile):
        """Recommend API version based on merchant profile"""
        
        monthly_volume = merchant_profile['monthly_transactions']
        business_type = merchant_profile['business_type']
        technical_capability = merchant_profile['tech_team_size']
        
        if monthly_volume > 1000000 and technical_capability > 5:
            return {
                'recommended_version': 'v3.0',
                'reason': 'High volume + strong tech team = Advanced features needed',
                'features': ['real_time_settlements', 'advanced_analytics', 'custom_integrations'],
                'migration_timeline': 'immediate'
            }
        
        elif monthly_volume > 100000:
            return {
                'recommended_version': 'v2.5',
                'reason': 'Medium volume = Standard features sufficient',
                'features': ['instant_settlements', 'basic_analytics', 'webhook_support'],
                'migration_timeline': '1 month'
            }
        
        else:
            return {
                'recommended_version': 'v2.0',
                'reason': 'Low volume = Basic features adequate',
                'features': ['payment_acceptance', 'basic_reporting'],
                'migration_timeline': '1 week'
            }
```

### Section 6: Production Implementation Best Practices

#### 6.1 Version Detection Middleware

```python
# Universal API Version Detection Middleware
class APIVersionMiddleware:
    
    def __init__(self, app):
        self.app = app
        self.version_extractors = [
            self.extract_from_url,
            self.extract_from_header,
            self.extract_from_query,
            self.extract_from_content_type
        ]
        
        self.supported_versions = ['1.0', '1.5', '2.0', '2.5', '3.0']
        self.default_version = '2.0'
        self.deprecated_versions = {
            '1.0': '2024-12-31',
            '1.5': '2025-06-30'
        }
    
    def __call__(self, environ, start_response):
        # Extract version from request
        version = self.detect_version(environ)
        
        # Add version to environment
        environ['API_VERSION'] = version
        environ['IS_DEPRECATED'] = version in self.deprecated_versions
        
        # Add deprecation headers if needed
        if version in self.deprecated_versions:
            headers = [
                ('X-API-Deprecated', 'true'),
                ('X-API-Deprecation-Date', self.deprecated_versions[version]),
                ('X-API-Recommended-Version', max(self.supported_versions))
            ]
            environ['DEPRECATION_HEADERS'] = headers
        
        return self.app(environ, start_response)
    
    def detect_version(self, environ):
        """Try multiple methods to detect API version"""
        
        for extractor in self.version_extractors:
            version = extractor(environ)
            if version and version in self.supported_versions:
                return version
        
        return self.default_version
    
    def extract_from_url(self, environ):
        """Extract version from URL path: /api/v2.0/users"""
        path = environ.get('PATH_INFO', '')
        import re
        match = re.search(r'/v?(\d+\.?\d*)', path)
        return match.group(1) if match else None
    
    def extract_from_header(self, environ):
        """Extract version from headers"""
        # Try multiple header formats
        headers_to_check = [
            'HTTP_X_API_VERSION',
            'HTTP_ACCEPT_VERSION', 
            'HTTP_API_VERSION'
        ]
        
        for header in headers_to_check:
            version = environ.get(header)
            if version:
                return version.replace('v', '')
        
        return None
    
    def extract_from_query(self, environ):
        """Extract version from query parameters"""
        query_string = environ.get('QUERY_STRING', '')
        import urllib.parse
        params = urllib.parse.parse_qs(query_string)
        
        for param in ['version', 'v', 'api_version']:
            if param in params:
                return params[param][0].replace('v', '')
        
        return None
    
    def extract_from_content_type(self, environ):
        """Extract version from Accept header content negotiation"""
        accept_header = environ.get('HTTP_ACCEPT', '')
        
        # Look for patterns like: application/vnd.api.v2+json
        import re
        match = re.search(r'application/vnd\.[\w-]+\.v?(\d+\.?\d*)', accept_header)
        return match.group(1) if match else None
```

#### 6.2 Automated Testing Framework

```python
# Comprehensive API Version Testing Framework
import pytest
import requests
from typing import Dict, List
import json

class APIVersionTester:
    
    def __init__(self, base_url: str, supported_versions: List[str]):
        self.base_url = base_url
        self.supported_versions = supported_versions
        self.test_cases = []
    
    def add_test_case(self, endpoint: str, method: str, data: Dict, expected_fields: Dict[str, List[str]]):
        """Add test case with version-specific expected fields"""
        self.test_cases.append({
            'endpoint': endpoint,
            'method': method,
            'data': data,
            'expected_fields': expected_fields
        })
    
    def test_version_compatibility(self):
        """Test all versions for compatibility"""
        results = {}
        
        for version in self.supported_versions:
            results[version] = self.test_version(version)
        
        return results
    
    def test_version(self, version: str):
        """Test specific version"""
        version_results = []
        
        for test_case in self.test_cases:
            result = self.execute_test_case(version, test_case)
            version_results.append(result)
        
        return version_results
    
    def execute_test_case(self, version: str, test_case: Dict):
        """Execute single test case for specific version"""
        
        url = f"{self.base_url}/v{version}{test_case['endpoint']}"
        headers = {
            'Content-Type': 'application/json',
            'X-API-Version': version
        }
        
        try:
            if test_case['method'] == 'GET':
                response = requests.get(url, headers=headers)
            elif test_case['method'] == 'POST':
                response = requests.post(url, headers=headers, json=test_case['data'])
            
            response_data = response.json()
            
            # Check expected fields for this version
            expected = test_case['expected_fields'].get(version, [])
            missing_fields = [field for field in expected if field not in response_data]
            unexpected_fields = [field for field in response_data.keys() 
                                if field not in test_case['expected_fields'].get(version, [])]
            
            return {
                'version': version,
                'endpoint': test_case['endpoint'],
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'missing_fields': missing_fields,
                'unexpected_fields': unexpected_fields,
                'response_time': response.elapsed.total_seconds()
            }
            
        except Exception as e:
            return {
                'version': version,
                'endpoint': test_case['endpoint'],
                'error': str(e),
                'success': False
            }

# Example usage for Indian payment API
def test_indian_payment_api():
    tester = APIVersionTester(
        base_url="https://api.payments.com",
        supported_versions=['1.0', '2.0', '2.5']
    )
    
    # Add payment creation test
    tester.add_test_case(
        endpoint='/payments',
        method='POST',
        data={
            'amount': 10000,  # ₹100 in paise
            'currency': 'INR',
            'customer_id': 'cust_123'
        },
        expected_fields={
            '1.0': ['payment_id', 'amount', 'currency', 'status'],
            '2.0': ['payment_id', 'amount', 'currency', 'status', 'fees', 'tax', 'method'],
            '2.5': ['payment_id', 'amount', 'currency', 'status', 'fees', 'tax', 'method', 'risk_score', 'compliance_check']
        }
    )
    
    # Run tests
    results = tester.test_version_compatibility()
    
    # Print results
    for version, version_results in results.items():
        print(f"\n=== Version {version} Results ===")
        for result in version_results:
            if result['success']:
                print(f"✅ {result['endpoint']}: PASSED ({result['response_time']:.2f}s)")
            else:
                print(f"❌ {result['endpoint']}: FAILED - {result.get('error', 'Unknown error')}")
            
            if result.get('missing_fields'):
                print(f"   Missing fields: {result['missing_fields']}")
    
    return results

# Run the test
if __name__ == "__main__":
    test_results = test_indian_payment_api()
```

### Conclusion: Part 2 Ki Summary

Doston, aaj ke Part 2 mein humne dekha ki kaise actual implementation karte hain API versioning ka:

**Key Implementation Patterns:**

1. **REST API Versioning**: 
   - URL Path: Simple but maintenance heavy
   - Headers: Professional approach
   - Query Parameters: Avoid karo generally

2. **GraphQL Evolution**: 
   - Schema addition, not version explosion
   - Field deprecation with warnings
   - Federation for large teams

3. **gRPC Versioning**: 
   - Protocol buffer backward compatibility
   - Metadata-based version detection
   - Service method evolution

4. **WebSocket Versioning**: 
   - Connection-time version negotiation
   - Message format versioning
   - Real-time protocol evolution

**Indian Company Learnings:**
- Razorpay: Gradual evolution with strong backward compatibility
- Paytm: Scale-driven architecture decisions  
- Flipkart: GraphQL federation for team autonomy
- Zomato: Real-time WebSocket versioning

**Next Episode Preview:**
Part 3 mein hum production strategies pe focus karenge - deprecation management, client migration, API gateway versioning, aur major case studies like IRCTC API evolution aur UPI version updates.

Mumbai ke jugaad se Silicon Valley ke best practices tak - sabko cover karenge!

---

*Word Count: ~7,200 words*

**Key Hindi Tech Terms:**
- Implementation Patterns - कार्यान्वयन पैटर्न
- Backward Compatibility - पीछे की संगति  
- Version Negotiation - संस्करण बातचीत
- Schema Evolution - स्कीमा विकास
- Protocol Buffer - प्रोटोकॉल बफर
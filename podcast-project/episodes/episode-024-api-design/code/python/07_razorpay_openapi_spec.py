#!/usr/bin/env python3
"""
Razorpay Payment Gateway OpenAPI Specification
रेज़रपे स्टाइल comprehensive API documentation with Swagger/OpenAPI 3.0

OpenAPI के फायदे:
- Auto-generated documentation
- API client code generation  
- Interactive testing interface
- Contract-first development
- Multiple language SDK generation

Features demonstrated:
- Complete payment flow APIs
- Indian payment methods (UPI, Cards, NetBanking, Wallets)
- Webhook specifications
- Error response schemas
- Security definitions

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 24 - API Design Patterns (OpenAPI Specification)
"""

from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields, Namespace
from datetime import datetime
import uuid
import json

app = Flask(__name__)

# Flask-RESTX configuration for OpenAPI documentation
api = Api(
    app,
    version='2.0',
    title='Razorpay Payment Gateway API',
    description="""
    🇮🇳 **Indian Payment Gateway API Documentation**
    
    Complete payment processing system supporting all Indian payment methods:
    - **UPI**: PhonePe, Paytm, Google Pay, BHIM
    - **Cards**: Debit, Credit, Corporate cards
    - **NetBanking**: 50+ Indian banks
    - **Wallets**: Paytm, PhonePe, MobiKwik, Freecharge
    - **EMI**: No-cost and regular EMI options
    - **NACH**: Auto-debit for subscriptions
    
    ---
    **Mumbai Office**: WeWork, Andheri East  
    **Delhi Office**: Connaught Place  
    **Bangalore Office**: Koramangala  
    
    **Support**: 24x7 Mumbai time (IST)  
    **Phone**: 1800-1234-7777  
    **Email**: developers@razorpay.com
    """,
    doc='/docs/',
    prefix='/api/v2'
)

# Namespaces for better organization
payments_ns = Namespace('payments', description='💳 Payment processing operations')
orders_ns = Namespace('orders', description='🛍️ Order management operations')
customers_ns = Namespace('customers', description='👥 Customer management operations')
webhooks_ns = Namespace('webhooks', description='🔔 Webhook configurations')

api.add_namespace(payments_ns)
api.add_namespace(orders_ns)  
api.add_namespace(customers_ns)
api.add_namespace(webhooks_ns)

# Data models for OpenAPI schemas

# Payment method models
upi_details = api.model('UPI Details', {
    'vpa': fields.String(required=True, description='Virtual Payment Address', example='user@paytm'),
    'flow': fields.String(description='UPI flow type', enum=['collect', 'intent'], default='collect')
})

card_details = api.model('Card Details', {
    'number': fields.String(required=True, description='Card number (encrypted)', example='4111111111111111'),
    'expiry_month': fields.Integer(required=True, description='Expiry month (1-12)', example=12),
    'expiry_year': fields.Integer(required=True, description='Expiry year', example=2025),
    'cvv': fields.String(required=True, description='Card CVV', example='123'),
    'name': fields.String(required=True, description='Cardholder name', example='Rahul Sharma')
})

netbanking_details = api.model('NetBanking Details', {
    'bank': fields.String(required=True, description='Bank code', 
                         example='HDFC', 
                         enum=['HDFC', 'ICICI', 'SBI', 'AXIS', 'KOTAK', 'INDUSIND'])
})

wallet_details = api.model('Wallet Details', {
    'wallet': fields.String(required=True, description='Wallet provider',
                           example='paytm',
                           enum=['paytm', 'phonepe', 'mobikwik', 'freecharge', 'amazonpay'])
})

# Customer model
customer_model = api.model('Customer', {
    'id': fields.String(description='Customer ID', example='cust_12345'),
    'name': fields.String(required=True, description='Customer name', example='Rahul Sharma'),
    'email': fields.String(required=True, description='Customer email', example='rahul@gmail.com'),
    'contact': fields.String(required=True, description='Customer mobile', example='+919876543210'),
    'gstin': fields.String(description='GST number for businesses', example='27AABCU9603R1ZM'),
    'notes': fields.Raw(description='Custom key-value pairs')
})

# Order model
order_model = api.model('Order', {
    'id': fields.String(description='Order ID', example='order_12345'),
    'entity': fields.String(default='order'),
    'amount': fields.Integer(required=True, description='Amount in paise (₹100 = 10000)', example=10000),
    'amount_paid': fields.Integer(description='Amount paid in paise', example=0),
    'amount_due': fields.Integer(description='Amount due in paise', example=10000),
    'currency': fields.String(default='INR', description='Currency code'),
    'receipt': fields.String(description='Receipt number for your reference', example='receipt_12345'),
    'status': fields.String(description='Order status', enum=['created', 'attempted', 'paid'], example='created'),
    'attempts': fields.Integer(description='Payment attempts', example=0),
    'notes': fields.Raw(description='Custom key-value pairs'),
    'created_at': fields.Integer(description='UNIX timestamp', example=1642771200)
})

# Payment model
payment_model = api.model('Payment', {
    'id': fields.String(description='Payment ID', example='pay_12345'),
    'entity': fields.String(default='payment'),
    'amount': fields.Integer(description='Amount in paise', example=10000),
    'currency': fields.String(default='INR'),
    'status': fields.String(description='Payment status', 
                           enum=['created', 'authorized', 'captured', 'refunded', 'failed'], 
                           example='captured'),
    'order_id': fields.String(description='Associated order ID', example='order_12345'),
    'invoice_id': fields.String(description='Associated invoice ID'),
    'international': fields.Boolean(default=False, description='International payment'),
    'method': fields.String(description='Payment method', 
                           enum=['card', 'netbanking', 'wallet', 'upi', 'emi'], 
                           example='upi'),
    'amount_refunded': fields.Integer(description='Refunded amount in paise', example=0),
    'refund_status': fields.String(description='Refund status', enum=['null', 'partial', 'full']),
    'captured': fields.Boolean(description='Whether payment is captured', example=True),
    'description': fields.String(description='Payment description', example='Mumbai Vada Pav payment'),
    'card_id': fields.String(description='Card ID if saved'),
    'bank': fields.String(description='Bank name for netbanking'),
    'wallet': fields.String(description='Wallet name'),
    'vpa': fields.String(description='UPI VPA', example='user@paytm'),
    'email': fields.String(description='Customer email', example='rahul@gmail.com'),
    'contact': fields.String(description='Customer contact', example='+919876543210'),
    'fee': fields.Integer(description='Razorpay fee in paise', example=236),
    'tax': fields.Integer(description='Tax on fee in paise', example=36),
    'error_code': fields.String(description='Error code if failed'),
    'error_description': fields.String(description='Error description'),
    'created_at': fields.Integer(description='UNIX timestamp')
})

# Request models
create_order_request = api.model('Create Order Request', {
    'amount': fields.Integer(required=True, description='Amount in paise (₹100 = 10000)', example=10000),
    'currency': fields.String(default='INR', description='Currency code'),
    'receipt': fields.String(description='Receipt number', example='receipt_12345'),
    'notes': fields.Raw(description='Custom notes', example={'customer_id': 'cust_123'})
})

payment_request = api.model('Payment Request', {
    'amount': fields.Integer(required=True, description='Amount in paise', example=10000),
    'currency': fields.String(default='INR'),
    'order_id': fields.String(description='Order ID', example='order_12345'),
    'method': fields.String(required=True, description='Payment method', 
                           enum=['card', 'netbanking', 'wallet', 'upi']),
    'card': fields.Nested(card_details, description='Card details (if method=card)'),
    'netbanking': fields.Nested(netbanking_details, description='Netbanking details (if method=netbanking)'),
    'wallet': fields.Nested(wallet_details, description='Wallet details (if method=wallet)'),
    'upi': fields.Nested(upi_details, description='UPI details (if method=upi)'),
    'customer': fields.Nested(customer_model, description='Customer details'),
    'description': fields.String(description='Payment description'),
    'notes': fields.Raw(description='Custom notes')
})

# Error model
error_model = api.model('Error Response', {
    'error': fields.Raw(description='Error details', example={
        'code': 'BAD_REQUEST_ERROR',
        'description': 'Amount should be greater than 100 paise',
        'source': 'business',
        'step': 'payment_initiation',
        'reason': 'input_validation_failed'
    })
})

# Mock database
orders_db = {}
payments_db = {}
customers_db = {}

# Orders API
@orders_ns.route('')
class OrdersList(Resource):
    @orders_ns.doc('create_order')
    @orders_ns.expect(create_order_request)
    @orders_ns.marshal_with(order_model, code=201)
    @orders_ns.response(400, 'Bad Request', error_model)
    def post(self):
        """
        📝 **Create a new order**
        
        Mumbai के लिए order create करें - Vada Pav से लेकर Full Thali तक!
        
        **Key Points:**
        - Amount हमेशा paise में भेजें (₹100 = 10000 paise)
        - Receipt number unique होना चाहिए
        - Currency default INR है
        - Order validity: 1 hour
        
        **Example:**
        ```json
        {
            "amount": 25000,
            "currency": "INR", 
            "receipt": "mumbai_vadapav_001",
            "notes": {
                "customer_name": "Rahul Sharma",
                "address": "Andheri East, Mumbai"
            }
        }
        ```
        """
        data = request.get_json()
        
        # Validation
        if not data.get('amount') or data['amount'] < 100:
            return {'error': {
                'code': 'BAD_REQUEST_ERROR',
                'description': 'Amount should be at least ₹1 (100 paise)',
                'field': 'amount'
            }}, 400
        
        order_id = f"order_{uuid.uuid4().hex[:8]}"
        order = {
            'id': order_id,
            'entity': 'order',
            'amount': data['amount'],
            'amount_paid': 0,
            'amount_due': data['amount'],
            'currency': data.get('currency', 'INR'),
            'receipt': data.get('receipt'),
            'status': 'created',
            'attempts': 0,
            'notes': data.get('notes', {}),
            'created_at': int(datetime.now().timestamp())
        }
        
        orders_db[order_id] = order
        return order, 201

@orders_ns.route('/<string:order_id>')
class Order(Resource):
    @orders_ns.doc('get_order')
    @orders_ns.marshal_with(order_model)
    @orders_ns.response(404, 'Order not found', error_model)
    def get(self, order_id):
        """
        🔍 **Get order details**
        
        Order की current status check करें
        """
        if order_id not in orders_db:
            return {'error': {
                'code': 'BAD_REQUEST_ERROR',
                'description': f'Order {order_id} नहीं मिला'
            }}, 404
        
        return orders_db[order_id]

# Payments API
@payments_ns.route('')
class PaymentsList(Resource):
    @payments_ns.doc('create_payment')
    @payments_ns.expect(payment_request)
    @payments_ns.marshal_with(payment_model, code=200)
    @payments_ns.response(400, 'Payment failed', error_model)
    def post(self):
        """
        💳 **Process a payment**
        
        सभी Indian payment methods support:
        
        **UPI Payments:**
        - PhonePe: user@ybl
        - Paytm: user@paytm  
        - Google Pay: user@okhdfcbank
        - BHIM: user@upi
        
        **Card Payments:**
        - All major Indian banks
        - International cards accepted
        - EMI options available
        
        **NetBanking:**
        - 50+ Indian banks
        - Real-time processing
        
        **Wallets:**
        - Paytm, PhonePe, MobiKwik
        - Instant processing
        
        **Example UPI Payment:**
        ```json
        {
            "amount": 25000,
            "currency": "INR",
            "method": "upi",
            "upi": {
                "vpa": "rahul@paytm",
                "flow": "collect"
            },
            "description": "Mumbai Vada Pav Corner payment"
        }
        ```
        """
        data = request.get_json()
        
        # Basic validation
        if not data.get('amount') or data['amount'] < 100:
            return {'error': {
                'code': 'BAD_REQUEST_ERROR',
                'description': 'Minimum amount ₹1 (100 paise)'
            }}, 400
        
        if not data.get('method'):
            return {'error': {
                'code': 'BAD_REQUEST_ERROR', 
                'description': 'Payment method required'
            }}, 400
        
        payment_id = f"pay_{uuid.uuid4().hex[:8]}"
        method = data['method']
        
        # Mock payment processing based on method
        payment = {
            'id': payment_id,
            'entity': 'payment',
            'amount': data['amount'],
            'currency': data.get('currency', 'INR'),
            'status': 'captured',  # Mock successful payment
            'order_id': data.get('order_id'),
            'method': method,
            'amount_refunded': 0,
            'refund_status': None,
            'captured': True,
            'description': data.get('description'),
            'international': False,
            'fee': int(data['amount'] * 0.02),  # 2% fee
            'tax': int(data['amount'] * 0.02 * 0.18),  # 18% GST on fee
            'created_at': int(datetime.now().timestamp())
        }
        
        # Add method-specific details
        if method == 'upi':
            upi_data = data.get('upi', {})
            payment['vpa'] = upi_data.get('vpa')
            payment['bank'] = 'HDFC'  # Mock bank
        elif method == 'card':
            card_data = data.get('card', {})
            payment['card_id'] = f"card_{uuid.uuid4().hex[:8]}"
            payment['bank'] = 'HDFC'
        elif method == 'netbanking':
            nb_data = data.get('netbanking', {})
            payment['bank'] = nb_data.get('bank', 'HDFC')
        elif method == 'wallet':
            wallet_data = data.get('wallet', {})
            payment['wallet'] = wallet_data.get('wallet', 'paytm')
        
        # Add customer details if provided
        customer = data.get('customer', {})
        if customer:
            payment['email'] = customer.get('email')
            payment['contact'] = customer.get('contact')
        
        payments_db[payment_id] = payment
        
        # Update order if order_id provided
        order_id = data.get('order_id')
        if order_id and order_id in orders_db:
            orders_db[order_id]['amount_paid'] = data['amount']
            orders_db[order_id]['amount_due'] = 0
            orders_db[order_id]['status'] = 'paid'
            orders_db[order_id]['attempts'] += 1
        
        return payment

@payments_ns.route('/<string:payment_id>')
class Payment(Resource):
    @payments_ns.doc('get_payment')
    @payments_ns.marshal_with(payment_model)
    @payments_ns.response(404, 'Payment not found', error_model)
    def get(self, payment_id):
        """
        🔍 **Get payment details**
        
        Payment की complete details fetch करें
        """
        if payment_id not in payments_db:
            return {'error': {
                'code': 'BAD_REQUEST_ERROR',
                'description': f'Payment {payment_id} नहीं मिला'
            }}, 404
        
        return payments_db[payment_id]

@payments_ns.route('/<string:payment_id>/capture')
class PaymentCapture(Resource):
    @payments_ns.doc('capture_payment')
    @payments_ns.marshal_with(payment_model)
    def post(self, payment_id):
        """
        ✅ **Capture authorized payment**
        
        Auto-capture disabled payments को manually capture करें
        """
        if payment_id not in payments_db:
            return {'error': {'description': 'Payment not found'}}, 404
        
        payment = payments_db[payment_id]
        payment['status'] = 'captured'
        payment['captured'] = True
        
        return payment

# Customers API
@customers_ns.route('')
class CustomersList(Resource):
    @customers_ns.doc('create_customer')
    @customers_ns.expect(customer_model)
    @customers_ns.marshal_with(customer_model, code=201)
    def post(self):
        """
        👥 **Create a new customer**
        
        Customer profile बनाएं recurring payments के लिए
        """
        data = request.get_json()
        
        customer_id = f"cust_{uuid.uuid4().hex[:8]}"
        customer = {
            'id': customer_id,
            'entity': 'customer',
            'name': data.get('name'),
            'email': data.get('email'),
            'contact': data.get('contact'),
            'gstin': data.get('gstin'),
            'notes': data.get('notes', {}),
            'created_at': int(datetime.now().timestamp())
        }
        
        customers_db[customer_id] = customer
        return customer, 201

# Webhooks API
@webhooks_ns.route('/payment.authorized')
class PaymentAuthorizedWebhook(Resource):
    @webhooks_ns.doc('payment_authorized_webhook')
    def post(self):
        """
        🔔 **Payment Authorized Webhook**
        
        जब payment authorize हो जाए तो यह webhook trigger होता है
        
        **Webhook Headers:**
        ```
        X-Razorpay-Event-Id: evt_12345
        X-Razorpay-Signature: signature_value
        ```
        
        **Payload:**
        ```json
        {
            "entity": "event",
            "account_id": "acc_12345",
            "event": "payment.authorized",
            "contains": ["payment"],
            "payload": {
                "payment": {
                    "entity": "payment",
                    "id": "pay_12345",
                    "status": "authorized"
                }
            },
            "created_at": 1642771200
        }
        ```
        """
        return {'message': 'Webhook received'}, 200

@webhooks_ns.route('/payment.captured')
class PaymentCapturedWebhook(Resource):
    @webhooks_ns.doc('payment_captured_webhook')
    def post(self):
        """
        🔔 **Payment Captured Webhook**
        
        Payment capture होने पर trigger होता है
        """
        return {'message': 'Webhook received'}, 200

@webhooks_ns.route('/payment.failed')
class PaymentFailedWebhook(Resource):
    @webhooks_ns.doc('payment_failed_webhook')  
    def post(self):
        """
        🔔 **Payment Failed Webhook**
        
        Payment fail होने पर trigger होता है
        """
        return {'message': 'Webhook received'}, 200

# Add authentication to API documentation
authorizations = {
    'API Key': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'API Key in format: "Basic base64(key_id:key_secret)"'
    }
}

api.authorizations = authorizations

if __name__ == '__main__':
    print("💳 Razorpay Payment Gateway API with OpenAPI Documentation")
    print("📚 Interactive documentation available at: http://localhost:8002/docs/")
    print("🇮🇳 Supporting all Indian payment methods:")
    print("   - UPI (PhonePe, Paytm, Google Pay)")
    print("   - Cards (Debit, Credit, Corporate)")
    print("   - NetBanking (50+ banks)")
    print("   - Wallets (Paytm, PhonePe, etc.)")
    print("   - EMI options")
    print("\n🏗️ OpenAPI 3.0 features:")
    print("   - Interactive API testing")
    print("   - Auto-generated client SDKs")
    print("   - Comprehensive schemas")
    print("   - Webhook documentation")
    print("   - Mumbai-style examples")
    
    app.run(host='0.0.0.0', port=8002, debug=True)
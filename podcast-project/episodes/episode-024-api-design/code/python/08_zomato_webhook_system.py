#!/usr/bin/env python3
"""
Zomato Order Update Webhook System
जोमैटो style real-time order updates के लिए webhook implementation

Webhook Use Cases:
- Order status updates (placed → preparing → delivered)
- Payment confirmations  
- Restaurant acceptance/rejection
- Delivery partner assignment
- Real-time notifications to customers

Features:
- Webhook signature verification
- Retry mechanism with exponential backoff
- Dead letter queue for failed webhooks
- Event filtering and routing
- Mumbai restaurant integration

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 24 - API Design Patterns (Webhook Implementation)
"""

from flask import Flask, request, jsonify
import requests
import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import uuid
import threading
from queue import Queue, PriorityQueue
import sqlite3
from dataclasses import dataclass
from enum import Enum

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Webhook configuration
WEBHOOK_SECRET = "zomato_webhook_secret_mumbai_2025"
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAYS = [1, 5, 15]  # seconds
WEBHOOK_TIMEOUT = 10  # seconds

# Event types
class EventType(Enum):
    ORDER_PLACED = "order.placed"
    ORDER_CONFIRMED = "order.confirmed"
    ORDER_PREPARING = "order.preparing"
    ORDER_READY = "order.ready"
    ORDER_PICKED_UP = "order.picked_up"
    ORDER_DELIVERED = "order.delivered"
    ORDER_CANCELLED = "order.cancelled"
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"

@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration"""
    id: str
    url: str
    events: List[str]  # Event types to subscribe
    secret: str
    active: bool = True
    retry_count: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None

@dataclass
class WebhookEvent:
    """Webhook event data"""
    event_id: str
    event_type: str
    timestamp: datetime
    data: Dict
    attempts: int = 0
    next_retry: Optional[datetime] = None

# In-memory storage (Production में यह Redis/PostgreSQL होगा)
webhook_endpoints = {}
pending_webhooks = PriorityQueue()
failed_webhooks = Queue()

# Mumbai restaurants और उनके webhook endpoints
RESTAURANT_WEBHOOKS = {
    "rest_mumbai_vadapav": WebhookEndpoint(
        id="rest_mumbai_vadapav",
        url="https://mumbai-vadapav-corner.com/webhooks/zomato",
        events=[EventType.ORDER_PLACED.value, EventType.ORDER_CONFIRMED.value, 
               EventType.ORDER_CANCELLED.value],
        secret="vadapav_secret_123"
    ),
    "rest_delhi_chawal": WebhookEndpoint(
        id="rest_delhi_chawal",
        url="https://delhi-chawal-wala.com/api/webhooks",
        events=[EventType.ORDER_PLACED.value, EventType.ORDER_PREPARING.value,
               EventType.ORDER_READY.value],
        secret="chawal_secret_456"
    ),
    "rest_bangalore_dosa": WebhookEndpoint(
        id="rest_bangalore_dosa",
        url="https://bangalore-dosa-corner.in/webhook-handler",
        events=[EventType.ORDER_PLACED.value, EventType.ORDER_DELIVERED.value],
        secret="dosa_secret_789"
    )
}

# Customer notification endpoints
CUSTOMER_WEBHOOKS = {
    "customer_app": WebhookEndpoint(
        id="customer_app",
        url="https://zomato-customer-app.com/webhooks/order-updates",
        events=[EventType.ORDER_CONFIRMED.value, EventType.ORDER_PREPARING.value,
               EventType.ORDER_READY.value, EventType.ORDER_DELIVERED.value],
        secret="customer_app_secret"
    ),
    "sms_service": WebhookEndpoint(
        id="sms_service", 
        url="https://sms-gateway.zomato.com/send-update",
        events=[EventType.ORDER_CONFIRMED.value, EventType.ORDER_DELIVERED.value,
               EventType.ORDER_CANCELLED.value],
        secret="sms_secret"
    )
}

# Mock orders database
ORDERS_DB = {
    "order_mumbai_001": {
        "order_id": "order_mumbai_001",
        "customer_name": "Rahul Sharma",
        "customer_phone": "+91-9876543210",
        "restaurant_id": "rest_mumbai_vadapav", 
        "restaurant_name": "Mumbai Vada Pav Corner",
        "items": [
            {"name": "Vada Pav", "quantity": 2, "price": 40},
            {"name": "Misal Pav", "quantity": 1, "price": 80}
        ],
        "total_amount": 160.00,
        "status": "placed",
        "delivery_address": "A-101 Mumbai Heights, Andheri East",
        "estimated_delivery": "45 mins",
        "created_at": datetime.now().isoformat()
    }
}

def generate_webhook_signature(payload: str, secret: str) -> str:
    """
    Webhook signature generate करता है security के लिए
    HMAC-SHA256 based signature जैसे GitHub/Stripe करते हैं
    """
    signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """
    Incoming webhook signature verify करता है
    """
    expected_signature = generate_webhook_signature(payload, secret)
    return hmac.compare_digest(expected_signature, signature)

def create_webhook_event(event_type: str, order_data: Dict) -> WebhookEvent:
    """
    Webhook event create करता है
    """
    event = WebhookEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type=event_type,
        timestamp=datetime.now(),
        data={
            "event_type": event_type,
            "order": order_data,
            "zomato_metadata": {
                "city": "Mumbai",
                "zone": "Western Suburbs",
                "delivery_time": "45 mins"
            }
        }
    )
    return event

def send_webhook(endpoint: WebhookEndpoint, event: WebhookEvent) -> bool:
    """
    Individual webhook send करता है
    """
    try:
        payload = json.dumps({
            "event_id": event.event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data
        })
        
        signature = generate_webhook_signature(payload, endpoint.secret)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Zomato-Event-Type': event.event_type,
            'X-Zomato-Event-ID': event.event_id,
            'X-Zomato-Signature': signature,
            'User-Agent': 'Zomato-Webhooks/1.0'
        }
        
        logger.info(f"Sending webhook to {endpoint.url}: {event.event_type}")
        
        # Mock HTTP request (Production में actual HTTP call होगी)
        response = requests.post(
            endpoint.url,
            data=payload,
            headers=headers,
            timeout=WEBHOOK_TIMEOUT
        )
        
        if response.status_code == 200:
            endpoint.last_success = datetime.now()
            logger.info(f"Webhook delivered successfully to {endpoint.id}")
            return True
        else:
            logger.error(f"Webhook failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook request failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Webhook send error: {str(e)}")
        return False

def dispatch_webhook_event(event: WebhookEvent):
    """
    Webhook event को सभी subscribed endpoints पे dispatch करता है
    """
    # Restaurant webhooks
    for endpoint in RESTAURANT_WEBHOOKS.values():
        if endpoint.active and event.event_type in endpoint.events:
            success = send_webhook(endpoint, event)
            if not success:
                # Add to retry queue
                event.attempts += 1
                if event.attempts < MAX_RETRY_ATTEMPTS:
                    event.next_retry = datetime.now() + timedelta(
                        seconds=RETRY_DELAYS[min(event.attempts-1, len(RETRY_DELAYS)-1)]
                    )
                    pending_webhooks.put((event.next_retry.timestamp(), event))
                else:
                    # Move to dead letter queue
                    failed_webhooks.put((endpoint.id, event))
    
    # Customer webhooks  
    for endpoint in CUSTOMER_WEBHOOKS.values():
        if endpoint.active and event.event_type in endpoint.events:
            success = send_webhook(endpoint, event)
            if not success and event.attempts < MAX_RETRY_ATTEMPTS:
                # Retry logic for customer notifications
                event.attempts += 1
                event.next_retry = datetime.now() + timedelta(seconds=RETRY_DELAYS[0])
                pending_webhooks.put((event.next_retry.timestamp(), event))

def webhook_retry_worker():
    """
    Background worker for webhook retries
    """
    while True:
        try:
            if not pending_webhooks.empty():
                retry_time, event = pending_webhooks.get()
                
                if datetime.now().timestamp() >= retry_time:
                    logger.info(f"Retrying webhook: {event.event_id} (attempt {event.attempts})")
                    dispatch_webhook_event(event)
                else:
                    # Put back in queue if not time yet
                    pending_webhooks.put((retry_time, event))
            
            time.sleep(1)  # Check every second
            
        except Exception as e:
            logger.error(f"Webhook retry worker error: {str(e)}")
            time.sleep(5)

# Start background worker thread
retry_thread = threading.Thread(target=webhook_retry_worker, daemon=True)
retry_thread.start()

# API endpoints

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """
    Order status update - यहाँ से webhook events trigger होते हैं
    """
    try:
        data = request.get_json()
        new_status = data.get('status')
        updated_by = data.get('updated_by', 'system')  # restaurant, delivery_partner, system
        
        if order_id not in ORDERS_DB:
            return jsonify({"error": "Order not found"}), 404
        
        order = ORDERS_DB[order_id]
        old_status = order['status']
        
        # Update order status
        order['status'] = new_status
        order['updated_at'] = datetime.now().isoformat()
        order['updated_by'] = updated_by
        
        # Map status to event type
        status_to_event = {
            'confirmed': EventType.ORDER_CONFIRMED.value,
            'preparing': EventType.ORDER_PREPARING.value,
            'ready': EventType.ORDER_READY.value,
            'picked_up': EventType.ORDER_PICKED_UP.value,
            'delivered': EventType.ORDER_DELIVERED.value,
            'cancelled': EventType.ORDER_CANCELLED.value
        }
        
        event_type = status_to_event.get(new_status)
        if event_type:
            # Create and dispatch webhook event
            webhook_event = create_webhook_event(event_type, order)
            dispatch_webhook_event(webhook_event)
            
            logger.info(f"Order {order_id} status changed: {old_status} → {new_status}")
        
        return jsonify({
            "success": True,
            "order_id": order_id,
            "old_status": old_status,
            "new_status": new_status,
            "webhook_dispatched": event_type is not None,
            "message": f"Order status updated! Webhook भेज दिया गया है"
        })
        
    except Exception as e:
        logger.error(f"Order status update error: {str(e)}")
        return jsonify({"error": "Status update failed"}), 500

@app.route('/api/webhooks/test', methods=['POST'])
def test_webhook():
    """
    Webhook testing endpoint - Manual webhook trigger के लिए
    """
    try:
        data = request.get_json()
        event_type = data.get('event_type', EventType.ORDER_PLACED.value)
        order_id = data.get('order_id', 'order_mumbai_001')
        
        if order_id not in ORDERS_DB:
            return jsonify({"error": "Order not found"}), 404
        
        order = ORDERS_DB[order_id]
        
        # Create test webhook event
        webhook_event = create_webhook_event(event_type, order)
        dispatch_webhook_event(webhook_event)
        
        return jsonify({
            "success": True,
            "event_id": webhook_event.event_id,
            "event_type": event_type,
            "order_id": order_id,
            "message": f"Test webhook dispatched! Event: {event_type}"
        })
        
    except Exception as e:
        logger.error(f"Test webhook error: {str(e)}")
        return jsonify({"error": "Test webhook failed"}), 500

@app.route('/webhooks/restaurant/<restaurant_id>', methods=['POST'])
def receive_restaurant_webhook(restaurant_id):
    """
    Restaurant webhook receiver - Restaurant से updates receive करने के लिए
    """
    try:
        # Verify signature
        payload = request.get_data(as_text=True)
        signature = request.headers.get('X-Restaurant-Signature', '')
        
        restaurant_secret = f"{restaurant_id}_secret"  # Get from database
        
        if not verify_webhook_signature(payload, signature, restaurant_secret):
            return jsonify({"error": "Invalid signature"}), 401
        
        data = request.get_json()
        event_type = data.get('event_type')
        order_id = data.get('order_id')
        
        logger.info(f"Restaurant webhook received: {restaurant_id} - {event_type}")
        
        # Process restaurant update
        if event_type == 'order.accepted':
            # Update order status and trigger customer notification
            if order_id in ORDERS_DB:
                ORDERS_DB[order_id]['status'] = 'confirmed'
                ORDERS_DB[order_id]['confirmed_by_restaurant'] = datetime.now().isoformat()
                
                # Send customer notification
                customer_event = create_webhook_event(
                    EventType.ORDER_CONFIRMED.value,
                    ORDERS_DB[order_id]
                )
                dispatch_webhook_event(customer_event)
        
        return jsonify({
            "success": True,
            "message": "Restaurant webhook processed successfully"
        })
        
    except Exception as e:
        logger.error(f"Restaurant webhook error: {str(e)}")
        return jsonify({"error": "Webhook processing failed"}), 500

@app.route('/api/webhooks/endpoints', methods=['GET'])
def list_webhook_endpoints():
    """
    Webhook endpoints list करता है - Debugging के लिए
    """
    all_endpoints = {}
    all_endpoints.update(RESTAURANT_WEBHOOKS)
    all_endpoints.update(CUSTOMER_WEBHOOKS)
    
    endpoints_info = {}
    for endpoint_id, endpoint in all_endpoints.items():
        endpoints_info[endpoint_id] = {
            "id": endpoint.id,
            "url": endpoint.url,
            "events": endpoint.events,
            "active": endpoint.active,
            "last_success": endpoint.last_success.isoformat() if endpoint.last_success else None,
            "last_failure": endpoint.last_failure.isoformat() if endpoint.last_failure else None
        }
    
    return jsonify({
        "total_endpoints": len(endpoints_info),
        "endpoints": endpoints_info,
        "pending_retries": pending_webhooks.qsize(),
        "failed_webhooks": failed_webhooks.qsize()
    })

@app.route('/api/webhooks/failed', methods=['GET'])
def get_failed_webhooks():
    """
    Failed webhooks list करता है - Dead letter queue
    """
    failed_list = []
    
    # Get all failed webhooks (non-destructive peek)
    temp_queue = Queue()
    while not failed_webhooks.empty():
        failed_item = failed_webhooks.get()
        failed_list.append({
            "endpoint_id": failed_item[0],
            "event_id": failed_item[1].event_id,
            "event_type": failed_item[1].event_type,
            "attempts": failed_item[1].attempts,
            "timestamp": failed_item[1].timestamp.isoformat()
        })
        temp_queue.put(failed_item)
    
    # Put items back
    while not temp_queue.empty():
        failed_webhooks.put(temp_queue.get())
    
    return jsonify({
        "failed_webhooks": failed_list,
        "total_failed": len(failed_list),
        "message": "یہ webhooks fail ho gaye hain - Manual intervention required"
    })

@app.route('/api/orders', methods=['GET'])
def list_orders():
    """
    Orders list - Current orders status देखने के लिए
    """
    return jsonify({
        "orders": list(ORDERS_DB.values()),
        "total_orders": len(ORDERS_DB)
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check with webhook system status"""
    return jsonify({
        "status": "healthy",
        "service": "Zomato Webhook System",
        "features": [
            "Real-time order updates",
            "Webhook signature verification",
            "Retry mechanism with exponential backoff", 
            "Dead letter queue for failed deliveries",
            "Multi-endpoint event dispatch",
            "Restaurant and customer notifications"
        ],
        "statistics": {
            "active_endpoints": len(RESTAURANT_WEBHOOKS) + len(CUSTOMER_WEBHOOKS),
            "pending_retries": pending_webhooks.qsize(),
            "failed_webhooks": failed_webhooks.qsize(),
            "supported_events": [e.value for e in EventType]
        },
        "message": "Zomato webhook system ready! Mumbai से Delhi tak real-time updates 🚀"
    })

if __name__ == '__main__':
    print("🍕 Zomato Webhook System starting...")
    print("📡 Real-time order update system:")
    print("   - Restaurant status updates")
    print("   - Customer notifications")  
    print("   - Delivery partner tracking")
    print("   - Payment confirmations")
    print("\n🔒 Security features:")
    print("   - HMAC-SHA256 signature verification")
    print("   - Event type filtering")
    print("   - Retry mechanism")
    print("   - Dead letter queue")
    print("\n🏪 Mumbai restaurants integrated:")
    print("   - Vada Pav Corner")
    print("   - Delhi Chawal Wala") 
    print("   - Bangalore Dosa Corner")
    
    app.run(host='0.0.0.0', port=8003, debug=True)
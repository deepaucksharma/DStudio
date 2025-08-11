"""
Flipkart Order Processing Multi-Step Workflow
Episode 12: E-commerce Order Orchestration

यह DAG Flipkart जैसे e-commerce platform का order processing workflow है
हर मिनट नए orders check करता है और process करता है
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
import json
import random

default_args = {
    'owner': 'flipkart-ops-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'email': ['ops@flipkart.com', 'alerts@flipkart.com']
}

dag = DAG(
    dag_id='flipkart_order_processing_workflow',
    default_args=default_args,
    description='Flipkart Order Processing - Complete E-commerce Flow',
    schedule_interval=timedelta(minutes=5),  # हर 5 मिनट check करेगा
    catchup=False,
    max_active_runs=3,  # 3 parallel runs allowed
    tags=['flipkart', 'ecommerce', 'order-processing'],
)

def fetch_new_orders():
    """नए orders को database से fetch करना"""
    print("🛒 Fetching new orders from Flipkart database...")
    
    # Mock orders data - real में database query होगी
    new_orders = [
        {
            'order_id': 'FLP2025001001',
            'customer_id': 'CUST123456',
            'customer_name': 'राज पटेल',
            'items': [
                {'product_id': 'MOB001', 'name': 'iPhone 15', 'price': 79900, 'qty': 1},
                {'product_id': 'ACC001', 'name': 'Phone Cover', 'price': 299, 'qty': 1}
            ],
            'total_amount': 80199,
            'payment_method': 'UPI',
            'delivery_address': 'Mumbai, Maharashtra',
            'order_time': datetime.now().isoformat(),
            'order_type': 'regular'  # regular, priority, bulk
        },
        {
            'order_id': 'FLP2025001002', 
            'customer_id': 'CUST789012',
            'customer_name': 'प्रिया शर्मा',
            'items': [
                {'product_id': 'FASH001', 'name': 'Kurta Set', 'price': 1299, 'qty': 2}
            ],
            'total_amount': 2598,
            'payment_method': 'COD',
            'delivery_address': 'Delhi, India',
            'order_time': datetime.now().isoformat(),
            'order_type': 'priority'
        }
    ]
    
    print(f"✅ Found {len(new_orders)} new orders")
    for order in new_orders:
        print(f"📦 Order: {order['order_id']} - ₹{order['total_amount']} - {order['customer_name']}")
    
    # Orders को Variable में store करना
    Variable.set("pending_orders", json.dumps(new_orders))
    return len(new_orders)

def validate_orders():
    """Orders की validation करना"""
    print("✅ Order Validation Process शुरू...")
    
    orders = json.loads(Variable.get("pending_orders", "[]"))
    valid_orders = []
    invalid_orders = []
    
    for order in orders:
        # Validation checks
        issues = []
        
        # Amount validation
        calculated_total = sum(item['price'] * item['qty'] for item in order['items'])
        if calculated_total != order['total_amount']:
            issues.append(f"Amount mismatch: calculated {calculated_total}, order total {order['total_amount']}")
        
        # Address validation
        if not order['delivery_address'] or len(order['delivery_address']) < 10:
            issues.append("Invalid delivery address")
        
        # Payment validation
        if order['payment_method'] not in ['UPI', 'Credit Card', 'Debit Card', 'COD', 'Net Banking']:
            issues.append(f"Invalid payment method: {order['payment_method']}")
        
        # Items validation
        if not order['items'] or len(order['items']) == 0:
            issues.append("No items in order")
        
        if issues:
            order['validation_issues'] = issues
            invalid_orders.append(order)
            print(f"❌ Invalid Order {order['order_id']}: {', '.join(issues)}")
        else:
            valid_orders.append(order)
            print(f"✅ Valid Order {order['order_id']}")
    
    Variable.set("valid_orders", json.dumps(valid_orders))
    Variable.set("invalid_orders", json.dumps(invalid_orders))
    
    print(f"📊 Validation Summary: {len(valid_orders)} valid, {len(invalid_orders)} invalid")
    return len(valid_orders)

def check_inventory():
    """Inventory availability check करना"""
    print("📦 Inventory Availability Check...")
    
    valid_orders = json.loads(Variable.get("valid_orders", "[]"))
    
    # Mock inventory data
    inventory = {
        'MOB001': {'available': 50, 'reserved': 5, 'warehouse': 'Mumbai'},
        'ACC001': {'available': 100, 'reserved': 10, 'warehouse': 'Mumbai'}, 
        'FASH001': {'available': 25, 'reserved': 3, 'warehouse': 'Delhi'}
    }
    
    orders_with_inventory = []
    out_of_stock_orders = []
    
    for order in valid_orders:
        inventory_available = True
        unavailable_items = []
        
        for item in order['items']:
            product_id = item['product_id']
            required_qty = item['qty']
            
            if product_id in inventory:
                available = inventory[product_id]['available'] - inventory[product_id]['reserved']
                if available < required_qty:
                    inventory_available = False
                    unavailable_items.append({
                        'product_id': product_id,
                        'required': required_qty,
                        'available': available
                    })
                else:
                    # Reserve inventory
                    inventory[product_id]['reserved'] += required_qty
            else:
                inventory_available = False
                unavailable_items.append({
                    'product_id': product_id,
                    'required': required_qty,
                    'available': 0
                })
        
        if inventory_available:
            orders_with_inventory.append(order)
            print(f"✅ Inventory OK for order {order['order_id']}")
        else:
            order['unavailable_items'] = unavailable_items
            out_of_stock_orders.append(order)
            print(f"❌ Inventory shortage for order {order['order_id']}")
    
    Variable.set("confirmed_orders", json.dumps(orders_with_inventory))
    Variable.set("inventory_shortage_orders", json.dumps(out_of_stock_orders))
    
    return len(orders_with_inventory)

def payment_processing():
    """Payment processing और verification"""
    print("💳 Payment Processing शुरू...")
    
    confirmed_orders = json.loads(Variable.get("confirmed_orders", "[]"))
    successful_payments = []
    failed_payments = []
    
    for order in confirmed_orders:
        payment_method = order['payment_method']
        amount = order['total_amount']
        
        print(f"💰 Processing payment for Order {order['order_id']} - ₹{amount} via {payment_method}")
        
        # Mock payment processing
        if payment_method == 'COD':
            # COD orders always succeed initially
            payment_success = True
            transaction_id = f"COD_{order['order_id']}"
        else:
            # Digital payments - 95% success rate
            payment_success = random.random() > 0.05
            transaction_id = f"TXN_{random.randint(100000, 999999)}" if payment_success else None
        
        if payment_success:
            order['transaction_id'] = transaction_id
            order['payment_status'] = 'SUCCESS'
            successful_payments.append(order)
            print(f"✅ Payment successful: {transaction_id}")
        else:
            order['payment_status'] = 'FAILED'
            order['failure_reason'] = 'Bank declined / Insufficient funds'
            failed_payments.append(order)
            print(f"❌ Payment failed for order {order['order_id']}")
    
    Variable.set("paid_orders", json.dumps(successful_payments))
    Variable.set("payment_failed_orders", json.dumps(failed_payments))
    
    return len(successful_payments)

def decide_fulfillment_route():
    """Order को कहाँ भेजना है - यह decide करना"""
    paid_orders = json.loads(Variable.get("paid_orders", "[]"))
    
    if not paid_orders:
        print("कोई paid orders नहीं मिले!")
        return 'no_orders_to_process'
    
    # Order types के basis पर routing
    regular_orders = [o for o in paid_orders if o.get('order_type') == 'regular']
    priority_orders = [o for o in paid_orders if o.get('order_type') == 'priority']
    bulk_orders = [o for o in paid_orders if o.get('order_type') == 'bulk']
    
    print(f"📊 Order Distribution: Regular={len(regular_orders)}, Priority={len(priority_orders)}, Bulk={len(bulk_orders)}")
    
    if priority_orders:
        Variable.set("processing_orders", json.dumps(priority_orders))
        return 'priority_fulfillment'
    elif bulk_orders:
        Variable.set("processing_orders", json.dumps(bulk_orders))
        return 'bulk_fulfillment'
    else:
        Variable.set("processing_orders", json.dumps(regular_orders))
        return 'regular_fulfillment'

def regular_fulfillment():
    """Regular orders की fulfillment"""
    print("📦 Regular Fulfillment Process...")
    processing_orders = json.loads(Variable.get("processing_orders", "[]"))
    
    for order in processing_orders:
        print(f"🚚 Processing regular order {order['order_id']}")
        print(f"📍 Delivery to: {order['delivery_address']}")
        print(f"⏰ Expected delivery: 3-5 business days")
    
    # Order status update
    for order in processing_orders:
        order['fulfillment_status'] = 'IN_PROGRESS'
        order['expected_delivery'] = (datetime.now() + timedelta(days=4)).isoformat()
    
    Variable.set("fulfilled_orders", json.dumps(processing_orders))
    return f"Regular fulfillment completed for {len(processing_orders)} orders"

def priority_fulfillment():
    """Priority/Express orders की fulfillment"""
    print("🚀 Priority Fulfillment Process...")
    processing_orders = json.loads(Variable.get("processing_orders", "[]"))
    
    for order in processing_orders:
        print(f"⚡ Processing priority order {order['order_id']}")
        print(f"📍 Express delivery to: {order['delivery_address']}")
        print(f"⏰ Expected delivery: Next day delivery")
    
    # Faster processing
    for order in processing_orders:
        order['fulfillment_status'] = 'EXPEDITED'
        order['expected_delivery'] = (datetime.now() + timedelta(days=1)).isoformat()
        order['delivery_partner'] = 'Flipkart Express'
    
    Variable.set("fulfilled_orders", json.dumps(processing_orders))
    return f"Priority fulfillment completed for {len(processing_orders)} orders"

def bulk_fulfillment():
    """Bulk orders की fulfillment"""
    print("📦📦📦 Bulk Fulfillment Process...")
    processing_orders = json.loads(Variable.get("processing_orders", "[]"))
    
    for order in processing_orders:
        print(f"🏭 Processing bulk order {order['order_id']}")
        print(f"📦 Large quantity shipment")
        
    # Special bulk processing
    for order in processing_orders:
        order['fulfillment_status'] = 'BULK_PROCESSING'
        order['expected_delivery'] = (datetime.now() + timedelta(days=7)).isoformat()
        order['special_handling'] = 'Bulk shipment - consolidated delivery'
    
    Variable.set("fulfilled_orders", json.dumps(processing_orders))
    return f"Bulk fulfillment completed for {len(processing_orders)} orders"

def send_customer_notifications():
    """Customers को notifications भेजना"""
    print("📧 Customer Notifications...")
    fulfilled_orders = json.loads(Variable.get("fulfilled_orders", "[]"))
    
    for order in fulfilled_orders:
        customer_name = order['customer_name']
        order_id = order['order_id']
        expected_delivery = order.get('expected_delivery', 'Soon')
        
        # Mock SMS/Email/Push notification
        notification_message = f"""
        नमस्ते {customer_name}! 
        
        आपका Flipkart order confirm हो गया! 🎉
        Order ID: {order_id}
        Expected Delivery: {expected_delivery}
        
        Track your order: flipkart.com/track/{order_id}
        
        Happy Shopping! 🛒
        """
        
        print(f"📱 Notification sent to {customer_name}")
        print(f"Message: {notification_message.strip()}")
    
    return f"Notifications sent for {len(fulfilled_orders)} orders"

# Task definitions
fetch_orders_task = PythonOperator(
    task_id='fetch_new_orders',
    python_callable=fetch_new_orders,
    dag=dag
)

validate_orders_task = PythonOperator(
    task_id='validate_orders', 
    python_callable=validate_orders,
    dag=dag
)

inventory_check_task = PythonOperator(
    task_id='check_inventory',
    python_callable=check_inventory,
    dag=dag
)

payment_processing_task = PythonOperator(
    task_id='payment_processing',
    python_callable=payment_processing,
    dag=dag
)

# Branching operator - routing decision
fulfillment_router = BranchPythonOperator(
    task_id='decide_fulfillment_route',
    python_callable=decide_fulfillment_route,
    dag=dag
)

# Different fulfillment paths
regular_fulfillment_task = PythonOperator(
    task_id='regular_fulfillment',
    python_callable=regular_fulfillment,
    dag=dag
)

priority_fulfillment_task = PythonOperator(
    task_id='priority_fulfillment', 
    python_callable=priority_fulfillment,
    dag=dag
)

bulk_fulfillment_task = PythonOperator(
    task_id='bulk_fulfillment',
    python_callable=bulk_fulfillment,
    dag=dag
)

no_orders_task = DummyOperator(
    task_id='no_orders_to_process',
    dag=dag
)

# Join point after branching
fulfillment_complete = DummyOperator(
    task_id='fulfillment_complete',
    trigger_rule='none_failed_or_skipped',  # Join after branching
    dag=dag
)

notifications_task = PythonOperator(
    task_id='send_customer_notifications',
    python_callable=send_customer_notifications,
    dag=dag
)

# Task Dependencies
fetch_orders_task >> validate_orders_task >> inventory_check_task >> payment_processing_task
payment_processing_task >> fulfillment_router

# Branching paths
fulfillment_router >> [regular_fulfillment_task, priority_fulfillment_task, bulk_fulfillment_task, no_orders_task]

# Join after branching
[regular_fulfillment_task, priority_fulfillment_task, bulk_fulfillment_task, no_orders_task] >> fulfillment_complete

# Final notification
fulfillment_complete >> notifications_task

"""
Real-world Production Considerations:

1. Database Integration:
   - Replace mock data with actual DB queries
   - Use connection pooling
   - Implement proper transactions

2. External APIs:
   - Payment gateway integration (Razorpay, Paytm)
   - SMS gateway (Twilio, MSG91)
   - Email service (SendGrid, SES)
   - Logistics APIs (Delhivery, Blue Dart)

3. Error Handling:
   - Dead letter queues for failed orders
   - Retry mechanisms with exponential backoff
   - Circuit breakers for external services

4. Monitoring:
   - Order processing metrics
   - Success/failure rates
   - Processing time monitoring
   - Alert on unusual patterns

5. Scalability:
   - Horizontal scaling with multiple workers
   - Queue-based processing (RabbitMQ, Apache Kafka)
   - Microservices architecture
   - Database sharding

6. Security:
   - Data encryption at rest and in transit
   - PCI compliance for payment data
   - Access control and audit logging

यह workflow production में millions of orders process करती है daily!
"""
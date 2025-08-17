# Episode 096: Event Streaming Architectures - Real-time Data Flow Ka Mumbai Connection

## Introduction: Mumbai Ki Dabbawala System Aur Event Streaming

Dosto, aaj main aapko le chalega ek bahut hi interesting journey pe. Imagine karo Mumbai ki famous dabbawala system - har din 2 lakh tiffin boxes, zero central database, no WhatsApp groups, phir bhi 99.999% accuracy rate. Kaise possible hai ye? Answer hai event streaming architecture mein!

Mumbai mein jab ek housewife apna dabba ready karta hai Andheri mein, aur wo dabba exactly 12:30 PM pe Nariman Point ke office mein pahunchta hai, toh ye magic nahi hai - ye pure event-driven architecture hai. Har step pe ek event generate hota hai, har dabbawala ek consumer hai, aur entire system ek massive real-time stream processing engine ki tarah kaam karta hai.

Aaj ke digital world mein, companies like Swiggy, Zomato, Flipkart, aur Zerodha exactly yahi pattern use karte hain. Jab aap Swiggy pe order place karte ho, toh thousands of events fire hote hain real-time mein - order placed, restaurant notified, delivery partner assigned, payment processed, ETA calculated. Har event ek message hai jo different services ko trigger karta hai.

### Event Streaming Kya Hai Actually?

Event streaming matlab continuous flow of data events jo real-time mein process hote rahte hain. Traditional request-response model mein aap pizza order karte ho aur wait karte ho response ke liye. But event streaming mein, jaise hi aap order place karte ho, immediately multiple events trigger ho jaate hain parallel mein:

```python
# Traditional Request-Response (Synchronous)
def place_order_traditional(order):
    # Step by step execution
    validate_order(order)           # Wait for validation
    charge_payment(order.amount)    # Wait for payment
    notify_restaurant(order)        # Wait for restaurant
    assign_delivery(order)          # Wait for assignment
    return order_confirmation       # Finally return

# Event Streaming (Asynchronous)
def place_order_event_stream(order):
    # Immediate events fired
    event_bus.publish('ORDER_PLACED', order)
    # No waiting - multiple services react independently
    return order_id  # Immediate response
```

Mumbai dabbawalas mein ye exactly same pattern hai. Jab housewife dabba ready kar deti hai, wo immediately signal deti hai pickup wale ko. Pickup wala signal deta hai sorting center ko, sorting center station wale ko, station wala delivery wale ko. Har step pe event generate hota hai aur next person react karta hai.

### Real Numbers Ka Game: Dabbawala System Analytics

Mumbai dabbawala system ke numbers dekhiye:
- Daily deliveries: 2,00,000 tiffins
- Error rate: 1 in 16 million (better than 6 sigma)
- Processing time: 3-4 hours end-to-end
- Zero technology dependency
- Zero central coordination

Modern tech companies ke comparison mein:
- Swiggy: 4 million orders per day
- Error rate: ~2-3% (order issues)
- Processing time: 30-45 minutes
- Technology dependency: 100%
- Central coordination: Heavy

Interesting fact: Dabbawala system ka error rate better hai most tech companies se! Why? Because unka event-driven architecture naturally resilient hai.

### Event Streaming Ki Power: Real Examples

**Flipkart Big Billion Day 2024:**
- Peak traffic: 10 crore users simultaneously
- Events per second: 50 lakh
- Order placement events: Real-time inventory updates
- Payment events: Multiple payment gateway routing
- Delivery events: Dynamic ETA calculations

```python
# Flipkart Event Streaming Architecture (Simplified)
class FlipkartEventStream:
    def __init__(self):
        self.kafka_cluster = KafkaCluster([
            'broker1.flipkart.com:9092',
            'broker2.flipkart.com:9092',
            'broker3.flipkart.com:9092'
        ])
        
    def handle_order_event(self, event):
        """
        Big Billion Day mein har second 1000+ orders
        """
        if event.type == 'ORDER_PLACED':
            # Parallel event publishing
            self.publish_to_inventory(event)      # Update stock
            self.publish_to_payment(event)        # Process payment
            self.publish_to_recommendation(event)  # Update ML models
            self.publish_to_analytics(event)      # Real-time dashboards
            
    def publish_to_inventory(self, event):
        # Real-time stock updates across warehouses
        inventory_event = {
            'product_id': event.product_id,
            'quantity_sold': event.quantity,
            'warehouse_ids': event.warehouse_ids,
            'timestamp': event.timestamp
        }
        self.kafka_cluster.send('inventory-updates', inventory_event)
```

**Zerodha Kite Real-time Trading:**
- Price updates: Every 100 milliseconds
- Order events: Sub-second execution
- P&L calculations: Real-time across crores of positions
- Market data: 5000+ stocks simultaneously

### Event Streaming vs Traditional Architecture

**Traditional Monolithic Approach:**
```python
# Old school way - Everything in sequence
def process_food_order(order):
    # Each step waits for previous one
    user = validate_user(order.user_id)          # 200ms
    restaurant = check_restaurant(order.rest_id)  # 300ms
    payment = process_payment(order.amount)       # 500ms
    delivery = assign_delivery_boy(order)         # 400ms
    
    # Total time: 1.4 seconds
    # If any step fails, entire process fails
    return order_confirmation
```

**Event Streaming Approach:**
```python
# Modern way - Events fire independently
def process_food_order_events(order):
    # Immediate response
    order_id = generate_order_id()
    
    # Fire events simultaneously
    event_bus.publish('USER_VALIDATION_REQUIRED', {
        'order_id': order_id,
        'user_id': order.user_id
    })
    
    event_bus.publish('RESTAURANT_NOTIFICATION', {
        'order_id': order_id,
        'restaurant_id': order.restaurant_id,
        'items': order.items
    })
    
    event_bus.publish('PAYMENT_PROCESSING', {
        'order_id': order_id,
        'amount': order.amount,
        'payment_method': order.payment_method
    })
    
    # Return immediately - 50ms response
    return order_id
```

### Mumbai Mein Event Streaming Examples

**Local Train System:**
Mumbai local trains bhi event-driven hain. Har station pe train arrival ek event hai jo multiple systems ko trigger karta hai:
- Platform display updates
- Announcement systems
- Crowd management alerts
- Next train ETA calculations

**Traffic Signal Coordination:**
Mumbai traffic signals connected hain through events. Ek signal green hone pe next signals ko events send karte hain optimized flow ke liye.

**Monsoon Water Logging System:**
BMC ka flood monitoring system event-driven hai - rainfall sensors, water level sensors, pump stations sabko events connect karte hain.

### Indian Companies Aur Event Streaming

**Paytm Payment Processing:**
- UPI transactions: 100 crore per month
- Each transaction generates 10+ events
- Real-time fraud detection
- Instant settlement notifications

**Ola Ride Matching:**
- Driver location events: Every 5 seconds
- Ride request events: Real-time matching
- ETA calculation events: Dynamic routing
- Surge pricing events: Demand-based calculations

**IRCTC Ticket Booking:**
- Tatkal booking: 1000+ requests per second
- Seat availability events: Real-time updates
- Waiting list events: Position calculations
- Payment events: Multiple gateway handling

### Event Streaming Benefits

1. **Scalability**: Handle millions of events per second
2. **Resilience**: One service down doesn't break others
3. **Real-time**: Immediate response and processing
4. **Flexibility**: Easy to add new consumers
5. **Audit Trail**: Complete history of all events

### Challenges Bhi Hain

1. **Complexity**: Debugging distributed events is tough
2. **Ordering**: Maintaining event sequence across partitions
3. **Exactly-once delivery**: Preventing duplicate processing
4. **Monitoring**: Tracking events across multiple services
5. **Data consistency**: Eventual consistency model

Aaj ke episode mein hum detail mein explore karenge:
- Apache Kafka architecture aur Indian use cases
- Event Sourcing patterns with real code examples
- CQRS implementation for payment systems
- Stream processing with real-time analytics
- Production stories from Swiggy, Flipkart, Hotstar

Ready ho? Chalo shuru karte hain event streaming ki duniya mein!

---

## Part 1: Event Streaming Fundamentals - Dabbawala Se Data Stream Tak

### Chapter 1: Event-Driven Architecture Basics

Dosto, event-driven architecture samajhne ke liye sabse pehle events ko samajhna padega. Event kya hai? Simple terms mein, event ek notification hai ki kuch hua hai. Jaise Mumbai mein traffic signal red se green ho gaya - ye ek event hai. Instantly sab drivers ko pata chal jata hai ki ab move kar sakte hain.

**Event Ki Definition:**
Event ek immutable fact hai - something that happened in the past. Aap isko change nahi kar sakte, sirf react kar sakte hain.

```python
# Event Structure Example
class OrderPlacedEvent:
    def __init__(self, order_id, user_id, items, timestamp, amount):
        self.event_type = "ORDER_PLACED"
        self.order_id = order_id
        self.user_id = user_id
        self.items = items
        self.timestamp = timestamp  # When it happened
        self.amount = amount
        
    def to_dict(self):
        return {
            'event_type': self.event_type,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'items': self.items,
            'timestamp': self.timestamp.isoformat(),
            'amount': self.amount
        }

# Usage in Swiggy-like system
order_event = OrderPlacedEvent(
    order_id="SWG_123456",
    user_id="USER_789",
    items=[
        {"name": "Butter Chicken", "quantity": 2, "price": 350},
        {"name": "Naan", "quantity": 4, "price": 60}
    ],
    timestamp=datetime.now(),
    amount=470
)
```

### Event-Driven Architecture Ke Components

**1. Event Producers (Event Banane Wale):**
Ye wo services hain jo events generate karte hain. Jaise dabbawala system mein housewife ek event producer hai - "Dabba Ready" event generate karti hai.

```python
class FoodOrderProducer:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        
    def place_order(self, order_details):
        # Business logic for order placement
        order = self.validate_and_create_order(order_details)
        
        # Generate event
        event = OrderPlacedEvent(
            order_id=order.id,
            user_id=order.user_id,
            items=order.items,
            timestamp=datetime.now(),
            amount=order.total_amount
        )
        
        # Publish event to stream
        self.event_bus.publish('food-orders', event.to_dict())
        
        return order.id
```

**2. Event Consumers (Event React Karne Wale):**
Ye wo services hain jo events ko consume karte hain aur action lete hain. Dabbawala system mein pickup boy, sorting center, delivery boy sabko events consume karte hain.

```python
class RestaurantNotificationConsumer:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        
    def consume_orders(self):
        for event in self.event_bus.consume('food-orders'):
            if event['event_type'] == 'ORDER_PLACED':
                self.notify_restaurant(event)
                
    def notify_restaurant(self, order_event):
        # Extract restaurant from order items
        restaurant_id = self.get_restaurant_from_items(order_event['items'])
        
        # Send notification
        notification = {
            'order_id': order_event['order_id'],
            'items': order_event['items'],
            'customer_location': self.get_user_location(order_event['user_id']),
            'estimated_prep_time': self.calculate_prep_time(order_event['items'])
        }
        
        self.send_to_restaurant(restaurant_id, notification)
```

**3. Event Bus/Stream (Event Highway):**
Ye main infrastructure hai jo events ko producers se consumers tak pahunchata hai. Mumbai mein local train network ki tarah - sabko connect karta hai.

```python
import json
from kafka import KafkaProducer, KafkaConsumer

class EventBus:
    def __init__(self, bootstrap_servers):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
    def publish(self, topic, event):
        """
        Event publish karna Kafka topic pe
        """
        try:
            future = self.producer.send(topic, event)
            record_metadata = future.get(timeout=10)
            
            print(f"Event published to {topic}:")
            print(f"Topic: {record_metadata.topic}")
            print(f"Partition: {record_metadata.partition}")
            print(f"Offset: {record_metadata.offset}")
            
        except Exception as e:
            print(f"Failed to publish event: {str(e)}")
            
    def consume(self, topic, group_id):
        """
        Event consume karna Kafka topic se
        """
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        for message in consumer:
            yield message.value
```

### Event-Driven vs Request-Response: Mumbai Traffic Example

**Request-Response Model (Traditional):**
Imagine Mumbai traffic mein har car driver ko har intersection pe manually ask karna pade ki aage jane ka permission hai ki nahi. Driver police se puchega, police traffic control room se puchega, phir answer milega. Ye synchronous model hai.

```python
# Synchronous Request-Response
def check_route_permission(driver, route):
    # Driver waits for each response
    intersection1_ok = traffic_police.check_permission(driver, "Bandra")     # 2 sec wait
    intersection2_ok = traffic_control.check_permission(driver, "Worli")     # 3 sec wait  
    intersection3_ok = mumbai_police.check_permission(driver, "Nariman")     # 4 sec wait
    
    # Total wait time: 9 seconds
    if all([intersection1_ok, intersection2_ok, intersection3_ok]):
        return "ALLOWED"
    else:
        return "BLOCKED"
```

**Event-Driven Model (Modern):**
Actual Mumbai traffic system event-driven hai. Traffic signals, cameras, sensors sab events generate karte rahte hain. Google Maps, traffic apps ye events consume karke real-time updates dete hain.

```python
# Event-Driven Traffic System
class TrafficEventSystem:
    def __init__(self):
        self.event_bus = EventBus(['kafka1:9092', 'kafka2:9092'])
        
    def signal_changed(self, intersection, signal_state):
        # Traffic signal event
        event = {
            'event_type': 'SIGNAL_CHANGED',
            'intersection': intersection,
            'signal_state': signal_state,  # RED, GREEN, YELLOW
            'timestamp': datetime.now().isoformat(),
            'traffic_density': self.get_current_density(intersection)
        }
        
        self.event_bus.publish('traffic-signals', event)
        
    def vehicle_detected(self, intersection, vehicle_count):
        # Traffic density event
        event = {
            'event_type': 'TRAFFIC_DENSITY',
            'intersection': intersection,
            'vehicle_count': vehicle_count,
            'timestamp': datetime.now().isoformat()
        }
        
        self.event_bus.publish('traffic-density', event)

# Multiple consumers react to traffic events
class GoogleMapsConsumer:
    def consume_traffic_events(self):
        for event in event_bus.consume('traffic-signals', 'google-maps-group'):
            self.update_route_calculations(event)
            
class UberConsumer:
    def consume_traffic_events(self):
        for event in event_bus.consume('traffic-signals', 'uber-group'):
            self.update_driver_routes(event)
            
class MumbaiPoliceConsumer:
    def consume_traffic_events(self):
        for event in event_bus.consume('traffic-density', 'mumbai-police-group'):
            if event['vehicle_count'] > 100:
                self.deploy_traffic_constable(event['intersection'])
```

### Benefits of Event-Driven Architecture

**1. Loose Coupling:**
Services ek dusre ko directly nahi jaante. Sirf events ke through communicate karte hain. Jaise dabbawala system mein pickup boy ko nahi pata ki final delivery kahan hogi, bas apna part kar deta hai.

**2. Scalability:**
New consumers easily add kar sakte hain bina existing system ko disturb kiye. Jaise Mumbai mein new dabbawala join ho sakta hai system mein.

```python
# Adding new consumer without affecting existing ones
class AnalyticsConsumer:
    """
    Naya consumer add kiya analytics ke liye
    Existing order processing consumers ko koi effect nahi
    """
    def __init__(self):
        self.event_bus = EventBus(['kafka1:9092'])
        
    def consume_order_events(self):
        for event in self.event_bus.consume('food-orders', 'analytics-group'):
            self.track_order_metrics(event)
            self.update_realtime_dashboard(event)
            
    def track_order_metrics(self, event):
        # Real-time analytics
        metrics = {
            'order_count': 1,
            'revenue': event['amount'],
            'timestamp': event['timestamp'],
            'restaurant_id': self.extract_restaurant_id(event)
        }
        
        # Send to analytics database
        self.analytics_db.insert(metrics)
```

**3. Resilience:**
Agar ek service down ho jaye, other services kaam karte rahte hain. Events queue mein store hote rahte hain.

**4. Real-time Processing:**
Events immediately process hote hain, no waiting.

### Event Types aur Patterns

**1. Domain Events:**
Business-related events jo domain experts samajh sakte hain.

```python
# Domain Events Examples
class UserRegisteredEvent:
    def __init__(self, user_id, email, registration_source):
        self.event_type = "USER_REGISTERED"
        self.user_id = user_id
        self.email = email
        self.registration_source = registration_source  # web, mobile, facebook
        self.timestamp = datetime.now()

class PaymentFailedEvent:
    def __init__(self, order_id, user_id, amount, failure_reason):
        self.event_type = "PAYMENT_FAILED"
        self.order_id = order_id
        self.user_id = user_id
        self.amount = amount
        self.failure_reason = failure_reason
        self.timestamp = datetime.now()
```

**2. Integration Events:**
Systems ke beech communication ke liye.

```python
class InventoryUpdatedEvent:
    """
    Flipkart inventory service se other services ko notify karne ke liye
    """
    def __init__(self, product_id, current_stock, warehouse_id):
        self.event_type = "INVENTORY_UPDATED"
        self.product_id = product_id
        self.current_stock = current_stock
        self.warehouse_id = warehouse_id
        self.timestamp = datetime.now()
```

**3. System Events:**
Technical events for monitoring aur debugging.

```python
class ServiceHealthEvent:
    def __init__(self, service_name, health_status, response_time):
        self.event_type = "SERVICE_HEALTH"
        self.service_name = service_name
        self.health_status = health_status  # HEALTHY, DEGRADED, DOWN
        self.response_time = response_time
        self.timestamp = datetime.now()
```

---

### Chapter 2: Producers, Consumers, Topics - Event Highway Ka Traffic System

Event streaming mein producers, consumers, aur topics ka concept Mumbai ke traffic system ki tarah hai. Producers hain vehicles jo road pe aate hain, topics hain roads/lanes, aur consumers hain destination points.

### Producers: Event Generate Karne Wale

Producer wo service hai jo events create karta hai. Real-world mein har user action, system change, ya external trigger ek event produce kar sakta hai.

**Swiggy Order Producer Example:**

```python
class SwiggyOrderProducer:
    def __init__(self, kafka_bootstrap_servers):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            key_serializer=str.encode,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            # Production settings for reliability
            acks='all',  # Wait for all replicas to acknowledge
            retries=3,   # Retry failed sends
            batch_size=16384,  # Batch size for efficiency
            linger_ms=10       # Wait 10ms to batch more messages
        )
        
    def place_order(self, user_id, restaurant_id, items, delivery_address):
        """
        User order place karta hai - multiple events generate hote hain
        """
        order_id = self.generate_order_id()
        
        # Main order event
        order_event = {
            'event_type': 'ORDER_PLACED',
            'order_id': order_id,
            'user_id': user_id,
            'restaurant_id': restaurant_id,
            'items': items,
            'delivery_address': delivery_address,
            'total_amount': self.calculate_total(items),
            'timestamp': datetime.now().isoformat(),
            'order_status': 'PLACED'
        }
        
        # Publish main order event
        self.producer.send(
            topic='swiggy-orders',
            key=order_id,  # Key for partitioning
            value=order_event
        )
        
        # Generate related events
        self.generate_inventory_check_event(order_id, items)
        self.generate_payment_processing_event(order_id, order_event['total_amount'])
        self.generate_restaurant_notification_event(order_id, restaurant_id, items)
        
        return order_id
        
    def generate_inventory_check_event(self, order_id, items):
        """
        Inventory service ke liye event
        """
        inventory_event = {
            'event_type': 'INVENTORY_CHECK_REQUIRED',
            'order_id': order_id,
            'items': items,
            'timestamp': datetime.now().isoformat()
        }
        
        self.producer.send('inventory-checks', inventory_event)
        
    def generate_payment_processing_event(self, order_id, amount):
        """
        Payment service ke liye event
        """
        payment_event = {
            'event_type': 'PAYMENT_PROCESSING_REQUIRED',
            'order_id': order_id,
            'amount': amount,
            'currency': 'INR',
            'timestamp': datetime.now().isoformat()
        }
        
        self.producer.send('payment-processing', payment_event)
```

**Producer Configuration for Indian Scale:**

```python
class ProductionKafkaProducer:
    def __init__(self):
        """
        Production-ready producer configuration
        Indian companies ke real requirements ke liye
        """
        self.producer = KafkaProducer(
            bootstrap_servers=[
                'kafka-mumbai-1.internal:9092',
                'kafka-mumbai-2.internal:9092', 
                'kafka-delhi-1.internal:9092'   # Multi-city setup
            ],
            
            # Reliability settings
            acks='all',              # All replicas must acknowledge
            retries=2147483647,      # Retry indefinitely
            max_in_flight_requests_per_connection=5,
            enable_idempotence=True, # Prevent duplicate messages
            
            # Performance settings for Big Billion Day scale
            batch_size=32768,        # 32KB batches
            linger_ms=5,             # Wait 5ms for batching
            compression_type='snappy', # Fast compression
            buffer_memory=67108864,   # 64MB buffer
            
            # Serialization
            key_serializer=str.encode,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
        )
        
    def send_with_callback(self, topic, key, value):
        """
        Callback ke saath message send karna
        """
        def on_send_success(record_metadata):
            print(f"Message sent to {record_metadata.topic}:{record_metadata.partition}:{record_metadata.offset}")
            
        def on_send_error(exception):
            print(f"Message failed to send: {exception}")
            # Alert monitoring system
            self.alert_ops_team(exception)
            
        future = self.producer.send(topic, key=key, value=value)
        future.add_callback(on_send_success)
        future.add_errback(on_send_error)
```

### Topics: Event Highways

Topics Kafka mein channels hain jahan events store hote hain. Ye Mumbai highways ki tarah hain - Western Express Highway pe sirf west-bound traffic, Eastern Express Highway pe east-bound traffic.

**Topic Design Patterns:**

```python
class TopicManager:
    def __init__(self):
        self.admin_client = KafkaAdminClient(
            bootstrap_servers=['kafka1:9092', 'kafka2:9092']
        )
        
    def create_swiggy_topics(self):
        """
        Swiggy-style topics create karna
        """
        topics = [
            # Order lifecycle topics
            NewTopic(name='order-placed', num_partitions=12, replication_factor=3),
            NewTopic(name='order-confirmed', num_partitions=12, replication_factor=3),
            NewTopic(name='order-preparing', num_partitions=8, replication_factor=3),
            NewTopic(name='order-ready', num_partitions=8, replication_factor=3),
            NewTopic(name='order-picked-up', num_partitions=6, replication_factor=3),
            NewTopic(name='order-delivered', num_partitions=6, replication_factor=3),
            
            # Business domain topics
            NewTopic(name='payment-events', num_partitions=16, replication_factor=3),
            NewTopic(name='delivery-tracking', num_partitions=20, replication_factor=3),
            NewTopic(name='restaurant-notifications', num_partitions=10, replication_factor=3),
            NewTopic(name='user-activity', num_partitions=24, replication_factor=3),
            
            # Analytics topics
            NewTopic(name='real-time-metrics', num_partitions=8, replication_factor=2),
            NewTopic(name='ml-feature-updates', num_partitions=4, replication_factor=2)
        ]
        
        # Create topics
        fs = self.admin_client.create_topics(topics)
        
        for topic, f in fs.items():
            try:
                f.result()  # Wait for creation
                print(f"Topic {topic} created successfully")
            except Exception as e:
                print(f"Failed to create topic {topic}: {e}")
```

**Partitioning Strategy for Indian Scale:**

```python
class PartitioningStrategy:
    """
    Indian companies ke liye smart partitioning
    """
    
    def get_partition_key(self, event_type, event_data):
        """
        Event type ke basis pe partition key decide karna
        """
        if event_type == 'ORDER_PLACED':
            # User ID ke basis pe partition - same user ke orders same partition mein
            return f"user_{event_data['user_id']}"
            
        elif event_type == 'DELIVERY_TRACKING':
            # Delivery partner ID ke basis pe partition
            return f"partner_{event_data['delivery_partner_id']}"
            
        elif event_type == 'PAYMENT_PROCESSING':
            # Payment gateway ke basis pe partition for load balancing
            gateway = event_data.get('payment_gateway', 'default')
            return f"gateway_{gateway}"
            
        elif event_type == 'RESTAURANT_NOTIFICATION':
            # Restaurant ID ke basis pe partition
            return f"restaurant_{event_data['restaurant_id']}"
            
        else:
            # Default partitioning
            return f"default_{hash(str(event_data)) % 10}"

# Usage example
partitioner = PartitioningStrategy()

def send_order_event(order_data):
    partition_key = partitioner.get_partition_key('ORDER_PLACED', order_data)
    
    producer.send(
        'order-placed',
        key=partition_key,
        value=order_data
    )
```

### Consumers: Event Process Karne Wale

Consumers wo services hain jo topics se events read karke business logic execute karte hain. Ye Mumbai mein different delivery services ki tarah hain - koi Amazon delivery karta hai, koi Flipkart, koi local courier.

**Restaurant Notification Consumer:**

```python
class RestaurantNotificationConsumer:
    def __init__(self, group_id='restaurant-notification-service'):
        self.consumer = KafkaConsumer(
            'order-placed',
            'order-cancelled',
            bootstrap_servers=['kafka1:9092', 'kafka2:9092'],
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            
            # Consumer configuration for reliability
            enable_auto_commit=False,  # Manual commit for accuracy
            auto_offset_reset='earliest',  # Start from beginning if no offset
            max_poll_records=100,  # Process 100 records at a time
            session_timeout_ms=30000,  # 30 second timeout
            heartbeat_interval_ms=10000,  # 10 second heartbeat
        )
        
        self.sms_service = SMSService()
        self.email_service = EmailService()
        self.push_notification_service = PushNotificationService()
        
    def start_consuming(self):
        """
        Restaurant notifications consume karna
        """
        try:
            for message in self.consumer:
                event = message.value
                
                if event['event_type'] == 'ORDER_PLACED':
                    self.handle_new_order(event)
                elif event['event_type'] == 'ORDER_CANCELLED':
                    self.handle_order_cancellation(event)
                    
                # Manual commit after successful processing
                self.consumer.commit()
                
        except Exception as e:
            print(f"Consumer error: {e}")
            # Restart consumer or alert ops team
            
    def handle_new_order(self, order_event):
        """
        Naya order notification bhejना restaurant को
        """
        restaurant_id = order_event['restaurant_id']
        order_details = {
            'order_id': order_event['order_id'],
            'items': order_event['items'],
            'customer_address': order_event['delivery_address'],
            'total_amount': order_event['total_amount'],
            'expected_prep_time': self.calculate_prep_time(order_event['items'])
        }
        
        # Multiple channels mein notification send karna
        restaurant_contact = self.get_restaurant_contact(restaurant_id)
        
        # SMS notification
        sms_message = f"नया ऑर्डर! Order ID: {order_details['order_id']}, Amount: ₹{order_details['total_amount']}"
        self.sms_service.send(restaurant_contact['phone'], sms_message)
        
        # Email notification
        self.email_service.send_order_email(restaurant_contact['email'], order_details)
        
        # Push notification to restaurant app
        self.push_notification_service.send_to_restaurant(restaurant_id, order_details)
        
        # Update restaurant dashboard
        self.update_restaurant_dashboard(restaurant_id, order_details)
```

**Delivery Tracking Consumer:**

```python
class DeliveryTrackingConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'delivery-partner-location',
            'order-picked-up',
            'order-delivered',
            bootstrap_servers=['kafka1:9092', 'kafka2:9092'],
            group_id='delivery-tracking-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        self.redis_client = redis.Redis(host='redis-cluster.internal')
        self.websocket_service = WebSocketService()
        
    def start_consuming(self):
        for message in self.consumer:
            event = message.value
            
            if event['event_type'] == 'DELIVERY_PARTNER_LOCATION':
                self.update_partner_location(event)
            elif event['event_type'] == 'ORDER_PICKED_UP':
                self.handle_pickup(event)
            elif event['event_type'] == 'ORDER_DELIVERED':
                self.handle_delivery(event)
                
    def update_partner_location(self, location_event):
        """
        Delivery partner ka real-time location update
        """
        partner_id = location_event['delivery_partner_id']
        location = location_event['location']
        
        # Redis mein current location store karna
        location_key = f"partner_location:{partner_id}"
        self.redis_client.hset(location_key, {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'timestamp': location_event['timestamp'],
            'accuracy': location.get('accuracy', 10)
        })
        
        # Active orders ke liye ETA calculate karna
        active_orders = self.get_active_orders_for_partner(partner_id)
        
        for order_id in active_orders:
            new_eta = self.calculate_eta(partner_id, order_id, location)
            
            # Customer ko real-time update send karna
            eta_update = {
                'order_id': order_id,
                'delivery_partner_location': location,
                'estimated_arrival': new_eta,
                'timestamp': datetime.now().isoformat()
            }
            
            # WebSocket se real-time update
            user_id = self.get_user_for_order(order_id)
            self.websocket_service.send_to_user(user_id, eta_update)
```

### Consumer Groups: Load Distribution

Consumer groups Kafka ka brilliant feature hai. Same topic ko multiple consumers parallel mein process kar sakte hain, but har message sirf ek consumer ko milta hai.

```python
class ScalableOrderProcessor:
    """
    Multiple consumers ke saath order processing
    Big Billion Day ke liye scale karna
    """
    
    def __init__(self, instance_id):
        self.instance_id = instance_id
        
        # Same group ID but different instances
        self.consumer = KafkaConsumer(
            'order-placed',
            bootstrap_servers=['kafka1:9092', 'kafka2:9092'],
            group_id='order-processing-service',  # Same group
            client_id=f'order-processor-{instance_id}',  # Different client
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            max_poll_records=50  # Process 50 orders at a time
        )
        
    def start_processing(self):
        print(f"Order processor {self.instance_id} starting...")
        
        for message in self.consumer:
            order_event = message.value
            
            # Process order
            processing_result = self.process_order(order_event)
            
            if processing_result['success']:
                print(f"Instance {self.instance_id} processed order {order_event['order_id']}")
            else:
                print(f"Instance {self.instance_id} failed to process order {order_event['order_id']}")
                # Send to dead letter queue
                self.send_to_dlq(order_event, processing_result['error'])

# Multiple instances run karna for scalability
def run_multiple_order_processors():
    import multiprocessing
    
    # 8 parallel processors for handling high load
    processes = []
    for i in range(8):
        processor = ScalableOrderProcessor(instance_id=i)
        process = multiprocessing.Process(target=processor.start_processing)
        processes.append(process)
        process.start()
    
    # Wait for all processes
    for process in processes:
        process.join()
```

### Advanced Consumer Patterns

**1. Exactly-Once Processing:**

```python
class ExactlyOnceOrderProcessor:
    """
    Duplicate order processing prevent karna
    """
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            'order-placed',
            enable_auto_commit=False,  # Manual commit
            isolation_level='read_committed'  # Only committed messages
        )
        
        self.processed_orders = set()  # In-memory deduplication
        self.db = DatabaseConnection()
        
    def process_order_exactly_once(self, order_event):
        order_id = order_event['order_id']
        
        # Check if already processed
        if self.is_already_processed(order_id):
            print(f"Order {order_id} already processed, skipping")
            return
            
        try:
            # Start database transaction
            with self.db.transaction():
                # Process order
                self.process_order_business_logic(order_event)
                
                # Mark as processed
                self.mark_as_processed(order_id)
                
                # Commit Kafka offset
                self.consumer.commit()
                
        except Exception as e:
            # Transaction will rollback automatically
            print(f"Failed to process order {order_id}: {e}")
            # Don't commit Kafka offset - message will be reprocessed
```

**2. Dead Letter Queue Pattern:**

```python
class ResilientOrderConsumer:
    def __init__(self):
        self.main_consumer = KafkaConsumer('order-placed')
        self.dlq_producer = KafkaProducer()  # Dead letter queue producer
        
    def process_with_dlq(self, order_event):
        try:
            # Try processing order
            result = self.process_order(order_event)
            return result
            
        except RetryableException as e:
            # Temporary failure - retry
            print(f"Retryable error for order {order_event['order_id']}: {e}")
            raise  # Will be retried by Kafka
            
        except PermanentException as e:
            # Permanent failure - send to DLQ
            print(f"Permanent error for order {order_event['order_id']}: {e}")
            
            dlq_message = {
                'original_event': order_event,
                'error_message': str(e),
                'error_type': type(e).__name__,
                'failed_at': datetime.now().isoformat(),
                'retry_count': order_event.get('retry_count', 0)
            }
            
            # Send to dead letter queue
            self.dlq_producer.send('order-processing-dlq', dlq_message)
            
            # Don't raise - message is handled
            return {'success': False, 'sent_to_dlq': True}
```

Ye Chapter 2 complete hota hai producers, consumers, aur topics ki detailed explanation ke saath. Next chapter mein hum delivery guarantees ke bare mein detail mein discuss karenge - exactly-once, at-least-once, at-most-once delivery patterns ke saath real production examples.

---

### Chapter 3: Delivery Guarantees - Message Delivery Ki Guarantee System

Dosto, delivery guarantees event streaming ka sabse critical part hai. Imagine karo Mumbai mein dabbawala system mein agar delivery guarantee nahi ho toh kya hoga? Office jane wale logo ka khana ghar pe reh jayega! Same problem event streaming mein bhi hai - agar message delivery guarantee nahi hai, toh orders lose ho sakte hain, payments duplicate ho sakte hain, ya phir notifications miss ho sakte hain.

### Types of Delivery Guarantees

**1. At-Most-Once Delivery:**
Message maximum ek baar deliver hoga, ya bilkul nahi hoga. Fast hai but message loss ho sakta hai.

**2. At-Least-Once Delivery:**
Message kam se kam ek baar deliver hoga, but duplicate bhi ho sakta hai.

**3. Exactly-Once Delivery:**
Message exactly ek hi baar process hoga. Sabse challenging but business-critical.

### At-Most-Once Delivery: Fire-and-Forget Pattern

Ye pattern fast hai but reliability kam hai. Jaise Mumbai local train mein announcement hota hai platform pe - agar aapne suna toh suna, nahi suna toh miss ho gaya.

```python
class AtMostOnceProducer:
    """
    Fast but unreliable message delivery
    Social media likes, views jaise non-critical events ke liye
    """
    
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka1:9092'],
            acks=0,  # Don't wait for any acknowledgment
            retries=0,  # No retries
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
    def track_user_activity(self, user_id, activity_type, page_url):
        """
        User activity tracking - loss acceptable
        """
        activity_event = {
            'user_id': user_id,
            'activity_type': activity_type,  # PAGE_VIEW, CLICK, SCROLL
            'page_url': page_url,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.get_session_id(user_id)
        }
        
        # Fire and forget - no waiting for acknowledgment
        self.producer.send('user-activity', activity_event)
        
        # No error handling - just log for debugging
        print(f"Activity tracked for user {user_id}: {activity_type}")

# Consumer for at-most-once
class AtMostOnceConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'user-activity',
            enable_auto_commit=True,  # Auto commit offsets
            auto_commit_interval_ms=5000,  # Commit every 5 seconds
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
    def process_activity(self):
        for message in self.consumer:
            activity = message.value
            
            # Process immediately without error handling
            self.update_analytics_db(activity)
            
            # If processing fails, message is lost
            # But that's acceptable for analytics data
```

**Use Cases for At-Most-Once:**
- Page view tracking
- Social media interactions (likes, shares)
- Real-time analytics (some data loss acceptable)
- Gaming telemetry
- IoT sensor data (frequent updates)

### At-Least-Once Delivery: Retry Until Success

Ye pattern ensure karta hai ki message definitely deliver ho, but duplicate bhi ho sakta hai. Jaise WhatsApp message - message deliver hone tak retry karta rehta hai.

```python
class AtLeastOnceProducer:
    """
    Reliable delivery with possible duplicates
    Payment notifications, order confirmations ke liye
    """
    
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka1:9092', 'kafka2:9092'],
            acks='all',  # Wait for all replicas
            retries=2147483647,  # Retry indefinitely
            retry_backoff_ms=100,  # Backoff between retries
            max_in_flight_requests_per_connection=5,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
    def send_payment_notification(self, user_id, payment_id, amount, status):
        """
        Payment notification - must be delivered
        """
        notification_event = {
            'event_type': 'PAYMENT_NOTIFICATION',
            'user_id': user_id,
            'payment_id': payment_id,
            'amount': amount,
            'status': status,  # SUCCESS, FAILED, PENDING
            'timestamp': datetime.now().isoformat(),
            'idempotency_key': f"payment_{payment_id}_{status}"  # For deduplication
        }
        
        try:
            # Will retry until successful
            future = self.producer.send('payment-notifications', notification_event)
            record_metadata = future.get(timeout=60)  # Wait up to 60 seconds
            
            print(f"Payment notification sent: {record_metadata.topic}:{record_metadata.offset}")
            
        except Exception as e:
            # Log error but producer will keep retrying
            print(f"Payment notification error (will retry): {e}")
            raise

class AtLeastOnceConsumer:
    """
    Consumer that handles potential duplicates
    """
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            'payment-notifications',
            enable_auto_commit=False,  # Manual commit for reliability
            max_poll_records=10,  # Small batches for quick processing
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        self.processed_notifications = {}  # In-memory deduplication
        self.sms_service = SMSService()
        
    def process_notifications(self):
        for message in self.consumer:
            notification = message.value
            idempotency_key = notification['idempotency_key']
            
            # Check for duplicate
            if self.is_duplicate(idempotency_key):
                print(f"Duplicate notification detected: {idempotency_key}")
                self.consumer.commit()  # Commit offset but skip processing
                continue
                
            try:
                # Process notification
                self.send_sms_notification(notification)
                self.update_user_dashboard(notification)
                
                # Mark as processed
                self.mark_as_processed(idempotency_key)
                
                # Commit offset
                self.consumer.commit()
                
            except Exception as e:
                print(f"Failed to process notification: {e}")
                # Don't commit - message will be reprocessed
                
    def is_duplicate(self, idempotency_key):
        return idempotency_key in self.processed_notifications
        
    def mark_as_processed(self, idempotency_key):
        self.processed_notifications[idempotency_key] = datetime.now()
```

**Real Production Example - Paytm Payment Notifications:**

```python
class PaytmNotificationSystem:
    """
    Paytm-style payment notification system
    At-least-once delivery with deduplication
    """
    
    def __init__(self):
        self.producer = AtLeastOnceProducer()
        self.redis_client = redis.Redis(host='redis-cluster')
        
    def notify_payment_success(self, user_id, transaction_id, amount):
        """
        Payment success notification - must reach user
        """
        notification_data = {
            'user_id': user_id,
            'transaction_id': transaction_id,
            'amount': amount,
            'notification_type': 'PAYMENT_SUCCESS',
            'channels': ['SMS', 'EMAIL', 'PUSH'],  # Multiple channels
            'retry_count': 0,
            'idempotency_key': f"payment_success_{transaction_id}"
        }
        
        # Send to notification service
        self.producer.send_payment_notification(
            user_id, transaction_id, amount, 'SUCCESS'
        )
        
    def handle_notification_failure(self, notification_data):
        """
        Handle notification delivery failures
        """
        retry_count = notification_data.get('retry_count', 0)
        
        if retry_count < 3:
            # Retry with backoff
            delay = (2 ** retry_count) * 60  # Exponential backoff
            
            retry_notification = notification_data.copy()
            retry_notification['retry_count'] = retry_count + 1
            retry_notification['scheduled_at'] = datetime.now() + timedelta(seconds=delay)
            
            # Schedule retry
            self.schedule_notification_retry(retry_notification)
            
        else:
            # Send to manual intervention queue
            self.send_to_manual_review(notification_data)
```

### Exactly-Once Delivery: Perfect Delivery Guarantee

Ye sabse challenging pattern hai. Message exactly ek baar process hoga - no duplicates, no loss. Banking aur financial transactions ke liye zaroori hai.

```python
class ExactlyOnceProcessor:
    """
    Exactly-once processing for critical business events
    Banking transactions, order payments ke liye
    """
    
    def __init__(self):
        # Kafka with idempotent producer
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka1:9092'],
            acks='all',
            retries=2147483647,
            enable_idempotence=True,  # Exactly-once producer
            max_in_flight_requests_per_connection=5,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        self.consumer = KafkaConsumer(
            enable_auto_commit=False,
            isolation_level='read_committed',  # Only read committed messages
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        self.db = DatabaseConnection()
        
    def process_bank_transfer(self, transfer_event):
        """
        Bank transfer processing - must be exactly once
        """
        transfer_id = transfer_event['transfer_id']
        from_account = transfer_event['from_account']
        to_account = transfer_event['to_account']
        amount = transfer_event['amount']
        
        # Start transaction
        with self.db.transaction():
            # Check if already processed
            if self.is_transfer_already_processed(transfer_id):
                print(f"Transfer {transfer_id} already processed")
                self.consumer.commit()
                return
                
            # Validate accounts and balance
            if not self.validate_transfer(from_account, to_account, amount):
                raise InvalidTransferException(f"Invalid transfer: {transfer_id}")
                
            # Perform transfer
            self.debit_account(from_account, amount)
            self.credit_account(to_account, amount)
            
            # Record transfer
            self.record_transfer(transfer_id, from_account, to_account, amount)
            
            # Send confirmation events
            self.send_transfer_confirmation(transfer_event)
            
            # Commit database transaction and Kafka offset together
            self.consumer.commit()
            
    def is_transfer_already_processed(self, transfer_id):
        """
        Database mein check karna ki transfer already processed hai
        """
        query = "SELECT id FROM processed_transfers WHERE transfer_id = %s"
        result = self.db.execute(query, (transfer_id,))
        return len(result) > 0
        
    def record_transfer(self, transfer_id, from_account, to_account, amount):
        """
        Transfer record karna idempotency ke liye
        """
        query = """
        INSERT INTO processed_transfers 
        (transfer_id, from_account, to_account, amount, processed_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute(query, (
            transfer_id, from_account, to_account, amount, datetime.now()
        ))
```

**HDFC Bank Style Exactly-Once Processing:**

```python
class HDFCTransactionProcessor:
    """
    HDFC Bank style transaction processing
    Exactly-once with full audit trail
    """
    
    def __init__(self):
        self.kafka_consumer = KafkaConsumer(
            'banking-transactions',
            group_id='hdfc-transaction-processor',
            enable_auto_commit=False,
            isolation_level='read_committed'
        )
        
        self.core_banking_db = CoreBankingDB()
        self.audit_db = AuditDB()
        
    def process_upi_transaction(self, transaction_event):
        """
        UPI transaction processing with exactly-once guarantee
        """
        transaction_id = transaction_event['transaction_id']
        
        with self.core_banking_db.transaction():
            # Idempotency check
            existing_transaction = self.get_existing_transaction(transaction_id)
            if existing_transaction:
                if existing_transaction['status'] == 'COMPLETED':
                    print(f"Transaction {transaction_id} already completed")
                    self.kafka_consumer.commit()
                    return existing_transaction
                elif existing_transaction['status'] == 'FAILED':
                    print(f"Transaction {transaction_id} already failed")
                    self.kafka_consumer.commit()
                    return existing_transaction
                    
            # Create transaction record
            self.create_transaction_record(transaction_event)
            
            try:
                # Validate transaction
                validation_result = self.validate_upi_transaction(transaction_event)
                if not validation_result['valid']:
                    self.fail_transaction(transaction_id, validation_result['reason'])
                    self.kafka_consumer.commit()
                    return {'status': 'FAILED', 'reason': validation_result['reason']}
                
                # Process payment
                self.process_payment(transaction_event)
                
                # Update transaction status
                self.complete_transaction(transaction_id)
                
                # Send notifications
                self.send_transaction_notifications(transaction_event)
                
                # Audit logging
                self.audit_db.log_transaction(transaction_id, 'COMPLETED', transaction_event)
                
                # Commit everything together
                self.kafka_consumer.commit()
                
                return {'status': 'COMPLETED', 'transaction_id': transaction_id}
                
            except Exception as e:
                # Mark transaction as failed
                self.fail_transaction(transaction_id, str(e))
                
                # Audit failure
                self.audit_db.log_transaction(transaction_id, 'FAILED', transaction_event, str(e))
                
                # Commit the failure state
                self.kafka_consumer.commit()
                
                raise TransactionProcessingException(f"Transaction {transaction_id} failed: {e}")
                
    def validate_upi_transaction(self, transaction_event):
        """
        UPI transaction validation
        """
        validations = [
            self.validate_account_exists(transaction_event['from_account']),
            self.validate_account_exists(transaction_event['to_account']),
            self.validate_sufficient_balance(transaction_event['from_account'], transaction_event['amount']),
            self.validate_daily_limit(transaction_event['from_account'], transaction_event['amount']),
            self.validate_not_duplicate(transaction_event['transaction_id'])
        ]
        
        for validation in validations:
            if not validation['valid']:
                return validation
                
        return {'valid': True}
```

### Delivery Guarantee Selection Guide

**Choose At-Most-Once when:**
- High throughput needed
- Some data loss acceptable
- Real-time analytics
- IoT sensor data
- Social media interactions

**Choose At-Least-Once when:**
- Reliability important
- Can handle duplicates
- Notifications systems
- Email marketing
- Order confirmations

**Choose Exactly-Once when:**
- Zero tolerance for duplicates
- Financial transactions
- Inventory updates
- Critical business events
- Compliance requirements

### Indian Production Examples

**1. PhonePe UPI Transactions (Exactly-Once):**
```python
class PhonePeUPIProcessor:
    def process_upi_payment(self, payment_event):
        """
        PhonePe UPI payments - exactly once processing
        """
        with self.transaction_manager.transaction():
            # Check if payment already processed
            if self.is_payment_processed(payment_event['upi_ref_id']):
                return self.get_payment_status(payment_event['upi_ref_id'])
                
            # Process with NPCI
            npci_response = self.send_to_npci(payment_event)
            
            # Update local records
            self.update_payment_status(payment_event, npci_response)
            
            # Commit transaction and Kafka offset
            self.commit_all()
```

**2. Zomato Order Updates (At-Least-Once):**
```python
class ZomatoOrderUpdates:
    def send_order_status_update(self, order_event):
        """
        Order status updates - can handle duplicates
        """
        # Send to multiple channels
        self.send_push_notification(order_event)  # Idempotent
        self.send_sms_update(order_event)         # Idempotent
        self.update_app_status(order_event)       # Idempotent
```

**3. Hotstar Live Streaming (At-Most-Once):**
```python
class HotstarViewAnalytics:
    def track_viewer_activity(self, view_event):
        """
        Live streaming analytics - fast over accurate
        """
        # Fire and forget for real-time analytics
        self.analytics_stream.send(view_event)
        # Some loss acceptable for live metrics
```

Part 1 complete! Next parts mein hum Apache Kafka architecture, Event Sourcing, CQRS, aur real production case studies detail mein cover karenge. Ye foundation strong banane ke liye zaroori tha - ab hum advanced topics pe dive kar sakte hain!
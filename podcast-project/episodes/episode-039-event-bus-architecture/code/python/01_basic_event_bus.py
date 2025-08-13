#!/usr/bin/env python3
"""
Basic Event Bus Implementation
=============================

Production-ready event bus implementation for decoupled communication.
Event bus enables publish-subscribe messaging between different components.

Mumbai Context: यह Mumbai local train के announcement system जैसा है!
हर station पर announcements होते हैं (events publish), और जो passengers को
चाहिए वो सुनते हैं (subscribe). कोई direct connection नहीं है!

Real-world usage:
- Microservices communication
- Event-driven architecture
- Domain event handling  
- System integration
- Notification systems
"""

import time
import threading
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import sqlite3
from abc import ABC, abstractmethod
import asyncio
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """Event priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Event:
    """Event message structure"""
    event_id: str
    event_type: str
    source: str
    data: Dict[str, Any]
    timestamp: float
    correlation_id: str = ""
    priority: EventPriority = EventPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    ttl_seconds: Optional[int] = None  # Time to live

    def is_expired(self) -> bool:
        """Check if event has expired"""
        if self.ttl_seconds is None:
            return False
        return time.time() > (self.timestamp + self.ttl_seconds)

class EventHandler(ABC):
    """Abstract event handler interface"""
    
    @abstractmethod
    def handle(self, event: Event) -> bool:
        """Handle event - return True if successful"""
        pass
    
    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """Check if handler can handle this event type"""
        pass
    
    def get_handler_id(self) -> str:
        """Get unique handler identifier"""
        return self.__class__.__name__

class Subscription:
    """Event subscription details"""
    
    def __init__(self, handler: EventHandler, event_types: Set[str], 
                 priority_filter: Optional[EventPriority] = None,
                 source_filter: Optional[str] = None):
        self.handler = handler
        self.event_types = event_types
        self.priority_filter = priority_filter
        self.source_filter = source_filter
        self.created_at = time.time()
        self.processed_count = 0
        self.error_count = 0
        self.last_processed_at = None

    def matches(self, event: Event) -> bool:
        """Check if subscription matches the event"""
        # Check event type
        if event.event_type not in self.event_types:
            return False
        
        # Check priority filter
        if self.priority_filter and event.priority != self.priority_filter:
            return False
        
        # Check source filter
        if self.source_filter and event.source != self.source_filter:
            return False
        
        return True

class EventBus:
    """
    Basic Event Bus Implementation
    
    Mumbai Metaphor: यह Mumbai Railway के announcement system जैसा है!
    Central PA system से सभी platforms पर announcements होते हैं.
    Passengers अपनी जरुरत के हिसाब से सुनते हैं.
    """
    
    def __init__(self, max_workers: int = 10, persistent: bool = True):
        self.subscriptions: List[Subscription] = []
        self.event_store: List[Event] = []
        self.dead_letter_queue: List[Event] = []
        self.max_workers = max_workers
        self.persistent = persistent
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.event_queue = queue.PriorityQueue()
        self.lock = threading.RLock()
        self.running = False
        
        # Statistics
        self.stats = {
            'events_published': 0,
            'events_processed': 0,
            'events_failed': 0,
            'events_dead_lettered': 0,
            'active_subscriptions': 0
        }
        
        # Database for persistence
        if persistent:
            self.db_path = "eventbus.db"
            self._init_database()
        
        logger.info(f"🚌 Event Bus initialized (workers: {max_workers}, persistent: {persistent})")
    
    def _init_database(self):
        """Initialize database for event persistence"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    correlation_id TEXT,
                    priority INTEGER,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    ttl_seconds INTEGER,
                    status TEXT DEFAULT 'PUBLISHED',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_type_timestamp 
                ON events(event_type, timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status_timestamp 
                ON events(status, timestamp)
            """)
    
    def start(self):
        """Start the event bus processing"""
        with self.lock:
            if self.running:
                return
            
            self.running = True
            
            # Start event processing thread
            threading.Thread(target=self._process_events, daemon=True).start()
            
            logger.info("🚀 Event Bus started")
    
    def stop(self):
        """Stop the event bus processing"""
        with self.lock:
            self.running = False
            self.executor.shutdown(wait=True)
            
            logger.info("🛑 Event Bus stopped")
    
    def subscribe(self, handler: EventHandler, event_types: Set[str],
                  priority_filter: Optional[EventPriority] = None,
                  source_filter: Optional[str] = None) -> str:
        """
        Subscribe to events
        
        Args:
            handler: Event handler
            event_types: Set of event types to subscribe to
            priority_filter: Optional priority filter
            source_filter: Optional source filter
            
        Returns:
            Subscription ID
        """
        with self.lock:
            subscription = Subscription(handler, event_types, priority_filter, source_filter)
            self.subscriptions.append(subscription)
            self.stats['active_subscriptions'] = len(self.subscriptions)
            
            logger.info(f"📝 Subscription added: {handler.get_handler_id()} for {event_types}")
            
            return f"{handler.get_handler_id()}_{len(self.subscriptions)}"
    
    def unsubscribe(self, handler: EventHandler):
        """Unsubscribe handler from all events"""
        with self.lock:
            self.subscriptions = [
                sub for sub in self.subscriptions 
                if sub.handler.get_handler_id() != handler.get_handler_id()
            ]
            self.stats['active_subscriptions'] = len(self.subscriptions)
            
            logger.info(f"🗑️ Handler unsubscribed: {handler.get_handler_id()}")
    
    def publish(self, event: Event):
        """
        Publish an event to the bus
        
        Args:
            event: Event to publish
        """
        # Validate event
        if event.is_expired():
            logger.warning(f"⚠️ Event expired, not publishing: {event.event_id}")
            return
        
        with self.lock:
            # Store event
            self.event_store.append(event)
            self.stats['events_published'] += 1
            
            # Persist to database if enabled
            if self.persistent:
                self._persist_event(event)
            
            # Add to processing queue with priority
            priority_value = 5 - event.priority.value  # Higher priority = lower number
            self.event_queue.put((priority_value, time.time(), event))
            
            logger.info(f"📢 Event published: {event.event_type} from {event.source} (ID: {event.event_id})")
    
    def _process_events(self):
        """Background event processing loop"""
        while self.running:
            try:
                # Get event from queue with timeout
                try:
                    priority, queued_at, event = self.event_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Check if event expired while in queue
                if event.is_expired():
                    logger.warning(f"⚠️ Event expired in queue: {event.event_id}")
                    continue
                
                # Find matching subscriptions
                matching_subscriptions = []
                with self.lock:
                    for subscription in self.subscriptions:
                        if subscription.matches(event):
                            matching_subscriptions.append(subscription)
                
                # Process event with matching handlers
                if matching_subscriptions:
                    self._dispatch_event(event, matching_subscriptions)
                else:
                    logger.debug(f"🔍 No handlers found for event: {event.event_type}")
                
                self.event_queue.task_done()
                
            except Exception as e:
                logger.error(f"❌ Error in event processing loop: {e}")
    
    def _dispatch_event(self, event: Event, subscriptions: List[Subscription]):
        """Dispatch event to matching subscriptions"""
        
        def handle_event(subscription: Subscription) -> bool:
            """Handle event with single subscription"""
            try:
                handler_id = subscription.handler.get_handler_id()
                logger.debug(f"🔄 Processing event {event.event_id} with {handler_id}")
                
                success = subscription.handler.handle(event)
                
                if success:
                    subscription.processed_count += 1
                    subscription.last_processed_at = time.time()
                    logger.debug(f"✅ Event processed successfully by {handler_id}")
                    return True
                else:
                    subscription.error_count += 1
                    logger.warning(f"❌ Event processing failed by {handler_id}")
                    return False
                    
            except Exception as e:
                subscription.error_count += 1
                logger.error(f"❌ Exception in event handler {handler_id}: {e}")
                return False
        
        # Submit handler tasks to thread pool
        futures = []
        for subscription in subscriptions:
            future = self.executor.submit(handle_event, subscription)
            futures.append((subscription, future))
        
        # Collect results
        successful_handlers = 0
        failed_handlers = 0
        
        for subscription, future in futures:
            try:
                success = future.result(timeout=30)  # 30 second timeout per handler
                if success:
                    successful_handlers += 1
                else:
                    failed_handlers += 1
            except Exception as e:
                failed_handlers += 1
                logger.error(f"❌ Handler execution error: {e}")
        
        # Update statistics
        if successful_handlers > 0:
            self.stats['events_processed'] += 1
        
        if failed_handlers > 0:
            self.stats['events_failed'] += 1
            
            # Check if event should be retried or dead-lettered
            if event.retry_count < event.max_retries:
                # Retry event
                event.retry_count += 1
                logger.info(f"🔄 Retrying event {event.event_id} (attempt {event.retry_count}/{event.max_retries})")
                
                # Add delay before retry
                time.sleep(0.1 * (2 ** event.retry_count))  # Exponential backoff
                self.publish(event)
            else:
                # Move to dead letter queue
                self._dead_letter_event(event)
        
        logger.info(f"📊 Event {event.event_id} processed by {successful_handlers} handlers, {failed_handlers} failed")
    
    def _dead_letter_event(self, event: Event):
        """Move failed event to dead letter queue"""
        with self.lock:
            self.dead_letter_queue.append(event)
            self.stats['events_dead_lettered'] += 1
            
            # Persist dead letter event
            if self.persistent:
                self._persist_event(event, status='DEAD_LETTERED')
            
            logger.warning(f"💀 Event moved to dead letter queue: {event.event_id}")
    
    def _persist_event(self, event: Event, status: str = 'PUBLISHED'):
        """Persist event to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO events 
                    (event_id, event_type, source, data, timestamp, correlation_id,
                     priority, retry_count, max_retries, ttl_seconds, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.event_type,
                    event.source,
                    json.dumps(event.data),
                    event.timestamp,
                    event.correlation_id,
                    event.priority.value,
                    event.retry_count,
                    event.max_retries,
                    event.ttl_seconds,
                    status
                ))
        except Exception as e:
            logger.error(f"❌ Failed to persist event: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        with self.lock:
            # Calculate subscription statistics
            subscription_stats = {}
            for subscription in self.subscriptions:
                handler_id = subscription.handler.get_handler_id()
                if handler_id not in subscription_stats:
                    subscription_stats[handler_id] = {
                        'processed_count': 0,
                        'error_count': 0,
                        'event_types': set()
                    }
                
                subscription_stats[handler_id]['processed_count'] += subscription.processed_count
                subscription_stats[handler_id]['error_count'] += subscription.error_count
                subscription_stats[handler_id]['event_types'].update(subscription.event_types)
            
            # Convert sets to lists for JSON serialization
            for handler_stats in subscription_stats.values():
                handler_stats['event_types'] = list(handler_stats['event_types'])
            
            return {
                **self.stats,
                'queue_size': self.event_queue.qsize(),
                'dead_letter_queue_size': len(self.dead_letter_queue),
                'subscription_stats': subscription_stats
            }
    
    def get_events(self, event_type: Optional[str] = None, 
                   source: Optional[str] = None,
                   limit: int = 100) -> List[Event]:
        """Get events from store with optional filtering"""
        with self.lock:
            filtered_events = self.event_store
            
            if event_type:
                filtered_events = [e for e in filtered_events if e.event_type == event_type]
            
            if source:
                filtered_events = [e for e in filtered_events if e.source == source]
            
            # Sort by timestamp (newest first) and limit
            filtered_events.sort(key=lambda e: e.timestamp, reverse=True)
            return filtered_events[:limit]
    
    def get_dead_letter_events(self) -> List[Event]:
        """Get events from dead letter queue"""
        with self.lock:
            return self.dead_letter_queue.copy()

# Example event handlers for demonstration

class OrderEventHandler(EventHandler):
    """Handler for order-related events"""
    
    def __init__(self):
        self.processed_orders = {}
    
    def handle(self, event: Event) -> bool:
        try:
            if event.event_type == "ORDER_CREATED":
                order_id = event.data.get('order_id')
                customer_id = event.data.get('customer_id')
                total_amount = event.data.get('total_amount', 0)
                
                # Process order
                self.processed_orders[order_id] = {
                    'customer_id': customer_id,
                    'total_amount': total_amount,
                    'status': 'PROCESSING',
                    'processed_at': time.time()
                }
                
                logger.info(f"📦 Order processed: {order_id} for {customer_id} (₹{total_amount:.2f})")
                return True
                
            elif event.event_type == "ORDER_CANCELLED":
                order_id = event.data.get('order_id')
                if order_id in self.processed_orders:
                    self.processed_orders[order_id]['status'] = 'CANCELLED'
                    logger.info(f"🚫 Order cancelled: {order_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error processing order event: {e}")
            return False
        
        return True
    
    def can_handle(self, event_type: str) -> bool:
        return event_type in ["ORDER_CREATED", "ORDER_CANCELLED", "ORDER_UPDATED"]

class PaymentEventHandler(EventHandler):
    """Handler for payment-related events"""
    
    def __init__(self):
        self.processed_payments = {}
    
    def handle(self, event: Event) -> bool:
        try:
            if event.event_type == "PAYMENT_INITIATED":
                payment_id = event.data.get('payment_id')
                order_id = event.data.get('order_id')
                amount = event.data.get('amount', 0)
                
                # Simulate payment processing (90% success rate)
                success = (hash(payment_id) % 10) < 9
                
                if success:
                    self.processed_payments[payment_id] = {
                        'order_id': order_id,
                        'amount': amount,
                        'status': 'COMPLETED',
                        'processed_at': time.time()
                    }
                    logger.info(f"💰 Payment processed: {payment_id} - ₹{amount:.2f}")
                else:
                    logger.warning(f"❌ Payment failed: {payment_id}")
                
                return success
                
        except Exception as e:
            logger.error(f"❌ Error processing payment event: {e}")
            return False
        
        return True
    
    def can_handle(self, event_type: str) -> bool:
        return event_type in ["PAYMENT_INITIATED", "PAYMENT_COMPLETED", "PAYMENT_FAILED"]

class NotificationEventHandler(EventHandler):
    """Handler for notification events"""
    
    def __init__(self):
        self.sent_notifications = []
    
    def handle(self, event: Event) -> bool:
        try:
            notification_data = {
                'event_id': event.event_id,
                'event_type': event.event_type,
                'recipient': event.data.get('customer_id', 'unknown'),
                'message': self._generate_message(event),
                'sent_at': time.time()
            }
            
            self.sent_notifications.append(notification_data)
            
            logger.info(f"📱 Notification sent: {event.event_type} to {notification_data['recipient']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
            return False
    
    def _generate_message(self, event: Event) -> str:
        """Generate notification message based on event"""
        if event.event_type == "ORDER_CREATED":
            return f"आपका order confirm हो गया है! Order ID: {event.data.get('order_id', 'N/A')}"
        elif event.event_type == "PAYMENT_INITIATED":
            return f"Payment processing हो रहा है। Amount: ₹{event.data.get('amount', 0):.2f}"
        elif event.event_type == "ORDER_CANCELLED":
            return f"आपका order cancel हो गया है। Order ID: {event.data.get('order_id', 'N/A')}"
        else:
            return f"Update: {event.event_type}"
    
    def can_handle(self, event_type: str) -> bool:
        return True  # Handle all events for notifications

def simulate_zomato_order_events():
    """
    Simulate Zomato order processing using event bus
    
    Mumbai Scenario: Zomato का order processing system event-driven है!
    जब customer order place करता है, तो multiple services events के through
    coordinate करती हैं - order service, payment service, notification service.
    """
    logger.info("🍽️ Starting Zomato Event Bus simulation...")
    
    # Initialize event bus
    event_bus = EventBus(max_workers=5, persistent=True)
    event_bus.start()
    
    # Initialize event handlers
    order_handler = OrderEventHandler()
    payment_handler = PaymentEventHandler()
    notification_handler = NotificationEventHandler()
    
    # Subscribe handlers to events
    event_bus.subscribe(
        order_handler, 
        {"ORDER_CREATED", "ORDER_CANCELLED", "ORDER_UPDATED"}
    )
    
    event_bus.subscribe(
        payment_handler,
        {"PAYMENT_INITIATED"},
        priority_filter=EventPriority.HIGH  # High priority for payments
    )
    
    event_bus.subscribe(
        notification_handler,
        {"ORDER_CREATED", "PAYMENT_INITIATED", "ORDER_CANCELLED"},
        priority_filter=None  # Accept all priorities
    )
    
    logger.info("🎭 All handlers subscribed to events")
    
    # Simulate order processing events
    sample_orders = [
        {
            'order_id': 'ORD_001',
            'customer_id': 'customer_rahul_001',
            'restaurant_id': 'rest_mumbai_darbar',
            'items': ['Butter Chicken', 'Garlic Naan'],
            'total_amount': 450.0
        },
        {
            'order_id': 'ORD_002',
            'customer_id': 'customer_priya_002',
            'restaurant_id': 'rest_theobroma_powai',
            'items': ['Chocolate Cake'],
            'total_amount': 350.0
        },
        {
            'order_id': 'ORD_003',
            'customer_id': 'customer_arjun_003',
            'restaurant_id': 'rest_burger_king',
            'items': ['Whopper Meal'],
            'total_amount': 280.0
        }
    ]
    
    # Publish order events
    for order in sample_orders:
        # 1. Order Created Event
        order_created_event = Event(
            event_id=f"{order['order_id']}_CREATED_{int(time.time() * 1000)}",
            event_type="ORDER_CREATED",
            source="OrderService",
            data=order,
            timestamp=time.time(),
            priority=EventPriority.NORMAL,
            correlation_id=order['order_id']
        )
        
        event_bus.publish(order_created_event)
        
        # 2. Payment Initiated Event (after small delay)
        time.sleep(0.1)
        
        payment_event = Event(
            event_id=f"PAY_{order['order_id']}_{int(time.time() * 1000)}",
            event_type="PAYMENT_INITIATED",
            source="PaymentService",
            data={
                'payment_id': f"PAY_{order['order_id']}",
                'order_id': order['order_id'],
                'customer_id': order['customer_id'],
                'amount': order['total_amount']
            },
            timestamp=time.time(),
            priority=EventPriority.HIGH,  # High priority for payments
            correlation_id=order['order_id']
        )
        
        event_bus.publish(payment_event)
        
        # 3. Simulate order cancellation for one order
        if order['order_id'] == 'ORD_002':
            time.sleep(0.2)
            
            cancel_event = Event(
                event_id=f"{order['order_id']}_CANCELLED_{int(time.time() * 1000)}",
                event_type="ORDER_CANCELLED",
                source="OrderService",
                data={
                    'order_id': order['order_id'],
                    'customer_id': order['customer_id'],
                    'reason': 'Customer requested cancellation'
                },
                timestamp=time.time(),
                priority=EventPriority.HIGH,
                correlation_id=order['order_id']
            )
            
            event_bus.publish(cancel_event)
        
        time.sleep(0.5)  # Delay between orders
    
    # Wait for all events to be processed
    logger.info("⏳ Waiting for all events to be processed...")
    time.sleep(3)
    
    # Show results
    stats = event_bus.get_statistics()
    
    logger.info("\n📊 Event Bus Statistics:")
    logger.info(f"Events published: {stats['events_published']}")
    logger.info(f"Events processed: {stats['events_processed']}")
    logger.info(f"Events failed: {stats['events_failed']}")
    logger.info(f"Dead letter queue: {stats['dead_letter_queue_size']}")
    logger.info(f"Active subscriptions: {stats['active_subscriptions']}")
    logger.info(f"Queue size: {stats['queue_size']}")
    
    # Show handler statistics
    logger.info("\n🎭 Handler Statistics:")
    for handler_id, handler_stats in stats['subscription_stats'].items():
        logger.info(f"  {handler_id}:")
        logger.info(f"    Processed: {handler_stats['processed_count']}")
        logger.info(f"    Errors: {handler_stats['error_count']}")
        logger.info(f"    Event types: {handler_stats['event_types']}")
    
    # Show processed orders
    logger.info(f"\n📦 Processed Orders:")
    for order_id, order_info in order_handler.processed_orders.items():
        logger.info(f"  {order_id}: {order_info['status']} - ₹{order_info['total_amount']:.2f}")
    
    # Show processed payments
    logger.info(f"\n💰 Processed Payments:")
    for payment_id, payment_info in payment_handler.processed_payments.items():
        logger.info(f"  {payment_id}: {payment_info['status']} - ₹{payment_info['amount']:.2f}")
    
    # Show notifications sent
    logger.info(f"\n📱 Notifications Sent: {len(notification_handler.sent_notifications)}")
    for notification in notification_handler.sent_notifications[-5:]:  # Last 5
        logger.info(f"  To {notification['recipient']}: {notification['message']}")
    
    # Show dead letter events
    dead_letters = event_bus.get_dead_letter_events()
    if dead_letters:
        logger.info(f"\n💀 Dead Letter Events: {len(dead_letters)}")
        for event in dead_letters:
            logger.info(f"  {event.event_id}: {event.event_type} (retries: {event.retry_count})")
    
    # Cleanup
    event_bus.stop()

if __name__ == "__main__":
    try:
        simulate_zomato_order_events()
        logger.info("\n🎉 Zomato Event Bus simulation completed successfully!")
    except KeyboardInterrupt:
        logger.info("\nSimulation interrupted by user")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()
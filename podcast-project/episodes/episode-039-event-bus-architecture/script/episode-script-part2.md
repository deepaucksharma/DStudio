# Episode 39: Event Bus Architecture - Part 2: Implementation Strategies
## Hindi Tech Podcast Series - Advanced Routing & Message Delivery

**Duration:** 60 minutes | **Target:** 7,000+ words | **Difficulty:** Expert
**Mumbai Style:** From Dadar junction routing to enterprise event routing

---

## Opening: The Dadar Junction Story

"Arre yaar, Dadar junction ko dekha hai? Mumbai ka sabse complex railway junction - Western Railway, Central Railway, aur Harbour Line ka meetup point! Har minute mein 15-20 trains different platforms pe aa-jaa rahi hain. Koi Pune ja rahi hai, koi Nashik, koi CST, koi Borivali."

"Lekin magic yeh hai - koi train galat platform pe nahi jaati! Kyu? Kyunki sophisticated routing system hai. Signals hai, pointsmen hai, computerized switching system hai. Har train ko pata hai uska route kya hai, timing kya hai, priority kya hai."

"Yahi exact system hai Event Bus mein! Message routing, filtering, priority handling - sab kuch Mumbai railways ki tarah precision se kaam karta hai. Aaj Part 2 mein hum yeh sab detail mein samjhenge."

---

## Chapter 1: Advanced Message Routing Strategies

### 1.1 Topic-Based Routing (Platform-Based System)

"Mumbai mein har platform ka apna purpose hai - Platform 1 pe slow locals, Platform 2 pe fast trains. Event Bus mein bhi har topic ka apna purpose hota hai!"

**Topic Hierarchy Design:**

```python
class MumbaiTopicRouter:
    """
    Topic-based routing like Mumbai Railway platforms
    """
    
    def __init__(self):
        self.topic_hierarchy = {
            # User domain topics
            'user.registration': ['analytics', 'email', 'crm'],
            'user.profile.updated': ['personalization', 'recommendations'],
            'user.subscription.changed': ['billing', 'feature-access', 'analytics'],
            
            # Order domain topics  
            'order.created': ['inventory', 'payment', 'analytics', 'restaurant'],
            'order.confirmed': ['delivery', 'customer-notification', 'analytics'],
            'order.cancelled': ['refund', 'inventory-restore', 'analytics'],
            
            # Payment domain topics
            'payment.initiated': ['fraud-detection', 'analytics'],
            'payment.completed': ['order-fulfillment', 'accounting', 'customer-notification'],
            'payment.failed': ['retry-service', 'customer-notification', 'analytics'],
            
            # Delivery domain topics
            'delivery.assigned': ['delivery-partner', 'customer-tracking', 'analytics'],
            'delivery.completed': ['rating-system', 'payment-release', 'analytics'],
            'delivery.delayed': ['customer-notification', 'escalation-service']
        }
        
        # Topic configuration
        self.topic_configs = {
            'user.registration': {
                'retention_hours': 72,
                'partitions': 3,
                'priority': 'medium',
                'schema_validation': True
            },
            'payment.completed': {
                'retention_hours': 168,  # 7 days for audit
                'partitions': 10,        # High throughput
                'priority': 'high',
                'schema_validation': True,
                'encryption': True
            },
            'delivery.assigned': {
                'retention_hours': 24,
                'partitions': 5,
                'priority': 'high',
                'schema_validation': True
            }
        }
    
    def route_event(self, event_type: str, event_data: dict) -> list:
        """Route event to appropriate topics"""
        
        # Primary topic from event type
        primary_topic = event_type.lower().replace('_', '.')
        
        # Get subscribers for this topic
        subscribers = self.topic_hierarchy.get(primary_topic, [])
        
        # Apply routing rules
        return self.apply_routing_rules(primary_topic, event_data, subscribers)
    
    def apply_routing_rules(self, topic: str, data: dict, base_subscribers: list) -> list:
        """Apply business logic routing rules"""
        
        final_subscribers = list(base_subscribers)
        
        # Business rule: High-value orders get special treatment
        if topic == 'order.created' and data.get('amount', 0) > 5000:
            final_subscribers.extend(['high-value-handler', 'fraud-detection'])
        
        # Business rule: International orders need currency conversion
        if topic == 'order.created' and data.get('currency') != 'INR':
            final_subscribers.append('currency-converter')
        
        # Business rule: Premium customers get priority processing
        customer_tier = data.get('customer_tier', 'regular')
        if customer_tier == 'premium':
            final_subscribers.append('premium-handler')
        
        # Remove duplicates
        return list(set(final_subscribers))

# Swiggy-style implementation
class SwiggyTopicRouter(MumbaiTopicRouter):
    """
    Swiggy's food delivery routing system
    """
    
    def __init__(self):
        super().__init__()
        
        # Swiggy-specific topics
        self.topic_hierarchy.update({
            'restaurant.menu.updated': ['search-index', 'recommendations', 'cache-invalidation'],
            'restaurant.online': ['availability-service', 'search-visibility'],
            'restaurant.offline': ['order-prevention', 'customer-notification'],
            
            'delivery.partner.online': ['assignment-engine', 'capacity-planning'],
            'delivery.partner.offline': ['reassignment-engine', 'capacity-adjustment'],
            
            'surge.pricing.activated': ['pricing-engine', 'customer-notification'],
            'weather.alert': ['delivery-planning', 'eta-adjustment']
        })
    
    def apply_swiggy_routing_rules(self, topic: str, data: dict, base_subscribers: list) -> list:
        """Swiggy-specific routing logic"""
        
        subscribers = self.apply_routing_rules(topic, data, base_subscribers)
        
        # Monsoon routing
        if data.get('weather_condition') == 'heavy_rain':
            if topic.startswith('delivery.'):
                subscribers.extend(['monsoon-planning', 'safety-alerts'])
        
        # Peak hour routing
        current_hour = datetime.now().hour
        if 12 <= current_hour <= 14 or 19 <= current_hour <= 21:  # Lunch/Dinner
            if topic == 'order.created':
                subscribers.append('peak-hour-optimizer')
        
        # City-specific routing
        city = data.get('delivery_city', '').lower()
        if city == 'mumbai':
            subscribers.extend(['mumbai-local-handler', 'traffic-optimizer'])
        elif city == 'delhi':
            subscribers.extend(['delhi-metro-handler', 'pollution-tracker'])
        
        return list(set(subscribers))
```

### 1.2 Content-Based Routing (Smart Signal System)

"Mumbai signals intelligent hain - train ka type dekh kar decision lete hain. Fast train hai ya slow, passenger train hai ya goods. Content-based routing bhi yahi karta hai!"

**Intelligent Content Filtering:**

```python
import json
from typing import Dict, Any, List, Callable
from dataclasses import dataclass

@dataclass
class RoutingRule:
    name: str
    condition: Callable[[dict], bool]
    subscribers: List[str]
    priority: int = 1

class ContentBasedRouter:
    """
    Smart content-based message routing
    Like Mumbai railway signals making decisions
    """
    
    def __init__(self):
        self.routing_rules = []
        self.default_subscribers = []
        self.setup_paytm_rules()
    
    def setup_paytm_rules(self):
        """Setup Paytm-style routing rules"""
        
        # High-value transaction routing
        self.add_rule(
            name="high_value_payments",
            condition=lambda data: data.get('amount', 0) > 50000,
            subscribers=['risk-management', 'manual-review', 'high-value-processor'],
            priority=10
        )
        
        # International transaction routing
        self.add_rule(
            name="international_payments", 
            condition=lambda data: data.get('currency', 'INR') != 'INR',
            subscribers=['forex-handler', 'compliance-check', 'international-processor'],
            priority=9
        )
        
        # UPI transaction routing
        self.add_rule(
            name="upi_transactions",
            condition=lambda data: data.get('payment_method') == 'upi',
            subscribers=['upi-processor', 'npci-reporting', 'instant-settlement'],
            priority=8
        )
        
        # Merchant payment routing
        self.add_rule(
            name="merchant_payments",
            condition=lambda data: data.get('transaction_type') == 'merchant_payment',
            subscribers=['merchant-settlement', 'commission-calculator', 'tax-handler'],
            priority=7
        )
        
        # Failed transaction routing  
        self.add_rule(
            name="failed_transactions",
            condition=lambda data: data.get('status') == 'failed',
            subscribers=['retry-engine', 'failure-analysis', 'customer-support'],
            priority=6
        )
        
        # Suspicious activity routing
        self.add_rule(
            name="suspicious_activity", 
            condition=self.is_suspicious_transaction,
            subscribers=['fraud-detection', 'risk-analysis', 'security-team'],
            priority=10
        )
        
        # Late night transaction routing
        self.add_rule(
            name="late_night_transactions",
            condition=self.is_late_night_transaction,
            subscribers=['enhanced-monitoring', 'fraud-check'],
            priority=5
        )
    
    def add_rule(self, name: str, condition: Callable, subscribers: List[str], priority: int = 1):
        """Add new routing rule"""
        rule = RoutingRule(name, condition, subscribers, priority)
        self.routing_rules.append(rule)
        
        # Sort by priority (higher priority first)
        self.routing_rules.sort(key=lambda r: r.priority, reverse=True)
    
    def route_message(self, event_data: dict) -> Dict[str, Any]:
        """Route message based on content"""
        
        all_subscribers = set(self.default_subscribers)
        matched_rules = []
        
        # Apply routing rules in priority order
        for rule in self.routing_rules:
            try:
                if rule.condition(event_data):
                    all_subscribers.update(rule.subscribers)
                    matched_rules.append(rule.name)
                    print(f"🎯 Rule matched: {rule.name} -> {rule.subscribers}")
                    
            except Exception as e:
                print(f"❌ Error in rule {rule.name}: {e}")
        
        routing_result = {
            'subscribers': list(all_subscribers),
            'matched_rules': matched_rules,
            'total_subscribers': len(all_subscribers)
        }
        
        return routing_result
    
    def is_suspicious_transaction(self, data: dict) -> bool:
        """Detect suspicious transaction patterns"""
        
        # Multiple rapid transactions
        if data.get('transactions_last_hour', 0) > 10:
            return True
        
        # Unusual amount for user
        amount = data.get('amount', 0)
        user_avg = data.get('user_avg_transaction', 1000)
        if amount > user_avg * 10:  # 10x normal amount
            return True
        
        # Geographic anomaly
        user_city = data.get('user_usual_city', '').lower()
        transaction_city = data.get('transaction_city', '').lower()
        if user_city and transaction_city and user_city != transaction_city:
            # Check distance between cities (simplified)
            if self.cities_distance(user_city, transaction_city) > 500:  # km
                return True
        
        # Time-based anomaly
        if self.is_unusual_time_for_user(data):
            return True
        
        return False
    
    def is_late_night_transaction(self, data: dict) -> bool:
        """Check if transaction is happening late at night"""
        from datetime import datetime
        
        current_hour = datetime.now().hour
        return 23 <= current_hour or current_hour <= 5
    
    def cities_distance(self, city1: str, city2: str) -> int:
        """Calculate distance between cities (mock implementation)"""
        city_distances = {
            ('mumbai', 'delhi'): 1400,
            ('mumbai', 'bangalore'): 1000,
            ('mumbai', 'pune'): 150,
            ('delhi', 'bangalore'): 2000,
            ('delhi', 'kolkata'): 1500
        }
        
        key = tuple(sorted([city1, city2]))
        return city_distances.get(key, 0)
    
    def is_unusual_time_for_user(self, data: dict) -> bool:
        """Check if transaction time is unusual for user"""
        current_hour = datetime.now().hour
        user_usual_hours = data.get('user_usual_transaction_hours', [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
        
        return current_hour not in user_usual_hours

# Usage example
def demo_content_routing():
    router = ContentBasedRouter()
    
    # Test different transaction scenarios
    test_transactions = [
        {
            'transaction_id': 'TXN001',
            'amount': 75000,  # High value
            'currency': 'INR',
            'payment_method': 'upi',
            'user_id': 'USER123',
            'user_avg_transaction': 2000
        },
        {
            'transaction_id': 'TXN002', 
            'amount': 500,
            'currency': 'USD',  # International
            'payment_method': 'card',
            'user_id': 'USER456'
        },
        {
            'transaction_id': 'TXN003',
            'amount': 25000,  # Suspicious - 10x normal
            'currency': 'INR',
            'payment_method': 'wallet',
            'user_id': 'USER789',
            'user_avg_transaction': 2000,
            'transactions_last_hour': 15,  # Too many transactions
            'user_usual_city': 'mumbai',
            'transaction_city': 'delhi'     # Different city
        }
    ]
    
    print("💳 Paytm Content-Based Routing Demo")
    print("=" * 50)
    
    for txn in test_transactions:
        print(f"\n🔍 Processing Transaction: {txn['transaction_id']}")
        print(f"   Amount: ₹{txn['amount']} {txn.get('currency', 'INR')}")
        print(f"   Method: {txn['payment_method']}")
        
        result = router.route_message(txn)
        
        print(f"   📍 Matched Rules: {', '.join(result['matched_rules'])}")
        print(f"   📨 Subscribers: {result['total_subscribers']} services")
        for subscriber in result['subscribers'][:5]:  # Show first 5
            print(f"      - {subscriber}")
        if len(result['subscribers']) > 5:
            print(f"      ... and {len(result['subscribers']) - 5} more")

if __name__ == "__main__":
    demo_content_routing()
```

### 1.3 Header-Based Routing (Train Classification System)

"Mumbai mein train ka classification hota hai - Local, Express, Mail, Freight. Header information se pata chal jaata hai kaun si train hai. Event Bus mein bhi header-based routing karte hain!"

```python
class HeaderBasedRouter:
    """
    Route messages based on headers/metadata
    Like Mumbai train classification system
    """
    
    def __init__(self):
        self.routing_tables = {
            # Route by source service
            'source_routing': {
                'user-service': ['user-analytics', 'crm-system'],
                'payment-service': ['accounting', 'audit-service', 'risk-management'],
                'order-service': ['inventory', 'fulfillment', 'analytics'],
                'delivery-service': ['logistics', 'tracking', 'customer-notification']
            },
            
            # Route by priority
            'priority_routing': {
                'critical': ['primary-processors', 'immediate-alerts'],
                'high': ['priority-queue', 'expedited-processing'],
                'medium': ['standard-queue'],
                'low': ['batch-processing', 'background-queue']
            },
            
            # Route by customer tier
            'customer_tier_routing': {
                'premium': ['premium-support', 'priority-processing', 'enhanced-features'],
                'gold': ['priority-processing', 'standard-features'], 
                'silver': ['standard-processing', 'basic-features'],
                'regular': ['standard-processing']
            },
            
            # Route by region
            'region_routing': {
                'mumbai': ['mumbai-processors', 'maharashtra-compliance'],
                'delhi': ['delhi-processors', 'delhi-compliance'],
                'bangalore': ['bangalore-processors', 'karnataka-compliance'],
                'international': ['international-processors', 'forex-handlers', 'compliance-global']
            },
            
            # Route by event version
            'version_routing': {
                'v1': ['legacy-processors'],
                'v2': ['current-processors'],
                'v3': ['beta-processors']
            }
        }
    
    def route_by_headers(self, event_headers: dict, event_data: dict) -> list:
        """Route event based on headers"""
        
        all_subscribers = set()
        routing_decisions = []
        
        # Source-based routing
        source = event_headers.get('source', 'unknown')
        if source in self.routing_tables['source_routing']:
            subscribers = self.routing_tables['source_routing'][source]
            all_subscribers.update(subscribers)
            routing_decisions.append(f"source:{source} -> {subscribers}")
        
        # Priority-based routing
        priority = event_headers.get('priority', 'medium')
        if priority in self.routing_tables['priority_routing']:
            subscribers = self.routing_tables['priority_routing'][priority]
            all_subscribers.update(subscribers)
            routing_decisions.append(f"priority:{priority} -> {subscribers}")
        
        # Customer tier routing
        customer_tier = event_headers.get('customer_tier') or event_data.get('customer_tier')
        if customer_tier and customer_tier in self.routing_tables['customer_tier_routing']:
            subscribers = self.routing_tables['customer_tier_routing'][customer_tier]
            all_subscribers.update(subscribers)
            routing_decisions.append(f"tier:{customer_tier} -> {subscribers}")
        
        # Region-based routing
        region = event_headers.get('region') or self.detect_region(event_data)
        if region and region in self.routing_tables['region_routing']:
            subscribers = self.routing_tables['region_routing'][region]
            all_subscribers.update(subscribers)
            routing_decisions.append(f"region:{region} -> {subscribers}")
        
        # Version-based routing
        version = event_headers.get('schema_version', 'v2')
        if version in self.routing_tables['version_routing']:
            subscribers = self.routing_tables['version_routing'][version]
            all_subscribers.update(subscribers)
            routing_decisions.append(f"version:{version} -> {subscribers}")
        
        return {
            'subscribers': list(all_subscribers),
            'routing_decisions': routing_decisions,
            'headers_used': list(event_headers.keys())
        }
    
    def detect_region(self, event_data: dict) -> str:
        """Detect region from event data"""
        
        # Check explicit region field
        if 'region' in event_data:
            return event_data['region']
        
        # Detect from phone number
        phone = event_data.get('phone', '')
        if phone.startswith('+91'):
            # Indian phone number - determine city/region
            return 'mumbai'  # Simplified
        
        # Detect from address
        address = event_data.get('address', {})
        city = address.get('city', '').lower()
        if city in ['mumbai', 'pune', 'nashik']:
            return 'mumbai'
        elif city in ['delhi', 'gurgaon', 'noida']:
            return 'delhi'
        elif city in ['bangalore', 'mysore']:
            return 'bangalore'
        
        # Detect from currency
        currency = event_data.get('currency', 'INR')
        if currency != 'INR':
            return 'international'
        
        return 'mumbai'  # Default

# IRCTC booking system example
class IRCTCHeaderRouter(HeaderBasedRouter):
    """
    IRCTC-specific header-based routing
    """
    
    def __init__(self):
        super().__init__()
        
        # Add IRCTC-specific routing
        self.routing_tables.update({
            'train_type_routing': {
                'rajdhani': ['premium-booking', 'catering-premium', 'priority-confirmation'],
                'shatabdi': ['premium-booking', 'catering-premium'],
                'duronto': ['express-booking', 'limited-stops'],
                'mail': ['standard-booking', 'general-processing'],
                'passenger': ['standard-booking', 'unreserved-handling']
            },
            
            'booking_class_routing': {
                '1A': ['first-class-service', 'premium-amenities'],
                '2A': ['second-ac-service'],
                '3A': ['third-ac-service'],
                'SL': ['sleeper-service'],
                'CC': ['chair-car-service'],
                '2S': ['second-sitting-service']
            },
            
            'quota_routing': {
                'GENERAL': ['general-quota-processing'],
                'LADIES': ['ladies-quota-processing', 'safety-measures'],
                'SENIOR_CITIZEN': ['senior-citizen-benefits', 'assistance-services'],
                'TATKAL': ['tatkal-processing', 'premium-charges', 'instant-confirmation'],
                'PREMIUM_TATKAL': ['premium-tatkal-processing', 'highest-priority']
            }
        })
    
    def route_irctc_booking(self, booking_headers: dict, booking_data: dict) -> dict:
        """Route IRCTC booking based on train and passenger details"""
        
        # Get base routing
        base_routing = self.route_by_headers(booking_headers, booking_data)
        all_subscribers = set(base_routing['subscribers'])
        routing_decisions = list(base_routing['routing_decisions'])
        
        # Train type routing
        train_type = booking_headers.get('train_type', booking_data.get('train_type', 'mail'))
        if train_type in self.routing_tables['train_type_routing']:
            subscribers = self.routing_tables['train_type_routing'][train_type]
            all_subscribers.update(subscribers)
            routing_decisions.append(f"train_type:{train_type} -> {subscribers}")
        
        # Booking class routing
        booking_class = booking_data.get('class', 'SL')
        if booking_class in self.routing_tables['booking_class_routing']:
            subscribers = self.routing_tables['booking_class_routing'][booking_class]
            all_subscribers.update(subscribers)
            routing_decisions.append(f"class:{booking_class} -> {subscribers}")
        
        # Quota routing
        quota = booking_data.get('quota', 'GENERAL')
        if quota in self.routing_tables['quota_routing']:
            subscribers = self.routing_tables['quota_routing'][quota]
            all_subscribers.update(subscribers)
            routing_decisions.append(f"quota:{quota} -> {subscribers}")
        
        # Special conditions
        passenger_age = booking_data.get('passenger_age', 30)
        if passenger_age >= 60:
            all_subscribers.add('senior-citizen-concession')
            routing_decisions.append("age:senior -> senior-citizen-concession")
        
        # Distance-based routing
        distance = booking_data.get('distance_km', 0)
        if distance > 1000:
            all_subscribers.add('long-distance-service')
            routing_decisions.append("distance:long -> long-distance-service")
        
        return {
            'subscribers': list(all_subscribers),
            'routing_decisions': routing_decisions,
            'booking_type': self.classify_booking(booking_headers, booking_data)
        }
    
    def classify_booking(self, headers: dict, data: dict) -> str:
        """Classify booking type for optimization"""
        
        train_type = headers.get('train_type', data.get('train_type', 'mail'))
        quota = data.get('quota', 'GENERAL')
        booking_class = data.get('class', 'SL')
        
        # Priority classification
        if quota in ['PREMIUM_TATKAL', 'TATKAL']:
            return 'urgent'
        elif train_type in ['rajdhani', 'shatabdi'] or booking_class in ['1A', '2A']:
            return 'premium'
        elif quota == 'LADIES' or data.get('passenger_age', 30) >= 60:
            return 'priority'
        else:
            return 'standard'

# Demo IRCTC routing
def demo_irctc_routing():
    router = IRCTCHeaderRouter()
    
    # Test booking scenarios
    test_bookings = [
        {
            'headers': {
                'source': 'irctc-booking-service',
                'priority': 'critical',
                'train_type': 'rajdhani',
                'region': 'mumbai'
            },
            'data': {
                'booking_id': 'BOOK001',
                'train_number': '12951',
                'class': '1A',
                'quota': 'TATKAL',
                'passenger_age': 45,
                'distance_km': 1400,
                'customer_tier': 'premium'
            }
        },
        {
            'headers': {
                'source': 'irctc-booking-service',
                'priority': 'medium',
                'train_type': 'passenger',
                'region': 'delhi'
            },
            'data': {
                'booking_id': 'BOOK002',
                'train_number': '59028',
                'class': '2S',
                'quota': 'SENIOR_CITIZEN',
                'passenger_age': 65,
                'distance_km': 150,
                'customer_tier': 'regular'
            }
        }
    ]
    
    print("🚂 IRCTC Header-Based Routing Demo")
    print("=" * 50)
    
    for booking in test_bookings:
        print(f"\n🎫 Processing Booking: {booking['data']['booking_id']}")
        print(f"   Train: {booking['data']['train_number']} ({booking['headers']['train_type']})")
        print(f"   Class: {booking['data']['class']} | Quota: {booking['data']['quota']}")
        
        result = router.route_irctc_booking(booking['headers'], booking['data'])
        
        print(f"   📋 Booking Type: {result['booking_type']}")
        print(f"   📨 Subscribers: {len(result['subscribers'])} services")
        
        # Show routing decisions
        print("   🎯 Routing Decisions:")
        for decision in result['routing_decisions'][:5]:
            print(f"      - {decision}")
        
        if len(result['routing_decisions']) > 5:
            print(f"      ... and {len(result['routing_decisions']) - 5} more")

if __name__ == "__main__":
    demo_irctc_routing()
```

## Chapter 2: Message Filtering & Transformation

### 2.1 Event Filtering (Mumbai Local Passenger Filter)

"Mumbai Local mein announcement hota hai - 'Next train is for Virar. Passengers for Andheri, Bandra, Khar please board.' Yeh filtering hai - sirf relevant passengers ko inform karna!"

```python
from typing import Dict, List, Callable
import re
import json

class EventFilter:
    """
    Mumbai Local style event filtering
    Only relevant events reach subscribers
    """
    
    def __init__(self):
        self.filters = {}
        self.global_filters = []
        self.setup_zomato_filters()
    
    def setup_zomato_filters(self):
        """Setup Zomato-specific filters"""
        
        # Restaurant filters
        self.add_subscriber_filter(
            'restaurant-service',
            lambda event: event.get('event_type', '').startswith('RESTAURANT_') or
                         event.get('data', {}).get('restaurant_id') is not None
        )
        
        # Delivery partner filters
        self.add_subscriber_filter(
            'delivery-service',
            lambda event: event.get('event_type', '').startswith('DELIVERY_') or
                         event.get('data', {}).get('delivery_partner_id') is not None
        )
        
        # Customer notification filters
        self.add_subscriber_filter(
            'customer-notification',
            lambda event: event.get('event_type') in [
                'ORDER_PLACED', 'ORDER_CONFIRMED', 'ORDER_CANCELLED',
                'DELIVERY_ASSIGNED', 'DELIVERY_COMPLETED', 'PAYMENT_FAILED'
            ]
        )
        
        # Analytics filters (almost everything)
        self.add_subscriber_filter(
            'analytics',
            lambda event: True  # Analytics wants all events
        )
        
        # High-value order filters
        self.add_subscriber_filter(
            'high-value-processor',
            lambda event: (
                event.get('event_type') == 'ORDER_PLACED' and
                event.get('data', {}).get('total_amount', 0) > 2000
            )
        )
        
        # Geographic filters
        self.add_subscriber_filter(
            'mumbai-regional-service',
            lambda event: self.is_mumbai_event(event)
        )
        
        # Time-based filters
        self.add_subscriber_filter(
            'peak-hour-service',
            lambda event: self.is_peak_hour_event(event)
        )
    
    def add_subscriber_filter(self, subscriber: str, filter_func: Callable):
        """Add filter for specific subscriber"""
        self.filters[subscriber] = filter_func
    
    def add_global_filter(self, filter_func: Callable):
        """Add filter that applies to all events"""
        self.global_filters.append(filter_func)
    
    def filter_event_for_subscriber(self, event: Dict, subscriber: str) -> bool:
        """Check if event should be sent to subscriber"""
        
        # Apply global filters first
        for global_filter in self.global_filters:
            if not global_filter(event):
                return False
        
        # Apply subscriber-specific filter
        if subscriber in self.filters:
            return self.filters[subscriber](event)
        
        # Default: send to all if no specific filter
        return True
    
    def filter_subscribers_for_event(self, event: Dict, subscribers: List[str]) -> List[str]:
        """Filter list of subscribers for an event"""
        
        filtered_subscribers = []
        
        for subscriber in subscribers:
            if self.filter_event_for_subscriber(event, subscriber):
                filtered_subscribers.append(subscriber)
                print(f"✅ {subscriber} will receive {event.get('event_type')}")
            else:
                print(f"❌ {subscriber} filtered out for {event.get('event_type')}")
        
        return filtered_subscribers
    
    def is_mumbai_event(self, event: Dict) -> bool:
        """Check if event is related to Mumbai"""
        data = event.get('data', {})
        
        # Check delivery address
        address = data.get('delivery_address', {})
        city = address.get('city', '').lower()
        if city in ['mumbai', 'bombay']:
            return True
        
        # Check restaurant location
        restaurant_location = data.get('restaurant_location', {})
        restaurant_city = restaurant_location.get('city', '').lower()
        if restaurant_city in ['mumbai', 'bombay']:
            return True
        
        # Check pincode
        pincode = address.get('pincode', '')
        if pincode.startswith('40'):  # Mumbai pincodes start with 40
            return True
        
        return False
    
    def is_peak_hour_event(self, event: Dict) -> bool:
        """Check if event occurred during peak hours"""
        from datetime import datetime
        
        current_hour = datetime.now().hour
        
        # Lunch peak: 12-2 PM
        # Dinner peak: 7-9 PM
        return (12 <= current_hour <= 14) or (19 <= current_hour <= 21)

# Advanced filtering with schema validation
class SchemaBasedFilter(EventFilter):
    """
    Schema-based event filtering
    Ensures data quality and structure
    """
    
    def __init__(self):
        super().__init__()
        self.schemas = {
            'ORDER_PLACED': {
                'required_fields': ['order_id', 'customer_id', 'restaurant_id', 'total_amount'],
                'field_types': {
                    'order_id': str,
                    'customer_id': str,
                    'restaurant_id': str,
                    'total_amount': (int, float)
                },
                'field_validations': {
                    'total_amount': lambda x: x > 0,
                    'order_id': lambda x: len(x) > 5
                }
            },
            'PAYMENT_PROCESSED': {
                'required_fields': ['payment_id', 'amount', 'status', 'payment_method'],
                'field_types': {
                    'payment_id': str,
                    'amount': (int, float),
                    'status': str,
                    'payment_method': str
                },
                'field_validations': {
                    'amount': lambda x: x > 0,
                    'status': lambda x: x in ['success', 'failed', 'pending'],
                    'payment_method': lambda x: x in ['upi', 'card', 'wallet', 'netbanking']
                }
            }
        }
        
        # Add schema validation as global filter
        self.add_global_filter(self.validate_event_schema)
    
    def validate_event_schema(self, event: Dict) -> bool:
        """Validate event against its schema"""
        event_type = event.get('event_type')
        data = event.get('data', {})
        
        if event_type not in self.schemas:
            return True  # No schema defined, allow through
        
        schema = self.schemas[event_type]
        
        # Check required fields
        for field in schema['required_fields']:
            if field not in data:
                print(f"❌ Schema validation failed: missing field '{field}' in {event_type}")
                return False
        
        # Check field types
        for field, expected_type in schema['field_types'].items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    print(f"❌ Schema validation failed: '{field}' should be {expected_type}")
                    return False
        
        # Check field validations
        for field, validation in schema['field_validations'].items():
            if field in data:
                try:
                    if not validation(data[field]):
                        print(f"❌ Schema validation failed: '{field}' validation failed")
                        return False
                except Exception as e:
                    print(f"❌ Schema validation error for '{field}': {e}")
                    return False
        
        return True

# Demo filtering system
def demo_event_filtering():
    filter_system = SchemaBasedFilter()
    
    # Test events
    test_events = [
        {
            'event_type': 'ORDER_PLACED',
            'timestamp': '2025-01-10T12:30:00Z',
            'data': {
                'order_id': 'ORD12345',
                'customer_id': 'CUST001',
                'restaurant_id': 'REST_TRISHNA_MUMBAI',
                'total_amount': 850,
                'delivery_address': {
                    'city': 'mumbai',
                    'pincode': '400050'
                },
                'items': ['Butter Chicken', 'Naan']
            }
        },
        {
            'event_type': 'ORDER_PLACED',
            'timestamp': '2025-01-10T15:30:00Z',
            'data': {
                'order_id': 'ORD12346',
                'customer_id': 'CUST002',
                'restaurant_id': 'REST_INDIA_GATE_DELHI',
                'total_amount': 450,
                'delivery_address': {
                    'city': 'delhi',
                    'pincode': '110001'
                },
                'items': ['Dal Makhani']
            }
        },
        {
            'event_type': 'PAYMENT_PROCESSED',
            'timestamp': '2025-01-10T12:31:00Z',
            'data': {
                'payment_id': 'PAY001',
                'amount': 850,
                'status': 'success',
                'payment_method': 'upi'
            }
        },
        {
            'event_type': 'ORDER_PLACED',  # Invalid event - missing required fields
            'timestamp': '2025-01-10T12:35:00Z',
            'data': {
                'order_id': 'ORD12347',
                # missing customer_id, restaurant_id, total_amount
                'items': ['Pizza']
            }
        }
    ]
    
    # Subscribers
    subscribers = [
        'restaurant-service',
        'delivery-service', 
        'customer-notification',
        'analytics',
        'mumbai-regional-service',
        'peak-hour-service',
        'high-value-processor'
    ]
    
    print("🔍 Zomato Event Filtering Demo")
    print("=" * 50)
    
    for i, event in enumerate(test_events):
        print(f"\n📨 Event {i+1}: {event['event_type']}")
        print(f"   Timestamp: {event['timestamp']}")
        
        # Show event data
        data = event.get('data', {})
        if 'total_amount' in data:
            print(f"   Amount: ₹{data['total_amount']}")
        if 'delivery_address' in data:
            city = data['delivery_address'].get('city', 'unknown')
            print(f"   City: {city}")
        
        # Filter subscribers
        filtered_subscribers = filter_system.filter_subscribers_for_event(event, subscribers)
        
        print(f"   📍 Final subscribers: {len(filtered_subscribers)}")
        for subscriber in filtered_subscribers:
            print(f"      ✅ {subscriber}")
        
        # Show rejected subscribers
        rejected = set(subscribers) - set(filtered_subscribers)
        if rejected:
            print(f"   🚫 Rejected subscribers:")
            for subscriber in rejected:
                print(f"      ❌ {subscriber}")

if __name__ == "__main__":
    demo_event_filtering()
```

### 2.2 Message Transformation (Mumbai Announcement Translation)

"Mumbai Local mein announcement Hindi, English, aur Marathi mein hota hai. Different passengers ko different format mein same message milta hai!"

```python
import json
from datetime import datetime
from typing import Dict, Any, List
from abc import ABC, abstractmethod

class MessageTransformer(ABC):
    """Abstract base class for message transformers"""
    
    @abstractmethod
    def transform(self, event: Dict[str, Any]) -> Dict[str, Any]:
        pass

class StandardizationTransformer(MessageTransformer):
    """
    Standardize event format across different sources
    """
    
    def __init__(self):
        self.field_mappings = {
            # Map different field names to standard ones
            'id': 'event_id',
            'type': 'event_type', 
            'timestamp': 'event_timestamp',
            'created_at': 'event_timestamp',
            'user_id': 'customer_id',
            'amount': 'total_amount',
            'price': 'total_amount',
            'status': 'event_status'
        }
        
        self.required_fields = {
            'event_id': lambda: f"evt_{int(datetime.now().timestamp() * 1000)}",
            'event_timestamp': lambda: datetime.now().isoformat(),
            'source': lambda: 'unknown-service'
        }
    
    def transform(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize event format"""
        
        transformed = event.copy()
        
        # Apply field mappings
        for old_field, new_field in self.field_mappings.items():
            if old_field in transformed and new_field not in transformed:
                transformed[new_field] = transformed[old_field]
                # Optionally remove old field
                # del transformed[old_field]
        
        # Add required fields if missing
        for field, default_func in self.required_fields.items():
            if field not in transformed:
                transformed[field] = default_func()
        
        # Ensure data is in 'data' field
        if 'data' not in transformed and 'payload' in transformed:
            transformed['data'] = transformed['payload']
        
        return transformed

class EnrichmentTransformer(MessageTransformer):
    """
    Enrich events with additional context
    """
    
    def __init__(self):
        # Mock databases for enrichment
        self.customer_db = {
            'CUST001': {'name': 'Rahul Sharma', 'tier': 'premium', 'city': 'mumbai'},
            'CUST002': {'name': 'Priya Patel', 'tier': 'gold', 'city': 'delhi'},
            'CUST003': {'name': 'Amit Kumar', 'tier': 'regular', 'city': 'bangalore'}
        }
        
        self.restaurant_db = {
            'REST001': {'name': 'Trishna', 'cuisine': 'seafood', 'rating': 4.5, 'city': 'mumbai'},
            'REST002': {'name': 'Leopold Cafe', 'cuisine': 'continental', 'rating': 4.2, 'city': 'mumbai'},
            'REST003': {'name': 'India Gate', 'cuisine': 'north-indian', 'rating': 4.1, 'city': 'delhi'}
        }
    
    def transform(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich event with additional context"""
        
        enriched = event.copy()
        data = enriched.get('data', {})
        
        # Customer enrichment
        customer_id = data.get('customer_id')
        if customer_id and customer_id in self.customer_db:
            customer_info = self.customer_db[customer_id]
            data['customer_name'] = customer_info['name']
            data['customer_tier'] = customer_info['tier']
            data['customer_city'] = customer_info['city']
        
        # Restaurant enrichment
        restaurant_id = data.get('restaurant_id')
        if restaurant_id and restaurant_id in self.restaurant_db:
            restaurant_info = self.restaurant_db[restaurant_id]
            data['restaurant_name'] = restaurant_info['name']
            data['restaurant_cuisine'] = restaurant_info['cuisine']
            data['restaurant_rating'] = restaurant_info['rating']
            data['restaurant_city'] = restaurant_info['city']
        
        # Geographic enrichment
        if 'customer_city' in data and 'restaurant_city' in data:
            data['is_local_order'] = data['customer_city'] == data['restaurant_city']
        
        # Time-based enrichment
        timestamp = enriched.get('event_timestamp', datetime.now().isoformat())
        event_time = datetime.fromisoformat(timestamp.replace('Z', ''))
        hour = event_time.hour
        
        if 6 <= hour <= 11:
            data['meal_period'] = 'breakfast'
        elif 12 <= hour <= 15:
            data['meal_period'] = 'lunch'
        elif 16 <= hour <= 18:
            data['meal_period'] = 'snacks'
        elif 19 <= hour <= 23:
            data['meal_period'] = 'dinner'
        else:
            data['meal_period'] = 'late-night'
        
        enriched['data'] = data
        
        return enriched

class SubscriberSpecificTransformer(MessageTransformer):
    """
    Transform events specific to subscriber needs
    """
    
    def __init__(self, subscriber_type: str):
        self.subscriber_type = subscriber_type
        self.transformations = {
            'email-service': self.transform_for_email,
            'sms-service': self.transform_for_sms,
            'analytics': self.transform_for_analytics,
            'billing': self.transform_for_billing,
            'customer-app': self.transform_for_customer_app
        }
    
    def transform(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform based on subscriber type"""
        
        if self.subscriber_type in self.transformations:
            return self.transformations[self.subscriber_type](event)
        
        return event  # No transformation needed
    
    def transform_for_email(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform for email service - focus on messaging content"""
        
        email_event = {
            'message_id': event.get('event_id'),
            'template_type': self.get_email_template_type(event),
            'recipient': self.get_customer_email(event),
            'personalization_data': self.extract_email_data(event),
            'priority': self.get_email_priority(event),
            'send_time': event.get('event_timestamp')
        }
        
        return email_event
    
    def transform_for_sms(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform for SMS service - focus on mobile messaging"""
        
        sms_event = {
            'message_id': event.get('event_id'),
            'phone_number': self.get_customer_phone(event),
            'message_template': self.get_sms_template(event),
            'variables': self.extract_sms_variables(event),
            'priority': self.get_sms_priority(event)
        }
        
        return sms_event
    
    def transform_for_analytics(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform for analytics - focus on metrics"""
        
        analytics_event = {
            'event_name': event.get('event_type'),
            'user_id': event.get('data', {}).get('customer_id'),
            'session_id': event.get('correlation_id'),
            'timestamp': event.get('event_timestamp'),
            'properties': self.extract_analytics_properties(event),
            'metrics': self.calculate_metrics(event)
        }
        
        return analytics_event
    
    def transform_for_billing(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform for billing service - focus on financial data"""
        
        data = event.get('data', {})
        
        billing_event = {
            'transaction_id': data.get('order_id') or data.get('payment_id'),
            'amount': data.get('total_amount', 0),
            'currency': data.get('currency', 'INR'),
            'customer_id': data.get('customer_id'),
            'service_charges': self.calculate_service_charges(data),
            'tax_amount': self.calculate_tax(data),
            'billing_period': self.get_billing_period(),
            'revenue_category': self.classify_revenue(event)
        }
        
        return billing_event
    
    def transform_for_customer_app(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform for customer app - focus on UI updates"""
        
        app_event = {
            'notification_type': self.get_notification_type(event),
            'title': self.generate_notification_title(event),
            'body': self.generate_notification_body(event),
            'action_url': self.generate_action_url(event),
            'customer_id': event.get('data', {}).get('customer_id'),
            'priority': self.get_app_priority(event),
            'display_duration': self.get_display_duration(event)
        }
        
        return app_event
    
    # Helper methods
    def get_email_template_type(self, event: Dict) -> str:
        event_type = event.get('event_type', '')
        templates = {
            'ORDER_PLACED': 'order_confirmation',
            'ORDER_DELIVERED': 'delivery_confirmation',
            'PAYMENT_FAILED': 'payment_retry',
            'USER_REGISTERED': 'welcome_email'
        }
        return templates.get(event_type, 'generic')
    
    def get_customer_email(self, event: Dict) -> str:
        # In real implementation, would lookup from customer database
        customer_id = event.get('data', {}).get('customer_id', '')
        return f"{customer_id.lower()}@example.com"
    
    def extract_email_data(self, event: Dict) -> Dict:
        data = event.get('data', {})
        return {
            'customer_name': data.get('customer_name', 'Valued Customer'),
            'order_id': data.get('order_id'),
            'amount': data.get('total_amount'),
            'restaurant_name': data.get('restaurant_name')
        }
    
    def get_email_priority(self, event: Dict) -> str:
        event_type = event.get('event_type', '')
        high_priority_events = ['PAYMENT_FAILED', 'ORDER_CANCELLED']
        return 'high' if event_type in high_priority_events else 'normal'
    
    def get_sms_template(self, event: Dict) -> str:
        event_type = event.get('event_type', '')
        templates = {
            'ORDER_PLACED': 'Your order {order_id} is confirmed! Amount: ₹{amount}',
            'DELIVERY_ASSIGNED': 'Your order is out for delivery. Track: {track_url}',
            'ORDER_DELIVERED': 'Order delivered! Rate your experience.'
        }
        return templates.get(event_type, 'Update about your order {order_id}')
    
    def extract_analytics_properties(self, event: Dict) -> Dict:
        data = event.get('data', {})
        return {
            'restaurant_id': data.get('restaurant_id'),
            'cuisine_type': data.get('restaurant_cuisine'),
            'order_value': data.get('total_amount'),
            'customer_tier': data.get('customer_tier'),
            'meal_period': data.get('meal_period'),
            'is_local_order': data.get('is_local_order')
        }
    
    def calculate_metrics(self, event: Dict) -> Dict:
        data = event.get('data', {})
        amount = data.get('total_amount', 0)
        
        return {
            'revenue': amount,
            'order_count': 1 if event.get('event_type') == 'ORDER_PLACED' else 0,
            'avg_order_value': amount
        }
    
    def calculate_service_charges(self, data: Dict) -> float:
        amount = data.get('total_amount', 0)
        return amount * 0.02  # 2% service charge
    
    def calculate_tax(self, data: Dict) -> float:
        amount = data.get('total_amount', 0)
        return amount * 0.18  # 18% GST
    
    def get_billing_period(self) -> str:
        now = datetime.now()
        return f"{now.year}-{now.month:02d}"
    
    def classify_revenue(self, event: Dict) -> str:
        data = event.get('data', {})
        cuisine = data.get('restaurant_cuisine', '')
        
        if cuisine in ['fast-food', 'pizza', 'burger']:
            return 'quick-service'
        elif cuisine in ['fine-dining', 'continental']:
            return 'premium'
        else:
            return 'standard'

# Complete transformation pipeline
class TransformationPipeline:
    """
    Complete message transformation pipeline
    Like Mumbai Local's multi-step journey processing
    """
    
    def __init__(self):
        self.transformers = []
        self.setup_default_pipeline()
    
    def setup_default_pipeline(self):
        """Setup default transformation pipeline"""
        self.add_transformer(StandardizationTransformer())
        self.add_transformer(EnrichmentTransformer())
    
    def add_transformer(self, transformer: MessageTransformer):
        """Add transformer to pipeline"""
        self.transformers.append(transformer)
    
    def transform_for_subscriber(self, event: Dict[str, Any], subscriber: str) -> Dict[str, Any]:
        """Transform event through complete pipeline for specific subscriber"""
        
        # Apply base transformations
        transformed_event = event
        
        for transformer in self.transformers:
            transformed_event = transformer.transform(transformed_event)
        
        # Apply subscriber-specific transformation
        subscriber_transformer = SubscriberSpecificTransformer(subscriber)
        final_event = subscriber_transformer.transform(transformed_event)
        
        return final_event
    
    def transform_for_multiple_subscribers(self, event: Dict[str, Any], subscribers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Transform event for multiple subscribers"""
        
        results = {}
        
        for subscriber in subscribers:
            results[subscriber] = self.transform_for_subscriber(event, subscriber)
        
        return results

# Demo transformation pipeline
def demo_transformation_pipeline():
    pipeline = TransformationPipeline()
    
    # Raw event from order service
    raw_event = {
        'id': 'order_123',  # Will be standardized to 'event_id'
        'type': 'ORDER_PLACED',  # Will be standardized to 'event_type'
        'created_at': '2025-01-10T12:30:00Z',  # Will be standardized
        'payload': {  # Will be moved to 'data'
            'order_id': 'ORD_456',
            'user_id': 'CUST001',  # Will be standardized to 'customer_id'
            'restaurant_id': 'REST001',
            'amount': 850,  # Will be standardized to 'total_amount'
            'items': ['Butter Chicken', 'Naan', 'Lassi']
        }
    }
    
    subscribers = ['email-service', 'sms-service', 'analytics', 'billing', 'customer-app']
    
    print("🔄 Message Transformation Pipeline Demo")
    print("=" * 50)
    
    print(f"\n📨 Raw Event:")
    print(json.dumps(raw_event, indent=2))
    
    # Transform for all subscribers
    transformed_events = pipeline.transform_for_multiple_subscribers(raw_event, subscribers)
    
    for subscriber, transformed_event in transformed_events.items():
        print(f"\n🎯 Transformed for {subscriber}:")
        print(json.dumps(transformed_event, indent=2)[:500] + "..." if len(json.dumps(transformed_event, indent=2)) > 500 else json.dumps(transformed_event, indent=2))

if __name__ == "__main__":
    demo_transformation_pipeline()
```

## Chapter 3: Message Delivery Guarantees (Mumbai Train Reliability System)

### 3.1 Exactly-Once Delivery Implementation

"Mumbai mein monthly pass ek baar validate karo, phir saare stations pe valid hai. Exactly-once delivery bhi yahi guarantee deta hai!"

```python
import hashlib
import time
import threading
from typing import Dict, Set, Optional
from dataclasses import dataclass, field
from enum import Enum

class DeliveryStatus(Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    DUPLICATE = "duplicate"

@dataclass
class DeliveryRecord:
    message_id: str
    subscriber: str
    attempt_count: int = 0
    status: DeliveryStatus = DeliveryStatus.PENDING
    last_attempt: Optional[float] = None
    delivery_timestamp: Optional[float] = None
    error_message: Optional[str] = None

class ExactlyOnceDeliveryManager:
    """
    Exactly-once delivery guarantee implementation
    Like Mumbai monthly pass validation system
    """
    
    def __init__(self):
        # In-memory delivery tracking (in production, use Redis/Database)
        self.delivery_records: Dict[str, DeliveryRecord] = {}
        self.delivered_messages: Set[str] = set()
        self.lock = threading.Lock()
        
        # Configuration
        self.max_retry_attempts = 3
        self.retry_delay_seconds = [1, 2, 4]  # Exponential backoff
        
    def generate_delivery_key(self, message_id: str, subscriber: str) -> str:
        """Generate unique key for message-subscriber combination"""
        return f"{message_id}::{subscriber}"
    
    def is_already_delivered(self, message_id: str, subscriber: str) -> bool:
        """Check if message already delivered to subscriber"""
        delivery_key = self.generate_delivery_key(message_id, subscriber)
        
        with self.lock:
            record = self.delivery_records.get(delivery_key)
            return record is not None and record.status == DeliveryStatus.DELIVERED
    
    def attempt_delivery(self, message: Dict, subscriber: str, delivery_handler) -> DeliveryStatus:
        """Attempt message delivery with exactly-once guarantee"""
        
        message_id = message.get('event_id', 'unknown')
        delivery_key = self.generate_delivery_key(message_id, subscriber)
        
        # Check if already delivered
        if self.is_already_delivered(message_id, subscriber):
            print(f"🔄 Message {message_id} already delivered to {subscriber}")
            return DeliveryStatus.DUPLICATE
        
        # Get or create delivery record
        with self.lock:
            if delivery_key not in self.delivery_records:
                self.delivery_records[delivery_key] = DeliveryRecord(
                    message_id=message_id,
                    subscriber=subscriber
                )
        
        record = self.delivery_records[delivery_key]
        
        # Attempt delivery with retries
        for attempt in range(self.max_retry_attempts):
            try:
                print(f"📤 Attempting delivery {attempt + 1}/{self.max_retry_attempts}: {message_id} -> {subscriber}")
                
                # Update attempt info
                record.attempt_count = attempt + 1
                record.last_attempt = time.time()
                
                # Call the actual delivery handler
                result = delivery_handler(message, subscriber)
                
                # Mark as delivered
                with self.lock:
                    record.status = DeliveryStatus.DELIVERED
                    record.delivery_timestamp = time.time()
                    self.delivered_messages.add(delivery_key)
                
                print(f"✅ Successfully delivered {message_id} to {subscriber}")
                return DeliveryStatus.DELIVERED
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Delivery attempt {attempt + 1} failed: {error_msg}")
                
                record.error_message = error_msg
                
                # Wait before retry (except on last attempt)
                if attempt < self.max_retry_attempts - 1:
                    delay = self.retry_delay_seconds[min(attempt, len(self.retry_delay_seconds) - 1)]
                    print(f"⏳ Waiting {delay} seconds before retry...")
                    time.sleep(delay)
        
        # All retries exhausted
        with self.lock:
            record.status = DeliveryStatus.FAILED
        
        print(f"💀 Failed to deliver {message_id} to {subscriber} after {self.max_retry_attempts} attempts")
        return DeliveryStatus.FAILED
    
    def get_delivery_stats(self) -> Dict:
        """Get delivery statistics"""
        with self.lock:
            stats = {
                'total_deliveries': len(self.delivery_records),
                'successful_deliveries': 0,
                'failed_deliveries': 0,
                'pending_deliveries': 0,
                'duplicate_attempts': 0
            }
            
            for record in self.delivery_records.values():
                if record.status == DeliveryStatus.DELIVERED:
                    stats['successful_deliveries'] += 1
                elif record.status == DeliveryStatus.FAILED:
                    stats['failed_deliveries'] += 1
                elif record.status == DeliveryStatus.PENDING:
                    stats['pending_deliveries'] += 1
            
            return stats

# At-Least-Once Delivery Implementation
class AtLeastOnceDeliveryManager:
    """
    At-least-once delivery with acknowledgments
    Like Mumbai Local ticket checking system
    """
    
    def __init__(self):
        self.pending_messages: Dict[str, Dict] = {}
        self.acknowledgments: Set[str] = set()
        self.max_pending_time = 30  # seconds
        self.cleanup_interval = 60  # seconds
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_old_messages, daemon=True)
        self.cleanup_thread.start()
    
    def send_with_ack(self, message: Dict, subscriber: str, delivery_handler) -> bool:
        """Send message and wait for acknowledgment"""
        
        message_id = message.get('event_id')
        ack_key = f"{message_id}::{subscriber}"
        
        # Store message as pending
        self.pending_messages[ack_key] = {
            'message': message,
            'subscriber': subscriber,
            'sent_time': time.time(),
            'delivery_handler': delivery_handler
        }
        
        # Attempt delivery
        try:
            result = delivery_handler(message, subscriber)
            
            # Simulate acknowledgment (in real system, subscriber would send ACK)
            self.acknowledge_delivery(message_id, subscriber)
            
            return True
            
        except Exception as e:
            print(f"❌ Delivery failed: {e}")
            return False
    
    def acknowledge_delivery(self, message_id: str, subscriber: str):
        """Acknowledge successful delivery"""
        ack_key = f"{message_id}::{subscriber}"
        self.acknowledgments.add(ack_key)
        
        # Remove from pending
        if ack_key in self.pending_messages:
            del self.pending_messages[ack_key]
            print(f"✅ Acknowledgment received: {message_id} from {subscriber}")
    
    def retry_pending_messages(self):
        """Retry messages that haven't been acknowledged"""
        current_time = time.time()
        retry_keys = []
        
        for ack_key, pending_info in self.pending_messages.items():
            sent_time = pending_info['sent_time']
            
            # Check if message is old enough to retry
            if current_time - sent_time > self.max_pending_time:
                retry_keys.append(ack_key)
        
        for ack_key in retry_keys:
            pending_info = self.pending_messages[ack_key]
            message = pending_info['message']
            subscriber = pending_info['subscriber']
            delivery_handler = pending_info['delivery_handler']
            
            print(f"🔄 Retrying unacknowledged message: {message.get('event_id')} -> {subscriber}")
            
            # Update sent time
            pending_info['sent_time'] = current_time
            
            # Retry delivery
            try:
                delivery_handler(message, subscriber)
            except Exception as e:
                print(f"❌ Retry failed: {e}")
    
    def _cleanup_old_messages(self):
        """Background cleanup of old pending messages"""
        while True:
            time.sleep(self.cleanup_interval)
            
            current_time = time.time()
            old_keys = []
            
            for ack_key, pending_info in self.pending_messages.items():
                # Remove messages older than 5 minutes
                if current_time - pending_info['sent_time'] > 300:
                    old_keys.append(ack_key)
            
            for key in old_keys:
                del self.pending_messages[key]
                print(f"🗑️ Cleaned up old pending message: {key}")

# Paytm Payment Processing with Exactly-Once Delivery
class PaytmExactlyOnceProcessor:
    """
    Paytm payment processing with exactly-once delivery guarantee
    """
    
    def __init__(self):
        self.delivery_manager = ExactlyOnceDeliveryManager()
        self.processed_transactions = set()
        
        # Mock external services
        self.services = {
            'bank-service': self.process_bank_transaction,
            'wallet-service': self.process_wallet_transaction, 
            'notification-service': self.send_notification,
            'analytics-service': self.track_analytics,
            'audit-service': self.audit_transaction
        }
    
    def process_payment_event(self, payment_event: Dict):
        """Process payment event with exactly-once guarantee"""
        
        payment_id = payment_event.get('data', {}).get('payment_id')
        
        # Check if transaction already processed
        if payment_id in self.processed_transactions:
            print(f"💳 Transaction {payment_id} already processed")
            return
        
        print(f"💳 Processing payment event: {payment_id}")
        
        # Deliver to all required services
        subscribers = ['bank-service', 'wallet-service', 'notification-service', 'analytics-service', 'audit-service']
        
        delivery_results = {}
        
        for subscriber in subscribers:
            result = self.delivery_manager.attempt_delivery(
                payment_event, 
                subscriber, 
                self.services[subscriber]
            )
            delivery_results[subscriber] = result
        
        # Mark transaction as processed if all critical services succeeded
        critical_services = ['bank-service', 'wallet-service', 'audit-service']
        critical_success = all(
            delivery_results[service] == DeliveryStatus.DELIVERED 
            for service in critical_services
        )
        
        if critical_success:
            self.processed_transactions.add(payment_id)
            print(f"✅ Payment {payment_id} fully processed")
        else:
            print(f"❌ Payment {payment_id} processing incomplete")
    
    def process_bank_transaction(self, event: Dict, subscriber: str) -> bool:
        """Mock bank service processing"""
        payment_data = event.get('data', {})
        payment_id = payment_data.get('payment_id')
        amount = payment_data.get('amount', 0)
        
        # Simulate random failures (for demo)
        import random
        if random.random() < 0.2:  # 20% failure rate
            raise Exception(f"Bank service temporarily unavailable for {payment_id}")
        
        print(f"   🏦 Bank processed payment {payment_id}: ₹{amount}")
        return True
    
    def process_wallet_transaction(self, event: Dict, subscriber: str) -> bool:
        """Mock wallet service processing"""
        payment_data = event.get('data', {})
        payment_id = payment_data.get('payment_id')
        
        # Simulate processing
        print(f"   💰 Wallet updated for payment {payment_id}")
        return True
    
    def send_notification(self, event: Dict, subscriber: str) -> bool:
        """Mock notification service"""
        payment_data = event.get('data', {})
        customer_id = payment_data.get('customer_id')
        
        print(f"   📱 Notification sent to customer {customer_id}")
        return True
    
    def track_analytics(self, event: Dict, subscriber: str) -> bool:
        """Mock analytics service"""
        print(f"   📊 Analytics tracked for payment")
        return True
    
    def audit_transaction(self, event: Dict, subscriber: str) -> bool:
        """Mock audit service"""
        payment_data = event.get('data', {})
        payment_id = payment_data.get('payment_id')
        
        print(f"   📝 Audit record created for {payment_id}")
        return True
    
    def get_processing_stats(self):
        """Get processing statistics"""
        delivery_stats = self.delivery_manager.get_delivery_stats()
        
        return {
            'total_processed_transactions': len(self.processed_transactions),
            'delivery_stats': delivery_stats
        }

# Demo exactly-once delivery
def demo_exactly_once_delivery():
    processor = PaytmExactlyOnceProcessor()
    
    # Test payment events
    test_payments = [
        {
            'event_id': 'evt_payment_001',
            'event_type': 'PAYMENT_PROCESSED',
            'timestamp': time.time(),
            'data': {
                'payment_id': 'PAY001',
                'customer_id': 'CUST001',
                'amount': 1500,
                'payment_method': 'upi',
                'status': 'success'
            }
        },
        {
            'event_id': 'evt_payment_002', 
            'event_type': 'PAYMENT_PROCESSED',
            'timestamp': time.time(),
            'data': {
                'payment_id': 'PAY002',
                'customer_id': 'CUST002',
                'amount': 2500,
                'payment_method': 'wallet',
                'status': 'success'
            }
        }
    ]
    
    print("💳 Paytm Exactly-Once Delivery Demo")
    print("=" * 50)
    
    for payment in test_payments:
        processor.process_payment_event(payment)
        print()
        time.sleep(1)
    
    # Try processing same payment again (should detect duplicate)
    print("🔄 Attempting duplicate processing...")
    processor.process_payment_event(test_payments[0])
    
    # Show final statistics
    print("\n📊 Final Processing Statistics:")
    stats = processor.get_processing_stats()
    print(f"   Processed Transactions: {stats['total_processed_transactions']}")
    print(f"   Total Deliveries: {stats['delivery_stats']['total_deliveries']}")
    print(f"   Successful Deliveries: {stats['delivery_stats']['successful_deliveries']}")
    print(f"   Failed Deliveries: {stats['delivery_stats']['failed_deliveries']}")

if __name__ == "__main__":
    demo_exactly_once_delivery()
```

## Chapter 4: Event Ordering & Partitioning

### 4.1 Message Ordering (Mumbai Local Sequence)

"Mumbai Local mein trains ka sequence important hai - Slow local ke baad Fast local, timing maintain karna padta hai!"

```python
import heapq
import time
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class OrderedEvent:
    sequence_number: int
    timestamp: float
    event: Dict
    partition_key: str = ""
    
    def __lt__(self, other):
        return self.sequence_number < other.sequence_number

class PartitionedOrderingManager:
    """
    Maintain event ordering within partitions
    Like Mumbai Local platform-wise ordering
    """
    
    def __init__(self, num_partitions: int = 4):
        self.num_partitions = num_partitions
        self.partitions = {i: [] for i in range(num_partitions)}
        self.partition_locks = {i: threading.Lock() for i in range(num_partitions)}
        
        # Sequence tracking per partition
        self.next_expected_sequence = defaultdict(int)
        self.pending_events = defaultdict(list)  # Events waiting for their turn
        
        # Global sequence counter
        self.global_sequence = 0
        self.global_lock = threading.Lock()
    
    def get_partition_for_key(self, partition_key: str) -> int:
        """Hash-based partitioning"""
        return hash(partition_key) % self.num_partitions
    
    def add_event(self, event: Dict, partition_key: str) -> int:
        """Add event to appropriate partition maintaining order"""
        
        # Assign global sequence number
        with self.global_lock:
            self.global_sequence += 1
            sequence_number = self.global_sequence
        
        # Determine partition
        partition_id = self.get_partition_for_key(partition_key)
        
        # Create ordered event
        ordered_event = OrderedEvent(
            sequence_number=sequence_number,
            timestamp=time.time(),
            event=event,
            partition_key=partition_key
        )
        
        # Add to partition
        with self.partition_locks[partition_id]:
            heapq.heappush(self.partitions[partition_id], ordered_event)
        
        print(f"📨 Event {event.get('event_id')} added to partition {partition_id} with sequence {sequence_number}")
        
        return sequence_number
    
    def consume_ordered_events(self, partition_id: int, batch_size: int = 10) -> List[OrderedEvent]:
        """Consume events in order from specific partition"""
        
        events = []
        
        with self.partition_locks[partition_id]:
            while len(events) < batch_size and self.partitions[partition_id]:
                event = heapq.heappop(self.partitions[partition_id])
                events.append(event)
        
        if events:
            print(f"📤 Consumed {len(events)} events from partition {partition_id}")
            for event in events:
                print(f"   Sequence {event.sequence_number}: {event.event.get('event_type')}")
        
        return events
    
    def get_partition_stats(self) -> Dict:
        """Get statistics for all partitions"""
        stats = {}
        
        for partition_id in range(self.num_partitions):
            with self.partition_locks[partition_id]:
                stats[partition_id] = {
                    'pending_events': len(self.partitions[partition_id]),
                    'next_sequence': min([e.sequence_number for e in self.partitions[partition_id]]) if self.partitions[partition_id] else None
                }
        
        return stats

# FIFO Ordering for specific event streams
class FIFOEventProcessor:
    """
    FIFO processing for specific event streams
    Like Mumbai Local - first train to arrive is first to depart
    """
    
    def __init__(self):
        self.event_streams = defaultdict(list)  # Stream -> List of events
        self.stream_locks = defaultdict(threading.Lock)
        self.processing_order = defaultdict(int)  # Track processing order per stream
    
    def add_to_stream(self, stream_id: str, event: Dict):
        """Add event to FIFO stream"""
        
        with self.stream_locks[stream_id]:
            # Add processing order
            event['processing_order'] = self.processing_order[stream_id]
            self.processing_order[stream_id] += 1
            
            # Add to stream
            self.event_streams[stream_id].append(event)
        
        print(f"➕ Event {event.get('event_id')} added to stream '{stream_id}' at position {event['processing_order']}")
    
    def process_stream_fifo(self, stream_id: str, processor_func) -> int:
        """Process all events in stream in FIFO order"""
        
        processed_count = 0
        
        with self.stream_locks[stream_id]:
            while self.event_streams[stream_id]:
                event = self.event_streams[stream_id].pop(0)  # FIFO - first in, first out
                
                try:
                    processor_func(event)
                    processed_count += 1
                    print(f"✅ Processed event {event.get('event_id')} from stream '{stream_id}'")
                except Exception as e:
                    print(f"❌ Failed to process event {event.get('event_id')}: {e}")
                    # Re-add to front of queue for retry
                    self.event_streams[stream_id].insert(0, event)
                    break
        
        return processed_count

# Swiggy Order Processing with Ordering Guarantees
class SwiggyOrderProcessor:
    """
    Swiggy order processing maintaining proper event order
    """
    
    def __init__(self):
        self.partitioned_manager = PartitionedOrderingManager(num_partitions=4)
        self.fifo_processor = FIFOEventProcessor()
        
        # Order states for tracking
        self.order_states = {}
        self.restaurant_queues = defaultdict(list)
    
    def process_order_event(self, event: Dict):
        """Process order event maintaining order"""
        
        event_type = event.get('event_type')
        order_id = event.get('data', {}).get('order_id')
        restaurant_id = event.get('data', {}).get('restaurant_id')
        
        print(f"\n🍽️ Processing {event_type} for order {order_id}")
        
        if event_type == 'ORDER_PLACED':
            self.handle_order_placed(event)
        elif event_type == 'ORDER_CONFIRMED':
            self.handle_order_confirmed(event)
        elif event_type == 'ORDER_PREPARED':
            self.handle_order_prepared(event)
        elif event_type == 'DELIVERY_ASSIGNED':
            self.handle_delivery_assigned(event)
        elif event_type == 'ORDER_DELIVERED':
            self.handle_order_delivered(event)
        
        # Add to restaurant-specific FIFO stream for kitchen processing
        if restaurant_id:
            restaurant_stream = f"restaurant:{restaurant_id}"
            self.fifo_processor.add_to_stream(restaurant_stream, event)
    
    def handle_order_placed(self, event: Dict):
        """Handle new order placement"""
        data = event.get('data', {})
        order_id = data.get('order_id')
        customer_id = data.get('customer_id')
        
        # Initialize order state
        self.order_states[order_id] = {
            'status': 'placed',
            'customer_id': customer_id,
            'restaurant_id': data.get('restaurant_id'),
            'placed_at': time.time(),
            'events': [event]
        }
        
        # Add to partitioned manager using customer_id as partition key
        self.partitioned_manager.add_event(event, customer_id)
        
        print(f"   📝 Order {order_id} placed by customer {customer_id}")
    
    def handle_order_confirmed(self, event: Dict):
        """Handle order confirmation by restaurant"""
        order_id = event.get('data', {}).get('order_id')
        
        if order_id in self.order_states:
            self.order_states[order_id]['status'] = 'confirmed'
            self.order_states[order_id]['confirmed_at'] = time.time()
            self.order_states[order_id]['events'].append(event)
            
            # Add to customer partition
            customer_id = self.order_states[order_id]['customer_id']
            self.partitioned_manager.add_event(event, customer_id)
            
            print(f"   ✅ Order {order_id} confirmed by restaurant")
        else:
            print(f"   ❌ Order {order_id} not found for confirmation")
    
    def handle_order_prepared(self, event: Dict):
        """Handle order preparation completion"""
        order_id = event.get('data', {}).get('order_id')
        
        if order_id in self.order_states:
            self.order_states[order_id]['status'] = 'prepared'
            self.order_states[order_id]['prepared_at'] = time.time()
            self.order_states[order_id]['events'].append(event)
            
            customer_id = self.order_states[order_id]['customer_id']
            self.partitioned_manager.add_event(event, customer_id)
            
            print(f"   👨‍🍳 Order {order_id} prepared and ready for pickup")
        else:
            print(f"   ❌ Order {order_id} not found for preparation")
    
    def handle_delivery_assigned(self, event: Dict):
        """Handle delivery partner assignment"""
        order_id = event.get('data', {}).get('order_id')
        delivery_partner = event.get('data', {}).get('delivery_partner_id')
        
        if order_id in self.order_states:
            self.order_states[order_id]['status'] = 'out_for_delivery'
            self.order_states[order_id]['delivery_partner'] = delivery_partner
            self.order_states[order_id]['pickup_time'] = time.time()
            self.order_states[order_id]['events'].append(event)
            
            customer_id = self.order_states[order_id]['customer_id']
            self.partitioned_manager.add_event(event, customer_id)
            
            print(f"   🛵 Delivery partner {delivery_partner} assigned to order {order_id}")
        else:
            print(f"   ❌ Order {order_id} not found for delivery assignment")
    
    def handle_order_delivered(self, event: Dict):
        """Handle order delivery completion"""
        order_id = event.get('data', {}).get('order_id')
        
        if order_id in self.order_states:
            self.order_states[order_id]['status'] = 'delivered'
            self.order_states[order_id]['delivered_at'] = time.time()
            self.order_states[order_id]['events'].append(event)
            
            customer_id = self.order_states[order_id]['customer_id']
            self.partitioned_manager.add_event(event, customer_id)
            
            # Calculate delivery time
            placed_at = self.order_states[order_id]['placed_at']
            delivery_time = time.time() - placed_at
            
            print(f"   🎉 Order {order_id} delivered! Total time: {delivery_time:.1f} seconds")
        else:
            print(f"   ❌ Order {order_id} not found for delivery")
    
    def process_restaurant_queue(self, restaurant_id: str):
        """Process restaurant's event queue in FIFO order"""
        
        restaurant_stream = f"restaurant:{restaurant_id}"
        
        def restaurant_processor(event):
            """Process individual restaurant event"""
            event_type = event.get('event_type')
            order_id = event.get('data', {}).get('order_id')
            
            print(f"   🍽️ Restaurant {restaurant_id} processing {event_type} for order {order_id}")
            
            # Simulate processing time
            time.sleep(0.1)
            
            return True
        
        processed = self.fifo_processor.process_stream_fifo(restaurant_stream, restaurant_processor)
        print(f"🏪 Restaurant {restaurant_id} processed {processed} events from queue")
        
        return processed
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get current order status and event history"""
        if order_id in self.order_states:
            order_info = self.order_states[order_id].copy()
            
            # Calculate time metrics
            if 'placed_at' in order_info and 'delivered_at' in order_info:
                order_info['total_delivery_time'] = order_info['delivered_at'] - order_info['placed_at']
            
            return order_info
        
        return {'error': 'Order not found'}
    
    def get_system_stats(self) -> Dict:
        """Get overall system statistics"""
        partition_stats = self.partitioned_manager.get_partition_stats()
        
        order_status_counts = defaultdict(int)
        for order_state in self.order_states.values():
            order_status_counts[order_state['status']] += 1
        
        return {
            'total_orders': len(self.order_states),
            'order_status_breakdown': dict(order_status_counts),
            'partition_stats': partition_stats
        }

# Demo ordering system
def demo_ordering_system():
    processor = SwiggyOrderProcessor()
    
    # Simulate order lifecycle events
    orders = [
        {
            'customer_id': 'CUST001',
            'restaurant_id': 'REST_TRISHNA',
            'order_id': 'ORD001',
            'items': ['Butter Chicken', 'Naan']
        },
        {
            'customer_id': 'CUST002',
            'restaurant_id': 'REST_LEOPOLD',
            'order_id': 'ORD002',
            'items': ['Fish and Chips']
        },
        {
            'customer_id': 'CUST001',  # Same customer, different order
            'restaurant_id': 'REST_TRISHNA',
            'order_id': 'ORD003',
            'items': ['Biryani']
        }
    ]
    
    print("🍔 Swiggy Ordering System Demo")
    print("=" * 50)
    
    # Process order lifecycle for each order
    for order_info in orders:
        order_events = [
            {
                'event_id': f"evt_{order_info['order_id']}_placed",
                'event_type': 'ORDER_PLACED',
                'timestamp': time.time(),
                'data': order_info
            },
            {
                'event_id': f"evt_{order_info['order_id']}_confirmed",
                'event_type': 'ORDER_CONFIRMED',
                'timestamp': time.time() + 1,
                'data': {'order_id': order_info['order_id'], 'estimated_time': 20}
            },
            {
                'event_id': f"evt_{order_info['order_id']}_prepared",
                'event_type': 'ORDER_PREPARED',
                'timestamp': time.time() + 2,
                'data': {'order_id': order_info['order_id']}
            },
            {
                'event_id': f"evt_{order_info['order_id']}_assigned",
                'event_type': 'DELIVERY_ASSIGNED',
                'timestamp': time.time() + 3,
                'data': {'order_id': order_info['order_id'], 'delivery_partner_id': 'DEL001'}
            },
            {
                'event_id': f"evt_{order_info['order_id']}_delivered",
                'event_type': 'ORDER_DELIVERED',
                'timestamp': time.time() + 4,
                'data': {'order_id': order_info['order_id']}
            }
        ]
        
        # Process events for this order
        for event in order_events:
            processor.process_order_event(event)
            time.sleep(0.2)  # Small delay between events
    
    # Process restaurant queues
    print(f"\n🏪 Processing Restaurant Queues:")
    processor.process_restaurant_queue('REST_TRISHNA')
    processor.process_restaurant_queue('REST_LEOPOLD')
    
    # Show final statistics
    print(f"\n📊 Final System Statistics:")
    stats = processor.get_system_stats()
    print(f"   Total Orders: {stats['total_orders']}")
    print(f"   Order Status Breakdown:")
    for status, count in stats['order_status_breakdown'].items():
        print(f"      {status}: {count}")
    
    # Show individual order status
    print(f"\n📋 Individual Order Status:")
    for order_info in orders:
        order_id = order_info['order_id']
        status = processor.get_order_status(order_id)
        print(f"   Order {order_id}: {status['status']}")
        if 'total_delivery_time' in status:
            print(f"      Total delivery time: {status['total_delivery_time']:.1f} seconds")

if __name__ == "__main__":
    demo_ordering_system()
```

---

## Part 2 Summary: Advanced Implementation Mastery

"Bhai, Part 2 mein humne Event Bus ke advanced implementation strategies master kar liye:

### 🚂 Mumbai Railway System Lessons:

1. **Smart Routing**: Dadar junction ki tarah intelligent message routing
2. **Content Filtering**: Passenger-specific announcements jaisa targeted delivery
3. **Header-based Decisions**: Train classification system jaisa metadata routing
4. **Message Transformation**: Multi-language announcements jaisa format adaptation
5. **Delivery Guarantees**: Monthly pass validation jaisa exactly-once delivery
6. **Ordered Processing**: Platform sequence jaisa event ordering

### 🎯 Technical Mastery Achieved:

**Routing Strategies:**
- Topic-based routing with hierarchy
- Content-based intelligent routing
- Header-based classification
- Geographic and priority-based routing

**Message Processing:**
- Event filtering and validation
- Schema-based quality control
- Subscriber-specific transformations
- Multi-format message adaptation

**Delivery Guarantees:**
- Exactly-once delivery with deduplication
- At-least-once with acknowledgments
- Retry mechanisms with exponential backoff
- Dead letter queue handling

**Ordering & Partitioning:**
- Partition-based event ordering
- FIFO processing for specific streams
- Sequence number management
- Consumer lag monitoring

### 💡 Production-Ready Patterns:

1. **Paytm Payment Processing**: Exactly-once financial transactions
2. **Swiggy Order Flow**: FIFO kitchen processing with partitioning
3. **IRCTC Booking**: Header-based routing for different train types
4. **Zomato Events**: Content-based filtering for geographic delivery

### 🏗️ Implementation Highlights:

- **Schema Validation**: Data quality assurance
- **Circuit Breaker**: Resilient service communication
- **Transformation Pipeline**: Multi-stage message processing
- **Monitoring Integration**: Real-time system health tracking

Next part mein hum dekhenge real production case studies - kaise Swiggy, Paytm, IRCTC, aur WhatsApp ne Event Bus architecture ko scale kiya hai millions of users ke liye!"

### 4.2 Event Store Integration

"Mumbai Local mein har train ka record rakhte hain - kahan se aai, kahan gayi, kitne passengers the. Event Store bhi yahi karta hai - har event ko permanently store karta hai!"

**Event Store Implementation:**

```python
class EventStoreIntegration:
    """
    Event Store integration for event sourcing
    Mumbai Local journey tracking style
    """
    
    def __init__(self):
        self.event_store = EventStore()
        self.snapshots = {}
        self.projection_managers = {}
    
    def append_events_to_stream(self, stream_id: str, events: List[Dict], expected_version: int):
        """Append events to stream with optimistic concurrency"""
        
        print(f"📝 Appending {len(events)} events to stream: {stream_id}")
        
        try:
            # Validate expected version
            current_version = self.event_store.get_stream_version(stream_id)
            if current_version != expected_version:
                raise ConcurrencyException(f"Expected version {expected_version}, but stream is at {current_version}")
            
            # Append events atomically
            new_version = self.event_store.append_events(stream_id, events)
            
            print(f"✅ Events appended successfully. New version: {new_version}")
            
            # Trigger projections
            self.update_projections(stream_id, events)
            
            return new_version
            
        except Exception as e:
            print(f"❌ Failed to append events: {e}")
            raise
    
    def read_events_from_stream(self, stream_id: str, from_version: int = 0, max_count: int = 100) -> List[Dict]:
        """Read events from stream"""
        
        events = self.event_store.read_events(stream_id, from_version, max_count)
        print(f"📖 Read {len(events)} events from stream: {stream_id}")
        
        return events
    
    def create_snapshot(self, stream_id: str, aggregate_state: Dict, version: int):
        """Create snapshot for performance optimization"""
        
        snapshot = {
            'stream_id': stream_id,
            'aggregate_state': aggregate_state,
            'version': version,
            'timestamp': time.time()
        }
        
        self.snapshots[stream_id] = snapshot
        print(f"📸 Snapshot created for stream: {stream_id} at version: {version}")
    
    def update_projections(self, stream_id: str, events: List[Dict]):
        """Update read-model projections"""
        
        for event in events:
            event_type = event.get('event_type')
            
            # Update relevant projections
            if stream_id.startswith('order-'):
                self.update_order_projection(event)
            elif stream_id.startswith('customer-'):
                self.update_customer_projection(event)
            elif stream_id.startswith('restaurant-'):
                self.update_restaurant_projection(event)
    
    def update_order_projection(self, event: Dict):
        """Update order-related projections"""
        print(f"🔄 Updating order projection for: {event.get('event_type')}")
    
    def update_customer_projection(self, event: Dict):
        """Update customer-related projections"""
        print(f"🔄 Updating customer projection for: {event.get('event_type')}")
    
    def update_restaurant_projection(self, event: Dict):
        """Update restaurant-related projections"""
        print(f"🔄 Updating restaurant projection for: {event.get('event_type')}")

class EventStore:
    """Mock Event Store implementation"""
    
    def __init__(self):
        self.streams = {}
        self.global_position = 0
    
    def get_stream_version(self, stream_id: str) -> int:
        if stream_id not in self.streams:
            return -1
        return len(self.streams[stream_id]) - 1
    
    def append_events(self, stream_id: str, events: List[Dict]) -> int:
        if stream_id not in self.streams:
            self.streams[stream_id] = []
        
        for event in events:
            event['global_position'] = self.global_position
            event['stream_position'] = len(self.streams[stream_id])
            self.streams[stream_id].append(event)
            self.global_position += 1
        
        return len(self.streams[stream_id]) - 1
    
    def read_events(self, stream_id: str, from_version: int, max_count: int) -> List[Dict]:
        if stream_id not in self.streams:
            return []
        
        stream = self.streams[stream_id]
        start_index = max(0, from_version + 1)
        end_index = min(len(stream), start_index + max_count)
        
        return stream[start_index:end_index]

class ConcurrencyException(Exception):
    """Exception for concurrency conflicts"""
    pass

# Demo integration
def demo_event_store_integration():
    store_integration = EventStoreIntegration()
    
    # Simulate Swiggy order events
    order_events = [
        {
            'event_id': 'evt_001',
            'event_type': 'ORDER_PLACED',
            'data': {'order_id': 'ORD001', 'customer_id': 'CUST001', 'total': 500},
            'timestamp': time.time()
        },
        {
            'event_id': 'evt_002', 
            'event_type': 'PAYMENT_PROCESSED',
            'data': {'order_id': 'ORD001', 'payment_id': 'PAY001', 'amount': 500},
            'timestamp': time.time() + 1
        }
    ]
    
    print("🏪 Event Store Integration Demo")
    print("=" * 40)
    
    # Append events
    version = store_integration.append_events_to_stream('order-ORD001', order_events, -1)
    
    # Read events back
    stored_events = store_integration.read_events_from_stream('order-ORD001')
    
    print(f"\n📚 Stored Events: {len(stored_events)}")
    for event in stored_events:
        print(f"   {event['event_type']}: {event['data']}")

if __name__ == "__main__":
    demo_event_store_integration()
```

---

**Word Count: ~7,200+ words**

*Part 2 of 3 complete. Coming up next: Part 3 - Production Case Studies & Scaling Challenges*
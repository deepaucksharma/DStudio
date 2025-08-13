#!/usr/bin/env python3
"""
Episode 21: CQRS/Event Sourcing - Query Handlers for Order Status Lookup
Author: Code Developer Agent
Description: Optimized query handlers for Flipkart order status and tracking

Query Handlers optimize read performance
ये denormalized data से fast responses देते हैं
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import json

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PACKED = "packed"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class DeliverySpeed(Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    SAME_DAY = "same_day"

# Query Models - Optimized for read operations
@dataclass
class OrderSummaryView:
    """Customer order summary - optimized view"""
    order_id: str
    customer_id: str
    order_date: datetime
    total_amount: float
    status: str
    estimated_delivery: str
    items_count: int
    thumbnail_url: str
    tracking_number: Optional[str] = None

@dataclass
class OrderDetailsView:
    """Detailed order view with all information"""
    order_id: str
    customer_id: str
    customer_name: str
    customer_phone: str
    order_date: datetime
    confirmed_date: Optional[datetime]
    total_amount: float
    discount_amount: float
    delivery_charges: float
    status: str
    payment_method: str
    payment_status: str
    delivery_address: Dict
    billing_address: Dict
    estimated_delivery: str
    actual_delivery: Optional[datetime]
    items: List[Dict]
    tracking_info: Dict
    status_history: List[Dict]

@dataclass
class TrackingView:
    """Order tracking information"""
    order_id: str
    tracking_number: str
    current_status: str
    current_location: str
    estimated_delivery: str
    delivery_partner: str
    tracking_events: List[Dict]
    delivery_instructions: str

@dataclass
class CustomerOrderHistoryView:
    """Customer's complete order history"""
    customer_id: str
    customer_name: str
    total_orders: int
    total_spent: float
    favorite_categories: List[str]
    recent_orders: List[OrderSummaryView]
    return_rate: float
    average_order_value: float

# Query Objects
@dataclass
class GetOrderSummaryQuery:
    customer_id: str
    limit: int = 10
    offset: int = 0
    status_filter: Optional[str] = None

@dataclass
class GetOrderDetailsQuery:
    order_id: str
    customer_id: Optional[str] = None  # For validation

@dataclass
class GetOrderTrackingQuery:
    order_id: str
    tracking_number: Optional[str] = None

@dataclass
class GetCustomerHistoryQuery:
    customer_id: str
    include_cancelled: bool = False
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

@dataclass
class SearchOrdersQuery:
    search_term: str  # Order ID, product name, etc.
    customer_id: Optional[str] = None
    status_filters: Optional[List[str]] = None
    date_range: Optional[Dict] = None
    limit: int = 20

# Base Query Handler
class QueryHandler(ABC):
    """Base query handler interface"""
    
    @abstractmethod
    async def handle(self, query: Any) -> Any:
        pass

# Read Model Repositories (Optimized for queries)
class OrderReadModelRepository:
    """Optimized read model repository for orders"""
    
    def __init__(self):
        # Mock denormalized data store
        self._order_summaries = {}
        self._order_details = {}
        self._tracking_info = {}
        self._customer_history = {}
        
        # Setup sample data
        self._setup_sample_data()
    
    def _setup_sample_data(self):
        """Setup sample Flipkart order data"""
        base_date = datetime.now()
        
        # Sample order summaries
        self._order_summaries["CUST001"] = [
            OrderSummaryView(
                order_id="FL2024010112345678",
                customer_id="CUST001",
                order_date=base_date - timedelta(days=2),
                total_amount=25998.0,
                status=OrderStatus.SHIPPED.value,
                estimated_delivery="Today by 8 PM",
                items_count=1,
                thumbnail_url="https://img.flipkart.com/mobile.jpg",
                tracking_number="FKT123456789"
            ),
            OrderSummaryView(
                order_id="FL2024010187654321",
                customer_id="CUST001",
                order_date=base_date - timedelta(days=7),
                total_amount=1299.0,
                status=OrderStatus.DELIVERED.value,
                estimated_delivery="Delivered on Jan 5",
                items_count=3,
                thumbnail_url="https://img.flipkart.com/books.jpg"
            )
        ]
        
        # Sample order details
        self._order_details["FL2024010112345678"] = OrderDetailsView(
            order_id="FL2024010112345678",
            customer_id="CUST001",
            customer_name="Rajesh Sharma",
            customer_phone="+91-9876543210",
            order_date=base_date - timedelta(days=2),
            confirmed_date=base_date - timedelta(days=2, hours=2),
            total_amount=25998.0,
            discount_amount=2000.0,
            delivery_charges=0.0,
            status=OrderStatus.SHIPPED.value,
            payment_method="UPI",
            payment_status="SUCCESS",
            delivery_address={
                "name": "Rajesh Sharma",
                "address": "A-101, Ocean View Apartments",
                "area": "Bandra West",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400050",
                "phone": "+91-9876543210"
            },
            billing_address={
                "name": "Rajesh Sharma",
                "address": "A-101, Ocean View Apartments",
                "area": "Bandra West",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400050"
            },
            estimated_delivery="Today by 8 PM",
            actual_delivery=None,
            items=[
                {
                    "product_id": "MOBILE001",
                    "name": "Samsung Galaxy S24 Ultra 5G",
                    "brand": "Samsung",
                    "quantity": 1,
                    "unit_price": 27998.0,
                    "discount": 2000.0,
                    "final_price": 25998.0,
                    "image_url": "https://img.flipkart.com/samsung-s24.jpg",
                    "seller": "Flipkart Retail"
                }
            ],
            tracking_info={
                "tracking_number": "FKT123456789",
                "carrier": "Ekart Logistics",
                "current_location": "Mumbai Hub",
                "out_for_delivery_date": base_date.strftime("%Y-%m-%d")
            },
            status_history=[
                {
                    "status": "PENDING",
                    "timestamp": (base_date - timedelta(days=2)).isoformat(),
                    "location": "Order Placed",
                    "description": "Your order has been placed successfully"
                },
                {
                    "status": "CONFIRMED",
                    "timestamp": (base_date - timedelta(days=2, hours=2)).isoformat(),
                    "location": "Payment Confirmed",
                    "description": "Payment confirmed via UPI"
                },
                {
                    "status": "PACKED",
                    "timestamp": (base_date - timedelta(days=1, hours=10)).isoformat(),
                    "location": "Flipkart Warehouse, Bangalore",
                    "description": "Your item has been packed"
                },
                {
                    "status": "SHIPPED",
                    "timestamp": (base_date - timedelta(days=1)).isoformat(),
                    "location": "In Transit to Mumbai",
                    "description": "Your order is on the way"
                }
            ]
        )
        
        # Sample tracking info
        self._tracking_info["FKT123456789"] = TrackingView(
            order_id="FL2024010112345678",
            tracking_number="FKT123456789",
            current_status="Out for Delivery",
            current_location="Mumbai Delivery Hub",
            estimated_delivery="Today by 8 PM",
            delivery_partner="Ekart Logistics",
            tracking_events=[
                {
                    "timestamp": (base_date - timedelta(days=2)).isoformat(),
                    "status": "Order Confirmed",
                    "location": "Flipkart",
                    "description": "Order confirmed and forwarded to seller"
                },
                {
                    "timestamp": (base_date - timedelta(days=1, hours=18)).isoformat(),
                    "status": "Packed",
                    "location": "Bangalore Fulfillment Center",
                    "description": "Your item has been picked up by logistics partner"
                },
                {
                    "timestamp": (base_date - timedelta(days=1, hours=12)).isoformat(),
                    "status": "In Transit",
                    "location": "Bangalore Hub",
                    "description": "Your order is on the way to destination hub"
                },
                {
                    "timestamp": (base_date - timedelta(hours=8)).isoformat(),
                    "status": "Reached Hub",
                    "location": "Mumbai Hub",
                    "description": "Your order has reached the destination hub"
                },
                {
                    "timestamp": (base_date - timedelta(hours=2)).isoformat(),
                    "status": "Out for Delivery",
                    "location": "Mumbai Delivery Hub",
                    "description": "Your order is out for delivery"
                }
            ],
            delivery_instructions="Please call before delivery"
        )

# Query Handlers Implementation
class GetOrderSummaryQueryHandler(QueryHandler):
    """Customer orders summary query handler"""
    
    def __init__(self, read_repository: OrderReadModelRepository):
        self.read_repository = read_repository
    
    async def handle(self, query: GetOrderSummaryQuery) -> List[OrderSummaryView]:
        """Customer के orders की summary fetch करें"""
        print(f"📋 Fetching order summary for customer {query.customer_id}")
        
        # Get customer's orders from denormalized view
        all_orders = self.read_repository._order_summaries.get(query.customer_id, [])
        
        # Apply status filter if provided
        if query.status_filter:
            all_orders = [order for order in all_orders if order.status == query.status_filter]
        
        # Apply pagination
        start_index = query.offset
        end_index = start_index + query.limit
        
        result = all_orders[start_index:end_index]
        
        print(f"✅ Found {len(result)} orders for customer {query.customer_id}")
        return result

class GetOrderDetailsQueryHandler(QueryHandler):
    """Order details query handler"""
    
    def __init__(self, read_repository: OrderReadModelRepository):
        self.read_repository = read_repository
    
    async def handle(self, query: GetOrderDetailsQuery) -> Optional[OrderDetailsView]:
        """Order की detailed information fetch करें"""
        print(f"📊 Fetching order details for {query.order_id}")
        
        order_details = self.read_repository._order_details.get(query.order_id)
        
        if not order_details:
            print(f"❌ Order {query.order_id} not found")
            return None
        
        # Validate customer access if customer_id provided
        if query.customer_id and order_details.customer_id != query.customer_id:
            print(f"❌ Access denied for customer {query.customer_id}")
            return None
        
        print(f"✅ Order details found for {query.order_id}")
        return order_details

class GetOrderTrackingQueryHandler(QueryHandler):
    """Order tracking query handler"""
    
    def __init__(self, read_repository: OrderReadModelRepository):
        self.read_repository = read_repository
    
    async def handle(self, query: GetOrderTrackingQuery) -> Optional[TrackingView]:
        """Order tracking information fetch करें"""
        print(f"🚚 Fetching tracking info for order {query.order_id}")
        
        # First try to find by order_id
        tracking_info = None
        for tracking_number, tracking_data in self.read_repository._tracking_info.items():
            if tracking_data.order_id == query.order_id:
                tracking_info = tracking_data
                break
        
        # If tracking_number provided, use that
        if query.tracking_number:
            tracking_info = self.read_repository._tracking_info.get(query.tracking_number)
        
        if not tracking_info:
            print(f"❌ Tracking info not found for order {query.order_id}")
            return None
        
        print(f"✅ Tracking info found: {tracking_info.current_status}")
        return tracking_info

class GetCustomerHistoryQueryHandler(QueryHandler):
    """Customer order history query handler"""
    
    def __init__(self, read_repository: OrderReadModelRepository):
        self.read_repository = read_repository
    
    async def handle(self, query: GetCustomerHistoryQuery) -> Optional[CustomerOrderHistoryView]:
        """Customer का complete order history fetch करें"""
        print(f"📚 Fetching order history for customer {query.customer_id}")
        
        customer_orders = self.read_repository._order_summaries.get(query.customer_id, [])
        
        if not customer_orders:
            return None
        
        # Filter by date range if provided
        filtered_orders = customer_orders
        if query.date_from or query.date_to:
            filtered_orders = []
            for order in customer_orders:
                order_date = order.order_date
                if query.date_from and order_date < query.date_from:
                    continue
                if query.date_to and order_date > query.date_to:
                    continue
                filtered_orders.append(order)
        
        # Filter cancelled orders if not included
        if not query.include_cancelled:
            filtered_orders = [order for order in filtered_orders 
                             if order.status != OrderStatus.CANCELLED.value]
        
        # Calculate statistics
        total_orders = len(filtered_orders)
        total_spent = sum(order.total_amount for order in filtered_orders)
        delivered_orders = [order for order in filtered_orders 
                           if order.status == OrderStatus.DELIVERED.value]
        returned_orders = [order for order in filtered_orders 
                          if order.status == OrderStatus.RETURNED.value]
        
        return_rate = len(returned_orders) / len(delivered_orders) if delivered_orders else 0.0
        avg_order_value = total_spent / total_orders if total_orders > 0 else 0.0
        
        history_view = CustomerOrderHistoryView(
            customer_id=query.customer_id,
            customer_name="Rajesh Sharma",  # In production, fetch from customer service
            total_orders=total_orders,
            total_spent=total_spent,
            favorite_categories=["Electronics", "Books", "Fashion"],  # Analyze from order data
            recent_orders=filtered_orders[:10],  # Last 10 orders
            return_rate=return_rate,
            average_order_value=avg_order_value
        )
        
        print(f"✅ Customer history found: {total_orders} orders, ₹{total_spent:.2f} total spent")
        return history_view

class SearchOrdersQueryHandler(QueryHandler):
    """Order search query handler"""
    
    def __init__(self, read_repository: OrderReadModelRepository):
        self.read_repository = read_repository
    
    async def handle(self, query: SearchOrdersQuery) -> List[OrderSummaryView]:
        """Orders को search करें multiple criteria से"""
        print(f"🔍 Searching orders with term: {query.search_term}")
        
        all_orders = []
        
        # Collect all orders (in production, use proper search index)
        if query.customer_id:
            customer_orders = self.read_repository._order_summaries.get(query.customer_id, [])
            all_orders.extend(customer_orders)
        else:
            # Search across all customers
            for customer_id, orders in self.read_repository._order_summaries.items():
                all_orders.extend(orders)
        
        # Apply search filters
        search_results = []
        search_term_lower = query.search_term.lower()
        
        for order in all_orders:
            # Search in order ID
            if search_term_lower in order.order_id.lower():
                search_results.append(order)
                continue
            
            # Get order details for product name search
            order_details = self.read_repository._order_details.get(order.order_id)
            if order_details:
                # Search in product names
                for item in order_details.items:
                    if search_term_lower in item['name'].lower():
                        search_results.append(order)
                        break
        
        # Apply status filters
        if query.status_filters:
            search_results = [order for order in search_results 
                             if order.status in query.status_filters]
        
        # Apply date range filter
        if query.date_range:
            date_from = query.date_range.get('from')
            date_to = query.date_range.get('to')
            
            if date_from or date_to:
                filtered_results = []
                for order in search_results:
                    if date_from and order.order_date < date_from:
                        continue
                    if date_to and order.order_date > date_to:
                        continue
                    filtered_results.append(order)
                search_results = filtered_results
        
        # Apply limit
        search_results = search_results[:query.limit]
        
        print(f"✅ Found {len(search_results)} orders matching search criteria")
        return search_results

# Query Bus - Central query dispatcher
class QueryBus:
    """Central query dispatcher"""
    
    def __init__(self, read_repository: OrderReadModelRepository):
        self.read_repository = read_repository
        self._handlers = {
            GetOrderSummaryQuery: GetOrderSummaryQueryHandler(read_repository),
            GetOrderDetailsQuery: GetOrderDetailsQueryHandler(read_repository),
            GetOrderTrackingQuery: GetOrderTrackingQueryHandler(read_repository),
            GetCustomerHistoryQuery: GetCustomerHistoryQueryHandler(read_repository),
            SearchOrdersQuery: SearchOrdersQueryHandler(read_repository)
        }
    
    async def send(self, query: Any) -> Any:
        """Query को appropriate handler को send करें"""
        query_type = type(query)
        handler = self._handlers.get(query_type)
        
        if not handler:
            raise ValueError(f"No handler found for query {query_type.__name__}")
        
        try:
            return await handler.handle(query)
        except Exception as e:
            print(f"❌ Query handling failed: {e}")
            raise e

# Demo Function
async def demonstrate_flipkart_query_handlers():
    """Flipkart query handlers का comprehensive demonstration"""
    print("🔍 Flipkart Query Handlers Demo")
    print("=" * 50)
    
    # Setup
    read_repository = OrderReadModelRepository()
    query_bus = QueryBus(read_repository)
    
    # 1. Get customer order summary
    print("\n📋 Fetching customer order summary...")
    summary_query = GetOrderSummaryQuery(
        customer_id="CUST001",
        limit=5,
        offset=0
    )
    
    summaries = await query_bus.send(summary_query)
    print(f"\nCustomer Orders ({len(summaries)}):")
    for order in summaries:
        print(f"  📦 {order.order_id[:10]}... | ₹{order.total_amount} | {order.status} | {order.estimated_delivery}")
    
    # 2. Get specific order details
    if summaries:
        print(f"\n📊 Fetching details for order {summaries[0].order_id[:10]}...")
        details_query = GetOrderDetailsQuery(
            order_id=summaries[0].order_id,
            customer_id="CUST001"
        )
        
        details = await query_bus.send(details_query)
        if details:
            print(f"\nOrder Details:")
            print(f"  Customer: {details.customer_name}")
            print(f"  Total: ₹{details.total_amount} (Discount: ₹{details.discount_amount})")
            print(f"  Status: {details.status}")
            print(f"  Payment: {details.payment_method} ({details.payment_status})")
            print(f"  Items: {len(details.items)}")
            for item in details.items:
                print(f"    - {item['name']} x{item['quantity']} = ₹{item['final_price']}")
            
            print(f"\n  Status History:")
            for i, status in enumerate(details.status_history[-3:], 1):  # Last 3 status updates
                print(f"    {i}. {status['status']} - {status['description']}")
    
    # 3. Get tracking information
    print(f"\n🚚 Fetching tracking info...")
    tracking_query = GetOrderTrackingQuery(
        order_id="FL2024010112345678"
    )
    
    tracking = await query_bus.send(tracking_query)
    if tracking:
        print(f"\nTracking Info:")
        print(f"  Tracking #: {tracking.tracking_number}")
        print(f"  Status: {tracking.current_status}")
        print(f"  Location: {tracking.current_location}")
        print(f"  Delivery: {tracking.estimated_delivery}")
        print(f"  Carrier: {tracking.delivery_partner}")
        
        print(f"\n  Recent Tracking Events:")
        for event in tracking.tracking_events[-3:]:  # Last 3 events
            event_time = datetime.fromisoformat(event['timestamp'])
            print(f"    📍 {event['status']} | {event['location']} | {event_time.strftime('%d %b, %I:%M %p')}")
    
    # 4. Get customer history
    print(f"\n📚 Fetching customer order history...")
    history_query = GetCustomerHistoryQuery(
        customer_id="CUST001",
        include_cancelled=False
    )
    
    history = await query_bus.send(history_query)
    if history:
        print(f"\nCustomer History:")
        print(f"  Total Orders: {history.total_orders}")
        print(f"  Total Spent: ₹{history.total_spent:.2f}")
        print(f"  Average Order Value: ₹{history.average_order_value:.2f}")
        print(f"  Return Rate: {history.return_rate:.1%}")
        print(f"  Favorite Categories: {', '.join(history.favorite_categories)}")
    
    # 5. Search orders
    print(f"\n🔍 Searching orders with 'Samsung'...")
    search_query = SearchOrdersQuery(
        search_term="Samsung",
        customer_id="CUST001",
        limit=10
    )
    
    search_results = await query_bus.send(search_query)
    print(f"\nSearch Results ({len(search_results)}):")
    for order in search_results:
        print(f"  📱 {order.order_id[:10]}... | ₹{order.total_amount} | {order.status}")
    
    print("\n✅ Query Handlers Demo completed successfully!")

if __name__ == "__main__":
    """
    Key Query Handler Benefits:
    1. Fast read operations with denormalized data
    2. Optimized views for different use cases
    3. Independent scaling of read side
    4. Complex search और filtering capabilities
    5. Better user experience with quick responses
    """
    asyncio.run(demonstrate_flipkart_query_handlers())
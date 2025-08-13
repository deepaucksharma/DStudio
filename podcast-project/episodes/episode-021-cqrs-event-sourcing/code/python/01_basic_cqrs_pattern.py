#!/usr/bin/env python3
"""
Episode 21: CQRS/Event Sourcing - Basic CQRS Pattern Implementation
Author: Code Developer Agent
Description: Basic CQRS pattern implementation with Flipkart order processing example

CQRS अलग करता है read और write operations को
यह pattern बहुत useful है high-scale Indian e-commerce में
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import uuid
import asyncio
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Command Model - Write Side (Flipkart Orders)
@dataclass
class CreateOrderCommand:
    """Flipkart order create करने का command"""
    customer_id: str
    product_id: str
    quantity: int
    price: float
    delivery_address: str

@dataclass
class UpdateOrderStatusCommand:
    """Order status update करने का command"""
    order_id: str
    new_status: OrderStatus
    reason: str = ""

# Events - Domain Events 
@dataclass
class OrderCreatedEvent:
    """Jab naya order create hota hai"""
    order_id: str
    customer_id: str
    product_id: str
    quantity: int
    price: float
    delivery_address: str
    created_at: datetime

@dataclass
class OrderStatusUpdatedEvent:
    """Jab order ka status change hota hai"""
    order_id: str
    old_status: OrderStatus
    new_status: OrderStatus
    updated_at: datetime
    reason: str

# Write Model - Domain Aggregate
class Order:
    """Flipkart Order aggregate - write side representation"""
    
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.customer_id = None
        self.product_id = None
        self.quantity = 0
        self.price = 0.0
        self.delivery_address = ""
        self.status = OrderStatus.PENDING
        self.created_at = None
        self.updated_at = None
        self._uncommitted_events: List[Any] = []
    
    def create_order(self, customer_id: str, product_id: str, 
                    quantity: int, price: float, delivery_address: str):
        """Naya order create करें"""
        self.customer_id = customer_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        self.delivery_address = delivery_address
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        
        # Domain event add करें
        event = OrderCreatedEvent(
            order_id=self.order_id,
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
            price=price,
            delivery_address=delivery_address,
            created_at=self.created_at
        )
        self._uncommitted_events.append(event)
    
    def update_status(self, new_status: OrderStatus, reason: str = ""):
        """Order status update करें"""
        if new_status == self.status:
            return  # No change needed
        
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        
        # Domain event add करें
        event = OrderStatusUpdatedEvent(
            order_id=self.order_id,
            old_status=old_status,
            new_status=new_status,
            updated_at=self.updated_at,
            reason=reason
        )
        self._uncommitted_events.append(event)
    
    def get_uncommitted_events(self) -> List[Any]:
        """Uncommitted events return करें"""
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self):
        """Events को committed mark करें"""
        self._uncommitted_events.clear()

# Command Handlers - Business Logic for Write Operations
class CommandHandler(ABC):
    @abstractmethod
    async def handle(self, command: Any) -> Any:
        pass

class CreateOrderCommandHandler(CommandHandler):
    """Flipkart order creation handler"""
    
    def __init__(self, order_repository):
        self.order_repository = order_repository
    
    async def handle(self, command: CreateOrderCommand) -> str:
        """Order create करने का main logic"""
        order_id = str(uuid.uuid4())
        order = Order(order_id)
        
        # Business validation
        if command.quantity <= 0:
            raise ValueError("Quantity 0 से ज्यादा होनी चाहिए")
        
        if command.price <= 0:
            raise ValueError("Price valid होनी चाहिए")
        
        # Order create करें
        order.create_order(
            customer_id=command.customer_id,
            product_id=command.product_id,
            quantity=command.quantity,
            price=command.price,
            delivery_address=command.delivery_address
        )
        
        # Repository में save करें
        await self.order_repository.save(order)
        
        print(f"✅ Order {order_id} successfully created for customer {command.customer_id}")
        return order_id

class UpdateOrderStatusCommandHandler(CommandHandler):
    """Order status update handler"""
    
    def __init__(self, order_repository):
        self.order_repository = order_repository
    
    async def handle(self, command: UpdateOrderStatusCommand) -> bool:
        """Order status update का main logic"""
        order = await self.order_repository.get_by_id(command.order_id)
        
        if not order:
            raise ValueError(f"Order {command.order_id} नहीं मिला")
        
        # Status update करें
        order.update_status(command.new_status, command.reason)
        
        # Repository में save करें
        await self.order_repository.save(order)
        
        print(f"✅ Order {command.order_id} status updated to {command.new_status.value}")
        return True

# Read Model - Query Side Representations
@dataclass
class OrderSummaryReadModel:
    """Customer के लिए order summary view"""
    order_id: str
    customer_id: str
    product_name: str
    total_amount: float
    status: str
    estimated_delivery: str
    created_at: datetime

@dataclass
class OrderDetailsReadModel:
    """Detailed order view for admin/support"""
    order_id: str
    customer_id: str
    customer_name: str
    customer_phone: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_amount: float
    status: str
    delivery_address: str
    created_at: datetime
    updated_at: datetime
    status_history: List[Dict]

# Query Handlers - Read Operations
class QueryHandler(ABC):
    @abstractmethod
    async def handle(self, query: Any) -> Any:
        pass

@dataclass
class GetOrderSummaryQuery:
    customer_id: str

@dataclass
class GetOrderDetailsQuery:
    order_id: str

class GetOrderSummaryQueryHandler(QueryHandler):
    """Customer order summary query handler"""
    
    def __init__(self, read_db):
        self.read_db = read_db
    
    async def handle(self, query: GetOrderSummaryQuery) -> List[OrderSummaryReadModel]:
        """Customer के सभी orders की summary fetch करें"""
        # यहाँ normally आप database से optimized read model fetch करेंगे
        orders = await self.read_db.get_orders_by_customer(query.customer_id)
        
        result = []
        for order_data in orders:
            summary = OrderSummaryReadModel(
                order_id=order_data['order_id'],
                customer_id=order_data['customer_id'],
                product_name=order_data['product_name'],
                total_amount=order_data['total_amount'],
                status=order_data['status'],
                estimated_delivery=order_data['estimated_delivery'],
                created_at=order_data['created_at']
            )
            result.append(summary)
        
        return result

class GetOrderDetailsQueryHandler(QueryHandler):
    """Order details query handler"""
    
    def __init__(self, read_db):
        self.read_db = read_db
    
    async def handle(self, query: GetOrderDetailsQuery) -> OrderDetailsReadModel:
        """Specific order की detailed information fetch करें"""
        order_data = await self.read_db.get_order_details(query.order_id)
        
        if not order_data:
            raise ValueError(f"Order {query.order_id} नहीं मिला")
        
        details = OrderDetailsReadModel(
            order_id=order_data['order_id'],
            customer_id=order_data['customer_id'],
            customer_name=order_data['customer_name'],
            customer_phone=order_data['customer_phone'],
            product_id=order_data['product_id'],
            product_name=order_data['product_name'],
            quantity=order_data['quantity'],
            unit_price=order_data['unit_price'],
            total_amount=order_data['total_amount'],
            status=order_data['status'],
            delivery_address=order_data['delivery_address'],
            created_at=order_data['created_at'],
            updated_at=order_data['updated_at'],
            status_history=order_data['status_history']
        )
        
        return details

# Mock Repository and Database
class OrderRepository:
    """Write side repository"""
    
    def __init__(self):
        self._orders: Dict[str, Order] = {}
    
    async def save(self, order: Order):
        """Order को save करें और events publish करें"""
        self._orders[order.order_id] = order
        
        # Events publish करें (normally event bus को)
        events = order.get_uncommitted_events()
        for event in events:
            await self._publish_event(event)
        
        order.mark_events_as_committed()
    
    async def get_by_id(self, order_id: str) -> Order:
        """Order ID से order fetch करें"""
        return self._orders.get(order_id)
    
    async def _publish_event(self, event):
        """Event को publish करें (mock implementation)"""
        print(f"📢 Event Published: {type(event).__name__} for order {event.order_id}")

class ReadDatabase:
    """Read side database (denormalized views)"""
    
    def __init__(self):
        self._order_summaries: Dict[str, List[Dict]] = {}
        self._order_details: Dict[str, Dict] = {}
    
    async def get_orders_by_customer(self, customer_id: str) -> List[Dict]:
        """Customer के orders की summary return करें"""
        return self._order_summaries.get(customer_id, [])
    
    async def get_order_details(self, order_id: str) -> Dict:
        """Order की detailed information return करें"""
        return self._order_details.get(order_id)
    
    # Event handlers for read model updates
    async def handle_order_created_event(self, event: OrderCreatedEvent):
        """Order created event handle करें"""
        if event.customer_id not in self._order_summaries:
            self._order_summaries[event.customer_id] = []
        
        summary_data = {
            'order_id': event.order_id,
            'customer_id': event.customer_id,
            'product_name': f"Product {event.product_id}",
            'total_amount': event.price * event.quantity,
            'status': OrderStatus.PENDING.value,
            'estimated_delivery': "3-5 business days",
            'created_at': event.created_at
        }
        
        self._order_summaries[event.customer_id].append(summary_data)
        
        # Detailed view भी update करें
        self._order_details[event.order_id] = {
            'order_id': event.order_id,
            'customer_id': event.customer_id,
            'customer_name': f"Customer {event.customer_id}",
            'customer_phone': "+91-9876543210",
            'product_id': event.product_id,
            'product_name': f"Product {event.product_id}",
            'quantity': event.quantity,
            'unit_price': event.price,
            'total_amount': event.price * event.quantity,
            'status': OrderStatus.PENDING.value,
            'delivery_address': event.delivery_address,
            'created_at': event.created_at,
            'updated_at': event.created_at,
            'status_history': [{'status': OrderStatus.PENDING.value, 'timestamp': event.created_at}]
        }

# CQRS Facade - Main Application Interface
class FlipkartOrderCQRSSystem:
    """Main CQRS system for Flipkart orders"""
    
    def __init__(self):
        self.order_repository = OrderRepository()
        self.read_database = ReadDatabase()
        
        # Command handlers
        self.create_order_handler = CreateOrderCommandHandler(self.order_repository)
        self.update_status_handler = UpdateOrderStatusCommandHandler(self.order_repository)
        
        # Query handlers
        self.get_summary_handler = GetOrderSummaryQueryHandler(self.read_database)
        self.get_details_handler = GetOrderDetailsQueryHandler(self.read_database)
    
    async def execute_command(self, command) -> Any:
        """Command execute करें"""
        if isinstance(command, CreateOrderCommand):
            return await self.create_order_handler.handle(command)
        elif isinstance(command, UpdateOrderStatusCommand):
            return await self.update_status_handler.handle(command)
        else:
            raise ValueError(f"Unknown command type: {type(command)}")
    
    async def execute_query(self, query) -> Any:
        """Query execute करें"""
        if isinstance(query, GetOrderSummaryQuery):
            return await self.get_summary_handler.handle(query)
        elif isinstance(query, GetOrderDetailsQuery):
            return await self.get_details_handler.handle(query)
        else:
            raise ValueError(f"Unknown query type: {type(query)}")

# Demo Function
async def demonstrate_flipkart_cqrs():
    """Flipkart CQRS system का demonstration"""
    print("🛒 Flipkart CQRS Order System Demo")
    print("=" * 50)
    
    system = FlipkartOrderCQRSSystem()
    
    # 1. नया order create करें
    create_command = CreateOrderCommand(
        customer_id="CUST001",
        product_id="PROD123",
        quantity=2,
        price=999.99,
        delivery_address="Andheri East, Mumbai, Maharashtra 400069"
    )
    
    order_id = await system.execute_command(create_command)
    
    # 2. Order status update करें
    update_command = UpdateOrderStatusCommand(
        order_id=order_id,
        new_status=OrderStatus.CONFIRMED,
        reason="Payment successful"
    )
    
    await system.execute_command(update_command)
    
    # 3. Customer orders summary query करें
    summary_query = GetOrderSummaryQuery(customer_id="CUST001")
    summaries = await system.execute_query(summary_query)
    
    print("\n📋 Customer Order Summaries:")
    for summary in summaries:
        print(f"  Order: {summary.order_id[:8]}... | Amount: ₹{summary.total_amount} | Status: {summary.status}")
    
    # 4. Specific order details query करें
    details_query = GetOrderDetailsQuery(order_id=order_id)
    details = await system.execute_query(details_query)
    
    print(f"\n📊 Order Details for {order_id[:8]}...")
    print(f"  Customer: {details.customer_name}")
    print(f"  Product: {details.product_name}")
    print(f"  Total: ₹{details.total_amount}")
    print(f"  Status: {details.status}")
    print(f"  Address: {details.delivery_address}")
    
    print("\n✅ CQRS Demo completed successfully!")

if __name__ == "__main__":
    """
    Key CQRS Benefits demonstrated:
    1. Separate models for reads और writes
    2. Optimized queries बिना complex joins के
    3. Independent scaling of read/write sides
    4. Event-driven architecture support
    5. Better performance for high-scale e-commerce
    """
    asyncio.run(demonstrate_flipkart_cqrs())
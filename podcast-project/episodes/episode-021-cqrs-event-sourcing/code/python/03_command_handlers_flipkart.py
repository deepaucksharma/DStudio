#!/usr/bin/env python3
"""
Episode 21: CQRS/Event Sourcing - Command Handlers for Flipkart Order Processing
Author: Code Developer Agent
Description: Production-grade command handlers for Flipkart's order management system

Command Handlers हैं business logic का दिल
ये validate करते हैं, execute करते हैं, और events generate करते हैं
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
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

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

class InventoryStatus(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OUT_OF_STOCK = "out_of_stock"

# Commands - Intent to change state
@dataclass
class CreateOrderCommand:
    """Flipkart में नया order create करने का command"""
    customer_id: str
    items: List[Dict]  # [{'product_id': 'P123', 'quantity': 2, 'price': 999.99}]
    delivery_address: str
    payment_method: str
    coupon_code: Optional[str] = None
    delivery_instructions: Optional[str] = None

@dataclass
class ConfirmPaymentCommand:
    """Payment confirmation command"""
    order_id: str
    payment_id: str
    payment_method: str
    amount: float
    gateway_response: Dict

@dataclass
class UpdateInventoryCommand:
    """Inventory update command"""
    product_id: str
    quantity_change: int  # Positive for restock, negative for consumption
    reason: str
    reference_id: str  # Order ID या purchase order ID

@dataclass
class CancelOrderCommand:
    """Order cancellation command"""
    order_id: str
    reason: str
    cancelled_by: str  # customer, system, admin
    refund_required: bool = True

@dataclass
class UpdateOrderStatusCommand:
    """Order status update command"""
    order_id: str
    new_status: OrderStatus
    tracking_info: Optional[Dict] = None
    updated_by: str = "system"

# Domain Events
@dataclass
class OrderCreatedEvent:
    order_id: str
    customer_id: str
    items: List[Dict]
    total_amount: float
    delivery_address: str
    payment_method: str
    created_at: datetime

@dataclass
class PaymentConfirmedEvent:
    order_id: str
    payment_id: str
    amount: float
    payment_method: str
    confirmed_at: datetime

@dataclass
class InventoryUpdatedEvent:
    product_id: str
    old_quantity: int
    new_quantity: int
    change_amount: int
    reason: str
    reference_id: str
    updated_at: datetime

@dataclass
class OrderCancelledEvent:
    order_id: str
    reason: str
    cancelled_by: str
    refund_amount: float
    cancelled_at: datetime

@dataclass
class OrderStatusUpdatedEvent:
    order_id: str
    old_status: OrderStatus
    new_status: OrderStatus
    tracking_info: Optional[Dict]
    updated_by: str
    updated_at: datetime

# Base Command Handler
class CommandHandler(ABC):
    """Base command handler interface"""
    
    @abstractmethod
    async def handle(self, command: Any) -> Any:
        pass
    
    @abstractmethod
    def can_handle(self, command: Any) -> bool:
        pass

# Order Aggregate
class FlipkartOrder:
    """Flipkart Order aggregate with business logic"""
    
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.customer_id = None
        self.items = []
        self.total_amount = 0.0
        self.delivery_address = ""
        self.payment_method = ""
        self.payment_status = PaymentStatus.PENDING
        self.order_status = OrderStatus.PENDING
        self.created_at = None
        self.confirmed_at = None
        self.tracking_info = {}
        self.version = 0
        self._uncommitted_events = []
    
    def create_order(self, customer_id: str, items: List[Dict], 
                    delivery_address: str, payment_method: str):
        """नया order create करें"""
        # Business validation
        if not items:
            raise ValueError("Order में कम से कम एक item होना चाहिए")
        
        total = sum(item['quantity'] * item['price'] for item in items)
        if total <= 0:
            raise ValueError("Order amount valid होना चाहिए")
        
        # State update
        self.customer_id = customer_id
        self.items = items
        self.total_amount = total
        self.delivery_address = delivery_address
        self.payment_method = payment_method
        self.order_status = OrderStatus.PENDING
        self.payment_status = PaymentStatus.PENDING
        self.created_at = datetime.now()
        
        # Domain event
        event = OrderCreatedEvent(
            order_id=self.order_id,
            customer_id=customer_id,
            items=items,
            total_amount=total,
            delivery_address=delivery_address,
            payment_method=payment_method,
            created_at=self.created_at
        )
        
        self._add_event(event)
    
    def confirm_payment(self, payment_id: str, amount: float):
        """Payment confirm करें"""
        if self.payment_status != PaymentStatus.PENDING:
            raise ValueError(f"Payment already in {self.payment_status.value} state")
        
        if amount != self.total_amount:
            raise ValueError(f"Payment amount {amount} doesn't match order amount {self.total_amount}")
        
        self.payment_status = PaymentStatus.SUCCESS
        self.order_status = OrderStatus.CONFIRMED
        self.confirmed_at = datetime.now()
        
        event = PaymentConfirmedEvent(
            order_id=self.order_id,
            payment_id=payment_id,
            amount=amount,
            payment_method=self.payment_method,
            confirmed_at=self.confirmed_at
        )
        
        self._add_event(event)
    
    def update_status(self, new_status: OrderStatus, tracking_info: Dict = None, 
                     updated_by: str = "system"):
        """Order status update करें"""
        if new_status == self.order_status:
            return  # No change needed
        
        # Business rules for status transitions
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PACKED, OrderStatus.CANCELLED],
            OrderStatus.PACKED: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.RETURNED],
            OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED, OrderStatus.RETURNED],
            OrderStatus.DELIVERED: [OrderStatus.RETURNED],
            OrderStatus.CANCELLED: [],  # Final state
            OrderStatus.RETURNED: []   # Final state
        }
        
        if new_status not in valid_transitions.get(self.order_status, []):
            raise ValueError(f"Invalid status transition from {self.order_status.value} to {new_status.value}")
        
        old_status = self.order_status
        self.order_status = new_status
        if tracking_info:
            self.tracking_info.update(tracking_info)
        
        event = OrderStatusUpdatedEvent(
            order_id=self.order_id,
            old_status=old_status,
            new_status=new_status,
            tracking_info=tracking_info,
            updated_by=updated_by,
            updated_at=datetime.now()
        )
        
        self._add_event(event)
    
    def cancel_order(self, reason: str, cancelled_by: str):
        """Order cancel करें"""
        if self.order_status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED, OrderStatus.RETURNED]:
            raise ValueError(f"Cannot cancel order in {self.order_status.value} state")
        
        old_status = self.order_status
        self.order_status = OrderStatus.CANCELLED
        
        # Refund amount calculation
        refund_amount = self.total_amount if self.payment_status == PaymentStatus.SUCCESS else 0.0
        
        event = OrderCancelledEvent(
            order_id=self.order_id,
            reason=reason,
            cancelled_by=cancelled_by,
            refund_amount=refund_amount,
            cancelled_at=datetime.now()
        )
        
        self._add_event(event)
    
    def _add_event(self, event):
        """Event को uncommitted list में add करें"""
        self.version += 1
        self._uncommitted_events.append(event)
    
    def get_uncommitted_events(self):
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self):
        self._uncommitted_events.clear()

# Product Inventory Aggregate
class ProductInventory:
    """Product inventory management"""
    
    def __init__(self, product_id: str):
        self.product_id = product_id
        self.quantity = 0
        self.reserved_quantity = 0
        self.status = InventoryStatus.OUT_OF_STOCK
        self.last_updated = None
        self.version = 0
        self._uncommitted_events = []
    
    def update_quantity(self, quantity_change: int, reason: str, reference_id: str):
        """Inventory quantity update करें"""
        old_quantity = self.quantity
        new_quantity = self.quantity + quantity_change
        
        if new_quantity < 0:
            raise ValueError("Inventory quantity cannot be negative")
        
        self.quantity = new_quantity
        self.last_updated = datetime.now()
        
        # Status update
        if self.quantity > 0:
            self.status = InventoryStatus.AVAILABLE
        else:
            self.status = InventoryStatus.OUT_OF_STOCK
        
        event = InventoryUpdatedEvent(
            product_id=self.product_id,
            old_quantity=old_quantity,
            new_quantity=new_quantity,
            change_amount=quantity_change,
            reason=reason,
            reference_id=reference_id,
            updated_at=self.last_updated
        )
        
        self._add_event(event)
    
    def reserve_quantity(self, quantity: int, order_id: str):
        """Inventory reserve करें order के लिए"""
        if quantity > (self.quantity - self.reserved_quantity):
            raise ValueError("Not enough inventory available to reserve")
        
        self.reserved_quantity += quantity
        print(f"Reserved {quantity} units for order {order_id}")
    
    def release_reservation(self, quantity: int, order_id: str):
        """Reserved inventory को release करें"""
        if quantity > self.reserved_quantity:
            raise ValueError("Cannot release more than reserved quantity")
        
        self.reserved_quantity -= quantity
        print(f"Released {quantity} units reservation for order {order_id}")
    
    def _add_event(self, event):
        self.version += 1
        self._uncommitted_events.append(event)
    
    def get_uncommitted_events(self):
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self):
        self._uncommitted_events.clear()

# Command Handlers Implementation
class CreateOrderCommandHandler(CommandHandler):
    """Order creation command handler"""
    
    def __init__(self, order_repository, inventory_repository, pricing_service):
        self.order_repository = order_repository
        self.inventory_repository = inventory_repository
        self.pricing_service = pricing_service
    
    def can_handle(self, command: Any) -> bool:
        return isinstance(command, CreateOrderCommand)
    
    async def handle(self, command: CreateOrderCommand) -> str:
        """Order create करने का main business logic"""
        print(f"🛒 Processing order creation for customer {command.customer_id}")
        
        # 1. Validate customer and items
        await self._validate_command(command)
        
        # 2. Check inventory availability
        await self._check_inventory(command.items)
        
        # 3. Calculate pricing with discounts
        final_items = await self._calculate_pricing(command.items, command.coupon_code)
        
        # 4. Create order aggregate
        order_id = f"FL{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        order = FlipkartOrder(order_id)
        
        order.create_order(
            customer_id=command.customer_id,
            items=final_items,
            delivery_address=command.delivery_address,
            payment_method=command.payment_method
        )
        
        # 5. Reserve inventory
        await self._reserve_inventory(final_items, order_id)
        
        # 6. Save order
        await self.order_repository.save(order)
        
        print(f"✅ Order {order_id} created successfully!")
        return order_id
    
    async def _validate_command(self, command: CreateOrderCommand):
        """Command validation"""
        if not command.customer_id:
            raise ValueError("Customer ID required")
        
        if not command.items:
            raise ValueError("At least one item required")
        
        if not command.delivery_address:
            raise ValueError("Delivery address required")
        
        for item in command.items:
            if item['quantity'] <= 0:
                raise ValueError(f"Invalid quantity for product {item['product_id']}")
    
    async def _check_inventory(self, items: List[Dict]):
        """Inventory availability check"""
        for item in items:
            inventory = await self.inventory_repository.get_by_id(item['product_id'])
            if not inventory or inventory.quantity < item['quantity']:
                raise ValueError(f"Insufficient inventory for product {item['product_id']}")
    
    async def _calculate_pricing(self, items: List[Dict], coupon_code: str) -> List[Dict]:
        """Pricing calculation with discounts"""
        final_items = []
        
        for item in items:
            # Get current pricing (can be different from cached price)
            current_price = await self.pricing_service.get_current_price(item['product_id'])
            
            final_item = {
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'unit_price': current_price,
                'total_price': current_price * item['quantity']
            }
            
            final_items.append(final_item)
        
        # Apply coupon if applicable
        if coupon_code:
            discount = await self.pricing_service.apply_coupon(final_items, coupon_code)
            print(f"💰 Coupon {coupon_code} applied: ₹{discount} discount")
        
        return final_items
    
    async def _reserve_inventory(self, items: List[Dict], order_id: str):
        """Inventory को reserve करें"""
        for item in items:
            inventory = await self.inventory_repository.get_by_id(item['product_id'])
            inventory.reserve_quantity(item['quantity'], order_id)
            await self.inventory_repository.save(inventory)

class ConfirmPaymentCommandHandler(CommandHandler):
    """Payment confirmation handler"""
    
    def __init__(self, order_repository, payment_service):
        self.order_repository = order_repository
        self.payment_service = payment_service
    
    def can_handle(self, command: Any) -> bool:
        return isinstance(command, ConfirmPaymentCommand)
    
    async def handle(self, command: ConfirmPaymentCommand) -> bool:
        """Payment confirmation का business logic"""
        print(f"💳 Processing payment confirmation for order {command.order_id}")
        
        # 1. Validate payment with gateway
        is_valid = await self.payment_service.validate_payment(
            command.payment_id, command.amount, command.gateway_response
        )
        
        if not is_valid:
            raise ValueError("Payment validation failed")
        
        # 2. Load order
        order = await self.order_repository.get_by_id(command.order_id)
        if not order:
            raise ValueError(f"Order {command.order_id} not found")
        
        # 3. Confirm payment in order
        order.confirm_payment(command.payment_id, command.amount)
        
        # 4. Save order
        await self.order_repository.save(order)
        
        print(f"✅ Payment confirmed for order {command.order_id}")
        return True

class UpdateInventoryCommandHandler(CommandHandler):
    """Inventory update handler"""
    
    def __init__(self, inventory_repository):
        self.inventory_repository = inventory_repository
    
    def can_handle(self, command: Any) -> bool:
        return isinstance(command, UpdateInventoryCommand)
    
    async def handle(self, command: UpdateInventoryCommand) -> bool:
        """Inventory update का business logic"""
        print(f"📦 Updating inventory for product {command.product_id}")
        
        # Load inventory
        inventory = await self.inventory_repository.get_by_id(command.product_id)
        if not inventory:
            # Create new inventory if doesn't exist
            inventory = ProductInventory(command.product_id)
        
        # Update quantity
        inventory.update_quantity(
            command.quantity_change,
            command.reason,
            command.reference_id
        )
        
        # Save inventory
        await self.inventory_repository.save(inventory)
        
        print(f"✅ Inventory updated for product {command.product_id}")
        return True

class CancelOrderCommandHandler(CommandHandler):
    """Order cancellation handler"""
    
    def __init__(self, order_repository, inventory_repository, refund_service):
        self.order_repository = order_repository
        self.inventory_repository = inventory_repository
        self.refund_service = refund_service
    
    def can_handle(self, command: Any) -> bool:
        return isinstance(command, CancelOrderCommand)
    
    async def handle(self, command: CancelOrderCommand) -> bool:
        """Order cancellation का business logic"""
        print(f"❌ Processing order cancellation for {command.order_id}")
        
        # 1. Load order
        order = await self.order_repository.get_by_id(command.order_id)
        if not order:
            raise ValueError(f"Order {command.order_id} not found")
        
        # 2. Cancel order
        order.cancel_order(command.reason, command.cancelled_by)
        
        # 3. Release inventory reservations
        await self._release_inventory_reservations(order)
        
        # 4. Process refund if needed
        if command.refund_required and order.payment_status == PaymentStatus.SUCCESS:
            await self.refund_service.process_refund(
                order.order_id, order.total_amount, command.reason
            )
        
        # 5. Save order
        await self.order_repository.save(order)
        
        print(f"✅ Order {command.order_id} cancelled successfully")
        return True
    
    async def _release_inventory_reservations(self, order: FlipkartOrder):
        """Reserved inventory को release करें"""
        for item in order.items:
            inventory = await self.inventory_repository.get_by_id(item['product_id'])
            if inventory:
                inventory.release_reservation(item['quantity'], order.order_id)
                await self.inventory_repository.save(inventory)

# Command Bus - Central command dispatcher
class CommandBus:
    """Central command dispatcher for all commands"""
    
    def __init__(self):
        self._handlers: List[CommandHandler] = []
    
    def register_handler(self, handler: CommandHandler):
        """Command handler register करें"""
        self._handlers.append(handler)
    
    async def send(self, command: Any) -> Any:
        """Command को appropriate handler को send करें"""
        for handler in self._handlers:
            if handler.can_handle(command):
                try:
                    return await handler.handle(command)
                except Exception as e:
                    print(f"❌ Command handling failed: {e}")
                    raise e
        
        raise ValueError(f"No handler found for command {type(command).__name__}")

# Mock Services for demonstration
class MockPricingService:
    async def get_current_price(self, product_id: str) -> float:
        # Mock pricing logic
        base_prices = {
            'MOBILE001': 25999.0,
            'LAPTOP001': 65999.0,
            'BOOK001': 299.0
        }
        return base_prices.get(product_id, 999.0)
    
    async def apply_coupon(self, items: List[Dict], coupon_code: str) -> float:
        # Mock coupon logic
        total = sum(item['total_price'] for item in items)
        if coupon_code == "FLIPKART10":
            return total * 0.1  # 10% discount
        return 0.0

class MockPaymentService:
    async def validate_payment(self, payment_id: str, amount: float, gateway_response: Dict) -> bool:
        # Mock payment validation
        return gateway_response.get('status') == 'success'

class MockRefundService:
    async def process_refund(self, order_id: str, amount: float, reason: str):
        print(f"💰 Refund of ₹{amount} processed for order {order_id}")

class MockRepository:
    def __init__(self):
        self._data = {}
    
    async def save(self, aggregate):
        self._data[aggregate.order_id if hasattr(aggregate, 'order_id') else aggregate.product_id] = aggregate
        aggregate.mark_events_as_committed()
    
    async def get_by_id(self, id: str):
        return self._data.get(id)

# Demo Function
async def demonstrate_flipkart_command_handlers():
    """Flipkart command handlers का comprehensive demonstration"""
    print("🛒 Flipkart Command Handlers Demo")
    print("=" * 50)
    
    # Setup repositories and services
    order_repository = MockRepository()
    inventory_repository = MockRepository()
    pricing_service = MockPricingService()
    payment_service = MockPaymentService()
    refund_service = MockRefundService()
    
    # Setup command handlers
    create_order_handler = CreateOrderCommandHandler(order_repository, inventory_repository, pricing_service)
    confirm_payment_handler = ConfirmPaymentCommandHandler(order_repository, payment_service)
    update_inventory_handler = UpdateInventoryCommandHandler(inventory_repository)
    cancel_order_handler = CancelOrderCommandHandler(order_repository, inventory_repository, refund_service)
    
    # Setup command bus
    command_bus = CommandBus()
    command_bus.register_handler(create_order_handler)
    command_bus.register_handler(confirm_payment_handler)
    command_bus.register_handler(update_inventory_handler)
    command_bus.register_handler(cancel_order_handler)
    
    # 1. First, stock inventory
    print("\n📦 Stocking inventory...")
    inventory_commands = [
        UpdateInventoryCommand("MOBILE001", 100, "Initial stock", "PURCHASE001"),
        UpdateInventoryCommand("LAPTOP001", 50, "Initial stock", "PURCHASE002"),
        UpdateInventoryCommand("BOOK001", 200, "Initial stock", "PURCHASE003")
    ]
    
    for cmd in inventory_commands:
        await command_bus.send(cmd)
    
    # 2. Create order
    print("\n🛒 Creating new order...")
    create_command = CreateOrderCommand(
        customer_id="CUST001",
        items=[
            {'product_id': 'MOBILE001', 'quantity': 1, 'price': 25999.0},
            {'product_id': 'BOOK001', 'quantity': 2, 'price': 299.0}
        ],
        delivery_address="Bandra West, Mumbai, Maharashtra 400050",
        payment_method="UPI",
        coupon_code="FLIPKART10"
    )
    
    order_id = await command_bus.send(create_command)
    
    # 3. Confirm payment
    print("\n💳 Confirming payment...")
    payment_command = ConfirmPaymentCommand(
        order_id=order_id,
        payment_id="PAY123456",
        payment_method="UPI",
        amount=23698.2,  # After 10% discount
        gateway_response={'status': 'success', 'transaction_id': 'TXN789'}
    )
    
    await command_bus.send(payment_command)
    
    # 4. Cancel order (demonstration)
    print("\n❌ Cancelling order for demo...")
    cancel_command = CancelOrderCommand(
        order_id=order_id,
        reason="Customer requested cancellation",
        cancelled_by="customer",
        refund_required=True
    )
    
    await command_bus.send(cancel_command)
    
    print("\n✅ Command Handlers Demo completed successfully!")

if __name__ == "__main__":
    """
    Key Command Handler Benefits:
    1. Business logic centralization
    2. Consistent validation और error handling
    3. Transaction management
    4. Event sourcing integration
    5. Testable और maintainable code
    """
    asyncio.run(demonstrate_flipkart_command_handlers())
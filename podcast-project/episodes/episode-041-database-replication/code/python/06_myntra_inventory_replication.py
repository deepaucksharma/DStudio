#!/usr/bin/env python3
"""
Episode 41: Database Replication Strategies
Example 6: Myntra-style E-commerce Inventory Replication

यह example Myntra जैसे fashion e-commerce में inventory replication
का complex implementation दिखाता है। Size, color, variants के साथ
multi-dimensional inventory management include की गई है।

Real-world Use Case: Fashion E-commerce Platform
- Multi-variant product inventory (size, color, style)
- Regional warehouse distribution
- Real-time inventory synchronization
- Flash sale inventory management
"""

import asyncio
import time
import uuid
import json
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InventoryEventType(Enum):
    STOCK_IN = "stock_in"
    STOCK_OUT = "stock_out"
    RESERVE = "reserve"
    RELEASE = "release"
    TRANSFER = "transfer"
    DAMAGE = "damage"
    RETURN = "return"

class SaleType(Enum):
    REGULAR = "regular"
    FLASH_SALE = "flash_sale"
    CLEARANCE = "clearance"
    PRE_ORDER = "pre_order"

@dataclass
class ProductVariant:
    """Fashion product variant (size, color, style)"""
    sku: str
    product_id: str
    brand: str
    category: str
    sub_category: str
    size: str
    color: str
    style: str
    material: str
    gender: str
    base_price: float
    sale_price: Optional[float] = None
    
@dataclass
class InventoryItem:
    """Inventory item with location and status"""
    sku: str
    warehouse_id: str
    quantity_available: int
    quantity_reserved: int
    quantity_damaged: int
    reorder_level: int
    max_stock_level: int
    last_updated: datetime
    cost_price: float
    
@dataclass
class InventoryEvent:
    """Inventory change event"""
    event_id: str
    sku: str
    warehouse_id: str
    event_type: InventoryEventType
    quantity: int
    reason: str
    order_id: Optional[str]
    user_id: Optional[str]
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)

class MyntraWarehouseNode:
    """
    Myntra warehouse node with fashion inventory management
    Regional warehouse के लिए specialized inventory handling
    """
    
    def __init__(self, warehouse_id: str, region: str, location: str):
        self.warehouse_id = warehouse_id
        self.region = region
        self.location = location
        
        # Fashion inventory storage
        self.products: Dict[str, ProductVariant] = {}  # sku -> product
        self.inventory: Dict[str, InventoryItem] = {}  # sku -> inventory
        
        # Event log for replication
        self.event_log: List[InventoryEvent] = []
        self.event_sequence = 0
        
        # Replication network
        self.peer_warehouses: List['MyntraWarehouseNode'] = []
        self.replication_queue: asyncio.Queue = asyncio.Queue()
        
        # Flash sale management
        self.flash_sale_active = False
        self.flash_sale_products: Set[str] = set()
        
        # Performance metrics
        self.events_processed = 0
        self.replication_lag_ms = 0.0
        self.stock_outs_today = 0
        
        # Regional specialization
        self.regional_preferences: Dict[str, float] = {}  # category -> demand_factor
        
        # Initialize with fashion inventory
        self._initialize_fashion_inventory()
        
    def _initialize_fashion_inventory(self):
        """Initialize with popular fashion items"""
        
        # Popular Indian fashion brands and categories
        fashion_data = [
            # Men's Western Wear
            {"brand": "H&M", "category": "Men", "sub_category": "T-Shirts", "sizes": ["S", "M", "L", "XL", "XXL"], 
             "colors": ["Black", "White", "Navy", "Red", "Green"], "base_price": 999},
            {"brand": "Zara", "category": "Men", "sub_category": "Shirts", "sizes": ["S", "M", "L", "XL"], 
             "colors": ["White", "Blue", "Black", "Grey"], "base_price": 2999},
            
            # Women's Western Wear  
            {"brand": "Forever 21", "category": "Women", "sub_category": "Dresses", "sizes": ["XS", "S", "M", "L", "XL"], 
             "colors": ["Black", "Red", "Blue", "White", "Pink"], "base_price": 1599},
            {"brand": "Vero Moda", "category": "Women", "sub_category": "Tops", "sizes": ["XS", "S", "M", "L"], 
             "colors": ["Black", "White", "Pink", "Blue"], "base_price": 1299},
            
            # Indian Ethnic Wear
            {"brand": "W", "category": "Women", "sub_category": "Kurtas", "sizes": ["S", "M", "L", "XL"], 
             "colors": ["Red", "Blue", "Green", "Yellow", "Pink"], "base_price": 1999},
            {"brand": "Manyavar", "category": "Men", "sub_category": "Kurtas", "sizes": ["S", "M", "L", "XL", "XXL"], 
             "colors": ["White", "Cream", "Gold", "Maroon"], "base_price": 3999},
             
            # Footwear
            {"brand": "Nike", "category": "Unisex", "sub_category": "Sneakers", "sizes": ["6", "7", "8", "9", "10", "11"], 
             "colors": ["Black", "White", "Red", "Blue"], "base_price": 5999},
            {"brand": "Bata", "category": "Men", "sub_category": "Formal Shoes", "sizes": ["6", "7", "8", "9", "10"], 
             "colors": ["Black", "Brown"], "base_price": 2499},
        ]
        
        # Generate product variants
        for item in fashion_data:
            for size in item["sizes"]:
                for color in item["colors"]:
                    sku = f"{item['brand'][:3].upper()}{item['category'][:1]}{item['sub_category'][:2].upper()}{size}{color[:2].upper()}"
                    
                    variant = ProductVariant(
                        sku=sku,
                        product_id=f"{item['brand']}_{item['sub_category']}",
                        brand=item["brand"],
                        category=item["category"],
                        sub_category=item["sub_category"],
                        size=size,
                        color=color,
                        style="Regular",
                        material="Cotton",  # Default
                        gender=item["category"],
                        base_price=item["base_price"]
                    )
                    
                    self.products[sku] = variant
                    
                    # Initialize inventory
                    initial_stock = random.randint(20, 100)
                    inventory_item = InventoryItem(
                        sku=sku,
                        warehouse_id=self.warehouse_id,
                        quantity_available=initial_stock,
                        quantity_reserved=0,
                        quantity_damaged=0,
                        reorder_level=10,
                        max_stock_level=200,
                        last_updated=datetime.now(),
                        cost_price=item["base_price"] * 0.6  # 40% margin
                    )
                    
                    self.inventory[sku] = inventory_item
                    
        # Set regional preferences
        if "Mumbai" in self.location:
            self.regional_preferences = {"Western": 0.7, "Ethnic": 0.3}
        elif "Delhi" in self.location:
            self.regional_preferences = {"Western": 0.6, "Ethnic": 0.4}
        elif "Bangalore" in self.location:
            self.regional_preferences = {"Western": 0.8, "Ethnic": 0.2}
        else:
            self.regional_preferences = {"Western": 0.5, "Ethnic": 0.5}
            
    def add_peer_warehouse(self, peer: 'MyntraWarehouseNode'):
        """Add peer warehouse for replication"""
        self.peer_warehouses.append(peer)
        logger.info(f"Added peer warehouse {peer.location} to {self.location}")
        
    async def process_inventory_event(self, sku: str, event_type: InventoryEventType,
                                    quantity: int, reason: str, order_id: Optional[str] = None,
                                    metadata: Dict = None) -> Tuple[bool, str]:
        """
        Process inventory event with fashion-specific logic
        यहाँ Myntra के actual inventory operations simulate किए गए हैं
        """
        
        if sku not in self.inventory:
            return False, f"SKU {sku} not found in warehouse {self.warehouse_id}"
            
        # Create event
        event = InventoryEvent(
            event_id=f"EVT_{self.warehouse_id}_{self.event_sequence:06d}",
            sku=sku,
            warehouse_id=self.warehouse_id,
            event_type=event_type,
            quantity=quantity,
            reason=reason,
            order_id=order_id,
            user_id="SYSTEM",  # Would be actual user in real system
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.event_sequence += 1
        
        # Validate event
        if not self._validate_inventory_event(event):
            return False, "Event validation failed"
            
        # Apply event locally
        success = await self._apply_inventory_event(event)
        
        if success:
            # Add to event log
            self.event_log.append(event)
            self.events_processed += 1
            
            # Queue for replication
            await self.replication_queue.put(event)
            
            logger.info(f"{self.location}: {event_type.value} {quantity} units of {sku}")
            return True, event.event_id
        else:
            return False, "Failed to apply inventory event"
            
    def _validate_inventory_event(self, event: InventoryEvent) -> bool:
        """Validate inventory event according to fashion retail rules"""
        
        inventory_item = self.inventory[event.sku]
        
        if event.event_type == InventoryEventType.STOCK_OUT:
            # Check available stock
            available = inventory_item.quantity_available - inventory_item.quantity_reserved
            if available < event.quantity:
                logger.warning(f"Insufficient stock for {event.sku}: available={available}, requested={event.quantity}")
                return False
                
        elif event.event_type == InventoryEventType.RESERVE:
            # Check reservable stock
            if inventory_item.quantity_available < event.quantity:
                return False
                
        elif event.event_type == InventoryEventType.RELEASE:
            # Check reserved quantity
            if inventory_item.quantity_reserved < event.quantity:
                return False
                
        # Check max stock level for stock_in
        if event.event_type == InventoryEventType.STOCK_IN:
            total_after_addition = (inventory_item.quantity_available + 
                                  inventory_item.quantity_reserved + 
                                  event.quantity)
            if total_after_addition > inventory_item.max_stock_level:
                logger.warning(f"Exceeds max stock level for {event.sku}")
                return False
                
        return True
        
    async def _apply_inventory_event(self, event: InventoryEvent) -> bool:
        """Apply inventory event to local state"""
        
        try:
            inventory_item = self.inventory[event.sku]
            
            if event.event_type == InventoryEventType.STOCK_IN:
                inventory_item.quantity_available += event.quantity
                
            elif event.event_type == InventoryEventType.STOCK_OUT:
                inventory_item.quantity_available -= event.quantity
                
                # Check for stock out
                if inventory_item.quantity_available <= inventory_item.reorder_level:
                    self.stock_outs_today += 1
                    await self._trigger_reorder(event.sku)
                    
            elif event.event_type == InventoryEventType.RESERVE:
                inventory_item.quantity_available -= event.quantity
                inventory_item.quantity_reserved += event.quantity
                
            elif event.event_type == InventoryEventType.RELEASE:
                inventory_item.quantity_reserved -= event.quantity
                inventory_item.quantity_available += event.quantity
                
            elif event.event_type == InventoryEventType.DAMAGE:
                inventory_item.quantity_available -= event.quantity
                inventory_item.quantity_damaged += event.quantity
                
            elif event.event_type == InventoryEventType.RETURN:
                inventory_item.quantity_available += event.quantity
                
            inventory_item.last_updated = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply inventory event: {e}")
            return False
            
    async def _trigger_reorder(self, sku: str):
        """Trigger reorder when stock is low"""
        
        inventory_item = self.inventory[sku]
        product = self.products[sku]
        
        # Calculate reorder quantity based on regional demand
        base_reorder = inventory_item.max_stock_level - inventory_item.quantity_available
        
        # Adjust based on regional preferences
        category_key = "Western" if product.sub_category in ["T-Shirts", "Shirts", "Dresses", "Tops"] else "Ethnic"
        demand_factor = self.regional_preferences.get(category_key, 1.0)
        
        reorder_quantity = int(base_reorder * demand_factor)
        
        logger.info(f"Triggering reorder for {sku}: {reorder_quantity} units (regional factor: {demand_factor})")
        
        # In real system, this would create purchase order
        # For simulation, we'll auto-restock after delay
        await asyncio.sleep(1)  # Simulate procurement delay
        
        await self.process_inventory_event(
            sku, InventoryEventType.STOCK_IN, reorder_quantity, 
            "Auto reorder", metadata={"reorder": True, "demand_factor": demand_factor}
        )
        
    async def start_flash_sale(self, product_skus: List[str], duration_minutes: int = 60):
        """
        Start flash sale for specific products
        यहाँ Myntra के flash sale logic simulate की गई है
        """
        
        self.flash_sale_active = True
        self.flash_sale_products = set(product_skus)
        
        logger.info(f"{self.location}: Flash sale started for {len(product_skus)} products")
        
        # Apply flash sale prices
        for sku in product_skus:
            if sku in self.products:
                product = self.products[sku]
                if not product.sale_price:
                    # 30-50% discount for flash sale
                    discount = random.uniform(0.3, 0.5)
                    product.sale_price = round(product.base_price * (1 - discount), 2)
                    
        # Schedule end of flash sale
        asyncio.create_task(self._end_flash_sale_after_delay(duration_minutes))
        
    async def _end_flash_sale_after_delay(self, duration_minutes: int):
        """End flash sale after specified duration"""
        await asyncio.sleep(duration_minutes * 60)
        
        self.flash_sale_active = False
        
        # Remove sale prices
        for sku in self.flash_sale_products:
            if sku in self.products:
                self.products[sku].sale_price = None
                
        self.flash_sale_products.clear()
        logger.info(f"{self.location}: Flash sale ended")
        
    async def process_order(self, order_items: List[Tuple[str, int]], order_id: str) -> Tuple[bool, List[str]]:
        """
        Process customer order with inventory reservation
        Real Myntra order processing simulation
        """
        
        # First pass: Check availability and reserve
        reservation_events = []
        failed_skus = []
        
        for sku, quantity in order_items:
            if sku not in self.inventory:
                failed_skus.append(f"{sku}: Not available in this warehouse")
                continue
                
            inventory_item = self.inventory[sku]
            available = inventory_item.quantity_available - inventory_item.quantity_reserved
            
            if available < quantity:
                failed_skus.append(f"{sku}: Only {available} available, requested {quantity}")
                continue
                
            reservation_events.append((sku, quantity))
            
        # If any item failed, don't process order
        if failed_skus:
            return False, failed_skus
            
        # Reserve all items
        for sku, quantity in reservation_events:
            await self.process_inventory_event(
                sku, InventoryEventType.RESERVE, quantity, 
                "Order reservation", order_id,
                metadata={"order_processing": True}
            )
            
        logger.info(f"Order {order_id} processed successfully: {len(reservation_events)} items reserved")
        return True, []
        
    async def fulfill_order(self, order_items: List[Tuple[str, int]], order_id: str) -> bool:
        """Fulfill order by converting reservations to stock-out"""
        
        for sku, quantity in order_items:
            # Release reservation
            await self.process_inventory_event(
                sku, InventoryEventType.RELEASE, quantity,
                "Order fulfillment", order_id
            )
            
            # Stock out (shipment)
            await self.process_inventory_event(
                sku, InventoryEventType.STOCK_OUT, quantity,
                "Order shipment", order_id
            )
            
        logger.info(f"Order {order_id} fulfilled successfully")
        return True
        
    async def start_replication(self):
        """Start async replication to peer warehouses"""
        logger.info(f"Starting replication for {self.location}")
        
        while True:
            try:
                # Wait for events to replicate
                event = await asyncio.wait_for(self.replication_queue.get(), timeout=1.0)
                
                # Replicate to all peers
                replication_tasks = []
                for peer in self.peer_warehouses:
                    task = asyncio.create_task(peer.receive_replicated_event(event))
                    replication_tasks.append(task)
                    
                if replication_tasks:
                    # Async replication - fire and forget
                    asyncio.gather(*replication_tasks, return_exceptions=True)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Replication error in {self.location}: {e}")
                
    async def receive_replicated_event(self, event: InventoryEvent):
        """Receive and apply replicated event"""
        
        # Check if event already processed
        if any(e.event_id == event.event_id for e in self.event_log):
            return
            
        # Apply if SKU exists in this warehouse
        if event.sku in self.inventory:
            try:
                await self._apply_inventory_event(event)
                self.event_log.append(event)
                logger.debug(f"{self.location}: Applied replicated event {event.event_id}")
            except Exception as e:
                logger.error(f"Failed to apply replicated event: {e}")
                
    def get_inventory_summary(self) -> Dict:
        """Get inventory summary for dashboard"""
        
        total_skus = len(self.inventory)
        total_stock = sum(item.quantity_available for item in self.inventory.values())
        total_reserved = sum(item.quantity_reserved for item in self.inventory.values())
        low_stock_count = sum(1 for item in self.inventory.values() 
                             if item.quantity_available <= item.reorder_level)
        
        # Brand-wise summary
        brand_summary = defaultdict(lambda: {"stock": 0, "value": 0})
        for sku, inventory_item in self.inventory.items():
            product = self.products[sku]
            brand_summary[product.brand]["stock"] += inventory_item.quantity_available
            brand_summary[product.brand]["value"] += (inventory_item.quantity_available * product.base_price)
            
        return {
            "warehouse_id": self.warehouse_id,
            "location": self.location,
            "region": self.region,
            "total_skus": total_skus,
            "total_stock": total_stock,
            "total_reserved": total_reserved,
            "low_stock_count": low_stock_count,
            "stock_outs_today": self.stock_outs_today,
            "events_processed": self.events_processed,
            "flash_sale_active": self.flash_sale_active,
            "brand_summary": dict(brand_summary),
            "replication_lag_ms": self.replication_lag_ms
        }

class MyntraInventoryCluster:
    """Complete Myntra inventory cluster"""
    
    def __init__(self):
        # Create regional warehouses
        self.warehouses = {
            "MUM_WH": MyntraWarehouseNode("MUM_WH", "West", "Mumbai Fashion Hub"),
            "DEL_WH": MyntraWarehouseNode("DEL_WH", "North", "Delhi Fashion Center"),  
            "BLR_WH": MyntraWarehouseNode("BLR_WH", "South", "Bangalore Tech Fashion"),
            "CHE_WH": MyntraWarehouseNode("CHE_WH", "South", "Chennai Traditional Hub"),
            "KOL_WH": MyntraWarehouseNode("KOL_WH", "East", "Kolkata Cultural Fashion")
        }
        
        # Setup peer connections
        self._setup_replication_network()
        
    def _setup_replication_network(self):
        """Setup replication between warehouses"""
        warehouse_list = list(self.warehouses.values())
        
        for warehouse in warehouse_list:
            for peer in warehouse_list:
                if warehouse != peer:
                    warehouse.add_peer_warehouse(peer)
                    
    async def start_cluster(self):
        """Start all warehouse replication"""
        logger.info("Starting Myntra inventory cluster...")
        
        replication_tasks = []
        for warehouse in self.warehouses.values():
            task = asyncio.create_task(warehouse.start_replication())
            replication_tasks.append(task)
            
        return replication_tasks
        
    async def simulate_myntra_operations(self, duration_minutes: int = 3):
        """
        Simulate realistic Myntra operations
        Fashion e-commerce specific patterns
        """
        logger.info(f"Starting Myntra operations simulation for {duration_minutes} minutes...")
        
        import random
        start_time = time.time()
        operations_count = 0
        
        # Get sample SKUs for operations
        sample_warehouse = next(iter(self.warehouses.values()))
        all_skus = list(sample_warehouse.products.keys())
        
        while (time.time() - start_time) < (duration_minutes * 60):
            # Select random warehouse and operation
            warehouse = random.choice(list(self.warehouses.values()))
            
            # Simulate different operation patterns
            operation = random.choices(
                ["customer_order", "stock_in", "return", "damage", "transfer"],
                weights=[0.5, 0.2, 0.15, 0.1, 0.05]
            )[0]
            
            if operation == "customer_order":
                # Simulate customer order
                order_id = f"ORD_{int(time.time() * 1000)}"
                
                # Random 1-3 items per order
                order_items = []
                for _ in range(random.randint(1, 3)):
                    sku = random.choice(all_skus)
                    quantity = random.randint(1, 2)
                    order_items.append((sku, quantity))
                    
                success, errors = await warehouse.process_order(order_items, order_id)
                
                if success:
                    # Simulate fulfillment after short delay
                    await asyncio.sleep(0.1)
                    await warehouse.fulfill_order(order_items, order_id)
                    operations_count += 1
                    
            elif operation == "stock_in":
                # Simulate stock arrival
                sku = random.choice(all_skus)
                quantity = random.randint(10, 50)
                
                await warehouse.process_inventory_event(
                    sku, InventoryEventType.STOCK_IN, quantity,
                    "Vendor shipment", metadata={"vendor": "Fashion Supplier"}
                )
                operations_count += 1
                
            elif operation == "return":
                # Simulate customer return
                sku = random.choice(all_skus)
                quantity = random.randint(1, 3)
                
                await warehouse.process_inventory_event(
                    sku, InventoryEventType.RETURN, quantity,
                    "Customer return", metadata={"reason": "Size issue"}
                )
                operations_count += 1
                
            # High frequency operations
            await asyncio.sleep(0.1)
            
        logger.info(f"Myntra operations simulation completed: {operations_count} operations")
        return operations_count
        
    async def simulate_flash_sale(self):
        """Simulate Myntra flash sale across all warehouses"""
        logger.info("Starting flash sale simulation...")
        
        # Select products for flash sale
        sample_warehouse = next(iter(self.warehouses.values()))
        all_skus = list(sample_warehouse.products.keys())
        flash_sale_skus = random.sample(all_skus, min(20, len(all_skus)))
        
        # Start flash sale in all warehouses
        flash_sale_tasks = []
        for warehouse in self.warehouses.values():
            task = asyncio.create_task(warehouse.start_flash_sale(flash_sale_skus, duration_minutes=2))
            flash_sale_tasks.append(task)
            
        # Simulate high order volume during flash sale
        await asyncio.sleep(1)  # Let flash sale start
        
        order_count = 0
        for _ in range(50):  # 50 flash sale orders
            warehouse = random.choice(list(self.warehouses.values()))
            
            # Flash sale orders tend to be single item
            sku = random.choice(flash_sale_skus)
            order_id = f"FLASH_{int(time.time() * 1000)}_{order_count}"
            
            success, errors = await warehouse.process_order([(sku, 1)], order_id)
            if success:
                await warehouse.fulfill_order([(sku, 1)], order_id)
                order_count += 1
                
            await asyncio.sleep(0.05)  # High frequency during flash sale
            
        logger.info(f"Flash sale completed: {order_count} orders processed")
        return order_count
        
    def get_cluster_status(self) -> Dict:
        """Get complete cluster status"""
        
        return {
            "cluster_size": len(self.warehouses),
            "warehouses": {wh_id: wh.get_inventory_summary() for wh_id, wh in self.warehouses.items()}
        }

# Testing and demonstration
async def demonstrate_myntra_replication():
    """
    Complete demonstration of Myntra-style inventory replication
    Fashion e-commerce specific scenarios
    """
    print("\n" + "="*70)
    print("Myntra Fashion E-commerce Inventory Replication Demonstration")
    print("Episode 41: Database Replication Strategies")
    print("="*70)
    
    # Initialize cluster
    cluster = MyntraInventoryCluster()
    
    # Start replication
    replication_tasks = await cluster.start_cluster()
    
    # Show initial status
    logger.info("\n--- Initial Warehouse Status ---")
    for wh_id, warehouse in cluster.warehouses.items():
        summary = warehouse.get_inventory_summary()
        print(f"{warehouse.location}: {summary['total_stock']} items across {summary['total_skus']} SKUs")
        
    # Demonstrate fashion-specific operations
    logger.info("\n--- Fashion Operations Demo ---")
    
    mumbai_wh = cluster.warehouses["MUM_WH"]
    
    # Simulate popular product stock-out in Mumbai
    popular_sku = "H&MMTSS2BL"  # H&M Men's T-Shirt Size S Black
    await mumbai_wh.process_inventory_event(
        popular_sku, InventoryEventType.STOCK_OUT, 15,
        "High demand in Mumbai fashion week"
    )
    
    # Process a multi-item fashion order
    order_items = [
        ("H&MMTSS2BL", 1),  # H&M T-shirt
        ("ZAMWDRSMPK", 1),   # Zara Women's Dress
        ("NIKUNSNK6BL", 1)   # Nike Unisex Sneakers
    ]
    
    success, errors = await mumbai_wh.process_order(order_items, "FASHION_ORD_001")
    print(f"Fashion order processing: {'SUCCESS' if success else 'FAILED'}")
    
    if success:
        await mumbai_wh.fulfill_order(order_items, "FASHION_ORD_001")
        print("Fashion order fulfilled successfully")
        
    # Simulate flash sale
    logger.info("\n--- Flash Sale Simulation ---")
    flash_orders = await cluster.simulate_flash_sale()
    print(f"Flash sale processed {flash_orders} orders")
    
    # High-volume operations
    logger.info("\n--- High-Volume Operations ---")
    operations_count = await cluster.simulate_myntra_operations(duration_minutes=1)
    print(f"Processed {operations_count} fashion operations")
    
    # Wait for replication to settle
    await asyncio.sleep(2)
    
    # Final status
    logger.info("\n--- Final Cluster Status ---")
    final_status = cluster.get_cluster_status()
    
    print(f"\nWarehouse Summary:")
    for wh_id, wh_summary in final_status['warehouses'].items():
        print(f"  {wh_summary['location']}:")
        print(f"    Total Stock: {wh_summary['total_stock']}")
        print(f"    Reserved: {wh_summary['total_reserved']}")
        print(f"    Low Stock Items: {wh_summary['low_stock_count']}")
        print(f"    Events Processed: {wh_summary['events_processed']}")
        
        # Show top brands by stock value
        brands = sorted(wh_summary['brand_summary'].items(), 
                       key=lambda x: x[1]['value'], reverse=True)[:3]
        print(f"    Top Brands: {', '.join([f'{b[0]} (₹{b[1]['value']:,.0f})' for b in brands])}")
        
    # Regional analysis
    logger.info("\n--- Regional Analysis ---")
    regional_data = defaultdict(lambda: {"total_stock": 0, "total_value": 0})
    
    for wh_id, wh_summary in final_status['warehouses'].items():
        region = cluster.warehouses[wh_id].region
        regional_data[region]["total_stock"] += wh_summary['total_stock']
        
        for brand, brand_data in wh_summary['brand_summary'].items():
            regional_data[region]["total_value"] += brand_data['value']
            
    for region, data in regional_data.items():
        print(f"{region} Region: {data['total_stock']} items, ₹{data['total_value']:,.0f} value")

if __name__ == "__main__":
    print("Myntra Fashion E-commerce Inventory Replication")
    print("Episode 41: Database Replication Strategies")
    print("Demonstrating complex fashion inventory management with replication...")
    
    # Run the demonstration
    asyncio.run(demonstrate_myntra_replication())
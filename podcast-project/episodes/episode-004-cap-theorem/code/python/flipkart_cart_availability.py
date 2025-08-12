#!/usr/bin/env python3
"""
Flipkart Cart Availability System - Episode 4
E-commerce में availability-first approach का practical implementation

यह system दिखाता है कि कैसे Flipkart जैसे Indian e-commerce platforms
high availability maintain करते हैं, even during:
- Flash sales (Big Billion Day)
- Network partitions (ISP failures)
- Server crashes (AWS/Azure outages)
- Peak traffic (festival seasons)

CAP Trade-off: Availability + Partition Tolerance > Consistency
"""

import time
import threading
import uuid
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import random
from collections import defaultdict
import hashlib

class ProductCategory(Enum):
    """Flipkart product categories"""
    ELECTRONICS = "electronics"       # Mobile, laptop
    FASHION = "fashion"               # Clothing, shoes
    HOME_KITCHEN = "home_kitchen"     # Appliances, furniture  
    BOOKS = "books"                   # Books, stationery
    GROCERY = "grocery"               # Food items, daily needs

class CartAction(Enum):
    """Shopping cart operations"""
    ADD_ITEM = "add_item"
    REMOVE_ITEM = "remove_item"
    UPDATE_QUANTITY = "update_quantity"
    CLEAR_CART = "clear_cart"
    APPLY_COUPON = "apply_coupon"

class NodeStatus(Enum):
    """Data center status"""
    ACTIVE = "active"                 # Normal operations
    DEGRADED = "degraded"            # Partial functionality
    FAILED = "failed"                # Node down
    RECOVERING = "recovering"         # Coming back online

@dataclass
class Product:
    """Flipkart product representation"""
    product_id: str
    name: str
    category: ProductCategory
    price: float
    available_stock: int
    seller: str = "Flipkart"
    is_in_sale: bool = False
    sale_discount: float = 0.0
    
    def get_effective_price(self) -> float:
        """Calculate price after discount"""
        if self.is_in_sale:
            return self.price * (1 - self.sale_discount)
        return self.price

@dataclass  
class CartItem:
    """Shopping cart item"""
    product_id: str
    quantity: int
    added_timestamp: datetime
    user_id: str
    session_id: str
    
    def __post_init__(self):
        if not isinstance(self.added_timestamp, datetime):
            self.added_timestamp = datetime.now()

@dataclass
class ShoppingCart:
    """User shopping cart with metadata"""
    user_id: str
    session_id: str
    items: Dict[str, CartItem] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    applied_coupons: List[str] = field(default_factory=list)
    total_value: float = 0.0
    version: int = 1  # For conflict resolution
    
    def add_item(self, product_id: str, quantity: int):
        """Add item to cart with availability check"""
        if product_id in self.items:
            self.items[product_id].quantity += quantity
        else:
            self.items[product_id] = CartItem(
                product_id=product_id,
                quantity=quantity,
                added_timestamp=datetime.now(),
                user_id=self.user_id,
                session_id=self.session_id
            )
        self.last_updated = datetime.now()
        self.version += 1

class FlipkartAvailabilitySystem:
    """
    Flipkart high-availability shopping cart system
    
    Design principles:
    1. Always accept cart operations (availability first)
    2. Handle conflicts during checkout (eventual consistency)
    3. Graceful degradation during failures
    4. Cross-region replication for disaster recovery
    
    Real scenarios:
    - Big Billion Day traffic spikes
    - Regional internet outages  
    - Flash sale inventory conflicts
    - Mobile app offline mode
    """
    
    def __init__(self, num_regions: int = 4):
        # Multi-region setup (like Flipkart's actual infrastructure)
        self.regions = {
            "MUMBAI": {"status": NodeStatus.ACTIVE, "carts": {}, "products": {}, "load": 0},
            "DELHI": {"status": NodeStatus.ACTIVE, "carts": {}, "products": {}, "load": 0},
            "BANGALORE": {"status": NodeStatus.ACTIVE, "carts": {}, "products": {}, "load": 0},
            "HYDERABAD": {"status": NodeStatus.ACTIVE, "carts": {}, "products": {}, "load": 0}
        }
        
        # System metrics
        self.total_requests = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.conflict_resolutions = 0
        self.partition_events = 0
        
        # Conflict resolution and sync
        self.pending_sync = defaultdict(list)
        self.conflict_resolution_strategies = {
            "last_writer_wins": self._resolve_last_writer_wins,
            "merge_carts": self._resolve_merge_carts,
            "user_preference": self._resolve_user_preference
        }
        
        # Background processes
        self.sync_thread = None
        self.health_check_thread = None
        self.is_running = True
        
        print(f"🛒 Flipkart Availability System initialized")
        print(f"🌍 Regions: {list(self.regions.keys())}")
        print(f"⚡ Focus: High Availability + Partition Tolerance")
        
        # Initialize sample data
        self._initialize_sample_data()
        self._start_background_processes()

    def _initialize_sample_data(self):
        """Initialize sample products - Indian e-commerce favorites"""
        sample_products = [
            Product("PHONE001", "Samsung Galaxy S23", ProductCategory.ELECTRONICS, 65000.0, 100, "Samsung Official"),
            Product("LAPTOP001", "MacBook Air M2", ProductCategory.ELECTRONICS, 115000.0, 50, "Apple Store"),
            Product("SHIRT001", "Allen Solly Formal Shirt", ProductCategory.FASHION, 1500.0, 200, "Allen Solly"),
            Product("BOOK001", "Wings of Fire - A.P.J. Abdul Kalam", ProductCategory.BOOKS, 350.0, 500, "Flipkart"),
            Product("MIXER001", "Preethi Mixer Grinder", ProductCategory.HOME_KITCHEN, 4500.0, 80, "Preethi Official"),
            Product("RICE001", "Basmati Rice 5kg", ProductCategory.GROCERY, 450.0, 1000, "India Gate")
        ]
        
        # Replicate products across all regions  
        for region in self.regions:
            for product in sample_products:
                self.regions[region]["products"][product.product_id] = product
        
        print("✅ Sample products initialized across all regions")

    def _start_background_processes(self):
        """Start background sync and health check processes"""
        self.sync_thread = threading.Thread(target=self._background_sync_process, daemon=True)
        self.health_check_thread = threading.Thread(target=self._health_check_process, daemon=True)
        
        self.sync_thread.start()
        self.health_check_thread.start()
        print("🔄 Background processes started (sync + health check)")

    def _get_preferred_region(self, user_id: str) -> str:
        """
        Get user's preferred region based on geography/load balancing
        Real में यह user के location और current load के basis पर decide होता है
        """
        active_regions = [region for region, data in self.regions.items() 
                         if data["status"] == NodeStatus.ACTIVE]
        
        if not active_regions:
            return None
        
        # Simple load balancing - choose region with lowest load
        return min(active_regions, key=lambda r: self.regions[r]["load"])

    def add_to_cart(self, user_id: str, product_id: str, quantity: int, 
                   session_id: str = None) -> Tuple[bool, str, Dict]:
        """
        Add item to shopping cart with high availability guarantee
        
        यह function हमेशा success return करने की कोशिश करता है,
        भले ही कुछ regions down हों या inventory conflicts हों।
        """
        self.total_requests += 1
        
        if not session_id:
            session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"
        
        print(f"\n🛍️  Adding to cart: User {user_id}, Product {product_id}, Qty {quantity}")
        
        # Step 1: Choose best available region
        preferred_region = self._get_preferred_region(user_id)
        if not preferred_region:
            self.failed_operations += 1
            return False, "All regions unavailable", {}
        
        # Step 2: Try primary region first
        success, message, cart_data = self._add_to_cart_region(
            user_id, product_id, quantity, session_id, preferred_region
        )
        
        if success:
            # Step 3: Async replication to other regions (fire and forget for availability)
            self._async_replicate_cart_operation(
                user_id, CartAction.ADD_ITEM, product_id, quantity, session_id
            )
            
            self.successful_operations += 1
            print(f"✅ Item added successfully in region {preferred_region}")
            return True, f"Added to cart successfully", cart_data
        
        # Step 4: Fallback to other regions if primary fails
        for region in self.regions:
            if region != preferred_region and self.regions[region]["status"] == NodeStatus.ACTIVE:
                success, message, cart_data = self._add_to_cart_region(
                    user_id, product_id, quantity, session_id, region
                )
                if success:
                    self.successful_operations += 1
                    print(f"✅ Item added via fallback region {region}")
                    return True, f"Added via backup region", cart_data
        
        # If all regions fail, still accept the request (availability first!)
        # Store in pending queue for later processing
        self.pending_sync[user_id].append({
            "action": CartAction.ADD_ITEM,
            "product_id": product_id,
            "quantity": quantity,
            "session_id": session_id,
            "timestamp": datetime.now(),
            "status": "pending"
        })
        
        self.successful_operations += 1  # We accepted the request
        print(f"📥 Request queued for later processing (graceful degradation)")
        return True, "Request accepted - will be processed when system recovers", {}

    def _add_to_cart_region(self, user_id: str, product_id: str, quantity: int, 
                           session_id: str, region: str) -> Tuple[bool, str, Dict]:
        """Add item to cart in specific region"""
        try:
            region_data = self.regions[region]
            
            # Check product availability
            if product_id not in region_data["products"]:
                return False, "Product not found", {}
            
            product = region_data["products"][product_id]
            
            # For high availability, we accept the request even with low stock
            # (conflict resolution happens at checkout)
            
            # Get or create cart
            cart_key = f"{user_id}_{session_id}"
            if cart_key not in region_data["carts"]:
                region_data["carts"][cart_key] = ShoppingCart(
                    user_id=user_id,
                    session_id=session_id
                )
            
            cart = region_data["carts"][cart_key]
            cart.add_item(product_id, quantity)
            
            # Update load metrics
            region_data["load"] += 1
            
            # Calculate cart value
            cart_value = self._calculate_cart_value(cart, region)
            cart.total_value = cart_value
            
            cart_info = {
                "cart_id": cart_key,
                "total_items": len(cart.items),
                "total_value": cart_value,
                "region": region,
                "last_updated": cart.last_updated.isoformat(),
                "version": cart.version
            }
            
            return True, "Added successfully", cart_info
            
        except Exception as e:
            print(f"❌ Error in region {region}: {e}")
            return False, str(e), {}

    def _calculate_cart_value(self, cart: ShoppingCart, region: str) -> float:
        """Calculate total cart value"""
        total = 0.0
        region_data = self.regions[region]
        
        for product_id, cart_item in cart.items.items():
            if product_id in region_data["products"]:
                product = region_data["products"][product_id]
                total += product.get_effective_price() * cart_item.quantity
        
        return total

    def _async_replicate_cart_operation(self, user_id: str, action: CartAction, 
                                       product_id: str, quantity: int, session_id: str):
        """
        Asynchronously replicate cart operations to other regions
        यह eventual consistency के लिए है - immediate availability के साथ
        """
        def replicate():
            time.sleep(0.1)  # Simulate network delay
            
            for region in self.regions:
                if self.regions[region]["status"] == NodeStatus.ACTIVE:
                    try:
                        if action == CartAction.ADD_ITEM:
                            self._add_to_cart_region(user_id, product_id, quantity, session_id, region)
                    except:
                        # Silent failure for async replication (availability focus)
                        pass
        
        thread = threading.Thread(target=replicate, daemon=True)
        thread.start()

    def get_cart(self, user_id: str, session_id: str = None) -> Tuple[bool, Dict]:
        """
        Retrieve shopping cart with consistency check
        
        यह function different regions से cart data fetch करके
        conflicts को detect और resolve करता है
        """
        self.total_requests += 1
        
        if not session_id:
            # Find most recent session for user
            session_id = self._find_latest_session(user_id)
            if not session_id:
                return False, {"error": "No cart found for user"}
        
        cart_key = f"{user_id}_{session_id}"
        carts_from_regions = {}
        
        # Fetch cart from all available regions
        for region, region_data in self.regions.items():
            if region_data["status"] == NodeStatus.ACTIVE:
                if cart_key in region_data["carts"]:
                    carts_from_regions[region] = region_data["carts"][cart_key]
        
        if not carts_from_regions:
            return False, {"error": "Cart not found in any region"}
        
        # Check for conflicts between regions
        if len(carts_from_regions) > 1:
            resolved_cart = self._resolve_cart_conflicts(carts_from_regions, user_id)
            self.conflict_resolutions += 1
        else:
            resolved_cart = list(carts_from_regions.values())[0]
        
        # Calculate final cart details
        best_region = self._get_preferred_region(user_id)
        cart_value = self._calculate_cart_value(resolved_cart, best_region)
        
        cart_details = {
            "user_id": user_id,
            "session_id": session_id,
            "total_items": len(resolved_cart.items),
            "total_value": cart_value,
            "items": [],
            "created_at": resolved_cart.created_at.isoformat(),
            "last_updated": resolved_cart.last_updated.isoformat(),
            "applied_coupons": resolved_cart.applied_coupons,
            "version": resolved_cart.version,
            "regions_checked": list(carts_from_regions.keys()),
            "conflicts_resolved": len(carts_from_regions) > 1
        }
        
        # Add item details
        best_region_data = self.regions[best_region]
        for product_id, cart_item in resolved_cart.items.items():
            if product_id in best_region_data["products"]:
                product = best_region_data["products"][product_id]
                cart_details["items"].append({
                    "product_id": product_id,
                    "name": product.name,
                    "quantity": cart_item.quantity,
                    "unit_price": product.get_effective_price(),
                    "total_price": product.get_effective_price() * cart_item.quantity,
                    "added_at": cart_item.added_timestamp.isoformat()
                })
        
        self.successful_operations += 1
        return True, cart_details

    def _find_latest_session(self, user_id: str) -> Optional[str]:
        """Find user's most recent session across all regions"""
        latest_session = None
        latest_time = None
        
        for region_data in self.regions.values():
            for cart_key, cart in region_data["carts"].items():
                if cart.user_id == user_id:
                    if latest_time is None or cart.last_updated > latest_time:
                        latest_time = cart.last_updated
                        latest_session = cart.session_id
        
        return latest_session

    def _resolve_cart_conflicts(self, carts_from_regions: Dict[str, ShoppingCart], 
                               user_id: str) -> ShoppingCart:
        """
        Resolve conflicts between cart versions from different regions
        
        Strategy: Merge carts और user को best experience देना
        """
        print(f"🔄 Resolving cart conflicts for user {user_id}")
        print(f"   Regions involved: {list(carts_from_regions.keys())}")
        
        # Strategy 1: Use newest cart as base
        newest_cart = max(carts_from_regions.values(), key=lambda c: c.last_updated)
        base_cart = ShoppingCart(
            user_id=newest_cart.user_id,
            session_id=newest_cart.session_id,
            created_at=newest_cart.created_at,
            last_updated=datetime.now(),
            version=newest_cart.version + 1
        )
        
        # Strategy 2: Merge all items (maximum quantity wins)
        all_items = {}
        for cart in carts_from_regions.values():
            for product_id, item in cart.items.items():
                if product_id not in all_items:
                    all_items[product_id] = item
                else:
                    # Take maximum quantity (user-friendly approach)
                    if item.quantity > all_items[product_id].quantity:
                        all_items[product_id] = item
        
        base_cart.items = all_items
        
        # Strategy 3: Merge coupons
        all_coupons = set()
        for cart in carts_from_regions.values():
            all_coupons.update(cart.applied_coupons)
        base_cart.applied_coupons = list(all_coupons)
        
        print(f"✅ Conflict resolved: {len(all_items)} unique items, {len(all_coupons)} coupons")
        
        return base_cart

    def simulate_flash_sale(self, product_id: str, duration: int = 30, 
                           concurrent_users: int = 100):
        """
        Simulate Flipkart flash sale scenario - Big Billion Day style
        
        यह test करता है कि system high load और conflicts को
        कैसे handle करता है availability को maintain करते हुए
        """
        print(f"\n🔥 FLASH SALE SIMULATION STARTED")
        print(f"   Product: {product_id}")
        print(f"   Duration: {duration} seconds")
        print(f"   Concurrent users: {concurrent_users}")
        print(f"   Focus: Maintain availability during peak load")
        
        # Reset metrics
        start_time = time.time()
        initial_requests = self.total_requests
        initial_successful = self.successful_operations
        initial_failed = self.failed_operations
        
        def simulate_user_behavior(user_id: int):
            """Simulate individual user behavior during flash sale"""
            try:
                # Random delays to simulate real user behavior
                time.sleep(random.uniform(0, 5))
                
                # Add multiple items quickly (typical flash sale behavior)
                for i in range(random.randint(1, 3)):
                    success, message, cart_data = self.add_to_cart(
                        user_id=f"user_{user_id}",
                        product_id=product_id,
                        quantity=random.randint(1, 2),
                        session_id=f"flash_session_{user_id}"
                    )
                    
                    # Small delay between adds
                    time.sleep(random.uniform(0.1, 0.5))
                
                # Some users also check their cart
                if random.random() < 0.3:  # 30% users check cart
                    time.sleep(random.uniform(0.2, 1.0))
                    self.get_cart(f"user_{user_id}", f"flash_session_{user_id}")
                
            except Exception as e:
                print(f"User {user_id} simulation error: {e}")
        
        # Launch concurrent user simulations
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            for user_id in range(concurrent_users):
                future = executor.submit(simulate_user_behavior, user_id)
                futures.append(future)
            
            # Wait for all users to complete or timeout
            for future in futures:
                try:
                    future.result(timeout=duration)
                except Exception as e:
                    pass  # Continue even if individual users fail
        
        # Calculate flash sale results
        end_time = time.time()
        actual_duration = end_time - start_time
        
        requests_processed = self.total_requests - initial_requests
        successful_ops = self.successful_operations - initial_successful
        failed_ops = self.failed_operations - initial_failed
        
        success_rate = (successful_ops / requests_processed * 100) if requests_processed > 0 else 0
        
        print(f"\n📊 FLASH SALE RESULTS:")
        print(f"   Duration: {actual_duration:.2f} seconds")
        print(f"   Total requests: {requests_processed}")
        print(f"   Successful operations: {successful_ops}")
        print(f"   Failed operations: {failed_ops}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Requests/second: {requests_processed/actual_duration:.1f}")
        print(f"   Conflict resolutions: {self.conflict_resolutions}")
        
        # Check system health after flash sale
        active_regions = sum(1 for region_data in self.regions.values() 
                           if region_data["status"] == NodeStatus.ACTIVE)
        print(f"   Active regions after sale: {active_regions}/{len(self.regions)}")
        
        if success_rate > 95:
            print("🎉 EXCELLENT: System maintained high availability during flash sale!")
        elif success_rate > 90:
            print("✅ GOOD: System handled flash sale well with minor issues")
        else:
            print("⚠️  WARNING: System struggled during flash sale")

    def simulate_region_failure(self, region: str, duration: int = 10):
        """
        Simulate regional failure - जैसे AWS region down हो जाना
        """
        print(f"\n💥 REGION FAILURE SIMULATION: {region} going down for {duration}s")
        
        if region not in self.regions:
            print(f"❌ Region {region} not found")
            return
        
        # Mark region as failed
        original_status = self.regions[region]["status"]
        self.regions[region]["status"] = NodeStatus.FAILED
        self.partition_events += 1
        
        print(f"🔴 Region {region} marked as FAILED")
        print(f"📊 Testing availability during regional outage...")
        
        # Test operations during failure
        test_results = []
        for i in range(5):
            success, message, cart_data = self.add_to_cart(
                user_id=f"test_user_{i}",
                product_id="PHONE001",
                quantity=1
            )
            test_results.append(success)
            time.sleep(1)
        
        successful_during_failure = sum(test_results)
        print(f"✅ Operations successful during failure: {successful_during_failure}/5")
        
        # Simulate recovery
        time.sleep(duration)
        
        print(f"🔄 Region {region} recovering...")
        self.regions[region]["status"] = NodeStatus.RECOVERING
        time.sleep(2)
        
        self.regions[region]["status"] = original_status
        print(f"✅ Region {region} fully recovered")

    def _background_sync_process(self):
        """
        Background process for eventual consistency
        यह process pending operations को process करता है
        """
        while self.is_running:
            try:
                # Process pending sync operations
                for user_id, pending_ops in list(self.pending_sync.items()):
                    if not pending_ops:
                        continue
                    
                    # Try to process pending operations
                    processed_ops = []
                    for op in pending_ops:
                        if op["action"] == CartAction.ADD_ITEM:
                            success, _, _ = self.add_to_cart(
                                user_id=user_id,
                                product_id=op["product_id"],
                                quantity=op["quantity"],
                                session_id=op["session_id"]
                            )
                            if success:
                                processed_ops.append(op)
                    
                    # Remove processed operations
                    for op in processed_ops:
                        pending_ops.remove(op)
                
                time.sleep(5)  # Sync interval
                
            except Exception as e:
                print(f"Background sync error: {e}")
                time.sleep(1)

    def _health_check_process(self):
        """Background health monitoring"""
        while self.is_running:
            try:
                for region, region_data in self.regions.items():
                    # Simulate random health check
                    if region_data["status"] == NodeStatus.ACTIVE:
                        # Occasionally mark regions as degraded (simulate real issues)
                        if random.random() < 0.001:  # 0.1% chance
                            region_data["status"] = NodeStatus.DEGRADED
                            print(f"⚠️  Region {region} degraded due to health check")
                            
                            # Auto-recovery after some time
                            def auto_recover():
                                time.sleep(random.uniform(10, 30))
                                if region_data["status"] == NodeStatus.DEGRADED:
                                    region_data["status"] = NodeStatus.ACTIVE
                                    print(f"✅ Region {region} auto-recovered")
                            
                            threading.Thread(target=auto_recover, daemon=True).start()
                
                time.sleep(10)  # Health check interval
                
            except Exception as e:
                print(f"Health check error: {e}")
                time.sleep(5)

    def get_system_metrics(self) -> Dict:
        """Get comprehensive system metrics"""
        active_regions = sum(1 for data in self.regions.values() 
                           if data["status"] == NodeStatus.ACTIVE)
        
        total_carts = sum(len(data["carts"]) for data in self.regions.values())
        avg_load = sum(data["load"] for data in self.regions.values()) / len(self.regions)
        
        success_rate = 0
        if self.total_requests > 0:
            success_rate = (self.successful_operations / self.total_requests) * 100
        
        return {
            "total_requests": self.total_requests,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": f"{success_rate:.2f}%",
            "active_regions": f"{active_regions}/{len(self.regions)}",
            "total_carts": total_carts,
            "average_load": f"{avg_load:.1f}",
            "conflict_resolutions": self.conflict_resolutions,
            "partition_events": self.partition_events,
            "pending_sync_operations": sum(len(ops) for ops in self.pending_sync.values())
        }

def main():
    """
    Main demonstration - Flipkart availability scenarios
    """
    print("🛒 Flipkart Cart Availability System Demo")
    print("=" * 55)
    
    # Initialize system
    flipkart = FlipkartAvailabilitySystem()
    
    # Scenario 1: Normal shopping experience
    print("\n📱 SCENARIO 1: Normal Shopping Experience")
    
    # User adds items to cart
    success, message, cart_info = flipkart.add_to_cart("customer_001", "PHONE001", 1)
    print(f"Add phone to cart: {message}")
    
    success, message, cart_info = flipkart.add_to_cart("customer_001", "SHIRT001", 2)
    print(f"Add shirts to cart: {message}")
    
    # Check cart
    success, cart_details = flipkart.get_cart("customer_001")
    if success:
        print(f"Cart total: ₹{cart_details['total_value']:.2f} ({cart_details['total_items']} items)")
    
    # Scenario 2: Regional failure handling
    print("\n🌪️  SCENARIO 2: Regional Outage Handling")
    flipkart.simulate_region_failure("MUMBAI", duration=5)
    
    # Scenario 3: Flash sale simulation
    print("\n⚡ SCENARIO 3: Flash Sale Load Test")
    flipkart.simulate_flash_sale("PHONE001", duration=10, concurrent_users=20)
    
    # Scenario 4: System metrics and health
    print("\n📊 SCENARIO 4: System Health Report")
    metrics = flipkart.get_system_metrics()
    print("System Metrics:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    # Final system state
    print(f"\n✅ Flipkart availability demo completed!")
    print(f"Key learnings:")
    print(f"1. E-commerce prioritizes availability over consistency")
    print(f"2. Graceful degradation during failures")
    print(f"3. Eventual consistency with conflict resolution")
    print(f"4. Regional failover for disaster recovery")
    print(f"5. Flash sales test system's availability limits")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 6: Distributed Trace Correlation System

भारतीय context: Flipkart checkout flow की तरह multi-service tracing
जैसे shopping cart se payment gateway tak का complete journey track करना

Real-world scenario: BBD 2024 के दौरान 5 crore orders process करना
Challenge: 50+ microservices में correlation maintain करना
"""

import uuid
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
import structlog
import asyncio
from contextlib import asynccontextmanager

# भारतीय e-commerce services की detailed tracing setup
@dataclass
class IndianEcommerceService:
    """भारतीय e-commerce platform की service definition"""
    name: str
    version: str
    region: str  # Mumbai, Bangalore, Delhi
    tier: str  # metro, tier2, tier3
    capacity: int  # requests per second
    latency_sla: float  # milliseconds
    
class FlipkartTraceCorrelator:
    """
    Flipkart-style distributed tracing system
    
    Features:
    - Multi-service correlation 
    - Indian regional tracking
    - Festival season load handling
    - Payment gateway correlation
    - Customer journey mapping
    """
    
    def __init__(self, service_name: str, region: str = "mumbai"):
        self.service_name = service_name
        self.region = region
        self.correlation_cache = {}  # user_id -> trace_context mapping
        
        # Initialize OpenTelemetry setup
        self._setup_tracing()
        self.tracer = trace.get_tracer(__name__)
        
        # Indian payment gateways और services
        self.indian_services = {
            "checkout": IndianEcommerceService("checkout-service", "v2.1", region, "metro", 5000, 100),
            "inventory": IndianEcommerceService("inventory-service", "v1.8", region, "metro", 8000, 50),
            "payment": IndianEcommerceService("payment-gateway", "v3.2", region, "metro", 3000, 200),
            "upi": IndianEcommerceService("upi-processor", "v2.5", region, "metro", 10000, 80),
            "notification": IndianEcommerceService("sms-whatsapp-service", "v1.9", region, "metro", 15000, 30),
            "logistics": IndianEcommerceService("ekart-delivery", "v2.7", region, "metro", 2000, 500)
        }
        
        # Logger setup for Indian compliance
        self.logger = structlog.get_logger("flipkart-tracer")
        
    def _setup_tracing(self):
        """OpenTelemetry tracing setup for Indian infrastructure"""
        
        # Service resource identification
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": "2.1.0",
            "deployment.environment": "production",
            "region": self.region,
            "country": "India",
            "compliance.rbi": "enabled",  # RBI compliance tracking
            "compliance.dpdp": "enabled"   # DPDP Act compliance
        })
        
        # Jaeger exporter for distributed tracing
        jaeger_exporter = JaegerExporter(
            agent_host_name="jaeger-agent.monitoring.svc.cluster.local",
            agent_port=6831,
            collector_endpoint="http://jaeger-collector.monitoring:14268/api/traces"
        )
        
        # Set tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))
        
        # Add span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
    def generate_indian_trace_context(self, user_id: str, session_id: str) -> Dict[str, str]:
        """
        भारतीय user के लिए trace context generate करना
        
        Args:
            user_id: Flipkart user ID (phone number based)
            session_id: Session identifier
            
        Returns:
            Trace context with Indian metadata
        """
        
        # Indian-specific trace context
        trace_context = {
            "trace_id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "country_code": "IN",
            "currency": "INR",
            "preferred_language": random.choice(["hindi", "english", "tamil", "bengali"]),
            "user_tier": random.choice(["plus", "premium", "regular"]),
            "region": self.region,
            "device_type": random.choice(["android", "ios", "web", "mweb"]),
            "payment_preference": random.choice(["upi", "cards", "cod", "wallet"]),
            "created_at": datetime.now().isoformat()
        }
        
        # Cache for correlation
        self.correlation_cache[user_id] = trace_context
        
        return trace_context
        
    async def trace_flipkart_checkout_flow(self, user_id: str, product_ids: List[str], 
                                          payment_method: str = "upi") -> Dict[str, Any]:
        """
        Complete Flipkart checkout flow tracing
        
        Real scenario: User "9876543210" buying iPhone 15 + AirPods during BBD
        Total order value: ₹1,25,000
        Expected services: 8+ microservices involved
        """
        
        session_id = f"session_{int(time.time())}"
        trace_context = self.generate_indian_trace_context(user_id, session_id)
        
        with self.tracer.start_as_current_span("flipkart_checkout_flow") as parent_span:
            
            # Set span attributes for Indian context
            parent_span.set_attributes({
                "user.id": user_id,
                "user.country": "IN",
                "user.region": self.region,
                "order.value.currency": "INR",
                "checkout.flow": "express",
                "event.name": "big_billion_days_2024"
            })
            
            checkout_result = {}
            
            try:
                # Step 1: Cart validation और inventory check
                cart_result = await self._trace_cart_validation(
                    trace_context, product_ids, parent_span
                )
                checkout_result["cart_validation"] = cart_result
                
                # Step 2: Address validation (Indian pincode system)
                address_result = await self._trace_address_validation(
                    trace_context, parent_span
                )
                checkout_result["address_validation"] = address_result
                
                # Step 3: Payment processing (UPI/Cards/Wallet)
                payment_result = await self._trace_payment_processing(
                    trace_context, payment_method, parent_span
                )
                checkout_result["payment_processing"] = payment_result
                
                # Step 4: Order creation और confirmation
                order_result = await self._trace_order_creation(
                    trace_context, parent_span
                )
                checkout_result["order_creation"] = order_result
                
                # Step 5: Notification dispatch (SMS/WhatsApp/Push)
                notification_result = await self._trace_notification_dispatch(
                    trace_context, parent_span
                )
                checkout_result["notifications"] = notification_result
                
                # Step 6: Logistics assignment (Ekart/3PL)
                logistics_result = await self._trace_logistics_assignment(
                    trace_context, parent_span
                )
                checkout_result["logistics"] = logistics_result
                
                # Success metrics
                parent_span.set_status(trace.Status(trace.StatusCode.OK))
                parent_span.set_attribute("checkout.success", True)
                
                # Log successful checkout for business metrics
                self.logger.info(
                    "flipkart_checkout_success",
                    user_id=user_id,
                    trace_id=trace_context["trace_id"],
                    region=self.region,
                    payment_method=payment_method,
                    total_latency_ms=int(time.time() * 1000) - int(parent_span.start_time / 1000000)
                )
                
            except Exception as e:
                # Error handling with detailed context
                parent_span.record_exception(e)
                parent_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                
                checkout_result["error"] = {
                    "message": str(e),
                    "step": "checkout_flow",
                    "trace_id": trace_context["trace_id"]
                }
                
                self.logger.error(
                    "flipkart_checkout_failed",
                    user_id=user_id,
                    error=str(e),
                    trace_id=trace_context["trace_id"]
                )
                
            return checkout_result
            
    async def _trace_cart_validation(self, context: Dict, product_ids: List[str], 
                                    parent_span) -> Dict[str, Any]:
        """Cart validation with inventory check across Indian warehouses"""
        
        with self.tracer.start_as_current_span("cart_validation", parent=parent_span) as span:
            
            span.set_attributes({
                "service.name": "cart-service",
                "product.count": len(product_ids),
                "warehouse.region": self.region
            })
            
            # Simulate Indian warehouse inventory check
            # Real scenario: Check across Mumbai, Bangalore, Delhi warehouses
            warehouses = ["mumbai_wh_1", "bangalore_wh_2", "delhi_wh_1"]
            inventory_results = {}
            
            for warehouse in warehouses:
                # Simulate warehouse latency (higher for tier-3 cities)
                if "mumbai" in warehouse:
                    await asyncio.sleep(0.05)  # 50ms for metro
                else:
                    await asyncio.sleep(0.1)   # 100ms for other cities
                    
                inventory_results[warehouse] = {
                    "available": random.choice([True, False]),
                    "quantity": random.randint(1, 100),
                    "price_inr": random.randint(1000, 50000),
                    "delivery_estimate": random.choice(["same_day", "next_day", "2_days"])
                }
            
            # Cart validation result
            cart_result = {
                "status": "validated",
                "total_items": len(product_ids),
                "inventory_check": inventory_results,
                "estimated_total_inr": sum([inv["price_inr"] for inv in inventory_results.values()]),
                "delivery_feasible": True
            }
            
            span.set_attribute("cart.total_value_inr", cart_result["estimated_total_inr"])
            span.set_status(trace.Status(trace.StatusCode.OK))
            
            return cart_result
            
    async def _trace_address_validation(self, context: Dict, parent_span) -> Dict[str, Any]:
        """Indian address validation with pincode और delivery feasibility"""
        
        with self.tracer.start_as_current_span("address_validation", parent=parent_span) as span:
            
            # Indian address components
            indian_pincodes = ["400001", "560001", "110001", "600001", "500001"]
            pincode = random.choice(indian_pincodes)
            
            span.set_attributes({
                "service.name": "address-service",
                "address.pincode": pincode,
                "address.country": "IN",
                "delivery.serviceable": True
            })
            
            # Simulate address validation latency
            await asyncio.sleep(0.03)
            
            # Address validation result
            address_result = {
                "pincode": pincode,
                "city": random.choice(["Mumbai", "Bangalore", "Delhi", "Chennai"]),
                "state": random.choice(["Maharashtra", "Karnataka", "Delhi", "Tamil Nadu"]),
                "delivery_serviceable": True,
                "cod_available": random.choice([True, False]),
                "estimated_delivery_days": random.randint(1, 5)
            }
            
            span.set_status(trace.Status(trace.StatusCode.OK))
            return address_result
            
    async def _trace_payment_processing(self, context: Dict, payment_method: str, 
                                       parent_span) -> Dict[str, Any]:
        """
        Indian payment processing tracing
        
        Supports: UPI, Cards, Wallets, COD
        Integration: Paytm, PhonePe, Razorpay, CCAvenue
        """
        
        with self.tracer.start_as_current_span("payment_processing", parent=parent_span) as span:
            
            span.set_attributes({
                "service.name": "payment-gateway",
                "payment.method": payment_method,
                "payment.currency": "INR",
                "payment.country": "IN"
            })
            
            # Payment method specific processing
            if payment_method == "upi":
                payment_result = await self._process_upi_payment(context, span)
            elif payment_method == "cards":
                payment_result = await self._process_card_payment(context, span)
            elif payment_method == "wallet":
                payment_result = await self._process_wallet_payment(context, span)
            else:  # COD
                payment_result = await self._process_cod_payment(context, span)
            
            span.set_attribute("payment.success", payment_result["success"])
            span.set_attribute("payment.transaction_id", payment_result["transaction_id"])
            
            if payment_result["success"]:
                span.set_status(trace.Status(trace.StatusCode.OK))
            else:
                span.set_status(trace.Status(trace.StatusCode.ERROR, payment_result["error"]))
            
            return payment_result
            
    async def _process_upi_payment(self, context: Dict, parent_span) -> Dict[str, Any]:
        """UPI payment processing with bank integration"""
        
        with self.tracer.start_as_current_span("upi_payment", parent=parent_span) as span:
            
            # Indian UPI banks
            upi_banks = ["SBI", "HDFC", "ICICI", "Axis", "Kotak"]
            selected_bank = random.choice(upi_banks)
            
            span.set_attributes({
                "upi.bank": selected_bank,
                "upi.app": random.choice(["PhonePe", "Paytm", "GPay", "BHIM"]),
                "upi.vpa": f"user@{selected_bank.lower()}"
            })
            
            # Simulate UPI processing time (typically 2-5 seconds)
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # UPI success rate (Indian average ~95%)
            success = random.random() > 0.05
            
            if success:
                return {
                    "success": True,
                    "transaction_id": f"UPI{int(time.time())}{random.randint(1000, 9999)}",
                    "bank": selected_bank,
                    "processing_time_ms": random.randint(100, 300),
                    "fees_inr": 0  # UPI is free for consumers
                }
            else:
                return {
                    "success": False,
                    "error": random.choice([
                        "Insufficient balance",
                        "Bank server timeout", 
                        "Invalid UPI PIN",
                        "Transaction limit exceeded"
                    ]),
                    "bank": selected_bank
                }
                
    async def _process_card_payment(self, context: Dict, parent_span) -> Dict[str, Any]:
        """Credit/Debit card payment processing"""
        
        with self.tracer.start_as_current_span("card_payment", parent=parent_span) as span:
            
            card_types = ["VISA", "MasterCard", "RuPay", "Amex"]
            card_type = random.choice(card_types)
            
            span.set_attributes({
                "card.type": card_type,
                "card.country": "IN",
                "gateway": "Razorpay"
            })
            
            # Card processing time
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Card success rate (typically ~90%)
            success = random.random() > 0.1
            
            if success:
                return {
                    "success": True,
                    "transaction_id": f"CARD{int(time.time())}{random.randint(1000, 9999)}",
                    "card_type": card_type,
                    "processing_time_ms": random.randint(200, 500),
                    "fees_inr": random.randint(10, 50)  # Card processing fees
                }
            else:
                return {
                    "success": False,
                    "error": random.choice([
                        "Card declined",
                        "Insufficient funds",
                        "Invalid CVV",
                        "Card expired",
                        "Bank server error"
                    ]),
                    "card_type": card_type
                }
                
    async def _process_wallet_payment(self, context: Dict, parent_span) -> Dict[str, Any]:
        """Wallet payment processing (Paytm, PhonePe, etc.)"""
        
        with self.tracer.start_as_current_span("wallet_payment", parent=parent_span) as span:
            
            wallets = ["Paytm", "PhonePe", "Amazon Pay", "Mobikwik", "Freecharge"]
            wallet = random.choice(wallets)
            
            span.set_attributes({
                "wallet.provider": wallet,
                "wallet.country": "IN"
            })
            
            await asyncio.sleep(random.uniform(0.05, 0.15))
            
            success = random.random() > 0.02  # Wallets have high success rate
            
            if success:
                return {
                    "success": True,
                    "transaction_id": f"WALLET{int(time.time())}{random.randint(1000, 9999)}",
                    "wallet": wallet,
                    "processing_time_ms": random.randint(50, 150),
                    "fees_inr": 0,  # Usually no fees
                    "cashback_earned": random.randint(0, 100)
                }
            else:
                return {
                    "success": False,
                    "error": "Insufficient wallet balance",
                    "wallet": wallet
                }
                
    async def _process_cod_payment(self, context: Dict, parent_span) -> Dict[str, Any]:
        """Cash on Delivery processing"""
        
        with self.tracer.start_as_current_span("cod_payment", parent=parent_span) as span:
            
            span.set_attributes({
                "payment.type": "cash_on_delivery",
                "cod.charges_inr": 49
            })
            
            # COD is always successful at this stage
            await asyncio.sleep(0.01)
            
            return {
                "success": True,
                "transaction_id": f"COD{int(time.time())}{random.randint(1000, 9999)}",
                "payment_type": "cod",
                "cod_charges": 49,
                "processing_time_ms": 10
            }
            
    async def _trace_order_creation(self, context: Dict, parent_span) -> Dict[str, Any]:
        """Order creation और confirmation"""
        
        with self.tracer.start_as_current_span("order_creation", parent=parent_span) as span:
            
            order_id = f"FLIP{int(time.time())}{random.randint(100000, 999999)}"
            
            span.set_attributes({
                "service.name": "order-service",
                "order.id": order_id,
                "order.country": "IN"
            })
            
            await asyncio.sleep(0.02)
            
            order_result = {
                "order_id": order_id,
                "status": "confirmed",
                "estimated_delivery": "2024-11-15",
                "tracking_enabled": True,
                "cancellation_allowed": True
            }
            
            span.set_status(trace.Status(trace.StatusCode.OK))
            return order_result
            
    async def _trace_notification_dispatch(self, context: Dict, parent_span) -> Dict[str, Any]:
        """Multi-channel notification dispatch"""
        
        with self.tracer.start_as_current_span("notification_dispatch", parent=parent_span) as span:
            
            span.set_attributes({
                "service.name": "notification-service",
                "channels": "sms,whatsapp,push,email"
            })
            
            # Indian mobile number format
            mobile = f"+91{context['user_id']}"
            
            notifications = {}
            
            # SMS notification
            notifications["sms"] = {
                "status": "sent",
                "provider": "TextLocal",
                "mobile": mobile,
                "delivery_time_ms": random.randint(1000, 5000)
            }
            
            # WhatsApp notification (increasingly popular in India)
            notifications["whatsapp"] = {
                "status": "sent",
                "provider": "Gupshup",
                "mobile": mobile,
                "delivery_time_ms": random.randint(2000, 8000)
            }
            
            # Push notification
            notifications["push"] = {
                "status": "sent",
                "platform": context.get("device_type", "android"),
                "delivery_time_ms": random.randint(500, 2000)
            }
            
            await asyncio.sleep(0.01)
            
            span.set_status(trace.Status(trace.StatusCode.OK))
            return notifications
            
    async def _trace_logistics_assignment(self, context: Dict, parent_span) -> Dict[str, Any]:
        """Logistics partner assignment"""
        
        with self.tracer.start_as_current_span("logistics_assignment", parent=parent_span) as span:
            
            # Indian logistics partners
            logistics_partners = ["Ekart", "Delhivery", "BlueDart", "DTDC", "Aramex"]
            assigned_partner = random.choice(logistics_partners)
            
            span.set_attributes({
                "service.name": "logistics-service",
                "partner": assigned_partner,
                "delivery.type": "standard"
            })
            
            await asyncio.sleep(0.05)
            
            logistics_result = {
                "partner": assigned_partner,
                "tracking_id": f"SHIP{int(time.time())}{random.randint(1000, 9999)}",
                "estimated_pickup": "2024-11-12",
                "estimated_delivery": "2024-11-15",
                "delivery_slots": ["morning", "afternoon", "evening"]
            }
            
            span.set_status(trace.Status(trace.StatusCode.OK))
            return logistics_result
            
    def get_correlation_metrics(self) -> Dict[str, Any]:
        """Get trace correlation metrics for monitoring"""
        
        total_traces = len(self.correlation_cache)
        
        return {
            "total_active_traces": total_traces,
            "region": self.region,
            "service_health": {
                service_name: {
                    "capacity": service.capacity,
                    "latency_sla": service.latency_sla,
                    "status": "healthy"
                }
                for service_name, service in self.indian_services.items()
            },
            "correlation_cache_size": len(self.correlation_cache),
            "memory_usage_mb": total_traces * 0.1,  # Rough estimate
            "generated_at": datetime.now().isoformat()
        }

# Test functions for validation
async def test_flipkart_bbd_scenario():
    """
    Test BBD scenario with high load
    
    Scenario: Big Billion Days के दौरान typical user journey
    """
    print("🛒 Testing Flipkart BBD distributed tracing...")
    
    correlator = FlipkartTraceCorrelator("flipkart-checkout", "mumbai")
    
    # Multiple concurrent checkouts (BBD load simulation)
    tasks = []
    
    for i in range(5):  # Simulate 5 concurrent users
        user_id = f"98765432{10 + i}"
        product_ids = [f"prod_{j}" for j in range(1, 4)]  # 3 products each
        payment_method = random.choice(["upi", "cards", "wallet", "cod"])
        
        task = correlator.trace_flipkart_checkout_flow(
            user_id, product_ids, payment_method
        )
        tasks.append(task)
    
    # Execute all checkouts concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Print results
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ User {i+1} checkout failed: {result}")
        else:
            print(f"✅ User {i+1} checkout completed successfully")
            
    # Print correlation metrics
    metrics = correlator.get_correlation_metrics()
    print(f"\n📊 Correlation Metrics:")
    print(f"Active traces: {metrics['total_active_traces']}")
    print(f"Memory usage: {metrics['memory_usage_mb']} MB")
    
    return results

async def test_payment_method_correlation():
    """Test different payment methods correlation"""
    print("\n💳 Testing payment method correlation...")
    
    correlator = FlipkartTraceCorrelator("payment-service", "bangalore")
    
    payment_methods = ["upi", "cards", "wallet", "cod"]
    
    for method in payment_methods:
        print(f"\n🔄 Testing {method.upper()} payment...")
        
        result = await correlator.trace_flipkart_checkout_flow(
            "9876543210", ["iphone15", "airpods"], method
        )
        
        if "error" in result:
            print(f"❌ {method} failed: {result['error']['message']}")
        else:
            payment_success = result.get("payment_processing", {}).get("success", False)
            print(f"{'✅' if payment_success else '❌'} {method} payment: {payment_success}")

if __name__ == "__main__":
    print("🚀 Episode 16: Distributed Trace Correlation System")
    print("🇮🇳 Mumbai se Bangalore tak sabka trace correlation!")
    print("=" * 60)
    
    # Run test scenarios
    asyncio.run(test_flipkart_bbd_scenario())
    asyncio.run(test_payment_method_correlation())
    
    print("\n" + "=" * 60)
    print("✅ Distributed trace correlation testing completed!")
    print("📊 Jaeger UI: http://localhost:16686")
    print("🔍 Next: Check correlation graphs in monitoring dashboard")
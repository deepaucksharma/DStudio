#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 3: OpenTelemetry Distributed Tracing for Flipkart Checkout

Flipkart Big Billion Days scale पर complete checkout flow tracing
Production-ready distributed tracing with OpenTelemetry

Author: Hindi Tech Podcast
Context: E-commerce checkout flow monitoring at Indian scale
"""

import time
import random
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

# OpenTelemetry imports
from opentelemetry import trace, baggage, context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor

import structlog

logger = structlog.get_logger()

class CheckoutStage(Enum):
    """Flipkart checkout के different stages"""
    CART_VALIDATION = "cart_validation"
    INVENTORY_CHECK = "inventory_check"
    PRICING_CALCULATION = "pricing_calculation"
    DISCOUNT_APPLICATION = "discount_application"
    GST_CALCULATION = "gst_calculation"
    SHIPPING_CALCULATION = "shipping_calculation"
    PAYMENT_PROCESSING = "payment_processing"
    ORDER_CREATION = "order_creation"
    INVENTORY_ALLOCATION = "inventory_allocation"
    NOTIFICATION_SENDING = "notification_sending"

class PaymentMethod(Enum):
    """Indian payment methods"""
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    NET_BANKING = "net_banking"
    DIGITAL_WALLET = "digital_wallet"
    COD = "cash_on_delivery"
    EMI = "emi"
    GIFT_CARD = "gift_card"

@dataclass
class FlipkartUser:
    """Flipkart user का data structure"""
    user_id: str
    email: str
    phone: str
    city: str
    state: str
    pincode: str
    tier: str  # metro, tier1, tier2, tier3
    plus_member: bool = False
    segment: str = "regular"  # vip, regular, new

@dataclass
class Product:
    """Product information for checkout"""
    product_id: str
    name: str
    price: float
    quantity: int
    seller_id: str
    warehouse_location: str
    category: str
    weight_kg: float = 1.0

@dataclass
class CheckoutContext:
    """Complete checkout context with tracing information"""
    checkout_id: str
    user: FlipkartUser
    products: List[Product]
    payment_method: PaymentMethod
    is_bbd: bool = False  # Big Billion Days flag
    discount_code: Optional[str] = None
    shipping_address: Dict[str, str] = None
    billing_address: Dict[str, str] = None
    
class FlipkartTracingService:
    """
    Flipkart checkout के लिए comprehensive tracing service
    OpenTelemetry के साथ production-ready implementation
    """
    
    def __init__(self, service_name: str = "flipkart-checkout", 
                 jaeger_endpoint: str = "http://localhost:14268/api/traces"):
        """
        Tracing service initialize करता है
        """
        self.service_name = service_name
        
        # Resource configuration with Indian context
        resource = Resource.create({
            "service.name": service_name,
            "service.version": "1.0.0",
            "service.instance.id": f"{service_name}-{uuid.uuid4().hex[:8]}",
            "deployment.environment": "production",
            "region": "ap-south-1",  # Mumbai region
            "country": "IN",
            "data_center": "mumbai-dc1"
        })
        
        # Setup tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))
        
        # Setup Jaeger exporter
        jaeger_exporter = JaegerExporter(
            endpoint=jaeger_endpoint,
            max_tag_value_length=1024,
            username=None,
            password=None,
        )
        
        # Add span processors
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Console exporter for development
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        trace.get_tracer_provider().add_span_processor(console_processor)
        
        # Get tracer
        self.tracer = trace.get_tracer(__name__)
        
        # Instrument common libraries
        RequestsInstrumentor().instrument()
        AsyncioInstrumentor().instrument()
        
        logger.info("Flipkart tracing service initialized", 
                   service=service_name, jaeger_endpoint=jaeger_endpoint)

    async def trace_complete_checkout(self, checkout_context: CheckoutContext) -> Dict[str, Any]:
        """
        Complete checkout flow को trace करता है
        Root span से लेकर all sub-operations तक
        """
        trace_id = trace.get_current_span().get_span_context().trace_id
        
        with self.tracer.start_as_current_span(
            "flipkart_checkout_flow",
            attributes={
                "checkout.id": checkout_context.checkout_id,
                "user.id": checkout_context.user.user_id,
                "user.city": checkout_context.user.city,
                "user.tier": checkout_context.user.tier,
                "user.plus_member": checkout_context.user.plus_member,
                "payment.method": checkout_context.payment_method.value,
                "products.count": len(checkout_context.products),
                "is_bbd": checkout_context.is_bbd,
                "business.event": "big_billion_days" if checkout_context.is_bbd else "regular_sale",
                "trace.id": f"{trace_id:032x}"
            }
        ) as root_span:
            
            try:
                checkout_result = {"success": False, "order_id": None, "errors": []}\n                
                # Stage 1: Cart Validation
                cart_valid = await self._trace_cart_validation(checkout_context)
                if not cart_valid:
                    checkout_result["errors"].append("Cart validation failed")
                    root_span.set_status(trace.Status(trace.StatusCode.ERROR, "Cart validation failed"))
                    return checkout_result
                
                # Stage 2: Inventory Check
                inventory_available = await self._trace_inventory_check(checkout_context)
                if not inventory_available:
                    checkout_result["errors"].append("Inventory not available")
                    root_span.set_status(trace.Status(trace.StatusCode.ERROR, "Inventory unavailable"))
                    return checkout_result
                
                # Stage 3: Pricing Calculation
                pricing_result = await self._trace_pricing_calculation(checkout_context)
                
                # Stage 4: Payment Processing
                payment_result = await self._trace_payment_processing(checkout_context, pricing_result)
                if not payment_result["success"]:
                    checkout_result["errors"].append(f"Payment failed: {payment_result['error']}")
                    root_span.set_status(trace.Status(trace.StatusCode.ERROR, "Payment processing failed"))
                    return checkout_result
                
                # Stage 5: Order Creation
                order_result = await self._trace_order_creation(checkout_context, pricing_result)
                
                # Stage 6: Final notifications
                await self._trace_notification_sending(checkout_context, order_result)
                
                checkout_result.update({
                    "success": True,
                    "order_id": order_result["order_id"],
                    "total_amount": pricing_result["total_amount"],
                    "estimated_delivery": order_result["estimated_delivery"]
                })
                
                # Add success attributes
                root_span.set_attributes({
                    "checkout.success": True,
                    "order.id": order_result["order_id"],
                    "order.value": pricing_result["total_amount"],
                    "order.currency": "INR"
                })
                
                logger.info("Checkout completed successfully", 
                           checkout_id=checkout_context.checkout_id,
                           order_id=order_result["order_id"],
                           trace_id=f"{trace_id:032x}")
                
                return checkout_result
                
            except Exception as e:
                root_span.record_exception(e)
                root_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                checkout_result["errors"].append(f"Checkout failed: {str(e)}")
                
                logger.error("Checkout failed", 
                           checkout_id=checkout_context.checkout_id,
                           error=str(e),
                           trace_id=f"{trace_id:032x}")
                
                return checkout_result

    async def _trace_cart_validation(self, context: CheckoutContext) -> bool:
        """
        Cart validation को trace करता है
        Product availability, pricing, inventory checks
        """
        with self.tracer.start_as_current_span(
            "cart_validation",
            attributes={
                "stage": CheckoutStage.CART_VALIDATION.value,
                "products.count": len(context.products),
                "validation.type": "comprehensive"
            }
        ) as span:
            
            # Simulate validation latency
            validation_time = random.uniform(0.1, 0.5)  # 100-500ms
            await asyncio.sleep(validation_time)
            
            # Product validation
            for i, product in enumerate(context.products):
                with self.tracer.start_as_current_span(
                    f"validate_product_{i+1}",
                    attributes={
                        "product.id": product.product_id,
                        "product.name": product.name,
                        "product.price": product.price,
                        "product.quantity": product.quantity,
                        "product.seller": product.seller_id,
                        "product.warehouse": product.warehouse_location
                    }
                ):
                    # Simulate product validation
                    await asyncio.sleep(0.05)
            
            # Validation result (95% success rate normally, 85% during BBD)
            success_rate = 0.85 if context.is_bbd else 0.95
            is_valid = random.random() < success_rate
            
            span.set_attributes({
                "validation.success": is_valid,
                "validation.duration_ms": validation_time * 1000
            })
            
            if not is_valid:
                span.set_status(trace.Status(trace.StatusCode.ERROR, "Cart validation failed"))
            
            return is_valid

    async def _trace_inventory_check(self, context: CheckoutContext) -> bool:
        """
        Inventory availability check को trace करता है
        Multi-warehouse inventory lookup
        """
        with self.tracer.start_as_current_span(
            "inventory_check",
            attributes={
                "stage": CheckoutStage.INVENTORY_CHECK.value,
                "warehouses.count": len(set(p.warehouse_location for p in context.products))
            }
        ) as span:
            
            inventory_available = True
            total_check_time = 0
            
            # Check inventory for each product
            for product in context.products:
                with self.tracer.start_as_current_span(
                    "warehouse_inventory_lookup",
                    attributes={
                        "warehouse.location": product.warehouse_location,
                        "product.id": product.product_id,
                        "requested.quantity": product.quantity
                    }
                ) as warehouse_span:
                    
                    # Simulate warehouse API call
                    check_time = random.uniform(0.05, 0.2)
                    await asyncio.sleep(check_time)
                    total_check_time += check_time
                    
                    # Inventory availability (90% during BBD, 98% normally)
                    availability = 0.90 if context.is_bbd else 0.98
                    is_available = random.random() < availability
                    available_quantity = product.quantity if is_available else random.randint(0, product.quantity-1)
                    
                    warehouse_span.set_attributes({
                        "inventory.available": is_available,
                        "inventory.quantity_available": available_quantity,
                        "inventory.check_duration_ms": check_time * 1000
                    })
                    
                    if not is_available:
                        inventory_available = False
                        warehouse_span.set_status(trace.Status(trace.StatusCode.ERROR, "Insufficient inventory"))
            
            span.set_attributes({
                "inventory.all_available": inventory_available,
                "inventory.total_check_duration_ms": total_check_time * 1000
            })
            
            return inventory_available

    async def _trace_pricing_calculation(self, context: CheckoutContext) -> Dict[str, Any]:
        """
        Pricing calculation को trace करता है
        Discounts, GST, shipping charges के साथ
        """
        with self.tracer.start_as_current_span(
            "pricing_calculation",
            attributes={
                "stage": CheckoutStage.PRICING_CALCULATION.value,
                "user.plus_member": context.user.plus_member,
                "discount_code": context.discount_code or "none"
            }
        ) as span:
            
            subtotal = sum(p.price * p.quantity for p in context.products)
            
            # Discount calculation
            discount_amount = 0
            with self.tracer.start_as_current_span(
                "discount_calculation",
                attributes={"subtotal": subtotal}
            ) as discount_span:
                
                await asyncio.sleep(0.1)  # Discount service call
                
                if context.discount_code:
                    discount_amount = subtotal * 0.15  # 15% discount
                elif context.user.plus_member:
                    discount_amount = subtotal * 0.05  # 5% Plus member discount
                elif context.is_bbd:
                    discount_amount = subtotal * 0.20  # 20% BBD discount
                
                discount_span.set_attributes({
                    "discount.amount": discount_amount,
                    "discount.percentage": (discount_amount / subtotal * 100) if subtotal > 0 else 0
                })
            
            # GST calculation (Indian tax system)
            gst_amount = 0
            with self.tracer.start_as_current_span(
                "gst_calculation",
                attributes={
                    "user.state": context.user.state,
                    "billing.state": context.billing_address.get("state", context.user.state) if context.billing_address else context.user.state
                }
            ) as gst_span:
                
                await asyncio.sleep(0.05)  # GST service call
                
                # Simplified GST calculation
                taxable_amount = subtotal - discount_amount
                
                for product in context.products:
                    if product.category in ["electronics", "appliances"]:
                        gst_rate = 0.18  # 18% GST
                    elif product.category in ["clothing", "footwear"]:
                        gst_rate = 0.12  # 12% GST
                    else:
                        gst_rate = 0.05  # 5% GST
                    
                    product_gst = (product.price * product.quantity) * gst_rate
                    gst_amount += product_gst
                
                gst_span.set_attributes({
                    "gst.amount": gst_amount,
                    "gst.applicable_amount": taxable_amount
                })
            
            # Shipping calculation
            shipping_amount = 0
            with self.tracer.start_as_current_span(
                "shipping_calculation",
                attributes={
                    "user.city": context.user.city,
                    "user.tier": context.user.tier,
                    "total_weight": sum(p.weight_kg * p.quantity for p in context.products)
                }
            ) as shipping_span:
                
                await asyncio.sleep(0.05)
                
                total_weight = sum(p.weight_kg * p.quantity for p in context.products)
                
                if context.user.plus_member:
                    shipping_amount = 0  # Free shipping for Plus members
                elif context.user.tier == "metro":
                    shipping_amount = 40 if total_weight > 0.5 else 0
                elif context.user.tier == "tier1":
                    shipping_amount = 60
                else:
                    shipping_amount = 80
                
                shipping_span.set_attributes({
                    "shipping.amount": shipping_amount,
                    "shipping.weight_kg": total_weight,
                    "shipping.free": shipping_amount == 0
                })
            
            total_amount = subtotal - discount_amount + gst_amount + shipping_amount
            
            pricing_result = {
                "subtotal": subtotal,
                "discount_amount": discount_amount,
                "gst_amount": gst_amount,
                "shipping_amount": shipping_amount,
                "total_amount": total_amount
            }
            
            span.set_attributes({
                "pricing.subtotal": subtotal,
                "pricing.discount": discount_amount,
                "pricing.gst": gst_amount,
                "pricing.shipping": shipping_amount,
                "pricing.total": total_amount,
                "pricing.currency": "INR"
            })
            
            return pricing_result

    async def _trace_payment_processing(self, context: CheckoutContext, 
                                      pricing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Payment processing को trace करता है
        Multiple payment gateways के साथ
        """
        with self.tracer.start_as_current_span(
            "payment_processing",
            attributes={
                "stage": CheckoutStage.PAYMENT_PROCESSING.value,
                "payment.method": context.payment_method.value,
                "payment.amount": pricing["total_amount"],
                "payment.currency": "INR"
            }
        ) as span:
            
            # Payment gateway selection
            gateway = self._select_payment_gateway(context.payment_method, context.user.city)
            
            with self.tracer.start_as_current_span(
                "payment_gateway_call",
                attributes={
                    "gateway.name": gateway,
                    "gateway.method": context.payment_method.value
                }
            ) as gateway_span:
                
                # Simulate payment processing time
                if context.payment_method == PaymentMethod.UPI:
                    processing_time = random.uniform(2, 8)  # 2-8 seconds for UPI
                elif context.payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
                    processing_time = random.uniform(3, 12)  # 3-12 seconds for cards
                elif context.payment_method == PaymentMethod.NET_BANKING:
                    processing_time = random.uniform(10, 30)  # 10-30 seconds for net banking
                else:
                    processing_time = random.uniform(1, 5)  # 1-5 seconds for others
                
                await asyncio.sleep(processing_time)
                
                # Payment success rate (varies by method)
                success_rates = {
                    PaymentMethod.UPI: 0.96,
                    PaymentMethod.CREDIT_CARD: 0.88,
                    PaymentMethod.DEBIT_CARD: 0.85,
                    PaymentMethod.NET_BANKING: 0.82,
                    PaymentMethod.DIGITAL_WALLET: 0.94,
                    PaymentMethod.COD: 0.99,
                    PaymentMethod.EMI: 0.78
                }
                
                success_rate = success_rates.get(context.payment_method, 0.90)
                if context.is_bbd:
                    success_rate -= 0.05  # Lower success rate during peak load
                
                is_successful = random.random() < success_rate
                
                payment_result = {
                    "success": is_successful,
                    "transaction_id": f"TXN{uuid.uuid4().hex[:12].upper()}",
                    "gateway": gateway,
                    "processing_time": processing_time
                }
                
                if not is_successful:
                    error_codes = ["BANK_TIMEOUT", "INSUFFICIENT_FUNDS", "CARD_DECLINED", "TECHNICAL_ERROR"]
                    payment_result["error"] = random.choice(error_codes)
                    gateway_span.set_status(trace.Status(trace.StatusCode.ERROR, payment_result["error"]))
                
                gateway_span.set_attributes({
                    "payment.success": is_successful,
                    "payment.transaction_id": payment_result["transaction_id"],
                    "payment.processing_time_ms": processing_time * 1000
                })
                
                if not is_successful:
                    gateway_span.set_attribute("payment.error_code", payment_result["error"])
            
            span.set_attributes({
                "payment.gateway": gateway,
                "payment.success": payment_result["success"],
                "payment.transaction_id": payment_result["transaction_id"]
            })
            
            return payment_result

    async def _trace_order_creation(self, context: CheckoutContext, 
                                  pricing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Order creation को trace करता है
        Database operations के साथ
        """
        with self.tracer.start_as_current_span(
            "order_creation",
            attributes={
                "stage": CheckoutStage.ORDER_CREATION.value,
                "user.id": context.user.user_id
            }
        ) as span:
            
            order_id = f"OD{int(time.time())}{random.randint(100000, 999999)}"
            
            # Database operations
            with self.tracer.start_as_current_span(
                "database_order_insert",
                attributes={
                    "db.operation": "INSERT",
                    "db.table": "orders",
                    "order.id": order_id
                }
            ):
                await asyncio.sleep(0.1)  # Database insert
            
            # Inventory allocation
            with self.tracer.start_as_current_span(
                "inventory_allocation",
                attributes={
                    "stage": CheckoutStage.INVENTORY_ALLOCATION.value,
                    "products.count": len(context.products)
                }
            ):
                await asyncio.sleep(0.15)  # Inventory allocation
            
            # Estimated delivery calculation
            delivery_days = 1 if context.user.tier == "metro" else 3
            estimated_delivery = (datetime.now() + timedelta(days=delivery_days)).strftime("%Y-%m-%d")
            
            order_result = {
                "order_id": order_id,
                "estimated_delivery": estimated_delivery,
                "status": "confirmed"
            }
            
            span.set_attributes({
                "order.id": order_id,
                "order.status": "confirmed",
                "order.estimated_delivery": estimated_delivery,
                "order.value": pricing["total_amount"]
            })
            
            return order_result

    async def _trace_notification_sending(self, context: CheckoutContext, 
                                        order_result: Dict[str, Any]):
        """
        Notifications को trace करता है
        SMS, Email, Push notifications
        """
        with self.tracer.start_as_current_span(
            "notification_sending",
            attributes={
                "stage": CheckoutStage.NOTIFICATION_SENDING.value,
                "user.phone": context.user.phone,
                "user.email": context.user.email
            }
        ) as span:
            
            notifications = []
            
            # SMS notification
            with self.tracer.start_as_current_span(
                "sms_notification",
                attributes={
                    "notification.type": "sms",
                    "notification.recipient": context.user.phone
                }
            ):
                await asyncio.sleep(0.05)
                notifications.append("sms_sent")
            
            # Email notification
            with self.tracer.start_as_current_span(
                "email_notification",
                attributes={
                    "notification.type": "email",
                    "notification.recipient": context.user.email
                }
            ):
                await asyncio.sleep(0.1)
                notifications.append("email_sent")
            
            # Push notification (if mobile app)
            with self.tracer.start_as_current_span(
                "push_notification",
                attributes={
                    "notification.type": "push",
                    "notification.platform": "android"
                }
            ):
                await asyncio.sleep(0.02)
                notifications.append("push_sent")
            
            span.set_attributes({
                "notifications.sent": notifications,
                "notifications.count": len(notifications)
            })

    def _select_payment_gateway(self, payment_method: PaymentMethod, city: str) -> str:
        """
        Payment method और location के base पर gateway select करता है
        """
        if payment_method == PaymentMethod.UPI:
            return random.choice(["razorpay_upi", "payu_upi", "cashfree_upi"])
        elif payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
            return random.choice(["razorpay_cards", "payu_cards", "ccavenue_cards"])
        elif payment_method == PaymentMethod.NET_BANKING:
            return random.choice(["billdesk", "atom", "citrus"])
        else:
            return "razorpay_default"

def create_sample_checkout_context() -> CheckoutContext:
    """
    Sample checkout context create करता है testing के लिए
    """
    # Sample user
    user = FlipkartUser(
        user_id=f"U{random.randint(100000, 999999)}",
        email="user@example.com",
        phone=f"+91{random.randint(7000000000, 9999999999)}",
        city=random.choice(["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]),
        state=random.choice(["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "West Bengal"]),
        pincode=f"{random.randint(100000, 999999)}",
        tier=random.choice(["metro", "tier1", "tier2"]),
        plus_member=random.choice([True, False]),
        segment=random.choice(["vip", "regular", "new"])
    )
    
    # Sample products
    products = [
        Product(
            product_id=f"P{random.randint(1000000, 9999999)}",
            name="iPhone 15 Pro",
            price=134900.0,
            quantity=1,
            seller_id="SELLER001",
            warehouse_location="Mumbai",
            category="electronics",
            weight_kg=0.2
        ),
        Product(
            product_id=f"P{random.randint(1000000, 9999999)}",
            name="AirPods Pro",
            price=24900.0,
            quantity=1,
            seller_id="SELLER001",
            warehouse_location="Mumbai",
            category="electronics",
            weight_kg=0.1
        )
    ]
    
    return CheckoutContext(
        checkout_id=f"CHK{uuid.uuid4().hex[:12].upper()}",
        user=user,
        products=products,
        payment_method=random.choice(list(PaymentMethod)),
        is_bbd=random.choice([True, False]),
        discount_code="BBD2024" if random.random() < 0.3 else None,
        shipping_address={"city": user.city, "state": user.state, "pincode": user.pincode},
        billing_address={"city": user.city, "state": user.state, "pincode": user.pincode}
    )

async def main():
    """
    Main function - Flipkart checkout tracing demonstration
    """
    print("🛒 Flipkart Checkout Distributed Tracing Demo")
    print("📊 OpenTelemetry implementation for Indian e-commerce scale")
    print("🎯 Big Billion Days ready with complete flow tracing")
    print("\nTracing Features:")
    print("  ✅ Complete checkout flow tracking")
    print("  ✅ Multi-service span correlation")
    print("  ✅ Payment gateway integration")
    print("  ✅ Indian tax (GST) calculation")
    print("  ✅ Regional performance analysis")
    print("  ✅ BBD load simulation")
    print("\nAccess URLs:")
    print("  🔍 Jaeger UI: http://localhost:16686")
    print("  📊 Metrics: http://localhost:8000/metrics")
    print("\nPress Ctrl+C to stop\n")
    
    # Initialize tracing service
    tracing_service = FlipkartTracingService()
    
    # Simulate multiple checkout flows
    for i in range(5):
        print(f"\n🔄 Processing checkout {i+1}/5...")
        
        # Create sample context
        checkout_context = create_sample_checkout_context()
        
        # Process checkout with tracing
        result = await tracing_service.trace_complete_checkout(checkout_context)
        
        if result["success"]:
            print(f"✅ Checkout successful - Order: {result['order_id']}")
        else:
            print(f"❌ Checkout failed - Errors: {result['errors']}")
        
        # Wait between checkouts
        await asyncio.sleep(2)
    
    print("\n🎉 Tracing demonstration completed!")
    print("Check Jaeger UI for detailed trace analysis")

if __name__ == "__main__":
    asyncio.run(main())

"""
Production Deployment Notes:

1. OpenTelemetry Configuration:
   - Set proper service name and version
   - Configure resource attributes for environment
   - Set up proper sampling rates for production
   - Use batch span processors for performance

2. Jaeger Setup:
   - Deploy Jaeger with proper storage backend
   - Configure retention policies
   - Set up proper authentication
   - Scale collector and query services

3. Trace Sampling:
   - Always sample: Payment failures, errors
   - High sample rate (10%): Checkout flows
   - Low sample rate (1%): Health checks
   - Adaptive sampling during BBD

4. Custom Instrumentation:
   - Business logic tracing
   - Database query tracking
   - External API call monitoring
   - Performance bottleneck identification

5. Alert Integration:
   - Trace-based alerting for high error rates
   - Latency percentile monitoring
   - Business metric correlation
   - Regional performance degradation

Example Trace Queries:
- Error rate: service_operation_error_total
- P99 latency: service_operation_latency{quantile="0.99"}
- Checkout success rate: checkout_flow_success_rate
- Payment gateway performance: payment_gateway_latency by gateway

Span Attributes Best Practices:
- Use consistent naming conventions
- Include business context (user tier, region)
- Add correlation IDs for debugging
- Limit cardinality for performance
"""
#!/usr/bin/env python3
"""
Jaeger Distributed Tracing System
Microservices Tracing for Indian E-commerce - Flipkart, Myntra, Nykaa

यह system distributed tracing implement करता है Jaeger के साथ।
Production में request flow tracking, performance bottlenecks, और dependency mapping।

Real-world Context:
- Flipkart processes 5M+ orders with 50+ microservices
- Average request touches 15-20 services during checkout
- Trace correlation reduces debugging time from days to hours
- 99th percentile latency monitoring for SLA compliance
"""

import time
import uuid
import random
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import threading
from contextlib import contextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Span:
    """Distributed tracing span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, Any] = None
    logs: List[Dict[str, Any]] = None
    status: str = "ok"  # ok, error, timeout
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.logs is None:
            self.logs = []

class FlipkartTracer:
    """
    Production Distributed Tracer for Indian E-commerce
    
    Features:
    - Request correlation across microservices
    - Performance bottleneck identification
    - Error propagation tracking
    - Business transaction mapping
    - Real-time trace analysis
    """
    
    def __init__(self, service_name: str = "flipkart-api-gateway"):
        self.service_name = service_name
        self.active_spans: Dict[str, Span] = {}
        self.completed_traces: Dict[str, List[Span]] = {}
        self.span_storage: List[Span] = []
        
        # Service topology for Indian e-commerce
        self.service_topology = {
            'api-gateway': {
                'downstream': ['user-service', 'product-service', 'cart-service'],
                'datacenter': 'mumbai-dc1',
                'team': 'platform'
            },
            'user-service': {
                'downstream': ['kyc-service', 'wallet-service', 'notification-service'],
                'datacenter': 'mumbai-dc1',
                'team': 'user-platform'
            },
            'product-service': {
                'downstream': ['inventory-service', 'catalog-service', 'recommendation-service'],
                'datacenter': 'bangalore-dc1',
                'team': 'product-platform'
            },
            'cart-service': {
                'downstream': ['pricing-service', 'coupon-service', 'inventory-service'],
                'datacenter': 'mumbai-dc1',
                'team': 'commerce'
            },
            'order-service': {
                'downstream': ['payment-service', 'fulfillment-service', 'notification-service'],
                'datacenter': 'mumbai-dc1',
                'team': 'order-management'
            },
            'payment-service': {
                'downstream': ['razorpay-gateway', 'paytm-gateway', 'upi-service'],
                'datacenter': 'mumbai-dc1',
                'team': 'payments'
            },
            'fulfillment-service': {
                'downstream': ['logistics-service', 'packaging-service', 'tracking-service'],
                'datacenter': 'chennai-dc1',
                'team': 'supply-chain'
            }
        }
        
        logger.info(f"Distributed tracer initialized for {service_name}")
    
    def start_trace(self, operation_name: str, **tags) -> str:
        """Start a new distributed trace"""
        trace_id = self._generate_trace_id()
        span_id = self._generate_span_id()
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            operation_name=operation_name,
            service_name=self.service_name,
            start_time=time.time(),
            tags={
                'service.name': self.service_name,
                'span.kind': 'server',
                'component': 'flipkart-platform',
                **tags
            }
        )
        
        self.active_spans[span_id] = span
        return trace_id
    
    @contextmanager
    def span(
        self,
        operation_name: str,
        trace_id: str,
        parent_span_id: Optional[str] = None,
        **tags
    ):
        """Context manager for creating spans"""
        span_id = self._generate_span_id()
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=self.service_name,
            start_time=time.time(),
            tags={
                'service.name': self.service_name,
                **tags
            }
        )
        
        self.active_spans[span_id] = span
        
        try:
            yield span
            span.status = "ok"
        except Exception as e:
            span.status = "error"
            span.tags['error'] = True
            span.tags['error.message'] = str(e)
            self._log_to_span(span, "error", {"message": str(e)})
            raise
        finally:
            span.end_time = time.time()
            span.duration_ms = (span.end_time - span.start_time) * 1000
            self._finish_span(span)
    
    def _finish_span(self, span: Span):
        """Finish and store completed span"""
        if span.span_id in self.active_spans:
            del self.active_spans[span.span_id]
        
        self.span_storage.append(span)
        
        # Group spans by trace
        if span.trace_id not in self.completed_traces:
            self.completed_traces[span.trace_id] = []
        self.completed_traces[span.trace_id].append(span)
    
    def _log_to_span(self, span: Span, level: str, fields: Dict[str, Any]):
        """Add log entry to span"""
        log_entry = {
            'timestamp': time.time(),
            'level': level,
            'fields': fields
        }
        span.logs.append(log_entry)
    
    def _generate_trace_id(self) -> str:
        """Generate unique trace ID"""
        return f"flipkart-{uuid.uuid4().hex[:16]}"
    
    def _generate_span_id(self) -> str:
        """Generate unique span ID"""
        return uuid.uuid4().hex[:8]
    
    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """Get comprehensive trace summary"""
        if trace_id not in self.completed_traces:
            return {}
        
        spans = self.completed_traces[trace_id]
        
        # Calculate trace metrics
        total_duration = max(span.duration_ms or 0 for span in spans)
        service_count = len(set(span.service_name for span in spans))
        span_count = len(spans)
        error_count = len([span for span in spans if span.status == "error"])
        
        # Build service call graph
        service_calls = {}
        for span in spans:
            service = span.service_name
            if service not in service_calls:
                service_calls[service] = {
                    'operations': [],
                    'duration_ms': 0,
                    'error_count': 0
                }
            
            service_calls[service]['operations'].append(span.operation_name)
            service_calls[service]['duration_ms'] += span.duration_ms or 0
            if span.status == "error":
                service_calls[service]['error_count'] += 1
        
        # Find critical path
        critical_path = self._find_critical_path(spans)
        
        return {
            'trace_id': trace_id,
            'total_duration_ms': total_duration,
            'service_count': service_count,
            'span_count': span_count,
            'error_count': error_count,
            'success_rate': ((span_count - error_count) / span_count * 100) if span_count > 0 else 0,
            'service_calls': service_calls,
            'critical_path': critical_path,
            'root_span': next((span for span in spans if span.parent_span_id is None), None)
        }
    
    def _find_critical_path(self, spans: List[Span]) -> List[str]:
        """Find the critical path through the trace"""
        # Build span relationships
        span_map = {span.span_id: span for span in spans}
        children = {}
        
        for span in spans:
            if span.parent_span_id:
                if span.parent_span_id not in children:
                    children[span.parent_span_id] = []
                children[span.parent_span_id].append(span.span_id)
        
        # Find longest path
        def get_path_duration(span_id: str) -> Tuple[float, List[str]]:
            span = span_map[span_id]
            if span_id not in children:
                return span.duration_ms or 0, [span.operation_name]
            
            max_duration = 0
            max_path = []
            
            for child_id in children[span_id]:
                child_duration, child_path = get_path_duration(child_id)
                if child_duration > max_duration:
                    max_duration = child_duration
                    max_path = child_path
            
            return (span.duration_ms or 0) + max_duration, [span.operation_name] + max_path
        
        # Start from root spans
        root_spans = [span for span in spans if span.parent_span_id is None]
        if not root_spans:
            return []
        
        _, critical_path = get_path_duration(root_spans[0].span_id)
        return critical_path

class EcommerceTraceSimulator:
    """Simulate realistic e-commerce transaction traces"""
    
    def __init__(self, tracer: FlipkartTracer):
        self.tracer = tracer
        self.running = True
    
    async def simulate_product_search(self, trace_id: str, parent_span_id: str = None):
        """Simulate product search flow"""
        
        with self.tracer.span(
            "product_search",
            trace_id,
            parent_span_id,
            operation="search",
            search_query="iphone 15",
            user_tier="gold"
        ) as search_span:
            
            # Simulate search in product service
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Call downstream services
            await self.simulate_catalog_lookup(trace_id, search_span.span_id)
            await self.simulate_recommendation_service(trace_id, search_span.span_id)
            await self.simulate_inventory_check(trace_id, search_span.span_id)
    
    async def simulate_catalog_lookup(self, trace_id: str, parent_span_id: str):
        """Simulate catalog service call"""
        
        with self.tracer.span(
            "catalog_lookup",
            trace_id,
            parent_span_id,
            service_name="catalog-service",
            database="postgres",
            table="products"
        ) as catalog_span:
            
            # Simulate database query
            await asyncio.sleep(random.uniform(0.05, 0.15))
            
            # Add business context
            catalog_span.tags['product_count'] = random.randint(10, 100)
            catalog_span.tags['category'] = "electronics"
            
            self.tracer._log_to_span(
                catalog_span, 
                "info", 
                {"message": "Products fetched from catalog", "count": 25}
            )
    
    async def simulate_recommendation_service(self, trace_id: str, parent_span_id: str):
        """Simulate ML recommendation service"""
        
        with self.tracer.span(
            "get_recommendations",
            trace_id,
            parent_span_id,
            service_name="recommendation-service",
            ml_model="collaborative_filtering_v2",
            datacenter="bangalore"
        ) as rec_span:
            
            # Simulate ML inference
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            rec_span.tags['recommendation_count'] = 10
            rec_span.tags['model_confidence'] = 0.89
    
    async def simulate_inventory_check(self, trace_id: str, parent_span_id: str):
        """Simulate inventory availability check"""
        
        with self.tracer.span(
            "check_inventory",
            trace_id,
            parent_span_id,
            service_name="inventory-service",
            cache="redis",
            warehouse="mumbai_bkc"
        ) as inv_span:
            
            await asyncio.sleep(random.uniform(0.08, 0.2))
            
            # Sometimes inventory service has issues
            if random.random() < 0.05:  # 5% error rate
                raise Exception("Inventory service timeout")
            
            inv_span.tags['in_stock'] = True
            inv_span.tags['quantity'] = random.randint(1, 50)
    
    async def simulate_checkout_flow(self, trace_id: str, parent_span_id: str = None):
        """Simulate complete checkout flow"""
        
        with self.tracer.span(
            "checkout_flow",
            trace_id,
            parent_span_id,
            user_id="user_123456",
            cart_value=15999.0,
            payment_method="upi"
        ) as checkout_span:
            
            # User validation
            await self.simulate_user_validation(trace_id, checkout_span.span_id)
            
            # Price calculation
            await self.simulate_price_calculation(trace_id, checkout_span.span_id)
            
            # Payment processing
            await self.simulate_payment_processing(trace_id, checkout_span.span_id)
            
            # Order creation
            await self.simulate_order_creation(trace_id, checkout_span.span_id)
    
    async def simulate_user_validation(self, trace_id: str, parent_span_id: str):
        """Simulate user validation"""
        
        with self.tracer.span(
            "validate_user",
            trace_id,
            parent_span_id,
            service_name="user-service",
            validation_type="kyc_check"
        ) as user_span:
            
            await asyncio.sleep(random.uniform(0.05, 0.15))
            
            # KYC service call
            with self.tracer.span(
                "kyc_verification",
                trace_id,
                user_span.span_id,
                service_name="kyc-service",
                kyc_status="verified"
            ):
                await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def simulate_price_calculation(self, trace_id: str, parent_span_id: str):
        """Simulate dynamic pricing calculation"""
        
        with self.tracer.span(
            "calculate_pricing",
            trace_id,
            parent_span_id,
            service_name="pricing-service",
            pricing_strategy="dynamic"
        ) as price_span:
            
            await asyncio.sleep(random.uniform(0.1, 0.25))
            
            # Coupon service
            with self.tracer.span(
                "apply_coupons",
                trace_id,
                price_span.span_id,
                service_name="coupon-service"
            ):
                await asyncio.sleep(random.uniform(0.05, 0.1))
                
            price_span.tags['final_amount'] = 15999.0
            price_span.tags['discount'] = 1000.0
    
    async def simulate_payment_processing(self, trace_id: str, parent_span_id: str):
        """Simulate payment processing with multiple gateways"""
        
        with self.tracer.span(
            "process_payment",
            trace_id,
            parent_span_id,
            service_name="payment-service",
            amount=15999.0,
            currency="INR"
        ) as payment_span:
            
            # Try UPI first
            try:
                with self.tracer.span(
                    "upi_payment",
                    trace_id,
                    payment_span.span_id,
                    service_name="upi-service",
                    gateway="razorpay",
                    bank="hdfc"
                ) as upi_span:
                    
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                    
                    # Simulate UPI failures
                    if random.random() < 0.1:  # 10% failure rate
                        raise Exception("UPI transaction failed")
                    
                    upi_span.tags['transaction_id'] = f"upi_{uuid.uuid4().hex[:12]}"
                    upi_span.tags['bank_ref'] = f"hdfc_{random.randint(100000, 999999)}"
                    
            except Exception as e:
                # Fallback to card payment
                with self.tracer.span(
                    "card_payment_fallback",
                    trace_id,
                    payment_span.span_id,
                    service_name="card-service",
                    gateway="paytm"
                ) as card_span:
                    
                    await asyncio.sleep(random.uniform(0.3, 1.0))
                    card_span.tags['transaction_id'] = f"card_{uuid.uuid4().hex[:12]}"
    
    async def simulate_order_creation(self, trace_id: str, parent_span_id: str):
        """Simulate order creation and fulfillment"""
        
        with self.tracer.span(
            "create_order",
            trace_id,
            parent_span_id,
            service_name="order-service",
            order_type="standard"
        ) as order_span:
            
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            order_id = f"ORD{random.randint(1000000, 9999999)}"
            order_span.tags['order_id'] = order_id
            
            # Fulfillment service
            with self.tracer.span(
                "assign_fulfillment",
                trace_id,
                order_span.span_id,
                service_name="fulfillment-service",
                warehouse="mumbai_bkc"
            ) as fulfill_span:
                
                await asyncio.sleep(random.uniform(0.2, 0.4))
                fulfill_span.tags['estimated_delivery'] = "2024-12-15"
                
                # Notification service
                with self.tracer.span(
                    "send_confirmation",
                    trace_id,
                    fulfill_span.span_id,
                    service_name="notification-service",
                    channel="sms"
                ):
                    await asyncio.sleep(random.uniform(0.05, 0.1))

def demonstrate_distributed_tracing():
    """Demonstrate distributed tracing for Indian e-commerce"""
    print("\n🔍 Jaeger Distributed Tracing Demo - Indian E-commerce")
    print("=" * 55)
    
    # Initialize tracer
    tracer = FlipkartTracer("flipkart-api-gateway")
    simulator = EcommerceTraceSimulator(tracer)
    
    print("✅ Distributed tracer initialized")
    print("🛒 Simulating e-commerce microservices traces")
    
    async def run_trace_simulation():
        # Scenario 1: Product search trace
        print("\n🔍 Scenario 1: Product Search Flow")
        print("-" * 35)
        
        search_trace_id = tracer.start_trace(
            "product_search_request",
            http_method="GET",
            http_url="/api/v1/search?q=iphone",
            user_id="user_123456",
            user_tier="gold"
        )
        
        try:
            with tracer.span(
                "api_gateway_request",
                search_trace_id,
                http_status_code=200
            ) as gateway_span:
                
                await simulator.simulate_product_search(search_trace_id, gateway_span.span_id)
                
        except Exception as e:
            logger.error(f"Search trace error: {e}")
        
        print(f"   ✅ Search trace completed: {search_trace_id}")
        
        # Scenario 2: Checkout flow trace
        print("\n💳 Scenario 2: Checkout Flow")
        print("-" * 28)
        
        checkout_trace_id = tracer.start_trace(
            "checkout_request",
            http_method="POST",
            http_url="/api/v1/checkout",
            user_id="user_789012",
            cart_items=2,
            total_amount=15999.0
        )
        
        try:
            with tracer.span(
                "api_gateway_checkout",
                checkout_trace_id,
                business_transaction="order_placement"
            ) as checkout_gateway:
                
                await simulator.simulate_checkout_flow(checkout_trace_id, checkout_gateway.span_id)
                
        except Exception as e:
            logger.error(f"Checkout trace error: {e}")
        
        print(f"   ✅ Checkout trace completed: {checkout_trace_id}")
        
        # Analyze traces
        print("\n📊 Trace Analysis")
        print("-" * 17)
        
        # Analyze search trace
        search_summary = tracer.get_trace_summary(search_trace_id)
        if search_summary:
            print(f"\n🔍 Search Trace Analysis:")
            print(f"   Duration: {search_summary['total_duration_ms']:.2f}ms")
            print(f"   Services: {search_summary['service_count']}")
            print(f"   Spans: {search_summary['span_count']}")
            print(f"   Success Rate: {search_summary['success_rate']:.1f}%")
            print(f"   Critical Path: {' → '.join(search_summary['critical_path'])}")
            
            print("\n   Service Breakdown:")
            for service, metrics in search_summary['service_calls'].items():
                print(f"     • {service}: {metrics['duration_ms']:.2f}ms")
                if metrics['error_count'] > 0:
                    print(f"       ⚠️  {metrics['error_count']} errors")
        
        # Analyze checkout trace
        checkout_summary = tracer.get_trace_summary(checkout_trace_id)
        if checkout_summary:
            print(f"\n💳 Checkout Trace Analysis:")
            print(f"   Duration: {checkout_summary['total_duration_ms']:.2f}ms")
            print(f"   Services: {checkout_summary['service_count']}")
            print(f"   Spans: {checkout_summary['span_count']}")
            print(f"   Success Rate: {checkout_summary['success_rate']:.1f}%")
            print(f"   Critical Path: {' → '.join(checkout_summary['critical_path'][:5])}...")
        
        return [search_trace_id, checkout_trace_id]
    
    # Run simulation
    trace_ids = asyncio.run(run_trace_simulation())
    
    # Show trace storage stats
    print(f"\n📈 Tracing Statistics")
    print("-" * 22)
    print(f"📊 Total traces: {len(tracer.completed_traces)}")
    print(f"📊 Total spans: {len(tracer.span_storage)}")
    print(f"📊 Active spans: {len(tracer.active_spans)}")
    
    # Show service topology
    print(f"\n🏗️  Service Topology")
    print("-" * 19)
    
    print("🌐 Microservices Architecture:")
    for service, config in tracer.service_topology.items():
        print(f"   • {service} ({config['team']}) - {config['datacenter']}")
        if config['downstream']:
            print(f"     → {', '.join(config['downstream'])}")
    
    # Best practices
    print(f"\n💡 Distributed Tracing Best Practices")
    print("-" * 38)
    print("✓ Trace ID propagation across all services")
    print("✓ Sampling strategies for high-volume systems")
    print("✓ Business context in spans (user_id, order_id)")
    print("✓ Error tracking and root cause analysis")
    print("✓ Performance bottleneck identification")
    print("✓ Service dependency mapping")
    print("✓ Critical path analysis for optimization")
    print("✓ Integration with metrics and logging")

if __name__ == "__main__":
    demonstrate_distributed_tracing()
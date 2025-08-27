# Episode 094: Distributed Tracing & Observability - Part 2
## Implementation & Tools - Jaeger, Zipkin, and Real Production (Minutes 61-120)

*Total Word Count Target: 7,000 words*

---

## Chapter 6: Jaeger - Uber's Gift to Distributed Tracing

### Understanding Jaeger Architecture

"Jaeger, jo Uber ne banaya, is like having CCTV cameras on every street corner in Mumbai - har movement track hoti hai, har turn visible hai!"

```python
import jaeger_client
from jaeger_client import Config
from opentracing import tracer as opentracing_tracer
import time
import random

class OlaJaegerImplementation:
    """
    Ola's Jaeger setup for ride tracking
    Handling 1 million rides per day across India
    """
    
    def __init__(self):
        # Jaeger configuration - production setup
        config = Config(
            config={
                'sampler': {
                    'type': 'adaptive',  # Adaptive sampling for high traffic
                    'param': 0.001,      # 0.1% sampling initially
                    'max_traces_per_second': 100  # Rate limiting
                },
                'local_agent': {
                    'reporting_host': 'jaeger-agent.ola.internal',
                    'reporting_port': '6831',
                },
                'logging': True,
                'reporter_batch_size': 100,
                'reporter_queue_size': 1000,
                'propagation': 'b3',  # Zipkin B3 headers for compatibility
                'tags': {
                    'service.environment': 'production',
                    'service.region': 'india',
                    'service.datacenter': 'mumbai-dc1'
                }
            },
            service_name='ola-ride-service',
            validate=True,
        )
        
        self.tracer = config.initialize_tracer()
    
    def trace_ride_booking(self, ride_request):
        """
        Complete ride booking flow with Jaeger tracing
        From request to driver assignment
        """
        
        # Start root span
        with self.tracer.start_span('book_ride') as booking_span:
            booking_span.set_tag('ride.type', ride_request['ride_type'])
            booking_span.set_tag('customer.id', ride_request['customer_id'])
            booking_span.set_tag('pickup.location', ride_request['pickup'])
            booking_span.set_tag('drop.location', ride_request['drop'])
            booking_span.set_tag('estimated.fare', ride_request['estimated_fare'])
            
            # Step 1: Validate customer
            with self.tracer.start_span('validate_customer', 
                                       child_of=booking_span) as validate_span:
                validate_span.set_tag('customer.tier', 'gold')
                validate_span.set_tag('customer.rating', 4.8)
                
                # Check blacklist
                with self.tracer.start_span('check_blacklist',
                                           child_of=validate_span) as blacklist_span:
                    time.sleep(0.01)  # Simulate DB check
                    blacklist_span.set_tag('blacklisted', False)
                
                # Check payment method
                with self.tracer.start_span('verify_payment',
                                           child_of=validate_span) as payment_span:
                    payment_span.set_tag('payment.method', 'upi')
                    payment_span.set_tag('payment.verified', True)
                    time.sleep(0.02)
            
            # Step 2: Find nearby drivers
            with self.tracer.start_span('find_drivers',
                                       child_of=booking_span) as driver_span:
                driver_span.set_tag('search.radius_km', 3)
                
                # Geo query
                with self.tracer.start_span('geo_query',
                                           child_of=driver_span) as geo_span:
                    geo_span.set_tag('database', 'redis-geo')
                    geo_span.set_tag('query.type', 'GEORADIUS')
                    time.sleep(0.05)
                    
                    drivers_found = random.randint(5, 20)
                    geo_span.set_tag('drivers.found', drivers_found)
                
                # Filter available drivers
                with self.tracer.start_span('filter_available',
                                           child_of=driver_span) as filter_span:
                    available_drivers = drivers_found - random.randint(0, 5)
                    filter_span.set_tag('drivers.available', available_drivers)
                    
                    if available_drivers == 0:
                        filter_span.set_tag('error', True)
                        filter_span.log_kv({'event': 'no_drivers_available'})
                        raise Exception("No drivers available")
            
            # Step 3: Calculate surge pricing
            with self.tracer.start_span('calculate_surge',
                                       child_of=booking_span) as surge_span:
                surge_span.set_tag('demand', 'high')
                surge_span.set_tag('supply', available_drivers)
                
                surge_multiplier = self._calculate_surge(
                    demand=100,
                    supply=available_drivers
                )
                surge_span.set_tag('surge.multiplier', surge_multiplier)
                surge_span.set_tag('final.fare', 
                                  ride_request['estimated_fare'] * surge_multiplier)
            
            # Step 4: Assign driver
            with self.tracer.start_span('assign_driver',
                                       child_of=booking_span) as assign_span:
                
                # Driver selection algorithm
                with self.tracer.start_span('driver_selection',
                                           child_of=assign_span) as select_span:
                    select_span.set_tag('algorithm', 'proximity_rating_hybrid')
                    time.sleep(0.03)
                    
                    selected_driver = {
                        'id': 'DRV-MH-12345',
                        'name': 'Rajesh Kumar',
                        'rating': 4.7,
                        'vehicle': 'Swift Dzire',
                        'number': 'MH 01 AB 1234',
                        'eta_minutes': random.randint(3, 10)
                    }
                    
                    select_span.set_tag('driver.id', selected_driver['id'])
                    select_span.set_tag('driver.eta', selected_driver['eta_minutes'])
                
                # Send notification to driver
                with self.tracer.start_span('notify_driver',
                                           child_of=assign_span) as notify_span:
                    notify_span.set_tag('notification.type', 'push')
                    notify_span.set_tag('fcm.token', 'driver_token_123')
                    time.sleep(0.01)
                
                # Wait for acceptance
                with self.tracer.start_span('await_acceptance',
                                           child_of=assign_span) as accept_span:
                    time.sleep(random.uniform(1, 3))  # Simulate wait
                    
                    accepted = random.choice([True, True, True, False])
                    accept_span.set_tag('driver.accepted', accepted)
                    
                    if not accepted:
                        accept_span.log_kv({'event': 'driver_rejected'})
                        # Would retry with next driver
            
            # Step 5: Confirm booking
            with self.tracer.start_span('confirm_booking',
                                       child_of=booking_span) as confirm_span:
                booking_id = f"OLA-{int(time.time())}"
                confirm_span.set_tag('booking.id', booking_id)
                confirm_span.set_tag('booking.status', 'confirmed')
                
                # Send customer notification
                with self.tracer.start_span('notify_customer',
                                           child_of=confirm_span) as cust_notify:
                    cust_notify.set_tag('channels', ['sms', 'push', 'email'])
                    time.sleep(0.02)
                
                booking_span.set_tag('booking.id', booking_id)
                booking_span.set_tag('success', True)
                
                return booking_id
    
    def _calculate_surge(self, demand, supply):
        """Calculate surge pricing multiplier"""
        if supply == 0:
            return 3.0  # Maximum surge
        
        ratio = demand / supply
        if ratio > 5:
            return 2.5
        elif ratio > 3:
            return 2.0
        elif ratio > 2:
            return 1.5
        else:
            return 1.0
```

### Jaeger Query and Analysis

"Jaeger ka query interface is like Mumbai Police's crime investigation system - har detail, har connection visible!"

```python
class JaegerQueryAnalysis:
    """
    Jaeger query and analysis capabilities
    Used by Swiggy for performance optimization
    """
    
    def __init__(self):
        self.jaeger_query_url = "http://jaeger-query.swiggy.internal:16686"
        self.services = [
            'order-service',
            'restaurant-service',
            'delivery-service',
            'payment-service',
            'notification-service'
        ]
    
    def analyze_slow_traces(self, service_name, threshold_ms=1000):
        """
        Find slow traces for analysis
        Like finding traffic jams in city
        """
        import requests
        
        # Query Jaeger for traces
        params = {
            'service': service_name,
            'minDuration': f"{threshold_ms}ms",
            'limit': 100,
            'lookback': '1h'
        }
        
        response = requests.get(
            f"{self.jaeger_query_url}/api/traces",
            params=params
        )
        
        traces = response.json()['data']
        
        slow_patterns = {
            'database_slow': [],
            'network_timeout': [],
            'cpu_intensive': [],
            'external_api_slow': []
        }
        
        for trace in traces:
            # Analyze trace structure
            spans = trace['spans']
            
            # Find root cause of slowness
            for span in spans:
                duration_ms = span['duration'] / 1000  # Convert to ms
                
                if duration_ms > threshold_ms:
                    # Check span tags for patterns
                    tags = {tag['key']: tag['value'] 
                           for tag in span['tags']}
                    
                    if 'db.type' in tags:
                        slow_patterns['database_slow'].append({
                            'span_id': span['spanID'],
                            'operation': span['operationName'],
                            'duration_ms': duration_ms,
                            'query': tags.get('db.statement', 'N/A')
                        })
                    
                    elif 'http.url' in tags:
                        if 'external' in tags['http.url']:
                            slow_patterns['external_api_slow'].append({
                                'span_id': span['spanID'],
                                'url': tags['http.url'],
                                'duration_ms': duration_ms,
                                'status_code': tags.get('http.status_code')
                            })
                    
                    elif 'error' in tags and tags['error']:
                        slow_patterns['network_timeout'].append({
                            'span_id': span['spanID'],
                            'operation': span['operationName'],
                            'duration_ms': duration_ms,
                            'error': span.get('logs', [])
                        })
        
        return slow_patterns
    
    def trace_comparison(self, trace_id_1, trace_id_2):
        """
        Compare two traces - like comparing two routes to office
        Useful for A/B testing and performance regression
        """
        
        comparison = {
            'trace_1': self._get_trace_details(trace_id_1),
            'trace_2': self._get_trace_details(trace_id_2),
            'analysis': {}
        }
        
        # Duration comparison
        duration_diff = (comparison['trace_2']['duration'] - 
                        comparison['trace_1']['duration'])
        
        comparison['analysis']['duration_change_ms'] = duration_diff
        comparison['analysis']['duration_change_percent'] = (
            (duration_diff / comparison['trace_1']['duration']) * 100
        )
        
        # Span count comparison
        span_diff = (comparison['trace_2']['span_count'] - 
                    comparison['trace_1']['span_count'])
        
        comparison['analysis']['span_count_change'] = span_diff
        
        # Find new operations in trace 2
        ops_1 = set(comparison['trace_1']['operations'])
        ops_2 = set(comparison['trace_2']['operations'])
        
        comparison['analysis']['new_operations'] = list(ops_2 - ops_1)
        comparison['analysis']['removed_operations'] = list(ops_1 - ops_2)
        
        # Performance regression detection
        if duration_diff > comparison['trace_1']['duration'] * 0.2:
            comparison['analysis']['regression_detected'] = True
            comparison['analysis']['severity'] = 'high' if duration_diff > 1000 else 'medium'
        
        return comparison
```

## Chapter 7: Zipkin - Twitter's Distributed Tracing

### Zipkin Architecture and Setup

"Zipkin, Twitter ka contribution, is like Delhi Metro's control room - real-time tracking of every train (request) in the system!"

```java
// Zipkin implementation at Paytm
import zipkin2.Span;
import zipkin2.reporter.AsyncReporter;
import zipkin2.reporter.okhttp3.OkHttpSender;
import brave.Tracing;
import brave.Tracer;
import brave.propagation.B3Propagation;
import brave.propagation.ExtraFieldPropagation;
import brave.sampler.Sampler;

public class PaytmZipkinTracing {
    
    private final Tracer tracer;
    private final AsyncReporter<Span> reporter;
    
    public PaytmZipkinTracing() {
        // Configure Zipkin sender
        OkHttpSender sender = OkHttpSender.create(
            "http://zipkin-collector.paytm.internal:9411/api/v2/spans"
        );
        
        // Configure async reporter for better performance
        reporter = AsyncReporter.builder(sender)
            .queuedMaxSpans(1000)
            .messageTimeout(1, TimeUnit.SECONDS)
            .build();
        
        // Build tracing with Indian context
        Tracing tracing = Tracing.newBuilder()
            .localServiceName("paytm-payment-service")
            .spanReporter(reporter)
            .propagationFactory(
                ExtraFieldPropagation.newFactoryBuilder(B3Propagation.FACTORY)
                    .addPrefixedFields("paytm-", Arrays.asList(
                        "user-tier",
                        "merchant-id", 
                        "payment-mode",
                        "bank-code"
                    ))
                    .build()
            )
            .sampler(Sampler.create(0.1f)) // 10% sampling for high traffic
            .build();
        
        this.tracer = tracing.tracer();
    }
    
    public String processUPIPayment(PaymentRequest request) {
        // Start main span
        Span rootSpan = tracer.newTrace()
            .name("process_upi_payment")
            .tag("payment.amount", String.valueOf(request.getAmount()))
            .tag("payment.mode", "UPI")
            .tag("customer.vpa", request.getUpiId())
            .tag("merchant.id", request.getMerchantId())
            .start();
        
        try (Tracer.SpanInScope ws = tracer.withSpanInScope(rootSpan)) {
            
            // Step 1: Validate UPI ID
            Span validateSpan = tracer.nextSpan()
                .name("validate_upi_id")
                .tag("upi.id", request.getUpiId())
                .start();
            
            try (Tracer.SpanInScope validScope = tracer.withSpanInScope(validateSpan)) {
                boolean isValid = validateUPIWithNPCI(request.getUpiId());
                validateSpan.tag("validation.result", String.valueOf(isValid));
                
                if (!isValid) {
                    validateSpan.tag("error", "invalid_upi_id");
                    throw new InvalidUPIException("Invalid UPI ID");
                }
            } finally {
                validateSpan.finish();
            }
            
            // Step 2: Check account balance
            Span balanceSpan = tracer.nextSpan()
                .name("check_account_balance")
                .tag("bank.name", extractBankFromUPI(request.getUpiId()))
                .start();
            
            try (Tracer.SpanInScope balScope = tracer.withSpanInScope(balanceSpan)) {
                double balance = checkBalanceViaUPI(request.getUpiId());
                balanceSpan.tag("account.balance", String.valueOf(balance));
                
                if (balance < request.getAmount()) {
                    balanceSpan.tag("error", "insufficient_balance");
                    throw new InsufficientBalanceException();
                }
            } finally {
                balanceSpan.finish();
            }
            
            // Step 3: Process through NPCI
            Span npciSpan = tracer.nextSpan()
                .name("npci_transaction")
                .tag("npci.request_id", generateNPCIRequestId())
                .start();
            
            String transactionId;
            try (Tracer.SpanInScope npciScope = tracer.withSpanInScope(npciSpan)) {
                transactionId = processViaNPCI(request);
                npciSpan.tag("transaction.id", transactionId);
                npciSpan.tag("transaction.status", "success");
            } catch (Exception e) {
                npciSpan.tag("error", e.getMessage());
                throw e;
            } finally {
                npciSpan.finish();
            }
            
            // Step 4: Update merchant account
            Span merchantSpan = tracer.nextSpan()
                .name("update_merchant_account")
                .tag("merchant.id", request.getMerchantId())
                .start();
            
            try (Tracer.SpanInScope merchScope = tracer.withSpanInScope(merchantSpan)) {
                updateMerchantBalance(request.getMerchantId(), request.getAmount());
                merchantSpan.tag("update.status", "success");
            } finally {
                merchantSpan.finish();
            }
            
            rootSpan.tag("transaction.id", transactionId);
            rootSpan.tag("status", "success");
            
            return transactionId;
            
        } catch (Exception e) {
            rootSpan.tag("error", e.getMessage());
            throw e;
        } finally {
            rootSpan.finish();
        }
    }
}
```

### Zipkin Storage and Scalability

"Zipkin ka storage is like Indian government's Aadhaar database - billions of records, fast retrieval!"

```python
class ZipkinStorageOptimization:
    """
    Zipkin storage optimization strategies
    Based on Flipkart's Big Billion Days requirements
    """
    
    def __init__(self):
        self.storage_backends = {
            'cassandra': {
                'pros': ['Horizontal scaling', 'High write throughput'],
                'cons': ['Complex operations', 'Higher latency for reads'],
                'use_case': 'Long-term storage (30+ days)',
                'retention_days': 30,
                'estimated_storage_gb_per_day': 500
            },
            'elasticsearch': {
                'pros': ['Fast searches', 'Rich queries', 'Good UI'],
                'cons': ['Memory intensive', 'Complex cluster management'],
                'use_case': 'Recent traces (7 days)',
                'retention_days': 7,
                'estimated_storage_gb_per_day': 300
            },
            'mysql': {
                'pros': ['Simple setup', 'ACID compliance'],
                'cons': ['Limited scale', 'Single point of failure'],
                'use_case': 'Development/Testing only',
                'retention_days': 1,
                'estimated_storage_gb_per_day': 50
            }
        }
    
    def implement_tiered_storage(self):
        """
        Tiered storage strategy for cost optimization
        Like different types of godowns for inventory
        """
        
        tiers = {
            'hot_tier': {
                'description': 'Last 24 hours - Like items in shop display',
                'storage': 'Elasticsearch with SSD',
                'sampling_rate': 1.0,  # Keep everything
                'access_pattern': 'Frequent reads for debugging',
                'retention': '24 hours',
                'estimated_cost_per_gb': 0.50  # USD
            },
            'warm_tier': {
                'description': '1-7 days - Like items in back storage',
                'storage': 'Elasticsearch with HDD',
                'sampling_rate': 0.1,  # Downsample to 10%
                'access_pattern': 'Occasional investigation',
                'retention': '7 days',
                'estimated_cost_per_gb': 0.10
            },
            'cold_tier': {
                'description': '7-30 days - Like warehouse storage',
                'storage': 'Cassandra',
                'sampling_rate': 0.01,  # Keep only 1%
                'access_pattern': 'Rare access for compliance',
                'retention': '30 days',
                'estimated_cost_per_gb': 0.03
            },
            'archive_tier': {
                'description': '30+ days - Like old records in basement',
                'storage': 'S3 Glacier',
                'sampling_rate': 0.001,  # Keep only errors and critical
                'access_pattern': 'Compliance and audit only',
                'retention': '365 days',
                'estimated_cost_per_gb': 0.004
            }
        }
        
        return tiers
    
    def calculate_storage_requirements(self, requests_per_second):
        """
        Calculate storage needs for Big Billion Days level traffic
        """
        
        # Assumptions based on Flipkart's actual data
        avg_spans_per_trace = 50
        avg_span_size_bytes = 1024  # 1KB per span
        sampling_rate = 0.1  # 10% sampling
        
        # Calculate per second
        traces_per_second = requests_per_second * sampling_rate
        spans_per_second = traces_per_second * avg_spans_per_trace
        bytes_per_second = spans_per_second * avg_span_size_bytes
        
        # Calculate daily storage
        gb_per_day = (bytes_per_second * 86400) / (1024**3)
        
        # Factor in different tiers
        storage_by_tier = {
            'hot_tier_gb': gb_per_day * 1.0,  # Keep all
            'warm_tier_gb': gb_per_day * 0.1 * 7,  # 10% for 7 days
            'cold_tier_gb': gb_per_day * 0.01 * 23,  # 1% for 23 more days
            'archive_tier_gb': gb_per_day * 0.001 * 335  # 0.1% for rest of year
        }
        
        total_storage_gb = sum(storage_by_tier.values())
        
        # Cost calculation in INR
        cost_per_month_inr = (
            storage_by_tier['hot_tier_gb'] * 0.50 * 30 * 83 +  # USD to INR
            storage_by_tier['warm_tier_gb'] * 0.10 * 83 +
            storage_by_tier['cold_tier_gb'] * 0.03 * 83 +
            storage_by_tier['archive_tier_gb'] * 0.004 * 83
        )
        
        print(f"📊 Storage Requirements for {requests_per_second} RPS:")
        print(f"  Daily new data: {gb_per_day:.2f} GB")
        print(f"  Total storage needed: {total_storage_gb:.2f} GB")
        print(f"  Monthly cost: ₹{cost_per_month_inr:,.0f}")
        
        return storage_by_tier
```

## Chapter 8: Performance Optimization with Tracing

### Finding Performance Bottlenecks

"Performance bottlenecks are like traffic signals on Mumbai roads - ek signal slow, pura route slow!"

```python
class PerformanceBottleneckAnalyzer:
    """
    Advanced bottleneck detection using tracing
    MakeMyTrip's approach to optimization
    """
    
    def __init__(self):
        self.performance_thresholds = {
            'database_query': 100,  # ms
            'cache_lookup': 10,
            'api_call': 500,
            'computation': 50,
            'network_io': 200
        }
    
    def analyze_trace_for_bottlenecks(self, trace_data):
        """
        Comprehensive bottleneck analysis
        Like finding the slowest moving train in Mumbai local
        """
        
        bottlenecks = {
            'critical_path': [],
            'parallel_slowness': [],
            'repeated_operations': [],
            'n_plus_one_queries': [],
            'missing_cache': []
        }
        
        # Build span tree
        span_tree = self._build_span_tree(trace_data['spans'])
        
        # Find critical path (longest execution path)
        critical_path = self._find_critical_path(span_tree)
        
        for span_id in critical_path:
            span = self._get_span_by_id(trace_data['spans'], span_id)
            duration_ms = span['duration'] / 1000
            
            # Check if span exceeds threshold
            operation_type = self._classify_operation(span['operationName'])
            threshold = self.performance_thresholds.get(operation_type, 100)
            
            if duration_ms > threshold:
                bottlenecks['critical_path'].append({
                    'span_id': span_id,
                    'operation': span['operationName'],
                    'duration_ms': duration_ms,
                    'threshold_ms': threshold,
                    'excess_ms': duration_ms - threshold,
                    'tags': span.get('tags', {})
                })
        
        # Detect N+1 query problems
        db_operations = {}
        for span in trace_data['spans']:
            if 'db.statement' in span.get('tags', {}):
                query = span['tags']['db.statement']
                if query not in db_operations:
                    db_operations[query] = []
                db_operations[query].append(span)
        
        for query, spans in db_operations.items():
            if len(spans) > 3:  # More than 3 similar queries
                bottlenecks['n_plus_one_queries'].append({
                    'query': query[:100],  # First 100 chars
                    'count': len(spans),
                    'total_time_ms': sum(s['duration']/1000 for s in spans),
                    'suggestion': 'Use batch query or JOIN'
                })
        
        # Detect missing cache opportunities
        for span in trace_data['spans']:
            if 'cache.hit' in span.get('tags', {}):
                if not span['tags']['cache.hit']:
                    duration_ms = span['duration'] / 1000
                    if duration_ms > 50:  # Slow miss
                        bottlenecks['missing_cache'].append({
                            'operation': span['operationName'],
                            'duration_ms': duration_ms,
                            'key': span['tags'].get('cache.key', 'unknown')
                        })
        
        return bottlenecks
    
    def generate_optimization_report(self, bottlenecks):
        """
        Generate actionable optimization report
        Like a doctor's prescription for performance
        """
        
        report = {
            'summary': {},
            'recommendations': [],
            'estimated_improvement': {}
        }
        
        # Critical path optimization
        if bottlenecks['critical_path']:
            total_excess = sum(b['excess_ms'] for b in bottlenecks['critical_path'])
            report['summary']['critical_path_excess_ms'] = total_excess
            
            report['recommendations'].append({
                'priority': 'HIGH',
                'issue': f"Critical path has {total_excess}ms excess latency",
                'solution': 'Optimize slowest operations in critical path',
                'operations': [b['operation'] for b in bottlenecks['critical_path'][:3]]
            })
        
        # N+1 query problems
        if bottlenecks['n_plus_one_queries']:
            total_n_plus_one_time = sum(
                q['total_time_ms'] for q in bottlenecks['n_plus_one_queries']
            )
            
            report['recommendations'].append({
                'priority': 'HIGH',
                'issue': f"N+1 queries consuming {total_n_plus_one_time}ms",
                'solution': 'Implement batch queries or use DataLoader pattern',
                'potential_saving_ms': total_n_plus_one_time * 0.8
            })
        
        # Cache optimization
        if bottlenecks['missing_cache']:
            cache_miss_time = sum(
                m['duration_ms'] for m in bottlenecks['missing_cache']
            )
            
            report['recommendations'].append({
                'priority': 'MEDIUM',
                'issue': f"Cache misses causing {cache_miss_time}ms delay",
                'solution': 'Implement aggressive caching for frequently accessed data',
                'potential_saving_ms': cache_miss_time * 0.9
            })
        
        # Calculate total potential improvement
        total_potential_saving = sum(
            rec.get('potential_saving_ms', 0) 
            for rec in report['recommendations']
        )
        
        report['estimated_improvement'] = {
            'current_latency_ms': sum(
                b.get('duration_ms', 0) 
                for b in bottlenecks['critical_path']
            ),
            'potential_saving_ms': total_potential_saving,
            'improvement_percentage': (
                total_potential_saving / 
                report['estimated_improvement'].get('current_latency_ms', 1)
            ) * 100
        }
        
        return report
```

## Chapter 9: Distributed Tracing in Microservices

### Tracing Across Service Boundaries

"Microservices mein tracing is like tracking a Diwali gift package - har ghar (service) se guzarta hai, har jagah kuch add hota hai!"

```go
// Microservice tracing implementation - Razorpay's architecture
package main

import (
    "context"
    "fmt"
    "time"
    
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/trace"
    "go.opentelemetry.io/otel/propagation"
)

// RazorpayPaymentService handles payment processing with tracing
type RazorpayPaymentService struct {
    tracer trace.Tracer
    propagator propagation.TextMapPropagator
}

func NewRazorpayPaymentService() *RazorpayPaymentService {
    tracer := otel.Tracer("razorpay-payment-service")
    propagator := otel.GetTextMapPropagator()
    
    return &RazorpayPaymentService{
        tracer: tracer,
        propagator: propagator,
    }
}

// ProcessPayment handles the complete payment flow
func (s *RazorpayPaymentService) ProcessPayment(ctx context.Context, 
    request PaymentRequest) (*PaymentResponse, error) {
    
    // Start main span
    ctx, span := s.tracer.Start(ctx, "process_payment",
        trace.WithSpanKind(trace.SpanKindServer),
        trace.WithAttributes(
            attribute.String("payment.id", request.PaymentID),
            attribute.Float64("payment.amount", request.Amount),
            attribute.String("payment.currency", "INR"),
            attribute.String("payment.method", request.Method),
            attribute.String("merchant.id", request.MerchantID),
        ))
    defer span.End()
    
    // Step 1: Validate merchant
    if err := s.validateMerchant(ctx, request.MerchantID); err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, "Merchant validation failed")
        return nil, err
    }
    
    // Step 2: Risk assessment
    riskScore := s.assessRisk(ctx, request)
    span.SetAttributes(attribute.Float64("risk.score", riskScore))
    
    if riskScore > 0.8 {
        span.AddEvent("High risk transaction detected",
            trace.WithAttributes(
                attribute.Float64("risk.score", riskScore),
                attribute.String("action", "manual_review_required"),
            ))
        
        // Route to manual review
        return s.routeToManualReview(ctx, request)
    }
    
    // Step 3: Process based on payment method
    var result *PaymentResponse
    var err error
    
    switch request.Method {
    case "UPI":
        result, err = s.processUPIPayment(ctx, request)
    case "CARD":
        result, err = s.processCardPayment(ctx, request)
    case "NETBANKING":
        result, err = s.processNetbanking(ctx, request)
    case "WALLET":
        result, err = s.processWalletPayment(ctx, request)
    default:
        err = fmt.Errorf("unsupported payment method: %s", request.Method)
    }
    
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        return nil, err
    }
    
    span.SetAttributes(
        attribute.String("transaction.id", result.TransactionID),
        attribute.String("transaction.status", result.Status),
    )
    
    return result, nil
}

// processUPIPayment handles UPI specific flow
func (s *RazorpayPaymentService) processUPIPayment(ctx context.Context,
    request PaymentRequest) (*PaymentResponse, error) {
    
    ctx, span := s.tracer.Start(ctx, "process_upi_payment")
    defer span.End()
    
    span.SetAttributes(
        attribute.String("upi.vpa", request.UPIVPA),
        attribute.String("upi.app", request.UPIApp),
    )
    
    // Validate VPA with NPCI
    ctx, validateSpan := s.tracer.Start(ctx, "validate_vpa_npci")
    
    isValid := s.validateVPAWithNPCI(request.UPIVPA)
    validateSpan.SetAttributes(
        attribute.Bool("vpa.valid", isValid),
        attribute.String("npci.response_time", "125ms"),
    )
    validateSpan.End()
    
    if !isValid {
        return nil, fmt.Errorf("invalid VPA: %s", request.UPIVPA)
    }
    
    // Send collect request
    ctx, collectSpan := s.tracer.Start(ctx, "send_collect_request")
    collectSpan.SetAttributes(
        attribute.String("bank.name", s.extractBankFromVPA(request.UPIVPA)),
        attribute.Float64("amount", request.Amount),
    )
    
    collectRequest := &NPCICollectRequest{
        VPA:      request.UPIVPA,
        Amount:   request.Amount,
        RefID:    generateRefID(),
        ExpireAt: time.Now().Add(15 * time.Minute),
    }
    
    response, err := s.sendToNPCI(ctx, collectRequest)
    collectSpan.End()
    
    if err != nil {
        return nil, err
    }
    
    // Wait for customer approval (async)
    ctx, approvalSpan := s.tracer.Start(ctx, "await_customer_approval")
    approvalSpan.SetAttributes(
        attribute.String("notification.sent", "true"),
        attribute.String("timeout", "5m"),
    )
    
    approved := s.waitForApproval(ctx, response.RefID, 5*time.Minute)
    approvalSpan.SetAttributes(attribute.Bool("customer.approved", approved))
    approvalSpan.End()
    
    if !approved {
        return &PaymentResponse{
            Status: "FAILED",
            Reason: "Customer did not approve",
        }, nil
    }
    
    return &PaymentResponse{
        TransactionID: response.TransactionID,
        Status:       "SUCCESS",
        Timestamp:    time.Now(),
    }, nil
}
```

---

*[Part 2 continues reaching 7,000 words with more implementation details...]*

**[TO BE CONTINUED IN PART 3...]**
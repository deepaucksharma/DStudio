#!/usr/bin/env python3
"""
Prometheus Metrics Collection System
Production Monitoring for Indian Fintech - Paytm, PhonePe, Razorpay

यह system comprehensive metrics collection implement करता है Prometheus के साथ।
Production में business metrics, infrastructure metrics, और SLA monitoring।

Real-world Context:
- Paytm monitors 10,000+ metrics across microservices
- PhonePe tracks 100M+ UPI transactions with <1s latency
- Indian fintech requires 99.9% uptime monitoring
- RBI mandates real-time transaction monitoring
"""

import time
import random
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from prometheus_client import Counter, Histogram, Gauge, Summary, Info, start_http_server
import psutil
import asyncio
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics for Indian fintech applications
class PaytmMetricsCollector:
    """
    Production Prometheus Metrics for Indian Fintech
    
    Features:
    - Business metrics (transactions, revenue)
    - Infrastructure metrics (CPU, memory, network)
    - Application metrics (response times, error rates)
    - Custom SLA metrics
    - Real-time dashboard integration
    """
    
    def __init__(self, service_name: str = "paytm-payment-service"):
        self.service_name = service_name
        
        # Business Metrics - Critical for Indian fintech
        self.transaction_counter = Counter(
            'paytm_transactions_total',
            'Total number of transactions processed',
            ['method', 'status', 'currency', 'merchant_type']
        )
        
        self.transaction_amount = Histogram(
            'paytm_transaction_amount_rupees',
            'Transaction amounts in INR',
            ['method', 'merchant_category'],
            buckets=[10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, float('inf')]
        )
        
        self.revenue_gauge = Gauge(
            'paytm_revenue_inr_total',
            'Total revenue in INR',
            ['business_unit', 'city']
        )
        
        # UPI specific metrics (critical for Indian market)
        self.upi_success_rate = Gauge(
            'paytm_upi_success_rate',
            'UPI transaction success rate percentage',
            ['bank', 'hour_of_day']
        )
        
        self.upi_response_time = Histogram(
            'paytm_upi_response_time_seconds',
            'UPI transaction response time',
            ['bank', 'transaction_type'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float('inf')]
        )
        
        # Infrastructure Metrics
        self.cpu_usage = Gauge(
            'paytm_cpu_usage_percent',
            'CPU usage percentage',
            ['instance', 'datacenter']
        )
        
        self.memory_usage = Gauge(
            'paytm_memory_usage_bytes',
            'Memory usage in bytes',
            ['instance', 'type']
        )
        
        self.database_connections = Gauge(
            'paytm_database_connections',
            'Active database connections',
            ['database', 'pool']
        )
        
        # Application Performance Metrics
        self.api_requests = Counter(
            'paytm_api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.api_duration = Histogram(
            'paytm_api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint'],
            buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf')]
        )
        
        self.error_rate = Gauge(
            'paytm_error_rate_percent',
            'Error rate percentage',
            ['service', 'error_type']
        )
        
        # SLA and Compliance Metrics
        self.sla_availability = Gauge(
            'paytm_sla_availability_percent',
            'Service availability percentage',
            ['service', 'tier']
        )
        
        self.compliance_score = Gauge(
            'paytm_compliance_score',
            'Regulatory compliance score',
            ['regulation', 'category']
        )
        
        # Custom Business Logic Metrics
        self.wallet_balance = Histogram(
            'paytm_wallet_balance_inr',
            'User wallet balances in INR',
            ['user_tier', 'kyc_status'],
            buckets=[0, 100, 500, 1000, 2000, 5000, 10000, 25000, 50000, float('inf')]
        )
        
        self.merchant_onboarding = Counter(
            'paytm_merchant_onboarding_total',
            'Total merchants onboarded',
            ['category', 'city', 'onboarding_channel']
        )
        
        # Service info
        self.service_info = Info(
            'paytm_service_info',
            'Service information and metadata'
        )
        
        # Initialize service info
        self.service_info.info({
            'version': '2.1.0',
            'environment': 'production',
            'datacenter': 'mumbai-dc1',
            'service': service_name,
            'team': 'payments-platform'
        })
        
        logger.info(f"Prometheus metrics initialized for {service_name}")
    
    def record_transaction(
        self,
        amount: float,
        method: str = "upi",
        status: str = "success",
        merchant_type: str = "ecommerce",
        bank: str = "hdfc"
    ):
        """Record a financial transaction with comprehensive metrics"""
        
        # Increment transaction counter
        self.transaction_counter.labels(
            method=method,
            status=status,
            currency="INR",
            merchant_type=merchant_type
        ).inc()
        
        # Record transaction amount
        self.transaction_amount.labels(
            method=method,
            merchant_category=merchant_type
        ).observe(amount)
        
        # Update UPI specific metrics
        if method == "upi":
            # Simulate success rate based on bank
            bank_success_rates = {
                'hdfc': 98.5,
                'icici': 98.2,
                'sbi': 97.8,
                'axis': 98.0,
                'kotak': 97.9
            }
            
            current_hour = datetime.now().hour
            success_rate = bank_success_rates.get(bank, 97.0)
            
            # Add some variability based on time of day
            if 9 <= current_hour <= 17:  # Business hours
                success_rate += 0.5
            elif 22 <= current_hour or current_hour <= 6:  # Night hours
                success_rate -= 1.0
            
            self.upi_success_rate.labels(
                bank=bank,
                hour_of_day=str(current_hour)
            ).set(success_rate)
            
            # Record UPI response time
            response_time = random.uniform(0.2, 2.0)  # Simulated response time
            if status == "failed":
                response_time += random.uniform(1.0, 3.0)  # Failed transactions take longer
            
            self.upi_response_time.labels(
                bank=bank,
                transaction_type="p2p" if amount < 5000 else "p2m"
            ).observe(response_time)
        
        logger.info(f"Transaction recorded: {amount} INR via {method} - {status}")
    
    def record_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float
    ):
        """Record API request metrics"""
        
        self.api_requests.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.api_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def update_infrastructure_metrics(self):
        """Update infrastructure monitoring metrics"""
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_usage.labels(
            instance=f"{self.service_name}-1",
            datacenter="mumbai-dc1"
        ).set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.memory_usage.labels(
            instance=f"{self.service_name}-1",
            type="used"
        ).set(memory.used)
        
        self.memory_usage.labels(
            instance=f"{self.service_name}-1",
            type="available"
        ).set(memory.available)
        
        # Simulate database connections
        db_connections = {
            'postgres-payments': random.randint(45, 95),
            'redis-cache': random.randint(20, 50),
            'mongodb-analytics': random.randint(30, 80)
        }
        
        for db, connections in db_connections.items():
            self.database_connections.labels(
                database=db,
                pool="primary"
            ).set(connections)
    
    def update_business_metrics(self):
        """Update business-specific metrics for Indian fintech"""
        
        # Revenue by business unit and city
        business_units = ['payments', 'lending', 'insurance', 'gold']
        cities = ['mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata']
        
        for unit in business_units:
            for city in cities:
                # Simulate revenue (higher for tier-1 cities)
                base_revenue = random.uniform(100000, 500000)
                if city in ['mumbai', 'delhi', 'bangalore']:
                    base_revenue *= 2.5
                
                self.revenue_gauge.labels(
                    business_unit=unit,
                    city=city
                ).set(base_revenue)
        
        # Error rates by service
        services = ['payment-api', 'wallet-service', 'kyc-service', 'notification-service']
        for service in services:
            error_rate = random.uniform(0.1, 2.5)  # 0.1% to 2.5% error rate
            self.error_rate.labels(
                service=service,
                error_type="application_error"
            ).set(error_rate)
        
        # SLA metrics
        tier1_services = ['payment-api', 'upi-gateway']
        tier2_services = ['notification-service', 'analytics-service']
        
        for service in tier1_services:
            availability = random.uniform(99.8, 99.99)  # High availability for critical services
            self.sla_availability.labels(
                service=service,
                tier="tier1"
            ).set(availability)
        
        for service in tier2_services:
            availability = random.uniform(99.0, 99.5)  # Lower SLA for non-critical services
            self.sla_availability.labels(
                service=service,
                tier="tier2"
            ).set(availability)
        
        # Compliance metrics
        regulations = ['rbi_guidelines', 'pci_dss', 'data_protection']
        for regulation in regulations:
            compliance_score = random.uniform(85, 98)  # High compliance scores
            self.compliance_score.labels(
                regulation=regulation,
                category="payments"
            ).set(compliance_score)
        
        # Wallet balance distribution
        user_tiers = ['basic', 'silver', 'gold', 'platinum']
        kyc_statuses = ['verified', 'pending', 'rejected']
        
        for tier in user_tiers:
            for kyc in kyc_statuses:
                # Different balance ranges for different tiers
                if tier == 'basic':
                    balance = random.uniform(0, 2000)
                elif tier == 'silver':
                    balance = random.uniform(500, 10000)
                elif tier == 'gold':
                    balance = random.uniform(2000, 25000)
                else:  # platinum
                    balance = random.uniform(5000, 50000)
                
                self.wallet_balance.labels(
                    user_tier=tier,
                    kyc_status=kyc
                ).observe(balance)
        
        # Merchant onboarding
        categories = ['grocery', 'restaurant', 'pharmacy', 'petrol', 'ecommerce']
        channels = ['app', 'website', 'field_executive', 'partner']
        
        for category in categories:
            for city in cities[:3]:  # Top 3 cities
                for channel in channels:
                    # More onboarding in business hours
                    current_hour = datetime.now().hour
                    base_count = 1
                    if 9 <= current_hour <= 18:
                        base_count = random.randint(2, 5)
                    
                    for _ in range(base_count):
                        self.merchant_onboarding.labels(
                            category=category,
                            city=city,
                            onboarding_channel=channel
                        ).inc()

class MetricsSimulator:
    """Simulate realistic metrics for demonstration"""
    
    def __init__(self, metrics_collector: PaytmMetricsCollector):
        self.collector = metrics_collector
        self.running = True
    
    def simulate_payment_traffic(self):
        """Simulate realistic payment traffic patterns"""
        
        while self.running:
            # Simulate various transaction types
            transaction_types = [
                {'method': 'upi', 'amount_range': (10, 5000), 'weight': 60},
                {'method': 'card', 'amount_range': (100, 10000), 'weight': 25},
                {'method': 'wallet', 'amount_range': (50, 2000), 'weight': 10},
                {'method': 'netbanking', 'amount_range': (500, 25000), 'weight': 5}
            ]
            
            # Choose transaction type based on weight
            weights = [t['weight'] for t in transaction_types]
            selected_type = random.choices(transaction_types, weights=weights)[0]
            
            # Generate transaction
            amount = random.uniform(*selected_type['amount_range'])
            
            # Success rate varies by method
            success_rates = {
                'upi': 0.985,
                'card': 0.92,
                'wallet': 0.995,
                'netbanking': 0.88
            }
            
            is_success = random.random() < success_rates[selected_type['method']]
            status = 'success' if is_success else 'failed'
            
            # Banks and merchant types
            banks = ['hdfc', 'icici', 'sbi', 'axis', 'kotak']
            merchant_types = ['ecommerce', 'grocery', 'restaurant', 'utility', 'travel']
            
            self.collector.record_transaction(
                amount=amount,
                method=selected_type['method'],
                status=status,
                merchant_type=random.choice(merchant_types),
                bank=random.choice(banks)
            )
            
            # Simulate API requests
            endpoints = [
                '/api/v1/payments/initiate',
                '/api/v1/payments/status',
                '/api/v1/wallet/balance',
                '/api/v1/merchants/onboard',
                '/api/v1/kyc/verify'
            ]
            
            endpoint = random.choice(endpoints)
            method = 'POST' if 'initiate' in endpoint or 'onboard' in endpoint else 'GET'
            
            # Response time varies by endpoint
            if 'payments' in endpoint:
                duration = random.uniform(0.05, 1.5)
                status_code = 200 if is_success else random.choice([400, 500, 503])
            else:
                duration = random.uniform(0.01, 0.5)
                status_code = random.choices([200, 400, 500], weights=[95, 3, 2])[0]
            
            self.collector.record_api_request(method, endpoint, status_code, duration)
            
            # Variable sleep based on time of day (more traffic during business hours)
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 21:  # Business hours
                time.sleep(random.uniform(0.1, 0.5))
            else:  # Off hours
                time.sleep(random.uniform(0.5, 2.0))
    
    def update_system_metrics(self):
        """Periodically update system and business metrics"""
        
        while self.running:
            self.collector.update_infrastructure_metrics()
            self.collector.update_business_metrics()
            time.sleep(30)  # Update every 30 seconds
    
    def stop(self):
        """Stop the simulation"""
        self.running = False

def demonstrate_prometheus_metrics():
    """Demonstrate comprehensive Prometheus metrics for Indian fintech"""
    print("\n📊 Prometheus Metrics Collection Demo - Indian Fintech")
    print("=" * 55)
    
    # Initialize metrics collector
    collector = PaytmMetricsCollector("paytm-payment-gateway")
    
    print("✅ Prometheus metrics collector initialized")
    print("📈 Collecting business, infrastructure, and application metrics")
    
    # Start Prometheus HTTP server
    try:
        start_http_server(8000)
        print("🌐 Prometheus metrics server started on :8000")
        print("   Visit http://localhost:8000/metrics to see metrics")
    except Exception as e:
        print(f"⚠️  Could not start HTTP server: {e}")
    
    # Demonstrate various metric types
    print("\n💳 Recording Sample Transactions")
    print("-" * 35)
    
    # Sample transactions
    sample_transactions = [
        {'amount': 1500, 'method': 'upi', 'status': 'success', 'merchant': 'grocery', 'bank': 'hdfc'},
        {'amount': 5000, 'method': 'card', 'status': 'success', 'merchant': 'ecommerce', 'bank': 'icici'},
        {'amount': 500, 'method': 'wallet', 'status': 'failed', 'merchant': 'restaurant', 'bank': 'sbi'},
        {'amount': 25000, 'method': 'netbanking', 'status': 'success', 'merchant': 'travel', 'bank': 'axis'},
        {'amount': 200, 'method': 'upi', 'status': 'success', 'merchant': 'utility', 'bank': 'kotak'}
    ]
    
    for txn in sample_transactions:
        collector.record_transaction(**txn)
        print(f"   💰 {txn['amount']} INR via {txn['method']} - {txn['status']}")
        time.sleep(0.5)
    
    # Demonstrate API metrics
    print("\n🔗 Recording API Requests")
    print("-" * 25)
    
    api_calls = [
        {'method': 'POST', 'endpoint': '/api/v1/payments/initiate', 'status': 200, 'duration': 0.245},
        {'method': 'GET', 'endpoint': '/api/v1/wallet/balance', 'status': 200, 'duration': 0.082},
        {'method': 'POST', 'endpoint': '/api/v1/kyc/verify', 'status': 400, 'duration': 0.156},
        {'method': 'GET', 'endpoint': '/api/v1/payments/status', 'status': 500, 'duration': 2.1}
    ]
    
    for api_call in api_calls:
        collector.record_api_request(**api_call)
        print(f"   🔗 {api_call['method']} {api_call['endpoint']} - {api_call['status']} ({api_call['duration']}s)")
        time.sleep(0.3)
    
    # Update infrastructure metrics
    print("\n🖥️  Updating Infrastructure Metrics")
    print("-" * 35)
    
    collector.update_infrastructure_metrics()
    print("   ✅ CPU, memory, and database metrics updated")
    
    # Update business metrics
    print("\n📊 Updating Business Metrics")
    print("-" * 30)
    
    collector.update_business_metrics()
    print("   ✅ Revenue, compliance, and SLA metrics updated")
    
    # Start simulation for continuous metrics
    print("\n🔄 Starting Continuous Metrics Simulation")
    print("-" * 42)
    
    simulator = MetricsSimulator(collector)
    
    # Start simulation threads
    traffic_thread = threading.Thread(target=simulator.simulate_payment_traffic)
    metrics_thread = threading.Thread(target=simulator.update_system_metrics)
    
    traffic_thread.daemon = True
    metrics_thread.daemon = True
    
    traffic_thread.start()
    metrics_thread.start()
    
    print("🚀 Traffic simulation started")
    print("📊 System metrics updates started")
    
    # Run simulation for demo
    print("\n⏱️  Running simulation for 30 seconds...")
    time.sleep(30)
    
    simulator.stop()
    
    # Show metrics summary
    print("\n📈 Metrics Collection Summary")
    print("-" * 32)
    print("✅ Business Metrics:")
    print("   • Transaction counters and amounts")
    print("   • Revenue by business unit and city")
    print("   • UPI success rates by bank")
    print("   • Merchant onboarding statistics")
    
    print("✅ Infrastructure Metrics:")
    print("   • CPU and memory usage")
    print("   • Database connection pools")
    print("   • Network and disk I/O")
    
    print("✅ Application Metrics:")
    print("   • API request rates and latencies")
    print("   • Error rates by service")
    print("   • Response time histograms")
    
    print("✅ SLA & Compliance Metrics:")
    print("   • Service availability percentages")
    print("   • Regulatory compliance scores")
    print("   • Performance SLA tracking")
    
    print(f"\n🎯 Key Features Demonstrated:")
    print("   • Multi-dimensional labels")
    print("   • Histogram buckets for Indian transaction amounts")
    print("   • Business-specific metrics for fintech")
    print("   • Real-time UPI performance tracking")
    print("   • Compliance and SLA monitoring")
    
    print(f"\n🔗 Production Integration:")
    print("   • Grafana dashboards for visualization")
    print("   • AlertManager for incident response")
    print("   • Service discovery integration")
    print("   • Long-term storage with remote write")

if __name__ == "__main__":
    demonstrate_prometheus_metrics()
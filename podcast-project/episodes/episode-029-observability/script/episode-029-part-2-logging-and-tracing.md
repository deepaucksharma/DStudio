# Episode 029: Observability & Distributed Tracing - Part 2
## Logging and Tracing (7,000+ words)

---

## Structured Logging Deep Dive - Police Station Record Keeping

Welcome back doston! Part 2 mein hum jaayenge logging aur tracing ke world mein. Socho Mumbai ke police station mein kaise har complaint, har FIR, har action properly record hota hai timestamps ke saath - exactly wahi concept hai structured logging ka.

### The Evolution from Print Statements to Structured Logging

**Traditional Debugging (Ghar ka Jugaad):**
```python
# Old school debugging - Ekdum street-side mechanic style
print("User logged in")
print("Payment started")  
print("Something went wrong!")
print(f"Error: {error}")
```

**Modern Structured Logging (Professional Police Station Style):**
```python
import json
import logging
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, service_name: str, version: str):
        self.service_name = service_name
        self.version = version
        self.logger = logging.getLogger(service_name)
        
        # Configure JSON formatter
        formatter = JsonFormatter()
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(self, level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "service": self.service_name,
            "version": self.version,
            "message": message,
            **kwargs  # Additional context
        }
        
        # Add trace context if available
        current_trace = get_current_trace_context()
        if current_trace:
            log_entry.update({
                "trace_id": current_trace.trace_id,
                "span_id": current_trace.span_id
            })
            
        self.logger.info(json.dumps(log_entry))

# Usage in Flipkart Payment Service
logger = StructuredLogger("payment-service", "v2.3.1")

# User authentication
logger.log_event("INFO", "User authentication attempt",
    user_id="user_789456",
    ip_address="203.192.12.45",
    user_agent="Chrome/118.0",
    country="India",
    state="Maharashtra"
)

# Payment processing
logger.log_event("INFO", "Payment initiated", 
    user_id="user_789456",
    payment_id="pay_987654321", 
    amount=2999.00,
    currency="INR",
    payment_method="UPI",
    merchant_category="Electronics",
    gateway="razorpay"
)

# Error logging with full context
logger.log_event("ERROR", "Payment gateway timeout",
    user_id="user_789456", 
    payment_id="pay_987654321",
    error_type="GATEWAY_TIMEOUT",
    gateway="razorpay",
    timeout_duration=30,
    retry_attempt=3,
    business_impact="revenue_loss",
    estimated_loss_inr=2999.00
)
```

### ELK Stack Implementation - Mumbai Police Station Analogy

Mumbai Police station mein different types of records hote hain - FIR book, visitor log, evidence register. Similarly, ELK stack mein different components handle different aspects:

**E - Elasticsearch (Central Record Repository)**
```python
# Police Station Central Database
class PoliceStationElasticsearch:
    def __init__(self):
        self.es_client = Elasticsearch([
            {"host": "es-master-1", "port": 9200},
            {"host": "es-master-2", "port": 9200}, 
            {"host": "es-master-3", "port": 9200}
        ])
        
    def store_fir(self, fir_data):
        """Store FIR like storing application logs"""
        index_name = f"police-fir-{datetime.now().strftime('%Y-%m')}"
        
        fir_document = {
            "timestamp": fir_data["incident_time"],
            "fir_number": fir_data["fir_no"],
            "incident_type": fir_data["type"],
            "location": fir_data["location"],
            "complainant": fir_data["complainant"],
            "accused": fir_data["accused"], 
            "investigating_officer": fir_data["io"],
            "status": fir_data["status"],
            "evidence": fir_data.get("evidence", []),
            "witnesses": fir_data.get("witnesses", [])
        }
        
        self.es_client.index(
            index=index_name,
            document=fir_document
        )

# Real E-commerce Log Storage
class EcommerceElasticsearch:
    def __init__(self):
        self.es_client = Elasticsearch([
            {"host": "es-data-1", "port": 9200},
            {"host": "es-data-2", "port": 9200},
            {"host": "es-data-3", "port": 9200}
        ])
        
        # Index templates for different log types
        self.setup_index_templates()
        
    def setup_index_templates(self):
        """Setup index templates for different services"""
        
        # Payment service logs template
        payment_template = {
            "index_patterns": ["payment-logs-*"],
            "template": {
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "service": {"type": "keyword"},
                        "trace_id": {"type": "keyword"},
                        "span_id": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "payment_id": {"type": "keyword"},
                        "amount": {"type": "double"},
                        "currency": {"type": "keyword"},
                        "payment_method": {"type": "keyword"},
                        "gateway": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "error_code": {"type": "keyword"},
                        "response_time_ms": {"type": "integer"},
                        "ip_address": {"type": "ip"},
                        "country": {"type": "keyword"},
                        "state": {"type": "keyword"}
                    }
                },
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 1,
                    "refresh_interval": "5s",
                    # Automatic lifecycle management
                    "index.lifecycle.name": "payment-logs-policy"
                }
            }
        }
        
        self.es_client.indices.put_template(
            name="payment-logs-template",
            body=payment_template
        )
```

**L - Logstash (Data Processing Pipeline)**
```ruby
# logstash.conf - Processing payment logs
input {
  beats {
    port => 5044
  }
  
  kafka {
    bootstrap_servers => "kafka-1:9092,kafka-2:9092,kafka-3:9092"
    topics => ["payment-logs", "order-logs", "user-logs"]
    consumer_threads => 4
    group_id => "logstash-consumer-group"
  }
}

filter {
  # Parse JSON logs
  json {
    source => "message"
  }
  
  # Add geographic information for IP addresses
  geoip {
    source => "ip_address"
    target => "geoip"
    add_field => {
      "location" => "%{[geoip][city_name]}, %{[geoip][region_name]}"
    }
  }
  
  # Extract payment method details
  if [service] == "payment-service" {
    if [payment_method] == "UPI" {
      # Extract bank from UPI VPA
      grok {
        match => { 
          "upi_vpa" => ".*@(?<upi_bank>[a-z]+)" 
        }
      }
      
      # Classify transaction type
      if [amount] > 50000 {
        mutate {
          add_field => { "transaction_category" => "high_value" }
        }
      } else if [amount] > 10000 {
        mutate {
          add_field => { "transaction_category" => "medium_value" }
        }
      } else {
        mutate {
          add_field => { "transaction_category" => "low_value" }
        }
      }
    }
  }
  
  # Fraud detection scoring
  if [service] == "fraud-detection" {
    ruby {
      code => "
        fraud_indicators = 0
        
        # Check for suspicious patterns
        if event.get('login_location') != event.get('transaction_location')
          fraud_indicators += 1
        end
        
        if event.get('transaction_time').hour < 6 or event.get('transaction_time').hour > 23
          fraud_indicators += 1
        end
        
        if event.get('amount').to_f > event.get('user_avg_transaction') * 5
          fraud_indicators += 2
        end
        
        event.set('fraud_score', fraud_indicators)
        
        if fraud_indicators >= 2
          event.set('requires_manual_review', true)
        end
      "
    }
  }
  
  # Enrich with user context from Redis cache
  elasticsearch {
    hosts => ["redis-1:6379"]
    query => "GET user:%{user_id}"
    fields => {
      "user_tier" => "user_tier"
      "registration_date" => "user_registration_date"
      "last_successful_payment" => "last_payment_date"
    }
  }
  
  # Add business context
  mutate {
    add_field => {
      "business_hour" => "%{[@timestamp]}"
      "day_of_week" => "%{[@timestamp]}"
    }
  }
  
  date {
    match => [ "business_hour", "ISO8601" ]
    target => "business_hour"
  }
  
  # Classify as business hours (9 AM - 9 PM IST)
  if [business_hour][hour] >= 9 and [business_hour][hour] <= 21 {
    mutate {
      add_field => { "is_business_hours" => true }
    }
  } else {
    mutate {
      add_field => { "is_business_hours" => false }
    }
  }
}

output {
  # Route to different indices based on service
  if [service] == "payment-service" {
    elasticsearch {
      hosts => ["es-1:9200", "es-2:9200", "es-3:9200"]
      index => "payment-logs-%{+YYYY.MM.dd}"
    }
  } else if [service] == "order-service" {
    elasticsearch {
      hosts => ["es-1:9200", "es-2:9200", "es-3:9200"] 
      index => "order-logs-%{+YYYY.MM.dd}"
    }
  } else {
    elasticsearch {
      hosts => ["es-1:9200", "es-2:9200", "es-3:9200"]
      index => "application-logs-%{+YYYY.MM.dd}"
    }
  }
  
  # Send high-value transaction logs to security team
  if [transaction_category] == "high_value" {
    email {
      to => "security-team@company.com"
      subject => "High Value Transaction Alert: ₹%{amount}"
      body => "Transaction Details:\nUser: %{user_id}\nAmount: ₹%{amount}\nMethod: %{payment_method}\nTime: %{timestamp}"
    }
  }
  
  # Real-time alerts for failed payments
  if [level] == "ERROR" and [service] == "payment-service" {
    http {
      url => "http://alert-manager:9093/api/v1/alerts"
      http_method => "post"
      content_type => "application/json"
      mapping => {
        "alert" => "PaymentProcessingError"
        "summary" => "Payment failed for user %{user_id}"
        "severity" => "high"
        "labels" => {
          "service" => "%{service}"
          "error_type" => "%{error_code}"
        }
      }
    }
  }
}
```

**K - Kibana (Investigation Dashboard)**
```json
{
  "kibana_dashboard": {
    "title": "Payment Service Investigation Dashboard",
    "panels": [
      {
        "title": "Payment Success Rate by Gateway",
        "type": "line_chart",
        "query": {
          "query": "service:payment-service AND level:INFO",
          "aggregations": {
            "success_rate": {
              "date_histogram": {
                "field": "timestamp",
                "interval": "5m"
              },
              "aggs": {
                "by_gateway": {
                  "terms": {"field": "gateway"},
                  "aggs": {
                    "success_rate": {
                      "filters": {
                        "success": {"match": {"status": "success"}},
                        "total": {"match_all": {}}
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      {
        "title": "Error Analysis by Payment Method",
        "type": "pie_chart", 
        "query": {
          "query": "service:payment-service AND level:ERROR",
          "aggregations": {
            "by_method": {
              "terms": {"field": "payment_method"},
              "aggs": {
                "by_error_code": {
                  "terms": {"field": "error_code"}
                }
              }
            }
          }
        }
      },
      {
        "title": "Geographic Distribution of Transactions",
        "type": "map",
        "query": {
          "query": "service:payment-service AND geoip.location:*",
          "aggregations": {
            "locations": {
              "geohash_grid": {
                "field": "geoip.location",
                "precision": 3
              },
              "aggs": {
                "transaction_volume": {
                  "sum": {"field": "amount"}
                }
              }
            }
          }
        }
      }
    ]
  }
}
```

### Advanced Log Analysis for Indian E-commerce

**Real-time Fraud Detection through Log Analysis:**
```python
class FraudDetectionLogAnalyzer:
    def __init__(self):
        self.redis_client = redis.Redis(host='redis-fraud-cache')
        self.es_client = Elasticsearch(['es-1:9200'])
        
    def analyze_payment_attempt(self, log_entry):
        """Real-time fraud analysis based on log patterns"""
        user_id = log_entry['user_id']
        amount = log_entry['amount']
        location = log_entry.get('geoip', {}).get('city_name', 'Unknown')
        
        fraud_score = 0
        fraud_reasons = []
        
        # Check 1: Velocity fraud (too many transactions)
        recent_transactions = self.get_recent_transactions(user_id, minutes=10)
        if len(recent_transactions) > 5:
            fraud_score += 30
            fraud_reasons.append("high_velocity_transactions")
            
        # Check 2: Location inconsistency
        user_usual_location = self.get_user_usual_location(user_id)
        if user_usual_location and user_usual_location != location:
            distance_km = self.calculate_distance(user_usual_location, location)
            if distance_km > 100:  # More than 100km from usual location
                fraud_score += 25
                fraud_reasons.append("location_anomaly")
                
        # Check 3: Amount anomaly
        user_avg_transaction = self.get_user_avg_transaction(user_id)
        if amount > user_avg_transaction * 10:  # 10x higher than usual
            fraud_score += 40
            fraud_reasons.append("amount_anomaly")
            
        # Check 4: Time-based analysis
        transaction_hour = datetime.now().hour
        if transaction_hour < 6 or transaction_hour > 23:  # Night transactions
            fraud_score += 15
            fraud_reasons.append("unusual_time")
            
        # Check 5: Device fingerprinting
        device_id = log_entry.get('device_id')
        if device_id and self.is_device_suspicious(device_id):
            fraud_score += 35
            fraud_reasons.append("suspicious_device")
            
        # Final fraud assessment
        risk_level = self.calculate_risk_level(fraud_score)
        
        fraud_analysis = {
            "user_id": user_id,
            "fraud_score": fraud_score,
            "risk_level": risk_level,
            "fraud_reasons": fraud_reasons,
            "requires_manual_review": fraud_score > 50,
            "should_block_transaction": fraud_score > 80,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        # Log fraud analysis result
        self.log_fraud_analysis(fraud_analysis)
        
        # Take action based on risk level
        if fraud_analysis["should_block_transaction"]:
            self.block_transaction(log_entry["payment_id"])
            self.notify_security_team(fraud_analysis)
            
        return fraud_analysis
        
    def get_recent_transactions(self, user_id, minutes=10):
        """Query recent transactions from Elasticsearch"""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"user_id": user_id}},
                        {"term": {"service": "payment-service"}},
                        {"range": {
                            "timestamp": {
                                "gte": f"now-{minutes}m"
                            }
                        }}
                    ]
                }
            },
            "sort": [{"timestamp": {"order": "desc"}}]
        }
        
        result = self.es_client.search(
            index="payment-logs-*",
            body=query
        )
        
        return result['hits']['hits']
```

### Real-time Log Streaming with Kafka

**Kafka-based Log Processing Pipeline:**
```python
from kafka import KafkaProducer, KafkaConsumer
import json
from typing import Dict, List
import threading

class RealTimeLogProcessor:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka-1:9092', 'kafka-2:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8'),
            # Optimize for high throughput
            batch_size=16384,
            linger_ms=10,
            compression_type='snappy'
        )
        
        self.consumers = {}
        self.processing_threads = []
        
    def setup_log_topics(self):
        """Setup Kafka topics for different log streams"""
        topics = {
            "payment-logs-critical": {"partitions": 6, "replication": 3},
            "payment-logs-info": {"partitions": 3, "replication": 2},  
            "order-logs": {"partitions": 4, "replication": 2},
            "user-activity-logs": {"partitions": 8, "replication": 2},
            "security-logs": {"partitions": 2, "replication": 3},
            "fraud-alerts": {"partitions": 2, "replication": 3}
        }
        
        for topic, config in topics.items():
            self.create_topic(topic, **config)
            
    def publish_log(self, log_entry: Dict):
        """Smart routing of logs to appropriate topics"""
        service = log_entry.get('service', 'unknown')
        level = log_entry.get('level', 'INFO')
        
        # Route based on service and criticality
        if service == 'payment-service':
            if level in ['ERROR', 'CRITICAL']:
                topic = 'payment-logs-critical'
                # Use user_id as partition key for ordered processing
                partition_key = log_entry.get('user_id', 'default')
            else:
                topic = 'payment-logs-info'
                partition_key = log_entry.get('payment_id', 'default')
                
        elif service == 'fraud-detection':
            topic = 'security-logs'
            partition_key = log_entry.get('user_id', 'default')
            
        elif 'fraud_score' in log_entry and log_entry['fraud_score'] > 50:
            topic = 'fraud-alerts'
            partition_key = log_entry.get('user_id', 'default')
            
        else:
            topic = f"{service}-logs"
            partition_key = 'default'
            
        # Add metadata
        log_entry.update({
            "kafka_topic": topic,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "partition_key": partition_key
        })
        
        # Publish to Kafka
        future = self.producer.send(
            topic=topic,
            key=partition_key,
            value=log_entry
        )
        
        # Handle delivery confirmation asynchronously
        future.add_callback(self.on_send_success)
        future.add_errback(self.on_send_error)
        
    def start_processing_consumers(self):
        """Start background consumers for different log types"""
        
        # Critical payment log processor
        critical_consumer = KafkaConsumer(
            'payment-logs-critical',
            bootstrap_servers=['kafka-1:9092', 'kafka-2:9092'],
            group_id='critical-log-processor',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            # Process immediately, no batching for critical logs
            max_poll_records=1,
            session_timeout_ms=30000
        )
        
        critical_thread = threading.Thread(
            target=self.process_critical_logs,
            args=(critical_consumer,),
            daemon=True
        )
        critical_thread.start()
        self.processing_threads.append(critical_thread)
        
        # Fraud alert processor
        fraud_consumer = KafkaConsumer(
            'fraud-alerts',
            bootstrap_servers=['kafka-1:9092', 'kafka-2:9092'],
            group_id='fraud-alert-processor',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            max_poll_records=10
        )
        
        fraud_thread = threading.Thread(
            target=self.process_fraud_alerts,
            args=(fraud_consumer,),
            daemon=True
        )
        fraud_thread.start()
        self.processing_threads.append(fraud_thread)
        
    def process_critical_logs(self, consumer: KafkaConsumer):
        """Process critical payment logs with immediate action"""
        for message in consumer:
            log_entry = message.value
            
            try:
                # Immediate processing for critical errors
                if log_entry.get('level') == 'ERROR':
                    self.handle_critical_error(log_entry)
                    
                # Store in Elasticsearch for analysis
                self.store_in_elasticsearch(log_entry, index='critical-logs')
                
                # Send to monitoring systems
                self.send_to_monitoring(log_entry)
                
            except Exception as e:
                logger.error(f"Failed to process critical log: {e}")
                # Dead letter queue for failed processing
                self.send_to_dlq(log_entry, str(e))
                
    def handle_critical_error(self, log_entry: Dict):
        """Immediate handling of critical payment errors"""
        error_type = log_entry.get('error_code', 'UNKNOWN_ERROR')
        user_id = log_entry.get('user_id')
        payment_id = log_entry.get('payment_id')
        
        # Circuit breaker pattern
        if error_type == 'GATEWAY_TIMEOUT':
            self.increment_gateway_error_count(log_entry.get('gateway'))
            
            # If too many timeouts, enable circuit breaker
            error_count = self.get_gateway_error_count(log_entry.get('gateway'))
            if error_count > 10:  # 10 errors in current window
                self.enable_circuit_breaker(log_entry.get('gateway'))
                self.notify_ops_team(f"Circuit breaker enabled for {log_entry.get('gateway')}")
                
        # Automatic retry for transient errors
        elif error_type in ['NETWORK_ERROR', 'TEMPORARY_UNAVAILABLE']:
            retry_count = log_entry.get('retry_attempt', 0)
            if retry_count < 3:
                self.schedule_payment_retry(payment_id, retry_count + 1)
                
        # Fraud detection trigger
        elif error_type == 'FRAUD_DETECTED':
            self.trigger_fraud_investigation(user_id, log_entry)
            
    def process_fraud_alerts(self, consumer: KafkaConsumer):
        """Process fraud alerts with ML model updates"""
        batch = []
        
        for message in consumer:
            batch.append(message.value)
            
            # Process in batches of 50 for efficiency
            if len(batch) >= 50:
                self.process_fraud_batch(batch)
                batch = []
                
    def process_fraud_batch(self, fraud_logs: List[Dict]):
        """Batch process fraud alerts"""
        # Update fraud detection models with new patterns
        fraud_patterns = self.extract_fraud_patterns(fraud_logs)
        self.update_fraud_ml_model(fraud_patterns)
        
        # Generate risk scores for affected users
        affected_users = [log['user_id'] for log in fraud_logs]
        risk_scores = self.calculate_user_risk_scores(affected_users)
        
        # Take protective actions for high-risk users
        for user_id, risk_score in risk_scores.items():
            if risk_score > 0.8:
                self.apply_user_restrictions(user_id, risk_score)
```

---

## Distributed Tracing - Dabbawala Route Tracking

Ab aate hain distributed tracing pe - sabse interesting topic! Mumbai ke dabbawala system se better example mil hi nahi sakta tracing explain karne ke liye.

### OpenTelemetry Implementation for Indian E-commerce

**Complete Tracing Setup:**
```python
from opentelemetry import trace, metrics, baggage
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.propagate import inject, extract
import time
import random

class EcommerceTracer:
    def __init__(self, service_name: str, jaeger_endpoint: str):
        # Initialize tracing
        trace.set_tracer_provider(TracerProvider(
            resource=Resource.create({
                "service.name": service_name,
                "service.version": "2.1.0",
                "deployment.environment": "production",
                "telemetry.sdk.language": "python"
            })
        ))
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="jaeger-agent",
            agent_port=6831,
        )
        
        # Batch processing for performance
        span_processor = BatchSpanProcessor(
            jaeger_exporter,
            max_queue_size=2048,
            schedule_delay_millis=5000,
            export_timeout_millis=30000,
            max_export_batch_size=512
        )
        
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        self.tracer = trace.get_tracer(service_name)
        
        # Auto-instrument popular libraries
        RequestsInstrumentor().instrument()
        FlaskInstrumentor().instrument()
        
    def trace_payment_flow(self, user_id: str, order_data: dict):
        """Trace complete payment flow like dabbawala delivery"""
        
        with self.tracer.start_span("payment_flow_initiation") as root_span:
            # Add user context - like dabbawala pickup address
            root_span.set_attributes({
                "user.id": user_id,
                "order.id": order_data["order_id"],
                "order.value": order_data["amount"],
                "order.currency": "INR",
                "order.items_count": len(order_data["items"]),
                "user.tier": self.get_user_tier(user_id),
                "user.city": order_data.get("shipping_city", "Unknown")
            })
            
            # Step 1: User validation (like verifying pickup address)
            with self.tracer.start_span("user_validation") as validation_span:
                validation_span.set_attributes({
                    "validation.type": "kyc_check",
                    "user.kyc_status": "verified"
                })
                
                # Simulate KYC check
                kyc_result = self.verify_user_kyc(user_id)
                validation_span.set_attribute("validation.result", kyc_result)
                
                if not kyc_result:
                    validation_span.record_exception(
                        Exception("KYC validation failed")
                    )
                    validation_span.set_status(
                        trace.Status(trace.StatusCode.ERROR)
                    )
                    return
                    
            # Step 2: Inventory check (like checking dabba availability)
            with self.tracer.start_span("inventory_validation") as inventory_span:
                inventory_span.set_attributes({
                    "inventory.check_type": "real_time",
                    "inventory.warehouse_count": 3
                })
                
                for item in order_data["items"]:
                    # Child span for each item check
                    with self.tracer.start_span(f"item_availability_check") as item_span:
                        item_span.set_attributes({
                            "item.id": item["product_id"],
                            "item.quantity_requested": item["quantity"],
                            "item.warehouse": item.get("warehouse", "mumbai-central")
                        })
                        
                        availability = self.check_item_availability(
                            item["product_id"], 
                            item["quantity"]
                        )
                        item_span.set_attribute("item.available", availability)
                        
                        if not availability:
                            item_span.add_event("out_of_stock", {
                                "alternative_suggested": True,
                                "estimated_restock": "2025-01-15"
                            })
                            
            # Step 3: Payment processing (like dabba sorting and routing)
            with self.tracer.start_span("payment_processing") as payment_span:
                payment_method = order_data.get("payment_method", "UPI")
                payment_span.set_attributes({
                    "payment.method": payment_method,
                    "payment.amount": order_data["amount"],
                    "payment.currency": "INR"
                })
                
                # UPI payment flow tracing
                if payment_method == "UPI":
                    payment_result = self.trace_upi_payment(
                        order_data["upi_vpa"], 
                        order_data["amount"],
                        order_data["order_id"]
                    )
                    
                # Credit card payment flow  
                elif payment_method == "CREDIT_CARD":
                    payment_result = self.trace_credit_card_payment(
                        order_data["card_token"],
                        order_data["amount"]
                    )
                    
                payment_span.set_attribute("payment.status", payment_result["status"])
                payment_span.set_attribute("payment.transaction_id", payment_result["txn_id"])
                
            # Step 4: Order fulfillment (like final delivery)
            if payment_result["status"] == "SUCCESS":
                with self.tracer.start_span("order_fulfillment") as fulfillment_span:
                    fulfillment_span.set_attributes({
                        "fulfillment.type": "standard_delivery",
                        "fulfillment.estimated_delivery": "2025-01-12",
                        "fulfillment.warehouse": "mumbai-bkc"
                    })
                    
                    # Inventory update
                    with self.tracer.start_span("inventory_update") as inv_update_span:
                        self.update_inventory(order_data["items"])
                        inv_update_span.add_event("inventory_decremented")
                        
                    # Notification sending
                    with self.tracer.start_span("customer_notification") as notify_span:
                        self.send_order_confirmation(user_id, order_data["order_id"])
                        notify_span.add_event("sms_sent", {
                            "phone": order_data.get("phone", "****"),
                            "template": "order_confirmation_hindi"
                        })
                        
                    fulfillment_span.add_event("order_confirmed", {
                        "confirmation_id": f"CONF_{random.randint(100000, 999999)}"
                    })
                    
            # Add business metrics to trace
            root_span.set_attributes({
                "business.conversion_completed": payment_result["status"] == "SUCCESS",
                "business.revenue_impact_inr": order_data["amount"] if payment_result["status"] == "SUCCESS" else 0,
                "business.customer_segment": self.get_customer_segment(user_id),
                "business.marketing_channel": order_data.get("utm_source", "direct")
            })
            
    def trace_upi_payment(self, upi_vpa: str, amount: float, order_id: str):
        """Detailed UPI payment tracing"""
        
        with self.tracer.start_span("upi_payment_initiation") as upi_span:
            # Extract bank from UPI VPA
            bank_code = upi_vpa.split('@')[1] if '@' in upi_vpa else 'unknown'
            
            upi_span.set_attributes({
                "upi.vpa_masked": self.mask_upi_vpa(upi_vpa),
                "upi.bank": bank_code,
                "upi.amount": amount,
                "upi.order_reference": order_id
            })
            
            # Step 1: Bank validation
            with self.tracer.start_span("upi_bank_validation") as bank_span:
                bank_span.set_attribute("upi.bank_code", bank_code)
                
                # Simulate bank API call
                bank_response = self.call_bank_validation_api(bank_code, upi_vpa)
                bank_span.set_attributes({
                    "upi.bank_response_time_ms": bank_response["response_time"],
                    "upi.bank_status": bank_response["status"]
                })
                
                if bank_response["status"] != "ACTIVE":
                    bank_span.record_exception(
                        Exception(f"Bank validation failed: {bank_response['error']}")
                    )
                    return {"status": "FAILED", "error": "BANK_VALIDATION_FAILED"}
                    
            # Step 2: NPCI transaction processing
            with self.tracer.start_span("npci_transaction") as npci_span:
                npci_ref = f"NPCI{random.randint(1000000, 9999999)}"
                npci_span.set_attributes({
                    "npci.reference_id": npci_ref,
                    "npci.transaction_type": "P2M",  # Person to Merchant
                    "npci.amount": amount
                })
                
                # Simulate NPCI processing stages
                npci_span.add_event("collect_request_sent", {
                    "timestamp": time.time(),
                    "payer_bank": bank_code
                })
                
                time.sleep(0.1)  # Simulate processing delay
                
                npci_span.add_event("payer_approval_received", {
                    "timestamp": time.time(),
                    "approval_method": "mobile_app"
                })
                
                time.sleep(0.05)
                
                npci_span.add_event("settlement_initiated", {
                    "timestamp": time.time(),
                    "settlement_type": "instant"
                })
                
                # Payment completion
                transaction_id = f"TXN_{random.randint(100000000, 999999999)}"
                npci_span.set_attribute("npci.transaction_id", transaction_id)
                
            upi_span.add_event("payment_completed", {
                "final_status": "SUCCESS",
                "transaction_id": transaction_id,
                "settlement_time": "immediate"
            })
            
            return {
                "status": "SUCCESS", 
                "txn_id": transaction_id,
                "npci_ref": npci_ref
            }
            
    def mask_upi_vpa(self, upi_vpa: str) -> str:
        """Mask UPI VPA for privacy in traces"""
        if '@' in upi_vpa:
            user_part, domain = upi_vpa.split('@')
            if len(user_part) > 4:
                masked_user = user_part[:2] + '*' * (len(user_part) - 4) + user_part[-2:]
                return f"{masked_user}@{domain}"
        return "***@***"
```

### Service Mesh Integration with Istio

**Istio Configuration for Observability:**
```yaml
# istio-observability.yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: ecommerce-observability
spec:
  values:
    telemetry:
      v2:
        enabled: true
        prometheus:
          configOverride:
            metric_relabeling_configs:
              - source_labels: [__name__]
                regex: 'istio_request_duration_milliseconds'
                target_label: __name__
                replacement: 'http_request_duration_seconds'
                
        # Enable distributed tracing  
        tracing:
          - providers:
              jaeger:
                service: "jaeger-collector.observability.svc.cluster.local"
                port: 14268
          - random_sampling_percentage: 1.0  # 1% sampling in production
            
  meshConfig:
    # Global tracing configuration
    defaultConfig:
      tracing:
        sampling: 1.0
        custom_tags:
          business_context:
            header:
              name: "x-business-context"
          user_tier:
            header:
              name: "x-user-tier"
          request_source:
            header:
              name: "x-request-source"
              
---
# Telemetry configuration for business metrics
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: business-metrics
spec:
  metrics:
    - providers:
        - name: prometheus
    - overrides:
        - match:
            metric: ALL_METRICS
          tagOverrides:
            business_unit:
              operation: UPSERT
              value: "ecommerce"
            cost_center:
              operation: UPSERT  
              value: "technology"
              
---
# Custom metric for payment success rate
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry  
metadata:
  name: payment-success-rate
spec:
  selector:
    matchLabels:
      app: payment-service
  metrics:
    - providers:
        - name: prometheus
    - overrides:
        - match:
            metric: requests_total
          tagOverrides:
            payment_method:
              operation: UPSERT
              value: |
                has(request.headers['payment-method']) ?
                request.headers['payment-method'] : 'unknown'
            transaction_amount_bucket:
              operation: UPSERT
              value: |
                has(request.headers['amount']) ?
                (double(request.headers['amount']) > 10000.0 ? 'high' :
                 double(request.headers['amount']) > 1000.0 ? 'medium' : 'low') : 'unknown'
```

### Context Propagation Across Services

**W3C Trace Context Implementation:**
```python
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.w3c import W3CTraceContextPropagator
from opentelemetry.propagators.w3c import W3CBaggagePropagator
from opentelemetry.propagators.composite import CompositePropagator

# Set up W3C trace context propagation
set_global_textmap(
    CompositePropagator([
        W3CTraceContextPropagator(),
        W3CBaggagePropagator(),
    ])
)

class ServiceToServiceCommunication:
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
        
    def call_downstream_service(self, service_url: str, payload: dict, business_context: dict):
        """Make service call with full trace context propagation"""
        
        with self.tracer.start_span("downstream_service_call") as span:
            # Add business context to span
            span.set_attributes({
                "downstream.service_name": self.extract_service_name(service_url),
                "downstream.operation": payload.get("operation", "unknown"),
                "business.user_id": business_context.get("user_id"),
                "business.order_id": business_context.get("order_id"),
                "business.priority": business_context.get("priority", "normal")
            })
            
            # Prepare headers for context propagation
            headers = {}
            
            # Inject W3C trace context
            inject(headers)
            
            # Add business context headers
            headers.update({
                "X-Business-Context": json.dumps(business_context),
                "X-User-Tier": business_context.get("user_tier", "standard"),
                "X-Request-Priority": business_context.get("priority", "normal"),
                "X-Correlation-ID": business_context.get("correlation_id")
            })
            
            # Add baggage for cross-cutting concerns  
            baggage.set_baggage("user.id", business_context.get("user_id"))
            baggage.set_baggage("order.id", business_context.get("order_id"))
            baggage.set_baggage("feature.flags", json.dumps(business_context.get("feature_flags", {})))
            
            try:
                # Make HTTP call with context
                response = requests.post(
                    service_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                # Add response metrics to span
                span.set_attributes({
                    "http.status_code": response.status_code,
                    "http.response_size": len(response.content),
                    "downstream.response_time_ms": response.elapsed.total_seconds() * 1000
                })
                
                if response.status_code >= 400:
                    span.set_status(trace.Status(trace.StatusCode.ERROR))
                    span.record_exception(
                        Exception(f"HTTP {response.status_code}: {response.text}")
                    )
                    
                return response
                
            except requests.exceptions.Timeout as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                span.add_event("request_timeout", {
                    "timeout_duration": "30s",
                    "retry_recommended": True
                })
                raise
                
            except requests.exceptions.RequestException as e:
                span.record_exception(e) 
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                raise
```

### Performance Impact Analysis and Sampling

**Smart Sampling for Production:**
```python
class IndianEcommerceSampler:
    """Custom sampler for Indian e-commerce workloads"""
    
    def __init__(self):
        self.base_sampling_rate = 0.01  # 1% base rate
        self.high_value_threshold = 10000  # ₹10,000
        self.festival_multiplier = 5.0
        self.error_sampling_rate = 1.0  # Always sample errors
        
    def should_sample(self, context, trace_id, name, kind, attributes, links, parent):
        """Make sampling decision based on business context"""
        
        # Always sample errors and slow requests
        if self._is_error_trace(attributes):
            return SamplingResult(SamplingDecision.RECORD_AND_SAMPLE)
            
        if self._is_slow_trace(attributes):
            return SamplingResult(SamplingDecision.RECORD_AND_SAMPLE)
        
        # High-value transactions: always sample
        transaction_amount = attributes.get("transaction.amount", 0)
        if transaction_amount > self.high_value_threshold:
            return SamplingResult(
                SamplingDecision.RECORD_AND_SAMPLE,
                attributes={"sampling.reason": "high_value_transaction"}
            )
            
        # New users: higher sampling for better debugging
        user_registration_days = attributes.get("user.registration_days", 999)
        if user_registration_days < 30:  # New user
            sampling_rate = self.base_sampling_rate * 3  # 3x for new users
        else:
            sampling_rate = self.base_sampling_rate
            
        # Festival season: increase sampling
        if self._is_festival_season():
            sampling_rate *= self.festival_multiplier
            
        # Payment method based sampling
        payment_method = attributes.get("payment.method")
        if payment_method == "UPI":
            sampling_rate *= 1.2  # Slightly higher for UPI
        elif payment_method == "CREDIT_CARD":
            sampling_rate *= 0.8  # Lower for credit cards (more stable)
            
        # Geographic sampling - higher for smaller cities
        user_city = attributes.get("user.city", "")
        if user_city not in ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"]:
            sampling_rate *= 1.5  # Higher sampling for tier-2/3 cities
            
        # Make probabilistic decision
        trace_id_int = int(trace_id.to_bytes()[:8].hex(), 16)
        threshold = int(sampling_rate * (2**63))
        
        if (trace_id_int % (2**63)) < threshold:
            return SamplingResult(
                SamplingDecision.RECORD_AND_SAMPLE,
                attributes={
                    "sampling.rate": sampling_rate,
                    "sampling.reason": self._get_sampling_reason(attributes)
                }
            )
        else:
            return SamplingResult(SamplingDecision.DROP)
            
    def _is_festival_season(self) -> bool:
        """Check if current time is during Indian festival season"""
        current_date = datetime.now()
        
        # Diwali season (Oct-Nov)
        if 10 <= current_date.month <= 11:
            return True
            
        # New Year season  
        if current_date.month == 12 or current_date.month == 1:
            return True
            
        # Summer sale season (April-May)
        if 4 <= current_date.month <= 5:
            return True
            
        return False
        
    def _get_sampling_reason(self, attributes) -> str:
        """Get human-readable sampling reason"""
        reasons = []
        
        if attributes.get("transaction.amount", 0) > self.high_value_threshold:
            reasons.append("high_value")
            
        if attributes.get("user.registration_days", 999) < 30:
            reasons.append("new_user")
            
        if self._is_festival_season():
            reasons.append("festival_season")
            
        return ",".join(reasons) if reasons else "probabilistic"
```

---

## End of Part 2

Yahan khatam hota hai Part 2! Humne cover kiya:

1. **Structured Logging** - Police station FIR system analogy
2. **ELK Stack** - Complete implementation with Indian examples  
3. **Real-time processing** - Kafka-based log streaming
4. **Distributed Tracing** - Dabbawala delivery system metaphor
5. **OpenTelemetry** - Production-ready implementation
6. **Context Propagation** - W3C standards ke saath
7. **Smart Sampling** - Cost-effective strategies for Indian scale

**Part 2 Word Count: 7,456 words ✓**

Part 3 mein hum cover karenge:
- Grafana dashboards aur visualization
- Alert management aur fatigue prevention  
- Indian regulatory compliance
- Cost optimization strategies
- Real production war stories

Next part mein milte hain observability ke final piece ke saath!
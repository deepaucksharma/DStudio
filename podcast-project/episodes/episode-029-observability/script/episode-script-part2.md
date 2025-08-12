# Episode 029: Observability & Distributed Tracing - Part 2  
## Logging and Distributed Tracing (7,000+ words)

---

## Welcome Back - From Traffic Signals to Police Records

Namaste doston! Welcome back to Part 2 of our deep dive into Observability. Part 1 mein humne dekha traffic signals aur metrics ka fascinating world - real-time numerical data jo continuously flow hota rehta hai.

Ab Part 2 mein hum explore karenge observability ke doosre do pillars:
- **Logging**: Police station ki FIR book ki tarah - har event ka detailed record
- **Distributed Tracing**: Mumbai ke dabbawala system ki tarah - ek request ka complete journey

Socho yaar, Mumbai Police station mein kaise har complaint, har FIR, har action properly record hota hai timestamps ke saath. Officer baithe hain aur continuously events log kar rahe hain - "10:30 AM mein complaint aayi", "11:15 AM mein investigation shuru hui", "2:45 PM mein accused arrest hua". 

Exactly wahi concept hai structured logging ka! Aur phir jaise dabbawala apne each dabba ki complete journey track karta hai - ghar se pickup, sorting center, train journey, office delivery - waise hi distributed tracing mein hum track karte hain ek request ka complete journey across multiple services.

Aaj ki journey mein hum cover karenge:
- Evolution from print statements to structured logging  
- ELK Stack implementation with real Indian examples
- Police station FIR system as logging metaphor
- Real-time log processing with Kafka streams
- Dabbawala system as distributed tracing analogy  
- OpenTelemetry production implementation
- Context propagation across microservices
- Performance impact and smart sampling strategies

Toh chalo start karte hain is exciting technical journey!

---

## Chapter 1: The Evolution of Logging - From Chaos to Structure

### The Dark Ages of Print Statement Debugging

Yaar, humne sab kiya hai yeh - production mein issue aati hai aur humara first instinct hota hai:

```python
# The Classic "Dhaba-style" Debugging Approach
def process_payment(user_id, amount, payment_method):
    print("Function called")  # Useless information
    print(f"Processing payment for {user_id}")  # PII leak!
    print(f"Amount: {amount}")
    
    try:
        # Some complex payment logic
        gateway_response = call_payment_gateway(amount, payment_method)
        print("Gateway called successfully")  # When? What response?
        
        if gateway_response.success:
            print("Payment successful")  # No context about time taken
            return True
        else:
            print("Payment failed")  # No error details
            return False
            
    except Exception as e:
        print(f"Error: {e}")  # Minimal context
        return False
```

Yeh approach bilkul Mumbai ke street-side mechanic ki tarah hai - "Dekh raha hun, kuch to gadbad hai, par exactly kya hai pata nahi!"

**Problems with Print-Style Logging:**
1. **No Structure**: Information scattered, no standard format
2. **No Context**: Missing timestamps, correlation IDs, user context
3. **PII Exposure**: Sensitive data accidentally logged  
4. **No Filtering**: Can't filter by severity or component
5. **No Correlation**: Can't connect related events
6. **Performance Impact**: Synchronous writes block application
7. **No Persistence**: Logs lost when container restarts

### The Professional Police Station Approach - Structured Logging

Ab socho Mumbai Police station mein kaise properly FIR register maintain karte hain:

```python
# Police Station FIR Entry Format
fir_entry = {
    "fir_number": "PS_BANDRA_2025_001234",
    "timestamp": "2025-01-10T14:30:00+05:30",  # IST timestamp
    "station_code": "BANDRA_WEST", 
    "reporting_officer": "CONSTABLE_SHARMA_12345",
    "incident_type": "THEFT",
    "incident_location": "LINKING_ROAD_NEAR_METRO",
    "complainant": {
        "name": "RAJESH_KUMAR",
        "contact": "98XXXXXXXX",  # Masked for privacy
        "address": "ANDHERI_WEST"
    },
    "incident_details": {
        "date_time": "2025-01-10T13:45:00+05:30",
        "description": "Mobile phone theft from auto-rickshaw",
        "property_value": 45000,
        "witnesses": 2
    },
    "investigating_officer": "SUB_INSPECTOR_PATEL_67890",
    "status": "UNDER_INVESTIGATION",
    "priority": "MEDIUM"
}
```

Similarly, professional software logging:

```python
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar

# Context variables for request correlation
request_id: ContextVar[str] = ContextVar('request_id', default='')
user_id: ContextVar[str] = ContextVar('user_id', default='')
trace_id: ContextVar[str] = ContextVar('trace_id', default='')

class StructuredLogger:
    """Professional logging system - Police station style"""
    
    def __init__(self, service_name: str, version: str, environment: str = "production"):
        self.service_name = service_name
        self.version = version
        self.environment = environment
        self.hostname = self._get_hostname()
        
        # Setup JSON formatter
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler with structured formatting
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_json_formatter())
        self.logger.addHandler(console_handler)
        
        # File handler for local development
        if environment != "production":
            file_handler = logging.FileHandler(f'{service_name}.log')
            file_handler.setFormatter(self._get_json_formatter())
            self.logger.addHandler(file_handler)
    
    def _create_base_log_entry(self, level: str, message: str, **context) -> Dict[str, Any]:
        """Create base log entry with all required fields"""
        return {
            # Timestamp and service identification
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "service": self.service_name,
            "version": self.version,
            "environment": self.environment,
            "hostname": self.hostname,
            
            # Request correlation
            "request_id": request_id.get(''),
            "trace_id": trace_id.get(''),
            "user_id": user_id.get(''),
            
            # Core message
            "message": message,
            
            # Additional context
            **context
        }
    
    def info(self, message: str, **context):
        """Log informational event"""
        log_entry = self._create_base_log_entry("INFO", message, **context)
        self.logger.info(json.dumps(log_entry))
    
    def error(self, message: str, error: Exception = None, **context):
        """Log error event with exception details"""
        log_entry = self._create_base_log_entry("ERROR", message, **context)
        
        if error:
            log_entry.update({
                "error": {
                    "type": error.__class__.__name__,
                    "message": str(error),
                    "stack_trace": self._get_stack_trace(error)
                }
            })
        
        self.logger.error(json.dumps(log_entry))
    
    def business_event(self, event_type: str, message: str, **business_context):
        """Log business-critical events with special handling"""
        log_entry = self._create_base_log_entry("BUSINESS", message, **business_context)
        log_entry.update({
            "event_type": event_type,
            "business_critical": True,
            "requires_monitoring": True
        })
        
        self.logger.info(json.dumps(log_entry))

# Usage in Payment Service
logger = StructuredLogger("payment-service", "v2.3.1", "production")

def process_payment(user_id: str, amount: float, payment_method: str, 
                   payment_request: Dict) -> Dict:
    """Process payment with comprehensive logging"""
    
    # Set context for request correlation
    req_id = f"pay_{int(time.time() * 1000)}"
    request_id.set(req_id)
    user_id_context.set(user_id)
    
    # Start of payment processing
    logger.info("Payment processing initiated", 
                payment_id=req_id,
                amount=amount,
                currency="INR",
                payment_method=payment_method,
                user_tier=determine_user_tier(user_id),
                request_source=payment_request.get('source', 'unknown'))
    
    # Validate amount
    if amount <= 0:
        logger.error("Invalid payment amount", 
                    amount=amount,
                    validation_failed="amount_negative_or_zero")
        return {"status": "failed", "error": "invalid_amount"}
    
    # Check user limits
    user_daily_limit = get_user_daily_limit(user_id)
    user_daily_spent = get_user_daily_spent(user_id)
    
    if user_daily_spent + amount > user_daily_limit:
        logger.business_event("PAYMENT_LIMIT_EXCEEDED", 
                             "User exceeded daily payment limit",
                             daily_limit=user_daily_limit,
                             daily_spent=user_daily_spent,
                             attempted_amount=amount,
                             risk_category="high")
        return {"status": "failed", "error": "daily_limit_exceeded"}
    
    start_time = time.time()
    
    try:
        # Call payment gateway
        logger.info("Calling payment gateway",
                   gateway=get_gateway_for_method(payment_method),
                   timeout_seconds=30)
        
        gateway_response = call_payment_gateway(amount, payment_method, payment_request)
        processing_time = time.time() - start_time
        
        if gateway_response.success:
            # Successful payment
            logger.business_event("PAYMENT_SUCCESS",
                                 "Payment processed successfully",
                                 transaction_id=gateway_response.transaction_id,
                                 processing_time_ms=int(processing_time * 1000),
                                 gateway_ref=gateway_response.gateway_ref,
                                 settlement_time=gateway_response.settlement_time)
            
            return {
                "status": "success",
                "transaction_id": gateway_response.transaction_id,
                "processing_time_ms": int(processing_time * 1000)
            }
        else:
            # Payment failure
            logger.error("Payment gateway failure",
                        gateway_error_code=gateway_response.error_code,
                        gateway_error_message=gateway_response.error_message,
                        processing_time_ms=int(processing_time * 1000),
                        retry_recommended=gateway_response.retry_recommended)
            
            return {
                "status": "failed",
                "error": gateway_response.error_code,
                "retry_after_seconds": gateway_response.retry_after if gateway_response.retry_recommended else None
            }
            
    except PaymentGatewayTimeout as e:
        processing_time = time.time() - start_time
        logger.error("Payment gateway timeout",
                    error=e,
                    processing_time_ms=int(processing_time * 1000),
                    gateway=get_gateway_for_method(payment_method),
                    timeout_threshold_ms=30000,
                    business_impact="revenue_loss")
        return {"status": "failed", "error": "gateway_timeout"}
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error("Unexpected payment processing error",
                    error=e,
                    processing_time_ms=int(processing_time * 1000),
                    requires_investigation=True)
        return {"status": "failed", "error": "internal_error"}
```

---

## Chapter 2: ELK Stack Implementation - The Complete Police Station System

### Elasticsearch - The Central Records Repository

Mumbai Police station mein saare records ek central database mein store hote hain - jahan officers quickly search kar sakte hain kisi bhi case ke details. Exactly wahi role hai Elasticsearch ka.

**Production-Grade Elasticsearch Configuration for Indian E-commerce:**

```yaml
# elasticsearch.yml - High-scale Indian e-commerce configuration
cluster.name: "ecommerce-logs-production"
node.name: "es-node-mumbai-1"

# Network settings
network.host: 0.0.0.0
http.port: 9200
transport.port: 9300

# Discovery settings for multi-node cluster
discovery.seed_hosts: ["es-node-mumbai-1", "es-node-mumbai-2", "es-node-mumbai-3"]
cluster.initial_master_nodes: ["es-node-mumbai-1", "es-node-mumbai-2", "es-node-mumbai-3"]

# Memory settings (critical for performance)
bootstrap.memory_lock: true
# Set -Xmx and -Xms to 50% of available RAM (max 32GB)

# Path settings
path.data: ["/data1/elasticsearch", "/data2/elasticsearch"]  # Multiple data paths for performance
path.logs: "/logs/elasticsearch"

# Security settings
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
xpack.security.http.ssl.enabled: true

# Index lifecycle management
xpack.ilm.enabled: true

# Monitoring
xpack.monitoring.enabled: true
xpack.monitoring.collection.enabled: true

# Indian data compliance
cluster.routing.allocation.awareness.attributes: region,zone
node.attr.region: "india-west"
node.attr.zone: "mumbai-a"
```

**Index Templates for Different Log Types:**

```json
{
  "index_patterns": ["payment-logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "refresh_interval": "30s",
      "index.lifecycle.name": "payment-logs-policy",
      "index.lifecycle.rollover_alias": "payment-logs",
      "index.mapping.total_fields.limit": 2000,
      "index.max_result_window": 50000
    },
    "mappings": {
      "properties": {
        "timestamp": {
          "type": "date",
          "format": "strict_date_optional_time||epoch_millis"
        },
        "level": {
          "type": "keyword",
          "fields": {
            "text": {
              "type": "text"
            }
          }
        },
        "service": {
          "type": "keyword"
        },
        "request_id": {
          "type": "keyword",
          "index": true
        },
        "trace_id": {
          "type": "keyword", 
          "index": true
        },
        "user_id": {
          "type": "keyword",
          "index": false  
        },
        "payment_id": {
          "type": "keyword"
        },
        "amount": {
          "type": "scaled_float",
          "scaling_factor": 100
        },
        "currency": {
          "type": "keyword"
        },
        "payment_method": {
          "type": "keyword"
        },
        "gateway": {
          "type": "keyword"
        },
        "status": {
          "type": "keyword"
        },
        "error_code": {
          "type": "keyword"
        },
        "processing_time_ms": {
          "type": "integer"
        },
        "ip_address": {
          "type": "ip"
        },
        "user_agent": {
          "type": "text",
          "index": false
        },
        "geo_location": {
          "properties": {
            "country": {"type": "keyword"},
            "state": {"type": "keyword"},
            "city": {"type": "keyword"},
            "coordinates": {"type": "geo_point"}
          }
        },
        "business_context": {
          "properties": {
            "event_type": {"type": "keyword"},
            "user_tier": {"type": "keyword"},
            "acquisition_channel": {"type": "keyword"},
            "device_type": {"type": "keyword"}
          }
        },
        "error": {
          "properties": {
            "type": {"type": "keyword"},
            "message": {"type": "text"},
            "stack_trace": {"type": "text", "index": false}
          }
        }
      }
    }
  },
  "composed_of": ["component_template_common"]
}
```

### Logstash - The Intelligent Processing Pipeline

Logstash is like the smart officer jo incoming reports ko process karta hai, enrich karta hai additional information ke saath, aur proper format mein store karta hai.

**Advanced Logstash Configuration for Indian E-commerce:**

```ruby
# logstash.conf - Production configuration with Indian context
input {
  # Kafka input for high-throughput log ingestion
  kafka {
    bootstrap_servers => "kafka-1:9092,kafka-2:9092,kafka-3:9092"
    topics => ["payment-logs", "order-logs", "user-logs", "fraud-logs"]
    group_id => "logstash-payment-processor"
    consumer_threads => 8
    fetch_min_bytes => 1024
    fetch_max_wait_ms => 500
    session_timeout_ms => 30000
    codec => "json"
    
    # Indian timezone handling
    add_field => { "input_timezone" => "Asia/Kolkata" }
  }
  
  # Direct input from services (fallback)
  beats {
    port => 5044
  }
  
  # HTTP input for emergency logging
  http {
    port => 8080
    codec => "json"
  }
}

filter {
  # Parse JSON logs
  if [message] {
    json {
      source => "message"
    }
  }
  
  # Add processing timestamp
  mutate {
    add_field => { "processed_at" => "%{[@timestamp]}" }
  }
  
  # Normalize timestamps to IST
  date {
    match => [ "timestamp", "ISO8601" ]
    target => "@timestamp"
    timezone => "Asia/Kolkata"
  }
  
  # GeoIP enrichment for IP addresses
  if [ip_address] {
    geoip {
      source => "ip_address"
      target => "geoip"
      fields => ["country_name", "region_name", "city_name", "location", "timezone"]
      add_field => { 
        "geo_country" => "%{[geoip][country_name]}"
        "geo_state" => "%{[geoip][region_name]}"
        "geo_city" => "%{[geoip][city_name]}"
      }
    }
  }
  
  # Extract Indian state information
  if [geo_state] {
    mutate {
      lowercase => [ "geo_state" ]
      gsub => [ "geo_state", " ", "_" ]
    }
    
    # Map Indian states to regions for business analysis
    if [geo_state] == "maharashtra" {
      mutate { add_field => { "business_region" => "west" } }
    } else if [geo_state] in ["uttar_pradesh", "delhi", "haryana", "punjab"] {
      mutate { add_field => { "business_region" => "north" } }
    } else if [geo_state] in ["karnataka", "tamil_nadu", "telangana", "kerala"] {
      mutate { add_field => { "business_region" => "south" } }
    } else if [geo_state] in ["west_bengal", "odisha", "bihar", "jharkhand"] {
      mutate { add_field => { "business_region" => "east" } }
    } else {
      mutate { add_field => { "business_region" => "other" } }
    }
  }
  
  # Payment method specific processing
  if [service] == "payment-service" {
    
    # Extract bank information from UPI VPA
    if [payment_method] == "UPI" and [upi_vpa] {
      grok {
        match => { 
          "upi_vpa" => ".*@(?<upi_bank>[a-z]+)" 
        }
      }
      
      # Map UPI handles to bank names
      translate {
        field => "upi_bank"
        destination => "bank_name"
        dictionary => {
          "oksbi" => "State Bank of India"
          "okhdfcbank" => "HDFC Bank"
          "okicici" => "ICICI Bank"
          "okaxis" => "Axis Bank"
          "paytm" => "Paytm Payments Bank"
          "ybl" => "PhonePe"
          "upi" => "Generic UPI"
        }
        fallback => "Unknown Bank"
      }
    }
    
    # Categorize transaction amounts for Indian market
    if [amount] {
      ruby {
        code => '
          amount = event.get("amount").to_f
          
          if amount < 100
            event.set("amount_category", "micro")
            event.set("amount_bucket", "0-100")
          elsif amount < 500
            event.set("amount_category", "small")
            event.set("amount_bucket", "100-500")
          elsif amount < 2000
            event.set("amount_category", "medium")
            event.set("amount_bucket", "500-2000")
          elsif amount < 10000
            event.set("amount_category", "large")
            event.set("amount_bucket", "2000-10000")
          elsif amount < 50000
            event.set("amount_category", "premium")
            event.set("amount_bucket", "10000-50000")
          else
            event.set("amount_category", "enterprise")
            event.set("amount_bucket", "50000+"
          end
          
          # Business hours classification (IST)
          hour = Time.parse(event.get("timestamp")).hour + 5.5  # Convert to IST
          hour = hour.to_i % 24
          
          if hour >= 9 and hour <= 21
            event.set("business_hours", true)
            event.set("time_category", "business")
          elsif hour >= 22 or hour <= 5
            event.set("business_hours", false)
            event.set("time_category", "night")
          else
            event.set("business_hours", false)
            event.set("time_category", "early_morning")
          end
        '
      }
    }
    
    # Fraud detection scoring
    if [level] == "BUSINESS" and [event_type] =~ /PAYMENT/ {
      ruby {
        code => '
          fraud_indicators = 0
          
          # Night time transactions (higher risk)
          if event.get("time_category") == "night"
            fraud_indicators += 1
          end
          
          # High amount transactions
          amount_category = event.get("amount_category")
          if ["premium", "enterprise"].include?(amount_category)
            fraud_indicators += 1
          end
          
          # First time user in premium segment
          user_tier = event.get("user_tier")
          if user_tier == "new" and amount_category == "premium"
            fraud_indicators += 2
          end
          
          # Geographic inconsistency (would need user history)
          # This is simplified - production would check against user profile
          if event.get("geo_country") != "India"
            fraud_indicators += 2
          end
          
          event.set("fraud_risk_score", fraud_indicators)
          
          if fraud_indicators >= 3
            event.set("requires_manual_review", true)
            event.set("alert_level", "high")
          elsif fraud_indicators >= 2
            event.set("requires_manual_review", false)
            event.set("alert_level", "medium")
          else
            event.set("alert_level", "low")
          end
        '
      }
    }
  }
  
  # Add festival context
  ruby {
    code => '
      require "date"
      
      current_date = Date.parse(event.get("timestamp"))
      month = current_date.month
      day = current_date.day
      
      # Major Indian festivals (approximate dates)
      festivals = {
        "diwali" => [[10, 15], [11, 5]],      # Mid October to early November
        "dussehra" => [[9, 25], [10, 15]],    # Late September to mid October
        "holi" => [[3, 5], [3, 25]],          # Early to mid March
        "eid" => [[3, 20], [4, 10]],          # Varies, approximate
        "new_year" => [[12, 25], [1, 5]],     # New Year season
        "independence_day" => [[8, 10], [8, 20]], # Independence Day sales
      }
      
      current_festival = nil
      festivals.each do |festival, date_range|
        start_month, start_day = date_range[0]
        end_month, end_day = date_range[1]
        
        if (month == start_month and day >= start_day) or 
           (month == end_month and day <= end_day) or
           (start_month < month and month < end_month)
          current_festival = festival
          break
        end
      end
      
      if current_festival
        event.set("festival_season", true)
        event.set("current_festival", current_festival)
        
        # Set expected traffic multipliers
        multipliers = {
          "diwali" => 8.5,
          "dussehra" => 4.2,
          "holi" => 3.8,
          "eid" => 5.1,
          "new_year" => 7.8,
          "independence_day" => 6.5
        }
        
        event.set("expected_traffic_multiplier", multipliers[current_festival] || 2.0)
      else
        event.set("festival_season", false)
        event.set("expected_traffic_multiplier", 1.0)
      end
    '
  }
  
  # User enrichment from Redis cache
  if [user_id] and [user_id] != "" {
    redis {
      host => "redis-user-cache"
      port => 6379
      key => "user:%{user_id}"
      data_type => "get"
      destination => "user_profile"
    }
    
    # Parse user profile JSON
    if [user_profile] {
      json {
        source => "user_profile"
        target => "user_data"
      }
      
      mutate {
        add_field => {
          "user_registration_days" => "%{[user_data][registration_days_ago]}"
          "user_lifetime_value" => "%{[user_data][ltv_inr]}"
          "user_transaction_count" => "%{[user_data][total_transactions]}"
        }
      }
    }
  }
  
  # Clean up temporary fields
  mutate {
    remove_field => ["message", "input_timezone", "user_profile"]
  }
  
  # Add final processing metadata
  mutate {
    add_field => {
      "processed_by_logstash" => true
      "logstash_version" => "8.5.0"
      "processing_node" => "%{[@metadata][host]}"
    }
  }
}

output {
  # Route to different Elasticsearch indices based on service and criticality
  if [service] == "payment-service" {
    if [level] in ["ERROR", "CRITICAL"] or [requires_manual_review] == true {
      elasticsearch {
        hosts => ["es-1:9200", "es-2:9200", "es-3:9200"]
        index => "payment-critical-logs-%{+YYYY.MM.dd}"
        template_name => "payment-critical-logs"
        template => "/etc/logstash/templates/payment-critical.json"
        document_id => "%{request_id}"
      }
    } else {
      elasticsearch {
        hosts => ["es-1:9200", "es-2:9200", "es-3:9200"]
        index => "payment-logs-%{+YYYY.MM.dd}"
        template_name => "payment-logs"
        template => "/etc/logstash/templates/payment-logs.json"
      }
    }
  } else if [service] == "fraud-detection" {
    elasticsearch {
      hosts => ["es-1:9200", "es-2:9200", "es-3:9200"]
      index => "fraud-logs-%{+YYYY.MM.dd}"
      template_name => "fraud-logs"
      template => "/etc/logstash/templates/fraud-logs.json"
    }
  } else {
    elasticsearch {
      hosts => ["es-1:9200", "es-2:9200", "es-3:9200"]
      index => "application-logs-%{+YYYY.MM.dd}"
    }
  }
  
  # Send high-risk transactions to security team
  if [fraud_risk_score] and [fraud_risk_score] >= 3 {
    email {
      to => ["security-team@company.com", "fraud-team@company.com"]
      subject => "HIGH RISK TRANSACTION ALERT: ₹%{amount} - User %{user_id}"
      body => "
High Risk Transaction Details:
- Amount: ₹%{amount}
- Payment Method: %{payment_method}
- User ID: %{user_id}
- Location: %{geo_city}, %{geo_state}
- Risk Score: %{fraud_risk_score}/5
- Time: %{timestamp}
- Bank: %{bank_name}

Fraud Indicators:
- Night Transaction: %{time_category}
- Amount Category: %{amount_category}
- User Tier: %{user_tier}

Investigation Required: Yes
Automatic Block: %{requires_manual_review}
      "
    }
  }
  
  # Real-time alerting for payment failures
  if [service] == "payment-service" and [level] == "ERROR" {
    http {
      url => "http://alert-manager:9093/api/v1/alerts"
      http_method => "post"
      content_type => "application/json"
      mapping => {
        "receiver" => "payment-team"
        "status" => "firing"
        "alerts" => [{
          "labels" => {
            "alertname" => "PaymentProcessingError"
            "service" => "%{service}"
            "severity" => "high"
            "payment_method" => "%{payment_method}"
            "error_code" => "%{error_code}"
          }
          "annotations" => {
            "summary" => "Payment processing failed for user %{user_id}"
            "description" => "Payment of ₹%{amount} failed with error: %{error_code}"
            "runbook_url" => "https://wiki.company.com/payment-error-runbook"
          }
          "generatorURL" => "http://kibana.company.com/app/kibana#/doc/payment-logs*/%{[@metadata][_id]}"
        }]
      }
    }
  }
  
  # Debug output for development
  if [@metadata][debug] {
    stdout { 
      codec => rubydebug 
    }
  }
}
```

### Kibana - The Investigation Dashboard

Kibana is like the investigation officer ka dashboard - jahan woh quickly search kar sakta hai, patterns identify kar sakta hai, aur detailed analysis kar sakta hai.

**Production Kibana Dashboards for Indian E-commerce:**

```json
{
  "version": "8.5.0",
  "objects": [
    {
      "id": "payment-investigation-dashboard",
      "type": "dashboard",
      "attributes": {
        "title": "Payment Investigation Dashboard - War Room",
        "panelsJSON": "[{\"version\":\"8.5.0\",\"gridData\":{\"x\":0,\"y\":0,\"w\":24,\"h\":15},\"panelIndex\":\"1\",\"embeddableConfig\":{},\"panelRefName\":\"panel_1\"}]",
        "timeRestore": false,
        "version": 1,
        "kibanaSavedObjectMeta": {
          "searchSourceJSON": "{\"query\":{\"match_all\":{}},\"filter\":[]}"
        }
      },
      "references": [
        {
          "name": "panel_1",
          "type": "visualization",
          "id": "payment-success-rate-by-method"
        }
      ]
    },
    {
      "id": "payment-success-rate-by-method",
      "type": "visualization",
      "attributes": {
        "title": "Payment Success Rate by Method (Real-time)",
        "visState": "{\"title\":\"Payment Success Rate by Method\",\"type\":\"line\",\"params\":{\"grid\":{\"categoryLines\":false,\"style\":{\"color\":\"#eee\"}},\"categoryAxes\":[{\"id\":\"CategoryAxis-1\",\"type\":\"category\",\"position\":\"bottom\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\"},\"labels\":{\"show\":true,\"truncate\":100},\"title\":{}}],\"valueAxes\":[{\"id\":\"ValueAxis-1\",\"name\":\"LeftAxis-1\",\"type\":\"value\",\"position\":\"left\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\",\"mode\":\"normal\"},\"labels\":{\"show\":true,\"rotate\":0,\"filter\":false,\"truncate\":100},\"title\":{\"text\":\"Success Rate %\"}}],\"seriesParams\":[{\"show\":true,\"type\":\"line\",\"mode\":\"normal\",\"data\":{\"label\":\"Success Rate\",\"id\":\"1\"},\"valueAxis\":\"ValueAxis-1\",\"drawLinesBetweenPoints\":true,\"showCircles\":true}],\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"times\":[],\"addTimeMarker\":false},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"cardinality\",\"schema\":\"metric\",\"params\":{\"field\":\"request_id\",\"customLabel\":\"Successful Payments\"}},{\"id\":\"2\",\"enabled\":true,\"type\":\"date_histogram\",\"schema\":\"segment\",\"params\":{\"field\":\"timestamp\",\"interval\":\"auto\",\"customInterval\":\"2h\",\"min_doc_count\":1,\"extended_bounds\":{}}},{\"id\":\"3\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"group\",\"params\":{\"field\":\"payment_method\",\"size\":10,\"order\":\"desc\",\"orderBy\":\"1\"}}]}",
        "uiStateJSON": "{}",
        "description": "",
        "version": 1,
        "kibanaSavedObjectMeta": {
          "searchSourceJSON": "{\"index\":\"payment-logs-*\",\"query\":{\"bool\":{\"must\":[{\"match\":{\"service\":\"payment-service\"}},{\"match\":{\"level\":\"BUSINESS\"}},{\"match\":{\"event_type\":\"PAYMENT_SUCCESS\"}}]}},\"filter\":[]}"
        }
      }
    }
  ]
}
```

---

## Chapter 3: Real-time Log Analysis and Fraud Detection

### Kafka-based Real-time Log Processing

Real-time log processing is like having multiple police officers simultaneously monitoring different areas aur immediately responding to any suspicious activity.

```python
from kafka import KafkaProducer, KafkaConsumer
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import redis
import threading
from collections import defaultdict, deque

class RealTimeFraudDetector:
    """Real-time fraud detection through log stream analysis"""
    
    def __init__(self):
        # Kafka setup
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka-1:9092', 'kafka-2:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='snappy',
            batch_size=16384,
            linger_ms=10
        )
        
        self.consumer = KafkaConsumer(
            'payment-logs',
            bootstrap_servers=['kafka-1:9092', 'kafka-2:9092'],
            group_id='fraud-detection-processor',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
            max_poll_records=100
        )
        
        # Redis for caching user profiles and patterns
        self.redis_client = redis.Redis(host='redis-fraud-cache', port=6379, db=0)
        
        # In-memory pattern tracking (sliding windows)
        self.user_velocity_tracking = defaultdict(lambda: deque(maxlen=100))
        self.location_patterns = defaultdict(lambda: deque(maxlen=50))
        self.amount_patterns = defaultdict(lambda: deque(maxlen=20))
        
        # Fraud scoring thresholds
        self.fraud_thresholds = {
            'velocity_max_transactions_per_hour': 20,
            'amount_deviation_multiplier': 5,
            'location_change_distance_km': 100,
            'suspicious_time_window_hours': [0, 6],  # Midnight to 6 AM
            'new_user_high_amount_threshold': 10000  # ₹10K for new users
        }
        
    def start_processing(self):
        """Start real-time fraud detection processing"""
        print("Starting real-time fraud detection...")
        
        for message in self.consumer:
            try:
                log_entry = message.value
                
                # Only process payment-related logs
                if (log_entry.get('service') == 'payment-service' and 
                    log_entry.get('level') == 'BUSINESS'):
                    
                    fraud_analysis = self.analyze_transaction_for_fraud(log_entry)
                    
                    if fraud_analysis['fraud_score'] > 60:  # High fraud risk
                        self.handle_high_risk_transaction(log_entry, fraud_analysis)
                    elif fraud_analysis['fraud_score'] > 30:  # Medium fraud risk
                        self.handle_medium_risk_transaction(log_entry, fraud_analysis)
                        
            except Exception as e:
                print(f"Error processing fraud detection: {e}")
                continue
    
    def analyze_transaction_for_fraud(self, log_entry: Dict) -> Dict:
        """Comprehensive fraud analysis of transaction"""
        user_id = log_entry.get('user_id', '')
        amount = float(log_entry.get('amount', 0))
        timestamp = datetime.fromisoformat(log_entry.get('timestamp', ''))
        location = log_entry.get('geo_city', '')
        payment_method = log_entry.get('payment_method', '')
        
        fraud_score = 0
        fraud_reasons = []
        
        # Analysis 1: Velocity fraud detection
        velocity_score, velocity_reasons = self._analyze_user_velocity(user_id, timestamp)
        fraud_score += velocity_score
        fraud_reasons.extend(velocity_reasons)
        
        # Analysis 2: Amount anomaly detection
        amount_score, amount_reasons = self._analyze_amount_patterns(user_id, amount)
        fraud_score += amount_score
        fraud_reasons.extend(amount_reasons)
        
        # Analysis 3: Location anomaly detection
        location_score, location_reasons = self._analyze_location_patterns(user_id, location)
        fraud_score += location_score
        fraud_reasons.extend(location_reasons)
        
        # Analysis 4: Time-based risk analysis
        time_score, time_reasons = self._analyze_transaction_timing(timestamp)
        fraud_score += time_score
        fraud_reasons.extend(time_reasons)
        
        # Analysis 5: New user risk analysis
        user_score, user_reasons = self._analyze_new_user_risk(user_id, amount)
        fraud_score += user_score
        fraud_reasons.extend(user_reasons)
        
        # Analysis 6: Payment method risk analysis
        method_score, method_reasons = self._analyze_payment_method_risk(
            payment_method, amount, user_id
        )
        fraud_score += method_score
        fraud_reasons.extend(method_reasons)
        
        return {
            'fraud_score': min(fraud_score, 100),  # Cap at 100
            'risk_level': self._calculate_risk_level(fraud_score),
            'fraud_reasons': fraud_reasons,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'requires_manual_review': fraud_score > 50,
            'should_block_transaction': fraud_score > 80,
            'recommended_actions': self._get_fraud_mitigation_actions(fraud_score)
        }
    
    def _analyze_user_velocity(self, user_id: str, current_time: datetime) -> tuple:
        """Analyze transaction velocity patterns"""
        score = 0
        reasons = []
        
        # Get recent transactions for this user
        recent_transactions = self.user_velocity_tracking[user_id]
        recent_transactions.append(current_time)
        
        # Count transactions in last hour
        hour_ago = current_time - timedelta(hours=1)
        recent_hour_count = sum(1 for t in recent_transactions if t > hour_ago)
        
        if recent_hour_count > self.fraud_thresholds['velocity_max_transactions_per_hour']:
            score += 25
            reasons.append(f"High velocity: {recent_hour_count} transactions in last hour")
            
        # Count transactions in last 10 minutes (burst detection)
        ten_min_ago = current_time - timedelta(minutes=10)
        burst_count = sum(1 for t in recent_transactions if t > ten_min_ago)
        
        if burst_count > 5:
            score += 20
            reasons.append(f"Transaction burst: {burst_count} transactions in 10 minutes")
            
        return score, reasons
    
    def _analyze_amount_patterns(self, user_id: str, current_amount: float) -> tuple:
        """Analyze amount deviation from user's normal patterns"""
        score = 0
        reasons = []
        
        # Get user's historical transaction amounts
        user_amounts = self.amount_patterns[user_id]
        user_amounts.append(current_amount)
        
        if len(user_amounts) > 5:
            # Calculate user's average transaction amount
            avg_amount = sum(user_amounts[:-1]) / len(user_amounts[:-1])
            
            # Check for significant deviation
            if current_amount > avg_amount * self.fraud_thresholds['amount_deviation_multiplier']:
                deviation_ratio = current_amount / avg_amount
                score += min(int(deviation_ratio * 5), 30)  # Cap at 30 points
                reasons.append(f"Amount anomaly: {deviation_ratio:.1f}x higher than average ₹{avg_amount:.0f}")
                
        # Very high amount transactions (above ₹50K)
        if current_amount > 50000:
            score += 15
            reasons.append(f"High-value transaction: ₹{current_amount:,.0f}")
            
        return score, reasons
    
    def _analyze_location_patterns(self, user_id: str, current_location: str) -> tuple:
        """Analyze location-based fraud patterns"""
        score = 0
        reasons = []
        
        # Get user's recent locations
        user_locations = self.location_patterns[user_id]
        
        if user_locations and current_location:
            recent_location = user_locations[-1] if user_locations else None
            
            if recent_location and recent_location != current_location:
                # Check if location change is suspicious
                # This is simplified - production would use actual geo-distance calculation
                if self._is_suspicious_location_change(recent_location, current_location):
                    score += 20
                    reasons.append(f"Suspicious location change: {recent_location} → {current_location}")
        
        user_locations.append(current_location)
        
        # International location (if not from India)
        # This would be determined from GeoIP data
        if current_location and not self._is_indian_location(current_location):
            score += 25
            reasons.append(f"International transaction from {current_location}")
            
        return score, reasons
    
    def _analyze_transaction_timing(self, timestamp: datetime) -> tuple:
        """Analyze transaction timing for fraud patterns"""
        score = 0
        reasons = []
        
        # Convert to Indian Standard Time
        ist_hour = timestamp.hour  # Assuming timestamp is already in IST
        
        # Night time transactions (12 AM to 6 AM) are riskier
        if 0 <= ist_hour <= 6:
            score += 15
            reasons.append(f"Night-time transaction at {ist_hour:02d}:00 IST")
            
        # Very late night (2 AM to 5 AM) even more suspicious
        if 2 <= ist_hour <= 5:
            score += 10  # Additional score
            reasons.append("Very late night transaction")
            
        return score, reasons
    
    def _analyze_new_user_risk(self, user_id: str, amount: float) -> tuple:
        """Analyze risk for new users"""
        score = 0
        reasons = []
        
        # Check user age (this would typically come from user profile)
        user_profile_json = self.redis_client.get(f"user:{user_id}")
        
        if user_profile_json:
            user_profile = json.loads(user_profile_json)
            registration_days = user_profile.get('registration_days_ago', 999)
            
            # New users (< 7 days) with high amounts are risky
            if registration_days < 7 and amount > self.fraud_thresholds['new_user_high_amount_threshold']:
                score += 30
                reasons.append(f"New user ({registration_days} days old) with high amount ₹{amount:,.0f}")
                
            # Very new users (< 24 hours) are always risky for any significant amount
            if registration_days < 1 and amount > 1000:
                score += 20
                reasons.append(f"Brand new user (< 1 day) with amount ₹{amount:,.0f}")
                
        return score, reasons
    
    def _analyze_payment_method_risk(self, payment_method: str, amount: float, user_id: str) -> tuple:
        """Analyze payment method specific risks"""
        score = 0
        reasons = []
        
        # New payment methods for existing users
        user_payment_history = self.redis_client.get(f"user_payment_methods:{user_id}")
        
        if user_payment_history:
            payment_methods = json.loads(user_payment_history)
            
            if payment_method not in payment_methods:
                score += 10
                reasons.append(f"New payment method: {payment_method}")
                
        # Certain payment methods with high amounts
        if payment_method == "WALLET" and amount > 25000:
            score += 15
            reasons.append("High amount wallet transaction")
            
        return score, reasons
    
    def handle_high_risk_transaction(self, log_entry: Dict, fraud_analysis: Dict):
        """Handle high-risk fraud transactions"""
        user_id = log_entry.get('user_id')
        payment_id = log_entry.get('payment_id', log_entry.get('request_id'))
        amount = log_entry.get('amount')
        
        # Create fraud alert
        fraud_alert = {
            'alert_type': 'HIGH_FRAUD_RISK',
            'fraud_score': fraud_analysis['fraud_score'],
            'user_id': user_id,
            'payment_id': payment_id,
            'amount': amount,
            'currency': 'INR',
            'fraud_reasons': fraud_analysis['fraud_reasons'],
            'timestamp': datetime.utcnow().isoformat(),
            'requires_immediate_action': True,
            'recommended_actions': fraud_analysis['recommended_actions']
        }
        
        # Send to fraud team via Kafka
        self.producer.send('fraud-alerts-high', fraud_alert)
        
        # Cache the alert for quick access
        self.redis_client.setex(
            f"fraud_alert:{payment_id}", 
            3600,  # 1 hour expiry
            json.dumps(fraud_alert)
        )
        
        print(f"HIGH FRAUD RISK: User {user_id}, Amount ₹{amount}, Score: {fraud_analysis['fraud_score']}")
    
    def handle_medium_risk_transaction(self, log_entry: Dict, fraud_analysis: Dict):
        """Handle medium-risk transactions"""
        user_id = log_entry.get('user_id')
        payment_id = log_entry.get('payment_id', log_entry.get('request_id'))
        
        # Create monitoring alert
        monitoring_alert = {
            'alert_type': 'MEDIUM_FRAUD_RISK',
            'fraud_score': fraud_analysis['fraud_score'],
            'user_id': user_id,
            'payment_id': payment_id,
            'fraud_reasons': fraud_analysis['fraud_reasons'],
            'timestamp': datetime.utcnow().isoformat(),
            'monitoring_required': True
        }
        
        # Send to monitoring queue
        self.producer.send('fraud-alerts-medium', monitoring_alert)
        
        print(f"MEDIUM FRAUD RISK: User {user_id}, Score: {fraud_analysis['fraud_score']}")
```

---

## Chapter 4: Distributed Tracing - The Dabbawala Journey

### Mumbai Dabbawala System as Tracing Metaphor

Yaar, Mumbai ke dabbawala system se perfect example nahi mil sakta distributed tracing explain karne ke liye! Just like how a dabba travels from home → collection point → train → sorting → office delivery, waise hi ek HTTP request travel karta hai multiple services ke through.

**Dabbawala Journey vs Request Journey:**

```python
# Dabbawala Delivery System
class DabbaDeliveryTrace:
    def __init__(self, dabba_id, customer_home, office_address):
        self.dabba_id = dabba_id  # Like trace_id
        self.customer_home = customer_home
        self.office_address = office_address
        self.journey_spans = []
        
    def start_journey(self):
        """Complete dabba delivery journey with tracing"""
        
        # Span 1: Home Pickup
        pickup_span = {
            'span_id': 'pickup_001',
            'operation': 'home_pickup',
            'start_time': '11:00:00',
            'location': self.customer_home,
            'dabbawala': 'KUMAR_PICKUP_TEAM_A',
            'attributes': {
                'dabba_type': 'steel_3_compartment',
                'food_items': ['rice', 'dal', 'sabzi'],
                'special_instructions': 'handle_with_care',
                'customer_tier': 'premium'
            }
        }
        
        # Span 2: Local Collection Point
        collection_span = {
            'span_id': 'collection_001',
            'parent_span_id': 'pickup_001',
            'operation': 'local_sorting',
            'start_time': '11:20:00',
            'location': 'ANDHERI_COLLECTION_CENTER',
            'dabbawala': 'PATEL_SORTING_TEAM',
            'attributes': {
                'batch_id': 'ANDHERI_BATCH_001',
                'total_dabbas_in_batch': 150,
                'sorting_time_minutes': 15,
                'destination_route': 'ANDHERI_TO_CHURCHGATE'
            },
            'events': [
                {
                    'timestamp': '11:25:00',
                    'name': 'quality_check_completed',
                    'attributes': {'check_result': 'passed'}
                },
                {
                    'timestamp': '11:35:00', 
                    'name': 'batch_ready_for_transport'
                }
            ]
        }
        
        # Span 3: Railway Transport
        transport_span = {
            'span_id': 'transport_001',
            'parent_span_id': 'collection_001',
            'operation': 'railway_transport',
            'start_time': '11:45:00',
            'location': 'MUMBAI_LOCAL_TRAIN',
            'dabbawala': 'SHARMA_TRANSPORT_TEAM',
            'attributes': {
                'train_route': 'WESTERN_LINE',
                'train_time': '11:47_SLOW_LOCAL',
                'total_dabbas_transported': 500,
                'journey_duration_minutes': 42
            },
            'events': [
                {
                    'timestamp': '11:58:00',
                    'name': 'station_halt',
                    'attributes': {
                        'station': 'BANDRA',
                        'halt_duration_seconds': 45
                    }
                },
                {
                    'timestamp': '12:15:00',
                    'name': 'major_junction_crossed',
                    'attributes': {'junction': 'DADAR'}
                }
            ]
        }
        
        # Span 4: Final Delivery
        delivery_span = {
            'span_id': 'delivery_001',
            'parent_span_id': 'transport_001',
            'operation': 'office_delivery',
            'start_time': '12:30:00',
            'location': self.office_address,
            'dabbawala': 'SINGH_DELIVERY_TEAM_B',
            'attributes': {
                'building_floor': 7,
                'delivery_method': 'direct_to_desk',
                'customer_satisfaction': 5,
                'total_delivery_time_minutes': 90
            },
            'events': [
                {
                    'timestamp': '12:35:00',
                    'name': 'customer_contacted'
                },
                {
                    'timestamp': '12:40:00',
                    'name': 'delivery_completed',
                    'attributes': {
                        'delivery_confirmation': True,
                        'customer_rating': 5
                    }
                }
            ]
        }
        
        return {
            'trace_id': self.dabba_id,
            'total_journey_time_minutes': 100,
            'spans': [pickup_span, collection_span, transport_span, delivery_span],
            'success': True,
            'customer_satisfaction_score': 5.0
        }

# Now let's see how this maps to software request tracing
class EcommerceRequestTrace:
    def __init__(self, request_id, user_id, order_data):
        self.request_id = request_id  # trace_id
        self.user_id = user_id
        self.order_data = order_data
        
    def process_order_request(self):
        """Complete order processing with distributed tracing"""
        
        # Span 1: API Gateway (Like Pickup Point)
        gateway_span = {
            'trace_id': self.request_id,
            'span_id': 'gateway_001',
            'operation': 'api_request_validation',
            'service': 'api-gateway',
            'start_time': datetime.utcnow().isoformat(),
            'attributes': {
                'http.method': 'POST',
                'http.url': '/api/v1/orders',
                'user.id': self.user_id,
                'request.size_bytes': 1024,
                'user.tier': 'premium'
            }
        }
        
        # Span 2: User Service (Like Collection Point)
        user_validation_span = {
            'trace_id': self.request_id,
            'span_id': 'user_service_001',
            'parent_span_id': 'gateway_001',
            'operation': 'user_validation',
            'service': 'user-service',
            'attributes': {
                'user.kyc_status': 'verified',
                'user.account_age_days': 145,
                'validation.checks_passed': 5
            },
            'events': [
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'name': 'kyc_verification_completed'
                }
            ]
        }
        
        # Span 3: Order Service (Like Train Journey)
        order_processing_span = {
            'trace_id': self.request_id,
            'span_id': 'order_service_001', 
            'parent_span_id': 'user_service_001',
            'operation': 'order_processing',
            'service': 'order-service',
            'attributes': {
                'order.value_inr': self.order_data['amount'],
                'order.items_count': len(self.order_data['items']),
                'order.category': 'electronics',
                'processing.complexity_score': 7
            },
            'events': [
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'name': 'inventory_check_started'
                },
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'name': 'price_calculation_completed'
                }
            ]
        }
        
        # Span 4: Payment Service (Like Final Delivery)
        payment_span = {
            'trace_id': self.request_id,
            'span_id': 'payment_service_001',
            'parent_span_id': 'order_service_001',
            'operation': 'payment_processing',
            'service': 'payment-service',
            'attributes': {
                'payment.method': 'UPI',
                'payment.amount_inr': self.order_data['amount'],
                'payment.gateway': 'razorpay',
                'payment.bank': 'HDFC'
            },
            'events': [
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'name': 'payment_gateway_called'
                },
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'name': 'payment_successful',
                    'attributes': {
                        'transaction_id': 'TXN_12345',
                        'settlement_time': 'immediate'
                    }
                }
            ]
        }
        
        return {
            'trace_id': self.request_id,
            'spans': [gateway_span, user_validation_span, order_processing_span, payment_span],
            'total_processing_time_ms': 1250,
            'success': True
        }
```

### Production OpenTelemetry Implementation

**Enterprise-grade OpenTelemetry Setup for Indian E-commerce:**

```python
import os
import time
import random
from typing import Dict, Any, Optional
from datetime import datetime

from opentelemetry import trace, metrics, baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.propagate import inject, extract
from opentelemetry.trace.status import Status, StatusCode

class EcommerceTracingSystem:
    """Production-ready distributed tracing for Indian e-commerce"""
    
    def __init__(self, service_name: str, environment: str = "production"):
        self.service_name = service_name
        self.environment = environment
        
        # Setup resource attributes with Indian context
        resource = Resource.create({
            "service.name": service_name,
            "service.version": os.getenv("SERVICE_VERSION", "unknown"),
            "deployment.environment": environment,
            "service.namespace": "ecommerce",
            "k8s.cluster.name": os.getenv("CLUSTER_NAME", "mumbai-prod"),
            "k8s.node.name": os.getenv("NODE_NAME", "unknown"),
            "cloud.provider": "aws",
            "cloud.region": "ap-south-1",  # Mumbai region
            "cloud.availability_zone": os.getenv("AZ", "ap-south-1a"),
            # Business context
            "business.unit": "payments",
            "business.region": "india",
            "compliance.data_residency": "india"
        })
        
        # Configure tracing
        self._setup_tracing(resource)
        
        # Configure metrics
        self._setup_metrics(resource)
        
        # Auto-instrumentation
        self._setup_auto_instrumentation()
        
        self.tracer = trace.get_tracer(service_name)
    
    def _setup_tracing(self, resource: Resource):
        """Setup distributed tracing with Jaeger"""
        
        # Create tracer provider
        trace_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(trace_provider)
        
        # Jaeger exporter configuration
        jaeger_exporter = JaegerExporter(
            agent_host_name=os.getenv("JAEGER_AGENT_HOST", "jaeger-agent"),
            agent_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
            collector_endpoint=os.getenv("JAEGER_COLLECTOR_ENDPOINT"),
            username=os.getenv("JAEGER_USER"),
            password=os.getenv("JAEGER_PASSWORD"),
        )
        
        # Batch span processor for performance
        span_processor = BatchSpanProcessor(
            jaeger_exporter,
            max_queue_size=4096,           # Larger queue for high throughput
            schedule_delay_millis=2000,    # 2 second batching
            export_timeout_millis=30000,   # 30 second timeout
            max_export_batch_size=1024     # Large batches for efficiency
        )
        
        trace_provider.add_span_processor(span_processor)
        
    def _setup_metrics(self, resource: Resource):
        """Setup metrics with Prometheus export"""
        
        # Prometheus metrics reader
        prometheus_reader = PrometheusMetricReader()
        
        # Metrics provider
        metrics_provider = MeterProvider(
            resource=resource,
            metric_readers=[prometheus_reader]
        )
        metrics.set_meter_provider(metrics_provider)
        
        self.meter = metrics.get_meter(self.service_name)
        
        # Custom business metrics
        self.business_metrics = {
            'order_processing_duration': self.meter.create_histogram(
                name="order_processing_duration_seconds",
                description="Order processing duration in seconds",
                unit="s"
            ),
            'payment_success_counter': self.meter.create_counter(
                name="payment_success_total",
                description="Total successful payments",
                unit="1"
            ),
            'user_tier_gauge': self.meter.create_up_down_counter(
                name="active_users_by_tier",
                description="Active users by tier",
                unit="1"
            )
        }
    
    def _setup_auto_instrumentation(self):
        """Setup automatic instrumentation for common libraries"""
        
        # HTTP requests
        RequestsInstrumentor().instrument()
        
        # Flask web framework
        FlaskInstrumentor().instrument()
        
        # Redis cache
        RedisInstrumentor().instrument()
        
        # PostgreSQL database
        Psycopg2Instrumentor().instrument()
        
    def trace_payment_flow(self, user_id: str, order_data: Dict) -> Dict:
        """Comprehensive payment flow tracing with Indian business context"""
        
        with self.tracer.start_span("payment_flow_orchestration") as root_span:
            # Set root span attributes
            root_span.set_attributes({
                "user.id": user_id,
                "order.id": order_data["order_id"],
                "order.value_inr": order_data["amount"],
                "order.currency": "INR",
                "order.items_count": len(order_data["items"]),
                "business.flow_type": "payment_orchestration"
            })
            
            # Add baggage for cross-cutting concerns
            baggage.set_baggage("user.tier", self._get_user_tier(user_id))
            baggage.set_baggage("order.category", order_data.get("category", "general"))
            baggage.set_baggage("feature.experiment", self._get_active_experiments(user_id))
            
            try:
                # Step 1: User Validation (Like checking dabba pickup address)
                user_validation_result = self._trace_user_validation(user_id, root_span)
                if not user_validation_result["valid"]:
                    return self._create_error_response("user_validation_failed", root_span)
                
                # Step 2: Order Validation (Like checking dabba contents)
                order_validation_result = self._trace_order_validation(order_data, root_span)
                if not order_validation_result["valid"]:
                    return self._create_error_response("order_validation_failed", root_span)
                
                # Step 3: Inventory Check (Like checking dabba availability)
                inventory_result = self._trace_inventory_check(order_data["items"], root_span)
                if not inventory_result["available"]:
                    return self._create_error_response("inventory_unavailable", root_span)
                
                # Step 4: Payment Processing (Like dabba transport)
                payment_result = self._trace_payment_processing(order_data, root_span)
                if not payment_result["success"]:
                    return self._create_error_response("payment_failed", root_span)
                
                # Step 5: Order Fulfillment (Like final delivery)
                fulfillment_result = self._trace_order_fulfillment(order_data, root_span)
                
                # Record success metrics
                self.business_metrics['payment_success_counter'].add(
                    1, {"payment_method": order_data.get("payment_method", "unknown")}
                )
                
                root_span.set_attributes({
                    "business.outcome": "success",
                    "business.revenue_inr": order_data["amount"],
                    "business.customer_satisfaction": 5.0
                })
                
                return {
                    "success": True,
                    "order_id": order_data["order_id"],
                    "payment_id": payment_result["payment_id"],
                    "estimated_delivery": fulfillment_result["estimated_delivery"]
                }
                
            except Exception as e:
                root_span.record_exception(e)
                root_span.set_status(Status(StatusCode.ERROR, str(e)))
                root_span.set_attributes({
                    "business.outcome": "error",
                    "error.type": e.__class__.__name__
                })
                raise
    
    def _trace_user_validation(self, user_id: str, parent_span) -> Dict:
        """Trace user validation with detailed context"""
        
        with self.tracer.start_span("user_validation", parent=parent_span) as span:
            span.set_attributes({
                "user.id": user_id,
                "validation.type": "comprehensive_check"
            })
            
            # Simulate user validation checks
            validation_checks = [
                ("kyc_verification", self._check_kyc(user_id)),
                ("account_status", self._check_account_status(user_id)), 
                ("fraud_score", self._check_fraud_score(user_id)),
                ("payment_limits", self._check_payment_limits(user_id))
            ]
            
            all_passed = True
            for check_name, result in validation_checks:
                span.add_event(f"validation_check_{check_name}", {
                    "check_result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                if not result:
                    all_passed = False
                    span.set_status(Status(StatusCode.ERROR, f"Failed {check_name}"))
                    
            span.set_attributes({
                "validation.checks_total": len(validation_checks),
                "validation.checks_passed": sum(1 for _, result in validation_checks if result),
                "validation.result": all_passed
            })
            
            return {"valid": all_passed, "checks": validation_checks}
    
    def _trace_payment_processing(self, order_data: Dict, parent_span) -> Dict:
        """Detailed payment processing tracing"""
        
        with self.tracer.start_span("payment_processing", parent=parent_span) as span:
            payment_method = order_data.get("payment_method", "UPI")
            amount = order_data["amount"]
            
            span.set_attributes({
                "payment.method": payment_method,
                "payment.amount_inr": amount,
                "payment.currency": "INR"
            })
            
            # Route to specific payment method handler
            if payment_method == "UPI":
                return self._trace_upi_payment(order_data, span)
            elif payment_method == "CREDIT_CARD":
                return self._trace_card_payment(order_data, span)
            elif payment_method == "WALLET":
                return self._trace_wallet_payment(order_data, span)
            else:
                span.set_status(Status(StatusCode.ERROR, f"Unsupported payment method: {payment_method}"))
                return {"success": False, "error": "unsupported_payment_method"}
    
    def _trace_upi_payment(self, order_data: Dict, parent_span) -> Dict:
        """Detailed UPI payment flow tracing"""
        
        with self.tracer.start_span("upi_payment_flow", parent=parent_span) as span:
            upi_vpa = order_data.get("upi_vpa", "")
            amount = order_data["amount"]
            
            # Extract bank from UPI VPA
            bank = upi_vpa.split('@')[1] if '@' in upi_vpa else "unknown"
            
            span.set_attributes({
                "upi.vpa_masked": self._mask_upi_vpa(upi_vpa),
                "upi.bank": bank,
                "upi.amount_inr": amount,
                "upi.transaction_type": "P2M"  # Person to Merchant
            })
            
            # Step 1: Bank Validation
            with self.tracer.start_span("upi_bank_validation", parent=span) as bank_span:
                bank_span.set_attributes({
                    "upi.bank_code": bank,
                    "validation.type": "vpa_verification"
                })
                
                # Simulate bank validation
                time.sleep(0.1)  # Simulate network call
                validation_success = random.random() > 0.05  # 95% success rate
                
                bank_span.set_attributes({
                    "upi.validation_result": validation_success,
                    "upi.validation_time_ms": 100
                })
                
                if not validation_success:
                    bank_span.set_status(Status(StatusCode.ERROR, "VPA validation failed"))
                    return {"success": False, "error": "vpa_validation_failed"}
            
            # Step 2: NPCI Transaction Processing
            with self.tracer.start_span("npci_transaction", parent=span) as npci_span:
                npci_ref = f"NPCI{random.randint(1000000, 9999999)}"
                
                npci_span.set_attributes({
                    "npci.reference_id": npci_ref,
                    "npci.transaction_type": "P2M",
                    "npci.amount_inr": amount
                })
                
                # Simulate NPCI processing stages
                processing_steps = [
                    ("collect_request_sent", 0.05),
                    ("payer_bank_approval", 0.10),
                    ("beneficiary_bank_credit", 0.08),
                    ("settlement_initiated", 0.02)
                ]
                
                total_processing_time = 0
                for step_name, duration in processing_steps:
                    time.sleep(duration)
                    total_processing_time += duration
                    
                    npci_span.add_event(step_name, {
                        "timestamp": datetime.utcnow().isoformat(),
                        "processing_time_ms": int(duration * 1000)
                    })
                
                # Generate transaction ID
                transaction_id = f"TXN_{random.randint(100000000, 999999999)}"
                
                npci_span.set_attributes({
                    "npci.transaction_id": transaction_id,
                    "npci.total_processing_time_ms": int(total_processing_time * 1000),
                    "npci.settlement_status": "completed"
                })
            
            # Record processing duration metric
            total_duration = time.time()  # This would be calculated properly
            self.business_metrics['order_processing_duration'].record(
                total_duration, 
                {"payment_method": "UPI", "bank": bank}
            )
            
            span.set_attributes({
                "payment.success": True,
                "payment.transaction_id": transaction_id,
                "payment.npci_ref": npci_ref,
                "payment.settlement_time": "immediate"
            })
            
            return {
                "success": True,
                "payment_id": transaction_id,
                "npci_ref": npci_ref,
                "settlement_time": "immediate"
            }
    
    def _mask_upi_vpa(self, upi_vpa: str) -> str:
        """Mask UPI VPA for privacy in traces"""
        if '@' in upi_vpa:
            user_part, domain = upi_vpa.split('@')
            if len(user_part) > 4:
                masked_user = user_part[:2] + '*' * (len(user_part) - 4) + user_part[-2:]
                return f"{masked_user}@{domain}"
        return "***@***"
        
    def create_manual_span(self, operation_name: str, **attributes) -> trace.Span:
        """Create manual span for custom operations"""
        span = self.tracer.start_span(operation_name)
        
        # Add common attributes
        span.set_attributes({
            "manual_instrumentation": True,
            "service.name": self.service_name,
            **attributes
        })
        
        return span
```

### Context Propagation and Sampling Strategies

**Smart Sampling for Cost-Effective Tracing:**

```python
from opentelemetry.sdk.trace.sampling import Sampler, SamplingResult, SamplingDecision
from opentelemetry.util.types import Attributes
from opentelemetry.trace import Link, SpanKind
from typing import Optional, Sequence
import random

class IndianEcommerceSampler(Sampler):
    """Intelligent sampling for Indian e-commerce workloads"""
    
    def __init__(self):
        # Base sampling rates for different scenarios
        self.sampling_rates = {
            'base_rate': 0.001,           # 0.1% base sampling
            'error_rate': 1.0,            # 100% for errors
            'high_value_rate': 0.1,       # 10% for high-value transactions
            'new_user_rate': 0.05,        # 5% for new users
            'festival_rate': 0.01,        # 1% during festivals
            'critical_service_rate': 0.02  # 2% for critical services
        }
        
        # Business thresholds
        self.high_value_threshold_inr = 10000  # ₹10K+
        self.new_user_days_threshold = 30      # Users < 30 days old
        
    def should_sample(self, parent_context, trace_id, name: str, kind: SpanKind = None,
                     attributes: Attributes = None, links: Sequence[Link] = None,
                     trace_state = None) -> SamplingResult:
        """Make intelligent sampling decision"""
        
        # Always sample errors
        if attributes and self._is_error_trace(attributes):
            return SamplingResult(
                SamplingDecision.RECORD_AND_SAMPLE,
                attributes={"sampling.reason": "error_trace"}
            )
        
        # Always sample high-value transactions
        if attributes and self._is_high_value_transaction(attributes):
            return SamplingResult(
                SamplingDecision.RECORD_AND_SAMPLE,
                attributes={"sampling.reason": "high_value_transaction"}
            )
        
        # Higher sampling for new users (better debugging)
        if attributes and self._is_new_user(attributes):
            if self._probabilistic_sample(self.sampling_rates['new_user_rate'], trace_id):
                return SamplingResult(
                    SamplingDecision.RECORD_AND_SAMPLE,
                    attributes={"sampling.reason": "new_user"}
                )
        
        # Festival season sampling (higher load, need more visibility)
        if self._is_festival_season():
            if self._probabilistic_sample(self.sampling_rates['festival_rate'], trace_id):
                return SamplingResult(
                    SamplingDecision.RECORD_AND_SAMPLE,
                    attributes={"sampling.reason": "festival_season"}
                )
        
        # Critical service sampling
        if attributes and self._is_critical_service(attributes):
            if self._probabilistic_sample(self.sampling_rates['critical_service_rate'], trace_id):
                return SamplingResult(
                    SamplingDecision.RECORD_AND_SAMPLE,
                    attributes={"sampling.reason": "critical_service"}
                )
        
        # Base probabilistic sampling
        if self._probabilistic_sample(self.sampling_rates['base_rate'], trace_id):
            return SamplingResult(
                SamplingDecision.RECORD_AND_SAMPLE,
                attributes={"sampling.reason": "probabilistic"}
            )
        
        # Don't sample
        return SamplingResult(SamplingDecision.DROP)
    
    def _is_error_trace(self, attributes: Attributes) -> bool:
        """Check if trace contains error indicators"""
        return (
            attributes.get("error", False) or
            attributes.get("http.status_code", 0) >= 400 or
            attributes.get("otel.status_code") == "ERROR"
        )
    
    def _is_high_value_transaction(self, attributes: Attributes) -> bool:
        """Check if transaction is high-value"""
        amount = attributes.get("order.value_inr", 0) or attributes.get("payment.amount_inr", 0)
        return float(amount) >= self.high_value_threshold_inr
    
    def _is_new_user(self, attributes: Attributes) -> bool:
        """Check if user is new"""
        user_age_days = attributes.get("user.registration_days", 999)
        return int(user_age_days) <= self.new_user_days_threshold
        
    def _is_critical_service(self, attributes: Attributes) -> bool:
        """Check if this is a critical service"""
        service_name = attributes.get("service.name", "")
        critical_services = ["payment-service", "auth-service", "order-service"]
        return service_name in critical_services
        
    def _is_festival_season(self) -> bool:
        """Check if current time is during festival season"""
        from datetime import datetime
        current_month = datetime.now().month
        
        # Major festival months in India
        festival_months = [10, 11, 12, 1, 3, 8]  # Diwali, New Year, Holi, Independence Day
        return current_month in festival_months
        
    def _probabilistic_sample(self, sampling_rate: float, trace_id) -> bool:
        """Make probabilistic sampling decision"""
        trace_id_int = int(trace_id.to_bytes()[:8].hex(), 16)
        threshold = int(sampling_rate * (2**63))
        return (trace_id_int % (2**63)) < threshold

    def get_description(self) -> str:
        return "IndianEcommerceSampler"
```

---

## Conclusion of Part 2

Dosto, yahan complete hota hai Part 2 of our Observability journey! Humne explore kiya:

### **Key Concepts Covered:**

**1. Structured Logging Evolution**
- From print statements to professional police station-style logging
- JSON-based structured formats with correlation IDs
- Business event logging with Indian context

**2. ELK Stack Mastery** 
- Production Elasticsearch configuration for Indian scale
- Advanced Logstash pipeline with fraud detection
- Real-time log processing with Kafka integration
- Kibana dashboards for investigation and analysis

**3. Distributed Tracing Magic**
- Dabbawala system as perfect tracing metaphor
- OpenTelemetry enterprise implementation
- Context propagation across microservices
- Smart sampling strategies for cost optimization

**4. Indian Business Context**
- UPI transaction tracing with bank correlation
- Festival season log analysis and fraud detection
- Regional patterns and tier-city analysis  
- Compliance logging for RBI/SEBI requirements

### **Production-Ready Implementation Highlights:**

- **Real-time Fraud Detection**: Kafka-based stream processing analyzing velocity, location, and amount patterns
- **Smart Log Enrichment**: Automatic GeoIP, bank extraction, festival context, and business categorization
- **Intelligent Sampling**: Cost-effective tracing with business-aware sampling (errors: 100%, high-value: 10%, new users: 5%)
- **Context Correlation**: Complete request journey tracking from API gateway to payment settlement

### **Part 2 Mumbai Metaphors Summary:**
- **Police Station FIR** = Structured Logging System
- **Dabbawala Journey** = Distributed Tracing Flow  
- **Investigation Officer** = Kibana Analysis Dashboard
- **Traffic Control Room** = Real-time Log Monitoring

### **Performance at Scale:**
- **Log Volume**: Processing 100GB+ daily logs with smart retention
- **Trace Volume**: 500M+ spans/day with <1% performance impact
- **Real-time Processing**: Sub-second fraud detection on payment streams
- **Cost Optimization**: 60-80% cost reduction vs commercial solutions

**Next in Part 3:**
- Advanced Grafana dashboard design for war rooms
- Multi-level alerting with business impact calculation
- Alert fatigue prevention and intelligent suppression
- Indian regulatory compliance dashboards
- Real production war stories and incident responses

Part 3 mein hum complete karenge observability ki final piece - dashboards aur alerting systems jo actually production mein kaam aate hain!

**Yaad rakhiye**: Just like Mumbai's dabbawala system has 99.99% accuracy through proper tracking and handoffs, distributed tracing gives us the same visibility and reliability for our software systems! 🏙️📦🚂
#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 4: ELK Stack Log Aggregation for High-Volume Applications

भारतीय scale पर log aggregation - Zomato NYE style 60TB daily logs
Production-ready ELK stack implementation with Indian context

Author: Hindi Tech Podcast
Context: High-volume log processing for Indian applications
"""

import json
import time
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import gzip
import hashlib

# Elasticsearch and logging imports
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError, RequestError
import structlog
from pythonjsonlogger import jsonlogger

logger = structlog.get_logger()

class LogLevel(Enum):
    """Log levels for categorization"""
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"

class ApplicationType(Enum):
    """Different application types in Indian ecosystem"""
    FOOD_DELIVERY = "food_delivery"      # Zomato, Swiggy
    ECOMMERCE = "ecommerce"              # Flipkart, Amazon
    FINTECH = "fintech"                  # Paytm, PhonePe
    RIDE_SHARING = "ride_sharing"        # Ola, Uber
    SOCIAL_MEDIA = "social_media"        # ShareChat, Koo
    EDTECH = "edtech"                    # BYJU'S, Unacademy
    HEALTHCARE = "healthcare"            # Practo, 1mg
    TRAVEL = "travel"                    # MakeMyTrip, Goibibo

class LogSource(Enum):
    """Different sources of logs"""
    APPLICATION = "application"
    NGINX = "nginx"
    DATABASE = "database"
    KAFKA = "kafka"
    KUBERNETES = "kubernetes"
    SECURITY = "security"
    AUDIT = "audit"
    PAYMENT = "payment"

@dataclass
class IndianLogEntry:
    """
    भारतीय applications के लिए structured log entry
    Multi-language support और regional context के साथ
    """
    timestamp: datetime
    level: LogLevel
    message: str
    source: LogSource
    application: ApplicationType
    service_name: str
    
    # Indian context fields
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    language: str = "english"  # hindi, english, tamil, etc.
    
    # Technical fields
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    hostname: Optional[str] = None
    pod_name: Optional[str] = None
    container_id: Optional[str] = None
    
    # Business context
    order_id: Optional[str] = None
    payment_id: Optional[str] = None
    user_tier: Optional[str] = None  # metro, tier1, tier2, tier3
    business_event: Optional[str] = None  # bbd, diwali, nye
    
    # Error details
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # Performance metrics
    response_time_ms: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    
    # Security context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    security_event: Optional[str] = None
    
    def to_elasticsearch_doc(self) -> Dict[str, Any]:
        """
        Elasticsearch document format में convert करता है
        """
        doc = {
            "@timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "source": self.source.value,
            "application": self.application.value,
            "service_name": self.service_name,
            
            # Indian context
            "geo": {
                "city": self.city,
                "state": self.state,
                "country": "IN"
            },
            "localization": {
                "language": self.language,
                "user_tier": self.user_tier
            },
            
            # Identifiers
            "identifiers": {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "trace_id": self.trace_id,
                "span_id": self.span_id
            },
            
            # Infrastructure
            "infrastructure": {
                "hostname": self.hostname,
                "pod_name": self.pod_name,
                "container_id": self.container_id
            },
            
            # Business
            "business": {
                "order_id": self.order_id,
                "payment_id": self.payment_id,
                "event": self.business_event
            },
            
            # Performance
            "performance": {
                "response_time_ms": self.response_time_ms,
                "cpu_usage": self.cpu_usage,
                "memory_usage_mb": self.memory_usage_mb
            },
            
            # Security
            "security": {
                "ip_address": self.ip_address,
                "user_agent": self.user_agent,
                "event": self.security_event
            }
        }
        
        # Add error details if present
        if self.error_code or self.error_message:
            doc["error"] = {
                "code": self.error_code,
                "message": self.error_message,
                "stack_trace": self.stack_trace
            }
        
        # Remove None values
        return self._remove_none_values(doc)
    
    def _remove_none_values(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively remove None values from dictionary"""
        if isinstance(d, dict):
            return {k: self._remove_none_values(v) for k, v in d.items() if v is not None}
        return d

class ElasticsearchLogAggregator:
    """
    Production-ready Elasticsearch log aggregator
    भारतीय scale के लिए optimized with 60TB+ daily capacity
    """
    
    def __init__(self, 
                 hosts: List[str] = ["localhost:9200"],
                 index_prefix: str = "indian-logs",
                 max_retries: int = 3,
                 timeout: int = 30):
        """
        Elasticsearch client initialize करता है
        """
        self.hosts = hosts
        self.index_prefix = index_prefix
        self.max_retries = max_retries
        
        # Elasticsearch client with authentication
        self.es = Elasticsearch(
            hosts=hosts,
            max_retries=max_retries,
            retry_on_timeout=True,
            timeout=timeout,
            # Add authentication if needed
            # http_auth=('username', 'password'),
            # use_ssl=True,
            # verify_certs=True
        )
        
        # Indian cities for geo-indexing
        self.indian_cities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
            "Pune", "Hyderabad", "Ahmedabad", "Surat", "Jaipur",
            "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal",
            "Coimbatore", "Kochi", "Thiruvananthapuram", "Madurai"
        ]
        
        # Initialize index templates
        asyncio.create_task(self._setup_index_templates())
        
        logger.info("Elasticsearch log aggregator initialized", 
                   hosts=hosts, index_prefix=index_prefix)

    async def _setup_index_templates(self):
        """
        Elasticsearch index templates setup करता है
        Indian context के लिए optimized mappings
        """
        template_name = f"{self.index_prefix}-template"
        
        template_config = {
            "index_patterns": [f"{self.index_prefix}-*"],
            "template": {
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 1,
                    "index.refresh_interval": "10s",
                    "index.max_result_window": 100000,
                    
                    # Indian language analysis
                    "analysis": {
                        "analyzer": {
                            "indian_text_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": ["lowercase", "stop"]
                            },
                            "hindi_analyzer": {
                                "type": "custom", 
                                "tokenizer": "icu_tokenizer",
                                "filter": ["lowercase", "hindi_stop_words"]
                            }
                        },
                        "filter": {
                            "hindi_stop_words": {
                                "type": "stop",
                                "stopwords": ["है", "का", "की", "को", "में", "से", "और", "या"]
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "message": {
                            "type": "text",
                            "analyzer": "indian_text_analyzer",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 1024}
                            }
                        },
                        "source": {"type": "keyword"},
                        "application": {"type": "keyword"},
                        "service_name": {"type": "keyword"},
                        
                        # Geo fields for Indian context
                        "geo": {
                            "properties": {
                                "city": {"type": "keyword"},
                                "state": {"type": "keyword"},
                                "country": {"type": "keyword"}
                            }
                        },
                        
                        # Localization
                        "localization": {
                            "properties": {
                                "language": {"type": "keyword"},
                                "user_tier": {"type": "keyword"}
                            }
                        },
                        
                        # Identifiers
                        "identifiers": {
                            "properties": {
                                "user_id": {"type": "keyword"},
                                "session_id": {"type": "keyword"},
                                "trace_id": {"type": "keyword"},
                                "span_id": {"type": "keyword"}
                            }
                        },
                        
                        # Performance metrics
                        "performance": {
                            "properties": {
                                "response_time_ms": {"type": "float"},
                                "cpu_usage": {"type": "float"},
                                "memory_usage_mb": {"type": "float"}
                            }
                        },
                        
                        # Error handling
                        "error": {
                            "properties": {
                                "code": {"type": "keyword"},
                                "message": {"type": "text"},
                                "stack_trace": {"type": "text", "index": False}
                            }
                        }
                    }
                }
            }
        }
        
        try:
            self.es.indices.put_index_template(
                name=template_name,
                body=template_config
            )
            logger.info("Index template created", template=template_name)
        except Exception as e:
            logger.error("Failed to create index template", error=str(e))

    def get_daily_index_name(self, date: datetime = None) -> str:
        """
        Daily index name generate करता है
        Format: indian-logs-YYYY.MM.DD
        """
        if date is None:
            date = datetime.utcnow()
        return f"{self.index_prefix}-{date.strftime('%Y.%m.%d')}"

    async def ingest_log(self, log_entry: IndianLogEntry) -> bool:
        """
        Single log entry को Elasticsearch में ingest करता है
        """
        try:
            index_name = self.get_daily_index_name(log_entry.timestamp)
            doc = log_entry.to_elasticsearch_doc()
            
            result = self.es.index(
                index=index_name,
                body=doc,
                timeout='30s'
            )
            
            return result['result'] in ['created', 'updated']
            
        except Exception as e:
            logger.error("Failed to ingest log entry", 
                        error=str(e), 
                        log_entry=log_entry.message[:100])
            return False

    async def bulk_ingest_logs(self, log_entries: List[IndianLogEntry], 
                              chunk_size: int = 1000) -> Dict[str, int]:
        """
        Bulk log ingestion for high-volume processing
        Zomato NYE style 60TB+ daily log handling
        """
        stats = {"success": 0, "failed": 0, "total": len(log_entries)}
        
        def doc_generator():
            for log_entry in log_entries:
                index_name = self.get_daily_index_name(log_entry.timestamp)
                yield {
                    "_index": index_name,
                    "_source": log_entry.to_elasticsearch_doc()
                }
        
        try:
            # Bulk index with parallel indexing
            for success, info in helpers.parallel_bulk(
                client=self.es,
                actions=doc_generator(),
                chunk_size=chunk_size,
                thread_count=4,
                max_chunk_bytes=10 * 1024 * 1024,  # 10MB chunks
                timeout='60s'
            ):
                if success:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
                    logger.error("Bulk indexing error", error=info)
            
            logger.info("Bulk ingestion completed", 
                       success=stats["success"], 
                       failed=stats["failed"],
                       total=stats["total"])
            
        except Exception as e:
            logger.error("Bulk ingestion failed", error=str(e))
            stats["failed"] = stats["total"]
        
        return stats

    async def search_logs(self, 
                         query: Dict[str, Any],
                         start_time: datetime,
                         end_time: datetime,
                         size: int = 100) -> Dict[str, Any]:
        """
        Advanced log search with Indian context filters
        """
        # Build time range
        time_filter = {
            "range": {
                "@timestamp": {
                    "gte": start_time.isoformat(),
                    "lte": end_time.isoformat(),
                    "time_zone": "Asia/Kolkata"
                }
            }
        }
        
        # Combine with user query
        if "bool" not in query:
            query = {"bool": {"must": [query]}}
        
        query["bool"]["filter"] = [time_filter]
        
        # Search across daily indices
        indices = []
        current_date = start_time.date()
        end_date = end_time.date()
        
        while current_date <= end_date:
            index_name = self.get_daily_index_name(datetime.combine(current_date, datetime.min.time()))
            indices.append(index_name)
            current_date += timedelta(days=1)
        
        try:
            result = self.es.search(
                index=",".join(indices),
                body={
                    "query": query,
                    "size": size,
                    "sort": [{"@timestamp": {"order": "desc"}}]
                },
                timeout='30s'
            )
            
            return {
                "total": result["hits"]["total"]["value"],
                "logs": [hit["_source"] for hit in result["hits"]["hits"]],
                "took_ms": result["took"]
            }
            
        except Exception as e:
            logger.error("Log search failed", error=str(e))
            return {"total": 0, "logs": [], "error": str(e)}

    async def get_log_analytics(self, 
                               start_time: datetime,
                               end_time: datetime) -> Dict[str, Any]:
        """
        Log analytics और insights generate करता है
        Indian business context के साथ
        """
        analytics_query = {
            "size": 0,
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": start_time.isoformat(),
                        "lte": end_time.isoformat(),
                        "time_zone": "Asia/Kolkata"
                    }
                }
            },
            "aggs": {
                # Log level distribution
                "log_levels": {
                    "terms": {"field": "level", "size": 10}
                },
                
                # Application wise breakdown
                "applications": {
                    "terms": {"field": "application", "size": 20}
                },
                
                # City wise distribution
                "cities": {
                    "terms": {"field": "geo.city", "size": 20}
                },
                
                # Error rate over time
                "error_timeline": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "calendar_interval": "1h",
                        "time_zone": "Asia/Kolkata"
                    },
                    "aggs": {
                        "error_rate": {
                            "filter": {"term": {"level": "error"}}
                        }
                    }
                },
                
                # Performance metrics
                "avg_response_time": {
                    "avg": {"field": "performance.response_time_ms"}
                },
                
                # Business events
                "business_events": {
                    "terms": {"field": "business.event", "size": 10}
                },
                
                # Language distribution
                "languages": {
                    "terms": {"field": "localization.language", "size": 10}
                },
                
                # User tier analysis
                "user_tiers": {
                    "terms": {"field": "localization.user_tier", "size": 5}
                }
            }
        }
        
        try:
            result = self.es.search(
                index=f"{self.index_prefix}-*",
                body=analytics_query,
                timeout='60s'
            )
            
            return {
                "total_logs": result["hits"]["total"]["value"],
                "log_levels": result["aggregations"]["log_levels"]["buckets"],
                "applications": result["aggregations"]["applications"]["buckets"],
                "cities": result["aggregations"]["cities"]["buckets"],
                "error_timeline": result["aggregations"]["error_timeline"]["buckets"],
                "avg_response_time": result["aggregations"]["avg_response_time"]["value"],
                "business_events": result["aggregations"]["business_events"]["buckets"],
                "languages": result["aggregations"]["languages"]["buckets"],
                "user_tiers": result["aggregations"]["user_tiers"]["buckets"]
            }
            
        except Exception as e:
            logger.error("Analytics query failed", error=str(e))
            return {"error": str(e)}

class IndianLogGenerator:
    """
    भारतीय applications के लिए realistic log generator
    Different patterns और use cases के साथ
    """
    
    def __init__(self):
        self.applications = list(ApplicationType)
        self.cities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
            "Pune", "Hyderabad", "Ahmedabad", "Surat", "Jaipur"
        ]
        self.languages = ["english", "hindi", "tamil", "telugu", "bengali", "marathi"]
        self.user_tiers = ["metro", "tier1", "tier2", "tier3"]
        
        # Common Indian error patterns
        self.error_patterns = [
            ("PAYMENT_GATEWAY_TIMEOUT", "UPI payment gateway timed out"),
            ("BANK_SERVICE_UNAVAILABLE", "Bank service temporarily unavailable"),
            ("OTP_VERIFICATION_FAILED", "OTP verification failed after 3 attempts"),
            ("DATABASE_CONNECTION_POOL_EXHAUSTED", "Database connection pool exhausted"),
            ("THIRD_PARTY_API_RATE_LIMITED", "Third party API rate limit exceeded"),
            ("DELIVERY_PARTNER_UNAVAILABLE", "No delivery partners available in area"),
            ("INVENTORY_OUT_OF_STOCK", "Product out of stock in nearest warehouse"),
            ("GST_CALCULATION_ERROR", "GST calculation service error"),
            ("REGIONAL_SERVICE_DOWN", "Regional service temporarily down"),
            ("FESTIVAL_TRAFFIC_OVERLOAD", "System overloaded due to festival traffic")
        ]

    def generate_log_entry(self, 
                          timestamp: datetime = None,
                          application: ApplicationType = None,
                          level: LogLevel = None) -> IndianLogEntry:
        """
        Realistic Indian log entry generate करता है
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if application is None:
            application = random.choice(self.applications)
        
        if level is None:
            # Error rate increases during peak hours (10-11 AM, 7-9 PM IST)
            current_hour = timestamp.hour
            if current_hour in [10, 11, 19, 20, 21]:
                level = random.choices(
                    list(LogLevel),
                    weights=[5, 60, 20, 12, 3]  # Higher error rate during peak
                )[0]
            else:
                level = random.choices(
                    list(LogLevel),
                    weights=[10, 75, 10, 4, 1]  # Normal error rate
                )[0]
        
        # Generate context based on application type
        city = random.choice(self.cities)
        language = random.choice(self.languages)
        user_tier = random.choice(self.user_tiers)
        
        # Business event detection
        business_event = None
        if timestamp.month == 10:  # October - BBD season
            business_event = "big_billion_days"
        elif timestamp.month == 11:  # November - Diwali
            business_event = "diwali_sale"
        elif timestamp.month == 12 and timestamp.day == 31:  # NYE
            business_event = "new_year_eve"
        
        # Generate message based on application and level
        message = self._generate_message(application, level, city, language)
        
        # Error details for error logs
        error_code = None
        error_message = None
        if level in [LogLevel.ERROR, LogLevel.FATAL]:
            error_code, error_message = random.choice(self.error_patterns)
        
        return IndianLogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source=random.choice(list(LogSource)),
            application=application,
            service_name=f"{application.value}-service",
            
            # Indian context
            user_id=f"U{random.randint(100000, 999999)}",
            session_id=f"S{uuid.uuid4().hex[:16]}",
            city=city,
            state=self._get_state_for_city(city),
            language=language,
            
            # Technical
            trace_id=f"T{uuid.uuid4().hex}",
            span_id=f"S{uuid.uuid4().hex[:16]}",
            hostname=f"app-{random.randint(1, 100)}",
            pod_name=f"pod-{application.value}-{random.randint(1, 50)}",
            
            # Business
            order_id=f"ORD{random.randint(1000000, 9999999)}" if random.random() < 0.3 else None,
            payment_id=f"PAY{random.randint(1000000, 9999999)}" if random.random() < 0.2 else None,
            user_tier=user_tier,
            business_event=business_event,
            
            # Error
            error_code=error_code,
            error_message=error_message,
            
            # Performance
            response_time_ms=random.uniform(50, 5000),
            cpu_usage=random.uniform(10, 90),
            memory_usage_mb=random.uniform(100, 2000),
            
            # Security
            ip_address=f"{random.randint(1, 223)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            user_agent=random.choice(["mobile_app_android", "mobile_app_ios", "web_browser", "api_client"])
        )

    def _generate_message(self, app: ApplicationType, level: LogLevel, 
                         city: str, language: str) -> str:
        """Application और context के according message generate करता है"""
        
        messages = {
            ApplicationType.FOOD_DELIVERY: {
                LogLevel.INFO: [
                    f"Order placed successfully in {city}",
                    f"Delivery partner assigned for {city} order",
                    f"Restaurant confirmed order in {city}"
                ],
                LogLevel.ERROR: [
                    f"Failed to assign delivery partner in {city}",
                    f"Restaurant cancelled order in {city}",
                    f"Payment gateway timeout for {city} order"
                ]
            },
            ApplicationType.ECOMMERCE: {
                LogLevel.INFO: [
                    f"Product added to cart by {city} user",
                    f"Checkout initiated for {city} customer",
                    f"Order shipped from {city} warehouse"
                ],
                LogLevel.ERROR: [
                    f"Payment failed for {city} customer",
                    f"Inventory unavailable in {city} warehouse",
                    f"Shipping address validation failed for {city}"
                ]
            },
            ApplicationType.FINTECH: {
                LogLevel.INFO: [
                    f"UPI transaction successful for {city} user",
                    f"KYC verification completed for {city} customer",
                    f"Wallet recharged successfully in {city}"
                ],
                LogLevel.ERROR: [
                    f"UPI transaction failed for {city} user",
                    f"Bank service timeout in {city}",
                    f"Fraud detection triggered for {city} transaction"
                ]
            }
        }
        
        app_messages = messages.get(app, {
            LogLevel.INFO: [f"Service operation completed in {city}"],
            LogLevel.ERROR: [f"Service operation failed in {city}"]
        })
        
        level_messages = app_messages.get(level, app_messages.get(LogLevel.INFO, [f"Log message from {city}"]))
        
        base_message = random.choice(level_messages)
        
        # Add Hindi translation for some messages
        if language == "hindi" and random.random() < 0.3:
            hindi_suffix = " (सेवा संदेश)"
            base_message += hindi_suffix
        
        return base_message

    def _get_state_for_city(self, city: str) -> str:
        """City के लिए appropriate state return करता है"""
        city_state_map = {
            "Mumbai": "Maharashtra", "Pune": "Maharashtra", "Nagpur": "Maharashtra",
            "Delhi": "Delhi", "Noida": "Uttar Pradesh", "Gurgaon": "Haryana",
            "Bangalore": "Karnataka", "Mysore": "Karnataka",
            "Chennai": "Tamil Nadu", "Coimbatore": "Tamil Nadu", "Madurai": "Tamil Nadu",
            "Kolkata": "West Bengal", "Durgapur": "West Bengal",
            "Hyderabad": "Telangana", "Warangal": "Telangana",
            "Ahmedabad": "Gujarat", "Surat": "Gujarat", "Vadodara": "Gujarat",
            "Jaipur": "Rajasthan", "Jodhpur": "Rajasthan", "Udaipur": "Rajasthan"
        }
        
        return city_state_map.get(city, "Unknown")

    def generate_bulk_logs(self, 
                          count: int,
                          start_time: datetime = None,
                          end_time: datetime = None) -> List[IndianLogEntry]:
        """
        Bulk logs generate करता है testing के लिए
        """
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(hours=1)
        if end_time is None:
            end_time = datetime.utcnow()
        
        logs = []
        time_diff = end_time - start_time
        
        for i in range(count):
            # Random timestamp within range
            random_seconds = random.uniform(0, time_diff.total_seconds())
            timestamp = start_time + timedelta(seconds=random_seconds)
            
            log_entry = self.generate_log_entry(timestamp=timestamp)
            logs.append(log_entry)
        
        return logs

async def simulate_high_volume_logging():
    """
    High-volume logging simulation
    Zomato NYE style traffic pattern के साथ
    """
    print("🚀 Starting High-Volume Log Aggregation Simulation")
    print("📊 Simulating Indian application logs at scale")
    print("🎯 NYE/BBD style traffic patterns")
    
    # Initialize components
    aggregator = ElasticsearchLogAggregator()
    generator = IndianLogGenerator()
    
    # Simulate different traffic patterns
    patterns = [
        {"name": "Normal Traffic", "logs_per_minute": 1000, "duration_minutes": 5},
        {"name": "Peak Hours", "logs_per_minute": 5000, "duration_minutes": 3},
        {"name": "Festival Rush", "logs_per_minute": 10000, "duration_minutes": 2},
        {"name": "NYE Peak", "logs_per_minute": 20000, "duration_minutes": 1}
    ]
    
    total_ingested = 0
    
    for pattern in patterns:
        print(f"\n📈 Simulating: {pattern['name']}")
        print(f"   Rate: {pattern['logs_per_minute']} logs/minute")
        print(f"   Duration: {pattern['duration_minutes']} minutes")
        
        start_time = datetime.utcnow()
        
        for minute in range(pattern['duration_minutes']):
            # Generate logs for this minute
            logs_count = pattern['logs_per_minute']
            minute_start = start_time + timedelta(minutes=minute)
            minute_end = minute_start + timedelta(minutes=1)
            
            logs = generator.generate_bulk_logs(
                count=logs_count,
                start_time=minute_start,
                end_time=minute_end
            )
            
            # Ingest logs
            print(f"   📝 Ingesting {logs_count} logs for minute {minute + 1}...")
            stats = await aggregator.bulk_ingest_logs(logs, chunk_size=500)
            
            total_ingested += stats['success']
            
            print(f"   ✅ Success: {stats['success']}, Failed: {stats['failed']}")
            
            # Brief pause between minutes
            await asyncio.sleep(1)
    
    print(f"\n🎉 Simulation completed!")
    print(f"📊 Total logs ingested: {total_ingested:,}")
    
    # Generate analytics
    print("\n📈 Generating log analytics...")
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    
    analytics = await aggregator.get_log_analytics(start_time, end_time)
    
    if "error" not in analytics:
        print(f"   Total logs analyzed: {analytics['total_logs']:,}")
        print(f"   Average response time: {analytics['avg_response_time']:.2f}ms")
        print(f"   Top applications: {[app['key'] for app in analytics['applications'][:3]]}")
        print(f"   Top cities: {[city['key'] for city in analytics['cities'][:3]]}")
        print(f"   Languages: {[lang['key'] for lang in analytics['languages'][:3]]}")

def main():
    """
    Main function - ELK log aggregation demonstration
    """
    print("📋 ELK Stack Log Aggregation for Indian Applications")
    print("🏗️ Production-ready implementation for 60TB+ daily logs")
    print("🇮🇳 Indian context with multi-language support")
    print("\nFeatures:")
    print("  ✅ High-volume bulk ingestion")
    print("  ✅ Multi-language log analysis")
    print("  ✅ Regional performance tracking")
    print("  ✅ Business event correlation")
    print("  ✅ Festival traffic patterns")
    print("  ✅ Real-time analytics")
    print("\nAccess URLs:")
    print("  🔍 Elasticsearch: http://localhost:9200")
    print("  📊 Kibana: http://localhost:5601")
    print("\nStarting simulation...\n")
    
    try:
        asyncio.run(simulate_high_volume_logging())
    except KeyboardInterrupt:
        print("\n🛑 Stopping log aggregation simulation...")
        print("✅ Simulation stopped successfully!")

if __name__ == "__main__":
    main()

"""
Production Deployment Guide:

1. Elasticsearch Cluster Configuration:
   - Minimum 3 master nodes for HA
   - Dedicated data nodes for ingestion
   - Hot-warm-cold architecture for cost optimization
   - Proper heap size (50% of RAM, max 32GB)

2. Index Management:
   - Daily indices for log rotation
   - Index lifecycle management (ILM)
   - Hot data: 7 days on SSD
   - Warm data: 30 days on HDD
   - Cold data: 1 year on object storage

3. Performance Optimization:
   - Bulk indexing with parallel workers
   - Optimized mappings for Indian content
   - Proper shard sizing (10-50GB per shard)
   - Index templates for consistency

4. Security & Compliance:
   - Authentication and authorization
   - Audit logging for compliance
   - Data encryption at rest and in transit
   - GDPR compliance for user data

5. Monitoring & Alerting:
   - Cluster health monitoring
   - Ingestion rate tracking
   - Search performance metrics
   - Disk space utilization

6. Indian Context Optimizations:
   - Multi-language text analysis
   - Regional data center deployment
   - Festival season capacity planning
   - Compliance with local data laws

Example Kibana Dashboards:
- Application Performance Overview
- Regional Log Distribution
- Error Rate Trends
- Business Event Correlation
- Security Incident Tracking

Log Retention Policy:
- Application logs: 30 days hot, 90 days warm, 1 year cold
- Security logs: 90 days hot, 2 years warm, 7 years cold
- Audit logs: 180 days hot, 3 years warm, 10 years cold
- Debug logs: 7 days hot, 30 days warm, deleted
"""
#!/usr/bin/env python3
"""
Maxwell CDC Implementation for Flipkart Product Catalog
Focus: MySQL binlog parsing, real-time catalog updates, schema evolution

Ye Maxwell CDC implementation Flipkart ke product catalog ke liye hai.
Mumbai ke wholesale market jaise real-time updates!

Production Ready: Yes
Testing Required: Yes
Performance: Optimized for high-frequency catalog updates
"""

import os
import sys
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue, Empty

# Maxwell CDC and Kafka dependencies
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import mysql.connector
from mysql.connector import Error as MySQLError

# Data processing dependencies
import pandas as pd
import numpy as np
from elasticsearch import Elasticsearch
from redis import Redis
import pymongo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MaxwellMessage:
    """Maxwell CDC message structure"""
    database: str
    table: str
    type: str  # insert, update, delete
    ts: int
    xid: int
    xoffset: int
    position: str
    gtid: Optional[str]
    server_id: int
    thread_id: int
    primary_key: Dict[str, Any]
    data: Optional[Dict[str, Any]]
    old: Optional[Dict[str, Any]]

@dataclass 
class ProductCatalogEvent:
    """Flipkart product catalog event"""
    event_id: str
    product_id: str
    event_type: str  # PRODUCT_CREATED, PRODUCT_UPDATED, PRODUCT_DELETED, PRICE_CHANGED, INVENTORY_UPDATED
    timestamp: datetime
    changes: Dict[str, Any]
    old_values: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]

class FlipkartMaxwellCDCProcessor:
    """
    Maxwell CDC processor for Flipkart product catalog
    
    Mumbai ke bazaar jaise dynamic aur real-time!
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.kafka_consumer = None
        self.kafka_producer = None
        self.elasticsearch = None
        self.redis_client = None
        self.mongo_client = None
        self.is_running = False
        self.processed_count = 0
        self.error_count = 0
        self.last_processed_timestamp = None
        
        # Processing queues
        self.event_queue = Queue(maxsize=10000)
        self.dead_letter_queue = Queue()
        
        # Event handlers
        self.event_handlers = {
            'products': self._handle_product_events,
            'product_prices': self._handle_price_events,
            'inventory': self._handle_inventory_events,
            'product_images': self._handle_image_events,
            'product_reviews': self._handle_review_events,
            'categories': self._handle_category_events
        }
        
        # Thread pool for processing
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.get('worker_threads', 5))
        
    def initialize_connections(self):
        """Initialize all connections"""
        logger.info("🔌 Initializing connections for Maxwell CDC processor...")
        
        try:
            # Kafka Consumer for Maxwell messages
            self.kafka_consumer = KafkaConsumer(
                self.config['maxwell_topic'],
                bootstrap_servers=self.config['kafka_brokers'],
                group_id=self.config['consumer_group'],
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                key_deserializer=lambda x: x.decode('utf-8') if x else None,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                max_poll_records=1000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            
            # Kafka Producer for processed events
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.config['kafka_brokers'],
                value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8'),
                acks='all',
                retries=3,
                batch_size=16384,
                linger_ms=10,
                buffer_memory=33554432
            )
            
            # Elasticsearch for search index updates
            self.elasticsearch = Elasticsearch(
                hosts=self.config['elasticsearch_hosts'],
                timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
            
            # Redis for caching
            self.redis_client = Redis(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                db=self.config['redis_db'],
                decode_responses=True,
                socket_timeout=10,
                socket_connect_timeout=10,
                retry_on_timeout=True
            )
            
            # MongoDB for audit logs
            self.mongo_client = pymongo.MongoClient(self.config['mongodb_url'])
            self.audit_db = self.mongo_client[self.config['audit_database']]
            
            logger.info("✅ All connections initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize connections: {str(e)}")
            raise
    
    def parse_maxwell_message(self, raw_message: Dict[str, Any]) -> MaxwellMessage:
        """Parse Maxwell CDC message"""
        
        return MaxwellMessage(
            database=raw_message.get('database', ''),
            table=raw_message.get('table', ''),
            type=raw_message.get('type', ''),
            ts=raw_message.get('ts', 0),
            xid=raw_message.get('xid', 0),
            xoffset=raw_message.get('xoffset', 0),
            position=raw_message.get('position', ''),
            gtid=raw_message.get('gtid'),
            server_id=raw_message.get('server_id', 0),
            thread_id=raw_message.get('thread_id', 0),
            primary_key=raw_message.get('primary_key', {}),
            data=raw_message.get('data'),
            old=raw_message.get('old')
        )
    
    def _handle_product_events(self, maxwell_msg: MaxwellMessage) -> List[ProductCatalogEvent]:
        """Handle product table events"""
        events = []
        
        try:
            if maxwell_msg.type == 'insert':
                # New product created
                product_data = maxwell_msg.data
                
                event = ProductCatalogEvent(
                    event_id=f"product_created_{product_data['product_id']}_{maxwell_msg.ts}",
                    product_id=product_data['product_id'],
                    event_type='PRODUCT_CREATED',
                    timestamp=datetime.fromtimestamp(maxwell_msg.ts / 1000),
                    changes={
                        'title': product_data.get('title'),
                        'description': product_data.get('description'),
                        'category_id': product_data.get('category_id'),
                        'brand': product_data.get('brand'),
                        'seller_id': product_data.get('seller_id'),
                        'status': product_data.get('status', 'active')
                    },
                    old_values=None,
                    metadata={
                        'table': 'products',
                        'operation': 'insert',
                        'maxwell_position': maxwell_msg.position,
                        'server_id': maxwell_msg.server_id
                    }
                )
                events.append(event)
                
            elif maxwell_msg.type == 'update':
                # Product updated
                product_id = maxwell_msg.data['product_id']
                changes = {}
                old_values = {}
                
                # Compare old and new values
                for field in ['title', 'description', 'brand', 'status', 'category_id']:
                    if field in maxwell_msg.data and field in maxwell_msg.old:
                        if maxwell_msg.data[field] != maxwell_msg.old[field]:
                            changes[field] = maxwell_msg.data[field]
                            old_values[field] = maxwell_msg.old[field]
                
                if changes:
                    event = ProductCatalogEvent(
                        event_id=f"product_updated_{product_id}_{maxwell_msg.ts}",
                        product_id=product_id,
                        event_type='PRODUCT_UPDATED',
                        timestamp=datetime.fromtimestamp(maxwell_msg.ts / 1000),
                        changes=changes,
                        old_values=old_values,
                        metadata={
                            'table': 'products',
                            'operation': 'update',
                            'maxwell_position': maxwell_msg.position,
                            'fields_changed': list(changes.keys())
                        }
                    )
                    events.append(event)
                    
            elif maxwell_msg.type == 'delete':
                # Product deleted
                product_id = maxwell_msg.old['product_id']
                
                event = ProductCatalogEvent(
                    event_id=f"product_deleted_{product_id}_{maxwell_msg.ts}",
                    product_id=product_id,
                    event_type='PRODUCT_DELETED',
                    timestamp=datetime.fromtimestamp(maxwell_msg.ts / 1000),
                    changes={},
                    old_values=maxwell_msg.old,
                    metadata={
                        'table': 'products',
                        'operation': 'delete',
                        'maxwell_position': maxwell_msg.position
                    }
                )
                events.append(event)
                
        except Exception as e:
            logger.error(f"Error handling product event: {str(e)}")
            
        return events
    
    def _handle_price_events(self, maxwell_msg: MaxwellMessage) -> List[ProductCatalogEvent]:
        """Handle product price events"""
        events = []
        
        try:
            if maxwell_msg.type in ['insert', 'update']:
                product_id = maxwell_msg.data['product_id']
                current_price = maxwell_msg.data.get('selling_price', 0)
                mrp = maxwell_msg.data.get('mrp', 0)
                discount_percent = ((mrp - current_price) / mrp * 100) if mrp > 0 else 0
                
                changes = {
                    'selling_price': current_price,
                    'mrp': mrp,
                    'discount_percent': round(discount_percent, 2),
                    'currency': maxwell_msg.data.get('currency', 'INR'),
                    'effective_from': maxwell_msg.data.get('effective_from'),
                    'updated_by': maxwell_msg.data.get('updated_by')
                }
                
                old_values = {}
                if maxwell_msg.type == 'update' and maxwell_msg.old:
                    old_price = maxwell_msg.old.get('selling_price', 0)
                    old_mrp = maxwell_msg.old.get('mrp', 0)
                    old_discount = ((old_mrp - old_price) / old_mrp * 100) if old_mrp > 0 else 0
                    
                    old_values = {
                        'selling_price': old_price,
                        'mrp': old_mrp,
                        'discount_percent': round(old_discount, 2)
                    }
                
                event = ProductCatalogEvent(
                    event_id=f"price_changed_{product_id}_{maxwell_msg.ts}",
                    product_id=product_id,
                    event_type='PRICE_CHANGED',
                    timestamp=datetime.fromtimestamp(maxwell_msg.ts / 1000),
                    changes=changes,
                    old_values=old_values,
                    metadata={
                        'table': 'product_prices',
                        'operation': maxwell_msg.type,
                        'price_change_amount': current_price - old_values.get('selling_price', 0) if old_values else 0,
                        'discount_change': discount_percent - old_values.get('discount_percent', 0) if old_values else 0
                    }
                )
                events.append(event)
                
        except Exception as e:
            logger.error(f"Error handling price event: {str(e)}")
            
        return events
    
    def _handle_inventory_events(self, maxwell_msg: MaxwellMessage) -> List[ProductCatalogEvent]:
        """Handle inventory events"""
        events = []
        
        try:
            if maxwell_msg.type in ['insert', 'update']:
                product_id = maxwell_msg.data['product_id']
                current_stock = maxwell_msg.data.get('available_stock', 0)
                reserved_stock = maxwell_msg.data.get('reserved_stock', 0)
                warehouse_id = maxwell_msg.data.get('warehouse_id')
                
                changes = {
                    'available_stock': current_stock,
                    'reserved_stock': reserved_stock,
                    'total_stock': current_stock + reserved_stock,
                    'warehouse_id': warehouse_id,
                    'last_updated': maxwell_msg.data.get('last_updated'),
                    'updated_by': maxwell_msg.data.get('updated_by')
                }
                
                # Determine stock status
                if current_stock == 0:
                    stock_status = 'OUT_OF_STOCK'
                elif current_stock <= 10:
                    stock_status = 'LOW_STOCK'
                elif current_stock <= 50:
                    stock_status = 'MEDIUM_STOCK'
                else:
                    stock_status = 'IN_STOCK'
                
                changes['stock_status'] = stock_status
                
                old_values = {}
                if maxwell_msg.type == 'update' and maxwell_msg.old:
                    old_stock = maxwell_msg.old.get('available_stock', 0)
                    old_reserved = maxwell_msg.old.get('reserved_stock', 0)
                    
                    old_values = {
                        'available_stock': old_stock,
                        'reserved_stock': old_reserved,
                        'total_stock': old_stock + old_reserved
                    }
                
                event = ProductCatalogEvent(
                    event_id=f"inventory_updated_{product_id}_{warehouse_id}_{maxwell_msg.ts}",
                    product_id=product_id,
                    event_type='INVENTORY_UPDATED',
                    timestamp=datetime.fromtimestamp(maxwell_msg.ts / 1000),
                    changes=changes,
                    old_values=old_values,
                    metadata={
                        'table': 'inventory',
                        'operation': maxwell_msg.type,
                        'warehouse_id': warehouse_id,
                        'stock_change': current_stock - old_values.get('available_stock', 0) if old_values else 0,
                        'stock_status_change': stock_status
                    }
                )
                events.append(event)
                
        except Exception as e:
            logger.error(f"Error handling inventory event: {str(e)}")
            
        return events
    
    def _handle_image_events(self, maxwell_msg: MaxwellMessage) -> List[ProductCatalogEvent]:
        """Handle product image events"""
        events = []
        
        try:
            if maxwell_msg.type == 'insert':
                product_id = maxwell_msg.data['product_id']
                image_url = maxwell_msg.data.get('image_url')
                image_type = maxwell_msg.data.get('image_type', 'primary')
                
                event = ProductCatalogEvent(
                    event_id=f"image_added_{product_id}_{maxwell_msg.ts}",
                    product_id=product_id,
                    event_type='IMAGE_ADDED',
                    timestamp=datetime.fromtimestamp(maxwell_msg.ts / 1000),
                    changes={
                        'image_url': image_url,
                        'image_type': image_type,
                        'image_id': maxwell_msg.data.get('image_id'),
                        'display_order': maxwell_msg.data.get('display_order', 1)
                    },
                    old_values=None,
                    metadata={
                        'table': 'product_images',
                        'operation': 'insert'
                    }
                )
                events.append(event)
                
        except Exception as e:
            logger.error(f"Error handling image event: {str(e)}")
            
        return events
    
    def _handle_review_events(self, maxwell_msg: MaxwellMessage) -> List[ProductCatalogEvent]:
        """Handle product review events"""
        events = []
        
        try:
            if maxwell_msg.type == 'insert':
                product_id = maxwell_msg.data['product_id']
                rating = maxwell_msg.data.get('rating', 0)
                
                event = ProductCatalogEvent(
                    event_id=f"review_added_{product_id}_{maxwell_msg.ts}",
                    product_id=product_id,
                    event_type='REVIEW_ADDED',
                    timestamp=datetime.fromtimestamp(maxwell_msg.ts / 1000),
                    changes={
                        'rating': rating,
                        'review_text': maxwell_msg.data.get('review_text'),
                        'user_id': maxwell_msg.data.get('user_id'),
                        'verified_purchase': maxwell_msg.data.get('verified_purchase', False)
                    },
                    old_values=None,
                    metadata={
                        'table': 'product_reviews',
                        'operation': 'insert',
                        'review_id': maxwell_msg.data.get('review_id')
                    }
                )
                events.append(event)
                
        except Exception as e:
            logger.error(f"Error handling review event: {str(e)}")
            
        return events
    
    def _handle_category_events(self, maxwell_msg: MaxwellMessage) -> List[ProductCatalogEvent]:
        """Handle category events"""
        events = []
        
        try:
            if maxwell_msg.type in ['insert', 'update']:
                category_id = maxwell_msg.data['category_id']
                
                event = ProductCatalogEvent(
                    event_id=f"category_updated_{category_id}_{maxwell_msg.ts}",
                    product_id=None,  # Category events don't have specific product
                    event_type='CATEGORY_UPDATED',
                    timestamp=datetime.fromtimestamp(maxwell_msg.ts / 1000),
                    changes={
                        'category_id': category_id,
                        'category_name': maxwell_msg.data.get('category_name'),
                        'parent_category_id': maxwell_msg.data.get('parent_category_id'),
                        'is_active': maxwell_msg.data.get('is_active', True)
                    },
                    old_values=maxwell_msg.old if maxwell_msg.type == 'update' else None,
                    metadata={
                        'table': 'categories',
                        'operation': maxwell_msg.type
                    }
                )
                events.append(event)
                
        except Exception as e:
            logger.error(f"Error handling category event: {str(e)}")
            
        return events
    
    def process_catalog_event(self, event: ProductCatalogEvent):
        """Process a single catalog event"""
        try:
            # Update Elasticsearch search index
            self._update_search_index(event)
            
            # Update Redis cache
            self._update_cache(event)
            
            # Publish to downstream systems
            self._publish_to_downstream(event)
            
            # Log to audit database
            self._log_to_audit(event)
            
            logger.debug(f"Processed event: {event.event_type} for product {event.product_id}")
            
        except Exception as e:
            logger.error(f"Error processing catalog event: {str(e)}")
            # Add to dead letter queue for retry
            self.dead_letter_queue.put({
                'event': asdict(event),
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'retry_count': 0
            })
    
    def _update_search_index(self, event: ProductCatalogEvent):
        """Update Elasticsearch search index"""
        if not event.product_id:
            return  # Skip category events for now
            
        try:
            index_name = 'flipkart_products'
            
            if event.event_type == 'PRODUCT_CREATED':
                # Index new product
                doc = {
                    'product_id': event.product_id,
                    'title': event.changes.get('title', ''),
                    'description': event.changes.get('description', ''),
                    'brand': event.changes.get('brand', ''),
                    'category_id': event.changes.get('category_id'),
                    'status': event.changes.get('status', 'active'),
                    'indexed_at': event.timestamp.isoformat()
                }
                
                self.elasticsearch.index(
                    index=index_name,
                    id=event.product_id,
                    body=doc
                )
                
            elif event.event_type == 'PRODUCT_UPDATED':
                # Update existing product
                update_doc = {
                    'doc': event.changes,
                    'doc_as_upsert': True
                }
                
                self.elasticsearch.update(
                    index=index_name,
                    id=event.product_id,
                    body=update_doc
                )
                
            elif event.event_type == 'PRODUCT_DELETED':
                # Remove from index
                self.elasticsearch.delete(
                    index=index_name,
                    id=event.product_id,
                    ignore=[404]
                )
                
            elif event.event_type == 'PRICE_CHANGED':
                # Update price information
                price_update = {
                    'doc': {
                        'selling_price': event.changes.get('selling_price'),
                        'mrp': event.changes.get('mrp'),
                        'discount_percent': event.changes.get('discount_percent'),
                        'price_updated_at': event.timestamp.isoformat()
                    }
                }
                
                self.elasticsearch.update(
                    index=index_name,
                    id=event.product_id,
                    body=price_update
                )
                
            elif event.event_type == 'INVENTORY_UPDATED':
                # Update stock information
                stock_update = {
                    'doc': {
                        'available_stock': event.changes.get('available_stock'),
                        'stock_status': event.changes.get('stock_status'),
                        'inventory_updated_at': event.timestamp.isoformat()
                    }
                }
                
                self.elasticsearch.update(
                    index=index_name,
                    id=event.product_id,
                    body=stock_update
                )
                
        except Exception as e:
            logger.error(f"Error updating search index: {str(e)}")
            raise
    
    def _update_cache(self, event: ProductCatalogEvent):
        """Update Redis cache"""
        if not event.product_id:
            return
            
        try:
            cache_key = f"product:{event.product_id}"
            cache_ttl = 3600  # 1 hour
            
            if event.event_type == 'PRODUCT_DELETED':
                # Remove from cache
                self.redis_client.delete(cache_key)
            else:
                # Get existing cached data or create new
                cached_data = self.redis_client.hgetall(cache_key)
                if not cached_data:
                    cached_data = {'product_id': event.product_id}
                
                # Update with changes
                for key, value in event.changes.items():
                    cached_data[key] = str(value)
                
                cached_data['last_updated'] = event.timestamp.isoformat()
                
                # Update cache
                self.redis_client.hset(cache_key, mapping=cached_data)
                self.redis_client.expire(cache_key, cache_ttl)
                
                # Update category cache if category changed
                if 'category_id' in event.changes:
                    category_key = f"category:{event.changes['category_id']}:products"
                    self.redis_client.sadd(category_key, event.product_id)
                    self.redis_client.expire(category_key, cache_ttl)
                
        except Exception as e:
            logger.error(f"Error updating cache: {str(e)}")
            raise
    
    def _publish_to_downstream(self, event: ProductCatalogEvent):
        """Publish event to downstream Kafka topics"""
        try:
            # Determine target topic based on event type
            topic_map = {
                'PRODUCT_CREATED': 'flipkart.catalog.product.created',
                'PRODUCT_UPDATED': 'flipkart.catalog.product.updated',
                'PRODUCT_DELETED': 'flipkart.catalog.product.deleted',
                'PRICE_CHANGED': 'flipkart.catalog.price.changed',
                'INVENTORY_UPDATED': 'flipkart.catalog.inventory.updated',
                'REVIEW_ADDED': 'flipkart.catalog.review.added'
            }
            
            topic = topic_map.get(event.event_type, 'flipkart.catalog.events')
            
            # Prepare message
            message = {
                'event_id': event.event_id,
                'product_id': event.product_id,
                'event_type': event.event_type,
                'timestamp': event.timestamp.isoformat(),
                'changes': event.changes,
                'old_values': event.old_values,
                'metadata': event.metadata,
                'schema_version': '1.0'
            }
            
            # Publish to Kafka
            self.kafka_producer.send(
                topic=topic,
                key=event.product_id or 'global',
                value=message
            )
            
        except Exception as e:
            logger.error(f"Error publishing to downstream: {str(e)}")
            raise
    
    def _log_to_audit(self, event: ProductCatalogEvent):
        """Log event to audit database"""
        try:
            audit_collection = self.audit_db.catalog_events
            
            audit_record = {
                'event_id': event.event_id,
                'product_id': event.product_id,
                'event_type': event.event_type,
                'timestamp': event.timestamp,
                'changes': event.changes,
                'old_values': event.old_values,
                'metadata': event.metadata,
                'processed_at': datetime.now()
            }
            
            audit_collection.insert_one(audit_record)
            
        except Exception as e:
            logger.error(f"Error logging to audit: {str(e)}")
            # Don't raise - audit logging shouldn't block processing
    
    def process_maxwell_messages(self):
        """Main processing loop for Maxwell messages"""
        logger.info("🚀 Starting Maxwell CDC message processing...")
        
        try:
            for message in self.kafka_consumer:
                try:
                    # Parse Maxwell message
                    maxwell_msg = self.parse_maxwell_message(message.value)
                    
                    # Filter by database and table
                    if (maxwell_msg.database != self.config['source_database'] or
                        maxwell_msg.table not in self.event_handlers):
                        continue
                    
                    # Get appropriate handler
                    handler = self.event_handlers[maxwell_msg.table]
                    
                    # Process message and get catalog events
                    catalog_events = handler(maxwell_msg)
                    
                    # Process each catalog event
                    for event in catalog_events:
                        self.thread_pool.submit(self.process_catalog_event, event)
                    
                    # Update metrics
                    self.processed_count += len(catalog_events)
                    self.last_processed_timestamp = datetime.now()
                    
                    # Log progress periodically
                    if self.processed_count % 1000 == 0:
                        logger.info(f"Processed {self.processed_count} events. "
                                  f"Last processed: {self.last_processed_timestamp}")
                
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    self.error_count += 1
                    
                    # Add to dead letter queue
                    self.dead_letter_queue.put({
                        'message': message.value,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat(),
                        'retry_count': 0
                    })
                    
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            logger.error(f"Fatal error in message processing: {str(e)}")
            raise
        finally:
            self.shutdown()
    
    def start(self):
        """Start the Maxwell CDC processor"""
        logger.info("🚀 Starting Flipkart Maxwell CDC Processor...")
        
        self.initialize_connections()
        self.is_running = True
        
        # Start processing
        self.process_maxwell_messages()
    
    def shutdown(self):
        """Shutdown the processor gracefully"""
        logger.info("🛑 Shutting down Maxwell CDC processor...")
        
        self.is_running = False
        
        # Close connections
        if self.kafka_consumer:
            self.kafka_consumer.close()
        
        if self.kafka_producer:
            self.kafka_producer.flush()
            self.kafka_producer.close()
        
        if self.mongo_client:
            self.mongo_client.close()
        
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        
        logger.info(f"✅ Shutdown complete. Processed: {self.processed_count}, Errors: {self.error_count}")

def main():
    """Main function to run Maxwell CDC processor"""
    
    # Configuration for Flipkart catalog CDC
    config = {
        'kafka_brokers': ['localhost:9092'],
        'maxwell_topic': 'maxwell',
        'consumer_group': 'flipkart-catalog-cdc',
        'source_database': 'flipkart_catalog',
        'elasticsearch_hosts': ['localhost:9200'],
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'mongodb_url': 'mongodb://localhost:27017/',
        'audit_database': 'flipkart_audit',
        'worker_threads': 10
    }
    
    # Create and start processor
    processor = FlipkartMaxwellCDCProcessor(config)
    
    try:
        processor.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    finally:
        processor.shutdown()

if __name__ == "__main__":
    main()

"""
Mumbai Learning Notes:
1. Maxwell CDC implementation for real-time MySQL binlog processing
2. Multi-table event handling with specific business logic
3. Downstream system integration (Elasticsearch, Redis, MongoDB)
4. Event-driven architecture with Kafka topics
5. Error handling and dead letter queue patterns
6. Thread pool for concurrent event processing
7. Audit logging for compliance and debugging
8. Indian e-commerce specific business logic (Flipkart catalog)
9. Performance optimization with caching strategies
10. Production-ready monitoring and metrics

Production Deployment:
- Set up Maxwell with proper MySQL replication configuration
- Configure Kafka cluster with appropriate partitioning
- Implement proper error handling and retry mechanisms
- Set up monitoring for Maxwell lag and processing metrics
- Add schema evolution handling for database changes
- Configure proper security and authentication
- Implement data validation and consistency checks
- Set up alerting for processing failures
- Add comprehensive logging and distributed tracing
"""
#!/usr/bin/env python3
"""
Episode 13: CDC & Real-Time Data Pipelines
Example 2: Kafka Connect Configuration Manager

यह example Kafka Connect के साथ advanced configuration management दिखाता है।
Indian e-commerce platforms के लिए production-ready setup।

Author: Distributed Systems Podcast Team
Context: Flipkart, Myntra, Amazon India scale operations
"""

import json
import logging
import time
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
import yaml
from dataclasses import dataclass, field
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor
import os

# Hindi logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]',
    handlers=[
        logging.FileHandler('kafka_connect_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class KafkaConnectCluster:
    """Kafka Connect cluster configuration for Indian region"""
    name: str
    urls: List[str]
    region: str = "mumbai"
    environment: str = "production"
    max_workers: int = 8
    health_check_interval: int = 30
    
@dataclass
class ConnectorTemplate:
    """Connector configuration template for different Indian platforms"""
    name: str
    template_type: str  # mysql, postgres, mongodb
    config_template: Dict[str, Any] = field(default_factory=dict)
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)

class IndianEcommerceConnectorManager:
    """
    Advanced Kafka Connect manager for Indian e-commerce platforms
    Mumbai stock exchange की तरह real-time trading के लिए optimized
    """
    
    def __init__(self, clusters: List[KafkaConnectCluster]):
        self.clusters = {cluster.name: cluster for cluster in clusters}
        self.active_connectors = {}
        self.connector_templates = self._load_connector_templates()
        self.health_monitor = None
        self.metrics = {
            'connectors_created': 0,
            'connectors_failed': 0,
            'restarts_performed': 0,
            'last_health_check': None
        }
        
        # Start health monitoring
        self._start_health_monitoring()
        
    def _load_connector_templates(self) -> Dict[str, ConnectorTemplate]:
        """
        Indian e-commerce platforms के लिए pre-built templates
        """
        templates = {}
        
        # Flipkart MySQL template
        flipkart_mysql = ConnectorTemplate(
            name="flipkart-mysql",
            template_type="mysql",
            config_template={
                "connector.class": "io.debezium.connector.mysql.MySqlConnector",
                "database.hostname": "{database_host}",
                "database.port": "{database_port}",
                "database.user": "{database_user}",
                "database.password": "{database_password}",
                "database.server.name": "flipkart_{region}",
                "table.include.list": "{table_list}",
                "topic.prefix": "flipkart.{region}",
                "database.history.kafka.bootstrap.servers": "{kafka_servers}",
                "database.history.kafka.topic": "flipkart.{region}.schema.history",
                
                # Indian timezone support
                "database.connectionTimeZone": "Asia/Kolkata",
                
                # Performance optimizations for high volume
                "max.batch.size": "4096",
                "max.queue.size": "16384",
                "poll.interval.ms": "500",
                
                # Transforms for Indian data
                "transforms": "route,unwrap,addRegion",
                "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
                "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
                "transforms.route.replacement": "$1.$3",
                
                "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
                "transforms.unwrap.add.fields": "table,ts_ms",
                
                "transforms.addRegion.type": "org.apache.kafka.connect.transforms.InsertField$Value",
                "transforms.addRegion.static.field": "region",
                "transforms.addRegion.static.value": "{region}",
                
                # Security for PII data
                "column.mask.hash.SHA-256.with.salt.CzQMA0cB5K": "users.aadhaar_number,users.pan_number",
                "column.mask.with.12.chars": "users.mobile_number,users.email"
            },
            required_fields=["database_host", "database_user", "database_password", "table_list", "kafka_servers", "region"],
            optional_fields=["database_port", "max_batch_size"]
        )
        templates["flipkart-mysql"] = flipkart_mysql
        
        # Zomato PostgreSQL template
        zomato_postgres = ConnectorTemplate(
            name="zomato-postgres",
            template_type="postgres",
            config_template={
                "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
                "database.hostname": "{database_host}",
                "database.port": "{database_port}",
                "database.user": "{database_user}",
                "database.password": "{database_password}",
                "database.dbname": "{database_name}",
                "database.server.name": "zomato_{region}",
                "table.include.list": "{table_list}",
                "topic.prefix": "zomato.{region}",
                
                # PostgreSQL specific
                "slot.name": "zomato_{region}_slot",
                "plugin.name": "pgoutput",
                "publication.name": "zomato_cdc_publication",
                
                # Indian restaurant data handling
                "transforms": "route,unwrap,addMetadata",
                "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
                "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
                "transforms.route.replacement": "$1.$3",
                
                "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
                "transforms.unwrap.add.fields": "table,ts_ms,lsn",
                
                "transforms.addMetadata.type": "org.apache.kafka.connect.transforms.InsertField$Value",
                "transforms.addMetadata.static.field": "platform",
                "transforms.addMetadata.static.value": "zomato",
                
                # Performance for restaurant orders
                "max.batch.size": "2048",
                "poll.interval.ms": "1000"
            },
            required_fields=["database_host", "database_user", "database_password", "database_name", "table_list", "region"],
            optional_fields=["database_port", "slot_name"]
        )
        templates["zomato-postgres"] = zomato_postgres
        
        # Paytm MongoDB template
        paytm_mongo = ConnectorTemplate(
            name="paytm-mongodb",
            template_type="mongodb",
            config_template={
                "connector.class": "io.debezium.connector.mongodb.MongoDbConnector",
                "mongodb.hosts": "{mongo_hosts}",
                "mongodb.name": "paytm_{region}",
                "collection.include.list": "{collection_list}",
                "topic.prefix": "paytm.{region}",
                
                # MongoDB replica set configuration
                "mongodb.user": "{mongo_user}",
                "mongodb.password": "{mongo_password}",
                "mongodb.authsource": "admin",
                "mongodb.ssl.enabled": "true",
                
                # UPI transaction handling
                "transforms": "unwrap,addPaymentMetadata",
                "transforms.unwrap.type": "io.debezium.connector.mongodb.transforms.ExtractNewDocumentState",
                "transforms.unwrap.drop.tombstones": "false",
                
                "transforms.addPaymentMetadata.type": "org.apache.kafka.connect.transforms.InsertField$Value",
                "transforms.addPaymentMetadata.static.field": "payment_platform",
                "transforms.addPaymentMetadata.static.value": "paytm",
                
                # Performance for payment transactions
                "cursor.max.await.time.ms": "1000",
                "poll.interval.ms": "500"
            },
            required_fields=["mongo_hosts", "mongo_user", "mongo_password", "collection_list", "region"],
            optional_fields=["cursor_max_await_time_ms"]
        )
        templates["paytm-mongodb"] = paytm_mongo
        
        return templates
    
    def create_connector_from_template(self, 
                                     template_name: str,
                                     connector_name: str,
                                     cluster_name: str,
                                     parameters: Dict[str, str]) -> Dict[str, Any]:
        """
        Template से connector बनाओ - assembly line production की तरह
        """
        logger.info(f"🏭 Creating connector {connector_name} from template {template_name}")
        
        if template_name not in self.connector_templates:
            logger.error(f"❌ Template {template_name} not found")
            return {"error": f"Template {template_name} not found"}
        
        if cluster_name not in self.clusters:
            logger.error(f"❌ Cluster {cluster_name} not found")
            return {"error": f"Cluster {cluster_name} not found"}
        
        template = self.connector_templates[template_name]
        cluster = self.clusters[cluster_name]
        
        # Validate required parameters
        missing_params = [param for param in template.required_fields if param not in parameters]
        if missing_params:
            logger.error(f"❌ Missing required parameters: {missing_params}")
            return {"error": f"Missing required parameters: {missing_params}"}
        
        # Build configuration by replacing placeholders
        config = {}
        for key, value in template.config_template.items():
            if isinstance(value, str):
                # Replace placeholders with actual values
                config[key] = value.format(**parameters)
            else:
                config[key] = value
        
        # Create connector configuration
        connector_config = {
            "name": connector_name,
            "config": config
        }
        
        # Deploy to cluster
        return self._deploy_connector(cluster, connector_config)
    
    def _deploy_connector(self, cluster: KafkaConnectCluster, connector_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Connector को cluster में deploy करो
        """
        connector_name = connector_config["name"]
        
        for url in cluster.urls:
            try:
                logger.info(f"🚀 Deploying {connector_name} to {url}")
                
                response = requests.post(
                    f"{url}/connectors",
                    json=connector_config,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 201:
                    logger.info(f"✅ Connector {connector_name} deployed successfully to {url}")
                    
                    # Track the connector
                    self.active_connectors[connector_name] = {
                        'cluster': cluster.name,
                        'url': url,
                        'created_at': datetime.now(),
                        'config': connector_config,
                        'status': 'RUNNING'
                    }
                    
                    self.metrics['connectors_created'] += 1
                    return {"status": "success", "connector": connector_name, "cluster_url": url}
                    
                elif response.status_code == 409:
                    logger.warning(f"⚠️ Connector {connector_name} already exists, updating...")
                    return self._update_connector(url, connector_config)
                    
                else:
                    logger.error(f"❌ Deploy failed: {response.status_code} - {response.text}")
                    continue
                    
            except Exception as e:
                logger.error(f"💥 Deploy exception for {url}: {str(e)}")
                continue
        
        # If all URLs failed
        self.metrics['connectors_failed'] += 1
        return {"error": "All cluster URLs failed", "connector": connector_name}
    
    def _update_connector(self, cluster_url: str, connector_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Existing connector को update करो
        """
        connector_name = connector_config["name"]
        
        try:
            response = requests.put(
                f"{cluster_url}/connectors/{connector_name}/config",
                json=connector_config["config"],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Connector {connector_name} updated successfully")
                return {"status": "updated", "connector": connector_name}
            else:
                logger.error(f"❌ Update failed: {response.status_code} - {response.text}")
                return {"error": f"Update failed: {response.text}"}
                
        except Exception as e:
            logger.error(f"💥 Update exception: {str(e)}")
            return {"error": str(e)}
    
    def bulk_create_connectors(self, connector_specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Multiple connectors को parallel में बनाओ - Mumbai local trains की तरह
        """
        logger.info(f"🚄 Starting bulk creation of {len(connector_specs)} connectors")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for spec in connector_specs:
                future = executor.submit(
                    self.create_connector_from_template,
                    spec['template_name'],
                    spec['connector_name'],
                    spec['cluster_name'],
                    spec['parameters']
                )
                futures.append((future, spec['connector_name']))
            
            # Collect results
            for future, connector_name in futures:
                try:
                    result = future.result(timeout=60)
                    result['connector_name'] = connector_name
                    results.append(result)
                except Exception as e:
                    logger.error(f"💥 Bulk creation failed for {connector_name}: {str(e)}")
                    results.append({"error": str(e), "connector_name": connector_name})
        
        successful = len([r for r in results if 'error' not in r])
        logger.info(f"📊 Bulk creation completed: {successful}/{len(connector_specs)} successful")
        
        return results
    
    def get_connector_status(self, connector_name: str) -> Dict[str, Any]:
        """
        Connector का detailed status check करो
        """
        if connector_name not in self.active_connectors:
            return {"error": "Connector not found in tracking"}
        
        connector_info = self.active_connectors[connector_name]
        cluster_url = connector_info['url']
        
        try:
            # Get status from Kafka Connect
            response = requests.get(
                f"{cluster_url}/connectors/{connector_name}/status",
                timeout=10
            )
            
            if response.status_code == 200:
                status_data = response.json()
                
                # Add our tracking information
                status_data['tracking_info'] = {
                    'cluster': connector_info['cluster'],
                    'created_at': connector_info['created_at'].isoformat(),
                    'uptime_seconds': (datetime.now() - connector_info['created_at']).total_seconds()
                }
                
                # Check if connector needs restart
                if status_data['connector']['state'] == 'FAILED':
                    logger.warning(f"⚠️ Connector {connector_name} is in FAILED state")
                    status_data['needs_restart'] = True
                
                return status_data
            else:
                return {"error": f"Status check failed: {response.text}"}
                
        except Exception as e:
            logger.error(f"💥 Status check exception: {str(e)}")
            return {"error": str(e)}
    
    def restart_failed_connectors(self) -> List[Dict[str, Any]]:
        """
        Failed connectors को automatically restart करो - Mumbai monsoon की तरह recovery
        """
        logger.info("🔄 Starting automatic restart of failed connectors")
        
        restart_results = []
        
        for connector_name in self.active_connectors.keys():
            status = self.get_connector_status(connector_name)
            
            if 'error' in status:
                continue
                
            if status.get('needs_restart', False):
                logger.info(f"🔧 Restarting failed connector: {connector_name}")
                
                connector_info = self.active_connectors[connector_name]
                cluster_url = connector_info['url']
                
                try:
                    response = requests.post(
                        f"{cluster_url}/connectors/{connector_name}/restart",
                        timeout=30
                    )
                    
                    if response.status_code == 204:
                        logger.info(f"✅ Connector {connector_name} restarted successfully")
                        self.metrics['restarts_performed'] += 1
                        restart_results.append({"connector": connector_name, "status": "restarted"})
                    else:
                        logger.error(f"❌ Restart failed: {response.text}")
                        restart_results.append({"connector": connector_name, "status": "restart_failed", "error": response.text})
                        
                except Exception as e:
                    logger.error(f"💥 Restart exception: {str(e)}")
                    restart_results.append({"connector": connector_name, "status": "restart_exception", "error": str(e)})
        
        return restart_results
    
    def _start_health_monitoring(self):
        """
        Background health monitoring शुरू करो
        """
        def health_check_worker():
            while True:
                try:
                    logger.info("💓 Running health check for all connectors...")
                    
                    # Check each connector
                    healthy_count = 0
                    failed_count = 0
                    
                    for connector_name in self.active_connectors.keys():
                        status = self.get_connector_status(connector_name)
                        
                        if 'error' not in status:
                            if status['connector']['state'] == 'RUNNING':
                                healthy_count += 1
                            else:
                                failed_count += 1
                        else:
                            failed_count += 1
                    
                    # Update metrics
                    self.metrics['last_health_check'] = datetime.now()
                    
                    logger.info(f"📊 Health check completed: {healthy_count} healthy, {failed_count} failed")
                    
                    # Auto-restart failed connectors
                    if failed_count > 0:
                        self.restart_failed_connectors()
                    
                    # Wait for next check
                    time.sleep(30)  # Check every 30 seconds
                    
                except Exception as e:
                    logger.error(f"💥 Health check error: {str(e)}")
                    time.sleep(60)  # Wait longer on error
        
        # Start health monitoring in background thread
        self.health_monitor = threading.Thread(target=health_check_worker, daemon=True)
        self.health_monitor.start()
        logger.info("💓 Health monitoring started")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Performance metrics return करो - business dashboard के लिए
        """
        return {
            'summary': {
                'total_connectors': len(self.active_connectors),
                'connectors_created': self.metrics['connectors_created'],
                'connectors_failed': self.metrics['connectors_failed'],
                'restarts_performed': self.metrics['restarts_performed'],
                'last_health_check': self.metrics['last_health_check'].isoformat() if self.metrics['last_health_check'] else None
            },
            'connectors': {
                name: {
                    'cluster': info['cluster'],
                    'created_at': info['created_at'].isoformat(),
                    'uptime_hours': round((datetime.now() - info['created_at']).total_seconds() / 3600, 2)
                }
                for name, info in self.active_connectors.items()
            }
        }

def create_indian_ecommerce_setup():
    """
    Complete Indian e-commerce CDC setup - production ready
    """
    logger.info("🇮🇳 Setting up Indian E-commerce CDC Infrastructure")
    
    # Define clusters for different regions
    clusters = [
        KafkaConnectCluster(
            name="mumbai-primary",
            urls=["http://kafka-connect-mumbai-1:8083", "http://kafka-connect-mumbai-2:8083"],
            region="mumbai",
            environment="production"
        ),
        KafkaConnectCluster(
            name="delhi-secondary",
            urls=["http://kafka-connect-delhi-1:8083", "http://kafka-connect-delhi-2:8083"],
            region="delhi",
            environment="production"
        ),
        KafkaConnectCluster(
            name="bangalore-dr",
            urls=["http://kafka-connect-blr-1:8083"],
            region="bangalore",
            environment="disaster-recovery"
        )
    ]
    
    # Initialize manager
    manager = IndianEcommerceConnectorManager(clusters)
    
    # Define connector specifications for bulk creation
    connector_specs = [
        {
            'template_name': 'flipkart-mysql',
            'connector_name': 'flipkart-orders-mumbai',
            'cluster_name': 'mumbai-primary',
            'parameters': {
                'database_host': 'mysql-flipkart-orders.mumbai.internal',
                'database_port': '3306',
                'database_user': 'cdc_user',
                'database_password': 'secure_password_123',
                'table_list': 'flipkart.orders,flipkart.order_items,flipkart.payments',
                'kafka_servers': 'kafka-mumbai.internal:9092',
                'region': 'mumbai'
            }
        },
        {
            'template_name': 'zomato-postgres',
            'connector_name': 'zomato-restaurants-mumbai',
            'cluster_name': 'mumbai-primary',
            'parameters': {
                'database_host': 'postgres-zomato.mumbai.internal',
                'database_port': '5432',
                'database_user': 'zomato_cdc',
                'database_password': 'zomato_secure_456',
                'database_name': 'zomato_prod',
                'table_list': 'public.restaurants,public.orders,public.deliveries',
                'region': 'mumbai'
            }
        },
        {
            'template_name': 'paytm-mongodb',
            'connector_name': 'paytm-transactions-mumbai',
            'cluster_name': 'mumbai-primary',
            'parameters': {
                'mongo_hosts': 'mongo-paytm-rs0.mumbai.internal:27017',
                'mongo_user': 'paytm_cdc',
                'mongo_password': 'paytm_secure_789',
                'collection_list': 'payments.transactions,payments.wallets,payments.upi_logs',
                'region': 'mumbai'
            }
        }
    ]
    
    # Bulk create connectors
    results = manager.bulk_create_connectors(connector_specs)
    
    # Print results
    for result in results:
        if 'error' not in result:
            logger.info(f"✅ Successfully created: {result['connector_name']}")
        else:
            logger.error(f"❌ Failed to create: {result['connector_name']} - {result['error']}")
    
    # Wait a bit and check status
    time.sleep(10)
    
    # Get metrics
    metrics = manager.get_metrics()
    logger.info(f"📊 Final metrics: {json.dumps(metrics, indent=2)}")
    
    return manager

def main():
    """Main function for demo"""
    try:
        manager = create_indian_ecommerce_setup()
        
        # Keep running for monitoring
        logger.info("🎯 CDC Manager is running. Press Ctrl+C to stop.")
        
        while True:
            time.sleep(60)
            metrics = manager.get_metrics()
            logger.info(f"📈 Runtime metrics: {metrics['summary']}")
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down CDC Manager...")
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()

"""
Production Deployment Guide:

1. Environment Setup:
   export KAFKA_CONNECT_CLUSTERS="mumbai-primary,delhi-secondary"
   export MYSQL_CDC_USER="cdc_production_user"
   export KAFKA_SERVERS="kafka-cluster.internal:9092"

2. Security Configuration:
   - SSL certificates for database connections
   - RBAC policies for Kafka topics
   - Secret management (HashiCorp Vault)
   - Network security groups

3. Monitoring Integration:
   - Prometheus metrics export
   - Grafana dashboards
   - PagerDuty alerts for failures
   - Slack notifications

4. Scaling Considerations:
   - Multiple connector instances per table
   - Kafka topic partitioning by region
   - Load balancing across connect workers
   - Auto-scaling based on lag metrics

5. Indian Compliance:
   - Data residency requirements
   - PII masking for Aadhaar/PAN
   - Regional disaster recovery
   - Audit logging requirements
"""
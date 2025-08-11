#!/usr/bin/env python3
"""
Episode 13: CDC & Real-Time Data Pipelines
Example 1: Basic Debezium CDC Setup with MySQL and Kafka

यह example Debezium के साथ MySQL से Kafka में basic CDC setup दिखाता है।
Production-ready configuration के साथ Indian e-commerce use case।

Author: Distributed Systems Podcast Team
Context: Indian e-commerce order processing at scale
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
import mysql.connector
from kafka import KafkaProducer, KafkaConsumer
from dataclasses import dataclass
import uuid

# Hindi में logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cdc_debezium.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DebeziumConfig:
    """Debezium connector configuration for Indian e-commerce orders"""
    name: str
    connector_class: str
    database_hostname: str
    database_port: int
    database_user: str
    database_password: str
    database_server_name: str
    table_whitelist: str
    kafka_topic_prefix: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "config": {
                "connector.class": self.connector_class,
                "database.hostname": self.database_hostname,
                "database.port": self.database_port,
                "database.user": self.database_user,
                "database.password": self.database_password,
                "database.server.name": self.database_server_name,
                "table.whitelist": self.table_whitelist,
                "database.history.kafka.bootstrap.servers": "localhost:9092",
                "database.history.kafka.topic": f"{self.kafka_topic_prefix}.schema-changes",
                "include.schema.changes": "true",
                "transforms": "route",
                "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
                "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
                "transforms.route.replacement": f"{self.kafka_topic_prefix}.$3"
            }
        }

class DebeziumConnectorManager:
    """
    Debezium connector management for Indian e-commerce platforms
    Mumbai के Flipkart, Myntra जैसे platforms के लिए optimized
    """
    
    def __init__(self, connect_url: str = "http://localhost:8083"):
        self.connect_url = connect_url
        self.session = requests.Session()
        
        # Indian e-commerce specific headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Source": "Indian-Ecommerce-CDC"
        })
        
    def create_connector(self, config: DebeziumConfig) -> Dict[str, Any]:
        """
        नया connector बनाओ - Flipkart orders के लिए
        """
        logger.info(f"📡 नया CDC connector बना रहे हैं: {config.name}")
        
        try:
            response = self.session.post(
                f"{self.connect_url}/connectors",
                json=config.to_dict(),
                timeout=30
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Connector successfully बना: {config.name}")
                return response.json()
            else:
                logger.error(f"❌ Connector creation failed: {response.text}")
                return {"error": response.text, "status_code": response.status_code}
                
        except Exception as e:
            logger.error(f"💥 Connector creation exception: {str(e)}")
            return {"error": str(e)}
    
    def get_connector_status(self, connector_name: str) -> Dict[str, Any]:
        """
        Connector का status check करो - production के लिए जरूरी
        """
        try:
            response = self.session.get(
                f"{self.connect_url}/connectors/{connector_name}/status",
                timeout=10
            )
            
            if response.status_code == 200:
                status = response.json()
                logger.info(f"📊 Connector {connector_name} status: {status['connector']['state']}")
                return status
            else:
                logger.warning(f"⚠️ Status check failed: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"💥 Status check exception: {str(e)}")
            return {"error": str(e)}
    
    def restart_connector(self, connector_name: str) -> bool:
        """
        Connector restart करो - Mumbai traffic jam की तरह stuck हो गया तो
        """
        logger.info(f"🔄 Restarting connector: {connector_name}")
        
        try:
            response = self.session.post(
                f"{self.connect_url}/connectors/{connector_name}/restart",
                timeout=30
            )
            
            if response.status_code == 204:
                logger.info(f"✅ Connector successfully restarted: {connector_name}")
                return True
            else:
                logger.error(f"❌ Restart failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Restart exception: {str(e)}")
            return False

class IndianEcommerceOrdersManager:
    """
    Indian e-commerce orders के लिए sample data और CDC monitoring
    """
    
    def __init__(self, mysql_config: Dict[str, Any]):
        self.mysql_config = mysql_config
        self.connection = None
        self.indian_cities = [
            "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
            "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat"
        ]
        self.indian_products = [
            "Samsung Galaxy S24", "iPhone 15", "OnePlus 12", "Xiaomi 14",
            "Realme GT Neo 6", "Vivo V30 Pro", "Oppo Reno 11",
            "Nothing Phone 2a", "iQOO Neo 9 Pro", "Motorola Edge 50"
        ]
        
    def connect_to_mysql(self) -> bool:
        """MySQL connection establish करो"""
        try:
            self.connection = mysql.connector.connect(**self.mysql_config)
            logger.info("✅ MySQL connection established")
            return True
        except Exception as e:
            logger.error(f"💥 MySQL connection failed: {str(e)}")
            return False
    
    def setup_sample_tables(self):
        """
        Indian e-commerce के लिए sample tables बनाओ
        """
        if not self.connection:
            logger.error("❌ No MySQL connection available")
            return
            
        cursor = self.connection.cursor()
        
        # Orders table - Flipkart style
        orders_table = """
        CREATE TABLE IF NOT EXISTS flipkart_orders (
            order_id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            product_name VARCHAR(200) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'INR',
            city VARCHAR(50) NOT NULL,
            state VARCHAR(50) NOT NULL,
            payment_method ENUM('UPI', 'Card', 'Wallet', 'COD') NOT NULL,
            order_status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            seller_id VARCHAR(50) NOT NULL,
            delivery_expected DATE,
            
            INDEX idx_user_id (user_id),
            INDEX idx_order_status (order_status),
            INDEX idx_created_at (created_at),
            INDEX idx_city (city)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        # Payment transactions table - Paytm/PhonePe style
        payments_table = """
        CREATE TABLE IF NOT EXISTS payment_transactions (
            transaction_id VARCHAR(50) PRIMARY KEY,
            order_id VARCHAR(50) NOT NULL,
            payment_gateway ENUM('Razorpay', 'Paytm', 'PhonePe', 'GooglePay') NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            status ENUM('initiated', 'success', 'failed', 'refunded') DEFAULT 'initiated',
            upi_id VARCHAR(100),
            bank_ref_no VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP NULL,
            
            FOREIGN KEY (order_id) REFERENCES flipkart_orders(order_id),
            INDEX idx_order_id (order_id),
            INDEX idx_status (status),
            INDEX idx_payment_gateway (payment_gateway)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        try:
            cursor.execute(orders_table)
            cursor.execute(payments_table)
            self.connection.commit()
            logger.info("✅ Sample tables created successfully")
        except Exception as e:
            logger.error(f"💥 Table creation failed: {str(e)}")
        finally:
            cursor.close()
    
    def generate_sample_orders(self, count: int = 100):
        """
        Indian context के साथ sample orders generate करो
        """
        if not self.connection:
            logger.error("❌ No MySQL connection available")
            return
            
        cursor = self.connection.cursor()
        
        for i in range(count):
            order_id = f"FKT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
            user_id = f"user_{str(uuid.uuid4())[:8]}"
            product_name = self.indian_products[i % len(self.indian_products)]
            
            # Indian pricing logic - रुपये में
            base_price = 15000 + (i % 85000)  # 15K to 1L range
            price = round(base_price * (0.8 + 0.4 * (i % 100) / 100), 2)
            
            city = self.indian_cities[i % len(self.indian_cities)]
            state_map = {
                "Mumbai": "Maharashtra", "Delhi": "Delhi", "Bangalore": "Karnataka",
                "Hyderabad": "Telangana", "Chennai": "Tamil Nadu", "Kolkata": "West Bengal",
                "Pune": "Maharashtra", "Ahmedabad": "Gujarat", "Jaipur": "Rajasthan",
                "Surat": "Gujarat"
            }
            state = state_map.get(city, "Maharashtra")
            
            payment_methods = ["UPI", "Card", "Wallet", "COD"]
            payment_method = payment_methods[i % len(payment_methods)]
            
            seller_id = f"seller_{(i % 50) + 1:03d}"
            
            order_query = """
            INSERT INTO flipkart_orders 
            (order_id, user_id, product_name, price, city, state, payment_method, seller_id, delivery_expected)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, DATE_ADD(NOW(), INTERVAL 3 DAY))
            """
            
            try:
                cursor.execute(order_query, (
                    order_id, user_id, product_name, price, city, state, payment_method, seller_id
                ))
                
                # Payment transaction भी बनाओ
                transaction_id = f"TXN{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
                gateways = ["Razorpay", "Paytm", "PhonePe", "GooglePay"]
                gateway = gateways[i % len(gateways)]
                
                if payment_method == "UPI":
                    upi_id = f"user{i % 1000}@{['paytm', 'phonepe', 'googlepay'][i % 3]}"
                else:
                    upi_id = None
                    
                payment_query = """
                INSERT INTO payment_transactions 
                (transaction_id, order_id, payment_gateway, amount, upi_id)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                cursor.execute(payment_query, (
                    transaction_id, order_id, gateway, price, upi_id
                ))
                
            except Exception as e:
                logger.error(f"💥 Order creation failed: {str(e)}")
                continue
        
        try:
            self.connection.commit()
            logger.info(f"✅ Successfully created {count} sample orders")
        except Exception as e:
            logger.error(f"💥 Commit failed: {str(e)}")
        finally:
            cursor.close()

class KafkaCDCConsumer:
    """
    Kafka से CDC messages consume करने के लिए
    """
    
    def __init__(self, bootstrap_servers: List[str], topics: List[str]):
        self.bootstrap_servers = bootstrap_servers
        self.topics = topics
        self.consumer = None
        
    def start_consuming(self):
        """
        CDC messages consume करना शुरू करो
        """
        try:
            self.consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                group_id='indian-ecommerce-cdc-group',
                auto_offset_reset='earliest'
            )
            
            logger.info(f"📡 Starting CDC consumer for topics: {self.topics}")
            
            for message in self.consumer:
                self.process_cdc_message(message)
                
        except Exception as e:
            logger.error(f"💥 Consumer error: {str(e)}")
        finally:
            if self.consumer:
                self.consumer.close()
    
    def process_cdc_message(self, message):
        """
        Individual CDC message process करो
        """
        try:
            topic = message.topic
            value = message.value
            
            # Debezium message structure
            if 'payload' in value:
                payload = value['payload']
                operation = payload.get('op', 'unknown')  # c=create, u=update, d=delete
                
                if operation == 'c':
                    logger.info(f"🆕 New order created: {payload.get('after', {}).get('order_id', 'unknown')}")
                elif operation == 'u':
                    logger.info(f"🔄 Order updated: {payload.get('after', {}).get('order_id', 'unknown')}")
                elif operation == 'd':
                    logger.info(f"🗑️ Order deleted: {payload.get('before', {}).get('order_id', 'unknown')}")
                
                # Mumbai street style processing
                self.mumbai_style_processing(payload, operation)
                
        except Exception as e:
            logger.error(f"💥 Message processing error: {str(e)}")
    
    def mumbai_style_processing(self, payload: Dict[str, Any], operation: str):
        """
        Mumbai की street style में data process करो
        """
        try:
            if operation in ['c', 'u']:  # Create या Update
                order_data = payload.get('after', {})
                city = order_data.get('city', '')
                amount = order_data.get('price', 0)
                payment_method = order_data.get('payment_method', '')
                
                # Mumbai local train की तरह categorize करो
                if city in ['Mumbai', 'Pune']:  # Maharashtra belt
                    category = "Western Line"
                elif city in ['Delhi', 'Jaipur']:  # North belt
                    category = "Northern Line" 
                elif city in ['Bangalore', 'Chennai']:  # South belt
                    category = "Southern Line"
                else:
                    category = "Harbour Line"  # Others
                
                # Amount के हिसाब से priority
                if amount > 50000:
                    priority = "Express"  # Rajdhani Express
                elif amount > 20000:
                    priority = "Superfast"  # Shatabdi Express
                else:
                    priority = "Passenger"  # Local train
                
                logger.info(f"🚂 {category} - {priority} - ₹{amount:,.2f} - {payment_method} - {city}")
                
                # Real-time analytics के लिए
                self.update_real_time_metrics(city, amount, payment_method)
                
        except Exception as e:
            logger.error(f"💥 Mumbai processing error: {str(e)}")
    
    def update_real_time_metrics(self, city: str, amount: float, payment_method: str):
        """
        Real-time metrics update करो - production dashboards के लिए
        """
        # यहाँ Redis, InfluxDB, या Prometheus metrics update करो
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'city': city,
            'amount': amount,
            'payment_method': payment_method,
            'region': self.get_region_from_city(city)
        }
        
        # Production में यहाँ metrics push करोगे
        logger.info(f"📈 Metrics updated: {json.dumps(metrics, indent=2)}")
    
    def get_region_from_city(self, city: str) -> str:
        """City से region map करो"""
        region_map = {
            'Mumbai': 'West', 'Pune': 'West', 'Ahmedabad': 'West', 'Surat': 'West',
            'Delhi': 'North', 'Jaipur': 'North',
            'Bangalore': 'South', 'Chennai': 'South', 'Hyderabad': 'South',
            'Kolkata': 'East'
        }
        return region_map.get(city, 'Other')

def main():
    """
    Main function - Production CDC setup
    """
    logger.info("🚀 Starting Indian E-commerce CDC Pipeline")
    
    # MySQL configuration - production values
    mysql_config = {
        'host': 'localhost',
        'database': 'indian_ecommerce',
        'user': 'debezium_user',
        'password': 'strong_password_123',
        'port': 3306,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    # Step 1: Setup sample data
    orders_manager = IndianEcommerceOrdersManager(mysql_config)
    if orders_manager.connect_to_mysql():
        orders_manager.setup_sample_tables()
        orders_manager.generate_sample_orders(50)
    
    # Step 2: Setup Debezium connector
    debezium_config = DebeziumConfig(
        name="indian-ecommerce-orders-connector",
        connector_class="io.debezium.connector.mysql.MySqlConnector",
        database_hostname="localhost",
        database_port=3306,
        database_user="debezium_user",
        database_password="strong_password_123",
        database_server_name="indian_ecommerce_server",
        table_whitelist="indian_ecommerce.flipkart_orders,indian_ecommerce.payment_transactions",
        kafka_topic_prefix="indian.ecommerce"
    )
    
    connector_manager = DebeziumConnectorManager()
    
    # Create connector
    result = connector_manager.create_connector(debezium_config)
    if 'error' not in result:
        logger.info("✅ Debezium connector created successfully")
        
        # Wait for connector to start
        time.sleep(5)
        
        # Check status
        status = connector_manager.get_connector_status("indian-ecommerce-orders-connector")
        logger.info(f"📊 Connector status: {json.dumps(status, indent=2)}")
    
    # Step 3: Start consuming CDC messages
    topics = [
        "indian.ecommerce.flipkart_orders",
        "indian.ecommerce.payment_transactions"
    ]
    
    consumer = KafkaCDCConsumer(
        bootstrap_servers=['localhost:9092'],
        topics=topics
    )
    
    # Production में यह separate service होगी
    logger.info("🎯 Starting CDC message consumption...")
    consumer.start_consuming()

if __name__ == "__main__":
    main()

"""
Production Deployment Notes:

1. डेप्लॉयमेंट चेकलिस्ट:
   - MySQL binlog enabled (log-bin, server-id set)
   - Kafka cluster running (3+ brokers for production)
   - Debezium Connect distributed mode
   - Monitoring: Prometheus + Grafana
   - Alerting: PagerDuty/Slack integration

2. स्केलिंग कंसीडेरेशन:
   - Multiple connector instances for different tables
   - Kafka partitioning by customer_id or region
   - Consumer groups for parallel processing
   - Dead letter queues for error handling

3. Indian E-commerce Specific:
   - Festival season load testing (Diwali, Big Billion Day)
   - Regional compliance (data residency)
   - Payment gateway integration monitoring
   - Multi-language support in error messages

4. Performance Tuning:
   - Batch size optimization
   - Kafka compression (snappy/lz4)
   - MySQL read replica for CDC
   - Connection pooling

5. Security:
   - SSL/TLS encryption
   - RBAC for Kafka topics
   - Database user permissions
   - Network security (VPC/subnets)
"""
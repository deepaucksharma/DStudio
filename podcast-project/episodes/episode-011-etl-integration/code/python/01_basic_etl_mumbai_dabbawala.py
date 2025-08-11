#!/usr/bin/env python3
"""
Basic ETL Pipeline - Mumbai Dabbawala System
============================================

Mumbai के दब्बावाले जैसे Data को एक जगह से उठाकर दूसरी जगह पहुंचाना।
Extract करो, Transform करो, Load करो - बिल्कुल Lunch delivery की तरह।

Real-world use case: E-commerce product catalog sync between systems

Author: DStudio Engineering Team
Episode: 11 - ETL & Data Integration Patterns
"""

import mysql.connector
import psycopg2
import pandas as pd
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
import json
from dataclasses import dataclass
from contextlib import contextmanager

# डेटा हेल्थ ट्रैकिंग के लिए metrics
@dataclass
class ETLMetrics:
    """ETL pipeline के performance metrics - जैसे dabbawala की delivery report"""
    start_time: datetime
    end_time: Optional[datetime] = None
    records_extracted: int = 0
    records_transformed: int = 0
    records_loaded: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def duration_minutes(self) -> float:
        """कितनी देर लगी delivery में - minutes में"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return 0.0
    
    def success_rate(self) -> float:
        """कितना successful delivery हुआ - percentage में"""
        if self.records_extracted == 0:
            return 0.0
        return (self.records_loaded / self.records_extracted) * 100

class MumbaiDabbawalaETL:
    """
    Mumbai Dabbawala Style ETL Pipeline
    ===================================
    
    जैसे दब्बावाले:
    1. घर से खाना उठाते हैं (Extract)
    2. Station पे sort करते हैं (Transform) 
    3. Office में deliver करते हैं (Load)
    
    वैसे ही हम data को process करते हैं।
    """
    
    def __init__(self, mysql_config: Dict, postgres_config: Dict):
        self.mysql_config = mysql_config
        self.postgres_config = postgres_config
        self.logger = self._setup_logging()
        self.metrics = None
        
    def _setup_logging(self):
        """Log setup - हर step का record रखना जरूरी है"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('etl_pipeline.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('DabbawalaETL')
    
    @contextmanager
    def mysql_connection(self):
        """MySQL connection manager - घर का connection"""
        connection = None
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            self.logger.info("🏠 MySQL से connection establish हुआ - घर connected!")
            yield connection
        except Exception as e:
            self.logger.error(f"❌ MySQL connection failed: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
                self.logger.info("🔐 MySQL connection closed")
    
    @contextmanager 
    def postgres_connection(self):
        """PostgreSQL connection manager - office का connection"""
        connection = None
        try:
            connection = psycopg2.connect(**self.postgres_config)
            self.logger.info("🏢 PostgreSQL से connection establish हुआ - office connected!")
            yield connection
        except Exception as e:
            self.logger.error(f"❌ PostgreSQL connection failed: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
                self.logger.info("🔐 PostgreSQL connection closed")
    
    def extract_flipkart_products(self) -> pd.DataFrame:
        """
        Extract Phase - घर से डेटा उठाना
        ==============================
        
        Flipkart के products को MySQL से निकालते हैं।
        यह वो phase है जब dabbawala घर-घर जाकर खाना collect करता है।
        """
        self.logger.info("🚚 शुरू हो रहा है EXTRACT phase - data collection")
        
        query = """
        SELECT 
            product_id,
            product_name,
            category_id,
            price,
            stock_quantity,
            seller_id,
            rating,
            reviews_count,
            created_at,
            updated_at
        FROM flipkart_products 
        WHERE updated_at > DATE_SUB(NOW(), INTERVAL 1 DAY)
        AND is_active = 1
        ORDER BY updated_at DESC
        """
        
        try:
            with self.mysql_connection() as conn:
                # Pandas का use करके efficiently data load करना
                df = pd.read_sql(query, conn)
                
                self.metrics.records_extracted = len(df)
                self.logger.info(f"✅ {len(df)} products extract हुए - dabbawala ने {len(df)} dabba collect किए!")
                
                if len(df) == 0:
                    self.logger.warning("⚠️ कोई नया data नहीं मिला - empty dabba!")
                    
                return df
                
        except Exception as e:
            error_msg = f"Extract phase में error: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.metrics.errors.append(error_msg)
            raise

    def transform_product_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform Phase - डेटा को साफ़ करना और format करना  
        ==================================================
        
        जैसे dabbawala railway station पे सभी dabba को sort करता है,
        वैसे ही हम data को clean और standardize करते हैं।
        """
        self.logger.info("🔄 शुरू हो रहा है TRANSFORM phase - data cleaning और formatting")
        
        if df.empty:
            self.logger.info("📭 कोई data नहीं है transform करने के लिए")
            return df
        
        original_count = len(df)
        
        try:
            # 1. डुप्लिकेट हटाना - same product multiple times नहीं होना चाहिए
            df = df.drop_duplicates(subset=['product_id'])
            self.logger.info(f"🧹 Duplicates removed: {original_count - len(df)} duplicate entries")
            
            # 2. Price validation - negative या zero price valid नहीं है
            df = df[df['price'] > 0]
            self.logger.info(f"💰 Invalid prices filtered out")
            
            # 3. Category enrichment - category name add करना
            category_mapping = {
                1: 'Electronics', 2: 'Clothing', 3: 'Books', 
                4: 'Home & Kitchen', 5: 'Sports', 6: 'Beauty'
            }
            df['category_name'] = df['category_id'].map(category_mapping)
            
            # 4. Price bands - pricing categories बनाना (Indian context)
            def get_price_band(price):
                """Price को Indian market के according categorize करना"""
                if price < 500:
                    return 'Budget'  # Affordable for everyone
                elif price < 2000:
                    return 'Mid-Range'  # Middle class friendly
                elif price < 10000:
                    return 'Premium'  # Upper middle class
                else:
                    return 'Luxury'  # High-end segment
            
            df['price_band'] = df['price'].apply(get_price_band)
            
            # 5. Seller performance score - rating के basis पर
            def calculate_seller_score(rating, reviews_count):
                """Seller की performance calculate करना"""
                if reviews_count < 10:
                    return 'New Seller'  # Kam reviews
                elif rating >= 4.5:
                    return 'Excellent'  # Top performer
                elif rating >= 4.0:
                    return 'Good'      # Decent seller
                elif rating >= 3.5:
                    return 'Average'   # Okayish
                else:
                    return 'Poor'      # Improvement needed
            
            df['seller_performance'] = df.apply(
                lambda x: calculate_seller_score(x['rating'], x['reviews_count']), 
                axis=1
            )
            
            # 6. Stock status - inventory levels
            def get_stock_status(quantity):
                """Stock level के according status"""
                if quantity == 0:
                    return 'Out of Stock'
                elif quantity < 10:
                    return 'Low Stock'  # Urgent restocking needed
                elif quantity < 50:
                    return 'Medium Stock'
                else:
                    return 'High Stock'  # Well stocked
            
            df['stock_status'] = df['stock_quantity'].apply(get_stock_status)
            
            # 7. Data types को properly set करना
            df['product_id'] = df['product_id'].astype(str)
            df['price'] = df['price'].round(2)  # Paisa के लिए 2 decimal places
            df['rating'] = df['rating'].round(1)
            
            # 8. Null values handling - missing data को handle करना
            df['product_name'].fillna('Unknown Product', inplace=True)
            df['category_name'].fillna('Uncategorized', inplace=True)
            
            # 9. Business rules validation
            # Review count और rating consistent होना चाहिए
            df.loc[df['reviews_count'] == 0, 'rating'] = 0
            
            # 10. Timestamp formatting for PostgreSQL
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['updated_at'] = pd.to_datetime(df['updated_at'])
            df['processed_at'] = datetime.now()  # Processing timestamp add करना
            
            self.metrics.records_transformed = len(df)
            transform_success_rate = (len(df) / original_count) * 100
            
            self.logger.info(f"✅ Transform complete! {len(df)}/{original_count} records processed ({transform_success_rate:.1f}% success rate)")
            self.logger.info(f"🎯 Added columns: category_name, price_band, seller_performance, stock_status, processed_at")
            
            return df
            
        except Exception as e:
            error_msg = f"Transform phase में error: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.metrics.errors.append(error_msg)
            raise

    def load_to_postgres(self, df: pd.DataFrame) -> bool:
        """
        Load Phase - Cleaned data को PostgreSQL में store करना
        ====================================================
        
        यह final delivery phase है - dabbawala office में dabba पहुंचाता है।
        """
        self.logger.info("📦 शुरू हो रहा है LOAD phase - final destination में data delivery")
        
        if df.empty:
            self.logger.info("📭 कोई data नहीं है load करने के लिए")
            return True
        
        try:
            with self.postgres_connection() as conn:
                cursor = conn.cursor()
                
                # Table create करना अगर exist नहीं करती
                create_table_query = """
                CREATE TABLE IF NOT EXISTS flipkart_products_processed (
                    product_id VARCHAR(50) PRIMARY KEY,
                    product_name VARCHAR(255) NOT NULL,
                    category_id INTEGER,
                    category_name VARCHAR(100),
                    price DECIMAL(10,2),
                    price_band VARCHAR(20),
                    stock_quantity INTEGER,
                    stock_status VARCHAR(20),
                    seller_id VARCHAR(50),
                    seller_performance VARCHAR(20),
                    rating DECIMAL(3,1),
                    reviews_count INTEGER,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                cursor.execute(create_table_query)
                self.logger.info("🏗️ Table structure ready - delivery location prepared!")
                
                # Bulk insert के लिए data prepare करना
                records = []
                for _, row in df.iterrows():
                    record = (
                        row['product_id'], row['product_name'], row['category_id'],
                        row['category_name'], row['price'], row['price_band'],
                        row['stock_quantity'], row['stock_status'], row['seller_id'],
                        row['seller_performance'], row['rating'], row['reviews_count'],
                        row['created_at'], row['updated_at'], row['processed_at']
                    )
                    records.append(record)
                
                # Upsert operation - existing records को update करना, नई को insert करना
                upsert_query = """
                INSERT INTO flipkart_products_processed (
                    product_id, product_name, category_id, category_name,
                    price, price_band, stock_quantity, stock_status,
                    seller_id, seller_performance, rating, reviews_count,
                    created_at, updated_at, processed_at
                ) VALUES %s
                ON CONFLICT (product_id) 
                DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    category_id = EXCLUDED.category_id,
                    category_name = EXCLUDED.category_name,
                    price = EXCLUDED.price,
                    price_band = EXCLUDED.price_band,
                    stock_quantity = EXCLUDED.stock_quantity,
                    stock_status = EXCLUDED.stock_status,
                    seller_performance = EXCLUDED.seller_performance,
                    rating = EXCLUDED.rating,
                    reviews_count = EXCLUDED.reviews_count,
                    updated_at = EXCLUDED.updated_at,
                    processed_at = EXCLUDED.processed_at
                """
                
                # Psycopg2 के execute_values का use करके bulk insert
                from psycopg2.extras import execute_values
                execute_values(cursor, upsert_query, records, template=None)
                
                # Transaction commit करना
                conn.commit()
                
                self.metrics.records_loaded = len(records)
                self.logger.info(f"✅ {len(records)} records successfully loaded to PostgreSQL")
                self.logger.info(f"📊 Load complete - all dabbas delivered successfully!")
                
                # Data quality verification
                cursor.execute("SELECT COUNT(*) FROM flipkart_products_processed WHERE processed_at::date = CURRENT_DATE")
                today_count = cursor.fetchone()[0]
                self.logger.info(f"📈 Today's total processed records: {today_count}")
                
                return True
                
        except Exception as e:
            error_msg = f"Load phase में error: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.metrics.errors.append(error_msg)
            return False

    def run_etl_pipeline(self) -> Dict:
        """
        Complete ETL Pipeline Execution
        ==============================
        
        Mumbai dabbawala की तरह complete delivery cycle चलाना।
        """
        self.logger.info("🚀 Starting Mumbai Dabbawala ETL Pipeline...")
        self.metrics = ETLMetrics(start_time=datetime.now())
        
        pipeline_success = False
        
        try:
            # Step 1: Extract - घर से data उठाना
            self.logger.info("📍 Step 1/3: EXTRACT phase starting...")
            extracted_data = self.extract_flipkart_products()
            
            # Step 2: Transform - data को process करना
            self.logger.info("📍 Step 2/3: TRANSFORM phase starting...")  
            transformed_data = self.transform_product_data(extracted_data)
            
            # Step 3: Load - final destination में deliver करना
            self.logger.info("📍 Step 3/3: LOAD phase starting...")
            load_success = self.load_to_postgres(transformed_data)
            
            pipeline_success = load_success
            
        except Exception as e:
            self.logger.error(f"💥 Pipeline failed: {str(e)}")
            self.metrics.errors.append(f"Pipeline failure: {str(e)}")
            
        finally:
            # Pipeline completion
            self.metrics.end_time = datetime.now()
            
            # Final report generation
            report = self._generate_pipeline_report(pipeline_success)
            self.logger.info("📋 Pipeline execution completed!")
            
            return report
    
    def _generate_pipeline_report(self, success: bool) -> Dict:
        """Pipeline की detailed report generate करना"""
        
        report = {
            "pipeline_name": "Mumbai Dabbawala ETL",
            "execution_date": self.metrics.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "SUCCESS" if success else "FAILED",
            "duration_minutes": self.metrics.duration_minutes(),
            "performance_metrics": {
                "records_extracted": self.metrics.records_extracted,
                "records_transformed": self.metrics.records_transformed, 
                "records_loaded": self.metrics.records_loaded,
                "success_rate_percent": self.metrics.success_rate(),
                "processing_speed_records_per_minute": (
                    self.metrics.records_loaded / self.metrics.duration_minutes() 
                    if self.metrics.duration_minutes() > 0 else 0
                )
            },
            "errors": self.metrics.errors,
            "recommendations": []
        }
        
        # Performance recommendations
        if self.metrics.success_rate() < 95:
            report["recommendations"].append("⚠️ Success rate is below 95%. Check data quality issues.")
        
        if self.metrics.duration_minutes() > 30:
            report["recommendations"].append("🐌 Pipeline is taking more than 30 minutes. Consider optimization.")
        
        if len(self.metrics.errors) == 0:
            report["recommendations"].append("✅ Pipeline ran without errors. Great job!")
        
        return report

def main():
    """
    Main execution function - Production ready example
    ================================================
    
    Real Mumbai dabbawala ETL pipeline को run करना।
    """
    
    print("🚀 Mumbai Dabbawala ETL Pipeline Starting...")
    print("=" * 60)
    
    # Database configurations - Production settings
    mysql_config = {
        'host': 'mysql-master.flipkart.com',  # Master DB for reads
        'user': 'etl_user',
        'password': 'secure_password_123',
        'database': 'flipkart_products',
        'port': 3306,
        'charset': 'utf8mb4',
        'autocommit': False,
        'connect_timeout': 30
    }
    
    postgres_config = {
        'host': 'postgres-warehouse.analytics.com',  # Data warehouse
        'user': 'warehouse_etl',
        'password': 'warehouse_secure_pass',
        'database': 'analytics_db',
        'port': 5432,
        'connect_timeout': 30
    }
    
    # ETL pipeline initialization
    etl_pipeline = MumbaiDabbawalaETL(mysql_config, postgres_config)
    
    try:
        # Execute complete pipeline
        result = etl_pipeline.run_etl_pipeline()
        
        # Print final report
        print("\n📊 Pipeline Execution Report:")
        print("=" * 40)
        print(json.dumps(result, indent=2, default=str))
        
        # Success/Failure indication
        if result["status"] == "SUCCESS":
            print(f"\n✅ Pipeline completed successfully!")
            print(f"⏱️ Duration: {result['duration_minutes']:.2f} minutes")
            print(f"📦 Processed: {result['performance_metrics']['records_loaded']} records")
            print(f"🎯 Success Rate: {result['performance_metrics']['success_rate_percent']:.1f}%")
        else:
            print(f"\n❌ Pipeline failed!")
            print(f"💥 Errors: {len(result['errors'])} issues found")
    
    except Exception as e:
        print(f"\n💥 Critical Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    """
    Script execution entry point
    ===========================
    
    Production environment में इसे cron job या Airflow task के रूप में run करना।
    """
    
    success = main()
    exit(0 if success else 1)


# Performance Tips for Production:
"""
🔧 Production Optimization Tips:

1. **Connection Pooling**: 
   - MySQL और PostgreSQL के लिए connection pooling use करें
   - SQLAlchemy या psycopg2 pool का उपयोग करें

2. **Batch Processing**:
   - Large datasets के लिए chunks में process करें  
   - Memory usage control करने के लिए

3. **Parallel Processing**:
   - Multiple threads/processes का उपयोग करें
   - concurrent.futures का use करें

4. **Monitoring**:
   - Prometheus metrics add करें
   - Grafana dashboards बनाएं
   - Error alerting setup करें

5. **Error Recovery**:
   - Dead letter queues implement करें
   - Exponential backoff retry करें
   - Circuit breaker pattern use करें

6. **Data Quality**:
   - Great Expectations library use करें
   - Data validation rules implement करें
   - Schema evolution handling करें

7. **Cost Optimization**:
   - Read replicas का use करें source के लिए
   - Compression enable करें
   - Archive old data को cheaper storage पर move करें

Mumbai ke dabbawale की तरह - Time pe delivery, Quality guaranteed! 🥘📦
"""
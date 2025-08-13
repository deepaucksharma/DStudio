#!/usr/bin/env python3
"""
DataOps Example 02: Data Versioning and Lineage Tracking
Complete data lineage tracking system with versioning for Indian companies
Focus: Flipkart inventory tracking, Paytm transaction lineage, Zomato order flow

Author: DataOps Architecture Series
Episode: 015 - DataOps Automation
"""

import os
import sys
import json
import uuid
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import sqlite3
import boto3
from botocore.exceptions import NoCredentialsError
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSON
import dvc.api
import git

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/dataops/lineage.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Database setup
Base = declarative_base()

class DataAssetType(Enum):
    """Types of data assets in Indian e-commerce companies"""
    RAW_DATA = "raw_data"
    PROCESSED_DATA = "processed_data"
    FEATURE_DATA = "feature_data"
    MODEL_DATA = "model_data"
    REPORT_DATA = "report_data"
    EXTERNAL_API = "external_api"

class TransformationType(Enum):
    """Types of data transformations"""
    ETL = "etl"
    CLEANING = "cleaning"
    AGGREGATION = "aggregation"
    ENRICHMENT = "enrichment"
    VALIDATION = "validation"
    ML_FEATURE_ENGINEERING = "ml_feature_engineering"

@dataclass
class DataVersion:
    """Data version metadata"""
    version_id: str
    asset_name: str
    version_number: str
    checksum: str
    size_bytes: int
    row_count: int
    schema_hash: str
    created_at: datetime
    created_by: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

class DataAsset(Base):
    """Data asset model for tracking"""
    __tablename__ = 'data_assets'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)
    description = Column(Text)
    owner = Column(String, nullable=False)
    business_domain = Column(String)  # e.g., "flipkart_inventory", "paytm_payments"
    sensitivity_level = Column(String)  # "public", "internal", "confidential", "restricted"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)

class DataVersion(Base):
    """Data version model"""
    __tablename__ = 'data_versions'
    
    version_id = Column(String, primary_key=True)
    asset_id = Column(String, nullable=False)
    version_number = Column(String, nullable=False)
    checksum = Column(String, nullable=False)
    size_bytes = Column(Integer)
    row_count = Column(Integer)
    schema_hash = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=False)
    tags = Column(JSON)
    metadata = Column(JSON)

class DataLineage(Base):
    """Data lineage model"""
    __tablename__ = 'data_lineage'
    
    id = Column(String, primary_key=True)
    source_asset_id = Column(String, nullable=False)
    target_asset_id = Column(String, nullable=False)
    transformation_type = Column(String, nullable=False)
    transformation_code = Column(Text)
    execution_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class DataQualityCheck(Base):
    """Data quality check results"""
    __tablename__ = 'data_quality_checks'
    
    id = Column(String, primary_key=True)
    version_id = Column(String, nullable=False)
    check_type = Column(String, nullable=False)
    check_name = Column(String, nullable=False)
    passed = Column(Boolean, nullable=False)
    score = Column(Float)
    details = Column(JSON)
    executed_at = Column(DateTime, default=datetime.utcnow)

class DataVersioningSystem:
    """
    Complete data versioning system for Indian companies
    Handles large datasets like Flipkart product catalog, Paytm transactions
    """
    
    def __init__(self, storage_backend: str = "local", database_url: str = "sqlite:///dataops.db"):
        self.storage_backend = storage_backend
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Initialize storage backend
        if storage_backend == "s3":
            self.s3_client = boto3.client('s3')
            self.bucket_name = "indian-dataops-versions"
        
        logger.info(f"Data versioning system initialized with {storage_backend} backend")
    
    def calculate_data_checksum(self, data: pd.DataFrame) -> str:
        """Calculate checksum for data integrity"""
        try:
            # Convert dataframe to string representation for hashing
            data_string = data.to_csv(index=False, encoding='utf-8')
            checksum = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
            return checksum
        except Exception as e:
            logger.error(f"Checksum calculation failed: {e}")
            return ""
    
    def calculate_schema_hash(self, data: pd.DataFrame) -> str:
        """Calculate schema hash for schema evolution tracking"""
        try:
            schema_info = {
                'columns': list(data.columns),
                'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
                'shape': data.shape
            }
            schema_string = json.dumps(schema_info, sort_keys=True)
            schema_hash = hashlib.md5(schema_string.encode()).hexdigest()
            return schema_hash
        except Exception as e:
            logger.error(f"Schema hash calculation failed: {e}")
            return ""
    
    def create_data_asset(self, name: str, asset_type: DataAssetType, 
                         owner: str, business_domain: str,
                         description: str = "", sensitivity_level: str = "internal") -> str:
        """Create new data asset"""
        try:
            asset_id = str(uuid.uuid4())
            
            asset = DataAsset(
                id=asset_id,
                name=name,
                asset_type=asset_type.value,
                description=description,
                owner=owner,
                business_domain=business_domain,
                sensitivity_level=sensitivity_level,
                metadata={}
            )
            
            self.session.add(asset)
            self.session.commit()
            
            logger.info(f"Data asset created: {name} (ID: {asset_id})")
            return asset_id
            
        except Exception as e:
            logger.error(f"Failed to create data asset: {e}")
            self.session.rollback()
            raise
    
    def version_data(self, asset_id: str, data: pd.DataFrame, 
                    version_number: str, created_by: str,
                    tags: List[str] = None, metadata: Dict = None) -> str:
        """Create new version of data asset"""
        try:
            version_id = str(uuid.uuid4())
            checksum = self.calculate_data_checksum(data)
            schema_hash = self.calculate_schema_hash(data)
            
            # Store data based on backend
            file_path = self.store_data_version(asset_id, version_id, data)
            
            version = DataVersion(
                version_id=version_id,
                asset_id=asset_id,
                version_number=version_number,
                checksum=checksum,
                size_bytes=len(data.to_csv(index=False).encode('utf-8')),
                row_count=len(data),
                schema_hash=schema_hash,
                file_path=file_path,
                created_by=created_by,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            self.session.add(version)
            self.session.commit()
            
            logger.info(f"Data version created: {version_number} for asset {asset_id}")
            return version_id
            
        except Exception as e:
            logger.error(f"Failed to version data: {e}")
            self.session.rollback()
            raise
    
    def store_data_version(self, asset_id: str, version_id: str, data: pd.DataFrame) -> str:
        """Store data version in appropriate backend"""
        try:
            filename = f"{asset_id}/{version_id}/data.parquet"
            
            if self.storage_backend == "local":
                # Store locally
                local_path = f"/tmp/dataops_versions/{filename}"
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                data.to_parquet(local_path, compression='snappy')
                return local_path
                
            elif self.storage_backend == "s3":
                # Store in S3
                temp_path = f"/tmp/{version_id}.parquet"
                data.to_parquet(temp_path, compression='snappy')
                
                self.s3_client.upload_file(temp_path, self.bucket_name, filename)
                os.remove(temp_path)
                
                return f"s3://{self.bucket_name}/{filename}"
            
            else:
                raise ValueError(f"Unsupported storage backend: {self.storage_backend}")
                
        except Exception as e:
            logger.error(f"Failed to store data version: {e}")
            raise
    
    def get_data_version(self, version_id: str) -> pd.DataFrame:
        """Retrieve specific data version"""
        try:
            version = self.session.query(DataVersion).filter_by(version_id=version_id).first()
            if not version:
                raise ValueError(f"Version {version_id} not found")
            
            if self.storage_backend == "local":
                return pd.read_parquet(version.file_path)
            elif self.storage_backend == "s3":
                # Download from S3 and read
                temp_path = f"/tmp/{version_id}.parquet"
                s3_path = version.file_path.replace(f"s3://{self.bucket_name}/", "")
                self.s3_client.download_file(self.bucket_name, s3_path, temp_path)
                data = pd.read_parquet(temp_path)
                os.remove(temp_path)
                return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve data version: {e}")
            raise
    
    def compare_versions(self, version_id_1: str, version_id_2: str) -> Dict:
        """Compare two data versions"""
        try:
            version1 = self.session.query(DataVersion).filter_by(version_id=version_id_1).first()
            version2 = self.session.query(DataVersion).filter_by(version_id=version_id_2).first()
            
            if not version1 or not version2:
                raise ValueError("One or both versions not found")
            
            comparison = {
                'version_1': {
                    'version_number': version1.version_number,
                    'checksum': version1.checksum,
                    'row_count': version1.row_count,
                    'schema_hash': version1.schema_hash,
                    'created_at': version1.created_at.isoformat()
                },
                'version_2': {
                    'version_number': version2.version_number,
                    'checksum': version2.checksum,
                    'row_count': version2.row_count,
                    'schema_hash': version2.schema_hash,
                    'created_at': version2.created_at.isoformat()
                },
                'differences': {
                    'data_changed': version1.checksum != version2.checksum,
                    'schema_changed': version1.schema_hash != version2.schema_hash,
                    'row_count_diff': version2.row_count - version1.row_count,
                    'size_diff_bytes': version2.size_bytes - version1.size_bytes
                }
            }
            
            # If data changed, get detailed diff
            if comparison['differences']['data_changed']:
                data1 = self.get_data_version(version_id_1)
                data2 = self.get_data_version(version_id_2)
                comparison['differences']['detailed_diff'] = self.get_detailed_diff(data1, data2)
            
            return comparison
            
        except Exception as e:
            logger.error(f"Version comparison failed: {e}")
            raise
    
    def get_detailed_diff(self, data1: pd.DataFrame, data2: pd.DataFrame) -> Dict:
        """Get detailed differences between two datasets"""
        try:
            diff_info = {
                'columns_added': list(set(data2.columns) - set(data1.columns)),
                'columns_removed': list(set(data1.columns) - set(data2.columns)),
                'common_columns': list(set(data1.columns) & set(data2.columns)),
                'row_changes': {}
            }
            
            # Check for data type changes in common columns
            dtype_changes = {}
            for col in diff_info['common_columns']:
                if str(data1[col].dtype) != str(data2[col].dtype):
                    dtype_changes[col] = {
                        'from': str(data1[col].dtype),
                        'to': str(data2[col].dtype)
                    }
            diff_info['dtype_changes'] = dtype_changes
            
            return diff_info
            
        except Exception as e:
            logger.error(f"Detailed diff calculation failed: {e}")
            return {}

class DataLineageTracker:
    """
    Data lineage tracking for Indian e-commerce companies
    Tracks data flow from source to insights
    """
    
    def __init__(self, database_url: str = "sqlite:///dataops.db"):
        self.engine = create_engine(database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.lineage_graph = nx.DiGraph()
    
    def record_transformation(self, source_asset_id: str, target_asset_id: str,
                            transformation_type: TransformationType,
                            transformation_code: str = "", execution_id: str = "",
                            metadata: Dict = None) -> str:
        """Record data transformation lineage"""
        try:
            lineage_id = str(uuid.uuid4())
            
            lineage = DataLineage(
                id=lineage_id,
                source_asset_id=source_asset_id,
                target_asset_id=target_asset_id,
                transformation_type=transformation_type.value,
                transformation_code=transformation_code,
                execution_id=execution_id,
                metadata=metadata or {}
            )
            
            self.session.add(lineage)
            self.session.commit()
            
            # Add to graph for visualization
            self.lineage_graph.add_edge(source_asset_id, target_asset_id, 
                                      transformation=transformation_type.value,
                                      lineage_id=lineage_id)
            
            logger.info(f"Lineage recorded: {source_asset_id} -> {target_asset_id}")
            return lineage_id
            
        except Exception as e:
            logger.error(f"Failed to record lineage: {e}")
            self.session.rollback()
            raise
    
    def get_upstream_lineage(self, asset_id: str, depth: int = 10) -> List[Dict]:
        """Get upstream data lineage for an asset"""
        try:
            upstream_lineage = []
            
            def traverse_upstream(current_asset_id: str, current_depth: int):
                if current_depth <= 0:
                    return
                
                lineages = self.session.query(DataLineage).filter_by(
                    target_asset_id=current_asset_id
                ).all()
                
                for lineage in lineages:
                    upstream_lineage.append({
                        'source_asset_id': lineage.source_asset_id,
                        'target_asset_id': lineage.target_asset_id,
                        'transformation_type': lineage.transformation_type,
                        'created_at': lineage.created_at.isoformat(),
                        'depth': depth - current_depth + 1
                    })
                    
                    # Recursively traverse upstream
                    traverse_upstream(lineage.source_asset_id, current_depth - 1)
            
            traverse_upstream(asset_id, depth)
            return upstream_lineage
            
        except Exception as e:
            logger.error(f"Failed to get upstream lineage: {e}")
            return []
    
    def get_downstream_lineage(self, asset_id: str, depth: int = 10) -> List[Dict]:
        """Get downstream data lineage for an asset"""
        try:
            downstream_lineage = []
            
            def traverse_downstream(current_asset_id: str, current_depth: int):
                if current_depth <= 0:
                    return
                
                lineages = self.session.query(DataLineage).filter_by(
                    source_asset_id=current_asset_id
                ).all()
                
                for lineage in lineages:
                    downstream_lineage.append({
                        'source_asset_id': lineage.source_asset_id,
                        'target_asset_id': lineage.target_asset_id,
                        'transformation_type': lineage.transformation_type,
                        'created_at': lineage.created_at.isoformat(),
                        'depth': depth - current_depth + 1
                    })
                    
                    # Recursively traverse downstream
                    traverse_downstream(lineage.target_asset_id, current_depth - 1)
            
            traverse_downstream(asset_id, depth)
            return downstream_lineage
            
        except Exception as e:
            logger.error(f"Failed to get downstream lineage: {e}")
            return []
    
    def visualize_lineage(self, asset_id: str, output_path: str = "/tmp/lineage_graph.png"):
        """Create visual representation of data lineage"""
        try:
            # Get complete lineage
            upstream = self.get_upstream_lineage(asset_id)
            downstream = self.get_downstream_lineage(asset_id)
            
            # Create subgraph
            nodes = set([asset_id])
            edges = []
            
            for lineage in upstream + downstream:
                nodes.add(lineage['source_asset_id'])
                nodes.add(lineage['target_asset_id'])
                edges.append((lineage['source_asset_id'], lineage['target_asset_id']))
            
            # Create graph
            G = nx.DiGraph()
            G.add_nodes_from(nodes)
            G.add_edges_from(edges)
            
            # Create visualization
            plt.figure(figsize=(15, 10))
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            # Color nodes based on type
            node_colors = []
            for node in G.nodes():
                if node == asset_id:
                    node_colors.append('red')  # Target asset
                elif node in [l['source_asset_id'] for l in upstream]:
                    node_colors.append('lightblue')  # Upstream
                else:
                    node_colors.append('lightgreen')  # Downstream
            
            nx.draw(G, pos, node_color=node_colors, node_size=3000, 
                   with_labels=False, arrows=True, arrowsize=20, 
                   font_size=8, font_weight='bold')
            
            # Add labels
            labels = {node: node[:8] + '...' if len(node) > 8 else node for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=8)
            
            plt.title(f"Data Lineage for Asset: {asset_id[:8]}...", fontsize=16)
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Lineage graph saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Lineage visualization failed: {e}")
            return None
    
    def get_impact_analysis(self, asset_id: str) -> Dict:
        """Analyze impact of changes to a data asset"""
        try:
            downstream = self.get_downstream_lineage(asset_id)
            
            # Count affected assets by transformation type
            impact_summary = {
                'total_affected_assets': len(set([d['target_asset_id'] for d in downstream])),
                'affected_by_type': {},
                'critical_dependencies': [],
                'recommendations': []
            }
            
            # Group by transformation type
            for lineage in downstream:
                trans_type = lineage['transformation_type']
                if trans_type not in impact_summary['affected_by_type']:
                    impact_summary['affected_by_type'][trans_type] = 0
                impact_summary['affected_by_type'][trans_type] += 1
            
            # Identify critical dependencies (more than 3 downstream assets)
            if impact_summary['total_affected_assets'] > 3:
                impact_summary['critical_dependencies'].append(asset_id)
                impact_summary['recommendations'].append(
                    "High impact asset - implement careful change management"
                )
            
            # Generate recommendations based on Indian company best practices
            if 'ml_feature_engineering' in impact_summary['affected_by_type']:
                impact_summary['recommendations'].append(
                    "ML features affected - retrain models and validate performance"
                )
            
            if 'etl' in impact_summary['affected_by_type']:
                impact_summary['recommendations'].append(
                    "ETL pipelines affected - validate data quality downstream"
                )
            
            return impact_summary
            
        except Exception as e:
            logger.error(f"Impact analysis failed: {e}")
            return {}

class IndianEcommerceDataVersioningDemo:
    """
    Demonstration of data versioning for Indian e-commerce companies
    Examples: Flipkart inventory, Paytm transactions, Zomato orders
    """
    
    def __init__(self):
        self.versioning_system = DataVersioningSystem()
        self.lineage_tracker = DataLineageTracker()
    
    def demo_flipkart_inventory_versioning(self):
        """Demo versioning of Flipkart inventory data"""
        logger.info("🛒 Starting Flipkart inventory versioning demo")
        
        # Create asset
        asset_id = self.versioning_system.create_data_asset(
            name="flipkart_product_inventory",
            asset_type=DataAssetType.RAW_DATA,
            owner="inventory_team@flipkart.com",
            business_domain="flipkart_inventory",
            description="Daily product inventory snapshot",
            sensitivity_level="internal"
        )
        
        # Create initial inventory data (Version 1.0)
        initial_inventory = pd.DataFrame({
            'product_id': ['PRD001', 'PRD002', 'PRD003', 'PRD004', 'PRD005'],
            'product_name': [
                'iPhone 15 Pro Max 256GB',
                'Samsung Galaxy S24 Ultra',
                'OnePlus 12 5G',
                'Google Pixel 8 Pro',
                'Nothing Phone 2'
            ],
            'category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics'],
            'brand': ['Apple', 'Samsung', 'OnePlus', 'Google', 'Nothing'],
            'price_inr': [134900, 124999, 64999, 84999, 44999],
            'stock_quantity': [150, 200, 300, 100, 250],
            'warehouse_location': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad'],
            'last_updated': [datetime.now()] * 5
        })
        
        version_1_id = self.versioning_system.version_data(
            asset_id=asset_id,
            data=initial_inventory,
            version_number="1.0",
            created_by="inventory_automation@flipkart.com",
            tags=["daily_snapshot", "production"],
            metadata={"source": "warehouse_management_system", "region": "india"}
        )
        
        # Simulate stock updates (Version 1.1)
        updated_inventory = initial_inventory.copy()
        updated_inventory.loc[0, 'stock_quantity'] = 120  # iPhone stock reduced
        updated_inventory.loc[1, 'stock_quantity'] = 180  # Samsung stock reduced
        updated_inventory.loc[2, 'price_inr'] = 62999     # OnePlus price reduced
        
        version_2_id = self.versioning_system.version_data(
            asset_id=asset_id,
            data=updated_inventory,
            version_number="1.1",
            created_by="inventory_automation@flipkart.com",
            tags=["stock_update", "price_change"],
            metadata={"trigger": "sale_day_update", "discount_applied": True}
        )
        
        # Compare versions
        comparison = self.versioning_system.compare_versions(version_1_id, version_2_id)
        
        logger.info(f"📊 Inventory versioning completed:")
        logger.info(f"   Asset ID: {asset_id}")
        logger.info(f"   Version 1.0 ID: {version_1_id}")
        logger.info(f"   Version 1.1 ID: {version_2_id}")
        logger.info(f"   Data changed: {comparison['differences']['data_changed']}")
        logger.info(f"   Row count diff: {comparison['differences']['row_count_diff']}")
        
        return asset_id, version_1_id, version_2_id
    
    def demo_paytm_transaction_lineage(self):
        """Demo lineage tracking for Paytm transaction processing"""
        logger.info("💳 Starting Paytm transaction lineage demo")
        
        # Raw transaction data
        raw_asset_id = self.versioning_system.create_data_asset(
            name="paytm_raw_transactions",
            asset_type=DataAssetType.RAW_DATA,
            owner="payments_team@paytm.com",
            business_domain="paytm_payments",
            description="Raw transaction events from payment gateway"
        )
        
        # Processed transaction data
        processed_asset_id = self.versioning_system.create_data_asset(
            name="paytm_processed_transactions",
            asset_type=DataAssetType.PROCESSED_DATA,
            owner="data_engineering@paytm.com",
            business_domain="paytm_payments",
            description="Cleaned and validated transactions"
        )
        
        # Feature engineered data for fraud detection
        feature_asset_id = self.versioning_system.create_data_asset(
            name="paytm_fraud_features",
            asset_type=DataAssetType.FEATURE_DATA,
            owner="ml_team@paytm.com",
            business_domain="paytm_fraud_detection",
            description="Features for fraud detection model"
        )
        
        # Daily aggregated reports
        report_asset_id = self.versioning_system.create_data_asset(
            name="paytm_daily_transaction_report",
            asset_type=DataAssetType.REPORT_DATA,
            owner="analytics_team@paytm.com",
            business_domain="paytm_analytics",
            description="Daily transaction summary for business teams"
        )
        
        # Record lineage transformations
        etl_lineage_id = self.lineage_tracker.record_transformation(
            source_asset_id=raw_asset_id,
            target_asset_id=processed_asset_id,
            transformation_type=TransformationType.ETL,
            transformation_code="""
            -- Paytm Transaction ETL
            SELECT 
                transaction_id,
                user_id,
                merchant_id,
                amount,
                currency,
                status,
                payment_method,
                created_at,
                CASE 
                    WHEN amount > 200000 THEN 'high_value'
                    WHEN amount > 10000 THEN 'medium_value'
                    ELSE 'low_value'
                END as risk_category
            FROM raw_transactions
            WHERE status IN ('SUCCESS', 'PENDING', 'FAILED')
            AND created_at >= CURRENT_DATE - INTERVAL '1 day'
            """,
            metadata={"pipeline": "daily_etl", "cost_inr": 250}
        )
        
        feature_lineage_id = self.lineage_tracker.record_transformation(
            source_asset_id=processed_asset_id,
            target_asset_id=feature_asset_id,
            transformation_type=TransformationType.ML_FEATURE_ENGINEERING,
            transformation_code="""
            # Fraud detection feature engineering
            features = [
                'transaction_amount_normalized',
                'merchant_risk_score',
                'user_transaction_frequency_24h',
                'payment_method_risk_score',
                'geographic_anomaly_score'
            ]
            """,
            metadata={"ml_pipeline": "fraud_detection_v2", "cost_inr": 150}
        )
        
        report_lineage_id = self.lineage_tracker.record_transformation(
            source_asset_id=processed_asset_id,
            target_asset_id=report_asset_id,
            transformation_type=TransformationType.AGGREGATION,
            transformation_code="""
            -- Daily transaction summary
            SELECT 
                DATE(created_at) as transaction_date,
                COUNT(*) as total_transactions,
                SUM(amount) as total_amount_inr,
                AVG(amount) as avg_amount_inr,
                COUNT(DISTINCT merchant_id) as unique_merchants,
                COUNT(DISTINCT user_id) as unique_users
            FROM processed_transactions
            GROUP BY DATE(created_at)
            """,
            metadata={"report_type": "daily_summary", "cost_inr": 50}
        )
        
        # Get lineage information
        upstream_lineage = self.lineage_tracker.get_upstream_lineage(feature_asset_id)
        downstream_lineage = self.lineage_tracker.get_downstream_lineage(processed_asset_id)
        
        logger.info(f"💳 Paytm transaction lineage completed:")
        logger.info(f"   Raw transactions -> Processed: {etl_lineage_id}")
        logger.info(f"   Processed -> Features: {feature_lineage_id}")
        logger.info(f"   Processed -> Reports: {report_lineage_id}")
        logger.info(f"   Upstream assets for features: {len(upstream_lineage)}")
        logger.info(f"   Downstream assets from processed: {len(downstream_lineage)}")
        
        return {
            'raw_asset_id': raw_asset_id,
            'processed_asset_id': processed_asset_id,
            'feature_asset_id': feature_asset_id,
            'report_asset_id': report_asset_id
        }
    
    def demo_impact_analysis(self, asset_id: str):
        """Demo impact analysis for data changes"""
        logger.info(f"📈 Running impact analysis for asset: {asset_id}")
        
        impact = self.lineage_tracker.get_impact_analysis(asset_id)
        
        logger.info(f"   Total affected assets: {impact['total_affected_assets']}")
        logger.info(f"   Affected by transformation type: {impact['affected_by_type']}")
        logger.info(f"   Recommendations: {impact['recommendations']}")
        
        return impact

def main():
    """Demonstrate data versioning and lineage tracking for Indian companies"""
    
    print("🚀 Starting DataOps Versioning and Lineage Demo")
    print("=" * 60)
    
    demo = IndianEcommerceDataVersioningDemo()
    
    # Demo 1: Flipkart inventory versioning
    print("\n📦 Demo 1: Flipkart Inventory Versioning")
    flipkart_asset_id, v1_id, v2_id = demo.demo_flipkart_inventory_versioning()
    
    # Demo 2: Paytm transaction lineage
    print("\n💳 Demo 2: Paytm Transaction Lineage")
    paytm_assets = demo.demo_paytm_transaction_lineage()
    
    # Demo 3: Impact analysis
    print("\n📈 Demo 3: Impact Analysis")
    impact = demo.demo_impact_analysis(paytm_assets['processed_asset_id'])
    
    # Generate lineage visualization
    print("\n🎨 Generating lineage visualization...")
    viz_path = demo.lineage_tracker.visualize_lineage(
        paytm_assets['processed_asset_id'],
        "/tmp/paytm_lineage.png"
    )
    
    if viz_path:
        print(f"   Lineage graph saved to: {viz_path}")
    
    # Cost summary for Indian companies
    total_cost_inr = 250 + 150 + 50  # ETL + Feature Engineering + Reporting
    print(f"\n💰 Daily data processing cost: ₹{total_cost_inr:,.2f}")
    print(f"   Monthly estimated cost: ₹{total_cost_inr * 30:,.2f}")
    print(f"   Annual estimated cost: ₹{total_cost_inr * 365:,.2f}")
    
    print("\n✅ DataOps versioning and lineage demo completed!")
    print("\n📋 Key features demonstrated:")
    print("   ✓ Data asset versioning with checksums")
    print("   ✓ Schema evolution tracking")
    print("   ✓ End-to-end lineage tracking")
    print("   ✓ Impact analysis for changes")
    print("   ✓ Visual lineage representation")
    print("   ✓ Cost tracking in INR")
    print("   ✓ Indian company specific examples")

if __name__ == "__main__":
    main()
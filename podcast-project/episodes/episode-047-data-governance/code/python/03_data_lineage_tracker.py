#!/usr/bin/env python3
"""
Data Lineage Tracker and Impact Analysis System
Episode 47: Data Governance at Scale

Mumbai ki local train system की तरह, यह system track करता है कि data
कहां से आया, कहां गया, और किसने क्या transformation किया।

Author: Hindi Podcast Series
Context: End-to-end data lineage tracking for complex data pipelines
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import hashlib
from pathlib import Path
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataOperationType(Enum):
    """Types of data operations"""
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    AGGREGATE = "aggregate"
    JOIN = "join"
    FILTER = "filter"
    ENRICH = "enrich"
    VALIDATE = "validate"
    EXPORT = "export"

class DataQualityStatus(Enum):
    """Data quality status"""
    GOOD = "good"
    WARNING = "warning"
    POOR = "poor"
    UNKNOWN = "unknown"

@dataclass
class DataAsset:
    """Data asset definition"""
    asset_id: str
    name: str
    asset_type: str  # table, file, api, stream
    location: str
    schema: Dict[str, str]  # field_name -> data_type
    owner: str
    created_at: datetime
    updated_at: datetime
    description: str
    tags: List[str]
    quality_status: DataQualityStatus

@dataclass
class DataTransformation:
    """Data transformation record"""
    transformation_id: str
    source_assets: List[str]
    target_asset: str
    operation_type: DataOperationType
    transformation_logic: str
    fields_used: List[str]
    fields_created: List[str]
    executed_by: str
    executed_at: datetime
    execution_duration: float  # seconds
    records_processed: int
    success: bool
    error_message: Optional[str]

@dataclass
class LineageNode:
    """Node in data lineage graph"""
    node_id: str
    asset: DataAsset
    level: int  # Distance from source
    children: Set[str]
    parents: Set[str]

class DataLineageTracker:
    """
    Comprehensive data lineage tracking system
    
    Features:
    - Asset registration and discovery
    - Transformation tracking
    - Impact analysis
    - Column-level lineage
    - Data quality propagation
    - Compliance tracking
    """
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.lineage_graph = nx.DiGraph()
        self.assets = {}
        self.transformations = {}
        self.init_database()
        
        logger.info("Data lineage tracker initialized")
    
    def init_database(self):
        """Initialize SQLite database for lineage storage"""
        self.conn = sqlite3.connect(self.db_path)
        
        # Create tables
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                asset_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                location TEXT NOT NULL,
                schema_json TEXT,
                owner TEXT NOT NULL,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                description TEXT,
                tags_json TEXT,
                quality_status TEXT
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS transformations (
                transformation_id TEXT PRIMARY KEY,
                source_assets_json TEXT,
                target_asset TEXT,
                operation_type TEXT,
                transformation_logic TEXT,
                fields_used_json TEXT,
                fields_created_json TEXT,
                executed_by TEXT,
                executed_at TIMESTAMP,
                execution_duration REAL,
                records_processed INTEGER,
                success BOOLEAN,
                error_message TEXT
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS lineage_edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_asset TEXT,
                target_asset TEXT,
                transformation_id TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (transformation_id) REFERENCES transformations (transformation_id)
            )
        ''')
        
        self.conn.commit()
    
    def register_asset(self, asset: DataAsset) -> str:
        """Register a data asset"""
        self.assets[asset.asset_id] = asset
        
        # Store in database
        self.conn.execute('''
            INSERT OR REPLACE INTO assets 
            (asset_id, name, asset_type, location, schema_json, owner, 
             created_at, updated_at, description, tags_json, quality_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            asset.asset_id,
            asset.name,
            asset.asset_type,
            asset.location,
            json.dumps(asset.schema),
            asset.owner,
            asset.created_at,
            asset.updated_at,
            asset.description,
            json.dumps(asset.tags),
            asset.quality_status.value
        ))
        
        self.conn.commit()
        
        # Add to graph
        self.lineage_graph.add_node(asset.asset_id, **asdict(asset))
        
        logger.info(f"Registered asset: {asset.name} ({asset.asset_id})")
        
        return asset.asset_id
    
    def track_transformation(self, transformation: DataTransformation) -> str:
        """Track a data transformation"""
        self.transformations[transformation.transformation_id] = transformation
        
        # Store in database
        self.conn.execute('''
            INSERT OR REPLACE INTO transformations 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transformation.transformation_id,
            json.dumps(transformation.source_assets),
            transformation.target_asset,
            transformation.operation_type.value,
            transformation.transformation_logic,
            json.dumps(transformation.fields_used),
            json.dumps(transformation.fields_created),
            transformation.executed_by,
            transformation.executed_at,
            transformation.execution_duration,
            transformation.records_processed,
            transformation.success,
            transformation.error_message
        ))
        
        # Create lineage edges
        for source_asset in transformation.source_assets:
            self.conn.execute('''
                INSERT INTO lineage_edges (source_asset, target_asset, transformation_id, created_at)
                VALUES (?, ?, ?, ?)
            ''', (source_asset, transformation.target_asset, 
                  transformation.transformation_id, datetime.now()))
            
            # Add edge to graph
            self.lineage_graph.add_edge(
                source_asset, 
                transformation.target_asset,
                transformation_id=transformation.transformation_id,
                operation_type=transformation.operation_type.value,
                executed_at=transformation.executed_at
            )
        
        self.conn.commit()
        
        logger.info(f"Tracked transformation: {transformation.transformation_id}")
        
        return transformation.transformation_id
    
    def get_upstream_lineage(self, asset_id: str, max_depth: int = 10) -> Dict[str, Any]:
        """Get upstream data lineage for an asset"""
        if asset_id not in self.lineage_graph:
            return {"error": f"Asset {asset_id} not found"}
        
        upstream_assets = []
        visited = set()
        
        def traverse_upstream(current_asset, depth=0):
            if depth >= max_depth or current_asset in visited:
                return
            
            visited.add(current_asset)
            
            # Get predecessors (upstream assets)
            predecessors = list(self.lineage_graph.predecessors(current_asset))
            
            for predecessor in predecessors:
                edge_data = self.lineage_graph[predecessor][current_asset]
                transformation_id = edge_data.get('transformation_id')
                
                transformation = self.transformations.get(transformation_id)
                
                upstream_info = {
                    'asset_id': predecessor,
                    'asset_name': self.assets[predecessor].name if predecessor in self.assets else 'Unknown',
                    'transformation_id': transformation_id,
                    'operation_type': edge_data.get('operation_type'),
                    'executed_at': edge_data.get('executed_at'),
                    'depth': depth + 1
                }
                
                if transformation:
                    upstream_info.update({
                        'transformation_logic': transformation.transformation_logic,
                        'fields_used': transformation.fields_used,
                        'records_processed': transformation.records_processed,
                        'success': transformation.success
                    })
                
                upstream_assets.append(upstream_info)
                
                # Recursive call
                traverse_upstream(predecessor, depth + 1)
        
        traverse_upstream(asset_id)
        
        return {
            'target_asset': asset_id,
            'upstream_assets': upstream_assets,
            'total_upstream': len(upstream_assets)
        }
    
    def get_downstream_lineage(self, asset_id: str, max_depth: int = 10) -> Dict[str, Any]:
        """Get downstream data lineage for an asset"""
        if asset_id not in self.lineage_graph:
            return {"error": f"Asset {asset_id} not found"}
        
        downstream_assets = []
        visited = set()
        
        def traverse_downstream(current_asset, depth=0):
            if depth >= max_depth or current_asset in visited:
                return
            
            visited.add(current_asset)
            
            # Get successors (downstream assets)
            successors = list(self.lineage_graph.successors(current_asset))
            
            for successor in successors:
                edge_data = self.lineage_graph[current_asset][successor]
                transformation_id = edge_data.get('transformation_id')
                
                transformation = self.transformations.get(transformation_id)
                
                downstream_info = {
                    'asset_id': successor,
                    'asset_name': self.assets[successor].name if successor in self.assets else 'Unknown',
                    'transformation_id': transformation_id,
                    'operation_type': edge_data.get('operation_type'),
                    'executed_at': edge_data.get('executed_at'),
                    'depth': depth + 1
                }
                
                if transformation:
                    downstream_info.update({
                        'transformation_logic': transformation.transformation_logic,
                        'fields_created': transformation.fields_created,
                        'records_processed': transformation.records_processed,
                        'success': transformation.success
                    })
                
                downstream_assets.append(downstream_info)
                
                # Recursive call
                traverse_downstream(successor, depth + 1)
        
        traverse_downstream(asset_id)
        
        return {
            'source_asset': asset_id,
            'downstream_assets': downstream_assets,
            'total_downstream': len(downstream_assets)
        }
    
    def analyze_impact(self, asset_id: str) -> Dict[str, Any]:
        """Analyze impact of changes to an asset"""
        downstream = self.get_downstream_lineage(asset_id)
        
        if "error" in downstream:
            return downstream
        
        # Categorize impacted assets
        impacted_assets = downstream['downstream_assets']
        
        # Group by asset type
        impact_by_type = {}
        impact_by_owner = {}
        critical_paths = []
        
        for asset_info in impacted_assets:
            asset_id_downstream = asset_info['asset_id']
            
            if asset_id_downstream in self.assets:
                asset = self.assets[asset_id_downstream]
                
                # By type
                if asset.asset_type not in impact_by_type:
                    impact_by_type[asset.asset_type] = 0
                impact_by_type[asset.asset_type] += 1
                
                # By owner
                if asset.owner not in impact_by_owner:
                    impact_by_owner[asset.owner] = []
                impact_by_owner[asset.owner].append(asset.name)
                
                # Critical paths (reports, dashboards)
                if asset.asset_type in ['dashboard', 'report', 'ml_model']:
                    critical_paths.append({
                        'asset_name': asset.name,
                        'asset_type': asset.asset_type,
                        'owner': asset.owner,
                        'depth': asset_info['depth']
                    })
        
        return {
            'source_asset': asset_id,
            'total_impacted_assets': len(impacted_assets),
            'impact_by_type': impact_by_type,
            'impact_by_owner': impact_by_owner,
            'critical_paths': critical_paths,
            'max_depth': max(asset_info['depth'] for asset_info in impacted_assets) if impacted_assets else 0,
            'recommendations': self.generate_impact_recommendations(impacted_assets, critical_paths)
        }
    
    def generate_impact_recommendations(self, impacted_assets: List[Dict], 
                                      critical_paths: List[Dict]) -> List[str]:
        """Generate recommendations based on impact analysis"""
        recommendations = []
        
        total_impact = len(impacted_assets)
        critical_count = len(critical_paths)
        
        if total_impact == 0:
            recommendations.append("✅ No downstream dependencies found - safe to modify")
            return recommendations
        
        if critical_count > 0:
            recommendations.append(f"🚨 CRITICAL: {critical_count} business-critical assets will be impacted")
            recommendations.append("   - Coordinate with business stakeholders before changes")
            recommendations.append("   - Plan for testing of dashboards and reports")
        
        if total_impact > 10:
            recommendations.append(f"⚠️ HIGH IMPACT: {total_impact} assets will be affected")
            recommendations.append("   - Create comprehensive testing plan")
            recommendations.append("   - Consider phased rollout approach")
        elif total_impact > 5:
            recommendations.append(f"⚠️ MEDIUM IMPACT: {total_impact} assets will be affected")
            recommendations.append("   - Test downstream transformations")
        else:
            recommendations.append(f"ℹ️ LOW IMPACT: {total_impact} assets will be affected")
        
        recommendations.extend([
            "📧 Notify asset owners before making changes",
            "📝 Document all schema or logic changes",
            "🔄 Set up monitoring for downstream pipelines",
            "🧪 Run integration tests after changes"
        ])
        
        return recommendations
    
    def get_column_lineage(self, asset_id: str, column_name: str) -> Dict[str, Any]:
        """Get column-level lineage"""
        column_lineage = []
        
        # Get all transformations that target this asset
        upstream_lineage = self.get_upstream_lineage(asset_id)
        
        if "error" in upstream_lineage:
            return upstream_lineage
        
        for upstream_info in upstream_lineage['upstream_assets']:
            transformation_id = upstream_info.get('transformation_id')
            if transformation_id in self.transformations:
                transformation = self.transformations[transformation_id]
                
                # Check if this column was created or used in this transformation
                if column_name in transformation.fields_created or column_name in transformation.fields_used:
                    column_lineage.append({
                        'source_asset': upstream_info['asset_id'],
                        'transformation': transformation.transformation_logic,
                        'operation_type': transformation.operation_type.value,
                        'fields_used': transformation.fields_used,
                        'executed_at': transformation.executed_at
                    })
        
        return {
            'asset_id': asset_id,
            'column_name': column_name,
            'column_lineage': column_lineage,
            'lineage_depth': len(column_lineage)
        }
    
    def visualize_lineage(self, asset_id: str, output_path: str = None, 
                         include_upstream: bool = True, include_downstream: bool = True):
        """Create visual representation of data lineage"""
        import matplotlib.pyplot as plt
        import networkx as nx
        
        # Create subgraph for visualization
        nodes_to_include = {asset_id}
        
        if include_upstream:
            upstream = self.get_upstream_lineage(asset_id)
            if "upstream_assets" in upstream:
                nodes_to_include.update([asset['asset_id'] for asset in upstream['upstream_assets']])
        
        if include_downstream:
            downstream = self.get_downstream_lineage(asset_id)
            if "downstream_assets" in downstream:
                nodes_to_include.update([asset['asset_id'] for asset in downstream['downstream_assets']])
        
        subgraph = self.lineage_graph.subgraph(nodes_to_include)
        
        # Create visualization
        plt.figure(figsize=(15, 10))
        
        # Position nodes
        pos = nx.spring_layout(subgraph, k=3, iterations=50)
        
        # Draw nodes with different colors by type
        node_colors = []
        for node in subgraph.nodes():
            if node in self.assets:
                asset_type = self.assets[node].asset_type
                if asset_type == 'source':
                    node_colors.append('lightgreen')
                elif asset_type == 'transform':
                    node_colors.append('lightblue')
                elif asset_type == 'target':
                    node_colors.append('lightcoral')
                else:
                    node_colors.append('lightgray')
            else:
                node_colors.append('lightgray')
        
        # Highlight the main asset
        main_asset_color = 'gold' if asset_id in subgraph.nodes() else None
        if main_asset_color:
            main_asset_idx = list(subgraph.nodes()).index(asset_id)
            node_colors[main_asset_idx] = main_asset_color
        
        # Draw the graph
        nx.draw(subgraph, pos, 
                node_color=node_colors,
                node_size=3000,
                with_labels=True,
                labels={node: self.assets[node].name if node in self.assets else node[:8] 
                        for node in subgraph.nodes()},
                font_size=8,
                font_weight='bold',
                arrows=True,
                arrowsize=20,
                edge_color='gray',
                alpha=0.7)
        
        plt.title(f"Data Lineage for {self.assets[asset_id].name if asset_id in self.assets else asset_id}", 
                 fontsize=16, fontweight='bold')
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', 
                      markersize=10, label='Source'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', 
                      markersize=10, label='Transform'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', 
                      markersize=10, label='Target'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gold', 
                      markersize=10, label='Focus Asset')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Lineage visualization saved to {output_path}")
        
        plt.show()
    
    def export_lineage_metadata(self, output_path: str):
        """Export complete lineage metadata"""
        metadata = {
            'assets': {asset_id: asdict(asset) for asset_id, asset in self.assets.items()},
            'transformations': {t_id: asdict(transformation) for t_id, transformation in self.transformations.items()},
            'lineage_edges': []
        }
        
        # Convert datetime objects to strings
        for asset_data in metadata['assets'].values():
            asset_data['created_at'] = asset_data['created_at'].isoformat()
            asset_data['updated_at'] = asset_data['updated_at'].isoformat()
            asset_data['quality_status'] = asset_data['quality_status'].value
        
        for trans_data in metadata['transformations'].values():
            trans_data['executed_at'] = trans_data['executed_at'].isoformat()
            trans_data['operation_type'] = trans_data['operation_type'].value
        
        # Add edges
        for edge in self.lineage_graph.edges(data=True):
            source, target, data = edge
            edge_info = {
                'source': source,
                'target': target,
                'transformation_id': data.get('transformation_id'),
                'operation_type': data.get('operation_type'),
                'executed_at': data.get('executed_at').isoformat() if data.get('executed_at') else None
            }
            metadata['lineage_edges'].append(edge_info)
        
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"Lineage metadata exported to {output_path}")

def create_sample_ecommerce_pipeline():
    """Create sample e-commerce data pipeline for demonstration"""
    tracker = DataLineageTracker()
    
    # Create sample assets - Mumbai e-commerce pipeline
    
    # 1. Source systems
    orders_api = DataAsset(
        asset_id="flipkart_orders_api",
        name="Flipkart Orders API",
        asset_type="api",
        location="https://api.flipkart.com/orders",
        schema={"order_id": "string", "customer_id": "string", "amount": "decimal", "created_at": "timestamp"},
        owner="orders-team@flipkart.com",
        created_at=datetime(2023, 1, 1),
        updated_at=datetime.now(),
        description="Real-time orders from Flipkart platform",
        tags=["source", "realtime", "orders"],
        quality_status=DataQualityStatus.GOOD
    )
    
    customers_db = DataAsset(
        asset_id="customer_master_db",
        name="Customer Master Database",
        asset_type="table",
        location="mysql://prod-db/customers",
        schema={"customer_id": "string", "name": "string", "email": "string", "city": "string"},
        owner="customer-team@flipkart.com",
        created_at=datetime(2022, 6, 1),
        updated_at=datetime.now(),
        description="Master customer information",
        tags=["master", "customers", "pii"],
        quality_status=DataQualityStatus.GOOD
    )
    
    # 2. Staging area
    orders_staging = DataAsset(
        asset_id="orders_staging_table",
        name="Orders Staging Table",
        asset_type="table",
        location="snowflake://warehouse/staging.orders",
        schema={"order_id": "string", "customer_id": "string", "amount": "decimal", "order_date": "date", "processed_at": "timestamp"},
        owner="data-eng@flipkart.com",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        description="Staging area for order data",
        tags=["staging", "etl"],
        quality_status=DataQualityStatus.GOOD
    )
    
    # 3. Enriched data
    enriched_orders = DataAsset(
        asset_id="enriched_orders_table",
        name="Enriched Orders with Customer Info",
        asset_type="table",
        location="snowflake://warehouse/marts.enriched_orders",
        schema={
            "order_id": "string", "customer_id": "string", "customer_name": "string", 
            "customer_city": "string", "amount": "decimal", "order_date": "date"
        },
        owner="data-eng@flipkart.com",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        description="Orders enriched with customer information",
        tags=["mart", "enriched", "analytics"],
        quality_status=DataQualityStatus.GOOD
    )
    
    # 4. Analytics tables
    daily_sales_report = DataAsset(
        asset_id="daily_sales_report",
        name="Daily Sales Report",
        asset_type="report",
        location="tableau://dashboards/daily_sales",
        schema={"sale_date": "date", "total_amount": "decimal", "order_count": "integer", "avg_order_value": "decimal"},
        owner="analytics-team@flipkart.com",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        description="Daily sales performance report",
        tags=["report", "daily", "sales"],
        quality_status=DataQualityStatus.WARNING
    )
    
    # Register all assets
    for asset in [orders_api, customers_db, orders_staging, enriched_orders, daily_sales_report]:
        tracker.register_asset(asset)
    
    # Create transformations
    
    # 1. Extract orders from API to staging
    extract_orders = DataTransformation(
        transformation_id="extract_orders_001",
        source_assets=["flipkart_orders_api"],
        target_asset="orders_staging_table",
        operation_type=DataOperationType.EXTRACT,
        transformation_logic="SELECT order_id, customer_id, amount, DATE(created_at) as order_date, NOW() as processed_at FROM orders_api WHERE DATE(created_at) = CURRENT_DATE",
        fields_used=["order_id", "customer_id", "amount", "created_at"],
        fields_created=["order_date", "processed_at"],
        executed_by="airflow-worker",
        executed_at=datetime.now(),
        execution_duration=45.5,
        records_processed=12567,
        success=True,
        error_message=None
    )
    
    # 2. Enrich orders with customer data
    enrich_orders = DataTransformation(
        transformation_id="enrich_orders_001",
        source_assets=["orders_staging_table", "customer_master_db"],
        target_asset="enriched_orders_table",
        operation_type=DataOperationType.JOIN,
        transformation_logic="""
        SELECT o.order_id, o.customer_id, c.name as customer_name, c.city as customer_city, 
               o.amount, o.order_date
        FROM orders_staging_table o
        LEFT JOIN customer_master_db c ON o.customer_id = c.customer_id
        """,
        fields_used=["order_id", "customer_id", "amount", "order_date", "name", "city"],
        fields_created=["customer_name", "customer_city"],
        executed_by="dbt-cloud",
        executed_at=datetime.now(),
        execution_duration=125.8,
        records_processed=12567,
        success=True,
        error_message=None
    )
    
    # 3. Generate daily sales report
    generate_report = DataTransformation(
        transformation_id="daily_sales_report_001",
        source_assets=["enriched_orders_table"],
        target_asset="daily_sales_report",
        operation_type=DataOperationType.AGGREGATE,
        transformation_logic="""
        SELECT 
            order_date as sale_date,
            SUM(amount) as total_amount,
            COUNT(*) as order_count,
            AVG(amount) as avg_order_value
        FROM enriched_orders_table
        WHERE order_date = CURRENT_DATE
        GROUP BY order_date
        """,
        fields_used=["order_date", "amount"],
        fields_created=["sale_date", "total_amount", "order_count", "avg_order_value"],
        executed_by="tableau-refresh",
        executed_at=datetime.now(),
        execution_duration=15.2,
        records_processed=1,
        success=True,
        error_message=None
    )
    
    # Track all transformations
    for transformation in [extract_orders, enrich_orders, generate_report]:
        tracker.track_transformation(transformation)
    
    return tracker

def main():
    """Main function demonstrating data lineage tracker"""
    print("🔗 Starting Data Lineage Tracker Demo")
    print("=" * 60)
    
    # Create sample e-commerce pipeline
    print("Creating sample e-commerce data pipeline...")
    tracker = create_sample_ecommerce_pipeline()
    
    print(f"✅ Pipeline created with {len(tracker.assets)} assets and {len(tracker.transformations)} transformations")
    print()
    
    # Test upstream lineage
    print("🔍 Analyzing upstream lineage for Daily Sales Report...")
    upstream = tracker.get_upstream_lineage("daily_sales_report")
    print(f"Found {upstream['total_upstream']} upstream dependencies:")
    
    for asset in upstream['upstream_assets']:
        print(f"  - {asset['asset_name']} ({asset['operation_type']}) at depth {asset['depth']}")
    print()
    
    # Test downstream lineage
    print("🔍 Analyzing downstream lineage for Orders API...")
    downstream = tracker.get_downstream_lineage("flipkart_orders_api")
    print(f"Found {downstream['total_downstream']} downstream dependencies:")
    
    for asset in downstream['downstream_assets']:
        print(f"  - {asset['asset_name']} ({asset['operation_type']}) at depth {asset['depth']}")
    print()
    
    # Impact analysis
    print("💥 Performing impact analysis for Customer Master Database...")
    impact = tracker.analyze_impact("customer_master_db")
    
    print(f"Total impacted assets: {impact['total_impacted_assets']}")
    print(f"Critical paths: {len(impact['critical_paths'])}")
    print(f"Impact by type: {impact['impact_by_type']}")
    
    print("\n🚀 Recommendations:")
    for i, recommendation in enumerate(impact['recommendations'], 1):
        print(f"{i}. {recommendation}")
    
    # Column-level lineage
    print("\n📊 Column-level lineage for 'total_amount' in Daily Sales Report:")
    column_lineage = tracker.get_column_lineage("daily_sales_report", "total_amount")
    
    print(f"Lineage depth: {column_lineage['lineage_depth']}")
    for lineage_step in column_lineage['column_lineage']:
        print(f"  - Source: {lineage_step['source_asset']}")
        print(f"    Operation: {lineage_step['operation_type']}")
        print(f"    Fields used: {lineage_step['fields_used']}")
    
    # Export metadata
    print("\n📤 Exporting lineage metadata...")
    tracker.export_lineage_metadata("/tmp/lineage_metadata.json")
    print("Metadata exported successfully!")
    
    print("\n✅ Data lineage tracking demo completed successfully!")

if __name__ == "__main__":
    main()
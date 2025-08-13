#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 13
Data Lineage Tracking System

Complete data lineage tracking for data pipelines and transformations
Data pipelines और transformations के लिए complete data lineage tracking

Author: DStudio Team
Context: Data lineage like Flipkart/Amazon data engineering teams
Scale: Track lineage for 100+ TB data processing daily
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque
import uuid
import hashlib
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import re

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - डेटा वंशावली - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """Data source definition"""
    source_id: str
    source_name: str
    source_type: str  # 'database', 'file', 'api', 'stream'
    location: str
    schema: Dict[str, str]
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataTransformation:
    """Data transformation definition"""
    transformation_id: str
    transformation_name: str
    transformation_type: str  # 'filter', 'aggregate', 'join', 'custom'
    input_sources: List[str]
    output_target: str
    transformation_logic: str
    executed_at: datetime
    executed_by: str
    execution_time: float
    records_input: int
    records_output: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataQualityIssue:
    """Data quality issue tracking"""
    issue_id: str
    source_id: str
    transformation_id: Optional[str]
    issue_type: str
    severity: str
    description: str
    detected_at: datetime
    affected_records: int
    resolved: bool = False
    resolution_notes: Optional[str] = None

class DataLineageTracker:
    """
    Complete data lineage tracking system for data pipelines
    Data pipelines के लिए complete data lineage tracking system
    
    Features:
    1. Track data sources and transformations
    2. Maintain complete lineage graph
    3. Impact analysis for changes
    4. Data quality issue tracking
    5. Compliance and audit trails
    6. Visualization of data flow
    
    Scale: Handle lineage for 100+ TB daily data processing
    """
    
    def __init__(self, db_path: str = 'data_lineage.db'):
        """Initialize data lineage tracker"""
        
        self.db_path = db_path
        self.db_connection = None
        
        # In-memory lineage graph for fast queries
        self.lineage_graph = nx.DiGraph()
        
        # Cache for frequently accessed lineage paths
        self.lineage_cache = {}
        
        # Data source registry
        self.data_sources = {}
        
        # Transformation history
        self.transformations = {}
        
        # Quality issues tracking
        self.quality_issues = {}
        
        # Initialize database
        self._init_database()
        
        # Load existing lineage data
        self._load_lineage_data()
        
        logger.info("Data Lineage Tracker initialized - डेटा वंशावली ट्रैकर तैयार!")

    def _init_database(self):
        """Initialize SQLite database for lineage storage"""
        try:
            self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.db_connection.cursor()
            
            # Data sources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_sources (
                    source_id TEXT PRIMARY KEY,
                    source_name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    location TEXT NOT NULL,
                    schema_json TEXT,
                    created_at DATETIME,
                    metadata_json TEXT
                )
            ''')
            
            # Transformations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transformations (
                    transformation_id TEXT PRIMARY KEY,
                    transformation_name TEXT NOT NULL,
                    transformation_type TEXT NOT NULL,
                    input_sources_json TEXT,
                    output_target TEXT,
                    transformation_logic TEXT,
                    executed_at DATETIME,
                    executed_by TEXT,
                    execution_time REAL,
                    records_input INTEGER,
                    records_output INTEGER,
                    metadata_json TEXT
                )
            ''')
            
            # Lineage relationships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lineage_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT,
                    target_id TEXT,
                    transformation_id TEXT,
                    relationship_type TEXT,
                    created_at DATETIME,
                    FOREIGN KEY (transformation_id) REFERENCES transformations(transformation_id)
                )
            ''')
            
            # Data quality issues table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_issues (
                    issue_id TEXT PRIMARY KEY,
                    source_id TEXT,
                    transformation_id TEXT,
                    issue_type TEXT,
                    severity TEXT,
                    description TEXT,
                    detected_at DATETIME,
                    affected_records INTEGER,
                    resolved BOOLEAN,
                    resolution_notes TEXT,
                    FOREIGN KEY (source_id) REFERENCES data_sources(source_id),
                    FOREIGN KEY (transformation_id) REFERENCES transformations(transformation_id)
                )
            ''')
            
            # Column-level lineage table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS column_lineage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_column TEXT,
                    target_column TEXT,
                    transformation_id TEXT,
                    transformation_logic TEXT,
                    created_at DATETIME,
                    FOREIGN KEY (transformation_id) REFERENCES transformations(transformation_id)
                )
            ''')
            
            self.db_connection.commit()
            logger.info("Lineage database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.db_connection = None

    def _load_lineage_data(self):
        """Load existing lineage data from database"""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Load data sources
            cursor.execute('SELECT * FROM data_sources')
            for row in cursor.fetchall():
                source = DataSource(
                    source_id=row[0],
                    source_name=row[1],
                    source_type=row[2],
                    location=row[3],
                    schema=json.loads(row[4]) if row[4] else {},
                    created_at=datetime.fromisoformat(row[5]),
                    metadata=json.loads(row[6]) if row[6] else {}
                )
                self.data_sources[source.source_id] = source
                self.lineage_graph.add_node(source.source_id, **asdict(source))
            
            # Load transformations
            cursor.execute('SELECT * FROM transformations')
            for row in cursor.fetchall():
                transformation = DataTransformation(
                    transformation_id=row[0],
                    transformation_name=row[1],
                    transformation_type=row[2],
                    input_sources=json.loads(row[3]),
                    output_target=row[4],
                    transformation_logic=row[5],
                    executed_at=datetime.fromisoformat(row[6]),
                    executed_by=row[7],
                    execution_time=row[8],
                    records_input=row[9],
                    records_output=row[10],
                    metadata=json.loads(row[11]) if row[11] else {}
                )
                self.transformations[transformation.transformation_id] = transformation
            
            # Load lineage relationships
            cursor.execute('SELECT * FROM lineage_relationships')
            for row in cursor.fetchall():
                source_id, target_id, transformation_id = row[1], row[2], row[3]
                self.lineage_graph.add_edge(
                    source_id, target_id,
                    transformation_id=transformation_id,
                    relationship_type=row[4],
                    created_at=row[5]
                )
            
            logger.info(f"Loaded {len(self.data_sources)} sources and {len(self.transformations)} transformations")
            
        except Exception as e:
            logger.error(f"Failed to load lineage data: {e}")

    def register_data_source(self, source: DataSource) -> bool:
        """
        Register a new data source in the lineage
        Lineage में नया data source register करना
        """
        try:
            # Add to in-memory structures
            self.data_sources[source.source_id] = source
            self.lineage_graph.add_node(source.source_id, **asdict(source))
            
            # Store in database
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO data_sources 
                    (source_id, source_name, source_type, location, schema_json, created_at, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    source.source_id,
                    source.source_name,
                    source.source_type,
                    source.location,
                    json.dumps(source.schema),
                    source.created_at.isoformat(),
                    json.dumps(source.metadata)
                ))
                self.db_connection.commit()
            
            logger.info(f"Registered data source: {source.source_name} ({source.source_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register data source: {e}")
            return False

    def record_transformation(self, transformation: DataTransformation) -> bool:
        """
        Record a data transformation and update lineage
        Data transformation record करना और lineage update करना
        """
        try:
            # Add to in-memory structures
            self.transformations[transformation.transformation_id] = transformation
            
            # Add lineage relationships
            for input_source in transformation.input_sources:
                self.lineage_graph.add_edge(
                    input_source,
                    transformation.output_target,
                    transformation_id=transformation.transformation_id,
                    transformation_name=transformation.transformation_name,
                    transformation_type=transformation.transformation_type,
                    executed_at=transformation.executed_at.isoformat()
                )
            
            # Store transformation in database
            if self.db_connection:
                cursor = self.db_connection.cursor()
                
                # Insert transformation
                cursor.execute('''
                    INSERT OR REPLACE INTO transformations 
                    (transformation_id, transformation_name, transformation_type, 
                     input_sources_json, output_target, transformation_logic,
                     executed_at, executed_by, execution_time, records_input, 
                     records_output, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transformation.transformation_id,
                    transformation.transformation_name,
                    transformation.transformation_type,
                    json.dumps(transformation.input_sources),
                    transformation.output_target,
                    transformation.transformation_logic,
                    transformation.executed_at.isoformat(),
                    transformation.executed_by,
                    transformation.execution_time,
                    transformation.records_input,
                    transformation.records_output,
                    json.dumps(transformation.metadata)
                ))
                
                # Insert lineage relationships
                for input_source in transformation.input_sources:
                    cursor.execute('''
                        INSERT INTO lineage_relationships 
                        (source_id, target_id, transformation_id, relationship_type, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        input_source,
                        transformation.output_target,
                        transformation.transformation_id,
                        'transformation',
                        datetime.now().isoformat()
                    ))
                
                self.db_connection.commit()
            
            # Clear cache as lineage has changed
            self.lineage_cache.clear()
            
            logger.info(f"Recorded transformation: {transformation.transformation_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record transformation: {e}")
            return False

    def trace_lineage_upstream(self, target_id: str, depth: int = 10) -> Dict[str, Any]:
        """
        Trace data lineage upstream from a target
        Target से upstream data lineage trace करना
        """
        
        cache_key = f"upstream_{target_id}_{depth}"
        if cache_key in self.lineage_cache:
            return self.lineage_cache[cache_key]
        
        try:
            # Find all upstream sources within specified depth
            upstream_nodes = set()
            transformation_path = []
            
            # BFS to find upstream lineage
            queue = deque([(target_id, 0)])
            visited = {target_id}
            
            while queue:
                current_node, current_depth = queue.popleft()
                
                if current_depth >= depth:
                    continue
                
                # Get predecessors (upstream sources)
                for predecessor in self.lineage_graph.predecessors(current_node):
                    if predecessor not in visited:
                        visited.add(predecessor)
                        upstream_nodes.add(predecessor)
                        
                        # Get transformation details
                        edge_data = self.lineage_graph.get_edge_data(predecessor, current_node)
                        if edge_data:
                            transformation_path.append({
                                'source': predecessor,
                                'target': current_node,
                                'transformation_id': edge_data.get('transformation_id'),
                                'transformation_name': edge_data.get('transformation_name'),
                                'transformation_type': edge_data.get('transformation_type'),
                                'executed_at': edge_data.get('executed_at')
                            })
                        
                        queue.append((predecessor, current_depth + 1))
            
            # Build detailed lineage information
            lineage_info = {
                'target_id': target_id,
                'upstream_sources': list(upstream_nodes),
                'transformation_path': transformation_path,
                'total_upstream_sources': len(upstream_nodes),
                'lineage_depth': depth,
                'generated_at': datetime.now().isoformat()
            }
            
            # Add source details
            source_details = {}
            for source_id in upstream_nodes:
                if source_id in self.data_sources:
                    source_details[source_id] = asdict(self.data_sources[source_id])
            
            lineage_info['source_details'] = source_details
            
            # Cache the result
            self.lineage_cache[cache_key] = lineage_info
            
            return lineage_info
            
        except Exception as e:
            logger.error(f"Failed to trace upstream lineage: {e}")
            return {'error': str(e)}

    def trace_lineage_downstream(self, source_id: str, depth: int = 10) -> Dict[str, Any]:
        """
        Trace data lineage downstream from a source
        Source से downstream data lineage trace करना
        """
        
        cache_key = f"downstream_{source_id}_{depth}"
        if cache_key in self.lineage_cache:
            return self.lineage_cache[cache_key]
        
        try:
            # Find all downstream targets within specified depth
            downstream_nodes = set()
            transformation_path = []
            
            # BFS to find downstream lineage
            queue = deque([(source_id, 0)])
            visited = {source_id}
            
            while queue:
                current_node, current_depth = queue.popleft()
                
                if current_depth >= depth:
                    continue
                
                # Get successors (downstream targets)
                for successor in self.lineage_graph.successors(current_node):
                    if successor not in visited:
                        visited.add(successor)
                        downstream_nodes.add(successor)
                        
                        # Get transformation details
                        edge_data = self.lineage_graph.get_edge_data(current_node, successor)
                        if edge_data:
                            transformation_path.append({
                                'source': current_node,
                                'target': successor,
                                'transformation_id': edge_data.get('transformation_id'),
                                'transformation_name': edge_data.get('transformation_name'),
                                'transformation_type': edge_data.get('transformation_type'),
                                'executed_at': edge_data.get('executed_at')
                            })
                        
                        queue.append((successor, current_depth + 1))
            
            # Build detailed lineage information
            lineage_info = {
                'source_id': source_id,
                'downstream_targets': list(downstream_nodes),
                'transformation_path': transformation_path,
                'total_downstream_targets': len(downstream_nodes),
                'lineage_depth': depth,
                'generated_at': datetime.now().isoformat()
            }
            
            # Cache the result
            self.lineage_cache[cache_key] = lineage_info
            
            return lineage_info
            
        except Exception as e:
            logger.error(f"Failed to trace downstream lineage: {e}")
            return {'error': str(e)}

    def impact_analysis(self, source_id: str) -> Dict[str, Any]:
        """
        Perform impact analysis for changes to a data source
        Data source के changes के लिए impact analysis
        """
        
        try:
            # Get downstream lineage
            downstream_lineage = self.trace_lineage_downstream(source_id)
            
            if 'error' in downstream_lineage:
                return downstream_lineage
            
            # Analyze impact on different components
            impacted_sources = set(downstream_lineage['downstream_targets'])
            impacted_transformations = set()
            
            # Get transformations that will be affected
            for transform_info in downstream_lineage['transformation_path']:
                if transform_info['transformation_id']:
                    impacted_transformations.add(transform_info['transformation_id'])
            
            # Categorize impact by source type
            impact_by_type = defaultdict(list)
            for target_id in impacted_sources:
                if target_id in self.data_sources:
                    source_type = self.data_sources[target_id].source_type
                    impact_by_type[source_type].append(target_id)
            
            # Calculate severity score
            severity_score = 0
            severity_score += len(impacted_sources) * 10  # Each impacted source adds 10 points
            severity_score += len(impacted_transformations) * 5  # Each transformation adds 5 points
            
            # Determine severity level
            if severity_score >= 100:
                severity_level = 'CRITICAL'
            elif severity_score >= 50:
                severity_level = 'HIGH'
            elif severity_score >= 20:
                severity_level = 'MEDIUM'
            else:
                severity_level = 'LOW'
            
            impact_analysis = {
                'source_id': source_id,
                'severity_level': severity_level,
                'severity_score': severity_score,
                'total_impacted_sources': len(impacted_sources),
                'total_impacted_transformations': len(impacted_transformations),
                'impacted_sources': list(impacted_sources),
                'impacted_transformations': list(impacted_transformations),
                'impact_by_type': dict(impact_by_type),
                'recommendations': self._generate_impact_recommendations(
                    severity_level, len(impacted_sources), len(impacted_transformations)
                ),
                'generated_at': datetime.now().isoformat()
            }
            
            return impact_analysis
            
        except Exception as e:
            logger.error(f"Failed to perform impact analysis: {e}")
            return {'error': str(e)}

    def _generate_impact_recommendations(self, severity: str, sources: int, transformations: int) -> List[str]:
        """Generate recommendations based on impact analysis"""
        
        recommendations = []
        
        if severity == 'CRITICAL':
            recommendations.append("CRITICAL: Schedule maintenance window for changes")
            recommendations.append("Notify all downstream teams before making changes")
            recommendations.append("Create rollback plan with data backups")
        
        elif severity == 'HIGH':
            recommendations.append("HIGH: Coordinate with downstream teams")
            recommendations.append("Test changes in staging environment first")
            recommendations.append("Monitor data quality after changes")
        
        elif severity == 'MEDIUM':
            recommendations.append("MEDIUM: Review impact with team lead")
            recommendations.append("Update documentation after changes")
        
        else:
            recommendations.append("LOW: Proceed with standard change process")
        
        if sources > 10:
            recommendations.append(f"Many sources affected ({sources}) - consider phased rollout")
        
        if transformations > 5:
            recommendations.append(f"Multiple transformations affected ({transformations}) - validate logic")
        
        return recommendations

    def visualize_lineage(self, focus_node: str, depth: int = 3) -> str:
        """
        Create interactive visualization of data lineage
        Data lineage का interactive visualization बनाना
        """
        
        try:
            # Get subgraph around focus node
            upstream = self.trace_lineage_upstream(focus_node, depth)
            downstream = self.trace_lineage_downstream(focus_node, depth)
            
            # Combine all nodes
            all_nodes = {focus_node}
            all_nodes.update(upstream.get('upstream_sources', []))
            all_nodes.update(downstream.get('downstream_targets', []))
            
            # Create subgraph
            subgraph = self.lineage_graph.subgraph(all_nodes)
            
            # Calculate layout
            pos = nx.spring_layout(subgraph, k=2, iterations=50)
            
            # Prepare data for Plotly
            edge_x = []
            edge_y = []
            edge_info = []
            
            for edge in subgraph.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                
                edge_data = subgraph.get_edge_data(edge[0], edge[1])
                edge_info.append(edge_data.get('transformation_name', 'Unknown'))
            
            # Node information
            node_x = []
            node_y = []
            node_text = []
            node_color = []
            
            for node in subgraph.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                # Node information
                if node in self.data_sources:
                    source = self.data_sources[node]
                    node_text.append(f"{source.source_name}<br>Type: {source.source_type}")
                    
                    # Color by type
                    if source.source_type == 'database':
                        node_color.append('blue')
                    elif source.source_type == 'file':
                        node_color.append('green')
                    elif source.source_type == 'api':
                        node_color.append('orange')
                    else:
                        node_color.append('gray')
                else:
                    node_text.append(node)
                    node_color.append('red')  # Missing source info
            
            # Create Plotly figure
            fig = go.Figure()
            
            # Add edges
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='lightgray'),
                hoverinfo='none',
                mode='lines',
                showlegend=False
            ))
            
            # Add nodes
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=[node.split('_')[-1] for node in subgraph.nodes()],  # Short labels
                hovertext=node_text,
                textposition="middle center",
                marker=dict(
                    size=30,
                    color=node_color,
                    line=dict(width=2, color='white')
                ),
                showlegend=False
            ))
            
            # Update layout
            fig.update_layout(
                title=f"Data Lineage for {focus_node}",
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="Hover over nodes for details",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='gray', size=12)
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            logger.error(f"Failed to create lineage visualization: {e}")
            return f"<html><body><h1>Error creating visualization: {e}</h1></body></html>"

    def generate_lineage_report(self) -> Dict[str, Any]:
        """Generate comprehensive lineage report"""
        
        try:
            # Basic statistics
            total_sources = len(self.data_sources)
            total_transformations = len(self.transformations)
            total_relationships = self.lineage_graph.number_of_edges()
            
            # Source type distribution
            source_type_dist = defaultdict(int)
            for source in self.data_sources.values():
                source_type_dist[source.source_type] += 1
            
            # Transformation type distribution
            transform_type_dist = defaultdict(int)
            for transform in self.transformations.values():
                transform_type_dist[transform.transformation_type] += 1
            
            # Complexity metrics
            avg_downstream = np.mean([len(list(self.lineage_graph.successors(node))) 
                                    for node in self.lineage_graph.nodes()]) if self.lineage_graph.nodes() else 0
            
            avg_upstream = np.mean([len(list(self.lineage_graph.predecessors(node))) 
                                  for node in self.lineage_graph.nodes()]) if self.lineage_graph.nodes() else 0
            
            # Most connected sources
            node_degrees = dict(self.lineage_graph.degree())
            most_connected = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
            
            report = {
                'report_generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_data_sources': total_sources,
                    'total_transformations': total_transformations,
                    'total_lineage_relationships': total_relationships,
                    'average_downstream_connections': round(avg_downstream, 2),
                    'average_upstream_connections': round(avg_upstream, 2)
                },
                'distributions': {
                    'source_types': dict(source_type_dist),
                    'transformation_types': dict(transform_type_dist)
                },
                'most_connected_sources': most_connected,
                'recommendations': self._generate_lineage_recommendations(
                    total_sources, total_transformations, avg_downstream, avg_upstream
                )
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate lineage report: {e}")
            return {'error': str(e)}

    def _generate_lineage_recommendations(self, sources: int, transforms: int, 
                                        avg_downstream: float, avg_upstream: float) -> List[str]:
        """Generate recommendations for lineage management"""
        
        recommendations = []
        
        if sources > 100:
            recommendations.append("Large number of sources - consider source consolidation")
        
        if transforms > 200:
            recommendations.append("Many transformations - review for optimization opportunities")
        
        if avg_downstream > 5:
            recommendations.append("High fan-out detected - consider data mart strategy")
        
        if avg_upstream > 5:
            recommendations.append("Complex joins detected - review transformation logic")
        
        recommendations.append("Regular lineage audits recommended")
        recommendations.append("Document business purpose for each transformation")
        
        return recommendations

def create_sample_lineage_data(tracker: DataLineageTracker):
    """Create sample lineage data for Indian e-commerce scenario"""
    
    # Sample data sources
    sources = [
        DataSource(
            source_id='orders_db',
            source_name='Orders Database',
            source_type='database',
            location='mysql://prod-db:3306/orders',
            schema={'order_id': 'string', 'customer_id': 'string', 'amount': 'decimal'},
            created_at=datetime.now() - timedelta(days=365),
            metadata={'owner': 'orders-team', 'sla': 'critical'}
        ),
        DataSource(
            source_id='customers_db',
            source_name='Customers Database',
            source_type='database',
            location='postgresql://prod-db:5432/customers',
            schema={'customer_id': 'string', 'name': 'string', 'email': 'string'},
            created_at=datetime.now() - timedelta(days=300),
            metadata={'owner': 'customer-team', 'sla': 'high'}
        ),
        DataSource(
            source_id='payment_api',
            source_name='Payment Gateway API',
            source_type='api',
            location='https://api.razorpay.com/v1/payments',
            schema={'payment_id': 'string', 'amount': 'decimal', 'status': 'string'},
            created_at=datetime.now() - timedelta(days=200),
            metadata={'owner': 'payments-team', 'rate_limit': '1000/min'}
        ),
        DataSource(
            source_id='flipkart_orders_mart',
            source_name='Flipkart Orders Data Mart',
            source_type='database',
            location='bigquery://analytics/flipkart_orders',
            schema={'order_id': 'string', 'customer_name': 'string', 'order_value': 'decimal'},
            created_at=datetime.now() - timedelta(days=100),
            metadata={'owner': 'analytics-team', 'refresh': 'daily'}
        )
    ]
    
    # Register sources
    for source in sources:
        tracker.register_data_source(source)
    
    # Sample transformations
    transformations = [
        DataTransformation(
            transformation_id='orders_enrichment',
            transformation_name='Orders Customer Enrichment',
            transformation_type='join',
            input_sources=['orders_db', 'customers_db'],
            output_target='enriched_orders_temp',
            transformation_logic='SELECT o.*, c.name, c.email FROM orders o JOIN customers c ON o.customer_id = c.customer_id',
            executed_at=datetime.now() - timedelta(hours=2),
            executed_by='etl-service',
            execution_time=120.5,
            records_input=1000000,
            records_output=980000,
            metadata={'job_id': 'job_12345', 'cluster': 'spark-prod'}
        ),
        DataTransformation(
            transformation_id='payment_aggregation',
            transformation_name='Daily Payment Aggregation',
            transformation_type='aggregate',
            input_sources=['payment_api'],
            output_target='daily_payments_summary',
            transformation_logic='SELECT DATE(created_at) as date, SUM(amount) as total_amount, COUNT(*) as transaction_count FROM payments GROUP BY DATE(created_at)',
            executed_at=datetime.now() - timedelta(hours=1),
            executed_by='analytics-pipeline',
            execution_time=45.2,
            records_input=500000,
            records_output=30,
            metadata={'schedule': 'daily', 'priority': 'high'}
        ),
        DataTransformation(
            transformation_id='orders_mart_creation',
            transformation_name='Create Flipkart Orders Mart',
            transformation_type='custom',
            input_sources=['enriched_orders_temp', 'daily_payments_summary'],
            output_target='flipkart_orders_mart',
            transformation_logic='Complex ETL logic for creating orders data mart with payment information',
            executed_at=datetime.now() - timedelta(minutes=30),
            executed_by='data-engineering',
            execution_time=300.8,
            records_input=980000,
            records_output=975000,
            metadata={'version': '2.1', 'data_quality_score': 0.99}
        )
    ]
    
    # Record transformations
    for transformation in transformations:
        tracker.record_transformation(transformation)
    
    logger.info("Sample lineage data created successfully")

def main():
    """Main execution function - demo of data lineage tracking system"""
    
    print("🔗 Data Lineage Tracking System Demo")
    print("डेटा वंशावली ट्रैकिंग सिस्टम का प्रदर्शन\n")
    
    # Initialize tracker
    tracker = DataLineageTracker('demo_lineage.db')
    
    # Test 1: Create sample lineage data
    print("Test 1: Creating Sample Lineage Data")
    print("=" * 35)
    
    create_sample_lineage_data(tracker)
    print("Sample lineage data created with Indian e-commerce scenario")
    
    # Test 2: Trace upstream lineage
    print("\nTest 2: Upstream Lineage Tracing")
    print("=" * 35)
    
    upstream_lineage = tracker.trace_lineage_upstream('flipkart_orders_mart')
    
    if 'error' not in upstream_lineage:
        print(f"""
        Upstream Lineage for 'flipkart_orders_mart':
        ==========================================
        Total upstream sources: {upstream_lineage['total_upstream_sources']}
        Upstream sources: {upstream_lineage['upstream_sources']}
        
        Transformation Path:
        """)
        
        for i, transform in enumerate(upstream_lineage['transformation_path']):
            print(f"{i+1}. {transform['source']} → {transform['target']}")
            print(f"   Transformation: {transform['transformation_name']}")
            print(f"   Type: {transform['transformation_type']}")
            print()
    else:
        print(f"Error tracing upstream lineage: {upstream_lineage['error']}")
    
    # Test 3: Trace downstream lineage
    print("\nTest 3: Downstream Lineage Tracing")
    print("=" * 35)
    
    downstream_lineage = tracker.trace_lineage_downstream('orders_db')
    
    if 'error' not in downstream_lineage:
        print(f"""
        Downstream Lineage for 'orders_db':
        ===================================
        Total downstream targets: {downstream_lineage['total_downstream_targets']}
        Downstream targets: {downstream_lineage['downstream_targets']}
        """)
    else:
        print(f"Error tracing downstream lineage: {downstream_lineage['error']}")
    
    # Test 4: Impact analysis
    print("\nTest 4: Impact Analysis")
    print("=" * 25)
    
    impact_analysis = tracker.impact_analysis('orders_db')
    
    if 'error' not in impact_analysis:
        print(f"""
        Impact Analysis for 'orders_db':
        ===============================
        Severity Level: {impact_analysis['severity_level']}
        Severity Score: {impact_analysis['severity_score']}
        Impacted Sources: {impact_analysis['total_impacted_sources']}
        Impacted Transformations: {impact_analysis['total_impacted_transformations']}
        
        Impact by Type:
        {json.dumps(impact_analysis['impact_by_type'], indent=2)}
        
        Recommendations:
        {chr(10).join(['- ' + rec for rec in impact_analysis['recommendations']])}
        """)
    else:
        print(f"Error in impact analysis: {impact_analysis['error']}")
    
    # Test 5: Lineage visualization
    print("\nTest 5: Lineage Visualization")
    print("=" * 30)
    
    visualization_html = tracker.visualize_lineage('flipkart_orders_mart', depth=3)
    
    # Save visualization to file
    with open('lineage_visualization.html', 'w', encoding='utf-8') as f:
        f.write(visualization_html)
    
    print("Lineage visualization created and saved as 'lineage_visualization.html'")
    print("Open this file in a web browser to view the interactive lineage graph")
    
    # Test 6: Generate comprehensive report
    print("\nTest 6: Lineage Report Generation")
    print("=" * 35)
    
    report = tracker.generate_lineage_report()
    
    if 'error' not in report:
        print(f"""
        Lineage Report Summary:
        ======================
        Total Data Sources: {report['summary']['total_data_sources']}
        Total Transformations: {report['summary']['total_transformations']}
        Total Relationships: {report['summary']['total_lineage_relationships']}
        Avg Downstream Connections: {report['summary']['average_downstream_connections']}
        Avg Upstream Connections: {report['summary']['average_upstream_connections']}
        
        Source Type Distribution:
        {json.dumps(report['distributions']['source_types'], indent=2)}
        
        Transformation Type Distribution:
        {json.dumps(report['distributions']['transformation_types'], indent=2)}
        
        Most Connected Sources:
        {chr(10).join([f"- {node}: {degree} connections" for node, degree in report['most_connected_sources']])}
        
        Recommendations:
        {chr(10).join(['- ' + rec for rec in report['recommendations']])}
        """)
    else:
        print(f"Error generating report: {report['error']}")
    
    print("\n✅ Data Lineage Tracking System Demo Complete!")
    print("Lineage tracking ready for production - वंशावली ट्रैकिंग उत्पादन के लिए तैयार!")
    
    return {
        'upstream_lineage': upstream_lineage,
        'downstream_lineage': downstream_lineage,
        'impact_analysis': impact_analysis,
        'report': report
    }

if __name__ == "__main__":
    results = main()
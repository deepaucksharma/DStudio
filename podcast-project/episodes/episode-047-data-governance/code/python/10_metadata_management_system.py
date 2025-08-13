"""
Metadata Management System
मेटाडेटा प्रबंधन सिस्टम

Real-world example: Zomato's metadata management for restaurant and menu data
Comprehensive metadata management for data discovery and governance
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import re
from collections import defaultdict

class MetadataType(Enum):
    """Metadata types - मेटाडेटा प्रकार"""
    BUSINESS = "business"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    QUALITY = "quality"
    SECURITY = "security"
    COMPLIANCE = "compliance"

class DataAssetType(Enum):
    """Data asset types - डेटा संपत्ति प्रकार"""
    DATABASE = "database"
    TABLE = "table"
    COLUMN = "column"
    VIEW = "view"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    DASHBOARD = "dashboard"
    REPORT = "report"

@dataclass
class MetadataAttribute:
    """Individual metadata attribute - व्यक्तिगत मेटाडेटा विशेषता"""
    attribute_id: str
    name: str
    value: Any
    data_type: str  # string, number, boolean, date, json
    metadata_type: MetadataType
    is_required: bool = False
    is_searchable: bool = True
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class DataAssetMetadata:
    """Complete metadata for a data asset - डेटा संपत्ति के लिए संपूर्ण मेटाडेटा"""
    asset_id: str
    asset_name: str
    asset_type: DataAssetType
    description: str
    owner: str
    domain: str  # restaurants, customers, delivery, payments
    attributes: Dict[str, MetadataAttribute] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    relationships: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"

@dataclass
class MetadataSchema:
    """Schema definition for metadata - मेटाडेटा के लिए स्कीमा परिभाषा"""
    schema_id: str
    schema_name: str
    asset_type: DataAssetType
    required_attributes: List[str]
    optional_attributes: List[str]
    validation_rules: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

class ZomatoMetadataManager:
    """
    Zomato Metadata Management System
    जोमैटो मेटाडेटा प्रबंधन सिस्टम
    
    Manages metadata for restaurants, menus, customers, and delivery data
    """
    
    def __init__(self):
        self.metadata_catalog: Dict[str, DataAssetMetadata] = {}
        self.metadata_schemas: Dict[str, MetadataSchema] = {}
        self.search_index: Dict[str, Set[str]] = defaultdict(set)  # term -> asset_ids
        self.lineage_graph: Dict[str, List[str]] = defaultdict(list)  # asset_id -> dependent_assets
        self.audit_log: List[Dict] = []
        
        self.setup_default_schemas()
        self.setup_sample_assets()
    
    def setup_default_schemas(self):
        """Setup default metadata schemas - डिफ़ॉल्ट मेटाडेटा स्कीमा सेट करें"""
        
        # Restaurant data schema
        restaurant_schema = MetadataSchema(
            schema_id="schema_restaurant",
            schema_name="Restaurant Data Schema",
            asset_type=DataAssetType.TABLE,
            required_attributes=[
                "business_purpose", "data_owner", "update_frequency", 
                "data_classification", "pii_fields"
            ],
            optional_attributes=[
                "data_source", "retention_period", "backup_policy",
                "quality_score", "compliance_flags"
            ],
            validation_rules={
                "data_classification": ["public", "internal", "confidential", "restricted"],
                "update_frequency": ["real_time", "daily", "weekly", "monthly"],
                "quality_score": {"min": 0, "max": 100}
            }
        )
        self.metadata_schemas[restaurant_schema.schema_id] = restaurant_schema
        
        # Menu data schema
        menu_schema = MetadataSchema(
            schema_id="schema_menu",
            schema_name="Menu Data Schema", 
            asset_type=DataAssetType.TABLE,
            required_attributes=[
                "business_purpose", "data_owner", "update_frequency",
                "cuisine_types", "allergen_info"
            ],
            optional_attributes=[
                "seasonal_availability", "nutritional_info", "price_currency",
                "image_metadata", "translation_status"
            ],
            validation_rules={
                "cuisine_types": ["north_indian", "south_indian", "chinese", "italian", "continental"],
                "price_currency": ["INR", "USD"],
                "allergen_info": ["nuts", "dairy", "gluten", "soy", "eggs"]
            }
        )
        self.metadata_schemas[menu_schema.schema_id] = menu_schema
        
        print("🔧 Default metadata schemas initialized")
    
    def setup_sample_assets(self):
        """Setup sample data assets - नमूना डेटा संपत्ति सेट करें"""
        
        # Restaurant master table
        restaurant_table = DataAssetMetadata(
            asset_id="zomato_restaurants_master",
            asset_name="Restaurant Master Table",
            asset_type=DataAssetType.TABLE,
            description="Master table containing all restaurant information in Zomato platform",
            owner="restaurant-team@zomato.com",
            domain="restaurants"
        )
        
        # Add business metadata
        restaurant_table.attributes["business_purpose"] = MetadataAttribute(
            attribute_id="bp_001",
            name="business_purpose",
            value="Store comprehensive restaurant information for search and discovery",
            data_type="string",
            metadata_type=MetadataType.BUSINESS,
            is_required=True,
            created_by="product-manager@zomato.com"
        )
        
        restaurant_table.attributes["target_audience"] = MetadataAttribute(
            attribute_id="ta_001",
            name="target_audience",
            value="Customer app, restaurant partners, delivery partners",
            data_type="string",
            metadata_type=MetadataType.BUSINESS,
            created_by="product-manager@zomato.com"
        )
        
        # Add technical metadata
        restaurant_table.attributes["storage_location"] = MetadataAttribute(
            attribute_id="sl_001", 
            name="storage_location",
            value="postgres://restaurants-db.zomato.com:5432/prod",
            data_type="string",
            metadata_type=MetadataType.TECHNICAL,
            is_searchable=False,
            created_by="dba@zomato.com"
        )
        
        restaurant_table.attributes["row_count"] = MetadataAttribute(
            attribute_id="rc_001",
            name="row_count",
            value=250000,
            data_type="number",
            metadata_type=MetadataType.OPERATIONAL,
            created_by="data-eng@zomato.com"
        )
        
        # Add quality metadata
        restaurant_table.attributes["data_quality_score"] = MetadataAttribute(
            attribute_id="dqs_001",
            name="data_quality_score",
            value=87.5,
            data_type="number",
            metadata_type=MetadataType.QUALITY,
            created_by="quality-team@zomato.com"
        )
        
        # Add compliance metadata
        restaurant_table.attributes["contains_pii"] = MetadataAttribute(
            attribute_id="pii_001",
            name="contains_pii",
            value=True,
            data_type="boolean",
            metadata_type=MetadataType.COMPLIANCE,
            created_by="compliance@zomato.com"
        )
        
        restaurant_table.attributes["gdpr_applicable"] = MetadataAttribute(
            attribute_id="gdpr_001",
            name="gdpr_applicable",
            value=True,
            data_type="boolean", 
            metadata_type=MetadataType.COMPLIANCE,
            created_by="legal@zomato.com"
        )
        
        # Add tags
        restaurant_table.tags = {"master_data", "restaurants", "pii", "production", "high_volume"}
        
        self.register_metadata(restaurant_table)
        
        # Menu items table
        menu_table = DataAssetMetadata(
            asset_id="zomato_menu_items",
            asset_name="Menu Items Table",
            asset_type=DataAssetType.TABLE,
            description="All menu items with pricing, descriptions, and availability",
            owner="catalog-team@zomato.com",
            domain="restaurants"
        )
        
        menu_table.attributes["business_purpose"] = MetadataAttribute(
            attribute_id="bp_002",
            name="business_purpose", 
            value="Store menu items for restaurant catalog and ordering system",
            data_type="string",
            metadata_type=MetadataType.BUSINESS,
            is_required=True
        )
        
        menu_table.attributes["update_frequency"] = MetadataAttribute(
            attribute_id="uf_002",
            name="update_frequency",
            value="real_time",
            data_type="string",
            metadata_type=MetadataType.OPERATIONAL
        )
        
        menu_table.attributes["cuisine_coverage"] = MetadataAttribute(
            attribute_id="cc_002",
            name="cuisine_coverage",
            value=["north_indian", "south_indian", "chinese", "italian", "continental", "desserts"],
            data_type="json",
            metadata_type=MetadataType.BUSINESS
        )
        
        menu_table.tags = {"menu_data", "real_time", "catalog", "pricing"}
        
        # Create relationship
        menu_table.relationships = [
            {
                "type": "depends_on",
                "related_asset": "zomato_restaurants_master",
                "relationship_description": "Menu items belong to restaurants"
            }
        ]
        
        self.register_metadata(menu_table)
        
        # Customer orders analytics view
        orders_view = DataAssetMetadata(
            asset_id="customer_orders_analytics_view",
            asset_name="Customer Orders Analytics View",
            asset_type=DataAssetType.VIEW,
            description="Aggregated view of customer ordering patterns for business intelligence",
            owner="analytics-team@zomato.com", 
            domain="customers"
        )
        
        orders_view.attributes["business_purpose"] = MetadataAttribute(
            attribute_id="bp_003",
            name="business_purpose",
            value="Provide insights into customer ordering behavior and trends",
            data_type="string",
            metadata_type=MetadataType.BUSINESS
        )
        
        orders_view.attributes["refresh_schedule"] = MetadataAttribute(
            attribute_id="rs_003",
            name="refresh_schedule",
            value="0 2 * * *",  # Daily at 2 AM
            data_type="string",
            metadata_type=MetadataType.OPERATIONAL
        )
        
        orders_view.attributes["contains_sensitive_data"] = MetadataAttribute(
            attribute_id="csd_003",
            name="contains_sensitive_data",
            value=False,
            data_type="boolean",
            metadata_type=MetadataType.SECURITY
        )
        
        orders_view.tags = {"analytics", "aggregated", "business_intelligence", "customer_insights"}
        
        self.register_metadata(orders_view)
        
        print("📊 Sample data assets registered")
    
    def register_metadata(self, asset_metadata: DataAssetMetadata):
        """Register metadata for a data asset - डेटा संपत्ति के लिए मेटाडेटा पंजीकृत करें"""
        
        # Validate against schema if available
        schema_id = f"schema_{asset_metadata.domain}"
        if schema_id in self.metadata_schemas:
            validation_errors = self.validate_against_schema(asset_metadata, schema_id)
            if validation_errors:
                print(f"⚠️ Validation errors for {asset_metadata.asset_name}:")
                for error in validation_errors:
                    print(f"  - {error}")
        
        # Store in catalog
        self.metadata_catalog[asset_metadata.asset_id] = asset_metadata
        
        # Update search index
        self.update_search_index(asset_metadata)
        
        # Update lineage graph
        for relationship in asset_metadata.relationships:
            if relationship["type"] == "depends_on":
                related_asset = relationship["related_asset"]
                self.lineage_graph[related_asset].append(asset_metadata.asset_id)
        
        # Audit log
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "metadata_registered",
            "asset_id": asset_metadata.asset_id,
            "asset_name": asset_metadata.asset_name,
            "owner": asset_metadata.owner,
            "domain": asset_metadata.domain
        })
        
        print(f"📝 Registered metadata for: {asset_metadata.asset_name}")
    
    def validate_against_schema(self, asset_metadata: DataAssetMetadata, schema_id: str) -> List[str]:
        """Validate metadata against schema - स्कीमा के विरुद्ध मेटाडेटा मान्य करें"""
        errors = []
        
        if schema_id not in self.metadata_schemas:
            return ["Schema not found"]
        
        schema = self.metadata_schemas[schema_id]
        
        # Check required attributes
        for required_attr in schema.required_attributes:
            if required_attr not in asset_metadata.attributes:
                errors.append(f"Missing required attribute: {required_attr}")
        
        # Validate attribute values
        for attr_name, attribute in asset_metadata.attributes.items():
            if attr_name in schema.validation_rules:
                rule = schema.validation_rules[attr_name]
                
                if isinstance(rule, list):  # Enum validation
                    if attribute.value not in rule:
                        errors.append(f"Invalid value for {attr_name}: {attribute.value}")
                        
                elif isinstance(rule, dict):  # Range validation
                    if "min" in rule and "max" in rule:
                        if not (rule["min"] <= attribute.value <= rule["max"]):
                            errors.append(f"Value out of range for {attr_name}: {attribute.value}")
        
        return errors
    
    def update_search_index(self, asset_metadata: DataAssetMetadata):
        """Update search index - सर्च इंडेक्स अपडेट करें"""
        
        # Index asset name and description
        name_terms = self.tokenize(asset_metadata.asset_name.lower())
        desc_terms = self.tokenize(asset_metadata.description.lower())
        
        all_terms = set(name_terms + desc_terms)
        
        # Index searchable attributes
        for attribute in asset_metadata.attributes.values():
            if attribute.is_searchable and isinstance(attribute.value, str):
                attr_terms = self.tokenize(attribute.value.lower())
                all_terms.update(attr_terms)
        
        # Index tags
        all_terms.update(tag.lower() for tag in asset_metadata.tags)
        
        # Index domain and owner
        all_terms.add(asset_metadata.domain.lower())
        all_terms.update(self.tokenize(asset_metadata.owner.lower()))
        
        # Update index
        for term in all_terms:
            self.search_index[term].add(asset_metadata.asset_id)
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text for search - सर्च के लिए टेक्स्ट टोकनाइज़ करें"""
        # Simple tokenization - remove special chars and split
        tokens = re.findall(r'\b\w+\b', text)
        return [token for token in tokens if len(token) > 2]
    
    def search_assets(self, query: str, filters: Optional[Dict] = None) -> List[DataAssetMetadata]:
        """Search for data assets - डेटा संपत्ति खोजें"""
        
        query_terms = self.tokenize(query.lower())
        
        if not query_terms:
            return []
        
        # Find assets matching query terms
        matching_assets = set()
        
        for term in query_terms:
            # Exact match
            if term in self.search_index:
                matching_assets.update(self.search_index[term])
            
            # Partial match
            for indexed_term in self.search_index:
                if term in indexed_term or indexed_term in term:
                    matching_assets.update(self.search_index[indexed_term])
        
        # Get asset metadata
        results = []
        for asset_id in matching_assets:
            if asset_id in self.metadata_catalog:
                asset = self.metadata_catalog[asset_id]
                
                # Apply filters
                if filters:
                    if not self.match_filters(asset, filters):
                        continue
                
                results.append(asset)
        
        # Sort by relevance (simplified)
        results.sort(key=lambda x: len(set(self.tokenize(x.asset_name.lower())) & set(query_terms)), reverse=True)
        
        return results
    
    def match_filters(self, asset: DataAssetMetadata, filters: Dict) -> bool:
        """Check if asset matches filters - जांचें कि एसेट फिल्टर मैच करता है या नहीं"""
        
        if "domain" in filters and asset.domain != filters["domain"]:
            return False
            
        if "asset_type" in filters and asset.asset_type.value != filters["asset_type"]:
            return False
            
        if "owner" in filters and filters["owner"] not in asset.owner:
            return False
            
        if "tags" in filters:
            required_tags = set(filters["tags"])
            if not required_tags.issubset(asset.tags):
                return False
        
        if "metadata_type" in filters:
            metadata_type = MetadataType(filters["metadata_type"])
            has_type = any(attr.metadata_type == metadata_type 
                          for attr in asset.attributes.values())
            if not has_type:
                return False
        
        return True
    
    def get_asset_lineage(self, asset_id: str, direction: str = "downstream") -> Dict[str, Any]:
        """Get data lineage for an asset - एसेट के लिए डेटा लाइनेज प्राप्त करें"""
        
        if asset_id not in self.metadata_catalog:
            return {"error": "Asset not found"}
        
        lineage = {
            "asset_id": asset_id,
            "asset_name": self.metadata_catalog[asset_id].asset_name,
            "direction": direction,
            "relationships": []
        }
        
        if direction == "downstream":
            # Assets that depend on this one
            dependent_assets = self.lineage_graph.get(asset_id, [])
            for dep_asset_id in dependent_assets:
                if dep_asset_id in self.metadata_catalog:
                    dep_asset = self.metadata_catalog[dep_asset_id]
                    lineage["relationships"].append({
                        "asset_id": dep_asset_id,
                        "asset_name": dep_asset.asset_name,
                        "relationship_type": "dependent"
                    })
        
        elif direction == "upstream":
            # Assets this one depends on
            current_asset = self.metadata_catalog[asset_id]
            for relationship in current_asset.relationships:
                if relationship["type"] == "depends_on":
                    related_asset_id = relationship["related_asset"]
                    if related_asset_id in self.metadata_catalog:
                        related_asset = self.metadata_catalog[related_asset_id]
                        lineage["relationships"].append({
                            "asset_id": related_asset_id,
                            "asset_name": related_asset.asset_name,
                            "relationship_type": "dependency"
                        })
        
        return lineage
    
    def generate_data_catalog_report(self) -> Dict[str, Any]:
        """Generate comprehensive data catalog report - व्यापक डेटा कैटलॉग रिपोर्ट जेनरेट करें"""
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_assets": len(self.metadata_catalog),
                "total_schemas": len(self.metadata_schemas),
                "indexed_terms": len(self.search_index)
            },
            "assets_by_domain": {},
            "assets_by_type": {},
            "assets_by_owner": {},
            "metadata_coverage": {},
            "quality_metrics": {},
            "compliance_status": {}
        }
        
        # Analyze assets
        for asset in self.metadata_catalog.values():
            # By domain
            domain = asset.domain
            report["assets_by_domain"][domain] = report["assets_by_domain"].get(domain, 0) + 1
            
            # By type
            asset_type = asset.asset_type.value
            report["assets_by_type"][asset_type] = report["assets_by_type"].get(asset_type, 0) + 1
            
            # By owner
            owner = asset.owner
            report["assets_by_owner"][owner] = report["assets_by_owner"].get(owner, 0) + 1
            
            # Metadata coverage
            for metadata_type in MetadataType:
                type_key = metadata_type.value
                if type_key not in report["metadata_coverage"]:
                    report["metadata_coverage"][type_key] = {"count": 0, "assets": 0}
                
                has_type = any(attr.metadata_type == metadata_type 
                              for attr in asset.attributes.values())
                if has_type:
                    report["metadata_coverage"][type_key]["assets"] += 1
                    report["metadata_coverage"][type_key]["count"] += sum(
                        1 for attr in asset.attributes.values() 
                        if attr.metadata_type == metadata_type
                    )
        
        # Quality metrics
        quality_scores = []
        for asset in self.metadata_catalog.values():
            for attr in asset.attributes.values():
                if attr.name == "data_quality_score" and isinstance(attr.value, (int, float)):
                    quality_scores.append(attr.value)
        
        if quality_scores:
            report["quality_metrics"] = {
                "average_quality_score": sum(quality_scores) / len(quality_scores),
                "assets_with_quality_score": len(quality_scores),
                "min_quality_score": min(quality_scores),
                "max_quality_score": max(quality_scores)
            }
        
        # Compliance status
        pii_assets = 0
        gdpr_assets = 0
        
        for asset in self.metadata_catalog.values():
            for attr in asset.attributes.values():
                if attr.name == "contains_pii" and attr.value:
                    pii_assets += 1
                if attr.name == "gdpr_applicable" and attr.value:
                    gdpr_assets += 1
        
        report["compliance_status"] = {
            "assets_with_pii": pii_assets,
            "gdpr_applicable_assets": gdpr_assets,
            "compliance_coverage": (pii_assets + gdpr_assets) / (2 * len(self.metadata_catalog)) * 100
        }
        
        return report
    
    def update_metadata_attribute(self, asset_id: str, attribute_name: str, new_value: Any, updated_by: str):
        """Update metadata attribute - मेटाडेटा विशेषता अपडेट करें"""
        
        if asset_id not in self.metadata_catalog:
            print(f"❌ Asset {asset_id} not found")
            return False
        
        asset = self.metadata_catalog[asset_id]
        
        if attribute_name not in asset.attributes:
            print(f"❌ Attribute {attribute_name} not found in asset {asset_id}")
            return False
        
        old_value = asset.attributes[attribute_name].value
        asset.attributes[attribute_name].value = new_value
        asset.attributes[attribute_name].updated_at = datetime.now()
        asset.updated_at = datetime.now()
        
        # Re-index if searchable
        if asset.attributes[attribute_name].is_searchable:
            self.update_search_index(asset)
        
        # Audit log
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "metadata_updated",
            "asset_id": asset_id,
            "attribute_name": attribute_name,
            "old_value": str(old_value),
            "new_value": str(new_value),
            "updated_by": updated_by
        })
        
        print(f"✅ Updated {attribute_name} for {asset.asset_name}")
        return True

def main():
    """
    Main demonstration function
    मुख्य प्रदर्शन फ़ंक्शन
    """
    print("🍽️ Zomato Metadata Management System Demo")
    print("=" * 50)
    
    metadata_manager = ZomatoMetadataManager()
    
    # Search for assets
    print("\n🔍 Searching for assets...")
    
    # Search by keyword
    restaurant_assets = metadata_manager.search_assets("restaurant")
    print(f"Found {len(restaurant_assets)} assets for 'restaurant':")
    for asset in restaurant_assets:
        print(f"  - {asset.asset_name} ({asset.domain})")
    
    # Search with filters
    table_assets = metadata_manager.search_assets(
        "data",
        filters={"asset_type": "table", "domain": "restaurants"}
    )
    print(f"\nFound {len(table_assets)} table assets in restaurants domain:")
    for asset in table_assets:
        print(f"  - {asset.asset_name}")
    
    # Get lineage
    print("\n🔗 Data Lineage Analysis:")
    lineage = metadata_manager.get_asset_lineage("zomato_restaurants_master", "downstream")
    print(f"Downstream lineage for {lineage['asset_name']}:")
    for rel in lineage["relationships"]:
        print(f"  -> {rel['asset_name']} ({rel['relationship_type']})")
    
    # Update metadata
    print("\n✏️ Updating metadata...")
    metadata_manager.update_metadata_attribute(
        "zomato_restaurants_master",
        "data_quality_score", 
        92.3,
        "data-eng@zomato.com"
    )
    
    # Generate catalog report
    print("\n📊 Data Catalog Report:")
    report = metadata_manager.generate_data_catalog_report()
    
    print(f"Summary: {report['summary']}")
    print(f"Assets by Domain: {report['assets_by_domain']}")
    print(f"Assets by Type: {report['assets_by_type']}")
    print(f"Metadata Coverage: {report['metadata_coverage']}")
    
    if report['quality_metrics']:
        print(f"Quality Metrics: {report['quality_metrics']}")
    
    print(f"Compliance Status: {report['compliance_status']}")

if __name__ == "__main__":
    main()
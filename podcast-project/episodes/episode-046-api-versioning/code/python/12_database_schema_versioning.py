"""
Database Schema Versioning System
डेटाबेस स्कीमा वर्जनिंग सिस्टम

UPI payment schema evolution के लिए schema versioning system
Handles backward compatible database changes for payment systems
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import uuid

class SchemaChangeType(Enum):
    """Schema change types - स्कीमा चेंज के प्रकार"""
    ADD_COLUMN = "add_column"
    DROP_COLUMN = "drop_column"
    MODIFY_COLUMN = "modify_column"
    ADD_INDEX = "add_index"
    DROP_INDEX = "drop_index"
    ADD_TABLE = "add_table"
    DROP_TABLE = "drop_table"

@dataclass
class SchemaChange:
    """Individual schema change - व्यक्तिगत स्कीमा परिवर्तन"""
    change_type: SchemaChangeType
    table_name: str
    column_name: Optional[str] = None
    data_type: Optional[str] = None
    is_nullable: bool = True
    default_value: Optional[Any] = None
    migration_sql: str = ""
    rollback_sql: str = ""

@dataclass
class SchemaVersion:
    """Schema version definition - स्कीमा वर्जन परिभाषा"""
    version: str
    description: str
    changes: List[SchemaChange]
    created_at: datetime
    applied_at: Optional[datetime] = None
    rollback_at: Optional[datetime] = None

class UPIPaymentSchemaVersioning:
    """
    UPI Payment Database Schema Versioning System
    UPI पेमेंट डेटाबेस स्कीमा वर्जनिंग सिस्टम
    
    Real-world example: PhonePe/Paytm payment schema evolution
    """
    
    def __init__(self):
        self.versions: Dict[str, SchemaVersion] = {}
        self.current_version = "1.0.0"
        self.applied_versions: List[str] = []
        
    def create_version(self, version: str, description: str, 
                      changes: List[SchemaChange]) -> SchemaVersion:
        """
        Create new schema version
        नया स्कीमा वर्जन बनाएं
        """
        schema_version = SchemaVersion(
            version=version,
            description=description,
            changes=changes,
            created_at=datetime.now()
        )
        
        self.versions[version] = schema_version
        print(f"📊 Schema version {version} created: {description}")
        return schema_version
    
    def validate_change_compatibility(self, change: SchemaChange) -> bool:
        """
        Validate if change is backward compatible
        बैकवर्ड कम्पैटिबिलिटी की जांच करें
        """
        breaking_changes = [
            SchemaChangeType.DROP_COLUMN,
            SchemaChangeType.DROP_TABLE,
            SchemaChangeType.MODIFY_COLUMN
        ]
        
        if change.change_type in breaking_changes:
            print(f"⚠️ Warning: {change.change_type.value} is potentially breaking")
            return False
            
        return True
    
    def apply_version(self, version: str) -> bool:
        """
        Apply schema version
        स्कीमा वर्जन लागू करें
        """
        if version not in self.versions:
            print(f"❌ Version {version} not found")
            return False
            
        schema_version = self.versions[version]
        
        # Validate all changes
        for change in schema_version.changes:
            if not self.validate_change_compatibility(change):
                print(f"❌ Change validation failed for {change.change_type.value}")
                
        try:
            # Apply changes (simulated)
            for change in schema_version.changes:
                self._execute_schema_change(change)
                
            schema_version.applied_at = datetime.now()
            self.applied_versions.append(version)
            self.current_version = version
            
            print(f"✅ Schema version {version} applied successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error applying schema version {version}: {str(e)}")
            return False
    
    def _execute_schema_change(self, change: SchemaChange):
        """
        Execute individual schema change
        व्यक्तिगत स्कीमा परिवर्तन निष्पादित करें
        """
        print(f"🔧 Executing: {change.change_type.value} on {change.table_name}")
        
        if change.migration_sql:
            print(f"SQL: {change.migration_sql}")
            
        # Simulate execution time
        import time
        time.sleep(0.1)
    
    def rollback_version(self, version: str) -> bool:
        """
        Rollback schema version
        स्कीमा वर्जन को वापस करें
        """
        if version not in self.applied_versions:
            print(f"❌ Version {version} not applied")
            return False
            
        schema_version = self.versions[version]
        
        try:
            # Execute rollback SQL in reverse order
            for change in reversed(schema_version.changes):
                if change.rollback_sql:
                    print(f"🔄 Rollback: {change.rollback_sql}")
                    
            schema_version.rollback_at = datetime.now()
            self.applied_versions.remove(version)
            
            print(f"✅ Schema version {version} rolled back successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error rolling back version {version}: {str(e)}")
            return False
    
    def get_version_diff(self, from_version: str, to_version: str) -> List[SchemaChange]:
        """
        Get differences between two versions
        दो वर्जन के बीच अंतर प्राप्त करें
        """
        diff_changes = []
        
        if from_version in self.versions and to_version in self.versions:
            from_changes = self.versions[from_version].changes
            to_changes = self.versions[to_version].changes
            
            # Simple diff logic (in real implementation, would be more complex)
            for change in to_changes:
                if change not in from_changes:
                    diff_changes.append(change)
                    
        return diff_changes

def main():
    """
    Main demonstration function
    मुख्य प्रदर्शन फ़ंक्शन
    """
    print("🏦 UPI Payment Schema Versioning Demo")
    print("=" * 50)
    
    # Initialize schema versioning system
    schema_system = UPIPaymentSchemaVersioning()
    
    # Version 1.1.0 - Add UPI ID verification
    changes_v1_1 = [
        SchemaChange(
            change_type=SchemaChangeType.ADD_COLUMN,
            table_name="payments",
            column_name="upi_verification_status",
            data_type="VARCHAR(20)",
            default_value="pending",
            migration_sql="ALTER TABLE payments ADD COLUMN upi_verification_status VARCHAR(20) DEFAULT 'pending'",
            rollback_sql="ALTER TABLE payments DROP COLUMN upi_verification_status"
        ),
        SchemaChange(
            change_type=SchemaChangeType.ADD_INDEX,
            table_name="payments",
            column_name="upi_verification_status",
            migration_sql="CREATE INDEX idx_payments_upi_verification ON payments(upi_verification_status)",
            rollback_sql="DROP INDEX idx_payments_upi_verification"
        )
    ]
    
    version_1_1 = schema_system.create_version(
        "1.1.0", 
        "Add UPI verification status tracking", 
        changes_v1_1
    )
    
    # Version 1.2.0 - Add merchant category support
    changes_v1_2 = [
        SchemaChange(
            change_type=SchemaChangeType.ADD_TABLE,
            table_name="merchant_categories",
            migration_sql="""
            CREATE TABLE merchant_categories (
                id UUID PRIMARY KEY,
                category_code VARCHAR(10) NOT NULL,
                category_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            rollback_sql="DROP TABLE merchant_categories"
        ),
        SchemaChange(
            change_type=SchemaChangeType.ADD_COLUMN,
            table_name="payments",
            column_name="merchant_category_id",
            data_type="UUID",
            migration_sql="ALTER TABLE payments ADD COLUMN merchant_category_id UUID REFERENCES merchant_categories(id)",
            rollback_sql="ALTER TABLE payments DROP COLUMN merchant_category_id"
        )
    ]
    
    version_1_2 = schema_system.create_version(
        "1.2.0", 
        "Add merchant category support for UPI payments", 
        changes_v1_2
    )
    
    # Apply versions
    print("\n🚀 Applying schema versions...")
    schema_system.apply_version("1.1.0")
    schema_system.apply_version("1.2.0")
    
    print(f"\n📊 Current schema version: {schema_system.current_version}")
    print(f"Applied versions: {schema_system.applied_versions}")
    
    # Demonstrate rollback
    print("\n🔄 Rolling back version 1.2.0...")
    schema_system.rollback_version("1.2.0")
    
    # Version diff
    print("\n📋 Version differences:")
    diff = schema_system.get_version_diff("1.0.0", "1.1.0")
    for change in diff:
        print(f"  - {change.change_type.value}: {change.table_name}.{change.column_name}")

if __name__ == "__main__":
    main()
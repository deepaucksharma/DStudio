#!/usr/bin/env python3
"""
REST API Backward Compatibility Management
Inspired by IRCTC API evolution - maintain backward compatibility while adding features

Example: IRCTC ne kaise ensure kiya ki purane mobile apps break na ho
"""

from flask import Flask, request, jsonify
from functools import wraps
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompatibilityLevel(Enum):
    """Compatibility levels for API changes"""
    FULLY_COMPATIBLE = "fully_compatible"      # No breaking changes
    BACKWARD_COMPATIBLE = "backward_compatible"  # New fields only
    BREAKING_CHANGE = "breaking_change"        # Requires client updates

@dataclass
class APIField:
    """API field metadata"""
    name: str
    field_type: str
    required: bool = False
    deprecated: bool = False
    added_in_version: str = "1.0"
    deprecated_in_version: Optional[str] = None
    removal_version: Optional[str] = None

@dataclass
class TrainBookingV1:
    """Version 1: Basic train booking structure"""
    pnr: str
    train_number: str
    date: str
    passenger_name: str
    seat_number: str
    status: str

@dataclass
class TrainBookingV2:
    """Version 2: Enhanced with coach details"""
    pnr: str
    train_number: str
    train_name: str  # New field
    date: str
    passenger_name: str
    seat_number: str
    coach: str  # New field
    status: str
    booking_time: str  # New field

@dataclass 
class TrainBookingV3:
    """Version 3: Full featured with payment and meal info"""
    pnr: str
    train_number: str
    train_name: str
    date: str
    passenger_name: str
    seat_number: str
    coach: str
    status: str
    booking_time: str
    fare: float  # New field
    payment_method: str  # New field
    meal_preference: Optional[str] = None  # New optional field
    mobile_number: str = ""  # New field with default
    # Deprecated field (kept for compatibility)
    old_status_code: Optional[str] = None

class BackwardCompatibilityManager:
    """
    Manage backward compatibility for REST API evolution
    IRCTC style - ensure old mobile apps continue working
    """
    
    def __init__(self):
        self.field_registry = self._initialize_field_registry()
        self.version_mappings = self._initialize_version_mappings()
        self.default_values = self._initialize_default_values()
    
    def _initialize_field_registry(self) -> Dict[str, APIField]:
        """Initialize field registry with evolution history"""
        return {
            # V1 fields
            "pnr": APIField("pnr", "string", required=True, added_in_version="1.0"),
            "train_number": APIField("train_number", "string", required=True, added_in_version="1.0"),
            "date": APIField("date", "string", required=True, added_in_version="1.0"),
            "passenger_name": APIField("passenger_name", "string", required=True, added_in_version="1.0"),
            "seat_number": APIField("seat_number", "string", required=True, added_in_version="1.0"),
            "status": APIField("status", "string", required=True, added_in_version="1.0"),
            
            # V2 fields
            "train_name": APIField("train_name", "string", required=False, added_in_version="2.0"),
            "coach": APIField("coach", "string", required=False, added_in_version="2.0"),
            "booking_time": APIField("booking_time", "string", required=False, added_in_version="2.0"),
            
            # V3 fields
            "fare": APIField("fare", "float", required=False, added_in_version="3.0"),
            "payment_method": APIField("payment_method", "string", required=False, added_in_version="3.0"),
            "meal_preference": APIField("meal_preference", "string", required=False, added_in_version="3.0"),
            "mobile_number": APIField("mobile_number", "string", required=False, added_in_version="3.0"),
            
            # Deprecated fields
            "old_status_code": APIField("old_status_code", "string", required=False, 
                                      deprecated=True, deprecated_in_version="2.0", 
                                      removal_version="4.0")
        }
    
    def _initialize_version_mappings(self) -> Dict[str, List[str]]:
        """Map versions to their supported fields"""
        return {
            "1.0": ["pnr", "train_number", "date", "passenger_name", "seat_number", "status"],
            "2.0": ["pnr", "train_number", "train_name", "date", "passenger_name", 
                   "seat_number", "coach", "status", "booking_time"],
            "3.0": ["pnr", "train_number", "train_name", "date", "passenger_name",
                   "seat_number", "coach", "status", "booking_time", "fare", 
                   "payment_method", "meal_preference", "mobile_number"]
        }
    
    def _initialize_default_values(self) -> Dict[str, Any]:
        """Default values for new fields to maintain compatibility"""
        return {
            "train_name": "Unknown Train",
            "coach": "General",
            "booking_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fare": 0.0,
            "payment_method": "Cash",
            "meal_preference": None,
            "mobile_number": ""
        }
    
    def transform_response_for_version(self, data: Dict[str, Any], target_version: str) -> Dict[str, Any]:
        """
        Transform response data to match target version schema
        Remove fields not available in target version
        """
        if target_version not in self.version_mappings:
            raise ValueError(f"Unsupported version: {target_version}")
        
        supported_fields = self.version_mappings[target_version]
        transformed_data = {}
        
        # Only include fields supported in target version
        for field in supported_fields:
            if field in data:
                transformed_data[field] = data[field]
            else:
                # Provide default value if field is missing
                if field in self.default_values:
                    transformed_data[field] = self.default_values[field]
        
        return transformed_data
    
    def validate_request_for_version(self, request_data: Dict[str, Any], target_version: str) -> List[str]:
        """
        Validate request data against version schema
        Return list of validation errors
        """
        errors = []
        supported_fields = self.version_mappings.get(target_version, [])
        
        # Check required fields
        for field_name in supported_fields:
            field_info = self.field_registry.get(field_name)
            if field_info and field_info.required and field_name not in request_data:
                errors.append(f"Missing required field: {field_name}")
        
        # Check for unknown fields (warning, not error for backward compatibility)
        for field_name in request_data:
            if field_name not in supported_fields:
                logger.warning(f"Unknown field '{field_name}' in version {target_version}")
        
        return errors
    
    def get_compatibility_level(self, from_version: str, to_version: str) -> CompatibilityLevel:
        """Determine compatibility level between versions"""
        from_fields = set(self.version_mappings.get(from_version, []))
        to_fields = set(self.version_mappings.get(to_version, []))
        
        # If to_version has all fields of from_version, it's backward compatible
        if from_fields.issubset(to_fields):
            return CompatibilityLevel.BACKWARD_COMPATIBLE
        
        # If some fields are removed, it's a breaking change
        missing_fields = from_fields - to_fields
        if missing_fields:
            return CompatibilityLevel.BREAKING_CHANGE
        
        return CompatibilityLevel.FULLY_COMPATIBLE
    
    def get_migration_guide(self, from_version: str, to_version: str) -> Dict[str, Any]:
        """Generate migration guide between versions"""
        from_fields = set(self.version_mappings.get(from_version, []))
        to_fields = set(self.version_mappings.get(to_version, []))
        
        added_fields = to_fields - from_fields
        removed_fields = from_fields - to_fields
        deprecated_fields = [f for f in from_fields if self.field_registry.get(f, {}).deprecated]
        
        return {
            "from_version": from_version,
            "to_version": to_version,
            "compatibility_level": self.get_compatibility_level(from_version, to_version).value,
            "added_fields": list(added_fields),
            "removed_fields": list(removed_fields),
            "deprecated_fields": deprecated_fields,
            "migration_steps": self._generate_migration_steps(from_version, to_version),
            "timeline": "6 months transition period recommended"
        }
    
    def _generate_migration_steps(self, from_version: str, to_version: str) -> List[str]:
        """Generate step-by-step migration guide"""
        steps = []
        
        from_fields = set(self.version_mappings.get(from_version, []))
        to_fields = set(self.version_mappings.get(to_version, []))
        
        added_fields = to_fields - from_fields
        removed_fields = from_fields - to_fields
        
        if added_fields:
            steps.append(f"1. Update client to handle new fields: {', '.join(added_fields)}")
            steps.append("2. Test with new optional fields to ensure no breaking changes")
        
        if removed_fields:
            steps.append(f"3. ⚠️  WARNING: Fields will be removed: {', '.join(removed_fields)}")
            steps.append("4. Update client code to not depend on removed fields")
            steps.append("5. Test thoroughly before version upgrade")
        
        steps.append("6. Update API version header in requests")
        steps.append("7. Monitor logs for any compatibility issues")
        
        return steps

# Flask app with backward compatibility
app = Flask(__name__)
compatibility_manager = BackwardCompatibilityManager()

def version_compatible(func):
    """Decorator to handle version compatibility"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get version from header (default to 1.0 for old clients)
        api_version = request.headers.get('API-Version', '1.0')
        
        # Store version in request context
        request.api_version = api_version
        
        # Call the actual function
        response = func(*args, **kwargs)
        
        # Transform response based on version
        if hasattr(response, 'get_json') and response.get_json():
            original_data = response.get_json()
            
            # Transform data for requested version
            if 'data' in original_data:
                if isinstance(original_data['data'], list):
                    # Transform each item in list
                    transformed_items = []
                    for item in original_data['data']:
                        transformed_item = compatibility_manager.transform_response_for_version(
                            item, api_version
                        )
                        transformed_items.append(transformed_item)
                    original_data['data'] = transformed_items
                else:
                    # Transform single item
                    original_data['data'] = compatibility_manager.transform_response_for_version(
                        original_data['data'], api_version
                    )
            
            # Add version info to response
            original_data['_meta'] = {
                'api_version': api_version,
                'response_transformed': True,
                'compatible_versions': list(compatibility_manager.version_mappings.keys())
            }
            
            return jsonify(original_data)
        
        return response
    
    return wrapper

# Mock database
BOOKINGS = [
    {
        "pnr": "1234567890",
        "train_number": "12345",
        "train_name": "Rajdhani Express",
        "date": "2024-01-15",
        "passenger_name": "Rahul Sharma",
        "seat_number": "A1-25",
        "coach": "A1",
        "status": "Confirmed",
        "booking_time": "2024-01-10 14:30:00",
        "fare": 2500.00,
        "payment_method": "UPI",
        "meal_preference": "Vegetarian",
        "mobile_number": "9876543210"
    },
    {
        "pnr": "9876543210",
        "train_number": "54321",
        "train_name": "Shatabdi Express",
        "date": "2024-01-20",
        "passenger_name": "Priya Patel",
        "seat_number": "B2-15",
        "coach": "B2",
        "status": "Waiting",
        "booking_time": "2024-01-12 09:15:00",
        "fare": 1800.00,
        "payment_method": "Credit Card",
        "meal_preference": "Jain",
        "mobile_number": "8765432109"
    }
]

@app.route('/api/bookings', methods=['GET'])
@version_compatible
def get_bookings():
    """
    Get all bookings with version-specific response format
    Supports v1.0, v2.0, v3.0 clients
    """
    return jsonify({
        "data": BOOKINGS,
        "message": "Bookings retrieved successfully",
        "hindi_message": "Booking details mil gaye"
    })

@app.route('/api/bookings/<pnr>', methods=['GET'])
@version_compatible
def get_booking_by_pnr(pnr):
    """
    Get specific booking by PNR with backward compatibility
    """
    booking = next((b for b in BOOKINGS if b["pnr"] == pnr), None)
    
    if not booking:
        return jsonify({
            "error": "PNR not found",
            "hindi_message": "PNR नहीं मिला"
        }), 404
    
    return jsonify({
        "data": booking,
        "message": "Booking found",
        "hindi_message": "Booking mil gaya"
    })

@app.route('/api/bookings', methods=['POST'])
@version_compatible
def create_booking():
    """
    Create new booking with version-specific validation
    """
    api_version = request.api_version
    data = request.get_json()
    
    # Validate request data for version
    validation_errors = compatibility_manager.validate_request_for_version(data, api_version)
    
    if validation_errors:
        return jsonify({
            "error": "Validation failed",
            "errors": validation_errors,
            "api_version": api_version
        }), 400
    
    # Generate new PNR
    new_pnr = f"PNR{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Create booking with version-appropriate fields
    new_booking = {
        "pnr": new_pnr,
        "train_number": data.get("train_number"),
        "date": data.get("date"),
        "passenger_name": data.get("passenger_name"),
        "seat_number": data.get("seat_number", "TBD"),
        "status": "Confirmed"
    }
    
    # Add version-specific fields with defaults
    if api_version >= "2.0":
        new_booking.update({
            "train_name": data.get("train_name", "Unknown Train"),
            "coach": data.get("coach", "General"),
            "booking_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    if api_version >= "3.0":
        new_booking.update({
            "fare": data.get("fare", 0.0),
            "payment_method": data.get("payment_method", "Cash"),
            "meal_preference": data.get("meal_preference"),
            "mobile_number": data.get("mobile_number", "")
        })
    
    BOOKINGS.append(new_booking)
    
    return jsonify({
        "data": new_booking,
        "message": "Booking created successfully",
        "hindi_message": "Booking successfully create ho gaya"
    }), 201

@app.route('/api/compatibility-info', methods=['GET'])
def get_compatibility_info():
    """
    Get API compatibility information
    """
    from_version = request.args.get('from_version', '1.0')
    to_version = request.args.get('to_version', '3.0')
    
    migration_guide = compatibility_manager.get_migration_guide(from_version, to_version)
    
    return jsonify({
        "compatibility_info": migration_guide,
        "supported_versions": list(compatibility_manager.version_mappings.keys()),
        "field_registry": {
            name: asdict(field) for name, field in compatibility_manager.field_registry.items()
        },
        "recommendations": [
            "Always specify API-Version header",
            "Test with new versions before upgrading",
            "Monitor deprecation warnings",
            "Plan migration during low-traffic periods"
        ]
    })

@app.route('/api/version-health', methods=['GET'])
def version_health():
    """
    Health check with version-specific metrics
    """
    version = request.headers.get('API-Version', '1.0')
    
    # Mock usage statistics
    version_stats = {
        "1.0": {"active_clients": 1200, "deprecated": True, "sunset_date": "2024-06-30"},
        "2.0": {"active_clients": 3500, "deprecated": False, "sunset_date": None},
        "3.0": {"active_clients": 2100, "deprecated": False, "sunset_date": None}
    }
    
    stats = version_stats.get(version, {})
    
    return jsonify({
        "version": version,
        "status": "healthy",
        "deprecated": stats.get("deprecated", False),
        "sunset_date": stats.get("sunset_date"),
        "active_clients": stats.get("active_clients", 0),
        "compatibility_level": "backward_compatible",
        "supported_operations": list(compatibility_manager.version_mappings.get(version, [])),
        "timestamp": datetime.now().isoformat()
    })

def demonstrate_backward_compatibility():
    """
    Demonstrate backward compatibility management
    """
    print("🔥 REST API Backward Compatibility - IRCTC Style")
    print("=" * 60)
    
    # Example migration scenarios
    scenarios = [
        ("1.0", "2.0"),
        ("2.0", "3.0"),
        ("1.0", "3.0")
    ]
    
    for from_ver, to_ver in scenarios:
        print(f"\n📈 Migration: {from_ver} -> {to_ver}")
        migration_guide = compatibility_manager.get_migration_guide(from_ver, to_ver)
        
        print(f"Compatibility Level: {migration_guide['compatibility_level']}")
        print(f"Added Fields: {migration_guide['added_fields']}")
        print(f"Removed Fields: {migration_guide['removed_fields']}")
        
        print("Migration Steps:")
        for step in migration_guide['migration_steps']:
            print(f"  {step}")
    
    print("\n🎯 Backward Compatibility Best Practices:")
    print("1. Never remove required fields in minor versions")
    print("2. Always provide default values for new fields")
    print("3. Use deprecation warnings before removing features")
    print("4. Maintain field types - don't change string to int")
    print("5. Add new optional fields only")
    
    print("\n⚠️  Breaking Changes to Avoid:")
    print("1. Changing field names or types")
    print("2. Making optional fields required")
    print("3. Removing fields without deprecation period")
    print("4. Changing response format structure")
    print("5. Modifying error response format")
    
    print("\n💡 IRCTC Lessons Learned:")
    print("1. Mobile apps update slowly - maintain compatibility longer")
    print("2. Regional language support requires careful field mapping")
    print("3. Railway booking is critical - never break during rush hours")
    print("4. Provide clear upgrade paths for booking partners")

if __name__ == "__main__":
    demonstrate_backward_compatibility()
    
    # Start Flask app for testing
    # app.run(debug=True, port=5003)
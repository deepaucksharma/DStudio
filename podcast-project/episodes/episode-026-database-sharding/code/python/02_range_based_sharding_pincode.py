#!/usr/bin/env python3
"""
Range-based Sharding using Indian PIN codes
भारतीय पिन कोड आधारित रेंज शार्डिंग

यह example दिखाता है कि कैसे भारत के PIN codes का use करके
geographical range-based sharding implement करें।
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import bisect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PincodeRange:
    """PIN code range definition"""
    start_pin: int
    end_pin: int
    region_name: str
    state: str
    shard_name: str
    shard_host: str


class PincodeShardManager:
    """भारतीय PIN code based sharding system"""
    
    def __init__(self):
        """Initialize with Indian PIN code ranges"""
        self.pincode_ranges = self._initialize_indian_pincode_ranges()
        # Sort ranges by start_pin for binary search
        self.pincode_ranges.sort(key=lambda x: x.start_pin)
        
        logger.info(f"PIN code sharding initialized with {len(self.pincode_ranges)} ranges")
    
    def _initialize_indian_pincode_ranges(self) -> List[PincodeRange]:
        """
        Initialize Indian PIN code ranges based on postal circles
        भारतीय पोस्टल सर्कल के अनुसार PIN code ranges
        """
        return [
            # Delhi (110xxx-122xxx)
            PincodeRange(110001, 122413, "Delhi NCR", "Delhi", 
                        "delhi_shard", "delhi-ecom-db.india.com"),
            
            # Mumbai (400xxx-421xxx) 
            PincodeRange(400001, 421605, "Mumbai Metro", "Maharashtra",
                        "mumbai_shard", "mumbai-ecom-db.india.com"),
            
            # Kolkata (700xxx-743xxx)
            PincodeRange(700001, 743711, "Kolkata Region", "West Bengal",
                        "kolkata_shard", "kolkata-ecom-db.india.com"),
            
            # Chennai (600xxx-635xxx)
            PincodeRange(600001, 635812, "Chennai Region", "Tamil Nadu", 
                        "chennai_shard", "chennai-ecom-db.india.com"),
            
            # Bangalore (560xxx-576xxx)
            PincodeRange(560001, 576248, "Bangalore Region", "Karnataka",
                        "bangalore_shard", "bangalore-ecom-db.india.com"),
            
            # Hyderabad (500xxx-509xxx)
            PincodeRange(500001, 509412, "Hyderabad Region", "Telangana",
                        "hyderabad_shard", "hyderabad-ecom-db.india.com"),
            
            # Pune (411xxx-414xxx)
            PincodeRange(411001, 414806, "Pune Region", "Maharashtra",
                        "pune_shard", "pune-ecom-db.india.com"),
            
            # Ahmedabad (380xxx-388xxx)
            PincodeRange(380001, 388640, "Ahmedabad Region", "Gujarat",
                        "ahmedabad_shard", "ahmedabad-ecom-db.india.com"),
            
            # North India (other states)
            PincodeRange(110000, 199999, "North India", "Multiple States",
                        "north_india_shard", "north-ecom-db.india.com"),
            
            # South India (other areas)  
            PincodeRange(500000, 699999, "South India", "Multiple States",
                        "south_india_shard", "south-ecom-db.india.com"),
            
            # East India
            PincodeRange(700000, 799999, "East India", "Multiple States", 
                        "east_india_shard", "east-ecom-db.india.com"),
            
            # West India 
            PincodeRange(300000, 499999, "West India", "Multiple States",
                        "west_india_shard", "west-ecom-db.india.com"),
        ]
    
    def get_shard_for_pincode(self, pincode: str) -> Optional[PincodeRange]:
        """
        Get appropriate shard for given PIN code
        
        Args:
            pincode: 6-digit Indian PIN code
            
        Returns:
            PincodeRange object or None if not found
        """
        # Validate PIN code format
        if not self._validate_pincode(pincode):
            raise ValueError(f"Invalid PIN code format: {pincode}")
        
        pin_int = int(pincode)
        
        # Binary search for the range containing this PIN code
        for range_obj in self.pincode_ranges:
            if range_obj.start_pin <= pin_int <= range_obj.end_pin:
                logger.info(f"PIN {pincode} mapped to {range_obj.shard_name} ({range_obj.region_name})")
                return range_obj
        
        # If no exact match found, use fallback logic
        logger.warning(f"PIN {pincode} not found in defined ranges, using fallback")
        return self._get_fallback_shard(pin_int)
    
    def _validate_pincode(self, pincode: str) -> bool:
        """Validate Indian PIN code format"""
        # Remove spaces and handle various formats
        clean_pin = pincode.replace(' ', '').replace('-', '')
        
        # Must be exactly 6 digits
        if len(clean_pin) != 6 or not clean_pin.isdigit():
            return False
        
        # First digit should be 1-8 (valid postal circles in India)
        first_digit = int(clean_pin[0])
        return 1 <= first_digit <= 8
    
    def _get_fallback_shard(self, pin_int: int) -> PincodeRange:
        """Get fallback shard based on PIN code first digit"""
        first_digit = int(str(pin_int)[0])
        
        fallback_mapping = {
            1: "north_india_shard",      # Delhi, Punjab, Haryana
            2: "north_india_shard",      # Uttar Pradesh, Uttarakhand  
            3: "west_india_shard",       # Rajasthan, Gujarat
            4: "west_india_shard",       # Maharashtra, Goa
            5: "south_india_shard",      # Andhra Pradesh, Karnataka
            6: "south_india_shard",      # Tamil Nadu, Kerala
            7: "east_india_shard",       # West Bengal, Odisha
            8: "east_india_shard",       # Bihar, Jharkhand
        }
        
        shard_name = fallback_mapping.get(first_digit, "north_india_shard")
        
        return PincodeRange(
            start_pin=pin_int,
            end_pin=pin_int,
            region_name="Fallback Region",
            state="Unknown",
            shard_name=shard_name,
            shard_host=f"{shard_name.replace('_', '-')}.india.com"
        )
    
    def get_shards_in_radius(self, center_pincode: str, radius_km: int) -> List[PincodeRange]:
        """
        Get all shards within a geographical radius (simplified implementation)
        
        Args:
            center_pincode: Central PIN code
            radius_km: Radius in kilometers
            
        Returns:
            List of PincodeRange objects within radius
        """
        # This is a simplified implementation
        # In production, you'd use actual geographical coordinates
        
        center_pin = int(center_pincode)
        pin_range_km = radius_km * 10  # Rough approximation: 10 PIN units per km
        
        relevant_shards = []
        
        for range_obj in self.pincode_ranges:
            # Check if range overlaps with radius
            if (range_obj.start_pin <= center_pin + pin_range_km and 
                range_obj.end_pin >= center_pin - pin_range_km):
                relevant_shards.append(range_obj)
        
        return relevant_shards
    
    def get_regional_analytics(self, orders: List[Dict]) -> Dict:
        """
        Analyze order distribution across regions
        
        Args:
            orders: List of orders with pincode field
            
        Returns:
            Regional analytics dictionary
        """
        region_stats = {}
        
        for order in orders:
            pincode = order.get('delivery_pincode')
            if not pincode:
                continue
                
            try:
                shard = self.get_shard_for_pincode(pincode)
                if shard:
                    region = shard.region_name
                    
                    if region not in region_stats:
                        region_stats[region] = {
                            'order_count': 0,
                            'total_value': 0,
                            'shard_name': shard.shard_name
                        }
                    
                    region_stats[region]['order_count'] += 1
                    region_stats[region]['total_value'] += order.get('amount', 0)
                    
            except ValueError as e:
                logger.warning(f"Invalid pincode in order: {e}")
        
        return region_stats


# Example usage - Flipkart/Amazon जैसे e-commerce के लिए
def main():
    """Main example demonstrating PIN code based sharding"""
    
    shard_manager = PincodeShardManager()
    
    # Sample e-commerce orders with delivery PIN codes
    sample_orders = [
        {'order_id': 'FL001', 'delivery_pincode': '110001', 'amount': 2500},  # Delhi
        {'order_id': 'FL002', 'delivery_pincode': '400001', 'amount': 3200},  # Mumbai
        {'order_id': 'FL003', 'delivery_pincode': '560001', 'amount': 1800},  # Bangalore
        {'order_id': 'FL004', 'delivery_pincode': '700001', 'amount': 4100},  # Kolkata
        {'order_id': 'FL005', 'delivery_pincode': '600001', 'amount': 2900},  # Chennai
        {'order_id': 'FL006', 'delivery_pincode': '380001', 'amount': 3600},  # Ahmedabad
        {'order_id': 'FL007', 'delivery_pincode': '500001', 'amount': 2200},  # Hyderabad
        {'order_id': 'FL008', 'delivery_pincode': '411001', 'amount': 3800},  # Pune
        {'order_id': 'FL009', 'delivery_pincode': '141001', 'amount': 1900},  # Ludhiana
        {'order_id': 'FL010', 'delivery_pincode': '226001', 'amount': 2700},  # Lucknow
    ]
    
    print("\n🏬 ई-कॉमर्स PIN Code शार्डिंग सिस्टम")
    print("=" * 50)
    
    # Test shard assignment for each PIN code
    print("\n📦 Order to Shard Mapping:")
    print("-" * 40)
    
    for order in sample_orders:
        pincode = order['delivery_pincode']
        shard = shard_manager.get_shard_for_pincode(pincode)
        
        if shard:
            print(f"Order {order['order_id']}: PIN {pincode} -> "
                  f"{shard.shard_name} ({shard.region_name})")
    
    # Regional analytics
    print("\n📊 Regional Order Analytics:")
    print("-" * 35)
    
    analytics = shard_manager.get_regional_analytics(sample_orders)
    
    total_orders = sum(stats['order_count'] for stats in analytics.values())
    total_value = sum(stats['total_value'] for stats in analytics.values())
    
    for region, stats in analytics.items():
        order_percentage = (stats['order_count'] / total_orders) * 100
        value_percentage = (stats['total_value'] / total_value) * 100
        avg_order_value = stats['total_value'] / stats['order_count']
        
        print(f"\n{region}:")
        print(f"  Orders: {stats['order_count']} ({order_percentage:.1f}%)")
        print(f"  Value: ₹{stats['total_value']:,} ({value_percentage:.1f}%)")
        print(f"  Avg Order: ₹{avg_order_value:.0f}")
        print(f"  Shard: {stats['shard_name']}")
    
    # Test radius-based shard selection for Mumbai delivery
    print("\n🚚 Radius-based Delivery (Mumbai center):")
    print("-" * 45)
    
    mumbai_center = "400001"
    nearby_shards = shard_manager.get_shards_in_radius(mumbai_center, 50)  # 50km radius
    
    print(f"Shards within 50km of PIN {mumbai_center}:")
    for shard in nearby_shards:
        print(f"  - {shard.shard_name} ({shard.region_name})")
    
    print(f"\n💡 Total shards for Mumbai region delivery: {len(nearby_shards)}")


if __name__ == "__main__":
    main()
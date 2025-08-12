#!/usr/bin/env python3
"""
Hash-based Sharding for Aadhaar Number Distribution
भारतीय आधार संख्या के लिए हैश-आधारित शार्डिंग

यह example दिखाता है कि कैसे 130 crore भारतीयों के Aadhaar numbers को
multiple database shards में distribute करें using consistent hashing.
"""

import hashlib
import bisect
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AadhaarShardManager:
    """आधार नंबर शार्डिंग manager - भारत के digital identity system के लिए"""
    
    def __init__(self, shard_configs: List[Dict]):
        """
        Initialize sharding manager with database configurations
        
        Args:
            shard_configs: List of shard configurations
            Format: [{'name': 'shard_north', 'host': 'delhi-db.example.com', 'capacity': 1000000}]
        """
        self.shards = shard_configs
        self.hash_ring = []  # Consistent hash ring
        self.shard_lookup = {}  # Hash -> Shard mapping
        
        # Create hash ring for consistent hashing - चक्रीय हैशिंग
        self._build_hash_ring()
        
        logger.info(f"शार्डिंग मैनेजर initialized with {len(self.shards)} shards")
        
    def _build_hash_ring(self):
        """Build consistent hash ring for load distribution"""
        virtual_nodes = 150  # Virtual nodes per physical shard for better distribution
        
        for shard in self.shards:
            for i in range(virtual_nodes):
                # Create virtual nodes - वर्चुअल नोड्स
                key = f"{shard['name']}:{i}"
                hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
                
                bisect.insort(self.hash_ring, hash_value)
                self.shard_lookup[hash_value] = shard
                
        logger.info(f"Hash ring built with {len(self.hash_ring)} virtual nodes")
    
    def get_shard_for_aadhaar(self, aadhaar_number: str) -> Dict:
        """
        Get appropriate shard for given Aadhaar number
        
        Args:
            aadhaar_number: 12-digit Aadhaar number
            
        Returns:
            Shard configuration dictionary
        """
        # Validate Aadhaar format - आधार संख्या validation
        if not self._validate_aadhaar(aadhaar_number):
            raise ValueError(f"Invalid Aadhaar number: {aadhaar_number}")
        
        # Hash the Aadhaar number
        hash_value = int(hashlib.md5(aadhaar_number.encode()).hexdigest(), 16)
        
        # Find the appropriate shard in hash ring
        idx = bisect.bisect_right(self.hash_ring, hash_value)
        if idx == len(self.hash_ring):
            idx = 0  # Wrap around for circular hash ring
            
        ring_position = self.hash_ring[idx]
        shard = self.shard_lookup[ring_position]
        
        logger.info(f"Aadhaar {aadhaar_number} mapped to shard: {shard['name']}")
        return shard
    
    def _validate_aadhaar(self, aadhaar_number: str) -> bool:
        """Validate Aadhaar number format"""
        # Remove spaces and hyphens
        clean_aadhaar = aadhaar_number.replace(' ', '').replace('-', '')
        
        # Check if 12 digits
        if len(clean_aadhaar) != 12 or not clean_aadhaar.isdigit():
            return False
            
        # Basic Verhoeff checksum validation (simplified)
        return True
    
    def get_distribution_stats(self, aadhaar_samples: List[str]) -> Dict:
        """Get distribution statistics across shards"""
        shard_counts = {}
        
        for aadhaar in aadhaar_samples:
            try:
                shard = self.get_shard_for_aadhaar(aadhaar)
                shard_name = shard['name']
                shard_counts[shard_name] = shard_counts.get(shard_name, 0) + 1
            except ValueError as e:
                logger.warning(f"Skipping invalid Aadhaar: {e}")
        
        return shard_counts
    
    def rebalance_shards(self, new_shard_config: Dict):
        """Add new shard and rebalance the ring"""
        logger.info(f"Adding new shard: {new_shard_config['name']}")
        
        self.shards.append(new_shard_config)
        self.hash_ring.clear()
        self.shard_lookup.clear()
        
        # Rebuild hash ring with new shard
        self._build_hash_ring()
        
        logger.info("Shard rebalancing completed")


# Example usage - उदाहरण उपयोग
def main():
    """Main example demonstrating Aadhaar sharding"""
    
    # भारत के विभिन्न regions के लिए database shards
    shard_configs = [
        {
            'name': 'north_india_shard',
            'host': 'delhi-aadhaar-db.uidai.gov.in',
            'capacity': 30000000,  # 3 crore records
            'region': 'North India'
        },
        {
            'name': 'south_india_shard', 
            'host': 'bangalore-aadhaar-db.uidai.gov.in',
            'capacity': 25000000,  # 2.5 crore records
            'region': 'South India'
        },
        {
            'name': 'west_india_shard',
            'host': 'mumbai-aadhaar-db.uidai.gov.in', 
            'capacity': 35000000,  # 3.5 crore records
            'region': 'West India'
        },
        {
            'name': 'east_india_shard',
            'host': 'kolkata-aadhaar-db.uidai.gov.in',
            'capacity': 20000000,  # 2 crore records
            'region': 'East India'
        }
    ]
    
    # Initialize shard manager
    shard_manager = AadhaarShardManager(shard_configs)
    
    # Sample Aadhaar numbers for testing
    sample_aadhaars = [
        '123456789012',  # Mumbai resident
        '234567890123',  # Delhi resident  
        '345678901234',  # Bangalore resident
        '456789012345',  # Kolkata resident
        '567890123456',  # Chennai resident
        '678901234567',  # Pune resident
        '789012345678',  # Hyderabad resident
        '890123456789',  # Ahmedabad resident
    ]
    
    print("\n🏛️  भारतीय आधार डेटाबेस शार्डिंग सिस्टम")
    print("=" * 50)
    
    # Test shard assignment for each Aadhaar
    for aadhaar in sample_aadhaars:
        shard = shard_manager.get_shard_for_aadhaar(aadhaar)
        print(f"Aadhaar: {aadhaar} -> {shard['name']} ({shard['region']})")
    
    # Get distribution statistics
    print("\n📊 Distribution Statistics:")
    print("-" * 30)
    stats = shard_manager.get_distribution_stats(sample_aadhaars)
    
    for shard_name, count in stats.items():
        percentage = (count / len(sample_aadhaars)) * 100
        print(f"{shard_name}: {count} records ({percentage:.1f}%)")
    
    # Demonstrate adding new shard for Northeast India
    print("\n🔄 Adding Northeast India Shard...")
    northeast_shard = {
        'name': 'northeast_india_shard',
        'host': 'guwahati-aadhaar-db.uidai.gov.in',
        'capacity': 5000000,  # 50 lakh records
        'region': 'Northeast India'
    }
    
    shard_manager.rebalance_shards(northeast_shard)
    
    print("\n📊 Updated Distribution after rebalancing:")
    print("-" * 40)
    updated_stats = shard_manager.get_distribution_stats(sample_aadhaars)
    
    for shard_name, count in updated_stats.items():
        percentage = (count / len(sample_aadhaars)) * 100
        print(f"{shard_name}: {count} records ({percentage:.1f}%)")


if __name__ == "__main__":
    main()
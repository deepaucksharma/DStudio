#!/usr/bin/env python3
"""
Geo-based Sharding for State-wise User Data Distribution
भारतीय राज्य आधारित भौगोलिक शार्डिंग

यह example दिखाता है कि कैसे भारत के 28 states और 8 union territories
के आधार पर geographical sharding implement करें।
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeographicalZone(Enum):
    """भारतीय भौगोलिक क्षेत्र"""
    NORTH = "North India"
    SOUTH = "South India" 
    EAST = "East India"
    WEST = "West India"
    NORTHEAST = "Northeast India"
    CENTRAL = "Central India"


@dataclass
class StateShardConfig:
    """State-wise shard configuration"""
    state_name: str
    state_code: str
    zone: GeographicalZone
    capital: str
    population_crore: float  # Population in crores
    shard_name: str
    primary_host: str
    secondary_host: str
    is_metro_state: bool
    languages: List[str]


class GeoShardManager:
    """भारतीय राज्य आधारित geographical sharding system"""
    
    def __init__(self):
        """Initialize with Indian states and UT configurations"""
        self.state_configs = self._initialize_indian_states()
        self.zone_shards = self._organize_by_zones()
        
        logger.info(f"Geo-sharding initialized with {len(self.state_configs)} states/UTs")
    
    def _initialize_indian_states(self) -> Dict[str, StateShardConfig]:
        """Initialize Indian states and Union Territories with shard configs"""
        
        states = {
            # North India - उत्तर भारत
            'delhi': StateShardConfig(
                'Delhi', 'DL', GeographicalZone.NORTH, 'New Delhi', 3.2,
                'delhi_metro_shard', 'delhi-primary.india.db', 'delhi-secondary.india.db',
                True, ['Hindi', 'English', 'Punjabi']
            ),
            'punjab': StateShardConfig(
                'Punjab', 'PB', GeographicalZone.NORTH, 'Chandigarh', 2.8,
                'north_shard_1', 'chandigarh-primary.india.db', 'chandigarh-secondary.india.db',
                False, ['Punjabi', 'Hindi']
            ),
            'haryana': StateShardConfig(
                'Haryana', 'HR', GeographicalZone.NORTH, 'Chandigarh', 2.5,
                'north_shard_1', 'chandigarh-primary.india.db', 'chandigarh-secondary.india.db',
                False, ['Hindi', 'Punjabi']
            ),
            'uttar_pradesh': StateShardConfig(
                'Uttar Pradesh', 'UP', GeographicalZone.NORTH, 'Lucknow', 23.4,
                'up_mega_shard', 'lucknow-primary.india.db', 'kanpur-secondary.india.db', 
                False, ['Hindi', 'Urdu']
            ),
            'rajasthan': StateShardConfig(
                'Rajasthan', 'RJ', GeographicalZone.NORTH, 'Jaipur', 6.9,
                'north_shard_2', 'jaipur-primary.india.db', 'jodhpur-secondary.india.db',
                False, ['Hindi', 'Rajasthani']
            ),
            
            # South India - दक्षिण भारत  
            'karnataka': StateShardConfig(
                'Karnataka', 'KA', GeographicalZone.SOUTH, 'Bengaluru', 6.7,
                'bangalore_tech_shard', 'bangalore-primary.india.db', 'mysore-secondary.india.db',
                True, ['Kannada', 'English', 'Hindi']
            ),
            'tamil_nadu': StateShardConfig(
                'Tamil Nadu', 'TN', GeographicalZone.SOUTH, 'Chennai', 7.6,
                'chennai_metro_shard', 'chennai-primary.india.db', 'coimbatore-secondary.india.db',
                True, ['Tamil', 'English']
            ),
            'andhra_pradesh': StateShardConfig(
                'Andhra Pradesh', 'AP', GeographicalZone.SOUTH, 'Amaravati', 5.3,
                'south_shard_1', 'visakhapatnam-primary.india.db', 'vijayawada-secondary.india.db',
                False, ['Telugu', 'Hindi']
            ),
            'telangana': StateShardConfig(
                'Telangana', 'TG', GeographicalZone.SOUTH, 'Hyderabad', 3.9,
                'hyderabad_tech_shard', 'hyderabad-primary.india.db', 'warangal-secondary.india.db',
                True, ['Telugu', 'Hindi', 'English']
            ),
            'kerala': StateShardConfig(
                'Kerala', 'KL', GeographicalZone.SOUTH, 'Thiruvananthapuram', 3.5,
                'south_shard_2', 'kochi-primary.india.db', 'kozhikode-secondary.india.db',
                False, ['Malayalam', 'English']
            ),
            
            # West India - पश्चिम भारत
            'maharashtra': StateShardConfig(
                'Maharashtra', 'MH', GeographicalZone.WEST, 'Mumbai', 12.4,
                'mumbai_financial_shard', 'mumbai-primary.india.db', 'pune-secondary.india.db',
                True, ['Marathi', 'Hindi', 'English']
            ),
            'gujarat': StateShardConfig(
                'Gujarat', 'GJ', GeographicalZone.WEST, 'Gandhinagar', 6.2,
                'west_shard_1', 'ahmedabad-primary.india.db', 'surat-secondary.india.db',
                False, ['Gujarati', 'Hindi']
            ),
            'goa': StateShardConfig(
                'Goa', 'GA', GeographicalZone.WEST, 'Panaji', 0.15,
                'west_shard_2', 'panaji-primary.india.db', 'margao-secondary.india.db',
                False, ['Konkani', 'English', 'Hindi']
            ),
            
            # East India - पूर्व भारत
            'west_bengal': StateShardConfig(
                'West Bengal', 'WB', GeographicalZone.EAST, 'Kolkata', 9.7,
                'kolkata_cultural_shard', 'kolkata-primary.india.db', 'durgapur-secondary.india.db',
                True, ['Bengali', 'Hindi', 'English']
            ),
            'odisha': StateShardConfig(
                'Odisha', 'OR', GeographicalZone.EAST, 'Bhubaneswar', 4.5,
                'east_shard_1', 'bhubaneswar-primary.india.db', 'cuttack-secondary.india.db',
                False, ['Odia', 'Hindi']
            ),
            'bihar': StateShardConfig(
                'Bihar', 'BR', GeographicalZone.EAST, 'Patna', 12.4,
                'east_shard_2', 'patna-primary.india.db', 'gaya-secondary.india.db',
                False, ['Hindi', 'Bhojpuri']
            ),
            
            # Northeast India - पूर्वोत्तर भारत
            'assam': StateShardConfig(
                'Assam', 'AS', GeographicalZone.NORTHEAST, 'Dispur', 3.5,
                'northeast_shard', 'guwahati-primary.india.db', 'dibrugarh-secondary.india.db',
                False, ['Assamese', 'Bengali', 'Hindi']
            ),
            
            # Central India - मध्य भारत  
            'madhya_pradesh': StateShardConfig(
                'Madhya Pradesh', 'MP', GeographicalZone.CENTRAL, 'Bhopal', 8.3,
                'central_shard_1', 'bhopal-primary.india.db', 'indore-secondary.india.db',
                False, ['Hindi']
            ),
        }
        
        return states
    
    def _organize_by_zones(self) -> Dict[GeographicalZone, List[str]]:
        """Organize states by geographical zones"""
        zone_mapping = defaultdict(list)
        
        for state_key, config in self.state_configs.items():
            zone_mapping[config.zone].append(state_key)
        
        return dict(zone_mapping)
    
    def get_shard_for_state(self, state_identifier: str) -> Optional[StateShardConfig]:
        """
        Get shard configuration for a state
        
        Args:
            state_identifier: State name, code, or key
            
        Returns:
            StateShardConfig or None
        """
        # Try direct key lookup
        if state_identifier.lower().replace(' ', '_') in self.state_configs:
            return self.state_configs[state_identifier.lower().replace(' ', '_')]
        
        # Try state code lookup
        for config in self.state_configs.values():
            if config.state_code.lower() == state_identifier.lower():
                return config
        
        # Try state name lookup
        for config in self.state_configs.values():
            if config.state_name.lower() == state_identifier.lower():
                return config
        
        logger.warning(f"State not found: {state_identifier}")
        return None
    
    def get_zone_shards(self, zone: GeographicalZone) -> List[StateShardConfig]:
        """Get all shard configs for a geographical zone"""
        zone_states = self.zone_shards.get(zone, [])
        return [self.state_configs[state] for state in zone_states]
    
    def get_nearest_shards(self, user_state: str, max_distance: int = 2) -> List[StateShardConfig]:
        """
        Get nearest shards based on geographical proximity
        (Simplified implementation using zone-based logic)
        
        Args:
            user_state: User's state identifier
            max_distance: Maximum zone distance (1=same zone, 2=adjacent zones)
            
        Returns:
            List of nearby shard configurations
        """
        user_config = self.get_shard_for_state(user_state)
        if not user_config:
            return []
        
        nearby_shards = []
        user_zone = user_config.zone
        
        # Add shards from same zone (distance 1)
        same_zone_shards = self.get_zone_shards(user_zone)
        nearby_shards.extend(same_zone_shards)
        
        if max_distance >= 2:
            # Add adjacent zones based on geographical proximity
            adjacent_zones = self._get_adjacent_zones(user_zone)
            for zone in adjacent_zones:
                zone_shards = self.get_zone_shards(zone)
                nearby_shards.extend(zone_shards)
        
        return nearby_shards
    
    def _get_adjacent_zones(self, zone: GeographicalZone) -> List[GeographicalZone]:
        """Get geographically adjacent zones"""
        adjacency_map = {
            GeographicalZone.NORTH: [GeographicalZone.WEST, GeographicalZone.CENTRAL],
            GeographicalZone.SOUTH: [GeographicalZone.WEST, GeographicalZone.CENTRAL],
            GeographicalZone.EAST: [GeographicalZone.NORTHEAST, GeographicalZone.CENTRAL],
            GeographicalZone.WEST: [GeographicalZone.NORTH, GeographicalZone.SOUTH, GeographicalZone.CENTRAL],
            GeographicalZone.NORTHEAST: [GeographicalZone.EAST],
            GeographicalZone.CENTRAL: [GeographicalZone.NORTH, GeographicalZone.SOUTH, GeographicalZone.EAST, GeographicalZone.WEST],
        }
        
        return adjacency_map.get(zone, [])
    
    def analyze_user_distribution(self, users: List[Dict]) -> Dict:
        """Analyze user distribution across states and zones"""
        state_stats = defaultdict(int)
        zone_stats = defaultdict(int)
        shard_stats = defaultdict(int)
        
        total_users = len(users)
        
        for user in users:
            state = user.get('state', '').lower()
            config = self.get_shard_for_state(state)
            
            if config:
                state_stats[config.state_name] += 1
                zone_stats[config.zone.value] += 1
                shard_stats[config.shard_name] += 1
        
        return {
            'total_users': total_users,
            'state_distribution': dict(state_stats),
            'zone_distribution': dict(zone_stats),
            'shard_distribution': dict(shard_stats),
            'coverage_percentage': (len(state_stats) / len(self.state_configs)) * 100
        }
    
    def recommend_shard_scaling(self, analytics: Dict) -> List[Dict]:
        """Recommend shard scaling based on user distribution"""
        recommendations = []
        shard_distribution = analytics.get('shard_distribution', {})
        total_users = analytics.get('total_users', 0)
        
        if total_users == 0:
            return recommendations
        
        # Calculate average users per shard
        avg_users_per_shard = total_users / len(shard_distribution)
        
        for shard_name, user_count in shard_distribution.items():
            load_percentage = (user_count / total_users) * 100
            
            if user_count > avg_users_per_shard * 1.5:  # 50% above average
                recommendations.append({
                    'shard_name': shard_name,
                    'action': 'SCALE_UP',
                    'current_users': user_count,
                    'load_percentage': load_percentage,
                    'reason': f'High load - {load_percentage:.1f}% of total users'
                })
            elif user_count < avg_users_per_shard * 0.3:  # 70% below average
                recommendations.append({
                    'shard_name': shard_name,
                    'action': 'CONSIDER_MERGE',
                    'current_users': user_count,
                    'load_percentage': load_percentage,
                    'reason': f'Low utilization - only {load_percentage:.1f}% of total users'
                })
        
        return recommendations


# Example usage - भारतीय social media/gaming platform के लिए
def main():
    """Main example demonstrating geo-based state sharding"""
    
    geo_manager = GeoShardManager()
    
    # Sample users from different Indian states
    sample_users = [
        {'user_id': 'U001', 'name': 'राज शर्मा', 'state': 'Delhi', 'city': 'New Delhi'},
        {'user_id': 'U002', 'name': 'प्रिया पटेल', 'state': 'Gujarat', 'city': 'Ahmedabad'}, 
        {'user_id': 'U003', 'name': 'अर्जुन नायर', 'state': 'Karnataka', 'city': 'Bengaluru'},
        {'user_id': 'U004', 'name': 'दीप्ति मुखर्जी', 'state': 'West Bengal', 'city': 'Kolkata'},
        {'user_id': 'U005', 'name': 'विकास रेड्डी', 'state': 'Telangana', 'city': 'Hyderabad'},
        {'user_id': 'U006', 'name': 'अनिल कुमार', 'state': 'Tamil Nadu', 'city': 'Chennai'},
        {'user_id': 'U007', 'name': 'सुनीता देशपांडे', 'state': 'Maharashtra', 'city': 'Pune'},
        {'user_id': 'U008', 'name': 'रवि यादव', 'state': 'Bihar', 'city': 'Patna'},
        {'user_id': 'U009', 'name': 'मीरा गुप्ता', 'state': 'Uttar Pradesh', 'city': 'Lucknow'},
        {'user_id': 'U010', 'name': 'करीम खान', 'state': 'Assam', 'city': 'Guwahati'},
    ]
    
    print("\n🗺️ भारतीय भौगोलिक शार्डिंग सिस्टम")
    print("=" * 50)
    
    # Test shard assignment for each user
    print("\n👥 User to Shard Mapping:")
    print("-" * 40)
    
    for user in sample_users:
        state = user['state']
        config = geo_manager.get_shard_for_state(state)
        
        if config:
            print(f"{user['name']} ({state}) -> {config.shard_name}")
            print(f"   Zone: {config.zone.value}, Languages: {', '.join(config.languages)}")
        else:
            print(f"{user['name']} ({state}) -> No shard found!")
    
    # Zone-wise distribution
    print("\n🌍 Zone-wise Shard Distribution:")
    print("-" * 40)
    
    for zone in GeographicalZone:
        zone_shards = geo_manager.get_zone_shards(zone)
        unique_shards = list(set(shard.shard_name for shard in zone_shards))
        
        print(f"\n{zone.value}:")
        print(f"  States: {len(zone_shards)}")
        print(f"  Unique Shards: {len(unique_shards)}")
        print(f"  Shard Names: {', '.join(unique_shards)}")
    
    # User analytics
    print("\n📊 User Distribution Analytics:")
    print("-" * 35)
    
    analytics = geo_manager.analyze_user_distribution(sample_users)
    
    print(f"Total Users: {analytics['total_users']}")
    print(f"State Coverage: {analytics['coverage_percentage']:.1f}%")
    
    print("\nZone Distribution:")
    for zone, count in analytics['zone_distribution'].items():
        percentage = (count / analytics['total_users']) * 100
        print(f"  {zone}: {count} users ({percentage:.1f}%)")
    
    print("\nShard Load Distribution:")
    for shard, count in analytics['shard_distribution'].items():
        percentage = (count / analytics['total_users']) * 100
        print(f"  {shard}: {count} users ({percentage:.1f}%)")
    
    # Scaling recommendations
    print("\n🔧 Shard Scaling Recommendations:")
    print("-" * 40)
    
    recommendations = geo_manager.recommend_shard_scaling(analytics)
    
    if recommendations:
        for rec in recommendations:
            print(f"\n{rec['shard_name']}:")
            print(f"  Action: {rec['action']}")
            print(f"  Load: {rec['load_percentage']:.1f}%")
            print(f"  Reason: {rec['reason']}")
    else:
        print("No scaling recommendations at current load levels.")
    
    # Test proximity-based shard selection for Mumbai user
    print("\n📍 Proximity-based Shards (Mumbai user):")
    print("-" * 45)
    
    nearby_shards = geo_manager.get_nearest_shards('Maharashtra', max_distance=2)
    print(f"Recommended shards for Maharashtra user:")
    
    for shard in nearby_shards:
        print(f"  - {shard.shard_name} ({shard.state_name}, {shard.zone.value})")


if __name__ == "__main__":
    main()
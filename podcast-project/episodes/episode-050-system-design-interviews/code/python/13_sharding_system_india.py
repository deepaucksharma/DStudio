#!/usr/bin/env python3
"""
Database Sharding System for India - Episode 50: System Design Interview Mastery
Paytm/PhonePe User Data Sharding by Phone Numbers and Regions

Database sharding जैसे India का postal system है।
हर PIN code area के अनुसार different post offices में data distribute करना।

Author: Hindi Podcast Series
Topic: Database Sharding with Indian Phone Numbers and Geographic Regions
"""

import hashlib
import re
import time
import threading
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json
import sqlite3
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShardingStrategy(Enum):
    """Database sharding strategies"""
    PHONE_NUMBER = "phone_number"          # Mobile number based sharding
    GEOGRAPHIC = "geographic"              # State/region based sharding
    USER_ID_HASH = "user_id_hash"         # Hash-based user ID sharding
    HYBRID = "hybrid"                     # Combination of multiple strategies
    TIME_BASED = "time_based"             # Time-based sharding for analytics

class IndianRegion(Enum):
    """Indian geographic regions for sharding"""
    NORTH = "north"           # Delhi, Punjab, Haryana, UP, Uttarakhand, HP, J&K
    SOUTH = "south"           # Karnataka, Tamil Nadu, Andhra Pradesh, Telangana, Kerala
    WEST = "west"             # Maharashtra, Gujarat, Rajasthan, Goa, MP
    EAST = "east"             # West Bengal, Odisha, Jharkhand, Bihar
    NORTHEAST = "northeast"   # Assam, Manipur, Meghalaya, Mizoram, Nagaland, Tripura, Arunachal Pradesh
    CENTRAL = "central"       # Chhattisgarh, Madhya Pradesh (overlap with west)

@dataclass
class ShardInfo:
    """Information about a database shard"""
    shard_id: str
    region: IndianRegion
    host: str
    port: int
    database: str
    is_active: bool = True
    capacity_percentage: float = 0.0
    connection_count: int = 0
    last_health_check: float = 0.0
    
    def get_connection_string(self) -> str:
        """Get database connection string"""
        return f"postgresql://{self.host}:{self.port}/{self.database}"

@dataclass 
class UserRecord:
    """User record with Indian context"""
    user_id: str
    phone_number: str           # +91XXXXXXXXXX format
    state: str                  # Indian state name
    city: str                   # City name
    pincode: str               # 6-digit PIN code
    region: IndianRegion       # Derived from state
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Derive region from state"""
        if not hasattr(self, 'region') or self.region is None:
            self.region = IndianPhoneNumberSharding.get_region_from_state(self.state)

class IndianPhoneNumberSharding:
    """Phone number based sharding for Indian mobile numbers"""
    
    # Indian mobile number prefixes by region/operator
    REGION_PREFIXES = {
        IndianRegion.NORTH: ['70', '71', '75', '76', '81', '85'],       # Delhi, Punjab, Haryana circles
        IndianRegion.SOUTH: ['72', '73', '74', '82', '86', '87'],       # Karnataka, TN, AP, Telangana
        IndianRegion.WEST: ['77', '78', '79', '83', '88', '89'],        # Maharashtra, Gujarat, Rajasthan  
        IndianRegion.EAST: ['80', '84', '90', '91', '92', '93'],        # WB, Odisha, Bihar
        IndianRegion.NORTHEAST: ['94', '95', '96', '97'],               # NE states
        IndianRegion.CENTRAL: ['98', '99']                              # Central states
    }
    
    # State to region mapping
    STATE_TO_REGION = {
        # North
        'Delhi': IndianRegion.NORTH, 'Punjab': IndianRegion.NORTH, 'Haryana': IndianRegion.NORTH,
        'Uttar Pradesh': IndianRegion.NORTH, 'Uttarakhand': IndianRegion.NORTH, 
        'Himachal Pradesh': IndianRegion.NORTH, 'Jammu and Kashmir': IndianRegion.NORTH,
        'Ladakh': IndianRegion.NORTH, 'Chandigarh': IndianRegion.NORTH,
        
        # South
        'Karnataka': IndianRegion.SOUTH, 'Tamil Nadu': IndianRegion.SOUTH, 
        'Andhra Pradesh': IndianRegion.SOUTH, 'Telangana': IndianRegion.SOUTH,
        'Kerala': IndianRegion.SOUTH, 'Puducherry': IndianRegion.SOUTH,
        
        # West
        'Maharashtra': IndianRegion.WEST, 'Gujarat': IndianRegion.WEST,
        'Rajasthan': IndianRegion.WEST, 'Goa': IndianRegion.WEST,
        'Dadra and Nagar Haveli': IndianRegion.WEST, 'Daman and Diu': IndianRegion.WEST,
        
        # East  
        'West Bengal': IndianRegion.EAST, 'Odisha': IndianRegion.EAST,
        'Jharkhand': IndianRegion.EAST, 'Bihar': IndianRegion.EAST,
        
        # Northeast
        'Assam': IndianRegion.NORTHEAST, 'Manipur': IndianRegion.NORTHEAST,
        'Meghalaya': IndianRegion.NORTHEAST, 'Mizoram': IndianRegion.NORTHEAST,
        'Nagaland': IndianRegion.NORTHEAST, 'Tripura': IndianRegion.NORTHEAST,
        'Arunachal Pradesh': IndianRegion.NORTHEAST, 'Sikkim': IndianRegion.NORTHEAST,
        
        # Central
        'Madhya Pradesh': IndianRegion.CENTRAL, 'Chhattisgarh': IndianRegion.CENTRAL
    }
    
    @staticmethod
    def validate_indian_phone(phone_number: str) -> bool:
        """Validate Indian mobile number format"""
        # Remove spaces, dashes, and country code
        clean_phone = re.sub(r'[\s\-\+]', '', phone_number)
        
        # Remove country code if present
        if clean_phone.startswith('91') and len(clean_phone) == 12:
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('+91') and len(clean_phone) == 13:
            clean_phone = clean_phone[3:]
        
        # Check if it's a valid 10-digit Indian mobile number
        if not (len(clean_phone) == 10 and clean_phone.isdigit()):
            return False
        
        # Check if first digit is valid (6-9)
        if clean_phone[0] not in ['6', '7', '8', '9']:
            return False
        
        return True
    
    @staticmethod
    def normalize_phone_number(phone_number: str) -> str:
        """Normalize phone number to standard format"""
        if not IndianPhoneNumberSharding.validate_indian_phone(phone_number):
            raise ValueError(f"Invalid Indian phone number: {phone_number}")
        
        clean_phone = re.sub(r'[\s\-\+]', '', phone_number)
        
        # Remove country code if present
        if clean_phone.startswith('91') and len(clean_phone) == 12:
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('+91') and len(clean_phone) == 13:
            clean_phone = clean_phone[3:]
        
        return f"+91{clean_phone}"
    
    @staticmethod
    def get_region_from_phone(phone_number: str) -> IndianRegion:
        """Get region based on phone number prefix"""
        normalized = IndianPhoneNumberSharding.normalize_phone_number(phone_number)
        prefix = normalized[3:5]  # Get first 2 digits after +91
        
        for region, prefixes in IndianPhoneNumberSharding.REGION_PREFIXES.items():
            if prefix in prefixes:
                return region
        
        # Default to central for unknown prefixes
        return IndianRegion.CENTRAL
    
    @staticmethod
    def get_region_from_state(state: str) -> IndianRegion:
        """Get region based on Indian state"""
        return IndianPhoneNumberSharding.STATE_TO_REGION.get(state, IndianRegion.CENTRAL)
    
    @staticmethod
    def get_shard_key_from_phone(phone_number: str, num_shards: int = 16) -> int:
        """Generate shard key from phone number"""
        normalized = IndianPhoneNumberSharding.normalize_phone_number(phone_number)
        # Use last 4 digits for better distribution
        last_digits = normalized[-4:]
        hash_value = int(hashlib.md5(last_digits.encode()).hexdigest(), 16)
        return hash_value % num_shards

class PaytmShardingSystem:
    """Paytm-style user data sharding system"""
    
    def __init__(self, num_shards_per_region: int = 4):
        """Initialize Paytm sharding system"""
        self.num_shards_per_region = num_shards_per_region
        self.shards: Dict[str, ShardInfo] = {}
        self.user_shard_mapping: Dict[str, str] = {}  # user_id -> shard_id
        self.phone_shard_mapping: Dict[str, str] = {}  # phone -> shard_id
        self.shard_connections: Dict[str, Any] = {}  # shard_id -> connection
        self.lock = threading.RLock()
        self.stats = defaultdict(int)
        
        # Initialize shards for each region
        self._initialize_shards()
        
        print(f"💳 Paytm Sharding System initialized")
        print(f"   Regions: {len(IndianRegion)}")
        print(f"   Shards per region: {num_shards_per_region}")
        print(f"   Total shards: {len(self.shards)}")
    
    def _initialize_shards(self):
        """Initialize database shards for each Indian region"""
        shard_counter = 0
        
        for region in IndianRegion:
            for shard_num in range(self.num_shards_per_region):
                shard_id = f"{region.value}_shard_{shard_num:02d}"
                
                # Different hosting for different regions (simulate)
                region_hosts = {
                    IndianRegion.NORTH: "delhi-db-cluster.paytm.in",
                    IndianRegion.SOUTH: "bangalore-db-cluster.paytm.in", 
                    IndianRegion.WEST: "mumbai-db-cluster.paytm.in",
                    IndianRegion.EAST: "kolkata-db-cluster.paytm.in",
                    IndianRegion.NORTHEAST: "guwahati-db-cluster.paytm.in",
                    IndianRegion.CENTRAL: "bhopal-db-cluster.paytm.in"
                }
                
                shard = ShardInfo(
                    shard_id=shard_id,
                    region=region,
                    host=region_hosts[region],
                    port=5432 + shard_counter,
                    database=f"paytm_users_{shard_id}",
                    is_active=True,
                    last_health_check=time.time()
                )
                
                self.shards[shard_id] = shard
                
                # Create SQLite connection for demo
                self.shard_connections[shard_id] = sqlite3.connect(
                    f":memory:", 
                    check_same_thread=False
                )
                self._initialize_shard_schema(shard_id)
                
                shard_counter += 1
        
        logger.info(f"Initialized {len(self.shards)} shards across {len(IndianRegion)} regions")
    
    def _initialize_shard_schema(self, shard_id: str):
        """Initialize database schema for shard"""
        conn = self.shard_connections[shard_id]
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                phone_number TEXT UNIQUE NOT NULL,
                state TEXT NOT NULL,
                city TEXT NOT NULL,
                pincode TEXT NOT NULL,
                region TEXT NOT NULL,
                created_at REAL NOT NULL,
                last_activity REAL NOT NULL
            )
        ''')
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        logger.debug(f"Schema initialized for shard: {shard_id}")
    
    def get_shard_for_user(self, user: UserRecord) -> str:
        """Get appropriate shard for user based on multiple factors"""
        with self.lock:
            # Check if user already has a shard assigned
            if user.phone_number in self.phone_shard_mapping:
                return self.phone_shard_mapping[user.phone_number]
            
            # Primary sharding by region
            region = user.region
            
            # Secondary sharding within region by phone number
            phone_hash = IndianPhoneNumberSharding.get_shard_key_from_phone(
                user.phone_number, 
                self.num_shards_per_region
            )
            
            shard_id = f"{region.value}_shard_{phone_hash:02d}"
            
            # Verify shard exists and is active
            if shard_id not in self.shards or not self.shards[shard_id].is_active:
                # Fallback to first active shard in region
                for fallback_id, shard in self.shards.items():
                    if (shard.region == region and 
                        shard.is_active and 
                        shard.capacity_percentage < 90.0):
                        shard_id = fallback_id
                        break
            
            # Store mapping for future lookups
            self.user_shard_mapping[user.user_id] = shard_id
            self.phone_shard_mapping[user.phone_number] = shard_id
            
            logger.debug(f"Assigned user {user.user_id} to shard {shard_id}")
            return shard_id
    
    def store_user(self, user: UserRecord) -> bool:
        """Store user in appropriate shard"""
        try:
            shard_id = self.get_shard_for_user(user)
            conn = self.shard_connections[shard_id]
            cursor = conn.cursor()
            
            # Insert user record
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, phone_number, state, city, pincode, region, created_at, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.user_id, user.phone_number, user.state, user.city, 
                user.pincode, user.region.value, user.created_at, user.last_activity
            ))
            
            conn.commit()
            self.stats['users_stored'] += 1
            
            # Update shard capacity
            self.shards[shard_id].connection_count += 1
            
            logger.info(f"User {user.user_id} stored in shard {shard_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to store user {user.user_id}: {e}")
            return False
    
    def get_user_by_phone(self, phone_number: str) -> Optional[UserRecord]:
        """Retrieve user by phone number"""
        try:
            normalized_phone = IndianPhoneNumberSharding.normalize_phone_number(phone_number)
            
            # Check if we have mapping for this phone
            if normalized_phone in self.phone_shard_mapping:
                shard_id = self.phone_shard_mapping[normalized_phone]
                conn = self.shard_connections[shard_id]
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id, phone_number, state, city, pincode, region, created_at, last_activity
                    FROM users WHERE phone_number = ?
                ''', (normalized_phone,))
                
                row = cursor.fetchone()
                if row:
                    self.stats['users_retrieved'] += 1
                    return UserRecord(
                        user_id=row[0],
                        phone_number=row[1], 
                        state=row[2],
                        city=row[3],
                        pincode=row[4],
                        region=IndianRegion(row[5]),
                        created_at=row[6],
                        last_activity=row[7]
                    )
            
            # Phone not in mapping, search across relevant shards
            region = IndianPhoneNumberSharding.get_region_from_phone(normalized_phone)
            
            for shard_id, shard in self.shards.items():
                if shard.region == region:
                    conn = self.shard_connections[shard_id]
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT user_id, phone_number, state, city, pincode, region, created_at, last_activity
                        FROM users WHERE phone_number = ?
                    ''', (normalized_phone,))
                    
                    row = cursor.fetchone()
                    if row:
                        # Update mapping for future lookups
                        self.phone_shard_mapping[normalized_phone] = shard_id
                        self.user_shard_mapping[row[0]] = shard_id
                        self.stats['users_retrieved'] += 1
                        
                        return UserRecord(
                            user_id=row[0],
                            phone_number=row[1],
                            state=row[2], 
                            city=row[3],
                            pincode=row[4],
                            region=IndianRegion(row[5]),
                            created_at=row[6],
                            last_activity=row[7]
                        )
            
            self.stats['users_not_found'] += 1
            return None
        
        except Exception as e:
            logger.error(f"Failed to retrieve user by phone {phone_number}: {e}")
            return None
    
    def get_users_by_region(self, region: IndianRegion, limit: int = 100) -> List[UserRecord]:
        """Get users from specific region"""
        users = []
        
        try:
            for shard_id, shard in self.shards.items():
                if shard.region == region:
                    conn = self.shard_connections[shard_id]
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT user_id, phone_number, state, city, pincode, region, created_at, last_activity
                        FROM users ORDER BY last_activity DESC LIMIT ?
                    ''', (limit,))
                    
                    rows = cursor.fetchall()
                    for row in rows:
                        users.append(UserRecord(
                            user_id=row[0],
                            phone_number=row[1],
                            state=row[2],
                            city=row[3], 
                            pincode=row[4],
                            region=IndianRegion(row[5]),
                            created_at=row[6],
                            last_activity=row[7]
                        ))
            
            self.stats['regional_queries'] += 1
            return users[:limit]
        
        except Exception as e:
            logger.error(f"Failed to get users by region {region}: {e}")
            return []
    
    def store_transaction(self, transaction: Dict) -> bool:
        """Store transaction in user's shard"""
        try:
            user_id = transaction['user_id']
            phone_number = transaction.get('phone_number')
            
            # Find user's shard
            shard_id = None
            if user_id in self.user_shard_mapping:
                shard_id = self.user_shard_mapping[user_id]
            elif phone_number and phone_number in self.phone_shard_mapping:
                shard_id = self.phone_shard_mapping[phone_number]
            else:
                logger.error(f"Cannot find shard for user {user_id}")
                return False
            
            conn = self.shard_connections[shard_id]
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transactions 
                (transaction_id, user_id, amount, transaction_type, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                transaction['transaction_id'],
                transaction['user_id'],
                transaction['amount'], 
                transaction['transaction_type'],
                transaction.get('created_at', time.time())
            ))
            
            conn.commit()
            self.stats['transactions_stored'] += 1
            
            logger.info(f"Transaction {transaction['transaction_id']} stored in shard {shard_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to store transaction: {e}")
            return False
    
    def get_shard_statistics(self) -> Dict:
        """Get detailed shard statistics"""
        shard_stats = {}
        
        for shard_id, shard in self.shards.items():
            conn = self.shard_connections[shard_id]
            cursor = conn.cursor()
            
            # Get user count
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()[0]
            
            # Get transaction count
            cursor.execute('SELECT COUNT(*) FROM transactions')
            transaction_count = cursor.fetchone()[0]
            
            # Get recent activity
            cursor.execute('SELECT COUNT(*) FROM users WHERE last_activity > ?', 
                         (time.time() - 86400,))  # Last 24 hours
            active_users_24h = cursor.fetchone()[0]
            
            shard_stats[shard_id] = {
                'region': shard.region.value,
                'host': shard.host,
                'is_active': shard.is_active,
                'user_count': user_count,
                'transaction_count': transaction_count,
                'active_users_24h': active_users_24h,
                'capacity_percentage': (user_count / 10000 * 100),  # Assume 10k capacity
                'connection_count': shard.connection_count
            }
        
        return {
            'total_shards': len(self.shards),
            'active_shards': len([s for s in self.shards.values() if s.is_active]),
            'shard_details': shard_stats,
            'global_stats': dict(self.stats)
        }
    
    def rebalance_shard(self, overloaded_shard_id: str) -> bool:
        """Rebalance overloaded shard by moving users"""
        if overloaded_shard_id not in self.shards:
            return False
        
        try:
            overloaded_shard = self.shards[overloaded_shard_id]
            region = overloaded_shard.region
            
            # Find least loaded shard in same region
            region_shards = [(id, shard) for id, shard in self.shards.items() 
                           if shard.region == region and shard.is_active]
            
            if len(region_shards) <= 1:
                logger.warning(f"Cannot rebalance - only one shard in region {region}")
                return False
            
            # Sort by capacity
            region_shards.sort(key=lambda x: x[1].connection_count)
            target_shard_id, target_shard = region_shards[0]
            
            if target_shard_id == overloaded_shard_id:
                target_shard_id, target_shard = region_shards[1]
            
            logger.info(f"Rebalancing from {overloaded_shard_id} to {target_shard_id}")
            
            # For demo, just log the rebalancing action
            # In production, this would involve:
            # 1. Selecting users to move
            # 2. Creating transactions to move data
            # 3. Updating shard mappings
            # 4. Cleaning up old data
            
            self.stats['rebalance_operations'] += 1
            return True
        
        except Exception as e:
            logger.error(f"Rebalancing failed: {e}")
            return False
    
    def shutdown(self):
        """Shutdown all shard connections"""
        for shard_id, conn in self.shard_connections.items():
            try:
                conn.close()
                logger.debug(f"Closed connection for shard {shard_id}")
            except:
                pass
        
        logger.info("All shard connections closed")

def demonstrate_phone_number_sharding():
    """Demonstrate Indian phone number sharding"""
    print("📱 Indian Phone Number Sharding Demo - Paytm User Distribution")
    print("=" * 70)
    
    # Test phone number validation and region detection
    test_phones = [
        "+91 9876543210",  # Valid format with country code
        "8765432109",      # Valid 10-digit number
        "91-7654321098",   # Valid with country code and dash
        "12345",           # Invalid - too short
        "9876543210",      # Valid 10-digit
        "+91 6543210987"   # Valid with country code
    ]
    
    print("\n🔍 Phone Number Validation and Region Detection:")
    print("-" * 55)
    
    for phone in test_phones:
        try:
            is_valid = IndianPhoneNumberSharding.validate_indian_phone(phone)
            if is_valid:
                normalized = IndianPhoneNumberSharding.normalize_phone_number(phone)
                region = IndianPhoneNumberSharding.get_region_from_phone(phone)
                shard_key = IndianPhoneNumberSharding.get_shard_key_from_phone(phone, 4)
                
                print(f"   {phone:<15} → {normalized:<15} Region: {region.value:<10} Shard: {shard_key}")
            else:
                print(f"   {phone:<15} → ❌ Invalid format")
        except Exception as e:
            print(f"   {phone:<15} → ❌ Error: {e}")
    
    # Test region mapping from states
    print(f"\n🗺️ State to Region Mapping:")
    print("-" * 30)
    
    test_states = ['Maharashtra', 'Karnataka', 'Delhi', 'West Bengal', 'Assam', 'Madhya Pradesh']
    for state in test_states:
        region = IndianPhoneNumberSharding.get_region_from_state(state)
        print(f"   {state:<20} → {region.value}")

def demonstrate_paytm_sharding_system():
    """Demonstrate complete Paytm sharding system"""
    print("\n💳 Paytm Sharding System Demo - Complete User Management")
    print("=" * 65)
    
    # Initialize sharding system
    paytm_shards = PaytmShardingSystem(num_shards_per_region=3)
    
    # Create sample Indian users from different regions
    sample_users = [
        UserRecord("user_001", "+91 9876543210", "Maharashtra", "Mumbai", "400001"),
        UserRecord("user_002", "+91 8765432109", "Karnataka", "Bangalore", "560001"),
        UserRecord("user_003", "+91 7654321098", "Delhi", "New Delhi", "110001"),
        UserRecord("user_004", "+91 9123456789", "West Bengal", "Kolkata", "700001"),
        UserRecord("user_005", "+91 8234567890", "Tamil Nadu", "Chennai", "600001"),
        UserRecord("user_006", "+91 7345678901", "Gujarat", "Ahmedabad", "380001"),
        UserRecord("user_007", "+91 6456789012", "Assam", "Guwahati", "781001"),
        UserRecord("user_008", "+91 9567890123", "Punjab", "Chandigarh", "160001"),
        UserRecord("user_009", "+91 8678901234", "Rajasthan", "Jaipur", "302001"),
        UserRecord("user_010", "+91 7789012345", "Madhya Pradesh", "Bhopal", "462001")
    ]
    
    print(f"\n👥 Storing {len(sample_users)} users across shards:")
    print("-" * 50)
    
    # Store users and track shard distribution
    shard_distribution = defaultdict(int)
    
    for user in sample_users:
        success = paytm_shards.store_user(user)
        if success:
            shard_id = paytm_shards.get_shard_for_user(user)
            shard_distribution[shard_id] += 1
            region = user.region.value if hasattr(user, 'region') else 'unknown'
            print(f"   ✅ {user.phone_number:<15} ({user.state:<15}) → {shard_id} ({region})")
        else:
            print(f"   ❌ Failed to store {user.phone_number}")
    
    # Show shard distribution
    print(f"\n📊 User Distribution Across Shards:")
    print("-" * 35)
    for shard_id, count in sorted(shard_distribution.items()):
        print(f"   {shard_id:<20}: {count} users")
    
    # Test user retrieval
    print(f"\n🔍 Testing User Retrieval:")
    print("-" * 30)
    
    test_phones = ["+91 9876543210", "+91 8765432109", "+91 7654321098", "+91 9999999999"]
    
    for phone in test_phones:
        user = paytm_shards.get_user_by_phone(phone)
        if user:
            print(f"   {phone:<15} → Found: {user.user_id} in {user.state}")
        else:
            print(f"   {phone:<15} → Not found")
    
    # Test regional queries
    print(f"\n🌍 Regional User Queries:")
    print("-" * 25)
    
    for region in [IndianRegion.WEST, IndianRegion.SOUTH, IndianRegion.NORTH]:
        users = paytm_shards.get_users_by_region(region, limit=5)
        print(f"   {region.value.upper():<10}: {len(users)} users found")
        for user in users[:2]:  # Show first 2
            print(f"     - {user.phone_number} ({user.state})")
    
    # Simulate transactions
    print(f"\n💰 Simulating Transactions:")
    print("-" * 30)
    
    transactions = [
        {
            'transaction_id': 'TXN_001',
            'user_id': 'user_001',
            'amount': 500.0,
            'transaction_type': 'payment',
            'phone_number': '+91 9876543210'
        },
        {
            'transaction_id': 'TXN_002', 
            'user_id': 'user_002',
            'amount': 1200.0,
            'transaction_type': 'recharge',
            'phone_number': '+91 8765432109'
        },
        {
            'transaction_id': 'TXN_003',
            'user_id': 'user_003', 
            'amount': 750.0,
            'transaction_type': 'transfer',
            'phone_number': '+91 7654321098'
        }
    ]
    
    for txn in transactions:
        success = paytm_shards.store_transaction(txn)
        status = "✅ Stored" if success else "❌ Failed"
        print(f"   {txn['transaction_id']}: ₹{txn['amount']} → {status}")
    
    # Show detailed statistics
    print(f"\n📈 Detailed Shard Statistics:")
    print("-" * 30)
    
    stats = paytm_shards.get_shard_statistics()
    
    print(f"   Total Shards: {stats['total_shards']}")
    print(f"   Active Shards: {stats['active_shards']}")
    
    # Show per-region statistics
    region_stats = defaultdict(lambda: {'shards': 0, 'users': 0, 'transactions': 0})
    
    for shard_id, shard_data in stats['shard_details'].items():
        region = shard_data['region']
        region_stats[region]['shards'] += 1
        region_stats[region]['users'] += shard_data['user_count']
        region_stats[region]['transactions'] += shard_data['transaction_count']
    
    print(f"\n📋 Region-wise Summary:")
    print("-" * 25)
    for region, data in sorted(region_stats.items()):
        print(f"   {region.upper():<12}: {data['shards']} shards, {data['users']} users, {data['transactions']} txns")
    
    # Global statistics
    global_stats = stats['global_stats']
    print(f"\n🌐 Global Statistics:")
    print("-" * 20)
    print(f"   Users Stored: {global_stats['users_stored']}")
    print(f"   Users Retrieved: {global_stats['users_retrieved']}")
    print(f"   Transactions Stored: {global_stats['transactions_stored']}")
    print(f"   Regional Queries: {global_stats['regional_queries']}")
    
    # Cleanup
    paytm_shards.shutdown()
    
    return paytm_shards

def demonstrate_high_load_sharding():
    """Demonstrate sharding under high load"""
    print("\n⚡ High Load Sharding Demo - Diwali Sale Traffic")
    print("=" * 55)
    
    paytm_shards = PaytmShardingSystem(num_shards_per_region=2)
    
    print(f"🎯 Simulating Diwali sale with 1000 concurrent users...")
    
    import random
    import threading
    import concurrent.futures
    
    # Indian states for random user generation
    indian_states = [
        ('Maharashtra', 'Mumbai', '400001'), ('Karnataka', 'Bangalore', '560001'),
        ('Delhi', 'New Delhi', '110001'), ('Tamil Nadu', 'Chennai', '600001'),
        ('West Bengal', 'Kolkata', '700001'), ('Gujarat', 'Ahmedabad', '380001'),
        ('Rajasthan', 'Jaipur', '302001'), ('Punjab', 'Amritsar', '143001'),
        ('Uttar Pradesh', 'Lucknow', '226001'), ('Assam', 'Guwahati', '781001')
    ]
    
    def create_random_user(user_index: int) -> UserRecord:
        """Create random Indian user"""
        state, city, pincode = random.choice(indian_states)
        phone_base = random.randint(7000000000, 9999999999)
        phone = f"+91 {phone_base}"
        
        return UserRecord(
            user_id=f"diwali_user_{user_index:04d}",
            phone_number=phone,
            state=state,
            city=city,
            pincode=pincode
        )
    
    def user_registration_worker(start_idx: int, count: int) -> Dict:
        """Worker thread for user registration"""
        results = {'success': 0, 'failed': 0}
        
        for i in range(count):
            try:
                user = create_random_user(start_idx + i)
                if paytm_shards.store_user(user):
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    
                # Simulate some transactions
                if results['success'] % 3 == 0:  # Every 3rd user makes transaction
                    txn = {
                        'transaction_id': f'DIWALI_TXN_{start_idx + i}',
                        'user_id': user.user_id,
                        'amount': random.uniform(100, 5000),
                        'transaction_type': 'payment',
                        'phone_number': user.phone_number
                    }
                    paytm_shards.store_transaction(txn)
            
            except Exception as e:
                results['failed'] += 1
                if results['failed'] % 50 == 0:  # Log every 50th failure
                    logger.error(f"User creation failed: {e}")
        
        return results
    
    # Run concurrent user registration
    start_time = time.time()
    total_users = 1000
    batch_size = 100
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        
        for i in range(0, total_users, batch_size):
            future = executor.submit(user_registration_worker, i, min(batch_size, total_users - i))
            futures.append(future)
        
        # Collect results
        total_success = 0
        total_failed = 0
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            total_success += result['success']
            total_failed += result['failed']
            
            print(f"   Batch completed: {total_success + total_failed}/{total_users} users processed")
    
    end_time = time.time()
    
    print(f"\n📊 High Load Test Results:")
    print("-" * 30)
    print(f"   Total Users: {total_users}")
    print(f"   Successful Registrations: {total_success}")
    print(f"   Failed Registrations: {total_failed}")
    print(f"   Success Rate: {total_success/total_users*100:.1f}%")
    print(f"   Total Time: {end_time - start_time:.2f}s")
    print(f"   Throughput: {total_users/(end_time - start_time):.1f} users/sec")
    
    # Final shard statistics
    final_stats = paytm_shards.get_shard_statistics()
    
    print(f"\n🏗️ Final Shard Load Distribution:")
    print("-" * 35)
    
    max_load = 0
    min_load = float('inf')
    
    for shard_id, shard_data in final_stats['shard_details'].items():
        user_count = shard_data['user_count']
        region = shard_data['region']
        
        max_load = max(max_load, user_count)
        min_load = min(min_load, user_count) if user_count > 0 else min_load
        
        print(f"   {shard_id:<20}: {user_count:>4} users ({region})")
    
    if max_load > 0 and min_load != float('inf'):
        load_balance_ratio = min_load / max_load
        print(f"\n⚖️ Load Balance Ratio: {load_balance_ratio:.2f} (1.0 = perfect balance)")
    
    paytm_shards.shutdown()

if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_phone_number_sharding()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_paytm_sharding_system()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_high_load_sharding()
    
    print(f"\n✅ Database Sharding Demo Complete!")
    print(f"📚 Key Concepts Demonstrated:")
    print(f"   • Phone Number Sharding - Indian mobile number-based distribution")
    print(f"   • Geographic Sharding - Region-based data partitioning") 
    print(f"   • Hybrid Sharding - Combined phone + geographic strategy")
    print(f"   • Shard Mapping - User-to-shard relationship management")
    print(f"   • Cross-Shard Queries - Regional data aggregation")
    print(f"   • Load Balancing - Even distribution across shards")
    print(f"   • High Availability - Multiple shards per region")
    print(f"   • Indian Context - States, regions, PIN codes, phone formats")
    print(f"   • Scalability - Handling high concurrent load")
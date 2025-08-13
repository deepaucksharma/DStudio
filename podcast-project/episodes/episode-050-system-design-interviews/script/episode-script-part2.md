# Episode 50: System Design Interview Mastery - Part 2 (Hour 2)
## Scalability Patterns aur Database Design ki Duniya

---

## Introduction: Mumbai Monsoon se System Design tak

Namaste doston! Welcome back to part 2 of our system design interview mastery series. Agar aap ne part 1 miss kiya hai, jaldi se sun lijiye - wahan humne basic framework aur requirements gathering cover kiya tha.

Part 2 mein hum deep dive kar rahe hain into the real meat and potatoes of system design - scalability patterns, database design, caching strategies, aur kaise handle karte hain massive Indian systems jaise WhatsApp India, UPI, aur Flipkart Big Billion Days.

Mumbai mein jaise monsoon season mein puri city ka infrastructure test hota hai - roads flood ho jati hain, local trains late chalti hain, power cuts aate hain - exactly waise hi system design interviews mein aapka technical infrastructure ka knowledge test hota hai. Aur just like Mumbai ke log monsoon ke liye prepare karte hain with backup plans, alternative routes, aur emergency supplies, waise hi aapko system design ke liye prepare karna padta hai with multiple scaling strategies, backup systems, aur graceful degradation.

Aaj hum seekhenge ki kaise design karte hain systems jo handle kar saken:
- WhatsApp India ke 500M users aur 100B+ daily messages
- UPI system ke 10 billion monthly transactions 
- Flipkart Big Billion Days ke 100M concurrent users
- Aadhaar verification system ke billion daily verifications

Toh chalo shuru karte hain is technical monsoon ka!

---

## Chapter 1: Scalability Patterns - Mumbai Traffic Management se Seekh

### Vertical vs Horizontal Scaling: South Mumbai vs Suburbs Story

Doston, scalability ko samjhane ke liye main aapko Mumbai ke development pattern se example deta hu. 

**Vertical Scaling - South Mumbai Approach**

South Mumbai mein kya hota hai? Land kam hai, toh log kya karte hain? Upar jaate hain! Altamount Road pe dekho - 50-storey buildings, har floor pe crores ka flat. Yahi hai vertical scaling.

```python
class VerticalScaling:
    def __init__(self):
        self.current_server = {
            'cpu_cores': 4,
            'ram_gb': 16,
            'storage_tb': 1
        }
    
    def scale_up(self, multiplier):
        """Just like building taller in South Mumbai"""
        self.current_server['cpu_cores'] *= multiplier
        self.current_server['ram_gb'] *= multiplier
        self.current_server['storage_tb'] *= multiplier
        
        # Cost increases exponentially, just like South Mumbai real estate!
        cost_multiplier = multiplier ** 1.5
        return f"Upgraded server, cost increased by {cost_multiplier}x"

# Example: Paytm payment server during Diwali
paytm_server = VerticalScaling()
print(paytm_server.scale_up(4))  # 4x bigger server for festival season
```

**Vertical Scaling ke fayde**:
- Simple implementation - just upgrade the box
- No application changes needed
- Shared memory aur resources ka better utilization

**Nuksaan**:
- Extremely expensive at scale - 64-core server costs 10x more than 8-core
- Single point of failure - agar server crash ho gaya, sab kuch band
- Limited by hardware - you can't buy infinite RAM or CPU

**Real Indian Example**: Initially, IRCTC (Indian Railway ticket booking) used massive vertical scaling. Ek huge IBM server tha worth ₹50 crores! But still tatkal booking time pe crash ho jata tha kyunki demand was just too much.

**Horizontal Scaling - Suburbs Development Model**

Ab imagine karo Mumbai suburbs - Andheri, Borivali, Thane. Yahan kya strategy hai? Har jagah similar buildings, connected by local trains aur buses. Yahi hai horizontal scaling!

```python
class HorizontalScaling:
    def __init__(self):
        self.servers = [
            {'id': 1, 'load': 0, 'capacity': 1000},
        ]
        self.load_balancer = LoadBalancer()
    
    def scale_out(self, additional_servers):
        """Add more servers like adding new buildings in suburbs"""
        for i in range(additional_servers):
            new_server = {
                'id': len(self.servers) + 1,
                'load': 0, 
                'capacity': 1000
            }
            self.servers.append(new_server)
        
        print(f"Added {additional_servers} servers. Total capacity: {len(self.servers) * 1000}")
        return self.servers

# Example: Flipkart during Big Billion Days
flipkart_cluster = HorizontalScaling()
flipkart_cluster.scale_out(50)  # Add 50 more servers overnight!
```

**Horizontal Scaling benefits**:
- Cost-effective - 10 small servers cheaper than 1 huge server
- Fault tolerant - agar 2-3 servers down ho jaye, baki chal rahe hain
- Linear scaling - double servers, roughly double capacity

**Challenges**:
- Complex application architecture needed
- Data consistency across multiple servers
- Network communication overhead

### Load Balancing Strategies: Mumbai Traffic Signal Management

Mumbai mein traffic management kaise hoti hai? Multiple strategies combine karke!

**Round Robin - Regular Traffic Signals**

```python
class RoundRobinBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.current = 0
    
    def get_next_server(self):
        """Like traffic signals - each direction gets equal time"""
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server

# IRCTC normal booking - round robin works fine
servers = ['server1', 'server2', 'server3', 'server4']
balancer = RoundRobinBalancer(servers)

for request in range(8):
    server = balancer.get_next_server()
    print(f"Request {request+1} → {server}")
```

**Weighted Round Robin - VIP Lane System**

Mumbai mein dekha hai VIP convoy ke liye separate lane? Waise hi weighted load balancing!

```python
class WeightedRoundRobinBalancer:
    def __init__(self, servers_with_weights):
        self.servers = []
        # Create server list based on weights
        for server, weight in servers_with_weights.items():
            self.servers.extend([server] * weight)
        self.current = 0
    
    def get_next_server(self):
        """High-capacity servers get more requests"""
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server

# Flipkart setup - powerful servers get more weight
server_config = {
    'powerful_server_1': 5,    # Gets 5x more requests
    'powerful_server_2': 5,
    'normal_server_1': 2,      # Gets 2x requests
    'normal_server_2': 2,
    'backup_server': 1         # Gets 1x requests (minimum)
}

flipkart_balancer = WeightedRoundRobinBalancer(server_config)
```

**Least Connections - Smart Traffic Management**

```python
class LeastConnectionsBalancer:
    def __init__(self, servers):
        self.servers = {server: 0 for server in servers}  # Track active connections
    
    def get_least_loaded_server(self):
        """Route to server with least active connections"""
        return min(self.servers.keys(), key=lambda x: self.servers[x])
    
    def handle_request(self, request_duration=1):
        server = self.get_least_loaded_server()
        self.servers[server] += 1  # Increase connection count
        
        print(f"Routing to {server} (connections: {self.servers[server]})")
        return server
    
    def complete_request(self, server):
        """Called when request completes"""
        if self.servers[server] > 0:
            self.servers[server] -= 1

# Zomato during lunch rush - smart routing based on current load
zomato_balancer = LeastConnectionsBalancer(['kitchen_1', 'kitchen_2', 'kitchen_3'])
```

### Circuit Breaker Pattern - Mumbai Monsoon Ki Tarah

Mumbai mein monsoon season mein kya hota hai? Jab bahut zyada paani aa jata hai, toh roads ko block kar dete hain, trains ruk jati hain. Exactly yahi concept hai circuit breaker pattern ka!

```python
import time
import random
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation - like clear roads
    OPEN = "open"           # Service unavailable - like flooded roads  
    HALF_OPEN = "half_open" # Testing - like checking if water receded

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """
        Mumbai traffic analogy:
        - CLOSED: Roads are clear, traffic flowing normally
        - OPEN: Roads flooded, no traffic allowed
        - HALF_OPEN: Testing if roads are passable again
        """
        
        if self.state == CircuitState.OPEN:
            # Check if enough time passed to try again
            if self.last_failure_time and \
               time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                print("🟡 Circuit HALF-OPEN: Testing if service recovered (like checking if flood water receded)")
            else:
                print("🔴 Circuit OPEN: Service unavailable (road flooded, use alternative route)")
                raise Exception("Service unavailable - circuit breaker open")
        
        try:
            # Attempt the call
            result = func(*args, **kwargs)
            self.on_success()
            return result
            
        except self.expected_exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        """Called when service call succeeds"""
        if self.state == CircuitState.HALF_OPEN:
            print("✅ Service recovered! Circuit CLOSED (roads clear again)")
        
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def on_failure(self):
        """Called when service call fails"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"⚠️ Circuit OPEN: Too many failures ({self.failure_count}), blocking traffic")
        else:
            print(f"⚠️ Failure #{self.failure_count}, threshold: {self.failure_threshold}")

# Example: Paytm calling bank API during high load
def unreliable_bank_api():
    """Simulates bank API that might fail during high load"""
    if random.random() < 0.7:  # 70% chance of failure during peak
        raise Exception("Bank API timeout - probably too much load")
    return "Payment successful"

# Paytm's circuit breaker protecting against bank API failures
paytm_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

# Simulate payment requests during Diwali shopping
print("🎆 Diwali shopping rush - testing circuit breaker:\n")

for attempt in range(10):
    try:
        result = paytm_circuit_breaker.call(unreliable_bank_api)
        print(f"✅ Payment {attempt+1}: {result}")
    except Exception as e:
        print(f"❌ Payment {attempt+1}: Failed - {e}")
    
    time.sleep(2)  # Small delay between attempts
    print("---")
```

Is code se kya samjha? Circuit breaker pattern prevents cascade failures. Jaise Mumbai mein ek road flood ho jaye toh traffic police alternate routes suggest karte hain, waise hi circuit breaker alternate services ya cached responses provide karta hai.

---

## Chapter 2: Database Design aur Data Modeling - Mumbai Housing Strategy

### Relational vs NoSQL: Planned Colony vs Slum Redevelopment

Database choice karna Mumbai mein ghar dhundne jaisa hai - location, budget, requirements sab matter karta hai!

**Relational Database - Planned Societies (like Hiranandani Gardens)**

```python
# Traditional RDBMS approach - like planned housing societies
class RelationalUserSystem:
    """
    Just like Hiranandani Gardens - everything planned, structured, organized
    But expensive and less flexible
    """
    
    def create_user_tables(self):
        sql_schema = """
        -- Users table - like society member registry
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone_number VARCHAR(15) UNIQUE NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            date_of_birth DATE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Addresses table - like flat details
        CREATE TABLE addresses (
            address_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            building_name VARCHAR(255),
            flat_number VARCHAR(10),
            area VARCHAR(255),
            city VARCHAR(100),
            pincode VARCHAR(6),
            address_type ENUM('home', 'office', 'other'),
            is_default BOOLEAN DEFAULT FALSE
        );
        
        -- Orders table - like society bill payments
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            address_id INTEGER REFERENCES addresses(address_id),
            total_amount DECIMAL(10,2) NOT NULL,
            order_status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled'),
            payment_method VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        -- ACID properties guaranteed - like society rules are strictly enforced
        -- Complex joins possible - like connecting user->address->orders easily
        -- But scaling is expensive - like getting bigger flat in same society
        """
        return sql_schema

# Example: HDFC Bank customer management
# They use Oracle/DB2 because they NEED ACID properties for financial data
# Agar bank balance inconsistent ho jaye, customers ka trust khatam!
```

**NoSQL Approach - Flexible Slum Redevelopment (like Dharavi)**

```python
# Document database approach - flexible but requires careful planning
class NoSQLUserSystem:
    """
    Like Dharavi redevelopment - flexible, adaptive, can grow organically
    But requires different mindset and careful design
    """
    
    def create_user_document(self):
        user_document = {
            "_id": "user_12345",
            "email": "mumbai_techie@gmail.com",
            "phone": "+91-9876543210",
            "profile": {
                "full_name": "Rajesh Sharma",
                "date_of_birth": "1992-08-15",
                "occupation": "Software Engineer",
                "company": "Flipkart"
            },
            
            # Embedded addresses - no joins needed!
            "addresses": [
                {
                    "type": "home",
                    "building": "Royal Palms",
                    "area": "Andheri East",
                    "city": "Mumbai",
                    "pincode": "400069",
                    "is_default": True
                },
                {
                    "type": "office",
                    "building": "Flipkart Building",
                    "area": "Bangalore",  # Works from Bangalore office
                    "pincode": "560103",
                    "is_default": False
                }
            ],
            
            # Recent orders embedded - fast access!
            "recent_orders": [
                {
                    "order_id": "ORD_001",
                    "amount": 2500.00,
                    "status": "delivered",
                    "items": ["iPhone case", "Power bank"],
                    "order_date": "2025-01-10"
                }
            ],
            
            # Metadata for fast queries
            "created_at": "2024-03-15T10:30:00Z",
            "last_login": "2025-01-13T14:25:00Z",
            "total_orders": 47,
            "total_spent": 125000.50,
            
            # Can add new fields without schema migration!
            "preferences": {
                "language": "hindi",
                "currency": "INR",
                "notifications": {
                    "email": True,
                    "sms": True,
                    "whatsapp": True
                }
            }
        }
        return user_document

# Example: Zomato restaurant data
# They use MongoDB because restaurant menus change frequently
# New cuisines, seasonal items - schema flexibility needed!
```

### Database Sharding - Mumbai Local Train Line Strategy

Mumbai local trains kaise efficiently run karte hain? Multiple parallel lines! Western, Central, Harbour - each serves different areas. Yahi strategy hai database sharding ki!

```python
class DatabaseSharding:
    """
    Mumbai Local Train model for database sharding:
    - Western Line: Serves Bandra, Andheri, Borivali (User IDs 0-33M)
    - Central Line: Serves Dadar, Kurla, Thane (User IDs 33M-66M)  
    - Harbour Line: Serves Vashi, Panvel (User IDs 66M-100M)
    """
    
    def __init__(self):
        self.shards = {
            'western_line': {
                'server': 'db-west-mumbai.internal',
                'user_range': (0, 33_000_000),
                'areas': ['Bandra', 'Andheri', 'Borivali', 'Malad']
            },
            'central_line': {
                'server': 'db-central-mumbai.internal', 
                'user_range': (33_000_001, 66_000_000),
                'areas': ['Dadar', 'Kurla', 'Thane', 'Kalyan']
            },
            'harbour_line': {
                'server': 'db-harbour-mumbai.internal',
                'user_range': (66_000_001, 100_000_000),
                'areas': ['Vashi', 'Panvel', 'Kharghar']
            }
        }
    
    def get_shard_for_user(self, user_id):
        """Route user to correct database shard - like choosing right train line"""
        for line_name, shard_info in self.shards.items():
            min_id, max_id = shard_info['user_range']
            if min_id <= user_id <= max_id:
                return {
                    'shard': line_name,
                    'server': shard_info['server'],
                    'routing_info': f"User {user_id} → {line_name.replace('_', ' ').title()}"
                }
        
        raise Exception(f"User ID {user_id} out of range - need new train line!")
    
    def create_user(self, user_data):
        """Create user in appropriate shard"""
        user_id = user_data['user_id']
        shard_info = self.get_shard_for_user(user_id)
        
        print(f"🚂 {shard_info['routing_info']}")
        
        # In real implementation, this would connect to actual database
        return {
            'user_created': True,
            'shard': shard_info['shard'],
            'server': shard_info['server']
        }
    
    def get_user(self, user_id):
        """Retrieve user from correct shard"""
        shard_info = self.get_shard_for_user(user_id)
        print(f"🔍 Fetching user {user_id} from {shard_info['shard']}")
        
        # Simulate database query
        return {
            'user_id': user_id,
            'shard': shard_info['shard'],
            'data': f"User data from {shard_info['server']}"
        }

# Example: Flipkart user management during Big Billion Days
flipkart_sharding = DatabaseSharding()

# Create users across different shards
test_users = [
    {'user_id': 15_000_000, 'name': 'Priya Mumbai'},     # Western line
    {'user_id': 45_000_000, 'name': 'Rahul Thane'},     # Central line  
    {'user_id': 75_000_000, 'name': 'Sneha Panvel'}     # Harbour line
]

print("🏬 Flipkart Big Billion Days - User Creation Across Shards:\n")

for user in test_users:
    result = flipkart_sharding.create_user(user)
    print(f"✅ Created: {user['name']} in {result['shard']}")
    print()

# Fetching users
print("📱 User Login Requests During Peak Hours:\n")
for user in test_users:
    result = flipkart_sharding.get_user(user['user_id'])
    print(f"🔓 Login: {user['name']}")
    print()
```

**Sharding ke fayde**:
- Massive scale - har shard independently scale kar sakta hai
- Performance - queries sirf relevant data pe run hoti hai
- Fault isolation - agar ek shard down ho jaye, baki kaam karte rahe

**Challenges**:
- Cross-shard queries complex - imagine Western line se Central line ka data chahiye
- Rebalancing difficult - agar Western line overcrowded ho jaye
- Application complexity - code mein shard routing logic

### Master-Slave Replication - Mumbai Dabba System Strategy

Mumbai ke famous dabbawalas ka system dekha hai? Har area mein ek main collection point (master), aur multiple pickup/delivery points (slaves). Same concept database replication mein!

```python
import threading
import time
import random

class DatabaseReplication:
    """
    Dabba system inspired database replication:
    - Master = Main sorting station (writes)
    - Slaves = Local pickup points (reads)
    """
    
    def __init__(self):
        self.master = {
            'server': 'master-db-mumbai.internal',
            'data': {},
            'write_operations': 0
        }
        
        self.slaves = [
            {
                'server': 'slave-db-andheri.internal', 
                'data': {},
                'read_operations': 0,
                'replication_lag': 0
            },
            {
                'server': 'slave-db-bandra.internal',
                'data': {}, 
                'read_operations': 0,
                'replication_lag': 0
            },
            {
                'server': 'slave-db-thane.internal',
                'data': {},
                'read_operations': 0, 
                'replication_lag': 0
            }
        ]
        
        # Start replication process
        self.start_replication()
    
    def write_to_master(self, key, value):
        """All writes go to master - like main dabba sorting center"""
        self.master['data'][key] = value
        self.master['write_operations'] += 1
        
        print(f"✍️ WRITE to Master: {key} = {value}")
        print(f"   Total writes: {self.master['write_operations']}")
        
        return {"status": "success", "operation": "write", "server": "master"}
    
    def read_from_slave(self, key):
        """Reads distributed across slaves - like local dabba pickup points"""
        # Choose slave with least load (round-robin could work too)
        chosen_slave = min(self.slaves, key=lambda x: x['read_operations'])
        chosen_slave['read_operations'] += 1
        
        value = chosen_slave['data'].get(key, "Not found")
        
        print(f"📖 READ from {chosen_slave['server']}: {key} = {value}")
        print(f"   Read operations: {chosen_slave['read_operations']}")
        
        if chosen_slave['replication_lag'] > 0:
            print(f"   ⚠️ Data might be {chosen_slave['replication_lag']}s behind master")
        
        return {"status": "success", "value": value, "server": chosen_slave['server']}
    
    def start_replication(self):
        """Background process to sync data from master to slaves"""
        def replicate():
            while True:
                # Simulate replication delay (network latency, processing time)
                time.sleep(random.uniform(0.5, 2.0))  # 0.5-2 second delay
                
                for slave in self.slaves:
                    # Copy master data to slave
                    slave['data'] = self.master['data'].copy()
                    slave['replication_lag'] = random.uniform(0.1, 1.5)  # Simulate lag
        
        # Start replication in background thread
        replication_thread = threading.Thread(target=replicate, daemon=True)
        replication_thread.start()

# Example: Zomato restaurant database during lunch rush
zomato_db = DatabaseReplication()

print("🍕 Zomato Database Operations During Lunch Rush (12-2 PM):\n")

# Restaurant updates menu (write to master)
print("📝 Restaurant Menu Updates (Master Writes):")
zomato_db.write_to_master("restaurant_123_menu", "Updated lunch specials")
zomato_db.write_to_master("restaurant_456_availability", "No longer serving pizza")
zomato_db.write_to_master("restaurant_789_offers", "Buy 1 Get 1 Free biryani")

print("\n" + "="*50)

# Customers checking menu (read from slaves)
print("\n👥 Customer Menu Lookups (Slave Reads):")
time.sleep(1)  # Wait a bit for replication
zomato_db.read_from_slave("restaurant_123_menu")
zomato_db.read_from_slave("restaurant_456_availability")
zomato_db.read_from_slave("restaurant_789_offers")
zomato_db.read_from_slave("restaurant_999_reviews")  # This won't exist

print("\n💡 Key Benefits of Master-Slave Setup:")
print("✅ Write performance: All writes go to optimized master server")
print("✅ Read scalability: Multiple slaves handle read traffic")
print("✅ Fault tolerance: If one slave fails, others continue serving")
print("✅ Geographic distribution: Slaves closer to users for faster reads")
```

---

## Chapter 3: Caching Strategies - Mumbai Street Food Ki Tarah

Caching samjhane ke liye Mumbai street food ka perfect example hai! Vada pav wala advance mein kitne vada pav ready rakhta hai? Chai wala kitna milk boil kar rakhta hai? Yahi sab caching strategies hain!

### Cache-Aside Pattern - Vada Pav Stall Strategy

```python
import time
import random

class CacheAsidePattern:
    """
    Mumbai Vada Pav stall strategy:
    - Customer orders vada pav
    - First check if ready-made available (cache)
    - If not, make fresh (database)
    - Store some extra for next customers (cache population)
    """
    
    def __init__(self):
        self.cache = {}  # Ready-made vada pav counter
        self.database = {  # Kitchen - where actual cooking happens
            'vada_pav': {'cooking_time': 3, 'popularity': 10},
            'pav_bhaji': {'cooking_time': 5, 'popularity': 8}, 
            'misal_pav': {'cooking_time': 4, 'popularity': 6},
            'dosa': {'cooking_time': 2, 'popularity': 9}
        }
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_cooking_time = 0
    
    def get_food_item(self, item_name):
        """Customer orders food - check cache first, then cook if needed"""
        print(f"🍴 Customer orders: {item_name}")
        
        # Step 1: Check cache (ready-made counter)
        if item_name in self.cache:
            self.cache_hits += 1
            print(f"✅ Cache HIT! Serving ready-made {item_name}")
            print(f"   ⚡ Instant delivery - no waiting!")
            return {
                'item': item_name,
                'source': 'cache',
                'wait_time': 0,
                'freshly_made': False
            }
        
        # Step 2: Cache miss - need to cook (database query)
        self.cache_misses += 1
        print(f"❌ Cache MISS! Need to cook fresh {item_name}")
        
        if item_name not in self.database:
            print(f"   🚫 Sorry, we don't make {item_name}")
            return None
        
        # Step 3: Cook the item (simulate database query)
        cooking_info = self.database[item_name]
        cooking_time = cooking_info['cooking_time']
        self.total_cooking_time += cooking_time
        
        print(f"   👨‍🍳 Cooking {item_name}... (takes {cooking_time} minutes)")
        time.sleep(cooking_time * 0.1)  # Simulate cooking time (scaled down)
        
        # Step 4: Store in cache for future orders
        self.cache[item_name] = {
            'prepared_at': time.time(),
            'freshness_duration': 30  # Ready-made items stay fresh for 30 minutes
        }
        
        print(f"   📦 Stored extra {item_name} in ready-made counter for next customers")
        
        return {
            'item': item_name,
            'source': 'freshly_cooked',
            'wait_time': cooking_time,
            'freshly_made': True
        }
    
    def cache_cleanup(self):
        """Remove stale items from cache - like throwing away old vada pavs"""
        current_time = time.time()
        stale_items = []
        
        for item, cache_data in self.cache.items():
            item_age = current_time - cache_data['prepared_at']
            if item_age > cache_data['freshness_duration']:
                stale_items.append(item)
        
        for item in stale_items:
            del self.cache[item]
            print(f"🗑️ Removed stale {item} from cache")
    
    def get_stats(self):
        """Show performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate_percentage': round(hit_rate, 2),
            'total_cooking_time_saved': self.total_cooking_time,
            'current_cache_items': list(self.cache.keys())
        }

# Example: Mumbai street food stall during lunch rush
print("🏪 Mumbai Street Food Stall - Cache-Aside Pattern Demo\n")
print("=" * 60)

vadapav_stall = CacheAsidePattern()

# Simulate lunch rush orders
lunch_orders = [
    'vada_pav', 'vada_pav', 'pav_bhaji', 'vada_pav',  # Popular items
    'dosa', 'misal_pav', 'vada_pav', 'pav_bhaji',
    'dosa', 'vada_pav'  # Repeat orders
]

print("🍽️ LUNCH RUSH SIMULATION:")
print("-" * 30)

for order_num, item in enumerate(lunch_orders, 1):
    print(f"\nOrder #{order_num}:")
    result = vadapav_stall.get_food_item(item)
    if result:
        print(f"✅ Delivered {result['item']} in {result['wait_time']} minutes")
    print("-" * 30)
    
    # Periodic cache cleanup
    if order_num % 5 == 0:
        vadapav_stall.cache_cleanup()

# Final statistics
print("\n📊 FINAL PERFORMANCE STATS:")
stats = vadapav_stall.get_stats()
for key, value in stats.items():
    print(f"{key}: {value}")

print(f"\n💡 INSIGHTS:")
print(f"Cache hit rate: {stats['hit_rate_percentage']}% - Higher is better!")
print(f"Time saved by caching: {stats['total_cooking_time_saved']} minutes")
print(f"Customer satisfaction: {'🔥 Excellent' if stats['hit_rate_percentage'] > 60 else '👍 Good' if stats['hit_rate_percentage'] > 30 else '😐 Needs improvement'}")
```

### Write-Through vs Write-Behind - Dhaba vs Fast Food Strategy

```python
class WriteThroughCache:
    """
    Traditional dhaba strategy:
    - Every order written in register AND cooked immediately
    - Slower but everything consistent
    - Customer waits but gets exactly what they ordered
    """
    
    def __init__(self):
        self.cache = {}
        self.database = {}
        self.operations = []
    
    def write_data(self, key, value):
        print(f"📝 Write-Through: Storing {key} = {value}")
        
        # Write to cache first (fast memory)
        self.cache[key] = value
        print(f"   ✅ Saved to cache (ready counter)")
        
        # Write to database simultaneously (permanent storage)  
        time.sleep(0.2)  # Simulate database write delay
        self.database[key] = value
        print(f"   ✅ Saved to database (kitchen register)")
        
        self.operations.append(f"Write-Through: {key}")
        return "Success - data saved in both cache and database"

class WriteBehindCache:
    """
    Modern fast food strategy:
    - Take order, give receipt immediately (cache)
    - Cook and update kitchen records later (async database write)
    - Faster response but risk of inconsistency
    """
    
    def __init__(self):
        self.cache = {}
        self.database = {}
        self.pending_writes = []
        self.operations = []
        
        # Start background process to flush pending writes
        import threading
        self.background_writer = threading.Thread(target=self._background_flush, daemon=True)
        self.background_writer.start()
    
    def write_data(self, key, value):
        print(f"⚡ Write-Behind: Quick save {key} = {value}")
        
        # Write to cache immediately (instant receipt)
        self.cache[key] = value
        print(f"   ✅ Saved to cache (receipt given)")
        
        # Queue for background database write
        self.pending_writes.append({'key': key, 'value': value})
        print(f"   📋 Queued for database update (kitchen will get order soon)")
        
        self.operations.append(f"Write-Behind: {key}")
        return "Success - receipt ready, kitchen processing in background"
    
    def _background_flush(self):
        """Background process to write queued data to database"""
        while True:
            if self.pending_writes:
                # Process one pending write
                write_op = self.pending_writes.pop(0)
                
                print(f"   🔄 Background: Writing {write_op['key']} to database...")
                time.sleep(0.5)  # Simulate database write
                self.database[write_op['key']] = write_op['value']
                print(f"   ✅ Background: {write_op['key']} saved to database")
            
            time.sleep(1)  # Check for pending writes every second

# Comparison demo
print("🏪 WRITE STRATEGIES COMPARISON\n")
print("=" * 50)

print("🐌 TRADITIONAL DHABA (Write-Through):")
dhaba = WriteThroughCache()
start_time = time.time()

dhaba.write_data("order_1", "Butter Chicken + Naan")
dhaba.write_data("order_2", "Dal Tadka + Rice") 
dhaba.write_data("order_3", "Paneer Tikka + Roti")

dhaba_time = time.time() - start_time
print(f"⏱️ Total time: {dhaba_time:.2f} seconds")
print(f"✅ Guarantee: All orders in both receipt AND kitchen register")

print("\n" + "=" * 50)

print("⚡ MODERN FAST FOOD (Write-Behind):")
fast_food = WriteBehindCache()
start_time = time.time()

fast_food.write_data("order_1", "McChicken Burger")
fast_food.write_data("order_2", "Big Mac + Fries")
fast_food.write_data("order_3", "Chicken McNuggets")

fast_food_time = time.time() - start_time  
print(f"⏱️ Total time: {fast_food_time:.2f} seconds")
print(f"⚠️ Risk: Receipts ready immediately, but kitchen updates happening in background")

print(f"\n📊 PERFORMANCE COMPARISON:")
print(f"Speed improvement: {((dhaba_time - fast_food_time) / dhaba_time * 100):.1f}% faster")
print(f"Trade-off: Speed vs Consistency guarantee")
```

### Multi-Level Caching - Mumbai Food Delivery Chain

```python
class MultiLevelCache:
    """
    Mumbai food delivery hierarchy:
    L1 Cache = Delivery boy's bag (fastest, smallest)
    L2 Cache = Restaurant ready counter (fast, medium)  
    L3 Cache = Restaurant kitchen (slower, largest)
    Database = Wholesale market (slowest, unlimited)
    """
    
    def __init__(self):
        # L1 Cache - Delivery boy's bag (very fast, very small)
        self.l1_cache = {}
        self.l1_capacity = 3
        self.l1_access_time = 0.01  # 10ms
        
        # L2 Cache - Restaurant counter (fast, small)
        self.l2_cache = {}
        self.l2_capacity = 10  
        self.l2_access_time = 0.05  # 50ms
        
        # L3 Cache - Kitchen storage (medium, large)
        self.l3_cache = {}
        self.l3_capacity = 50
        self.l3_access_time = 0.2  # 200ms
        
        # Database - Wholesale market (slow, unlimited)
        self.database = {
            f"dish_{i}": f"Recipe for dish {i}" for i in range(1, 1001)
        }
        self.db_access_time = 1.0  # 1 second
        
        self.stats = {
            'l1_hits': 0, 'l2_hits': 0, 'l3_hits': 0, 'db_hits': 0,
            'total_requests': 0, 'total_time': 0
        }
    
    def get_item(self, item_key):
        """Get item using multi-level caching strategy"""
        self.stats['total_requests'] += 1
        start_time = time.time()
        
        print(f"🔍 Looking for: {item_key}")
        
        # Try L1 Cache first (delivery boy's bag)
        if item_key in self.l1_cache:
            time.sleep(self.l1_access_time)
            self.stats['l1_hits'] += 1
            elapsed = time.time() - start_time
            self.stats['total_time'] += elapsed
            print(f"✅ L1 HIT! Found in delivery boy's bag ({elapsed*1000:.1f}ms)")
            return self.l1_cache[item_key]
        
        # Try L2 Cache (restaurant counter)
        if item_key in self.l2_cache:
            time.sleep(self.l2_access_time)
            value = self.l2_cache[item_key]
            
            # Promote to L1 cache
            self._add_to_l1(item_key, value)
            
            self.stats['l2_hits'] += 1
            elapsed = time.time() - start_time
            self.stats['total_time'] += elapsed
            print(f"✅ L2 HIT! Found at restaurant counter ({elapsed*1000:.1f}ms)")
            print(f"   📤 Promoted to delivery bag for faster access")
            return value
        
        # Try L3 Cache (kitchen storage)
        if item_key in self.l3_cache:
            time.sleep(self.l3_access_time)
            value = self.l3_cache[item_key]
            
            # Promote to L2 and L1
            self._add_to_l2(item_key, value)
            self._add_to_l1(item_key, value)
            
            self.stats['l3_hits'] += 1
            elapsed = time.time() - start_time
            self.stats['total_time'] += elapsed
            print(f"✅ L3 HIT! Found in kitchen storage ({elapsed*1000:.1f}ms)")
            print(f"   📤 Promoted to counter and delivery bag")
            return value
        
        # Finally, check database (wholesale market)
        if item_key in self.database:
            time.sleep(self.db_access_time)
            value = self.database[item_key]
            
            # Store in all cache levels
            self._add_to_l3(item_key, value)
            self._add_to_l2(item_key, value)
            self._add_to_l1(item_key, value)
            
            self.stats['db_hits'] += 1
            elapsed = time.time() - start_time
            self.stats['total_time'] += elapsed
            print(f"✅ DATABASE HIT! Got from wholesale market ({elapsed*1000:.1f}ms)")
            print(f"   📤 Cached at all levels for future orders")
            return value
        
        print(f"❌ Item not found anywhere!")
        return None
    
    def _add_to_l1(self, key, value):
        """Add to L1 cache with LRU eviction"""
        if len(self.l1_cache) >= self.l1_capacity:
            # Remove least recently used
            oldest_key = next(iter(self.l1_cache))
            del self.l1_cache[oldest_key]
            print(f"   🗑️ Removed {oldest_key} from delivery bag (full)")
        
        self.l1_cache[key] = value
    
    def _add_to_l2(self, key, value):
        """Add to L2 cache with LRU eviction"""
        if len(self.l2_cache) >= self.l2_capacity:
            oldest_key = next(iter(self.l2_cache))
            del self.l2_cache[oldest_key]
            print(f"   🗑️ Removed {oldest_key} from restaurant counter (full)")
        
        self.l2_cache[key] = value
    
    def _add_to_l3(self, key, value):
        """Add to L3 cache with LRU eviction"""
        if len(self.l3_cache) >= self.l3_capacity:
            oldest_key = next(iter(self.l3_cache))
            del self.l3_cache[oldest_key]
            print(f"   🗑️ Removed {oldest_key} from kitchen storage (full)")
        
        self.l3_cache[key] = value
    
    def print_stats(self):
        """Show cache performance statistics"""
        total = self.stats['total_requests']
        if total == 0:
            return
        
        avg_time = self.stats['total_time'] / total
        
        print(f"\n📊 MULTI-LEVEL CACHE PERFORMANCE:")
        print(f"L1 Cache hits: {self.stats['l1_hits']}/{total} ({self.stats['l1_hits']/total*100:.1f}%) - Delivery bag")
        print(f"L2 Cache hits: {self.stats['l2_hits']}/{total} ({self.stats['l2_hits']/total*100:.1f}%) - Restaurant counter") 
        print(f"L3 Cache hits: {self.stats['l3_hits']}/{total} ({self.stats['l3_hits']/total*100:.1f}%) - Kitchen storage")
        print(f"Database hits: {self.stats['db_hits']}/{total} ({self.stats['db_hits']/total*100:.1f}%) - Wholesale market")
        print(f"Average response time: {avg_time*1000:.1f}ms")

# Demo: Mumbai food delivery with multi-level caching
print("🚚 MUMBAI FOOD DELIVERY - MULTI-LEVEL CACHING DEMO\n")
print("=" * 60)

swiggy_cache = MultiLevelCache()

# Simulate food delivery orders
orders = [
    "dish_42",  # First time - will go to database
    "dish_15",  # First time - database  
    "dish_42",  # Second time - should be in L1 cache
    "dish_7",   # New dish - database
    "dish_15",  # Should be in L1 cache
    "dish_100", # New dish - database (will push others out of L1)
    "dish_42",  # Might be pushed to L2 cache
    "dish_15"   # Popular dish - likely in L1 or L2
]

for order_num, dish in enumerate(orders, 1):
    print(f"\n🍽️ ORDER #{order_num}: {dish}")
    print("-" * 40)
    
    result = swiggy_cache.get_item(dish)
    if result:
        print(f"✅ Order fulfilled: {dish}")
    
    print("-" * 40)

swiggy_cache.print_stats()

print(f"\n💡 KEY INSIGHTS:")
print(f"✅ Multi-level caching provides excellent performance")
print(f"✅ Popular items get promoted to faster cache levels")  
print(f"✅ LRU eviction ensures most relevant items stay cached")
print(f"✅ Similar to Mumbai's food delivery optimization!")
```

---

## Chapter 4: Message Queues aur Async Processing - Mumbai Dabba System

Mumbai ke dabbawalas ka system dekha hai? 200,000 lunch boxes daily deliver karte hain with 99.999% accuracy! No computers, no GPS, no smartphones. Pure coordination aur systematic approach. Yahi inspiration hai message queue systems ke liye.

### Point-to-Point Queue - Direct Dabba Delivery

```python
import threading
import time
import queue
from dataclasses import dataclass
from typing import List
from enum import Enum

@dataclass
class DabbaOrder:
    """Represents a lunch box order like Mumbai dabbawalas"""
    order_id: str
    pickup_address: str
    delivery_address: str
    customer_name: str
    contents: str
    priority: str = "normal"  # normal, urgent (like extra tip for faster delivery)
    estimated_delivery_time: int = 60  # minutes
    
class OrderStatus(Enum):
    RECEIVED = "received"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit" 
    DELIVERED = "delivered"
    FAILED = "failed"

class DabbaPointToPointQueue:
    """
    Mumbai Dabbawala Point-to-Point system:
    - One order goes to exactly one delivery person
    - No sharing of orders between delivery persons
    - Guarantees exactly-once delivery (no duplicate lunches!)
    """
    
    def __init__(self, max_capacity=100):
        self.order_queue = queue.Queue(maxsize=max_capacity)
        self.processing_orders = {}  # Track orders being processed
        self.completed_orders = {}   # Track completed deliveries
        self.failed_orders = {}      # Track failed deliveries
        
        self.delivery_persons = []
        self.stats = {
            'total_orders': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'average_delivery_time': 0
        }
        
        # Start delivery person workers
        self._start_delivery_workers()
    
    def place_order(self, order: DabbaOrder):
        """Customer places lunch order - like calling dabbawala"""
        try:
            self.order_queue.put(order, timeout=5)  # 5 second timeout
            self.stats['total_orders'] += 1
            
            print(f"📞 Order placed: {order.order_id}")
            print(f"   🏠 Pickup: {order.pickup_address}")
            print(f"   🏢 Delivery: {order.delivery_address}")
            print(f"   🍛 Contents: {order.contents}")
            
            return {
                'status': 'accepted',
                'order_id': order.order_id,
                'estimated_delivery': f"{order.estimated_delivery_time} minutes",
                'queue_position': self.order_queue.qsize()
            }
            
        except queue.Full:
            print(f"❌ Order rejected: Queue full! (Too many orders)")
            return {
                'status': 'rejected',
                'reason': 'System overloaded, try after some time'
            }
    
    def _start_delivery_workers(self):
        """Start delivery person threads - like hiring dabbawalas"""
        delivery_areas = [
            "Andheri-Bandra Route",
            "Dadar-Lower Parel Route", 
            "Thane-Kurla Route",
            "Borivali-Malad Route"
        ]
        
        for area in delivery_areas:
            worker = threading.Thread(
                target=self._delivery_worker,
                args=(area,),
                daemon=True
            )
            worker.start()
            self.delivery_persons.append(area)
            
        print(f"👥 Started {len(delivery_areas)} delivery workers")
    
    def _delivery_worker(self, worker_name):
        """Individual delivery person working continuously"""
        while True:
            try:
                # Wait for new order
                order = self.order_queue.get(timeout=10)
                
                print(f"\n👤 {worker_name} picked up order: {order.order_id}")
                self.processing_orders[order.order_id] = {
                    'order': order,
                    'worker': worker_name,
                    'start_time': time.time(),
                    'status': OrderStatus.PICKED_UP
                }
                
                # Simulate pickup process
                print(f"   📦 Picking up from {order.pickup_address}...")
                time.sleep(random.uniform(2, 5))  # 2-5 second pickup time
                
                self.processing_orders[order.order_id]['status'] = OrderStatus.IN_TRANSIT
                print(f"   🚴‍♂️ In transit to {order.delivery_address}...")
                
                # Simulate delivery time (based on Mumbai traffic!)
                delivery_time = random.uniform(30, 90)  # 30-90 second simulation
                
                # Higher chance of delay during rush hours
                current_hour = time.localtime().tm_hour
                if 9 <= current_hour <= 11 or 13 <= current_hour <= 15:  # Rush hours
                    delivery_time *= random.uniform(1.2, 2.0)  # 20-100% delay
                    print(f"   🚦 Rush hour traffic - delivery delayed!")
                
                time.sleep(delivery_time * 0.01)  # Scale down for demo
                
                # 99.999% success rate like real dabbawalas!
                if random.random() < 0.99999:
                    self._complete_delivery(order, worker_name, delivery_time)
                else:
                    self._fail_delivery(order, worker_name, "Customer not found")
                
                # Mark task as done
                self.order_queue.task_done()
                
            except queue.Empty:
                # No orders to process - wait a bit
                time.sleep(1)
            except Exception as e:
                print(f"❌ {worker_name} error: {e}")
    
    def _complete_delivery(self, order, worker_name, delivery_time):
        """Successfully complete delivery"""
        completion_time = time.time()
        
        self.completed_orders[order.order_id] = {
            'order': order,
            'worker': worker_name,
            'delivery_time': delivery_time,
            'completed_at': completion_time
        }
        
        # Remove from processing
        if order.order_id in self.processing_orders:
            del self.processing_orders[order.order_id]
        
        self.stats['successful_deliveries'] += 1
        
        print(f"   ✅ Delivered successfully!")
        print(f"   ⏱️  Delivery time: {delivery_time:.1f} seconds")
        print(f"   📍 Delivered to: {order.delivery_address}")
    
    def _fail_delivery(self, order, worker_name, reason):
        """Handle delivery failure"""
        self.failed_orders[order.order_id] = {
            'order': order,
            'worker': worker_name,
            'reason': reason,
            'failed_at': time.time()
        }
        
        if order.order_id in self.processing_orders:
            del self.processing_orders[order.order_id]
        
        self.stats['failed_deliveries'] += 1
        
        print(f"   ❌ Delivery failed: {reason}")
        # In real system, would retry or refund
    
    def get_order_status(self, order_id):
        """Track order status - like calling dabbawala for updates"""
        if order_id in self.completed_orders:
            return {'status': 'delivered', 'details': self.completed_orders[order_id]}
        elif order_id in self.processing_orders:
            return {'status': 'in_transit', 'details': self.processing_orders[order_id]}
        elif order_id in self.failed_orders:
            return {'status': 'failed', 'details': self.failed_orders[order_id]}
        else:
            return {'status': 'not_found'}
    
    def get_system_stats(self):
        """Get overall system performance"""
        success_rate = 0
        if self.stats['total_orders'] > 0:
            success_rate = (self.stats['successful_deliveries'] / self.stats['total_orders']) * 100
        
        return {
            'total_orders': self.stats['total_orders'],
            'successful_deliveries': self.stats['successful_deliveries'],
            'failed_deliveries': self.stats['failed_deliveries'],
            'success_rate_percentage': round(success_rate, 3),
            'active_delivery_workers': len(self.delivery_persons),
            'orders_in_queue': self.order_queue.qsize(),
            'orders_being_processed': len(self.processing_orders)
        }

# Example: Mumbai lunch delivery during peak hours
print("🍱 MUMBAI DABBA DELIVERY SYSTEM - POINT-TO-POINT QUEUE\n")
print("=" * 60)

import random
random.seed(42)  # For consistent demo results

# Create delivery system
mumbai_dabbawala = DabbaPointToPointQueue()

# Wait for workers to start
time.sleep(1)

# Simulate lunch orders during peak time (12 PM - 1 PM)
sample_orders = [
    DabbaOrder("ORD001", "Andheri East Home", "BKC Office", "Rajesh Sharma", "Dal Chawal + Sabzi"),
    DabbaOrder("ORD002", "Bandra West Home", "Nariman Point", "Priya Patel", "Roti + Paneer + Rice"),
    DabbaOrder("ORD003", "Thane Home", "Powai Office", "Amit Kumar", "Biryani + Raita"),
    DabbaOrder("ORD004", "Borivali Home", "Andheri Office", "Sneha Desai", "Gujarati Thali"),
    DabbaOrder("ORD005", "Dadar Home", "Fort Office", "Rohit Singh", "Punjabi Meal")
]

print("📞 PLACING LUNCH ORDERS:")
print("-" * 30)

for order in sample_orders:
    result = mumbai_dabbawala.place_order(order)
    print(f"Status: {result['status']}")
    if result['status'] == 'accepted':
        print(f"Queue position: {result['queue_position']}")
    print()

print("🚴‍♂️ DELIVERY IN PROGRESS...")
print("-" * 30)

# Let the system process orders
time.sleep(15)  # Wait for deliveries to complete

print("\n📊 DELIVERY SYSTEM STATISTICS:")
stats = mumbai_dabbawala.get_system_stats()
for key, value in stats.items():
    print(f"{key}: {value}")

print(f"\n🏆 SUCCESS RATE: {stats['success_rate_percentage']}%")
print(f"💡 Real Mumbai dabbawalas achieve 99.999% success rate!")
print(f"🎯 Our system achieved: {stats['success_rate_percentage']}%")
```

### Publish-Subscribe Pattern - Mumbai News Distribution

```python
import threading
import time
from typing import List, Dict, Callable
from dataclasses import dataclass
from enum import Enum

class NewsCategory(Enum):
    LOCAL_TRAIN = "local_train"
    TRAFFIC = "traffic"
    WEATHER = "weather"
    CRICKET = "cricket"
    BOLLYWOOD = "bollywood"
    BUSINESS = "business"

@dataclass
class NewsUpdate:
    """News update - like Mumbai street announcements"""
    news_id: str
    category: NewsCategory
    title: str
    content: str
    priority: int = 1  # 1=low, 5=critical
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class MumbaiNewsPubSub:
    """
    Mumbai street news distribution system:
    - Publishers: Traffic police, railway announcements, weather dept
    - Subscribers: Radio stations, mobile apps, newspapers, citizens
    - Topics: Train delays, traffic jams, weather alerts, cricket scores
    """
    
    def __init__(self):
        self.topics = {}  # topic -> list of subscribers
        self.message_history = {}  # topic -> list of recent messages
        self.subscriber_stats = {}  # subscriber -> stats
        self.publisher_stats = {}  # publisher -> stats
        self._lock = threading.Lock()
    
    def create_topic(self, topic: NewsCategory):
        """Create new news topic - like starting new announcement channel"""
        with self._lock:
            if topic not in self.topics:
                self.topics[topic] = []
                self.message_history[topic] = []
                print(f"📻 Created news topic: {topic.value}")
                return True
            return False
    
    def subscribe(self, topic: NewsCategory, subscriber_name: str, callback: Callable):
        """Subscribe to news updates - like tuning into radio station"""
        with self._lock:
            if topic not in self.topics:
                self.create_topic(topic)
            
            subscriber_info = {
                'name': subscriber_name,
                'callback': callback,
                'subscribed_at': time.time(),
                'messages_received': 0
            }
            
            self.topics[topic].append(subscriber_info)
            self.subscriber_stats[subscriber_name] = {
                'topics': [topic],
                'total_messages': 0,
                'subscription_time': time.time()
            }
            
            print(f"👂 {subscriber_name} subscribed to {topic.value}")
            
            # Send recent messages to new subscriber
            recent_messages = self.message_history[topic][-5:]  # Last 5 messages
            if recent_messages:
                print(f"   📰 Sending {len(recent_messages)} recent updates...")
                for msg in recent_messages:
                    callback(msg)
    
    def unsubscribe(self, topic: NewsCategory, subscriber_name: str):
        """Unsubscribe from news updates"""
        with self._lock:
            if topic in self.topics:
                self.topics[topic] = [
                    sub for sub in self.topics[topic] 
                    if sub['name'] != subscriber_name
                ]
                print(f"👋 {subscriber_name} unsubscribed from {topic.value}")
    
    def publish(self, topic: NewsCategory, news: NewsUpdate, publisher_name: str):
        """Publish news update - like making street announcement"""
        with self._lock:
            if topic not in self.topics:
                self.create_topic(topic)
            
            # Add to message history
            self.message_history[topic].append(news)
            
            # Keep only last 50 messages per topic
            if len(self.message_history[topic]) > 50:
                self.message_history[topic] = self.message_history[topic][-50:]
            
            # Update publisher stats
            if publisher_name not in self.publisher_stats:
                self.publisher_stats[publisher_name] = {
                    'messages_published': 0,
                    'topics_published': set()
                }
            
            self.publisher_stats[publisher_name]['messages_published'] += 1
            self.publisher_stats[publisher_name]['topics_published'].add(topic)
            
            print(f"📢 {publisher_name} published: {news.title}")
            
            # Notify all subscribers
            subscribers = self.topics[topic].copy()  # Copy to avoid race conditions
            
        # Notify subscribers outside the lock to prevent blocking
        for subscriber in subscribers:
            try:
                subscriber['callback'](news)
                subscriber['messages_received'] += 1
                
                if subscriber['name'] in self.subscriber_stats:
                    self.subscriber_stats[subscriber['name']]['total_messages'] += 1
                    
            except Exception as e:
                print(f"❌ Failed to notify {subscriber['name']}: {e}")
    
    def get_topic_stats(self, topic: NewsCategory):
        """Get statistics for a specific topic"""
        with self._lock:
            if topic not in self.topics:
                return None
            
            return {
                'topic': topic.value,
                'subscriber_count': len(self.topics[topic]),
                'message_count': len(self.message_history[topic]),
                'subscribers': [sub['name'] for sub in self.topics[topic]]
            }
    
    def get_system_stats(self):
        """Get overall system statistics"""
        with self._lock:
            total_topics = len(self.topics)
            total_subscribers = sum(len(subs) for subs in self.topics.values())
            total_messages = sum(len(history) for history in self.message_history.values())
            
            return {
                'total_topics': total_topics,
                'total_subscribers': total_subscribers,
                'total_messages_published': total_messages,
                'active_publishers': len(self.publisher_stats),
                'topics': list(topic.value for topic in self.topics.keys())
            }

# Subscriber callback functions (different apps/services)
def radio_fm_callback(news: NewsUpdate):
    """Radio FM station - announces important news"""
    if news.priority >= 3:  # Only high priority news
        print(f"📻 [Radio FM] BREAKING: {news.title}")

def mobile_app_callback(news: NewsUpdate):
    """Mobile app - shows all news with push notifications"""
    priority_icon = "🚨" if news.priority >= 4 else "📱"
    print(f"{priority_icon} [Mobile App] {news.title}")

def newspaper_callback(news: NewsUpdate):
    """Newspaper - collects news for next day's print"""
    print(f"📰 [Newspaper] Filed: {news.title} (for tomorrow's edition)")

def traffic_app_callback(news: NewsUpdate):
    """Traffic app - only cares about traffic and train updates"""
    if news.category in [NewsCategory.TRAFFIC, NewsCategory.LOCAL_TRAIN]:
        print(f"🚦 [Traffic App] ALERT: {news.title}")

def cricket_fan_callback(news: NewsUpdate):
    """Cricket fan - only wants cricket updates"""
    if news.category == NewsCategory.CRICKET:
        print(f"🏏 [Cricket Fan] SCORE UPDATE: {news.title}")

# Example: Mumbai news distribution system
print("📰 MUMBAI NEWS DISTRIBUTION - PUBLISH-SUBSCRIBE SYSTEM\n")
print("=" * 60)

# Create news distribution system
mumbai_news = MumbaiNewsPubSub()

# Create subscribers (various apps and services)
print("👥 SETTING UP SUBSCRIBERS:")
print("-" * 30)

mumbai_news.subscribe(NewsCategory.LOCAL_TRAIN, "Radio FM", radio_fm_callback)
mumbai_news.subscribe(NewsCategory.TRAFFIC, "Radio FM", radio_fm_callback)

mumbai_news.subscribe(NewsCategory.LOCAL_TRAIN, "Mobile App", mobile_app_callback)
mumbai_news.subscribe(NewsCategory.TRAFFIC, "Mobile App", mobile_app_callback)
mumbai_news.subscribe(NewsCategory.WEATHER, "Mobile App", mobile_app_callback)
mumbai_news.subscribe(NewsCategory.CRICKET, "Mobile App", mobile_app_callback)

mumbai_news.subscribe(NewsCategory.BUSINESS, "Newspaper", newspaper_callback)
mumbai_news.subscribe(NewsCategory.BOLLYWOOD, "Newspaper", newspaper_callback)

mumbai_news.subscribe(NewsCategory.TRAFFIC, "Traffic App", traffic_app_callback)
mumbai_news.subscribe(NewsCategory.LOCAL_TRAIN, "Traffic App", traffic_app_callback)

mumbai_news.subscribe(NewsCategory.CRICKET, "Cricket Fan", cricket_fan_callback)

print("\n📢 PUBLISHING NEWS UPDATES:")
print("-" * 30)

# Simulate news updates from different sources
news_updates = [
    (NewsCategory.LOCAL_TRAIN, 
     NewsUpdate("N001", NewsCategory.LOCAL_TRAIN, "Western Line Delayed by 15 mins", 
                "Due to signal failure at Andheri station", priority=4),
     "Railway Authority"),
    
    (NewsCategory.TRAFFIC,
     NewsUpdate("N002", NewsCategory.TRAFFIC, "Heavy Traffic on Eastern Express Highway",
                "Accident near Chembur, expect 30min delay", priority=3),
     "Traffic Police"),
    
    (NewsCategory.WEATHER,
     NewsUpdate("N003", NewsCategory.WEATHER, "Heavy Rain Alert for Mumbai",
                "IMD predicts 100mm rain in next 3 hours", priority=5),
     "Weather Department"),
    
    (NewsCategory.CRICKET,
     NewsUpdate("N004", NewsCategory.CRICKET, "India beats Australia by 6 wickets",
                "Kohli scores magnificent century", priority=2),
     "Sports Network"),
    
    (NewsCategory.LOCAL_TRAIN,
     NewsUpdate("N005", NewsCategory.LOCAL_TRAIN, "All Train Services Restored",
                "Signal issue at Andheri resolved", priority=3),
     "Railway Authority"),
     
    (NewsCategory.BOLLYWOOD,
     NewsUpdate("N006", NewsCategory.BOLLYWOOD, "Shahrukh Khan announces new movie",
                "Collaboration with Rajkumar Hirani", priority=1),
     "Entertainment News")
]

for topic, news, publisher in news_updates:
    mumbai_news.publish(topic, news, publisher)
    print()
    time.sleep(0.5)  # Small delay between news updates

print("\n📊 SYSTEM STATISTICS:")
stats = mumbai_news.get_system_stats()
for key, value in stats.items():
    print(f"{key}: {value}")

print("\n🎯 TOPIC-WISE BREAKDOWN:")
for topic in [NewsCategory.LOCAL_TRAIN, NewsCategory.TRAFFIC, NewsCategory.CRICKET]:
    topic_stats = mumbai_news.get_topic_stats(topic)
    if topic_stats:
        print(f"{topic_stats['topic']}: {topic_stats['subscriber_count']} subscribers, {topic_stats['message_count']} messages")
```

---

## Chapter 5: Real System Walkthroughs - Indian Scale Designs

### WhatsApp for India - 500M Users ka Architecture

WhatsApp India mein 500 million users hain - yani har 3rd Indian WhatsApp use karta hai! Iska architecture design karna Mumbai local train system design karne jaisa hai. Let's walk through it:

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
import hashlib
import json
import time

@dataclass
class WhatsAppMessage:
    message_id: str
    sender_id: str
    recipient_id: str
    content: str
    message_type: str  # text, image, voice, video
    timestamp: float
    is_group_message: bool = False
    group_id: Optional[str] = None
    encryption_key: Optional[str] = None

class WhatsAppIndiaArchitecture:
    """
    WhatsApp India Architecture Design:
    - 500M users, 100B+ messages per day
    - Multi-region deployment for Indian diversity
    - Optimized for 2G/3G networks
    - 22 Indian languages support
    """
    
    def __init__(self):
        # Regional data centers - like Mumbai local train zones
        self.data_centers = {
            'mumbai': {
                'region': 'Western India',
                'users_capacity': 150_000_000,  # 150M users
                'languages': ['hindi', 'marathi', 'gujarati'],
                'network_optimization': '2G_optimized'
            },
            'bangalore': {
                'region': 'Southern India',
                'users_capacity': 120_000_000,  # 120M users
                'languages': ['kannada', 'tamil', 'telugu'],
                'network_optimization': '4G_optimized'
            },
            'delhi': {
                'region': 'Northern India', 
                'users_capacity': 180_000_000,  # 180M users
                'languages': ['hindi', 'punjabi', 'urdu'],
                'network_optimization': '3G_optimized'
            },
            'hyderabad': {
                'region': 'Backup & DR',
                'users_capacity': 50_000_000,   # 50M backup capacity
                'languages': ['telugu', 'hindi'],
                'network_optimization': 'all_networks'
            }
        }
        
        # Message routing and storage
        self.message_routing = MessageRoutingService()
        self.user_sessions = {}  # Active user sessions
        self.message_stats = {
            'total_messages': 0,
            'messages_per_second': 0,
            'peak_messages_per_second': 0
        }
    
    def get_user_datacenter(self, user_id: str) -> str:
        """Route user to nearest data center - like choosing train line"""
        # Use consistent hashing based on user ID
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        
        # Route based on hash to ensure consistent routing
        if hash_value % 4 == 0:
            return 'mumbai'
        elif hash_value % 4 == 1:
            return 'bangalore'
        elif hash_value % 4 == 2:
            return 'delhi'
        else:
            return 'hyderabad'
    
    def send_message(self, message: WhatsAppMessage) -> Dict:
        """Send WhatsApp message with Indian optimizations"""
        
        # Step 1: Route sender and recipient to data centers
        sender_dc = self.get_user_datacenter(message.sender_id)
        recipient_dc = self.get_user_datacenter(message.recipient_id)
        
        print(f"📱 Message routing:")
        print(f"   Sender {message.sender_id} → {sender_dc} DC")
        print(f"   Recipient {message.recipient_id} → {recipient_dc} DC")
        
        # Step 2: Network optimization for Indian conditions
        optimized_message = self.optimize_for_indian_networks(message, sender_dc)
        
        # Step 3: Multi-language support
        if self.requires_language_processing(optimized_message):
            optimized_message = self.process_indian_language(optimized_message)
        
        # Step 4: End-to-end encryption
        encrypted_message = self.encrypt_message(optimized_message)
        
        # Step 5: Store message for sender (write to sender's DC)
        self.store_message(encrypted_message, sender_dc, "outgoing")
        
        # Step 6: Deliver to recipient
        delivery_result = self.deliver_message(encrypted_message, recipient_dc)
        
        # Step 7: Update statistics
        self.update_message_stats()
        
        return {
            'message_id': message.message_id,
            'status': delivery_result['status'],
            'sender_dc': sender_dc,
            'recipient_dc': recipient_dc,
            'delivery_time_ms': delivery_result['delivery_time_ms'],
            'network_optimization': optimized_message.get('optimization_applied', 'none')
        }
    
    def optimize_for_indian_networks(self, message: WhatsAppMessage, dc: str) -> Dict:
        """Optimize message for Indian network conditions"""
        dc_info = self.data_centers[dc]
        network_type = dc_info['network_optimization']
        
        optimization = {
            'original_message': message,
            'optimization_applied': network_type
        }
        
        if '2G_optimized' in network_type:
            # Aggressive compression for 2G networks
            optimization.update({
                'compression_level': 'maximum',
                'image_quality': 'low',  # Reduce image quality
                'video_disabled': True,  # Disable video on 2G
                'voice_compression': 'high'
            })
            print(f"   🐌 2G optimization applied: Max compression, low quality media")
            
        elif '3G_optimized' in network_type:
            # Moderate optimization for 3G
            optimization.update({
                'compression_level': 'medium',
                'image_quality': 'medium',
                'video_quality': 'low',
                'voice_compression': 'medium'
            })
            print(f"   📶 3G optimization applied: Medium compression")
            
        else:  # 4G_optimized
            # Minimal optimization for 4G
            optimization.update({
                'compression_level': 'low',
                'image_quality': 'high',
                'video_quality': 'medium',
                'voice_compression': 'low'
            })
            print(f"   🚀 4G optimization applied: High quality, minimal compression")
        
        return optimization
    
    def requires_language_processing(self, message_data: Dict) -> bool:
        """Check if message needs Indian language processing"""
        message = message_data['original_message']
        
        # Simple detection - check for non-ASCII characters (Devanagari, etc.)
        text = message.content
        has_indian_script = any(ord(char) > 127 for char in text)
        
        return has_indian_script
    
    def process_indian_language(self, message_data: Dict) -> Dict:
        """Process Indian language text for better delivery"""
        message = message_data['original_message']
        
        # Simulated language processing
        language_features = {
            'detected_language': 'hindi',  # Simplified detection
            'transliteration_applied': True,
            'unicode_normalization': True,
            'font_embedding': 'devanagari'
        }
        
        message_data['language_processing'] = language_features
        print(f"   🌐 Language processing: Hindi script detected")
        
        return message_data
    
    def encrypt_message(self, message_data: Dict) -> Dict:
        """Apply end-to-end encryption"""
        message = message_data['original_message']
        
        # Generate encryption key (simplified)
        encryption_key = hashlib.sha256(
            f"{message.sender_id}{message.recipient_id}{message.timestamp}".encode()
        ).hexdigest()[:32]
        
        message_data['encryption'] = {
            'algorithm': 'Signal_Protocol',
            'key_id': encryption_key[:8],  # First 8 chars as key ID
            'encrypted': True
        }
        
        print(f"   🔐 End-to-end encryption applied: {message_data['encryption']['key_id']}")
        
        return message_data
    
    def store_message(self, encrypted_message: Dict, dc: str, direction: str):
        """Store message in appropriate data center"""
        message = encrypted_message['original_message']
        
        # Storage strategy
        storage_info = {
            'dc': dc,
            'table': f"messages_{direction}_{dc}",
            'partition_key': f"user_{message.sender_id}",
            'sort_key': f"timestamp_{message.timestamp}"
        }
        
        print(f"   💾 Stored in {dc} DC: {storage_info['table']}")
        
        return storage_info
    
    def deliver_message(self, encrypted_message: Dict, recipient_dc: str) -> Dict:
        """Deliver message to recipient"""
        message = encrypted_message['original_message']
        
        # Simulate delivery time based on cross-DC communication
        if recipient_dc == 'mumbai':
            base_latency = 50   # ms
        elif recipient_dc == 'bangalore':
            base_latency = 80   # ms
        elif recipient_dc == 'delhi':
            base_latency = 60   # ms
        else:
            base_latency = 100  # ms for backup DC
        
        # Add network optimization impact
        if encrypted_message.get('optimization_applied') == '2G_optimized':
            base_latency *= 2.5  # 2G is slow
        elif encrypted_message.get('optimization_applied') == '3G_optimized':
            base_latency *= 1.5  # 3G is moderate
        
        delivery_time = base_latency + (time.time() % 50)  # Add some randomness
        
        print(f"   📨 Delivered to {recipient_dc} DC in {delivery_time:.1f}ms")
        
        return {
            'status': 'delivered',
            'delivery_time_ms': round(delivery_time, 1),
            'recipient_dc': recipient_dc
        }
    
    def update_message_stats(self):
        """Update system statistics"""
        self.message_stats['total_messages'] += 1
        
        # Calculate messages per second (simplified)
        current_time = time.time()
        if not hasattr(self, 'last_stats_update'):
            self.last_stats_update = current_time
            self.messages_in_current_second = 1
        else:
            if current_time - self.last_stats_update >= 1:
                # New second
                self.message_stats['messages_per_second'] = self.messages_in_current_second
                if self.messages_in_current_second > self.message_stats['peak_messages_per_second']:
                    self.message_stats['peak_messages_per_second'] = self.messages_in_current_second
                
                self.last_stats_update = current_time
                self.messages_in_current_second = 1
            else:
                self.messages_in_current_second += 1
    
    def get_system_stats(self):
        """Get WhatsApp India system statistics"""
        total_capacity = sum(dc['users_capacity'] for dc in self.data_centers.values())
        
        return {
            'total_user_capacity': total_capacity,
            'data_centers': len(self.data_centers),
            'supported_languages': 22,  # Approximate
            'total_messages_processed': self.message_stats['total_messages'],
            'current_messages_per_second': self.message_stats['messages_per_second'],
            'peak_messages_per_second': self.message_stats['peak_messages_per_second'],
            'network_optimizations': ['2G', '3G', '4G', '5G'],
            'encryption': 'End-to-end Signal Protocol'
        }

class MessageRoutingService:
    """Handle message routing across DCs"""
    def __init__(self):
        pass

# Example: WhatsApp India message delivery simulation
print("💬 WHATSAPP INDIA ARCHITECTURE - MESSAGE DELIVERY SIMULATION\n")
print("=" * 70)

# Create WhatsApp India system
whatsapp_india = WhatsAppIndiaArchitecture()

# Simulate typical Indian WhatsApp conversations
print("📱 SIMULATING TYPICAL INDIAN WHATSAPP USAGE:")
print("-" * 50)

# Family group chat during festival
family_messages = [
    WhatsAppMessage("msg_001", "user_mumbai_123", "group_family", 
                    "Happy Diwali everyone! 🪔✨", "text", time.time()),
    WhatsAppMessage("msg_002", "user_delhi_456", "group_family",
                    "आपको भी दीपावली की हार्दिक शुभकामनाएं! 🎆", "text", time.time()),
    WhatsAppMessage("msg_003", "user_bangalore_789", "group_family",
                    "Voice message with Diwali wishes", "voice", time.time())
]

for msg in family_messages:
    print(f"\n📧 Family Group Message: {msg.content[:50]}...")
    result = whatsapp_india.send_message(msg)
    print(f"✅ Status: {result['status']} in {result['delivery_time_ms']}ms")
    print(f"   Route: {result['sender_dc']} → {result['recipient_dc']}")

# Business communication
print(f"\n" + "="*50)
print("💼 BUSINESS COMMUNICATION:")

business_msg = WhatsAppMessage("msg_004", "user_mumbai_business", "user_delhi_client",
                              "Meeting confirmed for tomorrow 2 PM", "text", time.time())

print(f"\n💼 Business Message: {business_msg.content}")
result = whatsapp_india.send_message(business_msg)
print(f"✅ Status: {result['status']} in {result['delivery_time_ms']}ms")

print(f"\n📊 WHATSAPP INDIA SYSTEM STATISTICS:")
stats = whatsapp_india.get_system_stats()
for key, value in stats.items():
    print(f"{key}: {value}")

print(f"\n🇮🇳 INDIA-SPECIFIC OPTIMIZATIONS:")
print(f"✅ Multi-language support for 22 Indian languages")
print(f"✅ Network optimization for 2G/3G networks")  
print(f"✅ Regional data centers for low latency")
print(f"✅ Aggressive compression for data cost savings")
print(f"✅ End-to-end encryption for privacy")
```

### UPI Payment System - 10 Billion Transactions ka Backend

UPI (Unified Payments Interface) India ka digital payment revolution hai! Monthly 10 billion+ transactions process karta hai. Iska architecture design karna RBI ke saath coordination jaisa hai:

```python
import uuid
import time
import threading
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
import hashlib

class TransactionStatus(Enum):
    INITIATED = "initiated"
    BANK_PROCESSING = "bank_processing"  
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class UPITransaction:
    transaction_id: str
    sender_vpa: str      # Virtual Payment Address (like user@paytm)
    recipient_vpa: str
    amount: float
    currency: str = "INR"
    purpose: str = "personal"
    timestamp: float = None
    reference_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class UPISystemArchitecture:
    """
    UPI System Architecture - India's Digital Payment Backbone
    
    Components:
    - NPCI Switch: Central clearing house
    - PSPs: Payment Service Providers (PhonePe, GooglePay, Paytm)
    - Banks: Core banking systems
    - Mobile Apps: User interfaces
    
    Scale: 10B+ transactions/month, ₹50 lakh crore annual value
    """
    
    def __init__(self):
        # NPCI Central Switch - like Mumbai Central Station
        self.npci_switch = NPCISwitch()
        
        # Payment Service Providers
        self.psps = {
            'phonepe': {
                'name': 'PhonePe',
                'bank_partner': 'Yes Bank',
                'users': 450_000_000,
                'market_share': 0.47,  # 47% market share
                'processing_capacity': 50000  # TPS
            },
            'googlepay': {
                'name': 'Google Pay',
                'bank_partner': 'ICICI Bank', 
                'users': 350_000_000,
                'market_share': 0.36,
                'processing_capacity': 40000
            },
            'paytm': {
                'name': 'Paytm',
                'bank_partner': 'Paytm Payments Bank',
                'users': 350_000_000,
                'market_share': 0.15,
                'processing_capacity': 30000
            },
            'other': {
                'name': 'Other PSPs',
                'bank_partner': 'Various',
                'users': 50_000_000,
                'market_share': 0.02,
                'processing_capacity': 10000
            }
        }
        
        # Banks participating in UPI
        self.banks = {
            'sbi': {
                'name': 'State Bank of India',
                'customers': 450_000_000,
                'upi_enabled': True,
                'processing_capacity': 100000,  # TPS
                'uptime_sla': 0.9995  # 99.95%
            },
            'hdfc': {
                'name': 'HDFC Bank',
                'customers': 68_000_000,
                'upi_enabled': True,
                'processing_capacity': 80000,
                'uptime_sla': 0.9999
            },
            'icici': {
                'name': 'ICICI Bank',
                'customers': 63_000_000,
                'upi_enabled': True,
                'processing_capacity': 75000,
                'uptime_sla': 0.9998
            }
        }
        
        # Transaction statistics
        self.transaction_stats = {
            'total_transactions': 0,
            'successful_transactions': 0,
            'failed_transactions': 0,
            'total_value_inr': 0.0,
            'avg_transaction_value': 0.0,
            'peak_tps': 0,
            'current_tps': 0
        }
        
        # Active transactions
        self.active_transactions = {}
        self._transaction_lock = threading.Lock()
    
    def initiate_payment(self, transaction: UPITransaction) -> Dict:
        """Initiate UPI payment - like sending payment instruction"""
        
        print(f"💰 UPI Payment Initiated:")
        print(f"   From: {transaction.sender_vpa}")
        print(f"   To: {transaction.recipient_vpa}")
        print(f"   Amount: ₹{transaction.amount:,.2f}")
        print(f"   Purpose: {transaction.purpose}")
        
        # Step 1: Validate VPAs and get PSP routing
        sender_routing = self.get_vpa_routing(transaction.sender_vpa)
        recipient_routing = self.get_vpa_routing(transaction.recipient_vpa)
        
        if not sender_routing or not recipient_routing:
            return self._create_response("failed", "Invalid VPA", transaction)
        
        print(f"   🏦 Sender PSP: {sender_routing['psp_name']}")
        print(f"   🏦 Recipient PSP: {recipient_routing['psp_name']}")
        
        # Step 2: Route through NPCI Switch
        with self._transaction_lock:
            self.active_transactions[transaction.transaction_id] = {
                'transaction': transaction,
                'status': TransactionStatus.INITIATED,
                'sender_routing': sender_routing,
                'recipient_routing': recipient_routing,
                'start_time': time.time()
            }
        
        # Step 3: Process through NPCI
        npci_result = self.npci_switch.process_transaction(
            transaction, sender_routing, recipient_routing
        )
        
        # Step 4: Update transaction status
        with self._transaction_lock:
            if transaction.transaction_id in self.active_transactions:
                self.active_transactions[transaction.transaction_id]['status'] = npci_result['status']
                self.active_transactions[transaction.transaction_id]['npci_response'] = npci_result
        
        # Step 5: Update statistics
        self._update_transaction_stats(transaction, npci_result['status'])
        
        return self._create_response(
            npci_result['status'], 
            npci_result['message'],
            transaction,
            {
                'processing_time_ms': npci_result['processing_time_ms'],
                'reference_number': npci_result.get('reference_number'),
                'sender_psp': sender_routing['psp_name'],
                'recipient_psp': recipient_routing['psp_name']
            }
        )
    
    def get_vpa_routing(self, vpa: str) -> Optional[Dict]:
        """Get PSP routing information from VPA"""
        # VPA format: user@psp (like user@paytm, user@phonepe)
        if '@' not in vpa:
            return None
        
        username, psp_handle = vpa.split('@')
        
        # Map PSP handles to our PSP database
        psp_mapping = {
            'phonepe': 'phonepe',
            'paytm': 'paytm', 
            'googlepay': 'googlepay',
            'gpay': 'googlepay',
            'ibl': 'other',  # IDFC First Bank
            'oksbi': 'other',  # SBI
            'okhdfcbank': 'other'  # HDFC
        }
        
        psp_key = psp_mapping.get(psp_handle.lower())
        if not psp_key:
            return None
        
        psp_info = self.psps[psp_key]
        return {
            'psp_key': psp_key,
            'psp_name': psp_info['name'],
            'bank_partner': psp_info['bank_partner'],
            'username': username
        }
    
    def _create_response(self, status: str, message: str, transaction: UPITransaction, extra_data: Dict = None) -> Dict:
        """Create standardized response"""
        response = {
            'transaction_id': transaction.transaction_id,
            'status': status,
            'message': message,
            'amount': transaction.amount,
            'timestamp': datetime.fromtimestamp(transaction.timestamp).isoformat()
        }
        
        if extra_data:
            response.update(extra_data)
        
        return response
    
    def _update_transaction_stats(self, transaction: UPITransaction, status: str):
        """Update system statistics"""
        self.transaction_stats['total_transactions'] += 1
        self.transaction_stats['total_value_inr'] += transaction.amount
        
        if status == 'success':
            self.transaction_stats['successful_transactions'] += 1
        else:
            self.transaction_stats['failed_transactions'] += 1
        
        # Update average transaction value
        self.transaction_stats['avg_transaction_value'] = (
            self.transaction_stats['total_value_inr'] / 
            self.transaction_stats['total_transactions']
        )
    
    def get_transaction_status(self, transaction_id: str) -> Optional[Dict]:
        """Check transaction status"""
        with self._transaction_lock:
            if transaction_id in self.active_transactions:
                tx_data = self.active_transactions[transaction_id]
                return {
                    'transaction_id': transaction_id,
                    'status': tx_data['status'].value,
                    'amount': tx_data['transaction'].amount,
                    'sender_vpa': tx_data['transaction'].sender_vpa,
                    'recipient_vpa': tx_data['transaction'].recipient_vpa,
                    'processing_time': time.time() - tx_data['start_time']
                }
        return None
    
    def get_system_stats(self) -> Dict:
        """Get UPI system statistics"""
        success_rate = 0
        if self.transaction_stats['total_transactions'] > 0:
            success_rate = (
                self.transaction_stats['successful_transactions'] / 
                self.transaction_stats['total_transactions'] * 100
            )
        
        return {
            'total_transactions': self.transaction_stats['total_transactions'],
            'successful_transactions': self.transaction_stats['successful_transactions'],
            'failed_transactions': self.transaction_stats['failed_transactions'],
            'success_rate_percentage': round(success_rate, 2),
            'total_value_processed_inr': self.transaction_stats['total_value_inr'],
            'average_transaction_value_inr': round(self.transaction_stats['avg_transaction_value'], 2),
            'active_psps': len(self.psps),
            'participating_banks': len(self.banks),
            'active_transactions': len(self.active_transactions)
        }

class NPCISwitch:
    """
    National Payments Corporation of India Switch
    Central clearing house for all UPI transactions
    """
    
    def __init__(self):
        self.processing_capacity = 100000  # 100K TPS theoretical max
        self.current_load = 0
        self.fraud_detection = FraudDetectionSystem()
    
    def process_transaction(self, transaction: UPITransaction, sender_routing: Dict, recipient_routing: Dict) -> Dict:
        """Process transaction through NPCI switch"""
        
        start_time = time.time()
        
        print(f"   🏛️  NPCI: Processing transaction {transaction.transaction_id}")
        
        # Step 1: Load balancing and capacity check
        if self.current_load >= self.processing_capacity * 0.9:  # 90% capacity
            return {
                'status': 'failed',
                'message': 'System overloaded, please try again',
                'processing_time_ms': (time.time() - start_time) * 1000
            }
        
        # Step 2: Fraud detection
        fraud_score = self.fraud_detection.check_transaction(transaction)
        if fraud_score > 0.8:  # High fraud probability
            print(f"   🚨 Fraud detected: Score {fraud_score}")
            return {
                'status': 'failed',
                'message': 'Transaction blocked for security reasons',
                'processing_time_ms': (time.time() - start_time) * 1000
            }
        
        # Step 3: Simulate bank processing time
        # Higher amounts take longer due to additional checks
        processing_delay = 0.5  # Base 500ms
        if transaction.amount > 50000:  # ₹50,000+
            processing_delay += 1.0  # Additional 1 second
        if transaction.amount > 200000:  # ₹2,00,000+
            processing_delay += 2.0  # Additional 2 seconds (RBI guidelines)
        
        # Simulate processing
        time.sleep(processing_delay * 0.01)  # Scale down for demo
        
        # Step 4: Success probability (based on real UPI stats)
        # Real UPI success rate is ~95-98%
        import random
        success_probability = 0.96  # 96% success rate
        
        if random.random() < success_probability:
            processing_time = (time.time() - start_time) * 1000
            reference_number = f"UPI{int(time.time())}{random.randint(100000, 999999)}"
            
            print(f"   ✅ NPCI: Transaction successful in {processing_time:.1f}ms")
            
            return {
                'status': 'success',
                'message': 'Transaction completed successfully',
                'processing_time_ms': round(processing_time, 1),
                'reference_number': reference_number
            }
        else:
            processing_time = (time.time() - start_time) * 1000
            failure_reasons = [
                'Insufficient balance',
                'Account blocked',
                'Daily limit exceeded',
                'Technical failure at bank',
                'Invalid account details'
            ]
            
            failure_reason = random.choice(failure_reasons)
            print(f"   ❌ NPCI: Transaction failed - {failure_reason}")
            
            return {
                'status': 'failed',
                'message': failure_reason,
                'processing_time_ms': round(processing_time, 1)
            }

class FraudDetectionSystem:
    """Simple fraud detection for UPI transactions"""
    
    def check_transaction(self, transaction: UPITransaction) -> float:
        """Return fraud score between 0-1 (higher = more suspicious)"""
        fraud_score = 0.0
        
        # High amount transactions are riskier
        if transaction.amount > 100000:  # ₹1 lakh+
            fraud_score += 0.3
        
        # Very high amounts are very risky
        if transaction.amount > 500000:  # ₹5 lakh+
            fraud_score += 0.5
        
        # Random factor for simulation
        import random
        fraud_score += random.uniform(0, 0.2)
        
        return min(fraud_score, 1.0)

# Example: UPI system processing various transactions
print("🏛️ UPI PAYMENT SYSTEM - TRANSACTION PROCESSING SIMULATION\n")
print("=" * 70)

# Create UPI system
upi_system = UPISystemArchitecture()

# Simulate typical UPI transactions in India
print("💰 SIMULATING TYPICAL INDIAN UPI TRANSACTIONS:")
print("-" * 50)

sample_transactions = [
    # Small payment - tea/coffee
    UPITransaction(
        str(uuid.uuid4()),
        "rajesh@phonepe",
        "teashop@paytm", 
        20.0,  # ₹20 tea
        purpose="food"
    ),
    
    # Bill splitting among friends
    UPITransaction(
        str(uuid.uuid4()),
        "priya@googlepay",
        "amit@phonepe",
        350.0,  # ₹350 dinner split
        purpose="personal"
    ),
    
    # Rent payment
    UPITransaction(
        str(uuid.uuid4()),
        "student@paytm",
        "landlord@phonepe",
        25000.0,  # ₹25,000 rent
        purpose="rent"
    ),
    
    # Large business payment
    UPITransaction(
        str(uuid.uuid4()),
        "company@hdfc",
        "vendor@sbi",
        150000.0,  # ₹1.5 lakh business payment
        purpose="business"
    )
]

for i, transaction in enumerate(sample_transactions, 1):
    print(f"\n💳 TRANSACTION #{i}:")
    print("-" * 30)
    
    result = upi_system.initiate_payment(transaction)
    
    print(f"📊 Result: {result['status'].upper()}")
    print(f"   Message: {result['message']}")
    print(f"   Processing Time: {result.get('processing_time_ms', 'N/A')}ms")
    
    if result['status'] == 'success':
        print(f"   Reference: {result.get('reference_number', 'N/A')}")
    
    print("-" * 30)

print(f"\n📊 UPI SYSTEM PERFORMANCE STATISTICS:")
stats = upi_system.get_system_stats()
for key, value in stats.items():
    if isinstance(value, float):
        print(f"{key}: ₹{value:,.2f}" if 'inr' in key.lower() else f"{key}: {value:.2f}")
    else:
        print(f"{key}: {value:,}" if isinstance(value, int) else f"{key}: {value}")

print(f"\n🇮🇳 UPI INDIA SUCCESS METRICS:")
print(f"✅ Monthly Volume: 10+ Billion transactions")
print(f"✅ Annual Value: ₹50+ Lakh Crore")
print(f"✅ Success Rate: 95-98% (Industry leading)")
print(f"✅ Processing Time: <5 seconds average")
print(f"✅ Participating Banks: 400+ banks")
print(f"✅ Active Users: 350+ Million")
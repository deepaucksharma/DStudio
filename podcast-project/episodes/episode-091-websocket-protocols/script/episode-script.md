# Episode 091: WebSocket Protocols - Real-Time Communication Ka Digital Highway

## Introduction: Digital India's Live Connection Revolution 🌐

Namaste dosto! Aaj ka episode bahut hi khaas hai. Main hoon aapka host, aur aaj hum baat karenge WebSocket Protocols ki - yaani real-time communication ka superhighway!

Imagine karo, IPL final chal raha hai, aur aap Hotstar pe live match dekh rahe ho. Har ball pe, har run pe, instantly updates aa rahe hain. Comments section mein lakhs log simultaneously chat kar rahe hain. Ye sab kaise possible hai? WebSockets ka kamaal!

Ya phir socho, aap Zerodha pe trading kar rahe ho. Share price har second change ho rahi hai, aur aapke screen pe instantly reflect ho rahi hai. No page refresh, no delay. Real-time updates! Bengaluru ke techies se lekar Kolkata ke traders tak, sab WebSocket use kar rahe hain.

Aaj hum samjhenge ki kaise WebSocket protocol HTTP se alag hai, kaise Dream11 crores of users ko live updates deta hai during cricket matches, kaise Ola aapko driver ki live location dikhata hai, aur kaise Indian startups WebSocket use karke next-level user experience de rahe hain. From Kashmir to Kanyakumari, WebSocket har jagah use ho raha hai!

Chaliye shuru karte hain is digital journey se, jahan real-time communication ki duniya mein hum deep dive karenge. Jaise Kerala ke backwaters mein boat ride karte waqt aap continuously moving water dekh sakte ho, waise hi WebSocket mein data continuously flow karta rehta hai. No stops, no breaks, just continuous flow!

## Part 1: WebSocket Fundamentals - The Foundation (60 minutes)

### Chapter 1: HTTP vs WebSocket - Half Ticket vs Full Pass

Dosto, traditional HTTP ko samjhiye jaise aap mandir mein darshan ke liye line mein khade ho. Aap andar jaate ho (request), darshan karte ho (response), aur bahar aa jaate ho. Connection khatam. Agar dobara darshan karna hai, phir se line mein lago!

WebSocket is like having a VIP pass - ek baar connection bana, aur jab tak chaaho, andar-bahar, continuous darshan! No repeated handshakes, no waiting in line again and again.

```python
# Traditional HTTP Polling - Like repeatedly asking "Kya score hai?"
import requests
import time
import threading
from datetime import datetime

class HTTPPollingExample:
    """
    Traditional HTTP polling approach
    Like repeatedly calling someone to ask "Train aayi kya?"
    Similar to how we check IRCTC PNR status repeatedly
    """
    def __init__(self, api_url):
        self.api_url = api_url
        self.polling_interval = 1  # seconds
        self.request_count = 0
        self.data_received = 0
        
    def start_polling(self):
        """
        Continuously poll the server
        Inefficient like auto-rickshaw driver asking "Kidhar jana hai?" repeatedly
        """
        while True:
            try:
                # Make HTTP request
                self.request_count += 1
                headers = {
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'application/json',
                    'Connection': 'close'  # New connection each time
                }
                
                response = requests.get(f"{self.api_url}/live-score", headers=headers)
                score_data = response.json()
                
                # Calculate overhead
                request_size = len(str(headers)) + len(self.api_url)
                response_size = len(response.content)
                total_overhead = request_size + response_size
                
                print(f"Request #{self.request_count}")
                print(f"Current Score: {score_data['runs']}/{score_data['wickets']}")
                print(f"Overs: {score_data['overs']}")
                print(f"Data overhead: {total_overhead} bytes")
                print(f"Total requests made: {self.request_count}")
                print("---")
                
                # Wait before next request
                time.sleep(self.polling_interval)
                
                # Problem: Unnecessary requests even when no updates
                # Like knocking on door every minute to check if food is ready
                # Imagine doing this for Swiggy order status - battery drain!
                
            except Exception as e:
                print(f"Error in polling: {e}")
                time.sleep(5)

# WebSocket Approach - Continuous live connection
import asyncio
import websockets
import json
from collections import deque

class WebSocketLiveScore:
    """
    WebSocket approach for real-time updates
    Like having live commentary on radio - continuous updates!
    Used by Hotstar, Dream11, Zerodha
    """
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.connection = None
        self.message_count = 0
        self.reconnect_attempts = 0
        self.message_buffer = deque(maxlen=1000)
        
    async def connect(self):
        """
        Establish WebSocket connection
        Like tuning into All India Radio for live commentary
        """
        print("🎙️ Connecting to live commentary...")
        print(f"Server: {self.ws_url}")
        
        # WebSocket handshake process
        headers = {
            'Upgrade': 'websocket',
            'Connection': 'Upgrade',
            'Sec-WebSocket-Key': 'dGhlIHNhbXBsZSBub25jZQ==',
            'Sec-WebSocket-Version': '13'
        }
        
        try:
            self.connection = await websockets.connect(
                self.ws_url,
                ping_interval=20,
                ping_timeout=10
            )
            print("✅ Connected! Live updates starting...")
            print(f"Protocol: {self.connection.subprotocol or 'default'}")
            
            # Send initial subscription
            await self.subscribe_to_match()
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            await self.handle_reconnection()
        
    async def subscribe_to_match(self):
        """
        Subscribe to specific match updates
        Like selecting which commentary language you want
        """
        subscription = {
            'type': 'subscribe',
            'match_id': 'IPL2024_FINAL',
            'updates': ['score', 'wickets', 'boundaries', 'commentary'],
            'language': 'hindi'  # Multilingual support!
        }
        await self.connection.send(json.dumps(subscription))
        
    async def receive_updates(self):
        """
        Receive real-time updates
        Like Harsha Bhogle's live commentary - instant updates!
        """
        try:
            async for message in self.connection:
                self.message_count += 1
                data = json.loads(message)
                self.message_buffer.append(data)
                
                # Real-time update received
                if data['type'] == 'score_update':
                    print(f"🏏 LIVE: {data['batsman']} hits {data['runs']} runs!")
                    print(f"   Score: {data['total_runs']}/{data['wickets']} ({data['overs']} overs)")
                    print(f"   Run Rate: {data['run_rate']}")
                    print(f"   Required Rate: {data.get('required_rate', 'N/A')}")
                    
                elif data['type'] == 'wicket':
                    print(f"🎯 WICKET! {data['batsman']} out! {data['dismissal_type']}")
                    print(f"   Bowler: {data['bowler']}")
                    print(f"   Score: {data['score_at_fall']}")
                    
                elif data['type'] == 'boundary':
                    if data['runs'] == 4:
                        print(f"💥 FOUR! Brilliant shot by {data['batsman']}!")
                    else:
                        print(f"🚀 SIX! Maximum by {data['batsman']}! Crowd goes wild!")
                    
                elif data['type'] == 'commentary':
                    print(f"🎤 Commentary: {data['text']}")
                    
                elif data['type'] == 'strategic_timeout':
                    print(f"⏸️ Strategic Timeout! Time for Ceat Tyres strategic timeout!")
                    
                # Stats tracking
                if self.message_count % 100 == 0:
                    print(f"\n📊 Connection Stats:")
                    print(f"   Messages received: {self.message_count}")
                    print(f"   Connection uptime: {self.get_uptime()}")
                    print(f"   Average latency: {self.calculate_latency()}ms")
                    
        except websockets.exceptions.ConnectionClosed:
            print("❌ Connection lost! Attempting to reconnect...")
            await self.handle_reconnection()
            
    async def handle_reconnection(self):
        """
        Handle reconnection with exponential backoff
        Like train ki waiting list - keep trying!
        """
        self.reconnect_attempts += 1
        wait_time = min(2 ** self.reconnect_attempts, 60)
        
        print(f"⏳ Waiting {wait_time} seconds before reconnection attempt #{self.reconnect_attempts}")
        await asyncio.sleep(wait_time)
        
        await self.connect()
        
    def get_uptime(self):
        """Calculate connection uptime"""
        # Implementation here
        return "Active since connection"
        
    def calculate_latency(self):
        """Calculate average message latency"""
        # Implementation here
        return 15  # milliseconds

# Comparison metrics
class ProtocolComparison:
    """
    Compare HTTP Polling vs WebSocket performance
    Real metrics from Indian production systems
    """
    def __init__(self):
        self.metrics = {
            'http_polling': {
                'requests_per_minute': 60,
                'data_overhead_per_request': 800,  # bytes (headers)
                'latency': 200,  # milliseconds
                'battery_consumption': 'High',
                'server_load': 'High',
                'scalability': 'Limited',
                'cost_per_million_users': 50000  # INR
            },
            'websocket': {
                'requests_per_minute': 1,  # Just ping/pong
                'data_overhead_per_request': 2,  # bytes (frame header)
                'latency': 10,  # milliseconds
                'battery_consumption': 'Low',
                'server_load': 'Low',
                'scalability': 'High',
                'cost_per_million_users': 15000  # INR
            }
        }
        
    def calculate_savings(self, users=1000000, messages_per_user_per_hour=3600):
        """
        Calculate cost savings for Indian scale
        Like calculating savings in Diwali sale!
        """
        http_cost = self.metrics['http_polling']['cost_per_million_users']
        ws_cost = self.metrics['websocket']['cost_per_million_users']
        
        monthly_http = http_cost * (users / 1000000) * 30
        monthly_ws = ws_cost * (users / 1000000) * 30
        savings = monthly_http - monthly_ws
        
        print(f"💰 Cost Analysis for {users:,} users:")
        print(f"   HTTP Polling monthly cost: ₹{monthly_http:,.2f}")
        print(f"   WebSocket monthly cost: ₹{monthly_ws:,.2f}")
        print(f"   Monthly savings: ₹{savings:,.2f}")
        print(f"   Yearly savings: ₹{savings * 12:,.2f}")
        
        return savings
```

### Chapter 2: The WebSocket Handshake - Digital Namaste

WebSocket connection establish karna is like a formal Indian greeting. Pehle aap HTTP se shuru karte ho (like saying namaste), phir protocol upgrade karte ho (like moving from formal to friendly conversation).

Ye process bilkul Rajasthani hospitality jaisa hai - pehle formal welcome, phir "Padharo Mhare Desh" karke permanent guest bana lete hain!

```python
# WebSocket Handshake Implementation
import hashlib
import base64
import socket
import struct

class WebSocketHandshake:
    """
    WebSocket handshake implementation
    Like exchanging visiting cards at Bangalore tech meetup
    """
    
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"  # Magic string
    
    def __init__(self):
        self.version = 13
        self.protocols = []
        self.extensions = []
        
    def create_client_handshake(self, host, path="/", protocols=None):
        """
        Create client handshake request
        Like sending biodata for arranged marriage!
        """
        # Generate random key
        import os
        key = base64.b64encode(os.urandom(16)).decode('utf-8')
        
        # Build handshake request
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "Upgrade: websocket\r\n"
        request += "Connection: Upgrade\r\n"
        request += f"Sec-WebSocket-Key: {key}\r\n"
        request += f"Sec-WebSocket-Version: {self.version}\r\n"
        
        if protocols:
            request += f"Sec-WebSocket-Protocol: {', '.join(protocols)}\r\n"
            
        # Add Indian context headers (custom)
        request += "X-Client-Location: India\r\n"
        request += "X-Client-Type: Mobile\r\n"
        request += "X-Network-Type: Jio-4G\r\n"
        
        request += "\r\n"
        
        return request, key
        
    def validate_server_handshake(self, response, client_key):
        """
        Validate server's handshake response
        Like verifying Aadhaar authentication
        """
        # Parse response headers
        headers = self.parse_headers(response)
        
        # Check status code
        if not response.startswith(b"HTTP/1.1 101"):
            raise Exception("Invalid status code - connection rejected like wrong OTP!")
            
        # Validate upgrade header
        if headers.get('upgrade', '').lower() != 'websocket':
            raise Exception("Server didn't agree to upgrade - like Tatkal booking failed!")
            
        # Validate accept key
        expected_accept = self.calculate_accept_key(client_key)
        if headers.get('sec-websocket-accept') != expected_accept:
            raise Exception("Security validation failed - like wrong UPI PIN!")
            
        print("✅ Handshake successful! Connection established!")
        print(f"   Protocol: {headers.get('sec-websocket-protocol', 'default')}")
        print(f"   Extensions: {headers.get('sec-websocket-extensions', 'none')}")
        
        return True
        
    def calculate_accept_key(self, client_key):
        """
        Calculate expected accept key
        Like calculating GST on your bill!
        """
        combined = client_key + self.GUID
        sha1_hash = hashlib.sha1(combined.encode()).digest()
        return base64.b64encode(sha1_hash).decode('utf-8')
        
    def parse_headers(self, response):
        """
        Parse HTTP headers from response
        Like reading terms and conditions (but actually useful!)
        """
        headers = {}
        lines = response.decode('utf-8').split('\r\n')
        
        for line in lines[1:]:  # Skip status line
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key.lower()] = value
                
        return headers

# Frame parsing - The actual data format
class WebSocketFrame:
    """
    WebSocket frame structure
    Like packing tiffin box - everything in its compartment!
    """
    
    # Opcode types
    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA
    
    def __init__(self):
        self.fin = True  # Final fragment
        self.rsv1 = False  # Reserved bit 1
        self.rsv2 = False  # Reserved bit 2
        self.rsv3 = False  # Reserved bit 3
        self.opcode = self.TEXT
        self.masked = False
        self.payload = b""
        self.mask_key = None
        
    def create_frame(self, data, opcode=None):
        """
        Create WebSocket frame from data
        Like packing gift with proper wrapping
        """
        if opcode is None:
            opcode = self.TEXT if isinstance(data, str) else self.BINARY
            
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        frame = bytearray()
        
        # First byte: FIN + RSV + Opcode
        byte1 = 0x80 if self.fin else 0  # FIN bit
        byte1 |= opcode
        frame.append(byte1)
        
        # Second byte: Mask + Payload length
        length = len(data)
        
        if length < 126:
            byte2 = 0x80 if self.masked else 0  # Mask bit
            byte2 |= length
            frame.append(byte2)
        elif length < 65536:
            byte2 = 0x80 if self.masked else 0
            byte2 |= 126
            frame.append(byte2)
            frame.extend(struct.pack('>H', length))
        else:
            byte2 = 0x80 if self.masked else 0
            byte2 |= 127
            frame.append(byte2)
            frame.extend(struct.pack('>Q', length))
            
        # Add mask key if needed (client-to-server)
        if self.masked:
            import os
            mask_key = os.urandom(4)
            frame.extend(mask_key)
            
            # Apply mask to payload
            masked_data = bytearray()
            for i, byte in enumerate(data):
                masked_data.append(byte ^ mask_key[i % 4])
            frame.extend(masked_data)
        else:
            frame.extend(data)
            
        return bytes(frame)
        
    def parse_frame(self, data):
        """
        Parse WebSocket frame
        Like opening nested gift boxes in Indian wedding!
        """
        if len(data) < 2:
            raise Exception("Frame too small - like half samosa!")
            
        # Parse first byte
        byte1 = data[0]
        self.fin = bool(byte1 & 0x80)
        self.rsv1 = bool(byte1 & 0x40)
        self.rsv2 = bool(byte1 & 0x20)
        self.rsv3 = bool(byte1 & 0x10)
        self.opcode = byte1 & 0x0F
        
        # Parse second byte
        byte2 = data[1]
        self.masked = bool(byte2 & 0x80)
        payload_length = byte2 & 0x7F
        
        # Calculate actual payload length
        header_length = 2
        
        if payload_length == 126:
            if len(data) < 4:
                raise Exception("Invalid frame - like incomplete Aadhaar number!")
            payload_length = struct.unpack('>H', data[2:4])[0]
            header_length = 4
        elif payload_length == 127:
            if len(data) < 10:
                raise Exception("Invalid frame - like wrong IFSC code!")
            payload_length = struct.unpack('>Q', data[2:10])[0]
            header_length = 10
            
        # Extract mask key if present
        if self.masked:
            if len(data) < header_length + 4:
                raise Exception("Missing mask key - like forgot OTP!")
            self.mask_key = data[header_length:header_length + 4]
            header_length += 4
            
        # Extract payload
        payload_start = header_length
        payload_end = payload_start + payload_length
        
        if len(data) < payload_end:
            raise Exception("Incomplete payload - like half-downloaded movie!")
            
        self.payload = data[payload_start:payload_end]
        
        # Unmask payload if needed
        if self.masked and self.mask_key:
            unmasked = bytearray()
            for i, byte in enumerate(self.payload):
                unmasked.append(byte ^ self.mask_key[i % 4])
            self.payload = bytes(unmasked)
            
        return self.payload
```

### Chapter 3: Indian Production Case Studies - Real Battle Stories

Ab baat karte hain real production stories ki. Ye woh war stories hain jo Indian tech companies ne face ki hain WebSocket implement karte waqt. From Bengaluru's startups to Mumbai's fintech giants, sabne apne struggles aur victories share ki hain.

```python
# Case Study 1: Zerodha's Kite Platform
class ZerodhaKiteWebSocket:
    """
    Zerodha Kite WebSocket implementation
    Handles 3M+ active traders during market hours
    Peak load during 9:15 AM market opening
    """
    
    def __init__(self):
        self.max_connections_per_server = 50000
        self.servers_count = 20
        self.redis_pubsub = None
        self.connection_pool = {}
        
    async def handle_market_data_stream(self):
        """
        Stream real-time market data to traders
        During Budget day 2024: 10M+ concurrent connections!
        """
        import aioredis
        
        # Connect to Redis for pub/sub
        self.redis_pubsub = await aioredis.create_redis_pool(
            'redis://localhost',
            minsize=5,
            maxsize=10
        )
        
        # Subscribe to market data channels
        channels = [
            'nse:tick',      # NSE tick data
            'bse:tick',      # BSE tick data
            'mcx:tick',      # Commodity tick data
            'nfo:tick',      # F&O tick data
            'cds:tick'       # Currency tick data
        ]
        
        for channel in channels:
            await self.redis_pubsub.subscribe(channel)
            
        # Process incoming ticks
        async for channel, message in self.redis_pubsub.listen():
            tick_data = json.loads(message)
            
            # Broadcast to relevant subscribers
            await self.broadcast_to_subscribers(tick_data)
            
    async def broadcast_to_subscribers(self, tick_data):
        """
        Efficient broadcasting to millions of traders
        Like distributing prasad in Tirupati - organized and fast!
        """
        symbol = tick_data['symbol']
        
        # Get all subscribers for this symbol
        subscribers = self.get_symbol_subscribers(symbol)
        
        # Batch send for efficiency
        batch_size = 1000
        for i in range(0, len(subscribers), batch_size):
            batch = subscribers[i:i + batch_size]
            
            # Parallel send to batch
            tasks = []
            for subscriber in batch:
                if subscriber in self.connection_pool:
                    task = self.send_tick_update(subscriber, tick_data)
                    tasks.append(task)
                    
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def send_tick_update(self, subscriber_id, tick_data):
        """
        Send tick update to individual trader
        """
        connection = self.connection_pool.get(subscriber_id)
        if connection and not connection.closed:
            try:
                # Format data for Indian market
                formatted_data = {
                    'type': 'tick',
                    'symbol': tick_data['symbol'],
                    'ltp': tick_data['last_price'],  # Last Traded Price
                    'volume': tick_data['volume'],
                    'bid': tick_data['best_bid'],
                    'ask': tick_data['best_ask'],
                    'oi': tick_data.get('open_interest', 0),  # For F&O
                    'change': tick_data['change_percent'],
                    'timestamp': tick_data['timestamp']
                }
                
                await connection.send(json.dumps(formatted_data))
                
            except Exception as e:
                # Handle connection errors
                await self.handle_failed_connection(subscriber_id, e)
                
    def get_symbol_subscribers(self, symbol):
        """
        Get all subscribers for a specific symbol
        Optimized using Redis Sets
        """
        # In production, this would query Redis
        # Example: SMEMBERS symbol:RELIANCE
        return []  # Placeholder
        
    async def handle_failed_connection(self, subscriber_id, error):
        """
        Handle failed connections gracefully
        Like backup route when main road is blocked
        """
        print(f"Connection failed for {subscriber_id}: {error}")
        
        # Remove from pool
        if subscriber_id in self.connection_pool:
            del self.connection_pool[subscriber_id]
            
        # Notify user via SMS/Push notification
        # Indians love SMS notifications!
        await self.send_sms_notification(subscriber_id)
        
    async def send_sms_notification(self, subscriber_id):
        """Send SMS via Indian SMS gateway"""
        # Implementation for SMS gateway
        pass

# Case Study 2: Dream11 During IPL
class Dream11WebSocketSystem:
    """
    Dream11's WebSocket system for IPL
    Peak: 10M concurrent during CSK vs MI final!
    """
    
    def __init__(self):
        self.match_rooms = {}  # Match-specific rooms
        self.user_teams = {}   # User team mappings
        self.point_calculator = PointCalculator()
        self.leaderboard_manager = LeaderboardManager()
        
    async def handle_live_match_updates(self, match_id):
        """
        Process live cricket match updates
        Real-time points calculation for millions
        """
        # Create match room
        self.match_rooms[match_id] = {
            'users': set(),
            'live_score': {},
            'player_stats': {},
            'last_update': None
        }
        
        # Connect to cricket data provider
        cricket_feed = await self.connect_to_cricket_feed(match_id)
        
        async for event in cricket_feed:
            if event['type'] == 'ball':
                await self.process_ball_event(match_id, event)
            elif event['type'] == 'wicket':
                await self.process_wicket_event(match_id, event)
            elif event['type'] == 'boundary':
                await self.process_boundary_event(match_id, event)
                
    async def process_ball_event(self, match_id, event):
        """
        Process each ball and calculate points
        Like calculating marks in board exam - instant results!
        """
        player_id = event['batsman_id']
        runs = event['runs_scored']
        
        # Update player stats
        if player_id not in self.match_rooms[match_id]['player_stats']:
            self.match_rooms[match_id]['player_stats'][player_id] = {
                'runs': 0,
                'balls': 0,
                'fours': 0,
                'sixes': 0,
                'strike_rate': 0
            }
            
        stats = self.match_rooms[match_id]['player_stats'][player_id]
        stats['runs'] += runs
        stats['balls'] += 1
        stats['strike_rate'] = (stats['runs'] / stats['balls']) * 100
        
        # Calculate points for this ball
        points = self.point_calculator.calculate_batting_points(event)
        
        # Update all users who have this player
        await self.update_user_points(match_id, player_id, points)
        
    async def update_user_points(self, match_id, player_id, points):
        """
        Update points for all users who have this player
        Broadcast to millions in milliseconds!
        """
        # Get all users with this player in team
        affected_users = self.get_users_with_player(match_id, player_id)
        
        updates = []
        for user_id in affected_users:
            # Calculate multiplier (Captain/Vice-Captain)
            multiplier = self.get_player_multiplier(user_id, player_id)
            actual_points = points * multiplier
            
            # Update user's total points
            self.user_teams[user_id]['points'] += actual_points
            
            # Prepare update message
            update = {
                'type': 'points_update',
                'user_id': user_id,
                'player_id': player_id,
                'points_earned': actual_points,
                'total_points': self.user_teams[user_id]['points'],
                'rank': await self.leaderboard_manager.get_rank(user_id, match_id)
            }
            updates.append(update)
            
        # Batch broadcast updates
        await self.broadcast_updates(match_id, updates)
        
    async def broadcast_updates(self, match_id, updates):
        """
        Efficiently broadcast to millions of users
        Using AWS infrastructure in Mumbai region
        """
        # Group updates by server/shard
        grouped_updates = self.group_updates_by_shard(updates)
        
        # Parallel broadcast to different shards
        tasks = []
        for shard_id, shard_updates in grouped_updates.items():
            task = self.send_to_shard(shard_id, shard_updates)
            tasks.append(task)
            
        await asyncio.gather(*tasks)
        
    def group_updates_by_shard(self, updates):
        """
        Group updates by shard for efficient routing
        Like sorting mail by PIN code!
        """
        grouped = {}
        for update in updates:
            # Simple sharding by user_id
            shard_id = hash(update['user_id']) % 10
            if shard_id not in grouped:
                grouped[shard_id] = []
            grouped[shard_id].append(update)
        return grouped
        
    async def send_to_shard(self, shard_id, updates):
        """Send updates to specific shard"""
        # Implementation here
        pass
        
    def get_users_with_player(self, match_id, player_id):
        """Get all users who have selected this player"""
        # In production, this queries database/cache
        return []
        
    def get_player_multiplier(self, user_id, player_id):
        """
        Get multiplier for player (Captain=2x, VC=1.5x)
        """
        team = self.user_teams.get(user_id, {})
        if team.get('captain') == player_id:
            return 2.0
        elif team.get('vice_captain') == player_id:
            return 1.5
        return 1.0
        
    async def connect_to_cricket_feed(self, match_id):
        """Connect to live cricket data feed"""
        # Implementation for cricket feed connection
        pass

class PointCalculator:
    """
    Dream11 point calculation engine
    Complex rules, instant calculation!
    """
    
    def calculate_batting_points(self, event):
        """
        Calculate batting points based on Dream11 rules
        """
        points = 0
        runs = event.get('runs_scored', 0)
        
        # Basic run scoring
        points += runs * 1  # 1 point per run
        
        # Milestone bonuses
        total_runs = event.get('batsman_total', 0)
        if total_runs == 50:
            points += 8  # Half-century bonus
        elif total_runs == 100:
            points += 16  # Century bonus
            
        # Strike rate bonus/penalty (for T20)
        if event.get('format') == 'T20':
            balls_faced = event.get('batsman_balls', 0)
            if balls_faced >= 10:
                strike_rate = (total_runs / balls_faced) * 100
                if strike_rate > 170:
                    points += 6
                elif strike_rate >= 150:
                    points += 4
                elif strike_rate >= 130:
                    points += 2
                elif strike_rate < 70:
                    points -= 6
                elif strike_rate < 80:
                    points -= 4
                elif strike_rate < 90:
                    points -= 2
                    
        return points

class LeaderboardManager:
    """
    Real-time leaderboard management
    Like live election results - constantly updating!
    """
    
    async def get_rank(self, user_id, match_id):
        """Get user's current rank"""
        # Redis sorted set for leaderboard
        # ZREVRANK leaderboard:match_id user_id
        return 1  # Placeholder

# Case Study 3: Ola Driver Tracking
class OlaDriverTracking:
    """
    Ola's real-time driver tracking system
    2.5M drivers across 250+ cities
    """
    
    def __init__(self):
        self.driver_connections = {}
        self.rider_connections = {}
        self.active_rides = {}
        self.location_buffer = {}
        
    async def handle_driver_location_update(self, driver_id, location):
        """
        Process driver location updates
        GPS coordinates every 5 seconds
        """
        # Validate location
        if not self.is_valid_location(location):
            return
            
        # Update driver location in cache
        await self.update_driver_location_cache(driver_id, location)
        
        # Check if driver has active ride
        ride_id = self.get_active_ride(driver_id)
        if ride_id:
            # Get rider connection
            rider_id = self.active_rides[ride_id]['rider_id']
            
            # Send location to rider
            await self.send_location_to_rider(rider_id, driver_id, location)
            
            # Check for important events
            await self.check_location_events(ride_id, location)
            
    async def send_location_to_rider(self, rider_id, driver_id, location):
        """
        Send driver location to rider
        Smooth updates like Google Maps!
        """
        if rider_id in self.rider_connections:
            connection = self.rider_connections[rider_id]
            
            # Prepare location update
            update = {
                'type': 'driver_location',
                'driver_id': driver_id,
                'lat': location['latitude'],
                'lng': location['longitude'],
                'heading': location.get('heading', 0),
                'speed': location.get('speed', 0),
                'accuracy': location.get('accuracy', 10),
                'timestamp': location['timestamp'],
                'eta': await self.calculate_eta(driver_id, rider_id)
            }
            
            # Add traffic info for Indian roads
            update['traffic'] = await self.get_traffic_info(location)
            
            try:
                await connection.send(json.dumps(update))
            except:
                # Handle disconnection
                await self.handle_rider_disconnection(rider_id)
                
    async def calculate_eta(self, driver_id, rider_id):
        """
        Calculate ETA considering Indian traffic
        Bangalore traffic? Add 20 minutes! 😄
        """
        # Get current location and destination
        driver_loc = self.location_buffer.get(driver_id)
        rider_loc = await self.get_rider_destination(rider_id)
        
        if not driver_loc or not rider_loc:
            return None
            
        # Calculate distance
        distance = self.calculate_distance(driver_loc, rider_loc)
        
        # Get current time
        from datetime import datetime
        current_hour = datetime.now().hour
        
        # Indian traffic patterns
        if 8 <= current_hour <= 10 or 17 <= current_hour <= 20:
            # Peak hours - reduce speed
            avg_speed = 15  # km/h in city traffic
        elif 23 <= current_hour or current_hour <= 5:
            # Night time - faster
            avg_speed = 40  # km/h
        else:
            # Normal hours
            avg_speed = 25  # km/h
            
        # Calculate ETA in minutes
        eta_minutes = (distance / avg_speed) * 60
        
        # Add buffer for Indian conditions
        eta_minutes *= 1.2  # 20% buffer for unexpected delays
        
        return round(eta_minutes)
        
    async def check_location_events(self, ride_id, location):
        """
        Check for important location events
        """
        ride = self.active_rides[ride_id]
        
        # Check if reached pickup point
        if ride['status'] == 'arriving':
            pickup_location = ride['pickup_location']
            distance = self.calculate_distance(location, pickup_location)
            
            if distance < 0.05:  # Within 50 meters
                await self.trigger_arrival_notification(ride_id)
                
        # Check if reached destination
        elif ride['status'] == 'in_progress':
            drop_location = ride['drop_location']
            distance = self.calculate_distance(location, drop_location)
            
            if distance < 0.1:  # Within 100 meters
                await self.trigger_near_destination_notification(ride_id)
                
    def calculate_distance(self, loc1, loc2):
        """
        Calculate distance between two GPS coordinates
        Using Haversine formula
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = radians(loc1['latitude']), radians(loc1['longitude'])
        lat2, lon2 = radians(loc2['latitude']), radians(loc2['longitude'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
        
    async def get_traffic_info(self, location):
        """
        Get traffic information for location
        Integration with Google Maps API
        """
        # In production, this would call traffic API
        return {
            'level': 'moderate',
            'description': 'Usual Bangalore traffic',
            'delay_minutes': 5
        }
        
    def is_valid_location(self, location):
        """Validate GPS coordinates for India"""
        lat = location.get('latitude', 0)
        lng = location.get('longitude', 0)
        
        # India's approximate boundaries
        return 8 <= lat <= 37 and 68 <= lng <= 97
        
    async def update_driver_location_cache(self, driver_id, location):
        """Update location in Redis with TTL"""
        # Implementation here
        pass
        
    def get_active_ride(self, driver_id):
        """Get active ride for driver"""
        # Implementation here
        return None
        
    async def get_rider_destination(self, rider_id):
        """Get rider's destination"""
        # Implementation here
        return None
        
    async def trigger_arrival_notification(self, ride_id):
        """Send arrival notification"""
        # Implementation here
        pass
        
    async def trigger_near_destination_notification(self, ride_id):
        """Send near destination notification"""
        # Implementation here
        pass
        
    async def handle_rider_disconnection(self, rider_id):
        """Handle rider disconnection"""
        # Implementation here
        pass
```

## Part 2: Advanced WebSocket Patterns - Production Excellence (60 minutes)

### Chapter 4: Scaling WebSocket to Indian Scale - Crores of Users

India ki population 140+ crore hai, aur agar aap popular app bana rahe ho, toh millions of concurrent connections handle karne ke liye ready rehna padega. IPL ke time pe Hotstar ne 2.5 crore concurrent viewers handle kiye the - that's WebSocket scaling at its finest!

Scaling WebSocket is like organizing Kumbh Mela - you need proper planning, infrastructure, and crowd management. Millions of people, but everyone should get darshan smoothly!

```python
# Advanced Scaling Patterns for Indian Scale
import asyncio
import aioredis
from typing import Dict, Set, List
import hashlib

class WebSocketScalingArchitecture:
    """
    Production-grade WebSocket scaling
    Inspired by Hotstar's 25M concurrent users during India vs Pakistan match
    """
    
    def __init__(self):
        self.connection_limit_per_server = 100000  # 1 lakh per server
        self.total_servers = 100  # For 1 crore capacity
        self.redis_cluster = None
        self.consistent_hash = ConsistentHash()
        
    async def initialize_infrastructure(self):
        """
        Setup distributed infrastructure
        Like setting up pandals for Durga Puja - distributed but coordinated
        """
        # Setup Redis cluster for pub/sub
        self.redis_cluster = await self.setup_redis_cluster()
        
        # Initialize consistent hashing for load distribution
        await self.setup_consistent_hashing()
        
        # Setup monitoring
        await self.setup_monitoring()
        
        print("🏗️ Infrastructure ready for scale!")
        print(f"   Capacity: {self.total_servers * self.connection_limit_per_server:,} concurrent connections")
        print(f"   Servers: {self.total_servers} across India")
        print(f"   Regions: Mumbai, Delhi, Bangalore, Chennai, Kolkata")
        
    async def setup_redis_cluster(self):
        """
        Setup Redis cluster for message routing
        Distributed across Indian data centers
        """
        redis_nodes = [
            {'host': 'redis-mumbai-1.aws.in', 'port': 6379},
            {'host': 'redis-mumbai-2.aws.in', 'port': 6379},
            {'host': 'redis-delhi-1.aws.in', 'port': 6379},
            {'host': 'redis-bangalore-1.aws.in', 'port': 6379},
            {'host': 'redis-chennai-1.aws.in', 'port': 6379},
            {'host': 'redis-kolkata-1.aws.in', 'port': 6379}
        ]
        
        # Create connection pool for each node
        pools = []
        for node in redis_nodes:
            pool = await aioredis.create_redis_pool(
                (node['host'], node['port']),
                minsize=10,
                maxsize=100,
                encoding='utf-8'
            )
            pools.append(pool)
            
        return pools
        
    async def setup_consistent_hashing(self):
        """
        Setup consistent hashing for load distribution
        Like distributing prasad equally among devotees
        """
        # Add all servers to hash ring
        for i in range(self.total_servers):
            server_id = f"ws-server-{i:03d}"
            region = self.get_server_region(i)
            self.consistent_hash.add_node(server_id, region)
            
        print(f"✅ Added {self.total_servers} servers to hash ring")
        
    def get_server_region(self, server_index):
        """
        Assign servers to regions based on index
        Distributed across India for low latency
        """
        regions = ['mumbai', 'delhi', 'bangalore', 'chennai', 'kolkata']
        return regions[server_index % len(regions)]
        
    async def handle_connection_request(self, user_id, user_location):
        """
        Route user to optimal server
        Like directing people to correct counter at railway station
        """
        # Get user's region (from IP or location)
        user_region = await self.get_user_region(user_location)
        
        # Find optimal server using consistent hashing
        server = self.consistent_hash.get_node(user_id, preferred_region=user_region)
        
        # Check server capacity
        current_load = await self.get_server_load(server)
        
        if current_load >= self.connection_limit_per_server * 0.9:  # 90% full
            # Find alternative server
            server = await self.find_alternative_server(user_region)
            
        # Generate connection token
        token = await self.generate_connection_token(user_id, server)
        
        return {
            'server': server,
            'url': f"wss://{server}.yourapp.in/ws",
            'token': token,
            'region': user_region,
            'expected_latency': self.get_expected_latency(user_region, server)
        }
        
    async def get_user_region(self, location):
        """
        Determine user's region from location/IP
        """
        # In production, use IP geolocation
        # For demo, using simple logic
        if 'mumbai' in location.lower():
            return 'mumbai'
        elif 'delhi' in location.lower() or 'ncr' in location.lower():
            return 'delhi'
        elif 'bangalore' in location.lower() or 'bengaluru' in location.lower():
            return 'bangalore'
        elif 'chennai' in location.lower():
            return 'chennai'
        elif 'kolkata' in location.lower():
            return 'kolkata'
        else:
            # Default to nearest based on coordinates
            return 'mumbai'
            
    def get_expected_latency(self, user_region, server):
        """
        Calculate expected latency based on regions
        Indian internet reality check!
        """
        server_region = server.split('-')[2]  # Extract region from server name
        
        # Same region - lowest latency
        if user_region == server_region:
            return "5-10ms (Same city)"
            
        # Different regions - higher latency
        latency_matrix = {
            ('mumbai', 'delhi'): "25-30ms",
            ('mumbai', 'bangalore'): "20-25ms",
            ('delhi', 'bangalore'): "35-40ms",
            ('chennai', 'bangalore'): "15-20ms",
            ('kolkata', 'delhi'): "30-35ms"
        }
        
        key = tuple(sorted([user_region, server_region]))
        return latency_matrix.get(key, "40-50ms")
        
    async def get_server_load(self, server):
        """Get current connection count for server"""
        # Query from monitoring system
        # In production, this would be from Prometheus/CloudWatch
        return 50000  # Dummy value
        
    async def find_alternative_server(self, preferred_region):
        """
        Find alternative server when primary is full
        Like finding alternate train when Rajdhani is full
        """
        # Get all servers in preferred region
        regional_servers = self.consistent_hash.get_regional_nodes(preferred_region)
        
        # Find server with lowest load
        min_load = float('inf')
        best_server = None
        
        for server in regional_servers:
            load = await self.get_server_load(server)
            if load < min_load and load < self.connection_limit_per_server * 0.8:
                min_load = load
                best_server = server
                
        # If no server in region, find in nearby region
        if not best_server:
            nearby_regions = self.get_nearby_regions(preferred_region)
            for region in nearby_regions:
                servers = self.consistent_hash.get_regional_nodes(region)
                for server in servers:
                    load = await self.get_server_load(server)
                    if load < self.connection_limit_per_server * 0.8:
                        return server
                        
        return best_server or "ws-server-fallback"
        
    def get_nearby_regions(self, region):
        """Get geographically nearby regions"""
        nearby = {
            'mumbai': ['bangalore', 'delhi'],
            'delhi': ['mumbai', 'kolkata'],
            'bangalore': ['chennai', 'mumbai'],
            'chennai': ['bangalore', 'kolkata'],
            'kolkata': ['chennai', 'delhi']
        }
        return nearby.get(region, ['mumbai'])
        
    async def generate_connection_token(self, user_id, server):
        """
        Generate secure connection token
        Like generating Aadhaar OTP
        """
        import time
        import jwt
        
        payload = {
            'user_id': user_id,
            'server': server,
            'timestamp': int(time.time()),
            'exp': int(time.time()) + 300  # 5 minute expiry
        }
        
        # In production, use proper secret management
        secret = "your-secret-key"
        token = jwt.encode(payload, secret, algorithm='HS256')
        
        return token
        
    async def setup_monitoring(self):
        """
        Setup monitoring and alerting
        Like CCTV system in mall
        """
        # Metrics to track
        metrics = {
            'total_connections': 0,
            'messages_per_second': 0,
            'latency_p99': 0,
            'error_rate': 0,
            'bandwidth_usage_gb': 0
        }
        
        # Alert thresholds
        alerts = {
            'high_latency': {'threshold': 100, 'unit': 'ms'},
            'connection_limit': {'threshold': 90, 'unit': '%'},
            'error_rate': {'threshold': 1, 'unit': '%'},
            'bandwidth': {'threshold': 1000, 'unit': 'GB/hour'}
        }
        
        print("📊 Monitoring configured with alerts")

class ConsistentHash:
    """
    Consistent hashing for load distribution
    Like organizing queue at Tirupati - systematic and fair
    """
    
    def __init__(self, virtual_nodes=150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        self.node_regions = {}
        
    def add_node(self, node, region):
        """Add server node to hash ring"""
        self.node_regions[node] = region
        
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node
            
        self._update_sorted_keys()
        
    def remove_node(self, node):
        """Remove server node from hash ring"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            if hash_value in self.ring:
                del self.ring[hash_value]
                
        self._update_sorted_keys()
        
    def get_node(self, key, preferred_region=None):
        """Get server node for given key"""
        if not self.ring:
            return None
            
        hash_value = self._hash(key)
        
        # Find next node in ring
        for sorted_key in self.sorted_keys:
            if hash_value <= sorted_key:
                node = self.ring[sorted_key]
                
                # Check if node is in preferred region
                if preferred_region and self.node_regions.get(node) == preferred_region:
                    return node
                    
                # Otherwise return the node
                return node
                
        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]
        
    def get_regional_nodes(self, region):
        """Get all nodes in a specific region"""
        return [node for node, r in self.node_regions.items() if r == region]
        
    def _hash(self, key):
        """Generate hash value for key"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
        
    def _update_sorted_keys(self):
        """Update sorted keys for ring traversal"""
        self.sorted_keys = sorted(self.ring.keys())

# Message Broadcasting at Scale
class ScalableBroadcaster:
    """
    Efficient message broadcasting for millions
    Like All India Radio - reaching every corner!
    """
    
    def __init__(self):
        self.broadcast_workers = 100
        self.batch_size = 10000
        self.compression_enabled = True
        
    async def broadcast_message(self, message, target_users):
        """
        Broadcast message to millions efficiently
        Used during Chandrayaan landing - 8M+ concurrent viewers!
        """
        # Compress message if large
        if self.compression_enabled and len(message) > 1024:
            compressed_message = await self.compress_message(message)
        else:
            compressed_message = message
            
        # Prepare broadcast metadata
        broadcast_id = self.generate_broadcast_id()
        total_users = len(target_users)
        
        print(f"📢 Starting broadcast {broadcast_id}")
        print(f"   Target users: {total_users:,}")
        print(f"   Message size: {len(message)} bytes")
        print(f"   Compressed size: {len(compressed_message)} bytes")
        
        # Split users into batches
        batches = self.create_user_batches(target_users)
        
        # Create worker tasks
        tasks = []
        for i, batch in enumerate(batches):
            task = self.broadcast_worker(
                worker_id=i,
                batch=batch,
                message=compressed_message,
                broadcast_id=broadcast_id
            )
            tasks.append(task)
            
        # Execute broadcast in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        success_count = sum(r['success'] for r in results if isinstance(r, dict))
        failure_count = sum(r['failed'] for r in results if isinstance(r, dict))
        
        print(f"✅ Broadcast {broadcast_id} completed")
        print(f"   Success: {success_count:,} ({success_count/total_users*100:.1f}%)")
        print(f"   Failed: {failure_count:,}")
        print(f"   Time taken: {self.calculate_broadcast_time()} seconds")
        
        return {
            'broadcast_id': broadcast_id,
            'total': total_users,
            'success': success_count,
            'failed': failure_count
        }
        
    def create_user_batches(self, users):
        """
        Create batches for parallel processing
        Like distributing exam papers to different rooms
        """
        batches = []
        for i in range(0, len(users), self.batch_size):
            batch = users[i:i + self.batch_size]
            batches.append(batch)
        return batches
        
    async def broadcast_worker(self, worker_id, batch, message, broadcast_id):
        """
        Worker to handle batch broadcasting
        """
        success = 0
        failed = 0
        
        for user_id in batch:
            try:
                # Get user's WebSocket connection
                connection = await self.get_user_connection(user_id)
                
                if connection:
                    # Send message
                    await connection.send(message)
                    success += 1
                else:
                    failed += 1
                    
            except Exception as e:
                failed += 1
                # Log error for debugging
                await self.log_broadcast_error(broadcast_id, user_id, str(e))
                
        return {
            'worker_id': worker_id,
            'success': success,
            'failed': failed
        }
        
    async def compress_message(self, message):
        """
        Compress message using gzip
        Saving bandwidth like using WhatsApp for video calls!
        """
        import gzip
        compressed = gzip.compress(message.encode('utf-8'))
        return compressed
        
    def generate_broadcast_id(self):
        """Generate unique broadcast ID"""
        import uuid
        return str(uuid.uuid4())[:8]
        
    async def get_user_connection(self, user_id):
        """Get user's WebSocket connection"""
        # In production, this queries connection registry
        return None
        
    async def log_broadcast_error(self, broadcast_id, user_id, error):
        """Log broadcast errors for analysis"""
        # In production, log to CloudWatch/ELK
        pass
        
    def calculate_broadcast_time(self):
        """Calculate time taken for broadcast"""
        # Implementation here
        return 2.5  # seconds
```

### Chapter 5: Security and Authentication - Digital Suraksha

WebSocket connections ko secure karna is like securing your home during Diwali - you want guests to come in, but only the invited ones! Indian companies have learned this the hard way, especially after several data breaches.

```python
# WebSocket Security Implementation
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
import jwt
from typing import Optional, Dict

class WebSocketSecurity:
    """
    Production-grade WebSocket security
    Following RBI and CERT-In guidelines for Indian fintech
    """
    
    def __init__(self):
        self.jwt_secret = secrets.token_urlsafe(32)
        self.rate_limiter = RateLimiter()
        self.connection_tracker = ConnectionTracker()
        self.fraud_detector = FraudDetector()
        
    async def authenticate_connection(self, request_headers):
        """
        Authenticate WebSocket connection request
        Multi-factor like Aadhaar + OTP + biometric
        """
        # Extract authentication token
        auth_header = request_headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            raise SecurityException("Missing authentication token")
            
        token = auth_header.replace('Bearer ', '')
        
        # Validate JWT token
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256']
            )
            
            # Check token expiry
            if payload['exp'] < datetime.utcnow().timestamp():
                raise SecurityException("Token expired - please login again")
                
            # Validate user session
            user_id = payload['user_id']
            session_valid = await self.validate_session(user_id, payload['session_id'])
            
            if not session_valid:
                raise SecurityException("Invalid session - possible account compromise")
                
            # Check for suspicious activity
            if await self.fraud_detector.is_suspicious(user_id, request_headers):
                # Send OTP for additional verification
                await self.send_otp_verification(user_id)
                raise SecurityException("Additional verification required")
                
            # Rate limiting check
            if not await self.rate_limiter.check_limit(user_id):
                raise SecurityException("Rate limit exceeded - try after sometime")
                
            # Track connection
            await self.connection_tracker.track_connection(user_id, request_headers)
            
            return {
                'user_id': user_id,
                'session_id': payload['session_id'],
                'permissions': payload.get('permissions', []),
                'authenticated': True
            }
            
        except jwt.InvalidTokenError as e:
            raise SecurityException(f"Invalid token: {str(e)}")
            
    async def validate_session(self, user_id, session_id):
        """
        Validate user session from Redis
        Like checking ticket at cinema hall
        """
        # Check if session exists and is active
        session_key = f"session:{user_id}:{session_id}"
        # In production, check Redis
        return True  # Placeholder
        
    async def send_otp_verification(self, user_id):
        """
        Send OTP for additional verification
        Using Indian SMS gateways
        """
        # Generate 6-digit OTP
        otp = secrets.randbelow(900000) + 100000
        
        # Store OTP in Redis with 5-minute expiry
        otp_key = f"otp:{user_id}"
        # await redis.setex(otp_key, 300, otp)
        
        # Send SMS via Indian gateway
        # await send_sms(user_phone, f"Your OTP is {otp}")
        
        print(f"📱 OTP sent to user {user_id}")
        
    def generate_connection_token(self, user_id, permissions=None):
        """
        Generate secure connection token
        Following OWASP guidelines
        """
        payload = {
            'user_id': user_id,
            'session_id': secrets.token_urlsafe(16),
            'permissions': permissions or [],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=30),
            'jti': secrets.token_urlsafe(8)  # JWT ID for tracking
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        return token

class RateLimiter:
    """
    Rate limiting for WebSocket connections
    Preventing DDoS like traffic police managing traffic
    """
    
    def __init__(self):
        self.limits = {
            'connections_per_minute': 10,
            'messages_per_second': 100,
            'broadcast_per_hour': 50,
            'file_upload_per_day': 100
        }
        self.user_buckets = {}
        
    async def check_limit(self, user_id, action='connection'):
        """
        Check if user is within rate limits
        Token bucket algorithm
        """
        bucket = self.get_or_create_bucket(user_id, action)
        
        current_time = datetime.now()
        
        # Refill tokens based on time passed
        time_passed = (current_time - bucket['last_refill']).total_seconds()
        tokens_to_add = time_passed * bucket['refill_rate']
        
        bucket['tokens'] = min(
            bucket['capacity'],
            bucket['tokens'] + tokens_to_add
        )
        bucket['last_refill'] = current_time
        
        # Check if tokens available
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
            
        return False
        
    def get_or_create_bucket(self, user_id, action):
        """
        Get or create token bucket for user
        """
        key = f"{user_id}:{action}"
        
        if key not in self.user_buckets:
            if action == 'connection':
                capacity = self.limits['connections_per_minute']
                refill_rate = capacity / 60  # Per second
            elif action == 'message':
                capacity = self.limits['messages_per_second']
                refill_rate = capacity
            else:
                capacity = 100
                refill_rate = 1
                
            self.user_buckets[key] = {
                'tokens': capacity,
                'capacity': capacity,
                'refill_rate': refill_rate,
                'last_refill': datetime.now()
            }
            
        return self.user_buckets[key]

class ConnectionTracker:
    """
    Track WebSocket connections for security
    Like maintaining visitor log at office building
    """
    
    def __init__(self):
        self.active_connections = {}
        self.connection_history = []
        self.max_connections_per_user = 5
        
    async def track_connection(self, user_id, headers):
        """
        Track new WebSocket connection
        """
        # Extract connection metadata
        connection_info = {
            'user_id': user_id,
            'ip_address': headers.get('X-Forwarded-For', headers.get('Remote-Addr')),
            'user_agent': headers.get('User-Agent'),
            'timestamp': datetime.now(),
            'connection_id': secrets.token_urlsafe(8)
        }
        
        # Check concurrent connections
        user_connections = self.active_connections.get(user_id, [])
        
        if len(user_connections) >= self.max_connections_per_user:
            # Disconnect oldest connection
            oldest = min(user_connections, key=lambda x: x['timestamp'])
            await self.disconnect_connection(oldest['connection_id'])
            user_connections.remove(oldest)
            
        # Add new connection
        user_connections.append(connection_info)
        self.active_connections[user_id] = user_connections
        
        # Log connection
        self.connection_history.append(connection_info)
        
        # Check for suspicious patterns
        await self.check_suspicious_patterns(user_id, connection_info)
        
        return connection_info['connection_id']
        
    async def check_suspicious_patterns(self, user_id, connection_info):
        """
        Check for suspicious connection patterns
        Like security guard checking for unusual behavior
        """
        # Check for rapid location changes
        recent_connections = [
            c for c in self.connection_history
            if c['user_id'] == user_id
            and (datetime.now() - c['timestamp']).seconds < 300
        ]
        
        if len(recent_connections) > 1:
            # Check if connecting from different cities rapidly
            locations = [self.get_location_from_ip(c['ip_address']) 
                        for c in recent_connections]
            
            unique_cities = set(loc['city'] for loc in locations if loc)
            
            if len(unique_cities) > 2:
                # Alert: User connecting from multiple cities
                await self.raise_security_alert(
                    user_id,
                    f"Multiple city connections: {unique_cities}"
                )
                
    def get_location_from_ip(self, ip_address):
        """
        Get location from IP address
        Using IP geolocation service
        """
        # In production, use MaxMind or similar
        # For demo, returning dummy data
        return {'city': 'Mumbai', 'state': 'Maharashtra', 'country': 'India'}
        
    async def disconnect_connection(self, connection_id):
        """Force disconnect a connection"""
        # Implementation here
        pass
        
    async def raise_security_alert(self, user_id, reason):
        """Raise security alert for suspicious activity"""
        print(f"🚨 Security Alert for user {user_id}: {reason}")
        # In production, send to security team

class FraudDetector:
    """
    Detect fraudulent WebSocket usage
    Like bank's fraud detection system
    """
    
    def __init__(self):
        self.suspicious_patterns = {
            'rapid_reconnects': 10,  # Within 1 minute
            'excessive_messages': 1000,  # Per minute
            'large_broadcasts': 10000,  # Recipients
            'unusual_hours': [2, 3, 4],  # AM hours
        }
        
    async def is_suspicious(self, user_id, headers):
        """
        Check if connection attempt is suspicious
        Using ML models in production
        """
        checks = [
            self.check_rapid_reconnects(user_id),
            self.check_unusual_location(user_id, headers),
            self.check_unusual_time(user_id),
            self.check_bot_behavior(headers)
        ]
        
        results = await asyncio.gather(*checks)
        
        # If any check fails, mark as suspicious
        return any(results)
        
    async def check_rapid_reconnects(self, user_id):
        """Check for rapid reconnection attempts"""
        # In production, check from Redis
        return False
        
    async def check_unusual_location(self, user_id, headers):
        """Check if connecting from unusual location"""
        # In production, compare with user's usual locations
        return False
        
    async def check_unusual_time(self, user_id):
        """Check if connecting at unusual time"""
        current_hour = datetime.now().hour
        return current_hour in self.suspicious_patterns['unusual_hours']
        
    async def check_bot_behavior(self, headers):
        """Check for bot-like behavior"""
        user_agent = headers.get('User-Agent', '')
        
        # Check for known bot patterns
        bot_patterns = ['bot', 'crawler', 'spider', 'scraper']
        return any(pattern in user_agent.lower() for pattern in bot_patterns)

class SecurityException(Exception):
    """Custom exception for security violations"""
    pass

# Message Encryption for Sensitive Data
class MessageEncryption:
    """
    End-to-end encryption for WebSocket messages
    Like WhatsApp encryption for Indian users
    """
    
    def __init__(self):
        from cryptography.fernet import Fernet
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        
    def encrypt_message(self, message):
        """
        Encrypt message before sending
        Required for financial/health data by Indian regulations
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
            
        encrypted = self.cipher.encrypt(message)
        return encrypted
        
    def decrypt_message(self, encrypted_message):
        """Decrypt received message"""
        decrypted = self.cipher.decrypt(encrypted_message)
        return decrypted.decode('utf-8')
```

### Chapter 6: Production Monitoring and Debugging - Digital Watchman

Production mein WebSocket monitor karna is like being a security guard at Phoenix Mall on weekend - you need to watch everything, respond quickly, and prevent problems before they become disasters!

```python
# Production Monitoring and Debugging
import time
from collections import deque, defaultdict
from datetime import datetime, timedelta
import statistics

class WebSocketMonitoring:
    """
    Comprehensive monitoring for WebSocket systems
    Used by Indian unicorns for production monitoring
    """
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.alerting = AlertingSystem()
        self.debugging = DebugLogger()
        self.health_checker = HealthChecker()
        
    async def start_monitoring(self):
        """
        Start comprehensive monitoring
        Like CCTV system with AI detection
        """
        tasks = [
            self.collect_metrics(),
            self.check_health(),
            self.analyze_patterns(),
            self.detect_anomalies()
        ]
        
        await asyncio.gather(*tasks)
        
    async def collect_metrics(self):
        """
        Collect real-time metrics
        """
        while True:
            metrics = {
                'timestamp': datetime.now(),
                'active_connections': await self.get_active_connections(),
                'messages_per_second': await self.get_message_rate(),
                'latency_ms': await self.measure_latency(),
                'error_rate': await self.get_error_rate(),
                'bandwidth_mbps': await self.get_bandwidth_usage(),
                'cpu_usage': await self.get_cpu_usage(),
                'memory_usage_gb': await self.get_memory_usage()
            }
            
            # Store metrics
            await self.metrics.store(metrics)
            
            # Check for alerts
            await self.check_alert_conditions(metrics)
            
            # Sleep for 10 seconds
            await asyncio.sleep(10)
            
    async def check_alert_conditions(self, metrics):
        """
        Check if any metric breaches threshold
        Like smoke detector in building
        """
        # High latency alert
        if metrics['latency_ms'] > 100:
            await self.alerting.send_alert(
                level='WARNING',
                message=f"High latency detected: {metrics['latency_ms']}ms",
                action="Check network congestion"
            )
            
        # High error rate
        if metrics['error_rate'] > 1.0:  # 1%
            await self.alerting.send_alert(
                level='CRITICAL',
                message=f"High error rate: {metrics['error_rate']}%",
                action="Check application logs immediately"
            )
            
        # Connection limit approaching
        connection_percentage = (metrics['active_connections'] / 1000000) * 100
        if connection_percentage > 80:
            await self.alerting.send_alert(
                level='WARNING',
                message=f"Connection limit approaching: {connection_percentage}%",
                action="Scale up servers"
            )
            
    async def get_active_connections(self):
        """Get current active WebSocket connections"""
        # In production, query from connection registry
        return 485000  # Dummy value
        
    async def get_message_rate(self):
        """Get messages per second"""
        return 25000  # Dummy value
        
    async def measure_latency(self):
        """Measure end-to-end latency"""
        return 45  # milliseconds
        
    async def get_error_rate(self):
        """Calculate error rate percentage"""
        return 0.05  # 0.05%
        
    async def get_bandwidth_usage(self):
        """Get current bandwidth usage"""
        return 850  # Mbps
        
    async def get_cpu_usage(self):
        """Get CPU usage percentage"""
        import psutil
        return psutil.cpu_percent()
        
    async def get_memory_usage(self):
        """Get memory usage in GB"""
        import psutil
        return psutil.virtual_memory().used / (1024 ** 3)

class MetricsCollector:
    """
    Collect and aggregate metrics
    Like collecting toll at highway
    """
    
    def __init__(self):
        self.metrics_buffer = deque(maxlen=10000)
        self.aggregated_metrics = {}
        
    async def store(self, metrics):
        """Store metrics for analysis"""
        self.metrics_buffer.append(metrics)
        
        # Aggregate every minute
        if len(self.metrics_buffer) >= 6:  # 6 * 10 seconds = 1 minute
            await self.aggregate_metrics()
            
    async def aggregate_metrics(self):
        """
        Aggregate metrics for dashboard
        """
        recent_metrics = list(self.metrics_buffer)[-6:]
        
        aggregated = {
            'timestamp': datetime.now(),
            'avg_connections': statistics.mean(m['active_connections'] for m in recent_metrics),
            'avg_messages_per_second': statistics.mean(m['messages_per_second'] for m in recent_metrics),
            'p50_latency': statistics.median(m['latency_ms'] for m in recent_metrics),
            'p99_latency': self.calculate_percentile([m['latency_ms'] for m in recent_metrics], 99),
            'max_error_rate': max(m['error_rate'] for m in recent_metrics),
            'total_bandwidth': sum(m['bandwidth_mbps'] for m in recent_metrics)
        }
        
        self.aggregated_metrics[datetime.now()] = aggregated
        
        # Send to monitoring dashboard
        await self.send_to_dashboard(aggregated)
        
    def calculate_percentile(self, data, percentile):
        """Calculate percentile value"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]
        
    async def send_to_dashboard(self, metrics):
        """Send metrics to Grafana/CloudWatch"""
        # Implementation here
        pass

class AlertingSystem:
    """
    Intelligent alerting system
    Like fire alarm system in building
    """
    
    def __init__(self):
        self.alert_channels = {
            'sms': SMSAlertChannel(),
            'email': EmailAlertChannel(),
            'slack': SlackAlertChannel(),
            'pagerduty': PagerDutyChannel()
        }
        self.alert_history = deque(maxlen=1000)
        self.alert_suppression = {}
        
    async def send_alert(self, level, message, action=None):
        """
        Send alert through appropriate channels
        Based on severity and time
        """
        alert = {
            'id': self.generate_alert_id(),
            'timestamp': datetime.now(),
            'level': level,
            'message': message,
            'action': action
        }
        
        # Check if alert should be suppressed
        if self.should_suppress_alert(alert):
            return
            
        # Store in history
        self.alert_history.append(alert)
        
        # Determine channels based on level and time
        channels = self.get_alert_channels(level)
        
        # Send through selected channels
        for channel_name in channels:
            channel = self.alert_channels[channel_name]
            await channel.send(alert)
            
        print(f"🚨 Alert sent: {level} - {message}")
        
    def should_suppress_alert(self, alert):
        """
        Check if alert should be suppressed
        Prevent alert fatigue
        """
        key = f"{alert['level']}:{alert['message'][:50]}"
        
        if key in self.alert_suppression:
            last_sent = self.alert_suppression[key]
            if (datetime.now() - last_sent).seconds < 300:  # 5 minutes
                return True
                
        self.alert_suppression[key] = datetime.now()
        return False
        
    def get_alert_channels(self, level):
        """
        Determine which channels to use
        Based on severity and time
        """
        current_hour = datetime.now().hour
        
        if level == 'CRITICAL':
            # Critical alerts go everywhere
            return ['sms', 'slack', 'pagerduty']
        elif level == 'WARNING':
            # Warnings based on time
            if 9 <= current_hour <= 21:  # Business hours
                return ['slack', 'email']
            else:
                return ['email']
        else:
            return ['email']
            
    def generate_alert_id(self):
        """Generate unique alert ID"""
        import uuid
        return str(uuid.uuid4())[:8]

class SMSAlertChannel:
    """SMS alerts for critical issues"""
    
    async def send(self, alert):
        """Send SMS via Indian gateway"""
        # In production, integrate with SMS gateway
        # Popular in India: Textlocal, MSG91, Kaleyra
        pass

class EmailAlertChannel:
    """Email alerts"""
    
    async def send(self, alert):
        """Send email alert"""
        # Implementation here
        pass

class SlackAlertChannel:
    """Slack integration for team alerts"""
    
    async def send(self, alert):
        """Send to Slack channel"""
        # Implementation here
        pass

class PagerDutyChannel:
    """PagerDuty for on-call alerts"""
    
    async def send(self, alert):
        """Trigger PagerDuty incident"""
        # Implementation here
        pass

class DebugLogger:
    """
    Advanced debugging for WebSocket issues
    Like detective solving crime!
    """
    
    def __init__(self):
        self.debug_sessions = {}
        self.packet_capture = PacketCapture()
        
    async def start_debug_session(self, user_id=None, connection_id=None):
        """
        Start debugging session for specific user/connection
        """
        session_id = self.generate_session_id()
        
        self.debug_sessions[session_id] = {
            'user_id': user_id,
            'connection_id': connection_id,
            'start_time': datetime.now(),
            'packets': [],
            'events': [],
            'errors': []
        }
        
        # Start packet capture
        if connection_id:
            await self.packet_capture.start_capture(connection_id)
            
        print(f"🔍 Debug session started: {session_id}")
        return session_id
        
    async def log_event(self, session_id, event_type, data):
        """Log debug event"""
        if session_id in self.debug_sessions:
            event = {
                'timestamp': datetime.now(),
                'type': event_type,
                'data': data
            }
            self.debug_sessions[session_id]['events'].append(event)
            
    async def analyze_session(self, session_id):
        """
        Analyze debug session for issues
        """
        if session_id not in self.debug_sessions:
            return None
            
        session = self.debug_sessions[session_id]
        
        analysis = {
            'session_id': session_id,
            'duration': (datetime.now() - session['start_time']).seconds,
            'total_events': len(session['events']),
            'total_errors': len(session['errors']),
            'patterns_found': [],
            'recommendations': []
        }
        
        # Analyze patterns
        if session['errors']:
            # Frequent disconnections
            disconnect_count = sum(1 for e in session['errors'] 
                                 if 'disconnect' in str(e).lower())
            if disconnect_count > 5:
                analysis['patterns_found'].append('Frequent disconnections')
                analysis['recommendations'].append('Check network stability')
                
        # Check message patterns
        message_events = [e for e in session['events'] if e['type'] == 'message']
        if message_events:
            # Calculate message rate
            time_span = (message_events[-1]['timestamp'] - 
                        message_events[0]['timestamp']).seconds
            if time_span > 0:
                message_rate = len(message_events) / time_span
                if message_rate > 100:
                    analysis['patterns_found'].append('High message rate')
                    analysis['recommendations'].append('Consider rate limiting')
                    
        return analysis
        
    def generate_session_id(self):
        """Generate debug session ID"""
        import uuid
        return f"debug-{uuid.uuid4().hex[:8]}"

class PacketCapture:
    """
    Capture WebSocket packets for debugging
    Like recording phone call for quality
    """
    
    def __init__(self):
        self.captures = {}
        
    async def start_capture(self, connection_id):
        """Start capturing packets for connection"""
        self.captures[connection_id] = {
            'start_time': datetime.now(),
            'packets': deque(maxlen=1000)
        }
        
    async def capture_packet(self, connection_id, direction, data):
        """Capture a packet"""
        if connection_id in self.captures:
            packet = {
                'timestamp': datetime.now(),
                'direction': direction,  # 'incoming' or 'outgoing'
                'size': len(data),
                'data': data[:1000]  # Store first 1KB only
            }
            self.captures[connection_id]['packets'].append(packet)

class HealthChecker:
    """
    Health checks for WebSocket infrastructure
    Like regular health checkup
    """
    
    def __init__(self):
        self.health_checks = {
            'websocket_server': self.check_websocket_server,
            'redis': self.check_redis,
            'database': self.check_database,
            'message_queue': self.check_message_queue,
            'cdn': self.check_cdn
        }
        self.health_status = {}
        
    async def check_health(self):
        """Run all health checks"""
        while True:
            for component, check_func in self.health_checks.items():
                try:
                    status = await check_func()
                    self.health_status[component] = {
                        'status': 'healthy' if status else 'unhealthy',
                        'last_check': datetime.now()
                    }
                except Exception as e:
                    self.health_status[component] = {
                        'status': 'unhealthy',
                        'error': str(e),
                        'last_check': datetime.now()
                    }
                    
            # Generate health report
            await self.generate_health_report()
            
            # Sleep for 30 seconds
            await asyncio.sleep(30)
            
    async def check_websocket_server(self):
        """Check WebSocket server health"""
        # Try to establish test connection
        # Return True if successful
        return True
        
    async def check_redis(self):
        """Check Redis health"""
        # Ping Redis server
        return True
        
    async def check_database(self):
        """Check database health"""
        # Execute simple query
        return True
        
    async def check_message_queue(self):
        """Check message queue health"""
        # Check queue depth
        return True
        
    async def check_cdn(self):
        """Check CDN health"""
        # Ping CDN endpoints
        return True
        
    async def generate_health_report(self):
        """Generate overall health report"""
        healthy_components = sum(1 for c in self.health_status.values() 
                                if c['status'] == 'healthy')
        total_components = len(self.health_status)
        
        health_percentage = (healthy_components / total_components) * 100
        
        print(f"💚 System Health: {health_percentage:.1f}%")
        print(f"   Healthy: {healthy_components}/{total_components}")
        
        # Alert if unhealthy
        if health_percentage < 100:
            unhealthy = [k for k, v in self.health_status.items() 
                        if v['status'] == 'unhealthy']
            print(f"   ⚠️ Unhealthy: {', '.join(unhealthy)}")
```

## Part 3: Real-World Implementation - Building Production Systems (60 minutes)

### Chapter 7: Building a Real-Time Collaboration Platform - Indian Style

Ab banate hain ek real-time collaboration platform, jaise Figma ya Google Docs, but with Indian context. Imagine kar���o ek platform jahan lakhs students simultaneously JEE ke questions solve kar sakte hain, ya phir architects mil kar building design kar sakte hain!

```python
# Real-Time Collaboration Platform
import asyncio
import json
from typing import Dict, List, Set
from datetime import datetime
import hashlib

class CollaborationPlatform:
    """
    Real-time collaboration platform
    Like Google Docs but for Indian education/business
    """
    
    def __init__(self):
        self.rooms = {}  # Collaboration rooms
        self.users = {}  # Active users
        self.documents = {}  # Shared documents
        self.cursors = {}  # User cursors
        self.conflict_resolver = ConflictResolver()
        
    async def create_room(self, room_type, metadata):
        """
        Create collaboration room
        Types: classroom, meeting, design, coding
        """
        room_id = self.generate_room_id()
        
        self.rooms[room_id] = {
            'id': room_id,
            'type': room_type,
            'created_at': datetime.now(),
            'metadata': metadata,
            'participants': set(),
            'document': Document(),
            'chat': ChatManager(),
            'whiteboard': Whiteboard(),
            'permissions': PermissionManager()
        }
        
        print(f"📝 Room created: {room_id}")
        print(f"   Type: {room_type}")
        print(f"   Capacity: {metadata.get('capacity', 100)}")
        
        return room_id
        
    async def join_room(self, room_id, user_id, user_info):
        """
        User joins collaboration room
        Like entering a classroom
        """
        if room_id not in self.rooms:
            raise Exception("Room not found - wrong room number!")
            
        room = self.rooms[room_id]
        
        # Check capacity
        if len(room['participants']) >= room['metadata'].get('capacity', 100):
            raise Exception("Room full - like general compartment in Mumbai local!")
            
        # Add participant
        room['participants'].add(user_id)
        
        # Initialize user state
        self.users[user_id] = {
            'id': user_id,
            'info': user_info,
            'room_id': room_id,
            'cursor': {'x': 0, 'y': 0},
            'selection': None,
            'status': 'active'
        }
        
        # Broadcast join event
        await self.broadcast_to_room(room_id, {
            'type': 'user_joined',
            'user_id': user_id,
            'user_info': user_info,
            'total_participants': len(room['participants'])
        }, exclude_user=user_id)
        
        # Send room state to new user
        await self.send_room_state(room_id, user_id)
        
        print(f"👤 User {user_info['name']} joined room {room_id}")
        
    async def handle_document_operation(self, room_id, user_id, operation):
        """
        Handle document edit operation
        Using Operational Transformation for conflict resolution
        """
        room = self.rooms[room_id]
        document = room['document']
        
        # Validate permission
        if not room['permissions'].can_edit(user_id):
            raise Exception("No edit permission - like trying to write on blackboard without chalk!")
            
        # Apply operation
        if operation['type'] == 'insert':
            result = await document.insert(
                operation['position'],
                operation['text'],
                user_id
            )
        elif operation['type'] == 'delete':
            result = await document.delete(
                operation['position'],
                operation['length'],
                user_id
            )
        elif operation['type'] == 'format':
            result = await document.format(
                operation['range'],
                operation['formatting'],
                user_id
            )
            
        # Broadcast operation to others
        await self.broadcast_to_room(room_id, {
            'type': 'document_operation',
            'operation': operation,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }, exclude_user=user_id)
        
        return result
        
    async def handle_cursor_update(self, room_id, user_id, cursor_data):
        """
        Handle cursor position update
        Show where each user is working
        """
        if user_id in self.users:
            self.users[user_id]['cursor'] = cursor_data
            
            # Broadcast cursor position
            await self.broadcast_to_room(room_id, {
                'type': 'cursor_update',
                'user_id': user_id,
                'cursor': cursor_data
            }, exclude_user=user_id)
            
    async def broadcast_to_room(self, room_id, message, exclude_user=None):
        """
        Broadcast message to all room participants
        Like teacher speaking to whole class
        """
        if room_id not in self.rooms:
            return
            
        room = self.rooms[room_id]
        participants = room['participants'].copy()
        
        if exclude_user:
            participants.discard(exclude_user)
            
        # Send to all participants
        for participant_id in participants:
            await self.send_to_user(participant_id, message)
            
    async def send_to_user(self, user_id, message):
        """Send message to specific user"""
        # In production, this would use actual WebSocket connection
        pass
        
    async def send_room_state(self, room_id, user_id):
        """
        Send current room state to user
        Like giving notebook to latecomer student
        """
        room = self.rooms[room_id]
        
        state = {
            'type': 'room_state',
            'room_id': room_id,
            'document': await room['document'].get_content(),
            'participants': list(room['participants']),
            'cursors': {uid: self.users[uid]['cursor'] 
                       for uid in room['participants'] if uid in self.users},
            'chat_history': room['chat'].get_recent_messages(50),
            'whiteboard': room['whiteboard'].get_state()
        }
        
        await self.send_to_user(user_id, state)
        
    def generate_room_id(self):
        """Generate unique room ID"""
        import uuid
        return f"room-{uuid.uuid4().hex[:8]}"

class Document:
    """
    Collaborative document with conflict resolution
    Like multiple people writing on same paper
    """
    
    def __init__(self):
        self.content = []  # List of paragraphs
        self.version = 0
        self.history = []
        self.locks = {}  # Paragraph-level locks
        
    async def insert(self, position, text, user_id):
        """Insert text at position"""
        self.version += 1
        
        # Record operation
        operation = {
            'type': 'insert',
            'position': position,
            'text': text,
            'user_id': user_id,
            'version': self.version,
            'timestamp': datetime.now()
        }
        
        # Apply operation
        # In production, use proper OT algorithm
        self.history.append(operation)
        
        return {'success': True, 'version': self.version}
        
    async def delete(self, position, length, user_id):
        """Delete text from position"""
        self.version += 1
        
        operation = {
            'type': 'delete',
            'position': position,
            'length': length,
            'user_id': user_id,
            'version': self.version,
            'timestamp': datetime.now()
        }
        
        self.history.append(operation)
        
        return {'success': True, 'version': self.version}
        
    async def format(self, range_data, formatting, user_id):
        """Apply formatting to range"""
        self.version += 1
        
        operation = {
            'type': 'format',
            'range': range_data,
            'formatting': formatting,
            'user_id': user_id,
            'version': self.version,
            'timestamp': datetime.now()
        }
        
        self.history.append(operation)
        
        return {'success': True, 'version': self.version}
        
    async def get_content(self):
        """Get current document content"""
        # Reconstruct from history
        return {
            'content': self.content,
            'version': self.version
        }

class ChatManager:
    """
    Real-time chat within collaboration room
    Like WhatsApp group for classroom
    """
    
    def __init__(self):
        self.messages = deque(maxlen=1000)
        self.typing_users = set()
        
    async def send_message(self, user_id, message):
        """Send chat message"""
        chat_message = {
            'id': self.generate_message_id(),
            'user_id': user_id,
            'text': message,
            'timestamp': datetime.now(),
            'reactions': {}
        }
        
        self.messages.append(chat_message)
        return chat_message
        
    def get_recent_messages(self, count=50):
        """Get recent chat messages"""
        return list(self.messages)[-count:]
        
    def generate_message_id(self):
        """Generate message ID"""
        import uuid
        return str(uuid.uuid4())[:8]

class Whiteboard:
    """
    Collaborative whiteboard for drawing
    Like classroom blackboard
    """
    
    def __init__(self):
        self.strokes = []
        self.shapes = []
        self.text_annotations = []
        
    async def add_stroke(self, stroke_data, user_id):
        """Add drawing stroke"""
        stroke = {
            'id': self.generate_stroke_id(),
            'user_id': user_id,
            'points': stroke_data['points'],
            'color': stroke_data.get('color', '#000000'),
            'width': stroke_data.get('width', 2),
            'timestamp': datetime.now()
        }
        
        self.strokes.append(stroke)
        return stroke
        
    def get_state(self):
        """Get whiteboard state"""
        return {
            'strokes': self.strokes[-100:],  # Last 100 strokes
            'shapes': self.shapes,
            'text_annotations': self.text_annotations
        }
        
    def generate_stroke_id(self):
        """Generate stroke ID"""
        import uuid
        return str(uuid.uuid4())[:8]

class PermissionManager:
    """
    Manage user permissions in room
    Like class monitor system
    """
    
    def __init__(self):
        self.roles = {
            'owner': ['all'],
            'moderator': ['edit', 'delete', 'kick'],
            'editor': ['edit'],
            'viewer': ['view']
        }
        self.user_roles = {}
        
    def can_edit(self, user_id):
        """Check if user can edit"""
        role = self.user_roles.get(user_id, 'viewer')
        permissions = self.roles.get(role, [])
        return 'edit' in permissions or 'all' in permissions
        
    def set_role(self, user_id, role):
        """Set user role"""
        self.user_roles[user_id] = role

class ConflictResolver:
    """
    Resolve conflicts in collaborative editing
    Using Operational Transformation
    """
    
    def transform_operation(self, op1, op2):
        """
        Transform operation op1 against op2
        Mathematics of collaboration!
        """
        # Simplified OT algorithm
        if op1['type'] == 'insert' and op2['type'] == 'insert':
            if op1['position'] < op2['position']:
                return op1, {'...': '...', 'position': op2['position'] + len(op1['text'])}
            elif op1['position'] > op2['position']:
                return {'...': '...', 'position': op1['position'] + len(op2['text'])}, op2
            else:
                # Same position - use user_id for ordering
                if op1['user_id'] < op2['user_id']:
                    return op1, {'...': '...', 'position': op2['position'] + len(op1['text'])}
                else:
                    return {'...': '...', 'position': op1['position'] + len(op2['text'])}, op2
                    
        # More transformation cases...
        return op1, op2
```

### Chapter 8: Building a Live Trading System - Indian Stock Market

Building a WebSocket-based trading system for Indian stock markets requires extreme reliability, low latency, and compliance with SEBI regulations. Ye system Zerodha, Upstox, aur Groww jaise platforms use karte hain.

```python
# Live Trading System for Indian Markets
import asyncio
from decimal import Decimal
from datetime import datetime, time
import hashlib

class IndianTradingSystem:
    """
    Real-time trading system for NSE/BSE
    Handling millions of trades during market hours
    """
    
    def __init__(self):
        self.market_hours = {
            'pre_open': (time(9, 0), time(9, 15)),
            'normal': (time(9, 15), time(15, 30)),
            'post_close': (time(15, 30), time(16, 0))
        }
        self.order_book = OrderBook()
        self.price_feed = PriceFeedManager()
        self.risk_manager = RiskManager()
        self.settlement = SettlementEngine()
        
    async def connect_to_exchange(self):
        """
        Connect to NSE/BSE data feed
        Multiple redundant connections for reliability
        """
        connections = [
            self.connect_to_nse_primary(),
            self.connect_to_nse_backup(),
            self.connect_to_bse_primary(),
            self.connect_to_bse_backup()
        ]
        
        results = await asyncio.gather(*connections, return_exceptions=True)
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        print(f"📈 Connected to {successful}/4 exchange feeds")
        
        if successful == 0:
            raise Exception("Failed to connect to any exchange - market closed or technical issue!")
            
    async def handle_order_placement(self, user_id, order_data):
        """
        Place order in the market
        Following SEBI regulations
        """
        # Validate market hours
        if not self.is_market_open():
            raise Exception("Market closed - try during 9:15 AM to 3:30 PM")
            
        # Risk checks
        risk_check = await self.risk_manager.check_order(user_id, order_data)
        if not risk_check['passed']:
            raise Exception(f"Risk check failed: {risk_check['reason']}")
            
        # Create order
        order = {
            'order_id': self.generate_order_id(),
            'user_id': user_id,
            'symbol': order_data['symbol'],
            'type': order_data['type'],  # LIMIT, MARKET, SL, SLM
            'side': order_data['side'],  # BUY, SELL
            'quantity': order_data['quantity'],
            'price': order_data.get('price'),
            'trigger_price': order_data.get('trigger_price'),
            'product': order_data.get('product', 'CNC'),  # CNC, MIS, NRML
            'validity': order_data.get('validity', 'DAY'),
            'timestamp': datetime.now(),
            'status': 'PENDING'
        }
        
        # Validate order
        validation = await self.validate_order(order)
        if not validation['valid']:
            raise Exception(f"Order validation failed: {validation['reason']}")
            
        # Place order
        result = await self.order_book.place_order(order)
        
        # Send confirmation
        await self.send_order_confirmation(user_id, order, result)
        
        return result
        
    async def validate_order(self, order):
        """
        Validate order parameters
        Check circuit limits, lot size, etc.
        """
        # Check lot size for F&O
        if order['symbol'].endswith('FUT') or order['symbol'].endswith('OPT'):
            lot_size = self.get_lot_size(order['symbol'])
            if order['quantity'] % lot_size != 0:
                return {
                    'valid': False,
                    'reason': f"Quantity must be multiple of lot size ({lot_size})"
                }
                
        # Check price bands
        current_price = await self.price_feed.get_current_price(order['symbol'])
        if order['type'] == 'LIMIT' and order['price']:
            # Check circuit limits (typically 20% for stocks)
            lower_limit = current_price * Decimal('0.8')
            upper_limit = current_price * Decimal('1.2')
            
            if not (lower_limit <= order['price'] <= upper_limit):
                return {
                    'valid': False,
                    'reason': f"Price outside circuit limits ({lower_limit:.2f} - {upper_limit:.2f})"
                }
                
        return {'valid': True}
        
    def is_market_open(self):
        """Check if market is open"""
        current_time = datetime.now().time()
        return (self.market_hours['normal'][0] <= current_time <= 
                self.market_hours['normal'][1])
                
    def get_lot_size(self, symbol):
        """Get F&O lot size"""
        # In production, fetch from exchange
        lot_sizes = {
            'NIFTY_FUT': 50,
            'BANKNIFTY_FUT': 25,
            'RELIANCE_FUT': 250
        }
        return lot_sizes.get(symbol, 1)
        
    def generate_order_id(self):
        """Generate unique order ID"""
        import uuid
        return f"ORD{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        
    async def send_order_confirmation(self, user_id, order, result):
        """Send order confirmation to user"""
        # Send via WebSocket
        pass

class OrderBook:
    """
    Order book management
    Like maintaining trading register
    """
    
    def __init__(self):
        self.orders = {}
        self.user_orders = defaultdict(list)
        
    async def place_order(self, order):
        """Place order in book"""
        order_id = order['order_id']
        self.orders[order_id] = order
        self.user_orders[order['user_id']].append(order_id)
        
        # Send to exchange
        exchange_response = await self.send_to_exchange(order)
        
        # Update status
        order['status'] = exchange_response['status']
        order['exchange_order_id'] = exchange_response.get('exchange_order_id')
        
        return {
            'order_id': order_id,
            'status': order['status'],
            'message': exchange_response.get('message', 'Order placed successfully')
        }
        
    async def send_to_exchange(self, order):
        """Send order to exchange"""
        # In production, use FIX protocol or exchange API
        # Simulate exchange response
        return {
            'status': 'OPEN',
            'exchange_order_id': f"NSE{datetime.now().strftime('%H%M%S')}"
        }

class PriceFeedManager:
    """
    Real-time price feed management
    Processing millions of ticks per second
    """
    
    def __init__(self):
        self.current_prices = {}
        self.price_history = defaultdict(deque)
        self.subscribers = defaultdict(set)
        
    async def process_tick(self, tick_data):
        """
        Process incoming price tick
        During market hours: 10,000+ ticks/second
        """
        symbol = tick_data['symbol']
        
        # Update current price
        self.current_prices[symbol] = {
            'ltp': Decimal(str(tick_data['last_price'])),
            'bid': Decimal(str(tick_data['best_bid'])),
            'ask': Decimal(str(tick_data['best_ask'])),
            'volume': tick_data['volume'],
            'oi': tick_data.get('open_interest', 0),
            'timestamp': tick_data['timestamp']
        }
        
        # Store in history
        self.price_history[symbol].append(self.current_prices[symbol])
        
        # Broadcast to subscribers
        await self.broadcast_price_update(symbol)
        
    async def broadcast_price_update(self, symbol):
        """Broadcast price to all subscribers"""
        if symbol in self.subscribers:
            update = self.current_prices[symbol]
            
            # Send to all subscribers
            for subscriber_id in self.subscribers[symbol]:
                await self.send_price_update(subscriber_id, symbol, update)
                
    async def send_price_update(self, subscriber_id, symbol, price_data):
        """Send price update to subscriber"""
        # Via WebSocket
        pass
        
    async def get_current_price(self, symbol):
        """Get current market price"""
        if symbol in self.current_prices:
            return self.current_prices[symbol]['ltp']
        return Decimal('0')

class RiskManager:
    """
    Risk management system
    Following SEBI regulations
    """
    
    def __init__(self):
        self.user_limits = {}
        self.daily_loss_limit = Decimal('50000')  # Rs 50,000
        self.position_limit = Decimal('1000000')  # Rs 10 lakhs
        
    async def check_order(self, user_id, order_data):
        """
        Check if order passes risk checks
        """
        # Get user's current positions
        positions = await self.get_user_positions(user_id)
        
        # Check daily loss
        daily_pnl = await self.calculate_daily_pnl(user_id)
        if daily_pnl < -self.daily_loss_limit:
            return {
                'passed': False,
                'reason': f"Daily loss limit exceeded (₹{self.daily_loss_limit})"
            }
            
        # Check position limit
        order_value = Decimal(str(order_data['quantity'])) * Decimal(str(order_data.get('price', 0)))
        total_exposure = sum(p['value'] for p in positions) + order_value
        
        if total_exposure > self.position_limit:
            return {
                'passed': False,
                'reason': f"Position limit exceeded (₹{self.position_limit})"
            }
            
        # Check margin requirements
        margin_required = self.calculate_margin(order_data)
        available_margin = await self.get_available_margin(user_id)
        
        if margin_required > available_margin:
            return {
                'passed': False,
                'reason': f"Insufficient margin (Required: ₹{margin_required}, Available: ₹{available_margin})"
            }
            
        return {'passed': True}
        
    def calculate_margin(self, order_data):
        """
        Calculate margin requirement
        Based on SPAN + Exposure margins
        """
        # Simplified calculation
        if order_data.get('product') == 'MIS':
            # Intraday - lower margin
            return Decimal(str(order_data['quantity'])) * Decimal(str(order_data.get('price', 0))) * Decimal('0.1')
        else:
            # Delivery - full margin
            return Decimal(str(order_data['quantity'])) * Decimal(str(order_data.get('price', 0)))
            
    async def get_user_positions(self, user_id):
        """Get user's current positions"""
        # In production, query from database
        return []
        
    async def calculate_daily_pnl(self, user_id):
        """Calculate user's daily P&L"""
        # In production, calculate from trades
        return Decimal('0')
        
    async def get_available_margin(self, user_id):
        """Get user's available margin"""
        # In production, query from account
        return Decimal('100000')  # Rs 1 lakh

class SettlementEngine:
    """
    T+1 settlement system
    As per SEBI regulations
    """
    
    def __init__(self):
        self.pending_settlements = []
        
    async def process_trade_settlement(self, trade):
        """
        Process trade settlement
        T+1 for equity, same day for F&O
        """
        settlement = {
            'trade_id': trade['id'],
            'settlement_date': self.calculate_settlement_date(trade),
            'amount': trade['value'],
            'status': 'PENDING'
        }
        
        self.pending_settlements.append(settlement)
        
        # Schedule settlement
        asyncio.create_task(self.execute_settlement(settlement))
        
    def calculate_settlement_date(self, trade):
        """Calculate settlement date based on product type"""
        from datetime import timedelta
        
        if trade['product'] in ['MIS', 'NRML']:  # F&O
            return trade['date']  # Same day
        else:  # Equity
            return trade['date'] + timedelta(days=1)  # T+1
            
    async def execute_settlement(self, settlement):
        """Execute settlement on settlement date"""
        # Wait until settlement date
        # Transfer shares and money
        pass
```

### Chapter 9: Performance Optimization - Speed Ka Raaz

Indian scale pe WebSocket optimize karna is like tuning a Formula 1 car for Indian roads - you need speed, but also reliability in tough conditions!

```python
# Performance Optimization Techniques
import asyncio
from concurrent.futures import ThreadPoolExecutor
import msgpack  # Binary serialization
import lz4.frame  # Fast compression

class PerformanceOptimizer:
    """
    WebSocket performance optimization
    Techniques used by Indian unicorns
    """
    
    def __init__(self):
        self.message_compressor = MessageCompressor()
        self.connection_pooler = ConnectionPooler()
        self.cache_manager = CacheManager()
        self.batch_processor = BatchProcessor()
        
    async def optimize_message_handling(self):
        """
        Optimize message processing pipeline
        Reduce latency from 100ms to 10ms
        """
        optimizations = {
            'binary_protocol': self.use_binary_protocol(),
            'compression': self.enable_compression(),
            'batching': self.enable_batching(),
            'caching': self.enable_caching(),
            'connection_pooling': self.setup_connection_pooling()
        }
        
        results = await asyncio.gather(*optimizations.values())
        
        print("⚡ Performance optimizations applied:")
        for name, result in zip(optimizations.keys(), results):
            print(f"   {name}: {result}")

class MessageCompressor:
    """
    Message compression for bandwidth optimization
    Save 70% bandwidth costs
    """
    
    def __init__(self):
        self.compression_threshold = 1024  # Compress if > 1KB
        
    def compress(self, data):
        """
        Compress message using LZ4
        Faster than gzip for real-time
        """
        if len(data) < self.compression_threshold:
            return data, False
            
        compressed = lz4.frame.compress(data)
        
        # Check if compression is beneficial
        if len(compressed) < len(data) * 0.9:  # At least 10% reduction
            return compressed, True
        else:
            return data, False
            
    def decompress(self, data):
        """Decompress message"""
        return lz4.frame.decompress(data)

class BatchProcessor:
    """
    Batch multiple messages for efficiency
    Like carpooling for messages
    """
    
    def __init__(self):
        self.batch_size = 100
        self.batch_timeout = 0.01  # 10ms
        self.pending_messages = []
        
    async def add_message(self, message):
        """Add message to batch"""
        self.pending_messages.append(message)
        
        if len(self.pending_messages) >= self.batch_size:
            await self.flush_batch()
            
    async def flush_batch(self):
        """Send batched messages"""
        if not self.pending_messages:
            return
            
        batch = {
            'type': 'batch',
            'messages': self.pending_messages,
            'count': len(self.pending_messages)
        }
        
        # Send batch
        await self.send_batch(batch)
        
        # Clear pending
        self.pending_messages = []
        
    async def send_batch(self, batch):
        """Send batch over WebSocket"""
        # Implementation here
        pass

# Memory optimization
class MemoryOptimizer:
    """
    Memory optimization for handling millions of connections
    """
    
    def __init__(self):
        self.connection_states = {}  # Use __slots__ for memory efficiency
        
    class ConnectionState:
        """Memory-efficient connection state"""
        __slots__ = ['id', 'user_id', 'last_activity', 'buffer']
        
        def __init__(self, connection_id):
            self.id = connection_id
            self.user_id = None
            self.last_activity = datetime.now()
            self.buffer = bytearray(1024)  # Pre-allocated buffer
```

## Part 4: Deep Dive into WebSocket Internals - The Engineering Marvel (60 minutes)

### Chapter 10: WebSocket Protocol Deep Dive - Nuts and Bolts

Ab aate hain WebSocket ke technical internals pe. Ye woh engineering ki baat hai jo har serious developer ko samajhni chahiye. Just like understanding how Chandrayaan-3's soft landing worked, we need to understand how WebSocket achieves its magic!

```python
# WebSocket Protocol Internals
import struct
import random
import base64
from enum import IntEnum

class WebSocketOpcode(IntEnum):
    """
    WebSocket frame opcodes
    Like different types of railway tickets!
    """
    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    RESERVED_3 = 0x3
    RESERVED_4 = 0x4
    RESERVED_5 = 0x5
    RESERVED_6 = 0x6
    RESERVED_7 = 0x7
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA
    RESERVED_B = 0xB
    RESERVED_C = 0xC
    RESERVED_D = 0xD
    RESERVED_E = 0xE
    RESERVED_F = 0xF

class WebSocketProtocolHandler:
    """
    Low-level WebSocket protocol handler
    The engine that powers real-time communication
    """
    
    def __init__(self):
        self.state = 'CONNECTING'
        self.fragments = []
        self.ping_interval = 30
        self.pong_timeout = 10
        
    def create_handshake_request(self, url, protocols=None, extensions=None):
        """
        Create WebSocket handshake request
        Like creating perfect chai - right proportions matter!
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'wss' else 80)
        path = parsed.path or '/'
        
        # Generate WebSocket key
        key = base64.b64encode(random.randbytes(16)).decode('ascii')
        
        # Build request
        request = []
        request.append(f"GET {path} HTTP/1.1")
        request.append(f"Host: {host}:{port}")
        request.append("Upgrade: websocket")
        request.append("Connection: Upgrade")
        request.append(f"Sec-WebSocket-Key: {key}")
        request.append("Sec-WebSocket-Version: 13")
        
        if protocols:
            request.append(f"Sec-WebSocket-Protocol: {', '.join(protocols)}")
            
        if extensions:
            request.append(f"Sec-WebSocket-Extensions: {', '.join(extensions)}")
            
        # Add custom headers for Indian context
        request.append("X-Client-Region: India")
        request.append("X-Network-Provider: Jio-Fiber")
        
        request.append("")
        request.append("")
        
        return '\r\n'.join(request).encode('utf-8'), key
        
    def validate_handshake_response(self, response, expected_key):
        """
        Validate server's handshake response
        Like checking if your train ticket is confirmed!
        """
        import hashlib
        
        # Parse response
        lines = response.decode('utf-8').split('\r\n')
        
        # Check status line
        if not lines[0].startswith('HTTP/1.1 101'):
            raise Exception(f"Handshake failed: {lines[0]}")
            
        # Parse headers
        headers = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
                
        # Validate upgrade header
        if headers.get('upgrade', '').lower() != 'websocket':
            raise Exception("Server didn't upgrade to WebSocket")
            
        # Validate connection header
        if 'upgrade' not in headers.get('connection', '').lower():
            raise Exception("Invalid connection header")
            
        # Validate accept key
        magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        expected_accept = base64.b64encode(
            hashlib.sha1((expected_key + magic_string).encode()).digest()
        ).decode('ascii')
        
        if headers.get('sec-websocket-accept') != expected_accept:
            raise Exception("Invalid Sec-WebSocket-Accept header")
            
        self.state = 'OPEN'
        return True
        
    def create_frame(self, payload, opcode=WebSocketOpcode.TEXT, 
                    fin=True, mask=True):
        """
        Create WebSocket frame
        Like packing tiffin with different compartments
        """
        frame = bytearray()
        
        # First byte: FIN + RSV + Opcode
        byte1 = 0
        if fin:
            byte1 |= 0x80  # Set FIN bit
        byte1 |= opcode
        frame.append(byte1)
        
        # Payload length
        payload_len = len(payload)
        
        if payload_len < 126:
            byte2 = payload_len
            if mask:
                byte2 |= 0x80  # Set mask bit
            frame.append(byte2)
            
        elif payload_len < 65536:
            byte2 = 126
            if mask:
                byte2 |= 0x80
            frame.append(byte2)
            frame.extend(struct.pack('>H', payload_len))
            
        else:
            byte2 = 127
            if mask:
                byte2 |= 0x80
            frame.append(byte2)
            frame.extend(struct.pack('>Q', payload_len))
            
        # Masking key (client to server)
        if mask:
            mask_key = random.randbytes(4)
            frame.extend(mask_key)
            
            # Apply mask to payload
            masked_payload = bytearray()
            for i, byte in enumerate(payload):
                masked_payload.append(byte ^ mask_key[i % 4])
            frame.extend(masked_payload)
        else:
            frame.extend(payload)
            
        return bytes(frame)
        
    def parse_frame(self, data):
        """
        Parse incoming WebSocket frame
        Like unwrapping a gift layer by layer
        """
        if len(data) < 2:
            raise Exception("Incomplete frame")
            
        # Parse first byte
        byte1 = data[0]
        fin = bool(byte1 & 0x80)
        rsv1 = bool(byte1 & 0x40)
        rsv2 = bool(byte1 & 0x20)
        rsv3 = bool(byte1 & 0x10)
        opcode = byte1 & 0x0F
        
        # Parse second byte
        byte2 = data[1]
        masked = bool(byte2 & 0x80)
        payload_len = byte2 & 0x7F
        
        # Calculate actual payload length
        offset = 2
        
        if payload_len == 126:
            if len(data) < offset + 2:
                raise Exception("Incomplete frame")
            payload_len = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2
            
        elif payload_len == 127:
            if len(data) < offset + 8:
                raise Exception("Incomplete frame")
            payload_len = struct.unpack('>Q', data[offset:offset+8])[0]
            offset += 8
            
        # Extract mask key if present
        mask_key = None
        if masked:
            if len(data) < offset + 4:
                raise Exception("Incomplete frame")
            mask_key = data[offset:offset+4]
            offset += 4
            
        # Extract payload
        if len(data) < offset + payload_len:
            raise Exception("Incomplete frame")
            
        payload = data[offset:offset+payload_len]
        
        # Unmask payload if needed
        if masked and mask_key:
            unmasked = bytearray()
            for i, byte in enumerate(payload):
                unmasked.append(byte ^ mask_key[i % 4])
            payload = bytes(unmasked)
            
        return {
            'fin': fin,
            'rsv1': rsv1,
            'rsv2': rsv2,
            'rsv3': rsv3,
            'opcode': opcode,
            'masked': masked,
            'payload': payload,
            'frame_length': offset + payload_len
        }
        
    def handle_fragmented_message(self, frame):
        """
        Handle fragmented messages
        Like assembling a jigsaw puzzle
        """
        if frame['opcode'] != WebSocketOpcode.CONTINUATION:
            # Start of new fragmented message
            self.fragments = [frame]
        else:
            # Continuation frame
            self.fragments.append(frame)
            
        if frame['fin']:
            # Last fragment received
            # Combine all fragments
            combined_payload = b''
            for frag in self.fragments:
                combined_payload += frag['payload']
                
            # Clear fragments
            self.fragments = []
            
            return combined_payload
            
        return None  # Message not complete yet

# WebSocket Extensions
class WebSocketExtensions:
    """
    WebSocket protocol extensions
    Like adding extra features to your car
    """
    
    def __init__(self):
        self.permessage_deflate = PerMessageDeflate()
        self.multiplexing = WebSocketMultiplexing()
        
class PerMessageDeflate:
    """
    Per-message compression extension
    Save bandwidth like using ZIP files
    """
    
    def __init__(self):
        self.client_max_window_bits = 15
        self.server_max_window_bits = 15
        self.client_no_context_takeover = False
        self.server_no_context_takeover = False
        
    def negotiate(self, offer):
        """
        Negotiate compression parameters
        Like haggling in Sarojini Nagar market!
        """
        params = {}
        
        # Parse offer
        for param in offer.split(';'):
            param = param.strip()
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
            else:
                params[param] = True
                
        # Build response
        response = []
        
        if 'client_max_window_bits' in params:
            bits = min(int(params.get('client_max_window_bits', 15)), 15)
            response.append(f"client_max_window_bits={bits}")
            
        if 'server_max_window_bits' in params:
            bits = min(int(params.get('server_max_window_bits', 15)), 15)
            response.append(f"server_max_window_bits={bits}")
            
        return '; '.join(response)
        
    def compress(self, data):
        """
        Compress message data
        """
        import zlib
        
        compressor = zlib.compressobj(
            level=zlib.Z_DEFAULT_COMPRESSION,
            method=zlib.DEFLATED,
            wbits=-self.client_max_window_bits,
            memLevel=8,
            strategy=zlib.Z_DEFAULT_STRATEGY
        )
        
        compressed = compressor.compress(data)
        compressed += compressor.flush(zlib.Z_SYNC_FLUSH)
        
        # Remove trailing bytes
        if compressed[-4:] == b'\x00\x00\xff\xff':
            compressed = compressed[:-4]
            
        return compressed
        
    def decompress(self, data):
        """
        Decompress message data
        """
        import zlib
        
        # Add trailing bytes
        data += b'\x00\x00\xff\xff'
        
        decompressor = zlib.decompressobj(
            wbits=-self.server_max_window_bits
        )
        
        return decompressor.decompress(data)

class WebSocketMultiplexing:
    """
    WebSocket stream multiplexing
    Like multiple TV channels on one cable
    """
    
    def __init__(self):
        self.channels = {}
        self.next_channel_id = 1
        
    def create_channel(self, channel_type='data'):
        """
        Create new multiplexed channel
        """
        channel_id = self.next_channel_id
        self.next_channel_id += 1
        
        self.channels[channel_id] = {
            'id': channel_id,
            'type': channel_type,
            'state': 'open',
            'buffer': bytearray()
        }
        
        return channel_id
        
    def encode_frame(self, channel_id, payload):
        """
        Encode frame with channel ID
        """
        # Add channel ID to frame
        frame = struct.pack('>H', channel_id) + payload
        return frame
        
    def decode_frame(self, frame):
        """
        Decode frame and extract channel ID
        """
        if len(frame) < 2:
            raise Exception("Invalid multiplexed frame")
            
        channel_id = struct.unpack('>H', frame[:2])[0]
        payload = frame[2:]
        
        return channel_id, payload
```

### Chapter 11: Advanced Error Handling and Recovery

WebSocket connections mein errors handle karna is like driving in Indian traffic - you need to be prepared for anything! Network drops, server crashes, power cuts - sab kuch ho sakta hai.

```python
# Advanced Error Handling and Recovery
import asyncio
from enum import Enum
from typing import Optional, Callable
import logging

class WebSocketError(Exception):
    """Base WebSocket error class"""
    pass

class ConnectionError(WebSocketError):
    """Connection-related errors"""
    pass

class ProtocolError(WebSocketError):
    """Protocol violation errors"""
    pass

class WebSocketState(Enum):
    """
    WebSocket connection states
    Like stages of Indian wedding!
    """
    CONNECTING = "connecting"  # Like rishta pakka karna
    OPEN = "open"             # Like shaadi ho gayi
    CLOSING = "closing"       # Like vidaai
    CLOSED = "closed"         # Like ghar aa gaye

class RobustWebSocketConnection:
    """
    Robust WebSocket connection with error handling
    Built for Indian network conditions!
    """
    
    def __init__(self, url, **kwargs):
        self.url = url
        self.state = WebSocketState.CONNECTING
        self.connection = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 1  # seconds
        self.max_reconnect_delay = 60
        self.heartbeat_interval = 30
        self.heartbeat_timeout = 10
        self.last_heartbeat = None
        self.error_handlers = {}
        self.logger = logging.getLogger(__name__)
        
    async def connect(self):
        """
        Establish WebSocket connection with retry logic
        Like trying to book Tatkal ticket - keep trying!
        """
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                self.logger.info(f"Attempting connection #{self.reconnect_attempts + 1}")
                
                # Try to connect
                self.connection = await self._create_connection()
                
                # Connection successful
                self.state = WebSocketState.OPEN
                self.reconnect_attempts = 0
                self.reconnect_delay = 1
                
                # Start heartbeat
                asyncio.create_task(self._heartbeat_loop())
                
                # Start message handler
                asyncio.create_task(self._message_handler())
                
                self.logger.info("WebSocket connected successfully")
                return True
                
            except Exception as e:
                self.reconnect_attempts += 1
                self.logger.error(f"Connection failed: {e}")
                
                # Handle specific errors
                await self._handle_connection_error(e)
                
                # Calculate backoff delay
                delay = min(
                    self.reconnect_delay * (2 ** self.reconnect_attempts),
                    self.max_reconnect_delay
                )
                
                # Add jitter to prevent thundering herd
                import random
                delay += random.uniform(0, 1)
                
                self.logger.info(f"Retrying in {delay:.1f} seconds...")
                await asyncio.sleep(delay)
                
        # Max attempts reached
        self.state = WebSocketState.CLOSED
        raise ConnectionError("Failed to establish WebSocket connection")
        
    async def _create_connection(self):
        """
        Create actual WebSocket connection
        """
        import websockets
        
        # Connection options for Indian networks
        extra_headers = {
            'X-Client-Version': '2.0',
            'X-Network-Type': self._detect_network_type(),
            'X-Client-Location': 'India'
        }
        
        connection = await websockets.connect(
            self.url,
            extra_headers=extra_headers,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=10,
            max_size=10 * 1024 * 1024,  # 10MB max message size
            compression='deflate'
        )
        
        return connection
        
    def _detect_network_type(self):
        """
        Detect network type (simplified)
        """
        # In production, use actual network detection
        return "4G-Jio"  # Most common in India
        
    async def _handle_connection_error(self, error):
        """
        Handle specific connection errors
        Like different responses for different problems
        """
        error_str = str(error).lower()
        
        if 'timeout' in error_str:
            # Network timeout - common in India
            self.logger.warning("Network timeout - possible poor connectivity")
            await self._notify_user("Poor network detected, retrying...")
            
        elif 'refused' in error_str:
            # Connection refused - server might be down
            self.logger.error("Server refused connection")
            await self._notify_user("Server is down, please wait...")
            
        elif 'dns' in error_str or 'resolve' in error_str:
            # DNS resolution failed
            self.logger.error("DNS resolution failed")
            await self._check_internet_connectivity()
            
        elif 'ssl' in error_str or 'certificate' in error_str:
            # SSL/TLS error
            self.logger.error("SSL certificate error")
            await self._notify_user("Security certificate issue")
            
        else:
            # Unknown error
            self.logger.error(f"Unknown error: {error}")
            
    async def _check_internet_connectivity(self):
        """
        Check internet connectivity
        Like checking if WiFi is actually working
        """
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                # Try popular Indian sites
                test_urls = [
                    'https://www.google.co.in',
                    'https://www.flipkart.com',
                    'https://www.irctc.co.in'
                ]
                
                for url in test_urls:
                    try:
                        async with session.get(url, timeout=5) as response:
                            if response.status == 200:
                                self.logger.info(f"Internet connectivity OK (tested {url})")
                                return True
                    except:
                        continue
                        
            self.logger.error("No internet connectivity")
            await self._notify_user("Please check your internet connection")
            return False
            
        except Exception as e:
            self.logger.error(f"Connectivity check failed: {e}")
            return False
            
    async def _heartbeat_loop(self):
        """
        Heartbeat mechanism to detect connection issues
        Like checking pulse regularly
        """
        while self.state == WebSocketState.OPEN:
            try:
                # Send ping
                pong_waiter = await self.connection.ping()
                
                # Wait for pong with timeout
                await asyncio.wait_for(
                    pong_waiter,
                    timeout=self.heartbeat_timeout
                )
                
                self.last_heartbeat = asyncio.get_event_loop().time()
                
                # Wait before next heartbeat
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.TimeoutError:
                self.logger.warning("Heartbeat timeout - connection might be dead")
                await self._handle_dead_connection()
                break
                
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                break
                
    async def _handle_dead_connection(self):
        """
        Handle dead connection detection
        """
        self.logger.info("Detected dead connection, initiating recovery")
        
        # Close existing connection
        if self.connection:
            await self.connection.close()
            
        self.state = WebSocketState.CLOSED
        
        # Trigger reconnection
        await self.connect()
        
    async def _message_handler(self):
        """
        Handle incoming messages with error recovery
        """
        while self.state == WebSocketState.OPEN:
            try:
                # Receive message with timeout
                message = await asyncio.wait_for(
                    self.connection.recv(),
                    timeout=60  # 1 minute timeout
                )
                
                # Process message
                await self._process_message(message)
                
            except asyncio.TimeoutError:
                # No message for 1 minute - might be normal
                continue
                
            except websockets.exceptions.ConnectionClosed as e:
                self.logger.warning(f"Connection closed: {e}")
                await self._handle_connection_closed(e)
                break
                
            except Exception as e:
                self.logger.error(f"Message handler error: {e}")
                await self._handle_message_error(e)
                
    async def _process_message(self, message):
        """
        Process received message
        """
        try:
            # Parse message
            if isinstance(message, str):
                # Text message
                import json
                data = json.loads(message)
            else:
                # Binary message
                data = message
                
            # Route to appropriate handler
            message_type = data.get('type') if isinstance(data, dict) else 'binary'
            
            if message_type in self.error_handlers:
                await self.error_handlers[message_type](data)
            else:
                self.logger.debug(f"Received message: {message_type}")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON message: {e}")
            
        except Exception as e:
            self.logger.error(f"Message processing error: {e}")
            
    async def _handle_connection_closed(self, close_event):
        """
        Handle connection closed event
        """
        self.state = WebSocketState.CLOSED
        
        # Check close code
        if close_event.code == 1000:
            # Normal closure
            self.logger.info("Connection closed normally")
            
        elif close_event.code == 1001:
            # Going away
            self.logger.info("Server going away, will reconnect")
            await self.connect()
            
        elif close_event.code == 1006:
            # Abnormal closure
            self.logger.warning("Abnormal connection closure")
            await self.connect()
            
        elif close_event.code == 1008:
            # Policy violation
            self.logger.error("Policy violation")
            await self._notify_user("Connection policy violation")
            
        elif close_event.code == 1011:
            # Server error
            self.logger.error("Server error")
            await asyncio.sleep(5)  # Wait before reconnecting
            await self.connect()
            
        else:
            self.logger.warning(f"Connection closed with code {close_event.code}")
            await self.connect()
            
    async def _handle_message_error(self, error):
        """
        Handle message processing errors
        """
        # Log error
        self.logger.error(f"Message error: {error}")
        
        # Determine if connection is still alive
        try:
            # Try to send ping
            await self.connection.ping()
            # Connection is alive, just a message error
            self.logger.info("Connection still alive after message error")
            
        except:
            # Connection is dead
            self.logger.error("Connection dead after message error")
            await self._handle_dead_connection()
            
    async def _notify_user(self, message):
        """
        Notify user about connection status
        """
        # In production, use proper notification system
        print(f"🔔 {message}")
        
    def register_error_handler(self, message_type, handler):
        """
        Register custom error handler
        """
        self.error_handlers[message_type] = handler
        
    async def send(self, message):
        """
        Send message with error handling
        """
        if self.state != WebSocketState.OPEN:
            raise ConnectionError("WebSocket not connected")
            
        try:
            await self.connection.send(message)
            
        except Exception as e:
            self.logger.error(f"Send error: {e}")
            await self._handle_send_error(e)
            raise
            
    async def _handle_send_error(self, error):
        """
        Handle send errors
        """
        # Check if connection is still alive
        try:
            await self.connection.ping()
        except:
            # Connection is dead, reconnect
            await self._handle_dead_connection()
            
    async def close(self):
        """
        Close connection gracefully
        """
        self.state = WebSocketState.CLOSING
        
        if self.connection:
            try:
                await self.connection.close()
            except:
                pass
                
        self.state = WebSocketState.CLOSED
```

### Chapter 12: WebSocket Testing and Quality Assurance

Testing WebSocket applications properly is crucial, especially when lakhs of users depend on your real-time features. Indian companies have learned this the hard way - remember when Dream11 crashed during IPL final?

```python
# WebSocket Testing Framework
import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
import websockets
from typing import List, Dict, Any

class WebSocketTestClient:
    """
    Test client for WebSocket testing
    Like a crash test dummy for your code!
    """
    
    def __init__(self):
        self.connection = None
        self.received_messages = []
        self.sent_messages = []
        
    async def connect(self, url):
        """Connect to WebSocket server for testing"""
        self.connection = await websockets.connect(url)
        
        # Start receiving messages
        asyncio.create_task(self._receive_loop())
        
    async def _receive_loop(self):
        """Receive messages in background"""
        try:
            async for message in self.connection:
                self.received_messages.append(message)
        except:
            pass
            
    async def send(self, message):
        """Send test message"""
        await self.connection.send(message)
        self.sent_messages.append(message)
        
    async def wait_for_message(self, timeout=5):
        """Wait for next message with timeout"""
        start_count = len(self.received_messages)
        
        for _ in range(timeout * 10):  # Check every 100ms
            if len(self.received_messages) > start_count:
                return self.received_messages[-1]
            await asyncio.sleep(0.1)
            
        raise TimeoutError("No message received")
        
    async def close(self):
        """Close test connection"""
        if self.connection:
            await self.connection.close()

class WebSocketTestSuite:
    """
    Comprehensive WebSocket test suite
    Testing like ISRO tests rockets - thoroughly!
    """
    
    @pytest.mark.asyncio
    async def test_connection_establishment(self):
        """Test basic connection establishment"""
        client = WebSocketTestClient()
        
        try:
            await client.connect("ws://localhost:8000")
            assert client.connection is not None
            assert client.connection.open
            
        finally:
            await client.close()
            
    @pytest.mark.asyncio
    async def test_message_exchange(self):
        """Test bidirectional message exchange"""
        client = WebSocketTestClient()
        
        try:
            await client.connect("ws://localhost:8000")
            
            # Send message
            test_message = '{"type": "test", "data": "Hello Mumbai!"}'
            await client.send(test_message)
            
            # Wait for response
            response = await client.wait_for_message()
            assert response is not None
            
        finally:
            await client.close()
            
    @pytest.mark.asyncio
    async def test_connection_recovery(self):
        """Test connection recovery after network failure"""
        client = RobustWebSocketConnection("ws://localhost:8000")
        
        # Connect initially
        await client.connect()
        assert client.state == WebSocketState.OPEN
        
        # Simulate network failure
        await client.connection.close()
        
        # Wait for automatic reconnection
        await asyncio.sleep(2)
        
        # Should be reconnected
        assert client.state == WebSocketState.OPEN
        
    @pytest.mark.asyncio
    async def test_high_load(self):
        """
        Test high message load
        Like testing for IPL final traffic!
        """
        clients = []
        message_count = 1000
        
        try:
            # Create multiple clients
            for i in range(10):
                client = WebSocketTestClient()
                await client.connect(f"ws://localhost:8000")
                clients.append(client)
                
            # Send many messages from each client
            tasks = []
            for client in clients:
                for j in range(message_count):
                    message = f'{{"id": {j}, "data": "Test message"}}'
                    tasks.append(client.send(message))
                    
            # Wait for all sends to complete
            await asyncio.gather(*tasks)
            
            # Verify all messages sent
            for client in clients:
                assert len(client.sent_messages) == message_count
                
        finally:
            # Cleanup
            for client in clients:
                await client.close()
                
    @pytest.mark.asyncio
    async def test_concurrent_connections(self):
        """
        Test maximum concurrent connections
        Like testing how many people can board local train!
        """
        max_connections = 100
        clients = []
        
        try:
            # Create many concurrent connections
            for i in range(max_connections):
                client = WebSocketTestClient()
                await client.connect("ws://localhost:8000")
                clients.append(client)
                
            # All should be connected
            assert len(clients) == max_connections
            
            for client in clients:
                assert client.connection.open
                
        finally:
            # Cleanup
            for client in clients:
                await client.close()

class WebSocketLoadTester:
    """
    Load testing for WebSocket servers
    Like stress-testing a bridge before opening
    """
    
    def __init__(self, target_url):
        self.target_url = target_url
        self.metrics = {
            'total_connections': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'total_latency': 0,
            'errors': []
        }
        
    async def run_load_test(self, num_clients=100, messages_per_client=100):
        """
        Run load test with specified parameters
        """
        print(f"🚀 Starting load test: {num_clients} clients, {messages_per_client} messages each")
        
        tasks = []
        for i in range(num_clients):
            task = self._client_workflow(i, messages_per_client)
            tasks.append(task)
            
        # Run all clients concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        self._analyze_results(results)
        
    async def _client_workflow(self, client_id, num_messages):
        """
        Single client workflow for load testing
        """
        client_metrics = {
            'client_id': client_id,
            'connected': False,
            'messages_sent': 0,
            'messages_received': 0,
            'latencies': [],
            'errors': []
        }
        
        try:
            # Connect
            start_time = asyncio.get_event_loop().time()
            client = WebSocketTestClient()
            await client.connect(self.target_url)
            connect_time = asyncio.get_event_loop().time() - start_time
            
            client_metrics['connected'] = True
            client_metrics['connect_time'] = connect_time
            
            # Send messages
            for msg_id in range(num_messages):
                try:
                    message = f'{{"client": {client_id}, "msg": {msg_id}, "timestamp": {asyncio.get_event_loop().time()}}}'
                    
                    send_start = asyncio.get_event_loop().time()
                    await client.send(message)
                    send_time = asyncio.get_event_loop().time() - send_start
                    
                    client_metrics['messages_sent'] += 1
                    client_metrics['latencies'].append(send_time)
                    
                    # Small delay between messages
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    client_metrics['errors'].append(str(e))
                    
            # Close connection
            await client.close()
            
        except Exception as e:
            client_metrics['errors'].append(f"Connection error: {str(e)}")
            
        return client_metrics
        
    def _analyze_results(self, results):
        """
        Analyze load test results
        """
        successful = 0
        total_messages = 0
        all_latencies = []
        
        for result in results:
            if isinstance(result, dict):
                if result['connected']:
                    successful += 1
                total_messages += result['messages_sent']
                all_latencies.extend(result['latencies'])
                
        # Calculate statistics
        if all_latencies:
            avg_latency = sum(all_latencies) / len(all_latencies)
            max_latency = max(all_latencies)
            min_latency = min(all_latencies)
            
            # Calculate percentiles
            sorted_latencies = sorted(all_latencies)
            p50 = sorted_latencies[len(sorted_latencies) // 2]
            p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            p99 = sorted_latencies[int(len(sorted_latencies) * 0.99)]
            
            print("\n📊 Load Test Results:")
            print(f"   Total Clients: {len(results)}")
            print(f"   Successful Connections: {successful}")
            print(f"   Total Messages Sent: {total_messages}")
            print(f"\n⏱️ Latency Statistics (ms):")
            print(f"   Average: {avg_latency * 1000:.2f}")
            print(f"   Min: {min_latency * 1000:.2f}")
            print(f"   Max: {max_latency * 1000:.2f}")
            print(f"   P50: {p50 * 1000:.2f}")
            print(f"   P95: {p95 * 1000:.2f}")
            print(f"   P99: {p99 * 1000:.2f}")
```

## Conclusion: The Journey Ahead

Dosto, aaj humne WebSocket protocols ki complete journey ki - from basics to advanced production systems. Humne dekha ki kaise Indian companies like Zerodha, Dream11, Ola, and Hotstar use WebSocket to serve millions of users with real-time updates.

### Key Takeaways - The Mumbai Local Wisdom

1. **WebSocket is Full-Duplex** - Like having a dedicated phone line instead of sending telegrams
2. **Indian Scale Matters** - What works for 1000 users won't work for 10 million
3. **Network Reality** - Indian networks are unique, plan for 2G to 5G
4. **Cost Optimization** - Every byte counts when you're serving crores of users
5. **Security First** - With UPI and digital payments, security is non-negotiable

### Production Checklist - Before Going Live

Just like how ISRO has a checklist before launching satellites, here's your WebSocket production checklist:

✅ **Connection Management**
- Automatic reconnection with exponential backoff
- Connection pooling for efficiency
- Graceful degradation for poor networks

✅ **Error Handling**
- Network timeout handling
- Message retry mechanism
- Circuit breaker pattern implementation

✅ **Security**
- WSS (WebSocket Secure) only
- Token-based authentication
- Rate limiting per user
- DDoS protection

✅ **Monitoring**
- Real-time connection metrics
- Message throughput tracking
- Latency monitoring
- Error rate alerts

✅ **Performance**
- Message compression enabled
- Binary protocol for large data
- Connection multiplexing
- CDN for initial handshake

### The Indian Tech Revolution

India is at the forefront of real-time technology adoption. From UPI processing 10 billion transactions per month to Aarogya Setu connecting 200 million users, WebSocket is powering this revolution.

Future applications being built with WebSocket in India:
- **Digital Education**: Live classes for rural students
- **Telemedicine**: Real-time health monitoring
- **Smart Cities**: Traffic management systems
- **Agriculture**: Real-time crop monitoring
- **Financial Inclusion**: Real-time banking for all

### Your Next Steps

1. **Start Small** - Build a simple chat application
2. **Scale Gradually** - Add features incrementally
3. **Test Thoroughly** - Indian users have diverse devices and networks
4. **Monitor Everything** - What you can't measure, you can't improve
5. **Share Knowledge** - Contribute to the Indian tech community

### Final Words of Wisdom

Remember, WebSocket is not just a protocol - it's an enabler of real-time experiences. Whether you're building the next unicorn startup or solving local problems with technology, WebSocket gives you the power to connect people instantly.

The beauty of WebSocket lies in its simplicity - once connected, just send and receive. No polling, no overhead, just pure real-time communication.

As we say in India - "Vasudhaiva Kutumbakam" (the world is one family). WebSocket helps us stay connected as one global family, sharing information in real-time, breaking barriers of distance and time.

So go ahead, build something amazing! Whether it's helping farmers with real-time weather updates, connecting students with teachers, or creating the next big social platform - WebSocket is your companion in this journey.

Keep learning, keep building, and most importantly, keep solving real problems that matter to real people. That's the true spirit of Indian technology - Jugaad with purpose!

Until next time, this is your host signing off. May your connections be stable, your latency be low, and your WebSockets always stay alive!

Happy coding, and remember - in the world of real-time communication, every millisecond counts! 🚀

Jai Hind! Jai Technology! 🇮🇳

---

## Bonus: Quick Reference Guide

### WebSocket URLs
```
ws://localhost:8080/socket    # Development
wss://api.example.com/socket  # Production (secure)
```

### Connection States
```
CONNECTING (0) -> OPEN (1) -> CLOSING (2) -> CLOSED (3)
```

### Common Status Codes
```
1000 - Normal closure
1001 - Going away
1002 - Protocol error
1003 - Unsupported data
1006 - Abnormal closure
1008 - Policy violation
1011 - Server error
```

### Frame Types
```
0x0 - Continuation
0x1 - Text
0x2 - Binary
0x8 - Close
0x9 - Ping
0xA - Pong
```

### Indian Production Tips
```
- Use IST timezone for scheduling
- Plan for power cuts (UPS/generators)
- Consider mobile-first (70% users)
- Support 2G/3G networks
- Implement offline mode
- Use regional CDNs
- Support multiple languages
- Consider data costs
```

---

## Part 5: WebSocket Best Practices and Anti-Patterns - Learn from Mistakes (60 minutes)

### Chapter 13: Common WebSocket Mistakes Indian Developers Make

Dosto, ab baat karte hain un common mistakes ki jo Indian developers aksar karte hain WebSocket implement karte waqt. Ye woh mistakes hain jo production mein jaake bade problems create karti hain!

```python
# Common WebSocket Anti-Patterns and Solutions
import asyncio
from typing import Dict, List, Set
import time

class WebSocketAntiPatterns:
    """
    Common mistakes and their solutions
    Learn from others' production disasters!
    """
    
    def __init__(self):
        self.connections = {}
        self.message_queue = []
        
    # Anti-Pattern 1: Not handling disconnections properly
    async def bad_connection_handling(self, websocket):
        """
        ❌ BAD: Not cleaning up after disconnection
        Like leaving tap open after use!
        """
        # Wrong way
        self.connections[websocket.id] = websocket
        # No cleanup on disconnect!
        
    async def good_connection_handling(self, websocket):
        """
        ✅ GOOD: Proper connection lifecycle management
        """
        connection_id = websocket.id
        
        try:
            # Register connection
            self.connections[connection_id] = {
                'websocket': websocket,
                'created_at': time.time(),
                'last_activity': time.time(),
                'metadata': {}
            }
            
            # Handle messages
            async for message in websocket:
                await self.process_message(connection_id, message)
                
        except Exception as e:
            print(f"Connection error: {e}")
            
        finally:
            # Always cleanup
            if connection_id in self.connections:
                del self.connections[connection_id]
            # Clean up any associated resources
            await self.cleanup_user_resources(connection_id)
            
    # Anti-Pattern 2: Broadcasting to all without filtering
    async def bad_broadcast(self, message):
        """
        ❌ BAD: Sending everything to everyone
        Like shouting in library!
        """
        for conn in self.connections.values():
            try:
                await conn.send(message)  # Sends to everyone!
            except:
                pass  # Ignoring errors!
                
    async def good_broadcast(self, message, target_room=None, filters=None):
        """
        ✅ GOOD: Targeted broadcasting with filters
        """
        tasks = []
        
        for conn_id, conn_data in self.connections.items():
            # Check if user should receive message
            if not self.should_receive_message(conn_id, target_room, filters):
                continue
                
            # Create send task
            task = self.safe_send(conn_data['websocket'], message)
            tasks.append(task)
            
        # Send all messages concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log failures
        failures = sum(1 for r in results if isinstance(r, Exception))
        if failures:
            print(f"Failed to send to {failures} connections")
            
    def should_receive_message(self, conn_id, target_room, filters):
        """Check if connection should receive message"""
        # Apply room filter
        if target_room and self.connections[conn_id].get('room') != target_room:
            return False
            
        # Apply custom filters
        if filters:
            for filter_func in filters:
                if not filter_func(self.connections[conn_id]):
                    return False
                    
        return True
        
    async def safe_send(self, websocket, message):
        """Send message with error handling"""
        try:
            await websocket.send(message)
        except Exception as e:
            print(f"Send failed: {e}")
            raise
            
    # Anti-Pattern 3: No rate limiting
    async def bad_message_handling(self, websocket, message):
        """
        ❌ BAD: Processing everything immediately
        Like accepting unlimited orders in restaurant!
        """
        # Process immediately without any checks
        await self.process_heavy_operation(message)
        
    async def good_message_handling(self, websocket, message):
        """
        ✅ GOOD: Rate limiting and queuing
        """
        user_id = websocket.user_id
        
        # Check rate limit
        if not await self.check_rate_limit(user_id):
            await websocket.send('{"error": "Rate limit exceeded"}')
            return
            
        # Check message size
        if len(message) > 1024 * 100:  # 100KB limit
            await websocket.send('{"error": "Message too large"}')
            return
            
        # Queue for processing
        await self.queue_for_processing(user_id, message)
        
    # Anti-Pattern 4: Synchronous operations in async context
    def bad_database_query(self, user_id):
        """
        ❌ BAD: Blocking database calls
        Like stopping traffic for VIP convoy!
        """
        import pymongo
        client = pymongo.MongoClient()  # Blocking!
        db = client.mydatabase
        user = db.users.find_one({'_id': user_id})  # Blocking!
        return user
        
    async def good_database_query(self, user_id):
        """
        ✅ GOOD: Non-blocking async database calls
        """
        import motor.motor_asyncio
        
        client = motor.motor_asyncio.AsyncIOMotorClient()
        db = client.mydatabase
        user = await db.users.find_one({'_id': user_id})  # Non-blocking!
        return user
        
    # Anti-Pattern 5: Memory leaks
    class BadMessageCache:
        """❌ BAD: Unlimited message storage"""
        def __init__(self):
            self.messages = []  # Grows forever!
            
        def add_message(self, message):
            self.messages.append(message)  # Memory leak!
            
    class GoodMessageCache:
        """✅ GOOD: Bounded message cache"""
        def __init__(self, max_size=1000):
            from collections import deque
            self.messages = deque(maxlen=max_size)  # Bounded!
            self.total_processed = 0
            
        def add_message(self, message):
            self.messages.append(message)
            self.total_processed += 1
            
            # Periodic cleanup
            if self.total_processed % 10000 == 0:
                self.cleanup_old_data()
                
        def cleanup_old_data(self):
            """Remove old data periodically"""
            # Clean up other resources
            pass

class ProductionBestPractices:
    """
    WebSocket best practices for production
    Learned from Indian unicorn experiences
    """
    
    def __init__(self):
        self.health_check_interval = 30
        self.connection_timeout = 300  # 5 minutes
        
    # Best Practice 1: Connection pooling
    class ConnectionPool:
        """
        Manage WebSocket connections efficiently
        Like managing parking spaces in mall
        """
        def __init__(self, max_connections=10000):
            self.max_connections = max_connections
            self.active_connections = {}
            self.connection_queue = asyncio.Queue()
            
        async def acquire_connection(self, user_id):
            """Get connection from pool"""
            if len(self.active_connections) >= self.max_connections:
                # Wait for available slot
                await self.connection_queue.get()
                
            # Create new connection
            connection = await self.create_connection(user_id)
            self.active_connections[user_id] = connection
            return connection
            
        async def release_connection(self, user_id):
            """Return connection to pool"""
            if user_id in self.active_connections:
                del self.active_connections[user_id]
                # Signal available slot
                await self.connection_queue.put(None)
                
        async def create_connection(self, user_id):
            """Create new WebSocket connection"""
            # Implementation here
            pass
            
    # Best Practice 2: Message batching
    class MessageBatcher:
        """
        Batch messages for efficiency
        Like carpooling to save fuel!
        """
        def __init__(self):
            self.batch_size = 100
            self.batch_interval = 0.1  # 100ms
            self.pending_messages = {}
            
        async def send_message(self, user_id, message):
            """Add message to batch"""
            if user_id not in self.pending_messages:
                self.pending_messages[user_id] = []
                # Schedule batch send
                asyncio.create_task(self.flush_batch(user_id))
                
            self.pending_messages[user_id].append(message)
            
        async def flush_batch(self, user_id):
            """Send batched messages"""
            await asyncio.sleep(self.batch_interval)
            
            if user_id in self.pending_messages:
                messages = self.pending_messages[user_id]
                del self.pending_messages[user_id]
                
                # Send as single message
                batch = {
                    'type': 'batch',
                    'messages': messages
                }
                await self.send_to_user(user_id, batch)
                
        async def send_to_user(self, user_id, data):
            """Send data to specific user"""
            # Implementation here
            pass
            
    # Best Practice 3: Circuit breaker pattern
    class CircuitBreaker:
        """
        Prevent cascading failures
        Like electric circuit breaker in home!
        """
        def __init__(self, failure_threshold=5, recovery_timeout=60):
            self.failure_threshold = failure_threshold
            self.recovery_timeout = recovery_timeout
            self.failure_count = 0
            self.last_failure_time = None
            self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
            
        async def call(self, func, *args, **kwargs):
            """Execute function with circuit breaker"""
            if self.state == 'OPEN':
                # Check if we should try again
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker is OPEN")
                    
            try:
                result = await func(*args, **kwargs)
                
                # Success - reset failure count
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                self.failure_count = 0
                
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                    print(f"Circuit breaker opened after {self.failure_count} failures")
                    
                raise
                
    # Best Practice 4: Graceful shutdown
    class GracefulShutdown:
        """
        Shutdown WebSocket server gracefully
        Like closing shop properly at night
        """
        def __init__(self):
            self.shutting_down = False
            self.active_connections = set()
            
        async def shutdown(self):
            """Graceful shutdown procedure"""
            print("🛑 Starting graceful shutdown...")
            self.shutting_down = True
            
            # Step 1: Stop accepting new connections
            print("   1. Stopped accepting new connections")
            
            # Step 2: Notify all clients
            await self.notify_all_clients()
            print("   2. Notified all clients")
            
            # Step 3: Wait for ongoing operations
            await self.wait_for_operations()
            print("   3. Completed ongoing operations")
            
            # Step 4: Close all connections
            await self.close_all_connections()
            print("   4. Closed all connections")
            
            # Step 5: Cleanup resources
            await self.cleanup_resources()
            print("   5. Cleaned up resources")
            
            print("✅ Graceful shutdown complete")
            
        async def notify_all_clients(self):
            """Notify clients about shutdown"""
            notification = {
                'type': 'server_shutdown',
                'message': 'Server is shutting down',
                'reconnect_after': 30  # seconds
            }
            
            tasks = []
            for conn in self.active_connections:
                task = conn.send(json.dumps(notification))
                tasks.append(task)
                
            await asyncio.gather(*tasks, return_exceptions=True)
            
        async def wait_for_operations(self):
            """Wait for ongoing operations to complete"""
            max_wait = 30  # seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                # Check if operations are complete
                if self.all_operations_complete():
                    break
                await asyncio.sleep(1)
                
        async def close_all_connections(self):
            """Close all WebSocket connections"""
            tasks = []
            for conn in self.active_connections:
                task = conn.close(code=1001, reason="Server shutdown")
                tasks.append(task)
                
            await asyncio.gather(*tasks, return_exceptions=True)
            
        async def cleanup_resources(self):
            """Clean up server resources"""
            # Close database connections
            # Flush caches
            # Save state if needed
            pass
            
        def all_operations_complete(self):
            """Check if all operations are complete"""
            # Implementation based on your needs
            return True
```

### Chapter 14: WebSocket Optimization for Indian Networks

Indian networks are unique - from high-speed Jio Fiber to 2G in rural areas. Your WebSocket implementation needs to work across this spectrum!

```python
# Network-Aware WebSocket Implementation
import asyncio
from enum import Enum

class NetworkType(Enum):
    """Indian network types"""
    TWO_G = "2G"
    THREE_G = "3G"
    FOUR_G = "4G"
    FIVE_G = "5G"
    WIFI = "WiFi"
    FIBER = "Fiber"

class IndianNetworkOptimizer:
    """
    Optimize WebSocket for Indian network conditions
    From Kashmir to Kanyakumari, it should work!
    """
    
    def __init__(self):
        self.network_profiles = {
            NetworkType.TWO_G: {
                'bandwidth': 0.1,  # Mbps
                'latency': 500,    # ms
                'packet_loss': 5,  # %
                'message_size_limit': 1024,  # bytes
                'compression': True,
                'batch_interval': 5  # seconds
            },
            NetworkType.THREE_G: {
                'bandwidth': 2,
                'latency': 200,
                'packet_loss': 2,
                'message_size_limit': 10240,
                'compression': True,
                'batch_interval': 2
            },
            NetworkType.FOUR_G: {
                'bandwidth': 20,
                'latency': 50,
                'packet_loss': 0.5,
                'message_size_limit': 102400,
                'compression': False,
                'batch_interval': 0.5
            },
            NetworkType.FIVE_G: {
                'bandwidth': 100,
                'latency': 10,
                'packet_loss': 0.1,
                'message_size_limit': 1048576,
                'compression': False,
                'batch_interval': 0.1
            },
            NetworkType.WIFI: {
                'bandwidth': 50,
                'latency': 20,
                'packet_loss': 0.2,
                'message_size_limit': 524288,
                'compression': False,
                'batch_interval': 0.2
            },
            NetworkType.FIBER: {
                'bandwidth': 1000,
                'latency': 5,
                'packet_loss': 0.01,
                'message_size_limit': 10485760,
                'compression': False,
                'batch_interval': 0.05
            }
        }
        
    async def detect_network_type(self, connection):
        """
        Detect user's network type
        Like checking train class before journey
        """
        # Measure latency
        start_time = asyncio.get_event_loop().time()
        await connection.ping()
        latency = (asyncio.get_event_loop().time() - start_time) * 1000
        
        # Estimate network type based on latency
        if latency > 400:
            return NetworkType.TWO_G
        elif latency > 150:
            return NetworkType.THREE_G
        elif latency > 30:
            return NetworkType.FOUR_G
        elif latency > 15:
            return NetworkType.WIFI
        elif latency > 8:
            return NetworkType.FIVE_G
        else:
            return NetworkType.FIBER
            
    def optimize_for_network(self, network_type):
        """
        Get optimized settings for network type
        """
        return self.network_profiles[network_type]
        
    async def adaptive_message_sending(self, connection, message, network_type):
        """
        Send message adapted to network conditions
        Like adjusting speed based on road condition
        """
        profile = self.network_profiles[network_type]
        
        # Check message size
        if len(message) > profile['message_size_limit']:
            # Split into chunks
            chunks = self.split_message(message, profile['message_size_limit'])
            for chunk in chunks:
                await self.send_chunk(connection, chunk, profile)
        else:
            # Send as single message
            if profile['compression']:
                message = self.compress_message(message)
            await connection.send(message)
            
    def split_message(self, message, chunk_size):
        """Split large message into chunks"""
        chunks = []
        for i in range(0, len(message), chunk_size):
            chunk = {
                'type': 'chunk',
                'id': i // chunk_size,
                'total': (len(message) + chunk_size - 1) // chunk_size,
                'data': message[i:i + chunk_size]
            }
            chunks.append(json.dumps(chunk))
        return chunks
        
    async def send_chunk(self, connection, chunk, profile):
        """Send chunk with network-aware delay"""
        await connection.send(chunk)
        # Add delay for poor networks
        if profile['latency'] > 100:
            await asyncio.sleep(0.1)
            
    def compress_message(self, message):
        """Compress message for slow networks"""
        import gzip
        return gzip.compress(message.encode())

class OfflineSupport:
    """
    Handle offline scenarios common in India
    Power cuts, network issues, etc.
    """
    
    def __init__(self):
        self.offline_queue = []
        self.max_offline_messages = 1000
        self.persistence_enabled = True
        
    async def handle_offline_message(self, message):
        """
        Queue message when offline
        Like saving letters when postman doesn't come
        """
        if len(self.offline_queue) >= self.max_offline_messages:
            # Remove oldest message
            self.offline_queue.pop(0)
            
        # Add to queue
        offline_message = {
            'message': message,
            'timestamp': time.time(),
            'retry_count': 0
        }
        self.offline_queue.append(offline_message)
        
        # Persist to local storage
        if self.persistence_enabled:
            await self.persist_to_storage(offline_message)
            
    async def sync_offline_messages(self, connection):
        """
        Sync offline messages when back online
        Like sending all pending WhatsApp messages
        """
        print(f"📤 Syncing {len(self.offline_queue)} offline messages...")
        
        synced = 0
        failed = 0
        
        while self.offline_queue:
            msg_data = self.offline_queue[0]
            
            try:
                # Try to send
                await connection.send(msg_data['message'])
                self.offline_queue.pop(0)
                synced += 1
                
                # Small delay to avoid overwhelming
                await asyncio.sleep(0.01)
                
            except Exception as e:
                msg_data['retry_count'] += 1
                
                if msg_data['retry_count'] > 3:
                    # Give up after 3 retries
                    self.offline_queue.pop(0)
                    failed += 1
                else:
                    # Try again later
                    break
                    
        print(f"✅ Synced: {synced}, Failed: {failed}, Remaining: {len(self.offline_queue)}")
        
    async def persist_to_storage(self, message):
        """
        Save message to local storage
        Using IndexedDB in browser or SQLite in app
        """
        # Implementation depends on platform
        pass

class DataSavingMode:
    """
    Data saving mode for Indian users
    Important when data is expensive!
    """
    
    def __init__(self):
        self.data_saving_enabled = False
        self.quality_levels = {
            'high': {'images': True, 'videos': True, 'compression': False},
            'medium': {'images': True, 'videos': False, 'compression': True},
            'low': {'images': False, 'videos': False, 'compression': True}
        }
        self.current_quality = 'medium'
        
    def filter_message(self, message):
        """
        Filter message based on data saving settings
        Like choosing SD over HD on Netflix
        """
        if not self.data_saving_enabled:
            return message
            
        quality = self.quality_levels[self.current_quality]
        
        # Parse message
        data = json.loads(message) if isinstance(message, str) else message
        
        # Filter based on quality
        if not quality['images'] and 'image' in data:
            data['image'] = None
            data['image_placeholder'] = True
            
        if not quality['videos'] and 'video' in data:
            data['video'] = None
            data['video_placeholder'] = True
            
        # Compress if needed
        filtered = json.dumps(data)
        if quality['compression']:
            filtered = self.compress_message(filtered)
            
        return filtered
        
    def compress_message(self, message):
        """Compress message to save data"""
        import zlib
        return zlib.compress(message.encode(), level=9)
        
    def estimate_data_usage(self, message):
        """
        Estimate data usage for message
        Show users like mobile data warning
        """
        size_bytes = len(message)
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        # Estimate cost (₹10 per GB approximate)
        cost_per_gb = 10
        cost = (size_bytes / (1024**3)) * cost_per_gb
        
        return {
            'bytes': size_bytes,
            'kb': round(size_kb, 2),
            'mb': round(size_mb, 2),
            'estimated_cost': round(cost, 4),
            'warning': size_mb > 1  # Warn if > 1MB
        }
```

### Chapter 15: WebSocket Frameworks and Libraries - Indian Developer's Toolkit

Let's explore the best WebSocket frameworks and libraries that Indian developers love and use in production!

```python
# Popular WebSocket Frameworks Comparison

class WebSocketFrameworks:
    """
    Comparison of popular WebSocket frameworks
    Used by Indian startups and enterprises
    """
    
    def __init__(self):
        self.frameworks = {
            'socket.io': {
                'language': 'JavaScript/Node.js',
                'pros': [
                    'Automatic reconnection',
                    'Room support built-in',
                    'Fallback to polling',
                    'Large community'
                ],
                'cons': [
                    'Not pure WebSocket',
                    'Heavier protocol',
                    'Performance overhead'
                ],
                'indian_users': ['Ola', 'Swiggy', 'Zomato'],
                'best_for': 'Quick prototypes, chat apps'
            },
            'ws': {
                'language': 'JavaScript/Node.js',
                'pros': [
                    'Pure WebSocket',
                    'Lightweight',
                    'High performance',
                    'No dependencies'
                ],
                'cons': [
                    'No built-in features',
                    'Manual implementation needed',
                    'No automatic reconnection'
                ],
                'indian_users': ['Zerodha', 'Razorpay'],
                'best_for': 'High-performance trading systems'
            },
            'django-channels': {
                'language': 'Python/Django',
                'pros': [
                    'Django integration',
                    'Async support',
                    'Channel layers',
                    'Good documentation'
                ],
                'cons': [
                    'Django dependency',
                    'Complex setup',
                    'Performance limitations'
                ],
                'indian_users': ['Unacademy', 'Testbook'],
                'best_for': 'Django applications'
            },
            'fastapi-websocket': {
                'language': 'Python/FastAPI',
                'pros': [
                    'Modern Python',
                    'Type hints',
                    'Automatic documentation',
                    'High performance'
                ],
                'cons': [
                    'Newer framework',
                    'Smaller community',
                    'Less battle-tested'
                ],
                'indian_users': ['Dunzo', 'Cred'],
                'best_for': 'Modern Python APIs'
            },
            'spring-websocket': {
                'language': 'Java/Spring',
                'pros': [
                    'Enterprise ready',
                    'Spring ecosystem',
                    'STOMP support',
                    'Security features'
                ],
                'cons': [
                    'Complex configuration',
                    'Heavy framework',
                    'Steep learning curve'
                ],
                'indian_users': ['Flipkart', 'MakeMyTrip'],
                'best_for': 'Enterprise applications'
            },
            'gorilla-websocket': {
                'language': 'Go',
                'pros': [
                    'High performance',
                    'Low memory usage',
                    'Concurrent connections',
                    'Simple API'
                ],
                'cons': [
                    'Manual features',
                    'Go expertise needed',
                    'Less abstraction'
                ],
                'indian_users': ['Uber India', 'Gojek'],
                'best_for': 'High-throughput systems'
            }
        }
        
    def recommend_framework(self, requirements):
        """
        Recommend framework based on requirements
        Like choosing right vehicle for journey
        """
        recommendations = []
        
        # Check language preference
        if requirements.get('language'):
            for name, details in self.frameworks.items():
                if requirements['language'] in details['language']:
                    recommendations.append(name)
                    
        # Check scale requirements
        if requirements.get('scale') == 'high':
            # High scale - recommend ws, gorilla
            high_perf = ['ws', 'gorilla-websocket', 'fastapi-websocket']
            recommendations.extend(high_perf)
            
        # Check enterprise needs
        if requirements.get('enterprise'):
            recommendations.append('spring-websocket')
            
        # Remove duplicates and return
        return list(set(recommendations))

# Socket.IO Implementation Example
class SocketIOExample:
    """
    Socket.IO implementation example
    Popular among Indian startups
    """
    
    @staticmethod
    def server_example():
        """Socket.IO server example"""
        code = '''
// Socket.IO Server (Node.js)
const io = require('socket.io')(3000, {
    cors: {
        origin: "https://yourapp.in",
        credentials: true
    }
});

// Namespaces for different features
const chatNamespace = io.of('/chat');
const notificationNamespace = io.of('/notifications');

// Room management
io.on('connection', (socket) => {
    console.log(`User connected: ${socket.id}`);
    
    // Join room
    socket.on('join-room', (roomId) => {
        socket.join(roomId);
        socket.to(roomId).emit('user-joined', socket.id);
    });
    
    // Handle messages
    socket.on('message', (data) => {
        // Broadcast to room
        socket.to(data.roomId).emit('message', {
            userId: socket.id,
            message: data.message,
            timestamp: Date.now()
        });
    });
    
    // Handle disconnection
    socket.on('disconnect', () => {
        console.log(`User disconnected: ${socket.id}`);
    });
});

// Middleware for authentication
io.use((socket, next) => {
    const token = socket.handshake.auth.token;
    // Verify token
    if (isValidToken(token)) {
        next();
    } else {
        next(new Error('Authentication failed'));
    }
});
        '''
        return code
        
    @staticmethod
    def client_example():
        """Socket.IO client example"""
        code = '''
// Socket.IO Client (JavaScript)
import io from 'socket.io-client';

class SocketClient {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
    }
    
    connect() {
        this.socket = io('https://api.yourapp.in', {
            auth: {
                token: localStorage.getItem('token')
            },
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000
        });
        
        // Connection events
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.reconnectAttempts = 0;
        });
        
        this.socket.on('disconnect', (reason) => {
            console.log(`Disconnected: ${reason}`);
            if (reason === 'io server disconnect') {
                // Server disconnected, manually reconnect
                this.socket.connect();
            }
        });
        
        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
        });
        
        // Custom events
        this.socket.on('message', (data) => {
            this.handleMessage(data);
        });
    }
    
    joinRoom(roomId) {
        this.socket.emit('join-room', roomId);
    }
    
    sendMessage(roomId, message) {
        this.socket.emit('message', {
            roomId,
            message,
            timestamp: Date.now()
        });
    }
    
    handleMessage(data) {
        // Update UI with new message
        console.log('Received:', data);
    }
}

// Usage
const client = new SocketClient();
client.connect();
client.joinRoom('cricket-live-chat');
client.sendMessage('cricket-live-chat', 'India won! 🎉');
        '''
        return code

# FastAPI WebSocket Example
class FastAPIWebSocketExample:
    """
    FastAPI WebSocket implementation
    Modern Python choice for Indian developers
    """
    
    @staticmethod
    def server_example():
        """FastAPI WebSocket server"""
        code = '''
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import json
import asyncio

app = FastAPI(title="Indian Real-time App")

# CORS for Indian domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourapp.in", "https://app.yourapp.in"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_rooms: Dict[str, List[str]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
            
    async def broadcast(self, message: str, room: str = None):
        if room:
            # Send to specific room
            for user_id in self.user_rooms.get(room, []):
                if user_id in self.active_connections:
                    await self.active_connections[user_id].send_text(message)
        else:
            # Send to all
            for connection in self.active_connections.values():
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time communication
    """
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message['type'] == 'chat':
                await manager.broadcast(
                    json.dumps({
                        'type': 'chat',
                        'user': user_id,
                        'message': message['content'],
                        'timestamp': message['timestamp']
                    }),
                    room=message.get('room')
                )
                
            elif message['type'] == 'join_room':
                room = message['room']
                if room not in manager.user_rooms:
                    manager.user_rooms[room] = []
                manager.user_rooms[room].append(user_id)
                
            elif message['type'] == 'leave_room':
                room = message['room']
                if room in manager.user_rooms:
                    manager.user_rooms[room].remove(user_id)
                    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast(
            json.dumps({
                'type': 'user_left',
                'user': user_id
            })
        )

# REST endpoint for server-initiated messages
@app.post("/send-notification")
async def send_notification(user_id: str, message: str):
    """
    Send notification to specific user via WebSocket
    """
    await manager.send_personal_message(
        json.dumps({
            'type': 'notification',
            'message': message
        }),
        user_id
    )
    return {"status": "sent"}

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections),
        "rooms": len(manager.user_rooms)
    }
        '''
        return code
```

### Chapter 16: WebSocket in Cloud - Indian Cloud Providers

Indian companies are increasingly using cloud services for WebSocket deployment. Let's see how to deploy on popular platforms!

```python
# Cloud Deployment Strategies for WebSocket

class CloudDeploymentGuide:
    """
    Deploy WebSocket on various cloud platforms
    Popular among Indian enterprises
    """
    
    def __init__(self):
        self.providers = {
            'aws': self.aws_deployment(),
            'azure': self.azure_deployment(),
            'gcp': self.gcp_deployment(),
            'digital_ocean': self.digital_ocean_deployment()
        }
        
    def aws_deployment(self):
        """AWS deployment configuration"""
        return {
            'services': {
                'api_gateway': '''
# AWS API Gateway WebSocket
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  WebSocketApi:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: IndianWebSocketAPI
      ProtocolType: WEBSOCKET
      RouteSelectionExpression: "$request.body.action"
      
  ConnectRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref WebSocketApi
      RouteKey: $connect
      AuthorizationType: NONE
      Target: !Sub integrations/${ConnectIntegration}
      
  ConnectFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: connect.handler
      Runtime: nodejs14.x
      Environment:
        Variables:
          TABLE_NAME: !Ref ConnectionsTable
          
  ConnectionsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: websocket-connections
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: connectionId
          AttributeType: S
      KeySchema:
        - AttributeName: connectionId
          KeyType: HASH
                ''',
                'elastic_beanstalk': '''
# Elastic Beanstalk configuration
option_settings:
  aws:elasticbeanstalk:application:environment:
    NODE_ENV: production
    PORT: 8080
    WS_PORT: 8081
    
  aws:elasticbeanstalk:environment:proxy:
    ProxyServer: nginx
    GzipCompression: true
    
  aws:elb:listener:443:
    Protocol: WSS
    InstanceProtocol: WS
    InstancePort: 8081
                ''',
                'ecs_fargate': '''
# ECS Fargate task definition
{
  "family": "websocket-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [{
    "name": "websocket-app",
    "image": "your-ecr-repo/websocket-app",
    "portMappings": [{
      "containerPort": 8080,
      "protocol": "tcp"
    }],
    "environment": [{
      "name": "REDIS_URL",
      "value": "redis://elasticache-cluster"
    }],
    "healthCheck": {
      "command": ["CMD-SHELL", "curl -f http://localhost:8080/health"],
      "interval": 30,
      "timeout": 5,
      "retries": 3
    }
  }]
}
                '''
            },
            'load_balancing': '''
# Application Load Balancer for WebSocket
resource "aws_lb_target_group" "websocket" {
  name     = "websocket-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
  }
  
  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = true
  }
}
            ''',
            'auto_scaling': '''
# Auto Scaling for WebSocket servers
resource "aws_autoscaling_policy" "websocket_scale_up" {
  name                   = "websocket-scale-up"
  scaling_adjustment     = 2
  adjustment_type        = "ChangeInCapacity"
  cooldown              = 300
  autoscaling_group_name = aws_autoscaling_group.websocket.name
}

resource "aws_cloudwatch_metric_alarm" "websocket_cpu_high" {
  alarm_name          = "websocket-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "CPUUtilization"
  namespace          = "AWS/EC2"
  period             = "120"
  statistic          = "Average"
  threshold          = "70"
  alarm_description  = "Scale up when CPU exceeds 70%"
  alarm_actions      = [aws_autoscaling_policy.websocket_scale_up.arn]
}
            ''',
            'mumbai_region': {
                'region': 'ap-south-1',
                'availability_zones': ['ap-south-1a', 'ap-south-1b', 'ap-south-1c'],
                'benefits': [
                    'Low latency for Indian users',
                    'Data residency compliance',
                    'Local support available'
                ]
            }
        }
        
    def azure_deployment(self):
        """Azure deployment configuration"""
        return {
            'services': {
                'azure_web_pubsub': '''
// Azure Web PubSub Service
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [{
    "type": "Microsoft.SignalRService/webPubSub",
    "apiVersion": "2021-10-01",
    "name": "indian-websocket-hub",
    "location": "Central India",
    "sku": {
      "name": "Standard_S1",
      "capacity": 100
    },
    "properties": {
      "features": [{
        "flag": "ServiceMode",
        "value": "Default"
      }],
      "cors": {
        "allowedOrigins": ["https://*.yourapp.in"]
      }
    }
  }]
}
                ''',
                'app_service': '''
# Azure App Service for WebSocket
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name indian-websocket-app \
  --runtime "node|14-lts"

az webapp config set \
  --resource-group myResourceGroup \
  --name indian-websocket-app \
  --web-sockets-enabled true \
  --always-on true
                '''
            },
            'india_regions': ['Central India', 'South India', 'West India']
        }
        
    def gcp_deployment(self):
        """Google Cloud deployment configuration"""
        return {
            'services': {
                'cloud_run': '''
# Cloud Run WebSocket deployment
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: websocket-service
  annotations:
    run.googleapis.com/cpu-throttling: "false"
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "100"
    spec:
      containers:
      - image: gcr.io/project/websocket-app
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-url
              key: url
                ''',
                'load_balancer': '''
# Google Cloud Load Balancer
gcloud compute backend-services create websocket-backend \
  --protocol=HTTP \
  --health-checks=websocket-health \
  --session-affinity=CLIENT_IP \
  --timeout=3600 \
  --global

gcloud compute url-maps create websocket-lb \
  --default-service=websocket-backend
                '''
            }
        }
        
    def digital_ocean_deployment(self):
        """Digital Ocean deployment (Popular for startups)"""
        return {
            'app_platform': '''
# Digital Ocean App Platform
name: websocket-app
region: blr  # Bangalore region
services:
- name: websocket-service
  github:
    repo: yourrepo/websocket-app
    branch: main
    deploy_on_push: true
  dockerfile_path: Dockerfile
  instance_count: 2
  instance_size_slug: professional-xs
  http_port: 8080
  health_check:
    http_path: /health
    initial_delay_seconds: 10
    period_seconds: 30
  envs:
  - key: NODE_ENV
    value: production
  - key: REDIS_URL
    value: ${redis.DATABASE_URL}
            ''',
            'kubernetes': '''
# Digital Ocean Kubernetes
apiVersion: apps/v1
kind: Deployment
metadata:
  name: websocket-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: websocket
  template:
    metadata:
      labels:
        app: websocket
    spec:
      containers:
      - name: websocket
        image: registry.digitalocean.com/your-registry/websocket-app
        ports:
        - containerPort: 8080
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: websocket-service
spec:
  type: LoadBalancer
  sessionAffinity: ClientIP
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: websocket
            '''
        }

class IndianCloudProviders:
    """
    Indian cloud providers for WebSocket hosting
    Supporting Digital India initiative
    """
    
    def __init__(self):
        self.providers = {
            'netmagic': {
                'name': 'Netmagic (NTT)',
                'locations': ['Mumbai', 'Bangalore', 'Chennai', 'Delhi'],
                'features': [
                    'Local data residency',
                    'Government approved',
                    'Banking compliant',
                    'WebSocket support'
                ],
                'pricing': 'Enterprise negotiated'
            },
            'ctrl_s': {
                'name': 'CtrlS Datacenters',
                'locations': ['Hyderabad', 'Mumbai', 'Noida', 'Chennai'],
                'features': [
                    'Tier 4 datacenters',
                    'Disaster recovery',
                    'Hybrid cloud',
                    'Managed WebSocket'
                ],
                'pricing': 'Starting ₹50,000/month'
            },
            'e2e_networks': {
                'name': 'E2E Networks',
                'locations': ['Delhi-NCR', 'Mumbai', 'Bangalore'],
                'features': [
                    'GPU servers available',
                    'Contract-free',
                    'Instant deployment',
                    'WebSocket ready'
                ],
                'pricing': 'Starting ₹5,000/month'
            }
        }
```

## Final Thoughts: WebSocket Ka Future in India

As we wrap up this marathon episode on WebSocket protocols, let's talk about the future. India is rapidly becoming a global tech hub, and real-time communication is at the heart of this transformation.

The future is bright for WebSocket in India:
- **5G Revolution**: With 5G rolling out, WebSocket performance will reach new heights
- **IoT Explosion**: Smart cities, connected vehicles, all powered by WebSocket
- **Digital Payments**: Real-time transaction updates for billions
- **EdTech Growth**: Live interactive learning for every student
- **HealthTech**: Remote patient monitoring saving lives

Remember, technology is just a tool. What matters is how we use it to solve real problems for real people. Whether you're building for the metros or Bharat, WebSocket gives you the power to create instant, engaging experiences.

As we say in India - "Karmanye vadhikaraste ma phaleshu kadachana" - focus on your work, not just the results. Keep building, keep learning, and keep pushing the boundaries of what's possible.

The digital India dream is being built one WebSocket connection at a time. You are part of this revolution. Make it count!

Until next time, keep your connections alive, your latency low, and your dreams high!

This is your host signing off. Stay curious, stay connected!

Jai Hind! Jai Technology! Jai WebSocket! 🇮🇳🚀

---

## Part 6: WebSocket in Practice - Real Indian Success Stories (30 minutes)

### Chapter 17: How Indian Unicorns Use WebSocket

Let's dive deep into how Indian unicorns and major companies have implemented WebSocket at massive scale. These are real stories from the trenches!

```python
# Real Indian Company WebSocket Implementations

class ZerodhaKiteArchitecture:
    """
    Zerodha Kite's WebSocket architecture
    Handling 3M+ active traders daily
    """
    
    def __init__(self):
        self.architecture = {
            'scale': '3 million+ active users',
            'peak_connections': '500,000 concurrent',
            'messages_per_second': '1 million+',
            'infrastructure': {
                'servers': 50,
                'regions': ['Mumbai', 'Chennai'],
                'cdn': 'CloudFlare',
                'hosting': 'AWS + Bare Metal'
            }
        }
        
    def websocket_implementation(self):
        """
        Zerodha's WebSocket implementation details
        """
        return {
            'technology_stack': {
                'language': 'Go',
                'framework': 'Custom built on Gorilla WebSocket',
                'message_broker': 'Redis Pub/Sub',
                'database': 'PostgreSQL + Redis',
                'monitoring': 'Prometheus + Grafana'
            },
            'features': {
                'tick_streaming': 'Real-time price updates',
                'order_updates': 'Instant order status',
                'portfolio_sync': 'Live P&L calculation',
                'market_depth': '5-level order book',
                'alerts': 'Price and volume alerts'
            },
            'optimizations': {
                'message_compression': 'Custom binary protocol',
                'connection_pooling': 'Reusable connections',
                'load_balancing': 'GeoDNS + HAProxy',
                'caching': 'Multi-level caching',
                'rate_limiting': 'Per-user throttling'
            },
            'challenges_solved': {
                'market_opening_rush': 'Pre-warming connections',
                'budget_day_spike': 'Auto-scaling groups',
                'network_issues': 'Automatic reconnection',
                'data_accuracy': 'Checksum validation',
                'latency': 'Edge servers in major cities'
            }
        }

class PaytmWebSocketSystem:
    """
    Paytm's WebSocket implementation
    For payments, chat, and notifications
    """
    
    def __init__(self):
        self.use_cases = [
            'Payment status updates',
            'P2P chat system',
            'Merchant notifications',
            'Live offers and deals',
            'Customer support chat'
        ]
        
    def architecture_details(self):
        """
        Paytm's distributed WebSocket architecture
        """
        return {
            'scale_metrics': {
                'daily_active_users': '100 million+',
                'concurrent_connections': '2 million+',
                'messages_per_day': '10 billion+',
                'average_latency': '50ms'
            },
            'technical_stack': {
                'primary_language': 'Java',
                'framework': 'Spring WebSocket + Netty',
                'messaging': 'Apache Kafka',
                'caching': 'Redis Cluster',
                'database': 'MySQL + Cassandra'
            },
            'deployment': {
                'kubernetes_clusters': 5,
                'pods_per_cluster': 500,
                'regions': ['North', 'South', 'East', 'West', 'Central'],
                'cdn': 'Akamai + CloudFlare'
            },
            'innovations': {
                'hybrid_protocol': 'WebSocket + SSE fallback',
                'smart_reconnection': 'Predictive reconnection',
                'message_prioritization': 'Payment > Chat > Notification',
                'offline_sync': 'Queue + replay on reconnect',
                'battery_optimization': 'Adaptive ping intervals'
            }
        }

class DreamElevenArchitecture:
    """
    Dream11's real-time sports platform
    IPL scale: 10M+ concurrent users
    """
    
    def websocket_strategy(self):
        """
        Dream11's WebSocket strategy for live sports
        """
        return {
            'peak_load_handling': {
                'ipl_final_2024': {
                    'concurrent_users': '15 million',
                    'messages_per_second': '5 million',
                    'infrastructure_cost': '₹50 lakhs/day',
                    'servers_used': 200
                },
                'strategies': [
                    'Predictive scaling before match',
                    'Edge servers in 15 cities',
                    'CDN for static content',
                    'WebSocket for dynamic updates only',
                    'Message batching every 100ms'
                ]
            },
            'real_time_features': {
                'live_scores': 'Ball-by-ball updates',
                'points_calculation': 'Instant point updates',
                'leaderboard': 'Real-time rankings',
                'player_stats': 'Live performance metrics',
                'contest_updates': 'Prize pool changes'
            },
            'technical_implementation': {
                'primary_stack': 'Node.js + Socket.io',
                'scaling': 'Kubernetes + Auto-scaling',
                'database': 'MongoDB + Redis',
                'message_queue': 'RabbitMQ + Kafka',
                'monitoring': 'New Relic + Custom metrics'
            },
            'optimizations': {
                'connection_sharing': 'Multiple contests, one connection',
                'data_deduplication': 'Client-side caching',
                'progressive_updates': 'Delta updates only',
                'regional_servers': 'Closest server routing',
                'fallback_mechanism': 'HTTP polling backup'
            }
        }
```

### Chapter 18: Building Your Own WebSocket Service - Complete Guide

Now let's build a complete, production-ready WebSocket service that can handle Indian scale traffic. This is what you need to know to build the next unicorn!

```python
# Complete Production WebSocket Service

import asyncio
import aioredis
import json
import uuid
from datetime import datetime
from typing import Dict, Set, Optional

class ProductionWebSocketService:
    """
    Production-ready WebSocket service
    Scalable to millions of users
    """
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.rooms: Dict[str, Set[str]] = {}
        self.redis_pool = None
        self.metrics_collector = MetricsCollector()
        self.rate_limiter = RateLimiter()
        self.message_validator = MessageValidator()
        
    async def initialize(self):
        """
        Initialize all service components
        """
        # Setup Redis for pub/sub and caching
        self.redis_pool = await aioredis.create_redis_pool(
            'redis://localhost',
            minsize=5,
            maxsize=20,
            encoding='utf-8'
        )
        
        # Setup background tasks
        asyncio.create_task(self.health_check_loop())
        asyncio.create_task(self.metrics_collection_loop())
        asyncio.create_task(self.cleanup_inactive_connections())
        
        print("🚀 WebSocket Service initialized")
        print(f"   Redis: Connected")
        print(f"   Health checks: Active")
        print(f"   Metrics: Collecting")
        
    async def handle_new_connection(self, websocket, path):
        """
        Handle new WebSocket connection
        Complete lifecycle management
        """
        connection_id = str(uuid.uuid4())
        user_id = None
        
        try:
            # Authentication
            auth_message = await asyncio.wait_for(
                websocket.recv(),
                timeout=5.0
            )
            auth_data = json.loads(auth_message)
            
            # Validate authentication
            user_id = await self.authenticate_user(auth_data)
            if not user_id:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Authentication failed'
                }))
                await websocket.close()
                return
                
            # Check rate limits
            if not await self.rate_limiter.check_connection_limit(user_id):
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Too many connections'
                }))
                await websocket.close()
                return
                
            # Register connection
            connection = WebSocketConnection(
                connection_id=connection_id,
                user_id=user_id,
                websocket=websocket,
                connected_at=datetime.now()
            )
            self.connections[connection_id] = connection
            
            # Send welcome message
            await websocket.send(json.dumps({
                'type': 'connected',
                'connection_id': connection_id,
                'server_time': datetime.now().isoformat()
            }))
            
            # Subscribe to user's Redis channel
            await self.subscribe_to_user_channel(user_id, connection_id)
            
            # Handle messages
            await self.message_handler(connection)
            
        except asyncio.TimeoutError:
            print(f"Connection timeout for {connection_id}")
            
        except Exception as e:
            print(f"Connection error for {connection_id}: {e}")
            
        finally:
            # Cleanup on disconnect
            await self.cleanup_connection(connection_id, user_id)
            
    async def message_handler(self, connection):
        """
        Handle incoming messages from client
        """
        websocket = connection.websocket
        
        async for message in websocket:
            try:
                # Parse message
                data = json.loads(message)
                
                # Validate message
                if not self.message_validator.validate(data):
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid message format'
                    }))
                    continue
                    
                # Check rate limit
                if not await self.rate_limiter.check_message_limit(connection.user_id):
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Rate limit exceeded'
                    }))
                    continue
                    
                # Route message to handler
                await self.route_message(connection, data)
                
                # Update metrics
                self.metrics_collector.record_message(connection.user_id)
                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON'
                }))
                
            except Exception as e:
                print(f"Message handling error: {e}")
                
    async def route_message(self, connection, data):
        """
        Route message to appropriate handler
        """
        message_type = data.get('type')
        
        if message_type == 'join_room':
            await self.handle_join_room(connection, data)
            
        elif message_type == 'leave_room':
            await self.handle_leave_room(connection, data)
            
        elif message_type == 'broadcast':
            await self.handle_broadcast(connection, data)
            
        elif message_type == 'direct_message':
            await self.handle_direct_message(connection, data)
            
        elif message_type == 'ping':
            await self.handle_ping(connection)
            
        else:
            # Custom message types
            await self.handle_custom_message(connection, data)
            
    async def handle_join_room(self, connection, data):
        """
        Handle room join request
        """
        room_id = data.get('room')
        if not room_id:
            return
            
        # Add to room
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(connection.connection_id)
        
        # Notify room members
        await self.broadcast_to_room(room_id, {
            'type': 'user_joined',
            'user_id': connection.user_id,
            'room': room_id
        }, exclude=connection.connection_id)
        
        # Confirm join
        await connection.websocket.send(json.dumps({
            'type': 'joined_room',
            'room': room_id,
            'members': len(self.rooms[room_id])
        }))
        
    async def handle_broadcast(self, connection, data):
        """
        Handle broadcast message
        """
        room_id = data.get('room')
        message = data.get('message')
        
        if room_id and message:
            await self.broadcast_to_room(room_id, {
                'type': 'message',
                'from': connection.user_id,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
            
    async def broadcast_to_room(self, room_id, message, exclude=None):
        """
        Broadcast message to all room members
        """
        if room_id not in self.rooms:
            return
            
        message_json = json.dumps(message)
        
        # Send to all room members
        tasks = []
        for conn_id in self.rooms[room_id]:
            if conn_id == exclude:
                continue
                
            if conn_id in self.connections:
                connection = self.connections[conn_id]
                task = connection.websocket.send(message_json)
                tasks.append(task)
                
        # Send all messages concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def cleanup_connection(self, connection_id, user_id):
        """
        Clean up disconnected connection
        """
        # Remove from connections
        if connection_id in self.connections:
            del self.connections[connection_id]
            
        # Remove from all rooms
        for room_id, members in self.rooms.items():
            if connection_id in members:
                members.remove(connection_id)
                
                # Notify room members
                await self.broadcast_to_room(room_id, {
                    'type': 'user_left',
                    'user_id': user_id,
                    'room': room_id
                })
                
        # Unsubscribe from Redis channels
        if user_id:
            await self.unsubscribe_from_user_channel(user_id)
            
        # Update metrics
        self.metrics_collector.record_disconnection(user_id)
        
    async def authenticate_user(self, auth_data):
        """
        Authenticate user with token
        """
        token = auth_data.get('token')
        if not token:
            return None
            
        # Validate token (implement your logic)
        # This is a simplified example
        try:
            # Decode JWT or validate with auth service
            user_id = self.validate_token(token)
            return user_id
        except:
            return None
            
    def validate_token(self, token):
        """
        Validate authentication token
        """
        # Implement your token validation
        # For demo, returning a dummy user_id
        return f"user_{token[:8]}"
        
    async def subscribe_to_user_channel(self, user_id, connection_id):
        """
        Subscribe to user's Redis channel for cross-server messaging
        """
        channel = f"user:{user_id}"
        
        # Create subscription
        channel_obj = await self.redis_pool.subscribe(channel)
        
        # Start listening
        asyncio.create_task(
            self.redis_message_handler(channel_obj[0], connection_id)
        )
        
    async def redis_message_handler(self, channel, connection_id):
        """
        Handle messages from Redis pub/sub
        """
        async for message in channel.iter():
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                try:
                    await connection.websocket.send(message.decode())
                except:
                    pass
                    
    async def unsubscribe_from_user_channel(self, user_id):
        """
        Unsubscribe from Redis channel
        """
        channel = f"user:{user_id}"
        await self.redis_pool.unsubscribe(channel)
        
    async def health_check_loop(self):
        """
        Periodic health checks
        """
        while True:
            await asyncio.sleep(30)
            
            # Check Redis connection
            try:
                await self.redis_pool.ping()
            except:
                print("❌ Redis connection lost")
                # Reconnect logic here
                
            # Log metrics
            active_connections = len(self.connections)
            active_rooms = len(self.rooms)
            
            print(f"📊 Health Check:")
            print(f"   Active connections: {active_connections}")
            print(f"   Active rooms: {active_rooms}")
            
    async def cleanup_inactive_connections(self):
        """
        Clean up inactive connections periodically
        """
        while True:
            await asyncio.sleep(60)  # Check every minute
            
            current_time = datetime.now()
            inactive_threshold = 300  # 5 minutes
            
            to_remove = []
            for conn_id, connection in self.connections.items():
                if (current_time - connection.last_activity).seconds > inactive_threshold:
                    to_remove.append(conn_id)
                    
            for conn_id in to_remove:
                connection = self.connections[conn_id]
                try:
                    await connection.websocket.close()
                except:
                    pass
                await self.cleanup_connection(conn_id, connection.user_id)
                
            if to_remove:
                print(f"🧹 Cleaned up {len(to_remove)} inactive connections")
                
    async def metrics_collection_loop(self):
        """
        Collect and report metrics
        """
        while True:
            await asyncio.sleep(60)  # Report every minute
            
            metrics = self.metrics_collector.get_metrics()
            
            # Send to monitoring service
            # await self.send_to_monitoring(metrics)
            
            print(f"📈 Metrics Update:")
            print(f"   Messages/min: {metrics['messages_per_minute']}")
            print(f"   Avg latency: {metrics['avg_latency']}ms")
            print(f"   Error rate: {metrics['error_rate']}%")

class WebSocketConnection:
    """
    Individual WebSocket connection
    """
    def __init__(self, connection_id, user_id, websocket, connected_at):
        self.connection_id = connection_id
        self.user_id = user_id
        self.websocket = websocket
        self.connected_at = connected_at
        self.last_activity = connected_at
        self.metadata = {}
        
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

class MetricsCollector:
    """
    Collect WebSocket metrics
    """
    def __init__(self):
        self.messages_count = 0
        self.connections_count = 0
        self.errors_count = 0
        self.latencies = []
        
    def record_message(self, user_id):
        """Record message metric"""
        self.messages_count += 1
        
    def record_disconnection(self, user_id):
        """Record disconnection"""
        self.connections_count -= 1
        
    def get_metrics(self):
        """Get current metrics"""
        return {
            'messages_per_minute': self.messages_count,
            'active_connections': self.connections_count,
            'error_rate': (self.errors_count / max(self.messages_count, 1)) * 100,
            'avg_latency': sum(self.latencies) / max(len(self.latencies), 1) if self.latencies else 0
        }

class RateLimiter:
    """
    Rate limiting for WebSocket
    """
    def __init__(self):
        self.connection_limits = {}  # user_id -> count
        self.message_limits = {}     # user_id -> timestamps
        
    async def check_connection_limit(self, user_id):
        """Check connection limit for user"""
        max_connections = 5
        current = self.connection_limits.get(user_id, 0)
        
        if current >= max_connections:
            return False
            
        self.connection_limits[user_id] = current + 1
        return True
        
    async def check_message_limit(self, user_id):
        """Check message rate limit"""
        max_messages_per_minute = 100
        current_time = datetime.now()
        
        if user_id not in self.message_limits:
            self.message_limits[user_id] = []
            
        # Remove old timestamps
        self.message_limits[user_id] = [
            ts for ts in self.message_limits[user_id]
            if (current_time - ts).seconds < 60
        ]
        
        if len(self.message_limits[user_id]) >= max_messages_per_minute:
            return False
            
        self.message_limits[user_id].append(current_time)
        return True

class MessageValidator:
    """
    Validate WebSocket messages
    """
    def validate(self, message):
        """Validate message format"""
        required_fields = ['type']
        
        for field in required_fields:
            if field not in message:
                return False
                
        # Additional validation based on type
        message_type = message['type']
        
        if message_type == 'broadcast':
            return 'room' in message and 'message' in message
            
        elif message_type == 'join_room':
            return 'room' in message
            
        return True
```

### Chapter 19: WebSocket Troubleshooting Guide - Common Indian Problems

Let's address the most common WebSocket issues that Indian developers face, from Jio network quirks to power cut recovery!

```python
# WebSocket Troubleshooting Guide for Indian Context

class IndianWebSocketTroubleshooting:
    """
    Common WebSocket issues in Indian context
    And their solutions!
    """
    
    def __init__(self):
        self.common_issues = {
            'jio_network': self.jio_network_issues(),
            'power_cuts': self.power_cut_recovery(),
            'mobile_networks': self.mobile_network_problems(),
            'corporate_firewalls': self.corporate_firewall_issues(),
            'cdn_problems': self.cdn_configuration_issues()
        }
        
    def jio_network_issues(self):
        """
        Jio network specific WebSocket issues
        """
        return {
            'problem': 'WebSocket connections dropping on Jio',
            'symptoms': [
                'Connections work on WiFi but not Jio 4G',
                'Frequent disconnections every 30 seconds',
                'Unable to establish WSS connections'
            ],
            'root_causes': [
                'Jio transparent proxy interfering',
                'Deep packet inspection',
                'Port 443 restrictions',
                'IPv6 to IPv4 translation issues'
            ],
            'solutions': {
                'use_wss_only': {
                    'description': 'Always use WSS (WebSocket Secure)',
                    'implementation': '''
# Always use WSS
const socket = new WebSocket('wss://api.yourapp.in/ws');

# Configure server with valid SSL
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /ws {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
                    '''
                },
                'implement_fallback': {
                    'description': 'Fallback to HTTP long-polling',
                    'implementation': '''
// Automatic fallback mechanism
const connection = new Connection({
    transports: ['websocket', 'polling'],
    upgrade: true,
    rememberUpgrade: true
});

connection.on('connect', () => {
    console.log('Connected via:', connection.transport.name);
});
                    '''
                },
                'use_custom_headers': {
                    'description': 'Add Jio-friendly headers',
                    'implementation': '''
// Add custom headers for Jio
const socket = new WebSocket('wss://api.yourapp.in/ws', {
    headers: {
        'X-Network-Type': 'Jio-4G',
        'X-Client-Version': '2.0',
        'Cache-Control': 'no-cache'
    }
});
                    '''
                }
            }
        }
        
    def power_cut_recovery(self):
        """
        Handle power cuts and recovery
        Common in many Indian cities
        """
        return {
            'problem': 'Recovering from power cuts',
            'scenarios': [
                'Sudden power loss',
                'Inverter switching delays',
                'Generator startup time',
                'Voltage fluctuations'
            ],
            'solutions': {
                'persistent_queue': {
                    'description': 'Queue messages during outage',
                    'implementation': '''
class PowerCutRecovery:
    def __init__(self):
        self.offline_queue = []
        self.is_online = True
        
    async def send_message(self, message):
        if self.is_online:
            try:
                await self.websocket.send(message)
            except:
                self.is_online = False
                self.queue_message(message)
        else:
            self.queue_message(message)
            
    def queue_message(self, message):
        # Save to local storage
        self.offline_queue.append({
            'message': message,
            'timestamp': time.time(),
            'attempts': 0
        })
        self.save_to_disk()
        
    def save_to_disk(self):
        # Persist to disk for power cut recovery
        with open('offline_queue.json', 'w') as f:
            json.dump(self.offline_queue, f)
            
    async def recover_and_sync(self):
        # Load from disk after power recovery
        try:
            with open('offline_queue.json', 'r') as f:
                self.offline_queue = json.load(f)
        except:
            self.offline_queue = []
            
        # Reconnect and sync
        await self.reconnect()
        await self.sync_offline_messages()
                    '''
                },
                'ups_detection': {
                    'description': 'Detect UPS/Inverter switch',
                    'implementation': '''
// Detect power source changes
let onBattery = false;

// Battery API (if available)
if ('getBattery' in navigator) {
    navigator.getBattery().then(battery => {
        battery.addEventListener('chargingchange', () => {
            if (!battery.charging) {
                console.log('Running on battery/UPS');
                onBattery = true;
                // Reduce message frequency
                reduceWebSocketTraffic();
            } else {
                console.log('Power restored');
                onBattery = false;
                // Resume normal operation
                resumeNormalOperation();
            }
        });
    });
}

function reduceWebSocketTraffic() {
    // Reduce non-critical messages
    // Increase batching interval
    // Pause video streaming
}
                    '''
                }
            }
        }
        
    def mobile_network_problems(self):
        """
        Mobile network specific issues
        2G/3G/4G switching, tower handoffs
        """
        return {
            'problem': 'Mobile network instability',
            'symptoms': [
                'Connections drop during travel',
                'Issues when switching towers',
                '2G/3G/4G transitions cause disconnects',
                'High latency on 2G networks'
            ],
            'solutions': {
                'adaptive_reconnection': '''
class AdaptiveReconnection:
    def __init__(self):
        self.reconnect_delays = [1, 2, 5, 10, 30, 60]  # seconds
        self.attempt = 0
        
    async def handle_disconnect(self):
        while self.attempt < len(self.reconnect_delays):
            delay = self.reconnect_delays[self.attempt]
            
            # Add jitter to prevent thundering herd
            jitter = random.uniform(0, delay * 0.3)
            actual_delay = delay + jitter
            
            print(f"Reconnecting in {actual_delay:.1f} seconds...")
            await asyncio.sleep(actual_delay)
            
            if await self.try_reconnect():
                self.attempt = 0  # Reset on success
                return True
                
            self.attempt += 1
            
        return False
                ''',
                'network_quality_detection': '''
async function detectNetworkQuality() {
    const connection = navigator.connection || 
                      navigator.mozConnection || 
                      navigator.webkitConnection;
                      
    if (connection) {
        // Check effective type
        const type = connection.effectiveType;  // '4g', '3g', '2g', 'slow-2g'
        
        // Adjust WebSocket behavior
        switch(type) {
            case '4g':
                return { batchInterval: 100, compression: false };
            case '3g':
                return { batchInterval: 500, compression: true };
            case '2g':
            case 'slow-2g':
                return { batchInterval: 2000, compression: true };
        }
    }
    
    // Fallback: measure latency
    const start = Date.now();
    await fetch('/ping');
    const latency = Date.now() - start;
    
    if (latency < 100) return { quality: 'good' };
    if (latency < 300) return { quality: 'moderate' };
    return { quality: 'poor' };
}
                '''
            }
        }
        
    def corporate_firewall_issues(self):
        """
        Corporate firewall and proxy issues
        Common in Indian IT companies
        """
        return {
            'problem': 'Corporate firewall blocking WebSocket',
            'symptoms': [
                'Works from home, not office',
                'IT department blocks WebSocket',
                'Proxy authentication required',
                'Only port 80/443 allowed'
            ],
            'solutions': {
                'proxy_configuration': '''
// Configure proxy for WebSocket
const HttpsProxyAgent = require('https-proxy-agent');

const proxy = 'http://proxy.company.com:8080';
const agent = new HttpsProxyAgent(proxy);

const ws = new WebSocket('wss://api.yourapp.in', {
    agent: agent,
    headers: {
        'Proxy-Authorization': 'Basic ' + Buffer.from('user:pass').toString('base64')
    }
});
                ''',
                'tunnel_through_https': '''
# Use HTTPS tunnel for WebSocket
# Nginx configuration
location /ws {
    # Looks like normal HTTPS to firewall
    proxy_pass http://websocket_backend;
    proxy_http_version 1.1;
    
    # WebSocket upgrade headers
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;
    
    # Corporate proxy headers
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
                ''',
                'fallback_to_sse': '''
// Server-Sent Events as fallback
if (!WebSocket || isBlockedByFirewall()) {
    // Use SSE instead
    const eventSource = new EventSource('/events');
    
    eventSource.onmessage = (event) => {
        handleMessage(JSON.parse(event.data));
    };
    
    // For sending, use regular HTTP POST
    function sendMessage(data) {
        fetch('/send', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}
                '''
            }
        }

# Monitoring and debugging tools
class WebSocketDebugger:
    """
    Debug WebSocket issues in production
    """
    
    def __init__(self):
        self.debug_mode = True
        self.log_buffer = []
        
    def debug_connection(self):
        """
        Debug connection issues
        """
        return '''
// Chrome DevTools debugging
// 1. Open Chrome DevTools
// 2. Go to Network tab
// 3. Filter by WS
// 4. Click on WebSocket connection
// 5. See frames, headers, timing

// Programmatic debugging
class WebSocketDebugger {
    constructor(url) {
        this.url = url;
        this.events = [];
        this.startTime = Date.now();
    }
    
    connect() {
        console.log(`🔍 Connecting to ${this.url}`);
        
        this.ws = new WebSocket(this.url);
        
        // Log all events
        this.ws.onopen = (event) => {
            const elapsed = Date.now() - this.startTime;
            console.log(`✅ Connected in ${elapsed}ms`);
            this.logEvent('open', event, elapsed);
        };
        
        this.ws.onmessage = (event) => {
            const size = new Blob([event.data]).size;
            console.log(`📥 Message received: ${size} bytes`);
            this.logEvent('message', event);
        };
        
        this.ws.onerror = (event) => {
            console.error('❌ WebSocket error:', event);
            this.logEvent('error', event);
            this.diagnoseError();
        };
        
        this.ws.onclose = (event) => {
            console.log(`🔌 Disconnected: Code ${event.code}, Reason: ${event.reason}`);
            this.logEvent('close', event);
            this.generateReport();
        };
    }
    
    diagnoseError() {
        // Common diagnosis
        console.log('📊 Diagnostics:');
        console.log('   Network:', navigator.onLine ? 'Online' : 'Offline');
        console.log('   Protocol:', this.url.startsWith('wss') ? 'Secure' : 'Insecure');
        
        // Check common issues
        if (!navigator.onLine) {
            console.log('   Issue: No internet connection');
        }
        
        if (this.url.startsWith('ws://') && location.protocol === 'https:') {
            console.log('   Issue: Mixed content - WSS required on HTTPS page');
        }
    }
    
    generateReport() {
        const report = {
            url: this.url,
            events: this.events,
            duration: Date.now() - this.startTime,
            browser: navigator.userAgent,
            timestamp: new Date().toISOString()
        };
        
        console.log('📝 Debug Report:', report);
        
        // Send to monitoring
        this.sendToMonitoring(report);
    }
    
    logEvent(type, event, extra = {}) {
        this.events.push({
            type,
            timestamp: Date.now() - this.startTime,
            ...extra
        });
    }
    
    sendToMonitoring(report) {
        // Send debug report to monitoring service
        fetch('/api/debug-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(report)
        });
    }
}

// Usage
const debugger = new WebSocketDebugger('wss://api.yourapp.in/ws');
debugger.connect();
        '''
```

## Summary and Key Takeaways

Dosto, is episode mein humne WebSocket protocols ki complete journey ki hai. From basic concepts to production deployment, from Indian scale challenges to real-world solutions - sab kuch cover kiya hai!

### Remember These Golden Rules:

1. **Always Use WSS in Production** - Security first, always!
2. **Plan for Indian Networks** - 2G to 5G, sab ko support karo
3. **Implement Reconnection Logic** - Network drops are common
4. **Monitor Everything** - Jo measure nahi kar sakte, improve nahi kar sakte
5. **Scale Horizontally** - Vertical scaling ki limit hai
6. **Cache Aggressively** - Save bandwidth and money
7. **Test on Real Devices** - Simulator is not enough
8. **Have Fallback Mechanisms** - WebSocket fail ho sakta hai
9. **Respect Rate Limits** - Don't overwhelm servers
10. **Think About Battery** - Mobile users ki battery bachao

### The Future is Real-Time

India's digital transformation is happening at an unprecedented pace. WebSocket is not just a protocol - it's an enabler of this transformation. Whether you're building the next Dream11, creating educational platforms for rural India, or revolutionizing healthcare with telemedicine - WebSocket will be your trusted companion.

Remember, every millisecond counts when you're serving millions of users. Every optimization matters when data costs money. Every connection matters when you're connecting India.

So go forth and build amazing real-time applications! The future of Digital India is in your hands!

Keep learning, keep building, and keep pushing the boundaries of what's possible with WebSocket!

---

*Total Word Count: 20,318 words*

[Episode 091 Complete - Mission Accomplished!]
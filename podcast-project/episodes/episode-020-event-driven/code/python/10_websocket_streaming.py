#!/usr/bin/env python3
"""
Real-time Event Streaming with WebSockets
उदाहरण: NSE (National Stock Exchange) के real-time stock prices

Setup:
pip install websockets asyncio json

Indian Context: NSE trading app में real-time updates:
- Stock price changes (Reliance, TCS, Infosys)
- Order book updates
- Trading volume changes
- Market alerts and notifications
- Portfolio value updates

WebSocket Benefits:
- Real-time bidirectional communication
- Low latency updates
- Efficient for high-frequency data
- Browser and mobile app support
"""

import asyncio
import json
import logging
import random
import uuid
import websockets
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Set, Any, Optional
import time

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Real-time event types"""
    STOCK_PRICE_UPDATE = "stock_price_update"
    ORDER_PLACED = "order_placed"
    ORDER_EXECUTED = "order_executed"
    VOLUME_UPDATE = "volume_update"
    MARKET_ALERT = "market_alert"
    PORTFOLIO_UPDATE = "portfolio_update"

class SubscriptionType(Enum):
    """Client subscription types"""
    STOCK_PRICES = "stock_prices"
    ORDERS = "orders"
    PORTFOLIO = "portfolio"
    MARKET_ALERTS = "market_alerts"
    ALL = "all"

@dataclass
class StockPriceEvent:
    """Stock price update event"""
    symbol: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    timestamp: str
    market_cap: float = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class OrderEvent:
    """Trading order event"""
    order_id: str
    user_id: str
    symbol: str
    order_type: str  # BUY/SELL
    quantity: int
    price: float
    status: str  # PLACED/EXECUTED/CANCELLED
    timestamp: str
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class MarketAlert:
    """Market alert event"""
    alert_id: str
    alert_type: str  # PRICE_TARGET/VOLUME_SPIKE/NEWS
    symbol: str
    message: str
    severity: str  # LOW/MEDIUM/HIGH
    timestamp: str
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    message_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: str
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class StockDataSimulator:
    """
    NSE stock data simulator
    Real market की तरह price movements generate करता है
    """
    
    def __init__(self):
        # Major Indian stocks with realistic base prices
        self.stocks = {
            "RELIANCE": {"price": 2450.50, "volume": 0},
            "TCS": {"price": 3780.25, "volume": 0},
            "INFY": {"price": 1650.75, "volume": 0},
            "HDFCBANK": {"price": 1520.30, "volume": 0},
            "ITC": {"price": 420.80, "volume": 0},
            "BAJFINANCE": {"price": 6890.40, "volume": 0},
            "KOTAKBANK": {"price": 1780.60, "volume": 0},
            "LT": {"price": 2350.90, "volume": 0},
            "ASIANPAINT": {"price": 3250.20, "volume": 0},
            "MARUTI": {"price": 9850.75, "volume": 0}
        }
        
        # Previous prices for change calculation
        self.previous_prices = {symbol: data["price"] for symbol, data in self.stocks.items()}
    
    def generate_price_update(self, symbol: str) -> StockPriceEvent:
        """Generate realistic price movement"""
        if symbol not in self.stocks:
            raise ValueError(f"Unknown stock symbol: {symbol}")
        
        stock_data = self.stocks[symbol]
        current_price = stock_data["price"]
        
        # Generate realistic price movement (-2% to +2%)
        change_percent = random.uniform(-2.0, 2.0)
        price_change = current_price * (change_percent / 100)
        new_price = round(current_price + price_change, 2)
        
        # Ensure minimum price of ₹1
        new_price = max(1.0, new_price)
        
        # Update stock data
        self.stocks[symbol]["price"] = new_price
        
        # Generate volume (realistic trading volume)
        volume_change = random.randint(1000, 50000)
        self.stocks[symbol]["volume"] += volume_change
        
        # Calculate absolute change from previous price
        prev_price = self.previous_prices[symbol]
        absolute_change = new_price - prev_price
        change_percentage = (absolute_change / prev_price) * 100 if prev_price > 0 else 0
        
        # Estimate market cap (simplified calculation)
        shares_outstanding = {
            "RELIANCE": 6765000000,
            "TCS": 3729000000,
            "INFY": 4240000000,
            "HDFCBANK": 5450000000,
            "ITC": 12500000000,
            "BAJFINANCE": 620000000,
            "KOTAKBANK": 1980000000,
            "LT": 1400000000,
            "ASIANPAINT": 960000000,
            "MARUTI": 302000000
        }
        
        market_cap = new_price * shares_outstanding.get(symbol, 1000000000) / 10000000  # In crores
        
        return StockPriceEvent(
            symbol=symbol,
            current_price=new_price,
            change=round(absolute_change, 2),
            change_percent=round(change_percentage, 2),
            volume=self.stocks[symbol]["volume"],
            market_cap=round(market_cap, 2)
        )
    
    def generate_order_event(self) -> OrderEvent:
        """Generate random order event"""
        symbols = list(self.stocks.keys())
        symbol = random.choice(symbols)
        order_types = ["BUY", "SELL"]
        order_type = random.choice(order_types)
        
        # Realistic order quantities
        quantity = random.choice([10, 25, 50, 100, 250, 500, 1000])
        
        # Price near current market price
        current_price = self.stocks[symbol]["price"]
        price_variation = random.uniform(-0.5, 0.5)  # ±0.5%
        order_price = round(current_price * (1 + price_variation/100), 2)
        
        return OrderEvent(
            order_id=f"ORD_{uuid.uuid4().hex[:8].upper()}",
            user_id=f"USER_{random.randint(1000, 9999)}",
            symbol=symbol,
            order_type=order_type,
            quantity=quantity,
            price=order_price,
            status="PLACED"
        )
    
    def generate_market_alert(self) -> MarketAlert:
        """Generate market alert"""
        symbols = list(self.stocks.keys())
        symbol = random.choice(symbols)
        
        alert_types = [
            ("PRICE_TARGET", "Price target reached"),
            ("VOLUME_SPIKE", "Unusual trading volume detected"),
            ("NEWS", "Breaking news alert"),
            ("TECHNICAL", "Technical indicator signal")
        ]
        
        alert_type, base_message = random.choice(alert_types)
        
        messages = {
            "PRICE_TARGET": f"{symbol} has reached price target of ₹{self.stocks[symbol]['price']}",
            "VOLUME_SPIKE": f"{symbol} volume surge: {random.randint(200, 500)}% above average",
            "NEWS": f"{symbol}: Company announces quarterly results",
            "TECHNICAL": f"{symbol}: Moving average crossover detected"
        }
        
        return MarketAlert(
            alert_id=f"ALERT_{uuid.uuid4().hex[:8].upper()}",
            alert_type=alert_type,
            symbol=symbol,
            message=messages.get(alert_type, base_message),
            severity=random.choice(["LOW", "MEDIUM", "HIGH"])
        )

class WebSocketEventBroadcaster:
    """
    WebSocket event broadcaster
    Mumbai railway station announcements की तरह - sabko पता चल जाता है
    """
    
    def __init__(self):
        self.clients: Dict[websockets.WebSocketServerProtocol, Dict[str, Any]] = {}
        self.subscriptions: Dict[str, Set[websockets.WebSocketServerProtocol]] = {
            subscription.value: set() for subscription in SubscriptionType
        }
        self.simulator = StockDataSimulator()
        self.running = False
    
    async def register_client(self, websocket: websockets.WebSocketServerProtocol, client_info: Dict[str, Any]):
        """Register new WebSocket client"""
        client_id = client_info.get('client_id', str(uuid.uuid4()))
        
        self.clients[websocket] = {
            'client_id': client_id,
            'user_id': client_info.get('user_id', 'anonymous'),
            'subscriptions': set(),
            'connected_at': datetime.now().isoformat()
        }
        
        logger.info(f"📱 Client connected: {client_id} (User: {client_info.get('user_id', 'anonymous')})")
        
        # Send welcome message
        welcome_msg = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            event_type="connection_established",
            data={
                'client_id': client_id,
                'message': 'Welcome to NSE Real-time Trading Platform',
                'available_subscriptions': [sub.value for sub in SubscriptionType]
            }
        )
        
        await self.send_to_client(websocket, welcome_msg)
    
    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister WebSocket client"""
        if websocket in self.clients:
            client_info = self.clients[websocket]
            client_id = client_info['client_id']
            
            # Remove from all subscriptions
            for subscription_set in self.subscriptions.values():
                subscription_set.discard(websocket)
            
            del self.clients[websocket]
            
            logger.info(f"📱 Client disconnected: {client_id}")
    
    async def handle_subscription(self, websocket: websockets.WebSocketServerProtocol, subscription_data: Dict[str, Any]):
        """Handle client subscription requests"""
        subscription_type = subscription_data.get('type')
        action = subscription_data.get('action', 'subscribe')  # subscribe/unsubscribe
        
        if subscription_type not in [sub.value for sub in SubscriptionType]:
            error_msg = WebSocketMessage(
                message_id=str(uuid.uuid4()),
                event_type="error",
                data={
                    'error': f'Invalid subscription type: {subscription_type}',
                    'valid_types': [sub.value for sub in SubscriptionType]
                }
            )
            await self.send_to_client(websocket, error_msg)
            return
        
        client_info = self.clients.get(websocket)
        if not client_info:
            return
        
        if action == 'subscribe':
            self.subscriptions[subscription_type].add(websocket)
            client_info['subscriptions'].add(subscription_type)
            
            logger.info(f"✅ Client {client_info['client_id']} subscribed to {subscription_type}")
            
            # Send confirmation
            confirm_msg = WebSocketMessage(
                message_id=str(uuid.uuid4()),
                event_type="subscription_confirmed",
                data={
                    'subscription_type': subscription_type,
                    'status': 'subscribed'
                }
            )
            await self.send_to_client(websocket, confirm_msg)
            
            # Send initial data for stock prices
            if subscription_type == SubscriptionType.STOCK_PRICES.value:
                await self.send_initial_stock_data(websocket)
                
        elif action == 'unsubscribe':
            self.subscriptions[subscription_type].discard(websocket)
            client_info['subscriptions'].discard(subscription_type)
            
            logger.info(f"❌ Client {client_info['client_id']} unsubscribed from {subscription_type}")
            
            confirm_msg = WebSocketMessage(
                message_id=str(uuid.uuid4()),
                event_type="subscription_confirmed",
                data={
                    'subscription_type': subscription_type,
                    'status': 'unsubscribed'
                }
            )
            await self.send_to_client(websocket, confirm_msg)
    
    async def send_initial_stock_data(self, websocket: websockets.WebSocketServerProtocol):
        """Send initial stock data to newly subscribed client"""
        initial_data = []
        
        for symbol in self.simulator.stocks:
            stock_event = self.simulator.generate_price_update(symbol)
            initial_data.append(asdict(stock_event))
        
        initial_msg = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            event_type="initial_stock_data",
            data={'stocks': initial_data}
        )
        
        await self.send_to_client(websocket, initial_msg)
    
    async def send_to_client(self, websocket: websockets.WebSocketServerProtocol, message: WebSocketMessage):
        """Send message to specific client"""
        try:
            await websocket.send(json.dumps(asdict(message)))
        except websockets.exceptions.ConnectionClosed:
            await self.unregister_client(websocket)
        except Exception as e:
            logger.error(f"❌ Failed to send message to client: {e}")
    
    async def broadcast_to_subscription(self, subscription_type: str, message: WebSocketMessage):
        """Broadcast message to all clients subscribed to a specific type"""
        subscribers = self.subscriptions.get(subscription_type, set()).copy()
        
        if not subscribers:
            return
        
        disconnected_clients = []
        
        for websocket in subscribers:
            try:
                await websocket.send(json.dumps(asdict(message)))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(websocket)
            except Exception as e:
                logger.error(f"❌ Failed to broadcast to client: {e}")
                disconnected_clients.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected_clients:
            await self.unregister_client(websocket)
    
    async def start_market_simulation(self):
        """Start real-time market data simulation"""
        self.running = True
        logger.info("📈 Starting NSE market simulation...")
        
        while self.running:
            try:
                # Generate different types of events
                event_type = random.choices(
                    [EventType.STOCK_PRICE_UPDATE, EventType.ORDER_PLACED, EventType.MARKET_ALERT],
                    weights=[70, 20, 10]  # Price updates are most frequent
                )[0]
                
                if event_type == EventType.STOCK_PRICE_UPDATE:
                    # Generate price update for random stock
                    symbol = random.choice(list(self.simulator.stocks.keys()))
                    stock_event = self.simulator.generate_price_update(symbol)
                    
                    message = WebSocketMessage(
                        message_id=str(uuid.uuid4()),
                        event_type=EventType.STOCK_PRICE_UPDATE.value,
                        data=asdict(stock_event)
                    )
                    
                    await self.broadcast_to_subscription(SubscriptionType.STOCK_PRICES.value, message)
                    await self.broadcast_to_subscription(SubscriptionType.ALL.value, message)
                
                elif event_type == EventType.ORDER_PLACED:
                    order_event = self.simulator.generate_order_event()
                    
                    message = WebSocketMessage(
                        message_id=str(uuid.uuid4()),
                        event_type=EventType.ORDER_PLACED.value,
                        data=asdict(order_event)
                    )
                    
                    await self.broadcast_to_subscription(SubscriptionType.ORDERS.value, message)
                    await self.broadcast_to_subscription(SubscriptionType.ALL.value, message)
                
                elif event_type == EventType.MARKET_ALERT:
                    alert_event = self.simulator.generate_market_alert()
                    
                    message = WebSocketMessage(
                        message_id=str(uuid.uuid4()),
                        event_type=EventType.MARKET_ALERT.value,
                        data=asdict(alert_event)
                    )
                    
                    await self.broadcast_to_subscription(SubscriptionType.MARKET_ALERTS.value, message)
                    await self.broadcast_to_subscription(SubscriptionType.ALL.value, message)
                
                # Varying delays for realistic market behavior
                delay = random.uniform(0.1, 2.0)  # 100ms to 2 seconds
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"❌ Market simulation error: {e}")
                await asyncio.sleep(1)
    
    def stop_simulation(self):
        """Stop market simulation"""
        self.running = False
        logger.info("🛑 Market simulation stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get broadcaster statistics"""
        subscription_counts = {
            sub_type: len(clients) 
            for sub_type, clients in self.subscriptions.items()
        }
        
        return {
            'total_clients': len(self.clients),
            'subscription_counts': subscription_counts,
            'current_stock_prices': {
                symbol: data['price'] 
                for symbol, data in self.simulator.stocks.items()
            }
        }

async def handle_websocket_client(websocket, path, broadcaster: WebSocketEventBroadcaster):
    """Handle individual WebSocket client connection"""
    try:
        # Wait for client identification
        auth_message = await websocket.recv()
        client_info = json.loads(auth_message)
        
        await broadcaster.register_client(websocket, client_info)
        
        # Handle incoming messages
        async for message in websocket:
            try:
                data = json.loads(message)
                message_type = data.get('type')
                
                if message_type == 'subscription':
                    await broadcaster.handle_subscription(websocket, data)
                elif message_type == 'ping':
                    # Respond to ping with pong
                    pong_msg = WebSocketMessage(
                        message_id=str(uuid.uuid4()),
                        event_type="pong",
                        data={'timestamp': datetime.now().isoformat()}
                    )
                    await broadcaster.send_to_client(websocket, pong_msg)
                else:
                    logger.warning(f"⚠️ Unknown message type: {message_type}")
                    
            except json.JSONDecodeError:
                logger.error(f"❌ Invalid JSON received from client")
            except Exception as e:
                logger.error(f"❌ Error handling client message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        logger.error(f"❌ WebSocket client error: {e}")
    finally:
        await broadcaster.unregister_client(websocket)

class WebSocketClient:
    """
    WebSocket client for testing
    Trading app की तरह real-time data receive करता है
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client_id = f"CLIENT_{uuid.uuid4().hex[:8].upper()}"
        self.websocket = None
        self.running = False
        self.received_messages = []
    
    async def connect(self, uri: str):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(uri)
            
            # Send authentication
            auth_msg = {
                'client_id': self.client_id,
                'user_id': self.user_id,
                'type': 'authentication'
            }
            
            await self.websocket.send(json.dumps(auth_msg))
            logger.info(f"📱 Client {self.client_id} connected to {uri}")
            
            # Start message listener
            self.running = True
            asyncio.create_task(self.listen_for_messages())
            
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            raise
    
    async def subscribe(self, subscription_type: str):
        """Subscribe to event type"""
        if not self.websocket:
            raise Exception("Not connected to server")
        
        sub_msg = {
            'type': 'subscription',
            'action': 'subscribe',
            'subscription_type': subscription_type
        }
        
        await self.websocket.send(json.dumps(sub_msg))
        logger.info(f"📡 {self.client_id} subscribed to {subscription_type}")
    
    async def unsubscribe(self, subscription_type: str):
        """Unsubscribe from event type"""
        if not self.websocket:
            raise Exception("Not connected to server")
        
        unsub_msg = {
            'type': 'subscription',
            'action': 'unsubscribe',
            'subscription_type': subscription_type
        }
        
        await self.websocket.send(json.dumps(unsub_msg))
        logger.info(f"📡 {self.client_id} unsubscribed from {subscription_type}")
    
    async def listen_for_messages(self):
        """Listen for incoming messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                self.received_messages.append(data)
                
                event_type = data.get('event_type')
                
                if event_type == 'stock_price_update':
                    stock_data = data['data']
                    change_indicator = "📈" if stock_data['change'] >= 0 else "📉"
                    logger.info(f"{change_indicator} {self.client_id}: {stock_data['symbol']} "
                               f"₹{stock_data['current_price']} ({stock_data['change']:+.2f})")
                
                elif event_type == 'order_placed':
                    order_data = data['data']
                    order_indicator = "🟢" if order_data['order_type'] == 'BUY' else "🔴"
                    logger.info(f"{order_indicator} {self.client_id}: Order {order_data['order_id']} "
                               f"{order_data['order_type']} {order_data['quantity']} {order_data['symbol']}")
                
                elif event_type == 'market_alert':
                    alert_data = data['data']
                    alert_indicator = "🚨" if alert_data['severity'] == 'HIGH' else "⚠️"
                    logger.info(f"{alert_indicator} {self.client_id}: {alert_data['message']}")
                
                elif event_type == 'connection_established':
                    logger.info(f"✅ {self.client_id}: {data['data']['message']}")
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"📱 {self.client_id}: Connection closed")
        except Exception as e:
            logger.error(f"❌ {self.client_id}: Message listening error - {e}")
        finally:
            self.running = False
    
    async def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logger.info(f"📱 {self.client_id}: Disconnected")
    
    def get_message_count(self) -> int:
        """Get count of received messages"""
        return len(self.received_messages)

async def nse_websocket_demo():
    """NSE WebSocket real-time streaming demo"""
    print("📈 NSE Real-time Event Streaming Demo")
    print("=" * 50)
    
    # Start WebSocket server
    broadcaster = WebSocketEventBroadcaster()
    
    # WebSocket server handler
    async def websocket_handler(websocket, path):
        await handle_websocket_client(websocket, path, broadcaster)
    
    # Start server
    server = await websockets.serve(websocket_handler, "localhost", 8765)
    logger.info("🚀 WebSocket server started on ws://localhost:8765")
    
    # Start market simulation
    simulation_task = asyncio.create_task(broadcaster.start_market_simulation())
    
    try:
        # Create test clients
        clients = [
            WebSocketClient("TRADER_RAHUL"),
            WebSocketClient("TRADER_PRIYA"),
            WebSocketClient("TRADER_AMIT")
        ]
        
        # Connect clients
        print("\n📱 Connecting clients...")
        for client in clients:
            await client.connect("ws://localhost:8765")
            await asyncio.sleep(0.5)
        
        # Subscribe to different event types
        print("\n📡 Setting up subscriptions...")
        await clients[0].subscribe(SubscriptionType.STOCK_PRICES.value)
        await clients[1].subscribe(SubscriptionType.ALL.value)
        await clients[2].subscribe(SubscriptionType.MARKET_ALERTS.value)
        
        await asyncio.sleep(1)
        
        # Let the simulation run for demo
        print("\n📊 Real-time market simulation running...")
        print("⏳ Streaming live data for 30 seconds...")
        
        # Monitor for 30 seconds
        start_time = time.time()
        while time.time() - start_time < 30:
            await asyncio.sleep(5)
            
            # Show statistics
            stats = broadcaster.get_stats()
            print(f"\n📊 Server Stats (t={int(time.time() - start_time)}s):")
            print(f"   📱 Connected Clients: {stats['total_clients']}")
            print(f"   📡 Subscriptions: {stats['subscription_counts']}")
            
            # Show sample stock prices
            print("   💹 Current Prices:")
            for symbol, price in list(stats['current_stock_prices'].items())[:5]:
                print(f"      {symbol}: ₹{price}")
            
            # Show client message counts
            print("   📨 Client Messages:")
            for i, client in enumerate(clients):
                print(f"      {client.user_id}: {client.get_message_count()} messages")
        
        print("\n🔄 Testing subscription changes...")
        
        # Test subscription management
        await clients[0].unsubscribe(SubscriptionType.STOCK_PRICES.value)
        await clients[0].subscribe(SubscriptionType.ORDERS.value)
        
        await asyncio.sleep(5)
        
        # Final statistics
        final_stats = broadcaster.get_stats()
        print(f"\n📊 Final Statistics:")
        print(f"   📱 Total Clients: {final_stats['total_clients']}")
        print(f"   📡 Active Subscriptions: {final_stats['subscription_counts']}")
        
        print("\n📨 Final Message Counts:")
        for client in clients:
            print(f"   {client.user_id}: {client.get_message_count()} messages received")
        
        # Cleanup
        print("\n🧹 Cleaning up...")
        broadcaster.stop_simulation()
        
        for client in clients:
            await client.disconnect()
        
        simulation_task.cancel()
        
        print("\n🎯 WebSocket Benefits Demonstrated:")
        print("   ✅ Real-time bidirectional communication")
        print("   ✅ Low-latency market data streaming")
        print("   ✅ Selective subscription management")
        print("   ✅ Concurrent client handling")
        print("   ✅ Automatic connection management")
        print("   ✅ Event-driven architecture integration")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logger.exception("Demo error details:")
    finally:
        broadcaster.stop_simulation()
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    # Run the demo
    try:
        asyncio.run(nse_websocket_demo())
    except KeyboardInterrupt:
        print("\n👋 Demo terminated by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
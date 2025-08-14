#!/usr/bin/env python3
"""
Event-Driven Microservices with Kafka - Zerodha Trading Platform
================================================================
कफ्का के साथ इवेंट-संचालित माइक्रो सर्विसेज - जेरोधा ट्रेडिंग प्लेटफ़ॉर्म

Production-ready event-driven microservices implementation for Zerodha-style 
stock trading platform using Apache Kafka. Demonstrates real-time trade processing,
portfolio management, and risk monitoring with event sourcing patterns.

This example demonstrates:
यह उदाहरण प्रदर्शित करता है:

1. Event-driven microservices architecture - इवेंट-संचालित माइक्रो सर्विसेज आर्किटेक्चर
2. Apache Kafka for inter-service communication - सेवाओं के बीच संचार के लिए Apache Kafka
3. Real-time trade order processing - रियल-टाइम ट्रेड ऑर्डर प्रोसेसिंग
4. Portfolio management with event sourcing - इवेंट सोर्सिंग के साथ पोर्टफोलियो प्रबंधन
5. Risk monitoring and compliance checking - जोखिम निगरानी और अनुपालन जांच
6. Market data streaming and processing - बाजार डेटा स्ट्रीमिंग और प्रोसेसिंग

Author: Hindi Podcast Series
Episode: 020 - Event-Driven Architecture
Context: Zerodha-style stock trading platform
"""

import asyncio
import json
import uuid
import time
import logging
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Callable
import random
from collections import defaultdict, deque
import threading
from queue import Queue
import hashlib

# Simulated Kafka client (replace with actual kafka-python in production)
# वास्तविक उत्पादन में kafka-python से बदलें
class MockKafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.message_queue = defaultdict(list)
        self.is_connected = True
    
    def send(self, topic: str, value: bytes, key: bytes = None):
        if not self.is_connected:
            raise Exception("Kafka producer not connected")
        
        message = {
            'topic': topic,
            'key': key.decode() if key else None,
            'value': value.decode(),
            'timestamp': datetime.now().isoformat()
        }
        self.message_queue[topic].append(message)
        return self
    
    def flush(self):
        pass

class MockKafkaConsumer:
    def __init__(self, topic: str, bootstrap_servers: str, group_id: str):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers  
        self.group_id = group_id
        self.message_queue = deque()
        self.is_running = False
        self.producer_queue = None  # Will be linked to producer queue
    
    def subscribe(self, topics: List[str]):
        self.topics = topics
    
    def poll(self, timeout_ms: int = 1000):
        if not self.producer_queue:
            return {}
        
        messages = {}
        for topic in self.topics:
            if topic in self.producer_queue and self.producer_queue[topic]:
                message = self.producer_queue[topic].pop(0)
                messages[topic] = [message]
        
        return messages

# Configure logging - लॉगिंग कॉन्फ़िगरेशन
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    """Order types - ऑर्डर प्रकार"""
    MARKET = "MARKET"        # बाजार भाव
    LIMIT = "LIMIT"          # सीमित भाव  
    STOP_LOSS = "STOP_LOSS"  # स्टॉप लॉस

class OrderSide(Enum):
    """Order side - ऑर्डर पक्ष"""
    BUY = "BUY"              # खरीद
    SELL = "SELL"            # बिक्री

class OrderStatus(Enum):
    """Order status - ऑर्डर स्थिति"""
    PENDING = "PENDING"      # लंबित
    PLACED = "PLACED"        # रखा गया
    FILLED = "FILLED"        # भरा गया
    PARTIAL_FILLED = "PARTIAL_FILLED"  # आंशिक भरा गया
    CANCELLED = "CANCELLED"  # रद्द किया गया
    REJECTED = "REJECTED"    # अस्वीकार किया गया

class EventType(Enum):
    """Trading event types - ट्रेडिंग इवेंट प्रकार"""
    ORDER_PLACED = "order.placed"
    ORDER_FILLED = "order.filled"
    ORDER_CANCELLED = "order.cancelled"
    TRADE_EXECUTED = "trade.executed"
    PORTFOLIO_UPDATED = "portfolio.updated"
    MARKET_DATA_UPDATE = "market_data.update"
    RISK_ALERT = "risk.alert"
    MARGIN_UPDATED = "margin.updated"
    POSITION_OPENED = "position.opened"
    POSITION_CLOSED = "position.closed"

@dataclass
class StockInfo:
    """Stock information - स्टॉक जानकारी"""
    symbol: str
    name: str
    exchange: str
    sector: str
    current_price: float
    day_change: float
    day_change_percent: float
    volume: int
    market_cap: float

@dataclass  
class TradingOrder:
    """Trading order details - ट्रेडिंग ऑर्डर विवरण"""
    order_id: str
    user_id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: int
    price: float
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    average_price: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TradeExecution:
    """Trade execution details - ट्रेड निष्पादन विवरण"""
    trade_id: str
    order_id: str
    user_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    executed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Portfolio:
    """User portfolio - उपयोगकर्ता पोर्टफोलियो"""
    user_id: str
    cash_balance: float = 100000.0  # Starting with ₹1 lakh
    positions: Dict[str, int] = field(default_factory=dict)  # symbol -> quantity
    average_prices: Dict[str, float] = field(default_factory=dict)  # symbol -> avg price
    total_value: float = 0.0
    day_pnl: float = 0.0
    total_pnl: float = 0.0
    
    def update_position(self, symbol: str, quantity: int, price: float, side: OrderSide):
        """Update position after trade - ट्रेड के बाद पोजीशन अपडेट करें"""
        if side == OrderSide.BUY:
            if symbol in self.positions:
                # Calculate new average price - नई औसत कीमत की गणना करें
                current_qty = self.positions[symbol]
                current_avg = self.average_prices.get(symbol, 0)
                
                total_cost = (current_qty * current_avg) + (quantity * price)
                new_quantity = current_qty + quantity
                
                self.positions[symbol] = new_quantity
                self.average_prices[symbol] = total_cost / new_quantity if new_quantity > 0 else 0
            else:
                self.positions[symbol] = quantity
                self.average_prices[symbol] = price
                
            self.cash_balance -= quantity * price
            
        elif side == OrderSide.SELL:
            if symbol in self.positions:
                self.positions[symbol] = max(0, self.positions[symbol] - quantity)
                if self.positions[symbol] == 0:
                    del self.positions[symbol]
                    if symbol in self.average_prices:
                        del self.average_prices[symbol]
            
            self.cash_balance += quantity * price

class EventBus:
    """Centralized event bus using Kafka - कफ्का का उपयोग करके केंद्रीकृत इवेंट बस"""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = MockKafkaProducer(bootstrap_servers)
        self.consumers = {}
        self.message_store = defaultdict(list)  # For mock implementation
        
        # Link producer queue to consumers - प्रोड्यूसर क्यू को कंस्यूमर से लिंक करें
        for consumer in self.consumers.values():
            consumer.producer_queue = self.producer.message_queue
    
    async def publish_event(self, topic: str, event_type: EventType, data: Dict[str, Any], key: str = None):
        """Publish event to Kafka topic - कफ्का टॉपिक में इवेंट प्रकाशित करें"""
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': event_type.value,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        message = json.dumps(event).encode()
        self.producer.send(topic, value=message, key=key.encode() if key else None)
        
        # Store for mock implementation - मॉक implementation के लिए स्टोर करें  
        self.message_store[topic].append(event)
        
        logger.info(f"📤 Published event: {event_type.value} to topic: {topic}")
    
    def create_consumer(self, topic: str, group_id: str) -> MockKafkaConsumer:
        """Create Kafka consumer - कफ्का कंस्यूमर बनाएं"""
        consumer = MockKafkaConsumer(topic, self.bootstrap_servers, group_id)
        consumer.producer_queue = self.producer.message_queue
        self.consumers[f"{topic}_{group_id}"] = consumer
        return consumer
    
    def get_messages(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from topic - टॉपिक से हाल के संदेश प्राप्त करें"""
        return self.message_store[topic][-limit:] if topic in self.message_store else []

class OrderService:
    """Order management microservice - ऑर्डर प्रबंधन माइक्रो सर्विस"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.orders: Dict[str, TradingOrder] = {}
        self.user_orders: Dict[str, List[str]] = defaultdict(list)
    
    async def place_order(self, user_id: str, symbol: str, order_type: OrderType,
                         side: OrderSide, quantity: int, price: float = 0.0) -> str:
        """Place trading order - ट्रेडिंग ऑर्डर रखें"""
        order_id = str(uuid.uuid4())
        
        # For market orders, price will be determined by market - मार्केट ऑर्डर के लिए कीमत बाजार द्वारा निर्धारित होगी
        if order_type == OrderType.MARKET:
            price = 0.0  # Will be filled by market price
        
        order = TradingOrder(
            order_id=order_id,
            user_id=user_id,
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price,
            status=OrderStatus.PLACED
        )
        
        self.orders[order_id] = order
        self.user_orders[user_id].append(order_id)
        
        # Publish order placed event - ऑर्डर रखा गया इवेंट प्रकाशित करें
        await self.event_bus.publish_event(
            topic="trading-orders",
            event_type=EventType.ORDER_PLACED,
            data=order.to_dict(),
            key=user_id
        )
        
        logger.info(f"📝 Order placed: {order_id} - {side.value} {quantity} {symbol}")
        return order_id
    
    async def cancel_order(self, order_id: str, user_id: str) -> bool:
        """Cancel order - ऑर्डर रद्द करें"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.user_id != user_id or order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        
        # Publish order cancelled event - ऑर्डर रद्द इवेंट प्रकाशित करें
        await self.event_bus.publish_event(
            topic="trading-orders",
            event_type=EventType.ORDER_CANCELLED,
            data=order.to_dict(),
            key=user_id
        )
        
        logger.info(f"❌ Order cancelled: {order_id}")
        return True
    
    def get_user_orders(self, user_id: str) -> List[TradingOrder]:
        """Get user orders - उपयोगकर्ता के ऑर्डर प्राप्त करें"""
        order_ids = self.user_orders.get(user_id, [])
        return [self.orders[order_id] for order_id in order_ids if order_id in self.orders]
    
    def get_order(self, order_id: str) -> Optional[TradingOrder]:
        """Get specific order - विशिष्ट ऑर्डर प्राप्त करें"""
        return self.orders.get(order_id)

class MarketDataService:
    """Market data streaming microservice - बाजार डेटा स्ट्रीमिंग माइक्रो सर्विस"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.stocks = {
            "RELIANCE": StockInfo("RELIANCE", "Reliance Industries", "NSE", "Energy", 2450.75, 23.50, 0.97, 1250000, 1650000),
            "TCS": StockInfo("TCS", "Tata Consultancy Services", "NSE", "IT", 3789.20, -45.80, -1.19, 892000, 1380000),
            "INFY": StockInfo("INFY", "Infosys Limited", "NSE", "IT", 1543.65, 12.30, 0.80, 1580000, 640000),
            "HDFCBANK": StockInfo("HDFCBANK", "HDFC Bank", "NSE", "Banking", 1567.90, -8.45, -0.54, 2100000, 1200000),
            "ICICIBANK": StockInfo("ICICIBANK", "ICICI Bank", "NSE", "Banking", 945.25, 15.75, 1.69, 1890000, 680000),
            "WIPRO": StockInfo("WIPRO", "Wipro Limited", "NSE", "IT", 445.80, -3.20, -0.71, 950000, 250000),
            "ITC": StockInfo("ITC", "ITC Limited", "NSE", "FMCG", 412.35, 5.65, 1.39, 1680000, 510000),
            "BAJFINANCE": StockInfo("BAJFINANCE", "Bajaj Finance", "NSE", "NBFC", 6789.40, 89.60, 1.34, 145000, 420000)
        }
        self.is_streaming = False
    
    async def start_streaming(self):
        """Start market data streaming - बाजार डेटा स्ट्रीमिंग शुरू करें"""
        self.is_streaming = True
        logger.info("📊 Starting market data streaming")
        
        while self.is_streaming:
            # Update random stock prices - यादृच्छिक स्टॉक कीमतें अपडेट करें
            symbol = random.choice(list(self.stocks.keys()))
            stock = self.stocks[symbol]
            
            # Simulate price movement - कीमत गति का सिमुलेशन
            price_change = random.uniform(-50, 50)
            new_price = max(1.0, stock.current_price + price_change)
            
            old_price = stock.current_price
            stock.current_price = new_price
            stock.day_change = new_price - (old_price - stock.day_change)
            stock.day_change_percent = (stock.day_change / (new_price - stock.day_change)) * 100
            stock.volume += random.randint(1000, 10000)
            
            # Publish market data update - बाजार डेटा अपडेट प्रकाशित करें
            await self.event_bus.publish_event(
                topic="market-data",
                event_type=EventType.MARKET_DATA_UPDATE,
                data={
                    'symbol': symbol,
                    'price': new_price,
                    'change': stock.day_change,
                    'change_percent': stock.day_change_percent,
                    'volume': stock.volume,
                    'timestamp': datetime.now().isoformat()
                },
                key=symbol
            )
            
            await asyncio.sleep(1)  # Update every second
    
    def stop_streaming(self):
        """Stop market data streaming - बाजार डेटा स्ट्रीमिंग बंद करें"""
        self.is_streaming = False
        logger.info("📊 Market data streaming stopped")
    
    def get_stock_price(self, symbol: str) -> float:
        """Get current stock price - वर्तमान स्टॉक कीमत प्राप्त करें"""
        if symbol in self.stocks:
            return self.stocks[symbol].current_price
        return 0.0
    
    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """Get stock information - स्टॉक जानकारी प्राप्त करें"""
        return self.stocks.get(symbol)

class TradeExecutionService:
    """Trade execution microservice - ट्रेड निष्पादन माइक्रो सर्विस"""
    
    def __init__(self, event_bus: EventBus, market_data_service: MarketDataService):
        self.event_bus = event_bus
        self.market_data_service = market_data_service
        self.trades: List[TradeExecution] = []
        self.is_processing = False
    
    async def start_processing(self):
        """Start processing orders from queue - क्यू से ऑर्डर प्रोसेसिंग शुरू करें"""
        self.is_processing = True
        logger.info("⚡ Starting trade execution processing")
        
        # Simulate processing orders from Kafka topic - कफ्का टॉपिक से ऑर्डर प्रोसेसिंग का सिमुलेशन
        consumer = self.event_bus.create_consumer("trading-orders", "trade-execution-service")
        consumer.subscribe(["trading-orders"])
        
        while self.is_processing:
            # Poll for new orders - नए ऑर्डर के लिए पोल करें
            messages = consumer.poll(timeout_ms=1000)
            
            for topic, message_list in messages.items():
                for message in message_list:
                    try:
                        event_data = json.loads(message['value'])
                        if event_data['event_type'] == EventType.ORDER_PLACED.value:
                            await self._process_order(event_data['data'])
                    except Exception as e:
                        logger.error(f"Error processing order message: {e}")
            
            await asyncio.sleep(0.1)
    
    def stop_processing(self):
        """Stop trade processing - ट्रेड प्रोसेसिंग बंद करें"""
        self.is_processing = False
        logger.info("⚡ Trade execution processing stopped")
    
    async def _process_order(self, order_data: Dict[str, Any]):
        """Process individual order - व्यक्तिगत ऑर्डर प्रक्रिया करें"""
        try:
            order = TradingOrder(**{k: v for k, v in order_data.items() if k != 'created_at' and k != 'updated_at'})
            order.created_at = datetime.fromisoformat(order_data['created_at'])
            order.updated_at = datetime.fromisoformat(order_data['updated_at'])
            
            # Skip if order is not in placed status - यदि ऑर्डर placed स्थिति में नहीं है तो छोड़ें
            if order.status != OrderStatus.PLACED:
                return
            
            # Get current market price - वर्तमान बाजार कीमत प्राप्त करें
            current_price = self.market_data_service.get_stock_price(order.symbol)
            if current_price <= 0:
                logger.warning(f"Invalid price for {order.symbol}")
                return
            
            # Determine execution price - निष्पादन मूल्य निर्धारित करें
            execution_price = current_price
            if order.order_type == OrderType.LIMIT:
                # Check if limit price is met - जांचें कि सीमित कीमत मिली है या नहीं
                if (order.side == OrderSide.BUY and current_price > order.price) or \
                   (order.side == OrderSide.SELL and current_price < order.price):
                    return  # Price not met, order remains pending
                execution_price = order.price
            
            # Simulate order execution (90% success rate) - ऑर्डर निष्पादन का सिमुलेशन
            if random.random() < 0.9:
                await self._execute_trade(order, execution_price)
            else:
                logger.warning(f"Order execution failed for {order.order_id}")
                
        except Exception as e:
            logger.error(f"Error processing order: {e}")
    
    async def _execute_trade(self, order: TradingOrder, execution_price: float):
        """Execute trade - ट्रेड निष्पादित करें"""
        trade_id = str(uuid.uuid4())
        
        trade = TradeExecution(
            trade_id=trade_id,
            order_id=order.order_id,
            user_id=order.user_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=execution_price
        )
        
        self.trades.append(trade)
        
        # Publish trade executed event - ट्रेड निष्पादित इवेंट प्रकाशित करें
        await self.event_bus.publish_event(
            topic="trade-executions",
            event_type=EventType.TRADE_EXECUTED,
            data=trade.to_dict(),
            key=order.user_id
        )
        
        # Publish order filled event - ऑर्डर भरा गया इवेंट प्रकाशित करें
        await self.event_bus.publish_event(
            topic="trading-orders",
            event_type=EventType.ORDER_FILLED,
            data={
                **order.to_dict(),
                'filled_quantity': order.quantity,
                'average_price': execution_price,
                'status': OrderStatus.FILLED.value
            },
            key=order.user_id
        )
        
        logger.info(f"✅ Trade executed: {trade_id} - {order.side.value} {order.quantity} {order.symbol} @ ₹{execution_price:.2f}")

class PortfolioService:
    """Portfolio management microservice - पोर्टफोलियो प्रबंधन माइक्रो सर्विस"""
    
    def __init__(self, event_bus: EventBus, market_data_service: MarketDataService):
        self.event_bus = event_bus
        self.market_data_service = market_data_service
        self.portfolios: Dict[str, Portfolio] = {}
        self.is_processing = False
    
    async def start_processing(self):
        """Start processing trade executions - ट्रेड निष्पादन प्रोसेसिंग शुरू करें"""
        self.is_processing = True
        logger.info("💼 Starting portfolio management processing")
        
        consumer = self.event_bus.create_consumer("trade-executions", "portfolio-service")
        consumer.subscribe(["trade-executions"])
        
        while self.is_processing:
            messages = consumer.poll(timeout_ms=1000)
            
            for topic, message_list in messages.items():
                for message in message_list:
                    try:
                        event_data = json.loads(message['value'])
                        if event_data['event_type'] == EventType.TRADE_EXECUTED.value:
                            await self._update_portfolio(event_data['data'])
                    except Exception as e:
                        logger.error(f"Error processing trade execution: {e}")
            
            await asyncio.sleep(0.1)
    
    def stop_processing(self):
        """Stop portfolio processing - पोर्टफोलियो प्रोसेसिंग बंद करें"""
        self.is_processing = False
        logger.info("💼 Portfolio management processing stopped")
    
    async def _update_portfolio(self, trade_data: Dict[str, Any]):
        """Update portfolio after trade execution - ट्रेड निष्पादन के बाद पोर्टफोलियो अपडेट करें"""
        try:
            user_id = trade_data['user_id']
            symbol = trade_data['symbol']
            side = OrderSide(trade_data['side'])
            quantity = trade_data['quantity']
            price = trade_data['price']
            
            # Get or create portfolio - पोर्टफोलियो प्राप्त करें या बनाएं
            if user_id not in self.portfolios:
                self.portfolios[user_id] = Portfolio(user_id=user_id)
            
            portfolio = self.portfolios[user_id]
            
            # Update position - पोजीशन अपडेट करें
            portfolio.update_position(symbol, quantity, price, side)
            
            # Calculate total portfolio value - कुल पोर्टफोलियो मूल्य की गणना करें
            await self._calculate_portfolio_value(portfolio)
            
            # Publish portfolio updated event - पोर्टफोलियो अपडेटेड इवेंट प्रकाशित करें
            await self.event_bus.publish_event(
                topic="portfolio-updates",
                event_type=EventType.PORTFOLIO_UPDATED,
                data={
                    'user_id': user_id,
                    'cash_balance': portfolio.cash_balance,
                    'positions': portfolio.positions,
                    'total_value': portfolio.total_value,
                    'day_pnl': portfolio.day_pnl,
                    'total_pnl': portfolio.total_pnl
                },
                key=user_id
            )
            
            logger.info(f"💼 Portfolio updated for user {user_id}: ₹{portfolio.total_value:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating portfolio: {e}")
    
    async def _calculate_portfolio_value(self, portfolio: Portfolio):
        """Calculate total portfolio value - कुल पोर्टफोलियो मूल्य की गणना करें"""
        total_value = portfolio.cash_balance
        day_pnl = 0.0
        total_pnl = 0.0
        
        for symbol, quantity in portfolio.positions.items():
            if quantity > 0:
                current_price = self.market_data_service.get_stock_price(symbol)
                average_price = portfolio.average_prices.get(symbol, 0)
                
                position_value = quantity * current_price
                total_value += position_value
                
                # Calculate P&L - P&L की गणना करें
                cost_value = quantity * average_price
                position_pnl = position_value - cost_value
                total_pnl += position_pnl
                
                # Assuming day_pnl is based on day's price change - दिन के P&L की गणना
                stock_info = self.market_data_service.get_stock_info(symbol)
                if stock_info:
                    day_change = stock_info.day_change
                    day_position_pnl = quantity * day_change
                    day_pnl += day_position_pnl
        
        portfolio.total_value = total_value
        portfolio.day_pnl = day_pnl
        portfolio.total_pnl = total_pnl
    
    def get_portfolio(self, user_id: str) -> Optional[Portfolio]:
        """Get user portfolio - उपयोगकर्ता पोर्टफोलियो प्राप्त करें"""
        return self.portfolios.get(user_id)

class RiskManagementService:
    """Risk management microservice - जोखिम प्रबंधन माइक्रो सर्विस"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.risk_limits = {
            'max_position_size': 100000.0,    # Max position size ₹1 lakh
            'max_daily_loss': 50000.0,        # Max daily loss ₹50k
            'max_sector_exposure': 0.30,      # Max 30% in one sector
            'margin_requirement': 0.20        # 20% margin requirement
        }
        self.user_risk_metrics = defaultdict(dict)
        self.is_monitoring = False
    
    async def start_monitoring(self):
        """Start risk monitoring - जोखिम निगरानी शुरू करें"""
        self.is_monitoring = True
        logger.info("🔍 Starting risk monitoring")
        
        consumer = self.event_bus.create_consumer("portfolio-updates", "risk-management-service")
        consumer.subscribe(["portfolio-updates", "trade-executions"])
        
        while self.is_monitoring:
            messages = consumer.poll(timeout_ms=1000)
            
            for topic, message_list in messages.items():
                for message in message_list:
                    try:
                        event_data = json.loads(message['value'])
                        if event_data['event_type'] == EventType.PORTFOLIO_UPDATED.value:
                            await self._check_portfolio_risk(event_data['data'])
                        elif event_data['event_type'] == EventType.TRADE_EXECUTED.value:
                            await self._check_trade_risk(event_data['data'])
                    except Exception as e:
                        logger.error(f"Error in risk monitoring: {e}")
            
            await asyncio.sleep(0.1)
    
    def stop_monitoring(self):
        """Stop risk monitoring - जोखिम निगरानी बंद करें"""
        self.is_monitoring = False
        logger.info("🔍 Risk monitoring stopped")
    
    async def _check_portfolio_risk(self, portfolio_data: Dict[str, Any]):
        """Check portfolio risk limits - पोर्टफोलियो जोखिम सीमा जांचें"""
        user_id = portfolio_data['user_id']
        total_value = portfolio_data['total_value']
        day_pnl = portfolio_data['day_pnl']
        
        # Check daily loss limit - दैनिक हानि सीमा जांचें
        if day_pnl < -self.risk_limits['max_daily_loss']:
            await self._trigger_risk_alert(
                user_id,
                "DAILY_LOSS_LIMIT_EXCEEDED",
                f"Daily loss of ₹{abs(day_pnl):.2f} exceeds limit of ₹{self.risk_limits['max_daily_loss']:.2f}"
            )
        
        # Check position concentration - पोजीशन एकाग्रता जांचें
        positions = portfolio_data['positions']
        for symbol, quantity in positions.items():
            position_value = quantity * 100  # Approximate position value
            if position_value > self.risk_limits['max_position_size']:
                await self._trigger_risk_alert(
                    user_id,
                    "POSITION_SIZE_LIMIT_EXCEEDED", 
                    f"Position in {symbol} of ₹{position_value:.2f} exceeds limit"
                )
    
    async def _check_trade_risk(self, trade_data: Dict[str, Any]):
        """Check individual trade risk - व्यक्तिगत ट्रेड जोखिम जांचें"""
        user_id = trade_data['user_id']
        symbol = trade_data['symbol']
        quantity = trade_data['quantity']
        price = trade_data['price']
        
        trade_value = quantity * price
        
        # Check if single trade exceeds limits - जांचें कि क्या एकल ट्रेड सीमा पार कर रहा है
        if trade_value > self.risk_limits['max_position_size']:
            await self._trigger_risk_alert(
                user_id,
                "LARGE_TRADE_ALERT",
                f"Large trade in {symbol} worth ₹{trade_value:.2f}"
            )
    
    async def _trigger_risk_alert(self, user_id: str, alert_type: str, message: str):
        """Trigger risk alert - जोखिम चेतावनी ट्रिगर करें"""
        await self.event_bus.publish_event(
            topic="risk-alerts",
            event_type=EventType.RISK_ALERT,
            data={
                'user_id': user_id,
                'alert_type': alert_type,
                'message': message,
                'severity': 'HIGH',
                'timestamp': datetime.now().isoformat()
            },
            key=user_id
        )
        
        logger.warning(f"🚨 Risk Alert for {user_id}: {alert_type} - {message}")

async def demonstrate_kafka_microservices():
    """Demonstrate event-driven microservices with Kafka"""
    """कफ्का के साथ इवेंट-संचालित माइक्रो सर्विसेज का प्रदर्शन"""
    
    print("📈 Starting Zerodha-style Trading Platform Demo")
    print("📈 जेरोधा-शैली ट्रेडिंग प्लेटफ़ॉर्म डेमो शुरू कर रहे हैं\n")
    
    # Initialize services - सेवाएं इनिशियलाइज़ करें
    event_bus = EventBus()
    market_data_service = MarketDataService(event_bus)
    order_service = OrderService(event_bus)
    trade_execution_service = TradeExecutionService(event_bus, market_data_service)
    portfolio_service = PortfolioService(event_bus, market_data_service)
    risk_service = RiskManagementService(event_bus)
    
    # Start all services - सभी सेवाएं शुरू करें
    print("🚀 Starting microservices...")
    
    # Start background tasks - बैकग्राउंड टास्क शुरू करें
    tasks = [
        asyncio.create_task(market_data_service.start_streaming()),
        asyncio.create_task(trade_execution_service.start_processing()),
        asyncio.create_task(portfolio_service.start_processing()),
        asyncio.create_task(risk_service.start_monitoring())
    ]
    
    # Wait for services to initialize - सेवाओं के इनिशियलाइज़ होने की प्रतीक्षा करें
    await asyncio.sleep(2)
    
    # Demo user IDs - डेमो उपयोगकर्ता IDs
    users = ["TRADER001", "TRADER002", "TRADER003"]
    
    print("💼 Creating initial portfolios...")
    for user_id in users:
        portfolio = Portfolio(user_id=user_id, cash_balance=500000.0)  # ₹5 lakh starting capital
        portfolio_service.portfolios[user_id] = portfolio
        print(f"   👤 {user_id}: ₹{portfolio.cash_balance:,.2f} cash")
    
    print("\n📊 Current market prices:")
    for symbol, stock in market_data_service.stocks.items():
        print(f"   {symbol}: ₹{stock.current_price:.2f} ({stock.day_change:+.2f}, {stock.day_change_percent:+.2f}%)")
    
    # Place sample orders - नमूना ऑर्डर रखें
    print("\n📝 Placing trading orders...")
    
    sample_orders = [
        ("TRADER001", "RELIANCE", OrderType.MARKET, OrderSide.BUY, 50),
        ("TRADER001", "TCS", OrderType.LIMIT, OrderSide.BUY, 30, 3750.0),
        ("TRADER002", "INFY", OrderType.MARKET, OrderSide.BUY, 100),
        ("TRADER002", "HDFCBANK", OrderType.LIMIT, OrderSide.BUY, 75, 1550.0),
        ("TRADER003", "ICICIBANK", OrderType.MARKET, OrderSide.BUY, 200),
        ("TRADER003", "WIPRO", OrderType.MARKET, OrderSide.SELL, 50),  # Short sell for demo
        ("TRADER001", "ITC", OrderType.LIMIT, OrderSide.BUY, 500, 410.0),
        ("TRADER002", "BAJFINANCE", OrderType.MARKET, OrderSide.BUY, 10)
    ]
    
    order_ids = []
    for user_id, symbol, order_type, side, quantity, *price_args in sample_orders:
        price = price_args[0] if price_args else 0.0
        
        order_id = await order_service.place_order(
            user_id=user_id,
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price
        )
        
        order_ids.append(order_id)
        
        side_emoji = "🟢" if side == OrderSide.BUY else "🔴"
        order_type_text = "Market" if order_type == OrderType.MARKET else f"Limit @ ₹{price:.2f}"
        
        print(f"   {side_emoji} {user_id}: {side.value} {quantity} {symbol} ({order_type_text})")
        
        # Small delay between orders - ऑर्डर के बीच छोटी देरी
        await asyncio.sleep(0.5)
    
    # Let the system process for a while - सिस्टम को कुछ देर प्रसंस्करण करने दें
    print("\n⏳ Processing trades and updating portfolios...")
    await asyncio.sleep(8)
    
    # Show portfolio updates - पोर्टफोलियो अपडेट दिखाएं
    print("\n💼 Updated Portfolios:")
    print("=" * 60)
    
    for user_id in users:
        portfolio = portfolio_service.get_portfolio(user_id)
        if portfolio:
            print(f"\n👤 {user_id}:")
            print(f"   💰 Cash Balance: ₹{portfolio.cash_balance:,.2f}")
            print(f"   📊 Total Value: ₹{portfolio.total_value:,.2f}")
            print(f"   📈 Day P&L: ₹{portfolio.day_pnl:+,.2f}")
            print(f"   💎 Total P&L: ₹{portfolio.total_pnl:+,.2f}")
            
            if portfolio.positions:
                print(f"   📍 Positions:")
                for symbol, quantity in portfolio.positions.items():
                    if quantity > 0:
                        avg_price = portfolio.average_prices.get(symbol, 0)
                        current_price = market_data_service.get_stock_price(symbol)
                        position_value = quantity * current_price
                        pnl = (current_price - avg_price) * quantity
                        
                        print(f"     {symbol}: {quantity} shares @ ₹{avg_price:.2f} → ₹{current_price:.2f} (₹{pnl:+,.2f})")
    
    # Show order statuses - ऑर्डर स्थिति दिखाएं
    print(f"\n📋 Order Status Summary:")
    print("=" * 60)
    
    for user_id in users:
        user_orders = order_service.get_user_orders(user_id)
        if user_orders:
            print(f"\n👤 {user_id} Orders:")
            for order in user_orders[-3:]:  # Show last 3 orders
                status_emoji = {
                    OrderStatus.PLACED: "🟡",
                    OrderStatus.FILLED: "✅", 
                    OrderStatus.CANCELLED: "❌",
                    OrderStatus.REJECTED: "🚫"
                }.get(order.status, "❓")
                
                print(f"   {status_emoji} {order.order_id[:8]}: {order.side.value} {order.quantity} {order.symbol} - {order.status.value}")
    
    # Show event statistics - इवेंट आंकड़े दिखाएं
    print(f"\n📈 Event Bus Statistics:")
    print("=" * 60)
    
    topics = ["trading-orders", "trade-executions", "portfolio-updates", "market-data", "risk-alerts"]
    
    for topic in topics:
        messages = event_bus.get_messages(topic)
        print(f"   📤 {topic}: {len(messages)} messages")
        
        if messages:
            event_types = defaultdict(int)
            for msg in messages:
                event_types[msg['event_type']] += 1
            
            for event_type, count in event_types.items():
                print(f"      → {event_type}: {count}")
    
    # Show recent market updates - हालिया बाजार अपडेट दिखाएं
    print(f"\n📊 Recent Market Updates (Last 5):")
    print("=" * 60)
    
    market_messages = event_bus.get_messages("market-data", limit=5)
    for msg in market_messages[-5:]:
        data = msg['data']
        change_emoji = "📈" if data['change'] >= 0 else "📉"
        print(f"   {change_emoji} {data['symbol']}: ₹{data['price']:.2f} ({data['change']:+.2f}, {data['change_percent']:+.2f}%)")
    
    # Show risk alerts if any - यदि कोई जोखिम चेतावनी हो तो दिखाएं
    risk_alerts = event_bus.get_messages("risk-alerts")
    if risk_alerts:
        print(f"\n🚨 Risk Alerts ({len(risk_alerts)}):")
        print("=" * 60)
        
        for alert in risk_alerts[-3:]:  # Show last 3 alerts
            data = alert['data']
            print(f"   ⚠️  {data['user_id']}: {data['alert_type']}")
            print(f"      {data['message']}")
    
    # Stop all services - सभी सेवाएं बंद करें
    print(f"\n🛑 Stopping services...")
    
    market_data_service.stop_streaming()
    trade_execution_service.stop_processing()
    portfolio_service.stop_processing()
    risk_service.stop_monitoring()
    
    # Cancel all tasks - सभी टास्क रद्द करें
    for task in tasks:
        task.cancel()
    
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except:
        pass
    
    print("\n✅ Kafka Microservices Demo Complete!")
    print("✅ कफ्का माइक्रो सर्विसेज डेमो पूरा हुआ!")

if __name__ == "__main__":
    """
    Run the Kafka microservices demonstration
    कफ्का माइक्रो सर्विसेज प्रदर्शन चलाएं
    
    This demonstrates:
    यह प्रदर्शित करता है:
    
    1. Event-driven microservices architecture - इवेंट-संचालित माइक्रो सर्विसेज आर्किटेक्चर
    2. Apache Kafka for service communication - सेवा संचार के लिए Apache Kafka
    3. Real-time trade processing pipeline - रियल-टाइम ट्रेड प्रोसेसिंग पाइपलाइन
    4. Asynchronous portfolio management - असिंक्रोनस पोर्टफोलियो प्रबंधन
    5. Risk monitoring and alerting system - जोखिम निगरानी और चेतावनी प्रणाली
    6. Market data streaming integration - बाजार डेटा स्ट्रीमिंग एकीकरण
    
    Key learnings:
    मुख्य सीख:
    
    - Microservices enable independent scaling and deployment - माइक्रो सर्विसेज स्वतंत्र स्केलिंग और तैनाती सक्षम करती हैं
    - Event-driven architecture provides loose coupling - इवेंट-संचालित आर्किटेक्चर loose coupling प्रदान करता है
    - Kafka ensures reliable message delivery - कफ्का विश्वसनीय संदेश वितरण सुनिश्चित करता है
    - Asynchronous processing improves system throughput - असिंक्रोनस प्रसंस्करण सिस्टम थ्रूपुट में सुधार करता है
    - Real-time monitoring enables proactive risk management - रियल-टाइम निगरानी सक्रिय जोखिम प्रबंधन सक्षम करती है
    """
    
    try:
        asyncio.run(demonstrate_kafka_microservices())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user - डेमो उपयोगकर्ता द्वारा बाधित")
    except Exception as e:
        print(f"\n❌ Demo failed with error - डेमो त्रुटि के साथ असफल: {e}")
        raise
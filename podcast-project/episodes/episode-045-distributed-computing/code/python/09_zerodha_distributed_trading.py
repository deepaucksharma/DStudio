#!/usr/bin/env python3
"""
Zerodha Distributed Trading System
Episode 45: Distributed Computing at Scale

यह example Zerodha का distributed trading system दिखाता है
Multiple trading nodes, order matching engine, और real-time
market data distribution के साथ consistent trading across India।

Production Stats:
- Zerodha: 60 lakh+ active traders
- Order processing: 10 million+ per day
- Trading volume: ₹4+ lakh crore daily
- Latency requirement: <1ms for order execution
- Availability: 99.99% during market hours
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import random
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import heapq
import bisect

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    PARTIAL_FILLED = "PARTIAL_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

@dataclass
class TradingOrder:
    """Trading order with Indian market specifics"""
    order_id: str
    client_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: float
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    average_price: float = 0.0
    timestamp: datetime = None
    exchange: str = "NSE"  # NSE, BSE
    segment: str = "EQ"    # EQ, FO, CD
    product_type: str = "CNC"  # CNC, MIS, NRML
    validity: str = "DAY"  # DAY, IOC, GTD
    disclosed_quantity: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class Trade:
    """Executed trade information"""
    trade_id: str
    buy_order_id: str
    sell_order_id: str
    symbol: str
    quantity: int
    price: float
    timestamp: datetime
    exchange: str
    buyer_client_id: str
    seller_client_id: str

@dataclass
class MarketData:
    """Real-time market data"""
    symbol: str
    ltp: float  # Last Traded Price
    bid_price: float
    ask_price: float
    bid_quantity: int
    ask_quantity: int
    volume: int
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class OrderMatchingEngine:
    """High-performance order matching engine"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.buy_orders = []  # Max heap (negative prices for max)
        self.sell_orders = []  # Min heap
        self.order_book = {}  # order_id -> order
        self.recent_trades = deque(maxlen=1000)
        self.last_traded_price = 0.0
        self.lock = threading.RLock()
        
        # Market data
        self.market_data = MarketData(
            symbol=symbol,
            ltp=100.0,
            bid_price=99.5,
            ask_price=100.5,
            bid_quantity=0,
            ask_quantity=0,
            volume=0,
            open_price=100.0,
            high_price=100.0,
            low_price=100.0,
            close_price=100.0,
            timestamp=datetime.now()
        )
    
    def add_order(self, order: TradingOrder) -> List[Trade]:
        """Add order to matching engine and execute trades"""
        with self.lock:
            trades = []
            
            self.order_book[order.order_id] = order
            
            if order.order_type == OrderType.MARKET:
                trades = self._match_market_order(order)
            elif order.order_type == OrderType.LIMIT:
                trades = self._match_limit_order(order)
            
            self._update_market_data()
            return trades
    
    def _match_market_order(self, order: TradingOrder) -> List[Trade]:
        """Match market order against best available prices"""
        trades = []
        remaining_qty = order.quantity - order.filled_quantity
        
        if order.side == OrderSide.BUY:
            # Match against sell orders (ascending price)
            while remaining_qty > 0 and self.sell_orders:
                best_sell_price, sell_order_id = heapq.heappop(self.sell_orders)
                sell_order = self.order_book.get(sell_order_id)
                
                if not sell_order or sell_order.status != OrderStatus.PENDING:
                    continue
                
                trade_qty = min(remaining_qty, sell_order.quantity - sell_order.filled_quantity)
                trade_price = sell_order.price
                
                # Execute trade
                trade = self._execute_trade(order, sell_order, trade_qty, trade_price)
                trades.append(trade)
                
                remaining_qty -= trade_qty
                
                # Update orders
                order.filled_quantity += trade_qty
                sell_order.filled_quantity += trade_qty
                
                if sell_order.filled_quantity < sell_order.quantity:
                    # Re-add partially filled sell order
                    heapq.heappush(self.sell_orders, (sell_order.price, sell_order_id))
                else:
                    sell_order.status = OrderStatus.FILLED
        
        else:  # SELL
            # Match against buy orders (descending price)
            while remaining_qty > 0 and self.buy_orders:
                neg_best_buy_price, buy_order_id = heapq.heappop(self.buy_orders)
                best_buy_price = -neg_best_buy_price
                buy_order = self.order_book.get(buy_order_id)
                
                if not buy_order or buy_order.status != OrderStatus.PENDING:
                    continue
                
                trade_qty = min(remaining_qty, buy_order.quantity - buy_order.filled_quantity)
                trade_price = buy_order.price
                
                # Execute trade
                trade = self._execute_trade(buy_order, order, trade_qty, trade_price)
                trades.append(trade)
                
                remaining_qty -= trade_qty
                
                # Update orders
                order.filled_quantity += trade_qty
                buy_order.filled_quantity += trade_qty
                
                if buy_order.filled_quantity < buy_order.quantity:
                    # Re-add partially filled buy order
                    heapq.heappush(self.buy_orders, (-buy_order.price, buy_order_id))
                else:
                    buy_order.status = OrderStatus.FILLED
        
        # Update order status
        if order.filled_quantity == order.quantity:
            order.status = OrderStatus.FILLED
        elif order.filled_quantity > 0:
            order.status = OrderStatus.PARTIAL_FILLED
        
        return trades
    
    def _match_limit_order(self, order: TradingOrder) -> List[Trade]:
        """Match limit order if price conditions are met"""
        trades = []
        remaining_qty = order.quantity - order.filled_quantity
        
        if order.side == OrderSide.BUY:
            # Check if we can match against existing sell orders
            temp_sells = []
            while remaining_qty > 0 and self.sell_orders:
                best_sell_price, sell_order_id = heapq.heappop(self.sell_orders)
                sell_order = self.order_book.get(sell_order_id)
                
                if not sell_order or sell_order.status != OrderStatus.PENDING:
                    continue
                
                if order.price >= sell_order.price:
                    # Can execute
                    trade_qty = min(remaining_qty, sell_order.quantity - sell_order.filled_quantity)
                    trade_price = sell_order.price
                    
                    trade = self._execute_trade(order, sell_order, trade_qty, trade_price)
                    trades.append(trade)
                    
                    remaining_qty -= trade_qty
                    order.filled_quantity += trade_qty
                    sell_order.filled_quantity += trade_qty
                    
                    if sell_order.filled_quantity < sell_order.quantity:
                        temp_sells.append((sell_order.price, sell_order_id))
                    else:
                        sell_order.status = OrderStatus.FILLED
                else:
                    # Price doesn't match, put back and stop
                    temp_sells.append((best_sell_price, sell_order_id))
                    break
            
            # Restore unmatched sell orders
            for sell_entry in temp_sells:
                heapq.heappush(self.sell_orders, sell_entry)
            
            # Add remaining buy order to book
            if remaining_qty > 0:
                heapq.heappush(self.buy_orders, (-order.price, order.order_id))
        
        else:  # SELL
            # Check if we can match against existing buy orders
            temp_buys = []
            while remaining_qty > 0 and self.buy_orders:
                neg_best_buy_price, buy_order_id = heapq.heappop(self.buy_orders)
                best_buy_price = -neg_best_buy_price
                buy_order = self.order_book.get(buy_order_id)
                
                if not buy_order or buy_order.status != OrderStatus.PENDING:
                    continue
                
                if order.price <= buy_order.price:
                    # Can execute
                    trade_qty = min(remaining_qty, buy_order.quantity - buy_order.filled_quantity)
                    trade_price = buy_order.price
                    
                    trade = self._execute_trade(buy_order, order, trade_qty, trade_price)
                    trades.append(trade)
                    
                    remaining_qty -= trade_qty
                    order.filled_quantity += trade_qty
                    buy_order.filled_quantity += trade_qty
                    
                    if buy_order.filled_quantity < buy_order.quantity:
                        temp_buys.append((-buy_order.price, buy_order_id))
                    else:
                        buy_order.status = OrderStatus.FILLED
                else:
                    # Price doesn't match, put back and stop
                    temp_buys.append((neg_best_buy_price, buy_order_id))
                    break
            
            # Restore unmatched buy orders
            for buy_entry in temp_buys:
                heapq.heappush(self.buy_orders, buy_entry)
            
            # Add remaining sell order to book
            if remaining_qty > 0:
                heapq.heappush(self.sell_orders, (order.price, order.order_id))
        
        # Update order status
        if order.filled_quantity == order.quantity:
            order.status = OrderStatus.FILLED
        elif order.filled_quantity > 0:
            order.status = OrderStatus.PARTIAL_FILLED
        
        return trades
    
    def _execute_trade(self, buy_order: TradingOrder, sell_order: TradingOrder, 
                      quantity: int, price: float) -> Trade:
        """Execute a trade between buy and sell orders"""
        trade = Trade(
            trade_id=str(uuid.uuid4()),
            buy_order_id=buy_order.order_id,
            sell_order_id=sell_order.order_id,
            symbol=self.symbol,
            quantity=quantity,
            price=price,
            timestamp=datetime.now(),
            exchange=buy_order.exchange,
            buyer_client_id=buy_order.client_id,
            seller_client_id=sell_order.client_id
        )
        
        self.recent_trades.append(trade)
        self.last_traded_price = price
        
        logger.info(f"💰 Trade executed: {quantity} shares of {self.symbol} at ₹{price:.2f}")
        
        return trade
    
    def _update_market_data(self):
        """Update market data based on current order book"""
        # Get best bid and ask
        best_bid_price = 0.0
        best_bid_qty = 0
        if self.buy_orders:
            neg_price, order_id = max(self.buy_orders)
            best_bid_price = -neg_price
            order = self.order_book.get(order_id)
            if order:
                best_bid_qty = order.quantity - order.filled_quantity
        
        best_ask_price = float('inf')
        best_ask_qty = 0
        if self.sell_orders:
            price, order_id = min(self.sell_orders)
            best_ask_price = price
            order = self.order_book.get(order_id)
            if order:
                best_ask_qty = order.quantity - order.filled_quantity
        
        if best_ask_price == float('inf'):
            best_ask_price = 0.0
        
        # Update market data
        self.market_data.bid_price = best_bid_price
        self.market_data.ask_price = best_ask_price
        self.market_data.bid_quantity = best_bid_qty
        self.market_data.ask_quantity = best_ask_qty
        
        if self.last_traded_price > 0:
            self.market_data.ltp = self.last_traded_price
            self.market_data.high_price = max(self.market_data.high_price, self.last_traded_price)
            self.market_data.low_price = min(self.market_data.low_price, self.last_traded_price)
        
        self.market_data.timestamp = datetime.now()
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        with self.lock:
            order = self.order_book.get(order_id)
            if not order or order.status != OrderStatus.PENDING:
                return False
            
            order.status = OrderStatus.CANCELLED
            
            # Remove from order books
            self.buy_orders = [(price, oid) for price, oid in self.buy_orders if oid != order_id]
            self.sell_orders = [(price, oid) for price, oid in self.sell_orders if oid != order_id]
            
            heapq.heapify(self.buy_orders)
            heapq.heapify(self.sell_orders)
            
            logger.info(f"❌ Order cancelled: {order_id}")
            return True
    
    def get_order_book_depth(self, levels: int = 5) -> Dict[str, Any]:
        """Get order book depth for market data display"""
        with self.lock:
            # Aggregate buy orders by price
            buy_levels = defaultdict(int)
            for neg_price, order_id in self.buy_orders:
                price = -neg_price
                order = self.order_book.get(order_id)
                if order and order.status == OrderStatus.PENDING:
                    buy_levels[price] += order.quantity - order.filled_quantity
            
            # Aggregate sell orders by price
            sell_levels = defaultdict(int)
            for price, order_id in self.sell_orders:
                order = self.order_book.get(order_id)
                if order and order.status == OrderStatus.PENDING:
                    sell_levels[price] += order.quantity - order.filled_quantity
            
            # Get top levels
            top_buys = sorted(buy_levels.items(), reverse=True)[:levels]
            top_sells = sorted(sell_levels.items())[:levels]
            
            return {
                "symbol": self.symbol,
                "bids": [{"price": price, "quantity": qty} for price, qty in top_buys],
                "asks": [{"price": price, "quantity": qty} for price, qty in top_sells],
                "last_trade_price": self.last_traded_price,
                "timestamp": datetime.now().isoformat()
            }

class DistributedTradingNode:
    """Individual trading node in distributed system"""
    
    def __init__(self, node_id: str, symbols: List[str]):
        self.node_id = node_id
        self.symbols = symbols
        self.matching_engines = {symbol: OrderMatchingEngine(symbol) for symbol in symbols}
        self.client_connections = {}  # client_id -> connection_info
        self.order_routing_table = {}  # symbol -> primary_node_id
        self.peer_nodes = {}  # node_id -> connection_info
        self.is_primary = {}  # symbol -> bool
        
        # Performance metrics
        self.orders_processed = 0
        self.trades_executed = 0
        self.total_latency = 0.0
        
        # Message queues for inter-node communication
        self.outbound_queue = asyncio.Queue()
        self.inbound_queue = asyncio.Queue()
        
        logger.info(f"🏦 Trading node {node_id} initialized for symbols: {symbols}")
    
    async def process_order(self, order: TradingOrder) -> Dict[str, Any]:
        """Process trading order with distributed routing"""
        start_time = time.time()
        
        try:
            # Check if this node handles the symbol
            if order.symbol not in self.symbols:
                # Route to appropriate node
                return await self._route_order_to_node(order)
            
            # Process locally
            matching_engine = self.matching_engines[order.symbol]
            trades = matching_engine.add_order(order)
            
            # Update metrics
            self.orders_processed += 1
            self.trades_executed += len(trades)
            self.total_latency += (time.time() - start_time) * 1000
            
            # Broadcast trades to other nodes
            if trades:
                await self._broadcast_trades(trades)
            
            # Send order updates to client
            await self._send_order_update(order)
            
            return {
                "order_id": order.order_id,
                "status": order.status.value,
                "filled_quantity": order.filled_quantity,
                "trades": [asdict(trade) for trade in trades],
                "processing_time_ms": (time.time() - start_time) * 1000
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing order {order.order_id}: {e}")
            return {
                "order_id": order.order_id,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def _route_order_to_node(self, order: TradingOrder) -> Dict[str, Any]:
        """Route order to the appropriate node for the symbol"""
        primary_node = self.order_routing_table.get(order.symbol)
        
        if not primary_node:
            logger.error(f"❌ No primary node found for symbol {order.symbol}")
            return {"error": f"No handler for symbol {order.symbol}"}
        
        # In a real system, this would be a network call
        logger.info(f"🔄 Routing order {order.order_id} for {order.symbol} to node {primary_node}")
        
        # Simulate routing delay
        await asyncio.sleep(0.001)  # 1ms network latency
        
        return {
            "order_id": order.order_id,
            "status": "ROUTED",
            "routed_to": primary_node
        }
    
    async def _broadcast_trades(self, trades: List[Trade]):
        """Broadcast executed trades to all peer nodes"""
        for trade in trades:
            message = {
                "type": "TRADE_EXECUTED",
                "trade": asdict(trade),
                "source_node": self.node_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to outbound queue
            await self.outbound_queue.put(message)
    
    async def _send_order_update(self, order: TradingOrder):
        """Send order status update to client"""
        update = {
            "type": "ORDER_UPDATE",
            "order_id": order.order_id,
            "client_id": order.client_id,
            "status": order.status.value,
            "filled_quantity": order.filled_quantity,
            "average_price": order.average_price,
            "timestamp": datetime.now().isoformat()
        }
        
        # In real system, this would send to client via WebSocket/TCP
        logger.debug(f"📡 Order update sent to client {order.client_id}: {order.order_id} -> {order.status.value}")
    
    def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get current market data for symbol"""
        if symbol in self.matching_engines:
            return self.matching_engines[symbol].market_data
        return None
    
    def get_order_book(self, symbol: str, depth: int = 5) -> Optional[Dict[str, Any]]:
        """Get order book depth for symbol"""
        if symbol in self.matching_engines:
            return self.matching_engines[symbol].get_order_book_depth(depth)
        return None
    
    def get_node_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this node"""
        avg_latency = self.total_latency / max(self.orders_processed, 1)
        
        return {
            "node_id": self.node_id,
            "symbols_handled": self.symbols,
            "orders_processed": self.orders_processed,
            "trades_executed": self.trades_executed,
            "average_latency_ms": avg_latency,
            "orders_per_second": self.orders_processed / 60,  # Approximate
            "status": "ACTIVE"
        }

class ZerodhaDistributedTradingSystem:
    """Complete distributed trading system"""
    
    def __init__(self):
        # Indian stock symbols
        self.nse_symbols = [
            "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "HINDUNILVR",
            "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK", "INFY",
            "LT", "HCLTECH", "ASIANPAINT", "MARUTI", "AXISBANK"
        ]
        
        # Create distributed nodes
        self.nodes = {}
        self.setup_distributed_nodes()
        
        # System metrics
        self.system_start_time = datetime.now()
        self.total_orders = 0
        self.total_trades = 0
        self.total_volume = 0.0
        self.total_value = 0.0
        
        logger.info(f"🚀 Zerodha distributed trading system initialized with {len(self.nodes)} nodes")
    
    def setup_distributed_nodes(self):
        """Setup distributed trading nodes for load balancing"""
        # Distribute symbols across nodes for load balancing
        symbols_per_node = 5
        
        for i in range(0, len(self.nse_symbols), symbols_per_node):
            node_id = f"trading_node_{i//symbols_per_node + 1}"
            node_symbols = self.nse_symbols[i:i + symbols_per_node]
            
            node = DistributedTradingNode(node_id, node_symbols)
            self.nodes[node_id] = node
            
            # Set up routing table
            for symbol in node_symbols:
                for other_node in self.nodes.values():
                    other_node.order_routing_table[symbol] = node_id
                    other_node.is_primary[symbol] = (other_node.node_id == node_id)
    
    def route_order(self, order: TradingOrder) -> str:
        """Route order to appropriate node based on symbol"""
        # Simple hash-based routing
        symbol_hash = hash(order.symbol) % len(self.nodes)
        node_ids = list(self.nodes.keys())
        selected_node = node_ids[symbol_hash]
        
        # Check if node handles this symbol
        node = self.nodes[selected_node]
        if order.symbol in node.symbols:
            return selected_node
        
        # Fallback: find node that handles this symbol
        for node_id, node in self.nodes.items():
            if order.symbol in node.symbols:
                return node_id
        
        return list(self.nodes.keys())[0]  # Default fallback
    
    async def submit_order(self, order: TradingOrder) -> Dict[str, Any]:
        """Submit order to distributed trading system"""
        # Route to appropriate node
        target_node_id = self.route_order(order)
        target_node = self.nodes[target_node_id]
        
        # Process order
        result = await target_node.process_order(order)
        
        # Update system metrics
        self.total_orders += 1
        if 'trades' in result:
            trades = result['trades']
            self.total_trades += len(trades)
            for trade in trades:
                self.total_volume += trade['quantity']
                self.total_value += trade['quantity'] * trade['price']
        
        return result
    
    def get_market_data_all(self) -> Dict[str, MarketData]:
        """Get market data for all symbols"""
        market_data = {}
        
        for node in self.nodes.values():
            for symbol in node.symbols:
                data = node.get_market_data(symbol)
                if data:
                    market_data[symbol] = data
        
        return market_data
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and metrics"""
        uptime = datetime.now() - self.system_start_time
        
        # Aggregate node metrics
        total_orders_processed = sum(node.orders_processed for node in self.nodes.values())
        total_trades_executed = sum(node.trades_executed for node in self.nodes.values())
        
        # Calculate average latency across all nodes
        total_latency = sum(node.total_latency for node in self.nodes.values())
        avg_latency = total_latency / max(total_orders_processed, 1)
        
        node_statuses = {node_id: node.get_node_metrics() for node_id, node in self.nodes.items()}
        
        return {
            "system_uptime": str(uptime),
            "total_nodes": len(self.nodes),
            "symbols_covered": len(self.nse_symbols),
            "orders_processed": total_orders_processed,
            "trades_executed": total_trades_executed,
            "total_volume": self.total_volume,
            "total_value_inr": self.total_value,
            "average_latency_ms": avg_latency,
            "orders_per_second": total_orders_processed / max(uptime.total_seconds(), 1),
            "nodes": node_statuses,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_system_dashboard(self):
        """Print comprehensive system dashboard"""
        status = self.get_system_status()
        
        print(f"\n{'='*80}")
        print(f"📈 ZERODHA DISTRIBUTED TRADING SYSTEM DASHBOARD 📈")
        print(f"{'='*80}")
        
        print(f"🏦 System Overview:")
        print(f"   Trading Nodes: {status['total_nodes']}")
        print(f"   Symbols Covered: {status['symbols_covered']}")
        print(f"   System Uptime: {status['system_uptime']}")
        
        print(f"\n📊 Trading Metrics:")
        print(f"   Orders Processed: {status['orders_processed']:,}")
        print(f"   Trades Executed: {status['trades_executed']:,}")
        print(f"   Total Volume: {status['total_volume']:,.0f} shares")
        print(f"   Total Value: ₹{status['total_value_inr']:,.2f}")
        
        print(f"\n⚡ Performance Metrics:")
        print(f"   Average Latency: {status['average_latency_ms']:.2f} ms")
        print(f"   Orders/Second: {status['orders_per_second']:.1f}")
        
        print(f"\n🖥️ Node Status:")
        for node_id, node_status in status['nodes'].items():
            print(f"   {node_id}:")
            print(f"     Symbols: {len(node_status['symbols_handled'])}")
            print(f"     Orders: {node_status['orders_processed']:,}")
            print(f"     Trades: {node_status['trades_executed']:,}")
            print(f"     Latency: {node_status['average_latency_ms']:.2f} ms")
        
        print(f"\n🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")

def generate_random_order() -> TradingOrder:
    """Generate realistic trading order for simulation"""
    symbols = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "HINDUNILVR"]
    sides = [OrderSide.BUY, OrderSide.SELL]
    order_types = [OrderType.MARKET, OrderType.LIMIT]
    
    symbol = random.choice(symbols)
    side = random.choice(sides)
    order_type = random.choice(order_types)
    
    # Realistic Indian stock prices and quantities
    base_price = {
        "RELIANCE": 2500, "TCS": 3800, "HDFCBANK": 1650,
        "ICICIBANK": 950, "HINDUNILVR": 2400
    }.get(symbol, 1000)
    
    price = base_price + random.uniform(-50, 50)
    quantity = random.choice([1, 5, 10, 25, 50, 100]) * random.randint(1, 10)
    
    return TradingOrder(
        order_id=str(uuid.uuid4()),
        client_id=f"client_{random.randint(1000, 9999)}",
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=round(price, 2) if order_type == OrderType.LIMIT else 0.0,
        exchange="NSE",
        segment="EQ",
        product_type=random.choice(["CNC", "MIS"]),
        validity="DAY"
    )

async def simulate_trading_session(system: ZerodhaDistributedTradingSystem, duration_minutes: int = 5):
    """Simulate realistic trading session"""
    logger.info(f"📈 Starting Zerodha trading simulation for {duration_minutes} minutes")
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    order_count = 0
    
    try:
        while time.time() < end_time:
            # Generate orders with realistic patterns
            # Peak trading hours have higher order rates
            current_hour = datetime.now().hour
            
            if 9 <= current_hour <= 11 or 14 <= current_hour <= 15:
                # Peak hours - higher order rate
                orders_per_second = random.randint(5, 15)
            else:
                # Normal hours
                orders_per_second = random.randint(2, 8)
            
            # Generate and submit orders
            for _ in range(orders_per_second):
                order = generate_random_order()
                result = await system.submit_order(order)
                order_count += 1
                
                # Log interesting events
                if 'trades' in result and result['trades']:
                    trades = result['trades']
                    for trade in trades:
                        logger.info(f"💰 Trade: {trade['quantity']} {trade['symbol']} @ ₹{trade['price']:.2f}")
            
            # Print dashboard every 30 seconds
            if order_count % 100 == 0:
                system.print_system_dashboard()
            
            # Small delay between batches
            await asyncio.sleep(1.0)
    
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")
    
    logger.info(f"🏁 Trading simulation completed! Processed {order_count} orders")
    
    # Final dashboard
    system.print_system_dashboard()

async def main():
    """Main demo function"""
    print("🇮🇳 Zerodha Distributed Trading System")
    print("📈 High-performance distributed order matching और execution engine")
    print("🏦 Real-time trading across NSE symbols with sub-millisecond latency...\n")
    
    # Initialize distributed trading system
    system = ZerodhaDistributedTradingSystem()
    
    try:
        # Show initial system status
        system.print_system_dashboard()
        
        # Run trading simulation
        await simulate_trading_session(system, duration_minutes=3)
        
        print(f"\n🎯 SIMULATION COMPLETED!")
        print(f"💡 Production system capabilities:")
        print(f"   - Handle 10M+ orders per day")
        print(f"   - Sub-millisecond order execution")
        print(f"   - 99.99% uptime during market hours")
        print(f"   - Real-time market data distribution")
        print(f"   - Distributed load balancing across nodes")
        print(f"   - Fault-tolerant order matching")
        
    except Exception as e:
        logger.error(f"❌ Error in simulation: {e}")

if __name__ == "__main__":
    # Run the distributed trading system demo
    asyncio.run(main())
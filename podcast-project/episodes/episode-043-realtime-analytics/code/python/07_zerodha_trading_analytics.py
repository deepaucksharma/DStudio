#!/usr/bin/env python3
"""
Zerodha Real-time Trading Analytics
Episode 43: Real-time Analytics at Scale

यह example Zerodha जैसे trading platform का real-time analytics दिखाता है
Market hours के दौरान millions of trade orders और price updates handle करता है।

Real Production Stats:
- Zerodha: 6+ million active traders
- Peak trades/minute: 100,000+ (during market volatility)
- Market data updates: 1000+ per second per script
- P&L calculations: Real-time for 20+ million positions
"""

import asyncio
import json
import time
import random
import math
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
import numpy as np
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

@dataclass
class StockPrice:
    """Stock price data structure"""
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    change_percent: float
    bid: float
    ask: float

@dataclass
class TradeOrder:
    """Trade order data structure"""
    order_id: str
    user_id: str
    symbol: str
    order_type: OrderType
    quantity: int
    price: float
    timestamp: datetime
    status: OrderStatus
    exchange: str  # NSE, BSE
    order_category: str  # EQUITY, DERIVATIVE

@dataclass
class UserPosition:
    """User position data"""
    user_id: str
    symbol: str
    quantity: int  # Positive for long, negative for short
    avg_price: float
    current_price: float
    pnl: float
    pnl_percent: float

class ZerodhaRealTimeAnalytics:
    """
    Real-time trading analytics for Zerodha-like platform
    Handles market data, order flow, and P&L calculations
    """
    
    def __init__(self):
        # Market data storage
        self.stock_prices = {}  # symbol -> StockPrice
        self.price_history = defaultdict(lambda: deque(maxlen=1000))  # symbol -> price_deque
        
        # Order management
        self.pending_orders = {}  # order_id -> TradeOrder
        self.executed_orders = []
        self.order_book = defaultdict(lambda: {'buy': [], 'sell': []})  # symbol -> orders
        
        # User positions
        self.user_positions = defaultdict(dict)  # user_id -> {symbol: UserPosition}
        self.user_pnl = defaultdict(float)  # user_id -> total_pnl
        
        # Real-time metrics
        self.metrics = {
            "total_orders_today": 0,
            "executed_orders_today": 0,
            "total_volume_traded": 0,
            "total_turnover": 0.0,
            "active_users": set(),
            "top_traded_stocks": defaultdict(int),
            "market_mood": "NEUTRAL",  # BULLISH, BEARISH, NEUTRAL
            "last_updated": datetime.now()
        }
        
        # Popular Indian stocks
        self.indian_stocks = {
            "RELIANCE": {"price": 2450.0, "volume": 1000000},
            "TCS": {"price": 3890.0, "volume": 800000},
            "HDFCBANK": {"price": 1678.0, "volume": 1200000},
            "ICICIBANK": {"price": 945.0, "volume": 900000},
            "INFY": {"price": 1456.0, "volume": 750000},
            "ITC": {"price": 462.0, "volume": 2000000},
            "SBIN": {"price": 598.0, "volume": 3000000},
            "BHARTIARTL": {"price": 1089.0, "volume": 1500000},
            "KOTAKBANK": {"price": 1845.0, "volume": 600000},
            "LT": {"price": 3234.0, "volume": 400000},
            "ASIANPAINT": {"price": 3456.0, "volume": 300000},
            "MARUTI": {"price": 10234.0, "volume": 200000},
            "SUNPHARMA": {"price": 1123.0, "volume": 800000},
            "NTPC": {"price": 234.0, "volume": 5000000},
            "POWERGRID": {"price": 267.0, "volume": 2500000}
        }
        
        # Initialize stock prices
        for symbol, data in self.indian_stocks.items():
            self.stock_prices[symbol] = StockPrice(
                symbol=symbol,
                price=data["price"],
                volume=data["volume"],
                timestamp=datetime.now(),
                change_percent=0.0,
                bid=data["price"] - 0.5,
                ask=data["price"] + 0.5
            )
    
    def generate_market_data_update(self, symbol: str) -> StockPrice:
        """Generate realistic market data update"""
        current_price = self.stock_prices[symbol]
        
        # Simulate price movement with some volatility
        # Indian markets typically move ±0.1% to ±2% per minute
        volatility = random.uniform(0.001, 0.02)  # 0.1% to 2%
        direction = random.choice([-1, 1])
        
        # Add some market trend bias
        market_bias = self.get_market_trend_bias()
        direction_probability = 0.6 if market_bias > 0 else 0.4
        if random.random() < direction_probability:
            direction = 1 if market_bias > 0 else -1
        
        price_change = current_price.price * volatility * direction
        new_price = max(current_price.price + price_change, 1.0)  # Price can't be negative
        
        # Calculate change percentage from day's open
        day_open_price = self.indian_stocks[symbol]["price"]
        change_percent = ((new_price - day_open_price) / day_open_price) * 100
        
        # Generate volume (proportional to price movement for realism)
        base_volume = self.indian_stocks[symbol]["volume"]
        volume_multiplier = 1 + abs(volatility * 10)  # Higher volatility = higher volume
        volume = int(base_volume * volume_multiplier * random.uniform(0.8, 1.2))
        
        return StockPrice(
            symbol=symbol,
            price=round(new_price, 2),
            volume=volume,
            timestamp=datetime.now(),
            change_percent=round(change_percent, 2),
            bid=round(new_price - 0.5, 2),
            ask=round(new_price + 0.5, 2)
        )
    
    def get_market_trend_bias(self) -> float:
        """
        Calculate market trend bias based on Nifty movement
        Real में यह actual market indices से आता है
        """
        # Simulate market trend (bullish morning, neutral afternoon, volatile evening)
        current_hour = datetime.now().hour
        
        if 9 <= current_hour <= 11:  # Morning session - typically bullish
            return random.uniform(0.1, 0.8)
        elif 11 <= current_hour <= 14:  # Afternoon - neutral
            return random.uniform(-0.3, 0.3)
        else:  # Evening - more volatile
            return random.uniform(-1.0, 1.0)
    
    async def update_market_data(self):
        """Update market data for all stocks"""
        for symbol in self.indian_stocks.keys():
            new_price_data = self.generate_market_data_update(symbol)
            self.stock_prices[symbol] = new_price_data
            self.price_history[symbol].append(new_price_data.price)
        
        # Update market mood based on overall movement
        positive_moves = sum(1 for p in self.stock_prices.values() if p.change_percent > 0)
        total_stocks = len(self.stock_prices)
        
        if positive_moves > (total_stocks * 0.7):
            self.metrics["market_mood"] = "BULLISH"
        elif positive_moves < (total_stocks * 0.3):
            self.metrics["market_mood"] = "BEARISH"
        else:
            self.metrics["market_mood"] = "NEUTRAL"
    
    def generate_trade_order(self) -> TradeOrder:
        """Generate realistic trade order"""
        symbol = random.choice(list(self.indian_stocks.keys()))
        current_price = self.stock_prices[symbol].price
        
        # User trading behavior (retail vs institutional)
        user_type = random.choices(["retail", "institutional"], weights=[85, 15])[0]
        
        if user_type == "retail":
            user_id = f"retail_{random.randint(1, 100000)}"
            quantity = random.choice([1, 5, 10, 25, 50, 100])  # Typical retail quantities
            # Retail traders often place market orders or slightly off-market limit orders
            price_variation = random.uniform(-0.5, 0.5)  # ±0.5% from current price
        else:
            user_id = f"inst_{random.randint(1, 1000)}"
            quantity = random.choice([500, 1000, 2500, 5000, 10000])  # Institutional quantities
            # Institutional traders use more sophisticated pricing
            price_variation = random.uniform(-0.2, 0.2)  # ±0.2% from current price
        
        order_price = current_price * (1 + price_variation / 100)
        
        return TradeOrder(
            order_id=f"ORD_{int(time.time())}_{random.randint(1000, 9999)}",
            user_id=user_id,
            symbol=symbol,
            order_type=random.choice([OrderType.BUY, OrderType.SELL]),
            quantity=quantity,
            price=round(order_price, 2),
            timestamp=datetime.now(),
            status=OrderStatus.PENDING,
            exchange=random.choice(["NSE", "BSE"]),
            order_category="EQUITY"
        )
    
    async def process_trade_order(self, order: TradeOrder):
        """Process trade order and attempt execution"""
        self.pending_orders[order.order_id] = order
        self.metrics["total_orders_today"] += 1
        self.metrics["active_users"].add(order.user_id)
        
        # Simple order matching logic
        current_price = self.stock_prices[order.symbol].price
        
        # Execute if price is within acceptable range (simplified matching engine)
        price_tolerance = 0.01  # 1% tolerance
        
        if order.order_type == OrderType.BUY and order.price >= (current_price * (1 - price_tolerance)):
            await self.execute_order(order, current_price)
        elif order.order_type == OrderType.SELL and order.price <= (current_price * (1 + price_tolerance)):
            await self.execute_order(order, current_price)
        else:
            # Keep in order book for later matching
            self.order_book[order.symbol][order.order_type.value.lower()].append(order)
    
    async def execute_order(self, order: TradeOrder, execution_price: float):
        """Execute trade order and update positions"""
        order.status = OrderStatus.EXECUTED
        order.price = execution_price  # Update to actual execution price
        
        self.executed_orders.append(order)
        self.metrics["executed_orders_today"] += 1
        self.metrics["total_volume_traded"] += order.quantity
        self.metrics["total_turnover"] += (order.quantity * execution_price)
        self.metrics["top_traded_stocks"][order.symbol] += order.quantity
        
        # Update user position
        await self.update_user_position(order, execution_price)
        
        # Remove from pending orders
        if order.order_id in self.pending_orders:
            del self.pending_orders[order.order_id]
        
        logger.info(f"✅ Executed: {order.user_id} {order.order_type.value} {order.quantity} {order.symbol} @ ₹{execution_price}")
    
    async def update_user_position(self, order: TradeOrder, execution_price: float):
        """Update user position and calculate P&L"""
        user_id = order.user_id
        symbol = order.symbol
        
        if symbol not in self.user_positions[user_id]:
            # New position
            quantity = order.quantity if order.order_type == OrderType.BUY else -order.quantity
            self.user_positions[user_id][symbol] = UserPosition(
                user_id=user_id,
                symbol=symbol,
                quantity=quantity,
                avg_price=execution_price,
                current_price=execution_price,
                pnl=0.0,
                pnl_percent=0.0
            )
        else:
            # Update existing position
            position = self.user_positions[user_id][symbol]
            
            if order.order_type == OrderType.BUY:
                # Adding to position
                total_value = (position.quantity * position.avg_price) + (order.quantity * execution_price)
                total_quantity = position.quantity + order.quantity
                position.avg_price = total_value / total_quantity if total_quantity != 0 else execution_price
                position.quantity = total_quantity
            else:
                # Reducing position
                position.quantity -= order.quantity
                if position.quantity == 0:
                    # Position closed - realize P&L
                    realized_pnl = (execution_price - position.avg_price) * order.quantity
                    self.user_pnl[user_id] += realized_pnl
                    del self.user_positions[user_id][symbol]
                    return
        
        # Update current price and P&L
        await self.calculate_position_pnl(user_id, symbol)
    
    async def calculate_position_pnl(self, user_id: str, symbol: str):
        """Calculate unrealized P&L for a position"""
        if symbol in self.user_positions[user_id]:
            position = self.user_positions[user_id][symbol]
            current_price = self.stock_prices[symbol].price
            
            position.current_price = current_price
            position.pnl = (current_price - position.avg_price) * position.quantity
            position.pnl_percent = ((current_price - position.avg_price) / position.avg_price) * 100
    
    async def calculate_all_pnl(self):
        """Calculate P&L for all user positions"""
        for user_id in self.user_positions:
            for symbol in self.user_positions[user_id]:
                await self.calculate_position_pnl(user_id, symbol)
    
    def get_top_gainers_losers(self) -> Dict[str, List[Tuple[str, float]]]:
        """Get top gainers and losers"""
        sorted_by_change = sorted(
            self.stock_prices.items(),
            key=lambda x: x[1].change_percent,
            reverse=True
        )
        
        gainers = [(symbol, data.change_percent) for symbol, data in sorted_by_change[:5]]
        losers = [(symbol, data.change_percent) for symbol, data in sorted_by_change[-5:]]
        
        return {"gainers": gainers, "losers": losers}
    
    def print_market_dashboard(self):
        """Print real-time market dashboard"""
        print(f"\n{'='*70}")
        print(f"📈 ZERODHA REAL-TIME TRADING DASHBOARD 📉")
        print(f"{'='*70}")
        print(f"Market Mood: {self.metrics['market_mood']} {'🟢' if self.metrics['market_mood'] == 'BULLISH' else '🔴' if self.metrics['market_mood'] == 'BEARISH' else '🟡'}")
        print(f"Total Orders Today: {self.metrics['total_orders_today']:,}")
        print(f"Executed Orders: {self.metrics['executed_orders_today']:,}")
        print(f"Execution Rate: {(self.metrics['executed_orders_today']/max(1, self.metrics['total_orders_today'])*100):.1f}%")
        print(f"Total Volume: {self.metrics['total_volume_traded']:,}")
        print(f"Total Turnover: ₹{self.metrics['total_turnover']/10000000:.2f} Cr")
        print(f"Active Users: {len(self.metrics['active_users']):,}")
        print(f"Pending Orders: {len(self.pending_orders):,}")
        
        # Top traded stocks
        if self.metrics["top_traded_stocks"]:
            print(f"\n📊 Top Traded Stocks:")
            sorted_stocks = sorted(
                self.metrics["top_traded_stocks"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for symbol, volume in sorted_stocks:
                price_data = self.stock_prices[symbol]
                print(f"  {symbol}: {volume:,} qty @ ₹{price_data.price} ({price_data.change_percent:+.2f}%)")
        
        # Gainers and losers
        gainers_losers = self.get_top_gainers_losers()
        
        print(f"\n🚀 Top Gainers:")
        for symbol, change in gainers_losers["gainers"]:
            print(f"  {symbol}: {change:+.2f}%")
        
        print(f"\n📉 Top Losers:")
        for symbol, change in gainers_losers["losers"]:
            print(f"  {symbol}: {change:+.2f}%")
        
        print(f"\nLast Updated: {datetime.now().strftime('%H:%M:%S')}")
    
    def print_user_portfolio(self, user_id: str):
        """Print user portfolio with P&L"""
        if user_id not in self.user_positions or not self.user_positions[user_id]:
            print(f"\nNo positions found for user {user_id}")
            return
        
        print(f"\n{'='*50}")
        print(f"👤 PORTFOLIO: {user_id}")
        print(f"{'='*50}")
        
        total_pnl = 0
        total_investment = 0
        
        for symbol, position in self.user_positions[user_id].items():
            investment = position.quantity * position.avg_price
            current_value = position.quantity * position.current_price
            total_pnl += position.pnl
            total_investment += abs(investment)
            
            status = "LONG" if position.quantity > 0 else "SHORT"
            pnl_color = "🟢" if position.pnl >= 0 else "🔴"
            
            print(f"{symbol} ({status}): {abs(position.quantity)} @ ₹{position.avg_price:.2f}")
            print(f"  Current: ₹{position.current_price:.2f} | P&L: {pnl_color} ₹{position.pnl:.2f} ({position.pnl_percent:+.2f}%)")
            print(f"  Investment: ₹{abs(investment):,.2f} | Current Value: ₹{abs(current_value):,.2f}")
            print()
        
        overall_return = (total_pnl / max(1, total_investment)) * 100
        print(f"💰 Total P&L: {'🟢' if total_pnl >= 0 else '🔴'} ₹{total_pnl:.2f}")
        print(f"📊 Overall Return: {overall_return:+.2f}%")
    
    async def simulate_trading_day(self, duration_minutes: int = 10):
        """
        Simulate a trading day with realistic patterns
        Indian markets: 9:15 AM - 3:30 PM
        """
        logger.info(f"📈 Starting trading day simulation for {duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Trading session patterns
        patterns = [
            (0.0, 0.2, 500, "Opening Bell - High Activity"),      # First 20% - opening rush
            (0.2, 0.4, 200, "Morning Session - Steady Trading"),   # Next 20% - normal trading
            (0.4, 0.6, 300, "Midday Session - Volume Pickup"),    # Middle - slight increase
            (0.6, 0.8, 150, "Afternoon Session - Lower Activity"), # Afternoon lull
            (0.8, 1.0, 600, "Closing Bell - Final Rush")          # Last 20% - closing rush
        ]
        
        current_pattern_index = 0
        
        try:
            while time.time() < end_time:
                current_progress = (time.time() - start_time) / (duration_minutes * 60)
                
                # Update current trading pattern
                if current_pattern_index < len(patterns):
                    pattern_start, pattern_end, orders_per_min, pattern_name = patterns[current_pattern_index]
                    
                    if current_progress >= pattern_end and current_pattern_index < len(patterns) - 1:
                        current_pattern_index += 1
                        logger.info(f"📊 Trading Pattern: {pattern_name}")
                        orders_per_min = patterns[current_pattern_index][2]
                    elif pattern_start <= current_progress <= pattern_end:
                        orders_per_min = patterns[current_pattern_index][2]
                
                # Update market data every second
                await self.update_market_data()
                
                # Generate trade orders based on current pattern
                orders_this_cycle = random.poisson(orders_per_min // 60)  # Convert per minute to per second
                
                for _ in range(orders_this_cycle):
                    order = self.generate_trade_order()
                    await self.process_trade_order(order)
                
                # Calculate all P&L
                await self.calculate_all_pnl()
                
                # Print dashboard every 30 seconds
                if int(time.time()) % 30 == 0:
                    self.print_market_dashboard()
                    
                    # Show sample user portfolio
                    if self.user_positions:
                        sample_user = random.choice(list(self.user_positions.keys()))
                        self.print_user_portfolio(sample_user)
                
                await asyncio.sleep(1)  # 1 second processing cycle
                
        except KeyboardInterrupt:
            logger.info("Trading simulation stopped by user")
        
        logger.info("📈 Trading day simulation completed!")
        self.print_market_dashboard()

async def main():
    """Main demo function"""
    print("🚀 Starting Zerodha Real-time Trading Analytics Demo")
    
    analytics = ZerodhaRealTimeAnalytics()
    
    try:
        # Run trading day simulation
        await analytics.simulate_trading_day(duration_minutes=3)
        
        # Final summary
        print(f"\n🏁 TRADING DAY SUMMARY")
        print(f"Total Orders: {analytics.metrics['total_orders_today']:,}")
        print(f"Executed Orders: {analytics.metrics['executed_orders_today']:,}")
        print(f"Total Turnover: ₹{analytics.metrics['total_turnover']/10000000:.2f} Crores")
        print(f"Unique Traders: {len(analytics.metrics['active_users']):,}")
        
    except Exception as e:
        logger.error(f"Error in trading simulation: {e}")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
#!/usr/bin/env python3
"""
Event Sourcing Implementation with Event Store
उदाहरण: Zerodha portfolio events को event sourcing के साथ track करना

Setup:
pip install sqlalchemy sqlite3 asyncio

Indian Context: Zerodha app मein हर trade, portfolio change, 
fund addition को event के रूप में store करना:
- Trade executed events
- Portfolio balance updates
- Fund addition/withdrawal
- Stock purchase/sale events
- P&L calculation events

Event Sourcing benefits:
- Complete audit trail (regulatory compliance)
- Point-in-time portfolio reconstruction
- Replay capabilities for testing
- Immutable event history
"""

import asyncio
import json
import sqlite3
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Portfolio event types"""
    FUND_ADDED = "fund.added"
    FUND_WITHDRAWN = "fund.withdrawn"
    STOCK_PURCHASED = "stock.purchased"
    STOCK_SOLD = "stock.sold"
    DIVIDEND_RECEIVED = "dividend.received"
    PORTFOLIO_CREATED = "portfolio.created"

@dataclass
class DomainEvent:
    """Base domain event structure"""
    event_id: str
    event_type: str
    aggregate_id: str  # Portfolio ID
    event_data: Dict[str, Any]
    event_version: int
    timestamp: str
    user_id: str
    correlation_id: str = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())

class EventStore:
    """
    Event Store implementation using SQLite
    Production mein PostgreSQL/MongoDB use करेंगे
    """
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Database tables create karna"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Events table - immutable event storage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                event_type TEXT NOT NULL,
                aggregate_id TEXT NOT NULL,
                event_data TEXT NOT NULL,
                event_version INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                correlation_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Snapshots table - performance optimization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aggregate_id TEXT NOT NULL,
                snapshot_data TEXT NOT NULL,
                version INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                UNIQUE(aggregate_id, version)
            )
        ''')
        
        # Indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_aggregate_id ON events(aggregate_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Event store database initialized")
    
    async def append_event(self, event: DomainEvent) -> bool:
        """
        Event को store में append karna
        Immutable - एक बार store होने के बाद change नहीं होता
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (
                    event_id, event_type, aggregate_id, event_data,
                    event_version, timestamp, user_id, correlation_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.event_type,
                event.aggregate_id,
                json.dumps(event.event_data),
                event.event_version,
                event.timestamp,
                event.user_id,
                event.correlation_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📝 Event stored: {event.event_type} for aggregate {event.aggregate_id}")
            return True
            
        except sqlite3.IntegrityError as e:
            logger.error(f"❌ Event already exists: {event.event_id}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to store event: {e}")
            return False
    
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[DomainEvent]:
        """Aggregate ke liye events retrieve karna"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT event_id, event_type, aggregate_id, event_data,
                   event_version, timestamp, user_id, correlation_id
            FROM events 
            WHERE aggregate_id = ? AND event_version > ?
            ORDER BY event_version ASC
        ''', (aggregate_id, from_version))
        
        events = []
        for row in cursor.fetchall():
            event = DomainEvent(
                event_id=row[0],
                event_type=row[1],
                aggregate_id=row[2],
                event_data=json.loads(row[3]),
                event_version=row[4],
                timestamp=row[5],
                user_id=row[6],
                correlation_id=row[7]
            )
            events.append(event)
        
        conn.close()
        return events
    
    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[DomainEvent]:
        """Event type के basis par events retrieve karna"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT event_id, event_type, aggregate_id, event_data,
                   event_version, timestamp, user_id, correlation_id
            FROM events 
            WHERE event_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (event_type, limit))
        
        events = []
        for row in cursor.fetchall():
            event = DomainEvent(
                event_id=row[0],
                event_type=row[1],
                aggregate_id=row[2],
                event_data=json.loads(row[3]),
                event_version=row[4],
                timestamp=row[5],
                user_id=row[6],
                correlation_id=row[7]
            )
            events.append(event)
        
        conn.close()
        return events

@dataclass
class Portfolio:
    """
    Portfolio aggregate - event sourcing pattern
    State को events से reconstruct करते हैं
    """
    portfolio_id: str
    user_id: str
    balance: float = 0.0
    stocks: Dict[str, Dict] = None
    total_invested: float = 0.0
    current_value: float = 0.0
    version: int = 0
    
    def __post_init__(self):
        if self.stocks is None:
            self.stocks = {}
    
    @property
    def profit_loss(self) -> float:
        """Current P&L calculation"""
        return self.current_value - self.total_invested
    
    @property
    def profit_loss_percentage(self) -> float:
        """P&L percentage"""
        if self.total_invested == 0:
            return 0.0
        return (self.profit_loss / self.total_invested) * 100

class PortfolioEventHandler:
    """Portfolio events को handle करने के lिए"""
    
    @staticmethod
    def apply_event(portfolio: Portfolio, event: DomainEvent) -> Portfolio:
        """
        Event को portfolio state पर apply करना
        Mumbai local station की तरह - हर station पर state change
        """
        event_type = event.event_type
        data = event.event_data
        
        if event_type == EventType.PORTFOLIO_CREATED.value:
            portfolio.balance = data.get('initial_balance', 0.0)
            
        elif event_type == EventType.FUND_ADDED.value:
            portfolio.balance += data['amount']
            
        elif event_type == EventType.FUND_WITHDRAWN.value:
            portfolio.balance -= data['amount']
            
        elif event_type == EventType.STOCK_PURCHASED.value:
            symbol = data['symbol']
            quantity = data['quantity']
            price = data['price']
            total_cost = quantity * price
            
            # Balance से cost deduct karna
            portfolio.balance -= total_cost
            portfolio.total_invested += total_cost
            
            # Stock position update karna
            if symbol in portfolio.stocks:
                existing = portfolio.stocks[symbol]
                total_qty = existing['quantity'] + quantity
                avg_price = ((existing['quantity'] * existing['avg_price']) + 
                            (quantity * price)) / total_qty
                
                portfolio.stocks[symbol] = {
                    'quantity': total_qty,
                    'avg_price': avg_price,
                    'current_price': price  # Latest price
                }
            else:
                portfolio.stocks[symbol] = {
                    'quantity': quantity,
                    'avg_price': price,
                    'current_price': price
                }
            
        elif event_type == EventType.STOCK_SOLD.value:
            symbol = data['symbol']
            quantity = data['quantity']
            price = data['price']
            total_value = quantity * price
            
            # Balance mein sale proceeds add karna
            portfolio.balance += total_value
            
            # Stock position update karna
            if symbol in portfolio.stocks:
                portfolio.stocks[symbol]['quantity'] -= quantity
                if portfolio.stocks[symbol]['quantity'] <= 0:
                    del portfolio.stocks[symbol]
                    
        elif event_type == EventType.DIVIDEND_RECEIVED.value:
            dividend_amount = data['amount']
            portfolio.balance += dividend_amount
        
        # Portfolio version increment karna
        portfolio.version = event.event_version
        
        # Current value calculate karna
        portfolio.current_value = portfolio.balance
        for stock_data in portfolio.stocks.values():
            portfolio.current_value += (stock_data['quantity'] * 
                                      stock_data['current_price'])
        
        return portfolio

class PortfolioService:
    """Portfolio service - commands को events में convert karna"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.event_handler = PortfolioEventHandler()
    
    async def create_portfolio(self, user_id: str, initial_balance: float = 0.0) -> str:
        """नया portfolio create karna"""
        portfolio_id = f"PORT_{uuid.uuid4().hex[:8].upper()}"
        
        event = DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PORTFOLIO_CREATED.value,
            aggregate_id=portfolio_id,
            event_data={
                'initial_balance': initial_balance,
                'created_by': user_id
            },
            event_version=1,
            timestamp=datetime.now().isoformat(),
            user_id=user_id
        )
        
        await self.event_store.append_event(event)
        
        logger.info(f"📊 Portfolio created: {portfolio_id} for user {user_id}")
        return portfolio_id
    
    async def add_funds(self, portfolio_id: str, user_id: str, amount: float) -> bool:
        """Portfolio mein funds add karna"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Current version get karna
        events = await self.event_store.get_events(portfolio_id)
        current_version = len(events)
        
        event = DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.FUND_ADDED.value,
            aggregate_id=portfolio_id,
            event_data={
                'amount': amount,
                'transaction_ref': f"FUND_{uuid.uuid4().hex[:8]}"
            },
            event_version=current_version + 1,
            timestamp=datetime.now().isoformat(),
            user_id=user_id
        )
        
        success = await self.event_store.append_event(event)
        if success:
            logger.info(f"💰 Funds added: ₹{amount} to portfolio {portfolio_id}")
        
        return success
    
    async def buy_stock(self, portfolio_id: str, user_id: str, symbol: str, 
                       quantity: int, price: float) -> bool:
        """Stock purchase karna"""
        total_cost = quantity * price
        
        # Current portfolio state check karna
        portfolio = await self.reconstruct_portfolio(portfolio_id)
        if portfolio.balance < total_cost:
            logger.error(f"❌ Insufficient balance: ₹{portfolio.balance} < ₹{total_cost}")
            return False
        
        event = DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.STOCK_PURCHASED.value,
            aggregate_id=portfolio_id,
            event_data={
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                'total_cost': total_cost,
                'order_ref': f"ORD_{uuid.uuid4().hex[:8]}"
            },
            event_version=portfolio.version + 1,
            timestamp=datetime.now().isoformat(),
            user_id=user_id
        )
        
        success = await self.event_store.append_event(event)
        if success:
            logger.info(f"📈 Stock purchased: {quantity} shares of {symbol} @ ₹{price}")
        
        return success
    
    async def sell_stock(self, portfolio_id: str, user_id: str, symbol: str,
                        quantity: int, price: float) -> bool:
        """Stock sell karna"""
        # Current portfolio state check karna
        portfolio = await self.reconstruct_portfolio(portfolio_id)
        
        if symbol not in portfolio.stocks:
            logger.error(f"❌ Stock not found in portfolio: {symbol}")
            return False
            
        available_qty = portfolio.stocks[symbol]['quantity']
        if available_qty < quantity:
            logger.error(f"❌ Insufficient quantity: {available_qty} < {quantity}")
            return False
        
        event = DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.STOCK_SOLD.value,
            aggregate_id=portfolio_id,
            event_data={
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                'total_value': quantity * price,
                'order_ref': f"ORD_{uuid.uuid4().hex[:8]}"
            },
            event_version=portfolio.version + 1,
            timestamp=datetime.now().isoformat(),
            user_id=user_id
        )
        
        success = await self.event_store.append_event(event)
        if success:
            logger.info(f"📉 Stock sold: {quantity} shares of {symbol} @ ₹{price}")
        
        return success
    
    async def reconstruct_portfolio(self, portfolio_id: str) -> Portfolio:
        """
        Events से portfolio state reconstruct karna
        Time machine की तरह - past state को recreate करना
        """
        events = await self.event_store.get_events(portfolio_id)
        
        if not events:
            raise ValueError(f"Portfolio not found: {portfolio_id}")
        
        # Initial portfolio state
        first_event = events[0]
        portfolio = Portfolio(
            portfolio_id=portfolio_id,
            user_id=first_event.user_id
        )
        
        # सभी events को apply करना
        for event in events:
            portfolio = self.event_handler.apply_event(portfolio, event)
        
        return portfolio
    
    async def get_portfolio_at_time(self, portfolio_id: str, 
                                   target_time: datetime) -> Portfolio:
        """
        Specific time par portfolio state retrieve karna
        Historical analysis के लिए useful
        """
        events = await self.event_store.get_events(portfolio_id)
        
        # Filter events before target time
        filtered_events = [
            event for event in events 
            if datetime.fromisoformat(event.timestamp) <= target_time
        ]
        
        if not filtered_events:
            raise ValueError(f"No events found before {target_time}")
        
        # Reconstruct portfolio with filtered events
        first_event = filtered_events[0]
        portfolio = Portfolio(
            portfolio_id=portfolio_id,
            user_id=first_event.user_id
        )
        
        for event in filtered_events:
            portfolio = self.event_handler.apply_event(portfolio, event)
        
        return portfolio

async def zerodha_portfolio_demo():
    """Zerodha portfolio event sourcing demo"""
    print("📊 Zerodha Portfolio Event Sourcing Demo")
    print("=" * 50)
    
    # Event store initialize karna
    event_store = EventStore("zerodha_portfolio.db")
    portfolio_service = PortfolioService(event_store)
    
    # User और portfolio create karna
    user_id = "USER_RAMESH_123"
    portfolio_id = await portfolio_service.create_portfolio(user_id, 0.0)
    
    print(f"👤 User: {user_id}")
    print(f"📊 Portfolio: {portfolio_id}")
    print()
    
    # Funds add karna
    await portfolio_service.add_funds(portfolio_id, user_id, 100000.0)  # ₹1 lakh
    
    # Current portfolio status
    portfolio = await portfolio_service.reconstruct_portfolio(portfolio_id)
    print(f"💰 Current Balance: ₹{portfolio.balance:,.2f}")
    print()
    
    # Stock purchases
    stocks_to_buy = [
        ("RELIANCE", 10, 2500.0),  # Reliance shares
        ("TCS", 5, 3800.0),        # TCS shares
        ("INFY", 8, 1650.0),       # Infosys shares
        ("HDFC", 3, 2750.0),       # HDFC shares
    ]
    
    print("📈 Buying stocks...")
    for symbol, qty, price in stocks_to_buy:
        success = await portfolio_service.buy_stock(portfolio_id, user_id, symbol, qty, price)
        if success:
            print(f"✅ Bought {qty} shares of {symbol} @ ₹{price}")
        else:
            print(f"❌ Failed to buy {symbol}")
        await asyncio.sleep(0.1)
    
    print()
    
    # Current portfolio after purchases
    portfolio = await portfolio_service.reconstruct_portfolio(portfolio_id)
    print("📊 Portfolio Summary:")
    print(f"   💰 Available Balance: ₹{portfolio.balance:,.2f}")
    print(f"   💹 Total Invested: ₹{portfolio.total_invested:,.2f}")
    print(f"   📈 Current Value: ₹{portfolio.current_value:,.2f}")
    print(f"   💵 P&L: ₹{portfolio.profit_loss:,.2f} ({portfolio.profit_loss_percentage:.2f}%)")
    print()
    
    print("📋 Stock Holdings:")
    for symbol, stock_data in portfolio.stocks.items():
        qty = stock_data['quantity']
        avg_price = stock_data['avg_price']
        current_price = stock_data['current_price']
        invested = qty * avg_price
        current_val = qty * current_price
        pnl = current_val - invested
        
        print(f"   📊 {symbol}: {qty} shares @ ₹{avg_price:.2f} avg")
        print(f"      Current: ₹{current_price:.2f}, Value: ₹{current_val:,.2f}, P&L: ₹{pnl:,.2f}")
    print()
    
    # Sell some stocks
    print("📉 Selling some stocks...")
    await portfolio_service.sell_stock(portfolio_id, user_id, "RELIANCE", 5, 2600.0)  # Profit booking
    await portfolio_service.sell_stock(portfolio_id, user_id, "TCS", 2, 3750.0)       # Small loss
    
    # Final portfolio state
    final_portfolio = await portfolio_service.reconstruct_portfolio(portfolio_id)
    print("\n📊 Final Portfolio Summary:")
    print(f"   💰 Available Balance: ₹{final_portfolio.balance:,.2f}")
    print(f"   💹 Total Invested: ₹{final_portfolio.total_invested:,.2f}")
    print(f"   📈 Current Value: ₹{final_portfolio.current_value:,.2f}")
    print(f"   💵 P&L: ₹{final_portfolio.profit_loss:,.2f} ({final_portfolio.profit_loss_percentage:.2f}%)")
    
    # Event history analysis
    print(f"\n📋 Event History Analysis:")
    all_events = await event_store.get_events(portfolio_id)
    print(f"   📝 Total Events: {len(all_events)}")
    
    event_types = {}
    for event in all_events:
        event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
    
    for event_type, count in event_types.items():
        print(f"   🔸 {event_type}: {count} events")
    
    # Point-in-time portfolio (after 3rd event)
    if len(all_events) >= 3:
        third_event_time = datetime.fromisoformat(all_events[2].timestamp)
        historical_portfolio = await portfolio_service.get_portfolio_at_time(
            portfolio_id, third_event_time
        )
        print(f"\n🕒 Portfolio state after 3rd event:")
        print(f"   💰 Balance: ₹{historical_portfolio.balance:,.2f}")
        print(f"   📊 Holdings: {len(historical_portfolio.stocks)} stocks")

if __name__ == "__main__":
    asyncio.run(zerodha_portfolio_demo())
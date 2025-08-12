"""
Projection Rebuilder - IRCTC Booking System के लिए
यह example दिखाता है कि कैसे events से different projections बनाते हैं
"""

import asyncio
import sqlite3
import json
import uuid
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IRCTC Event Types
class IRCTCEventType(Enum):
    """IRCTC events के types"""
    TICKET_SEARCHED = "TICKET_SEARCHED"
    TICKET_BOOKED = "TICKET_BOOKED"
    PAYMENT_PROCESSED = "PAYMENT_PROCESSED"
    TICKET_CONFIRMED = "TICKET_CONFIRMED"
    TICKET_CANCELLED = "TICKET_CANCELLED"
    REFUND_INITIATED = "REFUND_INITIATED"
    SEAT_ALLOCATED = "SEAT_ALLOCATED"
    WAITING_LIST_UPDATED = "WAITING_LIST_UPDATED"
    TATKAL_BOOKING = "TATKAL_BOOKING"

class TicketStatus(Enum):
    """Ticket का status"""
    BOOKED = "BOOKED"
    CONFIRMED = "CONFIRMED"
    WAITING = "WAITING"
    RAC = "RAC"
    CANCELLED = "CANCELLED"

class ClassType(Enum):
    """Train के classes"""
    SL = "Sleeper"
    AC3 = "AC 3 Tier"
    AC2 = "AC 2 Tier"  
    AC1 = "AC 1 Tier"
    CC = "Chair Car"
    EC = "Executive Chair"

# Base Event Structure
@dataclass
class IRCTCEvent:
    """IRCTC events का base structure"""
    event_id: str
    pnr_number: str
    event_type: IRCTCEventType
    timestamp: datetime
    version: int
    data: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

# Event Store
class IRCTCEventStore:
    """IRCTC events के लिए event store"""
    
    def __init__(self, db_path: str = "irctc_events.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Database tables create करता है"""
        with sqlite3.connect(self.db_path) as conn:
            # Main events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS irctc_events (
                    event_id TEXT PRIMARY KEY,
                    pnr_number TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Projections tables
            
            # 1. Ticket Summary Projection
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ticket_summary (
                    pnr_number TEXT PRIMARY KEY,
                    passenger_name TEXT,
                    train_number TEXT,
                    train_name TEXT,
                    from_station TEXT,
                    to_station TEXT,
                    journey_date TEXT,
                    class_type TEXT,
                    seat_numbers TEXT,
                    current_status TEXT,
                    booking_amount REAL,
                    booking_timestamp TEXT,
                    last_updated TEXT
                )
            """)
            
            # 2. Daily Revenue Projection
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_revenue (
                    date TEXT PRIMARY KEY,
                    total_bookings INTEGER DEFAULT 0,
                    total_revenue REAL DEFAULT 0,
                    cancelled_bookings INTEGER DEFAULT 0,
                    refund_amount REAL DEFAULT 0,
                    net_revenue REAL DEFAULT 0,
                    last_updated TEXT
                )
            """)
            
            # 3. Route Popularity Projection
            conn.execute("""
                CREATE TABLE IF NOT EXISTS route_popularity (
                    route_key TEXT PRIMARY KEY,
                    from_station TEXT,
                    to_station TEXT,
                    total_searches INTEGER DEFAULT 0,
                    total_bookings INTEGER DEFAULT 0,
                    conversion_rate REAL DEFAULT 0,
                    peak_booking_hour INTEGER,
                    last_updated TEXT
                )
            """)
            
            # 4. Train Occupancy Projection
            conn.execute("""
                CREATE TABLE IF NOT EXISTS train_occupancy (
                    train_date_key TEXT PRIMARY KEY,
                    train_number TEXT,
                    journey_date TEXT,
                    class_type TEXT,
                    total_seats INTEGER,
                    booked_seats INTEGER DEFAULT 0,
                    confirmed_seats INTEGER DEFAULT 0,
                    waiting_list INTEGER DEFAULT 0,
                    rac_seats INTEGER DEFAULT 0,
                    occupancy_percentage REAL DEFAULT 0,
                    last_updated TEXT
                )
            """)
            
            # 5. User Booking History Projection  
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_booking_history (
                    user_id TEXT,
                    pnr_number TEXT,
                    booking_date TEXT,
                    journey_date TEXT,
                    route TEXT,
                    amount REAL,
                    status TEXT,
                    PRIMARY KEY (user_id, pnr_number)
                )
            """)
            
            # Indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_pnr ON irctc_events(pnr_number)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON irctc_events(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON irctc_events(timestamp)")
            
        logger.info("IRCTC Event Store initialized with projection tables")
    
    async def append_event(self, event: IRCTCEvent) -> bool:
        """Event को store में save करता है"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO irctc_events 
                    (event_id, pnr_number, event_type, timestamp, version, data, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.pnr_number,
                    event.event_type.value,
                    event.timestamp.isoformat(),
                    event.version,
                    json.dumps(event.data),
                    json.dumps(event.metadata) if event.metadata else None
                ))
            
            logger.info(f"IRCTC event stored: {event.event_type.value} for PNR {event.pnr_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store IRCTC event: {str(e)}")
            raise
    
    async def get_events_by_pnr(self, pnr_number: str) -> List[IRCTCEvent]:
        """PNR के सभी events retrieve करता है"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT * FROM irctc_events 
                    WHERE pnr_number = ?
                    ORDER BY version ASC
                """, (pnr_number,))
                
                events = []
                for row in cursor.fetchall():
                    event = IRCTCEvent(
                        event_id=row['event_id'],
                        pnr_number=row['pnr_number'],
                        event_type=IRCTCEventType(row['event_type']),
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        version=row['version'],
                        data=json.loads(row['data']),
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    )
                    events.append(event)
                
                return events
                
        except Exception as e:
            logger.error(f"Failed to get events by PNR: {str(e)}")
            raise
    
    async def get_all_events_stream(self, batch_size: int = 1000):
        """सभी events का stream - projection rebuild के लिए"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                offset = 0
                while True:
                    cursor = conn.execute("""
                        SELECT * FROM irctc_events 
                        ORDER BY timestamp ASC
                        LIMIT ? OFFSET ?
                    """, (batch_size, offset))
                    
                    rows = cursor.fetchall()
                    if not rows:
                        break
                    
                    for row in rows:
                        event = IRCTCEvent(
                            event_id=row['event_id'],
                            pnr_number=row['pnr_number'],
                            event_type=IRCTCEventType(row['event_type']),
                            timestamp=datetime.fromisoformat(row['timestamp']),
                            version=row['version'],
                            data=json.loads(row['data']),
                            metadata=json.loads(row['metadata']) if row['metadata'] else {}
                        )
                        yield event
                    
                    offset += batch_size
                    
        except Exception as e:
            logger.error(f"Failed to stream events: {str(e)}")
            raise

# Projection Builders
class ProjectionBuilder:
    """Base class for all projection builders"""
    
    def __init__(self, event_store: IRCTCEventStore):
        self.event_store = event_store
    
    async def rebuild_projection(self):
        """Projection को completely rebuild करता है"""
        await self._clear_projection()
        
        async for event in self.event_store.get_all_events_stream():
            await self._handle_event(event)
        
        logger.info(f"{self.__class__.__name__} projection rebuilt successfully")
    
    async def _clear_projection(self):
        """Projection data को clear करता है"""
        raise NotImplementedError
    
    async def _handle_event(self, event: IRCTCEvent):
        """Individual event को handle करता है"""
        raise NotImplementedError

class TicketSummaryProjection(ProjectionBuilder):
    """Ticket summary का projection - current state के लिए"""
    
    async def _clear_projection(self):
        """Ticket summary table को clear करता है"""
        with sqlite3.connect(self.event_store.db_path) as conn:
            conn.execute("DELETE FROM ticket_summary")
    
    async def _handle_event(self, event: IRCTCEvent):
        """Ticket events को handle करता है"""
        with sqlite3.connect(self.event_store.db_path) as conn:
            
            if event.event_type == IRCTCEventType.TICKET_BOOKED:
                # नया ticket entry बनाते हैं
                conn.execute("""
                    INSERT OR REPLACE INTO ticket_summary 
                    (pnr_number, passenger_name, train_number, train_name, 
                     from_station, to_station, journey_date, class_type, 
                     current_status, booking_amount, booking_timestamp, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.pnr_number,
                    event.data.get('passenger_name'),
                    event.data.get('train_number'),
                    event.data.get('train_name'),
                    event.data.get('from_station'),
                    event.data.get('to_station'),
                    event.data.get('journey_date'),
                    event.data.get('class_type'),
                    "BOOKED",
                    event.data.get('amount', 0),
                    event.timestamp.isoformat(),
                    datetime.now().isoformat()
                ))
                
            elif event.event_type == IRCTCEventType.TICKET_CONFIRMED:
                # Ticket को confirmed mark करते हैं
                conn.execute("""
                    UPDATE ticket_summary 
                    SET current_status = 'CONFIRMED', 
                        seat_numbers = ?,
                        last_updated = ?
                    WHERE pnr_number = ?
                """, (
                    event.data.get('seat_numbers'),
                    datetime.now().isoformat(),
                    event.pnr_number
                ))
                
            elif event.event_type == IRCTCEventType.TICKET_CANCELLED:
                # Ticket को cancelled mark करते हैं
                conn.execute("""
                    UPDATE ticket_summary 
                    SET current_status = 'CANCELLED',
                        last_updated = ?
                    WHERE pnr_number = ?
                """, (
                    datetime.now().isoformat(),
                    event.pnr_number
                ))

class DailyRevenueProjection(ProjectionBuilder):
    """Daily revenue का projection - analytics के लिए"""
    
    async def _clear_projection(self):
        """Daily revenue table को clear करता है"""
        with sqlite3.connect(self.event_store.db_path) as conn:
            conn.execute("DELETE FROM daily_revenue")
    
    async def _handle_event(self, event: IRCTCEvent):
        """Revenue events को handle करता है"""
        event_date = event.timestamp.date().isoformat()
        
        with sqlite3.connect(self.event_store.db_path) as conn:
            
            if event.event_type == IRCTCEventType.PAYMENT_PROCESSED:
                amount = float(event.data.get('amount', 0))
                
                # Daily revenue entry बनाते या update करते हैं
                conn.execute("""
                    INSERT INTO daily_revenue (date, last_updated)
                    VALUES (?, ?)
                    ON CONFLICT(date) DO NOTHING
                """, (event_date, datetime.now().isoformat()))
                
                conn.execute("""
                    UPDATE daily_revenue 
                    SET total_bookings = total_bookings + 1,
                        total_revenue = total_revenue + ?,
                        net_revenue = total_revenue - refund_amount,
                        last_updated = ?
                    WHERE date = ?
                """, (amount, datetime.now().isoformat(), event_date))
                
            elif event.event_type == IRCTCEventType.REFUND_INITIATED:
                refund_amount = float(event.data.get('refund_amount', 0))
                
                conn.execute("""
                    INSERT INTO daily_revenue (date, last_updated)
                    VALUES (?, ?)
                    ON CONFLICT(date) DO NOTHING
                """, (event_date, datetime.now().isoformat()))
                
                conn.execute("""
                    UPDATE daily_revenue 
                    SET cancelled_bookings = cancelled_bookings + 1,
                        refund_amount = refund_amount + ?,
                        net_revenue = total_revenue - refund_amount,
                        last_updated = ?
                    WHERE date = ?
                """, (refund_amount, datetime.now().isoformat(), event_date))

class RoutePopularityProjection(ProjectionBuilder):
    """Route popularity का projection - demand analysis के लिए"""
    
    async def _clear_projection(self):
        """Route popularity table को clear करता है"""
        with sqlite3.connect(self.event_store.db_path) as conn:
            conn.execute("DELETE FROM route_popularity")
    
    async def _handle_event(self, event: IRCTCEvent):
        """Route events को handle करता है"""
        with sqlite3.connect(self.event_store.db_path) as conn:
            
            if event.event_type == IRCTCEventType.TICKET_SEARCHED:
                from_station = event.data.get('from_station')
                to_station = event.data.get('to_station')
                route_key = f"{from_station}-{to_station}"
                
                # Route entry बनाते या update करते हैं
                conn.execute("""
                    INSERT INTO route_popularity 
                    (route_key, from_station, to_station, total_searches, last_updated)
                    VALUES (?, ?, ?, 1, ?)
                    ON CONFLICT(route_key) DO UPDATE SET
                        total_searches = total_searches + 1,
                        last_updated = ?
                """, (
                    route_key, from_station, to_station,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
            elif event.event_type == IRCTCEventType.TICKET_BOOKED:
                from_station = event.data.get('from_station')
                to_station = event.data.get('to_station')
                route_key = f"{from_station}-{to_station}"
                booking_hour = event.timestamp.hour
                
                conn.execute("""
                    INSERT INTO route_popularity 
                    (route_key, from_station, to_station, total_bookings, peak_booking_hour, last_updated)
                    VALUES (?, ?, ?, 1, ?, ?)
                    ON CONFLICT(route_key) DO UPDATE SET
                        total_bookings = total_bookings + 1,
                        peak_booking_hour = ?,
                        conversion_rate = CASE 
                            WHEN total_searches > 0 
                            THEN (total_bookings * 100.0 / total_searches) 
                            ELSE 0 
                        END,
                        last_updated = ?
                """, (
                    route_key, from_station, to_station, booking_hour,
                    datetime.now().isoformat(),
                    booking_hour,
                    datetime.now().isoformat()
                ))

class TrainOccupancyProjection(ProjectionBuilder):
    """Train occupancy का projection - capacity management के लिए"""
    
    async def _clear_projection(self):
        """Train occupancy table को clear करता है"""
        with sqlite3.connect(self.event_store.db_path) as conn:
            conn.execute("DELETE FROM train_occupancy")
    
    async def _handle_event(self, event: IRCTCEvent):
        """Train occupancy events को handle करता है"""
        with sqlite3.connect(self.event_store.db_path) as conn:
            
            if event.event_type == IRCTCEventType.TICKET_BOOKED:
                train_number = event.data.get('train_number')
                journey_date = event.data.get('journey_date')
                class_type = event.data.get('class_type')
                train_date_key = f"{train_number}-{journey_date}-{class_type}"
                
                # Class capacity map करते हैं
                capacity_map = {
                    "SL": 72,    # Sleeper
                    "AC3": 64,   # AC 3 Tier
                    "AC2": 48,   # AC 2 Tier
                    "AC1": 24,   # AC 1 Tier
                    "CC": 78,    # Chair Car
                    "EC": 56     # Executive Chair
                }
                
                total_capacity = capacity_map.get(class_type, 72)
                
                # Train occupancy entry बनाते या update करते हैं
                conn.execute("""
                    INSERT INTO train_occupancy 
                    (train_date_key, train_number, journey_date, class_type, 
                     total_seats, booked_seats, last_updated)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                    ON CONFLICT(train_date_key) DO UPDATE SET
                        booked_seats = booked_seats + 1,
                        occupancy_percentage = (booked_seats * 100.0 / total_seats),
                        last_updated = ?
                """, (
                    train_date_key, train_number, journey_date, class_type,
                    total_capacity, datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
            elif event.event_type == IRCTCEventType.TICKET_CONFIRMED:
                train_number = event.data.get('train_number')
                journey_date = event.data.get('journey_date')
                class_type = event.data.get('class_type')
                train_date_key = f"{train_number}-{journey_date}-{class_type}"
                
                conn.execute("""
                    UPDATE train_occupancy 
                    SET confirmed_seats = confirmed_seats + 1,
                        last_updated = ?
                    WHERE train_date_key = ?
                """, (datetime.now().isoformat(), train_date_key))

# Projection Manager
class ProjectionManager:
    """सभी projections को manage करता है"""
    
    def __init__(self, event_store: IRCTCEventStore):
        self.event_store = event_store
        self.projections = {
            'ticket_summary': TicketSummaryProjection(event_store),
            'daily_revenue': DailyRevenueProjection(event_store),
            'route_popularity': RoutePopularityProjection(event_store),
            'train_occupancy': TrainOccupancyProjection(event_store)
        }
    
    async def rebuild_all_projections(self):
        """सभी projections को rebuild करता है"""
        logger.info("🔄 Starting projection rebuild for all views...")
        
        for name, projection in self.projections.items():
            logger.info(f"Rebuilding {name} projection...")
            await projection.rebuild_projection()
        
        logger.info("✅ All projections rebuilt successfully")
    
    async def rebuild_projection(self, projection_name: str):
        """Specific projection को rebuild करता है"""
        if projection_name not in self.projections:
            raise ValueError(f"Projection {projection_name} not found")
        
        logger.info(f"🔄 Rebuilding {projection_name} projection...")
        await self.projections[projection_name].rebuild_projection()
        logger.info(f"✅ {projection_name} projection rebuilt")
    
    async def handle_new_event(self, event: IRCTCEvent):
        """नया event आने पर सभी projections को update करता है"""
        await self.event_store.append_event(event)
        
        # सभी projections को real-time update करते हैं
        for projection in self.projections.values():
            await projection._handle_event(event)

# Demo Data Generator
class IRCTCDataGenerator:
    """Demo के लिए realistic IRCTC data generate करता है"""
    
    def __init__(self):
        self.stations = [
            "NEW DELHI", "MUMBAI CENTRAL", "BENGALURU", "CHENNAI CENTRAL",
            "KOLKATA", "PUNE", "HYDERABAD", "AHMEDABAD", "JAIPUR", "LUCKNOW"
        ]
        
        self.trains = [
            {"number": "12951", "name": "MUMBAI RAJDHANI"},
            {"number": "12301", "name": "HOWRAH RAJDHANI"},
            {"number": "22691", "name": "BENGALURU RAJDHANI"},
            {"number": "12615", "name": "GRAND TRUNK EXPRESS"},
            {"number": "16687", "name": "NAVYUG EXPRESS"}
        ]
        
        self.passenger_names = [
            "राम शर्मा", "सीता पटेल", "अमित कुमार", "प्रिया गुप्ता",
            "विकास सिंह", "अंकिता शाह", "रोहित वर्मा", "पूजा जैन"
        ]
    
    def generate_sample_events(self, count: int = 100) -> List[IRCTCEvent]:
        """Sample IRCTC events generate करता है"""
        events = []
        
        for i in range(count):
            # Random data generate करते हैं
            pnr = f"PNR{uuid.uuid4().hex[:10].upper()}"
            train = self.trains[i % len(self.trains)]
            passenger = self.passenger_names[i % len(self.passenger_names)]
            from_station = self.stations[i % len(self.stations)]
            to_station = self.stations[(i + 1) % len(self.stations)]
            
            if from_station == to_station:
                to_station = self.stations[(i + 2) % len(self.stations)]
            
            journey_date = (datetime.now() + timedelta(days=(i % 30))).date().isoformat()
            class_type = ["SL", "AC3", "AC2", "AC1"][i % 4]
            
            # Ticket search event
            search_event = IRCTCEvent(
                event_id=str(uuid.uuid4()),
                pnr_number=pnr,
                event_type=IRCTCEventType.TICKET_SEARCHED,
                timestamp=datetime.now() - timedelta(minutes=i*2),
                version=1,
                data={
                    "from_station": from_station,
                    "to_station": to_station,
                    "journey_date": journey_date,
                    "class_type": class_type
                },
                metadata={"user_ip": "192.168.1.100", "session_id": str(uuid.uuid4())}
            )
            events.append(search_event)
            
            # Ticket booking event (80% conversion rate)
            if i % 5 != 0:  # 80% of searches convert to bookings
                amount = {
                    "SL": 350 + (i % 200),
                    "AC3": 750 + (i % 300), 
                    "AC2": 1200 + (i % 400),
                    "AC1": 2000 + (i % 600)
                }[class_type]
                
                booking_event = IRCTCEvent(
                    event_id=str(uuid.uuid4()),
                    pnr_number=pnr,
                    event_type=IRCTCEventType.TICKET_BOOKED,
                    timestamp=datetime.now() - timedelta(minutes=i*2-5),
                    version=2,
                    data={
                        "passenger_name": passenger,
                        "train_number": train["number"],
                        "train_name": train["name"],
                        "from_station": from_station,
                        "to_station": to_station,
                        "journey_date": journey_date,
                        "class_type": class_type,
                        "amount": amount
                    },
                    metadata={"payment_method": "UPI", "mobile": "98765XXXXX"}
                )
                events.append(booking_event)
                
                # Payment processed event
                payment_event = IRCTCEvent(
                    event_id=str(uuid.uuid4()),
                    pnr_number=pnr,
                    event_type=IRCTCEventType.PAYMENT_PROCESSED,
                    timestamp=datetime.now() - timedelta(minutes=i*2-10),
                    version=3,
                    data={
                        "amount": amount,
                        "payment_method": "UPI",
                        "transaction_id": f"TXN{uuid.uuid4().hex[:12].upper()}"
                    },
                    metadata={"gateway": "PAYTM", "status": "SUCCESS"}
                )
                events.append(payment_event)
                
                # Ticket confirmation (90% of bookings get confirmed)
                if i % 10 != 0:
                    seat_number = f"{class_type}{(i%50)+1:02d}"
                    
                    confirmation_event = IRCTCEvent(
                        event_id=str(uuid.uuid4()),
                        pnr_number=pnr,
                        event_type=IRCTCEventType.TICKET_CONFIRMED,
                        timestamp=datetime.now() - timedelta(minutes=i*2-15),
                        version=4,
                        data={
                            "seat_numbers": seat_number,
                            "coach": f"{class_type}1",
                            "train_number": train["number"],
                            "journey_date": journey_date,
                            "class_type": class_type
                        },
                        metadata={"chart_prepared": True}
                    )
                    events.append(confirmation_event)
        
        return events

# Demo Functions
async def demo_irctc_projections():
    """IRCTC projections का comprehensive demo"""
    print("🚂 IRCTC Projection Rebuilder Demo")
    print("=" * 60)
    
    # Setup
    event_store = IRCTCEventStore("irctc_demo.db")
    projection_manager = ProjectionManager(event_store)
    data_generator = IRCTCDataGenerator()
    
    # Sample data generate करते हैं
    print("📊 Generating sample IRCTC booking data...")
    sample_events = data_generator.generate_sample_events(50)
    
    # Events को store करते हैं
    for event in sample_events:
        await event_store.append_event(event)
    
    print(f"✅ Generated and stored {len(sample_events)} events")
    
    # Projections rebuild करते हैं
    print("\n🔄 Rebuilding all projections...")
    await projection_manager.rebuild_all_projections()
    
    # Projection results display करते हैं
    await display_projection_results(event_store)

async def display_projection_results(event_store: IRCTCEventStore):
    """Projection results को display करता है"""
    
    with sqlite3.connect(event_store.db_path) as conn:
        conn.row_factory = sqlite3.Row
        
        print("\n📋 1. Ticket Summary Projection")
        print("-" * 40)
        
        cursor = conn.execute("""
            SELECT pnr_number, passenger_name, train_name, 
                   from_station, to_station, current_status, booking_amount
            FROM ticket_summary 
            ORDER BY booking_timestamp DESC 
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            print(f"🎫 {row['pnr_number']}: {row['passenger_name']}")
            print(f"   🚂 {row['train_name']}: {row['from_station']} → {row['to_station']}")
            print(f"   💰 ₹{row['booking_amount']} | Status: {row['current_status']}")
            print()
        
        print("\n💰 2. Daily Revenue Projection")
        print("-" * 40)
        
        cursor = conn.execute("""
            SELECT date, total_bookings, total_revenue, 
                   cancelled_bookings, refund_amount, net_revenue
            FROM daily_revenue 
            ORDER BY date DESC 
            LIMIT 7
        """)
        
        for row in cursor.fetchall():
            print(f"📅 {row['date']}")
            print(f"   📊 Bookings: {row['total_bookings']} | Cancelled: {row['cancelled_bookings']}")
            print(f"   💵 Revenue: ₹{row['total_revenue']:.2f} | Refunds: ₹{row['refund_amount']:.2f}")
            print(f"   💎 Net Revenue: ₹{row['net_revenue']:.2f}")
            print()
        
        print("\n🗺️  3. Route Popularity Projection")
        print("-" * 40)
        
        cursor = conn.execute("""
            SELECT from_station, to_station, total_searches, 
                   total_bookings, conversion_rate, peak_booking_hour
            FROM route_popularity 
            ORDER BY total_bookings DESC 
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            print(f"🛤️  {row['from_station']} → {row['to_station']}")
            print(f"   🔍 Searches: {row['total_searches']} | Bookings: {row['total_bookings']}")
            print(f"   📈 Conversion: {row['conversion_rate']:.1f}% | Peak Hour: {row['peak_booking_hour']}:00")
            print()
        
        print("\n🚆 4. Train Occupancy Projection")
        print("-" * 40)
        
        cursor = conn.execute("""
            SELECT train_number, journey_date, class_type, 
                   total_seats, booked_seats, confirmed_seats, occupancy_percentage
            FROM train_occupancy 
            ORDER BY occupancy_percentage DESC 
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            print(f"🚂 Train {row['train_number']} | {row['journey_date']} | {row['class_type']}")
            print(f"   💺 Capacity: {row['total_seats']} | Booked: {row['booked_seats']} | Confirmed: {row['confirmed_seats']}")
            print(f"   📊 Occupancy: {row['occupancy_percentage']:.1f}%")
            print()

async def demo_projection_rebuild_scenario():
    """Projection rebuild scenario का demo"""
    print("\n" + "="*60)
    print("🔄 Projection Rebuild Scenario Demo")
    print("="*60)
    
    event_store = IRCTCEventStore("irctc_demo.db")
    projection_manager = ProjectionManager(event_store)
    
    print("\n📊 Current projection state:")
    
    # Current revenue check करते हैं
    with sqlite3.connect(event_store.db_path) as conn:
        cursor = conn.execute("SELECT SUM(total_revenue) as total FROM daily_revenue")
        current_revenue = cursor.fetchone()[0] or 0
        print(f"💰 Total Revenue in projection: ₹{current_revenue:.2f}")
        
        cursor = conn.execute("SELECT COUNT(*) as count FROM ticket_summary")
        ticket_count = cursor.fetchone()[0]
        print(f"🎫 Total Tickets in projection: {ticket_count}")
    
    print("\n🚀 Simulating data corruption - clearing projections...")
    
    # Projections को manually clear करते हैं (corruption simulate करने के लिए)
    with sqlite3.connect(event_store.db_path) as conn:
        conn.execute("DELETE FROM daily_revenue")
        conn.execute("DELETE FROM ticket_summary")
        conn.execute("DELETE FROM route_popularity")
        conn.execute("DELETE FROM train_occupancy")
    
    print("❌ Projections cleared (corruption simulated)")
    
    # Verify करते हैं कि projections empty हैं
    with sqlite3.connect(event_store.db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM ticket_summary")
        print(f"🎫 Tickets after clearing: {cursor.fetchone()[0]}")
    
    print("\n🔄 Rebuilding projections from event stream...")
    
    # Projections को rebuild करते हैं
    await projection_manager.rebuild_all_projections()
    
    print("✅ Projections rebuilt successfully")
    
    # Verify करते हैं कि data restore हो गया
    with sqlite3.connect(event_store.db_path) as conn:
        cursor = conn.execute("SELECT SUM(total_revenue) as total FROM daily_revenue")
        restored_revenue = cursor.fetchone()[0] or 0
        print(f"💰 Restored Revenue: ₹{restored_revenue:.2f}")
        
        cursor = conn.execute("SELECT COUNT(*) as count FROM ticket_summary")
        restored_tickets = cursor.fetchone()[0]
        print(f"🎫 Restored Tickets: {restored_tickets}")
    
    print(f"\n✅ Data integrity verified:")
    print(f"   Revenue match: {abs(current_revenue - restored_revenue) < 0.01}")
    print(f"   Ticket count match: {ticket_count == restored_tickets}")

if __name__ == "__main__":
    import asyncio
    
    print("Projection Rebuilder Demo")
    print("="*50)
    
    # Main demo
    asyncio.run(demo_irctc_projections())
    
    # Rebuild scenario demo
    asyncio.run(demo_projection_rebuild_scenario())
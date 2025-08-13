#!/usr/bin/env python3
"""
Episode 22: Streaming Architectures - Amazon Kinesis Data Streams for IRCTC Real-time Analytics
Author: Code Developer Agent
Description: AWS Kinesis implementation for IRCTC train booking analytics and monitoring

Kinesis है AWS का managed streaming service
IRCTC जैसे high-volume booking systems के लिए perfect है
"""

import asyncio
import json
import boto3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Mock Kinesis (replace with real boto3 in production)
class MockKinesisClient:
    """Mock Kinesis client for demonstration"""
    
    def __init__(self):
        self.streams = {}
        self.records = []
        print("🌊 Mock Kinesis client initialized")
    
    def put_record(self, StreamName: str, Data: bytes, PartitionKey: str, **kwargs):
        """Put single record to Kinesis stream"""
        record = {
            'SequenceNumber': str(int(time.time() * 1000000)),
            'ApproximateArrivalTimestamp': datetime.now(),
            'Data': Data,
            'PartitionKey': PartitionKey,
            'StreamName': StreamName
        }
        
        self.records.append(record)
        print(f"📤 Record sent to {StreamName}: {PartitionKey}")
        
        return {
            'SequenceNumber': record['SequenceNumber'],
            'ShardId': f"shardId-{hash(PartitionKey) % 4:08d}"
        }
    
    def put_records(self, Records: List[Dict], StreamName: str, **kwargs):
        """Put multiple records to Kinesis stream"""
        failed_records = []
        
        for i, record in enumerate(Records):
            try:
                self.put_record(
                    StreamName=StreamName,
                    Data=record['Data'],
                    PartitionKey=record['PartitionKey']
                )
            except Exception as e:
                failed_records.append({
                    'RecordIndex': i,
                    'ErrorCode': 'InternalFailure',
                    'ErrorMessage': str(e)
                })
        
        return {
            'FailedRecordCount': len(failed_records),
            'Records': [{'SequenceNumber': str(int(time.time() * 1000000))} 
                       for _ in range(len(Records) - len(failed_records))],
            'FailedRecords': failed_records
        }
    
    def get_records(self, ShardIterator: str, Limit: int = 100, **kwargs):
        """Get records from Kinesis stream"""
        # Return last N records for demo
        recent_records = self.records[-Limit:]
        
        kinesis_records = []
        for record in recent_records:
            kinesis_records.append({
                'SequenceNumber': record['SequenceNumber'],
                'ApproximateArrivalTimestamp': record['ApproximateArrivalTimestamp'],
                'Data': record['Data'],
                'PartitionKey': record['PartitionKey']
            })
        
        return {
            'Records': kinesis_records,
            'NextShardIterator': f"iterator-{int(time.time())}"
        }

# IRCTC Domain Models
class BookingStatus(Enum):
    SEARCHING = "searching"
    AVAILABLE = "available"
    BOOKING = "booking"
    CONFIRMED = "confirmed"
    WAITING = "waiting"
    CANCELLED = "cancelled"
    RAC = "rac"

class TrainClass(Enum):
    SL = "sleeper"
    AC3 = "ac_3_tier"
    AC2 = "ac_2_tier"
    AC1 = "ac_1_tier"
    CC = "chair_car"
    EC = "executive_chair"

@dataclass
class IRCTCBookingEvent:
    """IRCTC booking event model"""
    event_id: str
    event_type: str
    user_id: str
    session_id: str
    pnr_number: Optional[str]
    train_number: str
    train_name: str
    from_station: str
    to_station: str
    journey_date: str
    booking_class: TrainClass
    passenger_count: int
    fare_amount: float
    booking_status: BookingStatus
    timestamp: datetime
    device_info: Dict[str, str]
    location: Dict[str, str]
    metadata: Dict[str, Any]

@dataclass
class TrainOccupancyEvent:
    """Train occupancy monitoring event"""
    event_id: str
    train_number: str
    date: str
    from_station: str
    to_station: str
    class_type: TrainClass
    total_seats: int
    booked_seats: int
    waiting_list: int
    rac_list: int
    occupancy_percentage: float
    timestamp: datetime

@dataclass
class PaymentEvent:
    """IRCTC payment event"""
    event_id: str
    pnr_number: str
    payment_id: str
    amount: float
    payment_method: str
    bank_name: str
    payment_status: str
    processing_time_ms: int
    timestamp: datetime

# Kinesis Producers
class IRCTCBookingProducer:
    """High-throughput IRCTC booking events producer"""
    
    def __init__(self, stream_name: str):
        self.kinesis_client = MockKinesisClient()  # Replace with boto3.client('kinesis')
        self.stream_name = stream_name
        self.batch_size = 500
        self.batch_timeout_seconds = 1
        self.record_buffer = []
        self.last_flush = time.time()
        self.lock = threading.Lock()
        
        # Start background flushing
        self.flush_thread = threading.Thread(target=self._background_flush, daemon=True)
        self.flush_thread.start()
    
    async def send_booking_event(self, event: IRCTCBookingEvent):
        """Send booking event to Kinesis"""
        try:
            # Create Kinesis record
            record_data = self._serialize_event(event)
            partition_key = self._get_partition_key(event)
            
            with self.lock:
                self.record_buffer.append({
                    'Data': record_data,
                    'PartitionKey': partition_key
                })
                
                # Flush if batch is full
                if len(self.record_buffer) >= self.batch_size:
                    await self._flush_records()
            
            print(f"📊 IRCTC event queued: {event.event_type} for train {event.train_number}")
            
        except Exception as e:
            print(f"❌ Failed to send booking event: {e}")
            raise
    
    def _serialize_event(self, event: IRCTCBookingEvent) -> bytes:
        """Serialize event to JSON bytes"""
        event_dict = asdict(event)
        event_dict['timestamp'] = event.timestamp.isoformat()
        event_dict['booking_class'] = event.booking_class.value
        event_dict['booking_status'] = event.booking_status.value
        
        return json.dumps(event_dict).encode('utf-8')
    
    def _get_partition_key(self, event: IRCTCBookingEvent) -> str:
        """Get partition key for even distribution"""
        # Partition by train_number + date for even distribution
        partition_data = f"{event.train_number}_{event.journey_date}"
        return hashlib.md5(partition_data.encode()).hexdigest()[:16]
    
    async def _flush_records(self):
        """Flush buffered records to Kinesis"""
        if not self.record_buffer:
            return
        
        try:
            response = self.kinesis_client.put_records(
                Records=self.record_buffer,
                StreamName=self.stream_name
            )
            
            failed_count = response.get('FailedRecordCount', 0)
            success_count = len(self.record_buffer) - failed_count
            
            print(f"📤 Flushed {success_count} records to Kinesis (failed: {failed_count})")
            
            # Clear buffer
            self.record_buffer.clear()
            self.last_flush = time.time()
            
        except Exception as e:
            print(f"❌ Failed to flush records: {e}")
            # Keep records in buffer for retry
    
    def _background_flush(self):
        """Background thread for periodic flushing"""
        while True:
            time.sleep(self.batch_timeout_seconds)
            
            with self.lock:
                if (time.time() - self.last_flush) >= self.batch_timeout_seconds and self.record_buffer:
                    asyncio.run(self._flush_records())

class TrainOccupancyProducer:
    """Train occupancy monitoring producer"""
    
    def __init__(self, stream_name: str):
        self.kinesis_client = MockKinesisClient()
        self.stream_name = stream_name
    
    async def send_occupancy_update(self, event: TrainOccupancyEvent):
        """Send train occupancy update"""
        try:
            # Serialize event
            event_dict = asdict(event)
            event_dict['timestamp'] = event.timestamp.isoformat()
            event_dict['class_type'] = event.class_type.value
            
            record_data = json.dumps(event_dict).encode('utf-8')
            partition_key = f"{event.train_number}_{event.date}_{event.class_type.value}"
            
            response = self.kinesis_client.put_record(
                StreamName=self.stream_name,
                Data=record_data,
                PartitionKey=partition_key
            )
            
            print(f"🚂 Train occupancy sent: {event.train_number} - {event.occupancy_percentage:.1f}%")
            
        except Exception as e:
            print(f"❌ Failed to send occupancy event: {e}")
            raise

# Kinesis Consumers
class IRCTCAnalyticsConsumer:
    """Real-time IRCTC analytics consumer"""
    
    def __init__(self, stream_name: str):
        self.kinesis_client = MockKinesisClient()
        self.stream_name = stream_name
        self.analytics = IRCTCAnalytics()
        self.running = False
    
    async def start_consuming(self):
        """Start consuming and processing events"""
        self.running = True
        print(f"📥 Starting IRCTC analytics consumer for {self.stream_name}")
        
        # Mock shard iterator (in production, use describe_stream and get_shard_iterator)
        shard_iterator = "mock-iterator-000001"
        
        while self.running:
            try:
                # Get records from Kinesis
                response = self.kinesis_client.get_records(
                    ShardIterator=shard_iterator,
                    Limit=100
                )
                
                records = response.get('Records', [])
                
                if records:
                    # Process records
                    await self._process_records(records)
                    
                    # Update shard iterator
                    shard_iterator = response.get('NextShardIterator', shard_iterator)
                else:
                    # No records, wait before next poll
                    await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Consumer error: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def _process_records(self, records: List[Dict]):
        """Process batch of Kinesis records"""
        booking_events = []
        
        for record in records:
            try:
                # Deserialize event
                event_data = json.loads(record['Data'].decode('utf-8'))
                
                if 'train_number' in event_data and 'user_id' in event_data:
                    # This is a booking event
                    booking_event = self._deserialize_booking_event(event_data)
                    booking_events.append(booking_event)
                
            except Exception as e:
                print(f"⚠️ Failed to process record: {e}")
        
        if booking_events:
            # Update analytics
            await self.analytics.process_booking_events(booking_events)
            print(f"📊 Processed {len(booking_events)} booking events")
    
    def _deserialize_booking_event(self, data: Dict) -> IRCTCBookingEvent:
        """Deserialize booking event from JSON"""
        return IRCTCBookingEvent(
            event_id=data['event_id'],
            event_type=data['event_type'],
            user_id=data['user_id'],
            session_id=data['session_id'],
            pnr_number=data.get('pnr_number'),
            train_number=data['train_number'],
            train_name=data['train_name'],
            from_station=data['from_station'],
            to_station=data['to_station'],
            journey_date=data['journey_date'],
            booking_class=TrainClass(data['booking_class']),
            passenger_count=data['passenger_count'],
            fare_amount=data['fare_amount'],
            booking_status=BookingStatus(data['booking_status']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            device_info=data['device_info'],
            location=data['location'],
            metadata=data['metadata']
        )
    
    def stop(self):
        """Stop consuming"""
        self.running = False
        print("🛑 IRCTC analytics consumer stopped")

# Real-time Analytics Engine
class IRCTCAnalytics:
    """Real-time IRCTC booking analytics"""
    
    def __init__(self):
        self.booking_counts = {}
        self.train_popularity = {}
        self.route_analytics = {}
        self.class_preferences = {}
        self.revenue_metrics = {}
        self.user_activity = {}
        self.peak_booking_times = {}
        
    async def process_booking_events(self, events: List[IRCTCBookingEvent]):
        """Process booking events for real-time analytics"""
        for event in events:
            await self._update_booking_analytics(event)
    
    async def _update_booking_analytics(self, event: IRCTCBookingEvent):
        """Update various analytics metrics"""
        
        # 1. Booking counts by hour
        hour_key = event.timestamp.strftime('%Y-%m-%d_%H')
        self.booking_counts[hour_key] = self.booking_counts.get(hour_key, 0) + 1
        
        # 2. Train popularity
        train_key = event.train_number
        if train_key not in self.train_popularity:
            self.train_popularity[train_key] = {
                'train_name': event.train_name,
                'booking_count': 0,
                'total_passengers': 0,
                'total_revenue': 0.0
            }
        
        self.train_popularity[train_key]['booking_count'] += 1
        self.train_popularity[train_key]['total_passengers'] += event.passenger_count
        if event.booking_status == BookingStatus.CONFIRMED:
            self.train_popularity[train_key]['total_revenue'] += event.fare_amount
        
        # 3. Route analytics
        route_key = f"{event.from_station}-{event.to_station}"
        if route_key not in self.route_analytics:
            self.route_analytics[route_key] = {
                'booking_count': 0,
                'passenger_count': 0,
                'average_fare': 0.0,
                'popular_trains': {}
            }
        
        route_stats = self.route_analytics[route_key]
        route_stats['booking_count'] += 1
        route_stats['passenger_count'] += event.passenger_count
        
        # Update average fare
        if route_stats['booking_count'] > 0:
            current_total = route_stats['average_fare'] * (route_stats['booking_count'] - 1)
            route_stats['average_fare'] = (current_total + event.fare_amount) / route_stats['booking_count']
        
        # Popular trains for route
        if event.train_number not in route_stats['popular_trains']:
            route_stats['popular_trains'][event.train_number] = 0
        route_stats['popular_trains'][event.train_number] += 1
        
        # 4. Class preferences
        class_key = event.booking_class.value
        if class_key not in self.class_preferences:
            self.class_preferences[class_key] = {
                'booking_count': 0,
                'passenger_count': 0,
                'revenue': 0.0
            }
        
        self.class_preferences[class_key]['booking_count'] += 1
        self.class_preferences[class_key]['passenger_count'] += event.passenger_count
        if event.booking_status == BookingStatus.CONFIRMED:
            self.class_preferences[class_key]['revenue'] += event.fare_amount
        
        # 5. User activity patterns
        if event.user_id not in self.user_activity:
            self.user_activity[event.user_id] = {
                'booking_count': 0,
                'total_spent': 0.0,
                'preferred_class': {},
                'favorite_routes': {}
            }
        
        user_stats = self.user_activity[event.user_id]
        user_stats['booking_count'] += 1
        if event.booking_status == BookingStatus.CONFIRMED:
            user_stats['total_spent'] += event.fare_amount
        
        # Track preferred class
        if class_key not in user_stats['preferred_class']:
            user_stats['preferred_class'][class_key] = 0
        user_stats['preferred_class'][class_key] += 1
        
        # Track favorite routes
        if route_key not in user_stats['favorite_routes']:
            user_stats['favorite_routes'][route_key] = 0
        user_stats['favorite_routes'][route_key] += 1
    
    def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time analytics dashboard data"""
        
        # Top 5 popular trains
        top_trains = sorted(
            self.train_popularity.items(),
            key=lambda x: x[1]['booking_count'],
            reverse=True
        )[:5]
        
        # Top 5 popular routes
        top_routes = sorted(
            self.route_analytics.items(),
            key=lambda x: x[1]['booking_count'],
            reverse=True
        )[:5]
        
        # Class distribution
        total_bookings = sum(stats['booking_count'] for stats in self.class_preferences.values())
        class_distribution = {}
        for class_type, stats in self.class_preferences.items():
            percentage = (stats['booking_count'] / total_bookings * 100) if total_bookings > 0 else 0
            class_distribution[class_type] = {
                'bookings': stats['booking_count'],
                'percentage': round(percentage, 2),
                'revenue': stats['revenue']
            }
        
        # Recent booking activity (last hour)
        current_hour = datetime.now().strftime('%Y-%m-%d_%H')
        recent_bookings = self.booking_counts.get(current_hour, 0)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_bookings': sum(self.booking_counts.values()),
            'recent_bookings_hour': recent_bookings,
            'top_trains': [
                {
                    'train_number': train_no,
                    'train_name': stats['train_name'],
                    'bookings': stats['booking_count'],
                    'passengers': stats['total_passengers'],
                    'revenue': stats['total_revenue']
                }
                for train_no, stats in top_trains
            ],
            'top_routes': [
                {
                    'route': route,
                    'bookings': stats['booking_count'],
                    'passengers': stats['passenger_count'],
                    'avg_fare': round(stats['average_fare'], 2)
                }
                for route, stats in top_routes
            ],
            'class_distribution': class_distribution,
            'active_users': len(self.user_activity)
        }

# Event Generator for Demo
class IRCTCEventGenerator:
    """Generate realistic IRCTC booking events"""
    
    def __init__(self):
        self.trains = [
            {"number": "12951", "name": "Mumbai Rajdhani Express"},
            {"number": "12302", "name": "Kolkata Rajdhani Express"},
            {"number": "12434", "name": "Chennai Rajdhani Express"},
            {"number": "22692", "name": "Bangalore Rajdhani Express"},
            {"number": "12650", "name": "Karnataka Express"},
            {"number": "11014", "name": "Lokmanya Tilak Express"},
            {"number": "12516", "name": "Thiruvananthapuram Express"},
            {"number": "12618", "name": "Mangala Lakshadweep Express"}
        ]
        
        self.stations = [
            "NDLS", "CSTM", "HWH", "MAS", "SBC", "PUNE", "NGP", "BPL", "JBP", "AGC"
        ]
        
        self.users = [f"USER{i:03d}" for i in range(1, 101)]  # 100 users
    
    def generate_booking_event(self) -> IRCTCBookingEvent:
        """Generate realistic booking event"""
        import random
        
        train = random.choice(self.trains)
        from_station = random.choice(self.stations)
        to_station = random.choice([s for s in self.stations if s != from_station])
        
        # Generate journey date (next 60 days)
        journey_date = (datetime.now() + timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d')
        
        return IRCTCBookingEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:8].upper()}",
            event_type=random.choice(["search", "booking_attempt", "booking_confirmed", "payment"]),
            user_id=random.choice(self.users),
            session_id=f"SESS_{uuid.uuid4().hex[:8]}",
            pnr_number=f"PNR{random.randint(1000000000, 9999999999)}" if random.random() > 0.3 else None,
            train_number=train["number"],
            train_name=train["name"],
            from_station=from_station,
            to_station=to_station,
            journey_date=journey_date,
            booking_class=random.choice(list(TrainClass)),
            passenger_count=random.randint(1, 6),
            fare_amount=round(random.uniform(200, 5000), 2),
            booking_status=random.choice(list(BookingStatus)),
            timestamp=datetime.now(),
            device_info={
                "platform": random.choice(["web", "android", "ios"]),
                "app_version": "1.2.3"
            },
            location={
                "city": random.choice(["Mumbai", "Delhi", "Kolkata", "Chennai", "Bangalore"]),
                "state": "Maharashtra"
            },
            metadata={
                "booking_channel": random.choice(["website", "mobile_app", "api"]),
                "payment_method": random.choice(["credit_card", "debit_card", "upi", "net_banking"])
            }
        )

# Demo Function
async def demonstrate_irctc_kinesis_streaming():
    """Demonstrate IRCTC streaming with Kinesis"""
    print("🚂 IRCTC Kinesis Streaming Analytics Demo")
    print("=" * 50)
    
    # Setup producers and consumers
    booking_producer = IRCTCBookingProducer("irctc-booking-events")
    analytics_consumer = IRCTCAnalyticsConsumer("irctc-booking-events")
    event_generator = IRCTCEventGenerator()
    
    try:
        # Start analytics consumer
        consumer_task = asyncio.create_task(analytics_consumer.start_consuming())
        
        # Generate booking events
        print("\n📊 Generating IRCTC booking events...")
        
        for i in range(50):  # Generate 50 events
            event = event_generator.generate_booking_event()
            await booking_producer.send_booking_event(event)
            
            # Small delay to simulate real-time flow
            await asyncio.sleep(0.1)
            
            if (i + 1) % 10 == 0:
                print(f"📈 Generated {i + 1} events")
        
        # Let consumer process events
        print("\n⏳ Processing events...")
        await asyncio.sleep(3)
        
        # Get analytics dashboard
        dashboard = analytics_consumer.analytics.get_real_time_dashboard()
        
        print("\n📊 Real-time IRCTC Analytics Dashboard:")
        print("=" * 50)
        print(f"📈 Total Bookings: {dashboard['total_bookings']}")
        print(f"🕐 Recent Bookings (Last Hour): {dashboard['recent_bookings_hour']}")
        print(f"👥 Active Users: {dashboard['active_users']}")
        
        print(f"\n🚂 Top Popular Trains:")
        for i, train in enumerate(dashboard['top_trains'], 1):
            print(f"  {i}. {train['train_number']} - {train['train_name']}")
            print(f"     Bookings: {train['bookings']}, Revenue: ₹{train['revenue']:.2f}")
        
        print(f"\n🛤️ Top Popular Routes:")
        for i, route in enumerate(dashboard['top_routes'], 1):
            print(f"  {i}. {route['route']}")
            print(f"     Bookings: {route['bookings']}, Avg Fare: ₹{route['avg_fare']}")
        
        print(f"\n🎫 Class Distribution:")
        for class_type, stats in dashboard['class_distribution'].items():
            print(f"  {class_type}: {stats['bookings']} bookings ({stats['percentage']:.1f}%)")
        
        # Stop consumer
        analytics_consumer.stop()
        await asyncio.sleep(1)
        
        print("\n✅ IRCTC Kinesis Streaming Demo completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        analytics_consumer.stop()

if __name__ == "__main__":
    """
    Key Amazon Kinesis Benefits for IRCTC:
    1. High Throughput: Millions of booking events per second
    2. Real-time Processing: Immediate analytics और insights
    3. Scalability: Auto-scaling based on demand
    4. Durability: Data retention for replay
    5. Integration: Easy AWS service integration
    6. Cost-effective: Pay per use model
    7. Managed Service: No infrastructure management
    """
    asyncio.run(demonstrate_irctc_kinesis_streaming())
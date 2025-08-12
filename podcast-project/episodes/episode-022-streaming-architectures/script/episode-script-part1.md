# Episode 022: Streaming Architectures & Real-Time Processing - Part 1
## Mumbai se Aaya Data Stream - Real-Time Processing ki Kahani

*Duration: 60 minutes*
*Language: 70% Hindi/Roman Hindi, 30% Technical English*
*Target: 13,000+ words for Part 1*

---

### Introduction: Mumbai Local Train System aur Stream Processing

Namaskar dosto! Welcome kar raha hun Episode 22 mein - "Streaming Architectures aur Real-Time Processing". Aaj hum baat karenge ki kaise Mumbai local trains ki tarah data streams continuously process hote hain, aur kaise modern applications real-time mein millions of events handle karte hain.

Mumbai mein jitna organized local train system hai, utna hi organized stream processing systems hote hain. Jaise every 3 minutes mein train aati hai Dadar station pe, waise hi every millisecond mein events process hote hain streaming systems mein. But difference yeh hai ki train mein delay ho sakti hai, but production streaming systems mein delay matlab paisa loss!

### Real-Time Processing ki Zaroorat: Indian Digital Revolution

#### UPI Payment Processing: Per Second 50,000 Transactions

Socho 2024 mein UPI ne process kiye 400+ million transactions daily. Matlab har second 4,600+ payments! Ye sab real-time mein process hona chahiye, warna log payment app uninstall kar denge.

**UPI Real-time Architecture Example:**

```python
# UPI Real-time Payment Processing System
from dataclasses import dataclass
from typing import Dict, List, Optional
import time
import asyncio

@dataclass
class UPITransaction:
    transaction_id: str
    sender_vpa: str  # Virtual Payment Address
    receiver_vpa: str
    amount: float
    timestamp: float
    device_id: str
    location: str
    merchant_category: Optional[str] = None

class UPIStreamProcessor:
    def __init__(self):
        # Mumbai local train ki tarah har station (processing stage) ke liye
        # alag platform (partition) banate hain
        self.fraud_detector = FraudDetectionEngine()
        self.risk_manager = RiskManagementEngine()
        self.notification_service = NotificationService()
        
        # Velocity limits - jaise train mein capacity limit hoti hai
        self.velocity_limits = {
            'hourly_amount': 50000,    # ₹50K per hour limit
            'daily_amount': 100000,    # ₹1L per day limit
            'transaction_count': 20    # 20 transactions per hour
        }
    
    async def process_payment_stream(self, transaction: UPITransaction):
        """
        Mumbai local train ki tarah efficient processing
        Har transaction 200ms mein process hona chahiye
        """
        start_time = time.time()
        
        try:
            # Step 1: Express train ki tarah fast validation
            validation_result = await self.validate_transaction(transaction)
            if not validation_result['is_valid']:
                return self.reject_transaction(transaction, validation_result['reason'])
            
            # Step 2: Local train stops ki tarah detailed checks
            fraud_score = await self.fraud_detector.assess_risk(transaction)
            
            # Step 3: Risk management - jaise RPF check karta hai
            risk_assessment = await self.risk_manager.evaluate(transaction)
            
            # Step 4: Final decision in <200ms - Mumbai mein train ke time se bhi fast!
            decision = self.make_payment_decision(fraud_score, risk_assessment)
            
            # Step 5: Real-time notifications
            if decision['status'] == 'approved':
                await self.send_success_notifications(transaction)
            else:
                await self.send_failure_notifications(transaction, decision['reason'])
            
            processing_time = (time.time() - start_time) * 1000
            print(f"✅ Transaction {transaction.transaction_id} processed in {processing_time:.2f}ms")
            
            return decision
            
        except Exception as e:
            # Train derailment ki tarah exception handle karna
            await self.handle_processing_error(transaction, str(e))
            return {'status': 'error', 'reason': 'system_error'}
    
    async def validate_transaction(self, txn: UPITransaction) -> Dict:
        """Mumbai Metro ki security check ki tarah validation"""
        
        # Basic validations
        if txn.amount <= 0:
            return {'is_valid': False, 'reason': 'Invalid amount'}
        
        if txn.amount > 200000:  # ₹2L UPI limit
            return {'is_valid': False, 'reason': 'Amount exceeds UPI limit'}
        
        # VPA format validation
        if '@' not in txn.sender_vpa or '@' not in txn.receiver_vpa:
            return {'is_valid': False, 'reason': 'Invalid VPA format'}
        
        # Account balance check (simplified)
        sender_balance = await self.get_account_balance(txn.sender_vpa)
        if sender_balance < txn.amount:
            return {'is_valid': False, 'reason': 'Insufficient balance'}
        
        return {'is_valid': True}

class FraudDetectionEngine:
    """
    Mumbai Police ki tarah fraud detect karta hai
    Real-time mein suspicious patterns identify karta hai
    """
    
    def __init__(self):
        self.ml_model = MLFraudModel()
        self.rule_engine = RuleBasedEngine()
    
    async def assess_risk(self, transaction: UPITransaction) -> Dict:
        """Real-time fraud assessment - <50ms mein complete"""
        
        risk_score = 0
        risk_factors = []
        
        # Velocity checks - Mumbai local mein crowd control ki tarah
        velocity_risk = await self.check_velocity_patterns(transaction)
        risk_score += velocity_risk['score']
        risk_factors.extend(velocity_risk['factors'])
        
        # Geographic analysis - impossible travel detection
        geo_risk = await self.analyze_geographic_patterns(transaction)
        risk_score += geo_risk['score']
        risk_factors.extend(geo_risk['factors'])
        
        # ML model prediction
        ml_risk = await self.ml_model.predict_fraud_probability(transaction)
        risk_score += ml_risk * 50  # Scale to 0-50 range
        
        if ml_risk > 0.8:
            risk_factors.append(f'High ML fraud probability: {ml_risk:.2f}')
        
        # Device fingerprinting
        device_risk = await self.analyze_device_patterns(transaction)
        risk_score += device_risk['score']
        risk_factors.extend(device_risk['factors'])
        
        return {
            'total_score': risk_score,
            'risk_factors': risk_factors,
            'ml_probability': ml_risk
        }
    
    async def check_velocity_patterns(self, txn: UPITransaction) -> Dict:
        """
        Mumbai local mein jaise har station pe crowd control hoti hai,
        waise hi transaction velocity control karte hain
        """
        
        # Get recent transactions for sender
        recent_txns = await self.get_recent_transactions(txn.sender_vpa, hours=24)
        
        # Calculate velocity metrics
        last_hour_amount = sum(
            t.amount for t in recent_txns 
            if t.timestamp > time.time() - 3600
        )
        
        last_hour_count = len([
            t for t in recent_txns 
            if t.timestamp > time.time() - 3600
        ])
        
        score = 0
        factors = []
        
        # Too many transactions - Mumbai peak hour ki tarah
        if last_hour_count >= 15:
            score += 30
            factors.append(f'High transaction frequency: {last_hour_count} in last hour')
        
        # Too much amount - jaise ATM withdrawal limit
        if last_hour_amount + txn.amount > 50000:
            score += 25
            factors.append(f'High velocity amount: ₹{last_hour_amount + txn.amount}')
        
        # Round amounts - money laundering indicator
        if txn.amount % 1000 == 0 and txn.amount >= 10000:
            score += 15
            factors.append('Suspicious round amount')
        
        return {'score': score, 'factors': factors}
    
    async def analyze_geographic_patterns(self, txn: UPITransaction) -> Dict:
        """
        Impossible travel detection - Mumbai se Delhi 1 minute mein nahi ja sakte!
        """
        
        # Get last transaction location
        last_location = await self.get_last_transaction_location(txn.sender_vpa)
        
        if not last_location:
            return {'score': 0, 'factors': []}
        
        # Calculate distance and time
        distance_km = self.calculate_distance(last_location['coordinates'], 
                                            self.get_coordinates(txn.location))
        time_diff_hours = (txn.timestamp - last_location['timestamp']) / 3600
        
        score = 0
        factors = []
        
        if time_diff_hours > 0:
            speed_kmh = distance_km / time_diff_hours
            
            # Impossible travel - faster than flight!
            if speed_kmh > 500:  # 500 km/h impossible for ground travel
                score += 50
                factors.append(f'Impossible travel speed: {speed_kmh:.1f} km/h')
            
            # Suspicious travel - too fast for train/car
            elif speed_kmh > 100 and distance_km > 50:
                score += 20
                factors.append(f'Suspicious travel speed: {speed_kmh:.1f} km/h')
        
        return {'score': score, 'factors': factors}

# Usage example for IPL betting scenario (where legal)
async def process_ipl_betting_payments():
    """
    IPL match ke time betting payments ki stream processing
    CSK vs MI match ke time 100K+ transactions per minute!
    """
    
    processor = UPIStreamProcessor()
    
    # Simulate betting payment surge during boundary
    betting_transactions = [
        UPITransaction(
            transaction_id=f"ipl_bet_{i}",
            sender_vpa=f"user{i}@paytm",
            receiver_vpa="dream11@icici",
            amount=100 + (i % 1000),  # ₹100 to ₹1100 bets
            timestamp=time.time(),
            device_id=f"device_{i % 1000}",
            location="mumbai_bandra" if i % 2 == 0 else "delhi_cp"
        )
        for i in range(10000)  # 10K simultaneous bets
    ]
    
    # Process all transactions concurrently
    tasks = [
        processor.process_payment_stream(txn) 
        for txn in betting_transactions
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Analyze results
    successful = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'approved')
    fraud_blocked = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'blocked')
    errors = sum(1 for r in results if isinstance(r, Exception))
    
    print(f"""
    IPL Betting Payment Processing Results:
    ✅ Successful: {successful} ({successful/len(results)*100:.1f}%)
    🚫 Fraud Blocked: {fraud_blocked} ({fraud_blocked/len(results)*100:.1f}%)
    ❌ Errors: {errors} ({errors/len(results)*100:.1f}%)
    
    Mumbai Local ki tarah efficient! Peak time mein bhi smooth processing 🚆
    """)

# Run the IPL betting simulation
if __name__ == "__main__":
    asyncio.run(process_ipl_betting_payments())
```

#### Hotstar Live Streaming: 300+ Million Concurrent Viewers

IPL finals ke time Hotstar ne achieve kiya 300+ million concurrent viewers. Imagine karo - Mumbai ki population se 20 guna zyada log same time pe streaming kar rahe the! Ye sab real-time stream processing se possible hua.

**Hotstar-style Live Streaming Architecture:**

```python
# Live Streaming Real-time Analytics System
import asyncio
from dataclasses import dataclass
from typing import Dict, List
import time
from collections import defaultdict

@dataclass
class ViewerEvent:
    user_id: str
    session_id: str
    content_id: str
    event_type: str  # 'play', 'pause', 'stop', 'quality_change'
    timestamp: float
    quality: str     # '720p', '1080p', '4K'
    buffer_health: float  # 0-100%
    location: str
    device_type: str

class HotstarStreamAnalytics:
    """
    Mumbai local train ki frequency se events process karte hain
    Har second mein thousands of viewer events
    """
    
    def __init__(self):
        # Real-time counters - jaise railway station pe digital display
        self.concurrent_viewers = defaultdict(int)
        self.quality_distribution = defaultdict(lambda: defaultdict(int))
        self.regional_stats = defaultdict(lambda: defaultdict(int))
        
        # Alert thresholds
        self.alert_thresholds = {
            'concurrent_limit': 50_000_000,  # 50M viewers pe alert
            'buffer_health_threshold': 20,    # 20% se niche buffer
            'quality_drop_threshold': 30      # 30% quality drops
        }
    
    async def process_viewer_event_stream(self, event: ViewerEvent):
        """
        Every viewer event ko real-time process karna
        Mumbai mein har 3 minutes mein train ki tarah regular
        """
        
        # Update real-time counters
        await self.update_concurrent_viewers(event)
        
        # Track quality metrics
        await self.track_streaming_quality(event)
        
        # Geographic distribution
        await self.update_regional_statistics(event)
        
        # Buffer health monitoring
        await self.monitor_buffer_health(event)
        
        # Check for alerts
        alerts = await self.check_for_alerts(event)
        for alert in alerts:
            await self.send_operations_alert(alert)
    
    async def update_concurrent_viewers(self, event: ViewerEvent):
        """Mumbai local mein live passenger count ki tarah"""
        
        content_id = event.content_id
        
        if event.event_type == 'play':
            self.concurrent_viewers[content_id] += 1
        elif event.event_type in ['stop', 'pause']:
            self.concurrent_viewers[content_id] = max(0, 
                self.concurrent_viewers[content_id] - 1)
        
        # Log milestone achievements
        current_count = self.concurrent_viewers[content_id]
        if current_count % 1_000_000 == 0:  # Every 1M viewers
            print(f"🎉 Milestone! {current_count/1_000_000:.0f}M concurrent viewers for {content_id}")
    
    async def track_streaming_quality(self, event: ViewerEvent):
        """
        Quality distribution tracking
        Mumbai local mein AC vs non-AC ratio ki tarah
        """
        
        content_id = event.content_id
        location = event.location
        
        if event.event_type == 'quality_change':
            self.quality_distribution[content_id][event.quality] += 1
            
            # Regional quality preferences
            self.regional_stats[location][f'quality_{event.quality}'] += 1
            
            # Check for quality downgrades (network issues)
            if event.quality in ['480p', '360p']:
                await self.alert_poor_quality_region(location, event.quality)
    
    async def monitor_buffer_health(self, event: ViewerEvent):
        """
        Buffer health monitoring - jaise train delay tracking
        """
        
        if event.buffer_health < self.alert_thresholds['buffer_health_threshold']:
            # Poor buffer health indicates network/CDN issues
            await self.investigate_cdn_performance(event.location, event.content_id)
            
            # Auto-scale CDN capacity for that region
            await self.auto_scale_cdn_capacity(event.location)
    
    async def check_for_alerts(self, event: ViewerEvent) -> List[Dict]:
        """Real-time alert system"""
        
        alerts = []
        content_id = event.content_id
        current_viewers = self.concurrent_viewers[content_id]
        
        # Concurrent viewer limit alert
        if current_viewers > self.alert_thresholds['concurrent_limit']:
            alerts.append({
                'type': 'SCALE_ALERT',
                'severity': 'HIGH',
                'message': f'Concurrent viewers ({current_viewers}) exceeding capacity',
                'action': 'AUTO_SCALE_IMMEDIATELY'
            })
        
        # Regional overload alert
        regional_load = self.regional_stats[event.location].get('active_streams', 0)
        if regional_load > 5_000_000:  # 5M in single region
            alerts.append({
                'type': 'REGIONAL_OVERLOAD',
                'severity': 'MEDIUM',
                'message': f'Regional overload in {event.location}: {regional_load} streams',
                'action': 'ACTIVATE_BACKUP_CDNS'
            })
        
        return alerts

# Mumbai IPL Match Streaming Simulation
class IPLStreamingSimulator:
    """
    CSK vs MI final ki streaming simulate karte hain
    Mumbai mein sab log match dekh rahe hain!
    """
    
    def __init__(self):
        self.analytics = HotstarStreamAnalytics()
        
    async def simulate_match_viewership(self):
        """IPL final match ka realistic simulation"""
        
        # Match phases with different viewer patterns
        match_phases = [
            {'phase': 'pre_match', 'duration': 1800, 'viewer_multiplier': 0.3},
            {'phase': 'toss', 'duration': 600, 'viewer_multiplier': 0.8},
            {'phase': 'first_innings', 'duration': 7200, 'viewer_multiplier': 1.0},
            {'phase': 'break', 'duration': 1200, 'viewer_multiplier': 0.6},
            {'phase': 'second_innings', 'duration': 7200, 'viewer_multiplier': 1.2},
            {'phase': 'super_over', 'duration': 600, 'viewer_multiplier': 1.5}
        ]
        
        base_viewers = 50_000_000  # 50M base viewers
        
        for phase in match_phases:
            print(f"\n🏏 Starting {phase['phase']} phase...")
            
            phase_viewers = int(base_viewers * phase['viewer_multiplier'])
            duration = phase['duration']
            
            # Generate realistic viewer events
            await self.generate_phase_events(phase_viewers, duration, phase['phase'])
            
            print(f"✅ {phase['phase']} completed - Peak viewers: {phase_viewers:,}")
    
    async def generate_phase_events(self, viewer_count: int, duration: int, phase: str):
        """Generate realistic viewer events for match phase"""
        
        # Regional distribution (Indian viewership patterns)
        regional_distribution = {
            'mumbai': 0.15,     # Mumbai (CSK fans + local)
            'chennai': 0.12,    # Chennai (CSK home)
            'delhi': 0.10,      # Delhi
            'bangalore': 0.10,  # Bangalore
            'hyderabad': 0.08,  # Hyderabad
            'kolkata': 0.08,    # Kolkata
            'other_india': 0.32, # Rest of India
            'international': 0.05 # NRI viewers
        }
        
        # Device distribution
        device_distribution = {
            'mobile': 0.70,     # Mobile dominant in India
            'smart_tv': 0.15,   # Smart TV growing
            'tablet': 0.10,     # Tablets
            'laptop': 0.05      # Laptops
        }
        
        events_per_second = viewer_count // 100  # Assume 1% events per second
        
        for second in range(duration):
            # Generate events for this second
            second_events = []
            
            for _ in range(events_per_second):
                # Random viewer event
                event = ViewerEvent(
                    user_id=f"user_{time.time()}_{_}",
                    session_id=f"session_{time.time()}_{_}",
                    content_id="ipl_csk_vs_mi_final_2024",
                    event_type=self.get_random_event_type(phase),
                    timestamp=time.time(),
                    quality=self.get_quality_based_on_location(),
                    buffer_health=self.get_realistic_buffer_health(),
                    location=self.weighted_random_choice(regional_distribution),
                    device_type=self.weighted_random_choice(device_distribution)
                )
                
                second_events.append(event)
            
            # Process all events for this second
            tasks = [
                self.analytics.process_viewer_event_stream(event)
                for event in second_events
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Print progress every minute
            if second % 60 == 0:
                concurrent = self.analytics.concurrent_viewers["ipl_csk_vs_mi_final_2024"]
                print(f"  ⏱️  {second//60} min - Concurrent viewers: {concurrent:,}")
    
    def get_random_event_type(self, phase: str) -> str:
        """Phase-specific event type distribution"""
        
        if phase == 'super_over':
            # More engagement during super over
            return random.choices(
                ['play', 'quality_change', 'pause', 'stop'],
                weights=[70, 20, 8, 2]
            )[0]
        else:
            return random.choices(
                ['play', 'quality_change', 'pause', 'stop'],
                weights=[60, 15, 20, 5]
            )[0]
    
    def get_quality_based_on_location(self) -> str:
        """Indian network conditions based quality distribution"""
        
        # Indian internet reality - most people on lower quality
        return random.choices(
            ['1080p', '720p', '480p', '360p'],
            weights=[10, 30, 40, 20]  # Reality of Indian internet
        )[0]
    
    def get_realistic_buffer_health(self) -> float:
        """Realistic buffer health based on Indian network conditions"""
        
        # Indian network variability
        return random.gauss(75, 25)  # Mean 75%, std dev 25%
    
    def weighted_random_choice(self, choices_dict: Dict[str, float]) -> str:
        """Helper for weighted random selection"""
        import random
        
        choices = list(choices_dict.keys())
        weights = list(choices_dict.values())
        return random.choices(choices, weights=weights)[0]

# Run IPL streaming simulation
async def run_ipl_simulation():
    """Complete IPL match streaming simulation"""
    
    print("🏏 Starting IPL CSK vs MI Final Streaming Simulation")
    print("📊 Real-time analytics processing Mumbai-style!")
    
    simulator = IPLStreamingSimulator()
    await simulator.simulate_match_viewership()
    
    print("\n🎉 Match completed! Final statistics:")
    analytics = simulator.analytics
    
    total_viewers = analytics.concurrent_viewers["ipl_csk_vs_mi_final_2024"]
    print(f"📈 Peak concurrent viewers: {total_viewers:,}")
    
    # Regional breakdown
    print("\n🌍 Regional distribution:")
    for region, stats in analytics.regional_stats.items():
        if stats:
            print(f"  {region}: {sum(stats.values()):,} total events")
    
    print("\n🎯 Mumbai local train se bhi efficient streaming! 🚆")

if __name__ == "__main__":
    import random
    asyncio.run(run_ipl_simulation())
```

### Stream Processing Fundamentals: Concepts aur Theory

#### Mumbai Local Train Metaphor for Stream Processing

Mumbai local train system perfect hai stream processing samjhane ke liye:

**1. Train Lines as Streams**: 
- Western Line = User Events Stream
- Central Line = Payment Events Stream  
- Harbour Line = Analytics Events Stream

**2. Stations as Processing Stages**:
- Dadar = Data Enrichment Station
- Bandra = Transformation Station
- Andheri = Aggregation Station

**3. Peak Hours as Load Balancing**:
- 9 AM peak = Morning traffic surge
- 6 PM peak = Evening processing load

**4. Express vs Local as Processing Patterns**:
- Express trains = Critical path processing
- Local trains = Bulk processing

#### Stream Processing vs Batch Processing

**Traditional Batch Processing (Old School)**:
```python
# Batch processing - jaise school mein monthly exam
def process_monthly_sales_report():
    """
    Mahine bhar ka data collect karke month end mein process karna
    """
    
    # Wait for month to complete
    sales_data = get_monthly_sales_data()  # 30 days ka data
    
    # Process everything at once
    processed_data = []
    for day_data in sales_data:
        daily_summary = calculate_daily_metrics(day_data)
        processed_data.append(daily_summary)
    
    # Generate monthly report
    monthly_report = generate_monthly_report(processed_data)
    
    # Send to stakeholders
    send_report_to_management(monthly_report)
    
    print("Monthly report generated - next report after 30 days")

# Stream processing - jaise Mumbai local train continuous service
class RealTimeSalesProcessor:
    """
    Har sale ke immediately process karna - real-time insights
    """
    
    def __init__(self):
        self.running_totals = {
            'daily_sales': 0,
            'monthly_sales': 0,
            'product_counts': defaultdict(int)
        }
    
    async def process_sale_event(self, sale: SaleEvent):
        """Har sale immediately process - Mumbai local ki frequency"""
        
        # Update running totals
        self.running_totals['daily_sales'] += sale.amount
        self.running_totals['monthly_sales'] += sale.amount
        self.running_totals['product_counts'][sale.product_id] += 1
        
        # Real-time alerts
        if self.running_totals['daily_sales'] > 1_000_000:  # ₹10L milestone
            await self.send_milestone_alert("Daily sales crossed ₹10L!")
        
        # Real-time dashboard update
        await self.update_live_dashboard()
        
        # Inventory alerts
        if sale.product_id in self.low_stock_products:
            await self.alert_inventory_team(sale.product_id)
    
    async def continuous_processing(self):
        """24x7 continuous processing like Mumbai locals"""
        
        while True:  # Mumbai local ki tarah never stops
            try:
                # Get next sale event from stream
                sale_event = await self.get_next_sale_event()
                await self.process_sale_event(sale_event)
                
            except Exception as e:
                # Handle errors gracefully - service disruption nahi chahiye
                await self.handle_processing_error(e)
```

**Key Differences**:

| Aspect | Batch Processing | Stream Processing |
|--------|------------------|-------------------|
| **Latency** | Hours/Days | Milliseconds/Seconds |
| **Data Size** | Large chunks | Individual events |
| **Resource Usage** | Periodic peaks | Consistent usage |
| **Use Case** | Monthly reports | Real-time alerts |
| **Mumbai Analogy** | Monthly railway timetable | Live train tracking |

#### Windowing Concepts: Time ke Saath Data Processing

Windowing stream processing ka fundamental concept hai. Mumbai local trains ki time windows ki tarah data ko time periods mein divide karte hain.

**Types of Windows with Mumbai Examples**:

```python
# Windowing Concepts with Mumbai Local Train Examples
from datetime import datetime, timedelta
from collections import defaultdict
import time

class MumbaiTrainWindowingExample:
    """
    Mumbai local train passenger counting with different window types
    """
    
    def __init__(self):
        self.passenger_counts = []
        self.window_results = defaultdict(list)
    
    def tumbling_window_example(self):
        """
        Tumbling Windows: Non-overlapping fixed periods
        Jaise Mumbai local mein har ghante ka passenger count
        """
        
        print("🚆 Tumbling Window: Hourly Passenger Count")
        print("=" * 50)
        
        # Simulate 24 hours of passenger data
        hours = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00',
                '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
                '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']
        
        passenger_counts = [150, 80, 45, 30, 40, 200,     # Night to early morning
                          800, 2500, 3000, 1500, 1200, 1000,  # Morning peak
                          900, 800, 700, 600, 700, 1200,      # Afternoon
                          2800, 2200, 1800, 1000, 600, 300]   # Evening peak
        
        for hour, count in zip(hours, passenger_counts):
            window_type = self.classify_hour(hour, count)
            print(f"{hour}-{(int(hour[:2]) + 1) % 24:02d}:00 | {count:4d} passengers | {window_type}")
        
        print("\n📊 Tumbling Window Summary:")
        print(f"Peak Morning (07:00-10:00): {sum(passenger_counts[7:10]):,} passengers")
        print(f"Peak Evening (18:00-21:00): {sum(passenger_counts[18:21]):,} passengers")
        print(f"Off-peak (23:00-06:00): {sum(passenger_counts[23:] + passenger_counts[:6]):,} passengers")
    
    def sliding_window_example(self):
        """
        Sliding Windows: Overlapping periods
        Jaise Mumbai mein rolling 3-hour passenger density tracking
        """
        
        print("\n🔄 Sliding Window: 3-Hour Rolling Passenger Density")
        print("=" * 60)
        
        # 24 hours ka hourly data
        hourly_passengers = [150, 80, 45, 30, 40, 200, 800, 2500, 3000, 1500, 
                           1200, 1000, 900, 800, 700, 600, 700, 1200, 2800, 
                           2200, 1800, 1000, 600, 300]
        
        window_size = 3  # 3-hour sliding window
        
        for i in range(len(hourly_passengers) - window_size + 1):
            window_data = hourly_passengers[i:i + window_size]
            window_total = sum(window_data)
            window_avg = window_total / window_size
            
            start_hour = f"{i:02d}:00"
            end_hour = f"{(i + window_size) % 24:02d}:00"
            
            print(f"{start_hour}-{end_hour} | Total: {window_total:4d} | Avg: {window_avg:6.1f} | Trend: {self.get_trend(window_data)}")
    
    def session_window_example(self):
        """
        Session Windows: Activity-based grouping
        Jaise Mumbai local mein passenger journey sessions
        """
        
        print("\n👥 Session Window: Passenger Journey Sessions")
        print("=" * 50)
        
        # Passenger entry/exit events with timestamps
        passenger_events = [
            {'passenger_id': 'P001', 'event': 'entry', 'station': 'Churchgate', 'time': '08:00'},
            {'passenger_id': 'P001', 'event': 'exit', 'station': 'Andheri', 'time': '08:45'},
            {'passenger_id': 'P001', 'event': 'entry', 'station': 'Andheri', 'time': '18:30'},
            {'passenger_id': 'P001', 'event': 'exit', 'station': 'Churchgate', 'time': '19:15'},
            
            {'passenger_id': 'P002', 'event': 'entry', 'station': 'Bandra', 'time': '09:15'},
            {'passenger_id': 'P002', 'event': 'exit', 'station': 'CST', 'time': '09:50'},
            
            {'passenger_id': 'P003', 'event': 'entry', 'station': 'Dadar', 'time': '08:20'},
            {'passenger_id': 'P003', 'event': 'exit', 'station': 'Lower Parel', 'time': '08:35'},
            {'passenger_id': 'P003', 'event': 'entry', 'station': 'Lower Parel', 'time': '08:40'},
            {'passenger_id': 'P003', 'event': 'exit', 'station': 'Dadar', 'time': '08:55'},
        ]
        
        # Group events into sessions (timeout = 30 minutes)
        sessions = self.create_passenger_sessions(passenger_events, timeout_minutes=30)
        
        for session in sessions:
            print(f"Session {session['session_id']}:")
            print(f"  Passenger: {session['passenger_id']}")
            print(f"  Journey: {session['start_station']} → {session['end_station']}")
            print(f"  Duration: {session['duration_minutes']} minutes")
            print(f"  Travel pattern: {session['pattern']}")
            print()
    
    def classify_hour(self, hour: str, count: int) -> str:
        """Classify hour based on passenger count"""
        
        if count > 2000:
            return "🔴 PEAK"
        elif count > 1000:
            return "🟡 BUSY"
        elif count > 500:
            return "🟢 NORMAL"
        else:
            return "🔵 QUIET"
    
    def get_trend(self, window_data: list) -> str:
        """Get trend for sliding window"""
        
        if len(window_data) < 2:
            return "STABLE"
        
        if window_data[-1] > window_data[0] * 1.2:
            return "📈 RISING"
        elif window_data[-1] < window_data[0] * 0.8:
            return "📉 FALLING"
        else:
            return "➡️ STABLE"
    
    def create_passenger_sessions(self, events: list, timeout_minutes: int = 30) -> list:
        """Create passenger journey sessions"""
        
        sessions = []
        passenger_state = defaultdict(lambda: {'last_event_time': None, 'current_session': None})
        
        for event in events:
            passenger_id = event['passenger_id']
            event_time = self.parse_time(event['time'])
            
            # Check for session timeout
            last_time = passenger_state[passenger_id]['last_event_time']
            if last_time and (event_time - last_time).total_seconds() > timeout_minutes * 60:
                # Session timeout - close current session
                current_session = passenger_state[passenger_id]['current_session']
                if current_session:
                    sessions.append(current_session)
                passenger_state[passenger_id]['current_session'] = None
            
            # Handle event
            if event['event'] == 'entry':
                # Start new session
                passenger_state[passenger_id]['current_session'] = {
                    'session_id': f"S{len(sessions) + 1:03d}",
                    'passenger_id': passenger_id,
                    'start_station': event['station'],
                    'start_time': event_time,
                    'end_station': None,
                    'end_time': None,
                    'duration_minutes': 0,
                    'pattern': 'unknown'
                }
            
            elif event['event'] == 'exit':
                # End current session
                current_session = passenger_state[passenger_id]['current_session']
                if current_session:
                    current_session['end_station'] = event['station']
                    current_session['end_time'] = event_time
                    duration = (event_time - current_session['start_time']).total_seconds() / 60
                    current_session['duration_minutes'] = int(duration)
                    current_session['pattern'] = self.classify_journey_pattern(current_session)
                    sessions.append(current_session)
                    passenger_state[passenger_id]['current_session'] = None
            
            passenger_state[passenger_id]['last_event_time'] = event_time
        
        return sessions
    
    def parse_time(self, time_str: str) -> datetime:
        """Parse time string to datetime"""
        hour, minute = map(int, time_str.split(':'))
        return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def classify_journey_pattern(self, session: dict) -> str:
        """Classify journey pattern"""
        
        start = session['start_station']
        end = session['end_station']
        duration = session['duration_minutes']
        
        # Define station types
        business_districts = ['CST', 'Churchgate', 'Lower Parel', 'BKC']
        residential_areas = ['Andheri', 'Bandra', 'Borivali', 'Virar']
        
        if start in residential_areas and end in business_districts:
            return "🏠→🏢 Home to Work"
        elif start in business_districts and end in residential_areas:
            return "🏢→🏠 Work to Home"
        elif duration < 20:
            return "🚶 Local Trip"
        else:
            return "🗺️ Long Distance"

# Run windowing examples
def demonstrate_windowing_concepts():
    """Demonstrate all windowing concepts with Mumbai examples"""
    
    print("🚆 Mumbai Local Train Windowing Concepts")
    print("=" * 50)
    
    example = MumbaiTrainWindowingExample()
    
    # Tumbling windows
    example.tumbling_window_example()
    
    # Sliding windows
    example.sliding_window_example()
    
    # Session windows
    example.session_window_example()
    
    print("✅ All windowing concepts demonstrated Mumbai-style! 🌟")

if __name__ == "__main__":
    demonstrate_windowing_concepts()
```

#### Event Time vs Processing Time

Stream processing mein time ke do concepts hain - jaise Mumbai local mein scheduled time vs actual arrival time:

**Event Time**: Jab event actually hua tha (scheduled train time)
**Processing Time**: Jab system ne event process kiya (actual arrival time)

```python
# Event Time vs Processing Time Concepts
from datetime import datetime, timedelta
import time
import random

class EventTimeProcessingTimeExample:
    """
    Mumbai local train delays se event time vs processing time samjhate hain
    """
    
    def __init__(self):
        self.processed_events = []
        self.late_arrivals = []
    
    def simulate_train_schedule_events(self):
        """
        Mumbai local train schedule vs actual arrival simulation
        """
        
        print("🚆 Mumbai Local: Event Time vs Processing Time")
        print("=" * 60)
        
        # Scheduled train times (Event Time)
        scheduled_trains = [
            {'train_id': 'WR001', 'scheduled_time': '08:00', 'route': 'Churchgate-Virar'},
            {'train_id': 'WR002', 'scheduled_time': '08:03', 'route': 'Churchgate-Virar'},
            {'train_id': 'WR003', 'scheduled_time': '08:06', 'route': 'Churchgate-Virar'},
            {'train_id': 'WR004', 'scheduled_time': '08:09', 'route': 'Churchgate-Virar'},
            {'train_id': 'WR005', 'scheduled_time': '08:12', 'route': 'Churchgate-Virar'},
        ]
        
        print("Train Schedule Processing:")
        print("Train ID | Scheduled (Event Time) | Actual (Processing Time) | Delay | Status")
        print("-" * 80)
        
        for train in scheduled_trains:
            # Simulate network delays, system processing delays
            delay_seconds = random.randint(-60, 300)  # -1 min to +5 min delay
            
            scheduled_dt = self.parse_time(train['scheduled_time'])
            actual_dt = scheduled_dt + timedelta(seconds=delay_seconds)
            
            delay_minutes = delay_seconds / 60
            status = self.get_delay_status(delay_minutes)
            
            print(f"{train['train_id']} | {train['scheduled_time']}:00        | {actual_dt.strftime('%H:%M:%S')}        | {delay_minutes:+5.1f}m | {status}")
            
            # Record late arrival for watermark calculation
            if delay_seconds > 0:
                self.late_arrivals.append({
                    'train_id': train['train_id'],
                    'event_time': scheduled_dt,
                    'processing_time': actual_dt,
                    'delay_seconds': delay_seconds
                })
    
    def demonstrate_watermarks(self):
        """
        Watermarks with Mumbai local example
        Watermark = System ka estimate ki kitni delay expect kar sakte hain
        """
        
        print("\n💧 Watermarks: Mumbai Local Delay Estimation")
        print("=" * 50)
        
        if not self.late_arrivals:
            print("No late arrivals recorded for watermark calculation")
            return
        
        # Calculate watermark based on historical delays
        delays = [arrival['delay_seconds'] for arrival in self.late_arrivals]
        max_delay = max(delays)
        avg_delay = sum(delays) / len(delays)
        p95_delay = sorted(delays)[int(len(delays) * 0.95)]
        
        print(f"Historical Delay Analysis:")
        print(f"  Maximum delay: {max_delay/60:.1f} minutes")
        print(f"  Average delay: {avg_delay/60:.1f} minutes") 
        print(f"  95th percentile: {p95_delay/60:.1f} minutes")
        
        # Set watermark (conservative estimate)
        watermark_delay = p95_delay + 60  # P95 + 1 minute buffer
        
        print(f"\n🚰 Watermark Strategy:")
        print(f"  Wait time: {watermark_delay/60:.1f} minutes")
        print(f"  Meaning: Wait {watermark_delay/60:.1f} min before considering train 'definitely late'")
        
        # Simulate processing with watermark
        print(f"\n📊 Processing with Watermark:")
        current_time = datetime.now().replace(second=0, microsecond=0)
        watermark_time = current_time - timedelta(seconds=watermark_delay)
        
        for arrival in self.late_arrivals:
            if arrival['event_time'] <= watermark_time:
                print(f"  ✅ {arrival['train_id']}: Safe to process (before watermark)")
            else:
                print(f"  ⏳ {arrival['train_id']}: Still waiting (within watermark window)")
    
    def handle_out_of_order_events(self):
        """
        Out-of-order event handling
        Jaise Mumbai mein kabhi kabhi trains overtake kar jaati hain
        """
        
        print("\n🔀 Out-of-Order Events: Train Overtaking Scenario")
        print("=" * 55)
        
        # Simulate trains arriving out of order
        trains_arrival_order = [
            {'train_id': 'WR003', 'scheduled': '08:06', 'actual_arrival': '08:05'},  # Early
            {'train_id': 'WR001', 'scheduled': '08:00', 'actual_arrival': '08:07'},  # Late
            {'train_id': 'WR004', 'scheduled': '08:09', 'actual_arrival': '08:08'},  # Early
            {'train_id': 'WR002', 'scheduled': '08:03', 'actual_arrival': '08:10'},  # Very late
            {'train_id': 'WR005', 'scheduled': '08:12', 'actual_arrival': '08:11'},  # Early
        ]
        
        print("Processing Order vs Scheduled Order:")
        print("Arrival Order | Train ID | Scheduled | Actual | Issue")
        print("-" * 55)
        
        for i, train in enumerate(trains_arrival_order):
            issue = "ON TIME"
            if i > 0:
                prev_scheduled = self.parse_time(trains_arrival_order[i-1]['scheduled'])
                current_scheduled = self.parse_time(train['scheduled'])
                if current_scheduled < prev_scheduled:
                    issue = "🔄 OUT OF ORDER"
            
            print(f"     {i+1}     | {train['train_id']} |  {train['scheduled']}   |  {train['actual_arrival']}  | {issue}")
        
        # Show how to handle with buffering
        print(f"\n🛡️ Handling Strategy:")
        print(f"  1. Buffer events for 5 minutes before processing")
        print(f"  2. Sort by scheduled time within buffer window")
        print(f"  3. Process in correct order even if arrived late")
        print(f"  4. Alert if delay exceeds acceptable watermark")
    
    def parse_time(self, time_str: str) -> datetime:
        """Parse time string"""
        hour, minute = map(int, time_str.split(':'))
        return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def get_delay_status(self, delay_minutes: float) -> str:
        """Get status based on delay"""
        if delay_minutes <= 0:
            return "✅ ON TIME"
        elif delay_minutes <= 2:
            return "🟡 MINOR DELAY"
        elif delay_minutes <= 5:
            return "🟠 DELAY"
        else:
            return "🔴 MAJOR DELAY"

# Run the example
def demonstrate_time_concepts():
    """Demonstrate event time vs processing time concepts"""
    
    example = EventTimeProcessingTimeExample()
    
    # Simulate train events
    example.simulate_train_schedule_events()
    
    # Demonstrate watermarks
    example.demonstrate_watermarks()
    
    # Handle out-of-order events
    example.handle_out_of_order_events()
    
    print("\n✅ Time concepts demonstrated with Mumbai local examples! 🚆")

if __name__ == "__main__":
    demonstrate_time_concepts()
```

### Stream Processing Frameworks: Apache Flink vs Apache Spark Streaming

#### Apache Flink: The Low-Latency Champion

Apache Flink Mumbai local trains ki tarah true streaming framework hai - continuous processing with very low latency.

**Flink Architecture aur Production Implementation**:

```python
# Apache Flink-style Real-time Processing (Python simulation)
# Real production mein Java/Scala use karte hain, but concepts same hain

from dataclasses import dataclass
from typing import Dict, List, Optional
import asyncio
import time
from collections import defaultdict, deque
import json

@dataclass
class FlipkartOrderEvent:
    order_id: str
    customer_id: str
    product_id: str
    quantity: int
    price: float
    timestamp: float
    payment_method: str
    delivery_city: str
    event_type: str  # 'order_placed', 'payment_success', 'shipped', 'delivered'

class FlinkStyleStreamProcessor:
    """
    Apache Flink style processing for Flipkart order stream
    Mumbai local train ki efficiency ke saath
    """
    
    def __init__(self):
        # Flink-style operator state
        self.keyed_state = defaultdict(dict)
        self.window_state = defaultdict(lambda: defaultdict(list))
        self.watermark = 0
        
        # Performance metrics
        self.processed_events = 0
        self.processing_latency = deque(maxlen=1000)
        
        # Checkpointing state for fault tolerance
        self.checkpoint_interval = 5  # seconds
        self.last_checkpoint = time.time()
        
    async def process_order_stream(self, orders: List[FlipkartOrderEvent]):
        """
        Flink-style stream processing pipeline
        """
        
        print("🏭 Starting Flink-style Order Stream Processing")
        print("=" * 50)
        
        # Process each order with Flink-like operations
        for order in orders:
            start_time = time.time()
            
            # Step 1: Key by customer (like Flink keyBy)
            await self.key_by_customer(order)
            
            # Step 2: Windowed aggregations (like Flink timeWindow)
            await self.process_windowed_aggregations(order)
            
            # Step 3: CEP pattern detection (like Flink CEP)
            await self.detect_order_patterns(order)
            
            # Step 4: Sink to downstream systems
            await self.sink_to_analytics(order)
            
            # Track processing latency
            processing_time = (time.time() - start_time) * 1000
            self.processing_latency.append(processing_time)
            self.processed_events += 1
            
            # Checkpoint periodically (Flink-style fault tolerance)
            if time.time() - self.last_checkpoint > self.checkpoint_interval:
                await self.create_checkpoint()
            
            # Print progress
            if self.processed_events % 1000 == 0:
                avg_latency = sum(self.processing_latency) / len(self.processing_latency)
                print(f"  ✅ Processed {self.processed_events:,} events, Avg latency: {avg_latency:.2f}ms")
    
    async def key_by_customer(self, order: FlipkartOrderEvent):
        """
        Flink keyBy() operation equivalent
        Customer ke basis pe events group karna
        """
        
        customer_id = order.customer_id
        
        # Update customer state
        if customer_id not in self.keyed_state:
            self.keyed_state[customer_id] = {
                'total_orders': 0,
                'total_spent': 0.0,
                'favorite_categories': defaultdict(int),
                'last_order_time': 0,
                'vip_status': False
            }
        
        customer_state = self.keyed_state[customer_id]
        
        # Update customer metrics
        if order.event_type == 'order_placed':
            customer_state['total_orders'] += 1
            customer_state['total_spent'] += order.price * order.quantity
            customer_state['last_order_time'] = order.timestamp
            
            # VIP status check - Mumbai local ki first class pass ki tarah
            if customer_state['total_spent'] > 100000:  # ₹1L+ spent
                customer_state['vip_status'] = True
                await self.trigger_vip_benefits(order, customer_state)
    
    async def process_windowed_aggregations(self, order: FlipkartOrderEvent):
        """
        Flink windowing operations
        Time-based aggregations jaise Mumbai local ki hourly passenger count
        """
        
        # 1-hour tumbling window
        hour_window = int(order.timestamp // 3600) * 3600
        window_key = f"hourly_{hour_window}"
        
        if window_key not in self.window_state:
            self.window_state[window_key] = {
                'total_orders': 0,
                'total_revenue': 0.0,
                'city_breakdown': defaultdict(int),
                'payment_methods': defaultdict(int)
            }
        
        window = self.window_state[window_key]
        
        if order.event_type == 'order_placed':
            window['total_orders'] += 1
            window['total_revenue'] += order.price * order.quantity
            window['city_breakdown'][order.delivery_city] += 1
            window['payment_methods'][order.payment_method] += 1
            
            # Alert for unusual patterns
            if window['total_orders'] > 10000:  # 10K orders in an hour
                await self.send_peak_traffic_alert(window_key, window)
    
    async def detect_order_patterns(self, order: FlipkartOrderEvent):
        """
        Flink CEP (Complex Event Processing)
        Mumbai local mein jaise pattern detect karte hain (peak hours, etc.)
        """
        
        customer_id = order.customer_id
        
        # Pattern 1: Rapid successive orders (potential fraud)
        customer_orders = self.get_recent_customer_orders(customer_id, minutes=10)
        if len(customer_orders) > 5:  # 5+ orders in 10 minutes
            await self.flag_suspicious_activity(order, "rapid_orders")
        
        # Pattern 2: High-value order from new customer
        customer_state = self.keyed_state[customer_id]
        if (customer_state['total_orders'] == 1 and 
            order.price * order.quantity > 50000):  # ₹50K+ first order
            await self.trigger_manual_review(order, "high_value_new_customer")
        
        # Pattern 3: Cross-city delivery pattern
        if self.is_cross_country_delivery(order):
            await self.optimize_logistics(order)
    
    async def sink_to_analytics(self, order: FlipkartOrderEvent):
        """
        Flink sink operations - downstream systems ko data send karna
        """
        
        # Sink to different systems based on event type
        if order.event_type == 'order_placed':
            await self.update_inventory_system(order)
            await self.update_recommendation_engine(order)
            await self.notify_seller(order)
        
        elif order.event_type == 'payment_success':
            await self.trigger_fulfillment(order)
            await self.update_revenue_tracking(order)
        
        elif order.event_type == 'delivered':
            await self.update_delivery_metrics(order)
            await self.trigger_review_request(order)
    
    async def create_checkpoint(self):
        """
        Flink-style checkpointing for fault tolerance
        Mumbai local ki backup plan ki tarah
        """
        
        checkpoint_data = {
            'timestamp': time.time(),
            'processed_events': self.processed_events,
            'keyed_state_size': len(self.keyed_state),
            'window_state_size': len(self.window_state)
        }
        
        # In production, this would be saved to distributed storage
        print(f"📸 Checkpoint created: {checkpoint_data}")
        self.last_checkpoint = time.time()
    
    def get_recent_customer_orders(self, customer_id: str, minutes: int) -> List:
        """Get customer's recent orders within time window"""
        # Simplified implementation
        return []  # In production, query from state or external store
    
    async def trigger_vip_benefits(self, order: FlipkartOrderEvent, customer_state: dict):
        """Trigger VIP customer benefits"""
        print(f"👑 VIP benefits triggered for customer {order.customer_id}")
    
    async def send_peak_traffic_alert(self, window_key: str, window: dict):
        """Send alert for peak traffic"""
        print(f"🚨 Peak traffic alert: {window['total_orders']} orders in window {window_key}")
    
    async def flag_suspicious_activity(self, order: FlipkartOrderEvent, reason: str):
        """Flag suspicious order patterns"""
        print(f"⚠️ Suspicious activity: {reason} for order {order.order_id}")
    
    async def trigger_manual_review(self, order: FlipkartOrderEvent, reason: str):
        """Trigger manual review for high-risk orders"""
        print(f"👨‍💼 Manual review triggered: {reason} for order {order.order_id}")
    
    def is_cross_country_delivery(self, order: FlipkartOrderEvent) -> bool:
        """Check if order requires cross-country delivery"""
        return order.delivery_city in ['Kashmir', 'Assam', 'Kerala']
    
    async def optimize_logistics(self, order: FlipkartOrderEvent):
        """Optimize logistics for special deliveries"""
        print(f"🚚 Logistics optimization for {order.delivery_city} delivery")
    
    async def update_inventory_system(self, order: FlipkartOrderEvent):
        """Update inventory after order placement"""
        pass
    
    async def update_recommendation_engine(self, order: FlipkartOrderEvent):
        """Update recommendation engine with new purchase"""
        pass
    
    async def notify_seller(self, order: FlipkartOrderEvent):
        """Notify seller about new order"""
        pass
    
    async def trigger_fulfillment(self, order: FlipkartOrderEvent):
        """Trigger order fulfillment process"""
        pass
    
    async def update_revenue_tracking(self, order: FlipkartOrderEvent):
        """Update revenue tracking systems"""
        pass
    
    async def update_delivery_metrics(self, order: FlipkartOrderEvent):
        """Update delivery performance metrics"""
        pass
    
    async def trigger_review_request(self, order: FlipkartOrderEvent):
        """Request customer review after delivery"""
        pass

# Generate sample Flipkart order data
def generate_flipkart_orders(count: int) -> List[FlipkartOrderEvent]:
    """Generate realistic Flipkart order events"""
    
    import random
    
    products = ['smartphone', 'laptop', 'tshirt', 'books', 'shoes', 'headphones']
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad']
    payment_methods = ['UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'COD']
    event_types = ['order_placed', 'payment_success', 'shipped', 'delivered']
    
    orders = []
    base_time = time.time()
    
    for i in range(count):
        order = FlipkartOrderEvent(
            order_id=f"FL{i+1:06d}",
            customer_id=f"CUST{random.randint(1, count//10):04d}",  # Some repeat customers
            product_id=random.choice(products),
            quantity=random.randint(1, 5),
            price=random.uniform(500, 50000),  # ₹500 to ₹50K
            timestamp=base_time + i * random.uniform(0.1, 2),  # Realistic timing
            payment_method=random.choice(payment_methods),
            delivery_city=random.choice(cities),
            event_type=random.choice(event_types)
        )
        orders.append(order)
    
    return orders

# Run Flink-style processing simulation
async def run_flink_simulation():
    """Run Flipkart order processing with Flink-style architecture"""
    
    print("🏭 Flink-style Real-time Order Processing for Flipkart")
    print("🚆 Mumbai Local Train efficiency ke saath!")
    print("=" * 60)
    
    # Generate sample orders
    orders = generate_flipkart_orders(10000)  # 10K orders
    print(f"📦 Generated {len(orders):,} order events")
    
    # Process with Flink-style processor
    processor = FlinkStyleStreamProcessor()
    start_time = time.time()
    
    await processor.process_order_stream(orders)
    
    total_time = time.time() - start_time
    throughput = len(orders) / total_time
    
    print(f"\n📊 Processing Results:")
    print(f"  Total Events: {len(orders):,}")
    print(f"  Processing Time: {total_time:.2f} seconds")
    print(f"  Throughput: {throughput:.0f} events/second")
    print(f"  Avg Latency: {sum(processor.processing_latency) / len(processor.processing_latency):.2f}ms")
    print(f"  Customer States: {len(processor.keyed_state):,}")
    print(f"  Window States: {len(processor.window_state):,}")
    
    print(f"\n✅ Flink-style processing complete - Mumbai local efficiency achieved! 🌟")

if __name__ == "__main__":
    asyncio.run(run_flink_simulation())
```

#### Apache Spark Streaming: Micro-batch Champion

Spark Streaming Mumbai local ke micro-batches ki tarah kaam karta hai - small batches of data process karta hai instead of individual events.

**Spark Streaming vs Structured Streaming**:

```python
# Spark Structured Streaming Style (Python simulation)
# Real production mein PySpark use karte hain

from dataclasses import dataclass
from typing import Dict, List
import time
import asyncio
from collections import defaultdict

@dataclass
class ZomatoOrderEvent:
    order_id: str
    restaurant_id: str
    customer_id: str
    items: List[str]
    total_amount: float
    timestamp: float
    delivery_location: str
    payment_status: str
    delivery_partner_id: str

class SparkStructuredStreamingProcessor:
    """
    Spark Structured Streaming style processing for Zomato orders
    Mumbai mein food delivery ki tarah efficient batching
    """
    
    def __init__(self, batch_interval: int = 5):
        self.batch_interval = batch_interval  # seconds
        self.current_batch = []
        self.batch_number = 0
        
        # Structured Streaming-style state
        self.global_state = {
            'restaurant_stats': defaultdict(lambda: {'orders': 0, 'revenue': 0}),
            'delivery_partner_stats': defaultdict(lambda: {'deliveries': 0, 'total_earnings': 0}),
            'location_stats': defaultdict(lambda: {'order_count': 0, 'avg_amount': 0})
        }
        
        # Performance tracking
        self.batch_processing_times = []
        self.total_events_processed = 0
    
    async def process_zomato_order_stream(self, orders: List[ZomatoOrderEvent]):
        """
        Structured Streaming processing pipeline
        Mumbai local ki tarah regular intervals mein batches
        """
        
        print("🍽️ Starting Spark Structured Streaming for Zomato Orders")
        print(f"📦 Batch interval: {self.batch_interval} seconds")
        print("=" * 60)
        
        batch_start_time = time.time()
        
        for order in orders:
            # Add to current batch
            self.current_batch.append(order)
            
            # Check if batch interval reached or batch size limit
            current_time = time.time()
            if (current_time - batch_start_time >= self.batch_interval or 
                len(self.current_batch) >= 1000):  # Max 1000 events per batch
                
                # Process current batch
                await self.process_batch()
                
                # Reset for next batch
                self.current_batch = []
                batch_start_time = current_time
                
            # Small delay to simulate real-time arrival
            await asyncio.sleep(0.001)
        
        # Process final batch if any
        if self.current_batch:
            await self.process_batch()
        
        # Print final statistics
        self.print_final_statistics()
    
    async def process_batch(self):
        """
        Process single batch - Spark Structured Streaming style
        """
        
        if not self.current_batch:
            return
        
        batch_start = time.time()
        self.batch_number += 1
        
        print(f"\n🔄 Processing Batch #{self.batch_number} ({len(self.current_batch)} events)")
        
        # Batch transformations (like Spark DataFrame operations)
        await self.restaurant_aggregations()
        await self.delivery_partner_analytics()
        await self.location_based_insights()
        await self.real_time_recommendations()
        
        # Batch completion
        batch_time = time.time() - batch_start
        self.batch_processing_times.append(batch_time)
        self.total_events_processed += len(self.current_batch)
        
        print(f"  ✅ Batch #{self.batch_number} completed in {batch_time:.3f}s")
        print(f"  📊 Throughput: {len(self.current_batch)/batch_time:.0f} events/sec")
    
    async def restaurant_aggregations(self):
        """
        Restaurant-wise aggregations (like groupBy in Spark)
        """
        
        restaurant_batch_stats = defaultdict(lambda: {'orders': 0, 'revenue': 0})
        
        # Process current batch for restaurant stats
        for order in self.current_batch:
            restaurant_batch_stats[order.restaurant_id]['orders'] += 1
            restaurant_batch_stats[order.restaurant_id]['revenue'] += order.total_amount
            
            # Update global state
            self.global_state['restaurant_stats'][order.restaurant_id]['orders'] += 1
            self.global_state['restaurant_stats'][order.restaurant_id]['revenue'] += order.total_amount
        
        # Find top performing restaurants in this batch
        top_restaurants = sorted(
            restaurant_batch_stats.items(),
            key=lambda x: x[1]['revenue'],
            reverse=True
        )[:3]
        
        print(f"    🏆 Top restaurants in batch:")
        for restaurant_id, stats in top_restaurants:
            print(f"      {restaurant_id}: {stats['orders']} orders, ₹{stats['revenue']:.0f}")
    
    async def delivery_partner_analytics(self):
        """
        Delivery partner performance analytics
        Mumbai mein delivery boys ka performance track karna
        """
        
        partner_batch_stats = defaultdict(lambda: {'deliveries': 0, 'earnings': 0})
        
        for order in self.current_batch:
            if order.payment_status == 'completed':
                partner_id = order.delivery_partner_id
                delivery_fee = order.total_amount * 0.1  # 10% delivery fee
                
                partner_batch_stats[partner_id]['deliveries'] += 1
                partner_batch_stats[partner_id]['earnings'] += delivery_fee
                
                # Update global state
                self.global_state['delivery_partner_stats'][partner_id]['deliveries'] += 1
                self.global_state['delivery_partner_stats'][partner_id]['total_earnings'] += delivery_fee
        
        # Alert for high-performing partners
        for partner_id, stats in partner_batch_stats.items():
            if stats['deliveries'] > 20:  # 20+ deliveries in single batch
                print(f"    🚀 Star performer: Partner {partner_id} - {stats['deliveries']} deliveries")
    
    async def location_based_insights(self):
        """
        Location-based analytics for demand forecasting
        Mumbai ke different areas ka demand pattern
        """
        
        location_batch_stats = defaultdict(lambda: {'orders': 0, 'total_amount': 0})
        
        for order in self.current_batch:
            location = order.delivery_location
            location_batch_stats[location]['orders'] += 1
            location_batch_stats[location]['total_amount'] += order.total_amount
        
        # Calculate average order value by location
        for location, stats in location_batch_stats.items():
            if stats['orders'] > 0:
                avg_amount = stats['total_amount'] / stats['orders']
                
                # Update global state
                global_stats = self.global_state['location_stats'][location]
                global_stats['order_count'] += stats['orders']
                # Update running average
                total_orders = global_stats['order_count']
                if total_orders > 0:
                    global_stats['avg_amount'] = (
                        (global_stats['avg_amount'] * (total_orders - stats['orders']) + 
                         stats['total_amount']) / total_orders
                    )
        
        # Find hotspots in current batch
        hotspots = [loc for loc, stats in location_batch_stats.items() if stats['orders'] > 10]
        if hotspots:
            print(f"    🌶️ Demand hotspots: {', '.join(hotspots)}")
    
    async def real_time_recommendations(self):
        """
        Real-time recommendation updates
        Batch processing se recommendation engine update karna
        """
        
        # Popular items in current batch
        item_frequency = defaultdict(int)
        for order in self.current_batch:
            for item in order.items:
                item_frequency[item] += 1
        
        # Find trending items
        trending_items = sorted(item_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if trending_items:
            print(f"    📈 Trending items: {[item[0] for item in trending_items[:3]]}")
    
    def print_final_statistics(self):
        """Print comprehensive processing statistics"""
        
        print(f"\n📊 Final Processing Statistics")
        print("=" * 50)
        print(f"Total Events Processed: {self.total_events_processed:,}")
        print(f"Total Batches: {self.batch_number}")
        print(f"Avg Batch Processing Time: {sum(self.batch_processing_times)/len(self.batch_processing_times):.3f}s")
        print(f"Total Processing Time: {sum(self.batch_processing_times):.2f}s")
        
        # Top restaurants globally
        top_restaurants = sorted(
            self.global_state['restaurant_stats'].items(),
            key=lambda x: x[1]['revenue'],
            reverse=True
        )[:5]
        
        print(f"\n🏆 Top Restaurants (Global):")
        for restaurant_id, stats in top_restaurants:
            print(f"  {restaurant_id}: {stats['orders']} orders, ₹{stats['revenue']:.0f} revenue")
        
        # Top delivery partners
        top_partners = sorted(
            self.global_state['delivery_partner_stats'].items(),
            key=lambda x: x[1]['deliveries'],
            reverse=True
        )[:5]
        
        print(f"\n🚴 Top Delivery Partners:")
        for partner_id, stats in top_partners:
            print(f"  {partner_id}: {stats['deliveries']} deliveries, ₹{stats['total_earnings']:.0f} earnings")

# Generate sample Zomato order data
def generate_zomato_orders(count: int) -> List[ZomatoOrderEvent]:
    """Generate realistic Zomato order events"""
    
    import random
    
    restaurants = ['Maharaja Restaurant', 'South Indian Express', 'Pizza Corner', 
                  'Burger Junction', 'Chinese Palace', 'Desi Dhaba']
    locations = ['Bandra West', 'Andheri East', 'Lower Parel', 'Powai', 'Goregaon', 'Malad']
    food_items = ['biryani', 'pizza', 'burger', 'dosa', 'noodles', 'dal_rice', 'sandwich']
    payment_statuses = ['completed', 'pending', 'failed']
    
    orders = []
    base_time = time.time()
    
    for i in range(count):
        # Random number of items per order
        num_items = random.randint(1, 4)
        items = random.sample(food_items, num_items)
        
        order = ZomatoOrderEvent(
            order_id=f"ZOM{i+1:06d}",
            restaurant_id=random.choice(restaurants),
            customer_id=f"CUST{random.randint(1, count//20):04d}",
            items=items,
            total_amount=random.uniform(150, 1500),  # ₹150 to ₹1500
            timestamp=base_time + i * random.uniform(0.5, 3),
            delivery_location=random.choice(locations),
            payment_status=random.choices(payment_statuses, weights=[85, 10, 5])[0],
            delivery_partner_id=f"DP{random.randint(1, 100):03d}"
        )
        orders.append(order)
    
    return orders

# Comparison: Flink vs Spark approach
async def compare_processing_approaches():
    """
    Compare Flink (true streaming) vs Spark (micro-batch) approaches
    """
    
    print("🔬 Flink vs Spark Streaming Comparison")
    print("=" * 50)
    
    # Generate test data
    orders = generate_zomato_orders(5000)
    
    print(f"📦 Test data: {len(orders):,} Zomato orders\n")
    
    # Test Spark Structured Streaming (micro-batch)
    print("🔥 Testing Spark Structured Streaming (Micro-batch)")
    spark_processor = SparkStructuredStreamingProcessor(batch_interval=3)
    
    spark_start = time.time()
    await spark_processor.process_zomato_order_stream(orders.copy())
    spark_total_time = time.time() - spark_start
    
    print(f"\n📊 Spark Results:")
    print(f"  Total Time: {spark_total_time:.2f}s")
    print(f"  Throughput: {len(orders)/spark_total_time:.0f} events/sec")
    print(f"  Latency Model: Micro-batch (3s intervals)")
    print(f"  Memory Usage: Batched (efficient for high throughput)")
    
    print(f"\n💡 Mumbai Train Analogy:")
    print(f"  Spark = Mumbai local trains with fixed 3-minute intervals")
    print(f"  Predictable, efficient for bulk passenger transport")
    print(f"  Good for: High throughput analytics, batch ETL jobs")
    
    print(f"\n✅ Comparison complete! Choose based on your latency requirements 🎯")

# Run streaming comparison
if __name__ == "__main__":
    asyncio.run(compare_processing_approaches())
```

### Real-world Production Implementation: Paytm Payment Processing

Paytm ke production system ko samjhte hain - kaise real-time mein millions of payments process karte hain:

```python
# Paytm-style Real-time Payment Processing System
from dataclasses import dataclass
from typing import Dict, List, Optional
import time
import asyncio
import hashlib
import random
from enum import Enum

class FraudRiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PaytmPaymentEvent:
    transaction_id: str
    sender_phone: str
    receiver_phone: str
    amount: float
    payment_method: str  # 'wallet', 'upi', 'card'
    merchant_id: Optional[str]
    location: str
    device_fingerprint: str
    timestamp: float
    transaction_type: str  # 'p2p', 'p2m', 'bill_payment'

class PaytmFraudDetectionEngine:
    """
    Paytm-style real-time fraud detection
    Mumbai Police ki tarah 24x7 vigilant
    """
    
    def __init__(self):
        # User behavior profiles
        self.user_profiles = {}
        
        # Fraud detection rules
        self.fraud_rules = {
            'velocity_limits': {
                'hourly_amount': 50000,  # ₹50K per hour
                'daily_amount': 200000,  # ₹2L per day
                'transaction_count_hourly': 20
            },
            'amount_patterns': {
                'suspicious_round_amounts': [10000, 25000, 50000, 100000],
                'just_below_limits': [9999, 24999, 49999, 99999]
            },
            'device_risk': {
                'new_device_threshold': 48,  # hours
                'max_users_per_device': 3
            }
        }
        
        # ML model simulation (in production, real ML model hogi)
        self.ml_model_weights = {
            'velocity_score': 0.3,
            'device_score': 0.25,
            'amount_score': 0.2,
            'location_score': 0.15,
            'merchant_score': 0.1
        }
    
    async def assess_transaction_risk(self, payment: PaytmPaymentEvent) -> Dict:
        """
        Real-time fraud risk assessment
        <100ms mein complete hona chahiye
        """
        
        start_time = time.time()
        
        # Initialize risk assessment
        risk_assessment = {
            'transaction_id': payment.transaction_id,
            'risk_level': FraudRiskLevel.LOW,
            'risk_score': 0,
            'risk_factors': [],
            'recommended_action': 'approve',
            'processing_time_ms': 0
        }
        
        try:
            # 1. Velocity analysis
            velocity_risk = await self.check_velocity_patterns(payment)
            risk_assessment['risk_score'] += velocity_risk['score']
            risk_assessment['risk_factors'].extend(velocity_risk['factors'])
            
            # 2. Device fingerprint analysis
            device_risk = await self.analyze_device_patterns(payment)
            risk_assessment['risk_score'] += device_risk['score']
            risk_assessment['risk_factors'].extend(device_risk['factors'])
            
            # 3. Amount pattern analysis
            amount_risk = self.analyze_amount_patterns(payment)
            risk_assessment['risk_score'] += amount_risk['score']
            risk_assessment['risk_factors'].extend(amount_risk['factors'])
            
            # 4. Geographic analysis
            geo_risk = await self.analyze_geographic_patterns(payment)
            risk_assessment['risk_score'] += geo_risk['score']
            risk_assessment['risk_factors'].extend(geo_risk['factors'])
            
            # 5. Merchant risk (if P2M transaction)
            if payment.merchant_id:
                merchant_risk = await self.analyze_merchant_risk(payment)
                risk_assessment['risk_score'] += merchant_risk['score']
                risk_assessment['risk_factors'].extend(merchant_risk['factors'])
            
            # 6. ML model prediction
            ml_risk = self.ml_fraud_prediction(payment, risk_assessment)
            risk_assessment['risk_score'] += ml_risk['score']
            risk_assessment['risk_factors'].extend(ml_risk['factors'])
            
            # Final risk determination
            risk_assessment['risk_level'] = self.determine_risk_level(risk_assessment['risk_score'])
            risk_assessment['recommended_action'] = self.determine_action(risk_assessment['risk_level'])
            
        except Exception as e:
            # Error handling - default to manual review
            risk_assessment['risk_level'] = FraudRiskLevel.HIGH
            risk_assessment['recommended_action'] = 'manual_review'
            risk_assessment['risk_factors'].append(f'Error in risk assessment: {str(e)}')
        
        finally:
            risk_assessment['processing_time_ms'] = (time.time() - start_time) * 1000
        
        return risk_assessment
    
    async def check_velocity_patterns(self, payment: PaytmPaymentEvent) -> Dict:
        """
        Velocity pattern analysis - Mumbai local ki crowd control ki tarah
        """
        
        sender_phone = payment.sender_phone
        current_time = payment.timestamp
        
        # Get user profile
        if sender_phone not in self.user_profiles:
            self.user_profiles[sender_phone] = {
                'transactions': [],
                'total_amount_today': 0,
                'first_transaction_time': current_time
            }
        
        user_profile = self.user_profiles[sender_phone]
        
        # Add current transaction
        user_profile['transactions'].append({
            'amount': payment.amount,
            'timestamp': current_time,
            'type': payment.transaction_type
        })
        
        # Clean old transactions (keep only last 24 hours)
        user_profile['transactions'] = [
            txn for txn in user_profile['transactions']
            if current_time - txn['timestamp'] < 86400  # 24 hours
        ]
        
        # Calculate velocity metrics
        last_hour_txns = [
            txn for txn in user_profile['transactions']
            if current_time - txn['timestamp'] < 3600  # 1 hour
        ]
        
        hourly_amount = sum(txn['amount'] for txn in last_hour_txns)
        hourly_count = len(last_hour_txns)
        daily_amount = sum(txn['amount'] for txn in user_profile['transactions'])
        
        # Risk scoring
        score = 0
        factors = []
        
        # Check hourly limits
        if hourly_amount > self.fraud_rules['velocity_limits']['hourly_amount']:
            score += 40
            factors.append(f'Hourly amount limit exceeded: ₹{hourly_amount:,.0f}')
        
        if hourly_count > self.fraud_rules['velocity_limits']['transaction_count_hourly']:
            score += 30
            factors.append(f'Too many transactions per hour: {hourly_count}')
        
        # Check daily limits
        if daily_amount > self.fraud_rules['velocity_limits']['daily_amount']:
            score += 50
            factors.append(f'Daily amount limit exceeded: ₹{daily_amount:,.0f}')
        
        # Pattern analysis
        if len(last_hour_txns) >= 5:
            amounts = [txn['amount'] for txn in last_hour_txns[-5:]]
            if all(amt == amounts[0] for amt in amounts):
                score += 25
                factors.append('Repeated identical amounts')
        
        return {'score': score, 'factors': factors}
    
    async def analyze_device_patterns(self, payment: PaytmPaymentEvent) -> Dict:
        """
        Device fingerprint analysis
        Mumbai mein jaise CCTV se suspicious activity detect karte hain
        """
        
        device_fingerprint = payment.device_fingerprint
        sender_phone = payment.sender_phone
        
        score = 0
        factors = []
        
        # Check if device is new for this user
        user_devices = self.get_user_devices(sender_phone)
        if device_fingerprint not in user_devices:
            score += 20
            factors.append('New device for user')
            
            # Higher risk for large amounts on new device
            if payment.amount > 25000:
                score += 15
                factors.append('Large amount on new device')
        
        # Check device sharing
        device_users = self.get_device_users(device_fingerprint)
        if len(device_users) > self.fraud_rules['device_risk']['max_users_per_device']:
            score += 30
            factors.append(f'Device shared by {len(device_users)} users')
        
        # Check for device manipulation indicators
        if self.is_device_fingerprint_suspicious(device_fingerprint):
            score += 35
            factors.append('Suspicious device fingerprint')
        
        return {'score': score, 'factors': factors}
    
    def analyze_amount_patterns(self, payment: PaytmPaymentEvent) -> Dict:
        """
        Amount pattern analysis for money laundering detection
        """
        
        amount = payment.amount
        score = 0
        factors = []
        
        # Check for suspicious round amounts
        if amount in self.fraud_rules['amount_patterns']['suspicious_round_amounts']:
            score += 20
            factors.append('Suspicious round amount')
        
        # Check for just-below-limit amounts
        if amount in self.fraud_rules['amount_patterns']['just_below_limits']:
            score += 35
            factors.append('Amount just below reporting threshold')
        
        # Check for structuring (multiple transactions just below limits)
        if 9000 <= amount <= 9999:
            score += 25
            factors.append('Potential structuring attempt')
        
        # Time-based amount analysis
        current_hour = time.localtime(payment.timestamp).tm_hour
        if current_hour < 6 or current_hour > 23:  # Late night/early morning
            if amount > 10000:
                score += 15
                factors.append('Large late-night transaction')
        
        return {'score': score, 'factors': factors}
    
    async def analyze_geographic_patterns(self, payment: PaytmPaymentEvent) -> Dict:
        """
        Geographic pattern analysis - impossible travel detection
        """
        
        sender_phone = payment.sender_phone
        current_location = payment.location
        current_time = payment.timestamp
        
        score = 0
        factors = []
        
        # Get last known location
        last_location_data = self.get_last_location(sender_phone)
        
        if last_location_data:
            last_location = last_location_data['location']
            last_time = last_location_data['timestamp']
            
            # Calculate distance and travel time
            distance_km = self.calculate_distance(last_location, current_location)
            time_diff_hours = (current_time - last_time) / 3600
            
            if time_diff_hours > 0:
                speed_kmh = distance_km / time_diff_hours
                
                # Impossible travel (faster than flight)
                if speed_kmh > 900:  # Jet speed
                    score += 50
                    factors.append(f'Impossible travel: {speed_kmh:.0f} km/h')
                
                # Suspicious travel (very fast)
                elif speed_kmh > 100:
                    score += 20
                    factors.append(f'Suspicious travel speed: {speed_kmh:.0f} km/h')
        
        # High-risk location check
        if self.is_high_risk_location(current_location):
            score += 15
            factors.append('Transaction from high-risk location')
        
        return {'score': score, 'factors': factors}
    
    async def analyze_merchant_risk(self, payment: PaytmPaymentEvent) -> Dict:
        """
        Merchant risk analysis for P2M transactions
        """
        
        merchant_id = payment.merchant_id
        score = 0
        factors = []
        
        # Merchant reputation score
        merchant_risk_score = self.get_merchant_risk_score(merchant_id)
        
        if merchant_risk_score > 70:
            score += 30
            factors.append('High-risk merchant')
        elif merchant_risk_score > 50:
            score += 15
            factors.append('Medium-risk merchant')
        
        # New merchant check
        if self.is_new_merchant(merchant_id):
            score += 10
            factors.append('New merchant')
        
        # Merchant category risk
        category_risk = self.get_merchant_category_risk(merchant_id)
        score += category_risk['score']
        factors.extend(category_risk['factors'])
        
        return {'score': score, 'factors': factors}
    
    def ml_fraud_prediction(self, payment: PaytmPaymentEvent, risk_assessment: Dict) -> Dict:
        """
        ML model prediction simulation
        Real production mein trained ML model use hogi
        """
        
        # Feature extraction
        features = {
            'amount_log': math.log(max(payment.amount, 1)),
            'is_weekend': time.localtime(payment.timestamp).tm_wday >= 5,
            'hour_of_day': time.localtime(payment.timestamp).tm_hour,
            'transaction_type_encoded': hash(payment.transaction_type) % 100,
            'payment_method_encoded': hash(payment.payment_method) % 100,
            'current_risk_score': risk_assessment['risk_score']
        }
        
        # Simplified ML prediction (real model would be much more complex)
        ml_score = 0
        for feature, value in features.items():
            ml_score += abs(hash(f"{feature}_{value}") % 100) / 100
        
        ml_score = min(ml_score * 20, 30)  # Scale to 0-30 range
        
        factors = []
        if ml_score > 20:
            factors.append(f'High ML fraud probability: {ml_score/30:.2f}')
        
        return {'score': ml_score, 'factors': factors}
    
    def determine_risk_level(self, total_score: float) -> FraudRiskLevel:
        """Determine overall risk level based on total score"""
        
        if total_score >= 80:
            return FraudRiskLevel.CRITICAL
        elif total_score >= 60:
            return FraudRiskLevel.HIGH
        elif total_score >= 40:
            return FraudRiskLevel.MEDIUM
        else:
            return FraudRiskLevel.LOW
    
    def determine_action(self, risk_level: FraudRiskLevel) -> str:
        """Determine recommended action based on risk level"""
        
        action_map = {
            FraudRiskLevel.LOW: 'approve',
            FraudRiskLevel.MEDIUM: 'additional_verification',
            FraudRiskLevel.HIGH: 'manual_review',
            FraudRiskLevel.CRITICAL: 'block'
        }
        
        return action_map[risk_level]
    
    # Helper methods (simplified implementations)
    def get_user_devices(self, phone: str) -> List[str]:
        """Get devices associated with user"""
        return ['device1', 'device2']  # Simplified
    
    def get_device_users(self, device: str) -> List[str]:
        """Get users associated with device"""
        return ['user1']  # Simplified
    
    def is_device_fingerprint_suspicious(self, fingerprint: str) -> bool:
        """Check if device fingerprint is suspicious"""
        return len(fingerprint) < 10  # Simplified check
    
    def get_last_location(self, phone: str) -> Optional[Dict]:
        """Get last known location for user"""
        return {'location': 'Mumbai', 'timestamp': time.time() - 3600}  # Simplified
    
    def calculate_distance(self, loc1: str, loc2: str) -> float:
        """Calculate distance between locations"""
        if loc1 == loc2:
            return 0
        return random.uniform(10, 500)  # Simplified
    
    def is_high_risk_location(self, location: str) -> bool:
        """Check if location is high-risk"""
        high_risk_locations = ['Border Area', 'Disputed Territory']
        return location in high_risk_locations
    
    def get_merchant_risk_score(self, merchant_id: str) -> int:
        """Get merchant risk score"""
        return hash(merchant_id) % 100  # Simplified
    
    def is_new_merchant(self, merchant_id: str) -> bool:
        """Check if merchant is new"""
        return 'NEW' in merchant_id  # Simplified
    
    def get_merchant_category_risk(self, merchant_id: str) -> Dict:
        """Get merchant category risk"""
        return {'score': 5, 'factors': []}  # Simplified

class PaytmStreamProcessor:
    """
    Main Paytm stream processing engine
    Mumbai local train ki efficiency se payments process karta hai
    """
    
    def __init__(self):
        self.fraud_engine = PaytmFraudDetectionEngine()
        self.processed_count = 0
        self.blocked_count = 0
        self.manual_review_count = 0
        self.approved_count = 0
        
        # Performance metrics
        self.processing_times = []
        
    async def process_payment_stream(self, payments: List[PaytmPaymentEvent]):
        """Process stream of payment events"""
        
        print("💰 Starting Paytm Payment Stream Processing")
        print("🚆 Mumbai Local efficiency ke saath fraud detection!")
        print("=" * 60)
        
        tasks = []
        
        # Process payments concurrently (like multiple train lines)
        for payment in payments:
            task = self.process_single_payment(payment)
            tasks.append(task)
            
            # Process in batches to avoid overwhelming the system
            if len(tasks) >= 100:
                await asyncio.gather(*tasks)
                tasks = []
        
        # Process remaining payments
        if tasks:
            await asyncio.gather(*tasks)
        
        # Print final statistics
        self.print_processing_statistics()
    
    async def process_single_payment(self, payment: PaytmPaymentEvent):
        """Process single payment with fraud detection"""
        
        start_time = time.time()
        
        try:
            # Risk assessment
            risk_assessment = await self.fraud_engine.assess_transaction_risk(payment)
            
            # Take action based on risk level
            if risk_assessment['recommended_action'] == 'approve':
                await self.approve_payment(payment)
                self.approved_count += 1
            
            elif risk_assessment['recommended_action'] == 'block':
                await self.block_payment(payment, risk_assessment)
                self.blocked_count += 1
            
            elif risk_assessment['recommended_action'] == 'manual_review':
                await self.queue_manual_review(payment, risk_assessment)
                self.manual_review_count += 1
            
            elif risk_assessment['recommended_action'] == 'additional_verification':
                await self.request_additional_verification(payment)
                self.manual_review_count += 1
            
            self.processed_count += 1
            
            # Track processing time
            processing_time = (time.time() - start_time) * 1000
            self.processing_times.append(processing_time)
            
            # Log high-risk transactions
            if risk_assessment['risk_level'] in [FraudRiskLevel.HIGH, FraudRiskLevel.CRITICAL]:
                print(f"⚠️ High-risk transaction: {payment.transaction_id} - {risk_assessment['risk_level'].value}")
        
        except Exception as e:
            print(f"❌ Error processing payment {payment.transaction_id}: {str(e)}")
    
    async def approve_payment(self, payment: PaytmPaymentEvent):
        """Approve payment and process"""
        # In production: debit sender, credit receiver, update balances
        pass
    
    async def block_payment(self, payment: PaytmPaymentEvent, risk_assessment: Dict):
        """Block suspicious payment"""
        # In production: block transaction, notify user, log for investigation
        pass
    
    async def queue_manual_review(self, payment: PaytmPaymentEvent, risk_assessment: Dict):
        """Queue payment for manual review"""
        # In production: add to review queue, notify fraud team
        pass
    
    async def request_additional_verification(self, payment: PaytmPaymentEvent):
        """Request additional verification from user"""
        # In production: send OTP, request PIN, biometric verification
        pass
    
    def print_processing_statistics(self):
        """Print comprehensive processing statistics"""
        
        print(f"\n📊 Paytm Payment Processing Results")
        print("=" * 50)
        print(f"Total Payments Processed: {self.processed_count:,}")
        print(f"✅ Approved: {self.approved_count:,} ({self.approved_count/self.processed_count*100:.1f}%)")
        print(f"🔍 Manual Review: {self.manual_review_count:,} ({self.manual_review_count/self.processed_count*100:.1f}%)")
        print(f"🚫 Blocked: {self.blocked_count:,} ({self.blocked_count/self.processed_count*100:.1f}%)")
        
        if self.processing_times:
            avg_processing_time = sum(self.processing_times) / len(self.processing_times)
            p95_processing_time = sorted(self.processing_times)[int(len(self.processing_times) * 0.95)]
            
            print(f"\n⏱️ Performance Metrics:")
            print(f"Average Processing Time: {avg_processing_time:.2f}ms")
            print(f"95th Percentile Time: {p95_processing_time:.2f}ms")
            print(f"Throughput: {len(self.processing_times)/(sum(self.processing_times)/1000):.0f} payments/second")
        
        print(f"\n🎯 Fraud Detection Effectiveness:")
        fraud_detection_rate = (self.blocked_count + self.manual_review_count) / self.processed_count * 100
        print(f"Fraud Detection Rate: {fraud_detection_rate:.1f}%")
        print(f"False Positive Target: <1% (Industry Standard)")

# Generate sample Paytm payment events
def generate_paytm_payments(count: int) -> List[PaytmPaymentEvent]:
    """Generate realistic Paytm payment events"""
    
    import random
    import math
    
    payment_methods = ['wallet', 'upi', 'card']
    transaction_types = ['p2p', 'p2m', 'bill_payment']
    locations = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune']
    
    payments = []
    base_time = time.time()
    
    for i in range(count):
        # Generate realistic amounts with bias toward smaller amounts
        amount = random.lognormvariate(math.log(500), 1.5)  # Log-normal distribution
        amount = min(amount, 100000)  # Cap at ₹1L
        
        payment = PaytmPaymentEvent(
            transaction_id=f"PTM{i+1:08d}",
            sender_phone=f"+91{random.randint(7000000000, 9999999999)}",
            receiver_phone=f"+91{random.randint(7000000000, 9999999999)}",
            amount=round(amount, 2),
            payment_method=random.choice(payment_methods),
            merchant_id=f"MERCHANT{random.randint(1, 1000):04d}" if random.random() < 0.3 else None,
            location=random.choice(locations),
            device_fingerprint=f"device_{hash(str(i + random.randint(1, 100))) % 10000:04d}",
            timestamp=base_time + i * random.uniform(0.1, 5),
            transaction_type=random.choice(transaction_types)
        )
        payments.append(payment)
    
    return payments

# Run Paytm fraud detection simulation
async def run_paytm_simulation():
    """Run complete Paytm payment processing simulation"""
    
    print("💰 Paytm Real-time Payment Processing & Fraud Detection")
    print("🇮🇳 Processing payments at Indian scale!")
    print("=" * 60)
    
    # Generate sample payments
    payments = generate_paytm_payments(5000)  # 5K payments
    print(f"💳 Generated {len(payments):,} payment events")
    
    # Process with Paytm-style fraud detection
    processor = PaytmStreamProcessor()
    
    start_time = time.time()
    await processor.process_payment_stream(payments)
    total_time = time.time() - start_time
    
    print(f"\n🎉 Processing completed in {total_time:.2f} seconds")
    print(f"🚀 Overall throughput: {len(payments)/total_time:.0f} payments/second")
    print(f"🛡️ Mumbai local train se bhi fast aur safe! 💪")

if __name__ == "__main__":
    import math
    asyncio.run(run_paytm_simulation())
```

### Part 1 Summary aur Mumbai Ki Seekh

Dosto, Part 1 mein humne dekha ki stream processing kaise Mumbai local trains ki tarah kaam karta hai:

**Key Learnings:**

1. **Real-time Processing Importance**: UPI payments, IPL streaming, Flipkart orders - sab real-time processing chahiye

2. **Windowing Concepts**: Time windows Mumbai local ke time tables ki tarah important hain

3. **Event Time vs Processing Time**: Scheduled vs actual arrival time - both matter

4. **Flink vs Spark**: True streaming vs micro-batch - dono ke apne benefits

5. **Production Scale Examples**: Hotstar 300M viewers, Paytm millions payments - real Indian scale!

**Mumbai Ki Seekh:**
- Stream processing Mumbai local ki tarah continuous aur reliable honi chahiye
- Peak hours handle karna (jaise 9 AM traffic) critical hai
- Fault tolerance railway ki backup plans ki tarah zaroori hai
- Performance monitoring station announcements ki tarah real-time honi chahiye

Part 2 mein hum dekhenge advanced stream processing patterns, Kafka Streams, aur complex event processing. Stay tuned! 🚆✨

---

*Word Count: ~13,500 words*
*Next: Part 2 - Advanced Stream Processing Patterns and Kafka Streams*
#!/usr/bin/env python3
"""
On-Call Rotation Manager - Episode 3: Human Factor in Tech
===========================================================

Mumbai ke local train schedule ki tarah, on-call rotation bhi fair aur predictable hona chahiye.
Har engineer ko equal opportunity milni chahiye rest karne ki, aur festivals/family events
ka respect karna chahiye.

Features:
- Fair rotation algorithm with weighted distribution
- Indian festival calendar integration
- Family emergency handling
- Burnout prevention with mandatory rest periods
- Multi-timezone support for global teams
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json
import hashlib
from collections import defaultdict

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class RotationStatus(Enum):
    AVAILABLE = "available"
    ON_CALL = "on_call"
    UNAVAILABLE = "unavailable"
    RECOVERING = "recovering"

@dataclass
class Engineer:
    """Engineer profile with cultural and personal considerations"""
    id: str
    name: str
    email: str
    timezone: str
    experience_level: int  # 1-5 scale
    max_consecutive_days: int = 7
    preferred_days: List[str] = None  # ["monday", "tuesday"]
    avoided_days: List[str] = None    # ["friday", "saturday"] 
    family_obligations: List[str] = None  # ["school_pickup", "elderly_care"]
    
    def __post_init__(self):
        if self.preferred_days is None:
            self.preferred_days = []
        if self.avoided_days is None:
            self.avoided_days = []
        if self.family_obligations is None:
            self.family_obligations = []

@dataclass
class OnCallShift:
    """On-call shift with Indian context considerations"""
    start_time: datetime
    end_time: datetime
    engineer: Engineer
    priority_level: Priority
    incidents_handled: int = 0
    stress_score: float = 0.0
    festival_conflict: bool = False

class IndianFestivalCalendar:
    """Indian festival calendar for respectful scheduling"""
    
    def __init__(self):
        # 2024-2025 major festivals (sample data)
        self.festivals = {
            "2024-03-08": "Holi",
            "2024-03-25": "Ram Navami", 
            "2024-04-11": "Eid ul-Fitr",
            "2024-04-17": "Mahavir Jayanti",
            "2024-05-01": "Labor Day",
            "2024-05-23": "Buddha Purnima",
            "2024-06-17": "Eid al-Adha",
            "2024-08-15": "Independence Day",
            "2024-08-26": "Janmashtami",
            "2024-09-07": "Ganesh Chaturthi",
            "2024-10-02": "Gandhi Jayanti",
            "2024-10-12": "Dussehra",
            "2024-11-01": "Diwali",
            "2024-11-15": "Guru Nanak Jayanti",
            "2024-12-25": "Christmas"
        }
        
    def is_festival(self, date: datetime) -> Tuple[bool, Optional[str]]:
        """Check if date is a festival"""
        date_str = date.strftime("%Y-%m-%d")
        if date_str in self.festivals:
            return True, self.festivals[date_str]
        return False, None
    
    def get_festival_impact(self, date: datetime) -> float:
        """Calculate festival impact on availability (0-1 scale)"""
        is_fest, festival_name = self.is_festival(date)
        if not is_fest:
            return 0.0
            
        # Major festivals have higher impact
        major_festivals = ["Diwali", "Holi", "Eid ul-Fitr", "Christmas", "Dussehra"]
        if festival_name in major_festivals:
            return 0.8  # High impact
        return 0.4  # Medium impact

class BurnoutCalculator:
    """Mumbai traffic ki tarah, burnout bhi predict kar sakte hain pattern dekh kar"""
    
    def __init__(self):
        self.stress_weights = {
            Priority.LOW: 1.0,
            Priority.MEDIUM: 2.5,
            Priority.HIGH: 4.0,
            Priority.CRITICAL: 6.0
        }
    
    def calculate_stress_score(self, shifts: List[OnCallShift]) -> float:
        """Calculate cumulative stress score for an engineer"""
        total_stress = 0.0
        consecutive_days = 0
        
        # Sort shifts by start time
        sorted_shifts = sorted(shifts, key=lambda x: x.start_time)
        
        for i, shift in enumerate(sorted_shifts):
            # Base stress from priority
            base_stress = self.stress_weights[shift.priority_level]
            
            # Consecutive day multiplier (Mumbai monsoon effect - gets worse)
            if i > 0:
                prev_shift = sorted_shifts[i-1]
                if (shift.start_time - prev_shift.end_time).days <= 1:
                    consecutive_days += 1
                    base_stress *= (1 + consecutive_days * 0.3)  # 30% increase per consecutive day
                else:
                    consecutive_days = 0
            
            # Weekend/festival penalty
            if shift.start_time.weekday() >= 5:  # Saturday/Sunday
                base_stress *= 1.4
            
            if shift.festival_conflict:
                base_stress *= 1.6  # Festival conflict is stressful
            
            # Incident volume impact
            incident_multiplier = 1 + (shift.incidents_handled * 0.2)
            base_stress *= incident_multiplier
            
            total_stress += base_stress
        
        return total_stress
    
    def needs_recovery(self, engineer: Engineer, recent_shifts: List[OnCallShift]) -> bool:
        """Determine if engineer needs mandatory recovery time"""
        if not recent_shifts:
            return False
            
        stress_score = self.calculate_stress_score(recent_shifts)
        
        # Experience-based thresholds
        thresholds = {
            1: 15.0,  # Junior engineers
            2: 20.0,  # Mid-level
            3: 25.0,  # Senior
            4: 30.0,  # Staff
            5: 35.0   # Principal
        }
        
        threshold = thresholds.get(engineer.experience_level, 20.0)
        return stress_score > threshold

class FairRotationAlgorithm:
    """Fair rotation algorithm - sabka number aayega, bas patience rakho"""
    
    def __init__(self):
        self.rotation_history = defaultdict(list)
        self.engineer_scores = defaultdict(float)
        
    def calculate_fairness_score(self, engineer: Engineer, target_date: datetime) -> float:
        """Calculate how 'fair' it would be to assign this engineer"""
        base_score = 100.0
        
        # Recent assignment penalty
        recent_assignments = len([s for s in self.rotation_history[engineer.id] 
                                if (target_date - s.start_time).days <= 14])
        base_score -= recent_assignments * 15
        
        # Experience bonus (senior engineers can handle more)
        base_score += engineer.experience_level * 5
        
        # Preferred day bonus
        day_name = target_date.strftime("%A").lower()
        if day_name in engineer.preferred_days:
            base_score += 10
        if day_name in engineer.avoided_days:
            base_score -= 20
        
        return max(0, base_score)

class OnCallRotationManager:
    """Main on-call rotation manager - Mumbai local train schedule se inspire"""
    
    def __init__(self):
        self.engineers: List[Engineer] = []
        self.festival_calendar = IndianFestivalCalendar()
        self.burnout_calculator = BurnoutCalculator()
        self.rotation_algorithm = FairRotationAlgorithm()
        self.current_assignments: Dict[str, OnCallShift] = {}
        self.shift_history: List[OnCallShift] = []
        
    def add_engineer(self, engineer: Engineer):
        """Add engineer to rotation pool"""
        self.engineers.append(engineer)
        print(f"✅ Added {engineer.name} to on-call rotation pool")
    
    def remove_engineer(self, engineer_id: str, reason: str = ""):
        """Remove engineer from rotation (promotion, resignation, etc.)"""
        self.engineers = [e for e in self.engineers if e.id != engineer_id]
        if reason:
            print(f"🔄 Removed engineer {engineer_id} from rotation: {reason}")
    
    def mark_unavailable(self, engineer_id: str, start_date: datetime, 
                        end_date: datetime, reason: str = ""):
        """Mark engineer unavailable (vacation, training, family emergency)"""
        # In production, this would update database
        print(f"📅 Engineer {engineer_id} marked unavailable from {start_date} to {end_date}")
        if reason:
            print(f"   Reason: {reason}")
    
    def find_best_engineer(self, target_date: datetime, 
                          priority: Priority) -> Optional[Engineer]:
        """Find best engineer for given date and priority"""
        available_engineers = []
        
        for engineer in self.engineers:
            # Check if engineer needs recovery
            recent_shifts = [s for s in self.shift_history 
                           if s.engineer.id == engineer.id and 
                           (target_date - s.start_time).days <= 7]
            
            if self.burnout_calculator.needs_recovery(engineer, recent_shifts):
                continue
                
            # Check festival conflicts
            is_festival, festival_name = self.festival_calendar.is_festival(target_date)
            festival_impact = self.festival_calendar.get_festival_impact(target_date)
            
            # Calculate fairness score
            fairness_score = self.rotation_algorithm.calculate_fairness_score(
                engineer, target_date)
            
            # Adjust score for festival impact
            if is_festival:
                fairness_score *= (1 - festival_impact)
            
            available_engineers.append((engineer, fairness_score, is_festival))
        
        if not available_engineers:
            return None
            
        # Sort by fairness score (higher is better)
        available_engineers.sort(key=lambda x: x[1], reverse=True)
        best_engineer, score, festival_conflict = available_engineers[0]
        
        print(f"🎯 Selected {best_engineer.name} (score: {score:.1f}) for {target_date}")
        if festival_conflict:
            print(f"   ⚠️  Festival conflict detected, but best available option")
            
        return best_engineer
    
    def create_shift(self, start_time: datetime, end_time: datetime,
                    priority: Priority) -> Optional[OnCallShift]:
        """Create a new on-call shift"""
        engineer = self.find_best_engineer(start_time, priority)
        if not engineer:
            print(f"❌ No available engineer for {start_time}")
            return None
            
        is_festival, festival_name = self.festival_calendar.is_festival(start_time)
        
        shift = OnCallShift(
            start_time=start_time,
            end_time=end_time,
            engineer=engineer,
            priority_level=priority,
            festival_conflict=is_festival
        )
        
        # Update tracking
        self.current_assignments[engineer.id] = shift
        self.shift_history.append(shift)
        self.rotation_algorithm.rotation_history[engineer.id].append(shift)
        
        if is_festival:
            print(f"🪔 Festival shift created: {festival_name}")
            
        return shift
    
    def generate_monthly_schedule(self, year: int, month: int) -> List[OnCallShift]:
        """Generate complete monthly on-call schedule"""
        print(f"\n🗓️  Generating on-call schedule for {month}/{year}")
        
        # Calculate month boundaries
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        schedule = []
        current_date = start_date
        
        while current_date <= end_date:
            # Create 24-hour shifts
            shift_start = current_date.replace(hour=0, minute=0, second=0)
            shift_end = shift_start + timedelta(hours=24)
            
            # Determine priority based on day (weekends are higher priority)
            if current_date.weekday() >= 5:  # Weekend
                priority = Priority.HIGH
            else:
                priority = Priority.MEDIUM
            
            shift = self.create_shift(shift_start, shift_end, priority)
            if shift:
                schedule.append(shift)
            
            current_date += timedelta(days=1)
        
        self.print_schedule_summary(schedule)
        return schedule
    
    def print_schedule_summary(self, schedule: List[OnCallShift]):
        """Print schedule summary with fairness analysis"""
        print(f"\n📊 Schedule Summary:")
        print(f"   Total shifts: {len(schedule)}")
        
        # Engineer distribution
        engineer_counts = defaultdict(int)
        festival_shifts = 0
        
        for shift in schedule:
            engineer_counts[shift.engineer.name] += 1
            if shift.festival_conflict:
                festival_shifts += 1
        
        print(f"   Festival conflicts: {festival_shifts}")
        print(f"\n👥 Engineer Distribution:")
        for name, count in sorted(engineer_counts.items()):
            print(f"   {name}: {count} shifts")
        
        # Fairness calculation
        if engineer_counts:
            avg_shifts = sum(engineer_counts.values()) / len(engineer_counts)
            max_deviation = max(abs(count - avg_shifts) for count in engineer_counts.values())
            fairness_score = max(0, 100 - (max_deviation / avg_shifts * 100))
            print(f"\n⚖️  Fairness Score: {fairness_score:.1f}% (100% is perfect)")
    
    def handle_incident(self, engineer_id: str, severity: Priority, 
                       resolution_time_hours: float):
        """Record incident handling for stress calculation"""
        if engineer_id in self.current_assignments:
            shift = self.current_assignments[engineer_id]
            shift.incidents_handled += 1
            
            # Calculate stress impact
            stress_impact = {
                Priority.LOW: 0.5,
                Priority.MEDIUM: 1.5,
                Priority.HIGH: 3.0,
                Priority.CRITICAL: 5.0
            }
            
            shift.stress_score += stress_impact[severity] * (resolution_time_hours / 2)
            print(f"🚨 Incident handled by {shift.engineer.name}")
            print(f"   Severity: {severity.name}, Duration: {resolution_time_hours}h")
            print(f"   Updated stress score: {shift.stress_score:.1f}")
    
    def get_team_health_report(self) -> Dict:
        """Generate team health report"""
        if not self.engineers:
            return {"error": "No engineers in rotation pool"}
        
        total_stress = 0
        recovery_needed = 0
        recent_shifts = defaultdict(list)
        
        # Collect recent shift data (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        for shift in self.shift_history:
            if shift.start_time >= cutoff_date:
                recent_shifts[shift.engineer.id].append(shift)
        
        for engineer in self.engineers:
            eng_shifts = recent_shifts[engineer.id]
            stress = self.burnout_calculator.calculate_stress_score(eng_shifts)
            total_stress += stress
            
            if self.burnout_calculator.needs_recovery(engineer, eng_shifts):
                recovery_needed += 1
        
        avg_stress = total_stress / len(self.engineers) if self.engineers else 0
        
        return {
            "total_engineers": len(self.engineers),
            "engineers_needing_recovery": recovery_needed,
            "average_stress_score": round(avg_stress, 2),
            "team_health_status": "GOOD" if recovery_needed == 0 else "NEEDS_ATTENTION",
            "recommendation": self._get_health_recommendation(recovery_needed, avg_stress)
        }
    
    def _get_health_recommendation(self, recovery_needed: int, avg_stress: float) -> str:
        """Get team health recommendation"""
        if recovery_needed > 0:
            return f"{recovery_needed} engineers need mandatory rest. Consider hiring contractors."
        elif avg_stress > 25:
            return "Team stress is high. Review incident patterns and automation opportunities."
        elif avg_stress > 15:
            return "Team stress is moderate. Monitor closely and plan stress-reduction activities."
        else:
            return "Team health is good. Current rotation is sustainable."

def demo_rotation_manager():
    """Demo the on-call rotation manager"""
    print("🚀 On-Call Rotation Manager Demo")
    print("=" * 50)
    
    # Initialize manager
    manager = OnCallRotationManager()
    
    # Add sample engineers (Indian IT company scenario)
    engineers = [
        Engineer("ENG001", "Rajesh Kumar", "rajesh@company.com", "Asia/Kolkata", 4,
                preferred_days=["tuesday", "wednesday"], 
                family_obligations=["school_pickup"]),
        Engineer("ENG002", "Priya Sharma", "priya@company.com", "Asia/Kolkata", 3,
                avoided_days=["friday"], 
                family_obligations=["elderly_care"]),
        Engineer("ENG003", "Amit Singh", "amit@company.com", "Asia/Kolkata", 2,
                preferred_days=["monday", "thursday"]),
        Engineer("ENG004", "Sneha Patel", "sneha@company.com", "Asia/Kolkata", 5,
                max_consecutive_days=5),
        Engineer("ENG005", "Vikram Reddy", "vikram@company.com", "Asia/Kolkata", 3,
                avoided_days=["saturday", "sunday"],
                family_obligations=["weekend_family_time"])
    ]
    
    for engineer in engineers:
        manager.add_engineer(engineer)
    
    # Generate schedule for March 2024 (includes Holi)
    schedule = manager.generate_monthly_schedule(2024, 3)
    
    # Simulate some incidents
    print(f"\n🚨 Simulating incidents...")
    if schedule:
        # High severity incident during Holi
        manager.handle_incident("ENG001", Priority.CRITICAL, 4.5)
        
        # Regular incidents
        manager.handle_incident("ENG002", Priority.MEDIUM, 2.0)
        manager.handle_incident("ENG003", Priority.HIGH, 3.0)
    
    # Generate team health report
    print(f"\n🏥 Team Health Report")
    health_report = manager.get_team_health_report()
    for key, value in health_report.items():
        print(f"   {key}: {value}")
    
    # Demo cultural considerations
    print(f"\n🪔 Cultural Considerations Demo")
    test_date = datetime(2024, 3, 8)  # Holi
    is_festival, festival_name = manager.festival_calendar.is_festival(test_date)
    impact = manager.festival_calendar.get_festival_impact(test_date)
    print(f"   Date: {test_date.strftime('%Y-%m-%d')}")
    print(f"   Festival: {festival_name if is_festival else 'None'}")
    print(f"   Impact Score: {impact} (0=none, 1=complete conflict)")

if __name__ == "__main__":
    demo_rotation_manager()
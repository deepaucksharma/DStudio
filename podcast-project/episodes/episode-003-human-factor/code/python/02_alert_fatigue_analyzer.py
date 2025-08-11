#!/usr/bin/env python3
"""
Alert Fatigue Analyzer - Episode 3: Human Factor in Tech
========================================================

Mumbai traffic ki tarah alerts bhi jam ho jaate hain. Jitni zyada alerts, utna kam attention.
Ye tool track karta hai alert patterns aur recommend karta hai ki kaise reduce kare fatigue.

Mumbai Traffic Metaphor:
- Green Signal: Low frequency, actionable alerts (like empty roads at 3 AM)
- Yellow Signal: Medium frequency, needs attention (like evening traffic)  
- Red Signal: High frequency, alert fatigue (like peak hour jam at Bandra-Worli)
- Horn Pollution: Noisy, non-actionable alerts (like unnecessary honking)

Features:
- Alert frequency analysis with time-based patterns
- Fatigue score calculation using Mumbai traffic principles
- Noise detection (alerts that don't lead to actions)
- Recommendation engine for alert consolidation
- Cultural context for Indian work patterns
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum
import json
import statistics
from collections import defaultdict, Counter
import re

class AlertSeverity(Enum):
    INFO = "info"           # Bas information ke liye
    WARNING = "warning"     # Dhyan dena zaroori hai  
    ERROR = "error"         # Problem hai, fix karna padega
    CRITICAL = "critical"   # Production down, sabko jagana padega

class AlertStatus(Enum):
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged" 
    RESOLVED = "resolved"
    IGNORED = "ignored"      # Mumbai traffic me horn ki tarah - sun liya, react nahi kiya

class TrafficSignal(Enum):
    GREEN = "green"     # Smooth flow, low alert rate
    YELLOW = "yellow"   # Caution needed, moderate alerts
    RED = "red"         # Jam situation, high alert rate

@dataclass
class Alert:
    """Individual alert with Indian context tracking"""
    id: str
    timestamp: datetime
    severity: AlertSeverity
    source: str                    # Service/component name
    message: str
    status: AlertStatus = AlertStatus.TRIGGERED
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    time_to_acknowledge: Optional[float] = None  # Minutes
    time_to_resolve: Optional[float] = None      # Minutes
    resulted_in_action: bool = False             # Did someone actually do something?
    is_repeat: bool = False                      # Same alert repeated within window
    noise_score: float = 0.0                     # 0=actionable, 1=pure noise
    
    def acknowledge(self, engineer: str):
        """Acknowledge alert - engineer ne dekha"""
        if self.status == AlertStatus.TRIGGERED:
            self.status = AlertStatus.ACKNOWLEDGED
            self.acknowledged_by = engineer
            self.acknowledged_at = datetime.now()
            self.time_to_acknowledge = (self.acknowledged_at - self.timestamp).total_seconds() / 60
    
    def resolve(self, action_taken: bool = False):
        """Resolve alert with action tracking"""
        if self.status in [AlertStatus.TRIGGERED, AlertStatus.ACKNOWLEDGED]:
            self.status = AlertStatus.RESOLVED
            self.resolved_at = datetime.now()
            self.time_to_resolve = (self.resolved_at - self.timestamp).total_seconds() / 60
            self.resulted_in_action = action_taken
    
    def ignore(self):
        """Mark alert as ignored (Mumbai horn syndrome)"""
        self.status = AlertStatus.IGNORED

@dataclass  
class AlertPattern:
    """Pattern detection for similar alerts"""
    pattern_id: str
    message_regex: str
    source_pattern: str
    frequency_per_hour: float
    avg_resolution_time: float
    action_rate: float          # Percentage that result in actual action
    recommendation: str

@dataclass
class EngineerFatigueProfile:
    """Individual engineer's alert fatigue profile"""
    engineer_id: str
    name: str
    total_alerts_received: int = 0
    alerts_acknowledged: int = 0
    alerts_ignored: int = 0
    avg_acknowledgment_time: float = 0.0
    fatigue_score: float = 0.0
    preferred_alert_channels: List[str] = field(default_factory=list)
    work_hours: Tuple[int, int] = (9, 18)  # IST working hours
    weekend_on_call: bool = False

class MumbaiTrafficAnalyzer:
    """Mumbai traffic-style alert flow analysis"""
    
    def __init__(self):
        # Traffic thresholds based on Mumbai patterns
        self.traffic_thresholds = {
            "peak_hours": (8, 11, 17, 21),    # Morning & evening rush
            "off_peak": (11, 17, 21, 8),      # Relatively smooth
            "night": (23, 6),                 # Minimal traffic
            "weekend": "different_pattern"     # Weekends have different flow
        }
    
    def get_traffic_signal(self, alerts_per_hour: float, time_of_day: int, 
                          is_weekend: bool = False) -> TrafficSignal:
        """Get traffic signal based on alert rate and time"""
        
        # Weekend adjustment (lighter traffic, different patterns)
        if is_weekend:
            alerts_per_hour *= 0.7
        
        # Peak hours have higher tolerance (expected heavy traffic)
        if time_of_day in [8, 9, 10, 18, 19, 20]:
            green_threshold = 15
            red_threshold = 40
        # Off-peak hours should be smoother
        elif time_of_day in [11, 12, 13, 14, 15, 16]:
            green_threshold = 8
            red_threshold = 20
        # Night hours should be very quiet
        else:
            green_threshold = 3
            red_threshold = 10
        
        if alerts_per_hour <= green_threshold:
            return TrafficSignal.GREEN
        elif alerts_per_hour <= red_threshold:
            return TrafficSignal.YELLOW
        else:
            return TrafficSignal.RED
    
    def analyze_flow_patterns(self, alerts: List[Alert]) -> Dict:
        """Analyze alert flow like Mumbai traffic patterns"""
        hourly_counts = defaultdict(list)
        
        for alert in alerts:
            hour = alert.timestamp.hour
            is_weekend = alert.timestamp.weekday() >= 5
            hourly_counts[hour].append(alert)
        
        pattern_analysis = {}
        
        for hour in range(24):
            hour_alerts = hourly_counts[hour]
            if not hour_alerts:
                continue
                
            alerts_per_hour = len(hour_alerts)
            is_weekend = hour_alerts[0].timestamp.weekday() >= 5
            signal = self.get_traffic_signal(alerts_per_hour, hour, is_weekend)
            
            # Calculate quality metrics
            acknowledged = sum(1 for a in hour_alerts if a.status != AlertStatus.IGNORED)
            action_rate = sum(1 for a in hour_alerts if a.resulted_in_action) / len(hour_alerts)
            
            pattern_analysis[f"{hour}:00"] = {
                "signal": signal,
                "alerts_count": alerts_per_hour,
                "acknowledgment_rate": acknowledged / len(hour_alerts),
                "action_rate": action_rate,
                "metaphor": self._get_traffic_metaphor(signal, hour)
            }
        
        return pattern_analysis
    
    def _get_traffic_metaphor(self, signal: TrafficSignal, hour: int) -> str:
        """Get Mumbai traffic metaphor for the situation"""
        if signal == TrafficSignal.GREEN:
            if 2 <= hour <= 5:
                return "Midnight express - khali roads, smooth ride"
            else:
                return "Free flowing traffic at Marine Drive"
                
        elif signal == TrafficSignal.YELLOW:
            if 8 <= hour <= 10:
                return "Office time rush building up at BKC"
            elif 18 <= hour <= 20:
                return "Evening rush starting at Andheri"
            else:
                return "Moderate traffic, manageable delays"
                
        else:  # RED
            if 8 <= hour <= 10:
                return "Peak hour jam at Bandra-Worli Sea Link"
            elif 18 <= hour <= 20:
                return "Evening nightmare at Western Express Highway"
            else:
                return "Unexpected jam - check for accident or breakdown"

class NoiseDetector:
    """Detect noisy alerts that don't add value (like unnecessary honking)"""
    
    def __init__(self):
        self.noise_patterns = [
            # Common noise patterns in Indian IT
            r".*connection timeout.*retry.*",           # Network flakiness
            r".*disk space.*[0-9]+%.*",                # Gradual disk fill
            r".*memory usage.*normal.*",               # Memory fluctuations
            r".*ssl certificate.*30 days.*",          # Certificate expiry warnings
            r".*backup.*completed.*warnings.*",        # Backup minor issues
            r".*load balancer.*health check.*",        # LB temporary failures
        ]
        
        self.signal_patterns = [
            # Real issues that need attention
            r".*production.*down.*",                   # Production issues
            r".*payment.*failed.*",                   # Payment gateway issues
            r".*database.*connection.*failed.*",       # DB connectivity
            r".*api.*response time.*exceeded.*",       # Performance degradation
            r".*security.*breach.*detected.*",         # Security issues
        ]
    
    def calculate_noise_score(self, alert: Alert) -> float:
        """Calculate noise score (0=signal, 1=noise)"""
        message = alert.message.lower()
        
        # Check for clear signal patterns first
        for pattern in self.signal_patterns:
            if re.search(pattern, message):
                return 0.1  # Definitely signal
        
        # Check for noise patterns
        noise_indicators = 0
        for pattern in self.noise_patterns:
            if re.search(pattern, message):
                noise_indicators += 1
        
        base_noise = min(noise_indicators * 0.3, 0.9)
        
        # Additional noise indicators
        if alert.severity == AlertSeverity.INFO:
            base_noise += 0.2
        
        if not alert.resulted_in_action:
            base_noise += 0.3
        
        if alert.status == AlertStatus.IGNORED:
            base_noise += 0.4
        
        # Repeat alert penalty
        if alert.is_repeat:
            base_noise += 0.2
        
        return min(base_noise, 1.0)

class AlertFatigueAnalyzer:
    """Main alert fatigue analyzer - Mumbai traffic engineer ki tarah"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.engineers: Dict[str, EngineerFatigueProfile] = {}
        self.patterns: List[AlertPattern] = []
        self.traffic_analyzer = MumbaiTrafficAnalyzer()
        self.noise_detector = NoiseDetector()
        
        # Analysis windows
        self.analysis_windows = {
            "last_hour": timedelta(hours=1),
            "last_day": timedelta(days=1),
            "last_week": timedelta(weeks=1),
            "last_month": timedelta(days=30)
        }
    
    def add_alert(self, alert: Alert):
        """Add new alert to analysis"""
        # Check for repeats
        alert.is_repeat = self._is_repeat_alert(alert)
        
        # Calculate noise score
        alert.noise_score = self.noise_detector.calculate_noise_score(alert)
        
        self.alerts.append(alert)
        
        print(f"📨 Alert added: {alert.severity.value} from {alert.source}")
        if alert.is_repeat:
            print(f"   🔄 Repeat alert detected")
        if alert.noise_score > 0.7:
            print(f"   📢 High noise score: {alert.noise_score:.2f}")
    
    def _is_repeat_alert(self, new_alert: Alert, window_minutes: int = 15) -> bool:
        """Check if this is a repeat of recent alert"""
        cutoff = new_alert.timestamp - timedelta(minutes=window_minutes)
        
        for existing_alert in reversed(self.alerts):
            if existing_alert.timestamp < cutoff:
                break
                
            if (existing_alert.source == new_alert.source and 
                existing_alert.severity == new_alert.severity and
                self._messages_similar(existing_alert.message, new_alert.message)):
                return True
        
        return False
    
    def _messages_similar(self, msg1: str, msg2: str, threshold: float = 0.8) -> bool:
        """Check if two alert messages are similar"""
        # Simple similarity check - in production use more sophisticated NLP
        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())
        
        if not words1 or not words2:
            return False
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold
    
    def register_engineer(self, profile: EngineerFatigueProfile):
        """Register engineer for fatigue tracking"""
        self.engineers[profile.engineer_id] = profile
        print(f"👨‍💻 Registered engineer: {profile.name}")
    
    def calculate_team_fatigue_score(self) -> float:
        """Calculate overall team fatigue score (Mumbai traffic index style)"""
        if not self.alerts:
            return 0.0
            
        recent_window = datetime.now() - self.analysis_windows["last_day"]
        recent_alerts = [a for a in self.alerts if a.timestamp >= recent_window]
        
        if not recent_alerts:
            return 0.0
        
        # Base metrics
        total_alerts = len(recent_alerts)
        ignored_rate = sum(1 for a in recent_alerts if a.status == AlertStatus.IGNORED) / total_alerts
        noise_rate = sum(a.noise_score for a in recent_alerts) / total_alerts
        repeat_rate = sum(1 for a in recent_alerts if a.is_repeat) / total_alerts
        
        # Time-based fatigue (peak hour penalty)
        peak_hour_alerts = sum(1 for a in recent_alerts 
                              if a.timestamp.hour in [8, 9, 10, 18, 19, 20])
        peak_penalty = (peak_hour_alerts / total_alerts) * 0.3
        
        # Calculate fatigue components
        volume_fatigue = min(total_alerts / 100, 1.0)      # Volume impact
        quality_fatigue = (ignored_rate + noise_rate) / 2   # Quality impact  
        pattern_fatigue = repeat_rate                       # Pattern impact
        timing_fatigue = peak_penalty                       # Timing impact
        
        # Combined score (0-100 scale, Mumbai traffic style)
        fatigue_score = (volume_fatigue + quality_fatigue + pattern_fatigue + timing_fatigue) * 25
        
        return min(fatigue_score, 100.0)
    
    def get_traffic_report(self) -> Dict:
        """Get Mumbai traffic style alert flow report"""
        if not self.alerts:
            return {"error": "No alerts to analyze"}
            
        recent_alerts = [a for a in self.alerts 
                        if a.timestamp >= datetime.now() - self.analysis_windows["last_day"]]
        
        if not recent_alerts:
            return {"error": "No recent alerts"}
        
        flow_analysis = self.traffic_analyzer.analyze_flow_patterns(recent_alerts)
        fatigue_score = self.calculate_team_fatigue_score()
        
        # Traffic signal summary
        signals = [data["signal"] for data in flow_analysis.values()]
        signal_count = Counter(signals)
        
        overall_signal = TrafficSignal.GREEN
        if signal_count[TrafficSignal.RED] > 0:
            overall_signal = TrafficSignal.RED
        elif signal_count[TrafficSignal.YELLOW] > 0:
            overall_signal = TrafficSignal.YELLOW
        
        return {
            "overall_signal": overall_signal.value,
            "fatigue_score": round(fatigue_score, 1),
            "total_alerts_24h": len(recent_alerts),
            "hourly_patterns": flow_analysis,
            "recommendations": self._generate_traffic_recommendations(
                fatigue_score, overall_signal, recent_alerts),
            "mumbai_metaphor": self._get_overall_metaphor(overall_signal, fatigue_score)
        }
    
    def _generate_traffic_recommendations(self, fatigue_score: float, 
                                        signal: TrafficSignal, 
                                        alerts: List[Alert]) -> List[str]:
        """Generate recommendations based on traffic analysis"""
        recommendations = []
        
        if signal == TrafficSignal.RED:
            recommendations.append("🚨 Alert jam detected! Consider emergency alert consolidation")
            recommendations.append("📱 Implement alert throttling during peak hours")
            
        if fatigue_score > 70:
            recommendations.append("😴 High fatigue detected - review alert thresholds")
            recommendations.append("🔇 Enable do-not-disturb during non-critical hours")
            
        # Noise analysis
        noisy_alerts = [a for a in alerts if a.noise_score > 0.7]
        if len(noisy_alerts) > len(alerts) * 0.3:
            recommendations.append("📢 Too many noisy alerts - review alert rules")
            recommendations.append("🎯 Focus on actionable alerts only")
            
        # Repeat analysis  
        repeat_alerts = [a for a in alerts if a.is_repeat]
        if len(repeat_alerts) > len(alerts) * 0.2:
            recommendations.append("🔄 High repeat rate - implement alert deduplication")
            recommendations.append("⏰ Increase alert grouping window")
            
        # Time-based recommendations
        peak_alerts = [a for a in alerts if a.timestamp.hour in [8, 9, 10, 18, 19, 20]]
        if len(peak_alerts) > len(alerts) * 0.4:
            recommendations.append("⏰ Many peak-hour alerts - consider off-peak maintenance")
            recommendations.append("🎯 Prioritize critical alerts during rush hours")
        
        if not recommendations:
            recommendations.append("✅ Alert flow looks healthy - current setup working well")
        
        return recommendations
    
    def _get_overall_metaphor(self, signal: TrafficSignal, fatigue_score: float) -> str:
        """Get overall Mumbai traffic metaphor"""
        if signal == TrafficSignal.GREEN and fatigue_score < 30:
            return "🌊 Smooth sailing like Marine Drive at midnight - engineers are happy!"
            
        elif signal == TrafficSignal.YELLOW or 30 <= fatigue_score < 60:
            return "🚦 Moderate traffic like BKC during lunch time - manageable but watch closely"
            
        elif signal == TrafficSignal.RED or fatigue_score >= 60:
            return "🔴 Complete jam like Bandra-Worli during monsoon - immediate action needed!"
            
        else:
            return "🎯 Mixed conditions - some areas smooth, others need attention"
    
    def identify_alert_patterns(self) -> List[AlertPattern]:
        """Identify recurring alert patterns for consolidation"""
        if not self.alerts:
            return []
            
        # Group alerts by source and similarity
        source_groups = defaultdict(list)
        for alert in self.alerts:
            source_groups[alert.source].append(alert)
        
        patterns = []
        for source, source_alerts in source_groups.items():
            # Analyze message patterns
            message_groups = defaultdict(list)
            
            for alert in source_alerts:
                # Simple pattern grouping (in production, use ML)
                pattern_key = self._extract_message_pattern(alert.message)
                message_groups[pattern_key].append(alert)
            
            # Create patterns for groups with multiple alerts
            for pattern_key, pattern_alerts in message_groups.items():
                if len(pattern_alerts) >= 3:  # Minimum threshold
                    pattern = self._create_alert_pattern(
                        source, pattern_key, pattern_alerts)
                    patterns.append(pattern)
        
        self.patterns = patterns
        return patterns
    
    def _extract_message_pattern(self, message: str) -> str:
        """Extract pattern from alert message (simplified)"""
        # Remove numbers and timestamps
        pattern = re.sub(r'\d+', 'X', message)
        pattern = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', 'DATE', pattern)
        pattern = re.sub(r'\b\d{2}:\d{2}:\d{2}\b', 'TIME', pattern)
        
        return pattern.lower()
    
    def _create_alert_pattern(self, source: str, pattern_key: str, 
                            alerts: List[Alert]) -> AlertPattern:
        """Create alert pattern from similar alerts"""
        # Calculate pattern metrics
        total_time = sum((a.resolved_at - a.timestamp).total_seconds() 
                        for a in alerts if a.resolved_at) / 60
        avg_resolution = total_time / len(alerts) if alerts else 0
        
        action_rate = sum(1 for a in alerts if a.resulted_in_action) / len(alerts)
        
        # Calculate frequency
        if len(alerts) > 1:
            time_span = (alerts[-1].timestamp - alerts[0].timestamp).total_seconds() / 3600
            frequency = len(alerts) / time_span if time_span > 0 else 0
        else:
            frequency = 0
        
        # Generate recommendation
        if action_rate < 0.2:
            recommendation = f"Consider increasing threshold - only {action_rate*100:.1f}% result in action"
        elif frequency > 5:
            recommendation = f"High frequency ({frequency:.1f}/hour) - implement grouping"
        else:
            recommendation = "Pattern looks reasonable - monitor for changes"
        
        return AlertPattern(
            pattern_id=f"{source}_{hash(pattern_key)}",
            message_regex=pattern_key,
            source_pattern=source,
            frequency_per_hour=frequency,
            avg_resolution_time=avg_resolution,
            action_rate=action_rate,
            recommendation=recommendation
        )
    
    def generate_consolidation_report(self) -> Dict:
        """Generate alert consolidation recommendations"""
        patterns = self.identify_alert_patterns()
        
        consolidation_opportunities = []
        potential_noise_reduction = 0
        
        for pattern in patterns:
            if pattern.action_rate < 0.3 or pattern.frequency_per_hour > 10:
                consolidation_opportunities.append({
                    "pattern": pattern.source_pattern,
                    "frequency": pattern.frequency_per_hour,
                    "action_rate": pattern.action_rate,
                    "recommendation": pattern.recommendation,
                    "potential_reduction": pattern.frequency_per_hour * 0.7  # Estimated reduction
                })
                potential_noise_reduction += pattern.frequency_per_hour * 0.7
        
        return {
            "total_patterns_analyzed": len(patterns),
            "consolidation_opportunities": len(consolidation_opportunities),
            "potential_alert_reduction_per_hour": round(potential_noise_reduction, 1),
            "opportunities": consolidation_opportunities,
            "estimated_fatigue_improvement": min(potential_noise_reduction * 2, 50)
        }

def demo_alert_fatigue_analyzer():
    """Demo the alert fatigue analyzer"""
    print("🚨 Alert Fatigue Analyzer Demo - Mumbai Traffic Style")
    print("=" * 60)
    
    analyzer = AlertFatigueAnalyzer()
    
    # Register engineers
    engineers = [
        EngineerFatigueProfile("ENG001", "Rajesh Kumar", work_hours=(9, 18)),
        EngineerFatigueProfile("ENG002", "Priya Sharma", work_hours=(10, 19), weekend_on_call=True),
        EngineerFatigueProfile("ENG003", "Amit Singh", work_hours=(8, 17))
    ]
    
    for engineer in engineers:
        analyzer.register_engineer(engineer)
    
    # Simulate alert patterns (Mumbai traffic style)
    base_time = datetime.now().replace(hour=8, minute=0, second=0)  # Start at 8 AM
    
    # Morning rush alerts (8-10 AM)
    print("\n🌅 Simulating morning rush hour alerts...")
    for hour in range(8, 10):
        for minute in range(0, 60, 15):  # Every 15 minutes
            timestamp = base_time.replace(hour=hour, minute=minute)
            
            # High frequency during peak hours
            if hour == 9:  # Peak of rush hour
                # Multiple alerts
                analyzer.add_alert(Alert(
                    id=f"ALERT_{hour}_{minute}_1",
                    timestamp=timestamp,
                    severity=AlertSeverity.WARNING,
                    source="payment-gateway",
                    message=f"Payment timeout rate increased to 15% at {timestamp}"
                ))
                
                # Repeat alert (noise)
                analyzer.add_alert(Alert(
                    id=f"ALERT_{hour}_{minute}_2", 
                    timestamp=timestamp + timedelta(minutes=2),
                    severity=AlertSeverity.WARNING,
                    source="payment-gateway",
                    message=f"Payment timeout rate increased to 16% at {timestamp}"
                ))
            
            # Regular monitoring alerts
            analyzer.add_alert(Alert(
                id=f"ALERT_{hour}_{minute}_3",
                timestamp=timestamp,
                severity=AlertSeverity.INFO,
                source="monitoring",
                message=f"CPU usage at 75% - within normal range"
            ))
    
    # Afternoon calm period (2-5 PM)
    print("🌤️  Simulating calm afternoon period...")
    for hour in range(14, 17):
        timestamp = base_time.replace(hour=hour, minute=0)
        analyzer.add_alert(Alert(
            id=f"ALERT_{hour}_low",
            timestamp=timestamp,
            severity=AlertSeverity.INFO,
            source="backup-system",
            message=f"Daily backup completed successfully with minor warnings"
        ))
    
    # Evening rush alerts (6-8 PM)  
    print("🌆 Simulating evening rush hour alerts...")
    for hour in range(18, 20):
        for minute in range(0, 60, 10):  # Every 10 minutes
            timestamp = base_time.replace(hour=hour, minute=minute)
            
            # Critical alert during peak traffic
            if hour == 19 and minute == 30:
                analyzer.add_alert(Alert(
                    id=f"CRITICAL_{hour}_{minute}",
                    timestamp=timestamp,
                    severity=AlertSeverity.CRITICAL,
                    source="api-gateway",
                    message="API gateway response time exceeded 5 seconds - production impact"
                ))
                
                # Acknowledge and resolve the critical alert
                critical_alert = analyzer.alerts[-1]
                critical_alert.acknowledge("ENG002")
                critical_alert.resolve(action_taken=True)
            
            # Regular alerts
            analyzer.add_alert(Alert(
                id=f"ALERT_{hour}_{minute}",
                timestamp=timestamp,
                severity=AlertSeverity.ERROR,
                source="database",
                message=f"Database connection pool utilization at 85%"
            ))
    
    # Simulate some ignored alerts (alert fatigue effect)
    for alert in analyzer.alerts:
        if alert.severity == AlertSeverity.INFO and "within normal range" in alert.message:
            alert.ignore()  # Engineers start ignoring routine alerts
    
    # Generate traffic report
    print("\n🚦 Alert Traffic Report:")
    traffic_report = analyzer.get_traffic_report()
    
    print(f"Overall Signal: {traffic_report['overall_signal']}")
    print(f"Team Fatigue Score: {traffic_report['fatigue_score']}/100")
    print(f"24h Alert Volume: {traffic_report['total_alerts_24h']}")
    print(f"Mumbai Metaphor: {traffic_report['mumbai_metaphor']}")
    
    print(f"\n📊 Hourly Pattern Analysis:")
    for time_slot, data in traffic_report['hourly_patterns'].items():
        print(f"   {time_slot}: {data['signal'].value} signal - {data['alerts_count']} alerts")
        print(f"            {data['metaphor']}")
    
    print(f"\n💡 Recommendations:")
    for i, recommendation in enumerate(traffic_report['recommendations'], 1):
        print(f"   {i}. {recommendation}")
    
    # Pattern analysis
    print(f"\n🔍 Pattern Analysis:")
    patterns = analyzer.identify_alert_patterns()
    print(f"   Detected {len(patterns)} alert patterns")
    
    for pattern in patterns[:3]:  # Show top 3 patterns
        print(f"   Pattern: {pattern.source_pattern}")
        print(f"   Frequency: {pattern.frequency_per_hour:.1f}/hour")
        print(f"   Action Rate: {pattern.action_rate*100:.1f}%")
        print(f"   Recommendation: {pattern.recommendation}")
        print()
    
    # Consolidation opportunities
    print(f"\n🎯 Alert Consolidation Report:")
    consolidation_report = analyzer.generate_consolidation_report()
    print(f"   Patterns Analyzed: {consolidation_report['total_patterns_analyzed']}")
    print(f"   Consolidation Opportunities: {consolidation_report['consolidation_opportunities']}")
    print(f"   Potential Reduction: {consolidation_report['potential_alert_reduction_per_hour']:.1f} alerts/hour")
    print(f"   Estimated Fatigue Improvement: {consolidation_report['estimated_fatigue_improvement']}%")
    
    if consolidation_report['opportunities']:
        print(f"\n   Top Consolidation Opportunities:")
        for i, opp in enumerate(consolidation_report['opportunities'][:2], 1):
            print(f"   {i}. {opp['pattern']}: {opp['frequency']:.1f}/hour, "
                  f"{opp['action_rate']*100:.1f}% action rate")
            print(f"      {opp['recommendation']}")

if __name__ == "__main__":
    demo_alert_fatigue_analyzer()
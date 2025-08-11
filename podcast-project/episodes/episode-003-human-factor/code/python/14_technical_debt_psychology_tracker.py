#!/usr/bin/env python3
"""
Technical Debt Psychology Tracker - Episode 3: Human Factor in Tech
===================================================================

Technical debt ka psychological impact measure karna. Engineer morale,
business pressure, aur long-term team health ke correlation ko track karta hai.

Features:
- Technical debt accumulation pattern analysis
- Team morale correlation tracking
- Business pressure impact assessment
- Refactoring prioritization based on psychology
- Productivity decline measurement
- Cultural resistance to debt paydown
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import statistics
from collections import defaultdict

class DebtCategory(Enum):
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    ARCHITECTURE = "architecture"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"

class PressureSource(Enum):
    BUSINESS_DEADLINES = "business_deadlines"
    CUSTOMER_REQUESTS = "customer_requests"
    TECHNICAL_LIMITATIONS = "technical_limitations"
    RESOURCE_CONSTRAINTS = "resource_constraints"
    MARKET_COMPETITION = "market_competition"

@dataclass
class TechnicalDebtItem:
    id: str
    title: str
    description: str
    category: DebtCategory
    estimated_effort_hours: int
    impact_score: int  # 1-10 scale
    frustration_level: int  # 1-10 how frustrating it is to work with
    created_date: datetime
    source_pressure: PressureSource
    affected_engineers: List[str]
    business_justification: str
    
    # Psychology tracking
    developer_complaints: int = 0
    workaround_complexity: int = 1  # 1-5 scale
    new_engineer_confusion_rate: float = 0.0  # % of new engineers confused
    debugging_time_multiplier: float = 1.0
    
@dataclass
class Engineer:
    id: str
    name: str
    experience_level: int  # 1-5
    debt_tolerance: float  # 0-1 scale
    current_morale: int  # 1-10 scale
    productivity_score: float  # 0-1 scale
    burnout_risk: float  # 0-1 scale
    
    # Debt interaction history
    debt_items_worked_on: List[str] = field(default_factory=list)
    refactoring_contributions: int = 0
    debt_creation_incidents: int = 0

@dataclass
class MoraleSnapshot:
    timestamp: datetime
    team_average_morale: float
    total_debt_score: float
    debt_category_breakdown: Dict[DebtCategory, float]
    business_pressure_level: int  # 1-10
    recent_debt_additions: int
    recent_debt_paydowns: int

class TechnicalDebtPsychologyTracker:
    def __init__(self):
        self.debt_items: List[TechnicalDebtItem] = []
        self.engineers: Dict[str, Engineer] = {}
        self.morale_history: List[MoraleSnapshot] = []
        self.pressure_events: List[Dict] = []
    
    def add_engineer(self, engineer: Engineer):
        self.engineers[engineer.id] = engineer
        print(f"👤 Added {engineer.name} to debt psychology tracking")
        
    def add_debt_item(self, debt_item: TechnicalDebtItem):
        self.debt_items.append(debt_item)
        
        # Impact on affected engineers' morale
        for eng_id in debt_item.affected_engineers:
            if eng_id in self.engineers:
                engineer = self.engineers[eng_id]
                # Higher frustration items reduce morale more
                morale_impact = -(debt_item.frustration_level * 0.3)
                engineer.current_morale = max(1, engineer.current_morale + morale_impact)
                engineer.debt_items_worked_on.append(debt_item.id)
        
        print(f"📝 Added technical debt: {debt_item.title}")
        print(f"   Frustration Level: {debt_item.frustration_level}/10")
        print(f"   Affected Engineers: {len(debt_item.affected_engineers)}")
    
    def record_business_pressure_event(self, pressure_source: PressureSource, 
                                     intensity: int, description: str):
        """Record business pressure event that may lead to debt"""
        event = {
            "timestamp": datetime.now(),
            "source": pressure_source,
            "intensity": intensity,
            "description": description
        }
        self.pressure_events.append(event)
        
        print(f"📈 Business pressure recorded: {pressure_source.value} (intensity: {intensity}/10)")
    
    def calculate_debt_burden_score(self) -> float:
        """Calculate overall technical debt burden score"""
        if not self.debt_items:
            return 0.0
        
        total_score = 0.0
        for item in self.debt_items:
            # Weight by impact, effort, and frustration
            item_score = (item.impact_score * 0.4 + 
                         item.frustration_level * 0.4 + 
                         min(item.estimated_effort_hours / 10, 10) * 0.2)
            total_score += item_score
        
        # Normalize to 0-100 scale
        return min(total_score / len(self.debt_items) * 10, 100)
    
    def analyze_morale_debt_correlation(self) -> Dict:
        """Analyze correlation between technical debt and team morale"""
        if len(self.morale_history) < 3:
            return {"insufficient_data": True}
        
        # Extract morale and debt scores from history
        morale_scores = [snap.team_average_morale for snap in self.morale_history]
        debt_scores = [snap.total_debt_score for snap in self.morale_history]
        
        # Simple correlation calculation
        correlation = self._calculate_correlation(morale_scores, debt_scores)
        
        # Analyze trends
        recent_morale_trend = self._calculate_trend(morale_scores[-5:])
        recent_debt_trend = self._calculate_trend(debt_scores[-5:])
        
        return {
            "correlation_coefficient": correlation,
            "recent_morale_trend": recent_morale_trend,
            "recent_debt_trend": recent_debt_trend,
            "relationship_strength": abs(correlation),
            "impact_assessment": self._assess_debt_morale_impact(correlation, recent_morale_trend)
        }
    
    def identify_high_frustration_debt(self) -> List[TechnicalDebtItem]:
        """Identify debt items causing highest frustration"""
        # Sort by combined frustration and developer complaints
        frustrating_items = sorted(
            self.debt_items,
            key=lambda item: (item.frustration_level * 0.6 + 
                            item.developer_complaints * 0.4),
            reverse=True
        )
        
        return frustrating_items[:5]  # Top 5 most frustrating
    
    def calculate_productivity_impact(self) -> Dict:
        """Calculate how technical debt impacts team productivity"""
        if not self.engineers:
            return {"no_data": True}
        
        # Current team productivity
        current_productivity = statistics.mean(eng.productivity_score for eng in self.engineers.values())
        
        # Estimate productivity without debt (theoretical)
        debt_burden = self.calculate_debt_burden_score()
        estimated_clean_productivity = current_productivity / (1 - debt_burden / 200)
        
        productivity_loss = estimated_clean_productivity - current_productivity
        
        # Calculate time waste from debugging multipliers
        avg_debug_multiplier = statistics.mean(
            item.debugging_time_multiplier for item in self.debt_items
        ) if self.debt_items else 1.0
        
        time_waste_percentage = ((avg_debug_multiplier - 1.0) * 100)
        
        return {
            "current_team_productivity": current_productivity,
            "estimated_clean_productivity": estimated_clean_productivity,
            "productivity_loss": productivity_loss,
            "productivity_loss_percentage": (productivity_loss / estimated_clean_productivity) * 100,
            "debug_time_waste_percentage": time_waste_percentage,
            "debt_burden_score": debt_burden
        }
    
    def prioritize_debt_by_psychology(self) -> List[Dict]:
        """Prioritize debt paydown based on psychological factors"""
        prioritized = []
        
        for item in self.debt_items:
            # Calculate psychological priority score
            frustration_weight = item.frustration_level * 0.3
            complaint_weight = min(item.developer_complaints, 10) * 0.2
            confusion_weight = item.new_engineer_confusion_rate * 20 * 0.2
            debug_weight = (item.debugging_time_multiplier - 1) * 10 * 0.15
            effort_penalty = item.estimated_effort_hours / 100 * 0.15  # Prefer lower effort
            
            psychology_score = (frustration_weight + complaint_weight + 
                              confusion_weight + debug_weight - effort_penalty)
            
            # Factor in business impact
            business_adjusted_score = psychology_score * (item.impact_score / 10)
            
            prioritized.append({
                "debt_item": item,
                "psychology_score": psychology_score,
                "business_adjusted_score": business_adjusted_score,
                "recommendation_reason": self._get_priority_reason(item)
            })
        
        # Sort by business-adjusted psychology score
        prioritized.sort(key=lambda x: x["business_adjusted_score"], reverse=True)
        
        return prioritized[:10]  # Top 10 priorities
    
    def track_refactoring_resistance(self) -> Dict:
        """Track cultural resistance to technical debt paydown"""
        total_debt_items = len(self.debt_items)
        if total_debt_items == 0:
            return {"no_debt_to_analyze": True}
        
        # Calculate age of debt items
        current_time = datetime.now()
        debt_ages = [(current_time - item.created_date).days for item in self.debt_items]
        avg_debt_age = statistics.mean(debt_ages)
        
        # Calculate refactoring activity
        total_refactoring_contributions = sum(eng.refactoring_contributions 
                                            for eng in self.engineers.values())
        total_debt_creation = sum(eng.debt_creation_incidents 
                                for eng in self.engineers.values())
        
        # Resistance indicators
        refactoring_ratio = total_refactoring_contributions / max(total_debt_creation, 1)
        old_debt_ratio = len([age for age in debt_ages if age > 90]) / total_debt_items
        
        resistance_score = (1 - refactoring_ratio) * 0.6 + old_debt_ratio * 0.4
        
        return {
            "average_debt_age_days": avg_debt_age,
            "refactoring_to_creation_ratio": refactoring_ratio,
            "old_debt_percentage": old_debt_ratio * 100,
            "cultural_resistance_score": resistance_score * 100,
            "resistance_level": self._categorize_resistance(resistance_score)
        }
    
    def take_morale_snapshot(self):
        """Take a snapshot of current team morale and debt state"""
        if not self.engineers:
            return
        
        current_morale = statistics.mean(eng.current_morale for eng in self.engineers.values())
        debt_score = self.calculate_debt_burden_score()
        
        # Category breakdown
        category_breakdown = defaultdict(float)
        for item in self.debt_items:
            category_breakdown[item.category] += item.impact_score
        
        # Recent activity (last 30 days)
        recent_additions = len([item for item in self.debt_items 
                              if (datetime.now() - item.created_date).days <= 30])
        
        # Business pressure (from recent events)
        recent_pressure_events = [event for event in self.pressure_events
                                if (datetime.now() - event["timestamp"]).days <= 7]
        avg_pressure = statistics.mean([event["intensity"] for event in recent_pressure_events]) \
                      if recent_pressure_events else 5
        
        snapshot = MoraleSnapshot(
            timestamp=datetime.now(),
            team_average_morale=current_morale,
            total_debt_score=debt_score,
            debt_category_breakdown=dict(category_breakdown),
            business_pressure_level=int(avg_pressure),
            recent_debt_additions=recent_additions,
            recent_debt_paydowns=0  # Would track actual paydowns
        )
        
        self.morale_history.append(snapshot)
        print(f"📸 Morale snapshot taken: Team morale {current_morale:.1f}/10, Debt score {debt_score:.1f}")
    
    def generate_psychology_report(self) -> Dict:
        """Generate comprehensive technical debt psychology report"""
        debt_burden = self.calculate_debt_burden_score()
        morale_analysis = self.analyze_morale_debt_correlation()
        productivity_impact = self.calculate_productivity_impact()
        high_frustration = self.identify_high_frustration_debt()
        priorities = self.prioritize_debt_by_psychology()
        resistance = self.track_refactoring_resistance()
        
        return {
            "analysis_date": datetime.now(),
            "team_size": len(self.engineers),
            "total_debt_items": len(self.debt_items),
            "debt_burden_score": debt_burden,
            "morale_debt_correlation": morale_analysis,
            "productivity_impact": productivity_impact,
            "top_frustrating_items": [item.title for item in high_frustration],
            "refactoring_priorities": [p["debt_item"].title for p in priorities[:5]],
            "cultural_resistance": resistance,
            "recommendations": self._generate_psychology_recommendations(
                debt_burden, morale_analysis, productivity_impact, resistance
            )
        }
    
    # Helper methods
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate simple correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x_sq = sum(xi * xi for xi in x)
        sum_y_sq = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x_sq - sum_x * sum_x) * (n * sum_y_sq - sum_y * sum_y)) ** 0.5
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "stable"
        
        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])
        
        diff = second_half - first_half
        if diff > 0.5:
            return "improving"
        elif diff < -0.5:
            return "declining"
        else:
            return "stable"
    
    def _assess_debt_morale_impact(self, correlation: float, morale_trend: str) -> str:
        """Assess the impact of debt on morale"""
        if correlation < -0.6:
            return "Strong negative impact - debt is significantly hurting morale"
        elif correlation < -0.3:
            return "Moderate negative impact - debt affecting team happiness"
        elif morale_trend == "declining":
            return "Declining morale trend - monitor debt accumulation closely"
        else:
            return "Limited impact - team coping well with current debt levels"
    
    def _get_priority_reason(self, item: TechnicalDebtItem) -> str:
        """Get reason for prioritizing this debt item"""
        if item.frustration_level >= 8:
            return "High frustration level affecting daily work"
        elif item.new_engineer_confusion_rate > 0.5:
            return "Confusing to new team members, impacting onboarding"
        elif item.debugging_time_multiplier > 2.0:
            return "Significantly slowing down debugging and maintenance"
        elif item.developer_complaints >= 5:
            return "Frequent complaints from multiple developers"
        else:
            return "Good balance of impact vs effort"
    
    def _categorize_resistance(self, resistance_score: float) -> str:
        """Categorize cultural resistance level"""
        if resistance_score > 0.7:
            return "High resistance - cultural intervention needed"
        elif resistance_score > 0.4:
            return "Moderate resistance - encourage refactoring initiatives"
        else:
            return "Low resistance - healthy refactoring culture"
    
    def _generate_psychology_recommendations(self, debt_burden: float, morale_analysis: Dict,
                                           productivity_impact: Dict, resistance: Dict) -> List[str]:
        """Generate psychology-based recommendations"""
        recommendations = []
        
        if debt_burden > 60:
            recommendations.append("🚨 High debt burden detected - immediate action needed")
            recommendations.append("🎯 Focus on high-frustration items first")
        
        if morale_analysis.get("correlation_coefficient", 0) < -0.5:
            recommendations.append("📉 Debt significantly impacting morale - prioritize team happiness")
            recommendations.append("🗣️ Conduct team retrospectives on debt frustrations")
        
        if productivity_impact.get("productivity_loss_percentage", 0) > 20:
            recommendations.append("⏱️ Significant productivity loss - business case for refactoring")
            recommendations.append("📊 Present productivity metrics to stakeholders")
        
        if resistance.get("cultural_resistance_score", 0) > 60:
            recommendations.append("🏛️ Address cultural resistance to refactoring")
            recommendations.append("🎓 Provide technical debt education to team")
        
        # Indian context recommendations
        recommendations.append("👥 Create 'debt cleanup' team activities")
        recommendations.append("🏆 Recognize and celebrate debt reduction efforts")
        
        return recommendations

def demo_technical_debt_psychology_tracker():
    print("🧠 Technical Debt Psychology Tracker Demo")
    print("=" * 50)
    
    tracker = TechnicalDebtPsychologyTracker()
    
    # Add engineers
    engineers = [
        Engineer("E1", "Rajesh Kumar", 4, 0.7, 7, 0.8, 0.3),
        Engineer("E2", "Priya Menon", 3, 0.5, 6, 0.7, 0.4),
        Engineer("E3", "Amit Patel", 2, 0.6, 5, 0.6, 0.5),
    ]
    
    for eng in engineers:
        tracker.add_engineer(eng)
    
    # Add debt items with varying psychological impact
    debt_items = [
        TechnicalDebtItem(
            "DEBT001", "Legacy Authentication System",
            "Old auth system causing frequent bugs and security concerns",
            DebtCategory.ARCHITECTURE, 120, 9, 8,
            datetime.now() - timedelta(days=180),
            PressureSource.BUSINESS_DEADLINES, ["E1", "E2"],
            "Had to ship quickly for major client",
            developer_complaints=8, workaround_complexity=4,
            new_engineer_confusion_rate=0.8, debugging_time_multiplier=2.5
        ),
        TechnicalDebtItem(
            "DEBT002", "Missing Unit Tests in Payment Module",
            "Critical payment processing lacks comprehensive test coverage",
            DebtCategory.TESTING, 80, 8, 7,
            datetime.now() - timedelta(days=90),
            PressureSource.CUSTOMER_REQUESTS, ["E1", "E3"],
            "Customer demanded feature faster than testing schedule",
            developer_complaints=5, workaround_complexity=3,
            new_engineer_confusion_rate=0.6, debugging_time_multiplier=1.8
        ),
        TechnicalDebtItem(
            "DEBT003", "Outdated Documentation",
            "API documentation is severely outdated and misleading",
            DebtCategory.DOCUMENTATION, 40, 6, 9,
            datetime.now() - timedelta(days=270),
            PressureSource.RESOURCE_CONSTRAINTS, ["E2", "E3"],
            "No time allocated for documentation updates",
            developer_complaints=12, workaround_complexity=2,
            new_engineer_confusion_rate=0.9, debugging_time_multiplier=1.3
        )
    ]
    
    for item in debt_items:
        tracker.add_debt_item(item)
    
    # Record business pressure events
    tracker.record_business_pressure_event(
        PressureSource.BUSINESS_DEADLINES, 8, 
        "Quarter-end push for new feature delivery"
    )
    
    # Take morale snapshots
    tracker.take_morale_snapshot()
    
    # Simulate some time passing and changes
    tracker.engineers["E3"].current_morale = 4  # Declining morale
    tracker.take_morale_snapshot()
    
    # Generate comprehensive report
    print("\n📊 Generating Technical Debt Psychology Report...")
    report = tracker.generate_psychology_report()
    
    print(f"\n🎯 Technical Debt Psychology Analysis")
    print(f"Team Size: {report['team_size']}")
    print(f"Total Debt Items: {report['total_debt_items']}")
    print(f"Debt Burden Score: {report['debt_burden_score']:.1f}/100")
    
    print(f"\n📈 Productivity Impact:")
    prod_impact = report['productivity_impact']
    if 'productivity_loss_percentage' in prod_impact:
        print(f"   Productivity Loss: {prod_impact['productivity_loss_percentage']:.1f}%")
        print(f"   Debug Time Waste: {prod_impact['debug_time_waste_percentage']:.1f}%")
    
    print(f"\n😤 Top Frustrating Items:")
    for item in report['top_frustrating_items']:
        print(f"   • {item}")
    
    print(f"\n🎯 Refactoring Priorities:")
    for item in report['refactoring_priorities']:
        print(f"   • {item}")
    
    cultural_resistance = report['cultural_resistance']
    if 'cultural_resistance_score' in cultural_resistance:
        print(f"\n🏛️ Cultural Analysis:")
        print(f"   Resistance Score: {cultural_resistance['cultural_resistance_score']:.1f}%")
        print(f"   Resistance Level: {cultural_resistance['resistance_level']}")
        print(f"   Average Debt Age: {cultural_resistance['average_debt_age_days']:.0f} days")
    
    print(f"\n💡 Psychology-Based Recommendations:")
    for rec in report['recommendations']:
        print(f"   • {rec}")

if __name__ == "__main__":
    demo_technical_debt_psychology_tracker()
#!/usr/bin/env python3
"""
Sustainable Engineering Metrics - Episode 3: Human Factor in Tech  
================================================================

Long-term engineering sustainability measure karna - velocity, quality, team health
ka balance check karte hue. Indian workplace context ke saath career longevity aur
family balance considerations.

Features:
- Sustainable velocity tracking
- Quality vs speed balance analysis
- Team health trending over time
- Burnout prediction algorithms
- Career progression sustainability
- Work-life integration scoring
- Long-term productivity forecasting
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import statistics
import math
from collections import defaultdict

class SustainabilityMetric(Enum):
    VELOCITY_CONSISTENCY = "velocity_consistency"
    QUALITY_MAINTENANCE = "quality_maintenance"
    TEAM_STABILITY = "team_stability"
    LEARNING_GROWTH = "learning_growth"
    WORK_LIFE_INTEGRATION = "work_life_integration"
    CAREER_PROGRESSION = "career_progression"
    INNOVATION_TIME = "innovation_time"

class RiskLevel(Enum):
    LOW = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class EngineerProfile:
    """Engineer profile with sustainability factors"""
    id: str
    name: str
    joining_date: datetime
    current_level: int  # 1-7 career level
    age: int
    family_stage: str  # "single", "married", "new_parent", "established_family"
    
    # Performance metrics
    velocity_history: List[float] = field(default_factory=list)
    quality_scores: List[float] = field(default_factory=list)
    learning_hours: List[int] = field(default_factory=list)
    overtime_hours: List[int] = field(default_factory=list)
    
    # Wellness indicators
    stress_levels: List[int] = field(default_factory=list)  # 1-10
    job_satisfaction: List[int] = field(default_factory=list)  # 1-10
    career_growth_satisfaction: List[int] = field(default_factory=list)  # 1-10
    
    # Sustainability flags
    burnout_risk_score: float = 0.0
    career_plateau_risk: float = 0.0
    retention_probability: float = 1.0

@dataclass
class TeamMetrics:
    """Team-level sustainability metrics"""
    team_id: str
    measurement_period: datetime
    
    # Velocity metrics
    average_velocity: float
    velocity_consistency: float  # Lower variance = more consistent
    sustainable_velocity_score: float
    
    # Quality metrics
    defect_rate: float
    code_review_thoroughness: float
    technical_debt_ratio: float
    
    # Team health
    average_team_morale: float
    knowledge_distribution_score: float  # Avoid single points of failure
    collaboration_effectiveness: float
    
    # Sustainability indicators
    overtime_frequency: float
    learning_investment_ratio: float
    innovation_time_percentage: float
    
    # Predictive metrics
    projected_burnout_risk: float
    team_stability_forecast: float
    sustainable_growth_potential: float

@dataclass
class SustainabilityAlert:
    """Alert for sustainability risks"""
    alert_id: str
    timestamp: datetime
    risk_level: RiskLevel
    category: SustainabilityMetric
    affected_entities: List[str]  # Engineer IDs or team IDs
    description: str
    recommended_actions: List[str]
    predicted_impact_timeline: str

class SustainableEngineeringMetrics:
    """Main system for tracking sustainable engineering practices"""
    
    def __init__(self):
        self.engineers: Dict[str, EngineerProfile] = {}
        self.team_metrics_history: List[TeamMetrics] = []
        self.sustainability_alerts: List[SustainabilityAlert] = []
        
        # Sustainability thresholds (based on research and industry standards)
        self.thresholds = {
            "max_sustainable_overtime_hours": 5,  # per week
            "min_learning_hours_per_month": 8,
            "max_velocity_variance": 0.3,  # 30% variance
            "min_job_satisfaction": 6,  # out of 10
            "max_stress_level": 7,  # out of 10
            "min_innovation_time": 0.15,  # 15% of time
        }
        
    def add_engineer(self, engineer: EngineerProfile):
        """Add engineer to sustainability tracking"""
        self.engineers[engineer.id] = engineer
        print(f"👤 Added {engineer.name} to sustainability tracking")
        print(f"   Career Level: {engineer.current_level}, Family Stage: {engineer.family_stage}")
    
    def record_sprint_metrics(self, engineer_id: str, velocity: float, quality_score: float,
                            overtime_hours: int, stress_level: int, learning_hours: int = 0):
        """Record sprint-level metrics for sustainability analysis"""
        if engineer_id not in self.engineers:
            print(f"❌ Engineer {engineer_id} not found")
            return
            
        engineer = self.engineers[engineer_id]
        engineer.velocity_history.append(velocity)
        engineer.quality_scores.append(quality_score)
        engineer.overtime_hours.append(overtime_hours)
        engineer.stress_levels.append(stress_level)
        engineer.learning_hours.append(learning_hours)
        
        # Calculate sustainability scores
        self._update_sustainability_scores(engineer)
        
        print(f"📊 Recorded metrics for {engineer.name}")
        if overtime_hours > self.thresholds["max_sustainable_overtime_hours"]:
            print(f"   ⚠️ High overtime: {overtime_hours}h (threshold: {self.thresholds['max_sustainable_overtime_hours']}h)")
        if stress_level > self.thresholds["max_stress_level"]:
            print(f"   🔥 High stress: {stress_level}/10")
    
    def _update_sustainability_scores(self, engineer: EngineerProfile):
        """Update engineer's sustainability risk scores"""
        if len(engineer.velocity_history) < 3:
            return  # Need at least 3 data points
        
        # Burnout risk calculation
        recent_overtime = engineer.overtime_hours[-4:] if len(engineer.overtime_hours) >= 4 else engineer.overtime_hours
        recent_stress = engineer.stress_levels[-4:] if len(engineer.stress_levels) >= 4 else engineer.stress_levels
        
        avg_overtime = statistics.mean(recent_overtime) if recent_overtime else 0
        avg_stress = statistics.mean(recent_stress) if recent_stress else 5
        
        # Burnout risk factors
        overtime_risk = min(avg_overtime / 20, 1.0)  # 20h+ = 100% risk contribution
        stress_risk = max(0, (avg_stress - 5) / 5)  # Stress above 5 contributes to risk
        
        # Velocity decline risk
        velocity_trend = self._calculate_trend(engineer.velocity_history[-6:])
        velocity_risk = max(0, -velocity_trend)  # Negative trend increases risk
        
        # Quality pressure risk
        quality_trend = self._calculate_trend(engineer.quality_scores[-6:])
        quality_risk = max(0, -quality_trend * 2)  # Quality decline = higher risk
        
        engineer.burnout_risk_score = (overtime_risk * 0.3 + stress_risk * 0.3 + 
                                     velocity_risk * 0.2 + quality_risk * 0.2)
        
        # Career plateau risk
        learning_trend = self._calculate_trend(engineer.learning_hours[-6:]) if len(engineer.learning_hours) >= 6 else 0
        career_stagnation = 1.0 if learning_trend < -0.5 else max(0, -learning_trend)
        
        # Age and level-based plateau risk
        years_in_role = (datetime.now() - engineer.joining_date).days / 365
        level_progression_rate = engineer.current_level / max(years_in_role, 1)
        
        expected_progression_rate = 0.8  # Expected level per year (adjustable)
        progression_gap = max(0, expected_progression_rate - level_progression_rate)
        
        engineer.career_plateau_risk = (career_stagnation * 0.6 + progression_gap * 0.4)
        
        # Retention probability (inverse of burnout + plateau risks)
        combined_risk = (engineer.burnout_risk_score + engineer.career_plateau_risk) / 2
        engineer.retention_probability = max(0.1, 1.0 - combined_risk)
    
    def calculate_team_sustainability_score(self, team_engineers: List[str]) -> Dict:
        """Calculate comprehensive team sustainability score"""
        if not team_engineers or not all(eng_id in self.engineers for eng_id in team_engineers):
            return {"error": "Invalid engineer list"}
        
        team = [self.engineers[eng_id] for eng_id in team_engineers]
        
        # Team velocity sustainability
        team_velocities = []
        for engineer in team:
            if engineer.velocity_history:
                team_velocities.extend(engineer.velocity_history[-4:])  # Recent 4 sprints
        
        velocity_consistency = 1.0 - (statistics.stdev(team_velocities) / statistics.mean(team_velocities)) \
                              if len(team_velocities) > 1 and statistics.mean(team_velocities) > 0 else 0.5
        
        # Team quality sustainability  
        team_quality = []
        for engineer in team:
            if engineer.quality_scores:
                team_quality.extend(engineer.quality_scores[-4:])
        
        avg_quality = statistics.mean(team_quality) if team_quality else 0.5
        quality_trend = self._calculate_trend(team_quality) if len(team_quality) > 2 else 0
        
        # Team wellness
        team_stress = []
        team_satisfaction = []
        for engineer in team:
            if engineer.stress_levels:
                team_stress.extend(engineer.stress_levels[-4:])
            if engineer.job_satisfaction:
                team_satisfaction.extend(engineer.job_satisfaction[-4:])
        
        avg_stress = statistics.mean(team_stress) if team_stress else 5
        avg_satisfaction = statistics.mean(team_satisfaction) if team_satisfaction else 5
        
        # Risk assessment
        avg_burnout_risk = statistics.mean(eng.burnout_risk_score for eng in team)
        avg_plateau_risk = statistics.mean(eng.career_plateau_risk for eng in team)
        avg_retention = statistics.mean(eng.retention_probability for eng in team)
        
        # Overall sustainability score
        wellness_score = ((10 - avg_stress) + avg_satisfaction) / 20  # 0-1 scale
        performance_score = (velocity_consistency + avg_quality + max(0, quality_trend)) / 3
        stability_score = avg_retention
        
        overall_sustainability = (wellness_score * 0.4 + performance_score * 0.35 + stability_score * 0.25)
        
        return {
            "team_size": len(team),
            "overall_sustainability_score": overall_sustainability,
            "velocity_consistency": velocity_consistency,
            "average_quality": avg_quality,
            "quality_trend": quality_trend,
            "average_stress_level": avg_stress,
            "average_satisfaction": avg_satisfaction,
            "average_burnout_risk": avg_burnout_risk,
            "average_plateau_risk": avg_plateau_risk,
            "retention_probability": avg_retention,
            "sustainability_grade": self._get_sustainability_grade(overall_sustainability)
        }
    
    def predict_team_health_trajectory(self, team_engineers: List[str], 
                                     months_ahead: int = 6) -> Dict:
        """Predict team health trajectory based on current trends"""
        current_metrics = self.calculate_team_sustainability_score(team_engineers)
        
        if "error" in current_metrics:
            return current_metrics
        
        # Trend analysis
        team = [self.engineers[eng_id] for eng_id in team_engineers if eng_id in self.engineers]
        
        # Stress trajectory
        all_recent_stress = []
        for engineer in team:
            if len(engineer.stress_levels) >= 6:
                all_recent_stress.extend(engineer.stress_levels[-6:])
        
        stress_trend = self._calculate_trend(all_recent_stress) if len(all_recent_stress) > 2 else 0
        predicted_stress = current_metrics["average_stress_level"] + (stress_trend * months_ahead)
        
        # Burnout risk trajectory
        burnout_trend = sum(eng.burnout_risk_score for eng in team) / len(team) if team else 0
        predicted_burnout_risk = min(1.0, burnout_trend + (stress_trend * 0.1 * months_ahead))
        
        # Quality trajectory
        all_recent_quality = []
        for engineer in team:
            if len(engineer.quality_scores) >= 6:
                all_recent_quality.extend(engineer.quality_scores[-6:])
        
        quality_trend = self._calculate_trend(all_recent_quality) if len(all_recent_quality) > 2 else 0
        predicted_quality = current_metrics["average_quality"] + (quality_trend * months_ahead)
        
        # Overall health prediction
        predicted_wellness = max(0.1, min(1.0, ((10 - predicted_stress) / 10)))
        predicted_performance = max(0.1, min(1.0, predicted_quality))
        predicted_sustainability = (predicted_wellness * 0.6 + predicted_performance * 0.4)
        
        return {
            "prediction_horizon_months": months_ahead,
            "current_sustainability": current_metrics["overall_sustainability_score"],
            "predicted_sustainability": predicted_sustainability,
            "predicted_stress_level": predicted_stress,
            "predicted_burnout_risk": predicted_burnout_risk,
            "predicted_quality": predicted_quality,
            "trajectory": self._get_trajectory_description(
                current_metrics["overall_sustainability_score"], 
                predicted_sustainability
            ),
            "risk_factors": self._identify_trajectory_risks(team),
            "intervention_recommendations": self._generate_intervention_recommendations(
                predicted_stress, predicted_burnout_risk, predicted_quality
            )
        }
    
    def generate_sustainability_alerts(self) -> List[SustainabilityAlert]:
        """Generate proactive sustainability alerts"""
        new_alerts = []
        
        for engineer_id, engineer in self.engineers.items():
            # High burnout risk alert
            if engineer.burnout_risk_score > 0.7:
                alert = SustainabilityAlert(
                    alert_id=f"BURNOUT_{engineer_id}_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    risk_level=RiskLevel.HIGH if engineer.burnout_risk_score > 0.8 else RiskLevel.MODERATE,
                    category=SustainabilityMetric.WORK_LIFE_INTEGRATION,
                    affected_entities=[engineer_id],
                    description=f"High burnout risk detected for {engineer.name} (score: {engineer.burnout_risk_score:.2f})",
                    recommended_actions=[
                        "🏖️ Recommend immediate time off or reduced workload",
                        "💬 Schedule 1-on-1 discussion about workload and stress",
                        "🎯 Review and adjust sprint commitments",
                        "🧘 Provide access to wellness resources"
                    ],
                    predicted_impact_timeline="2-4 weeks without intervention"
                )
                new_alerts.append(alert)
            
            # Career plateau alert
            if engineer.career_plateau_risk > 0.6:
                alert = SustainabilityAlert(
                    alert_id=f"PLATEAU_{engineer_id}_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    risk_level=RiskLevel.MODERATE,
                    category=SustainabilityMetric.CAREER_PROGRESSION,
                    affected_entities=[engineer_id],
                    description=f"Career plateau risk for {engineer.name} (score: {engineer.career_plateau_risk:.2f})",
                    recommended_actions=[
                        "📚 Provide learning and development opportunities",
                        "🎯 Create challenging stretch assignments",
                        "👨‍🏫 Offer mentorship or leadership roles",
                        "🚀 Discuss career growth plan and expectations"
                    ],
                    predicted_impact_timeline="3-6 months without intervention"
                )
                new_alerts.append(alert)
            
            # Declining quality alert
            if (len(engineer.quality_scores) >= 4 and 
                self._calculate_trend(engineer.quality_scores[-4:]) < -0.1):
                alert = SustainabilityAlert(
                    alert_id=f"QUALITY_{engineer_id}_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    risk_level=RiskLevel.MODERATE,
                    category=SustainabilityMetric.QUALITY_MAINTENANCE,
                    affected_entities=[engineer_id],
                    description=f"Declining quality trend for {engineer.name}",
                    recommended_actions=[
                        "🔍 Review workload and time pressures",
                        "👥 Provide additional code review support",
                        "📖 Offer training on quality practices",
                        "⏰ Adjust sprint velocity to allow for quality focus"
                    ],
                    predicted_impact_timeline="1-2 sprints without intervention"
                )
                new_alerts.append(alert)
        
        self.sustainability_alerts.extend(new_alerts)
        return new_alerts
    
    def generate_comprehensive_report(self, team_engineers: List[str]) -> Dict:
        """Generate comprehensive sustainability report"""
        team_metrics = self.calculate_team_sustainability_score(team_engineers)
        trajectory = self.predict_team_health_trajectory(team_engineers)
        alerts = self.generate_sustainability_alerts()
        
        # Individual engineer insights
        individual_insights = {}
        for eng_id in team_engineers:
            if eng_id in self.engineers:
                engineer = self.engineers[eng_id]
                individual_insights[engineer.name] = {
                    "burnout_risk": engineer.burnout_risk_score,
                    "career_plateau_risk": engineer.career_plateau_risk,
                    "retention_probability": engineer.retention_probability,
                    "sustainability_status": self._get_individual_sustainability_status(engineer)
                }
        
        return {
            "report_date": datetime.now(),
            "team_sustainability": team_metrics,
            "trajectory_prediction": trajectory,
            "individual_insights": individual_insights,
            "active_alerts": len([a for a in alerts if a.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]),
            "recommendations": self._generate_comprehensive_recommendations(team_metrics, trajectory, alerts),
            "long_term_outlook": self._assess_long_term_outlook(team_metrics, trajectory)
        }
    
    # Helper methods
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend slope for a list of values"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        y = values
        
        # Simple linear regression slope
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x_sq = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_sq - sum_x * sum_x) \
                if (n * sum_x_sq - sum_x * sum_x) != 0 else 0
        
        return slope
    
    def _get_sustainability_grade(self, score: float) -> str:
        """Convert sustainability score to letter grade"""
        if score >= 0.9:
            return "A+ (Excellent)"
        elif score >= 0.8:
            return "A (Very Good)"
        elif score >= 0.7:
            return "B (Good)"
        elif score >= 0.6:
            return "C (Adequate)"
        elif score >= 0.5:
            return "D (Concerning)"
        else:
            return "F (Critical)"
    
    def _get_trajectory_description(self, current: float, predicted: float) -> str:
        """Get description of trajectory"""
        change = predicted - current
        if change > 0.1:
            return "Improving"
        elif change < -0.1:
            return "Declining"
        else:
            return "Stable"
    
    def _identify_trajectory_risks(self, team: List[EngineerProfile]) -> List[str]:
        """Identify risks in team trajectory"""
        risks = []
        
        high_burnout_count = sum(1 for eng in team if eng.burnout_risk_score > 0.6)
        if high_burnout_count > len(team) * 0.3:
            risks.append(f"{high_burnout_count} team members at high burnout risk")
        
        low_retention_count = sum(1 for eng in team if eng.retention_probability < 0.7)
        if low_retention_count > 0:
            risks.append(f"{low_retention_count} team members at flight risk")
        
        plateau_count = sum(1 for eng in team if eng.career_plateau_risk > 0.5)
        if plateau_count > len(team) * 0.4:
            risks.append(f"{plateau_count} team members facing career plateau")
        
        return risks
    
    def _generate_intervention_recommendations(self, predicted_stress: float,
                                            predicted_burnout: float, 
                                            predicted_quality: float) -> List[str]:
        """Generate intervention recommendations"""
        recommendations = []
        
        if predicted_stress > 7:
            recommendations.append("🧘 Implement stress management initiatives")
            recommendations.append("⏰ Review workload distribution and deadlines")
        
        if predicted_burnout > 0.6:
            recommendations.append("🏖️ Plan mandatory rest periods and vacations")
            recommendations.append("👥 Consider team expansion or workload reduction")
        
        if predicted_quality < 0.6:
            recommendations.append("🔍 Increase focus on quality practices and code review")
            recommendations.append("📚 Provide technical skills training")
        
        # Indian context recommendations
        recommendations.append("🪔 Consider cultural events and festival planning in workload")
        recommendations.append("👨‍👩‍👧‍👦 Support work-life integration for family obligations")
        
        return recommendations
    
    def _get_individual_sustainability_status(self, engineer: EngineerProfile) -> str:
        """Get individual sustainability status"""
        if engineer.burnout_risk_score > 0.7:
            return "High Risk - Immediate Attention Needed"
        elif engineer.career_plateau_risk > 0.6:
            return "Career Development Focus Needed"
        elif engineer.retention_probability < 0.7:
            return "Retention Risk - Engagement Required"
        else:
            return "Sustainable - Monitor Regularly"
    
    def _generate_comprehensive_recommendations(self, team_metrics: Dict, 
                                             trajectory: Dict, alerts: List) -> List[str]:
        """Generate comprehensive recommendations"""
        recommendations = []
        
        if team_metrics.get("overall_sustainability_score", 0) < 0.7:
            recommendations.append("🎯 Focus on team sustainability improvements")
            
        if trajectory.get("trajectory") == "Declining":
            recommendations.append("🚨 Immediate intervention needed to reverse declining trend")
        
        if len(alerts) > 0:
            recommendations.append(f"📢 Address {len(alerts)} active sustainability alerts")
        
        recommendations.extend([
            "📊 Implement regular sustainability monitoring",
            "🗣️ Conduct monthly team retrospectives on sustainability",
            "🎓 Provide continuous learning and development opportunities",
            "⚖️ Maintain sustainable pace and realistic goal setting"
        ])
        
        return recommendations
    
    def _assess_long_term_outlook(self, team_metrics: Dict, trajectory: Dict) -> str:
        """Assess long-term team outlook"""
        current_score = team_metrics.get("overall_sustainability_score", 0)
        predicted_score = trajectory.get("predicted_sustainability", 0)
        
        if predicted_score > 0.8 and current_score > 0.7:
            return "Excellent - Team positioned for long-term success"
        elif predicted_score > 0.6 and trajectory.get("trajectory") == "Improving":
            return "Good - Positive trajectory with sustained effort"
        elif predicted_score < 0.5 or trajectory.get("trajectory") == "Declining":
            return "Concerning - Significant changes needed for sustainability"
        else:
            return "Moderate - Regular monitoring and adjustments needed"

def demo_sustainable_engineering_metrics():
    """Demo the sustainable engineering metrics system"""
    print("⚖️ Sustainable Engineering Metrics Demo")
    print("=" * 45)
    
    system = SustainableEngineeringMetrics()
    
    # Add engineers with different sustainability profiles
    engineers = [
        EngineerProfile(
            "E1", "Rajesh Kumar", datetime(2020, 1, 1), 4, 32, "married"
        ),
        EngineerProfile(
            "E2", "Priya Menon", datetime(2021, 6, 1), 3, 28, "new_parent"  
        ),
        EngineerProfile(
            "E3", "Amit Patel", datetime(2022, 3, 1), 2, 25, "single"
        )
    ]
    
    for engineer in engineers:
        system.add_engineer(engineer)
    
    # Simulate sprint metrics over time
    print("\n📈 Simulating sprint metrics over time...")
    
    # Rajesh - Experienced but showing burnout signs
    rajesh_metrics = [
        (8.5, 0.85, 2, 4, 6),   # Sprint 1: Good performance, low overtime
        (8.2, 0.82, 4, 5, 4),   # Sprint 2: Slight decline, more overtime
        (7.8, 0.78, 8, 6, 2),   # Sprint 3: Performance drop, high overtime
        (7.2, 0.70, 12, 7, 1),  # Sprint 4: Concerning decline, very high overtime
        (6.8, 0.65, 15, 8, 0),  # Sprint 5: Clear burnout signs
    ]
    
    for i, (vel, qual, ot, stress, learn) in enumerate(rajesh_metrics, 1):
        system.record_sprint_metrics("E1", vel, qual, ot, stress, learn)
        print(f"   Sprint {i} - Rajesh: velocity={vel}, quality={qual}, overtime={ot}h")
    
    # Priya - New parent, sustainable but limited growth
    priya_metrics = [
        (7.0, 0.90, 0, 6, 8),   # Good quality, no overtime, learning time
        (6.8, 0.88, 1, 6, 6),   # Consistent performance
        (6.5, 0.85, 2, 7, 4),   # Family pressures increasing
        (6.2, 0.82, 0, 7, 2),   # Reduced capacity but maintaining quality
        (6.0, 0.80, 1, 6, 3),   # Finding sustainable balance
    ]
    
    for i, (vel, qual, ot, stress, learn) in enumerate(priya_metrics, 1):
        system.record_sprint_metrics("E2", vel, qual, ot, stress, learn)
    
    # Amit - Junior, inconsistent but growing
    amit_metrics = [
        (4.5, 0.60, 6, 7, 12),  # Learning curve, high effort
        (5.2, 0.70, 4, 6, 10),  # Improving
        (6.0, 0.75, 2, 5, 8),   # Good progress
        (6.8, 0.80, 3, 4, 6),   # Solid improvement
        (7.2, 0.82, 1, 4, 8),   # Becoming sustainable
    ]
    
    for i, (vel, qual, ot, stress, learn) in enumerate(amit_metrics, 1):
        system.record_sprint_metrics("E3", vel, qual, ot, stress, learn)
    
    # Calculate team sustainability
    team_engineers = ["E1", "E2", "E3"]
    
    print("\n📊 Calculating team sustainability metrics...")
    team_metrics = system.calculate_team_sustainability_score(team_engineers)
    
    print(f"\n🎯 Team Sustainability Analysis:")
    print(f"Overall Score: {team_metrics['overall_sustainability_score']:.2f}")
    print(f"Sustainability Grade: {team_metrics['sustainability_grade']}")
    print(f"Velocity Consistency: {team_metrics['velocity_consistency']:.2f}")
    print(f"Average Quality: {team_metrics['average_quality']:.2f}")
    print(f"Average Stress: {team_metrics['average_stress_level']:.1f}/10")
    print(f"Burnout Risk: {team_metrics['average_burnout_risk']:.2f}")
    print(f"Retention Probability: {team_metrics['retention_probability']:.2f}")
    
    # Predict future trajectory
    print(f"\n🔮 Predicting 6-month trajectory...")
    trajectory = system.predict_team_health_trajectory(team_engineers, 6)
    
    print(f"Current Sustainability: {trajectory['current_sustainability']:.2f}")
    print(f"Predicted Sustainability: {trajectory['predicted_sustainability']:.2f}")
    print(f"Trajectory: {trajectory['trajectory']}")
    print(f"Predicted Stress Level: {trajectory['predicted_stress_level']:.1f}/10")
    print(f"Predicted Burnout Risk: {trajectory['predicted_burnout_risk']:.2f}")
    
    # Generate alerts
    print(f"\n🚨 Sustainability Alerts:")
    alerts = system.generate_sustainability_alerts()
    for alert in alerts:
        print(f"   {alert.risk_level.name}: {alert.description}")
        for action in alert.recommended_actions[:2]:
            print(f"     • {action}")
    
    # Comprehensive report
    print(f"\n📋 Comprehensive Sustainability Report:")
    report = system.generate_comprehensive_report(team_engineers)
    
    print(f"Long-term Outlook: {report['long_term_outlook']}")
    print(f"Active Critical Alerts: {report['active_alerts']}")
    
    print(f"\n👤 Individual Insights:")
    for name, insights in report['individual_insights'].items():
        print(f"   {name}:")
        print(f"     Burnout Risk: {insights['burnout_risk']:.2f}")
        print(f"     Status: {insights['sustainability_status']}")
    
    print(f"\n💡 Key Recommendations:")
    for rec in report['recommendations'][:4]:
        print(f"   • {rec}")

if __name__ == "__main__":
    demo_sustainable_engineering_metrics()
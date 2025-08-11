#!/usr/bin/env python3
"""
Incident Stress Calculator - Episode 3: Human Factor in Tech
===========================================================

Production incidents ke time pe team members ka stress level calculate karna
aur recovery recommendations dena. Indian workplace context ke saath.

Features:
- Real-time stress level monitoring during incidents
- Recovery time estimation based on incident severity
- Team stress aggregation and distribution
- Post-incident recovery tracking
- Burnout prevention alerts
- Cultural stress factors consideration
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import statistics

class IncidentSeverity(Enum):
    SEV1 = {"value": 4, "name": "Critical"}
    SEV2 = {"value": 3, "name": "High"}
    SEV3 = {"value": 2, "name": "Medium"}
    SEV4 = {"value": 1, "name": "Low"}

class StressLevel(Enum):
    LOW = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class IncidentParticipant:
    employee_id: str
    role_in_incident: str  # "commander", "responder", "observer"
    duration_involved: timedelta
    after_hours: bool
    weekend_involved: bool
    family_disrupted: bool  # Indian context - family time disrupted

@dataclass
class Incident:
    id: str
    title: str
    severity: IncidentSeverity
    start_time: datetime
    end_time: Optional[datetime]
    participants: List[IncidentParticipant]
    customer_impact: bool
    revenue_impact: float  # In INR
    media_attention: bool
    
@dataclass
class Employee:
    id: str
    name: str
    experience_level: int  # 1-5
    stress_tolerance: float  # 0-1
    recent_incident_count: int
    last_incident_date: Optional[datetime]
    family_responsibilities: int  # 1-5 scale
    
class IncidentStressCalculator:
    def __init__(self):
        self.employees: Dict[str, Employee] = {}
        self.incidents: List[Incident] = []
        self.stress_history: Dict[str, List[float]] = {}
        
    def add_employee(self, employee: Employee):
        self.employees[employee.id] = employee
        self.stress_history[employee.id] = []
        print(f"👤 Added {employee.name} to stress monitoring")
    
    def calculate_incident_stress(self, incident: Incident, employee_id: str) -> float:
        """Calculate stress level for an employee during incident"""
        employee = self.employees[employee_id]
        participant = next((p for p in incident.participants if p.employee_id == employee_id), None)
        
        if not participant:
            return 0.0
        
        # Base stress from incident severity
        base_stress = incident.severity.value["value"] * 0.25
        
        # Role-based stress multiplier
        role_multipliers = {
            "commander": 1.5,
            "responder": 1.0,
            "observer": 0.5
        }
        role_stress = base_stress * role_multipliers.get(participant.role_in_incident, 1.0)
        
        # Duration impact
        duration_hours = participant.duration_involved.total_seconds() / 3600
        duration_stress = min(duration_hours * 0.1, 1.0)  # Cap at 1.0
        
        # After-hours penalty (Indian context - family time importance)
        after_hours_penalty = 0.3 if participant.after_hours else 0.0
        weekend_penalty = 0.2 if participant.weekend_involved else 0.0
        family_disruption_penalty = 0.4 if participant.family_disrupted else 0.0
        
        # Customer/revenue impact stress
        impact_stress = 0.2 if incident.customer_impact else 0.0
        if incident.revenue_impact > 100000:  # 1 lakh INR
            impact_stress += 0.3
        
        # Media attention stress (Indian corporate culture)
        media_stress = 0.3 if incident.media_attention else 0.0
        
        # Experience-based adjustment
        experience_factor = max(0.5, (6 - employee.experience_level) / 5)
        
        # Recent incident fatigue
        fatigue_factor = min(employee.recent_incident_count * 0.1, 0.5)
        
        total_stress = (role_stress + duration_stress + after_hours_penalty + 
                       weekend_penalty + family_disruption_penalty + impact_stress + 
                       media_stress) * experience_factor + fatigue_factor
        
        # Adjust for personal stress tolerance
        adjusted_stress = total_stress / employee.stress_tolerance
        
        return min(adjusted_stress, 4.0)  # Cap at critical level
    
    def estimate_recovery_time(self, stress_level: float, employee: Employee) -> timedelta:
        """Estimate recovery time based on stress level and employee factors"""
        base_recovery_hours = stress_level * 6  # 6 hours per stress unit
        
        # Experience reduces recovery time
        experience_factor = max(0.5, (6 - employee.experience_level) / 5)
        
        # Family responsibilities may increase recovery time (Indian context)
        family_factor = 1 + (employee.family_responsibilities / 10)
        
        recovery_hours = base_recovery_hours * experience_factor * family_factor
        return timedelta(hours=recovery_hours)
    
    def calculate_team_stress_distribution(self, incident: Incident) -> Dict:
        """Calculate stress distribution across team"""
        stress_levels = {}
        total_stress = 0.0
        
        for participant in incident.participants:
            stress = self.calculate_incident_stress(incident, participant.employee_id)
            stress_levels[participant.employee_id] = stress
            total_stress += stress
            
            # Track in history
            self.stress_history[participant.employee_id].append(stress)
        
        avg_stress = total_stress / len(incident.participants) if incident.participants else 0
        
        # Identify high-stress individuals
        high_stress_employees = [emp_id for emp_id, stress in stress_levels.items() if stress >= 3.0]
        
        return {
            "individual_stress": stress_levels,
            "average_stress": avg_stress,
            "total_team_stress": total_stress,
            "high_stress_count": len(high_stress_employees),
            "high_stress_employees": high_stress_employees
        }
    
    def generate_recovery_plan(self, incident: Incident) -> Dict:
        """Generate recovery recommendations for team"""
        stress_distribution = self.calculate_team_stress_distribution(incident)
        recovery_recommendations = []
        
        # General recommendations
        if stress_distribution["average_stress"] > 2.5:
            recovery_recommendations.append("🧘 Team decompression session recommended")
            recovery_recommendations.append("☕ Informal team gathering for stress relief")
        
        # Individual recommendations
        individual_plans = {}
        for participant in incident.participants:
            employee = self.employees[participant.employee_id]
            stress = stress_distribution["individual_stress"][participant.employee_id]
            recovery_time = self.estimate_recovery_time(stress, employee)
            
            recommendations = []
            if stress >= 3.0:
                recommendations.append("🏖️ Take immediate time off for recovery")
                recommendations.append("💬 Consider counseling support")
            elif stress >= 2.0:
                recommendations.append("😴 Ensure adequate rest and sleep")
                recommendations.append("🏃 Light physical activity recommended")
            else:
                recommendations.append("✅ Normal recovery expected")
            
            # Indian context - family time consideration
            if participant.family_disrupted:
                recommendations.append("👨‍👩‍👧‍👦 Prioritize family time for emotional recovery")
            
            individual_plans[participant.employee_id] = {
                "stress_level": stress,
                "estimated_recovery_time": recovery_time,
                "recommendations": recommendations
            }
        
        return {
            "team_recommendations": recovery_recommendations,
            "individual_plans": individual_plans,
            "overall_recovery_estimate": max([plan["estimated_recovery_time"] 
                                            for plan in individual_plans.values()], 
                                           default=timedelta(0))
        }
    
    def check_burnout_risk(self, employee_id: str) -> Dict:
        """Check employee burnout risk based on stress history"""
        if employee_id not in self.stress_history:
            return {"risk_level": "unknown", "recommendations": []}
        
        history = self.stress_history[employee_id]
        if len(history) < 3:
            return {"risk_level": "insufficient_data", "recommendations": []}
        
        recent_avg = statistics.mean(history[-5:])  # Last 5 incidents
        overall_avg = statistics.mean(history)
        trend = recent_avg - overall_avg
        
        risk_level = "low"
        if recent_avg > 2.5 and trend > 0.5:
            risk_level = "high"
        elif recent_avg > 2.0 or trend > 0.3:
            risk_level = "moderate"
        
        recommendations = []
        if risk_level == "high":
            recommendations.extend([
                "🚨 Immediate intervention needed",
                "📅 Reduce on-call duties temporarily", 
                "🏥 Professional support recommended"
            ])
        elif risk_level == "moderate":
            recommendations.extend([
                "⚠️ Monitor closely",
                "💪 Stress management training",
                "⚖️ Work-life balance review"
            ])
        
        return {
            "risk_level": risk_level,
            "recent_average_stress": recent_avg,
            "trend": trend,
            "recommendations": recommendations
        }

def demo_incident_stress_calculator():
    print("📊 Incident Stress Calculator Demo")
    print("=" * 40)
    
    calculator = IncidentStressCalculator()
    
    # Add employees
    employees = [
        Employee("E1", "Rajesh Kumar", 4, 0.8, 2, datetime.now() - timedelta(days=10), 4),
        Employee("E2", "Priya Menon", 3, 0.6, 1, datetime.now() - timedelta(days=5), 2),  
        Employee("E3", "Amit Patel", 2, 0.7, 0, None, 1),
    ]
    
    for emp in employees:
        calculator.add_employee(emp)
    
    # Create a sample incident
    incident = Incident(
        id="INC001",
        title="Payment Gateway Complete Failure",
        severity=IncidentSeverity.SEV1,
        start_time=datetime.now() - timedelta(hours=3),
        end_time=datetime.now() - timedelta(hours=1),
        participants=[
            IncidentParticipant("E1", "commander", timedelta(hours=2), True, False, True),
            IncidentParticipant("E2", "responder", timedelta(hours=2), True, False, False),
            IncidentParticipant("E3", "observer", timedelta(hours=1), True, False, False),
        ],
        customer_impact=True,
        revenue_impact=500000,  # 5 lakh INR
        media_attention=True
    )
    
    # Calculate stress distribution
    stress_dist = calculator.calculate_team_stress_distribution(incident)
    
    print(f"\n📈 Incident Stress Analysis:")
    print(f"Incident: {incident.title}")
    print(f"Severity: {incident.severity.value['name']}")
    print(f"Team Average Stress: {stress_dist['average_stress']:.2f}/4.0")
    print(f"High Stress Members: {stress_dist['high_stress_count']}")
    
    print(f"\n👤 Individual Stress Levels:")
    for emp_id, stress in stress_dist['individual_stress'].items():
        employee = calculator.employees[emp_id]
        print(f"   {employee.name}: {stress:.2f}/4.0")
    
    # Generate recovery plan
    recovery_plan = calculator.generate_recovery_plan(incident)
    
    print(f"\n🏥 Recovery Plan:")
    print(f"Overall Recovery Time: {recovery_plan['overall_recovery_estimate']}")
    
    print(f"\nTeam Recommendations:")
    for rec in recovery_plan['team_recommendations']:
        print(f"   • {rec}")
    
    print(f"\nIndividual Plans:")
    for emp_id, plan in recovery_plan['individual_plans'].items():
        employee = calculator.employees[emp_id]
        print(f"\n   {employee.name}:")
        print(f"   Recovery Time: {plan['estimated_recovery_time']}")
        for rec in plan['recommendations']:
            print(f"   • {rec}")
    
    # Check burnout risk (simulate history)
    calculator.stress_history["E1"].extend([2.8, 3.1, 2.9, 3.2])  # Simulate history
    burnout_risk = calculator.check_burnout_risk("E1")
    
    print(f"\n🔥 Burnout Risk Assessment for Rajesh:")
    print(f"Risk Level: {burnout_risk['risk_level']}")
    print(f"Recent Average Stress: {burnout_risk.get('recent_average_stress', 0):.2f}")
    for rec in burnout_risk['recommendations']:
        print(f"   • {rec}")

if __name__ == "__main__":
    demo_incident_stress_calculator()
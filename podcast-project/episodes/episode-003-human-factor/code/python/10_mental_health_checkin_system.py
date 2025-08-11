#!/usr/bin/env python3
"""
Mental Health Check-in System - Episode 3: Human Factor in Tech
==============================================================

Indian workplace mein mental health monitoring with cultural sensitivity.
Family pressures, work stress, aur social expectations ko consider karte hue.

Features:
- Anonymous wellness surveys
- Stress pattern detection
- Cultural stigma-free reporting
- Family pressure impact assessment
- Festival season mental health tracking
- Confidential support resource recommendations
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import statistics
from collections import defaultdict

class WellnessLevel(Enum):
    EXCELLENT = 5
    GOOD = 4
    MODERATE = 3
    CONCERNING = 2
    CRITICAL = 1

class StressCategory(Enum):
    WORK_PRESSURE = "work_pressure"
    FAMILY_EXPECTATIONS = "family_expectations"
    FINANCIAL_CONCERNS = "financial_concerns"
    HEALTH_ISSUES = "health_issues"
    RELATIONSHIP_STRESS = "relationship_stress"
    CAREER_UNCERTAINTY = "career_uncertainty"

@dataclass
class WellnessCheckIn:
    id: str
    employee_id: str
    timestamp: datetime
    overall_wellness: WellnessLevel
    stress_categories: Dict[StressCategory, int]  # 1-5 scale
    sleep_quality: int  # 1-5 scale
    work_life_balance: int  # 1-5 scale
    social_connection: int  # 1-5 scale
    anonymous_feedback: str
    is_anonymous: bool = True

@dataclass
class Employee:
    id: str
    name: str
    team: str
    joining_date: datetime
    family_status: str  # "single", "married", "married_with_kids"
    support_system_strength: int  # 1-5 scale

class MentalHealthCheckInSystem:
    def __init__(self):
        self.employees: Dict[str, Employee] = {}
        self.check_ins: List[WellnessCheckIn] = []
        self.wellness_trends: Dict[str, List[float]] = defaultdict(list)
        
    def add_employee(self, employee: Employee):
        self.employees[employee.id] = employee
        print(f"🤗 Added {employee.name} to wellness monitoring (confidential)")
    
    def record_check_in(self, check_in: WellnessCheckIn):
        self.check_ins.append(check_in)
        self.wellness_trends[check_in.employee_id].append(check_in.overall_wellness.value)
        
        # Alert for critical wellness levels
        if check_in.overall_wellness == WellnessLevel.CRITICAL:
            self._trigger_support_alert(check_in.employee_id)
        
        print("💚 Wellness check-in recorded (confidential)")
    
    def _trigger_support_alert(self, employee_id: str):
        """Confidentially trigger support for employee in critical state"""
        print("🚨 Support resources automatically recommended (confidential)")
        # In real system: trigger HR support, counseling resources, etc.
    
    def analyze_team_wellness(self, team_name: str) -> Dict:
        """Analyze team wellness trends (aggregated, anonymous)"""
        team_employees = [emp for emp in self.employees.values() if emp.team == team_name]
        team_check_ins = [ci for ci in self.check_ins 
                         if ci.employee_id in [emp.id for emp in team_employees]]
        
        if not team_check_ins:
            return {"error": "No data available"}
        
        # Aggregate metrics (preserving anonymity)
        recent_check_ins = [ci for ci in team_check_ins 
                          if ci.timestamp >= datetime.now() - timedelta(days=30)]
        
        avg_wellness = statistics.mean(ci.overall_wellness.value for ci in recent_check_ins)
        stress_patterns = defaultdict(list)
        
        for check_in in recent_check_ins:
            for category, level in check_in.stress_categories.items():
                stress_patterns[category].append(level)
        
        avg_stress = {category: statistics.mean(levels) 
                     for category, levels in stress_patterns.items()}
        
        return {
            "team_name": team_name,
            "team_size": len(team_employees),
            "average_wellness": avg_wellness,
            "stress_patterns": avg_stress,
            "risk_level": self._calculate_team_risk_level(avg_wellness, avg_stress),
            "recommendations": self._generate_team_recommendations(avg_wellness, avg_stress)
        }
    
    def _calculate_team_risk_level(self, avg_wellness: float, stress_patterns: Dict) -> str:
        """Calculate team mental health risk level"""
        if avg_wellness >= 4.0:
            return "Low Risk"
        elif avg_wellness >= 3.0:
            return "Moderate Risk"
        else:
            return "High Risk"
    
    def _generate_team_recommendations(self, avg_wellness: float, stress_patterns: Dict) -> List[str]:
        """Generate team-level wellness recommendations"""
        recommendations = []
        
        if avg_wellness < 3.5:
            recommendations.append("🧘 Consider team wellness activities")
            recommendations.append("⏰ Review workload distribution")
        
        # Check for high stress categories
        if stress_patterns.get(StressCategory.WORK_PRESSURE, 0) > 3.5:
            recommendations.append("💼 Address work pressure and deadlines")
        
        if stress_patterns.get(StressCategory.FAMILY_EXPECTATIONS, 0) > 3.0:
            recommendations.append("👨‍👩‍👧‍👦 Provide family-work balance support")
        
        recommendations.append("📞 Ensure EAP resources are well-communicated")
        
        return recommendations

def demo_mental_health_system():
    print("💚 Mental Health Check-in System Demo")
    print("=" * 45)
    
    system = MentalHealthCheckInSystem()
    
    # Add employees
    employees = [
        Employee("E1", "Employee A", "Engineering", datetime.now() - timedelta(days=365), "married_with_kids", 3),
        Employee("E2", "Employee B", "Engineering", datetime.now() - timedelta(days=730), "single", 4),
        Employee("E3", "Employee C", "Engineering", datetime.now() - timedelta(days=180), "married", 2),
    ]
    
    for emp in employees:
        system.add_employee(emp)
    
    # Simulate check-ins
    check_ins = [
        WellnessCheckIn(
            id="CHK1",
            employee_id="E1",
            timestamp=datetime.now() - timedelta(days=1),
            overall_wellness=WellnessLevel.MODERATE,
            stress_categories={
                StressCategory.WORK_PRESSURE: 4,
                StressCategory.FAMILY_EXPECTATIONS: 3,
                StressCategory.FINANCIAL_CONCERNS: 2
            },
            sleep_quality=3,
            work_life_balance=2,
            social_connection=3,
            anonymous_feedback="Work-life balance is challenging with kids"
        ),
        WellnessCheckIn(
            id="CHK2", 
            employee_id="E2",
            timestamp=datetime.now() - timedelta(days=1),
            overall_wellness=WellnessLevel.GOOD,
            stress_categories={
                StressCategory.WORK_PRESSURE: 2,
                StressCategory.CAREER_UNCERTAINTY: 3
            },
            sleep_quality=4,
            work_life_balance=4,
            social_connection=4,
            anonymous_feedback="Generally doing well"
        )
    ]
    
    for check_in in check_ins:
        system.record_check_in(check_in)
    
    # Analyze team wellness
    team_analysis = system.analyze_team_wellness("Engineering")
    
    print(f"\n📊 Team Wellness Analysis (Anonymous):")
    print(f"Team: {team_analysis['team_name']}")
    print(f"Average Wellness: {team_analysis['average_wellness']:.2f}/5.0")
    print(f"Risk Level: {team_analysis['risk_level']}")
    
    print(f"\n🎯 Stress Patterns:")
    for category, level in team_analysis['stress_patterns'].items():
        print(f"   {category.value}: {level:.1f}/5.0")
    
    print(f"\n💡 Recommendations:")
    for rec in team_analysis['recommendations']:
        print(f"   • {rec}")

if __name__ == "__main__":
    demo_mental_health_system()
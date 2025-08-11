#!/usr/bin/env python3
"""
Cultural Bias Detector - Episode 3: Human Factor in Tech
========================================================

Indian workplace mein unconscious bias detect karna aur address karna.
Regional, linguistic, aur hierarchical biases ko identify kar ke fair workplace banane ke liye.

Features:
- Language preference bias detection
- Regional stereotype identification  
- Hierarchy-based discrimination alerts
- Meeting participation equity analysis
- Promotion pattern fairness scoring
- Cultural celebration inclusivity tracking
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
import statistics
from collections import defaultdict, Counter

class BiasType(Enum):
    LINGUISTIC = "linguistic"
    REGIONAL = "regional"  
    HIERARCHICAL = "hierarchical"
    GENDER = "gender"
    AGE = "age"
    EDUCATIONAL = "educational"

@dataclass
class BiasIncident:
    id: str
    timestamp: datetime
    bias_type: BiasType
    description: str
    severity_score: float  # 0-1
    participants: List[str]
    context: str
    resolution_status: str = "open"

@dataclass
class Employee:
    id: str
    name: str
    region: str
    primary_language: str
    age: int
    gender: str
    education_background: str
    hierarchy_level: int
    years_at_company: int
    
    # Participation metrics
    meeting_participation_score: float = 0.5
    idea_acceptance_rate: float = 0.5
    promotion_velocity: float = 0.5
    mentorship_opportunities: int = 0

class CulturalBiasDetector:
    def __init__(self):
        self.employees: Dict[str, Employee] = {}
        self.incidents: List[BiasIncident] = []
        self.bias_patterns: Dict[BiasType, float] = defaultdict(float)
    
    def add_employee(self, employee: Employee):
        self.employees[employee.id] = employee
        print(f"👤 Added {employee.name} from {employee.region} to bias monitoring")
    
    def detect_language_bias(self) -> List[BiasIncident]:
        """Detect language-based bias patterns"""
        incidents = []
        
        # Group employees by language
        lang_groups = defaultdict(list)
        for emp in self.employees.values():
            lang_groups[emp.primary_language].append(emp)
        
        # Compare participation scores across language groups
        lang_scores = {}
        for lang, emps in lang_groups.items():
            if len(emps) > 1:
                avg_participation = statistics.mean(e.meeting_participation_score for e in emps)
                lang_scores[lang] = avg_participation
        
        if len(lang_scores) > 1:
            max_score = max(lang_scores.values())
            min_score = min(lang_scores.values())
            
            if max_score - min_score > 0.2:  # Significant gap
                incident = BiasIncident(
                    id=f"BIAS_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    bias_type=BiasType.LINGUISTIC,
                    description=f"Language bias detected: {max_score-min_score:.2f} participation gap",
                    severity_score=max_score - min_score,
                    participants=list(self.employees.keys()),
                    context="meeting_participation"
                )
                incidents.append(incident)
        
        return incidents
    
    def analyze_promotion_fairness(self) -> Dict:
        """Analyze promotion patterns for bias"""
        regional_promotion_rates = defaultdict(list)
        gender_promotion_rates = defaultdict(list)
        
        for emp in self.employees.values():
            regional_promotion_rates[emp.region].append(emp.promotion_velocity)
            gender_promotion_rates[emp.gender].append(emp.promotion_velocity)
        
        analysis = {
            "regional_fairness": self._calculate_fairness_score(regional_promotion_rates),
            "gender_fairness": self._calculate_fairness_score(gender_promotion_rates),
            "overall_bias_risk": 0.0
        }
        
        # Calculate overall bias risk
        fairness_scores = [analysis["regional_fairness"], analysis["gender_fairness"]]
        analysis["overall_bias_risk"] = 1.0 - statistics.mean(fairness_scores)
        
        return analysis
    
    def _calculate_fairness_score(self, group_data: Dict) -> float:
        """Calculate fairness score across groups"""
        if len(group_data) < 2:
            return 1.0
        
        group_means = []
        for group, values in group_data.items():
            if values:
                group_means.append(statistics.mean(values))
        
        if len(group_means) < 2:
            return 1.0
        
        # Calculate coefficient of variation (lower is more fair)
        mean_of_means = statistics.mean(group_means)
        if mean_of_means == 0:
            return 1.0
        
        std_of_means = statistics.stdev(group_means) if len(group_means) > 1 else 0
        coefficient_of_variation = std_of_means / mean_of_means
        
        # Convert to fairness score (0-1, higher is more fair)
        fairness_score = max(0, 1 - coefficient_of_variation)
        return fairness_score
    
    def generate_bias_report(self) -> Dict:
        """Generate comprehensive bias analysis report"""
        language_incidents = self.detect_language_bias()
        promotion_analysis = self.analyze_promotion_fairness()
        
        return {
            "total_employees": len(self.employees),
            "bias_incidents": len(language_incidents),
            "language_bias_detected": len(language_incidents) > 0,
            "promotion_fairness": promotion_analysis,
            "recommendations": self._generate_recommendations(language_incidents, promotion_analysis)
        }
    
    def _generate_recommendations(self, incidents: List, analysis: Dict) -> List[str]:
        recommendations = []
        
        if incidents:
            recommendations.append("🗣️ Implement multilingual meeting support")
            recommendations.append("📚 Provide communication skills training")
        
        if analysis["overall_bias_risk"] > 0.3:
            recommendations.append("⚖️ Review promotion criteria for fairness")
            recommendations.append("👥 Implement bias awareness training")
        
        recommendations.append("📊 Regular bias auditing and monitoring")
        
        return recommendations

def demo_cultural_bias_detector():
    print("🔍 Cultural Bias Detector Demo")
    print("=" * 40)
    
    detector = CulturalBiasDetector()
    
    # Add diverse employees
    employees = [
        Employee("E1", "Rajesh Kumar", "North India", "Hindi", 35, "Male", "Engineering", 5, 8),
        Employee("E2", "Priya Menon", "South India", "Malayalam", 32, "Female", "Engineering", 4, 6),
        Employee("E3", "Amit Patel", "West India", "Gujarati", 28, "Male", "Engineering", 3, 4),
        Employee("E4", "Sneha Singh", "North India", "Hindi", 26, "Female", "Engineering", 2, 2),
    ]
    
    # Simulate bias - Hindi speakers have higher participation
    employees[0].meeting_participation_score = 0.8  # Hindi speaker
    employees[3].meeting_participation_score = 0.7  # Hindi speaker
    employees[1].meeting_participation_score = 0.4  # Malayalam speaker
    employees[2].meeting_participation_score = 0.3  # Gujarati speaker
    
    for emp in employees:
        detector.add_employee(emp)
    
    report = detector.generate_bias_report()
    
    print(f"\n📊 Bias Analysis Report:")
    print(f"Total Employees: {report['total_employees']}")
    print(f"Language Bias Detected: {report['language_bias_detected']}")
    print(f"Overall Bias Risk: {report['promotion_fairness']['overall_bias_risk']:.2f}")
    
    print(f"\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"   • {rec}")

if __name__ == "__main__":
    demo_cultural_bias_detector()
#!/usr/bin/env python3
"""
Knowledge Sharing Platform - Episode 3: Human Factor in Tech
============================================================

Indian IT companies mein knowledge sharing aur mentorship tracking.
Senior-junior relationships, domain expertise sharing, aur learning paths.

Features:
- Mentorship relationship tracking
- Knowledge gap identification
- Expertise mapping
- Learning path recommendations
- Cross-team knowledge transfer
- Cultural knowledge preservation
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
import statistics

class ExpertiseLevel(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4

class KnowledgeType(Enum):
    TECHNICAL = "technical"
    DOMAIN = "domain"
    PROCESS = "process"
    CULTURAL = "cultural"
    SOFT_SKILLS = "soft_skills"

@dataclass
class KnowledgeItem:
    id: str
    title: str
    content: str
    knowledge_type: KnowledgeType
    domain: str
    tags: List[str]
    author_id: str
    created_at: datetime
    difficulty_level: ExpertiseLevel
    views: int = 0
    usefulness_score: float = 0.0

@dataclass
class Employee:
    id: str
    name: str
    expertise_areas: Dict[str, ExpertiseLevel]
    mentoring_capacity: int
    learning_goals: List[str]
    knowledge_contributions: int = 0

class KnowledgeSharingPlatform:
    def __init__(self):
        self.employees: Dict[str, Employee] = {}
        self.knowledge_items: List[KnowledgeItem] = []
        self.mentorship_relationships: Dict[str, List[str]] = defaultdict(list)
    
    def add_employee(self, employee: Employee):
        self.employees[employee.id] = employee
        print(f"👤 Added {employee.name} with {len(employee.expertise_areas)} expertise areas")
    
    def create_knowledge_item(self, item: KnowledgeItem):
        self.knowledge_items.append(item)
        self.employees[item.author_id].knowledge_contributions += 1
        print(f"📚 Created knowledge item: {item.title}")
    
    def find_mentors(self, learning_domain: str, expertise_required: ExpertiseLevel) -> List[str]:
        """Find potential mentors for a domain"""
        mentors = []
        for emp_id, employee in self.employees.items():
            if (learning_domain in employee.expertise_areas and 
                employee.expertise_areas[learning_domain].value >= expertise_required.value and
                len(self.mentorship_relationships[emp_id]) < employee.mentoring_capacity):
                mentors.append(emp_id)
        return mentors
    
    def establish_mentorship(self, mentor_id: str, mentee_id: str):
        """Establish mentorship relationship"""
        self.mentorship_relationships[mentor_id].append(mentee_id)
        print(f"🤝 Mentorship established: {mentor_id} -> {mentee_id}")
    
    def analyze_knowledge_gaps(self) -> Dict:
        """Identify knowledge gaps in the organization"""
        domain_expertise = defaultdict(list)
        
        for employee in self.employees.values():
            for domain, level in employee.expertise_areas.items():
                domain_expertise[domain].append(level.value)
        
        gaps = {}
        for domain, levels in domain_expertise.items():
            if levels:
                avg_level = statistics.mean(levels)
                expert_count = len([l for l in levels if l >= 3])  # Advanced or Expert
                
                if avg_level < 2.5 or expert_count == 0:
                    gaps[domain] = {
                        "average_expertise": avg_level,
                        "expert_count": expert_count,
                        "priority": "high" if expert_count == 0 else "medium"
                    }
        
        return gaps
    
    def recommend_learning_paths(self, employee_id: str) -> List[Dict]:
        """Recommend learning paths for employee"""
        employee = self.employees[employee_id]
        recommendations = []
        
        for goal in employee.learning_goals:
            # Find knowledge items related to goal
            relevant_items = [item for item in self.knowledge_items 
                            if goal.lower() in item.title.lower() or 
                               goal.lower() in ' '.join(item.tags).lower()]
            
            # Find mentors
            potential_mentors = self.find_mentors(goal, ExpertiseLevel.ADVANCED)
            
            recommendations.append({
                "learning_goal": goal,
                "knowledge_resources": len(relevant_items),
                "available_mentors": len(potential_mentors),
                "recommended_mentor": potential_mentors[0] if potential_mentors else None
            })
        
        return recommendations

def demo_knowledge_sharing_platform():
    print("📚 Knowledge Sharing Platform Demo")
    print("=" * 40)
    
    platform = KnowledgeSharingPlatform()
    
    # Add employees with different expertise
    employees = [
        Employee(
            "E1", "Rajesh Kumar",
            {"python": ExpertiseLevel.EXPERT, "microservices": ExpertiseLevel.ADVANCED},
            2, ["leadership", "system_design"]
        ),
        Employee(
            "E2", "Priya Menon", 
            {"react": ExpertiseLevel.ADVANCED, "ui_design": ExpertiseLevel.EXPERT},
            1, ["backend_development"]
        ),
        Employee(
            "E3", "Amit Patel",
            {"java": ExpertiseLevel.INTERMEDIATE, "python": ExpertiseLevel.BEGINNER},
            0, ["python", "microservices"]
        )
    ]
    
    for emp in employees:
        platform.add_employee(emp)
    
    # Create knowledge items
    knowledge_items = [
        KnowledgeItem(
            "K1", "Python Best Practices for Microservices",
            "Comprehensive guide to Python microservices...",
            KnowledgeType.TECHNICAL, "backend", ["python", "microservices"],
            "E1", datetime.now(), ExpertiseLevel.ADVANCED
        ),
        KnowledgeItem(
            "K2", "React Component Design Patterns", 
            "Common patterns for React components...",
            KnowledgeType.TECHNICAL, "frontend", ["react", "ui"],
            "E2", datetime.now(), ExpertiseLevel.INTERMEDIATE
        )
    ]
    
    for item in knowledge_items:
        platform.create_knowledge_item(item)
    
    # Analyze knowledge gaps
    gaps = platform.analyze_knowledge_gaps()
    print(f"\n🔍 Knowledge Gaps Analysis:")
    for domain, gap_info in gaps.items():
        print(f"   {domain}: Avg level {gap_info['average_expertise']:.1f}, "
              f"Experts: {gap_info['expert_count']}, Priority: {gap_info['priority']}")
    
    # Find mentors and establish mentorship
    mentors = platform.find_mentors("python", ExpertiseLevel.ADVANCED)
    print(f"\n🤝 Available Python mentors: {mentors}")
    
    if mentors:
        platform.establish_mentorship(mentors[0], "E3")
    
    # Recommend learning paths
    recommendations = platform.recommend_learning_paths("E3")
    print(f"\n📈 Learning Recommendations for Amit:")
    for rec in recommendations:
        print(f"   Goal: {rec['learning_goal']}")
        print(f"   Resources: {rec['knowledge_resources']}, Mentors: {rec['available_mentors']}")
        if rec['recommended_mentor']:
            print(f"   Recommended Mentor: {rec['recommended_mentor']}")

if __name__ == "__main__":
    demo_knowledge_sharing_platform()
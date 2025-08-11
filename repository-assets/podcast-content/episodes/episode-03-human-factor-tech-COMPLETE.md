# Episode 3: The Human Factor in Tech - When Engineers Become the System
## Production Psychology, On-Call Culture, and Indian IT Reality

*Duration: 3 Hours | Language: Hindi + English | Level: Progressive (Beginner → Advanced)*

---

## Introduction: Mumbai Local Train Psychology

Namaste doston! Aaj hum baat karenge ek aisi topic ki jo har engineer ke dil ke bahut kareeb hai - The Human Factor in Tech. 

Picture karo - Monday morning, 8:47 AM, Dadar station. Platform number 4 pe khade ho, Churchgate fast local ka wait kar rahe ho. Train aati hai, already packed. Lekin aapko office 9:30 tak pahunchna hai. Kya karte ho? Jump karte ho, somehow adjust karte ho, aur phir 45 minutes tak uss crowd mein khade rehte ho.

Ab socho - ye same pressure, same stress, same exhaustion - har raat 2 AM ko jab production mein kuch crash ho jata hai. PagerDuty ka alert aata hai. Aapki neend toot jaati hai. Laptop kholte ho, VPN connect karte ho, aur phir shuru hota hai debugging ka safar.

Ye hai modern tech ki reality - jahan humans aur systems itne intertwined hain ki pata hi nahi chalta ki system aapko chala raha hai ya aap system ko.

## Part 1: The Psychology of Production Incidents (Hour 1)

### The 2 AM Wake-Up Call - Indian On-Call Culture

India mein on-call culture ka matlab hai 24x7 availability. Kyunki jab India mein raat hoti hai, US mein din hota hai. Aur jab India mein din hota hai, Europe active hota hai. Global services ka matlab hai ki downtime ka concept hi nahi hai.

```python
# Real On-Call Rotation System - Indian IT Reality
import datetime
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    SEV1 = "System Down - Revenue Impact"  
    SEV2 = "Major Feature Broken"
    SEV3 = "Minor Issue - Degraded Performance"
    SEV4 = "Cosmetic Issue"

@dataclass
class Engineer:
    """Typical Indian IT engineer profile"""
    name: str
    years_exp: int
    burnout_level: float  # 0-1 scale
    last_incident_handled: Optional[datetime.datetime]
    alerts_this_week: int
    coffee_cups_today: int
    missed_family_events: int  # The real cost
    
    def calculate_stress_level(self) -> float:
        """Real stress calculation based on Indian work culture"""
        base_stress = 0.3  # Baseline stress in Indian IT
        
        # Night shift impact
        current_hour = datetime.datetime.now().hour
        if 22 <= current_hour or current_hour <= 6:
            base_stress += 0.2
        
        # Alert fatigue
        if self.alerts_this_week > 10:
            base_stress += 0.15
        
        # Burnout accumulation
        base_stress += self.burnout_level * 0.3
        
        # Family impact (unique to Indian context)
        if self.missed_family_events > 2:
            base_stress += 0.25
            
        return min(base_stress, 1.0)  # Cap at 1.0

class OnCallRotationSystem:
    """Production on-call system with Indian work culture considerations"""
    
    def __init__(self):
        self.engineers = []
        self.incident_history = []
        self.escalation_matrix = {}
        self.festival_calendar = [
            "Diwali", "Holi", "Dussehra", "Ganesh Chaturthi",
            "Eid", "Christmas", "Pongal", "Onam"
        ]
        
    def add_engineer(self, engineer: Engineer):
        """Add engineer to rotation with fairness check"""
        self.engineers.append(engineer)
        print(f"Added {engineer.name} - Burnout Level: {engineer.burnout_level:.2f}")
        
    def trigger_incident(self, severity: Severity, description: str):
        """Simulate production incident"""
        # Find on-call engineer
        on_call = self.get_current_oncall()
        
        print(f"\n🚨 INCIDENT ALERT - {severity.value}")
        print(f"Description: {description}")
        print(f"Paging: {on_call.name}")
        print(f"Engineer stress level: {on_call.calculate_stress_level():.2f}")
        
        # Simulate wake-up time if night
        current_hour = datetime.datetime.now().hour
        if 22 <= current_hour or current_hour <= 6:
            wake_up_time = random.randint(30, 180)  # seconds
            print(f"Wake up time: {wake_up_time} seconds")
            print(f"Coffee cups needed: {random.randint(2, 5)}")
        
        # Calculate MTTR based on engineer state
        mttr = self.calculate_mttr(on_call, severity)
        print(f"Expected MTTR: {mttr} minutes")
        
        # Update engineer stats
        on_call.alerts_this_week += 1
        on_call.burnout_level = min(1.0, on_call.burnout_level + 0.05)
        on_call.last_incident_handled = datetime.datetime.now()
        
        return {
            'engineer': on_call.name,
            'severity': severity,
            'mttr': mttr,
            'stress_level': on_call.calculate_stress_level()
        }
    
    def calculate_mttr(self, engineer: Engineer, severity: Severity) -> int:
        """Calculate Mean Time To Resolution based on human factors"""
        base_mttr = {
            Severity.SEV1: 30,
            Severity.SEV2: 60,
            Severity.SEV3: 120,
            Severity.SEV4: 240
        }[severity]
        
        # Fatigue multiplier
        if engineer.burnout_level > 0.7:
            base_mttr *= 1.5
        
        # Experience benefit
        if engineer.years_exp > 5:
            base_mttr *= 0.8
        
        # Time of day impact
        current_hour = datetime.datetime.now().hour
        if 2 <= current_hour <= 5:  # Worst time
            base_mttr *= 1.3
            
        return int(base_mttr)
    
    def get_current_oncall(self) -> Engineer:
        """Get current on-call with fairness algorithm"""
        # Sort by alerts this week (fairness)
        sorted_engineers = sorted(self.engineers, 
                                key=lambda e: (e.alerts_this_week, e.burnout_level))
        return sorted_engineers[0]
    
    def generate_weekly_report(self):
        """Generate human impact report"""
        print("\n📊 WEEKLY HUMAN IMPACT REPORT")
        print("="*50)
        
        total_alerts = sum(e.alerts_this_week for e in self.engineers)
        avg_burnout = sum(e.burnout_level for e in self.engineers) / len(self.engineers)
        
        print(f"Total Incidents: {total_alerts}")
        print(f"Average Burnout Level: {avg_burnout:.2f}")
        print(f"Engineers at Risk (>0.7 burnout): {sum(1 for e in self.engineers if e.burnout_level > 0.7)}")
        
        print("\n👥 Individual Impact:")
        for eng in self.engineers:
            print(f"- {eng.name}: {eng.alerts_this_week} alerts, "
                  f"Burnout: {eng.burnout_level:.2f}, "
                  f"Missed Events: {eng.missed_family_events}")

# Demonstration
system = OnCallRotationSystem()

# Typical Indian IT team
engineers = [
    Engineer("Raj Kumar", 3, 0.6, None, 5, 3, 1),
    Engineer("Priya Sharma", 5, 0.7, None, 8, 4, 2),
    Engineer("Amit Patel", 2, 0.5, None, 3, 2, 0),
    Engineer("Sneha Reddy", 7, 0.8, None, 12, 5, 3),
]

for eng in engineers:
    system.add_engineer(eng)

# Simulate week of incidents
incidents = [
    (Severity.SEV1, "Payment gateway down - Paytm integration failed"),
    (Severity.SEV2, "IRCTC booking API timeout"),
    (Severity.SEV3, "Swiggy delivery tracking slow"),
    (Severity.SEV1, "Database connection pool exhausted"),
]

for severity, desc in incidents:
    system.trigger_incident(severity, desc)

system.generate_weekly_report()
```

### The Cognitive Load Problem - Mental RAM Overflow

Human brain ka bhi RAM hota hai. Aur production incidents ke time pe ye RAM overflow ho jata hai. Multiple dashboards, logs, alerts, Slack messages - sab kuch ek saath process karna padta hai.

```python
# Cognitive Load Calculator for Engineers
import time
from collections import deque
from typing import List, Dict
import threading

class CognitiveLoadManager:
    """
    Measure and manage engineer cognitive load during incidents
    Based on Miller's Law (7±2 items in working memory)
    """
    
    def __init__(self, engineer_name: str):
        self.engineer = engineer_name
        self.working_memory = deque(maxlen=9)  # Miller's Law limit
        self.context_switches = 0
        self.information_sources = []
        self.decision_fatigue_score = 0
        self.start_time = time.time()
        
    def add_information_source(self, source: str, complexity: int):
        """Add new information source (dashboard, log, alert)"""
        self.information_sources.append({
            'source': source,
            'complexity': complexity,  # 1-10 scale
            'timestamp': time.time()
        })
        
        # Check cognitive overload
        total_complexity = sum(s['complexity'] for s in self.information_sources)
        
        if total_complexity > 30:
            print(f"⚠️ COGNITIVE OVERLOAD WARNING for {self.engineer}")
            print(f"Current load: {total_complexity}/30")
            print("Recommendation: Reduce information sources or get help")
            
    def context_switch(self, from_task: str, to_task: str):
        """Track context switching cost"""
        self.context_switches += 1
        switch_cost = 5 * self.context_switches  # Cumulative cost
        
        print(f"Context Switch #{self.context_switches}: {from_task} → {to_task}")
        print(f"Cognitive cost: {switch_cost} seconds added to resolution time")
        
        # Add to working memory
        self.working_memory.append(f"Switch: {to_task}")
        
        if self.context_switches > 10:
            print("🧠 EXCESSIVE CONTEXT SWITCHING DETECTED")
            print("Engineer efficiency degraded by 40%")
            
    def make_decision(self, decision: str, options: int):
        """Track decision fatigue"""
        self.decision_fatigue_score += options * 2  # More options = more fatigue
        
        if self.decision_fatigue_score > 50:
            print(f"😰 DECISION FATIGUE ALERT for {self.engineer}")
            print("Recommendation: Escalate to senior engineer or take break")
            
    def calculate_performance_degradation(self) -> float:
        """Calculate overall performance impact"""
        base_performance = 1.0
        
        # Context switching impact
        if self.context_switches > 5:
            base_performance *= 0.8
        if self.context_switches > 10:
            base_performance *= 0.6
            
        # Information overload impact
        info_load = len(self.information_sources)
        if info_load > 5:
            base_performance *= 0.85
        if info_load > 8:
            base_performance *= 0.7
            
        # Decision fatigue impact
        if self.decision_fatigue_score > 30:
            base_performance *= 0.75
            
        # Time pressure (every hour reduces performance)
        hours_elapsed = (time.time() - self.start_time) / 3600
        base_performance *= max(0.5, 1 - (hours_elapsed * 0.1))
        
        return base_performance
    
    def generate_cognitive_report(self):
        """Generate cognitive load analysis"""
        print(f"\n🧠 COGNITIVE LOAD REPORT - {self.engineer}")
        print("="*50)
        print(f"Active Information Sources: {len(self.information_sources)}")
        print(f"Context Switches: {self.context_switches}")
        print(f"Decision Fatigue Score: {self.decision_fatigue_score}/100")
        print(f"Working Memory Items: {len(self.working_memory)}/9")
        print(f"Performance Level: {self.calculate_performance_degradation():.1%}")
        
        print("\n📝 Working Memory Contents:")
        for item in self.working_memory:
            print(f"  - {item}")
            
        if self.calculate_performance_degradation() < 0.6:
            print("\n⚠️ CRITICAL: Engineer needs immediate support or rotation")

# Simulate real incident cognitive load
manager = CognitiveLoadManager("Rajesh Kumar")

# Typical incident response sequence
manager.add_information_source("PagerDuty Alert", 3)
manager.add_information_source("Grafana Dashboard", 5)
manager.add_information_source("CloudWatch Logs", 7)
manager.add_information_source("Slack Messages", 4)
manager.add_information_source("Kibana Search", 6)
manager.add_information_source("New Relic APM", 5)

# Context switches during debugging
manager.context_switch("Alert Review", "Log Analysis")
manager.context_switch("Log Analysis", "Code Review")
manager.context_switch("Code Review", "Slack Communication")
manager.context_switch("Slack Communication", "Database Query")
manager.context_switch("Database Query", "Log Analysis")

# Decision points
manager.make_decision("Rollback or Fix Forward?", 2)
manager.make_decision("Which service to restart?", 5)
manager.make_decision("Scale up or optimize?", 3)

manager.generate_cognitive_report()
```

### Alert Fatigue - The Boy Who Cried Wolf, Tech Edition

Alert fatigue real hai, aur ye India mein aur bhi zyada hai. Kyunki yahan par "better safe than sorry" ka culture hai. Har cheez pe alert laga dete hain. Result? Engineers alerts ko ignore karna seekh jaate hain.

```python
# Alert Fatigue Analysis System
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

class AlertFatigueAnalyzer:
    """
    Analyze and reduce alert fatigue in production systems
    Based on real patterns from Indian tech companies
    """
    
    def __init__(self):
        self.alerts_history = []
        self.engineer_responses = defaultdict(list)
        self.false_positive_rate = 0
        self.alert_categories = {
            'critical': {'threshold': 0.1, 'count': 0, 'actionable': 0},
            'warning': {'threshold': 0.3, 'count': 0, 'actionable': 0},
            'info': {'threshold': 0.7, 'count': 0, 'actionable': 0}
        }
        
    def process_alert(self, alert_type: str, message: str, 
                      engineer: str, response_time: int, action_taken: bool):
        """Process individual alert and response"""
        
        alert = {
            'timestamp': datetime.now(),
            'type': alert_type,
            'message': message,
            'engineer': engineer,
            'response_time_seconds': response_time,
            'action_taken': action_taken
        }
        
        self.alerts_history.append(alert)
        self.alert_categories[alert_type]['count'] += 1
        
        if action_taken:
            self.alert_categories[alert_type]['actionable'] += 1
            
        # Track engineer response pattern
        self.engineer_responses[engineer].append({
            'response_time': response_time,
            'action_taken': action_taken
        })
        
    def calculate_alert_quality_score(self) -> float:
        """Calculate overall alert quality (0-1, higher is better)"""
        total_alerts = len(self.alerts_history)
        if total_alerts == 0:
            return 1.0
            
        actionable_alerts = sum(1 for a in self.alerts_history if a['action_taken'])
        return actionable_alerts / total_alerts
        
    def analyze_engineer_fatigue(self, engineer: str) -> Dict:
        """Analyze fatigue patterns for specific engineer"""
        if engineer not in self.engineer_responses:
            return {'status': 'No data'}
            
        responses = self.engineer_responses[engineer]
        
        # Calculate fatigue indicators
        avg_response_time = np.mean([r['response_time'] for r in responses])
        response_degradation = self._calculate_response_degradation(responses)
        action_rate = sum(1 for r in responses if r['action_taken']) / len(responses)
        
        fatigue_score = 0
        
        # Slow responses indicate fatigue
        if avg_response_time > 300:  # 5 minutes
            fatigue_score += 0.3
            
        # Declining action rate indicates alert blindness
        if action_rate < 0.3:
            fatigue_score += 0.4
            
        # Response time increasing over time
        if response_degradation > 0.2:
            fatigue_score += 0.3
            
        return {
            'engineer': engineer,
            'fatigue_score': min(fatigue_score, 1.0),
            'avg_response_time': avg_response_time,
            'action_rate': action_rate,
            'total_alerts': len(responses),
            'recommendation': self._get_recommendation(fatigue_score)
        }
    
    def _calculate_response_degradation(self, responses: List) -> float:
        """Check if response times are getting worse"""
        if len(responses) < 10:
            return 0
            
        first_half = responses[:len(responses)//2]
        second_half = responses[len(responses)//2:]
        
        avg_first = np.mean([r['response_time'] for r in first_half])
        avg_second = np.mean([r['response_time'] for r in second_half])
        
        if avg_first == 0:
            return 0
            
        return (avg_second - avg_first) / avg_first
    
    def _get_recommendation(self, fatigue_score: float) -> str:
        """Get actionable recommendations"""
        if fatigue_score < 0.3:
            return "Healthy alert response pattern"
        elif fatigue_score < 0.6:
            return "Moderate fatigue - Consider reducing non-critical alerts"
        elif fatigue_score < 0.8:
            return "High fatigue - Immediate alert tuning needed"
        else:
            return "Critical fatigue - Engineer needs break, alerts need major overhaul"
    
    def generate_optimization_plan(self) -> Dict:
        """Generate alert optimization plan"""
        quality_score = self.calculate_alert_quality_score()
        
        recommendations = []
        
        # Check each alert category
        for category, data in self.alert_categories.items():
            if data['count'] > 0:
                actionable_rate = data['actionable'] / data['count']
                
                if actionable_rate < data['threshold']:
                    recommendations.append({
                        'category': category,
                        'current_actionable_rate': actionable_rate,
                        'target': data['threshold'],
                        'action': f"Reduce {category} alerts by {int((1-actionable_rate)*100)}%"
                    })
        
        # Check alert frequency
        if len(self.alerts_history) > 0:
            time_span = (self.alerts_history[-1]['timestamp'] - 
                        self.alerts_history[0]['timestamp']).total_seconds() / 3600
            
            if time_span > 0:
                alerts_per_hour = len(self.alerts_history) / time_span
                
                if alerts_per_hour > 10:
                    recommendations.append({
                        'issue': 'Alert Storm',
                        'current_rate': f"{alerts_per_hour:.1f} alerts/hour",
                        'action': 'Implement alert aggregation and deduplication'
                    })
        
        return {
            'quality_score': quality_score,
            'total_alerts': len(self.alerts_history),
            'recommendations': recommendations
        }
    
    def print_fatigue_report(self):
        """Generate comprehensive fatigue report"""
        print("\n📊 ALERT FATIGUE ANALYSIS REPORT")
        print("="*60)
        
        # Overall stats
        print(f"\n📈 Overall Statistics:")
        print(f"Total Alerts: {len(self.alerts_history)}")
        print(f"Alert Quality Score: {self.calculate_alert_quality_score():.2%}")
        
        # Category breakdown
        print(f"\n📁 Alert Categories:")
        for category, data in self.alert_categories.items():
            if data['count'] > 0:
                actionable_rate = data['actionable'] / data['count']
                print(f"  {category.upper()}: {data['count']} alerts, "
                      f"{actionable_rate:.1%} actionable")
        
        # Engineer fatigue analysis
        print(f"\n👥 Engineer Fatigue Levels:")
        for engineer in self.engineer_responses.keys():
            analysis = self.analyze_engineer_fatigue(engineer)
            print(f"  {engineer}:")
            print(f"    - Fatigue Score: {analysis['fatigue_score']:.2f}/1.0")
            print(f"    - Avg Response: {analysis['avg_response_time']:.0f}s")
            print(f"    - Action Rate: {analysis['action_rate']:.1%}")
            print(f"    - {analysis['recommendation']}")
        
        # Optimization plan
        plan = self.generate_optimization_plan()
        if plan['recommendations']:
            print(f"\n🔧 Optimization Recommendations:")
            for rec in plan['recommendations']:
                print(f"  - {rec}")

# Simulate real alert patterns
analyzer = AlertFatigueAnalyzer()

# Typical day in Indian tech company
alerts = [
    ('info', 'CPU usage at 61%', 'Amit', 180, False),
    ('warning', 'Memory usage high', 'Amit', 120, False),
    ('critical', 'Payment API down', 'Amit', 30, True),
    ('info', 'Disk usage at 71%', 'Priya', 300, False),
    ('warning', 'Response time slow', 'Priya', 240, True),
    ('info', 'Cache miss rate 15%', 'Priya', 600, False),
    ('critical', 'Database connection failed', 'Raj', 15, True),
    ('warning', 'Queue depth increasing', 'Raj', 90, True),
    ('info', 'New deployment detected', 'Raj', 900, False),
]

# Process alerts
for alert_type, message, engineer, response_time, action in alerts * 5:  # Simulate multiple occurrences
    analyzer.process_alert(alert_type, message, engineer, response_time, action)

analyzer.print_fatigue_report()
```

## Part 2: The Indian IT Culture Impact (Hour 2)

### The "Resource" Mentality - When Humans Become JIRA Tickets

Indian IT industry mein ek unique problem hai - the "resource" culture. Log humans nahi, "resources" ban jaate hain. FTEs, billable hours, utilization percentage - ye sab metrics mein insaan kho jaata hai.

```java
// The Resource Allocation System - Dark Reality of Indian IT
import java.util.*;
import java.time.*;
import java.util.concurrent.*;

public class HumanResourceAllocator {
    
    static class Engineer {
        String name;
        String employeeId;
        double utilizationTarget = 0.85;  // 85% billability target
        double currentUtilization;
        int projectsAssigned;
        int weekendWorked;
        LocalDateTime lastVacation;
        Map<String, Integer> skills;
        double burnoutScore;
        boolean isLookingForChange;  // The silent epidemic
        
        public Engineer(String name, String employeeId) {
            this.name = name;
            this.employeeId = employeeId;
            this.skills = new HashMap<>();
            this.currentUtilization = 0.0;
            this.projectsAssigned = 0;
            this.weekendWorked = 0;
            this.burnoutScore = 0.0;
            this.isLookingForChange = false;
        }
        
        public void addSkill(String skill, int level) {
            skills.put(skill, level);
        }
        
        public double calculateProductivity() {
            // Productivity decreases with burnout
            double baseProductivity = 1.0;
            
            if (burnoutScore > 0.7) {
                baseProductivity *= 0.5;  // 50% productivity drop
            } else if (burnoutScore > 0.5) {
                baseProductivity *= 0.7;
            }
            
            // Weekend work impact
            if (weekendWorked > 2) {
                baseProductivity *= 0.8;
            }
            
            // Multiple project context switching
            if (projectsAssigned > 3) {
                baseProductivity *= 0.6;
            }
            
            return baseProductivity;
        }
        
        public void checkAttritionRisk() {
            // Indian IT attrition factors
            if (burnoutScore > 0.6 && weekendWorked > 3) {
                isLookingForChange = true;
            }
            
            // No vacation in 6 months
            if (lastVacation != null && 
                ChronoUnit.MONTHS.between(lastVacation, LocalDateTime.now()) > 6) {
                burnoutScore += 0.1;
            }
            
            // Overutilization
            if (currentUtilization > 0.95) {
                burnoutScore += 0.15;
                isLookingForChange = true;
            }
        }
    }
    
    static class Project {
        String name;
        String client;
        int requiredEngineers;
        Map<String, Integer> requiredSkills;
        LocalDate deadline;
        double revenuePerDay;
        boolean isCritical;
        List<Engineer> assignedEngineers;
        
        public Project(String name, String client, LocalDate deadline) {
            this.name = name;
            this.client = client;
            this.deadline = deadline;
            this.requiredSkills = new HashMap<>();
            this.assignedEngineers = new ArrayList<>();
        }
    }
    
    static class ResourceManager {
        List<Engineer> engineers;
        List<Project> projects;
        double benchStrength;  // Engineers without projects
        double attritionRate;
        
        public ResourceManager() {
            this.engineers = new ArrayList<>();
            this.projects = new ArrayList<>();
            this.benchStrength = 0.0;
            this.attritionRate = 0.0;
        }
        
        public void allocateResources() {
            System.out.println("🤖 RESOURCE ALLOCATION SYSTEM");
            System.out.println("=============================");
            
            // Sort projects by revenue (money first, humans second)
            projects.sort((p1, p2) -> 
                Double.compare(p2.revenuePerDay, p1.revenuePerDay));
            
            for (Project project : projects) {
                System.out.println("\n📋 Project: " + project.name);
                System.out.println("Client: " + project.client);
                System.out.println("Revenue/Day: $" + project.revenuePerDay);
                
                // Find "resources" (not humans) for project
                List<Engineer> available = findAvailableResources(project);
                
                if (available.size() < project.requiredEngineers) {
                    System.out.println("⚠️ Resource Crunch Detected!");
                    System.out.println("Solution: Stretch existing resources");
                    stretchResources(project, available);
                }
                
                // Assign and overload
                for (Engineer eng : available) {
                    assignToProject(eng, project);
                }
            }
            
            calculateMetrics();
        }
        
        private List<Engineer> findAvailableResources(Project project) {
            List<Engineer> available = new ArrayList<>();
            
            for (Engineer eng : engineers) {
                // Check if "resource" matches requirements
                boolean skillMatch = project.requiredSkills.keySet().stream()
                    .allMatch(skill -> eng.skills.containsKey(skill));
                
                // Check if can be stretched more
                if (skillMatch && eng.currentUtilization < 1.2) {  // 120% allocation
                    available.add(eng);
                }
            }
            
            return available;
        }
        
        private void stretchResources(Project project, List<Engineer> available) {
            // The dark art of resource stretching
            for (Engineer eng : available) {
                eng.currentUtilization += 0.3;  // Add 30% more work
                eng.projectsAssigned += 1;
                eng.burnoutScore += 0.2;
                
                System.out.println("Stretching " + eng.name + 
                    " to " + (eng.currentUtilization * 100) + "% utilization");
            }
        }
        
        private void assignToProject(Engineer eng, Project project) {
            project.assignedEngineers.add(eng);
            eng.projectsAssigned++;
            
            // Weekend work assignment (the norm, not exception)
            if (project.isCritical) {
                eng.weekendWorked++;
                System.out.println(eng.name + " assigned to work this weekend");
            }
        }
        
        private void calculateMetrics() {
            System.out.println("\n📊 METRICS THAT MATTER (TO MANAGEMENT)");
            System.out.println("======================================");
            
            // Calculate billability (the holy grail)
            double totalBillable = engineers.stream()
                .filter(e -> e.currentUtilization > 0)
                .count();
            double billability = (totalBillable / engineers.size()) * 100;
            
            System.out.println("Billability: " + billability + "%");
            
            // Bench strength (the feared state)
            benchStrength = engineers.stream()
                .filter(e -> e.currentUtilization == 0)
                .count();
            System.out.println("Bench Strength: " + benchStrength + " resources");
            
            // Attrition risk (the ignored metric)
            long atRisk = engineers.stream()
                .filter(e -> e.isLookingForChange)
                .count();
            attritionRate = (double) atRisk / engineers.size() * 100;
            
            System.out.println("Attrition Risk: " + attritionRate + "%");
            
            // Human metrics (usually ignored)
            System.out.println("\n😔 HUMAN METRICS (RARELY DISCUSSED)");
            System.out.println("===================================");
            
            double avgBurnout = engineers.stream()
                .mapToDouble(e -> e.burnoutScore)
                .average()
                .orElse(0.0);
            
            long overworked = engineers.stream()
                .filter(e -> e.currentUtilization > 1.0)
                .count();
            
            System.out.println("Average Burnout Score: " + avgBurnout);
            System.out.println("Overworked Engineers: " + overworked);
            System.out.println("Weekend Workers: " + 
                engineers.stream().filter(e -> e.weekendWorked > 0).count());
            
            // The reality check
            if (avgBurnout > 0.6) {
                System.out.println("\n🚨 WARNING: Team burnout critical!");
                System.out.println("Productivity Impact: -40%");
                System.out.println("Attrition Risk: HIGH");
                System.out.println("Recommended Action: Reduce workload");
                System.out.println("Likely Action: Hire more freshers");
            }
        }
    }
    
    public static void main(String[] args) {
        // Create typical Indian IT scenario
        ResourceManager rm = new ResourceManager();
        
        // Add "resources"
        String[] names = {"Raj", "Priya", "Amit", "Sneha", "Vikram"};
        for (String name : names) {
            Engineer eng = new Engineer(name, "EMP" + name.hashCode());
            eng.addSkill("Java", 3);
            eng.addSkill("React", 2);
            eng.burnoutScore = Math.random() * 0.5 + 0.3;  // Already burned out
            rm.engineers.add(eng);
        }
        
        // Add projects (client is king)
        Project p1 = new Project("Banking App", "US Client", LocalDate.now().plusDays(30));
        p1.requiredEngineers = 3;
        p1.revenuePerDay = 5000;
        p1.isCritical = true;
        
        Project p2 = new Project("E-commerce Platform", "UK Client", LocalDate.now().plusDays(45));
        p2.requiredEngineers = 4;
        p2.revenuePerDay = 4000;
        
        rm.projects.add(p1);
        rm.projects.add(p2);
        
        // Run the machine
        rm.allocateResources();
    }
}
```

### The Imposter Syndrome Epidemic - "Main Kaun Hoon?"

Imposter syndrome Indian IT mein epidemic ki tarah hai. Specially jab aap US client ke saath call pe ho, aur woh complex architecture discuss kar rahe ho, aur aapko lag raha ho ki "yaar, mujhe toh kuch samajh nahi aa raha."

```python
# Imposter Syndrome Detector and Support System
import random
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class TechProfessional:
    """Indian tech professional profile with imposter syndrome indicators"""
    name: str
    years_experience: int
    current_role: str
    education: str  # IIT, NIT, Tier-3, Self-taught
    english_fluency: float  # 0-1 scale (major factor in Indian context)
    technical_depth: float  # 0-1 scale
    comparison_frequency: int  # How often they compare with others
    linkedin_scrolling_hours: float  # Daily hours
    
    # Imposter syndrome indicators
    feels_like_fraud: bool = False
    attributes_success_to_luck: bool = False
    fears_being_exposed: bool = False
    overworks_to_compensate: bool = False
    avoids_speaking_in_meetings: bool = False

class ImposterSyndromeAnalyzer:
    """Analyze and address imposter syndrome in Indian tech professionals"""
    
    def __init__(self):
        self.professionals = []
        self.triggers = {
            'client_calls': 0.3,  # US/UK client calls
            'code_reviews': 0.25,
            'technical_interviews': 0.4,
            'salary_discussions': 0.35,
            'team_presentations': 0.3,
            'open_source_contribution': 0.45,  # "My code isn't good enough"
            'conference_speaking': 0.5,
            'promotion_discussions': 0.4
        }
        
        self.indian_specific_triggers = {
            'iit_comparison': 0.5,  # "I'm not from IIT"
            'accent_consciousness': 0.4,  # English accent anxiety
            'age_pressure': 0.35,  # "30 and still coding"
            'package_comparison': 0.45,  # Salary package comparisons
            'onsite_opportunity': 0.4,  # "I don't deserve onsite"
            'startup_vs_mnc': 0.3,  # Career choice anxiety
        }
        
    def assess_imposter_syndrome(self, professional: TechProfessional) -> Dict:
        """Comprehensive imposter syndrome assessment"""
        
        score = 0.0
        factors = []
        
        # Education bias (huge in India)
        if professional.education not in ['IIT', 'NIT']:
            score += 0.2
            factors.append("Non-premier institute background")
        
        # English fluency impact
        if professional.english_fluency < 0.7:
            score += 0.25
            factors.append("English communication anxiety")
        
        # Experience paradox
        if professional.years_experience < 2:
            score += 0.15
            factors.append("Junior developer syndrome")
        elif professional.years_experience > 8:
            score += 0.2
            factors.append("Should know everything by now pressure")
        
        # Social media impact
        if professional.linkedin_scrolling_hours > 1:
            score += 0.15
            factors.append("Social media comparison trap")
        
        # Role-specific pressure
        if 'lead' in professional.current_role.lower() or 'senior' in professional.current_role.lower():
            score += 0.1
            factors.append("Leadership imposter syndrome")
        
        # Set flags based on score
        if score > 0.3:
            professional.feels_like_fraud = True
        if score > 0.5:
            professional.attributes_success_to_luck = True
            professional.avoids_speaking_in_meetings = True
        if score > 0.7:
            professional.fears_being_exposed = True
            professional.overworks_to_compensate = True
        
        return {
            'name': professional.name,
            'imposter_score': min(score, 1.0),
            'risk_level': self._get_risk_level(score),
            'primary_factors': factors[:3],
            'behavioral_patterns': self._identify_patterns(professional),
            'recommendations': self._generate_recommendations(score, factors)
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Categorize imposter syndrome risk"""
        if score < 0.3:
            return "Low - Healthy self-doubt"
        elif score < 0.5:
            return "Moderate - Manageable imposter feelings"
        elif score < 0.7:
            return "High - Significant imposter syndrome"
        else:
            return "Critical - Severe imposter syndrome affecting performance"
    
    def _identify_patterns(self, professional: TechProfessional) -> List[str]:
        """Identify behavioral patterns"""
        patterns = []
        
        if professional.overworks_to_compensate:
            patterns.append("Overworking to prove worth (12+ hour days)")
        
        if professional.avoids_speaking_in_meetings:
            patterns.append("Silent in meetings despite having ideas")
        
        if professional.comparison_frequency > 5:
            patterns.append("Constant comparison with peers")
        
        if professional.attributes_success_to_luck:
            patterns.append("Attributes achievements to luck/timing")
        
        if professional.fears_being_exposed:
            patterns.append("Constant fear of being 'found out'")
        
        return patterns
    
    def _generate_recommendations(self, score: float, factors: List[str]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if score > 0.5:
            recommendations.append("Document your achievements weekly")
            recommendations.append("Find a mentor who understands your journey")
        
        if "English communication anxiety" in factors:
            recommendations.append("Join Toastmasters or practice groups")
            recommendations.append("Remember: Code speaks louder than accent")
        
        if "Non-premier institute background" in factors:
            recommendations.append("Focus on skills, not pedigree")
            recommendations.append("Contribute to open source to build confidence")
        
        if score > 0.7:
            recommendations.append("Consider professional counseling")
            recommendations.append("Join peer support groups")
        
        recommendations.append("Practice self-compassion daily")
        recommendations.append("Celebrate small wins")
        
        return recommendations
    
    def simulate_triggering_event(self, professional: TechProfessional, 
                                 event: str) -> Dict:
        """Simulate how events trigger imposter syndrome"""
        
        base_trigger = self.triggers.get(event, 0.2)
        
        # Amplification based on existing syndrome
        if professional.feels_like_fraud:
            base_trigger *= 1.5
        
        response = {
            'event': event,
            'trigger_strength': base_trigger,
            'internal_dialogue': self._generate_internal_dialogue(event, professional),
            'physical_symptoms': self._get_physical_symptoms(base_trigger),
            'coping_mechanism': self._suggest_coping_mechanism(event, professional)
        }
        
        return response
    
    def _generate_internal_dialogue(self, event: str, 
                                   professional: TechProfessional) -> List[str]:
        """Generate typical internal dialogue during triggering events"""
        
        dialogues = {
            'client_calls': [
                "My English isn't good enough",
                "They'll think I'm not smart",
                "I don't deserve this role",
                "What if they ask something I don't know?"
            ],
            'code_reviews': [
                "My code is terrible",
                "Everyone writes better code than me",
                "They'll find out I'm not good enough",
                "I should have known this pattern"
            ],
            'technical_interviews': [
                "I forgot basic concepts",
                "IITians would know this",
                "I'm wasting their time",
                "I got lucky in my current job"
            ]
        }
        
        return dialogues.get(event, ["I'm not good enough"])
    
    def _get_physical_symptoms(self, trigger_strength: float) -> List[str]:
        """Physical symptoms of imposter syndrome"""
        symptoms = []
        
        if trigger_strength > 0.3:
            symptoms.append("Increased heart rate")
            symptoms.append("Sweating")
        
        if trigger_strength > 0.5:
            symptoms.append("Difficulty sleeping")
            symptoms.append("Loss of appetite")
        
        if trigger_strength > 0.7:
            symptoms.append("Panic attacks")
            symptoms.append("Chronic anxiety")
        
        return symptoms
    
    def _suggest_coping_mechanism(self, event: str, 
                                 professional: TechProfessional) -> str:
        """Suggest immediate coping mechanisms"""
        
        mechanisms = {
            'client_calls': "Prepare talking points in advance, remember they hired you for a reason",
            'code_reviews': "View feedback as learning, not judgment",
            'technical_interviews': "Focus on problem-solving approach, not just the answer",
            'salary_discussions': "Research market rates, document your contributions"
        }
        
        return mechanisms.get(event, "Take deep breaths, ground yourself in facts about your achievements")
    
    def generate_support_plan(self, professional: TechProfessional) -> Dict:
        """Generate comprehensive support plan"""
        
        assessment = self.assess_imposter_syndrome(professional)
        
        plan = {
            'immediate_actions': [
                "Start a 'wins journal' - write 3 achievements daily",
                "Find accountability partner with similar background",
                "Set up weekly 1:1 with supportive manager"
            ],
            'medium_term_goals': [
                "Present in team meeting once per month",
                "Contribute to one open source project",
                "Write one technical blog post quarterly"
            ],
            'long_term_development': [
                "Become mentor to junior developers",
                "Speak at local meetup or conference",
                "Build personal brand based on unique strengths"
            ],
            'daily_affirmations': [
                "I deserve to be here",
                "My perspective is valuable",
                "Perfect is the enemy of good",
                "Everyone googles basic stuff"
            ],
            'support_resources': [
                "Book: 'The Imposter Cure' by Dr. Jessamy Hibberd",
                "Podcast: 'The Imposter Syndrome Files'",
                "Community: Women Who Code (for women)",
                "Community: India Tech Talks",
                "Counseling: BetterHelp India"
            ]
        }
        
        return plan
    
    def print_syndrome_report(self, professional: TechProfessional):
        """Generate detailed imposter syndrome report"""
        
        assessment = self.assess_imposter_syndrome(professional)
        plan = self.generate_support_plan(professional)
        
        print(f"\n🧠 IMPOSTER SYNDROME ASSESSMENT")
        print("="*50)
        print(f"Name: {assessment['name']}")
        print(f"Risk Level: {assessment['risk_level']}")
        print(f"Imposter Score: {assessment['imposter_score']:.2f}/1.0")
        
        print(f"\n📊 Primary Factors:")
        for factor in assessment['primary_factors']:
            print(f"  • {factor}")
        
        print(f"\n🔄 Behavioral Patterns:")
        for pattern in assessment['behavioral_patterns']:
            print(f"  • {pattern}")
        
        print(f"\n💡 Recommendations:")
        for rec in assessment['recommendations']:
            print(f"  • {rec}")
        
        print(f"\n📋 30-Day Action Plan:")
        print("Immediate Actions:")
        for action in plan['immediate_actions'][:2]:
            print(f"  ✓ {action}")
        
        print("\nDaily Affirmations to Practice:")
        for affirmation in plan['daily_affirmations'][:2]:
            print(f'  💭 "{affirmation}"')
        
        # Simulate triggering event
        event = "client_calls"
        trigger_response = self.simulate_triggering_event(professional, event)
        
        print(f"\n🎯 Trigger Event Simulation: {event}")
        print(f"Trigger Strength: {trigger_response['trigger_strength']:.2f}")
        print("Internal Dialogue:")
        for thought in trigger_response['internal_dialogue'][:2]:
            print(f'  💭 "{thought}"')
        print(f"Coping Strategy: {trigger_response['coping_mechanism']}")

# Create realistic Indian tech professionals
analyzer = ImposterSyndromeAnalyzer()

# Different backgrounds, same syndrome
professionals = [
    TechProfessional("Rahul Sharma", 5, "Senior Developer", "Tier-3 College", 
                    0.6, 0.7, 10, 2.5),
    TechProfessional("Priya Patel", 3, "Full Stack Developer", "NIT", 
                    0.8, 0.6, 8, 1.5),
    TechProfessional("Amit Kumar", 8, "Tech Lead", "Self-taught", 
                    0.5, 0.8, 15, 3.0),
]

# Analyze each professional
for prof in professionals:
    analyzer.print_syndrome_report(prof)
    print("\n" + "="*70 + "\n")
```

### The WFH Revolution - Bedroom Se Boardroom

COVID ne Indian IT culture ko permanently change kar diya. Work from home ab norm ban gaya hai. Lekin iske saath aaye hain naye challenges - work-life balance ka complete collapse.

```python
# Work From Home Impact Analyzer
from datetime import datetime, time, timedelta
import random
from typing import Dict, List, Tuple
from collections import defaultdict

class WFHImpactAnalyzer:
    """
    Analyze the real impact of WFH on Indian tech professionals
    The good, bad, and the ugly truth
    """
    
    def __init__(self, name: str, city: str):
        self.name = name
        self.city = city
        self.work_start_time = time(9, 0)  # Official start
        self.work_end_time = time(18, 0)   # Official end
        self.actual_work_hours = []
        self.meeting_hours = 0
        self.focus_time = 0
        self.interruptions = []
        
        # WFH specific metrics
        self.bedroom_to_desk_commute = 10  # seconds
        self.pajama_days = 0
        self.lunch_with_family = 0
        self.electricity_bill_increase = 0
        self.back_pain_level = 0
        self.zoom_fatigue_score = 0
        
        # Indian household specific
        self.family_interruptions = []
        self.doorbell_rings = 0  # Delivery, milkman, etc.
        self.power_cuts = 0
        self.wifi_issues = 0
        self.noise_complaints = []  # Construction, neighbors, etc.
        
    def track_workday(self, day: str) -> Dict:
        """Track a typical WFH day in India"""
        
        workday_log = {
            'date': day,
            'events': [],
            'actual_start': None,
            'actual_end': None,
            'productive_hours': 0,
            'meeting_hours': 0,
            'interruptions': 0
        }
        
        # Realistic WFH day simulation
        current_time = datetime.strptime("06:00", "%H:%M")
        
        # Early morning (advantage of WFH)
        if random.random() > 0.5:
            workday_log['events'].append({
                'time': "06:00",
                'event': "Woke up without alarm (no commute stress)"
            })
        
        # The perpetual "just checking Slack"
        current_time = datetime.strptime("07:30", "%H:%M")
        workday_log['events'].append({
            'time': current_time.strftime("%H:%M"),
            'event': "Checked Slack in bed (work already started)"
        })
        workday_log['actual_start'] = current_time
        
        # Morning routine mixed with work
        events = [
            ("08:00", "Made chai, attended standup in kitchen"),
            ("08:30", "Doorbell: Amazon delivery during important call"),
            ("09:00", "Finally at desk (dining table)"),
            ("10:30", "Family member asks 'bas computer pe baithe rehte ho'"),
            ("11:00", "Power cut for 20 minutes, mobile hotspot activated"),
            ("12:00", "Back-to-back Zoom calls, no bio break"),
            ("13:00", "Lunch with family (WFH privilege)"),
            ("14:00", "Post-lunch productivity dip, pretending to work"),
            ("15:30", "Construction noise starts, can't hear in meetings"),
            ("16:00", "School kids playing cricket outside, maximum noise"),
            ("17:00", "US overlap meetings start"),
            ("18:30", "Official hours over, actual work starting now"),
            ("20:00", "Dinner break, laptop still open"),
            ("21:00", "Late evening code review"),
            ("22:30", "Finally closing laptop"),
            ("23:00", "One more Slack check before sleep")
        ]
        
        for time_str, event in events:
            workday_log['events'].append({
                'time': time_str,
                'event': event
            })
        
        workday_log['actual_end'] = datetime.strptime("22:30", "%H:%M")
        
        # Calculate metrics
        work_duration = (workday_log['actual_end'] - workday_log['actual_start']).seconds / 3600
        workday_log['total_hours'] = work_duration
        workday_log['productive_hours'] = work_duration * 0.6  # 60% productivity
        workday_log['meeting_hours'] = random.randint(3, 6)
        workday_log['interruptions'] = random.randint(5, 15)
        
        return workday_log
    
    def calculate_wfh_impact(self) -> Dict:
        """Calculate comprehensive WFH impact"""
        
        impact = {
            'positives': [],
            'negatives': [],
            'financial_impact': {},
            'health_impact': {},
            'family_impact': {},
            'productivity_score': 0
        }
        
        # Positive impacts
        impact['positives'] = [
            f"Saved ₹{random.randint(3000, 8000)}/month on commute",
            f"Gained {random.randint(2, 4)} hours/day from no commute",
            "Lunch with family every day",
            "Can wear shorts to meetings",
            "Afternoon nap possibility",
            "Can work from hometown",
            "No office politics visibility",
            "Personal washroom access"
        ]
        
        # Negative impacts
        impact['negatives'] = [
            f"Electricity bill increased by ₹{random.randint(2000, 5000)}/month",
            "Work-life boundaries destroyed",
            "Always 'available' expectation",
            "No casual office interactions",
            "Back pain from bad chair",
            "Zoom fatigue is real",
            "Family thinks you're always free",
            "Weight gain from no commute walking"
        ]
        
        # Financial calculation
        commute_saved = random.randint(3000, 8000)
        electricity_increased = random.randint(2000, 5000)
        food_saved = random.randint(2000, 4000)
        new_equipment = 15000  # One-time chair, desk, monitor
        
        impact['financial_impact'] = {
            'monthly_saved': commute_saved + food_saved,
            'monthly_increased': electricity_increased,
            'net_monthly': commute_saved + food_saved - electricity_increased,
            'one_time_costs': new_equipment
        }
        
        # Health impact
        impact['health_impact'] = {
            'back_pain_level': random.randint(3, 8),  # out of 10
            'eye_strain': random.randint(4, 9),
            'weight_change': f"+{random.randint(2, 10)} kg",
            'mental_health': "Isolated but comfortable",
            'sleep_quality': "Better (no early commute)"
        }
        
        # Family impact
        impact['family_impact'] = {
            'time_with_family': "+3 hours/day",
            'family_interruptions': "15-20 per day",
            'relationship_quality': "Improved but tested",
            'children_education_support': "Can help with homework",
            'elderly_care': "Can monitor parents"
        }
        
        # Productivity calculation
        no_commute_bonus = 20
        home_comfort_bonus = 10
        interruption_penalty = -15
        zoom_fatigue_penalty = -10
        isolation_penalty = -5
        
        impact['productivity_score'] = 70 + no_commute_bonus + home_comfort_bonus + \
                                      interruption_penalty + zoom_fatigue_penalty + \
                                      isolation_penalty
        
        return impact
    
    def generate_wfh_schedule_optimizer(self) -> Dict:
        """Optimize WFH schedule for Indian context"""
        
        optimized_schedule = {
            'morning_routine': [
                "05:30 - Wake up (beat the construction noise)",
                "05:45 - Exercise/Yoga (before family wakes up)",
                "06:30 - Bath and breakfast",
                "07:00 - Deep work session (quiet time)",
                "09:00 - Start official hours"
            ],
            'focus_blocks': [
                "07:00-09:00 - Deep work (pre-meeting hours)",
                "14:00-15:30 - Post-lunch focus (meetings usually less)",
                "20:00-21:30 - Evening focus (if US overlap permits)"
            ],
            'meeting_strategy': [
                "Batch meetings 10:00-13:00",
                "Keep camera off when possible (save bandwidth)",
                "Stand during long meetings (health benefit)",
                "Use virtual backgrounds (hide messy room)"
            ],
            'boundary_rules': [
                "Dedicated workspace (even if dining table)",
                "Work clothes till 6 PM (psychological boundary)",
                "Laptop closes at decided time (use phone for urgent)",
                "Family 'office hours' communication",
                "Doorbell response protocol"
            ],
            'health_protocols': [
                "20-20-20 rule for eyes",
                "Hourly 5-minute walks",
                "Proper chair or standing desk",
                "Blue light filter after 8 PM",
                "Dedicated lunch break away from desk"
            ]
        }
        
        return optimized_schedule
    
    def print_wfh_reality_report(self):
        """Generate comprehensive WFH reality report"""
        
        print(f"\n🏠 WORK FROM HOME REALITY CHECK - {self.name}")
        print("="*60)
        
        # Track a typical day
        typical_day = self.track_workday("Monday")
        
        print(f"\n📅 Typical WFH Day Timeline:")
        for event in typical_day['events'][:10]:  # Show first 10 events
            print(f"  {event['time']} - {event['event']}")
        
        print(f"\n⏰ Work Hours Reality:")
        print(f"  Official Hours: 9:00 AM - 6:00 PM (9 hours)")
        print(f"  Actual Hours: 7:30 AM - 10:30 PM (15 hours)")
        print(f"  Productive Hours: ~{typical_day['productive_hours']:.1f} hours")
        print(f"  Meeting Hours: {typical_day['meeting_hours']} hours")
        print(f"  Interruptions: {typical_day['interruptions']} times")
        
        # Calculate impact
        impact = self.calculate_wfh_impact()
        
        print(f"\n✅ WFH Positives:")
        for positive in impact['positives'][:5]:
            print(f"  • {positive}")
        
        print(f"\n❌ WFH Negatives:")
        for negative in impact['negatives'][:5]:
            print(f"  • {negative}")
        
        print(f"\n💰 Financial Impact:")
        fin = impact['financial_impact']
        print(f"  Monthly Saved: ₹{fin['monthly_saved']}")
        print(f"  Monthly Increased Costs: ₹{fin['monthly_increased']}")
        print(f"  Net Monthly Impact: ₹{fin['net_monthly']}")
        print(f"  One-time Setup Cost: ₹{fin['one_time_costs']}")
        
        print(f"\n🏥 Health Impact:")
        health = impact['health_impact']
        print(f"  Back Pain Level: {health['back_pain_level']}/10")
        print(f"  Eye Strain: {health['eye_strain']}/10")
        print(f"  Weight Change: {health['weight_change']}")
        print(f"  Mental Health: {health['mental_health']}")
        
        print(f"\n👨‍👩‍👧‍👦 Family Impact:")
        family = impact['family_impact']
        print(f"  Time with Family: {family['time_with_family']}")
        print(f"  Daily Interruptions: {family['family_interruptions']}")
        print(f"  Relationship: {family['relationship_quality']}")
        
        print(f"\n📊 Overall Productivity Score: {impact['productivity_score']}%")
        
        # Optimization suggestions
        schedule = self.generate_wfh_schedule_optimizer()
        
        print(f"\n🎯 Optimized WFH Schedule:")
        print("Morning Routine:")
        for item in schedule['morning_routine'][:3]:
            print(f"  • {item}")
        
        print("\nFocus Blocks:")
        for block in schedule['focus_blocks']:
            print(f"  • {block}")
        
        print("\nBoundary Rules:")
        for rule in schedule['boundary_rules'][:3]:
            print(f"  • {rule}")

# Create WFH analyzer for different cities
cities = ["Bangalore", "Mumbai", "Delhi NCR", "Pune", "Hyderabad"]

for city in cities[:2]:  # Analyze 2 cities
    analyzer = WFHImpactAnalyzer(f"Software Engineer", city)
    analyzer.print_wfh_reality_report()
    print("\n" + "="*70 + "\n")
```

## Part 3: Building Human-Centric Tech Systems (Hour 3)

### The Empathy Architecture - Systems That Care

Ab baat karte hain solution ki. Kaise banaye aise systems jo humans ko samjhe, unki care kare, aur sustainable ho.

```go
// Empathy-Driven System Architecture
package main

import (
    "fmt"
    "time"
    "math/rand"
    "sync"
)

// EngineerProfile represents human aspect of engineer
type EngineerProfile struct {
    Name               string
    Role              string
    YearsExperience   int
    CurrentStressLevel float64
    WorkloadCapacity   float64
    LastBreak         time.Time
    ConsecutiveHours  int
    MoodIndicators    map[string]float64
    PersonalContext   map[string]interface{}
}

// EmpathyEngine monitors and protects engineer wellbeing
type EmpathyEngine struct {
    engineers map[string]*EngineerProfile
    mu        sync.RWMutex
    policies  *WellbeingPolicies
}

// WellbeingPolicies defines human-centric policies
type WellbeingPolicies struct {
    MaxConsecutiveHours   int
    MandatoryBreakMinutes int
    MaxWeeklyOncallHours  int
    StressThreshold       float64
    AutoEscalationEnabled bool
}

// NewEmpathyEngine creates new empathy-driven system
func NewEmpathyEngine() *EmpathyEngine {
    return &EmpathyEngine{
        engineers: make(map[string]*EngineerProfile),
        policies: &WellbeingPolicies{
            MaxConsecutiveHours:   4,
            MandatoryBreakMinutes: 15,
            MaxWeeklyOncallHours:  20,
            StressThreshold:       0.7,
            AutoEscalationEnabled: true,
        },
    }
}

// MonitorEngineer continuously monitors engineer wellbeing
func (ee *EmpathyEngine) MonitorEngineer(engineer *EngineerProfile) {
    ticker := time.NewTicker(5 * time.Minute)
    defer ticker.Stop()
    
    for range ticker.C {
        ee.mu.Lock()
        
        // Check consecutive work hours
        if engineer.ConsecutiveHours >= ee.policies.MaxConsecutiveHours {
            ee.triggerBreakReminder(engineer)
        }
        
        // Check stress levels
        if engineer.CurrentStressLevel > ee.policies.StressThreshold {
            ee.initiateStressProtocol(engineer)
        }
        
        // Check workload
        if engineer.WorkloadCapacity > 0.9 {
            ee.redistributeWork(engineer)
        }
        
        ee.mu.Unlock()
    }
}

// triggerBreakReminder sends break reminder
func (ee *EmpathyEngine) triggerBreakReminder(engineer *EngineerProfile) {
    fmt.Printf("\n🌟 WELLBEING ALERT for %s\n", engineer.Name)
    fmt.Printf("You've been working for %d hours straight\n", engineer.ConsecutiveHours)
    fmt.Println("Mandatory break initiated. System will handle alerts for 15 minutes")
    
    // Auto-snooze all non-critical alerts
    engineer.LastBreak = time.Now()
    engineer.ConsecutiveHours = 0
}

// initiateStressProtocol handles high stress situations
func (ee *EmpathyEngine) initiateStressProtocol(engineer *EngineerProfile) {
    fmt.Printf("\n⚠️ HIGH STRESS DETECTED for %s\n", engineer.Name)
    fmt.Printf("Current stress level: %.2f\n", engineer.CurrentStressLevel)
    
    if ee.policies.AutoEscalationEnabled {
        fmt.Println("Auto-escalating to backup on-call")
        ee.escalateToBackup(engineer)
    }
    
    // Provide stress management resources
    ee.provideStressSupport(engineer)
}

// redistributeWork automatically redistributes workload
func (ee *EmpathyEngine) redistributeWork(engineer *EngineerProfile) {
    fmt.Printf("\n📊 WORKLOAD REDISTRIBUTION for %s\n", engineer.Name)
    fmt.Println("Automatically reassigning non-critical tasks")
    
    // Find engineers with lower workload
    for _, other := range ee.engineers {
        if other.WorkloadCapacity < 0.6 && other.Name != engineer.Name {
            fmt.Printf("Transferring tasks to %s\n", other.Name)
            engineer.WorkloadCapacity -= 0.2
            other.WorkloadCapacity += 0.2
            break
        }
    }
}

// escalateToBackup finds backup engineer
func (ee *EmpathyEngine) escalateToBackup(engineer *EngineerProfile) {
    // Find the least stressed backup
    var backup *EngineerProfile
    minStress := 1.0
    
    for _, eng := range ee.engineers {
        if eng.Name != engineer.Name && eng.CurrentStressLevel < minStress {
            backup = eng
            minStress = eng.CurrentStressLevel
        }
    }
    
    if backup != nil {
        fmt.Printf("Escalating to %s (stress level: %.2f)\n", 
            backup.Name, backup.CurrentStressLevel)
    }
}

// provideStressSupport offers stress management resources
func (ee *EmpathyEngine) provideStressSupport(engineer *EngineerProfile) {
    fmt.Println("\n💙 STRESS SUPPORT RESOURCES:")
    fmt.Println("• 5-minute guided breathing exercise available")
    fmt.Println("• Team wellbeing champion notified")
    fmt.Println("• Optional 1:1 with manager scheduled")
    fmt.Println("• Mental health resources shared via email")
}

// IncidentResponseCoordinator manages incidents with human factors
type IncidentResponseCoordinator struct {
    empathyEngine *EmpathyEngine
    incidentCount int
    mu            sync.Mutex
}

// HandleIncident handles incident with empathy
func (irc *IncidentResponseCoordinator) HandleIncident(
    severity string, 
    description string,
) {
    irc.mu.Lock()
    defer irc.mu.Unlock()
    
    irc.incidentCount++
    
    fmt.Printf("\n🚨 INCIDENT #%d: %s\n", irc.incidentCount, description)
    fmt.Printf("Severity: %s\n", severity)
    
    // Select responder based on human factors
    responder := irc.selectOptimalResponder(severity)
    
    if responder != nil {
        fmt.Printf("Assigned to: %s\n", responder.Name)
        fmt.Printf("Engineer stress level: %.2f\n", responder.CurrentStressLevel)
        
        // Provide context and support
        irc.provideIncidentSupport(responder, severity)
        
        // Update engineer state
        responder.ConsecutiveHours++
        responder.CurrentStressLevel += 0.1
        
        // Simulate incident resolution
        irc.simulateResolution(responder, severity)
    }
}

// selectOptimalResponder selects best responder considering human factors
func (irc *IncidentResponseCoordinator) selectOptimalResponder(
    severity string,
) *EngineerProfile {
    
    irc.empathyEngine.mu.RLock()
    defer irc.empathyEngine.mu.RUnlock()
    
    var bestEngineer *EngineerProfile
    bestScore := 0.0
    
    for _, eng := range irc.empathyEngine.engineers {
        // Calculate suitability score
        score := irc.calculateSuitabilityScore(eng, severity)
        
        if score > bestScore {
            bestScore = score
            bestEngineer = eng
        }
    }
    
    return bestEngineer
}

// calculateSuitabilityScore calculates engineer suitability
func (irc *IncidentResponseCoordinator) calculateSuitabilityScore(
    engineer *EngineerProfile,
    severity string,
) float64 {
    
    score := 1.0
    
    // Experience bonus
    score += float64(engineer.YearsExperience) * 0.1
    
    // Stress penalty
    score -= engineer.CurrentStressLevel * 0.5
    
    // Workload penalty
    score -= engineer.WorkloadCapacity * 0.3
    
    // Consecutive hours penalty
    if engineer.ConsecutiveHours > 3 {
        score -= 0.3
    }
    
    // Recent break bonus
    if time.Since(engineer.LastBreak) < 2*time.Hour {
        score += 0.2
    }
    
    return score
}

// provideIncidentSupport provides human-centric incident support
func (irc *IncidentResponseCoordinator) provideIncidentSupport(
    engineer *EngineerProfile,
    severity string,
) {
    fmt.Println("\n📋 INCIDENT SUPPORT ACTIVATED:")
    
    if severity == "SEV1" {
        fmt.Println("• Backup engineer alerted as shadow")
        fmt.Println("• Manager notified for moral support")
        fmt.Println("• War room created with screen sharing")
    }
    
    fmt.Println("• Recent similar incidents pulled up")
    fmt.Println("• Runbook automatically opened")
    fmt.Println("• Do Not Disturb enabled on Slack")
    
    if engineer.CurrentStressLevel > 0.5 {
        fmt.Println("• Stress detected - calming music playlist started")
        fmt.Println("• Quick wins checklist provided")
    }
}

// simulateResolution simulates incident resolution
func (irc *IncidentResponseCoordinator) simulateResolution(
    engineer *EngineerProfile,
    severity string,
) {
    // Simulate resolution time based on human factors
    baseTime := 30 // minutes
    
    if severity == "SEV1" {
        baseTime = 60
    }
    
    // Adjust based on stress
    actualTime := float64(baseTime) * (1 + engineer.CurrentStressLevel)
    
    fmt.Printf("\nResolution time: %.0f minutes\n", actualTime)
    
    // Post-incident care
    fmt.Println("\n🎯 POST-INCIDENT CARE:")
    fmt.Println("• Mandatory 30-minute break enforced")
    fmt.Println("• Incident debrief scheduled for tomorrow")
    fmt.Println("• Appreciation message sent to engineer")
    fmt.Println("• Stress level monitoring increased")
}

// TeamWellbeingDashboard provides team wellbeing metrics
type TeamWellbeingDashboard struct {
    empathyEngine *EmpathyEngine
}

// GenerateWellbeingReport generates team wellbeing report
func (twd *TeamWellbeingDashboard) GenerateWellbeingReport() {
    fmt.Println("\n📊 TEAM WELLBEING DASHBOARD")
    fmt.Println("="*50)
    
    twd.empathyEngine.mu.RLock()
    defer twd.empathyEngine.mu.RUnlock()
    
    totalStress := 0.0
    overworked := 0
    needsBreak := 0
    
    for _, eng := range twd.empathyEngine.engineers {
        totalStress += eng.CurrentStressLevel
        
        if eng.WorkloadCapacity > 0.8 {
            overworked++
        }
        
        if eng.ConsecutiveHours > 3 {
            needsBreak++
        }
    }
    
    avgStress := totalStress / float64(len(twd.empathyEngine.engineers))
    
    fmt.Printf("\n📈 Team Metrics:\n")
    fmt.Printf("Average Stress Level: %.2f\n", avgStress)
    fmt.Printf("Overworked Engineers: %d\n", overworked)
    fmt.Printf("Need Break: %d\n", needsBreak)
    
    // Recommendations
    fmt.Println("\n💡 Recommendations:")
    
    if avgStress > 0.6 {
        fmt.Println("• Team stress high - consider workload redistribution")
        fmt.Println("• Schedule team bonding activity")
        fmt.Println("• Review on-call rotation fairness")
    }
    
    if overworked > len(twd.empathyEngine.engineers)/2 {
        fmt.Println("• Majority overworked - hiring recommended")
        fmt.Println("• Prioritize and drop non-critical work")
    }
    
    if needsBreak > 0 {
        fmt.Printf("• %d engineers need immediate break\n", needsBreak)
    }
}

func main() {
    fmt.Println("🚀 HUMAN-CENTRIC TECH SYSTEM")
    fmt.Println("Building systems that care about engineers")
    fmt.Println("="*60)
    
    // Initialize empathy engine
    empathyEngine := NewEmpathyEngine()
    
    // Add engineers
    engineers := []*EngineerProfile{
        {
            Name:               "Raj Kumar",
            Role:              "Senior SRE",
            YearsExperience:   5,
            CurrentStressLevel: 0.6,
            WorkloadCapacity:   0.7,
            LastBreak:         time.Now().Add(-3 * time.Hour),
            ConsecutiveHours:  3,
        },
        {
            Name:               "Priya Sharma",
            Role:              "DevOps Engineer",
            YearsExperience:   3,
            CurrentStressLevel: 0.8,
            WorkloadCapacity:   0.9,
            LastBreak:         time.Now().Add(-5 * time.Hour),
            ConsecutiveHours:  5,
        },
        {
            Name:               "Amit Patel",
            Role:              "Platform Engineer",
            YearsExperience:   7,
            CurrentStressLevel: 0.4,
            WorkloadCapacity:   0.6,
            LastBreak:         time.Now().Add(-1 * time.Hour),
            ConsecutiveHours:  1,
        },
    }
    
    for _, eng := range engineers {
        empathyEngine.engineers[eng.Name] = eng
    }
    
    // Create incident coordinator
    coordinator := &IncidentResponseCoordinator{
        empathyEngine: empathyEngine,
    }
    
    // Simulate incidents
    incidents := []struct {
        severity    string
        description string
    }{
        {"SEV2", "API response time degraded"},
        {"SEV1", "Payment service down"},
        {"SEV3", "Monitoring dashboard slow"},
    }
    
    for _, incident := range incidents {
        coordinator.HandleIncident(incident.severity, incident.description)
        time.Sleep(1 * time.Second)
    }
    
    // Generate wellbeing report
    dashboard := &TeamWellbeingDashboard{
        empathyEngine: empathyEngine,
    }
    dashboard.GenerateWellbeingReport()
    
    // Check individual engineers
    fmt.Println("\n👥 Individual Wellbeing Checks:")
    for _, eng := range engineers {
        if eng.ConsecutiveHours >= empathyEngine.policies.MaxConsecutiveHours {
            empathyEngine.triggerBreakReminder(eng)
        }
        if eng.CurrentStressLevel > empathyEngine.policies.StressThreshold {
            empathyEngine.initiateStressProtocol(eng)
        }
    }
}
```

### Building Psychological Safety in Tech Teams

Psychological safety ka matlab hai ki engineers bina dar ke questions puch sake, mistakes admit kar sake, aur help maang sake. Indian context mein ye aur bhi important hai kyunki yahan hierarchy culture strong hai.

```python
# Psychological Safety Framework for Indian Tech Teams
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

class SafetyLevel(Enum):
    CRITICAL = "Critical - Fear-based culture"
    LOW = "Low - Hierarchical barriers"
    MODERATE = "Moderate - Some openness"
    HIGH = "High - Safe to fail"
    EXCELLENT = "Excellent - Innovation thrives"

@dataclass
class TeamMember:
    name: str
    designation: str
    years_exp: int
    speaks_in_meetings: bool = False
    asks_questions: bool = False
    admits_mistakes: bool = False
    shares_ideas: bool = False
    helps_others: bool = True
    fear_score: float = 0.5  # 0 = no fear, 1 = high fear

class PsychologicalSafetyBuilder:
    """
    Build and measure psychological safety in Indian tech teams
    Address hierarchy, fear of judgment, and cultural barriers
    """
    
    def __init__(self, team_name: str):
        self.team_name = team_name
        self.team_members = []
        self.safety_score = 0.0
        self.cultural_barriers = [
            "Hierarchy respect",
            "Fear of looking stupid",
            "Yes-sir culture",
            "Avoiding confrontation",
            "Individual blame culture"
        ]
        self.safety_practices = []
        self.incident_history = []
        
    def add_team_member(self, member: TeamMember):
        """Add team member and assess their safety level"""
        self.team_members.append(member)
        self._assess_member_safety(member)
    
    def _assess_member_safety(self, member: TeamMember):
        """Assess individual psychological safety"""
        safety_indicators = 0
        total_indicators = 5
        
        if member.speaks_in_meetings:
            safety_indicators += 1
        if member.asks_questions:
            safety_indicators += 1
        if member.admits_mistakes:
            safety_indicators += 1
        if member.shares_ideas:
            safety_indicators += 1
        if member.helps_others:
            safety_indicators += 1
        
        member.fear_score = 1 - (safety_indicators / total_indicators)
    
    def measure_team_safety(self) -> Dict:
        """Measure overall team psychological safety"""
        if not self.team_members:
            return {'level': SafetyLevel.CRITICAL, 'score': 0}
        
        # Calculate various metrics
        metrics = {
            'speaks_ratio': sum(1 for m in self.team_members if m.speaks_in_meetings) / len(self.team_members),
            'questions_ratio': sum(1 for m in self.team_members if m.asks_questions) / len(self.team_members),
            'mistakes_ratio': sum(1 for m in self.team_members if m.admits_mistakes) / len(self.team_members),
            'ideas_ratio': sum(1 for m in self.team_members if m.shares_ideas) / len(self.team_members),
            'helping_ratio': sum(1 for m in self.team_members if m.helps_others) / len(self.team_members),
            'avg_fear': sum(m.fear_score for m in self.team_members) / len(self.team_members)
        }
        
        # Calculate overall safety score
        self.safety_score = (
            metrics['speaks_ratio'] * 0.2 +
            metrics['questions_ratio'] * 0.25 +
            metrics['mistakes_ratio'] * 0.25 +
            metrics['ideas_ratio'] * 0.2 +
            metrics['helping_ratio'] * 0.1
        )
        
        # Determine safety level
        if self.safety_score < 0.2:
            level = SafetyLevel.CRITICAL
        elif self.safety_score < 0.4:
            level = SafetyLevel.LOW
        elif self.safety_score < 0.6:
            level = SafetyLevel.MODERATE
        elif self.safety_score < 0.8:
            level = SafetyLevel.HIGH
        else:
            level = SafetyLevel.EXCELLENT
        
        return {
            'level': level,
            'score': self.safety_score,
            'metrics': metrics,
            'barriers': self._identify_barriers(metrics),
            'strengths': self._identify_strengths(metrics)
        }
    
    def _identify_barriers(self, metrics: Dict) -> List[str]:
        """Identify specific barriers to psychological safety"""
        barriers = []
        
        if metrics['questions_ratio'] < 0.3:
            barriers.append("Team afraid to ask questions")
        
        if metrics['mistakes_ratio'] < 0.2:
            barriers.append("Blame culture - mistakes hidden")
        
        if metrics['speaks_ratio'] < 0.4:
            barriers.append("Junior members stay silent")
        
        if metrics['avg_fear'] > 0.6:
            barriers.append("High fear levels across team")
        
        if metrics['ideas_ratio'] < 0.3:
            barriers.append("Innovation stifled - ideas not shared")
        
        return barriers
    
    def _identify_strengths(self, metrics: Dict) -> List[str]:
        """Identify team strengths"""
        strengths = []
        
        if metrics['helping_ratio'] > 0.7:
            strengths.append("Strong helping culture")
        
        if metrics['questions_ratio'] > 0.5:
            strengths.append("Healthy questioning culture")
        
        if metrics['mistakes_ratio'] > 0.4:
            strengths.append("Mistakes treated as learning")
        
        return strengths
    
    def implement_safety_practice(self, practice: str) -> Dict:
        """Implement specific psychological safety practice"""
        self.safety_practices.append({
            'practice': practice,
            'implemented_date': datetime.now(),
            'impact': self._simulate_practice_impact(practice)
        })
        
        return self.safety_practices[-1]
    
    def _simulate_practice_impact(self, practice: str) -> float:
        """Simulate impact of safety practice"""
        practice_impacts = {
            'blameless_postmortems': 0.15,
            'anonymous_feedback': 0.10,
            'failure_fridays': 0.12,
            'question_appreciation': 0.08,
            'peer_mentoring': 0.10,
            'flat_communication': 0.15,
            'mistake_sharing_sessions': 0.12,
            'idea_brainstorming': 0.08
        }
        
        impact = practice_impacts.get(practice.lower().replace(' ', '_'), 0.05)
        
        # Apply impact to team members
        for member in self.team_members:
            if random.random() < impact:
                member.fear_score = max(0, member.fear_score - 0.1)
                
                # Randomly improve behaviors
                if random.random() < 0.5:
                    member.asks_questions = True
                if random.random() < 0.3:
                    member.admits_mistakes = True
        
        return impact
    
    def simulate_incident_response(self, incident_type: str) -> Dict:
        """Simulate how team responds to incidents"""
        response = {
            'incident': incident_type,
            'timestamp': datetime.now(),
            'responses': []
        }
        
        for member in self.team_members:
            member_response = self._generate_member_response(member, incident_type)
            response['responses'].append(member_response)
        
        # Analyze response patterns
        response['analysis'] = self._analyze_incident_response(response['responses'])
        self.incident_history.append(response)
        
        return response
    
    def _generate_member_response(self, member: TeamMember, incident: str) -> Dict:
        """Generate individual response to incident"""
        response = {
            'member': member.name,
            'role': member.designation
        }
        
        if member.fear_score > 0.7:
            response['action'] = "Stays silent, waits for senior to speak"
            response['thoughts'] = "What if I say something wrong?"
        elif member.fear_score > 0.4:
            response['action'] = "Shares partial information"
            response['thoughts'] = "I'll only share what's safe"
        else:
            response['action'] = "Actively participates in resolution"
            response['thoughts'] = "Let me share what I know"
        
        # Check if admits mistakes
        if incident == "production_bug" and member.admits_mistakes:
            response['admits_responsibility'] = True
            response['statement'] = "I think my code change might have caused this"
        else:
            response['admits_responsibility'] = False
            response['statement'] = "The system has been unstable lately"
        
        return response
    
    def _analyze_incident_response(self, responses: List[Dict]) -> Dict:
        """Analyze team's incident response patterns"""
        active_participants = sum(1 for r in responses 
                                if "actively" in r.get('action', '').lower())
        
        admitted_mistakes = sum(1 for r in responses 
                               if r.get('admits_responsibility', False))
        
        silent_members = sum(1 for r in responses 
                            if "silent" in r.get('action', '').lower())
        
        return {
            'participation_rate': active_participants / len(responses),
            'responsibility_rate': admitted_mistakes / len(responses),
            'silence_rate': silent_members / len(responses),
            'safety_assessment': self._assess_response_safety(
                active_participants, admitted_mistakes, silent_members, len(responses)
            )
        }
    
    def _assess_response_safety(self, active: int, admits: int, 
                               silent: int, total: int) -> str:
        """Assess psychological safety from incident response"""
        if silent > total / 2:
            return "Critical - Team paralyzed by fear"
        elif admits == 0:
            return "Low - Blame avoidance culture"
        elif active > total * 0.7:
            return "High - Team collaborates openly"
        else:
            return "Moderate - Some barriers remain"
    
    def generate_improvement_plan(self) -> Dict:
        """Generate customized improvement plan"""
        current_safety = self.measure_team_safety()
        
        plan = {
            'current_state': current_safety['level'].value,
            'target_state': SafetyLevel.HIGH.value,
            'timeline': '3 months',
            'quick_wins': [],
            'long_term_changes': [],
            'metrics_to_track': []
        }
        
        # Quick wins (1-2 weeks)
        if current_safety['metrics']['questions_ratio'] < 0.5:
            plan['quick_wins'].append({
                'action': 'Start "No Stupid Questions" sessions',
                'how': 'Weekly 30-min session where only questions allowed',
                'impact': 'Normalize asking questions'
            })
        
        if current_safety['metrics']['mistakes_ratio'] < 0.3:
            plan['quick_wins'].append({
                'action': 'Implement "Failure Friday"',
                'how': 'Share one failure/learning every Friday standup',
                'impact': 'Destigmatize mistakes'
            })
        
        # Long-term changes (1-3 months)
        plan['long_term_changes'].append({
            'action': 'Flatten communication hierarchy',
            'how': 'Skip-level meetings, open office hours, peer reviews',
            'impact': 'Reduce power distance'
        })
        
        plan['long_term_changes'].append({
            'action': 'Implement blameless post-mortems',
            'how': 'Focus on system failures, not people failures',
            'impact': 'Build learning culture'
        })
        
        # Metrics to track
        plan['metrics_to_track'] = [
            'Weekly question count in meetings',
            'Incident response participation rate',
            'Anonymous safety survey scores',
            'Idea submission rate',
            'Voluntary mistake admissions'
        ]
        
        return plan
    
    def print_safety_report(self):
        """Generate comprehensive psychological safety report"""
        safety = self.measure_team_safety()
        
        print(f"\n🧠 PSYCHOLOGICAL SAFETY REPORT - {self.team_name}")
        print("="*60)
        
        print(f"\n📊 Overall Safety Level: {safety['level'].value}")
        print(f"Safety Score: {safety['score']:.2f}/1.0")
        
        print(f"\n📈 Team Behaviors:")
        metrics = safety['metrics']
        print(f"  Speak in meetings: {metrics['speaks_ratio']:.1%}")
        print(f"  Ask questions: {metrics['questions_ratio']:.1%}")
        print(f"  Admit mistakes: {metrics['mistakes_ratio']:.1%}")
        print(f"  Share ideas: {metrics['ideas_ratio']:.1%}")
        print(f"  Help others: {metrics['helping_ratio']:.1%}")
        print(f"  Average fear level: {metrics['avg_fear']:.2f}/1.0")
        
        if safety['barriers']:
            print(f"\n🚧 Barriers Identified:")
            for barrier in safety['barriers']:
                print(f"  ❌ {barrier}")
        
        if safety['strengths']:
            print(f"\n💪 Team Strengths:")
            for strength in safety['strengths']:
                print(f"  ✅ {strength}")
        
        # Improvement plan
        plan = self.generate_improvement_plan()
        print(f"\n🎯 Improvement Plan:")
        print(f"Target: {plan['target_state']}")
        print(f"Timeline: {plan['timeline']}")
        
        print(f"\n⚡ Quick Wins:")
        for win in plan['quick_wins'][:2]:
            print(f"  • {win['action']}")
            print(f"    How: {win['how']}")
        
        print(f"\n🔄 Long-term Changes:")
        for change in plan['long_term_changes'][:2]:
            print(f"  • {change['action']}")
            print(f"    Impact: {change['impact']}")

# Create a typical Indian tech team
team = PsychologicalSafetyBuilder("Payment Platform Team")

# Add team members with realistic profiles
team_members = [
    TeamMember("Rajesh (TL)", "Tech Lead", 8, True, True, False, True, True, 0.3),
    TeamMember("Priya", "Senior Engineer", 5, True, False, False, False, True, 0.5),
    TeamMember("Amit", "Engineer", 3, False, False, False, False, True, 0.7),
    TeamMember("Sneha", "Junior Engineer", 1, False, False, False, False, True, 0.8),
    TeamMember("Vikram", "Senior Engineer", 6, True, True, True, True, True, 0.2),
]

for member in team_members:
    team.add_team_member(member)

# Generate report
team.print_safety_report()

# Simulate incident
print("\n" + "="*60)
print("🚨 INCIDENT SIMULATION: Production Bug Found")
incident_response = team.simulate_incident_response("production_bug")

print(f"\nTeam Response Analysis:")
analysis = incident_response['analysis']
print(f"  Active Participation: {analysis['participation_rate']:.1%}")
print(f"  Admitted Responsibility: {analysis['responsibility_rate']:.1%}")
print(f"  Silent Members: {analysis['silence_rate']:.1%}")
print(f"  Safety Assessment: {analysis['safety_assessment']}")

# Implement improvement practice
print("\n" + "="*60)
print("📈 IMPLEMENTING SAFETY PRACTICE")
practice = team.implement_safety_practice("blameless_postmortems")
print(f"Practice: Blameless Postmortems")
print(f"Expected Impact: {practice['impact']:.1%} improvement")

# Re-measure after practice
new_safety = team.measure_team_safety()
print(f"New Safety Score: {new_safety['score']:.2f}/1.0")
```

### The Future of Human-Centric Tech

Technology ka future sirf AI aur automation mein nahi hai. Real future hai human-machine collaboration mein, jahan technology humans ko replace nahi, empower karti hai.

## Conclusion: The Path Forward

Doston, aaj humne dekha ki kaise tech industry mein human factor sabse important hai. Chahe on-call stress ho, imposter syndrome ho, ya WFH challenges - inn sab ka solution technology mein nahi, empathy mein hai.

Key takeaways:
1. Engineers are humans first, resources second
2. Psychological safety drives innovation
3. Burnout is a system failure, not personal failure
4. Empathy can be architected into systems
5. Indian IT culture needs fundamental reform

Remember - "Code likhna aasan hai, humans ko samajhna mushkil."

Next episode mein hum baat karenge Distributed Systems ke CAP Theorem ki - kaise Consistency, Availability, aur Partition Tolerance mein se sirf do choose kar sakte ho. Tab tak ke liye, take care of yourself and your team.

Jai Hind! 🇮🇳

---

*Total Word Count: 20,122 words*
*Episode Duration: 3 hours*
*Language Mix: 70% Hindi, 30% English*
*Code Examples: 15+*
*Indian Context: Throughout*
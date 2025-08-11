#!/usr/bin/env python3
"""
Team Cognitive Load Calculator - Episode 3: Human Factor in Tech
================================================================

Team ki mental capacity calculate karna - context switching aur complexity ko measure karte hue.
John Sweller ke Cognitive Load Theory ko software teams ke liye adapt kiya gaya hai.

Cognitive Load Types:
1. Intrinsic Load - Task ki inherent difficulty  
2. Extraneous Load - Distractions, poor tools, context switching
3. Germane Load - Learning aur skill building

Features:
- Context switching cost calculation
- Task complexity scoring
- Team capacity planning
- Overload warning system
- Learning load optimization
- Indian workplace context integration
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
import json
import statistics
from collections import defaultdict, Counter

class TaskComplexity(Enum):
    TRIVIAL = 1      # Copy-paste, config changes
    SIMPLE = 2       # Bug fixes, small features
    MODERATE = 3     # Feature development
    COMPLEX = 4      # Architecture changes
    VERY_COMPLEX = 5 # System redesign, new domains

class TaskType(Enum):
    DEVELOPMENT = "development"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging" 
    MEETING = "meeting"
    DOCUMENTATION = "documentation"
    LEARNING = "learning"
    SUPPORT = "support"
    MENTORING = "mentoring"
    PLANNING = "planning"

class ContextType(Enum):
    SAME_PROJECT = "same_project"
    DIFFERENT_PROJECT = "different_project"
    DIFFERENT_DOMAIN = "different_domain"
    DIFFERENT_LANGUAGE = "different_language"
    DIFFERENT_TEAM = "different_team"

@dataclass
class TaskActivity:
    """Individual task activity with cognitive load factors"""
    id: str
    engineer_id: str
    task_type: TaskType
    complexity: TaskComplexity
    start_time: datetime
    end_time: datetime
    title: str
    description: str
    domain: str                    # "payments", "authentication", "notifications"
    project: str
    programming_language: Optional[str] = None
    technologies_used: List[str] = field(default_factory=list)
    requires_learning: bool = False
    collaboration_needed: bool = False
    interruptions: int = 0         # Number of interruptions during task
    context_switches: int = 0      # Number of context switches
    mental_effort_rating: Optional[int] = None  # 1-10 self-reported effort
    
@dataclass
class Engineer:
    """Engineer profile with cognitive capabilities"""
    id: str
    name: str
    email: str
    experience_years: int
    seniority_level: str          # "junior", "mid", "senior", "lead"
    expertise_domains: List[str]   # Familiar domains
    programming_languages: List[str]
    mental_energy_pattern: Dict[int, float]  # Hour -> energy level (0-1)
    max_concurrent_contexts: int = 3  # Max contexts before overload
    learning_capacity: float = 0.3   # % of time available for learning
    multitasking_ability: float = 0.7  # Ability to handle multiple tasks
    interruption_tolerance: float = 0.5  # Tolerance for interruptions
    
    # Indian workplace specific
    language_comfort: Dict[str, float] = field(default_factory=dict)  # Language -> comfort
    cultural_context_switching: float = 0.8  # Hindi/English switching ability
    mentorship_load: int = 0  # Number of people being mentored

@dataclass
class CognitiveLoadMetrics:
    """Comprehensive cognitive load metrics"""
    engineer_id: str
    time_period_start: datetime
    time_period_end: datetime
    
    # Core cognitive loads
    intrinsic_load: float         # Task complexity load
    extraneous_load: float        # Distraction/inefficiency load  
    germane_load: float           # Learning load
    total_cognitive_load: float
    
    # Detailed breakdowns
    context_switching_cost: float
    domain_switching_penalty: float
    language_switching_cost: float
    interruption_impact: float
    collaboration_overhead: float
    learning_investment: float
    
    # Capacity utilization
    cognitive_capacity_used: float    # % of total capacity used
    overload_episodes: int           # Times capacity exceeded
    peak_load_hour: Optional[int]    # Hour with highest load
    optimal_load_hours: List[int]    # Hours with optimal load
    
    # Quality indicators
    focus_quality_score: float       # Sustained attention quality
    task_completion_rate: float      # % of started tasks completed
    rework_indicator: float          # Amount of rework needed
    
    # Recommendations
    load_balancing_suggestions: List[str]
    optimal_task_scheduling: Dict[int, str]  # Hour -> task type recommendation

class CognitiveLoadCalculator:
    """Main cognitive load calculator with Indian workplace considerations"""
    
    def __init__(self):
        # Cognitive load weights based on research
        self.complexity_weights = {
            TaskComplexity.TRIVIAL: 0.1,
            TaskComplexity.SIMPLE: 0.3,
            TaskComplexity.MODERATE: 0.6,
            TaskComplexity.COMPLEX: 0.8,
            TaskComplexity.VERY_COMPLEX: 1.0
        }
        
        # Context switching penalties
        self.context_switch_penalties = {
            ContextType.SAME_PROJECT: 0.1,
            ContextType.DIFFERENT_PROJECT: 0.3,
            ContextType.DIFFERENT_DOMAIN: 0.5,
            ContextType.DIFFERENT_LANGUAGE: 0.4,
            ContextType.DIFFERENT_TEAM: 0.6
        }
        
        # Task type cognitive demands
        self.task_type_demands = {
            TaskType.DEVELOPMENT: 0.8,
            TaskType.CODE_REVIEW: 0.6,
            TaskType.DEBUGGING: 0.9,
            TaskType.MEETING: 0.4,
            TaskType.DOCUMENTATION: 0.3,
            TaskType.LEARNING: 0.7,
            TaskType.SUPPORT: 0.5,
            TaskType.MENTORING: 0.6,
            TaskType.PLANNING: 0.5
        }
        
        # Indian workplace factors
        self.language_switching_penalty = 0.1  # Hindi-English switching
        self.hierarchy_meeting_load = 0.2      # Additional load in hierarchical meetings
        self.festival_period_capacity = 0.8   # Reduced capacity during festivals
    
    def calculate_intrinsic_load(self, tasks: List[TaskActivity], engineer: Engineer) -> float:
        """Calculate intrinsic cognitive load from task complexity"""
        total_intrinsic = 0.0
        total_duration = 0.0
        
        for task in tasks:
            duration_hours = (task.end_time - task.start_time).total_seconds() / 3600
            
            # Base complexity load
            complexity_load = self.complexity_weights[task.complexity]
            
            # Adjust for engineer expertise
            domain_familiarity = 1.0
            if task.domain in engineer.expertise_domains:
                domain_familiarity = 0.7  # Familiar domain reduces load
            else:
                domain_familiarity = 1.3  # Unfamiliar domain increases load
            
            # Programming language familiarity
            lang_familiarity = 1.0
            if task.programming_language:
                if task.programming_language in engineer.programming_languages:
                    lang_familiarity = 0.8
                else:
                    lang_familiarity = 1.4
            
            # Learning requirement adjustment
            learning_multiplier = 1.2 if task.requires_learning else 1.0
            
            task_intrinsic_load = (complexity_load * domain_familiarity * 
                                 lang_familiarity * learning_multiplier * duration_hours)
            
            total_intrinsic += task_intrinsic_load
            total_duration += duration_hours
        
        return total_intrinsic / total_duration if total_duration > 0 else 0
    
    def calculate_extraneous_load(self, tasks: List[TaskActivity], engineer: Engineer) -> float:
        """Calculate extraneous cognitive load from inefficiencies"""
        total_extraneous = 0.0
        total_duration = 0.0
        
        context_switches = self._count_context_switches(tasks)
        interruption_load = sum(task.interruptions for task in tasks)
        
        for task in tasks:
            duration_hours = (task.end_time - task.start_time).total_seconds() / 3600
            
            # Base task type demand
            base_demand = self.task_type_demands[task.task_type]
            
            # Context switching penalty
            context_penalty = 0.0
            if len(tasks) > 1:  # Multiple tasks indicate context switching
                context_penalty = self._calculate_context_switch_penalty(task, tasks)
            
            # Interruption penalty
            interruption_penalty = min(task.interruptions * 0.1, 0.5)  # Cap at 50%
            
            # Collaboration overhead
            collaboration_penalty = 0.2 if task.collaboration_needed else 0.0
            
            # Meeting fatigue (Indian context - hierarchy heavy meetings)
            meeting_penalty = 0.0
            if task.task_type == TaskType.MEETING:
                # Assume hierarchical meetings are more draining
                meeting_penalty = self.hierarchy_meeting_load
            
            task_extraneous_load = ((base_demand + context_penalty + interruption_penalty + 
                                   collaboration_penalty + meeting_penalty) * duration_hours)
            
            total_extraneous += task_extraneous_load
            total_duration += duration_hours
        
        return total_extraneous / total_duration if total_duration > 0 else 0
    
    def calculate_germane_load(self, tasks: List[TaskActivity], engineer: Engineer) -> float:
        """Calculate germane cognitive load from learning activities"""
        total_germane = 0.0
        total_duration = 0.0
        
        for task in tasks:
            duration_hours = (task.end_time - task.start_time).total_seconds() / 3600
            
            # Direct learning activities
            learning_load = 0.0
            if task.task_type == TaskType.LEARNING:
                learning_load = 0.8  # High germane load for explicit learning
            elif task.requires_learning:
                learning_load = 0.4  # Medium load for implicit learning
            elif task.task_type == TaskType.MENTORING:
                learning_load = 0.3  # Mentoring also involves learning
            
            # New domain/technology learning
            if task.domain not in engineer.expertise_domains:
                learning_load += 0.2
            
            if task.programming_language not in engineer.programming_languages:
                learning_load += 0.3
            
            # Cap germane load
            learning_load = min(learning_load, 1.0)
            
            task_germane_load = learning_load * duration_hours
            
            total_germane += task_germane_load
            total_duration += duration_hours
        
        return total_germane / total_duration if total_duration > 0 else 0
    
    def _count_context_switches(self, tasks: List[TaskActivity]) -> int:
        """Count context switches between tasks"""
        if len(tasks) <= 1:
            return 0
        
        switches = 0
        sorted_tasks = sorted(tasks, key=lambda t: t.start_time)
        
        for i in range(1, len(sorted_tasks)):
            current_task = sorted_tasks[i]
            previous_task = sorted_tasks[i-1]
            
            # Check for context switch
            if (current_task.project != previous_task.project or
                current_task.domain != previous_task.domain or
                current_task.programming_language != previous_task.programming_language):
                switches += 1
        
        return switches
    
    def _calculate_context_switch_penalty(self, task: TaskActivity, all_tasks: List[TaskActivity]) -> float:
        """Calculate context switch penalty for a specific task"""
        penalty = 0.0
        
        # Find the previous task
        sorted_tasks = sorted(all_tasks, key=lambda t: t.start_time)
        task_index = next((i for i, t in enumerate(sorted_tasks) if t.id == task.id), -1)
        
        if task_index > 0:
            previous_task = sorted_tasks[task_index - 1]
            
            # Different project
            if task.project != previous_task.project:
                penalty += self.context_switch_penalties[ContextType.DIFFERENT_PROJECT]
            
            # Different domain
            if task.domain != previous_task.domain:
                penalty += self.context_switch_penalties[ContextType.DIFFERENT_DOMAIN]
            
            # Different programming language
            if (task.programming_language and previous_task.programming_language and 
                task.programming_language != previous_task.programming_language):
                penalty += self.context_switch_penalties[ContextType.DIFFERENT_LANGUAGE]
        
        return penalty
    
    def calculate_cognitive_capacity_utilization(self, total_load: float, engineer: Engineer, 
                                               task_hour: int) -> float:
        """Calculate cognitive capacity utilization at specific hour"""
        # Base capacity (assumes 1.0 is maximum sustainable load)
        base_capacity = 1.0
        
        # Adjust for time of day energy pattern
        energy_multiplier = engineer.mental_energy_pattern.get(task_hour, 0.7)
        
        # Adjust for seniority (senior engineers have higher capacity)
        seniority_multipliers = {
            "junior": 0.7,
            "mid": 0.8, 
            "senior": 1.0,
            "lead": 1.1
        }
        seniority_multiplier = seniority_multipliers.get(engineer.seniority_level, 0.8)
        
        # Mentorship load reduces available capacity
        mentorship_penalty = engineer.mentorship_load * 0.1
        
        effective_capacity = (base_capacity * energy_multiplier * seniority_multiplier - 
                            mentorship_penalty)
        
        utilization = total_load / effective_capacity if effective_capacity > 0 else float('inf')
        return min(utilization, 2.0)  # Cap at 200% for display purposes
    
    def identify_overload_episodes(self, tasks: List[TaskActivity], engineer: Engineer) -> List[Tuple[datetime, float]]:
        """Identify time periods when cognitive load exceeded capacity"""
        overload_episodes = []
        
        # Group tasks by hour
        hourly_tasks = defaultdict(list)
        for task in tasks:
            hour = task.start_time.hour
            hourly_tasks[hour].append(task)
        
        for hour, hour_tasks in hourly_tasks.items():
            if not hour_tasks:
                continue
                
            # Calculate loads for this hour
            intrinsic = self.calculate_intrinsic_load(hour_tasks, engineer)
            extraneous = self.calculate_extraneous_load(hour_tasks, engineer)
            germane = self.calculate_germane_load(hour_tasks, engineer)
            total_load = intrinsic + extraneous + germane
            
            # Check capacity utilization
            utilization = self.calculate_cognitive_capacity_utilization(total_load, engineer, hour)
            
            if utilization > 1.0:  # Overload threshold
                timestamp = hour_tasks[0].start_time.replace(minute=0, second=0, microsecond=0)
                overload_episodes.append((timestamp, utilization))
        
        return overload_episodes
    
    def calculate_focus_quality(self, tasks: List[TaskActivity]) -> float:
        """Calculate focus quality based on task patterns"""
        if not tasks:
            return 0.0
        
        total_interruptions = sum(task.interruptions for task in tasks)
        total_tasks = len(tasks)
        
        # Calculate average task duration (longer = better focus)
        durations = [(task.end_time - task.start_time).total_seconds() / 3600 for task in tasks]
        avg_duration = statistics.mean(durations)
        
        # Optimal task duration is 1-2 hours for deep work
        duration_score = 1.0
        if avg_duration < 0.5:  # Too short
            duration_score = avg_duration * 2
        elif avg_duration > 3:  # Too long without break
            duration_score = max(0.3, 1 - (avg_duration - 3) * 0.1)
        
        # Interruption penalty
        interruption_penalty = min(total_interruptions / total_tasks * 0.2, 0.8)
        
        focus_score = duration_score - interruption_penalty
        return max(0, focus_score)
    
    def calculate_comprehensive_metrics(self, engineer: Engineer, tasks: List[TaskActivity], 
                                      time_period_start: datetime, 
                                      time_period_end: datetime) -> CognitiveLoadMetrics:
        """Calculate comprehensive cognitive load metrics"""
        
        # Calculate core cognitive loads
        intrinsic_load = self.calculate_intrinsic_load(tasks, engineer)
        extraneous_load = self.calculate_extraneous_load(tasks, engineer)
        germane_load = self.calculate_germane_load(tasks, engineer)
        total_load = intrinsic_load + extraneous_load + germane_load
        
        # Calculate detailed breakdowns
        context_switches = self._count_context_switches(tasks)
        context_switching_cost = context_switches * 0.2  # Estimated cost per switch
        
        # Language switching (Indian context)
        language_switches = self._count_language_switches(tasks, engineer)
        language_switching_cost = language_switches * self.language_switching_penalty
        
        # Interruption impact
        total_interruptions = sum(task.interruptions for task in tasks)
        interruption_impact = min(total_interruptions * 0.1, 0.5)
        
        # Collaboration overhead
        collaboration_tasks = sum(1 for task in tasks if task.collaboration_needed)
        collaboration_overhead = collaboration_tasks / len(tasks) * 0.3 if tasks else 0
        
        # Learning investment
        learning_tasks = [t for t in tasks if t.requires_learning or t.task_type == TaskType.LEARNING]
        learning_investment = len(learning_tasks) / len(tasks) if tasks else 0
        
        # Domain switching penalty
        domains = set(task.domain for task in tasks)
        domain_switching_penalty = max(0, (len(domains) - 1) * 0.1)
        
        # Capacity utilization analysis
        overload_episodes = self.identify_overload_episodes(tasks, engineer)
        
        # Find peak and optimal hours
        hourly_loads = self._calculate_hourly_loads(tasks, engineer)
        peak_load_hour = max(hourly_loads.keys(), key=lambda h: hourly_loads[h]) if hourly_loads else None
        optimal_load_hours = [h for h, load in hourly_loads.items() if 0.6 <= load <= 0.8]
        
        # Quality indicators
        focus_quality = self.calculate_focus_quality(tasks)
        completed_tasks = sum(1 for task in tasks if task.end_time <= time_period_end)
        task_completion_rate = completed_tasks / len(tasks) if tasks else 0
        
        # Estimate rework (simplified)
        high_complexity_tasks = [t for t in tasks if t.complexity.value >= 4]
        rework_indicator = len(high_complexity_tasks) / len(tasks) * 0.3 if tasks else 0
        
        # Generate recommendations
        suggestions = self._generate_load_balancing_suggestions(
            engineer, total_load, overload_episodes, context_switches)
        
        optimal_scheduling = self._generate_optimal_task_scheduling(engineer, hourly_loads)
        
        return CognitiveLoadMetrics(
            engineer_id=engineer.id,
            time_period_start=time_period_start,
            time_period_end=time_period_end,
            intrinsic_load=intrinsic_load,
            extraneous_load=extraneous_load,
            germane_load=germane_load,
            total_cognitive_load=total_load,
            context_switching_cost=context_switching_cost,
            domain_switching_penalty=domain_switching_penalty,
            language_switching_cost=language_switching_cost,
            interruption_impact=interruption_impact,
            collaboration_overhead=collaboration_overhead,
            learning_investment=learning_investment,
            cognitive_capacity_used=min(total_load, 2.0),
            overload_episodes=len(overload_episodes),
            peak_load_hour=peak_load_hour,
            optimal_load_hours=optimal_load_hours,
            focus_quality_score=focus_quality,
            task_completion_rate=task_completion_rate,
            rework_indicator=rework_indicator,
            load_balancing_suggestions=suggestions,
            optimal_task_scheduling=optimal_scheduling
        )
    
    def _count_language_switches(self, tasks: List[TaskActivity], engineer: Engineer) -> int:
        """Count language context switches (Hindi/English in Indian workplace)"""
        # Simplified - assume meetings in Hindi, coding in English
        switches = 0
        prev_language = None
        
        for task in sorted(tasks, key=lambda t: t.start_time):
            current_language = "Hindi" if task.task_type == TaskType.MEETING else "English"
            if prev_language and prev_language != current_language:
                switches += 1
            prev_language = current_language
        
        return switches
    
    def _calculate_hourly_loads(self, tasks: List[TaskActivity], engineer: Engineer) -> Dict[int, float]:
        """Calculate cognitive load for each hour"""
        hourly_loads = {}
        
        for hour in range(24):
            hour_tasks = [t for t in tasks if t.start_time.hour == hour]
            if hour_tasks:
                intrinsic = self.calculate_intrinsic_load(hour_tasks, engineer)
                extraneous = self.calculate_extraneous_load(hour_tasks, engineer)
                germane = self.calculate_germane_load(hour_tasks, engineer)
                hourly_loads[hour] = intrinsic + extraneous + germane
        
        return hourly_loads
    
    def _generate_load_balancing_suggestions(self, engineer: Engineer, total_load: float,
                                           overload_episodes: List, context_switches: int) -> List[str]:
        """Generate personalized load balancing suggestions"""
        suggestions = []
        
        if total_load > 1.2:
            suggestions.append(
                f"🔴 Total cognitive load is high ({total_load:.2f}). Consider task prioritization or delegation."
            )
        
        if context_switches > 5:
            suggestions.append(
                f"🔄 High context switching ({context_switches} switches). Group similar tasks together."
            )
        
        if len(overload_episodes) > 0:
            suggestions.append(
                f"⚠️ {len(overload_episodes)} overload episodes detected. Schedule demanding tasks during high-energy hours."
            )
        
        # Indian workplace specific
        if engineer.mentorship_load > 2:
            suggestions.append(
                "👨‍🏫 High mentorship load. Consider structured mentoring sessions to reduce ad-hoc interruptions."
            )
        
        # Experience-based suggestions
        if engineer.seniority_level == "junior":
            suggestions.append(
                "🌱 Focus on 1-2 domains to build expertise. Avoid excessive context switching."
            )
        elif engineer.seniority_level == "lead":
            suggestions.append(
                "👔 Balance individual contribution with team coordination. Delegate routine tasks."
            )
        
        return suggestions[:5]  # Top 5 suggestions
    
    def _generate_optimal_task_scheduling(self, engineer: Engineer, 
                                        hourly_loads: Dict[int, float]) -> Dict[int, str]:
        """Generate optimal task type recommendations by hour"""
        scheduling = {}
        
        # Get energy pattern
        energy_pattern = engineer.mental_energy_pattern
        
        for hour in range(9, 18):  # Standard work hours
            energy_level = energy_pattern.get(hour, 0.7)
            current_load = hourly_loads.get(hour, 0.0)
            
            if energy_level > 0.8 and current_load < 0.6:
                scheduling[hour] = "High complexity development work"
            elif energy_level > 0.6 and current_load < 0.8:
                scheduling[hour] = "Moderate complexity tasks or code reviews"
            elif energy_level > 0.4:
                scheduling[hour] = "Meetings, documentation, or learning"
            else:
                scheduling[hour] = "Administrative tasks or breaks"
        
        return scheduling

def demo_cognitive_load_calculator():
    """Demo the cognitive load calculator"""
    print("🧠 Team Cognitive Load Calculator Demo")
    print("=" * 50)
    
    calculator = CognitiveLoadCalculator()
    
    # Create sample engineer with Indian workplace context
    engineer = Engineer(
        id="ENG001",
        name="Rajesh Kumar",
        email="rajesh@company.com",
        experience_years=5,
        seniority_level="senior",
        expertise_domains=["payments", "authentication"],
        programming_languages=["Java", "Python", "JavaScript"],
        mental_energy_pattern={
            9: 0.6,   # Slow start
            10: 0.8,  # Peak morning
            11: 0.9,  # High focus
            12: 0.7,  # Pre-lunch dip
            14: 0.8,  # Post-lunch recovery
            15: 0.9,  # Afternoon peak
            16: 0.8,  # Good focus
            17: 0.6,  # Energy decline
            18: 0.4   # End of day
        },
        max_concurrent_contexts=3,
        learning_capacity=0.3,
        multitasking_ability=0.7,
        interruption_tolerance=0.6,
        language_comfort={"Hindi": 0.9, "English": 0.8},
        cultural_context_switching=0.8,
        mentorship_load=2  # Mentoring 2 junior engineers
    )
    
    print(f"👤 Engineer: {engineer.name} ({engineer.seniority_level})")
    print(f"   Expertise: {', '.join(engineer.expertise_domains)}")
    print(f"   Languages: {', '.join(engineer.programming_languages)}")
    print(f"   Mentorship Load: {engineer.mentorship_load} mentees")
    
    # Create sample tasks showing various cognitive loads
    base_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    tasks = [
        # Morning high-complexity development
        TaskActivity(
            id="T001",
            engineer_id=engineer.id,
            task_type=TaskType.DEVELOPMENT,
            complexity=TaskComplexity.COMPLEX,
            start_time=base_time,
            end_time=base_time + timedelta(hours=2),
            title="Implement payment retry mechanism",
            description="Complex payment flow with circuit breakers",
            domain="payments",
            project="payment-service",
            programming_language="Java",
            technologies_used=["Spring Boot", "Redis", "Kafka"],
            requires_learning=False,
            collaboration_needed=False,
            interruptions=1
        ),
        
        # Context switch to different domain
        TaskActivity(
            id="T002",
            engineer_id=engineer.id,
            task_type=TaskType.CODE_REVIEW,
            complexity=TaskComplexity.MODERATE,
            start_time=base_time + timedelta(hours=2, minutes=15),
            end_time=base_time + timedelta(hours=3),
            title="Review authentication service changes",
            description="OAuth2 implementation review",
            domain="authentication",  # Different domain
            project="auth-service",   # Different project
            programming_language="Python",  # Different language
            requires_learning=True,   # New OAuth2 concepts
            collaboration_needed=True,
            interruptions=0
        ),
        
        # Meeting (hierarchical, in Hindi)
        TaskActivity(
            id="T003",
            engineer_id=engineer.id,
            task_type=TaskType.MEETING,
            complexity=TaskComplexity.SIMPLE,
            start_time=base_time + timedelta(hours=3, minutes=30),
            end_time=base_time + timedelta(hours=4, minutes=30),
            title="Sprint planning with management",
            description="Planning meeting with senior management",
            domain="process",
            project="general",
            collaboration_needed=True,
            interruptions=0
        ),
        
        # Mentoring session
        TaskActivity(
            id="T004",
            engineer_id=engineer.id,
            task_type=TaskType.MENTORING,
            complexity=TaskComplexity.MODERATE,
            start_time=base_time + timedelta(hours=5),
            end_time=base_time + timedelta(hours=6),
            title="Code review with junior engineer",
            description="Mentoring session on design patterns",
            domain="general",
            project="general",
            programming_language="Java",
            collaboration_needed=True,
            interruptions=2
        ),
        
        # Late afternoon debugging (high cognitive load)
        TaskActivity(
            id="T005",
            engineer_id=engineer.id,
            task_type=TaskType.DEBUGGING,
            complexity=TaskComplexity.VERY_COMPLEX,
            start_time=base_time + timedelta(hours=6, minutes=30),
            end_time=base_time + timedelta(hours=8),
            title="Debug production payment failures",
            description="Complex production issue investigation",
            domain="payments",
            project="payment-service",
            programming_language="Java",
            requires_learning=False,
            collaboration_needed=True,
            interruptions=3,  # Multiple stakeholder interruptions
            mental_effort_rating=9
        )
    ]
    
    print(f"\n📊 Analyzing {len(tasks)} tasks over 8-hour period...")
    
    # Calculate comprehensive metrics
    time_start = base_time
    time_end = base_time + timedelta(hours=9)
    
    metrics = calculator.calculate_comprehensive_metrics(
        engineer, tasks, time_start, time_end
    )
    
    print(f"\n🧠 Cognitive Load Analysis Results:")
    print(f"=" * 40)
    
    print(f"📈 Core Cognitive Loads:")
    print(f"   Intrinsic Load:  {metrics.intrinsic_load:.3f} (task complexity)")
    print(f"   Extraneous Load: {metrics.extraneous_load:.3f} (inefficiencies/distractions)")
    print(f"   Germane Load:    {metrics.germane_load:.3f} (learning activities)")
    print(f"   Total Load:      {metrics.total_cognitive_load:.3f}")
    
    print(f"\n🔄 Load Breakdown:")
    print(f"   Context Switching Cost:   {metrics.context_switching_cost:.3f}")
    print(f"   Domain Switching Penalty: {metrics.domain_switching_penalty:.3f}")
    print(f"   Language Switching Cost:  {metrics.language_switching_cost:.3f}")
    print(f"   Interruption Impact:      {metrics.interruption_impact:.3f}")
    print(f"   Collaboration Overhead:   {metrics.collaboration_overhead:.3f}")
    print(f"   Learning Investment:      {metrics.learning_investment:.3f}")
    
    print(f"\n⚖️ Capacity Utilization:")
    print(f"   Capacity Used:       {metrics.cognitive_capacity_used:.1%}")
    print(f"   Overload Episodes:   {metrics.overload_episodes}")
    if metrics.peak_load_hour:
        print(f"   Peak Load Hour:      {metrics.peak_load_hour}:00")
    print(f"   Optimal Load Hours:  {[f'{h}:00' for h in metrics.optimal_load_hours]}")
    
    print(f"\n🎯 Quality Indicators:")
    print(f"   Focus Quality:        {metrics.focus_quality_score:.1%}")
    print(f"   Task Completion:      {metrics.task_completion_rate:.1%}")
    print(f"   Rework Indicator:     {metrics.rework_indicator:.1%}")
    
    print(f"\n💡 Load Balancing Suggestions:")
    for i, suggestion in enumerate(metrics.load_balancing_suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    print(f"\n⏰ Optimal Task Scheduling:")
    for hour, recommendation in sorted(metrics.optimal_task_scheduling.items()):
        print(f"   {hour}:00 - {recommendation}")
    
    # Task-specific analysis
    print(f"\n📋 Task-Specific Analysis:")
    for task in tasks:
        duration = (task.end_time - task.start_time).total_seconds() / 3600
        print(f"\n   {task.title}:")
        print(f"   - Type: {task.task_type.value}, Complexity: {task.complexity.name}")
        print(f"   - Duration: {duration:.1f}h, Interruptions: {task.interruptions}")
        print(f"   - Domain: {task.domain}, Language: {task.programming_language}")
        if task.requires_learning:
            print(f"   - 📚 Learning required")
        if task.collaboration_needed:
            print(f"   - 👥 Collaboration needed")

if __name__ == "__main__":
    demo_cognitive_load_calculator()
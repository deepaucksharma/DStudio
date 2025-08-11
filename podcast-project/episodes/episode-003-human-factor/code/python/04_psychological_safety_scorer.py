#!/usr/bin/env python3
"""
Psychological Safety Scorer - Episode 3: Human Factor in Tech
============================================================

Indian workplace mein psychological safety measure karna - respect aur hierarchy ko balance karte hue.
Amy Edmondson ke research ko Indian context mein adapt kiya gaya hai.

Indian Context Considerations:
- Hierarchy respect vs open communication balance
- Family metaphors in team dynamics ("team family" culture)
- Regional language comfort levels
- Festival and cultural inclusion
- Extended family obligations understanding
- Cross-generational mentorship patterns

Based on research from:
- Amy Edmondson (Harvard Business School)
- Google's Project Aristotle
- Indian IT companies' internal surveys
- Cultural adaptation studies
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import json
import statistics
from collections import defaultdict, Counter
import re

class SafetyDimension(Enum):
    SPEAK_UP = "speak_up"                        # Dare to raise concerns
    MAKE_MISTAKES = "make_mistakes"              # Safe to admit errors
    ASK_QUESTIONS = "ask_questions"              # No stupid questions
    CHALLENGE_IDEAS = "challenge_ideas"          # Respectfully disagree
    SHOW_VULNERABILITY = "show_vulnerability"    # Admit knowledge gaps
    CULTURAL_INCLUSION = "cultural_inclusion"    # Regional/cultural comfort
    HIERARCHY_RESPECT = "hierarchy_respect"      # Balance respect with openness

class TeamRole(Enum):
    INTERN = 1
    JUNIOR = 2
    MID_LEVEL = 3
    SENIOR = 4
    LEAD = 5
    MANAGER = 6

class CulturalBackground(Enum):
    NORTH_INDIA = "north_india"
    SOUTH_INDIA = "south_india"
    WEST_INDIA = "west_india"
    EAST_INDIA = "east_india"
    METROPOLITAN = "metropolitan"
    TIER2_CITY = "tier2_city"
    RURAL_BACKGROUND = "rural_background"

@dataclass
class TeamMember:
    """Team member profile with Indian cultural context"""
    id: str
    name: str
    role: TeamRole
    years_experience: int
    cultural_background: CulturalBackground
    primary_language: str
    comfortable_languages: List[str]
    joining_date: datetime
    is_first_job: bool = False
    has_extended_family_obligations: bool = False
    prefers_formal_communication: bool = False
    mentorship_relationships: List[str] = field(default_factory=list)  # IDs of mentors/mentees
    
    def __post_init__(self):
        if not self.comfortable_languages:
            self.comfortable_languages = [self.primary_language, "English"]

@dataclass
class SafetyObservation:
    """Observation of psychological safety behavior"""
    id: str
    timestamp: datetime
    observer_id: str
    team_member_id: str
    dimension: SafetyDimension
    behavior_description: str
    positive_indicator: bool  # True if behavior indicates safety, False if indicates fear
    context: str  # Meeting, code review, incident response, etc.
    hierarchy_involved: bool = False  # Was hierarchy a factor?
    language_barrier: bool = False   # Was language a barrier?
    cultural_sensitivity: float = 0.0  # 0-1 scale of cultural appropriateness

@dataclass
class TeamSafetyMetrics:
    """Comprehensive team safety metrics"""
    team_id: str
    measurement_date: datetime
    dimension_scores: Dict[SafetyDimension, float]
    overall_score: float
    cultural_inclusion_score: float
    hierarchy_balance_score: float
    improvement_areas: List[str]
    strengths: List[str]
    recommendations: List[str]

class IndianWorkplaceSafetyFramework:
    """Framework for measuring psychological safety in Indian workplace context"""
    
    def __init__(self):
        # Indian workplace specific safety indicators
        self.positive_indicators = {
            SafetyDimension.SPEAK_UP: [
                "raised concern about technical decision respectfully",
                "suggested alternative approach in team meeting",
                "reported potential issue without fear",
                "gave feedback to senior team member politely",
                "spoke up in hindi/regional language comfortably"
            ],
            
            SafetyDimension.MAKE_MISTAKES: [
                "admitted mistake openly in standup",
                "asked for help after making error",
                "shared learning from personal failure", 
                "took ownership of bug without blame",
                "discussed failed experiment results"
            ],
            
            SafetyDimension.ASK_QUESTIONS: [
                "asked clarifying questions in meeting",
                "requested explanation of technical concept",
                "asked about company processes",
                "sought help with unfamiliar technology",
                "asked 'why' questions about decisions"
            ],
            
            SafetyDimension.CHALLENGE_IDEAS: [
                "respectfully disagreed with technical approach",
                "suggested improvement to existing process",
                "questioned requirement with valid reasoning",
                "offered alternative solution",
                "challenged assumption while maintaining respect"
            ],
            
            SafetyDimension.SHOW_VULNERABILITY: [
                "admitted knowledge gap in area",
                "asked for mentorship/guidance",
                "shared personal learning challenges",
                "requested additional training",
                "acknowledged need for skill development"
            ],
            
            SafetyDimension.CULTURAL_INCLUSION: [
                "celebrated regional festival with team",
                "shared cultural perspective on problem",
                "used comfortable language in informal settings", 
                "included cultural context in solutions",
                "felt comfortable with family obligations discussion"
            ],
            
            SafetyDimension.HIERARCHY_RESPECT: [
                "balanced respect with honest feedback",
                "approached senior member with concerns appropriately",
                "maintained courtesy while disagreeing",
                "followed escalation protocols respectfully",
                "addressed manager with appropriate formality"
            ]
        }
        
        # Negative indicators (signs of psychological unsafety)
        self.negative_indicators = {
            SafetyDimension.SPEAK_UP: [
                "stayed silent despite having concerns",
                "agreed with everything without input",
                "avoided sharing opinions",
                "only spoke when directly asked",
                "seemed hesitant to contribute"
            ],
            
            SafetyDimension.MAKE_MISTAKES: [
                "hid mistake until discovered",
                "blamed others for personal error", 
                "showed extreme stress over minor bug",
                "avoided taking on challenging tasks",
                "defensive when error was pointed out"
            ],
            
            SafetyDimension.ASK_QUESTIONS: [
                "pretended to understand when confused",
                "struggled silently instead of asking",
                "avoided asking 'basic' questions",
                "seemed afraid to show knowledge gaps",
                "only asked questions offline/privately"
            ],
            
            SafetyDimension.CHALLENGE_IDEAS: [
                "agreed with obviously flawed approach",
                "avoided suggesting improvements",
                "deferred to seniority over logic",
                "suppressed valid technical concerns",
                "seemed afraid to offer alternatives"
            ],
            
            SafetyDimension.SHOW_VULNERABILITY: [
                "claimed to know everything",
                "avoided learning opportunities",
                "resistant to feedback or coaching",
                "tried to appear perfect always",
                "avoided admitting confusion"
            ],
            
            SafetyDimension.CULTURAL_INCLUSION: [
                "avoided sharing cultural background",
                "seemed uncomfortable during festivals",
                "only communicated in formal English",
                "appeared isolated during cultural celebrations",
                "hesitant to discuss family obligations"
            ],
            
            SafetyDimension.HIERARCHY_RESPECT: [
                "excessive deference limiting contribution",
                "fear-based compliance without understanding",
                "avoided any form of disagreement",
                "seemed intimidated by senior presence",
                "communication became formal/stiff with hierarchy"
            ]
        }
    
    def calculate_dimension_score(self, observations: List[SafetyObservation], 
                                 dimension: SafetyDimension) -> float:
        """Calculate score for specific safety dimension"""
        relevant_obs = [o for o in observations if o.dimension == dimension]
        if not relevant_obs:
            return 0.5  # Neutral score when no data
        
        positive_count = sum(1 for o in relevant_obs if o.positive_indicator)
        total_count = len(relevant_obs)
        
        base_score = positive_count / total_count
        
        # Adjust for cultural context
        cultural_adjustment = 0.0
        hierarchy_adjustment = 0.0
        
        for obs in relevant_obs:
            if obs.cultural_sensitivity > 0.7:
                cultural_adjustment += 0.1
            if obs.hierarchy_involved and obs.positive_indicator:
                hierarchy_adjustment += 0.1  # Extra credit for positive hierarchy interaction
        
        # Normalize adjustments
        cultural_adjustment = min(cultural_adjustment / len(relevant_obs), 0.2)
        hierarchy_adjustment = min(hierarchy_adjustment / len(relevant_obs), 0.2)
        
        final_score = min(base_score + cultural_adjustment + hierarchy_adjustment, 1.0)
        return final_score

class PsychologicalSafetyScorer:
    """Main psychological safety scoring system with Indian workplace awareness"""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.team_members: List[TeamMember] = []
        self.observations: List[SafetyObservation] = []
        self.framework = IndianWorkplaceSafetyFramework()
        self.historical_scores: List[TeamSafetyMetrics] = []
    
    def add_team_member(self, member: TeamMember):
        """Add team member to psychological safety tracking"""
        self.team_members.append(member)
        print(f"👤 Added {member.name} ({member.role.name}) to safety tracking")
        
        # Special welcome for first-job members
        if member.is_first_job:
            print(f"   🌱 First job - extra support and mentorship recommended")
    
    def record_observation(self, observation: SafetyObservation):
        """Record psychological safety observation"""
        self.observations.append(observation)
        
        # Provide immediate feedback for positive behaviors
        if observation.positive_indicator:
            print(f"✅ Positive safety behavior observed: {observation.dimension.value}")
            if observation.hierarchy_involved:
                print(f"   💪 Especially good - involved hierarchy interaction")
        else:
            print(f"⚠️  Safety concern noted: {observation.dimension.value}")
            if observation.language_barrier:
                print(f"   🗣️  Language barrier may be a factor")
    
    def calculate_team_score(self, days_back: int = 30) -> TeamSafetyMetrics:
        """Calculate comprehensive team psychological safety score"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_observations = [o for o in self.observations if o.timestamp >= cutoff_date]
        
        if not recent_observations:
            return self._create_default_metrics()
        
        # Calculate dimension scores
        dimension_scores = {}
        for dimension in SafetyDimension:
            score = self.framework.calculate_dimension_score(recent_observations, dimension)
            dimension_scores[dimension] = score
        
        # Calculate overall score (weighted average)
        weights = {
            SafetyDimension.SPEAK_UP: 0.20,
            SafetyDimension.MAKE_MISTAKES: 0.18,
            SafetyDimension.ASK_QUESTIONS: 0.15,
            SafetyDimension.CHALLENGE_IDEAS: 0.15,
            SafetyDimension.SHOW_VULNERABILITY: 0.12,
            SafetyDimension.CULTURAL_INCLUSION: 0.10,  # Important in Indian context
            SafetyDimension.HIERARCHY_RESPECT: 0.10    # Critical in Indian workplace
        }
        
        overall_score = sum(score * weights[dim] for dim, score in dimension_scores.items())
        
        # Special scores for Indian context
        cultural_inclusion_score = dimension_scores[SafetyDimension.CULTURAL_INCLUSION]
        hierarchy_balance_score = dimension_scores[SafetyDimension.HIERARCHY_RESPECT]
        
        # Generate insights
        improvement_areas = self._identify_improvement_areas(dimension_scores)
        strengths = self._identify_strengths(dimension_scores)
        recommendations = self._generate_recommendations(dimension_scores, recent_observations)
        
        metrics = TeamSafetyMetrics(
            team_id=self.team_id,
            measurement_date=datetime.now(),
            dimension_scores=dimension_scores,
            overall_score=overall_score,
            cultural_inclusion_score=cultural_inclusion_score,
            hierarchy_balance_score=hierarchy_balance_score,
            improvement_areas=improvement_areas,
            strengths=strengths,
            recommendations=recommendations
        )
        
        self.historical_scores.append(metrics)
        return metrics
    
    def _create_default_metrics(self) -> TeamSafetyMetrics:
        """Create default metrics when no observations exist"""
        return TeamSafetyMetrics(
            team_id=self.team_id,
            measurement_date=datetime.now(),
            dimension_scores={dim: 0.5 for dim in SafetyDimension},
            overall_score=0.5,
            cultural_inclusion_score=0.5,
            hierarchy_balance_score=0.5,
            improvement_areas=["Need to collect observations"],
            strengths=["Team exists and is being monitored"],
            recommendations=["Start collecting psychological safety observations"]
        )
    
    def _identify_improvement_areas(self, scores: Dict[SafetyDimension, float]) -> List[str]:
        """Identify areas needing improvement based on scores"""
        improvement_areas = []
        
        for dimension, score in scores.items():
            if score < 0.6:  # Below good threshold
                area_name = dimension.value.replace('_', ' ').title()
                improvement_areas.append(f"{area_name} (Score: {score:.2f})")
        
        # Sort by lowest scores first
        improvement_areas.sort(key=lambda x: float(x.split('Score: ')[1].split(')')[0]))
        
        return improvement_areas[:3]  # Top 3 areas
    
    def _identify_strengths(self, scores: Dict[SafetyDimension, float]) -> List[str]:
        """Identify team strengths based on high scores"""
        strengths = []
        
        for dimension, score in scores.items():
            if score >= 0.8:  # High threshold
                area_name = dimension.value.replace('_', ' ').title()
                strengths.append(f"{area_name} (Score: {score:.2f})")
        
        # Sort by highest scores first
        strengths.sort(key=lambda x: float(x.split('Score: ')[1].split(')')[0]), reverse=True)
        
        return strengths
    
    def _generate_recommendations(self, scores: Dict[SafetyDimension, float], 
                                 observations: List[SafetyObservation]) -> List[str]:
        """Generate actionable recommendations for improving psychological safety"""
        recommendations = []
        
        # Overall recommendations based on scores
        if scores[SafetyDimension.SPEAK_UP] < 0.6:
            recommendations.append(
                "🗣️ Create more opportunities for team members to share opinions safely. "
                "Try anonymous feedback sessions or 'devil's advocate' roles in meetings."
            )
        
        if scores[SafetyDimension.MAKE_MISTAKES] < 0.6:
            recommendations.append(
                "🔍 Implement blameless postmortem culture. Share stories of learning from mistakes. "
                "Consider 'failure parties' to celebrate learning opportunities."
            )
        
        if scores[SafetyDimension.ASK_QUESTIONS] < 0.6:
            recommendations.append(
                "❓ Establish 'no stupid questions' policy explicitly. "
                "Have senior members model question-asking behavior."
            )
        
        if scores[SafetyDimension.CULTURAL_INCLUSION] < 0.7:
            recommendations.append(
                "🪔 Enhance cultural inclusion: celebrate diverse festivals, "
                "allow comfortable language use, respect family obligations."
            )
        
        if scores[SafetyDimension.HIERARCHY_RESPECT] < 0.7:
            recommendations.append(
                "⚖️ Balance hierarchy respect with open communication. "
                "Train leaders on encouraging upward feedback while maintaining cultural respect."
            )
        
        # Observation-based recommendations
        language_barriers = sum(1 for o in observations if o.language_barrier)
        if language_barriers > len(observations) * 0.3:
            recommendations.append(
                "🌐 Address language barriers: provide multilingual resources, "
                "encourage regional language use in informal settings."
            )
        
        hierarchy_issues = sum(1 for o in observations 
                             if o.hierarchy_involved and not o.positive_indicator)
        if hierarchy_issues > 0:
            recommendations.append(
                "👔 Provide hierarchy navigation training for both seniors and juniors. "
                "Focus on respectful ways to disagree and provide feedback."
            )
        
        # Role-specific recommendations
        junior_members = [m for m in self.team_members if m.role in [TeamRole.INTERN, TeamRole.JUNIOR]]
        if len(junior_members) > len(self.team_members) * 0.4:
            recommendations.append(
                "🌱 High proportion of junior members - implement structured mentorship "
                "and buddy systems. Create safe learning environments."
            )
        
        return recommendations[:5]  # Top 5 recommendations
    
    def analyze_individual_safety(self, member_id: str) -> Dict:
        """Analyze psychological safety for individual team member"""
        member = next((m for m in self.team_members if m.id == member_id), None)
        if not member:
            return {"error": "Member not found"}
        
        # Get recent observations for this member
        recent_obs = [o for o in self.observations 
                     if o.team_member_id == member_id and 
                     o.timestamp >= datetime.now() - timedelta(days=30)]
        
        if not recent_obs:
            return {
                "member": member.name,
                "status": "No recent observations",
                "recommendation": "Start collecting behavioral observations"
            }
        
        # Calculate individual dimension scores
        individual_scores = {}
        for dimension in SafetyDimension:
            relevant_obs = [o for o in recent_obs if o.dimension == dimension]
            if relevant_obs:
                positive_rate = sum(1 for o in relevant_obs if o.positive_indicator) / len(relevant_obs)
                individual_scores[dimension] = positive_rate
        
        # Identify patterns
        patterns = []
        
        # New joiner pattern
        if member.is_first_job and (datetime.now() - member.joining_date).days < 90:
            patterns.append("New to industry - may need extra encouragement")
        
        # Cultural background consideration
        if member.cultural_background in [CulturalBackground.TIER2_CITY, CulturalBackground.RURAL_BACKGROUND]:
            patterns.append("Non-metro background - may prefer more formal communication initially")
        
        # Language comfort
        if len(member.comfortable_languages) == 1:
            patterns.append("Single language comfort - may benefit from multilingual support")
        
        # Role-based patterns
        if member.role == TeamRole.INTERN:
            patterns.append("Intern - focus on learning safety and mistake tolerance")
        elif member.role in [TeamRole.MANAGER, TeamRole.LEAD]:
            patterns.append("Leadership role - model psychological safety behaviors")
        
        return {
            "member": member.name,
            "role": member.role.name,
            "overall_participation": len(recent_obs),
            "positive_behavior_rate": sum(1 for o in recent_obs if o.positive_indicator) / len(recent_obs),
            "dimension_scores": individual_scores,
            "patterns": patterns,
            "recommendations": self._get_individual_recommendations(member, recent_obs)
        }
    
    def _get_individual_recommendations(self, member: TeamMember, 
                                      observations: List[SafetyObservation]) -> List[str]:
        """Get personalized recommendations for individual team member"""
        recommendations = []
        
        positive_rate = sum(1 for o in observations if o.positive_indicator) / len(observations)
        
        if positive_rate < 0.5:
            recommendations.append(f"Focus on creating safe space for {member.name} to contribute")
            
            if member.is_first_job:
                recommendations.append("Assign dedicated mentor for first-job guidance")
            
            if member.role in [TeamRole.INTERN, TeamRole.JUNIOR]:
                recommendations.append("Provide structured learning opportunities and clear expectations")
        
        # Language-based recommendations
        if "English" not in member.comfortable_languages:
            recommendations.append("Consider multilingual documentation and communication options")
        
        # Cultural recommendations
        if member.has_extended_family_obligations:
            recommendations.append("Show flexibility and understanding for family commitments")
        
        # Hierarchy-based recommendations  
        if member.prefers_formal_communication:
            recommendations.append("Respect formal communication preferences while encouraging openness")
        
        return recommendations
    
    def generate_safety_report(self) -> Dict:
        """Generate comprehensive team psychological safety report"""
        metrics = self.calculate_team_score()
        
        # Get individual analysis for all members
        individual_analyses = {}
        for member in self.team_members:
            individual_analyses[member.name] = self.analyze_individual_safety(member.id)
        
        # Calculate team composition insights
        composition_insights = self._analyze_team_composition()
        
        # Trend analysis if historical data exists
        trends = self._analyze_trends() if len(self.historical_scores) > 1 else {}
        
        return {
            "team_id": self.team_id,
            "measurement_date": metrics.measurement_date.strftime("%Y-%m-%d"),
            "overall_score": round(metrics.overall_score * 100, 1),
            "score_interpretation": self._interpret_overall_score(metrics.overall_score),
            "dimension_scores": {
                dim.value: round(score * 100, 1) 
                for dim, score in metrics.dimension_scores.items()
            },
            "cultural_inclusion_score": round(metrics.cultural_inclusion_score * 100, 1),
            "hierarchy_balance_score": round(metrics.hierarchy_balance_score * 100, 1),
            "strengths": metrics.strengths,
            "improvement_areas": metrics.improvement_areas,
            "recommendations": metrics.recommendations,
            "individual_analyses": individual_analyses,
            "team_composition": composition_insights,
            "trends": trends,
            "total_observations": len(self.observations),
            "recent_observations": len([o for o in self.observations 
                                      if o.timestamp >= datetime.now() - timedelta(days=30)])
        }
    
    def _interpret_overall_score(self, score: float) -> str:
        """Interpret overall psychological safety score"""
        if score >= 0.85:
            return "🏆 Excellent - Team has very high psychological safety"
        elif score >= 0.75:
            return "✅ Good - Team feels generally safe to take risks and be vulnerable"
        elif score >= 0.60:
            return "⚠️ Moderate - Some safety present but room for improvement"
        elif score >= 0.40:
            return "🔶 Below Average - Significant safety concerns need attention"
        else:
            return "🚨 Poor - Major psychological safety issues require immediate action"
    
    def _analyze_team_composition(self) -> Dict:
        """Analyze team composition for diversity and inclusion insights"""
        if not self.team_members:
            return {}
        
        # Role distribution
        role_counts = Counter(member.role for member in self.team_members)
        
        # Cultural background distribution
        cultural_counts = Counter(member.cultural_background for member in self.team_members)
        
        # Experience distribution
        experience_brackets = {
            "0-2 years": len([m for m in self.team_members if m.years_experience <= 2]),
            "3-5 years": len([m for m in self.team_members if 3 <= m.years_experience <= 5]),
            "6+ years": len([m for m in self.team_members if m.years_experience > 5])
        }
        
        # Language diversity
        all_languages = set()
        for member in self.team_members:
            all_languages.update(member.comfortable_languages)
        
        return {
            "total_members": len(self.team_members),
            "role_distribution": dict(role_counts),
            "cultural_diversity": dict(cultural_counts),
            "experience_distribution": experience_brackets,
            "language_diversity": list(all_languages),
            "first_job_members": len([m for m in self.team_members if m.is_first_job]),
            "family_obligations": len([m for m in self.team_members if m.has_extended_family_obligations])
        }
    
    def _analyze_trends(self) -> Dict:
        """Analyze trends in psychological safety over time"""
        if len(self.historical_scores) < 2:
            return {}
        
        latest = self.historical_scores[-1]
        previous = self.historical_scores[-2]
        
        score_change = latest.overall_score - previous.overall_score
        
        dimension_trends = {}
        for dimension in SafetyDimension:
            current_score = latest.dimension_scores[dimension]
            previous_score = previous.dimension_scores[dimension]
            change = current_score - previous_score
            
            if abs(change) >= 0.05:  # Significant change threshold
                trend = "improving" if change > 0 else "declining"
                dimension_trends[dimension.value] = {
                    "trend": trend,
                    "change": round(change * 100, 1)
                }
        
        return {
            "overall_trend": "improving" if score_change > 0 else "declining" if score_change < 0 else "stable",
            "score_change": round(score_change * 100, 1),
            "dimension_trends": dimension_trends,
            "measurements_count": len(self.historical_scores)
        }

def demo_psychological_safety_scorer():
    """Demo the psychological safety scoring system"""
    print("🛡️ Psychological Safety Scorer Demo - Indian Workplace Context")
    print("=" * 65)
    
    # Create team safety scorer
    scorer = PsychologicalSafetyScorer("TEAM_PAYMENTS")
    
    # Add diverse team members (Indian tech company scenario)
    members = [
        TeamMember(
            id="TM001",
            name="Rajesh Kumar",
            role=TeamRole.LEAD,
            years_experience=8,
            cultural_background=CulturalBackground.NORTH_INDIA,
            primary_language="Hindi",
            comfortable_languages=["Hindi", "English"],
            joining_date=datetime.now() - timedelta(days=1200),
            prefers_formal_communication=True
        ),
        
        TeamMember(
            id="TM002", 
            name="Priya Menon",
            role=TeamRole.SENIOR,
            years_experience=5,
            cultural_background=CulturalBackground.SOUTH_INDIA,
            primary_language="Malayalam",
            comfortable_languages=["Malayalam", "Tamil", "English"],
            joining_date=datetime.now() - timedelta(days=800),
            has_extended_family_obligations=True
        ),
        
        TeamMember(
            id="TM003",
            name="Amit Patel", 
            role=TeamRole.MID_LEVEL,
            years_experience=3,
            cultural_background=CulturalBackground.WEST_INDIA,
            primary_language="Gujarati",
            comfortable_languages=["Gujarati", "Hindi", "English"],
            joining_date=datetime.now() - timedelta(days=400)
        ),
        
        TeamMember(
            id="TM004",
            name="Sneha Singh",
            role=TeamRole.JUNIOR, 
            years_experience=1,
            cultural_background=CulturalBackground.TIER2_CITY,
            primary_language="Hindi",
            comfortable_languages=["Hindi", "English"],
            joining_date=datetime.now() - timedelta(days=120),
            is_first_job=True
        ),
        
        TeamMember(
            id="TM005",
            name="Arjun Reddy",
            role=TeamRole.INTERN,
            years_experience=0,
            cultural_background=CulturalBackground.SOUTH_INDIA,
            primary_language="Telugu", 
            comfortable_languages=["Telugu", "English"],
            joining_date=datetime.now() - timedelta(days=30),
            is_first_job=True
        )
    ]
    
    for member in members:
        scorer.add_team_member(member)
    
    print("\n" + "=" * 50)
    
    # Simulate various safety observations
    observations = [
        # Positive behaviors
        SafetyObservation(
            id="OBS001",
            timestamp=datetime.now() - timedelta(days=5),
            observer_id="TM001",
            team_member_id="TM004",
            dimension=SafetyDimension.ASK_QUESTIONS,
            behavior_description="Asked clarifying questions about payment flow in team meeting",
            positive_indicator=True,
            context="team meeting",
            cultural_sensitivity=0.8
        ),
        
        SafetyObservation(
            id="OBS002",
            timestamp=datetime.now() - timedelta(days=4),
            observer_id="TM001",
            team_member_id="TM002",
            dimension=SafetyDimension.CHALLENGE_IDEAS,
            behavior_description="Respectfully suggested alternative database design approach",
            positive_indicator=True,
            context="architecture review",
            hierarchy_involved=True,
            cultural_sensitivity=0.9
        ),
        
        SafetyObservation(
            id="OBS003",
            timestamp=datetime.now() - timedelta(days=3),
            observer_id="TM002",
            team_member_id="TM005",
            dimension=SafetyDimension.MAKE_MISTAKES,
            behavior_description="Admitted to introducing bug and asked for help fixing it",
            positive_indicator=True,
            context="code review",
            cultural_sensitivity=0.7
        ),
        
        SafetyObservation(
            id="OBS004",
            timestamp=datetime.now() - timedelta(days=3),
            observer_id="TM001",
            team_member_id="TM002",
            dimension=SafetyDimension.CULTURAL_INCLUSION,
            behavior_description="Explained Onam festival context while discussing Kerala user preferences",
            positive_indicator=True,
            context="product planning",
            cultural_sensitivity=1.0
        ),
        
        # Concerning behaviors
        SafetyObservation(
            id="OBS005",
            timestamp=datetime.now() - timedelta(days=2),
            observer_id="TM001",
            team_member_id="TM005",
            dimension=SafetyDimension.SPEAK_UP,
            behavior_description="Stayed silent during design discussion despite having concerns",
            positive_indicator=False,
            context="team meeting",
            hierarchy_involved=True,
            language_barrier=True
        ),
        
        SafetyObservation(
            id="OBS006",
            timestamp=datetime.now() - timedelta(days=1),
            observer_id="TM003",
            team_member_id="TM004",
            dimension=SafetyDimension.SHOW_VULNERABILITY,
            behavior_description="Pretended to understand complex concept instead of asking for explanation",
            positive_indicator=False,
            context="technical discussion",
            cultural_sensitivity=0.3
        ),
        
        # More positive behaviors
        SafetyObservation(
            id="OBS007",
            timestamp=datetime.now() - timedelta(hours=12),
            observer_id="TM002",
            team_member_id="TM003",
            dimension=SafetyDimension.HIERARCHY_RESPECT,
            behavior_description="Balanced respect with honest feedback to team lead about process improvement",
            positive_indicator=True,
            context="one-on-one meeting",
            hierarchy_involved=True,
            cultural_sensitivity=0.9
        )
    ]
    
    print("📊 Recording behavioral observations...")
    for obs in observations:
        scorer.record_observation(obs)
    
    print("\n" + "=" * 50)
    
    # Generate comprehensive safety report
    print("📋 Generating Team Psychological Safety Report...")
    safety_report = scorer.generate_safety_report()
    
    print(f"\n🎯 Team Psychological Safety Report")
    print(f"Team: {safety_report['team_id']}")
    print(f"Date: {safety_report['measurement_date']}")
    print(f"Overall Score: {safety_report['overall_score']}/100")
    print(f"Interpretation: {safety_report['score_interpretation']}")
    
    print(f"\n📊 Dimension Scores:")
    for dimension, score in safety_report['dimension_scores'].items():
        print(f"   {dimension.replace('_', ' ').title()}: {score}/100")
    
    print(f"\n🌈 Cultural Context Scores:")
    print(f"   Cultural Inclusion: {safety_report['cultural_inclusion_score']}/100")
    print(f"   Hierarchy Balance: {safety_report['hierarchy_balance_score']}/100")
    
    print(f"\n💪 Team Strengths:")
    for strength in safety_report['strengths']:
        print(f"   ✅ {strength}")
    
    print(f"\n🎯 Improvement Areas:")
    for area in safety_report['improvement_areas']:
        print(f"   📈 {area}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(safety_report['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n👥 Team Composition:")
    comp = safety_report['team_composition']
    print(f"   Total Members: {comp['total_members']}")
    print(f"   First Job Members: {comp['first_job_members']}")
    print(f"   Members with Family Obligations: {comp['family_obligations']}")
    print(f"   Language Diversity: {', '.join(comp['language_diversity'])}")
    
    print(f"\n👤 Individual Analyses (Sample):")
    for name, analysis in list(safety_report['individual_analyses'].items())[:2]:
        if 'error' not in analysis:
            print(f"   {name}:")
            print(f"     Participation: {analysis['overall_participation']} observations")
            print(f"     Positive Rate: {analysis['positive_behavior_rate']:.1%}")
            if analysis['patterns']:
                print(f"     Patterns: {', '.join(analysis['patterns'])}")
    
    print(f"\n📈 Data Summary:")
    print(f"   Total Observations: {safety_report['total_observations']}")
    print(f"   Recent Observations (30d): {safety_report['recent_observations']}")

if __name__ == "__main__":
    demo_psychological_safety_scorer()
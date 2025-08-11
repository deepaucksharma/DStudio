#!/usr/bin/env python3
"""
Blameless Postmortem Generator - Episode 3: Human Factor in Tech
===============================================================

Indian workplace mein blameless culture banana - respectful language use karte hue.
Galti se seekhna, blame nahi karna. "Koi baat nahi, agli baar better karenge" attitude.

Features:
- Respectful language patterns for Indian workplace
- Focus on system improvements rather than individual blame
- Cultural sensitivity in language and tone
- Learning-focused narrative generation
- Action item prioritization
- Team morale preservation

Based on practices from:
- Google SRE postmortem culture
- Netflix blameless postmortems  
- Indian IT companies' incident reviews
- Cultural adaptation for respect-based communication
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import json
import re
from collections import defaultdict

class IncidentSeverity(Enum):
    SEV1 = "Critical - Production completely down"
    SEV2 = "High - Major functionality affected"  
    SEV3 = "Medium - Minor issues with workaround"
    SEV4 = "Low - Cosmetic or non-critical issues"

class ActionPriority(Enum):
    IMMEDIATE = "immediate"    # Fix within 24 hours
    HIGH = "high"             # Fix within 1 week
    MEDIUM = "medium"         # Fix within 1 month
    LOW = "low"               # Fix when possible

class ComponentType(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"  
    DATABASE = "database"
    INFRASTRUCTURE = "infrastructure"
    MONITORING = "monitoring"
    PROCESS = "process"
    DOCUMENTATION = "documentation"

@dataclass
class TimelineEvent:
    """Timeline event with respectful documentation"""
    timestamp: datetime
    description: str
    actor: Optional[str] = None  # Who performed the action (optional for privacy)
    event_type: str = "action"   # action, detection, escalation, resolution
    impact: Optional[str] = None
    was_correct_action: bool = True  # For learning purposes, not blame

@dataclass
class ContributingFactor:
    """Contributing factor with no-blame framing"""
    factor_id: str
    category: ComponentType
    description: str
    why_it_contributed: str
    prevention_ideas: List[str] = field(default_factory=list)
    similar_incidents: List[str] = field(default_factory=list)

@dataclass 
class ActionItem:
    """Action item for improvement"""
    id: str
    description: str
    priority: ActionPriority
    assignee: Optional[str] = None
    estimated_effort: Optional[str] = None  # "2 days", "1 week", etc.
    category: ComponentType = ComponentType.PROCESS
    due_date: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    success_criteria: Optional[str] = None

@dataclass
class LearningPoint:
    """Key learning from the incident"""
    learning_id: str
    title: str
    description: str
    category: str  # "technical", "process", "communication", "monitoring"
    applicable_teams: List[str] = field(default_factory=list)
    knowledge_gap_filled: Optional[str] = None

class RespectfulLanguageProcessor:
    """Generate respectful, blameless language for Indian workplace"""
    
    def __init__(self):
        # Respectful language patterns
        self.respectful_phrases = {
            "system_focus": [
                "The system experienced",
                "Due to system configuration",
                "The process allowed for", 
                "System behavior resulted in",
                "Technical circumstances led to"
            ],
            
            "learning_focus": [
                "This provided an opportunity to learn",
                "We discovered that",
                "This incident helped us understand",
                "The situation revealed", 
                "We gained insight into"
            ],
            
            "improvement_focus": [
                "Moving forward, we will",
                "To prevent similar situations",
                "Our next steps include",
                "We plan to strengthen",
                "The team will implement"
            ],
            
            "acknowledgment": [
                "The team responded promptly",
                "Quick thinking helped minimize impact", 
                "Effective collaboration during resolution",
                "Good escalation following procedures",
                "Team showed excellent dedication"
            ],
            
            "indian_courtesy": [
                "With due respect to all involved",
                "Acknowledging everyone's best efforts",
                "Recognizing the team's commitment",
                "Appreciating the swift response",
                "Honoring the learning opportunity"
            ]
        }
        
        # Words to avoid (blame language)
        self.blame_words = [
            "fault", "blame", "mistake", "error", "wrong", "failed", "careless",
            "should have known", "obvious", "simple", "basic", "silly"
        ]
        
        # Respectful alternatives
        self.respectful_alternatives = {
            "mistake": "learning opportunity",
            "error": "unexpected behavior", 
            "failed": "did not perform as expected",
            "wrong": "different from intended",
            "fault": "contributing factor",
            "should have": "could have",
            "obvious": "clear in hindsight",
            "simple": "straightforward",
            "careless": "unintentional oversight"
        }
    
    def make_respectful(self, text: str) -> str:
        """Convert text to respectful, blameless language"""
        respectful_text = text.lower()
        
        # Replace blame words with respectful alternatives
        for blame_word, alternative in self.respectful_alternatives.items():
            respectful_text = respectful_text.replace(blame_word, alternative)
        
        # Capitalize first letter of sentences
        sentences = respectful_text.split('. ')
        respectful_text = '. '.join(sentence.capitalize() for sentence in sentences)
        
        return respectful_text
    
    def add_respectful_framing(self, description: str, context: str = "general") -> str:
        """Add respectful framing to descriptions"""
        if context == "timeline":
            return f"During this time, {description.lower()}"
        elif context == "learning":
            return f"This situation helped us understand that {description.lower()}"
        elif context == "improvement":
            return f"To enhance our system, {description.lower()}"
        else:
            return self.make_respectful(description)

class BlamelessPostmortemGenerator:
    """Main postmortem generator with Indian workplace cultural sensitivity"""
    
    def __init__(self):
        self.language_processor = RespectfulLanguageProcessor()
    
    def generate_postmortem(self, incident_data: Dict) -> Dict:
        """Generate complete blameless postmortem document"""
        
        # Validate required fields
        required_fields = ['title', 'severity', 'start_time', 'end_time', 'impact_description']
        for field in required_fields:
            if field not in incident_data:
                raise ValueError(f"Missing required field: {field}")
        
        postmortem = {
            # Header information
            "postmortem_id": f"PM-{datetime.now().strftime('%Y%m%d')}-{hash(incident_data['title']) % 10000}",
            "incident_title": incident_data['title'],
            "incident_date": incident_data['start_time'],
            "severity": incident_data['severity'],
            "duration_minutes": self._calculate_duration(incident_data['start_time'], incident_data['end_time']),
            "teams_involved": incident_data.get('teams_involved', []),
            "created_by": incident_data.get('created_by', 'System'),
            "created_date": datetime.now(),
            
            # Executive Summary (respectful)
            "executive_summary": self._generate_executive_summary(incident_data),
            
            # Impact Analysis
            "impact_analysis": self._generate_impact_analysis(incident_data),
            
            # Timeline (blameless)
            "timeline": self._generate_blameless_timeline(incident_data.get('timeline_events', [])),
            
            # Root Cause Analysis (system-focused)
            "contributing_factors": self._analyze_contributing_factors(incident_data.get('contributing_factors', [])),
            
            # What Went Well (positive reinforcement)
            "what_went_well": self._identify_positive_aspects(incident_data.get('positive_aspects', [])),
            
            # Learning Points
            "learning_points": self._extract_learning_points(incident_data),
            
            # Action Items (improvement-focused)
            "action_items": self._generate_action_items(incident_data.get('action_items', [])),
            
            # Prevention Strategies
            "prevention_strategies": self._suggest_prevention_strategies(incident_data),
            
            # Communication Plan
            "communication_plan": self._create_communication_plan(incident_data),
            
            # Cultural Acknowledgments
            "acknowledgments": self._generate_cultural_acknowledgments(incident_data)
        }
        
        return postmortem
    
    def _calculate_duration(self, start_time: str, end_time: str) -> int:
        """Calculate incident duration in minutes"""
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        return int((end - start).total_seconds() / 60)
    
    def _generate_executive_summary(self, incident_data: Dict) -> str:
        """Generate respectful executive summary"""
        severity = incident_data['severity']
        title = incident_data['title']
        impact = incident_data['impact_description']
        
        summary_template = f"""
On {incident_data['start_time'].split('T')[0]}, our system experienced an incident involving {title.lower()}. 
{self.language_processor.make_respectful(impact)}

The incident was classified as {severity} and lasted approximately {self._calculate_duration(incident_data['start_time'], incident_data['end_time'])} minutes. 
Our team responded promptly and implemented appropriate measures to restore service.

This incident provided valuable learning opportunities and has led to actionable improvements 
in our systems and processes. All team members demonstrated professionalism and dedication 
during the incident response.
        """.strip()
        
        return summary_template
    
    def _generate_impact_analysis(self, incident_data: Dict) -> Dict:
        """Generate impact analysis with respectful framing"""
        impact_data = incident_data.get('impact', {})
        
        return {
            "user_impact": {
                "affected_users": impact_data.get('affected_users', 'Unknown'),
                "user_experience": self.language_processor.make_respectful(
                    impact_data.get('user_experience', 'Some users experienced service disruption')
                ),
                "geographic_impact": impact_data.get('geographic_impact', 'Multiple regions')
            },
            
            "business_impact": {
                "revenue_impact": impact_data.get('revenue_impact', 'Minimal'),
                "reputation_impact": "Managed through transparent communication",
                "operational_impact": self.language_processor.make_respectful(
                    impact_data.get('operational_impact', 'Temporary operational adjustments required')
                )
            },
            
            "technical_impact": {
                "systems_affected": impact_data.get('systems_affected', []),
                "data_integrity": "Maintained throughout incident",
                "security_impact": "No security compromise detected"
            }
        }
    
    def _generate_blameless_timeline(self, events: List[Dict]) -> List[Dict]:
        """Generate blameless timeline focusing on system behavior"""
        blameless_timeline = []
        
        for event in events:
            timeline_event = {
                "timestamp": event.get('timestamp'),
                "description": self.language_processor.add_respectful_framing(
                    event.get('description', ''), "timeline"
                ),
                "type": event.get('type', 'system_event'),
                "impact": event.get('impact'),
                "response_quality": self._assess_response_quality(event)
            }
            
            # Remove any blame language
            timeline_event["description"] = self.language_processor.make_respectful(
                timeline_event["description"]
            )
            
            blameless_timeline.append(timeline_event)
        
        return blameless_timeline
    
    def _assess_response_quality(self, event: Dict) -> str:
        """Assess response quality in positive terms"""
        if event.get('was_effective', True):
            return "Appropriate response following procedures"
        else:
            return "Learning opportunity for process improvement"
    
    def _analyze_contributing_factors(self, factors: List[Dict]) -> List[Dict]:
        """Analyze contributing factors with system focus"""
        analyzed_factors = []
        
        for factor in factors:
            analyzed_factor = {
                "category": factor.get('category', 'system'),
                "description": self.language_processor.make_respectful(
                    factor.get('description', '')
                ),
                "system_behavior": f"The system behaved as configured, which allowed for {factor.get('contribution', 'the incident conditions')}",
                "improvement_opportunity": factor.get('improvement_opportunity', 'System enhancement identified'),
                "prevention_ideas": factor.get('prevention_ideas', [])
            }
            analyzed_factors.append(analyzed_factor)
        
        return analyzed_factors
    
    def _identify_positive_aspects(self, positive_data: List[Dict]) -> List[str]:
        """Identify what went well during the incident"""
        default_positives = [
            "Team responded promptly to incident notification",
            "Escalation procedures were followed appropriately", 
            "Communication channels remained effective throughout",
            "System monitoring detected the issue quickly",
            "Recovery procedures were executed successfully",
            "Team collaboration was exemplary during resolution",
            "Documentation was updated in real-time",
            "Customer communication was handled professionally"
        ]
        
        custom_positives = []
        for positive in positive_data:
            respectful_positive = self.language_processor.make_respectful(
                positive.get('description', '')
            )
            custom_positives.append(respectful_positive)
        
        return custom_positives if custom_positives else default_positives[:4]
    
    def _extract_learning_points(self, incident_data: Dict) -> List[Dict]:
        """Extract key learning points from incident"""
        learning_points = []
        
        # Technical learnings
        if 'technical_learnings' in incident_data:
            for learning in incident_data['technical_learnings']:
                learning_points.append({
                    "category": "Technical",
                    "title": learning.get('title', 'System Behavior Understanding'),
                    "description": self.language_processor.add_respectful_framing(
                        learning.get('description', ''), "learning"
                    ),
                    "applicable_to": learning.get('applicable_teams', ['All Engineering Teams'])
                })
        
        # Process learnings
        learning_points.append({
            "category": "Process",
            "title": "Incident Response Process Effectiveness", 
            "description": "This incident helped us understand our current process strengths and areas for enhancement",
            "applicable_to": ["All Teams"]
        })
        
        # Communication learnings
        learning_points.append({
            "category": "Communication",
            "title": "Cross-Team Coordination",
            "description": "We gained insights into effective communication patterns during high-stress situations",
            "applicable_to": ["Engineering", "Operations", "Support"]
        })
        
        return learning_points
    
    def _generate_action_items(self, action_data: List[Dict]) -> List[Dict]:
        """Generate improvement-focused action items"""
        action_items = []
        
        for action in action_data:
            action_item = {
                "id": action.get('id', f"AI-{len(action_items) + 1}"),
                "title": action.get('title', 'System Enhancement'),
                "description": self.language_processor.add_respectful_framing(
                    action.get('description', ''), "improvement"
                ),
                "priority": action.get('priority', ActionPriority.MEDIUM.value),
                "category": action.get('category', 'process'),
                "assignee": action.get('assignee', 'Team Lead'),
                "estimated_effort": action.get('estimated_effort', '1 week'),
                "success_criteria": action.get('success_criteria', 'Implementation completed and tested'),
                "due_date": action.get('due_date'),
                "rationale": f"This enhancement will help prevent similar system behaviors in the future"
            }
            action_items.append(action_item)
        
        # Add default action items if none provided
        if not action_items:
            default_actions = [
                {
                    "id": "AI-1",
                    "title": "Enhance Monitoring and Alerting",
                    "description": "Implement additional monitoring to detect similar conditions earlier",
                    "priority": ActionPriority.HIGH.value,
                    "category": "monitoring",
                    "estimated_effort": "1 week"
                },
                {
                    "id": "AI-2", 
                    "title": "Update Incident Response Procedures",
                    "description": "Incorporate learnings from this incident into our response procedures",
                    "priority": ActionPriority.MEDIUM.value,
                    "category": "process",
                    "estimated_effort": "3 days"
                }
            ]
            action_items.extend(default_actions)
        
        return action_items
    
    def _suggest_prevention_strategies(self, incident_data: Dict) -> List[Dict]:
        """Suggest prevention strategies"""
        strategies = [
            {
                "category": "Technical Prevention",
                "strategies": [
                    "Implement circuit breakers for external dependencies",
                    "Add comprehensive health checks for all critical services",
                    "Enhance automated testing coverage for edge cases",
                    "Implement gradual rollout procedures for configuration changes"
                ]
            },
            {
                "category": "Process Prevention", 
                "strategies": [
                    "Conduct regular disaster recovery drills",
                    "Implement peer review for all infrastructure changes",
                    "Create detailed runbooks for common scenarios",
                    "Establish clear escalation criteria and procedures"
                ]
            },
            {
                "category": "Cultural Prevention",
                "strategies": [
                    "Foster blameless culture where reporting issues is encouraged",
                    "Regular team retrospectives to identify process improvements",
                    "Cross-team knowledge sharing sessions",
                    "Psychological safety workshops for all team members"
                ]
            }
        ]
        
        return strategies
    
    def _create_communication_plan(self, incident_data: Dict) -> Dict:
        """Create respectful communication plan"""
        return {
            "internal_communication": {
                "engineering_team": "Share technical learnings and improvements in next team meeting",
                "management": "Present incident summary focusing on improvements and prevention",
                "other_teams": "Share relevant learnings that might apply to their systems"
            },
            
            "external_communication": {
                "customers": "Transparent update on improvements made (if customer-facing incident)",
                "stakeholders": "Summary of incident response effectiveness and future improvements",
                "public": "Professional communication emphasizing our commitment to reliability"
            },
            
            "follow_up": {
                "one_week": "Review progress on immediate action items",
                "one_month": "Assess effectiveness of implemented improvements",
                "quarterly": "Include learnings in broader system reliability review"
            }
        }
    
    def _generate_cultural_acknowledgments(self, incident_data: Dict) -> Dict:
        """Generate cultural acknowledgments respecting Indian workplace values"""
        return {
            "team_appreciation": [
                "We acknowledge the dedication and professionalism shown by all team members during this incident",
                "The collaborative spirit demonstrated reflects the strong team culture we have built",
                "Special recognition for maintaining composure and following procedures under pressure",
                "Thank you to everyone who contributed to the swift resolution of this incident"
            ],
            
            "learning_mindset": [
                "This incident represents a valuable learning opportunity for our entire organization",
                "We approach this postmortem with curiosity and a commitment to improvement",
                "Every challenge helps us build a more resilient and reliable system",
                "We view this as part of our continuous journey toward operational excellence"
            ],
            
            "respect_and_dignity": [
                "All individuals involved acted with the best intentions and available information",
                "We recognize that complex systems can behave unexpectedly despite our best efforts",
                "This postmortem is conducted in a spirit of mutual respect and shared learning",
                "We honor the commitment of all team members to our users and our mission"
            ]
        }
    
    def format_postmortem_document(self, postmortem_data: Dict) -> str:
        """Format postmortem as readable document"""
        doc = f"""
# Incident Postmortem: {postmortem_data['incident_title']}

**Postmortem ID:** {postmortem_data['postmortem_id']}  
**Incident Date:** {postmortem_data['incident_date']}  
**Severity:** {postmortem_data['severity']}  
**Duration:** {postmortem_data['duration_minutes']} minutes  
**Teams Involved:** {', '.join(postmortem_data['teams_involved'])}  
**Created By:** {postmortem_data['created_by']}  
**Created Date:** {postmortem_data['created_date'].strftime('%Y-%m-%d %H:%M')}  

## Executive Summary

{postmortem_data['executive_summary']}

## Impact Analysis

### User Impact
- **Affected Users:** {postmortem_data['impact_analysis']['user_impact']['affected_users']}
- **User Experience:** {postmortem_data['impact_analysis']['user_impact']['user_experience']}
- **Geographic Impact:** {postmortem_data['impact_analysis']['user_impact']['geographic_impact']}

### Business Impact
- **Revenue Impact:** {postmortem_data['impact_analysis']['business_impact']['revenue_impact']}
- **Reputation Impact:** {postmortem_data['impact_analysis']['business_impact']['reputation_impact']}
- **Operational Impact:** {postmortem_data['impact_analysis']['business_impact']['operational_impact']}

## Timeline

"""
        # Add timeline events
        for event in postmortem_data['timeline']:
            doc += f"**{event['timestamp']}** - {event['description']}\n"
            if event.get('impact'):
                doc += f"  - Impact: {event['impact']}\n"
            doc += "\n"
        
        doc += f"""
## Contributing Factors

"""
        # Add contributing factors
        for i, factor in enumerate(postmortem_data['contributing_factors'], 1):
            doc += f"{i}. **{factor['category'].title()}**: {factor['description']}\n"
            doc += f"   - System Behavior: {factor['system_behavior']}\n"
            doc += f"   - Improvement Opportunity: {factor['improvement_opportunity']}\n\n"
        
        doc += f"""
## What Went Well

"""
        for positive in postmortem_data['what_went_well']:
            doc += f"- {positive}\n"
        
        doc += f"""

## Learning Points

"""
        for learning in postmortem_data['learning_points']:
            doc += f"### {learning['title']} ({learning['category']})\n"
            doc += f"{learning['description']}\n"
            doc += f"**Applicable To:** {', '.join(learning['applicable_to'])}\n\n"
        
        doc += f"""
## Action Items

"""
        for action in postmortem_data['action_items']:
            doc += f"### {action['id']}: {action['title']}\n"
            doc += f"**Priority:** {action['priority']}\n"
            doc += f"**Description:** {action['description']}\n"
            doc += f"**Assignee:** {action['assignee']}\n"
            doc += f"**Estimated Effort:** {action['estimated_effort']}\n"
            doc += f"**Success Criteria:** {action['success_criteria']}\n\n"
        
        doc += f"""
## Prevention Strategies

"""
        for strategy_group in postmortem_data['prevention_strategies']:
            doc += f"### {strategy_group['category']}\n"
            for strategy in strategy_group['strategies']:
                doc += f"- {strategy}\n"
            doc += "\n"
        
        doc += f"""
## Acknowledgments

### Team Appreciation
"""
        for ack in postmortem_data['acknowledgments']['team_appreciation']:
            doc += f"- {ack}\n"
        
        doc += f"""
### Learning Mindset
"""
        for ack in postmortem_data['acknowledgments']['learning_mindset']:
            doc += f"- {ack}\n"
        
        doc += f"""
### Respect and Dignity
"""
        for ack in postmortem_data['acknowledgments']['respect_and_dignity']:
            doc += f"- {ack}\n"
        
        doc += f"""

---
*This postmortem was generated with a focus on learning, improvement, and respect for all individuals involved.*
"""
        
        return doc.strip()

def demo_blameless_postmortem_generator():
    """Demo the blameless postmortem generator"""
    print("📋 Blameless Postmortem Generator Demo - Indian Workplace Culture")
    print("=" * 70)
    
    generator = BlamelessPostmortemGenerator()
    
    # Sample incident data (Payment gateway failure - common in Indian fintech)
    incident_data = {
        "title": "Payment Gateway Timeout During Peak Traffic",
        "severity": "SEV1",
        "start_time": "2024-03-15T18:30:00Z",
        "end_time": "2024-03-15T19:45:00Z", 
        "impact_description": "Users unable to complete transactions during evening peak hours",
        "teams_involved": ["Backend Engineering", "DevOps", "Support", "Product"],
        "created_by": "Rajesh Kumar (SRE Lead)",
        
        "impact": {
            "affected_users": "Approximately 50,000 users",
            "user_experience": "Transaction timeouts and error messages during checkout",
            "geographic_impact": "Mumbai, Delhi, Bangalore primarily affected",
            "revenue_impact": "Estimated ₹12 lakhs in lost transactions",
            "systems_affected": ["Payment Service", "Database Cluster", "Load Balancer"]
        },
        
        "timeline_events": [
            {
                "timestamp": "2024-03-15T18:30:00Z",
                "description": "First payment timeout alerts received",
                "type": "detection",
                "impact": "Initial user reports started"
            },
            {
                "timestamp": "2024-03-15T18:35:00Z", 
                "description": "Database connection pool exhaustion identified",
                "type": "diagnosis",
                "impact": "Root cause direction established"
            },
            {
                "timestamp": "2024-03-15T18:45:00Z",
                "description": "Emergency database scaling initiated",
                "type": "mitigation",
                "impact": "Partial service restoration began"
            },
            {
                "timestamp": "2024-03-15T19:15:00Z",
                "description": "Additional connection pool configured",
                "type": "resolution",
                "impact": "Full service restoration achieved"
            }
        ],
        
        "contributing_factors": [
            {
                "category": "infrastructure",
                "description": "Database connection pool was configured for average load, not peak traffic",
                "contribution": "pool exhaustion during traffic spike", 
                "improvement_opportunity": "Dynamic scaling configuration",
                "prevention_ideas": ["Auto-scaling connection pools", "Load testing with realistic traffic patterns"]
            },
            {
                "category": "monitoring",
                "description": "Connection pool utilization was not monitored with appropriate thresholds",
                "contribution": "delayed detection of resource exhaustion",
                "improvement_opportunity": "Enhanced monitoring coverage",
                "prevention_ideas": ["Pool utilization alerts", "Predictive threshold alerts"]
            }
        ],
        
        "positive_aspects": [
            {
                "description": "Incident was detected within 5 minutes of occurrence"
            },
            {
                "description": "Team escalation followed standard procedures effectively"
            },
            {
                "description": "Customer communication was prompt and transparent"
            }
        ],
        
        "technical_learnings": [
            {
                "title": "Database Connection Pool Behavior Under Load",
                "description": "Connection pools need to be sized for peak traffic, not average load patterns",
                "applicable_teams": ["Backend Engineering", "Infrastructure"]
            }
        ],
        
        "action_items": [
            {
                "id": "AI-001",
                "title": "Implement Auto-Scaling Connection Pools",
                "description": "Configure database connection pools to scale automatically based on traffic patterns",
                "priority": "immediate",
                "category": "infrastructure",
                "assignee": "DevOps Team",
                "estimated_effort": "1 week",
                "success_criteria": "Connection pools auto-scale during load testing"
            },
            {
                "id": "AI-002", 
                "title": "Enhanced Database Monitoring",
                "description": "Add comprehensive monitoring for all database resource utilization",
                "priority": "high",
                "category": "monitoring",
                "assignee": "SRE Team",
                "estimated_effort": "3 days",
                "success_criteria": "All database resources monitored with appropriate alerts"
            }
        ]
    }
    
    print("📊 Generating blameless postmortem...")
    postmortem = generator.generate_postmortem(incident_data)
    
    print("📄 Formatting postmortem document...")
    formatted_doc = generator.format_postmortem_document(postmortem)
    
    # Print key sections of the postmortem
    print("\n" + "=" * 50)
    print("🎯 SAMPLE POSTMORTEM SECTIONS:")
    print("=" * 50)
    
    print(f"\n📋 EXECUTIVE SUMMARY:")
    print(postmortem['executive_summary'])
    
    print(f"\n⏱️ INCIDENT DETAILS:")
    print(f"Duration: {postmortem['duration_minutes']} minutes")
    print(f"Severity: {postmortem['severity']}")
    print(f"Teams: {', '.join(postmortem['teams_involved'])}")
    
    print(f"\n✅ WHAT WENT WELL:")
    for positive in postmortem['what_went_well'][:3]:
        print(f"   • {positive}")
    
    print(f"\n🔍 CONTRIBUTING FACTORS (System-Focused):")
    for i, factor in enumerate(postmortem['contributing_factors'], 1):
        print(f"   {i}. {factor['description']}")
        print(f"      System Behavior: {factor['system_behavior']}")
        print()
    
    print(f"\n📚 LEARNING POINTS:")
    for learning in postmortem['learning_points'][:2]:
        print(f"   • {learning['title']}: {learning['description']}")
    
    print(f"\n🎯 ACTION ITEMS:")
    for action in postmortem['action_items']:
        print(f"   • {action['id']}: {action['title']}")
        print(f"     Priority: {action['priority']}, Effort: {action['estimated_effort']}")
        print(f"     {action['description']}")
        print()
    
    print(f"\n🙏 CULTURAL ACKNOWLEDGMENTS:")
    print("Team Appreciation:")
    for ack in postmortem['acknowledgments']['team_appreciation'][:2]:
        print(f"   • {ack}")
    
    print(f"\nLearning Mindset:")
    for ack in postmortem['acknowledgments']['learning_mindset'][:2]:
        print(f"   • {ack}")
    
    print(f"\n📈 LANGUAGE PROCESSING DEMO:")
    processor = generator.language_processor
    
    blame_examples = [
        "The developer made a mistake in the configuration",
        "This was a simple error that should have been caught",
        "The team failed to follow the obvious procedure"
    ]
    
    print("Before (Blame Language) -> After (Respectful Language):")
    for example in blame_examples:
        respectful = processor.make_respectful(example)
        print(f"   '{example}'")
        print(f"   -> '{respectful}'\n")

if __name__ == "__main__":
    demo_blameless_postmortem_generator()
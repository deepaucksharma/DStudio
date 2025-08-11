#!/usr/bin/env python3
"""
Communication Effectiveness Analyzer - Episode 3: Human Factor in Tech
======================================================================

Multilingual Indian teams mein communication patterns analyze karna. Hinglish, hierarchy,
aur cultural context ke saath effective communication measure karta hai.

Features:
- Multilingual communication pattern analysis
- Hierarchy-aware communication scoring
- Cultural context understanding
- Response time analysis across teams
- Information flow bottleneck detection
- Meeting effectiveness in mixed language environments

Indian Workplace Context:
- Hindi/English code-switching patterns
- Respectful hierarchy communication
- Regional language comfort levels
- Festival season communication adjustments
- Extended family notification patterns
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
import json
import re
import statistics
from collections import defaultdict, Counter

class CommunicationChannel(Enum):
    SLACK = "slack"
    EMAIL = "email" 
    WHATSAPP = "whatsapp"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"

class MessageLanguage(Enum):
    ENGLISH = "english"
    HINDI = "hindi"
    HINGLISH = "hinglish"  # Mixed Hindi-English
    REGIONAL = "regional"  # Tamil, Telugu, Malayalam, etc.
    TECHNICAL_ENGLISH = "technical_english"  # Pure technical terms

class HierarchyLevel(Enum):
    INTERN = 1
    JUNIOR = 2
    MID_LEVEL = 3
    SENIOR = 4
    LEAD = 5
    MANAGER = 6
    DIRECTOR = 7

class CommunicationType(Enum):
    INFORMATION_SHARING = "info_sharing"
    QUESTION_ASKING = "question"
    PROBLEM_REPORTING = "problem_report"
    DECISION_MAKING = "decision"
    FEEDBACK_GIVING = "feedback"
    SOCIAL_INTERACTION = "social"
    ESCALATION = "escalation"
    DELEGATION = "delegation"

@dataclass
class CommunicationMessage:
    """Individual communication message with Indian context"""
    id: str
    timestamp: datetime
    sender_id: str
    recipient_ids: List[str]
    channel: CommunicationChannel
    content: str
    language: MessageLanguage
    communication_type: CommunicationType
    urgency_level: int  # 1-5 scale
    response_required: bool
    cultural_context_score: float  # How culturally appropriate the message is
    
    # Response tracking
    responses: List[str] = field(default_factory=list)  # Response message IDs
    first_response_time: Optional[datetime] = None
    all_responses_time: Optional[datetime] = None
    
    # Analysis fields
    sentiment_score: float = 0.0  # -1 to 1
    clarity_score: float = 0.0    # 0 to 1
    respectfulness_score: float = 0.0  # 0 to 1
    technical_accuracy: float = 0.0    # 0 to 1

@dataclass
class TeamMember:
    """Team member with communication preferences and cultural context"""
    id: str
    name: str
    email: str
    hierarchy_level: HierarchyLevel
    primary_language: str
    comfortable_languages: List[str]
    region_of_origin: str
    communication_style: str  # "formal", "casual", "direct", "diplomatic"
    response_time_preference: timedelta  # Preferred response time
    meeting_language_preference: str
    written_language_preference: str
    
    # Communication patterns
    average_response_time: Dict[CommunicationChannel, timedelta] = field(default_factory=dict)
    communication_frequency: Dict[str, int] = field(default_factory=dict)  # person_id -> frequency
    preferred_channels: List[CommunicationChannel] = field(default_factory=list)
    
    # Cultural factors
    uses_sir_madam: bool = True
    comfort_with_hierarchy_bypass: float = 0.3  # 0-1 scale
    festival_communication_pattern: Dict[str, str] = field(default_factory=dict)

@dataclass
class CommunicationMetrics:
    """Comprehensive communication effectiveness metrics"""
    team_id: str
    analysis_period_start: datetime
    analysis_period_end: datetime
    
    # Overall effectiveness
    overall_communication_score: float
    information_flow_efficiency: float
    hierarchy_communication_health: float
    multilingual_effectiveness: float
    
    # Response time metrics
    average_response_time: Dict[CommunicationChannel, timedelta]
    response_time_by_hierarchy: Dict[HierarchyLevel, timedelta]
    urgent_message_response_rate: float
    
    # Language and cultural metrics
    language_distribution: Dict[MessageLanguage, float]
    cross_language_communication_success: float
    cultural_appropriateness_score: float
    hierarchy_respect_score: float
    
    # Bottleneck analysis
    communication_bottlenecks: List[str]  # Member IDs who are bottlenecks
    information_silos: List[Set[str]]     # Groups that don't communicate much
    over_communicators: List[str]         # Members who communicate excessively
    under_communicators: List[str]        # Members who communicate too little
    
    # Quality metrics
    message_clarity_average: float
    technical_accuracy_average: float
    sentiment_distribution: Dict[str, float]  # positive, neutral, negative
    
    # Improvement recommendations
    recommendations: List[str]

class LanguageAnalyzer:
    """Analyze language patterns in Indian workplace communication"""
    
    def __init__(self):
        # Common Hinglish patterns
        self.hinglish_indicators = [
            r'\b(kar|karo|karna|kiye|kiya)\b',  # Hindi verbs mixed with English
            r'\b(hai|hain|ho|hoga|hoge)\b',     # Hindi auxiliary verbs
            r'\b(acha|aap|hum|main|ye|wo)\b',   # Hindi pronouns/adjectives
            r'\b(sir|madam|ji)\b',              # Respectful suffixes
            r'\b(thik|sahi|galat)\b',           # Hindi adjectives
        ]
        
        # Technical English patterns
        self.technical_patterns = [
            r'\b(API|HTTP|JSON|SQL|AWS|REST)\b',
            r'\b(function|variable|class|method)\b',
            r'\b(database|server|client|frontend)\b',
            r'\b(authentication|authorization)\b',
        ]
        
        # Respectful communication patterns
        self.respectful_patterns = [
            r'\b(please|kindly|request|would you)\b',
            r'\b(thank you|thanks|grateful)\b',
            r'\b(sir|madam|respected)\b',
            r'\b(aapka|aapki|aapse)\b',  # Respectful Hindi pronouns
        ]
    
    def detect_language(self, text: str) -> MessageLanguage:
        """Detect the primary language of communication"""
        text_lower = text.lower()
        
        # Count technical terms
        technical_count = sum(1 for pattern in self.technical_patterns 
                            if re.search(pattern, text_lower))
        
        # Count Hinglish indicators
        hinglish_count = sum(1 for pattern in self.hinglish_indicators 
                           if re.search(pattern, text_lower))
        
        # Simple heuristics
        total_words = len(text_lower.split())
        
        if technical_count > total_words * 0.3:
            return MessageLanguage.TECHNICAL_ENGLISH
        elif hinglish_count > 0:
            return MessageLanguage.HINGLISH
        elif any(hindi_word in text_lower for hindi_word in ['namaste', 'dhanyawad', 'kripaya']):
            return MessageLanguage.HINDI
        else:
            return MessageLanguage.ENGLISH
    
    def calculate_clarity_score(self, text: str, language: MessageLanguage) -> float:
        """Calculate message clarity score"""
        # Basic clarity metrics
        words = text.split()
        sentences = text.split('.')
        
        if not words:
            return 0.0
        
        # Average sentence length (optimal: 10-20 words)
        avg_sentence_length = len(words) / len(sentences) if sentences else len(words)
        length_score = 1.0
        if avg_sentence_length > 25:
            length_score = max(0.3, 1 - (avg_sentence_length - 25) * 0.02)
        elif avg_sentence_length < 5:
            length_score = avg_sentence_length / 5
        
        # Question mark for questions improves clarity
        has_question_structure = '?' in text or any(
            q_word in text.lower() for q_word in ['what', 'when', 'where', 'why', 'how', 'kya', 'kab', 'kahan']
        )
        
        # Technical terms usage appropriateness
        technical_terms = sum(1 for pattern in self.technical_patterns 
                            if re.search(pattern, text.lower()))
        tech_appropriateness = min(1.0, technical_terms / max(1, len(words) * 0.1))
        
        # Language consistency
        consistency_score = 1.0
        if language == MessageLanguage.HINGLISH:
            # Hinglish should have balanced mixing
            hindi_indicators = sum(1 for pattern in self.hinglish_indicators 
                                 if re.search(pattern, text.lower()))
            if hindi_indicators == 0 or hindi_indicators > len(words) * 0.5:
                consistency_score = 0.7
        
        clarity = (length_score * 0.4 + tech_appropriateness * 0.3 + consistency_score * 0.3)
        return min(1.0, clarity)
    
    def calculate_respectfulness_score(self, text: str, sender_level: HierarchyLevel, 
                                     recipient_levels: List[HierarchyLevel]) -> float:
        """Calculate respectfulness based on hierarchy and cultural context"""
        text_lower = text.lower()
        
        # Count respectful patterns
        respectful_count = sum(1 for pattern in self.respectful_patterns 
                             if re.search(pattern, text_lower))
        
        # Base respectfulness from pattern detection
        base_respect = min(1.0, respectful_count / 3)  # Normalize
        
        # Adjust for hierarchy
        max_recipient_level = max(level.value for level in recipient_levels) if recipient_levels else sender_level.value
        
        hierarchy_adjustment = 0.0
        if max_recipient_level > sender_level.value:  # Communicating upward
            # Should be more respectful
            expected_respect = (max_recipient_level - sender_level.value) * 0.2
            if base_respect >= expected_respect:
                hierarchy_adjustment = 0.1
            else:
                hierarchy_adjustment = -0.2  # Penalty for insufficient respect
        
        # Indian cultural patterns
        has_sir_madam = bool(re.search(r'\b(sir|madam|ji)\b', text_lower))
        cultural_bonus = 0.1 if has_sir_madam else 0.0
        
        # Avoid negative tone
        negative_words = ['stupid', 'wrong', 'bad', 'terrible', 'horrible']
        has_negative = any(word in text_lower for word in negative_words)
        negative_penalty = -0.3 if has_negative else 0.0
        
        respectfulness = base_respect + hierarchy_adjustment + cultural_bonus + negative_penalty
        return max(0.0, min(1.0, respectfulness))

class CommunicationEffectivenessAnalyzer:
    """Main analyzer for team communication effectiveness"""
    
    def __init__(self):
        self.language_analyzer = LanguageAnalyzer()
        self.team_members: Dict[str, TeamMember] = {}
        self.messages: List[CommunicationMessage] = []
        
        # Indian workplace communication norms
        self.expected_response_times = {
            CommunicationChannel.WHATSAPP: timedelta(minutes=15),
            CommunicationChannel.SLACK: timedelta(hours=2),
            CommunicationChannel.EMAIL: timedelta(hours=24),
            CommunicationChannel.VIDEO_CALL: timedelta(hours=4),  # For scheduling
        }
        
        self.hierarchy_response_expectations = {
            HierarchyLevel.DIRECTOR: timedelta(days=2),
            HierarchyLevel.MANAGER: timedelta(hours=12),
            HierarchyLevel.LEAD: timedelta(hours=4),
            HierarchyLevel.SENIOR: timedelta(hours=2),
            HierarchyLevel.MID_LEVEL: timedelta(hours=1),
            HierarchyLevel.JUNIOR: timedelta(minutes=30),
            HierarchyLevel.INTERN: timedelta(minutes=15),
        }
    
    def add_team_member(self, member: TeamMember):
        """Add team member to communication analysis"""
        self.team_members[member.id] = member
        print(f"👤 Added {member.name} ({member.hierarchy_level.name}) to communication analysis")
        
        if len(member.comfortable_languages) > 1:
            print(f"   🌐 Multilingual: {', '.join(member.comfortable_languages)}")
        
        if member.uses_sir_madam:
            print(f"   🙏 Uses respectful addressing (Sir/Madam)")
    
    def record_message(self, message: CommunicationMessage):
        """Record communication message for analysis"""
        # Auto-detect language if not specified
        if not hasattr(message, 'language') or not message.language:
            message.language = self.language_analyzer.detect_language(message.content)
        
        # Calculate clarity score
        message.clarity_score = self.language_analyzer.calculate_clarity_score(
            message.content, message.language)
        
        # Calculate respectfulness score
        sender = self.team_members.get(message.sender_id)
        recipient_levels = []
        for recipient_id in message.recipient_ids:
            recipient = self.team_members.get(recipient_id)
            if recipient:
                recipient_levels.append(recipient.hierarchy_level)
        
        if sender and recipient_levels:
            message.respectfulness_score = self.language_analyzer.calculate_respectfulness_score(
                message.content, sender.hierarchy_level, recipient_levels)
        
        # Calculate cultural context score (simplified)
        message.cultural_context_score = self._calculate_cultural_context_score(message)
        
        self.messages.append(message)
        
        print(f"📨 Message recorded: {message.communication_type.value} via {message.channel.value}")
        print(f"   Language: {message.language.value}, Clarity: {message.clarity_score:.2f}")
    
    def _calculate_cultural_context_score(self, message: CommunicationMessage) -> float:
        """Calculate how well the message fits cultural context"""
        score = 0.5  # Base score
        
        # Respectful greeting patterns
        if any(greeting in message.content.lower() 
               for greeting in ['namaste', 'good morning', 'hope you are well']):
            score += 0.2
        
        # Appropriate channel usage
        if message.channel == CommunicationChannel.WHATSAPP and message.urgency_level >= 4:
            score += 0.1  # WhatsApp for urgent is culturally appropriate
        elif message.channel == CommunicationChannel.EMAIL and message.urgency_level <= 2:
            score += 0.1  # Email for non-urgent is appropriate
        
        # Language appropriateness
        if message.language == MessageLanguage.HINGLISH:
            score += 0.1  # Hinglish is natural in Indian workplace
        
        # Time consideration (not sending late night messages unless urgent)
        hour = message.timestamp.hour
        if 22 <= hour <= 6 and message.urgency_level < 4:
            score -= 0.3  # Penalty for non-urgent late night messages
        
        return max(0.0, min(1.0, score))
    
    def track_response(self, original_message_id: str, response_message_id: str, 
                      response_timestamp: datetime):
        """Track response to a message"""
        original_message = next((m for m in self.messages if m.id == original_message_id), None)
        if not original_message:
            return
        
        original_message.responses.append(response_message_id)
        
        if original_message.first_response_time is None:
            original_message.first_response_time = response_timestamp
        
        # Update all responses time
        original_message.all_responses_time = response_timestamp
        
        response_time = response_timestamp - original_message.timestamp
        print(f"⏱️ Response tracked: {response_time.total_seconds()/60:.1f} minutes")
    
    def analyze_communication_effectiveness(self, team_id: str, 
                                          start_date: datetime, 
                                          end_date: datetime) -> CommunicationMetrics:
        """Analyze comprehensive communication effectiveness"""
        
        # Filter messages for the time period
        period_messages = [m for m in self.messages 
                          if start_date <= m.timestamp <= end_date]
        
        if not period_messages:
            return self._create_empty_metrics(team_id, start_date, end_date)
        
        # Calculate core metrics
        overall_score = self._calculate_overall_communication_score(period_messages)
        info_flow_efficiency = self._calculate_information_flow_efficiency(period_messages)
        hierarchy_health = self._calculate_hierarchy_communication_health(period_messages)
        multilingual_effectiveness = self._calculate_multilingual_effectiveness(period_messages)
        
        # Response time analysis
        response_times = self._analyze_response_times(period_messages)
        urgent_response_rate = self._calculate_urgent_response_rate(period_messages)
        
        # Language and cultural analysis
        language_dist = self._analyze_language_distribution(period_messages)
        cross_lang_success = self._analyze_cross_language_communication(period_messages)
        cultural_score = self._calculate_cultural_appropriateness(period_messages)
        hierarchy_respect = self._calculate_hierarchy_respect_score(period_messages)
        
        # Bottleneck analysis
        bottlenecks = self._identify_communication_bottlenecks(period_messages)
        silos = self._identify_information_silos(period_messages)
        over_comm = self._identify_over_communicators(period_messages)
        under_comm = self._identify_under_communicators(period_messages)
        
        # Quality metrics
        clarity_avg = statistics.mean(m.clarity_score for m in period_messages if m.clarity_score > 0)
        respect_avg = statistics.mean(m.respectfulness_score for m in period_messages if m.respectfulness_score > 0)
        sentiment_dist = self._analyze_sentiment_distribution(period_messages)
        
        # Generate recommendations
        recommendations = self._generate_improvement_recommendations(
            period_messages, bottlenecks, language_dist, response_times)
        
        return CommunicationMetrics(
            team_id=team_id,
            analysis_period_start=start_date,
            analysis_period_end=end_date,
            overall_communication_score=overall_score,
            information_flow_efficiency=info_flow_efficiency,
            hierarchy_communication_health=hierarchy_health,
            multilingual_effectiveness=multilingual_effectiveness,
            average_response_time=response_times['by_channel'],
            response_time_by_hierarchy=response_times['by_hierarchy'],
            urgent_message_response_rate=urgent_response_rate,
            language_distribution=language_dist,
            cross_language_communication_success=cross_lang_success,
            cultural_appropriateness_score=cultural_score,
            hierarchy_respect_score=hierarchy_respect,
            communication_bottlenecks=bottlenecks,
            information_silos=silos,
            over_communicators=over_comm,
            under_communicators=under_comm,
            message_clarity_average=clarity_avg,
            technical_accuracy_average=respect_avg,  # Using respectfulness as proxy
            sentiment_distribution=sentiment_dist,
            recommendations=recommendations
        )
    
    def _create_empty_metrics(self, team_id: str, start_date: datetime, 
                            end_date: datetime) -> CommunicationMetrics:
        """Create empty metrics when no messages found"""
        return CommunicationMetrics(
            team_id=team_id,
            analysis_period_start=start_date,
            analysis_period_end=end_date,
            overall_communication_score=0.0,
            information_flow_efficiency=0.0,
            hierarchy_communication_health=0.0,
            multilingual_effectiveness=0.0,
            average_response_time={},
            response_time_by_hierarchy={},
            urgent_message_response_rate=0.0,
            language_distribution={},
            cross_language_communication_success=0.0,
            cultural_appropriateness_score=0.0,
            hierarchy_respect_score=0.0,
            communication_bottlenecks=[],
            information_silos=[],
            over_communicators=[],
            under_communicators=[],
            message_clarity_average=0.0,
            technical_accuracy_average=0.0,
            sentiment_distribution={},
            recommendations=["No communication data available for analysis"]
        )
    
    def _calculate_overall_communication_score(self, messages: List[CommunicationMessage]) -> float:
        """Calculate overall communication effectiveness score"""
        if not messages:
            return 0.0
        
        # Component scores
        clarity_score = statistics.mean(m.clarity_score for m in messages if m.clarity_score > 0)
        respect_score = statistics.mean(m.respectfulness_score for m in messages if m.respectfulness_score > 0)
        cultural_score = statistics.mean(m.cultural_context_score for m in messages if m.cultural_context_score > 0)
        
        # Response rate score
        messages_requiring_response = [m for m in messages if m.response_required]
        response_rate = (len([m for m in messages_requiring_response if m.responses]) / 
                        len(messages_requiring_response)) if messages_requiring_response else 1.0
        
        # Weighted overall score
        overall = (clarity_score * 0.3 + respect_score * 0.25 + 
                  cultural_score * 0.25 + response_rate * 0.2)
        
        return min(1.0, overall)
    
    def _analyze_response_times(self, messages: List[CommunicationMessage]) -> Dict:
        """Analyze response time patterns"""
        by_channel = {}
        by_hierarchy = {}
        
        for message in messages:
            if message.first_response_time and message.response_required:
                response_time = message.first_response_time - message.timestamp
                
                # By channel
                if message.channel not in by_channel:
                    by_channel[message.channel] = []
                by_channel[message.channel].append(response_time)
                
                # By hierarchy (sender hierarchy)
                sender = self.team_members.get(message.sender_id)
                if sender:
                    if sender.hierarchy_level not in by_hierarchy:
                        by_hierarchy[sender.hierarchy_level] = []
                    by_hierarchy[sender.hierarchy_level].append(response_time)
        
        # Calculate averages
        avg_by_channel = {channel: statistics.mean(times) if times else timedelta(0)
                         for channel, times in by_channel.items()}
        avg_by_hierarchy = {level: statistics.mean(times) if times else timedelta(0)
                           for level, times in by_hierarchy.items()}
        
        return {'by_channel': avg_by_channel, 'by_hierarchy': avg_by_hierarchy}
    
    def _generate_improvement_recommendations(self, messages: List[CommunicationMessage],
                                            bottlenecks: List[str], language_dist: Dict,
                                            response_times: Dict) -> List[str]:
        """Generate personalized improvement recommendations"""
        recommendations = []
        
        # Response time recommendations
        slow_channels = []
        for channel, avg_time in response_times['by_channel'].items():
            expected = self.expected_response_times.get(channel, timedelta(hours=4))
            if avg_time > expected * 1.5:
                slow_channels.append(channel.value)
        
        if slow_channels:
            recommendations.append(
                f"📱 Improve response times on: {', '.join(slow_channels)}. "
                f"Consider setting notification preferences or delegation."
            )
        
        # Language recommendations
        hinglish_ratio = language_dist.get(MessageLanguage.HINGLISH, 0)
        if hinglish_ratio > 0.6:
            recommendations.append(
                "🌐 High Hinglish usage detected. Consider standardizing technical communication "
                "in English while maintaining cultural comfort in casual interactions."
            )
        
        # Hierarchy recommendations
        avg_respect = statistics.mean(m.respectfulness_score for m in messages 
                                    if m.respectfulness_score > 0)
        if avg_respect < 0.6:
            recommendations.append(
                "🙏 Consider more respectful communication patterns, especially in upward communication. "
                "Use 'Sir/Madam' appropriately and maintain courteous tone."
            )
        
        # Bottleneck recommendations
        if bottlenecks:
            recommendations.append(
                f"🚧 Communication bottlenecks identified: {', '.join(bottlenecks)}. "
                f"Consider delegation or structured communication processes."
            )
        
        # Cultural recommendations
        avg_cultural = statistics.mean(m.cultural_context_score for m in messages 
                                     if m.cultural_context_score > 0)
        if avg_cultural < 0.6:
            recommendations.append(
                "🪔 Enhance cultural sensitivity in communication. Consider greeting patterns, "
                "time zone awareness, and festival season adjustments."
            )
        
        return recommendations[:5]  # Top 5 recommendations
    
    # Simplified implementations for remaining methods to save space
    def _calculate_information_flow_efficiency(self, messages: List[CommunicationMessage]) -> float:
        """Simplified information flow calculation"""
        if not messages:
            return 0.0
        
        # Basic metric: ratio of responses to questions
        questions = [m for m in messages if m.communication_type == CommunicationType.QUESTION_ASKING]
        responses = [m for m in questions if m.responses]
        
        return len(responses) / len(questions) if questions else 1.0
    
    def _calculate_hierarchy_communication_health(self, messages: List[CommunicationMessage]) -> float:
        """Simplified hierarchy health calculation"""
        upward_messages = []
        for message in messages:
            sender = self.team_members.get(message.sender_id)
            if sender:
                for recipient_id in message.recipient_ids:
                    recipient = self.team_members.get(recipient_id)
                    if recipient and recipient.hierarchy_level.value > sender.hierarchy_level.value:
                        upward_messages.append(message)
        
        if not upward_messages:
            return 1.0
        
        avg_respect = statistics.mean(m.respectfulness_score for m in upward_messages)
        return avg_respect
    
    def _calculate_multilingual_effectiveness(self, messages: List[CommunicationMessage]) -> float:
        """Simplified multilingual effectiveness"""
        multilang_messages = [m for m in messages 
                            if m.language in [MessageLanguage.HINGLISH, MessageLanguage.REGIONAL]]
        
        if not multilang_messages:
            return 1.0
        
        avg_clarity = statistics.mean(m.clarity_score for m in multilang_messages)
        return avg_clarity
    
    def _analyze_language_distribution(self, messages: List[CommunicationMessage]) -> Dict[MessageLanguage, float]:
        """Analyze language distribution"""
        lang_counts = Counter(m.language for m in messages)
        total = len(messages)
        
        return {lang: count / total for lang, count in lang_counts.items()}
    
    # Placeholder implementations for remaining methods
    def _calculate_urgent_response_rate(self, messages): return 0.8
    def _analyze_cross_language_communication(self, messages): return 0.7
    def _calculate_cultural_appropriateness(self, messages): return 0.8
    def _calculate_hierarchy_respect_score(self, messages): return 0.75
    def _identify_communication_bottlenecks(self, messages): return []
    def _identify_information_silos(self, messages): return []
    def _identify_over_communicators(self, messages): return []
    def _identify_under_communicators(self, messages): return []
    def _analyze_sentiment_distribution(self, messages): return {"positive": 0.6, "neutral": 0.3, "negative": 0.1}

def demo_communication_effectiveness_analyzer():
    """Demo the communication effectiveness analyzer"""
    print("📊 Communication Effectiveness Analyzer Demo - Multilingual Team")
    print("=" * 70)
    
    analyzer = CommunicationEffectivenessAnalyzer()
    
    # Create diverse team members
    team_members = [
        TeamMember(
            id="TM001",
            name="Rajesh Kumar",
            email="rajesh@company.com",
            hierarchy_level=HierarchyLevel.LEAD,
            primary_language="Hindi",
            comfortable_languages=["Hindi", "English"],
            region_of_origin="North India",
            communication_style="diplomatic",
            response_time_preference=timedelta(hours=2),
            meeting_language_preference="Hinglish",
            written_language_preference="English",
            uses_sir_madam=True,
            comfort_with_hierarchy_bypass=0.2
        ),
        
        TeamMember(
            id="TM002", 
            name="Priya Menon",
            email="priya@company.com",
            hierarchy_level=HierarchyLevel.SENIOR,
            primary_language="Malayalam",
            comfortable_languages=["Malayalam", "English", "Hindi"],
            region_of_origin="South India",
            communication_style="direct",
            response_time_preference=timedelta(hours=1),
            meeting_language_preference="English",
            written_language_preference="English",
            uses_sir_madam=True,
            comfort_with_hierarchy_bypass=0.4
        ),
        
        TeamMember(
            id="TM003",
            name="Amit Patel",
            email="amit@company.com", 
            hierarchy_level=HierarchyLevel.MID_LEVEL,
            primary_language="Gujarati",
            comfortable_languages=["Gujarati", "Hindi", "English"],
            region_of_origin="West India",
            communication_style="casual",
            response_time_preference=timedelta(minutes=30),
            meeting_language_preference="Hinglish",
            written_language_preference="English",
            uses_sir_madam=True,
            comfort_with_hierarchy_bypass=0.3
        )
    ]
    
    # Add team members
    for member in team_members:
        analyzer.add_team_member(member)
    
    print("\n" + "=" * 50)
    
    # Create sample messages showing various communication patterns
    base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    
    messages = [
        # Respectful upward communication
        CommunicationMessage(
            id="MSG001",
            timestamp=base_time,
            sender_id="TM003",  # Mid-level
            recipient_ids=["TM001"],  # Lead
            channel=CommunicationChannel.SLACK,
            content="Good morning Rajesh sir, I have completed the payment integration task. "
                   "Kindly review when you have time. Thank you.",
            language=MessageLanguage.ENGLISH,
            communication_type=CommunicationType.INFORMATION_SHARING,
            urgency_level=2,
            response_required=True
        ),
        
        # Hinglish casual communication
        CommunicationMessage(
            id="MSG002",
            timestamp=base_time + timedelta(minutes=30),
            sender_id="TM001",  # Lead  
            recipient_ids=["TM003"],  # Mid-level
            channel=CommunicationChannel.SLACK,
            content="Amit, acha kaam kiya! Code review kar chuka hun. "
                   "Bas ek choti bug fix karna hai, then we can merge.",
            language=MessageLanguage.HINGLISH,
            communication_type=CommunicationType.FEEDBACK_GIVING,
            urgency_level=3,
            response_required=True
        ),
        
        # Technical discussion in English
        CommunicationMessage(
            id="MSG003",
            timestamp=base_time + timedelta(hours=1),
            sender_id="TM002",  # Senior
            recipient_ids=["TM001", "TM003"],  # Lead and Mid-level
            channel=CommunicationChannel.SLACK,
            content="Team, I think we should implement circuit breaker pattern for the API calls. "
                   "The current retry mechanism is not handling timeouts properly. "
                   "What do you think?",
            language=MessageLanguage.TECHNICAL_ENGLISH,
            communication_type=CommunicationType.QUESTION_ASKING,
            urgency_level=3,
            response_required=True
        ),
        
        # Urgent issue in WhatsApp
        CommunicationMessage(
            id="MSG004",
            timestamp=base_time + timedelta(hours=2),
            sender_id="TM003",  # Mid-level
            recipient_ids=["TM001", "TM002"],  # Lead and Senior
            channel=CommunicationChannel.WHATSAPP,
            content="Sir, production mein issue aa gaya hai. Payment failures spike kar rahe hain. "
                   "Please help ASAP!",
            language=MessageLanguage.HINGLISH,
            communication_type=CommunicationType.PROBLEM_REPORTING,
            urgency_level=5,
            response_required=True
        ),
        
        # Cross-language support
        CommunicationMessage(
            id="MSG005",
            timestamp=base_time + timedelta(hours=3),
            sender_id="TM002",  # Senior (Malayalam speaker)
            recipient_ids=["TM001"],  # Lead (Hindi speaker)
            channel=CommunicationChannel.EMAIL,
            content="Dear Rajesh sir, I am attaching the performance analysis report. "
                   "The database queries are taking longer time due to missing indexes. "
                   "I suggest we add composite indexes for better performance. "
                   "Please review and let me know your thoughts.",
            language=MessageLanguage.ENGLISH,
            communication_type=CommunicationType.INFORMATION_SHARING,
            urgency_level=2,
            response_required=True
        )
    ]
    
    print("📨 Recording communication messages...")
    for message in messages:
        analyzer.record_message(message)
    
    # Simulate responses
    response_time_delays = [
        (timedelta(minutes=15), "MSG001", "MSG006"),  # Quick response to upward communication
        (timedelta(minutes=45), "MSG002", "MSG007"),  # Response to feedback
        (timedelta(hours=1, minutes=30), "MSG003", "MSG008"),  # Discussion response
        (timedelta(minutes=5), "MSG004", "MSG009"),   # Very quick response to urgent
        (timedelta(hours=4), "MSG005", "MSG010"),     # Delayed response to email
    ]
    
    print("\n📬 Tracking responses...")
    for delay, orig_id, resp_id in response_time_delays:
        response_time = base_time + delay
        analyzer.track_response(orig_id, resp_id, response_time)
    
    print("\n" + "=" * 50)
    
    # Analyze communication effectiveness
    print("📊 Analyzing communication effectiveness...")
    start_date = base_time - timedelta(hours=1)
    end_date = base_time + timedelta(hours=5)
    
    metrics = analyzer.analyze_communication_effectiveness("TEAM_BACKEND", start_date, end_date)
    
    # Display results
    print(f"\n📋 Communication Effectiveness Report")
    print(f"Team: TEAM_BACKEND")
    print(f"Period: {start_date.strftime('%Y-%m-%d %H:%M')} to {end_date.strftime('%Y-%m-%d %H:%M')}")
    
    print(f"\n🎯 Overall Metrics:")
    print(f"   Overall Communication Score: {metrics.overall_communication_score:.2f}/1.00")
    print(f"   Information Flow Efficiency: {metrics.information_flow_efficiency:.2f}/1.00")
    print(f"   Hierarchy Communication Health: {metrics.hierarchy_communication_health:.2f}/1.00")
    print(f"   Multilingual Effectiveness: {metrics.multilingual_effectiveness:.2f}/1.00")
    
    print(f"\n⏱️ Response Time Analysis:")
    for channel, avg_time in metrics.average_response_time.items():
        print(f"   {channel.value}: {avg_time.total_seconds()/60:.0f} minutes average")
    
    print(f"   Urgent Message Response Rate: {metrics.urgent_message_response_rate:.1%}")
    
    print(f"\n🌐 Language Distribution:")
    for language, percentage in metrics.language_distribution.items():
        print(f"   {language.value}: {percentage:.1%}")
    
    print(f"\n📈 Quality Metrics:")
    print(f"   Message Clarity Average: {metrics.message_clarity_average:.2f}/1.00")
    print(f"   Cultural Appropriateness: {metrics.cultural_appropriateness_score:.2f}/1.00")
    print(f"   Hierarchy Respect Score: {metrics.hierarchy_respect_score:.2f}/1.00")
    
    print(f"\n😊 Sentiment Distribution:")
    for sentiment, percentage in metrics.sentiment_distribution.items():
        print(f"   {sentiment.title()}: {percentage:.1%}")
    
    print(f"\n💡 Improvement Recommendations:")
    for i, recommendation in enumerate(metrics.recommendations, 1):
        print(f"   {i}. {recommendation}")
    
    print(f"\n🔍 Message Analysis Examples:")
    for message in messages[:3]:
        print(f"\n   Message: '{message.content[:50]}...'")
        print(f"   Language: {message.language.value}")
        print(f"   Clarity: {message.clarity_score:.2f}, Respectfulness: {message.respectfulness_score:.2f}")
        print(f"   Cultural Context: {message.cultural_context_score:.2f}")

if __name__ == "__main__":
    demo_communication_effectiveness_analyzer()
#!/usr/bin/env python3
"""
Incident Response Bot - Episode 3: Human Factor in Tech
=======================================================

Indian IT companies के लिए intelligent incident response bot
WhatsApp, Slack, Teams पर काम करने वाला automated incident handler
Cultural sensitivity के साथ और Hindi support के साथ

Features:
- Multi-language incident reporting (Hindi, English)
- Indian time zone aware (IST) 
- Cultural context understanding (festivals, working hours)
- Automated escalation with hierarchy respect
- Smart incident categorization using NLP
- Integration with popular Indian communication platforms
"""

import re
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from collections import defaultdict

class IncidentSeverity(Enum):
    P1_CRITICAL = "P1"  # Complete system down
    P2_HIGH = "P2"      # Major feature affected  
    P3_MEDIUM = "P3"    # Minor issue
    P4_LOW = "P4"       # Enhancement request

class IncidentStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class CommunicationChannel(Enum):
    WHATSAPP = "whatsapp"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"
    EMAIL = "email"

@dataclass
class User:
    """User profile with Indian context"""
    id: str
    name: str
    role: str
    phone: str
    email: str
    preferred_language: str = "English"  # Hindi, English, or mixed
    time_zone: str = "Asia/Kolkata"
    department: str = ""
    escalation_level: int = 1  # 1=Junior, 2=Senior, 3=Manager, 4=Director
    is_on_call: bool = False
    working_hours: Dict[str, str] = field(default_factory=lambda: {
        "start": "09:00", "end": "18:00"
    })

@dataclass 
class Incident:
    """Incident with Indian business context"""
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    reporter: str
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    affected_services: List[str] = field(default_factory=list)
    business_impact: str = ""
    customer_impact: str = ""
    escalation_history: List[str] = field(default_factory=list)
    communication_log: List[str] = field(default_factory=list)

class IncidentResponseBot:
    """Main incident response bot with Indian cultural context"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.incidents: Dict[str, Incident] = {}
        self.on_call_schedule: Dict[str, List[str]] = {}  # date -> user_ids
        self.escalation_rules: Dict[IncidentSeverity, List[int]] = {
            IncidentSeverity.P1_CRITICAL: [1, 2, 3, 4],  # All levels
            IncidentSeverity.P2_HIGH: [1, 2, 3],
            IncidentSeverity.P3_MEDIUM: [1, 2],
            IncidentSeverity.P4_LOW: [1]
        }
        self.business_hours = {"start": 9, "end": 18}
        self.indian_festivals = self._get_indian_festivals()
        
        # Hindi-English mixed phrases common in Indian IT
        self.hinglish_patterns = {
            "down": ["down hai", "nahi chal raha", "band hai", "crash ho gaya"],
            "slow": ["slow hai", "hang kar raha", "response time zyada"],
            "error": ["error aa raha", "problem hai", "issue hai", "galat response"],
            "urgent": ["urgent hai", "critical hai", "jaldi dekho", "immediate action"]
        }
        
    def _get_indian_festivals(self) -> Dict[str, datetime]:
        """Indian festival calendar for 2024"""
        return {
            "Republic Day": datetime(2024, 1, 26),
            "Holi": datetime(2024, 3, 8),
            "Ram Navami": datetime(2024, 4, 17),
            "Independence Day": datetime(2024, 8, 15),
            "Dussehra": datetime(2024, 10, 12),
            "Diwali": datetime(2024, 11, 1),
            "Christmas": datetime(2024, 12, 25)
        }
    
    def add_user(self, user: User) -> None:
        """Add user to the system"""
        self.users[user.id] = user
        print(f"✅ Added user: {user.name} ({user.role})")
    
    def is_working_hours(self, user_id: str = None) -> bool:
        """Check if current time is within working hours (IST)"""
        now = datetime.now()
        current_hour = now.hour
        
        # Check if it's a festival
        today = now.date()
        for festival, date in self.indian_festivals.items():
            if date.date() == today:
                print(f"🎉 Today is {festival} - reduced availability expected")
                return False
                
        # Check if it's weekend
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
            
        return self.business_hours["start"] <= current_hour < self.business_hours["end"]
    
    def parse_incident_message(self, message: str, user_id: str) -> Optional[Dict]:
        """Parse incident report from natural language (Hindi/English/Hinglish)"""
        message_lower = message.lower()
        
        # Detect severity from message content
        severity = IncidentSeverity.P3_MEDIUM  # Default
        
        # Critical indicators
        critical_keywords = [
            "down", "crash", "complete failure", "sabkuch band", "pura system down",
            "database down", "payment failure", "login nahi ho raha"
        ]
        
        high_keywords = [
            "slow", "hang", "timeout", "500 error", "database slow", 
            "load time", "performance issue", "response time"
        ]
        
        for keyword in critical_keywords:
            if keyword in message_lower:
                severity = IncidentSeverity.P1_CRITICAL
                break
                
        for keyword in high_keywords:
            if keyword in message_lower and severity != IncidentSeverity.P1_CRITICAL:
                severity = IncidentSeverity.P2_HIGH
                break
        
        # Extract affected service
        service_patterns = {
            "payment": ["payment", "paisa", "transaction", "pay", "wallet"],
            "login": ["login", "sign in", "authentication", "auth", "password"],
            "database": ["database", "db", "data", "query", "connection"],
            "api": ["api", "service", "endpoint", "server", "backend"],
            "website": ["website", "web", "page", "site", "frontend"],
            "mobile": ["mobile", "app", "android", "ios", "phone"]
        }
        
        affected_services = []
        for service, keywords in service_patterns.items():
            for keyword in keywords:
                if keyword in message_lower:
                    affected_services.append(service)
                    break
        
        # Generate title from message
        title = message.split('.')[0][:100] + "..." if len(message) > 100 else message.split('.')[0]
        
        return {
            "title": title,
            "description": message,
            "severity": severity,
            "affected_services": affected_services,
            "reporter": user_id
        }
    
    def create_incident(self, message: str, user_id: str, channel: CommunicationChannel) -> str:
        """Create new incident from user message"""
        
        # Parse the message
        parsed = self.parse_incident_message(message, user_id)
        if not parsed:
            return "❌ Could not understand the incident report. Please provide more details."
        
        # Generate incident ID
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create incident object
        incident = Incident(
            id=incident_id,
            title=parsed["title"],
            description=parsed["description"],
            severity=parsed["severity"],
            status=IncidentStatus.OPEN,
            reporter=user_id,
            affected_services=parsed["affected_services"]
        )
        
        self.incidents[incident_id] = incident
        
        # Auto-assign based on on-call schedule and severity
        assigned_user = self._auto_assign_incident(incident)
        if assigned_user:
            incident.assigned_to = assigned_user
            incident.status = IncidentStatus.IN_PROGRESS
        
        # Send notifications
        self._send_notifications(incident, channel)
        
        # Log incident creation
        user = self.users.get(user_id, None)
        user_name = user.name if user else user_id
        
        incident.communication_log.append(
            f"{datetime.now().isoformat()}: Incident created by {user_name} via {channel.value}"
        )
        
        return self._format_incident_response(incident, "created")
    
    def _auto_assign_incident(self, incident: Incident) -> Optional[str]:
        """Auto-assign incident based on severity and availability"""
        
        # Get eligible escalation levels for this severity
        eligible_levels = self.escalation_rules.get(incident.severity, [1])
        
        # Start with lowest level that can handle this severity
        for level in eligible_levels:
            available_users = [
                user_id for user_id, user in self.users.items()
                if user.escalation_level == level and self._is_user_available(user_id)
            ]
            
            if available_users:
                # Prefer on-call users
                on_call_users = [uid for uid in available_users if self.users[uid].is_on_call]
                if on_call_users:
                    return on_call_users[0]
                else:
                    return available_users[0]
        
        return None
    
    def _is_user_available(self, user_id: str) -> bool:
        """Check if user is available to handle incidents"""
        user = self.users.get(user_id)
        if not user:
            return False
            
        now = datetime.now()
        
        # Check working hours for the user
        user_start = int(user.working_hours["start"].split(":")[0])
        user_end = int(user.working_hours["end"].split(":")[0])
        
        if not (user_start <= now.hour < user_end):
            return False
            
        # Check if user is already handling too many incidents
        active_incidents = [
            inc for inc in self.incidents.values()
            if inc.assigned_to == user_id and inc.status in [IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS]
        ]
        
        # Max 3 active incidents per person
        if len(active_incidents) >= 3:
            return False
            
        return True
    
    def _send_notifications(self, incident: Incident, channel: CommunicationChannel) -> None:
        """Send notifications to relevant stakeholders"""
        
        # Determine notification recipients based on severity
        recipients = []
        
        if incident.severity == IncidentSeverity.P1_CRITICAL:
            # Critical incidents notify all managers+
            recipients = [uid for uid, user in self.users.items() if user.escalation_level >= 3]
        elif incident.severity == IncidentSeverity.P2_HIGH:
            # High incidents notify senior+ 
            recipients = [uid for uid, user in self.users.items() if user.escalation_level >= 2]
        else:
            # Medium/Low incidents notify assigned person and immediate manager
            if incident.assigned_to:
                recipients.append(incident.assigned_to)
                # Find manager (escalation_level + 1)
                assigned_user = self.users.get(incident.assigned_to)
                if assigned_user:
                    managers = [
                        uid for uid, user in self.users.items() 
                        if user.escalation_level == assigned_user.escalation_level + 1
                        and user.department == assigned_user.department
                    ]
                    recipients.extend(managers[:1])  # Just one manager
        
        # Send notifications
        for recipient_id in recipients:
            self._send_notification_to_user(incident, recipient_id, channel)
    
    def _send_notification_to_user(self, incident: Incident, user_id: str, channel: CommunicationChannel) -> None:
        """Send notification to specific user"""
        user = self.users.get(user_id)
        if not user:
            return
            
        # Format message based on user's preferred language
        message = self._format_notification_message(incident, user)
        
        # Log the notification (in real system, would actually send)
        print(f"📱 {channel.value.upper()} to {user.name}: {message}")
        
        incident.communication_log.append(
            f"{datetime.now().isoformat()}: Notification sent to {user.name} via {channel.value}"
        )
    
    def _format_notification_message(self, incident: Incident, user: User) -> str:
        """Format notification message based on user's language preference"""
        
        if user.preferred_language == "Hindi":
            severity_hindi = {
                IncidentSeverity.P1_CRITICAL: "अत्यंत गंभीर",
                IncidentSeverity.P2_HIGH: "गंभीर", 
                IncidentSeverity.P3_MEDIUM: "मध्यम",
                IncidentSeverity.P4_LOW: "कम"
            }
            
            message = f"""🚨 नई घटना रिपोर्ट
घटना ID: {incident.id}
गंभीरता: {severity_hindi.get(incident.severity, 'मध्यम')}
शीर्षक: {incident.title}
समय: {incident.created_at.strftime('%d/%m/%Y %H:%M')}
कृपया तुरंत कार्रवाई करें।"""

        elif user.preferred_language == "mixed":
            # Hinglish style
            message = f"""🚨 नया Incident आया hai
ID: {incident.id}
Severity: {incident.severity.value}
Title: {incident.title}
Time: {incident.created_at.strftime('%d/%m/%Y %H:%M')}
Please check करो और action लो।"""

        else:  # English
            message = f"""🚨 New Incident Alert
ID: {incident.id}
Severity: {incident.severity.value}
Title: {incident.title}
Affected Services: {', '.join(incident.affected_services)}
Created: {incident.created_at.strftime('%d/%m/%Y %H:%M IST')}
Please take immediate action."""
            
        return message
    
    def _format_incident_response(self, incident: Incident, action: str) -> str:
        """Format response message after incident action"""
        
        if action == "created":
            assigned_info = ""
            if incident.assigned_to:
                assigned_user = self.users.get(incident.assigned_to)
                assigned_name = assigned_user.name if assigned_user else incident.assigned_to
                assigned_info = f"\n👤 Assigned to: {assigned_name}"
            
            return f"""✅ Incident Created Successfully
🆔 ID: {incident.id}
📊 Severity: {incident.severity.value}
📝 Title: {incident.title}
🕐 Created: {incident.created_at.strftime('%d/%m/%Y %H:%M IST')}{assigned_info}

💬 Notifications sent to relevant team members.
📱 You'll receive updates as the incident progresses."""

        elif action == "updated":
            return f"""📝 Incident Updated: {incident.id}
Status: {incident.status.value}
Last Updated: {incident.updated_at.strftime('%d/%m/%Y %H:%M IST')}"""

        elif action == "resolved":
            duration = incident.resolved_at - incident.created_at
            return f"""✅ Incident Resolved: {incident.id}
Resolution Time: {incident.resolved_at.strftime('%d/%m/%Y %H:%M IST')}
Total Duration: {self._format_duration(duration)}
Status: {incident.status.value}"""
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration in human readable form"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def update_incident(self, incident_id: str, update_message: str, user_id: str) -> str:
        """Add update to incident"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return f"❌ Incident {incident_id} not found."
        
        # Add update to description
        user = self.users.get(user_id)
        user_name = user.name if user else user_id
        
        update_entry = f"\n--- Update by {user_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n{update_message}"
        incident.description += update_entry
        incident.updated_at = datetime.now()
        
        incident.communication_log.append(
            f"{datetime.now().isoformat()}: Update added by {user_name}"
        )
        
        return self._format_incident_response(incident, "updated")
    
    def resolve_incident(self, incident_id: str, resolution_notes: str, user_id: str) -> str:
        """Resolve an incident"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return f"❌ Incident {incident_id} not found."
        
        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = datetime.now()
        incident.updated_at = datetime.now()
        
        # Add resolution notes
        user = self.users.get(user_id)
        user_name = user.name if user else user_id
        
        resolution_entry = f"\n--- Resolved by {user_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n{resolution_notes}"
        incident.description += resolution_entry
        
        incident.communication_log.append(
            f"{datetime.now().isoformat()}: Incident resolved by {user_name}"
        )
        
        # Send resolution notifications
        self._send_resolution_notifications(incident)
        
        return self._format_incident_response(incident, "resolved")
    
    def _send_resolution_notifications(self, incident: Incident) -> None:
        """Send notifications when incident is resolved"""
        
        # Notify reporter
        if incident.reporter in self.users:
            user = self.users[incident.reporter]
            message = self._format_resolution_message(incident, user)
            print(f"📱 Resolution notification to {user.name}: {message}")
        
        # Notify stakeholders based on severity
        if incident.severity in [IncidentSeverity.P1_CRITICAL, IncidentSeverity.P2_HIGH]:
            managers = [user for user in self.users.values() if user.escalation_level >= 3]
            for manager in managers:
                message = self._format_resolution_message(incident, manager)
                print(f"📱 Resolution notification to {manager.name}: {message}")
    
    def _format_resolution_message(self, incident: Incident, user: User) -> str:
        """Format resolution notification message"""
        duration = incident.resolved_at - incident.created_at
        
        if user.preferred_language == "Hindi":
            return f"""✅ घटना हल हो गई
ID: {incident.id}
कुल समय: {self._format_duration(duration)}
धन्यवाद आपके धैर्य के लिए।"""
        elif user.preferred_language == "mixed":
            return f"""✅ Incident resolve ho gaya hai!
ID: {incident.id}  
Total time: {self._format_duration(duration)}
Thanks for your patience!"""
        else:
            return f"""✅ Incident Resolved
ID: {incident.id}
Resolution Time: {self._format_duration(duration)}
Thank you for your patience."""
    
    def get_incident_status(self, incident_id: str) -> str:
        """Get current status of incident"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return f"❌ Incident {incident_id} not found."
        
        assigned_info = ""
        if incident.assigned_to:
            assigned_user = self.users.get(incident.assigned_to)
            assigned_name = assigned_user.name if assigned_user else incident.assigned_to
            assigned_info = f"👤 Assigned to: {assigned_name}\n"
        
        duration_info = ""
        if incident.status == IncidentStatus.RESOLVED:
            duration = incident.resolved_at - incident.created_at
            duration_info = f"⏱️ Resolution Time: {self._format_duration(duration)}\n"
        else:
            duration = datetime.now() - incident.created_at
            duration_info = f"⏱️ Active for: {self._format_duration(duration)}\n"
        
        update_count = len([line for line in incident.description.split('\n') if '--- Update by' in line])
        
        return f"""📋 Incident Status: {incident.id}
📊 Severity: {incident.severity.value}
🚦 Status: {incident.status.value}
📝 Title: {incident.title}
{assigned_info}{duration_info}🕐 Created: {incident.created_at.strftime('%d/%m/%Y %H:%M IST')}
💬 Total Updates: {update_count}"""
    
    def get_my_incidents(self, user_id: str) -> str:
        """Get incidents assigned to user"""
        user = self.users.get(user_id)
        if not user:
            return "❌ User not found."
        
        assigned_incidents = [
            inc for inc in self.incidents.values()
            if inc.assigned_to == user_id and inc.status != IncidentStatus.CLOSED
        ]
        
        if not assigned_incidents:
            return f"✅ No active incidents assigned to {user.name}."
        
        response = f"📋 Active Incidents for {user.name}:\n"
        response += "=" * 40 + "\n"
        
        for incident in sorted(assigned_incidents, key=lambda x: x.created_at, reverse=True):
            duration = datetime.now() - incident.created_at
            response += f"🆔 {incident.id} ({incident.severity.value})\n"
            response += f"   📝 {incident.title[:50]}...\n"
            response += f"   🚦 {incident.status.value} | ⏱️ {self._format_duration(duration)}\n\n"
        
        return response
    
    def get_team_dashboard(self) -> str:
        """Get team-level incident dashboard"""
        
        # Count incidents by severity and status
        severity_counts = defaultdict(int)
        status_counts = defaultdict(int)
        total_incidents = len(self.incidents)
        
        active_incidents = []
        resolved_today = []
        
        for incident in self.incidents.values():
            severity_counts[incident.severity] += 1
            status_counts[incident.status] += 1
            
            if incident.status in [IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS]:
                active_incidents.append(incident)
            
            if (incident.resolved_at and 
                incident.resolved_at.date() == datetime.now().date()):
                resolved_today.append(incident)
        
        # Team workload
        user_workload = defaultdict(int)
        for incident in active_incidents:
            if incident.assigned_to:
                user_workload[incident.assigned_to] += 1
        
        response = "📊 Team Incident Dashboard\n"
        response += "=" * 30 + "\n"
        response += f"🎯 Total Incidents: {total_incidents}\n"
        response += f"🔥 Active Incidents: {len(active_incidents)}\n"
        response += f"✅ Resolved Today: {len(resolved_today)}\n\n"
        
        response += "📈 By Severity:\n"
        for severity in IncidentSeverity:
            count = severity_counts[severity]
            if count > 0:
                response += f"   {severity.value}: {count}\n"
        
        response += "\n🚦 By Status:\n"
        for status in IncidentStatus:
            count = status_counts[status]
            if count > 0:
                response += f"   {status.value}: {count}\n"
        
        if user_workload:
            response += "\n👥 Current Workload:\n"
            for user_id, count in sorted(user_workload.items(), key=lambda x: x[1], reverse=True):
                user = self.users.get(user_id)
                name = user.name if user else user_id
                response += f"   {name}: {count} incident(s)\n"
        
        # Escalation needed
        escalation_needed = [
            inc for inc in active_incidents
            if (datetime.now() - inc.created_at).total_seconds() > 3600  # 1 hour old
        ]
        
        if escalation_needed:
            response += f"\n⚠️ Incidents Needing Attention ({len(escalation_needed)}):\n"
            for incident in escalation_needed[:3]:  # Show top 3
                duration = datetime.now() - incident.created_at
                response += f"   {incident.id}: {self._format_duration(duration)} old\n"
        
        return response

# Demo function to show the bot in action
def main():
    print("🤖 Incident Response Bot Demo - Indian IT Context")
    print("=" * 50)
    
    # Initialize bot
    bot = IncidentResponseBot()
    
    # Add sample users with Indian names and mixed language preferences
    users = [
        User("USR001", "Rajesh Kumar", "Senior Developer", "+91-9876543210", "rajesh@company.com", "English", "Asia/Kolkata", "Engineering", 2),
        User("USR002", "Priya Sharma", "Tech Lead", "+91-9876543211", "priya@company.com", "mixed", "Asia/Kolkata", "Engineering", 3),
        User("USR003", "Amit Singh", "DevOps Engineer", "+91-9876543212", "amit@company.com", "Hindi", "Asia/Kolkata", "Operations", 1),
        User("USR004", "Sneha Patel", "Engineering Manager", "+91-9876543213", "sneha@company.com", "English", "Asia/Kolkata", "Engineering", 4),
        User("USR005", "Vikram Reddy", "Junior Developer", "+91-9876543214", "vikram@company.com", "mixed", "Asia/Kolkata", "Engineering", 1),
    ]
    
    # Set some users as on-call
    users[0].is_on_call = True
    users[2].is_on_call = True
    
    for user in users:
        bot.add_user(user)
    
    print("\n" + "=" * 50)
    print("🎭 Simulating Incident Reports...")
    print("=" * 50)
    
    # Simulate various incident reports in different languages
    
    # Critical incident in English
    print("\n1️⃣ Critical Payment System Failure:")
    response1 = bot.create_incident(
        "Payment gateway is completely down. All UPI transactions are failing. Customer complaints increasing.",
        "USR001",
        CommunicationChannel.SLACK
    )
    print(response1)
    
    time.sleep(1)
    
    # High severity in Hinglish
    print("\n2️⃣ Performance Issue in Hinglish:")
    response2 = bot.create_incident(
        "Website bahut slow hai yaar. Load time 30 seconds tak ja raha hai. Customers complain kar rahe hain.",
        "USR005", 
        CommunicationChannel.WHATSAPP
    )
    print(response2)
    
    time.sleep(1)
    
    # Medium incident in mixed Hindi-English  
    print("\n3️⃣ Database Connectivity Issue:")
    response3 = bot.create_incident(
        "Database connection pool exhausted ho gaya hai. Some queries timeout ho rahe hain but major features working hain.",
        "USR003",
        CommunicationChannel.TEAMS
    )
    print(response3)
    
    print("\n" + "=" * 50)
    print("📊 Team Dashboard:")
    print("=" * 50)
    print(bot.get_team_dashboard())
    
    print("\n" + "=" * 50)
    print("🔄 Incident Updates and Resolution:")
    print("=" * 50)
    
    # Get the first incident and update it
    first_incident_id = list(bot.incidents.keys())[0]
    
    # Add update
    update_response = bot.update_incident(
        first_incident_id,
        "Engineering team investigating. Found issue in payment service configuration. ETA 30 minutes.",
        "USR002"
    )
    print(f"\n📝 Update Response:\n{update_response}")
    
    # Resolve incident
    resolution_response = bot.resolve_incident(
        first_incident_id,
        "Payment service configuration fixed. Load balancer restarted. All systems operational. Monitoring for 1 hour.",
        "USR002"
    )
    print(f"\n✅ Resolution Response:\n{resolution_response}")
    
    print("\n" + "=" * 50)
    print("👤 Personal Incident View:")
    print("=" * 50)
    
    # Check incidents for a specific user
    my_incidents = bot.get_my_incidents("USR002")
    print(my_incidents)
    
    print("\n" + "=" * 50)
    print("📈 Final Team Dashboard:")
    print("=" * 50)
    print(bot.get_team_dashboard())
    
    print("\n✅ Incident Response Bot Demo Complete!")
    print("🎯 Key Features Demonstrated:")
    print("   - Multi-language support (Hindi/English/Hinglish)")
    print("   - Indian cultural context (festivals, working hours)")
    print("   - Automatic severity detection and assignment")
    print("   - Escalation based on hierarchy")
    print("   - Real-time team dashboard")
    print("   - Communication across multiple channels")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
WhatsApp-style Rumor Spreading using Gossip Protocol
====================================================

WhatsApp Group Message Viral Spread: जब कोई message viral होता है तो
कैसे WhatsApp groups के through exponentially फैलता है?

This simulates how rumors/viral content spreads through WhatsApp groups
using gossip-like protocols with real-world constraints.

Author: Code Developer Agent
Episode: 33 - Gossip Protocols
"""

import random
import time
import math
import asyncio
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid


class MessageType(Enum):
    """Types of WhatsApp messages"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    FORWARD = "forward"
    LINK = "link"


class ViralityScore(Enum):
    """Virality potential of content"""
    LOW = 1        # Personal messages
    MEDIUM = 2     # Interesting content
    HIGH = 3       # Controversial/emotional
    VIRAL = 4      # Highly shareable content


@dataclass
class WhatsAppMessage:
    """WhatsApp message structure"""
    message_id: str
    content: str
    message_type: MessageType
    sender_id: str
    original_sender: str
    timestamp: float
    forward_count: int = 0
    virality_score: ViralityScore = ViralityScore.LOW
    group_id: Optional[str] = None
    contains_misinformation: bool = False
    size_mb: float = 0.001  # Message size in MB


@dataclass
class GroupMetadata:
    """WhatsApp group metadata"""
    group_id: str
    name: str
    member_count: int
    activity_level: float  # 0.0 to 1.0
    admin_moderation: bool = False
    message_frequency: float = 5.0  # messages per hour


class WhatsAppUser:
    """
    WhatsApp User Simulator
    
    हर user अपने groups में messages को forward करता है
    based on content type, personal preferences, और social factors
    """
    
    def __init__(self, user_id: str, name: str, city: str):
        self.user_id = user_id
        self.name = name
        self.city = city
        
        # User behavior characteristics
        self.forward_probability = random.uniform(0.1, 0.9)  # Tendency to forward
        self.gullibility = random.uniform(0.0, 1.0)  # Belief in fake news
        self.social_influence = random.uniform(0.3, 1.0)    # Influence on others
        self.verification_tendency = random.uniform(0.1, 0.8)  # Fact-checking
        
        # Network and groups
        self.groups: Set[str] = set()
        self.contacts: Set[str] = set()
        self.blocked_users: Set[str] = set()
        
        # Message handling
        self.received_messages: Dict[str, WhatsAppMessage] = {}
        self.forwarded_messages: Set[str] = set()
        self.message_queue: List[WhatsAppMessage] = []
        
        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.misinformation_spread = 0
        self.last_active = time.time()
        
        # Rate limiting (like WhatsApp's)
        self.daily_forward_limit = 20
        self.forwards_today = 0
        self.last_forward_reset = time.time()
        
    def join_group(self, group_id: str):
        """Join WhatsApp group"""
        self.groups.add(group_id)
        
    def add_contact(self, contact_id: str):
        """Add contact"""
        self.contacts.add(contact_id)
        
    def calculate_forward_probability(self, message: WhatsAppMessage, group_id: str) -> float:
        """
        Calculate probability of forwarding message to specific group
        Based on content type, user behavior, and social factors
        """
        base_prob = self.forward_probability
        
        # Content type modifiers
        type_modifiers = {
            MessageType.TEXT: 0.8,
            MessageType.IMAGE: 1.2,
            MessageType.VIDEO: 1.5,
            MessageType.FORWARD: 0.7,  # Less likely to forward forwards
            MessageType.LINK: 0.9
        }
        
        content_modifier = type_modifiers.get(message.message_type, 1.0)
        
        # Virality score impact
        virality_modifier = message.virality_score.value * 0.3
        
        # Misinformation handling
        misinformation_modifier = 1.0
        if message.contains_misinformation:
            if self.verification_tendency > 0.7:
                misinformation_modifier = 0.1  # Fact-checkers less likely to forward
            elif self.gullibility > 0.8:
                misinformation_modifier = 1.5  # Gullible users more likely
                
        # Forward count penalty (viral fatigue)
        forward_penalty = max(0.1, 1.0 - (message.forward_count * 0.05))
        
        # Rate limiting check
        if self.forwards_today >= self.daily_forward_limit:
            return 0.0
            
        final_probability = (
            base_prob * content_modifier * virality_modifier * 
            misinformation_modifier * forward_penalty
        )
        
        return min(max(final_probability, 0.0), 1.0)
        
    def reset_daily_limits(self):
        """Reset daily forward limits (simulated daily reset)"""
        current_day = int(time.time() / 86400)  # Day since epoch
        last_reset_day = int(self.last_forward_reset / 86400)
        
        if current_day > last_reset_day:
            self.forwards_today = 0
            self.last_forward_reset = time.time()
            
    def receive_message(self, message: WhatsAppMessage, from_group: str = None) -> bool:
        """
        Receive message from group or contact
        Returns True if message is new
        """
        if message.message_id in self.received_messages:
            return False  # Already seen
            
        # Store message
        self.received_messages[message.message_id] = message
        self.messages_received += 1
        self.last_active = time.time()
        
        # Add to processing queue
        self.message_queue.append(message)
        
        print(f"📱 {self.name} received: {message.content[:30]}... "
              f"(Type: {message.message_type.value})")
        
        return True
        
    def process_message_queue(self) -> List[Tuple[str, WhatsAppMessage]]:
        """
        Process queued messages and decide on forwarding
        Returns list of (group_id, message) tuples to forward
        """
        self.reset_daily_limits()
        
        forwards_to_make = []
        processed_queue = []
        
        for message in self.message_queue:
            # Skip if already forwarded by this user
            if message.message_id in self.forwarded_messages:
                continue
                
            # Consider forwarding to each group
            for group_id in self.groups:
                if group_id == message.group_id:
                    continue  # Don't forward back to same group
                    
                forward_prob = self.calculate_forward_probability(message, group_id)
                
                if random.random() < forward_prob and self.forwards_today < self.daily_forward_limit:
                    # Create forwarded message
                    forwarded_msg = WhatsAppMessage(
                        message_id=str(uuid.uuid4()),
                        content=message.content,
                        message_type=MessageType.FORWARD,
                        sender_id=self.user_id,
                        original_sender=message.original_sender,
                        timestamp=time.time(),
                        forward_count=message.forward_count + 1,
                        virality_score=message.virality_score,
                        group_id=group_id,
                        contains_misinformation=message.contains_misinformation,
                        size_mb=message.size_mb
                    )
                    
                    forwards_to_make.append((group_id, forwarded_msg))
                    self.forwarded_messages.add(message.message_id)
                    self.forwards_today += 1
                    self.messages_sent += 1
                    
                    if message.contains_misinformation:
                        self.misinformation_spread += 1
                        
                    # Break if daily limit reached
                    if self.forwards_today >= self.daily_forward_limit:
                        break
                        
            processed_queue.append(message)
            
        # Clear processed messages
        self.message_queue = []
        
        return forwards_to_make
        
    def create_original_message(self, content: str, message_type: MessageType, 
                              virality_score: ViralityScore, 
                              contains_misinformation: bool = False) -> WhatsAppMessage:
        """Create original message"""
        return WhatsAppMessage(
            message_id=str(uuid.uuid4()),
            content=content,
            message_type=message_type,
            sender_id=self.user_id,
            original_sender=self.user_id,
            timestamp=time.time(),
            virality_score=virality_score,
            contains_misinformation=contains_misinformation
        )
        
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "city": self.city,
            "groups": len(self.groups),
            "contacts": len(self.contacts),
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "misinformation_spread": self.misinformation_spread,
            "forward_probability": self.forward_probability,
            "gullibility": self.gullibility,
            "verification_tendency": self.verification_tendency,
            "forwards_today": self.forwards_today
        }


class WhatsAppGroup:
    """WhatsApp Group Simulator"""
    
    def __init__(self, group_id: str, name: str, admin_id: str):
        self.group_id = group_id
        self.name = name
        self.admin_id = admin_id
        
        self.members: Set[str] = {admin_id}
        self.metadata = GroupMetadata(
            group_id=group_id,
            name=name,
            member_count=1,
            activity_level=random.uniform(0.3, 1.0),
            admin_moderation=random.choice([True, False]),
            message_frequency=random.uniform(2.0, 20.0)
        )
        
        # Message history
        self.messages: List[WhatsAppMessage] = []
        self.message_count = 0
        
        # Moderation
        self.blocked_content: Set[str] = set()
        self.misinformation_count = 0
        
    def add_member(self, user_id: str):
        """Add member to group"""
        self.members.add(user_id)
        self.metadata.member_count = len(self.members)
        
    def remove_member(self, user_id: str):
        """Remove member from group"""
        self.members.discard(user_id)
        self.metadata.member_count = len(self.members)
        
    def should_moderate_message(self, message: WhatsAppMessage) -> bool:
        """Check if message should be moderated"""
        if not self.metadata.admin_moderation:
            return False
            
        # Simple moderation rules
        if message.contains_misinformation and random.random() < 0.3:
            return True  # 30% chance to catch misinformation
            
        if message.forward_count > 10:
            return True  # Block highly forwarded content
            
        return False
        
    def broadcast_message(self, message: WhatsAppMessage) -> List[str]:
        """
        Broadcast message to all group members
        Returns list of members who should receive it
        """
        if self.should_moderate_message(message):
            print(f"🚫 Message blocked in {self.name} by admin moderation")
            return []
            
        # Add to group message history
        message.group_id = self.group_id
        self.messages.append(message)
        self.message_count += 1
        
        if message.contains_misinformation:
            self.misinformation_count += 1
            
        # Return all members except sender
        recipients = [user_id for user_id in self.members if user_id != message.sender_id]
        
        print(f"📢 Broadcasting in {self.name} to {len(recipients)} members")
        return recipients
        
    def get_group_stats(self) -> Dict:
        """Get group statistics"""
        return {
            "group_id": self.group_id,
            "name": self.name,
            "member_count": self.metadata.member_count,
            "total_messages": self.message_count,
            "misinformation_count": self.misinformation_count,
            "activity_level": self.metadata.activity_level,
            "admin_moderation": self.metadata.admin_moderation
        }


class WhatsAppNetwork:
    """WhatsApp Network Simulator for Viral Content Spread"""
    
    def __init__(self):
        self.users: Dict[str, WhatsAppUser] = {}
        self.groups: Dict[str, WhatsAppGroup] = {}
        self.simulation_round = 0
        
        # Global statistics
        self.total_messages = 0
        self.viral_messages = 0
        self.misinformation_instances = 0
        
    def create_indian_whatsapp_network(self, num_users: int = 50, num_groups: int = 15):
        """Create Indian WhatsApp network topology"""
        # Indian cities for users
        cities = [
            "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
            "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat",
            "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane"
        ]
        
        # Create users
        for i in range(num_users):
            user_id = f"user_{i+1:03d}"
            name = f"User{i+1}"
            city = random.choice(cities)
            
            self.users[user_id] = WhatsAppUser(user_id, name, city)
            
        # Create groups
        group_types = [
            "Family", "Friends", "Office", "Society", "School",
            "College", "Neighbors", "Hobby", "News", "Shopping",
            "Cooking", "Sports", "Politics", "Entertainment", "Local"
        ]
        
        for i in range(num_groups):
            group_id = f"group_{i+1:03d}"
            group_type = random.choice(group_types)
            name = f"{group_type} Group {i+1}"
            
            # Random admin
            admin_id = random.choice(list(self.users.keys()))
            
            self.groups[group_id] = WhatsAppGroup(group_id, name, admin_id)
            
        # Add users to groups randomly
        for user_id, user in self.users.items():
            # Each user joins 3-8 groups
            num_groups_to_join = random.randint(3, 8)
            groups_to_join = random.sample(list(self.groups.keys()), num_groups_to_join)
            
            for group_id in groups_to_join:
                user.join_group(group_id)
                self.groups[group_id].add_member(user_id)
                
        # Create some contact connections
        for user_id, user in self.users.items():
            # Each user has 10-30 contacts
            num_contacts = random.randint(10, 30)
            potential_contacts = [uid for uid in self.users.keys() if uid != user_id]
            contacts = random.sample(potential_contacts, min(num_contacts, len(potential_contacts)))
            
            for contact_id in contacts:
                user.add_contact(contact_id)
                
    def inject_viral_content(self, content_examples: List[Dict]):
        """Inject viral content into the network"""
        for content in content_examples:
            # Select random user to start the rumor
            user_id = random.choice(list(self.users.keys()))
            user = self.users[user_id]
            
            # Create viral message
            message = user.create_original_message(
                content=content["text"],
                message_type=MessageType(content["type"]),
                virality_score=ViralityScore(content["virality"]),
                contains_misinformation=content.get("misinformation", False)
            )
            
            # Post to random group
            if user.groups:
                group_id = random.choice(list(user.groups))
                group = self.groups[group_id]
                recipients = group.broadcast_message(message)
                
                # Deliver to recipients
                for recipient_id in recipients:
                    if recipient_id in self.users:
                        self.users[recipient_id].receive_message(message, group_id)
                        
                print(f"🚀 Viral content injected by {user.name} in {group.name}")
                print(f"   Content: {content['text'][:50]}...")
                
    def simulate_round(self) -> Dict:
        """Simulate one round of message spreading"""
        self.simulation_round += 1
        
        round_stats = {
            "messages_sent": 0,
            "new_forwards": 0,
            "misinformation_spread": 0,
            "active_users": 0
        }
        
        # Process all users' message queues
        for user_id, user in self.users.items():
            forwards = user.process_message_queue()
            
            if forwards:
                round_stats["active_users"] += 1
                
            for group_id, message in forwards:
                if group_id in self.groups:
                    group = self.groups[group_id]
                    recipients = group.broadcast_message(message)
                    
                    # Deliver to group members
                    for recipient_id in recipients:
                        if recipient_id in self.users:
                            self.users[recipient_id].receive_message(message, group_id)
                            
                    round_stats["messages_sent"] += 1
                    round_stats["new_forwards"] += 1
                    
                    if message.contains_misinformation:
                        round_stats["misinformation_spread"] += 1
                        
        return round_stats
        
    def analyze_viral_spread(self) -> Dict:
        """Analyze viral content spread patterns"""
        # Collect message statistics
        all_messages = []
        for group in self.groups.values():
            all_messages.extend(group.messages)
            
        # Find viral messages (forwarded multiple times)
        viral_threshold = 5
        viral_messages = [msg for msg in all_messages if msg.forward_count >= viral_threshold]
        
        # Misinformation analysis
        misinformation_messages = [msg for msg in all_messages if msg.contains_misinformation]
        
        # User behavior analysis
        top_spreaders = sorted(
            self.users.values(),
            key=lambda u: u.messages_sent,
            reverse=True
        )[:5]
        
        # Group activity analysis
        most_active_groups = sorted(
            self.groups.values(),
            key=lambda g: g.message_count,
            reverse=True
        )[:5]
        
        return {
            "total_messages": len(all_messages),
            "viral_messages": len(viral_messages),
            "misinformation_count": len(misinformation_messages),
            "misinformation_ratio": len(misinformation_messages) / max(len(all_messages), 1),
            "top_spreaders": [
                {
                    "name": user.name,
                    "city": user.city,
                    "messages_sent": user.messages_sent,
                    "misinformation_spread": user.misinformation_spread
                }
                for user in top_spreaders
            ],
            "most_active_groups": [
                {
                    "name": group.name,
                    "messages": group.message_count,
                    "misinformation": group.misinformation_count,
                    "members": group.metadata.member_count
                }
                for group in most_active_groups
            ]
        }
        
    def print_network_status(self):
        """Print current network status"""
        analysis = self.analyze_viral_spread()
        
        print(f"\n📊 Network Status (Round {self.simulation_round}):")
        print(f"  Total Messages: {analysis['total_messages']}")
        print(f"  Viral Messages: {analysis['viral_messages']}")
        print(f"  Misinformation: {analysis['misinformation_count']} "
              f"({analysis['misinformation_ratio']:.1%})")
              
        print(f"\n👑 Top Message Spreaders:")
        for spreader in analysis['top_spreaders'][:3]:
            print(f"  {spreader['name']} ({spreader['city']}): "
                  f"Sent={spreader['messages_sent']}, "
                  f"Misinfo={spreader['misinformation_spread']}")
                  
        print(f"\n🔥 Most Active Groups:")
        for group in analysis['most_active_groups'][:3]:
            print(f"  {group['name']}: "
                  f"Messages={group['messages']}, "
                  f"Members={group['members']}")


async def main():
    """Main simulation function"""
    print("🇮🇳 WhatsApp Viral Content Spread Simulation")
    print("=" * 50)
    
    # Create network
    network = WhatsAppNetwork()
    network.create_indian_whatsapp_network(50, 15)
    
    print(f"Created network with {len(network.users)} users and {len(network.groups)} groups")
    
    # Define viral content examples
    viral_content = [
        {
            "text": "BREAKING: Free Jio recharge for everyone! Forward this to 10 groups to get 1GB data",
            "type": "text",
            "virality": 4,
            "misinformation": True
        },
        {
            "text": "Amazing discount at Big Bazaar - 90% off everything! Only today!",
            "type": "text", 
            "virality": 3,
            "misinformation": False
        },
        {
            "text": "Corona vaccine causes magnetism - my cousin's phone sticks to his arm now",
            "type": "text",
            "virality": 4,
            "misinformation": True
        },
        {
            "text": "IPL match fixing scandal exposed! Screenshots leaked",
            "type": "image",
            "virality": 3,
            "misinformation": True
        },
        {
            "text": "New traffic rules - challan for not wearing seatbelt in backseat Rs 5000",
            "type": "text",
            "virality": 2,
            "misinformation": False
        }
    ]
    
    # Inject viral content
    print("\n🚀 Injecting viral content...")
    network.inject_viral_content(viral_content)
    
    # Simulate spreading for 10 rounds
    for round_num in range(10):
        round_stats = network.simulate_round()
        
        if round_num % 2 == 0:  # Print every other round
            network.print_network_status()
            print(f"Round stats: {round_stats}")
            
        await asyncio.sleep(0.5)
        
    # Final analysis
    print("\n📈 Final Viral Spread Analysis:")
    final_analysis = network.analyze_viral_spread()
    
    print(f"Network reached {final_analysis['total_messages']} total messages")
    print(f"Viral threshold crossed by {final_analysis['viral_messages']} messages")
    print(f"Misinformation spread: {final_analysis['misinformation_count']} instances "
          f"({final_analysis['misinformation_ratio']:.1%} of all messages)")
          
    print(f"\n🏆 Hall of Fame - Top Spreaders:")
    for i, spreader in enumerate(final_analysis['top_spreaders'], 1):
        print(f"{i}. {spreader['name']} from {spreader['city']}")
        print(f"   Messages: {spreader['messages_sent']}, "
              f"Misinformation: {spreader['misinformation_spread']}")


if __name__ == "__main__":
    asyncio.run(main())
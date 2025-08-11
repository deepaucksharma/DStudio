#!/usr/bin/env python3
"""
Queue Fairness Algorithm - Episode 2
क्यू निष्पक्षता एल्गोरिदम

Weighted Fair Queuing implementation with IRCTC Tatkal fairness principles
IRCTC Tatkal निष्पक्षता सिद्धांतों के साथ Weighted Fair Queuing implementation

जैसे IRCTC में Tatkal booking fair होनी चाहिए - सबको equal chance मिले!
यह algorithm ensure करती है कि हर user को fair treatment मिले।

Author: Code Developer Agent A5-C-002
Indian Context: IRCTC Tatkal fairness, Zomato delivery priorities, fair resource allocation
"""

import time
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import heapq
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserTier(Enum):
    """User tier for fair queuing - Fair queuing के लिए user tier"""
    PREMIUM = "premium"        # प्रीमियम - Highest priority, more resources
    REGULAR = "regular"        # नियमित - Standard priority  
    BULK = "bulk"             # थोक - Lower priority, background processing
    FREE = "free"             # मुफ्त - Lowest priority, limited resources

class FairnessPolicy(Enum):
    """Fairness policies - निष्पक्षता नीतियां"""
    STRICT_FIFO = "strict_fifo"                    # सख्त FIFO - First come first serve
    WEIGHTED_FAIR = "weighted_fair"                # भारित निष्पक्ष - Based on user tiers
    PROPORTIONAL_SHARE = "proportional_share"      # आनुपातिक साझाकरण - Based on resource allocation
    LOTTERY_SCHEDULING = "lottery_scheduling"       # लॉटरी शेड्यूलिंग - Probabilistic fairness
    IRCTC_TATKAL_FAIR = "irctc_tatkal_fair"       # IRCTC तत्काल निष्पक्ष - Indian context fairness

@dataclass
class FairQueueRequest:
    """Request in fair queue system - Fair queue system में अनुरोध"""
    request_id: str
    user_id: str
    user_tier: UserTier
    arrival_time: datetime
    processing_time_estimate: float  # seconds
    resource_requirement: float     # 0.0 to 1.0 (CPU/memory requirement)
    
    # Fairness tracking
    virtual_finish_time: float = 0.0
    actual_wait_time: float = 0.0
    priority_boost: float = 0.0     # Anti-starvation boost
    
    # Indian context
    region: str = "mumbai"
    service_type: str = "booking"   # booking, payment, delivery, etc.
    is_urgent: bool = False         # Emergency/critical request
    
    def __lt__(self, other):
        """Comparison for heapq - heapq के लिए तुलना"""
        return self.virtual_finish_time < other.virtual_finish_time

@dataclass 
class UserAccount:
    """User account for fairness tracking - निष्पक्षता tracking के लिए user account"""
    user_id: str
    user_tier: UserTier
    
    # Resource allocation
    allocated_bandwidth: float      # Fraction of total resources (0.0 to 1.0)
    consumed_resources: float = 0.0  # Resources used so far
    virtual_time: float = 0.0       # Virtual time for fair queuing
    
    # Fairness metrics
    total_requests: int = 0
    successful_requests: int = 0
    total_wait_time: float = 0.0
    average_wait_time: float = 0.0
    
    # Anti-starvation
    last_service_time: Optional[datetime] = None
    starvation_credits: float = 0.0  # Credits for being starved
    
    # Indian context
    region: str = "mumbai"
    signup_date: datetime = field(default_factory=datetime.now)
    is_verified: bool = False       # Verified accounts get slight boost

class FairQueueScheduler:
    """Fair queue scheduler with multiple fairness policies - कई निष्पक्षता नीतियों के साथ fair queue scheduler"""
    
    def __init__(self, policy: FairnessPolicy = FairnessPolicy.WEIGHTED_FAIR):
        self.policy = policy
        self.request_queue = []  # Priority queue for requests
        self.user_accounts: Dict[str, UserAccount] = {}
        
        # Scheduling state
        self.virtual_clock = 0.0
        self.total_allocated_bandwidth = 0.0
        self.lock = threading.Lock()
        
        # Fairness tracking
        self.fairness_metrics = {
            'total_processed': 0,
            'user_service_times': {},
            'tier_service_counts': {tier.value: 0 for tier in UserTier},
            'starvation_events': 0
        }
        
        # Indian context configurations
        self.tier_weights = {
            UserTier.PREMIUM: 0.4,    # 40% of resources
            UserTier.REGULAR: 0.35,   # 35% of resources  
            UserTier.BULK: 0.2,       # 20% of resources
            UserTier.FREE: 0.05       # 5% of resources
        }
        
        # Regional fairness adjustments
        self.regional_adjustments = {
            'mumbai': 1.0,     # Base adjustment
            'delhi': 0.95,     # Slightly lower due to infrastructure
            'bangalore': 1.05, # Slightly higher due to tech infrastructure
            'tier2': 0.9,      # Tier 2 cities get 10% less
            'rural': 0.8       # Rural areas get 20% less due to connectivity
        }
        
        # Anti-starvation parameters
        self.starvation_threshold = 300.0  # 5 minutes without service
        self.starvation_boost_factor = 2.0  # 2x priority boost when starved
        
        logger.info(f"🎯 Fair Queue Scheduler initialized with {policy.value} policy")
        logger.info(f"   Tier weights: {self.tier_weights}")
    
    def register_user(self, user_id: str, user_tier: UserTier, region: str = "mumbai") -> UserAccount:
        """Register a new user - नया user रजिस्टर करें"""
        
        with self.lock:
            if user_id in self.user_accounts:
                return self.user_accounts[user_id]
            
            # Allocate bandwidth based on tier
            allocated_bandwidth = self.tier_weights[user_tier]
            
            account = UserAccount(
                user_id=user_id,
                user_tier=user_tier,
                allocated_bandwidth=allocated_bandwidth,
                region=region,
                is_verified=random.choice([True, False])  # Random verification status
            )
            
            self.user_accounts[user_id] = account
            self.total_allocated_bandwidth += allocated_bandwidth
            
            logger.info(f"👤 Registered user {user_id} ({user_tier.value}) from {region}")
            logger.info(f"   Allocated bandwidth: {allocated_bandwidth:.3f}")
            
            return account
    
    def enqueue_request(self, request: FairQueueRequest) -> bool:
        """Add request to fair queue - Fair queue में request जोड़ें"""
        
        with self.lock:
            # Ensure user is registered
            if request.user_id not in self.user_accounts:
                self.register_user(request.user_id, request.user_tier, request.region)
            
            account = self.user_accounts[request.user_id]
            
            # Calculate virtual finish time based on policy
            virtual_finish_time = self._calculate_virtual_finish_time(request, account)
            request.virtual_finish_time = virtual_finish_time
            
            # Apply regional and contextual adjustments
            self._apply_contextual_adjustments(request, account)
            
            # Add to priority queue
            heapq.heappush(self.request_queue, request)
            account.total_requests += 1
            
            logger.info(f"📥 Enqueued request {request.request_id} for user {request.user_id}")
            logger.info(f"   Virtual finish time: {virtual_finish_time:.3f}")
            logger.info(f"   Current queue size: {len(self.request_queue)}")
            
            return True
    
    def _calculate_virtual_finish_time(self, request: FairQueueRequest, account: UserAccount) -> float:
        """Calculate virtual finish time for fair scheduling - Fair scheduling के लिए virtual finish time की गणना"""
        
        if self.policy == FairnessPolicy.STRICT_FIFO:
            # Simple FIFO - earliest arrival first
            return request.arrival_time.timestamp()
        
        elif self.policy == FairnessPolicy.WEIGHTED_FAIR:
            # Weighted Fair Queuing - based on allocated bandwidth
            service_time = request.processing_time_estimate / account.allocated_bandwidth
            return account.virtual_time + service_time
        
        elif self.policy == FairnessPolicy.PROPORTIONAL_SHARE:
            # Proportional share based on tier
            share = self.tier_weights[request.user_tier]
            return self.virtual_clock + (request.processing_time_estimate / share)
        
        elif self.policy == FairnessPolicy.LOTTERY_SCHEDULING:
            # Lottery-based scheduling with random component
            base_time = request.arrival_time.timestamp()
            lottery_factor = random.uniform(0.5, 1.5)  # Random factor
            tier_factor = 2.0 - (list(UserTier).index(request.user_tier) * 0.3)  # Higher tier = lower time
            return base_time * lottery_factor / tier_factor
        
        elif self.policy == FairnessPolicy.IRCTC_TATKAL_FAIR:
            # IRCTC-style fairness - considers arrival time, user tier, and anti-gaming measures
            return self._calculate_irctc_tatkal_fairness(request, account)
        
        else:
            return request.arrival_time.timestamp()
    
    def _calculate_irctc_tatkal_fairness(self, request: FairQueueRequest, account: UserAccount) -> float:
        """IRCTC Tatkal-style fairness calculation - IRCTC Tatkal-style निष्पक्षता गणना"""
        
        base_time = request.arrival_time.timestamp()
        
        # User tier adjustment (premium gets slight advantage, but not too much)
        tier_adjustment = {
            UserTier.PREMIUM: 0.9,   # 10% advantage
            UserTier.REGULAR: 1.0,   # No adjustment
            UserTier.BULK: 1.1,      # 10% disadvantage
            UserTier.FREE: 1.2       # 20% disadvantage
        }
        
        adjusted_time = base_time * tier_adjustment[request.user_tier]
        
        # Anti-gaming measures
        # 1. Limit advantage for users with too many recent requests
        recent_requests = sum(1 for req_time in account.user_id if True)  # Simplified
        if account.total_requests > 10:
            gaming_penalty = 1 + (account.total_requests - 10) * 0.01  # 1% penalty per extra request
            adjusted_time *= gaming_penalty
        
        # 2. Regional fairness - users from areas with poor connectivity get slight advantage
        regional_factor = self.regional_adjustments.get(request.region, 1.0)
        adjusted_time *= regional_factor
        
        # 3. Verification bonus
        if account.is_verified:
            adjusted_time *= 0.98  # 2% advantage for verified users
        
        # 4. Anti-starvation boost
        if account.starvation_credits > 0:
            starvation_boost = max(0.1, 1.0 - (account.starvation_credits * 0.1))
            adjusted_time *= starvation_boost
            logger.debug(f"Applied starvation boost to {request.user_id}: {starvation_boost:.3f}")
        
        return adjusted_time
    
    def _apply_contextual_adjustments(self, request: FairQueueRequest, account: UserAccount):
        """Apply Indian context adjustments - भारतीय संदर्भ adjustments लागू करें"""
        
        # Festival season adjustment - during festivals, be more lenient
        current_month = datetime.now().month
        if current_month in [3, 4, 10, 11]:  # Festival months
            request.priority_boost += 0.05
        
        # Peak hour handling - during peak hours, prioritize by service type
        current_hour = datetime.now().hour
        if 8 <= current_hour <= 11 or 18 <= current_hour <= 21:  # Peak hours
            if request.service_type == "booking":
                request.priority_boost += 0.1  # Booking gets priority during peak
            elif request.service_type == "payment":
                request.priority_boost += 0.15  # Payment gets highest priority
        
        # Urgent request handling
        if request.is_urgent:
            request.priority_boost += 0.5
            request.virtual_finish_time *= 0.5  # 50% faster service
    
    def dequeue_next_request(self) -> Optional[FairQueueRequest]:
        """Get next request based on fairness policy - निष्पक्षता नीति के आधार पर अगला request प्राप्त करें"""
        
        with self.lock:
            if not self.request_queue:
                return None
            
            # Check for starvation and apply credits
            self._check_and_handle_starvation()
            
            # Get next request
            next_request = heapq.heappop(self.request_queue)
            
            # Update account metrics
            account = self.user_accounts[next_request.user_id]
            account.virtual_time = next_request.virtual_finish_time
            account.last_service_time = datetime.now()
            account.successful_requests += 1
            
            # Calculate actual wait time
            actual_wait_time = (datetime.now() - next_request.arrival_time).total_seconds()
            next_request.actual_wait_time = actual_wait_time
            account.total_wait_time += actual_wait_time
            account.average_wait_time = account.total_wait_time / account.successful_requests
            
            # Update global metrics
            self.fairness_metrics['total_processed'] += 1
            self.fairness_metrics['tier_service_counts'][next_request.user_tier.value] += 1
            
            # Update virtual clock
            self.virtual_clock = max(self.virtual_clock, next_request.virtual_finish_time)
            
            logger.info(f"📤 Dequeued request {next_request.request_id} for user {next_request.user_id}")
            logger.info(f"   Actual wait time: {actual_wait_time:.2f}s")
            logger.info(f"   User average wait: {account.average_wait_time:.2f}s")
            
            return next_request
    
    def _check_and_handle_starvation(self):
        """Check for starved users and apply credits - भूखे users की जांच करें और credits लागू करें"""
        
        current_time = datetime.now()
        
        for user_id, account in self.user_accounts.items():
            if account.last_service_time is None:
                # New user, set baseline
                account.last_service_time = current_time
                continue
            
            time_since_service = (current_time - account.last_service_time).total_seconds()
            
            if time_since_service > self.starvation_threshold:
                # User is being starved
                old_credits = account.starvation_credits
                account.starvation_credits += (time_since_service - self.starvation_threshold) / 60.0  # Credits per minute
                
                # Update requests in queue with starvation boost
                for request in self.request_queue:
                    if request.user_id == user_id:
                        request.virtual_finish_time *= (1.0 / self.starvation_boost_factor)
                
                if old_credits == 0:  # First time starved
                    self.fairness_metrics['starvation_events'] += 1
                    logger.warning(f"🚨 Starvation detected for user {user_id}")
                    logger.warning(f"   Time since last service: {time_since_service:.1f}s")
                    logger.warning(f"   Applied starvation credits: {account.starvation_credits:.2f}")
                
                # Re-heapify to apply starvation boost
                heapq.heapify(self.request_queue)
    
    def get_fairness_report(self) -> Dict[str, Any]:
        """Generate fairness analysis report - निष्पक्षता विश्लेषण रिपोर्ट जेनरेट करें"""
        
        with self.lock:
            report = {
                'policy': self.policy.value,
                'timestamp': datetime.now().isoformat(),
                'queue_status': {
                    'current_queue_size': len(self.request_queue),
                    'total_users': len(self.user_accounts),
                    'virtual_clock': self.virtual_clock
                },
                'processing_stats': dict(self.fairness_metrics),
                'user_analysis': {},
                'tier_fairness_analysis': {},
                'regional_analysis': {}
            }
            
            # User-level analysis
            for user_id, account in self.user_accounts.items():
                if account.successful_requests > 0:
                    report['user_analysis'][user_id] = {
                        'tier': account.user_tier.value,
                        'region': account.region,
                        'total_requests': account.total_requests,
                        'successful_requests': account.successful_requests,
                        'success_rate': account.successful_requests / account.total_requests,
                        'average_wait_time': account.average_wait_time,
                        'allocated_bandwidth': account.allocated_bandwidth,
                        'starvation_credits': account.starvation_credits,
                        'is_verified': account.is_verified
                    }
            
            # Tier-level fairness analysis
            for tier in UserTier:
                tier_users = [acc for acc in self.user_accounts.values() if acc.user_tier == tier]
                if tier_users:
                    successful_users = [acc for acc in tier_users if acc.successful_requests > 0]
                    if successful_users:
                        avg_wait_times = [acc.average_wait_time for acc in successful_users]
                        report['tier_fairness_analysis'][tier.value] = {
                            'total_users': len(tier_users),
                            'active_users': len(successful_users),
                            'average_wait_time': sum(avg_wait_times) / len(avg_wait_times),
                            'min_wait_time': min(avg_wait_times),
                            'max_wait_time': max(avg_wait_times),
                            'allocated_bandwidth': self.tier_weights[tier],
                            'service_count': self.fairness_metrics['tier_service_counts'][tier.value]
                        }
            
            # Regional analysis
            regional_data = {}
            for account in self.user_accounts.values():
                if account.successful_requests > 0:
                    region = account.region
                    if region not in regional_data:
                        regional_data[region] = []
                    regional_data[region].append(account.average_wait_time)
            
            for region, wait_times in regional_data.items():
                report['regional_analysis'][region] = {
                    'user_count': len(wait_times),
                    'average_wait_time': sum(wait_times) / len(wait_times),
                    'adjustment_factor': self.regional_adjustments.get(region, 1.0)
                }
            
            return report
    
    def export_fairness_metrics(self, filename: str):
        """Export fairness metrics to JSON - निष्पक्षता metrics को JSON में export करें"""
        
        report = self.get_fairness_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Fairness report exported to: {filename}")
    
    def simulate_user_requests(self, num_requests: int = 100, duration_seconds: int = 60):
        """Simulate user requests for testing - परीक्षण के लिए user requests simulate करें"""
        
        logger.info(f"🎭 Starting simulation: {num_requests} requests over {duration_seconds} seconds")
        
        # Create diverse set of users
        users = [
            ("user_premium_mumbai", UserTier.PREMIUM, "mumbai", "booking"),
            ("user_regular_delhi", UserTier.REGULAR, "delhi", "payment"),
            ("user_bulk_bangalore", UserTier.BULK, "bangalore", "delivery"),
            ("user_free_tier2", UserTier.FREE, "tier2", "booking"),
            ("user_premium_chennai", UserTier.PREMIUM, "chennai", "payment"),
            ("user_regular_mumbai", UserTier.REGULAR, "mumbai", "booking"),
            ("user_bulk_rural", UserTier.BULK, "rural", "delivery"),
            ("user_free_delhi", UserTier.FREE, "delhi", "booking")
        ]
        
        # Register users
        for user_id, tier, region, _ in users:
            self.register_user(user_id, tier, region)
        
        # Generate requests
        requests_generated = 0
        start_time = datetime.now()
        
        while requests_generated < num_requests and (datetime.now() - start_time).total_seconds() < duration_seconds:
            # Pick random user
            user_id, tier, region, service_type = random.choice(users)
            
            # Create request
            request = FairQueueRequest(
                request_id=f"req_{requests_generated:04d}",
                user_id=user_id,
                user_tier=tier,
                arrival_time=datetime.now(),
                processing_time_estimate=random.uniform(1.0, 5.0),  # 1-5 seconds
                resource_requirement=random.uniform(0.1, 0.8),      # 10-80% resource usage
                region=region,
                service_type=service_type,
                is_urgent=random.random() < 0.1  # 10% urgent requests
            )
            
            self.enqueue_request(request)
            requests_generated += 1
            
            # Random inter-arrival time
            time.sleep(random.uniform(0.1, 1.0))
        
        logger.info(f"✅ Simulation completed: {requests_generated} requests generated")

def main():
    """Main function to demonstrate fair queue algorithm - मुख्य function"""
    
    print("⚖️  Queue Fairness Algorithm Demo - Episode 2")
    print("Queue निष्पक्षता एल्गोरिदम डेमो - एपिसोड 2\n")
    
    # Test different fairness policies
    policies_to_test = [
        FairnessPolicy.WEIGHTED_FAIR,
        FairnessPolicy.IRCTC_TATKAL_FAIR,
        FairnessPolicy.PROPORTIONAL_SHARE,
        FairnessPolicy.LOTTERY_SCHEDULING
    ]
    
    print(f"Testing {len(policies_to_test)} fairness policies:")
    for i, policy in enumerate(policies_to_test, 1):
        print(f"  {i}. {policy.value}")
    
    results = {}
    
    for policy in policies_to_test:
        print(f"\n{'='*80}")
        print(f"TESTING: {policy.value.upper()}")
        print(f"परीक्षण: {policy.value.upper()}")
        print('='*80)
        
        # Create scheduler with policy
        scheduler = FairQueueScheduler(policy)
        
        # Run simulation
        scheduler.simulate_user_requests(num_requests=50, duration_seconds=30)
        
        # Process some requests
        processed_requests = []
        process_count = min(30, len(scheduler.request_queue))  # Process up to 30 requests
        
        print(f"\nProcessing {process_count} requests...")
        for i in range(process_count):
            request = scheduler.dequeue_next_request()
            if request:
                processed_requests.append(request)
            else:
                break
            
            # Small delay to simulate processing
            time.sleep(0.1)
        
        # Generate fairness report
        report = scheduler.get_fairness_report()
        results[policy.value] = report
        
        # Print summary
        print(f"\n📊 SUMMARY FOR {policy.value.upper()}:")
        print(f"   Requests processed: {len(processed_requests)}")
        print(f"   Total users: {report['queue_status']['total_users']}")
        print(f"   Starvation events: {report['processing_stats']['starvation_events']}")
        
        # Tier fairness analysis
        if report['tier_fairness_analysis']:
            print(f"\n   Tier-wise Average Wait Times:")
            for tier, data in report['tier_fairness_analysis'].items():
                print(f"     {tier}: {data['average_wait_time']:.2f}s ({data['active_users']} users)")
        
        # Regional fairness
        if report['regional_analysis']:
            print(f"\n   Regional Average Wait Times:")
            for region, data in report['regional_analysis'].items():
                print(f"     {region}: {data['average_wait_time']:.2f}s ({data['user_count']} users)")
        
        # Export detailed report
        report_filename = f"fairness_report_{policy.value}.json"
        scheduler.export_fairness_metrics(report_filename)
        
        print(f"   📁 Detailed report: {report_filename}")
    
    # Comparative analysis
    print(f"\n{'='*80}")
    print("COMPARATIVE FAIRNESS ANALYSIS | तुलनात्मक निष्पक्षता विश्लेषण")
    print('='*80)
    
    # Compare starvation events
    print("\n🚨 Starvation Events Comparison:")
    starvation_data = []
    for policy_name, report in results.items():
        starvation_count = report['processing_stats']['starvation_events']
        starvation_data.append((policy_name, starvation_count))
        print(f"   {policy_name}: {starvation_count} events")
    
    # Find best policy for starvation prevention
    best_starvation_policy = min(starvation_data, key=lambda x: x[1])
    print(f"   🏆 Best for starvation prevention: {best_starvation_policy[0]}")
    
    # Compare tier fairness
    print(f"\n⚖️  Tier Fairness Comparison (Average Wait Times):")
    tier_comparison = {}
    
    for policy_name, report in results.items():
        if report['tier_fairness_analysis']:
            print(f"\n   {policy_name}:")
            for tier, data in report['tier_fairness_analysis'].items():
                if tier not in tier_comparison:
                    tier_comparison[tier] = []
                tier_comparison[tier].append((policy_name, data['average_wait_time']))
                print(f"     {tier}: {data['average_wait_time']:.2f}s")
    
    # Regional fairness comparison
    print(f"\n🌍 Regional Fairness Comparison:")
    for policy_name, report in results.items():
        if report['regional_analysis']:
            print(f"\n   {policy_name}:")
            for region, data in report['regional_analysis'].items():
                print(f"     {region}: {data['average_wait_time']:.2f}s")
    
    # Recommendations
    print(f"\n{'='*80}")
    print("RECOMMENDATIONS | सिफारिशें")
    print('='*80)
    
    recommendations = [
        f"1. For IRCTC-like systems: Use '{FairnessPolicy.IRCTC_TATKAL_FAIR.value}' policy",
        "   IRCTC जैसे सिस्टम के लिए: IRCTC Tatkal Fair policy का उपयोग करें",
        
        f"2. For general systems: '{FairnessPolicy.WEIGHTED_FAIR.value}' provides good balance",
        "   सामान्य सिस्टम के लिए: Weighted Fair अच्छा संतुलन प्रदान करता है",
        
        "3. Monitor starvation events and adjust policies accordingly",
        "   Starvation events की निगरानी करें और तदनुसार policies adjust करें",
        
        "4. Regional adjustments are crucial for Indian context",
        "   भारतीय संदर्भ के लिए regional adjustments महत्वपूर्ण हैं",
        
        "5. Anti-gaming measures prevent system abuse",
        "   Anti-gaming उपाय system abuse को रोकते हैं"
    ]
    
    for rec in recommendations:
        print(f"   {rec}")
    
    # Export comparative analysis
    comparative_report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'policies_tested': [p.value for p in policies_to_test],
        'starvation_comparison': dict(starvation_data),
        'best_starvation_policy': best_starvation_policy[0],
        'tier_fairness_comparison': tier_comparison,
        'full_reports': results,
        'recommendations': recommendations
    }
    
    with open('fairness_comparative_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(comparative_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Comparative analysis exported: fairness_comparative_analysis.json")
    
    print(f"\n🎉 Queue Fairness Algorithm demonstration completed!")
    print("Queue निष्पक्षता एल्गोरिदम प्रदर्शन पूर्ण!")
    
    print(f"\n💡 KEY LEARNINGS | मुख्य शिक्षाएं:")
    print("1. Different fairness policies suit different use cases")
    print("   अलग-अलग निष्पक्षता नीतियां अलग-अलग उपयोग के मामलों के लिए उपयुक्त हैं")
    print("2. IRCTC-style fairness prevents gaming and ensures equity")
    print("   IRCTC-style निष्पक्षता gaming को रोकती है और equity ensure करती है")
    print("3. Anti-starvation measures are essential for user satisfaction")
    print("   उपयोगकर्ता संतुष्टि के लिए anti-starvation उपाय आवश्यक हैं")
    print("4. Regional adjustments matter in diverse markets like India")
    print("   भारत जैसे diverse markets में regional adjustments मायने रखते हैं")

if __name__ == "__main__":
    main()
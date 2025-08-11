#!/usr/bin/env python3
"""
Chaos Monkey Implementation - Episode 2
चाओस इंजीनियरिंग के लिए सर्विस टर्मिनेशन टूल

Production-ready chaos monkey for terminating services randomly to test system resilience.
मुंबई लोकल ट्रेन की तरह - कभी कभी रुकना पड़ता है, फिर देखते हैं कि सिस्टम कैसे handle करता है!

Author: Code Developer Agent A5-C-002
Indian Context: IRCTC, Zomato, Flipkart scale chaos testing
"""

import random
import time
import logging
import json
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import signal
import os

# Hindi + English logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s | समय: %(asctime)s'
)
logger = logging.getLogger(__name__)

class ChaosMode(Enum):
    """Chaos execution modes - चाओस के तरीके"""
    CONSERVATIVE = "conservative"  # धीरे धीरे - like testing during off-peak hours
    AGGRESSIVE = "aggressive"      # तेज़ी से - like GameDay testing
    GRADUAL = "gradual"           # बढ़ते हुए - progressive chaos
    MUMBAI_MONSOON = "mumbai_monsoon"  # मुंबई मानसून - unpredictable chaos

@dataclass
class ServiceTarget:
    """Target service for chaos - टारगेट सर्विस"""
    name: str
    process_name: str
    port: int
    priority: int  # 1=critical (payment), 5=non-critical (recommendations)
    region: str   # "mumbai", "delhi", "bangalore"
    max_downtime_seconds: int
    blast_radius_limit: float  # 0.0 to 1.0 (percentage of instances)
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ChaosEvent:
    """Chaos event record - चाओस इवेंट रिकॉर्ड"""
    event_id: str
    timestamp: datetime
    service_name: str
    action: str
    success: bool
    duration_seconds: float
    impact_score: float  # 0-10 scale
    recovery_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    
    def to_dict(self):
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

class SafetyController:
    """Safety controls for chaos engineering - सुरक्षा नियंत्रण"""
    
    def __init__(self, max_concurrent_failures: int = 2):
        self.max_concurrent_failures = max_concurrent_failures
        self.active_failures = []
        self.safety_lock = threading.Lock()
        
        # Indian business hours (IST) - भारतीय व्यापारिक घंटे
        self.safe_hours = {
            'start': 10,  # 10 AM IST
            'end': 18     # 6 PM IST  
        }
        
        # Critical periods to avoid - महत्वपूर्ण समय जब chaos नहीं करना
        self.avoid_periods = [
            "diwali_sale",      # दिवाली सेल
            "ipl_final",        # आईपीएल फाइनल
            "jee_results",      # जेईई रिजल्ट
            "salary_day",       # तनख्वाह का दिन
            "festival_booking"  # त्योहार बुकिंग
        ]
    
    def is_safe_to_proceed(self, service: ServiceTarget) -> tuple[bool, str]:
        """Check if it's safe to cause chaos - सुरक्षा जांच"""
        
        with self.safety_lock:
            # Check concurrent failures - समानांतर failures की जांच
            if len(self.active_failures) >= self.max_concurrent_failures:
                return False, f"Too many concurrent failures: {len(self.active_failures)}"
            
            # Check business hours - व्यापारिक घंटों की जांच
            current_hour = datetime.now().hour
            if not (self.safe_hours['start'] <= current_hour <= self.safe_hours['end']):
                return False, f"Outside safe hours (10 AM - 6 PM IST)"
            
            # Check service priority - सर्विस priority की जांच
            if service.priority <= 2:  # Critical services
                # Extra caution for critical services like payment, user auth
                if random.random() < 0.7:  # 70% chance to skip critical services
                    return False, "Critical service - safety override"
            
            # Mumbai monsoon logic - मुंबई मानसून की तरह
            if datetime.now().month in [6, 7, 8, 9]:  # Monsoon months
                # During monsoon, be extra careful like Mumbai trains
                if random.random() < 0.3:
                    return False, "Monsoon season - reduced chaos frequency"
            
            return True, "Safe to proceed"
    
    def register_failure(self, event_id: str, service_name: str):
        """Register an active failure - सक्रिय failure रजिस्टर करें"""
        with self.safety_lock:
            self.active_failures.append({
                'event_id': event_id,
                'service_name': service_name,
                'start_time': datetime.now()
            })
            logger.info(f"🔥 Registered failure: {service_name} | फेलियर रजिस्टर: {service_name}")
    
    def unregister_failure(self, event_id: str):
        """Unregister a failure when service recovers - रिकवरी पर failure हटाएं"""
        with self.safety_lock:
            self.active_failures = [f for f in self.active_failures if f['event_id'] != event_id]
            logger.info(f"✅ Unregistered failure: {event_id} | फेलियर हटाया: {event_id}")

class ChaosMonkey:
    """Main Chaos Monkey class - मुख्य चाओस मंकी क्लास"""
    
    def __init__(self, mode: ChaosMode = ChaosMode.CONSERVATIVE):
        self.mode = mode
        self.safety_controller = SafetyController()
        self.events_history: List[ChaosEvent] = []
        self.targets: List[ServiceTarget] = []
        self.is_running = False
        self.stats = {
            'total_chaos_events': 0,
            'successful_events': 0,
            'failed_events': 0,
            'total_downtime_seconds': 0,
            'services_affected': set()
        }
        
        logger.info(f"🐒 Chaos Monkey initialized in {mode.value} mode | चाओस मंकी शुरू")
    
    def add_target_service(self, service: ServiceTarget):
        """Add a service to chaos target list - सर्विस को टारगेट लिस्ट में जोड़ें"""
        self.targets.append(service)
        logger.info(f"🎯 Added target: {service.name} (Priority: {service.priority})")
        
        # Indian service examples - भारतीय सर्विस उदाहरण
        if "payment" in service.name.lower():
            logger.warning(f"⚠️  Payment service added - Extra caution enabled | पेमेंट सर्विस - अतिरिक्त सावधानी")
        elif "recommendation" in service.name.lower():
            logger.info(f"📊 Recommendation service - Low risk | रेकमंडेशन - कम जोखिम")
    
    def load_indian_service_targets(self):
        """Load typical Indian service targets - भारतीय सर्विस टार्गेट लोड करें"""
        
        # IRCTC-like booking service
        irctc_booking = ServiceTarget(
            name="irctc_booking_service",
            process_name="booking-service",
            port=8080,
            priority=1,  # Critical - ticket booking
            region="mumbai",
            max_downtime_seconds=30,
            blast_radius_limit=0.1  # Only 10% instances
        )
        
        # Zomato-like delivery service
        zomato_delivery = ServiceTarget(
            name="zomato_delivery_service", 
            process_name="delivery-service",
            port=8081,
            priority=2,  # Important but not critical
            region="bangalore", 
            max_downtime_seconds=120,
            blast_radius_limit=0.2
        )
        
        # Flipkart-like recommendation service
        flipkart_recommendations = ServiceTarget(
            name="flipkart_recommendation_service",
            process_name="recommendation-service", 
            port=8082,
            priority=4,  # Less critical
            region="delhi",
            max_downtime_seconds=300,
            blast_radius_limit=0.5
        )
        
        # Paytm-like wallet service
        paytm_wallet = ServiceTarget(
            name="paytm_wallet_service",
            process_name="wallet-service",
            port=8083, 
            priority=1,  # Critical - money involved
            region="mumbai",
            max_downtime_seconds=15,
            blast_radius_limit=0.05  # Very limited blast radius
        )
        
        for service in [irctc_booking, zomato_delivery, flipkart_recommendations, paytm_wallet]:
            self.add_target_service(service)
    
    def _select_chaos_target(self) -> Optional[ServiceTarget]:
        """Select a target for chaos based on mode - चाओस के लिए टारगेट चुनें"""
        
        if not self.targets:
            return None
        
        if self.mode == ChaosMode.CONSERVATIVE:
            # Prefer non-critical services - गैर-महत्वपूर्ण सर्विसेस पसंद करें
            non_critical = [t for t in self.targets if t.priority >= 3]
            if non_critical:
                return random.choice(non_critical)
        
        elif self.mode == ChaosMode.AGGRESSIVE:
            # Can target any service - कोई भी सर्विस टारगेट कर सकते हैं
            return random.choice(self.targets)
        
        elif self.mode == ChaosMode.GRADUAL:
            # Start with low priority, gradually increase - धीरे धीरे priority बढ़ाएं
            total_events = len(self.events_history)
            if total_events < 10:
                low_priority = [t for t in self.targets if t.priority >= 4]
                if low_priority:
                    return random.choice(low_priority)
            elif total_events < 50:
                medium_priority = [t for t in self.targets if 2 <= t.priority <= 3]
                if medium_priority:
                    return random.choice(medium_priority)
        
        elif self.mode == ChaosMode.MUMBAI_MONSOON:
            # Unpredictable like Mumbai monsoon - मुंबई मानसून की तरह अप्रत्याशित
            # Sometimes hit critical services, sometimes don't
            if random.random() < 0.3:  # 30% chance for critical
                critical = [t for t in self.targets if t.priority <= 2]
                if critical:
                    return random.choice(critical)
            else:
                non_critical = [t for t in self.targets if t.priority >= 3]
                if non_critical:
                    return random.choice(non_critical)
        
        # Default fallback
        return random.choice(self.targets)
    
    def _calculate_chaos_intensity(self) -> float:
        """Calculate chaos intensity based on mode - चाओस की तीव्रता की गणना"""
        
        base_intensity = {
            ChaosMode.CONSERVATIVE: 0.1,    # 10% intensity
            ChaosMode.AGGRESSIVE: 0.8,      # 80% intensity  
            ChaosMode.GRADUAL: min(0.1 + len(self.events_history) * 0.01, 0.6),  # Gradual increase
            ChaosMode.MUMBAI_MONSOON: random.uniform(0.2, 0.9)  # Random like weather
        }
        
        intensity = base_intensity.get(self.mode, 0.3)
        
        # Mumbai traffic adjustment - मुंबई ट्रैफिक adjustment
        current_hour = datetime.now().hour
        if 8 <= current_hour <= 10 or 18 <= current_hour <= 21:  # Peak hours
            intensity *= 0.5  # Reduce chaos during peak hours
            logger.info("🚗 Peak hours detected - Reducing chaos intensity | पीक ऑवर्स - कम चाओस")
        
        return intensity
    
    def _terminate_service_instance(self, service: ServiceTarget, intensity: float) -> ChaosEvent:
        """Terminate service instances - सर्विस इंस्टेंस बंद करें"""
        
        event_id = f"chaos_{service.name}_{int(time.time())}"
        start_time = datetime.now()
        
        try:
            # Calculate how many instances to terminate based on blast radius
            instances_to_kill = max(1, int(service.blast_radius_limit * 10 * intensity))
            
            logger.info(f"🔥 Starting chaos: {service.name} | चाओस शुरू: {service.name}")
            logger.info(f"   Intensity: {intensity:.2f} | तीव्रता: {intensity:.2f}")
            logger.info(f"   Instances to terminate: {instances_to_kill} | बंद करने वाले instances: {instances_to_kill}")
            
            # Register the failure with safety controller
            self.safety_controller.register_failure(event_id, service.name)
            
            # Simulate service termination (in real world, this would use Kubernetes API, Docker, etc.)
            chaos_duration = min(
                random.uniform(5, service.max_downtime_seconds),
                service.max_downtime_seconds
            )
            
            # For demonstration, we'll simulate the chaos
            # In production, you'd use:
            # - kubectl delete pod (for Kubernetes)
            # - docker stop (for Docker)
            # - systemctl stop (for systemd services)
            # - kill -9 PID (for process termination)
            
            logger.info(f"💥 Simulating {chaos_duration:.1f}s downtime for {service.name}")
            logger.info(f"   In production: kubectl delete pod {service.process_name}-*")
            
            # Simulate chaos impact
            time.sleep(min(chaos_duration, 2))  # Don't actually sleep too long in demo
            
            # Calculate impact score based on service priority and duration
            impact_score = self._calculate_impact_score(service, chaos_duration, instances_to_kill)
            
            # Create successful chaos event
            event = ChaosEvent(
                event_id=event_id,
                timestamp=start_time,
                service_name=service.name,
                action=f"terminate_{instances_to_kill}_instances",
                success=True,
                duration_seconds=chaos_duration,
                impact_score=impact_score,
                recovery_time_seconds=chaos_duration * 1.2  # Recovery usually takes 20% longer
            )
            
            # Update statistics
            self.stats['total_chaos_events'] += 1
            self.stats['successful_events'] += 1
            self.stats['total_downtime_seconds'] += chaos_duration
            self.stats['services_affected'].add(service.name)
            
            logger.info(f"✅ Chaos completed: {service.name} | चाओस पूर्ण: {service.name}")
            logger.info(f"   Impact Score: {impact_score:.1f}/10 | प्रभाव स्कोर: {impact_score:.1f}/10")
            
            return event
            
        except Exception as e:
            logger.error(f"❌ Chaos failed: {service.name} - {str(e)} | चाओस असफल: {service.name}")
            
            event = ChaosEvent(
                event_id=event_id,
                timestamp=start_time,
                service_name=service.name,
                action="terminate_instances",
                success=False,
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                impact_score=0,
                error_message=str(e)
            )
            
            self.stats['total_chaos_events'] += 1
            self.stats['failed_events'] += 1
            
            return event
            
        finally:
            # Always unregister the failure
            self.safety_controller.unregister_failure(event_id)
    
    def _calculate_impact_score(self, service: ServiceTarget, duration: float, instances: int) -> float:
        """Calculate impact score (0-10) - प्रभाव स्कोर की गणना"""
        
        # Base score from service priority (1=critical=high score, 5=low=low score)
        priority_score = (6 - service.priority) * 2  # Critical=10, Low=2
        
        # Duration factor (longer duration = higher impact)
        duration_factor = min(duration / service.max_downtime_seconds, 1.0)
        
        # Instances factor (more instances = higher impact)  
        instances_factor = min(instances / 5.0, 1.0)
        
        # Regional factor (Mumbai = higher impact due to higher traffic)
        region_multiplier = {
            'mumbai': 1.2,    # मुंबई - highest traffic
            'delhi': 1.1,     # दिल्ली - high traffic  
            'bangalore': 1.0, # बैंगलोर - moderate traffic
            'chennai': 0.9,   # चेन्नई - lower traffic
            'kolkata': 0.9    # कोलकाता - lower traffic
        }.get(service.region, 1.0)
        
        impact_score = (priority_score * duration_factor * instances_factor * region_multiplier)
        return min(impact_score, 10.0)
    
    def run_single_chaos_event(self) -> Optional[ChaosEvent]:
        """Run a single chaos event - एक चाओस इवेंट चलाएं"""
        
        # Select target
        target = self._select_chaos_target()
        if not target:
            logger.warning("No chaos targets available | कोई चाओस टारगेट उपलब्ध नहीं")
            return None
        
        # Safety check
        safe, reason = self.safety_controller.is_safe_to_proceed(target)
        if not safe:
            logger.info(f"🛡️  Safety override: {reason} | सुरक्षा रोक: {reason}")
            return None
        
        # Calculate intensity
        intensity = self._calculate_chaos_intensity()
        
        # Execute chaos
        event = self._terminate_service_instance(target, intensity)
        self.events_history.append(event)
        
        return event
    
    def start_continuous_chaos(self, interval_seconds: int = 300):
        """Start continuous chaos engineering - निरंतर चाओस इंजीनियरिंग शुरू करें"""
        
        self.is_running = True
        logger.info(f"🚀 Starting continuous chaos mode | निरंतर चाओस मोड शुरू")
        logger.info(f"   Interval: {interval_seconds}s | अंतराल: {interval_seconds}s")
        logger.info(f"   Mode: {self.mode.value} | मोड: {self.mode.value}")
        
        while self.is_running:
            try:
                # Run chaos event
                event = self.run_single_chaos_event()
                
                if event:
                    logger.info(f"📊 Chaos stats: {self.get_stats_summary()}")
                
                # Wait for next chaos event
                logger.info(f"⏱️  Waiting {interval_seconds}s for next chaos | अगले चाओस के लिए प्रतीक्षा")
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopping chaos monkey | चाओस मंकी बंद कर रहे हैं")
                self.stop()
                break
            except Exception as e:
                logger.error(f"❌ Error in chaos loop: {e} | चाओस लूप में एरर: {e}")
                time.sleep(30)  # Wait before retry
    
    def stop(self):
        """Stop chaos monkey - चाओस मंकी बंद करें"""
        self.is_running = False
        logger.info("🛑 Chaos Monkey stopped | चाओस मंकी बंद")
    
    def get_stats_summary(self) -> str:
        """Get statistics summary - आंकड़ों का सारांश"""
        success_rate = (self.stats['successful_events'] / max(self.stats['total_chaos_events'], 1)) * 100
        
        return (f"Events: {self.stats['total_chaos_events']}, "
                f"Success: {success_rate:.1f}%, "
                f"Downtime: {self.stats['total_downtime_seconds']:.1f}s, "
                f"Services: {len(self.stats['services_affected'])}")
    
    def generate_chaos_report(self) -> Dict:
        """Generate detailed chaos report - विस्तृत चाओस रिपोर्ट"""
        
        # Calculate insights
        total_events = len(self.events_history)
        if total_events == 0:
            return {"message": "No chaos events executed yet"}
        
        successful_events = [e for e in self.events_history if e.success]
        failed_events = [e for e in self.events_history if not e.success]
        
        # Impact analysis
        high_impact_events = [e for e in successful_events if e.impact_score >= 7]
        medium_impact_events = [e for e in successful_events if 4 <= e.impact_score < 7]
        low_impact_events = [e for e in successful_events if e.impact_score < 4]
        
        # Service-wise breakdown
        service_stats = {}
        for event in self.events_history:
            if event.service_name not in service_stats:
                service_stats[event.service_name] = {
                    'total_events': 0,
                    'successful_events': 0,
                    'total_downtime': 0,
                    'avg_impact_score': 0
                }
            
            stats = service_stats[event.service_name]
            stats['total_events'] += 1
            if event.success:
                stats['successful_events'] += 1
                stats['total_downtime'] += event.duration_seconds
                stats['avg_impact_score'] += event.impact_score
        
        # Calculate averages
        for service_name, stats in service_stats.items():
            if stats['successful_events'] > 0:
                stats['avg_impact_score'] /= stats['successful_events']
        
        report = {
            'chaos_monkey_mode': self.mode.value,
            'report_generated_at': datetime.now().isoformat(),
            'summary': {
                'total_chaos_events': total_events,
                'successful_events': len(successful_events),
                'failed_events': len(failed_events),
                'success_rate_percentage': (len(successful_events) / total_events) * 100,
                'total_downtime_seconds': sum(e.duration_seconds for e in successful_events),
                'average_impact_score': sum(e.impact_score for e in successful_events) / max(len(successful_events), 1),
                'services_affected': len(self.stats['services_affected'])
            },
            'impact_analysis': {
                'high_impact_events': len(high_impact_events),    # 7-10 score
                'medium_impact_events': len(medium_impact_events), # 4-7 score
                'low_impact_events': len(low_impact_events)        # 0-4 score
            },
            'service_breakdown': service_stats,
            'recent_events': [event.to_dict() for event in self.events_history[-10:]],  # Last 10 events
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on chaos history - सिफारिशों की सूची"""
        recommendations = []
        
        # Analyze patterns
        if len(self.events_history) >= 5:
            high_impact_events = [e for e in self.events_history if e.impact_score >= 7]
            
            if len(high_impact_events) > len(self.events_history) * 0.3:
                recommendations.append(
                    "बहुत अधिक high-impact events हो रहे हैं - chaos intensity कम करने पर विचार करें"
                )
            
            failed_events = [e for e in self.events_history if not e.success]
            if len(failed_events) > len(self.events_history) * 0.2:
                recommendations.append(
                    "Failed events बहुत हैं - safety controls की जांच करें"
                )
            
            # Service-specific recommendations
            service_impact = {}
            for event in self.events_history:
                if event.success and event.service_name not in service_impact:
                    service_impact[event.service_name] = []
                if event.success:
                    service_impact[event.service_name].append(event.impact_score)
            
            for service_name, scores in service_impact.items():
                avg_score = sum(scores) / len(scores)
                if avg_score >= 8:
                    recommendations.append(
                        f"{service_name} में बहुत high impact - इस service के लिए अलग strategy अपनाएं"
                    )
        
        # General recommendations
        if len(recommendations) == 0:
            recommendations.extend([
                "चाओस इंजीनियरिंग well controlled है - continue current approach",
                "GameDay exercises के लिए तैयार हैं",
                "Production में gradual rollout consider करें"
            ])
        
        return recommendations

def main():
    """Main function to demonstrate Chaos Monkey - मुख्य function"""
    
    print("🐒 Chaos Monkey Demo - Episode 2")
    print("चाओस इंजीनियरिंग डेमो - एपिसोड 2\n")
    
    # Initialize chaos monkey in conservative mode
    chaos_monkey = ChaosMonkey(mode=ChaosMode.CONSERVATIVE)
    
    # Load Indian service targets
    chaos_monkey.load_indian_service_targets()
    
    print(f"Loaded {len(chaos_monkey.targets)} service targets:")
    for i, target in enumerate(chaos_monkey.targets, 1):
        print(f"  {i}. {target.name} (Priority: {target.priority}, Region: {target.region})")
    
    print("\n" + "="*60)
    print("Running 5 chaos events for demonstration...")
    print("डेमो के लिए 5 चाओस इवेंट चला रहे हैं...")
    print("="*60 + "\n")
    
    # Run a few chaos events for demonstration
    for i in range(5):
        print(f"--- Chaos Event {i+1} ---")
        event = chaos_monkey.run_single_chaos_event()
        
        if event:
            print(f"✅ Event completed: {event.action} on {event.service_name}")
            print(f"   Impact Score: {event.impact_score:.1f}/10")
            print(f"   Duration: {event.duration_seconds:.1f}s")
            if event.recovery_time_seconds:
                print(f"   Recovery Time: {event.recovery_time_seconds:.1f}s")
        else:
            print("⏭️  Event skipped due to safety controls")
        
        print(f"📊 Current Stats: {chaos_monkey.get_stats_summary()}")
        print()
        
        time.sleep(1)  # Small delay for demo
    
    # Generate final report
    print("\n" + "="*60)
    print("FINAL CHAOS REPORT | अंतिम चाओस रिपोर्ट")
    print("="*60)
    
    report = chaos_monkey.generate_chaos_report()
    
    # Print summary
    summary = report['summary']
    print(f"\n📈 SUMMARY:")
    print(f"   Total Events: {summary['total_chaos_events']}")
    print(f"   Success Rate: {summary['success_rate_percentage']:.1f}%")
    print(f"   Total Downtime: {summary['total_downtime_seconds']:.1f}s")
    print(f"   Average Impact: {summary['average_impact_score']:.1f}/10")
    print(f"   Services Affected: {summary['services_affected']}")
    
    # Print impact analysis
    impact = report['impact_analysis']
    print(f"\n🎯 IMPACT ANALYSIS:")
    print(f"   High Impact Events (7-10): {impact['high_impact_events']}")
    print(f"   Medium Impact Events (4-7): {impact['medium_impact_events']}")
    print(f"   Low Impact Events (0-4): {impact['low_impact_events']}")
    
    # Print recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"   • {rec}")
    
    # Service breakdown
    print(f"\n🔧 SERVICE BREAKDOWN:")
    for service_name, stats in report['service_breakdown'].items():
        print(f"   {service_name}:")
        print(f"     Events: {stats['total_events']} | Success: {stats['successful_events']}")
        print(f"     Downtime: {stats['total_downtime']:.1f}s | Avg Impact: {stats['avg_impact_score']:.1f}")
    
    print(f"\n🎉 Chaos Monkey demonstration completed!")
    print(f"   Report saved at: chaos_report_{int(time.time())}.json")
    
    # Save report to file
    report_filename = f"chaos_report_{int(time.time())}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
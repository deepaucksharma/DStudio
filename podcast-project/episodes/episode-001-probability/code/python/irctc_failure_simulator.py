#!/usr/bin/env python3
"""
IRCTC Tatkal Booking Failure Probability Simulator
स्वतंत्रता दिवस पर IRCTC के टिकट बुकिंग failure का probability calculator

Indian Context: IRCTC पर तत्काल टिकट बुकिंग के दौरान server failure patterns का analysis
Mumbai Example: 15 अगस्त को Mumbai से Delhi के लिए Rajdhani Express का ticket book करना
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class IRCTCFailureSimulator:
    def __init__(self):
        # IRCTC server configurations - real भारतीय context
        self.peak_hours = [(9, 11), (21, 23)]  # Morning और evening rush
        self.tatkal_timing = [(10, 0), (11, 0)]  # AC और Non-AC Tatkal timings
        self.server_capacity = 100000  # Concurrent users
        self.database_timeout = 5.0  # seconds
        
        # Failure probabilities (real IRCTC statistics से inspired)
        self.base_failure_rate = 0.05  # 5% normal failure rate
        self.peak_multiplier = 3.0     # Peak hours में 3x failure
        self.tatkal_multiplier = 5.0   # Tatkal time में 5x failure
        
        # Popular routes और उनके load patterns
        self.popular_routes = {
            "MUMBAI_DELHI": {"base_load": 0.8, "festival_multiplier": 2.0},
            "DELHI_MUMBAI": {"base_load": 0.8, "festival_multiplier": 2.0},
            "KOLKATA_DELHI": {"base_load": 0.6, "festival_multiplier": 1.8},
            "CHENNAI_BANGALORE": {"base_load": 0.7, "festival_multiplier": 1.5},
            "PUNE_MUMBAI": {"base_load": 0.5, "festival_multiplier": 1.3}
        }
        
        # Festival seasons जब traffic बहुत high होता है
        self.festival_periods = [
            "DIWALI", "HOLI", "EID", "DUSSEHRA", "INDEPENDENCE_DAY"
        ]

    def calculate_failure_probability(self, 
                                    current_time: datetime,
                                    route: str,
                                    user_count: int,
                                    is_festival: bool = False,
                                    is_tatkal: bool = False) -> float:
        """
        IRCTC booking failure probability calculator
        
        Formula: P(failure) = base_rate × peak_factor × load_factor × festival_factor × tatkal_factor
        """
        hour = current_time.hour
        minute = current_time.minute
        
        # Base failure probability
        failure_prob = self.base_failure_rate
        
        # Peak hours effect - Mumbai local trains की तरह rush hours में problem
        is_peak = any(start <= hour <= end for start, end in self.peak_hours)
        if is_peak:
            failure_prob *= self.peak_multiplier
            
        # Tatkal timing effect - 10 AM और 11 AM का disaster
        is_tatkal_time = any(
            hour == tatkal_hour and minute == tatkal_minute 
            for tatkal_hour, tatkal_minute in self.tatkal_timing
        )
        if is_tatkal or is_tatkal_time:
            failure_prob *= self.tatkal_multiplier
            
        # Server load effect
        load_factor = min(user_count / self.server_capacity, 2.0)  # Max 2x
        failure_prob *= (1 + load_factor)
        
        # Route popularity effect
        if route in self.popular_routes:
            route_load = self.popular_routes[route]["base_load"]
            failure_prob *= (1 + route_load)
            
            # Festival effect - Independence Day पर extra traffic
            if is_festival:
                festival_multiplier = self.popular_routes[route]["festival_multiplier"]
                failure_prob *= festival_multiplier
        
        # Maximum probability cap at 95%
        return min(failure_prob, 0.95)

    def simulate_booking_attempt(self, 
                                route: str, 
                                user_count: int,
                                is_festival: bool = False,
                                is_tatkal: bool = False) -> Dict:
        """
        Single booking attempt simulation
        Real IRCTC experience को simulate करता है
        """
        current_time = datetime.now()
        
        # Failure probability calculate करें
        failure_prob = self.calculate_failure_probability(
            current_time, route, user_count, is_festival, is_tatkal
        )
        
        # Random failure simulation
        booking_failed = random.random() < failure_prob
        
        # Response time simulation - failure के साथ timeout भी आता है
        if booking_failed:
            response_time = random.uniform(self.database_timeout, 30.0)  # Timeout
            error_type = self.get_irctc_error_type(failure_prob)
        else:
            response_time = random.uniform(0.5, 3.0)  # Normal response
            error_type = None
            
        return {
            "timestamp": current_time.isoformat(),
            "route": route,
            "user_count": user_count,
            "failure_probability": failure_prob,
            "booking_failed": booking_failed,
            "response_time": response_time,
            "error_type": error_type,
            "is_festival": is_festival,
            "is_tatkal": is_tatkal
        }

    def get_irctc_error_type(self, failure_prob: float) -> str:
        """
        IRCTC के real error messages simulate करता है
        """
        if failure_prob > 0.7:
            return random.choice([
                "TECHNICAL_DIFFICULTY",
                "SERVER_BUSY",
                "NETWORK_CONNECTIVITY_ERROR",
                "SERVICE_UNAVAILABLE"
            ])
        elif failure_prob > 0.4:
            return random.choice([
                "TIMEOUT_ERROR", 
                "DATABASE_CONNECTION_FAILED",
                "PAYMENT_GATEWAY_ERROR"
            ])
        else:
            return random.choice([
                "SESSION_EXPIRED",
                "CAPTCHA_ERROR", 
                "USER_AUTHENTICATION_FAILED"
            ])

    def monte_carlo_simulation(self, 
                              route: str,
                              simulation_count: int = 10000,
                              user_range: Tuple[int, int] = (50000, 150000),
                              festival_probability: float = 0.1,
                              tatkal_probability: float = 0.3) -> Dict:
        """
        Monte Carlo simulation for IRCTC booking success rate
        बड़े scale पर probability patterns को analyze करता है
        """
        print(f"🚂 शुरू कर रहे हैं {simulation_count} IRCTC booking simulations...")
        print(f"📍 Route: {route}")
        print(f"👥 User range: {user_range[0]:,} to {user_range[1]:,}")
        
        results = []
        success_count = 0
        total_response_time = 0
        error_distribution = {}
        
        for i in range(simulation_count):
            # Random parameters generate करें
            user_count = random.randint(*user_range)
            is_festival = random.random() < festival_probability
            is_tatkal = random.random() < tatkal_probability
            
            # Simulation run करें
            result = self.simulate_booking_attempt(
                route, user_count, is_festival, is_tatkal
            )
            
            results.append(result)
            
            # Statistics collect करें
            if not result["booking_failed"]:
                success_count += 1
                
            total_response_time += result["response_time"]
            
            if result["error_type"]:
                error_distribution[result["error_type"]] = \
                    error_distribution.get(result["error_type"], 0) + 1
            
            # Progress indicator
            if (i + 1) % 1000 == 0:
                print(f"✅ Completed {i + 1:,} simulations...")
        
        # Final statistics
        success_rate = success_count / simulation_count
        avg_response_time = total_response_time / simulation_count
        
        return {
            "simulation_stats": {
                "total_simulations": simulation_count,
                "success_rate": success_rate,
                "failure_rate": 1 - success_rate,
                "avg_response_time": avg_response_time
            },
            "error_distribution": error_distribution,
            "route": route,
            "detailed_results": results[-100:]  # Last 100 results for analysis
        }

def main():
    """
    Main simulation runner - Independence Day IRCTC booking का example
    """
    print("🇮🇳 IRCTC Independence Day Booking Failure Analysis")
    print("=" * 60)
    
    simulator = IRCTCFailureSimulator()
    
    # Independence Day Mumbai to Delhi booking simulation
    print("\n🎯 Scenario: 15 अगस्त को Mumbai-Delhi Rajdhani booking")
    
    result = simulator.monte_carlo_simulation(
        route="MUMBAI_DELHI",
        simulation_count=10000,
        user_range=(80000, 200000),  # Heavy traffic
        festival_probability=0.8,    # High festival traffic
        tatkal_probability=0.6       # Many tatkal attempts
    )
    
    # Results display करें
    stats = result["simulation_stats"]
    print(f"\n📊 Simulation Results:")
    print(f"✅ Success Rate: {stats['success_rate']:.2%}")
    print(f"❌ Failure Rate: {stats['failure_rate']:.2%}")
    print(f"⏱️  Average Response Time: {stats['avg_response_time']:.2f} seconds")
    
    print(f"\n🚨 Error Distribution:")
    for error_type, count in result["error_distribution"].items():
        percentage = (count / stats['total_simulations']) * 100
        print(f"   {error_type}: {count:,} ({percentage:.1f}%)")
    
    # Peak hour analysis
    print(f"\n🕐 Peak Hour Analysis:")
    peak_failures = 0
    tatkal_failures = 0
    
    for booking in result["detailed_results"]:
        if booking["booking_failed"]:
            booking_time = datetime.fromisoformat(booking["timestamp"])
            hour = booking_time.hour
            
            if 9 <= hour <= 11 or 21 <= hour <= 23:
                peak_failures += 1
            if booking["is_tatkal"]:
                tatkal_failures += 1
    
    peak_failure_rate = peak_failures / len(result["detailed_results"])
    tatkal_failure_rate = tatkal_failures / len(result["detailed_results"])
    
    print(f"   Peak Hours Failure Rate: {peak_failure_rate:.2%}")
    print(f"   Tatkal Booking Failure Rate: {tatkal_failure_rate:.2%}")
    
    # Mumbai train analogy
    print(f"\n🚇 Mumbai Local Train Analogy:")
    print(f"   IRCTC booking success ≈ Mumbai local train में seat मिलना")
    print(f"   Peak hours = Rush hours (9-11 AM, 9-11 PM)")
    print(f"   Tatkal timing = Virar fast train का timing (limited seats)")
    print(f"   Festival traffic = Ganpati visarjan के दिन की crowd")
    
    # Business impact
    revenue_loss = stats['failure_rate'] * 100000 * 1500  # 1L users, ₹1500 avg ticket
    print(f"\n💰 Business Impact:")
    print(f"   Estimated daily revenue loss: ₹{revenue_loss:,.0f}")
    print(f"   User frustration index: {stats['failure_rate'] * 10:.1f}/10")

if __name__ == "__main__":
    main()
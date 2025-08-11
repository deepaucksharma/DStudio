#!/usr/bin/env python3
"""
Kingman Formula Calculator - Episode 2
किंगमैन फार्मूला कैलकुलेटर

Heavy traffic approximation calculator for queue systems using Kingman's formula
Kingman के फार्मूले का उपयोग करके queue systems के लिए heavy traffic approximation calculator

Mumbai traffic जैसे heavy load conditions में queue behavior predict करने के लिए!

Author: Code Developer Agent A5-C-002  
Indian Context: Mumbai traffic modeling, IRCTC heavy load, festival booking predictions
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

@dataclass
class QueueParameters:
    """Queue system parameters - Queue system के parameters"""
    arrival_rate: float      # λ (lambda) - arrivals per second
    service_rate: float      # μ (mu) - services per second  
    num_servers: int = 1     # c - number of servers
    arrival_variance: float = None    # Variance in arrival process
    service_variance: float = None    # Variance in service time
    
    def __post_init__(self):
        if self.arrival_variance is None:
            # Default to Poisson arrival (variance = mean)
            self.arrival_variance = self.arrival_rate
        if self.service_variance is None:
            # Default to exponential service (variance = mean²)
            self.service_variance = (1/self.service_rate)**2

@dataclass
class QueueResults:
    """Queue analysis results - Queue विश्लेषण परिणाम"""
    utilization: float           # ρ - system utilization
    avg_queue_length: float      # L - average number in system
    avg_wait_time: float         # W - average time in system
    avg_queue_wait: float        # Wq - average waiting time in queue
    avg_queue_size: float        # Lq - average number waiting in queue
    
    # Kingman's approximation specific
    kingman_wait_time: float     # Kingman's formula result
    kingman_queue_length: float  # Using Little's law with Kingman
    
    # Accuracy and confidence
    approximation_accuracy: str  # "High", "Medium", "Low"
    traffic_intensity: float     # ρ = λ/μ
    
    # Indian context insights
    mumbai_analogy: str = ""
    irctc_analogy: str = ""

class KingmanFormulaCalculator:
    """Calculator for Kingman's heavy traffic approximation - Kingman के heavy traffic approximation के लिए calculator"""
    
    def __init__(self):
        self.results_history: List[QueueResults] = []
        
        # Indian context mappings
        self.mumbai_traffic_analogies = {
            (0.0, 0.5): "सुबह के समय - कम ट्रैफिक, smooth flow",
            (0.5, 0.7): "दिन का समय - moderate traffic, occasional delays", 
            (0.7, 0.85): "शाम का peak hour - heavy traffic, longer waits",
            (0.85, 0.95): "रश hour में फंसे - बहुत heavy traffic, significant delays",
            (0.95, 1.0): "Complete jam - standstill traffic, extreme delays"
        }
        
        self.irctc_analogies = {
            (0.0, 0.5): "Normal booking - quick response, no queue",
            (0.5, 0.7): "Busy period - slight delays, manageable queue",
            (0.7, 0.85): "Festival season - heavy load, noticeable waits",
            (0.85, 0.95): "Tatkal booking rush - extreme load, long waits", 
            (0.95, 1.0): "Server overload - system struggling, very long queues"
        }
    
    def calculate_exact_mm1(self, params: QueueParameters) -> QueueResults:
        """Calculate exact M/M/1 results for comparison - तुलना के लिए exact M/M/1 परिणाम"""
        
        if params.num_servers != 1:
            raise ValueError("M/M/1 formula only works for single server")
        
        rho = params.arrival_rate / params.service_rate
        
        if rho >= 1.0:
            raise ValueError(f"System unstable: ρ = {rho:.3f} >= 1.0")
        
        # Standard M/M/1 formulas
        avg_queue_length = rho / (1 - rho)  # L
        avg_wait_time = avg_queue_length / params.arrival_rate  # W (Little's Law)
        avg_queue_size = (rho**2) / (1 - rho)  # Lq
        avg_queue_wait = avg_queue_size / params.arrival_rate  # Wq
        
        return QueueResults(
            utilization=rho,
            avg_queue_length=avg_queue_length,
            avg_wait_time=avg_wait_time,
            avg_queue_wait=avg_queue_wait,
            avg_queue_size=avg_queue_size,
            kingman_wait_time=avg_queue_wait,  # Same as exact for M/M/1
            kingman_queue_length=avg_queue_size,
            approximation_accuracy="Exact",
            traffic_intensity=rho,
            mumbai_analogy=self._get_mumbai_analogy(rho),
            irctc_analogy=self._get_irctc_analogy(rho)
        )
    
    def calculate_kingman_approximation(self, params: QueueParameters) -> QueueResults:
        """Calculate using Kingman's heavy traffic approximation - Kingman के heavy traffic approximation का उपयोग करके गणना"""
        
        lambda_rate = params.arrival_rate
        mu_rate = params.service_rate
        c = params.num_servers
        
        # Traffic intensity
        rho = lambda_rate / (c * mu_rate)
        
        if rho >= 1.0:
            raise ValueError(f"System unstable: ρ = {rho:.3f} >= 1.0")
        
        # Coefficient of variation for arrival and service processes
        ca_squared = params.arrival_variance / (lambda_rate**2)  # CV² for arrivals
        cs_squared = params.service_variance * (mu_rate**2)      # CV² for service times
        
        # Kingman's formula for average waiting time in queue
        # Wq ≈ (ca² + cs²)/2 × ρ/(1-ρ) × 1/μ
        kingman_queue_wait = ((ca_squared + cs_squared) / 2) * (rho / (1 - rho)) * (1 / mu_rate)
        
        # For multi-server systems, apply correction factor
        if c > 1:
            # Approximation for multi-server case
            correction_factor = self._multi_server_correction(c, rho)
            kingman_queue_wait *= correction_factor
        
        # Using Little's Law to get other metrics
        kingman_queue_length = lambda_rate * kingman_queue_wait  # Lq = λ × Wq
        avg_wait_time = kingman_queue_wait + (1 / mu_rate)       # W = Wq + 1/μ
        avg_queue_length = lambda_rate * avg_wait_time           # L = λ × W
        
        # Assess approximation accuracy
        accuracy = self._assess_accuracy(rho, ca_squared, cs_squared)
        
        results = QueueResults(
            utilization=rho,
            avg_queue_length=avg_queue_length,
            avg_wait_time=avg_wait_time,
            avg_queue_wait=kingman_queue_wait,
            avg_queue_size=kingman_queue_length,
            kingman_wait_time=kingman_queue_wait,
            kingman_queue_length=kingman_queue_length,
            approximation_accuracy=accuracy,
            traffic_intensity=rho,
            mumbai_analogy=self._get_mumbai_analogy(rho),
            irctc_analogy=self._get_irctc_analogy(rho)
        )
        
        self.results_history.append(results)
        return results
    
    def _multi_server_correction(self, c: int, rho: float) -> float:
        """Multi-server correction factor for Kingman's formula - Kingman के फार्मूले के लिए multi-server correction factor"""
        
        # Approximate correction based on Erlang-C formula influence
        # More servers reduce waiting time
        if c == 1:
            return 1.0
        elif c == 2:
            return 0.7  # Roughly 30% reduction with 2 servers
        elif c <= 4:
            return 0.5  # 50% reduction for 3-4 servers
        else:
            return 0.3  # 70% reduction for 5+ servers
    
    def _assess_accuracy(self, rho: float, ca_squared: float, cs_squared: float) -> str:
        """Assess accuracy of Kingman's approximation - Kingman के approximation की सटीकता का आकलन"""
        
        # Kingman's formula is most accurate under heavy traffic (ρ → 1)
        # and when coefficient of variation is not too extreme
        
        if rho > 0.9:
            if 0.5 <= ca_squared <= 2.0 and 0.5 <= cs_squared <= 2.0:
                return "High"
            else:
                return "Medium"
        elif rho > 0.7:
            return "Medium"
        else:
            return "Low"
    
    def _get_mumbai_analogy(self, rho: float) -> str:
        """Get Mumbai traffic analogy - Mumbai traffic की सादृश्यता प्राप्त करें"""
        for (low, high), analogy in self.mumbai_traffic_analogies.items():
            if low <= rho < high:
                return analogy
        return "Extreme traffic conditions"
    
    def _get_irctc_analogy(self, rho: float) -> str:
        """Get IRCTC analogy - IRCTC की सादृश्यता प्राप्त करें"""
        for (low, high), analogy in self.irctc_analogies.items():
            if low <= rho < high:
                return analogy
        return "System overload conditions"
    
    def compare_scenarios(self, scenarios: List[Tuple[str, QueueParameters]]) -> Dict[str, QueueResults]:
        """Compare multiple queue scenarios - कई queue scenarios की तुलना करें"""
        
        results = {}
        
        print("🔍 SCENARIO COMPARISON | स्थिति तुलना")
        print("="*60)
        
        for name, params in scenarios:
            try:
                result = self.calculate_kingman_approximation(params)
                results[name] = result
                
                print(f"\n📊 {name}")
                print(f"   Traffic Intensity (ρ): {result.traffic_intensity:.3f}")
                print(f"   Average Queue Wait: {result.avg_queue_wait:.2f}s")
                print(f"   Average Queue Length: {result.avg_queue_size:.1f} items")
                print(f"   Approximation Accuracy: {result.approximation_accuracy}")
                print(f"   Mumbai Analogy: {result.mumbai_analogy}")
                print(f"   IRCTC Analogy: {result.irctc_analogy}")
                
            except ValueError as e:
                print(f"\n❌ {name}: {e}")
                results[name] = None
        
        return results
    
    def sensitivity_analysis(self, base_params: QueueParameters, 
                           parameter_ranges: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """Perform sensitivity analysis - संवेदनशीलता विश्लेषण करें"""
        
        print(f"\n🔬 SENSITIVITY ANALYSIS | संवेदनशीलता विश्लेषण")
        print("="*50)
        
        results = {}
        
        for param_name, values in parameter_ranges.items():
            wait_times = []
            queue_lengths = []
            utilizations = []
            
            for value in values:
                # Create modified parameters
                modified_params = QueueParameters(
                    arrival_rate=base_params.arrival_rate,
                    service_rate=base_params.service_rate, 
                    num_servers=base_params.num_servers,
                    arrival_variance=base_params.arrival_variance,
                    service_variance=base_params.service_variance
                )
                
                # Modify the specific parameter
                if param_name == 'arrival_rate':
                    modified_params.arrival_rate = value
                elif param_name == 'service_rate':
                    modified_params.service_rate = value
                elif param_name == 'num_servers':
                    modified_params.num_servers = int(value)
                
                try:
                    result = self.calculate_kingman_approximation(modified_params)
                    wait_times.append(result.avg_queue_wait)
                    queue_lengths.append(result.avg_queue_size)
                    utilizations.append(result.utilization)
                except ValueError:
                    wait_times.append(float('inf'))
                    queue_lengths.append(float('inf'))
                    utilizations.append(1.0)
            
            results[param_name] = {
                'values': values,
                'wait_times': wait_times,
                'queue_lengths': queue_lengths,
                'utilizations': utilizations
            }
            
            print(f"\n{param_name.title()} Sensitivity:")
            for i, value in enumerate(values):
                if wait_times[i] != float('inf'):
                    print(f"   {value}: Wait={wait_times[i]:.2f}s, Queue={queue_lengths[i]:.1f}, ρ={utilizations[i]:.3f}")
                else:
                    print(f"   {value}: UNSTABLE SYSTEM")
        
        return results
    
    def create_indian_scenarios(self) -> List[Tuple[str, QueueParameters]]:
        """Create realistic Indian service scenarios - वास्तविक भारतीय सेवा scenarios बनाएं"""
        
        scenarios = [
            # IRCTC Normal Day
            ("IRCTC Normal Day", QueueParameters(
                arrival_rate=50.0,    # 50 bookings/sec
                service_rate=60.0,    # 60 bookings processed/sec
                num_servers=1,
                arrival_variance=50.0,      # Poisson arrivals
                service_variance=1/60.0**2  # Exponential service
            )),
            
            # IRCTC Tatkal Rush
            ("IRCTC Tatkal Rush (10 AM)", QueueParameters(
                arrival_rate=200.0,   # 200 bookings/sec (4x normal)
                service_rate=180.0,   # Slightly slower due to load
                num_servers=2,        # Scale to 2 servers
                arrival_variance=400.0,     # Higher variance during rush
                service_variance=1/180.0**2
            )),
            
            # Mumbai Food Delivery Evening Peak
            ("Zomato Mumbai Evening Rush", QueueParameters(
                arrival_rate=150.0,   # 150 orders/sec
                service_rate=160.0,   # 160 orders processed/sec
                num_servers=3,        # 3 parallel processing units
                arrival_variance=200.0,     # Variable order timing
                service_variance=1/160.0**2
            )),
            
            # Flipkart Flash Sale
            ("Flipkart Flash Sale", QueueParameters(
                arrival_rate=500.0,   # 500 purchases/sec
                service_rate=450.0,   # System struggles at this scale
                num_servers=5,        # 5 servers to handle load
                arrival_variance=1000.0,    # Very bursty arrivals
                service_variance=1/450.0**2
            )),
            
            # Paytm UPI Peak Hour
            ("Paytm UPI Evening Peak", QueueParameters(
                arrival_rate=300.0,   # 300 transactions/sec
                service_rate=350.0,   # 350 transactions/sec capacity
                num_servers=2,        # 2 payment processing servers
                arrival_variance=350.0,
                service_variance=1/350.0**2
            )),
            
            # Mumbai Local Train Ticket Counter
            ("Mumbai Local Ticket Counter", QueueParameters(
                arrival_rate=80.0,    # 80 people/minute = 1.33/sec
                service_rate=1.5,     # 1.5 people served/sec
                num_servers=4,        # 4 ticket counters
                arrival_variance=100.0,
                service_variance=1/1.5**2
            ))
        ]
        
        return scenarios
    
    def generate_visualization(self, results: Dict[str, QueueResults], filename: str = "kingman_analysis.png"):
        """Generate visualization of Kingman analysis - Kingman विश्लेषण की visualization बनाएं"""
        
        if not results:
            return
        
        # Filter out failed results
        valid_results = {name: result for name, result in results.items() if result is not None}
        
        if not valid_results:
            return
        
        names = list(valid_results.keys())
        wait_times = [result.avg_queue_wait for result in valid_results.values()]
        queue_lengths = [result.avg_queue_size for result in valid_results.values()]
        utilizations = [result.utilization for result in valid_results.values()]
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Kingman Formula Analysis - Indian Service Scenarios\nKingman फार्मूला विश्लेषण - भारतीय सेवा स्थितियां', fontsize=16)
        
        # Average Queue Wait Time
        bars1 = ax1.bar(range(len(names)), wait_times, color=['red' if w > 5 else 'orange' if w > 2 else 'green' for w in wait_times])
        ax1.set_title('Average Queue Wait Time (seconds)\nऔसत Queue प्रतीक्षा समय (सेकंड)')
        ax1.set_xlabel('Scenarios | स्थितियां')
        ax1.set_ylabel('Wait Time (seconds) | प्रतीक्षा समय (सेकंड)')
        ax1.set_xticks(range(len(names)))
        ax1.set_xticklabels(names, rotation=45, ha='right')
        
        # Add value labels on bars
        for i, bar in enumerate(bars1):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{height:.1f}s', 
                    ha='center', va='bottom', fontsize=8)
        
        # Average Queue Length
        bars2 = ax2.bar(range(len(names)), queue_lengths, color=['red' if q > 10 else 'orange' if q > 5 else 'green' for q in queue_lengths])
        ax2.set_title('Average Queue Length\nऔसत Queue लंबाई')
        ax2.set_xlabel('Scenarios | स्थितियां')
        ax2.set_ylabel('Queue Length | Queue लंबाई')
        ax2.set_xticks(range(len(names)))
        ax2.set_xticklabels(names, rotation=45, ha='right')
        
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{height:.1f}', 
                    ha='center', va='bottom', fontsize=8)
        
        # System Utilization
        bars3 = ax3.bar(range(len(names)), utilizations, color=['red' if u > 0.9 else 'orange' if u > 0.7 else 'green' for u in utilizations])
        ax3.set_title('System Utilization (ρ)\nसिस्टम उपयोग (ρ)')
        ax3.set_xlabel('Scenarios | स्थितियां')
        ax3.set_ylabel('Utilization | उपयोग')
        ax3.set_xticks(range(len(names)))
        ax3.set_xticklabels(names, rotation=45, ha='right')
        ax3.axhline(y=0.8, color='orange', linestyle='--', alpha=0.7, label='80% threshold')
        ax3.axhline(y=0.9, color='red', linestyle='--', alpha=0.7, label='90% critical')
        ax3.legend()
        
        for i, bar in enumerate(bars3):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01, f'{height:.3f}', 
                    ha='center', va='bottom', fontsize=8)
        
        # Traffic Intensity vs Wait Time relationship
        rho_values = np.linspace(0.1, 0.95, 50)
        theoretical_waits = rho_values / (1 - rho_values)  # Simplified M/M/1 relationship
        
        ax4.plot(rho_values, theoretical_waits, 'b-', linewidth=2, label='Theoretical M/M/1', alpha=0.7)
        
        # Plot actual results
        actual_rhos = [result.utilization for result in valid_results.values()]
        actual_waits_normalized = [result.avg_queue_wait * result.utilization for result in valid_results.values()]  # Normalize for comparison
        
        ax4.scatter(actual_rhos, actual_waits_normalized, color='red', s=100, alpha=0.8, label='Indian Scenarios', zorder=5)
        
        # Annotate points
        for i, name in enumerate(names):
            ax4.annotate(name[:15] + '...', (actual_rhos[i], actual_waits_normalized[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8, alpha=0.8)
        
        ax4.set_title('Traffic Intensity vs Normalized Wait Time\nट्रैफिक तीव्रता बनाम Normalized प्रतीक्षा समय')
        ax4.set_xlabel('Traffic Intensity (ρ) | ट्रैफिक तीव्रता (ρ)')
        ax4.set_ylabel('Normalized Wait | Normalized प्रतीक्षा')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 Visualization saved: {filename}")
        
        return fig

def main():
    """Main function to demonstrate Kingman formula calculator - मुख्य function"""
    
    print("📊 Kingman Formula Calculator Demo - Episode 2")
    print("Kingman फार्मूला कैलकुलेटर डेमो - एपिसोड 2\n")
    
    calculator = KingmanFormulaCalculator()
    
    # Create Indian service scenarios
    scenarios = calculator.create_indian_scenarios()
    
    print(f"Created {len(scenarios)} Indian service scenarios:")
    for i, (name, params) in enumerate(scenarios, 1):
        print(f"  {i}. {name}")
        print(f"     Arrival Rate: {params.arrival_rate}/sec, Service Rate: {params.service_rate}/sec")
        print(f"     Servers: {params.num_servers}, Traffic Intensity: {params.arrival_rate/(params.num_servers * params.service_rate):.3f}")
    
    # Analyze all scenarios
    print(f"\n{'='*80}")
    print("KINGMAN FORMULA ANALYSIS | KINGMAN फार्मूला विश्लेषण")
    print('='*80)
    
    results = calculator.compare_scenarios(scenarios)
    
    # Detailed analysis of interesting cases
    print(f"\n{'='*80}")
    print("DETAILED INSIGHTS | विस्तृत अंतर्दृष्टि")
    print('='*80)
    
    # Find most congested scenario
    valid_results = {name: result for name, result in results.items() if result is not None}
    if valid_results:
        most_congested = max(valid_results.items(), key=lambda x: x[1].utilization)
        fastest_service = min(valid_results.items(), key=lambda x: x[1].avg_queue_wait)
        
        print(f"\n🚨 MOST CONGESTED SCENARIO:")
        print(f"   {most_congested[0]}")
        print(f"   Utilization: {most_congested[1].utilization:.1%}")
        print(f"   Wait Time: {most_congested[1].avg_queue_wait:.2f} seconds")
        print(f"   Mumbai Analogy: {most_congested[1].mumbai_analogy}")
        
        print(f"\n⚡ FASTEST SERVICE SCENARIO:")
        print(f"   {fastest_service[0]}")
        print(f"   Wait Time: {fastest_service[1].avg_queue_wait:.2f} seconds")
        print(f"   Queue Length: {fastest_service[1].avg_queue_size:.1f} items")
        print(f"   IRCTC Analogy: {fastest_service[1].irctc_analogy}")
    
    # Sensitivity analysis
    base_params = QueueParameters(
        arrival_rate=100.0,
        service_rate=120.0,
        num_servers=1
    )
    
    sensitivity_ranges = {
        'arrival_rate': [80, 90, 100, 110, 115, 118],
        'service_rate': [100, 110, 120, 130, 140, 150],
        'num_servers': [1, 2, 3, 4]
    }
    
    sensitivity_results = calculator.sensitivity_analysis(base_params, sensitivity_ranges)
    
    # Generate visualization
    print(f"\n{'='*80}")
    print("GENERATING VISUALIZATION | VISUALIZATION जेनरेट करना")
    print('='*80)
    
    calculator.generate_visualization(results, "kingman_indian_scenarios.png")
    
    # Export results to JSON
    export_data = {
        'analysis_timestamp': str(datetime.now()),
        'scenarios': {},
        'insights': {
            'most_congested': most_congested[0] if valid_results else None,
            'fastest_service': fastest_service[0] if valid_results else None,
            'total_scenarios_analyzed': len(scenarios),
            'successful_analyses': len(valid_results)
        }
    }
    
    for name, result in results.items():
        if result:
            export_data['scenarios'][name] = {
                'utilization': result.utilization,
                'avg_queue_wait_seconds': result.avg_queue_wait,
                'avg_queue_length': result.avg_queue_size,
                'approximation_accuracy': result.approximation_accuracy,
                'mumbai_analogy': result.mumbai_analogy,
                'irctc_analogy': result.irctc_analogy
            }
    
    with open('kingman_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print("📁 Results exported to: kingman_analysis_results.json")
    
    # Performance optimization recommendations
    print(f"\n{'='*80}")
    print("PERFORMANCE OPTIMIZATION RECOMMENDATIONS")
    print("प्रदर्शन अनुकूलन सिफारिशें")
    print('='*80)
    
    print("\nBased on Kingman's formula analysis:")
    print("Kingman के फार्मूला विश्लेषण के आधार पर:")
    
    recommendations = [
        "1. Keep traffic intensity (ρ) below 80% for stable performance",
        "   स्थिर प्रदर्शन के लिए traffic intensity को 80% से नीचे रखें",
        
        "2. Add servers when approaching 85% utilization",
        "   85% utilization के पास पहुंचने पर servers जोड़ें",
        
        "3. During peak events (Tatkal, Flash Sales), pre-scale capacity",
        "   Peak events के दौरान capacity को पहले से scale करें",
        
        "4. Monitor variance in arrival patterns - high variance increases wait times",
        "   Arrival patterns में variance की निगरानी करें - उच्च variance wait times बढ़ाता है",
        
        "5. Optimize service times - even small improvements have large impact at high utilization",
        "   Service times को optimize करें - छोटे सुधार भी high utilization पर बड़ा प्रभाव डालते हैं"
    ]
    
    for rec in recommendations:
        print(f"   {rec}")
    
    print(f"\n🎉 Kingman Formula Calculator demonstration completed!")
    print("Kingman फार्मूला कैलकुलेटर प्रदर्शन पूर्ण!")
    
    print(f"\n💡 KEY LEARNINGS | मुख्य शिक्षाएं:")
    print("1. Heavy traffic makes small changes have big impact")
    print("   Heavy traffic में छोटे changes का बड़ा impact होता है")
    print("2. Indian service patterns show extreme utilization during peak events")
    print("   भारतीय service patterns peak events के दौरान extreme utilization दिखाते हैं")
    print("3. Kingman's formula helps predict queue behavior under heavy load")
    print("   Kingman का formula heavy load में queue behavior predict करने में मदद करता है")

if __name__ == "__main__":
    main()
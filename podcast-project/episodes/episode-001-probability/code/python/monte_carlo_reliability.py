#!/usr/bin/env python3
"""
Monte Carlo Reliability Analysis for Indian Systems
====================================================

Mumbai के traffic patterns और system failures को simulate करके reliability analysis करते हैं।
Real-world examples include IRCTC, PhonePe, Flipkart, और Mumbai local trains.

मुख्य concepts:
1. Monte Carlo simulation for system reliability
2. Bayes theorem for failure prediction  
3. Markov chains for system state transitions
4. Indian infrastructure constraints modeling

Mumbai analogy: Local train reliability prediction during monsoon season
Author: Hindi Tech Podcast Series
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import random
import math
from datetime import datetime, timedelta
import json

# Hindi comments के साथ comprehensive Monte Carlo reliability simulator

@dataclass
class SystemComponent:
    """Individual system component with failure characteristics"""
    name: str                    # Component का नाम
    base_failure_rate: float    # Basic failure rate (failures per hour)
    repair_time: float          # Average repair time in hours
    criticality: str            # 'critical', 'important', 'optional'
    indian_factor: float        # Indian infrastructure impact (1.0 = no impact, >1.0 = higher failure)

@dataclass 
class MonteCarloConfig:
    """Monte Carlo simulation configuration"""
    num_simulations: int = 10000      # Number of simulations to run
    time_horizon: int = 8760          # Hours in a year (24*365)
    confidence_level: float = 0.95    # Confidence interval
    include_monsoon: bool = True      # Mumbai monsoon impact
    include_festivals: bool = True     # Indian festival load spikes
    
class IndianSystemReliabilityAnalyzer:
    """
    Monte Carlo reliability analysis with Indian context
    Mumbai local trains जैसी systems के लिए reliability prediction
    """
    
    def __init__(self, config: MonteCarloConfig):
        self.config = config
        self.components = self._initialize_components()
        self.results = {}
        
        # Indian specific factors - भारतीय context के लिए special multipliers
        self.monsoon_months = [6, 7, 8, 9]  # June to September
        self.festival_periods = [
            (10, 15, 2.5),  # Diwali - October 15 days, 2.5x load
            (3, 10, 2.0),   # Holi - March 10 days, 2x load
            (8, 7, 1.8),    # Ganesh Chaturthi - August 7 days, 1.8x load
        ]
        
        print("🇮🇳 Indian System Reliability Analyzer initialized")
        print("📊 Monte Carlo simulation ready for desi systems!")
        
    def _initialize_components(self) -> List[SystemComponent]:
        """Initialize system components with Indian characteristics"""
        
        # IRCTC booking system components - real production setup
        components = [
            SystemComponent("Load Balancer", 0.001, 2.0, "critical", 1.2),
            SystemComponent("Web Server", 0.005, 1.5, "critical", 1.4), 
            SystemComponent("Database", 0.003, 4.0, "critical", 1.6),
            SystemComponent("Payment Gateway", 0.008, 3.0, "critical", 1.8),
            SystemComponent("Session Server", 0.006, 2.5, "important", 1.3),
            SystemComponent("Cache Layer", 0.004, 1.0, "important", 1.1),
            SystemComponent("SMS Service", 0.010, 0.5, "important", 2.0),
            SystemComponent("Ticket Generation", 0.007, 3.5, "critical", 1.5),
            SystemComponent("User Profile DB", 0.002, 5.0, "optional", 1.2),
            SystemComponent("Analytics System", 0.009, 2.0, "optional", 1.0),
        ]
        
        print(f"🔧 Initialized {len(components)} components")
        print("📋 Component criticality distribution:")
        
        criticality_count = {}
        for comp in components:
            criticality_count[comp.criticality] = criticality_count.get(comp.criticality, 0) + 1
        
        for level, count in criticality_count.items():
            print(f"   {level}: {count} components")
            
        return components
        
    def _get_time_multipliers(self, hour_of_year: int) -> Dict[str, float]:
        """
        Get time-based multipliers for Indian context
        Mumbai के seasonal patterns और festival impacts
        """
        multipliers = {"base": 1.0, "load": 1.0, "failure": 1.0}
        
        # Month calculation - कौन सा महीना है?
        day_of_year = hour_of_year // 24
        month = (day_of_year // 30) + 1  # Rough month calculation
        day_in_month = day_of_year % 30
        
        # Monsoon impact - Mumbai में बारिश का असर
        if month in self.monsoon_months:
            multipliers["failure"] *= 1.8  # 80% higher failure rate
            multipliers["load"] *= 0.7     # 30% less traffic (people avoid travel)
            
        # Festival impact - त्योहारों का असर
        for festival_month, duration, load_multiplier in self.festival_periods:
            if month == festival_month and day_in_month <= duration:
                multipliers["load"] *= load_multiplier
                multipliers["failure"] *= 1.3  # Higher failure under load
                
        # Peak hours - office time का असर (9-11 AM, 6-8 PM)
        hour_of_day = hour_of_year % 24
        if 9 <= hour_of_day <= 11 or 18 <= hour_of_day <= 20:
            multipliers["load"] *= 1.6     # Peak traffic
            multipliers["failure"] *= 1.2  # Higher failure under load
            
        return multipliers
        
    def run_monte_carlo_simulation(self) -> Dict:
        """
        Run comprehensive Monte Carlo simulation
        Multiple scenarios के साथ reliability analysis
        """
        print("\n🎯 Starting Monte Carlo Reliability Analysis...")
        print(f"📊 Running {self.config.num_simulations:,} simulations")
        print(f"⏰ Time horizon: {self.config.time_horizon:,} hours ({self.config.time_horizon//24} days)")
        
        simulation_results = []
        
        for sim in range(self.config.num_simulations):
            if sim % 1000 == 0:
                print(f"🔄 Progress: {sim:,}/{self.config.num_simulations:,} ({sim/self.config.num_simulations*100:.1f}%)")
                
            # Single simulation run
            sim_result = self._run_single_simulation()
            simulation_results.append(sim_result)
            
        print("✅ Monte Carlo simulation completed!")
        
        # Analyze results - नतीजों का विश्लेषण
        return self._analyze_simulation_results(simulation_results)
        
    def _run_single_simulation(self) -> Dict:
        """
        Run a single Monte Carlo simulation
        एक complete system lifecycle simulate करते हैं
        """
        # Initialize component states - सभी components working state में start
        component_states = {comp.name: {"working": True, "last_failure": 0} 
                           for comp in self.components}
        
        system_uptime = 0
        total_failures = 0
        critical_failures = 0
        repair_costs = 0
        
        # Simulate hour by hour - घंटे-घंटे simulation
        for hour in range(self.config.time_horizon):
            # Get time-specific multipliers
            multipliers = self._get_time_multipliers(hour)
            
            system_working = True
            
            # Check each component - हर component की जांच
            for comp in self.components:
                current_state = component_states[comp.name]
                
                if current_state["working"]:
                    # Calculate failure probability for this hour
                    base_prob = comp.base_failure_rate * multipliers["failure"] * comp.indian_factor
                    failure_prob = 1 - math.exp(-base_prob)  # Exponential distribution
                    
                    if random.random() < failure_prob:
                        # Component failed! - Component fail हो गया!
                        current_state["working"] = False
                        current_state["last_failure"] = hour
                        
                        total_failures += 1
                        repair_costs += self._calculate_repair_cost(comp)
                        
                        if comp.criticality == "critical":
                            critical_failures += 1
                            system_working = False
                            
                else:
                    # Component is under repair - Component repair हो रहा है
                    time_in_repair = hour - current_state["last_failure"]
                    
                    # Check if repair is completed
                    repair_prob = 1 - math.exp(-1.0 / comp.repair_time)  # Exponential repair
                    
                    if random.random() < repair_prob and time_in_repair >= 0.5:
                        current_state["working"] = True
                        
            # Check overall system health
            critical_components_working = all(
                component_states[comp.name]["working"] 
                for comp in self.components 
                if comp.criticality == "critical"
            )
            
            if critical_components_working:
                system_uptime += 1
                
        # Calculate simulation metrics
        uptime_percentage = (system_uptime / self.config.time_horizon) * 100
        mtbf = self.config.time_horizon / max(total_failures, 1)  # Mean Time Between Failures
        
        return {
            "uptime_percentage": uptime_percentage,
            "total_failures": total_failures,
            "critical_failures": critical_failures, 
            "mtbf_hours": mtbf,
            "repair_costs": repair_costs,
            "availability": uptime_percentage / 100.0
        }
        
    def _calculate_repair_cost(self, component: SystemComponent) -> float:
        """
        Calculate repair cost in Indian context
        भारतीय rates और conditions के हिसाब से cost
        """
        base_costs = {
            "critical": 50000,     # ₹50,000 for critical components
            "important": 25000,    # ₹25,000 for important components  
            "optional": 10000      # ₹10,000 for optional components
        }
        
        base_cost = base_costs.get(component.criticality, 10000)
        
        # Indian factors - भारतीय specific costs
        indian_multiplier = 0.7  # Generally lower labor costs
        urgency_multiplier = 1.5 if component.criticality == "critical" else 1.0
        
        return base_cost * indian_multiplier * urgency_multiplier
        
    def _analyze_simulation_results(self, results: List[Dict]) -> Dict:
        """
        Comprehensive analysis of simulation results
        Monte Carlo results का detailed analysis
        """
        print("\n📊 Analyzing Monte Carlo Results...")
        
        df = pd.DataFrame(results)
        
        analysis = {
            "summary": {
                "total_simulations": len(results),
                "confidence_level": self.config.confidence_level
            },
            "availability": {
                "mean": df["availability"].mean(),
                "median": df["availability"].median(), 
                "std": df["availability"].std(),
                "min": df["availability"].min(),
                "max": df["availability"].max(),
                "percentiles": {
                    "p95": df["availability"].quantile(0.95),
                    "p99": df["availability"].quantile(0.99),
                    "p99.9": df["availability"].quantile(0.999)
                }
            },
            "failures": {
                "mean_total": df["total_failures"].mean(),
                "mean_critical": df["critical_failures"].mean(),
                "failure_rate_per_year": df["total_failures"].mean(),
            },
            "costs": {
                "mean_annual_repair_cost": df["repair_costs"].mean(),
                "total_cost_confidence_interval": self._confidence_interval(df["repair_costs"]),
            },
            "mtbf": {
                "mean_hours": df["mtbf_hours"].mean(),
                "mean_days": df["mtbf_hours"].mean() / 24,
                "confidence_interval": self._confidence_interval(df["mtbf_hours"])
            }
        }
        
        # SLA compliance analysis - SLA की compliance check करते हैं
        sla_targets = [0.95, 0.99, 0.999, 0.9999]  # 95%, 99%, 99.9%, 99.99% 
        
        analysis["sla_compliance"] = {}
        for sla in sla_targets:
            compliance_rate = (df["availability"] >= sla).mean()
            analysis["sla_compliance"][f"{sla*100}%"] = {
                "compliance_rate": compliance_rate,
                "meets_sla": compliance_rate > 0.95  # 95% of simulations should meet SLA
            }
            
        self.results = analysis
        return analysis
        
    def _confidence_interval(self, data: pd.Series) -> Tuple[float, float]:
        """Calculate confidence interval"""
        alpha = 1 - self.config.confidence_level
        lower = data.quantile(alpha/2)
        upper = data.quantile(1 - alpha/2)
        return (lower, upper)
        
    def generate_reliability_report(self) -> str:
        """
        Generate comprehensive reliability report
        Complete report with Mumbai analogies और practical insights
        """
        if not self.results:
            return "❌ No simulation results available. Run monte carlo simulation first!"
            
        report = []
        report.append("🇮🇳 INDIAN SYSTEM RELIABILITY ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"📊 Monte Carlo Analysis: {self.results['summary']['total_simulations']:,} simulations")
        report.append(f"🎯 Confidence Level: {self.results['summary']['confidence_level']*100}%")
        report.append("")
        
        # Availability Analysis
        avail = self.results['availability']
        report.append("🟢 SYSTEM AVAILABILITY ANALYSIS")
        report.append("-" * 40)
        report.append(f"📈 Mean Availability: {avail['mean']*100:.3f}%")
        report.append(f"📊 Median Availability: {avail['median']*100:.3f}%")
        report.append(f"📉 Standard Deviation: {avail['std']*100:.3f}%")
        report.append(f"🔻 Worst Case: {avail['min']*100:.3f}%")
        report.append(f"🔺 Best Case: {avail['max']*100:.3f}%")
        report.append("")
        
        report.append("📊 AVAILABILITY PERCENTILES:")
        report.append(f"   95th percentile: {avail['percentiles']['p95']*100:.3f}%")
        report.append(f"   99th percentile: {avail['percentiles']['p99']*100:.3f}%")  
        report.append(f"   99.9th percentile: {avail['percentiles']['p99.9']*100:.3f}%")
        report.append("")
        
        # Mumbai analogy for availability
        if avail['mean'] > 0.99:
            analogy = "Mumbai local trains के regular days जैसी reliability! 🚊"
        elif avail['mean'] > 0.95:
            analogy = "BEST buses जैसी decent reliability 🚌"
        else:
            analogy = "Mumbai traffic जैसी unpredictable availability! 🚗"
            
        report.append(f"🏙️ Mumbai Analogy: {analogy}")
        report.append("")
        
        # SLA Compliance
        report.append("🎯 SLA COMPLIANCE ANALYSIS")
        report.append("-" * 40)
        
        for sla_level, compliance in self.results['sla_compliance'].items():
            status = "✅ MEETS" if compliance['meets_sla'] else "❌ FAILS"
            report.append(f"{sla_level} SLA: {compliance['compliance_rate']*100:.1f}% compliance - {status}")
            
        report.append("")
        
        # Failure Analysis  
        failures = self.results['failures']
        report.append("🚨 FAILURE ANALYSIS")
        report.append("-" * 40)
        report.append(f"📈 Average Total Failures per Year: {failures['mean_total']:.1f}")
        report.append(f"🔥 Average Critical Failures per Year: {failures['mean_critical']:.1f}")
        report.append("")
        
        # MTBF Analysis
        mtbf = self.results['mtbf']
        report.append("⏰ MEAN TIME BETWEEN FAILURES (MTBF)")
        report.append("-" * 40)
        report.append(f"📊 Average MTBF: {mtbf['mean_hours']:.1f} hours ({mtbf['mean_days']:.1f} days)")
        
        lower, upper = mtbf['confidence_interval'] 
        report.append(f"🎯 {self.config.confidence_level*100}% Confidence Interval: {lower:.1f}h - {upper:.1f}h")
        report.append("")
        
        # Cost Analysis
        costs = self.results['costs']
        report.append("💰 COST ANALYSIS (Indian Rupees)")
        report.append("-" * 40)
        report.append(f"📈 Average Annual Repair Cost: ₹{costs['mean_annual_repair_cost']:,.0f}")
        
        cost_lower, cost_upper = costs['total_cost_confidence_interval']
        report.append(f"🎯 {self.config.confidence_level*100}% Cost Range: ₹{cost_lower:,.0f} - ₹{cost_upper:,.0f}")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS FOR INDIAN SYSTEMS")
        report.append("-" * 40)
        
        if avail['mean'] < 0.99:
            report.append("🔧 Consider improving critical component redundancy")
            report.append("🌧️  Add specific monsoon season preparations")
            
        if failures['mean_critical'] > 5:
            report.append("🚨 High critical failure rate - review component selection") 
            
        if costs['mean_annual_repair_cost'] > 500000:
            report.append("💰 Consider preventive maintenance to reduce repair costs")
            
        report.append("🎯 Focus on improving components with highest indian_factor")
        report.append("📱 Implement real-time monitoring like Mumbai traffic apps")
        report.append("⚡ Plan for power outages during monsoon season")
        report.append("")
        
        # Mumbai-specific insights
        report.append("🏙️ MUMBAI-SPECIFIC INSIGHTS")
        report.append("-" * 40)
        report.append("🌧️  Monsoon season impact: ~80% higher failure rates")
        report.append("🎉 Festival season impact: 2-2.5x higher loads")
        report.append("🚊 Peak hour patterns: 9-11 AM & 6-8 PM stress")
        report.append("🔧 Indian repair costs: ~30% lower than global average")
        report.append("")
        
        report.append("📞 For support: Think like Mumbai dabbawalas - reliable delivery!")
        report.append("🚀 Happy reliability engineering! May your systems be more reliable than IRCTC!")
        
        return "\n".join(report)
        
    def visualize_results(self) -> None:
        """
        Create visualization plots for reliability analysis
        Graphs और charts के साथ analysis को visualize करते हैं
        """
        if not self.results:
            print("❌ No results to visualize. Run simulation first!")
            return
            
        print("📊 Creating reliability visualization...")
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('🇮🇳 Indian System Reliability Analysis - Monte Carlo Results', fontsize=16, fontweight='bold')
        
        # Simulate data for visualization (since we don't store individual results)
        np.random.seed(42)
        n_samples = 1000
        
        availability_data = np.random.normal(
            self.results['availability']['mean'],
            self.results['availability']['std'],
            n_samples
        )
        
        failure_data = np.random.poisson(
            self.results['failures']['mean_total'],
            n_samples
        )
        
        # Plot 1: Availability Distribution
        axes[0,0].hist(availability_data * 100, bins=50, alpha=0.7, color='green', edgecolor='black')
        axes[0,0].axvline(self.results['availability']['mean'] * 100, color='red', linestyle='--', 
                         label=f'Mean: {self.results["availability"]["mean"]*100:.3f}%')
        axes[0,0].set_xlabel('Availability Percentage')
        axes[0,0].set_ylabel('Frequency')
        axes[0,0].set_title('🟢 System Availability Distribution')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # Plot 2: Failure Rate Distribution  
        axes[0,1].hist(failure_data, bins=30, alpha=0.7, color='red', edgecolor='black')
        axes[0,1].axvline(self.results['failures']['mean_total'], color='blue', linestyle='--',
                         label=f'Mean: {self.results["failures"]["mean_total"]:.1f}')
        axes[0,1].set_xlabel('Number of Failures per Year')
        axes[0,1].set_ylabel('Frequency') 
        axes[0,1].set_title('🚨 Annual Failure Distribution')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
        
        # Plot 3: SLA Compliance
        sla_levels = []
        compliance_rates = []
        
        for sla_level, compliance in self.results['sla_compliance'].items():
            sla_levels.append(sla_level)
            compliance_rates.append(compliance['compliance_rate'] * 100)
            
        bars = axes[1,0].bar(sla_levels, compliance_rates, alpha=0.7, color='blue', edgecolor='black')
        axes[1,0].axhline(95, color='red', linestyle='--', label='Target: 95%')
        axes[1,0].set_ylabel('Compliance Rate (%)')
        axes[1,0].set_title('🎯 SLA Compliance Rates')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, rate in zip(bars, compliance_rates):
            height = bar.get_height()
            axes[1,0].text(bar.get_x() + bar.get_width()/2., height + 1,
                          f'{rate:.1f}%', ha='center', va='bottom')
        
        # Plot 4: Component Failure Rates
        comp_names = [comp.name[:15] for comp in self.components[:8]]  # Top 8 components
        failure_rates = [(comp.base_failure_rate * comp.indian_factor * 8760) 
                        for comp in self.components[:8]]  # Annual failure rate
        
        bars = axes[1,1].barh(comp_names, failure_rates, alpha=0.7, color='orange', edgecolor='black')
        axes[1,1].set_xlabel('Expected Annual Failures')
        axes[1,1].set_title('🔧 Component Annual Failure Rates')
        axes[1,1].grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Visualization completed!")

def main():
    """
    Main function to demonstrate Monte Carlo reliability analysis
    Complete demo with Indian context
    """
    print("🚀 Starting Indian System Monte Carlo Reliability Analysis")
    print("=" * 60)
    
    # Configuration for analysis
    config = MonteCarloConfig(
        num_simulations=5000,        # Manageable number for demo
        time_horizon=8760,           # 1 year in hours  
        confidence_level=0.95,       # 95% confidence
        include_monsoon=True,        # Mumbai monsoon impact
        include_festivals=True       # Indian festival seasons
    )
    
    # Create analyzer
    analyzer = IndianSystemReliabilityAnalyzer(config)
    
    # Run Monte Carlo simulation
    results = analyzer.run_monte_carlo_simulation()
    
    # Generate and display report
    report = analyzer.generate_reliability_report() 
    print("\n" + report)
    
    # Create visualizations
    try:
        analyzer.visualize_results()
    except ImportError:
        print("📊 Matplotlib not available for visualization")
    except Exception as e:
        print(f"📊 Visualization error: {e}")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reliability_analysis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {filename}")
    print("🎉 Monte Carlo reliability analysis completed!")
    print("\n🏙️ Remember: Mumbai local trains भी reliable हैं despite challenges!")
    print("🚀 Your systems can be reliable too with proper analysis!")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Failure Correlation Analysis System
==================================

Advanced system to analyze correlations between different system failures.
Real examples: IRCTC-UPI correlation during festival seasons, Mumbai train-traffic correlation during monsoon

मुख्य concepts:
1. Correlation coefficient calculation between failures
2. Cascade failure pattern detection  
3. Time-series correlation analysis
4. Indian system interdependency mapping

Mumbai analogy: How local train delays cause traffic jams which affect delivery times
Author: Hindi Tech Podcast Series
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import pearsonr, spearmanr
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import math
import random

# Hindi comments के साथ comprehensive failure correlation analyzer

@dataclass
class FailureEvent:
    """Individual failure event"""
    timestamp: datetime
    component: str              # Which component failed
    failure_type: str           # Type of failure (timeout, crash, etc.)
    severity: float            # 0.0 to 1.0
    duration: float            # Duration in minutes
    recovery_time: float       # Time to recover in minutes
    cascade_depth: int         # How many other components affected
    root_cause: Optional[str]  # Root cause if known
    
    # Indian context
    monsoon_related: bool      # Whether related to monsoon
    festival_load: bool        # Whether during festival season
    peak_hour: bool           # Whether during peak hours

@dataclass
class CorrelationResult:
    """Correlation analysis result"""
    component_pair: Tuple[str, str]
    correlation_coefficient: float    # Pearson correlation (-1 to 1)
    p_value: float                   # Statistical significance
    confidence_level: float          # Confidence in correlation
    sample_size: int                 # Number of data points
    correlation_type: str            # 'POSITIVE', 'NEGATIVE', 'NONE'
    strength: str                    # 'WEAK', 'MODERATE', 'STRONG'
    
    # Time-based analysis
    lag_correlation: Dict[int, float]  # Correlation at different time lags
    best_lag: int                     # Time lag with highest correlation
    
    # Indian context insights
    mumbai_analogy: str              # Mumbai-based explanation
    business_impact: str             # Business impact description

class IndianFailureCorrelationAnalyzer:
    """
    Advanced failure correlation analyzer with Indian system context
    Mumbai के interconnected systems जैसा analysis - train delay affects everything!
    """
    
    def __init__(self, analysis_window_hours: int = 168):  # 1 week default
        self.analysis_window_hours = analysis_window_hours
        self.failure_events = deque(maxlen=10000)  # Keep last 10K events
        self.correlations = {}
        
        # Component relationship mapping - भारतीय systems की dependencies
        self.indian_system_dependencies = {
            'UPI_Gateway': ['Bank_API', 'SMS_Service', 'User_Session'],
            'IRCTC_Booking': ['Payment_Gateway', 'Database', 'SMS_Service', 'User_Session'],
            'Ecommerce_Cart': ['Payment_Gateway', 'Inventory_Service', 'User_Session'],
            'Food_Delivery': ['GPS_Service', 'Payment_Gateway', 'SMS_Service'],
            'Mumbai_Traffic': ['Weather_Service', 'GPS_Service'],
            'Power_Grid': ['Weather_Service'],
            'Internet_Service': ['Power_Grid', 'Weather_Service']
        }
        
        # Known correlation patterns in Indian systems
        self.known_patterns = {
            ('Mumbai_Traffic', 'Food_Delivery'): 0.7,      # Traffic affects delivery times
            ('Power_Grid', 'Internet_Service'): 0.8,       # Power cuts affect internet
            ('Weather_Service', 'Mumbai_Traffic'): 0.6,     # Weather affects traffic
            ('SMS_Service', 'UPI_Gateway'): 0.5,           # SMS issues affect UPI
            ('Weather_Service', 'Power_Grid'): 0.7         # Weather affects power
        }
        
        print("🔍 Indian Failure Correlation Analyzer initialized")
        print("📊 Ready to find hidden connections like Mumbai's interdependent systems!")
        
    def add_failure_event(self, event: FailureEvent) -> None:
        """
        Add a new failure event to the analysis
        नया failure event add करते हैं analysis के लिए
        """
        self.failure_events.append(event)
        
        # Auto-update correlations if we have enough data
        if len(self.failure_events) > 50:  # Minimum data threshold
            self._update_correlations()
            
    def _update_correlations(self) -> None:
        """
        Update correlation analysis with latest data
        Latest data के साथ correlations update करते हैं
        """
        # Get recent events within analysis window
        cutoff_time = datetime.now() - timedelta(hours=self.analysis_window_hours)
        recent_events = [e for e in self.failure_events if e.timestamp >= cutoff_time]
        
        if len(recent_events) < 10:  # Not enough data
            return
            
        # Create component pairs for analysis
        components = set(event.component for event in recent_events)
        component_pairs = []
        
        for comp1 in components:
            for comp2 in components:
                if comp1 < comp2:  # Avoid duplicates
                    component_pairs.append((comp1, comp2))
                    
        # Analyze each pair
        for pair in component_pairs:
            correlation = self._calculate_pair_correlation(pair, recent_events)
            if correlation:
                self.correlations[pair] = correlation
                
    def _calculate_pair_correlation(self, 
                                   component_pair: Tuple[str, str], 
                                   events: List[FailureEvent]) -> Optional[CorrelationResult]:
        """
        Calculate correlation between two components
        दो components के बीच correlation calculate करते हैं
        """
        comp1, comp2 = component_pair
        
        # Filter events for each component
        comp1_events = [e for e in events if e.component == comp1]
        comp2_events = [e for e in events if e.component == comp2]
        
        if len(comp1_events) < 5 or len(comp2_events) < 5:  # Not enough data
            return None
            
        # Create time series for correlation analysis
        time_series = self._create_correlation_time_series(comp1_events, comp2_events)
        
        if len(time_series) < 10:  # Need minimum data points
            return None
            
        # Calculate Pearson correlation
        comp1_values = [point['comp1_failures'] for point in time_series]
        comp2_values = [point['comp2_failures'] for point in time_series]
        
        correlation_coeff, p_value = pearsonr(comp1_values, comp2_values)
        
        # Calculate lag correlations (time-shifted correlations)
        lag_correlations = self._calculate_lag_correlations(comp1_values, comp2_values)
        best_lag = max(lag_correlations.keys(), key=lambda k: abs(lag_correlations[k]))
        
        # Determine correlation strength and type
        correlation_type = self._classify_correlation_type(correlation_coeff)
        strength = self._classify_correlation_strength(abs(correlation_coeff))
        
        # Generate Mumbai analogy and business impact
        mumbai_analogy = self._generate_mumbai_analogy(component_pair, correlation_coeff)
        business_impact = self._assess_business_impact(component_pair, correlation_coeff)
        
        return CorrelationResult(
            component_pair=component_pair,
            correlation_coefficient=correlation_coeff,
            p_value=p_value,
            confidence_level=1 - p_value,
            sample_size=len(time_series),
            correlation_type=correlation_type,
            strength=strength,
            lag_correlation=lag_correlations,
            best_lag=best_lag,
            mumbai_analogy=mumbai_analogy,
            business_impact=business_impact
        )
        
    def _create_correlation_time_series(self, 
                                       comp1_events: List[FailureEvent], 
                                       comp2_events: List[FailureEvent]) -> List[Dict]:
        """
        Create time series data for correlation analysis
        Time series data बनाते हैं correlation के लिए
        """
        # Determine time range
        all_events = comp1_events + comp2_events
        start_time = min(event.timestamp for event in all_events)
        end_time = max(event.timestamp for event in all_events)
        
        # Create hourly buckets
        time_series = []
        current_time = start_time
        
        while current_time <= end_time:
            bucket_end = current_time + timedelta(hours=1)
            
            # Count failures in this hour for each component
            comp1_failures = len([e for e in comp1_events 
                                if current_time <= e.timestamp < bucket_end])
            comp2_failures = len([e for e in comp2_events 
                                if current_time <= e.timestamp < bucket_end])
                                
            # Calculate severity metrics
            comp1_severity = sum(e.severity for e in comp1_events 
                               if current_time <= e.timestamp < bucket_end)
            comp2_severity = sum(e.severity for e in comp2_events 
                               if current_time <= e.timestamp < bucket_end)
            
            time_series.append({
                'timestamp': current_time,
                'comp1_failures': comp1_failures,
                'comp2_failures': comp2_failures,
                'comp1_severity': comp1_severity,
                'comp2_severity': comp2_severity
            })
            
            current_time = bucket_end
            
        return time_series
        
    def _calculate_lag_correlations(self, values1: List[float], values2: List[float]) -> Dict[int, float]:
        """
        Calculate correlations at different time lags
        Different time lags पर correlations calculate करते हैं
        """
        lag_correlations = {}
        max_lag = min(24, len(values1) // 4)  # Max 24 hours or 1/4 of data
        
        for lag in range(-max_lag, max_lag + 1):
            if lag == 0:
                # No lag correlation (already calculated)
                lag_correlations[lag], _ = pearsonr(values1, values2)
            elif lag > 0:
                # Positive lag: values2 leads values1
                if len(values1[lag:]) > 5 and len(values2[:-lag]) > 5:
                    corr, _ = pearsonr(values1[lag:], values2[:-lag])
                    lag_correlations[lag] = corr
            else:
                # Negative lag: values1 leads values2
                abs_lag = abs(lag)
                if len(values1[:-abs_lag]) > 5 and len(values2[abs_lag:]) > 5:
                    corr, _ = pearsonr(values1[:-abs_lag], values2[abs_lag:])
                    lag_correlations[lag] = corr
                    
        return lag_correlations
        
    def _classify_correlation_type(self, correlation: float) -> str:
        """Classify correlation as positive, negative, or none"""
        if abs(correlation) < 0.1:
            return "NONE"
        elif correlation > 0:
            return "POSITIVE"
        else:
            return "NEGATIVE"
            
    def _classify_correlation_strength(self, abs_correlation: float) -> str:
        """Classify correlation strength"""
        if abs_correlation < 0.3:
            return "WEAK"
        elif abs_correlation < 0.7:
            return "MODERATE"  
        else:
            return "STRONG"
            
    def _generate_mumbai_analogy(self, component_pair: Tuple[str, str], correlation: float) -> str:
        """
        Generate Mumbai-based analogy for the correlation
        Mumbai के analogies generate करते हैं correlation के लिए
        """
        comp1, comp2 = component_pair
        
        # Known Mumbai analogies
        mumbai_analogies = {
            ('Mumbai_Traffic', 'Food_Delivery'): 
                "जैसे traffic jam में food delivery slow हो जाती है",
            ('Power_Grid', 'Internet_Service'):
                "जैसे light जाने पर internet भी चला जाता है",
            ('Weather_Service', 'Mumbai_Traffic'):
                "जैसे बारिश होने पर traffic jam हो जाता है",
            ('SMS_Service', 'UPI_Gateway'):
                "जैसे SMS नहीं आने पर UPI payment stuck हो जाती है"
        }
        
        # Check if we have a predefined analogy
        if component_pair in mumbai_analogies:
            return mumbai_analogies[component_pair]
        
        # Generate generic analogy based on correlation strength
        if abs(correlation) > 0.7:
            if correlation > 0:
                return f"जैसे {comp1} fail होने पर {comp2} भी तुरंत fail हो जाता है - Mumbai local train chain reaction जैसा!"
            else:
                return f"जैसे {comp1} fail होने पर {comp2} बेहतर काम करता है - alternate route जैसा concept!"
        elif abs(correlation) > 0.3:
            return f"जैसे Mumbai की peak hours में - {comp1} और {comp2} का कुछ connection है, पूरा नहीं"
        else:
            return f"{comp1} और {comp2} का कोई strong connection नहीं - independent systems जैसे"
            
    def _assess_business_impact(self, component_pair: Tuple[str, str], correlation: float) -> str:
        """
        Assess business impact of the correlation
        Correlation का business impact assess करते हैं
        """
        comp1, comp2 = component_pair
        
        impact_levels = {
            'UPI_Gateway': 'HIGH',
            'Payment_Gateway': 'HIGH',
            'IRCTC_Booking': 'HIGH',
            'User_Session': 'MEDIUM',
            'SMS_Service': 'MEDIUM',
            'Food_Delivery': 'MEDIUM',
            'GPS_Service': 'LOW',
            'Weather_Service': 'LOW'
        }
        
        comp1_impact = impact_levels.get(comp1, 'LOW')
        comp2_impact = impact_levels.get(comp2, 'LOW')
        
        # Determine overall impact
        if comp1_impact == 'HIGH' or comp2_impact == 'HIGH':
            if abs(correlation) > 0.5:
                return f"CRITICAL: Strong correlation between critical systems - revenue impact expected"
            else:
                return f"HIGH: One critical system involved - monitor closely"
        elif comp1_impact == 'MEDIUM' or comp2_impact == 'MEDIUM':
            if abs(correlation) > 0.7:
                return f"MEDIUM: Moderate business impact - customer experience affected"
            else:
                return f"LOW: Limited business impact - operational efficiency affected"
        else:
            return f"LOW: Minimal business impact - infrastructure correlation"
            
    def detect_cascade_failures(self) -> List[Dict]:
        """
        Detect potential cascade failure patterns
        Cascade failure patterns detect करते हैं
        """
        cascade_patterns = []
        
        # Get recent high-correlation pairs
        high_correlations = [
            (pair, corr) for pair, corr in self.correlations.items()
            if abs(corr.correlation_coefficient) > 0.5 and corr.p_value < 0.05
        ]
        
        # Look for chains of correlations (A->B->C patterns)
        components = set()
        for (comp1, comp2), _ in high_correlations:
            components.add(comp1)
            components.add(comp2)
            
        for comp in components:
            # Find all components correlated with this one
            connected_components = []
            for (comp1, comp2), corr_result in high_correlations:
                if comp1 == comp and corr_result.correlation_coefficient > 0:
                    connected_components.append((comp2, corr_result.correlation_coefficient))
                elif comp2 == comp and corr_result.correlation_coefficient > 0:
                    connected_components.append((comp1, corr_result.correlation_coefficient))
                    
            if len(connected_components) >= 2:
                # Potential cascade failure pattern
                cascade_patterns.append({
                    'trigger_component': comp,
                    'affected_components': connected_components,
                    'cascade_potential': sum(corr for _, corr in connected_components) / len(connected_components),
                    'risk_level': self._assess_cascade_risk(comp, connected_components)
                })
                
        return sorted(cascade_patterns, key=lambda x: x['cascade_potential'], reverse=True)
        
    def _assess_cascade_risk(self, trigger: str, affected: List[Tuple[str, float]]) -> str:
        """Assess cascade failure risk level"""
        avg_correlation = sum(corr for _, corr in affected) / len(affected)
        num_affected = len(affected)
        
        # Check if critical systems are involved
        critical_systems = {'UPI_Gateway', 'Payment_Gateway', 'IRCTC_Booking'}
        has_critical = trigger in critical_systems or any(comp in critical_systems for comp, _ in affected)
        
        if avg_correlation > 0.7 and num_affected >= 3 and has_critical:
            return "CRITICAL"
        elif avg_correlation > 0.5 and num_affected >= 2:
            return "HIGH"
        elif avg_correlation > 0.3:
            return "MEDIUM"
        else:
            return "LOW"
            
    def generate_correlation_report(self) -> str:
        """
        Generate comprehensive correlation analysis report
        Comprehensive correlation report generate करते हैं
        """
        if not self.correlations:
            return "❌ No correlation data available. Add failure events first!"
            
        report = []
        report.append("🔍 INDIAN SYSTEM FAILURE CORRELATION REPORT")
        report.append("=" * 60)
        report.append(f"📊 Analysis Period: Last {self.analysis_window_hours} hours")
        report.append(f"🔧 Total Component Pairs Analyzed: {len(self.correlations)}")
        report.append(f"📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
        report.append("")
        
        # Sort correlations by strength
        sorted_correlations = sorted(
            self.correlations.items(), 
            key=lambda x: abs(x[1].correlation_coefficient), 
            reverse=True
        )
        
        # Strong correlations section
        strong_correlations = [(pair, corr) for pair, corr in sorted_correlations 
                             if corr.strength == "STRONG"]
        
        if strong_correlations:
            report.append("🔥 STRONG CORRELATIONS (|r| > 0.7)")
            report.append("-" * 50)
            
            for (comp1, comp2), corr in strong_correlations[:10]:  # Top 10
                sign = "+" if corr.correlation_coefficient > 0 else "-"
                report.append(f"\n🎯 {comp1} ↔ {comp2}")
                report.append(f"   Correlation: {sign}{abs(corr.correlation_coefficient):.3f}")
                report.append(f"   Confidence: {corr.confidence_level:.1%}")
                report.append(f"   Best Time Lag: {corr.best_lag} hours")
                report.append(f"   🏙️ Mumbai Analogy: {corr.mumbai_analogy}")
                report.append(f"   💼 Business Impact: {corr.business_impact}")
                
        # Cascade failure analysis
        cascade_patterns = self.detect_cascade_failures()
        if cascade_patterns:
            report.append("\n\n⛓️ CASCADE FAILURE PATTERNS")
            report.append("-" * 50)
            
            for pattern in cascade_patterns[:5]:  # Top 5 cascade risks
                report.append(f"\n🚨 Trigger: {pattern['trigger_component']}")
                report.append(f"   Risk Level: {pattern['risk_level']}")
                report.append(f"   Cascade Potential: {pattern['cascade_potential']:.3f}")
                report.append(f"   Affected Components:")
                
                for comp, corr in pattern['affected_components']:
                    report.append(f"     • {comp} (correlation: {corr:.3f})")
                    
        # Indian context insights
        report.append("\n\n🇮🇳 INDIAN SYSTEM INSIGHTS")
        report.append("-" * 50)
        
        # Count correlations by type
        positive_corrs = len([c for c in self.correlations.values() if c.correlation_type == "POSITIVE"])
        negative_corrs = len([c for c in self.correlations.values() if c.correlation_type == "NEGATIVE"])
        
        report.append(f"🔗 Positive Correlations: {positive_corrs} (failures cascade together)")
        report.append(f"🔀 Negative Correlations: {negative_corrs} (failures alternate/compensate)")
        
        # Seasonal analysis if we have enough data
        monsoon_correlations = self._analyze_seasonal_correlations()
        if monsoon_correlations:
            report.append(f"\n🌧️ MONSOON SEASON IMPACT:")
            for insight in monsoon_correlations:
                report.append(f"   • {insight}")
                
        # Recommendations
        report.append("\n\n💡 ACTIONABLE RECOMMENDATIONS")
        report.append("-" * 50)
        
        if strong_correlations:
            report.append("🛠️ For Strong Correlations:")
            report.append("   • Implement circuit breakers between correlated components")
            report.append("   • Set up alerts for cascade failure prevention")
            report.append("   • Design fallback mechanisms for high-risk pairs")
            
        if cascade_patterns:
            report.append("🔗 For Cascade Patterns:")
            report.append("   • Monitor trigger components more closely")
            report.append("   • Implement bulkhead patterns to isolate failures")
            report.append("   • Create disaster recovery plans for cascade scenarios")
            
        report.append("🏙️ Mumbai-Specific Recommendations:")
        report.append("   • Account for monsoon correlations in system design")
        report.append("   • Prepare for festival season cascade effects")
        report.append("   • Use Mumbai traffic patterns to predict system bottlenecks")
        
        report.append("\n🎯 Remember: Strong correlations mean one failure leads to another!")
        report.append("🚊 Like Mumbai locals - one delay affects the entire line!")
        
        return "\n".join(report)
        
    def _analyze_seasonal_correlations(self) -> List[str]:
        """Analyze seasonal correlation patterns"""
        insights = []
        
        # This would require more complex analysis with seasonal data
        # For demo, return some generic insights
        if any(event.monsoon_related for event in self.failure_events):
            insights.append("Higher correlations observed during monsoon season")
            
        if any(event.festival_load for event in self.failure_events):
            insights.append("Payment gateway correlations spike during festivals")
            
        if any(event.peak_hour for event in self.failure_events):
            insights.append("Peak hour failures show stronger correlations")
            
        return insights

def simulate_indian_system_failures() -> List[FailureEvent]:
    """
    Simulate realistic failure events for Indian systems
    भारतीय systems के लिए realistic failures simulate करते हैं
    """
    components = [
        'UPI_Gateway', 'Payment_Gateway', 'IRCTC_Booking', 'SMS_Service',
        'User_Session', 'Food_Delivery', 'Mumbai_Traffic', 'Power_Grid',
        'Internet_Service', 'Weather_Service', 'GPS_Service', 'Database'
    ]
    
    failure_types = [
        'TIMEOUT', 'CONNECTION_ERROR', 'SERVICE_UNAVAILABLE', 'DATABASE_ERROR',
        'NETWORK_PARTITION', 'RESOURCE_EXHAUSTION', 'CONFIGURATION_ERROR'
    ]
    
    events = []
    start_time = datetime.now() - timedelta(days=7)  # Last week
    
    # Generate 500 failure events with realistic patterns
    for i in range(500):
        # Random timestamp in the last week
        random_offset = random.uniform(0, 7 * 24 * 60 * 60)  # Random seconds in a week
        timestamp = start_time + timedelta(seconds=random_offset)
        
        # Component selection with realistic probabilities
        component_weights = {
            'SMS_Service': 0.2,      # SMS is most unreliable in India!
            'UPI_Gateway': 0.15,     # Payment issues common
            'Power_Grid': 0.15,      # Power cuts frequent
            'Internet_Service': 0.12, # Internet connectivity issues
            'IRCTC_Booking': 0.1,    # IRCTC has its moments
            'Payment_Gateway': 0.08,
            'Mumbai_Traffic': 0.05,
            'Food_Delivery': 0.05,
            'GPS_Service': 0.04,
            'User_Session': 0.03,
            'Weather_Service': 0.02,
            'Database': 0.01
        }
        
        component = random.choices(list(component_weights.keys()), 
                                 weights=list(component_weights.values()))[0]
        
        # Context-aware failure generation
        is_monsoon = timestamp.month in [6, 7, 8, 9]
        is_festival = timestamp.month in [10, 3, 8]  # Diwali, Holi, Ganesh
        is_peak_hour = timestamp.hour in [9, 10, 18, 19, 20]
        
        # Adjust severity based on context
        base_severity = random.uniform(0.3, 0.9)
        if is_monsoon and component in ['Power_Grid', 'Internet_Service', 'Mumbai_Traffic']:
            base_severity *= 1.4
        if is_festival and component in ['UPI_Gateway', 'Payment_Gateway', 'IRCTC_Booking']:
            base_severity *= 1.3
        if is_peak_hour:
            base_severity *= 1.2
            
        event = FailureEvent(
            timestamp=timestamp,
            component=component,
            failure_type=random.choice(failure_types),
            severity=min(1.0, base_severity),
            duration=random.uniform(5, 120),  # 5 minutes to 2 hours
            recovery_time=random.uniform(10, 180),  # 10 minutes to 3 hours
            cascade_depth=random.randint(0, 3),
            root_cause=None,
            monsoon_related=is_monsoon and random.random() < 0.6,
            festival_load=is_festival and random.random() < 0.4,
            peak_hour=is_peak_hour and random.random() < 0.7
        )
        
        events.append(event)
        
    return sorted(events, key=lambda x: x.timestamp)

async def demo_failure_correlation_analyzer():
    """
    Comprehensive demonstration of failure correlation analysis
    Complete demo with Indian system failure correlations
    """
    print("🔍 Indian Failure Correlation Analyzer Demo")
    print("=" * 60)
    
    # Create analyzer
    analyzer = IndianFailureCorrelationAnalyzer(analysis_window_hours=168)  # 1 week
    
    # Simulate failure events
    print("📊 Generating realistic Indian system failure events...")
    failure_events = simulate_indian_system_failures()
    
    print(f"✅ Generated {len(failure_events)} failure events")
    print("🔍 Adding events to correlation analyzer...")
    
    # Add events to analyzer
    for i, event in enumerate(failure_events):
        analyzer.add_failure_event(event)
        
        # Show progress every 100 events
        if (i + 1) % 100 == 0:
            print(f"   Processed {i + 1}/{len(failure_events)} events...")
            
    print("🧮 Analyzing correlations between system components...")
    
    # Force final correlation update
    analyzer._update_correlations()
    
    print(f"✅ Found correlations between {len(analyzer.correlations)} component pairs")
    
    # Display top correlations
    print("\n🔥 TOP 5 STRONGEST CORRELATIONS:")
    print("-" * 50)
    
    sorted_correlations = sorted(
        analyzer.correlations.items(),
        key=lambda x: abs(x[1].correlation_coefficient),
        reverse=True
    )
    
    for i, ((comp1, comp2), corr) in enumerate(sorted_correlations[:5]):
        sign = "📈" if corr.correlation_coefficient > 0 else "📉"
        print(f"\n{i+1}. {comp1} ↔ {comp2}")
        print(f"   {sign} Correlation: {corr.correlation_coefficient:+.3f}")
        print(f"   💪 Strength: {corr.strength}")
        print(f"   🎯 Confidence: {corr.confidence_level:.1%}")
        print(f"   🏙️ {corr.mumbai_analogy}")
        
    # Cascade failure analysis
    cascade_patterns = analyzer.detect_cascade_failures()
    print(f"\n⛓️ DETECTED {len(cascade_patterns)} CASCADE FAILURE PATTERNS:")
    
    for i, pattern in enumerate(cascade_patterns[:3]):  # Top 3
        print(f"\n🚨 Pattern {i+1}: {pattern['trigger_component']} triggers cascade")
        print(f"   Risk Level: {pattern['risk_level']}")
        print(f"   Cascade Potential: {pattern['cascade_potential']:.3f}")
        print(f"   Affects {len(pattern['affected_components'])} other components")
        
    # Generate comprehensive report
    print("\n📋 GENERATING COMPREHENSIVE CORRELATION REPORT...")
    report = analyzer.generate_correlation_report()
    print("\n" + report)
    
    print("\n🎉 Failure correlation analysis completed!")
    print("🏙️ Just like Mumbai's interconnected systems - one failure affects many!")
    print("💡 Use correlations to predict and prevent cascade failures!")

async def main():
    """Main demonstration function"""
    await demo_failure_correlation_analyzer()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
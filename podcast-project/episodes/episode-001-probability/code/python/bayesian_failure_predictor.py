#!/usr/bin/env python3
"""
Bayesian Failure Prediction System
==================================

Bayes theorem का use करके system failures predict करते हैं।
Real examples: PhonePe transaction failures, Mumbai train delays, IRCTC booking success rates

मुख्य concepts:
1. Bayes theorem for probabilistic reasoning
2. Prior/posterior probability updates
3. Evidence accumulation over time  
4. Indian payment system failure patterns

Mumbai analogy: Train delay prediction based on historical patterns
Author: Hindi Tech Podcast Series
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime, timedelta
import random
import math

# Hindi comments के साथ comprehensive Bayesian prediction system

@dataclass
class BayesianEvidence:
    """Evidence data point for Bayesian updates"""
    timestamp: datetime
    event_type: str          # 'success' या 'failure'
    context: Dict           # Additional context (load, weather, etc.)
    severity: float         # 0.0 to 1.0, failure severity
    system_component: str   # Which component failed/succeeded

@dataclass
class PriorBelief:
    """Prior probability beliefs about system"""
    component: str
    base_failure_rate: float      # Base failure probability
    seasonal_factors: Dict        # Seasonal multipliers
    load_sensitivity: float       # How sensitive to load (0-1)
    confidence: float            # How confident in this prior (0-1)

class IndianBayesianPredictor:
    """
    Bayesian failure prediction system with Indian context
    Mumbai के traffic patterns और festival seasons को consider करते हैं
    """
    
    def __init__(self):
        self.components = self._initialize_components()
        self.evidence_history = []
        self.posterior_beliefs = {}
        
        # Indian specific patterns - भारतीय context के patterns
        self.monsoon_impact = {
            6: 1.8, 7: 2.1, 8: 2.3, 9: 1.9  # June-September monsoon multipliers
        }
        
        self.festival_impact = {
            'diwali': 2.5,      # Diwali shopping surge
            'holi': 1.8,        # Holi celebrations  
            'ganesh': 2.0,      # Ganesh Chaturthi
            'eid': 1.9,         # Eid celebrations
            'independence': 1.4, # Independence Day traffic
            'regular': 1.0      # Normal days
        }
        
        self.peak_hours = {
            'morning': (9, 11),    # 9-11 AM office rush
            'evening': (18, 20),   # 6-8 PM return rush
            'lunch': (12, 14),     # Lunch hour
            'night': (22, 6)       # Night low activity
        }
        
        print("🧠 Bayesian Failure Prediction System initialized")
        print("📊 Ready to learn from Indian system patterns!")
        
    def _initialize_components(self) -> Dict[str, PriorBelief]:
        """Initialize system components with prior beliefs"""
        
        # UPI payment system components with Indian characteristics  
        components = {
            'payment_gateway': PriorBelief(
                component='payment_gateway',
                base_failure_rate=0.02,  # 2% base failure rate
                seasonal_factors={'monsoon': 1.5, 'festival': 2.2, 'normal': 1.0},
                load_sensitivity=0.8,    # Highly sensitive to load
                confidence=0.7
            ),
            'database': PriorBelief(
                component='database', 
                base_failure_rate=0.005, # 0.5% base failure rate
                seasonal_factors={'monsoon': 1.2, 'festival': 1.8, 'normal': 1.0},
                load_sensitivity=0.6,
                confidence=0.8
            ),
            'sms_service': PriorBelief(
                component='sms_service',
                base_failure_rate=0.08,  # 8% base failure rate (SMS हमेशा problem!)
                seasonal_factors={'monsoon': 2.0, 'festival': 3.0, 'normal': 1.0},
                load_sensitivity=0.9,    # Very sensitive
                confidence=0.6
            ),
            'load_balancer': PriorBelief(
                component='load_balancer',
                base_failure_rate=0.001, # 0.1% base failure rate  
                seasonal_factors={'monsoon': 1.1, 'festival': 1.4, 'normal': 1.0},
                load_sensitivity=0.4,
                confidence=0.9
            ),
            'user_session': PriorBelief(
                component='user_session',
                base_failure_rate=0.03,  # 3% base failure rate
                seasonal_factors={'monsoon': 1.3, 'festival': 2.1, 'normal': 1.0}, 
                load_sensitivity=0.7,
                confidence=0.7
            )
        }
        
        print(f"🔧 Initialized {len(components)} components with prior beliefs")
        return components
        
    def add_evidence(self, evidence: BayesianEvidence) -> None:
        """
        Add new evidence to update Bayesian beliefs  
        नया evidence के साथ beliefs को update करते हैं
        """
        self.evidence_history.append(evidence)
        
        # Update posterior beliefs using Bayes theorem
        self._update_posterior_beliefs(evidence)
        
    def _update_posterior_beliefs(self, new_evidence: BayesianEvidence) -> None:
        """
        Update posterior probabilities using Bayes theorem
        P(Failure|Evidence) = P(Evidence|Failure) * P(Failure) / P(Evidence)
        """
        component = new_evidence.system_component
        
        if component not in self.components:
            print(f"⚠️  Unknown component: {component}")
            return
            
        prior = self.components[component]
        
        # Get current context factors
        context_multiplier = self._calculate_context_multiplier(new_evidence)
        
        # Calculate likelihood: P(Evidence|Failure) और P(Evidence|Success)
        if new_evidence.event_type == 'failure':
            # Evidence supports failure hypothesis
            likelihood_failure = 0.9 * new_evidence.severity  # High likelihood if severe
            likelihood_success = 0.1 * (1 - new_evidence.severity)
        else:
            # Evidence supports success hypothesis  
            likelihood_failure = 0.1 + (0.3 * new_evidence.severity)  # Some chance still
            likelihood_success = 0.9 - (0.2 * new_evidence.severity)
            
        # Get current posterior (or use prior if first update)
        if component not in self.posterior_beliefs:
            current_failure_prob = prior.base_failure_rate * context_multiplier
        else:
            current_failure_prob = self.posterior_beliefs[component]['failure_probability']
            
        current_success_prob = 1 - current_failure_prob
        
        # Apply Bayes theorem
        # P(Evidence) = P(Evidence|Failure) * P(Failure) + P(Evidence|Success) * P(Success)
        evidence_probability = (likelihood_failure * current_failure_prob + 
                              likelihood_success * current_success_prob)
        
        if evidence_probability > 0:
            # Update posterior probabilities
            new_failure_prob = (likelihood_failure * current_failure_prob) / evidence_probability
            new_success_prob = (likelihood_success * current_success_prob) / evidence_probability
            
            # Store updated beliefs
            self.posterior_beliefs[component] = {
                'failure_probability': new_failure_prob,
                'success_probability': new_success_prob,
                'last_update': new_evidence.timestamp,
                'evidence_count': self.posterior_beliefs.get(component, {}).get('evidence_count', 0) + 1,
                'confidence': self._calculate_confidence(component)
            }
            
            print(f"🔄 Updated {component}: P(Failure) = {new_failure_prob:.4f}")
        
    def _calculate_context_multiplier(self, evidence: BayesianEvidence) -> float:
        """
        Calculate context-based multiplier for Indian conditions
        Mumbai के seasonal और traffic patterns के हिसाब से multiplier
        """
        multiplier = 1.0
        
        # Time-based factors
        hour = evidence.timestamp.hour
        month = evidence.timestamp.month
        
        # Monsoon impact - बारिश का असर
        if month in self.monsoon_impact:
            multiplier *= self.monsoon_impact[month]
            
        # Peak hour impact - rush hours का असर
        if 9 <= hour <= 11 or 18 <= hour <= 20:
            multiplier *= 1.4  # Peak hour stress
        elif 22 <= hour or hour <= 6:
            multiplier *= 0.7  # Low activity night hours
            
        # Festival impact - त्योहारों का असर
        festival_type = evidence.context.get('festival', 'regular')
        if festival_type in self.festival_impact:
            multiplier *= self.festival_impact[festival_type]
            
        # Load impact - system load का असर
        load_factor = evidence.context.get('load_factor', 1.0)
        if load_factor > 1.5:
            multiplier *= 1.3  # High load stress
        elif load_factor < 0.5:
            multiplier *= 0.8  # Low load relaxation
            
        return multiplier
        
    def _calculate_confidence(self, component: str) -> float:
        """
        Calculate confidence in prediction based on evidence history
        Evidence की quantity और quality के base पर confidence calculate करते हैं
        """
        if component not in self.posterior_beliefs:
            return self.components[component].confidence
            
        evidence_count = self.posterior_beliefs[component]['evidence_count']
        
        # More evidence = higher confidence (up to a limit)
        base_confidence = self.components[component].confidence
        evidence_boost = min(0.3, evidence_count * 0.02)  # Max 30% boost
        
        # Recent evidence gets more weight
        hours_since_update = (datetime.now() - self.posterior_beliefs[component]['last_update']).total_seconds() / 3600
        recency_penalty = max(0, min(0.2, hours_since_update * 0.001))  # Max 20% penalty
        
        final_confidence = base_confidence + evidence_boost - recency_penalty
        return max(0.1, min(0.99, final_confidence))  # Keep between 10-99%
        
    def predict_failure_probability(self, component: str, context: Dict = None) -> Dict:
        """
        Predict failure probability for a component given context
        Context के साथ failure probability predict करते हैं
        """
        if component not in self.components:
            return {'error': f'Unknown component: {component}'}
            
        # Get current timestamp for context
        current_time = datetime.now()
        
        if context is None:
            context = {}
            
        # Create evidence object for context calculation  
        mock_evidence = BayesianEvidence(
            timestamp=current_time,
            event_type='query',
            context=context,
            severity=0.0,
            system_component=component
        )
        
        # Get context multiplier
        context_multiplier = self._calculate_context_multiplier(mock_evidence)
        
        # Get current belief (posterior or prior)
        if component in self.posterior_beliefs:
            base_probability = self.posterior_beliefs[component]['failure_probability']
            confidence = self.posterior_beliefs[component]['confidence']
            evidence_count = self.posterior_beliefs[component]['evidence_count']
        else:
            base_probability = self.components[component].base_failure_rate
            confidence = self.components[component].confidence  
            evidence_count = 0
            
        # Apply context
        adjusted_probability = min(0.99, base_probability * context_multiplier)
        
        # Mumbai-specific insights
        insights = self._generate_mumbai_insights(component, adjusted_probability, context)
        
        return {
            'component': component,
            'failure_probability': adjusted_probability,
            'success_probability': 1 - adjusted_probability,
            'confidence': confidence,
            'context_multiplier': context_multiplier,
            'evidence_count': evidence_count,
            'prediction_time': current_time.isoformat(),
            'risk_level': self._get_risk_level(adjusted_probability),
            'mumbai_insights': insights,
            'recommendations': self._get_recommendations(component, adjusted_probability, context)
        }
        
    def _generate_mumbai_insights(self, component: str, probability: float, context: Dict) -> List[str]:
        """Generate Mumbai-specific insights"""
        insights = []
        
        current_hour = datetime.now().hour
        current_month = datetime.now().month
        
        # Time-based insights
        if 9 <= current_hour <= 11:
            insights.append("🌅 Morning office rush - IRCTC booking जैसा high load expected")
        elif 18 <= current_hour <= 20:
            insights.append("🌆 Evening return rush - Mumbai local train जैसी peak traffic")
        elif 22 <= current_hour or current_hour <= 6:
            insights.append("🌙 Night time - Delivery apps जैसा low activity period")
            
        # Monsoon insights
        if current_month in [6, 7, 8, 9]:
            insights.append("🌧️ Monsoon season active - Mumbai में पानी भरने जैसी problems expected")
            if probability > 0.1:
                insights.append("⚠️ Higher failure risk due to monsoon - waterlogging जैसे issues possible")
                
        # Load-based insights  
        load_factor = context.get('load_factor', 1.0)
        if load_factor > 2.0:
            insights.append("🚨 Very high load - Flipkart Big Billion Day जैसा traffic surge")
        elif load_factor > 1.5:
            insights.append("📈 High load detected - Festival shopping जैसा increased activity")
            
        # Festival insights
        festival = context.get('festival', 'regular')
        if festival != 'regular':
            insights.append(f"🎉 {festival.title()} season - Increased transaction volume expected")
            
        return insights
        
    def _get_risk_level(self, probability: float) -> str:
        """Convert probability to risk level"""
        if probability < 0.01:
            return "LOW 🟢"
        elif probability < 0.05:
            return "MODERATE 🟡" 
        elif probability < 0.15:
            return "HIGH 🟠"
        else:
            return "CRITICAL 🔴"
            
    def _get_recommendations(self, component: str, probability: float, context: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if probability > 0.1:
            recommendations.append("🔧 Enable circuit breaker pattern")
            recommendations.append("📊 Increase monitoring frequency")
            
        if probability > 0.2:
            recommendations.append("🚨 Consider load shedding")
            recommendations.append("👥 Alert on-call team")
            
        if context.get('load_factor', 1.0) > 1.8:
            recommendations.append("⚡ Scale up infrastructure")
            recommendations.append("🚦 Implement rate limiting")
            
        # Component-specific recommendations
        if component == 'sms_service' and probability > 0.05:
            recommendations.append("📱 Switch to alternate SMS provider")
            recommendations.append("📧 Use email as backup notification")
            
        if component == 'payment_gateway' and probability > 0.03:
            recommendations.append("💳 Route to backup payment processor")
            recommendations.append("🏦 Check with bank for service issues")
            
        return recommendations
        
    def analyze_trends(self, hours_back: int = 24) -> Dict:
        """
        Analyze failure trends over time
        पिछले कुछ घंटों में trends का analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_evidence = [e for e in self.evidence_history if e.timestamp >= cutoff_time]
        
        if not recent_evidence:
            return {'message': 'No recent evidence available'}
            
        # Component-wise analysis
        component_stats = {}
        for evidence in recent_evidence:
            comp = evidence.system_component
            if comp not in component_stats:
                component_stats[comp] = {'failures': 0, 'successes': 0, 'total': 0}
                
            component_stats[comp]['total'] += 1
            if evidence.event_type == 'failure':
                component_stats[comp]['failures'] += 1
            else:
                component_stats[comp]['successes'] += 1
                
        # Calculate trends
        trends = {}
        for comp, stats in component_stats.items():
            failure_rate = stats['failures'] / stats['total']
            
            # Get predicted rate
            prediction = self.predict_failure_probability(comp)
            predicted_rate = prediction['failure_probability']
            
            # Compare actual vs predicted
            if abs(failure_rate - predicted_rate) < 0.02:
                trend = "STABLE 📊"
            elif failure_rate > predicted_rate:
                trend = "WORSENING 📈"  
            else:
                trend = "IMPROVING 📉"
                
            trends[comp] = {
                'actual_failure_rate': failure_rate,
                'predicted_failure_rate': predicted_rate,
                'trend': trend,
                'sample_size': stats['total'],
                'confidence': 'HIGH' if stats['total'] >= 10 else 'LOW'
            }
            
        return {
            'analysis_period': f'Last {hours_back} hours',
            'total_evidence_points': len(recent_evidence),
            'component_trends': trends,
            'generated_at': datetime.now().isoformat()
        }
        
    def generate_prediction_report(self) -> str:
        """Generate comprehensive prediction report"""
        
        report = []
        report.append("🧠 BAYESIAN FAILURE PREDICTION REPORT")
        report.append("=" * 50)
        report.append(f"📊 Total Evidence Points: {len(self.evidence_history)}")
        report.append(f"🔧 Components Monitored: {len(self.components)}")
        report.append(f"📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
        report.append("")
        
        # Current predictions for all components
        report.append("🎯 CURRENT FAILURE PREDICTIONS")
        report.append("-" * 40)
        
        for component in self.components:
            prediction = self.predict_failure_probability(component)
            
            report.append(f"\n🔧 {component.upper()}")
            report.append(f"   Failure Probability: {prediction['failure_probability']:.4f} ({prediction['failure_probability']*100:.2f}%)")
            report.append(f"   Risk Level: {prediction['risk_level']}")
            report.append(f"   Confidence: {prediction['confidence']:.2f}")
            report.append(f"   Evidence Count: {prediction['evidence_count']}")
            
            if prediction['mumbai_insights']:
                report.append("   🏙️ Mumbai Insights:")
                for insight in prediction['mumbai_insights'][:2]:  # Top 2 insights
                    report.append(f"     • {insight}")
                    
        # Trend analysis
        trends = self.analyze_trends()
        if 'component_trends' in trends:
            report.append("\n\n📈 TREND ANALYSIS (Last 24 hours)")
            report.append("-" * 40)
            
            for comp, trend in trends['component_trends'].items():
                report.append(f"\n{comp}: {trend['trend']}")
                report.append(f"   Actual: {trend['actual_failure_rate']:.3f}")
                report.append(f"   Predicted: {trend['predicted_failure_rate']:.3f}")
                report.append(f"   Confidence: {trend['confidence']}")
                
        # Overall system health
        report.append("\n\n🏥 OVERALL SYSTEM HEALTH")
        report.append("-" * 40)
        
        avg_failure_prob = np.mean([
            self.predict_failure_probability(comp)['failure_probability'] 
            for comp in self.components
        ])
        
        if avg_failure_prob < 0.02:
            health_status = "EXCELLENT 🟢"
            analogy = "Mumbai local trains के non-monsoon days जैसी!"
        elif avg_failure_prob < 0.08:
            health_status = "GOOD 🟡"  
            analogy = "Regular weekday traffic जैसी smooth!"
        elif avg_failure_prob < 0.15:
            health_status = "CONCERNING 🟠"
            analogy = "Festival season rush जैसी busy!"
        else:
            health_status = "CRITICAL 🔴"
            analogy = "Mumbai monsoon floods जैसी chaotic!"
            
        report.append(f"System Health: {health_status}")
        report.append(f"Average Failure Probability: {avg_failure_prob:.4f} ({avg_failure_prob*100:.2f}%)")
        report.append(f"🏙️ Mumbai Analogy: {analogy}")
        
        report.append("\n\n💡 KEY LEARNINGS")
        report.append("-" * 40)
        report.append("• Bayes theorem helps in continuous learning from evidence")
        report.append("• Indian context (monsoon, festivals) significantly impacts predictions")
        report.append("• More evidence = better predictions (like Mumbai traffic experience)")
        report.append("• Real-time updates crucial for dynamic systems")
        
        report.append("\n🚀 Happy Bayesian learning! May your priors become posteriors!")
        
        return "\n".join(report)

def main():
    """
    Demonstration of Bayesian failure prediction system
    Complete demo with Indian payment system examples
    """
    print("🧠 Starting Bayesian Failure Prediction Demo")
    print("=" * 50)
    
    # Create predictor
    predictor = IndianBayesianPredictor()
    
    # Simulate some evidence from PhonePe-like payment system
    print("\n📱 Simulating PhonePe Payment System Evidence...")
    
    evidence_scenarios = [
        # Morning rush success
        BayesianEvidence(
            timestamp=datetime(2024, 7, 15, 9, 30),  # Monsoon morning
            event_type='success',
            context={'load_factor': 1.8, 'festival': 'regular'},
            severity=0.0,
            system_component='payment_gateway'
        ),
        
        # Festival season failure  
        BayesianEvidence(
            timestamp=datetime(2024, 10, 20, 14, 15),  # Diwali shopping
            event_type='failure', 
            context={'load_factor': 3.2, 'festival': 'diwali'},
            severity=0.7,
            system_component='database'
        ),
        
        # SMS service failure (common in India!)
        BayesianEvidence(
            timestamp=datetime(2024, 8, 15, 19, 45),  # Independence Day evening
            event_type='failure',
            context={'load_factor': 2.1, 'festival': 'independence'},
            severity=0.9,
            system_component='sms_service'
        ),
        
        # Load balancer success under normal load
        BayesianEvidence(
            timestamp=datetime(2024, 12, 5, 11, 0),   # Normal December day
            event_type='success',
            context={'load_factor': 1.1, 'festival': 'regular'}, 
            severity=0.0,
            system_component='load_balancer'
        ),
        
        # User session timeout during peak
        BayesianEvidence(
            timestamp=datetime(2024, 11, 12, 20, 30), # Evening shopping
            event_type='failure',
            context={'load_factor': 1.9, 'festival': 'regular'},
            severity=0.4,
            system_component='user_session'
        )
    ]
    
    # Add evidence to predictor
    for evidence in evidence_scenarios:
        predictor.add_evidence(evidence)
        
    print(f"✅ Added {len(evidence_scenarios)} evidence points")
    
    # Make predictions for different scenarios
    print("\n🎯 Making Predictions for Different Scenarios...")
    
    scenarios = [
        ("Normal morning", {'load_factor': 1.2, 'festival': 'regular'}),
        ("Diwali shopping peak", {'load_factor': 2.8, 'festival': 'diwali'}),
        ("Monsoon evening", {'load_factor': 1.5, 'festival': 'regular'}),
        ("Night time low load", {'load_factor': 0.4, 'festival': 'regular'})
    ]
    
    for scenario_name, context in scenarios:
        print(f"\n--- {scenario_name} ---")
        
        for component in ['payment_gateway', 'sms_service']:
            prediction = predictor.predict_failure_probability(component, context)
            print(f"{component}: {prediction['failure_probability']:.4f} ({prediction['risk_level']})")
            
    # Generate comprehensive report
    report = predictor.generate_prediction_report()
    print("\n" + report)
    
    print("\n🎉 Bayesian prediction demo completed!")
    print("🧠 Remember: Bayes theorem is like Mumbai traffic experience!")
    print("   The more you travel, the better you predict delays! 🚊")

if __name__ == "__main__":
    main()
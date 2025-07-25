# Law 7: Law of Economic Reality - Exercises

## Overview

These exercises focus on understanding and optimizing the economic trade-offs in distributed systems. You'll practice calculating TCO, making build vs buy decisions, optimizing cloud costs, and understanding hidden expenses in system design.

## Exercise 1: Total Cost of Ownership (TCO) Calculator

### Background
TCO extends beyond initial purchase price to include operational, maintenance, and hidden costs. This exercise builds a comprehensive TCO model for distributed systems.

### Task
Build a TCO calculator that considers all cost factors over the system lifetime.

```python
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class CostComponent:
    name: str
    category: str  # 'capital', 'operational', 'hidden'
    amount: float
    frequency: str  # 'one-time', 'monthly', 'yearly', 'hourly'
    growth_rate: float = 0.0  # Annual growth rate
    
class TCOCalculator:
    """Calculate Total Cost of Ownership for distributed systems"""
    
    def __init__(self, project_name: str, time_horizon_years: int = 3):
        self.project_name = project_name
        self.time_horizon_years = time_horizon_years
        self.cost_components = []
        self.assumptions = {}
        
    def add_cost(self, component: CostComponent):
        """Add a cost component to the model"""
        self.cost_components.append(component)
        
    def add_assumption(self, name: str, value: any):
        """Add an assumption for documentation"""
        self.assumptions[name] = value
        
    def calculate_tco(self) -> Dict:
        """Calculate total cost of ownership"""
        results = {
            'total': 0,
            'by_category': {'capital': 0, 'operational': 0, 'hidden': 0},
            'by_year': {},
            'monthly_run_rate': 0,
            'cost_breakdown': []
        }
        
# Calculate costs for each component
        for component in self.cost_components:
            total_cost = self._calculate_component_cost(component)
            results['total'] += total_cost
            results['by_category'][component.category] += total_cost
            
# Track breakdown
            results['cost_breakdown'].append({
                'name': component.name,
                'category': component.category,
                'total': total_cost,
                'percentage': 0  # Will calculate after
            })
            
# Distribute costs by year
            self._distribute_by_year(component, results['by_year'])
        
# Calculate percentages
        for item in results['cost_breakdown']:
            item['percentage'] = (item['total'] / results['total']) * 100
            
# Sort by total cost
        results['cost_breakdown'].sort(key=lambda x: x['total'], reverse=True)
        
# Calculate monthly run rate (operational costs only)
        monthly_operational = sum(
            self._get_monthly_cost(c) for c in self.cost_components
            if c.category == 'operational'
        )
        results['monthly_run_rate'] = monthly_operational
        
        return results
    
    def _calculate_component_cost(self, component: CostComponent) -> float:
        """Calculate total cost for a component over time horizon"""
        if component.frequency == 'one-time':
            return component.amount
            
        elif component.frequency == 'hourly':
# Hours in time horizon
            hours = self.time_horizon_years * 365 * 24
            return self._apply_growth(component.amount * hours, component.growth_rate)
            
        elif component.frequency == 'monthly':
            months = self.time_horizon_years * 12
            return self._apply_growth_series(component.amount, months, component.growth_rate / 12)
            
        elif component.frequency == 'yearly':
            return self._apply_growth_series(component.amount, self.time_horizon_years, component.growth_rate)
            
        return 0
    
    def _apply_growth(self, base_amount: float, growth_rate: float) -> float:
        """Apply compound growth over time horizon"""
        return base_amount * (1 + growth_rate) ** self.time_horizon_years
    
    def _apply_growth_series(self, amount: float, periods: int, period_rate: float) -> float:
        """Calculate sum of growing series"""
        if period_rate == 0:
            return amount * periods
        
# Sum of geometric series: a * (1 - r^n) / (1 - r)
        return amount * ((1 + period_rate) ** periods - 1) / period_rate
    
    def _get_monthly_cost(self, component: CostComponent) -> float:
        """Get monthly cost for a component"""
        if component.frequency == 'monthly':
            return component.amount * (1 + component.growth_rate / 12)
        elif component.frequency == 'yearly':
            return component.amount / 12 * (1 + component.growth_rate)
        elif component.frequency == 'hourly':
            return component.amount * 24 * 30  # Approximate month
        return 0
    
    def _distribute_by_year(self, component: CostComponent, year_dict: Dict):
        """Distribute costs across years"""
        for year in range(self.time_horizon_years):
            if year not in year_dict:
                year_dict[year] = 0
                
            if component.frequency == 'one-time':
                if year == 0:  # First year only
                    year_dict[year] += component.amount
                    
            elif component.frequency == 'yearly':
                annual_cost = component.amount * (1 + component.growth_rate) ** year
                year_dict[year] += annual_cost
                
            elif component.frequency == 'monthly':
                annual_cost = component.amount * 12 * (1 + component.growth_rate) ** year
                year_dict[year] += annual_cost
                
            elif component.frequency == 'hourly':
                annual_cost = component.amount * 24 * 365 * (1 + component.growth_rate) ** year
                year_dict[year] += annual_cost
    
    def generate_report(self) -> str:
        """Generate comprehensive TCO report"""
        results = self.calculate_tco()
        
        report = f"""
TCO Analysis: {self.project_name}
{'='*50}

Time Horizon: {self.time_horizon_years} years

EXECUTIVE SUMMARY
-----------------
Total Cost of Ownership: ${results['total']:,.2f}
Monthly Run Rate: ${results['monthly_run_rate']:,.2f}

Cost by Category:
- Capital Expenses: ${results['by_category']['capital']:,.2f} ({results['by_category']['capital']/results['total']*100:.1f}%)
- Operational Expenses: ${results['by_category']['operational']:,.2f} ({results['by_category']['operational']/results['total']*100:.1f}%)
- Hidden Costs: ${results['by_category']['hidden']:,.2f} ({results['by_category']['hidden']/results['total']*100:.1f}%)

Cost by Year:
"""
        for year, cost in sorted(results['by_year'].items()):
            report += f"- Year {year + 1}: ${cost:,.2f}\n"
        
        report += f"""
Top Cost Drivers:
-----------------
"""
        for item in results['cost_breakdown'][:10]:  # Top 10
            report += f"{item['name']:<30} ${item['total']:>12,.2f} ({item['percentage']:>5.1f}%)\n"
        
        if self.assumptions:
            report += f"""
Key Assumptions:
----------------
"""
            for key, value in self.assumptions.items():
                report += f"- {key}: {value}\n"
        
        return report
    
    def visualize_costs(self):
        """Create cost visualization charts"""
        results = self.calculate_tco()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'TCO Analysis: {self.project_name}', fontsize=16)
        
# 1. Cost by Category (Pie Chart)
        categories = list(results['by_category'].keys())
        values = list(results['by_category'].values())
        ax1.pie(values, labels=categories, autopct='%1.1f%%')
        ax1.set_title('Cost Distribution by Category')
        
# 2. Cost by Year (Bar Chart)
        years = [f'Year {y+1}' for y in sorted(results['by_year'].keys())]
        yearly_costs = [results['by_year'][y] for y in sorted(results['by_year'].keys())]
        ax2.bar(years, yearly_costs)
        ax2.set_title('Annual Costs')
        ax2.set_ylabel('Cost ($)')
        
# 3. Top Cost Drivers (Horizontal Bar)
        top_items = results['cost_breakdown'][:8]
        names = [item['name'] for item in top_items]
        costs = [item['total'] for item in top_items]
        ax3.barh(names, costs)
        ax3.set_title('Top Cost Drivers')
        ax3.set_xlabel('Total Cost ($)')
        
# 4. Cumulative Cost Over Time
        months = range(self.time_horizon_years * 12)
        cumulative = []
        monthly_cost = results['monthly_run_rate']
        
        for month in months:
            if month == 0:
# Include capital costs in first month
                cumulative.append(results['by_category']['capital'] + monthly_cost)
            else:
# Just add monthly operational costs
                growth = (1 + 0.05 / 12) ** month  # Assume 5% annual growth
                cumulative.append(cumulative[-1] + monthly_cost * growth)
        
        ax4.plot(months, cumulative)
        ax4.set_title('Cumulative Cost Over Time')
        ax4.set_xlabel('Months')
        ax4.set_ylabel('Cumulative Cost ($)')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

# Example: Compare on-premise vs cloud deployment
def compare_deployment_options():
    """Compare TCO of different deployment options"""
    
# Option 1: On-Premise Deployment
    on_premise = TCOCalculator("On-Premise Deployment", time_horizon_years=5)
    
# Capital costs
    on_premise.add_cost(CostComponent("Server Hardware", "capital", 150000, "one-time"))
    on_premise.add_cost(CostComponent("Network Equipment", "capital", 30000, "one-time"))
    on_premise.add_cost(CostComponent("Storage Arrays", "capital", 80000, "one-time"))
    on_premise.add_cost(CostComponent("Software Licenses", "capital", 50000, "one-time"))
    
# Operational costs
    on_premise.add_cost(CostComponent("Data Center Space", "operational", 5000, "monthly", 0.03))
    on_premise.add_cost(CostComponent("Power & Cooling", "operational", 3000, "monthly", 0.05))
    on_premise.add_cost(CostComponent("Internet Bandwidth", "operational", 2000, "monthly", 0.02))
    on_premise.add_cost(CostComponent("Hardware Maintenance", "operational", 15000, "yearly", 0.05))
    
# Hidden costs
    on_premise.add_cost(CostComponent("IT Staff (2 FTE)", "hidden", 200000, "yearly", 0.04))
    on_premise.add_cost(CostComponent("Downtime Impact", "hidden", 5000, "monthly", 0.0))
    on_premise.add_cost(CostComponent("Security Audits", "hidden", 20000, "yearly", 0.03))
    on_premise.add_cost(CostComponent("Disaster Recovery", "hidden", 30000, "yearly", 0.02))
    
# Assumptions
    on_premise.add_assumption("Hardware refresh cycle", "5 years")
    on_premise.add_assumption("Availability SLA", "99.5%")
    on_premise.add_assumption("Peak capacity utilization", "60%")
    
# Option 2: Cloud Deployment
    cloud = TCOCalculator("Cloud Deployment (AWS)", time_horizon_years=5)
    
# Capital costs (minimal)
    cloud.add_cost(CostComponent("Migration Costs", "capital", 50000, "one-time"))
    cloud.add_cost(CostComponent("Training", "capital", 20000, "one-time"))
    
# Operational costs
    cloud.add_cost(CostComponent("EC2 Instances", "operational", 0.50, "hourly", 0.0))  # ~20 instances
    cloud.add_cost(CostComponent("RDS Database", "operational", 0.30, "hourly", 0.0))  # Multi-AZ
    cloud.add_cost(CostComponent("S3 Storage", "operational", 2000, "monthly", 0.10))
    cloud.add_cost(CostComponent("Data Transfer", "operational", 3000, "monthly", 0.15))
    cloud.add_cost(CostComponent("CloudWatch/Monitoring", "operational", 500, "monthly", 0.05))
    cloud.add_cost(CostComponent("Support Plan", "operational", 5000, "monthly", 0.0))
    
# Hidden costs
    cloud.add_cost(CostComponent("Cloud Engineers (1 FTE)", "hidden", 120000, "yearly", 0.04))
    cloud.add_cost(CostComponent("Cost Optimization", "hidden", 1000, "monthly", 0.0))
    cloud.add_cost(CostComponent("Compliance Tools", "hidden", 15000, "yearly", 0.05))
    cloud.add_cost(CostComponent("Multi-Region DR", "hidden", 2000, "monthly", 0.10))
    
# Assumptions
    cloud.add_assumption("Reserved Instance discount", "30%")
    cloud.add_assumption("Availability SLA", "99.95%")
    cloud.add_assumption("Auto-scaling enabled", "Yes")
    
# Generate reports
    print(on_premise.generate_report())
    print("\n" + "="*70 + "\n")
    print(cloud.generate_report())
    
# Visualize both
    on_premise.visualize_costs()
    cloud.visualize_costs()
    
# Direct comparison
    on_premise_tco = on_premise.calculate_tco()['total']
    cloud_tco = cloud.calculate_tco()['total']
    
    print(f"\n{'='*50}")
    print("COMPARISON SUMMARY")
    print(f"{'='*50}")
    print(f"On-Premise TCO: ${on_premise_tco:,.2f}")
    print(f"Cloud TCO: ${cloud_tco:,.2f}")
    print(f"Difference: ${abs(on_premise_tco - cloud_tco):,.2f} ({abs(on_premise_tco - cloud_tco)/on_premise_tco*100:.1f}%)")
    print(f"Recommendation: {'Cloud' if cloud_tco < on_premise_tco else 'On-Premise'} is more cost-effective")

# Run the comparison
compare_deployment_options()
```

### Questions
1. What hidden costs are often overlooked in TCO calculations?
2. How does time horizon affect the TCO comparison?
3. What non-monetary factors should influence deployment decisions?

## Exercise 2: Build vs Buy Decision Framework

### Background
The build vs buy decision is one of the most critical economic choices in system design. This exercise creates a quantitative framework for making these decisions.

### Task
Develop a decision framework that considers all factors in build vs buy analysis.

```python
from enum import Enum
from typing import List, Dict, Optional, Tuple
import numpy as np

class Capability(Enum):
    CORE_DIFFERENTIATOR = "core_differentiator"
    SUPPORTING = "supporting"
    COMMODITY = "commodity"

@dataclass
class Feature:
    name: str
    importance: float  # 0-1 scale
    complexity: float  # 0-1 scale
    
@dataclass
class Solution:
    name: str
    type: str  # 'build' or 'buy'
    features: List[Feature]
    
class BuildVsBuyAnalyzer:
    """Comprehensive build vs buy decision framework"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.requirements = []
        self.build_factors = {}
        self.buy_options = []
        self.weights = {
            'cost': 0.25,
            'time': 0.20,
            'risk': 0.20,
            'control': 0.15,
            'flexibility': 0.10,
            'expertise': 0.10
        }
        
    def add_requirement(self, name: str, importance: float, complexity: float):
        """Add a functional requirement"""
        self.requirements.append(Feature(name, importance, complexity))
        
    def set_build_factors(self, 
                         team_size: int,
                         avg_salary: float,
                         months_to_build: float,
                         maintenance_percentage: float = 0.20):
        """Set factors for building in-house"""
        self.build_factors = {
            'team_size': team_size,
            'avg_salary': avg_salary,
            'months_to_build': months_to_build,
            'maintenance_percentage': maintenance_percentage
        }
        
    def add_buy_option(self, 
                      vendor: str,
                      license_cost: float,
                      implementation_months: float,
                      annual_support: float,
                      feature_coverage: Dict[str, float]):
        """Add a buy/vendor option"""
        self.buy_options.append({
            'vendor': vendor,
            'license_cost': license_cost,
            'implementation_months': implementation_months,
            'annual_support': annual_support,
            'feature_coverage': feature_coverage
        })
        
    def analyze(self, time_horizon_years: int = 3) -> Dict:
        """Perform comprehensive build vs buy analysis"""
        results = {
            'recommendation': '',
            'build_score': 0,
            'buy_scores': {},
            'detailed_analysis': {},
            'risk_factors': [],
            'decision_matrix': []
        }
        
# Analyze build option
        build_analysis = self._analyze_build_option(time_horizon_years)
        results['build_score'] = build_analysis['total_score']
        results['detailed_analysis']['build'] = build_analysis
        
# Analyze each buy option
        for option in self.buy_options:
            buy_analysis = self._analyze_buy_option(option, time_horizon_years)
            vendor = option['vendor']
            results['buy_scores'][vendor] = buy_analysis['total_score']
            results['detailed_analysis'][vendor] = buy_analysis
        
# Make recommendation
        all_scores = {'build': results['build_score']}
        all_scores.update(results['buy_scores'])
        best_option = max(all_scores, key=all_scores.get)
        results['recommendation'] = best_option
        
# Build decision matrix
        results['decision_matrix'] = self._build_decision_matrix(results['detailed_analysis'])
        
# Identify risk factors
        results['risk_factors'] = self._identify_risks(best_option, results['detailed_analysis'])
        
        return results
    
    def _analyze_build_option(self, years: int) -> Dict:
        """Analyze the build option"""
        analysis = {
            'total_cost': 0,
            'time_to_market': 0,
            'feature_fit': 0,
            'scores': {},
            'total_score': 0
        }
        
# Calculate costs
        build_cost = (self.build_factors['team_size'] * 
                     self.build_factors['avg_salary'] * 
                     self.build_factors['months_to_build'] / 12)
        
        maintenance_cost = (build_cost * self.build_factors['maintenance_percentage'] * years)
        
        analysis['total_cost'] = build_cost + maintenance_cost
        analysis['time_to_market'] = self.build_factors['months_to_build']
        analysis['feature_fit'] = 1.0  # Perfect fit when building
        
# Score each factor (0-100 scale)
        analysis['scores'] = {
            'cost': self._score_cost(analysis['total_cost'], years),
            'time': self._score_time(analysis['time_to_market']),
            'risk': self._score_build_risk(),
            'control': 95,  # High control when building
            'flexibility': 90,  # High flexibility
            'expertise': self._score_expertise_requirement('build')
        }
        
# Calculate weighted total
        analysis['total_score'] = sum(
            score * self.weights[factor]
            for factor, score in analysis['scores'].items()
        )
        
        return analysis
    
    def _analyze_buy_option(self, option: Dict, years: int) -> Dict:
        """Analyze a buy option"""
        analysis = {
            'total_cost': 0,
            'time_to_market': 0,
            'feature_fit': 0,
            'scores': {},
            'total_score': 0
        }
        
# Calculate costs
        total_cost = option['license_cost'] + (option['annual_support'] * years)
        analysis['total_cost'] = total_cost
        analysis['time_to_market'] = option['implementation_months']
        
# Calculate feature fit
        total_importance = sum(req.importance for req in self.requirements)
        covered_importance = sum(
            req.importance * option['feature_coverage'].get(req.name, 0)
            for req in self.requirements
        )
        analysis['feature_fit'] = covered_importance / total_importance if total_importance > 0 else 0
        
# Score each factor
        analysis['scores'] = {
            'cost': self._score_cost(analysis['total_cost'], years),
            'time': self._score_time(analysis['time_to_market']),
            'risk': self._score_vendor_risk(option),
            'control': 40,  # Limited control with vendor
            'flexibility': 50 * analysis['feature_fit'],  # Based on feature coverage
            'expertise': self._score_expertise_requirement('buy')
        }
        
# Calculate weighted total
        analysis['total_score'] = sum(
            score * self.weights[factor]
            for factor, score in analysis['scores'].items()
        )
        
        return analysis
    
    def _score_cost(self, cost: float, years: int) -> float:
        """Score cost factor (lower is better)"""
# Normalize against a baseline (e.g., $1M over time horizon)
        baseline = 1000000
        normalized = cost / baseline
        
# Inverse scoring - lower cost gets higher score
        if normalized <= 0.5:
            return 100
        elif normalized <= 1.0:
            return 80
        elif normalized <= 2.0:
            return 60
        elif normalized <= 3.0:
            return 40
        else:
            return 20
    
    def _score_time(self, months: float) -> float:
        """Score time to market (faster is better)"""
        if months <= 3:
            return 100
        elif months <= 6:
            return 80
        elif months <= 12:
            return 60
        elif months <= 18:
            return 40
        else:
            return 20
    
    def _score_build_risk(self) -> float:
        """Score risk of building in-house"""
# Consider team size, complexity, and track record
        base_score = 50
        
# Larger teams = more risk
        if self.build_factors['team_size'] > 10:
            base_score -= 10
        
# High complexity = more risk
        avg_complexity = np.mean([req.complexity for req in self.requirements])
        if avg_complexity > 0.7:
            base_score -= 20
        
        return max(20, base_score)
    
    def _score_vendor_risk(self, option: Dict) -> float:
        """Score vendor risk"""
        base_score = 70  # Vendors generally lower risk
        
# Adjust based on feature coverage
        coverage = sum(option['feature_coverage'].values()) / len(self.requirements)
        if coverage < 0.8:
            base_score -= 20
        
        return base_score
    
    def _score_expertise_requirement(self, approach: str) -> float:
        """Score based on expertise requirements"""
        if approach == 'build':
# Need specialized expertise
            avg_complexity = np.mean([req.complexity for req in self.requirements])
            if avg_complexity > 0.7:
                return 40  # Hard to find expertise
            else:
                return 70
        else:
            return 85  # Vendor handles expertise
    
    def _build_decision_matrix(self, analyses: Dict) -> List[Dict]:
        """Build decision matrix for visualization"""
        matrix = []
        
        for option, analysis in analyses.items():
            row = {
                'option': option,
                'total_cost': analysis['total_cost'],
                'time_months': analysis['time_to_market'],
                'feature_fit': analysis.get('feature_fit', 1.0) * 100,
                'total_score': analysis['total_score']
            }
            row.update(analysis['scores'])
            matrix.append(row)
        
        return matrix
    
    def _identify_risks(self, recommendation: str, analyses: Dict) -> List[str]:
        """Identify key risks with recommendation"""
        risks = []
        
        if recommendation == 'build':
            risks.append("Project delivery risk - building complex systems often takes longer than estimated")
            risks.append("Talent risk - need to maintain specialized team long-term")
            risks.append("Opportunity cost - team could work on core business features")
            
            avg_complexity = np.mean([req.complexity for req in self.requirements])
            if avg_complexity > 0.7:
                risks.append("Technical risk - high complexity increases failure probability")
        
        else:  # Buy option
            analysis = analyses[recommendation]
            if analysis.get('feature_fit', 0) < 0.8:
                risks.append("Feature gap risk - vendor doesn't cover all requirements")
            
            risks.append("Vendor lock-in risk - difficult to switch later")
            risks.append("Integration risk - may not fit perfectly with existing systems")
            risks.append("Support dependency - reliant on vendor for critical issues")
        
        return risks
    
    def generate_report(self, time_horizon_years: int = 3) -> str:
        """Generate comprehensive decision report"""
        results = self.analyze(time_horizon_years)
        
        report = f"""
Build vs Buy Analysis: {self.project_name}
{'='*60}

RECOMMENDATION: {results['recommendation'].upper()}
Overall Score: {results['detailed_analysis'][results['recommendation']]['total_score']:.1f}/100

EXECUTIVE SUMMARY
-----------------
"""
# Summary comparison
        for option, score in [('build', results['build_score'])] + list(results['buy_scores'].items()):
            analysis = results['detailed_analysis'][option]
            report += f"\n{option.upper()}:"
            report += f"\n  Total Score: {score:.1f}/100"
            report += f"\n  Total Cost ({time_horizon_years}yr): ${analysis['total_cost']:,.0f}"
            report += f"\n  Time to Market: {analysis['time_to_market']:.1f} months"
            if 'feature_fit' in analysis:
                report += f"\n  Feature Coverage: {analysis['feature_fit']*100:.0f}%"
        
        report += f"""

DETAILED SCORING
----------------
Factor Weights: {', '.join(f'{k}={v:.0%}' for k,v in self.weights.items())}

"""
# Decision matrix
        report += f"{'Option':<15} {'Cost':<8} {'Time':<8} {'Risk':<8} {'Control':<10} {'Flex':<8} {'Expert':<8} {'TOTAL':<8}\n"
        report += "-" * 75 + "\n"
        
        for row in results['decision_matrix']:
            report += f"{row['option']:<15} "
            report += f"{row['cost']:<8.0f} "
            report += f"{row['time']:<8.0f} "
            report += f"{row['risk']:<8.0f} "
            report += f"{row['control']:<10.0f} "
            report += f"{row['flexibility']:<8.0f} "
            report += f"{row['expertise']:<8.0f} "
            report += f"{row['total_score']:<8.1f}\n"
        
        report += f"""

KEY RISKS
---------
"""
        for i, risk in enumerate(results['risk_factors'], 1):
            report += f"{i}. {risk}\n"
        
        report += f"""

REQUIREMENTS ANALYSIS
--------------------
Total Requirements: {len(self.requirements)}
Average Complexity: {np.mean([r.complexity for r in self.requirements]):.2f}
Average Importance: {np.mean([r.importance for r in self.requirements]):.2f}

Top Requirements by Importance:
"""
        sorted_reqs = sorted(self.requirements, key=lambda x: x.importance, reverse=True)
        for req in sorted_reqs[:5]:
            report += f"- {req.name} (Importance: {req.importance:.2f}, Complexity: {req.complexity:.2f})\n"
        
        return report

# Example: Authentication System Decision
def analyze_auth_system():
    """Analyze build vs buy for authentication system"""
    
    analyzer = BuildVsBuyAnalyzer("Authentication System")
    
# Define requirements (name, importance 0-1, complexity 0-1)
    analyzer.add_requirement("User Registration", 1.0, 0.3)
    analyzer.add_requirement("Login/Logout", 1.0, 0.2)
    analyzer.add_requirement("Password Reset", 0.9, 0.3)
    analyzer.add_requirement("Multi-Factor Auth", 0.9, 0.7)
    analyzer.add_requirement("Social Login", 0.7, 0.6)
    analyzer.add_requirement("Session Management", 1.0, 0.5)
    analyzer.add_requirement("Role-Based Access", 0.8, 0.6)
    analyzer.add_requirement("API Key Management", 0.6, 0.4)
    analyzer.add_requirement("Audit Logging", 0.7, 0.3)
    analyzer.add_requirement("SAML/SSO", 0.5, 0.8)
    
# Build option parameters
    analyzer.set_build_factors(
        team_size=3,
        avg_salary=150000,
        months_to_build=6,
        maintenance_percentage=0.25
    )
    
# Buy option 1: Auth0
    analyzer.add_buy_option(
        vendor="Auth0",
        license_cost=24000,  # Annual
        implementation_months=1,
        annual_support=24000,
        feature_coverage={
            "User Registration": 1.0,
            "Login/Logout": 1.0,
            "Password Reset": 1.0,
            "Multi-Factor Auth": 1.0,
            "Social Login": 1.0,
            "Session Management": 1.0,
            "Role-Based Access": 0.9,
            "API Key Management": 0.8,
            "Audit Logging": 0.9,
            "SAML/SSO": 1.0
        }
    )
    
# Buy option 2: Okta
    analyzer.add_buy_option(
        vendor="Okta",
        license_cost=36000,  # Annual
        implementation_months=2,
        annual_support=36000,
        feature_coverage={
            "User Registration": 1.0,
            "Login/Logout": 1.0,
            "Password Reset": 1.0,
            "Multi-Factor Auth": 1.0,
            "Social Login": 0.9,
            "Session Management": 1.0,
            "Role-Based Access": 1.0,
            "API Key Management": 0.7,
            "Audit Logging": 1.0,
            "SAML/SSO": 1.0
        }
    )
    
# Buy option 3: AWS Cognito
    analyzer.add_buy_option(
        vendor="AWS Cognito",
        license_cost=12000,  # Estimated annual
        implementation_months=1.5,
        annual_support=12000,
        feature_coverage={
            "User Registration": 1.0,
            "Login/Logout": 1.0,
            "Password Reset": 1.0,
            "Multi-Factor Auth": 0.9,
            "Social Login": 0.8,
            "Session Management": 0.9,
            "Role-Based Access": 0.7,
            "API Key Management": 0.6,
            "Audit Logging": 0.7,
            "SAML/SSO": 0.8
        }
    )
    
# Generate analysis
    print(analyzer.generate_report(time_horizon_years=3))
    
# Sensitivity analysis - what if we need it faster?
    analyzer.weights['time'] = 0.40  # Double the weight of time
    analyzer.weights['cost'] = 0.15  # Reduce cost weight
    
    print("\n" + "="*60)
    print("SENSITIVITY ANALYSIS: Time-Critical Scenario")
    print("="*60)
    print(analyzer.generate_report(time_horizon_years=3))

# Run the analysis
analyze_auth_system()
```

### Questions
1. How do different weight assignments change the recommendation?
2. What intangible factors are hard to quantify in this framework?
3. When should you revisit a build vs buy decision?

## Exercise 3: Cloud Cost Optimization Strategies

### Background
Cloud costs can spiral out of control without proper optimization. This exercise implements various cost optimization strategies and measures their impact.

### Task
Build a cloud cost optimizer that identifies and implements savings opportunities.

```python
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Optional

class CloudResource:
    def __init__(self, resource_id: str, resource_type: str, 
                 region: str, tags: Dict[str, str]):
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.region = region
        self.tags = tags
        self.metrics = {}
        self.cost_per_hour = 0
        
class EC2Instance(CloudResource):
    def __init__(self, instance_id: str, instance_type: str, 
                 region: str, tags: Dict, state: str = 'running'):
        super().__init__(instance_id, 'ec2', region, tags)
        self.instance_type = instance_type
        self.state = state
        self.launch_time = datetime.now() - timedelta(days=30)
        self.cpu_utilization = []
        self.network_in = []
        self.network_out = []
        
# Simplified pricing model
        self.on_demand_pricing = {
            't3.micro': 0.0104,
            't3.small': 0.0208,
            't3.medium': 0.0416,
            't3.large': 0.0832,
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            'm5.2xlarge': 0.384,
            'c5.large': 0.085,
            'c5.xlarge': 0.17,
            'r5.large': 0.126,
            'r5.xlarge': 0.252
        }
        
        self.cost_per_hour = self.on_demand_pricing.get(instance_type, 0.1)

class CloudCostOptimizer:
    """Comprehensive cloud cost optimization engine"""
    
    def __init__(self):
        self.resources = []
        self.optimization_results = []
        self.total_monthly_cost = 0
        self.potential_savings = 0
        
    def add_resource(self, resource: CloudResource):
        """Add a cloud resource to analyze"""
        self.resources.append(resource)
        
    def analyze_costs(self) -> Dict:
        """Analyze current costs and identify optimization opportunities"""
        results = {
            'current_monthly_cost': 0,
            'optimized_monthly_cost': 0,
            'monthly_savings': 0,
            'savings_percentage': 0,
            'recommendations': [],
            'cost_breakdown': {},
            'quick_wins': [],
            'long_term_optimizations': []
        }
        
# Calculate current costs
        for resource in self.resources:
            monthly_cost = resource.cost_per_hour * 24 * 30
            results['current_monthly_cost'] += monthly_cost
            
            resource_type = resource.resource_type
            if resource_type not in results['cost_breakdown']:
                results['cost_breakdown'][resource_type] = 0
            results['cost_breakdown'][resource_type] += monthly_cost
        
# Run optimization strategies
        self._optimize_ec2_instances(results)
        self._optimize_reserved_instances(results)
        self._optimize_spot_instances(results)
        self._optimize_auto_scaling(results)
        self._optimize_storage(results)
        self._optimize_data_transfer(results)
        self._identify_unused_resources(results)
        self._optimize_instance_families(results)
        
# Calculate savings
        results['optimized_monthly_cost'] = results['current_monthly_cost'] - results['monthly_savings']
        results['savings_percentage'] = (results['monthly_savings'] / results['current_monthly_cost'] * 100) if results['current_monthly_cost'] > 0 else 0
        
# Categorize recommendations
        for rec in results['recommendations']:
            if rec['implementation_effort'] == 'low' and rec['savings'] > 100:
                results['quick_wins'].append(rec)
            elif rec['savings'] > 1000:
                results['long_term_optimizations'].append(rec)
        
        return results
    
    def _optimize_ec2_instances(self, results: Dict):
        """Optimize EC2 instance sizing and types"""
        ec2_instances = [r for r in self.resources if isinstance(r, EC2Instance)]
        
        for instance in ec2_instances:
# Check for rightsizing opportunities
            if hasattr(instance, 'cpu_utilization') and instance.cpu_utilization:
                avg_cpu = np.mean(instance.cpu_utilization)
                
                if avg_cpu < 20:  # Underutilized
                    current_cost = instance.cost_per_hour * 24 * 30
                    
# Recommend smaller instance
                    if instance.instance_type.endswith('xlarge'):
                        new_type = instance.instance_type.replace('xlarge', 'large')
                        new_cost = instance.on_demand_pricing.get(new_type, 0) * 24 * 30
                    elif instance.instance_type.endswith('large'):
                        new_type = instance.instance_type.replace('large', 'medium')
                        new_cost = instance.on_demand_pricing.get(new_type, 0) * 24 * 30
                    else:
                        continue
                    
                    savings = current_cost - new_cost
                    if savings > 0:
                        results['monthly_savings'] += savings
                        results['recommendations'].append({
                            'resource': instance.resource_id,
                            'type': 'rightsizing',
                            'current': instance.instance_type,
                            'recommended': new_type,
                            'reason': f'Low CPU utilization ({avg_cpu:.1f}%)',
                            'savings': savings,
                            'implementation_effort': 'low'
                        })
                
                elif avg_cpu > 80:  # Over-utilized
                    results['recommendations'].append({
                        'resource': instance.resource_id,
                        'type': 'performance',
                        'current': instance.instance_type,
                        'reason': f'High CPU utilization ({avg_cpu:.1f}%)',
                        'recommendation': 'Consider scaling up or out',
                        'savings': 0,
                        'implementation_effort': 'medium'
                    })
    
    def _optimize_reserved_instances(self, results: Dict):
        """Recommend reserved instance purchases"""
        ec2_instances = [r for r in self.resources if isinstance(r, EC2Instance)]
        
# Group by instance type and calculate steady-state usage
        instance_hours = {}
        for instance in ec2_instances:
            if instance.state == 'running':
                runtime = (datetime.now() - instance.launch_time).days
                if runtime > 30:  # Long-running instance
                    key = (instance.instance_type, instance.region)
                    if key not in instance_hours:
                        instance_hours[key] = 0
                    instance_hours[key] += 1
        
# Recommend RIs for steady-state workloads
        for (instance_type, region), count in instance_hours.items():
            if count >= 1:  # At least one long-running instance
                on_demand_cost = self._get_on_demand_price(instance_type) * 24 * 30 * count
                ri_cost = on_demand_cost * 0.6  # Assume 40% discount for 1-year RI
                
                monthly_savings = on_demand_cost - ri_cost
                results['monthly_savings'] += monthly_savings
                
                results['recommendations'].append({
                    'type': 'reserved_instance',
                    'instance_type': instance_type,
                    'region': region,
                    'count': count,
                    'monthly_on_demand': on_demand_cost,
                    'monthly_reserved': ri_cost,
                    'savings': monthly_savings,
                    'annual_savings': monthly_savings * 12,
                    'implementation_effort': 'low'
                })
    
    def _optimize_spot_instances(self, results: Dict):
        """Identify workloads suitable for spot instances"""
        ec2_instances = [r for r in self.resources if isinstance(r, EC2Instance)]
        
        for instance in ec2_instances:
# Check if workload is spot-suitable (based on tags)
            if instance.tags.get('workload-type') in ['batch', 'development', 'testing']:
                on_demand_cost = instance.cost_per_hour * 24 * 30
                spot_cost = on_demand_cost * 0.3  # Assume 70% discount
                
                savings = on_demand_cost - spot_cost
                results['monthly_savings'] += savings
                
                results['recommendations'].append({
                    'resource': instance.resource_id,
                    'type': 'spot_instance',
                    'workload': instance.tags.get('workload-type'),
                    'monthly_on_demand': on_demand_cost,
                    'monthly_spot': spot_cost,
                    'savings': savings,
                    'implementation_effort': 'medium'
                })
    
    def _optimize_auto_scaling(self, results: Dict):
        """Recommend auto-scaling configurations"""
        ec2_instances = [r for r in self.resources if isinstance(r, EC2Instance)]
        
# Group instances by application
        app_groups = {}
        for instance in ec2_instances:
            app = instance.tags.get('application', 'unknown')
            if app not in app_groups:
                app_groups[app] = []
            app_groups[app].append(instance)
        
# Check for scaling opportunities
        for app, instances in app_groups.items():
            if len(instances) > 2:  # Multiple instances of same app
# Simulate time-based usage pattern
                peak_hours = 8  # Business hours
                off_peak_hours = 16
                
                total_cost = sum(i.cost_per_hour * 24 * 30 for i in instances)
                
# With auto-scaling: run 50% capacity during off-peak
                auto_scale_cost = (
                    len(instances) * instances[0].cost_per_hour * peak_hours * 30 +
                    len(instances) * 0.5 * instances[0].cost_per_hour * off_peak_hours * 30
                )
                
                savings = total_cost - auto_scale_cost
                if savings > 0:
                    results['monthly_savings'] += savings
                    results['recommendations'].append({
                        'type': 'auto_scaling',
                        'application': app,
                        'current_instances': len(instances),
                        'recommendation': 'Implement time-based auto-scaling',
                        'peak_instances': len(instances),
                        'off_peak_instances': int(len(instances) * 0.5),
                        'savings': savings,
                        'implementation_effort': 'medium'
                    })
    
    def _identify_unused_resources(self, results: Dict):
        """Find and flag unused resources"""
        for resource in self.resources:
            if isinstance(resource, EC2Instance):
# Check if instance is stopped
                if resource.state == 'stopped':
                    stopped_days = (datetime.now() - resource.launch_time).days
                    if stopped_days > 7:
# EBS cost for stopped instance
                        ebs_cost = 0.10 * 100 / 30  # Assume 100GB EBS at $0.10/GB/month
                        daily_cost = ebs_cost
                        monthly_cost = daily_cost * 30
                        
                        results['monthly_savings'] += monthly_cost
                        results['recommendations'].append({
                            'resource': resource.resource_id,
                            'type': 'unused_resource',
                            'state': 'stopped',
                            'days_stopped': stopped_days,
                            'recommendation': 'Terminate or create AMI',
                            'savings': monthly_cost,
                            'implementation_effort': 'low'
                        })
                
# Check for low network activity (potential zombie)
                elif hasattr(resource, 'network_in') and resource.network_in:
                    avg_network = np.mean(resource.network_in + resource.network_out)
                    if avg_network < 1000:  # Less than 1KB/s average
                        monthly_cost = resource.cost_per_hour * 24 * 30
                        
                        results['recommendations'].append({
                            'resource': resource.resource_id,
                            'type': 'low_activity',
                            'network_avg_bytes': avg_network,
                            'recommendation': 'Investigate low network activity',
                            'potential_savings': monthly_cost,
                            'implementation_effort': 'low'
                        })
    
    def _optimize_storage(self, results: Dict):
        """Optimize storage costs"""
# Simulate storage optimization
        storage_recommendations = [
            {
                'type': 'storage_tiering',
                'current': 'EBS gp3',
                'recommended': 'EBS sc1',
                'use_case': 'Infrequent access data',
                'current_cost': 500,
                'optimized_cost': 125,
                'savings': 375,
                'implementation_effort': 'medium'
            },
            {
                'type': 'snapshot_lifecycle',
                'current_snapshots': 150,
                'recommended_retention': 30,
                'current_cost': 750,
                'optimized_cost': 150,
                'savings': 600,
                'implementation_effort': 'low'
            }
        ]
        
        for rec in storage_recommendations:
            results['monthly_savings'] += rec['savings']
            results['recommendations'].append(rec)
    
    def _optimize_data_transfer(self, results: Dict):
        """Optimize data transfer costs"""
# Simulate data transfer optimization
        transfer_optimization = {
            'type': 'data_transfer',
            'current_pattern': 'Cross-region replication',
            'recommendation': 'Use CloudFront for static content',
            'current_cost': 2000,
            'optimized_cost': 800,
            'savings': 1200,
            'implementation_effort': 'high'
        }
        
        results['monthly_savings'] += transfer_optimization['savings']
        results['recommendations'].append(transfer_optimization)
    
    def _optimize_instance_families(self, results: Dict):
        """Recommend newer instance families"""
        ec2_instances = [r for r in self.resources if isinstance(r, EC2Instance)]
        
# Map old to new instance families
        family_upgrades = {
            'm4': 'm5',
            'c4': 'c5',
            'r4': 'r5',
            't2': 't3'
        }
        
        for instance in ec2_instances:
            family = instance.instance_type.split('.')[0]
            if family in family_upgrades:
                new_family = family_upgrades[family]
                size = instance.instance_type.split('.')[1]
                new_type = f"{new_family}.{size}"
                
# Newer families are often 10-20% cheaper with better performance
                current_cost = instance.cost_per_hour * 24 * 30
                new_cost = current_cost * 0.85
                savings = current_cost - new_cost
                
                results['monthly_savings'] += savings
                results['recommendations'].append({
                    'resource': instance.resource_id,
                    'type': 'instance_family_upgrade',
                    'current': instance.instance_type,
                    'recommended': new_type,
                    'reason': 'Newer generation with better price/performance',
                    'savings': savings,
                    'implementation_effort': 'low'
                })
    
    def _get_on_demand_price(self, instance_type: str) -> float:
        """Get on-demand price for instance type"""
# Simplified pricing lookup
        prices = {
            't3.micro': 0.0104,
            't3.small': 0.0208,
            't3.medium': 0.0416,
            't3.large': 0.0832,
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            'c5.large': 0.085,
            'r5.large': 0.126
        }
        return prices.get(instance_type, 0.1)
    
    def generate_optimization_report(self) -> str:
        """Generate comprehensive optimization report"""
        results = self.analyze_costs()
        
        report = f"""
Cloud Cost Optimization Report
{'='*60}

EXECUTIVE SUMMARY
-----------------
Current Monthly Cost: ${results['current_monthly_cost']:,.2f}
Optimized Monthly Cost: ${results['optimized_monthly_cost']:,.2f}
Monthly Savings: ${results['monthly_savings']:,.2f}
Savings Percentage: {results['savings_percentage']:.1f}%
Annual Savings: ${results['monthly_savings'] * 12:,.2f}

COST BREAKDOWN
--------------
"""
        for resource_type, cost in results['cost_breakdown'].items():
            percentage = (cost / results['current_monthly_cost'] * 100) if results['current_monthly_cost'] > 0 else 0
            report += f"{resource_type}: ${cost:,.2f} ({percentage:.1f}%)\n"
        
        report += f"""

QUICK WINS (Low effort, immediate savings)
------------------------------------------
"""
        for rec in results['quick_wins']:
            report += f"\n{rec['type'].upper()}:"
            if 'resource' in rec:
                report += f"\n  Resource: {rec['resource']}"
            report += f"\n  Savings: ${rec['savings']:,.2f}/month"
            report += f"\n  Action: {rec.get('recommendation', rec.get('reason', ''))}"
        
        report += f"""

OPTIMIZATION RECOMMENDATIONS
----------------------------
"""
# Group by type
        by_type = {}
        for rec in results['recommendations']:
            rec_type = rec['type']
            if rec_type not in by_type:
                by_type[rec_type] = []
            by_type[rec_type].append(rec)
        
# Sort by total savings per type
        type_savings = {
            rec_type: sum(r['savings'] for r in recs)
            for rec_type, recs in by_type.items()
        }
        
        for rec_type in sorted(type_savings.keys(), key=lambda x: type_savings[x], reverse=True):
            recommendations = by_type[rec_type]
            total_savings = type_savings[rec_type]
            
            report += f"\n{rec_type.replace('_', ' ').upper()}"
            report += f"\nTotal Savings: ${total_savings:,.2f}/month\n"
            
            for rec in recommendations[:3]:  # Top 3 per category
                if rec_type == 'rightsizing':
                    report += f"  • {rec['resource']}: {rec['current']} → {rec['recommended']} (${rec['savings']:.2f}/mo)\n"
                elif rec_type == 'reserved_instance':
                    report += f"  • {rec['count']}x {rec['instance_type']} in {rec['region']} (${rec['savings']:.2f}/mo)\n"
                elif rec_type == 'spot_instance':
                    report += f"  • {rec['resource']}: {rec['workload']} workload (${rec['savings']:.2f}/mo)\n"
        
        report += f"""

IMPLEMENTATION ROADMAP
----------------------
"""
        effort_order = ['low', 'medium', 'high']
        for effort in effort_order:
            effort_recs = [r for r in results['recommendations'] if r['implementation_effort'] == effort]
            if effort_recs:
                total_savings = sum(r['savings'] for r in effort_recs)
                report += f"\n{effort.upper()} EFFORT: ${total_savings:,.2f}/month potential\n"
                report += f"  {len(effort_recs)} recommendations\n"
        
        return report

# Example: Analyze a sample infrastructure
def analyze_sample_infrastructure():
    """Create and analyze a sample cloud infrastructure"""
    
    optimizer = CloudCostOptimizer()
    
# Add production web servers
    for i in range(5):
        instance = EC2Instance(
            f"i-prod-web-{i}",
            "m5.large",
            "us-east-1",
            {"application": "web", "environment": "production"},
            "running"
        )
        instance.cpu_utilization = np.random.normal(15, 5, 100).tolist()  # Low utilization
        instance.network_in = np.random.normal(5000, 1000, 100).tolist()
        optimizer.add_resource(instance)
    
# Add API servers
    for i in range(3):
        instance = EC2Instance(
            f"i-prod-api-{i}",
            "c5.xlarge",
            "us-east-1",
            {"application": "api", "environment": "production"},
            "running"
        )
        instance.cpu_utilization = np.random.normal(60, 10, 100).tolist()  # Good utilization
        instance.network_in = np.random.normal(50000, 10000, 100).tolist()
        optimizer.add_resource(instance)
    
# Add batch processing (spot-eligible)
    for i in range(10):
        instance = EC2Instance(
            f"i-batch-{i}",
            "m5.2xlarge",
            "us-east-1",
            {"application": "batch", "workload-type": "batch"},
            "running"
        )
        instance.cpu_utilization = np.random.normal(70, 15, 100).tolist()
        optimizer.add_resource(instance)
    
# Add development instances (some stopped)
    for i in range(8):
        instance = EC2Instance(
            f"i-dev-{i}",
            "t3.large",
            "us-east-1",
            {"environment": "development", "workload-type": "development"},
            "stopped" if i > 4 else "running"
        )
        instance.launch_time = datetime.now() - timedelta(days=60)  # Old instances
        if instance.state == "running":
            instance.cpu_utilization = np.random.normal(5, 2, 100).tolist()  # Very low
            instance.network_in = np.random.normal(100, 50, 100).tolist()  # Minimal network
        optimizer.add_resource(instance)
    
# Add database instances (previous generation)
    for i in range(2):
        instance = EC2Instance(
            f"i-db-{i}",
            "r4.xlarge",  # Old generation
            "us-east-1",
            {"application": "database", "environment": "production"},
            "running"
        )
        instance.cpu_utilization = np.random.normal(40, 10, 100).tolist()
        optimizer.add_resource(instance)
    
# Generate and display report
    print(optimizer.generate_optimization_report())
    
# Calculate ROI
    results = optimizer.analyze_costs()
    implementation_cost = 10000  # Estimated cost to implement optimizations
    monthly_savings = results['monthly_savings']
    payback_months = implementation_cost / monthly_savings if monthly_savings > 0 else float('inf')
    
    print(f"\n{'='*60}")
    print("ROI ANALYSIS")
    print(f"{'='*60}")
    print(f"Implementation Cost: ${implementation_cost:,.2f}")
    print(f"Monthly Savings: ${monthly_savings:,.2f}")
    print(f"Payback Period: {payback_months:.1f} months")
    print(f"1-Year ROI: {((monthly_savings * 12 - implementation_cost) / implementation_cost * 100):.0f}%")

# Run the analysis
analyze_sample_infrastructure()
```

### Questions
1. Which optimization strategies provide the best ROI?
2. How do you balance cost optimization with performance requirements?
3. What are the risks of aggressive cost optimization?

## Exercise 4: Multi-Region Deployment Cost Analysis

### Background
Multi-region deployments provide resilience but significantly increase costs. This exercise analyzes the economic trade-offs.

### Task
Build a model to analyze costs and benefits of multi-region deployments.

```python
from enum import Enum
import networkx as nx
import matplotlib.pyplot as plt

class DeploymentStrategy(Enum):
    SINGLE_REGION = "single_region"
    ACTIVE_PASSIVE = "active_passive"
    ACTIVE_ACTIVE = "active_active"
    FOLLOW_THE_SUN = "follow_the_sun"

@dataclass
class Region:
    name: str
    code: str
    cost_multiplier: float  # Relative to baseline
    latency_to_users: Dict[str, float]  # Region -> latency ms
    data_transfer_cost: float  # $/GB

class MultiRegionAnalyzer:
    """Analyze costs and benefits of multi-region deployments"""
    
    def __init__(self, application_name: str):
        self.application_name = application_name
        self.regions = {}
        self.user_distribution = {}
        self.baseline_infrastructure = {}
        self.sla_requirements = {}
        
    def add_region(self, region: Region):
        """Add a region to consider"""
        self.regions[region.code] = region
        
    def set_user_distribution(self, distribution: Dict[str, float]):
        """Set percentage of users in each region"""
        self.user_distribution = distribution
        
    def set_baseline_infrastructure(self, 
                                  compute_units: int,
                                  storage_gb: int,
                                  bandwidth_gb_month: int):
        """Set baseline infrastructure requirements"""
        self.baseline_infrastructure = {
            'compute_units': compute_units,
            'storage_gb': storage_gb,
            'bandwidth_gb_month': bandwidth_gb_month
        }
        
    def set_sla_requirements(self,
                           availability_target: float,
                           max_latency_ms: float,
                           rpo_minutes: int,
                           rto_minutes: int):
        """Set SLA requirements"""
        self.sla_requirements = {
            'availability': availability_target,
            'max_latency': max_latency_ms,
            'rpo': rpo_minutes,
            'rto': rto_minutes
        }
        
    def analyze_deployment_strategies(self) -> Dict:
        """Analyze different deployment strategies"""
        results = {}
        
        strategies = [
            DeploymentStrategy.SINGLE_REGION,
            DeploymentStrategy.ACTIVE_PASSIVE,
            DeploymentStrategy.ACTIVE_ACTIVE,
            DeploymentStrategy.FOLLOW_THE_SUN
        ]
        
        for strategy in strategies:
            analysis = self._analyze_strategy(strategy)
            results[strategy.value] = analysis
            
# Add comparison
        results['comparison'] = self._compare_strategies(results)
        
        return results
    
    def _analyze_strategy(self, strategy: DeploymentStrategy) -> Dict:
        """Analyze a specific deployment strategy"""
        analysis = {
            'strategy': strategy.value,
            'regions_used': [],
            'monthly_cost': 0,
            'availability': 0,
            'average_latency': 0,
            'data_transfer_cost': 0,
            'complexity_score': 0,
            'meets_sla': False,
            'pros': [],
            'cons': [],
            'cost_breakdown': {}
        }
        
        if strategy == DeploymentStrategy.SINGLE_REGION:
# Pick optimal single region
            best_region = self._find_best_single_region()
            analysis['regions_used'] = [best_region]
            
# Calculate costs
            region = self.regions[best_region]
            base_cost = self._calculate_region_cost(region, 1.0)
            analysis['monthly_cost'] = base_cost
            analysis['cost_breakdown'] = {
                best_region: base_cost
            }
            
# Calculate metrics
            analysis['availability'] = 99.5  # Single region
            analysis['average_latency'] = self._calculate_average_latency([best_region])
            analysis['complexity_score'] = 1  # Simplest
            
# Pros/Cons
            analysis['pros'] = [
                "Lowest cost",
                "Simple architecture",
                "No data consistency issues"
            ]
            analysis['cons'] = [
                "Single point of failure",
                "High latency for distant users",
                "No disaster recovery"
            ]
            
        elif strategy == DeploymentStrategy.ACTIVE_PASSIVE:
# Primary + DR region
            primary = self._find_best_single_region()
            dr_region = self._find_dr_region(primary)
            analysis['regions_used'] = [primary, dr_region]
            
# Costs: Full in primary, 30% in DR
            primary_cost = self._calculate_region_cost(self.regions[primary], 1.0)
            dr_cost = self._calculate_region_cost(self.regions[dr_region], 0.3)
            replication_cost = self._calculate_replication_cost(primary, dr_region)
            
            analysis['monthly_cost'] = primary_cost + dr_cost + replication_cost
            analysis['data_transfer_cost'] = replication_cost
            analysis['cost_breakdown'] = {
                primary: primary_cost,
                dr_region: dr_cost,
                'replication': replication_cost
            }
            
# Metrics
            analysis['availability'] = 99.95  # With failover
            analysis['average_latency'] = self._calculate_average_latency([primary])
            analysis['complexity_score'] = 3
            
# Pros/Cons
            analysis['pros'] = [
                "Disaster recovery capability",
                "Improved availability",
                "Relatively simple failover"
            ]
            analysis['cons'] = [
                "Higher cost (30-40% more)",
                "DR resources mostly idle",
                "Failover causes downtime"
            ]
            
        elif strategy == DeploymentStrategy.ACTIVE_ACTIVE:
# Multiple active regions
            active_regions = self._select_active_regions()
            analysis['regions_used'] = active_regions
            
# Costs: Full deployment in each region
            total_cost = 0
            for region_code in active_regions:
                region = self.regions[region_code]
                region_cost = self._calculate_region_cost(region, 1.0)
                analysis['cost_breakdown'][region_code] = region_cost
                total_cost += region_cost
            
# Add inter-region replication
            replication_cost = self._calculate_mesh_replication_cost(active_regions)
            analysis['cost_breakdown']['replication'] = replication_cost
            total_cost += replication_cost
            
            analysis['monthly_cost'] = total_cost
            analysis['data_transfer_cost'] = replication_cost
            
# Metrics
            analysis['availability'] = 99.99  # High availability
            analysis['average_latency'] = self._calculate_average_latency(active_regions)
            analysis['complexity_score'] = 8
            
# Pros/Cons
            analysis['pros'] = [
                "Lowest latency globally",
                "Highest availability",
                "No single point of failure",
                "Load distribution"
            ]
            analysis['cons'] = [
                "Highest cost (2-3x)",
                "Complex data consistency",
                "Operational complexity",
                "Conflict resolution needed"
            ]
            
        elif strategy == DeploymentStrategy.FOLLOW_THE_SUN:
# Dynamic scaling by timezone
            all_regions = list(self.regions.keys())
            analysis['regions_used'] = all_regions
            
# Costs: Weighted by usage patterns
            total_cost = 0
            for region_code in all_regions:
                region = self.regions[region_code]
# Assume 8 hours peak per region
                usage_factor = 8/24
                region_cost = self._calculate_region_cost(region, usage_factor)
                analysis['cost_breakdown'][region_code] = region_cost
                total_cost += region_cost
            
# Minimal replication (config only)
            replication_cost = len(all_regions) * 100  # Nominal
            analysis['cost_breakdown']['replication'] = replication_cost
            total_cost += replication_cost
            
            analysis['monthly_cost'] = total_cost
            analysis['data_transfer_cost'] = replication_cost
            
# Metrics
            analysis['availability'] = 99.9
            analysis['average_latency'] = self._calculate_average_latency(all_regions)
            analysis['complexity_score'] = 6
            
# Pros/Cons
            analysis['pros'] = [
                "Cost efficient for global users",
                "Good latency during business hours",
                "Natural load distribution"
            ]
            analysis['cons'] = [
                "Complex orchestration",
                "Data locality challenges",
                "Requires stateless design"
            ]
        
# Check SLA compliance
        analysis['meets_sla'] = (
            analysis['availability'] >= self.sla_requirements['availability'] and
            analysis['average_latency'] <= self.sla_requirements['max_latency']
        )
        
        return analysis
    
    def _find_best_single_region(self) -> str:
        """Find optimal single region based on user distribution"""
        best_region = None
        best_score = float('inf')
        
        for region_code, region in self.regions.items():
            weighted_latency = 0
            for user_region, user_pct in self.user_distribution.items():
                latency = region.latency_to_users.get(user_region, 200)
                weighted_latency += latency * user_pct
                
# Consider cost as well
            cost_factor = region.cost_multiplier
            score = weighted_latency * cost_factor
            
            if score < best_score:
                best_score = score
                best_region = region_code
                
        return best_region
    
    def _find_dr_region(self, primary: str) -> str:
        """Find best DR region (different from primary)"""
        candidates = [r for r in self.regions.keys() if r != primary]
        
# Pick geographically diverse region with reasonable cost
# Simplified: just pick cheapest different region
        return min(candidates, 
                  key=lambda r: self.regions[r].cost_multiplier)
    
    def _select_active_regions(self) -> List[str]:
        """Select regions for active-active deployment"""
# Simple strategy: regions with >20% users
        selected = []
        for region_code in self.regions.keys():
            if self.user_distribution.get(region_code, 0) > 0.2:
                selected.append(region_code)
                
# Ensure at least 2 regions
        if len(selected) < 2:
            selected = list(self.regions.keys())[:2]
            
        return selected
    
    def _calculate_region_cost(self, region: Region, usage_factor: float) -> float:
        """Calculate monthly cost for a region"""
        base = self.baseline_infrastructure
        
# Compute cost (simplified)
        compute_cost = base['compute_units'] * 100 * region.cost_multiplier * usage_factor
        
# Storage cost
        storage_cost = base['storage_gb'] * 0.1 * region.cost_multiplier
        
# Bandwidth cost
        bandwidth_cost = base['bandwidth_gb_month'] * region.data_transfer_cost
        
        return compute_cost + storage_cost + bandwidth_cost
    
    def _calculate_replication_cost(self, source: str, dest: str) -> float:
        """Calculate replication cost between two regions"""
# Assume 10% of storage changes monthly
        change_rate = 0.1
        data_gb = self.baseline_infrastructure['storage_gb'] * change_rate
        
# Use source region's data transfer cost
        transfer_cost = self.regions[source].data_transfer_cost
        
        return data_gb * transfer_cost
    
    def _calculate_mesh_replication_cost(self, regions: List[str]) -> float:
        """Calculate full mesh replication cost"""
        total_cost = 0
        
        for i, source in enumerate(regions):
            for j, dest in enumerate(regions):
                if i != j:
                    total_cost += self._calculate_replication_cost(source, dest)
                    
        return total_cost
    
    def _calculate_average_latency(self, deployed_regions: List[str]) -> float:
        """Calculate weighted average latency"""
        total_weighted_latency = 0
        
        for user_region, user_pct in self.user_distribution.items():
# Find closest deployed region
            min_latency = float('inf')
            for deployed in deployed_regions:
                latency = self.regions[deployed].latency_to_users.get(user_region, 200)
                min_latency = min(min_latency, latency)
                
            total_weighted_latency += min_latency * user_pct
            
        return total_weighted_latency
    
    def _compare_strategies(self, results: Dict) -> Dict:
        """Compare all strategies"""
        comparison = {
            'cost_ranking': [],
            'latency_ranking': [],
            'availability_ranking': [],
            'complexity_ranking': [],
            'sla_compliant': [],
            'recommendations': []
        }
        
# Extract strategies (skip 'comparison' key)
        strategies = [k for k in results.keys() if k != 'comparison']
        
# Rank by different metrics
        comparison['cost_ranking'] = sorted(
            strategies,
            key=lambda s: results[s]['monthly_cost']
        )
        
        comparison['latency_ranking'] = sorted(
            strategies,
            key=lambda s: results[s]['average_latency']
        )
        
        comparison['availability_ranking'] = sorted(
            strategies,
            key=lambda s: results[s]['availability'],
            reverse=True
        )
        
        comparison['complexity_ranking'] = sorted(
            strategies,
            key=lambda s: results[s]['complexity_score']
        )
        
# SLA compliant strategies
        comparison['sla_compliant'] = [
            s for s in strategies if results[s]['meets_sla']
        ]
        
# Recommendations based on different priorities
        if comparison['sla_compliant']:
# If SLA is priority, pick cheapest compliant option
            comparison['recommendations'].append({
                'priority': 'SLA Compliance + Cost',
                'recommendation': min(
                    comparison['sla_compliant'],
                    key=lambda s: results[s]['monthly_cost']
                )
            })
        
        comparison['recommendations'].extend([
            {
                'priority': 'Minimum Cost',
                'recommendation': comparison['cost_ranking'][0]
            },
            {
                'priority': 'Best Performance',
                'recommendation': comparison['latency_ranking'][0]
            },
            {
                'priority': 'Maximum Availability',
                'recommendation': comparison['availability_ranking'][0]
            },
            {
                'priority': 'Simplicity',
                'recommendation': comparison['complexity_ranking'][0]
            }
        ])
        
        return comparison
    
    def visualize_deployment_costs(self, results: Dict):
        """Visualize deployment strategies and costs"""
        strategies = [k for k in results.keys() if k != 'comparison']
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Multi-Region Deployment Analysis: {self.application_name}', fontsize=16)
        
# 1. Cost comparison
        costs = [results[s]['monthly_cost'] for s in strategies]
        strategy_names = [s.replace('_', ' ').title() for s in strategies]
        
        ax1.bar(strategy_names, costs)
        ax1.set_title('Monthly Cost by Strategy')
        ax1.set_ylabel('Cost ($)')
        ax1.tick_params(axis='x', rotation=45)
        
# 2. Latency vs Cost scatter
        latencies = [results[s]['average_latency'] for s in strategies]
        
        ax2.scatter(costs, latencies, s=100)
        for i, name in enumerate(strategy_names):
            ax2.annotate(name, (costs[i], latencies[i]), fontsize=8)
        ax2.set_xlabel('Monthly Cost ($)')
        ax2.set_ylabel('Average Latency (ms)')
        ax2.set_title('Cost vs Performance Trade-off')
        
# 3. Availability comparison
        availabilities = [results[s]['availability'] for s in strategies]
        
        ax3.barh(strategy_names, availabilities)
        ax3.set_xlabel('Availability (%)')
        ax3.set_title('Availability by Strategy')
        ax3.set_xlim(99, 100)
        
# 4. Cost breakdown for most expensive strategy
        most_expensive = max(strategies, key=lambda s: results[s]['monthly_cost'])
        breakdown = results[most_expensive]['cost_breakdown']
        
        labels = list(breakdown.keys())
        values = list(breakdown.values())
        
        ax4.pie(values, labels=labels, autopct='%1.1f%%')
        ax4.set_title(f'Cost Breakdown: {most_expensive.replace("_", " ").title()}')
        
        plt.tight_layout()
        plt.show()
        
    def generate_deployment_report(self) -> str:
        """Generate comprehensive deployment analysis report"""
        results = self.analyze_deployment_strategies()
        
        report = f"""
Multi-Region Deployment Analysis: {self.application_name}
{'='*70}

BASELINE REQUIREMENTS
--------------------
Compute Units: {self.baseline_infrastructure['compute_units']}
Storage: {self.baseline_infrastructure['storage_gb']} GB
Bandwidth: {self.baseline_infrastructure['bandwidth_gb_month']} GB/month

SLA REQUIREMENTS
----------------
Availability Target: {self.sla_requirements['availability']}%
Maximum Latency: {self.sla_requirements['max_latency']} ms
RPO: {self.sla_requirements['rpo']} minutes
RTO: {self.sla_requirements['rto']} minutes

USER DISTRIBUTION
-----------------
"""
        for region, pct in self.user_distribution.items():
            report += f"{region}: {pct*100:.0f}%\n"
        
        report += f"""

STRATEGY ANALYSIS
-----------------
"""
        
        strategies = [k for k in results.keys() if k != 'comparison']
        
        for strategy in strategies:
            analysis = results[strategy]
            report += f"\n{strategy.replace('_', ' ').upper()}"
            report += f"\nRegions: {', '.join(analysis['regions_used'])}"
            report += f"\nMonthly Cost: ${analysis['monthly_cost']:,.2f}"
            report += f"\nAvailability: {analysis['availability']}%"
            report += f"\nAverage Latency: {analysis['average_latency']:.0f} ms"
            report += f"\nComplexity Score: {analysis['complexity_score']}/10"
            report += f"\nMeets SLA: {'YES' if analysis['meets_sla'] else 'NO'}"
            
            report += f"\n\nPros:"
            for pro in analysis['pros']:
                report += f"\n  + {pro}"
                
            report += f"\n\nCons:"
            for con in analysis['cons']:
                report += f"\n  - {con}"
                
            report += f"\n\n{'─'*50}"
        
        comparison = results['comparison']
        
        report += f"""

RECOMMENDATIONS
---------------
"""
        for rec in comparison['recommendations']:
            strategy = results[rec['recommendation']]
            report += f"\nIf {rec['priority']} is priority:"
            report += f"\n  → {rec['recommendation'].replace('_', ' ').title()}"
            report += f"\n  Cost: ${strategy['monthly_cost']:,.2f}/month"
            report += f"\n  Latency: {strategy['average_latency']:.0f} ms"
            report += f"\n  Availability: {strategy['availability']}%"
        
# ROI calculation for moving from single to multi-region
        single_cost = results['single_region']['monthly_cost']
        
        report += f"""

ROI ANALYSIS
------------
"""
        for strategy in strategies:
            if strategy != 'single_region':
                strat_cost = results[strategy]['monthly_cost']
                additional_cost = strat_cost - single_cost
                availability_gain = results[strategy]['availability'] - results['single_region']['availability']
                
                report += f"\n{strategy.replace('_', ' ').title()}:"
                report += f"\n  Additional Cost: ${additional_cost:,.2f}/month ({(additional_cost/single_cost*100):.0f}% increase)"
                report += f"\n  Availability Gain: {availability_gain:.2f}%"
                
# Estimate downtime cost (simplified)
                downtime_hours_saved = (availability_gain / 100) * 24 * 30
                downtime_cost_per_hour = 10000  # Example
                savings = downtime_hours_saved * downtime_cost_per_hour
                
                report += f"\n  Estimated Downtime Savings: ${savings:,.2f}/month"
                report += f"\n  Net Value: ${savings - additional_cost:,.2f}/month"
        
        return report

# Example: E-commerce platform multi-region analysis
def analyze_ecommerce_deployment():
    """Analyze multi-region deployment for global e-commerce"""
    
    analyzer = MultiRegionAnalyzer("Global E-commerce Platform")
    
# Define regions with costs and latencies
    regions = [
        Region("US East", "us-east-1", 1.0, {
            "us-east-1": 10, "us-west-1": 60, "eu-west-1": 80, 
            "ap-southeast-1": 200, "ap-northeast-1": 180
        }, 0.09),
        
        Region("US West", "us-west-1", 1.1, {
            "us-east-1": 60, "us-west-1": 10, "eu-west-1": 140,
            "ap-southeast-1": 150, "ap-northeast-1": 120
        }, 0.09),
        
        Region("EU West", "eu-west-1", 1.15, {
            "us-east-1": 80, "us-west-1": 140, "eu-west-1": 10,
            "ap-southeast-1": 180, "ap-northeast-1": 220
        }, 0.09),
        
        Region("Asia Pacific SE", "ap-southeast-1", 1.2, {
            "us-east-1": 200, "us-west-1": 150, "eu-west-1": 180,
            "ap-southeast-1": 10, "ap-northeast-1": 60
        }, 0.12),
        
        Region("Asia Pacific NE", "ap-northeast-1", 1.25, {
            "us-east-1": 180, "us-west-1": 120, "eu-west-1": 220,
            "ap-southeast-1": 60, "ap-northeast-1": 10
        }, 0.12)
    ]
    
    for region in regions:
        analyzer.add_region(region)
    
# User distribution
    analyzer.set_user_distribution({
        "us-east-1": 0.25,
        "us-west-1": 0.15,
        "eu-west-1": 0.30,
        "ap-southeast-1": 0.15,
        "ap-northeast-1": 0.15
    })
    
# Infrastructure baseline
    analyzer.set_baseline_infrastructure(
        compute_units=50,  # Number of servers
        storage_gb=10000,  # 10TB
        bandwidth_gb_month=50000  # 50TB
    )
    
# SLA requirements
    analyzer.set_sla_requirements(
        availability_target=99.95,
        max_latency_ms=100,
        rpo_minutes=15,
        rto_minutes=30
    )
    
# Generate analysis
    print(analyzer.generate_deployment_report())
    
# Visualize results
    results = analyzer.analyze_deployment_strategies()
    analyzer.visualize_deployment_costs(results)

# Run the analysis
analyze_ecommerce_deployment()
```

### Questions
1. When does multi-region deployment become cost-effective?
2. How do you quantify the value of reduced latency?
3. What hidden costs exist in multi-region architectures?

## Exercise 5: Hidden Cost Discovery Tool

### Background
Hidden costs can represent 20-40% of total IT spend. This exercise builds tools to discover and quantify these costs.

### Task
Create a comprehensive hidden cost discovery and analysis tool.

```python
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime, timedelta

class HiddenCostCategory(Enum):
    HUMAN_CAPITAL = "human_capital"
    TECHNICAL_DEBT = "technical_debt"
    OPERATIONAL_OVERHEAD = "operational_overhead"
    OPPORTUNITY_COST = "opportunity_cost"
    RISK_RELATED = "risk_related"
    COMPLIANCE = "compliance"
    VENDOR_LOCK_IN = "vendor_lock_in"

@dataclass
class HiddenCost:
    name: str
    category: HiddenCostCategory
    monthly_impact: float
    confidence: float  # 0-1, how confident in the estimate
    detection_method: str
    remediation: str
    effort_to_fix: str  # 'low', 'medium', 'high'

class HiddenCostAnalyzer:
    """Discover and quantify hidden costs in distributed systems"""
    
    def __init__(self, organization_name: str):
        self.organization_name = organization_name
        self.discovered_costs = []
        self.metrics = {}
        self.team_data = {}
        self.system_data = {}
        
    def set_team_metrics(self,
                        team_size: int,
                        avg_salary: float,
                        on_call_hours_month: float,
                        incident_count_month: float,
                        avg_incident_duration_hours: float):
        """Set team-related metrics"""
        self.team_data = {
            'size': team_size,
            'avg_salary': avg_salary,
            'on_call_hours': on_call_hours_month,
            'incidents': incident_count_month,
            'incident_duration': avg_incident_duration_hours
        }
        
    def set_system_metrics(self,
                          services_count: int,
                          avg_service_age_years: float,
                          tech_stack_diversity: int,
                          deployment_frequency_month: float,
                          rollback_rate: float):
        """Set system-related metrics"""
        self.system_data = {
            'services': services_count,
            'avg_age': avg_service_age_years,
            'tech_diversity': tech_stack_diversity,
            'deployments': deployment_frequency_month,
            'rollback_rate': rollback_rate
        }
        
    def discover_all_hidden_costs(self) -> List[HiddenCost]:
        """Run all discovery methods"""
        self.discovered_costs = []
        
# Run all analyzers
        self._analyze_human_capital_costs()
        self._analyze_technical_debt_costs()
        self._analyze_operational_overhead()
        self._analyze_opportunity_costs()
        self._analyze_risk_costs()
        self._analyze_compliance_costs()
        self._analyze_vendor_lock_in_costs()
        
        return self.discovered_costs
    
    def _analyze_human_capital_costs(self):
        """Analyze hidden human capital costs"""
        
# 1. On-call burnout cost
        if self.team_data.get('on_call_hours', 0) > 40:
# Excessive on-call leads to turnover
            turnover_risk = min((self.team_data['on_call_hours'] - 40) / 100, 0.5)
            replacement_cost = self.team_data['avg_salary'] * 1.5  # 150% to replace
            monthly_impact = (replacement_cost * turnover_risk) / 12
            
            self.discovered_costs.append(HiddenCost(
                "On-call induced turnover risk",
                HiddenCostCategory.HUMAN_CAPITAL,
                monthly_impact,
                0.7,
                "High on-call hours correlate with turnover",
                "Implement on-call rotation and automation",
                "medium"
            ))
        
# 2. Context switching cost
        if self.system_data.get('services', 0) > self.team_data.get('size', 1) * 2:
# Too many services per person
            services_per_person = self.system_data['services'] / self.team_data['size']
            
# Estimate 15% productivity loss per service over 2
            productivity_loss = min((services_per_person - 2) * 0.15, 0.5)
            monthly_impact = (self.team_data['avg_salary'] * self.team_data['size'] / 12) * productivity_loss
            
            self.discovered_costs.append(HiddenCost(
                "Context switching overhead",
                HiddenCostCategory.HUMAN_CAPITAL,
                monthly_impact,
                0.8,
                f"{services_per_person:.1f} services per engineer",
                "Consolidate services or grow team",
                "high"
            ))
        
# 3. Incident fatigue cost
        incident_hours = self.team_data.get('incidents', 0) * self.team_data.get('incident_duration', 2)
        if incident_hours > 20:
# High incident load reduces productivity
            productivity_loss = min(incident_hours / 160, 0.3)  # Work hours in month
            monthly_impact = (self.team_data['avg_salary'] * self.team_data['size'] / 12) * productivity_loss
            
            self.discovered_costs.append(HiddenCost(
                "Incident response overhead",
                HiddenCostCategory.HUMAN_CAPITAL,
                monthly_impact,
                0.9,
                f"{incident_hours:.0f} hours/month on incidents",
                "Improve system reliability and automation",
                "medium"
            ))
        
# 4. Knowledge silo cost
        if self.team_data.get('size', 0) < self.system_data.get('tech_diversity', 0):
# More technologies than people = knowledge silos
            risk_factor = 0.3  # 30% productivity hit
            monthly_impact = (self.team_data['avg_salary'] * self.team_data['size'] / 12) * risk_factor
            
            self.discovered_costs.append(HiddenCost(
                "Knowledge silo risk",
                HiddenCostCategory.HUMAN_CAPITAL,
                monthly_impact,
                0.6,
                "More tech stacks than team members",
                "Standardize technology choices",
                "high"
            ))
    
    def _analyze_technical_debt_costs(self):
        """Analyze technical debt related costs"""
        
# 1. Legacy system maintenance
        if self.system_data.get('avg_age', 0) > 3:
# Older systems cost more to maintain
            age_factor = (self.system_data['avg_age'] - 3) * 0.2
            base_maintenance = self.team_data['avg_salary'] * self.team_data['size'] * 0.3 / 12
            monthly_impact = base_maintenance * age_factor
            
            self.discovered_costs.append(HiddenCost(
                "Legacy system maintenance overhead",
                HiddenCostCategory.TECHNICAL_DEBT,
                monthly_impact,
                0.8,
                f"Average system age: {self.system_data['avg_age']:.1f} years",
                "Modernization program",
                "high"
            ))
        
# 2. High rollback rate cost
        if self.system_data.get('rollback_rate', 0) > 0.1:
# Each rollback costs time and credibility
            rollback_cost = 5000  # Per rollback
            rollbacks_month = self.system_data['deployments'] * self.system_data['rollback_rate']
            monthly_impact = rollback_cost * rollbacks_month
            
            self.discovered_costs.append(HiddenCost(
                "Deployment quality issues",
                HiddenCostCategory.TECHNICAL_DEBT,
                monthly_impact,
                0.9,
                f"{self.system_data['rollback_rate']*100:.0f}% rollback rate",
                "Improve testing and staging environments",
                "medium"
            ))
        
# 3. Dependency update debt
# Assume 20% of services have outdated dependencies
        outdated_services = self.system_data.get('services', 0) * 0.2
        update_hours_per_service = 40
        hourly_rate = self.team_data.get('avg_salary', 100000) / 2080
        
# Spread over 6 months
        monthly_impact = (outdated_services * update_hours_per_service * hourly_rate) / 6
        
        self.discovered_costs.append(HiddenCost(
            "Dependency update backlog",
            HiddenCostCategory.TECHNICAL_DEBT,
            monthly_impact,
            0.7,
            "Estimated 20% services need updates",
            "Regular dependency update schedule",
            "medium"
        ))
    
    def _analyze_operational_overhead(self):
        """Analyze operational overhead costs"""
        
# 1. Manual processes cost
# Estimate based on deployment frequency
        if self.system_data.get('deployments', 0) > 20:
            manual_hours_per_deploy = 2
            deploys = self.system_data['deployments']
            hourly_rate = self.team_data.get('avg_salary', 100000) / 2080
            
            monthly_impact = manual_hours_per_deploy * deploys * hourly_rate
            
            self.discovered_costs.append(HiddenCost(
                "Manual deployment overhead",
                HiddenCostCategory.OPERATIONAL_OVERHEAD,
                monthly_impact,
                0.8,
                f"{deploys} manual deployments/month",
                "Implement CI/CD automation",
                "medium"
            ))
        
# 2. Monitoring blind spots
# Assume 30% of issues are discovered by users
        user_discovered_incidents = self.team_data.get('incidents', 0) * 0.3
        reputation_cost_per_incident = 2000
        
        monthly_impact = user_discovered_incidents * reputation_cost_per_incident
        
        self.discovered_costs.append(HiddenCost(
            "Insufficient monitoring coverage",
            HiddenCostCategory.OPERATIONAL_OVERHEAD,
            monthly_impact,
            0.6,
            "Users discovering issues before ops",
            "Comprehensive monitoring implementation",
            "low"
        ))
        
# 3. Communication overhead
        if self.team_data.get('size', 0) > 10:
# Communication overhead grows with team size
            overhead_factor = (self.team_data['size'] - 10) * 0.02
            base_salary = self.team_data['avg_salary'] * self.team_data['size'] / 12
            monthly_impact = base_salary * overhead_factor
            
            self.discovered_costs.append(HiddenCost(
                "Communication overhead",
                HiddenCostCategory.OPERATIONAL_OVERHEAD,
                monthly_impact,
                0.7,
                f"Team size: {self.team_data['size']}",
                "Improve team structure and tools",
                "medium"
            ))
    
    def _analyze_opportunity_costs(self):
        """Analyze opportunity costs"""
        
# 1. Feature velocity impact
# Time spent on operations vs features
        ops_percentage = 0.4  # Assume 40% on ops
        potential_feature_value = 50000  # Per month of eng time
        
        monthly_impact = self.team_data['size'] * potential_feature_value * ops_percentage
        
        self.discovered_costs.append(HiddenCost(
            "Feature development opportunity cost",
            HiddenCostCategory.OPPORTUNITY_COST,
            monthly_impact,
            0.5,
            "40% time on operations vs features",
            "Increase automation and reliability",
            "high"
        ))
        
# 2. Scaling limitations
        if self.system_data.get('services', 0) > 0:
# Monolithic architectures limit scaling
            monolith_factor = max(0, 1 - (self.system_data['services'] / 20))
            scaling_opportunity_loss = 20000 * monolith_factor
            
            if scaling_opportunity_loss > 0:
                self.discovered_costs.append(HiddenCost(
                    "Architectural scaling constraints",
                    HiddenCostCategory.OPPORTUNITY_COST,
                    scaling_opportunity_loss,
                    0.4,
                    "Architecture limits business growth",
                    "Microservices migration",
                    "high"
                ))
    
    def _analyze_risk_costs(self):
        """Analyze risk-related costs"""
        
# 1. Single points of failure
# Estimate based on system count
        spof_count = max(1, self.system_data.get('services', 0) / 5)
        downtime_cost_hour = 10000
        failure_probability = 0.01  # 1% per month
        downtime_hours = 2
        
        monthly_impact = spof_count * downtime_cost_hour * failure_probability * downtime_hours
        
        self.discovered_costs.append(HiddenCost(
            "Single point of failure risk",
            HiddenCostCategory.RISK_RELATED,
            monthly_impact,
            0.6,
            f"Estimated {spof_count:.0f} SPOFs",
            "Implement redundancy",
            "medium"
        ))
        
# 2. Security breach risk
# Based on age and complexity
        breach_probability = min(0.001 * self.system_data.get('avg_age', 1), 0.01)
        breach_cost = 500000
        
        monthly_impact = breach_cost * breach_probability
        
        self.discovered_costs.append(HiddenCost(
            "Security breach risk",
            HiddenCostCategory.RISK_RELATED,
            monthly_impact,
            0.5,
            "Aging systems increase breach risk",
            "Security audit and updates",
            "high"
        ))
        
# 3. Data loss risk
# Assume inadequate backups
        data_loss_probability = 0.001
        data_value = 1000000
        
        monthly_impact = data_value * data_loss_probability
        
        self.discovered_costs.append(HiddenCost(
            "Data loss risk",
            HiddenCostCategory.RISK_RELATED,
            monthly_impact,
            0.7,
            "Backup strategy gaps",
            "Comprehensive backup solution",
            "low"
        ))
    
    def _analyze_compliance_costs(self):
        """Analyze compliance-related costs"""
        
# 1. Audit preparation
        audit_hours_month = 40
        hourly_rate = self.team_data.get('avg_salary', 100000) / 2080
        
        monthly_impact = audit_hours_month * hourly_rate
        
        self.discovered_costs.append(HiddenCost(
            "Compliance audit overhead",
            HiddenCostCategory.COMPLIANCE,
            monthly_impact,
            0.9,
            "Manual audit preparation",
            "Automated compliance reporting",
            "medium"
        ))
        
# 2. GDPR/Privacy compliance
        privacy_engineer_allocation = 0.5  # Half an engineer
        monthly_impact = (self.team_data.get('avg_salary', 100000) / 12) * privacy_engineer_allocation
        
        self.discovered_costs.append(HiddenCost(
            "Privacy compliance overhead",
            HiddenCostCategory.COMPLIANCE,
            monthly_impact,
            0.8,
            "GDPR and privacy requirements",
            "Privacy-by-design architecture",
            "high"
        ))
    
    def _analyze_vendor_lock_in_costs(self):
        """Analyze vendor lock-in costs"""
        
# 1. Switching cost risk
# Assume 30% premium due to lock-in
        vendor_premium = 0.3
# Estimate current vendor costs
        estimated_vendor_costs = 20000  # Monthly
        
        monthly_impact = estimated_vendor_costs * vendor_premium
        
        self.discovered_costs.append(HiddenCost(
            "Vendor lock-in premium",
            HiddenCostCategory.VENDOR_LOCK_IN,
            monthly_impact,
            0.6,
            "Limited negotiation leverage",
            "Multi-vendor strategy",
            "high"
        ))
        
# 2. Migration complexity cost
# Future migration would be expensive
        migration_cost = 500000
        amortized_monthly = migration_cost / 60  # Over 5 years
        
        self.discovered_costs.append(HiddenCost(
            "Future migration complexity",
            HiddenCostCategory.VENDOR_LOCK_IN,
            amortized_monthly,
            0.5,
            "Proprietary technology dependencies",
            "Use open standards",
            "high"
        ))
    
    def generate_hidden_cost_report(self) -> str:
        """Generate comprehensive hidden cost report"""
        if not self.discovered_costs:
            self.discover_all_hidden_costs()
            
        total_hidden = sum(cost.monthly_impact for cost in self.discovered_costs)
        
        report = f"""
Hidden Cost Analysis: {self.organization_name}
{'='*60}

EXECUTIVE SUMMARY
-----------------
Total Hidden Costs Discovered: ${total_hidden:,.2f}/month
Annual Hidden Costs: ${total_hidden * 12:,.2f}

This represents costs not typically captured in standard budgets.

TEAM METRICS
------------
Team Size: {self.team_data.get('size', 'N/A')}
Average Salary: ${self.team_data.get('avg_salary', 0):,.0f}
On-call Hours/Month: {self.team_data.get('on_call_hours', 0):.0f}
Incidents/Month: {self.team_data.get('incidents', 0):.0f}

SYSTEM METRICS
--------------
Services Count: {self.system_data.get('services', 0)}
Average Age: {self.system_data.get('avg_age', 0):.1f} years
Tech Stack Count: {self.system_data.get('tech_diversity', 0)}
Deployments/Month: {self.system_data.get('deployments', 0):.0f}

HIDDEN COSTS BY CATEGORY
------------------------
"""
        
# Group by category
        by_category = {}
        for cost in self.discovered_costs:
            if cost.category not in by_category:
                by_category[cost.category] = []
            by_category[cost.category].append(cost)
        
# Sort categories by total impact
        category_totals = {
            cat: sum(c.monthly_impact for c in costs)
            for cat, costs in by_category.items()
        }
        
        for category in sorted(category_totals.keys(), 
                             key=lambda x: category_totals[x], 
                             reverse=True):
            
            costs = by_category[category]
            total = category_totals[category]
            
            report += f"\n{category.value.replace('_', ' ').upper()}"
            report += f"\nTotal: ${total:,.2f}/month\n"
            
            for cost in sorted(costs, key=lambda x: x.monthly_impact, reverse=True):
                report += f"\n  • {cost.name}"
                report += f"\n    Impact: ${cost.monthly_impact:,.2f}/month"
                report += f"\n    Confidence: {cost.confidence*100:.0f}%"
                report += f"\n    Detection: {cost.detection_method}"
                report += f"\n    Fix Effort: {cost.effort_to_fix}"
                report += f"\n    Remediation: {cost.remediation}\n"
        
# Prioritized action plan
        report += f"""

PRIORITIZED ACTION PLAN
-----------------------
Quick Wins (Low effort, high impact):
"""
        quick_wins = [c for c in self.discovered_costs 
                     if c.effort_to_fix == 'low' and c.monthly_impact > 1000]
        quick_wins.sort(key=lambda x: x.monthly_impact, reverse=True)
        
        total_quick_win_savings = sum(c.monthly_impact for c in quick_wins)
        
        for i, cost in enumerate(quick_wins[:5], 1):
            report += f"\n{i}. {cost.name}"
            report += f"\n   Savings: ${cost.monthly_impact:,.2f}/month"
            report += f"\n   Action: {cost.remediation}"
        
        report += f"\n\nTotal Quick Win Savings: ${total_quick_win_savings:,.2f}/month"
        
# Long-term initiatives
        report += f"""

Strategic Initiatives (High effort, high impact):
"""
        strategic = [c for c in self.discovered_costs 
                    if c.effort_to_fix == 'high' and c.monthly_impact > 5000]
        strategic.sort(key=lambda x: x.monthly_impact, reverse=True)
        
        for i, cost in enumerate(strategic[:5], 1):
            report += f"\n{i}. {cost.name}"
            report += f"\n   Savings: ${cost.monthly_impact:,.2f}/month"
            report += f"\n   Investment Required: {cost.remediation}"
        
# ROI calculations
        report += f"""

RETURN ON INVESTMENT
--------------------
"""
# Assume implementation costs
        quick_win_cost = 20000
        strategic_cost = 200000
        
        quick_win_roi_months = quick_win_cost / total_quick_win_savings if total_quick_win_savings > 0 else float('inf')
        
        report += f"Quick Wins Implementation: ${quick_win_cost:,.0f}"
        report += f"\nPayback Period: {quick_win_roi_months:.1f} months"
        report += f"\n1-Year ROI: {((total_quick_win_savings * 12 - quick_win_cost) / quick_win_cost * 100):.0f}%"
        
        return report
    
    def visualize_hidden_costs(self):
        """Visualize hidden cost analysis"""
        if not self.discovered_costs:
            self.discover_all_hidden_costs()
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Hidden Cost Analysis: {self.organization_name}', fontsize=16)
        
# 1. Costs by category (pie)
        by_category = {}
        for cost in self.discovered_costs:
            cat = cost.category.value
            if cat not in by_category:
                by_category[cat] = 0
            by_category[cat] += cost.monthly_impact
            
        ax1.pie(by_category.values(), labels=by_category.keys(), autopct='%1.1f%%')
        ax1.set_title('Hidden Costs by Category')
        
# 2. Top 10 hidden costs (bar)
        top_costs = sorted(self.discovered_costs, 
                          key=lambda x: x.monthly_impact, 
                          reverse=True)[:10]
        
        names = [c.name[:30] + '...' if len(c.name) > 30 else c.name 
                for c in top_costs]
        values = [c.monthly_impact for c in top_costs]
        
        ax2.barh(names, values)
        ax2.set_xlabel('Monthly Impact ($)')
        ax2.set_title('Top 10 Hidden Costs')
        
# 3. Confidence vs Impact scatter
        impacts = [c.monthly_impact for c in self.discovered_costs]
        confidences = [c.confidence for c in self.discovered_costs]
        colors = [c.category.value for c in self.discovered_costs]
        
        scatter = ax3.scatter(impacts, confidences, c=range(len(colors)), alpha=0.6)
        ax3.set_xlabel('Monthly Impact ($)')
        ax3.set_ylabel('Confidence Level')
        ax3.set_title('Cost Impact vs Confidence')
        ax3.grid(True, alpha=0.3)
        
# 4. Effort vs Savings
        effort_map = {'low': 1, 'medium': 2, 'high': 3}
        efforts = [effort_map[c.effort_to_fix] for c in self.discovered_costs]
        
        ax4.scatter(efforts, impacts, alpha=0.6)
        ax4.set_xticks([1, 2, 3])
        ax4.set_xticklabels(['Low', 'Medium', 'High'])
        ax4.set_xlabel('Implementation Effort')
        ax4.set_ylabel('Monthly Savings ($)')
        ax4.set_title('Effort vs Potential Savings')
        ax4.grid(True, alpha=0.3)
        
# Annotate quick wins
        for cost in self.discovered_costs:
            if cost.effort_to_fix == 'low' and cost.monthly_impact > 5000:
                effort = effort_map[cost.effort_to_fix]
                ax4.annotate(cost.name[:20], 
                           (effort, cost.monthly_impact),
                           fontsize=8)
        
        plt.tight_layout()
        plt.show()

# Example: Analyze hidden costs for a SaaS company
def analyze_saas_hidden_costs():
    """Analyze hidden costs for a typical SaaS company"""
    
    analyzer = HiddenCostAnalyzer("FastGrow SaaS Inc.")
    
# Set team metrics
    analyzer.set_team_metrics(
        team_size=15,
        avg_salary=120000,
        on_call_hours_month=60,  # High on-call burden
        incident_count_month=25,  # Many incidents
        avg_incident_duration_hours=2.5
    )
    
# Set system metrics
    analyzer.set_system_metrics(
        services_count=45,  # Many microservices
        avg_service_age_years=4.5,  # Aging systems
        tech_stack_diversity=12,  # Many technologies
        deployment_frequency_month=80,  # Frequent deployments
        rollback_rate=0.15  # High rollback rate
    )
    
# Discover and report hidden costs
    print(analyzer.generate_hidden_cost_report())
    
# Visualize findings
    analyzer.visualize_hidden_costs()
    
# Calculate total IT spend visibility
    visible_costs = 500000  # Monthly visible IT costs
    hidden_costs = sum(c.monthly_impact for c in analyzer.discovered_costs)
    
    print(f"\n{'='*60}")
    print("TOTAL IT SPEND ANALYSIS")
    print(f"{'='*60}")
    print(f"Visible Costs: ${visible_costs:,.2f}/month")
    print(f"Hidden Costs: ${hidden_costs:,.2f}/month")
    print(f"True Total: ${visible_costs + hidden_costs:,.2f}/month")
    print(f"Hidden Cost Percentage: {(hidden_costs/(visible_costs+hidden_costs)*100):.1f}%")

# Run the analysis
analyze_saas_hidden_costs()
```

### Questions
1. Which hidden costs are most often overlooked?
2. How do you build a culture of cost awareness?
3. What leading indicators predict future hidden costs?

## Summary

These exercises demonstrate practical approaches to implementing the Law of Economic Reality in distributed systems:

1. **TCO Calculation**: Look beyond purchase price to lifetime costs
2. **Build vs Buy**: Quantify all factors in the decision
3. **Cost Optimization**: Systematically identify and capture savings
4. **Multi-Region Analysis**: Balance cost with performance and availability
5. **Hidden Cost Discovery**: Uncover the 20-40% of costs that hide in operations

Remember: Every technical decision is an economic decision. The most elegant architecture that bankrupts the company is a failure. Success requires balancing technical excellence with economic sustainability.

## Next Steps

1. Apply TCO analysis to your next infrastructure decision
2. Audit your current systems for hidden costs
3. Implement cost visibility into your development process
4. Create cost optimization as a continuous practice
5. Educate your team on the economic impact of their decisions

The best engineers don't just build systems that work—they build systems that create business value sustainably.
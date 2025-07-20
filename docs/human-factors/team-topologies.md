# Team Topologies for Distributed Systems

**Organizing teams for effective distributed systems development**

> *"Conway's Law is not a suggestion—it's a force of nature. Design your teams to match your desired architecture."*

---

## Understanding Team Topologies

Team Topologies provides four fundamental team types and three interaction modes to help organizations design their team structures for fast flow of value.

## The Four Team Types

### 1. Stream-Aligned Teams
**Purpose**: Deliver value directly to customers or users

```yaml
stream_aligned_team:
  characteristics:
    - End-to-end ownership of a service/product
    - Direct customer/user feedback loop
    - Cross-functional capabilities
    - Autonomous decision-making
  
  size: 5-9 people
  
  responsibilities:
    - Feature development
    - Service operations
    - On-call rotation
    - Customer support escalations
  
  examples:
    - "Checkout Team" (owns entire checkout flow)
    - "Mobile App Team" (owns mobile experience)
    - "Search Team" (owns search functionality)
```

### 2. Platform Teams
**Purpose**: Enable stream-aligned teams to deliver value faster

```yaml
platform_team:
  characteristics:
    - Provides internal services
    - Focuses on developer experience
    - Abstracts infrastructure complexity
    - Self-service capabilities
  
  size: 5-9 people per platform area
  
  services_provided:
    - Deployment pipelines
    - Monitoring and observability
    - Database platforms
    - Message queuing systems
  
  success_metrics:
    - Time to deploy new service
    - Platform adoption rate
    - Developer satisfaction scores
```

### 3. Enabling Teams
**Purpose**: Help stream-aligned teams overcome obstacles

```yaml
enabling_team:
  characteristics:
    - Temporary engagements
    - Knowledge transfer focus
    - Coaching and mentoring
    - Research and experimentation
  
  size: 3-5 specialists
  
  engagement_types:
    - New technology adoption
    - Performance optimization
    - Security improvements
    - Architecture evolution
  
  duration: 3-6 months per engagement
```

### 4. Complicated Subsystem Teams
**Purpose**: Manage technically complex subsystems

```yaml
complicated_subsystem_team:
  characteristics:
    - Deep specialist knowledge
    - Complex domain expertise
    - Clear interface boundaries
    - Limited cognitive load on others
  
  examples:
    - Machine learning model team
    - Video encoding team
    - Cryptography team
    - Real-time analytics engine team
```

## Team Interaction Modes

### 1. Collaboration
- **When**: Exploring new territory
- **Duration**: Limited time (weeks to months)
- **Goal**: Discover boundaries and interfaces

### 2. X-as-a-Service
- **When**: Clear boundaries exist
- **Duration**: Ongoing
- **Goal**: Minimal cognitive load, clear APIs

### 3. Facilitating
- **When**: Capability gaps exist
- **Duration**: Temporary (months)
- **Goal**: Level up team capabilities

## Conway's Law and System Design

> "Organizations which design systems are constrained to produce designs which are copies of the communication structures of these organizations." - Melvin Conway

### Implications for Distributed Systems

```python
class ConwayAnalyzer:
    """Analyze alignment between teams and architecture"""
    
    def analyze_alignment(self, teams, services):
        misalignments = []
        
        # Check service ownership
        for service in services:
            owners = self.find_service_owners(service, teams)
            
            if len(owners) == 0:
                misalignments.append({
                    'type': 'orphaned_service',
                    'service': service.name,
                    'impact': 'No clear ownership'
                })
            elif len(owners) > 1:
                misalignments.append({
                    'type': 'shared_ownership',
                    'service': service.name,
                    'owners': [t.name for t in owners],
                    'impact': 'Coordination overhead'
                })
        
        # Check team dependencies
        for team in teams:
            dependencies = self.analyze_team_dependencies(team)
            
            if len(dependencies) > 5:
                misalignments.append({
                    'type': 'high_coupling',
                    'team': team.name,
                    'dependencies': len(dependencies),
                    'impact': 'Reduced autonomy'
                })
        
        return misalignments
```

## Cognitive Load Management

### Types of Cognitive Load

1. **Intrinsic**: Fundamental complexity of the problem
2. **Extraneous**: Unnecessary complexity from poor design
3. **Germane**: Good complexity that helps learning

### Managing Team Cognitive Load

```python
class CognitiveLoadCalculator:
    def calculate_team_load(self, team):
        load_factors = {
            'services_owned': len(team.services) * 10,
            'technologies': len(team.tech_stack) * 5,
            'external_dependencies': len(team.dependencies) * 3,
            'on_call_frequency': team.on_call_weeks_per_year * 2,
            'meeting_hours_per_week': team.meeting_hours * 1,
            'documentation_debt': team.outdated_docs_count * 2
        }
        
        total_load = sum(load_factors.values())
        
        # Threshold based on team size
        capacity = team.size * 50  # 50 points per person
        
        return {
            'total_load': total_load,
            'capacity': capacity,
            'utilization': total_load / capacity,
            'breakdown': load_factors,
            'recommendation': self.get_recommendation(total_load / capacity)
        }
    
    def get_recommendation(self, utilization):
        if utilization > 1.2:
            return "Critical: Reduce scope immediately"
        elif utilization > 1.0:
            return "Warning: Team is overloaded"
        elif utilization > 0.8:
            return "Healthy: Near capacity"
        elif utilization > 0.6:
            return "Good: Room for growth"
        else:
            return "Consider additional responsibilities"
```

## Platform Team Patterns

### Building Effective Platforms

```yaml
platform_evolution:
  stage_1_extraction:
    trigger: "Same solution built 3+ times"
    action: "Extract common functionality"
    team: "Initial platform engineers"
    
  stage_2_self_service:
    trigger: "Platform team becomes bottleneck"
    action: "Build self-service capabilities"
    focus: "Developer experience"
    
  stage_3_product:
    trigger: "Platform widely adopted"
    action: "Treat platform as internal product"
    metrics: "Adoption, satisfaction, reliability"
```

### Platform as a Product

```python
class PlatformProduct:
    def __init__(self):
        self.features = []
        self.users = []  # Stream-aligned teams
        self.metrics = PlatformMetrics()
    
    def measure_success(self):
        return {
            'adoption_rate': len(self.users) / total_teams,
            'self_service_rate': self.metrics.self_service_requests / total_requests,
            'time_to_value': self.metrics.avg_onboarding_time,
            'user_satisfaction': self.metrics.nps_score,
            'reliability': self.metrics.uptime
        }
    
    def prioritize_features(self):
        # Use same product management techniques
        # as external products
        return sorted(self.features, 
                     key=lambda f: f.user_value / f.effort,
                     reverse=True)
```

## Team API and Boundaries

### Defining Team APIs

```yaml
team_api:
  checkout_team:
    provides:
      - Service: "Checkout API"
        SLA: "99.9% uptime"
        Response_time: "<200ms p99"
      
      - Service: "Order Processing"
        SLA: "99.95% success rate"
        Processing_time: "<5 seconds"
    
    consumes:
      - "Inventory Service"
      - "Payment Service"
      - "User Service"
    
    communication:
      - sync: "Slack #checkout-team"
      - async: "checkout-team@company.com"
      - on_call: "PagerDuty checkout-team"
    
    working_agreements:
      - "2-week sprint cycles"
      - "Thursday deployments"
      - "API changes require 30-day notice"
```

## Organizational Evolution

### Scaling Patterns

```python
class OrganizationalScaling:
    def recommend_split(self, team):
        """Recommend when and how to split teams"""
        
        indicators = {
            'size': team.size > 9,
            'services': len(team.services) > 5,
            'meetings': team.coordination_meetings > 10/week,
            'delivery': team.cycle_time > 2 * historical_average,
            'conflicts': team.merge_conflicts > 20/week
        }
        
        if sum(indicators.values()) >= 3:
            # Recommend split
            return self.suggest_split_strategy(team)
        
        return None
    
    def suggest_split_strategy(self, team):
        # Analyze service dependencies
        clusters = self.find_service_clusters(team.services)
        
        return {
            'strategy': 'service_boundary_split',
            'new_teams': [
                {
                    'name': f"{team.name}-{cluster.domain}",
                    'services': cluster.services,
                    'size': self.calculate_team_size(cluster)
                }
                for cluster in clusters
            ]
        }
```

## Anti-Patterns to Avoid

### 1. Shared Services Team
**Problem**: Creates bottlenecks and reduces ownership
**Solution**: Embed capabilities in stream-aligned teams

### 2. Architecture Team
**Problem**: Ivory tower architecture disconnected from reality
**Solution**: Enabling team that coaches and facilitates

### 3. Dev vs Ops Split
**Problem**: Throws problems over the wall
**Solution**: Stream-aligned teams own their operations

### 4. Component Teams
**Problem**: Requires coordination for any feature
**Solution**: Reorganize around value streams

## Measuring Team Effectiveness

```python
class TeamEffectivenessMetrics:
    def calculate_team_metrics(self, team):
        return {
            'flow_metrics': {
                'deployment_frequency': self.get_deployment_frequency(team),
                'lead_time': self.get_lead_time(team),
                'mttr': self.get_mttr(team),
                'change_failure_rate': self.get_change_failure_rate(team)
            },
            'team_health': {
                'psychological_safety': self.survey_score(team, 'safety'),
                'clarity': self.survey_score(team, 'role_clarity'),
                'autonomy': self.survey_score(team, 'decision_autonomy'),
                'mastery': self.survey_score(team, 'skill_growth'),
                'purpose': self.survey_score(team, 'mission_alignment')
            },
            'collaboration': {
                'dependencies': len(team.external_dependencies),
                'waiting_time': self.get_average_wait_time(team),
                'handoffs': self.count_handoffs(team)
            }
        }
```

## Case Study: Distributed System Team Design

### Before: Component Teams
```
Frontend Team → API Team → Backend Team → Database Team
(Each feature requires coordination across all teams)
```

### After: Stream-Aligned Teams
```
Checkout Team (owns entire checkout flow)
├── Frontend components
├── API endpoints
├── Business logic
├── Database schemas
└── Operations/monitoring

Search Team (owns search functionality)
├── Search UI
├── Search API
├── Indexing service
├── Search database
└── Relevance tuning
```

### Results
- 75% reduction in coordination meetings
- 60% faster feature delivery
- 90% reduction in cross-team dependencies
- 50% improvement in system reliability

---

<div class="navigation-footer">
<div class="pattern-relationships">
<h3>🔗 Related Concepts</h3>

**🤝 Related Topics**:
- [On-Call Culture](/human-factors/oncall-culture/) - Team operational responsibilities
- [Knowledge Management](/human-factors/knowledge-management/) - Sharing across teams
- [SRE Practices](/human-factors/sre-practices/) - Operational excellence

**🧠 Foundational Concepts**:
- [Axiom 7: Human Interface](/part1-axioms/axiom7-human-interface/) - Human factors
- [Control Pillar](/part2-pillars/control/) - System organization
</div>
</div>

---

*"Show me your org chart and I'll show you your architecture—it's Conway's Law in action."*
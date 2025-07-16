# Human Interface Exercises

!!! info "Prerequisites"
    - Completed [Human Interface Concepts](index.md)
    - Reviewed [Human Interface Examples](examples.md)
    - Access to a development environment

!!! tip "Quick Navigation"
    [← Examples](examples.md) | 
    [↑ Axioms Overview](../index.md) |
    [→ Next: Economics](../axiom-8-economics/index.md)

## Exercise 1: Design an Incident Dashboard

### Objective
Create a dashboard that helps operators quickly understand and respond to incidents.

### Requirements
```yaml
Must show:
- System health at a glance
- Active incidents with severity
- Recent changes that might be related
- Key business metrics impact
- Team status (who's on-call)

Constraints:
- Fits on one screen (no scrolling)
- Works on mobile for on-call
- Updates real-time
- Colorblind accessible
```

### Starter Template
```html
<!DOCTYPE html>
<html>
<head>
    <title>Incident Dashboard</title>
    <style>
        /* Design your layout here */
        .health-indicator {
            /* Visual health status */
        }
        .incident-card {
            /* Individual incident display */
        }
        /* Add more styles */
    </style>
</head>
<body>
    <div id="dashboard">
        <!-- Build your dashboard here -->
    </div>
    <script>
        // Add real-time updates
    </script>
</body>
</html>
```

### Evaluation Criteria
- Information hierarchy clear?
- Critical info visible immediately?
- Actions obvious and accessible?
- Works under stress test?

## Exercise 2: Improve a Configuration File

### Objective
Transform a confusing configuration into a human-friendly version.

### The Bad Configuration
```yaml
# Current production config (DO NOT COPY)
svc:
  p: 8080
  w: 100
  t: 30
  r: 3
  b: 1000
  m: 512
  x: true
  q: 
    s: 10000
    c: 5
    t: 60
  db:
    h: db.prod.internal
    p: 5432
    n: app_prod
    c: 50
    t: 5
```

### Your Task
1. Add meaningful names
2. Add documentation
3. Add validation rules
4. Add safe defaults
5. Group related settings
6. Add examples

### Solution Framework
```yaml
# Service Configuration
# Generated: 2024-01-15
# Environment: production

service:
  # Network settings
  network:
    port: 8080  # API port (default: 8080, range: 1024-65535)
    # Add more...

  # Performance settings
  performance:
    workers: 100  # Worker threads
    # WARNING: Each worker uses ~50MB RAM
    # Recommended: 2 × CPU cores
    # Add more...

# Continue restructuring...
```

## Exercise 3: Create an Alert Template

### Objective
Design an alert format that provides context and actionable information.

### Current Alert (Bad)
```
Subject: ERROR
database connection failed
```

### Your Task
Create a template that includes:
1. Clear severity indicator
2. Affected service/component
3. Impact assessment
4. Recent related events
5. Suggested actions
6. Relevant links

### Template Structure
```python
class Alert:
    def __init__(self):
        self.severity = None  # P1-P4
        self.title = None
        self.service = None
        self.impact = None
        self.context = []
        self.actions = []
        self.links = []
    
    def format_alert(self):
        # Build your alert format
        pass

# Example usage:
alert = Alert()
alert.severity = "P2"
alert.title = "Database connection pool exhausted"
# ... populate other fields
print(alert.format_alert())
```

## Exercise 4: Build a Deployment Safety Check

### Objective
Create a pre-deployment checklist that prevents common human errors.

### Requirements
The tool should check:
1. Current system health
2. Recent incidents
3. Deployment time appropriateness
4. Change size/risk assessment
5. Rollback plan existence
6. Team availability

### Starter Code
```python
class DeploymentSafetyCheck:
    def __init__(self, deployment_config):
        self.config = deployment_config
        self.checks = []
        
    def check_system_health(self):
        """Verify system is healthy before deployment"""
        # Implement health check
        pass
        
    def check_deployment_window(self):
        """Ensure we're not deploying at a bad time"""
        # Check business hours, holidays, etc.
        pass
        
    def check_change_size(self):
        """Assess risk based on change size"""
        # Lines changed, files affected, etc.
        pass
        
    def run_all_checks(self):
        """Run all safety checks"""
        # Return go/no-go decision with reasons
        pass

# Usage:
checker = DeploymentSafetyCheck(config)
result = checker.run_all_checks()
if result.safe_to_deploy:
    print("✅ Safe to deploy")
else:
    print(f"❌ Deployment blocked: {result.reasons}")
```

## Exercise 5: Design a Runbook Format

### Objective
Create a runbook template that's actually useful during incidents.

### Requirements
- Scannable under pressure
- Clear decision trees
- Copy-paste commands
- Expected outcomes
- Escalation paths

### Bad Runbook Example
```
When the service is down, check if it's running and if not, restart it.
If that doesn't work, check the logs. If you see errors, try to fix them.
If you can't fix them, escalate to the on-call engineer.
```

### Create Your Template
```markdown
# Runbook: [Service Name] Down

## Quick Status Check
```bash
# Copy-paste this block:
systemctl status myservice
curl -f http://localhost:8080/health || echo "Health check failed"
```

## Decision Tree
```
Service status shows "active"?
├─ YES → Check health endpoint
│   ├─ Returns 200 → Check dependencies
│   └─ Returns error → Go to "Health Check Failures"
└─ NO → Go to "Service Not Running"
```

## Common Scenarios

### Scenario 1: Service Not Running
Symptoms:
- systemctl shows "inactive" or "failed"

Actions:
1. Check recent logs:
   ```bash
   journalctl -u myservice -n 100
   ```

2. [Continue building template...]
```

## Exercise 6: Implement Progressive Disclosure

### Objective
Build a UI component that reveals complexity gradually.

### Example: System Metrics Display
```javascript
class MetricsDisplay {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.detailLevel = 'summary'; // summary, detailed, expert
    }
    
    renderSummary() {
        return `
            <div class="metrics-summary">
                <h2>System Health: ${this.getOverallHealth()}</h2>
                <button onclick="showDetails()">Show Details</button>
            </div>
        `;
    }
    
    renderDetailed() {
        // Show subsystem health
    }
    
    renderExpert() {
        // Show all metrics
    }
    
    // Implement the component
}
```

## Exercise 7: Alert Fatigue Reducer

### Objective
Implement an alert deduplication and prioritization system.

### The Problem
```python
# Current state: 1000 alerts/day
alerts = [
    {"service": "api", "error": "timeout", "count": 500},
    {"service": "api", "error": "timeout", "count": 501},
    {"service": "api", "error": "timeout", "count": 502},
    # ... hundreds more
]
```

### Your Task
```python
class AlertReducer:
    def __init__(self):
        self.alerts = []
        self.patterns = {}
        
    def add_alert(self, alert):
        """Add alert and check for patterns"""
        pass
        
    def should_notify(self, alert):
        """Decide if this alert should page someone"""
        # Consider:
        # - Is this a new pattern?
        # - Has it exceeded thresholds?
        # - Is it business critical?
        pass
        
    def get_summary(self):
        """Return human-readable summary"""
        # "500 timeout errors in last hour (increasing)"
        # Instead of 500 individual alerts
        pass
```

## Project: Complete Operator Experience

### Objective
Design a complete operator experience for a microservice.

### Deliverables
1. **Dashboard**: Main operational view
2. **Alerts**: Smart, contextual alerts  
3. **Runbooks**: Executable documentation
4. **Config**: Validated, documented configuration
5. **Tools**: CLI/GUI for common operations

### Evaluation Rubric
```yaml
Clarity:
  - Can a new operator understand in 5 minutes?
  - Is critical information immediately visible?
  
Safety:
  - Are dangerous operations protected?
  - Is there always an undo/rollback?
  
Efficiency:
  - Can routine tasks be done quickly?
  - Is automation available where appropriate?
  
Stress Testing:
  - Works at 3am when tired?
  - Works during major incident?
  - Works on mobile/tablet?
```

## Additional Challenges

### Challenge 1: The On-Call Experience
Design the complete on-call experience:
- Alert comes in at 3am
- How does operator get context?
- What tools do they have?
- How do they hand off?

### Challenge 2: The Deployment Experience  
Design safe, confidence-inspiring deployments:
- Pre-flight checks
- Progress visualization
- Rollback triggers
- Success confirmation

### Challenge 3: The Debugging Experience
Design tools for investigating issues:
- Correlate logs, metrics, traces
- Timeline reconstruction
- Hypothesis testing
- Root cause documentation

## Reflection Questions

After completing exercises:

1. **Cognitive Load**: Where did you reduce it? Where is it still high?

2. **Error Prevention**: What errors does your design prevent? What errors might still occur?

3. **Stress Testing**: Would your interface work for a panicked operator at 3am?

4. **Learnability**: Can a new team member use your interface with minimal training?

5. **Expertise Support**: Does your interface grow with the user from beginner to expert?

## Navigation

!!! tip "Continue Learning"
    
    **Next Axiom**: [Axiom 8: Economics](../axiom-8-economics/index.md) →
    
    **Related Tools**: [Operations Toolkit](../../tools/operations-toolkit.md)
    
    **Back to**: [Axioms Overview](../index.md)
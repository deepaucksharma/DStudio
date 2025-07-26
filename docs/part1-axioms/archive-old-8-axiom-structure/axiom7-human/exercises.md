---
title: "Axiom 7 Exercises: Master Human-System Interaction"
description: "Hands-on labs to design interfaces that prevent disasters, build runbooks that work at 3 AM, and create automation that enhances rather than replaces human judgment. Learn from real UI disasters to build better systems."
type: axiom
difficulty: advanced
reading_time: 45 min
prerequisites: [axiom1-latency, axiom2-capacity, axiom3-failure, axiom4-concurrency, axiom5-coordination, axiom6-observability, axiom7-human]
status: complete
completion_percentage: 100
last_updated: 2025-07-21
---

<!-- Navigation -->
[Home](/) → [Part I: Axioms](part1-axioms) → [Axiom 7](index.md) → **Human Interface Exercises**

# Human Interface Exercises

**From fat-finger disasters to elegant automation: build systems that enhance human capability**

---

## Hands-On Labs

### Lab 1: Production-Safe CLI Design

**Build command-line tools that prevent $440M mistakes**

#### Exercise 1.1: Safe Command Framework

```python
import os
import sys
import time
import json
import shlex
import subprocess
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import getpass
from datetime import datetime

class RiskLevel(Enum):
    SAFE = "safe"           # Read-only operations
    LOW = "low"             # Reversible changes
    MEDIUM = "medium"       # Harder to reverse
    HIGH = "high"           # Irreversible, single target
    CRITICAL = "critical"   # Irreversible, multiple targets

@dataclass
class CommandContext:
    """Context for command execution"""
    environment: str  # dev, staging, prod
    user: str
    sudo: bool
    dry_run: bool
    force: bool
    
class SafeCLI:
    """Framework for safe command-line operations"""
    
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.context = self.detect_context()
        self.command_history = []
        self.risk_assessor = RiskAssessor()
        
    def detect_context(self) -> CommandContext:
        """Automatically detect execution context"""
# TODO: Implement context detection
# 1. Check environment variables
# 2. Check hostname patterns
# 3. Check user permissions
# 4. Check for production indicators
        pass
        
    def execute_command(self, command: str, **kwargs) -> Dict:
        """Safe command execution with multiple checks"""
        
# Step 1: Parse and validate command
        parsed = self.parse_command(command)
        if not parsed['valid']:
            return {'error': parsed['error']}
            
# Step 2: Assess risk
        risk = self.risk_assessor.assess(parsed['command'], self.context)
        
# Step 3: Apply safety checks based on risk
        safety_checks = self.get_safety_checks(risk.level)
        
        for check in safety_checks:
            result = check(parsed['command'], self.context)
            if not result['passed']:
                return {'error': result['message'], 'check': check.__name__}
                
# Step 4: Get confirmation if needed
        if self.needs_confirmation(risk):
            if not self.get_confirmation(parsed['command'], risk):
                return {'status': 'cancelled', 'reason': 'user_cancelled'}
                
# Step 5: Execute with audit trail
        return self.execute_with_audit(parsed['command'], risk)
        
    def get_safety_checks(self, risk_level: RiskLevel) -> List[Callable]:
        """Get appropriate safety checks for risk level"""
        
        checks = [self.check_syntax]  # Always check syntax
        
        if risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
            checks.extend([
                self.check_permissions,
                self.check_target_exists,
                self.check_backup_exists
            ])
            
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            checks.extend([
                self.check_not_production_without_flag,
                self.check_change_window,
                self.check_approval
            ])
            
        if risk_level == RiskLevel.CRITICAL:
            checks.extend([
                self.require_two_person_auth,
                self.check_emergency_only
            ])
            
        return checks
        
    def build_confirmation_ui(self, command: Dict, risk: 'RiskAssessment') -> str:
        """Build confirmation UI based on risk"""
        
        if risk.level == RiskLevel.CRITICAL:
            ui = f"""
╔══════════════════════════════════════════════════════╗
║                   🚨 CRITICAL OPERATION 🚨            ║
╠══════════════════════════════════════════════════════╣
║ Command: {command['raw'][:45]:<45}║
║ Environment: {self.context.environment.upper():<40}║
║ Risk Level: {risk.level.value.upper():<41}║
║ Impact: {risk.impact_description[:47]:<47}║
╠══════════════════════════════════════════════════════╣
║ ⚠️  THIS OPERATION:                                   ║
{self.format_warnings(risk.warnings)}║
╠══════════════════════════════════════════════════════╣
║ Type exactly: {risk.confirmation_phrase:<37}║
╚══════════════════════════════════════════════════════╝
            """
        elif risk.level == RiskLevel.HIGH:
            ui = f"""
╔══════════════════════════════════════════════════════╗
║                 ⚠️  HIGH RISK OPERATION               ║  
╠══════════════════════════════════════════════════════╣
║ This will: {risk.impact_description[:42]:<42}║
║ Affects: {risk.affected_resources[:44]:<44}║
║ Recovery: {risk.recovery_method[:43]:<43}║
╠══════════════════════════════════════════════════════╣
║ Continue? Type 'yes' to proceed:                     ║
╚══════════════════════════════════════════════════════╝
            """
        else:
            ui = f"Execute: {command['raw']}? [y/N] "
            
        return ui

# Exercise: Complete the safe CLI implementation
class RiskAssessor:
    """Assess risk level of commands"""
    
    def __init__(self):
        self.patterns = {
            RiskLevel.CRITICAL: [
                r'rm -rf /',
                r'DROP DATABASE',
                r'DELETE FROM .* WHERE 1',
                r'kubectl delete namespace',
                r'terraform destroy'
            ],
            RiskLevel.HIGH: [
                r'ALTER TABLE',
                r'UPDATE .* SET',
                r'git push --force',
                r'systemctl stop'
            ],
            RiskLevel.MEDIUM: [
                r'git rebase',
                r'docker restart',
                r'npm install'
            ],
            RiskLevel.LOW: [
                r'git pull',
                r'echo',
                r'mkdir'
            ]
        }
        
    def assess(self, command: Dict, context: CommandContext) -> 'RiskAssessment':
        """Assess command risk"""
# TODO: Implement risk assessment based on:
# 1. Command pattern matching
# 2. Target environment
# 3. User permissions
# 4. Time of day
# 5. Recent incidents
        pass

# Test the safe CLI
cli = SafeCLI("prod-tools")

# Test commands of varying risk
test_commands = [
    "ls -la",                          # Safe
    "git status",                      # Safe  
    "systemctl restart nginx",         # Medium
    "UPDATE users SET active=false",   # High
    "rm -rf /var/data/*",             # Critical
]

for cmd in test_commands:
    result = cli.execute_command(cmd)
    print(f"Command: {cmd}")
    print(f"Result: {result}")
    print("-" * 60)
```

#### Exercise 1.2: Production Shell Wrapper

```python
class ProductionShell:
    """Safe shell wrapper for production environments"""
    
    def __init__(self):
        self.original_commands = {}
        self.command_wrappers = {}
        self.setup_environment()
        
    def setup_environment(self):
        """Configure production-safe environment"""
        
# Visual indicators
        os.environ['PS1'] = '\[\033[41m\]PRODUCTION\[\033[0m\] \u@\h:\w\$ '
        
# Safe defaults
        os.environ['PAGER'] = 'less -S'  # Prevent line wrap confusion
        os.environ['EDITOR'] = 'vim -R'  # Read-only by default
        
# Command aliases for safety
        self.create_safe_aliases()
        
    def create_safe_aliases(self):
        """Replace dangerous commands with safe versions"""
        
        aliases = {
            'rm': 'safe_rm',
            'dd': 'safe_dd',
            'truncate': 'safe_truncate',
            'DROP': 'safe_drop',
            '>': 'safe_redirect'  # Prevent accidental overwrites
        }
        
        for dangerous, safe in aliases.items():
            self.command_wrappers[dangerous] = self.create_wrapper(safe)
            
    def create_wrapper(self, safe_command: str) -> Callable:
        """Create a safety wrapper for a command"""
        
        def wrapper(*args, **kwargs):
# Check if this is actually dangerous
            if self.is_dangerous_invocation(safe_command, args):
                return self.handle_dangerous_command(safe_command, args)
            else:
# Execute safely
                return self.execute_safe(safe_command, args)
                
        return wrapper
        
    def command_logger(self, command: str):
        """Log all commands for audit"""
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user': getpass.getuser(),
            'command': command,
            'cwd': os.getcwd(),
            'environment': dict(os.environ),
            'tty': os.ttyname(0) if os.isatty(0) else None
        }
        
# Local logging
        with open('/var/log/production_commands.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
# Remote logging for critical commands
        if self.is_critical(command):
            self.send_to_audit_service(log_entry)
            
    def interactive_mode(self):
        """Enhanced interactive shell with safety features"""
        
        print("""
╔══════════════════════════════════════════════════════╗
║           🚨 PRODUCTION ENVIRONMENT 🚨                ║
╠══════════════════════════════════════════════════════╣
║ • All commands are logged                            ║
║ • Dangerous commands require confirmation            ║
║ • Type 'safe-mode' for additional protections        ║
║ • Type 'help-prod' for production guidelines         ║
╚══════════════════════════════════════════════════════╝
        """)
        
        while True:
            try:
# Show context in prompt
                prompt = self.build_context_prompt()
                command = input(prompt)
                
# Process command
                self.process_command(command)
                
            except KeyboardInterrupt:
                if self.confirm_exit():
                    break
                else:
                    continue

# Exercise: Build the production shell wrapper
shell = ProductionShell()

# Test safety features
test_scenarios = [
    "rm -rf /tmp/test",    # Should warn
    "cat /etc/passwd",     # Should allow
    "dd if=/dev/zero of=/dev/sda",  # Should block
    "sudo systemctl stop",  # Should require confirmation
]
```

---

### Lab 2: Runbook Excellence Workshop

**Create runbooks that actually work when everything is on fire**

#### Exercise 2.1: Intelligent Runbook System

```python
import yaml
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re
from datetime import datetime, timedelta

@dataclass
class RunbookStep:
    """Single step in a runbook"""
    title: str
    description: str
    commands: List[str]
    expected_output: Optional[str]
    timeout_seconds: int = 30
    can_fail: bool = False
    rollback_commands: Optional[List[str]] = None
    
class IntelligentRunbook:
    """Runbook system that guides operators"""
    
    def __init__(self, runbook_path: str):
        self.runbook = self.load_runbook(runbook_path)
        self.execution_log = []
        self.start_time = None
        self.context = {}
        
    def load_runbook(self, path: str) -> Dict:
        """Load and validate runbook"""
# TODO: Implement runbook loading with:
# 1. YAML/JSON parsing
# 2. Schema validation
# 3. Command safety checks
# 4. Prerequisite verification
        pass
        
    def execute_interactive(self):
        """Execute runbook with operator guidance"""
        
        self.start_time = datetime.now()
        print(f"""
╔══════════════════════════════════════════════════════╗
║           RUNBOOK: {self.runbook['title']:<34}║
╠══════════════════════════════════════════════════════╣
║ Severity: {self.runbook['severity']:<42}║
║ Est. Time: {self.runbook['estimated_minutes']:<37} minutes ║
║ Prerequisites: {len(self.runbook.get('prerequisites', [])):<33} checks ║
╚══════════════════════════════════════════════════════╝
        """)
        
# Check prerequisites
        if not self.check_prerequisites():
            return self.abort("Prerequisites not met")
            
# Execute steps
        for i, step in enumerate(self.runbook['steps']):
            if not self.execute_step(i + 1, step):
                if step.get('can_fail', False):
                    self.log_warning(f"Step {i+1} failed but continuing")
                else:
                    return self.handle_failure(i + 1, step)
                    
# Success!
        self.complete_runbook()
        
    def execute_step(self, step_num: int, step: Dict) -> bool:
        """Execute a single runbook step"""
        
# Show step info
        print(f"""
┌─────────────────────────────────────────────────────┐
│ Step {step_num}/{len(self.runbook['steps'])}: {step['title']:<40}│
├─────────────────────────────────────────────────────┤
│ {step['description']:<51}│
└─────────────────────────────────────────────────────┘
        """)
        
# TODO: Implement step execution with:
# 1. Command execution with timeout
# 2. Output validation
# 3. Error handling
# 4. Progress tracking
# 5. Rollback capability
        
# Execute commands
        for cmd in step.get('commands', []):
            if not self.execute_command(cmd, step.get('timeout_seconds', 30)):
                return False
                
# Validate output if specified
        if 'expected_output' in step:
            if not self.validate_output(step['expected_output']):
                return False
                
# Human verification if needed
        if step.get('requires_verification', False):
            if not self.get_operator_verification(step):
                return False
                
        return True
        
    def adaptive_guidance(self, error: Exception, step: Dict) -> Dict:
        """Provide intelligent guidance based on error"""
        
# TODO: Implement smart error handling:
# 1. Pattern match against known errors
# 2. Suggest alternative commands
# 3. Offer to search documentation
# 4. Connect to on-call if needed
        
        guidance = {
            'error_type': type(error).__name__,
            'suggestions': [],
            'documentation': [],
            'similar_incidents': []
        }
        
# Pattern matching for common issues
        error_patterns = {
            'Connection refused': {
                'suggestions': [
                    "Check if service is running: systemctl status {service}",
                    "Check firewall rules: iptables -L",
                    "Verify network connectivity: ping {host}"
                ],
                'likely_causes': ['Service down', 'Firewall blocking', 'Network issue']
            },
            'Permission denied': {
                'suggestions': [
                    "Check current user: whoami",
                    "Try with sudo: sudo {command}",
                    "Check file permissions: ls -la {file}"
                ],
                'likely_causes': ['Insufficient privileges', 'File ownership']
            }
        }
        
        return guidance

# Exercise: Create a complete runbook
sample_runbook = """
title: Database Connection Pool Exhausted
severity: HIGH
estimated_minutes: 15
tags: [database, connection-pool, performance]

prerequisites:
  - name: VPN Connected
    command: "ping -c 1 internal.db.host"
    expected: "1 packets transmitted, 1 received"
  - name: Database Accessible  
    command: "psql -h db.host -c 'SELECT 1'"
    expected: "1"

steps:
  - title: Check Current Connection Count
    description: Verify the database connection pool is actually exhausted
    commands:
      - "psql -h db.host -c 'SELECT count(*) FROM pg_stat_activity'"
    expected_output_contains: "max_connections"
    
  - title: Identify Connection Hogs
    description: Find which applications are using most connections
    commands:
      - "psql -h db.host -c 'SELECT application_name, count(*) FROM pg_stat_activity GROUP BY application_name ORDER BY count DESC'"
    requires_verification: true
    
  - title: Kill Idle Connections
    description: Terminate connections idle for >10 minutes
    commands:
      - "psql -h db.host -f /runbooks/sql/kill_idle_connections.sql"
    can_fail: false
    rollback_commands:
      - "echo 'No rollback needed for connection termination'"
      
  - title: Restart Connection Pool
    description: Restart the application connection pools
    commands:
      - "kubectl rollout restart deployment/api-service -n prod"
      - "kubectl rollout status deployment/api-service -n prod"
    timeout_seconds: 300
    
  - title: Verify Resolution
    description: Ensure connection pool is healthy
    commands:
      - "curl -s http://api.internal/health | jq .database"
    expected_output_contains: "healthy"
    
post_resolution:
  - Create incident report
  - Update connection pool sizing
  - Add monitoring for connection pool usage
"""

# Save and test the runbook
with open('db_connection_runbook.yaml', 'w') as f:
    f.write(sample_runbook)
    
runbook = IntelligentRunbook('db_connection_runbook.yaml')
runbook.execute_interactive()
```

#### Exercise 2.2: Runbook Testing Framework

```python
class RunbookTester:
    """Test runbooks before incidents happen"""
    
    def __init__(self, runbook_dir: str):
        self.runbook_dir = runbook_dir
        self.test_results = {}
        self.coverage = {}
        
    def test_all_runbooks(self) -> Dict:
        """Test all runbooks in directory"""
        
# TODO: Implement comprehensive testing:
# 1. Syntax validation
# 2. Command safety checks
# 3. Dry-run execution
# 4. Output validation
# 5. Time estimation accuracy
# 6. Rollback procedures
        pass
        
    def simulate_incident(self, runbook_name: str, 
                         failure_injection: Optional[Dict] = None) -> Dict:
        """Simulate incident and test runbook response"""
        
# TODO: Create realistic test scenarios
# Inject failures at different steps
# Measure operator decision time
# Track recovery success rate
        pass
        
    def chaos_test_runbook(self, runbook_name: str) -> List[Dict]:
        """Test runbook under chaotic conditions"""
        
        chaos_scenarios = [
            {"name": "network_flaky", "description": "20% packet loss"},
            {"name": "slow_commands", "description": "Commands take 10x longer"},
            {"name": "partial_failure", "description": "Some commands fail randomly"},
            {"name": "wrong_output", "description": "Unexpected command output"},
            {"name": "missing_tools", "description": "Required tools not installed"},
        ]
        
        results = []
        for scenario in chaos_scenarios:
            result = self.test_with_chaos(runbook_name, scenario)
            results.append(result)
            
        return results
        
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        
        report = f"""
# Runbook Test Report
Generated: {datetime.now():%Y-%m-%d %H:%M:%S}

## Summary
- Total Runbooks: {len(self.test_results)}
- Passed: {sum(1 for r in self.test_results.values() if r['passed'])}
- Failed: {sum(1 for r in self.test_results.values() if not r['passed'])}
- Coverage: {self.calculate_coverage():.1f}%

## Detailed Results
        """
        
        for runbook, result in self.test_results.items():
            report += f"""
### {runbook}
- Status: {'✅ PASS' if result['passed'] else '❌ FAIL'}
- Execution Time: {result['execution_time']:.1f}s
- Issues Found: {len(result.get('issues', []))}
            """
            
            if result.get('issues'):
                report += "\nIssues:\n"
                for issue in result['issues']:
                    report += f"- {issue['severity']}: {issue['description']}\n"
                    
        return report

# Exercise: Test your runbooks
tester = RunbookTester('./runbooks')
results = tester.test_all_runbooks()
print(tester.generate_test_report())
```

---

### Lab 3: Cognitive Load Optimization

**Design interfaces that work for tired brains**

#### Exercise 3.1: Adaptive UI Complexity

```python
class AdaptiveUI:
    """UI that adapts to operator state and expertise"""
    
    def __init__(self):
        self.user_profiles = {}
        self.current_cognitive_load = 0
        self.expertise_tracker = ExpertiseTracker()
        
    def assess_cognitive_load(self, user_id: str) -> float:
        """Estimate current cognitive load"""
        
        factors = {
            'time_on_shift': self.get_shift_duration(user_id),
            'incident_count': self.get_recent_incidents(user_id),
            'error_rate': self.get_recent_error_rate(user_id),
            'response_time': self.get_response_latency(user_id),
            'time_of_day': self.get_circadian_factor()
        }
        
# TODO: Implement cognitive load calculation
# Range: 0.0 (fresh) to 1.0 (exhausted)
        pass
        
    def render_dashboard(self, user_id: str) -> Dict:
        """Render dashboard adapted to user state"""
        
        cognitive_load = self.assess_cognitive_load(user_id)
        expertise = self.expertise_tracker.get_level(user_id)
        
        if cognitive_load > 0.8:  # High load - simplify everything
            return self.render_simplified_dashboard()
        elif expertise == 'expert' and cognitive_load < 0.3:
            return self.render_expert_dashboard()
        else:
            return self.render_standard_dashboard()
            
    def render_simplified_dashboard(self) -> Dict:
        """Ultra-simple dashboard for high cognitive load"""
        
        return {
            'layout': 'single-column',
            'panels': [
                {
                    'type': 'status',
                    'title': 'System Health',
                    'visualization': 'traffic-light',  # Red/Yellow/Green only
                    'details': 'hidden-by-default'
                },
                {
                    'type': 'actions',
                    'title': 'What To Do',
                    'items': self.get_prioritized_actions(limit=3),
                    'style': 'large-buttons'
                },
                {
                    'type': 'help',
                    'title': 'Get Help',
                    'options': ['Page Senior', 'View Runbook', 'Emergency']
                }
            ],
            'refresh_rate': 30,  # Slower to reduce distraction
            'animations': False,
            'sounds': True  # Audio alerts for critical only
        }
        
    def intelligent_error_messages(self, error: Exception, 
                                 cognitive_load: float) -> Dict:
        """Adapt error messages to cognitive state"""
        
        if cognitive_load > 0.7:
# Simple, actionable message
            return {
                'title': 'Something went wrong',
                'message': self.get_simple_explanation(error),
                'action': self.get_primary_action(error),
                'details_available': True  # But hidden
            }
        else:
# Detailed technical message
            return {
                'title': f'{type(error).__name__}',
                'message': str(error),
                'stack_trace': self.get_stack_trace(error),
                'related_logs': self.get_related_logs(error),
                'similar_incidents': self.find_similar(error),
                'suggested_fixes': self.suggest_fixes(error)
            }

# Exercise: Build adaptive UI system
ui = AdaptiveUI()

# Test with different cognitive loads
test_scenarios = [
    {'user_id': 'alice', 'hours_on_shift': 2, 'incidents': 0},   # Fresh
    {'user_id': 'bob', 'hours_on_shift': 8, 'incidents': 3},     # Tired
    {'user_id': 'charlie', 'hours_on_shift': 12, 'incidents': 5}, # Exhausted
]

for scenario in test_scenarios:
    dashboard = ui.render_dashboard(scenario['user_id'])
    print(f"User: {scenario['user_id']}")
    print(f"Dashboard complexity: {len(dashboard['panels'])} panels")
    print("-" * 60)
```

#### Exercise 3.2: Progressive Automation

```python
class ProgressiveAutomation:
    """Gradually increase automation as confidence grows"""
    
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.automation_level = 0  # 0-100%
        self.execution_history = []
        self.confidence_score = 0
        
    def execute_task(self, context: Dict) -> Dict:
        """Execute task with appropriate automation level"""
        
        level = self.get_automation_level()
        
        if level == 0:
# Full manual
            return self.execute_manual(context)
        elif level < 30:
# Assisted - suggestions only
            return self.execute_assisted(context)
        elif level < 70:
# Supervised - auto with confirmation
            return self.execute_supervised(context)
        elif level < 95:
# Automated with alerts
            return self.execute_automated_alert(context)
        else:
# Fully automated
            return self.execute_fully_automated(context)
            
    def execute_assisted(self, context: Dict) -> Dict:
        """Provide suggestions but human executes"""
        
        suggestions = self.generate_suggestions(context)
        
        print(f"""
┌─────────────────────────────────────────────────────┐
│ Task: {self.task_name:<45}│
│ Automation Level: {self.automation_level}% (Assisted)          │
├─────────────────────────────────────────────────────┤
│ Suggested Actions:                                  │
        """)
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"│ {i}. {suggestion['action']:<45}│")
            print(f"│    Confidence: {suggestion['confidence']:.1%:<33}│")
            
        print("└─────────────────────────────────────────────────────┘")
        
# Human selects and executes
        choice = input("Select action (or 'manual' for custom): ")
        return self.execute_human_choice(choice, suggestions)
        
    def learn_from_execution(self, result: Dict):
        """Learn from each execution to improve automation"""
        
        self.execution_history.append({
            'timestamp': datetime.now(),
            'result': result,
            'automation_level': self.automation_level
        })
        
# Update confidence based on success
        if result['status'] == 'success':
            self.confidence_score = min(100, self.confidence_score + 2)
        else:
            self.confidence_score = max(0, self.confidence_score - 10)
            
# Adjust automation level
        self.update_automation_level()
        
    def update_automation_level(self):
        """Gradually increase automation as confidence grows"""
        
# TODO: Implement smart automation progression
# Consider:
# 1. Success rate over time
# 2. Consistency of context
# 3. Impact of failures
# 4. Time since last failure
# 5. Operator feedback
        pass

# Exercise: Build progressive automation
tasks = [
    ProgressiveAutomation("Scale web servers"),
    ProgressiveAutomation("Database backup"),
    ProgressiveAutomation("Deploy to staging"),
    ProgressiveAutomation("Clear cache"),
]

# Simulate automation progression
for day in range(30):
    print(f"\nDay {day + 1}")
    for task in tasks:
        context = {'load': random.uniform(0.5, 1.5)}
        result = task.execute_task(context)
        task.learn_from_execution(result)
        print(f"{task.task_name}: {task.automation_level}% automated")
```

---

### Lab 4: Incident Command Interface

**Build tools for managing chaos**

#### Exercise 4.1: Incident Command System

```python
class IncidentCommand:
    """Unified interface for incident management"""
    
    def __init__(self):
        self.active_incident = None
        self.responders = {}
        self.timeline = []
        self.decisions = []
        
    def start_incident(self, alert: Dict) -> 'Incident':
        """Initialize incident response"""
        
        incident = Incident(
            id=self.generate_incident_id(),
            title=alert['title'],
            severity=self.assess_severity(alert),
            started_at=datetime.now()
        )
        
        self.active_incident = incident
        self.display_incident_dashboard()
        
        return incident
        
    def display_incident_dashboard(self):
        """Real-time incident command dashboard"""
        
        dashboard = f"""
╔══════════════════════════════════════════════════════╗
║                 INCIDENT COMMAND                      ║
╠══════════════════════════════════════════════════════╣
║ ID: {self.active_incident.id:<47}║
║ Title: {self.active_incident.title[:44]:<44}║
║ Severity: {self.active_incident.severity:<40}║
║ Duration: {self.get_duration():<40}║
╠══════════════════════════════════════════════════════╣
║ RESPONDERS:                                          ║
{self.format_responders()}║
╠══════════════════════════════════════════════════════╣
║ CURRENT STATUS:                                      ║
║ {self.active_incident.status:<48}║
╠══════════════════════════════════════════════════════╣
║ RECENT ACTIONS:                                      ║
{self.format_recent_actions()}║
╠══════════════════════════════════════════════════════╣
║ [1] Update Status  [2] Add Responder  [3] Decision  ║
║ [4] Run Playbook   [5] External Comm  [6] Handoff   ║
╚══════════════════════════════════════════════════════╝
        """
        
        return dashboard
        
    def make_decision(self, decision_type: str, details: Dict):
        """Record and communicate decisions"""
        
        decision = {
            'id': len(self.decisions) + 1,
            'timestamp': datetime.now(),
            'type': decision_type,
            'made_by': self.get_current_commander(),
            'details': details,
            'communicated_to': []
        }
        
# Record decision
        self.decisions.append(decision)
        self.timeline.append({
            'type': 'decision',
            'decision': decision
        })
        
# Communicate to relevant parties
        self.communicate_decision(decision)
        
# Update dashboard
        self.refresh_dashboard()
        
    def generate_sitrep(self) -> str:
        """Generate situation report"""
        
# TODO: Create concise situation report
# Include:
# - Current status
# - Impact assessment
# - Actions taken
# - Next steps
# - Resource needs
        pass
        
    def handoff_command(self, new_commander: str):
        """Smooth handoff to new incident commander"""
        
        handoff_package = {
            'incident': self.active_incident,
            'timeline': self.timeline,
            'decisions': self.decisions,
            'current_state': self.capture_current_state(),
            'open_actions': self.get_open_actions(),
            'key_contacts': self.get_key_contacts()
        }
        
# Generate handoff briefing
        briefing = self.generate_handoff_briefing(handoff_package)
        
# Notify all responders
        self.notify_handoff(new_commander)
        
        return briefing

# Exercise: Run incident simulation
command = IncidentCommand()

# Simulate incident
alert = {
    'title': 'Payment Processing Down',
    'source': 'monitoring.payments',
    'impact': 'No customer payments processing',
    'affected_services': ['payments-api', 'payment-gateway', 'transaction-db']
}

incident = command.start_incident(alert)

# Simulate incident progression
actions = [
    ('add_responder', {'name': 'Alice', 'role': 'SRE Lead'}),
    ('update_status', {'status': 'Investigating root cause'}),
    ('make_decision', {'type': 'rollback', 'target': 'payment-service v2.1.0'}),
    ('update_status', {'status': 'Rollback in progress'}),
    ('add_responder', {'name': 'Bob', 'role': 'Database Admin'}),
    ('update_status', {'status': 'Service restored, monitoring'})
]

for action_type, details in actions:
    time.sleep(1)  # Simulate time passing
    getattr(command, action_type)(details)
    print(command.display_incident_dashboard())
```

#### Exercise 4.2: Communication Templates

```python
class CommunicationTemplates:
    """Generate clear communications during incidents"""
    
    def __init__(self):
        self.templates = self.load_templates()
        self.audience_profiles = {
            'technical': {'detail_level': 'high', 'include_logs': True},
            'management': {'detail_level': 'medium', 'focus': 'impact'},
            'customers': {'detail_level': 'low', 'focus': 'resolution'},
            'legal': {'detail_level': 'medium', 'focus': 'compliance'}
        }
        
    def generate_update(self, incident: 'Incident', 
                       audience: str,
                       update_type: str) -> str:
        """Generate audience-appropriate update"""
        
# TODO: Create different messages for different audiences
# Technical: Full details, logs, metrics
# Management: Impact, timeline, resources
# Customers: Apology, timeline, workaround
# Legal: Compliance, data impact, remediation
        pass
        
    def status_page_update(self, incident: 'Incident') -> Dict:
        """Generate public status page update"""
        
        severity_emoji = {
            'low': '🟡',
            'medium': '🟠',
            'high': '🔴',
            'critical': '🚨'
        }
        
        return {
            'title': f"{severity_emoji[incident.severity]} {incident.title}",
            'status': self.simplify_status(incident.status),
            'message': self.generate_public_message(incident),
            'updated_at': datetime.now().isoformat(),
            'affected_services': self.get_public_service_names(incident.affected),
            'timeline': self.generate_public_timeline(incident)
        }

# Exercise: Generate communications
templates = CommunicationTemplates()

# Test different audience updates
incident = Incident(
    title="Database Performance Degradation",
    severity="high",
    status="Investigating",
    impact="30% of queries taking >5s"
)

for audience in ['technical', 'management', 'customers']:
    update = templates.generate_update(incident, audience, 'initial')
    print(f"\n{'='*60}")
    print(f"Update for {audience.upper()}:")
    print(update)
```

---

## 💪 Challenge Problems

### Challenge 1: Design for Failure

```python
"""
Scenario: You're designing a system that will be operated by:
- Junior engineers with 6 months experience
- Senior engineers during emergencies
- On-call engineers at 3 AM
- Engineers under extreme stress

Design a complete interface system that:
1. Prevents catastrophic errors
2. Guides users to correct actions
3. Adapts to operator state
4. Learns from near-misses
5. Works during partial system failures

Constraints:
- Must work on mobile devices
- Must work with 1990s terminal emulators
- Must be accessible (WCAG compliant)
- Must support 20+ languages
- Must work offline
"""

class ResilientInterface:
# Your implementation here
    pass
```

### Challenge 2: The Perfect Runbook

```python
"""
Create "The Perfect Runbook" that:

1. Works for any skill level
2. Adapts to incident specifics
3. Tracks what actually works
4. Updates itself based on outcomes
5. Integrates with all tools
6. Works when half the systems are down
7. Provides rollback for every action
8. Explains "why" not just "how"
9. Handles interrupted execution
10. Learns from every use

Bonus: Make it work via SMS when all else fails
"""

class PerfectRunbook:
# Your design here
    pass
```

### Challenge 3: Automation Psychology

```python
"""
Design an automation system that:

1. Maintains operator skills
2. Builds appropriate trust
3. Handles handoff between human/machine
4. Explains its actions
5. Accepts human override gracefully
6. Learns from human corrections
7. Knows its own limitations
8. Requests help appropriately

The system should pass the "Tuesday Test":
If the automation fails on a boring Tuesday,
can operators take over effectively?
"""

class HumanCentricAutomation:
# Your implementation
    pass
```

---

## Research Projects

### Project 1: Cognitive Load Measurement

```python
class CognitiveLoadMonitor:
    """Real-time cognitive load assessment"""
    
    def __init__(self):
        self.metrics = {
            'response_time': [],      # CLI response latency
            'error_rate': [],         # Typos and mistakes
            'help_requests': [],      # Documentation lookups
            'backtracking': [],       # Undo/cancel actions
            'pause_duration': []      # Think time
        }
        
    def assess_load(self) -> float:
        """Calculate current cognitive load"""
# TODO: Implement algorithm combining:
# - Response time degradation
# - Increase in errors
# - Help-seeking behavior
# - Decision paralysis indicators
        pass
        
    def recommend_intervention(self, load: float) -> str:
        """Suggest interventions based on load"""
# TODO: Recommendations like:
# - Simplify interface
# - Suggest break
# - Call for backup
# - Activate assisted mode
        pass

# Research: Validate against actual incident data
```

### Project 2: Failure Language Analysis

```python
"""
Analyze language patterns in incident communications to:
1. Detect stress levels
2. Predict miscommunication
3. Identify knowledge gaps
4. Suggest clarifications
5. Translate jargon automatically

Build NLP model that improves incident communication
"""

class IncidentLanguageAnalyzer:
# Your research implementation
    pass
```

---

## 📑 Design Patterns Reference

### Safety Pattern Checklist

```python
safety_patterns = {
    'confirmation': {
        'low_risk': 'Simple y/n confirmation',
        'medium_risk': 'Type command to confirm',
        'high_risk': 'Type exact phrase',
        'critical_risk': 'Two-person authorization'
    },
    'visibility': {
        'production': 'Red borders, warning banners',
        'staging': 'Yellow indicators',
        'development': 'Green/normal appearance'
    },
    'recovery': {
        'immediate': 'Undo button available',
        'quick': 'Rollback command documented',
        'possible': 'Backup exists',
        'difficult': 'Require approval first'
    }
}
```

### Cognitive Design Principles

```python
cognitive_principles = [
    "Recognition over recall",
    "Consistency across interfaces",
    "Progressive disclosure",
    "Immediate feedback",
    "Error prevention over error handling",
    "Reversible actions",
    "Reduce cognitive load",
    "Support interrupt/resume",
    "Clear information hierarchy",
    "Respect human limitations"
]
```

---

## Skills Assessment

Rate your understanding (1-5):
- [ ] Can design safe command interfaces
- [ ] Can create effective runbooks
- [ ] Understand cognitive load factors
- [ ] Can build adaptive interfaces
- [ ] Can design for failure scenarios
- [ ] Know automation handoff patterns
- [ ] Can measure interface effectiveness
- [ ] Can design for accessibility

**Score: ___/40** (32+ = Expert, 24-32 = Proficient, 16-24 = Intermediate, <16 = Keep practicing!)

---

## Final Challenge: Mission Control System

```python
"""
The Ultimate Test: Design SpaceX Mission Control Interface

Requirements:
- Control rocket launches (cannot fail)
- Support 100+ operators
- Handle emergencies in milliseconds
- Work during partial failures
- Support global operations
- Train new operators quickly
- Prevent any catastrophic commands
- Full audit trail
- Work in disaster scenarios

Your interface will control:
- Human lives
- Billion dollar assets
- Environmental safety
- International relations

Design the complete human interface system.
"""

class MissionControlInterface:
# Your implementation here
    pass
```

---

**Previous**: [Examples](examples.md) | **Next**: [Axiom 8: Economics](part1-axioms/archive-old-8-axiom-structure/axiom8-economics/)

**Related**: [SRE Practices](human-factors/sre-practices) • [Chaos Engineering](human-factors/chaos-engineering) • [Observability](part1-axioms/archive-old-8-axiom-structure/axiom6-observability/)

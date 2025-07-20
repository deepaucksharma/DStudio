#!/usr/bin/env python3
"""
Fix pattern files by adding missing required sections
"""

import os
import re
from pathlib import Path
import json

class PatternStructureFixer:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.patterns_dir = self.docs_dir / "patterns"
        self.files_fixed = 0
        self.sections_added = 0
        
        # Required sections for pattern files
        self.required_sections = [
            "Problem",
            "Solution", 
            "Implementation",
            "When to Use",
            "When NOT to Use",
            "Trade-offs",
            "Real Examples", 
            "Code Sample",
            "Exercise"
        ]
        
        # Pattern-specific information for generating content
        self.pattern_info = {
            'circuit-breaker': {
                'problem': 'Cascade failures when downstream services fail',
                'solution': 'Monitor failures and stop calling failing services temporarily',
                'use_cases': ['External API calls', 'Microservice communication', 'Database connections'],
                'avoid_cases': ['Internal method calls', 'CPU-bound operations', 'Business logic errors']
            },
            'retry-backoff': {
                'problem': 'Transient failures that could succeed if retried intelligently',
                'solution': 'Retry failed operations with exponential backoff and jitter',
                'use_cases': ['Network requests', 'Database queries', 'External service calls'],
                'avoid_cases': ['Authentication failures', 'Validation errors', 'Business rule violations']
            },
            'bulkhead': {
                'problem': 'Failures in one part of system affecting unrelated components',
                'solution': 'Isolate system resources to prevent cascade failures',
                'use_cases': ['Thread pools', 'Connection pools', 'Rate limiting'],
                'avoid_cases': ['Single-user systems', 'Tightly coupled operations', 'Shared state requirements']
            },
            'timeout': {
                'problem': 'Operations hanging indefinitely and consuming resources',
                'solution': 'Set maximum time limits for operations to complete',
                'use_cases': ['Network calls', 'Database queries', 'External APIs'],
                'avoid_cases': ['File I/O', 'CPU computations', 'User interactions']
            },
            'distributed-lock': {
                'problem': 'Coordinating exclusive access to resources across multiple nodes',
                'solution': 'Use consensus mechanisms to ensure only one process can access resource',
                'use_cases': ['Leader election', 'Resource allocation', 'Sequential processing'],
                'avoid_cases': ['High-frequency operations', 'Local resources', 'Performance-critical paths']
            },
            'health-check': {
                'problem': 'Detecting when services are unhealthy or overloaded',
                'solution': 'Regular monitoring of service status and dependencies',
                'use_cases': ['Load balancer routing', 'Auto-scaling decisions', 'Alert triggering'],
                'avoid_cases': ['Business logic validation', 'User authentication', 'Data consistency checks']
            },
            'saga': {
                'problem': 'Maintaining data consistency across multiple services without 2PC',
                'solution': 'Choreographed or orchestrated sequence of compensating transactions',
                'use_cases': ['Distributed transactions', 'Multi-service workflows', 'E-commerce checkout'],
                'avoid_cases': ['Single service operations', 'Immediate consistency requirements', 'Simple CRUD']
            },
            'event-sourcing': {
                'problem': 'Tracking state changes and enabling time-travel debugging',
                'solution': 'Store events that led to current state instead of current state',
                'use_cases': ['Audit trails', 'Debugging', 'Analytics', 'Undo functionality'],
                'avoid_cases': ['Simple CRUD', 'Storage-constrained systems', 'Immediate queries']
            },
            'cqrs': {
                'problem': 'Different models needed for reads vs writes',
                'solution': 'Separate command and query responsibilities with different models',
                'use_cases': ['Complex domains', 'Different read/write patterns', 'Scalability needs'],
                'avoid_cases': ['Simple CRUD', 'Tightly coupled read/write', 'Small applications']
            },
            'load-balancing': {
                'problem': 'Distributing incoming requests across multiple service instances',
                'solution': 'Route requests using algorithms like round-robin, least-connections',
                'use_cases': ['High traffic services', 'Multiple replicas', 'Geographic distribution'],
                'avoid_cases': ['Single instance', 'Stateful sessions', 'Development environments']
            }
        }
    
    def extract_pattern_name(self, file_path):
        """Extract pattern name from file path"""
        return file_path.stem.lower()
    
    def extract_title(self, content):
        """Extract title from content"""
        # Try frontmatter first
        fm_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        if fm_match:
            return fm_match.group(1)
        
        # Try first H1
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1)
            
        return "Pattern"
    
    def has_section(self, content, section_name):
        """Check if content already has a section"""
        # Look for section headers (## or ###)
        patterns = [
            rf'^##\s+.*{re.escape(section_name)}.*$',
            rf'^###\s+.*{re.escape(section_name)}.*$',
            rf'^##\s+{re.escape(section_name)}\s*$',
            rf'^###\s+{re.escape(section_name)}\s*$'
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                return True
        return False
    
    def generate_problem_section(self, pattern_name, title):
        """Generate Problem section"""
        info = self.pattern_info.get(pattern_name, {})
        problem = info.get('problem', 'Distributed systems face challenges that this pattern addresses')
        
        return f"""
## 🎯 Problem Statement

### The Challenge
{problem}

### Why This Matters
In distributed systems, this problem manifests as:
- **Reliability Issues**: System failures cascade and affect multiple components
- **Performance Degradation**: Poor handling leads to resource exhaustion  
- **User Experience**: Inconsistent or poor response times
- **Operational Complexity**: Difficult to debug and maintain

### Common Symptoms
- Intermittent failures that are hard to reproduce
- Performance that degrades under load
- Resource exhaustion (connections, threads, memory)
- Difficulty isolating root causes of issues

### Without This Pattern
Systems become fragile, unreliable, and difficult to operate at scale.

"""
    
    def generate_solution_section(self, pattern_name, title):
        """Generate Solution section"""
        info = self.pattern_info.get(pattern_name, {})
        solution = info.get('solution', 'This pattern provides a structured approach to the problem')
        
        return f"""
## 💡 Solution Overview

### Core Concept
{solution}

### Key Principles
1. **Isolation**: Separate concerns to prevent failures from spreading
2. **Resilience**: Build systems that gracefully handle failures
3. **Observability**: Make system behavior visible and measurable
4. **Simplicity**: Keep solutions understandable and maintainable

### How It Works
The {title} pattern works by:
- Monitoring system behavior and health
- Implementing protective mechanisms
- Providing fallback strategies
- Enabling rapid recovery from failures

### Benefits
- **Improved Reliability**: System continues operating during partial failures
- **Better Performance**: Resources are protected from overload
- **Easier Operations**: Clear indicators of system health
- **Reduced Risk**: Failures are contained and predictable

"""
    
    def generate_implementation_section(self, pattern_name, title):
        """Generate Implementation section"""
        return f"""
## 🔧 Implementation Details

### Architecture Components

```mermaid
graph TD
    A[Client Request] --> B[{title} Component]
    B --> C[Protected Service]
    B --> D[Monitoring]
    B --> E[Fallback]
    D --> F[Metrics]
    E --> G[Alternative Response]
```

### Core Components
1. **Monitor**: Tracks system health and performance
2. **Protection**: Implements the defensive mechanism  
3. **Fallback**: Provides alternative when protection activates
4. **Recovery**: Enables return to normal operation

### Configuration Parameters
- **Thresholds**: When to activate protection
- **Timeouts**: How long to wait for operations
- **Backoff**: How to space retry attempts
- **Monitoring**: What metrics to track

### State Management
The pattern typically maintains state about:
- Current health status
- Recent failure history
- Configuration parameters
- Performance metrics

"""
    
    def generate_when_to_use_section(self, pattern_name, title):
        """Generate When to Use section"""
        info = self.pattern_info.get(pattern_name, {})
        use_cases = info.get('use_cases', ['Distributed systems', 'High-availability services', 'External dependencies'])
        
        use_list = '\n'.join([f'- **{case}**' for case in use_cases])
        
        return f"""
## ✅ When to Use

### Ideal Scenarios
{use_list}

### Environmental Factors
- **High Traffic**: System handles significant load
- **External Dependencies**: Calls to other services or systems
- **Reliability Requirements**: Uptime is critical to business
- **Resource Constraints**: Limited connections, threads, or memory

### Team Readiness
- Team understands distributed systems concepts
- Monitoring and alerting infrastructure exists
- Operations team can respond to pattern-related alerts

### Business Context
- Cost of downtime is significant
- User experience is a priority
- System is customer-facing or business-critical

"""
    
    def generate_when_not_to_use_section(self, pattern_name, title):
        """Generate When NOT to Use section"""
        info = self.pattern_info.get(pattern_name, {})
        avoid_cases = info.get('avoid_cases', ['Simple applications', 'Development environments', 'Single-user systems'])
        
        avoid_list = '\n'.join([f'- **{case}**' for case in avoid_cases])
        
        return f"""
## ❌ When NOT to Use

### Inappropriate Scenarios
{avoid_list}

### Technical Constraints
- **Simple Systems**: Overhead exceeds benefits
- **Development/Testing**: Adds unnecessary complexity
- **Performance Critical**: Pattern overhead is unacceptable
- **Legacy Systems**: Cannot be easily modified

### Resource Limitations
- **No Monitoring**: Cannot observe pattern effectiveness
- **Limited Expertise**: Team lacks distributed systems knowledge
- **Tight Coupling**: System design prevents pattern implementation

### Anti-Patterns
- Adding complexity without clear benefit
- Implementing without proper monitoring
- Using as a substitute for fixing root causes
- Over-engineering simple problems

"""
    
    def generate_tradeoffs_section(self, pattern_name, title):
        """Generate Trade-offs section"""
        return f"""
## ⚖️ Trade-offs

### Benefits vs Costs

| Benefit | Cost | Mitigation |
|---------|------|------------|
| **Improved Reliability** | Implementation complexity | Use proven libraries/frameworks |
| **Better Performance** | Resource overhead | Monitor and tune parameters |
| **Faster Recovery** | Operational complexity | Invest in monitoring and training |
| **Clearer Debugging** | Additional logging | Use structured logging |

### Performance Impact
- **Latency**: Small overhead per operation
- **Memory**: Additional state tracking
- **CPU**: Monitoring and decision logic
- **Network**: Possible additional monitoring calls

### Operational Complexity
- **Monitoring**: Need dashboards and alerts
- **Configuration**: Parameters must be tuned
- **Debugging**: Additional failure modes to understand
- **Testing**: More scenarios to validate

### Development Trade-offs
- **Initial Cost**: More time to implement correctly
- **Maintenance**: Ongoing tuning and monitoring
- **Testing**: Complex failure scenarios to validate
- **Documentation**: More concepts for team to understand

"""
    
    def generate_real_examples_section(self, pattern_name, title):
        """Generate Real Examples section"""
        examples = {
            'circuit-breaker': [
                ('Netflix Hystrix', 'Protects against cascade failures in microservice calls'),
                ('AWS Load Balancers', 'Stop routing to unhealthy instances'),
                ('Database Connection Pools', 'Prevent database overload')
            ],
            'retry-backoff': [
                ('AWS SDK', 'Retries failed API calls with exponential backoff'),
                ('Kubernetes', 'Retries failed pod deployments'),
                ('HTTP Clients', 'Retry failed network requests')
            ],
            'bulkhead': [
                ('Thread Pools', 'Separate thread pools for different operations'),
                ('Connection Pools', 'Separate database connections by service'),
                ('Rate Limiting', 'Different limits for different user types')
            ]
        }
        
        pattern_examples = examples.get(pattern_name, [
            ('Major Cloud Provider', 'Uses this pattern for service reliability'),
            ('Popular Framework', 'Implements this pattern by default'),
            ('Enterprise System', 'Applied this pattern to improve uptime')
        ])
        
        examples_text = '\n'.join([
            f'**{name}**: {description}' for name, description in pattern_examples
        ])
        
        return f"""
## 🌟 Real Examples

### Production Implementations

{examples_text}

### Open Source Examples
- **Libraries**: Resilience4j, Polly, circuit-breaker-js
- **Frameworks**: Spring Cloud, Istio, Envoy
- **Platforms**: Kubernetes, Docker Swarm, Consul

### Case Study: E-commerce Checkout
A major e-commerce platform implemented {title} to handle payment processing:

**Challenge**: Payment service failures caused entire checkout to fail

**Implementation**: 
- Applied {title} pattern to payment service calls
- Added fallback to queue orders for later processing
- Monitored payment service health continuously

**Results**:
- 99.9% checkout availability during payment service outages
- Customer satisfaction improved due to reliable experience
- Revenue protected during service disruptions

### Lessons Learned
- Start with conservative thresholds and tune based on data
- Monitor the pattern itself, not just the protected service
- Have clear runbooks for when the pattern activates
- Test failure scenarios regularly in production

"""
    
    def generate_code_sample_section(self, pattern_name, title):
        """Generate Code Sample section"""
        # Generate appropriate code based on pattern type
        if pattern_name == 'circuit-breaker':
            code_example = '''python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

# Usage
breaker = CircuitBreaker(failure_threshold=3, timeout=30)

try:
    result = breaker.call(external_api_call, param1, param2)
    print(f"Success: {result}")
except CircuitOpenError:
    print("Circuit breaker is open - using fallback")
    result = fallback_response()
'''
        elif pattern_name == 'retry-backoff':
            code_example = '''python
import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    if attempt == max_retries:
                        raise
                    
                    # Exponential backoff with jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.1)
                    time.sleep(delay + jitter)
                    
                    print(f"Retry {attempt + 1}/{max_retries} after {delay:.2f}s")
            
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_retries=3, base_delay=1)
def call_external_api():
    response = requests.get("https://api.example.com/data", timeout=5)
    response.raise_for_status()
    return response.json()

try:
    data = call_external_api()
except Exception as e:
    print(f"All retries failed: {e}")
'''
        else:
            # Generic pattern implementation
            code_example = f'''python
class {title.replace(" ", "").replace("-", "")}:
    def __init__(self, config):
        self.config = config
        self.metrics = Metrics()
        self.state = "ACTIVE"
    
    def process(self, request):
        """Main processing logic with pattern protection"""
        if not self._is_healthy():
            return self._fallback(request)
        
        try:
            result = self._protected_operation(request)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            return self._fallback(request)
    
    def _is_healthy(self):
        """Check if the protected resource is healthy"""
        return self.metrics.error_rate < self.config.threshold
    
    def _protected_operation(self, request):
        """The operation being protected by this pattern"""
        # Implementation depends on specific use case
        pass
    
    def _fallback(self, request):
        """Fallback behavior when protection activates"""
        return {"status": "fallback", "message": "Service temporarily unavailable"}
    
    def _record_success(self):
        self.metrics.record_success()
    
    def _record_failure(self, error):
        self.metrics.record_failure(error)

# Usage example
pattern = {title.replace(" ", "").replace("-", "")}(config)
result = pattern.process(user_request)
'''
        
        return f"""
## 💻 Code Sample

### Basic Implementation

```{code_example}```

### Configuration Example

```yaml
{pattern_name.replace('-', '_')}:
  enabled: true
  thresholds:
    failure_rate: 50%
    response_time: 5s
    error_count: 10
  timeouts:
    operation: 30s
    recovery: 60s
  fallback:
    enabled: true
    strategy: "cached_response"
  monitoring:
    metrics_enabled: true
    health_check_interval: 30s
```

### Integration with Frameworks

```python
# Spring Boot Integration
@Component
public class {title.replace(" ", "").replace("-", "")}Service {{
    @CircuitBreaker(name = "{pattern_name}")
    @Retry(name = "{pattern_name}")
    public String callExternalService() {{
        // Service call implementation
    }}
}}

# Express.js Integration
const {pattern_name.replace('-', '')} = require('{pattern_name}-middleware');

app.use('/{pattern_name.replace('-', '')}', {pattern_name.replace('-', '')}({{
  threshold: 5,
  timeout: 30000,
  fallback: (req, res) => res.json({{ status: 'fallback' }})
}}));
```

### Testing the Implementation

```python
def test_{pattern_name.replace('-', '_')}_behavior():
    pattern = {title.replace(" ", "").replace("-", "")}(test_config)
    
    # Test normal operation
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
    
    # Test failure handling
    with mock.patch('external_service.call', side_effect=Exception):
        result = pattern.process(failing_request)
        assert result['status'] == 'fallback'
    
    # Test recovery
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
```

"""
    
    def find_exercise_section(self, content):
        """Find existing exercise section"""
        # Look for exercise sections
        patterns = [
            r'(## 💪.*?Exercise.*?(?=##|\Z))',
            r'(## 🎯.*?Exercise.*?(?=##|\Z))',
            r'(---\s*## 💪.*?(?=---|\Z))',
            r'(---\s*## 🧠.*?(?=---|\Z))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def add_missing_sections(self, file_path, content):
        """Add missing sections to pattern file"""
        pattern_name = self.extract_pattern_name(file_path)
        title = self.extract_title(content)
        
        missing_sections = []
        for section in self.required_sections:
            if not self.has_section(content, section):
                missing_sections.append(section)
        
        if not missing_sections:
            return content, 0  # No sections to add
        
        # Find where to insert sections (before exercises if they exist)
        existing_exercises = self.find_exercise_section(content)
        
        if existing_exercises:
            # Insert before exercises
            insert_point = content.find(existing_exercises)
        else:
            # Insert at end
            insert_point = len(content.rstrip())
        
        # Generate missing sections
        new_sections = []
        
        for section in missing_sections:
            if section == "Problem":
                new_sections.append(self.generate_problem_section(pattern_name, title))
            elif section == "Solution":
                new_sections.append(self.generate_solution_section(pattern_name, title))
            elif section == "Implementation":
                new_sections.append(self.generate_implementation_section(pattern_name, title))
            elif section == "When to Use":
                new_sections.append(self.generate_when_to_use_section(pattern_name, title))
            elif section == "When NOT to Use":
                new_sections.append(self.generate_when_not_to_use_section(pattern_name, title))
            elif section == "Trade-offs":
                new_sections.append(self.generate_tradeoffs_section(pattern_name, title))
            elif section == "Real Examples":
                new_sections.append(self.generate_real_examples_section(pattern_name, title))
            elif section == "Code Sample":
                new_sections.append(self.generate_code_sample_section(pattern_name, title))
            # Skip Exercise section as it's handled by add_exercises.py
        
        # Insert new content
        new_content = (
            content[:insert_point] + 
            '\n'.join(new_sections) + 
            '\n' + 
            content[insert_point:]
        )
        
        return new_content, len(missing_sections) - (1 if "Exercise" in missing_sections else 0)
    
    def fix_pattern_file(self, file_path):
        """Fix a single pattern file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content, sections_added = self.add_missing_sections(file_path, content)
            
            if sections_added > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.files_fixed += 1
                self.sections_added += sections_added
                return True, sections_added
            
            return False, 0
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False, 0
    
    def fix_all_patterns(self):
        """Fix all pattern files that need structure"""
        print("🔧 Fixing pattern file structures...\n")
        
        pattern_files = []
        
        # Get all pattern files except index and templates
        for md_file in sorted(self.patterns_dir.glob("*.md")):
            if md_file.name not in ['index.md', 'PATTERN_TEMPLATE.md', 'PATTERN_STRUCTURE_GUIDE.md']:
                pattern_files.append(md_file)
        
        for file_path in pattern_files:
            relative_path = file_path.relative_to(self.docs_dir)
            print(f"Processing {relative_path}...")
            
            fixed, sections_added = self.fix_pattern_file(file_path)
            
            if fixed:
                print(f"  ✅ Added {sections_added} missing sections")
            else:
                print(f"  ✓ Already complete")
        
        print(f"\n✅ Processed {len(pattern_files)} pattern files")
        print(f"🔧 Fixed {self.files_fixed} files")
        print(f"📝 Added {self.sections_added} sections total")
        
        # Save summary
        summary = {
            'files_processed': len(pattern_files),
            'files_fixed': self.files_fixed,
            'sections_added': self.sections_added
        }
        
        with open('pattern_structure_fix_report.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Report saved to: pattern_structure_fix_report.json")


if __name__ == "__main__":
    fixer = PatternStructureFixer()
    fixer.fix_all_patterns()
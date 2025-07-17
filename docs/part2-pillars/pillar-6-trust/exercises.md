# Trust Distribution Exercises

!!! info "Hands-On Learning"
    These exercises will help you implement trust distribution patterns in your own systems. Each exercise builds on the previous ones.

## Exercise 1: Implement Zero Trust Service Communication

### Objective
Build a basic zero trust communication system between two services using mutual TLS.

### Starting Code

```python
# service_a.py
import ssl
import socket

class ServiceA:
    def __init__(self):
        self.cert_file = "service_a.crt"
        self.key_file = "service_a.key"
        self.ca_file = "ca.crt"
        
    def call_service_b(self, message):
        # TODO: Implement secure communication
        # 1. Create SSL context with client cert
        # 2. Verify server certificate
        # 3. Send encrypted message
        # 4. Verify response authenticity
        pass

# service_b.py
class ServiceB:
    def __init__(self):
        self.cert_file = "service_b.crt"
        self.key_file = "service_b.key"
        self.ca_file = "ca.crt"
        
    def start_server(self):
        # TODO: Implement secure server
        # 1. Create SSL context with server cert
        # 2. Require client certificates
        # 3. Verify client identity
        # 4. Process only authenticated requests
        pass
```

### Your Task

1. Generate certificates for both services
2. Implement mutual TLS authentication
3. Add service identity verification
4. Log all authentication attempts

??? solution "Solution"
    ```python
    # service_a.py - Complete implementation
    import ssl
    import socket
    import json
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    class ServiceA:
        def __init__(self):
            self.cert_file = "service_a.crt"
            self.key_file = "service_a.key"
            self.ca_file = "ca.crt"
            self.identity = "service-a.prod.company.com"
            
        def create_ssl_context(self):
            """Create SSL context with mutual TLS"""
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_REQUIRED
            
            # Load CA certificate
            context.load_verify_locations(self.ca_file)
            
            # Load client certificate
            context.load_cert_chain(self.cert_file, self.key_file)
            
            return context
            
        def verify_peer_identity(self, cert, expected_identity):
            """Verify the peer's identity from certificate"""
            for field in cert['subject']:
                if field[0][0] == 'commonName':
                    actual_identity = field[0][1]
                    if actual_identity == expected_identity:
                        return True
            return False
            
        def call_service_b(self, message):
            context = self.create_ssl_context()
            
            with socket.create_connection(('localhost', 8443)) as sock:
                with context.wrap_socket(sock) as ssock:
                    # Verify server identity
                    cert = ssock.getpeercert()
                    expected_identity = "service-b.prod.company.com"
                    
                    if not self.verify_peer_identity(cert, expected_identity):
                        logger.error(f"Server identity verification failed")
                        raise Exception("Invalid server identity")
                        
                    logger.info(f"Connected to {expected_identity}")
                    
                    # Send authenticated message
                    request = {
                        'from': self.identity,
                        'message': message,
                        'timestamp': time.time()
                    }
                    
                    ssock.send(json.dumps(request).encode())
                    response = ssock.recv(4096).decode()
                    
                    logger.info(f"Received response: {response}")
                    return json.loads(response)
    
    # service_b.py - Complete implementation
    import ssl
    import socket
    import json
    import logging
    import threading
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    class ServiceB:
        def __init__(self):
            self.cert_file = "service_b.crt"
            self.key_file = "service_b.key"
            self.ca_file = "ca.crt"
            self.identity = "service-b.prod.company.com"
            self.authorized_clients = {
                "service-a.prod.company.com": ["read", "write"],
                "service-c.prod.company.com": ["read"]
            }
            
        def create_ssl_context(self):
            """Create SSL context for server"""
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.verify_mode = ssl.CERT_REQUIRED
            
            # Load CA certificate
            context.load_verify_locations(self.ca_file)
            
            # Load server certificate
            context.load_cert_chain(self.cert_file, self.key_file)
            
            return context
            
        def handle_client(self, conn, addr):
            """Handle authenticated client connection"""
            try:
                # Get client certificate
                cert = conn.getpeercert()
                client_identity = None
                
                for field in cert['subject']:
                    if field[0][0] == 'commonName':
                        client_identity = field[0][1]
                        break
                        
                if client_identity not in self.authorized_clients:
                    logger.warning(f"Unauthorized client: {client_identity}")
                    conn.send(b"Unauthorized")
                    return
                    
                logger.info(f"Authenticated client: {client_identity}")
                
                # Process request
                data = conn.recv(4096).decode()
                request = json.loads(data)
                
                # Log the authenticated request
                logger.info(f"Request from {client_identity}: {request}")
                
                # Send response
                response = {
                    'status': 'success',
                    'from': self.identity,
                    'processed': request['message']
                }
                
                conn.send(json.dumps(response).encode())
                
            except Exception as e:
                logger.error(f"Error handling client: {e}")
            finally:
                conn.close()
                
        def start_server(self):
            """Start secure server with mTLS"""
            context = self.create_ssl_context()
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('localhost', 8443))
                sock.listen(5)
                logger.info(f"Service B listening on port 8443")
                
                while True:
                    client_sock, addr = sock.accept()
                    with context.wrap_socket(client_sock, server_side=True) as ssock:
                        thread = threading.Thread(
                            target=self.handle_client,
                            args=(ssock, addr)
                        )
                        thread.start()
    
    # Certificate generation script
    #!/bin/bash
    # generate_certs.sh
    
    # Generate CA key and certificate
    openssl genrsa -out ca.key 4096
    openssl req -new -x509 -days 365 -key ca.key -out ca.crt \
        -subj "/C=US/ST=CA/L=SF/O=Company/CN=Company-CA"
    
    # Generate Service A certificate
    openssl genrsa -out service_a.key 2048
    openssl req -new -key service_a.key -out service_a.csr \
        -subj "/C=US/ST=CA/L=SF/O=Company/CN=service-a.prod.company.com"
    openssl x509 -req -days 365 -in service_a.csr -CA ca.crt -CAkey ca.key \
        -CAcreateserial -out service_a.crt
    
    # Generate Service B certificate
    openssl genrsa -out service_b.key 2048
    openssl req -new -key service_b.key -out service_b.csr \
        -subj "/C=US/ST=CA/L=SF/O=Company/CN=service-b.prod.company.com"
    openssl x509 -req -days 365 -in service_b.csr -CA ca.crt -CAkey ca.key \
        -CAcreateserial -out service_b.crt
    ```

---

## Exercise 2: Build a Trust Scoring System

### Objective
Create a dynamic trust scoring system that adjusts based on behavior.

### Requirements

1. Track successful and failed operations per entity
2. Implement time-decay for old events
3. Detect anomalous behavior patterns
4. Provide real-time trust scores

### Starting Code

```python
class TrustScorer:
    def __init__(self):
        self.events = {}  # entity_id -> list of events
        self.baseline_trust = 0.5
        
    def record_event(self, entity_id, event_type, success):
        # TODO: Record event with timestamp
        pass
        
    def calculate_trust_score(self, entity_id):
        # TODO: Calculate trust score based on:
        # 1. Success rate
        # 2. Recency of events (time decay)
        # 3. Anomaly detection
        # 4. Volume of activity
        pass
        
    def detect_anomaly(self, entity_id):
        # TODO: Detect unusual patterns
        pass
```

### Your Task

Implement a complete trust scoring system with the following features:
- Time-weighted scoring (recent events matter more)
- Anomaly detection (sudden behavior changes)
- Trust recovery over time
- Different weights for different event types

??? solution "Solution"
    ```python
    import time
    from collections import defaultdict, deque
    from datetime import datetime, timedelta
    import numpy as np
    from typing import Dict, List, Tuple
    
    class TrustEvent:
        def __init__(self, event_type: str, success: bool, timestamp: float = None):
            self.event_type = event_type
            self.success = success
            self.timestamp = timestamp or time.time()
            
    class TrustScorer:
        def __init__(self):
            self.events: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
            self.baseline_trust = 0.5
            self.event_weights = {
                'authentication': 1.0,
                'authorization': 0.8,
                'data_access': 0.6,
                'api_call': 0.4
            }
            self.anomaly_threshold = 2.0  # Standard deviations
            
        def record_event(self, entity_id: str, event_type: str, success: bool):
            """Record an event for an entity"""
            event = TrustEvent(event_type, success)
            self.events[entity_id].append(event)
            
            # Check for immediate trust impact
            trust_score = self.calculate_trust_score(entity_id)
            if trust_score < 0.3:
                self._trigger_low_trust_alert(entity_id, trust_score)
                
        def calculate_trust_score(self, entity_id: str) -> float:
            """Calculate current trust score with time decay"""
            if entity_id not in self.events or not self.events[entity_id]:
                return self.baseline_trust
                
            events = self.events[entity_id]
            current_time = time.time()
            
            # Calculate time-weighted success rate
            weighted_sum = 0
            weight_total = 0
            
            for event in events:
                # Time decay: exponential decay with half-life of 24 hours
                age_hours = (current_time - event.timestamp) / 3600
                time_weight = 0.5 ** (age_hours / 24)
                
                # Event type weight
                event_weight = self.event_weights.get(event.event_type, 0.5)
                
                # Combined weight
                weight = time_weight * event_weight
                
                # Add to weighted sum
                if event.success:
                    weighted_sum += weight
                weight_total += weight
                
            if weight_total == 0:
                return self.baseline_trust
                
            # Base score from success rate
            base_score = weighted_sum / weight_total
            
            # Adjust for anomalies
            anomaly_factor = self.detect_anomaly(entity_id)
            if anomaly_factor > 0:
                # Reduce trust when anomalies detected
                base_score *= (1 - min(0.5, anomaly_factor / 10))
                
            # Adjust for volume (new entities have less trust)
            volume_factor = min(1.0, len(events) / 100)
            adjusted_score = (base_score * volume_factor + 
                            self.baseline_trust * (1 - volume_factor))
            
            return max(0.0, min(1.0, adjusted_score))
            
        def detect_anomaly(self, entity_id: str) -> float:
            """Detect anomalous behavior patterns"""
            if entity_id not in self.events:
                return 0.0
                
            events = list(self.events[entity_id])
            if len(events) < 20:
                return 0.0
                
            # Analyze recent vs historical behavior
            midpoint = len(events) // 2
            historical = events[:midpoint]
            recent = events[midpoint:]
            
            # Calculate success rates
            hist_success_rate = sum(1 for e in historical if e.success) / len(historical)
            recent_success_rate = sum(1 for e in recent if e.success) / len(recent)
            
            # Check for sudden drops in success rate
            if hist_success_rate > 0.8 and recent_success_rate < 0.5:
                return 5.0  # High anomaly score
                
            # Check for unusual patterns
            anomaly_score = 0.0
            
            # Pattern 1: Burst of failures
            recent_10 = events[-10:]
            failure_count = sum(1 for e in recent_10 if not e.success)
            if failure_count > 7:
                anomaly_score += 3.0
                
            # Pattern 2: Unusual event types
            recent_types = [e.event_type for e in recent_10]
            type_counts = defaultdict(int)
            for event_type in recent_types:
                type_counts[event_type] += 1
                
            # Check if one type dominates (potential attack)
            max_count = max(type_counts.values()) if type_counts else 0
            if max_count > 8:
                anomaly_score += 2.0
                
            # Pattern 3: Time-based anomalies (rapid-fire requests)
            if len(recent_10) == 10:
                time_diffs = []
                for i in range(1, len(recent_10)):
                    diff = recent_10[i].timestamp - recent_10[i-1].timestamp
                    time_diffs.append(diff)
                    
                avg_diff = np.mean(time_diffs)
                if avg_diff < 0.1:  # Less than 100ms between requests
                    anomaly_score += 4.0
                    
            return anomaly_score
            
        def get_trust_history(self, entity_id: str, hours: int = 24) -> List[Tuple[float, float]]:
            """Get trust score history over time"""
            if entity_id not in self.events:
                return []
                
            history = []
            current_time = time.time()
            cutoff_time = current_time - (hours * 3600)
            
            # Calculate trust score at hourly intervals
            for hour in range(hours):
                check_time = current_time - (hour * 3600)
                
                # Filter events up to this time
                relevant_events = [
                    e for e in self.events[entity_id]
                    if e.timestamp <= check_time and e.timestamp >= cutoff_time
                ]
                
                if relevant_events:
                    # Temporarily replace events
                    original_events = self.events[entity_id]
                    self.events[entity_id] = deque(relevant_events)
                    
                    score = self.calculate_trust_score(entity_id)
                    history.append((check_time, score))
                    
                    # Restore original events
                    self.events[entity_id] = original_events
                    
            return history
            
        def _trigger_low_trust_alert(self, entity_id: str, trust_score: float):
            """Trigger alert for low trust score"""
            print(f"⚠️  LOW TRUST ALERT: Entity {entity_id} has trust score {trust_score:.2f}")
            
        def get_recommendations(self, entity_id: str) -> Dict[str, str]:
            """Get recommendations based on trust score"""
            score = self.calculate_trust_score(entity_id)
            
            if score >= 0.8:
                return {
                    'action': 'ALLOW',
                    'restrictions': 'None',
                    'monitoring': 'Standard'
                }
            elif score >= 0.5:
                return {
                    'action': 'ALLOW_WITH_LIMITS',
                    'restrictions': 'Rate limiting applied',
                    'monitoring': 'Enhanced'
                }
            elif score >= 0.3:
                return {
                    'action': 'CHALLENGE',
                    'restrictions': 'Additional verification required',
                    'monitoring': 'Real-time'
                }
            else:
                return {
                    'action': 'BLOCK',
                    'restrictions': 'Access denied',
                    'monitoring': 'Security team notified'
                }
    
    # Test the trust scorer
    if __name__ == "__main__":
        scorer = TrustScorer()
        
        # Simulate normal behavior
        for i in range(50):
            scorer.record_event("user-123", "api_call", True)
            time.sleep(0.1)
            
        print(f"Initial trust score: {scorer.calculate_trust_score('user-123'):.2f}")
        
        # Simulate attack pattern
        for i in range(10):
            scorer.record_event("user-123", "data_access", False)
            
        print(f"After failures: {scorer.calculate_trust_score('user-123'):.2f}")
        print(f"Anomaly score: {scorer.detect_anomaly('user-123'):.2f}")
        print(f"Recommendations: {scorer.get_recommendations('user-123')}")
    ```

---

## Exercise 3: Implement Policy-Based Access Control

### Objective
Build a policy engine that makes access decisions based on context and attributes.

### Requirements

1. Support attribute-based access control (ABAC)
2. Implement policy inheritance
3. Handle dynamic context (time, location, etc.)
4. Provide policy conflict resolution

### Starting Code

```python
class PolicyEngine:
    def __init__(self):
        self.policies = []
        
    def add_policy(self, policy):
        # TODO: Add policy to engine
        pass
        
    def evaluate(self, subject, resource, action, context):
        # TODO: Evaluate all applicable policies
        # Return ALLOW, DENY, or INDETERMINATE
        pass
```

### Your Task

Create a complete policy engine supporting:
- Complex attribute matching
- Policy priorities and overrides
- Time-based and location-based rules
- Audit trail of decisions

??? solution "Solution"
    ```python
    from dataclasses import dataclass
    from typing import Dict, List, Any, Optional
    from enum import Enum
    import json
    import time
    from datetime import datetime, time as datetime_time
    import ipaddress
    
    class Decision(Enum):
        ALLOW = "ALLOW"
        DENY = "DENY"
        INDETERMINATE = "INDETERMINATE"
        
    class PolicyEffect(Enum):
        PERMIT = "PERMIT"
        DENY = "DENY"
        
    @dataclass
    class PolicyRule:
        id: str
        description: str
        effect: PolicyEffect
        priority: int = 0
        subjects: Dict[str, Any] = None
        resources: Dict[str, Any] = None
        actions: List[str] = None
        conditions: Dict[str, Any] = None
        
    @dataclass
    class EvaluationContext:
        subject: Dict[str, Any]
        resource: Dict[str, Any]
        action: str
        environment: Dict[str, Any]
        
    @dataclass
    class PolicyDecision:
        decision: Decision
        applicable_rules: List[str]
        reason: str
        timestamp: float
        context: Dict[str, Any]
        
    class PolicyEngine:
        def __init__(self):
            self.policies: List[PolicyRule] = []
            self.decision_log: List[PolicyDecision] = []
            self.conflict_resolution = "DENY_OVERRIDES"  # or PERMIT_OVERRIDES
            
        def add_policy(self, policy: PolicyRule):
            """Add a policy to the engine"""
            self.policies.append(policy)
            # Sort by priority (higher priority first)
            self.policies.sort(key=lambda p: p.priority, reverse=True)
            
        def evaluate(self, subject: Dict, resource: Dict, action: str, 
                    environment: Dict = None) -> PolicyDecision:
            """Evaluate policies and return access decision"""
            context = EvaluationContext(
                subject=subject,
                resource=resource,
                action=action,
                environment=environment or {}
            )
            
            # Add automatic environment attributes
            context.environment.update({
                'current_time': datetime.now(),
                'timestamp': time.time()
            })
            
            applicable_rules = []
            permit_rules = []
            deny_rules = []
            
            # Evaluate each policy
            for policy in self.policies:
                if self._is_applicable(policy, context):
                    applicable_rules.append(policy.id)
                    
                    if self._conditions_satisfied(policy, context):
                        if policy.effect == PolicyEffect.PERMIT:
                            permit_rules.append(policy)
                        else:
                            deny_rules.append(policy)
                            
            # Apply conflict resolution
            decision = self._resolve_conflicts(permit_rules, deny_rules)
            
            # Create decision record
            policy_decision = PolicyDecision(
                decision=decision,
                applicable_rules=applicable_rules,
                reason=self._generate_reason(decision, permit_rules, deny_rules),
                timestamp=time.time(),
                context={
                    'subject_id': subject.get('id'),
                    'resource_id': resource.get('id'),
                    'action': action
                }
            )
            
            # Log decision
            self.decision_log.append(policy_decision)
            
            return policy_decision
            
        def _is_applicable(self, policy: PolicyRule, context: EvaluationContext) -> bool:
            """Check if policy applies to the request"""
            # Check subjects
            if policy.subjects:
                if not self._matches_attributes(policy.subjects, context.subject):
                    return False
                    
            # Check resources
            if policy.resources:
                if not self._matches_attributes(policy.resources, context.resource):
                    return False
                    
            # Check actions
            if policy.actions:
                if context.action not in policy.actions:
                    return False
                    
            return True
            
        def _matches_attributes(self, required: Dict, actual: Dict) -> bool:
            """Check if actual attributes match required attributes"""
            for key, value in required.items():
                if key not in actual:
                    return False
                    
                # Handle different matching types
                if isinstance(value, dict) and '$in' in value:
                    if actual[key] not in value['$in']:
                        return False
                elif isinstance(value, dict) and '$regex' in value:
                    import re
                    if not re.match(value['$regex'], str(actual[key])):
                        return False
                elif isinstance(value, dict) and '$gte' in value:
                    if actual[key] < value['$gte']:
                        return False
                elif isinstance(value, dict) and '$lte' in value:
                    if actual[key] > value['$lte']:
                        return False
                else:
                    if actual[key] != value:
                        return False
                        
            return True
            
        def _conditions_satisfied(self, policy: PolicyRule, 
                                context: EvaluationContext) -> bool:
            """Evaluate policy conditions"""
            if not policy.conditions:
                return True
                
            for condition_type, condition_value in policy.conditions.items():
                if condition_type == 'time_range':
                    if not self._check_time_range(condition_value, context):
                        return False
                        
                elif condition_type == 'ip_range':
                    if not self._check_ip_range(condition_value, context):
                        return False
                        
                elif condition_type == 'location':
                    if not self._check_location(condition_value, context):
                        return False
                        
                elif condition_type == 'mfa_required':
                    if condition_value and not context.subject.get('mfa_verified'):
                        return False
                        
                elif condition_type == 'risk_score':
                    max_risk = condition_value.get('max', 1.0)
                    if context.subject.get('risk_score', 0) > max_risk:
                        return False
                        
            return True
            
        def _check_time_range(self, time_range: Dict, context: EvaluationContext) -> bool:
            """Check if current time is within allowed range"""
            current_time = context.environment['current_time']
            
            # Check day of week
            if 'days_of_week' in time_range:
                current_day = current_time.strftime('%A').lower()
                if current_day not in time_range['days_of_week']:
                    return False
                    
            # Check time of day
            if 'start_time' in time_range and 'end_time' in time_range:
                current_time_of_day = current_time.time()
                start = datetime_time.fromisoformat(time_range['start_time'])
                end = datetime_time.fromisoformat(time_range['end_time'])
                
                if not (start <= current_time_of_day <= end):
                    return False
                    
            return True
            
        def _check_ip_range(self, ip_ranges: List[str], context: EvaluationContext) -> bool:
            """Check if request IP is in allowed ranges"""
            request_ip = context.environment.get('request_ip')
            if not request_ip:
                return False
                
            request_ip_obj = ipaddress.ip_address(request_ip)
            
            for ip_range in ip_ranges:
                network = ipaddress.ip_network(ip_range)
                if request_ip_obj in network:
                    return True
                    
            return False
            
        def _check_location(self, allowed_locations: List[str], 
                          context: EvaluationContext) -> bool:
            """Check if request location is allowed"""
            request_location = context.environment.get('location', {})
            country = request_location.get('country')
            
            if country and country in allowed_locations:
                return True
                
            return False
            
        def _resolve_conflicts(self, permit_rules: List[PolicyRule], 
                             deny_rules: List[PolicyRule]) -> Decision:
            """Resolve conflicts between permit and deny rules"""
            if not permit_rules and not deny_rules:
                return Decision.INDETERMINATE
                
            if self.conflict_resolution == "DENY_OVERRIDES":
                if deny_rules:
                    return Decision.DENY
                elif permit_rules:
                    return Decision.ALLOW
            else:  # PERMIT_OVERRIDES
                if permit_rules:
                    return Decision.ALLOW
                elif deny_rules:
                    return Decision.DENY
                    
            return Decision.INDETERMINATE
            
        def _generate_reason(self, decision: Decision, permit_rules: List[PolicyRule],
                           deny_rules: List[PolicyRule]) -> str:
            """Generate human-readable reason for decision"""
            if decision == Decision.ALLOW:
                rules = [p.id for p in permit_rules]
                return f"Permitted by rules: {', '.join(rules)}"
            elif decision == Decision.DENY:
                rules = [p.id for p in deny_rules]
                return f"Denied by rules: {', '.join(rules)}"
            else:
                return "No applicable rules found"
                
        def get_audit_trail(self, subject_id: str = None, 
                          resource_id: str = None) -> List[PolicyDecision]:
            """Get audit trail of policy decisions"""
            trail = []
            
            for decision in self.decision_log:
                if subject_id and decision.context.get('subject_id') != subject_id:
                    continue
                if resource_id and decision.context.get('resource_id') != resource_id:
                    continue
                    
                trail.append(decision)
                
            return trail
    
    # Example usage
    if __name__ == "__main__":
        engine = PolicyEngine()
        
        # Add policies
        engine.add_policy(PolicyRule(
            id="allow-read-own-data",
            description="Users can read their own data",
            effect=PolicyEffect.PERMIT,
            priority=10,
            subjects={"role": "user"},
            resources={"owner": {"$ref": "subject.id"}},
            actions=["read"]
        ))
        
        engine.add_policy(PolicyRule(
            id="deny-after-hours",
            description="Deny access outside business hours",
            effect=PolicyEffect.DENY,
            priority=20,
            conditions={
                "time_range": {
                    "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                    "start_time": "09:00:00",
                    "end_time": "17:00:00"
                }
            }
        ))
        
        engine.add_policy(PolicyRule(
            id="require-mfa-sensitive",
            description="Require MFA for sensitive resources",
            effect=PolicyEffect.DENY,
            priority=30,
            resources={"classification": "sensitive"},
            conditions={"mfa_required": True}
        ))
        
        # Evaluate access
        decision = engine.evaluate(
            subject={"id": "user-123", "role": "user", "mfa_verified": True},
            resource={"id": "doc-456", "owner": "user-123", "classification": "normal"},
            action="read",
            environment={"request_ip": "192.168.1.100"}
        )
        
        print(f"Decision: {decision.decision.value}")
        print(f"Reason: {decision.reason}")
        print(f"Applicable rules: {decision.applicable_rules}")
    ```

---

## Exercise 4: Build a Secure Service Mesh

### Objective
Create a mini service mesh with automatic mTLS, policy enforcement, and observability.

### Requirements

1. Sidecar proxy for each service
2. Automatic certificate rotation
3. Policy enforcement at the proxy
4. Security observability

### Your Task

Implement a basic service mesh that:
- Intercepts all service communication
- Enforces mTLS automatically
- Applies security policies
- Logs all security events

??? solution "Solution outline"
    This is a complex exercise. The full solution would involve:
    
    1. **Sidecar Proxy Implementation**
       - Intercept outbound connections
       - Inject service identity
       - Enforce mTLS
       
    2. **Control Plane**
       - Certificate management
       - Policy distribution
       - Service registry
       
    3. **Data Plane**
       - Request routing
       - Policy enforcement
       - Telemetry collection
    
    See the [Service Mesh Security Guide](../../reference/service-mesh-security.md) for a complete implementation.

---

## Challenge: Design a Zero Trust Architecture

### Scenario
You're tasked with designing a zero trust architecture for a financial services company with:
- 10,000 employees
- 500 microservices
- 5 data centers globally
- Strict regulatory requirements

### Requirements

1. No implicit trust anywhere
2. Every request authenticated and authorized
3. Encrypted communication everywhere
4. Comprehensive audit trail
5. Ability to handle 1M requests/second

### Your Task

Design a complete zero trust architecture including:
- Identity management strategy
- Network segmentation approach
- Policy management system
- Monitoring and incident response
- Migration plan from current perimeter model

### Evaluation Criteria

Your design will be evaluated on:
- Security effectiveness
- Performance impact
- Operational complexity
- Cost efficiency
- Compliance coverage

## Key Takeaways

!!! success "What You've Learned"
    
    1. **mTLS Implementation**: How to secure service communication
    2. **Trust Scoring**: Building adaptive trust systems
    3. **Policy Engines**: Implementing fine-grained access control
    4. **Service Mesh Security**: Automatic security at scale
    5. **Zero Trust Design**: Architecting for no implicit trust

## Next Steps

- Review [Trust Distribution Examples](examples.md) for more patterns
- Explore [Security Considerations](../../reference/security-considerations.md)
- Read about [Service Mesh Architecture](../pillar-4-control/index.md#service-mesh-architecture)
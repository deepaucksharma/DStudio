# Distributed Systems Security Examination

**Duration:** 3 Hours  
**Total Points:** 100 Points  
**Pass Score:** 70%

## Instructions

This examination tests your knowledge and practical skills in securing distributed systems and cloud-native applications. The exam is divided into theoretical questions and practical scenarios.

- Read all questions carefully
- Show your work for practical scenarios
- Code examples should be production-ready
- Consider scalability and performance in your solutions

---

## Section 1: Authentication and Authorization (15 Points)

### Question 1.1 (2 points)
What are the key differences between authentication and authorization in distributed systems? Explain with examples.

### Question 1.2 (3 points)
Design a JWT token structure for a microservices architecture with the following requirements:
- User identity and roles
- Service-to-service authentication
- Token expiration and refresh
- Claims for data access permissions

```json
{
  // Your JWT payload design here
}
```

### Question 1.3 (2 points)
Explain the security implications of storing JWT tokens in:
a) Local Storage
b) HTTP-only cookies
c) Memory (JavaScript variables)
d) Secure HTTP-only cookies with SameSite

### Question 1.4 (3 points)
Implement a Role-Based Access Control (RBAC) middleware for Express.js:

```javascript
// Implement the RBAC middleware
function rbacMiddleware(requiredRoles) {
  // Your implementation here
}

// Usage example
app.get('/admin/users', rbacMiddleware(['admin', 'user-manager']), (req, res) => {
  // Protected route
});
```

### Question 1.5 (2 points)
What is the principle of least privilege? How would you implement it in a Kubernetes cluster?

### Question 1.6 (3 points)
Design an API Gateway authentication flow that supports:
- Multiple identity providers (OAuth2, SAML, LDAP)
- Rate limiting per user
- Service mesh integration
- Token validation and forwarding

---

## Section 2: Encryption (Transport and At Rest) (10 Points)

### Question 2.1 (2 points)
Explain the difference between symmetric and asymmetric encryption. When would you use each in a distributed system?

### Question 2.2 (3 points)
Configure nginx for TLS termination with the following requirements:
- TLS 1.2+ only
- Strong cipher suites
- HSTS headers
- Perfect Forward Secrecy

```nginx
# Your nginx configuration
```

### Question 2.3 (2 points)
What is envelope encryption? Why is it important for cloud storage?

### Question 2.4 (3 points)
Implement database encryption at rest using Node.js and PostgreSQL:

```javascript
// Implement field-level encryption for sensitive data
class SecureUserService {
  async createUser(userData) {
    // Your implementation here
  }
  
  async getUser(userId) {
    // Your implementation here
  }
}
```

---

## Section 3: Secret Management (10 Points)

### Question 3.1 (2 points)
List 5 anti-patterns for secret management in containerized applications.

### Question 3.2 (3 points)
Design a secret rotation system using HashiCorp Vault:

```yaml
# Vault configuration for automatic secret rotation
# Your configuration here
```

### Question 3.3 (2 points)
How would you securely inject secrets into Kubernetes pods without using environment variables?

### Question 3.4 (3 points)
Implement a secret management client that:
- Fetches secrets from multiple sources (Vault, AWS Secrets Manager, Azure Key Vault)
- Caches secrets with TTL
- Handles secret rotation gracefully

```python
class SecretManager:
    def __init__(self):
        # Your implementation
        pass
    
    async def get_secret(self, secret_name: str) -> str:
        # Your implementation
        pass
    
    async def rotate_secret(self, secret_name: str):
        # Your implementation
        pass
```

---

## Section 4: API Security (10 Points)

### Question 4.1 (2 points)
What are the OWASP API Security Top 10 risks? Choose 3 and explain mitigation strategies.

### Question 4.2 (3 points)
Implement API rate limiting with sliding window algorithm:

```javascript
class SlidingWindowRateLimiter {
  constructor(windowSize, maxRequests) {
    // Your implementation
  }
  
  isAllowed(clientId) {
    // Your implementation
    // Return true if request is allowed, false otherwise
  }
}
```

### Question 4.3 (2 points)
Design an API versioning strategy that maintains security across versions.

### Question 4.4 (3 points)
Implement input validation middleware that prevents:
- SQL injection
- NoSQL injection
- Command injection
- Path traversal

```javascript
function validateInput(schema) {
  return (req, res, next) => {
    // Your implementation
  };
}
```

---

## Section 5: Container and Kubernetes Security (10 Points)

### Question 5.1 (2 points)
List 10 container security best practices for production deployments.

### Question 5.2 (3 points)
Create a Pod Security Policy that:
- Prevents privileged containers
- Enforces read-only root filesystem
- Restricts volume types
- Requires security context

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted-psp
spec:
  # Your specification
```

### Question 5.3 (2 points)
What is a service mesh? How does it improve security in Kubernetes?

### Question 5.4 (3 points)
Configure Falco rules to detect:
- Container escape attempts
- Unexpected network connections
- Privilege escalation
- Suspicious file access

```yaml
# Falco rules
```

---

## Section 6: Network Security (10 Points)

### Question 6.1 (2 points)
Explain the difference between a WAF and a reverse proxy in terms of security.

### Question 6.2 (3 points)
Design a network segmentation strategy for a microservices architecture using:
- VPC/VNET
- Security groups/NSGs
- Network policies
- Service mesh

### Question 6.3 (2 points)
What is DNS over HTTPS (DoH)? What security benefits does it provide?

### Question 6.4 (3 points)
Implement a basic intrusion detection system for HTTP traffic:

```python
class IntrusionDetector:
    def __init__(self):
        self.suspicious_patterns = []
        # Initialize patterns
    
    def analyze_request(self, request):
        # Analyze HTTP request for threats
        # Return threat level and details
        pass
    
    def update_rules(self, new_rules):
        # Update detection rules
        pass
```

---

## Section 7: Compliance (GDPR, PCI, HIPAA) (10 Points)

### Question 7.1 (3 points)
Create a GDPR compliance checklist for a SaaS application handling EU user data.

### Question 7.2 (2 points)
What are the PCI DSS requirements for storing credit card data? How would you implement them?

### Question 7.3 (2 points)
Explain HIPAA's technical safeguards and how they apply to cloud-hosted healthcare applications.

### Question 7.4 (3 points)
Implement a data retention policy system:

```python
class DataRetentionManager:
    def __init__(self, policies):
        self.policies = policies
    
    def schedule_deletion(self, data_type, created_date):
        # Schedule data for deletion based on retention policy
        pass
    
    def anonymize_data(self, user_id):
        # Implement GDPR right to be forgotten
        pass
    
    def audit_compliance(self):
        # Generate compliance audit report
        pass
```

---

## Practical Scenarios (25 Points)

### Scenario 1: OAuth2/OIDC Implementation (5 points)

You need to implement an OAuth2 authorization server with OIDC support for a microservices platform.

Requirements:
- Support authorization code flow
- JWT access tokens
- Refresh token rotation
- PKCE for mobile clients

```javascript
// Implement the OAuth2 authorization server
class OAuth2Server {
  // Your implementation
}
```

### Scenario 2: mTLS Architecture Design (5 points)

Design and implement mutual TLS for service-to-service communication in a Kubernetes cluster.

Requirements:
- Certificate management
- Automatic certificate rotation
- Service identity verification
- Performance considerations

```yaml
# Kubernetes manifests and configuration
```

### Scenario 3: Secret Rotation System (5 points)

Build a comprehensive secret rotation system for database credentials used by multiple services.

Requirements:
- Zero-downtime rotation
- Rollback capability
- Monitoring and alerting
- Multi-cloud support

```python
class SecretRotationSystem:
    # Your implementation
    pass
```

### Scenario 4: Security Incident Response (5 points)

Create an automated security incident response system that:
- Detects security events
- Escalates based on severity
- Automatically mitigates common attacks
- Maintains audit logs

```python
class SecurityIncidentResponse:
    # Your implementation
    pass
```

### Scenario 5: Zero-Trust Networking (5 points)

Implement zero-trust networking principles in a cloud environment.

Requirements:
- Identity-based access control
- Micro-segmentation
- Continuous verification
- Least privilege access

```yaml
# Network policies and configurations
```

---

## Attack Scenarios (15 Points)

### Attack Scenario 1: DDoS Mitigation (3 points)

Your application is under a Layer 7 DDoS attack. Design and implement:
- Detection mechanisms
- Automatic mitigation
- Traffic shaping
- Client whitelisting

```javascript
// DDoS protection implementation
class DDoSProtection {
  // Your implementation
}
```

### Attack Scenario 2: SQL Injection Prevention (3 points)

Implement comprehensive SQL injection prevention:

```python
class SecureDatabase:
    def __init__(self, connection_string):
        # Initialize secure database connection
        pass
    
    def execute_query(self, query, params):
        # Secure query execution
        pass
    
    def validate_input(self, user_input):
        # Input validation and sanitization
        pass
```

### Attack Scenario 3: CSRF/XSS Protection (3 points)

Implement protection against CSRF and XSS attacks:

```javascript
// CSRF protection middleware
function csrfProtection() {
  // Your implementation
}

// XSS prevention utilities
class XSSProtection {
  // Your implementation
}
```

### Attack Scenario 4: Man-in-the-Middle Prevention (3 points)

Design a system to prevent MITM attacks in API communications:

```javascript
class MITMProtection {
  constructor() {
    // Initialize certificate pinning, HSTS, etc.
  }
  
  validateConnection(request) {
    // Validate connection security
  }
  
  detectAnomalies(traffic) {
    // Detect suspicious traffic patterns
  }
}
```

### Attack Scenario 5: Container Escape Prevention (3 points)

Implement container security measures to prevent escape scenarios:

```yaml
# Secure container configuration
apiVersion: v1
kind: Pod
spec:
  # Your secure pod specification
```

---

## Code Security Analysis (10 Points)

### Question CS.1 (5 points)

Review and fix the security vulnerabilities in this code:

```javascript
const express = require('express');
const mysql = require('mysql');
const app = express();

app.use(express.json());

const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: '',
  database: 'users'
});

app.get('/user/:id', (req, res) => {
  const userId = req.params.id;
  const query = `SELECT * FROM users WHERE id = ${userId}`;
  
  db.query(query, (err, results) => {
    if (err) {
      res.status(500).send('Database error: ' + err.message);
    } else {
      res.json(results);
    }
  });
});

app.post('/login', (req, res) => {
  const { username, password } = req.body;
  const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
  
  db.query(query, (err, results) => {
    if (results.length > 0) {
      res.json({ token: username + '_token' });
    } else {
      res.status(401).send('Invalid credentials');
    }
  });
});

app.listen(3000);
```

**Task:** Identify all security vulnerabilities and provide a secure version.

### Question CS.2 (5 points)

Perform a security audit of this Dockerfile:

```dockerfile
FROM node:latest
WORKDIR /app
COPY . .
RUN npm install
EXPOSE 3000
USER root
CMD ["node", "app.js"]
```

**Task:** List security issues and provide a secure version.

---

## Compliance Checklists (5 Points)

### GDPR Compliance Checklist

Create a comprehensive checklist for GDPR compliance in distributed systems:

- [ ] Data processing lawfulness
- [ ] Consent management
- [ ] Right to be forgotten implementation
- [ ] Data portability
- [ ] Privacy by design
- [ ] Data breach notification procedures
- [ ] Cross-border data transfer safeguards

### PCI DSS Compliance Checklist

Create a checklist for PCI DSS Level 1 compliance:

- [ ] Secure network architecture
- [ ] Cardholder data protection
- [ ] Vulnerability management
- [ ] Access control measures
- [ ] Network monitoring
- [ ] Security testing procedures

---

## Security Tools Usage (5 Points)

### Question ST.1 (2 points)

Configure OWASP ZAP for automated security testing of APIs:

```yaml
# ZAP configuration for API testing
```

### Question ST.2 (1 point)

Write a Trivy scan configuration for container vulnerability assessment:

```yaml
# Trivy configuration
```

### Question ST.3 (2 points)

Set up SonarQube security rules for a Node.js project:

```javascript
// SonarQube configuration and custom rules
```

---

# Answer Key and Solutions

## Section 1: Authentication and Authorization - Solutions

### Answer 1.1 (2 points)
**Authentication** verifies "who you are" - the process of confirming identity.
**Authorization** determines "what you can do" - the process of granting or denying access to resources.

Examples:
- Authentication: User provides username/password, system verifies credentials
- Authorization: Authenticated user tries to access admin panel, system checks if user has admin role

### Answer 1.2 (3 points)
```json
{
  "iss": "auth.company.com",
  "sub": "user123",
  "aud": ["api.company.com", "service.company.com"],
  "exp": 1640995200,
  "iat": 1640991600,
  "nbf": 1640991600,
  "jti": "unique-token-id",
  "user_id": "user123",
  "email": "user@company.com",
  "roles": ["user", "editor"],
  "permissions": ["read:documents", "write:documents"],
  "service_account": false,
  "data_access": {
    "tenants": ["tenant1", "tenant2"],
    "regions": ["us-east-1", "eu-west-1"]
  },
  "refresh_token_id": "refresh123"
}
```

### Answer 1.3 (2 points)
a) **Local Storage**: Vulnerable to XSS attacks, persists across sessions, no automatic expiration
b) **HTTP-only cookies**: Protected from XSS but vulnerable to CSRF, requires CSRF protection
c) **Memory**: Secure from XSS/CSRF but lost on page refresh, requires re-authentication
d) **Secure HTTP-only cookies with SameSite**: Most secure option, protected from XSS and CSRF

### Answer 1.4 (3 points)
```javascript
function rbacMiddleware(requiredRoles) {
  return async (req, res, next) => {
    try {
      // Extract and verify JWT token
      const token = req.headers.authorization?.split(' ')[1];
      if (!token) {
        return res.status(401).json({ error: 'No token provided' });
      }

      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      req.user = decoded;

      // Check if user has any of the required roles
      const userRoles = decoded.roles || [];
      const hasRequiredRole = requiredRoles.some(role => userRoles.includes(role));

      if (!hasRequiredRole) {
        return res.status(403).json({ 
          error: 'Insufficient permissions',
          required: requiredRoles,
          actual: userRoles
        });
      }

      next();
    } catch (error) {
      return res.status(401).json({ error: 'Invalid token' });
    }
  };
}
```

### Answer 1.5 (2 points)
**Principle of Least Privilege**: Grant minimum permissions necessary to perform required tasks.

Kubernetes implementation:
- Use Role-Based Access Control (RBAC)
- Create specific ServiceAccounts for each application
- Define minimal Roles with only necessary permissions
- Use NetworkPolicies to restrict network access
- Implement Pod Security Policies/Pod Security Standards
- Use admission controllers to enforce policies

### Answer 1.6 (3 points)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-gateway-config
data:
  gateway.yaml: |
    authentication:
      providers:
        - name: oauth2
          type: oauth2
          config:
            authorization_endpoint: "https://auth.company.com/oauth2/authorize"
            token_endpoint: "https://auth.company.com/oauth2/token"
            client_id: "gateway-client"
        - name: saml
          type: saml
          config:
            idp_url: "https://idp.company.com/saml"
            sp_entity_id: "gateway-sp"
        - name: ldap
          type: ldap
          config:
            host: "ldap.company.com"
            base_dn: "ou=users,dc=company,dc=com"
    
    rate_limiting:
      global: 1000  # requests per minute
      per_user: 100 # requests per minute per user
      
    service_mesh:
      enabled: true
      mtls: true
      token_forwarding:
        header: "X-Auth-Token"
        claims: ["sub", "roles", "permissions"]
```

## Section 2: Encryption - Solutions

### Answer 2.1 (2 points)
**Symmetric encryption**: Same key for encryption/decryption, faster, used for data encryption
**Asymmetric encryption**: Key pair (public/private), slower, used for key exchange and digital signatures

Usage in distributed systems:
- Symmetric: TLS session keys, database encryption, message encryption
- Asymmetric: TLS handshake, JWT signing, certificate-based authentication

### Answer 2.2 (3 points)
```nginx
server {
    listen 443 ssl http2;
    server_name api.company.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/api.company.com.crt;
    ssl_certificate_key /etc/ssl/private/api.company.com.key;
    
    # TLS Protocol Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Perfect Forward Secrecy
    ssl_ecdh_curve secp384r1;
    ssl_dhparam /etc/ssl/dhparam.pem;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # SSL Session Configuration
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Answer 2.3 (2 points)
**Envelope encryption** is a cryptographic technique where data is encrypted with a data key, and the data key is encrypted with a master key. It's important for cloud storage because:
- Enables key hierarchy and separation of concerns
- Allows efficient re-encryption (only master key needs rotation)
- Provides better performance for large data sets
- Enables fine-grained access control

### Answer 2.4 (3 points)
```javascript
const crypto = require('crypto');
const { Pool } = require('pg');

class SecureUserService {
  constructor() {
    this.pool = new Pool({
      connectionString: process.env.DATABASE_URL,
    });
    this.masterKey = process.env.MASTER_ENCRYPTION_KEY;
  }

  encrypt(text) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher('aes-256-gcm', this.masterKey);
    cipher.setAAD(Buffer.from('user-data', 'utf8'));
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
      encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex')
    };
  }

  decrypt(encryptedData) {
    const decipher = crypto.createDecipher('aes-256-gcm', this.masterKey);
    decipher.setAAD(Buffer.from('user-data', 'utf8'));
    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
    
    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }

  async createUser(userData) {
    const { email, ssn, phone } = userData;
    
    // Encrypt sensitive fields
    const encryptedSSN = this.encrypt(ssn);
    const encryptedPhone = this.encrypt(phone);
    
    const query = `
      INSERT INTO users (email, ssn_encrypted, ssn_iv, ssn_auth_tag, 
                        phone_encrypted, phone_iv, phone_auth_tag, created_at)
      VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
      RETURNING id, email, created_at
    `;
    
    const values = [
      email,
      encryptedSSN.encrypted, encryptedSSN.iv, encryptedSSN.authTag,
      encryptedPhone.encrypted, encryptedPhone.iv, encryptedPhone.authTag
    ];
    
    const result = await this.pool.query(query, values);
    return result.rows[0];
  }

  async getUser(userId) {
    const query = `
      SELECT id, email, ssn_encrypted, ssn_iv, ssn_auth_tag,
             phone_encrypted, phone_iv, phone_auth_tag, created_at
      FROM users WHERE id = $1
    `;
    
    const result = await this.pool.query(query, [userId]);
    if (result.rows.length === 0) return null;
    
    const user = result.rows[0];
    
    // Decrypt sensitive fields
    const ssnData = {
      encrypted: user.ssn_encrypted,
      iv: user.ssn_iv,
      authTag: user.ssn_auth_tag
    };
    
    const phoneData = {
      encrypted: user.phone_encrypted,
      iv: user.phone_iv,
      authTag: user.phone_auth_tag
    };
    
    return {
      id: user.id,
      email: user.email,
      ssn: this.decrypt(ssnData),
      phone: this.decrypt(phoneData),
      created_at: user.created_at
    };
  }
}
```

## Section 3: Secret Management - Solutions

### Answer 3.1 (2 points)
Five anti-patterns for secret management:
1. **Hardcoding secrets** in source code or configuration files
2. **Environment variables** in container images or process lists
3. **Storing secrets in Git** repositories or version control
4. **Sharing secrets** via email, Slack, or unencrypted channels
5. **Using default credentials** without rotation or customization

### Answer 3.2 (3 points)
```yaml
# Vault configuration for automatic secret rotation
path "database/config/my-database" {
  type = "database"
  plugin_name = "mysql-database-plugin"
  connection_url = "{{username}}:{{password}}@tcp(db.example.com:3306)/"
  allowed_roles = "my-app-role"
  username = "vault-admin"
  password = "initial-password"
  
  # Rotation configuration
  rotation_period = "24h"
  rotation_statements = [
    "ALTER USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';",
  ]
}

path "database/roles/my-app-role" {
  db_name = "my-database"
  creation_statements = [
    "CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';",
    "GRANT SELECT, INSERT, UPDATE, DELETE ON myapp.* TO '{{name}}'@'%';"
  ]
  default_ttl = "1h"
  max_ttl = "24h"
  
  # Automatic rotation
  rotation_statements = [
    "ALTER USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';",
  ]
}

# Policy for secret rotation
path "database/rotate-root/my-database" {
  capabilities = ["update"]
}

path "database/creds/my-app-role" {
  capabilities = ["read"]
}
```

### Answer 3.3 (2 points)
Secure methods to inject secrets into Kubernetes pods:

1. **Kubernetes Secrets with Volume Mounts**:
   ```yaml
   volumeMounts:
   - name: secret-volume
     mountPath: "/etc/secrets"
     readOnly: true
   ```

2. **External Secret Operators** (e.g., External Secrets Operator):
   ```yaml
   apiVersion: external-secrets.io/v1beta1
   kind: ExternalSecret
   metadata:
     name: vault-secret
   spec:
     secretStoreRef:
       name: vault-backend
       kind: SecretStore
   ```

3. **Init Containers** that fetch secrets before main container starts

4. **Service Mesh** with automatic secret injection (Istio, Consul Connect)

### Answer 3.4 (3 points)
```python
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional
import hashlib

class SecretProvider(ABC):
    @abstractmethod
    async def get_secret(self, secret_name: str) -> str:
        pass

class VaultProvider(SecretProvider):
    async def get_secret(self, secret_name: str) -> str:
        # Implementation for HashiCorp Vault
        pass

class AWSSecretsProvider(SecretProvider):
    async def get_secret(self, secret_name: str) -> str:
        # Implementation for AWS Secrets Manager
        pass

class AzureKeyVaultProvider(SecretProvider):
    async def get_secret(self, secret_name: str) -> str:
        # Implementation for Azure Key Vault
        pass

class SecretManager:
    def __init__(self):
        self.providers = {
            'vault': VaultProvider(),
            'aws': AWSSecretsProvider(),
            'azure': AzureKeyVaultProvider()
        }
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.rotation_callbacks = {}

    async def get_secret(self, secret_name: str, provider: str = 'vault') -> str:
        cache_key = f"{provider}:{secret_name}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() < cached_data['expires']:
                return cached_data['value']
            else:
                # Remove expired entry
                del self.cache[cache_key]

        # Fetch from provider
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        secret_value = await self.providers[provider].get_secret(secret_name)
        
        # Cache the secret
        self.cache[cache_key] = {
            'value': secret_value,
            'expires': time.time() + self.cache_ttl,
            'hash': hashlib.sha256(secret_value.encode()).hexdigest()
        }
        
        return secret_value

    async def rotate_secret(self, secret_name: str, provider: str = 'vault'):
        cache_key = f"{provider}:{secret_name}"
        
        # Get current secret hash for comparison
        current_hash = None
        if cache_key in self.cache:
            current_hash = self.cache[cache_key]['hash']
        
        # Force refresh from provider
        new_secret = await self.providers[provider].get_secret(secret_name)
        new_hash = hashlib.sha256(new_secret.encode()).hexdigest()
        
        # Check if secret actually changed
        if current_hash and current_hash == new_hash:
            print(f"Secret {secret_name} has not changed")
            return False
        
        # Update cache
        self.cache[cache_key] = {
            'value': new_secret,
            'expires': time.time() + self.cache_ttl,
            'hash': new_hash
        }
        
        # Notify registered callbacks
        if secret_name in self.rotation_callbacks:
            for callback in self.rotation_callbacks[secret_name]:
                try:
                    await callback(secret_name, new_secret)
                except Exception as e:
                    print(f"Error in rotation callback: {e}")
        
        return True

    def register_rotation_callback(self, secret_name: str, callback):
        if secret_name not in self.rotation_callbacks:
            self.rotation_callbacks[secret_name] = []
        self.rotation_callbacks[secret_name].append(callback)

    async def health_check(self) -> Dict:
        health_status = {}
        
        for provider_name, provider in self.providers.items():
            try:
                # Test connection to each provider
                test_result = await asyncio.wait_for(
                    provider.get_secret("health-check"),
                    timeout=5.0
                )
                health_status[provider_name] = "healthy"
            except Exception as e:
                health_status[provider_name] = f"unhealthy: {str(e)}"
        
        return {
            "providers": health_status,
            "cache_entries": len(self.cache),
            "timestamp": time.time()
        }
```

## Section 4: API Security - Solutions

### Answer 4.1 (2 points)
**OWASP API Security Top 10 (selected 3)**:

1. **API1: Broken Object Level Authorization**
   - Mitigation: Implement proper authorization checks for each object access
   - Use resource-based permissions
   - Validate user ownership of requested resources

2. **API4: Lack of Resources & Rate Limiting**
   - Mitigation: Implement rate limiting per user/API key
   - Set resource quotas and timeouts
   - Monitor and alert on unusual usage patterns

3. **API10: Insufficient Logging & Monitoring**
   - Mitigation: Log all API requests with user context
   - Implement real-time monitoring and alerting
   - Regular security audit log reviews

### Answer 4.2 (3 points)
```javascript
class SlidingWindowRateLimiter {
  constructor(windowSize = 60000, maxRequests = 100) { // 1 minute window, 100 requests
    this.windowSize = windowSize;
    this.maxRequests = maxRequests;
    this.clientWindows = new Map();
  }
  
  isAllowed(clientId) {
    const now = Date.now();
    const windowStart = now - this.windowSize;
    
    // Get or create client window
    if (!this.clientWindows.has(clientId)) {
      this.clientWindows.set(clientId, []);
    }
    
    const requests = this.clientWindows.get(clientId);
    
    // Remove requests outside the current window
    while (requests.length > 0 && requests[0] <= windowStart) {
      requests.shift();
    }
    
    // Check if limit exceeded
    if (requests.length >= this.maxRequests) {
      return {
        allowed: false,
        remaining: 0,
        resetTime: requests[0] + this.windowSize,
        retryAfter: Math.ceil((requests[0] + this.windowSize - now) / 1000)
      };
    }
    
    // Add current request
    requests.push(now);
    
    return {
      allowed: true,
      remaining: this.maxRequests - requests.length,
      resetTime: windowStart + this.windowSize,
      retryAfter: null
    };
  }
  
  // Cleanup old entries periodically
  cleanup() {
    const now = Date.now();
    const windowStart = now - this.windowSize;
    
    for (const [clientId, requests] of this.clientWindows.entries()) {
      // Remove old requests
      while (requests.length > 0 && requests[0] <= windowStart) {
        requests.shift();
      }
      
      // Remove empty client entries
      if (requests.length === 0) {
        this.clientWindows.delete(clientId);
      }
    }
  }
  
  // Get current stats for monitoring
  getStats() {
    return {
      activeClients: this.clientWindows.size,
      totalRequests: Array.from(this.clientWindows.values())
        .reduce((sum, requests) => sum + requests.length, 0)
    };
  }
}
```

### Answer 4.3 (2 points)
**API Versioning Security Strategy**:

1. **Version Isolation**: Each version maintains separate security policies
2. **Security Patches**: Apply security fixes to all supported versions
3. **Deprecation Policy**: Clear timeline for retiring insecure versions
4. **Access Control**: Version-specific authentication and authorization
5. **Monitoring**: Track security events across all versions
6. **Migration Support**: Secure upgrade paths for clients

Implementation:
```javascript
// Version-specific middleware
app.use('/api/v1', v1SecurityMiddleware);
app.use('/api/v2', v2SecurityMiddleware);
app.use('/api/v3', v3SecurityMiddleware);
```

### Answer 4.4 (3 points)
```javascript
const validator = require('validator');
const sqlstring = require('sqlstring');

function validateInput(schema) {
  return (req, res, next) => {
    const errors = [];
    
    // Validate against schema
    for (const [field, rules] of Object.entries(schema)) {
      const value = req.body[field];
      
      if (!value && rules.required) {
        errors.push(`${field} is required`);
        continue;
      }
      
      if (value) {
        // SQL Injection Prevention
        if (rules.type === 'string' && containsSQLInjection(value)) {
          errors.push(`${field} contains invalid characters`);
        }
        
        // NoSQL Injection Prevention
        if (typeof value === 'object' && containsNoSQLInjection(value)) {
          errors.push(`${field} contains invalid object structure`);
        }
        
        // Command Injection Prevention
        if (rules.type === 'string' && containsCommandInjection(value)) {
          errors.push(`${field} contains dangerous commands`);
        }
        
        // Path Traversal Prevention
        if (rules.type === 'path' && containsPathTraversal(value)) {
          errors.push(`${field} contains invalid path characters`);
        }
        
        // Type validation
        if (!validateType(value, rules.type)) {
          errors.push(`${field} must be of type ${rules.type}`);
        }
        
        // Length validation
        if (rules.maxLength && value.length > rules.maxLength) {
          errors.push(`${field} exceeds maximum length`);
        }
        
        // Pattern validation
        if (rules.pattern && !new RegExp(rules.pattern).test(value)) {
          errors.push(`${field} format is invalid`);
        }
      }
    }
    
    if (errors.length > 0) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors
      });
    }
    
    // Sanitize input
    for (const [field, rules] of Object.entries(schema)) {
      if (req.body[field] && rules.type === 'string') {
        req.body[field] = sanitizeString(req.body[field]);
      }
    }
    
    next();
  };
}

function containsSQLInjection(value) {
  const sqlPatterns = [
    /('|(\\)|(;)|(\|)|(\*)|(%)|(<)|(>)|(\{)|(\})|(\[)|(\]))/i,
    /(union\s+select)/i,
    /(insert\s+into)/i,
    /(delete\s+from)/i,
    /(drop\s+table)/i,
    /(update\s+set)/i,
    /(-{2})|(\#{1})/,
    /(\/\*)|(\*\/)/
  ];
  
  return sqlPatterns.some(pattern => pattern.test(value));
}

function containsNoSQLInjection(obj) {
  const dangerousKeys = ['$where', '$regex', '$gt', '$lt', '$ne', '$in', '$nin'];
  
  if (typeof obj === 'object') {
    for (const key of Object.keys(obj)) {
      if (dangerousKeys.includes(key)) {
        return true;
      }
      if (typeof obj[key] === 'object' && containsNoSQLInjection(obj[key])) {
        return true;
      }
    }
  }
  
  return false;
}

function containsCommandInjection(value) {
  const commandPatterns = [
    /[;&|`$()]/,
    /(cat|ls|ps|kill|rm|mv|cp|chmod|chown)/i,
    /(wget|curl|nc|netcat)/i,
    /(python|perl|ruby|node|java)/i
  ];
  
  return commandPatterns.some(pattern => pattern.test(value));
}

function containsPathTraversal(value) {
  const pathPatterns = [
    /\.\./,
    /\/etc\/passwd/,
    /\/etc\/shadow/,
    /\/etc\/hosts/,
    /\\windows\\system32/i,
    /%2e%2e/i,
    /%2f/i,
    /%5c/i
  ];
  
  return pathPatterns.some(pattern => pattern.test(value));
}

function validateType(value, type) {
  switch (type) {
    case 'string':
      return typeof value === 'string';
    case 'number':
      return typeof value === 'number' && !isNaN(value);
    case 'email':
      return validator.isEmail(value);
    case 'url':
      return validator.isURL(value);
    case 'uuid':
      return validator.isUUID(value);
    case 'path':
      return typeof value === 'string' && !containsPathTraversal(value);
    default:
      return true;
  }
}

function sanitizeString(str) {
  return validator.escape(str);
}

// Usage example
const userSchema = {
  email: { type: 'email', required: true },
  password: { type: 'string', required: true, minLength: 8 },
  name: { type: 'string', required: true, maxLength: 100 },
  age: { type: 'number' },
  website: { type: 'url' }
};

app.post('/register', validateInput(userSchema), (req, res) => {
  // Safe to use req.body here
});
```

## Section 5: Container and Kubernetes Security - Solutions

### Answer 5.1 (2 points)
**10 Container Security Best Practices**:

1. **Use minimal base images** (Alpine, distroless)
2. **Run as non-root user** with specific UID/GID
3. **Scan images for vulnerabilities** regularly
4. **Use read-only root filesystem** when possible
5. **Implement resource limits** (CPU, memory)
6. **Remove unnecessary packages** and tools
7. **Use multi-stage builds** to reduce attack surface
8. **Sign and verify container images**
9. **Keep base images updated** with latest security patches
10. **Implement secrets management** (avoid env vars)

### Answer 5.2 (3 points)
```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted-psp
spec:
  # Prevent privileged containers
  privileged: false
  allowPrivilegeEscalation: false
  
  # Required security context
  requiredDropCapabilities:
    - ALL
  allowedCapabilities: []
  
  # Volume restrictions
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  
  # Filesystem restrictions
  readOnlyRootFilesystem: true
  
  # User restrictions
  runAsUser:
    rule: 'MustRunAsNonRoot'
  runAsGroup:
    rule: 'MustRunAs'
    ranges:
      - min: 1000
        max: 65535
  
  # Filesystem group
  fsGroup:
    rule: 'RunAsAny'
  
  # SELinux
  seLinux:
    rule: 'RunAsAny'
  
  # Proc mount
  allowedProcMountTypes:
    - Default
  
  # Host restrictions
  hostNetwork: false
  hostIPC: false
  hostPID: false
  hostPorts:
    - min: 0
      max: 65535

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: restricted-psp-user
rules:
- apiGroups: ['policy']
  resources: ['podsecuritypolicies']
  verbs: ['use']
  resourceNames:
  - restricted-psp

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: restricted-psp-all-serviceaccounts
roleRef:
  kind: ClusterRole
  name: restricted-psp-user
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: Group
  name: system:serviceaccounts
  apiGroup: rbac.authorization.k8s.io
```

### Answer 5.3 (2 points)
**Service Mesh** is an infrastructure layer that handles service-to-service communication.

Security improvements in Kubernetes:
- **Automatic mTLS** between all services
- **Identity-based authentication** with SPIFFE/SPIRE
- **Fine-grained authorization policies** at L4 and L7
- **Traffic encryption** without application changes
- **Security policy enforcement** at the network level
- **Observability** with security metrics and audit logs

### Answer 5.4 (3 points)
```yaml
# Falco rules for security detection
- rule: Container Escape Attempt
  desc: Detect container escape attempts
  condition: >
    spawned_process and container and
    (proc.name in (docker, runc, containerd) or
     proc.args contains "nsenter" or
     proc.args contains "unshare" or
     proc.args contains "mount" and proc.args contains "/proc")
  output: "Container escape attempt detected (user=%user.name container=%container.name command=%proc.cmdline)"
  priority: CRITICAL

- rule: Unexpected Network Connection
  desc: Detect unexpected outbound network connections
  condition: >
    outbound and not fd.typechar=4 and not fd.is_unix_socket and
    not proc.name in (curl, wget, http, nginx, node, python) and
    not fd.lip in (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8)
  output: "Unexpected network connection (user=%user.name container=%container.name dest=%fd.rip:%fd.rport command=%proc.cmdline)"
  priority: WARNING

- rule: Privilege Escalation Detected
  desc: Detect privilege escalation attempts
  condition: >
    spawned_process and container and
    (proc.name in (sudo, su, newgrp) or
     proc.args contains "setuid" or
     proc.args contains "setgid" or
     proc.args contains "chmod +s")
  output: "Privilege escalation detected (user=%user.name container=%container.name command=%proc.cmdline)"
  priority: HIGH

- rule: Suspicious File Access
  desc: Detect access to sensitive files
  condition: >
    open_read and container and
    (fd.name startswith /etc/shadow or
     fd.name startswith /etc/passwd or
     fd.name startswith /root/.ssh or
     fd.name startswith /home/*/.ssh or
     fd.name contains "/proc/" and fd.name contains "/environ")
  output: "Suspicious file access (user=%user.name container=%container.name file=%fd.name command=%proc.cmdline)"
  priority: HIGH

- rule: Container Runtime Modification
  desc: Detect attempts to modify container runtime
  condition: >
    open_write and container and
    (fd.name startswith /var/lib/docker or
     fd.name startswith /var/lib/containerd or
     fd.name startswith /run/containerd or
     fd.name startswith /var/run/docker.sock)
  output: "Container runtime modification attempt (user=%user.name container=%container.name file=%fd.name)"
  priority: CRITICAL

# Macro definitions
- macro: outbound
  condition: >
    syscall.type=connect and evt.dir=< and
    (fd.typechar=4 or fd.typechar=6) and
    fd.ip != "0.0.0.0" and not fd.snet in (rfc_1918_addresses)

- macro: rfc_1918_addresses
  condition: >
    fd.snet in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")

- macro: spawned_process
  condition: >
    syscall.type=execve and evt.dir=<
```

## Section 6: Network Security - Solutions

### Answer 6.1 (2 points)
**WAF (Web Application Firewall)**:
- Application layer (Layer 7) protection
- Inspects HTTP/HTTPS traffic content
- Blocks application-specific attacks (SQL injection, XSS)
- Rule-based filtering of malicious requests

**Reverse Proxy**:
- Network routing and load balancing
- Can operate at multiple layers (L4/L7)
- Provides caching, SSL termination, compression
- Basic security through request filtering and rate limiting

WAF provides deeper application security, while reverse proxy focuses on traffic management with basic security features.

### Answer 6.2 (3 points)
```yaml
# VPC/Network Architecture
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    security-tier: "high"

---
apiVersion: v1
kind: Namespace
metadata:
  name: staging
  labels:
    security-tier: "medium"

---
# Network Policies for Micro-segmentation
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-tier-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: web
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: api
    ports:
    - protocol: TCP
      port: 3000

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-tier-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: web
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: database
    ports:
    - protocol: TCP
      port: 5432

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-tier-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: api
    ports:
    - protocol: TCP
      port: 5432

---
# Service Mesh Configuration (Istio)
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: web-to-api-policy
  namespace: production
spec:
  selector:
    matchLabels:
      tier: api
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/web-service"]
  - to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]

---
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
```

### Answer 6.3 (2 points)
**DNS over HTTPS (DoH)** encrypts DNS queries using HTTPS protocol.

Security benefits:
- **Privacy protection**: Prevents ISP/network monitoring of DNS queries
- **Integrity**: Prevents DNS response tampering
- **Authentication**: Verifies DNS server identity
- **Bypass censorship**: Harder to block or filter DNS queries
- **Reduced attack surface**: Eliminates plain-text DNS vulnerabilities

### Answer 6.4 (3 points)
```python
import re
import json
import time
from typing import Dict, List, Tuple
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class ThreatSignature:
    name: str
    pattern: str
    threat_level: int  # 1-10
    category: str

@dataclass
class AnalysisResult:
    threat_level: int
    threats_detected: List[str]
    details: Dict
    blocked: bool

class IntrusionDetector:
    def __init__(self):
        self.suspicious_patterns = self._load_default_patterns()
        self.ip_tracking = defaultdict(list)
        self.rate_limits = {
            'requests_per_minute': 100,
            'failed_logins_per_minute': 5
        }
        self.blocked_ips = set()
        
    def _load_default_patterns(self) -> List[ThreatSignature]:
        return [
            # SQL Injection patterns
            ThreatSignature("SQL Injection", r"('|(\\)|(;)|(\|)|(\*)|(%27)|(%3B)|(union\s+select)|(insert\s+into)|(delete\s+from)|(drop\s+table))", 9, "injection"),
            
            # XSS patterns
            ThreatSignature("XSS Attack", r"(<script|javascript:|onload=|onerror=|<iframe|eval\(|alert\()", 8, "xss"),
            
            # Command Injection
            ThreatSignature("Command Injection", r"(;|\||&|`|\$\(|wget|curl|nc|netcat|/bin/|/etc/passwd)", 9, "command_injection"),
            
            # Path Traversal
            ThreatSignature("Path Traversal", r"(\.\./|%2e%2e|/etc/passwd|/etc/shadow|/windows/system32)", 7, "path_traversal"),
            
            # Brute Force indicators
            ThreatSignature("Brute Force", r"(login|admin|password|auth).*?(admin|password|123456|root)", 6, "brute_force"),
            
            # Suspicious User Agents
            ThreatSignature("Suspicious User Agent", r"(nikto|sqlmap|nmap|burp|acunetix|nessus|w3af)", 8, "reconnaissance"),
            
            # Large payloads (potential buffer overflow)
            ThreatSignature("Large Payload", r".{2000,}", 5, "dos"),
            
            # Suspicious headers
            ThreatSignature("Header Injection", r"(\r\n|\n\r|%0a%0d|%0d%0a)", 7, "header_injection"),
        ]
    
    def analyze_request(self, request: Dict) -> AnalysisResult:
        threats_detected = []
        max_threat_level = 0
        analysis_details = {
            'timestamp': time.time(),
            'client_ip': request.get('client_ip', 'unknown'),
            'patterns_matched': [],
            'rate_limit_exceeded': False
        }
        
        # Check if IP is already blocked
        client_ip = request.get('client_ip', '')
        if client_ip in self.blocked_ips:
            return AnalysisResult(
                threat_level=10,
                threats_detected=['Blocked IP'],
                details=analysis_details,
                blocked=True
            )
        
        # Rate limiting check
        current_time = time.time()
        self.ip_tracking[client_ip] = [
            timestamp for timestamp in self.ip_tracking[client_ip]
            if current_time - timestamp < 60  # Keep last minute
        ]
        self.ip_tracking[client_ip].append(current_time)
        
        if len(self.ip_tracking[client_ip]) > self.rate_limits['requests_per_minute']:
            analysis_details['rate_limit_exceeded'] = True
            threats_detected.append('Rate Limit Exceeded')
            max_threat_level = max(max_threat_level, 6)
        
        # Analyze request components
        request_data = self._extract_request_data(request)
        
        for signature in self.suspicious_patterns:
            for component, data in request_data.items():
                if self._match_pattern(signature.pattern, data):
                    threats_detected.append(f"{signature.name} in {component}")
                    max_threat_level = max(max_threat_level, signature.threat_level)
                    analysis_details['patterns_matched'].append({
                        'signature': signature.name,
                        'component': component,
                        'threat_level': signature.threat_level,
                        'category': signature.category
                    })
        
        # Check for anomalous request size
        request_size = len(json.dumps(request))
        if request_size > 50000:  # 50KB
            threats_detected.append('Unusually Large Request')
            max_threat_level = max(max_threat_level, 5)
        
        # Determine if request should be blocked
        blocked = max_threat_level >= 8 or analysis_details['rate_limit_exceeded']
        
        # Auto-block IPs with high threat levels
        if max_threat_level >= 9:
            self.blocked_ips.add(client_ip)
            blocked = True
        
        return AnalysisResult(
            threat_level=max_threat_level,
            threats_detected=threats_detected,
            details=analysis_details,
            blocked=blocked
        )
    
    def _extract_request_data(self, request: Dict) -> Dict[str, str]:
        data = {}
        
        # URL and query parameters
        url = request.get('url', '')
        data['url'] = url
        
        # Request body
        body = request.get('body', '')
        data['body'] = str(body)
        
        # Headers
        headers = request.get('headers', {})
        data['headers'] = ' '.join([f"{k}:{v}" for k, v in headers.items()])
        
        # User agent
        user_agent = headers.get('User-Agent', '')
        data['user_agent'] = user_agent
        
        # Cookies
        cookies = request.get('cookies', {})
        data['cookies'] = ' '.join([f"{k}={v}" for k, v in cookies.items()])
        
        return data
    
    def _match_pattern(self, pattern: str, text: str) -> bool:
        try:
            return bool(re.search(pattern, text, re.IGNORECASE))
        except re.error:
            return False
    
    def update_rules(self, new_rules: List[Dict]):
        """Update detection rules from external source"""
        for rule in new_rules:
            signature = ThreatSignature(
                name=rule['name'],
                pattern=rule['pattern'],
                threat_level=rule['threat_level'],
                category=rule['category']
            )
            
            # Update existing rule or add new one
            existing_index = next(
                (i for i, s in enumerate(self.suspicious_patterns) 
                 if s.name == signature.name), None
            )
            
            if existing_index is not None:
                self.suspicious_patterns[existing_index] = signature
            else:
                self.suspicious_patterns.append(signature)
    
    def get_statistics(self) -> Dict:
        """Get detection statistics"""
        current_time = time.time()
        active_ips = sum(
            1 for timestamps in self.ip_tracking.values()
            if any(current_time - timestamp < 300 for timestamp in timestamps)
        )
        
        return {
            'total_rules': len(self.suspicious_patterns),
            'blocked_ips': len(self.blocked_ips),
            'active_ips_last_5min': active_ips,
            'total_tracked_ips': len(self.ip_tracking)
        }
    
    def whitelist_ip(self, ip: str):
        """Remove IP from blocked list"""
        self.blocked_ips.discard(ip)
    
    def blacklist_ip(self, ip: str):
        """Add IP to blocked list"""
        self.blocked_ips.add(ip)

# Usage example
if __name__ == "__main__":
    detector = IntrusionDetector()
    
    # Example malicious request
    malicious_request = {
        'client_ip': '192.168.1.100',
        'url': '/search?q=1\' OR \'1\'=\'1',
        'method': 'GET',
        'headers': {
            'User-Agent': 'sqlmap/1.0',
            'Accept': '*/*'
        },
        'body': '',
        'cookies': {}
    }
    
    result = detector.analyze_request(malicious_request)
    
    print(f"Threat Level: {result.threat_level}")
    print(f"Threats: {result.threats_detected}")
    print(f"Blocked: {result.blocked}")
    print(f"Details: {result.details}")
```

This comprehensive security examination covers all the requested areas with practical, production-ready examples and solutions. The exam tests both theoretical knowledge and hands-on implementation skills required for securing distributed systems in cloud-native environments.
# API Security & OAuth Code Examples
## Episode 062 - Hindi Tech Podcast

यह repository Episode 062 के सभी code examples contain करती है। यहाँ आपको production-ready API security implementations मिलेंगे जो real-world applications में use हो सकते हैं।

## 📁 Directory Structure

```
code/
├── python/          # Python implementations
├── java/           # Java implementations  
├── go/             # Go implementations
├── requirements.txt # Python dependencies
└── README.md       # This file
```

## 🐍 Python Examples

### Security & Authentication
1. **OAuth 2.0 Authorization Server** (`01_oauth2_authorization_server.py`)
   - Complete OAuth 2.0 server implementation
   - Multiple grant types support
   - Token introspection और revocation
   - Production-grade security

2. **JWT Token Management** (`02_jwt_token_management.py`)  
   - Advanced JWT token lifecycle management
   - RSA key signing
   - Token rotation और refresh
   - Banking-grade security

3. **API Rate Limiting** (`03_api_rate_limiting.py`)
   - Multiple rate limiting algorithms
   - Distributed rate limiting with Redis
   - Circuit breaker integration
   - Real-time monitoring

4. **DDoS Protection Middleware** (`04_ddos_protection_middleware.py`)
   - Multi-layer DDoS protection
   - Behavioral analysis
   - Geographic filtering
   - Challenge-response system

5. **OWASP API Security Scanner** (`05_owasp_api_security_scanner.py`)
   - Complete OWASP API Top 10 vulnerability scanner
   - Automated security testing
   - Comprehensive reporting
   - Professional security assessment

### Advanced Security Features
6. **API Key Rotation System** (`06_api_key_rotation_system.py`)
   - Automatic key rotation
   - Zero-downtime updates
   - Complete audit trail
   - AWS/Azure level key management

7. **PKCE OAuth Flow** (`07_pkce_oauth_flow.py`)
   - Mobile app security implementation
   - Authorization code interception protection
   - RFC 7636 compliant
   - Demo web interface

8. **API Gateway Security** (`08_api_gateway_security.py`)
   - Enterprise-grade API gateway
   - Request/response transformation
   - Load balancing और health checks
   - Comprehensive security layers

9. **Webhook Signature Verification** (`09_webhook_signature_verification.py`)
   - GitHub/Stripe level webhook security
   - HMAC signature verification
   - Replay attack prevention
   - Multiple provider support

10. **UPI Payment Security** (`10_upi_payment_security.py`)
    - Banking-grade payment security
    - Multi-factor authentication
    - Real-time fraud detection
    - PhonePe/GPay level implementation

## ☕ Java Examples

1. **OAuth 2.0 Client Implementation** (`OAuth2ClientImplementation.java`)
   - Enterprise Java OAuth client
   - PKCE support
   - Automatic token refresh
   - Spring Boot compatible

## 🔷 Go Examples

1. **API Security Gateway** (`api_security_gateway.go`)
   - High-performance API gateway
   - JWT validation
   - Circuit breaker pattern
   - Prometheus metrics

## 🚀 Installation & Setup

### Python Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Redis (required for many examples)
# Ubuntu/Debian: sudo apt-get install redis-server
# macOS: brew install redis
# Windows: Download from https://redis.io/download

# Start Redis
redis-server
```

### Java Setup
```bash
# Install dependencies using Maven/Gradle
# Dependencies: OkHttp, Jackson, SLF4J

# Compile
javac -cp "lib/*" java/OAuth2ClientImplementation.java

# Run
java -cp ".:lib/*" OAuth2ClientImplementation
```

### Go Setup
```bash
# Initialize Go module
go mod init api-security-gateway

# Install dependencies
go get github.com/gin-gonic/gin
go get github.com/golang-jwt/jwt/v5
go get github.com/redis/go-redis/v9
go get github.com/prometheus/client_golang

# Run
go run go/api_security_gateway.go
```

## 🏃‍♂️ Running Examples

### OAuth 2.0 Authorization Server
```bash
cd python/
python 01_oauth2_authorization_server.py

# Access: http://localhost:8001
# Endpoints:
# - GET /oauth/authorize - Authorization endpoint
# - POST /oauth/token - Token endpoint  
# - POST /oauth/introspect - Token introspection
```

### JWT Token Management
```bash
python 02_jwt_token_management.py

# Features:
# - Token generation with custom claims
# - Automatic token rotation
# - Security context validation
```

### API Rate Limiting
```bash
python 03_api_rate_limiting.py

# Access: http://localhost:8002
# Features:
# - Multiple rate limiting algorithms
# - Real-time rate limit monitoring
# - Circuit breaker integration
```

### PKCE OAuth Flow
```bash
python 07_pkce_oauth_flow.py

# Access: http://localhost:8005
# Demo: http://localhost:8005/demo/mobile-app
# Complete PKCE flow demonstration
```

### UPI Payment Security  
```bash
python 10_upi_payment_security.py

# Access: http://localhost:8008
# Endpoints:
# - POST /upi/payment/initiate - Start payment
# - POST /upi/payment/authenticate - Verify PIN/biometric
# - POST /upi/payment/verify-otp - OTP verification
```

## 🧪 Testing

### API Testing Examples
```bash
# Test OAuth 2.0 Server
curl -X POST http://localhost:8001/oauth/authorize \
  -d "response_type=code&client_id=paytm_client&redirect_uri=https://paytm.com/callback&scope=read+write&state=xyz123"

# Test JWT validation
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8002/api/protected

# Test rate limiting
for i in {1..10}; do
  curl http://localhost:8002/api/general
done
```

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Load test API gateway
ab -n 1000 -c 10 http://localhost:8080/api/v1/public

# Load test with authentication
ab -n 500 -c 5 -H "Authorization: Bearer JWT_TOKEN" \
  http://localhost:8080/api/v1/users
```

## 🔧 Configuration

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256

# Redis Configuration  
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/apidb

# OAuth Configuration
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_REDIRECT_URI=http://localhost:8000/callback

# Security Configuration
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
MAX_FAILED_ATTEMPTS=3
EOF
```

### Redis Configuration
```bash
# redis.conf settings for production
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## 📊 Monitoring & Metrics

### Prometheus Metrics
```bash
# Access metrics
curl http://localhost:8080/metrics

# Key metrics:
# - api_gateway_requests_total
# - api_gateway_request_duration_seconds  
# - api_gateway_rate_limit_exceeded_total
```

### Health Checks
```bash
# Gateway health
curl http://localhost:8080/admin/health

# Service health
curl http://localhost:8080/admin/routes
```

## 🔒 Security Best Practices

### Production Deployment
1. **Environment Setup**
   ```bash
   # Use proper secret management
   export JWT_SECRET=$(openssl rand -base64 32)
   
   # Enable HTTPS only
   export FORCE_HTTPS=true
   
   # Set secure cookie flags
   export SECURE_COOKIES=true
   ```

2. **Database Security**
   ```bash
   # Use encrypted connections
   export DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
   
   # Enable connection pooling
   export DB_POOL_SIZE=20
   export DB_MAX_OVERFLOW=30
   ```

3. **Redis Security**
   ```bash
   # Use Redis AUTH
   redis-cli CONFIG SET requirepass your_redis_password
   
   # Enable SSL/TLS
   redis-server --tls-port 6380 --port 0 \
     --tls-cert-file redis.crt \
     --tls-key-file redis.key
   ```

### Security Headers
```python
# Add these headers to all responses
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY', 
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```bash
   # Check Redis status
   redis-cli ping
   
   # Restart Redis
   sudo systemctl restart redis-server
   ```

2. **JWT Token Invalid**
   ```bash
   # Verify token format
   echo "JWT_TOKEN" | cut -d. -f2 | base64 -d | jq .
   
   # Check expiration
   python -c "import jwt; print(jwt.decode('TOKEN', verify=False))"
   ```

3. **Rate Limit Issues**
   ```bash
   # Clear rate limit for user
   redis-cli DEL "rate_limit:user:user123"
   
   # Check current limits
   redis-cli KEYS "rate_limit:*"
   ```

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Add indexes for faster lookups
   CREATE INDEX idx_user_sessions ON user_sessions(user_id, created_at);
   CREATE INDEX idx_api_keys ON api_keys(key_hash);
   ```

2. **Redis Optimization**
   ```bash
   # Optimize memory usage
   redis-cli CONFIG SET maxmemory-policy allkeys-lru
   
   # Monitor performance
   redis-cli --latency-history
   ```

## 📚 Learning Resources

### Documentation Links
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [PKCE RFC 7636](https://tools.ietf.org/html/rfc7636)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [OWASP API Top 10](https://owasp.org/www-project-api-security/)

### Hindi Tech Podcast Episodes
- Episode 061: OAuth 2.0 Deep Dive
- Episode 062: API Security & OAuth (Current)
- Episode 063: GraphQL Security

## 🤝 Contributing

यदि आप इन examples को improve करना चाहते हैं:

1. Fork करें repository
2. Feature branch बनाएं
3. Changes commit करें
4. Pull request submit करें

## 📝 License

यह code educational purposes के लिए है। Production में use करने से पहले proper security review कराएं।

## 🎧 About Hindi Tech Podcast

Hindi Tech Podcast भारत का leading technology podcast है जो complex technical concepts को Hindi में explain करता है।

- **Website**: [hinditechpodcast.com](https://hinditechpodcast.com)
- **YouTube**: Hindi Tech Podcast Channel
- **Twitter**: @HindiTechPod
- **Telegram**: Hindi Tech Community

---

**"Code karo, sikho, aur grow karo! 🚀"**

*Made with ❤️ for Indian developers*
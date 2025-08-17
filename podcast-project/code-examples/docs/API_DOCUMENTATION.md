# API Documentation
## Episode Code Examples - Production APIs

### Overview
Complete API documentation for all podcast episode code examples. All APIs are production-ready and optimized for Indian infrastructure.

### Base URLs
- **Development**: `http://localhost:8080`
- **Staging**: `https://staging.yourapp.in`
- **Production**: `https://api.yourapp.in`

---

## Episode 081: Real-time Collaboration APIs

### WebSocket Connections
```
wss://api.yourapp.in/collaboration/ws
```

#### Connect to Collaboration Session
```javascript
const ws = new WebSocket('wss://api.yourapp.in/collaboration/ws');
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'join-room',
    roomId: 'document-123',
    userId: 'user-456'
  }));
};
```

#### CRDT Operations
```json
{
  "type": "operation",
  "operation": {
    "type": "insert",
    "position": 10,
    "text": "Hello World",
    "author": "user-456",
    "timestamp": 1640995200000
  }
}
```

---

## Episode 082: WebAssembly APIs

### Crypto Hash Module

#### Generate Hash
```javascript
import init, { CryptoHashModule } from './crypto_hash_wasm.js';

await init();
const crypto = new CryptoHashModule();
const result = crypto.sha256_hash("payment_data");

console.log(result.output_hash()); // Hash result
console.log(result.execution_time_ms()); // Performance
```

#### Payment Transaction Hash
```javascript
const transaction = new PaymentTransaction(
  "txn_123",
  1299.99,
  "INR", 
  "merchant_001",
  "customer_001",
  "UPI"
);

const hash = crypto.generate_payment_hash(transaction);
```

### Financial Calculator Module

#### SIP Calculation
```javascript
import { FinancialCalculator } from './financial_calculator_wasm.js';

const calculator = new FinancialCalculator();
const result = calculator.calculate_sip_returns(5000, 12, 10);

console.log(`Future Value: ₹${result.future_value()}`);
console.log(`Returns: ₹${result.returns()}`);
```

#### Option Pricing
```javascript
const optionPrice = calculator.black_scholes_option_price(
  15000, // spot price
  15500, // strike price
  30,    // days to expiry
  20,    // volatility %
  8.0,   // risk-free rate
  "CALL" // option type
);
```

---

## Episode 083: Edge Functions APIs

### Authentication API

#### Login Endpoint
```http
POST /auth/login
Content-Type: application/json

{
  "phone": "9876543210",
  "password": "secure_password",
  "login_method": "password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "refresh_token_here",
  "expires_in": 3600
}
```

#### Token Verification
```http
POST /auth/verify
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "valid": true,
  "user": {
    "phone": "98XXXX3210",
    "location": {
      "city": "Mumbai",
      "state": "Maharashtra"
    }
  }
}
```

#### Health Check
```http
GET /auth/health
```

**Response:**
```json
{
  "status": "healthy",
  "edge_location": "BOM",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "kv_sessions": "healthy",
    "kv_rate_limits": "healthy"
  }
}
```

---

## Episode 085: Platform Engineering APIs

### CLI Tool Commands

#### Deploy Application
```bash
indian-platform-cli deploy \
  --env production \
  --region mumbai \
  --replicas 3 \
  --config deploy.yaml
```

#### Scale Services
```bash
indian-platform-cli scale \
  --service payment-gateway \
  --replicas 10 \
  --region bangalore
```

#### Monitor Services
```bash
indian-platform-cli monitor \
  --service all \
  --duration 1h \
  --format json
```

---

## Common Response Formats

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "execution_time_ms": 45
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request parameters",
    "details": {
      "field": "phone",
      "issue": "Invalid Indian phone number format"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Performance Headers
All APIs include performance monitoring headers:
```http
X-Execution-Time: 45ms
X-Edge-Location: BOM
X-Request-ID: req_123456789
X-Rate-Limit-Remaining: 59
```

---

## Rate Limiting

### Default Limits
- **Authentication APIs**: 60 requests/minute per IP
- **Collaboration APIs**: 1000 operations/minute per user
- **WASM APIs**: 10000 calculations/minute per session
- **Platform APIs**: 100 commands/hour per API key

### Rate Limit Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995260
```

---

## Indian Network Optimization

### Response Compression
All APIs support compression optimized for Indian networks:
```http
Accept-Encoding: gzip, deflate, br
```

### Regional Routing
APIs automatically route to nearest Indian data center:
- **Mumbai**: Primary for West India
- **Bangalore**: Primary for South India  
- **Delhi**: Primary for North India

### Mobile Optimization
Special optimizations for Indian mobile networks:
- Reduced payload sizes for 3G networks
- Aggressive caching for frequent requests
- Offline-first architecture support

---

## Security

### Authentication
- **JWT Tokens**: RSA-256 signed with 1-hour expiry
- **Refresh Tokens**: 7-day expiry with rotation
- **Rate Limiting**: Per-IP and per-user limits
- **Indian Phone Validation**: Strict 10-digit validation

### Headers
Required security headers:
```http
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
Content-Type: application/json
User-Agent: YourApp/1.0 (India)
```

### CORS
Configured for Indian domains:
```http
Access-Control-Allow-Origin: *.yourapp.in
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
```

---

## SDK Examples

### JavaScript/TypeScript
```typescript
import { PodcastAPI } from '@podcast/api-client';

const client = new PodcastAPI({
  baseURL: 'https://api.yourapp.in',
  apiKey: 'your-api-key',
  region: 'mumbai'
});

// Real-time collaboration
const collaboration = await client.collaboration.joinRoom('doc-123');

// Financial calculations
const sipResult = await client.financial.calculateSIP({
  monthlyAmount: 5000,
  years: 10,
  expectedReturn: 12
});
```

### Python
```python
from podcast_api import PodcastClient

client = PodcastClient(
    base_url='https://api.yourapp.in',
    api_key='your-api-key',
    region='mumbai'
)

# Authentication
auth_result = client.auth.login(
    phone='9876543210',
    password='secure_password'
)

# WASM calculations  
crypto_result = client.crypto.sha256_hash('payment_data')
```

### Go
```go
import "github.com/podcast/api-client-go"

client := podcast.NewClient(&podcast.Config{
    BaseURL: "https://api.yourapp.in",
    APIKey:  "your-api-key",
    Region:  "mumbai",
})

result, err := client.Financial.CalculateSIP(&podcast.SIPRequest{
    MonthlyAmount: 5000,
    Years:        10,
    ExpectedReturn: 12,
})
```

---

## Monitoring and Analytics

### Performance Metrics
- **Response Time**: <100ms P95 for Indian users
- **Throughput**: 10,000+ requests/second per region
- **Availability**: 99.9% uptime SLA
- **Error Rate**: <0.1% for production APIs

### Business Metrics
- **User Engagement**: Track feature usage
- **Regional Performance**: Monitor by Indian states
- **Mobile vs Desktop**: Usage patterns
- **Language Preferences**: Hindi vs English usage

---

## Support

### Documentation
- **Postman Collection**: Available for all endpoints
- **OpenAPI Spec**: Complete API specification
- **SDK Documentation**: Language-specific guides
- **Video Tutorials**: Hindi and English explanations

### Contact
- **Email**: support@yourapp.in
- **Phone**: +91-80-1234-5678
- **Chat**: 24/7 support in Hindi and English
- **GitHub**: https://github.com/podcast/api-issues

---

**🇮🇳 Jai Hind! APIs ready for Indian scale! 🚀**
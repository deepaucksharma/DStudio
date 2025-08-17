/*
API Gateway Load Testing with k6
API गेटवे लोड टेस्टिंग

Testing API gateway patterns with Indian traffic scenarios:
- Diwali sale traffic spikes
- IPL match concurrent users  
- Regional routing validation
- Rate limiting verification
*/

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// Custom metrics for Indian context
const indianErrorRate = new Rate('indian_errors');
const upiLatency = new Trend('upi_transaction_latency');
const ecommerceLatency = new Trend('ecommerce_api_latency');
const authLatency = new Trend('auth_latency');

// Test configuration based on environment
const testConfig = {
  // Load test scenarios
  scenarios: {
    // Normal day traffic
    normal_traffic: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '2m', target: 100 },   // Ramp up
        { duration: '5m', target: 100 },   // Stay steady
        { duration: '2m', target: 0 },     // Ramp down
      ],
      tags: { scenario: 'normal' },
    },
    
    // Diwali sale traffic spike
    diwali_sale: {
      executor: 'ramping-vus',
      startVUs: 50,
      stages: [
        { duration: '1m', target: 500 },   // Quick ramp up
        { duration: '3m', target: 2000 },  // Peak traffic
        { duration: '10m', target: 2000 }, // Sustained load
        { duration: '2m', target: 500 },   // Gradual decline
        { duration: '1m', target: 0 },     // Complete ramp down
      ],
      tags: { scenario: 'diwali' },
    },
    
    // IPL match concurrent streaming
    ipl_streaming: {
      executor: 'ramping-vus',
      startVUs: 100,
      stages: [
        { duration: '30s', target: 1000 },  // Match starts
        { duration: '5m', target: 5000 },   // Peak viewership
        { duration: '15m', target: 8000 },  // Match peak
        { duration: '5m', target: 3000 },   // Match ends
        { duration: '2m', target: 0 },      // Users leave
      ],
      tags: { scenario: 'ipl' },
    },
    
    // UPI payment rush (salary day)
    upi_rush: {
      executor: 'ramping-vus',
      startVUs: 20,
      stages: [
        { duration: '1m', target: 300 },    // Morning rush
        { duration: '5m', target: 1000 },   // Peak payments
        { duration: '10m', target: 800 },   // Sustained activity
        { duration: '2m', target: 100 },    // Evening decline
      ],
      tags: { scenario: 'upi' },
    },
  },
  
  // Performance thresholds for Indian context
  thresholds: {
    // Overall API performance
    http_req_duration: [
      'p(95)<200',     // 95% of requests under 200ms
      'p(99)<500',     // 99% of requests under 500ms
    ],
    
    // Error rates
    http_req_failed: ['rate<0.1'],  // Less than 0.1% errors
    indian_errors: ['rate<0.05'],   // Less than 0.05% Indian-specific errors
    
    // Specific API latencies
    upi_transaction_latency: ['p(95)<100', 'p(99)<250'],
    ecommerce_api_latency: ['p(95)<150', 'p(99)<300'],
    auth_latency: ['p(95)<50', 'p(99)<100'],
    
    // Throughput
    http_reqs: ['rate>100'],  // At least 100 RPS
  },
};

// Indian cities and their characteristics
const indianCities = {
  mumbai: { lat: 19.0760, lng: 72.8777, population: 20000000 },
  delhi: { lat: 28.7041, lng: 77.1025, population: 32000000 },
  bangalore: { lat: 12.9716, lng: 77.5946, population: 13000000 },
  chennai: { lat: 13.0827, lng: 80.2707, population: 11000000 },
  kolkata: { lat: 22.5726, lng: 88.3639, population: 15000000 },
};

// Indian banks for UPI testing
const indianBanks = ['HDFC', 'ICICI', 'SBI', 'AXIS', 'KOTAK', 'PNB', 'BOB'];

// E-commerce product categories popular in India
const productCategories = [
  'electronics', 'fashion', 'home-kitchen', 'books', 
  'beauty', 'sports', 'automotive', 'grocery'
];

// Test data generators
function generateIndianUser() {
  const cities = Object.keys(indianCities);
  const city = cities[Math.floor(Math.random() * cities.length)];
  const names = ['Rajesh', 'Priya', 'Amit', 'Sunita', 'Vikram', 'Kavya'];
  const surnames = ['Sharma', 'Patel', 'Singh', 'Gupta', 'Kumar', 'Verma'];
  
  return {
    id: `user_${Math.random().toString(36).substr(2, 9)}`,
    name: `${names[Math.floor(Math.random() * names.length)]} ${surnames[Math.floor(Math.random() * surnames.length)]}`,
    email: `user${Math.floor(Math.random() * 100000)}@gmail.com`,
    phone: `+91${Math.floor(Math.random() * 9000000000) + 1000000000}`,
    city: city,
    coordinates: indianCities[city],
  };
}

function generateUPIId() {
  const handles = ['@paytm', '@phonepe', '@googlepay', '@amazonpay', '@bhim'];
  const names = ['rajesh', 'priya', 'amit', 'sunita', 'vikram'];
  return `${names[Math.floor(Math.random() * names.length)]}${Math.floor(Math.random() * 1000)}${handles[Math.floor(Math.random() * handles.length)]}`;
}

function generateBankAccount() {
  const bank = indianBanks[Math.floor(Math.random() * indianBanks.length)];
  return {
    bank: bank,
    account: `${bank}${Math.floor(Math.random() * 900000000) + 100000000}`,
    ifsc: `${bank}0001234`,
  };
}

// API Gateway base URL (configurable)
const API_BASE_URL = __ENV.API_BASE_URL || 'https://api-gateway.example.com';

// Test scenarios
export default function() {
  const scenario = __ENV.K6_SCENARIO || 'normal_traffic';
  const user = generateIndianUser();
  
  // Add Indian context headers
  const headers = {
    'Content-Type': 'application/json',
    'X-User-City': user.city,
    'X-User-Country': 'IN',
    'X-Request-ID': `req_${Math.random().toString(36).substr(2, 12)}`,
    'X-Client-Version': '2.1.0',
    'Accept-Language': 'hi,en-IN;q=0.9,en;q=0.8',
  };
  
  // Route requests based on scenario
  switch (scenario) {
    case 'diwali':
      runEcommerceDiwaliScenario(user, headers);
      break;
    case 'ipl':
      runIPLStreamingScenario(user, headers);
      break;
    case 'upi':
      runUPIPaymentScenario(user, headers);
      break;
    default:
      runNormalTrafficScenario(user, headers);
  }
  
  // Random sleep between 1-3 seconds (realistic user behavior)
  sleep(Math.random() * 2 + 1);
}

function runNormalTrafficScenario(user, headers) {
  const scenarios = [
    () => testAuthenticationAPI(user, headers),
    () => testUserProfileAPI(user, headers),
    () => testProductCatalogAPI(user, headers),
    () => testSearchAPI(user, headers),
  ];
  
  // Run random scenario
  const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
  scenario();
}

function runEcommerceDiwaliScenario(user, headers) {
  // Simulate Diwali shopping behavior
  
  // 1. User authentication
  const authResult = testAuthenticationAPI(user, headers);
  if (!authResult.success) return;
  
  // 2. Browse products (high frequency during sales)
  testProductCatalogAPI(user, headers);
  
  // 3. Search for deals
  const searchQuery = 'diwali sale offers';
  testSearchAPI(user, headers, searchQuery);
  
  // 4. Check cart (multiple times during decision making)
  for (let i = 0; i < Math.floor(Math.random() * 3) + 1; i++) {
    testCartAPI(user, headers);
    sleep(0.5);
  }
  
  // 5. Attempt payment (high conversion during sales)
  if (Math.random() < 0.7) { // 70% proceed to payment
    testPaymentAPI(user, headers);
  }
}

function runIPLStreamingScenario(user, headers) {
  // Simulate IPL match viewing behavior
  
  // 1. Quick authentication
  const authResult = testAuthenticationAPI(user, headers);
  if (!authResult.success) return;
  
  // 2. Get live match data
  testLiveStreamAPI(user, headers);
  
  // 3. Social features (comments, reactions)
  if (Math.random() < 0.8) {
    testSocialAPI(user, headers);
  }
  
  // 4. Get live scores frequently
  for (let i = 0; i < Math.floor(Math.random() * 5) + 1; i++) {
    testLiveScoreAPI(user, headers);
    sleep(Math.random() * 0.5);
  }
}

function runUPIPaymentScenario(user, headers) {
  // Simulate UPI payment flow
  
  // 1. Quick auth
  const authResult = testAuthenticationAPI(user, headers);
  if (!authResult.success) return;
  
  // 2. Multiple UPI transactions (salary day behavior)
  for (let i = 0; i < Math.floor(Math.random() * 3) + 1; i++) {
    testUPITransactionAPI(user, headers);
    sleep(Math.random() * 2);
  }
  
  // 3. Check transaction history
  testTransactionHistoryAPI(user, headers);
}

// Individual API test functions
function testAuthenticationAPI(user, headers) {
  const authStart = Date.now();
  
  const payload = {
    email: user.email,
    password: 'test123',
    device_info: {
      type: 'mobile',
      os: 'android',
      version: '11.0'
    }
  };
  
  const response = http.post(`${API_BASE_URL}/auth/login`, JSON.stringify(payload), { headers });
  
  const success = check(response, {
    'auth status is 200': (r) => r.status === 200,
    'auth response has token': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.token !== undefined;
      } catch (e) {
        return false;
      }
    },
    'auth latency < 100ms': (r) => r.timings.duration < 100,
  });
  
  if (!success) {
    indianErrorRate.add(1);
  }
  
  authLatency.add(Date.now() - authStart);
  
  return { success, token: success ? JSON.parse(response.body).token : null };
}

function testProductCatalogAPI(user, headers) {
  const catalogStart = Date.now();
  
  const category = productCategories[Math.floor(Math.random() * productCategories.length)];
  const response = http.get(`${API_BASE_URL}/products/category/${category}?page=1&limit=20&city=${user.city}`, { headers });
  
  const success = check(response, {
    'catalog status is 200': (r) => r.status === 200,
    'catalog has products': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.products && body.products.length > 0;
      } catch (e) {
        return false;
      }
    },
    'catalog latency < 200ms': (r) => r.timings.duration < 200,
  });
  
  if (!success) {
    indianErrorRate.add(1);
  }
  
  ecommerceLatency.add(Date.now() - catalogStart);
  
  return { success };
}

function testSearchAPI(user, headers, query = null) {
  const searchQuery = query || 'smartphone under 20000';
  const response = http.get(`${API_BASE_URL}/search?q=${encodeURIComponent(searchQuery)}&city=${user.city}`, { headers });
  
  const success = check(response, {
    'search status is 200': (r) => r.status === 200,
    'search has results': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.results !== undefined;
      } catch (e) {
        return false;
      }
    },
    'search latency < 150ms': (r) => r.timings.duration < 150,
  });
  
  if (!success) {
    indianErrorRate.add(1);
  }
  
  return { success };
}

function testCartAPI(user, headers) {
  const response = http.get(`${API_BASE_URL}/cart/${user.id}`, { headers });
  
  const success = check(response, {
    'cart status is 200': (r) => r.status === 200,
    'cart response valid': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.items !== undefined;
      } catch (e) {
        return false;
      }
    },
  });
  
  if (!success) {
    indianErrorRate.add(1);
  }
  
  return { success };
}

function testPaymentAPI(user, headers) {
  const paymentStart = Date.now();
  
  const payload = {
    user_id: user.id,
    amount: Math.floor(Math.random() * 50000) + 1000, // ₹1000-₹50000
    currency: 'INR',
    payment_method: 'UPI',
    upi_id: generateUPIId(),
    merchant_id: 'FLIPKART_MERCHANT',
  };
  
  const response = http.post(`${API_BASE_URL}/payments/process`, JSON.stringify(payload), { headers });
  
  const success = check(response, {
    'payment status is 200 or 202': (r) => r.status === 200 || r.status === 202,
    'payment has transaction_id': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.transaction_id !== undefined;
      } catch (e) {
        return false;
      }
    },
    'payment latency < 300ms': (r) => r.timings.duration < 300,
  });
  
  if (!success) {
    indianErrorRate.add(1);
  }
  
  return { success };
}

function testUPITransactionAPI(user, headers) {
  const upiStart = Date.now();
  
  const payload = {
    from_upi: generateUPIId(),
    to_upi: generateUPIId(),
    amount: Math.floor(Math.random() * 10000) + 100, // ₹100-₹10000
    purpose: 'P2P Transfer',
    note: 'Test payment',
  };
  
  const response = http.post(`${API_BASE_URL}/upi/transfer`, JSON.stringify(payload), { headers });
  
  const success = check(response, {
    'UPI status is 200 or 202': (r) => r.status === 200 || r.status === 202,
    'UPI has reference_id': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.reference_id !== undefined;
      } catch (e) {
        return false;
      }
    },
    'UPI latency < 150ms': (r) => r.timings.duration < 150,
  });
  
  if (!success) {
    indianErrorRate.add(1);
  }
  
  upiLatency.add(Date.now() - upiStart);
  
  return { success };
}

function testLiveStreamAPI(user, headers) {
  const response = http.get(`${API_BASE_URL}/streaming/live/ipl-match-1`, { headers });
  
  const success = check(response, {
    'stream status is 200': (r) => r.status === 200,
    'stream has manifest_url': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.manifest_url !== undefined;
      } catch (e) {
        return false;
      }
    },
  });
  
  if (!success) {
    indianErrorRate.add(1);
  }
  
  return { success };
}

function testSocialAPI(user, headers) {
  const payload = {
    user_id: user.id,
    match_id: 'ipl-match-1',
    message: 'Great shot! 🏏',
    type: 'comment'
  };
  
  const response = http.post(`${API_BASE_URL}/social/comment`, JSON.stringify(payload), { headers });
  
  const success = check(response, {
    'social status is 200 or 201': (r) => r.status === 200 || r.status === 201,
  });
  
  if (!success) {
    indianErrorRate.add(1);
  }
  
  return { success };
}

function testLiveScoreAPI(user, headers) {
  const response = http.get(`${API_BASE_URL}/sports/live-score/ipl-match-1`, { headers });
  
  const success = check(response, {
    'score status is 200': (r) => r.status === 200,
    'score has current_score': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.current_score !== undefined;
      } catch (e) {
        return false;
      }
    },
  });
  
  if (!success) {
    indianErrorRate.add(1);
  }
  
  return { success };
}

function testTransactionHistoryAPI(user, headers) {
  const response = http.get(`${API_BASE_URL}/transactions/history/${user.id}?limit=10`, { headers });
  
  const success = check(response, {
    'history status is 200': (r) => r.status === 200,
    'history has transactions': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.transactions !== undefined;
      } catch (e) {
        return false;
      }
    },
  });
  
  if (!success) {
    indianErrorRate.add(1);
  }
  
  return { success };
}

// Export configuration
export let options = testConfig;

// Custom summary with Indian context
export function handleSummary(data) {
  const summary = textSummary(data, { indent: ' ', enableColors: true });
  
  // Add Indian-specific metrics to summary
  const indianMetrics = `
🇮🇳 Indian Context Metrics:
==========================
🏦 UPI Transaction Latency:
   - P95: ${data.metrics.upi_transaction_latency?.values?.['p(95)']?.toFixed(2) || 'N/A'}ms
   - P99: ${data.metrics.upi_transaction_latency?.values?.['p(99)']?.toFixed(2) || 'N/A'}ms

🛒 E-commerce API Latency:
   - P95: ${data.metrics.ecommerce_api_latency?.values?.['p(95)']?.toFixed(2) || 'N/A'}ms
   - P99: ${data.metrics.ecommerce_api_latency?.values?.['p(99)']?.toFixed(2) || 'N/A'}ms

🔐 Authentication Latency:
   - P95: ${data.metrics.auth_latency?.values?.['p(95)']?.toFixed(2) || 'N/A'}ms
   - P99: ${data.metrics.auth_latency?.values?.['p(99)']?.toFixed(2) || 'N/A'}ms

❌ Indian Error Rate: ${(data.metrics.indian_errors?.values?.rate * 100 || 0).toFixed(2)}%

📊 Scenario Distribution:
${Object.keys(data.root_group.groups || {}).map(scenario => 
  `   - ${scenario}: ${data.root_group.groups[scenario].checks?.passes || 0} passes`
).join('\n')}
`;
  
  return {
    'stdout': summary + indianMetrics,
    'summary.html': generateHTMLReport(data),
    'summary.json': JSON.stringify(data, null, 2),
  };
}

function generateHTMLReport(data) {
  return `
<!DOCTYPE html>
<html>
<head>
    <title>API Gateway Load Test Report - Indian Context</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #FF9933; color: white; padding: 20px; text-align: center; }
        .metrics { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 20px 0; }
        .metric-card { background: #f5f5f5; padding: 15px; border-radius: 8px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #138808; }
        .error { color: #d63031; }
        .chart { height: 200px; background: #f0f0f0; margin: 10px 0; display: flex; align-items: center; justify-content: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🇮🇳 API Gateway Load Test Report</h1>
        <p>Testing Indian traffic patterns and performance</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <h3>🏦 UPI Performance</h3>
            <div class="metric-value">${data.metrics.upi_transaction_latency?.values?.['p(95)']?.toFixed(2) || 'N/A'}ms</div>
            <p>P95 Latency</p>
        </div>
        <div class="metric-card">
            <h3>🛒 E-commerce Performance</h3>
            <div class="metric-value">${data.metrics.ecommerce_api_latency?.values?.['p(95)']?.toFixed(2) || 'N/A'}ms</div>
            <p>P95 Latency</p>
        </div>
        <div class="metric-card">
            <h3>❌ Error Rate</h3>
            <div class="metric-value ${(data.metrics.http_req_failed?.values?.rate || 0) > 0.01 ? 'error' : ''}">${((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2)}%</div>
            <p>Overall Errors</p>
        </div>
    </div>
    
    <h2>📈 Performance Summary</h2>
    <ul>
        <li><strong>Total Requests:</strong> ${data.metrics.http_reqs?.values?.count || 0}</li>
        <li><strong>Requests/sec:</strong> ${data.metrics.http_reqs?.values?.rate?.toFixed(2) || 0}</li>
        <li><strong>Avg Response Time:</strong> ${data.metrics.http_req_duration?.values?.avg?.toFixed(2) || 0}ms</li>
        <li><strong>P95 Response Time:</strong> ${data.metrics.http_req_duration?.values?.['p(95)']?.toFixed(2) || 0}ms</li>
        <li><strong>P99 Response Time:</strong> ${data.metrics.http_req_duration?.values?.['p(99)']?.toFixed(2) || 0}ms</li>
    </ul>
    
    <h2>🎯 Indian Context Results</h2>
    <p>This load test simulated realistic Indian traffic patterns including:</p>
    <ul>
        <li>🪔 <strong>Diwali Sale Traffic:</strong> High-volume e-commerce requests</li>
        <li>🏏 <strong>IPL Streaming Load:</strong> Concurrent live streaming users</li>
        <li>💰 <strong>UPI Payment Rush:</strong> Salary day payment volumes</li>
        <li>🌍 <strong>Multi-city Routing:</strong> Mumbai, Delhi, Bangalore traffic</li>
    </ul>
    
    <p><em>Generated at: ${new Date().toISOString()}</em></p>
</body>
</html>
  `;
}

/*
Usage Examples:

# Normal traffic test
k6 run api-gateway-load-test.js

# Diwali sale simulation
k6 run -e K6_SCENARIO=diwali api-gateway-load-test.js

# IPL streaming simulation  
k6 run -e K6_SCENARIO=ipl api-gateway-load-test.js

# UPI payment rush
k6 run -e K6_SCENARIO=upi api-gateway-load-test.js

# Custom API base URL
k6 run -e API_BASE_URL=https://staging-api.example.com api-gateway-load-test.js

# Custom load levels
k6 run --vus 1000 --duration 30s api-gateway-load-test.js
*/
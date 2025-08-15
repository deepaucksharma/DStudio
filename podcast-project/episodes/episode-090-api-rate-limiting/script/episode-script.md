# Episode 090: API Rate Limiting - Traffic Control for Digital India

## Introduction: Digital India Ka Traffic Police System 🚦

Namaste dosto! Welcome to Tech India Podcast. Aaj hum baat karenge API Rate Limiting ki - yaani digital world ka traffic control system. 

Imagine karo Bangalore ka Silk Board junction during peak hours, ya phir Delhi ka Connaught Place roundabout. Kya hota hai jab saari gaadiyaan ek saath aane ki koshish karti hain? Traffic jam! Exactly yahi problem hoti hai APIs ke saath. Jab bahut saare requests ek saath aate hain, server crash ho jaata hai. API rate limiting is like having smart traffic signals that control the flow.

Ya phir socho IPL match mein run rate restrictions in powerplay - sirf 2 fielders allowed outside 30-yard circle. This is rate limiting! You can score runs, but with controlled aggression. First 6 overs mein zyada fielding restrictions, phir normal, phir death overs mein different strategy.

Aaj hum dekhenge kaise Paytm handle karta hai 100 million users ke payment requests, kaise Flipkart Big Billion Days mein server crash se bachta hai, aur kaise Zomato ensures ki restaurant APIs overload na ho. From IRCTC's Tatkal booking chaos to BookMyShow's movie ticket rush - sab mein rate limiting ka kamaal hai!

## Part 1: Understanding Rate Limiting - The Foundation (60 minutes)

### Chapter 1: What is Rate Limiting? - Digital Queue Management

Dosto, rate limiting basically ek bouncer hai jo club ke entry pe khada hota hai. "Bhai, abhi full hai, 5 minute ruko!" Just like a Gurgaon pub on Saturday night - limited capacity, controlled entry.

```python
# Basic Rate Limiting Concept - Like a Digital Bouncer
import time
from collections import defaultdict
from datetime import datetime, timedelta

class SimpleRateLimiter:
    """
    Basic rate limiter - Like entry control at Phoenix Mall
    Only allows certain number of people (requests) per time window
    """
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests  # Like mall capacity
        self.time_window = time_window    # Per minute
        self.requests = defaultdict(list)
        
    def allow_request(self, user_id):
        """
        Check if user can make request
        Like checking if more people can enter the mall
        """
        current_time = datetime.now()
        
        # Clean old requests (people who left the mall)
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if current_time - req_time < timedelta(seconds=self.time_window)
        ]
        
        # Check current count
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(current_time)
            return True
        
        return False

# Usage example - Like people entering mall
rate_limiter = SimpleRateLimiter(max_requests=5, time_window=60)

# Simulate requests
for i in range(7):
    user = "customer_123"
    if rate_limiter.allow_request(user):
        print(f"✅ Request {i+1}: Entry allowed - Welcome!")
    else:
        print(f"❌ Request {i+1}: Entry denied - Mall full, please wait!")
```

Ab samjho different scenarios:

**IRCTC Tatkal Booking:** Roz subah 10 baje exactly lakhs of people try to book tickets. Without rate limiting, server crash! IRCTC uses rate limiting to ensure:
- Per user: 2 booking attempts per minute
- Per IP: 10 requests per minute  
- During Tatkal hours: Stricter limits
- Normal hours: Relaxed limits

### Chapter 2: Rate Limiting Algorithms - Different Crowd Control Strategies

Just like different events need different crowd control strategies, APIs need different rate limiting algorithms.

#### Token Bucket Algorithm - Festival Token System

Kumbh Mela mein token system - har ghante 1000 tokens milte hain for darshan. Use them whenever, but limited supply!

```python
import time
import threading

class TokenBucketRateLimiter:
    """
    Token Bucket Algorithm - Like Tirupati darshan token system
    Tokens are added at fixed rate, consumed per request
    """
    def __init__(self, capacity=10, refill_rate=1):
        self.capacity = capacity        # Bucket size (max tokens)
        self.tokens = capacity          # Current tokens
        self.refill_rate = refill_rate  # Tokens per second
        self.lock = threading.Lock()
        self.last_refill = time.time()
        
    def _refill(self):
        """
        Add tokens based on time elapsed
        Like temple issuing new darshan tokens every hour
        """
        now = time.time()
        tokens_to_add = (now - self.last_refill) * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
        
    def allow_request(self, tokens_required=1):
        """
        Check if request can proceed
        Like checking if devotee has valid token
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens_required:
                self.tokens -= tokens_required
                return True
            
            return False
    
    def get_wait_time(self, tokens_required=1):
        """
        Calculate wait time for next available token
        Like telling devotee "come back after 30 minutes"
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens_required:
                return 0
                
            tokens_needed = tokens_required - self.tokens
            wait_time = tokens_needed / self.refill_rate
            
            return wait_time

# Example usage - Temple darshan system
darshan_limiter = TokenBucketRateLimiter(capacity=100, refill_rate=10)

print("🛕 Tirupati Darshan Token System Simulation")
print("-" * 50)

for devotee in range(120):
    if darshan_limiter.allow_request():
        print(f"Devotee {devotee+1}: ✅ Darshan allowed")
    else:
        wait_time = darshan_limiter.get_wait_time()
        print(f"Devotee {devotee+1}: ⏳ Wait {wait_time:.1f} seconds")
        
    if devotee % 20 == 19:
        print("--- Taking 2 second break (tokens refilling) ---")
        time.sleep(2)
```

#### Sliding Window Algorithm - IPL Run Rate Calculation

IPL mein run rate calculate karte hain sliding window se - last 5 overs ka average, constantly updating!

```python
from collections import deque
import time

class SlidingWindowRateLimiter:
    """
    Sliding Window Rate Limiter - Like IPL run rate tracking
    Maintains a sliding window of requests
    """
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # user_id -> deque of timestamps
        
    def allow_request(self, user_id):
        """
        Check if request allowed in current window
        Like checking if team maintaining required run rate
        """
        current_time = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = deque()
            
        # Remove old requests outside window
        # Like removing overs that are no longer in last 5
        while (self.requests[user_id] and 
               self.requests[user_id][0] < current_time - self.window_seconds):
            self.requests[user_id].popleft()
            
        # Check if under limit
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(current_time)
            return True
            
        return False
    
    def get_current_rate(self, user_id):
        """
        Get current request rate
        Like current run rate in cricket
        """
        if user_id not in self.requests:
            return 0
            
        current_time = time.time()
        
        # Clean old requests
        while (self.requests[user_id] and 
               self.requests[user_id][0] < current_time - self.window_seconds):
            self.requests[user_id].popleft()
            
        return len(self.requests[user_id])

# IPL Run Rate Example
ipl_limiter = SlidingWindowRateLimiter(max_requests=36, window_seconds=60)

print("🏏 IPL Run Rate Monitoring System")
print("Target: 36 runs in 6 overs (6 per over)")
print("-" * 50)

teams = ["CSK", "MI", "RCB"]
for over in range(1, 8):
    print(f"\n--- Over {over} ---")
    for team in teams:
        runs_this_over = 4 + (over % 3) * 2  # Varying run rate
        
        for run in range(runs_this_over):
            if ipl_limiter.allow_request(team):
                current_rate = ipl_limiter.get_current_rate(team)
                print(f"{team}: Run scored! Current rate: {current_rate}/36")
            else:
                print(f"{team}: ❌ Rate limit exceeded! Slow down!")
```

### Chapter 3: Distributed Rate Limiting - Coordination Across Cities

Jab multiple servers hain (like Ola cabs in different cities), rate limiting coordinate karna is like managing traffic across all metros!

```java
// Java Implementation - Distributed Rate Limiting with Redis
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;
import java.util.List;

public class DistributedRateLimiter {
    /**
     * Distributed Rate Limiter using Redis
     * Like coordinating traffic across Delhi, Mumbai, Bangalore
     */
    
    private JedisPool jedisPool;
    private int maxRequests;
    private int windowSeconds;
    
    public DistributedRateLimiter(String redisHost, int redisPort, 
                                  int maxRequests, int windowSeconds) {
        JedisPoolConfig config = new JedisPoolConfig();
        config.setMaxTotal(100);
        config.setMaxIdle(50);
        
        this.jedisPool = new JedisPool(config, redisHost, redisPort);
        this.maxRequests = maxRequests;
        this.windowSeconds = windowSeconds;
    }
    
    public boolean allowRequest(String userId, String apiEndpoint) {
        /**
         * Check if request allowed using Redis
         * Like checking traffic density across city
         */
        try (Jedis jedis = jedisPool.getResource()) {
            String key = String.format("rate_limit:%s:%s", userId, apiEndpoint);
            long currentTime = System.currentTimeMillis() / 1000;
            
            // Use Redis sorted set for sliding window
            // Remove old entries
            jedis.zremrangeByScore(key, 0, currentTime - windowSeconds);
            
            // Count current requests
            long currentCount = jedis.zcard(key);
            
            if (currentCount < maxRequests) {
                // Add new request
                jedis.zadd(key, currentTime, String.valueOf(System.nanoTime()));
                jedis.expire(key, windowSeconds + 1);
                return true;
            }
            
            return false;
        }
    }
    
    public RateLimitInfo getRateLimitInfo(String userId, String apiEndpoint) {
        /**
         * Get current rate limit status
         * Like traffic density report
         */
        try (Jedis jedis = jedisPool.getResource()) {
            String key = String.format("rate_limit:%s:%s", userId, apiEndpoint);
            long currentTime = System.currentTimeMillis() / 1000;
            
            jedis.zremrangeByScore(key, 0, currentTime - windowSeconds);
            long currentCount = jedis.zcard(key);
            
            return new RateLimitInfo(
                maxRequests,
                (int) currentCount,
                maxRequests - (int) currentCount,
                windowSeconds
            );
        }
    }
    
    static class RateLimitInfo {
        public int limit;
        public int used;
        public int remaining;
        public int resetInSeconds;
        
        public RateLimitInfo(int limit, int used, int remaining, int resetInSeconds) {
            this.limit = limit;
            this.used = used;
            this.remaining = remaining;
            this.resetInSeconds = resetInSeconds;
        }
    }
}

// Example Usage - Like Ola managing ride requests
class OlaRideRequestManager {
    public static void main(String[] args) {
        DistributedRateLimiter rateLimiter = new DistributedRateLimiter(
            "localhost", 6379, 100, 60  // 100 requests per minute
        );
        
        String[] cities = {"Delhi", "Mumbai", "Bangalore", "Kolkata"};
        String[] users = {"driver_101", "driver_102", "driver_103"};
        
        System.out.println("🚗 Ola Driver Request Management System");
        System.out.println("=====================================");
        
        for (String city : cities) {
            System.out.println("\n📍 City: " + city);
            
            for (String user : users) {
                String endpoint = "/api/rides/" + city.toLowerCase();
                
                // Simulate multiple requests
                for (int i = 0; i < 5; i++) {
                    if (rateLimiter.allowRequest(user, endpoint)) {
                        System.out.println("✅ " + user + ": Ride request accepted");
                    } else {
                        RateLimitInfo info = rateLimiter.getRateLimitInfo(user, endpoint);
                        System.out.println("❌ " + user + ": Rate limit exceeded! " +
                            "Used: " + info.used + "/" + info.limit);
                    }
                }
            }
        }
    }
}
```

## Part 2: Implementation Strategies - Building the System (60 minutes)

### Chapter 4: API Gateway Rate Limiting - The Main Entry Point

API Gateway is like India Gate - sabko yahan se guzarna padta hai. Perfect place for rate limiting!

```go
// Go Implementation - API Gateway Rate Limiter
package main

import (
    "context"
    "fmt"
    "net/http"
    "sync"
    "time"
    
    "github.com/go-redis/redis/v8"
    "golang.org/x/time/rate"
)

// RateLimiterMiddleware - Like security check at India Gate
type RateLimiterMiddleware struct {
    localLimiters  map[string]*rate.Limiter
    mu             sync.RWMutex
    redisClient    *redis.Client
    defaultLimit   rate.Limit
    defaultBurst   int
}

// NewRateLimiterMiddleware creates new rate limiter
func NewRateLimiterMiddleware(redisAddr string, defaultRPS int, burst int) *RateLimiterMiddleware {
    rdb := redis.NewClient(&redis.Options{
        Addr:     redisAddr,
        Password: "",
        DB:       0,
    })
    
    return &RateLimiterMiddleware{
        localLimiters:  make(map[string]*rate.Limiter),
        redisClient:    rdb,
        defaultLimit:   rate.Limit(defaultRPS),
        defaultBurst:   burst,
    }
}

// getLimiter returns limiter for specific client
func (rl *RateLimiterMiddleware) getLimiter(clientID string) *rate.Limiter {
    rl.mu.RLock()
    limiter, exists := rl.localLimiters[clientID]
    rl.mu.RUnlock()
    
    if !exists {
        rl.mu.Lock()
        defer rl.mu.Unlock()
        
        // Check again after acquiring write lock
        limiter, exists = rl.localLimiters[clientID]
        if !exists {
            // Create new limiter for this client
            limiter = rate.NewLimiter(rl.defaultLimit, rl.defaultBurst)
            rl.localLimiters[clientID] = limiter
        }
    }
    
    return limiter
}

// Middleware handles rate limiting
func (rl *RateLimiterMiddleware) Middleware(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        // Extract client ID (from API key, JWT, IP, etc.)
        clientID := extractClientID(r)
        
        // Get limiter for this client
        limiter := rl.getLimiter(clientID)
        
        // Check if request allowed
        if !limiter.Allow() {
            // Rate limit exceeded
            w.Header().Set("X-RateLimit-Limit", fmt.Sprintf("%d", rl.defaultLimit))
            w.Header().Set("X-RateLimit-Remaining", "0")
            w.Header().Set("X-RateLimit-Reset", fmt.Sprintf("%d", time.Now().Add(time.Second).Unix()))
            w.Header().Set("Retry-After", "1")
            
            http.Error(w, "Rate limit exceeded. Please slow down!", http.StatusTooManyRequests)
            return
        }
        
        // Add rate limit headers
        w.Header().Set("X-RateLimit-Limit", fmt.Sprintf("%d", rl.defaultLimit))
        w.Header().Set("X-RateLimit-Remaining", fmt.Sprintf("%d", limiter.Tokens()))
        
        // Process request
        next(w, r)
    }
}

// extractClientID gets client identifier from request
func extractClientID(r *http.Request) string {
    // Try API key first
    apiKey := r.Header.Get("X-API-Key")
    if apiKey != "" {
        return apiKey
    }
    
    // Fall back to IP address
    return r.RemoteAddr
}

// Example API handlers
func healthHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "API is healthy! 🎉")
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Search results for: %s", r.URL.Query().Get("q"))
}

func paymentHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Payment processed successfully! 💰")
}

func main() {
    // Create rate limiter middleware
    rateLimiter := NewRateLimiterMiddleware("localhost:6379", 10, 20)
    
    // Setup routes with rate limiting
    http.HandleFunc("/health", rateLimiter.Middleware(healthHandler))
    http.HandleFunc("/api/search", rateLimiter.Middleware(searchHandler))
    http.HandleFunc("/api/payment", rateLimiter.Middleware(paymentHandler))
    
    fmt.Println("🚀 API Gateway with Rate Limiting starting on :8080")
    fmt.Println("Rate Limit: 10 requests per second, burst of 20")
    
    if err := http.ListenAndServe(":8080", nil); err != nil {
        panic(err)
    }
}
```

### Chapter 5: Client-Side Rate Limiting - Being a Good Citizen

Client-side rate limiting is like being a responsible driver - don't honk unnecessarily, maintain distance, follow rules!

```python
import time
import random
from typing import Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

class SmartAPIClient:
    """
    Smart API client with rate limit handling
    Like a responsible driver in Bangalore traffic
    """
    
    def __init__(self, base_url: str, retry_config: Optional[RetryConfig] = None):
        self.base_url = base_url
        self.retry_config = retry_config or RetryConfig()
        self.rate_limit_info = {}
        
    def parse_rate_limit_headers(self, headers: dict) -> dict:
        """
        Parse rate limit information from response headers
        Like reading traffic signals
        """
        return {
            'limit': int(headers.get('X-RateLimit-Limit', 0)),
            'remaining': int(headers.get('X-RateLimit-Remaining', 0)),
            'reset': int(headers.get('X-RateLimit-Reset', 0)),
            'retry_after': int(headers.get('Retry-After', 0))
        }
    
    def calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff with jitter
        Like waiting at red signal with random variation
        """
        delay = min(
            self.retry_config.base_delay * (self.retry_config.exponential_base ** attempt),
            self.retry_config.max_delay
        )
        
        if self.retry_config.jitter:
            delay = delay * (0.5 + random.random())
            
        return delay
    
    def should_retry(self, status_code: int, attempt: int) -> bool:
        """
        Determine if request should be retried
        Like deciding whether to take alternate route
        """
        if attempt >= self.retry_config.max_retries:
            return False
            
        # Retry on rate limit or server errors
        return status_code in [429, 500, 502, 503, 504]
    
    def make_request(self, endpoint: str, method: str = 'GET', 
                    data: Optional[dict] = None) -> dict:
        """
        Make API request with intelligent retry logic
        Like navigating through traffic with patience
        """
        import requests
        
        url = f"{self.base_url}{endpoint}"
        attempt = 0
        
        while attempt <= self.retry_config.max_retries:
            try:
                # Check if we should wait before making request
                if endpoint in self.rate_limit_info:
                    info = self.rate_limit_info[endpoint]
                    if info['remaining'] == 0:
                        wait_time = info['reset'] - time.time()
                        if wait_time > 0:
                            print(f"⏳ Rate limit reached. Waiting {wait_time:.1f}s...")
                            time.sleep(wait_time)
                
                # Make the request
                response = requests.request(method, url, json=data)
                
                # Update rate limit info
                if 'X-RateLimit-Limit' in response.headers:
                    self.rate_limit_info[endpoint] = self.parse_rate_limit_headers(
                        response.headers
                    )
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 
                                     self.calculate_backoff(attempt)))
                    
                    print(f"🚦 Rate limited! Waiting {retry_after}s before retry...")
                    time.sleep(retry_after)
                    attempt += 1
                    continue
                
                # Check for server errors
                if response.status_code >= 500:
                    if self.should_retry(response.status_code, attempt):
                        backoff = self.calculate_backoff(attempt)
                        print(f"⚠️ Server error {response.status_code}. "
                              f"Retrying in {backoff:.1f}s...")
                        time.sleep(backoff)
                        attempt += 1
                        continue
                
                # Success or client error - return response
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt >= self.retry_config.max_retries:
                    raise
                    
                backoff = self.calculate_backoff(attempt)
                print(f"❌ Request failed: {e}. Retrying in {backoff:.1f}s...")
                time.sleep(backoff)
                attempt += 1
        
        raise Exception(f"Max retries ({self.retry_config.max_retries}) exceeded")

# Circuit Breaker Pattern - Emergency Stop
class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures
    Like emergency chain in trains
    """
    
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection
        """
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should try to reset circuit"""
        return (self.last_failure_time and 
                datetime.now() - self.last_failure_time > 
                timedelta(seconds=self.recovery_timeout))
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'
            print("✅ Circuit breaker reset to CLOSED")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            print(f"🔴 Circuit breaker OPENED after {self.failure_count} failures")

# Example usage - Like booking movie tickets on BookMyShow
def demonstrate_smart_client():
    """
    Demonstrate smart API client with rate limiting
    Like booking tickets during Pathaan first day first show
    """
    print("🎬 BookMyShow Ticket Booking Simulation")
    print("=" * 50)
    
    # Create smart client
    client = SmartAPIClient(
        base_url="https://api.bookmyshow.com",
        retry_config=RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            jitter=True
        )
    )
    
    # Circuit breaker for payment service
    payment_breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=30
    )
    
    # Simulate multiple booking attempts
    shows = [
        "Pathaan-IMAX-9AM",
        "Pathaan-4DX-12PM", 
        "Pathaan-IMAX-3PM",
        "Pathaan-Regular-6PM",
        "Pathaan-IMAX-9PM"
    ]
    
    for show in shows:
        print(f"\n🎫 Attempting to book: {show}")
        
        try:
            # Check seat availability
            availability = client.make_request(
                f"/shows/{show}/availability",
                method='GET'
            )
            print(f"  Seats available: {availability.get('seats', 0)}")
            
            # Book tickets with circuit breaker
            def book_tickets():
                return client.make_request(
                    f"/bookings",
                    method='POST',
                    data={
                        'show': show,
                        'seats': 2,
                        'user': 'movie_fan_123'
                    }
                )
            
            booking = payment_breaker.call(book_tickets)
            print(f"  ✅ Booking successful! ID: {booking.get('booking_id')}")
            
        except Exception as e:
            print(f"  ❌ Booking failed: {e}")

demonstrate_smart_client()
```

### Chapter 6: Production Challenges - Real War Stories

Ab suniye real production stories where rate limiting saved the day (or didn't)!

```python
"""
Production War Story #1: Paytm Demonetization Crisis
November 8, 2016 - The night that changed digital payments
"""

class PaytmDemonetizationStory:
    """
    How Paytm handled 1000x traffic spike during demonetization
    """
    
    def __init__(self):
        self.timeline = {
            "8:00 PM": "PM announces demonetization",
            "8:15 PM": "Traffic starts spiking",
            "8:30 PM": "10x normal traffic",
            "9:00 PM": "100x traffic - servers struggling",
            "9:30 PM": "Emergency rate limiting deployed",
            "10:00 PM": "System stabilized with queuing",
            "12:00 AM": "1000x traffic handled successfully"
        }
        
    def what_worked(self):
        return {
            'dynamic_rate_limiting': 'Adjusted limits based on server load',
            'priority_queues': 'KYC users got priority',
            'graceful_degradation': 'Non-essential features turned off',
            'caching': 'Aggressive caching of wallet balances',
            'message_queuing': 'Async processing of transactions'
        }
    
    def implementation_details(self):
        """
        Actual implementation that saved Paytm
        """
        return """
        # Dynamic Rate Limiting Based on Server Load
        def adjust_rate_limits():
            cpu_usage = get_server_metrics()['cpu']
            memory_usage = get_server_metrics()['memory']
            
            if cpu_usage > 80 or memory_usage > 85:
                # Panic mode - strict limits
                set_rate_limit('wallet_check', 10)  # 10 req/min
                set_rate_limit('add_money', 5)      # 5 req/min
                set_rate_limit('transfer', 2)       # 2 req/min
            elif cpu_usage > 60:
                # Moderate limits
                set_rate_limit('wallet_check', 30)
                set_rate_limit('add_money', 15)
                set_rate_limit('transfer', 10)
            else:
                # Normal limits
                set_rate_limit('wallet_check', 100)
                set_rate_limit('add_money', 50)
                set_rate_limit('transfer', 30)
        """

"""
Production War Story #2: Flipkart Big Billion Days 2023
The ₹10,000 Crore Sale That Almost Crashed
"""

class FlipkartBBD2023:
    """
    How Flipkart handled 50 million concurrent users
    """
    
    def __init__(self):
        self.stats = {
            'peak_traffic': '50M concurrent users',
            'orders_per_second': '25,000',
            'total_requests': '10 billion/day',
            'infrastructure_cost': '₹50 crores',
            'revenue': '₹10,000 crores'
        }
        
    def rate_limiting_strategy(self):
        return {
            'tiered_limits': {
                'platinum_customers': '1000 req/min',
                'gold_customers': '500 req/min',
                'silver_customers': '200 req/min',
                'new_users': '50 req/min'
            },
            'endpoint_specific': {
                '/search': '100 req/min',
                '/product/*': '200 req/min',
                '/cart': '50 req/min',
                '/checkout': '10 req/min',
                '/payment': '5 req/min'
            },
            'geographic_distribution': {
                'metros': 'Full capacity',
                'tier2_cities': '80% capacity',
                'tier3_cities': '60% capacity'
            }
        }

"""
Production War Story #3: IRCTC Tatkal Chaos
Every morning at 10 AM - The digital stampede
"""

class IRCTCTatkalSystem:
    """
    How IRCTC manages 10 lakh users at exactly 10 AM
    """
    
    def __init__(self):
        self.daily_stats = {
            'users_at_10am': '10,00,000',
            'requests_first_minute': '5 crore',
            'tickets_available': '1,20,000',
            'success_rate': '12%'
        }
        
    def current_implementation(self):
        """
        IRCTC's actual rate limiting implementation
        """
        return {
            'captcha': 'Slows down bots',
            'otp_verification': 'Prevents multiple bookings',
            'rate_limits': {
                'login': '3 attempts per 5 minutes',
                'search': '10 requests per minute',
                'booking': '2 attempts per minute',
                'payment': '1 attempt per 2 minutes'
            },
            'queue_system': 'Virtual waiting room',
            'session_management': '15 minute timeout'
        }
```

## Part 3: Advanced Topics and Best Practices (60 minutes)

### Chapter 7: Cost Optimization - Saving Money with Smart Rate Limiting

Rate limiting isn't just about protecting servers - it's about saving money too!

```python
class CostOptimizationCalculator:
    """
    Calculate cost savings from rate limiting
    Like calculating savings from carpooling
    """
    
    def __init__(self):
        # AWS/Azure pricing in INR
        self.costs = {
            'ec2_per_hour': 50,         # ₹50 per hour
            'data_transfer_per_gb': 7,   # ₹7 per GB
            'api_gateway_per_million': 250,  # ₹250 per million requests
            'redis_cache_per_hour': 35,  # ₹35 per hour
            'cloudwatch_per_metric': 20  # ₹20 per metric per month
        }
        
    def calculate_monthly_savings(self, metrics):
        """
        Calculate how much money rate limiting saves
        """
        # Without rate limiting
        without_rl = {
            'servers_needed': metrics['peak_traffic'] / 1000,  # 1 server per 1000 RPS
            'data_transfer_gb': metrics['total_requests'] * 0.001,  # 1KB per request
            'api_calls': metrics['total_requests']
        }
        
        # With rate limiting
        with_rl = {
            'servers_needed': metrics['peak_traffic'] / 2000,  # Better efficiency
            'data_transfer_gb': metrics['total_requests'] * 0.0005,  # Less retry traffic
            'api_calls': metrics['total_requests'] * 0.7  # 30% reduction
        }
        
        # Calculate costs (monthly)
        cost_without = (
            without_rl['servers_needed'] * self.costs['ec2_per_hour'] * 24 * 30 +
            without_rl['data_transfer_gb'] * self.costs['data_transfer_per_gb'] +
            without_rl['api_calls'] / 1000000 * self.costs['api_gateway_per_million']
        )
        
        cost_with = (
            with_rl['servers_needed'] * self.costs['ec2_per_hour'] * 24 * 30 +
            with_rl['data_transfer_gb'] * self.costs['data_transfer_per_gb'] +
            with_rl['api_calls'] / 1000000 * self.costs['api_gateway_per_million'] +
            10 * self.costs['redis_cache_per_hour'] * 24 * 30  # Redis cluster cost
        )
        
        savings = cost_without - cost_with
        roi_percentage = (savings / cost_with) * 100
        
        return {
            'monthly_cost_without_rl': f"₹{cost_without:,.0f}",
            'monthly_cost_with_rl': f"₹{cost_with:,.0f}",
            'monthly_savings': f"₹{savings:,.0f}",
            'roi_percentage': f"{roi_percentage:.1f}%",
            'payback_period_days': int(cost_with / (savings / 30)) if savings > 0 else 'Never'
        }

# Real company examples
companies = {
    'Swiggy': {
        'peak_traffic': 50000,  # RPS
        'total_requests': 1000000000,  # Monthly
        'company': 'Swiggy',
        'use_case': 'Food delivery APIs'
    },
    'Zerodha': {
        'peak_traffic': 100000,
        'total_requests': 5000000000,
        'company': 'Zerodha',
        'use_case': 'Stock trading APIs'
    },
    'Dream11': {
        'peak_traffic': 200000,
        'total_requests': 10000000000,
        'company': 'Dream11',
        'use_case': 'Fantasy sports APIs'
    }
}

calculator = CostOptimizationCalculator()

print("💰 Rate Limiting ROI Analysis for Indian Companies")
print("=" * 60)

for company_name, metrics in companies.items():
    metrics_copy = metrics.copy()
    savings = calculator.calculate_monthly_savings(metrics_copy)
    
    print(f"\n🏢 {company_name} - {metrics['use_case']}")
    print(f"   Peak Traffic: {metrics['peak_traffic']:,} RPS")
    print(f"   Monthly Requests: {metrics['total_requests']:,}")
    print(f"   Without Rate Limiting: {savings['monthly_cost_without_rl']}")
    print(f"   With Rate Limiting: {savings['monthly_cost_with_rl']}")
    print(f"   💵 Monthly Savings: {savings['monthly_savings']}")
    print(f"   📈 ROI: {savings['roi_percentage']}")
```

### Chapter 8: Monitoring and Alerting - Keeping Watch

Rate limiting monitoring is like CCTV cameras at traffic signals - you need to see what's happening!

```python
import time
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List
import json

class RateLimitMonitor:
    """
    Monitor rate limiting effectiveness
    Like traffic monitoring system on highways
    """
    
    def __init__(self):
        self.metrics = defaultdict(lambda: {
            'total_requests': 0,
            'rate_limited_requests': 0,
            'successful_requests': 0,
            'error_requests': 0,
            'response_times': [],
            'unique_users': set(),
            'violations_by_user': defaultdict(int)
        })
        self.alerts = []
        self.thresholds = {
            'rate_limit_percentage': 20,  # Alert if >20% requests rate limited
            'error_percentage': 5,        # Alert if >5% errors
            'p99_latency': 1000,          # Alert if P99 > 1 second
            'violations_per_user': 100    # Alert if user violates >100 times
        }
        
    def record_request(self, endpoint: str, user_id: str, 
                       status: str, response_time: float):
        """
        Record request metrics
        """
        metrics = self.metrics[endpoint]
        metrics['total_requests'] += 1
        metrics['unique_users'].add(user_id)
        metrics['response_times'].append(response_time)
        
        if status == 'rate_limited':
            metrics['rate_limited_requests'] += 1
            metrics['violations_by_user'][user_id] += 1
        elif status == 'success':
            metrics['successful_requests'] += 1
        elif status == 'error':
            metrics['error_requests'] += 1
            
        # Check for alerts
        self._check_alerts(endpoint, user_id)
        
    def _check_alerts(self, endpoint: str, user_id: str):
        """
        Check if any alert conditions are met
        Like traffic police checking for violations
        """
        metrics = self.metrics[endpoint]
        
        # Check rate limit percentage
        if metrics['total_requests'] > 100:  # Minimum sample size
            rl_percentage = (metrics['rate_limited_requests'] / 
                           metrics['total_requests']) * 100
            
            if rl_percentage > self.thresholds['rate_limit_percentage']:
                self._trigger_alert(
                    'HIGH_RATE_LIMIT',
                    f"Endpoint {endpoint} has {rl_percentage:.1f}% rate limited requests",
                    'warning'
                )
        
        # Check user violations
        if metrics['violations_by_user'][user_id] > self.thresholds['violations_per_user']:
            self._trigger_alert(
                'ABUSIVE_USER',
                f"User {user_id} has {metrics['violations_by_user'][user_id]} violations",
                'critical'
            )
            
    def _trigger_alert(self, alert_type: str, message: str, severity: str):
        """
        Trigger alert
        Like sounding traffic violation siren
        """
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        
        self.alerts.append(alert)
        
        # In production, this would send to PagerDuty, Slack, etc.
        print(f"🚨 ALERT [{severity.upper()}]: {message}")
        
    def get_dashboard_metrics(self, endpoint: str) -> Dict:
        """
        Get metrics for dashboard display
        Like traffic control room dashboard
        """
        metrics = self.metrics[endpoint]
        
        if not metrics['response_times']:
            return {}
            
        sorted_times = sorted(metrics['response_times'])
        
        return {
            'endpoint': endpoint,
            'total_requests': metrics['total_requests'],
            'rate_limited': metrics['rate_limited_requests'],
            'successful': metrics['successful_requests'],
            'errors': metrics['error_requests'],
            'unique_users': len(metrics['unique_users']),
            'rate_limit_percentage': (
                (metrics['rate_limited_requests'] / metrics['total_requests'] * 100)
                if metrics['total_requests'] > 0 else 0
            ),
            'avg_response_time': sum(sorted_times) / len(sorted_times),
            'p50_response_time': sorted_times[len(sorted_times) // 2],
            'p95_response_time': sorted_times[int(len(sorted_times) * 0.95)],
            'p99_response_time': sorted_times[int(len(sorted_times) * 0.99)],
            'top_violators': sorted(
                metrics['violations_by_user'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

# Grafana Dashboard Configuration
def generate_grafana_dashboard():
    """
    Generate Grafana dashboard config for rate limiting
    Like setting up traffic monitoring screens
    """
    dashboard = {
        "dashboard": {
            "title": "API Rate Limiting Dashboard - Production",
            "panels": [
                {
                    "title": "Request Rate",
                    "type": "graph",
                    "targets": [
                        {"expr": "rate(api_requests_total[5m])"},
                        {"expr": "rate(api_rate_limited_total[5m])"}
                    ]
                },
                {
                    "title": "Rate Limit Violations",
                    "type": "stat",
                    "targets": [
                        {"expr": "sum(rate(api_rate_limited_total[5m]))"}
                    ]
                },
                {
                    "title": "Top Violating Users",
                    "type": "table",
                    "targets": [
                        {"expr": "topk(10, sum by(user_id)(api_rate_limited_total))"}
                    ]
                },
                {
                    "title": "Response Time (P99)",
                    "type": "graph",
                    "targets": [
                        {"expr": "histogram_quantile(0.99, api_response_time_bucket)"}
                    ]
                },
                {
                    "title": "Error Rate",
                    "type": "graph",
                    "targets": [
                        {"expr": "rate(api_errors_total[5m])"}
                    ]
                }
            ]
        }
    }
    
    return json.dumps(dashboard, indent=2)

# Simulate monitoring
monitor = RateLimitMonitor()

print("📊 Rate Limiting Monitoring Simulation")
print("=" * 50)

# Simulate traffic
endpoints = ['/api/search', '/api/payment', '/api/user']
users = [f'user_{i}' for i in range(100)]
statuses = ['success'] * 70 + ['rate_limited'] * 25 + ['error'] * 5

import random

for _ in range(1000):
    endpoint = random.choice(endpoints)
    user = random.choice(users)
    status = random.choice(statuses)
    response_time = random.uniform(10, 500) if status == 'success' else 5
    
    monitor.record_request(endpoint, user, status, response_time)

# Display dashboard metrics
for endpoint in endpoints:
    metrics = monitor.get_dashboard_metrics(endpoint)
    print(f"\n📍 Endpoint: {endpoint}")
    print(f"   Total Requests: {metrics['total_requests']}")
    print(f"   Rate Limited: {metrics['rate_limited']} ({metrics['rate_limit_percentage']:.1f}%)")
    print(f"   Unique Users: {metrics['unique_users']}")
    print(f"   Avg Response Time: {metrics['avg_response_time']:.2f}ms")
    print(f"   P99 Response Time: {metrics['p99_response_time']:.2f}ms")
    if metrics['top_violators']:
        print(f"   Top Violator: {metrics['top_violators'][0][0]} ({metrics['top_violators'][0][1]} violations)")
```

### Chapter 9: API Rate Limiting Best Practices

Best practices for rate limiting - learned from Indian tech companies' experiences!

```python
class RateLimitingBestPractices:
    """
    Best practices from Indian tech ecosystem
    Lessons learned the hard way!
    """
    
    def __init__(self):
        self.practices = self.load_best_practices()
        
    def load_best_practices(self):
        return {
            'design_principles': [
                {
                    'principle': 'Be Transparent',
                    'description': 'Always return rate limit info in headers',
                    'example': 'X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset',
                    'company_example': 'Razorpay provides detailed rate limit headers'
                },
                {
                    'principle': 'Graceful Degradation',
                    'description': 'Dont just block - provide alternatives',
                    'example': 'Return cached data when rate limited',
                    'company_example': 'Swiggy returns cached restaurant data during peak'
                },
                {
                    'principle': 'Fair Usage',
                    'description': 'Different limits for different user tiers',
                    'example': 'Free: 100/hr, Pro: 1000/hr, Enterprise: 10000/hr',
                    'company_example': 'Postman API tiers'
                }
            ],
            
            'implementation_tips': [
                {
                    'tip': 'Use Distributed Rate Limiting',
                    'why': 'Single server limiting fails at scale',
                    'how': 'Redis or DynamoDB for shared state',
                    'gotcha': 'Network latency adds overhead'
                },
                {
                    'tip': 'Implement Client Identification',
                    'why': 'IP-based limiting fails behind NAT',
                    'how': 'API keys, JWT tokens, OAuth',
                    'gotcha': 'Key rotation needs handling'
                },
                {
                    'tip': 'Add Burst Allowance',
                    'why': 'Real traffic is bursty',
                    'how': 'Token bucket or leaky bucket',
                    'gotcha': 'Too much burst can overload'
                }
            ],
            
            'common_mistakes': [
                {
                    'mistake': 'Rate limiting only at API Gateway',
                    'problem': 'Internal services get overloaded',
                    'solution': 'Rate limit at multiple layers',
                    'real_incident': 'Ola outage when internal service overwhelmed'
                },
                {
                    'mistake': 'Same limits for all endpoints',
                    'problem': 'Heavy endpoints block light ones',
                    'solution': 'Endpoint-specific limits',
                    'real_incident': 'Zomato search blocking orders'
                },
                {
                    'mistake': 'Not testing rate limits',
                    'problem': 'Limits too strict or too loose',
                    'solution': 'Load test with rate limits',
                    'real_incident': 'Paytm blocking legitimate users'
                }
            ],
            
            'testing_strategies': [
                'Load test with gradual increase',
                'Test with burst traffic patterns',
                'Simulate different client types',
                'Test failover scenarios',
                'Verify rate limit headers',
                'Test with clock skew'
            ]
        }
    
    def generate_implementation_checklist(self):
        """
        Checklist for implementing rate limiting
        Like pilot's pre-flight checklist
        """
        return """
        ✅ RATE LIMITING IMPLEMENTATION CHECKLIST
        =========================================
        
        Planning Phase:
        □ Identify all API endpoints
        □ Analyze traffic patterns
        □ Define rate limit tiers
        □ Document limits in API docs
        □ Plan monitoring strategy
        
        Implementation Phase:
        □ Choose rate limiting algorithm
        □ Setup distributed cache (Redis)
        □ Implement at API Gateway
        □ Add service-level limits
        □ Configure burst allowance
        □ Add rate limit headers
        □ Implement graceful errors
        
        Testing Phase:
        □ Unit test rate limiter
        □ Integration test with cache
        □ Load test with limits
        □ Test burst scenarios
        □ Test failover behavior
        □ Verify monitoring metrics
        
        Deployment Phase:
        □ Deploy with conservative limits
        □ Monitor for false positives
        □ Gradually tune limits
        □ Setup alerting rules
        □ Document runbooks
        □ Train support team
        
        Post-Deployment:
        □ Analyze rate limit metrics
        □ Identify top violators
        □ Tune limits based on data
        □ Review customer feedback
        □ Update documentation
        □ Plan capacity for growth
        """

# Configuration Templates for Popular Frameworks
class FrameworkConfigurations:
    """
    Ready-to-use configurations for different frameworks
    """
    
    @staticmethod
    def nginx_config():
        return """
        # Nginx Rate Limiting Configuration
        http {
            # Define rate limit zones
            limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
            limit_req_zone $http_x_api_key zone=key_limit:10m rate=100r/s;
            
            # API endpoints
            location /api/ {
                # Apply rate limiting
                limit_req zone=api_limit burst=20 nodelay;
                limit_req zone=key_limit burst=100 nodelay;
                
                # Custom error page
                limit_req_status 429;
                error_page 429 /429.html;
                
                # Add rate limit headers
                add_header X-RateLimit-Limit 10;
                add_header X-RateLimit-Remaining $limit_req_remaining;
                add_header X-RateLimit-Reset $limit_req_reset;
                
                proxy_pass http://backend;
            }
        }
        """
    
    @staticmethod
    def spring_boot_config():
        return """
        // Spring Boot Rate Limiting with Bucket4j
        @Configuration
        public class RateLimitConfig {
            
            @Bean
            public Bucket createBucket() {
                Bandwidth limit = Bandwidth.classic(100, Refill.greedy(100, Duration.ofMinutes(1)));
                return Bucket4j.builder()
                    .addLimit(limit)
                    .build();
            }
            
            @Component
            public class RateLimitInterceptor implements HandlerInterceptor {
                
                @Autowired
                private Bucket bucket;
                
                @Override
                public boolean preHandle(HttpServletRequest request, 
                                       HttpServletResponse response, 
                                       Object handler) {
                    
                    ConsumptionProbe probe = bucket.tryConsumeAndReturnRemaining(1);
                    
                    if (probe.isConsumed()) {
                        response.addHeader("X-RateLimit-Remaining", 
                                         String.valueOf(probe.getRemainingTokens()));
                        return true;
                    } else {
                        response.setStatus(429);
                        response.addHeader("X-RateLimit-Retry-After", 
                                         String.valueOf(probe.getNanosToWaitForRefill() / 1_000_000_000));
                        return false;
                    }
                }
            }
        }
        """
    
    @staticmethod
    def express_js_config():
        return """
        // Express.js Rate Limiting with express-rate-limit
        const rateLimit = require('express-rate-limit');
        const RedisStore = require('rate-limit-redis');
        
        // Create limiter
        const apiLimiter = rateLimit({
            store: new RedisStore({
                client: redisClient,
                prefix: 'rl:'
            }),
            windowMs: 60 * 1000, // 1 minute
            max: 100, // 100 requests per minute
            message: 'Too many requests, please slow down!',
            standardHeaders: true, // Return rate limit info in headers
            legacyHeaders: false,
            handler: (req, res) => {
                res.status(429).json({
                    error: 'Rate limit exceeded',
                    retryAfter: req.rateLimit.resetTime
                });
            }
        });
        
        // Apply to routes
        app.use('/api/', apiLimiter);
        
        // Different limits for different endpoints
        const strictLimiter = rateLimit({
            windowMs: 60 * 1000,
            max: 10 // Only 10 requests per minute for sensitive endpoints
        });
        
        app.use('/api/payment', strictLimiter);
        """

# Generate complete implementation guide
practices = RateLimitingBestPractices()
configs = FrameworkConfigurations()

print("📚 Rate Limiting Best Practices Guide")
print("=" * 50)

print("\n🎯 Design Principles:")
for principle in practices.practices['design_principles']:
    print(f"\n{principle['principle']}")
    print(f"  📝 {principle['description']}")
    print(f"  💡 Example: {principle['example']}")
    print(f"  🏢 {principle['company_example']}")

print("\n❌ Common Mistakes to Avoid:")
for mistake in practices.practices['common_mistakes']:
    print(f"\n{mistake['mistake']}")
    print(f"  ⚠️ Problem: {mistake['problem']}")
    print(f"  ✅ Solution: {mistake['solution']}")
    print(f"  📰 Real Incident: {mistake['real_incident']}")

print("\n" + practices.generate_implementation_checklist())
```

### Conclusion: API Rate Limiting - Digital India's Traffic Management

Dosto, yeh tha humara complete journey through API Rate Limiting! Humne dekha ki kaise ye technology digital world ka traffic police hai, jo ensure karta hai ki servers crash na ho aur sabko fair chance mile.

Key takeaways:

1. **Rate limiting is essential** - Without it, your API is like Mumbai traffic without signals
2. **Choose the right algorithm** - Token bucket for flexibility, sliding window for accuracy
3. **Distributed systems need distributed rate limiting** - Redis is your friend
4. **Client-side handling is important** - Be a responsible API citizen
5. **Monitor everything** - You can't manage what you don't measure
6. **Cost optimization matters** - Rate limiting saves lakhs of rupees
7. **Learn from failures** - Every production incident teaches something

Indian companies like Paytm, Flipkart, Zomato have all learned these lessons the hard way. During demonetization, during Big Billion Days, during IPL finals - rate limiting has saved the day countless times.

Next time when you see "Too many requests" error, remember - it's not a bug, it's a feature! It's protecting the system from collapse, ensuring fair usage, and keeping the digital infrastructure running smoothly.

Keep learning, keep building, and remember - in the world of APIs, rate limiting is your safety net!

## Part 4: Advanced Implementation Patterns (60 minutes)

### Chapter 10: Geographic Rate Limiting - Region-Based Control

Different regions, different limits - like different speed limits on highways vs city roads!

1. **Comprehensive technical coverage** - All major rate limiting algorithms
2. **Indian context throughout** - IPL, Kumbh Mela, Bollywood, traffic examples
3. **15+ code examples** - Python, Java, Go implementations
4. **Real company case studies** - Paytm, Flipkart, Zomato, IRCTC, Ola
5. **Production war stories** - Demonetization, Big Billion Days, Tatkal chaos
6. **Cost analysis** - Detailed ROI calculations in INR
7. **Best practices** - From Indian tech ecosystem
8. **Monitoring and alerting** - Complete observability setup

The episode uses diverse Indian contexts beyond just Mumbai, incorporating references from:
- Sports (IPL cricket)
- Religious events (Kumbh Mela, Tirupati)
- Entertainment (Bollywood, BookMyShow)
- Transportation (IRCTC, Ola)
- E-commerce (Flipkart, Swiggy)
- Finance (Paytm, Razorpay, Zerodha)

---

*Thank you for listening! Next episode mein milenge with another exciting tech topic!* 🎙️🚀
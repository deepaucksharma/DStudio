#!/usr/bin/env python3
"""
Rate Limiter System Implementation - Episode 50: System Design Interview Mastery
UPI Transaction Rate Limiting System

Rate limiting जैसे Mumbai railway ticket counter का control है।
हर user को limited time में limited tickets ही मिल सकते हैं।

Author: Hindi Podcast Series
Topic: Rate Limiting Algorithms with Indian UPI Context
"""

import time
import threading
from collections import defaultdict, deque
from enum import Enum
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
import json
import redis
import hashlib

class RateLimitStrategy(Enum):
    """Rate limiting strategies - Traffic control ke different tarike"""
    TOKEN_BUCKET = "token_bucket"          # UPI transaction bucket
    SLIDING_WINDOW = "sliding_window"      # Time window based limiting
    FIXED_WINDOW = "fixed_window"          # Fixed time period limiting
    LEAKY_BUCKET = "leaky_bucket"         # Constant rate processing

@dataclass
class RateLimitConfig:
    """Rate limit configuration - UPI transaction rules"""
    max_requests: int                      # Maximum requests allowed
    window_size_seconds: int               # Time window in seconds
    burst_capacity: int = None             # Burst allowance
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    
    def __post_init__(self):
        if self.burst_capacity is None:
            self.burst_capacity = self.max_requests * 2

@dataclass
class RateLimitResult:
    """Rate limit check result"""
    allowed: bool
    remaining_requests: int = 0
    reset_time: float = 0.0
    retry_after: float = 0.0
    reason: str = ""

class TokenBucket:
    """Token Bucket Algorithm - UPI Transaction Token System"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket
        capacity: Maximum tokens (UPI daily limit - ₹1,00,000)
        refill_rate: Tokens per second (UPI refill rate - 10 per minute)
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()
        
        print(f"🪣 Token Bucket created - Capacity: {capacity}, Rate: {refill_rate}/sec")
    
    def consume(self, tokens_needed: int = 1) -> bool:
        """Consume tokens - UPI transaction attempt"""
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                print(f"✅ Token consumed - Remaining: {self.tokens}/{self.capacity}")
                return True
            else:
                print(f"🚫 Token bucket empty - Need: {tokens_needed}, Have: {self.tokens}")
                return False
    
    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        time_elapsed = now - self.last_refill
        tokens_to_add = time_elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_available_tokens(self) -> int:
        """Get current available tokens"""
        with self.lock:
            self._refill()
            return int(self.tokens)

class SlidingWindowCounter:
    """Sliding Window Rate Limiter - PhonePe transaction window"""
    
    def __init__(self, max_requests: int, window_size: int):
        """
        Initialize sliding window counter
        max_requests: Maximum requests in window (PhonePe daily limit)
        window_size: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests = deque()
        self.lock = threading.Lock()
        
        print(f"🪟 Sliding Window created - Max: {max_requests}/{window_size}s")
    
    def is_allowed(self, current_time: float = None) -> Tuple[bool, int]:
        """Check if request is allowed - PhonePe transaction check"""
        if current_time is None:
            current_time = time.time()
        
        with self.lock:
            # Remove expired requests
            window_start = current_time - self.window_size
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()
            
            # Check if we can accept new request
            if len(self.requests) < self.max_requests:
                self.requests.append(current_time)
                remaining = self.max_requests - len(self.requests)
                print(f"✅ Request allowed - Remaining: {remaining}")
                return True, remaining
            else:
                print(f"🚫 Rate limit exceeded - {len(self.requests)}/{self.max_requests}")
                return False, 0
    
    def get_request_count(self) -> int:
        """Get current request count in window"""
        with self.lock:
            current_time = time.time()
            window_start = current_time - self.window_size
            
            # Clean expired requests
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()
            
            return len(self.requests)

class UPIRateLimiter:
    """UPI Rate Limiter - Paytm/PhonePe/GPay Transaction Control"""
    
    def __init__(self, redis_client=None):
        """Initialize UPI rate limiter with different limits"""
        self.redis_client = redis_client
        self.local_limiters: Dict[str, Dict] = defaultdict(dict)
        self.lock = threading.Lock()
        
        # Indian UPI transaction limits (as per RBI guidelines)
        self.upi_limits = {
            'individual_per_transaction': 100000,    # ₹1,00,000 per transaction
            'individual_daily': 1000000,             # ₹10,00,000 per day
            'merchant_per_transaction': 5000000,     # ₹50,00,000 per transaction  
            'merchant_daily': 50000000,              # ₹5,00,00,000 per day
        }
        
        print("💳 UPI Rate Limiter initialized with RBI compliant limits")
        print(f"   Individual Daily Limit: ₹{self.upi_limits['individual_daily']:,}")
        print(f"   Merchant Daily Limit: ₹{self.upi_limits['merchant_daily']:,}")
    
    def check_upi_transaction_limit(self, 
                                  user_id: str, 
                                  amount: int, 
                                  user_type: str = 'individual') -> RateLimitResult:
        """Check UPI transaction limits - Paytm/PhonePe style"""
        
        # Get appropriate limits
        max_per_transaction = (self.upi_limits['individual_per_transaction'] 
                              if user_type == 'individual' 
                              else self.upi_limits['merchant_per_transaction'])
        
        max_daily = (self.upi_limits['individual_daily'] 
                    if user_type == 'individual' 
                    else self.upi_limits['merchant_daily'])
        
        # Check per transaction limit
        if amount > max_per_transaction:
            return RateLimitResult(
                allowed=False,
                reason=f"Transaction amount ₹{amount:,} exceeds limit ₹{max_per_transaction:,}"
            )
        
        # Check daily limit using sliding window
        daily_key = f"upi_daily_{user_type}_{user_id}"
        
        if self.redis_client:
            return self._check_redis_sliding_window(daily_key, amount, max_daily, 86400)
        else:
            return self._check_local_sliding_window(daily_key, amount, max_daily, 86400)
    
    def check_api_rate_limit(self, 
                           api_key: str, 
                           endpoint: str,
                           config: RateLimitConfig) -> RateLimitResult:
        """Check API rate limits - Razorpay/Instamojo style"""
        
        limiter_key = f"api_{api_key}_{endpoint}"
        
        if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return self._check_token_bucket(limiter_key, config)
        elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._check_sliding_window(limiter_key, config)
        elif config.strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._check_fixed_window(limiter_key, config)
    
    def _check_token_bucket(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Token bucket implementation"""
        if key not in self.local_limiters:
            refill_rate = config.max_requests / config.window_size_seconds
            self.local_limiters[key] = {
                'type': 'token_bucket',
                'bucket': TokenBucket(config.burst_capacity, refill_rate)
            }
        
        bucket = self.local_limiters[key]['bucket']
        allowed = bucket.consume(1)
        remaining = bucket.get_available_tokens()
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=remaining,
            reset_time=time.time() + config.window_size_seconds,
            retry_after=1.0 / (config.max_requests / config.window_size_seconds) if not allowed else 0,
            reason="Token bucket limit exceeded" if not allowed else "OK"
        )
    
    def _check_sliding_window(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Sliding window implementation"""
        if key not in self.local_limiters:
            self.local_limiters[key] = {
                'type': 'sliding_window',
                'counter': SlidingWindowCounter(config.max_requests, config.window_size_seconds)
            }
        
        counter = self.local_limiters[key]['counter']
        allowed, remaining = counter.is_allowed()
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=remaining,
            reset_time=time.time() + config.window_size_seconds,
            retry_after=config.window_size_seconds if not allowed else 0,
            reason="Sliding window limit exceeded" if not allowed else "OK"
        )
    
    def _check_fixed_window(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Fixed window implementation"""
        current_time = time.time()
        window_start = int(current_time // config.window_size_seconds)
        window_key = f"{key}_{window_start}"
        
        if window_key not in self.local_limiters:
            self.local_limiters[window_key] = {
                'type': 'fixed_window',
                'count': 0,
                'window_start': window_start
            }
        
        limiter_data = self.local_limiters[window_key]
        
        if limiter_data['count'] >= config.max_requests:
            next_window = (window_start + 1) * config.window_size_seconds
            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_time=next_window,
                retry_after=next_window - current_time,
                reason="Fixed window limit exceeded"
            )
        
        limiter_data['count'] += 1
        remaining = config.max_requests - limiter_data['count']
        
        return RateLimitResult(
            allowed=True,
            remaining_requests=remaining,
            reset_time=(window_start + 1) * config.window_size_seconds,
            reason="OK"
        )
    
    def _check_local_sliding_window(self, key: str, amount: int, max_daily: int, window_size: int) -> RateLimitResult:
        """Local sliding window for UPI amounts"""
        if key not in self.local_limiters:
            self.local_limiters[key] = {
                'type': 'upi_sliding_window',
                'transactions': deque(),
                'total_amount': 0
            }
        
        limiter_data = self.local_limiters[key]
        current_time = time.time()
        window_start = current_time - window_size
        
        # Remove expired transactions
        while (limiter_data['transactions'] and 
               limiter_data['transactions'][0]['time'] < window_start):
            expired = limiter_data['transactions'].popleft()
            limiter_data['total_amount'] -= expired['amount']
        
        # Check if adding this amount would exceed limit
        if limiter_data['total_amount'] + amount > max_daily:
            return RateLimitResult(
                allowed=False,
                remaining_requests=max_daily - limiter_data['total_amount'],
                reset_time=current_time + window_size,
                retry_after=window_size,
                reason=f"Daily UPI limit exceeded. Current: ₹{limiter_data['total_amount']:,}, Attempting: ₹{amount:,}, Limit: ₹{max_daily:,}"
            )
        
        # Add transaction
        limiter_data['transactions'].append({
            'time': current_time,
            'amount': amount
        })
        limiter_data['total_amount'] += amount
        
        return RateLimitResult(
            allowed=True,
            remaining_requests=max_daily - limiter_data['total_amount'],
            reset_time=current_time + window_size,
            reason="UPI transaction approved"
        )
    
    def _check_redis_sliding_window(self, key: str, amount: int, max_daily: int, window_size: int) -> RateLimitResult:
        """Redis-based sliding window (for distributed systems)"""
        current_time = time.time()
        window_start = current_time - window_size
        
        pipe = self.redis_client.pipeline()
        
        # Remove expired entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Get current total
        pipe.zrange(key, 0, -1, withscores=True)
        
        results = pipe.execute()
        current_transactions = results[1]
        current_total = sum(float(score) for _, score in current_transactions)
        
        if current_total + amount > max_daily:
            return RateLimitResult(
                allowed=False,
                remaining_requests=max_daily - current_total,
                reason=f"Redis UPI limit exceeded"
            )
        
        # Add new transaction
        self.redis_client.zadd(key, {str(current_time): amount})
        self.redis_client.expire(key, window_size)
        
        return RateLimitResult(
            allowed=True,
            remaining_requests=max_daily - current_total - amount,
            reason="Redis UPI transaction approved"
        )
    
    def get_limiter_stats(self) -> Dict:
        """Get rate limiter statistics"""
        stats = {
            'total_limiters': len(self.local_limiters),
            'limiter_types': defaultdict(int),
            'active_limiters': []
        }
        
        for key, limiter in self.local_limiters.items():
            limiter_type = limiter['type']
            stats['limiter_types'][limiter_type] += 1
            
            if limiter_type == 'upi_sliding_window':
                stats['active_limiters'].append({
                    'key': key,
                    'type': limiter_type,
                    'active_transactions': len(limiter['transactions']),
                    'current_amount': limiter['total_amount']
                })
        
        return stats

def demonstrate_upi_rate_limiting():
    """Demonstrate UPI Rate Limiting - PhonePe/Paytm style"""
    print("💳 UPI Rate Limiting Demo - PhonePe Style Transaction Control")
    print("=" * 70)
    
    # Initialize rate limiter
    rate_limiter = UPIRateLimiter()
    
    # Test individual user transactions
    user_id = "user_9876543210"  # Indian mobile number
    
    print(f"\n👤 Testing Individual User: {user_id}")
    print("-" * 50)
    
    # Test various transaction amounts
    test_transactions = [
        50000,    # ₹50,000 - Normal transaction
        150000,   # ₹1,50,000 - Above per-transaction limit
        75000,    # ₹75,000 - Normal transaction
        80000,    # ₹80,000 - Normal transaction
        90000,    # ₹90,000 - Should exceed daily limit
    ]
    
    daily_total = 0
    for i, amount in enumerate(test_transactions, 1):
        print(f"\n💰 Transaction {i}: ₹{amount:,}")
        
        result = rate_limiter.check_upi_transaction_limit(
            user_id=user_id,
            amount=amount,
            user_type='individual'
        )
        
        if result.allowed:
            daily_total += amount
            print(f"✅ Transaction approved")
            print(f"   Daily total: ₹{daily_total:,}")
            print(f"   Remaining limit: ₹{result.remaining_requests:,}")
        else:
            print(f"🚫 Transaction denied")
            print(f"   Reason: {result.reason}")
            if result.retry_after > 0:
                print(f"   Retry after: {result.retry_after:.0f} seconds")
    
    print(f"\n📊 Final Daily Total: ₹{daily_total:,}")

def demonstrate_api_rate_limiting():
    """Demonstrate API Rate Limiting - Razorpay style"""
    print("\n🔑 API Rate Limiting Demo - Razorpay Style API Control")
    print("=" * 70)
    
    rate_limiter = UPIRateLimiter()
    
    # Different API endpoints with different limits
    api_configs = {
        'payment_create': RateLimitConfig(
            max_requests=100,
            window_size_seconds=3600,  # 100 requests per hour
            strategy=RateLimitStrategy.TOKEN_BUCKET
        ),
        'payment_status': RateLimitConfig(
            max_requests=1000,
            window_size_seconds=3600,  # 1000 requests per hour
            strategy=RateLimitStrategy.SLIDING_WINDOW
        ),
        'webhook_verify': RateLimitConfig(
            max_requests=500,
            window_size_seconds=60,    # 500 requests per minute
            strategy=RateLimitStrategy.FIXED_WINDOW
        )
    }
    
    api_key = "rzp_test_1234567890"
    
    print(f"\n🔐 Testing API Key: {api_key}")
    
    for endpoint, config in api_configs.items():
        print(f"\n📡 Endpoint: {endpoint}")
        print(f"   Strategy: {config.strategy.value}")
        print(f"   Limit: {config.max_requests}/{config.window_size_seconds}s")
        
        # Test rapid requests
        for i in range(5):
            result = rate_limiter.check_api_rate_limit(
                api_key=api_key,
                endpoint=endpoint,
                config=config
            )
            
            print(f"   Request {i+1}: {'✅ Allowed' if result.allowed else '🚫 Denied'}"
                  f" (Remaining: {result.remaining_requests})")
            
            if not result.allowed:
                print(f"      Reason: {result.reason}")
                break
            
            time.sleep(0.1)  # Small delay between requests

def demonstrate_burst_handling():
    """Demonstrate burst traffic handling"""
    print("\n🚀 Burst Traffic Handling Demo - Flipkart Big Billion Day")
    print("=" * 70)
    
    # High-capacity token bucket for flash sales
    flash_sale_config = RateLimitConfig(
        max_requests=1000,      # Base rate: 1000 req/min
        window_size_seconds=60,
        burst_capacity=5000,    # Burst capacity: 5000 requests
        strategy=RateLimitStrategy.TOKEN_BUCKET
    )
    
    rate_limiter = UPIRateLimiter()
    
    api_key = "flipkart_flash_sale_api"
    
    print(f"⚡ Simulating flash sale traffic burst...")
    print(f"   Base rate: {flash_sale_config.max_requests}/min")
    print(f"   Burst capacity: {flash_sale_config.burst_capacity}")
    
    # Simulate burst of requests
    burst_requests = 100
    allowed_count = 0
    denied_count = 0
    
    for i in range(burst_requests):
        result = rate_limiter.check_api_rate_limit(
            api_key=api_key,
            endpoint="product_purchase",
            config=flash_sale_config
        )
        
        if result.allowed:
            allowed_count += 1
        else:
            denied_count += 1
        
        if i % 20 == 0:  # Show progress every 20 requests
            print(f"   Progress: {i+1}/{burst_requests} - "
                  f"Allowed: {allowed_count}, Denied: {denied_count}")
    
    print(f"\n📈 Burst Test Results:")
    print(f"   Total Requests: {burst_requests}")
    print(f"   Allowed: {allowed_count} ({allowed_count/burst_requests*100:.1f}%)")
    print(f"   Denied: {denied_count} ({denied_count/burst_requests*100:.1f}%)")

if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_upi_rate_limiting()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_api_rate_limiting()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_burst_handling()
    
    print(f"\n✅ Rate Limiter Demo Complete!")
    print(f"📚 Key Concepts Demonstrated:")
    print(f"   • Token Bucket - Burst handling with refill rate")
    print(f"   • Sliding Window - Precise request counting") 
    print(f"   • Fixed Window - Simple time-based limiting")
    print(f"   • UPI Limits - RBI compliant transaction limits")
    print(f"   • API Rate Limiting - Service protection")
    print(f"   • Burst Traffic - Flash sale scenario handling")
    print(f"   • Indian Context - UPI, Paytm, PhonePe, Razorpay examples")
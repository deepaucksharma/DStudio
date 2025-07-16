Page 59: Retry & Backoff
If at first you don't succeed, wait exponentially longer
THE PROBLEM
Transient failures happen:
- Network blips
- Service deploys
- Database failovers
- Rate limits

But naive retries make things worse!
THE SOLUTION
Smart retry strategies:
1. Exponential backoff
2. Jitter to prevent thundering herd
3. Circuit breaker integration
4. Idempotency keys
PSEUDO CODE IMPLEMENTATION
RetryHandler:
    execute_with_retry(operation, config):
        last_exception = null
        
        for attempt in range(config.max_attempts):
            try:
                return operation()
                
            catch exception as e:
                last_exception = e
                
                if not is_retryable(e):
                    raise e
                    
                if attempt < config.max_attempts - 1:
                    delay = calculate_delay(attempt, config)
                    sleep(delay)
                    
        raise RetriesExhaustedException(last_exception)
        
    calculate_delay(attempt, config):
        // Exponential backoff
        base_delay = config.base_delay * (2 ** attempt)
        
        // Add jitter
        jitter = random(0, base_delay * config.jitter_factor)
        
        // Cap at max
        total_delay = min(base_delay + jitter, config.max_delay)
        
        return total_delay
        
    is_retryable(exception):
        // Don't retry client errors
        if exception.status_code in [400, 401, 403, 404]:
            return false
            
        // Retry server errors
        if exception.status_code >= 500:
            return true
            
        // Retry specific exceptions
        retryable_types = [
            NetworkTimeout,
            ConnectionRefused,
            ServiceUnavailable
        ]
        
        return type(exception) in retryable_types

AdaptiveRetry:
    // Adjust retry based on success rate
    
    success_rate = calculate_success_rate()
    
    if success_rate < 0.1:  // 90% failing
        // Back off aggressively
        config.base_delay *= 2
        config.max_attempts = 2
        
    elif success_rate > 0.9:  // 90% succeeding
        // Can be more aggressive
        config.base_delay = original_base_delay
        config.max_attempts = original_max_attempts

IdempotentRetry:
    execute_with_idempotency(operation, idempotency_key):
        // Check if already executed
        result = check_idempotency_store(idempotency_key)
        if result:
            return result
            
        // Execute with retry
        result = execute_with_retry(operation)
        
        // Store result
        store_idempotency_result(idempotency_key, result)
        
        return result
Retry Strategies Comparison:
Strategy         Delay Pattern         Use Case
--------         -------------         --------
Fixed            1s, 1s, 1s           Simple/testing
Linear           1s, 2s, 3s           Predictable load
Exponential      1s, 2s, 4s, 8s       Reduce load on failure
Fibonacci        1s, 1s, 2s, 3s, 5s   Compromise
Custom           Based on error        Smart retry
✓ CHOOSE THIS WHEN:

Network calls involved
Transient failures expected
Operations are idempotent
Service has recovery time
Rate limits exist

⚠️ BEWARE OF:

Retry storms/amplification
Non-idempotent operations
Timeout multiplication
Resource exhaustion
Missing metrics

REAL EXAMPLES

AWS SDK: Built-in exponential backoff
Google: Client libraries with retry
Stripe: Idempotency keys for payments

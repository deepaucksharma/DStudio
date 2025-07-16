Page 58: Circuit Breaker
Fail fast, recover faster
THE PROBLEM
Cascading failures:
Service A → Service B (slow) → Timeout → Retry → More load → Slower → Death
         ↓
    Threads blocked
         ↓
    A dies too
THE SOLUTION
Circuit breaker states:
CLOSED → OPEN → HALF_OPEN → CLOSED
(normal) (failing) (testing) (recovered)

Stop calling failing services!
PSEUDO CODE IMPLEMENTATION
CircuitBreaker:
    state = CLOSED
    failure_count = 0
    success_count = 0
    last_failure_time = null
    
    call(function):
        if state == OPEN:
            if should_attempt_reset():
                state = HALF_OPEN
            else:
                raise CircuitOpenException()
                
        try:
            result = function()
            on_success()
            return result
        catch exception:
            on_failure()
            raise exception
            
    on_success():
        failure_count = 0
        if state == HALF_OPEN:
            success_count++
            if success_count >= success_threshold:
                state = CLOSED
                
    on_failure():
        failure_count++
        last_failure_time = now()
        
        if state == HALF_OPEN:
            state = OPEN
        elif failure_count >= failure_threshold:
            state = OPEN
            
    should_attempt_reset():
        return now() - last_failure_time >= reset_timeout

AdvancedCircuitBreaker:
    // Per-endpoint configuration
    configs = {
        '/api/payment': {threshold: 5, timeout: 60s},
        '/api/search': {threshold: 10, timeout: 30s},
        '/api/recommendation': {threshold: 20, timeout: 10s}
    }
    
    // Failure rate based
    calculate_failure_rate(window):
        recent_calls = get_calls_in_window(window)
        failure_rate = count_failures(recent_calls) / len(recent_calls)
        
        if failure_rate > 0.5:  // 50% failing
            open_circuit()
            
    // Gradual recovery
    half_open_strategy():
        // Let through increasing percentage
        allow_percentage = min(
            100,
            10 * minutes_since_opened
        )
        
        if random() < allow_percentage / 100:
            return allow_request()
        else:
            return reject_request()
Circuit Breaker Patterns:
1. TIMEOUT CIRCUIT BREAKER
   if response_time > threshold:
       count_as_failure()

2. ERROR RATE CIRCUIT BREAKER
   if error_rate > 50%:
       open_circuit()

3. CONSECUTIVE FAILURES
   if consecutive_failures > 5:
       open_circuit()

4. RESOURCE BASED
   if thread_pool_exhausted():
       open_circuit()
✓ CHOOSE THIS WHEN:

Calling external services
Cascading failure risk
Need fast failure
Resource protection important
Dependencies unreliable

⚠️ BEWARE OF:

Setting thresholds wrong
Not testing half-open
Missing circuit breaker metrics
Too aggressive (unnecessary failures)
Shared circuit breaker state

REAL EXAMPLES

Netflix: Hystrix (now Resilience4j)
Amazon: Service mesh circuit breaking
Spotify: Per-service circuit breakers

---
title: Progressive Disclosure Examples
description: Demonstrating collapsible content and progressive information reveal
tags:
  - ui-pattern
  - documentation
  - examples
---

# Progressive Disclosure Examples

Progressive disclosure helps manage information complexity by revealing details only when users need them.

## Basic Collapsible Sections

??? note "What is Progressive Disclosure?"
    Progressive disclosure is a design pattern that:
    
    - Reduces cognitive load by hiding complexity
    - Allows users to focus on primary tasks
    - Provides detailed information on demand
    - Improves page scannability
    
    This pattern is especially useful for technical documentation where different users need different levels of detail.

??? example "Simple Code Example"
    ```python
    def calculate_availability(uptime_minutes, total_minutes):
        """Calculate system availability percentage"""
        availability = (uptime_minutes / total_minutes) * 100
        return round(availability, 4)
    ```
    
    This function calculates the availability percentage of a system based on uptime.

## Nested Progressive Disclosure

??? info "Distributed Systems Concepts"
    Understanding distributed systems requires knowledge of several key areas:
    
    ??? abstract "CAP Theorem"
        The CAP theorem states that a distributed system can only guarantee two of:
        
        - **Consistency**: All nodes see the same data
        - **Availability**: System remains operational
        - **Partition Tolerance**: System continues despite network failures
        
        ??? tip "Real-World Trade-offs"
            - **CP Systems**: MongoDB, HBase, Redis
            - **AP Systems**: Cassandra, DynamoDB, CouchDB
            - **CA Systems**: Traditional RDBMS (not truly distributed)

    ??? abstract "Consensus Algorithms"
        Consensus algorithms ensure distributed systems agree on shared state:
        
        - **Raft**: Understandable consensus algorithm
        - **Paxos**: Complex but proven consensus protocol
        - **PBFT**: Byzantine fault tolerant consensus

## State-Aware Collapsibles

???+ warning "Performance Considerations"
    This section contains important performance information that's expanded by default using `???+`.
    
    Key metrics to monitor:
    - Response time (P50, P95, P99)
    - Error rate
    - Throughput
    - Resource utilization

??? success "Best Practices" 
    Follow these guidelines for optimal results:
    
    1. **Monitor First**: Establish baselines before optimization
    2. **Measure Impact**: Quantify improvements
    3. **Iterate**: Small, incremental changes
    4. **Document**: Record what worked and what didn't

## Complex Information Architecture

??? question "How do Circuit Breakers Work?"
    
    Circuit breakers protect distributed systems from cascading failures.
    
    ??? info "State Machine"
        Circuit breakers have three states:
        
        === "Closed"
            - Normal operation
            - All requests pass through
            - Monitors for failures
            
        === "Open"
            - Circuit has tripped
            - Requests fail immediately
            - No load on failing service
            
        === "Half-Open"
            - Testing recovery
            - Limited requests allowed
            - Determines next state
    
    ??? example "Implementation Example"
        ```python
        class CircuitBreaker:
            def __init__(self, failure_threshold=5, recovery_timeout=60):
                self.failure_threshold = failure_threshold
                self.recovery_timeout = recovery_timeout
                self.failure_count = 0
                self.last_failure_time = None
                self.state = 'CLOSED'
        ```
    
    ??? tip "Configuration Guidelines"
        | Parameter | Recommended Value | Notes |
        |-----------|------------------|--------|
        | Failure Threshold | 5-10 requests | Lower for critical services |
        | Recovery Timeout | 30-60 seconds | Higher for external services |
        | Success Threshold | 2-3 requests | For half-open state |

## Interactive Learning Paths

??? abstract "Choose Your Learning Path"
    
    Select the path that matches your experience level:
    
    ??? note "Beginner Path"
        Start with fundamental concepts:
        
        1. **Week 1-2**: Basic networking and protocols
        2. **Week 3-4**: Introduction to distributed systems
        3. **Week 5-6**: Common patterns and anti-patterns
        4. **Week 7-8**: Simple case studies
        
        ??? tip "Resources"
            - [Getting Started Guide](/introduction/getting-started)
            - [Glossary](/reference/glossary)
            - [Basic Patterns](/patterns/#beginner)
    
    ??? info "Intermediate Path" 
        Build on existing knowledge:
        
        1. **Week 1-2**: Advanced patterns (CQRS, Event Sourcing)
        2. **Week 3-4**: Consistency models and trade-offs
        3. **Week 5-6**: Performance optimization
        4. **Week 7-8**: Real-world case studies
        
        ??? tip "Resources"
            - [Advanced Patterns](/patterns/#intermediate)
            - [Quantitative Analysis](/quantitative)
            - [Case Studies](/case-studies)
    
    ??? warning "Expert Path"
        Deep dive into complex topics:
        
        1. **Week 1-2**: Formal verification and proofs
        2. **Week 3-4**: Novel consensus algorithms
        3. **Week 5-6**: Large-scale system design
        4. **Week 7-8**: Research papers and cutting edge
        
        ??? tip "Resources"
            - [Research Papers](/reference/)
            - [Advanced Mathematics](/quantitative/advanced)
            - [System Design](/case-studies/#expert)

## Styled Progressive Disclosure

??? axiom "Fundamental Law: Correlated Failure"
    !!! quote "Murphy's Law for Distributed Systems"
        "Components that can fail together, will fail together."
    
    This law derives from physical constraints:
    
    - Shared power sources create correlated electrical failures
    - Shared network switches create correlated connectivity failures  
    - Shared data centers create correlated availability failures
    
    ??? math "Mathematical Foundation"
        Given failure probability $p$ for a single component:
        
        - Independent failures: $P(all\_fail) = p^n$
        - Correlated failures: $P(all\_fail) = p$
        
        The difference grows exponentially with $n$.

??? pillar "Distribution Pillar: State Distribution"
    !!! abstract "Core Principle"
        Distributing state across multiple nodes improves availability but complicates consistency.
    
    ??? details "Implementation Strategies"
        
        === "Replication"
            - **Primary-Backup**: Simple but limited scalability
            - **Multi-Primary**: Complex but highly available
            - **Chain Replication**: Ordered consistency guarantees
        
        === "Partitioning"
            - **Range Partitioning**: Good for ordered access
            - **Hash Partitioning**: Even distribution
            - **Composite Keys**: Multi-dimensional partitioning
        
        === "Hybrid"
            - Combine replication and partitioning
            - Example: Cassandra, DynamoDB
            - Best of both worlds with added complexity

## Best Practices for Progressive Disclosure

!!! tip "Guidelines"
    
    1. **Start with Overview**: Present the most important information first
    2. **Use Clear Labels**: Make it obvious what information is hidden
    3. **Logical Grouping**: Related information should be disclosed together
    4. **Remember State**: Use `???+` for sections that should default to open
    5. **Avoid Over-Nesting**: Maximum 3 levels of nesting
    6. **Mobile Friendly**: Test collapsibles on small screens

## Accessibility Considerations

??? important "Accessibility Requirements"
    
    Ensure progressive disclosure is accessible:
    
    - ✅ Keyboard navigable (Enter/Space to toggle)
    - ✅ Screen reader compatible
    - ✅ Clear focus indicators
    - ✅ Semantic HTML structure
    - ✅ ARIA labels where needed
    
    ??? example "Testing Checklist"
        - [ ] Tab through all collapsibles
        - [ ] Test with screen reader
        - [ ] Verify focus indicators are visible
        - [ ] Check contrast ratios
        - [ ] Test with keyboard only
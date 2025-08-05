---
category: communication
current_relevance: mainstream
description: Decoupled messaging pattern where publishers send messages to topics
  and subscribers receive messages based on their interests
difficulty: intermediate
essential_question: How do we enable efficient communication between services using
  publish-subscribe pattern?
excellence_tier: gold
introduced: 1987-01
last-updated: 2025-07-26
modern-examples:
- company: Apache Kafka
  implementation: Distributed pub-sub for event streaming at LinkedIn, Uber, Netflix
  scale: 7 trillion messages/day at LinkedIn
- company: Redis
  implementation: In-memory pub-sub for real-time features
  scale: Millions of messages/sec with microsecond latency
- company: Google Cloud Pub/Sub
  implementation: Globally distributed message service
  scale: 500M messages/second, 99.95% SLA
pattern_status: recommended
prerequisites:
- message-queues
- event-driven
- distributed-systems
production-checklist:
- Choose delivery semantics (at-least-once, at-most-once, exactly-once)
- Configure topic partitioning for scalability
- Implement message ordering guarantees where needed
- Set up dead letter queues for failed messages
- Configure retention policies (hours to days)
- Monitor consumer lag and backpressure
- Implement idempotent consumers
- Set up topic-based access control
- Plan for message schema evolution
- Test fan-out performance under load
reading-time: 35 min
status: initial
tagline: Master publish-subscribe pattern for distributed systems success
title: Publish-Subscribe Pattern
type: pattern
when-not-to-use: Point-to-point communication, request-response patterns, transactional
  consistency requirements
when-to-use: Event-driven architectures, real-time notifications, decoupled microservices,
  multi-consumer scenarios
---


# Publish-Subscribe Pattern

!!! success "🏆 Gold Standard Pattern"
    **Decoupled Event Distribution** • Kafka, Redis, Google Pub/Sub proven
    
    The cornerstone of event-driven architectures. Pub-sub enables scalable, decoupled communication where publishers and subscribers operate independently, supporting everything from real-time notifications to event streaming.
    
    **Key Success Metrics:**
    - LinkedIn Kafka: 7 trillion messages/day powering all services
    - Redis Pub/Sub: Microsecond latency for real-time features
    - Google Pub/Sub: 500M messages/sec with global distribution

## Essential Questions This Pattern Answers

!!! question "Critical Decision Points"
    **Process Steps:**
- Initialize system
- Process requests
- Handle responses
- Manage failures

## Decision Matrix

| Factor | Score (1-5) | Reasoning |
|--------|-------------|-----------|
| **Complexity** | 3 | Message broker setup, topic management, but well-understood patterns |
| **Performance Impact** | 4 | Excellent throughput (millions/sec), async processing, minimal request latency |
| **Operational Overhead** | 4 | Broker management, monitoring consumer lag, message retention, dead letter queues |
| **Team Expertise Required** | 3 | Understanding of messaging concepts, delivery semantics, and event-driven architecture |
| **Scalability** | 5 | Outstanding - horizontal scaling, partitioning, fan-out to multiple consumers |

**Overall Recommendation: ✅ HIGHLY RECOMMENDED** - Essential for event-driven architectures and microservices communication.


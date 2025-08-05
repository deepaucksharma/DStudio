---
category: communication
current_relevance: mainstream
description: Unified entry point for microservices providing routing, authentication,
  and cross-cutting concerns
difficulty: intermediate
essential_question: How do we unify microservice access while handling auth, routing,
  and protocols?
excellence_tier: gold
introduced: 2011-10
modern_examples:
- company: Netflix
  implementation: Zuul gateway handles 50B+ requests daily across edge devices
  scale: 50B+ API requests/day, 130M+ subscribers
- company: Amazon
  implementation: AWS API Gateway manages APIs for Prime Video, Alexa, and retail
  scale: Trillions of API calls annually
- company: Uber
  implementation: Edge gateway routes requests across 3000+ microservices
  scale: 18M+ trips daily across 10,000+ cities
pattern_status: recommended
prerequisites:
- microservices-architecture
- http-protocols
- authentication
production_checklist:
- Implement request/response logging with correlation IDs
- Configure rate limiting per client (typical 1000 req/min)
- Enable circuit breakers for backend services (50% error threshold)
- Set up authentication/authorization (OAuth2/JWT)
- Configure caching for frequently accessed data (TTL 5-60s)
- Implement request/response transformation as needed
- Monitor latency percentiles (p50, p95, p99)
- Configure timeouts for each backend service (typically 5-30s)
- Set up health checks for all backend services
- Implement gradual rollout for configuration changes
reading_time: 20 min
related_laws:
- law4-tradeoffs
- law6-human-api
- law7-economics
related_pillars:
- control
- work
tagline: Single entry point for all your microservices - routing, auth, and more
title: API Gateway Pattern
type: pattern
---


# API Gateway Pattern

!!! success "🏆 Gold Standard Pattern"
    **Single Entry Point for Microservices** • Netflix, Amazon, Uber proven at 50B+ scale
    
    Simplifies client interactions by providing unified access to microservices with centralized authentication, routing, and protocol translation. The de facto standard for external API management.
    
    **Key Success Metrics:**
    - Netflix: 50B+ requests/day with 99.99% availability
    - Amazon: Trillions of API calls with sub-100ms p95 latency
    - Uber: 18M+ trips/day across 3000+ microservices

## Essential Question

**How do we unify microservice access while handling auth, routing, and protocols?**

## When to Use / When NOT to Use

### ✅ Use When

| Scenario | Example | Impact |
|----------|---------|--------|
| Multiple microservices | 10+ services requiring unified access | Reduces client complexity by 90% |
| Multiple client types | Mobile, web, IoT with different needs | Custom APIs per client type |
| Cross-cutting concerns | Auth, logging, rate limiting | Centralized policy enforcement |
| Protocol translation | REST to gRPC, HTTP to WebSocket | Single interface regardless of backend |

### ❌ DON'T Use When

| Scenario | Why | Alternative |
|----------|-----|-------------|
| < 5 services | Overkill complexity | Direct service communication |
| Ultra-low latency needs | Extra hop adds 5-10ms | [Service Mesh](service-mesh.md) sidecar |
| Internal services only | Wrong abstraction level | Service mesh for service-to-service |
| Simple proxying | Too heavyweight | nginx/HAProxy |

### The Story

Imagine a luxury hotel concierge desk. Guests don't navigate the hotel's complexity—finding housekeeping, room service, concierge services, spa booking. They simply approach one desk (the concierge) who handles routing, authentication ("Are you a guest?"), and coordination with all hotel services.

### Core Insight

> **Key Takeaway:** API Gateway transforms N×M client-service connections into N×1 client-gateway connections, centralizing cross-cutting concerns while maintaining service independence.

### In One Sentence

API Gateway **unifies microservice access** by **routing requests and handling cross-cutting concerns** to achieve **simplified client integration and centralized policy enforcement**.

### The Problem Space

<div class="failure-vignette">
<h4>🚨 What Happens Without This Pattern</h4>

**E-commerce Mobile App, 2019**: Mobile client called 47 different microservices directly. Each service had different auth mechanisms, API versions, and response formats. App load time: 15 seconds with 47 network connections.

**Impact**: App store rating dropped from 4.5 to 2.1 stars, 35% drop in mobile bookings ($180M revenue loss)
</div>

#### Key Components

| Component | Purpose | Responsibility |
|-----------|---------|----------------|
| Request Router | Service selection | Path-based routing, load balancing |
| Authentication | Identity verification | JWT validation, API key management |
| Rate Limiter | Traffic control | Per-client request limiting |
| Circuit Breaker | Fault tolerance | Prevent cascading failures |

### Basic Example

**Process Overview:** See production implementations for details


<details>
<summary>📄 View implementation code</summary>

from typing import Dict, Optional
import asyncio
import time

class APIGateway:
    def __init__(self):
        self.routes = {}  # path_pattern -> service mapping
        self.plugins = []  # middleware plugins
        self.cache = {}   # response cache
        
    def add_route(self, path_pattern: str, service_url: str):
        """Register a route mapping"""
        self.routes[path_pattern] = service_url
        
    def add_plugin(self, plugin):
        """Add middleware plugin"""
        self.plugins.append(plugin)
        
    async def handle_request(self, request):
        """Main request processing pipeline"""
        
        # **Process Steps:**
- Initialize system
- Process requests
- Handle responses
- Manage failures

</details>

## Decision Matrix

| Factor | Score (1-5) | Reasoning |
|--------|-------------|-----------|
| **Complexity** | 4 | Requires handling routing, auth, rate limiting, monitoring, and service discovery |
| **Performance Impact** | 3 | Adds network hop (~5-10ms), but enables caching and request optimization |
| **Operational Overhead** | 4 | High availability requirements, monitoring, configuration management, scaling |
| **Team Expertise Required** | 3 | Understanding of HTTP protocols, auth mechanisms, routing, and microservices |
| **Scalability** | 5 | Essential for microservices architecture, handles traffic aggregation and scaling |

**Overall Recommendation: ✅ HIGHLY RECOMMENDED** - Critical for microservices architectures with multiple client types and services.

## Real-World Examples

### Netflix Zuul
- **Scale**: 50B+ requests/day
- **Key Features**: Dynamic routing, circuit breakers, load balancing
- **Lessons**: Started with Zuul 1, migrated to Zuul 2 for reactive patterns

### Amazon API Gateway  
- **Scale**: Trillions of API calls annually
- **Key Features**: Serverless integration, automatic scaling, per-request pricing
- **Lessons**: Managed service approach reduces operational overhead

### Uber Edge Gateway
- **Scale**: 18M+ trips/day across 3000+ microservices
- **Key Features**: Custom protocol handling, advanced routing, traffic shaping
- **Lessons**: Built custom solution for specific performance requirements


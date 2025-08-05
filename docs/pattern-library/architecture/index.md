# Architecture Patterns

Patterns for system structure, deployment, and organization.

## Overview

Architecture patterns define the high-level structure of distributed systems. They provide blueprints for organizing services, managing dependencies, and enabling system evolution. These patterns address:

- **Service Organization** - How to structure services
- **Communication** - How services interact
- **Deployment** - How to package and deploy
- **Evolution** - How to change safely

## Pattern Categories

### Service Architecture
- **Microservices** - Fine-grained services
- **Service-Oriented Architecture** - Coarse-grained services
- **[Serverless/FaaS](serverless-faas.md)** - Function-based architecture
- **[Shared Nothing](shared-nothing.md)** - Isolated service architecture
- **[Cell-Based Architecture](cell-based.md)** - Fault-isolated cells
- **[Event-Driven Architecture](architecture/event-driven.md)** - Event-based communication
- **Modular Monolith** - Well-structured monolith

### Integration Patterns
- **API Gateway** - Unified entry point
- **[Backends for Frontends](backends-for-frontends.md)** - Client-specific APIs
- **Service Mesh** - Service communication layer
- **[Anti-Corruption Layer](anti-corruption-layer.md)** - Legacy integration
- **Enterprise Service Bus** - Message-based integration

### Deployment Patterns
- **[Sidecar](architecture/sidecar.md)** - Auxiliary service container
- **[Ambassador](ambassador.md)** - Proxy for external services
- **Adapter** - Interface standardization

### Evolutionary Patterns
- **[Strangler Fig](strangler-fig.md)** - Gradual replacement
- **[Choreography](choreography.md)** - Decentralized coordination
- **Branch by Abstraction** - Parallel development
- **Feature Toggles** - Runtime configuration
- **Blue-Green Deployment** - Zero-downtime updates

## Quick Decision Guide

| Requirement | Pattern |
|-------------|---------|
| Service autonomy | Microservices |
| Unified API | API Gateway |
| Service communication | Service Mesh |
| Legacy migration | Strangler Fig |
| A/B testing | Feature Toggles |
| Zero downtime | Blue-Green Deployment |

## Architecture Principles

1. **Loose Coupling** - Minimize dependencies
2. **High Cohesion** - Related functionality together
3. **Service Autonomy** - Independent deployment
4. **Technology Diversity** - Right tool for the job
5. **Evolutionary Design** - Enable change

---

*Browse individual patterns below or return to the [Pattern Library](../).*
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
- **[Serverless/FaaS](/pattern-library/architecture/serverless-faas/)** - Function-based architecture
- **[Shared Nothing](/pattern-library/architecture/shared-nothing/)** - Isolated service architecture
- **[Cell-Based Architecture](/pattern-library/architecture/cell-based/)** - Fault-isolated cells
- **[Event-Driven Architecture](/pattern-library/architecture/event-driven/)** - Event-based communication
- **Modular Monolith** - Well-structured monolith

### Integration Patterns
- **API Gateway** - Unified entry point
- **[Backends for Frontends](/pattern-library/architecture/backends-for-frontends/)** - Client-specific APIs
- **Service Mesh** - Service communication layer
- **[Anti-Corruption Layer](/pattern-library/architecture/anti-corruption-layer/)** - Legacy integration
- **Enterprise Service Bus** - Message-based integration

### Deployment Patterns
- **[Sidecar](/pattern-library/architecture/sidecar/)** - Auxiliary service container
- **[Ambassador](/pattern-library/architecture/ambassador/)** - Proxy for external services
- **Adapter** - Interface standardization

### Evolutionary Patterns
- **[Strangler Fig](/pattern-library/architecture/strangler-fig/)** - Gradual replacement
- **[Choreography](/pattern-library/architecture/choreography/)** - Decentralized coordination
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
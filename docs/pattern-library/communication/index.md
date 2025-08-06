---
type: pattern
category: communication
title: Index
description: 'TODO: Add description'
---

# Communication Patterns

Patterns for messaging, RPC, event streaming, and inter-service communication.

## Overview

Communication patterns address the fundamental challenge of how services talk to each other in a distributed system. These patterns handle concerns like:

- **Reliability** - Ensuring messages are delivered
- **Ordering** - Maintaining message sequence
- **Scalability** - Handling high message volumes
- **Decoupling** - Reducing service dependencies

## Pattern Categories

### Messaging Patterns
- **[Publish/Subscribe](..../pattern-library/communication.md/publish-subscribe.md)** - One-to-many message distribution
- **[Request/Reply](..../pattern-library/communication.md/request-reply.md)** - Asynchronous request-response
- **[WebSocket](..../pattern-library/communication.md/websocket.md)** - Real-time bidirectional communication
- **Message Queue** - Point-to-point asynchronous messaging
- **Message Router** - Content-based message routing

### RPC Patterns
- **[gRPC](..../pattern-library/communication.md/grpc.md)** - High-performance RPC with Protocol Buffers
- **Remote Procedure Call** - Synchronous method invocation
- **Async RPC** - Non-blocking remote calls
- **Streaming RPC** - Bidirectional streaming

### Service Discovery
- **[Service Discovery](..../pattern-library/communication.md/service-discovery.md)** - Dynamic service location
- **[Service Registry](..../pattern-library/communication.md/service-registry.md)** - Service metadata management

### Integration Patterns
- **[API Gateway](..../pattern-library/communication.md/api-gateway.md)** - Single entry point for clients
- **[Service Mesh](..../pattern-library/communication.md/service-mesh.md)** - Transparent service communication
- **Backend for Frontend** - Client-specific APIs

## Quick Decision Guide

| If you need... | Consider... |
|----------------|-------------|
| Simple async processing | Message Queue |
| Fan-out to multiple consumers | [Pub/Sub](..../pattern-library/communication.md/publish-subscribe.md) |
| Synchronous communication | [gRPC](..../pattern-library/communication.md/grpc.md) |
| Real-time bidirectional | [WebSocket](..../pattern-library/communication.md/websocket.md) |
| Async request-response | [Request/Reply](..../pattern-library/communication.md/request-reply.md) |
| API management | [API Gateway](..../pattern-library/communication.md/api-gateway.md) |
| Service-to-service mesh | [Service Mesh](..../pattern-library/communication.md/service-mesh.md) |
| Dynamic service location | [Service Discovery](..../pattern-library/communication.md/service-discovery.md) |

---

*Browse individual patterns below or return to the [Pattern Library](../index.md).*
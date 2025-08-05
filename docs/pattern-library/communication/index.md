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
- **[Publish/Subscribe](communication/publish-subscribe.md)** - One-to-many message distribution
- **[Request/Reply](request-reply.md)** - Asynchronous request-response
- **[WebSocket](communication/websocket.md)** - Real-time bidirectional communication
- **Message Queue** - Point-to-point asynchronous messaging
- **Message Router** - Content-based message routing

### RPC Patterns
- **[gRPC](grpc.md)** - High-performance RPC with Protocol Buffers
- **Remote Procedure Call** - Synchronous method invocation
- **Async RPC** - Non-blocking remote calls
- **Streaming RPC** - Bidirectional streaming

### Service Discovery
- **[Service Discovery](communication/service-discovery.md)** - Dynamic service location
- **[Service Registry](service-registry.md)** - Service metadata management

### Integration Patterns
- **[API Gateway](communication/api-gateway.md)** - Single entry point for clients
- **[Service Mesh](communication/service-mesh.md)** - Transparent service communication
- **Backend for Frontend** - Client-specific APIs

## Quick Decision Guide

| If you need... | Consider... |
|----------------|-------------|
| Simple async processing | Message Queue |
| Fan-out to multiple consumers | [Pub/Sub](communication/publish-subscribe.md) |
| Synchronous communication | [gRPC](grpc.md) |
| Real-time bidirectional | [WebSocket](communication/websocket.md) |
| Async request-response | [Request/Reply](request-reply.md) |
| API management | [API Gateway](communication/api-gateway.md) |
| Service-to-service mesh | [Service Mesh](communication/service-mesh.md) |
| Dynamic service location | [Service Discovery](communication/service-discovery.md) |

---

*Browse individual patterns below or return to the [Pattern Library](../).*
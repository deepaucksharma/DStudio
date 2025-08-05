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
- **[Publish/Subscribe](/pattern-library/communication/publish-subscribe/)** - One-to-many message distribution
- **[Request/Reply](/pattern-library/communication/request-reply/)** - Asynchronous request-response
- **[WebSocket](/pattern-library/communication/websocket/)** - Real-time bidirectional communication
- **Message Queue** - Point-to-point asynchronous messaging
- **Message Router** - Content-based message routing

### RPC Patterns
- **[gRPC](/pattern-library/communication/grpc/)** - High-performance RPC with Protocol Buffers
- **Remote Procedure Call** - Synchronous method invocation
- **Async RPC** - Non-blocking remote calls
- **Streaming RPC** - Bidirectional streaming

### Service Discovery
- **[Service Discovery](/pattern-library/communication/service-discovery/)** - Dynamic service location
- **[Service Registry](/pattern-library/communication/service-registry/)** - Service metadata management

### Integration Patterns
- **[API Gateway](/pattern-library/communication/api-gateway/)** - Single entry point for clients
- **[Service Mesh](/pattern-library/communication/service-mesh/)** - Transparent service communication
- **Backend for Frontend** - Client-specific APIs

## Quick Decision Guide

| If you need... | Consider... |
|----------------|-------------|
| Simple async processing | Message Queue |
| Fan-out to multiple consumers | [Pub/Sub](/pattern-library/communication/publish-subscribe/) |
| Synchronous communication | [gRPC](/pattern-library/communication/grpc/) |
| Real-time bidirectional | [WebSocket](/pattern-library/communication/websocket/) |
| Async request-response | [Request/Reply](/pattern-library/communication/request-reply/) |
| API management | [API Gateway](/pattern-library/communication/api-gateway/) |
| Service-to-service mesh | [Service Mesh](/pattern-library/communication/service-mesh/) |
| Dynamic service location | [Service Discovery](/pattern-library/communication/service-discovery/) |

---

*Browse individual patterns below or return to the [Pattern Library](../).*
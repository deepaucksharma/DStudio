---
title: WebSocket Pattern
category: communication
excellence_tier: silver
pattern_status: recommended
introduced: 2011-12
current_relevance: mainstream
---
# WebSocket Pattern

!!! success "🏆 Gold Standard Pattern"
**Implementation available in production systems**

## Essential Question
**How do we maintain persistent, bidirectional communication between clients and servers efficiently?**

## When to Use / When NOT to Use

### ✅ Use When
| Scenario | Why | Example |
|----------|-----|---------|
| **Real-time updates** | Push data instantly | Stock tickers, live scores |
| **Bidirectional flow** | Both sides initiate | Chat applications |
| **Low latency critical** | Minimal overhead | Online gaming |
| **High frequency updates** | Avoid polling overhead | Collaborative editing |

### ❌ DON'T Use When
| Scenario | Why | Alternative |
|----------|-----|-------------|
| **Request-response only** | Overhead not justified | REST API |
| **Unidirectional data** | One-way is simpler | Server-Sent Events |
| **Stateless operations** | Connection overhead | HTTP/2 |
| **Resource constrained** | Memory per connection | Long polling |

### The Phone Call Analogy
HTTP is like sending letters - you send a request and wait for a response. WebSocket is like a phone call - once connected, both parties can speak anytime without hanging up and redialing.

### Core Value
| Aspect | HTTP | WebSocket |
|--------|------|-----------|
| **Connection** | New for each request | Persistent |
| **Direction** | Client initiates only | Bidirectional |
| **Overhead** | Headers each time | One-time handshake |
| **Real-time** | Polling required | Native push |

### Basic Implementation

**System Flow:** Input → Processing → Output

### Performance Optimization

| Technique | Impact | Configuration |
|-----------|--------|---------------|
| **Message batching** | -70% syscalls | Buffer 10ms |
| **Binary frames** | -50% bandwidth | Use ArrayBuffer |
| **Compression** | -80% for text | permessage-deflate |
| **Connection pooling** | -90% handshakes | Reuse connections |

### Case Study: Discord's WebSocket Infrastructure

!!! info "🏢 Real-World Implementation"
**Implementation available in production systems**

### Advanced Reconnection

**System Flow:** Input → Processing → Output

<details>
<summary>View implementation code</summary>

<details>
<summary>📄 View decision logic</summary>

class ResilientWebSocket {
**Implementation available in production systems**

}

</details>

</details>

## Quick Reference

### Production Checklist ✓
- [ ] **Connection Management**
  - [ ] Implement heartbeat/ping-pong
  - [ ] Auto-reconnection with backoff
  - [ ] Connection pooling for scale
  - [ ] Graceful shutdown handling
  
- [ ] **Message Handling**
  - [ ] Message queuing for offline
  - [ ] Implement acknowledgments
  - [ ] Binary format for efficiency
  - [ ] Compression for large payloads
  
- [ ] **Security**
  - [ ] Authentication on connect
  - [ ] Rate limiting per connection
  - [ ] Input validation
  - [ ] Origin verification
  
- [ ] **Monitoring**
  - [ ] Connection count metrics
  - [ ] Message throughput
  - [ ] Latency percentiles
  - [ ] Error rates by type

### Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| **No heartbeat** | Silent disconnections | Ping/pong every 30s |
| **Memory leaks** | Server crash | Cleanup on disconnect |
| **No rate limiting** | DoS vulnerability | Per-connection limits |
| **Blocking operations** | Thread starvation | Use async everywhere |

### Performance Benchmarks

<details>
<summary>📄 View  code (6 lines)</summary>

**Implementation Concept:** See production systems for actual code

</details>

## Related Patterns

**Key Points:** Multiple configuration options and trade-offs available

## References

- [RFC 6455 - The WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [WebSocket API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Socket.IO](https://socket.io/) - WebSocket library with fallbacks
- [Discord's WebSocket Gateway](https://discord.com/developers/docs/topics/gateway)

---

**Previous**: [Service Discovery Pattern](../../pattern-library/communication/service-discovery.md) | **Next**: [Communication Patterns Index](../../index.md)

## Decision Matrix

### Quick Decision Table

| Factor | Low Complexity | Medium Complexity | High Complexity |
|--------|----------------|-------------------|-----------------|
| Team Size | < 5 developers | 5-20 developers | > 20 developers |
| Traffic | < 1K req/s | 1K-100K req/s | > 100K req/s |
| Data Volume | < 1GB | 1GB-1TB | > 1TB |
| **Recommendation** | ❌ Avoid | ⚠️ Consider | ✅ Implement |


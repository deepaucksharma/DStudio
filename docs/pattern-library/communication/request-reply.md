---
best_for:
**Key Points:** Multiple configuration options and trade-offs available

category: communication
current_relevance: mainstream
description: Asynchronous request-response communication pattern for distributed systems
difficulty: intermediate
essential_question: How do we achieve request-response semantics over asynchronous
  messaging systems?
excellence_tier: silver
introduced: 1990-01
pattern_status: use-with-expertise
prerequisites:
- message-queues
- distributed-systems
- asynchronous-programming
reading_time: 25 min
related_laws:
- law2-asynchrony
- law4-tradeoffs
- law6-human-api
related_pillars:
- work
- control
tagline: Asynchronous request-response with correlation management
title: Request-Reply Pattern
trade_offs:
  cons:
  - More complex than synchronous calls
  - Requires correlation ID management
  - Potential for lost replies and timeouts
  - State management overhead for pending requests
  - Debugging complexity with async flows
  pros:
  - Decouples client from server temporally
  - Enables asynchronous processing without blocking
  - Better resource utilization for long operations
  - Handles variable response times gracefully
  - Supports multiple reply patterns (single, stream, scatter-gather)
type: pattern
---

# Request-Reply Pattern

!!! info "🥈 Silver Tier Pattern"
**Implementation available in production systems**

## Essential Question

**How do we achieve request-response semantics over asynchronous messaging systems?**

## When to Use / When NOT to Use

### ✅ Use When

| Scenario | Example | Impact |
|----------|---------|--------|
| Long-running operations | File processing taking 5+ minutes | Frees client resources, enables parallel work |
| Legacy system integration | Mainframe communication via MQ | Bridges sync/async boundaries gracefully |
| Variable response times | Machine learning inference jobs | Handles unpredictable processing durations |
| Queue-based architectures | Order processing with confirmation | Provides response semantics over messaging |

### ❌ DON'T Use When

| Scenario | Why | Alternative |
|----------|-----|-------------|
| Simple synchronous calls | Added complexity without benefit | [gRPC](grpc.md) or REST |
| Real-time requirements | Messaging adds latency | [WebSocket](websocket.md) |
| Stateless operations | No need for response correlation | [Publish-Subscribe](publish-subscribe.md) |
| High-frequency trading | Every millisecond matters | Direct TCP connections |

### The Story

Imagine sending a letter with a pre-paid return envelope. Unlike email (immediate) or dropping a letter in a mailbox (fire-and-forget), you send your request knowing a response will come back asynchronously. You don't wait by the mailbox—you go about your business and handle the reply when it arrives.

### Core Insight

> **Key Takeaway:** Request-Reply transforms blocking synchronous calls into non-blocking asynchronous communication by using correlation IDs to match responses with requests.

### In One Sentence

Request-Reply **enables async request-response** by **using correlation IDs and reply queues** to achieve **temporal decoupling while maintaining response semantics**.

### The Problem Space

<div class="failure-vignette">
<h4>🚨 What Happens Without This Pattern</h4>

**Financial Services Company, 2021**: Trading system made synchronous calls to risk engine for each trade validation. Under peak load, 10,000 concurrent trades caused thread pool exhaustion. System froze for 3 minutes during market volatility.

**Impact**: $5M trading losses, regulatory compliance violation, client confidence damaged
</div>

#### Key Components

| Component | Purpose | Responsibility |
|-----------|---------|----------------|
| Correlation Manager | Request tracking | Generate IDs, manage timeouts, match responses |
| Reply Queue | Response delivery | Temporary queue for async responses |
| Request Handler | Server processing | Extract correlation, process, send reply |
| Timeout Manager | Cleanup | Remove expired correlations, prevent memory leaks |

### Basic Example

**Process Overview:** See production implementations for details

<details>
<summary>📄 View implementation code</summary>

import uuid
import asyncio
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Message:
**Implementation available in production systems**

class RequestReplyClient:
**Implementation available in production systems**

</details>

#### Critical Design Decisions

| Decision | Options | Trade-off | Recommendation |
|----------|---------|-----------|----------------|
| Correlation ID Strategy | UUID<br>Sequential numbers | UUID: No collisions<br>Sequential: Predictable | UUID for production systems |
| Reply Queue Management | Temporary queues<br>Shared reply queue | Temporary: Isolation<br>Shared: Efficiency | Temporary for security/isolation |
| Timeout Handling | Client-side only<br>Server-side cleanup | Client: Simple<br>Server: Robust | Both for comprehensive coverage |
| Error Propagation | Exception replies<br>Error codes | Exception: Rich context<br>Codes: Simple | Exception replies with structured errors |

### Decision Matrix

| Factor | Score (1-5) | Reasoning |
|--------|-------------|-----------|
| **Complexity** | 4 | Significant complexity managing correlation IDs, timeouts, reply queues, and asynchronous state |
| **Performance Impact** | 3 | Better resource utilization for long operations but adds messaging overhead and latency |
| **Operational Overhead** | 4 | Requires monitoring correlation state, managing timeouts, debugging async flows, and queue management |
| **Team Expertise Required** | 4 | Deep understanding of async programming, messaging patterns, and distributed systems timing |
| **Scalability** | 4 | Excellent for decoupling and handling variable load patterns without blocking resources |

**Overall Recommendation**: ⚠️ **USE WITH EXPERTISE** - Powerful for asynchronous processing but requires careful implementation of correlation management and timeout handling.

### Common Pitfalls

<div class="decision-box">
<h4>⚠️ Avoid These Mistakes</h4>

**Process Steps:**
- Initialize system
- Process requests
- Handle responses
- Manage failures


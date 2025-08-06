---
best_for: Distributed locks, leader election, session management, resource reservations
  where automatic cleanup is essential
category: coordination
current_relevance: mainstream
description: Time-bound resource ownership with automatic expiration for distributed
  systems reliability
difficulty: intermediate
essential_question: How do we prevent resources from being held forever when their
  owners disappear or become unreachable?
excellence_tier: silver
introduced: 1987-01
pattern_status: recommended
prerequisites:
- distributed-lock
- heartbeat
reading_time: 25 min
related_laws:
- asynchronous-reality
- correlated-failure
- distributed-knowledge
related_pillars:
- truth
- control
- state
tagline: Time-bound resource ownership with automatic expiration
title: Lease Pattern
trade_offs:
  cons:
  - False timeouts if renewal fails due to network issues
  - Clock skew can cause premature expiration
  - Renewal overhead creates additional network traffic
  - Lease duration tuning requires understanding workload patterns
  pros:
  - Automatic cleanup prevents resource hoarding
  - Time-based failure detection works across partitions
  - No manual cleanup required for crashed processes
  - Prevents eternal deadlocks in distributed systems
type: pattern
---

# Lease Pattern

!!! info "🥈 Silver Tier Pattern"
**Implementation available in production systems**

## Essential Question

**How do we prevent resources from being held forever when their owners disappear or become unreachable?**

## When to Use

## Decision Flow

/ When NOT to Use

### ✅ Use When

| Scenario | Example | Impact |
|----------|---------|--------|
| **Distributed Locking** | Database connection pools | Prevents eternal locks from crashed processes |
| **Leader Election** | Service coordinator selection | Automatic failover when leader becomes unreachable |
| **Session Management** | User login sessions | Automatic cleanup of inactive sessions |
| **Resource Reservations** | Compute resource allocation | Prevents resource hoarding from failed schedulers |

### ❌ DON'T Use When

| Scenario | Why | Alternative |
|----------|-----|-------------|
| **Permanent Ownership** | Need indefinite resource control | Traditional locks with explicit release |
| **Sub-second Operations** | Renewal overhead exceeds operation time | Optimistic concurrency control |
| **Single-Node Systems** | No distributed failure scenarios | Local locks and cleanup |
| **No Network Access** | Cannot implement renewal mechanism | Timeout-based patterns |

### The Story

Imagine borrowing a book from a library with a due date. You can renew it before it expires if you still need it, but if you forget or can't return it, the library automatically makes it available for others. This prevents books from being lost forever and ensures fair access to resources.

### The Parking Meter Analogy

A lease is like a parking meter:
**Key Points:** Multiple configuration options and trade-offs available

The key insight: Time-based ownership prevents resource hoarding when owners disappear.

### Lease Lifecycle

---

### The Problem Space

<div class="failure-vignette">
<h4>🚨 What Happens Without Time-Based Expiration</h4>

**Distributed System, 2019**: A microservice crashed while holding a database connection lock. Without automatic expiration, the resource remained locked for 8 hours until manual intervention, blocking all dependent services.

**Impact**: 8-hour service degradation, 40% revenue loss during peak hours, and manual oncall escalation to identify and resolve the stuck lock.
</div>

#### Core Properties

| Property | Description | Benefit |
|----------|-------------|---------|
| **Time-bound** | Every lease has expiration | No eternal locks |
| **Renewable** | Can extend before expiry | Long operations supported |
| **Automatic cleanup** | Expires without action | Handles failures gracefully |
| **Owner tracking** | Identifies leaseholder | Enables safe operations |

### Common Lease Durations

| Use Case | Typical Duration | Renewal Strategy |
|----------|------------------|------------------|
| **Distributed lock** | 10-30 seconds | Renew at 50% remaining |
| **Session management** | 5-30 minutes | Renew on activity |
| **Resource reservation** | 1-24 hours | Explicit renewal |
| **Cache entries** | 1-60 minutes | No renewal (expire) |
| **Leader election** | 5-15 seconds | Continuous renewal |

## Decision Matrix

| Factor | Score (1-5) | Reasoning |
|--------|-------------|-----------|
| **Complexity** | 3 | Time management, renewal logic, expiration handling, but well-established patterns |
| **Performance Impact** | 2 | Low overhead - periodic renewals and time checks, minimal impact on operations |
| **Operational Overhead** | 3 | Monitoring lease health, tuning durations, handling false timeouts |
| **Team Expertise Required** | 3 | Understanding of distributed timing, clock skew, and renewal strategies |
| **Scalability** | 4 | Scales well with lightweight time-based checks, prevents resource hoarding |

**Overall Recommendation: ✅ RECOMMENDED** - Essential for any distributed system requiring time-bound resource ownership.

---

### Production Lease Implementation

**Process Overview:** See production implementations for details

<details>
<summary>📄 View implementation code</summary>

from datetime import datetime, timedelta
from typing import Optional, Dict, Callable
import asyncio
import uuid
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Lease:
**Implementation available in production systems**

class LeaseStore(ABC):
**Implementation available in production systems**

class InMemoryLeaseStore(LeaseStore):
**Implementation available in production systems**

class LeaseManager:
**Implementation available in production systems**

## Redis-based implementation
class RedisLeaseStore(LeaseStore):
**Implementation available in production systems**

## Example usage patterns
async def distributed_job_example():
**Implementation available in production systems**

async def leader_election_example():
**Implementation available in production systems**

</details>

### Lease Renewal Strategies

---

#### **Process Steps:**
- Initialize system
- Process requests
- Handle responses
- Manage failures


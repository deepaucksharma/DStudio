# Common System Design Problems

Practice with frequently asked system design interview questions.

## Overview

This collection includes the most common system design problems asked in technical interviews. Each problem includes:

- **Problem Statement** - Clear requirements
- **Solution Approach** - Step-by-step design
- **Key Components** - Critical system parts
- **Scaling Considerations** - Growth handling
- **Trade-offs** - Design decisions
- **Follow-up Questions** - Advanced scenarios

## 📚 Available Problems

### Storage & Collaboration Systems
- **[Cloud Storage System](cloud-storage.md)** - Dropbox/Google Drive clone
- **[Collaborative Document Editor](collaborative-editor.md)** - Google Docs real-time editing

### Development & Infrastructure
- **[CI/CD Pipeline System](cicd-pipeline.md)** - Jenkins/GitHub Actions clone
- **[IoT Platform](iot-platform.md)** - Device management and data processing
- **[ML Serving System](ml-serving.md)** - Model deployment and inference

## 🎯 Difficulty Levels

### Intermediate (45-60 min)
| Problem | Key Concepts |
|---------|--------------|
| [Cloud Storage](cloud-storage.md) | File sync, deduplication, conflict resolution |
| [Collaborative Editor](collaborative-editor.md) | Real-time sync, operational transforms |
| [CI/CD Pipeline](cicd-pipeline.md) | Job orchestration, artifact management |

### Advanced (60+ min)
| Problem | Key Concepts |
|---------|--------------|
| [IoT Platform](iot-platform.md) | Device management, stream processing, time series data |
| [ML Serving System](ml-serving.md) | Model lifecycle, feature stores, A/B testing |

## 📊 Common Patterns Used

| Pattern | Used In | Purpose |
|---------|---------|---------|
| **Event Sourcing** | Cloud Storage, Collaborative Editor | Track all changes |
| **CQRS** | ML Serving | Separate read/write paths |
| **Message Queue** | IoT Platform, CI/CD | Async processing |
| **Consistent Hashing** | All systems | Data distribution |
| **Circuit Breaker** | ML Serving, IoT | Fault tolerance |
| **Load Balancing** | All systems | Traffic distribution |
| **Caching** | All systems | Performance |

## 🚀 More Problems Coming Soon

We're actively expanding this collection. Future problems will include:

### Fundamental Systems
- URL Shortener - Bitly, TinyURL clone
- Pastebin - Text sharing service
- Key-Value Store - Distributed cache/storage
- Rate Limiter - API throttling

### Social Media Systems
- Twitter Clone - Timeline, following, tweets
- Instagram - Photo sharing, stories
- Facebook News Feed - Feed generation
- LinkedIn - Professional network

### Messaging Systems
- WhatsApp - 1:1 and group chat
- Slack - Team communication
- Discord - Voice and text chat
- Email Service - Gmail-like system

### Media Systems
- YouTube - Video upload and streaming
- Netflix - Video streaming service
- Spotify - Music streaming
- Twitch - Live streaming

### E-commerce Systems
- Amazon - Product catalog, orders
- Payment System - Stripe/PayPal clone
- Inventory Management - Stock tracking
- Shopping Cart - Cart service

### Transportation Systems
- Uber/Lyft - Ride matching
- Uber Eats - Food delivery
- Maps Service - Google Maps clone
- Parking System - Smart parking

### Booking Systems
- Hotel Booking - Booking.com clone
- Movie Booking - Fandango clone
- Calendar System - Google Calendar
- Airline Booking - Flight reservations

## 💡 How to Use These Problems

### 1. Choose Based on Interview Target
- **FAANG**: Focus on scale (ML Serving, IoT Platform)
- **Startups**: Focus on practical systems (CI/CD, Cloud Storage)
- **Domain-specific**: Pick relevant problems

### 2. Practice Approach
1. **Understand Requirements** (5-10 min)
   - Functional requirements
   - Non-functional requirements
   - Scale estimates

2. **High-Level Design** (10-15 min)
   - Major components
   - Data flow
   - API design

3. **Detailed Design** (20-30 min)
   - Data models
   - Algorithms
   - System architecture

4. **Scale & Optimize** (10-15 min)
   - Bottleneck analysis
   - Caching strategy
   - Data partitioning

5. **Trade-offs & Alternatives** (5-10 min)
   - Design choices
   - Technology selection
   - Cost considerations

### 3. Key Skills to Demonstrate
- **Requirements gathering** - Ask clarifying questions
- **Estimation** - Back-of-envelope calculations
- **Trade-off analysis** - No perfect solutions
- **Incremental design** - Start simple, then scale
- **Best practices** - Security, monitoring, testing

## 📖 Study Resources

### Before Practice
- Review [System Design Frameworks](../frameworks/)
- Study [Common Patterns](../../../pattern-library/)
- Check [Scalability Numbers](../cheatsheets/)

### During Practice
- Use [System Design Checklist](../cheatsheets/system-design-checklist.md)
- Follow consistent approach
- Time yourself

### After Practice
- Compare with solutions
- Identify knowledge gaps
- Practice explaining out loud

## 🎪 Problem Selection Strategy

### Week 1-2: Fundamentals
Start with storage and infrastructure problems to build foundation

### Week 3-4: Intermediate Systems
Practice real-time collaboration and development tools

### Week 5-6: Advanced Systems
Tackle ML serving and IoT for complex distributed systems

### Week 7-8: Mock Interviews
Random problem selection with time constraints

---

*Remember: The goal isn't to memorize solutions but to develop systematic thinking for approaching any system design problem.*
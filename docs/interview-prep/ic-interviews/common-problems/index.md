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

## 📚 Problems by Category

### Fundamental Systems
- **[URL Shortener](url-shortener/)** - Bitly, TinyURL clone
- **[Pastebin](pastebin/)** - Text sharing service
- **[Key-Value Store](key-value-store/)** - Distributed cache/storage
- **[Rate Limiter](rate-limiter/)** - API throttling

### Social Media Systems
- **[Twitter Clone](twitter/)** - Timeline, following, tweets
- **[Instagram](instagram/)** - Photo sharing, stories
- **[Facebook News Feed](news-feed/)** - Feed generation
- **[LinkedIn](linkedin/)** - Professional network

### Messaging Systems
- **[WhatsApp](whatsapp/)** - 1:1 and group chat
- **[Slack](slack/)** - Team communication
- **[Discord](discord/)** - Voice and text chat
- **[Email Service](email/)** - Gmail-like system

### Media Systems
- **[YouTube](youtube/)** - Video upload and streaming
- **[Netflix](netflix/)** - Video streaming service
- **[Spotify](spotify/)** - Music streaming
- **[Twitch](twitch/)** - Live streaming

### E-commerce Systems
- **[Amazon](amazon/)** - Product catalog, orders
- **[Payment System](payment-system/)** - Stripe/PayPal clone
- **[Inventory Management](inventory/)** - Stock tracking
- **[Shopping Cart](shopping-cart/)** - Cart service

### Storage & Collaboration Systems
- **[Cloud Storage](cloud-storage/)** - Dropbox/Google Drive clone
- **[Collaborative Editor](collaborative-editor/)** - Google Docs real-time editing

### Development & Infrastructure
- **[CI/CD Pipeline](cicd-pipeline/)** - Jenkins/GitHub Actions clone
- **[IoT Platform](iot-platform/)** - Device management and data processing
- **[ML Serving System](ml-serving/)** - Model deployment and inference

### Transportation Systems
- **[Uber/Lyft](ride-sharing/)** - Ride matching
- **[Uber Eats](food-delivery/)** - Food delivery
- **[Maps Service](maps/)** - Google Maps clone
- **[Parking System](parking/)** - Smart parking

### Booking Systems
- **[Hotel Booking](hotel-booking/)** - Booking.com clone
- **[Movie Booking](movie-booking/)** - Fandango clone
- **[Calendar System](calendar/)** - Google Calendar
- **[Airline Booking](airline-booking/)** - Flight reservations

## 🎯 Difficulty Levels

### Beginner (30-45 min)
| Problem | Key Concepts |
|---------|--------------|
| URL Shortener | Encoding, caching, analytics |
| Pastebin | Storage, expiration |
| Rate Limiter | Algorithms, distribution |
| Key-Value Store | Partitioning, replication |

### Intermediate (45-60 min)
| Problem | Key Concepts |
|---------|--------------|
| Chat Application | WebSockets, message delivery |
| News Feed | Timeline generation, ranking |
| Video Upload | Encoding, storage, CDN |
| Payment System | Transactions, consistency |
| **[Cloud Storage](cloud-storage/)** | File sync, deduplication, conflict resolution |
| **[Collaborative Editor](collaborative-editor/)** | Real-time sync, operational transforms |
| **[CI/CD Pipeline](cicd-pipeline/)** | Job orchestration, artifact management |

### Advanced (60+ min)
| Problem | Key Concepts |
|---------|--------------|
| Uber System | Real-time matching, location |
| Search Engine | Indexing, ranking, crawling |
| Social Network | Graph algorithms, scaling |
| Live Streaming | Low latency, distribution |
| **[IoT Platform](iot-platform/)** | Device management, stream processing |
| **[ML Serving System](ml-serving/)** | Model lifecycle, feature stores, A/B testing |

## 📊 Common Patterns Used

### By Problem Type

| Problem Type | Common Patterns |
|--------------|-----------------|
| Real-time | WebSockets, Pub/Sub, Push Notifications |
| Feed Systems | Pull/Push/Hybrid, Timeline Generation |
| Storage | Sharding, Replication, Caching |
| Streaming | CDN, Encoding, Adaptive Bitrate |
| Transactions | Saga, 2PC, Event Sourcing |
| **Collaboration** | **Operational Transforms, CRDTs, WebSocket Scaling** |
| **File Systems** | **Content Addressable Storage, Deduplication, Conflict Resolution** |
| **DevOps** | **Event-Driven Architecture, Job Queues, Circuit Breaker** |
| **IoT** | **Stream Processing, Time Series DB, Device Management** |
| **ML Systems** | **Model Versioning, Feature Store, A/B Testing** |

## 🏃 Practice Strategy

### Week 1: Fundamentals
- Day 1-2: URL Shortener, Pastebin
- Day 3-4: Rate Limiter, KV Store
- Day 5-7: Review and variations

### Week 2: Communication
- Day 1-2: Chat systems
- Day 3-4: Feed systems
- Day 5-7: Notification systems

### Week 3: Media & Scale
- Day 1-2: Video systems
- Day 3-4: E-commerce
- Day 5-7: Transportation

### Week 4: Advanced & Specialized
- Day 1-2: IoT and ML serving systems
- Day 3-4: Collaboration and real-time systems
- Day 5-7: Mock interviews with new problems

## 💡 Problem-Solving Framework

1. **Clarify Requirements**
   - Functional requirements
   - Non-functional requirements
   - Scale estimates
   - Constraints

2. **Capacity Estimation**
   - Users and traffic
   - Storage needs
   - Bandwidth requirements

3. **System Design**
   - High-level architecture
   - Data model
   - API design
   - Algorithm choice

4. **Deep Dive**
   - Component details
   - Data flow
   - Failure scenarios

5. **Scale & Optimize**
   - Bottleneck identification
   - Caching strategy
   - Database optimization

---

## 🆕 Recently Added Problems

The following advanced system design problems have been added to cover modern distributed systems challenges:

- **[Cloud Storage System](cloud-storage/)** - File synchronization, deduplication, and conflict resolution
- **[IoT Platform](iot-platform/)** - Device management and real-time data processing at scale  
- **[ML Serving System](ml-serving/)** - Model lifecycle management and inference serving
- **[Collaborative Editor](collaborative-editor/)** - Real-time collaborative editing with operational transforms
- **[CI/CD Pipeline](cicd-pipeline/)** - Build orchestration and deployment automation

---

*Start with [URL Shortener](url-shortener/) for a classic introductory problem, or explore the new specialized problems for modern system design challenges.*
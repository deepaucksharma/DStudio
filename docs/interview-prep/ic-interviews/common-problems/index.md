---
title: Common Problems
description: Common Problems overview and navigation
category: interview-prep
tags: [interview-prep]
date: 2025-08-07
---

# Common System Design Problems

## Table of Contents

- [Overview](#overview)
- [📚 Available Problems](#-available-problems)
  - [Storage & Collaboration Systems](#storage-collaboration-systems)
  - [Development & Infrastructure](#development-infrastructure)
- [🎯 Difficulty Levels](#-difficulty-levels)
  - [Intermediate (45-60 min)](#intermediate-45-60-min)
  - [Advanced (60+ min)](#advanced-60-min)
- [📊 Common Patterns Used](#-common-patterns-used)
- [🚀 More Problems Coming Soon](#-more-problems-coming-soon)
  - [Fundamental Systems](#fundamental-systems)
  - [Social Media Systems](#social-media-systems)
  - [Messaging Systems](#messaging-systems)
  - [Media Systems](#media-systems)
  - [E-commerce Systems](#e-commerce-systems)
  - [Transportation Systems](#transportation-systems)
  - [Booking Systems](#booking-systems)
- [💡 How to Use These Problems](#-how-to-use-these-problems)
  - [1. Choose Based on Interview Target](#1-choose-based-on-interview-target)
  - [2. Practice Approach](#2-practice-approach)
  - [3. Key Skills to Demonstrate](#3-key-skills-to-demonstrate)
- [📖 Study Resources](#-study-resources)
  - [Before Practice](#before-practice)
  - [During Practice](#during-practice)
  - [After Practice](#after-practice)
- [🎪 Problem Selection Strategy](#-problem-selection-strategy)
  - [Week 1-2: Fundamentals](#week-1-2-fundamentals)
  - [Week 3-4: Intermediate Systems](#week-3-4-intermediate-systems)
  - [Week 5-6: Advanced Systems](#week-5-6-advanced-systems)
  - [Week 7-8: Mock Interviews](#week-7-8-mock-interviews)



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
- **[Cloud Storage System](../ic-interviews/common-problems/cloud-storage.md)** - Dropbox/Google Drive clone
- **[Collaborative Document Editor](../ic-interviews/common-problems/collaborative-editor.md)** - Google Docs real-time editing

### Development & Infrastructure
- **[CI/CD Pipeline System](../ic-interviews/common-problems/cicd-pipeline.md)** - Jenkins/GitHub Actions clone
- **[IoT Platform](../ic-interviews/common-problems/iot-platform.md)** - Device management and data processing
- **[ML Serving System](../ic-interviews/common-problems/ml-serving.md)** - Model deployment and inference

## 🎯 Difficulty Levels

### Intermediate (45-60 min)
| Problem | Key Concepts |
|---------|--------------|
| [Cloud Storage](../ic-interviews/common-problems/cloud-storage.md) | File sync, deduplication, conflict resolution |
| [Collaborative Editor](../ic-interviews/common-problems/collaborative-editor.md) | Real-time sync, operational transforms |
| [CI/CD Pipeline](../ic-interviews/common-problems/cicd-pipeline.md) | Job orchestration, artifact management |

### Advanced (60+ min)
| Problem | Key Concepts |
|---------|--------------|
| [IoT Platform](../ic-interviews/common-problems/iot-platform.md) | Device management, stream processing, time series data |
| [ML Serving System](../ic-interviews/common-problems/ml-serving.md) | Model lifecycle, feature stores, A/B testing |

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
- Review [System Design Frameworks](../ic-interviews/frameworks/)
- Study [Common Patterns](../pattern-library/)
- Check [Scalability Numbers](../ic-interviews/cheatsheets/)

### During Practice
- Use [System Design Checklist](../ic-interviews/cheatsheets/system-design-checklist.md)
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
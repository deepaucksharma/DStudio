---
title: "Law 6: Cognitive Load - Quick Assessment"
description: Objective assessment on human factors and operational complexity in distributed systems
type: test
difficulty: advanced
time_limit: 30 minutes
question_count: 30
passing_score: 75
---

# Law 6: The Law of Cognitive Load

⏱️ **Time:** 30 minutes | 📝 **30 questions** | ✅ **Passing:** 75%

!!! abstract "Core Principle"
    System complexity must respect human cognitive limits. Engineers cannot effectively operate systems they cannot understand.

---

## Section A: Fundamentals (10 questions)

### 1. [Multiple Choice] Alert Limit
What's the maximum number of alerts an on-call engineer can effectively handle per shift?
- A) 50-100
- B) 20-30
- C) 5-10 ✓
- D) 1-3

### 2. [True/False] Dashboard Quantity
More dashboards always improve system observability.
- **Answer:** False
- **Reason:** Too many dashboards increase cognitive load and reduce effectiveness.

### 3. [Fill in Blank] Miller's Number
The human brain can hold _______ ± 2 items in working memory.
- **Answer:** 7 (seven)

### 4. [Multiple Choice] Documentation Problem
What percentage of documentation is typically out of date after 6 months?
- A) 10%
- B) 30%
- C) 60% ✓
- D) 90%

### 5. [One-line] Alert Fatigue
What causes alert fatigue in operations teams?
- **Answer:** Too many non-actionable or false-positive alerts

### 6. [Multiple Choice] Runbook Effectiveness
Runbooks are most effective when they are:
- A) Comprehensive with every detail
- B) Concise with clear action steps ✓
- C) Written by developers only
- D) Never updated

### 7. [True/False] Microservice Complexity
Microservices always reduce cognitive load compared to monoliths.
- **Answer:** False
- **Reason:** Microservices can increase operational complexity and cognitive load.

### 8. [Fill in Blank] Context Switching
The cognitive penalty for context switching between tasks is approximately _______%.
- **Answer:** 25 (20-25% productivity loss)

### 9. [Multiple Choice] On-call Rotation
Optimal on-call rotation frequency is typically:
- A) Daily
- B) Weekly ✓
- C) Monthly
- D) Quarterly

### 10. [One-line] Automation Goal
What's the primary cognitive benefit of automation?
- **Answer:** Reduces repetitive tasks and decision fatigue

---

## Section B: Application (10 questions)

### 11. [Pattern Matching] Complexity Sources
Match the complexity source to its mitigation:
1. Too many services       A. Service mesh
2. Alert storms            B. Alert aggregation
3. Complex deployments     C. GitOps/automation
4. Unclear dependencies    D. Service map visualization

**Answers:** 1-A, 2-B, 3-C, 4-D

### 12. [Multiple Choice] Error Message Quality
Good error messages should include:
- A) Stack traces only
- B) Context, impact, and suggested action ✓
- C) Error codes only
- D) Timestamp only

### 13. [True/False] Tribal Knowledge
Relying on tribal knowledge for operations is a sustainable practice.
- **Answer:** False
- **Reason:** Creates single points of failure and increases cognitive load.

### 14. [Calculate] Team Size
Using the "two-pizza rule," maximum effective team size is approximately:
- **Answer:** 8-10 people

### 15. [Multiple Choice] Incident Command
During incidents, having a single incident commander:
- A) Slows down response
- B) Reduces cognitive load and improves coordination ✓
- C) Is unnecessary
- D) Increases confusion

### 16. [Fill in Blank] Observability Pillars
The three pillars of observability are: metrics, logs, and _______.
- **Answer:** traces

### 17. [One-line] Configuration Complexity
What's the main cognitive risk of having too many configuration parameters?
- **Answer:** Increased chance of misconfiguration and operational errors

### 18. [Multiple Choice] Service Naming
Good service naming conventions:
- A) Use creative, unique names
- B) Follow consistent, descriptive patterns ✓
- C) Use random identifiers
- D) Change frequently

### 19. [True/False] Full-stack Teams
Full-stack teams owning their services end-to-end always reduces cognitive load.
- **Answer:** False
- **Reason:** Can overwhelm teams with too many responsibilities.

### 20. [Pattern Match] Cognitive Tools
Match the tool to its cognitive benefit:
1. Distributed tracing    A. Reduces alert noise
2. Chaos engineering      B. Builds mental models
3. Feature flags         C. Simplifies rollback
4. Alert deduplication   D. Visualizes request flow

**Answers:** 1-D, 2-B, 3-C, 4-A

---

## Section C: Design & Operations (10 questions)

### 21. [Best Choice] New Engineer Onboarding
To minimize cognitive load for new engineers:
- A) Give them all documentation at once
- B) Structured progression with mentorship ✓
- C) Immediate on-call responsibility
- D) No documentation, learn by doing

### 22. [Multiple Choice] Architecture Diagram Limit
How many components can an architecture diagram have before becoming ineffective?
- A) 5-7
- B) 10-15 ✓
- C) 30-50
- D) Unlimited

### 23. [Rank Order] Cognitive Load Sources
Rank from highest to lowest cognitive load:
- Debugging distributed trace
- Reading single service logs
- Checking simple health endpoint
- Viewing aggregated metrics dashboard

**Answer:** Debugging distributed trace, Reading service logs, Viewing dashboard, Checking health endpoint

### 24. [One-line] Postmortem Purpose
From a cognitive load perspective, what's the main value of postmortems?
- **Answer:** Building shared mental models and preventing repeat incidents

### 25. [True/False] Zero-touch Operations
Fully automated "zero-touch" operations eliminates all cognitive load.
- **Answer:** False
- **Reason:** Automation failures require deep understanding to debug.

### 26. [Multiple Choice] Pager Duty Policy
Best practice for after-hours pages is:
- A) Page for everything
- B) Page only for customer-impacting issues ✓
- C) Never page
- D) Page randomly for training

### 27. [Fill in Blank] Mental Model
A shared _______ model helps teams understand system behavior consistently.
- **Answer:** mental

### 28. [Best Choice] System Complexity
When system complexity exceeds team cognitive capacity:
- A) Add more monitoring
- B) Simplify architecture or split teams ✓
- C) Hire smarter engineers
- D) Increase documentation

### 29. [Multiple Choice] Deployment Frequency
From a cognitive load perspective, optimal deployment frequency is:
- A) Once per quarter
- B) Once per month
- C) Multiple times per day with automation ✓
- D) Continuously without human intervention

### 30. [Identify] Anti-pattern
Which practice creates unnecessary cognitive load?
- A) Consistent naming conventions
- B) Automated testing
- C) Manual multi-step deployment processes ✓
- D) Centralized logging

---

## Answer Key Summary

**Section A (Fundamentals):** 1-C, 2-False, 3-7, 4-C, 5-Too many non-actionable alerts, 6-B, 7-False, 8-25, 9-B, 10-Reduces repetitive tasks

**Section B (Application):** 11-(1-A,2-B,3-C,4-D), 12-B, 13-False, 14-8-10, 15-B, 16-traces, 17-Increased misconfiguration risk, 18-B, 19-False, 20-(1-D,2-B,3-C,4-A)

**Section C (Design):** 21-B, 22-B, 23-Trace/Logs/Dashboard/Health, 24-Building shared mental models, 25-False, 26-B, 27-mental, 28-B, 29-C, 30-C

---

## Quick Reference Card

### Cognitive Limits

| Aspect | Human Limit | Implication |
|--------|------------|-------------|
| **Working Memory** | 7±2 items | Limit dashboard metrics |
| **Context Switch** | 25% penalty | Minimize interruptions |
| **Decision Fatigue** | 10-15/day | Automate routine decisions |
| **Alert Processing** | 5-10/shift | Reduce alert noise |
| **Learning Curve** | 3-6 months | Plan onboarding time |

### Complexity Reducers

1. **Consistent Patterns:** Naming, APIs, deployment
2. **Clear Boundaries:** Service ownership, responsibilities  
3. **Good Documentation:** Concise, current, accessible
4. **Effective Tooling:** Unified observability, automation
5. **Team Structure:** Right-sized, clear ownership

### Operational Best Practices

- **Progressive Disclosure:** Show details only when needed
- **Automation:** Reduce toil and repetitive decisions
- **Runbooks:** Clear, tested, actionable steps
- **Mental Models:** Build shared understanding
- **Blameless Culture:** Reduce fear, increase learning

### Remember
- **Humans are the bottleneck** - Respect cognitive limits
- **Simplicity scales** - Complex systems fail in complex ways
- **Automate toil** - Save human cognition for hard problems
- **Documentation rots** - Keep it minimal and current

---

*Continue to [Law 7: Economic Reality →](economic-reality-test.md)*
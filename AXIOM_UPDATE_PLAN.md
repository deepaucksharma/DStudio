# Comprehensive Site Update Plan: New 7-Axiom Structure

## Overview
The site is transitioning from 8 simple axioms to 7 advanced laws. This document tracks all required updates across the entire codebase.

## Axiom Mapping

### OLD → NEW Structure
```
OLD AXIOMS (8):
1. Latency (Speed of Light)
2. Finite Capacity  
3. Inevitable Failure
4. Concurrency Complexity
5. Coordination Costs
6. Limited Observability
7. Human Interface Constraints
8. Economic Reality

NEW AXIOMS (7):
1. Law of Correlated Failure ⛓️ (from old #3 + correlation concepts)
2. Law of Asynchronous Reality ⏳ (from old #1 + time uncertainty)
3. Law of Emergent Chaos 🌪️ (NEW - complexity at scale)
4. Law of Multidimensional Optimization ⚖️ (from old #5 + trade-offs)
5. Law of Distributed Knowledge 🧠 (from old #6 + epistemology)
6. Law of Cognitive Load 🤯 (from old #7)
7. Law of Economic Reality 💰 (from old #8)
```

## Critical Updates Required

### 1. Core Navigation Files
- [ ] `/docs/index.md` - Update "8 Axioms" → "7 Laws"
- [ ] `/docs/introduction/index.md` - Update axiom list
- [ ] `/docs/axioms/index.md` - Complete rewrite with new structure
- [ ] `/docs/pillars/index.md` - Update axiom-to-pillar mappings
- [ ] `/mkdocs.yml` - Update navigation structure

### 2. Axiom Directory Structure
```
Current State:
- axiom1-failure/ (new #1)
- axiom1-latency/ (OLD - to archive)
- axiom2-asynchrony/ (new #2)
- axiom2-capacity/ (OLD - to archive)
- axiom3-emergence/ (new #3)
- axiom3-failure/ (OLD - to archive)
- axiom4-tradeoffs/ (new #4)
- axiom4-concurrency/ (OLD - to archive)
- axiom5-epistemology/ (new #5)
- axiom5-coordination/ (OLD - to archive)
- axiom6-human-api/ (new #6)
- axiom6-observability/ (OLD - to archive)
- axiom7-economics/ (new #7)
- axiom7-human/ (OLD - to archive)
- axiom8-economics/ (OLD - to archive)
```

### 3. Cross-Reference Updates

#### Patterns that reference axioms:
- `/docs/patterns/circuit-breaker.md` - References old Axiom 3 (Failure)
- `/docs/patterns/caching-strategies.md` - References old Axiom 1 (Latency)
- `/docs/patterns/sharding.md` - References old Axiom 2 (Capacity)
- `/docs/patterns/consensus.md` - References old Axiom 5 (Coordination)
- `/docs/patterns/observability.md` - References old Axiom 6 (Observability)
- `/docs/patterns/auto-scaling.md` - References old Axiom 8 (Economics)

#### Pillars that map to axioms:
- Work Distribution: Old Axioms 1+2 → New Axioms 2+4
- State Distribution: Old Axioms 2+3 → New Axioms 1+3
- Truth Distribution: Old Axioms 4+5 → New Axioms 4+5
- Control Distribution: Old Axioms 6+7 → New Axioms 5+6
- Intelligence Distribution: All → New 3+4+7

#### Case Studies mentioning axioms:
- Amazon DynamoDB - Old Axiom 3 (Failure)
- Uber Location - Old Axiom 1 (Latency)
- PayPal Payments - Old Axiom 5 (Coordination)
- Spotify - Old Axiom 8 (Economics)

### 4. Content Updates by File

#### `/docs/index.md` (Homepage)
- Line 18: "⚛️ 8 Axioms" → "⚛️ 7 Laws"
- Update axioms link to new structure

#### `/docs/introduction/index.md`
- Line 16: "8 Fundamental Axioms" → "7 Advanced Laws"
- Update axiom list to new names

#### `/docs/axioms/index.md`
- Complete rewrite with new 7-law structure
- Add emoji indicators
- Update grid layout from 8 to 7 items
- New categorization: Physical Laws, Trade-offs, Human Interface

#### `/docs/pillars/index.md`
- Update axiom-to-pillar flow diagram
- Revise axiom combinations for each pillar
- Update mermaid diagram connections

#### `/mkdocs.yml`
- Lines 142-151: Update axiom navigation
- Remove references to old axiom directories
- Add new axiom structure with proper names

### 5. Implementation Phases

#### Phase 1: Core Structure (Immediate)
1. Update main index pages (home, intro, axioms, pillars)
2. Update mkdocs.yml navigation
3. Create axiom mapping reference

#### Phase 2: Directory Cleanup (Day 2)
1. Archive old axiom directories
2. Rename new directories to match structure
3. Update all internal links

#### Phase 3: Cross-References (Day 3-4)
1. Update pattern references
2. Update case study references
3. Update pillar mappings

#### Phase 4: Content Enhancement (Week 2)
1. Add missing axiom content (3, 4, 5, 6, 7)
2. Update existing axioms to new format
3. Add synthesis.md for interactions

### 6. Testing Checklist
- [ ] All navigation links work
- [ ] No references to "8 axioms" remain
- [ ] All cross-references updated
- [ ] Search index rebuilt
- [ ] No broken internal links
- [ ] Axiom emojis display correctly

### 7. Rollback Plan
If issues arise:
1. Git revert to previous state
2. Keep old axiom directories temporarily
3. Add redirects for old URLs
4. Gradual migration with both structures

## Quick Reference Card

### Old Axiom → New Axiom Mapping
```
Latency (1) → Asynchronous Reality (2)
Capacity (2) → Multidimensional Optimization (4) 
Failure (3) → Correlated Failure (1)
Concurrency (4) → Emergent Chaos (3)
Coordination (5) → Multidimensional Optimization (4)
Observability (6) → Distributed Knowledge (5)
Human (7) → Cognitive Load (6)
Economics (8) → Economic Reality (7)
```

### New Axiom Quick Reference
1. ⛓️ Correlated Failure - Dependencies amplify failures
2. ⏳ Asynchronous Reality - Information has uncertainty
3. 🌪️ Emergent Chaos - Complexity emerges at scale
4. ⚖️ Multidimensional Optimization - N-dimensional trade-offs
5. 🧠 Distributed Knowledge - Partial knowledge everywhere
6. 🤯 Cognitive Load - Human capacity limits
7. 💰 Economic Reality - Everything has a cost

## Notes
- The new structure is more advanced and philosophical
- Focus on laws rather than simple observations
- Each axiom now has deeper theoretical foundations
- Emphasis on emergence and correlation, not just individual constraints
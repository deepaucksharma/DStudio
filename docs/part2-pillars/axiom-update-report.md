# Pillars Section Review: Axiom Framework Update Report

## Overview
This report documents the review of the pillars section to ensure proper references to the new axiom framework (7 laws) instead of the old 8-axiom structure.

## Key Findings

### 1. Main Pillars Index (`/part2-pillars/index.md`)
**Status**: ❌ **Needs Updates**

The file still references 8 axioms and uses the old naming convention:
- Line 37-45: Lists 8 axioms with old names
- Line 62: "A8 [Economics]" in diagram
- Line 79: References all 8 axioms
- Line 162-167: Links to old axiom paths and names
- Line 339: References "8 Fundamental Axioms"

**Required Changes**:
- Update to 7 laws with new names
- Update all axiom links to use new paths
- Update diagram to remove Economics axiom

### 2. Pillar 1: Work Distribution (`/work/index.md`)
**Status**: ❌ **Needs Updates**

References old axiom structure:
- Line 21: Links to "Axiom 4: Concurrency"
- Line 51: References "Axiom 8: Economics"
- Line 57: References "Axiom 5: Coordination"
- Line 134-138: Links to Axioms 1-5 in diagram
- Line 178: Links to "Axiom 1: Latency"
- Line 219: Links to "Axiom 4: Concurrency"
- Line 344: References "Axiom 5: Coordination"
- Line 597: References "Axiom 2: Capacity"
- Line 1967-1972: Links to axioms in resources section

### 3. Pillar 2: State Distribution (`/state/index.md`)
**Status**: ❌ **Needs Updates**

References old axiom structure:
- Line 37: Links to "Axiom 2: Capacity"
- Line 37: Links to "Axiom 3: Failure"

### 4. Pillar 3: Truth Distribution (`/truth/index.md`)
**Status**: ❌ **Needs Updates**

References old axiom structure:
- Line 23: Links to "Axiom 3: Failure"
- Line 23: Links to "Axiom 5: Coordination"
- Prerequisites list "axiom4-concurrency" and "axiom5-coordination"

### 5. Pillar 4: Control Distribution (`/control/index.md`)
**Status**: ❌ **Needs Updates**

Prerequisites list old axiom names:
- "axiom3-failure"
- "axiom6-observability"
- "axiom7-human"

### 6. Pillar 5: Intelligence Distribution (`/intelligence/index.md`)
**Status**: ❌ **Needs Updates**

Prerequisites list old axiom names:
- "axiom6-observability"
- "axiom7-human"
- "axiom8-economics"

## Summary of Required Updates

### 1. Axiom Name Mapping
Old → New mapping needed:
- Axiom 1: Latency → Law 1: Speed of Light
- Axiom 2: Capacity → Law 2: Conservation
- Axiom 3: Failure → Law 3: Entropy
- Axiom 4: Concurrency → Law 4: Simultaneity
- Axiom 5: Coordination → Law 5: Consensus Cost
- Axiom 6: Observability → Law 6: Information Uncertainty
- Axiom 7: Human Interface → Law 7: Human Bandwidth
- Axiom 8: Economics → (Removed - integrated into other laws)

### 2. Path Updates
All axiom links need to be updated from:
- `../../part1-axioms/axiomN-name/index.md`
to:
- `../../part1-axioms/lawN-name/index.md`

### 3. Content Updates
- Remove all references to the 8th axiom (Economics)
- Update axiom counts from 8 to 7
- Update axiom names to use "Law" instead of "Axiom"
- Update prerequisite lists to use new law identifiers

### 4. Diagram Updates
Several Mermaid diagrams need updating:
- Remove Economics (A8) nodes
- Update axiom labels to law labels
- Update connections that reference removed axiom

## Recommended Action Plan

1. **Update Main Pillars Index** - Primary changes to axiom listing and counts
2. **Update Individual Pillar Files** - Fix all axiom references and links
3. **Update Prerequisites** - Change axiom identifiers to law identifiers
4. **Update Diagrams** - Remove Economics, update labels
5. **Verify Cross-References** - Ensure all pillar-to-axiom links are correct

## Impact Assessment

- **High Impact**: Main pillars index has extensive axiom references
- **Medium Impact**: Individual pillar files have scattered references
- **Low Impact**: Most content focuses on pillar concepts rather than axioms

The updates are primarily mechanical (find/replace) but require careful attention to:
- Correct law numbers
- Proper path structures
- Maintaining semantic accuracy when Economics axiom is removed
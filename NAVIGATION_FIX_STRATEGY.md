# Navigation Fix Strategy

## Current Situation Analysis

### What We Know:
1. **Basic links fixed**: 850+ simple broken links were fixed
2. **Structural issues remain**: Navigation architecture is fundamentally broken
3. **User impact**: Users can't discover related content effectively

### Root Causes:
1. **Path inconsistency**: Multiple ways to reference same content
2. **Missing bidirectional links**: One-way references break discovery
3. **No navigation standard**: Each file uses different reference patterns

## Correct Navigation Structure

### 1. Laws (7 Fundamental Laws)
**Canonical Path**: `/core-principles/laws/[law-slug]/`

**Correct Slugs**:
- Law 1: `correlated-failure` (NOT law1-failure)
- Law 2: `asynchronous-reality` (NOT law2-asynchrony)
- Law 3: `emergent-chaos` (NOT law3-chaos)
- Law 4: `multidimensional-optimization` (NOT law4-tradeoffs)
- Law 5: `distributed-knowledge` (NOT law5-epistemology)
- Law 6: `cognitive-load` (NOT law6-load)
- Law 7: `economic-reality` (NOT law7-economics)

### 2. Pillars (5 Foundational Pillars)
**Canonical Path**: `/core-principles/pillars/[pillar-slug]/`

**Correct Slugs**:
- Pillar 1: `work-distribution`
- Pillar 2: `state-distribution`
- Pillar 3: `truth-distribution`
- Pillar 4: `control-distribution`
- Pillar 5: `intelligence-distribution`

### 3. Patterns
**Canonical Path**: `/pattern-library/[category]/[pattern-slug]/`

**Categories**:
- `architecture`
- `communication`
- `coordination`
- `data-management`
- `resilience`
- `scaling`

### 4. Link Reference Patterns

#### From Pattern Library Files:
```markdown
- To laws: [Law Name](../../core-principles/laws/[slug]/)
- To pillars: [Pillar Name](../../core-principles/pillars/[slug]/)
- To other patterns: [Pattern Name](../[category]/[slug]/)
- To case studies: [Case Study](../../architects-handbook/case-studies/[category]/[slug]/)
```

#### From Core Principles Files:
```markdown
- To patterns: [Pattern Name](../../pattern-library/[category]/[slug]/)
- To case studies: [Case Study](../../architects-handbook/case-studies/[category]/[slug]/)
- Between laws/pillars: [Name](../laws/[slug]/) or [Name](../pillars/[slug]/)
```

#### From Architects Handbook:
```markdown
- To laws: [Law Name](../../core-principles/laws/[slug]/)
- To patterns: [Pattern Name](../../pattern-library/[category]/[slug]/)
```

## Implementation Strategy

### Phase 1: Critical Path Fixes (Immediate)
1. **Fix all law references** using correct slugs
2. **Standardize pillar references**
3. **Fix learning path navigation** (high user impact)

### Phase 2: Bidirectional Links (This Week)
1. **Laws → Patterns**: Add "Patterns Implementing This Law" sections
2. **Patterns → Case Studies**: Add "Real-World Implementations" sections
3. **Case Studies → Patterns**: Add "Pattern Analysis" sections

### Phase 3: Cross-References (Next Week)
1. **Pattern → Pattern**: Related patterns sections
2. **Law → Law**: Relationship explanations
3. **Pillar → Law**: Foundational connections

## Validation Approach

### 1. Path Validation
- Every link must resolve to an actual file
- Use consistent relative paths
- No absolute paths or shortcuts

### 2. Bidirectional Validation
For every A→B link, ensure B→A exists:
- Pattern mentions Law? Law must mention Pattern
- Case Study analyzes Pattern? Pattern must reference Case Study

### 3. User Journey Testing
Test common paths:
- Learning Path → Law → Pattern → Case Study
- Pattern → Related Pattern → Implementation
- Case Study → Pattern → Law → Related Law

## Success Metrics

1. **Zero 404s**: All navigation links resolve
2. **100% Bidirectional**: Every reference has a return path
3. **Consistent Paths**: Same reference style throughout
4. **Discoverable**: Users can find related content from any entry point

## Next Steps

1. **Create validation script** that checks all above rules
2. **Fix systematically** by category, not randomly
3. **Test user journeys** after each phase
4. **Document standards** for future contributors
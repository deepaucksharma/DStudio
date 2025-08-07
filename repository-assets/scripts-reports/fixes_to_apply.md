# Documentation Issues and Fixes
Generated: 2025-08-07T04:22:15.045037

## Summary

- Total pages: 640
- Pages with issues: 578 (90.3%)
- Total issues: 8292
- Auto-fixable issues: 3

## Issues by Severity

### ERROR: 5885 issues

- **broken_internal_link**: 5866 occurrences
- **unclosed_code_block**: 19 occurrences

### WARNING: 1548 issues

- **duplicate_heading_anchor**: 694 occurrences
- **heading_hierarchy_skip**: 470 occurrences
- **short_content**: 162 occurrences
- **placeholder_content**: 104 occurrences
- **invalid_frontmatter**: 78 occurrences
- **broken_external_link**: 26 occurrences
- **broken_anchor_link**: 12 occurrences
- **empty_link_text**: 2 occurrences (🤖 2 auto-fixable)

### INFO: 617 issues

- **long_code_block**: 323 occurrences
- **long_content**: 210 occurrences
- **heading_hierarchy_skip**: 45 occurrences
- **todo_marker**: 38 occurrences
- **insecure_http_link**: 1 occurrences (🤖 1 auto-fixable)

## Detailed Fixes

### duplicate_heading_anchor (232 occurrences)

**Severity**: low

**Example**: Duplicate anchor: focus-areas from heading "Focus Areas"

**Fix**: Make heading unique or use explicit anchor

**Sample pages affected**:
- `pattern-library/pattern-synthesis-guide`
- `pattern-library/visual-asset-creation-plan`
- `pattern-library/pattern-relationship-map`

### heading_hierarchy_skip (10 occurrences)

**Severity**: low

**Example**: Heading level jumps from H1 to H4

**Fix**: Use sequential heading levels

**Sample pages affected**:
- `pattern-library/architecture/event-driven`
- `pattern-library/architecture/backends-for-frontends`
- `pattern-library/architecture/valet-key`

### broken_internal_link (5866 occurrences)

**Severity**: error

**Example**: Link to non-existent page: /architects-handbook/human-factors/incident-response/

**Fix**: Create page architects-handbook/human-factors/incident-response/index.md or fix the link

**Sample pages affected**:
- `incident-response`
- `monolith-to-microservices`
- `latency-calculator`

### unclosed_code_block (19 occurrences)

**Severity**: error

**Example**: Odd number of ``` markers

**Fix**: Close all code blocks

**Sample pages affected**:
- `architects-handbook/QUALITY_IMPLEMENTATION_GUIDE`
- `architects-handbook/case-studies/social-communication/notification-system`
- `architects-handbook/case-studies/monitoring-observability/rate-limiter`

### duplicate_heading_anchor (694 occurrences)

**Severity**: warning

**Example**: Duplicate anchor: focus-areas from heading "Focus Areas"

**Fix**: Make heading unique or use explicit anchor

**Sample pages affected**:
- `interview-prep/ic-interviews/behavioral/by-level`
- `interview-prep/engineering-leadership/company-specific/microsoft/index`
- `interview-prep/engineering-leadership/level-1-first-principles/decision-making/index`

### heading_hierarchy_skip (470 occurrences)

**Severity**: warning

**Example**: Heading level jumps from H1 to H4

**Fix**: Use sequential heading levels

**Sample pages affected**:
- `CALCULATOR_VALIDATION_TESTING_PLAN`
- `interview-prep/engineering-leadership/hard-earned-wisdom/crisis-leadership-reality`
- `interview-prep/engineering-leadership/level-1-first-principles/value-creation/index`

### short_content (162 occurrences)

**Severity**: warning

**Example**: Only 34 words

**Fix**: Add more content or consider merging with another page

**Sample pages affected**:
- `incident-response`
- `human-factors`
- `monolith-to-microservices`

### placeholder_content (104 occurrences)

**Severity**: warning

**Example**: Found placeholder text: coming soon

**Fix**: Replace with actual content

**Sample pages affected**:
- `interview-prep/ic-interviews/cheatsheets/system-design-checklist/index`
- `interview-prep/ic-interviews/behavioral/index`
- `interview-prep/ic-interviews/common-problems/index`

### invalid_frontmatter (78 occurrences)

**Severity**: warning

**Example**: Failed to parse YAML frontmatter

**Fix**: Check YAML syntax in frontmatter

**Sample pages affected**:
- `interview-prep/ic-interviews/cheatsheets/system-design-checklist`
- `interview-prep/ic-interviews/behavioral/by-level`
- `interview-prep/ic-interviews/behavioral/scenarios`

### broken_external_link (26 occurrences)

**Severity**: warning

**Example**: External link unreachable: http://lambda-architecture.net/ (status: None)

**Fix**: Update or remove the broken link

**Sample pages affected**:
- `architects-handbook/case-studies/financial-commerce/ad-click-aggregation`
- `architects-handbook/case-studies/financial-commerce/stock-exchange`
- `architects-handbook/learning-paths/data-engineer`

### broken_anchor_link (12 occurrences)

**Severity**: warning

**Example**: Anchor #one-week-prep not found in interview-prep/engineering-leadership/navigation-guide

**Fix**: Add heading with anchor one-week-prep or fix the link

**Sample pages affected**:
- `interview-prep/ENGINEERING_LEADERSHIP_INTERVIEW_FRAMEWORK`
- `interview-prep/engineering-leadership/FRAMEWORK_ORGANIZATION`
- `interview-prep/engineering-leadership/navigation-guide`

### empty_link_text (2 occurrences)

**Severity**: warning

**Example**: Empty link text for URL: const LogRecord& a, const LogRecord& b

**Fix**: Add descriptive link text

**Sample pages affected**:
- `architects-handbook/case-studies/databases/amazon-aurora`
- `architects-handbook/case-studies/elite-engineering/figma-crdt-collaboration`

### long_code_block (323 occurrences)

**Severity**: info

**Example**: plain code block with 300 lines

**Fix**: Consider moving to separate file or splitting

**Sample pages affected**:
- `interview-prep/ic-interviews/cheatsheets/system-design-checklist`
- `architects-handbook/human-factors/security-incident-response`
- `architects-handbook/human-factors/disaster-recovery-planning`

### long_content (210 occurrences)

**Severity**: info

**Example**: 4067 words

**Fix**: Consider splitting into multiple pages

**Sample pages affected**:
- `interview-prep/engineering-leadership/hard-earned-wisdom/performance-management-reality`
- `interview-prep/engineering-leadership/hard-earned-wisdom/organizational-politics-mastery`
- `interview-prep/engineering-leadership/hard-earned-wisdom/human-cost-leadership`

### heading_hierarchy_skip (45 occurrences)

**Severity**: info

**Example**: Heading level jumps from H1 to H4

**Fix**: Use sequential heading levels

**Sample pages affected**:
- `company-specific/apple/index`
- `pattern-library/pattern-antipatterns-guide`
- `pattern-library/architecture/anti-corruption-layer`

### todo_marker (38 occurrences)

**Severity**: info

**Example**: hack: days where I code alongside the team

**Fix**: Address TODO item or move to issue tracker

**Sample pages affected**:
- `interview-prep/engineering-leadership/level-3-applications/technical-leadership/technical-strategy`
- `interview-prep/engineering-leadership/level-4-interview-execution/tools/mock-interview-guide`
- `interview-prep/engineering-leadership/level-4-interview-execution/tools/principle-hooks/index`

### insecure_http_link (1 occurrences)

**Severity**: info

**Example**: HTTP link (not HTTPS): http://lambda-architecture.net/

**Fix**: Consider using HTTPS

**Sample pages affected**:
- `architects-handbook/case-studies/financial-commerce/ad-click-aggregation`

## Pages Needing Most Attention

- **Request Batching/Pipelining** (`pattern-library/scaling/request-batching`): Quality 0/100, 78 issues
- **Deduplication** (`pattern-library/data-management/deduplication`): Quality 44/100, 44 issues
- **Common Algorithm Patterns** (`interview-prep/coding-interviews/algorithm-patterns`): Quality 46/100, 37 issues
- **Valet Key Pattern** (`pattern-library/architecture/valet-key`): Quality 47/100, 42 issues
- **Lambda Architecture** (`pattern-library/architecture/lambda-architecture`): Quality 49/100, 34 issues
- **Strangler Fig** (`pattern-library/architecture/strangler-fig`): Quality 49/100, 38 issues
- **Leader-Follower Pattern** (`pattern-library/coordination/leader-follower`): Quality 49/100, 48 issues
- **Logical Clocks (Lamport Clocks)** (`pattern-library/coordination/logical-clocks`): Quality 49/100, 39 issues
- **Engineering Leadership Levels Across Tech Companies** (`interview-prep/engineering-leadership/level-specific/level-expectations`): Quality 50/100, 22 issues
- **Pattern Combination Recipes - Proven Architectural Stacks** (`pattern-library/pattern-combination-recipes`): Quality 61/100, 26 issues
- **Pattern Relationship Map - Visual Guide to Pattern Connections** (`pattern-library/pattern-relationship-map`): Quality 61/100, 26 issues
- **Runbooks & Playbooks** (`architects-handbook/human-factors/runbooks-playbooks`): Quality 63/100, 24 issues
- **Scatter-Gather** (`pattern-library/scaling/scatter-gather`): Quality 64/100, 24 issues
- **Pattern Anti-Patterns Guide - What Not to Do** (`pattern-library/pattern-antipatterns-guide`): Quality 68/100, 26 issues
- **Structured Learning Path Template** (`architects-handbook/templates/structured-learning-path-example`): Quality 70/100, 47 issues
- **Law 2: The Law of Asynchronous Reality** (`core-principles/laws/asynchronous-reality`): Quality 73/100, 13 issues
- **Law 1: The Law of Inevitable and Correlated Failure** (`core-principles/laws/correlated-failure`): Quality 74/100, 32 issues
- **Digital Wallet System** (`architects-handbook/case-studies/financial-commerce/digital-wallet-enhanced`): Quality 76/100, 36 issues
- **Pattern Implementation Roadmap - Your Path to Distributed Systems Mastery** (`pattern-library/pattern-implementation-roadmap`): Quality 76/100, 42 issues
- **Information Theory** (`architects-handbook/quantitative-analysis/information-theory`): Quality 77/100, 14 issues

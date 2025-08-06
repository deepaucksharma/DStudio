# Documentation Issues and Fixes
Generated: 2025-08-06T16:02:27.035788

## Summary

- Total pages: 627
- Pages with issues: 579 (92.3%)
- Total issues: 5931
- Auto-fixable issues: 3

## Issues by Severity

### ERROR: 4591 issues

- **broken_internal_link**: 4573 occurrences
- **unclosed_code_block**: 18 occurrences

### WARNING: 577 issues

- **duplicate_heading_anchor**: 332 occurrences
- **placeholder_content**: 103 occurrences
- **short_content**: 84 occurrences
- **invalid_frontmatter**: 52 occurrences
- **broken_external_link**: 4 occurrences
- **empty_link_text**: 2 occurrences (🤖 2 auto-fixable)

### INFO: 763 issues

- **heading_hierarchy_skip**: 480 occurrences
- **long_code_block**: 153 occurrences
- **long_content**: 93 occurrences
- **todo_marker**: 36 occurrences
- **insecure_http_link**: 1 occurrences (🤖 1 auto-fixable)

## Detailed Fixes

### broken_internal_link (4573 occurrences)

**Severity**: error

**Example**: Link to non-existent page: /architects-handbook/human-factors/incident-response/

**Fix**: Create page architects-handbook/human-factors/incident-response/index.md or fix the link

**Sample pages affected**:
- `incident-response`
- `index`
- `human-factors`

### unclosed_code_block (18 occurrences)

**Severity**: error

**Example**: Odd number of ``` markers

**Fix**: Close all code blocks

**Sample pages affected**:
- `architects-handbook/QUALITY_IMPLEMENTATION_GUIDE`
- `architects-handbook/case-studies/social-communication/notification-system`
- `architects-handbook/case-studies/monitoring-observability/rate-limiter`

### duplicate_heading_anchor (332 occurrences)

**Severity**: warning

**Example**: Duplicate anchor: focus-areas from heading "Focus Areas"

**Fix**: Make heading unique or use explicit anchor

**Sample pages affected**:
- `interview-prep/ic-interviews/behavioral/by-level`
- `interview-prep/engineering-leadership/company-specific/microsoft/index`
- `interview-prep/engineering-leadership/level-1-first-principles/decision-making/index`

### placeholder_content (103 occurrences)

**Severity**: warning

**Example**: Found placeholder text: coming soon

**Fix**: Replace with actual content

**Sample pages affected**:
- `interview-prep/ic-interviews/cheatsheets/system-design-checklist/index`
- `interview-prep/ic-interviews/behavioral/index`
- `interview-prep/ic-interviews/common-problems/index`

### short_content (84 occurrences)

**Severity**: warning

**Example**: Only 34 words

**Fix**: Add more content or consider merging with another page

**Sample pages affected**:
- `incident-response`
- `human-factors`
- `monolith-to-microservices`

### invalid_frontmatter (52 occurrences)

**Severity**: warning

**Example**: Failed to parse YAML frontmatter

**Fix**: Check YAML syntax in frontmatter

**Sample pages affected**:
- `interview-prep/ic-interviews/cheatsheets/system-design-checklist`
- `interview-prep/ic-interviews/behavioral/by-level`
- `interview-prep/ic-interviews/behavioral/scenarios`

### broken_external_link (4 occurrences)

**Severity**: warning

**Example**: External link unreachable: http://lambda-architecture.net/ (status: None)

**Fix**: Update or remove the broken link

**Sample pages affected**:
- `architects-handbook/case-studies/financial-commerce/ad-click-aggregation`
- `architects-handbook/case-studies/financial-commerce/stock-exchange`

### empty_link_text (2 occurrences)

**Severity**: warning

**Example**: Empty link text for URL: const LogRecord& a, const LogRecord& b

**Fix**: Add descriptive link text

**Sample pages affected**:
- `architects-handbook/case-studies/databases/amazon-aurora`
- `architects-handbook/case-studies/elite-engineering/figma-crdt-collaboration`

### heading_hierarchy_skip (480 occurrences)

**Severity**: info

**Example**: Heading level jumps from H1 to H4

**Fix**: Use sequential heading levels

**Sample pages affected**:
- `CALCULATOR_VALIDATION_TESTING_PLAN`
- `interview-prep/engineering-leadership/hard-earned-wisdom/crisis-leadership-reality`
- `interview-prep/engineering-leadership/level-1-first-principles/value-creation/index`

### long_code_block (153 occurrences)

**Severity**: info

**Example**: plain code block with 300 lines

**Fix**: Consider moving to separate file or splitting

**Sample pages affected**:
- `interview-prep/ic-interviews/cheatsheets/system-design-checklist`
- `architects-handbook/human-factors/security-incident-response`
- `architects-handbook/human-factors/disaster-recovery-planning`

### long_content (93 occurrences)

**Severity**: info

**Example**: 4067 words

**Fix**: Consider splitting into multiple pages

**Sample pages affected**:
- `interview-prep/engineering-leadership/hard-earned-wisdom/performance-management-reality`
- `interview-prep/engineering-leadership/hard-earned-wisdom/organizational-politics-mastery`
- `interview-prep/engineering-leadership/hard-earned-wisdom/human-cost-leadership`

### todo_marker (36 occurrences)

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

- **Request Batching/Pipelining** (`pattern-library/scaling/request-batching`): Quality 0/100, 45 issues
- **Deduplication** (`pattern-library/data-management/deduplication`): Quality 44/100, 22 issues
- **Common Algorithm Patterns** (`interview-prep/coding-interviews/algorithm-patterns`): Quality 45/100, 19 issues
- **Leader-Follower Pattern** (`pattern-library/coordination/leader-follower`): Quality 45/100, 27 issues
- **Valet Key Pattern** (`pattern-library/architecture/valet-key`): Quality 47/100, 25 issues
- **Logical Clocks (Lamport Clocks)** (`pattern-library/coordination/logical-clocks`): Quality 47/100, 25 issues
- **Lambda Architecture** (`pattern-library/architecture/lambda-architecture`): Quality 49/100, 17 issues
- **Strangler Fig** (`pattern-library/architecture/strangler-fig`): Quality 49/100, 25 issues
- **Digital Wallet System** (`architects-handbook/case-studies/financial-commerce/digital-wallet-enhanced`): Quality 56/100, 23 issues
- **Quick Start Guide: From Zero to Production Excellence** (`excellence/implementation-guides/quick-start-guide`): Quality 57/100, 19 issues
- **Quality Assurance Implementation Guide** (`architects-handbook/QUALITY_IMPLEMENTATION_GUIDE`): Quality 60/100, 16 issues
- **Pattern Anti-Patterns Guide - What Not to Do** (`pattern-library/pattern-antipatterns-guide`): Quality 60/100, 15 issues
- **Pattern Combination Recipes - Proven Architectural Stacks** (`pattern-library/pattern-combination-recipes`): Quality 61/100, 13 issues
- **Pattern Relationship Map - Visual Guide to Pattern Connections** (`pattern-library/pattern-relationship-map`): Quality 61/100, 13 issues
- **Runbooks & Playbooks** (`architects-handbook/human-factors/runbooks-playbooks`): Quality 63/100, 13 issues
- **Scatter-Gather** (`pattern-library/scaling/scatter-gather`): Quality 64/100, 16 issues
- **Search Autocomplete System Design** (`architects-handbook/case-studies/search-analytics/search-autocomplete`): Quality 66/100, 39 issues
- **S3-like Object Storage System** (`architects-handbook/case-studies/infrastructure/s3-object-storage-enhanced`): Quality 68/100, 18 issues
- **Gaming Leaderboard System** (`architects-handbook/case-studies/search-analytics/gaming-leaderboard-enhanced`): Quality 68/100, 18 issues
- **Distributed Notification System** (`architects-handbook/case-studies/social-communication/notification-system`): Quality 68/100, 33 issues

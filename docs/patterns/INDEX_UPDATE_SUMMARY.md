# Pattern Index Update Summary

## Changes Made

### Main Updates
1. **Updated pattern count** from "119+" to "~95" patterns across both index.md and index-new.md
2. **Added curation note** explaining focus on practical, battle-tested solutions
3. **Removed references to archived patterns**:
   - Removed timeout.md and health-check.md from pattern tables
   - Replaced two-phase-commit references with saga pattern
   - Replaced vector-clocks references with logical-clocks
   - Removed references to meta-pattern files (quiz, comparison, combinations, selector)
   - Removed other archived patterns (gossip-protocol, merkle-trees, etc.)

### Specific Replacements
- Pattern Selector Tool link: Fixed to use `pattern-selector-tool.md` instead of `pattern-selector.md`
- Pattern Quiz: Redirected to Progress Tracker section
- Pattern Combinations: Redirected to Advanced Path section
- Health Check/Timeout: Replaced with Circuit Breaker/Retry in examples
- Two-Phase Commit: Replaced with Saga pattern throughout
- Vector Clocks: Replaced with Logical Clocks
- Anti-Entropy: Replaced with Read Repair

### Learning Path Updates
- Removed Timeout and Health Check from foundation patterns
- Added Observability as a foundation pattern
- Updated Week 1 resilience patterns to focus on Retry, Circuit Breaker, Rate Limiting, and Bulkhead
- Changed "Distributed transactions" to "Distributed workflows" for Saga pattern

### Navigation Updates
- Pattern Navigator replaces Pattern Selector Tool in quick navigation
- Removed links to archived meta-pattern files
- Added GitHub discussions link for community

## Result
Both index files now accurately reflect the curated set of ~95 high-value patterns, with all references to archived patterns removed or updated to point to appropriate alternatives.
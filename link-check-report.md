# Link Check Report for /docs/part1-axioms/ and /docs/part2-pillars/

**Date**: 2025-07-21  
**Scope**: All markdown files in `/docs/part1-axioms/` and `/docs/part2-pillars/` directories

## Summary

After scanning all files in the specified directories, I found the following issues:

## Missing Files (Broken Links)

### 1. Missing Pattern Files
- **`/docs/patterns/two-phase-commit.md`** - Referenced in:
  - `/docs/part1-axioms/axiom5-coordination/examples.md`
  - `/docs/part1-axioms/axiom5-coordination/exercises.md`

- **`/docs/patterns/api-gateway.md`** - Referenced in:
  - `/docs/part1-axioms/axiom7-human/exercises.md`

- **`/docs/patterns/multi-region.md`** - Referenced in:
  - `/docs/part1-axioms/axiom8-economics/exercises.md`

### 2. Missing Case Study Files
- **`/docs/case-studies/netflix-cdn.md`** - Referenced in:
  - `/docs/part1-axioms/axiom1-latency/examples.md`

### 3. Cross-Reference Issues

Several relative path references appear to be incorrect due to directory structure:
- Links using `../index.md` from index files would incorrectly go up one level too many
- Some files have incorrect relative paths that need adjustment based on their location

## Verified Existing Files

The following files were verified to exist:
- `/docs/case-studies/uber-location.md` ✓
- `/docs/case-studies/spotify-recommendations.md` ✓
- `/docs/case-studies/amazon-dynamo.md` ✓
- All other pattern files referenced (circuit-breaker, retry-backoff, bulkhead, etc.) ✓
- All quantitative files referenced ✓
- All human-factors files referenced ✓

## Additional Observations

1. **Extra Files**: Found `index-enhanced.md` in `/docs/part1-axioms/axiom1-latency/` which appears to be an enhanced version but is not linked from anywhere.

2. **External Links**: All external links (starting with https://) were not checked but appear properly formatted.

3. **Directory Structure**: The directory structure is consistent with:
   - Each axiom having its own directory with `index.md`, `examples.md`, and `exercises.md`
   - Each pillar having its own directory with the same structure
   - Supporting directories for patterns, case-studies, quantitative, human-factors, and tools

## Recommendations

1. **Create Missing Files**:
   - Add `/docs/patterns/two-phase-commit.md`
   - Add `/docs/patterns/api-gateway.md`
   - Add `/docs/patterns/multi-region.md`
   - Add `/docs/case-studies/netflix-cdn.md`

2. **Fix Relative Paths**: Review and fix relative path references, especially those using `../index.md` from index files.

3. **Consider**: Either integrate or remove the `index-enhanced.md` file in the axiom1-latency directory.

## File Count Summary

- **Part 1 Axioms**: 27 markdown files
- **Part 2 Pillars**: 30 markdown files
- **Total Scanned**: 57 files
- **Broken Links Found**: 4 unique missing files
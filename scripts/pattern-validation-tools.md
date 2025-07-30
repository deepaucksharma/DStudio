# Pattern Validation Tools

This directory contains tools for validating pattern content quality based on the Pattern Execution Plan requirements.

## Tools Overview

### 1. `pattern_validator.py` - Content Quality Validator
Validates pattern content against quality standards:
- Essential question presence
- Line count ≤ 1000
- "When NOT to use" position < 200 lines
- Template section compliance
- Code percentage < 20%
- Minimum 3 diagrams
- Decision matrix presence

### 2. `pattern-validator-metadata.py` - Metadata Validator
Validates pattern metadata (excellence framework):
- Required front matter fields
- Tier-specific requirements
- Valid enum values

### 3. `validate_all_patterns.py` - Batch Validator
Orchestrates both validators across all patterns and generates comprehensive reports.

### 4. `quick_pattern_check.sh` - CI/CD Quick Check
Fast validation script suitable for pre-commit hooks or CI/CD pipelines.

## Usage Examples

### Validate a Single Pattern
```bash
# Content validation
python3 scripts/pattern_validator.py --pattern circuit-breaker

# With specific directory
python3 scripts/pattern_validator.py --dir docs/pattern-library/resilience --pattern circuit-breaker
```

### Validate All Patterns
```bash
# Full validation with both content and metadata
python3 scripts/validate_all_patterns.py

# Content validation only
python3 scripts/validate_all_patterns.py --skip-metadata

# Generate JSON report
python3 scripts/pattern_validator.py --dir docs/pattern-library --format json --output validation.json
```

### Quick CI/CD Check
```bash
# Returns 0 if all pass, 1 if any fail
./scripts/quick_pattern_check.sh
```

## Report Formats

### Markdown Report (Default)
- Human-readable format
- Shows failed patterns with specific issues
- Includes metrics and statistics
- Lists perfect patterns

### JSON Report
- Machine-readable format
- Detailed metrics for each pattern
- Suitable for programmatic analysis
- Can be used for tracking progress

## Validation Criteria

### 1. Essential Question (Required)
- Must be present in content
- Should also be in front matter
- Clear, one-line problem statement

### 2. Line Count (Max: 1000)
- Total file lines should not exceed 1000
- Warning issued at 900 lines

### 3. "When NOT to Use" Position (Max: 200 lines)
- Must appear within first 200 lines
- Critical for quick decision making

### 4. Template Sections (Required)
All patterns must include:
- Essential Question
- When to Use / When NOT to Use
- Level 1: Intuition (5 min)
- Level 2: Foundation (10 min)
- Level 3: Deep Dive (15 min)
- Level 4: Expert (20 min)
- Level 5: Mastery (30 min)
- Quick Reference

### 5. Code Percentage (Max: 20%)
- Code blocks should be < 20% of content
- Prefer diagrams and concepts over implementation

### 6. Diagram Count (Min: 3)
- At least 3 Mermaid diagrams
- Visual explanation is prioritized

### 7. Decision Matrix (Required)
- Comparison table or decision criteria
- Helps users make informed choices

## Output Examples

### Failed Pattern Output
```
### circuit-breaker
**File**: `docs/pattern-library/resilience/circuit-breaker.md`
**Issues**: 2

- ❌ **code_percentage**: Code makes up 46.5% of content (max: 20%)
- ❌ **decision_matrix**: No decision matrix/comparison table found

**Metrics**:
- Total lines: 473
- Code lines: 220 (46.5%)
- Diagrams: 8
- Tables: 49
```

### Summary Statistics
```
## Summary
- **Total Patterns**: 91
- **Passed**: 45 (49.5%)
- **Failed**: 46
- **Total Issues**: 184
- **Total Warnings**: 23

## Issue Distribution
| Check | Count | Percentage |
|-------|-------|------------|
| template_sections | 78 | 85.7% |
| decision_matrix | 42 | 46.2% |
| code_percentage | 35 | 38.5% |
| when_not_position | 29 | 31.9% |
```

## Integration with Development Workflow

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
./scripts/quick_pattern_check.sh || exit 1
```

### GitHub Actions
```yaml
- name: Validate Patterns
  run: |
    pip install -r requirements.txt
    python3 scripts/pattern_validator.py --dir docs/pattern-library
```

### VS Code Task
Add to `.vscode/tasks.json`:
```json
{
    "label": "Validate Current Pattern",
    "type": "shell",
    "command": "python3",
    "args": [
        "${workspaceFolder}/scripts/pattern_validator.py",
        "--pattern",
        "${fileBasenameNoExtension}"
    ]
}
```

## Fixing Common Issues

### Code Percentage Too High
- Move implementation details to external links
- Replace code with diagrams
- Focus on concepts over implementation

### Missing Essential Question
- Add clear problem statement at top
- Include in front matter
- Make it scannable and direct

### Missing Decision Matrix
- Add comparison table
- Include "When to use vs When not to use"
- Provide clear selection criteria

### Line Count Too High
- Split into separate focused pages
- Move examples to appendix
- Remove verbose explanations

## Progress Tracking

Use JSON output to track improvement over time:
```bash
# Generate baseline
python3 scripts/pattern_validator.py --format json --output baseline.json

# After improvements
python3 scripts/pattern_validator.py --format json --output improved.json

# Compare results
jq -r '.summary' baseline.json improved.json
```
# Documentation Validation Scripts

## Philosophy: First Principles Approach

For MkDocs-based sites, validation should follow a simple principle:

**If MkDocs can build successfully with `--strict` mode, the navigation and links are valid.**

Everything else is about content quality and consistency.

## Primary Validation

### `mkdocs-validator.py`
- **Purpose**: Comprehensive MkDocs validation
- **What it does**:
  1. Runs `mkdocs build --strict` to catch all navigation/link errors
  2. Parses mkdocs.yml to validate file references
  3. Finds orphaned files not in navigation
  4. Checks for common problematic patterns
- **Usage**: `python3 scripts/mkdocs-validator.py`

## Content Quality Checks

### `deep-structure-analyzer.py`
- **Purpose**: Analyze documentation structure for consistency issues
- **Checks**: Frontmatter consistency, law references, path patterns, mkdocs alignment
- **Output**: DEEP_STRUCTURE_ISSUES.json

### `validate-frontmatter.py`
- **Purpose**: Ensure consistent frontmatter format
- **Checks**: Required fields, key naming conventions, valid enum values

### `validate-law-references.py`
- **Purpose**: Validate law references use correct naming
- **Checks**: Old law patterns (law1-failure) vs new (correlated-failure)

### `validate-paths.py`
- **Purpose**: Check for outdated path references
- **Checks**: Old structure references like /part1-axioms/, /patterns/ vs /pattern-library/

### `check-broken-links.py`
- **Purpose**: Find broken internal links
- **Note**: Redundant with mkdocs --strict but provides more detail

## CI/CD Integration

The GitHub Actions workflow runs validations in three groups:

1. **Primary Validation** (mkdocs-validation job)
   - Must pass for deployment
   - Uses mkdocs-validator.py

2. **Deep Structure Analysis** (deep-structure-analysis job)
   - Informational, continues on error
   - Generates detailed reports

3. **Content Quality Checks** (content-quality-checks job)
   - Informational, continues on error
   - Multiple specific validators

## Local Development

For pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

This will run basic validations before each commit.

## Key Insight

MkDocs with Material theme already has excellent link validation built-in. Rather than reimplementing this, we leverage `mkdocs build --strict` as the source of truth for navigation and link validity. Additional validators focus on content quality and consistency that MkDocs doesn't check.
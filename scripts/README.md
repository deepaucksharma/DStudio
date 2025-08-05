# Scripts Directory

This directory contains utility scripts for the DStudio documentation project.

## Validation Scripts (Primary)

These are the core validation scripts used in CI/CD:

- **`mkdocs-validator.py`** - Primary validation using MkDocs build --strict
- **`deep-structure-analyzer.py`** - Deep analysis of documentation structure
- **`validate-frontmatter.py`** - Validates frontmatter consistency
- **`validate-law-references.py`** - Validates law naming conventions
- **`validate-paths.py`** - Checks for outdated path references
- **`check-broken-links.py`** - Detailed broken link analysis

See `README-validation.md` for detailed documentation on the validation approach.

## Pattern Management

- **`pattern-manager.py`** - Interactive pattern management tool
- **`comprehensive_metadata_summary.py`** - Pattern metadata analysis

## Content Enhancement

- **`extract_mermaid_diagrams.py`** - Extract Mermaid diagrams from markdown
- **`render_mermaid_diagrams.py`** - Render Mermaid diagrams to images
- **`replace_mermaid_blocks.py`** - Replace Mermaid blocks with rendered images
- **`monitor_diagram_conversion.py`** - Monitor diagram conversion progress

## Template Management

- **`template_v2_transformer_enhanced.py`** - Transform content to V2 templates

## Navigation

- **`add-missing-descriptions.py`** - Add missing descriptions to pages
- **`analyze-patterns.py`** - Analyze pattern organization
- **`tier_section_validator.py`** - Validate tier sections

## Utilities

- **`cleanup-project.py`** - Project cleanup utilities
- **`setup_diagram_tools.sh`** - Setup diagram rendering tools

## Archived Scripts

Legacy and one-time use scripts have been moved to `scripts/archive/` to keep the main directory clean and focused.
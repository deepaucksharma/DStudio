---
title: Navigation Maintenance Guide
description: How to maintain and validate the documentation navigation structure
---

# Navigation Maintenance Guide

This guide explains how to maintain the navigation structure and use the automated validation tools.

## Overview

The DStudio documentation uses MkDocs for static site generation. The navigation structure is defined in `mkdocs.yml` and must be kept in sync with the actual documentation files in the `docs/` directory.

## Automated Validation

### CI/CD Pipeline

Every push and pull request triggers automatic navigation validation:

1. **Broken Link Detection**: Fails the build if any navigation links point to non-existent files
2. **Coverage Monitoring**: Warns if navigation coverage drops below 50%
3. **Orphan Detection**: Reports files not included in navigation
4. **Metadata Validation**: Checks for missing pattern metadata

### Local Validation

Run the navigation validator locally:

```bash
python3 scripts/navigation-validator.py
```

This generates a detailed report showing:
- Navigation coverage percentage
- List of orphaned files
- Broken navigation links
- Metadata issues
- Overall health score (A-F)

### Pre-commit Hook

Install the pre-commit hook to catch issues before committing:

```bash
ln -s ../scripts/pre-commit-navigation-check.sh .git/hooks/pre-commit
```

## Adding New Content

When adding new documentation:

1. **Create the markdown file** in the appropriate directory
2. **Add proper frontmatter**:
   ```yaml
   ---
   title: Your Page Title
   description: Brief description of the content
   # For patterns, also include:
   category: resilience|data|integration|architecture
   excellence_tier: gold|silver|bronze
   pattern_status: stable|experimental|deprecated
   ---
   ```

3. **Update mkdocs.yml** to include the new file in navigation:
   ```yaml
   nav:
     - Section:
       - Your Page: path/to/your-page.md
   ```

4. **Run validation** to ensure no issues:
   ```bash
   python3 scripts/navigation-validator.py
   ```

## Common Tasks

### Finding Orphaned Files

```bash
# List all orphaned files
python3 -c "import json; report=json.load(open('navigation-validation-report.json')); print('\n'.join(report['orphaned_files']))"
```

### Fixing Metadata Issues

For patterns missing metadata:
```bash
python3 scripts/fix-pattern-metadata.py
```

### Checking Navigation Health

```bash
# Quick health check
python3 scripts/navigation-validator.py | grep "Health Score"
```

## Navigation Structure Best Practices

1. **Logical Grouping**: Organize content into clear, logical sections
2. **Depth Limits**: Avoid navigation deeper than 3 levels
3. **Consistent Naming**: Use clear, descriptive names for sections
4. **Progressive Disclosure**: Show essential items first, details in subsections
5. **Cross-References**: Use the pattern catalog for comprehensive listings

## Troubleshooting

### "File not found" errors
- Check file paths are relative to `docs/` directory
- Ensure `.md` extension is included
- Verify case sensitivity (Linux is case-sensitive)

### High orphan rate
- Review orphaned files list
- Determine if files should be:
  - Added to navigation
  - Moved to archive
  - Deleted if obsolete

### Metadata validation failures
- Run the metadata fix script
- Manually add missing fields
- Use appropriate values for tier and status

## Maintenance Schedule

- **Daily**: CI/CD runs on all commits
- **Weekly**: Review orphaned files report
- **Monthly**: Comprehensive navigation audit
- **Quarterly**: Content deprecation review

## Tools Reference

| Tool | Purpose | Usage |
|------|---------|-------|
| `navigation-validator.py` | Full navigation validation | `python3 scripts/navigation-validator.py` |
| `fix-pattern-metadata.py` | Fix missing pattern metadata | `python3 scripts/fix-pattern-metadata.py` |
| `pre-commit-navigation-check.sh` | Pre-commit validation | Install as git hook |

## Getting Help

- Check the [MkDocs documentation](https://www.mkdocs.org/)
- Review the [Material theme docs](https://squidfunk.github.io/mkdocs-material/)
- Ask in project discussions
# Scripts Directory Inventory and Documentation

## Overview
This directory contains automation scripts for managing the DStudio documentation. Scripts are organized by functionality and purpose.

## Directory Structure

```
scripts/
├── knowledge-graph/     # Knowledge graph analysis and building tools
├── health-tracking/     # Pattern health monitoring and dashboards
└── (main scripts)       # Various automation and maintenance tools
```

## Knowledge Graph Tools
**Location:** `scripts/knowledge-graph/`

| Script | Purpose | Status |
|--------|---------|--------|
| `knowledge_graph_ultimate.py` | Production-ready knowledge graph with SQLite FTS5, async validation, incremental updates | **ACTIVE** |
| `knowledge_graph_advanced.py` | ML-enhanced version with semantic embeddings and TF-IDF | SUPERSEDED |
| `knowledge_graph_builder.py` | Basic implementation | SUPERSEDED |
| `query_knowledge_graph.py` | Query interface for knowledge graph database | **ACTIVE** |
| `test_knowledge_graph.py` | Test suite for knowledge graph | **ACTIVE** |

**Recommended:** Use `knowledge_graph_ultimate.py` for production use.

## Active Scripts by Category

### 1. Link Management
**Purpose:** Analyze and fix broken links, normalize paths, validate references

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `comprehensive_link_analysis.py` | Deep analysis of all link types with specific fixes | Initial link audit |
| `fix_all_link_issues.py` | Systematic link issue resolution | Bulk link fixes |
| `validate_all_links.py` | Validate internal and external links | Pre-deployment check |
| `check-broken-links.py` | Quick broken link detection | CI/CD pipeline |

### 2. Pattern Library Management
**Purpose:** Manage pattern templates, metadata, and transformations

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `pattern-manager.py` | Comprehensive pattern management CLI | Pattern CRUD operations |
| `comprehensive-pattern-validator.py` | Validate pattern structure and metadata | Quality assurance |
| `template_v2_transformer_enhanced.py` | Transform patterns to Template v2 format | Pattern migration |
| `pattern_validator.py` | Basic pattern validation | Quick checks |
| `tier_section_validator.py` | Validate tier classifications | Tier management |

### 3. Content Generation
**Purpose:** Create missing content, fix frontmatter, generate structures

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `create_missing_files.py` | Generate missing documentation files | Fill content gaps |
| `add-missing-frontmatter.py` | Add required frontmatter to files | Metadata fixes |
| `create-leadership-interview-structure.py` | Generate interview prep structure | Content scaffolding |
| `add-missing-descriptions.py` | Add descriptions to files lacking them | SEO improvement |

### 4. Navigation & Structure
**Purpose:** Fix navigation issues, validate structure, resolve 404s

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `final_navigation_fix.py` | Advanced navigation path fixes | Navigation overhaul |
| `analyze_navigation_issues.py` | Detect navigation problems | Diagnostic |
| `simple_nav_check.py` | Quick navigation validation | Pre-commit check |
| `validate_navigation.py` | Comprehensive nav validation | CI/CD pipeline |

### 5. Validation & QA
**Purpose:** Ensure documentation quality and consistency

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `mkdocs-validator.py` | First-principles MkDocs validation | Build validation |
| `final_validation.py` | Comprehensive side-effect checks | Post-migration |
| `validate-frontmatter.py` | Validate YAML frontmatter | Metadata QA |
| `validate_content.py` | Content structure validation | Content review |

### 6. Visual Assets
**Purpose:** Handle Mermaid diagrams and visual content

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `extract_mermaid_diagrams.py` | Extract and analyze diagrams | Diagram audit |
| `render_mermaid_diagrams.py` | Render diagrams to images | Static generation |
| `monitor_diagram_conversion.py` | Track diagram rendering | Build monitoring |

### 7. Cleanup & Maintenance
**Purpose:** Bulk operations, cleanup, and fixes

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `fix_admonitions.py` | Fix escaped admonition syntax | After bulk edits |
| `check_duplicates.py` | Find duplicate content | Content audit |
| `cleanup-project.py` | General project cleanup | Periodic maintenance |

## Shell Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `validate-all.sh` | Run all validation scripts | Pre-release |
| `quick_pattern_check.sh` | Quick pattern validation | Development |
| `pre-commit-pattern-validation.sh` | Git pre-commit hook | Git workflow |
| `pre-commit-navigation-check.sh` | Navigation pre-commit | Git workflow |
| `setup_diagram_tools.sh` | Install diagram dependencies | Setup |

## Deprecated/Obsolete Scripts

These scripts are superseded by newer versions or were one-time migrations:

### Superseded by Enhanced Versions
- `knowledge_graph_builder.py` → Use `knowledge_graph_ultimate.py`
- `knowledge_graph_advanced.py` → Use `knowledge_graph_ultimate.py`
- `template_v2_transformer.py` → Use `template_v2_transformer_enhanced.py`
- `comprehensive_navigation_fix.py` → Use `final_navigation_fix.py`
- `comprehensive_link_fixes.py` → Use `fix_all_link_issues.py`

### One-Time Migration Scripts (May Remove)
- `fix_deployed_broken_links.py` - Specific deployment fix
- `fix_navigation_404s.py` - Specific 404 resolution
- `fix_learning_paths.py` - Learning path migration
- `fix_metadata_issues.py` - Metadata migration
- `remove-broken-additions.py` - Cleanup after specific issue
- `continue-cleanup.py` - Continuation of specific cleanup
- `synthesize-cleanup.py` - Post-cleanup synthesis

### Analysis Scripts (Keep for Reference)
- `comprehensive_metadata_summary.py` - Metadata analysis
- `deep-structure-analyzer.py` - Deep structural analysis
- `analyze-patterns.py` - Pattern analysis

## Usage Guidelines

### Daily Development
```bash
# Quick validation before commits
./quick_pattern_check.sh
python3 simple_nav_check.py

# Fix common issues
python3 fix_admonitions.py
python3 add-missing-frontmatter.py
```

### Major Changes
```bash
# Full link analysis and fix
python3 comprehensive_link_analysis.py
python3 fix_all_link_issues.py

# Navigation overhaul
python3 analyze_navigation_issues.py
python3 final_navigation_fix.py
```

### Pre-Deployment
```bash
# Complete validation suite
./validate-all.sh
python3 mkdocs-validator.py
python3 final_validation.py
```

### Knowledge Graph Operations
```bash
cd knowledge-graph/
# Build/update graph
python3 knowledge_graph_ultimate.py

# Query graph
python3 query_knowledge_graph.py

# Run tests
python3 test_knowledge_graph.py
```

## Maintenance Recommendations

1. **Consolidate Link Scripts:** Merge multiple link-fixing scripts into a single comprehensive tool
2. **Archive Migration Scripts:** Move one-time migration scripts to an `archive/` folder
3. **Standardize Naming:** Use consistent naming convention (prefer underscores over hyphens)
4. **Add Unit Tests:** Create test suite for critical scripts
5. **Document Dependencies:** Add requirements.txt for Python dependencies

## Dependencies

Common Python packages used:
- `pyyaml` - YAML parsing
- `click` - CLI interfaces
- `pathlib` - Path operations
- `networkx` - Graph operations (knowledge graph)
- `sqlite3` - Database operations
- `asyncio` - Async operations
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests

## Notes

- Scripts prefixed with `final_` indicate the latest iteration of a tool
- Scripts with `comprehensive_` prefix perform deep analysis
- Shell scripts (`.sh`) are typically wrappers or batch operations
- The `health-tracking/` subdirectory contains specialized monitoring tools
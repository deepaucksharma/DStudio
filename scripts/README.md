# DStudio Scripts Directory

## 📁 Organization Structure

The scripts directory has been reorganized into functional categories for better maintainability:

```
scripts/
├── knowledge-graph/      # Knowledge graph building and analysis
├── link-management/      # Link validation and fixing tools
├── pattern-library/      # Pattern management and transformation
├── validation/           # Content and structure validation
├── navigation/           # Navigation structure and fixes
├── content-generation/   # Generate missing content and frontmatter
├── visual-assets/        # Mermaid diagram processing
├── health-tracking/      # Pattern health monitoring
└── archive/              # Deprecated and one-time migration scripts
```

## 🚀 Quick Start

### Most Common Operations

```bash
# Validate before committing
./quick_pattern_check.sh

# Fix common issues
python3 link-management/fix_all_link_issues.py
python3 navigation/final_navigation_fix.py

# Build knowledge graph
python3 knowledge-graph/knowledge_graph_ultimate.py

# Validate entire project
./validate-all.sh
```

## 📚 Documentation

- **[SCRIPT_INVENTORY.md](SCRIPT_INVENTORY.md)** - Detailed documentation of all scripts
- **[pattern-validation-tools.md](pattern-validation-tools.md)** - Pattern validation specifics
- **[README-validation.md](README-validation.md)** - Validation approach documentation
- **Category READMEs** - Each subdirectory contains its own README

## 🔧 Tool Categories

### Knowledge Graph (`knowledge-graph/`)
Advanced documentation analysis with semantic understanding:
- Build comprehensive knowledge graph
- Query relationships and quality metrics
- Export for external analysis

### Link Management (`link-management/`)
Ensure all links are valid and properly formatted:
- Detect and fix broken links
- Normalize link paths
- Validate external URLs

### Pattern Library (`pattern-library/`)
Manage distributed systems patterns:
- Transform to Template v2 format
- Validate pattern metadata
- Generate comparison matrices

### Validation (`validation/`)
Quality assurance for documentation:
- MkDocs structure validation
- Frontmatter consistency
- Content structure checks

### Navigation (`navigation/`)
Fix and maintain navigation structure:
- Resolve 404 errors
- Create redirect maps
- Validate navigation paths

### Content Generation (`content-generation/`)
Fill gaps in documentation:
- Create missing files
- Add required frontmatter
- Generate leadership content

### Visual Assets (`visual-assets/`)
Process and render diagrams:
- Extract Mermaid diagrams
- Render to static images
- Monitor rendering status

### Health Tracking (`health-tracking/`)
Monitor pattern library health:
- Track pattern quality scores
- Generate health dashboards
- Identify improvement areas

### Archive (`archive/`)
Historical scripts kept for reference:
- One-time migrations
- Superseded tools
- Specific fixes already applied

## 🔄 Workflow Integration

### Pre-commit Hooks
```bash
# Add to .git/hooks/pre-commit
./scripts/pre-commit-pattern-validation.sh
./scripts/pre-commit-navigation-check.sh
```

### CI/CD Pipeline
```yaml
# Example GitHub Actions
- name: Validate Documentation
  run: |
    ./scripts/validate-all.sh
    python3 scripts/validation/mkdocs-validator.py
```

### Periodic Maintenance
```bash
# Weekly quality check
python3 knowledge-graph/knowledge_graph_ultimate.py
python3 knowledge-graph/query_knowledge_graph.py

# Monthly cleanup
python3 validation/check_duplicates.py
python3 link-management/validate_all_links.py
```

## 🛠 Development

### Adding New Scripts
1. Place in appropriate category directory
2. Update SCRIPT_INVENTORY.md
3. Follow naming convention: `snake_case.py`
4. Include docstring with purpose

### Python Dependencies
```bash
pip install pyyaml click pathlib networkx aiohttp rich beautifulsoup4
```

### Shell Scripts in Root
- `validate-all.sh` - Run all validation scripts
- `quick_pattern_check.sh` - Quick pattern validation
- `pre-commit-*.sh` - Git hooks
- `check_links.sh` - Link checking wrapper
- `setup_diagram_tools.sh` - Setup diagram tools

## 📝 Maintenance Notes

- Scripts prefixed with `final_` are the latest iterations
- Scripts with `comprehensive_` perform deep analysis
- The `archive/` directory contains historical scripts
- Shell scripts remain in the root for easy access

## 📊 Script Statistics

- **Active Scripts:** ~50
- **Archived Scripts:** 13
- **Categories:** 9
- **Languages:** Python, Bash
- **Primary Use:** Documentation quality and maintenance

---

*Last organized: 2025-08-06*
*Use `organize_scripts.py` to reorganize if needed*
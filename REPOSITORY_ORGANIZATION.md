# Repository Organization Guide

This document describes the organization structure of the DStudio repository after consolidation.

## Repository Structure

```
DStudio/
├── docs/                    # Main documentation content (MkDocs site)
│   ├── introduction/        # Getting started guides
│   ├── part1-axioms/        # 7 fundamental laws
│   ├── part2-pillars/       # 5 foundational pillars
│   ├── patterns/            # 101 architectural patterns
│   ├── excellence/          # Excellence framework
│   ├── quantitative/        # Mathematical toolkit
│   ├── human-factors/       # Operational excellence
│   └── reference/           # Glossary, cheat sheets, etc.
│
├── podcast-content/         # All podcast-related content
│   ├── 01-foundational-series/
│   ├── 02-pattern-mastery-series/
│   ├── 03-architecture-deep-dives-series/
│   ├── enhancement-summaries/
│   │   ├── EPISODE_ENHANCEMENT_GUIDE.md
│   │   ├── ENHANCEMENT_SUMMARY_REPORT.md
│   │   ├── ENHANCEMENT_SUMMARY_EPISODES_22-32.md
│   │   ├── EPISODE_ENHANCEMENT_RECOMMENDATIONS.md
│   │   └── PLATINUM_ENHANCEMENT_SUMMARY.md
│   └── series-planning/
│       ├── architecture-series-summary.md
│       ├── series-3-quantitative-mastery-plan.md
│       └── series-4-human-factors-plan.md
│
├── project-docs/            # Internal project documentation
│   ├── tracking/            # Progress tracking
│   │   ├── PATTERN_FIX_TRACKER.md
│   │   └── PATTERN_FIX_PROGRESS_REPORT.md
│   ├── summaries/           # Project summaries
│   │   └── resilience-patterns-transformation-summary.md
│   └── pattern-planning/    # Pattern library planning
│       ├── PATTERN_ASSESSMENT_MATRIX.md
│       ├── PATTERN_IMPROVEMENT_ROADMAP.md
│       ├── PATTERN_LIBRARY_CRITICAL_REVIEW.md
│       ├── PATTERN_QUALITY_RUBRIC.md
│       └── PATTERN_TRANSFORMATION_EXAMPLES.md
│
├── reports/                 # Project reports and analysis
│   ├── archive/             # Historical documents
│   ├── analysis/            # JSON analysis files
│   ├── restructuring/       # Restructuring reports
│   └── *.md                 # Various status reports
│
├── scripts/                 # Utility scripts
│   ├── health-tracking/     # Pattern health dashboard scripts
│   └── *.py                 # Various Python scripts
│
├── data/                    # Data files
│   └── health-data/         # Pattern health metrics
│
├── .github/                 # GitHub configurations
│   └── workflows/           # CI/CD workflows
│
└── Root files:
    ├── README.md            # Project overview
    ├── CONTRIBUTING.md      # Contribution guidelines
    ├── CLAUDE.md            # Claude Code instructions
    ├── mkdocs.yml           # MkDocs configuration
    └── requirements.txt     # Python dependencies
```

## Key Principles

1. **Documentation First**: The `docs/` directory contains all user-facing documentation
2. **Clear Separation**: Internal project files are in `project-docs/`, not mixed with content
3. **Podcast Organization**: All podcast content is centralized in `podcast-content/`
4. **Reports Archive**: Historical reports are preserved in `reports/archive/`
5. **Clean Root**: Only essential files remain in the repository root

## Directory Purposes

### `/docs/`
The main documentation site content. This is what users see when they visit the site.

### `/podcast-content/`
All podcast episodes, enhancements, and planning documents. Organized by series with additional directories for summaries and planning.

### `/project-docs/`
Internal project documentation including:
- Progress tracking files
- Pattern planning documents
- Project summaries

### `/reports/`
Comprehensive project reports, analysis, and historical documents. Well-organized with subdirectories for different report types.

### `/scripts/`
Utility scripts for validation, checking, and maintenance tasks.

### `/data/`
Data files used by the documentation site, particularly for the pattern health dashboard.

## Benefits of This Organization

1. **Clarity**: Clear separation between user-facing content and internal documentation
2. **Maintainability**: Easy to find and update related files
3. **Scalability**: Structure supports future growth
4. **Professional**: Clean repository structure for open-source project
5. **Efficiency**: Reduced clutter and improved navigation
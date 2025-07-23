# Axiom to Law Terminology Change Report

## Executive Summary

The codebase currently uses inconsistent terminology between "axioms" and "laws". This report identifies all files that need updating to standardize on "laws" as the primary term.

## Critical Navigation Files

### 1. mkdocs.yml (Primary Navigation)
- **Current State**: Mixed usage - "Laws" in navigation labels but links to "axioms" paths
- **Issues**:
  - Navigation shows "The 7 Laws" but links to `/axioms/index.md`
  - Section labeled "Laws (Detailed)" links to `/part1-axioms/`
  - Path structure uses `part1-axioms` directory
- **Dependencies**: All internal links throughout the site reference these paths

### 2. Directory Structure
- **Current State**: 
  - `/docs/part1-axioms/` - Main content directory
  - `/docs/axioms/` - Overview page
  - Subdirectories: `axiom1-failure`, `axiom2-asynchrony`, etc.
- **Issues**: Directory names use "axiom" prefix
- **Impact**: Changing directory names will break all internal links

## Content Files Requiring Updates

### Core Documentation (141 files total)

#### High Priority - Navigation & Overview Pages
1. `/docs/axioms/index.md` - Main laws overview page
2. `/docs/part1-axioms/index.md` - Detailed laws section
3. `/docs/introduction/index.md` - References "7 Laws" correctly but links to axioms
4. `/docs/introduction/getting-started.md`
5. `/docs/learning-paths/index.md`

#### Law-Specific Pages (7 laws × multiple files each)
- Law 1: `/docs/part1-axioms/axiom1-failure/` (index.md, examples.md, exercises.md)
- Law 2: `/docs/part1-axioms/axiom2-asynchrony/` (index.md, examples.md, exercises.md)
- Law 3: `/docs/part1-axioms/axiom3-emergence/` (index.md, examples.md, exercises.md)
- Law 4: `/docs/part1-axioms/axiom4-tradeoffs/` (index.md, examples.md, exercises.md)
- Law 5: `/docs/part1-axioms/axiom5-epistemology/` (index.md)
- Law 6: `/docs/part1-axioms/axiom6-human-api/` (index.md)
- Law 7: `/docs/part1-axioms/axiom7-economics/` (index.md)

#### Cross-References in Other Sections
- **Patterns** (30+ files): Many patterns reference axioms in their "Law Connections" sections
- **Case Studies** (20+ files): Reference axioms in analysis
- **Pillars** (5 files): Reference foundation axioms
- **Quantitative** (10+ files): Mathematical analysis of axioms
- **Human Factors** (6+ files): Reference operational axioms

### CSS and Styling Files

1. `/docs/stylesheets/axioms.css` - Contains axiom-specific styling classes
   - `.axiom-header`, `.axiom-grid`, `.axiom-card`, `.axiom-color`
   - Color schemes for each axiom

2. `/docs/stylesheets/extra.css` - Contains axiom-related styles
   - `.axiom-box`, `.axioms-grid`, `.axiom-card`

### Supporting Files

1. **Templates**: 
   - `/templates/EXERCISE_TEMPLATE_AXIOM.md`
   - References to axioms in various templates

2. **Automation Scripts**:
   - `/automation/complete_axiom_content.py`
   - Other scripts that reference axiom structure

3. **Documentation**:
   - `/CLAUDE.md` - Project instructions reference "8 fundamental axioms"
   - `/README.md` - May reference axioms
   - `/internal-docs/NAVIGATION_ENHANCEMENTS.md` - References axiom cross-references

## Potential Issues and Dependencies

### 1. URL Structure Impact
- Current URLs: `/part1-axioms/axiom1-failure/`
- Proposed URLs: `/part1-laws/law1-failure/`
- **Issue**: Will break all existing bookmarks and external links

### 2. Internal Link Dependencies
- Hundreds of internal links throughout the documentation
- Pattern pages link to axioms
- Case studies reference axioms
- Cross-reference system built around axiom terminology

### 3. CSS Class Dependencies
- Many pages use `.axiom-box`, `.axiom-card` classes
- Changing class names requires updating all HTML/Markdown that uses them

### 4. Archive Directory
- `/docs/part1-axioms/archive-old-8-axiom-structure/` contains historical content
- May want to preserve for reference

## Recommended Approach

### Phase 1: Preparation
1. Create comprehensive list of all files with internal links
2. Inventory all CSS class usage
3. Document current URL structure for redirect mapping

### Phase 2: Systematic Updates
1. Update navigation labels first (mkdocs.yml)
2. Update content in pages (keeping URLs same initially)
3. Update CSS classes and styling
4. Update internal links
5. Finally update directory structure with redirects

### Phase 3: Validation
1. Check all internal links
2. Verify CSS styling still works
3. Test navigation thoroughly
4. Set up URL redirects for old paths

## Risk Assessment

- **High Risk**: Breaking internal navigation and links
- **Medium Risk**: Breaking external bookmarks/links
- **Low Risk**: CSS styling inconsistencies

## Effort Estimate

- **Total Files to Update**: 141+ files
- **Manual Review Required**: All pattern and case study cross-references
- **Testing Required**: Full site navigation and link validation
- **Estimated Time**: 4-6 hours for careful implementation

## Next Steps

1. Confirm terminology change from "axioms" to "laws"
2. Decide on URL structure (keep current vs change to match)
3. Plan redirect strategy for old URLs
4. Create detailed implementation checklist
5. Execute changes in phases with validation
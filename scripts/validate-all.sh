#!/bin/bash
# Comprehensive validation script for DStudio documentation
# Updated to work with reorganized script directory structure

set -e

echo "🚀 Starting comprehensive documentation validation..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create reports directory if it doesn't exist
REPORTS_DIR="validation-reports"
mkdir -p "$REPORTS_DIR"

# Timestamp for reports
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "\n${BLUE}1. Running link validation...${NC}"
if [ -f "$SCRIPT_DIR/link-management/validate_all_links.py" ]; then
    python3 "$SCRIPT_DIR/link-management/validate_all_links.py" \
        > "$REPORTS_DIR/link-validation-$TIMESTAMP.log" 2>&1 || {
        echo -e "${YELLOW}⚠️  Link validation found issues${NC}"
    }
fi

echo -e "\n${BLUE}2. Running navigation validation...${NC}"
if [ -f "$SCRIPT_DIR/navigation/validate_navigation.py" ]; then
    python3 "$SCRIPT_DIR/navigation/validate_navigation.py" \
        > "$REPORTS_DIR/navigation-validation-$TIMESTAMP.log" 2>&1 || {
        echo -e "${YELLOW}⚠️  Navigation validation found issues${NC}"
    }
fi

echo -e "\n${BLUE}3. Checking pattern library consistency...${NC}"
if [ -f "$SCRIPT_DIR/pattern-library/comprehensive-pattern-validator.py" ]; then
    python3 "$SCRIPT_DIR/pattern-library/comprehensive-pattern-validator.py" \
        > "$REPORTS_DIR/pattern-validation-$TIMESTAMP.md" 2>&1 || {
        echo -e "${YELLOW}⚠️  Pattern validation found issues${NC}"
    }
fi

echo -e "\n${BLUE}4. Validating frontmatter...${NC}"
if [ -f "$SCRIPT_DIR/validation/validate-frontmatter.py" ]; then
    python3 "$SCRIPT_DIR/validation/validate-frontmatter.py" \
        > "$REPORTS_DIR/frontmatter-validation-$TIMESTAMP.log" 2>&1 || {
        echo -e "${YELLOW}⚠️  Frontmatter validation found issues${NC}"
    }
fi

echo -e "\n${BLUE}5. Running MkDocs validation...${NC}"
if [ -f "$SCRIPT_DIR/validation/mkdocs-validator.py" ]; then
    python3 "$SCRIPT_DIR/validation/mkdocs-validator.py" \
        > "$REPORTS_DIR/mkdocs-validation-$TIMESTAMP.log" 2>&1 || {
        echo -e "${YELLOW}⚠️  MkDocs validation found issues${NC}"
    }
fi

echo -e "\n${BLUE}6. Running final validation checks...${NC}"
if [ -f "$SCRIPT_DIR/validation/final_validation.py" ]; then
    python3 "$SCRIPT_DIR/validation/final_validation.py" \
        > "$REPORTS_DIR/final-validation-$TIMESTAMP.log" 2>&1 || {
        echo -e "${YELLOW}⚠️  Final validation found issues${NC}"
    }
fi

echo -e "\n${BLUE}7. Building MkDocs (strict mode)...${NC}"
mkdocs build --strict --quiet > "$REPORTS_DIR/mkdocs-build-$TIMESTAMP.log" 2>&1 || {
    echo -e "${YELLOW}⚠️  MkDocs build had warnings/errors. Check $REPORTS_DIR/mkdocs-build-$TIMESTAMP.log${NC}"
}

echo -e "\n${BLUE}8. Generating summary report...${NC}"

# Count issues from logs
LINK_ISSUES=$(grep -c "ERROR\|WARNING" "$REPORTS_DIR/link-validation-$TIMESTAMP.log" 2>/dev/null || echo "0")
NAV_ISSUES=$(grep -c "ERROR\|WARNING" "$REPORTS_DIR/navigation-validation-$TIMESTAMP.log" 2>/dev/null || echo "0")
PATTERN_ISSUES=$(grep -c "❌\|⚠️" "$REPORTS_DIR/pattern-validation-$TIMESTAMP.md" 2>/dev/null || echo "0")
FRONTMATTER_ISSUES=$(grep -c "ERROR\|WARNING" "$REPORTS_DIR/frontmatter-validation-$TIMESTAMP.log" 2>/dev/null || echo "0")

# Create summary report
cat > "$REPORTS_DIR/validation-summary-$TIMESTAMP.md" << EOF
# Documentation Validation Summary

**Generated:** $(date)
**Script Version:** Reorganized structure (2025-08-06)

## Results Overview

| Category | Issues Found | Report File |
|----------|-------------|-------------|
| Link Validation | $LINK_ISSUES | [link-validation-$TIMESTAMP.log](link-validation-$TIMESTAMP.log) |
| Navigation | $NAV_ISSUES | [navigation-validation-$TIMESTAMP.log](navigation-validation-$TIMESTAMP.log) |
| Pattern Library | $PATTERN_ISSUES | [pattern-validation-$TIMESTAMP.md](pattern-validation-$TIMESTAMP.md) |
| Frontmatter | $FRONTMATTER_ISSUES | [frontmatter-validation-$TIMESTAMP.log](frontmatter-validation-$TIMESTAMP.log) |
| MkDocs Validation | - | [mkdocs-validation-$TIMESTAMP.log](mkdocs-validation-$TIMESTAMP.log) |
| Final Checks | - | [final-validation-$TIMESTAMP.log](final-validation-$TIMESTAMP.log) |
| MkDocs Build | - | [mkdocs-build-$TIMESTAMP.log](mkdocs-build-$TIMESTAMP.log) |

## Quick Fixes Available

### Fix All Link Issues
\`\`\`bash
python3 scripts/link-management/fix_all_link_issues.py
\`\`\`

### Fix Navigation Issues
\`\`\`bash
python3 scripts/navigation/final_navigation_fix.py
\`\`\`

### Fix Frontmatter Issues
\`\`\`bash
python3 scripts/content-generation/add-missing-frontmatter.py
\`\`\`

### Transform Patterns to V2
\`\`\`bash
python3 scripts/pattern-library/template_v2_transformer_enhanced.py
\`\`\`

## Knowledge Graph

To build and query the knowledge graph:
\`\`\`bash
python3 scripts/knowledge-graph/knowledge_graph_ultimate.py
python3 scripts/knowledge-graph/query_knowledge_graph.py
\`\`\`

## Script Categories

Scripts are now organized into:
- \`knowledge-graph/\` - Knowledge graph tools
- \`link-management/\` - Link validation and fixes
- \`pattern-library/\` - Pattern management
- \`validation/\` - Various validation tools
- \`navigation/\` - Navigation structure tools
- \`content-generation/\` - Content creation tools
- \`visual-assets/\` - Diagram processing
- \`archive/\` - Historical scripts

See \`scripts/SCRIPT_INVENTORY.md\` for detailed documentation.

EOF

echo -e "\n${GREEN}✅ Validation complete!${NC}"
echo -e "${GREEN}📁 Reports saved in: $REPORTS_DIR/${NC}"
echo -e "${GREEN}📄 Summary: $REPORTS_DIR/validation-summary-$TIMESTAMP.md${NC}"

# Show quick summary
echo -e "\n${BLUE}Quick Summary:${NC}"
echo "  Link Issues: $LINK_ISSUES"
echo "  Navigation Issues: $NAV_ISSUES"
echo "  Pattern Issues: $PATTERN_ISSUES"
echo "  Frontmatter Issues: $FRONTMATTER_ISSUES"

TOTAL_ISSUES=$((LINK_ISSUES + NAV_ISSUES + PATTERN_ISSUES + FRONTMATTER_ISSUES))

# Exit with appropriate code
if [ "$TOTAL_ISSUES" -eq 0 ]; then
    echo -e "\n${GREEN}✨ All validations passed!${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  $TOTAL_ISSUES issues found. Please review the reports.${NC}"
    exit 1
fi
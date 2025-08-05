#!/bin/bash
# Comprehensive validation script for DStudio documentation
# This script runs all validation checks and generates reports

set -e

echo "🚀 Starting comprehensive documentation validation..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create reports directory if it doesn't exist
REPORTS_DIR="validation-reports"
mkdir -p "$REPORTS_DIR"

# Timestamp for reports
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "\n${BLUE}1. Running comprehensive navigation and link validation...${NC}"
python3 scripts/comprehensive-navigation-validator.py \
    --verbose \
    --report json \
    --output "$REPORTS_DIR/nav-links-report-$TIMESTAMP.json"

# Also generate markdown report
python3 scripts/comprehensive-navigation-validator.py \
    --report markdown \
    --output "$REPORTS_DIR/nav-links-report-$TIMESTAMP.md"

echo -e "\n${BLUE}2. Checking pattern metadata consistency...${NC}"
if [ -f "scripts/comprehensive-pattern-validator.py" ]; then
    python3 scripts/comprehensive-pattern-validator.py \
        --report=markdown \
        > "$REPORTS_DIR/pattern-validation-$TIMESTAMP.md" || true
fi

echo -e "\n${BLUE}3. Validating MkDocs configuration...${NC}"
mkdocs build --strict --quiet > "$REPORTS_DIR/mkdocs-build-$TIMESTAMP.log" 2>&1 || {
    echo -e "${YELLOW}⚠️  MkDocs build had warnings/errors. Check $REPORTS_DIR/mkdocs-build-$TIMESTAMP.log${NC}"
}

echo -e "\n${BLUE}4. Generating summary report...${NC}"

# Create summary report
cat > "$REPORTS_DIR/validation-summary-$TIMESTAMP.md" << EOF
# Documentation Validation Summary

**Generated:** $(date)

## Reports Generated

1. **Navigation & Links Report**
   - JSON: [nav-links-report-$TIMESTAMP.json](nav-links-report-$TIMESTAMP.json)
   - Markdown: [nav-links-report-$TIMESTAMP.md](nav-links-report-$TIMESTAMP.md)

2. **Pattern Validation Report**
   - [pattern-validation-$TIMESTAMP.md](pattern-validation-$TIMESTAMP.md)

3. **MkDocs Build Log**
   - [mkdocs-build-$TIMESTAMP.log](mkdocs-build-$TIMESTAMP.log)

## Quick Actions

### Fix Broken Links Automatically
\`\`\`bash
python3 scripts/comprehensive-navigation-validator.py --fix
\`\`\`

### View Detailed Console Report
\`\`\`bash
python3 scripts/comprehensive-navigation-validator.py --verbose
\`\`\`

### Check Specific Issues

#### Orphaned Files Only
\`\`\`bash
python3 scripts/comprehensive-navigation-validator.py --report json | jq '.orphaned_files'
\`\`\`

#### Broken Links Only
\`\`\`bash
python3 scripts/comprehensive-navigation-validator.py --report json | jq '.broken_links'
\`\`\`

## Validation Scripts Available

- \`comprehensive-navigation-validator.py\` - All-in-one navigation and link checker
- \`check-navigation.py\` - Quick navigation file existence check
- \`verify-links.py\` - Internal link verification
- \`navigation-validator.py\` - Navigation structure analysis
- \`comprehensive-pattern-validator.py\` - Pattern metadata validation

EOF

echo -e "\n${GREEN}✅ Validation complete!${NC}"
echo -e "${GREEN}📁 Reports saved in: $REPORTS_DIR/${NC}"
echo -e "${GREEN}📄 Summary: $REPORTS_DIR/validation-summary-$TIMESTAMP.md${NC}"

# Show quick summary
echo -e "\n${BLUE}Quick Summary:${NC}"
python3 scripts/comprehensive-navigation-validator.py 2>/dev/null | grep -E "(Health Grade:|Total Files:|Broken Links:|Orphaned Files:)" || true

# Exit with appropriate code
if python3 scripts/comprehensive-navigation-validator.py --fail-on-warnings >/dev/null 2>&1; then
    echo -e "\n${GREEN}✨ All validations passed!${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some issues found. Please review the reports.${NC}"
    exit 1
fi
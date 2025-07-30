#!/bin/bash
# Quick pattern validation check for CI/CD or pre-commit hooks
# Returns 0 if all patterns pass, 1 if any fail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "Running pattern content validation..."

# Run the pattern validator
if python3 "$SCRIPT_DIR/pattern_validator.py" \
    --dir "$PROJECT_ROOT/docs/pattern-library" \
    --format json \
    --output /tmp/pattern_validation.json; then
    
    # Extract summary from JSON
    TOTAL=$(jq -r '.summary.total_patterns' /tmp/pattern_validation.json)
    PASSED=$(jq -r '.summary.passed' /tmp/pattern_validation.json)
    FAILED=$(jq -r '.summary.failed' /tmp/pattern_validation.json)
    
    echo -e "${GREEN}✅ Validation Complete${NC}"
    echo "  Total patterns: $TOTAL"
    echo "  Passed: $PASSED"
    echo "  Failed: $FAILED"
    
    if [ "$FAILED" -eq 0 ]; then
        echo -e "${GREEN}All patterns passed validation!${NC}"
        rm -f /tmp/pattern_validation.json
        exit 0
    else
        echo -e "${YELLOW}⚠️  Some patterns have issues:${NC}"
        
        # Show top issues
        echo -e "\nTop issues:"
        jq -r '.patterns[] | select(.passed == false) | "\(.name): \(.issues | length) issues"' \
            /tmp/pattern_validation.json | head -5
        
        echo -e "\nRun this for full report:"
        echo "  python3 $SCRIPT_DIR/pattern_validator.py --dir $PROJECT_ROOT/docs/pattern-library"
        
        rm -f /tmp/pattern_validation.json
        exit 1
    fi
else
    echo -e "${RED}❌ Validation script failed${NC}"
    exit 1
fi
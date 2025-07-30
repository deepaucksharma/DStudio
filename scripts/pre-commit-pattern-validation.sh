#!/bin/bash
# Pre-commit hook for pattern metadata validation

set -e

echo "🔍 Validating pattern metadata..."

# Change to repo root
cd "$(git rev-parse --show-toplevel)"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required for pattern validation"
    exit 1
fi

# Check if validation script exists
if [ ! -f "scripts/validate-pattern-metadata.py" ]; then
    echo "❌ Pattern validation script not found"
    exit 1
fi

# Run validation
echo "Running pattern metadata validation..."
if ! python3 scripts/validate-pattern-metadata.py > /dev/null 2>&1; then
    echo "❌ Pattern metadata validation failed!"
    echo ""
    echo "🔧 To fix issues automatically, run:"
    echo "   python3 scripts/fix-pattern-metadata.py"
    echo ""
    echo "📊 For detailed validation report, run:"
    echo "   python3 scripts/validate-pattern-metadata.py"
    echo ""
    exit 1
fi

# Check for errors in validation report
if [ -f "pattern_metadata_validation_report.json" ]; then
    ERRORS=$(python3 -c "
import json
try:
    with open('pattern_metadata_validation_report.json', 'r') as f:
        data = json.load(f)
    print(data.get('total_errors', 0))
except:
    print(0)
")
    
    if [ "$ERRORS" -gt 0 ]; then
        echo "❌ Found $ERRORS pattern metadata errors"
        echo ""
        echo "🔧 Run this command to fix issues automatically:"
        echo "   python3 scripts/fix-pattern-metadata.py"
        echo ""
        echo "📊 For detailed report:"
        echo "   python3 scripts/validate-pattern-metadata.py"
        echo ""
        exit 1
    fi
fi

echo "✅ Pattern metadata validation passed!"
exit 0
#!/bin/bash
# Pre-commit hook to validate navigation before committing

echo "🔍 Running navigation validation..."

# Check if mkdocs.yml or any docs files were modified
if git diff --cached --name-only | grep -E "(mkdocs\.yml|docs/.*\.md)"; then
    echo "📋 Navigation or documentation files modified, running validation..."
    
    # Run the validator
    python3 scripts/navigation-validator.py
    
    # Check for broken links
    if grep -q '"broken_links": \[' navigation-validation-report.json && ! grep -q '"broken_links": \[\]' navigation-validation-report.json; then
        echo "❌ ERROR: Broken navigation links detected!"
        echo "Please fix the following broken links before committing:"
        python3 -c "import json; report=json.load(open('navigation-validation-report.json')); [print(f'  - {link}') for link in report['broken_links']]"
        exit 1
    fi
    
    # Check navigation coverage
    coverage=$(python3 -c "import json; report=json.load(open('navigation-validation-report.json')); print(report['percentages']['navigation_coverage'])")
    echo "📊 Navigation coverage: ${coverage}%"
    
    # Get health score
    health_score=$(python3 -c "import json; report=json.load(open('navigation-validation-report.json')); print(report['summary']['health_score'])")
    echo "🏥 Health score: ${health_score}"
    
    # Check if new orphaned files were created
    new_files=$(git diff --cached --name-only --diff-filter=A | grep "docs/.*\.md")
    if [ ! -z "$new_files" ]; then
        echo "📝 New documentation files detected:"
        echo "$new_files"
        echo "⚠️  WARNING: Remember to add new files to mkdocs.yml navigation!"
    fi
    
    echo "✅ Navigation validation passed!"
else
    echo "ℹ️  No navigation or documentation changes detected, skipping validation."
fi

exit 0
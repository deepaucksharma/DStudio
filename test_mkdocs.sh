#!/bin/bash
# Test MkDocs build and serve

echo "Testing MkDocs build..."
mkdocs build --clean --quiet

if [ $? -eq 0 ]; then
    echo "✅ MkDocs build successful!"
    echo ""
    echo "Site structure created:"
    find site -name "*.html" | wc -l
    echo "HTML files generated"
else
    echo "❌ MkDocs build failed"
fi

echo ""
echo "Testing navigation structure..."
if [ -f site/index.html ]; then
    echo "✅ Homepage exists"
fi

if [ -d site/pattern-library ]; then
    echo "✅ Pattern library built"
fi

if [ -d site/interview-prep ]; then
    echo "✅ Interview prep section built"
fi

echo ""
echo "MkDocs is ready to serve with: mkdocs serve"
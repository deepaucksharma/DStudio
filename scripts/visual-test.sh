#!/bin/bash

# Visual Regression Testing Script
# Ensures design system changes don't break existing styles

echo "🎨 Starting Visual Regression Tests..."

# Check if backstop is installed
if ! command -v backstop &> /dev/null; then
    echo "📦 Installing BackstopJS..."
    npm install -g backstopjs
fi

# Start the development server in the background
echo "🚀 Starting development server..."
mkdocs serve &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Check if server is running
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "❌ Development server failed to start"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Run visual tests
echo "📸 Running visual regression tests..."
cd tests/visual

# Generate reference images if they don't exist
if [ ! -d "reference" ]; then
    echo "📸 Generating reference images..."
    backstop reference --config=backstop.json
fi

# Run tests
backstop test --config=backstop.json

# Capture exit code
TEST_EXIT_CODE=$?

# Stop the development server
echo "🛑 Stopping development server..."
kill $SERVER_PID

# Exit with test exit code
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Visual regression tests passed!"
else
    echo "❌ Visual regression tests failed!"
    echo "📊 View the report at: tests/visual/report/index.html"
fi

exit $TEST_EXIT_CODE
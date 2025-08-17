#!/bin/bash
# Docker entrypoint script for Hindi Podcast Testing Framework
# हिंदी पॉडकास्ट टेस्टिंग फ्रेमवर्क के लिए Docker एंट्री पॉइंट

set -e

# Print banner
echo "🧪 Hindi Podcast Testing Framework"
echo "हिंदी पॉडकास्ट टेस्टिंग फ्रेमवर्क"
echo "=================================="

# Function to wait for service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for $service_name to be ready at $host:$port..."
    
    while ! nc -z "$host" "$port" 2>/dev/null; do
        if [ $attempt -eq $max_attempts ]; then
            echo "❌ $service_name is not ready after $max_attempts attempts"
            return 1
        fi
        
        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "✅ $service_name is ready!"
    return 0
}

# Function to check environment
check_environment() {
    echo "🔍 Checking environment..."
    
    # Check Python version
    echo "Python version: $(python --version)"
    
    # Check k6 installation
    if command -v k6 >/dev/null 2>&1; then
        echo "k6 version: $(k6 version)"
    else
        echo "⚠️ k6 not installed"
    fi
    
    # Check Go installation
    if command -v go >/dev/null 2>&1; then
        echo "Go version: $(go version)"
    else
        echo "⚠️ Go not installed"
    fi
    
    # Check Java installation
    if command -v java >/dev/null 2>&1; then
        echo "Java version: $(java -version 2>&1 | head -1)"
    else
        echo "⚠️ Java not installed"
    fi
    
    # Check Maven installation
    if command -v mvn >/dev/null 2>&1; then
        echo "Maven version: $(mvn -version | head -1)"
    else
        echo "⚠️ Maven not installed"
    fi
    
    echo "✅ Environment check completed"
}

# Function to setup test environment
setup_test_environment() {
    echo "🔧 Setting up test environment..."
    
    # Create required directories
    mkdir -p /app/test-results
    mkdir -p /app/logs
    mkdir -p /app/reports
    mkdir -p /app/coverage
    
    # Set up environment file if it doesn't exist
    if [ ! -f /app/.env ]; then
        echo "📝 Creating environment file from template..."
        cp /app/.env.example /app/.env
        
        # Update environment for Docker
        sed -i 's/localhost/host.docker.internal/g' /app/.env
        echo "TEST_ENV=docker" >> /app/.env
        echo "INDIAN_REGION=${INDIAN_REGION:-mumbai}" >> /app/.env
    fi
    
    # Set up pytest configuration
    export PYTHONPATH=/app:$PYTHONPATH
    
    echo "✅ Test environment setup completed"
}

# Function to validate test structure
validate_test_structure() {
    echo "🧪 Validating test structure..."
    
    # Check required files
    required_files=(
        "pytest.ini"
        "conftest.py"
        "Makefile"
        "requirements.txt"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "/app/$file" ]; then
            echo "❌ Required file missing: $file"
            exit 1
        fi
    done
    
    # Check test directories
    test_dirs=(
        "unit"
        "integration"
        "e2e"
        "load"
        "security"
        "performance"
        "data-validation"
        "chaos"
    )
    
    for dir in "${test_dirs[@]}"; do
        if [ ! -d "/app/$dir" ]; then
            echo "⚠️ Test directory missing: $dir"
        fi
    done
    
    # Validate pytest configuration
    if ! pytest --collect-only --quiet >/dev/null 2>&1; then
        echo "❌ Pytest configuration validation failed"
        exit 1
    fi
    
    echo "✅ Test structure validation completed"
}

# Function to wait for external services
wait_for_external_services() {
    echo "🏗️ Waiting for external services..."
    
    # List of services to wait for (if configured)
    services=(
        "postgres:5432:PostgreSQL"
        "redis:6379:Redis"
        "consul:8500:Consul"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r host port name <<< "$service"
        
        # Check if service is configured in environment
        if env | grep -q "${host^^}"; then
            wait_for_service "$host" "$port" "$name" || echo "⚠️ $name not available, skipping..."
        fi
    done
    
    echo "✅ External services check completed"
}

# Function to run specific test category
run_test_category() {
    local category=$1
    echo "🧪 Running $category tests..."
    
    case $category in
        "unit")
            make test-unit
            ;;
        "integration")
            make test-integration
            ;;
        "load")
            make test-load
            ;;
        "security")
            make test-security
            ;;
        "e2e")
            make test-e2e
            ;;
        "chaos")
            make test-chaos
            ;;
        "performance")
            make test-performance
            ;;
        "data-validation")
            make test-data-validation
            ;;
        "indian")
            make test-indian
            ;;
        "all")
            make test
            ;;
        *)
            echo "❌ Unknown test category: $category"
            echo "Available categories: unit, integration, load, security, e2e, chaos, performance, data-validation, indian, all"
            exit 1
            ;;
    esac
}

# Function to generate reports
generate_reports() {
    echo "📊 Generating test reports..."
    
    # Generate coverage report
    if [ -f "/app/.coverage" ]; then
        make coverage
    fi
    
    # Generate comprehensive report
    make report
    
    echo "✅ Reports generated"
}

# Main execution logic
main() {
    echo "🚀 Starting Hindi Podcast Testing Framework..."
    
    # Check if running in CI environment
    if [ "$CI" = "true" ]; then
        echo "🤖 Running in CI environment"
    fi
    
    # Basic environment setup
    check_environment
    setup_test_environment
    validate_test_structure
    
    # Wait for services if needed
    if [ "$WAIT_FOR_SERVICES" = "true" ]; then
        wait_for_external_services
    fi
    
    # Parse command line arguments
    if [ $# -eq 0 ]; then
        echo "💡 No command provided, showing help..."
        make help
        exit 0
    fi
    
    case "$1" in
        "test")
            if [ -n "$2" ]; then
                run_test_category "$2"
            else
                run_test_category "all"
            fi
            ;;
        "setup")
            echo "✅ Setup completed successfully"
            ;;
        "validate")
            echo "✅ Validation completed successfully"
            ;;
        "reports")
            generate_reports
            ;;
        "shell")
            echo "🐚 Starting interactive shell..."
            exec /bin/bash
            ;;
        "help")
            make help
            ;;
        *)
            # Pass through to make or direct execution
            exec "$@"
            ;;
    esac
}

# Error handling
trap 'echo "❌ Script failed at line $LINENO"' ERR

# Execute main function
main "$@"
# Makefile for Comprehensive Testing Framework
# व्यापक परीक्षण फ्रेमवर्क के लिए Makefile

.PHONY: help setup test test-unit test-integration test-load test-security test-e2e test-chaos test-performance test-data-validation clean lint format check-deps install-deps docker-test

# Default target
help: ## Show this help message
	@echo "🧪 Comprehensive Testing Framework"
	@echo "हिंदी पॉडकास्ट टेस्टिंग फ्रेमवर्क"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment setup
setup: ## Setup test environment and install dependencies
	@echo "🔧 Setting up test environment..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt || true
	@echo "✅ Environment setup completed"

install-deps: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@if [ -f "unit/go/go.mod" ]; then cd unit/go && go mod tidy; fi
	@if [ -f "unit/java/pom.xml" ]; then cd unit/java && mvn install -DskipTests; fi
	@echo "✅ Dependencies installed"

check-deps: ## Check for dependency vulnerabilities
	@echo "🔍 Checking dependencies for vulnerabilities..."
	safety check
	pip-audit || echo "pip-audit not installed, skipping..."
	@echo "✅ Dependency check completed"

# Test execution targets
test: ## Run all tests
	@echo "🧪 Running comprehensive test suite..."
	@$(MAKE) test-unit
	@$(MAKE) test-integration
	@$(MAKE) test-performance
	@$(MAKE) test-data-validation
	@echo "✅ All tests completed"

test-unit: ## Run unit tests
	@echo "🔬 Running unit tests..."
	pytest -v -m unit --cov=unit --cov-report=term-missing --cov-report=html:htmlcov-unit
	@if [ -d "unit/go" ] && [ -f "unit/go/go.mod" ]; then cd unit/go && go test -v -race ./...; fi
	@if [ -d "unit/java" ] && [ -f "unit/java/pom.xml" ]; then cd unit/java && mvn test; fi
	@echo "✅ Unit tests completed"

test-unit-python: ## Run Python unit tests only
	@echo "🐍 Running Python unit tests..."
	pytest -v -m unit unit/python/ --cov=unit/python --cov-report=term-missing
	@echo "✅ Python unit tests completed"

test-unit-go: ## Run Go unit tests only
	@echo "🐹 Running Go unit tests..."
	@if [ -d "unit/go" ] && [ -f "unit/go/go.mod" ]; then \
		cd unit/go && go test -v -race -coverprofile=coverage.out ./...; \
		go tool cover -html=coverage.out -o coverage.html; \
	else \
		echo "No Go tests found"; \
	fi
	@echo "✅ Go unit tests completed"

test-unit-java: ## Run Java unit tests only
	@echo "☕ Running Java unit tests..."
	@if [ -d "unit/java" ] && [ -f "unit/java/pom.xml" ]; then \
		cd unit/java && mvn test; \
	else \
		echo "No Java tests found"; \
	fi
	@echo "✅ Java unit tests completed"

test-integration: ## Run integration tests
	@echo "🔗 Running integration tests..."
	pytest -v -m integration --cov=integration --cov-report=term-missing
	@echo "✅ Integration tests completed"

test-load: ## Run load tests with k6
	@echo "🚀 Running load tests..."
	@$(MAKE) test-load-normal
	@$(MAKE) test-load-diwali
	@$(MAKE) test-load-ipl
	@echo "✅ Load tests completed"

test-load-normal: ## Run normal traffic load test
	@echo "📈 Running normal traffic load test..."
	k6 run --vus 10 --duration 30s -e K6_SCENARIO=normal load/k6-scripts/api-gateway-load-test.js

test-load-diwali: ## Run Diwali sale traffic simulation
	@echo "🎆 Running Diwali sale traffic simulation..."
	k6 run --vus 100 --duration 2m -e K6_SCENARIO=diwali load/k6-scripts/api-gateway-load-test.js

test-load-ipl: ## Run IPL streaming traffic simulation
	@echo "🏏 Running IPL streaming traffic simulation..."
	k6 run --vus 200 --duration 1m -e K6_SCENARIO=ipl load/k6-scripts/api-gateway-load-test.js

test-load-custom: ## Run custom load test (specify VUS and DURATION)
	@echo "⚡ Running custom load test..."
	@if [ -z "$(VUS)" ] || [ -z "$(DURATION)" ]; then \
		echo "Usage: make test-load-custom VUS=<number> DURATION=<duration>"; \
		echo "Example: make test-load-custom VUS=500 DURATION=5m"; \
		exit 1; \
	fi
	k6 run --vus $(VUS) --duration $(DURATION) load/k6-scripts/api-gateway-load-test.js

test-security: ## Run security tests
	@echo "🔒 Running security tests..."
	pytest -v -m security
	@echo "✅ Security tests completed"

test-security-owasp: ## Run OWASP Top 10 tests
	@echo "🛡️ Running OWASP Top 10 security tests..."
	pytest -v -m "security and owasp"
	@echo "✅ OWASP security tests completed"

test-security-indian: ## Run Indian compliance tests
	@echo "🇮🇳 Running Indian compliance security tests..."
	pytest -v -m "security and indian_context"
	@echo "✅ Indian compliance tests completed"

test-e2e: ## Run end-to-end tests
	@echo "🎭 Running end-to-end tests..."
	pytest -v -m e2e
	@echo "✅ E2E tests completed"

test-e2e-banking: ## Run banking E2E tests
	@echo "🏦 Running banking E2E tests..."
	pytest -v -m "e2e and banking"
	@echo "✅ Banking E2E tests completed"

test-e2e-ecommerce: ## Run e-commerce E2E tests
	@echo "🛒 Running e-commerce E2E tests..."
	pytest -v -m "e2e and ecommerce"
	@echo "✅ E-commerce E2E tests completed"

test-e2e-gaming: ## Run gaming E2E tests
	@echo "🎮 Running gaming E2E tests..."
	pytest -v -m "e2e and gaming"
	@echo "✅ Gaming E2E tests completed"

test-chaos: ## Run chaos engineering tests
	@echo "🌪️ Running chaos engineering tests..."
	pytest -v -m chaos
	@echo "✅ Chaos engineering tests completed"

test-performance: ## Run performance benchmarks
	@echo "⚡ Running performance benchmarks..."
	pytest -v -m performance --benchmark-only
	@echo "✅ Performance benchmarks completed"

test-data-validation: ## Run data validation tests
	@echo "🔍 Running data validation tests..."
	pytest -v -m indian_context data-validation/
	@echo "✅ Data validation tests completed"

# Indian context specific tests
test-indian: ## Run all Indian context tests
	@echo "🇮🇳 Running all Indian context tests..."
	pytest -v -m indian_context
	@echo "✅ Indian context tests completed"

test-indian-data: ## Test Indian data formats
	@echo "📋 Testing Indian data formats..."
	pytest -v -m "indian_context and data_validation"
	@echo "✅ Indian data format tests completed"

test-indian-banking: ## Test Indian banking scenarios
	@echo "🏦 Testing Indian banking scenarios..."
	pytest -v -m "indian_context and banking"
	@echo "✅ Indian banking tests completed"

test-indian-festivals: ## Test festival traffic scenarios
	@echo "🎉 Testing festival traffic scenarios..."
	pytest -v -m "indian_context and festivals"
	@echo "✅ Festival scenario tests completed"

# Parallel test execution
test-parallel: ## Run tests in parallel
	@echo "⚡ Running tests in parallel..."
	pytest -n auto -v
	@echo "✅ Parallel tests completed"

test-parallel-unit: ## Run unit tests in parallel
	@echo "⚡ Running unit tests in parallel..."
	pytest -n auto -v -m unit
	@echo "✅ Parallel unit tests completed"

test-parallel-integration: ## Run integration tests in parallel
	@echo "⚡ Running integration tests in parallel..."
	pytest -n auto -v -m integration
	@echo "✅ Parallel integration tests completed"

# Test filtering and reporting
test-fast: ## Run only fast tests (exclude slow ones)
	@echo "🏃 Running fast tests only..."
	pytest -v -m "not slow"
	@echo "✅ Fast tests completed"

test-slow: ## Run only slow tests
	@echo "🐌 Running slow tests only..."
	pytest -v -m slow
	@echo "✅ Slow tests completed"

test-critical: ## Run only critical tests
	@echo "🚨 Running critical tests only..."
	pytest -v -m critical
	@echo "✅ Critical tests completed"

# Coverage and reporting
coverage: ## Generate test coverage report
	@echo "📊 Generating coverage report..."
	pytest --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "✅ Coverage report generated in htmlcov/"

coverage-unit: ## Generate unit test coverage
	@echo "📊 Generating unit test coverage..."
	pytest -m unit --cov=unit --cov-report=html:htmlcov-unit --cov-report=term-missing
	@echo "✅ Unit test coverage generated"

coverage-integration: ## Generate integration test coverage
	@echo "📊 Generating integration test coverage..."
	pytest -m integration --cov=integration --cov-report=html:htmlcov-integration --cov-report=term-missing
	@echo "✅ Integration test coverage generated"

report: ## Generate comprehensive test report
	@echo "📋 Generating comprehensive test report..."
	pytest --html=report.html --self-contained-html
	@echo "✅ Test report generated: report.html"

# Code quality
lint: ## Run code linting
	@echo "🔍 Running code linting..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	pylint **/*.py --exit-zero || true
	@echo "✅ Linting completed"

format: ## Format code with black and isort
	@echo "✨ Formatting code..."
	black .
	isort .
	@echo "✅ Code formatting completed"

type-check: ## Run type checking with mypy
	@echo "🔍 Running type checking..."
	mypy . --ignore-missing-imports --check-untyped-defs || true
	@echo "✅ Type checking completed"

security-scan: ## Run security scanning
	@echo "🔒 Running security scanning..."
	bandit -r . -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true
	@echo "✅ Security scanning completed"

# Docker targets
docker-build: ## Build test Docker image
	@echo "🐳 Building test Docker image..."
	docker build -t hindi-podcast-tests .
	@echo "✅ Docker image built"

docker-test: ## Run tests in Docker container
	@echo "🐳 Running tests in Docker..."
	docker run --rm -v $(PWD):/app hindi-podcast-tests make test
	@echo "✅ Docker tests completed"

docker-test-unit: ## Run unit tests in Docker
	@echo "🐳 Running unit tests in Docker..."
	docker run --rm -v $(PWD):/app hindi-podcast-tests make test-unit
	@echo "✅ Docker unit tests completed"

# Environment management
env-create: ## Create virtual environment
	@echo "🔧 Creating virtual environment..."
	python -m venv venv
	@echo "✅ Virtual environment created"
	@echo "💡 Activate with: source venv/bin/activate"

env-activate: ## Show command to activate virtual environment
	@echo "💡 To activate virtual environment, run:"
	@echo "source venv/bin/activate"

env-deactivate: ## Show command to deactivate virtual environment
	@echo "💡 To deactivate virtual environment, run:"
	@echo "deactivate"

# Database setup for integration tests
db-setup: ## Setup test databases
	@echo "🗄️ Setting up test databases..."
	docker run -d --name test-postgres -e POSTGRES_PASSWORD=testpass -e POSTGRES_USER=testuser -e POSTGRES_DB=testdb -p 5432:5432 postgres:15
	docker run -d --name test-redis -p 6379:6379 redis:7-alpine
	docker run -d --name test-consul -p 8500:8500 consul:1.16
	@echo "✅ Test databases started"

db-teardown: ## Teardown test databases
	@echo "🗄️ Tearing down test databases..."
	docker stop test-postgres test-redis test-consul || true
	docker rm test-postgres test-redis test-consul || true
	@echo "✅ Test databases removed"

db-status: ## Check test database status
	@echo "🗄️ Checking test database status..."
	@echo "PostgreSQL:"
	@docker ps --filter name=test-postgres --format "table {{.Names}}\t{{.Status}}" || echo "Not running"
	@echo "Redis:"
	@docker ps --filter name=test-redis --format "table {{.Names}}\t{{.Status}}" || echo "Not running"
	@echo "Consul:"
	@docker ps --filter name=test-consul --format "table {{.Names}}\t{{.Status}}" || echo "Not running"

# Cleanup targets
clean: ## Clean up generated files
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "htmlcov*" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type f -name "junit-*.xml" -delete
	find . -type f -name "*.log" -delete
	rm -f report.html
	rm -f bandit-report.json
	rm -f safety-report.json
	@echo "✅ Cleanup completed"

clean-all: clean db-teardown ## Clean everything including databases
	@echo "🧹 Complete cleanup..."
	docker system prune -f || true
	@echo "✅ Complete cleanup finished"

# Continuous Integration helpers
ci-setup: ## Setup CI environment
	@echo "🤖 Setting up CI environment..."
	@$(MAKE) setup
	@$(MAKE) check-deps
	@echo "✅ CI environment ready"

ci-test: ## Run CI test suite
	@echo "🤖 Running CI test suite..."
	@$(MAKE) test-unit
	@$(MAKE) test-integration
	@$(MAKE) test-security
	@$(MAKE) test-data-validation
	@echo "✅ CI tests completed"

ci-report: ## Generate CI reports
	@echo "🤖 Generating CI reports..."
	@$(MAKE) coverage
	@$(MAKE) lint
	@$(MAKE) security-scan
	@echo "✅ CI reports generated"

# Development helpers
dev-setup: ## Setup development environment
	@echo "🛠️ Setting up development environment..."
	@$(MAKE) env-create
	@echo "Now run: source venv/bin/activate && make setup"

dev-test: ## Run tests suitable for development
	@echo "🛠️ Running development tests..."
	@$(MAKE) test-fast
	@$(MAKE) lint
	@echo "✅ Development tests completed"

watch: ## Watch for file changes and run tests
	@echo "👀 Watching for file changes..."
	@command -v entr >/dev/null 2>&1 || (echo "Install entr: brew install entr" && exit 1)
	find . -name "*.py" | entr -c make test-fast

# Indian specific helpers
mumbai-test: ## Test with Mumbai region settings
	@echo "🌆 Testing with Mumbai region..."
	INDIAN_REGION=mumbai pytest -v -m indian_context

delhi-test: ## Test with Delhi region settings
	@echo "🏛️ Testing with Delhi region..."
	INDIAN_REGION=delhi pytest -v -m indian_context

bangalore-test: ## Test with Bangalore region settings
	@echo "🌃 Testing with Bangalore region..."
	INDIAN_REGION=bangalore pytest -v -m indian_context

# Performance testing helpers
perf-test-quick: ## Quick performance test
	@echo "⚡ Running quick performance test..."
	pytest -v -m performance --benchmark-min-rounds=1

perf-test-thorough: ## Thorough performance test
	@echo "⚡ Running thorough performance test..."
	pytest -v -m performance --benchmark-min-rounds=10

# Load testing with different scenarios
load-test-startup: ## Simulate startup traffic
	@echo "🚀 Simulating startup traffic..."
	k6 run --vus 50 --duration 1m -e K6_SCENARIO=startup load/k6-scripts/api-gateway-load-test.js

load-test-maintenance: ## Simulate maintenance window traffic
	@echo "🔧 Simulating maintenance window traffic..."
	k6 run --vus 5 --duration 30s -e K6_SCENARIO=maintenance load/k6-scripts/api-gateway-load-test.js

# Documentation helpers
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "Documentation available in docs/testing-guide.md"
	@echo "✅ Documentation ready"

docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	@command -v python3 >/dev/null 2>&1 && cd docs && python3 -m http.server 8000 || echo "Python 3 not available"

# Version information
version: ## Show version information
	@echo "🔢 Version Information:"
	@echo "Python: $(shell python --version)"
	@echo "Pytest: $(shell pytest --version | head -1)"
	@echo "K6: $(shell k6 version 2>/dev/null || echo 'Not installed')"
	@echo "Docker: $(shell docker --version 2>/dev/null || echo 'Not installed')"

# Status check
status: ## Show testing framework status
	@echo "📊 Testing Framework Status:"
	@echo "Environment: $(TEST_ENV)"
	@echo "Region: $(INDIAN_REGION)"
	@echo "Test files: $(shell find . -name 'test_*.py' | wc -l)"
	@echo "Test categories:"
	@echo "  - Unit tests: $(shell find unit/ -name 'test_*.py' | wc -l)"
	@echo "  - Integration tests: $(shell find integration/ -name 'test_*.py' | wc -l)"
	@echo "  - E2E tests: $(shell find e2e/ -name '*.py' | wc -l)"
	@echo "  - Security tests: $(shell find security/ -name '*.py' | wc -l)"
	@echo "  - Performance tests: $(shell find performance/ -name '*.py' | wc -l)"
	@echo "  - Data validation: $(shell find data-validation/ -name '*.py' | wc -l)"
	@echo "  - Chaos tests: $(shell find chaos/ -name '*.py' | wc -l)"
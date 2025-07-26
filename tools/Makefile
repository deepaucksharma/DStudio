# Makefile for Pattern Excellence Tools
#
# Common tasks for pattern classification, validation, and health tracking

# Variables
PYTHON := python3
PATTERNS_DIR := ../docs/patterns
OUTPUT_DIR := ../pattern-reports
HEALTH_DIR := ../health-dashboard
MATRIX_DIR := ../comparison-matrices

# Default target
.PHONY: help
help:
	@echo "Pattern Excellence Tools - Available Commands:"
	@echo ""
	@echo "  make classify-patterns    - Classify all patterns based on metrics"
	@echo "  make validate-patterns    - Validate pattern excellence metadata"
	@echo "  make update-health       - Update pattern health metrics and dashboard"
	@echo "  make generate-reports    - Generate all reports (classify + validate + health)"
	@echo "  make update-front-matter - Update pattern front matter with excellence metadata"
	@echo "  make comparison-matrix   - Generate pattern comparison matrices"
	@echo "  make quarterly-review    - Export data for quarterly review"
	@echo "  make clean              - Remove generated reports and dashboards"
	@echo "  make install-deps       - Install Python dependencies"
	@echo ""
	@echo "Single Pattern Commands:"
	@echo "  make classify-pattern PATTERN=<name>   - Classify a specific pattern"
	@echo "  make validate-pattern PATTERN=<name>   - Validate a specific pattern"
	@echo "  make update-pattern PATTERN=<name>     - Update front matter for a pattern"
	@echo ""
	@echo "Options:"
	@echo "  GITHUB_TOKEN=<token>  - Set GitHub token for API calls"
	@echo "  DRY_RUN=true         - Run updates in dry-run mode"

# Create output directories
.PHONY: create-dirs
create-dirs:
	@mkdir -p $(OUTPUT_DIR) $(HEALTH_DIR) $(MATRIX_DIR)

# Install dependencies
.PHONY: install-deps
install-deps:
	@echo "Installing Python dependencies..."
	@pip install pyyaml requests matplotlib numpy
	@echo "Dependencies installed successfully!"

# Classify all patterns
.PHONY: classify-patterns
classify-patterns: create-dirs
	@echo "Classifying patterns based on excellence criteria..."
	@$(PYTHON) scripts/pattern-classifier.py \
		--patterns-dir $(PATTERNS_DIR) \
		--output $(OUTPUT_DIR)/pattern_classification_report.md \
		$(if $(GITHUB_TOKEN),--github-token $(GITHUB_TOKEN))
	@echo "Classification complete! Report: $(OUTPUT_DIR)/pattern_classification_report.md"

# Classify single pattern
.PHONY: classify-pattern
classify-pattern:
	@if [ -z "$(PATTERN)" ]; then \
		echo "Error: PATTERN variable not set. Usage: make classify-pattern PATTERN=<name>"; \
		exit 1; \
	fi
	@echo "Classifying pattern: $(PATTERN)..."
	@$(PYTHON) scripts/pattern-classifier.py \
		--patterns-dir $(PATTERNS_DIR) \
		--pattern $(PATTERN) \
		$(if $(GITHUB_TOKEN),--github-token $(GITHUB_TOKEN))

# Validate all patterns
.PHONY: validate-patterns
validate-patterns: create-dirs
	@echo "Validating pattern excellence metadata..."
	@$(PYTHON) scripts/pattern-validator.py \
		--patterns-dir $(PATTERNS_DIR) \
		--output $(OUTPUT_DIR)/pattern_validation_report.md
	@echo "Validation complete! Report: $(OUTPUT_DIR)/pattern_validation_report.md"

# Validate single pattern
.PHONY: validate-pattern
validate-pattern:
	@if [ -z "$(PATTERN)" ]; then \
		echo "Error: PATTERN variable not set. Usage: make validate-pattern PATTERN=<name>"; \
		exit 1; \
	fi
	@echo "Validating pattern: $(PATTERN)..."
	@$(PYTHON) scripts/pattern-validator.py \
		--patterns-dir $(PATTERNS_DIR) \
		--pattern $(PATTERN)

# Update pattern health metrics
.PHONY: update-health
update-health: create-dirs classify-patterns
	@echo "Updating pattern health dashboard..."
	@$(PYTHON) health-tracking/pattern-health-dashboard.py \
		--patterns-dir $(PATTERNS_DIR) \
		--output-dir $(HEALTH_DIR)
	@echo "Health dashboard updated! View at: $(HEALTH_DIR)/health_summary.md"

# Update front matter for all patterns
.PHONY: update-front-matter
update-front-matter: create-dirs
	@echo "Updating pattern front matter..."
	@$(PYTHON) scripts/update-front-matter.py \
		--patterns-dir $(PATTERNS_DIR) \
		--output $(OUTPUT_DIR)/front_matter_update_report.md \
		$(if $(DRY_RUN),--dry-run)
	@echo "Front matter update complete! Report: $(OUTPUT_DIR)/front_matter_update_report.md"

# Update single pattern
.PHONY: update-pattern
update-pattern:
	@if [ -z "$(PATTERN)" ]; then \
		echo "Error: PATTERN variable not set. Usage: make update-pattern PATTERN=<name>"; \
		exit 1; \
	fi
	@echo "Updating front matter for pattern: $(PATTERN)..."
	@$(PYTHON) scripts/update-front-matter.py \
		--patterns-dir $(PATTERNS_DIR) \
		--pattern $(PATTERN) \
		$(if $(DRY_RUN),--dry-run)

# Generate comparison matrices
.PHONY: comparison-matrix
comparison-matrix: create-dirs
	@echo "Generating pattern comparison matrices..."
	@$(PYTHON) scripts/generate-comparison-matrix.py \
		--patterns-dir $(PATTERNS_DIR) \
		--output-dir $(MATRIX_DIR)
	@echo "Comparison matrices generated! View at: $(MATRIX_DIR)/master_comparison.md"

# Generate all reports
.PHONY: generate-reports
generate-reports: classify-patterns validate-patterns update-health comparison-matrix
	@echo ""
	@echo "===================================="
	@echo "All reports generated successfully!"
	@echo "===================================="
	@echo "Classification: $(OUTPUT_DIR)/pattern_classification_report.md"
	@echo "Validation:     $(OUTPUT_DIR)/pattern_validation_report.md"
	@echo "Health:         $(HEALTH_DIR)/health_summary.md"
	@echo "Comparison:     $(MATRIX_DIR)/master_comparison.md"

# Export quarterly review data
.PHONY: quarterly-review
quarterly-review: create-dirs update-health
	@echo "Exporting quarterly review data..."
	@$(PYTHON) health-tracking/pattern-health-dashboard.py \
		--patterns-dir $(PATTERNS_DIR) \
		--output-dir $(OUTPUT_DIR) \
		--export-quarterly
	@echo "Quarterly data exported to: $(OUTPUT_DIR)/quarterly_review_*.json"

# Clean generated files
.PHONY: clean
clean:
	@echo "Cleaning generated reports and dashboards..."
	@rm -rf $(OUTPUT_DIR) $(HEALTH_DIR) $(MATRIX_DIR)
	@rm -f $(PATTERNS_DIR)/pattern_metadata.json
	@rm -rf $(PATTERNS_DIR)/.backups
	@echo "Clean complete!"

# Quick status check
.PHONY: status
status:
	@echo "Pattern Excellence Status:"
	@echo "========================="
	@if [ -f $(OUTPUT_DIR)/pattern_classification_report.md ]; then \
		echo "✅ Classification report exists"; \
	else \
		echo "❌ Classification report missing"; \
	fi
	@if [ -f $(OUTPUT_DIR)/pattern_validation_report.md ]; then \
		echo "✅ Validation report exists"; \
	else \
		echo "❌ Validation report missing"; \
	fi
	@if [ -f $(HEALTH_DIR)/health_summary.md ]; then \
		echo "✅ Health dashboard exists"; \
	else \
		echo "❌ Health dashboard missing"; \
	fi
	@if [ -f $(MATRIX_DIR)/master_comparison.md ]; then \
		echo "✅ Comparison matrix exists"; \
	else \
		echo "❌ Comparison matrix missing"; \
	fi

# Development helpers
.PHONY: test-classify
test-classify:
	@echo "Testing pattern classification on 'circuit-breaker'..."
	@$(PYTHON) scripts/pattern-classifier.py \
		--patterns-dir $(PATTERNS_DIR) \
		--pattern circuit-breaker

.PHONY: test-validate
test-validate:
	@echo "Testing pattern validation on 'circuit-breaker'..."
	@$(PYTHON) scripts/pattern-validator.py \
		--patterns-dir $(PATTERNS_DIR) \
		--pattern circuit-breaker

.PHONY: dry-run
dry-run:
	@echo "Running front matter update in dry-run mode..."
	@$(MAKE) update-front-matter DRY_RUN=true
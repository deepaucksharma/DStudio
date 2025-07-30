#!/bin/bash
# Pattern Count Validation Script
# Validates that pattern counts mentioned in documentation match actual file counts

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATTERN_LIB_DIR="$PROJECT_ROOT/docs/pattern-library"
ERRORS=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ERRORS=$((ERRORS + 1))
}

# Count actual patterns
count_patterns() {
    local total=0
    
    for category_dir in "$PATTERN_LIB_DIR"/*; do
        if [[ -d "$category_dir" && $(basename "$category_dir") != "__pycache__" ]]; then
            category_count=$(find "$category_dir" -name "*.md" -not -name "index.md" | wc -l)
            total=$((total + category_count))
        fi
    done
    
    echo $total
}

# Count patterns by category
count_by_category() {
    local category="$1"
    local category_dir="$PATTERN_LIB_DIR/$category"
    
    if [[ -d "$category_dir" ]]; then
        find "$category_dir" -name "*.md" -not -name "index.md" | wc -l
    else
        echo 0
    fi
}

# Validate count in file
validate_count_in_file() {
    local file="$1"
    local expected_count="$2"
    local file_basename=$(basename "$file")
    
    if [[ ! -f "$file" ]]; then
        warn "File not found: $file"
        return
    fi
    
    log "Checking pattern counts in $file_basename..."
    
    # Common patterns to look for
    local patterns=(
        '[0-9]+\s+[Pp]atterns?'
        '[Pp]attern\s+[Ll]ibrary.*?[0-9]+'
        '[0-9]+\s+architectural\s+patterns?'
        'Total.*?[0-9]+.*?patterns?'
        '[0-9]+\s+battle-tested\s+patterns?'
        '[0-9]+\s+production-ready\s+patterns?'
    )
    
    local found_issues=0
    
    while IFS= read -r line_num; do
        local line_content=$(sed -n "${line_num}p" "$file")
        
        for pattern in "${patterns[@]}"; do
            if echo "$line_content" | grep -qiE "$pattern"; then
                local numbers=$(echo "$line_content" | grep -oE '[0-9]+')
                
                for number in $numbers; do
                    # Skip small numbers that are likely not pattern counts
                    if [[ $number -lt 10 ]]; then
                        continue
                    fi
                    
                    # Check if this number is close to our expected count
                    local diff=$((number - expected_count))
                    local abs_diff=${diff#-} # absolute value
                    
                    if [[ $abs_diff -gt 5 ]]; then
                        error "Line $line_num in $file_basename: Found count $number, expected ~$expected_count"
                        error "  Content: $line_content"
                        found_issues=1
                    else
                        log "  ✓ Line $line_num: Count $number is close to expected $expected_count"
                    fi
                done
            fi
        done
    done < <(grep -n -iE "$(IFS='|'; echo "${patterns[*]}")" "$file" | cut -d: -f1)
    
    if [[ $found_issues -eq 0 ]]; then
        log "  ✓ All pattern counts in $file_basename appear correct"
    fi
}

# Main validation
main() {
    log "Starting pattern count validation..."
    
    # Count total patterns
    local total_patterns
    total_patterns=$(count_patterns)
    log "Found $total_patterns total patterns"
    
    # Count by category
    declare -A category_counts
    for category_dir in "$PATTERN_LIB_DIR"/*; do
        if [[ -d "$category_dir" ]]; then
            local category=$(basename "$category_dir")
            if [[ "$category" != "__pycache__" ]]; then
                category_counts["$category"]=$(count_by_category "$category")
                log "  $category: ${category_counts[$category]} patterns"
            fi
        fi
    done
    
    # Files to check
    local files_to_check=(
        "$PROJECT_ROOT/README.md"
        "$PROJECT_ROOT/CLAUDE.md"
        "$PROJECT_ROOT/docs/index.md"
        "$PROJECT_ROOT/docs/pattern-library/index.md"
    )
    
    # Validate each file
    for file in "${files_to_check[@]}"; do
        validate_count_in_file "$file" "$total_patterns"
    done
    
    # Validate category-specific files
    for category in "${!category_counts[@]}"; do
        local category_index="$PATTERN_LIB_DIR/$category/index.md"
        if [[ -f "$category_index" ]]; then
            validate_count_in_file "$category_index" "${category_counts[$category]}"
        fi
    done
    
    # Summary
    echo
    log "Pattern Count Validation Summary:"
    log "  Total patterns: $total_patterns"
    log "  Categories checked: ${#category_counts[@]}"
    log "  Files validated: $((${#files_to_check[@]} + ${#category_counts[@]}))"
    
    if [[ $ERRORS -eq 0 ]]; then
        log "✅ All pattern counts appear correct!"
        exit 0
    else
        error "❌ Found $ERRORS pattern count inconsistencies"
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
Pattern Count Validation Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    --fix           Attempt to fix count inconsistencies (not implemented)

DESCRIPTION:
    Validates that pattern counts mentioned in documentation files match
    the actual number of patterns found in the pattern library.

    Checked files:
    - README.md
    - CLAUDE.md  
    - docs/index.md
    - docs/pattern-library/index.md
    - docs/pattern-library/*/index.md

EXIT CODES:
    0    All counts are correct
    1    Found count inconsistencies
    2    Invalid arguments or file access errors

EXAMPLES:
    $0                  # Validate all pattern counts
    $0 --verbose        # Validate with detailed output
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            set -x
            shift
            ;;
        --fix)
            warn "Fix mode not yet implemented"
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 2
            ;;
    esac
done

# Run main function
main
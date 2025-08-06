#!/bin/bash
#
# Architects Handbook - Link Validation Script
# Comprehensive link checking for internal and external references
#

set -euo pipefail

# Configuration
BASE_DIR="docs/architects-handbook"
REPORT_FILE="link_validation_report.txt"
TEMP_DIR=$(mktemp -d)
PARALLEL_JOBS=4

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_FILES=0
TOTAL_LINKS=0
BROKEN_INTERNAL=0
BROKEN_EXTERNAL=0
SUSPICIOUS_LINKS=0

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Extract all markdown links from a file
extract_links() {
    local file="$1"
    # Extract [text](url) patterns, handling multiline links
    grep -oP '\[([^\]]*)\]\(([^)]+)\)' "$file" 2>/dev/null | \
        sed -n 's/\[.*\](\(.*\))/\1/p' || true
}

# Check if internal file exists
check_internal_link() {
    local file="$1"
    local link="$2"
    local base_path
    
    # Handle different link formats
    if [[ "$link" =~ ^/DStudio/ ]]; then
        # Absolute path from repository root
        base_path="${link#/DStudio/}"
        if [[ -f "$base_path" ]]; then
            return 0
        fi
    elif [[ "$link" =~ ^\.\./ ]]; then
        # Relative path going up directories
        base_path=$(dirname "$file")
        resolved_path=$(realpath -m "$base_path/$link" 2>/dev/null)
        if [[ -f "$resolved_path" ]]; then
            return 0
        fi
    elif [[ "$link" =~ ^[^/] ]] && [[ "$link" =~ \.md$ ]]; then
        # Relative path in same directory
        base_path=$(dirname "$file")
        if [[ -f "$base_path/$link" ]]; then
            return 0
        fi
    elif [[ "$link" =~ ^# ]]; then
        # Anchor link within same file
        return 0
    fi
    
    return 1
}

# Check external links with retry logic
check_external_link() {
    local url="$1"
    local max_retries=3
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        if curl -s --head --max-time 10 --retry 1 "$url" > /dev/null 2>&1; then
            return 0
        fi
        ((retry++))
        sleep 1
    done
    
    return 1
}

# Analyze a single markdown file
analyze_file() {
    local file="$1"
    local file_report="$TEMP_DIR/$(basename "$file").report"
    local links_found=0
    local file_issues=0
    
    log "Analyzing: $file"
    
    # Extract all links
    while IFS= read -r link; do
        if [[ -z "$link" ]]; then
            continue
        fi
        
        ((links_found++))
        
        # Classify link type
        if [[ "$link" =~ ^https?:// ]]; then
            # External HTTP/HTTPS link
            if ! check_external_link "$link"; then
                echo "BROKEN_EXTERNAL: $link in $file" >> "$file_report"
                ((file_issues++))
            fi
        elif [[ "$link" =~ ^mailto: ]]; then
            # Email link - just validate format
            if [[ ! "$link" =~ ^mailto:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
                echo "INVALID_EMAIL: $link in $file" >> "$file_report"
                ((file_issues++))
            fi
        elif [[ "$link" =~ \.md$ ]] || [[ "$link" =~ ^/ ]] || [[ "$link" =~ ^\.\./ ]] || [[ "$link" =~ ^# ]]; then
            # Internal link
            if ! check_internal_link "$file" "$link"; then
                echo "BROKEN_INTERNAL: $link in $file" >> "$file_report"
                ((file_issues++))
            fi
        else
            # Suspicious or unclassified link
            echo "SUSPICIOUS: $link in $file" >> "$file_report"
            ((file_issues++))
        fi
    done < <(extract_links "$file")
    
    # Report file statistics
    echo "FILE_STATS: $file - Links: $links_found, Issues: $file_issues" >> "$file_report"
    
    return 0
}

# Process files in parallel
process_files_parallel() {
    local files=("$@")
    local pids=()
    local batch_size=$((${#files[@]} / PARALLEL_JOBS))
    
    if [[ $batch_size -eq 0 ]]; then
        batch_size=1
    fi
    
    log "Processing ${#files[@]} files in batches of $batch_size"
    
    for ((i = 0; i < ${#files[@]}; i += batch_size)); do
        {
            for ((j = i; j < i + batch_size && j < ${#files[@]}; j++)); do
                analyze_file "${files[j]}"
            done
        } &
        
        pids+=($!)
        
        # Limit concurrent jobs
        if [[ ${#pids[@]} -ge $PARALLEL_JOBS ]]; then
            wait "${pids[0]}"
            pids=("${pids[@]:1}")
        fi
    done
    
    # Wait for all remaining jobs
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
}

# Generate consolidated report
generate_report() {
    log "Generating consolidated report..."
    
    {
        echo "# Architects Handbook - Link Validation Report"
        echo "Generated: $(date)"
        echo "=============================================="
        echo
        
        # Count issues by type
        local broken_internal_count=$(find "$TEMP_DIR" -name "*.report" -exec cat {} \; | grep -c "BROKEN_INTERNAL:" || true)
        local broken_external_count=$(find "$TEMP_DIR" -name "*.report" -exec cat {} \; | grep -c "BROKEN_EXTERNAL:" || true)
        local suspicious_count=$(find "$TEMP_DIR" -name "*.report" -exec cat {} \; | grep -c "SUSPICIOUS:" || true)
        local invalid_email_count=$(find "$TEMP_DIR" -name "*.report" -exec cat {} \; | grep -c "INVALID_EMAIL:" || true)
        
        # Summary
        echo "## Summary"
        echo "- Files Analyzed: $TOTAL_FILES"
        echo "- Broken Internal Links: $broken_internal_count"
        echo "- Broken External Links: $broken_external_count"
        echo "- Suspicious Links: $suspicious_count"
        echo "- Invalid Email Links: $invalid_email_count"
        echo "- Total Issues: $((broken_internal_count + broken_external_count + suspicious_count + invalid_email_count))"
        echo
        
        # Detailed breakdown
        if [[ $broken_internal_count -gt 0 ]]; then
            echo "## Broken Internal Links"
            find "$TEMP_DIR" -name "*.report" -exec grep "BROKEN_INTERNAL:" {} \; | sort
            echo
        fi
        
        if [[ $broken_external_count -gt 0 ]]; then
            echo "## Broken External Links"
            find "$TEMP_DIR" -name "*.report" -exec grep "BROKEN_EXTERNAL:" {} \; | sort
            echo
        fi
        
        if [[ $suspicious_count -gt 0 ]]; then
            echo "## Suspicious Links"
            find "$TEMP_DIR" -name "*.report" -exec grep "SUSPICIOUS:" {} \; | sort
            echo
        fi
        
        if [[ $invalid_email_count -gt 0 ]]; then
            echo "## Invalid Email Links"
            find "$TEMP_DIR" -name "*.report" -exec grep "INVALID_EMAIL:" {} \; | sort
            echo
        fi
        
        # File statistics
        echo "## File Statistics"
        find "$TEMP_DIR" -name "*.report" -exec grep "FILE_STATS:" {} \; | \
            sort -k3 -n | tail -10
        echo
        
        # Set global counters for exit code
        BROKEN_INTERNAL=$broken_internal_count
        BROKEN_EXTERNAL=$broken_external_count
        SUSPICIOUS_LINKS=$suspicious_count
        
    } > "$REPORT_FILE"
}

# Cleanup function
cleanup() {
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
}

# Main execution
main() {
    log "Starting Architects Handbook Link Validation"
    echo "============================================="
    
    # Verify base directory exists
    if [[ ! -d "$BASE_DIR" ]]; then
        error "Base directory not found: $BASE_DIR"
        return 1
    fi
    
    # Set up cleanup trap
    trap cleanup EXIT
    
    # Find all markdown files
    mapfile -t md_files < <(find "$BASE_DIR" -name "*.md" -type f)
    TOTAL_FILES=${#md_files[@]}
    
    if [[ $TOTAL_FILES -eq 0 ]]; then
        error "No markdown files found in $BASE_DIR"
        return 1
    fi
    
    log "Found $TOTAL_FILES markdown files to analyze"
    
    # Process files
    process_files_parallel "${md_files[@]}"
    
    # Generate report
    generate_report
    
    # Display results
    echo
    if [[ $BROKEN_INTERNAL -eq 0 && $BROKEN_EXTERNAL -eq 0 ]]; then
        success "All links validated successfully!"
        success "Report saved to: $REPORT_FILE"
        return 0
    else
        if [[ $BROKEN_INTERNAL -gt 0 ]]; then
            error "Found $BROKEN_INTERNAL broken internal links"
        fi
        if [[ $BROKEN_EXTERNAL -gt 0 ]]; then
            error "Found $BROKEN_EXTERNAL broken external links"
        fi
        if [[ $SUSPICIOUS_LINKS -gt 0 ]]; then
            warning "Found $SUSPICIOUS_LINKS suspicious links"
        fi
        
        warning "Link validation completed with issues"
        warning "Report saved to: $REPORT_FILE"
        return 1
    fi
}

# Check dependencies
check_dependencies() {
    local missing_deps=()
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if ! command -v grep &> /dev/null; then
        missing_deps+=("grep")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "Missing dependencies: ${missing_deps[*]}"
        error "Please install missing dependencies and try again"
        return 1
    fi
    
    return 0
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if ! check_dependencies; then
        exit 1
    fi
    
    main "$@"
    exit $?
fi
#!/bin/bash

#######################################################################
# Production Rollback Script for Indian E-commerce Platform
# Episode 092: Container Orchestration - Emergency Rollback
# Context: Fast and safe rollback for Flipkart-style production environment
#######################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Indian specific configuration
INDIAN_TIMEZONE="Asia/Kolkata"
PRIMARY_REGION="ap-south-1"

# Script metadata
SCRIPT_NAME="Flipkart Emergency Rollback"
SCRIPT_VERSION="1.0.0"
ROLLBACK_TIMESTAMP=$(TZ="$INDIAN_TIMEZONE" date +'%Y%m%d%H%M%S')

# Default values
REGION="mumbai"
STEPS_BACK=1
DRY_RUN=false
EMERGENCY_MODE=false
SKIP_CONFIRMATION=false
FORCE_ROLLBACK=false

# Rollback configuration
CLUSTERS=()
RELEASE_PREFIX="flipkart-prod"
MONITORING_ENABLED=true

# Print banner
print_banner() {
    echo -e "${RED}"
    echo "╔══════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                     🚨 EMERGENCY ROLLBACK SYSTEM 🚨                            ║"
    echo "║                    🇮🇳 Flipkart Indian E-commerce Platform                      ║"
    echo "║                                                                                  ║"
    echo "║  ⚡ Fast & Safe Production Rollback                                            ║"
    echo "║  🛡️  Indian Compliance Maintained                                              ║"
    echo "║  📅 $(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')                                              ║"
    echo "║  🔧 Version: $SCRIPT_VERSION                                                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Logging functions
log() {
    echo -e "${GREEN}[$(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')] INFO: $1${NC}"
}

emergency() {
    echo -e "${RED}[$(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')] 🚨 EMERGENCY: $1${NC}"
}

# Print usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

🚨 Flipkart Indian E-commerce Emergency Rollback System

OPTIONS:
    -r, --region         Indian region (mumbai|delhi|bangalore|all) [default: mumbai]
    -s, --steps         Number of releases to rollback [default: 1]
    -n, --dry-run       Perform dry run without actual rollback
    -e, --emergency     Emergency mode - skip safety checks
    -y, --yes           Skip confirmation prompts
    -f, --force         Force rollback even with warnings
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output

EMERGENCY SCENARIOS:
    # Quick rollback in Mumbai (most common)
    $0 --region mumbai --yes

    # Emergency rollback all regions
    $0 --region all --emergency --yes

    # Rollback 2 steps back
    $0 --region mumbai --steps 2

    # Dry run to see what would be rolled back
    $0 --dry-run --region all

REGIONS:
    mumbai      Primary region (70% traffic) - Immediate rollback
    delhi       Secondary region (20% traffic) 
    bangalore   Tertiary region (10% traffic)
    all         Rollback all regions sequentially

SAFETY FEATURES:
    🛡️  Automatic health checks before rollback
    📊 Traffic monitoring during rollback
    🔄 Automatic traffic switching
    📢 Real-time notifications
    ⚡ Sub-minute rollback time

EMERGENCY HOTLINE: +91-80-XXXX-XXXX (24/7 DevOps Support)

For more information: https://docs.flipkart.com/emergency-procedures
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -s|--steps)
                STEPS_BACK="$2"
                shift 2
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -e|--emergency)
                EMERGENCY_MODE=true
                SKIP_CONFIRMATION=true
                shift
                ;;
            -y|--yes)
                SKIP_CONFIRMATION=true
                shift
                ;;
            -f|--force)
                FORCE_ROLLBACK=true
                shift
                ;;
            -v|--verbose)
                DEBUG=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Validate rollback prerequisites
validate_prerequisites() {
    log "🔍 Validating rollback prerequisites..."

    # Check required tools
    local tools=("kubectl" "helm" "jq" "curl")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "Required tool '$tool' is not installed"
            exit 1
        fi
    done

    # Validate region
    if [[ "$REGION" != "mumbai" && "$REGION" != "delhi" && "$REGION" != "bangalore" && "$REGION" != "all" ]]; then
        error "Invalid region: $REGION. Must be 'mumbai', 'delhi', 'bangalore', or 'all'"
        exit 1
    fi

    # Validate steps back
    if [[ ! "$STEPS_BACK" =~ ^[1-9][0-9]*$ ]]; then
        error "Invalid steps back: $STEPS_BACK. Must be a positive integer"
        exit 1
    fi

    if [[ "$STEPS_BACK" -gt 10 ]]; then
        error "Too many steps back: $STEPS_BACK. Maximum allowed is 10"
        exit 1
    fi

    log "✅ Prerequisites validation completed"
}

# Setup cluster configurations based on region
setup_cluster_config() {
    log "🔧 Setting up cluster configurations for region: $REGION"

    case $REGION in
        mumbai)
            CLUSTERS=("flipkart-mumbai-prod")
            ;;
        delhi)
            CLUSTERS=("flipkart-delhi-prod")
            ;;
        bangalore)
            CLUSTERS=("flipkart-bangalore-prod")
            ;;
        all)
            # Priority order: Mumbai first (primary), then Delhi, then Bangalore
            CLUSTERS=("flipkart-mumbai-prod" "flipkart-delhi-prod" "flipkart-bangalore-prod")
            ;;
    esac

    log "📋 Target clusters: ${CLUSTERS[*]}"
}

# Check current system health
check_system_health() {
    if [[ "$EMERGENCY_MODE" == true ]]; then
        warn "⚡ Emergency mode: Skipping health checks for speed"
        return 0
    fi

    log "🏥 Checking current system health..."

    local health_issues=0

    # Check each cluster
    for cluster in "${CLUSTERS[@]}"; do
        local region_name=""
        case $cluster in
            *mumbai*) region_name="mumbai" ;;
            *delhi*) region_name="delhi" ;;
            *bangalore*) region_name="bangalore" ;;
        esac

        info "Checking health for cluster: $cluster ($region_name)"
        
        # Set kubectl context
        if ! kubectl config use-context "$cluster" &>/dev/null; then
            error "Failed to set context for cluster: $cluster"
            ((health_issues++))
            continue
        fi

        # Check cluster connectivity
        if ! kubectl cluster-info &>/dev/null; then
            error "Cannot connect to cluster: $cluster"
            ((health_issues++))
            continue
        fi

        # Check if pods are running
        local failed_pods
        failed_pods=$(kubectl get pods -n flipkart-production --field-selector=status.phase!=Running --no-headers 2>/dev/null | wc -l)
        if [[ $failed_pods -gt 0 ]]; then
            warn "Cluster $cluster has $failed_pods failed pods"
            ((health_issues++))
        fi

        # Check CPU and memory usage
        local high_cpu_nodes
        high_cpu_nodes=$(kubectl top nodes --no-headers 2>/dev/null | awk '$3 > 80 {print $1}' | wc -l)
        if [[ $high_cpu_nodes -gt 0 ]]; then
            warn "Cluster $cluster has $high_cpu_nodes nodes with high CPU usage"
        fi

        log "✅ Health check completed for cluster: $cluster"
    done

    if [[ $health_issues -gt 0 ]]; then
        warn "⚠️  Detected $health_issues health issues"
        if [[ "$FORCE_ROLLBACK" == false ]]; then
            read -p "Continue with rollback anyway? (y/N): " -r
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                info "Rollback cancelled by user"
                exit 0
            fi
        fi
    else
        log "✅ All systems healthy"
    fi
}

# Get available releases for rollback
get_available_releases() {
    local cluster=$1
    local region_name=""
    
    case $cluster in
        *mumbai*) region_name="mumbai" ;;
        *delhi*) region_name="delhi" ;;
        *bangalore*) region_name="bangalore" ;;
    esac

    log "📋 Getting available releases for cluster: $cluster ($region_name)"

    # Set kubectl context
    kubectl config use-context "$cluster" &>/dev/null

    # Get Helm releases
    local releases
    releases=$(helm list -n flipkart-production --filter "$RELEASE_PREFIX-$region_name" -o json 2>/dev/null | jq -r '.[].name' | sort -rV)

    if [[ -z "$releases" ]]; then
        error "No releases found for rollback in cluster: $cluster"
        return 1
    fi

    local release_array=($releases)
    local total_releases=${#release_array[@]}

    info "Found $total_releases releases in $region_name:"
    for i in "${!release_array[@]}"; do
        local release="${release_array[$i]}"
        local revision
        revision=$(helm get metadata "$release" -n flipkart-production 2>/dev/null | grep "^REVISION:" | awk '{print $2}')
        local status
        status=$(helm status "$release" -n flipkart-production -o json 2>/dev/null | jq -r '.info.status')
        
        if [[ $i -eq 0 ]]; then
            info "  $((i+1)). $release (revision: $revision, status: $status) [CURRENT]"
        else
            info "  $((i+1)). $release (revision: $revision, status: $status)"
        fi
    done

    # Check if we can rollback the requested number of steps
    if [[ $STEPS_BACK -ge $total_releases ]]; then
        error "Cannot rollback $STEPS_BACK steps - only $total_releases releases available"
        return 1
    fi

    # Store releases for this cluster
    eval "RELEASES_$region_name=(${release_array[*]})"
    
    return 0
}

# Confirm rollback action
confirm_rollback() {
    if [[ "$SKIP_CONFIRMATION" == true ]]; then
        return 0
    fi

    echo -e "${YELLOW}"
    echo "╔══════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                            🚨 ROLLBACK CONFIRMATION 🚨                          ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    warn "⚠️  You are about to perform a PRODUCTION ROLLBACK"
    info "📋 Rollback Details:"
    info "   • Region(s): $REGION"
    info "   • Steps back: $STEPS_BACK"
    info "   • Timestamp: $(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')"
    info "   • Emergency mode: $([ "$EMERGENCY_MODE" == true ] && echo "YES" || echo "NO")"

    if [[ "$DRY_RUN" == true ]]; then
        info "   • Mode: DRY RUN (no actual changes)"
    else
        warn "   • Mode: PRODUCTION ROLLBACK (REAL CHANGES)"
    fi

    echo
    read -p "⚠️  Are you sure you want to proceed? Type 'YES' to confirm: " -r
    if [[ "$REPLY" != "YES" ]]; then
        info "Rollback cancelled by user"
        exit 0
    fi

    log "✅ Rollback confirmed by user"
}

# Rollback a specific cluster
rollback_cluster() {
    local cluster=$1
    local region_name=""
    
    case $cluster in
        *mumbai*) region_name="mumbai" ;;
        *delhi*) region_name="delhi" ;;
        *bangalore*) region_name="bangalore" ;;
    esac

    log "🔄 Rolling back cluster: $cluster ($region_name)"

    # Set kubectl context
    kubectl config use-context "$cluster" &>/dev/null

    # Get releases for this region
    local releases_var="RELEASES_$region_name[@]"
    local releases=("${!releases_var}")
    
    if [[ ${#releases[@]} -eq 0 ]]; then
        error "No releases available for rollback in $region_name"
        return 1
    fi

    local current_release="${releases[0]}"
    local target_release="${releases[$STEPS_BACK]}"

    info "Rolling back from: $current_release"
    info "Rolling back to: $target_release"

    if [[ "$DRY_RUN" == true ]]; then
        info "DRY RUN: Would rollback release $current_release to revision $(($(helm get metadata "$current_release" -n flipkart-production 2>/dev/null | grep "^REVISION:" | awk '{print $2}') - STEPS_BACK))"
        return 0
    fi

    # Record rollback start time
    local rollback_start_time=$SECONDS

    # Perform the rollback
    info "⚡ Executing rollback..."
    if helm rollback "$current_release" 0 -n flipkart-production --wait --timeout=300s; then
        local rollback_duration=$((SECONDS - rollback_start_time))
        log "✅ Rollback completed successfully in ${rollback_duration}s for cluster: $cluster"
    else
        error "❌ Rollback failed for cluster: $cluster"
        return 1
    fi

    # Verify rollback
    info "🔍 Verifying rollback..."
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        local ready_pods
        ready_pods=$(kubectl get pods -n flipkart-production -l "app.kubernetes.io/instance=$current_release" --field-selector=status.phase=Running 2>/dev/null | grep -c "Running" || echo "0")
        
        local total_pods
        total_pods=$(kubectl get pods -n flipkart-production -l "app.kubernetes.io/instance=$current_release" 2>/dev/null | grep -c "api-gateway" || echo "0")
        
        if [[ $ready_pods -gt 0 && $ready_pods -eq $total_pods ]]; then
            log "✅ All pods are running after rollback"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            error "❌ Rollback verification failed - pods not ready within timeout"
            return 1
        fi
        
        info "Waiting for pods to be ready... ($ready_pods/$total_pods ready, attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done

    # Health check after rollback
    info "🏥 Performing post-rollback health check..."
    local base_url=""
    case $region_name in
        mumbai) base_url="https://api.flipkart.com" ;;
        delhi) base_url="https://delhi.flipkart.com" ;;
        bangalore) base_url="https://bangalore.flipkart.com" ;;
    esac

    if [[ -n "$base_url" ]]; then
        local health_attempts=10
        local health_attempt=1
        
        while [[ $health_attempt -le $health_attempts ]]; do
            if curl -sf "$base_url/health" >/dev/null 2>&1; then
                log "✅ Health check passed for $region_name"
                break
            fi
            
            if [[ $health_attempt -eq $health_attempts ]]; then
                warn "⚠️  Health check failed for $region_name after rollback"
                # Don't fail the rollback for health check failure
            fi
            
            info "Waiting for health check to pass... (attempt $health_attempt/$health_attempts)"
            sleep 5
            ((health_attempt++))
        done
    fi

    return 0
}

# Send rollback notifications
send_rollback_notifications() {
    local status="SUCCESS"
    local icon="✅"
    local color="warning"  # Orange for rollbacks

    if [[ $? -ne 0 ]]; then
        status="FAILED"
        icon="❌"
        color="danger"
    fi

    local message="🔄 $icon Flipkart Production Rollback $status

• Region: $REGION
• Steps back: $STEPS_BACK
• Time: $(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')
• Emergency mode: $([ "$EMERGENCY_MODE" == true ] && echo "YES" || echo "NO")
• Duration: $((SECONDS / 60))m $((SECONDS % 60))s
• Rollback ID: $ROLLBACK_TIMESTAMP"

    # Slack notification (if webhook URL is set)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" \
            "$SLACK_WEBHOOK_URL" &>/dev/null || warn "Failed to send Slack notification"
    fi

    # Teams notification (if webhook URL is set)
    if [[ -n "${TEAMS_WEBHOOK_URL:-}" ]]; then
        local teams_payload="{
            \"@type\": \"MessageCard\",
            \"@context\": \"http://schema.org/extensions\",
            \"themeColor\": \"$color\",
            \"summary\": \"Flipkart Rollback $status\",
            \"sections\": [{
                \"activityTitle\": \"$message\"
            }]
        }"
        curl -X POST -H 'Content-type: application/json' \
            --data "$teams_payload" \
            "$TEAMS_WEBHOOK_URL" &>/dev/null || warn "Failed to send Teams notification"
    fi

    # PagerDuty incident resolution (if rollback was successful)
    if [[ "$status" == "SUCCESS" && -n "${PAGERDUTY_INTEGRATION_KEY:-}" ]]; then
        local pd_payload="{
            \"routing_key\": \"$PAGERDUTY_INTEGRATION_KEY\",
            \"event_action\": \"resolve\",
            \"dedup_key\": \"flipkart-production-incident\",
            \"payload\": {
                \"summary\": \"Flipkart production rollback completed successfully\",
                \"severity\": \"info\"
            }
        }"
        curl -X POST -H 'Content-type: application/json' \
            --data "$pd_payload" \
            "https://events.pagerduty.com/v2/enqueue" &>/dev/null || warn "Failed to resolve PagerDuty incident"
    fi

    log "📧 Notifications sent"
}

# Cleanup function
cleanup() {
    log "🧹 Performing cleanup..."
    
    # Reset kubectl context
    kubectl config unset current-context &>/dev/null || true
    
    # Clean up temporary files
    rm -f /tmp/flipkart-rollback-* &>/dev/null || true
    
    log "✅ Cleanup completed"
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Main rollback function
main() {
    print_banner
    
    log "🚨 Starting $SCRIPT_NAME v$SCRIPT_VERSION"
    log "🆔 Rollback ID: $ROLLBACK_TIMESTAMP"
    
    if [[ "$EMERGENCY_MODE" == true ]]; then
        emergency "⚡ EMERGENCY MODE ACTIVATED - Fast rollback in progress"
    fi
    
    # Parse command line arguments
    parse_args "$@"
    
    # Validate prerequisites
    validate_prerequisites
    
    # Setup cluster configuration
    setup_cluster_config
    
    # Check system health (unless emergency mode)
    check_system_health
    
    # Get available releases for each cluster
    local clusters_ready=0
    for cluster in "${CLUSTERS[@]}"; do
        if get_available_releases "$cluster"; then
            ((clusters_ready++))
        fi
    done
    
    if [[ $clusters_ready -eq 0 ]]; then
        error "No clusters ready for rollback"
        exit 1
    fi
    
    # Confirm rollback action
    confirm_rollback
    
    # Perform rollback on each cluster
    local successful_rollbacks=0
    local failed_rollbacks=0
    
    for cluster in "${CLUSTERS[@]}"; do
        if rollback_cluster "$cluster"; then
            ((successful_rollbacks++))
        else
            ((failed_rollbacks++))
            
            # In emergency mode, continue with other clusters even if one fails
            if [[ "$EMERGENCY_MODE" == false ]]; then
                error "Stopping rollback due to failure in cluster: $cluster"
                break
            else
                warn "Continuing emergency rollback despite failure in cluster: $cluster"
            fi
        fi
    done
    
    # Send notifications
    send_rollback_notifications
    
    # Final summary
    echo
    log "🎯 Rollback Summary:"
    log "   • Total clusters: ${#CLUSTERS[@]}"
    log "   • Successful rollbacks: $successful_rollbacks"
    log "   • Failed rollbacks: $failed_rollbacks"
    log "   • Duration: $((SECONDS / 60)) minutes and $((SECONDS % 60)) seconds"
    log "   • Rollback ID: $ROLLBACK_TIMESTAMP"
    
    if [[ "$DRY_RUN" == true ]]; then
        warn "🧪 This was a DRY RUN - no actual changes were made"
    fi
    
    if [[ $failed_rollbacks -gt 0 ]]; then
        if [[ $successful_rollbacks -gt 0 ]]; then
            warn "⚠️  Partial rollback completed - some clusters failed"
            exit 2
        else
            error "❌ Rollback failed completely"
            exit 1
        fi
    else
        log "🎉 Rollback completed successfully!"
        
        if [[ "$MONITORING_ENABLED" == true ]]; then
            info "📊 Continue monitoring the system for the next 30 minutes"
            info "🔗 Grafana: https://grafana.flipkart.internal"
            info "📈 Metrics: https://prometheus.flipkart.internal"
        fi
    fi
}

# Run main function with all arguments
main "$@"
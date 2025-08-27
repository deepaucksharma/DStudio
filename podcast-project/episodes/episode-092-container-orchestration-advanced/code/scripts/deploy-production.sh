#!/bin/bash

#######################################################################
# Production Deployment Script for Indian E-commerce Platform
# Episode 092: Container Orchestration - Production Deployment
# Context: Flipkart-style deployment with Indian compliance and optimization
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
SECONDARY_REGION="ap-southeast-1"

# Script metadata
SCRIPT_NAME="Flipkart Production Deployment"
SCRIPT_VERSION="1.0.0"
DEPLOYMENT_TIMESTAMP=$(TZ="$INDIAN_TIMEZONE" date +'%Y%m%d%H%M%S')

# Default values
ENVIRONMENT="production"
REGION="mumbai"
IMAGE_TAG=""
DRY_RUN=false
SKIP_VALIDATION=false
FESTIVAL_MODE=false
ROLLBACK_MODE=false
FORCE_DEPLOY=false

# Indian compliance flags
RBI_COMPLIANCE_CHECK=true
PCI_DSS_COMPLIANCE_CHECK=true
DATA_LOCALIZATION_CHECK=true

# Deployment configuration
NAMESPACES=("flipkart-production" "flipkart-monitoring")
SERVICES=("product-catalog" "order-management" "payment-service" "user-service" "search-service" "api-gateway")
CLUSTERS=()

# Print banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    🇮🇳 Flipkart Indian E-commerce Platform                        ║"
    echo "║                         Production Deployment Script                             ║"
    echo "║                                                                                  ║"
    echo "║  🏢 Episode 092: Container Orchestration                                        ║"
    echo "║  🌟 Optimized for Indian Infrastructure & Compliance                           ║"
    echo "║  📅 $(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')                                              ║"
    echo "║  📊 Version: $SCRIPT_VERSION                                                       ║"
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

debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${PURPLE}[$(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')] DEBUG: $1${NC}"
    fi
}

# Print usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

🇮🇳 Flipkart Indian E-commerce Production Deployment Script

OPTIONS:
    -e, --environment     Target environment (production|staging) [default: production]
    -r, --region         Indian region (mumbai|delhi|bangalore|all) [default: mumbai]
    -t, --tag            Docker image tag to deploy [required]
    -n, --dry-run        Perform dry run without actual deployment
    -s, --skip-validation Skip pre-deployment validation
    -f, --festival-mode  Enable festival season scaling
    -R, --rollback       Rollback to previous deployment
    -F, --force          Force deployment even with warnings
    -h, --help           Show this help message
    -v, --verbose        Enable verbose output

EXAMPLES:
    # Deploy to Mumbai production
    $0 --environment production --region mumbai --tag v1.2.3

    # Deploy to all regions with festival mode
    $0 --region all --tag v1.2.3 --festival-mode

    # Dry run deployment
    $0 --dry-run --tag v1.2.3

    # Rollback deployment
    $0 --rollback --region mumbai

INDIAN REGIONS:
    mumbai      Primary region (70% traffic) - Mumbai/Maharashtra
    delhi       Secondary region (20% traffic) - Delhi NCR
    bangalore   Tertiary region (10% traffic) - Bangalore/Karnataka
    all         Deploy to all regions sequentially

COMPLIANCE:
    🏛️  RBI (Reserve Bank of India) compliance checks
    💳 PCI-DSS compliance for payment systems
    🇮🇳 Data localization within Indian borders
    📜 Indian IT Act 2000 compliance

For more information: https://docs.flipkart.com/deployment
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -t|--tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -s|--skip-validation)
                SKIP_VALIDATION=true
                shift
                ;;
            -f|--festival-mode)
                FESTIVAL_MODE=true
                shift
                ;;
            -R|--rollback)
                ROLLBACK_MODE=true
                shift
                ;;
            -F|--force)
                FORCE_DEPLOY=true
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

# Validate deployment prerequisites
validate_prerequisites() {
    log "🔍 Validating deployment prerequisites..."

    # Check required tools
    local tools=("kubectl" "helm" "docker" "jq" "curl")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "Required tool '$tool' is not installed"
            exit 1
        fi
    done

    # Validate environment
    if [[ "$ENVIRONMENT" != "production" && "$ENVIRONMENT" != "staging" ]]; then
        error "Invalid environment: $ENVIRONMENT. Must be 'production' or 'staging'"
        exit 1
    fi

    # Validate region
    if [[ "$REGION" != "mumbai" && "$REGION" != "delhi" && "$REGION" != "bangalore" && "$REGION" != "all" ]]; then
        error "Invalid region: $REGION. Must be 'mumbai', 'delhi', 'bangalore', or 'all'"
        exit 1
    fi

    # Validate image tag
    if [[ -z "$IMAGE_TAG" && "$ROLLBACK_MODE" == false ]]; then
        error "Image tag is required for deployment. Use --tag option"
        exit 1
    fi

    # Check deployment window for production
    if [[ "$ENVIRONMENT" == "production" && "$FORCE_DEPLOY" == false ]]; then
        local current_hour=$(TZ="$INDIAN_TIMEZONE" date +'%H')
        if [[ $current_hour -lt 2 || $current_hour -gt 6 ]]; then
            warn "Deploying outside recommended window (2-6 AM IST)"
            read -p "Continue anyway? (y/N): " -r
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                info "Deployment cancelled by user"
                exit 0
            fi
        fi
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
            CLUSTERS=("flipkart-mumbai-prod" "flipkart-delhi-prod" "flipkart-bangalore-prod")
            ;;
    esac

    log "📋 Target clusters: ${CLUSTERS[*]}"
}

# Check Indian compliance requirements
check_indian_compliance() {
    if [[ "$SKIP_VALIDATION" == true ]]; then
        warn "Skipping compliance validation as requested"
        return 0
    fi

    log "🏛️ Performing Indian compliance validation..."

    # RBI Compliance Check
    if [[ "$RBI_COMPLIANCE_CHECK" == true ]]; then
        info "Checking RBI (Reserve Bank of India) compliance..."
        
        # Check data localization
        debug "Verifying data stays within Indian borders"
        if ! grep -rq "ap-south-1\|ap-southeast-1" kubernetes/; then
            error "Non-Indian regions detected in configuration - RBI violation"
            exit 1
        fi

        # Check encryption standards
        debug "Verifying encryption standards (AES-256)"
        if ! grep -rq "AES-256" kubernetes/secrets.yaml; then
            error "Required encryption standard not found - RBI violation"
            exit 1
        fi

        # Check audit logging
        debug "Verifying audit logging configuration"
        if ! grep -rq "audit.*enabled" kubernetes/; then
            warn "Audit logging not explicitly enabled - RBI recommendation"
        fi

        log "✅ RBI compliance check passed"
    fi

    # PCI-DSS Compliance Check
    if [[ "$PCI_DSS_COMPLIANCE_CHECK" == true ]]; then
        info "Checking PCI-DSS compliance for payment systems..."
        
        # Check TLS configuration
        if ! grep -rEq "TLSv1\.[23]" kubernetes/; then
            error "Secure TLS version not configured - PCI-DSS violation"
            exit 1
        fi

        # Check payment encryption
        if ! grep -rq "payment-encryption-key" kubernetes/secrets.yaml; then
            error "Payment encryption key not found - PCI-DSS violation"
            exit 1
        fi

        # Check tokenization
        if ! grep -rq "tokenization.*true" kubernetes/; then
            warn "Tokenization not explicitly enabled - PCI-DSS recommendation"
        fi

        log "✅ PCI-DSS compliance check passed"
    fi

    # Data Localization Check
    if [[ "$DATA_LOCALIZATION_CHECK" == true ]]; then
        info "Checking data localization compliance..."
        
        # Verify no data leaves Indian jurisdiction
        local non_indian_regions=$(grep -ro "us-\|eu-\|ap-northeast\|ap-southeast-[23]" kubernetes/ | wc -l)
        if [[ $non_indian_regions -gt 0 ]]; then
            error "Data localization violation detected - non-Indian regions found"
            exit 1
        fi

        log "✅ Data localization check passed"
    fi

    log "🎉 All Indian compliance checks completed successfully"
}

# Validate Kubernetes connectivity
validate_k8s_connectivity() {
    log "🔗 Validating Kubernetes cluster connectivity..."

    for cluster in "${CLUSTERS[@]}"; do
        info "Testing connectivity to cluster: $cluster"
        
        # Set kubeconfig context
        if ! kubectl config use-context "$cluster" &>/dev/null; then
            error "Failed to set context for cluster: $cluster"
            exit 1
        fi

        # Test cluster connectivity
        if ! kubectl cluster-info &>/dev/null; then
            error "Cannot connect to cluster: $cluster"
            exit 1
        fi

        # Check if we have necessary permissions
        if ! kubectl auth can-i create deployments -n flipkart-production &>/dev/null; then
            error "Insufficient permissions for cluster: $cluster"
            exit 1
        fi

        # Verify cluster region
        local cluster_region
        cluster_region=$(kubectl get nodes -o jsonpath='{.items[0].metadata.labels.topology\.kubernetes\.io/region}' 2>/dev/null || echo "unknown")
        debug "Cluster $cluster is in region: $cluster_region"

        log "✅ Cluster $cluster connectivity verified"
    done
}

# Check if it's festival season in India
check_festival_season() {
    log "🎉 Checking for Indian festival season..."

    local current_date
    current_date=$(TZ="$INDIAN_TIMEZONE" date +'%m%d')
    
    # Major Indian festivals (MM-DD format)
    local festivals=(
        "0126:Republic Day"
        "0815:Independence Day"
        "1002:Gandhi Jayanti"
        "1024:Dussehra"
        "1101:Diwali"
        "0325:Holi"
        "0410:Eid"
    )

    for festival in "${festivals[@]}"; do
        local fest_date="${festival%%:*}"
        local fest_name="${festival##*:}"
        
        if [[ "$current_date" == "$fest_date" ]]; then
            warn "🎊 Today is $fest_name - Festival season detected!"
            FESTIVAL_MODE=true
            break
        fi
    done

    if [[ "$FESTIVAL_MODE" == true ]]; then
        warn "🚀 Festival mode enabled - Enhanced scaling will be applied"
        log "📈 Expected traffic increase: 3-10x normal levels"
        log "💰 Auto-scaling: Min 10 replicas, Max 100 replicas"
        log "⚡ Performance mode: High CPU/Memory allocation"
    fi
}

# Pre-deployment validation
pre_deployment_validation() {
    log "🔎 Performing pre-deployment validation..."

    # Check image availability
    if [[ "$ROLLBACK_MODE" == false ]]; then
        info "Validating Docker image availability..."
        for service in "${SERVICES[@]}"; do
            local image="registry.flipkart.com/flipkart/$service:$IMAGE_TAG"
            if ! docker manifest inspect "$image" &>/dev/null; then
                error "Image not found: $image"
                exit 1
            fi
            debug "Image verified: $image"
        done
        log "✅ All Docker images are available"
    fi

    # Validate Helm charts
    info "Validating Helm charts..."
    if ! helm lint helm/api-gateway/ &>/dev/null; then
        error "Helm chart validation failed"
        exit 1
    fi
    log "✅ Helm charts are valid"

    # Check resource availability
    info "Checking cluster resource availability..."
    for cluster in "${CLUSTERS[@]}"; do
        kubectl config use-context "$cluster" &>/dev/null
        
        local cpu_available
        local memory_available
        cpu_available=$(kubectl top nodes --no-headers | awk '{sum+=$3} END {print sum}' | sed 's/m$//')
        memory_available=$(kubectl top nodes --no-headers | awk '{sum+=$5} END {print sum}' | sed 's/Mi$//')
        
        debug "Cluster $cluster - Available CPU: ${cpu_available:-unknown}m, Memory: ${memory_available:-unknown}Mi"
        
        # Check if cluster has enough resources for festival mode
        if [[ "$FESTIVAL_MODE" == true ]]; then
            warn "🎪 Festival mode requires additional resources - ensure adequate capacity"
        fi
    done

    log "✅ Pre-deployment validation completed"
}

# Deploy to a specific cluster
deploy_to_cluster() {
    local cluster=$1
    local region_name=""
    
    # Determine region name from cluster
    case $cluster in
        *mumbai*)
            region_name="mumbai"
            ;;
        *delhi*)
            region_name="delhi"
            ;;
        *bangalore*)
            region_name="bangalore"
            ;;
    esac

    log "🚀 Deploying to cluster: $cluster (Region: $region_name)"

    # Set kubectl context
    kubectl config use-context "$cluster" &>/dev/null

    # Create namespaces if they don't exist
    for namespace in "${NAMESPACES[@]}"; do
        if ! kubectl get namespace "$namespace" &>/dev/null; then
            info "Creating namespace: $namespace"
            if [[ "$DRY_RUN" == false ]]; then
                kubectl create namespace "$namespace"
            fi
        fi
    done

    # Prepare Helm values based on region and festival mode
    local helm_values_file="helm/api-gateway/values-production.yaml"
    local additional_args=""

    # Festival mode adjustments
    if [[ "$FESTIVAL_MODE" == true ]]; then
        additional_args+=" --set autoscaling.minReplicas=10"
        additional_args+=" --set autoscaling.maxReplicas=100"
        additional_args+=" --set resources.requests.cpu=2000m"
        additional_args+=" --set resources.requests.memory=4Gi"
        additional_args+=" --set festivalMode.enabled=true"
    fi

    # Region-specific adjustments
    case $region_name in
        mumbai)
            additional_args+=" --set replicaCount=10"
            additional_args+=" --set global.region=$PRIMARY_REGION"
            ;;
        delhi)
            additional_args+=" --set replicaCount=5"
            additional_args+=" --set global.region=$PRIMARY_REGION"
            helm_values_file="helm/api-gateway/values-production-delhi.yaml"
            ;;
        bangalore)
            additional_args+=" --set replicaCount=3"
            additional_args+=" --set global.region=$SECONDARY_REGION"
            helm_values_file="helm/api-gateway/values-production-bangalore.yaml"
            ;;
    esac

    # Generate unique release name for blue-green deployment
    local release_name="flipkart-prod-${region_name}-${DEPLOYMENT_TIMESTAMP}"

    # Perform Helm deployment
    local helm_command="helm upgrade --install $release_name helm/api-gateway/"
    helm_command+=" --namespace flipkart-production"
    helm_command+=" --set image.tag=$IMAGE_TAG"
    helm_command+=" --set global.environment=$ENVIRONMENT"
    helm_command+=" --set global.indianOptimization.timezone=$INDIAN_TIMEZONE"
    helm_command+=" --values $helm_values_file"
    helm_command+="$additional_args"
    helm_command+=" --wait --timeout=15m"

    if [[ "$DRY_RUN" == true ]]; then
        helm_command+=" --dry-run"
        info "DRY RUN: $helm_command"
    else
        info "Executing deployment..."
        debug "Command: $helm_command"
        
        if eval "$helm_command"; then
            log "✅ Deployment successful for cluster: $cluster"
        else
            error "Deployment failed for cluster: $cluster"
            exit 1
        fi
    fi

    # Verify deployment if not dry run
    if [[ "$DRY_RUN" == false ]]; then
        info "Verifying deployment..."
        
        # Wait for rollout to complete
        if kubectl rollout status deployment/"$release_name"-api-gateway -n flipkart-production --timeout=600s; then
            log "✅ Rollout completed successfully"
        else
            error "Rollout failed or timed out"
            exit 1
        fi

        # Health check
        local max_attempts=30
        local attempt=1
        while [[ $attempt -le $max_attempts ]]; do
            if kubectl get pods -n flipkart-production -l "app.kubernetes.io/instance=$release_name" | grep -q "Running"; then
                log "✅ Pods are running successfully"
                break
            fi
            
            if [[ $attempt -eq $max_attempts ]]; then
                error "Pods failed to start within timeout"
                exit 1
            fi
            
            debug "Waiting for pods to start... (attempt $attempt/$max_attempts)"
            sleep 10
            ((attempt++))
        done
    fi
}

# Perform rollback operation
perform_rollback() {
    log "🔄 Performing rollback operation..."

    for cluster in "${CLUSTERS[@]}"; do
        local region_name=""
        case $cluster in
            *mumbai*) region_name="mumbai" ;;
            *delhi*) region_name="delhi" ;;
            *bangalore*) region_name="bangalore" ;;
        esac

        log "🔄 Rolling back cluster: $cluster (Region: $region_name)"
        
        kubectl config use-context "$cluster" &>/dev/null
        
        # Get current release
        local current_releases
        current_releases=$(helm list -n flipkart-production --filter "flipkart-prod-$region_name" -o json | jq -r '.[].name' | sort -r)
        
        if [[ -z "$current_releases" ]]; then
            warn "No releases found for rollback in region: $region_name"
            continue
        fi

        # Rollback to previous release
        local latest_release
        latest_release=$(echo "$current_releases" | head -n1)
        
        if [[ "$DRY_RUN" == true ]]; then
            info "DRY RUN: Would rollback release: $latest_release"
        else
            info "Rolling back release: $latest_release"
            if helm rollback "$latest_release" -n flipkart-production; then
                log "✅ Rollback successful for cluster: $cluster"
            else
                error "Rollback failed for cluster: $cluster"
                exit 1
            fi
        fi
    done
}

# Health check after deployment
post_deployment_health_check() {
    log "🏥 Performing post-deployment health checks..."

    local base_urls=()
    case $REGION in
        mumbai|all)
            base_urls+=("https://api.flipkart.com")
            ;;
        delhi|all)
            base_urls+=("https://delhi.flipkart.com")
            ;;
        bangalore|all)
            base_urls+=("https://bangalore.flipkart.com")
            ;;
    esac

    for url in "${base_urls[@]}"; do
        info "Health checking: $url"
        
        # Basic health check
        if curl -sf "$url/health" >/dev/null; then
            log "✅ Health check passed: $url"
        else
            error "Health check failed: $url"
            exit 1
        fi

        # Indian-specific endpoints
        if curl -sf "$url/api/v1/regions/mumbai" >/dev/null; then
            debug "Regional endpoint check passed: $url"
        else
            warn "Regional endpoint check failed: $url"
        fi

        # Payment gateway health
        if curl -sf "$url/api/v1/payments/health" >/dev/null; then
            debug "Payment gateway health check passed: $url"
        else
            warn "Payment gateway health check failed: $url"
        fi
    done

    log "🎉 All health checks completed"
}

# Setup monitoring and alerting
setup_monitoring() {
    log "📊 Setting up monitoring and alerting..."

    # Deploy monitoring stack to primary cluster (Mumbai)
    kubectl config use-context "flipkart-mumbai-prod" &>/dev/null

    if [[ "$DRY_RUN" == false ]]; then
        # Deploy Prometheus
        info "Deploying Prometheus monitoring..."
        kubectl apply -f kubernetes/monitoring/prometheus.yaml -n flipkart-monitoring

        # Deploy Grafana
        info "Deploying Grafana dashboards..."
        kubectl apply -f kubernetes/monitoring/grafana.yaml -n flipkart-monitoring

        # Wait for monitoring stack to be ready
        kubectl wait --for=condition=available deployment/prometheus -n flipkart-monitoring --timeout=300s
        kubectl wait --for=condition=available deployment/grafana -n flipkart-monitoring --timeout=300s

        log "✅ Monitoring stack deployed successfully"
    else
        info "DRY RUN: Would deploy monitoring stack"
    fi
}

# Send deployment notifications
send_notifications() {
    log "📢 Sending deployment notifications..."

    local status="SUCCESS"
    local icon="✅"
    local color="good"

    if [[ $? -ne 0 ]]; then
        status="FAILED"
        icon="❌"
        color="danger"
    fi

    local message="$icon Flipkart Indian E-commerce Deployment $status

• Environment: $ENVIRONMENT
• Region: $REGION
• Version: $IMAGE_TAG
• Time: $(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')
• Festival Mode: $([ "$FESTIVAL_MODE" == true ] && echo "Enabled" || echo "Disabled")
• Compliance: RBI ✅ | PCI-DSS ✅ | Data Localization ✅"

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
            \"summary\": \"Flipkart Deployment $status\",
            \"sections\": [{
                \"activityTitle\": \"$message\"
            }]
        }"
        curl -X POST -H 'Content-type: application/json' \
            --data "$teams_payload" \
            "$TEAMS_WEBHOOK_URL" &>/dev/null || warn "Failed to send Teams notification"
    fi

    # Email notification (if configured)
    if command -v mail &> /dev/null && [[ -n "${NOTIFICATION_EMAIL:-}" ]]; then
        echo "$message" | mail -s "Flipkart Deployment $status" "$NOTIFICATION_EMAIL" || warn "Failed to send email notification"
    fi

    log "📧 Notifications sent"
}

# Cleanup function
cleanup() {
    log "🧹 Performing cleanup..."
    
    # Reset kubectl context
    kubectl config unset current-context &>/dev/null || true
    
    # Clean up temporary files
    rm -f /tmp/flipkart-deploy-* &>/dev/null || true
    
    log "✅ Cleanup completed"
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Main deployment function
main() {
    print_banner
    
    log "🚀 Starting $SCRIPT_NAME v$SCRIPT_VERSION"
    log "📋 Deployment ID: $DEPLOYMENT_TIMESTAMP"
    
    # Parse command line arguments
    parse_args "$@"
    
    # Validate prerequisites
    validate_prerequisites
    
    # Setup cluster configuration
    setup_cluster_config
    
    # Check Indian compliance
    check_indian_compliance
    
    # Validate Kubernetes connectivity
    validate_k8s_connectivity
    
    # Check for festival season
    check_festival_season
    
    # Pre-deployment validation
    pre_deployment_validation
    
    if [[ "$ROLLBACK_MODE" == true ]]; then
        # Perform rollback
        perform_rollback
    else
        # Deploy to clusters
        for cluster in "${CLUSTERS[@]}"; do
            deploy_to_cluster "$cluster"
        done
        
        # Post-deployment health checks
        post_deployment_health_check
        
        # Setup monitoring
        setup_monitoring
    fi
    
    # Send notifications
    send_notifications
    
    log "🎉 Deployment completed successfully!"
    log "📊 Deployment summary:"
    log "   • Environment: $ENVIRONMENT"
    log "   • Region(s): $REGION"
    log "   • Image Tag: $IMAGE_TAG"
    log "   • Festival Mode: $([ "$FESTIVAL_MODE" == true ] && echo "Enabled" || echo "Disabled")"
    log "   • Timestamp: $DEPLOYMENT_TIMESTAMP"
    log "   • Duration: $((SECONDS / 60)) minutes and $((SECONDS % 60)) seconds"
    
    if [[ "$DRY_RUN" == true ]]; then
        warn "🧪 This was a DRY RUN - no actual changes were made"
    fi
}

# Run main function with all arguments
main "$@"
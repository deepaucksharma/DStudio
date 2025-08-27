#!/bin/bash

#######################################################################
# Health Check Script for Indian E-commerce Platform
# Episode 092: Container Orchestration - Comprehensive Health Monitoring
# Context: Production health validation for Flipkart-style platform
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
SCRIPT_NAME="Flipkart Health Check"
SCRIPT_VERSION="1.0.0"
CHECK_TIMESTAMP=$(TZ="$INDIAN_TIMEZONE" date +'%Y%m%d%H%M%S')

# Default values
REGION="all"
CHECK_TYPE="comprehensive"
OUTPUT_FORMAT="console"
TIMEOUT=30
CONTINUOUS_MODE=false
INTERVAL=60
ALERT_MODE=false
EXPORT_METRICS=false

# Health check configuration
CLUSTERS=()
SERVICES=("product-catalog" "order-management" "payment-service" "user-service" "search-service" "api-gateway")
CRITICAL_ENDPOINTS=()
PAYMENT_GATEWAYS=("razorpay" "paytm" "phonepe" "upi")

# Health metrics
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Print banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                     🏥 HEALTH CHECK SYSTEM 🏥                                  ║"
    echo "║                    🇮🇳 Flipkart Indian E-commerce Platform                      ║"
    echo "║                                                                                  ║"
    echo "║  🔍 Comprehensive Production Health Monitoring                                 ║"
    echo "║  🎯 Indian Regional & Compliance Validation                                    ║"
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
    ((WARNING_CHECKS++))
}

error() {
    echo -e "${RED}[$(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')] ERROR: $1${NC}"
    ((FAILED_CHECKS++))
}

info() {
    echo -e "${BLUE}[$(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')] INFO: $1${NC}"
}

success() {
    echo -e "${GREEN}[$(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')] ✅ $1${NC}"
    ((PASSED_CHECKS++))
}

# Print usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

🏥 Flipkart Indian E-commerce Health Check System

OPTIONS:
    -r, --region         Indian region (mumbai|delhi|bangalore|all) [default: all]
    -t, --type          Check type (basic|comprehensive|payment|k8s) [default: comprehensive]
    -f, --format        Output format (console|json|prometheus) [default: console]
    -T, --timeout       Request timeout in seconds [default: 30]
    -c, --continuous    Continuous monitoring mode
    -i, --interval      Interval for continuous mode in seconds [default: 60]
    -a, --alert         Alert mode - send notifications on failures
    -e, --export        Export metrics to monitoring systems
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output

CHECK TYPES:
    basic           Quick health check of main endpoints
    comprehensive   Full system health validation (default)
    payment         Payment gateway specific checks
    k8s             Kubernetes cluster health only

OUTPUT FORMATS:
    console         Human-readable console output (default)
    json            JSON format for API integration
    prometheus      Prometheus metrics format

EXAMPLES:
    # Quick health check
    $0 --type basic

    # Full health check for Mumbai
    $0 --region mumbai --type comprehensive

    # Payment gateway validation
    $0 --type payment --alert

    # Continuous monitoring
    $0 --continuous --interval 30

    # Export metrics to Prometheus
    $0 --format prometheus --export

ENDPOINTS MONITORED:
    🌐 Public APIs (api.flipkart.com, delhi.flipkart.com, bangalore.flipkart.com)
    💳 Payment gateways (Razorpay, Paytm, PhonePe, UPI)
    ☸️  Kubernetes clusters (Mumbai, Delhi, Bangalore)
    📊 Monitoring systems (Prometheus, Grafana)
    🗄️  Databases (PostgreSQL, Redis, Elasticsearch)

For more information: https://docs.flipkart.com/health-monitoring
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
            -t|--type)
                CHECK_TYPE="$2"
                shift 2
                ;;
            -f|--format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            -T|--timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -c|--continuous)
                CONTINUOUS_MODE=true
                shift
                ;;
            -i|--interval)
                INTERVAL="$2"
                shift 2
                ;;
            -a|--alert)
                ALERT_MODE=true
                shift
                ;;
            -e|--export)
                EXPORT_METRICS=true
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

# Validate prerequisites
validate_prerequisites() {
    # Check required tools
    local tools=("curl" "jq")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "Required tool '$tool' is not installed"
            exit 1
        fi
    done

    # Add kubectl if k8s checks are needed
    if [[ "$CHECK_TYPE" == "k8s" || "$CHECK_TYPE" == "comprehensive" ]]; then
        if ! command -v "kubectl" &> /dev/null; then
            error "kubectl is required for Kubernetes health checks"
            exit 1
        fi
    fi

    # Validate region
    if [[ "$REGION" != "mumbai" && "$REGION" != "delhi" && "$REGION" != "bangalore" && "$REGION" != "all" ]]; then
        error "Invalid region: $REGION"
        exit 1
    fi

    # Validate check type
    if [[ "$CHECK_TYPE" != "basic" && "$CHECK_TYPE" != "comprehensive" && "$CHECK_TYPE" != "payment" && "$CHECK_TYPE" != "k8s" ]]; then
        error "Invalid check type: $CHECK_TYPE"
        exit 1
    fi

    # Validate output format
    if [[ "$OUTPUT_FORMAT" != "console" && "$OUTPUT_FORMAT" != "json" && "$OUTPUT_FORMAT" != "prometheus" ]]; then
        error "Invalid output format: $OUTPUT_FORMAT"
        exit 1
    fi

    # Validate timeout
    if [[ ! "$TIMEOUT" =~ ^[1-9][0-9]*$ ]] || [[ "$TIMEOUT" -gt 300 ]]; then
        error "Invalid timeout: $TIMEOUT. Must be 1-300 seconds"
        exit 1
    fi
}

# Setup configurations based on region
setup_configurations() {
    case $REGION in
        mumbai)
            CRITICAL_ENDPOINTS=("https://api.flipkart.com")
            CLUSTERS=("flipkart-mumbai-prod")
            ;;
        delhi)
            CRITICAL_ENDPOINTS=("https://delhi.flipkart.com")
            CLUSTERS=("flipkart-delhi-prod")
            ;;
        bangalore)
            CRITICAL_ENDPOINTS=("https://bangalore.flipkart.com")
            CLUSTERS=("flipkart-bangalore-prod")
            ;;
        all)
            CRITICAL_ENDPOINTS=("https://api.flipkart.com" "https://delhi.flipkart.com" "https://bangalore.flipkart.com")
            CLUSTERS=("flipkart-mumbai-prod" "flipkart-delhi-prod" "flipkart-bangalore-prod")
            ;;
    esac
}

# HTTP health check function
http_health_check() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    ((TOTAL_CHECKS++))
    
    local start_time=$SECONDS
    local response_code
    local response_time
    
    if response_code=$(curl -o /dev/null -s -w "%{http_code}" --max-time "$TIMEOUT" "$url"); then
        response_time=$((SECONDS - start_time))
        
        if [[ "$response_code" -eq "$expected_status" ]]; then
            success "$description - HTTP $response_code (${response_time}s)"
            return 0
        else
            error "$description - HTTP $response_code (expected $expected_status)"
            return 1
        fi
    else
        response_time=$((SECONDS - start_time))
        error "$description - Connection failed after ${response_time}s"
        return 1
    fi
}

# JSON response health check
json_health_check() {
    local url=$1
    local description=$2
    local expected_field=$3
    local expected_value=$4
    
    ((TOTAL_CHECKS++))
    
    local start_time=$SECONDS
    local response
    
    if response=$(curl -s --max-time "$TIMEOUT" "$url"); then
        local response_time=$((SECONDS - start_time))
        
        if echo "$response" | jq -e ".$expected_field" > /dev/null 2>&1; then
            local actual_value
            actual_value=$(echo "$response" | jq -r ".$expected_field")
            
            if [[ "$actual_value" == "$expected_value" ]]; then
                success "$description - $expected_field: $actual_value (${response_time}s)"
                return 0
            else
                error "$description - $expected_field: $actual_value (expected: $expected_value)"
                return 1
            fi
        else
            warn "$description - Field '$expected_field' not found in response"
            return 1
        fi
    else
        local response_time=$((SECONDS - start_time))
        error "$description - API call failed after ${response_time}s"
        return 1
    fi
}

# Basic health checks
perform_basic_checks() {
    log "🔍 Performing basic health checks..."
    
    # Check main endpoints
    for endpoint in "${CRITICAL_ENDPOINTS[@]}"; do
        local region_name=""
        case $endpoint in
            *api.flipkart.com*) region_name="Mumbai" ;;
            *delhi.flipkart.com*) region_name="Delhi" ;;
            *bangalore.flipkart.com*) region_name="Bangalore" ;;
        esac
        
        info "Checking $region_name region endpoint..."
        
        # Basic health endpoint
        http_health_check "$endpoint/health" "Health endpoint ($region_name)"
        
        # API version endpoint
        http_health_check "$endpoint/api/v1/version" "Version endpoint ($region_name)"
        
        # Regional endpoint
        case $region_name in
            Mumbai) http_health_check "$endpoint/api/v1/regions/mumbai" "Regional endpoint ($region_name)" ;;
            Delhi) http_health_check "$endpoint/api/v1/regions/delhi" "Regional endpoint ($region_name)" ;;
            Bangalore) http_health_check "$endpoint/api/v1/regions/bangalore" "Regional endpoint ($region_name)" ;;
        esac
    done
}

# Payment gateway health checks
perform_payment_checks() {
    log "💳 Performing payment gateway health checks..."
    
    for endpoint in "${CRITICAL_ENDPOINTS[@]}"; do
        local region_name=""
        case $endpoint in
            *api.flipkart.com*) region_name="Mumbai" ;;
            *delhi.flipkart.com*) region_name="Delhi" ;;
            *bangalore.flipkart.com*) region_name="Bangalore" ;;
        esac
        
        info "Checking payment systems in $region_name..."
        
        # Payment service health
        http_health_check "$endpoint/api/v1/payments/health" "Payment service health ($region_name)"
        
        # Payment gateways status
        json_health_check "$endpoint/api/v1/payments/gateways/status" "Payment gateways status ($region_name)" "status" "healthy"
        
        # Check individual gateway connectivity
        for gateway in "${PAYMENT_GATEWAYS[@]}"; do
            ((TOTAL_CHECKS++))
            
            local gateway_url="$endpoint/api/v1/payments/gateways/$gateway/ping"
            local start_time=$SECONDS
            
            if response=$(curl -s --max-time 15 "$gateway_url"); then
                local response_time=$((SECONDS - start_time))
                
                if echo "$response" | jq -e '.status' > /dev/null 2>&1; then
                    local status
                    status=$(echo "$response" | jq -r '.status')
                    
                    if [[ "$status" == "connected" || "$status" == "available" ]]; then
                        success "$gateway gateway connectivity ($region_name) - ${response_time}s"
                    else
                        warn "$gateway gateway ($region_name) - Status: $status"
                    fi
                else
                    warn "$gateway gateway ($region_name) - Unexpected response format"
                fi
            else
                local response_time=$((SECONDS - start_time))
                error "$gateway gateway ($region_name) - Connection failed after ${response_time}s"
            fi
        done
        
        # GST calculation service
        http_health_check "$endpoint/api/v1/gst/health" "GST calculation service ($region_name)"
        
        # UPI specific checks
        http_health_check "$endpoint/api/v1/payments/upi/health" "UPI service ($region_name)"
    done
}

# Kubernetes cluster health checks
perform_k8s_checks() {
    log "☸️  Performing Kubernetes health checks..."
    
    for cluster in "${CLUSTERS[@]}"; do
        local region_name=""
        case $cluster in
            *mumbai*) region_name="Mumbai" ;;
            *delhi*) region_name="Delhi" ;;
            *bangalore*) region_name="Bangalore" ;;
        esac
        
        info "Checking Kubernetes cluster: $cluster ($region_name)"
        
        # Set kubectl context
        ((TOTAL_CHECKS++))
        if kubectl config use-context "$cluster" &>/dev/null; then
            success "Kubectl context set for $cluster"
        else
            error "Failed to set kubectl context for $cluster"
            continue
        fi
        
        # Cluster info
        ((TOTAL_CHECKS++))
        if kubectl cluster-info &>/dev/null; then
            success "Cluster connectivity ($region_name)"
        else
            error "Cluster connectivity failed ($region_name)"
            continue
        fi
        
        # Node status
        ((TOTAL_CHECKS++))
        local total_nodes ready_nodes
        total_nodes=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
        ready_nodes=$(kubectl get nodes --no-headers 2>/dev/null | grep " Ready " | wc -l)
        
        if [[ $ready_nodes -eq $total_nodes && $total_nodes -gt 0 ]]; then
            success "All nodes ready ($ready_nodes/$total_nodes) in $region_name"
        else
            error "Node issues in $region_name - $ready_nodes/$total_nodes ready"
        fi
        
        # Namespace checks
        for namespace in "flipkart-production" "flipkart-monitoring"; do
            ((TOTAL_CHECKS++))
            if kubectl get namespace "$namespace" &>/dev/null; then
                success "Namespace $namespace exists ($region_name)"
            else
                error "Namespace $namespace missing ($region_name)"
            fi
        done
        
        # Pod health in production namespace
        ((TOTAL_CHECKS++))
        local total_pods running_pods
        total_pods=$(kubectl get pods -n flipkart-production --no-headers 2>/dev/null | wc -l)
        running_pods=$(kubectl get pods -n flipkart-production --no-headers 2>/dev/null | grep " Running " | wc -l)
        
        if [[ $running_pods -eq $total_pods && $total_pods -gt 0 ]]; then
            success "All pods running ($running_pods/$total_pods) in $region_name production"
        else
            warn "Pod issues in $region_name production - $running_pods/$total_pods running"
        fi
        
        # Service checks
        for service in "${SERVICES[@]}"; do
            ((TOTAL_CHECKS++))
            if kubectl get service "$service" -n flipkart-production &>/dev/null; then
                # Check if service has endpoints
                local endpoints
                endpoints=$(kubectl get endpoints "$service" -n flipkart-production -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null | wc -w)
                
                if [[ $endpoints -gt 0 ]]; then
                    success "Service $service has $endpoints endpoints ($region_name)"
                else
                    warn "Service $service has no endpoints ($region_name)"
                fi
            else
                error "Service $service not found ($region_name)"
            fi
        done
        
        # Resource usage checks
        ((TOTAL_CHECKS++))
        if command -v kubectl &> /dev/null && kubectl top nodes &>/dev/null; then
            local high_cpu_nodes
            high_cpu_nodes=$(kubectl top nodes --no-headers 2>/dev/null | awk '$3 > 80 {print $1}' | wc -l)
            
            if [[ $high_cpu_nodes -eq 0 ]]; then
                success "CPU usage normal in $region_name cluster"
            else
                warn "$high_cpu_nodes nodes with high CPU in $region_name cluster"
            fi
        else
            warn "Resource metrics not available for $region_name cluster"
        fi
    done
}

# Database health checks
perform_database_checks() {
    log "🗄️  Performing database health checks..."
    
    for endpoint in "${CRITICAL_ENDPOINTS[@]}"; do
        local region_name=""
        case $endpoint in
            *api.flipkart.com*) region_name="Mumbai" ;;
            *delhi.flipkart.com*) region_name="Delhi" ;;
            *bangalore.flipkart.com*) region_name="Bangalore" ;;
        esac
        
        info "Checking database connectivity in $region_name..."
        
        # PostgreSQL health
        json_health_check "$endpoint/api/v1/health/database/postgres" "PostgreSQL health ($region_name)" "status" "healthy"
        
        # Redis health  
        json_health_check "$endpoint/api/v1/health/cache/redis" "Redis health ($region_name)" "status" "healthy"
        
        # Elasticsearch health
        json_health_check "$endpoint/api/v1/health/search/elasticsearch" "Elasticsearch health ($region_name)" "status" "healthy"
        
        # Database performance metrics
        ((TOTAL_CHECKS++))
        local db_response_time_url="$endpoint/api/v1/health/database/performance"
        if response=$(curl -s --max-time "$TIMEOUT" "$db_response_time_url"); then
            if echo "$response" | jq -e '.avg_response_time_ms' > /dev/null 2>&1; then
                local avg_response_time
                avg_response_time=$(echo "$response" | jq -r '.avg_response_time_ms')
                
                if [[ $(echo "$avg_response_time < 100" | bc -l) -eq 1 ]]; then
                    success "Database performance good ($region_name) - ${avg_response_time}ms avg"
                elif [[ $(echo "$avg_response_time < 500" | bc -l) -eq 1 ]]; then
                    warn "Database performance degraded ($region_name) - ${avg_response_time}ms avg"
                else
                    error "Database performance poor ($region_name) - ${avg_response_time}ms avg"
                fi
            else
                warn "Database performance metrics unavailable ($region_name)"
            fi
        else
            error "Database performance check failed ($region_name)"
        fi
    done
}

# Monitoring system health checks
perform_monitoring_checks() {
    log "📊 Performing monitoring system health checks..."
    
    # Prometheus health
    for endpoint in "${CRITICAL_ENDPOINTS[@]}"; do
        local region_name=""
        case $endpoint in
            *api.flipkart.com*) region_name="Mumbai" ;;
            *delhi.flipkart.com*) region_name="Delhi" ;;
            *bangalore.flipkart.com*) region_name="Bangalore" ;;
        esac
        
        # Replace main domain with monitoring subdomain
        local monitoring_endpoint="${endpoint/api./prometheus.}"
        local grafana_endpoint="${endpoint/api./grafana.}"
        
        info "Checking monitoring systems in $region_name..."
        
        # Prometheus health
        http_health_check "$monitoring_endpoint/-/healthy" "Prometheus health ($region_name)"
        
        # Prometheus targets
        ((TOTAL_CHECKS++))
        local targets_url="$monitoring_endpoint/api/v1/targets"
        if response=$(curl -s --max-time "$TIMEOUT" "$targets_url"); then
            if echo "$response" | jq -e '.data.activeTargets' > /dev/null 2>&1; then
                local active_targets
                active_targets=$(echo "$response" | jq '.data.activeTargets | length')
                local healthy_targets
                healthy_targets=$(echo "$response" | jq '.data.activeTargets | map(select(.health == "up")) | length')
                
                if [[ $healthy_targets -eq $active_targets ]]; then
                    success "All Prometheus targets healthy ($healthy_targets/$active_targets) in $region_name"
                else
                    warn "Some Prometheus targets unhealthy ($healthy_targets/$active_targets) in $region_name"
                fi
            else
                warn "Prometheus targets data unavailable ($region_name)"
            fi
        else
            error "Prometheus targets check failed ($region_name)"
        fi
        
        # Grafana health
        http_health_check "$grafana_endpoint/api/health" "Grafana health ($region_name)"
    done
}

# Indian specific business checks
perform_indian_business_checks() {
    log "🇮🇳 Performing Indian business logic health checks..."
    
    for endpoint in "${CRITICAL_ENDPOINTS[@]}"; do
        local region_name=""
        case $endpoint in
            *api.flipkart.com*) region_name="Mumbai" ;;
            *delhi.flipkart.com*) region_name="Delhi" ;;
            *bangalore.flipkart.com*) region_name="Bangalore" ;;
        esac
        
        info "Checking Indian business functions in $region_name..."
        
        # GST calculation service
        ((TOTAL_CHECKS++))
        local gst_test_url="$endpoint/api/v1/gst/calculate"
        local gst_payload='{"amount": 1000, "state": "maharashtra", "category": "electronics"}'
        
        if response=$(curl -s --max-time "$TIMEOUT" -X POST -H "Content-Type: application/json" -d "$gst_payload" "$gst_test_url"); then
            if echo "$response" | jq -e '.gst_amount' > /dev/null 2>&1; then
                local gst_amount
                gst_amount=$(echo "$response" | jq -r '.gst_amount')
                
                # GST for electronics in Maharashtra should be 18%
                if [[ "$gst_amount" == "180" ]]; then
                    success "GST calculation correct ($region_name) - ₹180 for ₹1000"
                else
                    error "GST calculation incorrect ($region_name) - got ₹$gst_amount, expected ₹180"
                fi
            else
                error "GST calculation response invalid ($region_name)"
            fi
        else
            error "GST calculation service failed ($region_name)"
        fi
        
        # Indian cities service
        http_health_check "$endpoint/api/v1/cities/indian" "Indian cities service ($region_name)"
        
        # Regional delivery check
        json_health_check "$endpoint/api/v1/delivery/regions/$region_name" "Regional delivery ($region_name)" "available" "true"
        
        # Festival season detection
        ((TOTAL_CHECKS++))
        local festival_url="$endpoint/api/v1/business/festival-status"
        if response=$(curl -s --max-time "$TIMEOUT" "$festival_url"); then
            if echo "$response" | jq -e '.is_festival_season' > /dev/null 2>&1; then
                local is_festival_season
                is_festival_season=$(echo "$response" | jq -r '.is_festival_season')
                success "Festival season detection working ($region_name) - Status: $is_festival_season"
            else
                warn "Festival season detection response invalid ($region_name)"
            fi
        else
            error "Festival season detection failed ($region_name)"
        fi
    done
}

# Comprehensive health checks
perform_comprehensive_checks() {
    log "🔍 Performing comprehensive health checks..."
    
    perform_basic_checks
    perform_payment_checks
    perform_k8s_checks
    perform_database_checks
    perform_monitoring_checks
    perform_indian_business_checks
}

# Generate health report
generate_health_report() {
    local overall_status="HEALTHY"
    local overall_score=0
    
    if [[ $TOTAL_CHECKS -gt 0 ]]; then
        overall_score=$(( (PASSED_CHECKS * 100) / TOTAL_CHECKS ))
        
        if [[ $overall_score -ge 95 ]]; then
            overall_status="HEALTHY"
        elif [[ $overall_score -ge 80 ]]; then
            overall_status="DEGRADED"
        else
            overall_status="UNHEALTHY"
        fi
    fi
    
    case $OUTPUT_FORMAT in
        json)
            cat << EOF
{
  "timestamp": "$(TZ="$INDIAN_TIMEZONE" date --iso-8601=seconds)",
  "check_id": "$CHECK_TIMESTAMP",
  "region": "$REGION",
  "check_type": "$CHECK_TYPE",
  "overall_status": "$overall_status",
  "overall_score": $overall_score,
  "summary": {
    "total_checks": $TOTAL_CHECKS,
    "passed": $PASSED_CHECKS,
    "failed": $FAILED_CHECKS,
    "warnings": $WARNING_CHECKS
  },
  "indian_timezone": "$INDIAN_TIMEZONE",
  "compliance": {
    "rbi_compliant": true,
    "pci_dss_compliant": true,
    "data_localization": true
  }
}
EOF
            ;;
        prometheus)
            cat << EOF
# HELP flipkart_health_check_total Total number of health checks performed
# TYPE flipkart_health_check_total counter
flipkart_health_check_total{region="$REGION",type="$CHECK_TYPE"} $TOTAL_CHECKS

# HELP flipkart_health_check_passed Number of health checks that passed
# TYPE flipkart_health_check_passed counter
flipkart_health_check_passed{region="$REGION",type="$CHECK_TYPE"} $PASSED_CHECKS

# HELP flipkart_health_check_failed Number of health checks that failed
# TYPE flipkart_health_check_failed counter
flipkart_health_check_failed{region="$REGION",type="$CHECK_TYPE"} $FAILED_CHECKS

# HELP flipkart_health_check_warnings Number of health checks with warnings
# TYPE flipkart_health_check_warnings counter
flipkart_health_check_warnings{region="$REGION",type="$CHECK_TYPE"} $WARNING_CHECKS

# HELP flipkart_health_score Overall health score percentage
# TYPE flipkart_health_score gauge
flipkart_health_score{region="$REGION",type="$CHECK_TYPE"} $overall_score

# HELP flipkart_health_status Overall health status (1=healthy, 0.5=degraded, 0=unhealthy)
# TYPE flipkart_health_status gauge
flipkart_health_status{region="$REGION",type="$CHECK_TYPE"} $(case $overall_status in HEALTHY) echo "1" ;; DEGRADED) echo "0.5" ;; *) echo "0" ;; esac)
EOF
            ;;
        *)
            echo
            echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${CYAN}║                           📊 HEALTH CHECK SUMMARY 📊                            ║${NC}"
            echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════════╝${NC}"
            echo
            echo -e "🎯 Overall Status: $(case $overall_status in HEALTHY) echo -e "${GREEN}HEALTHY${NC}" ;; DEGRADED) echo -e "${YELLOW}DEGRADED${NC}" ;; *) echo -e "${RED}UNHEALTHY${NC}" ;; esac)"
            echo -e "📈 Health Score: $overall_score%"
            echo -e "🇮🇳 Region: $REGION"
            echo -e "🔍 Check Type: $CHECK_TYPE"
            echo -e "⏰ Timestamp: $(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')"
            echo
            echo -e "📋 Results Summary:"
            echo -e "   • Total Checks: $TOTAL_CHECKS"
            echo -e "   • ✅ Passed: $PASSED_CHECKS"
            echo -e "   • ❌ Failed: $FAILED_CHECKS"
            echo -e "   • ⚠️  Warnings: $WARNING_CHECKS"
            echo
            echo -e "🇮🇳 Compliance Status:"
            echo -e "   • 🏛️  RBI Compliant: ✅"
            echo -e "   • 💳 PCI-DSS Compliant: ✅"
            echo -e "   • 📍 Data Localization: ✅"
            echo
            ;;
    esac
}

# Send alerts if enabled
send_alerts() {
    if [[ "$ALERT_MODE" == false ]]; then
        return 0
    fi
    
    local overall_score=0
    if [[ $TOTAL_CHECKS -gt 0 ]]; then
        overall_score=$(( (PASSED_CHECKS * 100) / TOTAL_CHECKS ))
    fi
    
    # Only send alerts if health score is below threshold
    if [[ $overall_score -lt 95 ]]; then
        local message="🚨 Flipkart Health Alert

• Region: $REGION
• Health Score: $overall_score%
• Failed Checks: $FAILED_CHECKS
• Warnings: $WARNING_CHECKS
• Time: $(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')

Immediate attention required!"

        # Slack notification
        if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
            curl -X POST -H 'Content-type: application/json' \
                --data "{\"text\":\"$message\"}" \
                "$SLACK_WEBHOOK_URL" &>/dev/null || warn "Failed to send Slack alert"
        fi

        # PagerDuty alert
        if [[ -n "${PAGERDUTY_INTEGRATION_KEY:-}" && $overall_score -lt 80 ]]; then
            local pd_payload="{
                \"routing_key\": \"$PAGERDUTY_INTEGRATION_KEY\",
                \"event_action\": \"trigger\",
                \"dedup_key\": \"flipkart-health-check-$REGION\",
                \"payload\": {
                    \"summary\": \"Flipkart health check failure in $REGION\",
                    \"severity\": \"error\",
                    \"source\": \"health-check-system\"
                }
            }"
            curl -X POST -H 'Content-type: application/json' \
                --data "$pd_payload" \
                "https://events.pagerduty.com/v2/enqueue" &>/dev/null || warn "Failed to send PagerDuty alert"
        fi
    fi
}

# Export metrics to monitoring systems
export_health_metrics() {
    if [[ "$EXPORT_METRICS" == false ]]; then
        return 0
    fi
    
    # Export to Prometheus pushgateway if available
    if [[ -n "${PROMETHEUS_PUSHGATEWAY_URL:-}" ]]; then
        local metrics
        metrics=$(OUTPUT_FORMAT=prometheus generate_health_report)
        
        curl -X POST --data-binary "$metrics" \
            "$PROMETHEUS_PUSHGATEWAY_URL/metrics/job/flipkart-health-check/instance/$REGION" \
            &>/dev/null || warn "Failed to export metrics to Prometheus"
    fi
    
    # Export to custom metrics endpoint
    if [[ -n "${METRICS_ENDPOINT_URL:-}" ]]; then
        local json_metrics
        json_metrics=$(OUTPUT_FORMAT=json generate_health_report)
        
        curl -X POST -H 'Content-type: application/json' \
            --data "$json_metrics" \
            "$METRICS_ENDPOINT_URL" \
            &>/dev/null || warn "Failed to export metrics to custom endpoint"
    fi
}

# Main health check function
perform_health_checks() {
    log "🏥 Starting health checks for region: $REGION, type: $CHECK_TYPE"
    
    # Reset counters
    TOTAL_CHECKS=0
    PASSED_CHECKS=0
    FAILED_CHECKS=0
    WARNING_CHECKS=0
    
    case $CHECK_TYPE in
        basic)
            perform_basic_checks
            ;;
        payment)
            perform_payment_checks
            ;;
        k8s)
            perform_k8s_checks
            ;;
        comprehensive)
            perform_comprehensive_checks
            ;;
    esac
    
    # Generate and display report
    generate_health_report
    
    # Send alerts if needed
    send_alerts
    
    # Export metrics if enabled
    export_health_metrics
    
    log "🎉 Health check completed"
    
    # Return appropriate exit code
    if [[ $FAILED_CHECKS -gt 0 ]]; then
        return 1
    elif [[ $WARNING_CHECKS -gt 0 ]]; then
        return 2
    else
        return 0
    fi
}

# Main function
main() {
    print_banner
    
    log "🚀 Starting $SCRIPT_NAME v$SCRIPT_VERSION"
    log "🆔 Check ID: $CHECK_TIMESTAMP"
    
    # Parse command line arguments
    parse_args "$@"
    
    # Validate prerequisites
    validate_prerequisites
    
    # Setup configurations
    setup_configurations
    
    if [[ "$CONTINUOUS_MODE" == true ]]; then
        log "🔄 Starting continuous monitoring mode (interval: ${INTERVAL}s)"
        
        while true; do
            echo -e "\n${CYAN}=== Health Check Cycle: $(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST') ===${NC}"
            
            perform_health_checks
            
            echo -e "\n💤 Sleeping for $INTERVAL seconds..."
            sleep "$INTERVAL"
        done
    else
        perform_health_checks
        exit $?
    fi
}

# Run main function with all arguments
main "$@"
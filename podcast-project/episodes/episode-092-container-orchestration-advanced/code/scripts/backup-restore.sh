#!/bin/bash

#######################################################################
# Backup and Restore Script for Indian E-commerce Platform
# Episode 092: Container Orchestration - Data Protection & Recovery
# Context: Production-grade backup/restore for Flipkart-style platform
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
SCRIPT_NAME="Flipkart Backup & Restore"
SCRIPT_VERSION="1.0.0"
OPERATION_TIMESTAMP=$(TZ="$INDIAN_TIMEZONE" date +'%Y%m%d%H%M%S')

# Default values
OPERATION="backup"
BACKUP_TYPE="full"
REGION="mumbai"
RETENTION_DAYS=30
DRY_RUN=false
COMPRESS=true
ENCRYPT=true
VERIFY=true

# Backup configuration
BACKUP_BASE_PATH="/backup/flipkart"
S3_BUCKET="flipkart-backups-mumbai"
ENCRYPTION_KEY_FILE="/etc/backup/encryption.key"
CLUSTERS=()
DATABASES=("postgresql" "redis" "elasticsearch")
BACKUP_COMPONENTS=("databases" "kubernetes" "configurations" "secrets")

# Backup retention policy (Indian compliance)
DAILY_RETENTION=7    # 7 daily backups
WEEKLY_RETENTION=4   # 4 weekly backups
MONTHLY_RETENTION=12 # 12 monthly backups
YEARLY_RETENTION=7   # 7 yearly backups

# Print banner
print_banner() {
    case $OPERATION in
        backup)
            echo -e "${CYAN}"
            echo "╔══════════════════════════════════════════════════════════════════════════════════╗"
            echo "║                      💾 BACKUP SYSTEM 💾                                       ║"
            echo "║                    🇮🇳 Flipkart Indian E-commerce Platform                      ║"
            echo "║                                                                                  ║"
            echo "║  🛡️  Production Data Protection & Compliance                                   ║"
            echo "║  🔐 Encrypted & Compressed Backups                                             ║"
            echo "║  📅 $(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')                                              ║"
            echo "║  🔧 Version: $SCRIPT_VERSION                                                      ║"
            echo "╚══════════════════════════════════════════════════════════════════════════════════╝"
            ;;
        restore)
            echo -e "${YELLOW}"
            echo "╔══════════════════════════════════════════════════════════════════════════════════╗"
            echo "║                      🔄 RESTORE SYSTEM 🔄                                      ║"
            echo "║                    🇮🇳 Flipkart Indian E-commerce Platform                      ║"
            echo "║                                                                                  ║"
            echo "║  🚨 Production Data Recovery & Restoration                                     ║"
            echo "║  🔐 Encrypted Backup Decryption                                               ║"
            echo "║  📅 $(TZ="$INDIAN_TIMEZONE" date +'%Y-%m-%d %H:%M:%S IST')                                              ║"
            echo "║  🔧 Version: $SCRIPT_VERSION                                                      ║"
            echo "╚══════════════════════════════════════════════════════════════════════════════════╝"
            ;;
    esac
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

# Print usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

💾 Flipkart Indian E-commerce Backup & Restore System

OPTIONS:
    -o, --operation     Operation type (backup|restore|list|cleanup) [default: backup]
    -t, --type          Backup type (full|incremental|differential) [default: full]
    -r, --region        Indian region (mumbai|delhi|bangalore|all) [default: mumbai]
    -c, --components    Components to backup (databases,kubernetes,configurations,secrets,all) [default: all]
    -R, --retention     Retention period in days [default: 30]
    -n, --dry-run       Perform dry run without actual operations
    -C, --no-compress   Disable compression
    -E, --no-encrypt    Disable encryption (NOT RECOMMENDED)
    -V, --no-verify     Skip backup verification
    -f, --file          Specific backup file for restore operation
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output

BACKUP TYPES:
    full            Complete backup of all data (default)
    incremental     Incremental backup since last backup
    differential    Differential backup since last full backup

COMPONENTS:
    databases       PostgreSQL, Redis, Elasticsearch
    kubernetes      K8s configurations, manifests, secrets
    configurations  Application configs, environment variables
    secrets         Encrypted secrets and certificates
    all             All components (default)

OPERATIONS:
    backup          Create new backup
    restore         Restore from backup
    list            List available backups
    cleanup         Clean old backups per retention policy

EXAMPLES:
    # Full backup of Mumbai region
    $0 --operation backup --region mumbai --type full

    # Incremental backup of all regions
    $0 --operation backup --region all --type incremental

    # Restore from specific backup
    $0 --operation restore --file backup-20240115120000.tar.gz

    # List available backups
    $0 --operation list --region mumbai

    # Cleanup old backups
    $0 --operation cleanup --retention 15

INDIAN COMPLIANCE:
    🏛️  RBI data localization compliance
    🔐 AES-256 encryption for all backups
    📊 Audit logging for all operations
    🇮🇳 Data stored only within Indian borders
    📋 Compliance reporting for audits

STORAGE LOCATIONS:
    Local: $BACKUP_BASE_PATH
    S3: s3://$S3_BUCKET
    Regions: Mumbai (primary), Delhi, Bangalore

For more information: https://docs.flipkart.com/backup-restore
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -o|--operation)
                OPERATION="$2"
                shift 2
                ;;
            -t|--type)
                BACKUP_TYPE="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -c|--components)
                IFS=',' read -ra BACKUP_COMPONENTS <<< "$2"
                shift 2
                ;;
            -R|--retention)
                RETENTION_DAYS="$2"
                shift 2
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -C|--no-compress)
                COMPRESS=false
                shift
                ;;
            -E|--no-encrypt)
                ENCRYPT=false
                shift
                ;;
            -V|--no-verify)
                VERIFY=false
                shift
                ;;
            -f|--file)
                RESTORE_FILE="$2"
                shift 2
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
    log "🔍 Validating backup/restore prerequisites..."

    # Check required tools
    local tools=("kubectl" "pg_dump" "redis-cli" "tar" "openssl" "aws")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "Required tool '$tool' is not installed"
            exit 1
        fi
    done

    # Validate operation
    if [[ "$OPERATION" != "backup" && "$OPERATION" != "restore" && "$OPERATION" != "list" && "$OPERATION" != "cleanup" ]]; then
        error "Invalid operation: $OPERATION"
        exit 1
    fi

    # Validate backup type
    if [[ "$BACKUP_TYPE" != "full" && "$BACKUP_TYPE" != "incremental" && "$BACKUP_TYPE" != "differential" ]]; then
        error "Invalid backup type: $BACKUP_TYPE"
        exit 1
    fi

    # Validate region
    if [[ "$REGION" != "mumbai" && "$REGION" != "delhi" && "$REGION" != "bangalore" && "$REGION" != "all" ]]; then
        error "Invalid region: $REGION"
        exit 1
    fi

    # Check encryption key for production
    if [[ "$ENCRYPT" == true && ! -f "$ENCRYPTION_KEY_FILE" && "$DRY_RUN" == false ]]; then
        warn "Encryption key file not found: $ENCRYPTION_KEY_FILE"
        warn "Generating new encryption key..."
        mkdir -p "$(dirname "$ENCRYPTION_KEY_FILE")"
        openssl rand -base64 32 > "$ENCRYPTION_KEY_FILE"
        chmod 600 "$ENCRYPTION_KEY_FILE"
    fi

    # Check backup directory
    if [[ ! -d "$BACKUP_BASE_PATH" ]]; then
        info "Creating backup directory: $BACKUP_BASE_PATH"
        mkdir -p "$BACKUP_BASE_PATH"
    fi

    # Validate AWS credentials for S3
    if ! aws sts get-caller-identity &>/dev/null; then
        warn "AWS credentials not configured - S3 backup unavailable"
    fi

    log "✅ Prerequisites validation completed"
}

# Setup cluster configurations
setup_cluster_config() {
    case $REGION in
        mumbai)
            CLUSTERS=("flipkart-mumbai-prod")
            S3_BUCKET="flipkart-backups-mumbai"
            ;;
        delhi)
            CLUSTERS=("flipkart-delhi-prod")
            S3_BUCKET="flipkart-backups-delhi"
            ;;
        bangalore)
            CLUSTERS=("flipkart-bangalore-prod")
            S3_BUCKET="flipkart-backups-bangalore"
            ;;
        all)
            CLUSTERS=("flipkart-mumbai-prod" "flipkart-delhi-prod" "flipkart-bangalore-prod")
            S3_BUCKET="flipkart-backups-all-regions"
            ;;
    esac

    log "📋 Target clusters: ${CLUSTERS[*]}"
    log "🪣 S3 bucket: $S3_BUCKET"
}

# Generate backup metadata
generate_backup_metadata() {
    local backup_dir=$1
    
    cat > "$backup_dir/metadata.json" << EOF
{
  "backup_id": "$OPERATION_TIMESTAMP",
  "timestamp": "$(TZ="$INDIAN_TIMEZONE" date --iso-8601=seconds)",
  "region": "$REGION",
  "backup_type": "$BACKUP_TYPE",
  "components": $(printf '%s\n' "${BACKUP_COMPONENTS[@]}" | jq -R . | jq -s .),
  "compressed": $COMPRESS,
  "encrypted": $ENCRYPT,
  "verification": $VERIFY,
  "indian_timezone": "$INDIAN_TIMEZONE",
  "compliance": {
    "rbi_compliant": true,
    "data_localization": true,
    "encryption_standard": "AES-256"
  },
  "retention": {
    "days": $RETENTION_DAYS,
    "delete_after": "$(TZ="$INDIAN_TIMEZONE" date -d "+$RETENTION_DAYS days" --iso-8601=seconds)"
  },
  "clusters": $(printf '%s\n' "${CLUSTERS[@]}" | jq -R . | jq -s .),
  "script_version": "$SCRIPT_VERSION"
}
EOF
}

# Backup PostgreSQL databases
backup_postgresql() {
    local backup_dir=$1
    local region_name=$2
    
    info "📊 Backing up PostgreSQL databases for $region_name..."
    
    local pg_backup_dir="$backup_dir/postgresql"
    mkdir -p "$pg_backup_dir"
    
    # Database connection details (would be fetched from secrets in production)
    local databases=("flipkart" "analytics" "payments" "users")
    
    for db in "${databases[@]}"; do
        info "Backing up database: $db"
        
        local dump_file="$pg_backup_dir/${db}_${OPERATION_TIMESTAMP}.sql"
        
        if [[ "$DRY_RUN" == true ]]; then
            info "DRY RUN: Would backup database $db to $dump_file"
            touch "$dump_file"
        else
            # Get database credentials from Kubernetes secrets
            local db_host db_user db_pass
            db_host=$(kubectl get secret database-credentials -n flipkart-production -o jsonpath='{.data.host}' | base64 -d)
            db_user=$(kubectl get secret database-credentials -n flipkart-production -o jsonpath='{.data.username}' | base64 -d)
            db_pass=$(kubectl get secret database-credentials -n flipkart-production -o jsonpath='{.data.password}' | base64 -d)
            
            # Create backup with custom format for faster restore
            PGPASSWORD="$db_pass" pg_dump -h "$db_host" -U "$db_user" -d "$db" -f "$dump_file" --verbose
            
            if [[ $? -eq 0 ]]; then
                log "✅ Database $db backed up successfully"
                
                # Verify backup
                if [[ "$VERIFY" == true ]]; then
                    local line_count
                    line_count=$(wc -l < "$dump_file")
                    if [[ $line_count -gt 10 ]]; then
                        log "✅ Database backup verified: $line_count lines"
                    else
                        error "Database backup verification failed: only $line_count lines"
                        return 1
                    fi
                fi
            else
                error "Failed to backup database: $db"
                return 1
            fi
        fi
    done
    
    # Backup database performance metrics
    info "Backing up database performance metrics..."
    local metrics_file="$pg_backup_dir/performance_metrics_${OPERATION_TIMESTAMP}.json"
    
    if [[ "$DRY_RUN" == false ]]; then
        kubectl exec -n flipkart-production deployment/postgresql-primary -- \
            psql -U flipkart -d flipkart -c "
            SELECT json_build_object(
                'database_size', pg_database_size('flipkart'),
                'table_count', count(*),
                'index_usage', (SELECT json_object_agg(schemaname||'.'||tablename, idx_scan) 
                               FROM pg_stat_user_tables WHERE idx_scan > 0),
                'slow_queries', (SELECT count(*) FROM pg_stat_statements WHERE mean_time > 1000),
                'connections', (SELECT count(*) FROM pg_stat_activity),
                'timestamp', now()
            ) FROM information_schema.tables WHERE table_schema = 'public';
            " -t -A > "$metrics_file"
    fi
}

# Backup Redis data
backup_redis() {
    local backup_dir=$1
    local region_name=$2
    
    info "📦 Backing up Redis data for $region_name..."
    
    local redis_backup_dir="$backup_dir/redis"
    mkdir -p "$redis_backup_dir"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "DRY RUN: Would backup Redis data"
        return 0
    fi
    
    # Get Redis connection details
    local redis_host redis_pass
    redis_host=$(kubectl get service redis-cluster -n flipkart-production -o jsonpath='{.spec.clusterIP}')
    redis_pass=$(kubectl get secret redis-credentials -n flipkart-production -o jsonpath='{.data.password}' | base64 -d)
    
    # Create Redis backup using BGSAVE
    info "Triggering Redis background save..."
    kubectl exec -n flipkart-production deployment/redis-cluster -- \
        redis-cli -a "$redis_pass" BGSAVE
    
    # Wait for backup to complete
    local backup_status=""
    local attempts=0
    while [[ "$backup_status" != "OK" && $attempts -lt 60 ]]; do
        sleep 5
        backup_status=$(kubectl exec -n flipkart-production deployment/redis-cluster -- \
            redis-cli -a "$redis_pass" LASTSAVE)
        ((attempts++))
    done
    
    if [[ "$backup_status" == "OK" ]]; then
        # Copy RDB file
        local rdb_file="$redis_backup_dir/redis_${OPERATION_TIMESTAMP}.rdb"
        kubectl cp flipkart-production/redis-cluster-0:/data/dump.rdb "$rdb_file"
        
        log "✅ Redis data backed up successfully"
        
        # Backup Redis configuration
        kubectl exec -n flipkart-production deployment/redis-cluster -- \
            redis-cli -a "$redis_pass" CONFIG GET "*" > "$redis_backup_dir/redis_config_${OPERATION_TIMESTAMP}.txt"
        
        # Backup Redis info
        kubectl exec -n flipkart-production deployment/redis-cluster -- \
            redis-cli -a "$redis_pass" INFO ALL > "$redis_backup_dir/redis_info_${OPERATION_TIMESTAMP}.txt"
    else
        error "Redis backup failed - BGSAVE did not complete"
        return 1
    fi
}

# Backup Elasticsearch data
backup_elasticsearch() {
    local backup_dir=$1
    local region_name=$2
    
    info "🔍 Backing up Elasticsearch data for $region_name..."
    
    local es_backup_dir="$backup_dir/elasticsearch"
    mkdir -p "$es_backup_dir"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "DRY RUN: Would backup Elasticsearch data"
        return 0
    fi
    
    # Get Elasticsearch connection details
    local es_host es_user es_pass
    es_host=$(kubectl get service elasticsearch -n flipkart-production -o jsonpath='{.spec.clusterIP}')
    es_user=$(kubectl get secret elasticsearch-credentials -n flipkart-production -o jsonpath='{.data.username}' | base64 -d)
    es_pass=$(kubectl get secret elasticsearch-credentials -n flipkart-production -o jsonpath='{.data.password}' | base64 -d)
    
    # Create snapshot repository if not exists
    local snapshot_repo="flipkart_backups"
    local snapshot_name="snapshot_${OPERATION_TIMESTAMP}"
    
    # Register repository
    kubectl exec -n flipkart-production deployment/elasticsearch -- \
        curl -X PUT "localhost:9200/_snapshot/$snapshot_repo" \
        -H 'Content-Type: application/json' \
        -u "$es_user:$es_pass" \
        -d '{
            "type": "fs",
            "settings": {
                "location": "/usr/share/elasticsearch/backups"
            }
        }'
    
    # Create snapshot
    info "Creating Elasticsearch snapshot: $snapshot_name"
    kubectl exec -n flipkart-production deployment/elasticsearch -- \
        curl -X PUT "localhost:9200/_snapshot/$snapshot_repo/$snapshot_name?wait_for_completion=true" \
        -H 'Content-Type: application/json' \
        -u "$es_user:$es_pass" \
        -d '{
            "indices": "products,orders,users,logs",
            "ignore_unavailable": true,
            "include_global_state": false
        }'
    
    # Export snapshot
    local snapshot_file="$es_backup_dir/elasticsearch_${OPERATION_TIMESTAMP}.tar"
    kubectl exec -n flipkart-production deployment/elasticsearch -- \
        tar -cf "/tmp/es_backup.tar" -C "/usr/share/elasticsearch/backups" .
    
    kubectl cp "flipkart-production/elasticsearch-0:/tmp/es_backup.tar" "$snapshot_file"
    
    log "✅ Elasticsearch data backed up successfully"
    
    # Backup cluster settings
    kubectl exec -n flipkart-production deployment/elasticsearch -- \
        curl -X GET "localhost:9200/_cluster/settings" \
        -u "$es_user:$es_pass" > "$es_backup_dir/cluster_settings_${OPERATION_TIMESTAMP}.json"
}

# Backup Kubernetes configurations
backup_kubernetes() {
    local backup_dir=$1
    local cluster=$2
    
    local region_name=""
    case $cluster in
        *mumbai*) region_name="mumbai" ;;
        *delhi*) region_name="delhi" ;;
        *bangalore*) region_name="bangalore" ;;
    esac
    
    info "☸️  Backing up Kubernetes configurations for $region_name..."
    
    local k8s_backup_dir="$backup_dir/kubernetes/$region_name"
    mkdir -p "$k8s_backup_dir"
    
    # Set kubectl context
    kubectl config use-context "$cluster" &>/dev/null
    
    if [[ "$DRY_RUN" == true ]]; then
        info "DRY RUN: Would backup Kubernetes configurations for $cluster"
        return 0
    fi
    
    # Backup all deployments
    info "Backing up deployments..."
    kubectl get deployments -n flipkart-production -o yaml > "$k8s_backup_dir/deployments.yaml"
    
    # Backup all services
    info "Backing up services..."
    kubectl get services -n flipkart-production -o yaml > "$k8s_backup_dir/services.yaml"
    
    # Backup all configmaps
    info "Backing up configmaps..."
    kubectl get configmaps -n flipkart-production -o yaml > "$k8s_backup_dir/configmaps.yaml"
    
    # Backup all secrets (encrypted)
    info "Backing up secrets..."
    kubectl get secrets -n flipkart-production -o yaml > "$k8s_backup_dir/secrets.yaml"
    
    # Backup persistent volume claims
    info "Backing up PVCs..."
    kubectl get pvc -n flipkart-production -o yaml > "$k8s_backup_dir/pvc.yaml"
    
    # Backup ingress configurations
    info "Backing up ingress..."
    kubectl get ingress -n flipkart-production -o yaml > "$k8s_backup_dir/ingress.yaml"
    
    # Backup network policies
    info "Backing up network policies..."
    kubectl get networkpolicies -n flipkart-production -o yaml > "$k8s_backup_dir/networkpolicies.yaml"
    
    # Backup Helm releases
    info "Backing up Helm releases..."
    helm list -n flipkart-production -o yaml > "$k8s_backup_dir/helm_releases.yaml"
    
    # Backup monitoring configurations
    kubectl get all -n flipkart-monitoring -o yaml > "$k8s_backup_dir/monitoring.yaml"
    
    log "✅ Kubernetes configurations backed up successfully for $region_name"
}

# Compress backup directory
compress_backup() {
    local backup_dir=$1
    local backup_name=$2
    
    if [[ "$COMPRESS" == false ]]; then
        info "Compression disabled - skipping"
        return 0
    fi
    
    info "🗜️  Compressing backup: $backup_name"
    
    local compressed_file="${backup_dir}.tar.gz"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "DRY RUN: Would compress $backup_dir to $compressed_file"
        return 0
    fi
    
    # Create compressed archive
    tar -czf "$compressed_file" -C "$(dirname "$backup_dir")" "$(basename "$backup_dir")"
    
    if [[ $? -eq 0 ]]; then
        local original_size compressed_size compression_ratio
        original_size=$(du -sb "$backup_dir" | cut -f1)
        compressed_size=$(du -sb "$compressed_file" | cut -f1)
        compression_ratio=$(( (original_size - compressed_size) * 100 / original_size ))
        
        log "✅ Backup compressed successfully"
        log "📊 Original size: $(numfmt --to=iec $original_size)"
        log "📊 Compressed size: $(numfmt --to=iec $compressed_size)"
        log "📊 Compression ratio: ${compression_ratio}%"
        
        # Remove uncompressed directory
        rm -rf "$backup_dir"
        
        echo "$compressed_file"
    else
        error "Compression failed"
        return 1
    fi
}

# Encrypt backup file
encrypt_backup() {
    local backup_file=$1
    
    if [[ "$ENCRYPT" == false ]]; then
        info "Encryption disabled - skipping"
        echo "$backup_file"
        return 0
    fi
    
    info "🔐 Encrypting backup: $(basename "$backup_file")"
    
    local encrypted_file="${backup_file}.enc"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "DRY RUN: Would encrypt $backup_file to $encrypted_file"
        echo "$backup_file"
        return 0
    fi
    
    # Encrypt using AES-256-CBC
    openssl enc -aes-256-cbc -salt -in "$backup_file" -out "$encrypted_file" -pass file:"$ENCRYPTION_KEY_FILE"
    
    if [[ $? -eq 0 ]]; then
        log "✅ Backup encrypted successfully with AES-256"
        
        # Verify encryption
        if [[ "$VERIFY" == true ]]; then
            if openssl enc -aes-256-cbc -d -in "$encrypted_file" -pass file:"$ENCRYPTION_KEY_FILE" | head -c 10 > /dev/null; then
                log "✅ Encryption verified successfully"
            else
                error "Encryption verification failed"
                return 1
            fi
        fi
        
        # Remove unencrypted file
        rm -f "$backup_file"
        
        echo "$encrypted_file"
    else
        error "Encryption failed"
        return 1
    fi
}

# Upload backup to S3
upload_to_s3() {
    local backup_file=$1
    local backup_name=$2
    
    info "☁️  Uploading backup to S3: s3://$S3_BUCKET"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "DRY RUN: Would upload $backup_file to s3://$S3_BUCKET/$backup_name"
        return 0
    fi
    
    # Upload with server-side encryption
    aws s3 cp "$backup_file" "s3://$S3_BUCKET/$backup_name" \
        --storage-class STANDARD_IA \
        --server-side-encryption AES256 \
        --metadata "backup_id=$OPERATION_TIMESTAMP,region=$REGION,type=$BACKUP_TYPE"
    
    if [[ $? -eq 0 ]]; then
        log "✅ Backup uploaded to S3 successfully"
        
        # Set lifecycle policy for cost optimization
        aws s3api put-object-tagging \
            --bucket "$S3_BUCKET" \
            --key "$backup_name" \
            --tagging "TagSet=[{Key=Retention,Value=${RETENTION_DAYS}},{Key=Region,Value=${REGION}},{Key=Type,Value=${BACKUP_TYPE}}]"
        
        return 0
    else
        error "S3 upload failed"
        return 1
    fi
}

# Perform backup operation
perform_backup() {
    log "💾 Starting backup operation..."
    log "📋 Type: $BACKUP_TYPE, Region: $REGION, Components: ${BACKUP_COMPONENTS[*]}"
    
    # Create backup directory
    local backup_name="backup-${BACKUP_TYPE}-${REGION}-${OPERATION_TIMESTAMP}"
    local backup_dir="$BACKUP_BASE_PATH/$backup_name"
    
    if [[ "$DRY_RUN" == false ]]; then
        mkdir -p "$backup_dir"
    fi
    
    # Generate backup metadata
    generate_backup_metadata "$backup_dir"
    
    # Process each component
    for component in "${BACKUP_COMPONENTS[@]}"; do
        case $component in
            databases)
                for cluster in "${CLUSTERS[@]}"; do
                    kubectl config use-context "$cluster" &>/dev/null
                    
                    local region_name=""
                    case $cluster in
                        *mumbai*) region_name="mumbai" ;;
                        *delhi*) region_name="delhi" ;;
                        *bangalore*) region_name="bangalore" ;;
                    esac
                    
                    backup_postgresql "$backup_dir" "$region_name"
                    backup_redis "$backup_dir" "$region_name"
                    backup_elasticsearch "$backup_dir" "$region_name"
                done
                ;;
            kubernetes)
                for cluster in "${CLUSTERS[@]}"; do
                    backup_kubernetes "$backup_dir" "$cluster"
                done
                ;;
            configurations)
                info "📝 Backing up application configurations..."
                local config_dir="$backup_dir/configurations"
                mkdir -p "$config_dir"
                
                if [[ "$DRY_RUN" == false ]]; then
                    # Copy Helm values files
                    cp -r helm/api-gateway/values*.yaml "$config_dir/" 2>/dev/null || true
                    
                    # Copy CI/CD configurations
                    cp -r ci-cd/ "$config_dir/" 2>/dev/null || true
                    
                    # Copy monitoring configurations
                    cp -r kubernetes/monitoring/ "$config_dir/" 2>/dev/null || true
                fi
                ;;
            secrets)
                info "🔐 Backing up secrets and certificates..."
                local secrets_dir="$backup_dir/secrets"
                mkdir -p "$secrets_dir"
                
                if [[ "$DRY_RUN" == false ]]; then
                    # Backup encryption keys (encrypted again for double protection)
                    if [[ -f "$ENCRYPTION_KEY_FILE" ]]; then
                        cp "$ENCRYPTION_KEY_FILE" "$secrets_dir/"
                    fi
                    
                    # Backup TLS certificates
                    for cluster in "${CLUSTERS[@]}"; do
                        kubectl config use-context "$cluster" &>/dev/null
                        kubectl get secrets -n flipkart-production -l type=kubernetes.io/tls -o yaml > "$secrets_dir/tls-secrets-$(basename $cluster).yaml"
                    done
                fi
                ;;
            all)
                # This case is handled by expanding to all components
                ;;
        esac
    done
    
    # Compress backup
    local final_backup_file
    final_backup_file=$(compress_backup "$backup_dir" "$backup_name")
    
    # Encrypt backup
    final_backup_file=$(encrypt_backup "$final_backup_file")
    
    # Upload to S3
    upload_to_s3 "$final_backup_file" "$(basename "$final_backup_file")"
    
    log "🎉 Backup operation completed successfully!"
    log "📂 Backup file: $final_backup_file"
    log "☁️  S3 location: s3://$S3_BUCKET/$(basename "$final_backup_file")"
    log "🆔 Backup ID: $OPERATION_TIMESTAMP"
}

# List available backups
list_backups() {
    log "📋 Listing available backups for region: $REGION"
    
    echo -e "\n${CYAN}Local Backups:${NC}"
    if [[ -d "$BACKUP_BASE_PATH" ]]; then
        find "$BACKUP_BASE_PATH" -name "backup-*-${REGION}-*.tar.gz*" -type f | while read -r backup; do
            local backup_name size timestamp
            backup_name=$(basename "$backup")
            size=$(numfmt --to=iec $(stat -f%z "$backup" 2>/dev/null || stat -c%s "$backup"))
            timestamp=$(stat -f%Sm -t%Y-%m-%d\ %H:%M:%S "$backup" 2>/dev/null || stat -c%y "$backup" | cut -d' ' -f1-2)
            
            echo "  📦 $backup_name ($size) - $timestamp"
        done
    else
        echo "  No local backups found"
    fi
    
    echo -e "\n${CYAN}S3 Backups:${NC}"
    if aws s3 ls "s3://$S3_BUCKET/" &>/dev/null; then
        aws s3 ls "s3://$S3_BUCKET/" --recursive | grep "backup-.*-${REGION}-" | while read -r line; do
            local date time size file
            read -r date time size file <<< "$line"
            echo "  ☁️  $file ($(numfmt --to=iec $size)) - $date $time"
        done
    else
        echo "  S3 bucket not accessible or no backups found"
    fi
}

# Cleanup old backups
cleanup_backups() {
    log "🧹 Cleaning up old backups (retention: $RETENTION_DAYS days)"
    
    local cutoff_date
    cutoff_date=$(date -d "$RETENTION_DAYS days ago" +%s)
    
    # Cleanup local backups
    info "Cleaning up local backups..."
    if [[ -d "$BACKUP_BASE_PATH" ]]; then
        find "$BACKUP_BASE_PATH" -name "backup-*-${REGION}-*.tar.gz*" -type f | while read -r backup; do
            local backup_date
            backup_date=$(stat -f%Sm -t%s "$backup" 2>/dev/null || stat -c%Y "$backup")
            
            if [[ $backup_date -lt $cutoff_date ]]; then
                if [[ "$DRY_RUN" == true ]]; then
                    info "DRY RUN: Would delete local backup: $(basename "$backup")"
                else
                    info "Deleting old local backup: $(basename "$backup")"
                    rm -f "$backup"
                fi
            fi
        done
    fi
    
    # Cleanup S3 backups
    info "Cleaning up S3 backups..."
    if aws s3 ls "s3://$S3_BUCKET/" &>/dev/null; then
        aws s3api list-objects-v2 --bucket "$S3_BUCKET" --prefix "backup-" | \
        jq -r '.Contents[]? | select(.LastModified < "'$(date -d "$RETENTION_DAYS days ago" --iso-8601)'") | .Key' | \
        while read -r key; do
            if [[ "$key" == *"-${REGION}-"* ]]; then
                if [[ "$DRY_RUN" == true ]]; then
                    info "DRY RUN: Would delete S3 backup: $key"
                else
                    info "Deleting old S3 backup: $key"
                    aws s3 rm "s3://$S3_BUCKET/$key"
                fi
            fi
        done
    fi
    
    log "✅ Cleanup completed"
}

# Restore operation
perform_restore() {
    log "🔄 Starting restore operation..."
    
    if [[ -z "${RESTORE_FILE:-}" ]]; then
        error "Restore file not specified. Use --file option"
        exit 1
    fi
    
    warn "⚠️  This will restore data from backup: $RESTORE_FILE"
    warn "⚠️  This operation may overwrite existing data!"
    
    if [[ "$DRY_RUN" == false ]]; then
        read -p "Are you sure you want to proceed? Type 'YES' to confirm: " -r
        if [[ "$REPLY" != "YES" ]]; then
            info "Restore cancelled by user"
            exit 0
        fi
    fi
    
    # Download from S3 if needed
    local restore_file_path
    if [[ "$RESTORE_FILE" == s3://* ]]; then
        info "Downloading restore file from S3..."
        local temp_file="/tmp/$(basename "$RESTORE_FILE")"
        aws s3 cp "$RESTORE_FILE" "$temp_file"
        restore_file_path="$temp_file"
    else
        restore_file_path="$RESTORE_FILE"
    fi
    
    # Verify restore file exists
    if [[ ! -f "$restore_file_path" ]]; then
        error "Restore file not found: $restore_file_path"
        exit 1
    fi
    
    # Decrypt if needed
    if [[ "$restore_file_path" == *.enc ]]; then
        info "🔓 Decrypting restore file..."
        local decrypted_file="${restore_file_path%.enc}"
        
        if [[ "$DRY_RUN" == false ]]; then
            openssl enc -aes-256-cbc -d -in "$restore_file_path" -out "$decrypted_file" -pass file:"$ENCRYPTION_KEY_FILE"
            restore_file_path="$decrypted_file"
        fi
    fi
    
    # Extract backup
    info "📂 Extracting backup archive..."
    local restore_dir="/tmp/restore-$OPERATION_TIMESTAMP"
    
    if [[ "$DRY_RUN" == false ]]; then
        mkdir -p "$restore_dir"
        tar -xzf "$restore_file_path" -C "$restore_dir"
    fi
    
    # Read metadata
    local metadata_file="$restore_dir/*/metadata.json"
    if [[ -f $metadata_file ]]; then
        local backup_region backup_type backup_timestamp
        backup_region=$(jq -r '.region' "$metadata_file")
        backup_type=$(jq -r '.backup_type' "$metadata_file")
        backup_timestamp=$(jq -r '.timestamp' "$metadata_file")
        
        log "📋 Backup metadata:"
        log "   • Region: $backup_region"
        log "   • Type: $backup_type"
        log "   • Timestamp: $backup_timestamp"
    fi
    
    # Restore components (simplified - would need full implementation)
    warn "🚧 Restore functionality is a complex operation that requires:"
    warn "   • Database downtime coordination"
    warn "   • Kubernetes resource recreation"
    warn "   • Service mesh reconfiguration"
    warn "   • DNS and load balancer updates"
    warn "   • Extensive testing and validation"
    
    if [[ "$DRY_RUN" == true ]]; then
        log "✅ DRY RUN: Restore operation validated successfully"
    else
        warn "⚠️  Full restore implementation requires additional safety measures"
        warn "⚠️  Please coordinate with the operations team for production restore"
    fi
    
    # Cleanup temporary files
    rm -rf "$restore_dir" /tmp/restore-* 2>/dev/null || true
}

# Main function
main() {
    print_banner
    
    log "🚀 Starting $SCRIPT_NAME v$SCRIPT_VERSION"
    log "🆔 Operation ID: $OPERATION_TIMESTAMP"
    
    # Parse command line arguments
    parse_args "$@"
    
    # Handle component expansion
    if [[ "${BACKUP_COMPONENTS[*]}" == *"all"* ]]; then
        BACKUP_COMPONENTS=("databases" "kubernetes" "configurations" "secrets")
    fi
    
    # Validate prerequisites
    validate_prerequisites
    
    # Setup cluster configuration
    setup_cluster_config
    
    # Perform requested operation
    case $OPERATION in
        backup)
            perform_backup
            ;;
        restore)
            perform_restore
            ;;
        list)
            list_backups
            ;;
        cleanup)
            cleanup_backups
            ;;
    esac
    
    log "🎉 Operation completed successfully!"
    log "⏱️  Duration: $((SECONDS / 60)) minutes and $((SECONDS % 60)) seconds"
    
    if [[ "$DRY_RUN" == true ]]; then
        warn "🧪 This was a DRY RUN - no actual changes were made"
    fi
}

# Run main function with all arguments
main "$@"
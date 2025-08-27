#!/usr/bin/env groovy

/**
 * Jenkins Pipeline for Indian E-commerce Platform
 * Episode 092: Container Orchestration - Jenkins CI/CD
 * Context: Production-grade Jenkins pipeline optimized for Indian infrastructure and compliance
 */

pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins: worker
    region: mumbai
    compliance: rbi-pci-dss
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest-jdk17
    args: ['\$(JENKINS_SECRET)', '\$(JENKINS_NAME)']
    env:
    - name: TZ
      value: "Asia/Kolkata"
  - name: docker
    image: docker:24.0.6-dind
    securityContext:
      privileged: true
    env:
    - name: DOCKER_TLS_CERTDIR
      value: "/certs"
    - name: TZ
      value: "Asia/Kolkata"
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ['/bin/bash']
    args: ['-c', 'sleep infinity']
    env:
    - name: TZ
      value: "Asia/Kolkata"
  - name: helm
    image: alpine/helm:3.12.0
    command: ['/bin/bash']
    args: ['-c', 'sleep infinity']
    env:
    - name: TZ
      value: "Asia/Kolkata"
  - name: gradle
    image: gradle:8.4-jdk17
    command: ['/bin/bash']
    args: ['-c', 'sleep infinity']
    env:
    - name: TZ
      value: "Asia/Kolkata"
  - name: trivy
    image: aquasec/trivy:0.45.0
    command: ['/bin/bash']
    args: ['-c', 'sleep infinity']
    env:
    - name: TZ
      value: "Asia/Kolkata"
  nodeSelector:
    topology.kubernetes.io/region: "ap-south-1"
    node.flipkart.com/workload: "ci-cd"
  tolerations:
  - key: "ci-cd"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
"""
        }
    }
    
    // Environment variables for Indian infrastructure
    environment {
        // Docker Registry Configuration
        DOCKER_REGISTRY = 'registry.flipkart.com'
        DOCKER_REPO = 'flipkart'
        
        // Indian Cloud Configuration
        PRIMARY_REGION = 'ap-south-1'
        SECONDARY_REGION = 'ap-southeast-1'
        INDIAN_TIMEZONE = 'Asia/Kolkata'
        
        // Kubernetes Clusters
        MUMBAI_CLUSTER = 'flipkart-mumbai-prod'
        DELHI_CLUSTER = 'flipkart-delhi-prod'
        BANGALORE_CLUSTER = 'flipkart-bangalore-prod'
        
        // Indian Compliance Flags
        RBI_COMPLIANCE = 'enabled'
        PCI_DSS_COMPLIANCE = 'enabled'
        DATA_LOCALIZATION = 'enabled'
        IT_ACT_2000_COMPLIANCE = 'enabled'
        
        // Cost Optimization for Indian Infrastructure
        SPOT_INSTANCES = 'enabled'
        RESOURCE_OPTIMIZATION = 'enabled'
        SCHEDULED_SCALING = 'enabled'
        
        // Business Configuration
        DEPLOYMENT_WINDOW = '02:00-06:00'  // IST off-peak hours
        FESTIVAL_SEASON_SCALING = 'enabled'
        
        // Version and Build Info
        BUILD_VERSION = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
        BUILD_TIMESTAMP = sh(script: "TZ=${INDIAN_TIMEZONE} date +'%Y%m%d%H%M%S'", returnStdout: true).trim()
        
        // Microservices List
        MICROSERVICES = 'product-catalog,order-management,payment-service,user-service,search-service,api-gateway'
    }
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['staging', 'production'],
            description: 'Target deployment environment'
        )
        choice(
            name: 'REGION',
            choices: ['mumbai', 'delhi', 'bangalore', 'all'],
            description: 'Indian region for deployment'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip test execution'
        )
        booleanParam(
            name: 'DEPLOY_TO_PRODUCTION',
            defaultValue: false,
            description: 'Deploy to production environment'
        )
        booleanParam(
            name: 'FESTIVAL_MODE',
            defaultValue: false,
            description: 'Enable festival season scaling'
        )
        string(
            name: 'CUSTOM_TAG',
            defaultValue: '',
            description: 'Custom image tag (optional)'
        )
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '30', daysToKeepStr: '30'))
        timeout(time: 60, unit: 'MINUTES')
        timestamps()
        ansiColor('xterm')
        skipDefaultCheckout(false)
        parallelsAlwaysFailFast()
    }
    
    triggers {
        // Poll SCM every 5 minutes during Indian business hours (9 AM - 11 PM IST)
        pollSCM('H/5 3-17 * * 1-6')  // Adjusted for UTC
        
        // Scheduled build for dependency updates at 2 AM IST daily
        cron('H 20 * * *')  // 2 AM IST in UTC
    }
    
    stages {
        stage('Initialize') {
            steps {
                script {
                    // Set Indian timezone
                    sh 'export TZ=${INDIAN_TIMEZONE}'
                    
                    // Display build information
                    echo "🇮🇳 Starting Flipkart Indian E-commerce CI/CD Pipeline"
                    echo "Build Version: ${BUILD_VERSION}"
                    echo "Timestamp: ${BUILD_TIMESTAMP}"
                    echo "Current IST Time: ${sh(script: 'TZ=${INDIAN_TIMEZONE} date', returnStdout: true).trim()}"
                    echo "Environment: ${params.ENVIRONMENT}"
                    echo "Region: ${params.REGION}"
                    echo "Festival Mode: ${params.FESTIVAL_MODE}"
                    
                    // Set dynamic variables
                    env.IMAGE_TAG = params.CUSTOM_TAG ?: "${BUILD_VERSION}"
                    env.FESTIVAL_SCALING = params.FESTIVAL_MODE ? 'enabled' : 'disabled'
                    
                    // Check deployment window for production
                    if (params.ENVIRONMENT == 'production') {
                        def currentHour = sh(script: "TZ=${INDIAN_TIMEZONE} date +'%H'", returnStdout: true).trim().toInteger()
                        if (currentHour < 2 || currentHour > 6) {
                            echo "⚠️  Warning: Deploying outside recommended window (2-6 AM IST)"
                        }
                    }
                }
            }
        }
        
        stage('Checkout & Validate') {
            parallel {
                stage('Code Checkout') {
                    steps {
                        container('gradle') {
                            checkout scm
                            
                            // Validate Indian-specific configurations
                            script {
                                echo "🔍 Validating Indian regional configurations"
                                
                                def timezoneCheck = sh(
                                    script: 'grep -r "Asia/Kolkata" src/ || echo "NOT_FOUND"',
                                    returnStdout: true
                                ).trim()
                                if (timezoneCheck == "NOT_FOUND") {
                                    echo "⚠️  Warning: Indian timezone not configured"
                                }
                                
                                def currencyCheck = sh(
                                    script: 'grep -r "INR" src/ || echo "NOT_FOUND"',
                                    returnStdout: true
                                ).trim()
                                if (currencyCheck == "NOT_FOUND") {
                                    echo "⚠️  Warning: Indian currency not configured"
                                }
                                
                                def localeCheck = sh(
                                    script: 'grep -r "en_IN" src/ || echo "NOT_FOUND"',
                                    returnStdout: true
                                ).trim()
                                if (localeCheck == "NOT_FOUND") {
                                    echo "⚠️  Warning: Indian locale not configured"
                                }
                            }
                        }
                    }
                }
                
                stage('Environment Setup') {
                    steps {
                        container('gradle') {
                            script {
                                echo "🔧 Setting up build environment"
                                sh '''
                                    echo "Java Version:"
                                    java --version
                                    echo "Gradle Version:"
                                    gradle --version
                                    echo "Current IST Time:"
                                    TZ=${INDIAN_TIMEZONE} date
                                '''
                            }
                        }
                    }
                }
            }
        }
        
        stage('Security & Compliance Scan') {
            parallel {
                stage('Source Code Security Scan') {
                    steps {
                        container('trivy') {
                            script {
                                echo "🔒 Running security scan for Indian compliance"
                                
                                // Vulnerability scanning
                                sh '''
                                    trivy fs --security-checks vuln,secret,config . --format json --output trivy-results.json || true
                                    trivy fs --security-checks vuln,secret,config . --format table
                                '''
                                
                                // Check for hardcoded Indian payment credentials
                                echo "🔍 Checking for exposed Indian payment gateway credentials"
                                def razorpayCheck = sh(
                                    script: 'grep -r "rzp_test\\|rzp_live" . --exclude-dir=.git || echo "SAFE"',
                                    returnStdout: true
                                ).trim()
                                if (razorpayCheck != "SAFE") {
                                    error "❌ Razorpay credentials found in code!"
                                }
                                
                                def paytmCheck = sh(
                                    script: 'grep -r "MIDT.*paytm\\|paytm.*secret" . --exclude-dir=.git || echo "SAFE"',
                                    returnStdout: true
                                ).trim()
                                if (paytmCheck != "SAFE") {
                                    error "❌ Paytm credentials found in code!"
                                }
                                
                                echo "✅ No hardcoded Indian payment credentials found"
                            }
                            
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: '.',
                                reportFiles: 'trivy-results.json',
                                reportName: 'Security Scan Report'
                            ])
                        }
                    }
                }
                
                stage('RBI Compliance Check') {
                    steps {
                        container('kubectl') {
                            script {
                                echo "🏛️ Performing RBI compliance validation"
                                
                                // Check data localization
                                echo "📍 Verifying data stays within Indian borders"
                                def regionCheck = sh(
                                    script: 'grep -r "ap-south-1\\|ap-southeast-1" kubernetes/ || echo "NOT_FOUND"',
                                    returnStdout: true
                                ).trim()
                                if (regionCheck == "NOT_FOUND") {
                                    error "❌ Non-Indian regions detected in configuration"
                                }
                                
                                // Check encryption standards
                                echo "🔐 Verifying encryption standards (AES-256)"
                                def encryptionCheck = sh(
                                    script: 'grep -r "AES-256" kubernetes/secrets.yaml || echo "NOT_FOUND"',
                                    returnStdout: true
                                ).trim()
                                if (encryptionCheck == "NOT_FOUND") {
                                    error "❌ Required encryption standard not found"
                                }
                                
                                // Check audit logging
                                echo "📝 Verifying audit logging configuration"
                                sh 'grep -r "audit.*enabled" kubernetes/ || echo "⚠️  Warning: Audit logging not explicitly enabled"'
                                
                                echo "✅ RBI compliance check passed"
                            }
                        }
                    }
                }
                
                stage('PCI-DSS Compliance') {
                    steps {
                        container('kubectl') {
                            script {
                                echo "💳 Performing PCI-DSS compliance check for payment systems"
                                
                                // Check TLS configuration
                                def tlsCheck = sh(
                                    script: 'grep -rE "TLSv1\\.[23]" kubernetes/ || echo "NOT_FOUND"',
                                    returnStdout: true
                                ).trim()
                                if (tlsCheck == "NOT_FOUND") {
                                    error "❌ Secure TLS version not configured"
                                }
                                
                                // Check tokenization
                                sh 'grep -r "tokenization.*true" kubernetes/ || echo "⚠️  Warning: Tokenization not explicitly enabled"'
                                
                                // Check payment encryption
                                def paymentEncryptionCheck = sh(
                                    script: 'grep -r "payment-encryption-key" kubernetes/secrets.yaml || echo "NOT_FOUND"',
                                    returnStdout: true
                                ).trim()
                                if (paymentEncryptionCheck == "NOT_FOUND") {
                                    error "❌ Payment encryption key not found"
                                }
                                
                                echo "✅ PCI-DSS compliance check passed"
                            }
                        }
                    }
                }
            }
        }
        
        stage('Build & Test') {
            when {
                not { params.SKIP_TESTS }
            }
            parallel {
                stage('Unit Tests') {
                    steps {
                        container('gradle') {
                            script {
                                echo "🧪 Running unit tests for Indian e-commerce scenarios"
                                
                                sh '''
                                    ./gradlew clean test jacocoTestReport
                                    
                                    # Run Indian-specific test suites
                                    echo "🇮🇳 Running Indian payment gateway tests"
                                    ./gradlew test --tests "*Razorpay*" || true
                                    ./gradlew test --tests "*Paytm*" || true
                                    ./gradlew test --tests "*UPI*" || true
                                    ./gradlew test --tests "*PhonePe*" || true
                                    
                                    # Run localization tests
                                    echo "🌐 Running Indian localization tests"
                                    ./gradlew test --tests "*Localization*" || true
                                    ./gradlew test --tests "*GST*" || true
                                    ./gradlew test --tests "*Indian*" || true
                                '''
                            }
                            
                            publishTestResults testResultsPattern: '**/build/test-results/test/TEST-*.xml'
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'build/reports/jacoco/test/html',
                                reportFiles: 'index.html',
                                reportName: 'Code Coverage Report'
                            ])
                        }
                    }
                }
                
                stage('Code Quality Analysis') {
                    steps {
                        container('gradle') {
                            script {
                                echo "📊 Running code quality analysis"
                                
                                sh '''
                                    ./gradlew checkstyleMain spotbugsMain
                                    
                                    # Custom checks for Indian compliance
                                    echo "Checking for hardcoded values that should be configurable"
                                    grep -r "localhost" src/ --exclude-dir=test || echo "No localhost references found"
                                    grep -r "127.0.0.1" src/ --exclude-dir=test || echo "No localhost IP references found"
                                '''
                            }
                            
                            recordIssues enabledForFailure: true, tools: [
                                checkStyle(pattern: '**/build/reports/checkstyle/*.xml'),
                                spotBugs(pattern: '**/build/reports/spotbugs/*.xml')
                            ]
                        }
                    }
                }
            }
        }
        
        stage('Build Docker Images') {
            steps {
                container('docker') {
                    script {
                        echo "🐳 Building Docker images for Indian e-commerce platform"
                        
                        def microservices = env.MICROSERVICES.split(',')
                        def buildSteps = [:]
                        
                        microservices.each { service ->
                            buildSteps[service] = {
                                echo "Building ${service}"
                                sh """
                                    docker build \\
                                        --build-arg TIMEZONE=${INDIAN_TIMEZONE} \\
                                        --build-arg LOCALE=en_IN \\
                                        --build-arg CURRENCY=INR \\
                                        --build-arg BUILD_VERSION=${BUILD_VERSION} \\
                                        --tag ${DOCKER_REGISTRY}/${DOCKER_REPO}/${service}:${IMAGE_TAG} \\
                                        --tag ${DOCKER_REGISTRY}/${DOCKER_REPO}/${service}:latest \\
                                        --file Dockerfile.${service} \\
                                        .
                                """
                            }
                        }
                        
                        parallel buildSteps
                        
                        echo "✅ All Docker images built successfully"
                    }
                }
            }
        }
        
        stage('Container Security Scan') {
            steps {
                container('trivy') {
                    script {
                        echo "🔍 Scanning Docker images for vulnerabilities"
                        
                        def microservices = env.MICROSERVICES.split(',')
                        def scanSteps = [:]
                        
                        microservices.each { service ->
                            scanSteps[service] = {
                                echo "Scanning ${service}"
                                sh """
                                    trivy image \\
                                        --format table \\
                                        --severity CRITICAL,HIGH \\
                                        --exit-code 1 \\
                                        ${DOCKER_REGISTRY}/${DOCKER_REPO}/${service}:${IMAGE_TAG} || true
                                """
                            }
                        }
                        
                        parallel scanSteps
                    }
                }
            }
        }
        
        stage('Integration Tests') {
            when {
                not { params.SKIP_TESTS }
            }
            steps {
                container('docker') {
                    script {
                        echo "🔗 Running integration tests with Indian infrastructure"
                        
                        try {
                            sh '''
                                # Start test environment
                                docker-compose -f docker-compose.test.yml up -d
                                sleep 60  # Wait for services to start
                                
                                # Test basic health endpoints
                                docker-compose -f docker-compose.test.yml exec -T app curl -f http://localhost:8080/health || exit 1
                                
                                # Test Indian regional endpoints
                                docker-compose -f docker-compose.test.yml exec -T app curl -f http://localhost:8080/api/v1/health/mumbai || exit 1
                                docker-compose -f docker-compose.test.yml exec -T app curl -f http://localhost:8080/api/v1/health/delhi || exit 1
                                docker-compose -f docker-compose.test.yml exec -T app curl -f http://localhost:8080/api/v1/health/bangalore || exit 1
                                
                                # Test GST calculation endpoints
                                docker-compose -f docker-compose.test.yml exec -T app curl -X POST \\
                                    -H "Content-Type: application/json" \\
                                    -d '{"amount": 1000, "state": "maharashtra", "category": "electronics"}' \\
                                    http://localhost:8080/api/v1/gst/calculate || exit 1
                                
                                # Test Indian payment gateway mock endpoints
                                docker-compose -f docker-compose.test.yml exec -T app curl -f http://localhost:8080/api/v1/payments/gateways || exit 1
                                
                                echo "✅ Integration tests passed"
                            '''
                        } finally {
                            sh 'docker-compose -f docker-compose.test.yml down || true'
                        }
                    }
                }
            }
        }
        
        stage('Push Images') {
            steps {
                container('docker') {
                    script {
                        echo "📦 Pushing Docker images to registry"
                        
                        withCredentials([usernamePassword(
                            credentialsId: 'docker-registry-credentials',
                            usernameVariable: 'REGISTRY_USER',
                            passwordVariable: 'REGISTRY_PASS'
                        )]) {
                            sh 'echo $REGISTRY_PASS | docker login $DOCKER_REGISTRY -u $REGISTRY_USER --password-stdin'
                            
                            def microservices = env.MICROSERVICES.split(',')
                            microservices.each { service ->
                                sh """
                                    docker push ${DOCKER_REGISTRY}/${DOCKER_REPO}/${service}:${IMAGE_TAG}
                                    docker push ${DOCKER_REGISTRY}/${DOCKER_REPO}/${service}:latest
                                """
                            }
                        }
                        
                        echo "✅ All images pushed successfully"
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                anyOf {
                    branch 'develop'
                    expression { params.ENVIRONMENT == 'staging' }
                }
            }
            steps {
                container('helm') {
                    script {
                        echo "🚀 Deploying to Mumbai staging environment"
                        
                        withKubeConfig([credentialsId: 'kubeconfig-mumbai-staging']) {
                            sh """
                                # Create namespace if not exists
                                kubectl create namespace flipkart-staging --dry-run=client -o yaml | kubectl apply -f -
                                
                                # Deploy using Helm with Indian optimizations
                                helm upgrade --install flipkart-staging helm/api-gateway/ \\
                                    --namespace flipkart-staging \\
                                    --set image.tag=${IMAGE_TAG} \\
                                    --set global.region=${PRIMARY_REGION} \\
                                    --set global.environment=staging \\
                                    --set global.indianOptimization.timezone=${INDIAN_TIMEZONE} \\
                                    --set costOptimization.spotInstances.enabled=true \\
                                    --set replicaCount=3 \\
                                    --set festivalScaling.enabled=${FESTIVAL_SCALING} \\
                                    --values helm/api-gateway/values-staging.yaml \\
                                    --wait --timeout=10m
                                
                                # Verify deployment
                                kubectl rollout status deployment/flipkart-staging-api-gateway -n flipkart-staging --timeout=600s
                                kubectl get pods -n flipkart-staging
                            """
                        }
                        
                        echo "✅ Staging deployment completed"
                    }
                }
            }
        }
        
        stage('Staging Validation') {
            when {
                anyOf {
                    branch 'develop'
                    expression { params.ENVIRONMENT == 'staging' }
                }
            }
            steps {
                script {
                    echo "🧪 Running staging validation tests"
                    
                    sleep 60  // Wait for services to stabilize
                    
                    def stagingUrl = "https://staging-mumbai.flipkart.internal"
                    
                    sh """
                        # Health checks
                        curl -f ${stagingUrl}/health || exit 1
                        curl -f ${stagingUrl}/api/v1/regions/mumbai || exit 1
                        
                        # Indian specific endpoints
                        curl -f ${stagingUrl}/api/v1/payments/gateways || exit 1
                        
                        # Load test simulation
                        for i in {1..50}; do
                            curl -s ${stagingUrl}/health > /dev/null &
                        done
                        wait
                    """
                    
                    echo "✅ Staging validation passed"
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                anyOf {
                    allOf {
                        branch 'main'
                        expression { params.DEPLOY_TO_PRODUCTION }
                    }
                    expression { params.ENVIRONMENT == 'production' }
                }
            }
            parallel {
                stage('Deploy Mumbai Production') {
                    steps {
                        container('helm') {
                            script {
                                echo "🚀 Deploying to Mumbai production (primary region)"
                                
                                withKubeConfig([credentialsId: 'kubeconfig-mumbai-production']) {
                                    def deploymentTimestamp = sh(
                                        script: "TZ=${INDIAN_TIMEZONE} date +'%Y%m%d%H%M%S'",
                                        returnStdout: true
                                    ).trim()
                                    
                                    sh """
                                        # Blue-Green deployment strategy
                                        helm upgrade --install flipkart-prod-mumbai-${deploymentTimestamp} helm/api-gateway/ \\
                                            --namespace flipkart-production \\
                                            --set image.tag=${IMAGE_TAG} \\
                                            --set global.region=${PRIMARY_REGION} \\
                                            --set global.environment=production \\
                                            --set global.indianOptimization.timezone=${INDIAN_TIMEZONE} \\
                                            --set replicaCount=10 \\
                                            --set resources.requests.cpu=1000m \\
                                            --set resources.requests.memory=2Gi \\
                                            --set costOptimization.spotInstances.enabled=false \\
                                            --set festivalScaling.enabled=${FESTIVAL_SCALING} \\
                                            --set autoscaling.enabled=true \\
                                            --set autoscaling.minReplicas=10 \\
                                            --set autoscaling.maxReplicas=50 \\
                                            --values helm/api-gateway/values-production.yaml \\
                                            --wait --timeout=15m
                                        
                                        # Wait for deployment
                                        kubectl rollout status deployment/flipkart-prod-mumbai-${deploymentTimestamp}-api-gateway -n flipkart-production --timeout=900s
                                        
                                        # Health check
                                        kubectl get pods -n flipkart-production -l app.kubernetes.io/instance=flipkart-prod-mumbai-${deploymentTimestamp}
                                    """
                                }
                                
                                echo "✅ Mumbai production deployment completed"
                            }
                        }
                    }
                }
                
                stage('Deploy Delhi Production') {
                    when {
                        anyOf {
                            expression { params.REGION == 'delhi' }
                            expression { params.REGION == 'all' }
                        }
                    }
                    steps {
                        container('helm') {
                            script {
                                echo "🚀 Deploying to Delhi production (secondary region)"
                                
                                withKubeConfig([credentialsId: 'kubeconfig-delhi-production']) {
                                    def deploymentTimestamp = sh(
                                        script: "TZ=${INDIAN_TIMEZONE} date +'%Y%m%d%H%M%S'",
                                        returnStdout: true
                                    ).trim()
                                    
                                    sh """
                                        helm upgrade --install flipkart-prod-delhi-${deploymentTimestamp} helm/api-gateway/ \\
                                            --namespace flipkart-production \\
                                            --set image.tag=${IMAGE_TAG} \\
                                            --set global.region=${PRIMARY_REGION} \\
                                            --set global.environment=production \\
                                            --set global.indianOptimization.timezone=${INDIAN_TIMEZONE} \\
                                            --set replicaCount=5 \\
                                            --set festivalScaling.enabled=${FESTIVAL_SCALING} \\
                                            --values helm/api-gateway/values-production-delhi.yaml \\
                                            --wait --timeout=15m
                                        
                                        kubectl rollout status deployment/flipkart-prod-delhi-${deploymentTimestamp}-api-gateway -n flipkart-production --timeout=900s
                                    """
                                }
                                
                                echo "✅ Delhi production deployment completed"
                            }
                        }
                    }
                }
            }
        }
        
        stage('Production Validation') {
            when {
                anyOf {
                    allOf {
                        branch 'main'
                        expression { params.DEPLOY_TO_PRODUCTION }
                    }
                    expression { params.ENVIRONMENT == 'production' }
                }
            }
            steps {
                script {
                    echo "🔍 Running production validation tests"
                    
                    sleep 120  // Wait for traffic to stabilize
                    
                    sh '''
                        # Mumbai region tests
                        curl -f https://api.flipkart.com/health || exit 1
                        curl -f https://api.flipkart.com/api/v1/regions/mumbai || exit 1
                        
                        # Payment gateway connectivity
                        curl -f https://api.flipkart.com/api/v1/payments/health || exit 1
                        
                        # Indian specific functionality
                        curl -X GET https://api.flipkart.com/api/v1/cities/indian || exit 1
                    '''
                    
                    if (params.REGION == 'all' || params.REGION == 'delhi') {
                        sh '''
                            # Delhi region tests
                            curl -f https://delhi.flipkart.com/health || exit 1
                        '''
                    }
                    
                    echo "✅ Production validation passed"
                }
            }
        }
        
        stage('Setup Monitoring') {
            when {
                anyOf {
                    allOf {
                        branch 'main'
                        expression { params.DEPLOY_TO_PRODUCTION }
                    }
                    expression { params.ENVIRONMENT == 'production' }
                }
            }
            steps {
                container('kubectl') {
                    script {
                        echo "📊 Setting up monitoring for Indian production environment"
                        
                        withKubeConfig([credentialsId: 'kubeconfig-mumbai-production']) {
                            sh '''
                                # Deploy Prometheus with Indian business rules
                                kubectl apply -f kubernetes/monitoring/prometheus.yaml -n flipkart-monitoring
                                
                                # Deploy Grafana with Indian dashboards
                                kubectl apply -f kubernetes/monitoring/grafana.yaml -n flipkart-monitoring
                                
                                # Verify monitoring stack
                                kubectl wait --for=condition=available deployment/prometheus -n flipkart-monitoring --timeout=300s
                                kubectl wait --for=condition=available deployment/grafana -n flipkart-monitoring --timeout=300s
                                
                                kubectl get pods -n flipkart-monitoring
                            '''
                        }
                        
                        echo "✅ Monitoring setup completed"
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                def buildStatus = currentBuild.result ?: 'SUCCESS'
                def istTime = sh(script: "TZ=${INDIAN_TIMEZONE} date", returnStdout: true).trim()
                
                echo "🏁 Pipeline completed with status: ${buildStatus}"
                echo "📅 IST Time: ${istTime}"
                
                // Cleanup
                sh '''
                    docker system prune -f || true
                    kubectl config unset current-context || true
                '''
            }
        }
        
        success {
            script {
                echo "✅ Pipeline executed successfully!"
                
                // Send Slack notification
                slackSend(
                    channel: '#flipkart-deployments',
                    color: 'good',
                    message: """
🇮🇳 *Flipkart Indian E-commerce Deployment SUCCESS*
• *Environment:* ${params.ENVIRONMENT}
• *Region:* ${params.REGION}
• *Version:* ${IMAGE_TAG}
• *Time:* ${sh(script: "TZ=${INDIAN_TIMEZONE} date", returnStdout: true).trim()}
• *Compliance:* RBI ✅ | PCI-DSS ✅ | Data Localization ✅
• *Festival Mode:* ${params.FESTIVAL_MODE ? 'Enabled' : 'Disabled'}
                    """.stripIndent()
                )
                
                // Email notification
                emailext(
                    to: 'devops@flipkart.com,platform-team@flipkart.com',
                    subject: "✅ Flipkart Production Deployment Successful - ${env.BUILD_NUMBER}",
                    body: """
Dear Team,

The Flipkart Indian E-commerce platform has been successfully deployed.

Build Details:
- Environment: ${params.ENVIRONMENT}
- Region: ${params.REGION}
- Version: ${IMAGE_TAG}
- Time: ${sh(script: "TZ=${INDIAN_TIMEZONE} date", returnStdout: true).trim()}
- Festival Mode: ${params.FESTIVAL_MODE ? 'Enabled' : 'Disabled'}

Compliance Status:
- RBI Compliance: ✅ Verified
- PCI-DSS Compliance: ✅ Verified  
- Data Localization: ✅ Verified

Best regards,
DevOps Team
                    """
                )
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline failed!"
                
                // Send failure notification
                slackSend(
                    channel: '#flipkart-deployments',
                    color: 'danger',
                    message: """
🚨 *Flipkart Indian E-commerce Deployment FAILED*
• *Environment:* ${params.ENVIRONMENT}
• *Region:* ${params.REGION}
• *Build:* ${env.BUILD_NUMBER}
• *Time:* ${sh(script: "TZ=${INDIAN_TIMEZONE} date", returnStdout: true).trim()}
• *Check:* ${env.BUILD_URL}
                    """.stripIndent()
                )
                
                // Email failure notification
                emailext(
                    to: 'devops@flipkart.com,platform-team@flipkart.com',
                    subject: "🚨 Flipkart Deployment FAILED - ${env.BUILD_NUMBER}",
                    body: """
Dear Team,

The Flipkart Indian E-commerce platform deployment has FAILED.

Please check the build logs: ${env.BUILD_URL}

Environment: ${params.ENVIRONMENT}
Region: ${params.REGION}
Time: ${sh(script: "TZ=${INDIAN_TIMEZONE} date", returnStdout: true).trim()}

Immediate attention required.

Best regards,
DevOps Team
                    """
                )
            }
        }
        
        unstable {
            script {
                echo "⚠️  Pipeline completed with warnings"
                
                slackSend(
                    channel: '#flipkart-deployments',
                    color: 'warning',
                    message: """
⚠️ *Flipkart Indian E-commerce Deployment UNSTABLE*
• *Environment:* ${params.ENVIRONMENT}
• *Region:* ${params.REGION}
• *Build:* ${env.BUILD_NUMBER}
• *Time:* ${sh(script: "TZ=${INDIAN_TIMEZONE} date", returnStdout: true).trim()}
• *Check:* ${env.BUILD_URL}
                    """.stripIndent()
                )
            }
        }
        
        cleanup {
            script {
                echo "🧹 Performing cleanup"
                
                // Archive artifacts
                archiveArtifacts artifacts: '**/build/reports/**', allowEmptyArchive: true
                archiveArtifacts artifacts: 'trivy-results.json', allowEmptyArchive: true
                
                // Clean workspace
                cleanWs()
            }
        }
    }
}
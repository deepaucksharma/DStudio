package com.flipkart.container.security;

/**
 * Flipkart Container Security Scanner
 * Episode 17: Container Orchestration
 * 
 * यह example दिखाता है कि कैसे Flipkart जैसी companies
 * production में container security scanning करती हैं।
 * 
 * Real-world scenario: Flipkart का comprehensive container security
 */

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

/**
 * Container Security Vulnerability
 */
class SecurityVulnerability {
    private String cveId;
    private String severity;
    private String description;
    private String packageName;
    private String installedVersion;
    private String fixedVersion;
    private Double cvssScore;
    private String category;
    private LocalDateTime discoveredAt;
    
    // Constructors
    public SecurityVulnerability() {}
    
    public SecurityVulnerability(String cveId, String severity, String description, 
                               String packageName, String installedVersion, 
                               String fixedVersion, Double cvssScore, String category) {
        this.cveId = cveId;
        this.severity = severity;
        this.description = description;
        this.packageName = packageName;
        this.installedVersion = installedVersion;
        this.fixedVersion = fixedVersion;
        this.cvssScore = cvssScore;
        this.category = category;
        this.discoveredAt = LocalDateTime.now();
    }
    
    // Getters and Setters
    public String getCveId() { return cveId; }
    public void setCveId(String cveId) { this.cveId = cveId; }
    
    public String getSeverity() { return severity; }
    public void setSeverity(String severity) { this.severity = severity; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public String getPackageName() { return packageName; }
    public void setPackageName(String packageName) { this.packageName = packageName; }
    
    public String getInstalledVersion() { return installedVersion; }
    public void setInstalledVersion(String installedVersion) { this.installedVersion = installedVersion; }
    
    public String getFixedVersion() { return fixedVersion; }
    public void setFixedVersion(String fixedVersion) { this.fixedVersion = fixedVersion; }
    
    public Double getCvssScore() { return cvssScore; }
    public void setCvssScore(Double cvssScore) { this.cvssScore = cvssScore; }
    
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    
    public LocalDateTime getDiscoveredAt() { return discoveredAt; }
    public void setDiscoveredAt(LocalDateTime discoveredAt) { this.discoveredAt = discoveredAt; }
}

/**
 * Container Scan Result
 */
class ContainerScanResult {
    private String scanId;
    private String imageName;
    private String imageTag;
    private String registry;
    private String environment;
    private String region;
    private LocalDateTime scanTime;
    private String scanStatus;
    private List<SecurityVulnerability> vulnerabilities;
    private Map<String, Integer> vulnerabilityCount;
    private Double riskScore;
    private Boolean deploymentAllowed;
    private String complianceStatus;
    private List<String> recommendations;
    
    // Constructors
    public ContainerScanResult() {
        this.vulnerabilities = new ArrayList<>();
        this.vulnerabilityCount = new HashMap<>();
        this.recommendations = new ArrayList<>();
    }
    
    public ContainerScanResult(String imageName, String imageTag, String environment, String region) {
        this();
        this.scanId = generateScanId();
        this.imageName = imageName;
        this.imageTag = imageTag;
        this.environment = environment;
        this.region = region;
        this.scanTime = LocalDateTime.now();
        this.scanStatus = "IN_PROGRESS";
    }
    
    private String generateScanId() {
        return "SCAN-" + System.currentTimeMillis() + "-" + 
               String.format("%04d", new Random().nextInt(10000));
    }
    
    // Getters and Setters
    public String getScanId() { return scanId; }
    public void setScanId(String scanId) { this.scanId = scanId; }
    
    public String getImageName() { return imageName; }
    public void setImageName(String imageName) { this.imageName = imageName; }
    
    public String getImageTag() { return imageTag; }
    public void setImageTag(String imageTag) { this.imageTag = imageTag; }
    
    public String getRegistry() { return registry; }
    public void setRegistry(String registry) { this.registry = registry; }
    
    public String getEnvironment() { return environment; }
    public void setEnvironment(String environment) { this.environment = environment; }
    
    public String getRegion() { return region; }
    public void setRegion(String region) { this.region = region; }
    
    public LocalDateTime getScanTime() { return scanTime; }
    public void setScanTime(LocalDateTime scanTime) { this.scanTime = scanTime; }
    
    public String getScanStatus() { return scanStatus; }
    public void setScanStatus(String scanStatus) { this.scanStatus = scanStatus; }
    
    public List<SecurityVulnerability> getVulnerabilities() { return vulnerabilities; }
    public void setVulnerabilities(List<SecurityVulnerability> vulnerabilities) { this.vulnerabilities = vulnerabilities; }
    
    public Map<String, Integer> getVulnerabilityCount() { return vulnerabilityCount; }
    public void setVulnerabilityCount(Map<String, Integer> vulnerabilityCount) { this.vulnerabilityCount = vulnerabilityCount; }
    
    public Double getRiskScore() { return riskScore; }
    public void setRiskScore(Double riskScore) { this.riskScore = riskScore; }
    
    public Boolean getDeploymentAllowed() { return deploymentAllowed; }
    public void setDeploymentAllowed(Boolean deploymentAllowed) { this.deploymentAllowed = deploymentAllowed; }
    
    public String getComplianceStatus() { return complianceStatus; }
    public void setComplianceStatus(String complianceStatus) { this.complianceStatus = complianceStatus; }
    
    public List<String> getRecommendations() { return recommendations; }
    public void setRecommendations(List<String> recommendations) { this.recommendations = recommendations; }
}

/**
 * Security Policy Configuration
 */
class SecurityPolicy {
    private String policyName;
    private String environment;
    private Map<String, Integer> maxVulnerabilities;
    private Double maxRiskScore;
    private List<String> blockedPackages;
    private List<String> requiredSecurityHeaders;
    private Boolean requireSignedImages;
    private Boolean blockRootUser;
    
    public SecurityPolicy() {
        this.maxVulnerabilities = new HashMap<>();
        this.blockedPackages = new ArrayList<>();
        this.requiredSecurityHeaders = new ArrayList<>();
    }
    
    // Getters and Setters
    public String getPolicyName() { return policyName; }
    public void setPolicyName(String policyName) { this.policyName = policyName; }
    
    public String getEnvironment() { return environment; }
    public void setEnvironment(String environment) { this.environment = environment; }
    
    public Map<String, Integer> getMaxVulnerabilities() { return maxVulnerabilities; }
    public void setMaxVulnerabilities(Map<String, Integer> maxVulnerabilities) { this.maxVulnerabilities = maxVulnerabilities; }
    
    public Double getMaxRiskScore() { return maxRiskScore; }
    public void setMaxRiskScore(Double maxRiskScore) { this.maxRiskScore = maxRiskScore; }
    
    public List<String> getBlockedPackages() { return blockedPackages; }
    public void setBlockedPackages(List<String> blockedPackages) { this.blockedPackages = blockedPackages; }
    
    public List<String> getRequiredSecurityHeaders() { return requiredSecurityHeaders; }
    public void setRequiredSecurityHeaders(List<String> requiredSecurityHeaders) { this.requiredSecurityHeaders = requiredSecurityHeaders; }
    
    public Boolean getRequireSignedImages() { return requireSignedImages; }
    public void setRequireSignedImages(Boolean requireSignedImages) { this.requireSignedImages = requireSignedImages; }
    
    public Boolean getBlockRootUser() { return blockRootUser; }
    public void setBlockRootUser(Boolean blockRootUser) { this.blockRootUser = blockRootUser; }
}

/**
 * Flipkart Container Security Scanner
 * Production-ready security scanning with Indian compliance requirements
 */
@SpringBootApplication
public class FlipkartContainerSecurityScanner {
    
    private static final Logger logger = LoggerFactory.getLogger(FlipkartContainerSecurityScanner.class);
    
    // Thread pool for concurrent scanning
    private final ExecutorService scanExecutor = Executors.newFixedThreadPool(10);
    
    // Scan results storage (in production, this would be a database)
    private final Map<String, ContainerScanResult> scanResults = new ConcurrentHashMap<>();
    
    // Security policies for different environments
    private final Map<String, SecurityPolicy> securityPolicies = new HashMap<>();
    
    // Indian compliance requirements
    private final List<String> indianComplianceRequirements = Arrays.asList(
        "RBI_GUIDELINES", "IT_ACT_2000", "GDPR_COMPLIANCE", 
        "ISO_27001", "SOC2_TYPE2", "PCI_DSS"
    );
    
    public FlipkartContainerSecurityScanner() {
        initializeSecurityPolicies();
        logger.info("🛡️ Flipkart Container Security Scanner initialized!");
        logger.info("Production-ready security scanning banane ke liye ready!");
    }
    
    /**
     * Initialize security policies for different environments
     */
    private void initializeSecurityPolicies() {
        // Development environment policy (lenient)
        SecurityPolicy devPolicy = new SecurityPolicy();
        devPolicy.setPolicyName("FLIPKART_DEV_POLICY");
        devPolicy.setEnvironment("development");
        devPolicy.getMaxVulnerabilities().put("CRITICAL", 5);
        devPolicy.getMaxVulnerabilities().put("HIGH", 20);
        devPolicy.getMaxVulnerabilities().put("MEDIUM", 50);
        devPolicy.setMaxRiskScore(7.0);
        devPolicy.setRequireSignedImages(false);
        devPolicy.setBlockRootUser(false);
        
        // Staging environment policy (moderate)
        SecurityPolicy stagingPolicy = new SecurityPolicy();
        stagingPolicy.setPolicyName("FLIPKART_STAGING_POLICY");
        stagingPolicy.setEnvironment("staging");
        stagingPolicy.getMaxVulnerabilities().put("CRITICAL", 2);
        stagingPolicy.getMaxVulnerabilities().put("HIGH", 10);
        stagingPolicy.getMaxVulnerabilities().put("MEDIUM", 25);
        stagingPolicy.setMaxRiskScore(5.0);
        stagingPolicy.setRequireSignedImages(true);
        stagingPolicy.setBlockRootUser(true);
        
        // Production environment policy (strict)
        SecurityPolicy prodPolicy = new SecurityPolicy();
        prodPolicy.setPolicyName("FLIPKART_PROD_POLICY");
        prodPolicy.setEnvironment("production");
        prodPolicy.getMaxVulnerabilities().put("CRITICAL", 0);
        prodPolicy.getMaxVulnerabilities().put("HIGH", 0);
        prodPolicy.getMaxVulnerabilities().put("MEDIUM", 5);
        prodPolicy.setMaxRiskScore(3.0);
        prodPolicy.setRequireSignedImages(true);
        prodPolicy.setBlockRootUser(true);
        
        // Blocked packages for production
        prodPolicy.getBlockedPackages().addAll(Arrays.asList(
            "telnet", "ftp", "rsh", "wget", "curl"  // Security risk packages
        ));
        
        // Required security headers
        prodPolicy.getRequiredSecurityHeaders().addAll(Arrays.asList(
            "X-Content-Type-Options", "X-Frame-Options", 
            "X-XSS-Protection", "Strict-Transport-Security"
        ));
        
        securityPolicies.put("development", devPolicy);
        securityPolicies.put("staging", stagingPolicy);
        securityPolicies.put("production", prodPolicy);
        
        logger.info("🔒 Security policies initialized for all environments");
    }
    
    /**
     * Scan container image for security vulnerabilities
     */
    @PostMapping("/api/v1/scan")
    public ResponseEntity<Map<String, Object>> scanContainer(@RequestBody Map<String, String> request) {
        String imageName = request.get("image_name");
        String imageTag = request.get("image_tag");
        String environment = request.getOrDefault("environment", "development");
        String region = request.getOrDefault("region", "mumbai");
        
        logger.info("🔍 Starting security scan for {}:{} in {} environment", 
                   imageName, imageTag, environment);
        
        // Create scan result
        ContainerScanResult scanResult = new ContainerScanResult(imageName, imageTag, environment, region);
        scanResults.put(scanResult.getScanId(), scanResult);
        
        // Start async scanning
        CompletableFuture<Void> scanFuture = CompletableFuture.runAsync(() -> {
            performSecurityScan(scanResult);
        }, scanExecutor);
        
        Map<String, Object> response = new HashMap<>();
        response.put("scan_id", scanResult.getScanId());
        response.put("status", "INITIATED");
        response.put("message", "Security scan started successfully");
        response.put("estimated_completion", LocalDateTime.now().plusMinutes(5));
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * Get scan result by scan ID
     */
    @GetMapping("/api/v1/scan/{scanId}")
    public ResponseEntity<ContainerScanResult> getScanResult(@PathVariable String scanId) {
        ContainerScanResult result = scanResults.get(scanId);
        
        if (result == null) {
            return ResponseEntity.notFound().build();
        }
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Get security dashboard data
     */
    @GetMapping("/api/v1/dashboard")
    public ResponseEntity<Map<String, Object>> getSecurityDashboard() {
        Map<String, Object> dashboard = new HashMap<>();
        
        // Calculate statistics
        long totalScans = scanResults.size();
        long completedScans = scanResults.values().stream()
            .mapToLong(r -> "COMPLETED".equals(r.getScanStatus()) ? 1 : 0)
            .sum();
        
        long failedScans = scanResults.values().stream()
            .mapToLong(r -> "DEPLOYMENT_BLOCKED".equals(r.getComplianceStatus()) ? 1 : 0)
            .sum();
        
        // Vulnerability statistics
        Map<String, Long> vulnerabilityStats = scanResults.values().stream()
            .filter(r -> "COMPLETED".equals(r.getScanStatus()))
            .flatMap(r -> r.getVulnerabilities().stream())
            .collect(Collectors.groupingBy(
                SecurityVulnerability::getSeverity,
                Collectors.counting()
            ));
        
        // Regional statistics (Indian cities)
        Map<String, Long> regionalStats = scanResults.values().stream()
            .collect(Collectors.groupingBy(
                ContainerScanResult::getRegion,
                Collectors.counting()
            ));
        
        dashboard.put("total_scans", totalScans);
        dashboard.put("completed_scans", completedScans);
        dashboard.put("failed_scans", failedScans);
        dashboard.put("success_rate", totalScans > 0 ? (double)(completedScans - failedScans) / totalScans * 100 : 0);
        dashboard.put("vulnerability_stats", vulnerabilityStats);
        dashboard.put("regional_stats", regionalStats);
        dashboard.put("compliance_requirements", indianComplianceRequirements);
        dashboard.put("last_updated", LocalDateTime.now());
        
        return ResponseEntity.ok(dashboard);
    }
    
    /**
     * Perform comprehensive security scan
     */
    private void performSecurityScan(ContainerScanResult scanResult) {
        try {
            logger.info("🔍 Performing security scan: {}", scanResult.getScanId());
            
            // Step 1: Image vulnerability scanning
            scanResult.setScanStatus("SCANNING_VULNERABILITIES");
            List<SecurityVulnerability> vulnerabilities = scanImageVulnerabilities(
                scanResult.getImageName(), scanResult.getImageTag()
            );
            scanResult.setVulnerabilities(vulnerabilities);
            
            // Step 2: Calculate vulnerability counts
            Map<String, Integer> vulnCounts = calculateVulnerabilityCounts(vulnerabilities);
            scanResult.setVulnerabilityCount(vulnCounts);
            
            // Step 3: Calculate risk score
            Double riskScore = calculateRiskScore(vulnerabilities);
            scanResult.setRiskScore(riskScore);
            
            // Step 4: Policy compliance check
            scanResult.setScanStatus("CHECKING_COMPLIANCE");
            boolean isCompliant = checkPolicyCompliance(scanResult);
            scanResult.setDeploymentAllowed(isCompliant);
            scanResult.setComplianceStatus(isCompliant ? "COMPLIANT" : "DEPLOYMENT_BLOCKED");
            
            // Step 5: Generate recommendations
            List<String> recommendations = generateSecurityRecommendations(scanResult);
            scanResult.setRecommendations(recommendations);
            
            // Step 6: Complete scan
            scanResult.setScanStatus("COMPLETED");
            
            logger.info("✅ Security scan completed: {} (Risk Score: {}, Compliant: {})", 
                       scanResult.getScanId(), riskScore, isCompliant);
            
        } catch (Exception e) {
            logger.error("❌ Security scan failed: {}", scanResult.getScanId(), e);
            scanResult.setScanStatus("FAILED");
            scanResult.setComplianceStatus("SCAN_FAILED");
        }
    }
    
    /**
     * Scan image for vulnerabilities (simulated for demo)
     */
    private List<SecurityVulnerability> scanImageVulnerabilities(String imageName, String imageTag) {
        logger.info("🔍 Scanning vulnerabilities in {}:{}", imageName, imageTag);
        
        // Simulate vulnerability scanning (in production, integrate with Trivy, Clair, etc.)
        List<SecurityVulnerability> vulnerabilities = new ArrayList<>();
        
        // Generate realistic vulnerabilities based on image type
        if (imageName.contains("nginx")) {
            vulnerabilities.addAll(generateNginxVulnerabilities());
        } else if (imageName.contains("node")) {
            vulnerabilities.addAll(generateNodeVulnerabilities());
        } else if (imageName.contains("python")) {
            vulnerabilities.addAll(generatePythonVulnerabilities());
        } else if (imageName.contains("mysql")) {
            vulnerabilities.addAll(generateMySQLVulnerabilities());
        }
        
        // Add some common OS vulnerabilities
        vulnerabilities.addAll(generateOSVulnerabilities());
        
        // Simulate scan time
        try {
            Thread.sleep(3000); // 3 seconds scan time
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        logger.info("🔍 Found {} vulnerabilities", vulnerabilities.size());
        return vulnerabilities;
    }
    
    /**
     * Generate realistic nginx vulnerabilities
     */
    private List<SecurityVulnerability> generateNginxVulnerabilities() {
        return Arrays.asList(
            new SecurityVulnerability(
                "CVE-2021-23017", "HIGH", 
                "Off-by-one in Nginx resolver", 
                "nginx", "1.18.0", "1.20.1", 
                8.1, "DENIAL_OF_SERVICE"
            ),
            new SecurityVulnerability(
                "CVE-2019-20372", "MEDIUM",
                "Buffer overflow in nginx module",
                "nginx", "1.18.0", "1.19.0",
                6.5, "BUFFER_OVERFLOW"
            )
        );
    }
    
    /**
     * Generate realistic Node.js vulnerabilities
     */
    private List<SecurityVulnerability> generateNodeVulnerabilities() {
        return Arrays.asList(
            new SecurityVulnerability(
                "CVE-2022-32212", "HIGH",
                "DNS rebinding in Node.js inspector",
                "nodejs", "16.14.0", "16.15.1",
                7.5, "CODE_INJECTION"
            ),
            new SecurityVulnerability(
                "CVE-2022-32215", "MEDIUM",
                "HTTP request smuggling via malformed headers",
                "nodejs", "16.14.0", "16.17.0",
                6.5, "HTTP_SMUGGLING"
            )
        );
    }
    
    /**
     * Generate realistic Python vulnerabilities
     */
    private List<SecurityVulnerability> generatePythonVulnerabilities() {
        return Arrays.asList(
            new SecurityVulnerability(
                "CVE-2022-45061", "MEDIUM",
                "CPU denial of service via inefficient IDNA decoder",
                "python", "3.9.0", "3.9.16",
                5.9, "DENIAL_OF_SERVICE"
            ),
            new SecurityVulnerability(
                "CVE-2022-37454", "HIGH",
                "Buffer overflow in hashlib",
                "python", "3.9.0", "3.9.15",
                8.1, "BUFFER_OVERFLOW"
            )
        );
    }
    
    /**
     * Generate realistic MySQL vulnerabilities
     */
    private List<SecurityVulnerability> generateMySQLVulnerabilities() {
        return Arrays.asList(
            new SecurityVulnerability(
                "CVE-2022-21594", "HIGH",
                "Privilege escalation in MySQL server",
                "mysql", "8.0.30", "8.0.31",
                8.8, "PRIVILEGE_ESCALATION"
            ),
            new SecurityVulnerability(
                "CVE-2022-21589", "MEDIUM",
                "Information disclosure in MySQL",
                "mysql", "8.0.30", "8.0.31",
                6.5, "INFORMATION_DISCLOSURE"
            )
        );
    }
    
    /**
     * Generate OS-level vulnerabilities
     */
    private List<SecurityVulnerability> generateOSVulnerabilities() {
        return Arrays.asList(
            new SecurityVulnerability(
                "CVE-2022-2586", "CRITICAL",
                "Use-after-free in Linux kernel",
                "linux-kernel", "5.4.0", "5.4.210",
                9.8, "MEMORY_CORRUPTION"
            ),
            new SecurityVulnerability(
                "CVE-2022-32250", "HIGH",
                "Use-after-free in Netfilter",
                "netfilter", "5.4.0", "5.18.2",
                7.8, "PRIVILEGE_ESCALATION"
            )
        );
    }
    
    /**
     * Calculate vulnerability counts by severity
     */
    private Map<String, Integer> calculateVulnerabilityCounts(List<SecurityVulnerability> vulnerabilities) {
        return vulnerabilities.stream()
            .collect(Collectors.groupingBy(
                SecurityVulnerability::getSeverity,
                Collectors.collectingAndThen(Collectors.counting(), Math::toIntExact)
            ));
    }
    
    /**
     * Calculate overall risk score
     */
    private Double calculateRiskScore(List<SecurityVulnerability> vulnerabilities) {
        if (vulnerabilities.isEmpty()) {
            return 0.0;
        }
        
        double totalScore = vulnerabilities.stream()
            .mapToDouble(v -> v.getCvssScore() != null ? v.getCvssScore() : 0.0)
            .sum();
        
        double averageScore = totalScore / vulnerabilities.size();
        
        // Adjust score based on vulnerability count and severity distribution
        long criticalCount = vulnerabilities.stream()
            .mapToLong(v -> "CRITICAL".equals(v.getSeverity()) ? 1 : 0)
            .sum();
        
        long highCount = vulnerabilities.stream()
            .mapToLong(v -> "HIGH".equals(v.getSeverity()) ? 1 : 0)
            .sum();
        
        // Penalty for multiple high-severity vulnerabilities
        double severityPenalty = (criticalCount * 2.0) + (highCount * 1.0);
        
        return Math.min(10.0, averageScore + (severityPenalty * 0.1));
    }
    
    /**
     * Check policy compliance
     */
    private boolean checkPolicyCompliance(ContainerScanResult scanResult) {
        SecurityPolicy policy = securityPolicies.get(scanResult.getEnvironment());
        
        if (policy == null) {
            logger.warn("No security policy found for environment: {}", scanResult.getEnvironment());
            return false;
        }
        
        // Check vulnerability limits
        Map<String, Integer> vulnCounts = scanResult.getVulnerabilityCount();
        for (Map.Entry<String, Integer> limit : policy.getMaxVulnerabilities().entrySet()) {
            String severity = limit.getKey();
            Integer maxAllowed = limit.getValue();
            Integer actualCount = vulnCounts.getOrDefault(severity, 0);
            
            if (actualCount > maxAllowed) {
                logger.warn("Policy violation: {} {} vulnerabilities found, max allowed: {}", 
                           actualCount, severity, maxAllowed);
                return false;
            }
        }
        
        // Check risk score
        if (scanResult.getRiskScore() > policy.getMaxRiskScore()) {
            logger.warn("Policy violation: Risk score {} exceeds limit {}", 
                       scanResult.getRiskScore(), policy.getMaxRiskScore());
            return false;
        }
        
        // Check blocked packages
        for (SecurityVulnerability vuln : scanResult.getVulnerabilities()) {
            if (policy.getBlockedPackages().contains(vuln.getPackageName())) {
                logger.warn("Policy violation: Blocked package found: {}", vuln.getPackageName());
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Generate security recommendations
     */
    private List<String> generateSecurityRecommendations(ContainerScanResult scanResult) {
        List<String> recommendations = new ArrayList<>();
        
        // Critical vulnerabilities
        long criticalCount = scanResult.getVulnerabilities().stream()
            .mapToLong(v -> "CRITICAL".equals(v.getSeverity()) ? 1 : 0)
            .sum();
        
        if (criticalCount > 0) {
            recommendations.add(String.format(
                "🚨 URGENT: Fix %d critical vulnerabilities immediately before deployment", 
                criticalCount
            ));
        }
        
        // High vulnerabilities
        long highCount = scanResult.getVulnerabilities().stream()
            .mapToLong(v -> "HIGH".equals(v.getSeverity()) ? 1 : 0)
            .sum();
        
        if (highCount > 0) {
            recommendations.add(String.format(
                "⚠️ Address %d high-severity vulnerabilities within 24 hours", 
                highCount
            ));
        }
        
        // Risk score recommendations
        if (scanResult.getRiskScore() > 7.0) {
            recommendations.add("📊 Risk score is high. Consider using a minimal base image");
        }
        
        // Package-specific recommendations
        Set<String> vulnerablePackages = scanResult.getVulnerabilities().stream()
            .map(SecurityVulnerability::getPackageName)
            .collect(Collectors.toSet());
        
        if (vulnerablePackages.contains("nginx")) {
            recommendations.add("🔄 Update nginx to the latest stable version");
        }
        
        if (vulnerablePackages.contains("nodejs")) {
            recommendations.add("🔄 Update Node.js runtime and npm packages");
        }
        
        // Indian compliance recommendations
        if ("production".equals(scanResult.getEnvironment())) {
            recommendations.add("🇮🇳 Ensure compliance with RBI guidelines for financial data");
            recommendations.add("🔒 Implement encryption for data at rest (IT Act 2000 compliance)");
            recommendations.add("📋 Document security measures for audit (ISO 27001 requirement)");
        }
        
        // General security hardening
        recommendations.add("🛡️ Use distroless or minimal base images");
        recommendations.add("🔐 Implement image signing and verification");
        recommendations.add("📦 Regular security scanning in CI/CD pipeline");
        
        return recommendations;
    }
    
    public static void main(String[] args) {
        System.out.println("🛡️ Flipkart Container Security Scanner");
        System.out.println("Production-ready security scanning for Indian e-commerce");
        System.out.println("=" * 70);
        
        SpringApplication.run(FlipkartContainerSecurityScanner.class, args);
        
        System.out.println("🌐 Security Scanner API started on port 8080");
        System.out.println("📍 Endpoints:");
        System.out.println("   - POST /api/v1/scan - Start security scan");
        System.out.println("   - GET /api/v1/scan/{scanId} - Get scan result");
        System.out.println("   - GET /api/v1/dashboard - Security dashboard");
        System.out.println("🔒 Indian compliance: RBI, IT Act 2000, GDPR ready!");
    }
}

/*
Production Usage Examples:

# Start security scan:
curl -X POST http://localhost:8080/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{
    "image_name": "flipkart/product-service",
    "image_tag": "v2.1.0",
    "environment": "production",
    "region": "mumbai"
  }'

# Get scan result:
curl http://localhost:8080/api/v1/scan/SCAN-1234567890-1234

# Security dashboard:
curl http://localhost:8080/api/v1/dashboard

# Integration with CI/CD:
# GitLab CI/CD pipeline would call these APIs
# Jenkins pipeline security gate
# Kubernetes admission controllers

# Maven dependencies (add to pom.xml):
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <version>3.2.0</version>
    </dependency>
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
        <version>2.15.2</version>
    </dependency>
    <dependency>
        <groupId>org.slf4j</groupId>
        <artifactId>slf4j-api</artifactId>
        <version>2.0.7</version>
    </dependency>
</dependencies>

# Docker build:
mvn clean package
docker build -t flipkart/security-scanner:latest .

# Kubernetes deployment:
kubectl apply -f flipkart-security-scanner-deployment.yaml
*/
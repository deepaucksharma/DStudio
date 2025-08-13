/**
 * Data Governance Framework
 * डेटा गवर्नेंस फ्रेमवर्क
 * 
 * Real-world example: Reliance Jio's data governance system
 * Comprehensive data governance with Indian regulatory compliance
 */

package com.jio.governance;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.stream.Collectors;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;

/**
 * Data Classification Levels
 */
enum DataClassification {
    PUBLIC("public", 1),
    INTERNAL("internal", 2), 
    CONFIDENTIAL("confidential", 3),
    RESTRICTED("restricted", 4),
    PII("pii", 5),
    FINANCIAL("financial", 5),
    TELECOM("telecom", 4);  // Specific to telecom sector
    
    private final String label;
    private final int riskLevel;
    
    DataClassification(String label, int riskLevel) {
        this.label = label;
        this.riskLevel = riskLevel;
    }
    
    public String getLabel() { return label; }
    public int getRiskLevel() { return riskLevel; }
}

/**
 * Indian Data Regulations
 */
enum IndianRegulation {
    DPDP_ACT("Digital Personal Data Protection Act 2023", "IN"),
    IT_ACT("Information Technology Act 2000", "IN"),
    TRAI_REGULATIONS("TRAI Telecom Regulations", "IN"),
    RBI_GUIDELINES("RBI Data Localization Guidelines", "IN"),
    SEBI_REGULATIONS("SEBI Data Protection Regulations", "IN"),
    CERT_IN_GUIDELINES("CERT-In Cybersecurity Guidelines", "IN");
    
    private final String fullName;
    private final String jurisdiction;
    
    IndianRegulation(String fullName, String jurisdiction) {
        this.fullName = fullName;
        this.jurisdiction = jurisdiction;
    }
    
    public String getFullName() { return fullName; }
    public String getJurisdiction() { return jurisdiction; }
}

/**
 * Data Governance Policy
 */
class GovernancePolicy {
    private final String policyId;
    private final String policyName;
    private final DataClassification applicableClassification;
    private final IndianRegulation regulation;
    private final Map<String, String> rules;
    private final LocalDateTime effectiveDate;
    private final LocalDateTime expiryDate;
    private final boolean mandatory;
    
    public GovernancePolicy(String policyId, String policyName, 
                           DataClassification classification, IndianRegulation regulation,
                           Map<String, String> rules, LocalDateTime effectiveDate,
                           LocalDateTime expiryDate, boolean mandatory) {
        this.policyId = policyId;
        this.policyName = policyName;
        this.applicableClassification = classification;
        this.regulation = regulation;
        this.rules = new HashMap<>(rules);
        this.effectiveDate = effectiveDate;
        this.expiryDate = expiryDate;
        this.mandatory = mandatory;
    }
    
    // Getters
    public String getPolicyId() { return policyId; }
    public String getPolicyName() { return policyName; }
    public DataClassification getApplicableClassification() { return applicableClassification; }
    public IndianRegulation getRegulation() { return regulation; }
    public Map<String, String> getRules() { return new HashMap<>(rules); }
    public LocalDateTime getEffectiveDate() { return effectiveDate; }
    public LocalDateTime getExpiryDate() { return expiryDate; }
    public boolean isMandatory() { return mandatory; }
    
    public boolean isActive() {
        LocalDateTime now = LocalDateTime.now();
        return now.isAfter(effectiveDate) && (expiryDate == null || now.isBefore(expiryDate));
    }
}

/**
 * Data Asset representation
 */
class DataAsset {
    private final String assetId;
    private final String assetName;
    private final DataClassification classification;
    private final String dataOwner;
    private final String businessPurpose;
    private final Set<String> authorizedUsers;
    private final Map<String, String> metadata;
    private final LocalDateTime createdAt;
    private LocalDateTime lastAccessed;
    private final String storageLocation;
    private boolean encrypted;
    
    public DataAsset(String assetId, String assetName, DataClassification classification,
                    String dataOwner, String businessPurpose, Set<String> authorizedUsers,
                    String storageLocation) {
        this.assetId = assetId;
        this.assetName = assetName;
        this.classification = classification;
        this.dataOwner = dataOwner;
        this.businessPurpose = businessPurpose;
        this.authorizedUsers = new HashSet<>(authorizedUsers);
        this.metadata = new HashMap<>();
        this.createdAt = LocalDateTime.now();
        this.lastAccessed = LocalDateTime.now();
        this.storageLocation = storageLocation;
        this.encrypted = false;
    }
    
    // Getters and setters
    public String getAssetId() { return assetId; }
    public String getAssetName() { return assetName; }
    public DataClassification getClassification() { return classification; }
    public String getDataOwner() { return dataOwner; }
    public String getBusinessPurpose() { return businessPurpose; }
    public Set<String> getAuthorizedUsers() { return new HashSet<>(authorizedUsers); }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getLastAccessed() { return lastAccessed; }
    public String getStorageLocation() { return storageLocation; }
    public boolean isEncrypted() { return encrypted; }
    
    public void setLastAccessed(LocalDateTime lastAccessed) { this.lastAccessed = lastAccessed; }
    public void setEncrypted(boolean encrypted) { this.encrypted = encrypted; }
    
    public void addMetadata(String key, String value) {
        this.metadata.put(key, value);
    }
    
    public Map<String, String> getMetadata() {
        return new HashMap<>(metadata);
    }
}

/**
 * Data Access Request
 */
class DataAccessRequest {
    private final String requestId;
    private final String requesterUserId;
    private final String assetId;
    private final String accessPurpose;
    private final LocalDateTime requestTime;
    private final LocalDateTime requestedUntil;
    private String approverUserId;
    private String status; // pending, approved, rejected, expired
    private String rejectionReason;
    private LocalDateTime approvedAt;
    
    public DataAccessRequest(String requestId, String requesterUserId, String assetId,
                           String accessPurpose, LocalDateTime requestedUntil) {
        this.requestId = requestId;
        this.requesterUserId = requesterUserId;
        this.assetId = assetId;
        this.accessPurpose = accessPurpose;
        this.requestTime = LocalDateTime.now();
        this.requestedUntil = requestedUntil;
        this.status = "pending";
    }
    
    // Getters and setters
    public String getRequestId() { return requestId; }
    public String getRequesterUserId() { return requesterUserId; }
    public String getAssetId() { return assetId; }
    public String getAccessPurpose() { return accessPurpose; }
    public LocalDateTime getRequestTime() { return requestTime; }
    public LocalDateTime getRequestedUntil() { return requestedUntil; }
    public String getApproverUserId() { return approverUserId; }
    public String getStatus() { return status; }
    public String getRejectionReason() { return rejectionReason; }
    public LocalDateTime getApprovedAt() { return approvedAt; }
    
    public void setApproverUserId(String approverUserId) { this.approverUserId = approverUserId; }
    public void setStatus(String status) { this.status = status; }
    public void setRejectionReason(String rejectionReason) { this.rejectionReason = rejectionReason; }
    public void setApprovedAt(LocalDateTime approvedAt) { this.approvedAt = approvedAt; }
}

/**
 * Compliance Audit Log Entry
 */
class AuditLogEntry {
    private final String logId;
    private final String userId;
    private final String action;
    private final String assetId;
    private final LocalDateTime timestamp;
    private final String ipAddress;
    private final boolean successful;
    private final String details;
    
    public AuditLogEntry(String logId, String userId, String action, String assetId,
                        String ipAddress, boolean successful, String details) {
        this.logId = logId;
        this.userId = userId;
        this.action = action;
        this.assetId = assetId;
        this.timestamp = LocalDateTime.now();
        this.ipAddress = ipAddress;
        this.successful = successful;
        this.details = details;
    }
    
    // Getters
    public String getLogId() { return logId; }
    public String getUserId() { return userId; }
    public String getAction() { return action; }
    public String getAssetId() { return assetId; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public String getIpAddress() { return ipAddress; }
    public boolean isSuccessful() { return successful; }
    public String getDetails() { return details; }
}

/**
 * Jio Data Governance Framework
 * जियो डेटा गवर्नेंस फ्रेमवर्क
 */
public class DataGovernanceFramework {
    
    private final Map<String, GovernancePolicy> policies;
    private final Map<String, DataAsset> dataAssets;
    private final Map<String, DataAccessRequest> accessRequests;
    private final List<AuditLogEntry> auditLog;
    private final Set<String> dataStewrads;
    private final Map<String, Set<String>> userRoles;
    
    public DataGovernanceFramework() {
        this.policies = new ConcurrentHashMap<>();
        this.dataAssets = new ConcurrentHashMap<>();
        this.accessRequests = new ConcurrentHashMap<>();
        this.auditLog = Collections.synchronizedList(new ArrayList<>());
        this.dataStewrads = ConcurrentHashMap.newKeySet();
        this.userRoles = new ConcurrentHashMap<>();
        
        initializeDefaultPolicies();
        initializeDefaultRoles();
    }
    
    /**
     * Initialize default governance policies
     * डिफ़ॉल्ट गवर्नेंस नीतियां प्रारंभ करें
     */
    private void initializeDefaultPolicies() {
        System.out.println("🔧 Initializing Jio Data Governance policies...");
        
        // DPDP Act Policy for PII data
        Map<String, String> dpdpRules = new HashMap<>();
        dpdpRules.put("data_localization", "All personal data must be stored within India");
        dpdpRules.put("consent_required", "Explicit consent required for data processing");
        dpdpRules.put("retention_limit", "Data must be deleted when no longer needed");
        dpdpRules.put("data_minimization", "Collect only necessary personal data");
        
        GovernancePolicy dpdpPolicy = new GovernancePolicy(
            "DPDP_PII_001",
            "DPDP Act Compliance for Personal Data",
            DataClassification.PII,
            IndianRegulation.DPDP_ACT,
            dpdpRules,
            LocalDateTime.now().minusDays(30),
            null, // No expiry
            true
        );
        
        policies.put(dpdpPolicy.getPolicyId(), dpdpPolicy);
        
        // TRAI Policy for Telecom Data
        Map<String, String> traiRules = new HashMap<>();
        traiRules.put("call_data_retention", "Call detail records must be retained for 1 year");
        traiRules.put("location_data_consent", "Location tracking requires explicit consent");
        traiRules.put("do_not_disturb", "Respect DND preferences for marketing");
        traiRules.put("data_sharing", "Telecom data sharing requires regulatory approval");
        
        GovernancePolicy traiPolicy = new GovernancePolicy(
            "TRAI_TELECOM_001",
            "TRAI Compliance for Telecom Data",
            DataClassification.TELECOM,
            IndianRegulation.TRAI_REGULATIONS,
            traiRules,
            LocalDateTime.now().minusDays(60),
            null,
            true
        );
        
        policies.put(traiPolicy.getPolicyId(), traiPolicy);
        
        // RBI Policy for Financial Data
        Map<String, String> rbiRules = new HashMap<>();
        rbiRules.put("payment_data_localization", "Payment data must reside in India");
        rbiRules.put("financial_audit", "Regular financial data audits required");
        rbiRules.put("transaction_monitoring", "Monitor for suspicious transactions");
        
        GovernancePolicy rbiPolicy = new GovernancePolicy(
            "RBI_FINANCIAL_001",
            "RBI Compliance for Payment Data",
            DataClassification.FINANCIAL,
            IndianRegulation.RBI_GUIDELINES,
            rbiRules,
            LocalDateTime.now().minusDays(90),
            null,
            true
        );
        
        policies.put(rbiPolicy.getPolicyId(), rbiPolicy);
    }
    
    /**
     * Initialize default user roles
     * डिफ़ॉल्ट उपयोगकर्ता भूमिकाएं प्रारंभ करें
     */
    private void initializeDefaultRoles() {
        // Data Stewards
        dataStewrads.add("steward001");
        dataStewrads.add("steward002");
        
        // User roles
        userRoles.put("admin001", Set.of("data_admin", "policy_manager"));
        userRoles.put("steward001", Set.of("data_steward", "access_approver"));
        userRoles.put("analyst001", Set.of("data_analyst", "report_viewer"));
        userRoles.put("developer001", Set.of("application_developer", "data_consumer"));
    }
    
    /**
     * Register new data asset
     * नई डेटा संपत्ति पंजीकृत करें
     */
    public void registerDataAsset(DataAsset asset) {
        // Validate asset against policies
        List<String> violations = validateAssetCompliance(asset);
        
        if (!violations.isEmpty()) {
            System.out.println("⚠️ Asset registration has compliance violations:");
            violations.forEach(violation -> System.out.println("  - " + violation));
        }
        
        dataAssets.put(asset.getAssetId(), asset);
        
        // Apply automatic policy compliance
        applyAutomaticCompliance(asset);
        
        // Log registration
        auditLog.add(new AuditLogEntry(
            generateLogId(),
            "system",
            "ASSET_REGISTERED",
            asset.getAssetId(),
            "127.0.0.1",
            true,
            "Data asset registered: " + asset.getAssetName()
        ));
        
        System.out.println("📝 Registered data asset: " + asset.getAssetName() + 
                          " (Classification: " + asset.getClassification().getLabel() + ")");
    }
    
    /**
     * Validate asset compliance with policies
     * नीतियों के साथ संपत्ति अनुपालन को मान्य करें
     */
    private List<String> validateAssetCompliance(DataAsset asset) {
        List<String> violations = new ArrayList<>();
        
        // Find applicable policies
        List<GovernancePolicy> applicablePolicies = policies.values().stream()
            .filter(policy -> policy.getApplicableClassification() == asset.getClassification())
            .filter(GovernancePolicy::isActive)
            .collect(Collectors.toList());
        
        for (GovernancePolicy policy : applicablePolicies) {
            Map<String, String> rules = policy.getRules();
            
            // Check data localization
            if (rules.containsKey("data_localization") && 
                !asset.getStorageLocation().contains("IN")) {
                violations.add("Data localization violation: " + 
                              asset.getAssetName() + " not stored in India");
            }
            
            // Check encryption requirement
            if (policy.getApplicableClassification().getRiskLevel() >= 4 && 
                !asset.isEncrypted()) {
                violations.add("Encryption required for: " + asset.getAssetName());
            }
            
            // Check data owner assignment
            if (asset.getDataOwner() == null || asset.getDataOwner().trim().isEmpty()) {
                violations.add("Data owner must be assigned for: " + asset.getAssetName());
            }
        }
        
        return violations;
    }
    
    /**
     * Apply automatic compliance measures
     * स्वचालित अनुपालन उपाय लागू करें
     */
    private void applyAutomaticCompliance(DataAsset asset) {
        // Enable encryption for high-risk data
        if (asset.getClassification().getRiskLevel() >= 4 && !asset.isEncrypted()) {
            asset.setEncrypted(true);
            System.out.println("🔒 Auto-enabled encryption for: " + asset.getAssetName());
        }
        
        // Add compliance metadata
        asset.addMetadata("compliance_check_date", LocalDateTime.now().toString());
        asset.addMetadata("governance_framework_version", "1.0");
        
        // Set data localization flag if in India
        if (asset.getStorageLocation().contains("IN")) {
            asset.addMetadata("data_localized", "true");
        }
    }
    
    /**
     * Request data access
     * डेटा एक्सेस का अनुरोध करें
     */
    public String requestDataAccess(String requesterUserId, String assetId, 
                                   String accessPurpose, LocalDateTime requestedUntil) {
        
        // Validate asset exists
        if (!dataAssets.containsKey(assetId)) {
            System.out.println("❌ Asset not found: " + assetId);
            return null;
        }
        
        DataAsset asset = dataAssets.get(assetId);
        
        // Check if user already has access
        if (asset.getAuthorizedUsers().contains(requesterUserId)) {
            System.out.println("✅ User already has access to: " + asset.getAssetName());
            return null;
        }
        
        // Create access request
        String requestId = "REQ_" + System.currentTimeMillis();
        DataAccessRequest request = new DataAccessRequest(
            requestId, requesterUserId, assetId, accessPurpose, requestedUntil
        );
        
        accessRequests.put(requestId, request);
        
        // Auto-approve for low-risk data with valid business purpose
        if (asset.getClassification().getRiskLevel() <= 2 && 
            isValidBusinessPurpose(accessPurpose)) {
            approveAccessRequest(requestId, "system_auto");
        } else {
            // Notify data stewards for manual approval
            notifyDataStewards(request, asset);
        }
        
        // Log access request
        auditLog.add(new AuditLogEntry(
            generateLogId(),
            requesterUserId,
            "ACCESS_REQUESTED",
            assetId,
            "127.0.0.1",
            true,
            "Access requested for: " + accessPurpose
        ));
        
        System.out.println("📋 Access request created: " + requestId);
        return requestId;
    }
    
    /**
     * Approve data access request
     * डेटा एक्सेस अनुरोध को मंजूरी दें
     */
    public boolean approveAccessRequest(String requestId, String approverUserId) {
        DataAccessRequest request = accessRequests.get(requestId);
        
        if (request == null) {
            System.out.println("❌ Access request not found: " + requestId);
            return false;
        }
        
        if (!"pending".equals(request.getStatus())) {
            System.out.println("⚠️ Request already processed: " + requestId);
            return false;
        }
        
        // Validate approver authority
        if (!canApproveRequest(approverUserId, request)) {
            System.out.println("❌ Insufficient privileges to approve: " + requestId);
            return false;
        }
        
        // Update request
        request.setStatus("approved");
        request.setApproverUserId(approverUserId);
        request.setApprovedAt(LocalDateTime.now());
        
        // Grant access
        DataAsset asset = dataAssets.get(request.getAssetId());
        asset.getAuthorizedUsers().add(request.getRequesterUserId());
        
        // Log approval
        auditLog.add(new AuditLogEntry(
            generateLogId(),
            approverUserId,
            "ACCESS_APPROVED",
            request.getAssetId(),
            "127.0.0.1",
            true,
            "Access approved for user: " + request.getRequesterUserId()
        ));
        
        System.out.println("✅ Access approved: " + requestId);
        return true;
    }
    
    /**
     * Generate compliance report
     * अनुपालन रिपोर्ट उत्पन्न करें
     */
    public Map<String, Object> generateComplianceReport() {
        Map<String, Object> report = new HashMap<>();
        
        // Summary statistics
        Map<String, Object> summary = new HashMap<>();
        summary.put("total_assets", dataAssets.size());
        summary.put("total_policies", policies.size());
        summary.put("active_policies", policies.values().stream()
            .mapToInt(p -> p.isActive() ? 1 : 0).sum());
        summary.put("pending_requests", accessRequests.values().stream()
            .mapToInt(r -> "pending".equals(r.getStatus()) ? 1 : 0).sum());
        
        report.put("summary", summary);
        
        // Assets by classification
        Map<String, Long> assetsByClassification = dataAssets.values().stream()
            .collect(Collectors.groupingBy(
                asset -> asset.getClassification().getLabel(),
                Collectors.counting()
            ));
        report.put("assets_by_classification", assetsByClassification);
        
        // Compliance violations
        List<String> violations = new ArrayList<>();
        for (DataAsset asset : dataAssets.values()) {
            violations.addAll(validateAssetCompliance(asset));
        }
        report.put("compliance_violations", violations);
        
        // Recent audit activities
        List<AuditLogEntry> recentAudits = auditLog.stream()
            .filter(entry -> entry.getTimestamp().isAfter(LocalDateTime.now().minusDays(7)))
            .collect(Collectors.toList());
        
        Map<String, Long> auditsByAction = recentAudits.stream()
            .collect(Collectors.groupingBy(
                AuditLogEntry::getAction,
                Collectors.counting()
            ));
        report.put("recent_audit_activities", auditsByAction);
        
        // Policy coverage
        Map<String, Long> policyCoverage = new HashMap<>();
        for (IndianRegulation regulation : IndianRegulation.values()) {
            long count = policies.values().stream()
                .filter(p -> p.getRegulation() == regulation)
                .filter(GovernancePolicy::isActive)
                .count();
            policyCoverage.put(regulation.name(), count);
        }
        report.put("policy_coverage", policyCoverage);
        
        return report;
    }
    
    /**
     * Helper methods
     */
    private boolean isValidBusinessPurpose(String purpose) {
        Set<String> validPurposes = Set.of(
            "analytics", "reporting", "product_development", 
            "customer_service", "compliance", "research"
        );
        return validPurposes.contains(purpose.toLowerCase());
    }
    
    private void notifyDataStewards(DataAccessRequest request, DataAsset asset) {
        for (String steward : dataStewrads) {
            System.out.println("📧 Notifying data steward " + steward + 
                              " about access request: " + request.getRequestId());
        }
    }
    
    private boolean canApproveRequest(String approverUserId, DataAccessRequest request) {
        // Check if approver is data steward or asset owner
        if (dataStewrads.contains(approverUserId)) {
            return true;
        }
        
        DataAsset asset = dataAssets.get(request.getAssetId());
        if (asset != null && approverUserId.equals(asset.getDataOwner())) {
            return true;
        }
        
        // Check role-based permissions
        Set<String> roles = userRoles.get(approverUserId);
        return roles != null && (roles.contains("data_admin") || roles.contains("access_approver"));
    }
    
    private String generateLogId() {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            String input = System.currentTimeMillis() + "_" + Math.random();
            byte[] hash = md.digest(input.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            
            return "LOG_" + hexString.toString().substring(0, 8).toUpperCase();
        } catch (Exception e) {
            return "LOG_" + System.currentTimeMillis();
        }
    }
    
    /**
     * Main demonstration method
     * मुख्य प्रदर्शन विधि
     */
    public static void main(String[] args) {
        System.out.println("📱 Jio Data Governance Framework Demo");
        System.out.println("=====================================");
        
        DataGovernanceFramework framework = new DataGovernanceFramework();
        
        // Register sample data assets
        System.out.println("\n📝 Registering data assets...");
        
        // Customer PII data
        DataAsset customerData = new DataAsset(
            "ASSET_CUSTOMER_001",
            "Jio Customer Personal Data",
            DataClassification.PII,
            "data_owner_001",
            "Customer service and billing",
            Set.of("service_team", "billing_team"),
            "jio_datacenter_mumbai_IN"
        );
        framework.registerDataAsset(customerData);
        
        // Telecom usage data
        DataAsset usageData = new DataAsset(
            "ASSET_USAGE_001", 
            "Network Usage Analytics Data",
            DataClassification.TELECOM,
            "network_team_lead",
            "Network optimization and planning",
            Set.of("network_analysts", "planning_team"),
            "jio_datacenter_pune_IN"
        );
        framework.registerDataAsset(usageData);
        
        // Payment data
        DataAsset paymentData = new DataAsset(
            "ASSET_PAYMENT_001",
            "JioMoney Transaction Data", 
            DataClassification.FINANCIAL,
            "fintech_lead",
            "Payment processing and fraud detection",
            Set.of("payment_team", "fraud_team"),
            "jio_datacenter_bangalore_IN"
        );
        framework.registerDataAsset(paymentData);
        
        // Request data access
        System.out.println("\n🔐 Processing access requests...");
        
        String requestId1 = framework.requestDataAccess(
            "analyst001", "ASSET_USAGE_001", "analytics", 
            LocalDateTime.now().plusDays(30)
        );
        
        String requestId2 = framework.requestDataAccess(
            "developer001", "ASSET_CUSTOMER_001", "product_development",
            LocalDateTime.now().plusDays(60)
        );
        
        // Approve requests
        if (requestId2 != null) {
            framework.approveAccessRequest(requestId2, "steward001");
        }
        
        // Generate compliance report
        System.out.println("\n📊 Compliance Report:");
        Map<String, Object> report = framework.generateComplianceReport();
        
        System.out.println("Summary: " + report.get("summary"));
        System.out.println("Assets by Classification: " + report.get("assets_by_classification"));
        System.out.println("Compliance Violations: " + report.get("compliance_violations"));
        System.out.println("Policy Coverage: " + report.get("policy_coverage"));
        
        // Show recent audit activities
        System.out.println("\nRecent Audit Activities: " + report.get("recent_audit_activities"));
        
        System.out.println("\n✅ Data Governance Framework demonstration completed!");
    }
}
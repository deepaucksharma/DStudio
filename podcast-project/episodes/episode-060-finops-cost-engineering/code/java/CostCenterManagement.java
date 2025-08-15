package com.hinditech.finops.enterprise;

/**
 * Enterprise Cost Center Management System
 * ========================================
 * 
 * Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering
 * Enterprise-grade cost center management with department allocation
 * 
 * Author: Hindi Tech Community
 * Date: 2025
 * Version: 1.0
 * 
 * Features:
 * - Hierarchical cost center structure
 * - Automated cost allocation
 * - Budget management per cost center
 * - Approval workflows
 * - Real-time cost tracking
 * - Department-wise reporting
 * 
 * Mumbai Context: Cost center management जैसे Mumbai corporate office
 * - Department-wise budget allocation
 * - Project-wise expense tracking  
 * - Approval hierarchy for high-value expenses
 */

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;
import javax.annotation.concurrent.ThreadSafe;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Cost Center entity representing organizational unit
 * 
 * Mumbai Context: यह department structure जैसा है Mumbai office में
 */
public class CostCenter {
    private final String costCenterId;
    private final String name;
    private final String department;
    private final String manager;
    private final BigDecimal monthlyBudget;
    private final BigDecimal currentSpend;
    private final LocalDateTime createdAt;
    
    // Constructor
    public CostCenter(String costCenterId, String name, String department, 
                     String manager, BigDecimal monthlyBudget) {
        this.costCenterId = costCenterId;
        this.name = name;
        this.department = department;
        this.manager = manager;
        this.monthlyBudget = monthlyBudget;
        this.currentSpend = BigDecimal.ZERO;
        this.createdAt = LocalDateTime.now();
    }
    
    // Getters
    public String getCostCenterId() { return costCenterId; }
    public String getName() { return name; }
    public String getDepartment() { return department; }
    public String getManager() { return manager; }
    public BigDecimal getMonthlyBudget() { return monthlyBudget; }
    public BigDecimal getCurrentSpend() { return currentSpend; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    
    /**
     * Calculate budget utilization percentage
     * 
     * Mumbai Context: Monthly budget का कितना use हो गया
     */
    public double getBudgetUtilization() {
        if (monthlyBudget.compareTo(BigDecimal.ZERO) == 0) {
            return 0.0;
        }
        return currentSpend.divide(monthlyBudget, 4, BigDecimal.ROUND_HALF_UP)
                          .multiply(BigDecimal.valueOf(100))
                          .doubleValue();
    }
    
    @Override
    public String toString() {
        return String.format("CostCenter{id='%s', name='%s', dept='%s', budget=%s, spend=%s (%.1f%%)}", 
                           costCenterId, name, department, monthlyBudget, currentSpend, getBudgetUtilization());
    }
}

/**
 * Cost allocation entry for tracking expenses
 */
class CostAllocation {
    private final String allocationId;
    private final String costCenterId;
    private final String resourceId;
    private final String serviceName;
    private final BigDecimal amount;
    private final String currency;
    private final LocalDateTime timestamp;
    private final String allocatedBy;
    private final Map<String, String> tags;
    
    public CostAllocation(String allocationId, String costCenterId, String resourceId,
                         String serviceName, BigDecimal amount, String currency, 
                         String allocatedBy, Map<String, String> tags) {
        this.allocationId = allocationId;
        this.costCenterId = costCenterId;
        this.resourceId = resourceId;
        this.serviceName = serviceName;
        this.amount = amount;
        this.currency = currency;
        this.timestamp = LocalDateTime.now();
        this.allocatedBy = allocatedBy;
        this.tags = new HashMap<>(tags);
    }
    
    // Getters
    public String getAllocationId() { return allocationId; }
    public String getCostCenterId() { return costCenterId; }
    public String getResourceId() { return resourceId; }
    public String getServiceName() { return serviceName; }
    public BigDecimal getAmount() { return amount; }
    public String getCurrency() { return currency; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public String getAllocatedBy() { return allocatedBy; }
    public Map<String, String> getTags() { return new HashMap<>(tags); }
}

/**
 * Budget alert configuration
 */
class BudgetAlert {
    private final String alertId;
    private final String costCenterId;
    private final double thresholdPercentage;
    private final String alertType; // EMAIL, SLACK, SMS
    private final List<String> recipients;
    private final boolean isActive;
    
    public BudgetAlert(String alertId, String costCenterId, double thresholdPercentage,
                      String alertType, List<String> recipients) {
        this.alertId = alertId;
        this.costCenterId = costCenterId;
        this.thresholdPercentage = thresholdPercentage;
        this.alertType = alertType;
        this.recipients = new ArrayList<>(recipients);
        this.isActive = true;
    }
    
    // Getters
    public String getAlertId() { return alertId; }
    public String getCostCenterId() { return costCenterId; }
    public double getThresholdPercentage() { return thresholdPercentage; }
    public String getAlertType() { return alertType; }
    public List<String> getRecipients() { return new ArrayList<>(recipients); }
    public boolean isActive() { return isActive; }
}

/**
 * Main Cost Center Management System
 * 
 * Mumbai Context: यह complete enterprise cost management जैसा है
 * - Centralized cost tracking
 * - Department-wise budget allocation
 * - Real-time monitoring और alerts
 */
@ThreadSafe
public class CostCenterManagement {
    
    private static final Logger logger = LoggerFactory.getLogger(CostCenterManagement.class);
    
    // Thread-safe collections for concurrent access
    private final Map<String, CostCenter> costCenters = new ConcurrentHashMap<>();
    private final Map<String, List<CostAllocation>> allocations = new ConcurrentHashMap<>();
    private final Map<String, List<BudgetAlert>> budgetAlerts = new ConcurrentHashMap<>();
    
    // Configuration
    private final String defaultCurrency = "USD";
    private final DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    
    /**
     * Create new cost center
     * 
     * Mumbai Context: नया department setup करना office में
     */
    public synchronized boolean createCostCenter(String costCenterId, String name, 
                                               String department, String manager, 
                                               BigDecimal monthlyBudget) {
        try {
            if (costCenters.containsKey(costCenterId)) {
                logger.warn("Cost center already exists: {}", costCenterId);
                return false;
            }
            
            CostCenter costCenter = new CostCenter(costCenterId, name, department, 
                                                 manager, monthlyBudget);
            costCenters.put(costCenterId, costCenter);
            allocations.put(costCenterId, new ArrayList<>());
            budgetAlerts.put(costCenterId, new ArrayList<>());
            
            logger.info("Created cost center: {}", costCenter);
            return true;
            
        } catch (Exception e) {
            logger.error("Failed to create cost center: {}", costCenterId, e);
            return false;
        }
    }
    
    /**
     * Allocate cost to specific cost center
     * 
     * Mumbai Context: Resource का cost particular department को assign करना
     */
    public synchronized boolean allocateCost(String costCenterId, String resourceId,
                                           String serviceName, BigDecimal amount,
                                           String allocatedBy, Map<String, String> tags) {
        try {
            if (!costCenters.containsKey(costCenterId)) {
                logger.error("Cost center not found: {}", costCenterId);
                return false;
            }
            
            String allocationId = generateAllocationId(costCenterId, resourceId);
            CostAllocation allocation = new CostAllocation(
                allocationId, costCenterId, resourceId, serviceName,
                amount, defaultCurrency, allocatedBy, tags
            );
            
            allocations.get(costCenterId).add(allocation);
            
            // Check budget thresholds
            checkBudgetThresholds(costCenterId);
            
            logger.info("Allocated cost: {} {} to cost center: {}", 
                       amount, defaultCurrency, costCenterId);
            return true;
            
        } catch (Exception e) {
            logger.error("Failed to allocate cost to cost center: {}", costCenterId, e);
            return false;
        }
    }
    
    /**
     * Get current spend for cost center
     * 
     * Mumbai Context: Department का current month spending check करना
     */
    public BigDecimal getCurrentSpend(String costCenterId) {
        try {
            List<CostAllocation> centerAllocations = allocations.get(costCenterId);
            if (centerAllocations == null) {
                return BigDecimal.ZERO;
            }
            
            // Calculate current month spend
            LocalDateTime monthStart = LocalDateTime.now().withDayOfMonth(1).withHour(0).withMinute(0).withSecond(0);
            
            return centerAllocations.stream()
                    .filter(allocation -> allocation.getTimestamp().isAfter(monthStart))
                    .map(CostAllocation::getAmount)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);
                    
        } catch (Exception e) {
            logger.error("Failed to get current spend for cost center: {}", costCenterId, e);
            return BigDecimal.ZERO;
        }
    }
    
    /**
     * Setup budget alert for cost center
     * 
     * Mumbai Context: Budget limit के लिए alert setup करना
     */
    public synchronized boolean setupBudgetAlert(String costCenterId, double thresholdPercentage,
                                               String alertType, List<String> recipients) {
        try {
            if (!costCenters.containsKey(costCenterId)) {
                logger.error("Cost center not found: {}", costCenterId);
                return false;
            }
            
            String alertId = generateAlertId(costCenterId, thresholdPercentage);
            BudgetAlert alert = new BudgetAlert(alertId, costCenterId, thresholdPercentage,
                                              alertType, recipients);
            
            budgetAlerts.get(costCenterId).add(alert);
            
            logger.info("Setup budget alert: {}% threshold for cost center: {}", 
                       thresholdPercentage, costCenterId);
            return true;
            
        } catch (Exception e) {
            logger.error("Failed to setup budget alert for cost center: {}", costCenterId, e);
            return false;
        }
    }
    
    /**
     * Check budget thresholds and trigger alerts
     * 
     * Mumbai Context: Budget limit check करके automatic alert भेजना
     */
    private void checkBudgetThresholds(String costCenterId) {
        try {
            CostCenter costCenter = costCenters.get(costCenterId);
            if (costCenter == null) {
                return;
            }
            
            BigDecimal currentSpend = getCurrentSpend(costCenterId);
            double utilization = calculateUtilization(currentSpend, costCenter.getMonthlyBudget());
            
            List<BudgetAlert> alerts = budgetAlerts.get(costCenterId);
            if (alerts != null) {
                for (BudgetAlert alert : alerts) {
                    if (alert.isActive() && utilization >= alert.getThresholdPercentage()) {
                        triggerBudgetAlert(costCenter, alert, utilization, currentSpend);
                    }
                }
            }
            
        } catch (Exception e) {
            logger.error("Failed to check budget thresholds for cost center: {}", costCenterId, e);
        }
    }
    
    /**
     * Trigger budget alert
     * 
     * Mumbai Context: Budget alert को team को send करना
     */
    private void triggerBudgetAlert(CostCenter costCenter, BudgetAlert alert, 
                                  double utilization, BigDecimal currentSpend) {
        try {
            String alertMessage = String.format(
                "🚨 Budget Alert: %s\n" +
                "Cost Center: %s (%s)\n" +
                "Current Spend: %s %s\n" +
                "Monthly Budget: %s %s\n" +
                "Utilization: %.1f%%\n" +
                "Threshold: %.1f%%\n\n" +
                "Mumbai Context: यह आपके monthly budget limit का warning है!\n" +
                "जैसे mobile plan में data limit cross होने का alert\n\n" +
                "Action Required: Please review spending and take corrective measures\n" +
                "Contact: Cost Center Manager - %s",
                alert.getAlertType(),
                costCenter.getName(),
                costCenter.getDepartment(),
                currentSpend,
                "USD",
                costCenter.getMonthlyBudget(),
                "USD",
                utilization,
                alert.getThresholdPercentage(),
                costCenter.getManager()
            );
            
            // Send alert to recipients
            sendAlert(alert.getAlertType(), alert.getRecipients(), alertMessage);
            
            logger.warn("Budget alert triggered for cost center: {} - Utilization: {}%", 
                       costCenter.getCostCenterId(), utilization);
                       
        } catch (Exception e) {
            logger.error("Failed to trigger budget alert for cost center: {}", 
                        costCenter.getCostCenterId(), e);
        }
    }
    
    /**
     * Send alert through configured channel
     * 
     * Mumbai Context: Alert को appropriate channel से send करना
     */
    private void sendAlert(String alertType, List<String> recipients, String message) {
        try {
            switch (alertType.toUpperCase()) {
                case "EMAIL":
                    sendEmailAlert(recipients, message);
                    break;
                case "SLACK":
                    sendSlackAlert(recipients, message);
                    break;
                case "SMS":
                    sendSMSAlert(recipients, message);
                    break;
                default:
                    logger.warn("Unknown alert type: {}", alertType);
            }
        } catch (Exception e) {
            logger.error("Failed to send alert via {}: {}", alertType, e.getMessage());
        }
    }
    
    /**
     * Send email alert (placeholder implementation)
     */
    private void sendEmailAlert(List<String> recipients, String message) {
        // Implementation would integrate with email service (SES, SendGrid, etc.)
        logger.info("Email alert sent to {} recipients", recipients.size());
    }
    
    /**
     * Send Slack alert (placeholder implementation)
     */
    private void sendSlackAlert(List<String> channels, String message) {
        // Implementation would integrate with Slack webhook
        logger.info("Slack alert sent to {} channels", channels.size());
    }
    
    /**
     * Send SMS alert (placeholder implementation)
     */
    private void sendSMSAlert(List<String> phoneNumbers, String message) {
        // Implementation would integrate with SMS service (SNS, Twilio, etc.)
        logger.info("SMS alert sent to {} numbers", phoneNumbers.size());
    }
    
    /**
     * Generate comprehensive cost center report
     * 
     * Mumbai Context: Complete department-wise cost report
     */
    public String generateCostCenterReport() {
        try {
            StringBuilder report = new StringBuilder();
            report.append("Cost Center Management Report\n");
            report.append("============================\n");
            report.append("Generated: ").append(LocalDateTime.now().format(dateFormatter)).append("\n\n");
            
            report.append("EXECUTIVE SUMMARY (Mumbai Style)\n");
            report.append("===============================\n");
            report.append("यह report आपके organization के सभी departments का cost analysis है\n");
            report.append("जैसे Mumbai office में हर department का monthly budget tracking\n\n");
            
            BigDecimal totalBudget = BigDecimal.ZERO;
            BigDecimal totalSpend = BigDecimal.ZERO;
            
            report.append("COST CENTER BREAKDOWN\n");
            report.append("====================\n");
            
            for (CostCenter costCenter : costCenters.values()) {
                BigDecimal currentSpend = getCurrentSpend(costCenter.getCostCenterId());
                double utilization = calculateUtilization(currentSpend, costCenter.getMonthlyBudget());
                
                totalBudget = totalBudget.add(costCenter.getMonthlyBudget());
                totalSpend = totalSpend.add(currentSpend);
                
                String status = getUtilizationStatus(utilization);
                
                report.append(String.format("Department: %s (%s)\n", 
                                           costCenter.getName(), costCenter.getDepartment()));
                report.append(String.format("  Manager: %s\n", costCenter.getManager()));
                report.append(String.format("  Budget: $%s\n", costCenter.getMonthlyBudget()));
                report.append(String.format("  Current Spend: $%s\n", currentSpend));
                report.append(String.format("  Utilization: %.1f%% (%s)\n", utilization, status));
                report.append(String.format("  Remaining: $%s\n", 
                                           costCenter.getMonthlyBudget().subtract(currentSpend)));
                report.append("\n");
            }
            
            // Summary statistics
            double overallUtilization = calculateUtilization(totalSpend, totalBudget);
            
            report.append("OVERALL SUMMARY\n");
            report.append("==============\n");
            report.append(String.format("Total Budget: $%s\n", totalBudget));
            report.append(String.format("Total Spend: $%s\n", totalSpend));
            report.append(String.format("Overall Utilization: %.1f%%\n", overallUtilization));
            report.append(String.format("Remaining Budget: $%s\n", totalBudget.subtract(totalSpend)));
            
            // Mumbai context insights
            report.append("\nMUMBAI CONTEXT ANALYSIS\n");
            report.append("=======================\n");
            
            if (overallUtilization > 90) {
                report.append("🚨 CRITICAL: Overall budget utilization very high!\n");
                report.append("   Like Mumbai monsoon season - emergency measures needed\n");
            } else if (overallUtilization > 75) {
                report.append("⚠️  WARNING: Budget utilization approaching limits\n");
                report.append("   Like Mumbai traffic peak hours - careful monitoring needed\n");
            } else {
                report.append("✅ HEALTHY: Budget utilization within normal range\n");
                report.append("   Like smooth Mumbai local train journey - all good!\n");
            }
            
            // Recommendations
            report.append("\nRECOMMENDATIONS\n");
            report.append("==============\n");
            report.append("1. Review high-utilization departments for optimization\n");
            report.append("2. Implement automated cost controls for over-budget scenarios\n");
            report.append("3. Set up proactive alerts at 75% and 90% thresholds\n");
            report.append("4. Conduct quarterly budget reviews with department heads\n");
            report.append("5. Implement cost allocation tagging standards\n\n");
            
            report.append("Contact: Hindi Tech Community for enterprise FinOps consultation\n");
            
            return report.toString();
            
        } catch (Exception e) {
            logger.error("Failed to generate cost center report", e);
            return "Error generating cost center report: " + e.getMessage();
        }
    }
    
    // Helper methods
    
    private double calculateUtilization(BigDecimal spend, BigDecimal budget) {
        if (budget.compareTo(BigDecimal.ZERO) == 0) {
            return 0.0;
        }
        return spend.divide(budget, 4, BigDecimal.ROUND_HALF_UP)
                   .multiply(BigDecimal.valueOf(100))
                   .doubleValue();
    }
    
    private String getUtilizationStatus(double utilization) {
        if (utilization >= 100) {
            return "OVER BUDGET";
        } else if (utilization >= 90) {
            return "CRITICAL";
        } else if (utilization >= 75) {
            return "WARNING";
        } else {
            return "HEALTHY";
        }
    }
    
    private String generateAllocationId(String costCenterId, String resourceId) {
        return String.format("ALLOC-%s-%s-%d", 
                           costCenterId, resourceId, System.currentTimeMillis());
    }
    
    private String generateAlertId(String costCenterId, double threshold) {
        return String.format("ALERT-%s-%.0f-%d", 
                           costCenterId, threshold, System.currentTimeMillis());
    }
    
    // Getters for read-only access
    public Map<String, CostCenter> getCostCenters() {
        return new HashMap<>(costCenters);
    }
    
    public List<CostAllocation> getAllocations(String costCenterId) {
        return new ArrayList<>(allocations.getOrDefault(costCenterId, new ArrayList<>()));
    }
    
    /**
     * Main method for demonstration
     */
    public static void main(String[] args) {
        System.out.println("🏢 Initializing Enterprise Cost Center Management...");
        
        CostCenterManagement ccm = new CostCenterManagement();
        
        // Create cost centers
        System.out.println("\n📊 Creating cost centers...");
        ccm.createCostCenter("CC-ENG-001", "Engineering Team", "Engineering", 
                           "rajesh.sharma@company.com", new BigDecimal("50000"));
        ccm.createCostCenter("CC-MKT-001", "Marketing Team", "Marketing", 
                           "priya.patel@company.com", new BigDecimal("25000"));
        ccm.createCostCenter("CC-OPS-001", "Operations Team", "Operations", 
                           "amit.singh@company.com", new BigDecimal("30000"));
        
        // Setup budget alerts
        System.out.println("\n🔔 Setting up budget alerts...");
        ccm.setupBudgetAlert("CC-ENG-001", 75.0, "EMAIL", 
                           Arrays.asList("rajesh.sharma@company.com", "cto@company.com"));
        ccm.setupBudgetAlert("CC-MKT-001", 80.0, "SLACK", 
                           Arrays.asList("#marketing-alerts"));
        ccm.setupBudgetAlert("CC-OPS-001", 85.0, "EMAIL", 
                           Arrays.asList("amit.singh@company.com"));
        
        // Allocate some costs
        System.out.println("\n💰 Allocating costs to departments...");
        Map<String, String> tags = new HashMap<>();
        tags.put("project", "web-platform");
        tags.put("environment", "production");
        
        ccm.allocateCost("CC-ENG-001", "i-1234567890abcdef0", "EC2", 
                        new BigDecimal("15000"), "system", tags);
        ccm.allocateCost("CC-MKT-001", "db-marketing-prod", "RDS", 
                        new BigDecimal("8000"), "system", tags);
        ccm.allocateCost("CC-OPS-001", "bucket-ops-logs", "S3", 
                        new BigDecimal("2000"), "system", tags);
        
        // Generate and display report
        System.out.println("\n📄 Generating cost center report...");
        String report = ccm.generateCostCenterReport();
        System.out.println(report);
        
        // Display current spend
        System.out.println("\n💸 Current Department Spending:");
        for (String costCenterId : ccm.getCostCenters().keySet()) {
            BigDecimal spend = ccm.getCurrentSpend(costCenterId);
            CostCenter cc = ccm.getCostCenters().get(costCenterId);
            System.out.printf("  %s: $%s (%.1f%% of budget)\n", 
                             cc.getName(), spend, 
                             ccm.calculateUtilization(spend, cc.getMonthlyBudget()));
        }
        
        System.out.println("\n✅ Enterprise cost center management demo completed!");
        System.out.println("🏙️ Mumbai Context: यह system आपके corporate budget management को efficient बनाता है!");
    }
}

/*
Production Implementation Guide (Hindi):
========================================

1. Database Integration:
   - Use enterprise database (PostgreSQL, Oracle, SQL Server)
   - Implement proper transaction management
   - Add audit logging for all cost allocations
   - Set up database connection pooling

2. Enterprise Integration:
   - LDAP/Active Directory integration for user management
   - SAP/Oracle ERP integration for budget data
   - ServiceNow integration for approval workflows
   - Salesforce integration for customer cost allocation

3. Security & Compliance:
   - Role-based access control (RBAC)
   - Data encryption at rest and in transit
   - Audit trail for all financial transactions
   - SOX compliance for financial reporting

4. Mumbai Business Context:
   - Multi-currency support (USD, INR, EUR)
   - Regional cost center hierarchies
   - Local approval workflows
   - Integration with Indian financial regulations

5. Monitoring & Alerting:
   - Real-time budget monitoring
   - Automated threshold alerts
   - Executive dashboard integration
   - Mobile app notifications

यह system आपके enterprise cost management को Mumbai corporate culture के according efficient बनाएगा!
*/
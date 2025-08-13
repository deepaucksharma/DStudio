/**
 * Incident Command System - Episode 3: Human Factor in Tech
 * =========================================================
 * 
 * Indian corporate hierarchy के साथ incident management
 * TCS/Infosys style leadership structure के साथ crisis handling
 * 
 * Features:
 * - Hierarchical command structure (CEO -> CTO -> VP -> Senior -> Junior)
 * - Escalation matrix with cultural sensitivity
 * - Face-saving communication patterns
 * - Multi-language incident communication
 */

import java.util.*;
import java.util.concurrent.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

// Incident की severity levels
enum IncidentSeverity {
    P1_CRITICAL("P1 - Critical", "Complete system down", Arrays.asList("CEO", "CTO", "VP")),
    P2_HIGH("P2 - High", "Major feature affected", Arrays.asList("CTO", "VP", "Senior")),
    P3_MEDIUM("P3 - Medium", "Minor issue", Arrays.asList("VP", "Senior")),
    P4_LOW("P4 - Low", "Enhancement request", Arrays.asList("Senior"));
    
    private final String level;
    private final String description;
    private final List<String> escalationLevels;
    
    IncidentSeverity(String level, String description, List<String> escalationLevels) {
        this.level = level;
        this.description = description;
        this.escalationLevels = escalationLevels;
    }
    
    public List<String> getEscalationLevels() { return escalationLevels; }
    public String getLevel() { return level; }
    public String getDescription() { return description; }
}

// Employee hierarchy
class Employee {
    private String id;
    private String name;
    private String role;
    private String level; // CEO, CTO, VP, Senior, Junior
    private String department;
    private boolean isAvailable;
    private List<String> languages; // Hindi, English, Tamil, etc.
    private String phoneNumber;
    private String email;
    
    public Employee(String id, String name, String role, String level, String department) {
        this.id = id;
        this.name = name;
        this.role = role;
        this.level = level;
        this.department = department;
        this.isAvailable = true;
        this.languages = Arrays.asList("English", "Hindi");
    }
    
    // Getters and setters
    public String getId() { return id; }
    public String getName() { return name; }
    public String getRole() { return role; }
    public String getLevel() { return level; }
    public String getDepartment() { return department; }
    public boolean isAvailable() { return isAvailable; }
    public void setAvailable(boolean available) { this.isAvailable = available; }
    public List<String> getLanguages() { return languages; }
    public String getPhoneNumber() { return phoneNumber; }
    public String getEmail() { return email; }
}

// Incident का details
class Incident {
    private String incidentId;
    private String title;
    private String description;
    private IncidentSeverity severity;
    private LocalDateTime startTime;
    private LocalDateTime resolvedTime;
    private String affectedSystem;
    private List<String> impactedUsers;
    private String currentOwner;
    private List<String> escalationHistory;
    private Map<String, String> communications;
    
    public Incident(String incidentId, String title, String description, 
                   IncidentSeverity severity, String affectedSystem) {
        this.incidentId = incidentId;
        this.title = title;
        this.description = description;
        this.severity = severity;
        this.affectedSystem = affectedSystem;
        this.startTime = LocalDateTime.now();
        this.impactedUsers = new ArrayList<>();
        this.escalationHistory = new ArrayList<>();
        this.communications = new HashMap<>();
    }
    
    // Getters and setters
    public String getIncidentId() { return incidentId; }
    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public IncidentSeverity getSeverity() { return severity; }
    public LocalDateTime getStartTime() { return startTime; }
    public String getAffectedSystem() { return affectedSystem; }
    public String getCurrentOwner() { return currentOwner; }
    public void setCurrentOwner(String owner) { this.currentOwner = owner; }
    public List<String> getEscalationHistory() { return escalationHistory; }
    public Map<String, String> getCommunications() { return communications; }
    
    public void addEscalation(String escalationNote) {
        escalationHistory.add(LocalDateTime.now() + ": " + escalationNote);
    }
    
    public void addCommunication(String recipient, String message) {
        communications.put(recipient + "_" + LocalDateTime.now(), message);
    }
}

// Main Incident Command System
public class IncidentCommandSystem {
    private List<Employee> employees;
    private List<Incident> activeIncidents;
    private Map<String, List<Employee>> hierarchyMap;
    private ExecutorService communicationExecutor;
    
    public IncidentCommandSystem() {
        this.employees = new ArrayList<>();
        this.activeIncidents = new ArrayList<>();
        this.hierarchyMap = new HashMap<>();
        this.communicationExecutor = Executors.newFixedThreadPool(5);
        initializeHierarchy();
    }
    
    private void initializeHierarchy() {
        // TCS/Infosys style hierarchy setup
        hierarchyMap.put("CEO", new ArrayList<>());
        hierarchyMap.put("CTO", new ArrayList<>());
        hierarchyMap.put("VP", new ArrayList<>());
        hierarchyMap.put("Senior", new ArrayList<>());
        hierarchyMap.put("Junior", new ArrayList<>());
        
        // Sample employees - Indian names and roles
        addEmployee(new Employee("EMP001", "Rajesh Gupta", "Chief Executive Officer", "CEO", "Executive"));
        addEmployee(new Employee("EMP002", "Priya Sharma", "Chief Technology Officer", "CTO", "Technology"));
        addEmployee(new Employee("EMP003", "Amit Patel", "VP Engineering", "VP", "Engineering"));
        addEmployee(new Employee("EMP004", "Sneha Reddy", "Senior Architect", "Senior", "Engineering"));
        addEmployee(new Employee("EMP005", "Vikram Singh", "Senior Developer", "Senior", "Engineering"));
        addEmployee(new Employee("EMP006", "Kavya Nair", "Developer", "Junior", "Engineering"));
        addEmployee(new Employee("EMP007", "Arjun Kumar", "DevOps Engineer", "Junior", "Operations"));
    }
    
    public void addEmployee(Employee employee) {
        employees.add(employee);
        hierarchyMap.get(employee.getLevel()).add(employee);
    }
    
    public void createIncident(String title, String description, 
                              IncidentSeverity severity, String affectedSystem) {
        String incidentId = "INC" + System.currentTimeMillis();
        Incident incident = new Incident(incidentId, title, description, severity, affectedSystem);
        
        System.out.println("\n🚨 नया Incident Created: " + incidentId);
        System.out.println("Title: " + title);
        System.out.println("Severity: " + severity.getLevel());
        System.out.println("Affected System: " + affectedSystem);
        System.out.println("Time: " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        
        // Initial assignment based on severity
        assignInitialOwner(incident);
        activeIncidents.add(incident);
        
        // Start escalation timer
        startEscalationTimer(incident);
        
        // Send initial notifications
        sendInitialNotifications(incident);
    }
    
    private void assignInitialOwner(Incident incident) {
        IncidentSeverity severity = incident.getSeverity();
        List<String> eligibleLevels = severity.getEscalationLevels();
        
        // Start with the lowest level that can handle this severity
        String startLevel = eligibleLevels.get(eligibleLevels.size() - 1);
        List<Employee> availableEmployees = hierarchyMap.get(startLevel).stream()
            .filter(Employee::isAvailable)
            .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
        
        if (!availableEmployees.isEmpty()) {
            Employee assignedEmployee = availableEmployees.get(0);
            incident.setCurrentOwner(assignedEmployee.getId());
            assignedEmployee.setAvailable(false);
            
            System.out.println("✅ Assigned to: " + assignedEmployee.getName() + 
                             " (" + assignedEmployee.getRole() + ")");
            
            incident.addEscalation("Initial assignment to " + assignedEmployee.getName());
        } else {
            // Escalate immediately if no one available at starting level
            escalateIncident(incident);
        }
    }
    
    private void escalateIncident(Incident incident) {
        System.out.println("\n⬆️ Escalating incident: " + incident.getIncidentId());
        
        List<String> escalationLevels = incident.getSeverity().getEscalationLevels();
        String currentOwnerLevel = getCurrentOwnerLevel(incident.getCurrentOwner());
        
        int currentLevelIndex = escalationLevels.indexOf(currentOwnerLevel);
        if (currentLevelIndex > 0) {
            String nextLevel = escalationLevels.get(currentLevelIndex - 1);
            
            List<Employee> nextLevelEmployees = hierarchyMap.get(nextLevel).stream()
                .filter(Employee::isAvailable)
                .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
            
            if (!nextLevelEmployees.isEmpty()) {
                // Free up current owner
                if (incident.getCurrentOwner() != null) {
                    Employee currentOwner = findEmployeeById(incident.getCurrentOwner());
                    if (currentOwner != null) {
                        currentOwner.setAvailable(true);
                    }
                }
                
                // Assign to next level
                Employee newOwner = nextLevelEmployees.get(0);
                incident.setCurrentOwner(newOwner.getId());
                newOwner.setAvailable(false);
                
                String escalationMessage = String.format(
                    "Escalated from %s to %s (%s)", 
                    currentOwnerLevel, newOwner.getName(), newOwner.getRole()
                );
                
                incident.addEscalation(escalationMessage);
                System.out.println("✅ " + escalationMessage);
                
                // Send escalation notifications
                sendEscalationNotifications(incident, newOwner);
            } else {
                System.out.println("❌ No available employees at " + nextLevel + " level!");
                incident.addEscalation("Escalation failed - no available employees at " + nextLevel);
            }
        } else {
            System.out.println("🔥 Maximum escalation level reached! CEO involvement required!");
            incident.addEscalation("Maximum escalation reached - CEO notification sent");
        }
    }
    
    private String getCurrentOwnerLevel(String ownerId) {
        if (ownerId == null) return null;
        
        Employee owner = findEmployeeById(ownerId);
        return owner != null ? owner.getLevel() : null;
    }
    
    private Employee findEmployeeById(String employeeId) {
        return employees.stream()
            .filter(emp -> emp.getId().equals(employeeId))
            .findFirst()
            .orElse(null);
    }
    
    private void startEscalationTimer(Incident incident) {
        // Auto-escalation based on severity
        int escalationTimeMinutes;
        switch (incident.getSeverity()) {
            case P1_CRITICAL: escalationTimeMinutes = 15; break;
            case P2_HIGH: escalationTimeMinutes = 30; break;
            case P3_MEDIUM: escalationTimeMinutes = 60; break;
            case P4_LOW: escalationTimeMinutes = 240; break;
            default: escalationTimeMinutes = 60;
        }
        
        // Simulate escalation timer (in real system, use ScheduledExecutorService)
        Timer escalationTimer = new Timer();
        escalationTimer.schedule(new TimerTask() {
            @Override
            public void run() {
                if (activeIncidents.contains(incident)) {
                    System.out.println("\n⏰ Auto-escalation timer expired for: " + incident.getIncidentId());
                    escalateIncident(incident);
                }
            }
        }, escalationTimeMinutes * 1000); // Convert to milliseconds (demo purposes)
    }
    
    private void sendInitialNotifications(Incident incident) {
        communicationExecutor.submit(() -> {
            Employee owner = findEmployeeById(incident.getCurrentOwner());
            if (owner != null) {
                String message = generateCulturallyAppropriateMessage(incident, owner, "ASSIGNMENT");
                System.out.println("\n📱 SMS to " + owner.getName() + ": " + message);
                
                // Email notification
                String emailMessage = generateDetailedEmailMessage(incident);
                System.out.println("📧 Email to " + owner.getName() + ": " + emailMessage);
                
                incident.addCommunication(owner.getName(), message);
            }
        });
    }
    
    private void sendEscalationNotifications(Incident incident, Employee newOwner) {
        communicationExecutor.submit(() -> {
            String message = generateCulturallyAppropriateMessage(incident, newOwner, "ESCALATION");
            System.out.println("\n📱 Escalation SMS to " + newOwner.getName() + ": " + message);
            
            // Also notify all stakeholders
            List<String> stakeholders = incident.getSeverity().getEscalationLevels();
            for (String level : stakeholders) {
                for (Employee emp : hierarchyMap.get(level)) {
                    if (!emp.getId().equals(newOwner.getId())) {
                        String stakeholderMessage = generateStakeholderMessage(incident, emp);
                        System.out.println("📱 Stakeholder notification to " + emp.getName() + ": " + stakeholderMessage);
                    }
                }
            }
            
            incident.addCommunication(newOwner.getName(), message);
        });
    }
    
    private String generateCulturallyAppropriateMessage(Incident incident, Employee recipient, String type) {
        // Indian corporate communication style - respectful and hierarchical
        StringBuilder message = new StringBuilder();
        
        if (type.equals("ASSIGNMENT")) {
            message.append("नमस्ते ").append(recipient.getName()).append(" ji, ");
            message.append("आपको एक ").append(incident.getSeverity().getLevel())
                   .append(" incident assign किया गया है। ");
        } else if (type.equals("ESCALATION")) {
            message.append("नमस्ते ").append(recipient.getName()).append(" Sir/Madam, ");
            message.append("आपकी attention की जरूरत है - incident escalate हुआ है। ");
        }
        
        message.append("System: ").append(incident.getAffectedSystem()).append(". ");
        message.append("Please take immediate action. धन्यवाद।");
        
        return message.toString();
    }
    
    private String generateDetailedEmailMessage(Incident incident) {
        return String.format(
            "Subject: %s - %s\n\n" +
            "प्रिय Team,\n\n" +
            "Incident Details:\n" +
            "ID: %s\n" +
            "Title: %s\n" +
            "Severity: %s\n" +
            "Description: %s\n" +
            "Affected System: %s\n" +
            "Start Time: %s\n\n" +
            "कृपया तुरंत action लें और regular updates भेजते रहें।\n\n" +
            "Best regards,\n" +
            "Incident Management System",
            incident.getSeverity().getLevel(),
            incident.getTitle(),
            incident.getIncidentId(),
            incident.getTitle(),
            incident.getSeverity().getLevel(),
            incident.getDescription(),
            incident.getAffectedSystem(),
            incident.getStartTime().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
        );
    }
    
    private String generateStakeholderMessage(Incident incident, Employee stakeholder) {
        return String.format(
            "Status Update: %s incident %s is being handled. " +
            "Current owner updated. Your awareness is appreciated. " +
            "- Incident Management System",
            incident.getSeverity().getLevel(),
            incident.getIncidentId()
        );
    }
    
    public void resolveIncident(String incidentId, String resolutionNotes) {
        Incident incident = activeIncidents.stream()
            .filter(inc -> inc.getIncidentId().equals(incidentId))
            .findFirst()
            .orElse(null);
            
        if (incident != null) {
            incident.resolvedTime = LocalDateTime.now();
            
            // Free up the assigned employee
            if (incident.getCurrentOwner() != null) {
                Employee owner = findEmployeeById(incident.getCurrentOwner());
                if (owner != null) {
                    owner.setAvailable(true);
                }
            }
            
            activeIncidents.remove(incident);
            
            System.out.println("\n✅ Incident Resolved: " + incidentId);
            System.out.println("Resolution Time: " + incident.resolvedTime.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
            System.out.println("Total Duration: " + 
                java.time.Duration.between(incident.getStartTime(), incident.resolvedTime).toMinutes() + " minutes");
            System.out.println("Resolution Notes: " + resolutionNotes);
            
            // Send resolution notifications
            sendResolutionNotifications(incident, resolutionNotes);
        }
    }
    
    private void sendResolutionNotifications(Incident incident, String resolutionNotes) {
        communicationExecutor.submit(() -> {
            System.out.println("\n📢 Broadcasting resolution to all stakeholders...");
            
            String message = String.format(
                "✅ Good news! Incident %s has been resolved. " +
                "System %s is back to normal. " +
                "Thank you for your patience. " +
                "Resolution: %s",
                incident.getIncidentId(),
                incident.getAffectedSystem(),
                resolutionNotes
            );
            
            // Notify all levels that were involved
            for (String level : incident.getSeverity().getEscalationLevels()) {
                for (Employee emp : hierarchyMap.get(level)) {
                    System.out.println("📱 Resolution notification to " + emp.getName() + ": " + message);
                }
            }
        });
    }
    
    public void printIncidentReport() {
        System.out.println("\n📊 Incident Management Report");
        System.out.println("================================");
        System.out.println("Active Incidents: " + activeIncidents.size());
        
        for (Incident incident : activeIncidents) {
            System.out.println("\nIncident: " + incident.getIncidentId());
            System.out.println("  Title: " + incident.getTitle());
            System.out.println("  Severity: " + incident.getSeverity().getLevel());
            System.out.println("  Owner: " + (incident.getCurrentOwner() != null ? 
                findEmployeeById(incident.getCurrentOwner()).getName() : "Unassigned"));
            System.out.println("  Duration: " + 
                java.time.Duration.between(incident.getStartTime(), LocalDateTime.now()).toMinutes() + " minutes");
            System.out.println("  Escalations: " + incident.getEscalationHistory().size());
        }
        
        // Team availability
        System.out.println("\n👥 Team Availability:");
        for (String level : Arrays.asList("CEO", "CTO", "VP", "Senior", "Junior")) {
            long available = hierarchyMap.get(level).stream()
                .mapToLong(emp -> emp.isAvailable() ? 1 : 0)
                .sum();
            System.out.println("  " + level + ": " + available + "/" + hierarchyMap.get(level).size() + " available");
        }
    }
    
    // Demo method to show the system in action
    public static void main(String[] args) {
        System.out.println("🚀 Incident Command System Demo - Indian Corporate Style");
        System.out.println("=========================================================");
        
        IncidentCommandSystem ics = new IncidentCommandSystem();
        
        try {
            // Create different types of incidents
            ics.createIncident(
                "Payment Gateway Down", 
                "UPI payments failing across all platforms", 
                IncidentSeverity.P1_CRITICAL,
                "Payment Service"
            );
            
            Thread.sleep(2000);
            
            ics.createIncident(
                "Mobile App Slow Performance",
                "App response time increased by 200%",
                IncidentSeverity.P2_HIGH,
                "Mobile Application"
            );
            
            Thread.sleep(3000);
            
            ics.createIncident(
                "Email Service Degraded",
                "Some emails are delayed",
                IncidentSeverity.P3_MEDIUM,
                "Email Service"
            );
            
            Thread.sleep(2000);
            
            // Show current status
            ics.printIncidentReport();
            
            // Simulate resolution
            Thread.sleep(5000);
            System.out.println("\n🔧 Engineering team working on fixes...");
            Thread.sleep(3000);
            
            ics.resolveIncident("INC" + (System.currentTimeMillis() - 10000), 
                               "Database connection pool increased, load balancer reconfigured");
            
            Thread.sleep(1000);
            ics.printIncidentReport();
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            ics.communicationExecutor.shutdown();
        }
    }
}
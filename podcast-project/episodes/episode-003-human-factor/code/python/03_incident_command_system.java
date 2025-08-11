/*
 * Incident Command System - Episode 3: Human Factor in Tech
 * =========================================================
 * 
 * Indian organizational hierarchy ko respect karte hue incident management.
 * Senior logon ka experience aur junior logon ki energy - dono ka balance.
 * 
 * Indian Context Features:
 * - Respectful escalation (sir/madam culture)
 * - Cross-functional coordination (marketing, sales, support)
 * - Multiple language communication support
 * - Festival/holiday coverage planning
 * - Family emergency handling
 * 
 * Based on real incidents from Indian tech companies like:
 * - Paytm payment gateway failures
 * - Flipkart Big Billion Day crashes
 * - Ola surge pricing issues
 * - Zomato delivery disruptions
 */

package com.company.incident;

import java.time.LocalDateTime;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

// Incident severity with Indian business context
enum IncidentSeverity {
    SEV1_CRITICAL("Production completely down, revenue impact"),
    SEV2_HIGH("Major feature broken, customer complaints increasing"), 
    SEV3_MEDIUM("Minor issues, workaround available"),
    SEV4_LOW("Cosmetic issues, no business impact");
    
    private final String description;
    
    IncidentSeverity(String description) {
        this.description = description;
    }
    
    public String getDescription() { return description; }
}

// Indian organizational roles with respect hierarchy
enum TeamRole {
    INTERN(1, "Intern", "भажाcara"),
    JUNIOR_ENGINEER(2, "Junior SDE", "Junior Developer"),
    SENIOR_ENGINEER(3, "Senior SDE", "Senior Developer"), 
    TECH_LEAD(4, "Tech Lead", "Technical Lead"),
    ENGINEERING_MANAGER(5, "Engineering Manager", "Manager Sir/Madam"),
    DIRECTOR(6, "Director", "Director Sir/Madam"),
    VP_ENGINEERING(7, "VP Engineering", "VP Sir/Madam");
    
    private final int hierarchyLevel;
    private final String title;
    private final String respectfulAddress;
    
    TeamRole(int level, String title, String address) {
        this.hierarchyLevel = level;
        this.title = title;
        this.respectfulAddress = address;
    }
    
    public int getHierarchyLevel() { return hierarchyLevel; }
    public String getTitle() { return title; }  
    public String getRespectfulAddress() { return respectfulAddress; }
    
    public boolean canEscalateTo(TeamRole target) {
        return target.hierarchyLevel > this.hierarchyLevel;
    }
}

// Communication preferences for Indian workplace
enum CommunicationChannel {
    SLACK("Slack", "Quick updates, informal"),
    EMAIL("Email", "Formal communication, documentation"),
    WHATSAPP("WhatsApp", "Urgent alerts, personal reach"),
    PHONE_CALL("Phone", "Critical escalation, immediate response"),
    VIDEO_CALL("Video Call", "Complex discussions, screen sharing"),
    IN_PERSON("In Person", "Sensitive matters, relationship building");
    
    private final String channel;
    private final String usage;
    
    CommunicationChannel(String channel, String usage) {
        this.channel = channel;
        this.usage = usage;
    }
    
    public String getChannel() { return channel; }
    public String getUsage() { return usage; }
}

// Engineer profile with Indian context
class Engineer {
    private String id;
    private String name;
    private String email;
    private String phoneNumber;
    private String whatsappNumber;
    private TeamRole role;
    private List<String> skills;
    private List<String> languages; // Hindi, English, Tamil, etc.
    private boolean isOnVacation;
    private boolean hasFamilyEmergency;
    private LocalDateTime lastIncidentParticipation;
    private int totalIncidentsHandled;
    private double averageResolutionTime; // in hours
    private String timezone;
    
    // Constructor
    public Engineer(String id, String name, String email, String phone, TeamRole role) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.phoneNumber = phone;
        this.whatsappNumber = phone; // Assume same number
        this.role = role;
        this.skills = new ArrayList<>();
        this.languages = Arrays.asList("English", "Hindi");
        this.isOnVacation = false;
        this.hasFamilyEmergency = false;
        this.totalIncidentsHandled = 0;
        this.averageResolutionTime = 0.0;
        this.timezone = "Asia/Kolkata";
    }
    
    // Getters and setters
    public String getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getPhoneNumber() { return phoneNumber; }
    public String getWhatsappNumber() { return whatsappNumber; }
    public TeamRole getRole() { return role; }
    public List<String> getSkills() { return skills; }
    public List<String> getLanguages() { return languages; }
    public boolean isAvailable() { return !isOnVacation && !hasFamilyEmergency; }
    public LocalDateTime getLastIncidentParticipation() { return lastIncidentParticipation; }
    public int getTotalIncidentsHandled() { return totalIncidentsHandled; }
    public double getAverageResolutionTime() { return averageResolutionTime; }
    
    // Utility methods
    public void addSkill(String skill) { this.skills.add(skill); }
    public void markOnVacation(boolean onVacation) { this.isOnVacation = onVacation; }
    public void markFamilyEmergency(boolean emergency) { this.hasFamilyEmergency = emergency; }
    
    public void updateIncidentStats(LocalDateTime participationTime, double resolutionTime) {
        this.lastIncidentParticipation = participationTime;
        this.totalIncidentsHandled++;
        
        // Update average resolution time
        this.averageResolutionTime = ((this.averageResolutionTime * (totalIncidentsHandled - 1)) + resolutionTime) 
                                   / totalIncidentsHandled;
    }
    
    public String getRespectfulGreeting() {
        return "Namaste " + role.getRespectfulAddress();
    }
}

// Incident with comprehensive tracking
class Incident {
    private String id;
    private String title;
    private String description;
    private IncidentSeverity severity;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private Engineer incidentCommander;
    private List<Engineer> responders;
    private Map<String, String> timeline; // timestamp -> action
    private List<String> affectedServices;
    private double estimatedRevenueLoss; // in INR
    private int customersImpacted;
    private String rootCause;
    private List<String> actionItems;
    private Map<String, Object> metadata;
    private boolean isResolved;
    
    public Incident(String id, String title, String description, IncidentSeverity severity) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.severity = severity;
        this.startTime = LocalDateTime.now();
        this.responders = new ArrayList<>();
        this.timeline = new LinkedHashMap<>();
        this.affectedServices = new ArrayList<>();
        this.actionItems = new ArrayList<>();
        this.metadata = new HashMap<>();
        this.isResolved = false;
        this.estimatedRevenueLoss = 0.0;
        this.customersImpacted = 0;
        
        // Log initial timeline entry
        addTimelineEntry("Incident created: " + title);
    }
    
    public void addTimelineEntry(String action) {
        String timestamp = LocalDateTime.now().toString();
        timeline.put(timestamp, action);
    }
    
    public void assignIncidentCommander(Engineer commander) {
        this.incidentCommander = commander;
        addTimelineEntry("Incident Commander assigned: " + commander.getName() + 
                        " (" + commander.getRole().getTitle() + ")");
    }
    
    public void addResponder(Engineer responder) {
        if (!responders.contains(responder)) {
            responders.add(responder);
            addTimelineEntry("Responder added: " + responder.getName() + 
                           " (" + responder.getRole().getTitle() + ")");
        }
    }
    
    public void resolve(String resolution) {
        this.isResolved = true;
        this.endTime = LocalDateTime.now();
        this.rootCause = resolution;
        addTimelineEntry("Incident resolved: " + resolution);
        
        // Update responder statistics
        double resolutionTimeHours = Duration.between(startTime, endTime).toMinutes() / 60.0;
        for (Engineer responder : responders) {
            responder.updateIncidentStats(endTime, resolutionTimeHours);
        }
        if (incidentCommander != null) {
            incidentCommander.updateIncidentStats(endTime, resolutionTimeHours);
        }
    }
    
    // Getters
    public String getId() { return id; }
    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public IncidentSeverity getSeverity() { return severity; }
    public LocalDateTime getStartTime() { return startTime; }
    public LocalDateTime getEndTime() { return endTime; }
    public Engineer getIncidentCommander() { return incidentCommander; }
    public List<Engineer> getResponders() { return responders; }
    public Map<String, String> getTimeline() { return timeline; }
    public boolean isResolved() { return isResolved; }
    public double getEstimatedRevenueLoss() { return estimatedRevenueLoss; }
    public int getCustomersImpacted() { return customersImpacted; }
    
    public void setEstimatedRevenueLoss(double loss) { this.estimatedRevenueLoss = loss; }
    public void setCustomersImpacted(int customers) { this.customersImpacted = customers; }
    public void addAffectedService(String service) { this.affectedServices.add(service); }
    public void addActionItem(String actionItem) { this.actionItems.add(actionItem); }
}

// Communication manager for respectful Indian workplace communication
class CommunicationManager {
    private Map<IncidentSeverity, List<CommunicationChannel>> severityChannels;
    
    public CommunicationManager() {
        this.severityChannels = new HashMap<>();
        
        // Define communication channels by severity
        severityChannels.put(IncidentSeverity.SEV1_CRITICAL, 
            Arrays.asList(CommunicationChannel.PHONE_CALL, CommunicationChannel.WHATSAPP, 
                         CommunicationChannel.SLACK, CommunicationChannel.EMAIL));
        
        severityChannels.put(IncidentSeverity.SEV2_HIGH,
            Arrays.asList(CommunicationChannel.WHATSAPP, CommunicationChannel.SLACK, 
                         CommunicationChannel.PHONE_CALL, CommunicationChannel.EMAIL));
        
        severityChannels.put(IncidentSeverity.SEV3_MEDIUM,
            Arrays.asList(CommunicationChannel.SLACK, CommunicationChannel.EMAIL));
            
        severityChannels.put(IncidentSeverity.SEV4_LOW,
            Arrays.asList(CommunicationChannel.EMAIL, CommunicationChannel.SLACK));
    }
    
    public void sendNotification(Engineer engineer, Incident incident, String message) {
        List<CommunicationChannel> channels = severityChannels.get(incident.getSeverity());
        
        for (CommunicationChannel channel : channels) {
            String respectfulMessage = formatRespectfulMessage(engineer, incident, message);
            
            switch (channel) {
                case PHONE_CALL:
                    System.out.println("📞 Calling " + engineer.getPhoneNumber() + ": " + respectfulMessage);
                    break;
                case WHATSAPP:
                    System.out.println("📱 WhatsApp to " + engineer.getWhatsappNumber() + ": " + respectfulMessage);
                    break;
                case SLACK:
                    System.out.println("💬 Slack @" + engineer.getName() + ": " + respectfulMessage);
                    break;
                case EMAIL:
                    System.out.println("📧 Email to " + engineer.getEmail() + ": " + respectfulMessage);
                    break;
                default:
                    System.out.println("📢 " + channel.getChannel() + " to " + engineer.getName() + ": " + respectfulMessage);
            }
            
            // For critical incidents, try multiple channels
            if (incident.getSeverity() == IncidentSeverity.SEV1_CRITICAL) {
                continue; // Try all channels
            } else {
                break; // One channel sufficient for lower severity
            }
        }
    }
    
    private String formatRespectfulMessage(Engineer engineer, Incident incident, String message) {
        StringBuilder formatted = new StringBuilder();
        
        // Respectful greeting based on hierarchy
        if (engineer.getRole().getHierarchyLevel() >= 4) { // Senior roles
            formatted.append("Respected ").append(engineer.getRole().getRespectfulAddress()).append(", ");
        } else {
            formatted.append("Hi ").append(engineer.getName()).append(", ");
        }
        
        // Severity-based urgency indicator
        switch (incident.getSeverity()) {
            case SEV1_CRITICAL:
                formatted.append("🚨 CRITICAL: ");
                break;
            case SEV2_HIGH:
                formatted.append("⚠️ HIGH: ");
                break;
            default:
                formatted.append("ℹ️ ");
        }
        
        formatted.append(message);
        
        // Polite closing
        if (engineer.getRole().getHierarchyLevel() >= 4) {
            formatted.append("\n\nWith regards,\nIncident Management System");
        } else {
            formatted.append("\n\nThanks!");
        }
        
        return formatted.toString();
    }
}

// Escalation manager with Indian hierarchy respect
class EscalationManager {
    private Map<IncidentSeverity, List<TeamRole>> escalationMatrix;
    private Map<TeamRole, Duration> escalationTimeouts;
    
    public EscalationManager() {
        setupEscalationMatrix();
        setupTimeouts();
    }
    
    private void setupEscalationMatrix() {
        this.escalationMatrix = new HashMap<>();
        
        // SEV1 - Goes to top immediately but respectfully
        escalationMatrix.put(IncidentSeverity.SEV1_CRITICAL, 
            Arrays.asList(TeamRole.SENIOR_ENGINEER, TeamRole.TECH_LEAD, 
                         TeamRole.ENGINEERING_MANAGER, TeamRole.DIRECTOR, TeamRole.VP_ENGINEERING));
        
        // SEV2 - Senior technical people first
        escalationMatrix.put(IncidentSeverity.SEV2_HIGH,
            Arrays.asList(TeamRole.SENIOR_ENGINEER, TeamRole.TECH_LEAD, 
                         TeamRole.ENGINEERING_MANAGER));
        
        // SEV3 - Technical team handles
        escalationMatrix.put(IncidentSeverity.SEV3_MEDIUM,
            Arrays.asList(TeamRole.JUNIOR_ENGINEER, TeamRole.SENIOR_ENGINEER, TeamRole.TECH_LEAD));
            
        // SEV4 - Junior team can handle
        escalationMatrix.put(IncidentSeverity.SEV4_LOW,
            Arrays.asList(TeamRole.JUNIOR_ENGINEER, TeamRole.SENIOR_ENGINEER));
    }
    
    private void setupTimeouts() {
        this.escalationTimeouts = new HashMap<>();
        
        // Escalation timeouts based on role (Indian context - seniors get more time)
        escalationTimeouts.put(TeamRole.INTERN, Duration.ofMinutes(10));
        escalationTimeouts.put(TeamRole.JUNIOR_ENGINEER, Duration.ofMinutes(15));
        escalationTimeouts.put(TeamRole.SENIOR_ENGINEER, Duration.ofMinutes(20));
        escalationTimeouts.put(TeamRole.TECH_LEAD, Duration.ofMinutes(30));
        escalationTimeouts.put(TeamRole.ENGINEERING_MANAGER, Duration.ofHours(1));
        escalationTimeouts.put(TeamRole.DIRECTOR, Duration.ofHours(2));
        escalationTimeouts.put(TeamRole.VP_ENGINEERING, Duration.ofHours(4));
    }
    
    public List<Engineer> getEscalationChain(Incident incident, List<Engineer> allEngineers) {
        List<TeamRole> requiredRoles = escalationMatrix.get(incident.getSeverity());
        List<Engineer> escalationChain = new ArrayList<>();
        
        for (TeamRole role : requiredRoles) {
            // Find available engineers with this role
            List<Engineer> candidateEngineers = allEngineers.stream()
                .filter(e -> e.getRole() == role && e.isAvailable())
                .sorted((e1, e2) -> {
                    // Prefer engineers with recent incident experience
                    if (e1.getLastIncidentParticipation() == null && e2.getLastIncidentParticipation() == null) {
                        return 0;
                    }
                    if (e1.getLastIncidentParticipation() == null) return 1;
                    if (e2.getLastIncidentParticipation() == null) return -1;
                    return e2.getLastIncidentParticipation().compareTo(e1.getLastIncidentParticipation());
                })
                .collect(Collectors.toList());
            
            if (!candidateEngineers.isEmpty()) {
                escalationChain.add(candidateEngineers.get(0));
            }
        }
        
        return escalationChain;
    }
    
    public Duration getEscalationTimeout(TeamRole role) {
        return escalationTimeouts.getOrDefault(role, Duration.ofMinutes(15));
    }
}

// Main Incident Command System
public class IncidentCommandSystem {
    private List<Engineer> engineers;
    private Map<String, Incident> activeIncidents;
    private Map<String, Incident> resolvedIncidents;
    private CommunicationManager communicationManager;
    private EscalationManager escalationManager;
    
    public IncidentCommandSystem() {
        this.engineers = new ArrayList<>();
        this.activeIncidents = new ConcurrentHashMap<>();
        this.resolvedIncidents = new ConcurrentHashMap<>();
        this.communicationManager = new CommunicationManager();
        this.escalationManager = new EscalationManager();
    }
    
    public void addEngineer(Engineer engineer) {
        engineers.add(engineer);
        System.out.println("✅ Added " + engineer.getName() + " (" + engineer.getRole().getTitle() + ") to team");
    }
    
    public String createIncident(String title, String description, IncidentSeverity severity) {
        String incidentId = "INC-" + System.currentTimeMillis();
        Incident incident = new Incident(incidentId, title, description, severity);
        
        activeIncidents.put(incidentId, incident);
        
        System.out.println("🚨 New " + severity.name() + " incident created: " + title);
        System.out.println("   ID: " + incidentId);
        System.out.println("   Description: " + description);
        
        // Auto-assign incident commander and responders
        assignIncidentTeam(incident);
        
        return incidentId;
    }
    
    private void assignIncidentTeam(Incident incident) {
        List<Engineer> escalationChain = escalationManager.getEscalationChain(incident, engineers);
        
        if (escalationChain.isEmpty()) {
            System.out.println("❌ No available engineers found for incident assignment!");
            return;
        }
        
        // Assign incident commander (first in escalation chain)
        Engineer commander = escalationChain.get(0);
        incident.assignIncidentCommander(commander);
        
        // Add appropriate responders based on severity
        int respondersNeeded = getRespondersNeeded(incident.getSeverity());
        for (int i = 1; i < Math.min(escalationChain.size(), respondersNeeded + 1); i++) {
            incident.addResponder(escalationChain.get(i));
        }
        
        // Notify the team
        notifyIncidentTeam(incident);
    }
    
    private int getRespondersNeeded(IncidentSeverity severity) {
        switch (severity) {
            case SEV1_CRITICAL: return 4; // Full war room
            case SEV2_HIGH: return 2;      // Core team
            case SEV3_MEDIUM: return 1;    // Single responder
            case SEV4_LOW: return 0;       // Commander only
            default: return 1;
        }
    }
    
    private void notifyIncidentTeam(Incident incident) {
        String message = String.format(
            "You have been assigned to incident: %s\n" +
            "Severity: %s\n" +
            "Description: %s\n" +
            "Please join the incident response immediately.",
            incident.getTitle(),
            incident.getSeverity().name(),
            incident.getDescription()
        );
        
        // Notify incident commander
        if (incident.getIncidentCommander() != null) {
            communicationManager.sendNotification(incident.getIncidentCommander(), incident, 
                "You are the Incident Commander for this incident. " + message);
        }
        
        // Notify responders
        for (Engineer responder : incident.getResponders()) {
            communicationManager.sendNotification(responder, incident, 
                "You are assigned as responder for this incident. " + message);
        }
    }
    
    public void updateIncident(String incidentId, String update) {
        Incident incident = activeIncidents.get(incidentId);
        if (incident != null) {
            incident.addTimelineEntry(update);
            System.out.println("📝 Incident " + incidentId + " updated: " + update);
        }
    }
    
    public void resolveIncident(String incidentId, String resolution) {
        Incident incident = activeIncidents.get(incidentId);
        if (incident != null) {
            incident.resolve(resolution);
            activeIncidents.remove(incidentId);
            resolvedIncidents.put(incidentId, incident);
            
            System.out.println("✅ Incident " + incidentId + " resolved: " + resolution);
            
            // Thank the team (Indian courtesy)
            thankIncidentTeam(incident);
            
            // Generate post-incident summary
            generatePostIncidentSummary(incident);
        }
    }
    
    private void thankIncidentTeam(Incident incident) {
        String thankMessage = String.format(
            "Thank you for your excellent work on incident: %s\n" +
            "The incident has been successfully resolved.\n" +
            "Your dedication and quick response helped minimize the impact.\n\n" +
            "Please take some time to rest and recover.",
            incident.getTitle()
        );
        
        if (incident.getIncidentCommander() != null) {
            System.out.println("🙏 Thank you message sent to Incident Commander: " + 
                             incident.getIncidentCommander().getName());
        }
        
        for (Engineer responder : incident.getResponders()) {
            System.out.println("🙏 Thank you message sent to responder: " + responder.getName());
        }
    }
    
    private void generatePostIncidentSummary(Incident incident) {
        Duration duration = Duration.between(incident.getStartTime(), incident.getEndTime());
        long resolutionTimeMinutes = duration.toMinutes();
        
        System.out.println("\n📊 Post-Incident Summary for " + incident.getId());
        System.out.println("=" * 50);
        System.out.println("Title: " + incident.getTitle());
        System.out.println("Severity: " + incident.getSeverity().name());
        System.out.println("Resolution Time: " + resolutionTimeMinutes + " minutes");
        System.out.println("Incident Commander: " + 
            (incident.getIncidentCommander() != null ? incident.getIncidentCommander().getName() : "None"));
        System.out.println("Responders: " + incident.getResponders().size());
        
        if (incident.getEstimatedRevenueLoss() > 0) {
            System.out.println("Estimated Revenue Loss: ₹" + String.format("%.2f", incident.getEstimatedRevenueLoss()));
        }
        
        if (incident.getCustomersImpacted() > 0) {
            System.out.println("Customers Impacted: " + incident.getCustomersImpacted());
        }
        
        System.out.println("\nTimeline:");
        incident.getTimeline().forEach((timestamp, action) -> 
            System.out.println("  " + timestamp + ": " + action));
    }
    
    public void getIncidentStatus(String incidentId) {
        Incident incident = activeIncidents.get(incidentId);
        if (incident == null) {
            incident = resolvedIncidents.get(incidentId);
        }
        
        if (incident != null) {
            System.out.println("\n🔍 Incident Status: " + incidentId);
            System.out.println("Title: " + incident.getTitle());
            System.out.println("Status: " + (incident.isResolved() ? "RESOLVED" : "ACTIVE"));
            System.out.println("Severity: " + incident.getSeverity().name());
            System.out.println("Start Time: " + incident.getStartTime());
            
            if (incident.getIncidentCommander() != null) {
                System.out.println("Incident Commander: " + incident.getIncidentCommander().getName());
            }
            
            System.out.println("Responders: " + incident.getResponders().size());
            
            if (incident.isResolved()) {
                System.out.println("Resolution Time: " + 
                    Duration.between(incident.getStartTime(), incident.getEndTime()).toMinutes() + " minutes");
            }
        } else {
            System.out.println("❌ Incident not found: " + incidentId);
        }
    }
    
    public void getTeamHealthReport() {
        System.out.println("\n👥 Team Health Report");
        System.out.println("=" * 30);
        System.out.println("Total Engineers: " + engineers.size());
        
        long availableEngineers = engineers.stream().filter(Engineer::isAvailable).count();
        System.out.println("Available Engineers: " + availableEngineers);
        
        long onVacation = engineers.stream().filter(e -> !e.isAvailable()).count();
        System.out.println("On Vacation/Emergency: " + onVacation);
        
        System.out.println("\nActive Incidents: " + activeIncidents.size());
        System.out.println("Resolved Incidents (Total): " + resolvedIncidents.size());
        
        // Top responders
        List<Engineer> topResponders = engineers.stream()
            .sorted((e1, e2) -> Integer.compare(e2.getTotalIncidentsHandled(), e1.getTotalIncidentsHandled()))
            .limit(3)
            .collect(Collectors.toList());
        
        System.out.println("\n🏆 Top Incident Responders:");
        for (int i = 0; i < topResponders.size(); i++) {
            Engineer eng = topResponders.get(i);
            System.out.println(String.format("  %d. %s (%s): %d incidents, %.1fh avg resolution", 
                i + 1, eng.getName(), eng.getRole().getTitle(), 
                eng.getTotalIncidentsHandled(), eng.getAverageResolutionTime()));
        }
    }
    
    // Demo method
    public static void demoIncidentCommandSystem() {
        System.out.println("🚀 Incident Command System Demo - Indian Tech Company Style");
        System.out.println("=" * 70);
        
        IncidentCommandSystem ics = new IncidentCommandSystem();
        
        // Add engineers with Indian names and roles
        Engineer rajesh = new Engineer("ENG001", "Rajesh Kumar", "rajesh@company.com", "+91-98765-43210", TeamRole.VP_ENGINEERING);
        rajesh.addSkill("System Architecture");
        rajesh.addSkill("Crisis Management");
        
        Engineer priya = new Engineer("ENG002", "Priya Sharma", "priya@company.com", "+91-98765-43211", TeamRole.ENGINEERING_MANAGER);
        priya.addSkill("Team Management");
        priya.addSkill("Database Systems");
        
        Engineer amit = new Engineer("ENG003", "Amit Singh", "amit@company.com", "+91-98765-43212", TeamRole.TECH_LEAD);
        amit.addSkill("Microservices");
        amit.addSkill("DevOps");
        
        Engineer sneha = new Engineer("ENG004", "Sneha Patel", "sneha@company.com", "+91-98765-43213", TeamRole.SENIOR_ENGINEER);
        sneha.addSkill("Backend Development");
        sneha.addSkill("API Design");
        
        Engineer vikram = new Engineer("ENG005", "Vikram Reddy", "vikram@company.com", "+91-98765-43214", TeamRole.JUNIOR_ENGINEER);
        vikram.addSkill("Frontend Development");
        vikram.addSkill("React");
        
        // Add engineers to system
        ics.addEngineer(rajesh);
        ics.addEngineer(priya);
        ics.addEngineer(amit);
        ics.addEngineer(sneha);
        ics.addEngineer(vikram);
        
        System.out.println("\n" + "=" * 50);
        
        // Simulate critical incident (like Paytm payment gateway failure)
        String criticalIncidentId = ics.createIncident(
            "Payment Gateway Complete Failure",
            "All payment transactions failing across India. Customer complaints pouring in. " +
            "Estimated revenue loss: ₹50 lakhs per minute. Social media mentions spiking.",
            IncidentSeverity.SEV1_CRITICAL
        );
        
        // Update incident with progress
        try { Thread.sleep(1000); } catch (InterruptedException e) {}
        ics.updateIncident(criticalIncidentId, "Database connection pool exhausted identified as root cause");
        
        try { Thread.sleep(1000); } catch (InterruptedException e) {}
        ics.updateIncident(criticalIncidentId, "Emergency database scaling initiated");
        
        try { Thread.sleep(1000); } catch (InterruptedException e) {}
        ics.updateIncident(criticalIncidentId, "Payment processing restored, monitoring for stability");
        
        // Resolve the critical incident
        ics.resolveIncident(criticalIncidentId, 
            "Database connection pool configuration fixed. " +
            "Monitoring dashboards improved. Runbook updated for future incidents.");
        
        System.out.println("\n" + "=" * 50);
        
        // Simulate medium severity incident
        String mediumIncidentId = ics.createIncident(
            "Search Feature Slow Response",
            "Product search taking 5+ seconds to respond. " +
            "Conversion rate dropping but not critical.",
            IncidentSeverity.SEV3_MEDIUM
        );
        
        // Check incident status
        ics.getIncidentStatus(criticalIncidentId);
        ics.getIncidentStatus(mediumIncidentId);
        
        // Resolve medium incident
        ics.resolveIncident(mediumIncidentId, 
            "Elasticsearch index optimized. Search cache warming implemented.");
        
        // Generate team health report
        ics.getTeamHealthReport();
    }
    
    public static void main(String[] args) {
        demoIncidentCommandSystem();
    }
}